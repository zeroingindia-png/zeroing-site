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

TODO = ''   # unknown values are hidden, never shown as a placeholder
COLOURS = ["peepal", "haldi", "genda", "kattha", "neel", "sindoor"]

BRANDS = []
for n, x in enumerate(load("brands.json")):
    d = {"slug": x.get("slug") or slugify(x["name"]), "name": x["name"], "colour": x.get("colour") or COLOURS[n % len(COLOURS)],
         "line": x.get("line", ""), "makes": x.get("makes", ""),
         "idea": [q.strip() for q in (x.get("about") or "").split("\n\n") if q.strip()],
         "role": x.get("role") or "Community brand", "city": x.get("city", ""), "founder": x.get("founder", ""),
         "sustainability": x.get("sustainability", ""), "nature": x.get("nature", ""), "culture": x.get("culture", ""), "site": (x.get("website") or "").strip(),
         "instagram": (x.get("instagram") or "").strip().lstrip("@"),
         "logo": mf(x["logo"]) if x.get("logo") else "",
         "home": x.get("show_on_home", True),
         "products": [p for p in x.get("products", []) if p.get("name") and p.get("link")],
         "practices": [p for p in x.get("practices", []) if p.get("text")]}
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
ON_HOME = [b for b in BRANDS if b["home"]]
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
<link rel="icon" href="%%ROOT%%favicon.ico" sizes="32x32"><link rel="icon" href="%%ROOT%%favicon.svg" type="image/svg+xml"><link rel="icon" href="%%ROOT%%icon-192.png" type="image/png" sizes="192x192"><link rel="apple-touch-icon" href="%%ROOT%%apple-touch-icon.png">
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
                .replace("{CUR_SHOP}", cur("shop"))
                .replace("LOGO", LOGO))


def page(title, desc, main, P, H, current=""):
    head = HEAD.format(title=E(title), desc=E(desc), css=CSS).replace("%%ROOT%%", P)
    body = (HEADER + "\n<main>\n" + main + "\n" + CLOSING + "</main>\n\n<script>\n" + JS + "</script>\n")
    return head, fill(body, P, H, current)


def full_doc(head, body):
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="google-site-verification" content="I_2Pg3-2TY7JPOtMuB0WfO8n1XlkgRyKxHc2pVj1v-s">\n'
            + head + "\n</head>\n<body>\n" + body + "</body>\n</html>\n")


def write(path, text):
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)



def lane_html(P):
    stalls = []
    for i, b in enumerate(ON_HOME):
        mark = img(b["logo"], b["name"], P) if b.get("logo") else f'<span class="bname">{E(b["name"])}</span>'
        stalls.append(f'      <li class="stall" style="--i:{i}"><a href="{P}brands/{b["slug"]}.html"><span class="awning" aria-hidden="true"></span>'
                      f'<span class="board">{mark}</span><span class="what">{E(b["makes"] or b["line"])}</span></a></li>')
    n = len(ON_HOME)
    for j in range(3):
        stalls.append(f'      <li class="stall empty" style="--i:{n + j}"><span class="awning" aria-hidden="true"></span>'
                      f'<span class="board"><span class="soon">New in 2026</span></span></li>')
    stalls.append(f'      <li class="stall open" style="--i:{n + 3}"><a href="{P}join.html"><span class="awning" aria-hidden="true"></span>'
                  f'<span class="board"><span class="soon">Yours?</span></span><span class="what">Take a stall with us</span></a></li>')
    return '    <ol class="lane" aria-label="The lane: brands in Zeroing">\n' + "\n".join(stalls) + '\n    </ol>'


AREAS = ["Materials", "Packaging", "Making", "People", "Next step"]
LEVELS = {"founder": "Founder says", "proof": "Proof shared", "checked": "Checked by Zeroing"}


def shop_url_of(b):
    if b["site"]:
        return b["site"], "Visit the shop"
    if b["instagram"]:
        return f"https://www.instagram.com/{b['instagram']}/", "Shop on Instagram"
    return "", ""


