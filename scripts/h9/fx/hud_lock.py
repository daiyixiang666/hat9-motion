"""HUD 目标锁定 (#17 HUD, Quantum HUD Infographic 5.9K — Infographics 第 1): over a photo, four brackets fly in
from the frame corners and close on the subject, crosshairs extend, a dashed ring spins up, the surround dims,
and a monospaced readout types itself beside the box; a LOCK tag blinks on twos.

Adapts: a still ("image", any aspect — cover-cropped; "v": {x,y,w,h,ox} re-aims the box for the portrait crop),
footage ("video") or nothing (a dark HUD grid); a title from a word to a phrase (fitted) and 0–8 readout lines
(type size steps down with the count); the readout flips to whichever side of the box has room.
p: image | video · x y w h (box, % of frame) · v · text · readouts · video_start"""
from h9 import aefx
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]

aefx.PHOTO.add("hud_lock")     # photo page: header/footer switch to the light-on-photo treatment


def hud_lock(X, cid, t, d, p):
    x, y, w, h = (float(p.get(k, v)) for k, v in (("x", 40), ("y", 35), ("w", 22), ("h", 30)))
    ox = 50
    if X.portrait and p.get("v"):        # portrait crops the photo: give the box (and where the crop sits, ox %) separately
        pv = p["v"]; x, y, w, h = (float(pv.get(k, v)) for k, v in (("x", x), ("y", y), ("w", w), ("h", h))); ox = float(pv.get("ox", 50))
    reads = p.get("readouts", [])
    X.css("fx-hud", """
.fx .hli { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .hlb { position:absolute; }
.fx .hlb .hdim { position:absolute; inset:0; box-shadow:0 0 0 300vmax rgba(0,0,0,.5); }
.fx .hlb i.k { position:absolute; width:4.2vmin; height:4.2vmin; border:.45vmin solid var(--hud, #f6ce3a); }
.fx .hlb i.k:nth-of-type(1) { left:-.6vmin; top:-.6vmin; border-right:0; border-bottom:0; } .fx .hlb i.k:nth-of-type(2) { right:-.6vmin; top:-.6vmin; border-left:0; border-bottom:0; }
.fx .hlb i.k:nth-of-type(3) { left:-.6vmin; bottom:-.6vmin; border-right:0; border-top:0; } .fx .hlb i.k:nth-of-type(4) { right:-.6vmin; bottom:-.6vmin; border-left:0; border-top:0; }
.fx .hlb .hx, .fx .hlb .vx { position:absolute; background:var(--hud, #f6ce3a); opacity:.75; }
.fx .hlb .hx { top:50%; height:.18vmin; left:-14vmin; right:-14vmin; } .fx .hlb .vx { left:50%; width:.18vmin; top:-10vmin; bottom:-10vmin; }
.fx .hlb svg { position:absolute; left:50%; top:50%; width:24vmin; height:24vmin; margin:-12vmin 0 0 -12vmin; overflow:visible; }
.fx .hlb svg circle { fill:none; stroke:var(--hud, #f6ce3a); stroke-width:.35; }
.fx .hlb .hlk { position:absolute; left:0; top:-4.6vmin; font:700 1.9vmin var(--f-mono, monospace); color:#111; background:var(--hud, #f6ce3a); padding:.3vmin 1vmin; letter-spacing:.18em; }
.fx .hlr { position:absolute; font-family:var(--f-mono, monospace); font-weight:500; line-height:1.75; color:#fff; letter-spacing:.06em; text-shadow:0 .2vmin 1vmin rgba(0,0,0,.8); white-space:nowrap; }
.fx .hlr b { display:block; font-family:var(--f-display); font-weight:900; line-height:1.15; letter-spacing:0; margin-bottom:.8vmin; } .fx .hlr b .fl { display:block; white-space:nowrap; }
.fx .hgrid { background:radial-gradient(ellipse at 50% 45%, #1d2228, #0b0d10 70%), #0b0d10; } .fx .hgrid::after { content:''; position:absolute; inset:0; background-image:linear-gradient(rgba(246,206,58,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(246,206,58,.08) 1px, transparent 1px); background-size:6vmin 6vmin; }
.fx .hlr .c { opacity:1; }
.fx .hls { position:absolute; left:0; right:0; top:0; height:.3vmin; background:linear-gradient(90deg, transparent, var(--hud, #f6ce3a), transparent); opacity:.6; }
""")
    rx = x + w + 3 if x + w + 30 < 100 else x - 3
    side = "left" if x + w + 30 < 100 else "right"
    pos = f"left:{rx}%" if side == "left" else f"right:{100 - rx}%"
    if X.portrait: pos = f"left:{max(5, x - 2)}%"; rtop = f"top:{max(14, y - 15)}%"
    else: rtop = f"top:{y}%"
    reads = reads[:8]
    rs = 2.1 if len(reads) <= 4 else 1.8 if len(reads) <= 6 else 1.55
    room = (100 - (x + w) - 5) if side == "left" else (x - 5)
    Wv, Hv = F.frame_vmin(X)
    tw_ = max(16.0, (room / 100 * Wv) if not X.portrait else Wv * 0.8)
    ts, tl_ = F.fit(p.get("text", ""), tw_, 12, 4.4, 2.4, 2)
    rows = "".join(f'<div>{"".join(f"<i class=c>{X.rich(ch)}</i>" if ch.strip() else " " for ch in r)}</div>' for r in reads)
    if p.get("image"): bg = f'<img class="hli" src="{X.asset(p["image"])}" alt="" style="object-position:{ox}% 50%">'
    elif p.get("video"): bg = ""
    else: bg = '<div class="hli hgrid"></div>'
    inner = (f'{bg}<div class="hls"></div>'
             f'<div class="hlb" style="left:{x}%; top:{y}%; width:{w}%; height:{h}%"><div class="hdim"></div><div class="hx"></div><div class="vx"></div>'
             f'<i class="k"></i><i class="k"></i><i class="k"></i><i class="k"></i>'
             f'<svg viewBox="-50 -50 100 100"><circle r="46" stroke-dasharray="6 4"/><circle r="40" stroke-dasharray="1 3"/></svg><div class="hlk">LOCK</div></div>'
             f'<div class="hlr" style="{pos}; {rtop}; font-size:{rs:.2f}vmin"><b style="font-size:{ts:.2f}vmin">{F.lines_html(X, tl_)}</b>{rows}</div>')
    X.used_text.update("LOCK")
    if p.get("video") and not p.get("image"):
        vsel = F.video_bg(X, cid, t, d, p["video"], p.get("video_start", 0))
        _clip(X, cid, t, d, inner, F.no_bg(p))
        X.tw(f'tl.fromTo("{vsel}", {{scale:1.02}}, {{scale:1.1, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    else:
        _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .hli", {{scale:1.04}}, {{scale:1.12, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .hls", {{y:0}}, {{y:{X.H}, duration:1.2, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .hls", {{opacity:0, duration:0.2}}, {t + 1.1:.3f});')
    for k, (dx, dy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        X.tw(f'tl.from("{s} .hlb i.k:nth-of-type({k + 1})", {{x:"{dx * 40}vmin", y:"{dy * 30}vmin", opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.15 + k * 0.04:.3f});')
    X.tw(f'tl.from("{s} .hlb .hx", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {t + 0.45:.3f});')
    X.tw(f'tl.from("{s} .hlb .vx", {{scaleY:0, duration:0.5, ease:"expo.out"}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .hlb svg", {{scale:2.2, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.4:.3f});')
    X.tw(f'tl.fromTo("{s} .hlb svg", {{rotation:0}}, {{rotation:140, duration:{d:.2f}, ease:"power1.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hlb .hdim", {{opacity:0, duration:0.5}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("{s} .hlb .hlk", {{opacity:0, duration:0.01, repeat:5, yoyo:true, ease:"steps(1)"}}, {t + 0.8:.3f});')
    X.tw(f'tl.from("{s} .hlr b", {{x:-20, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.85:.3f});')
    nch = max(1, sum(len(r) for r in reads))
    X.tw(f'tl.from("{s} .hlr .c", {{opacity:0, duration:0.01, stagger:{min(0.025, max(0.004, (d - 1.4) / nch)):.4f}, ease:"none"}}, {t + 1.05:.3f});')
    X.sfx(t + 0.15, "whoosh_soft"); X.sfx(t + 0.8, "beep"); X.sfx(t + 1.05, "type")


FX = {"hud_lock": hud_lock}
