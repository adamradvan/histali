# Histali

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://adamradvan.github.io/histali/)
[![PWA Ready](https://img.shields.io/badge/PWA-ready-blue)](https://adamradvan.github.io/histali/)

A searchable food compatibility guide for people with histamine intolerance. Works offline as a Progressive Web App.

**<a href="https://adamradvan.github.io/histali/" target="_blank">Try it Now</a>**

---

## Features

- **Instant Search** — Filter 880+ foods with accent-insensitive matching
- **Multi-Filter** — Filter by histamine level, subcategory, and flags (shareable via URL)
- **Histamine Levels** — Color-coded compatibility ratings (well tolerated → very poorly tolerated)
- **Detailed Info** — Flags for histamine content (H), liberators (L), DAO blockers (B), and more
- **Works Offline** — Install as a PWA on mobile or desktop
- **Fast & Lightweight** — Pure HTML/CSS/JS, no frameworks

## Install on Your Phone

Add Histali to your home screen for quick access and offline use.

**iPhone / iPad:**
1. Open [Histali](https://adamradvan.github.io/histali/) in Safari
2. Tap the **Share** button (square with arrow)
3. Scroll down and tap **Add to Home Screen**

**Android:**
1. Open [Histali](https://adamradvan.github.io/histali/) in Chrome
2. Tap the **three-dot menu** (⋮)
3. Tap **Add to Home Screen** or **Install App**

## Data Source

Food compatibility data is sourced from the **SIGHI Food Compatibility List** by Heinz Lamprecht.

> © SIGHI — [mastzellaktivierung.info](https://www.mastzellaktivierung.info)

This data is for informational purposes only. Always consult a healthcare professional for medical advice.

## Development

### Prerequisites

- Node.js (v18+)

### Setup

```bash
# Clone the repo
git clone https://github.com/adamradvan/histali.git
cd histali

# Install dependencies
npm install

# Set up git hooks
git config core.hooksPath .hooks
```

### Build

The project uses Tailwind CSS v4. CSS is built from `src/input.css` to `dist/output.css`.

```bash
# Build CSS (minified)
npm run build:css

# Watch mode for development
npm run watch:css
```

### Project Structure

```
histali/
├── index.html          # Main app (single-page)
├── dist/output.css     # Built Tailwind CSS (committed)
├── src/input.css       # Tailwind source + custom styles
├── data/               # Food data (sk.json, en.json)
├── i18n/               # UI translations
├── sw.js               # Service worker for offline
└── .hooks/pre-commit   # Auto-builds CSS & updates SW cache
```

### How It Works

1. **No build step required for HTML/JS** — Pure vanilla JS, no bundler
2. **Tailwind CSS is pre-built** — `dist/output.css` is committed to the repo
3. **Pre-commit hook** — Automatically rebuilds CSS and updates service worker cache version before each commit
4. **GitHub Pages** — Serves static files directly, no CI/CD build step needed

## License

Code is open source. Food data is subject to SIGHI's non-commercial use terms with required attribution.
