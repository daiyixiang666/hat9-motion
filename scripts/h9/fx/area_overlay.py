"""面积对比 Area overlay — put A on top of B at true scale (the「把 A 国叠到 B 国上」map shot of Vox / Johnny Harris /
回形针; VideoHive Map Kit 1.4K, Infographics 3D Map Kit 3.2K): B's outline draws itself and fills, A flies in and
lands on B at the same kilometres-per-pixel, a scale bar settles, and the ratio counts up.

True scale: each shape is reprojected with a Lambert azimuthal equal-area projection centred on itself, then both
share one km → px factor, so the areas compare honestly wherever on Earth they are. Print the official areas
(`area`), the outline is only for the picture.

Shapes: a Chinese province (上海 / 上海市 / Shanghai / CN-SH; Natural Earth admin-1, China view, public domain), a
country (新加坡 / Singapore / SGP; Natural Earth 1:50m admin-0, China view), or your own GeoJSON (`geojson`) for
anything else or for finer outlines. Adapts: any size ratio (the bigger shape fits the box), names and notes from
a word to a sentence.
p: a {name, region | geojson, area, label} · b {…} · unit (km²) · title · note · mock
"""
from h9.aefx import _clip
import importlib.util, json, math, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
DATA = pathlib.Path(__file__).parent / "data"
_C = {}


def _feats():
    if "f" not in _C:
        _C["f"] = (W.topo(DATA / "china-provinces-ne.topo.json", "provinces"), W.topo(DATA / "world-chn-50m.topo.json"))
    return _C["f"]


def _rings(X, q):
    """-> list of outer rings (lon/lat) for a shape spec."""
    if q.get("geojson"):
        g = json.loads(W.resolve(X, q["geojson"]).read_text())
        out = []
        for f in g.get("features", [g]):
            geo = f.get("geometry", f)
            polys = [geo["coordinates"]] if geo["type"] == "Polygon" else geo["coordinates"]
            out += [[tuple(c[:2]) for c in poly[0]] for poly in polys]
        return out
    key = str(q.get("region", q.get("name", ""))).strip().lower()
    prov, world = _feats()
    import re
    short = lambda s: re.sub(r"(壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区|省|市)$", "", str(s))
    for f in prov:
        pr = f["props"]
        if key in {str(pr.get("name", "")).lower(), short(pr.get("name", "")).lower(), str(pr.get("name_en", "")).lower(), str(pr.get("iso_3166_2", "")).lower()}:
            return [poly[0] for poly in f["polys"]]
    for f in world:
        pr = f["props"]
        if key in {str(pr.get(k, "")).lower() for k in ("NAME_ZH", "NAME", "NAME_EN", "ISO_A3", "ADM0_A3", "ISO_A2")}:
            return [poly[0] for poly in f["polys"]]
    raise SystemExit(f"area_overlay: no shape for {key!r} (use a province / country name, ISO code, or a geojson)")


def _project(rings, islands=False):
    """LAEA centred on the shape; specks under 0.5 % of the main ring (far reefs, 南海 islets of 海南, 澎湖…) are left
    out of the picture unless islands=True, so the outline is centred on the land people recognise."""
    big = max(rings, key=lambda r: abs(W.ring_area(r)))
    lon0 = sum(q[0] for q in big) / len(big); lat0 = sum(q[1] for q in big) / len(big)
    f = W.laea(lon0, lat0)
    pr = [[f(*q) for q in r] for r in rings]
    amax = max(abs(W.ring_area(r)) for r in pr)
    if not islands: pr = [r for r in pr if abs(W.ring_area(r)) >= amax * 0.005]
    xs = [x for r in pr for x, _ in r]; ys = [y for r in pr for _, y in r]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return [[(x - cx, y - cy) for x, y in r] for r in pr], (max(xs) - min(xs), max(ys) - min(ys)), sum(abs(W.ring_area(r)) for r in pr)


