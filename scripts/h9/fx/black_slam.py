"""黑屏重击 Black Slam (MrBeast / Johnny Harris 式的黑场冲击字；AE 的 impact frame + camera shake；纪录片的黑场金句):
the page cuts to black; one white impact frame flashes, the line slams down out of a motion blur and the whole
frame takes a decaying shake; the *keyword* gets a hard accent bar; a small second line types underneath. With
hits, each word slams in on its own beat on the black, the last one stays.

Adapts: a word to ~40 glyphs (≤ 3 lines in 16:9, 4 in 9:16, fitted large), 0–8 hit words, sub any length (1–2 lines); works on any
theme (the black is its own ground, the theme only picks the accent bar); emoji and traditional Chinese measured
like any text. While the last word holds, outlines pulse out of it so the black never freezes.
p: text (*keyword* marked) · sub · hits · at
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit

CSS = """
.fx .bs { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .bs .bs-bg { position:absolute; inset:0; background:#050505; }
.fx .bs .bs-flash { position:absolute; inset:0; background:#ffffff; opacity:0; }
.fx .bs .bs-t { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; color:#f7f4ee; line-height:1.06; letter-spacing:-.01em; }
.fx .bs .bs-t .sl { display:block; white-space:nowrap; }
.fx .bs .bs-t .em .emb { left:-.06em; right:-.06em; bottom:.04em; top:auto; height:.2em; background:var(--bs-acc, #e2321f); transform-origin:0 50%; }
.fx .bs .bs-t .em .emt { position:relative; z-index:1; }
.fx .bs .bs-h { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; color:#f7f4ee; white-space:nowrap; opacity:0; }
.fx .bs .bs-s { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-mono, monospace); font-weight:500; color:rgba(247,244,238,.62); letter-spacing:.08em; }
.fx .bs .bs-gh { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; line-height:1.06; color:transparent;
  -webkit-text-stroke:.35vmin rgba(247,244,238,.8); white-space:nowrap; opacity:0; pointer-events:none; }
.fx .bs .bs-vig { position:absolute; inset:0; background:radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 45%, rgba(0,0,0,.75) 100%); }
"""


def black_slam(X, cid, t, d, p):
    P = X.portrait
    p = dict(p)
    acc = {"paper": "#e2321f", "red": "#e2321f", "lemon": "#f6ce3a", "ink": "#f6ce3a"}.get(p.get("theme") or "ink", "#e2321f")
    p["theme"] = "ink"      # the page is always black: the asked-for theme only picks the accent bar
    text = fit.as_text(p.get("text") or "")
    hits = [fit.as_text(h_) for h_ in fit.as_list(p.get("hits"))][:8]
    sub = fit.as_text(p.get("sub"))
    x, y, w, h = S.box(X, p)
    X.css("fx-bs", CSS)
    html = ['<div class="bs-bg"></div>']
    tf = fit.fit_text(text or (hits[-1] if hits else "！"), w * 0.92, h * 0.5, S.vm(X, 20 if P else 17), S.vm(X, 5), max_lines=4 if P else 3, lh=1.06)
    th = tf.n * tf.px * 1.06
    sp = S.vm(X, 3.0)
    sub_h = sp * 1.5 * 2 if sub else 0
    ty = y + (h - th - sub_h) / 2
    if hits:
        for k, hw in enumerate(hits):
            hf = fit.fit_text(hw, w * 0.9, h * 0.4, S.vm(X, 22 if P else 19), S.vm(X, 6), max_lines=1)
            html.append(f'<div class="bs-h" data-k="{k}" style="top:{y + (h - hf.px) / 2:.0f}px; font-size:{hf.px}px">{X.rich(hf.lines[0])}</div>')
    if text:
        html.append(f'<div class="bs-t" style="top:{ty:.0f}px; font-size:{tf.px}px; --bs-acc:{acc}; opacity:0">' + "".join(f'<span class="sl">{X.rich(l)}</span>' for l in tf.lines) + "</div>")
    # the word that stays sends out slow shockwave outlines, so the hold keeps breathing
    if text:
        html.append(f'<div class="bs-gh" data-layout-allow-overlap aria-hidden="true" style="top:{ty:.0f}px; font-size:{tf.px}px">' + "<br>".join(X.rich(l) for l in tf.lines) + "</div>")
    elif hits:
        html.append(f'<div class="bs-gh" data-layout-allow-overlap aria-hidden="true" style="top:{y + (h - hf.px) / 2:.0f}px; font-size:{hf.px}px">{X.rich(hf.lines[0])}</div>')
    if sub:
        sf = fit.fit_text(sub, w * 0.86, sp * 1.5 * 2, sp, S.vm(X, 2.6), max_lines=2, lh=1.5)
        html.append(f'<div class="bs-s" style="top:{ty + th + S.vm(X, 3):.0f}px; font-size:{sf.px}px">' + "<br>".join(X.rich(l) for l in sf.lines) + "</div>")
    html.append('<div class="bs-vig"></div><div class="bs-flash"></div>')
    _clip(X, cid, t, d, f'<div class="bs">{"".join(html)}</div>', p)
    s = f"#{cid} .bs"
    at = fit.as_list(p.get("at"))
    tl_ = []
    if at and X.chars:
        try: tl_ = [float(X.T(c, t)) for c in at]
        except SystemExit: tl_ = []
    n = len(hits)
    hit_t = tl_[:n] if len(tl_) >= n and n else [t + 0.15 + k * min(0.42, d * 0.5 / max(n, 1)) for k in range(n)]
    slam_t = (tl_[n] if len(tl_) > n else (hit_t[-1] + 0.45 if n else t + 0.12)) if text else None

    def impact(at_, big=True):
        X.tw(f'tl.fromTo("{s} .bs-flash", {{opacity:{0.9 if big else 0.45}}}, {{opacity:0, duration:{0.14 if big else 0.08}, ease:"power2.out", immediateRender:false}}, {at_:.3f});')
        amp = S.vm(X, 1.6 if big else 0.8)
        X.tw(f'tl.fromTo("{s}", {{x:0, y:0}}, {{keyframes:[{{x:{-amp:.0f}, y:{amp * 0.6:.0f}, duration:0.04}}, {{x:{amp * 0.8:.0f}, y:{-amp * 0.5:.0f}, duration:0.04}}, '
             f'{{x:{-amp * 0.5:.0f}, y:{amp * 0.3:.0f}, duration:0.05}}, {{x:{amp * 0.25:.0f}, y:0, duration:0.06}}, {{x:0, y:0, duration:0.08}}], immediateRender:false}}, {at_:.3f});')
        X.sfx(at_, "slam")
    for k, tk in enumerate(hit_t):
        sel = f'{s} .bs-h[data-k=\'{k}\']'
        if k: X.tw(f'tl.set("{s} .bs-h[data-k=\'{k - 1}\']", {{opacity:0}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{sel}", {{opacity:1, scale:2.4, filter:"blur(14px)"}}, {{scale:1, filter:"blur(0px)", duration:0.16, ease:"power4.out", immediateRender:false}}, {tk:.3f});')
        impact(tk, big=(k == n - 1 and not text))
    if text:
        if n: X.tw(f'tl.set("{s} .bs-h[data-k=\'{n - 1}\']", {{opacity:0}}, {slam_t:.3f});')
        X.tw(f'tl.fromTo("{s} .bs-t", {{opacity:1, scale:2.6, filter:"blur(22px)"}}, {{scale:1, filter:"blur(0px)", duration:0.18, ease:"power4.out", immediateRender:false}}, {slam_t:.3f});')
        impact(slam_t)
        X.tw(f'tl.fromTo("{s} .bs-t .em .emb", {{scaleX:0}}, {{scaleX:1, duration:0.3, ease:"power3.out", immediateRender:false}}, {slam_t + 0.25:.3f});')
        X.tw(f'tl.set("{s} .bs-t .em .emb", {{scaleX:0}}, {t:.3f});')
        X.tw(f'tl.to("{s} .bs-t", {{scale:{1.05 if sub else 1.1}, duration:{max(0.3, t + d - slam_t - 0.3):.2f}, ease:"none"}}, {slam_t + 0.25:.3f});')
    stay = slam_t if text else (hit_t[-1] if hit_t else None)
    if stay is not None:
        k, tp = 0, stay + 0.7
        while tp + 1.0 <= t + d - 0.2 and k < 6:
            X.tw(f'tl.fromTo("{s} .bs-gh", {{opacity:0.5, scale:1}}, {{opacity:0, scale:1.32, duration:1.0, ease:"power2.out", immediateRender:false}}, {tp:.3f});')
            k, tp = k + 1, tp + 1.15
    if sub:
        ts = (slam_t or (hit_t[-1] if hit_t else t)) + 0.45
        X.tw(f'tl.fromTo("{s} .bs-s", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.6, ease:"steps({max(6, min(30, len(sub)))})", immediateRender:false}}, {ts:.3f});')
        X.tw(f'tl.set("{s} .bs-s", {{clipPath:"inset(0 100% 0 0)"}}, {t:.3f});')


FX = {"black_slam": black_slam}
