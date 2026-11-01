"""PPT 幻灯片翻页 (a deck paged through like presenter view): the current slide fills a screen, the thumbnail strip
tracks where we are; few slides push one by one, many slides riffle fast and slow down onto the one that matters,
which then gets a push-in (optionally onto a region of it).

p: slides (images) or pdf (+ range [a, b] | "all") · focus (1-based slide to land on; default last) · at (switch times) ·
   zoom ([x, y, w, h] % of the focus slide) · title · counter (true)
Adapts: 1–200 slides of any aspect (letterboxed on the screen's own ratio); ≤8 → a push per slide on its cue,
more → a riffle that eases out; the strip windows around the current slide; 16:9 strip below, 9:16 strip below a
narrower screen. PDFs need PyMuPDF.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def slides(X, cid, t, d, p):
    src = dict(p)
    if p.get("slides") and not p.get("pdf"): src["pages"] = p["slides"]
    pages, nums = D.page_list(X, src, default_n=200)
    if not pages: raise SystemExit("slides needs `slides` or `pdf`")
    n = len(pages)
    focus = max(1, min(int(p.get("focus", n)), n)) - 1
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title = fit.as_text(p.get("title"))
    tf = D.C.fitted(X, title, bw * 0.75, 80, 40, 22, max_lines=1) if title else None
    th = (tf.px * 1.2 + 16) if tf else 0
    strip_h = 0 if n == 1 else (bh * (0.16 if not P else 0.12))
    sar = pages[0][1] / pages[0][2] if pages[0][2] else 16 / 9
    sw = min(bw, (bh - th - strip_h - 24) * sar); sh = sw / sar
    sx, sy = x0 + (bw - sw) / 2, y0 + th + (bh - th - strip_h - 24 - sh) / 2
    slides_html = "".join(f'<div class="sl-s" data-k="{i}"><img src="{u}" alt=""></div>' for i, (u, w, h) in enumerate(pages))
    # strip: a window of up to 9 thumbs (16:9) / 6 (9:16) around wherever we are
    vis = min(n, 9 if not P else 6)
    tgap = 12
    tw = min((bw - tgap * (vis - 1)) / vis, (strip_h - 10) * sar) if n > 1 else 0
    tht = tw / sar if tw else 0
    strip_w = n * tw + (n - 1) * tgap
    view_w = vis * tw + (vis - 1) * tgap
    stx = x0 + (bw - view_w) / 2; sty = y0 + bh - strip_h + (strip_h - tht) / 2
    thumbs = "".join(f'<div class="sl-t" data-k="{i}" style="left:{i * (tw + tgap):.1f}px; width:{tw:.1f}px; height:{tht:.1f}px"><img src="{u}" alt=""></div>' for i, (u, w, h) in enumerate(pages))
    strip = (f'<div class="sl-strip" style="left:{stx:.1f}px; top:{sty:.1f}px; width:{view_w:.1f}px; height:{tht:.1f}px">'
             f'<div class="sl-rail" style="width:{strip_w:.1f}px">{thumbs}<i class="sl-cur" style="width:{tw:.1f}px; height:{tht:.1f}px"></i></div></div>') if n > 1 else ""
    cnt = f'<div class="d2-tag sl-cnt" style="right:{X.W - (sx + sw) + 14:.0f}px; top:{sy + 14:.0f}px"><span class="sl-nw">{"".join(f'<b class="sl-n" data-k="{i}">{i + 1}</b>' for i in range(n))}</span> / {n}</div>' if p.get("counter", True) and n > 1 else ""
    head = f'<div class="d2-ttl sl-ttl" style="left:{x0}px; top:{y0}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else ""
    zb = p.get("zoom")
    X.used_text.update(title + "0123456789/ ")
    X.css("fx-d2", D.CSS)
    X.css("fx-slides", """
