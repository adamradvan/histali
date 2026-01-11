#!/usr/bin/env python3
"""Merge all chunk JSON files into final en.json"""

import json
from pathlib import Path

def merge_chunks():
    chunks_dir = Path(__file__).parent.parent / "chunks"
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    all_items = []

    # Read all chunks in order
    for i in range(1, 19):
        chunk_file = chunks_dir / f"chunk-{i:02d}.json"
        if chunk_file.exists():
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                items = chunk_data.get("items", [])
                all_items.extend(items)
                print(f"Chunk {i}: {len(items)} items")

    print(f"\nTotal items before deduplication: {len(all_items)}")

    # Deduplicate by normalized name
    seen = set()
    unique_items = []
    duplicates = []

    for item in all_items:
        # Normalize: lowercase, strip whitespace
        key = item["name"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
        else:
            duplicates.append(item["name"])

    print(f"Duplicates removed: {len(duplicates)}")
    print(f"Unique items: {len(unique_items)}")

    # Add IDs
    for idx, item in enumerate(unique_items, start=1):
        item["id"] = idx

    # Create final structure
    final_data = {
        "foods": unique_items,
        "enums": {
            "histamineLevel": {
                "WELL_TOLERATED": {"value": 0, "label": "Well tolerated", "color": "#4CAF50"},
                "MODERATELY_TOLERATED": {"value": 1, "label": "Moderately tolerated", "color": "#FFC107"},
                "POORLY_TOLERATED": {"value": 2, "label": "Poorly tolerated", "color": "#FF9800"},
                "VERY_POORLY_TOLERATED": {"value": 3, "label": "Very poorly tolerated", "color": "#F44336"},
                "INSUFFICIENT_INFO": {"value": -1, "label": "Insufficient info", "color": "#9E9E9E"},
                "VARIABLE": {"value": -2, "label": "Variable", "color": "#607D8B"}
            },
            "flags": {
                "HIGH_HISTAMINE": {"code": "H", "label": "High histamine content"},
                "FAST_SPOILAGE": {"code": "H!", "label": "Fast spoilage / histamine accumulates quickly"},
                "OTHER_BIOGENIC_AMINES": {"code": "A", "label": "Other biogenic amines"},
                "HISTAMINE_LIBERATOR": {"code": "L", "label": "Histamine liberator"},
                "DAO_BLOCKER": {"code": "B", "label": "DAO blocker"}
            },
            "categories": {
                "ANIMAL_PRODUCTS": {"label": "Animal products"},
                "PLANT_PRODUCTS": {"label": "Plant products"},
                "BEVERAGES": {"label": "Beverages"},
                "FOOD_ADDITIVES": {"label": "Food additives"},
                "DIETARY_SUPPLEMENTS": {"label": "Dietary supplements"},
                "PREPARATIONS": {"label": "Preparations, mixtures"}
            },
            "subcategories": {
                "EGGS": {"label": "Eggs", "category": "ANIMAL_PRODUCTS"},
                "DAIRY": {"label": "Dairy products", "category": "ANIMAL_PRODUCTS"},
                "MEAT": {"label": "Meat", "category": "ANIMAL_PRODUCTS"},
                "FISH": {"label": "Fish", "category": "ANIMAL_PRODUCTS"},
                "SEAFOOD": {"label": "Seafood", "category": "ANIMAL_PRODUCTS"},
                "OTHER": {"label": "Other animal products", "category": "ANIMAL_PRODUCTS"},
                "STARCHES": {"label": "Starch sources", "category": "PLANT_PRODUCTS"},
                "NUTS": {"label": "Nuts, seeds", "category": "PLANT_PRODUCTS"},
                "OILS_FATS": {"label": "Oils, fats", "category": "PLANT_PRODUCTS"},
                "VEGETABLES": {"label": "Vegetables", "category": "PLANT_PRODUCTS"},
                "HERBS": {"label": "Herbs", "category": "PLANT_PRODUCTS"},
                "FRUITS": {"label": "Fruits", "category": "PLANT_PRODUCTS"},
                "MUSHROOMS": {"label": "Mushrooms, algae", "category": "PLANT_PRODUCTS"},
                "SWEETENERS": {"label": "Sweeteners", "category": "PLANT_PRODUCTS"},
                "SPICES": {"label": "Spices", "category": "PLANT_PRODUCTS"},
                "WATER": {"label": "Water", "category": "BEVERAGES"},
                "ALCOHOLIC_BEVERAGES": {"label": "Alcoholic beverages", "category": "BEVERAGES"},
                "CAFFEINE_DRINKS": {"label": "Caffeine drinks, teas", "category": "BEVERAGES"},
                "FRUIT_JUICES": {"label": "Fruit juices", "category": "BEVERAGES"},
                "VEGETABLE_JUICES": {"label": "Vegetable juices", "category": "BEVERAGES"},
                "MILK_SUBSTITUTES": {"label": "Milk substitutes", "category": "BEVERAGES"},
                "SOFT_DRINKS": {"label": "Soft drinks", "category": "BEVERAGES"},
                "FOOD_ADDITIVES": {"label": "Food additives, E-numbers", "category": "FOOD_ADDITIVES"},
                "DIETARY_SUPPLEMENTS": {"label": "Dietary supplements", "category": "DIETARY_SUPPLEMENTS"},
                "PREPARATIONS": {"label": "Preparations, mixtures", "category": "PREPARATIONS"}
            }
        },
        "metadata": {
            "source": "SIGHI Food Compatibility List",
            "language": "en",
            "version": "2024-08-29",
            "totalItems": len(unique_items)
        }
    }

    # Write output
    output_file = output_dir / "en.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {output_file}")
    print(f"Final item count: {len(unique_items)}")

    # Print category breakdown
    print("\nCategory breakdown:")
    categories = {}
    for item in unique_items:
        cat = item.get("category", "UNKNOWN")
        categories[cat] = categories.get(cat, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    return unique_items, duplicates

if __name__ == "__main__":
    merge_chunks()
