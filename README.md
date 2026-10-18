# Zeroing website

Static site served by Cloudflare Pages.

- `public/` is what goes live. Cloudflare build output directory: `public`. No build command.
- `src/home.html` is the source for the home page; `ring.txt` is the hand-drawn zero path.
- Run `python3 build.py` after editing `src/` to regenerate `public/index.html`.
