# Bulk Markdown to PDF compiler (native pandoc)

Recursively convert Markdown files to beautiful PDFs using Pandoc.
All generated PDFs are placed in a single `documentr` directory.

The file hierarchy is flattened by replacing path separators (`/`) with `#` in the output filenames.
This keeps all PDFs together while preserving a hint of their original location.

## Requirements

This requires a functional pandoc and LaTeX installation, as well as downloading the Eisvogel template (`download-eisvogel.bash`).
