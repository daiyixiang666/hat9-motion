"""中国地图 · 省份高亮 / 分级设色 / 撒点 (China province map — the most-requested map shot in 商业拆解: 「门店集中在
哪几个省」「GDP 前五」; Envato "China Map Kit" / map infographic packs). The outline draws itself on, provinces fill,
highlighted ones light up in rank order with value labels and a ranked list beside the map, a choropleth
grades every province, store dots pop in waves; the camera can push into a region. Always with the 南海诸岛
inset (standard-map convention: South China Sea islands and the dashed line), Taiwan, Hong Kong and Macao in the
same treatment as the mainland, and no provincial data invented — pass the numbers you can cite.

Map data: Natural Earth admin-1 China provinces (public domain), projected at build time with an Albers
equal-area conic (25°N / 47°N, 105°E) — no CDN, deterministic. See data/CREDITS-china.md.

Adapts: 1–34 highlighted provinces; values for any subset (choropleth + top-N list, numbers auto 万/亿); dots
from a handful to ~600 (one dot = an auto unit); any province names (广东 / 广东省 / Guangdong / CN-GD).
p: highlight [names] | {name: label} · values {name: number} · top (N labelled) · unit · legend · dots {name: n}
   · dot_unit · points [[lon, lat, label]] · focus [names] · t_focus · hl (one name) · t_hl · title · mock
"""
from h9.aefx import _clip
from h9 import fit as FT
import importlib.util, json, math, pathlib, random, re, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")
DATA = pathlib.Path(__file__).parent / "data" / "china-provinces-ne.topo.json"
TENTH = [(122.55, 23.5), (122.75, 24.55)]            # 2013 standard map: the dash east of Taiwan (missing in Natural Earth)
_CACHE = {}


# ---------------------------------------------------------------- geometry (build time)
def _topo():
    if "t" in _CACHE: return _CACHE["t"]
    t = json.loads(DATA.read_text())
    sx, sy = t["transform"]["scale"]; tx, ty = t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def ring(ix):
        pts = []
        for i in ix:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    provs = []
    for g in t["objects"]["provinces"]["geometries"]:
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        provs.append({**g["properties"], "polys": [[ring(r) for r in poly] for poly in polys]})
    dashes = [[pt for i in g["arcs"] for pt in (arcs[i] if i >= 0 else arcs[~i][::-1])] for g in t["objects"]["ninedash"]["geometries"]]
    _CACHE["t"] = (provs, dashes + [TENTH])
    return _CACHE["t"]


P1, P2, L0 = math.radians(25), math.radians(47), math.radians(105)
_N = (math.sin(P1) + math.sin(P2)) / 2
_C = math.cos(P1) ** 2 + 2 * _N * math.sin(P1)
_R0 = math.sqrt(_C) / _N


def albers(lon, lat):
    th = _N * (math.radians(lon) - L0)
    r = math.sqrt(max(0.0, _C - 2 * _N * math.sin(math.radians(lat)))) / _N
    return r * math.sin(th), _R0 - r * math.cos(th)


def short(name): return re.sub(r"(壮族自治区|回族自治区|维吾尔自治区|自治区|特别行政区|省|市)$", "", str(name))


def _key(provs):
    k = {}
    for i, p in enumerate(provs):
        for v in (p["name"], short(p["name"]), p["name_en"].lower(), p["iso_3166_2"].lower(), p["adcode"]):
            k[str(v).lower()] = i
    k.update({"inner mongolia": k.get("inner mongol"), "macau": k.get("macao")})
    return k


def _find(k, name):
    s = str(name).strip().lower()
    return k.get(s, k.get(short(s), None))


def _area(r):
    return sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r))) / 2


def _centroid(r):
    a = _area(r) or 1e-9
    cx = sum((r[i][0] + r[i - 1][0]) * (r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1]) for i in range(len(r))) / (6 * a)
    cy = sum((r[i][1] + r[i - 1][1]) * (r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1]) for i in range(len(r))) / (6 * a)
    return cx, cy


