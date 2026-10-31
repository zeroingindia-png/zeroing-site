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
        "sustainability": "",
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
        "sustainability": "",
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
        "sustainability": "",
        "founder": "",
        "site": "https://ampor.in",
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
        "sustainability": "",
        "founder": "",
        "site": "",
        "instagram": "syzygyliving",
    },
]

TODO = '<span class="todo">To confirm</span>'

# Paste the public links here when you have them; the buttons appear on their own.
EPISODES = [
    {"slug": "akanksha-sood-singh", "parts": [
        {"label": "Part one", "ep": "Episode 01", "title": "First to film Indian lions in the dark", "youtube": "", "spotify": ""},
        {"label": "Part two", "ep": "Episode 02", "title": "The conversation continues", "youtube": "", "spotify": ""},
    ]},
]


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
<link rel="icon" href="%%ROOT%%favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anek+Devanagari:wdth,wght@75..125,300..800&family=Anek+Latin:wdth,wght@75..125,300..800&family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800&display=swap">
<style>
{css}</style>"""


LOGO = read("logo_path.txt").strip()
_mark_n = [0]


def hero_mark():
    """The Zeroing mark, cropped huge behind a hero. Its two halves lock together on load."""
    _mark_n[0] += 1
    i = _mark_n[0]
    return (f'<svg class="hero-mark" viewBox="0 0 1373 1002" aria-hidden="true">'
            f'<defs><clipPath id="mt{i}"><rect width="1373" height="506"/></clipPath>'
            f'<clipPath id="mb{i}"><rect y="506" width="1373" height="496"/></clipPath></defs>'
            f'<g class="top" clip-path="url(#mt{i})"><path fill-rule="evenodd" d="LOGO"/></g>'
            f'<g class="bot" clip-path="url(#mb{i})"><path fill-rule="evenodd" d="LOGO"/></g></svg>')


def fill(text, P, H, current=""):
    cur = lambda name: ' aria-current="page"' if current == name else ""
    while "{HERO_MARK}" in text:
        text = text.replace("{HERO_MARK}", hero_mark(), 1)
    return (text.replace("{P}", P).replace("{H}", H)
                .replace("{CUR_COMMUNITY}", cur("community"))
                .replace("{CUR_IS}", cur("podcast"))
                .replace("{CUR_JOIN}", cur("join"))
                .replace("RING", RING).replace("LOGO", LOGO))


def page(title, desc, main, P, H, current=""):
    head = HEAD.format(title=html.escape(title), desc=html.escape(desc), css=CSS).replace("%%ROOT%%", P)
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
            f'        <ul class="badges small"><li>Made in India</li><li>Homegrown</li></ul>\n'
            f'        <span class="open">Open the brand page</span>\n'
            f'      </a>')


def brand_main(b):
    ink = "kajal" if b["colour"] in ("haldi", "genda") else "chuna"
    idea = "\n".join(f"        <p>{html.escape(p)}</p>" for p in b["idea"])
    sus = (f"<p>{html.escape(b['sustainability'])}</p>" if b.get("sustainability")
           else '<p><span class="todo">To confirm with the founder: what the brand already does on materials, packaging or making, and the next step it is working on.</span></p>')
    shop_url = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
    shop_btn = (f'<a class="pill solid" href="{shop_url}" target="_blank" rel="noopener">Visit {html.escape(b["name"])}</a>'
                if shop_url else '<span class="pill line" aria-disabled="true">Shop link coming soon</span>')
    others = [o for o in BRANDS if o["slug"] != b["slug"]]
    nxt = "\n".join(
        f'      <li><a href="{o["slug"]}.html"><span class="name">{html.escape(o["name"])}</span><span>{html.escape(o["makes"])}</span></a></li>'
        for o in others)
    return f"""  <section class="field f-{b['colour']} hero brand-hero" id="top" data-ink="{ink}" data-field="{b['colour']}">
    {{HERO_MARK}}
    <div class="hero-body">
      <h1 class="display">{html.escape(b['name'])}</h1>
      <p class="lede">{html.escape(b['line'])}</p>
      <div class="actions">{shop_btn}</div>
    </div>
    <svg class="seal" viewBox="0 0 200 200" aria-hidden="true"><path d="RING"/><text x="100" y="94" text-anchor="middle">MADE IN</text><text x="100" y="122" text-anchor="middle">INDIA</text></svg>
    <div class="corners narrow"><span>Homegrown and made in India</span><span>{html.escape(b['role'])}</span></div>
  </section>

  <section class="field f-chuna" id="about" data-ink="kajal" data-field="chuna">
    <div class="about">
      <div class="idea">
        <h2 class="display">The idea</h2>
{idea}
        <h3 class="sub">Working towards sustainability</h3>
        {sus}
      </div>
      <dl class="facts-list">
        <div><dt>Makes</dt><dd>{html.escape(b['makes'])}</dd></div>
        <div><dt>Made in</dt><dd>India{(', ' + html.escape(b['city'])) if b['city'] else ''}</dd></div>
        <div><dt>Homegrown</dt><dd>Yes, Indian founded and run</dd></div>
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
    # Independent Society, the episode, and the information pages
    simple = [
        ("independent-society.html", "Independent Society", "Long, honest conversations about what working life in India actually looked like.", "independent-society.html", "podcast"),
        ("join.html", "Join Zeroing", "Apply to join Zeroing, a community of homegrown Indian brands.", "join.html", "join"),
        ("contact.html", "Contact Zeroing", "Write to Zeroing.", "contact.html", ""),
        ("the-other-details.html", "The Other Details", "The research lab of Zeroing: the money, the paperwork, the years nobody saw.", "the-other-details.html", ""),
        ("legal.html", "Zeroing Legal", "Disclaimer, privacy notice, terms of use and grievances for Zeroing.", "legal.html", ""),
    ]
    for out, title, desc, src, current in simple:
        head, body = page(title, desc, read("pages", src), P="", H="index.html", current=current)
        write(out, full_doc(head, body))

    ep = EPISODES[0]

    def buttons(part, first_solid=True):
        out = []
        if part["youtube"]:
            out.append(f'<a class="pill {"solid" if first_solid else "line"}" href="{part["youtube"]}" target="_blank" rel="noopener">Watch on YouTube</a>')
        if part["spotify"]:
            out.append(f'<a class="pill line" href="{part["spotify"]}" target="_blank" rel="noopener">Listen on Spotify</a>')
        return out or ['<span class="pill line" aria-disabled="true">Links coming soon</span>']

    watch = ['<a class="pill solid" href="#parts">Choose a part</a>']
    parts = "\n".join(
        f'      <li class="part">\n'
        f'        <p class="narrow">{html.escape(p["ep"])}</p>\n'
        f'        <h3>{html.escape(p["label"])}</h3>\n'
        f'        <p class="part-title">{html.escape(p["title"])}</p>\n'
        f'        <div class="actions">{"".join(buttons(p))}</div>\n'
        f'      </li>' for p in ep["parts"])
    main = (read("pages", "episode-akanksha.html").replace("{WATCH}", "\n          ".join(watch))
            .replace("{PARTS}", parts))
    head, body = page("Akanksha Sood Singh on Independent Society",
                      "Wildlife filmmaker Akanksha Sood Singh in a two part conversation with Independent Society, episodes 1 and 2.",
                      main, P="../", H="../index.html", current="podcast")
    write("episodes/akanksha-sood-singh.html", full_doc(head, body))
    print("built", 8 + len(BRANDS), "pages")
    from research import build_research
    build_research()


if __name__ == "__main__":
    build()
