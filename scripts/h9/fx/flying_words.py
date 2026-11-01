"""关键词飞过镜头 Flying Words (VideoHive "3D Fly-through Titles"；Element 3D 的 text fly-through；MV 歌词飞字):
the camera travels forward through a field of words: each keyword starts deep in the frame, small and soft,
rushes toward the lens and passes it off-centre; depth specks stream by for speed; the last word does not pass —
it decelerates into the centre, sharpens and gets an accent rule.

Adapts: 2–14 words of any length (emoji, Latin, traditional Chinese); flight time shares the beat (a long beat
flies slower, a short one tighter); words land on "at" cues when given; the final word fitted to ≤ 2 lines.
p: words · final (index, default last) · sub · at
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
.fx .fw { position:absolute; left:0; top:0; width:100%; height:100%; perspective:900px; perspective-origin:50% 50%; overflow:hidden; }
.fx .fw .fw-w, .fx .fw .fw-f { position:absolute; left:50%; top:50%; white-space:nowrap; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.05; text-align:center; }
.fx .fw .fw-f .sl { display:block; white-space:nowrap; }
.fx .fw .fw-rule { position:absolute; height:.7vmin; background:var(--accent); transform-origin:50% 50%; }
.fx .fw .fw-sub { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-body); font-weight:600; color:var(--muted); letter-spacing:.06em; }
.fx .fw .fw-sp { position:absolute; left:50%; top:50%; width:.45vmin; height:2.4vmin; border-radius:.3vmin; background:var(--fg); transform-origin:50% 50%; }
"""


