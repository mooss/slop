#!/usr/bin/env bash
{ # Bypass Bash autoreload.
set -euo pipefail

function topdf(){
    local -r destination="$1"
    pandoc --standalone\
           --from markdown\
           --to latex\
           --output "$destination"\
           --variable geometry:margin=2.5cm\
           --variable papersize:a4\
           --template ./eisvogel/eisvogel.latex\
           --table-of-content\
           --toc-depth 3\
           --variable lang:en\
           --pdf-engine=xelatex
}

function compile-markdown() {
    local -r md_file="$1"
    local clean_path

    clean_path="${md_file#$BASE_PATH}" # Strip the base path (whether absolute or relative).
    clean_path="${clean_path#/}"
    clean_path="${clean_path#./}"

    local pdf_name="${clean_path//\//#}" # Replace '/' with '#' in the path to put everything in a flat dir.
    pdf_name="${pdf_name%.md}.pdf"
    [[ -n "$PREFIX" ]] && pdf_name="${PREFIX}${pdf_name}"
    local -r pdf_output="documentr/${pdf_name}"

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
    echo "Usage: $0 <base_path> [prefix]" >&2
    exit 1
fi

export BASE_PATH="$1"
export PREFIX="${2:-}" # Optional prefix; empty if not supplied.

if [[ ! -d "$BASE_PATH" ]]; then
    echo "Error: '$BASE_PATH' is not a directory or does not exist." >&2
    exit 1
fi

mkdir -vp documentr

#################
# Script proper #

find "$BASE_PATH" -type f -name "*.md" -size 1M | grep -v node_modules | tr '\n' '\0' |
    xargs -0 -P "$(nproc)" -I {} bash -c 'compile-markdown "$1"' _ {}

echo "Conversion complete!"
exit
}
