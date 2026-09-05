"""Command-line interface for MIDI<->YAML conversion."""
import argparse
import sys
from typing import Optional, Sequence

from .conversion import convert, roundtrip


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Convert MIDI <-> YAML.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_conv = sub.add_parser("conv", help="Convert between MIDI and YAML based on file extensions")
    p_conv.add_argument("input_file")
    p_conv.add_argument("output_file")
    p_conv.add_argument(
        "--format",
        type=int,
        choices=[0, 1],
        default=1,
        help="MIDI format/type of the output MIDI file (default: 1, 2 is not supported)",
    )

    p_rt = sub.add_parser("roundtrip", help="Roundtrip MIDI/YAML conversion")
    p_rt.add_argument("input_file")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the CLI, returning a process exit code."""
    args = build_parser().parse_args(argv)

    try:
        if args.command == "conv":
            convert(args.input_file, args.output_file, midi_format=args.format)
        elif args.command == "roundtrip":
            roundtrip(args.input_file)
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
