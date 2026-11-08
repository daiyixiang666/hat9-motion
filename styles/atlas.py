"""atlas · 地图纪录 —— 一整张连续的世界地图当布景，镜头在地图上推拉摇移（Vox / Johnny Harris / 回形针 的地图段落）。
深海军蓝海面、纸色陆地、细国界、10° 经纬网；图框刻度、坐标读数、比例尺、右上角定位小图；
航线按真实海运网络算出来逐段描出，船标沿线行驶；危险区斜线填充；地名用纸色标签，按镜头自动避让；数据卡片放在画面一侧。
标题用思源宋体，数字和坐标用等宽字体。

整片是一个连续场景（WORLD），完全由数据驱动（写法见 examples/atlas/video.json 与 variants.json）：
  meta.places  {id: {ll:[lon,lat], name, sub?, value?, hot?, side?, small?}}   地名 / 港口 / 数据标注，任意个数
  meta.routes  {id: {from, to | coords, avoid?, color?, ship?}}                航线：searoute 海运网络最短路，或直接给坐标，任意条数与长度
  meta.zones   {id: {poly}} · meta.lines {id: {coords, label?}} · meta.seas [{ll, name, en, show:[beat ids]}] · meta.center_lon
  beat: camera(box | {fit:[...]} | "world") · moves · pins · draw · zones · cut · highlight · lines · detail · dim · clear · labels
        card(stat | bars | line | list | images | text) · title · thesis · outro · src
底图：Natural Earth 中国视角（world-chn-50m，公有领域）+ 南海断续线（10 段）；航线网络：searoute（Apache-2.0）。
"""
import os, json, math
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
_ROOTS = [Path(p) for p in __import__("os").environ.get("H9_MAP_DIR", "").split(__import__("os").pathsep) if p] + [
    SKILL / "assets" / "maps", SKILL / "examples" / "atlas" / "assets" / "map", *([Path(os.environ["H9_MEDIA"]) / "maps/vector"] if os.environ.get("H9_MEDIA") else [])]
_TEX = [SKILL / "examples" / "atlas" / "assets" / "map" / "paper-ambientcg-paper006.jpg",
        *([Path(os.environ["H9_MEDIA"]) / "textures/paper/paper-beige-fibrous_ambientcg-paper006.jpg"] if os.environ.get("H9_MEDIA") else [])]


def _lib(rel, required=True):
    """find a map file: $H9_MAP_DIR, assets/maps, examples/atlas/assets/map, then the local library (flat or in sub-folders)."""
    name = Path(rel).name
    for r in _ROOTS:
        for c in (r / rel, r / name):
            if c.exists(): return c
    if required: raise SystemExit(f"atlas: map file {rel} not found (set H9_MAP_DIR); looked in {', '.join(map(str, _ROOTS))}")
    return None

STYLE = {
    "name": "地图纪录", "en": "Atlas", "benchmarks": ["Vox 地图段落", "Johnny Harris", "回形针 PaperClip", "Kurzgesagt"],
    "tokens": {
        "bg": "#0f2733", "fg": "#f4efe3", "muted": "#a9bcc1", "accent": "#ffb02e", "accent2": "#ff5b3a", "alert": "#ff4a3d",
        "line": "#2b4652", "paper": "#ebe3cf", "ink": "#0f2733", "card": "#0b1d26", "card-fg": "#f4efe3",
        "sea": "#0f2733", "sea2": "#163644", "land": "#e9e1cc", "border": "#b9ad92", "route1": "#ffb02e", "route2": "#ff5b3a", "route3": "#6fd0ff",
        "cap-fg": "#fbf7ec", "cap-size": "42px", "cap-weight": "700", "cap-bottom": "58px", "cap-em": "#ffb02e",
        "cap-shadow": "0 2px 0 rgba(4,14,19,.9), 0 0 22px rgba(4,14,19,.85)", "punch-top": "70%", "punch-size": "76px", "punch-stroke": "0",
    },
    "fonts": {"display": "noto-serif-sc", "body": "noto-sans-sc", "mono": "jetbrains-mono", "latin": "eb-garamond-italic"},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.04, "cut": "hard", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07}), ("vignette", {"alpha": 0.4, "inner": 60})],
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 96, "bottom": 30, "h": 360}, "portrait": {"right": 40, "bottom": 560, "h": 320}},
    "sfx": {"transition": ("whoosh_soft", 0.3), "enter": ("whoosh_soft", 0.3), "pop": ("tick", 0.45), "hit": ("hit", 0.4), "mascot": ("whoosh_soft", 0.3),
            "count": ("type", 0.3), "fly": ("whoosh_deep", 0.35), "pin": ("click", 0.35), "alarm": ("beep", 0.22)},
}

K = 620.0                     # projection scale
PW, PH = 3420, 1800           # map plane (px)
TX, TY = PW / 2, PH / 2
ROUTE_COLORS = ["var(--route1)", "var(--route2)", "var(--route3)", "#c58cff", "#7be0a0", "#ff8fb1"]


# ================================================================ text fitting (balanced, never inside a word)
def _unit(ch):
    o = ord(ch)
    if o >= 0x2E80 or ch in "，。、：；！？“”（）《》—…·": return 1.0
    if ch == " ": return 0.28
    if ch.isdigit(): return 0.62
    if ch.isupper(): return 0.72
    if ch.islower(): return 0.58
    return 0.6


def _words(text):
    """jieba words, punctuation glued to the word before it, Latin runs kept whole; '|' is a forced break."""
    from h9 import core
    out = []
    for part in str(text).split("|"):
        toks = []
        for w in core.words(part):
            if not w: continue
            if toks and (all(c in "，。、：；！？”）》%" for c in w) or w == " "):
                toks[-1] += w
            else: toks.append(w)
        out.append(toks)
    return out


def fit(text, maxw, maxh, maxpx, minpx=16, lh=1.18, maxlines=3):
    """largest font size (px) at which `text` wraps into ≤ maxlines lines of ≤ maxw px, total height ≤ maxh. Returns (size, lines)."""
    paras = _words(str(text).replace("*", ""))
    for size in range(int(maxpx), int(minpx) - 1, -2):
        lines, ok = 0, True
        for toks in paras:
            cur = 0.0; lines += 1
            for w in toks:
                ww = sum(_unit(c) for c in w) * size
                if ww > maxw: ok = False; break
                if cur + ww > maxw and cur > 0: lines += 1; cur = ww
                else: cur += ww
            if not ok: break
        if ok and lines <= maxlines and lines * lh * size <= maxh: return size, lines
    return int(minpx), maxlines


def words_html(X, text, chars=True):
    """markup with each word unbreakable (span.w) and optional per-glyph spans for staggers; *强调* → em; '|' → <br>."""
    from h9.core import esc
    X.used_text.update(str(text))
    out, em = [], False
    for pi, part in enumerate(str(text).split("|")):
        if pi: out.append("<br>")
        for seg_i, seg in enumerate(part.split("*")):
            if seg_i: em = not em; out.append('<em class="em"><span class="emt">' if em else "</span></em>")
            for toks in _words(seg):
                for w in toks:
                    inner = "".join(f'<i class="c">{esc(c)}</i>' if c.strip() else " " for c in w) if chars else esc(w)
                    out.append(f'<span class="w">{inner}</span>')
    if em: out.append("</span></em>")
    return "".join(out)


# ================================================================ projection (identical to d3.geoNaturalEarth1().rotate([-L0, 0]))
class Proj:
    def __init__(self, center):
        self.L0 = float(center)

    def lam(self, lon): return ((lon - self.L0 + 180) % 360) - 180

    def __call__(self, lon, lat):
        lam = math.radians(self.lam(lon)); phi = math.radians(max(-89.9, min(89.9, lat)))
        p2 = phi * phi; p4 = p2 * p2
        x = lam * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
        y = phi * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
        return TX + K * x, TY - K * y

    def line(self, lls):
        """project a lon/lat polyline, split where it crosses the map seam (a trans-Pacific route never smears across)."""
        parts, cur, prev = [], [], None
        for lon, lat in lls:
            l = self.lam(lon)
            if prev is not None and abs(l - prev) > 180:
                if len(cur) > 1: parts.append(cur)
                cur = []
            cur.append(self(lon, lat)); prev = l
        if len(cur) > 1: parts.append(cur)
        return parts


def px_per_km(lat):
    phi = math.radians(lat); p2 = phi * phi; p4 = p2 * p2
    a = 0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4))
    return K * a / (6371.0 * max(math.cos(phi), 0.05))


def d_of(parts, close=False):
    return "".join("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + ("Z" if close else "") for pts in parts if pts)


def length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def resample(parts, n):
    """n+1 positions evenly spaced along the (possibly split) polyline, with heading."""
    segs = [(a, b) for pts in parts for a, b in zip(pts, pts[1:])]
    lens = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in segs]
    L = sum(lens) or 1; out, i, acc = [], 0, 0.0
    for k in range(n + 1):
        dd = L * k / n
        while i < len(segs) - 1 and acc + lens[i] < dd: acc += lens[i]; i += 1
        a, b = segs[i]; f = 0 if lens[i] == 0 else min(1, (dd - acc) / lens[i])
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))))
    return out


def clip_rect(ring, x0, y0, x1, y1):
    def inter(a, b, axis, v):
        t = (v - a[axis]) / (b[axis] - a[axis]) if b[axis] != a[axis] else 0
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    for axis, v, keep in ((0, x0, lambda p: p[0] >= x0), (0, x1, lambda p: p[0] <= x1), (1, y0, lambda p: p[1] >= y0), (1, y1, lambda p: p[1] <= y1)):
        out = []
        for i, cur in enumerate(ring):
            prev = ring[i - 1]
            if keep(cur):
                if not keep(prev): out.append(inter(prev, cur, axis, v))
                out.append(cur)
            elif keep(prev): out.append(inter(prev, cur, axis, v))
        ring = out
        if not ring: break
    return ring


# ================================================================ data
_NET = {}


