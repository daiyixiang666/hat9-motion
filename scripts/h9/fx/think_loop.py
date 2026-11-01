"""想一想 Think Loop (S15 · 主播停顿思考时的过渡; S01 句中停顿 1–2 秒画面不能死):
a loopable thinking beat — a thought bubble with typing dots breathes in the middle, question marks and light
specks orbit it on slow, out-of-phase ellipses, and the whole loop completes a whole number of cycles inside the
beat, so it can sit under any pause and still end where it started.

Adapts: 1–8 s+ (cycle length ≈ 1.6 s, rounded so the loop closes); text optional, a word to a short phrase (fitted);
0–8 orbiting marks ("orbits", default 5).
p: text · orbits (count) · glyph (default "?")
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def think_loop(X, cid, t, d, p):
    Wv, Hv = F.frame_vmin(X)
    n = int(p.get("orbits", 5)); g = str(p.get("glyph", "?"))
    ts, tl_ = F.fit(p.get("text", ""), Wv * 0.5, 10, 4.2, 2.2, 2) if p.get("text") else (0, [])
    cyc = d / max(1, round(d / 1.6))
    X.css("fx-p5th", """
.fx .p5th { position:absolute; inset:0; display:grid; place-items:center; }
.fx .p5th .bub { position:relative; display:flex; flex-direction:column; align-items:center; gap:1.6vmin; padding:4vmin 6vmin; border-radius:9vmin; background:var(--card); color:var(--card-fg, var(--fg));
  box-shadow:0 0 0 .3vmin color-mix(in srgb, var(--fg) 18%, transparent), 0 3vmin 8vmin rgba(0,0,0,.2); }
.fx .p5th .bub::after { content:''; position:absolute; left:18%; bottom:-4.4vmin; width:3vmin; height:3vmin; border-radius:50%; background:var(--card); box-shadow:-3vmin 3vmin 0 -.8vmin var(--card); }
.fx .p5th .dots { display:flex; gap:1.6vmin; } .fx .p5th .dots i { width:2.2vmin; height:2.2vmin; border-radius:50%; background:currentColor; opacity:.35; }
.fx .p5th .tx { font-family:var(--f-display); font-weight:800; text-align:center; line-height:1.2; } .fx .p5th .tx .fl { display:block; white-space:nowrap; }
.fx .p5th .orb { position:absolute; left:50%; top:50%; width:0; height:0; }
.fx .p5th .orb b { position:absolute; font:900 6vmin var(--f-display); color:var(--accent); transform:translate(-50%,-50%); }
.fx .p5th .orb i { position:absolute; width:1.2vmin; height:1.2vmin; border-radius:50%; background:var(--fg); opacity:.5; transform:translate(-50%,-50%); }
""")
    orbs = "".join(f'<div class="orb o{k}">' + (f"<b>{X.rich(g)}</b>" if k % 2 == 0 else "<i></i>") + "</div>" for k in range(n))
    inner = (f'<div class="p5th">{orbs}<div class="bub"><div class="dots"><i></i><i></i><i></i></div>'
             + (f'<div class="tx" style="font-size:{ts:.2f}vmin">{P.lines_html(X, tl_)}</div>' if tl_ else "") + "</div></div>")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    reps = max(1, round(d / cyc))
    X.tw(f'tl.from("{s} .p5th .bub", {{scale:0.6, opacity:0, duration:0.4, ease:"back.out(2)"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .p5th .bub", {{scale:1}}, {{scale:1.04, duration:{cyc / 2:.3f}, ease:"sine.inOut", yoyo:true, repeat:{reps * 2 - 1}, immediateRender:false}}, {t + 0.4:.3f});')
    X.tw(f'tl.fromTo("{s} .p5th .dots i", {{opacity:0.3, y:0}}, {{opacity:1, y:"-1vmin", duration:{cyc / 6:.3f}, ease:"sine.inOut", yoyo:true, repeat:{reps * 3 - 1}, stagger:{cyc / 9:.3f}}}, {t:.3f});')
    bw = max(18.0, (max(F.em(l) for l in tl_) * ts) if tl_ else 10.0) + 12      # the bubble: orbits stay outside it
    bh = (len(tl_) * ts * 1.2 if tl_ else 0) + 12
    rx = min(Wv * 0.46, max(Wv * (0.36 if X.portrait else 0.28), bw / 2 + 9))
    ry = min(Hv * 0.4, max(Hv * (0.12 if X.portrait else 0.16), bh / 2 + 8))
    for k in range(n):
        ph = 2 * math.pi * k / max(n, 1); spd = 1 + (k % 3) * 0.5
        pts = 24
        kf = ", ".join(f'{{x:"{rx * (1 - 0.15 * (k % 2)) * math.cos(ph + 2 * math.pi * spd * j / pts):.2f}vmin", y:"{ry * math.sin(ph + 2 * math.pi * spd * j / pts):.2f}vmin", duration:{d / pts:.3f}, ease:"none"}}' for j in range(1, pts + 1))
        X.tw(f'tl.set("{s} .p5th .o{k}", {{x:"{rx * (1 - 0.15 * (k % 2)) * math.cos(ph):.2f}vmin", y:"{ry * math.sin(ph):.2f}vmin"}}, {t:.3f}); tl.to("{s} .p5th .o{k}", {{keyframes:[{kf}]}}, {t:.3f});')
    X.tw(f'tl.from("{s} .p5th .orb", {{opacity:0, scale:0, duration:0.35, ease:"back.out(2)", stagger:0.06}}, {t + 0.15:.3f});')
    X.sfx(t, "pop", 0.25)


FX = {"think_loop": think_loop}
