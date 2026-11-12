"""光标演示层 (cursor demo · the pointer layer of Screen Studio-style tutorials; VideoHive "Phone 7 App & Gestures"
2.6K): a pointer that can sit on ANY screenshot or screen recording and act out what the narration says —
move, click (press + ripple), hover (a label pops), drag (press, a ghost chip and a trail follow, drop ripple) and
type (a small field types the text). The camera can follow the pointer.

p: image | video (any aspect) · start (s into the clip) · frame ("none" | "browser" | "phone"; default by aspect) · url · tab
   · path: [{act: move|click|hover|drag|type, x, y (0–1 of the picture, or source px), to:[x,y] (drag end), label, text,
   at (cue or seconds into the beat)}] · zoom (1 = still camera; 1.3–2 = follow each point) · trail (true)
Adapts: portrait or landscape pictures, stills or clips; 0–12 steps (0 = a slow drift with the pointer parked);
labels of any length (one line, fitted); tags flip away from the picture's edges.
"""
import importlib.util, pathlib, sys
from h9 import fit as FT
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


U = _load("_ui")
S = U.S


def cursor(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    src = p.get("video") or p.get("image")
    if not src: raise SystemExit("cursor needs `image` or `video` (the picture the pointer acts on)")
    is_vid = FT.is_video(src)
    sw, sh = FT.size(FT._abs(X, src)) or (1280, 800)
    ar = sw / sh
    kind = p.get("frame") or ("phone" if ar < 0.8 else ("browser" if ar > 1.25 else "none"))
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 20
    aw, ah = x1 - x0, y1 - y0
    g = S.frame_geom(kind, aw, ah, ar, P)
    fx_, fy_ = x0 + (aw - g["w"]) / 2, y0 + (ah - g["h"]) / 2
    vw, vh = g["vw"], g["vh"]
    k = vw / sw
    pic = (S.vtag(X, src, t, d, vw, vh, start=float(p.get("start", 0))) if is_vid
           else f'<img src="{S.prep(X, src)[0]}" alt="" style="width:{vw:.0f}px; height:{vh:.0f}px; object-fit:cover">')
    steps = []
    raw = list(FT.as_list(p.get("path") or p.get("steps")))[:12]
    auto = U.spread(len(raw), t + min(1.0, d * 0.22), t + d - min(1.1, d * 0.24))
    for i, st in enumerate(raw):
        st = st if isinstance(st, dict) else {"act": "click", "x": st[0], "y": st[1]}
        q = {"act": str(st.get("act", "click")), "x": S.frac(st.get("x", 0.5), sw) * k, "y": S.frac(st.get("y", 0.5), sh) * k,
             "label": str(st.get("label", "")), "text": str(st.get("text", "")), "t": U.when(X, st.get("at"), t, auto[i])}
        if st.get("to") is not None:
            q["tx"], q["ty"] = S.frac(st["to"][0], sw) * k, S.frac(st["to"][1], sh) * k
        elif q["act"] == "drag":
            q["tx"], q["ty"] = min(vw * 0.9, q["x"] + vw * 0.25), q["y"]
        q["fixed"] = st.get("at") is not None
        steps.append(q)
    st_times = []
    st_fixed = []
    st_say = []
    for q in steps:
        st_times.append(q["t"])
        st_fixed.append(q["fixed"])
        st_say.append([q["label"], q["text"]])
    st_times = U.follow(X, st_say, t, d, st_times, st_fixed, gap=0.6)    # a click lands when the narration names it
    for i in range(len(steps)):
        steps[i]["t"] = st_times[i]
    steps.sort(key=lambda q: q["t"])
    for i in range(1, len(steps)):                   # keep moves physically possible
        steps[i]["t"] = max(steps[i]["t"], steps[i - 1]["t"] + (1.25 if steps[i - 1]["act"] in ("drag", "type") else 0.6))
    steps = [q for q in steps if q["t"] < t + d - 0.35]
    tag_px = 26 if not P else 24
    over = []
    for i, q in enumerate(steps):
        ex, ey = (q.get("tx", q["x"]), q.get("ty", q["y"])) if q["act"] == "drag" else (q["x"], q["y"])
        over.append(f'<i class="ui-rip" data-i="{i}" style="left:{ex:.0f}px; top:{ey:.0f}px"></i>')
        if q["act"] == "drag":
            mx, my = (q["x"] + q["tx"]) / 2, min(q["y"], q["ty"]) - abs(q["tx"] - q["x"]) * 0.18
            over.append(f'<svg class="cu-trail" data-i="{i}" width="{vw:.0f}" height="{vh:.0f}" viewBox="0 0 {vw:.0f} {vh:.0f}" data-layout-allow-overflow>'
                        f'<path d="M{q["x"]:.1f} {q["y"]:.1f} Q{mx:.1f} {my:.1f} {q["tx"]:.1f} {q["ty"]:.1f}" pathLength="1"/></svg>')
            over.append(f'<div class="cu-ghost" data-i="{i}">{X.rich(q["label"] or "拖动")}</div>')
        if q["act"] == "type":
            n = len(q["text"])
            over.append(f'<div class="cu-field" data-i="{i}" style="left:{min(q["x"], vw - 360):.0f}px; top:{min(q["y"] + 28, vh - 70):.0f}px">'
                        f'<span>{U.typed(X, q["text"])}</span><i class="ui-caret"></i></div>')
        if q["label"] and q["act"] != "drag":
            f = FT.fit_text(q["label"], vw * 0.46, tag_px * 1.4, tag_px, 14, max_lines=1)
            right = ex < vw * 0.58
            below = ey < vh * 0.62
            side = f"left:{ex + 30:.0f}px;" if right else f"right:{vw - ex + 30:.0f}px;"
            vert = f"top:{ey + 22:.0f}px;" if below else f"bottom:{vh - ey + 22:.0f}px;"
            over.append(f'<div class="scr-tag cu-tag" data-i="{i}" style="{side} {vert} font-size:{f.px}px"><i>{i + 1:02d}</i>{X.rich(f.lines[0] if f.lines else q["label"])}</div>')
    X.used_text.update("0123456789拖动")
    zoom = (f'<div class="scr-zoom cu-zoom" data-layout-allow-overflow style="width:{vw:.0f}px; height:{vh:.0f}px">{pic}{"".join(over)}'
            f'<div class="cu-ptr">{U.CURSOR}</div></div>')
    fr = S.frame(X, kind, g, fx_, fy_, zoom, url=p.get("url", ""), tab=p.get("tab", ""), cls="cu-fr")
    X.css("fx-cursor", """
.cu-ptr { position:absolute; left:0; top:0; z-index:12; }
.cu-ptr .ui-cur { position:absolute; }
.cu-trail { position:absolute; left:0; top:0; z-index:6; overflow:visible; pointer-events:none; }
.cu-trail path { fill:none; stroke:var(--accent); stroke-width:5; stroke-linecap:round; stroke-dasharray:1 1; stroke-dashoffset:1; }
.cu-ghost { position:absolute; left:0; top:0; z-index:11; white-space:nowrap; font:800 24px var(--f-body); color:#111; background:#fff; padding:10px 16px; border-radius:10px;
  box-shadow:0 0 0 3px var(--accent), 0 14px 30px rgba(0,0,0,.3); opacity:0; transform-origin:0 0; }
.cu-field { position:absolute; z-index:10; display:flex; align-items:center; min-width:220px; height:58px; padding:0 18px; border-radius:12px; background:#fff; color:#111;
  font:700 26px var(--f-body); box-shadow:0 0 0 3px var(--accent), 0 14px 30px rgba(0,0,0,.28); opacity:0; white-space:nowrap; }
.cu-tag { white-space:nowrap; }
""")
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, fr, p, dark_chrome=p.get("dark_chrome", p.get("theme") == "ink"))
    s = f"#{sid}"
    zs = f"{s} .cu-zoom"
    X.tw(f'tl.from("{s} .cu-fr", {{y:50, scale:0.95, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    px_, py_ = vw * 0.7, vh * 0.78
    X.tw(f'tl.set("{s} .cu-ptr", {{x:{px_:.0f}, y:{py_:.0f}}}, {t:.3f});')
    z = float(p.get("zoom", 1.0))
    if not steps:
        X.tw(f'tl.fromTo("{zs}", {{scale:1, x:0, y:0}}, {{scale:1.07, x:{-vw * 0.035:.0f}, y:{-vh * 0.035:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    elif z <= 1.01:   # a still camera still breathes
        X.tw(f'tl.fromTo("{zs}", {{scale:1, x:0, y:0}}, {{scale:1.04, x:{-vw * 0.02:.0f}, y:{-vh * 0.02:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    zend = t    # the follow-camera never starts a move before the last one has landed
    for i, q in enumerate(steps):
        ti, a = q["t"], q["act"]
        arrive = ti - (0.38 if a == "drag" else 0.05)
        mv = 0.55
        X.tw(f'tl.to("{s} .cu-ptr", {{x:{q["x"]:.0f}, y:{q["y"]:.0f}, duration:{mv}, ease:"power2.inOut"}}, {arrive - mv:.3f});')
        if z > 1.01:
            zx, zy = S.zoom_xy(vw, vh, z, q["x"], q["y"])
            z0 = max(arrive - 0.7, zend)
            zd = max(0.3, min(0.75, arrive + 0.05 - z0))
            X.tw(f'tl.to("{zs}", {{scale:{z:.3f}, x:{zx:.0f}, y:{zy:.0f}, duration:{zd:.2f}, ease:"power3.inOut"}}, {z0:.3f});')
            zend = z0 + zd
        press = f'tl.fromTo("{s} .cu-ptr .ui-cur", {{scale:1}}, {{keyframes:[{{scale:0.8, duration:0.08}}, {{scale:1, duration:0.16}}], immediateRender:false}}, {{T:.3f}});'
        rip = f'tl.fromTo("{s} .ui-rip[data-i=\'{i}\']", {{scale:0.2, opacity:1}}, {{scale:1.3, opacity:0, duration:0.55, ease:"power2.out", immediateRender:false}}, {{T:.3f}});'
        if a in ("click", "type"):
            X.tw(press.replace("{T:.3f}", f"{ti:.3f}")); X.tw(rip.replace("{T:.3f}", f"{ti:.3f}")); X.sfx(ti, "click")
        if a == "hover":
            X.tw(f'tl.fromTo("{s} .ui-rip[data-i=\'{i}\']", {{scale:0.4, opacity:0.8}}, {{scale:0.9, opacity:0, duration:0.9, ease:"sine.out", immediateRender:false}}, {ti:.3f});')
        if a == "drag":
            t0 = ti - 0.3
            X.tw(f'tl.to("{s} .cu-ptr .ui-cur", {{scale:0.84, duration:0.1}}, {t0:.3f});')
            X.tw(f'tl.set("{s} .cu-ghost[data-i=\'{i}\']", {{x:{q["x"] + 16:.0f}, y:{q["y"] + 18:.0f}}}, {t0:.3f});')
            X.tw(f'tl.to("{s} .cu-ghost[data-i=\'{i}\']", {{opacity:1, scale:1.04, duration:0.18}}, {t0:.3f});')
            X.tw(f'tl.to("{s} .cu-ptr", {{x:{q["tx"]:.0f}, y:{q["ty"]:.0f}, duration:0.8, ease:"power2.inOut"}}, {t0 + 0.12:.3f});')
            X.tw(f'tl.to("{s} .cu-ghost[data-i=\'{i}\']", {{x:{q["tx"] + 16:.0f}, y:{q["ty"] + 18:.0f}, duration:0.8, ease:"power2.inOut"}}, {t0 + 0.12:.3f});')
            X.tw(f'tl.to("{s} .cu-trail[data-i=\'{i}\'] path", {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut"}}, {t0 + 0.12:.3f});')
            X.tw(f'tl.to("{s} .cu-ptr .ui-cur", {{scale:1, duration:0.12}}, {t0 + 0.95:.3f});')
            X.tw(rip.replace("{T:.3f}", f"{t0 + 0.95:.3f}"))
            X.tw(f'tl.to("{s} .cu-ghost[data-i=\'{i}\']", {{opacity:0, scale:0.9, duration:0.25}}, {t0 + 1.0:.3f});')
            if p.get("trail", True) is False or i + 1 < len(steps):
                X.tw(f'tl.to("{s} .cu-trail[data-i=\'{i}\']", {{opacity:0, duration:0.4}}, {t0 + 1.4:.3f});')
            X.sfx(t0, "click"); X.sfx(t0 + 0.95, "pop")
            q["x"], q["y"] = q["tx"], q["ty"]
        if a == "type":
            n = len(q["text"])
            X.tw(f'tl.fromTo("{s} .cu-field[data-i=\'{i}\']", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.25, ease:"expo.out", immediateRender:false}}, {ti + 0.1:.3f});')
            nxt = steps[i + 1]["t"] if i + 1 < len(steps) else t + d
            U.type_in(X, f'{s} .cu-field[data-i=\'{i}\']', ti + 0.3, n, cps=max(10.0, n / 1.0), caret=f'{s} .cu-field[data-i=\'{i}\'] .ui-caret', until=nxt - 0.2)
            X.sfx(ti + 0.3, "type")
            if i + 1 < len(steps):
                X.tw(f'tl.to("{s} .cu-field[data-i=\'{i}\']", {{opacity:0, duration:0.3}}, {nxt - 0.25:.3f});')
        if q["label"] and a != "drag":
            X.tw(f'tl.fromTo("{s} .cu-tag[data-i=\'{i}\']", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {ti + 0.08:.3f});')
            if i + 1 < len(steps):
                X.tw(f'tl.to("{s} .cu-tag[data-i=\'{i}\']", {{opacity:0, duration:0.25}}, {max(steps[i + 1]["t"] - 0.3, ti + 0.4):.3f});')
    if steps and z > 1.01 and max(steps[-1]["t"] + 1.2, zend) + 0.8 < t + d - 0.3:
        X.tw(f'tl.to("{zs}", {{scale:1, x:0, y:0, duration:0.8, ease:"power3.inOut"}}, {max(steps[-1]["t"] + 1.2, zend):.3f});')


FX = {"cursor": cursor}
