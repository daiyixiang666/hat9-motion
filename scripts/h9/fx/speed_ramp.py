"""变速：慢放 / 快进 (speed ramp — "放慢四倍看清楚" / "快进跳过"): the clip is re-timed at build time (ffmpeg,
cached, deterministic) and plays through its ramps; a speed badge pops at every change (0.25× · 4×), a small
graph-editor strip draws the speed curve with a running playhead, and each ramp lands on a flash. `drama: true`
adds the slow-motion grammar — letterbox bars and a cooler, desaturated picture while it is slow.

p: video · start · ramp [[a, b, speed], …] in source seconds (default: 1× → 0.25× → 1× around `start`) ·
   smooth (true = frame-blended slow motion, slower to build) · drama · badge (a short caption on the badge; `label` is the reel tag) ·
   graph (true) · focus
Adapts: 1–6 ramp segments, speeds 0.05×–16×, clips shorter than the beat (the last frame holds), any source aspect
(a clip whose shape fights the frame plays as a card), 16:9 and 9:16 badge / graph positions.
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A = _load("_av")

CSS = """
.sr-badge { position:absolute; display:flex; flex-direction:column; align-items:flex-start; gap:6px; opacity:0; }
.sr-badge b { font-family:var(--f-num, var(--f-display)); font-variation-settings:"wdth" 70, "wght" 900; font-weight:900; font-size:150px; line-height:.85; color:#fbfaf6; text-shadow:0 0 2px rgba(0,0,0,.5), 0 4px 0 rgba(0,0,0,.28), 0 6px 34px rgba(0,0,0,.7); -webkit-text-stroke:2px rgba(17,17,17,.55); paint-order:stroke fill; letter-spacing:-.02em; }
.sr-badge b small { font-size:.5em; margin-left:.04em; }
.sr-badge span { font:800 30px var(--f-body); color:#111; background:#f6ce3a; padding:4px 14px; border-radius:6px; }
.sr-badge.fast b { color:#f6ce3a; }
.sr-graph { position:absolute; background:rgba(12,12,12,.78); border-radius:12px; padding:12px 14px 10px; }
.sr-graph .lab { position:absolute; left:14px; top:8px; font:700 15px var(--f-mono, monospace); color:#bbb; letter-spacing:.1em; }
.sr-graph svg { position:absolute; left:14px; right:14px; bottom:10px; overflow:visible; }
.sr-graph polyline { fill:none; stroke:#f6ce3a; stroke-width:3.5; stroke-linejoin:round; }
.sr-graph .base { stroke:rgba(255,255,255,.25); stroke-width:1.5; stroke-dasharray:4 5; }
.sr-head { position:absolute; top:30px; bottom:10px; width:2px; background:#e2321f; }
.sr-head::before { content:''; position:absolute; top:-6px; left:-6px; width:14px; height:14px; border-radius:50%; background:#e2321f; }
.sr-flash { position:absolute; inset:0; background:#fff; opacity:0; }
.sr-bar { position:absolute; left:0; right:0; height:11%; background:#000; }
.sr-streaks { position:absolute; inset:0; opacity:0; background:repeating-linear-gradient(90deg, transparent 0 140px, rgba(255,255,255,.18) 140px 146px, transparent 146px 260px); }
"""


def speed_ramp(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    src = p.get("video")
    s0 = float(p.get("start", 0))
    dur = fit.duration(A.src_abs(X, src)) if src else 0
    ramp = p.get("ramp")
    if not ramp:
        L = max(0.6, min(dur - s0, 3.0) / 3) if dur else 0.8
        ramp = [[s0, s0 + L, 1], [s0 + L, s0 + 2 * L, 0.25], [s0 + 2 * L, s0 + 3 * L, 1]]
    path, odur, parts = A.retime(X, src, ramp, smooth=bool(p.get("smooth")))
    ar = fit.aspect(X, src, 16 / 9)
    m = 56 if P else 96
    card = max(ar / (W / H), (W / H) / ar) > 1.9
    if card:
        cw = (W - 2 * m) if ar > W / H else min(W * 0.46, (H - 360) * ar)
        ch = cw / ar
        cx, cy = (W - cw) / 2, (max(300, min((H - ch) / 2 - 80, 1250 - ch)) if P else (H - ch) / 2)
        rect = f"inset:auto; left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; border-radius:18px; box-shadow:0 30px 70px rgba(0,0,0,.35);"
    else:
        cx, cy, cw, ch, rect = 0, 0, W, H, ""
    vd = min(d, odur)
    _, vsel = fit.media(X, cid, "rv", str(path), t, vd, "sr-v", fill="cover", z=2, focus=p.get("focus"), extra_style=rect)
    X.css("fx-speed", CSS)
    S = f"#{cid}"
    tail = ""
    if odur < d - 0.05:                                   # hold the last frame for the rest of the beat
        tail = f'<img class="sr-tail" src="{A.still(X, str(path), max(0, odur - 0.05))}" alt="" style="position:absolute; left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; object-fit:cover;{" border-radius:18px;" if card else ""}">'
    # badges: one per segment whose speed differs from the previous one
    badges, marks = [], []
    prev = None
    bx, by = (cx + 40, cy + 40) if card else ((m, 252) if P else (m, 140))
    for i, (o0, o1, k) in enumerate(parts):
        if prev is not None and abs(k - prev) < 1e-3: continue
        prev = k
        if i == 0 and abs(k - 1) < 1e-3: continue
        txt = (f"{k:g}" if k >= 1 else f"{k:.2g}").rstrip("0").rstrip(".") if k != int(k) else f"{int(k)}"
        lab = p.get("badge") or ("慢放" if k < 1 else "快进" if k > 1 else "正常速度")
        X.used_text.update(txt + "×" + lab)
        badges.append(f'<div class="sr-badge{" fast" if k > 1 else ""}" data-i="{len(badges)}" style="left:{bx:.0f}px; top:{by:.0f}px"><b>{txt}<small>×</small></b><span>{X.rich(lab)}</span></div>')
        marks.append((t + o0, k))
    # graph-editor strip: speed over output time, playhead runs with the clip
    gw, gh = (360, 120) if not P else (420, 120)
    gx, gy = ((W - m - gw), (H - 300)) if not P else (m, 1130)
    if card and not P: gx, gy = cx + cw - gw - 24, cy + ch - gh - 24
    ks = [k for _, _, k in parts]
    kmax = max(1.0, max(ks)); kmin = min(ks)
    import math
    def yv(k):  # log scale, 1× in the middle band
        lo, hi = math.log(min(kmin, 0.25)), math.log(max(kmax, 4))
        return (gh - 46) * (1 - (math.log(k) - lo) / (hi - lo or 1))
    pts = []
    for o0, o1, k in parts:
        x0, x1 = (gw - 28) * o0 / odur, (gw - 28) * o1 / odur
        pts += [f"{x0:.1f},{yv(k):.1f}", f"{x1:.1f},{yv(k):.1f}"]
    X.used_text.update("SPEED")
    graph = ""
    if p.get("graph", True):
        graph = (f'<div class="sr-graph" style="left:{gx:.0f}px; top:{gy:.0f}px; width:{gw}px; height:{gh}px"><span class="lab">SPEED</span>'
                 f'<svg width="{gw - 28}" height="{gh - 46}" viewBox="0 0 {gw - 28} {gh - 46}"><line class="base" x1="0" x2="{gw - 28}" y1="{yv(1):.1f}" y2="{yv(1):.1f}"/>'
                 f'<polyline points="{" ".join(pts)}" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/></svg><i class="sr-head" style="left:14px"></i></div>')
    drama = p.get("drama")
    bars = '<i class="sr-bar" style="top:0; transform-origin:50% 0"></i><i class="sr-bar" style="bottom:0; transform-origin:50% 100%"></i>' if drama else ""
    over = f'{tail}<div class="sr-streaks"></div>{"".join(badges)}{graph}{bars}<div class="sr-flash"></div>'
    _clip(X, cid, t, d, over, p, transparent=True)
    if card: A.stage_bg(X, cid, t, d, p); A.scope(X, vsel, t, d)
    if drama: X.tw(f'tl.set("{S} .sr-bar", {{scaleY:0}}, {t:.3f});')
    if tail: X.tw(f'tl.set("{S} .sr-tail", {{opacity:0}}, {t:.3f}); tl.set("{S} .sr-tail", {{opacity:1}}, {t + odur - 0.04:.3f});')
    if graph:
        X.tw(f'tl.from("{S} .sr-graph", {{y:20, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.1:.3f});')
        X.tw(f'tl.to("{S} .sr-graph polyline", {{strokeDashoffset:0, duration:0.6, ease:"power2.inOut"}}, {t + 0.2:.3f});')
        X.tw(f'tl.fromTo("{S} .sr-head", {{x:0}}, {{x:{gw - 28}, duration:{vd:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{vsel}", {{scale:1.0}}, {{scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    for j, (tm, k) in enumerate(marks):
        nxt = marks[j + 1][0] if j + 1 < len(marks) else t + d
        b = f'{S} .sr-badge[data-i="{j}"]'
        gap = nxt - tm                                   # short segments (16× runs last a few frames) get short accents
        if gap > 0.08: X.tw(f'tl.fromTo("{S} .sr-flash", {{opacity:0.55}}, {{opacity:0, duration:{min(0.25, gap - 0.03):.2f}, immediateRender:false}}, {tm:.3f});')
        X.tw(f'tl.fromTo(\'{b}\', {{opacity:0, scale:1.6}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", transformOrigin:"0% 0%", immediateRender:false}}, {tm:.3f});')
        X.tw(f'tl.to(\'{b}\', {{opacity:0, duration:0.2, immediateRender:false}}, {max(tm + 0.5, nxt - 0.15):.3f});')
        X.sfx(tm, "whoosh_deep" if k < 1 else "whoosh")
        run = min(1.2, gap - 0.17)
        if k > 1 and run >= 0.1:
            X.tw(f'tl.fromTo("{S} .sr-streaks", {{opacity:0, x:0}}, {{opacity:1, x:-260, duration:{run:.2f}, ease:"none", immediateRender:false}}, {tm:.3f});')
            X.tw(f'tl.to("{S} .sr-streaks", {{opacity:0, duration:0.15, immediateRender:false}}, {tm + run + 0.01:.3f});')
        if drama and k < 1:
            X.tw(f'tl.to("{S} .sr-bar", {{scaleY:1, duration:0.45, ease:"expo.out"}}, {tm:.3f});')
            X.tw(f'tl.to("{vsel}", {{filter:"grayscale(0.7) contrast(1.1) brightness(0.95)", duration:0.5}}, {tm:.3f});')
            X.tw(f'tl.to("{S} .sr-bar", {{scaleY:0, duration:0.35, ease:"power2.in"}}, {max(tm + 0.5, nxt - 0.35):.3f});')
            X.tw(f'tl.to("{vsel}", {{filter:"grayscale(0) contrast(1) brightness(1)", duration:0.35}}, {max(tm + 0.5, nxt - 0.35):.3f});')


FX = {"speed_ramp": speed_ramp}
