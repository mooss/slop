"""Conversion functions between MIDI and YAML representations."""
import io
from pathlib import Path
from typing import Any, Union

import mido
import yaml

PathLike = Union[str, Path]

MIDI_EXTENSIONS = (".mid", ".midi")
YAML_EXTENSIONS = (".yaml", ".yml")


def midi_to_yaml_data(midi: mido.MidiFile) -> dict[str, Any]:
    """Convert a mido.MidiFile to a YAML-serializable dict."""
    return {
        "ticks_per_beat": midi.ticks_per_beat,
        "tracks": [
            [event.dict() for event in track]
            for track in midi.tracks
        ],
    }


def yaml_data_to_midi(data: dict[str, Any]) -> mido.MidiFile:
    """Convert a YAML-serializable dict to a mido.MidiFile."""
    midi = mido.MidiFile(ticks_per_beat=data["ticks_per_beat"])
    for track_data in data["tracks"]:
        track = mido.MidiTrack()
        for msg_dict in track_data:
            try:
                msg = mido.Message(**msg_dict)
            except LookupError: # A bit dirty to handle it this way but it appears to work.
                msg = mido.MetaMessage(**msg_dict)
            track.append(msg)
        midi.tracks.append(track)
    return midi


def midi_to_yaml(midi_path: PathLike, yaml_path: PathLike) -> None:
    """Read a MIDI file and write its YAML representation."""
    midi = mido.MidiFile(str(midi_path))
    data = midi_to_yaml_data(midi)
    with open(yaml_path, "w") as f:
        yaml.safe_dump(data, f)


def yaml_to_midi(yaml_path: PathLike, midi_path: PathLike) -> None:
    """Read a YAML file and write a MIDI file from it."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    midi = yaml_data_to_midi(data)
    midi.save(str(midi_path))


def roundtrip(path: PathLike) -> None:
    """Verify that a file survives a MIDI<->YAML roundtrip unchanged."""
    path = Path(path)
    ext = path.suffix.lower()

    if ext in MIDI_EXTENSIONS:
        original_bytes = path.read_bytes()
        midi = mido.MidiFile(file=io.BytesIO(original_bytes))
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


def convert(input_path: PathLike, output_path: PathLike) -> None:
    """Convert between MIDI and YAML based on file extensions."""
    input_ext = Path(input_path).suffix.lower()
    output_ext = Path(output_path).suffix.lower()

    if input_ext in MIDI_EXTENSIONS and output_ext in YAML_EXTENSIONS:
        midi_to_yaml(input_path, output_path)
    elif input_ext in YAML_EXTENSIONS and output_ext in MIDI_EXTENSIONS:
        yaml_to_midi(input_path, output_path)
    else:
        raise ValueError(
            f"Cannot convert {input_ext!r} to {output_ext!r}; "
            "expected MIDI (.mid/.midi) <-> YAML (.yaml/.yml)"
        )
