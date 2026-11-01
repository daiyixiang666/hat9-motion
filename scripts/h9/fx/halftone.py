"""低清图做成风格 (a small or blurry picture made intentional: halftone dots, duotone, or a two-ink riso print).
The tiny original shows first, honestly pixelated with its real size tagged; a scan bar then sweeps across and the
same picture comes back as print — the softness becomes texture instead of a flaw.

p: image · mode ("halftone" | "duotone" | "riso") · ink / paper / ink2 (hex; default the beat's theme fg / bg / accent) ·
   cell (dot pitch in px of the output; default by size) · title · kicker · at ("@词" / seconds for the sweep)
Adapts: any size from ~60 px wide (the smaller, the coarser the screen) and any aspect (cover-fitted in the box, focus
from `focus`); grey or colour input; 16:9 and 9:16. Processing happens once at build time (Pillow + numpy).
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def _print(X, src, mode, ink, paper, ink2, cell, out_w):
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    a = fit._abs(X, src)
    f, url = D.cache(X, f"{a}|{a.stat().st_mtime}|{mode}|{ink}|{paper}|{ink2}|{cell}|{out_w}", "png")
    with Image.open(a) as im0:
        im0 = im0.convert("RGB"); w0, h0 = im0.size
    if f.exists(): return url, (w0, h0)
    W = out_w; H = round(W * h0 / w0)
    g = im0.convert("L").resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(cell * 0.18))
    L = np.asarray(g, dtype=np.float32) / 255.0
    L = np.clip((L - L.min()) / max(1e-3, L.max() - L.min()), 0, 1)       # stretch: low-res frames are usually flat
    P, I, I2 = D.hexrgb(paper), D.hexrgb(ink), D.hexrgb(ink2)

    def dots(img, col, pitch, gain=1.0, dx=0.0, dy=0.0):
        dr = ImageDraw.Draw(img)
        r_max = pitch * 0.62
        y = pitch / 2; row = 0
        while y < H + pitch:
            x = pitch / 2 + (pitch / 2 if row % 2 else 0)
            while x < W + pitch:
                lx, ly = min(W - 1, max(0, int(x))), min(H - 1, max(0, int(y)))
                dark = (1 - L[ly, lx]) ** 0.9 * gain
                r = r_max * dark ** 0.5
                if r > 0.35: dr.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=col)
                x += pitch
            y += pitch * 0.866; row += 1

    if mode == "duotone":
        t = L[..., None] ** 0.9
        arr = (np.array(I) * (1 - t) + np.array(P) * t)
        noise = np.random.default_rng(7).normal(0, 6, arr.shape[:2])[..., None]
        out = Image.fromarray(np.clip(arr + noise, 0, 255).astype("uint8"))
    elif mode == "riso":
        base = Image.new("RGB", (W, H), P)
        a1 = Image.new("RGB", (W, H), (255, 255, 255)); dots(a1, I2, cell * 1.15, 1.0, 0, 0)
        a2 = Image.new("RGB", (W, H), (255, 255, 255)); dots(a2, I, cell * 0.9, 0.85, cell * 0.22, cell * 0.16)
        m = (np.asarray(base, dtype=np.float32) * np.asarray(a1, dtype=np.float32) / 255 * np.asarray(a2, dtype=np.float32) / 255)
        out = Image.fromarray(np.clip(m, 0, 255).astype("uint8"))
    else:
        out = Image.new("RGB", (W, H), P); dots(out, I, cell)
    out.save(f)
    return url, (w0, h0)


def halftone(X, cid, t, d, p):
    src = p.get("image") or p.get("src")
    if not src: raise SystemExit("halftone needs `image`")
    col = D.colors(X, p)
    mode = p.get("mode", "halftone")
    ink, paper, ink2 = p.get("ink", col["fg"]), p.get("paper", col["card"] if mode != "duotone" else col["bg"]), p.get("ink2", col["accent"])
    lum = lambda h: sum(c * k for c, k in zip(D.hexrgb(h), (0.2126, 0.7152, 0.0722))) / 255
    if abs(lum(ink) - lum(paper)) < 0.4: ink = "#151515" if lum(paper) > 0.5 else "#f4f1ea"
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    title = fit.as_text(p.get("title"))
    tf = D.C.fitted(X, title, (x1 - x0) * (0.9 if P else 0.6), 120, 56 if P else 52, 26, max_lines=2) if title else None
    fh = (y1 - y0) - ((tf.n * tf.px * 1.12 + 30) if (tf and P) else 0)
    fw = x1 - x0
    a = fit._abs(X, src)
    sz = fit.size(a) or (320, 180)
    ar_i, ar_b = sz[0] / sz[1], fw / fh
    fx0, fy0 = x0, y0
    if ar_i > ar_b * 1.6:                               # a strip: frame follows the picture, centred in the box
        nh = fw / ar_i; fy0 = y0 + (fh - nh) / 2; fh = nh
    elif ar_i < ar_b / 1.6:
        nw = fh * ar_i; fx0 = x0 + (fw - nw) / 2; fw = nw
    cell = int(p.get("cell") or max(9, round(1500 / 110)))
    out_w = 1500
    purl, _ = _print(X, src, mode, ink, paper, ink2, cell, out_w)
    lurl = X.asset(src)
    pos = fit.focus_css(p.get("focus"))
    tag0 = f"原图 {sz[0]}×{sz[1]} px"
    tag1 = {"halftone": "网点 · HALFTONE", "duotone": "双色 · DUOTONE", "riso": "孔版 · RISO"}.get(mode, mode)
    X.used_text.update(tag0 + tag1 + str(p.get("kicker", "")) + title)
    ttl_y = fy0 + fh + 24 if P else None
    head = ""
    if tf:
        if P: head = f'<div class="d2-ttl" style="left:{x0}px; top:{ttl_y:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>'
        else: head = f'<div class="d2-ttl ht-ttl" style="left:{fx0 + 36}px; bottom:{X.H - (fy0 + fh) + 36:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>'
    kick = f'<div class="d2-kick" style="left:{fx0 + 24}px; top:{fy0 + 24}px">{X.rich(p["kicker"])}</div>' if p.get("kicker") else ""
    frame = (f'<div class="ht-f" style="left:{fx0:.0f}px; top:{fy0:.0f}px; width:{fw:.0f}px; height:{fh:.0f}px">'
             f'<div class="ht-cam"><img class="ht-lo" src="{lurl}" alt="" style="object-position:{pos}"><img class="ht-pr" src="{purl}" alt="" style="object-position:{pos}"></div>'
             f'<i class="ht-bar"></i><div class="d2-tag ht-t0" style="right:20px; top:20px">{X.rich(tag0)}</div><div class="d2-tag ht-t1" style="right:20px; top:20px">{X.rich(tag1)}</div></div>')
    X.css("fx-d2", D.CSS)
    X.css("fx-halftone", """
