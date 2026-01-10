# Histali

[![GitHub Pages](https://img.shields.io/badge/demo-live-brightgreen)](https://adamradvan.github.io/histali/)
[![PWA Ready](https://img.shields.io/badge/PWA-ready-blue)](https://adamradvan.github.io/histali/)

A searchable food compatibility guide for people with histamine intolerance. Works offline as a Progressive Web App.

**<a href="https://adamradvan.github.io/histali/" target="_blank">Try it Now</a>**

---

## Features

- **Instant Search** — Filter 460+ foods with accent-insensitive matching
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

After cloning, set up git hooks:

```bash
git config core.hooksPath .hooks
```

This enables the pre-commit hook that auto-updates the service worker cache version.

## License

Code is open source. Food data is subject to SIGHI's non-commercial use terms with required attribution.
