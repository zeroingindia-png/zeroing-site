"""Build The Other Details, the research lab of Zeroing, into public/the-other-details/.

    python3 build.py          (calls build_research() at the end)

Studies live in src/research/studies.json: add one entry to add a study page.
Styling is Tailwind (src/research/input.css + utilities in the markup below),
compiled to public/research/lab.css by the Tailwind standalone CLI.
"""
import html, json, os, shutil, subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "research")
OUT = os.path.join(ROOT, "public", "the-other-details")
TAILWIND = os.environ.get("TAILWIND", "tailwindcss")   # path to the standalone CLI (v3.4)
DOT = {"teal": "bg-teal", "red": "bg-red", "gold": "bg-gold"}
VERDICT = {"current": "Current", "outdated": "Outdated", "check": "Check", "excluded": "Excluded"}


YT = "https://www.youtube.com/@zeroingnow"


def loop(name, cls="loop"):
    return f'<img class="{cls}" src="media/{name}.jpg" alt="" loading="lazy" decoding="async">'


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
<link rel="icon" href="../favicon.ico" sizes="32x32"><link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="../apple-touch-icon.png"><link rel="stylesheet" href="lab.css"></head>
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
{LAB_POLISH}
</body></html>
"""


LAB_POLISH = """<div class="lab-progress" aria-hidden="true"></div>
<style>
header nav a{display:inline-flex;align-items:center;min-height:40px}
footer li a{display:inline-block;padding:3px 0}
:where([id]){scroll-margin-top:84px}
:focus-visible{outline:2px solid #f4b942;outline-offset:3px;border-radius:4px}
.lab-progress{position:fixed;top:0;left:0;right:0;height:2px;z-index:60;pointer-events:none;transform-origin:0 50%;transform:scaleX(0);background:#e0505c}
@media (max-width:640px){footer li a{padding:7px 0}}
</style>
<script>
(function(){var b=document.querySelector('.lab-progress');if(!b)return;
if(document.documentElement.scrollHeight<innerHeight*4){b.remove();return}
var t=false;function p(){t=false;var m=document.documentElement.scrollHeight-innerHeight;b.style.transform='scaleX('+(m>0?Math.min(1,scrollY/m):0)+')'}
addEventListener('scroll',function(){if(!t){t=true;requestAnimationFrame(p)}},{passive:true});addEventListener('resize',p);p()})();
</script>"""


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
   {col("The lab", [("How we check data", "method.html"), ("Why the lab exists", "index.html#about"), ("Send us a detail", "index.html#lead")])}
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
    return f"""<style>.yt-reel{{position:relative;display:block}}.yt-play{{position:absolute;left:50%;top:50%;width:58px;height:40px;margin:-20px 0 0 -29px;border-radius:12px;background:#FF0000}}.yt-play::after{{content:"";position:absolute;left:23px;top:12px;border-style:solid;border-width:8px 0 8px 14px;border-color:transparent transparent transparent #fff}}</style><div class="glass mt-7 grid items-center gap-10 p-8 md:grid-cols-[300px_1fr]">
  <div class="aspect-[9/16] w-full max-w-[280px] rounded-[28px] border border-edge bg-[#1b1d23] p-2"><a href="{YT}" target="_blank" rel="noopener" class="yt-reel block h-full w-full overflow-hidden rounded-[21px] bg-black"><img src="media/{name}-poster.jpg" alt="Watch on YouTube" loading="lazy" class="h-full w-full object-cover"><span class="yt-play" aria-hidden="true"></span></a></div>
  <div class="grid gap-3.5"><span class="chip">{label}</span><h3 class="h-sec text-3xl">{h3}</h3><p class="max-w-[52ch] text-muted">{text}</p><a class="btn-ghost w-fit" href="{YT}" target="_blank" rel="noopener">Watch on YouTube &#8599;</a></div>
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


ABOUT = """<section id="about" class="lab-about grid gap-6 md:grid-cols-2">
  <div class="grid gap-4" style="align-content:start"><span class="chip">Why the lab exists</span><h2 class="h-sec">Every story about India <i>gets edited.</i></h2></div>
  <div class="grid gap-4 leading-relaxed text-muted" style="align-content:start;font-size:17px">
    <p>The unpaid invoice. The permission letter that sat on a desk for three months. The savings that paid the rent while the work got done. <span class="text-paper">That is the part we keep.</span></p>
    <p>The Other Details is the research lab of Zeroing, a community of homegrown Indian brands. It does two jobs. It traces every number we publish to the page it was first printed on. And it reviews the proof our brands share about how they make things. Only after that review can a practice on the shop page be marked Checked by Zeroing.</p>
    <p><a class="text-teal" href="https://www.instagram.com/theotherdetails/" target="_blank" rel="noopener">Follow @theotherdetails on Instagram</a></p>
  </div>
</section>"""

LEAD = """<section id="lead" class="glass lab-lead mt-20 grid gap-6 p-6 md:grid-cols-2">
  <div class="grid gap-4" style="align-content:start"><span class="chip chip-teal">Send us a detail</span><h2 class="h-sec">What detail of your work <i>never makes it into the story?</i></h2>
    <p class="text-muted">Your answer may become a lead for our research. We ask before we use anything you tell us.</p></div>
  <form class="lab-form" data-form="details" novalidate>
    <input class="hp" type="text" name="company_website" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label for="d-answer">Your answer</label><textarea id="d-answer" name="answer" required maxlength="1800" rows="5"></textarea>
    <div class="two"><div><label for="d-name">Your name</label><input id="d-name" name="name" required maxlength="120" autocomplete="name"></div>
    <div><label for="d-email">Email</label><input id="d-email" name="email" type="email" required autocomplete="email"></div></div>
    <label class="consent" for="d-consent"><input type="checkbox" id="d-consent" name="consent" required><span>I agree that Zeroing can store my answer as a research lead and contact me about it, as set out in the <a href="../legal.html#privacy">privacy notice</a>.</span></label>
    <div class="row"><button class="btn" type="submit">Send the detail</button><p class="status" role="status"></p></div>
  </form>
</section>
<style>
.lab-about{margin-top:96px;scroll-margin-top:96px}.lab-lead{scroll-margin-top:96px}@media(min-width:768px){.lab-lead{padding:40px;gap:40px}}
.lab-form{display:grid;gap:10px;align-content:start}
.lab-form label{font-size:13px;font-weight:600;color:inherit}
.lab-form input:not([type=checkbox]),.lab-form textarea{width:100%;box-sizing:border-box;min-height:48px;padding:12px 14px;border-radius:12px;border:1px solid hsla(0,0%,100%,.16);background:hsla(0,0%,100%,.04);color:inherit;font:inherit;font-size:15px}
.lab-form input:focus,.lab-form textarea:focus{outline:2px solid currentColor;outline-offset:2px}
.lab-form .two{display:grid;grid-template-columns:1fr 1fr;gap:12px}.lab-form .two>div{display:grid;gap:10px}
.lab-form .consent{display:flex;gap:10px;align-items:flex-start;font-weight:400;line-height:1.45;opacity:.85}
.lab-form .consent input{width:18px;height:18px;margin-top:2px;flex:none}
.lab-form .row{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin-top:6px}
.lab-form .status{font-size:14px;font-weight:600}
.lab-form .hp{position:absolute;left:-9999px;width:1px;height:1px;opacity:0}
.lab-form button[disabled]{opacity:.6}
@media (max-width:640px){.lab-form .two{grid-template-columns:1fr}}
</style>
<script>
document.querySelectorAll('form.lab-form').forEach(function(form){var st=form.querySelector('.status'),b=form.querySelector('button');
form.addEventListener('submit',function(e){e.preventDefault();var bad=[].find.call(form.elements,function(el){return el.willValidate&&!el.checkValidity()});
if(bad){st.textContent=bad.type==='checkbox'?'Tick the consent box so we can store your answer.':bad.type==='email'?'Enter an email address like name@example.com.':'Fill in every field.';bad.focus();return}
var d={form:'details'};new FormData(form).forEach(function(v,k){d[k]=v});d.consent=true;d.consent_text=form.querySelector('.consent').textContent.trim();
b.disabled=true;st.textContent='Sending.';fetch('/api/submit',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d)})
.then(function(r){return r.json().catch(function(){return{ok:false}})}).then(function(r){if(r.ok){form.reset();st.textContent='Thank you. Your answer is saved, and it may become a lead for our research.'}else{st.textContent=r.error||'That did not go through. Try again, or email zeroingindia@gmail.com.'}})
.catch(function(){st.textContent='That did not go through. Check your connection and try again.'}).then(function(){b.disabled=false})})});
</script>"""


FINDINGS = f"""<section id="findings" class="mt-20"><div class="grid gap-3.5"><span class="chip chip-teal">Findings</span><h2 class="h-sec">What our studies found. <i>Every number sourced.</i></h2><p class="max-w-[52ch] text-muted">From the lab's own research on roads, medicine and ethanol. Each figure is shown with the report it comes from.</p></div>
<div class="fd-grid"><article class="glass fd-card"><span class="chip">Roads</span><h3 class="font-head fd-h">Every three minutes</h3><ul class="fd-list"><li class="fd-row"><span class="fd-n">485</span><span class="fd-t">road deaths a day in India, about one every three minutes</span></li><li class="fd-row"><span class="fd-n">46%</span><span class="fd-t">of road deaths were two-wheeler riders</span></li><li class="fd-row"><span class="fd-n">2 in 3</span><span class="fd-t">people killed were aged 18 to 45</span></li><li class="fd-row"><span class="fd-n">~70%</span><span class="fd-t">of road deaths were linked to over-speeding; the deadliest hours are 6 pm to 9 pm</span></li></ul><p class="fd-src">Source: MoRTH, Road Accidents in India 2024, as reported by ThePrint and PolicyEdge</p><a class="fd-go" href="{YT}" target="_blank" rel="noopener">Watch the reels on YouTube &#8599;</a></article><article class="glass fd-card"><span class="chip">Medicine</span><h3 class="font-head fd-h">What is in the price</h3><ul class="fd-list"><li class="fd-row"><span class="fd-n">₹229 vs ₹18.70</span><span class="fd-t">for a strip of rosuvastatin 10 mg: branded against Jan Aushadhi</span></li><li class="fd-row"><span class="fd-n">82%</span><span class="fd-t">of the medicine market by value has no price ceiling; companies may raise MRP up to 10% a year</span></li><li class="fd-row"><span class="fd-n">43%</span><span class="fd-t">of health spending in India is still paid by families from their own pocket, down from 64% in 2013-14</span></li><li class="fd-row"><span class="fd-n">₹24,000 vs ₹1,100</span><span class="fd-t">typical out-of-pocket cost of a hospital stay: private against government</span></li></ul><p class="fd-src">Source: PMBI 2024 · Parliamentary Standing Committee, Aug 2026 · National Health Accounts 2022-23, NHSRC · NSS 80th round (2025)</p><a class="fd-go" href="{YT}" target="_blank" rel="noopener">Watch the reels on YouTube &#8599;</a></article><article class="glass fd-card"><span class="chip">Ethanol</span><h3 class="font-head fd-h">Cleaner fuel, at a cost</h3><ul class="fd-list"><li class="fd-row"><span class="fd-n">20 in 100</span><span class="fd-t">litres of petrol sold in India is now ethanol, made from crops</span></li><li class="fd-row"><span class="fd-n">1 to 6%</span><span class="fd-t">mileage lost on E20: about 1 to 2% in newer cars, up to 6% in older ones</span></li><li class="fd-row"><span class="fd-n">2,860 L</span><span class="fd-t">of water can go into one litre of ethanol made from sugar</span></li><li class="fd-row"><span class="fd-n">0 of 29</span><span class="fd-t">water samples tested in Zira, Punjab were fit to drink; officials did not prove the cause</span></li></ul><p class="fd-src">Source: PPAC 2025-26 · PIB, Jul 2026 · NITI Aayog ethanol roadmap · CPCB · CPCB and CGWB report to NGT, May 2023</p><a class="fd-go" href="{YT}" target="_blank" rel="noopener">Watch the reels on YouTube &#8599;</a></article></div>
<style>.fd-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:20px;margin-top:28px}}.fd-card{{padding:28px;display:grid;gap:14px;align-content:start}}.fd-h{{font-size:1.5rem;line-height:1.15;margin:0}}.fd-list{{list-style:none;margin:0;padding:0;display:grid;gap:14px}}.fd-row{{display:grid;gap:2px;border-top:1px solid hsla(0,0%,100%,.1);padding-top:12px}}.fd-n{{font-family:var(--font-head,inherit);font-weight:900;font-size:1.7rem;color:#ff5a5f;line-height:1.1}}.fd-t{{color:hsla(0,0%,100%,.78);font-size:.95rem;line-height:1.45}}.fd-src{{font-size:.78rem;color:hsla(0,0%,100%,.5);margin:6px 0 0;line-height:1.5}}.fd-go{{font-weight:600;font-size:.92rem;text-decoration:underline;text-underline-offset:3px}}</style>
</section>"""

REELS = """<section id="reels" class="mt-20"><div class="grid gap-3.5"><span class="chip chip-teal">Reels</span><h2 class="h-sec">New from the lab. <i>One minute each.</i></h2><p class="max-w-[52ch] text-muted">Roads, medicine and ethanol, each number with its source on screen. Watch them on our YouTube channel.</p></div>
<div class="tod-reels"><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/road-deaths.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Roads</span><span class="t">About 485 people die on India's roads every day.</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/medicine-part1.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Medicine 1/3</span><span class="t">A strip of cholesterol medicine for 229 rupees?</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/medicine-part2.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Medicine 2/3</span><span class="t">Who writes the MRP on your medicine strip?</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/medicine-part3.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Medicine 3/3</span><span class="t">What a typical stay in a private hospital costs.</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/ethanol-part1.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Ethanol 1/3</span><span class="t">It's not your car.</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/ethanol-part2.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Ethanol 2/3</span><span class="t">What a litre of ethanol leaves behind at the factory.</span></figcaption></figure><figure class="tod-reel"><a class="yt-reel" href="https://www.youtube.com/@zeroingnow" target="_blank" rel="noopener"><img src="media/ethanol-part3.jpg" alt="Watch on YouTube" loading="lazy"><span class="yt-play" aria-hidden="true"></span></a><figcaption><span class="chip">Ethanol 3/3</span><span class="t">Ethanol was meant to cut our oil bill.</span></figcaption></figure></div>
<style>.tod-reels{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px;margin-top:28px}
.tod-reel{margin:0;display:grid;gap:12px}.yt-reel{position:relative;display:block}.yt-reel img{display:block}.yt-play{position:absolute;left:50%;top:50%;width:58px;height:40px;margin:-20px 0 0 -29px;border-radius:12px;background:#FF0000}.yt-play::after{content:"";position:absolute;left:23px;top:12px;border-style:solid;border-width:8px 0 8px 14px;border-color:transparent transparent transparent #fff}.tod-reel img{width:100%;aspect-ratio:9/16;border-radius:18px;background:#000;border:1px solid hsla(0,0%,100%,.12);object-fit:cover}
.tod-reel figcaption{display:grid;gap:8px}.tod-reel .t{font-weight:600;line-height:1.35}
@media (max-width:640px){.tod-reels{grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}}</style>
</section>"""


def home_page(studies):
    mosaic = ('<div class="absolute inset-0 grid grid-cols-2 gap-1 md:grid-cols-[1.2fr_.8fr_1.2fr]" aria-hidden="true">'
              + '<img class="loop" src="media/tod-road.jpg" alt="">' + '<img class="loop" src="media/tod-medicine.jpg" alt="">' + '<img class="loop max-md:hidden" src="media/tod-farm.jpg" alt="">' + "</div>")
    ctas = '<div class="mt-7 flex flex-wrap gap-3"><a class="btn" href="data-centres.html">Start with Study 01</a><a class="btn btn-ghost" href="method.html">How we check data</a></div>'
    cards = ""
    for s in studies:
        cards += f"""<a class="glass group flex flex-col overflow-hidden no-underline transition hover:-translate-y-1 hover:border-teal/40" href="{s['slug']}.html">
      <div class="relative aspect-video overflow-hidden border-b border-edge">{loop(s['hero'], 'loop brightness-[.85]')}<span class="sticker bottom-4 left-4">{s['sticker']}</span></div>
      <div class="grid gap-3.5 p-6"><span class="chip chip-{s['accent']}">{s['chip']}</span><span class="font-head text-[26px] font-black leading-tight tracking-tight [&>i]:font-ital [&>i]:font-medium [&>i]:italic [&>i]:text-red">{s['question']}</span></div>
      <div class="border-t border-edge">{rows(s['card'])}</div>
      <span class="mt-auto border-t border-edge px-6 py-4 text-sm font-semibold text-teal">Read the study · {s['read']} →</span></a>"""
    main = hero(mosaic, "The research lab of Zeroing", "teal",
                "The other details. <i>Drawn so anyone can read them.</i>",
                "We open the reports behind the headlines, check where each number came from and how old it is, then draw it so it reads on your phone.", ctas, tall=True) + f"""
<div class="wrap pb-24">
  <div class="mt-20 grid gap-3.5"><span class="chip">Studies</span><h2 class="h-sec">Two questions, <i>answered with data.</i></h2></div>
  <div class="mt-10 grid gap-6 md:grid-cols-2">{cards}</div>
  <div class="mt-20 grid gap-3.5"><span class="chip chip-teal">Watch</span><h2 class="h-sec">Study 01 is also <i>a film for your phone.</i></h2></div>
  {reel_box("reel-cloud", "Reel · 2:13 · 9:16", "The cloud has <i>an address.</i>", "Real footage. Dot charts drawn to scale. Every source on screen, with captions and narration.")}
  """ + FINDINGS + REELS + ABOUT + LEAD + """
</div>"""
    return shell("The Other Details · The research lab of Zeroing", "The research lab of Zeroing: the numbers behind the news, traced to their sources and drawn so anyone can read them.", "home", main)


def method_page():
    rules = [("Trace to the origin", "Every figure goes back to the report that first published it, not the article that repeated it."),
             ("Check the date", "Older than about two years, or arithmetic that does not reconcile: labelled or replaced."),
             ("Ranges stay ranges", "Forecasts are dashed, estimates show their spread, \"more than\" keeps its open end."),
             ("One chart per job", "Squares for \"times\", unit grids for shares, lines for time, fans for forecasts, maps for place."),
             ("Fair and timeless", "No sides taken, no seasons named, nobody mocked. The data leads."),
             ("Credit the owners", "Data belongs to its original sources and owners. The Other Details only presents it.")]
    cards = "".join(f'<div class="glass p-6"><span class="font-head text-sm font-black tracking-widest text-teal">{i + 1:02d}</span><h3 class="mt-2.5 font-head text-2xl font-black tracking-tight">{h}</h3><p class="mt-2.5 text-muted">{p}</p></div>'
                    for i, (h, p) in enumerate(rules))
    main = f"""<section class="wrap pb-24 pt-14"><span class="chip chip-teal">How the lab works</span><h1 class="h-hero">Data can be wrong. <i>So we check it.</i></h1>
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
