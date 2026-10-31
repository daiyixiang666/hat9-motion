"""折线描绘 Line Chart Draw (D2, Envato Popular「Line Chart Infographic」; Mapal VOX 式信息图 34.6 万播放):
the line draws left→right with a glowing head; a value tag rides the head and counts the interpolated value,
each data point pops as the head passes it, the area fills down to the zero line, the last value lands big.

Adapts: 2–15+ points (labels thin out so they never collide; dots shrink), negative values (a zero line, the
area fills to it), huge values (auto 万 / 亿 or K / M / B via "compact"), any label length (fitted font).
p: points [[label, value], ...] · unit · dec · title · note · compact
"""
import json
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


def line_draw(X, cid, t, d, p):
    pts = [(str(lb), float(v)) for lb, v in p["points"]]
    n = len(pts)
    vals = [v for _, v in pts]
    div, suf = F.compact(max(abs(v) for v in vals), p.get("compact", "cn"))
    unit = (suf + p.get("unit", "")) if div != 1 else p.get("unit", "")
    dec = int(p.get("dec", 1 if div != 1 or any(v != int(v) for v in vals) else 0))
    W, H = (960, 560) if not X.portrait else (900, 760)
    lo, hi = F.series_range(vals, 1.18)
    sv = lambda v: (v - lo) / (hi - lo)
    pl, pr, pt, pb = 30, 70, 110, 80
    xy = [(pl + (W - pl - pr) * (i / max(n - 1, 1)), pt + (H - pt - pb) * (1 - sv(v))) for i, (_, v) in enumerate(pts)]
    zy = pt + (H - pt - pb) * (1 - sv(0))
    dd = f"M{xy[0][0]:.1f} {xy[0][1]:.1f}"
    for i in range(n - 1):
        p0 = xy[max(i - 1, 0)]; p1 = xy[i]; p2 = xy[i + 1]; p3 = xy[min(i + 2, n - 1)]
        k = 6 if n <= 8 else 10                          # tighter tension for dense series (less overshoot)
        c1 = (p1[0] + (p2[0] - p0[0]) / k, p1[1] + (p2[1] - p0[1]) / k); c2 = (p2[0] - (p3[0] - p1[0]) / k, p2[1] - (p3[1] - p1[1]) / k)
        dd += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    area = dd + f" L{xy[-1][0]:.1f} {zy:.1f} L{xy[0][0]:.1f} {zy:.1f} Z"
    # x labels: thin to what fits
    span_px = (W - pl - pr) / max(n - 1, 1)
    lab_px = max(F.em(lb) for lb, _ in pts) * 24 + 12
    step = 1
    while step < n and lab_px > span_px * step: step += 1
    show = set(range(0, n, step))
    if n - 1 not in show:
        if (n - 1) - max(show) < step * 0.6: show.discard(max(show))
        show.add(n - 1)
    r = 11 if n <= 8 else 8 if n <= 12 else 6
    X.css("fx-line", """
.fx .lc { position:absolute; left:50%; top:48%; width:min(100vmin, 86vw); transform:translate(-50%,-50%); }
#root.v .fx .lc { top:41%; width:90vw; }
.fx .lc svg { width:100%; height:auto; overflow:visible; display:block; }
.fx .lc .lct { font:900 4.4vmin var(--f-display); color:var(--fg); margin-bottom:1vmin; white-space:nowrap; }
.fx .lc .lct small { font:500 2vmin var(--f-mono, monospace); color:var(--muted); margin-left:1.6vmin; letter-spacing:.06em; }
.fx .lc .lcg { stroke:color-mix(in srgb, var(--fg) 13%, transparent); stroke-width:1.5; }
.fx .lc .lcax { stroke:var(--fg); stroke-width:3; }
.fx .lc .lcz { stroke:var(--fg); stroke-width:2; stroke-dasharray:8 6; opacity:.7; }
.fx .lc .lcl { fill:none; stroke:var(--accent); stroke-width:7; stroke-linecap:round; stroke-linejoin:round; }
.fx .lc .lca { fill:var(--accent); opacity:.16; }
.fx .lc .lcp { fill:var(--bg); stroke:var(--accent); stroke-width:5; }
.fx .lc .lch { fill:var(--accent); } .fx .lc .lchg { fill:var(--accent); opacity:.25; }
.fx .lc .lcb { font:700 24px var(--f-body); fill:var(--muted); text-anchor:middle; }
.fx .lc .lctag rect { fill:var(--fg); } .fx .lc .lctag text { font:800 30px var(--f-num, var(--f-display)); fill:var(--bg); text-anchor:middle; font-variant-numeric:tabular-nums; }
.fx .lc .lce { font:900 64px var(--f-num, var(--f-display)); fill:var(--accent); text-anchor:end; }
""")
    grid = "".join(f'<line class="lcg" x1="{pl}" x2="{W - pr}" y1="{pt + (H - pt - pb) * k / 4:.1f}" y2="{pt + (H - pt - pb) * k / 4:.1f}"/>' for k in range(4))
    zl = f'<line class="lcz" x1="{pl}" x2="{W - pr}" y1="{zy:.1f}" y2="{zy:.1f}"/>' if lo < 0 else ""
    dots = "".join(f'<circle class="lcp" data-i="{i}" cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>' for i, (x, y) in enumerate(xy))
    labs = "".join(f'<text class="lcb" x="{x:.1f}" y="{H - pb + 40}">{X.rich(lb)}</text>' for i, ((x, _), (lb, _)) in enumerate(zip(xy, pts)) if i in show)
    last = f"{pts[-1][1] / div:,.{dec}f}{unit}"
    tagw = max(F.em(f"{v / div:,.{dec}f}") for v in vals) * 30 * 0.62 / 0.6 + 36
    X.used_text.update("0123456789.,-" + unit)
    inner = (f'<div class="lc"><div class="lct">{X.rich(p.get("title", ""))}<small>{X.rich(p.get("note", ""))}</small></div>'
             f'<svg viewBox="0 0 {W} {H}">{grid}<line class="lcax" x1="{pl}" x2="{W - pr}" y1="{H - pb}" y2="{H - pb}"/>{zl}'
             f'<path class="lca" d="{area}"/><path class="lcl" d="{dd}"/>{dots}{labs}'
             f'<circle class="lchg" r="{r * 2.4:.0f}"/><circle class="lch" r="{r}"/><g class="lctag"><rect x="{-tagw / 2:.0f}" y="-74" width="{tagw:.0f}" height="50" rx="8"/><text y="-38">0</text></g>'
             f'<text class="lce" x="{W - pr}" y="{pt - 40}">{X.rich(last)}</text></svg></div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    dr = max(1.2, d * 0.5)
    t0 = t + 0.45
    X.tw(f'tl.from("{s} .lct", {{x:-30, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .lcax, {s} .lcg, {s} .lcz", {{scaleX:0, transformOrigin:"0 50%", duration:0.5, ease:"expo.out", stagger:0.05}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .lcb", {{opacity:0, y:10, duration:0.3, stagger:{min(0.06, 0.6 / max(len(show), 1)):.3f}}}, {t + 0.25:.3f});')
    fj = F.js_fmt(dec)
    X.tw(f'''(()=>{{const r=document.querySelector("{s}"), L=r.querySelector(".lcl"), len=L.getTotalLength(), hd=r.querySelector(".lch"), hg=r.querySelector(".lchg"), tg=r.querySelector(".lctag"), tx=tg.querySelector("text"), P={json.dumps([[round(x, 1), v / div] for (x, _), (_, v) in zip(xy, pts)])}, f={fj};
function val(x){{for(let i=0;i<P.length-1;i++){{if(x<=P[i+1][0]){{const q=(x-P[i][0])/(P[i+1][0]-P[i][0]); return P[i][1]+(P[i+1][1]-P[i][1])*Math.max(0,Math.min(1,q));}}}} return P[P.length-1][1];}}
function draw(k){{L.style.strokeDasharray=len; L.style.strokeDashoffset=len*(1-k); const q=L.getPointAtLength(len*k);
hd.setAttribute("cx",q.x); hd.setAttribute("cy",q.y); hg.setAttribute("cx",q.x); hg.setAttribute("cy",q.y); tg.setAttribute("transform",`translate(${{q.x}},${{q.y}})`);
tx.textContent=f(val(q.x)); const on=k>0.001; hd.style.opacity=on?1:0; hg.style.opacity=on?.25:0; tg.style.opacity=on&&k<0.999?1:0;}}
draw(0); const o={{k:0}}; tl.to(o,{{k:1,duration:{dr:.2f},ease:"power1.inOut",onUpdate:()=>draw(o.k)}},{t0:.3f});}})();''')
    for i, (x, _) in enumerate(xy):
        ti = t0 + dr * (x - pl) / (W - pl - pr) * 0.97
        X.tw(f'tl.from("{s} .lcp[data-i=\'{i}\']", {{scale:0, transformOrigin:"50% 50%", transformBox:"fill-box", duration:0.3, ease:"back.out(3)"}}, {ti:.3f});')
        if n <= 8 or i % 3 == 0: X.sfx(ti, "tick")
    X.tw(f'tl.from("{s} .lca", {{opacity:0, duration:0.6}}, {t0 + dr * 0.6:.3f});')
    X.tw(f'tl.from("{s} .lce", {{y:20, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t0 + dr:.3f});')
    X.sfx(t0 + dr, "hit")


FX = {"line_draw": line_draw}
