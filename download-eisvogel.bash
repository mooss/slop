#!/usr/bin/env bash
# Download and extract the Eisvogel pandoc LaTeX template if it is not already present.
# The template will be placed in a directory named "eisvogel" in the current working directory.

set -euo pipefail

TEMPLATE_URL="https://github.com/Wandmalfarbe/pandoc-latex-template/releases/download/v3.3.0/Eisvogel-3.3.0.tar.gz"
DEST_DIR="eisvogel"

if [[ -d "$DEST_DIR" ]]; then
    echo "Template directory \"$DEST_DIR\" already exists. Skipping download."
    exit 0
fi

# Use and cleanup a temp dir to download.
TMP_ARCHIVE="$(mktemp --suffix=.tar.gz)"
cleanup() {
    rm -f "$TMP_ARCHIVE"
}
trap cleanup EXIT

if command -v curl >/dev/null 2>&1; then
    curl -L -o "$TMP_ARCHIVE" "$TEMPLATE_URL"
else
    echo "Error: curl is not available." >&2
    exit 1
fi

echo "Extracting template to \"$DEST_DIR\"..."
mkdir -p "$DEST_DIR"
tar -xzf "$TMP_ARCHIVE" --strip-components=1 -C "$DEST_DIR"

echo "Done."
