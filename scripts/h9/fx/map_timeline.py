"""版图扩张 / 逐年撒点 Expansion over time (VideoHive Map Route Generator 3.5K, World Map Animation 2.8K; the「一年一年
铺开」map of every brand-expansion or city-ranking video): a big year counter runs, and on each year the places
that joined pop onto the China map with a ripple and a name tag; a running total sits beside the counter and the
older dots settle into the base colour as new ones arrive.

Map: Natural Earth admin-1 China provinces (public domain), Albers equal-area, always with the 南海诸岛 inset and
the dashed line (standard-map convention), Taiwan, Hong Kong and Macao drawn like the mainland. Points are given
as lon / lat — pass real coordinates and real years; nothing is invented.

Adapts: 1–300 points over any span of years (time per year from the beat length; years without news are skipped
quickly), names on for small batches and off for big ones (`labels`), an optional unit for the counter.
p: points [[name, lon, lat, year], ...] · from · to · unit · labels (auto | all | none) · title · note · mock
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
CM = _load("china_map")          # geometry only: _topo / albers / _d / TENTH


def map_timeline(X, cid, t, d, p):
    W.base(X)
    provs, dashes = CM._topo()
    pts = [(str(q[0]), float(q[1]), float(q[2]), int(q[3])) for q in p["points"]]
    pts.sort(key=lambda q: q[3])
    ys = sorted({q[3] for q in pts})
    y_from, y_to = int(p.get("from", ys[0])), int(p.get("to", ys[-1]))
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx
    if P: mx0, my0, mx1, my1 = x0, top + 150, x1, y1
    else: mx0, my0, mx1, my1 = x0 + (x1 - x0) * 0.3, top, x1, y1
    main = []
    for pv in provs:
        for poly in pv["polys"]:
            lat = sum(q[1] for q in poly[0]) / len(poly[0])
            if lat >= 17.0: main += [CM.albers(*q) for q in poly[0]]
    xs = [q[0] for q in main]; yy = [q[1] for q in main]
    k = min((mx1 - mx0) / (max(xs) - min(xs)), (my1 - my0) / (max(yy) - min(yy)))
    ox = mx0 + ((mx1 - mx0) - k * (max(xs) - min(xs))) / 2 - k * min(xs)
    oy = my0 + ((my1 - my0) - k * (max(yy) - min(yy))) / 2 + k * max(yy)
    S = lambda lon, lat: (ox + k * CM.albers(lon, lat)[0], oy - k * CM.albers(lon, lat)[1])
    ix0, iy0 = CM.albers(106.5, 25.5); ix1, iy1 = CM.albers(124.5, 2.5)
    iw = (mx1 - mx0) * (0.16 if not P else 0.2); ik = iw / abs(ix1 - ix0); ih = ik * abs(iy0 - iy1)
    bx, by = (ox + k * max(xs)) - iw, (oy - k * min(yy)) - ih
    SI = lambda lon, lat: (bx + ik * (CM.albers(lon, lat)[0] - ix0), by + ik * (iy0 - CM.albers(lon, lat)[1]))
    paths, inset = [], []
    for pv in provs:
        dm, di = [], []
        for poly in pv["polys"]:
            lon = sum(q[0] for q in poly[0]) / len(poly[0]); lat = sum(q[1] for q in poly[0]) / len(poly[0])
            if lat >= 17.0: dm.append(CM._d([S(*q) for q in poly[0]]))
            if 105 <= lon <= 125.5 and 2 <= lat <= 25.5 and pv["adcode"] in ("460000", "710000", "440000", "450000", "350000", "810000", "820000"):
                di.append(CM._d([SI(*q) for q in poly[0]]))
        if dm: paths.append(f'<path class="mtp" d="{"".join(dm)}"/>')
        if di: inset.append(f'<path class="mtip" d="{"".join(di)}"/>')
    dash_main = f'<path class="mtdash" d="{CM._d([S(*q) for q in CM.TENTH], False)}"/>'
    dash_ins = "".join(f'<path class="mtdash" d="{CM._d([SI(*q) for q in ln], False)}"/>' for ln in dashes)
    lab_mode = p.get("labels", "auto")
    per_year = {}
    for q in pts: per_year.setdefault(q[3], []).append(q)
    dots, tags, leads = [], [], []
    cnt_x, cnt_y = (x0, top) if P else (x0, top + 40)
    xy = [SI(q[1], q[2]) if (q[2] < 17.0 and 105 <= q[1] <= 125.5) else S(q[1], q[2]) for q in pts]     # 南海 points go into the inset
    # tags never cover each other, a dot, the inset or the counter: right / left / above / below, else dot only
    taken = [(x - 10, y - 10, 20, 20) for x, y in xy] + [(bx, by, iw, ih), (cnt_x, cnt_y, 520 if P else 420, 150 if P else 260)]
    for i, (name, lon, lat, yr) in enumerate(pts):
        x, y = xy[i]
        dots.append(f'<i class="mtd" data-i="{i}" data-y="{yr}" style="left:{x:.1f}px; top:{y:.1f}px"><b></b></i>')
        show = lab_mode == "all" or (lab_mode == "auto" and len(per_year[yr]) <= 6)
        if not show: continue
        tw, th = W.F.em(name) * 22 + 12, 30
        own = [o for o in taken if not (abs(o[0] + 10 - x) < 0.5 and abs(o[1] + 10 - y) < 0.5)]
        cands = [(x + 13, y - th / 2), (x - 13 - tw, y - th / 2), (x - tw / 2, y - 14 - th), (x - tw / 2, y + 14)]
        cands += [(x + 13 + dx, y - th / 2 + dy) for dy in (-th + 4, th - 4, -th * 1.6, th * 1.6) for dx in (0, 12)]
        cands += [(x - 13 - tw, y - th / 2 + dy) for dy in (-th + 4, th - 4, -th * 1.6, th * 1.6)]
        boxes = [(cx, cy, tw, th) for cx, cy in cands]
        c = W.pick_box(boxes, own, (), (x0, top, x1, y1), pad=2)
        if not c: continue
        taken.append(c)
        if boxes.index(c) >= 4:     # pushed off its dot: a thin leader keeps the pair readable
            lx, ly = min(max(x, c[0]), c[0] + c[2]), min(max(y, c[1]), c[1] + c[3])
            leads.append(f'<line class="mtll" data-y="{yr}" x1="{x:.1f}" y1="{y:.1f}" x2="{lx:.1f}" y2="{ly:.1f}"/>')
        tags.append(f'<div class="mtt" data-i="{i}" data-y="{yr}" style="left:{c[0]:.1f}px; top:{c[1]:.1f}px">{X.rich(name)}</div>')
    X.css("fx-mtl", """
