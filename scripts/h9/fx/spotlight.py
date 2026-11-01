"""聚光灯 (spotlight · "只看这一行"; VideoHive Explainer Video Toolkit 4 2.5K): everything dims except one box; the
light irises in from the whole frame onto the first target, then glides box to box (rects or circles), each with a
numbered label. Works on a still, a screenshot or a timed video, framed as a card, in a browser or full-bleed.

p: image | video · start · boxes: [{box:[x,y,w,h] (0–1 or source px), at, label, shape ("rect" | "circle")}] · dim (0.72)
   · frame ("none" | "browser" | "phone" | "bleed") · url · zoom (1 = no push; e.g. 1.25 pushes toward each box)
Adapts: any picture aspect (contained card, or cover when bleed), 1–8 boxes, boxes anywhere (labels flip above/below
and left/right to stay inside), any label length (fitted, one line).
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


S = _load("_screens")


def spotlight(X, cid, t, d, p):
    P = X.portrait
    src = p.get("video") or p.get("image")
    if not src: raise SystemExit("spotlight needs `image` or `video`")
    is_vid = fit.is_video(src)
    if is_vid: sw, sh = fit.size(fit._abs(X, src)) or (1280, 720)
    else: url, sw, sh = S.prep(X, src)
    ar = sw / sh
    kind = p.get("frame", "none")
    x0, y0, x1, y1 = S.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    if kind == "bleed":
        cw, ch = X.W, X.H; cx_, cy_ = 0, 0
        k = max(cw / sw, ch / sh); ox, oy = (cw - sw * k) / 2, (ch - sh * k) / 2
        g = None
    else:
        g = S.frame_geom(kind, aw, ah, ar, P)
        cx_, cy_ = x0 + (aw - g["w"]) / 2, y0 + (ah - g["h"]) / 2
        cw, ch = g["vw"], g["vh"]; k = cw / sw; ox = oy = 0
    pic = (S.vtag(X, src, t, d, sw * k, sh * k, start=float(p.get("start", 0))) if is_vid
           else f'<img src="{url}" alt="" style="width:{sw * k:.0f}px; height:{sh * k:.0f}px">')
    boxes = []
    for i, b in enumerate(fit.as_list(p.get("boxes"))):
        b = b if isinstance(b, dict) else {"box": b}
        bx, by, bw_, bh_ = S.box_of(b.get("box", b), sw, sh)
        X_, Y_, W_, H_ = ox + bx * k, oy + by * k, bw_ * k, bh_ * k
        pad = 10
        X_, Y_, W_, H_ = X_ - pad, Y_ - pad, W_ + 2 * pad, H_ + 2 * pad
        circ = b.get("shape") == "circle"
        if circ:
            r = max(W_, H_) / 2; cxm, cym = X_ + W_ / 2, Y_ + H_ / 2
            X_, Y_, W_, H_ = cxm - r, cym - r, 2 * r, 2 * r
        boxes.append({"x": X_, "y": Y_, "w": W_, "h": H_, "rx": (W_ / 2 if circ else 12), "label": str(b.get("label", "")), "at": b.get("at")})
    dim = float(p.get("dim", 0.72))
    mid = f"{cid}spm"
    lab = []
    for i, b in enumerate(boxes):
        if not b["label"]: continue
        f = fit.fit_text(b["label"], min(cw * 0.7, 640), 60, 30 if not P else 28, 18, max_lines=1)
        wpx = f.em * f.px + 64
        lx = min(max(b["x"], 8), cw - wpx - 8)
        above = b["y"] - 64 > 8
        ly = b["y"] - 60 if above else min(b["y"] + b["h"] + 12, ch - 56)
        X.used_text.update(b["label"] + "0123456789")
        lab.append(f'<div class="scr-tag sp-lab" data-i="{i}" style="left:{lx:.0f}px; top:{ly:.0f}px; font-size:{f.px}px"><i>{i + 1:02d}</i>{X.rich(f.lines[0])}</div>')
    svg = (f'<svg class="sp-ov" width="{cw:.0f}" height="{ch:.0f}" viewBox="0 0 {cw:.0f} {ch:.0f}"><defs><mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{cw:.0f}" height="{ch:.0f}">'
           f'<rect width="{cw:.0f}" height="{ch:.0f}" fill="#fff"/><rect class="sp-hole" x="0" y="0" width="{cw:.0f}" height="{ch:.0f}" rx="0" fill="#000"/></mask></defs>'
           f'<rect class="sp-dim" width="{cw:.0f}" height="{ch:.0f}" fill="rgb(5,7,10)" fill-opacity="{dim}" mask="url(#{mid})" opacity="0"/>'
           f'<rect class="sp-out" x="0" y="0" width="{cw:.0f}" height="{ch:.0f}" rx="0" fill="none" stroke="#f6ce3a" stroke-width="5" opacity="0"/></svg>')
    inner = f'<div class="scr-zoom sp-zoom" data-layout-allow-overflow style="width:{cw:.0f}px; height:{ch:.0f}px">{pic}{svg}{"".join(lab)}</div>'
    if kind == "bleed":
        body = f'<div class="sp-bleed" style="position:absolute; left:0; top:0; width:{cw}px; height:{ch}px; overflow:hidden">{inner}</div>'
    else:
        body = S.frame(X, kind, g, cx_, cy_, inner, url=p.get("url", ""), cls="sp-fr")
    X.css("fx-spotlight", ".sp-ov { position:absolute; left:0; top:0; z-index:4; overflow:visible; } .sp-lab { z-index:9; }")
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, body, p, dark_chrome=p.get("dark_chrome"))
    s = f"#{sid}"
    if kind != "bleed": X.tw(f'tl.from("{s} .sp-fr", {{y:50, scale:0.95, opacity:0, duration:0.65, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    n = len(boxes)
    if not n:
        X.tw(f'tl.fromTo("{s} .sp-zoom", {{scale:1}}, {{scale:1.06, transformOrigin:"50% 50%", duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        return
    t0, slot = t + 0.7, (d - 1.0) / n
    prev = t
    zoom = float(p.get("zoom", 1.0))
    for i, b in enumerate(boxes):
        ta = S.cue(X, b["at"], t, t0 + i * slot)
        mv = 0.75 if i == 0 else 0.6
        a = {"x": round(b["x"]), "y": round(b["y"]), "width": round(b["w"]), "height": round(b["h"]), "rx": round(b["rx"])}
        attr = ", ".join(f"{k_}:{v}" for k_, v in a.items())
        if i == 0: X.tw(f'tl.to("{s} .sp-dim", {{opacity:1, duration:0.35}}, {ta - mv:.3f});')
        X.tw(f'tl.to("{s} .sp-hole", {{attr:{{{attr}}}, duration:{mv}, ease:"power3.inOut"}}, {ta - mv:.3f});')
        X.tw(f'tl.to("{s} .sp-out", {{attr:{{{attr}}}, opacity:1, duration:{mv}, ease:"power3.inOut"}}, {ta - mv:.3f});')
        if zoom > 1.0:
            zx, zy = S.zoom_xy(cw, ch, zoom, b["x"] + b["w"] / 2, b["y"] + b["h"] / 2)
            X.tw(f'tl.to("{s} .sp-zoom", {{scale:{zoom:.3f}, x:{zx:.0f}, y:{zy:.0f}, duration:{mv + 0.2:.2f}, ease:"power3.inOut"}}, {ta - mv:.3f});')
        X.tw(f'tl.fromTo("{s} .sp-lab[data-i=\'{i}\']", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {ta:.3f});')
        if i > 0: X.tw(f'tl.to("{s} .sp-lab[data-i=\'{i - 1}\']", {{opacity:0, duration:0.2}}, {max(prev + 0.32, ta - 0.2):.3f});')
        prev = ta
        X.sfx(ta, "click")


FX = {"spotlight": spotlight}