def shop_cards(P):
    out = []
    for b in BRANDS:
        url, label = shop_url_of(b)
        head = (f'    <div class="shop-brand">{f'<span class="brand-logo">{img(b["logo"], "", P)}</span>' if b.get("logo") else ""}<h2 class="display"><a href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a></h2>'
                f'<p>{E(b["line"])}</p></div>')
        cards = []
        for p in b["products"]:
            pic = (f'<span class="card-img">{img(mf(p["image"]), p["name"], P)}</span>' if p.get("image")
                   else f'<span class="card-img colour" style="background:var(--{b["colour"]})"><span>{E(b["name"][:1])}</span></span>')
            price = f'<span class="price">{E(p["price"])}</span>' if p.get("price") else ""
            cards.append(f'      <a class="product" href="{E(p["link"])}" target="_blank" rel="noopener">{pic}'
                         f'<span class="pbody"><span class="pname">{E(p["name"])}</span>{price}'
                         f'<span class="pgo">Buy on {E(b["name"])} <span aria-hidden="true">&#8599;</span></span></span></a>')
        if not cards and url:
            btn = f'<a class="pill line" href="{url}" target="_blank" rel="noopener">{label} <span class="arr" aria-hidden="true">&#8599;</span></a>'
            cards.append(f'      <div class="product empty"><span class="pbody"><span class="pname">See everything {E(b["name"])} makes on its own shop.</span>{btn}</span></div>')
        prods = ('\n    <div class="products">\n' + "\n".join(cards) + '\n    </div>') if cards else ''
        out.append(f'    <div class="shop-row">\n{head}{prods}\n    </div>')
    return "\n".join(out)


def practices_html(P):
    if sum(1 for b in BRANDS if b["practices"]) < 3:
        return ""
    rows = []
    for b in BRANDS:
        items = "".join(
            f'<li data-area="{E(p.get("area", ""))}"><span class="parea">{E(p.get("area", ""))}</span>'
            f'<span class="ptext">{E(p["text"])}</span>'
            f'<span class="lv lv-{p.get("level", "founder")}">{LEVELS.get(p.get("level", "founder"), LEVELS["founder"])}</span></li>'
            for p in b["practices"])
        if not items:
            continue   # a brand that has not shared its practices is left out of the list
        rows.append(f'    <div class="pbrand"><h3><a href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a></h3><ul>{items}</ul></div>')
    return '    <div class="plist">\n' + "\n".join(rows) + '\n    </div>'


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
    # a real photograph if there is a good one, otherwise the brand's own logo; never a cropped strip of artwork
    # every community card shows the brand's own logo, so the brands sit side by side as equals
    if b.get("logo"):
        return f'<span class="card-img logo">{img(b["logo"], b["name"] + " logo", P)}</span>'
    if b.get("hero"):
        return f'<span class="card-img">{img(b.get("thumb") or b["hero"][0], b["hero"][1], P)}</span>'
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


SHOWCASE = {
    "indso": ("media/logo-indso.png", "word"),
    "ampor-eyewear": ("media/logo-ampor-eyewear.png", "word"),
    "vedi-kade": ("media/logo-vedi-kade.png", "word"),
}


def home_brand_row(b, P):
    if b["slug"] in SHOWCASE:
        src, kind = SHOWCASE[b["slug"]]
        src = src if kind == "remote" else P + src
        out = b["site"] or (f'https://www.instagram.com/{b["instagram"]}/' if b["instagram"] else "")
        label = b["site"].replace("https://", "").rstrip("/") if b["site"] else (f'@{b["instagram"]}' if b["instagram"] else "")
        go = f'<a class="sc-out" href="{out}" target="_blank" rel="noopener">{E(label)} &#8599;</a>' if out else ""
        return (f'      <li class="sc sc-{kind}"><a class="sc-img" href="{P}brands/{b["slug"]}.html" aria-label="{E(b["name"])}"><img src="{src}" alt="{E(b["name"])}: {E(b["makes"])}" loading="lazy" decoding="async"{(" onerror=" + chr(34) + "this.onerror=null;this.src='" + P + "media/logo-" + b["slug"] + ".png';this.style.objectFit='contain';this.style.padding='18%'" + chr(34)) if kind == "remote" and b.get("logo") else ""}></a>'
                f'<div class="sc-meta"><a class="sc-name" href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a><span>{E(b["makes"])}</span>{go}</div></li>')
    if b.get("logo"):
        thumb = f'<span class="thumb logo">{img(b["logo"], "", P)}</span>'
    elif b.get("hero"):
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
            if out else '')
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


def focus_block(b):
    # only what the founder has confirmed; nothing at all if nothing is confirmed
    cells = "".join(
        f'<div class="fc fc-{k}"><span class="fk">{t}</span><p>{E(b[k])}</p></div>' for k, t in FOCUS if b.get(k))
    return (f'<h3 class="sub">Where {E(b["name"])} stands</h3>\n        <div class="focus">{cells}</div>') if cells else ''


