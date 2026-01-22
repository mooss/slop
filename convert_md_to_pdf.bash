#!/usr/bin/env bash
set -euo pipefail

######################
# Arguments handling #

if [[ $# -ne 1 ]]; then
    echo "Error: Missing required argument." >&2
    echo "Usage: $0 <base_path>" >&2
    exit 1
fi

BASE_PATH="$1"

if [[ ! -d "$BASE_PATH" ]]; then
    echo "Error: '$BASE_PATH' is not a directory or does not exist." >&2
    exit 1
fi

mkdir -p documenter

#################
# Script proper #

find "$BASE_PATH" -name "*.md" -type f | while read -r md_file; do
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
    pdf_output="documenter/${pdf_name}"

    echo "Converting: $md_file -> $pdf_output"
    pandoc "$md_file" -o "$pdf_output"
done

echo "Conversion complete!"