def _hav(p, q):
    la1, lo1, la2, lo2 = map(math.radians, (p[1], p[0], q[1], q[0]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 3440.065 * math.asin(math.sqrt(min(1, h)))


def sea_route(a, b, avoid=()):
    """shortest sea path (nautical miles) on the searoute network.
    avoid: redsea | suez | panama | malacca | hormuz | gibraltar | bosporus; Arctic passages are off unless 'allow_arctic'."""
    import heapq
    if not _NET:
        g = json.loads(_lib("shipping/marnet_searoute-py.geojson").read_text())
        adj = {}
        key = lambda p: (round(p[0], 4), round(p[1], 4))
        for f in g["features"]:
            geo = f["geometry"]; ps = f["properties"].get("passage")
            for cs in ([geo["coordinates"]] if geo["type"] == "LineString" else geo["coordinates"]):
                for p, q in zip(cs, cs[1:]):
                    kp, kq = key(p), key(q); d = _hav(p, q)
                    adj.setdefault(kp, []).append((kq, d, ps)); adj.setdefault(kq, []).append((kp, d, ps))
        _NET["adj"] = adj; _NET["nodes"] = list(adj)
    adj, nodes = _NET["adj"], _NET["nodes"]
    near = lambda p: min(nodes, key=lambda n: _hav(n, p))
    av = set(avoid) | ({"arctic"} if "allow_arctic" not in avoid else set())
    def blocked(v, ps):
        if "arctic" in av and (ps in ("bering", "northwest") or v[1] > 62): return True
        if ("redsea" in av or "suez" in av) and (ps == "babalmandab" or (31 < v[0] < 44 and 12 < v[1] < 32)): return True
        if "panama" in av and (ps == "panama" or (-80.5 < v[0] < -78.5 and 8 < v[1] < 10)): return True
        if "malacca" in av and ps == "malacca": return True
        if "hormuz" in av and ps == "ormuz": return True
        if "gibraltar" in av and ps == "gibraltar": return True
        if "bosporus" in av and ps in ("bosporus", "dardanelles"): return True
        return False
    s, t = near(a), near(b); dist = {s: 0}; prev = {}; pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t: break
        if d > dist[u]: continue
        for v, w, ps in adj[u]:
            if blocked(v, ps): continue
            if d + w < dist.get(v, 1e18): dist[v] = d + w; prev[v] = u; heapq.heappush(pq, (d + w, v))
    if t not in dist: raise SystemExit(f"atlas: no sea route {a} → {b} with avoid={sorted(av)}")
    path = [t]
    while path[-1] != s: path.append(prev[path[-1]])
    return path[::-1], dist[t]


def dashline(P):
    """南海断续线: Natural Earth's 9 segments + the segment east of Taiwan (2013 standard map), placed by hand."""
    g = json.loads(_lib("naturalearth/ne_10m_admin_0_boundary_lines_maritime_indicator_chn.geojson").read_text())
    segs = [f["geometry"]["coordinates"] for f in g["features"] if f["geometry"]["type"] == "LineString"]
    segs.append([(122.55, 23.5), (122.75, 24.55)])
    return "".join(d_of(P.line(s)) for s in segs)


_DET = {}


def detail(P, box):
    """10 m coastlines clipped to a lon/lat box, for close-ups (the 50 m data is too coarse below ~200 km)."""
    if "g" not in _DET:
        f = _lib("ne_10m_admin_0_countries_chn.geojson", required=False)
        _DET["g"] = json.loads(f.read_text()) if f else {"features": []}     # without the 13 MB 10 m file, close-ups use the 50 m map
    x0, y0, x1, y1 = box; out = []
    for f in _DET["g"]["features"]:
        geo = f["geometry"]
        for poly in ([geo["coordinates"]] if geo["type"] == "Polygon" else geo["coordinates"]):
            ring = poly[0]; xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
            if max(xs) < x0 or min(xs) > x1 or max(ys) < y0 or min(ys) > y1: continue
            r = clip_rect([tuple(p) for p in ring], x0, y0, x1, y1)
            if len(r) > 2:
                a3 = f["properties"].get("ADM0_A3", "")
                a3 = "CHN" if a3 in ("HKG", "MAC") else a3
                out.append(f'<path class="detl d-{a3}" d="{d_of([[P(*p) for p in r]], True)}"/>')
    return "".join(out)


# ================================================================ CSS
CSS = r"""
.st-atlas .em .emb { display:none; }
.st-atlas .w { white-space:nowrap; }
.st-atlas .em .emt { color:var(--accent); }
.at-map { background:radial-gradient(ellipse 80% 70% at 50% 45%, var(--sea2), var(--sea) 70%); overflow:hidden; }
#mapcam { position:absolute; left:0; top:0; width:3420px; height:1800px; transform-origin:0 0; --z:1; }
#mapsvg { position:absolute; left:0; top:0; overflow:visible; }
#mapsvg .grat { fill:none; stroke:rgba(214,232,236,.08); stroke-width:calc(1px / var(--z)); }
#mapsvg .c { fill:var(--land); stroke:var(--border); stroke-width:calc(.8px / var(--z)); stroke-linejoin:round; }
#mapsvg .c-CHN { fill:#e6dcc3; }
#mapsvg .dash { fill:none; stroke:#c46a4a; stroke-width:calc(1.6px / var(--z)); stroke-linecap:round; }
#mapsvg .det { opacity:0; } #mapsvg .det .detl { fill:var(--land); stroke:var(--border); stroke-width:calc(1px / var(--z)); stroke-linejoin:round; }
#mapsvg .tex { opacity:.35; mix-blend-mode:multiply; }
#mapsvg .route { fill:none; stroke-linecap:round; stroke-linejoin:round; stroke-width:calc(4.5px / var(--z)); }
#mapsvg .glow { fill:none; stroke-linecap:round; stroke-width:calc(14px / var(--z)); opacity:.22; filter:blur(calc(3px / var(--z))); }
#mapsvg .cut { fill:none; stroke:var(--alert); stroke-width:calc(5px / var(--z)); stroke-dasharray:1.6 1.1; stroke-linecap:round; opacity:0; }
#mapsvg .zone { stroke:var(--alert); stroke-width:calc(2px / var(--z)); opacity:0; }
#mapsvg .wline { fill:none; stroke:#5fd2ff; stroke-width:calc(5px / var(--z)); stroke-linecap:round; stroke-linejoin:round; opacity:0; }
#mapsvg .wglow { fill:none; stroke:#5fd2ff; stroke-width:calc(22px / var(--z)); opacity:0; filter:blur(calc(6px / var(--z))); }
.mk { position:absolute; width:0; height:0; }
.mk > .in { position:absolute; left:0; top:0; transform:scale(calc(1 / var(--z))); transform-origin:0 0; }
.pin .dot { position:absolute; left:-9px; top:-9px; width:18px; height:18px; border-radius:50%; background:var(--fg); box-shadow:0 0 0 4px rgba(15,39,51,.65), 0 0 0 6px var(--fg); }
.pin.sm .dot { left:-6px; top:-6px; width:12px; height:12px; }
.pin .ring { position:absolute; left:-26px; top:-26px; width:52px; height:52px; border-radius:50%; border:2px solid var(--fg); opacity:0; }
.pin.hot .dot { background:var(--alert); box-shadow:0 0 0 4px rgba(15,39,51,.65), 0 0 0 6px var(--alert); }
.lab { position:absolute; white-space:nowrap; background:rgba(236,228,208,.95); padding:3px 11px 5px; border-radius:3px; box-shadow:0 3px 12px rgba(4,14,19,.4); opacity:0; }
.lab b { display:block; font-family:var(--f-display); font-weight:900; line-height:1.2; color:var(--ink); }
.lab > span { display:block; font-family:var(--f-mono); letter-spacing:.04em; color:#33505b; }
.lab .val { font-family:var(--f-mono); font-weight:700; line-height:1.1; color:#b5300f; }
.pin.hot .lab { border-left:4px solid var(--alert); }
.sea .in > div { position:absolute; left:0; top:0; transform:translate(-50%,-50%); white-space:nowrap; text-align:center; font-family:var(--f-latin), var(--f-display); font-style:italic; font-size:20px; letter-spacing:.3em; color:rgba(200,226,232,.78); }
.sea .in b { font-family:var(--f-display); font-style:normal; font-weight:700; letter-spacing:.5em; font-size:26px; display:block; color:rgba(220,236,240,.88); }
.ship .in > i { position:absolute; left:-15px; top:-11px; width:30px; height:22px; clip-path:polygon(0 0, 70% 0, 100% 50%, 70% 100%, 0 100%); }
.ship .in > em { position:absolute; left:-36px; top:-3px; width:26px; height:6px; border-radius:3px; opacity:.7; }
.xmark .in > i { position:absolute; left:-30px; top:-30px; width:60px; height:60px; }
.xmark .in > i::before, .xmark .in > i::after { content:''; position:absolute; left:26px; top:-4px; width:9px; height:68px; background:var(--alert); border-radius:4px; transform:rotate(45deg); box-shadow:0 0 0 3px rgba(15,39,51,.7); }
.xmark .in > i::after { transform:rotate(-45deg); }
.wlab .in > div { position:absolute; left:30px; top:-24px; white-space:nowrap; font-family:var(--f-mono); font-weight:700; font-size:30px; color:#0b1d26; background:#7fe0ff; padding:2px 12px; border-radius:3px; }
.at-frame { pointer-events:none; }
.at-frame .scT { position:absolute; left:0; right:0; top:0; height:140px; background:linear-gradient(rgba(6,18,24,.78), rgba(6,18,24,0)); }
.at-frame .scB { position:absolute; left:0; right:0; bottom:0; height:220px; background:linear-gradient(rgba(6,18,24,0), rgba(6,18,24,.82)); }
.at-frame .nl { position:absolute; inset:22px; border:1.5px solid rgba(244,239,227,.55); }
.at-frame .nl2 { position:absolute; inset:30px; border:1px solid rgba(244,239,227,.22); }
.at-frame .tk { position:absolute; background:rgba(244,239,227,.5); }
.at-frame .hd { position:absolute; left:58px; top:46px; display:flex; align-items:baseline; gap:18px; color:var(--fg); }
.at-frame .hd b { font-family:var(--f-display); font-weight:900; font-size:26px; letter-spacing:.06em; }
.at-frame .hd span { font-family:var(--f-mono); font-size:16px; letter-spacing:.2em; color:var(--muted); }
.at-frame .src { position:absolute; left:58px; bottom:30px; font-family:var(--f-mono); font-size:15px; letter-spacing:.03em; color:#e4eef0; text-shadow:0 1px 3px #061218; max-width:1180px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.at-frame .coord { position:absolute; right:58px; bottom:30px; font-family:var(--f-mono); font-size:16px; letter-spacing:.12em; color:var(--muted); text-align:right; }
.at-frame .sb { position:absolute; left:58px; bottom:72px; }
.at-frame .sb .bar { height:8px; background:repeating-linear-gradient(90deg, var(--fg) 0 25%, transparent 25% 50%); border:1.5px solid var(--fg); }
.at-frame .sb .n { margin-top:6px; font-family:var(--f-mono); font-size:16px; color:var(--fg); letter-spacing:.08em; display:flex; justify-content:space-between; text-shadow:0 1px 3px #061218, 0 0 10px #061218; }
.at-frame .loc { position:absolute; right:58px; top:96px; width:300px; height:158px; background:rgba(8,22,29,.82); border:1.5px solid rgba(244,239,227,.55); overflow:hidden; }
.at-frame .loc svg { position:absolute; left:0; top:0; }
.at-frame .loc .ll { fill:#c9bfa6; stroke:none; }
.at-frame .loc .vp { fill:rgba(255,176,46,.18); stroke:var(--accent); stroke-width:2; }
.at-frame .loc .cap { position:absolute; left:8px; bottom:4px; font-family:var(--f-mono); font-size:12px; letter-spacing:.18em; color:var(--muted); }
#root.v .at-frame .scT { height:300px; } #root.v .at-frame .scB { height:720px; background:linear-gradient(rgba(6,18,24,0), rgba(6,18,24,.8) 20%, rgba(6,18,24,.92)); }
#root.v .at-frame .nl { inset:150px 18px 300px; } #root.v .at-frame .nl2 { inset:158px 26px 308px; }
#root.v .at-frame .hd { left:44px; top:176px; } #root.v .at-frame .src { left:44px; bottom:auto; top:1478px; max-width:990px; }
#root.v .at-frame .coord { right:44px; bottom:auto; top:1560px; } #root.v .at-frame .sb { left:44px; bottom:auto; top:1262px; }
#root.v .at-frame .loc { right:44px; top:226px; width:250px; height:132px; }
.at-ov { pointer-events:none; }
.at-title { position:absolute; left:96px; top:132px; }
.at-title .k { font-family:var(--f-mono); font-size:19px; letter-spacing:.28em; color:var(--accent); text-transform:uppercase; }
.at-title .t { margin-top:10px; font-family:var(--f-display); font-weight:900; line-height:1.14; color:var(--fg); text-shadow:0 4px 30px rgba(4,14,19,.85); text-wrap:balance; }
.at-title .r { margin-top:18px; width:120px; height:4px; background:var(--accent); transform-origin:0 50%; }
.card { position:absolute; background:rgba(8,22,29,.9); border:1px solid rgba(244,239,227,.35); border-left:4px solid var(--accent); padding:20px 26px 22px; color:var(--fg); box-shadow:0 20px 60px rgba(0,0,0,.45); }
.card.red { border-left-color:var(--route2); }
.card .k { font-family:var(--f-mono); font-size:16px; letter-spacing:.16em; color:var(--muted); text-wrap:balance; }
.card .v { margin-top:6px; font-family:var(--f-mono); font-weight:700; line-height:1.05; letter-spacing:-.02em; text-wrap:balance; }
.card .v small { font-family:var(--f-display); font-weight:900; font-size:.45em; margin-left:8px; letter-spacing:0; }
.card .v.txt { font-family:var(--f-display); font-weight:900; letter-spacing:0; }
.card .s { margin-top:10px; font-family:var(--f-body); font-weight:500; font-size:22px; line-height:1.35; color:var(--muted); text-wrap:balance; }
.card .bars .row { display:grid; align-items:center; gap:14px; }
.card .bars .row span { font-family:var(--f-mono); color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.card .bars .row i { display:block; background:var(--accent); transform-origin:0 50%; }
.card .bars .row.hi i { background:var(--route2); }
.card .bars .row b { font-family:var(--f-mono); text-align:right; white-space:nowrap; }
.card .delta { margin-top:14px; font-family:var(--f-display); font-weight:900; font-size:40px; color:var(--route2); }
.card svg.ln { display:block; margin-top:12px; overflow:visible; }
.card svg.ln .ax { stroke:rgba(244,239,227,.3); stroke-width:1; }
.card svg.ln .pl { fill:none; stroke:var(--route2); stroke-width:4; stroke-linejoin:round; }
.card svg.ln .pt { fill:var(--fg); }
.card svg.ln text { font-family:var(--f-mono); font-size:17px; fill:var(--muted); }
.card svg.ln text.vv { fill:var(--fg); font-size:21px; font-weight:700; }
.card ol.list { list-style:none; margin:14px 0 0; padding:0; display:grid; column-gap:26px; row-gap:4px; }
.card ol.list li { display:flex; align-items:baseline; gap:12px; line-height:1.3; min-width:0; }
.card ol.list li i { font-style:normal; font-family:var(--f-mono); color:var(--accent); flex:none; font-size:.8em; }
.card ol.list li b { font-family:var(--f-body); font-weight:700; color:var(--fg); }
.card ol.list li em { font-style:normal; font-family:var(--f-mono); color:var(--muted); margin-left:auto; white-space:nowrap; }
.card .imgs { position:relative; margin-top:14px; }
.card .imgs img { position:absolute; object-fit:cover; border:1px solid rgba(244,239,227,.4); }
.card .imgs .cap { position:absolute; font-family:var(--f-mono); font-size:13px; color:#fff; background:rgba(6,18,24,.75); padding:2px 6px; }
.thesis { position:absolute; left:96px; top:300px; }
.thesis .t { font-family:var(--f-display); font-weight:900; line-height:1.16; color:var(--fg); text-shadow:0 6px 40px rgba(4,14,19,.9); text-wrap:balance; }
.outro { position:absolute; left:96px; top:330px; }
.outro .t { font-family:var(--f-display); font-weight:900; color:var(--fg); letter-spacing:.04em; line-height:1.12; text-shadow:0 6px 40px rgba(4,14,19,.9); text-wrap:balance; }
.outro .sub { margin-top:10px; font-family:var(--f-mono); font-size:22px; letter-spacing:.24em; color:var(--accent); }
.outro .cta { margin-top:30px; display:inline-block; font-family:var(--f-body); font-weight:700; font-size:30px; color:var(--ink); background:var(--fg); padding:10px 26px; }
#root.v .at-title { left:56px; top:400px; } #root.v .thesis { left:56px; top:470px; } #root.v .outro { left:56px; top:480px; }
"""


# ================================================================ the engine
class Atlas:
    def __init__(self, beats, times, X, D):
        self.X, self.D, self.beats, self.times = X, D, beats, times
        self.meta = X.v.get("meta", {})
        self.P = Proj(self.meta.get("center_lon", 60))
        self.V = X.portrait
        self.area = (40, 300, X.W - 40, 1250) if self.V else (70, 120, X.W - 70, 930)   # where the camera frames things
        self.card_w = X.W - 112 if self.V else 600

    # ---------------------------------------------------- helpers
    def T(self, v, t0, dflt=None):
        if v is None: return dflt
        return float(self.X.T(v, max(0.0, t0 - 0.05)))

    def ll(self, ref):
        """[lon,lat] or a place id."""
        if isinstance(ref, str):
            p = self.places.get(ref)
            if not p: raise SystemExit(f"atlas: unknown place {ref!r}")
            return tuple(p["ll"])
        return tuple(ref)

    def tw(self, s): self.X.tw(s)

    # ---------------------------------------------------- camera
    def box_of(self, cam):
        if cam is None: return None
        if cam == "world" or (isinstance(cam, dict) and cam.get("world")): return (self.P.L0 - 179, -56, self.P.L0 + 179, 76)
        if isinstance(cam, (list, tuple)): return tuple(cam)
        if "box" in cam: return tuple(cam["box"])
        pts = []
        for ref in cam.get("fit", []):
            if isinstance(ref, str) and ref.startswith("route:"): pts += self.routes[ref[6:]]["lls"]
            elif isinstance(ref, str) and ref.startswith("zone:"): pts += [tuple(p) for p in self.meta["zones"][ref[5:]]["poly"]]
            else: pts.append(self.ll(ref))
        if not pts: return None
        L0 = self.P.L0
        ls = [((p[0] - L0 + 180) % 360) - 180 + L0 for p in pts]; las = [p[1] for p in pts]
        lon0, lon1, lat0, lat1 = min(ls), max(ls), min(las), max(las)
        pad = cam.get("pad")
        pad = pad if pad is not None else max(2.0, 0.12 * max(lon1 - lon0, lat1 - lat0))
        return (lon0 - pad, lat0 - pad, lon1 + pad, lat1 + pad)

    def frame(self, box, reserve=None):
        P, X = self.P, self.X
        lon0, lat0, lon1, lat1 = box
        pts = [P(lon, lat) for lon in (lon0, (lon0 + lon1) / 2, lon1) for lat in (lat0, (lat0 + lat1) / 2, lat1)]
        bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts); by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
        cx0, cy0, cx1, cy1 = self.area
        if reserve is not None:
            if self.V: cy0 = max(cy0, min(reserve, cy1 - 300))     # portrait: cards / titles on top, reserve = their bottom edge
            elif isinstance(reserve, tuple) and reserve[0] == "T": cy0 = max(cy0, min(reserve[1], cy1 - 360))
            elif reserve == "L": cx0 = 96 + self.card_w + 40
            elif reserve == "R": cx1 = X.W - 96 - self.card_w - 40
        s = min((cx1 - cx0) / max(bx1 - bx0, 1), (cy1 - cy0) / max(by1 - by0, 1))
        s = max(0.3, min(s, 60))
        mx, my = (bx0 + bx1) / 2, (by0 + by1) / 2
        return s, (cx0 + cx1) / 2 - s * mx, (cy0 + cy1) / 2 - s * my, (lat0 + lat1) / 2

    # ---------------------------------------------------- build
    def run(self):
        X, P, meta = self.X, self.P, self.meta
        X.css("atlas", CSS)
        self.places = {k: dict(v) for k, v in meta.get("places", {}).items()}
        self.routes = {}
        for i, (rid, r) in enumerate(meta.get("routes", {}).items()):
            if r.get("coords"):
                lls = [tuple(p) for p in r["coords"]]; nm = sum(_hav(a, b) for a, b in zip(lls, lls[1:]))
            else:
                a, b = self.ll(r["from"]), self.ll(r["to"])
                net, nm = sea_route(a, b, tuple(r.get("avoid", ())))
                lls = [a] + net + [b]
            parts = P.line(lls)
            self.routes[rid] = {"lls": lls, "nm": nm, "parts": parts, "L": sum(length(p) for p in parts),
                                "color": r.get("color", ROUTE_COLORS[i % len(ROUTE_COLORS)]), "ship": r.get("ship", True)}
        self.beat_info = [{"b": b, "t": t, "d": d, "i": i} for i, (b, (t, d)) in enumerate(zip(self.beats, self.times))]
        self.build_map()
        self.build_events()
        self.build_camera()
        self.build_details()
        self.build_seas()
        self.build_labels()
        self.build_frame()
        self.build_overlays()

    # ---------------------------------------------------- the map layer
    def build_map(self):
        X, P, meta = self.X, self.P, self.meta
        tex = X.asset(str(next(p for p in _TEX if p.exists())))
        svg = [f'<svg id="mapsvg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" xmlns="http://www.w3.org/2000/svg">',
               '<defs><pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.6" height="1.6" fill="rgba(255,74,61,.10)"/><rect width=".55" height="1.6" fill="rgba(255,74,61,.55)"/></pattern>',
               '<clipPath id="landclip"><use href="#countries"/></clipPath><!--HATCH--></defs>',
               '<path class="grat" id="grat"/><g id="countries"></g>',
               f'<image class="tex" href="{tex}" x="0" y="0" width="{PW}" height="{PH}" preserveAspectRatio="xMidYMid slice" clip-path="url(#landclip)"/>']
        self.details = {bi["i"] for bi in self.beat_info if bi["b"].get("detail")}
        svg.append("<!--DETAIL-->")
        svg.append(f'<path class="dash" d="{dashline(P)}"/>')
        for zid, z in meta.get("zones", {}).items():
            ring = [tuple(p) for p in z["poly"]]
            svg.append(f'<path class="zone" id="zone-{zid}" fill="url(#hatch-{zid})" d="{d_of(P.line(ring + ring[:1]), True)}"/>')
        for rid, r in self.routes.items():
            d = d_of(r["parts"])
            svg.append(f'<path class="glow" id="rg-{rid}" d="{d}" stroke="{r["color"]}" stroke-dasharray="{r["L"]:.1f}" stroke-dashoffset="{r["L"]:.1f}"/>'
                       f'<path class="route" id="r-{rid}" d="{d}" stroke="{r["color"]}" stroke-dasharray="{r["L"]:.1f}" stroke-dashoffset="{r["L"]:.1f}"/>')
        self.cuts = []
        for bi in self.beat_info:
            c = bi["b"].get("cut")
            if not c: continue
            r = self.routes[c["route"]]; bx = c.get("box")
            seg = [p for p in r["lls"] if not bx or (bx[0] <= p[0] <= bx[2] and bx[1] <= p[1] <= bx[3])]
            cid = f"cut{bi['i']}"; svg.append(f'<path class="cut" id="{cid}" d="{d_of(P.line(seg))}"/>')
            self.cuts.append((bi, cid, c))
        self.wlines = {}
        for lid, ln in meta.get("lines", {}).items():
            parts = P.line([tuple(p) for p in ln["coords"]]); L = sum(length(p) for p in parts)
            svg.append(f'<path class="wglow" id="wg-{lid}" d="{d_of(parts)}"/><path class="wline" id="wl-{lid}" d="{d_of(parts)}" stroke-dasharray="{L:.2f}" stroke-dashoffset="{L:.2f}"/>')
            self.wlines[lid] = (parts, L)
        svg.append("</svg>")

        def mk(cls, lon, lat, inner):
            x, y = P(lon, lat)
            return f'<div class="mk {cls}" data-layout-allow-overlap style="left:{x:.1f}px; top:{y:.1f}px"><div class="in">{inner}</div></div>'
        self.mk = mk
        html = ["".join(svg)]
        for i, s_ in enumerate(meta.get("seas", [])):
            X.used_text.update(s_.get("name", "") + s_.get("en", ""))
            html.append(mk(f"sea sea{i}", *s_["ll"], f'<div><b>{s_.get("name", "")}</b>{s_.get("en", "")}</div>'))
        for rid, r in self.routes.items():
            if r["ship"]:
                html.append(mk(f"ship sh-{rid}", *r["lls"][0], f'<em style="background:linear-gradient(90deg, transparent, {r["color"]})"></em><i style="background:{r["color"]}"></i>'))
        for bi, cid, c in self.cuts:
            if c.get("x"): html.append(mk(f"xmark x{bi['i']}", *self.ll(c["x"]), "<i></i>"))
        for lid, ln in meta.get("lines", {}).items():
            if ln.get("label"):
                mid = ln["coords"][len(ln["coords"]) // 2]
                X.used_text.update(ln["label"])
                html.append(mk(f"wlab wb-{lid}", *mid, f"<div>{X.rich(ln['label'])}</div>"))
        self.pin_slot = len(html); html.append("")
        self.map_html = html
        L0 = P.L0
        self.script = ("<script>(function(){var T=" + _lib("world-chn-50m.topo.json").read_text() + ";"
                       f"var pr=d3.geoNaturalEarth1().rotate([{-L0},0]).scale({K}).translate([{TX},{TY}]);var pa=d3.geoPath(pr);if(pa.digits)pa.digits(1);"
                       "var fc=topojson.feature(T,T.objects.countries),h='';"
                       "fc.features.forEach(function(f){var a=f.properties.ADM0_A3,c=(a==='HKG'||a==='MAC')?'CHN':a,d=pa(f);if(d)h+='<path class=\"c c-'+c+'\" id=\"c-'+a+'\" d=\"'+d+'\"/>';});"
                       "document.getElementById('countries').innerHTML=h;document.getElementById('grat').setAttribute('d',pa(d3.geoGraticule10()));"
                       "var L=document.getElementById('locland');if(L){var s=L.getAttribute('data-s')*1,p2=d3.geoNaturalEarth1().rotate([" + str(-L0) + ",0]).scale(" + str(K) + "*s).translate([" + str(TX) + "*s," + str(TY) + "*s]);"
                       "L.setAttribute('d',d3.geoPath(p2)(topojson.merge(T,T.objects.countries.geometries)));}"
                       "})();</script>")
        X.extra_head = X.geo_scripts()     # vendored d3-geo + topojson-client when present, else the CDN

    # ---------------------------------------------------- map events per beat
    def build_events(self):
        X, P = self.X, self.P
        self.ship_tracks = {}
        self.tw('tl.set(".ship, .sea", {opacity:0}, 0);')
        for bi in self.beat_info:
            b, t, d = bi["b"], bi["t"], bi["d"]; end = t + d
            for dr in b.get("draw", []):
                dr = {"route": dr} if isinstance(dr, str) else dr
                rid = dr["route"]; r = self.routes[rid]
                t0 = self.T(dr.get("at"), t, t + 0.2)
                du = float(dr.get("dur") or max(1.2, end - t0 - 0.35))
                self.tw(f'tl.to("#r-{rid}, #rg-{rid}", {{strokeDashoffset:0, duration:{du:.2f}, ease:"none"}}, {t0:.3f});')
                if r["ship"]:
                    n = max(12, min(80, int(r["L"] / 25)))
                    pts = resample(r["parts"], n); step = du / n
                    x0, y0 = P(*r["lls"][0])
                    self.tw(f'tl.set(".sh-{rid}", {{opacity:1}}, {t0:.3f});')
                    kf = ",".join(f'{{x:{p[0] - x0:.1f}, y:{p[1] - y0:.1f}, rotation:{p[2]:.0f}, duration:{step:.3f}}}' for p in pts[1:])
                    self.tw(f'tl.to(".sh-{rid} .in", {{keyframes:[{kf}], ease:"none"}}, {t0:.3f});')
                    if not dr.get("keep_ship"): self.tw(f'tl.to(".sh-{rid}", {{opacity:0, duration:0.4}}, {t0 + du + 0.5:.3f});')
                    self.ship_tracks[rid] = (t0, du, pts)
                X.sfx(t0, "enter")
            for z in b.get("zones", []):
                z = {"zone": z} if isinstance(z, str) else z
                tz = self.T(z.get("at"), t, t + 0.4)
                self.tw(f'tl.to("#zone-{z["zone"]}", {{opacity:1, duration:0.5}}, {tz:.3f});')
                self.tw(f'tl.fromTo("#zone-{z["zone"]}", {{scale:0.94, transformOrigin:"50% 50%"}}, {{scale:1.03, duration:{max(1.0, end - tz):.2f}, ease:"sine.inOut", immediateRender:false}}, {tz:.3f});')
                X.sfx(tz, "alarm")
            for h in b.get("highlight", []):
                h = {"iso": h} if isinstance(h, str) else h
                th = self.T(h.get("at"), t, t + 0.3)
                for iso in ([h["iso"]] if isinstance(h["iso"], str) else h["iso"]):
                    self.tw(f'tl.to("#c-{iso}, .d-{iso}", {{fill:"{h.get("color", "#f3d48a")}", duration:0.5}}, {th:.3f});')
            for lid in b.get("lines", []):
                ln = {"line": lid} if isinstance(lid, str) else lid
                tl_ = self.T(ln.get("at"), t, t + 0.4); parts, L = self.wlines[ln["line"]]
                self.tw(f'tl.to("#wg-{ln["line"]}", {{opacity:0.55, duration:0.6}}, {tl_ + 0.1:.3f});')
                self.tw(f'tl.fromTo("#wl-{ln["line"]}", {{opacity:1, strokeDashoffset:{L:.2f}}}, {{opacity:1, strokeDashoffset:0, duration:1.0, ease:"power2.inOut", immediateRender:false}}, {tl_:.3f});')
                self.tw(f'tl.set(".wb-{ln["line"]}", {{opacity:0}}, 0);')
                self.tw(f'tl.to(".wb-{ln["line"]}", {{opacity:1, duration:0.3}}, {tl_ + 0.8:.3f});')
                X.sfx(tl_, "enter")
            if bi["i"] in self.details:
                self.tw(f'tl.to("#det{bi["i"]}", {{opacity:1, duration:0.6}}, {max(0, t - 0.1):.3f});')
                self.tw(f'tl.to("#det{bi["i"]}", {{opacity:0, duration:0.5}}, {end - 0.25:.3f});')
            if b.get("dim"):
                self.tw(f'tl.to(".route, .glow, .zone", {{opacity:0.12, duration:0.5}}, {max(0, t - 0.1):.3f});')
                self.tw(f'tl.to(".route", {{opacity:1, duration:0.5}}, {end - 0.2:.3f});')
                self.tw(f'tl.to(".glow", {{opacity:0.22, duration:0.5}}, {end - 0.2:.3f});')
            for clr in b.get("clear", []):
                tcl = max(0, t - 0.3)
                if clr in ("cuts", "all"):
                    self.tw(f'tl.to(".cut, .xmark", {{opacity:0, duration:0.4}}, {tcl:.3f});')
                    self.tw(f'tl.to(".route", {{opacity:1, duration:0.4}}, {tcl:.3f});')
                if clr in ("zones", "all"): self.tw(f'tl.to(".zone", {{opacity:0.0, duration:0.4}}, {tcl:.3f});')
                if clr in ("highlights", "all"): self.tw(f'tl.to("#countries .c, .detl", {{fill:"#e9e1cc", duration:0.4}}, {tcl:.3f});')
                if clr in ("lines", "all"): self.tw(f'tl.to(".wline, .wglow, .wlab", {{opacity:0, duration:0.4}}, {tcl:.3f});')
        for bi, cid, c in self.cuts:
            tc = self.T(c.get("at"), bi["t"], bi["t"] + 1.0)
            self.tw(f'tl.to("#{cid}", {{opacity:1, duration:0.15}}, {tc:.3f});')
            self.tw(f'tl.to("#r-{c["route"]}, #rg-{c["route"]}", {{opacity:0.28, duration:0.3}}, {tc:.3f});')
            if c.get("x"):
                self.tw(f'tl.set(".x{bi["i"]}", {{opacity:0}}, 0);')
                self.tw(f'tl.to(".x{bi["i"]}", {{opacity:1, duration:0.1}}, {tc + 0.1:.3f});')
                self.tw(f'tl.from(".x{bi["i"]} .in > i", {{scale:2.2, rotation:-30, duration:0.35, ease:"back.out(2)"}}, {tc + 0.1:.3f});')
            if c["route"] in self.ship_tracks: self.tw(f'tl.to(".sh-{c["route"]}", {{opacity:0, duration:0.3}}, {tc + 0.1:.3f});')
            X.sfx(tc + 0.1, "hit")

    # ---------------------------------------------------- camera keys
    def build_camera(self):
        X = self.X
        keys = []
        for bi in self.beat_info:
            b, t = bi["b"], bi["t"]
            res = self.reserve_of(bi)
            box = self.box_of(b.get("camera"))
            if box: keys.append((max(0.0, t - (0.3 if bi["i"] else 0)), box, res))
            for mv in b.get("moves", []):
                mb = self.box_of(mv.get("camera"))
                if mb: keys.append((self.T(mv.get("at"), t, t + 1.0), mb, res))
        if not keys: keys = [(0.0, (self.P.L0 - 179, -56, self.P.L0 + 179, 76), None)]
        keys.sort(key=lambda k: k[0])
        if keys[0][0] > 0: keys.insert(0, (0.0, keys[0][1], keys[0][2]))
        cams = [(tk, *self.frame(box, res), box) for tk, box, res in keys]
        s0, x0, y0 = cams[0][1], cams[0][2], cams[0][3]
        self.tw(f'tl.set("#mapcam", {{scale:{s0:.4f}, x:{x0:.1f}, y:{y0:.1f}, "--z":{s0:.4f}}}, 0);')
        self.cam_moves = []
        for k in range(len(cams)):
            tk, s, x, y, lat, box = cams[k]
            nxt = cams[k + 1][0] if k + 1 < len(cams) else self.D
            mv = 0.0 if k == 0 else max(0.5, min(1.4, nxt - tk - 0.1))
            if k:
                self.tw(f'tl.to("#mapcam", {{scale:{s:.4f}, x:{x:.1f}, y:{y:.1f}, "--z":{s:.4f}, duration:{mv:.2f}, ease:"power3.inOut"}}, {tk:.3f});')
                if s > 1.6 and cams[k - 1][1] < s * 0.8: X.sfx(tk, "fly")
            hold = nxt - (tk + mv) - 0.03
            if hold > 0.3:       # creep toward the frame centre while holding, so no second is static
                c = 1.02; cx, cy = (self.area[0] + self.area[2]) / 2, (self.area[1] + self.area[3]) / 2
                self.tw(f'tl.to("#mapcam", {{scale:{s * c:.4f}, x:{cx - (cx - x) * c:.1f}, y:{cy - (cy - y) * c:.1f}, "--z":{s * c:.4f}, duration:{hold:.2f}, ease:"none"}}, {tk + mv:.3f});')
            self.cam_moves.append((tk, mv, s, x, y, lat, box))

    def unproject_box(self, s, x, y, margin=0.25):
        """lon/lat box that covers the viewport of camera (s, x, y), with a margin (bisection on the projection)."""
        P, X = self.P, self.X
        px0, py0, px1, py1 = -x / s, -y / s, (X.W - x) / s, (X.H - y) / s
        cxp, cyp = (px0 + px1) / 2, (py0 + py1) / 2
        def solve(f, target, lo, hi):
            for _ in range(50):
                mid = (lo + hi) / 2
                if f(mid) < target: lo = mid
                else: hi = mid
            return (lo + hi) / 2
        latc = solve(lambda la: -P(self.P.L0, la)[1], -cyp, -89, 89)
        lonc = solve(lambda lo: P(lo, latc)[0], cxp, self.P.L0 - 179.9, self.P.L0 + 179.9)
        lon0 = solve(lambda lo: P(lo, latc)[0], px0, self.P.L0 - 179.9, self.P.L0 + 179.9)
        lon1 = solve(lambda lo: P(lo, latc)[0], px1, self.P.L0 - 179.9, self.P.L0 + 179.9)
        lat1 = solve(lambda la: -P(lonc, la)[1], -py0, -89, 89)
        lat0 = solve(lambda la: -P(lonc, la)[1], -py1, -89, 89)
        mw, mh = (lon1 - lon0) * margin, (lat1 - lat0) * margin
        return (lon0 - mw, lat0 - mh, lon1 + mw, lat1 + mh)

    def build_details(self):
        P = self.P
        parts = []
        for bi in self.beat_info:
            if bi["i"] not in self.details: continue
            dt = bi["b"]["detail"]
            if isinstance(dt, (list, tuple)): box = tuple(dt)
            else:
                end = bi["t"] + bi["d"]
                cams = [c for c in self.cam_moves if bi["t"] - 0.4 <= c[0] < end - 0.5] or [self.cam_moves[0]]
                boxes = [self.unproject_box(c[2], c[3], c[4]) for c in cams]
                box = (min(b_[0] for b_ in boxes), min(b_[1] for b_ in boxes), max(b_[2] for b_ in boxes), max(b_[3] for b_ in boxes))
            L0 = self.P.L0
            box = (max(box[0], L0 - 179), max(box[1], -85), min(box[2], L0 + 179), min(box[3], 85))
            (x0, y0), (x1, y1) = P(box[0], box[3]), P(box[2], box[1])
            parts.append(f'<g class="det" id="det{bi["i"]}"><rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" height="{y1 - y0:.0f}" fill="#163644"/>{detail(P, box)}</g>')
        hatch = []
        for zid in self.meta.get("zones", {}):
            zs = [self.cam_at(bi["t"] + bi["d"] * 0.6)[0] for bi in self.beat_info
                  if any((z if isinstance(z, str) else z.get("zone")) == zid for z in bi["b"].get("zones", []))] or [1.0]
            u = 10.0 / max(zs)                      # ~10 px stripes at the zoom the zone is seen
            hatch.append(f'<pattern id="hatch-{zid}" width="{u:.3f}" height="{u:.3f}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                         f'<rect width="{u:.3f}" height="{u:.3f}" fill="rgba(255,74,61,.10)"/><rect width="{u * 0.34:.3f}" height="{u:.3f}" fill="rgba(255,74,61,.55)"/></pattern>')
        self.map_html[0] = self.map_html[0].replace("<!--DETAIL-->", "".join(parts)).replace("<!--HATCH-->", "".join(hatch))

    def build_seas(self):
        for i, s_ in enumerate(self.meta.get("seas", [])):
            wins = [(bi["t"], bi["t"] + bi["d"]) for bi in self.beat_info if bi["b"].get("id") in s_.get("show", []) or bi["i"] in s_.get("show", [])]
            spans = []
            for a0, a1 in sorted(wins):
                if spans and a0 - spans[-1][1] < 0.2: spans[-1][1] = a1
                else: spans.append([a0, a1])
            for a0, a1 in spans:
                arrive = max([tk + mv for tk, mv, *_ in getattr(self, "cam_moves", []) if a0 - 0.4 <= tk <= a0 + 0.2] or [a0 + 0.3])
                self.tw(f'tl.to(".sea{i}", {{opacity:1, duration:0.5}}, {arrive:.3f});')
                if a1 < self.D - 0.1: self.tw(f'tl.to(".sea{i}", {{opacity:0, duration:0.4}}, {a1 - 0.45:.3f});')


    def cam_at(self, t):
        cur = self.cam_moves[0]
        for c in self.cam_moves:
            if c[0] + c[1] <= t + 0.01: cur = c
        return cur[2], cur[3], cur[4]

    # ---------------------------------------------------- cards: sizes (used for camera reserve and label avoidance)
    def reserve_of(self, bi):
        b = bi["b"]
        if _empty_card(b.get("card")): b.pop("card", None)
        if b.get("card"):
            if self.V: return 400 + self.card_size(b["card"])[1] + 40
            return b["card"].get("side", "L")
        if b.get("title"): return self.title_bottom(bi) if self.V else ("T", self.title_bottom(bi))
        return None

    def title_size(self, txt):
        maxw = self.X.W - 112 if self.V else 860
        return maxw, fit(txt, maxw, 330 if self.V else 360, 76 if self.V else 84, 34, maxlines=4)

    def title_bottom(self, bi):
        maxw, (size, lines) = self.title_size(bi["b"]["title"].get("text", ""))
        return int((400 if self.V else 132) + 40 + lines * size * 1.14 + 50)

    def title_rect(self, bi):
        txt = bi["b"]["title"].get("text", "")
        maxw, (size, lines) = self.title_size(txt)
        longest = max(sum(_unit(c) for c in part.replace("*", "")) for part in txt.split("|")) * size
        x0 = 56 if self.V else 96
        return (x0 - 20, (400 if self.V else 132) - 20, x0 + min(maxw, longest) + 30, self.title_bottom(bi))

    def card_size(self, c):
        w = self.card_w; typ = c.get("type", "stat")
        h = 22 + 20 + 22 + (40 if c.get("sub") else 0)
        if typ == "stat": h += self.stat_size(c, w)[0] * 1.1
        elif typ == "bars":
            rh, fs = self.bar_row(c); h += 14 + len(c.get("rows", [])) * (max(rh, (fs + 4) * 1.35) + 12) + (56 if c.get("delta") else 0)
        elif typ == "line": h += 12 + (230 if self.V else 190) + 40 + (self.stat_size(c, w)[0] * 1.1 if c.get("value") else 0)
        elif typ == "list": f, cols, rows = self.list_layout(c, w); h += 14 + rows * (f * 1.3 + 4)
        elif typ == "images": h += 14 + self.img_layout(c, w - 52)[1]
        elif typ == "text": f, n = fit(c.get("text", ""), w - 52, 300, 34, 18, maxlines=8); h += n * f * 1.4
        return w, int(h)

    def stat_size(self, c, w):
        v = str(c.get("value", "")); unit = str(c.get("unit", ""))
        num = _is_num(v)
        size, lines = fit(v + (" " + unit if unit else ""), w - 52, 200, 72 if num else 52, 24, lh=1.1, maxlines=1 if num else 3)
        return size * lines, size

    def bar_row(self, c):
        n = max(1, len(c.get("rows", [])))
        rh = max(10, min(32, int((300 if self.V else 260) / n) - 12))
        return rh, max(13, min(24, rh + 2))

    def list_layout(self, c, w):
        items = c.get("items", []); n = max(1, len(items))
        cols = 2 if (n > 6 and not self.V) or n > 10 else 1
        rows = math.ceil(n / cols)
        txts = [str(it if isinstance(it, str) else it.get("text", "")) + ("  " + str(it.get("value", "")) if isinstance(it, dict) else "") for it in items]
        longest = max([sum(_unit(ch) for ch in s_) for s_ in txts] or [4])
        colw = (w - 52 - (cols - 1) * 26) / cols - 46
        f = max(15, min(30, int(colw / max(longest, 1)), int((380 if self.V else 330) / (rows * 1.36))))
        return f, cols, rows

    def img_layout(self, c, w):
        """justified rows: any number of images of any aspect; returns (boxes, height)."""
        from PIL import Image
        ims = []
        for im in c.get("images", []):
            src = im if isinstance(im, str) else im["src"]
            p = Path(src) if Path(src).is_absolute() else self.X.src / src
            try:
                with Image.open(p) as I: a = I.width / max(I.height, 1)
            except Exception: a = 1.5
            ims.append((src, a, None if isinstance(im, str) else im.get("cap")))
        if not ims: return [], 0
        target = 170 if self.V else 140; gap = 8; rows, cur = [], []
        for it in ims:
            cur.append(it)
            if sum(a for _, a, _ in cur) * target + gap * (len(cur) - 1) >= w: rows.append(cur); cur = []
        if cur: rows.append(cur)
        boxes, y = [], 0
        for i, row in enumerate(rows):
            sa = sum(a for _, a, _ in row)
            full = (w - gap * (len(row) - 1)) / sa
            h = full if (i < len(rows) - 1 or sa * target > w * 0.75) else min(full, target)
            x = 0
            for src, a, cap in row:
                boxes.append((src, x, y, a * h, h, cap)); x += a * h + gap
            y += h + gap
        hmax = 460 if self.V else 380
        if y > hmax:
            k = hmax / y; boxes = [(s_, x * k, yy * k, ww * k, hh * k, cap) for s_, x, yy, ww, hh, cap in boxes]; y = hmax
        return boxes, y

    # ---------------------------------------------------- pins + label placement (collision avoidance per shot)
    def build_labels(self):
        X, P = self.X, self.P
        shown, order = {}, []
        for bi in self.beat_info:
            for i, pin in enumerate(bi["b"].get("pins", [])):
                pin = {"id": pin} if isinstance(pin, str) else pin
                pid = pin["id"]
                if pid in shown: continue
                at = pin.get("at")
                if isinstance(at, str) and at.startswith("pass:") and at[5:] in self.ship_tracks:
                    t0, du, pts = self.ship_tracks[at[5:]]
                    q = P(*self.ll(pid))
                    k = min(range(len(pts)), key=lambda j: math.hypot(pts[j][0] - q[0], pts[j][1] - q[1]))
                    tp = t0 + (k / max(len(pts) - 1, 1)) * du - 0.15
                elif isinstance(at, str) and at.startswith("pass:"): tp = bi["t"] + 0.3 + 0.18 * i
                else: tp = self.T(at, bi["t"], bi["t"] + 0.3 + 0.18 * i)
                shown[pid] = max(0.0, tp); order.append(pid)
        geo = {}
        for pid in order:
            p = self.places[pid]
            name, sub, val = str(p.get("name", pid)), str(p.get("sub", "")), str(p.get("value", ""))
            fs, nl = fit(name, 340, 80, 30, 18, maxlines=2)
            vs = fit(val, 340, 60, 34, 18, maxlines=1)[0] if val else 0
            wn = sum(_unit(c) for c in name) * fs / max(nl, 1)
            w = max(wn, sum(_unit(c) for c in sub) * 15, sum(_unit(c) for c in val) * vs) + 24
            h = 10 + nl * fs * 1.2 + (19 if sub else 0) + (vs * 1.15 if val else 0)
            geo[pid] = (min(w * 1.08 + 6, 380), h, fs, vs)
            X.used_text.update(name + sub + val)
        sides = ["E", "W", "N", "S", "NE", "NW", "SE", "SW"]
        place_by_beat = []          # one placement per camera shot (labels re-flow when the camera moves)
        segs = []
        for k, (tk, mv, s, x, y, lat, box) in enumerate(self.cam_moves):
            t_end = self.cam_moves[k + 1][0] if k + 1 < len(self.cam_moves) else self.D
            arrive = tk + mv
            bi = max((b_ for b_ in self.beat_info if b_["t"] <= arrive + 0.01), key=lambda b_: b_["t"])
            segs.append((tk, arrive, t_end, s, x, y, bi))
        for tk, arrive, t_end, s, x, y, bi in segs:
            vis = [pid for pid in order if shown[pid] <= t_end - 0.2]
            prio = [p_ if isinstance(p_, str) else p_["id"] for p_ in bi["b"].get("pins", [])]
            vis.sort(key=lambda q: (0 if q in prio else 1, 0 if self.places[q].get("hot") else 1, order.index(q)))
            obst = self.obstacles(bi)
            for si, s_ in enumerate(self.meta.get("seas", [])):
                if bi["b"].get("id") in s_.get("show", []) or bi["i"] in s_.get("show", []):
                    qx, qy = P(*s_["ll"]); qx, qy = x + s * qx, y + s * qy
                    hw = max(sum(_unit(c) for c in s_.get("name", "")) * 26 * 1.5, sum(_unit(c) for c in s_.get("en", "")) * 20 * 1.3) / 2
                    obst.append((qx - hw, qy - 32, qx + hw, qy + 32))
            dots = {pid: (x + s * P(*self.ll(pid))[0], y + s * P(*self.ll(pid))[1]) for pid in vis}
            dot_box = {pid: (sx - 20, sy - 20, sx + 20, sy + 20) for pid, (sx, sy) in dots.items()}
            chosen = {}
            closing = bool(bi["b"].get("thesis") or bi["b"].get("outro"))
            if bi["b"].get("labels", not closing) is not False:
                for pid in vis:
                    sx, sy = dots[pid]
                    if not (0 < sx < X.W and 0 < sy < X.H): continue
                    w, h, _, _ = geo[pid]
                    pref = self.places[pid].get("side")
                    for sd in ([pref] if pref else []) + sides:
                        r = _lab_rect(sd, sx, sy, w, h)
                        if r[0] < 30 or r[2] > X.W - 30 or r[1] < 30 or r[3] > X.H - 30: continue
                        rr = (r[0] - 5, r[1] - 5, r[2] + 5, r[3] + 5)
                        if any(_hit(rr, o) for o in obst): continue
                        if any(_hit(rr, bx) for q, bx in dot_box.items() if q != pid): continue
                        chosen[pid] = sd; obst.append(r); break
            place_by_beat.append(chosen)
        used = {pid: sorted({pb[pid] for pb in place_by_beat if pid in pb}) for pid in order}
        html = []
        for pid in order:
            p = self.places[pid]; w, h, fs, vs = geo[pid]
            labs = ""
            for sd in used[pid]:
                labs += (f'<div class="lab l-{sd}" style="{_lab_css(sd, w, h)}; width:max-content; max-width:380px; box-sizing:border-box; white-space:normal">'
                         + (f'<div class="val" style="font-size:{vs}px">{X.rich(p["value"])}</div>' if p.get("value") else "")
                         + f'<b style="font-size:{fs}px; text-wrap:balance">{words_html(X, p.get("name", pid), chars=False)}</b>'
                         + (f'<span style="font-size:15px">{X.rich(p["sub"])}</span>' if p.get("sub") else "") + "</div>")
            html.append(self.mk(f"pin pn-{pid}{' hot' if p.get('hot') else ''}{' sm' if p.get('small') else ''}", *self.ll(pid), f'<i class="ring"></i><i class="dot"></i>{labs}'))
        self.map_html[self.pin_slot] = "".join(html)
        X.clip("atlasmap", 0, self.D, f'<div id="mapcam">{"".join(self.map_html)}</div>{self.script}', "at-map", 1, track=2)
        self.tw('tl.set(".pin", {opacity:0}, 0);')
        for pid in order:
            tp = shown[pid]
            self.tw(f'tl.to(".pn-{pid}", {{opacity:1, duration:0.2}}, {tp:.3f});')
            self.tw(f'tl.from(".pn-{pid} .dot", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {tp:.3f});')
            self.tw(f'tl.fromTo(".pn-{pid} .ring", {{scale:0.4, opacity:1}}, {{scale:1.6, opacity:0, duration:0.8, ease:"power2.out", immediateRender:false}}, {tp:.3f});')
            X.sfx(tp, "pin")
        state = {}
        for (tk, arrive, t_end, *_), chosen in zip(segs, place_by_beat):
            for pid in order:
                for sd in used[pid]:
                    on = chosen.get(pid) == sd
                    if on == state.get((pid, sd), False): continue
                    ts = max(tk + (arrive - tk) * 0.6, shown[pid] + 0.08) if on else tk
                    self.tw(f'tl.to(".pn-{pid} .l-{sd}", {{opacity:{1 if on else 0}, duration:{0.35 if on else 0.2}}}, {ts:.3f});')
                    state[(pid, sd)] = on

    def obstacles(self, bi):
        X = self.X
        o = [(0, 0, X.W, 300), (X.W - 300, 220, X.W, 380), (0, 1200, X.W, X.H)] if self.V else [(0, 0, X.W, 140), (X.W - 370, 90, X.W, 270), (0, 860, X.W, X.H)]
        c = bi["b"].get("card")
        if c:
            w, h = self.card_size(c)
            if self.V: o.append((56, 400, 56 + w, 400 + h))
            elif c.get("side", "L") == "L": o.append((96, 150, 96 + w, 150 + h))
            else: o.append((X.W - 96 - w, 290, X.W - 96, 290 + h))
        if bi["b"].get("title"): o.append((0, 0, X.W, self.title_bottom(bi) + 150))
        if bi["b"].get("thesis") or bi["b"].get("outro"): o.append((0, 0, X.W, X.H * 0.62) if self.V else (0, 0, X.W * 0.66, X.H))
        return o

    # ---------------------------------------------------- frame furniture
    def build_frame(self):
        X, meta = self.X, self.meta
        ticks = "".join(f'<i class="tk" style="left:{22 + k * (X.W - 44) / 12:.0f}px; top:22px; width:1.5px; height:10px"></i><i class="tk" style="left:{22 + k * (X.W - 44) / 12:.0f}px; bottom:22px; width:1.5px; height:10px"></i>' for k in range(1, 12))
        rs = (250 if self.V else 300) / PW
        loc = (f'<div class="loc"><svg width="{PW * rs:.0f}" height="{PH * rs:.0f}"><path class="ll" id="locland" data-s="{rs:.5f}"/>'
               f'<rect class="vp" id="vp" x="0" y="0" width="10" height="10"/></svg><div class="cap">LOCATOR</div></div>')
        sb = '<div class="sb"><div class="bar" id="sbar" style="width:200px"></div><div class="n"><span>0</span><span id="sbn">1000 公里</span></div></div>'
        X.used_text.update("0123456789 公里°′NSEW·LOCATOR×.,")
        hd = f'<div class="hd"><b>{X.rich(meta.get("show", X.channel))}</b><span>{X.rich(meta.get("chapter", ""))}</span></div>'
        X.clip("atframe", 0, self.D, f'<div class="scT"></div><div class="scB"></div><div class="nl"></div><div class="nl2"></div>{ticks}{hd}{loc}{sb}<div class="coord" id="coord"></div><div class="src" id="src"></div>', "at-frame", 20, track=3)
        for (tk, mv, s, x, y, lat, box) in self.cam_moves:
            verb, dur = ("set", "") if mv == 0 else ("to", f', duration:{mv:.2f}, ease:"power3.inOut"')
            rx, ry, rw, rh = (-x / s) * rs, (-y / s) * rs, (X.W / s) * rs, (X.H / s) * rs
            self.tw(f'tl.{verb}("#vp", {{attr:{{x:{rx:.1f}, y:{ry:.1f}, width:{max(rw, 4):.1f}, height:{max(rh, 4):.1f}}}{dur}}}, {tk:.3f});')
            km, w = _nice_bar(s, lat)
            self.tw(f'tl.{verb}("#sbar", {{width:{w:.0f}{dur}}}, {tk:.3f});')
            self.tw(f'tl.set("#sbn", {{textContent:"{km:,} 公里"}}, {tk + mv / 2:.3f});')
            lon_c, lat_c = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            lon_c = ((lon_c + 180) % 360) - 180
            txt = f'{abs(lat_c):.1f}°{"N" if lat_c >= 0 else "S"} · {abs(lon_c):.1f}°{"E" if lon_c >= 0 else "W"} · ×{s:.1f}'
            self.tw(f'tl.set("#coord", {{textContent:"{txt}"}}, {tk + mv / 2:.3f});')
            X.used_text.update(txt + f"{km:,}")
        for bi in self.beat_info:
            src = bi["b"].get("src", meta.get("src", ""))
            X.used_text.update(src)
            self.tw(f'tl.set("#src", {{textContent:{json.dumps("来源：" + src if src else "", ensure_ascii=False)}}}, {bi["t"]:.3f});')
        self.tw('tl.from(".at-frame .nl, .at-frame .nl2", {opacity:0, scale:1.03, duration:0.8, ease:"expo.out"}, 0.05);')
        self.tw('tl.from(".at-frame .hd, .at-frame .loc, .at-frame .sb", {opacity:0, y:-10, duration:0.6, ease:"expo.out", stagger:0.08}, 0.3);')

    # ---------------------------------------------------- overlays: titles, cards, thesis, outro
    def build_overlays(self):
        X = self.X
        for bi in self.beat_info:
            b, t, d, i = bi["b"], bi["t"], bi["d"], bi["i"]; end = t + d
            if b.get("title"):
                tt = b["title"]; txt = tt.get("text", "")
                maxw, (size, _) = self.title_size(txt)
                cid = f"ttl{i}"
                tb_ = self.title_bottom(bi)
                X.clip(f"tsc{i}", t, d, "", "at-ov", 19, track=8, sty=f"height:{tb_ + 150}px; bottom:auto; background:linear-gradient(rgba(6,18,24,.9), rgba(6,18,24,.82) {max(40, tb_ - 40)}px, rgba(6,18,24,0))")
                self.tw(f'tl.from("#tsc{i}", {{opacity:0, duration:0.5}}, {t:.3f});')
                self.tw(f'tl.to("#tsc{i}", {{opacity:0, duration:0.35, ease:"power2.in"}}, {end - 0.4:.3f});')
                X.clip(cid, t, d, f'<div class="at-title" style="max-width:{maxw}px"><div class="k">{X.rich(tt.get("kicker", ""))}</div>'
                                  f'<div class="t" style="font-size:{size}px">{words_html(X, txt)}</div><div class="r"></div></div>', "at-ov", 25, track=4 + i % 3)
                self.tw(f'tl.from("#{cid} .k", {{opacity:0, x:-20, duration:0.5, ease:"expo.out"}}, {t + 0.15:.3f});')
                self.tw(f'tl.from("#{cid} .t .c", {{opacity:0, yPercent:40, duration:0.5, ease:"expo.out", stagger:{min(0.04, 1.2 / max(len(txt), 1)):.3f}}}, {t + 0.3:.3f});')
                self.tw(f'tl.from("#{cid} .r", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {t + 0.6:.3f});')
                self.tw(f'tl.to("#{cid} .at-title", {{opacity:0, duration:0.35, ease:"power2.in"}}, {end - 0.4:.3f});')
            if b.get("card"): self.card(bi)
            if b.get("thesis"):
                th = b["thesis"]; txt = th if isinstance(th, str) else th.get("text", "")
                maxw = X.W - 112 if self.V else 1100
                size, _ = fit(txt, maxw, 700 if self.V else 520, 110 if self.V else 118, 40, maxlines=5)
                cid = f"ths{i}"
                X.clip(cid, t, d, f'<div class="thesis" style="max-width:{maxw}px"><div class="t" style="font-size:{size}px">{words_html(X, txt)}</div></div>', "at-ov", 25, track=4 + i % 3)
                self.tw(f'tl.from("#{cid} .t .c", {{opacity:0, yPercent:30, filter:"blur(10px)", duration:0.55, ease:"expo.out", stagger:{min(0.05, 1.4 / max(len(txt), 1)):.3f}}}, {t + 0.25:.3f});')
                if end < self.D - 0.1: self.tw(f'tl.to("#{cid} .thesis", {{opacity:0, duration:0.3}}, {end - 0.3:.3f});')
                X.sfx(t + 0.25, "hit")
            if b.get("outro"):
                ob = b["outro"]; maxw = X.W - 112 if self.V else 1000
                size, _ = fit(ob.get("title", X.channel), maxw, 300, 112 if self.V else 120, 48, maxlines=2)
                cid = f"otr{i}"
                X.clip(cid, t, d, f'<div class="outro" style="max-width:{maxw}px"><div class="t" style="font-size:{size}px">{words_html(X, ob.get("title", X.channel))}</div>'
                                  f'<div class="sub">{X.rich(ob.get("sub", ""))}</div>' + (f'<div class="cta">{X.rich(ob["cta"])}</div>' if ob.get("cta") else "") + "</div>", "at-ov", 25, track=4 + i % 3)
                self.tw(f'tl.from("#{cid} .t .c", {{opacity:0, y:30, duration:0.5, ease:"expo.out", stagger:0.05}}, {t + 0.1:.3f});')
                self.tw(f'tl.from("#{cid} .sub, #{cid} .cta", {{opacity:0, y:16, duration:0.5, ease:"expo.out", stagger:0.12}}, {t + 0.5:.3f});')
        closing = [bi["t"] for bi in self.beat_info if bi["b"].get("thesis") or bi["b"].get("outro")]
        if closing:
            tdim = min(closing)
            g = "linear-gradient(rgba(8,22,29,.85), rgba(8,22,29,.45) 60%, rgba(8,22,29,.15))" if self.V else "linear-gradient(90deg, rgba(8,22,29,.82), rgba(8,22,29,.35) 70%, rgba(8,22,29,.1))"
            X.clip("atdim", tdim, self.D - tdim, "", "at-ov", 19, track=7, sty=f"background:{g}")
            self.tw(f'tl.from("#atdim", {{opacity:0, duration:0.6}}, {tdim:.3f});')

    def card(self, bi):
        X = self.X; b, t, d, i = bi["b"], bi["t"], bi["d"], bi["i"]
        c = b["card"]; typ = c.get("type", "stat"); w, h = self.card_size(c)
        t0 = self.T(c.get("at"), t, t + 0.2); t1 = t + d
        if self.V: pos = f"left:56px; top:400px; width:{w}px"
        elif c.get("side", "L") == "L": pos = f"left:96px; top:150px; width:{w}px"
        else: pos = f"right:96px; top:290px; width:{w}px"
        cid = f"cd{i}"
        body = f'<div class="k">{X.rich(c.get("k", ""))}</div>'
        js = []
        unit = (f'<small>{X.rich(c["unit"])}</small>' if c.get("unit") else "")
        if typ == "stat":
            v = str(c.get("value", "")); _, size = self.stat_size(c, w)
            if _is_num(v) and c.get("count", True):
                num, dec = _num(v)
                pre = v[:len(v) - len(v.lstrip("+−-$¥≈"))]
                body += f'<div class="v" style="font-size:{size}px"><span class="n">{pre}0</span>{unit}</div>'
                fmt = f'o.v.toFixed({dec})' if dec else 'Math.round(o.v).toLocaleString("en-US")'
                js.append(f'(()=>{{const o={{v:0}}, el=document.querySelector("#{cid} .n"); tl.to(o, {{v:{num}, duration:{float(c.get("count_dur", 1.0)):.2f}, ease:"power3.out", onUpdate:()=>{{el.textContent={json.dumps(pre)}+{fmt};}}}}, {t0 + 0.2:.3f});}})();')
                X.used_text.update(v + "0123456789.,")
            else:
                body += f'<div class="v txt" style="font-size:{size}px">{words_html(X, v, chars=False)}{unit}</div>'
        elif typ == "bars":
            rows = c.get("rows", []); rh, fs = self.bar_row(c)
            mx = max([abs(float(r[1])) for r in rows] or [1]) or 1
            lw = min(max([sum(_unit(ch) for ch in str(r[0])) for r in rows] or [2]) * fs + 6, (w - 52) * 0.4)
            vw = max([sum(_unit(ch) for ch in _fmtv(r[1], c)) for r in rows] or [3]) * (fs + 4) + 8
            hi = set(str(x) for x in c.get("hi", []))
            body += '<div class="bars">' + "".join(
                f'<div class="row{" hi" if (str(k) in hi or str(r[0]) in hi) else ""}" style="grid-template-columns:{lw:.0f}px 1fr {vw:.0f}px; margin-top:12px">'
                f'<span style="font-size:{fs}px">{X.rich(str(r[0]))}</span><i class="b{k}" style="height:{rh}px; width:{100 * abs(float(r[1])) / mx:.1f}%"></i><b style="font-size:{fs + 4}px">{X.rich(_fmtv(r[1], c))}</b></div>'
                for k, r in enumerate(rows)) + "</div>"
            if c.get("delta"): body += f'<div class="delta">{X.rich(c["delta"])}</div>'
            at_rows = c.get("at_rows") or []
            for k, r in enumerate(rows):
                tk = self.T(at_rows[k] if k < len(at_rows) else None, t, t0 + 0.4 + k * min(0.35, 1.6 / max(len(rows), 1)))
                js.append(f'tl.from("#{cid} .b{k}", {{scaleX:0, duration:0.6, ease:"expo.out"}}, {tk:.3f});')
            if c.get("delta"): js.append(f'tl.from("#{cid} .delta", {{opacity:0, y:14, duration:0.4, ease:"back.out(2)"}}, {self.T(c.get("at_delta"), t, t0 + 1.2):.3f});')
        elif typ == "line":
            pts = c.get("points", []); W_, H_ = (w - 52, 230 if self.V else 190)
            vals = [float(p[1]) for p in pts] or [0.0, 1.0]
            vmin = min(0.0, min(vals)); vmax = (max(vals) * 1.1) or 1.0
            xy = [((k * W_ / max(len(vals) - 1, 1)), H_ - H_ * (v - vmin) / (vmax - vmin)) for k, v in enumerate(vals)]
            Lp = length(xy)
            imax = max(range(len(vals)), key=lambda k: vals[k])
            showv = {0, len(xy) - 1, imax} if len(xy) > 4 else set(range(len(xy)))
            showd = {0, len(xy) - 1} if len(xy) > 3 else set(range(len(xy)))
            el = []
            for k, ((x, y), p) in enumerate(zip(xy, pts)):
                anc = "start" if k == 0 else ("end" if k == len(xy) - 1 else "middle")
                el.append(f'<circle class="pt" cx="{x:.0f}" cy="{y:.0f}" r="{6 if len(xy) < 12 else 3}"/>')
                if k in showv: el.append(f'<text class="vv" x="{x:.0f}" y="{y - 14:.0f}" text-anchor="{anc}">{X.rich(_fmtv(p[1], c))}</text>')
                if k in showd: el.append(f'<text x="{x:.0f}" y="{H_ + 28}" text-anchor="{anc}">{X.rich(str(p[0]))}</text>')
            if c.get("value"):
                body += f'<div class="v" style="font-size:{self.stat_size(c, w)[1]}px">{X.rich(str(c["value"]))}{unit}</div>'
            body += (f'<svg class="ln" width="{W_:.0f}" height="{H_ + 40}"><line class="ax" x1="0" y1="{H_}" x2="{W_:.0f}" y2="{H_}"/>'
                     f'<path class="pl" d="{d_of([xy])}" stroke-dasharray="{Lp:.1f}" stroke-dashoffset="{Lp:.1f}"/>{"".join(el)}</svg>')
            js.append(f'tl.to("#{cid} .pl", {{strokeDashoffset:0, duration:1.4, ease:"power2.inOut"}}, {t0 + 0.4:.3f});')
            js.append(f'tl.from("#{cid} svg circle, #{cid} svg text", {{opacity:0, duration:0.3, stagger:{min(0.25, 1.2 / max(len(el), 1)):.3f}}}, {t0 + 0.45:.3f});')
        elif typ == "list":
            items = c.get("items", []); f, cols, rows = self.list_layout(c, w)
            li = "".join(f'<li style="font-size:{f}px"><i>{k + 1:02d}</i><b>{words_html(X, it if isinstance(it, str) else it.get("text", ""), chars=False)}</b>'
                         + (f'<em>{X.rich(it["value"])}</em>' if isinstance(it, dict) and it.get("value") else "") + "</li>" for k, it in enumerate(items))
            body += f'<ol class="list" style="grid-template-columns:repeat({cols}, minmax(0, 1fr)); grid-template-rows:repeat({rows}, auto); grid-auto-flow:column">{li}</ol>'
            js.append(f'tl.from("#{cid} li", {{opacity:0, x:-16, duration:0.4, ease:"expo.out", stagger:{min(0.18, 2.0 / max(len(items), 1)):.3f}}}, {t0 + 0.3:.3f});')
            X.used_text.update("0123456789")
        elif typ == "images":
            boxes, hh = self.img_layout(c, w - 52)
            im = "".join(f'<img src="{X.asset(s_)}" alt="" style="left:{x:.0f}px; top:{y:.0f}px; width:{ww:.0f}px; height:{hh_:.0f}px">'
                         + (f'<div class="cap" style="left:{x + 6:.0f}px; top:{y + hh_ - 26:.0f}px">{X.rich(cap)}</div>' if cap else "")
                         for s_, x, y, ww, hh_, cap in boxes)
            if boxes:
                body += f'<div class="imgs" style="height:{hh:.0f}px">{im}</div>'
                js.append(f'tl.from("#{cid} .imgs img", {{opacity:0, scale:0.92, duration:0.45, ease:"expo.out", stagger:{min(0.15, 1.5 / max(len(boxes), 1)):.3f}}}, {t0 + 0.3:.3f});')
        elif typ == "text":
            f, n = fit(c.get("text", ""), w - 52, 300, 34, 18, maxlines=8)
            body += f'<div class="v txt" style="font-size:{f}px; line-height:1.4">{words_html(X, c.get("text", ""), chars=False)}</div>'
        if c.get("sub"): body += f'<div class="s">{X.rich(c["sub"])}</div>'
        X.clip(cid, t, d, f'<div class="card {c.get("tone", "")}" style="{pos}">{body}</div>', "at-ov", 25, track=4 + i % 3)
        self.tw(f'tl.from("#{cid} .card", {{opacity:0, x:-30, duration:0.5, ease:"expo.out"}}, {t0 + 0.05:.3f});')
        self.tw(f'tl.to("#{cid} .card", {{opacity:0, x:20, duration:0.3, ease:"power2.in"}}, {t1 - 0.32:.3f});')
        for s_ in js: self.tw(s_)
        X.sfx(t0 + 0.05, "enter")


def _empty_card(c):
    if not c: return True
    typ = c.get("type", "stat")
    body = {"stat": "value", "bars": "rows", "line": "points", "list": "items", "images": "images", "text": "text"}.get(typ, "value")
    return not c.get(body) and not c.get("sub")


def _is_num(v):
    s = str(v).replace(",", "").lstrip("+−-$¥≈").rstrip("%")
    try: float(s); return True
    except ValueError: return False


def _num(v):
    s = str(v).replace(",", "").lstrip("+−-$¥≈").rstrip("%")
    return float(s), (len(s.split(".")[1]) if "." in s else 0)


def _fmtv(v, c):
    if isinstance(v, (int, float)):
        dec = c.get("dec", 0 if float(v).is_integer() else 1)
        return f'{c.get("prefix", "")}{v:,.{dec}f}{c.get("suffix", "")}'
    return str(v)


def _nice_bar(s, lat, lo=140):
    ppk = px_per_km(lat) * s
    for km in (5, 10, 20, 50, 100, 200, 500, 1000, 2000, 3000, 5000):
        if km * ppk >= lo: return km, km * ppk
    return 5000, 5000 * ppk


def _lab_rect(sd, sx, sy, w, h):
    g = 20
    return {"E": (sx + g, sy - h / 2, sx + g + w, sy + h / 2), "W": (sx - g - w, sy - h / 2, sx - g, sy + h / 2),
            "N": (sx - w / 2, sy - g - h, sx + w / 2, sy - g), "S": (sx - w / 2, sy + g, sx + w / 2, sy + g + h),
            "NE": (sx + 12, sy - 12 - h, sx + 12 + w, sy - 12), "NW": (sx - 12 - w, sy - 12 - h, sx - 12, sy - 12),
            "SE": (sx + 12, sy + 12, sx + 12 + w, sy + 12 + h), "SW": (sx - 12 - w, sy + 12, sx - 12, sy + 12 + h)}[sd]


def _lab_css(sd, w, h):
    g = 20
    return {"E": f"left:{g}px; top:{-h / 2:.0f}px", "W": f"right:{g}px; top:{-h / 2:.0f}px", "N": f"left:{-w / 2:.0f}px; bottom:{g}px",
            "S": f"left:{-w / 2:.0f}px; top:{g}px", "NE": "left:12px; bottom:12px", "NW": "right:12px; bottom:12px",
            "SE": "left:12px; top:12px", "SW": "right:12px; top:12px"}[sd]


def _hit(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def WORLD(beats, times, X, D):
    Atlas(beats, times, X, D).run()
