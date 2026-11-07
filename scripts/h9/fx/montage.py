"""快切 Montage (抖音卡点混剪 · 无人声段落): a quick-cut run inside the film — one clip per beat (or every `per` beats,
0.5 = half beats) on the music's measured grid (meta.music_beats / <music>.beats.json), each clip at its best readable
moment ("in": "auto", the same picker as scripts/montage.py), a short push-in on every cut, an optional solid tag in
the top band. The beat starts on a beat (build.py snaps it), so the whole run sits on the music; the music bed is
lifted for the run unless the beat says "music": false.

Without measured beats it falls back to meta.bpm, else a 0.5 s grid.
p: clips [{src, in: "auto" | seconds, label (≤ 8 字), line (the sentence it illustrates — required)}] · per (default 1)
   · zoom (e.g. 1.45: every clip shown larger from its top edge, so subtitles burned into the clips fall out of frame)
When the beat has no "d" and the next beat has no "t", build.py makes the beat exactly as long as the run.
"""
import importlib.util, pathlib, sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


P = _load("_pace")


def cut_times(X, p, t, d):
    """[cut times] inside [t, t + d): t itself, then the grid every `per` beats; frame-snapped."""
    from h9 import beatsync
    per = float(p.get("per", 1))
    info = getattr(X, "music_beats", None)
    if info:
        g = beatsync.grid(info["beats"], per)
    else:
        g = P.beats(X, {}, t, d)
        if per == 0.5: g = beatsync.grid(g, 0.5)
        else: g = g[::max(1, int(per))]
    step = (g[1] - g[0]) if len(g) > 1 else 0.5
    cuts = [P.snap(X, t)]
    for x in g:
        x = P.snap(X, x)
        if x > cuts[-1] + 0.45 * step and x < t + d - 0.1: cuts.append(x)
    return cuts


def montage(X, cid, t, d, p):
    from h9 import beatsync, fit as FIT
    clips = p.get("clips") or []
    if not clips: raise SystemExit(f"montage at {t:.2f}s: give \"clips\": [{{\"src\", \"line\"}}, ...]")
    for c in clips:
        if not c.get("line"):
            raise SystemExit(f"montage {c.get('src')}: 写上它对应哪句话（\"line\"）——和口播无关的画面不进快切")
    p["hold"] = "static"             # cuts and push-ins are on the beat grid: no rate / elastic re-timing of this beat
    cuts = cut_times(X, p, t, d)
    if len(cuts) > len(clips):
        print(f"  montage {t:.2f}s: {len(cuts)} cuts fit, {len(clips)} clips given — the last clip holds to the end")
        cuts = cuts[:len(clips)]
    ends = cuts[1:] + [t + d]
    vm = min(X.W, X.H)
    size = max(64, vm // 11)
    X.css("fx-mtg", f""".fx .mtg {{ position:absolute; inset:0; pointer-events:none; }}
.fx .mtg .lb {{ position:absolute; left:50%; top:10%; transform:translateX(-50%); opacity:0; white-space:nowrap;
  font-family:var(--f-display, sans-serif); font-weight:900; font-size:{size}px; line-height:1; letter-spacing:.02em;
  color:#0a0a0a; background:#ffd600; padding:{size // 4}px {size // 3}px {size // 5}px; }}""")
    labels = []
    for i, (c, a, b) in enumerate(zip(clips, cuts, ends)):
        w = max(b - a, 1 / X.fps)
        src = beatsync._path(c["src"], X.src)
        if not src.exists(): raise SystemExit(f"montage: missing clip {src}")
        dur = FIT.duration(src) or w
        if c.get("in", "auto") == "auto": start = beatsync.best_moment_cached(src, w, dur, X.out / "assets")
        else: start = float(c["in"])
        _, sel = FIT.media(X, cid, f"m{i}", str(src), a, w, "mtgv", z=2, start=start)
        if sel:
            n6 = 6 / X.fps          # the push-in of scripts/montage.py: 7 % over the first 6 frames
            # "zoom": 1.5 shows the clip's top part larger (anchored at the top) — pushes burned-in subtitles out of frame
            z = float(p.get("zoom", 1))
            org = ', transformOrigin:"50% 0%"' if z != 1 else ""
            X.tw(f'tl.fromTo("{sel}", {{scale:{1.07 * z:.3f}{org}}}, {{scale:{z:.3f}, duration:{min(n6, w):.3f}, ease:"none", immediateRender:false}}, {a:.3f});')
        if c.get("label"):
            if len(c["label"]) > 8: print(f"  注意：快切标签「{c['label']}」超过 8 个字，半秒读不完")
            labels.append(f'<b class="lb lb{i}">{X.rich(c["label"])}</b>')
            X.tw(f'tl.set("#{cid} .lb{i}", {{opacity:1}}, {a:.3f}); tl.set("#{cid} .lb{i}", {{opacity:0}}, {b:.3f});')
        p.setdefault("_cuts", []).append({"t": round(a, 3), "src": pathlib.Path(c["src"]).name, "in": round(start, 2), "line": c["line"]})
    _clip(X, cid, t, d, f'<div class="mtg">{"".join(labels)}</div>', {}, transparent=True)


FX = {"montage": montage}
