# Bulk Markdown to PDF converter

Recursively convert Markdown files to beautiful PDFs using Pandoc.
All generated PDFs are placed in a single `documenter` directory.

The file hierarchy is flattened by replacing path separators (`/`) with `#` in the output filenames.
This keeps all PDFs together while preserving a hint of their original location.