.sl-scr { position:absolute; overflow:hidden; border-radius:10px; background:#0e0e0e; box-shadow:0 24px 70px rgba(0,0,0,.32), 0 0 0 1.5px color-mix(in srgb, var(--fg) 14%, transparent); }
.sl-cam { position:absolute; inset:0; transform-origin:0 0; }
.sl-s { position:absolute; inset:0; opacity:0; }
.sl-s img { width:100%; height:100%; object-fit:contain; display:block; background:#0e0e0e; }
.sl-strip { position:absolute; overflow:hidden; }
.sl-rail { position:absolute; left:0; top:0; height:100%; }
.sl-t { position:absolute; top:0; border-radius:6px; overflow:hidden; opacity:.45; box-shadow:0 0 0 1px color-mix(in srgb, var(--fg) 18%, transparent); }
.sl-t img { width:100%; height:100%; object-fit:cover; display:block; }
.sl-n { display:none; font-weight:700; } .sl-n[data-k="0"] { display:inline; }
.sl-cur { position:absolute; left:0; top:0; border-radius:6px; box-shadow:0 0 0 3px var(--accent); pointer-events:none; }
""")
    _clip(X, cid, t, d, f'<div class="d2 sl">{head}<div class="sl-scr" style="left:{sx:.1f}px; top:{sy:.1f}px; width:{sw:.1f}px; height:{sh:.1f}px"><div class="sl-cam">{slides_html}</div></div>{strip}{cnt}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .sl-scr", {{y:40, opacity:0, scale:0.97, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    if strip: X.tw(f'tl.from("{S} .sl-t", {{y:24, opacity:0, duration:0.4, ease:"power3.out", stagger:{min(0.04, 0.6 / n):.3f}}}, {t + 0.15:.3f});')
    if tf: X.tw(f'tl.from("{S} .sl-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.set("{S} .sl-s[data-k=\'0\']", {{opacity:1}}, {t:.3f});')
    seq = list(range(0, focus + 1)) if focus > 0 else [0]
    tz_budget = min(1.4, d * 0.3)
    if len(seq) <= 8:
        sw_times = D.times(X, p, t, d, len(seq), key="at", lead=0.35, tail=tz_budget)
        for j, k in enumerate(seq[1:], 1):
            tt = sw_times[j]
            X.tw(f'tl.fromTo("{S} .sl-s[data-k=\'{k}\']", {{opacity:1, xPercent:100}}, {{xPercent:0, duration:0.55, ease:"expo.inOut"}}, {tt:.3f});')
            X.tw(f'tl.to("{S} .sl-s[data-k=\'{seq[j - 1]}\']", {{xPercent:-35, opacity:0, duration:0.55, ease:"expo.inOut"}}, {tt:.3f});')
            X.sfx(tt, "whoosh_soft")
        land = sw_times[-1] + 0.55
    else:
        # riffle: intervals grow geometrically, so it rushes then settles onto the focus slide
        start, end = t + 0.45, t + d - tz_budget
        m = len(seq) - 1
        w = [1.12 ** i for i in range(m)]; sc = (end - start) / sum(w)
        tt = start
        for j in range(1, m + 1):
            tt += w[j - 1] * sc
            X.tw(f'tl.set("{S} .sl-s[data-k=\'{seq[j]}\']", {{opacity:1}}, {tt:.3f});')
            X.tw(f'tl.set("{S} .sl-s[data-k=\'{seq[j - 1]}\']", {{opacity:0}}, {tt:.3f});')
            if j % 3 == 0 or j == m: X.sfx(tt, "click")
        land = tt
    # counter + strip follow the slide shown
    if strip or cnt:
        times = []
        if len(seq) <= 8: times = [(k, (sw_times[j] if j else t)) for j, k in enumerate(seq)]
        else:
            tt = t + 0.45; times = [(0, t)]
            for j in range(1, len(seq)): tt += 1.12 ** (j - 1) * sc; times.append((seq[j], tt))
        prev = 0
        for k, tt in times:
            if cnt and k != prev:
                X.tw(f'tl.set("{S} .sl-n[data-k=\'{prev}\']", {{display:"none"}}, {tt:.3f});')
                X.tw(f'tl.set("{S} .sl-n[data-k=\'{k}\']", {{display:"inline"}}, {tt:.3f});')
                prev = k
            if strip:
                off = min(max(0, (k - vis // 2) * (tw + tgap)), max(0, strip_w - view_w))
                X.tw(f'tl.set("{S} .sl-cur", {{x:{k * (tw + tgap):.1f}}}, {tt:.3f});')
                X.tw(f'tl.set("{S} .sl-rail", {{x:{-off:.1f}}}, {tt:.3f});')
    # land: push into the focus slide (or a region of it)
    if zb:
        zs = max(1.15, min(2.6, 0.9 / max(zb[2] / 100, zb[3] / 100)))
        cxp, cyp = (zb[0] + zb[2] / 2) / 100 * sw, (zb[1] + zb[3] / 2) / 100 * sh
        tx = min(0, max(sw - zs * sw, sw / 2 - zs * cxp)); ty = min(0, max(sh - zs * sh, sh / 2 - zs * cyp))
    else:
        zs, tx, ty = 1.08, -sw * 0.04, -sh * 0.04
    X.tw(f'tl.to("{S} .sl-cam", {{scale:{zs:.3f}, x:{tx:.1f}, y:{ty:.1f}, duration:{max(0.5, min(1.0, t + d - land - 0.1)):.2f}, ease:"power3.inOut"}}, {land + 0.05:.3f});')


FX = {"slides": slides}
