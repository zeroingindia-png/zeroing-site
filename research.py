"""Build The Other Details research section into public/research/.

    python3 build.py          (calls build_research() at the end)

Studies live in src/research/studies.json: add one entry to add a study page.
Styling is Tailwind (src/research/input.css + utilities in the markup below),
compiled to public/research/lab.css by the Tailwind standalone CLI.
"""
import html, json, os, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "research")
OUT = os.path.join(ROOT, "public", "research")
TAILWIND = os.environ.get("TAILWIND", "tailwindcss")   # path to the standalone CLI (v3.4)
DOT = {"teal": "bg-teal", "red": "bg-red", "gold": "bg-gold"}
VERDICT = {"current": "Current", "outdated": "Outdated", "check": "Check", "excluded": "Excluded"}


def loop(name, cls="loop"):
    return (f'<video class="{cls}" autoplay muted loop playsinline poster="media/{name}.jpg" aria-hidden="true">'
            f'<source src="media/{name}.mp4" type="video/mp4"></video>')


def rows(items):
    return "".join(f'<div class="row"><span class="dot {DOT[c]}"></span><span class="l">{l}</span><span class="n">{n}</span></div>'
                   for l, n, c in items)


def shell(title, desc, here, main):
    nav = [("index.html", "Studies", "home"), ("data-centres.html", "Data centres", "data-centres"),
           ("gold.html", "Gold", "gold"), ("method.html", "Method", "method")]
    links = "".join(f'<a href="{h}" class="whitespace-nowrap rounded-lg px-2 py-1.5 text-[12px] sm:px-3 sm:text-[13px] font-semibold no-underline '
                    f'{"bg-white/[.07] text-paper ring-1 ring-inset ring-edge" if k == here else "text-muted hover:text-paper"}"'
                    f'{" aria-current=page" if k == here else ""}>{t}</a>' for h, t, k in nav)
    crumb = dict((k, t) for _, t, k in nav).get(here, "Studies")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}">
<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="lab.css"></head>
<body>
<header class="sticky top-0 z-40 border-b border-edge bg-ink/80 backdrop-blur-md">
  <div class="wrap flex items-center justify-between gap-2 py-3.5">
    <a href="../index.html" class="chip no-underline max-sm:hidden">Zeroing · The Other Details</a>
    <nav aria-label="Research" class="flex gap-0.5">{links}</nav>
    <a href="index.html" aria-label="The Other Details research, home"><img src="tod-logo.png" alt="the other details." class="h-4 w-auto shrink-0 sm:h-5"></a>
  </div>
