"""Build the Zeroing site.

    python3 build.py

Writes every page into public/ (what Cloudflare Pages serves) and preview.html
(the home page without its <head>, for Claude previews).
Words, links and photographs live in content/*.json (edited in Pages CMS); write "" for anything not confirmed yet.
Photographs live in public/media/. Keep them under about 500 KB each.
"""
import html, json, os, re

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
         "sustainability": x.get("sustainability", ""), "nature": x.get("nature", ""), "culture": x.get("culture", ""), "site": (x.get("website") or "").strip(),
         "instagram": (x.get("instagram") or "").strip().lstrip("@")}
    if x.get("hero_image"):
        d["wordmark" if x.get("hero_is_logo") else "hero"] = (mf(x["hero_image"]), x["name"] + (" logo" if x.get("hero_is_logo") else ""))
    if x.get("card_image"):
        d["thumb"] = mf(x["card_image"])
    if x.get("tape_image"):
        d["tape"] = mf(x["tape_image"])
    if x.get("craft"):
        d["craft"] = [(mf(c["image"]), c.get("title", ""), c.get("note", ""), False) for c in x["craft"] if c.get("image")]
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

def img(src, alt, P, eager=False):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return f'<img src="{P}media/{src}" alt="{E(alt)}" {load} decoding="async">'


def fill(text, P, H, current=""):
    cur = lambda name: ' aria-current="page"' if current == name else ""
    return (text.replace("{P}", P).replace("{H}", H)
                .replace("{SPOTIFY_SHOW}", SPOTIFY_SHOW)
                .replace("{CUR_COMMUNITY}", cur("community"))
                .replace("{CUR_IS}", cur("podcast"))
                .replace("{CUR_JOIN}", cur("join"))
                .replace("LOGO", LOGO))


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


def craft_reel(items, title, line, P):
    figs = []
    for src, t, note, wide in items:
        figs.append(f'        <figure class="craft-item{" wide" if wide else ""}"><div class="photo">{img(src, t + ". " + note, P)}</div>'
                    f'<figcaption><b>{E(t)}</b><span>{E(note)}</span></figcaption></figure>')
    return f"""  <section class="craft" id="craft">
    <div class="craft-head">
      <h2 class="display">{E(title)}</h2>
      <p>{line}</p>
    </div>
    <div class="craft-track">
{chr(10).join(figs)}
    </div>
  </section>
"""


FOCUS = [("nature", "Nature"), ("culture", "Culture"), ("sustainability", "Sustainability")]
ASK = "To confirm with the founder"


def focus_block(b):
    cells = "".join(
        f'<div class="fc fc-{k}"><span class="fk">{t}</span>'
        + (f'<p>{E(b[k])}</p>' if b.get(k) else f'<p><span class="todo">{ASK}</span></p>') + '</div>' for k, t in FOCUS)
    return f'<div class="focus">{cells}</div>'


def focus_table(P):
    head = "".join(f'<th scope="col">{t}</th>' for _, t in FOCUS)
    rows = "".join(
        f'<tr><th scope="row"><a href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a></th>'
        + "".join(f'<td>{E(b[k])}</td>' if b.get(k) else f'<td class="todo-cell"><span>{ASK}</span></td>' for k, _ in FOCUS) + '</tr>'
        for b in BRANDS)
    return f'<div class="focus-wrap"><table class="focus-table"><thead><tr><th scope="col">Brand</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>'


