"""音乐卡点 Beat Cut (S06 · 重拍落下画面切换; S05 纯音乐段落; 抖音卡点剪辑 / TypoKing 风格):
the picture follows the music — every cut lands on a beat (snapped to a whole frame), each new card punches in from
108 %, downbeats get a 2-frame flash and a bigger hit, word cards invert their colours on alternate beats, and a
row of beat ticks at the bottom lights up as the bar plays.

Beats come from p["beats"] (absolute s, or relative with beats_rel), else a bpm grid (meta.bpm / p.bpm — music made by
scripts/music.py starts its first bar at 0 s), else beats/<music>.json from `npx hyperframes beats`, else 0.5 s.
Adapts: any length (1 s ≈ 2 cuts at 100 bpm, 8 s ≈ 13); items = words / phrases (fitted), stills, clips (timed) or a
mix, any count (cycled); every = cut on every Nth beat (auto: 1 when the beat is ≥ 0.45 s, else 2).
p: items [text | path | {text | src}] · beats | bpm · beat_offset · every · ticks (default true)
"""
from h9.aefx import _clip, THEMES
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def beat_cut(X, cid, t, d, p):
    from h9 import fit as FIT
    Wv, Hv = F.frame_vmin(X)
    bts = P.beats(X, p, t, d)
    if not bts: bts = [P.snap(X, t)]
    step = (bts[1] - bts[0]) if len(bts) > 1 else 0.5
    every = int(p.get("every") or (1 if step >= 0.45 else 2))
    cuts = bts[::every]
    if cuts[0] - t < 0.3: cuts[0] = P.snap(X, t)          # a beat right at the start: the first card owns it
    else: cuts = [P.snap(X, t)] + cuts                       # otherwise a lead-in card until the first beat
    items = p.get("items") or ["卡点"]
    X.css("fx-p5bc", """
.fx .p5bc { position:absolute; inset:0; overflow:hidden; }
.fx .p5bc .cd { position:absolute; inset:0; display:grid; place-items:center; opacity:0; }
.fx .p5bc .cd.w { background:var(--bg); } .fx .p5bc .cd.w.inv { background:var(--fg); }
.fx .p5bc .cd .wd { text-align:center; font-family:var(--f-display); font-weight:900; line-height:1.02; letter-spacing:-.02em; color:var(--fg); }
.fx .p5bc .cd.inv .wd { color:var(--bg); } .fx .p5bc .cd .wd .fl { display:block; white-space:nowrap; }
.fx .p5bc .cd .wd em { font-style:normal; color:var(--accent); }
.fx .p5bc .cd.im { background:#000; } .fx .p5bc .cd img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .p5bc .ticks { position:absolute; left:50%; bottom:7%; transform:translateX(-50%); display:flex; gap:1vmin; z-index:3; }
.fx .p5bc .ticks i { width:1.4vmin; height:1.4vmin; border-radius:.3vmin; background:color-mix(in srgb, var(--fg) 25%, transparent); }
.fx .p5bc .ticks i.db { width:2.8vmin; }
.fx .p5bc .fl2 { position:absolute; inset:0; background:#fff; opacity:0; z-index:4; pointer-events:none; }
#root.v .fx .p5bc .ticks { bottom:26%; }
""")
    cards, sels = [], []
    ends = cuts[1:] + [t + d]
    for i, (a, b) in enumerate(zip(cuts, ends)):
        it = items[i % len(items)]
        txt = it.get("text") if isinstance(it, dict) else (None if (isinstance(it, str) and FIT.is_video(it)) or (isinstance(it, str) and pathlib.Path(it).suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) else it)
        src = (it.get("src") if isinstance(it, dict) else (it if txt is None else None))
        if src and FIT.is_video(src):
            _, sel = FIT.media(X, cid, f"b{i}", src, a, max(b - a, 0.08), "p5bcv", z=2, start=(i * 1.3) % 6)
            sels.append((sel, True))
            continue
        if src:
            cards.append(f'<div class="cd im cd{i}"><img src="{X.asset(src)}" alt=""></div>')
        else:
            ws, wl = F.fit(txt or "", Wv * 0.84, Hv * 0.5, 30 if X.portrait else 24, 5, 2)
            inv = " inv" if i % 2 else ""
            cards.append(f'<div class="cd w{inv} cd{i}"><div class="wd" style="font-size:{ws:.2f}vmin">{P.lines_html(X, wl)}</div></div>')
        sels.append((f"#{cid} .cd{i}", False))
    n_t = min(16, max(4, len(bts)))
    ticks = ('<div class="ticks">' + "".join(f'<i class="{"db" if P.downbeat(X, p, b) else ""}"></i>' for b in bts[:n_t]) + "</div>") if p.get("ticks", True) else ""
    inner = f'<div class="p5bc">{"".join(cards)}{ticks}<i class="fl2"></i></div>'
    _clip(X, cid, t, d, inner, p, transparent=True)      # cards paint their own ground; clips show through between them
    s = f"#{cid}"
    for i, ((a, b), (sel, is_vid)) in enumerate(zip(zip(cuts, ends), sels)):
        w = max(b - a, 0.08); pk = min(0.2, w * 0.4)
        if is_vid:       # a timed video window shows itself; punch it, then keep creeping until the next cut
            X.tw(f'tl.fromTo("{sel}", {{scale:1.12}}, {{keyframes:[{{scale:1.02, duration:{pk:.3f}, ease:"expo.out"}}, {{scale:1.07, duration:{max(w - pk, 0.04):.3f}, ease:"none"}}], immediateRender:false}}, {a:.3f});')
            continue
        X.tw(f'tl.set("{sel}", {{opacity:1}}, {a:.3f}); tl.set("{sel}", {{opacity:0}}, {b:.3f});')
        X.tw(f'tl.fromTo("{sel} > *", {{scale:1.1}}, {{keyframes:[{{scale:1.0, duration:{pk:.3f}, ease:"expo.out"}}, {{scale:1.05, duration:{max(w - pk, 0.04):.3f}, ease:"none"}}], immediateRender:false}}, {a:.3f});')
    X.tw(f'tl.set("{s} .p5bc", {{x:0}}, {t:.3f});')
    for k, b in enumerate(bts[:n_t]):
        db = P.downbeat(X, p, b)
        X.tw(f'tl.to("{s} .p5bc .ticks i:nth-child({k + 1})", {{background:"{THEMES.get(p.get("theme"), {}).get("accent", "#ff5a1f")}", duration:0.05}}, {b:.3f});')
        if db:
            X.tw(f'tl.fromTo("{s} .p5bc .fl2", {{opacity:0.5}}, {{opacity:0, duration:2 / {X.fps}, ease:"none", immediateRender:false}}, {b:.3f});')
            X.tw(f'tl.to("{s} .p5bc", {{keyframes:[{{x:-10, duration:0.033}}, {{x:6, duration:0.033}}, {{x:0, duration:0.04}}]}}, {b:.3f});')


FX = {"beat_cut": beat_cut}
