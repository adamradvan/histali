#!/bin/bash
# Step 1: PDF → HTML
# Converts foodlist.pdf to HTML using poppler's pdftohtml
# Output: translations/translated-{ISO-date}.html
#
# Usage: ./pdf_to_html.sh [pdf_file]
#   pdf_file: Optional, defaults to foodlist.pdf

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PDF_FILE="${1:-$SCRIPT_DIR/foodlist.pdf}"
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="$SCRIPT_DIR/translations"
OUTPUT_FILE="$OUTPUT_DIR/translated-$DATE.html"

# Check if pdftohtml is installed
if ! command -v pdftohtml &> /dev/null; then
    echo "Error: pdftohtml not found. Install with: brew install poppler"
    exit 1
fi

# Check if PDF exists
if [ ! -f "$PDF_FILE" ]; then
    echo "Error: PDF file not found: $PDF_FILE"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Convert PDF to HTML
echo "Converting $PDF_FILE to HTML..."
pdftohtml -noframes -enc UTF-8 "$PDF_FILE" "$OUTPUT_FILE"

echo "Done! Output: $OUTPUT_FILE"
echo ""
echo "Next step (Step 2: HTML → JSON):"
echo "  python html_to_json.py"
