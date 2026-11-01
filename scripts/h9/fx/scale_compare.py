"""尺度换算 Scale Comparison (「相当于 3 个三峡」「绕赤道 7.8 圈」; D1/D2 infographic family — Envato Popular
「Infographic」packs, Mapal「Animate Infographics Like VOX」34.6 万播放, the Kurzgesagt / Vox staple): turns one big number
into something you can picture, three ways —
  laps  : a line spirals round a globe until it has gone ratio times around (the counter ticks with every lap);
  units : the reference object repeats ratio times in a growing grid, the last one partly filled;
  area  : the reference square grows into the big one at the true area ratio.
The headline and the method line sit beside it; the ratio lands big with a pop.

Adapts: ratio 0.1 … 100,000+ (units groups icons ×10/×100 with a legend past ~120; laps caps the drawn turns and
says so; area keeps the small square visible), headline / ref / method from a word to a sentence (fitted), 16:9 puts
the picture right of the text, 9:16 above it.
p: mode (laps | units | area) · ratio (or value + ref_value) · head · ratio_label (e.g. "圈", "个三峡") · basis (what
one unit is) · method · icon (container | field | earth | building | car | person | cup | phone | box | ship | plane |
dam | coin) · dec
"""
import math
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

ICON = {   # 48×48 line icons, drawn here (MIT)
    "container": '<rect x="4" y="13" width="40" height="22" rx="1.5"/><path d="M11 13v22M18 13v22M25 13v22M32 13v22M39 13v22"/>',
    "field": '<rect x="4" y="10" width="40" height="28" rx="1"/><path d="M24 10v28"/><circle cx="24" cy="24" r="5"/><path d="M4 18h5v12H4M44 18h-5v12h5"/>',
    "earth": '<circle cx="24" cy="24" r="18"/><path d="M6 24h36M24 6c6 5 6 31 0 36M24 6c-6 5-6 31 0 36M9 14h30M9 34h30"/>',
    "building": '<path d="M10 42V8h18v34M28 42V18h10v24M6 42h36"/><path d="M15 14h3M21 14h3M15 20h3M21 20h3M15 26h3M21 26h3M15 32h3M21 32h3"/>',
    "car": '<path d="M6 30v-6l5-9h22l7 9h2v6H6z"/><circle cx="14" cy="32" r="4"/><circle cx="34" cy="32" r="4"/><path d="M13 24h22"/>',
    "person": '<circle cx="24" cy="13" r="6"/><path d="M12 42V30c0-6 5-10 12-10s12 4 12 10v12"/>',
    "cup": '<path d="M13 14h22l-3 28H16z"/><path d="M10 14h28M26 14l5-10"/>',
    "phone": '<rect x="14" y="4" width="20" height="40" rx="3"/><path d="M21 38h6"/>',
    "box": '<path d="M5 15l19-8 19 8v19l-19 8-19-8z"/><path d="M5 15l19 8 19-8M24 23v19"/>',
    "ship": '<path d="M4 32h40l-5 9H9z"/><path d="M10 32V22h22v10M16 22v-8h8v8M32 26h6v6"/>',
    "plane": '<path d="M4 26l16-3 9-15h4l-4 15 13 2 4-5h2l-2 8 2 8h-2l-4-5-13 2 4 15h-4l-9-15-16-3z"/>',
    "dam": '<path d="M4 40h40M8 40l6-28h20l6 28"/><path d="M14 12v28M20 12v28M26 12v28M32 12v28"/>',
    "coin": '<circle cx="24" cy="24" r="17"/><path d="M17.5 15.5l6.5 8 6.5-8M24 23.5V35M18 26h12M18 31h12"/>',
}

