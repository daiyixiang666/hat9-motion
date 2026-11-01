"""视频定格 + 标注 (freeze-frame & annotate — "停一下，看这里"): the clip plays, a white flash freezes it on the
exact frame, the picture pushes in while the rest dims and the marks draw on with their labels and a ⏸ timecode
stamp; then (by default) the marks clear and the clip resumes from the frozen frame. `mode: "drama"` adds the
slow-motion grammar of a dramatic freeze: letterbox bars, desaturation and a heavier push.

p: video · start (seconds into the clip) · at (freeze moment: "@词" / seconds into the beat; default 38 %) ·
   hold (seconds; default ≤ 2.4 s) · pins [{box:[x%,y%,w%,h%] of the source frame, shape: box|circle, label, sub}]
   (0–4; `pin` for one — `marks` is reserved by the engine) · stamp ("定格") · mode (note | drama) · resume (true) · focus
Adapts: any source aspect (a clip whose shape fights the frame — a 16:9 clip in 9:16 — plays as a card so the
marked area stays on screen), 0–4 marks (labels flip sides to stay inside the picture), any hold length, still
image instead of video (the freeze is then just the annotation).
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


A, C = _load("_av"), _load("_cite")

CSS = """
.ff-box { position:absolute; overflow:hidden; }
.ff-box.card { border-radius:18px; box-shadow:0 30px 70px rgba(0,0,0,.35); }
.ff-zoom { position:absolute; inset:0; }
.ff-still { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.ff-dim { position:absolute; inset:0; background:rgba(8,8,8,.58); opacity:0; }
.ff-mk { position:absolute; }
.ff-mk svg { position:absolute; inset:-8px; width:calc(100% + 16px); height:calc(100% + 16px); overflow:visible; }
.ff-mk rect, .ff-mk ellipse { fill:none; stroke:#f6ce3a; stroke-width:6; stroke-linecap:round; vector-effect:non-scaling-stroke; }
.ff-hole { position:absolute; border-radius:10px; box-shadow:0 0 0 4000px rgba(8,8,8,.55); }
.ff-hole.round { border-radius:50%; }
.ff-lab { position:absolute; white-space:nowrap; display:flex; flex-direction:column; gap:2px; }
.ff-lab b { font:900 34px var(--f-display); color:#111; background:#f6ce3a; padding:4px 14px; border-radius:6px; }
.ff-lab span { font:700 22px var(--f-body); color:#fbfaf6; text-shadow:0 2px 8px rgba(0,0,0,.7); padding-left:4px; }
.ff-lead { position:absolute; height:3px; background:#f6ce3a; transform-origin:0 50%; }
.ff-stamp { position:absolute; display:flex; align-items:center; gap:10px; font:800 24px var(--f-mono, monospace); color:#fbfaf6; background:rgba(17,17,17,.85); padding:6px 14px; border-radius:8px; letter-spacing:.06em; }
.ff-stamp i { font-style:normal; color:#e2321f; }
.ff-flash { position:absolute; inset:0; background:#fff; opacity:0; }
.ff-bar { position:absolute; left:0; right:0; height:11%; background:#000; }
"""


def freeze_frame(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    src = p.get("video") or p.get("image")
    vid = bool(src) and fit.is_video(src)
    s0 = float(p.get("start", 0))
    tf = A.when(X, p, "at", t, d, 0.38)
    hold = float(p.get("hold", min(2.4, d * 0.45)))
    hold = max(0.6, min(hold, t + d - tf - 0.2))
    resume = p.get("resume", True) and vid and (t + d - tf - hold) > 0.3
    drama = p.get("mode") == "drama"
    # where the picture sits: full frame, or a card when its shape fights the frame
    ar = fit.aspect(X, src, 16 / 9) if src else 16 / 9
    m = 56 if P else 96
    card = max(ar / (W / H), (W / H) / ar) > 1.9
    if card:
        cw = (W - 2 * m) if ar > W / H else min(W * 0.46, (H - 360) * ar)
        ch = cw / ar
        cx, cy = (W - cw) / 2, (max(300, min((H - ch) / 2 - 80, 1250 - ch)) if P else (H - ch) / 2)
    else:
        cx, cy, cw, ch = 0, 0, W, H
    rect = f"inset:auto; left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px;" + (" border-radius:18px;" if card else "")
    X.css("fx-freeze", CSS)
    S = f"#{cid}"
    sels = []
    if vid:
        _, va = fit.media(X, cid, "va", src, t, max(0.1, tf - t + 0.04), "ff-va", fill="cover", z=2, start=s0, extra_style=rect)
        sels.append(va)
        if resume:
            _, vb = fit.media(X, cid, "vb", src, tf + hold, t + d - tf - hold, "ff-vb", fill="cover", z=2, start=s0 + (tf - t), extra_style=rect)
            sels.append(vb)
        still_url = A.still(X, src, s0 + (tf - t))
    else:
        still_url = X.asset(src) if src else ""
    # marks, in the picture's own coordinates (they ride the push-in with the still)
    marks = p.get("pins") or ([p["pin"]] if p.get("pin") else [])     # ("marks" is a reserved beat key)
    marks = [mk if isinstance(mk, dict) else {"box": mk} for mk in marks][:4]
    mk_html, centers, placed = [], [], []
    lab_max = (ch - 90) if card else ((1240 if P else H - 250) - cy)     # full frame: labels stay above the caption
    boxes = [A.cover_map(X, src, mk.get("box", [40, 40, 20, 20]), frame=(0, 0, cw, ch)) if src else (cw * .4, ch * .4, cw * .2, ch * .2) for mk in marks]
    LH = 76
    for i, mk in enumerate(marks):
        bx, by, bw, bh = boxes[i]
        round_ = mk.get("shape") == "circle"
        centers.append((bx + bw / 2, by + bh / 2))
        shape = (f'<ellipse cx="50%" cy="50%" rx="50%" ry="50%" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>' if round_
                 else f'<rect x="0" y="0" width="100%" height="100%" rx="12" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>')
        hole = f'<div class="ff-hole{" round" if round_ else ""}" data-i="{i}" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px"></div>' if i == 0 else ""
        lab = mk.get("label", ""); sub = mk.get("sub", "")
        X.used_text.update(str(lab) + str(sub))
        lw = 40 + 37 * fit.width(str(lab))       # estimate for placement only; the label itself sizes to its text
        ymid = max(16, min(by + bh / 2 - 30, lab_max))
        # candidates (kind, x0, y0): beside the box on the roomier side, the other side, above, below. A label may not
        # leave the picture, land on an earlier label or on another mark's box — that would name the wrong thing.
        rs = (bx + bw / 2) < cw * 0.55
        side = [("r", bx + bw + 46, ymid), ("l", bx - 46 - lw, ymid)]
        cands = (side if rs else side[::-1]) + [("u", bx + bw / 2 - lw / 2, by - LH - 30), ("d", bx + bw / 2 - lw / 2, by + bh + 30)]
        def ok(c, strict=True):
            k, x0, y0 = c
            if x0 < 16 or x0 + lw > cw - 16 or y0 < 16 or y0 > lab_max: return False
            rect = (x0, y0, x0 + lw, y0 + LH)
            clash = lambda q: rect[0] < q[2] and q[0] < rect[2] and rect[1] < q[3] and q[1] < rect[3]
            if any(clash(q) for q in placed): return False
            return not strict or not any(clash((ox - 8, oy - 8, ox + ow + 8, oy + oh + 8)) for j, (ox, oy, ow, oh) in enumerate(boxes) if j != i)
        pick = next((c for c in cands if ok(c)), None) or next((c for c in cands if ok(c, False)), None) or cands[0]
        kind, x0, y0 = pick
        placed.append((x0, y0, x0 + lw, y0 + LH))
        if kind == "r":   lead = f'left:{bx + bw:.0f}px; top:{y0 + 22:.0f}px; width:{max(10, x0 - bx - bw):.0f}px'
        elif kind == "l": lead = f'left:{x0 + lw:.0f}px; top:{y0 + 22:.0f}px; width:{max(10, bx - x0 - lw):.0f}px'
        elif kind == "u": lead = f'left:{bx + bw / 2:.0f}px; top:{y0 + LH - 20:.0f}px; width:3px; height:{max(10, by - y0 - LH + 20):.0f}px'
        else:             lead = f'left:{bx + bw / 2:.0f}px; top:{by + bh:.0f}px; width:3px; height:{max(10, y0 - by - bh):.0f}px'
        al = {"r": "align-items:flex-start;", "l": "align-items:flex-end;", "u": "align-items:center;", "d": "align-items:center;"}[kind]
        anchor = {"r": f"left:{x0:.0f}px", "l": f"right:{cw - x0 - lw:.0f}px", "u": f"left:{x0 + lw / 2:.0f}px; transform:translateX(-50%)", "d": f"left:{x0 + lw / 2:.0f}px; transform:translateX(-50%)"}[kind]
        labhtml = (f'<div class="ff-lab" data-i="{i}" style="{anchor}; top:{y0:.0f}px; {al}">'
                   + (f"<b>{X.rich(lab)}</b>" if lab else "") + (f"<span>{X.rich(sub)}</span>" if sub else "") + "</div>")
        mk_html.append(hole + f'<div class="ff-mk" data-i="{i}" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px"><svg preserveAspectRatio="none">{shape}</svg></div>'
                       + (f'<i class="ff-lead" data-i="{i}" style="{lead}"></i>' + labhtml if lab or sub else ""))
    stamp = p.get("stamp", "定格")
    code = f"{int((s0 + tf - t) // 60):02d}:{(s0 + tf - t) % 60:04.1f}"
    X.used_text.update(str(stamp) + code + "⏸")
    still_img = f'<img class="ff-still" src="{still_url}" alt="">' if still_url else ""
    dim = '<div class="ff-dim"></div>' if not marks else ""
    box = (f'<div class="ff-box{" card" if card else ""}" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">'
           f'<div class="ff-zoom">{still_img}{dim}{"".join(mk_html)}</div>'
           f'<div class="ff-stamp" style="left:{18 if card else m}px; top:{18 if card else (272 if P else 104)}px"><i>⏸</i>{X.rich(stamp)}{(" · " + code) if vid else ""}</div><div class="ff-flash"></div></div>')
    bars = '<i class="ff-bar" style="top:0"></i><i class="ff-bar" style="bottom:0"></i>' if drama else ""
    _clip(X, cid, t, d, box + bars, p, transparent=vid)
    if card and vid: A.stage_bg(X, cid, t, d, p)
    Z = f"{S} .ff-zoom"
    vis = f"{S} .ff-zoom, {S} .ff-stamp"
    if vid:
        X.tw(f'tl.set("{vis}", {{opacity:0}}, {t:.3f});')
        X.tw(f'tl.set("{vis}", {{opacity:1}}, {tf:.3f});')
    # the freeze: flash, stamp, push toward the first mark, marks draw, dim (drama: bars + desaturate)
    X.tw(f'tl.fromTo("{S} .ff-flash", {{opacity:0.85}}, {{opacity:0, duration:0.28, ease:"power2.out", immediateRender:false}}, {tf:.3f});')
    X.sfx(tf, "click")
    if len(centers) > 1:        # several marks: push toward their middle, gently, so none leaves the picture
        ox, oy = sum(c[0] for c in centers) / len(centers), sum(c[1] for c in centers) / len(centers)
        push = 1.05
    else:
        ox, oy = centers[0] if centers else (cw / 2, ch / 2)
        push = 1.16 if drama else 1.09
    X.tw(f'tl.fromTo("{Z}", {{scale:1, transformOrigin:"{ox:.0f}px {oy:.0f}px"}}, {{scale:{push}, duration:{(hold - 0.24) if resume else hold:.2f}, ease:"power2.out", immediateRender:false}}, {tf:.3f});')
    X.tw(f'tl.from("{S} .ff-stamp", {{x:-20, opacity:0, duration:0.35, ease:"expo.out"}}, {tf + 0.05:.3f});')
    if drama:
        X.tw(f'tl.fromTo("{S} .ff-still", {{filter:"grayscale(0) contrast(1)"}}, {{filter:"grayscale(0.85) contrast(1.12)", duration:0.5, immediateRender:false}}, {tf:.3f});')
        X.tw(f'tl.from("{S} .ff-bar", {{scaleY:0, duration:0.45, ease:"expo.out", transformOrigin:"50% 0%"}}, {tf:.3f});')
    if marks:
        X.tw(f'tl.from("{S} .ff-hole", {{opacity:0, duration:0.35}}, {tf + 0.2:.3f});')
        for i in range(len(marks)):
            ti = tf + 0.25 + i * 0.32
            X.tw(f'tl.to("{S} .ff-mk[data-i=\'{i}\'] rect, {S} .ff-mk[data-i=\'{i}\'] ellipse", {{strokeDashoffset:0, duration:0.45, ease:"power2.inOut"}}, {ti:.3f});')
            X.tw(f'tl.from("{S} .ff-lead[data-i=\'{i}\']", {{scaleX:0, duration:0.3, ease:"expo.out"}}, {ti + 0.3:.3f});')
            X.tw(f'tl.from("{S} .ff-lab[data-i=\'{i}\'] > *", {{y:12, opacity:0, duration:0.35, ease:"expo.out", stagger:0.08}}, {ti + 0.38:.3f});')
            X.sfx(ti + 0.38, "pop")
    elif still_url:
        X.tw(f'tl.to("{S} .ff-dim", {{opacity:1, duration:0.4}}, {tf + 0.1:.3f});')
    if resume:
        t_out = tf + hold
        X.tw(f'tl.to("{S} .ff-hole, {S} .ff-mk, {S} .ff-lead, {S} .ff-lab, {S} .ff-stamp, {S} .ff-dim", {{opacity:0, duration:0.2}}, {t_out - 0.22:.3f});')
        X.tw(f'tl.to("{Z}", {{scale:1, duration:0.2, ease:"power2.in"}}, {t_out - 0.2:.3f});')
        X.tw(f'tl.set("{Z}", {{opacity:0}}, {t_out:.3f});')
        X.tw(f'tl.fromTo("{S} .ff-flash", {{opacity:0.5}}, {{opacity:0, duration:0.22, immediateRender:false}}, {t_out:.3f});')
        if drama: X.tw(f'tl.to("{S} .ff-bar", {{scaleY:0, duration:0.35, ease:"power2.in", transformOrigin:"50% 0%"}}, {t_out:.3f});')
    # the playing picture enters with a short settle (no creep: the frozen still must match it pixel for pixel)
    if sels: X.tw(f'tl.from("{sels[0]}", {{opacity:0, duration:0.25}}, {t:.3f});')


FX = {"freeze_frame": freeze_frame}
