# Zeroing website

Static site on Cloudflare Pages, with one Pages Function for the forms.

- `public/` is what goes live. `wrangler.toml` tells Cloudflare to serve it and binds the `zeroing-forms` D1 database as `DB`.
- `functions/api/submit.js` receives every form (join, guest, contact, details, newsletter) and stores it in the `submissions` table.
- `src/` holds the page sources, shared header, closing section, styles and script. `src/logo_path.txt` is the Zeroing mark.
- Run `python3 build.py` after editing `src/` to regenerate every page in `public/`.
- Brand details and episode links live at the top of `build.py`.

## Research section (The Other Details)

`public/the-other-details/` is The Other Details, the research lab, and holds the lab's studies: a landing page, one page per study and a method page. Everything is generated, so edit the sources only.

| File | What it is |
| --- | --- |
| `src/research/studies.json` | One entry per study: hero video, stats, glossary, chapters, takeaways, reel and the verdict ledger |
| `research.py` | Turns the JSON into pages (called at the end of `build.py`) |
| `src/research/input.css` + `tailwind.config.js` | Tailwind: house palette, Fontshare type, a few components |
| `src/research/charts.js` | The SVG charts, drawn into `<div id="f-NAME">` |
| `src/research/media/` | Pexels loops (`NAME.mp4` + `NAME.jpg` poster) and reels |

Build with the Tailwind standalone CLI (v3.4) on your path, or point to it:

```
TAILWIND=/path/to/tailwindcss python3 build.py
```

Without the CLI the pages still build and the last `lab.css` is kept.

**Add a study:** copy an entry in `studies.json`, give it a new `slug`, add its media and, if it needs a new chart, a block in `charts.js` named after the chapter's `fig`. Every ledger row needs a verdict: `current`, `outdated`, `check` or `excluded`. The repo skill `.claude/skills/research-study/` walks through it.

**Tools that help:** the `tod-research-desk`, `tod-visual-storytelling` and `tod-marketing-desk` skills; the GitHub connector to push; Cloudflare to deploy Pages. Optional: Google Drive for source PDFs, Consensus for papers, Twelve Data for prices.

## Edit words and photos (no code)

1. Go to https://app.pagescms.org and sign in with GitHub.
2. Open `zeroingindia-png/zeroing-site`. You get three forms: **Home page**, **Brands**, **Podcast**.
3. Change text, or click a photo to upload a new one. Press **Save**.
4. Cloudflare rebuilds the site in about a minute.

The words and photos live in `content/home.json`, `content/brands.json`, `content/podcast.json` and `public/media/`.
Other pages (community, join, contact, legal) are in `src/pages/*.html` and can be edited on GitHub directly.
Keep photos under about 500 KB (1600 px on the long side is plenty).

Cloudflare Pages settings: build command `python3 build.py`, output directory `public`.