</header>
<main>
{main}
</main>
{footer(crumb)}
<script src="charts.js"></script>
</body></html>
"""


def footer(crumb):
    col = lambda h, items: (f'<div><h4 class="mb-2.5 text-xs font-semibold text-paper">{h}</h4><ul class="grid gap-2">'
                            + "".join(f'<li><a class="text-muted no-underline hover:text-paper hover:underline" href="{u}"'
                                      f'{" target=_blank rel=noopener" if u.startswith("http") else ""}>{t}</a></li>' for t, u in items)
                            + "</ul></div>")
    return f"""<footer class="border-t border-edge bg-ink/90 pb-10 pt-7 text-xs leading-relaxed text-muted">
 <div class="wrap">
  <div class="grid gap-2.5 border-b border-edge pb-5">
   <p class="max-w-[110ch]">Every figure is traced to the report that first published it and marked with a verdict. <b class="text-paper">Current</b>: primary source, recent. <b class="text-paper">Outdated</b>: older than about two years and still widely quoted. <b class="text-paper">Check</b>: reported second-hand or does not reconcile. <b class="text-paper">Excluded</b>: no named or reliable source.</p>
   <p>Data belongs to its original sources and owners. The Other Details only presents it, to help more people understand it. Footage: free Pexels stock video.</p>
  </div>
  <div class="flex items-center gap-2.5 border-b border-edge py-4 text-paper"><img src="tod-logo.png" alt="the other details." class="h-3.5 w-auto"><span class="text-dim">›</span><span>{crumb}</span></div>
  <div class="grid grid-cols-1 gap-6 py-6 sm:grid-cols-2 lg:grid-cols-5">
   {col("Studies", [("The cloud has an address", "data-centres.html"), ("The gold at home", "gold.html"), ("All studies", "index.html")])}
   {col("The lab", [("How we check data", "method.html"), ("The Other Details", "../the-other-details.html"), ("Send us a detail", "../the-other-details.html#lead")])}
   {col("Primary sources", [("World Gold Council", "https://www.gold.org/goldhub"), ("CEEW", "https://www.ceew.in"), ("MeitY", "https://www.meity.gov.in"), ("WRI India", "https://wri-india.org"), ("Reserve Bank of India", "https://www.rbi.org.in")])}
   {col("Zeroing", [("Home", "../index.html"), ("Independent Society", "../independent-society.html"), ("Community", "../community.html"), ("Contact", "../contact.html")])}
   {col("Follow", [("@theotherdetails", "https://www.instagram.com/theotherdetails/"), ("@zeroingnow", "https://www.instagram.com/zeroingnow/")])}
  </div>
  <div class="flex flex-wrap justify-between gap-3 border-t border-edge pt-4"><span>© Zeroing · The Other Details. All data credited to its owners.</span><a class="text-muted no-underline hover:text-paper" href="../legal.html">Disclaimer, privacy and terms</a></div>
 </div>
</footer>"""


def hero(video_html, chip, accent, h1, lede, extra="", tall=False):
    return f"""<section class="relative flex {'min-h-[min(86vh,820px)]' if tall else 'min-h-[min(72vh,640px)]'} items-end overflow-hidden border-b border-edge">
  {video_html}
  <div class="absolute inset-0 bg-gradient-to-b from-ink/35 via-ink/55 to-ink"></div>
  <div class="wrap relative w-full pb-16 pt-28"><span class="chip chip-{accent}">{chip}</span><h1 class="h-hero">{h1}</h1><p class="lede">{lede}</p>{extra}</div>
</section>"""


def reel_box(name, label, h3, text):
    return f"""<div class="glass mt-7 grid items-center gap-10 p-8 md:grid-cols-[300px_1fr]">
  <div class="aspect-[9/16] w-full max-w-[280px] rounded-[28px] border border-edge bg-[#1b1d23] p-2"><video controls playsinline preload="none" poster="media/{name}-poster.jpg" class="h-full w-full rounded-[21px] bg-black object-cover"><source src="media/{name}.mp4" type="video/mp4"></video></div>
  <div class="grid gap-3.5"><span class="chip">{label}</span><h3 class="h-sec text-3xl">{h3}</h3><p class="max-w-[52ch] text-muted">{text}</p></div>
</div>"""


def study_page(s):
    words = "".join(f'<dt class="font-head font-black">{w}</dt><dd class="mb-2 text-[15px] text-muted">{d}</dd>' for w, d in s["words"])
    chaps = ""
    for i, c in enumerate(s["chapters"]):
        flip = "md:[&>*:first-child]:order-2 md:grid-cols-[1.2fr_.8fr]" if i % 2 else "md:grid-cols-[.8fr_1.2fr]"
        fig = f'<div class="fig glass p-6" id="f-{c["fig"]}"></div>' if c["fig"] else ""
        chaps += f"""
  <article class="mt-16 grid items-start gap-10 {flip}">
    <div class="aspect-[16/10] overflow-hidden rounded-2xl border border-edge md:sticky md:top-24 md:aspect-[4/5]">{loop(c["video"])}</div>
    <div class="grid min-w-0 gap-4"><span class="chip chip-{s['accent']}">{c['chip']}</span><h2 class="h-sec">{c['title']}</h2><p class="max-w-[62ch] text-muted">{c['text']}</p>{fig}<p class="why">{c['why']}</p><p class="src">Sources · {c['src']}</p></div>
  </article>"""
    take = "".join(f"<li>{t}</li>" for t in s["takeaways"])
    ledger = "".join(f'<div class="vrow"><span class="max-md:col-span-2">{a}</span><span class="font-head font-black">{b}</span><span class="text-muted">{c}</span><span><span class="st st-{d}">{VERDICT[d]}</span></span></div>'
                     for a, b, c, d in s["ledger"])
    reel = reel_box(s["reel"], "The film · 2:13", "Watch the study <i>on your phone.</i>", "The same numbers as a vertical film, narrated, with captions and every source on screen.") if s["reel"] else ""
    main = hero(loop(s["hero"], "absolute inset-0 h-full w-full object-cover"), f'{s["chip"]} · {s["read"]} read', s["accent"],
                f'{s["title"]} <i>{s["ital"]}</i>', s["lede"]) + f"""
