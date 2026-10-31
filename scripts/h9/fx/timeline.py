"""时间轴推进 Scrolling Timeline (D4, Company Timeline 3.2K — Titles 第 9; Smertimba Scrolling Timeline 23.9 万播放):
a rail runs off-frame, the camera tracks along it; each milestone ticks on in turn (dot, year, caption), passed
milestones dim, the last one lands in the accent.

Adapts: 2–12+ milestones (spacing, type size and tracking speed scale with the count and the time available),
years as any short label ("1997", "2025.3", "Q4"), captions from a word to a sentence (fitted, ≤ 3 lines).
p: items [[year, caption], ...] · hl (index that gets the accent; default last)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


def timeline(X, cid, t, d, p):
    items = [(str(y), str(c)) for y, c in p["items"]]
    n = len(items)
    hl = int(p.get("hl", n - 1))
    Wv, Hv = F.frame_vmin(X)
    step = (62 if X.portrait else 46) if n <= 6 else (52 if X.portrait else 38) if n <= 9 else (44 if X.portrait else 32)
    ys = min(14.0 if X.portrait else 11.0, step * 0.82 / max(max(F.em(y) for y, _ in items), 1))
    cap_w = step * 0.9
    cs = min(4.2 if X.portrait else 3.4, *(F.fit(c, cap_w, 14, 4.2 if X.portrait else 3.4, 2.0, 3)[0] for _, c in items))
    X.css("fx-tl", """
.fx .tlw { position:absolute; left:0; top:50%; height:0; }
.fx .tlw .tlr { position:absolute; left:0; top:0; height:.45vmin; margin-top:-.22vmin; background:color-mix(in srgb, var(--fg) 25%, transparent); }
.fx .tlw .tlf { position:absolute; left:0; top:0; height:.45vmin; margin-top:-.22vmin; background:var(--fg); transform-origin:0 50%; }
.fx .tlw .tlm { position:absolute; top:0; width:0; }
.fx .tlw .tlm i { position:absolute; left:-1.3vmin; top:-1.3vmin; width:2.6vmin; height:2.6vmin; border-radius:50%; background:var(--bg); border:.5vmin solid var(--fg); }
.fx .tlw .tlm .tly { position:absolute; bottom:4vmin; left:-.6vmin; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; color:var(--fg); letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .tlw .tlm .tlc { position:absolute; top:4.2vmin; left:-.6vmin; font-family:var(--f-body); font-weight:700; line-height:1.35; color:var(--fg); }
.fx .tlw .tlm .tlc .fl { display:block; white-space:nowrap; }
.fx .tlw .tlm.last i { background:var(--accent); border-color:var(--accent); } .fx .tlw .tlm.last .tly { color:var(--accent); }
""")
    vm = min(X.W, X.H) / 100
    x0 = X.W * (0.12 if X.portrait else 0.18)
    ms = []
    for i, (y, c) in enumerate(items):
        _, cl = F.fit(c, cap_w, 14, cs, cs, 3)
        ms.append(f'<div class="tlm{" last" if i == hl else ""}" data-i="{i}" style="left:{x0 + i * step * vm:.0f}px"><div class="tly" style="font-size:{ys:.2f}vmin">{X.rich(y)}</div><i></i>'
                  f'<div class="tlc" style="width:{cap_w:.1f}vmin; font-size:{cs:.2f}vmin">{F.lines_html(X, cl)}</div></div>')
    total = x0 + (n - 1) * step * vm + X.W
    inner = f'<div class="tlw"><i class="tlr" style="width:{total:.0f}px"></i><i class="tlf" style="width:{total:.0f}px"></i>{"".join(ms)}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    per = max(0.22, (d - 0.6) / n)
    mv = min(0.6, per * 0.9)
    X.tw(f'tl.from("{s} .tlw .tlr", {{scaleX:0, transformOrigin:"0 50%", duration:0.6, ease:"expo.out"}}, {t:.3f});')
    for i in range(n):
        ti = t + 0.25 + i * per
        target = max(0, x0 + i * step * vm - (X.W * (0.5 if X.portrait else 0.42)))
        X.tw(f'tl.to("{s} .tlw", {{x:{-target:.0f}, duration:{mv:.2f}, ease:"power3.inOut"}}, {ti - 0.1:.3f});')
        X.tw(f'tl.fromTo("{s} .tlw .tlf", {{scaleX:{(x0 + (i - 1) * step * vm) / total if i else 0:.4f}}}, {{scaleX:{(x0 + i * step * vm) / total:.4f}, duration:{min(0.5, per):.2f}, ease:"power2.out", immediateRender:false}}, {ti - 0.1:.3f});')
        X.tw(f'tl.from("{s} .tlm[data-i=\'{i}\'] i", {{scale:0, duration:0.35, ease:"back.out(3)"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .tlm[data-i=\'{i}\'] .tly", {{yPercent:60, opacity:0, duration:0.45, ease:"expo.out"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .tlm[data-i=\'{i}\'] .tlc", {{y:20, opacity:0, duration:0.4, ease:"expo.out"}}, {ti + 0.08:.3f});')
        if i < n - 1:
            X.tw(f'tl.to("{s} .tlm[data-i=\'{i}\'] .tly, {s} .tlm[data-i=\'{i}\'] .tlc", {{opacity:0.3, duration:0.3}}, {ti + per:.3f});')
        X.sfx(ti, "tick")


FX = {"timeline": timeline}
