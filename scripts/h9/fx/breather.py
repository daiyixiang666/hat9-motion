"""留白呼吸页 Breather (S03 · 说完金句停 2 秒让观众想; talkcraft「bed-echo-blur」/「slow-push-in」, 所长林超的金句停顿):
the line stays on screen while the frame keeps breathing — a camera creep that grows with the pause, the glyphs
open a hair apart, a light sheen passes once, dust motes drift, an accent rule draws slowly under the line and a
row of pause dots fills as the silence runs. A soft riser cues the music to lift.

Adapts: any hold from 1 s to 8 s+ (every motion is scaled to the duration; under 1.5 s only the creep and the rule
run); text from 1 glyph to a sentence (fitted, ≤ 3 lines) or none at all (an ambient hold); optional kicker and
attribution; background = theme, a still ("image", any aspect) or footage ("video"), dimmed; mood calm | heavy
(desaturated, slower, darker) | warm.
p: text · sub · kicker · image | video · mood · held (true = already on screen, no entrance) · lift (riser cue, default true) · meter
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


def breather(X, cid, t, d, p):
    from h9 import fit as FIT
    Wv, Hv = F.frame_vmin(X)
    mood = p.get("mood", "calm")
    bw = Wv * (0.84 if X.portrait else 0.74)
    ts, tl_ = F.fit(p.get("text", ""), bw, Hv * (0.34 if X.portrait else 0.42), 13 if X.portrait else 12, 3.2, 3) if p.get("text") else (0, [])
    X.css("fx-p5br", """
.fx .p5br { position:absolute; inset:0; }
.fx .p5br .glow { position:absolute; width:90vmin; height:90vmin; left:50%; top:50%; margin:-45vmin 0 0 -45vmin; border-radius:50%;
  background:radial-gradient(closest-side, color-mix(in srgb, var(--accent) 16%, transparent), transparent 70%); }
