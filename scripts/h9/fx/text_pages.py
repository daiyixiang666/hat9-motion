"""分屏读完一段话 Text Pages (小Lin说 / 回形针的长句字幕页；Apple keynote 的逐句高亮；Kinetic paragraph reveal):
a paragraph of 80–200+ glyphs is broken into sentences and grouped into as few pages as stay readable; each page
lifts in, the sentence being spoken lights up with a marker sweep while the rest wait in grey, read sentences
stay ink. A reading rail on the side fills page by page and a page counter ticks. Right-to-left scripts (Arabic,
Hebrew) flow from the right; traditional Chinese, emoji and mixed Latin are measured like any text.

Adapts: 1 sentence to ~15 sentences / ~400 glyphs; pages = as few as keep the type ≥ 4.4 vmin (16:9) / 5.2 vmin
(9:16); a translation line per page is optional. Sentence timing from "at" cues, else by length across the beat.
p: text (or pages: [..]) · title · translation (one string per page or one for all; "tr" is the beat transition key) · at · dir ("rtl" forced) · hl_style ("marker" | "color")
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit
from h9.core import esc

CSS = """
.fx .tp { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .tp .tp-k { position:absolute; font-family:var(--f-mono, monospace); font-weight:500; letter-spacing:.12em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.fx .tp .tp-k b { color:var(--accent); font-weight:700; margin-right:.6em; }
.fx .tp .tp-pg { position:absolute; font-family:var(--f-body); font-weight:700; line-height:1.55; color:var(--fg); word-break:normal; line-break:strict; }
.fx .tp .tp-pg.rtl { direction:rtl; text-align:right; }   /* Arabic / Hebrew glyphs fall back to the system font; a registry font can be added later */
.fx .tp .tp-s { opacity:.3;
  background-image:linear-gradient(var(--accent), var(--accent)); background-repeat:no-repeat; background-position:0 88%; background-size:0% 0.32em;
  -webkit-box-decoration-break:clone; box-decoration-break:clone; padding:0 .04em; }
.fx .tp .tp-pg.rtl .tp-s { background-position:100% 88%; }
.fx .tp .tp-tr { position:absolute; font-family:var(--f-body); font-weight:500; color:var(--muted); line-height:1.45; }
.fx .tp .tp-rail { position:absolute; width:.5vmin; background:color-mix(in srgb, var(--fg) 12%, transparent); border-radius:.25vmin; overflow:hidden; }
.fx .tp .tp-rail i { position:absolute; left:0; top:0; width:100%; height:100%; background:var(--accent); transform-origin:50% 0; transform:scaleY(0); }
.fx .tp .tp-n { position:absolute; font-family:var(--f-num, var(--f-mono)); font-weight:800; color:var(--fg); font-variant-numeric:tabular-nums; white-space:nowrap; }
.fx .tp .tp-n span { color:var(--muted); font-weight:500; }
"""


def _pages(sents, w, h, max_px, read_px, max_lines):
    """greedy: add sentences to a page while the page still fits at a readable size."""
    pages, cur = [], []
    for s in sents:
        trial = cur + [s]
        px, n = T2.fit_any("".join(trial), w, h, max_px, read_px * 0.98, max_lines=max_lines, lh=1.55)
        if cur and (px < read_px or n > max_lines):
            pages.append(cur); cur = [s]
        else:
            cur = trial
    if cur: pages.append(cur)
    return pages


def text_pages(X, cid, t, d, p):
    P = X.portrait
    if p.get("pages"):
        pages = [T2.sentences(fit.as_text(pg)) or [fit.as_text(pg)] for pg in fit.as_list(p["pages"])]
    else:
        sents = T2.sentences(fit.as_text(p.get("text") or p.get("paragraph") or "一段话。"))
        pages = None
    x, y, w, h = S.box(X, p)
    title = fit.as_text(p.get("title"))
    kpx = S.vm(X, 2.6)
    top = y + (kpx * 2.6 if title else 0)
    avail_h = h - (top - y) - S.vm(X, 4)
    tr = fit.as_list(p.get("translation") or p.get("trans"))
    if tr: avail_h *= 0.78
    rail_x = x
    tx = x + S.vm(X, 3.4)
    tw = w - S.vm(X, 3.4) - (0 if P else S.vm(X, 6))
    max_px, read_px = (S.vm(X, 7.6), S.vm(X, 5.2)) if P else (S.vm(X, 6.6), S.vm(X, 4.4))
    max_lines = 8 if P else 5
    if pages is None:
        pages = _pages(sents, tw, avail_h, max_px, read_px, max_lines)
    rtl = p.get("dir") == "rtl" or T2.is_rtl("".join(s for pg in pages for s in pg))
    if rtl:     # mirror: the rail sits on the right, where right-to-left reading starts
        tx = x + (0 if P else S.vm(X, 6))
        rail_x = tx + tw + S.vm(X, 2.9)
    # one size for every page: the smallest page size, so the type does not jump between pages
    px = min(T2.fit_any("".join(pg), tw, avail_h, max_px, read_px * 0.8, max_lines=max_lines, lh=1.55)[0] for pg in pages)
    # timing: one moment per sentence
    flat = [s for pg in pages for s in pg]
    n = len(flat)
    at = fit.as_list(p.get("at"))
    times = None
    if at and X.chars:
        try: times = [float(X.T(at[k], t)) for k in range(n)] if len(at) >= n else None
        except SystemExit: times = None
    if not times:
        lens = [max(4, len(fit.plain(s))) for s in flat]
        span = max(0.6, d - 0.55 - 0.5)
        acc, times = 0.0, []
        for L in lens:
            times.append(t + 0.45 + span * acc / sum(lens)); acc += L
    X.css("fx-tp", CSS)
    html = []
    if title:
        html.append(f'<div class="tp-k" style="left:{tx:.0f}px; top:{y:.0f}px; font-size:{kpx:.0f}px"><b>¶</b>{X.rich(title)}</div>')
    # the tallest page decides the vertical centring, so pages share one baseline grid
    heights = []
    for pg in pages:
        _, nl = T2.fit_any("".join(pg), tw, 1e6, px, px, max_lines=max_lines * 2, lh=1.55)
        heights.append(nl * px * 1.55)
    ph = max(heights)
    trh = 0
    if tr:
        trpx = min(S.vm(X, 3.4), px * 0.62)
        trh = trpx * 1.45 * 2 + S.vm(X, 2)
    py = top + max(0, (avail_h + (trh if tr else 0) - ph - trh) / 2)
    k = 0
    for pi, pg in enumerate(pages):
        spans = "".join(f'<span class="tp-s" data-k="{k + j}">{X.rich(s)}</span>' for j, s in enumerate(pg))
        k += len(pg)
        html.append(f'<div class="tp-pg{" rtl" if rtl else ""}" data-p="{pi}" style="left:{tx:.0f}px; top:{py:.0f}px; width:{tw:.0f}px; font-size:{px:.0f}px; opacity:0">{spans}</div>')
        if tr:
            line = tr[pi] if pi < len(tr) else (tr[0] if len(tr) == 1 and len(pages) == 1 else "")
            if line:
                html.append(f'<div class="tp-tr" data-p="{pi}" style="left:{tx:.0f}px; top:{py + ph + S.vm(X, 2):.0f}px; width:{tw:.0f}px; font-size:{trpx:.0f}px; opacity:0;{"text-align:right" if rtl else ""}">{X.rich(line)}</div>')
    html.append(f'<div class="tp-rail" style="left:{rail_x:.0f}px; top:{py:.0f}px; height:{ph:.0f}px"><i></i></div>')
    npx = S.vm(X, 3.0)
    if len(pages) > 1:
        nx = (x + w - npx * 3.2 if not rtl else x) if not P else (tx if not rtl else x + w - npx * 3.2)
        ny = (py + ph - npx) if not P else (py - npx * 1.9)
        html.append(f'<div class="tp-n" style="left:{nx:.0f}px; top:{ny:.0f}px; font-size:{npx:.0f}px">' +
                    "".join(f'<b data-p="{i}" style="position:absolute; left:0; top:0; opacity:0">{i + 1}<span> / {len(pages)}</span></b>' for i in range(len(pages))) + "</div>")
    _clip(X, cid, t, d, f'<div class="tp">{"".join(html)}</div>', p)
    s = f"#{cid} .tp"
    if title: X.tw(f'tl.from("{s} .tp-k", {{opacity:0, x:-24, duration:0.45, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .tp-rail", {{scaleY:0, transformOrigin:"50% 0", duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    # pages: each one owns the time from its first sentence to the next page's first sentence
    k = 0
    starts = []
    for pi, pg in enumerate(pages):
        starts.append(times[k]); k += len(pg)
    end = t + d
    for pi in range(len(pages)):
        a = max(t + 0.15, starts[pi] - 0.35)
        b = (starts[pi + 1] - 0.35) if pi + 1 < len(pages) else end
        sel = f'{s} [data-p="{pi}"]'
        X.tw(f'tl.fromTo("{s} .tp-pg[data-p=\'{pi}\']", {{opacity:0, y:{S.vm(X, 3):.0f}, filter:"blur(8px)"}}, '
             f'{{opacity:1, y:0, filter:"blur(0px)", duration:0.5, ease:"expo.out", immediateRender:false}}, {a:.3f});')
        if tr: X.tw(f'tl.fromTo("{s} .tp-tr[data-p=\'{pi}\']", {{opacity:0}}, {{opacity:1, duration:0.5, immediateRender:false}}, {a + 0.35:.3f});')
        if len(pages) > 1:
            X.tw(f'tl.set("{s} .tp-n b[data-p=\'{pi}\']", {{opacity:1}}, {a:.3f});')
            X.tw(f'tl.from("{s} .tp-n b[data-p=\'{pi}\']", {{yPercent:60, duration:0.35, ease:"back.out(2)"}}, {a:.3f});')
        rail_to = (pi + 1) / len(pages)
        X.tw(f'tl.to("{s} .tp-rail i", {{scaleY:{rail_to:.3f}, duration:{max(0.3, b - a - 0.1):.2f}, ease:"none"}}, {a:.3f});')
        if pi + 1 < len(pages):
            X.tw(f'tl.to("{s} .tp-pg[data-p=\'{pi}\']", {{opacity:0, y:-{S.vm(X, 3):.0f}, duration:0.3, ease:"power2.in"}}, {b:.3f});')
            if tr: X.tw(f'tl.to("{s} .tp-tr[data-p=\'{pi}\']", {{opacity:0, duration:0.25}}, {b:.3f});')
            if len(pages) > 1: X.tw(f'tl.set("{s} .tp-n b[data-p=\'{pi}\']", {{opacity:0}}, {b + 0.3:.3f});')
            X.sfx(b + 0.3, "paper")
    # sentences: the spoken one lights up, read ones stay ink
    for j, tj in enumerate(times):
        sel = f'{s} .tp-s[data-k=\'{j}\']'
        X.tw(f'tl.fromTo("{sel}", {{opacity:0.3, backgroundSize:"0% 0.32em"}}, {{opacity:1, backgroundSize:"100% 0.32em", duration:0.45, ease:"power2.out", immediateRender:false}}, {tj - 0.05:.3f});')
        nxt = times[j + 1] if j + 1 < len(times) else None
        if nxt is not None:
            X.tw(f'tl.to("{sel}", {{backgroundSize:"100% 0em", duration:0.3, ease:"power1.out"}}, {nxt - 0.05:.3f});')
    X.sfx(t + 0.1, "enter")


FX = {"text_pages": text_pages}
