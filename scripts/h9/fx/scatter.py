"""散点 / 气泡图 Scatter & bubble (VideoHive Infographic Maker 2.6K; Mapal「Animate Infographics Like VOX」34.6 万播放):
axes draw from the origin, gridlines fade up, the points drop onto the plane one by one (bubbles grow to their
size), labels slide out beside them without colliding, then one point is singled out with a ring and a note.

Adapts: 2–60 points (labels shown for up to 14, the rest as dots unless `labels: "all"`), linear or log axes
(`log: "x" | "y" | "xy"`), huge numbers on the axes in 万 / 亿, optional bubble size (3rd value) and group
(4th value, up to 4 colours with a legend), optional quadrant lines (`quad: true` = medians, or [x, y]).
p: points [[label, x, y, size?, group?], ...] · xlab · ylab · xunit · yunit · size_lab · hl (label or index)
   · hl_note · log · quad · title · note · mock · labels
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
GC = ["color-mix(in srgb, var(--fg) 62%, var(--bg))", "var(--accent)", "color-mix(in srgb, var(--accent) 45%, var(--fg))", "color-mix(in srgb, var(--fg) 35%, var(--bg))"]


def scatter(X, cid, t, d, p):
    W.base(X)
    pts = []
    for q in p["points"]:
        q = list(q)
        pts.append({"lab": str(q[0]), "x": float(W.num(q[1])), "y": float(W.num(q[2])),
                    "s": float(W.num(q[3])) if len(q) > 3 and q[3] is not None else None, "g": q[4] if len(q) > 4 else None})
    n = len(pts)
    logx, logy = "x" in str(p.get("log", "")), "y" in str(p.get("log", ""))
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    P = X.portrait
    # plot area (leave room for axis labels / legend)
    px0, py0, px1, py1 = x0 + (90 if not P else 80), y0 + hhpx + 10, x1 - (40 if not P else 10), y1 - (70 if not P else 120)
    xs, ys = [q["x"] for q in pts], [q["y"] for q in pts]
    def rng(v, lg):
        if lg:
            lo, hi = math.log10(max(min(v), 1e-9)), math.log10(max(v))
            return math.floor(lo), math.ceil(hi)
        lo, hi = min(0.0, min(v)), max(v)
        tk = W.nice_ticks(lo, hi * 1.08, 5)
        return tk[0], tk[-1]
    xl, xh = rng(xs, logx); yl, yh = rng(ys, logy)
    def mx(v): return px0 + ((math.log10(v) if logx else v) - xl) / ((xh - xl) or 1) * (px1 - px0)
    def my(v): return py1 - ((math.log10(v) if logy else v) - yl) / ((yh - yl) or 1) * (py1 - py0)
    xdiv, xsuf = W.F.compact(max(abs(v) for v in xs)); ydiv, ysuf = W.F.compact(max(abs(v) for v in ys))
    def decades(lo, hi, most):
        step = max(1, math.ceil((hi - lo) / most))
        return [10 ** k for k in range(int(lo), int(hi) + 1, step)]
    xt = decades(xl, xh, 4 if P else 7) if logx else W.nice_ticks(xl, xh, 5)
    yt = decades(yl, yh, 7) if logy else W.nice_ticks(yl, yh, 5)
    rmax = 58 if not P else 46
    smax = max((q["s"] for q in pts if q["s"]), default=None)
    groups = []
    for q in pts:
        if q["g"] is not None and q["g"] not in groups: groups.append(q["g"])
    hl = p.get("hl")
    hli = next((i for i, q in enumerate(pts) if q["lab"] == str(hl)), None) if isinstance(hl, str) else (int(hl) if hl is not None else None)
    show_lab = n <= 14 or p.get("labels") == "all"
    els, labs = [], []
    for i, q in enumerate(pts):
        cx, cy = mx(q["x"]), my(q["y"])
        r = (rmax * math.sqrt(q["s"] / smax)) if (smax and q["s"]) else (13 if n <= 20 else 8)
        col = GC[groups.index(q["g"]) % 4] if q["g"] is not None else ("var(--accent)" if i == hli else GC[0])
        q.update(cx=cx, cy=cy, r=r)
        els.append(f'<i class="scp{" hl" if i == hli else ""}" data-i="{i}" style="left:{cx - r:.1f}px; top:{cy - r:.1f}px; width:{2 * r:.1f}px; height:{2 * r:.1f}px; background:{col}"></i>')
        if show_lab or i == hli:
            fs = 30 if n <= 6 else 26 if n <= 12 else 22
            w = W.F.em(q["lab"]) * fs + 8
            right = cx + r + 12 + w < x1
            labs.append({"i": i, "y": cy, "h": fs * 1.25, "x": cx, "w": w, "fs": fs, "right": right, "r": r})
    W.place_labels(labs, 4)
    for L in labs:
        q = pts[L["i"]]
        lx = (q["cx"] + L["r"] + 12) if L["right"] else (q["cx"] - L["r"] - 12 - L["w"])
        els.append(f'<div class="w3lab scl{" hl" if L["i"] == hli else ""}" data-i="{L["i"]}" style="left:{lx:.1f}px; top:{L["y"] - L["h"] / 2:.1f}px; font-size:{L["fs"]}px">{X.rich(q["lab"])}</div>')
    # axes + grid
    ax = [f'<i class="scax x" style="left:{px0}px; top:{py1}px; width:{px1 - px0}px"></i>', f'<i class="scax y" style="left:{px0}px; top:{py0}px; height:{py1 - py0}px"></i>']
    for v in yt:
        yy = my(v)
        if yy < py0 - 1 or yy > py1 + 1: continue
        ax.append(f'<i class="scg" style="left:{px0}px; top:{yy:.1f}px; width:{px1 - px0}px"></i><div class="sct y" style="right:{X.W - px0 + 12}px; top:{yy - 13:.1f}px">{W.tick_auto(v) if logy else W.tick_label(v, ydiv, ysuf)}</div>')
    for v in xt:
        xx = mx(v)
        if xx < px0 - 1 or xx > px1 + 1: continue
        ax.append(f'<div class="sct x" style="left:{xx:.1f}px; top:{py1 + 10}px">{W.tick_auto(v) if logx else W.tick_label(v, xdiv, xsuf)}</div>')
    ax.append(f'<div class="scal x" style="right:{X.W - px1}px; top:{py1 + 42}px">{X.rich(p.get("xlab", ""))}<span>{X.rich(p.get("xunit", ""))}</span></div>')
    ax.append(f'<div class="scal y" style="left:{px0 + 14}px; top:{py0 - 4}px">{X.rich(p.get("ylab", ""))}<span>{X.rich(p.get("yunit", ""))}</span></div>')
    quad = ""
    if p.get("quad"):
        qx, qy = (p["quad"] if isinstance(p["quad"], (list, tuple)) else (sorted(xs)[n // 2], sorted(ys)[n // 2]))
        quad = f'<i class="scq v" style="left:{mx(qx):.1f}px; top:{py0}px; height:{py1 - py0}px"></i><i class="scq h" style="left:{px0}px; top:{my(qy):.1f}px; width:{px1 - px0}px"></i>'
    legend = ""
    if smax and p.get("size_lab"):
        legend += f'<div class="sclg"><i class="b"></i><i class="s"></i>{X.rich(p["size_lab"])}</div>'
    if groups:
        legend += "".join(f'<div class="sclg"><i style="background:{GC[gi % 4]}"></i>{X.rich(str(g))}</div>' for gi, g in enumerate(groups))
    note = ""
    if hli is not None and p.get("hl_note"):
        q = pts[hli]
        nfs, nls = W.fit_px(X, p["hl_note"], (px1 - px0) * 0.5 - 28, 2 * 22 * 1.35, 22, 17, 2)
        nw = max(W.F.em(l) for l in nls) * nfs + 30; nh = len(nls) * nfs * 1.35 + 20
        nx = min(max(q["cx"] - nw / 2, px0 + 10), px1 - nw)
        ny = q["cy"] - q["r"] - nh - 14 if q["cy"] - q["r"] - nh - 14 > py0 else q["cy"] + q["r"] + 20
        note = f'<div class="scnote" style="left:{nx:.0f}px; top:{ny:.0f}px; width:{nw:.0f}px; font-size:{nfs:.0f}px">{W.lines_html(X, nls)}</div>'
    X.css("fx-scatter", """
