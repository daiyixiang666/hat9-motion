"""空镜过场 B-roll Interlude (S04 · 两章之间 3 秒城市航拍; S05 纯音乐段落; Bloomberg Originals / 小Lin说 的章节空镜):
no one speaks — the frame hands over to footage. Letterbox bars close in, the given clips or stills are cut to fill
the time (cuts snap to the music's beats when there are any), each shot keeps moving (footage plays; stills get an
alternating push / pull / pan), a chapter tag draws itself in the corner, a timecode ticks, a source line credits
the footage, and the bars open again at the end.

Adapts: any length from 1 s to 8 s+ (shot count = length / ~1.4 s, capped by the clips you give); 0 clips (a slow
light-field instead), 1 clip (one long move) or many; clips and stills mixed, any aspect (focus-point crop, extreme
ratios over a blurred fill); kicker / title from a word to a phrase (fitted); grade mono | warm | none.
p: clips [path | {src, focus}] · kicker · title · source · beats | bpm · grade · letterbox (default true)
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


def interlude(X, cid, t, d, p):
    from h9 import fit as FIT
    Wv, Hv = F.frame_vmin(X)
    clips = p.get("clips") or []
    bts = P.beats(X, p, t, d) if (p.get("beats") or p.get("bpm") or X.v.get("meta", {}).get("bpm")) else []
    n = max(1, min(len(clips) or 1, round(d / 1.4)))
    cuts = P.even_cuts(X, t, d, n, bts)
    kick_s, kick_l = F.fit(p.get("kicker", ""), Wv * 0.5, 4, 2.2, 1.6, 1) if p.get("kicker") else (0, [])
    ttl_s, ttl_l = F.fit(p.get("title", ""), Wv * (0.7 if X.portrait else 0.46), 12, 6.2 if X.portrait else 5.4, 2.6, 2) if p.get("title") else (0, [])
    grade = p.get("grade", "")
    lb = 10 if not X.portrait else 7
    X.css("fx-p5in", f"""
.fx .p5in {{ position:absolute; inset:0; }}
.fx .p5in .lf {{ position:absolute; inset:-20%; background:radial-gradient(30% 40% at 30% 40%, color-mix(in srgb, var(--accent) 45%, transparent), transparent 70%),
  radial-gradient(35% 35% at 70% 60%, color-mix(in srgb, var(--fg) 22%, transparent), transparent 70%), var(--bg); filter:blur(5vmin); }}
