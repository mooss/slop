"""Command-line interface for MIDI<->YAML conversion."""
import argparse
import sys
from typing import Optional, Sequence

from .conversion import midi_to_yaml, roundtrip, yaml_to_midi


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Convert MIDI <-> YAML")
    sub = parser.add_subparsers(dest="command", required=True)

    p_m2y = sub.add_parser("midi2yaml", help="Convert MIDI file to YAML")
    p_m2y.add_argument("midi_file")
    p_m2y.add_argument("yaml_file")

    p_y2m = sub.add_parser("yaml2midi", help="Convert YAML file to MIDI")
    p_y2m.add_argument("yaml_file")
    p_y2m.add_argument("midi_file")

    p_rt = sub.add_parser("roundtrip", help="Roundtrip MIDI/YAML conversion")
    p_rt.add_argument("input_file")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI, returning a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        if args.command == "midi2yaml":
            midi_to_yaml(args.midi_file, args.yaml_file)
        elif args.command == "yaml2midi":
            yaml_to_midi(args.yaml_file, args.midi_file)
        elif args.command == "roundtrip":
            roundtrip(args.input_file)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
