"""真实组件出框 (UI lift · the "real component pops out of the page" move from product launch films and Screen Studio
demos): the real page sits in a browser frame and scrolls to one component; the component is boxed while the rest of
the page dims; then its own crisp 2× capture lifts out of the page to the middle of the frame (the page recedes behind
it) and a pointer demos it — hovering and clicking the component's real buttons, each labelled with the button's own text.
Built for scripts/ui_capture.py: every picture is a real capture, nothing is redrawn.

p: image (the full page, e.g. work/ui/page.png) · box [x, y, w, h] (the component on that page; 0–1 or page px)
   · piece (the component's own capture, e.g. work/ui/01-hero.png; default: the box cropped from image)
   · path: [{act: click|hover, x, y (0–1 of the piece, or piece px), label, at}] (0–6 steps)
   · frame ("browser" | "phone" | "none"; default by page width) · url · tab · dark_chrome · lift_at (cue or seconds)
Adapts: components of any aspect (a wide nav bar or a tall card) fill as much of the frame as their shape allows;
a component far down the page is scrolled to first; 0 steps = the lifted piece just breathes; labels flip inward at edges.
Re-skins with the style: outline, ripples and tags use the style's accent; the page behind takes the style's ground.
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

CSS = """
.ul-zoom > img { position:absolute; left:0; top:0; display:block; }
.ul-box { position:absolute; z-index:5; border:4px solid var(--accent); border-radius:10px; box-shadow:0 0 0 9999px rgba(8,10,14,.58); opacity:0; }
.ul-fr { transform-origin:50% 40%; }
.ul-piece { position:absolute; z-index:8; transform-origin:0 0; opacity:0; border-radius:14px; overflow:hidden;
  box-shadow:0 0 0 1px rgba(0,0,0,.10), 0 40px 90px rgba(0,0,0,.42), 0 10px 24px rgba(0,0,0,.22); background:var(--scr-page); }
.ul-piece > img { position:absolute; left:0; top:0; width:100%; height:100%; display:block; }
.ul-ring { position:absolute; inset:-8px; border:4px solid var(--accent); border-radius:20px; opacity:0; }
.ul-ptr { position:absolute; left:0; top:0; z-index:12; }
.ul-tag { position:absolute; z-index:11; white-space:nowrap; font:800 26px var(--f-body); color:var(--card); background:var(--accent);
  padding:7px 14px; border-radius:8px; box-shadow:0 10px 24px rgba(0,0,0,.28); opacity:0; }
