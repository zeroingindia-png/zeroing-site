"""Build the Zeroing site.

    python3 build.py

Writes every page into public/ (what Cloudflare Pages serves) and preview.html
(the home page without its <head>, for Claude previews).
Edit the brand details in BRANDS and the episode links in EPISODES below; write "" for anything not confirmed yet.
Photographs live in public/media/. Keep them under about 500 KB each.
"""
import html, json, math, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "public")
E = html.escape

CONTENT = os.path.join(ROOT, "content")


def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as f:
        return json.load(f)


def mf(v):
    """'/media/x.jpg' (as the editor saves it) -> 'x.jpg'."""
    v = (v or "").strip()
    return v.split("media/")[-1] if v else ""


def T(t):
    """Escape text and turn *words* into <em>words</em> (set in the serif italic)."""
    return re.sub(r"\*([^*]+)\*", r"<em>\1</em>", E(t or ""))


def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


# ---- everything below comes from content/*.json; edit those files (or use Pages CMS), not this script ----
HOME = load("home.json")
PODCAST = load("podcast.json")
SPOTIFY_SHOW = PODCAST.get("spotify_show", "")
YOUTUBE_CHANNEL = PODCAST.get("youtube_channel", "")

TODO = '<span class="todo">To confirm</span>'
COLOURS = ["peepal", "haldi", "genda", "kattha", "neel", "sindoor"]

BRANDS = []
for n, x in enumerate(load("brands.json")):
    d = {"slug": x.get("slug") or slugify(x["name"]), "name": x["name"], "colour": x.get("colour") or COLOURS[n % len(COLOURS)],
         "line": x.get("line", ""), "makes": x.get("makes", ""),
         "idea": [q.strip() for q in (x.get("about") or "").split("\n\n") if q.strip()],
         "role": x.get("role") or "Community brand", "city": x.get("city", ""), "founder": x.get("founder", ""),
         "sustainability": x.get("sustainability", ""), "site": (x.get("website") or "").strip(),
         "instagram": (x.get("instagram") or "").strip().lstrip("@")}
    if x.get("hero_image"):
        d["wordmark" if x.get("hero_is_logo") else "hero"] = (mf(x["hero_image"]), x["name"] + (" logo" if x.get("hero_is_logo") else ""))
    if x.get("card_image"):
        d["thumb"] = mf(x["card_image"])
    if x.get("tape_image"):
        d["tape"] = mf(x["tape_image"])
    if x.get("craft"):
        d["craft"] = [(mf(c["image"]), c.get("title", ""), c.get("note", "")) for c in x["craft"] if c.get("image")]
        d["craft_title"] = x.get("craft_title") or "How it is made"
        d["craft_line"] = x.get("craft_text", "")
    BRANDS.append(d)

EPISODES = [{"slug": "akanksha-sood-singh", "parts": PODCAST["parts"]}]
HIGHLIGHTS = [(h["time"], h["title"]) for h in PODCAST.get("highlights", [])]
FIELD_PHOTOS = [(mf(f["image"]), f.get("caption", ""), {"wide": "w", "tall": "t"}.get(f.get("shape"), "h"))
                for f in PODCAST.get("field_photos", []) if f.get("image")]


def read(*parts):
    with open(os.path.join(SRC, *parts), encoding="utf-8") as f:
        return f.read()


RING = open(os.path.join(ROOT, "ring.txt"), encoding="utf-8").read().strip()
CSS = read("base.css")
JS = read("script.js")
HEADER = read("partials", "header.html")
CLOSING = read("partials", "closing.html")
LOGO = read("logo_path.txt").strip()

HEAD = """<title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#C1272D">
<link rel="icon" href="%%ROOT%%favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anek+Devanagari:wdth,wght@75..125,300..800&family=Anek+Latin:wdth,wght@75..125,300..800&family=Bricolage+Grotesque:opsz,wdth,wght@12..96,75..100,200..800&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@500&display=swap">
<script>document.documentElement.classList.add('js')</script>
<style>
{css}</style>"""

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


def img(src, alt, P, eager=False, drift=None):
    d = f' data-drift="{drift}"' if drift else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{P}media/{src}" alt="{E(alt)}" {load} decoding="async"{d}>'