.fx .mt .mtp { fill:color-mix(in srgb, var(--fg) 7%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 40%, transparent); stroke-width:1.1; stroke-linejoin:round; }
.fx .mt .mtip { fill:color-mix(in srgb, var(--fg) 12%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 50%, transparent); stroke-width:.8; }
.fx .mt .mtib { fill:color-mix(in srgb, var(--fg) 3%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 45%, transparent); stroke-width:1.4; }
.fx .mt .mtdash { fill:none; stroke:color-mix(in srgb, var(--fg) 70%, transparent); stroke-width:2; stroke-linecap:round; }
.fx .mt .mtil { position:absolute; transform:translate(-50%,-50%); font:700 15px var(--f-body); color:var(--muted); white-space:nowrap; }
.fx .mt .mtd { position:absolute; width:0; height:0; }
.fx .mt .mtd::before { content:''; position:absolute; left:-9px; top:-9px; width:18px; height:18px; border-radius:50%; background:var(--accent); box-shadow:0 0 0 3px var(--bg); }
.fx .mt .mtd b { position:absolute; left:-9px; top:-9px; width:18px; height:18px; border-radius:50%; border:3px solid var(--accent); opacity:0; }
.fx .mt .mtt { position:absolute; height:30px; line-height:30px; font:800 22px/30px var(--f-body); color:var(--fg); white-space:nowrap; background:color-mix(in srgb, var(--bg) 80%, transparent); padding:0 6px; border-radius:4px; }
.fx .mt .mtll { stroke:var(--fg); stroke-width:1.5; opacity:.7; }
.fx .mt .mtc { position:absolute; }
.fx .mt .mtc .yr { font-size:150px; color:var(--fg); } .fx .mt .mtc .tot { display:flex; align-items:baseline; gap:10px; margin-top:14px; font:800 30px var(--f-body); color:var(--muted); }
.fx .mt .mtc .tot b { font:900 74px var(--f-num, var(--f-display)); color:var(--accent); }
#root.v .fx .mt .mtc .yr { font-size:120px; } #root.v .fx .mt .mtc { display:flex; align-items:flex-end; gap:40px; } #root.v .fx .mt .mtc .tot { margin-top:0; }
""")
    svg = (f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}"><defs><clipPath id="mtc-{cid}"><rect x="{bx:.1f}" y="{by:.1f}" width="{iw:.1f}" height="{ih:.1f}"/></clipPath></defs>'
           f'<g class="mtmap">{"".join(paths)}{dash_main}<rect class="mtib" x="{bx:.1f}" y="{by:.1f}" width="{iw:.1f}" height="{ih:.1f}"/>'
           f'<g clip-path="url(#mtc-{cid})">{"".join(inset)}{dash_ins}</g></g></svg>')
    ins_lab = f'<div class="mtil" style="left:{bx + iw / 2:.0f}px; top:{by + ih - 14:.0f}px">南海诸岛</div>'
    counter = (f'<div class="mtc" style="left:{cnt_x:.0f}px; top:{cnt_y:.0f}px"><div class="yr w3k"><span class="n">{y_from}</span></div>'
               f'<div class="tot"><b class="m">0</b>{X.rich(p.get("unit", ""))}</div></div>')
    lsvg = f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(leads)}</svg>' if leads else ""
    inner = f'<div class="w3 mt">{hh}{svg}{ins_lab}{lsvg}{"".join(dots)}{"".join(tags)}{counter}{W.mock_tag(X, p, x1 - 70, y0)}</div>'
    X.used_text.update("0123456789南海诸岛")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .mtmap", {{opacity:0, scale:0.96, svgOrigin:"{(mx0 + mx1) / 2:.0f} {(my0 + my1) / 2:.0f}", duration:0.7, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .mtil, {s} .mtc", {{opacity:0, duration:0.4}}, {t + 0.3:.3f});')
    t0, t1 = t + 0.6, t + d - 0.6
    span_y = max(1, y_to - y_from)
    # weighted timeline: years with points get more time than empty ones
    w = {yr: (3.0 if yr in per_year else 1.0) for yr in range(y_from, y_to + 1)}
    tot_w = sum(w.values())
    at, acc = {}, 0.0
    for yr in range(y_from, y_to + 1):
        at[yr] = t0 + (t1 - t0) * acc / tot_w; acc += w[yr]
    # the year counter steps through the same weighted times the dots use (piecewise-linear proxy, floor-printed)
    segs = ", ".join(f"[{at[yr]:.3f}, {(at[yr + 1] if yr + 1 in at else t1) - at[yr]:.3f}, {yr + 1}]" for yr in range(y_from, y_to))
    X.tw(f'(()=>{{const el=document.querySelector("{s} .mtc .yr .n"); const o={{v:{y_from}}}; const put=()=>{{el.textContent=String(Math.floor(o.v + 1e-6));}}; '
         f'[{segs}].forEach(([at, du, to]) => tl.to(o, {{v:to, duration:Math.max(0.05, du), ease:"none", onUpdate:put}}, at));}})();')
    run = 0
    for yr in sorted(per_year):
        if yr < y_from or yr > y_to: continue
        ty = at[yr]
        prev = run; run += len(per_year[yr])
        sel = f"{s} .mtd[data-y=\'{yr}\']"
        X.tw(f'tl.from("{sel}", {{scale:0, duration:0.4, ease:"back.out(3)", stagger:0.04}}, {ty:.3f});')
        X.tw(f'tl.fromTo("{sel} b", {{scale:1, opacity:0.9}}, {{scale:3.2, opacity:0, duration:0.8, ease:"power2.out", stagger:0.04}}, {ty:.3f});')
        has_tag = any(f'data-y="{yr}"' in tg for tg in tags)
        if has_tag: X.tw(f'tl.from("{s} .mtt[data-y=\'{yr}\']", {{opacity:0, x:-8, duration:0.3, stagger:0.04}}, {ty + 0.1:.3f});')
        if any(f'data-y="{yr}"' in ln for ln in leads):
            X.tw(f'tl.from("{s} .mtll[data-y=\'{yr}\']", {{opacity:0, duration:0.3}}, {ty + 0.1:.3f});')
        nxt = min([at[y2] for y2 in per_year if y2 > yr and y2 <= y_to] + [t1])
        if has_tag and nxt - ty > 0.9 and lab_mode != "all":
            X.tw(f'tl.to("{s} .mtt[data-y=\'{yr}\']", {{opacity:0.45, duration:0.3}}, {nxt:.3f});')
        W.count(X, f"{s} .mtc .tot .m", ty, run, dur=0.3, dec=0, start=prev)
        X.sfx(ty, "pop")


FX = {"map_timeline": map_timeline}
