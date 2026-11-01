"""GIF 动图 (drop a GIF in like any picture): at build time the GIF (or an animated WebP) becomes an H.264 clip that
loops for the whole beat — transparency flattened onto the frame colour — and plays as properly timed media in a
sticker, phone or window frame, with its loop length tagged.

p: gif · frame ("sticker" | "phone" | "window" | "none") · caption · title · speed (1 = native) · focus · fit ("contain" | "cover")
Adapts: any GIF size / aspect / length (a 0.4 s loop or a 10 s clip; shorter than the beat → loops); transparent GIFs;
16:9 frame centred, 9:16 frame on top with the caption below. Needs ffmpeg (already required) and Pillow.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def gif_clip(X, cid, t, d, p):
    src = p.get("gif") or p.get("src")
    if not src: raise SystemExit("gif_clip needs `gif`")
    frame = p.get("frame", "sticker")
    col = D.colors(X, p)
    bg = "#111111" if frame == "phone" else "#fbfaf6"
    mp4, gw, gh, native = D.loop_mp4(X, src, d, bg=bg, speed=float(p.get("speed", 1.0)))
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title, caption = fit.as_text(p.get("title")), fit.as_text(p.get("caption"))
    tf = D.C.fitted(X, title, bw * 0.9, 110, 52 if P else 48, 24, max_lines=2) if title else None
    cf = D.C.fitted(X, caption, bw * 0.86, 100, 40, 22, max_lines=2) if caption else None
    top = (tf.n * tf.px * 1.12 + 28) if tf else 0
    bot = (cf.n * cf.px * 1.25 + 28) if cf else 0
    ar = gw / gh
    pad = {"sticker": 12, "phone": 16, "window": 0, "none": 0}.get(frame, 12)
    bar = 40 if frame == "window" else 0
    if frame == "phone":
        if ar > 1.15:                                   # landscape GIF: the phone lies on its side
            ar_f = 19.5 / 9
            fw = min(bw * (0.8 if not P else 0.94), (bh - top - bot) * ar_f); fh = fw / ar_f
        else:
            ar_f = 9 / 19.5
            fh = min(bh - top - bot, (bw * 0.5) / ar_f); fw = fh * ar_f
    else:
        avail_w, avail_h = bw * (0.78 if not P else 0.94), bh - top - bot - bar
        fw = min(avail_w, avail_h * ar); fh = fw / ar
        fw += 2 * pad; fh += 2 * pad
    fx = x0 + (bw - fw) / 2
    fy = y0 + top + (bh - top - bot - fh - bar) / 2 + bar
    vx, vy, vw, vh = fx + pad, fy + pad, fw - 2 * pad, fh - 2 * pad
    radius = {"sticker": 6, "phone": 34, "window": 0, "none": 10}.get(frame, 6)
    style = (f"inset:auto; left:{vx:.1f}px; top:{vy:.1f}px; width:{vw:.1f}px; height:{vh:.1f}px; border-radius:{max(0, radius - 4)}px;"
             f" background:{bg}; visibility:hidden")
    fitmode = p.get("fit", "contain" if frame != "phone" else "cover")
    _, vsel = fit.media(X, cid, "gif", str(mp4), t, d, "gf-v", focus=p.get("focus"), fill="cover", z=4, extra_style=style)
    X.tw(f'tl.set("{vsel} video", {{objectFit:"{fitmode}"}}, {t:.3f});')
    X.tw(f'tl.set("{vsel}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.set("{vsel}", {{visibility:"hidden"}}, {t + d:.3f});')
    chrome = {"sticker": f'<div class="gf-fr gf-st" style="left:{fx:.1f}px; top:{fy:.1f}px; width:{fw:.1f}px; height:{fh:.1f}px"></div>',
              "phone": f'<div class="gf-fr gf-ph" style="left:{fx:.1f}px; top:{fy:.1f}px; width:{fw:.1f}px; height:{fh:.1f}px"></div>',
              "window": f'<div class="gf-fr gf-win" style="left:{fx:.1f}px; top:{fy - bar:.1f}px; width:{fw:.1f}px; height:{fh + bar:.1f}px"><i></i><i></i><i></i></div>',
              "none": ""}.get(frame, "")
    tag = f"GIF · {native:.1f} 秒循环" if native < d else f"GIF · {native:.1f} 秒"
    X.used_text.update(tag + title + caption)
    tag_html = f'<div class="d2-tag gf-tag" style="left:{fx:.0f}px; top:{fy - bar - 40:.0f}px">{X.rich(tag)}</div>'
    head = f'<div class="d2-ttl gf-ttl" style="left:{x0}px; top:{y0}px; width:{bw}px; text-align:center; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else ""
    cap = f'<div class="gf-cap" style="left:{x0}px; width:{bw}px; top:{fy + fh + 22:.0f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>' if cf else ""
    X.css("fx-d2", D.CSS)
    X.css("fx-gif", """
.gf-fr { position:absolute; }
.gf-st { background:#fbfaf6; border-radius:6px; box-shadow:0 2px 0 rgba(0,0,0,.08), 0 24px 56px rgba(0,0,0,.3); }
.gf-ph { background:#111; border-radius:38px; box-shadow:0 0 0 3px #2a2a2a, 0 30px 70px rgba(0,0,0,.4); }
.gf-win { background:color-mix(in srgb, var(--fg) 10%, var(--bg)); border-radius:12px 12px 4px 4px; box-shadow:0 24px 60px rgba(0,0,0,.28); }
.gf-win i { position:absolute; top:14px; width:12px; height:12px; border-radius:50%; background:color-mix(in srgb, var(--fg) 30%, transparent); }
.gf-win i:nth-child(1) { left:16px; } .gf-win i:nth-child(2) { left:36px; } .gf-win i:nth-child(3) { left:56px; }
.gf-cap { position:absolute; text-align:center; font-family:var(--f-body); font-weight:800; color:var(--fg); line-height:1.25; }
""")
    _clip(X, cid, t, d, f'<div class="d2 gf">{head}{chrome}{tag_html}{cap}</div>', p)
    S = f"#{cid}"
    if chrome: X.tw(f'tl.from("{S} .gf-fr", {{y:60, opacity:0, duration:0.55, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{vsel}", {{y:60, opacity:0, duration:0.55, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{S} .gf-tag", {{opacity:0, x:-16, duration:0.4, ease:"power3.out"}}, {t + 0.4:.3f});')
    if tf: X.tw(f'tl.from("{S} .gf-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    if cf: X.tw(f'tl.from("{S} .gf-cap .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.45:.3f});')
    X.sfx(t + 0.05, "pop")
    hold = t + 0.7
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .gf-fr, {vsel}", {{y:-10, duration:{t + d - hold:.2f}, ease:"sine.inOut"}}, {hold:.3f});')


FX = {"gif_clip": gif_clip}
