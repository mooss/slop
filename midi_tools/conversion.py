"""Conversion functions between MIDI and YAML representations."""
import io
from pathlib import Path
from typing import Any, Union

import mido
import yaml

PathLike = Union[str, Path]

MIDI_EXTENSIONS = (".mid", ".midi")
YAML_EXTENSIONS = (".yaml", ".yml")
MIDI_DEFAULT_TEMPO = 120.0
MIDI_DEFAULT_TIME_SIGNATURE = "4/4"


def _load_midi(source: Union[PathLike, io.BytesIO]) -> mido.MidiFile:
    """Open a MIDI file and raise ValueError if its type/format is 2."""
    if isinstance(source, (str, Path)):
        midi = mido.MidiFile(str(source))
    else:
        midi = mido.MidiFile(file=source)
    if midi.type == 2:
        raise ValueError("MIDI format/type 2 is not supported")
    return midi


def _merge_tracks(tracks: list[mido.MidiTrack]) -> mido.MidiTrack:
    """Merge multiple tracks into one track, sorted by absolute tick."""
    if len(tracks) == 0:
        return mido.MidiTrack()
    if len(tracks) == 1:
        return tracks[0]

    events = []  # (absolute_time, track_index, message)
    max_end_time = 0

    for track_index, track in enumerate(tracks):
        abs_time = 0
        for msg in track:
            abs_time += msg.time
            if msg.type == "end_of_track":
                max_end_time = max(max_end_time, abs_time)
            else:
                events.append((abs_time, track_index, msg))

    # Make sure tempo/meta events are sorted before the rest to maintain the interpretation.
    events.sort(key=lambda item: (item[0], 0 if item[2].is_meta else 1, item[1]))

    merged = mido.MidiTrack()
    current_time = 0
    for abs_time, _, msg in events:
        merged.append(msg.copy(time=abs_time - current_time))
        current_time = abs_time

    end_time = max(0, max_end_time - current_time)
    merged.append(mido.MetaMessage("end_of_track", time=end_time))
    return merged


def midi_to_yaml_data(midi: mido.MidiFile) -> dict[str, Any]:
    """Convert a mido.MidiFile to a YAML-serializable dict."""
    return {
        "ticks_per_beat": midi.ticks_per_beat,
        "tracks": [
            [event.dict() for event in track]
            for track in midi.tracks
        ],
    }


def yaml_data_to_midi(data: dict[str, Any], midi_format: int = 1) -> mido.MidiFile:
    """Convert a YAML-serializable dict to a mido.MidiFile."""
    midi = mido.MidiFile(type=midi_format, ticks_per_beat=data["ticks_per_beat"])
    tracks = []
    for track_data in data["tracks"]:
        track = mido.MidiTrack()
        for msg_dict in track_data:
            try:
                msg = mido.Message(**msg_dict)
            except LookupError: # A bit dirty to handle it this way but it appears to work.
                msg = mido.MetaMessage(**msg_dict)
            track.append(msg)
        tracks.append(track)

    if midi_format == 0:
        midi.tracks = [_merge_tracks(tracks)]
    else:
        midi.tracks = tracks

    return midi


def midi_to_midi(midi_path: PathLike, output_path: PathLike, midi_format: int = 1) -> None:
    """Read a MIDI file and write it with the requested MIDI format/type."""
    midi = _load_midi(midi_path)
    if midi_format == 0:
        midi.tracks = [_merge_tracks(midi.tracks)]
    midi.type = midi_format
    midi.save(str(output_path))


def midi_to_yaml(midi_path: PathLike, yaml_path: PathLike) -> None:
    """Read a MIDI file and write its YAML representation."""
    midi = _load_midi(midi_path)
    data = midi_to_yaml_data(midi)
    with open(yaml_path, "w") as f:
        yaml.safe_dump(data, f)


def yaml_to_midi(yaml_path: PathLike, midi_path: PathLike, midi_format: int = 1) -> None:
    """Read a YAML file and write a MIDI file from it."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    midi = yaml_data_to_midi(data, midi_format=midi_format)
    midi.save(str(midi_path))


def roundtrip(path: PathLike) -> None:
    """Verify that a file survives a MIDI<->YAML roundtrip unchanged."""
    path = Path(path)
    ext = path.suffix.lower()

    if ext in MIDI_EXTENSIONS:
        original_bytes = path.read_bytes()
        midi = _load_midi(io.BytesIO(original_bytes))
        data = midi_to_yaml_data(midi)
        roundtrip_midi = yaml_data_to_midi(data)
        out = io.BytesIO()
        roundtrip_midi.save(file=out)
        if out.getvalue() != original_bytes:
            raise RuntimeError("Roundtrip failed: MIDI output differs from input")

    elif ext in YAML_EXTENSIONS:
        with open(path) as f:
            original_data = yaml.safe_load(f)
        midi = yaml_data_to_midi(original_data)
        roundtrip_data = midi_to_yaml_data(midi)
        if roundtrip_data != original_data:
            raise RuntimeError("Roundtrip failed: YAML output differs from input")

    else:
        raise ValueError(f"Unknown extension: {ext}")


def build_midi_stats(midi_path: PathLike) -> dict[str, Any]:
    """Return useful statistics about a MIDI file."""
    midi = _load_midi(midi_path)

    tempos = []
    time_signatures = []

    for msg in _merge_tracks(midi.tracks):
        if msg.type == "set_tempo":
            bpm = round(60_000_000 / msg.tempo, 2)
            tempos.append(bpm)
        elif msg.type == "time_signature":
            ts = f"{msg.numerator}/{msg.denominator}"
            if ts not in time_signatures:
                time_signatures.append(ts)

    ntracks = len(midi.tracks)
    if midi.type == 1:
        ntracks -= 1

    return {
        "format": midi.type,
        "ntracks": ntracks,
        "duration": midi.length,
        "bpm": tempos or [MIDI_DEFAULT_TEMPO],
        "time_signatures": time_signatures or [MIDI_DEFAULT_TIME_SIGNATURE],
    }


def convert(input_path: PathLike, output_path: PathLike, midi_format: int = 1) -> None:
    """Convert between MIDI and YAML based on file extensions."""
    in_path = Path(input_path)
    out_path = Path(output_path)
    if in_path.resolve() == out_path.resolve():
        raise ValueError("Input and output files must be different")

    input_ext = in_path.suffix.lower()
    output_ext = out_path.suffix.lower()

    if input_ext in MIDI_EXTENSIONS and output_ext in YAML_EXTENSIONS:
        midi_to_yaml(in_path, out_path)
    elif input_ext in YAML_EXTENSIONS and output_ext in MIDI_EXTENSIONS:
        yaml_to_midi(in_path, out_path, midi_format=midi_format)
    elif input_ext in MIDI_EXTENSIONS and output_ext in MIDI_EXTENSIONS:
        midi_to_midi(in_path, out_path, midi_format=midi_format)
    else:
        raise ValueError(
            f"Cannot convert {input_ext!r} to {output_ext!r}; "
            "expected MIDI (.mid/.midi) <-> YAML (.yaml/.yml) or MIDI -> MIDI"
        )