def fill(text, P, H, current=""):
    cur = lambda name: ' aria-current="page"' if current == name else ""
    while "{HERO_MARK}" in text:
        text = text.replace("{HERO_MARK}", hero_mark(), 1)
    return (text.replace("{P}", P).replace("{H}", H)
                .replace("{SPOTIFY_SHOW}", SPOTIFY_SHOW)
                .replace("{CUR_COMMUNITY}", cur("community"))
                .replace("{CUR_IS}", cur("podcast"))
                .replace("{CUR_JOIN}", cur("join"))
                .replace("RING", RING).replace("LOGO", LOGO))


def page(title, desc, main, P, H, current=""):
    head = HEAD.format(title=E(title), desc=E(desc), css=CSS).replace("%%ROOT%%", P)
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


def brand_links(b, cls="site-chip"):
    out = []
    if b["site"]:
        out.append(f'<a class="{cls} go" href="{b["site"]}" target="_blank" rel="noopener">{b["site"].replace("https://", "")} <span aria-hidden="true">&#8599;</span></a>')
    if b["instagram"]:
        out.append(f'<a class="{cls}" href="https://www.instagram.com/{b["instagram"]}/" target="_blank" rel="noopener">@{b["instagram"]}</a>')
    return "".join(out)


def card_img(b, P):
    if b.get("hero"):
        return f'<span class="card-img">{img(b.get("thumb") or b["hero"][0], b["hero"][1], P)}</span>'
    if b.get("wordmark"):
        return f'<span class="card-img word">{img(b["wordmark"][0], b["wordmark"][1], P)}</span>'
    if b.get("tape"):
        return f'<span class="card-img word" style="background:var(--haldi)">{img(b["tape"], b["name"] + " packing tape", P)}</span>'
    return f'<span class="card-img colour" aria-hidden="true"><span>{E(b["name"][0])}</span></span>'


def brand_card(b, P):
    links = brand_links(b)
    return (f'      <article class="brand-card bc-{b["colour"]}">\n'
            f'        {card_img(b, P)}\n'
            f'        <div class="card-body">\n'
            f'          <span class="tag">{E(b["role"])}</span>\n'
            f'          <a class="bname" href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a>\n'
            f'          <span class="bline">{E(b["makes"])}</span>\n'
            f'          <ul class="badges small"><li>Made in India</li><li>Homegrown</li></ul>\n'
            f'          <div class="card-links">{links}</div>\n'
            f'        </div>\n'
            f'      </article>')


def home_brand_row(b, P):
    if b.get("hero"):
        thumb = f'<span class="thumb">{img(b.get("thumb") or b["hero"][0], "", P)}</span>'
    elif b.get("wordmark"):
        thumb = f'<span class="thumb word">{img(b["wordmark"][0], "", P)}</span>'
    elif b.get("tape"):
        thumb = f'<span class="thumb word" style="background:var(--haldi)">{img(b["tape"], "", P)}</span>'
    else:
        thumb = '<span class="thumb blank"></span>'
    out = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
    label = b["site"].replace("https://", "") if b["site"] else (f'@{b["instagram"]}' if b["instagram"] else "")
    what = (f'<a class="site-chip" href="{out}" target="_blank" rel="noopener">{label} <span aria-hidden="true">&#8599;</span></a>'
            if out else '<span class="what">Site coming soon</span>')
    return (f'      <li>{thumb}<a class="name" href="{P}brands/{b["slug"]}.html">{E(b["name"])}<small>{E(b["makes"])}</small></a>{what}</li>')


def craft_reel(items, title, line, P, label=""):
    figs = []
    for it in items:
        src, t, note = it[0], it[1], it[2]
        wide = len(it) > 3 and it[3] == "wide"
        figs.append(f'        <figure class="craft-item{" wide" if wide else ""}"><div class="photo">{img(src, t + ". " + note, P)}</div>'
                    f'<figcaption><b>{E(t)}</b><span>{E(note)}</span></figcaption></figure>')
    return f"""  <section class="craft" id="craft" data-ink="kajal" data-field="chuna">
    <div class="craft-pin">
      <div class="craft-head">
        <h2 class="display">{E(title)}</h2>
        <p>{line}</p>
      </div>
      <div class="craft-track">
{chr(10).join(figs)}
      </div>
      <div class="craft-progress" aria-hidden="true"><i></i></div>
    </div>
  </section>
"""


