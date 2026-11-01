"""多页文档快速翻阅 (riffle through a long document and stop on the page that matters): pages turn over on their
spine in perspective — slow, then a blur of pages, then slowing again — the page counter runs with them, the target page
settles, the camera moves in and the quoted passage is marked.

p: pdf (+ range [a, b]) or pages (images) · of (page count to show, e.g. the full document's when the PDF is an extract) · target (1-based page; omitted → the page that contains `quote`) · quote
   (PDF text to mark on the target) · hl ([x, y, w, h] % boxes on the target, for images / scans) · title · caption · flips (max pages
   actually turned, default 26)
Adapts: 2 to thousands of pages (turns are sampled from the pages before the target, the counter shows real numbers);
any page size; a quote of a few words to a paragraph; 16:9 document left + text right, 9:16 document on top. Needs PyMuPDF for PDFs.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def doc_flip(X, cid, t, d, p):
    rects = []
    if p.get("pdf"):
        total = D.pdf_count(X, p["pdf"])
        rg = p.get("range")
        lo, hi = (int(rg[0]), min(int(rg[1]), total)) if isinstance(rg, (list, tuple)) and len(rg) == 2 else (1, total)
        target = p.get("target")
        if not target and p.get("quote"): target, rects = D.pdf_find(X, p["pdf"], p["quote"])
        elif target and p.get("quote"): _, rects = D.pdf_find(X, p["pdf"], p["quote"], page=target)
        target = max(lo, min(int(target or hi), hi))
        k = int(p.get("flips", 26))
        span = list(range(lo, target))
        if len(span) > k: span = [span[round(i * (len(span) - 1) / (k - 1))] for i in range(k)]
        nums = span + [target]
        pages = D.pdf_pages(X, p["pdf"], nums, dpi=int(p.get("dpi", 80)))
        hi_page = D.pdf_pages(X, p["pdf"], [target], dpi=150)[0]
        pages[-1] = hi_page
    else:
        imgs, _ = D.page_list(X, p)
        if not imgs: raise SystemExit("doc_flip needs `pdf` or `pages`")
        total = len(imgs); target = max(1, min(int(p.get("target", total)), total))
        nums = list(range(1, target + 1)); pages = imgs[:target]
    if p.get("hl"):
        bx = p["hl"] if isinstance(p["hl"][0], (list, tuple)) else [p["hl"]]
        rects = [(b[0] / 100, b[1] / 100, (b[0] + b[2]) / 100, (b[1] + b[3]) / 100) for b in bx]
    n = len(pages)
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title, caption = fit.as_text(p.get("title")), fit.as_text(p.get("caption"))
    tw_ = bw * (0.95 if P else 0.36)
    tf = D.C.fitted(X, title, tw_, 170 if not P else 110, 58 if not P else 50, 26, max_lines=3) if title else None
    cf = D.C.fitted(X, caption, tw_, 130, 32, 20, max_lines=3) if caption else None
    tblock = ((tf.n * tf.px * 1.12 + 18) if tf else 0) + ((cf.n * cf.px * 1.3 + 8) if cf else 0) + 64
    par = pages[-1][1] / pages[-1][2] if pages[-1][2] else 0.77
    if P:
        aw, ah = bw, bh - tblock - 16
        ph = min(ah, aw * 0.62 / par); pw = ph * par
        ax, ay = x0 + (bw - pw) / 2 + pw * 0.18, y0 + (ah - ph) / 2
        tx, ty = x0, y0 + ah + 16
    else:
        aw = bw * 0.6; ah = bh
        ph = min(ah * 0.94, aw * 0.6 / par); pw = ph * par
        ax, ay = x0 + (aw - pw) / 2 + pw * 0.22, y0 + (ah - ph) / 2
        tx, ty = x0 + aw + 48, y0 + (bh - tblock) / 2 + 64
    sheets = "".join(f'<div class="df-p" data-k="{i}" style="z-index:{n - i}"><img src="{u}" alt=""><i class="df-sh"></i></div>' for i, (u, w, h) in enumerate(pages))
    marks = "".join(f'<i class="d2-mk df-mk" style="left:{r[0] * 100:.2f}%; top:{r[1] * 100:.2f}%; width:{(r[2] - r[0]) * 100:.2f}%; height:{(r[3] - r[1]) * 100:.2f}%"></i>' for r in rects)
    labels = "".join(f'<b class="df-n" data-k="{i}">{v}</b>' for i, v in enumerate(nums))
    X.used_text.update(title + caption + "第页共/ 0123456789p.")
    counter = f'<div class="df-cnt" style="left:{tx:.0f}px; top:{ty - 64:.0f}px">p. <span class="df-nw">{labels}</span> / {p.get("of", total)}</div>'
    head = f'<div class="d2-ttl df-ttl" style="left:{tx:.0f}px; top:{ty:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else ""
    cap = f'<div class="df-cap" style="left:{tx:.0f}px; top:{ty + ((tf.n * tf.px * 1.12 + 18) if tf else 0):.0f}px; width:{tw_:.0f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>' if cf else ""
    wx, wy, ww, wh = (x0, y0, bw, ah) if P else (x0, y0, aw, ah)       # the document window: the zoom never spills onto the text
    ax, ay = ax - wx, ay - wy
    book = (f'<div class="df-win" style="left:{wx:.0f}px; top:{wy:.0f}px; width:{ww:.0f}px; height:{wh:.0f}px"><div class="df-cam" style="left:0; top:0; width:{ww:.0f}px; height:{wh:.0f}px">'
            f'<div class="df-left" style="left:{ax - pw:.1f}px; top:{ay:.1f}px; width:{pw:.1f}px; height:{ph:.1f}px"></div>'
            f'<div class="df-stack" style="left:{ax:.1f}px; top:{ay:.1f}px; width:{pw:.1f}px; height:{ph:.1f}px">{sheets}<div class="df-mks" style="z-index:{n + 1}">{marks}</div></div></div></div>')
    X.css("fx-d2", D.CSS)
    X.css("fx-doc-flip", """
