#!/usr/bin/env bash
{ # Bypass Bash autoreload.
set -euo pipefail

# Determine script directory for absolute template path.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export SCRIPT_DIR

function topdf(){
    local -r destination="$1"
    pandoc --standalone\
           --from markdown\
           --to latex\
           --output "$destination"\
           --variable geometry:margin=2.5cm\
           --variable papersize:a4\
           --template "$SCRIPT_DIR/eisvogel/eisvogel.latex"\
           --table-of-content\
           --toc-depth 3\
           --variable lang:en\
           --pdf-engine=xelatex
}

function compile-markdown() {
    local -r md_file="$1"
    local -r output_mode="${2:-dir}" # "single" or "dir"

    local pdf_output

    if [[ "$output_mode" == "single" ]]; then
        local -r single_pdf_name="${PREFIX}$(basename -- "$md_file" .md).pdf"
        pdf_output="$(dirname "$md_file")/${single_pdf_name}"
    else
        local clean_path
        clean_path="${md_file#$BASE_PATH}" # Strip the base path (whether absolute or relative).
        clean_path="${clean_path#/}"
        clean_path="${clean_path#./}"

        local dir_pdf_name="${clean_path//\//#}" # Replace '/' with '#' in the path to put everything in a flat dir.
        dir_pdf_name="${dir_pdf_name%.md}.pdf"
        [[ -n "$PREFIX" ]] && dir_pdf_name="${PREFIX}${dir_pdf_name}"
        pdf_output="documentr/${dir_pdf_name}"
    fi

    if [[ -f "$pdf_output" && "$pdf_output" -nt "$md_file" ]]; then
        echo "Skipping: $md_file is older than $pdf_output"
        return
    fi

    echo "Converting: $md_file -> $pdf_output"
    mkdir -vp "$(dirname "$pdf_output")"
    cat "$md_file" | topdf "$pdf_output"
}

# Export functions so they are available in subshells spawned by xargs.
export -f topdf compile-markdown

######################
# Arguments handling #

if [[ $# -lt 1 || $# -gt 2 ]]; then
    echo "Error: Invalid number of arguments." >&2
    echo "Usage: $0 <base_path_or_md_file> [prefix]" >&2
    exit 1
fi

if [[ -f "$1" ]]; then
    INPUT_TYPE="file"
    SINGLE_FILE="$1"
    BASE_PATH="$(dirname -- "$1")"
elif [[ -d "$1" ]]; then
    INPUT_TYPE="dir"
    BASE_PATH="$1"
else
    echo "Error: '$1' is neither a Markdown file nor a directory." >&2
    exit 1
fi

export BASE_PATH
export PREFIX="${2:-}" # Optional prefix; empty if not supplied.

#################
# Script proper #

if [[ "$INPUT_TYPE" == "file" ]]; then
    compile-markdown "$SINGLE_FILE" "single"
else
    mkdir -vp documentr
    find "$BASE_PATH" -type f -name "*.md" -size 1M | grep -v node_modules | tr '\n' '\0' |
        xargs -0 -P "$(nproc)" -I {} bash -c 'compile-markdown "$1"' _ {}
fi

echo "Conversion complete!"
exit
}
