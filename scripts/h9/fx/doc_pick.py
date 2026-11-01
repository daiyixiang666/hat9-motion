"""从一叠文件里抽出一页 (the one page that matters, pulled from the pile): a loose stack of pages lands, one page
slides out from the middle of it, turns square to the camera, comes to the front enlarged, and its passage gets marked
while the rest of the pile sinks back.

p: pages (images) or pdf (+ range [a, b] | list of page numbers) · pick (1-based; default the middle) · quote (PDF text to
   mark on the picked page) · hl ([x, y, w, h] %) · tag (label on the picked page, e.g. "第 8 页"; default "第 N 页" for PDFs) · title · caption
Adapts: 2–12 pages shown (more are sampled), mixed sizes; the pick can be anywhere in the pile; 16:9 pile left / page centre-right,
9:16 pile above / page below its own title. PDFs need PyMuPDF.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def doc_pick(X, cid, t, d, p):
    pages, nums = D.page_list(X, p, default_n=8)
    if len(pages) > 12:
        idx = [round(i * (len(pages) - 1) / 11) for i in range(12)]
        pages = [pages[i] for i in idx]; nums = [nums[i] for i in idx]
    n = len(pages)
    if n == 0: raise SystemExit("doc_pick needs `pages` or `pdf`")
    pk = max(1, min(int(p.get("pick", (n + 1) // 2)), n)) - 1
    rects = []
    if p.get("pdf") and p.get("quote"): _, rects = D.pdf_find(X, p["pdf"], p["quote"], page=nums[pk])
    if p.get("hl"):
        bx = p["hl"] if isinstance(p["hl"][0], (list, tuple)) else [p["hl"]]
        rects = [(b[0] / 100, b[1] / 100, (b[0] + b[2]) / 100, (b[1] + b[3]) / 100) for b in bx]
    if p.get("pdf"): pages[pk] = D.pdf_pages(X, p["pdf"], [nums[pk]], dpi=150)[0]
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title, caption = fit.as_text(p.get("title")), fit.as_text(p.get("caption"))
    tf = D.C.fitted(X, title, bw * (0.95 if P else 0.3), 150 if not P else 100, 52 if not P else 48, 24, max_lines=3) if title else None
    cf = D.C.fitted(X, caption, bw * (0.95 if P else 0.3), 120, 30, 20, max_lines=3) if caption else None
    par = pages[pk][1] / pages[pk][2] if pages[pk][2] else 0.77
    r = X.rand
    if P:
        th = ((tf.n * tf.px * 1.12 + 16) if tf else 0) + ((cf.n * cf.px * 1.3 + 8) if cf else 0)
        sh = (bh - th) * 0.42; sw = sh * par
        scx, scy = x0 + bw * 0.5, y0 + sh * 0.6
        fh = (bh - th) * 0.62; fw = min(bw * 0.86, fh * par); fh = fw / par
        fcx, fcy = x0 + bw / 2, y1 - th - fh / 2 - 34
        tx, ty = x0, y1 - th + 6
    else:
        sh = bh * 0.62; sw = sh * par
        scx, scy = x0 + bw * 0.2, y0 + bh * 0.52
        fh = bh * 0.92; fw = min(bw * 0.34, fh * par); fh = fw / par
        fcx, fcy = x0 + bw * 0.55, y0 + bh / 2
        tblock = ((tf.n * tf.px * 1.12 + 16) if tf else 0) + ((cf.n * cf.px * 1.3) if cf else 0)
        tx, ty = x0 + bw * 0.74, y0 + (bh - tblock) / 2
    els = []; offs = []; his = []
    for i, (u, w, h) in enumerate(pages):
        rot = r.uniform(-9, 9); ox = r.uniform(-1, 1) * sw * 0.08; oy = r.uniform(-1, 1) * sh * 0.05
        offs.append((ox, oy))
        par_i = (w / h) if h else par
        wi = min(sh * par_i, sh * 1.45); hi = wi / par_i        # wide pages stay in the pile instead of spanning the frame
        his.append(hi)
        marks = "".join(f'<i class="d2-mk dk-mk" style="left:{q[0] * 100:.2f}%; top:{q[1] * 100:.2f}%; width:{(q[2] - q[0]) * 100:.2f}%; height:{(q[3] - q[1]) * 100:.2f}%"></i>' for q in rects) if i == pk else ""
        els.append(f'<div class="d2-sheet dk-p" data-k="{i}" style="left:{scx - wi / 2 + ox:.1f}px; top:{scy - hi / 2 + oy:.1f}px; width:{wi:.1f}px; height:{hi:.1f}px; z-index:{n - i}; --r:{rot:.1f}deg"><img src="{u}" alt="">{marks}</div>')
    s_up = fh / his[pk]
    lab = p.get("tag") or (f"第 {nums[pk]} 页" if p.get("pdf") else "")
    X.used_text.update(lab + title + caption)
    tag = f'<div class="d2-tag dk-tag" style="left:{fcx - fw / 2:.0f}px; top:{fcy - fh / 2 - 48:.0f}px; z-index:{n + 6}">{X.rich(lab)}</div>' if lab else ""
    head = f'<div class="d2-ttl dk-ttl" style="left:{tx:.0f}px; top:{ty:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else ""
    cap = f'<div class="dk-cap" style="left:{tx:.0f}px; top:{ty + ((tf.n * tf.px * 1.12 + 16) if tf else 0):.0f}px; width:{bw * (0.95 if P else 0.26):.0f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>' if cf else ""
    X.css("fx-d2", D.CSS)
    X.css("fx-doc-pick", """
