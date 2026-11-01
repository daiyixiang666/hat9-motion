"""多个来源汇到一点 Converge (VideoHive 3D Earth Connections 3.4K, Infographic Maker 2.6K; the Sankey-ish
「several streams into one total」shot): source cards land, curves draw from each to a target, particles stream
along the curves, and the target total ticks up as each stream arrives.

Adapts: 2–8 sources (stacked left→right in 16:9, top→bottom in 9:16), labels from a glyph to a phrase (fitted),
any magnitudes (万 / 亿); curve thickness follows each source's share; the target sums the sources unless a
`total` is given (use it when the sources don't add up to the whole, e.g. "others" left out).
p: sources [[label, value], ...] · target (label) · total · unit · dec · title · note · mock
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")


def converge(X, cid, t, d, p):
    W.base(X)
    src = [(str(a), float(W.num(b) or 0)) for a, b in p["sources"]][:8]
    n = len(src)
    total = float(W.num(p.get("total")) or sum(v for _, v in src))
    div, suf = W.F.compact(max([total] + [v for _, v in src]))
    unit = suf + p.get("unit", "")
    dec = int(p.get("dec", W.dec_of([v / div for _, v in src] + [total / div])))
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx
    vmax = max(v for _, v in src) or 1
    cards, curves, dots = [], [], []
    if P:
        cols = 2 if n > 3 else n
        rows = -(-n // cols)
        cw = (x1 - x0 - 20 * (cols - 1)) / cols; ch = 118
        tw_, th_ = (x1 - x0) * 0.86, 230
        tx, ty = (x0 + x1) / 2 - tw_ / 2, y1 - th_
        for i, (lab, v) in enumerate(src):
            r, c = divmod(i, cols)
            x, y = x0 + c * (cw + 20), top + r * (ch + 18)
            cards.append((i, x, y, cw, ch))
        ends = lambda i: ((cards[i][1] + cards[i][3] / 2, cards[i][2] + cards[i][4]), ((x0 + x1) / 2 + (i - (n - 1) / 2) * 28, ty))
        ctrl = lambda a, b: ((a[0], a[1] + (b[1] - a[1]) * 0.55), (b[0], b[1] - (b[1] - a[1]) * 0.45))
    else:
        cw = min(520, (x1 - x0) * 0.36); gap = 16
        ch = min(130, (y1 - top - gap * (n - 1)) / n)
        oy = top + max(0, (y1 - top - (ch * n + gap * (n - 1))) / 2)
        tw_, th_ = (x1 - x0) * 0.34, 300
        tx, ty = x1 - tw_, top + (y1 - top) / 2 - th_ / 2
        for i, (lab, v) in enumerate(src):
            cards.append((i, x0, oy + i * (ch + gap), cw, ch))
        ends = lambda i: ((cards[i][1] + cards[i][3], cards[i][2] + cards[i][4] / 2), (tx, ty + th_ / 2 + (i - (n - 1) / 2) * 22))
        ctrl = lambda a, b: ((a[0] + (b[0] - a[0]) * 0.55, a[1]), (b[0] - (b[0] - a[0]) * 0.45, b[1]))
    html = []
    paths_pts = []
    for i, x, y, w, h in cards:
        lab, v = src[i]
        row = h < 100      # short cards (many sources): label and number share one line
        vs = min(40, h * 0.5) if row else min(40, h * 0.34)
        vw = W.F.em(f"{v / div:,.{dec}f}") * vs * 0.62 + W.F.em(unit) * vs * 0.5 + 16
        ls, ll = W.fit_px(X, lab, (w - 40 - vw) if row else (w - 40), h * (0.5 if row else 0.42), 34 if not P else 30, 16, 1)
        html.append(f'<div class="cvs{" row" if row else ""}" data-i="{i}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">'
                    f'<span style="font-size:{ls:.0f}px">{X.rich(ll[0])}</span><b class="w3k" style="font-size:{vs:.0f}px"><span class="n">0</span><small>{X.rich(unit)}</small></b></div>')
        a, b = ends(i); c1, c2 = ctrl(a, b)
        pts = W.bezier(a, c1, c2, b, 18); paths_pts.append(pts)
        sw = 3 + 14 * (v / vmax)
        curves.append(f'<path class="cvp" data-i="{i}" d="M{a[0]:.1f},{a[1]:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {b[0]:.1f},{b[1]:.1f}" pathLength="1" style="stroke-width:{sw:.1f}"/>')
        for k in range(3):
            dots.append(f'<i class="cvd" data-i="{i}" data-k="{k}"></i>')
    ts, tl_ = W.fit_px(X, p.get("target", "合计"), tw_ - 50, 90, 40, 22, 2)
    bigs = min(130, (tw_ - 50) / max(0.6, W.F.em(f"{total / div:,.{dec}f}{unit}") * 0.62))
    target = (f'<div class="cvt" style="left:{tx:.0f}px; top:{ty:.0f}px; width:{tw_:.0f}px; height:{th_:.0f}px">'
              f'<span style="font-size:{ts:.0f}px">{W.lines_html(X, tl_)}</span><b class="w3k" style="font-size:{bigs:.0f}px"><span class="n">0</span><small>{X.rich(unit)}</small></b></div>')
    X.css("fx-converge", """
