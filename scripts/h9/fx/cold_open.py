"""无声开场 Cold Open (S08 · 黑场 1.5 秒后标题砸下，再开口; 电影预告 / Netflix 纪录片的冷开场):
picture before voice. A projector line opens the black, fragments of footage flicker past faster and faster
(or light streaks when there is none), a low rumble builds, the title slams in with a flash and a shake, the
kicker and sub settle, and the frame holds — creeping in — until the narration starts.

Adapts: any length from 1 s to 8 s+ (flash count and the title moment scale with it); 0–N clips or stills of any
aspect; title from a word to a phrase (fitted, ≤ 2 lines); kicker / sub optional.
Narration: give the beat t = 0 and d = the lead, and start the voice after it. Until the pipeline has meta.lead
(WP6), pad the voice file and shift words.json by the lead (examples/pacing/make_audio.py shows how).
p: title · kicker · sub · clips [path | {src, focus}] · at (title moment: "@词" | seconds) | at_rel · grade mono | warm
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def cold_open(X, cid, t, d, p):
    from h9 import fit as FIT
    Wv, Hv = F.frame_vmin(X)
    tt = P.at(X, p, "at", t, d, 0.6 if d >= 2 else 0.35)
    clips = p.get("clips") or []
    # flashes: accelerating windows between ~12% and the title moment
    a0 = t + max(0.25, (tt - t) * 0.18)
    n = max(0, min(len(clips) * 2 if clips else 0, round((tt - a0) / 0.28)))
    wins, x, k = [], a0, 0
    if n:
        span = tt - a0; weights = [1.0 / (1 + 0.35 * i) for i in range(n)]; sc = span / sum(weights)
        for w in weights: wins.append((P.snap(X, x), P.snap(X, x + w * sc * 0.82))); x += w * sc
    ts, tl_ = F.fit(p.get("title", ""), Wv * (0.86 if X.portrait else 0.78), Hv * 0.32, 15 if X.portrait else 13, 4, 2)
    X.css("fx-p5co", """
