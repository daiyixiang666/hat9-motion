"""环形占比 Donut / Proportion Ring (D3, Envato Popular「Infographic Pie Chart 250+」; Move Shapes 环形图 17.6 万播放):
the ring sweeps to the share with a counter in the hole, the remainder stays a faint track, the label reads out.

Adapts: one share ("value": 0–100) or 2–6 segments ("segments": [[label, value], ...], any units — normalised;
each sweeps in turn with a legend), labels from a word to a sentence (fitted), the centre number shrinks for
long figures. p: value | segments · text · sub · center (override the centre text) · dec
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]
SEG = ["var(--accent)", "var(--fg)", "color-mix(in srgb, var(--accent) 45%, var(--bg))", "color-mix(in srgb, var(--fg) 45%, var(--bg))",
       "color-mix(in srgb, var(--accent) 70%, var(--fg))", "color-mix(in srgb, var(--fg) 22%, var(--bg))"]


def donut(X, cid, t, d, p):
    dec = int(p.get("dec", 1))
    if p.get("segments"):
        raw = [(str(a), max(0.0, float(b))) for a, b in p["segments"]][:6]
        tot = sum(b for _, b in raw) or 1
        segs = [(a, b / tot * 100) for a, b in raw]
    else:
        v = max(0.0, min(100.0, float(p["value"])))
        segs = [(p.get("text", ""), v)]
    main = segs[0][1]
    ctext = p.get("center")
    Wv, Hv = F.frame_vmin(X)
    ring = 46 if X.portrait else 52
    hole = ring * 0.6
    numstr = ctext or f"{main:.{dec}f}%"
    cs = min(12.0, hole * 0.92 / max(F.em(numstr), 1))
    tw = (Wv * 0.86) if X.portrait else min(62.0, Wv - ring - 30)
    ts, tl_ = F.fit(p.get("text", segs[0][0]), tw, 18, 6.0, 3.0, 3)
    X.css("fx-donut", """
.fx .dn { display:flex; align-items:center; gap:7vmin; }
#root.v .fx .dn { flex-direction:column; gap:4vmin; margin-top:-26vmin; }
.fx .dn .dnr { position:relative; flex:none; }
.fx .dn svg { width:100%; height:100%; transform:rotate(-90deg); overflow:visible; }
.fx .dn .dntr { fill:none; stroke:color-mix(in srgb, var(--fg) 12%, transparent); stroke-width:13; }
.fx .dn .dna { fill:none; stroke-width:13; stroke-linecap:butt; }
.fx .dn .dnc { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; }
.fx .dn .dnc b { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; color:var(--fg); font-variant-numeric:tabular-nums; letter-spacing:-.02em; white-space:nowrap; }
.fx .dn .dnc b small { font-size:.45em; color:var(--accent); margin-left:.1em; }
.fx .dn .dnt strong { display:block; font-family:var(--f-display); font-weight:900; line-height:1.18; color:var(--fg); }
.fx .dn .dnt strong .fl { display:block; white-space:nowrap; }
.fx .dn .dnt > span { display:block; margin-top:2vmin; font:500 2.6vmin/1.5 var(--f-body); color:var(--muted); }
.fx .dn .dnt i.sw { display:inline-block; width:2.2vmin; height:2.2vmin; margin-right:1.2vmin; vertical-align:-.2vmin; }
.fx .dn .dnlg { margin-top:2.4vmin; display:grid; gap:1.1vmin; }
.fx .dn .dnlg div { display:flex; align-items:center; gap:1.2vmin; font:700 2.8vmin var(--f-body); color:var(--fg); white-space:nowrap; }
.fx .dn .dnlg div i { width:2vmin; height:2vmin; flex:none; } .fx .dn .dnlg div b { font-family:var(--f-num, var(--f-display)); margin-left:auto; padding-left:2vmin; }
#root.v .fx .dn .dnt { text-align:center; } #root.v .fx .dn .dnlg { justify-items:center; }
""")
    C = 2 * 3.14159265 * 40
    arcs, acc = [], 0.0
    for i, (lab, v) in enumerate(segs):
        arcs.append(f'<circle class="dna" data-i="{i}" cx="50" cy="50" r="40" style="stroke:{SEG[i % len(SEG)]}" stroke-dasharray="{C * v / 100:.2f} {C:.2f}" stroke-dashoffset="{-C * acc / 100:.2f}"/>')
        acc += v
    legend = ""
    if len(segs) > 1:
        legend = '<div class="dnlg">' + "".join(f'<div><i style="background:{SEG[i % len(SEG)]}"></i>{X.rich(a)}<b>{b:.{dec}f}%</b></div>' for i, (a, b) in enumerate(segs)) + "</div>"
    X.used_text.update("0123456789.%")
    cen = f'<b style="font-size:{cs:.2f}vmin">{X.rich(ctext)}</b>' if ctext else f'<b style="font-size:{cs:.2f}vmin"><span class="n">0</span><small>%</small></b>'
    sw = '<i class="sw" style="background:var(--accent)"></i>' if len(segs) == 1 else ""
    inner = (f'<div class="dn"><div class="dnr" style="width:{ring}vmin; height:{ring}vmin"><svg viewBox="0 0 100 100"><circle class="dntr" cx="50" cy="50" r="40"/>{"".join(arcs)}</svg>'
             f'<div class="dnc">{cen}</div></div>'
             f'<div class="dnt" style="max-width:{tw:.1f}vmin"><strong style="font-size:{ts:.2f}vmin">{sw}{F.lines_html(X, tl_)}</strong>'
             f'<span>{X.rich(p.get("sub", ""))}</span>{legend}</div></div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dnr", {{scale:0.7, opacity:0, rotation:-30, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    per = min(1.2, max(0.35, (d - 1.4) / len(segs)))
    for i, (lab, v) in enumerate(segs):
        ti = t + 0.3 + i * per * 0.8
        X.tw(f'tl.from("{s} .dna[data-i=\'{i}\']", {{strokeDasharray:"0 {C:.2f}", duration:{per:.2f}, ease:"power3.inOut"}}, {ti:.3f});')
    if not ctext:
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .n"); tl.to(o, {{v:{main}, duration:{per:.2f}, ease:"power3.inOut", onUpdate:()=>{{el.textContent=o.v.toFixed({dec});}}}}, {t + 0.3:.3f});}})();')
    X.tw(f'tl.from("{s} .dnt strong", {{x:40, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.7:.3f});')
    X.tw(f'tl.from("{s} .dnt > span, {s} .dnlg div", {{x:40, opacity:0, duration:0.45, ease:"expo.out", stagger:0.08}}, {t + 0.85:.3f});')
    X.tw(f'tl.to("{s} .dnr", {{keyframes:[{{scale:1.05, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}]}}, {t + 0.3 + per + (len(segs) - 1) * per * 0.8:.3f});')
    X.sfx(t + 0.3, "whoosh_soft"); X.sfx(t + 0.3 + per, "hit")


FX = {"donut": donut}
