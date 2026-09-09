import mido
import pytest
import yaml

from midi_tools.conversion import (
    yaml_data_to_midi,
    midi_to_yaml_data,
    convert,
    roundtrip,
)
from midi_tools.stats import build_midi_stats
from midi_tools.utils import _merge_tracks

###################
# Roundtrip tests #
###################

def test_yaml_manual_roundtrip(yaml_data):
    """YAML -> MIDI -> YAML must preserve the data exactly."""
    midi = yaml_data_to_midi(yaml_data)
    roundtrip_data = midi_to_yaml_data(midi)
    assert roundtrip_data == yaml_data


def test_yaml_roundtrip(yaml_data, tmp_path):
    """roundtrip() should not raise for a valid YAML file."""
    yaml_path = tmp_path / "input.yaml"
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    roundtrip(yaml_path)

###############
# Stats tests #
###############

def test_stats_format_and_tracks(yaml_data, tmp_path):
    """Stats should report format 1 and 2 tracks (excluding control track)."""
    # Convert YAML to MIDI and save to temp file
    midi = yaml_data_to_midi(yaml_data)
    midi_path = tmp_path / "test.mid"
    midi.save(str(midi_path))

    stats = build_midi_stats(midi_path)
    assert stats["format"] == 1
    assert stats["ntracks"] == 2


def test_stats_tempo_and_time_signature(yaml_data, tmp_path):
    """Stats should contain tempo 60 BPM and time signature 4/4."""
    midi = yaml_data_to_midi(yaml_data)
    midi_path = tmp_path / "test.mid"
    midi.save(str(midi_path))

    stats = build_midi_stats(midi_path)
    assert stats["bpm"] == [60.0]  # 60,000,000 / 1,000,000
    assert stats["time_signatures"] == ["4/4"]


def test_stats_track_info(yaml_data, tmp_path):
    """Track names and program names should be correct."""
    midi = yaml_data_to_midi(yaml_data)
    midi_path = tmp_path / "test.mid"
    midi.save(str(midi_path))

    stats = build_midi_stats(midi_path)
    tracks = stats["tracks"]
    assert len(tracks) == 2
    assert tracks[0]["name"] == "upper"
    assert tracks[0]["program"] == 6
    assert tracks[0]["program_name"] == "Harpsichord"
    assert tracks[1]["name"] == "lower"
    assert tracks[1]["program"] == 6
    assert tracks[1]["program_name"] == "Harpsichord"


def test_stats_defaults_without_meta(tmp_path):
    """Missing tempo/time-signature meta should use documented defaults."""
    midi = mido.MidiFile(type=0)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name="test", time=0))
    track.append(mido.Message("note_on", note=60, velocity=100, time=0, channel=0))
    track.append(mido.Message("note_off", note=60, velocity=64, time=100, channel=0))
    track.append(mido.MetaMessage("end_of_track", time=0))
    midi.tracks.append(track)

    midi_path = tmp_path / "simple.mid"
    midi.save(str(midi_path))

    stats = build_midi_stats(midi_path)
    assert stats["bpm"] == [120.0]
    assert stats["time_signatures"] == ["4/4"]
    assert stats["format"] == 0
    assert stats["ntracks"] == 1


def test_stats_rejects_type_2(tmp_path):
    """Type 2 MIDI files are unsupported and should raise ValueError."""
    midi = mido.MidiFile(type=2)
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name="async", time=0))
    track.append(mido.MetaMessage("end_of_track", time=1))
    midi.tracks.append(track)

    midi_path = tmp_path / "async.mid"
    midi.save(str(midi_path))

    with pytest.raises(ValueError):
        build_midi_stats(midi_path)


####################
# Conversion tests #
####################

def test_convert_yaml_to_midi_and_back(yaml_data, tmp_path):
    """Convert YAML->MIDI and MIDI->YAML should produce identical YAML."""
    yaml_path = tmp_path / "input.yaml"
    midi_path = tmp_path / "output.mid"
    yaml_out_path = tmp_path / "output.yaml"

    # Write YAML data to file
    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    # YAML -> MIDI
    convert(yaml_path, midi_path)

    # MIDI -> YAML
    convert(midi_path, yaml_out_path)

    # Compare YAML contents
    with open(yaml_out_path) as f:
        result = yaml.safe_load(f)
    assert result == yaml_data


def test_convert_midi_to_midi_format_0(yaml_data, tmp_path):
    """MIDI -> MIDI conversion should be able to change format to 0."""
    yaml_path = tmp_path / "input.yaml"
    midi_path = tmp_path / "output.mid"
    midi0_path = tmp_path / "output0.mid"

    with open(yaml_path, "w") as f:
        yaml.safe_dump(yaml_data, f)

    convert(yaml_path, midi_path)
    convert(midi_path, midi0_path, midi_format=0)

    midi = mido.MidiFile(str(midi0_path))
    assert midi.type == 0
    assert len(midi.tracks) == 1


def test_convert_rejects_same_path(tmp_path):
    """Converting a file to itself should fail."""
    path = tmp_path / "same.mid"
    path.write_bytes(b"")

    with pytest.raises(ValueError):
        convert(path, path)


def test_convert_rejects_unknown_extensions(tmp_path):
    """Unsupported input/output extensions should raise ValueError."""
    input_path = tmp_path / "input.txt"
    output_path = tmp_path / "output.mid"
    input_path.write_text("not midi")

    with pytest.raises(ValueError):
        convert(input_path, output_path)


###############
# Merge tests #
###############

def test_yaml_data_to_midi_format_0_merges_tracks(yaml_data):
    """Requesting format 0 should produce a single merged track."""
    midi = yaml_data_to_midi(yaml_data, midi_format=0)
    assert midi.type == 0
    assert len(midi.tracks) == 1


def test_merge_tracks_meta_before_note_at_same_time():
    """At the same absolute tick, meta events must precede note events."""
    control = mido.MidiTrack()
    control.append(mido.MetaMessage("track_name", name="control", time=0))
    control.append(mido.MetaMessage("set_tempo", tempo=500000, time=10))
    control.append(mido.MetaMessage("end_of_track", time=0))

    notes = mido.MidiTrack()
    notes.append(mido.MetaMessage("track_name", name="notes", time=0))
    notes.append(mido.Message("note_on", note=60, velocity=100, time=10, channel=0))
    notes.append(mido.Message("note_off", note=60, velocity=64, time=10, channel=0))
    notes.append(mido.MetaMessage("end_of_track", time=0))

    merged = _merge_tracks([control, notes])

    abs_time = 0
    seen = []
    for msg in merged:
        abs_time += msg.time
        seen.append((abs_time, msg.type))

    tempo_index = seen.index((10, "set_tempo"))
    note_on_index = seen.index((10, "note_on"))
    assert tempo_index < note_on_index