def brand_main(b, P="../"):
    ink = "kajal" if b["colour"] in ("haldi", "genda") else "chuna"
    idea = "\n".join(f"        <p>{E(p)}</p>" for p in b["idea"])
    sus = (f"<p>{E(b['sustainability'])}</p>" if b.get("sustainability")
           else '<p><span class="todo">To confirm with the founder: what the brand already does on materials, packaging or making, and the next step it is working on.</span></p>')
    shop_url = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
    shop_btn = (f'<a class="pill solid" href="{shop_url}" target="_blank" rel="noopener">Visit {E(b["name"])} <span class="arr" aria-hidden="true">&#8599;</span></a>'
                if shop_url else '<span class="pill line" aria-disabled="true">Shop link coming soon</span>')
    ig_btn = (f'<a class="pill line" href="https://www.instagram.com/{b["instagram"]}/" target="_blank" rel="noopener">@{b["instagram"]}</a>'
              if b["site"] and b["instagram"] else "")
    if b.get("hero"):
        photo = f'<div class="hero-photo">{img(b["hero"][0], b["hero"][1], P, eager=True, drift="0.08")}</div>'
        cls = ""
    elif b.get("wordmark"):
        photo = f'<div class="hero-photo word">{img(b["wordmark"][0], b["wordmark"][1], P, eager=True)}</div>'
        cls = ""
    else:
        photo, cls = "", " no-photo"
    tape = ""
    if b.get("tape"):
        one = img(b["tape"], "", P)
        tape = f'  <div class="tape" aria-label="{E(b["name"])} packing tape"><div class="tape-run">{one * 12}</div></div>\n'
    craft = craft_reel(b["craft"], b["craft_title"], E(b["craft_line"]), P) if b.get("craft") else ""
    others = [o for o in BRANDS if o["slug"] != b["slug"]]
    nxt = "\n".join(
        f'      <li><a href="{o["slug"]}.html"><span class="name">{E(o["name"])}</span><span>{E(o["makes"])}</span></a></li>'
        for o in others)
    return f"""  <section class="field f-{b['colour']} hero brand-hero{cls}" id="top" data-ink="{ink}" data-field="{b['colour']}">
    <div class="hero-text">
      {{HERO_MARK}}
      <div class="hero-body">
        <p class="corners narrow" style="margin:0;padding:0">{E(b['role'])}</p>
        <h1 class="display">{E(b['name'])}</h1>
        <p class="lede">{E(b['line'])}</p>
        <div class="actions">{shop_btn}{ig_btn}</div>
        <svg class="seal" viewBox="0 0 200 200" aria-hidden="true"><path d="RING"/><text x="100" y="94" text-anchor="middle">MADE IN</text><text x="100" y="122" text-anchor="middle">INDIA</text></svg>
      </div>
    </div>
    {photo}
  </section>
{tape}
  <section class="field f-chuna auto" id="about" data-ink="kajal" data-field="chuna">
    <div class="about">
      <div class="idea">
        <h2 class="display">The idea</h2>
{idea}
        <h3 class="sub">Working towards sustainability</h3>
        {sus}
      </div>
      <dl class="facts-list">
        <div><dt>Makes</dt><dd>{E(b['makes'])}</dd></div>
        <div><dt>Made in</dt><dd>India{(', ' + E(b['city'])) if b['city'] else ''}</dd></div>
        <div><dt>Homegrown</dt><dd>Yes, Indian founded and run</dd></div>
        <div><dt>Founder</dt><dd>{E(b['founder']) or TODO}</dd></div>
        <div><dt>In Zeroing</dt><dd>{E(b['role'])}</dd></div>
        <div><dt>Website</dt><dd>{site_link(b['site'])}</dd></div>
        <div><dt>Instagram</dt><dd>{ig(b['instagram'])}</dd></div>
      </dl>
    </div>
  </section>
{craft}
  <section class="field f-neel auto" id="more" data-ink="chuna" data-field="neel">
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


def to_seconds(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def highlights_html(spotify):
    rows = "\n".join(
        f'      <li><a href="{spotify}?t={to_seconds(t)}" target="_blank" rel="noopener"><span class="t">{t}</span>'
        f'<span class="hl-title">{E(title)}</span><span class="hl-play" aria-hidden="true">Play on Spotify &#8599;</span></a></li>'
        for t, title in HIGHLIGHTS)
    return f'    <ol class="highlights">\n{rows}\n    </ol>'


def listen_buttons(part, solid=True):
    out = []
    if part["spotify"]:
        out.append(f'<a class="pill spotify" href="{part["spotify"]}" target="_blank" rel="noopener">Listen on Spotify <span class="arr" aria-hidden="true">&#8599;</span></a>')
    if part["youtube"]:
        out.append(f'<a class="pill {"solid" if solid else "line"}" href="{part["youtube"]}" target="_blank" rel="noopener">Watch on YouTube <span class="arr" aria-hidden="true">&#8599;</span></a>')
    return "".join(out) or '<span class="pill line" aria-disabled="true">Links coming soon</span>'


def spotify_embed(url, title):
    if not url:
        return ""
    eid = url.rstrip("/").split("/")[-1]
    return (f'<iframe class="player" title="{E(title)} on Spotify" src="https://open.spotify.com/embed/episode/{eid}?theme=0" '
            f'loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>')


def orbit_html(P):
    """Community hero: the brands' own photographs circling the headline, like stalls around a lane."""
    items = []
    for b in BRANDS:
        if b.get("hero") and not b.get("wordmark"):
            items.append(("photo", b.get("thumb") or b["hero"][0], b["name"]))
        elif b.get("wordmark"):
            items.append(("word", b["wordmark"][0], b["name"]))
        elif b.get("tape"):
            items.append(("tape", b["tape"], b["name"]))
        else:
            items.append(("colour", b["colour"], b["name"]))
    for c in HOME_CRAFT:
        items.append(("photo", c[0], ""))
    items = items[:10]
    n = len(items)
    out = []
    for i, (kind, val, label) in enumerate(items):
        # two arcs, left and right of the headline, so the words stay clear
        half = (n + 1) // 2
        k, m = (i // 2, half) if True else (0, 1)
        t = (k + 0.5) / m
        a = (-68 + 136 * t) if i % 2 == 0 else (248 - 136 * t)
        x = 50 + 43 * math.cos(math.radians(a))
        y = 50 + 44 * math.sin(math.radians(a))
        size = [148, 118, 132, 104][i % 4]
        rot = [-6, 4, -3, 7, -5, 3][i % 6]
        style = f'--x:{x:.1f}%;--y:{y:.1f}%;--s:{size}px;--r:{rot}deg;--i:{i};--f:{7 + i % 4}s'
        cls = "o-card" + (" o-hide-s" if i % 2 else "")
        if kind == "colour":
            body = f'<span class="o-colour" style="background:var(--{val})"><span>{E(label)}</span></span>'
        elif kind == "tape":
            body = f'<span class="o-tape">{img(val, "", P)}</span>'
        elif kind == "word":
            body = f'<span class="o-word">{img(val, "", P)}</span>'
        else:
            body = img(val, "", P)
        tag = f'<span class="o-label">{E(label)}</span>' if label and kind != "colour" else ""
        out.append(f'<span class="{cls}" style="{style}">{body}{tag}</span>')
    return "\n      ".join(out)


def record_card():
    parts = EPISODES[0]["parts"]
    rows = [("Episodes on record", len(parts)), ("Moments in the highlights", len(HIGHLIGHTS)), ("Brands that presented it", 2)]
    li = "".join(f'<li><span>{E(k)}</span><b>{v}</b></li>' for k, v in rows)
    return (f'<aside class="rec-card" aria-label="This conversation in numbers"><div class="rec-top"><span>Akanksha Sood Singh</span>'
            f'<span class="rec-badge">Part two is out</span></div>'
            f'<p class="rec-title">Part one <span aria-hidden="true">&#8594;</span> <em>Part two</em></p><ul>{li}</ul></aside>')



def web_svg():
    """A line drawing of the community: every brand tied to the centre, and to each other. It draws itself on arrival."""
    cx, cy = 500, 215
    nodes = [("INDSO", 150, 78), ("Ampor Eyewear", 110, 300), ("Vedi Kade", 330, 385), ("Syzygy Living", 650, 385),
             ("Independent Society", 880, 92), ("The Other Details", 900, 318), ("New brand", 380, 42), ("New brand", 620, 40), ("New brand", 250, 200)]
    cross = [(0, 4), (1, 4), (4, 5), (2, 3), (0, 6), (7, 4), (8, 1), (3, 5)]
    paths, dots, i = [], [], 0

    def curve(a, b):
        (x1, y1), (x2, y2) = a, b
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        qx, qy = mx + (cx - mx) * 0.35, my + (cy - my) * 0.35
        return f"M{x1} {y1} Q{qx:.0f} {qy:.0f} {x2} {y2}"

    for n, (label, x, y) in enumerate(nodes):
        d = f"M{cx} {cy} L{x} {y}"
        paths.append(f'<path class="ln" pathLength="1" d="{d}" style="--d:{n * 120}ms"/>')
    for k, (a, b) in enumerate(cross):
        d = curve(nodes[a][1:], nodes[b][1:])
        paths.append(f'<path class="ln soft" pathLength="1" d="{d}" style="--d:{900 + k * 140}ms"/>')
        dots.append(f'<circle class="pulse" r="3.5"><animateMotion dur="{7 + k % 4}s" begin="{k * 0.9:.1f}s" repeatCount="indefinite" path="{d}"/></circle>')
    labels = []
    for n, (label, x, y) in enumerate(nodes):
        new = label == "New brand"
        anchor = "end" if x < cx - 40 else ("start" if x > cx + 40 else "middle")
        dx = -16 if anchor == "end" else (16 if anchor == "start" else 0)
        dy = 5 if anchor != "middle" else (-16 if y < cy else 28)
        labels.append(f'<g class="node{" new" if new else ""}" style="--d:{600 + n * 120}ms"><circle cx="{x}" cy="{y}" r="{6 if new else 8}"/>'
                      f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}">{E(label)}</text></g>')
    hub = (f'<g class="node hub" style="--d:300ms"><circle cx="{cx}" cy="{cy}" r="34"/>'
           f'<text x="{cx}" y="{cy + 6}" text-anchor="middle">Zeroing</text></g>')
    return ('<figure class="web" aria-label="Zeroing connects each brand, the podcast and the research lab, and the brands to each other">'
            '<svg viewBox="-190 0 1380 430" role="img" aria-hidden="true">'
            + "".join(paths) + "".join(dots) + "".join(labels) + hub + '</svg></figure>')


HOME_CRAFT = [(mf(c["image"]), c.get("title", ""), c.get("note", "")) + (("wide",) if c.get("wide") else ()) for c in HOME.get("craft", []) if c.get("image")]


def build():
    ep = EPISODES[0]
    p1, p2 = ep["parts"][0], ep["parts"][-1]

    # home
    H_ = HOME
    band_links = [("peepal", "{P}community.html", "Meet the brands"), ("neel", "{P}independent-society.html", "Listen"),
                  ("kattha", "{P}the-other-details/", "Read the studies")]
    bands = "\n".join(
        f'    <a class="band {c}" href="{h}">'
        + (f'<span class="band-img">{img(mf(bd.get("image")), "", "")}</span>' if bd.get("image") else "")
        + f'<h2 class="display">{E(bd.get("title", ""))}</h2><p>{E(bd.get("text", ""))}</p><span class="go">{go}</span></a>'
        for (c, h, go), bd in zip(band_links, H_.get("bands", [])))
    ledger = "\n".join(f'      <p><span class="n">{int(l.get("number") or 0)}</span>{E(l.get("text", ""))}</p>' for l in H_.get("ledger", []))
    home = (read("pages", "home.html")
            .replace("{HERO_TITLE}", T(H_.get("hero_title", ""))).replace("{HERO_TEXT}", E(H_.get("hero_text", "")))
            .replace("{BANDS}", bands)
            .replace("{CRAFT}", craft_reel(HOME_CRAFT, H_.get("craft_title", ""), T(H_.get("craft_text", "")), ""))
            .replace("{RECORD_LABEL}", E(H_.get("record_label", ""))).replace("{RECORD_NAME}", E(H_.get("record_name", "")))
            .replace("{RECORD_ROLE}", E(H_.get("record_role", ""))).replace("{RECORD_QUOTE}", E(H_.get("record_quote", "")))
            .replace("{RECORD_IMAGE}", mf(H_.get("record_image")))
            .replace("{LEDGER_SINCE}", E(H_.get("ledger_since", ""))).replace("{LEDGER}", ledger)
            .replace("{BRANDS_TITLE}", T(H_.get("brands_title", ""))).replace("{BRANDS_TEXT}", E(H_.get("brands_text", "")))
            .replace("{HOME_BRANDS}", "\n".join(home_brand_row(b, "") for b in BRANDS))
            .replace("{LISTEN_LATEST}", listen_buttons(p2))
            .replace("{WEB}", web_svg()))
    head, body = page("Zeroing",
                      "Zeroing is a community of Indian brands and the people behind them, and home of the Independent Society podcast.",
                      home, P="", H="")
    write("index.html", full_doc(head, body))
    with open(os.path.join(ROOT, "preview.html"), "w", encoding="utf-8") as f:
        f.write(head + "\n\n" + body)

    # community
    cards = "\n".join(brand_card(b, "") for b in BRANDS)
    main = read("pages", "community.html").replace("{ORBIT}", orbit_html("")).replace("{BRAND_CARDS}", cards).replace("{BRAND_COUNT}", str(len(BRANDS) + 3))
    head, body = page("Zeroing Community",
                      "The Indian brands in Zeroing, and what we learned from small business efforts around the world.",
                      main, P="", H="index.html", current="community")
    write("community.html", full_doc(head, body))

    # brands
    for b in BRANDS:
        head, body = page(f"{b['name']} in Zeroing", f"{b['name']}: {b['makes']}. Part of the Zeroing community.",
                          brand_main(b), P="../", H="../index.html", current="community")
        write(f"brands/{b['slug']}.html", full_doc(head, body))

    # Independent Society
    is_main = (read("pages", "independent-society.html")
               .replace("{EP1_LINKS}", listen_buttons(p1)).replace("{EP2_LINKS}", listen_buttons(p2))
               .replace("{EP1_TITLE}", E(p1["title"])).replace("{EP2_TITLE}", E(p2["title"]))
               .replace("{HIGHLIGHTS}", highlights_html(p2["spotify"]))
               .replace("{RECORD_CARD}", record_card())
               .replace("{YOUTUBE_CHANNEL_BTN}", f'<a class="pill line" href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener">Watch on YouTube <span class="arr" aria-hidden="true">&#8599;</span></a>' if YOUTUBE_CHANNEL else ""))
    simple = [
        ("independent-society.html", "Independent Society", "Long, honest conversations about what working life in India actually looked like.", is_main, "podcast"),
        ("join.html", "Join Zeroing", "Apply to join Zeroing, a community of homegrown Indian brands.", read("pages", "join.html"), "join"),
        ("contact.html", "Contact Zeroing", "Write to Zeroing.", read("pages", "contact.html"), ""),
        ("legal.html", "Zeroing Legal", "Disclaimer, privacy notice, terms of use and grievances for Zeroing.", read("pages", "legal.html"), ""),
    ]
    for out, title, desc, main, current in simple:
        head, body = page(title, desc, main, P="", H="index.html", current=current)
        write(out, full_doc(head, body))

    # the episode
    parts = "\n".join(
        f'      <li class="part">\n'
        f'        <p class="narrow">{E(p["ep"])} · {E(p["label"])}</p>\n'
        f'        <h3>{E(p["title"])}</h3>\n'
        f'        <p class="when">Released {E(p["date"])}</p>\n'
        f'        {spotify_embed(p["spotify"], p["title"])}\n'
        f'        <div class="actions">{listen_buttons(p)}</div>\n'
        f'      </li>' for p in ep["parts"])
    gallery = "\n".join(
        f'      <figure class="photo {c}">{img(src, cap or "Akanksha Sood Singh in the field", "../")}'
        + (f'<figcaption>{E(cap)}</figcaption>' if cap else "") + '</figure>'
        for src, cap, c in FIELD_PHOTOS)
    main = (read("pages", "episode-akanksha.html")
            .replace("{WATCH}", listen_buttons(p2) + '<a class="pill line" href="#parts">Both parts</a>')
            .replace("{PARTS}", parts)
            .replace("{HIGHLIGHTS}", highlights_html(p2["spotify"]))
            .replace("{GALLERY}", gallery)
            .replace("{PHOTO_CREDIT}", E(PODCAST.get("photo_credit", ""))))
    head, body = page("Akanksha Sood Singh on Independent Society",
                      "Wildlife filmmaker Akanksha Sood Singh in a two part conversation with Independent Society, episodes 1 and 2.",
                      main, P="../", H="../index.html", current="podcast")
    write("episodes/akanksha-sood-singh.html", full_doc(head, body))
    print("built", 8 + len(BRANDS), "pages")
    from research import build_research
    build_research()


if __name__ == "__main__":
    build()