.fx .p5co { position:absolute; inset:0; background:#000; overflow:hidden; }
.fx .p5co .pl { position:absolute; left:0; right:0; top:50%; height:.3vmin; margin-top:-.15vmin; background:#fff; box-shadow:0 0 3vmin 1vmin rgba(255,255,255,.6); transform-origin:50% 50%; }
.fx .p5co .st { position:absolute; inset:-10%; opacity:0;
  background:repeating-linear-gradient(100deg, transparent 0 7vmin, rgba(255,255,255,.08) 7vmin 7.6vmin, transparent 7.6vmin 15vmin),
             radial-gradient(40% 30% at 50% 50%, color-mix(in srgb, var(--accent) 50%, transparent), transparent 70%); }
.fx .p5co .fr { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0; filter:contrast(1.15) brightness(.9); }
.fx .p5co .tt { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2.2vmin; text-align:center; }
.fx .p5co .tt .k { font:700 2.2vmin var(--f-mono, monospace); letter-spacing:.36em; color:rgba(255,255,255,.75); text-transform:uppercase; }
.fx .p5co .tt .h { font-family:var(--f-display); font-weight:900; line-height:1.06; color:#fff; letter-spacing:-.015em; } .fx .p5co .tt .h .fl { display:block; white-space:nowrap; }
.fx .p5co .tt .h em { font-style:normal; color:var(--accent); }
.fx .p5co .tt .s { font:600 2.6vmin var(--f-body); color:rgba(255,255,255,.7); }
.fx .p5co .wash { position:absolute; inset:0; background:#fff; opacity:0; }
.fx .p5co .gr { position:absolute; inset:0; opacity:.08; background-image:radial-gradient(rgba(255,255,255,.8) 1px, transparent 1px); background-size:3px 3px; }
""")
    gcls = {"mono": " p5gm", "warm": " p5gw"}.get(p.get("grade", ""), "")
    frames = []
    for i, (a, b) in enumerate(wins):
        src = clips[i % len(clips)]
        focus = src.get("focus") if isinstance(src, dict) else None
        src = src.get("src") if isinstance(src, dict) else src
        if FIT.is_video(src):
            _, sel = FIT.media(X, cid, f"f{i}", src, a, max(b - a, 0.1), f"fr{gcls}", focus=focus, z=4, start=(i * 1.7) % 5)
            X.tw(f'tl.fromTo("{sel}", {{scale:1.15, opacity:1}}, {{scale:1.0, duration:{max(b - a, 0.1):.2f}, ease:"none"}}, {a:.3f});')
        else:
            frames.append(f'<img class="fr fr{i}{gcls}" src="{X.asset(src)}" alt="" style="object-position:{FIT.focus_css(focus)}">')
            X.tw(f'tl.set("#{cid} .fr{i}", {{opacity:1}}, {a:.3f}); tl.fromTo("#{cid} .fr{i}", {{scale:1.15}}, {{scale:1.0, duration:{max(b - a, 0.1):.2f}, ease:"none", immediateRender:false}}, {a:.3f}); tl.set("#{cid} .fr{i}", {{opacity:0}}, {b:.3f});')
    title = P.lines_html(X, tl_)
    inner = (f'<div class="p5co"><i class="pl"></i><div class="st"></div>{"".join(frames)}<div class="tt">'
             + (f'<div class="k">{X.rich(p["kicker"])}</div>' if p.get("kicker") else "") + f'<div class="h" style="font-size:{ts:.2f}vmin">{title}</div>'
             + (f'<div class="s">{X.rich(p["sub"])}</div>' if p.get("sub") else "") + '</div><i class="wash"></i><div class="gr"></div></div>')
    has_video = any(FIT.is_video(c.get("src") if isinstance(c, dict) else c) for c in clips)
    _clip(X, cid, t, d, inner, {k: v for k, v in p.items() if k != "theme"})     # footage flashes are timed root layers above this clip (z 4)
    s = f"#{cid}"
    pre = tt - t
    X.tw(f'tl.fromTo("{s} .p5co .pl", {{scaleX:0, opacity:1}}, {{scaleX:1, duration:{max(0.2, min(0.8, pre * 0.3)):.2f}, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.to("{s} .p5co .pl", {{scaleY:0, opacity:0, duration:0.2}}, {a0:.3f});')
    if not clips:
        X.tw(f'tl.fromTo("{s} .p5co .st", {{opacity:0, xPercent:-6}}, {{opacity:1, xPercent:6, duration:{max(0.2, pre - (a0 - t)):.2f}, ease:"power1.in"}}, {a0:.3f});')
        X.tw(f'tl.to("{s} .p5co .st", {{opacity:0.25, duration:0.3}}, {tt:.3f});')
    X.tw(f'tl.fromTo("{s} .p5co .wash", {{opacity:0.85}}, {{opacity:0, duration:0.22, ease:"none", immediateRender:false}}, {tt:.3f});')
    X.tw(f'tl.from("{s} .p5co .tt .h", {{scale:1.9, opacity:0, filter:"blur(12px)", duration:0.34, ease:"expo.out"}}, {tt:.3f});')
    X.tw(f'tl.fromTo("{s} .p5co .tt", {{x:0}}, {{keyframes:[{{x:-18, duration:0.04}}, {{x:13, duration:0.04}}, {{x:-6, duration:0.04}}, {{x:0, duration:0.05}}]}}, {tt + 0.05:.3f});')
    X.tw(f'tl.from("{s} .p5co .tt .k, {s} .p5co .tt .s", {{opacity:0, y:12, duration:0.5, ease:"expo.out", stagger:0.1}}, {tt + 0.3:.3f});')
    post = t + d - tt
    if post > 0.3: P.push(X, f"{s} .p5co .tt", tt + 0.2, post, base=0.012, cap=0.06)
    X.sfx(t + 0.05, "whoosh_deep", 0.4)
    for a, _ in wins[::2]: X.sfx(a, "shutter", 0.12)
    X.sfx(tt, "slam", 0.55); X.sfx(tt, "boom", 0.4)


FX = {"cold_open": cold_open}
