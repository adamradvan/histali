# Verify Sync Command

Verify that all configuration files are in sync with the actual file structure.

## Instructions

Perform these verification checks and report results in a table:

### 1. Service Worker Assets (sw.js)
Read `sw.js` and extract the `ASSETS_TO_CACHE` array. For each path (remove `/histali/` prefix):
- Check if the file exists in the project
- Report: path, exists (yes/no)

### 2. robots.txt Directories
Read `robots.txt` and extract `Disallow:` and `Allow:` paths:
- Check if each directory exists
- Report: path, type (disallow/allow), exists (yes/no)

### 3. manifest.json Icons
Read `manifest.json` and extract icon `src` paths:
- Check if each icon file exists
- Report: path, exists (yes/no)

### 4. URL Consistency
Extract URLs from:
- `index.html`: canonical (`<link rel="canonical">`), og:url, twitter:url, hreflang
- `sitemap.xml`: `<loc>` tags

Check all URLs use the same base: `https://adamradvan.github.io/histali/`
- Report: source file, URL, matches base (yes/no)

### 5. Script Path References
Check that scripts reference valid paths:
- `scripts/pdf_to_html.sh`: `source/foodlist.pdf`, `source/translations/`
- `scripts/html_to_json.py`: `source/translations/`
- `scripts/clean_html.py`: `source/pdf24.html`

Report: script, referenced path, exists (yes/no)

## Output Format

```
## Sync Verification Results

### 1. Service Worker Assets
| Path | Exists |
|------|--------|
| index.html | ✓ |
| ... | ... |

### 2. robots.txt Directories
| Path | Type | Exists |
|------|------|--------|
| /scripts/ | Disallow | ✓ |
| ... | ... | ... |

### 3. manifest.json Icons
| Path | Exists |
|------|--------|
| icons/icon-192.png | ✓ |
| ... | ... |

### 4. URL Consistency
| Source | URL | Valid |
|--------|-----|-------|
| canonical | https://... | ✓ |
| ... | ... | ... |

### 5. Script Paths
| Script | Path | Exists |
|--------|------|--------|
| pdf_to_html.sh | source/foodlist.pdf | ✓ |
| ... | ... | ... |

## Summary
- Total checks: X
- Passed: X
- Failed: X

[List any failures with suggested fixes]
```

Use ✓ for pass, ✗ for fail.
