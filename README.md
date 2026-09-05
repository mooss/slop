# Stochastic sparrow: learning music composition from examples

## Python setup

Run `scripts/setup-venv.sh` to create a virtual environment and install dependencies.

Activate the environment:
```
source .venv/bin/activate
```

## MIDI <-> YAML conversion

`midi.py` converts from MIDI to YAML and vice-versa, giving some mean to visualize MIDI data as text.

Usage:
- `midi.py conv input.midi output.yaml`
- `midi.py conv input.yaml output.midi`
- `midi.py conv input.midi output.midi --format 0`  # convert MIDI to MIDI with format 0
- `midi.py roundtrip input_file`   # verifies roundtrip conversion
