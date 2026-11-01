"""带原片字幕的素材 (footage that already carries burned-in subtitles or a speaker's own captions): the clip plays
full-bleed with a slow push; its subtitle band is detected from sampled frames (bright glyph edges in the top or
bottom strip) or given, and for this beat our captions — the beat's own line and the narration captions — move out
of that band so the two never sit on top of each other. Optional lower third and a dashed marker showing the band.

p: video (or image) · start · subs (auto | bottom | top | none; default auto) · show_band (draw the detected band) ·
   name / role (a lower third) · focus · zoom (start scale, 1.0; the push grows from the subtitle edge, so 1.1 crops
   a source's own top furniture while its bottom subtitles stay in frame)
Adapts: any source aspect (cover; a clip whose shape fights the frame plays as a card and the band is mapped into
it), subtitles at the top or bottom, no subtitles (nothing moves), 16:9 and 9:16 caption positions.
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
.fg-band { position:absolute; border:3px dashed #f6ce3a; border-radius:10px; }
.fg-band span { position:absolute; left:12px; top:-36px; font:800 22px var(--f-body); color:#111; background:#f6ce3a; padding:2px 10px; border-radius:5px; white-space:nowrap; }
.fg-l3 { position:absolute; display:flex; flex-direction:column; gap:4px; }
.fg-l3 b { font:900 40px var(--f-display); color:#fbfaf6; background:rgba(17,17,17,.82); padding:6px 16px; border-radius:6px; align-self:flex-start; }
.fg-l3 span { font:700 22px var(--f-mono, monospace); color:#111; background:#f6ce3a; padding:3px 12px; border-radius:5px; align-self:flex-start; }
.fg-vig { position:absolute; inset:0; background:radial-gradient(ellipse 80% 75% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45)); }
"""


def footage(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    src = p.get("video") or p.get("image")
    vid = bool(src) and fit.is_video(src)
    s0 = float(p.get("start", 0))
    ar = fit.aspect(X, src, 16 / 9) if src else 16 / 9
    m = 56 if P else 96
    card = max(ar / (W / H), (W / H) / ar) > 1.9
    if card:
        cw = (W - 2 * m) if ar > W / H else min(W * 0.46, (H - 360) * ar)
        ch = cw / ar
        cx, cy = (W - cw) / 2, (max(470, min((H - ch) / 2, 1250 - ch)) if P else (H - ch) / 2)
        rect = f"inset:auto; left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; border-radius:18px; box-shadow:0 30px 70px rgba(0,0,0,.35);"
    else:
        cx, cy, cw, ch, rect = 0, 0, W, H, ""
    band = p.get("subs", "auto")
    if band == "auto": band = A.subs_band(X, src, s0, d) if vid else None
    if band in ("none", None, False): band = None
    X.css("fx-footage", CSS)
    inner = ""
    if vid:
        _, vsel = fit.media(X, cid, "fv", src, t, d, "fg-v", fill="cover", z=2, start=s0, focus=p.get("focus"), extra_style=rect)
    else:
        mh, vsel = fit.media(X, cid, "fi", src, t, d, "fg-i", fill="cover" if card else "auto", focus=p.get("focus"), extra_style=rect) if src else ("", None)
        inner += mh
    if not card: inner += '<div class="fg-vig"></div>'
    if band and p.get("show_band"):
        f0, fh = A.band_box(ar < 1, band)
        by = cy + ch * f0
        lab = p.get("band_label", "原片字幕")
        X.used_text.update(lab)
        inner += f'<div class="fg-band" style="left:{cx + cw * 0.08:.0f}px; top:{by:.0f}px; width:{cw * 0.84:.0f}px; height:{ch * fh:.0f}px"><span>{X.rich(lab)}</span></div>'
    name, role = p.get("name", ""), p.get("role", "")
    if name:
        X.used_text.update(str(name) + str(role))
        ly = (cy + ch * 0.12) if band == "bottom" else (cy + ch * (0.62 if not P else 0.55))
        if not card: ly = (H * 0.30 if band == "bottom" else H * 0.66) if not P else (520 if band == "bottom" else 1080)
        inner += f'<div class="fg-l3" style="left:{(cx + 40) if card else m:.0f}px; top:{ly:.0f}px"><b>{X.rich(name)}</b>{f"<span>{X.rich(role)}</span>" if role else ""}</div>'
    _clip(X, cid, t, d, inner, p, transparent=vid)
    if card and vid: A.stage_bg(X, cid, t, d, p); A.scope(X, vsel, t, d)
    if not card: A.avoid_caps(X, cid, t, d, band)     # a card leaves our caption zone free already
    z0 = float(p.get("zoom", 1.0))
    S = f"#{cid}"
    if vsel:
        org = "50% 100%" if band == "bottom" else "50% 0%" if band == "top" else "50% 50%"     # push away from the subtitles, never over them
        X.tw(f'tl.fromTo("{vsel}", {{scale:{z0:.3f}, transformOrigin:"{org}"}}, {{scale:{z0 + 0.05:.3f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.from("{vsel}", {{opacity:0, duration:0.3}}, {t:.3f});')
    if band and p.get("show_band"):
        X.tw(f'tl.from("{S} .fg-band", {{opacity:0, scale:1.04, duration:0.4, ease:"expo.out"}}, {t + 0.5:.3f});')
        X.tw(f'tl.to("{S} .fg-band", {{opacity:0, duration:0.4}}, {t + min(d - 0.4, 2.6):.3f});')
    if name: X.tw(f'tl.from("{S} .fg-l3 > *", {{x:-30, opacity:0, duration:0.45, ease:"expo.out", stagger:0.1}}, {t + 0.4:.3f});')


FX = {"footage": footage}
