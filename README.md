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
- `midi.py midi2yaml input.midi output.yaml`
- `midi.py yaml2midi input.yaml output.midi`