<div class="wrap pb-24">
  <div class="relative z-10 -mt-12 grid gap-5 md:grid-cols-2">
    <div class="glass"><div class="flex justify-between px-5 pb-2 pt-4 text-xs font-semibold uppercase tracking-[.14em] text-muted"><span>{s['stats_title']}</span><b class="font-semibold text-red">{s['stats_note']}</b></div>{rows(s['stats'])}</div>
    <div class="glass grid gap-3 p-6"><span class="chip chip-{s['accent']}">Before you start</span><h3 class="h-sec text-3xl">Three words <i>you'll need.</i></h3><dl>{words}</dl></div>
  </div>{chaps}
  <div class="glass mt-16 p-7"><span class="chip chip-{s['accent']}">Key takeaways</span><ol class="mt-3.5 grid list-decimal gap-2.5 pl-6 font-head text-xl font-black leading-snug marker:text-teal">{take}</ol></div>
  {reel}
  <div class="glass mt-7 overflow-hidden"><div class="flex justify-between px-5 pb-2 pt-4 text-xs font-semibold uppercase tracking-[.14em] text-muted"><span>Every number, with its verdict</span><b class="font-semibold text-red">{len(s['ledger'])} facts</b></div>
  <div class="vrow max-md:hidden text-[11px] font-semibold uppercase tracking-[.14em] text-muted"><span>Claim</span><span>Value</span><span>Source · as of</span><span>Verdict</span></div>{ledger}</div>
</div>"""
    return shell(f'{s["title"]} {s["ital"]} · The Other Details', s["lede"], s["slug"], main)


def home_page(studies):
    mosaic = ('<div class="absolute inset-0 grid grid-cols-2 gap-1 md:grid-cols-[1.2fr_.8fr_1.2fr]" aria-hidden="true">'
              + loop("dc-servers") + loop("gd-bangles") + loop("dc-cracked", "loop max-md:hidden") + "</div>")
    ctas = '<div class="mt-7 flex flex-wrap gap-3"><a class="btn" href="data-centres.html">Start with Study 01</a><a class="btn btn-ghost" href="method.html">How we check data</a></div>'
    cards = ""
    for s in studies:
        cards += f"""<a class="glass group flex flex-col overflow-hidden no-underline transition hover:-translate-y-1 hover:border-teal/40" href="{s['slug']}.html">
      <div class="relative aspect-video overflow-hidden border-b border-edge">{loop(s['hero'], 'loop brightness-[.85]')}<span class="sticker bottom-4 left-4">{s['sticker']}</span></div>
      <div class="grid gap-3.5 p-6"><span class="chip chip-{s['accent']}">{s['chip']}</span><span class="font-head text-[26px] font-black leading-tight tracking-tight [&>i]:font-ital [&>i]:font-medium [&>i]:italic [&>i]:text-red">{s['question']}</span></div>
      <div class="border-t border-edge">{rows(s['card'])}</div>
      <span class="mt-auto border-t border-edge px-6 py-4 text-sm font-semibold text-teal">Read the study · {s['read']} →</span></a>"""
    main = hero(mosaic, "Zeroing research lab · every number traced", "teal",
                "The other details. <i>Drawn so anyone can read them.</i>",
                "We read the reports behind the headlines, check where each number comes from and how old it is, and turn it into reels, charts and lessons anyone can follow.", ctas, tall=True) + f"""