.ht-f { position:absolute; overflow:hidden; border-radius:12px; background:#111; box-shadow:0 20px 60px rgba(0,0,0,.25); }
.ht-cam { position:absolute; inset:0; }
.ht-cam img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.ht-lo { image-rendering:pixelated; }
.ht-pr { clip-path:inset(0 100% 0 0); }
.ht-bar { position:absolute; top:0; bottom:0; left:0; width:6px; margin-left:-3px; background:#fbfaf6; box-shadow:0 0 30px 8px rgba(255,255,255,.55); opacity:0; }
.ht-t1 { opacity:0; }
.ht-ttl { color:#fbfaf6; text-shadow:0 2px 18px rgba(0,0,0,.55); }
""")
    _clip(X, cid, t, d, f'<div class="d2 ht">{frame}{kick}{head}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .ht-f", {{opacity:0, scale:0.97, duration:0.5, ease:"power3.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{S} .ht-cam", {{scale:1.02}}, {{scale:1.1, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    ts = D.times(X, p, t, d, 1, key="at", lead=min(1.1, d * 0.32))[0]
    sw = min(1.1, max(0.6, d * 0.22))
    X.tw(f'tl.fromTo("{S} .ht-pr", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{sw:.2f}, ease:"power2.inOut"}}, {ts:.3f});')
    X.tw(f'tl.fromTo("{S} .ht-bar", {{x:0, opacity:1}}, {{x:{fw:.0f}, duration:{sw:.2f}, ease:"power2.inOut"}}, {ts:.3f});')
    X.tw(f'tl.to("{S} .ht-bar", {{opacity:0, duration:0.15}}, {ts + sw:.3f});')
    X.tw(f'tl.to("{S} .ht-t0", {{opacity:0, duration:0.2}}, {ts + sw * 0.5:.3f});')
    X.tw(f'tl.to("{S} .ht-t1", {{opacity:1, duration:0.25}}, {ts + sw * 0.6:.3f});')
    X.sfx(ts, "whoosh_soft")
    if tf: X.tw(f'tl.from("{S} .d2-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {ts + sw * 0.7:.3f});')
    if p.get("kicker"): X.tw(f'tl.from("{S} .d2-kick", {{opacity:0, y:-10, duration:0.4}}, {t + 0.2:.3f});')


FX = {"halftone": halftone}