def focus_table(P):
    # brands with nothing confirmed are left out, and so are columns nobody has filled
    brands = [b for b in ON_HOME if any(b.get(k) for k, _ in FOCUS)]
    cols = [(k, t) for k, t in FOCUS if any(b.get(k) for b in brands)]
    if not brands or not cols:
        return ''
    head = "".join(f'<th scope="col">{t}</th>' for _, t in cols)
    rows = "".join(
        f'<tr><th scope="row"><a href="{P}brands/{b["slug"]}.html">{E(b["name"])}</a></th>'
        + "".join(f'<td data-label="{t}">{E(b[k])}</td>' if b.get(k) else '<td class="empty"></td>' for k, t in cols) + '</tr>'
        for b in brands)
    return ('<h3 class="steps-title">What each brand tells us</h3>\n    '
            f'<div class="focus-wrap"><table class="focus-table"><thead><tr><th scope="col">Brand</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>')


def brand_main(b, P="../"):
    idea = "\n".join(f"        <p>{E(p)}</p>" for p in b["idea"])
    if b["site"]:
        shop_url, shop_label, nav_label = b["site"], f'Visit {E(b["site"].replace("https://", ""))}', "Visit"
    elif b["instagram"]:
        shop_url, shop_label, nav_label = f'https://www.instagram.com/{b["instagram"]}/', f'@{E(b["instagram"])} on Instagram', "Instagram"
    else:
        shop_url = shop_label = nav_label = ""
    shop_btn = (f'<a class="pill solid" href="{shop_url}" target="_blank" rel="noopener">{shop_label} <span class="arr" aria-hidden="true">&#8599;</span></a>'
                if shop_url else '')
    ig_btn = (f'<a class="pill line" href="https://www.instagram.com/{b["instagram"]}/" target="_blank" rel="noopener">@{b["instagram"]}</a>'
              if b["site"] and b["instagram"] else "")
    if b.get("hero"):
        # photo-led: the logo is the heading, the photograph sits beside it
        photo = f'<div class="hero-photo">{img(b["hero"][0], b["hero"][1], P, eager=True)}</div>'
        title = (f'<h1 class="display brand-mark">{img(b["logo"], b["name"], P, eager=True)}</h1>' if b.get("logo")
                 else f'<h1 class="display">{E(b["name"])}</h1>')
        cls = ""
    elif b.get("logo"):
        # logo-led: no weak photograph, the brand's own mark on a clean panel
        photo = f'<div class="hero-photo logo">{img(b["logo"], b["name"] + " logo", P, eager=True)}</div>'
        title, cls = f'<h1 class="display">{E(b["name"])}</h1>', " logo-led"
    else:
        photo, cls = "", " no-photo"
        title = f'<h1 class="display">{E(b["name"])}</h1>'
    craft = craft_reel(b["craft"], b["craft_title"], E(b["craft_line"]), P) if b.get("craft") else ""
    others = [o for o in BRANDS if o["slug"] != b["slug"]]
    nxt = "\n".join(
        f'      <li><a href="{o["slug"]}.html"><span class="name">{E(o["name"])}</span><span>{E(o["makes"])}</span></a></li>'
        for o in others)
    focus = focus_block(b)
    has_story = bool(b["idea"] or focus)
    about_title = "About" if has_story else "At a glance"
    chapters = [("about", about_title)] + ([("craft", b["craft_title"])] if b.get("craft") else []) + [("more", "More from the community")]
    LN = localnav(b["name"], chapters).replace('</span></nav>', (f'<a class="ln-buy" href="{shop_url}" target="_blank" rel="noopener">{nav_label}</a>' if shop_url else '') + '</span></nav>')
    facts = "".join(x for x in [
        f"<div><dt>Makes</dt><dd>{E(b['makes'])}</dd></div>" if b['makes'] else '',
        f"<div><dt>Made in</dt><dd>India{(', ' + E(b['city'])) if b['city'] else ''}</dd></div>",
        f"<div><dt>Founder</dt><dd>{E(b['founder'])}</dd></div>" if b['founder'] else '',
        f"<div><dt>Website</dt><dd>{site_link(b['site'])}</dd></div>" if b['site'] else '',
        f"<div><dt>Instagram</dt><dd>{ig(b['instagram'])}</dd></div>" if b['instagram'] else '',
    ])
    if has_story:
        about = f"""      <div class="idea">
        <h2 class="display">About</h2>
{idea}
        {focus}
      </div>
      <dl class="facts-list">{facts}</dl>"""
    else:
        about = f"""      <div class="idea">
        <h2 class="display">At a glance</h2>
      </div>
      <dl class="facts-list">{facts}</dl>"""
    return f"""  <section class="field f-{b['colour']} hero brand-hero{cls}" id="top">
    <div class="hero-text">
      <div class="hero-body">
        <p class="corners narrow" style="margin:0;padding:0">{E(b['role'])}</p>
        {title}
        <p class="lede">{E(b['line'])}</p>
        {f'<div class="actions">{shop_btn}{ig_btn}</div>' if shop_btn or ig_btn else ''}
      </div>
    </div>
    {photo}
  </section>
{LN}
  <section class="field f-chuna auto" id="about">
    <div class="about">
{about}
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
    yt = part.get("youtube") or "https://www.youtube.com/@zeroingnow"
    out.append(f'<a class="pill {"solid" if solid else "line"}" href="{yt}" target="_blank" rel="noopener">Watch on YouTube <span class="arr" aria-hidden="true">&#8599;</span></a>')
    return "".join(out)


def spotify_embed(url, title):
    if not url:
        return ""
    eid = url.rstrip("/").split("/")[-1]
    return (f'<iframe class="player" title="{E(title)} on Spotify" src="https://open.spotify.com/embed/episode/{eid}?theme=0" '
            f'loading="lazy" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"></iframe>')


def record_card():
    parts = EPISODES[0]["parts"]
    rows = [("Episodes on record", len(parts)), ("Next on record", "Inderjeet Singh"), ("Then", "Vijay Kumar Shukla")]
    li = "".join(f'<li><span>{E(k)}</span><b{"" if isinstance(v, int) else " class=" + chr(34) + "txt" + chr(34)}>{v}</b></li>' for k, v in rows)
    return (f'<aside class="rec-card" aria-label="This conversation in numbers"><div class="rec-top"><span>Akanksha Sood Singh</span>'
            f'<span class="rec-badge">Part two is out</span></div>'
            f'<p class="rec-title">Part one <span aria-hidden="true">&#8594;</span> <em>Part two</em></p><ul>{li}</ul></aside>')


HOME_CRAFT = [(mf(c["image"]), c.get("title", ""), c.get("note", ""), bool(c.get("wide"))) for c in HOME.get("craft", []) if c.get("image")]


ICON = {
    "community": '<path d="M3 9.5 4.5 4h15L21 9.5"/><path d="M3 9.5c0 1.4 1.3 2.5 3 2.5s3-1.1 3-2.5c0 1.4 1.3 2.5 3 2.5s3-1.1 3-2.5c0 1.4 1.3 2.5 3 2.5s3-1.1 3-2.5"/><path d="M5 12v8h14v-8"/><path d="M10 20v-4h4v4"/>',
    "podcast": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0"/><path d="M12 17.5V21M8.5 21h7"/>',
    "lab": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.3 15.3 5.2 5.2"/><path d="m7.5 12.5 2-2.5 2 1.5 2-3"/>',
    "nature": '<path d="M5 19C5 11 10 5 19 5c0 9-6 14-14 14z"/><path d="M5 19 13 11"/>',
    "culture": '<path d="M3 13h18c-1 4-4.5 6-9 6s-8-2-9-6z"/><path d="M12 10.5c-1.6-1.6-1.6-3.8 0-6.5 1.6 2.7 1.6 4.9 0 6.5z"/>',
    "sustainability": '<path d="M19.5 12a7.5 7.5 0 0 1-13.2 4.9"/><path d="M4.5 12a7.5 7.5 0 0 1 13.2-4.9"/><path d="M18 3.5v3.6h-3.6M6 20.5v-3.6h3.6"/>',
}


def icon(key):
    d = ICON.get(key)
    return (f'<svg class="ico" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{d}</svg>') if d else ""


def build():
    ep = EPISODES[0]
    p1, p2 = ep["parts"][0], ep["parts"][-1]

    # home
    H_ = HOME
    tile_links = [("t-light t-full", [("{P}community.html", "Meet the brands"), ("{P}join.html", "Apply to join")]),
                  ("t-dark", [("{P}independent-society.html", "Learn more"), (SPOTIFY_SHOW, "Listen on Spotify")]),
                  ("t-white", [("{P}the-other-details/", "Read the studies"), ("{P}the-other-details/#lead", "Send a detail")])]
    tile_icons = ["community", "podcast", "lab"]
    def tile(cls_links, bd, ic=""):
        cls, links = cls_links
        ls = "".join(f'<a class="tlink" href="{h}"{" target=_blank rel=noopener" if h.startswith("http") else ""}>{E(t)}</a>' for h, t in links if h)
        pic = f'<div class="tile-img">{img(mf(bd.get("image")), "", "")}</div>' if bd.get("image") else ""
        return (f'    <article class="tile {cls}"><div class="tile-text"><h2 class="display">{icon(ic)}{T(bd.get("title", ""))}</h2>'
                f'<p>{E(bd.get("text", ""))}</p><div class="tile-links">{ls}</div></div>{pic}</article>')
    bands = "\n".join(tile(cl, bd, ic) for cl, bd, ic in zip(tile_links, H_.get("bands", []), tile_icons))
    pillars = "\n".join(
        f'      <article class="pillar">'
        f'<h3>{icon(pl.get("title", "").strip().lower())}{T(pl.get("title", ""))}</h3><p class="pillar-line">{T(pl.get("line", ""))}</p>'
        f'<ul>{"".join(f"<li>{E(x)}</li>" for x in pl.get("points", []) if x)}</ul></article>'
        for pl in H_.get("pillars", []))
    steps = "\n".join(f'      <li><span class="dot">{i + 1}</span><span class="st">{E(st.get("title", ""))}</span><span class="sd">{E(st.get("text", ""))}</span></li>'
                      for i, st in enumerate(H_.get("steps", [])))
    home = (read("pages", "home.html")
            .replace("{HERO_TITLE}", T(H_.get("hero_title", ""))).replace("{HERO_TEXT}", E(H_.get("hero_text", "")))
            .replace("{BANDS}", bands)
            .replace("{CRAFT}", craft_reel(HOME_CRAFT, H_.get("craft_title", ""), T(H_.get("craft_text", "")), ""))
            .replace("{BRANDS_TITLE}", T(H_.get("brands_title", ""))).replace("{BRANDS_TEXT}", E(H_.get("brands_text", "")))
            .replace("{HOME_LANE}", lane_html("")).replace("{HOME_BRANDS}", "\n".join(home_brand_row(b, "") for b in ON_HOME))
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
    is_main = is_main.replace("  </section>\n", "  </section>\n" + localnav('Independent Society', [('why-show', 'Why it exists'), ('episodes', 'Episodes'), ('suggest', 'Suggest a guest')]), 1)
    simple = [
        ("independent-society.html", "Independent Society", "One person at a time, a long honest conversation about working life in India, seen from the inside.", is_main, "podcast"),
        ("join.html", "Join Zeroing", "Apply to join Zeroing, a community of homegrown Indian brands.", read("pages", "join.html"), "join"),
        ("shop.html", "Shop the lane", "Buy straight from the homegrown Indian brands in Zeroing, and see how each one makes it.",
         (read("pages", "shop.html") if sum(1 for b in BRANDS if b["practices"]) >= 3 else __import__("re").sub(r'\s*<div class="pfilter".*?</div>', '', read("pages", "shop.html"), count=1, flags=__import__("re").S)).replace("{SHOP_CARDS}", shop_cards("")).replace("{PRACTICES}", practices_html(""))
         .replace("{AREA_CHIPS}", "" if sum(1 for b in BRANDS if b["practices"]) < 3 else "\n".join(f'      <button type="button" class="chip" aria-pressed="false" data-area="{a}">{a}</button>' for a in AREAS)), "shop"),
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
        + (lambda v: f'        <a class="ep-thumb" href="{p["youtube"]}" target="_blank" rel="noopener" aria-label="Watch {E(p["ep"])} on YouTube"><img src="https://i.ytimg.com/vi/{v}/hqdefault.jpg" alt="{E(p["title"])}" loading="lazy" decoding="async"><span class="ep-play" aria-hidden="true"></span><span class="ep-tag">{E(p["ep"])}</span></a>\n' if v else "")((re.search(r"v=([\w-]+)", p.get("youtube") or "") or [None, None])[1]) +
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
    main = main.replace("  </section>\n", "  </section>\n" + localnav('Akanksha Sood Singh', [('parts', 'Both parts'), ('about', 'The conversation'), ('research', 'The research'), ('field', 'In the field')]), 1)
    head, body = page("Akanksha Sood Singh on Independent Society",
                      "Wildlife filmmaker Akanksha Sood Singh in conversation with Anshul Kumar on Independent Society. Episodes 1 and 2, on Spotify.",
                      main, P="../", H="../index.html", current="podcast")
    write("episodes/akanksha-sood-singh.html", full_doc(head, body))
    main404 = """  <section class="hero3" id="top">
    <p class="kicker">Page not found</p>
    <h1 class="display lane-title"><span class="b1">This stall has moved.</span> <span class="b2">The lane is still here.</span></h1>
    <p class="lede">The link may be old or mistyped. Start from one of these.</p>
    <div class="actions">
      <a class="pill solid" href="/">Home</a>
      <a class="pill line" href="/shop">Shop the lane</a>
      <a class="pill line" href="/independent-society">The podcast</a>
      <a class="pill line" href="/the-other-details/">The Other Details</a>
    </div>
  </section>
