---
name: research-study
description: Add or update a The Other Details study page in the Zeroing site's The Other Details section (public/the-other-details/), from verified data to built page.
---

# Add a research study

1. **Research first.** Use the `tod-research-desk` skill. Trace each number to the report that first published it. Record the claim, the value, the source with its date, and a verdict:
   - `current`: primary source, recent.
   - `outdated`: older than about two years and still quoted.
   - `check`: second-hand, or it doesn't reconcile.
   - `excluded`: no named source.
2. **Pick the chart per number.** Follow `tod-visual-storytelling`:
   - proportional squares for "N times"
   - a fan for forecasts (dashed)
   - a unit grid or waffle for shares
   - isotype for people
   - lines for time
3. **Media.** Use real footage only (Pexels or your own). Save `src/research/media/NAME.mp4` (720p, about 8s, no audio, under 1.5MB) and `NAME.jpg` as the poster.
4. **Write the entry.** Copy an object in `src/research/studies.json`. `chapters[].fig` names the chart. Leave `""` for no chart, or add a block to `src/research/charts.js` that draws into `F('f-NAME')`. Leave `reel` as `""` until the film exists.
5. **House rules:**
   - The lab is "The Other Details", never "Zeroing lab".
   - No dashes in prose and no months or seasons in headlines.
   - Fair and non-partisan.
   - Sources on screen.
   - Ending: "© Zeroing · The Other Details".
6. **Build and check.** Run `TAILWIND=/path/to/tailwindcss python3 build.py`. Then open `public/the-other-details/` at 1280px and 390px and confirm there is no horizontal scroll, the labels sit on their marks, and every ledger row has a verdict.
7. **Ship.** Commit on a branch, open a PR and merge. Cloudflare Pages deploys `public/`.

Connectors: GitHub (push), Cloudflare (deploy). Optional: Google Drive, Consensus, Twelve Data.
