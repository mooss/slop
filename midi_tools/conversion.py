"""Conversion functions between MIDI and YAML representations."""
from pathlib import Path

from .mir import Mir
from .utils import PathLike

def convert(input_path: PathLike, output_path: PathLike, midi_format: int = 1) -> None:
    """Convert between MIDI and YAML based on file extensions."""
    in_path = Path(input_path)
    out_path = Path(output_path)
    if in_path.resolve() == out_path.resolve():
        raise ValueError("Input and output files must be different")

    Mir.from_disk(in_path).to_disk(out_path, midi_format)
