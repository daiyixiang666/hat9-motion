"""漏斗 Funnel (VideoHive Infographic Maker 2.6K; Envato「Infographics」packs): stages drop in from the top as
trapezoid bands whose widths follow the values, numbers count, the drop between stages reads out as a percentage
chip on the side; one stage can be singled out.

Adapts: 2–8 stages (band height and type from the count), any magnitudes (万 / 亿 automatically), labels from a word
to a sentence (fitted, 2 lines), two ways of reading the percentages: `mode: "conv"` (each stage vs the one before,
a real conversion funnel) or `mode: "share"` (each stage as a share of the first — for nested groups that are
not a strict pipeline). Widths are value-proportional with a floor so the last band stays readable (`floor`).
p: stages [[label, value], ...] · unit · mode · hl (index) · floor (0–0.6) · title · note · mock
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


def funnel(X, cid, t, d, p):
    W.base(X)
    st = [(str(a), float(W.num(b))) for a, b in p["stages"]][:8]
    n = len(st)
    mode = p.get("mode", "conv")
    hl = int(p.get("hl", -1))
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    P = X.portrait
    top = y0 + hhpx + 10
    vmax = max(v for _, v in st) or 1

    def fmt_of(v):
        """each stage in its own magnitude (2.0亿 · 6.4万 · 90), so a tiny last stage still reads as a real number."""
        dv, sv = W.F.compact(abs(v))
        if "dec" in p: dc = int(p["dec"])
        elif dv == 1: dc = W.dec_of([v])
        else: dc = 0 if v / dv >= 100 else 1 if v / dv >= 10 else 2
        return dv, sv + p.get("unit", ""), dc
    fmts = [fmt_of(v) for _, v in st]
    floor = float(p.get("floor", 0.22))
    # geometry: funnel on the left (16:9) or full width (9:16); labels to the right
    if P: fx0, fx1, lab_x = x0, x0 + (x1 - x0) * 0.74, None
    else: fx0, fx1, lab_x = x0, x0 + (x1 - x0) * 0.56, x0 + (x1 - x0) * 0.6
    fw = fx1 - fx0; cx = (fx0 + fx1) / 2
    gap = 10
    bh = min(230 if P else 150, (y1 - top - gap * (n - 1)) / n)
    total_h = bh * n + gap * (n - 1)
    top += max(0, (y1 - top - total_h) / 2)
    widths = [fw * (floor + (1 - floor) * (v / vmax)) for _, v in st]
    bands, labels, chips = [], [], []
    for i, (lab, v) in enumerate(st):
        yt = top + i * (bh + gap); yb = yt + bh
        wt = widths[i]; wb = widths[i + 1] if i + 1 < n else widths[i] * 0.86
        pts = f"{cx - wt / 2:.1f},{yt:.1f} {cx + wt / 2:.1f},{yt:.1f} {cx + wb / 2:.1f},{yb:.1f} {cx - wb / 2:.1f},{yb:.1f}"
        shade = (0.88 - 0.55 * i / max(1, n - 1))
        col = "var(--accent)" if i == hl else f"color-mix(in srgb, var(--fg) {shade * 100:.0f}%, var(--bg))"
        bands.append(f'<polygon class="fnb" data-i="{i}" points="{pts}" style="fill:{col}"/>')
        div, unit, dec = fmts[i]
        vs = min(bh * 0.46, 64)
        vtxt = f"{v / div:,.{dec}f}{unit}"
        inside_ok = wb > W.F.em(vtxt) * vs * 0.7 + 30
        val = f'<span class="n">0</span><small>{X.rich(unit)}</small>'
        if P:
            vp = min(vs, 54)
            ls, ll = W.fit_px(X, lab, (wt + wb) / 2 * 0.9, bh * 0.36, 30, 18, 1)
            if max(W.F.em(vtxt) * vp * 0.66, W.F.em(ll[0]) * ls) + 24 <= (wt + wb) / 2 * 0.92:
                labels.append(f'<div class="fnin" data-i="{i}" style="left:{cx - wt / 2:.1f}px; width:{wt:.1f}px; top:{yt:.1f}px; height:{bh:.1f}px">'
                              f'<b class="w3k" style="font-size:{vp:.0f}px">{val}</b><span style="font-size:{ls:.0f}px">{X.rich(ll[0])}</span></div>')
            else:   # band too narrow: value + label sit beside it, inside the funnel column
                ox = cx + max(wt, wb) / 2 + 12; avail = fx1 - ox - 4
                vp = min(vp, bh * 0.42, 40, avail / max(1, W.F.em(vtxt) * 0.66))
                ls, ll = W.fit_px(X, lab, avail, bh * 0.4, 26, 16, 1)
                labels.append(f'<div class="fnin out" data-i="{i}" style="left:{ox:.1f}px; top:{yt:.1f}px; height:{bh:.1f}px">'
                              f'<b class="w3k" style="font-size:{vp:.0f}px">{val}</b><span style="font-size:{ls:.0f}px">{X.rich(ll[0])}</span></div>')
        else:
            ls, ll = W.fit_px(X, lab, (x1 - lab_x) * 0.62, bh * 0.8, 34, 20, 2)
            labels.append(f'<div class="fnlab" data-i="{i}" style="left:{lab_x:.0f}px; top:{yt + bh / 2:.1f}px; font-size:{ls:.0f}px">{W.lines_html(X, ll)}</div>')
            labels.append(f'<div class="fnin" data-i="{i}" style="left:{cx - wt / 2:.1f}px; width:{wt:.1f}px; top:{yt:.1f}px; height:{bh:.1f}px">'
                          f'<b class="w3k" style="font-size:{vs:.0f}px">{val}</b></div>' if inside_ok else
                          f'<div class="fnin out" data-i="{i}" style="left:{cx + wt / 2 + 10:.1f}px; top:{yt:.1f}px; height:{bh:.1f}px"><b class="w3k" style="font-size:{vs * 0.8:.0f}px">{val}</b></div>')
        if i > 0:
            base = st[i - 1][1] if mode == "conv" else st[0][1]
            pc = v / base * 100 if base else 0
            txt = (f"{pc:.1f}%".replace(".0%", "%")) if pc >= 1 or pc == 0 else f"{pc:.2g}%"
            cap = p.get("pct_label", "转化" if mode == "conv" else "占")
            chip_x = fx1 + 10
            chip_y = yt - gap / 2 - 18
            chips.append(f'<div class="fnc" data-i="{i}" style="left:{chip_x:.0f}px; top:{chip_y:.1f}px"><i></i>{X.rich(cap)} <b>{txt}</b></div>')
    X.css("fx-funnel", """
