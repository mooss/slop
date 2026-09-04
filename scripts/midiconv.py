#!/usr/bin/env python3
import argparse
import yaml
import mido


def midi_to_yaml(midi_path, yaml_path):
    midi = mido.MidiFile(midi_path)
    data = {
        "ticks_per_beat": midi.ticks_per_beat,
        "tracks": [
            [event.dict() for event in track]
            for track in midi.tracks
        ],
    }
    with open(yaml_path, "w") as f:
        yaml.safe_dump(data, f)


def yaml_to_midi(yaml_path, midi_path):
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

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

    midi.save(midi_path)


def main():
    parser = argparse.ArgumentParser(description="Convert MIDI <-> YAML")
    sub = parser.add_subparsers(dest="command", required=True)

    p_m2y = sub.add_parser("midi2yaml", help="Convert MIDI file to YAML")
    p_m2y.add_argument("midi_file")
    p_m2y.add_argument("yaml_file")

    p_y2m = sub.add_parser("yaml2midi", help="Convert YAML file to MIDI")
    p_y2m.add_argument("yaml_file")
    p_y2m.add_argument("midi_file")

    args = parser.parse_args()

    if args.command == "midi2yaml":
        midi_to_yaml(args.midi_file, args.yaml_file)
    elif args.command == "yaml2midi":
        yaml_to_midi(args.yaml_file, args.midi_file)

if __name__ == "__main__":
    main()
