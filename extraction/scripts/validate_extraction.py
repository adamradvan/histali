#!/usr/bin/env python3
"""Validate extracted data for completeness and consistency."""

import json
from pathlib import Path
from collections import Counter

VALID_LEVELS = {
    "WELL_TOLERATED",
    "MODERATELY_TOLERATED",
    "POORLY_TOLERATED",
    "VERY_POORLY_TOLERATED",
    "INSUFFICIENT_INFO",
    "VARIABLE"
}

VALID_FLAGS = {
    "HIGH_HISTAMINE",
    "FAST_SPOILAGE",
    "OTHER_BIOGENIC_AMINES",
    "HISTAMINE_LIBERATOR",
    "DAO_BLOCKER",
    "INSUFFICIENT_INFO"  # Some items have this as flag
}

VALID_CATEGORIES = {
    "ANIMAL_PRODUCTS",
    "PLANT_PRODUCTS",
    "BEVERAGES",
    "FOOD_ADDITIVES",
    "DIETARY_SUPPLEMENTS",
    "PREPARATIONS"
}

def validate():
    output_file = Path(__file__).parent.parent / "output" / "en.json"

    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    foods = data.get("foods", [])
    errors = []
    warnings = []

    print(f"Validating {len(foods)} food items...\n")

    # Check for required fields
    for item in foods:
        item_id = item.get("id", "?")
        name = item.get("name", "")

        if not name:
            errors.append(f"Item {item_id}: missing name")

        level = item.get("histamineLevel")
        if level not in VALID_LEVELS:
            errors.append(f"Item {item_id} ({name[:30]}): invalid histamine level '{level}'")

        category = item.get("category")
        if category not in VALID_CATEGORIES:
            errors.append(f"Item {item_id} ({name[:30]}): invalid category '{category}'")

        flags = item.get("flags", [])
        for flag in flags:
            if flag not in VALID_FLAGS:
                warnings.append(f"Item {item_id} ({name[:30]}): unknown flag '{flag}'")

    # Check for near-duplicate names (case-insensitive)
    names = [i["name"].lower().strip() for i in foods]
    name_counts = Counter(names)
    duplicates = [n for n, count in name_counts.items() if count > 1]
    if duplicates:
        warnings.append(f"Potential duplicates found: {len(duplicates)}")
        for d in duplicates[:5]:
            warnings.append(f"  - '{d}'")

    # Check histamine level distribution
    level_counts = Counter(item.get("histamineLevel") for item in foods)
    print("Histamine level distribution:")
    for level, count in sorted(level_counts.items(), key=lambda x: -x[1]):
        pct = count / len(foods) * 100
        print(f"  {level}: {count} ({pct:.1f}%)")

    # Check flag distribution
    flag_counts = Counter()
    for item in foods:
        for flag in item.get("flags", []):
            flag_counts[flag] += 1

    print("\nFlag distribution:")
    for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
        print(f"  {flag}: {count}")

    # Check category distribution
    cat_counts = Counter(item.get("category") for item in foods)
    print("\nCategory distribution:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        pct = count / len(foods) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")

    # Summary
    print(f"\n{'='*50}")
    print(f"Validation complete:")
    print(f"  Total items: {len(foods)}")
    print(f"  Errors: {len(errors)}")
    print(f"  Warnings: {len(warnings)}")

    if errors:
        print(f"\nErrors:")
        for e in errors[:10]:
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    if warnings:
        print(f"\nWarnings:")
        for w in warnings[:10]:
            print(f"  - {w}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more")

    # Check expected minimum count
    expected_min = 400
    if len(foods) < expected_min:
        print(f"\n⚠️  Only {len(foods)} items, expected at least {expected_min}")
    else:
        print(f"\n✓ Item count ({len(foods)}) meets expectations")

    return len(errors) == 0

if __name__ == "__main__":
    success = validate()
    exit(0 if success else 1)
