#!/usr/bin/env python3
"""
Step 2: HTML → JSON
Extracts food data from HTML (converted from PDF via pdftohtml) into JSON format.
Supports both pdftohtml format and pdf24 online converter format.

Usage:
    python scripts/html_to_json.py [html_file]

If no html_file is provided, uses the latest file in translations/ folder.
"""

import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from bs4 import BeautifulSoup


# Mapping abbreviations to enum names
FLAG_MAP = {
    "H": "HIGH_HISTAMINE",
    "H!": "FAST_SPOILAGE",
    "A": "OTHER_BIOGENIC_AMINES",
    "L": "HISTAMINE_LIBERATOR",
    "B": "DAO_BLOCKER",
}

HISTAMINE_MAP = {
    "0": "WELL_TOLERATED",
    "1": "MODERATELY_TOLERATED",
    "2": "POORLY_TOLERATED",
    "3": "VERY_POORLY_TOLERATED",
    "?": "INSUFFICIENT_INFO",
    "-": "VARIABLE",
}

# Category mapping
CATEGORY_MAP = {
    "Živočíšne potraviny": "ANIMAL_PRODUCTS",
    "Rastlinné potraviny": "PLANT_PRODUCTS",
}

# Subcategory mapping
SUBCATEGORY_MAP = {
    "vajcia": "EGGS",
    "mliečne výrobky": "DAIRY",
    "mäso": "MEAT",
    "ryby": "FISH",
    "morské plody": "SEAFOOD",
    "mořské plody": "SEAFOOD",
    "ostatné": "OTHER",
    "zelenina": "VEGETABLES",
    "ovocie": "FRUITS",
    "strukoviny": "LEGUMES",
    "orechy": "NUTS",
    "oleje a tuky": "OILS_FATS",
    "zdroje škrobu": "STARCHES",
    "nápoje": "BEVERAGES",
    "bylinky": "HERBS",
    "voda": "WATER",
    "huby": "MUSHROOMS",
    "koreniny": "SPICES",
    "sladidlá": "SWEETENERS",
}


@dataclass
class FoodItem:
    """Food item with properties."""
    name: str
    histamine_level: str = "INSUFFICIENT_INFO"
    flags: list = field(default_factory=list)
    notes: str = ""
    category: str = "OTHER"
    subcategory: str = "OTHER"


def normalize_subcategory(text: str) -> str:
    """Normalize subcategory text to enum value."""
    text_lower = text.lower().strip()

    for key, value in SUBCATEGORY_MAP.items():
        if key in text_lower:
            return value

    # Unknown subcategory - create from text using NFD normalization
    normalized = unicodedata.normalize('NFD', text.upper())
    normalized = re.sub(r'[\u0300-\u036f]', '', normalized)
    normalized = normalized.replace(" ", "_").replace(",", "")
    return normalized


def is_only_flags(text: str) -> bool:
    """Check if text contains only flag abbreviations."""
    parts = text.split()
    return all(p in FLAG_MAP or p == '?' for p in parts) and len(parts) > 0


def parse_flags_from_text(text: str) -> list:
    """Parse flags from a text string like 'H A L'."""
    return [FLAG_MAP[p] for p in text.split() if p in FLAG_MAP]


def add_flags(existing: list, new_flags: list) -> None:
    """Add flags to existing list, avoiding duplicates."""
    for flag in new_flags:
        if flag not in existing:
            existing.append(flag)


