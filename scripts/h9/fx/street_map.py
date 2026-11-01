"""街区级地图 Street-level map from your own GeoJSON (VideoHive Map Kit 1.4K, Map Route Generator 3.5K; the「这个路口开了
三家奶茶店」shot of 商业拆解 / 探店 videos): blocks and parks fade up, streets draw themselves (main roads first),
street names settle along them, places pop as pins with tags, and a route lights up with a walking dot and a
distance tag.

Street data is never fetched: pass your own GeoJSON (`geojson`) — LineStrings for streets (`kind`: major | minor |
rail, `name`), Polygons for blocks (`kind`: park | water | block | building), Points for places (`name`, `kind`:
shop | station | pin | hl). Draw-it-yourself 示意 maps work the same way; mark them with `mock`.
Adapts: any number of features (labels thinned when crowded), any extent (fitted with true aspect), an optional
route ([[lon, lat], ...] or the name of a LineString) and focus place.
p: geojson · route · route_label · hl (place name) · title · note · mock
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


def street_map(X, cid, t, d, p):
    W.base(X)
    g = json.loads(W.resolve(X, p["geojson"]).read_text())
    feats = g.get("features", [])
    allc = []
    for f in feats:
        geo = f["geometry"]; c = geo["coordinates"]
        if geo["type"] == "Point": allc.append(c)
        elif geo["type"] == "LineString": allc += c
        elif geo["type"] == "Polygon": allc += c[0]
    lon0 = sum(c[0] for c in allc) / len(allc); lat0 = sum(c[1] for c in allc) / len(allc)
    kx = math.cos(math.radians(lat0))
    xs = [(c[0] - lon0) * kx for c in allc]; ys = [c[1] - lat0 for c in allc]
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    mx0, my0, mx1, my1 = x0, y0 + hhpx, x1, y1
    k = min((mx1 - mx0) / ((max(xs) - min(xs)) or 1), (my1 - my0) / ((max(ys) - min(ys)) or 1)) * 0.94
    ox = mx0 + ((mx1 - mx0) - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = my0 + ((my1 - my0) - k * (max(ys) - min(ys))) / 2 + k * max(ys)
    S = lambda c: (ox + k * (c[0] - lon0) * kx, oy - k * (c[1] - lat0))
    m_per_px = 111320 / k              # degrees→metres at this latitude (y axis)
    polys, roads, names, places = [], [], [], []
    road_pts, lines, taken = {}, [], []
    for f in feats:
        geo, pr = f["geometry"], f.get("properties", {})
        kind = pr.get("kind", "")
        if geo["type"] == "Polygon":
            polys.append(f'<path class="smb {kind}" d="{W.path_d([S(c) for c in geo["coordinates"][0]])}"/>')
        elif geo["type"] == "LineString":
            pts = [S(c) for c in geo["coordinates"]]
            road_pts[pr.get("name", "")] = (geo["coordinates"], pts)
            lines.append((pr.get("name", ""), kind or "minor", pts))
            roads.append((0 if kind == "major" else 1 if kind != "rail" else 2,
                          f'<path class="smr {kind or "minor"}" data-k="{0 if kind == "major" else 1}" d="{W.path_d(pts, False)}" pathLength="1"/>'))
        elif geo["type"] == "Point":
            x, y = S(geo["coordinates"])
            is_hl = pr.get("name") == p.get("hl") or kind == "hl"
            nm = f'<b>{X.rich(pr["name"])}</b>' if pr.get("name") else ""
            places.append(f'<div class="smp {kind}{" hl" if is_hl else ""}" style="left:{x:.0f}px; top:{y:.0f}px"><i></i>{nm}</div>')
            taken.append((x - 18, y - 18, 36, 36))
            if pr.get("name"): taken.append((x + 20, y - 20, W.F.em(pr["name"]) * 28 + 12, 40))
    roads.sort(key=lambda r: r[0])
    # street names: beside the road, at the spot farthest from crossings, pins and other names
    for nm_, kind, pts in sorted([l for l in lines if l[0]], key=lambda l: l[1] != "major"):
        sw = 18 if kind == "major" else 9
        tw, th = W.F.em(nm_) * 18 * 1.1 + 6, 24
        best = None
        for i in range(len(pts) - 1):
            (ax, ay), (bx_, by_) = pts[i], pts[i + 1]
            L = math.dist(pts[i], pts[i + 1])
            if L < tw + 20: continue
            ang = math.degrees(math.atan2(by_ - ay, bx_ - ax))
            if ang > 90: ang -= 180
            if ang < -90: ang += 180
            nx, ny = -(by_ - ay) / L, (bx_ - ax) / L
            if ny > 0 or (abs(ny) < 1e-6 and nx > 0): nx, ny = -nx, -ny     # above, or left of a vertical road
            off = sw / 2 + th / 2 + 2
            ca, sa = abs(math.cos(math.radians(ang))), abs(math.sin(math.radians(ang)))
            bw, bh = ca * tw + sa * th, sa * tw + ca * th
            for f_ in (0.5, 0.3, 0.7, 0.2, 0.8, 0.4, 0.6):
                cx, cy = ax + (bx_ - ax) * f_ + nx * off, ay + (by_ - ay) * f_ + ny * off
                bxx = (cx - bw / 2, cy - bh / 2, bw, bh)
                if any(W.hit(bxx, o) for o in taken): continue
                if any(W.seg_hit(bxx, q[k], q[k + 1], 2) for n2, _, q in lines if n2 != nm_ for k in range(len(q) - 1)): continue
                score = min([W.seg_dist((cx, cy), q[k], q[k + 1]) for n2, _, q in lines if n2 != nm_ for k in range(len(q) - 1)] or [1e9])
                if not best or score > best[0]: best = (score, cx, cy, ang, bxx)
        if best:
            _, cx, cy, ang, bxx = best
            taken.append(bxx)
            names.append(f'<div class="smn" style="left:{cx:.0f}px; top:{cy:.0f}px; transform:translate(-50%,-50%) rotate({ang:.1f}deg)">{X.rich(nm_)}</div>')
    route_svg, route_pts, dist = "", [], 0.0
    rt = p.get("route")
    if rt:
        coords = road_pts[rt][0] if isinstance(rt, str) and rt in road_pts else rt
        route_pts = [S(c) for c in coords]
        dist = sum(math.dist(route_pts[i], route_pts[i + 1]) for i in range(len(route_pts) - 1)) * m_per_px
        route_svg = f'<path class="smrt" d="{W.path_d(route_pts, False)}" pathLength="1"/>'
    rlab = p.get("route_label") or (f"步行约 {round(dist / 10) * 10:.0f} 米" if dist else "")
    X.css("fx-street", """
