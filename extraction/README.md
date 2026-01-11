# SIGHI Food List PDF Extraction

Automated extraction pipeline for SIGHI food compatibility PDFs using Claude's vision capabilities.

## Quick Start

```bash
# 1. Place PDF in source folder
cp ~/Downloads/foodlist-sk.pdf extraction/source/

# 2. Setup extraction (converts PDF to images, initializes progress)
./extraction/scripts/setup.sh sk

# 3. Run Claude extraction command
# In Claude Code, run: /extract-pdf

# 4. After extraction completes, merge and validate
python3 extraction/scripts/merge_chunks.py
python3 extraction/scripts/validate_extraction.py

# 5. Copy to data folder
cp extraction/output/sk.json data/sk.json
```

## Directory Structure

```
extraction/
├── source/           # Place source PDFs here
│   └── foodlist-<lang>.pdf
├── images/           # Generated PNG images (300 DPI)
│   └── page-01.png, page-02.png, ...
├── chunks/           # Extracted chunk JSONs
│   └── chunk-01.json, chunk-02.json, ...
├── output/           # Merged output
│   └── <lang>.json
├── scripts/
│   ├── setup.sh      # Initialize extraction
│   ├── reset.sh      # Clean for new language
│   ├── merge_chunks.py
│   └── validate_extraction.py
├── progress.json     # Extraction state tracking
├── schema.json       # Reference schema
└── README.md
```

## Scripts

### setup.sh
Prepares extraction for a new language:
- Converts PDF to PNG images (300 DPI)
- Creates progress.json with chunk tracking
- Requires `poppler` (pdftoppm)

```bash
./extraction/scripts/setup.sh <lang> [pdf-path]
# Example: ./extraction/scripts/setup.sh sk
# Example: ./extraction/scripts/setup.sh de ~/Downloads/foodlist-de.pdf
```

### reset.sh
Cleans extraction workspace for a new language:
```bash
./extraction/scripts/reset.sh           # Full reset
./extraction/scripts/reset.sh --keep-source  # Keep PDFs
```

### merge_chunks.py
Merges all chunk files into final output:
- Deduplicates items by name
- Adds sequential IDs
- Outputs to `extraction/output/<lang>.json`

```bash
python3 extraction/scripts/merge_chunks.py [lang]
```

### validate_extraction.py
Validates extracted data:
- Checks required fields
- Validates enums
- Reports statistics

```bash
python3 extraction/scripts/validate_extraction.py
```

## Claude Extraction Command

Use `/extract-pdf` in Claude Code to run the extraction. The command:
1. Reads `progress.json` to find pending chunks
2. Uses vision to read page images
3. Extracts structured data from tables
4. Writes chunk JSON files
5. Updates progress

Run multiple times to process in batches (recommended: 4-6 chunks per session).

## Data Schema

### Food Item
```json
{
  "id": 1,
  "name": "Food name",
  "histamineLevel": "WELL_TOLERATED",
  "flags": ["HIGH_HISTAMINE", "HISTAMINE_LIBERATOR"],
  "notes": "Optional notes",
  "category": "ANIMAL_PRODUCTS",
  "subcategory": "DAIRY"
}
```

### Histamine Levels
| PDF Symbol | Enum | Meaning |
|------------|------|---------|
| 0 (green) | WELL_TOLERATED | Safe to eat |
| 1 (yellow) | MODERATELY_TOLERATED | Eat with caution |
| 2 (orange) | POORLY_TOLERATED | Avoid or limit |
| 3 (red) | VERY_POORLY_TOLERATED | Avoid |
| ? | INSUFFICIENT_INFO | Unknown |
| - | VARIABLE | Depends on preparation |

### Flags
| PDF Code | Enum | Meaning |
|----------|------|---------|
| H | HIGH_HISTAMINE | High histamine content |
| H! | FAST_SPOILAGE | Histamine accumulates quickly |
| A | OTHER_BIOGENIC_AMINES | Contains other biogenic amines |
| L | HISTAMINE_LIBERATOR | Triggers histamine release |
| B | DAO_BLOCKER | Blocks DAO enzyme |

## Troubleshooting

### "pdftoppm not found"
Install poppler:
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

### Low quality images
The setup script uses 300 DPI. For higher quality:
```bash
pdftoppm -png -r 400 input.pdf output
```

### Extraction errors
Check `progress.json` for error tracking. Re-run `/extract-pdf` to continue from last successful chunk.