def extract_pdftohtml_format(html_content: str) -> list:
    """Extract foods from pdftohtml format (line-based with <br/> tags)."""
    foods = []
    current_category = "ANIMAL_PRODUCTS"
    current_subcategory = "OTHER"
    data_started = False

    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Get all text content, preserving structure
    # pdftohtml uses <b> tags for headers and histamine levels

    lines = []
    for element in soup.body.children if soup.body else []:
        if element.name == 'b':
            lines.append(('bold', element.get_text().replace('\xa0', ' ').strip()))
        elif element.name == 'br':
            continue
        elif hasattr(element, 'name') and element.name == 'a':
            # Skip links
            continue
        elif hasattr(element, 'name') and element.name == 'img':
            # Skip images
            continue
        elif hasattr(element, 'string') and element.string:
            text = element.string.replace('\xa0', ' ').strip()
            if text:
                lines.append(('text', text))

    i = 0
    while i < len(lines):
        line_type, text = lines[i]

        # Skip until we find "Živočíšne potraviny"
        if not data_started:
            if "Živočíšne potraviny" in text:
                data_started = True
                current_category = "ANIMAL_PRODUCTS"
            i += 1
            continue

        # Skip headers and footers
        if any(skip in text for skip in ["Zoznam kompatibilných", "SIGHI", "www.",
                                          "http", "©", "Stav:", "Poznámky SK",
                                          "Označenie SK", "Oznacenie SK"]):
            i += 1
            continue

        # Check for category change
        if line_type == 'bold':
            if "Rastlinné potraviny" in text:
                current_category = "PLANT_PRODUCTS"
                i += 1
                continue
            elif "Živočíšne potraviny" in text:
                current_category = "ANIMAL_PRODUCTS"
                i += 1
                continue

            # Check for subcategory (bold text that's a known subcategory)
            text_lower = text.lower()
            is_subcategory = False
            for subcat_key in SUBCATEGORY_MAP.keys():
                if subcat_key in text_lower:
                    current_subcategory = SUBCATEGORY_MAP[subcat_key]
                    is_subcategory = True
                    break

            if is_subcategory:
                i += 1
                continue

            # Check if it's a histamine level (possibly with flags)
            # Pattern: "0", "1", "2", "3", "?", "-" possibly followed by flags
            histamine_match = re.match(r'^([0-3\?\-])\s*(.*)$', text)
            if histamine_match:
                histamine_level = HISTAMINE_MAP.get(histamine_match.group(1), "INSUFFICIENT_INFO")
                flags_text = histamine_match.group(2).strip()
                flags = parse_flags_from_text(flags_text)

                i += 1

                # Next line(s) might be more flags (plain text), then food name
                while i < len(lines):
                    next_type, next_text = lines[i]
                    next_text_clean = next_text.strip()

                    # Check if it's only flags (like "H A" or "L" or "?")
                    if is_only_flags(next_text_clean):
                        add_flags(flags, parse_flags_from_text(next_text_clean))
                        i += 1
                        continue

                    # Check if it's a single flag
                    if next_text_clean in FLAG_MAP:
                        add_flags(flags, [FLAG_MAP[next_text_clean]])
                        i += 1
                        continue

                    # Skip single "?" as it's often a flag indicator
                    if next_text_clean == '?':
                        i += 1
                        continue

                    # Check if it's the food name (not starting with flags)
                    if next_type == 'text':
                        food_name = next_text_clean
                        i += 1

                        # Collect notes (following text lines until next bold)
                        notes_parts = []
                        while i < len(lines) and lines[i][0] == 'text':
                            note_text = lines[i][1].strip()
                            # Stop if it looks like a new food item (single flag or histamine)
                            if note_text in FLAG_MAP or re.match(r'^[0-3\?\-]$', note_text):
                                break
                            if is_only_flags(note_text):
                                break
                            notes_parts.append(note_text)
                            i += 1

                        # Create food item - validate the name
                        if food_name and len(food_name) > 1:
                            # Skip if food name looks like flags or garbage
                            if not is_only_flags(food_name) and food_name not in ['?', '-']:
                                food = FoodItem(
                                    name=food_name,
                                    histamine_level=histamine_level,
                                    flags=flags,
                                    notes=" ".join(notes_parts),
                                    category=current_category,
                                    subcategory=current_subcategory
                                )
                                foods.append(food)
                        break
                    else:
                        break

                continue

        i += 1

    return foods


