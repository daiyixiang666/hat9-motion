"""长截图滚动 (website scroll · VideoHive Minimal Website Presentation 1.9K): a long screenshot inside a browser or
phone frame scrolls with eased stops; at each stop the target is boxed, labelled, and the rest of the page dims;
a scroll thumb tracks the position. A table of stops runs beside the frame (16:9) or under it (9:16).

p: image (any aspect, 1:1 … 1:20 tall, or landscape) · frame ("browser" | "phone" | "none"; default by width) · url · tab
   · stops: list of {find | heading | y | box:[x,y,w,h], label, at} — find/heading use the webpage.mjs json beside the image;
     y and box take 0–1 fractions or source px · hl ("box" | "band") · toc (true/false)
Adapts: 0 stops (a slow full scroll), 1–8 stops; a shot too short to scroll zooms into its stops instead (Ken Burns);
any label length (fitted); frame size solves for the area in both aspects.
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


def _stops(X, p, sw, sh, meta):
    out = []
    heads = meta.get("headings", []); boxes = meta.get("boxes", [])
    ms = (meta.get("width") or sw)
    k = sw / ms if ms else 1.0                       # json px → prepared-image px
    for st in fit.as_list(p.get("stops")):
        st = st if isinstance(st, dict) else {"y": st}
        bx = None
        if st.get("find"):
            b = next((b for b in boxes if b.get("find") == st["find"]), None)
            if b: bx = (b["x"] * k, b["y"] * k, b["w"] * k, b["h"] * k)
        if bx is None and st.get("heading"):
            hd = next((h for h in heads if str(st["heading"]) in h.get("text", "")), None)
            if hd: bx = (0, hd["y"] * k - 10 * k, sw, (hd.get("h", 40) + 20) * k)
        if bx is None and st.get("box") is not None:
            bx = S.box_of(st["box"], sw, sh)
        if bx is None and st.get("y") is not None:
            y = S.frac(st["y"], sh); bx = (0, y, sw, sh * 0.06)
        if bx is None: continue
        out.append({"box": bx, "label": st.get("label") or st.get("heading") or st.get("find") or "", "at": st.get("at")})
    return out


def scroll_shot(X, cid, t, d, p):
    P = X.portrait
    src = p.get("image") or p.get("shot")
    if not src: raise SystemExit("scroll_shot needs `image` (a screenshot)")
    meta = S.sidecar(X, src)
    url_img, sw, sh = S.prep(X, src)
    ar_src = sw / sh
    kind = p.get("frame") or ("phone" if (meta.get("width") or sw) <= 820 and ar_src < 0.9 else "browser")
    stops = _stops(X, p, sw, sh, meta)
    x0, y0, x1, y1 = S.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    toc = p.get("toc", True) and any(s["label"] for s in stops) and len(stops) >= 2
    # viewport aspect: phones are 9:19.5; browser windows ~4:3 (16:9 output) or ~4:5 (9:16) unless the shot is wider
    if kind == "phone": var = 9 / 19.5
    elif P: var = max(1.0, min(1.4, ar_src)) if ar_src > 1 else 1.04
    else: var = max(1.25, min(1.78, ar_src)) if ar_src > 1 else 1.3
    if P:
        bw, bh = aw, ah - (min(ah * 0.24, 70 * len(stops) + 30) if toc else 0)
    else:
        bw, bh = aw * (0.64 if toc else 0.9), ah
    g = S.frame_geom(kind, bw, bh, var, P)
    if P: fx_, fy_ = x0 + (aw - g["w"]) / 2, y0
    else: fx_, fy_ = (x0 if toc else x0 + (aw - g["w"]) / 2), y0 + (ah - g["h"]) / 2
    vw, vh = g["vw"], g["vh"]
    k = vw / sw                                       # image px → viewport px
    doc_h = sh * k
    room = doc_h - vh
    zoom_mode = room < vh * 0.12
    if zoom_mode:                                     # short or landscape shots: fit the whole page, zoom to stops
        k = min(vw / sw, vh / sh); doc_h = sh * k; room = 0
    dw = sw * k
    ox = (vw - dw) / 2 if zoom_mode else 0
    oy = (vh - doc_h) / 2 if zoom_mode else 0
    # highlight boxes + labels in doc space
    hls, tags = [], []
    for i, s in enumerate(stops):
        bx, by, bw_, bh_ = s["box"]
        X_, Y_, W_, H_ = ox + bx * k - 8, oy + by * k - 8, bw_ * k + 16, bh_ * k + 16
        X_ = max(ox + 6, X_); W_ = min(W_, ox + dw - 6 - X_)
        r = f"left:{X_:.0f}px; top:{Y_:.0f}px; width:{W_:.0f}px; height:{H_:.0f}px"
        hls.append(f'<div class="ss-hole" data-i="{i}" style="{r}"></div><div class="scr-hl ss-hl" data-i="{i}" style="{r}"></div>')
        if s["label"] and not toc:
            X.used_text.update(str(s["label"]))
            tags.append(f'<div class="scr-tag ss-tag" data-i="{i}" style="left:{X_ + 6:.0f}px; top:{Y_ + H_ + 10:.0f}px"><i>{i + 1:02d}</i>{X.rich(s["label"])}</div>')
    dim = ""
    thumb = ""
    if not zoom_mode:
        th = max(36, vh * vh / doc_h)
        thumb = f'<div class="ss-track"><i class="ss-thumb" style="height:{th:.0f}px"></i></div>'
    doc = (f'<div class="scr-zoom ss-doc" data-layout-allow-overflow style="width:{dw:.0f}px; height:{doc_h:.0f}px; left:{ox:.0f}px; top:{oy:.0f}px">'
           f'<img src="{url_img}" alt="" style="width:{dw:.0f}px; height:{doc_h:.0f}px" data-layout-allow-overflow>{dim}{"".join(hls)}{"".join(tags)}</div>{thumb}')
    fr = S.frame(X, kind, g, fx_, fy_, doc, url=p.get("url", meta.get("url", "")), tab=p.get("tab", ""), cls="ss-fr")
    # table of stops
    tocs = ""
    if toc:
        if P:
            tx, ty, tw, th_ = x0, fy_ + g["h"] + 26, aw, y1 - (fy_ + g["h"] + 26)
        else:
            tx, ty, tw, th_ = fx_ + g["w"] + 64, y0 + ah * 0.08, x1 - (fx_ + g["w"] + 64), ah * 0.84
        n = len(stops)
        rows = []
        per_h = th_ / max(n, 1)
        for i, s in enumerate(stops):
            f = fit.fit_text(fit.as_text(s["label"]), tw - 80, min(per_h * 0.78, 130 if not P else 60), 60 if not P else 40, 20, max_lines=2, lh=1.18)
            X.used_text.update(str(s["label"]) + "0123456789")
            rows.append(f'<div class="ss-row" data-i="{i}"><b>{i + 1:02d}</b><span style="font-size:{f.px}px">{"<br>".join(X.rich(l) for l in f.lines)}</span></div>')
        cols = 2 if P and n > 3 else 1
        tocs = (f'<div class="ss-toc" style="left:{tx:.0f}px; top:{ty:.0f}px; width:{tw:.0f}px; height:{th_:.0f}px; grid-template-columns:repeat({cols}, 1fr)">{"".join(rows)}'
                + ('' if P else '<i class="ss-rail"><b class="ss-prog"></b></i>') + '</div>')
    X.css("fx-scroll-shot", """