CSS = """
.fx .dtc { position:absolute; }
.fx .dtc .dtc-cam { position:absolute; inset:0; }
.fx .dtc .dtc-tx { position:absolute; }
.fx .dtc .dtc-h { font:900 4.6vmin/1.2 var(--f-display); color:var(--fg); }
.fx .dtc .dtc-h .fl { display:block; }
.fx .dtc .dtc-eq { display:flex; align-items:baseline; gap:1.2vmin; margin-top:2.4vmin; white-space:nowrap; }
.fx .dtc .dtc-eq .ap { font:700 4vmin var(--f-display); color:var(--muted); }
.fx .dtc .dtc-eq b { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.9; color:var(--accent); font-variant-numeric:tabular-nums; }
.fx .dtc .dtc-eq em { font:900 4.6vmin var(--f-display); font-style:normal; color:var(--fg); }
.fx .dtc .dtc-ref { margin-top:2vmin; font:700 2.4vmin/1.4 var(--f-body); color:var(--muted); }
.fx .dtc .dtc-m { margin-top:1.2vmin; font:500 1.7vmin/1.45 var(--f-mono, monospace); color:var(--muted); letter-spacing:.02em; }
.fx .dtc .dtc-vz { position:absolute; }
.fx .dtc svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.fx .dtc .glb { fill:none; stroke:var(--fg); stroke-width:.35; }
.fx .dtc .glb.f { fill:color-mix(in srgb, var(--fg) 6%, transparent); }
.fx .dtc .sp { fill:none; stroke:var(--accent); stroke-width:.55; stroke-linecap:round; }
.fx .dtc .hd { fill:var(--accent); }
.fx .dtc .ic { position:absolute; color:var(--fg); }
.fx .dtc .ic svg { position:static; width:100%; height:100%; fill:none; stroke:currentColor; stroke-width:2.6; stroke-linejoin:round; stroke-linecap:round; }
.fx .dtc .ic.last { color:var(--accent); }
.fx .dtc .lg { position:absolute; font:700 1.8vmin var(--f-mono, monospace); color:var(--muted); white-space:nowrap; display:flex; align-items:center; gap:.8vmin; }
.fx .dtc .lg i { display:inline-block; width:3vmin; height:3vmin; color:var(--fg); }
.fx .dtc .lg i svg { position:static; width:100%; height:100%; fill:none; stroke:currentColor; stroke-width:2.6; }
.fx .dtc .sq { position:absolute; border:.4vmin solid var(--fg); }
.fx .dtc .sq.a { background:var(--fg); }
.fx .dtc .sq.b { background:color-mix(in srgb, var(--accent) 18%, transparent); border-color:var(--accent); transform-origin:0 100%; }
.fx .dtc .sql { position:absolute; font:800 2.2vmin var(--f-body); color:var(--fg); white-space:nowrap; }
"""


def _icon(k): return f'<svg viewBox="0 0 48 48">{ICON.get(k, ICON["box"])}</svg>'


