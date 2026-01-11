#!/bin/bash
# Reset extraction workspace for new language
# Usage: ./reset.sh [--keep-source]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTRACTION_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${GREEN}[STEP]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

KEEP_SOURCE=false
if [ "$1" == "--keep-source" ]; then
    KEEP_SOURCE=true
fi

echo "This will reset the extraction workspace:"
echo "  - Delete all chunk files"
echo "  - Delete all image files"
echo "  - Delete output files"
echo "  - Reset progress.json"
if [ "$KEEP_SOURCE" = false ]; then
    echo "  - Delete source PDFs (use --keep-source to preserve)"
fi
echo ""
read -p "Continue? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

print_step "Cleaning chunks..."
rm -rf "$EXTRACTION_DIR/chunks"
mkdir -p "$EXTRACTION_DIR/chunks"

print_step "Cleaning images..."
rm -rf "$EXTRACTION_DIR/images"
mkdir -p "$EXTRACTION_DIR/images"

print_step "Cleaning output..."
rm -rf "$EXTRACTION_DIR/output"
mkdir -p "$EXTRACTION_DIR/output"

if [ "$KEEP_SOURCE" = false ]; then
    print_step "Cleaning source PDFs..."
    rm -f "$EXTRACTION_DIR/source/"*.pdf
fi

print_step "Resetting progress.json..."
cat > "$EXTRACTION_DIR/progress.json" << 'EOF'
{
  "language": null,
  "sourceFile": null,
  "totalPages": 0,
  "chunkSize": 2,
  "totalChunks": 0,
  "currentSection": {
    "category": null,
    "subcategory": null
  },
  "lastProcessedChunk": 0,
  "extractedCount": 0,
  "status": "not_initialized",
  "errors": [],
  "chunks": []
}
EOF

print_step "Reset complete!"
echo ""
echo "Next steps:"
echo "  1. Place your PDF in: extraction/source/foodlist-<lang>.pdf"
echo "  2. Run: ./extraction/scripts/setup.sh <lang>"