"""
    head, body = page("Page not found · Zeroing", "This page has moved. Start from the Zeroing home page.", main404, P="/", H="/")
    write("404.html", full_doc(head, body))
    print("built", 9 + len(BRANDS), "pages")
    from research import build_research
    build_research()
    share_tags()


SITE = "https://zeroingnow.com/"


SEO = {
    "index.html": ("Zeroing · A community of homegrown Indian brands",
                   "Zeroing brings homegrown, made-in-India brands together like stalls in one lane, with Independent Society, a podcast on working life in India, and a research lab."),
    "community.html": ("The Zeroing community · Homegrown brands from India",
                       "Meet the homegrown Indian brands in Zeroing, what we learned from Dastkar, Fashion Revolution and others, and how brands here open doors for each other."),
    "shop.html": ("Shop the lane · Buy from homegrown Indian brands · Zeroing",
                  "Buy straight from INDSO, Ampor Eyewear and other homegrown Indian brands in Zeroing, on their own shops, and see how each one makes its products."),
    "independent-society.html": ("Independent Society · A podcast on working life in India",
                                 "Independent Society by Zeroing: one person at a time, a long honest conversation about working life in India, seen from the inside. Listen on Spotify."),
    "episodes/akanksha-sood-singh.html": ("Akanksha Sood Singh, wildlife filmmaker · Independent Society",
                                          "Wildlife filmmaker Akanksha Sood Singh in conversation with Anshul Kumar on Independent Society by Zeroing. Two parts, on Spotify."),
    "join.html": ("Join Zeroing · Apply as a homegrown Indian brand",
                  "Apply to bring your made-in-India brand into Zeroing. Tell us what you make and one door you could open for another brand. We reply within 14 days."),
    "contact.html": ("Contact Zeroing · Brands, guests, press and creators",
                     "Write to Zeroing to join as a brand, suggest a podcast guest, ask as press or collaborate as a creator. Based in New Delhi."),
    "legal.html": ("Disclaimer, privacy and terms · Zeroing",
                   "How Zeroing handles your data, what we publish and why, and how to raise a grievance."),
}


def _clean_path(rel):
    if rel == "index.html":
        return ""
    if rel.endswith("/index.html"):
        return rel[:-10]
    return rel[:-5] if rel.endswith(".html") else rel


STUDY_TITLES = {
    "the-other-details/roads.html": "Who dies on India's roads: 485 deaths a day, explained · The Other Details",
    "the-other-details/medicine.html": "Why branded medicine costs more in India: Jan Aushadhi vs brand · The Other Details",
    "the-other-details/ethanol.html": "Ethanol in Indian petrol: E20 mileage, water and the cost · The Other Details",
    "the-other-details/method.html": "How The Other Details checks data · Zeroing research lab",
}


def extra_ld(rel, html, url, title, desc):
    """Structured data beyond the home and podcast pages: episodes, guests, brands, studies, breadcrumbs."""
    import re as _re
    out = []
    org = {"@type": "Organization", "name": "Zeroing", "url": SITE}
    crumbs = [("Zeroing", SITE)]
    if rel.startswith("episodes/"):
        crumbs += [("Independent Society", SITE + "independent-society"), ("Akanksha Sood Singh", url)]
        series = {"@type": "PodcastSeries", "name": "Independent Society", "url": SITE + "independent-society"}
        guest = {"@type": "Person", "name": "Akanksha Sood Singh", "jobTitle": "Wildlife filmmaker",
                 "sameAs": ["https://www.instagram.com/themrsass/", "https://thegaiapeople.com"]}
        host = {"@type": "Person", "name": "Anshul Kumar", "sameAs": ["https://www.instagram.com/anzhuls/"]}
        months = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], 1)}
        for i, p in enumerate(PODCAST["parts"], 1):
            d, m, y = p["date"].split()
            iso = f"{y}-{months[m]:02d}-{int(d):02d}"
            ep = {"@type": "PodcastEpisode", "name": p["title"], "episodeNumber": i, "datePublished": iso,
                  "url": url + "#parts", "partOfSeries": series, "actor": [guest], "creator": host,
                  "associatedMedia": {"@type": "MediaObject", "contentUrl": p["spotify"]}}
            out.append(ep)
            v = _re.search(r"v=([\w-]+)", p.get("youtube") or "")
            if v:
                out.append({"@type": "VideoObject", "name": f"{p['title']} | Independent Society Ep.{i:02d}",
                            "description": f"Akanksha Sood Singh in conversation with Anshul Kumar. {p['label']} of the conversation on Independent Society by Zeroing.",
                            "thumbnailUrl": f"https://i.ytimg.com/vi/{v.group(1)}/hqdefault.jpg", "uploadDate": iso,
                            "contentUrl": p["youtube"], "embedUrl": f"https://www.youtube.com/embed/{v.group(1)}", "publisher": org})
    elif rel.startswith("brands/"):
        b = next((x for x in BRANDS if x["slug"] == rel[7:-5]), None)
        if b:
            crumbs += [("Community", SITE + "community"), (b["name"], url)]
            brand = {"@type": "Brand", "name": b["name"], "description": b["line"], "url": url}
            if b.get("logo"):
                brand["logo"] = SITE + b["logo"].lstrip("/")
            out.append(brand)
    elif rel.startswith("the-other-details/") and rel != "the-other-details/index.html":
        crumbs += [("The Other Details", SITE + "the-other-details/"), (title.split(" · ")[0], url)]
        out.append({"@type": "Article", "headline": title.split(" · ")[0][:110], "description": desc, "url": url,
                    "inLanguage": "en-IN", "author": {"@type": "Organization", "name": "The Other Details", "url": SITE + "the-other-details/"},
                    "publisher": org, "isAccessibleForFree": True})
    elif rel in ("community.html", "shop.html", "join.html", "independent-society.html", "the-other-details/index.html", "contact.html"):
        crumbs += [(title.split(" · ")[0], url)]
    if len(crumbs) > 1:
        out.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, "item": u} for i, (n, u) in enumerate(crumbs, 1)]})
    return out


def share_tags():
    """Give every built page a canonical address and a preview card for WhatsApp, LinkedIn, X and others."""
    import glob, re as _re, datetime as _dt
    for full in glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(full, OUT).replace(os.sep, "/")
        if rel.startswith("media/"):
            continue
        html = open(full, encoding="utf-8").read()
        if 'property="og:title"' in html:
            continue

        def clean(m):
            path, frag = m.group(1), m.group(2) or ""
            if path == "index" or path.endswith("/index"):
                path = path[:-5] or "./"
            return f'href="{path}{frag}"'
        html = _re.sub(r'href="(?!https?:|mailto:|tel:|//)([^"#?]*?)\.html(#[^"]*)?"', clean, html)
        url = SITE + _clean_path(rel)
        seo = SEO.get(rel)
        if rel.startswith("brands/"):
            b = next((x for x in BRANDS if x["slug"] == rel[7:-5]), None)
            if b:
                seo = (f"{b['name']}: {b['makes'] or b['line']} · Zeroing",
                       f"{b['name']} is a homegrown Indian brand in the Zeroing community. {b['line']} See how it makes things and buy from its own shop.")
        if seo:
            html = _re.sub(r"<title>.*?</title>", "<title>" + E(seo[0]) + "</title>", html, count=1, flags=_re.S)
            html = _re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + E(seo[1]) + '">', html, count=1)
        html = html.replace('<html lang="en">', '<html lang="en-IN">', 1)
        title = (_re.search(r"<title>(.*?)</title>", html, _re.S) or [None, "Zeroing"])[1].strip()
        desc = (_re.search(r'<meta name="description" content="([^"]*)"', html) or [None, ""])[1]
        hero = _re.search(r'class="hero-photo[^"]*"><img src="([^"]+)"', html)
        image = SITE + "media/share.jpg"
        if hero and rel.startswith(("brands/", "episodes/")):
            image = SITE + _re.sub(r"^(\.\./)+", "", hero.group(1))
        lab_img = _re.search(r'<img src="(media/[^"]+\.jpg)"', html)
        if rel.startswith("the-other-details/") and lab_img:
            image = SITE + "the-other-details/" + lab_img.group(1)
        if rel == "independent-society.html":
            image = SITE + "media/ep-conversation.jpg"
        if rel.startswith("episodes/"):
            image = SITE + "media/as-portrait.jpg"
        if rel in STUDY_TITLES:
            title = STUDY_TITLES[rel]
            html = _re.sub(r"<title>.*?</title>", "<title>" + E(title) + "</title>", html, count=1, flags=_re.S)
        tags = (f'\n<link rel="canonical" href="{url}">'
                f'\n<meta property="og:type" content="website"><meta property="og:site_name" content="Zeroing"><meta property="og:locale" content="en_IN">'
                f'\n<meta property="og:url" content="{url}"><meta property="og:title" content="{title}">'
                f'\n<meta property="og:description" content="{desc}"><meta property="og:image" content="{image}">'
                f'\n<meta name="twitter:card" content="summary_large_image">')
        if rel in ("index.html", "independent-society.html"):
            import json as _json
            org = {"@type": "Organization", "name": "Zeroing", "url": SITE, "logo": SITE + "icon-512.png",
                   "description": "A community of homegrown Indian brands.", "email": "zeroingindia@gmail.com",
                   "sameAs": ["https://www.instagram.com/zeroingnow/", "https://www.instagram.com/theotherdetails/", "https://www.youtube.com/@zeroingnow"]}
            faq = {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in [
                    ("What is Zeroing?", "Zeroing is a community of homegrown, made-in-India brands based in New Delhi. The brands open doors for each other and each sells from its own shop."),
                    ("Which brands are in Zeroing?", "INDSO (botanical skincare), Ampor Eyewear, Vedi Kade (modern clothing with Tamil history in it) and Syzygy Living (design homeware), with three more brands that joined in 2026."),
                    ("What is Independent Society?", "Independent Society is Zeroing's podcast: one person at a time, a long honest conversation about working life in India. It is hosted by Anshul Kumar and is on Spotify."),
                    ("What is The Other Details?", "The Other Details is the research lab of Zeroing. It traces every number it publishes to the page it was first printed on."),
                    ("How can a brand join Zeroing?", "A brand applies on the Join page, says what it makes and names one door it could open for another brand. Zeroing replies within 14 days.")]]}
            data = org if rel == "index.html" else {
                "@type": "PodcastSeries", "name": "Independent Society", "url": url, "author": {"@type": "Person", "name": "Anshul Kumar"},
                "publisher": org, "sameAs": [PODCAST.get("spotify_show", "")], "description": desc}
            data["@context"] = "https://schema.org"
            tags += '\n<script type="application/ld+json">' + _json.dumps(data, ensure_ascii=False) + "</script>"
            if rel == "index.html":
                faq["@context"] = "https://schema.org"
                tags += '\n<script type="application/ld+json">' + _json.dumps(faq, ensure_ascii=False) + "</script>"
        for d in extra_ld(rel, html, url, title, desc):
            d["@context"] = "https://schema.org"
            tags += '\n<script type="application/ld+json">' + __import__("json").dumps(d, ensure_ascii=False) + "</script>"
        if rel.startswith("lab/"):
            tags += '\n<meta name="robots" content="noindex">'
        html = html.replace("</title>", "</title>" + tags, 1)
        open(full, "w", encoding="utf-8").write(html)
    urls = []
    for full in sorted(glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True)):
        rel = os.path.relpath(full, OUT).replace(os.sep, "/")
        if rel.startswith(("media/", "lab/")) or rel == "404.html":
            continue
        urls.append(SITE + _clean_path(rel))
    open(os.path.join(OUT, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{_dt.date.today().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n")
    bots = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Google-Extended", "Applebot-Extended", "CCBot"]
    open(os.path.join(OUT, "robots.txt"), "w").write("User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {SITE}sitemap.xml\n")
    lines = ["# Zeroing", "",
             "> Zeroing is a community of homegrown, made-in-India brands based in New Delhi. Brands stand together like stalls in one lane: they open doors for each other, share customers and suppliers, and each sells from its own shop. Zeroing also runs Independent Society, a long-form podcast about working life in India, and The Other Details, a research lab that traces every number it publishes to its source.", "",
             "## Brands"]
    for b in BRANDS:
        site = f" Shop: {b['site']}." if b.get("site") else ""
        lines.append(f"- [{b['name']}]({SITE}brands/{b['slug']}): {b['line']}{site}")
    lines += ["", "## Pages",
              f"- [Home]({SITE}): what Zeroing is and why it exists",
              f"- [Community]({SITE}community): the brands and what we learned from similar efforts",
              f"- [Shop the lane]({SITE}shop): buy from each brand on its own shop; practices labelled Founder says, Proof shared or Checked by Zeroing",
              f"- [Independent Society]({SITE}independent-society): the podcast, hosted by Anshul Kumar (Instagram @anzhuls), on Spotify and YouTube",
              f"- [Akanksha Sood Singh episode]({SITE}episodes/akanksha-sood-singh): wildlife filmmaker, two parts",
              f"- Episode 01 (19 June 2026) and Episode 02 (23 October 2026): Akanksha Sood Singh with Anshul Kumar, on Spotify and YouTube (youtube.com/watch?v=YZ1K7wolPtA, youtube.com/watch?v=Uqa-n-kpuPQ)",
              f"- Coming next on Independent Society: Inderjeet Singh, shot putter; then Vijay Kumar Shukla, retired CBI investigator",
              f"- Studies: [Roads]({SITE}the-other-details/roads), [Medicine]({SITE}the-other-details/medicine), [Ethanol]({SITE}the-other-details/ethanol), [Data centres]({SITE}the-other-details/data-centres), [Gold]({SITE}the-other-details/gold), [How we check data]({SITE}the-other-details/method)",
              f"- [The Other Details]({SITE}the-other-details/): research lab studies on data centres, gold, roads, medicine and ethanol, with reels on YouTube @zeroingnow",
              f"- [Join]({SITE}join): how a brand applies",
              f"- [Contact]({SITE}contact): zeroingindia@gmail.com, Instagram and YouTube @zeroingnow",
              "", "## Notes", "- Zeroing does not sell products itself and takes no payment.", "- Claims about how brands make things are labelled by how far they have been checked."]
    open(os.path.join(OUT, "llms.txt"), "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    build()