.ul-tag i { font-style:normal; font:700 15px var(--f-mono, monospace); margin-right:8px; opacity:.7; }
"""


def _crop(X, src, box):
    """the box cut out of the page (when no piece capture was given), cached in the build."""
    import hashlib
    from PIL import Image
    a = FT._abs(X, src)
    key = hashlib.sha1(f"{a}:{a.stat().st_mtime}:{box}".encode()).hexdigest()[:10]
    dst = X.out / "assets" / "img" / f"{a.stem}-piece-{key}.png"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(a) as im:
            x, y, w, h = (int(round(v)) for v in box)
            im.crop((x, y, x + w, y + h)).save(dst)
    return f"assets/img/{dst.name}", int(box[2]), int(box[3])


def ui_lift(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    src = p.get("image")
    if not src: raise SystemExit("ui_lift needs `image` (the page the component lives on)")
    if p.get("box") is None: raise SystemExit("ui_lift needs `box` (where the component sits on that page)")
    url_img, sw, sh = S.prep(X, src)
    osz = FT.size(FT._abs(X, src)) or (sw, sh)
    kp = sw / osz[0]                                     # original page px → prepared px
    bx, by, bw, bh = (v * kp for v in S.box_of(p["box"], osz[0], osz[1]))
    if p.get("piece"):
        piece_url = X.asset(p["piece"])
        pw, ph = FT.size(FT._abs(X, p["piece"])) or (bw, bh)
    else:
        piece_url, pw, ph = _crop(X, src, (bx / kp, by / kp, bw / kp, bh / kp))
    kind = p.get("frame") or ("browser" if P or osz[0] > 900 else "phone")
    x0, y0, x1, y1 = S.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    if P and kind != "phone":                            # 9:16: the frame takes the whole portrait content box
        bar = 52 if kind == "browser" else 0
        var = aw / (ah - bar)
    else:
        var = 9 / 19.5 if kind == "phone" else 1.45
    g = S.frame_geom(kind, aw * (1 if P else 0.86), ah, var, P)
    fx_, fy_ = x0 + (aw - g["w"]) / 2, y0 + (ah - g["h"]) / 2
    vw, vh = g["vw"], g["vh"]
    # the page window: in 9:16 a portrait crop around the component (a wide desktop page is not shrunk to fit)
    win = sw
    if P and kind != "phone":
        win = min(sw, max(bw * 1.12, sw * 0.36))
    ox = max(0.0, min(sw - win, bx + bw / 2 - win / 2))
    k = vw / win                                         # prepared px → viewport px
    doc_w, doc_h = sw * k, sh * k
    oy = max(0.0, min(doc_h - vh, (by + bh / 2) * k - vh / 2)) if doc_h > vh else 0.0
    # the component on screen once the page has scrolled to it (stage px)
    sx, sy = fx_ + g["vx"] + (bx - ox) * k, fy_ + g["vy"] + by * k - oy
    sbw, sbh = bw * k, bh * k
    # where it lands: as big as its shape allows (9:16: about 92 % of the frame width)
    ar = pw / ph
    tw = X.W * 0.92 if P else aw * 0.8
    th = tw / ar
    cap_h = ah * (0.9 if P else 0.78)
    if th > cap_h: th = cap_h; tw = th * ar
    tx, ty = (X.W - tw) / 2 if P else x0 + (aw - tw) / 2, y0 + (ah - th) / 2
    s0 = sbw / tw
    pad = 10
    box_html = (f'<div class="ul-box" style="left:{bx * k - pad:.0f}px; top:{by * k - pad:.0f}px; '
                f'width:{sbw + 2 * pad:.0f}px; height:{sbh + 2 * pad:.0f}px"></div>')
    zoom = (f'<div class="scr-zoom ul-zoom" data-layout-allow-overflow style="left:{-ox * k:.0f}px; width:{doc_w:.0f}px; height:{doc_h:.0f}px">'
            f'<img src="{url_img}" alt="" style="width:{doc_w:.0f}px; height:{doc_h:.0f}px">{box_html}</div>')
    fr = S.frame(X, kind, g, fx_, fy_, zoom, url=p.get("url", ""), tab=p.get("tab", ""), cls="ul-fr")
    # the demo on the lifted piece
    kk = tw / pw
    lift = U.when(X, p.get("lift_at"), t, t + min(1.9, d * 0.36))
    raw = list(FT.as_list(p.get("path") or p.get("steps")))[:6]
    auto = U.spread(len(raw), lift + 0.85, t + d - min(1.6, d * 0.3))      # labels get time to be read
    steps = []
    for i, st in enumerate(raw):
        st = st if isinstance(st, dict) else {"act": "click", "x": st[0], "y": st[1]}
        steps.append({"act": str(st.get("act", "click")), "x": S.frac(st.get("x", 0.5), pw) * kk, "y": S.frac(st.get("y", 0.5), ph) * kk,
                      "label": str(st.get("label", "")), "t": U.when(X, st.get("at"), t, auto[i])})
    steps.sort(key=lambda q: q["t"])
    for i in range(1, len(steps)):
        steps[i]["t"] = max(steps[i]["t"], steps[i - 1]["t"] + 1.3)       # each label stays long enough to read
    steps = [q for q in steps if q["t"] < t + d - 0.3]
    over = []
    tag_px = 26 if not P else 36                       # 9:16: phone-readable (≥ 36 px at 1080 wide)
    for i, q in enumerate(steps):
        over.append(f'<i class="ui-rip" data-i="{i}" style="left:{tx + q["x"]:.0f}px; top:{ty + q["y"]:.0f}px"></i>')
        if not q["label"]: continue
        f = FT.fit_text(q["label"], X.W * 0.6, tag_px * 1.4, tag_px, 16, max_lines=1)
        ex, ey = tx + q["x"], ty + q["y"]
        right = ex < X.W * 0.58
        below = ey < y0 + ah * 0.6
        side = f"left:{ex + 30:.0f}px;" if right else f"right:{X.W - ex + 30:.0f}px;"
        vert = f"top:{ey + 26:.0f}px;" if below else f"bottom:{X.H - ey + 26:.0f}px;"
        X.used_text.update(q["label"] + "0123456789")
        over.append(f'<div class="ul-tag" data-i="{i}" style="{side} {vert} font-size:{f.px}px"><i>{i + 1:02d}</i>{X.rich(f.lines[0] if f.lines else q["label"])}</div>')
    piece = (f'<div class="ul-piece" style="left:{tx:.0f}px; top:{ty:.0f}px; width:{tw:.0f}px; height:{th:.0f}px">'
             f'<img src="{piece_url}" alt=""><i class="ul-ring"></i></div>')
    ptr = f'<div class="ul-ptr">{U.CURSOR}</div>'
    X.css("fx-ui-lift", CSS)
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, fr + piece + "".join(over) + ptr, p, dark_chrome=p.get("dark_chrome", p.get("theme") == "ink"))
    s = f"#{sid}"
    # 1 · the page arrives and scrolls to the component
    X.tw(f'tl.from("{s} .ul-fr", {{y:60, scale:0.94, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.04:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    t_box = max(t + 0.5, lift - 0.75)
    if oy > 1:
        sd = max(0.4, min(1.1, t_box - t - 0.25))
        X.tw(f'tl.fromTo("{s} .ul-zoom", {{y:0}}, {{y:{-oy:.0f}, duration:{sd:.2f}, ease:"power3.inOut"}}, {t_box - sd:.3f});')
    # 2 · box it, dim the rest
    X.tw(f'tl.fromTo("{s} .ul-box", {{opacity:0, scale:1.06}}, {{opacity:1, scale:1, duration:0.35, ease:"power2.out", immediateRender:false}}, {t_box:.3f});')
    X.sfx(t_box, "click")
    # 3 · the real component lifts out, the page falls back
    X.tw(f'tl.set("{s} .ul-piece", {{opacity:1, x:{sx - tx:.1f}, y:{sy - ty:.1f}, scale:{s0:.4f}}}, {lift:.3f});')
    X.tw(f'tl.to("{s} .ul-piece", {{x:0, y:0, scale:1, duration:0.75, ease:"expo.inOut"}}, {lift:.3f});')
    X.tw(f'tl.to("{s} .ul-fr", {{scale:0.9, opacity:0.32, filter:"blur(4px)", duration:0.75, ease:"power2.inOut"}}, {lift:.3f});')
    X.tw(f'tl.to("{s} .ul-fr .scr-bar", {{opacity:0, duration:0.3}}, {lift:.3f});')     # its address bar would sit under the piece
    X.tw(f'tl.fromTo("{s} .ul-ring", {{opacity:0, scale:1.08}}, {{opacity:1, scale:1, duration:0.3, ease:"power2.out", immediateRender:false}}, {lift + 0.72:.3f});')
    X.tw(f'tl.to("{s} .ul-ring", {{opacity:0, duration:0.4}}, {lift + 1.15:.3f});')
    X.sfx(lift, "whoosh")
    X.sfx(lift + 0.72, "pop")
    land = lift + 0.75
    X.tw(f'tl.fromTo("{s} .ul-piece", {{scale:1}}, {{scale:{1.06 if P else 1.03}, x:{-tw * (0.03 if P else 0.015):.1f}, y:{-th * (0.03 if P else 0.015):.1f}, duration:{max(0.5, t + d - land):.2f}, ease:"none", immediateRender:false}}, {land:.3f});')
    # 4 · the pointer demos the real buttons
    if not steps: return
    px_, py_ = tx + tw * 0.8, min(ty + th + 60, y1 - 20)
    X.tw(f'tl.set("{s} .ul-ptr", {{x:{px_:.0f}, y:{py_:.0f}, opacity:0}}, {t:.3f});')
    X.tw(f'tl.to("{s} .ul-ptr", {{opacity:1, duration:0.2}}, {land:.3f});')
    for i, q in enumerate(steps):
        ti = q["t"]
        mv = 0.5
        X.tw(f'tl.to("{s} .ul-ptr", {{x:{tx + q["x"]:.0f}, y:{ty + q["y"]:.0f}, duration:{mv}, ease:"power2.inOut"}}, {ti - mv - 0.04:.3f});')
        if q["act"] == "hover":
            X.tw(f'tl.fromTo("{s} .ui-rip[data-i=\'{i}\']", {{scale:0.4, opacity:0.8}}, {{scale:0.9, opacity:0, duration:0.9, ease:"sine.out", immediateRender:false}}, {ti:.3f});')
        else:
            X.tw(f'tl.fromTo("{s} .ul-ptr .ui-cur", {{scale:1}}, {{keyframes:[{{scale:0.8, duration:0.08}}, {{scale:1, duration:0.16}}], immediateRender:false}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{s} .ui-rip[data-i=\'{i}\']", {{scale:0.2, opacity:1}}, {{scale:1.3, opacity:0, duration:0.55, ease:"power2.out", immediateRender:false}}, {ti:.3f});')
            X.sfx(ti, "click")
        if q["label"]:
            X.tw(f'tl.fromTo("{s} .ul-tag[data-i=\'{i}\']", {{opacity:0, y:12, scale:0.9}}, {{opacity:1, y:0, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {ti + 0.06:.3f});')
            if i + 1 < len(steps):
                X.tw(f'tl.to("{s} .ul-tag[data-i=\'{i}\']", {{opacity:0, duration:0.2}}, {max(steps[i + 1]["t"] - 0.3, ti + 0.4):.3f});')


FX = {"ui_lift": ui_lift}
