"""Various MIDI constants and minor utilities."""
import io
from pathlib import Path
from typing import IO, Union

import mido

PathLike = Union[str, Path]
FileLike = Union[PathLike, IO]

MIDI_EXTENSIONS = (".mid", ".midi")
YAML_EXTENSIONS = (".yaml", ".yml")
MIDI_DEFAULT_TEMPO = 120.0
MIDI_DEFAULT_TIME_SIGNATURE = "4/4"

# Mark functions as exported.
__all__ = ["_load_mido"]

def _load_mido(source: Union[PathLike, io.BytesIO]) -> mido.MidiFile:
    """Open a MIDI file and raise ValueError if its type/format is 2."""
    if isinstance(source, (str, Path)):
        midi = mido.MidiFile(str(source))
    else:
        midi = mido.MidiFile(file=source)
    if midi.type == 2:
        raise ValueError("MIDI format/type 2 is not supported")
    return midi