.ss-hole { position:absolute; border-radius:10px; box-shadow:0 0 0 4000px rgba(8,10,14,.55); opacity:0; z-index:4; }
.ss-hl { z-index:5; }
.ss-rail { position:absolute; left:-30px; top:6%; bottom:6%; width:4px; border-radius:2px; background:color-mix(in srgb, var(--fg) 14%, transparent); }
.ss-rail .ss-prog { position:absolute; left:0; right:0; top:0; height:100%; border-radius:2px; background:var(--accent); transform-origin:50% 0; }
.ss-track { position:absolute; right:6px; top:8px; bottom:8px; width:6px; border-radius:3px; background:rgba(127,127,127,.18); z-index:9; }
.ss-thumb { position:absolute; left:0; right:0; top:0; border-radius:3px; background:rgba(127,127,127,.7); }
.ss-toc { position:absolute; display:grid; align-content:center; gap:14px 26px; }
.ss-row { display:flex; align-items:baseline; gap:16px; color:var(--fg); opacity:.32; min-width:0; }
.ss-row b { font:700 24px var(--f-mono, monospace); color:var(--accent); flex:none; }
.ss-row span { font-family:var(--f-display, var(--f-body)); font-weight:900; line-height:1.2; }
""")
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, fr + tocs, p, dark_chrome=p.get("dark_chrome"))
    s = f"#{sid}"
    X.tw(f'tl.from("{s} .ss-fr", {{y:60, scale:0.94, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    if tocs and not P: X.tw(f'tl.set("{s} .ss-prog", {{scaleY:0}}, {t:.3f});')
    if tocs: X.tw(f'tl.from("{s} .ss-row", {{x:{0 if P else 40}, y:{24 if P else 0}, opacity:0, duration:0.5, ease:"expo.out", stagger:0.07}}, {t + 0.3:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # schedule: first move after the frame lands; holds share what is left
    t0, t_end = t + 0.75, t + d - 0.25
    n = len(stops)
    if n == 0:
        if room > 0:
            X.tw(f'tl.fromTo("{s} .ss-doc", {{y:0}}, {{y:{-room:.0f}, duration:{t_end - t0:.2f}, ease:"sine.inOut"}}, {t0:.3f});')
            X.tw(f'tl.fromTo("{s} .ss-thumb", {{y:0}}, {{y:{vh - 16 - max(36, vh * vh / doc_h):.0f}, duration:{t_end - t0:.2f}, ease:"sine.inOut"}}, {t0:.3f});')
        else:
            X.tw(f'tl.fromTo("{s} .ss-doc", {{scale:1}}, {{scale:1.08, duration:{t_end - t0:.2f}, ease:"none"}}, {t0:.3f});')
        return
    slot = (t_end - t0) / n
    prev_y, prev_t = 0.0, t0
    thumb_h = max(36, vh * vh / doc_h) if not zoom_mode else 0
    for i, st in enumerate(stops):
        bx, by, bw_, bh_ = st["box"]
        ta = S.cue(X, st.get("at"), t, t0 + i * slot)
        ta = max(ta, prev_t + 0.35)
        if zoom_mode:
            z = max(1.0, min(2.6, 0.62 * min(vw / (bw_ * k + 40), vh / (bh_ * k + 40))))
            cx, cy = ox + (bx + bw_ / 2) * k, oy + (by + bh_ / 2) * k
            zx, zy = S.zoom_xy(vw, vh, z, cx, cy)
            X.tw(f'tl.to("{s} .ss-doc", {{x:{zx - ox * (z - 1):.0f}, y:{zy - oy * (z - 1):.0f}, scale:{z:.3f}, transformOrigin:"0 0", duration:0.9, ease:"power3.inOut"}}, {ta - 0.75:.3f});')
            land = ta
        else:
            target = max(0.0, min(room, by * k - vh * 0.3))
            dist = abs(target - prev_y)
            mv = max(0.55, min(1.5, 0.45 + dist / (vh * 2.2)))
            start = max(prev_t + 0.05, ta - mv)
            X.tw(f'tl.to("{s} .ss-doc", {{y:{-target:.0f}, duration:{ta - start:.2f}, ease:"power3.inOut"}}, {start:.3f});')
            X.tw(f'tl.to("{s} .ss-thumb", {{y:{(vh - 16 - thumb_h) * (target / room if room else 0):.0f}, duration:{ta - start:.2f}, ease:"power3.inOut"}}, {start:.3f});')
            X.sfx(start, "whoosh_soft")
            prev_y = target
            land = ta
        # dim + box + label
        X.tw(f'tl.to("{s} .ss-hole[data-i=\'{i}\']", {{opacity:1, duration:0.3}}, {land:.3f});')
        X.tw(f'tl.fromTo("{s} .ss-hl[data-i=\'{i}\']", {{opacity:1, clipPath:"inset(0 100% 0 0 round 10px)"}}, {{clipPath:"inset(0 0% 0 0 round 10px)", duration:0.4, ease:"power3.out", immediateRender:false}}, {land:.3f});')
        X.tw(f'tl.set("{s} .ss-hl[data-i=\'{i}\']", {{zIndex:6}}, {land:.3f});')
        if not toc and st["label"]:
            X.tw(f'tl.fromTo("{s} .ss-tag[data-i=\'{i}\']", {{y:12, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {land + 0.15:.3f});')
        if toc:
            X.tw(f'tl.to("{s} .ss-row[data-i=\'{i}\']", {{opacity:1, x:{0 if P else 10}, duration:0.3, ease:"power2.out"}}, {land:.3f});')
            if i > 0: X.tw(f'tl.to("{s} .ss-row[data-i=\'{i - 1}\']", {{opacity:0.32, x:0, duration:0.3}}, {land:.3f});')
            if not P: X.tw(f'tl.to("{s} .ss-prog", {{scaleY:{(i + 1) / n:.3f}, duration:0.22, ease:"power2.out"}}, {land:.3f});')
        X.sfx(land, "click")
        nxt = S.cue(X, stops[i + 1].get("at"), t, t0 + (i + 1) * slot) if i + 1 < n else None
        if nxt is not None:
            X.tw(f'tl.to("{s} .ss-hl[data-i=\'{i}\'], {s} .ss-tag[data-i=\'{i}\'], {s} .ss-hole[data-i=\'{i}\']", {{opacity:0, duration:0.25}}, {max(land + 0.5, nxt - 0.9):.3f});')
        prev_t = land
    # keep the frame alive between stops
    X.tw(f'tl.fromTo("{s}", {{scale:1}}, {{scale:1.025, transformOrigin:"50% 50%", duration:{d:.2f}, ease:"none"}}, {t:.3f});')


FX = {"scroll_shot": scroll_shot}