.df-win { position:absolute; overflow:hidden; }
.df-cam { position:absolute; transform-origin:0 0; }
.df-stack { position:absolute; perspective:2200px; }
.df-stack::before { content:""; position:absolute; inset:0; transform:translate(7px, 7px); background:#e9e5dc; box-shadow:0 20px 50px rgba(0,0,0,.3); }
.df-p { position:absolute; inset:0; transform-origin:0 50%; background:#fbfaf6; backface-visibility:hidden; box-shadow:0 1px 0 rgba(0,0,0,.08); }
.df-p img { width:100%; height:100%; display:block; }
.df-sh { position:absolute; inset:0; background:linear-gradient(90deg, rgba(0,0,0,.18), rgba(0,0,0,0) 30%); opacity:0; }
.df-left { position:absolute; background:#f3efe6; box-shadow:0 18px 44px rgba(0,0,0,.24); opacity:0; }
.df-mks { position:absolute; inset:0; pointer-events:none; mix-blend-mode:multiply; }
.df-cnt { position:absolute; font-family:var(--f-mono, monospace); font-size:30px; font-weight:700; color:var(--fg); }
.df-n { display:none; color:var(--accent); } .df-n[data-k="0"] { display:inline; }
.df-cap { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.3; }
""")
    _clip(X, cid, t, d, f'<div class="d2 df">{book}{counter}{head}{cap}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .df-stack", {{y:60, rotation:-3, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.sfx(t, "paper")
    if tf: X.tw(f'tl.from("{S} .df-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{S} .df-cnt", {{opacity:0, x:-14, duration:0.4}}, {t + 0.2:.3f});')
    m = n - 1
    t_start = t + 0.55
    zoom_budget = min(1.7, d * 0.36)
    t_end = max(t_start + 0.4, t + d - zoom_budget)
    flip_t = []
    if m > 0:
        X.tw(f'tl.to("{S} .df-left", {{opacity:1, duration:0.3}}, {t_start:.3f});')
        for i in range(m):
            u = (i + 1) / m
            e = (u * u * (3 - 2 * u))                        # smoothstep: slow start, rush, settle
            tt = t_start + (t_end - t_start) * e
            flip_t.append(tt)
            gap = (t_end - t_start) / m
            dur = max(0.16, min(0.5, gap * 2.2))
            X.tw(f'tl.to("{S} .df-p[data-k=\'{i}\']", {{rotationY:-178, duration:{dur:.2f}, ease:"power2.in"}}, {tt - dur:.3f});')
            X.tw(f'tl.to("{S} .df-p[data-k=\'{i}\'] .df-sh", {{opacity:1, duration:{dur:.2f}}}, {tt - dur:.3f});')
            X.tw(f'tl.set("{S} .df-p[data-k=\'{i}\']", {{opacity:0}}, {tt:.3f});')
            X.tw(f'tl.set("{S} .df-n[data-k=\'{i}\']", {{display:"none"}}, {tt:.3f});')
            X.tw(f'tl.set("{S} .df-n[data-k=\'{i + 1}\']", {{display:"inline"}}, {tt:.3f});')
            if i % 3 == 0 or i == m - 1: X.sfx(tt, "paper" if i == m - 1 else "click")
    land = (flip_t[-1] if flip_t else t_start) + 0.1
    if rects:
        ux0 = min(r[0] for r in rects); uy0 = min(r[1] for r in rects); ux1 = max(r[2] for r in rects); uy1 = max(r[3] for r in rects)
        zs = max(1.2, min(2.4, (pw * 0.9) / max((ux1 - ux0) * pw, 1), ph * 0.45 / max((uy1 - uy0) * ph, 1)))
        cxp, cyp = ax + (ux0 + ux1) / 2 * pw, ay + (uy0 + uy1) / 2 * ph
        fxp, fyp = (ww / 2, wh / 2)
        X.tw(f'tl.to("{S} .df-cam", {{scale:{zs:.3f}, x:{fxp - zs * cxp:.1f}, y:{fyp - zs * cyp:.1f}, duration:0.9, ease:"power3.inOut"}}, {land:.3f});')
        X.tw(f'tl.fromTo("{S} .df-mk", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"power2.inOut", stagger:0.25}}, {land + 0.7:.3f});')
        X.sfx(land + 0.7, "click")
    else:
        X.tw(f'tl.to("{S} .df-cam", {{scale:1.06, x:{-(ax + pw / 2) * 0.06:.1f}, y:{-(ay + ph / 2) * 0.06:.1f}, duration:{max(0.5, t + d - land):.2f}, ease:"power2.out"}}, {land:.3f});')
    if cf: X.tw(f'tl.from("{S} .df-cap", {{opacity:0, y:14, duration:0.5}}, {land:.3f});')


FX = {"doc_flip": doc_flip}
