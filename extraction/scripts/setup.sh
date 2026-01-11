#!/bin/bash
# Setup script for PDF extraction
# Usage: ./setup.sh <language-code> [pdf-path]
# Example: ./setup.sh sk extraction/source/foodlist-sk.pdf

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACTION_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() { echo -e "${GREEN}[STEP]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check arguments
if [ -z "$1" ]; then
    echo "Usage: $0 <language-code> [pdf-path]"
    echo "Example: $0 sk extraction/source/foodlist-sk.pdf"
    echo ""
    echo "Language codes: en, sk, de, etc."
    exit 1
fi

LANG_CODE="$1"
PDF_PATH="${2:-$EXTRACTION_DIR/source/foodlist-$LANG_CODE.pdf}"

# Validate PDF exists
if [ ! -f "$PDF_PATH" ]; then
    print_error "PDF not found: $PDF_PATH"
    echo "Please place the PDF at: $PDF_PATH"
    echo "Or specify the path: $0 $LANG_CODE /path/to/file.pdf"
    exit 1
fi

print_step "Setting up extraction for language: $LANG_CODE"
print_step "PDF source: $PDF_PATH"

# Check for pdftoppm (poppler)
if ! command -v pdftoppm &> /dev/null; then
    print_error "pdftoppm not found. Install poppler:"
    echo "  macOS: brew install poppler"
    echo "  Ubuntu: sudo apt-get install poppler-utils"
    exit 1
fi

# Create directories
print_step "Creating directories..."
mkdir -p "$EXTRACTION_DIR/images"
mkdir -p "$EXTRACTION_DIR/chunks"
mkdir -p "$EXTRACTION_DIR/output"

# Clean existing files
print_step "Cleaning existing extraction data..."
rm -f "$EXTRACTION_DIR/images/"*.png
rm -f "$EXTRACTION_DIR/chunks/"*.json
rm -f "$EXTRACTION_DIR/output/"*.json

# Convert PDF to images
print_step "Converting PDF to PNG images (300 DPI)..."
pdftoppm -png -r 300 "$PDF_PATH" "$EXTRACTION_DIR/images/page"

# Rename to consistent format (page-01.png, page-02.png, etc.)
print_step "Renaming images to consistent format..."
cd "$EXTRACTION_DIR/images"
for f in page-*.png; do
    if [[ $f =~ page-([0-9]+)\.png ]]; then
        num="${BASH_REMATCH[1]}"
        # Pad to 2 digits
        padded=$(printf "%02d" "$num")
        mv "$f" "page-$padded.png" 2>/dev/null || true
    fi
done

# Count pages
PAGE_COUNT=$(ls -1 "$EXTRACTION_DIR/images/"page-*.png 2>/dev/null | wc -l | tr -d ' ')

if [ "$PAGE_COUNT" -eq 0 ]; then
    print_error "No pages extracted from PDF!"
    exit 1
fi

print_step "Extracted $PAGE_COUNT pages"

# Calculate chunks (2 pages per chunk)
CHUNK_SIZE=2
TOTAL_CHUNKS=$(( (PAGE_COUNT + CHUNK_SIZE - 1) / CHUNK_SIZE ))

# Create progress.json
print_step "Creating progress.json..."
CHUNKS_JSON="["
for i in $(seq 1 $TOTAL_CHUNKS); do
    START_PAGE=$(( (i - 1) * CHUNK_SIZE + 1 ))
    END_PAGE=$(( i * CHUNK_SIZE ))
    if [ $END_PAGE -gt $PAGE_COUNT ]; then
        END_PAGE=$PAGE_COUNT
    fi

    if [ $i -gt 1 ]; then
        CHUNKS_JSON+=","
    fi
    CHUNKS_JSON+="
    { \"chunkId\": $i, \"pages\": [$START_PAGE, $END_PAGE], \"status\": \"pending\", \"itemsExtracted\": 0 }"
done
CHUNKS_JSON+="
  ]"

cat > "$EXTRACTION_DIR/progress.json" << EOF
{
  "language": "$LANG_CODE",
  "sourceFile": "$PDF_PATH",
  "totalPages": $PAGE_COUNT,
  "chunkSize": $CHUNK_SIZE,
  "totalChunks": $TOTAL_CHUNKS,
  "currentSection": {
    "category": null,
    "subcategory": null
  },
  "lastProcessedChunk": 0,
  "extractedCount": 0,
  "status": "ready",
  "errors": [],
  "chunks": $CHUNKS_JSON
}
EOF

print_step "Setup complete!"
echo ""
echo "Summary:"
echo "  Language: $LANG_CODE"
echo "  Pages: $PAGE_COUNT"
echo "  Chunks: $TOTAL_CHUNKS (2 pages each)"
echo ""
echo "Next steps:"
echo "  1. Run Claude with: /extract-pdf"
echo "  2. Or manually extract chunks using Claude's vision"
echo "  3. Then run: python3 extraction/scripts/merge_chunks.py"
echo "  4. Finally: python3 extraction/scripts/validate_extraction.py"