def flying_words(X, cid, t, d, p):
    P = X.portrait
    words = [fit.as_text(w) for w in fit.as_list(p.get("words") or p.get("items"))][:14] or ["关键词"]
    fi = p.get("final")
    fi = fi if isinstance(fi, int) and 0 <= fi < len(words) else len(words) - 1
    sub = fit.as_text(p.get("sub"))
    x, y, w, h = S.box(X, p)
    cx, cy = x + w / 2, y + h / 2
    dx, dy = cx - X.W / 2, cy - X.H / 2         # the flight centre is the free area's centre, not the frame's (9:16 safe areas)
    final = words[fi]
    ff = fit.fit_text(final, w * 0.86, h * 0.42, S.vm(X, 17 if P else 15), S.vm(X, 5), max_lines=2, lh=1.05)
    fly = [wd for i, wd in enumerate(words) if i != fi]
    n = len(fly)
    r = X.rand
    # flight plan: launch times spread over the first ~70% of the beat; the final word lands after the last pass
    at = fit.as_list(p.get("at"))
    land = None
    if at and X.chars:
        try:
            cues = [float(X.T(c, t)) for c in at]
            if len(cues) >= len(words):
                launch = [cues[i] - 0.55 for i in range(len(words)) if i != fi]
                land = cues[fi]
        except SystemExit: pass
    if land is None:
        span = max(0.6, d * 0.62)
        launch = [t + 0.1 + span * k / max(n, 1) for k in range(n)]
        land = t + 0.25 + span
    dur = max(0.7, min(1.4, (land - t) / max(n * 0.55, 1)))
    if n: land = max(land, launch[-1] + dur * 0.95 + 0.25)     # the final word lands only after the last word has passed
    X.css("fx-fw", CSS)
    html = []
    import math
    NS = 64
    sp_ang = [r.uniform(0, 6.283) for _ in range(NS)]
    for k in range(NS):                                    # depth streaks: deterministic, pointing away from the centre
        html.append(f'<i class="fw-sp" data-layout-allow-overflow data-k="{k}" style="transform:rotate({math.degrees(sp_ang[k]) + 90:.0f}deg); opacity:0"></i>')
    for k, wd in enumerate(fly):
        wpx = min(ff.px * 0.75, S.vm(X, 11))
        wf = fit.fit_text(wd, w * 0.7, h * 0.3, wpx, S.vm(X, 3), max_lines=1)
        html.append(f'<div class="fw-w" data-layout-allow-overflow data-safe="ignore" data-k="{k}" style="font-size:{wf.px}px; opacity:0">{X.rich(wf.lines[0])}</div>')
    fh = ff.n * ff.px * 1.05
    html.append(f'<div class="fw-f" style="font-size:{ff.px}px; opacity:0">' + "".join(f'<span class="sl">{X.rich(l)}</span>' for l in ff.lines) + "</div>")
    fwid = ff.em * ff.px
    html.append(f'<i class="fw-rule" style="left:{X.W / 2 - fwid * 0.3:.0f}px; top:{X.H / 2 + fh / 2 + S.vm(X, 2.2):.0f}px; width:{fwid * 0.6:.0f}px"></i>')
    if sub:
        sf = fit.fit_text(sub, w * 0.8, S.vm(X, 8), S.vm(X, 3.2), S.vm(X, 2.6), max_lines=2)
        html.append(f'<div class="fw-sub" style="top:{X.H / 2 + fh / 2 + S.vm(X, 5):.0f}px; font-size:{sf.px}px">{"<br>".join(X.rich(l) for l in sf.lines)}</div>')
    _clip(X, cid, t, d, f'<div class="fw" style="left:{dx:.0f}px; top:{dy:.0f}px">{"".join(html)}</div>', p)
    s = f"#{cid} .fw"
    # streaks: waves of specks rushing outward so the field never stops moving
    for k in range(NS):
        ang = sp_ang[k]; dist = r.uniform(0.4, 0.9) * max(w, h)
        t0 = t + (k % 16) * (d / 16) * 0.92
        X.tw(f'tl.fromTo("{s} .fw-sp[data-k=\'{k}\']", {{x:0, y:0, scale:0.3, opacity:0}}, {{x:{dist * math.cos(ang):.0f}, y:{dist * math.sin(ang):.0f}, scale:2.6, '
             f'keyframes:{{opacity:[0, 0.7, 0]}}, duration:{r.uniform(0.8, 1.3):.2f}, ease:"power2.in", repeat:{max(0, int(d / 1.4))}, immediateRender:false}}, {t0:.3f});')
    for k in range(n):
        side = -1 if k % 2 == 0 else 1
        ex = side * r.uniform(0.32, 0.55) * w
        ey = r.choice([-1, 1]) * r.uniform(0.18, 0.4) * h
        tk = launch[k]
        X.tw(f'tl.fromTo("{s} .fw-w[data-k=\'{k}\']", {{xPercent:-50, yPercent:-50, x:{ex * 0.1:.0f}, y:{ey * 0.1:.0f}, z:-1100}}, '
             f'{{x:{ex * 1.45:.0f}, y:{ey * 1.45:.0f}, z:700, keyframes:{{opacity:[0, 1, 1, 1, 0], filter:["blur(4px)", "blur(0px)", "blur(0px)", "blur(0px)", "blur(2px)"]}}, '
             f'duration:{dur:.2f}, ease:"power1.in", immediateRender:false}}, {tk:.3f});')
        X.sfx(tk + dur * 0.7, "whoosh_soft")
    X.tw(f'tl.fromTo("{s} .fw-f", {{xPercent:-50, yPercent:-50, z:-2600, opacity:0, filter:"blur(10px)"}}, '
         f'{{z:0, opacity:1, filter:"blur(0px)", duration:0.9, ease:"expo.out", immediateRender:false}}, {land - 0.5:.3f});')
    X.tw(f'tl.to("{s} .fw-f", {{scale:1.04, duration:{max(0.3, t + d - land - 0.4):.2f}, ease:"none"}}, {land + 0.4:.3f});')
    X.tw(f'tl.from("{s} .fw-rule", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {land + 0.1:.3f});')
    if sub: X.tw(f'tl.from("{s} .fw-sub", {{opacity:0, y:16, duration:0.5}}, {land + 0.25:.3f});')
    X.sfx(land - 0.1, "hit")


FX = {"flying_words": flying_words}