def scale_compare(X, cid, t, d, p):
    mode = p.get("mode", "laps")
    if p.get("ratio") is not None: ratio = float(p["ratio"])
    else: ratio = float(p.get("value", 1)) / max(1e-12, float(p.get("ref_value", 1)))
    ratio = max(0.01, ratio)
    dec = int(p.get("dec", 1 if ratio < 100 and abs(ratio - round(ratio)) > 0.04 else 0))
    rl = p.get("ratio_label", "倍")
    bx, by, bw, bh = U.box(X)
    P = X.portrait
    # text block and picture boxes
    if P:
        vz = (6.0, 0.0, bw - 12.0, bh * 0.52); tx = (0.0, bh * 0.56, bw, bh * 0.44)
    else:
        tx = (0.0, 0.0, bw * 0.42, bh); vz = (bw * 0.47, 2.0, bw * 0.53, bh - 4.0)
    hs, hl = U.fit(p.get("head", ""), tx[2], tx[3] * 0.38, 4.8 if not P else 5.2, 2.6, 3)
    num = U.fmt(ratio, dec)
    ns = min(16.0 if not P else 14.0, (tx[2] - U.em(rl) * 4.6 - U.em("≈") * 4) / max(U.em(num), 1))
    X.css("fx-dtc", CSS)
    text = (f'<div class="dtc-tx" style="left:{tx[0]:.2f}vmin; top:{tx[1]:.2f}vmin; width:{tx[2]:.2f}vmin; height:{tx[3]:.2f}vmin; display:flex; flex-direction:column; justify-content:center">'
            f'<div class="dtc-h" style="font-size:{hs:.2f}vmin">{U.lines_html(X, hl)}</div>'
            f'<div class="dtc-eq"><span class="ap">≈</span><b style="font-size:{ns:.2f}vmin"><span class="n">0</span></b><em>{X.rich(rl)}</em></div>'
            f'{"<div class=dtc-ref>" + X.rich(p["basis"]) + "</div>" if p.get("basis") else ""}'
            f'{"<div class=dtc-m>" + X.rich(p["method"]) + "</div>" if p.get("method") else ""}</div>')
    vx, vy, vw, vh = vz
    pic = []
    if mode == "laps":
        side = min(vw, vh)
        R = side * 0.26
        turns = min(ratio, 24.0)
        gap = (side * 0.48 - R * 1.08) / max(turns, 1)
        pts, L = [], 0.0
        steps = max(60, int(turns * 90))
        prev = None
        for k in range(steps + 1):
            th = turns * 2 * math.pi * k / steps
            r = R * 1.08 + gap * th / (2 * math.pi)
            x = 50 + (r * math.sin(th)) / side * 100; y = 50 - (r * math.cos(th)) / side * 100
            if prev: L += math.hypot(x - prev[0], y - prev[1])
            pts.append((x, y)); prev = (x, y)
        dpath = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
        g = R / side * 100
        globe = (f'<circle class="glb f" cx="50" cy="50" r="{g:.2f}"/><ellipse class="glb" cx="50" cy="50" rx="{g * 0.45:.2f}" ry="{g:.2f}"/>'
                 f'<path class="glb" d="M{50 - g:.2f} 50 H{50 + g:.2f} M{50 - g * 0.87:.2f} {50 - g * 0.5:.2f} H{50 + g * 0.87:.2f} M{50 - g * 0.87:.2f} {50 + g * 0.5:.2f} H{50 + g * 0.87:.2f}"/>')
        pic.append(f'<div class="dtc-vz" style="left:{vx + (vw - side) / 2:.2f}vmin; top:{vy + (vh - side) / 2:.2f}vmin; width:{side:.2f}vmin; height:{side:.2f}vmin">'
                   f'<svg viewBox="0 0 100 100">{globe}<path class="sp" d="{dpath}" style="stroke-dasharray:{L:.2f}; stroke-dashoffset:{L:.2f}"/>'
                   f'<circle class="hd" r="1.4" cx="{pts[0][0]:.2f}" cy="{pts[0][1]:.2f}"/></svg></div>')
        if ratio > turns: pic.append(f'<div class="lg" style="left:{vx:.2f}vmin; top:{vy + vh - 3:.2f}vmin">只画出前 {int(turns)} 圈</div>')
        meta = ("laps", L, turns, pts)
    elif mode == "units":
        group = 1
        while ratio / group > 120: group *= 10
        cnt = ratio / group
        whole, frac = int(cnt), cnt - int(cnt)
        k = whole + (1 if frac > 0.04 else 0)
        k = max(1, k)
        from h9 import fit as FIT
        cols, rows = FIT.grid(k, vw, vh - (4 if group > 1 else 0), 1.0, gap=1.0)
        cell = min((vw - (cols - 1) * 1.0) / cols, (vh - (4 if group > 1 else 0) - (rows - 1) * 1.0) / rows)
        gw = cols * cell + (cols - 1) * 1.0; gh = rows * cell + (rows - 1) * 1.0
        ox = vx + (vw - gw) / 2; oy = vy + (vh - (4 if group > 1 else 0) - gh) / 2
        for i in range(k):
            r_, c_ = divmod(i, cols)
            last = i == k - 1 and frac > 0.04
            clip = f"clip-path:inset(0 {(1 - frac) * 100:.1f}% 0 0);" if last else ""
            pic.append(f'<div class="ic {"last" if last else ""}" data-i="{i}" style="left:{ox + c_ * (cell + 1):.2f}vmin; top:{oy + r_ * (cell + 1):.2f}vmin; width:{cell * 0.9:.2f}vmin; height:{cell * 0.9:.2f}vmin; {clip}">{_icon(p.get("icon", "box"))}</div>')
        if group > 1:
            pic.append(f'<div class="lg" style="left:{ox:.2f}vmin; top:{oy + gh + 1.5:.2f}vmin"><i>{_icon(p.get("icon", "box"))}</i>= {U.fmt(group, 0)} {X.rich(p.get("unit_name", "个"))}</div>')
            X.used_text.update("=0123456789,")
        meta = ("units", k)
    else:   # area
        side_b = min(vw, vh) * 0.86
        side_a = max(1.2, side_b / math.sqrt(max(ratio, 1)))
        if ratio < 1: side_a, side_b = side_b, side_b * math.sqrt(ratio)
        ox = vx + (vw - side_b) / 2; oy = vy + (vh + side_b) / 2
        pic.append(f'<i class="sq b" style="left:{ox:.2f}vmin; top:{oy - side_b:.2f}vmin; width:{side_b:.2f}vmin; height:{side_b:.2f}vmin"></i>')
        pic.append(f'<i class="sq a" style="left:{ox:.2f}vmin; top:{oy - side_a:.2f}vmin; width:{side_a:.2f}vmin; height:{side_a:.2f}vmin"></i>')
        if p.get("a_label"): pic.append(f'<div class="sql" style="left:{ox + side_a + 1:.2f}vmin; top:{oy - side_a - 3:.2f}vmin">{X.rich(p["a_label"])}</div>')
        if p.get("b_label"): pic.append(f'<div class="sql" style="left:{ox:.2f}vmin; top:{oy - side_b - 3.4:.2f}vmin">{X.rich(p["b_label"])}</div>')
        meta = ("area", side_a / side_b)
    X.used_text.update("≈0123456789.,只画出前圈")
    inner = f'<div class="dtc" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin"><div class="dtc-cam">{text}{"".join(pic)}</div></div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dtc-h .fl", {{yPercent:80, opacity:0, duration:0.6, ease:"expo.out", stagger:0.08}}, {t:.3f});')
    if p.get("basis") or p.get("method"): X.tw(f'tl.from("{s} .dtc-ref, {s} .dtc-m", {{y:14, opacity:0, duration:0.5, ease:"expo.out", stagger:0.1}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .dtc-eq", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.25:.3f});')
    run = max(1.0, min(d - 1.6, 3.2))
    t0 = t + 0.45
    if meta[0] == "laps":
        _, L, turns, pts = meta
        X.tw(f'tl.from("{s} .glb", {{scale:0.6, opacity:0, transformOrigin:"50% 50%", duration:0.6, ease:"expo.out", stagger:0.05}}, {t + 0.05:.3f});')
        X.tw(f'tl.to("{s} .sp", {{strokeDashoffset:0, duration:{run:.2f}, ease:"power1.inOut"}}, {t0:.3f});')
        # the head rides the spiral: sample the path at 24 keyframes (deterministic)
        kf = []
        for j in range(25):
            q = j / 24
            # power1.inOut progress → index
            e = 2 * q * q if q < 0.5 else 1 - (-2 * q + 2) ** 2 / 2
            x, y = pts[min(len(pts) - 1, int(e * (len(pts) - 1)))]
            kf.append(f'{{attr:{{cx:{x:.2f}, cy:{y:.2f}}}, duration:{run / 24:.3f}, ease:"none"}}')
        X.tw(f'tl.to("{s} .hd", {{keyframes:[{", ".join(kf)}]}}, {t0:.3f});')
        U.count(X, f"{s} .dtc-eq .n", t0, 0, ratio, run, dec, ease="power1.inOut")
        for j in range(1, int(min(turns, 12)) + 1): X.sfx(t0 + run * (j / turns) ** 0.9, "tick")
        tl_end = t0 + run
    elif meta[0] == "units":
        k = meta[1]
        X.tw(f'tl.from("{s} .ic", {{scale:0, opacity:0, duration:0.35, ease:"back.out(2.4)", stagger:{{each:{min(0.08, run / max(k, 1)):.3f}, from:"start"}}}}, {t0:.3f});')
        U.count(X, f"{s} .dtc-eq .n", t0, 0, ratio, run, dec, ease="none")
        if any('class="lg"' in h for h in pic): X.tw(f'tl.from("{s} .lg", {{opacity:0, duration:0.4}}, {t0 + run:.3f});')
        for j in range(min(k, 10)): X.sfx(t0 + run * j / max(min(k, 10), 1), "tick")
        tl_end = t0 + min(run, 0.08 * k + 0.35)
    else:
        X.tw(f'tl.from("{s} .sq.a", {{scale:0, transformOrigin:"0 100%", duration:0.5, ease:"back.out(2)"}}, {t + 0.3:.3f});')
        X.tw(f'tl.fromTo("{s} .sq.b", {{scale:{meta[1]:.4f}}}, {{scale:1, duration:{run:.2f}, ease:"expo.inOut"}}, {t0 + 0.2:.3f});')
        X.tw(f'tl.from("{s} .sql", {{opacity:0, y:10, duration:0.4, stagger:0.2}}, {t0:.3f});')
        U.count(X, f"{s} .dtc-eq .n", t0 + 0.2, 1, ratio, run, dec, ease="expo.inOut")
        X.sfx(t0 + 0.2, "whoosh_soft")
        tl_end = t0 + 0.2 + run
    X.tw(f'tl.fromTo("{s} .dtc-eq b", {{scale:1}}, {{keyframes:[{{scale:1.14, duration:0.14}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], transformOrigin:"0% 80%", immediateRender:false}}, {tl_end:.3f});')
    X.sfx(tl_end, "hit")
    X.tw(f'tl.fromTo("{s} .dtc-cam", {{scale:0.98}}, {{scale:1.03, transformOrigin:"{"70% 50%" if not P else "50% 30%"}", duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


FX = {"scale_compare": scale_compare}
