"""Build the Zeroing site.

    python3 build.py

Writes every page into public/ (what Cloudflare Pages serves) and preview.html
(the home page without its <head>, for Claude previews).
Edit the brand details in BRANDS below; write "" for anything not confirmed yet.
"""
import html, os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "public")

BRANDS = [
    {
        "slug": "vedi-kade",
        "name": "Vedi Kade",
        "colour": "genda",
        "line": "Modern clothing that carries Tamil history.",
        "makes": "Tamil cultural clothing for today",
        "idea": [
            "Vedi Kade designs modern outfits that draw on Tamil history and culture.",
            "Stories, symbols and ways of making from Tamil life are worked into clothes you can wear on an ordinary day, so heritage becomes part of what you wear now.",
        ],
        "role": "Community brand",
        "city": "",
        "founder": "",
        "site": "",
        "instagram": "",
    },
    {
        "slug": "indso",
        "name": "INDSO",
        "colour": "peepal",
        "line": "Botanical gels for Indian skin.",
        "makes": "Botanical skincare gels",
        "idea": [
            "INDSO makes light botanical gels for Indian skin, Indian heat and city air.",
            "The range is built on ingredients Indian homes have trusted for generations, such as turmeric, saffron, honey and ashwagandha, with every ingredient listed openly.",
        ],
        "role": "Presented Independent Society",
        "city": "",
        "founder": "",
        "site": "https://indso.in",
        "instagram": "indso.in",
    },
    {
        "slug": "ampor-eyewear",
        "name": "Ampor Eyewear",
        "colour": "haldi",
        "line": "Indian eyewear.",
        "makes": "Eyewear",
        "idea": ["Ampor Eyewear makes eyewear and was one of the two brands that presented the first conversation of Independent Society."],
        "role": "Presented Independent Society",
        "city": "",
        "founder": "",
        "site": "",
        "instagram": "amporeyewear",
    },
    {
        "slug": "syzygy-living",
        "name": "Syzygy Living",
        "colour": "kattha",
        "line": "Design homeware.",
        "makes": "Design homeware",
        "idea": ["Syzygy Living makes design homeware. Its name comes from the word for three heavenly bodies falling into line."],
        "role": "Community brand",
        "city": "",
        "founder": "",
        "site": "",
        "instagram": "syzygyliving",
    },
]

TODO = '<span class="todo">To confirm</span>'


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding="utf-8") as f:
        return f.read()


RING = open(os.path.join(ROOT, "ring.txt"), encoding="utf-8").read().strip()
CSS = read("base.css")
JS = read("script.js")
HEADER = read("partials", "header.html")
CLOSING = read("partials", "closing.html")

HEAD = """<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anek+Devanagari:wdth,wght@75..125,300..800&family=Anek+Latin:wdth,wght@75..125,300..800&display=swap">
<style>
{css}</style>"""


def fill(text, P, H, current=""):
    return (text.replace("{P}", P).replace("{H}", H)
                .replace("{CUR_COMMUNITY}", ' aria-current="page"' if current == "community" else "")
                .replace("RING", RING))


def page(title, desc, main, P, H, current=""):
    head = HEAD.format(title=html.escape(title), desc=html.escape(desc), css=CSS)
    body = (HEADER + "\n<main>\n" + main + "\n" + CLOSING + "</main>\n\n<script>\n" + JS + "</script>\n")
    return head, fill(body, P, H, current)


def full_doc(head, body):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "\n</head>\n<body>\n" + body + "</body>\n</html>\n")


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def ig(handle):
    return f'<a href="https://www.instagram.com/{handle}/" target="_blank" rel="noopener">@{handle}</a>' if handle else TODO


def site_link(url):
    return f'<a href="{url}" target="_blank" rel="noopener">{url.replace("https://", "")}</a>' if url else TODO


def brand_card(b, P):
    return (f'      <a class="brand-card bc-{b["colour"]}" href="{P}brands/{b["slug"]}.html">\n'
            f'        <span class="tag">{html.escape(b["role"])}</span>\n'
            f'        <span class="bname">{html.escape(b["name"])}</span>\n'
            f'        <span class="bline">{html.escape(b["makes"])}</span>\n'
            f'        <span class="open">Open the brand page</span>\n'
            f'      </a>')


