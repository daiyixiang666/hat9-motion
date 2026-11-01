"""shared helpers for the 不说话的时刻 effects (breather, interlude, suspense, cold_open, beat_cut, reaction, loading,
think_loop, chapter_breather). Files starting with _ are not effects; load by path like _fit.py.

beats(): the musical grid inside a window — explicit p["beats"], else a bpm grid (scripts/music.py starts its bar
at 0 s, so meta.bpm alone is enough), else beats/<music>.json from `npx hyperframes beats`, else every 0.5 s.
Every time is snapped to a whole frame so a cut lands within one frame of the beat.
"""
import json, math
from pathlib import Path


def snap(X, x): return round(float(x) * X.fps) / X.fps


def at(X, p, key, t, d, frac):
    """a moment inside the beat: "@词" cue, absolute seconds, p[key + "_rel"] seconds from t, or t + d * frac."""
    if p.get(key + "_rel") is not None: v = t + float(p[key + "_rel"])
    elif p.get(key) is not None: v = float(X.T(p[key], t))
    else: v = t + d * frac
    return snap(X, min(max(v, t + 0.05), t + d - 0.05))


def beats(X, p, t, d):
    meta = X.v.get("meta", {})
    if p.get("beats"):
        bs = [float(b) + (t if p.get("beats_rel") else 0) for b in p["beats"]]
    else:
        bpm = float(p.get("bpm") or meta.get("bpm") or 0)
        if not bpm and meta.get("music"):
            f = X.src / "beats" / (Path(meta["music"]).name + ".json")
            if f.exists():
                try:
                    j = json.loads(f.read_text())
                    bs = [float(b.get("time", b) if isinstance(b, dict) else b) for b in j.get("beats", j)]
                except (ValueError, TypeError, AttributeError):
                    bs = []
                return [snap(X, b) for b in bs if t - 1e-6 <= b < t + d - 0.05]
        step = 60.0 / bpm if bpm else 0.5
        off = float(p.get("beat_offset", meta.get("beat_offset", 0.0)))
        k0 = math.ceil((t - off) / step - 1e-6)
        bs = [off + k * step for k in range(k0, k0 + int(d / step) + 2)]
    return [snap(X, b) for b in bs if t - 1e-6 <= b < t + d - 0.05]


def downbeat(X, p, b):
    """True on the first beat of a bar (bpm grid only; explicit beats count every 4th)."""
    meta = X.v.get("meta", {})
    bpm = float(p.get("bpm") or meta.get("bpm") or 0)
    if not bpm: return False
    step = 60.0 / bpm
    off = float(p.get("beat_offset", meta.get("beat_offset", 0.0)))
    return round((b - off) / step) % 4 == 0


def motes(X, cid, t, d, n=16, cls="p5mo", color="var(--fg)", rise=8.0):
    """slow drifting dust motes: an ambient layer that keeps any hold alive. Deterministic (seeded X.rand)."""
    r = X.rand
    dots = []
    for k in range(n):
        x, y, s, o = r.uniform(3, 97), r.uniform(10, 95), r.uniform(0.25, 0.75), r.uniform(0.18, 0.55)
        dots.append(f'<i style="left:{x:.1f}%; top:{y:.1f}%; width:{s:.2f}vmin; height:{s:.2f}vmin; opacity:{o:.2f}"></i>')
    X.css(f"p5-motes-{cls}", f".fx .{cls} {{ position:absolute; inset:0; pointer-events:none; }} .fx .{cls} i {{ position:absolute; border-radius:50%; background:{color}; filter:blur(.08vmin); }}")
    sel = f"#{cid} .{cls} i"
    X.tw(f'tl.fromTo("{sel}", {{y:0, x:0}}, {{y:(i)=>-{rise}*(0.6+((i*37)%10)/10)+"vmin", x:(i)=>(((i*53)%9)-4)*0.6+"vmin", duration:{max(d, 0.5):.2f}, ease:"none"}}, {t:.3f});')
    return f'<div class="{cls}">{"".join(dots)}</div>'


def push(X, sel, t, d, base=0.012, cap=0.08, origin="50% 50%"):
    """a camera creep whose amount grows with the hold, so a 1 s and an 8 s pause both move."""
    s = 1 + min(cap, base * max(d, 1.0))
    X.tw(f'tl.fromTo("{sel}", {{scale:1, transformOrigin:"{origin}"}}, {{scale:{s:.4f}, duration:{max(d, 0.3):.2f}, ease:"none"}}, {t:.3f});')


def media_windows(X, cid, t, d, items, cuts, cls="p5sh", kb=True):
    """one picture per window [cuts[i], cuts[i+1]) — videos as timed root layers (fit.media), stills inside the
    clip with a Ken Burns move that alternates push / pull / pan. Returns the still markup for the effect clip."""
    from h9 import fit as FIT
    html = []
    base, extra = cls.split()[0], " ".join(cls.split()[1:])
    ends = cuts[1:] + [t + d]
    for i, (a, b) in enumerate(zip(cuts, ends)):
        src = items[i % len(items)] if items else None
        if isinstance(src, dict): focus, src = src.get("focus"), src.get("src") or src.get("video")
        else: focus = None
        if not src: continue
        w = max(b - a, 0.1)
        if FIT.is_video(src):
            _, sel = FIT.media(X, cid, f"w{i}", src, a, w, f"{base}v {extra}".strip(), focus=focus, z=2, start=(i * 2.3) % 6)
        else:
            mk, _ = FIT.media(X, cid, f"w{i}", src, t, d, f"{base}{i} {base} {extra}".strip(), focus=focus, extra_style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:0")
            html.append(mk)
            sel = f"#{cid} .{base}{i}"
            X.tw(f'tl.set("{sel}", {{opacity:1}}, {a:.3f}); tl.set("{sel}", {{opacity:0}}, {b:.3f});')
        if kb and sel:
            mv = i % 3
            if mv == 0: X.tw(f'tl.fromTo("{sel}", {{scale:1.0}}, {{scale:1.10, duration:{w:.2f}, ease:"none"}}, {a:.3f});')
            elif mv == 1: X.tw(f'tl.fromTo("{sel}", {{scale:1.12}}, {{scale:1.02, duration:{w:.2f}, ease:"none"}}, {a:.3f});')
            else: X.tw(f'tl.fromTo("{sel}", {{scale:1.08, xPercent:-2.5}}, {{scale:1.08, xPercent:2.5, duration:{w:.2f}, ease:"none"}}, {a:.3f});')
    return "".join(html)


def even_cuts(X, t, d, n, beats_=None, min_len=0.45):
    """n windows filling [t, t+d); each inner cut moves to the nearest beat when one is within 0.35 s."""
    n = max(1, n)
    cuts = [t + d * k / n for k in range(n)]
    if beats_:
        for k in range(1, n):
            near = min(beats_, key=lambda b: abs(b - cuts[k]))
            if abs(near - cuts[k]) < 0.35: cuts[k] = near
    out = [snap(X, cuts[0])]
    for c in cuts[1:]:
        c = snap(X, c)
        if c - out[-1] >= min_len and t + d - c >= min_len: out.append(c)
    return out


def fix_em(lines):
    """balanced breaks can split a *强调* pair across lines: close it at the line end and reopen on the next line."""
    out, open_ = [], False
    for l in lines:
        l = ("*" if open_ else "") + l
        if l.count("*") % 2: l += "*"; open_ = True
        else: open_ = False
        out.append(l.replace("**", ""))
    return out


def lines_html(X, lines, cls="fl"):
    return "".join(f'<span class="{cls}">{X.rich(x)}</span>' for x in fix_em(lines))
