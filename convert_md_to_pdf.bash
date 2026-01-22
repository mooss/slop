#!/usr/bin/env bash
set -euo pipefail

######################
# Arguments handling #

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Error: Invalid number of arguments." >&2
    echo "Usage: $0 <base_path> [prefix]" >&2
    exit 1
fi

BASE_PATH="$1"
PREFIX="${2:-}"   # Optional prefix; empty if not supplied

if [[ ! -d "$BASE_PATH" ]]; then
    echo "Error: '$BASE_PATH' is not a directory or does not exist." >&2
    exit 1
fi

mkdir -p documenter

#################
# Script proper #

# Skipping large files because they take too long and are probably not what we want.
find "$BASE_PATH" -type f -name "*.md" -size 1M | while read -r md_file; do
    if [[ "$md_file" == *"/documenter/"* ]]; then
        continue
    fi

    # Remove the leading base path (and any leading ./) from the filename to get a clean relative path
    if [[ "$md_file" == "$BASE_PATH"* ]]; then
        clean_path="${md_file#$BASE_PATH/}"
    else
        clean_path="${md_file#./}"
    fi

    pdf_name="${clean_path//\//#}" # Replace '/' with '#' in the path to put everything in a flat dir.
    pdf_name="${pdf_name%.md}.pdf"
    [[ -n "$PREFIX" ]] && pdf_name="${PREFIX}${pdf_name}"

    pdf_output="documenter/${pdf_name}"

    echo "Converting: $md_file -> $pdf_output"
    pandoc "$md_file" -o "$pdf_output" --pdf-engine=xelatex
done

echo "Conversion complete!"