.dk-p { transform:rotate(var(--r)); }
.dk-cap { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.3; }
.dk-tag { opacity:0; }
""")
    _clip(X, cid, t, d, f'<div class="d2 dk">{"".join(els)}{tag}{head}{cap}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .dk-p", {{y:-120, opacity:0, duration:0.45, ease:"power3.out", stagger:{{each:0.05, from:"end"}}}}, {t:.3f});')
    X.sfx(t + 0.1, "paper")
    if tf: X.tw(f'tl.from("{S} .dk-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t + 0.15:.3f});')
    tp = t + max(0.9, min(1.4, d * 0.3))
    sel = f"{S} .dk-p[data-k='{pk}']"
    side = sw * 0.9
    # out of the pile sideways (still under the pages above it), then over everything to the front
    X.tw(f'tl.to("{sel}", {{x:{side:.0f}, rotation:2, duration:0.45, ease:"power2.out"}}, {tp:.3f});')
    X.tw(f'tl.set("{sel}", {{zIndex:{n + 5}}}, {tp + 0.45:.3f});')
    X.tw(f'tl.to("{sel}", {{x:{fcx - scx - offs[pk][0]:.1f}, y:{fcy - scy - offs[pk][1]:.1f}, rotation:0, scale:{s_up:.3f}, duration:0.75, ease:"expo.inOut"}}, {tp + 0.45:.3f});')
    X.tw(f'tl.to("{S} .dk-p:not([data-k=\'{pk}\'])", {{y:"+=40", filter:"brightness(.75)", duration:0.6, ease:"power2.out"}}, {tp + 0.4:.3f});')
    X.sfx(tp, "whoosh_soft")
    if lab: X.tw(f'tl.to("{S} .dk-tag", {{opacity:1, duration:0.3}}, {tp + 1.1:.3f});')
    if rects:
        X.tw(f'tl.fromTo("{sel} .dk-mk", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"power2.inOut", stagger:0.25}}, {tp + 1.3:.3f});')
        X.sfx(tp + 1.3, "click")
    if cf: X.tw(f'tl.from("{S} .dk-cap", {{opacity:0, y:14, duration:0.5}}, {tp + 0.9:.3f});')
    hold = tp + 1.6
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{sel}", {{scale:{s_up * 1.02:.3f}, duration:{t + d - hold:.2f}, ease:"none"}}, {hold:.3f});')


FX = {"doc_pick": doc_pick}