.fx .sm .smwrap { position:absolute; inset:0; }
.fx .sm .smb { fill:color-mix(in srgb, var(--fg) 7%, var(--bg)); stroke:none; }
.fx .sm .smb.park { fill:color-mix(in srgb, #4caf50 22%, var(--bg)); } .fx .sm .smb.water { fill:color-mix(in srgb, #3b82f6 22%, var(--bg)); }
.fx .sm .smb.building { fill:color-mix(in srgb, var(--fg) 14%, var(--bg)); }
.fx .sm .smr { fill:none; stroke:color-mix(in srgb, var(--fg) 30%, var(--bg)); stroke-linecap:round; stroke-linejoin:round; stroke-width:9; }
.fx .sm .smr.major { stroke:color-mix(in srgb, var(--fg) 55%, var(--bg)); stroke-width:18; }
.fx .sm .smr.rail { stroke:var(--muted); stroke-width:4; stroke-dasharray:14 10; }
.fx .sm .smn { position:absolute; font:700 18px var(--f-body); color:var(--muted); white-space:nowrap; letter-spacing:.1em; }
.fx .sm .smp { position:absolute; width:0; height:0; }
.fx .sm .smp i { position:absolute; left:-12px; top:-12px; width:24px; height:24px; border-radius:50%; background:var(--fg); box-shadow:0 0 0 4px var(--bg); }
.fx .sm .smp.shop i { background:var(--accent); } .fx .sm .smp.station i { border-radius:6px; background:#2563eb; }
.fx .sm .smp.hl i { width:34px; height:34px; left:-17px; top:-17px; background:var(--accent); box-shadow:0 0 0 5px var(--bg), 0 0 0 9px var(--accent); }
.fx .sm .smp b { position:absolute; left:20px; top:-20px; font:800 28px var(--f-body); color:var(--fg); white-space:nowrap; background:color-mix(in srgb, var(--bg) 85%, transparent); padding:0 6px; border-radius:4px; }
.fx .sm .smrt { fill:none; stroke:var(--accent); stroke-width:8; stroke-linecap:round; stroke-linejoin:round; stroke-dasharray:1; }
.fx .sm .smdot { position:absolute; left:0; top:0; width:22px; height:22px; margin:-11px 0 0 -11px; border-radius:50%; background:var(--bg); border:5px solid var(--accent); opacity:0; }
.fx .sm .smrl { position:absolute; font:900 28px var(--f-display); color:var(--bg); background:var(--accent); padding:4px 14px; border-radius:6px; white-space:nowrap; }
""")
    svg = (f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}"><g class="smpoly">{"".join(polys)}</g>'
           f'{"".join(r for _, r in roads)}{route_svg}</svg>')
    rl = ""
    if route_pts and rlab:
        ex, ey = route_pts[-1]
        rw, rh_ = W.F.em(rlab) * 28 + 32, 46
        cands = [(ex + dx, ey + dy, rw, rh_) for dx, dy in ((24, 30), (24, -30 - rh_), (-24 - rw, 30), (-24 - rw, -30 - rh_), (-rw / 2, 40), (-rw / 2, -40 - rh_))]
        bxx = W.pick_box(cands, taken, [route_pts], (x0, my0, x1, y1)) or W.pick_box(cands, taken, (), (x0, my0, x1, y1)) or cands[0]
        rl = f'<div class="smrl" style="left:{bxx[0]:.0f}px; top:{bxx[1]:.0f}px">{X.rich(rlab)}</div>'
    inner = (f'<div class="w3 sm">{hh}<div class="smwrap">{svg}{"".join(names)}{"".join(places)}<i class="smdot"></i>{rl}</div>{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    X.used_text.update("步行约米0123456789")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    # a slow push-in toward the destination (or the map centre) keeps the frame alive while the route walks
    fx_, fy_ = route_pts[-1] if route_pts else ((mx0 + mx1) / 2, (my0 + my1) / 2)
    X.tw(f'tl.fromTo("{s} .smwrap", {{scale:1}}, {{scale:1.06, transformOrigin:"{fx_:.0f}px {fy_:.0f}px", duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .smpoly", {{opacity:0, duration:0.6}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .smr[data-k=\'0\']", {{strokeDasharray:1, strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut", stagger:0.08}}, {t + 0.2:.3f});')
    X.tw(f'tl.fromTo("{s} .smr[data-k=\'1\']", {{strokeDasharray:1, strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.6, ease:"power2.inOut", stagger:0.04}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .smn", {{opacity:0, duration:0.4, stagger:0.05}}, {t + 0.9:.3f});')
    X.tw(f'tl.from("{s} .smp", {{scale:0, y:-30, duration:0.45, ease:"back.out(2.5)", stagger:0.08}}, {t + 1.0:.3f});')
    X.sfx(t + 1.0, "pop")
    if route_pts:
        tr = t + 1.4 + 0.08 * len(places)
        dur = min(1.6, max(0.8, d - (tr - t) - 0.8))
        X.tw(f'tl.fromTo("{s} .smrt", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{dur:.2f}, ease:"none"}}, {tr:.3f});')
        # walking dot: resample the route by length so it moves at constant speed
        L = [0.0]
        for i in range(len(route_pts) - 1): L.append(L[-1] + math.dist(route_pts[i], route_pts[i + 1]))
        sp = []
        for j in range(21):
            target = L[-1] * j / 20
            i = max(0, min(len(L) - 2, next((q for q in range(len(L) - 1) if L[q + 1] >= target), len(L) - 2)))
            f_ = (target - L[i]) / ((L[i + 1] - L[i]) or 1)
            sp.append((route_pts[i][0] + (route_pts[i + 1][0] - route_pts[i][0]) * f_, route_pts[i][1] + (route_pts[i + 1][1] - route_pts[i][1]) * f_))
        W.travel(X, f"{s} .smdot", sp, tr, dur)
        X.tw(f'tl.from("{s} .smrl", {{scale:0, duration:0.4, ease:"back.out(2.5)"}}, {tr + dur:.3f});')
        X.sfx(tr + dur, "hit")


FX = {"street_map": street_map}
