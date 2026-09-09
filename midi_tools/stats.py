"""Functions to compute stats about MIDI files."""
from typing import Any

import mido

from .constants import MIDI_PROGRAMS
from .utils import (
    PathLike,
    MIDI_DEFAULT_TEMPO,
    MIDI_DEFAULT_TIME_SIGNATURE,
    _load_midi,
    _merge_tracks,
)

def _track_info(track: mido.MidiTrack) -> dict:
    """Return track name and first program change info."""
    name = None
    program = None
    for msg in track:
        if msg.type == "track_name" and name is None:
            name = msg.name
        elif msg.type == "program_change" and program is None:
            program = msg.program
        if name is not None and program is not None:
            break

    return {
        "name": name,
        "program": program,
        "program_name": MIDI_PROGRAMS.get(program) if program is not None else None,
    }


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

    tracks = midi.tracks
    if midi.type == 1:
        tracks = tracks[1:]
    ntracks = len(tracks)

    return {
        "format": midi.type,
        "ntracks": ntracks,
        "duration": midi.length,
        "bpm": tempos or [MIDI_DEFAULT_TEMPO],
        "time_signatures": time_signatures or [MIDI_DEFAULT_TIME_SIGNATURE],
        "tracks": [_track_info(track) for track in tracks],
    }
