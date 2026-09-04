#!/bin/bash
set -euo pipefail

if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed." >&2
    exit 1
fi

uv venv .venv
uv pip install mido pyyaml