.fx .p5br .bgm { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .p5br .veil { position:absolute; inset:0; background:color-mix(in srgb, var(--bg) 62%, transparent); }
.fx .p5br .cam { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2.4vmin; }
.fx .p5br .kick { font:700 2.1vmin var(--f-mono, monospace); letter-spacing:.32em; color:var(--muted); text-transform:uppercase; }
.fx .p5br .tx { position:relative; clip-path:inset(-14% -1% -14% -1%); text-align:center; font-family:var(--f-display); font-weight:900; line-height:1.14; color:var(--fg); letter-spacing:-.01em; }
.fx .p5br .tx .fl { display:block; white-space:nowrap; }
.fx .p5br .tx .sh { position:absolute; inset:-4% -8%; background:linear-gradient(100deg, transparent 35%, color-mix(in srgb, var(--fg) 30%, transparent) 50%, transparent 65%);
  mix-blend-mode:overlay; pointer-events:none; opacity:0; }
.fx .p5br .rule { width:var(--rw); height:.5vmin; background:var(--accent); transform-origin:50% 50%; }
.fx .p5br .sub { font:600 2.4vmin var(--f-body); color:var(--muted); letter-spacing:.06em; }
.fx .p5br .meter { position:absolute; left:50%; bottom:12%; display:flex; gap:1.2vmin; transform:translateX(-50%); }
.fx .p5br .meter i { width:.9vmin; height:.9vmin; border-radius:50%; background:color-mix(in srgb, var(--fg) 25%, transparent); }
.fx .p5br .meter b { position:absolute; left:0; top:0; height:.9vmin; border-radius:.45vmin; background:var(--fg); opacity:.75; width:.9vmin; }
.fx .p5br.heavy { filter:saturate(.15); } .fx .p5br.heavy .glow { opacity:.4; }
#root.v .fx .p5br .meter { bottom:24%; }
""")
    bg = ""
    if p.get("image") or p.get("video"):
        mk, vsel = FIT.media(X, cid, "bg", p.get("image") or p.get("video"), t, d, "bgm", focus=p.get("focus"), z=2)
        bg = (mk or "") + '<div class="veil"></div>'
    else:
        vsel = None
    n_dots = max(3, min(8, round(d * 1.5)))
    meter = (f'<div class="meter">{"".join("<i></i>" for _ in range(n_dots))}<b></b></div>' if p.get("meter", True) and d >= 1.5 else "")
    tx = (f'<div class="tx" style="font-size:{ts:.2f}vmin">{P.lines_html(X, tl_)}<i class="sh"></i></div>' if tl_ else "")
    rw = min(bw, max(F.em(FIT.plain(l)) for l in tl_) * ts) * 0.42 if tl_ else 24
    inner = (f'<div class="p5br {mood}">{bg}<div class="glow"></div>{P.motes(X, cid, t, d, 18 if d > 2 else 10, rise=6 + d)}'
             f'<div class="cam">' + (f'<div class="kick">{X.rich(p["kicker"])}</div>' if p.get("kicker") else "")
             + tx + f'<i class="rule" style="--rw:{rw:.1f}vmin"></i>' + (f'<div class="sub">{X.rich(p["sub"])}</div>' if p.get("sub") else "")
             + f'</div>{meter}</div>')
    _clip(X, cid, t, d, inner, p, transparent=bool(vsel))
    s = f"#{cid}"
    slow = 1.6 if mood == "heavy" else 1.0
    P.push(X, f"{s} .p5br .cam", t, d, base=0.010 * slow, cap=0.07)
    if vsel: P.push(X, vsel, t, d, base=0.012, cap=0.09)
    X.tw(f'tl.fromTo("{s} .p5br .glow", {{scale:0.9, opacity:0.6}}, {{scale:1.15, opacity:1, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    if not p.get("held"):
        X.tw(f'tl.from("{s} .p5br .tx .fl", {{yPercent:40, opacity:0, filter:"blur(10px)", duration:{min(0.9, d * 0.4):.2f}, ease:"expo.out", stagger:0.08}}, {t + 0.05:.3f});')
        X.tw(f'tl.from("{s} .p5br .kick", {{opacity:0, y:-10, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    # the glyphs open a hair apart while we wait (transform, never letter-spacing)
    X.tw(f'tl.fromTo("{s} .p5br .tx", {{scaleX:1}}, {{scaleX:{1 + min(0.03, 0.005 * d):.4f}, duration:{d:.2f}, ease:"sine.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .p5br .rule", {{scaleX:0}}, {{scaleX:1, duration:{max(0.4, d * 0.6):.2f}, ease:"power2.out"}}, {t + min(0.3, d * 0.2):.3f});')
    X.tw(f'tl.set("{s} .p5br .tx .sh", {{xPercent:-120}}, {t:.3f});')
    if d >= 1.5:
        X.tw(f'tl.fromTo("{s} .p5br .tx .sh", {{xPercent:-120, opacity:1}}, {{xPercent:240, opacity:1, duration:{min(1.4, d * 0.35):.2f}, ease:"power1.inOut", immediateRender:false}}, {t + d * 0.38:.3f});')
        X.tw(f'tl.set("{s} .p5br .tx .sh", {{opacity:0}}, {t + d * 0.38 + min(1.4, d * 0.35):.3f});')
        X.tw(f'tl.from("{s} .p5br .sub", {{opacity:0, y:12, duration:0.6, ease:"expo.out"}}, {t + min(0.6, d * 0.3):.3f});')
    if meter:
        full = (n_dots - 1) * 2.1 + 0.9
        X.tw(f'tl.fromTo("{s} .p5br .meter b", {{width:"0.9vmin"}}, {{width:"{full:.2f}vmin", duration:{d * 0.92:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.from("{s} .p5br .meter", {{opacity:0, duration:0.4}}, {t + 0.2:.3f});')
    if p.get("lift", True): X.sfx(t + 0.05, "riser", 0.16 if mood != "heavy" else 0.1)


FX = {"breather": breather}