def brand_main(b):
    ink = "kajal" if b["colour"] in ("haldi", "genda") else "chuna"
    idea = "\n".join(f"        <p>{html.escape(p)}</p>" for p in b["idea"])
    shop_url = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
    shop_btn = (f'<a class="pill solid" href="{shop_url}" target="_blank" rel="noopener">Visit {html.escape(b["name"])}</a>'
                if shop_url else '<span class="pill line" aria-disabled="true">Shop link coming soon</span>')
    others = [o for o in BRANDS if o["slug"] != b["slug"]]
    nxt = "\n".join(
        f'      <li><a href="{o["slug"]}.html"><span class="name">{html.escape(o["name"])}</span><span>{html.escape(o["makes"])}</span></a></li>'
        for o in others)
    return f"""  <section class="field f-{b['colour']} hero brand-hero" id="top" data-ink="{ink}" data-field="{b['colour']}">
    <svg class="hero-ring" viewBox="0 0 200 200" aria-hidden="true"><path class="draw" pathLength="1" d="RING"/></svg>
    <div class="hero-body">
      <h1 class="display">{html.escape(b['name'])}</h1>
      <p class="lede">{html.escape(b['line'])}</p>
      <div class="actions">{shop_btn}</div>
    </div>
    <div class="corners narrow"><span>Part of the Zeroing community</span><span>{html.escape(b['role'])}</span></div>
  </section>

  <section class="field f-chuna" id="about" data-ink="kajal" data-field="chuna">
    <div class="about">
      <div class="idea">
        <h2 class="display">The idea</h2>
{idea}
      </div>
      <dl class="facts-list">
        <div><dt>Makes</dt><dd>{html.escape(b['makes'])}</dd></div>
        <div><dt>Made in</dt><dd>{html.escape(b['city']) or TODO}</dd></div>
        <div><dt>Founder</dt><dd>{html.escape(b['founder']) or TODO}</dd></div>
        <div><dt>In Zeroing</dt><dd>{html.escape(b['role'])}</dd></div>
        <div><dt>Website</dt><dd>{site_link(b['site'])}</dd></div>
        <div><dt>Instagram</dt><dd>{ig(b['instagram'])}</dd></div>
      </dl>
    </div>
  </section>

  <section class="field f-neel" id="more" data-ink="chuna" data-field="neel">
    <div class="case-head">
      <h2 class="display">More from the community</h2>
      <p>Every brand here keeps its own shop. Zeroing introduces you; you buy from them directly.</p>
    </div>
    <ul class="next-brands">
{nxt}
      <li><a href="../community.html"><span class="name">The whole community</span><span>What we learned, and how we work together</span></a></li>
    </ul>
  </section>
"""


def build():
    # home
    head, body = page("Zeroing",
                      "Zeroing is a community of Indian brands and the people behind them, and home of the Independent Society podcast.",
                      read("pages", "home.html"), P="", H="")
    write("index.html", full_doc(head, body))
    with open(os.path.join(ROOT, "preview.html"), "w", encoding="utf-8") as f:
        f.write(head + "\n\n" + body)

    # community
    cards = "\n".join(brand_card(b, "") for b in BRANDS)
    main = read("pages", "community.html").replace("{BRAND_CARDS}", cards).replace("{BRAND_COUNT}", str(len(BRANDS) + 3))
    head, body = page("Zeroing Community",
                      "The Indian brands in Zeroing, and what we learned from small business efforts around the world.",
                      main, P="", H="index.html", current="community")
    write("community.html", full_doc(head, body))

    # brands
    for b in BRANDS:
        head, body = page(f"{b['name']} in Zeroing", f"{b['name']}: {b['makes']}. Part of the Zeroing community.",
                          brand_main(b), P="../", H="../index.html", current="community")
        write(f"brands/{b['slug']}.html", full_doc(head, body))
    print("built", 2 + len(BRANDS), "pages")


if __name__ == "__main__":
    build()
