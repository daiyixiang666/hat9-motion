"""雷达图 Radar / multi-axis comparison (Envato Popular「Polar Area Charts」; VideoHive Infographic Maker 2.6K):
the web of rings and spokes draws from the centre, each series inflates from the centre to its shape in turn,
vertices pop with their values, the legend names the series; one axis can be singled out.

Adapts: 3–10 axes (labels placed around the web, long names wrap), 1–3 series overlaid; raw values of any unit are
normalised per axis to the largest series value (or to `max` per axis) so mixed units can share a web — the raw
value is what gets printed. Labels from a glyph to a phrase.
p: axes [names] · series [{name, values}] · max [per-axis] · fmt [per-axis suffix] · hl (axis index) · title · note
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
SC = ["var(--accent)", "var(--fg)", "color-mix(in srgb, var(--accent) 45%, var(--fg))"]


def radar(X, cid, t, d, p):
    W.base(X)
    axes = [str(a) for a in p["axes"]][:10]
    k = len(axes)
    series = [{"name": str(s_.get("name", "")), "v": [float(W.num(v) or 0) for v in s_["values"]][:k]} for s_ in p["series"][:3]]
    mx = p.get("max") or [max(s_["v"][j] for s_ in series) or 1 for j in range(k)]
    sfx = p.get("fmt") or [""] * k
    hl = int(p.get("hl", -1))
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    P = X.portrait
    lab_room = 150 if not P else 120
    if P: cx, cy = (x0 + x1) / 2, y0 + hhpx + (y1 - y0 - hhpx - 110) / 2; R = min((x1 - x0) / 2 - lab_room, (y1 - y0 - hhpx - 110) / 2 - 50)
    else: cx, cy = x0 + (x1 - x0) * 0.42, y0 + hhpx + 20 + (y1 - y0 - hhpx - 20) / 2; R = min((x1 - x0) * 0.42 - lab_room, (y1 - y0 - hhpx - 20) / 2 - 95)
    ang = [-math.pi / 2 + 2 * math.pi * j / k for j in range(k)]
    pt = lambda j, r: (cx + r * math.cos(ang[j]), cy + r * math.sin(ang[j]))
    rings = []
    for lv in (0.25, 0.5, 0.75, 1.0):
        rings.append(f'<polygon class="rdr" points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in (pt(j, R * lv) for j in range(k)))}"/>')
    spokes = "".join(f'<line class="rds{" hl" if j == hl else ""}" x1="{cx:.1f}" y1="{cy:.1f}" x2="{pt(j, R)[0]:.1f}" y2="{pt(j, R)[1]:.1f}"/>' for j in range(k))
    shapes, verts, vals = [], [], []
    for si, s_ in enumerate(series):
        P_ = [pt(j, R * max(0.02, min(1.0, s_["v"][j] / mx[j]))) for j in range(k)]
        shapes.append(f'<g class="rdg" data-s="{si}" style="transform-origin:{cx:.1f}px {cy:.1f}px"><polygon class="rdp" points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in P_)}" style="fill:{SC[si]}; stroke:{SC[si]}"/></g>')
        for j, (a, b) in enumerate(P_):
            verts.append(f'<i class="rdv" data-s="{si}" style="left:{a - 7:.1f}px; top:{b - 7:.1f}px; background:{SC[si]}"></i>')
    labs = []
    for j, name in enumerate(axes):
        lx, ly = pt(j, R + 26)
        c = math.cos(ang[j])
        anchor = "translate(-50%,-100%)" if abs(c) < 0.25 and math.sin(ang[j]) < 0 else ("translate(-50%,0)" if abs(c) < 0.25 else ("translate(0,-50%)" if c > 0 else "translate(-100%,-50%)"))
        fs, ll = W.fit_px(X, name, lab_room + 40, 70, 30 if not P else 26, 18, 2)
        vline = " · ".join(f'<b style="color:{SC[si]}">{W.fmt(s_["v"][j], W.dec_of([s_["v"][j]]))}{X.rich(sfx[j] if j < len(sfx) else "")}</b>' for si, s_ in enumerate(series))
        labs.append(f'<div class="rdl{" hl" if j == hl else ""}" data-j="{j}" style="left:{lx:.1f}px; top:{ly:.1f}px; transform:{anchor}; font-size:{fs:.0f}px">{W.lines_html(X, ll)}<small>{vline}</small></div>')
    legend = "".join(f'<div class="rdlg" data-s="{si}"><i style="background:{SC[si]}"></i>{X.rich(s_["name"])}</div>' for si, s_ in enumerate(series))
    lg_pos = f"left:{x0}px; top:{y1 - 50}px" if P else f"left:{x0 + (x1 - x0) * 0.78:.0f}px; top:{cy - 60:.0f}px"
    X.css("fx-radar", """