.fx .sc .scax { position:absolute; background:var(--fg); } .fx .sc .scax.x { height:3px; transform-origin:0 50%; } .fx .sc .scax.y { width:3px; transform-origin:50% 100%; }
.fx .sc .scg { position:absolute; height:1px; background:color-mix(in srgb, var(--fg) 12%, transparent); transform-origin:0 50%; }
.fx .sc .sct { position:absolute; font:600 20px var(--f-num, var(--f-mono, monospace)); color:var(--muted); white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .sc .sct.x { transform:translateX(-50%); }
.fx .sc .scal { position:absolute; font:800 24px var(--f-body); color:var(--fg); white-space:nowrap; } .fx .sc .scal span { font-weight:500; color:var(--muted); margin-left:8px; font-size:.8em; }
.fx .sc .scp { position:absolute; border-radius:50%; box-shadow:0 0 0 3px var(--bg); opacity:.92; }
.fx .sc .scp.hl { box-shadow:0 0 0 3px var(--bg), 0 0 0 7px var(--accent); opacity:1; }
.fx .sc .scl.hl { color:var(--accent); }
.fx .sc .scq { position:absolute; background:repeating-linear-gradient(90deg, var(--muted) 0 8px, transparent 8px 16px); opacity:.5; }
.fx .sc .scq.v { width:2px; background:repeating-linear-gradient(180deg, var(--muted) 0 8px, transparent 8px 16px); } .fx .sc .scq.h { height:2px; }
.fx .sc .sclgs { position:absolute; display:flex; flex-wrap:wrap; gap:8px 26px; }
.fx .sc .sclg { display:flex; align-items:center; gap:10px; font:600 20px var(--f-body); color:var(--muted); white-space:nowrap; }
.fx .sc .sclg i { width:16px; height:16px; border-radius:50%; background:var(--muted); }
.fx .sc .sclg i.b { width:26px; height:26px; background:none; border:2px solid var(--muted); } .fx .sc .sclg i.s { width:12px; height:12px; background:none; border:2px solid var(--muted); margin-left:-6px; }
.fx .sc .scnote .fl { display:block; white-space:nowrap; } .fx .sc .scnote { position:absolute; font:700 22px/1.35 var(--f-body); color:var(--bg); background:var(--fg); padding:10px 14px; border-radius:6px; }
""")
    lg_pos = f"left:{px0}px; top:{py1 + 82}px" if P else f"left:{px0}px; top:{py1 + 44}px"
    inner = (f'<div class="w3 sc">{hh}{"".join(ax)}{quad}{"".join(els)}{note}'
             f'<div class="sclgs" style="{lg_pos}">{legend}</div>{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .scax.y", {{scaleY:0, duration:0.5, ease:"expo.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .scax.x", {{scaleX:0, duration:0.5, ease:"expo.inOut"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .scg", {{scaleX:0, duration:0.5, ease:"expo.out", stagger:0.05}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .sct, {s} .scal", {{opacity:0, duration:0.4, stagger:0.02}}, {t + 0.35:.3f});')
    order = sorted(range(n), key=lambda i: pts[i]["x"])
    st = min(0.18, max(0.012, (d * 0.22) / max(n, 1)))
    t0 = t + 0.5
    labeled = {L["i"] for L in labs}
    for k, i in enumerate(order):
        ti = t0 + k * st
        X.tw(f'tl.from("{s} .scp[data-i=\'{i}\']", {{scale:0, y:-30, duration:0.5, ease:"back.out(2)"}}, {ti:.3f});')
        if i in labeled: X.tw(f'tl.from("{s} .scl[data-i=\'{i}\']", {{opacity:0, x:-10, duration:0.35}}, {ti + 0.15:.3f});')
        if n <= 12: X.sfx(ti, "pop")
    tq = t0 + n * st + 0.2
    if quad: X.tw(f'tl.from("{s} .scq", {{opacity:0, duration:0.4}}, {tq:.3f});')
    if legend: X.tw(f'tl.from("{s} .sclg", {{opacity:0, y:10, duration:0.4, stagger:0.08}}, {tq:.3f});')
    if hli is not None:
        X.tw(f'tl.to("{s} .scp:not(.hl)", {{opacity:0.35, duration:0.4}}, {tq + 0.2:.3f});')
        X.tw(f'tl.fromTo("{s} .scp.hl", {{scale:1}}, {{keyframes:[{{scale:1.25, duration:0.15}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], immediateRender:false}}, {tq + 0.2:.3f});')
        X.tw(f'tl.from("{s} .scnote", {{y:16, opacity:0, duration:0.45, ease:"back.out(2)"}}, {tq + 0.35:.3f});')
        X.sfx(tq + 0.25, "hit")


FX = {"scatter": scatter}
