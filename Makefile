PYTHON := .venv/bin/python

.PHONY: setup constants test clean

setup:
	uv venv --allow-existing .venv
	uv pip install --python $(PYTHON) mido pyyaml pytest

constants:
	$(PYTHON) scripts/instantiate-constants.py

test:
	$(PYTHON) -m pytest

clean:
	rm -rf .venv .pytest_cache __pycache__ tests/__pycache__ midi_tools/__pycache__
