# Extract PDF Food Data

Extract structured food compatibility data from SIGHI PDF using vision capabilities.

## Prerequisites

Before running this command:
1. Ensure PDF exists at `source/foodlist-<lang>.pdf`
2. Run `./extraction/scripts/setup.sh <lang>` to convert PDF to images

## Instructions

Read the progress file at `extraction/progress.json` to understand current state.

### If status is "not_initialized" or "ready"
Start fresh extraction from chunk 1.

### If status is "in_progress"
Continue from `lastProcessedChunk + 1`.

### If status is "completed"
Inform user extraction is complete and suggest running merge/validate scripts.

## Extraction Process

For each pending chunk:

1. **Read the page images** using the Read tool:
   - `extraction/images/page-XX.png` (2 pages per chunk)

2. **Extract food items** from the table with these fields:
   - `name`: Food name (English designation)
   - `histamineLevel`: One of: WELL_TOLERATED (0), MODERATELY_TOLERATED (1), POORLY_TOLERATED (2), VERY_POORLY_TOLERATED (3), INSUFFICIENT_INFO (?), VARIABLE (-)
   - `flags`: Array of: HIGH_HISTAMINE (H), FAST_SPOILAGE (H!), OTHER_BIOGENIC_AMINES (A), HISTAMINE_LIBERATOR (L), DAO_BLOCKER (B)
   - `notes`: Remarks from the table
   - `category`: Current category header
   - `subcategory`: Current subcategory header

3. **Track section changes**: When you see a new category/subcategory header, update the tracking.

4. **Write chunk JSON** to `extraction/chunks/chunk-XX.json`:
```json
{
  "chunkId": X,
  "pages": [X, Y],
  "sectionUpdates": [{"page": X, "category": "...", "subcategory": "..."}],
  "items": [...],
  "endState": {"category": "...", "subcategory": "..."}
}
```

5. **Update progress.json** after each chunk:
   - Mark chunk as "completed"
   - Update `lastProcessedChunk`
   - Update `extractedCount`
   - Update `currentSection`

## Category Mappings

| PDF Header | Category Enum |
|------------|---------------|
| Animal Products / Eggs | ANIMAL_PRODUCTS / EGGS |
| Animal Products / Dairy | ANIMAL_PRODUCTS / DAIRY |
| Animal Products / Meat | ANIMAL_PRODUCTS / MEAT |
| Animal Products / Fish | ANIMAL_PRODUCTS / FISH |
| Animal Products / Seafood | ANIMAL_PRODUCTS / SEAFOOD |
| Plant Products / Starch sources | PLANT_PRODUCTS / STARCHES |
| Plant Products / Nuts | PLANT_PRODUCTS / NUTS |
| Plant Products / Oils, fats | PLANT_PRODUCTS / OILS_FATS |
| Plant Products / Vegetables | PLANT_PRODUCTS / VEGETABLES |
| Plant Products / Herbs | PLANT_PRODUCTS / HERBS |
| Plant Products / Fruits | PLANT_PRODUCTS / FRUITS |
| Plant Products / Mushrooms | PLANT_PRODUCTS / MUSHROOMS |
| Plant Products / Sweeteners | PLANT_PRODUCTS / SWEETENERS |
| Plant Products / Spices | PLANT_PRODUCTS / SPICES |
| Beverages / Water | BEVERAGES / WATER |
| Beverages / Alcoholic | BEVERAGES / ALCOHOLIC_BEVERAGES |
| Beverages / Caffeine | BEVERAGES / CAFFEINE_DRINKS |
| Food additives | FOOD_ADDITIVES / FOOD_ADDITIVES |
| Dietary supplements | DIETARY_SUPPLEMENTS / DIETARY_SUPPLEMENTS |
| Preparations | PREPARATIONS / PREPARATIONS |

## Histamine Level Mapping

| Symbol | Enum |
|--------|------|
| 0 (green) | WELL_TOLERATED |
| 1 (yellow) | MODERATELY_TOLERATED |
| 2 (orange) | POORLY_TOLERATED |
| 3 (red) | VERY_POORLY_TOLERATED |
| ? | INSUFFICIENT_INFO |
| - | VARIABLE |

## Batch Processing

Process chunks in batches for efficiency:
- Ask user how many chunks to process (suggest 4-6 at a time)
- After each batch, update progress and summarize
- User can run `/extract-pdf` again to continue

## After Extraction Complete

When all chunks are done:
1. Run `python3 extraction/scripts/merge_chunks.py`
2. Run `python3 extraction/scripts/validate_extraction.py`
3. Copy result: `cp extraction/output/<lang>.json data/<lang>.json`

## Example Workflow

```
User: /extract-pdf
Claude: Reading progress.json... Found 18 chunks, 0 completed.
        How many chunks should I process? (recommend 4-6)
User: 6
Claude: Processing chunks 1-6...
        [extracts and creates chunk files]
        Done! 6/18 chunks complete, ~200 items extracted.
        Run /extract-pdf to continue.
```