.fx .rd .rdr { fill:none; stroke:color-mix(in srgb, var(--fg) 16%, transparent); stroke-width:1.5; }
.fx .rd .rds { stroke:color-mix(in srgb, var(--fg) 22%, transparent); stroke-width:1.5; } .fx .rd .rds.hl { stroke:var(--accent); stroke-width:3; }
.fx .rd .rdp { fill-opacity:.22; stroke-width:4; stroke-linejoin:round; }
.fx .rd .rdv { position:absolute; width:14px; height:14px; border-radius:50%; box-shadow:0 0 0 3px var(--bg); }
.fx .rd .rdl { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--fg); text-align:center; line-height:1.15; }
.fx .rd .rdl .fl { display:block; white-space:nowrap; } .fx .rd .rdl small { display:block; margin-top:4px; font:600 .72em var(--f-num, var(--f-body)); white-space:nowrap; }
.fx .rd .rdl.hl { color:var(--accent); }
.fx .rd .rdlgs { position:absolute; display:flex; flex-direction:column; gap:14px; }
#root.v .fx .rd .rdlgs { flex-direction:row; gap:28px; }
.fx .rd .rdlg { display:flex; align-items:center; gap:12px; font:800 28px var(--f-body); color:var(--fg); white-space:nowrap; } .fx .rd .rdlg i { width:22px; height:22px; border-radius:4px; }
""")
    svg = f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(rings)}{spokes}{"".join(shapes)}</svg>'
    inner = f'<div class="w3 rd">{hh}{svg}{"".join(verts)}{"".join(labs)}<div class="rdlgs" style="{lg_pos}">{legend}</div>{W.mock_tag(X, p, x1 - 70, y0)}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .rdr", {{scale:0, transformOrigin:"{cx:.1f}px {cy:.1f}px", opacity:0, duration:0.6, ease:"expo.out", stagger:0.06}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .rds", {{opacity:0, duration:0.4, stagger:0.04}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .rdl", {{opacity:0, scale:0.8, duration:0.4, stagger:0.05}}, {t + 0.4:.3f});')
    sp = min(0.9, max(0.5, (d - 2.0) / max(len(series), 1)))
    for si in range(len(series)):
        ti = t + 0.8 + si * sp
        X.tw(f'tl.from("{s} .rdg[data-s=\'{si}\']", {{scale:0, duration:0.7, ease:"back.out(1.6)"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .rdv[data-s=\'{si}\']", {{scale:0, duration:0.3, ease:"back.out(3)", stagger:0.04}}, {ti + 0.35:.3f});')
        X.tw(f'tl.from("{s} .rdlg[data-s=\'{si}\']", {{opacity:0, x:-14, duration:0.4}}, {ti:.3f});')
        X.sfx(ti, "whoosh_soft")
    if 0 <= hl < k:
        th = t + 0.8 + len(series) * sp + 0.1
        X.tw(f'tl.fromTo("{s} .rdl.hl", {{scale:1}}, {{keyframes:[{{scale:1.18, duration:0.14}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {th:.3f});')
        X.sfx(th, "hit")


FX = {"radar": radar}