def _inside(pt, r):
    x, y = pt; c = False
    for i in range(len(r)):
        x1, y1 = r[i - 1]; x2, y2 = r[i]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1: c = not c
    return c


def _d(pts, closed=True):
    out, last = [], None
    for x, y in pts:
        if last and abs(x - last[0]) + abs(y - last[1]) < 0.7: continue
        out.append(f"{x:.1f},{y:.1f}"); last = (x, y)
    if len(out) < 2: return ""
    return "M" + "L".join(out) + ("Z" if closed else "")


# ---------------------------------------------------------------- effect
def china_map(X, cid, t, d, p):
    SO.base_css(X)
    provs, dashes = _topo()
    K = _key(provs)
    W, H, P = X.W, X.H, X.portrait
    values = {}
    for nm, v in (p.get("values") or {}).items():
        i = _find(K, nm); vv = SO.num(v)
        if i is not None and vv is not None: values[i] = vv
    hl_raw = p.get("highlight") or []
    hl_lab = {}
    if isinstance(hl_raw, dict):
        for nm, lab in hl_raw.items():
            i = _find(K, nm)
            if i is not None: hl_lab[i] = lab
    else:
        for nm in FT.as_list(hl_raw):
            i = _find(K, nm)
            if i is not None: hl_lab[i] = values.get(i, "")
    dots = {}
    for nm, v in (p.get("dots") or {}).items():
        i = _find(K, nm); vv = SO.num(v)
        if i is not None and vv: dots[i] = vv
    ranked = sorted(values, key=lambda i: -values[i]) if values else list(hl_lab)
    top_n = int(p.get("top", min(5, len(ranked)) if values else len(hl_lab)))
    lab_set = (ranked[:top_n] if values else list(hl_lab))[:12]
    has_list = bool(lab_set) and p.get("list", True)
    # map box
    if P: mx0, mx1, my0, my1 = 40, W - 40, 290, (960 if has_list else 1220)
    else: mx0, mx1, my0, my1 = 120, (1180 if has_list else W - 120), 150, 900
    main_pts = []
    for pv in provs:
        for poly in pv["polys"]:
            lon = sum(q[0] for q in poly[0]) / len(poly[0]); lat = sum(q[1] for q in poly[0]) / len(poly[0])
            if lat >= 17.0: main_pts += [albers(*q) for q in poly[0]]
    xs = [q[0] for q in main_pts]; ys = [q[1] for q in main_pts]
    k = min((mx1 - mx0) / (max(xs) - min(xs)), (my1 - my0) / (max(ys) - min(ys)))
    ox = mx0 + ((mx1 - mx0) - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = my0 + ((my1 - my0) - k * (max(ys) - min(ys))) / 2 + k * max(ys)
    S = lambda lon, lat: (ox + k * albers(lon, lat)[0], oy - k * albers(lon, lat)[1])
    # inset (南海诸岛): same projection, its own scale, bottom-right of the map
    ix0, iy0 = albers(106.5, 25.5); ix1, iy1 = albers(124.5, 2.5)
    iw = (mx1 - mx0) * (0.17 if not P else 0.2)
    ik = iw / abs(ix1 - ix0); ih = ik * abs(iy0 - iy1)
    bx, by = (ox + k * max(xs)) - iw, (oy - k * min(ys)) - ih
    SI = lambda lon, lat: (bx + ik * (albers(lon, lat)[0] - ix0), by + ik * (iy0 - albers(lon, lat)[1]))
    paths, fills, cents, inset, order = [], [], {}, [], []
    for i, pv in enumerate(provs):
        d_main, d_ins, best = [], [], (0, None)
        for poly in pv["polys"]:
            lon = sum(q[0] for q in poly[0]) / len(poly[0]); lat = sum(q[1] for q in poly[0]) / len(poly[0])
            ring = [S(*q) for q in poly[0]]
            if lat >= 17.0:
                d_main.append(_d(ring) + "".join(_d([S(*q) for q in hole]) for hole in poly[1:]))
                a = abs(_area(ring))
                if a > best[0]: best = (a, ring)
            if 105 <= lon <= 125.5 and 2 <= lat <= 25.5 and pv["adcode"] in ("460000", "710000", "440000", "450000", "350000", "810000", "820000"):
                d_ins.append(_d([SI(*q) for q in poly[0]]))
        if best[1]:
            cents[i] = (_centroid(best[1]), best[1])
        dm = "".join(d_main)
        if dm:
            paths.append(f'<path class="wpm-p" data-i="{i}" d="{dm}" pathLength="1"/>')
            order.append((cents[i][0][0] if i in cents else 0, i))
            if i in values or i in hl_lab:
                if values:
                    lo, hi = min(values.values()), max(values.values())
                    r = (values.get(i, lo) - lo) / ((hi - lo) or 1)
                    col = f"color-mix(in srgb, var(--accent) {22 + 78 * r:.0f}%, var(--card))"
                else: col = "var(--accent)"
                fills.append((ranked.index(i) if i in ranked else 99, f'<path class="wpm-f" data-i="{i}" d="{dm}" style="fill:{col}"/>'))
        if d_ins: inset.append(f'<path class="wpm-ip" d="{"".join(d_ins)}"/>')
    dash_main = f'<path class="wpm-dash" d="{_d([S(*q) for q in TENTH], False)}"/>'
    dash_ins = "".join(f'<path class="wpm-dash" d="{_d([SI(*q) for q in ln], False)}"/>' for ln in dashes)
    fills_sorted = [f for _, f in sorted(fills, key=lambda z: z[0])]
    # dots
    dot_html, legend_dot = [], ""
    if dots:
        tot = sum(dots.values())
        unit = SO.num(p.get("dot_unit")) or FT.nice_unit(tot, lo=60, hi=420)
        rnd = random.Random(int(p.get("seed", 7)))
        allp = []
        for i, v in dots.items():
            if i not in cents: continue
            ring = cents[i][1]; cnt = max(1, round(v / unit))
            rx = [q[0] for q in ring]; ry = [q[1] for q in ring]
            got, tries = 0, 0
            while got < cnt and tries < cnt * 60:
                tries += 1
                pt = (rnd.uniform(min(rx), max(rx)), rnd.uniform(min(ry), max(ry)))
                if _inside(pt, ring): allp.append((i, pt)); got += 1
        org = cents[max(dots, key=dots.get)][0] if dots else (W / 2, H / 2)
        allp.sort(key=lambda z: math.hypot(z[1][0] - org[0], z[1][1] - org[1]) + rnd.uniform(0, 60))
        r = SO.px(X, 0.42 if len(allp) > 250 else 0.55 if len(allp) > 120 else 0.7)
        dot_html = [f'<circle class="wpm-dt" cx="{pt[0]:.1f}" cy="{pt[1]:.1f}" r="{r:.1f}"/>' for _, pt in allp]
        legend_dot = f'<div class="wpm-lg"><i class="wpm-ld"></i>= {X.rich(FT.fmt_num(unit))} {X.rich(p.get("unit", ""))}</div>'
    pins = []
    for q in FT.as_list(p.get("points")):
        lon, lat = float(q[0]), float(q[1]); x, y = S(lon, lat)
        pins.append(f'<div class="wpm-pin" style="left:{x:.0f}px; top:{y:.0f}px"><i></i>{f"<b>{X.rich(q[2])}</b>" if len(q) > 2 else ""}</div>')
    # labels on the map (greedy de-overlap)
    labels, boxes = [], []
    fmt = lambda v: (FT.fmt_num(v, dec=p.get("dec")) if isinstance(v, (int, float)) else str(v)) if v != "" else ""
    for rank, i in enumerate(lab_set):
        if i not in cents: continue
        (cx, cy), _ = cents[i]
        if provs[i]["adcode"] == "620000": cx, cy = cx - k * 0.02, cy          # Gansu's centroid sits outside its shape; nudge into it
        txt = short(provs[i]["name"]); val = fmt(values.get(i, hl_lab.get(i, "")))
        w = SO.px(X, 2.0) * (len(txt) + len(str(val)) * 0.6) + SO.px(X, 3)
        h = SO.px(X, 4.2)
        y = cy
        for _ in range(6):
            if not any(abs(cx - bx_) < (w + bw_) / 2 and abs(y - by_) < h for bx_, by_, bw_ in boxes): break
            y += h * 0.9
        boxes.append((cx, y, w))
        labels.append(f'<div class="wpm-lb" data-i="{i}" style="left:{cx:.0f}px; top:{y:.0f}px"><b>{X.rich(txt)}</b>{f"<span>{X.rich(val)}</span>" if val else ""}</div>')
    # ranked list beside (16:9) or below (9:16) the map
    lst = ""
    if has_list:
        vmax = max([values[i] for i in lab_set if i in values] or [1])
        rows = []
        for rk, i in enumerate(lab_set):
            v = values.get(i); bar = (v / vmax * 100) if v else 100
            rows.append(f'<div class="wpm-r" data-i="{i}"><em>{rk + 1}</em><b>{X.rich(short(provs[i]["name"]))}</b><span>{X.rich(fmt(values.get(i, hl_lab.get(i, ""))))}{X.rich(p.get("unit", "")) if values else ""}</span>'
                        f'<i style="width:{bar:.1f}%"></i></div>')
        if P: lx, ly, lw = 70, 990, W - 140
        else: lx, ly, lw = 1240, 220, W - 1240 - 130
        cols = 2 if (P and len(rows) > 3) else 1
        ht = p.get("legend") or p.get("title") or ""
        head = f'<div class="wpm-lt">{X.rich(ht)}</div>' if ht else ""
        lst = (f'<div class="wpm-list" style="left:{lx}px; top:{ly}px; width:{lw}px; grid-template-columns:repeat({cols}, 1fr)">'
               f'{head}{"".join(rows)}</div>')
    ins_box = (f'<clipPath id="wpmc-{cid}"><rect x="{bx:.1f}" y="{by:.1f}" width="{iw:.1f}" height="{ih:.1f}"/></clipPath>'
               f'<rect class="wpm-ib" x="{bx:.1f}" y="{by:.1f}" width="{iw:.1f}" height="{ih:.1f}"/>'
               f'<g class="wpm-ins" clip-path="url(#wpmc-{cid})">{"".join(inset)}{dash_ins}</g>')
    ins_lab = f'<div class="wpm-il" style="left:{bx + iw / 2:.0f}px; top:{by + ih - SO.px(X, 2.2):.0f}px">南海诸岛</div>'
    X.css("fx-wpm", """
.fx .wpm { position:absolute; inset:0; font-family:var(--f-body); color:var(--fg); }
.fx .wpm-cam { position:absolute; inset:0; transform-origin:0 0; }
.fx .wpm svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.fx .wpm-p { fill:color-mix(in srgb, var(--fg) 7%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 55%, transparent); stroke-width:1.2; stroke-linejoin:round; stroke-dasharray:1 1; }
.fx .wpm-f { stroke:var(--bg); stroke-width:1.2; opacity:0; }
.fx .wpm-dash { fill:none; stroke:color-mix(in srgb, var(--fg) 70%, transparent); stroke-width:2.2; stroke-linecap:round; }
.fx .wpm-ib { fill:color-mix(in srgb, var(--fg) 3%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 45%, transparent); stroke-width:1.4; }
.fx .wpm-ip { fill:color-mix(in srgb, var(--fg) 12%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 55%, transparent); stroke-width:.8; }
.fx .wpm-il { position:absolute; transform:translate(-50%,-50%); font-size:1.5vmin; font-weight:700; opacity:.6; white-space:nowrap; }
.fx .wpm-dt { fill:var(--accent); }
.fx .wpm-lb { position:absolute; transform:translate(-50%,-50%); display:flex; gap:.6vmin; align-items:baseline; white-space:nowrap; padding:.3vmin 1vmin; border-radius:.6vmin;
  background:color-mix(in srgb, var(--bg) 88%, transparent); box-shadow:0 .4vmin 1.2vmin rgba(0,0,0,.18); }
.fx .wpm-lb b { font-size:2vmin; font-weight:900; } .fx .wpm-lb span { font:900 2vmin var(--f-num, var(--f-body)); color:var(--accent); font-variant-numeric:tabular-nums; }
.fx .wpm-pin { position:absolute; } .fx .wpm-pin i { position:absolute; left:-.9vmin; top:-.9vmin; width:1.8vmin; height:1.8vmin; border-radius:50%; background:var(--accent); box-shadow:0 0 0 .5vmin color-mix(in srgb, var(--accent) 30%, transparent); }
.fx .wpm-pin b { position:absolute; left:1.6vmin; top:-1.4vmin; font-size:1.9vmin; font-weight:800; white-space:nowrap; }
.fx .wpm-list { position:absolute; display:grid; gap:1.4vmin 3vmin; }
.fx .wpm-lt { grid-column:1 / -1; font-size:2.2vmin; font-weight:700; opacity:.6; margin-bottom:.6vmin; }
.fx .wpm-r { position:relative; display:grid; grid-template-columns:3.6vmin auto 1fr; align-items:baseline; gap:1.2vmin; padding-bottom:1.1vmin; }
.fx .wpm-r em { font:900 2.6vmin var(--f-num, var(--f-body)); font-style:normal; color:var(--accent); }
.fx .wpm-r b { font-size:3vmin; font-weight:900; } .fx .wpm-r span { justify-self:end; font:900 3vmin var(--f-num, var(--f-body)); font-variant-numeric:tabular-nums; }
.fx .wpm-r i { position:absolute; left:4.8vmin; right:0; bottom:0; height:.7vmin; border-radius:.35vmin; background:var(--accent); transform-origin:0 50%; max-width:calc(100% - 4.8vmin); }
.fx .wpm-lg { position:absolute; display:flex; align-items:center; gap:.8vmin; font-size:1.9vmin; font-weight:700; opacity:.7; }
.fx .wpm-ld { width:1.4vmin; height:1.4vmin; border-radius:50%; background:var(--accent); }
.fx .wpm-tt { position:absolute; font-size:2.6vmin; font-weight:900; }
""")
    title = f'<div class="wpm-tt" style="left:{mx0}px; top:{my0 - SO.px(X, 1):.0f}px">{X.rich(p["title"])}</div>' if p.get("title") and not has_list else ""
    lgd = legend_dot.replace('class="wpm-lg"', f'class="wpm-lg" style="left:{mx0}px; top:{(oy - k * min(ys)) - SO.px(X, 3):.0f}px"') if legend_dot else ""
    mock = f'<i class="wp-mock" style="left:{mx0}px; top:{my0 + SO.px(X, 3.5):.0f}px">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    inner = (f'<div class="wpm"><div class="wpm-cam"><svg viewBox="0 0 {W} {H}">{"".join(paths)}{"".join(fills_sorted)}{dash_main}{ins_box}<g class="wpm-dots">{"".join(dot_html)}</g></svg>'
             f'{ins_lab}{"".join(pins)}{"".join(labels)}</div>{lst}{title}{lgd}{mock}</div>')
    X.used_text.update("南海诸岛0123456789.万亿=" + "".join(short(pv["name"]) for pv in provs))
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    # 1. the outline draws west → east, then the land fills
    order.sort()
    ids = [i for _, i in order]
    for j, i in enumerate(ids):
        X.tw(f'tl.fromTo("{s} .wpm-p[data-i=\'{i}\']", {{strokeDashoffset:1, fillOpacity:0}}, {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut"}}, {t + 0.05 + j * 0.012:.3f});')
    X.tw(f'tl.to("{s} .wpm-p", {{fillOpacity:1, duration:0.5}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("{s} .wpm-ib, {s} .wpm-ins, {s} .wpm-il, {s} .wpm-dash", {{opacity:0, duration:0.5}}, {t + 0.7:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    th = SO.cue(X, p, "t_hl", t, t + d * 0.72)
    ta = t + 1.0
    span = max(0.4, min(th, t + d - 0.5) - ta - 0.3)
    nf = len(fills_sorted)
    if nf:
        rev = list(reversed(fills_sorted)) if values else fills_sorted      # choropleth grows from low to high
        st = min(0.18, span * 0.6 / nf)
        for j, html in enumerate(rev):
            i = re.search(r'data-i="(\d+)"', html).group(1)
            X.tw(f'tl.to("{s} .wpm-f[data-i=\'{i}\']", {{opacity:1, duration:0.35}}, {ta + j * st:.3f});')
    if labels:
        stl = min(0.25, span * 0.7 / max(len(labels), 1))
        for j, i in enumerate(lab_set):
            tj = ta + 0.3 + j * stl
            X.tw(f'tl.from("{s} .wpm-lb[data-i=\'{i}\']", {{scale:0.4, opacity:0, duration:0.4, ease:"back.out(2.4)"}}, {tj:.3f});')
            X.tw(f'tl.from("{s} .wpm-r[data-i=\'{i}\']", {{x:30, opacity:0, duration:0.45, ease:"expo.out"}}, {tj:.3f});')
            X.tw(f'tl.from("{s} .wpm-r[data-i=\'{i}\'] i", {{scaleX:0, duration:0.6, ease:"power3.out"}}, {tj + 0.1:.3f});')
            if j < 6: X.sfx(tj, "pop")
        X.tw(f'tl.from("{s} .wpm-lt", {{opacity:0, y:10, duration:0.4}}, {ta:.3f});')
    if dot_html:
        nd = len(dot_html)
        X.tw(f'tl.from("{s} .wpm-dt", {{attr:{{r:0}}, duration:0.3, ease:"back.out(3)", stagger:{{amount:{min(span, 2.4):.2f}}}}}, {ta:.3f});')
        X.tw(f'tl.from("{s} .wpm-lg", {{opacity:0, duration:0.4}}, {ta:.3f});')
        X.sfx(ta, "count")
    if p.get("points"):
        X.tw(f'tl.from("{s} .wpm-pin", {{scale:0, opacity:0, duration:0.4, ease:"back.out(3)", stagger:0.12}}, {ta:.3f});')
    focus = [_find(K, f) for f in FT.as_list(p.get("focus"))]
    focus = [i for i in focus if i is not None and i in cents]
    if focus:
        pts = [q for i in focus for q in cents[i][1]]
        fx0, fx1 = min(q[0] for q in pts), max(q[0] for q in pts); fy0, fy1 = min(q[1] for q in pts), max(q[1] for q in pts)
        sc = min(2.0, (mx1 - mx0) * 0.7 / max(fx1 - fx0, 1), (my1 - my0) * 0.7 / max(fy1 - fy0, 1))
        cxm, cym = (mx0 + mx1) / 2, (my0 + my1) / 2
        tx = cxm - sc * (fx0 + fx1) / 2; ty = cym - sc * (fy0 + fy1) / 2
        tf = SO.cue(X, p, "t_focus", t, th - 0.2)
        X.tw(f'tl.to("{s} .wpm-cam", {{scale:{sc:.3f}, x:{tx:.1f}, y:{ty:.1f}, duration:1.0, ease:"power3.inOut"}}, {tf:.3f});')
        X.tw(f'tl.to("{s} .wpm-ib, {s} .wpm-ins, {s} .wpm-il, {s} .wpm-lg", {{opacity:0, duration:0.3}}, {tf:.3f});')
        X.sfx(tf, "zoom")
    one = _find(K, p.get("hl")) if p.get("hl") else None
    if one is not None:
        X.tw(f'tl.to("{s} .wpm-f:not([data-i=\'{one}\'])", {{opacity:0.35, duration:0.4}}, {th:.3f});')
        X.tw(f'tl.fromTo("{s} .wpm-lb[data-i=\'{one}\']", {{scale:1}}, {{scale:1.35, duration:0.45, ease:"back.out(2.2)"}}, {th:.3f});')
        X.tw(f'tl.to("{s} .wpm-r:not([data-i=\'{one}\'])", {{opacity:0.4, duration:0.4}}, {th:.3f});')
        X.sfx(th, "hit")


FX = {"china_map": china_map}