.fx .cv .cvs { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:6px; padding:0 20px; border-radius:12px;
  background:var(--card); color:var(--card-fg); box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--fg) 12%, transparent); }
.fx .cv .cvs.row { flex-direction:row; align-items:center; justify-content:space-between; }
.fx .cv .cvs span { font-family:var(--f-body); font-weight:800; white-space:nowrap; } .fx .cv .cvs b { font-size:40px; color:var(--accent); white-space:nowrap; } .fx .cv .cvs b small { font-size:.5em; margin-left:.1em; color:var(--muted); }
.fx .cv .cvp { fill:none; stroke:color-mix(in srgb, var(--accent) 55%, transparent); stroke-linecap:round; }
.fx .cv .cvd { position:absolute; left:0; top:0; width:14px; height:14px; margin:-7px 0 0 -7px; border-radius:50%; background:var(--accent); box-shadow:0 0 12px var(--accent); opacity:0; }
.fx .cv .cvt { position:absolute; display:flex; flex-direction:column; justify-content:center; align-items:center; gap:10px; border-radius:18px; text-align:center;
  background:var(--card); color:var(--card-fg); box-shadow:inset 0 0 0 4px var(--accent), 0 18px 40px -20px rgba(0,0,0,.45); }
.fx .cv .cvt span { font-family:var(--f-display); font-weight:900; line-height:1.15; } .fx .cv .cvt span .fl { display:block; white-space:nowrap; }
.fx .cv .cvt b { color:var(--accent); } .fx .cv .cvt b small { font-size:.4em; margin-left:.1em; color:var(--card-fg); opacity:.8; }
""")
    svg = f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(curves)}</svg>'
    inner = f'<div class="w3 cv">{hh}{svg}{"".join(html)}{target}{"".join(dots)}{W.mock_tag(X, p, x1 - 70, y0)}</div>'
    X.used_text.update("0123456789.,")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .cvt", {{scale:0.85, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.2:.3f});')
    st = min(0.35, max(0.12, (d - 2.4) / max(n, 1) * 0.6))
    flow = 0.9
    run = 0.0
    for i, (lab, v) in enumerate(src):
        ti = t + 0.35 + i * st
        X.tw(f'tl.from("{s} .cvs[data-i=\'{i}\']", {{x:{0 if P else -40}, y:{-30 if P else 0}, opacity:0, duration:0.5, ease:"expo.out"}}, {ti:.3f});')
        W.count(X, f"{s} .cvs[data-i=\'{i}\'] .n", ti + 0.1, v / div, dur=0.6, dec=dec)
        X.tw(f'tl.fromTo("{s} .cvp[data-i=\'{i}\']", {{strokeDasharray:1, strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.7, ease:"power2.inOut"}}, {ti + 0.25:.3f});')
        reps = max(0, int((t + d - (ti + 0.6)) / flow) - 1)
        for k in range(3):
            W.travel(X, f"{s} .cvd[data-i=\'{i}\'][data-k=\'{k}\']", paths_pts[i], ti + 0.6 + k * flow / 3, flow, repeat=max(0, reps - 1))
        arrive = ti + 0.6 + flow
        prev = run; run += v
        W.count(X, f"{s} .cvt .n", arrive, (run if not p.get("total") else total * run / max(1e-9, sum(x for _, x in src))) / div, dur=0.35, dec=dec, start=prev / div)
        X.tw(f'tl.fromTo("{s} .cvt", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.1}}, {{scale:1, duration:0.25}}], immediateRender:false}}, {arrive:.3f});')
        X.sfx(arrive, "tick")
    X.sfx(t + 0.35 + n * st + 0.6 + flow, "hit")


FX = {"converge": converge}
