---
description: Run Lighthouse audit (performance, accessibility, SEO, best practices) and fix issues
allowed-tools: Bash, Read, Edit, Grep, Glob
---

# Lighthouse Audit Command

Run a comprehensive Lighthouse audit and fix any issues found.

## Prerequisites
- Lighthouse CLI must be installed: `npm install -g lighthouse`
- Python 3 must be available (for HTTP server)
- jq must be available (for JSON parsing)

## Instructions

### Step 1: Setup
Create reports directory and start local server:
```bash
mkdir -p .lighthouse-reports
pkill -f "python3 -m http.server 8888" 2>/dev/null || true
python3 -m http.server 8888 > /dev/null 2>&1 &
sleep 2
```

### Step 2: Run Lighthouse Audit
Run Lighthouse with all categories and save JSON output to `.lighthouse-reports/`:
```bash
lighthouse http://localhost:8888/index.html \
  --chrome-flags="--headless" \
  --output=json \
  --output-path=.lighthouse-reports/report.json \
  --quiet 2>/dev/null
```

### Step 3: Parse and Display Results
Extract scores from the JSON report:
```bash
cat .lighthouse-reports/report.json | jq -r '
  "## Lighthouse Scores\n" +
  "| Category | Score |\n|----------|-------|\n" +
  "| Performance | " + (.categories.performance.score * 100 | tostring) + "% |\n" +
  "| Accessibility | " + (.categories.accessibility.score * 100 | tostring) + "% |\n" +
  "| Best Practices | " + (.categories["best-practices"].score * 100 | tostring) + "% |\n" +
  "| SEO | " + (.categories.seo.score * 100 | tostring) + "% |"
'
```

### Step 4: Identify Failing Audits
Extract audits with score < 1 (failing):
```bash
cat .lighthouse-reports/report.json | jq '[.audits | to_entries[] | select(.value.score != null and .value.score < 1 and .value.score != 0) | {id: .key, title: .value.title, score: .value.score}]'
```

### Step 5: Fix Issues
For each failing audit:
1. Read the audit details from the JSON to understand what elements are affected
2. Use Grep/Glob to find the relevant code in the project
3. Use Edit to fix the issue
4. Document what was fixed

Common fixes:
- **aria-allowed-attr**: Remove invalid ARIA attributes or fix role mismatches
- **heading-order**: Ensure headings follow sequential order (h1 -> h2 -> h3)
- **color-contrast**: Increase contrast ratios in CSS
- **image-alt**: Add alt attributes to images
- **meta-description**: Add/improve meta description tag
- **link-text**: Improve link text to be descriptive

### Step 6: Verify Fixes
Re-run the audit to confirm improvements:
```bash
lighthouse http://localhost:8888/index.html \
  --chrome-flags="--headless" \
  --output=json \
  --quiet 2>/dev/null | jq -r '"Final Scores: Performance=" + (.categories.performance.score * 100 | tostring) + "% | Accessibility=" + (.categories.accessibility.score * 100 | tostring) + "% | Best Practices=" + (.categories["best-practices"].score * 100 | tostring) + "% | SEO=" + (.categories.seo.score * 100 | tostring) + "%"'
```

### Step 7: Cleanup
**IMPORTANT**: Always clean up at the end:
```bash
pkill -f "python3 -m http.server 8888" 2>/dev/null || true
rm -r .lighthouse-reports/ *.report.html 2>/dev/null || true
```

## Output Format

```
## Lighthouse Audit Results

### Initial Scores
| Category | Score |
|----------|-------|
| Performance | X% |
| Accessibility | X% |
| Best Practices | X% |
| SEO | X% |

### Issues Found
1. [Issue title] - [Brief description]
   - Fixed: [What was changed]

### Final Scores
| Category | Before | After |
|----------|--------|-------|
| Performance | X% | Y% |
| ... | ... | ... |

### Cleanup
- Deleted .lighthouse-reports/
- Killed HTTP server
```

## Notes
- Reports are stored in `.lighthouse-reports/` which is gitignored
- JetBrains built-in server (port 63342) requires authentication tokens and won't work with Lighthouse
- Always use a standalone HTTP server for reliable results
- The `--headless` flag runs Chrome without a visible window
- **Always run cleanup step** to remove reports and stop server