def brand_main(b, P="../"):
    idea = "\n".join(f"        <p>{E(p)}</p>" for p in b["idea"])
    shop_url = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
    shop_btn = (f'<a class="pill solid" href="{shop_url}" target="_blank" rel="noopener">Visit {E(b["name"])} <span class="arr" aria-hidden="true">&#8599;</span></a>'
                if shop_url else '<span class="pill line" aria-disabled="true">No shop link yet</span>')
    ig_btn = (f'<a class="pill line" href="https://www.instagram.com/{b["instagram"]}/" target="_blank" rel="noopener">@{b["instagram"]}</a>'
              if b["site"] and b["instagram"] else "")
    if b.get("hero"):
        photo = f'<div class="hero-photo">{img(b["hero"][0], b["hero"][1], P, eager=True)}</div>'
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
    chapters = [("about", "The idea")] + ([("craft", b["craft_title"])] if b.get("craft") else []) + [("more", "More from the community")]
    LN = localnav(b["name"], chapters).replace('</span></nav>', (f'<a class="ln-buy" href="{shop_url}" target="_blank" rel="noopener">Visit</a>' if shop_url else '') + '</span></nav>')
    return f"""  <section class="field f-{b['colour']} hero brand-hero{cls}" id="top">
    <div class="hero-text">
      <div class="hero-body">
        <p class="corners narrow" style="margin:0;padding:0">{E(b['role'])}</p>
        <h1 class="display">{E(b['name'])}</h1>
        <p class="lede">{E(b['line'])}</p>
        <div class="actions">{shop_btn}{ig_btn}</div>
      </div>
    </div>
    {photo}
  </section>
{LN}{tape}
  <section class="field f-chuna auto" id="about">
    <div class="about">
      <div class="idea">
        <h2 class="display">The idea</h2>
{idea}
        <h3 class="sub">Where {E(b['name'])} stands</h3>
        {focus_block(b)}
      </div>
      <dl class="facts-list">
        <div><dt>Makes</dt><dd>{E(b['makes'])}</dd></div>
        <div><dt>Made in</dt><dd>India{(', ' + E(b['city'])) if b['city'] else ''}</dd></div>
        <div><dt>Homegrown</dt><dd>Founded and run in India, as the founder has told us</dd></div>
        <div><dt>Founder</dt><dd>{E(b['founder']) or TODO}</dd></div>
        <div><dt>In Zeroing</dt><dd>{E(b['role'])}</dd></div>
        <div><dt>Website</dt><dd>{site_link(b['site'])}</dd></div>
        <div><dt>Instagram</dt><dd>{ig(b['instagram'])}</dd></div>
      </dl>
    </div>
  </section>
{craft}
  <section class="field f-neel auto" id="more">
    <div class="case-head">
      <h2 class="display">More from the community</h2>
      <p>Every brand here keeps its own shop. We make the introduction. You buy from them.</p>
    </div>
    <ul class="next-brands">
{nxt}
      <li><a href="../community.html"><span class="name">The whole community</span><span>Every brand, and what we have learned together</span></a></li>
    </ul>
  </section>
"""


def localnav(title, links):
    """Apple-style chapter bar under the header on long pages."""
    a = "".join(f'<a href="#{i}">{E(t)}</a>' for i, t in links)
    return f'  <nav class="localnav" aria-label="On this page"><span class="ln-title">{E(title)}</span><span class="ln-links">{a}</span></nav>\n'