<div class="wrap pb-24">
  <div class="mt-20 grid gap-3.5"><span class="chip">Studies</span><h2 class="h-sec">Two questions, <i>answered with data.</i></h2></div>
  <div class="mt-10 grid gap-6 md:grid-cols-2">{cards}</div>
  <div class="mt-20 grid gap-3.5"><span class="chip chip-teal">Watch</span><h2 class="h-sec">Each study is also <i>a two-minute film.</i></h2></div>
  {reel_box("reel-cloud", "Reel · 2:13 · 9:16", "The cloud has <i>an address.</i>", "Real footage, dot charts drawn to scale and every source on screen. Made for phones, with captions and narration.")}
</div>"""
    return shell("Research · The Other Details", "The research lab of Zeroing: the numbers behind the news, traced to their sources and drawn so anyone can read them.", "home", main)


def method_page():
    rules = [("Trace to the origin", "Every figure goes back to the report that first published it, not the article that repeated it."),
             ("Check the date", "Older than about two years, or arithmetic that does not reconcile: labelled or replaced."),
             ("Ranges stay ranges", "Forecasts are dashed, estimates show their spread, \"more than\" keeps its open end."),
             ("One chart per job", "Squares for \"times\", unit grids for shares, lines for time, fans for forecasts, maps for place."),
             ("Fair and timeless", "No sides taken, no seasons named, nobody mocked. The data leads."),
             ("Credit the owners", "Data belongs to its original sources and owners. The Other Details only presents it.")]
    cards = "".join(f'<div class="glass p-6"><span class="font-head text-sm font-black tracking-widest text-teal">{i + 1:02d}</span><h3 class="mt-2.5 font-head text-2xl font-black tracking-tight">{h}</h3><p class="mt-2.5 text-muted">{p}</p></div>'
                    for i, (h, p) in enumerate(rules))
    main = f"""<section class="wrap pb-24 pt-14"><span class="chip chip-teal">How the lab works</span><h1 class="h-hero">Data can be wrong. <i>We check anyway.</i></h1>
<p class="lede">The same six rules run every study, from the first search to the last frame of the reel.</p>
<div class="mt-10 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{cards}</div></section>"""
    return shell("Method · The Other Details", "How The Other Details checks every number before it reaches a page or a reel.", "method", main)


def build_research():
    studies = json.load(open(os.path.join(SRC, "studies.json"), encoding="utf-8"))
    os.makedirs(OUT, exist_ok=True)
    pages = {"index.html": home_page(studies), "method.html": method_page()}
    pages.update({f"{s['slug']}.html": study_page(s) for s in studies})
    for name, text in pages.items():
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(text)
    shutil.copytree(os.path.join(SRC, "media"), os.path.join(OUT, "media"), dirs_exist_ok=True)
    shutil.copy(os.path.join(SRC, "charts.js"), os.path.join(OUT, "charts.js"))
    # Tailwind scans the generated pages too, so classes written in this file are kept.
    cfg = os.path.join(SRC, "tailwind.config.js")
    try:
        subprocess.run([TAILWIND, "-c", cfg, "-i", os.path.join(SRC, "input.css"), "-o", os.path.join(OUT, "lab.css"),
                        "--content", os.path.join(OUT, "*.html") + "," + os.path.join(SRC, "*.js"), "--minify"],
                       check=True, cwd=ROOT, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print("research: Tailwind CLI not run, keeping the existing lab.css:", e)
    print("built", len(pages), "research pages")
