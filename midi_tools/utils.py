"""Various MIDI constants and minor utilities."""
import io
from pathlib import Path
from typing import Union

import mido

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