.fx .fn .fnb { stroke:var(--bg); stroke-width:2; }
.fx .fn .fnin { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:4px; color:var(--bg); text-align:center; }
.fx .fn .fnin.out { align-items:flex-start; color:var(--fg); }
.fx .fn .fnin b small { font-size:.45em; margin-left:.12em; opacity:.8; }
.fx .fn .fnin > span { font-family:var(--f-body); font-weight:700; white-space:nowrap; }
.fx .fn .fnlab { position:absolute; transform:translateY(-50%); font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.15; }
.fx .fn .fnlab .fl { display:block; white-space:nowrap; }
.fx .fn .fnc { position:absolute; display:flex; align-items:center; gap:8px; font:600 20px var(--f-body); color:var(--muted); white-space:nowrap; }
.fx .fn .fnc i { width:10px; height:10px; border-right:3px solid var(--muted); border-bottom:3px solid var(--muted); transform:rotate(45deg); margin-top:-6px; }
.fx .fn .fnc b { font:800 26px var(--f-num, var(--f-display)); color:var(--accent); }
""")
    svg = f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(bands)}</svg>'
    inner = f'<div class="w3 fn">{hh}{svg}{"".join(labels)}{"".join(chips)}{W.mock_tag(X, p, x1 - 70, y0)}</div>'
    X.used_text.update("0123456789.,%" + "".join(f[1] for f in fmts))
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    stp = min(0.45, max(0.15, (d - 1.8) / max(n, 1)))
    for i, (lab, v) in enumerate(st):
        ti = t + 0.3 + i * stp
        X.tw(f'tl.from("{s} .fnb[data-i=\'{i}\']", {{scaleX:0, opacity:0, transformOrigin:"50% 50%", duration:0.55, ease:"expo.out"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .fnin[data-i=\'{i}\'], {s} .fnlab[data-i=\'{i}\']", {{opacity:0, y:12, duration:0.4}}, {ti + 0.15:.3f});')
        W.count(X, f"{s} .fnin[data-i=\'{i}\'] .n", ti + 0.1, v / fmts[i][0], dur=0.7, dec=fmts[i][2])
        if f'class="fnc" data-i="{i}"' in "".join(chips):
            X.tw(f'tl.from("{s} .fnc[data-i=\'{i}\']", {{x:-16, opacity:0, duration:0.4, ease:"back.out(2)"}}, {ti + 0.3:.3f});')
        X.sfx(ti, "tick")
    if 0 <= hl < n:
        th = t + 0.3 + n * stp + 0.2
        X.tw(f'tl.fromTo("{s} .fnb[data-i=\'{hl}\']", {{scale:1}}, {{keyframes:[{{scale:1.05, duration:0.12}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], transformOrigin:"50% 50%", immediateRender:false}}, {th:.3f});')
        X.sfx(th, "hit")


FX = {"funnel": funnel}