def area_overlay(X, cid, t, d, p):
    W.base(X)
    a, b = p["a"], p["b"]
    ra, (aw, ah), area_a = _project(_rings(X, a), a.get("islands"))
    rb, (bw, bh), area_b = _project(_rings(X, b), b.get("islands"))
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx
    unit = p.get("unit", "km²")
    va, vb = W.num(a.get("area")), W.num(b.get("area"))
    # legend height first (9:16 stacks it under the map)
    lw = (x1 - x0) if P else (x1 - x0) * 0.36
    def row_h(q, v): return 38 * 1.2 + (24 * 1.25 + 2 if (v or q.get("label")) else 0)
    leg_h = row_h(b, vb) + row_h(a, va) + 44
    if P: mx0, my0, mx1, my1 = x0, top, x1, y1 - leg_h - 160
    else: mx0, my0, mx1, my1 = x0, top, x0 + (x1 - x0) * 0.6, y1
    W_, H_ = max(aw, bw), max(ah, bh)
    k = min((mx1 - mx0) / W_, (my1 - my0) / H_) * 0.86          # px per km, shared
    cx, cy = (mx0 + mx1) / 2, (my0 + my1) / 2
    def dd(rings): return "".join(W.path_d([(cx + x * k, cy - y * k) for x, y in r]) for r in rings)
    ratio = (vb or area_b) / (va or area_a) if (va or area_a) else 1      # official areas where given, outline km² otherwise
    big_is_b = ratio >= 1
    rr = ratio if big_is_b else 1 / ratio
    rtxt = p.get("ratio_text") or f"{(b if big_is_b else a).get('name', '')} ≈ {rr:,.{1 if rr < 20 else 0}f} 个 {(a if big_is_b else b).get('name', '')}"
    # scale bar: a round number of km ~ 1/4 of the map box
    raw = (mx1 - mx0) * 0.25 / k
    mag = 10 ** math.floor(math.log10(raw)); sb = min((m * mag for m in (1, 2, 5, 10) if m * mag >= raw * 0.6), default=mag)
    X.css("fx-areaov", """
.fx .ao .aob { fill:color-mix(in srgb, var(--fg) 12%, transparent); stroke:var(--fg); stroke-width:3; stroke-linejoin:round; }
.fx .ao .aoa { fill:color-mix(in srgb, var(--accent) 70%, transparent); stroke:var(--accent); stroke-width:3; stroke-linejoin:round; }
.fx .ao .aorg { fill:none; stroke:var(--accent); stroke-width:4; }
.fx .ao .aosb { position:absolute; height:8px; border:2px solid var(--fg); border-top:0; }
.fx .ao .aosbl { position:absolute; font:700 18px var(--f-mono, monospace); color:var(--fg); }
.fx .ao .aoleg { position:absolute; display:flex; flex-direction:column; gap:22px; }
.fx .ao .aol { display:flex; gap:16px; align-items:flex-start; }
.fx .ao .aol i { width:26px; height:26px; border-radius:5px; flex:none; margin-top:6px; }
.fx .ao .aol b { display:block; font:900 38px var(--f-display); color:var(--fg); }
.fx .ao .aol span { display:block; font:600 24px var(--f-num, var(--f-body)); color:var(--muted); margin-top:2px; }
.fx .ao .aor { font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.15; margin-top:10px; }
.fx .ao .aor b { color:var(--accent); }
.fx .ao .aor .fl { display:block; white-space:nowrap; }
""")
    small = max(aw, ah) * k < 36      # A is a speck at this scale: ring it so it can be found
    ring = f'<circle class="aorg" cx="{cx:.1f}" cy="{cy:.1f}" r="34"/>' if small else ""
    svg = (f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">'
           f'<path class="aob" d="{dd(rb)}" pathLength="1"/><g class="aoag"><path class="aoa" d="{dd(ra)}"/></g>{ring}</svg>')
    sbw = sb * k
    sbx, sby = mx0 + 10, my1 - 10
    rs, rl = W.fit_px(X, rtxt, lw, 160, 56 if not P else 48, 26, 2)
    leg_x, leg_y = (x0, y1 - leg_h - rs * 1.15 * len(rl) - 10) if P else (x0 + (x1 - x0) * 0.64, top + 40)
    def row(q, col, area):
        return (f'<div class="aol"><i style="background:{col}"></i><div><b>{X.rich(q.get("name", ""))}</b>'
                f'<span>{W.fmt(area, W.dec_of([area])) if area else ""} {X.rich(unit) if area else ""}{" · " + X.rich(q["label"]) if q.get("label") else ""}</span></div></div>')
    legend = (f'<div class="aoleg" style="left:{leg_x:.0f}px; top:{leg_y:.0f}px; width:{lw:.0f}px">{row(b, "color-mix(in srgb, var(--fg) 30%, transparent)", vb)}{row(a, "var(--accent)", va)}'
              f'<div class="aor" style="font-size:{rs:.0f}px">{W.lines_html(X, rl)}</div></div>')
    inner = (f'<div class="w3 ao">{hh}{svg}<i class="aosb" style="left:{sbx:.0f}px; top:{sby:.0f}px; width:{sbw:.0f}px"></i>'
             f'<div class="aosbl" style="left:{sbx:.0f}px; top:{sby - 30:.0f}px">{W.fmt(sb)} km</div>{legend}{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    X.used_text.update(rtxt + "0123456789.,km²≈个")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.fromTo("{s} .aob", {{strokeDasharray:1, strokeDashoffset:1, fillOpacity:0}}, {{strokeDashoffset:0, duration:{min(1.2, d * 0.25):.2f}, ease:"power2.inOut"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("{s} .aob", {{fillOpacity:1, duration:0.4}}, {t + 0.2 + min(1.2, d * 0.25):.3f});')
    ta = t + 0.4 + min(1.2, d * 0.25)
    X.tw(f'tl.from("{s} .aoag", {{x:{(mx1 - mx0) * 0.6:.0f}, y:-60, rotation:-12, opacity:0, svgOrigin:"{cx:.0f} {cy:.0f}", duration:0.9, ease:"expo.out"}}, {ta:.3f});')
    X.sfx(ta, "whoosh_soft")
    X.tw(f'tl.from("{s} .aosb, {s} .aosbl", {{opacity:0, duration:0.4}}, {ta + 0.3:.3f});')
    X.tw(f'tl.from("{s} .aol", {{x:30, opacity:0, duration:0.5, ease:"expo.out", stagger:0.12}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .aor .fl", {{yPercent:60, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {ta + 0.7:.3f});')
    X.tw(f'tl.fromTo("{s} .aoag", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.15}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], svgOrigin:"{cx:.0f} {cy:.0f}", immediateRender:false}}, {ta + 0.9:.3f});')
    X.sfx(ta + 0.9, "hit")
    if small:
        X.tw(f'tl.fromTo("{s} .aorg", {{scale:3, opacity:0}}, {{scale:1, opacity:1, svgOrigin:"{cx:.0f} {cy:.0f}", duration:0.6, ease:"expo.out", immediateRender:true}}, {ta + 0.8:.3f});')


FX = {"area_overlay": area_overlay}