def extract_foods(html_path: Path) -> list:
    """Extract foods from pdftohtml HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return extract_pdftohtml_format(content)


def deduplicate_foods(foods: list) -> list:
    """Remove duplicate foods."""
    seen = set()
    unique = []
    for food in foods:
        key = food.name.lower()
        if key not in seen:
            seen.add(key)
            unique.append(food)
    return unique


def create_json_structure(foods: list) -> dict:
    """Create final JSON structure."""
    subcategory_labels = {v: k.title() for k, v in SUBCATEGORY_MAP.items()}

    return {
        "foods": [
            {
                "id": i + 1,
                "category": f.category,
                "subcategory": f.subcategory,
                "name": f.name,
                "histamineLevel": f.histamine_level,
                "flags": f.flags,
                "notes": f.notes
            }
            for i, f in enumerate(foods)
        ],
        "enums": {
            "category": {
                "ANIMAL_PRODUCTS": "Živočíšne potraviny",
                "PLANT_PRODUCTS": "Rastlinné potraviny"
            },
            "subcategory": subcategory_labels,
            "histamineLevel": {
                "WELL_TOLERATED": {"value": "0", "label": "Dobre tolerované", "color": "#22c55e"},
                "MODERATELY_TOLERATED": {"value": "1", "label": "Stredne tolerované", "color": "#eab308"},
                "POORLY_TOLERATED": {"value": "2", "label": "Zle tolerované", "color": "#f97316"},
                "VERY_POORLY_TOLERATED": {"value": "3", "label": "Veľmi zle tolerované", "color": "#ef4444"},
                "INSUFFICIENT_INFO": {"value": "?", "label": "Nedostatočné informácie", "color": "#6b7280"},
                "VARIABLE": {"value": "-", "label": "Individuálne", "color": "#6b7280"}
            },
            "flag": {
                "HIGH_HISTAMINE": {"abbr": "H", "label": "Vysoký obsah histamínu"},
                "FAST_SPOILAGE": {"abbr": "H!", "label": "Rýchla tvorba histamínu"},
                "OTHER_BIOGENIC_AMINES": {"abbr": "A", "label": "Iné biogénne amíny"},
                "HISTAMINE_LIBERATOR": {"abbr": "L", "label": "Liberátor histamínu"},
                "DAO_BLOCKER": {"abbr": "B", "label": "Blokátor DAO"}
            }
        }
    }


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent  # Root project directory

    # Accept HTML path as command line argument, default to translations folder
    if len(sys.argv) > 1:
        html_path = Path(sys.argv[1])
    else:
        # Try to find latest file in source/translations/ folder
        translations_dir = project_dir / "source" / "translations"
        if translations_dir.exists():
            html_files = sorted(translations_dir.glob("translated-*.html"), reverse=True)
            if html_files:
                html_path = html_files[0]
                print(f"Using latest translation: {html_path.name}")
            else:
                html_path = project_dir / "foodlist.html"
        else:
            html_path = project_dir / "foodlist.html"

    output_path = project_dir / "data" / "sk.json"

    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}")
        print("Run ./scripts/pdf_to_html.sh first to generate the HTML file")
        sys.exit(1)

    print(f"Loading {html_path}...")
    foods = extract_foods(html_path)
    print(f"Found {len(foods)} food items")

    print("Removing duplicates...")
    foods = deduplicate_foods(foods)
    print(f"Unique items: {len(foods)}")

    print("Creating JSON...")
    data = create_json_structure(foods)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Saved to {output_path}")

    # Print first 10 items for verification
    print("\nFirst 10 items:")
    for food in data["foods"][:10]:
        flags_str = ", ".join(food['flags']) if food['flags'] else "none"
        print(f"  [{food['histamineLevel'][:4]}] {food['name']} (flags: {flags_str})")

    # Statistics
    print(f"\nStatistics:")
    hist_counts = {}
    for f in data["foods"]:
        h = f["histamineLevel"]
        hist_counts[h] = hist_counts.get(h, 0) + 1
    for level, count in sorted(hist_counts.items()):
        print(f"  {level}: {count}")


if __name__ == "__main__":
    main()
