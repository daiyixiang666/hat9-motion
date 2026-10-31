"""文字镂空透视频 Video Inside Text (SonduckFilm「5 Quick Text Effects」76.7 万播放；Mixkit「Video Mask Title」):
a huge word filled with the footage, the picture drifting inside the letters; then the word punches forward and
opens up until the footage fills the frame.

Adapts: words from 1 glyph to a short sentence (size fitted, ≤ 2 balanced lines, breaks between words); 0 images
(an accent gradient fills the letters, no punch-through), 1 image, or 2–12+ images that cut inside the letters on
a steady rhythm before the last one opens up. p: text · sub · image | images
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


def text_mask(X, cid, t, d, p):
    imgs = [X.asset(u) for u in (p.get("images") or ([p["image"]] if p.get("image") else []))]
    Wv, Hv = F.frame_vmin(X)
    size, lines = F.fit(p["text"], Wv * 0.86, Hv * (0.42 if X.portrait else 0.6), 34.0, 8.0, 2, lh=1.0)
    X.css("fx-tm", """
.fx .tmw { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; flex-direction:column; }
.fx .tmb { position:relative; }
.fx .tmt { font-family:var(--f-display); font-weight:900; line-height:1; letter-spacing:-.04em; color:transparent; -webkit-background-clip:text; background-clip:text;
  background-size:cover; background-position:50% 50%; padding:0 .04em; text-align:center; filter:drop-shadow(0 1vmin 3vmin color-mix(in srgb, var(--fg) 22%, transparent)); }
.fx .tmt .fl { display:block; white-space:nowrap; }
.fx .tmt + .tmt { position:absolute; inset:0; }
.fx .tmt.grad { background-image:linear-gradient(120deg, var(--accent), color-mix(in srgb, var(--accent) 40%, var(--fg))); }
.fx .tms { margin-top:2.6vmin; font:700 2.6vmin var(--f-body); letter-spacing:.42em; color:var(--muted); text-transform:uppercase; }
.fx .tmf { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; }
""")
    txt = F.lines_html(X, lines)
    if imgs:
        layers = "".join(f'<div class="tmt" data-k="{k}" style="font-size:{size:.2f}vmin; background-image:url({u})">{txt}</div>' for k, u in enumerate(imgs))
        full = f'<img class="tmf" src="{imgs[-1]}" alt="">'
    else:
        layers = f'<div class="tmt grad" style="font-size:{size:.2f}vmin">{txt}</div>'; full = ""
    inner = f'{full}<div class="tmw"><div class="tmb">{layers}</div><div class="tms">{X.rich(p.get("sub", ""))}</div></div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .tmb", {{scale:1.25, opacity:0, filter:"blur(14px)", duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .tmt", {{backgroundPosition:"30% 50%"}}, {{backgroundPosition:"70% 50%", duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .tms", {{y:16, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.35:.3f});')
    tp = t + d * 0.62
    n = len(imgs)
    if n > 1:                                  # cut through the pictures inside the letters, on a steady beat
        beat = max(0.12, (tp - (t + 0.5)) / n)
        for k in range(n):
            X.tw(f'tl.set("{s} .tmt[data-k=\'{k}\']", {{opacity:{1 if k == 0 else 0}}}, {t:.3f});')
        for k in range(1, n):
            X.tw(f'tl.set("{s} .tmt[data-k=\'{k}\']", {{opacity:1}}, {t + 0.5 + k * beat:.3f});')
            X.sfx(t + 0.5 + k * beat, "click")
    if not imgs:
        X.tw(f'tl.to("{s} .tmb", {{scale:1.06, duration:{d * 0.6:.2f}, ease:"sine.inOut"}}, {t + 0.75:.3f});')
        return
    X.tw(f'tl.to("{s} .tms", {{opacity:0, duration:0.2}}, {tp - 0.1:.3f});')
    X.tw(f'tl.to("{s} .tmb", {{scale:9, duration:0.75, ease:"power3.in"}}, {tp:.3f});')
    X.tw(f'tl.to("{s} .tmf", {{opacity:1, duration:0.3}}, {tp + 0.45:.3f});')
    X.tw(f'tl.to("{s} .tmb", {{opacity:0, duration:0.25}}, {tp + 0.45:.3f});')
    X.tw(f'tl.fromTo("{s} .tmf", {{scale:1.15}}, {{scale:1.0, duration:{max(0.5, d - (tp + 0.45 - t)):.2f}, ease:"expo.out", immediateRender:false}}, {tp + 0.45:.3f});')
    X.sfx(t + 0.05, "whoosh_soft"); X.sfx(tp, "whoosh_deep")


FX = {"text_mask": text_mask}
