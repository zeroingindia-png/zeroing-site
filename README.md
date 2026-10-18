# Zeroing website

Static site on Cloudflare Pages, with one Pages Function for the forms.

- `public/` is what goes live. `wrangler.toml` tells Cloudflare to serve it and binds the `zeroing-forms` D1 database as `DB`.
- `functions/api/submit.js` receives every form (join, guest, contact, details, newsletter) and stores it in the `submissions` table.
- `src/` holds the page sources, shared header, closing section, styles and script. `src/logo_path.txt` is the Zeroing mark.
- Run `python3 build.py` after editing `src/` to regenerate every page in `public/`.
- Brand details and episode links live at the top of `build.py`.