def to_seconds(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def highlights_html(spotify):
    rows = "\n".join(
        f'      <li><a href="{spotify}?t={to_seconds(t)}" target="_blank" rel="noopener"><span class="t">{t}</span>'
        f'<span class="hl-title">{E(title)}</span><span class="hl-play" aria-hidden="true">Play on Spotify &#8599;</span></a></li>'
        for t, title in HIGHLIGHTS)
    return f'    <ol class="highlights">\n{rows}\n    </ol>\n    <p class="src" style="margin-top:14px">Times may be a few seconds off on Spotify.</p>'


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


def record_card():
    parts = EPISODES[0]["parts"]
    rows = [("Episodes on record", len(parts)), ("Moments in the highlights", len(HIGHLIGHTS)), ("Brands that presented it", 2)]
    li = "".join(f'<li><span>{E(k)}</span><b>{v}</b></li>' for k, v in rows)
    return (f'<aside class="rec-card" aria-label="This conversation in numbers"><div class="rec-top"><span>Akanksha Sood Singh</span>'
            f'<span class="rec-badge">Part two is out</span></div>'
            f'<p class="rec-title">Part one <span aria-hidden="true">&#8594;</span> <em>Part two</em></p><ul>{li}</ul></aside>')


HOME_CRAFT = [(mf(c["image"]), c.get("title", ""), c.get("note", ""), bool(c.get("wide"))) for c in HOME.get("craft", []) if c.get("image")]


def build():
    ep = EPISODES[0]
    p1, p2 = ep["parts"][0], ep["parts"][-1]

    # home
    H_ = HOME
    tile_links = [("t-light t-full", [("{P}community.html", "Meet the brands"), ("{P}join.html", "Apply to join")]),
                  ("t-dark", [("{P}independent-society.html", "Learn more"), (SPOTIFY_SHOW, "Listen on Spotify")]),
                  ("t-white", [("{P}the-other-details/", "Read the studies"), ("{P}the-other-details/#lead", "Send a detail")])]
    def tile(cls_links, bd):
        cls, links = cls_links
        ls = "".join(f'<a class="tlink" href="{h}"{" target=_blank rel=noopener" if h.startswith("http") else ""}>{E(t)}</a>' for h, t in links if h)
        pic = f'<div class="tile-img">{img(mf(bd.get("image")), "", "")}</div>' if bd.get("image") else ""
        return (f'    <article class="tile {cls}"><div class="tile-text"><h2 class="display">{T(bd.get("title", ""))}</h2>'
                f'<p>{E(bd.get("text", ""))}</p><div class="tile-links">{ls}</div></div>{pic}</article>')
    bands = "\n".join(tile(cl, bd) for cl, bd in zip(tile_links, H_.get("bands", [])))
    pillars = "\n".join(
        f'      <article class="pillar"><figure class="photo pillar-img">{img(mf(pl.get("image")), pl.get("title", ""), "")}</figure>'
        f'<h3>{T(pl.get("title", ""))}</h3><p class="pillar-line">{T(pl.get("line", ""))}</p>'
        f'<ul>{"".join(f"<li>{E(x)}</li>" for x in pl.get("points", []) if x)}</ul></article>'
        for pl in H_.get("pillars", []))
    steps = "\n".join(f'      <li><span class="dot">{i + 1}</span><span class="st">{E(st.get("title", ""))}</span><span class="sd">{E(st.get("text", ""))}</span></li>'
                      for i, st in enumerate(H_.get("steps", [])))
    home = (read("pages", "home.html")
            .replace("{HERO_TITLE}", T(H_.get("hero_title", ""))).replace("{HERO_TEXT}", E(H_.get("hero_text", "")))
            .replace("{BANDS}", bands)
            .replace("{CRAFT}", craft_reel(HOME_CRAFT, H_.get("craft_title", ""), T(H_.get("craft_text", "")), ""))
            .replace("{BRANDS_TITLE}", T(H_.get("brands_title", ""))).replace("{BRANDS_TEXT}", E(H_.get("brands_text", "")))
            .replace("{HOME_BRANDS}", "\n".join(home_brand_row(b, "") for b in BRANDS))
            .replace("{LISTEN_LATEST}", listen_buttons(p2))
            .replace("{HOW_TITLE}", T(H_.get("how_title", ""))).replace("{HOW_TEXT}", E(H_.get("how_text", "")))
            .replace("{PILLARS}", pillars).replace("{STEPS_TITLE}", E(H_.get("steps_title", ""))).replace("{STEPS}", steps)
            .replace("{FOCUS_TABLE}", focus_table("")))
    head, body = page("Zeroing",
                      "Zeroing is a community of Indian brands and the people behind them, and home of the Independent Society podcast.",
                      home, P="", H="")
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

    # Independent Society
    is_main = (read("pages", "independent-society.html")
               .replace("{EP1_LINKS}", listen_buttons(p1)).replace("{EP2_LINKS}", listen_buttons(p2))
               .replace("{EP1_TITLE}", E(p1["title"])).replace("{EP2_TITLE}", E(p2["title"]))
               .replace("{HIGHLIGHTS}", highlights_html(p2["spotify"]))
               .replace("{RECORD_CARD}", record_card())
               .replace("{YOUTUBE_CHANNEL_BTN}", f'<a class="pill line" href="{YOUTUBE_CHANNEL}" target="_blank" rel="noopener">Watch on YouTube <span class="arr" aria-hidden="true">&#8599;</span></a>' if YOUTUBE_CHANNEL else ""))
    is_main = is_main.replace("  </section>\n", "  </section>\n" + localnav('Independent Society', [('why-show', 'Why it exists'), ('episodes', 'Episodes'), ('highlights', 'Highlights'), ('suggest', 'Suggest a guest')]), 1)
    simple = [
        ("independent-society.html", "Independent Society", "One person at a time, a long honest conversation about working life in India, seen from the inside.", is_main, "podcast"),
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
    main = main.replace("  </section>\n", "  </section>\n" + localnav('Akanksha Sood Singh', [('parts', 'Both parts'), ('highlights', 'Highlights'), ('about', 'The conversation'), ('field', 'In the field')]), 1)
    head, body = page("Akanksha Sood Singh on Independent Society",
                      "Wildlife filmmaker Akanksha Sood Singh in conversation with Anshul Kumar on Independent Society. Episodes 1 and 2, on Spotify.",
                      main, P="../", H="../index.html", current="podcast")
    write("episodes/akanksha-sood-singh.html", full_doc(head, body))
    print("built", 8 + len(BRANDS), "pages")
    from research import build_research
    build_research()


if __name__ == "__main__":
    build()
