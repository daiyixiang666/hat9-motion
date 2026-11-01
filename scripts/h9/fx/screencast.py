"""真实录屏推近 (screen recording · Screen-Studio-style auto zoom; VideoHive Phone 7 App & Gestures 2.6K, iTouch 2 App
Promo 2.1K): a real screen recording plays in a browser / phone frame; for every click the camera eases in on the
pointer, a ripple fires, the step list beside it advances, and an optional key area is boxed while the rest dims.

p: video (a real recording; an image works as a still) · start (seconds into the clip) · frame ("browser" | "phone" | "none";
   default by the clip's aspect) · url · tab · clicks: [{t (seconds into the clip) | at (cue / seconds into the beat), x, y
   (0–1 of the frame, or source px), zoom, label}] — or `clicks_json` (the record.mjs json: same shape) · cursor (true) ·
   steps (list of 0–8 lines, step i lights on click i) · hl: [{box:[x,y,w,h], at, until}] key areas
Adapts: landscape or portrait recordings, 0–12 clicks (0 = a slow push), any step count/length (fitted), clips shorter
than the beat (holds the last frame).
"""
import importlib.util, json, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


S = _load("_screens")


def screencast(X, cid, t, d, p):
    P = X.portrait
    src = p.get("video") or p.get("image")
    if not src: raise SystemExit("screencast needs `video` (a screen recording) or `image`")
    is_vid = fit.is_video(src)
    sz = fit.size(fit._abs(X, src)) or (1280, 800)
    sw, sh = sz
    ar = sw / sh
    start = float(p.get("start", 0))
    clicks = list(fit.as_list(p.get("clicks")))
    if not clicks and p.get("clicks_json"):
        clicks = json.loads(fit._abs(X, p["clicks_json"]).read_text()).get("clicks", [])
    kind = p.get("frame") or ("phone" if ar < 0.8 else "browser")
    steps = [str(x) for x in fit.as_list(p.get("steps"))]
    x0, y0, x1, y1 = S.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    side = bool(steps)
    if P:
        bw, bh = aw, ah - (min(ah * 0.3, 64 * len(steps) + 40) if side else 0)
    else:
        bw, bh = (aw * (0.7 if ar >= 1 else 0.46) if side else aw), ah
    g = S.frame_geom(kind, bw, bh, ar, P)
    if P: fx_, fy_ = x0 + (aw - g["w"]) / 2, y0
    else: fx_, fy_ = (x0 if side else x0 + (aw - g["w"]) / 2), y0 + (ah - g["h"]) / 2
    vw, vh = g["vw"], g["vh"]
    k = vw / sw
    pic = S.vtag(X, src, t, d, vw, vh, start=start) if is_vid else f'<img src="{S.prep(X, src)[0]}" alt="" style="width:{vw:.0f}px; height:{vh:.0f}px; object-fit:cover">'
    # click points in viewport px + their times
    pts = []
    for i, c in enumerate(clicks):
        c = c if isinstance(c, dict) else {"x": c[0], "y": c[1]}
        cx, cy = S.frac(c.get("x", 0.5), sw) * k, S.frac(c.get("y", 0.5), sh) * k
        if c.get("at") is not None: tc = S.cue(X, c["at"], t, t + 0.8 + i)
        elif c.get("t") is not None: tc = t + float(c["t"]) - start
        else: tc = t + 0.8 + i * max(1.2, (d - 1.2) / max(len(clicks), 1))
        if t + 0.25 <= tc <= t + d - 0.2:
            pts.append({"x": cx, "y": cy, "t": tc, "z": float(c.get("zoom", 1.9 if not P else 1.7)), "label": c.get("label", "")})
    hls = []
    for j, h in enumerate(fit.as_list(p.get("hl"))):
        bx, by, bw_, bh_ = S.box_of(h.get("box", h) if isinstance(h, dict) else h, sw, sh)
        ta = S.cue(X, h.get("at") if isinstance(h, dict) else None, t, t + d * 0.5)
        tu = S.cue(X, h.get("until") if isinstance(h, dict) else None, t, ta + 1.6)
        hls.append((bx * k, by * k, bw_ * k, bh_ * k, ta, tu))
    cur = S.CURSOR if p.get("cursor", True) else ""
    rips = "".join(f'<i class="scr-rip" data-i="{i}" style="transform:translate({q["x"]:.0f}px,{q["y"]:.0f}px)"></i>' for i, q in enumerate(pts))
    hlh = "".join(f'<div class="sc-hole" data-j="{j}" style="left:{a:.0f}px; top:{b:.0f}px; width:{c:.0f}px; height:{e:.0f}px"></div>'
                  f'<div class="scr-hl" data-j="{j}" style="left:{a:.0f}px; top:{b:.0f}px; width:{c:.0f}px; height:{e:.0f}px"></div>' for j, (a, b, c, e, _, _) in enumerate(hls))
    zoom = f'<div class="scr-zoom sc-zoom" data-layout-allow-overflow style="width:{vw:.0f}px; height:{vh:.0f}px">{pic}{hlh}{rips}{cur}</div>'
    fr = S.frame(X, kind, g, fx_, fy_, zoom, url=p.get("url", ""), tab=p.get("tab", ""), cls="sc-fr")
    # step list
    lst = ""
    if steps:
        if P: lx, ly, lw, lh_ = x0, fy_ + g["h"] + 28, aw, y1 - (fy_ + g["h"] + 28)
        else: lx, ly, lw, lh_ = fx_ + g["w"] + 60, y0 + ah * 0.06, x1 - (fx_ + g["w"] + 60), ah * 0.88
        per = lh_ / len(steps)
        rows = []
        for i, st in enumerate(steps):
            f = fit.fit_text(st, lw - 84, min(per * 0.8, 120 if not P else 56), 46 if not P else 36, 20, max_lines=2, lh=1.2)
            X.used_text.update(st + "0123456789")
            rows.append(f'<div class="sc-step" data-i="{i}"><b><i class="sc-on"></i><em>{i + 1}</em></b><span style="font-size:{f.px}px">{"<br>".join(X.rich(l) for l in f.lines)}</span></div>')
        lst = f'<div class="sc-steps" style="left:{lx:.0f}px; top:{ly:.0f}px; width:{lw:.0f}px; height:{lh_:.0f}px">{"".join(rows)}</div>'
    X.css("fx-screencast", """
.sc-hole { position:absolute; border-radius:10px; box-shadow:0 0 0 4000px rgba(8,10,14,.5); opacity:0; z-index:4; }
.sc-steps { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:16px; }
.sc-step { display:flex; align-items:center; gap:18px; color:var(--fg); opacity:.35; min-width:0; }
.sc-step b { position:relative; flex:none; width:52px; height:52px; border-radius:50%; display:grid; place-items:center; font:800 24px var(--f-mono, monospace);
  border:3px solid currentColor; }
.sc-step b em { position:relative; font-style:normal; }
.sc-step b .sc-on { position:absolute; inset:-7px; border-radius:50%; border:4px solid var(--accent); opacity:0; }
.sc-step span { font-family:var(--f-display, var(--f-body)); font-weight:800; line-height:1.2; }
#root.v .sc-step b { width:44px; height:44px; font-size:20px; }
""")
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, fr + lst, p, dark_chrome=p.get("dark_chrome", True))
    s = f"#{sid}"
    X.tw(f'tl.from("{s} .sc-fr", {{y:60, scale:0.94, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    if lst: X.tw(f'tl.from("{s} .sc-step", {{x:{0 if P else 30}, y:{20 if P else 0}, opacity:0, duration:0.45, ease:"expo.out", stagger:0.06}}, {t + 0.3:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # cursor + zoom choreography: ease in on each click, follow to the next, pull out at the end
    zsel = f"{s} .sc-zoom"
    if cur: X.tw(f'tl.set("{s} .scr-cur", {{x:{vw * 0.62:.0f}, y:{vh * 0.7:.0f}}}, {t:.3f});')
    if not pts:
        X.tw(f'tl.fromTo("{zsel}", {{scale:1, x:0, y:0}}, {{scale:1.08, x:{-vw * 0.04:.0f}, y:{-vh * 0.04:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    px, py = vw * 0.62, vh * 0.7
    zoomed = False
    for i, q in enumerate(pts):
        mv = 0.55
        if cur: X.tw(f'tl.to("{s} .scr-cur", {{x:{q["x"]:.0f}, y:{q["y"]:.0f}, duration:{mv}, ease:"power2.inOut"}}, {q["t"] - mv:.3f});')
        zx, zy = S.zoom_xy(vw, vh, q["z"], q["x"], q["y"])
        X.tw(f'tl.to("{zsel}", {{scale:{q["z"]:.3f}, x:{zx:.0f}, y:{zy:.0f}, duration:{0.8 if not zoomed else 0.7}, ease:"power3.inOut"}}, {q["t"] - 0.75:.3f});')
        zoomed = True
        X.tw(f'tl.fromTo("{s} .scr-rip[data-i=\'{i}\']", {{scale:0.2, opacity:1}}, {{scale:1.3, opacity:0, duration:0.55, ease:"power2.out", immediateRender:false}}, {q["t"]:.3f});')
        if cur: X.tw(f'tl.fromTo("{s} .scr-cur", {{scale:1}}, {{keyframes:[{{scale:0.82, duration:0.08}}, {{scale:1, duration:0.16}}], immediateRender:false}}, {q["t"]:.3f});')
        X.sfx(q["t"], "click")
        if steps and i < len(steps):
            X.tw(f'tl.to("{s} .sc-step[data-i=\'{i}\']", {{opacity:1, duration:0.3}}, {q["t"]:.3f});')
            X.tw(f'tl.fromTo("{s} .sc-step[data-i=\'{i}\'] .sc-on", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {q["t"]:.3f});')
            if i > 0: X.tw(f'tl.to("{s} .sc-step[data-i=\'{i - 1}\']", {{opacity:0.55, duration:0.3}}, {q["t"]:.3f});')
        nxt = pts[i + 1]["t"] if i + 1 < len(pts) else None
        if nxt is None or nxt - q["t"] > 2.6:          # a long gap: pull back out so the viewer sees where we are
            out_t = q["t"] + 1.3 if nxt is None else q["t"] + 1.2
            if out_t < t + d - 0.3:
                X.tw(f'tl.to("{zsel}", {{scale:1, x:0, y:0, duration:0.8, ease:"power3.inOut"}}, {out_t:.3f});')
                zoomed = False
        px, py = q["x"], q["y"]
    for j, (_, _, _, _, ta, tu) in enumerate(hls):
        X.tw(f'tl.to("{s} .sc-hole[data-j=\'{j}\']", {{opacity:1, duration:0.3}}, {ta:.3f});')
        X.tw(f'tl.fromTo("{s} .scr-hl[data-j=\'{j}\']", {{opacity:1, clipPath:"inset(0 100% 0 0 round 10px)"}}, {{clipPath:"inset(0 0% 0 0 round 10px)", duration:0.4, ease:"power3.out", immediateRender:false}}, {ta:.3f});')
        X.tw(f'tl.to("{s} .sc-hole[data-j=\'{j}\'], {s} .scr-hl[data-j=\'{j}\']", {{opacity:0, duration:0.3}}, {min(tu, t + d - 0.3):.3f});')
    if steps and not pts:     # no clicks: step through the list on a clock
        for i in range(len(steps)):
            ti = t + 0.8 + i * (d - 1.2) / len(steps)
            X.tw(f'tl.to("{s} .sc-step[data-i=\'{i}\']", {{opacity:1, duration:0.3}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{s} .sc-step[data-i=\'{i}\'] .sc-on", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {ti:.3f});')


FX = {"screencast": screencast}