.fx .p5in .bar {{ position:absolute; left:0; right:0; height:{lb}%; background:#000; z-index:3; }}
.fx .p5in .bar.t {{ top:0; }} .fx .p5in .bar.b {{ bottom:0; }}
.fx .p5in .tag {{ position:absolute; left:6%; bottom:calc({lb}% + 5%); z-index:4; color:#fff; text-shadow:0 .2vmin 1.4vmin rgba(0,0,0,.6); }}
.fx .p5in .tag .k {{ font-family:var(--f-mono, monospace); font-weight:700; letter-spacing:.3em; text-transform:uppercase; opacity:.85; white-space:nowrap; }}
.fx .p5in .tag .hr {{ display:block; height:.35vmin; width:14vmin; background:var(--accent); margin:1.2vmin 0 1.4vmin; transform-origin:0 50%; }}
.fx .p5in .tag .tt {{ font-family:var(--f-display); font-weight:900; line-height:1.12; }} .fx .p5in .tag .tt .fl {{ display:block; white-space:nowrap; }}
.fx .p5in .tc {{ position:absolute; right:6%; top:calc({lb}% + 3.5%); z-index:4; font:600 1.9vmin var(--f-mono, monospace); color:#fff; opacity:.75; letter-spacing:.12em; white-space:nowrap; }}
.fx .p5in .src {{ position:absolute; right:6%; bottom:calc({lb}% + 3.5%); z-index:4; font:500 1.6vmin var(--f-mono, monospace); color:#fff; opacity:.6; white-space:nowrap; }}
.fx .p5in .fl2 {{ position:absolute; inset:0; background:#fff; opacity:0; z-index:5; }}
#root .p5gm {{ filter:grayscale(1) contrast(1.08); }} #root .p5gw {{ filter:sepia(.35) saturate(1.1) contrast(1.05); }}
#root.v .fx .p5in .tag {{ left:7%; bottom:calc({lb}% + 22%); }} #root.v .fx .p5in .src {{ bottom:calc({lb}% + 18%); }}
""")
    gcls = {"mono": "p5gm", "warm": "p5gw"}.get(grade, "")
    stills = P.media_windows(X, cid, t, d, clips, cuts, cls=f"p5sh {gcls}".strip()) if clips else '<div class="lf"></div>'
    tag = ""
    if kick_l or ttl_l:
        tag = ('<div class="tag">' + (f'<div class="k" style="font-size:{kick_s:.2f}vmin">{X.rich(kick_l[0])}</div>' if kick_l else "")
               + '<i class="hr"></i>' + (f'<div class="tt" style="font-size:{ttl_s:.2f}vmin">{P.lines_html(X, ttl_l)}</div>' if ttl_l else "") + "</div>")
    lbars = '<i class="bar t"></i><i class="bar b"></i>' if p.get("letterbox", True) else ""
    src = f'<div class="src">{X.rich(p["source"])}</div>' if p.get("source") else ""
    inner = f'<div class="p5in">{stills}{lbars}{tag}<div class="tc">00:00:00</div>{src}<i class="fl2"></i></div>'
    has_video = any(FIT.is_video(c.get("src") if isinstance(c, dict) else c) for c in clips)
    _clip(X, cid, t, d, inner, p, transparent=has_video)
    s = f"#{cid}"
    if lbars:
        X.tw(f'tl.from("{s} .p5in .bar.t", {{yPercent:-100, duration:0.5, ease:"expo.out"}}, {t:.3f}); tl.from("{s} .p5in .bar.b", {{yPercent:100, duration:0.5, ease:"expo.out"}}, {t:.3f});')
        if d > 1.6:
            X.tw(f'tl.to("{s} .p5in .bar.t", {{yPercent:-100, duration:0.4, ease:"power2.in"}}, {t + d - 0.4:.3f}); tl.to("{s} .p5in .bar.b", {{yPercent:100, duration:0.4, ease:"power2.in"}}, {t + d - 0.4:.3f});')
    if not clips:
        X.tw(f'tl.fromTo("{s} .p5in .lf", {{rotation:0, scale:1}}, {{rotation:{18 + 4 * d:.0f}, scale:1.2, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if tag:
        tin = t + min(0.35, d * 0.15)
        X.tw(f'tl.from("{s} .p5in .tag .k", {{opacity:0, x:-16, duration:0.45, ease:"expo.out"}}, {tin:.3f});')
        X.tw(f'tl.from("{s} .p5in .tag .hr", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {tin + 0.1:.3f});')
        X.tw(f'tl.from("{s} .p5in .tag .tt .fl", {{yPercent:60, opacity:0, duration:0.6, ease:"expo.out", stagger:0.08}}, {tin + 0.2:.3f});')
        if d > 2.4: X.tw(f'tl.to("{s} .p5in .tag", {{opacity:0, y:10, duration:0.4, ease:"power2.in"}}, {t + d - 0.75:.3f});')
    fps = X.fps
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .p5in .tc"); tl.to(o, {{v:{d:.3f}, duration:{d:.3f}, ease:"none", onUpdate:()=>{{const f=Math.floor(o.v*{fps}); const ss=Math.floor(f/{fps}), ff=f%{fps}; el.textContent="00:00:"+String(ss).padStart(2,"0")+":"+String(ff).padStart(2,"0");}}}}, {t:.3f});}})();')
    for c in cuts[1:]:
        X.tw(f'tl.fromTo("{s} .p5in .fl2", {{opacity:0.35}}, {{opacity:0, duration:0.12, ease:"none", immediateRender:false}}, {c:.3f});')
        X.sfx(c, "hit", 0.18)
    X.sfx(t, "whoosh_soft", 0.3)


FX = {"interlude": interlude}
