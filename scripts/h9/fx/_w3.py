"""shared helpers for the W3 chart / map plugins (files starting with _ are not effects; load by path).

Everything is laid out in pixels inside the page's content box, which already keeps clear of the header, the
caption band and — in 9:16 — the platform safe areas (top 200 px, bottom 400 px, right 120 px on the lower half).
"""
import importlib.util, json, math, pathlib, random, sys

HERE = pathlib.Path(__file__).parent


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, HERE / f"{name}.py")
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F = load("_fit")


# ---------------------------------------------------------------- layout
def resolve(X, path):
    """a user file (GeoJSON …): absolute, else next to video.json (X.src), else relative to the skill root."""
    pth = pathlib.Path(path)
    if pth.is_absolute(): return pth
    for root in (pathlib.Path(X.src), HERE.parents[2]):
        if (root / pth).exists(): return root / pth
    raise SystemExit(f"file not found: {path} (looked next to the video.json and in the skill folder)")


def box(X):
    """content box (x0, y0, x1, y1) in px: under the header, above the caption, inside the safe areas."""
    if X.portrait: return 64, 290, X.W - 120, 1250
    return 110, 150, X.W - 110, 880


def best_grid(n, w, h):
    """columns for n square cells in a w×h box: biggest cells, preferring full last rows (100 -> 10×10)."""
    import math as _m
    best = None
    for cols in range(1, n + 1):
        rows = _m.ceil(n / cols)
        cell = min(w / cols, h / rows)
        waste = (rows * cols - n) / max(n, 1)
        score = cell * (1 - 5.0 * waste)
        if best is None or score > best[0] + 1e-9: best = (score, cols, rows, cell)
    return best[1], best[2], best[3]


def px(X, vmin): return min(X.W, X.H) * vmin / 100


def fit_px(X, text, w, h, max_px, min_px=22, max_lines=3):
    """F.fit in pixels -> (size_px, [lines])."""
    u = min(X.W, X.H) / 100
    s, lines = F.fit(text, w / u, h / u, max_px / u, min_px / u, max_lines)
    return s * u, lines


def lines_html(X, lines, cls="fl"): return F.lines_html(X, lines, cls)


def num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    s = str(v).replace(",", "").replace("，", "").strip()
    mul = 1.0
    if s.endswith("亿"): mul, s = 1e8, s[:-1]
    elif s.endswith("万"): mul, s = 1e4, s[:-1]
    if s.endswith("%"): s = s[:-1]
    try: return float(s) * mul
    except ValueError: return None


def fmt(v, dec=0):
    return f"{v:,.{dec}f}"


def dec_of(vals, cap=2):
    d = 0
    for v in vals:
        s = repr(float(v)).rstrip("0").rstrip(".")
        if "." in s: d = max(d, len(s.split(".")[1]))
    return min(cap, d)


def count(X, sel, t, v, dur=0.9, dec=0, ease="power3.out", start=0.0):
    """count an element's text from start to v (deterministic: driven by the master timeline)."""
    X.used_text.update("0123456789.,-+%")
    X.tw(f'(()=>{{const o={{v:{start}}}, el=document.querySelector("{sel}"), f={F.js_fmt(dec)}; if(!el) return; '
         f'tl.to(o, {{v:{v}, duration:{dur:.2f}, ease:"{ease}", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {t:.3f});}})();')


def rand(p, salt=0): return random.Random(int(p.get("seed", 9)) * 7919 + salt)


# ---------------------------------------------------------------- shared look
CSS = r"""
.fx .w3 { position:absolute; inset:0; }
.fx .w3 .w3t { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; letter-spacing:-.01em; }
.fx .w3 .w3t .fl { display:block; white-space:nowrap; }
.fx .w3 .w3n { position:absolute; font:500 20px/1.4 var(--f-mono, monospace); color:var(--muted); letter-spacing:.04em; white-space:nowrap; }
.fx .w3 .w3k { font-family:var(--f-num, var(--f-display)); font-weight:900; font-variant-numeric:tabular-nums; letter-spacing:-.02em; line-height:1; }
.fx .w3 .w3tag { display:inline-block; font:700 18px var(--f-body); color:var(--bg); background:var(--fg); padding:3px 10px; border-radius:4px; white-space:nowrap; }
.fx .w3 .w3mock { position:absolute; font:700 18px var(--f-body); color:var(--bg); background:var(--muted); padding:3px 10px; border-radius:4px; }
.fx .w3 svg.w3s { position:absolute; left:0; top:0; overflow:visible; }
.fx .w3 .w3lab { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; line-height:1.15; }
.fx .w3 .w3lab small { display:block; font-weight:500; color:var(--muted); font-size:.72em; margin-top:2px; }
"""


def base(X):
    X.css("fx-w3", CSS)


def head(X, p, x0, y0, w, max_px=None):
    """title + note block at (x0, y0); returns (html, height_px)."""
    title, note = p.get("title", ""), p.get("note", "")
    if not title and not note: return "", (44 if p.get("mock") else 0)     # keep the 示意 tag's corner clear
    if p.get("mock"): w -= 90
    mp = max_px or (56 if X.portrait else 50)
    s, ls = fit_px(X, title, w, mp * 2.3, mp, 26, 2) if title else (0, [])
    h = s * 1.12 * len(ls)
    out = f'<div class="w3t" style="left:{x0}px; top:{y0}px; font-size:{s:.1f}px">{lines_html(X, ls)}</div>' if title else ""
    if note:
        out += f'<div class="w3n" style="left:{x0}px; top:{y0 + h + 8:.0f}px">{X.rich(note)}</div>'
        h += 36
    return out, h + 18


def mock_tag(X, p, x, y):
    if not p.get("mock"): return ""
    lab = p["mock"] if isinstance(p["mock"], str) else "示意"
    return f'<div class="w3mock" style="left:{x}px; top:{y}px">{X.rich(lab)}</div>'


def head_in(X, s, t, p):
    """entrance for what head() / mock_tag() drew (only tweens elements that exist, so no empty GSAP targets)."""
    if p.get("title"):
        X.tw(f'tl.from("{s} .w3t .fl", {{yPercent:60, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t:.3f});')
    rest = ", ".join(f"{s} {c}" for c, k in ((".w3n", "note"), (".w3mock", "mock")) if p.get(k))
    if rest:
        X.tw(f'tl.from("{rest}", {{opacity:0, duration:0.4}}, {t + 0.2:.3f});')


# ---------------------------------------------------------------- icons (24×24 line icons, our own)
ICONS = {
    "person": '<circle cx="12" cy="7" r="4"/><path d="M4 22c0-4.4 3.6-8 8-8s8 3.6 8 8z"/>',
    "cup": '<path d="M6 7h12l-1.4 15H7.4z"/><path d="M5 7h14M13 7l2-5"/>',
    "store": '<path d="M4 10v11h16V10"/><path d="M3 10l2-6h14l2 6z"/><path d="M10 21v-6h4v6"/>',
    "car": '<path d="M3 16v-4l2-5h14l2 5v4z"/><circle cx="7.5" cy="17" r="2"/><circle cx="16.5" cy="17" r="2"/>',
    "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "house": '<path d="M3 11l9-8 9 8v10H3z"/><path d="M10 21v-6h4v6"/>',
    "coin": '<circle cx="12" cy="12" r="9"/><path d="M9 8l3 4 3-4M12 12v5M9 13h6M9 16h6"/>',
    "box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "heart": '<path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-3 4.5 4.5 0 0 1 8 3c0 6-8 11-8 11z"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="1.5"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "check": '<path d="M5 12l5 5 9-10"/>',
    "cross": '<path d="M6 6l12 12M18 6L6 18"/>',
}


def icon_svg(name, cls="w3ic"):
    body = ICONS.get(name)
    if body is None and str(name).lstrip().startswith(("M", "m")): body = f'<path d="{name}"/>'
    return f'<svg class="{cls}" viewBox="0 0 24 24">{body or ICONS["person"]}</svg>'


# ---------------------------------------------------------------- geo
def topo(path, obj=None):
    """decode a TopoJSON file -> list of features {props, polys: [[ring, hole...], ...]} in lon/lat."""
    t = json.loads(pathlib.Path(path).read_text())
    tr = t.get("transform")
    arcs = []
    for a in t["arcs"]:
        if tr:
            (sx, sy), (tx, ty) = tr["scale"], tr["translate"]
            x = y = 0; pts = []
            for dx, dy in a:
                x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        else: pts = [tuple(q) for q in a]
        arcs.append(pts)

    def ring(ix):
        pts = []
        for i in ix:
            a = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts.extend(a if not pts else a[1:])
        return pts
    o = t["objects"][obj] if obj else list(t["objects"].values())[0]
    out = []
    for g in o["geometries"]:
        if g["type"] not in ("Polygon", "MultiPolygon"): continue
        polys = [g["arcs"]] if g["type"] == "Polygon" else g["arcs"]
        out.append({"props": g.get("properties", {}), "polys": [[ring(r) for r in poly] for poly in polys]})
    return out


def laea(lon0, lat0):
    """Lambert azimuthal equal-area centred on (lon0, lat0) -> f(lon, lat) = (x_km, y_km), y up."""
    R = 6371.0088
    l0, p0 = math.radians(lon0), math.radians(lat0)

    def f(lon, lat):
        l, p = math.radians(lon), math.radians(lat)
        k = math.sqrt(2 / max(1e-12, 1 + math.sin(p0) * math.sin(p) + math.cos(p0) * math.cos(p) * math.cos(l - l0)))
        return R * k * math.cos(p) * math.sin(l - l0), R * k * (math.cos(p0) * math.sin(p) - math.sin(p0) * math.cos(p) * math.cos(l - l0))
    return f


def ring_area(r):
    return sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r))) / 2


def path_d(pts, closed=True, eps=0.6):
    out, last = [], None
    for x, y in pts:
        if last and abs(x - last[0]) + abs(y - last[1]) < eps: continue
        out.append(f"{x:.1f},{y:.1f}"); last = (x, y)
    if len(out) < 2: return ""
    return "M" + "L".join(out) + ("Z" if closed else "")


# ---------------------------------------------------------------- axes
def nice_ticks(lo, hi, n=5):
    """round tick values covering [lo, hi] (about n of them)."""
    if hi <= lo: hi = lo + 1
    raw = (hi - lo) / max(1, n - 1)
    mag = 10 ** math.floor(math.log10(raw))
    step = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw), default=10 * mag)
    a = math.floor(lo / step) * step; b = math.ceil(hi / step) * step
    out, v = [], a
    while v <= b + step * 1e-6:
        out.append(round(v, 10)); v += step
    return out


def tick_label(v, div=1, suf=""):
    x = v / div
    s = f"{x:,.0f}" if abs(x - round(x)) < 1e-9 else f"{x:,.1f}"
    return s + suf


def tick_auto(v):
    """a log-axis tick in its own magnitude: 1 · 1,000 · 10万 · 1亿 · 100亿."""
    for dv, sf in ((1e8, "亿"), (1e4, "万")):
        if abs(v) >= dv: return f"{v / dv:,.10g}{sf}"
    return f"{v:,.10g}"


def place_labels(items, min_gap):
    """items: list of dicts with y (desired centre) and h; nudges vertically so boxes don't overlap. In place."""
    items.sort(key=lambda o: o["y"])
    for i in range(1, len(items)):
        a, b = items[i - 1], items[i]
        need = (a["h"] + b["h"]) / 2 + min_gap
        if b["y"] - a["y"] < need and abs(b.get("x", 0) - a.get("x", 0)) < max(a.get("w", 9e9), b.get("w", 9e9)):
            b["y"] = a["y"] + need
    return items


def hit(a, b, pad=4):
    """axis-aligned boxes (x, y, w, h) overlap?"""
    return a[0] < b[0] + b[2] + pad and b[0] < a[0] + a[2] + pad and a[1] < b[1] + b[3] + pad and b[1] < a[1] + a[3] + pad


def seg_hit(bx, a, b, pad=4):
    """does segment a-b cross box (x, y, w, h)? (sampled; fine for label avoidance)"""
    n = max(2, int(math.dist(a, b) / 6))
    for i in range(n + 1):
        u = i / n; x = a[0] + (b[0] - a[0]) * u; y = a[1] + (b[1] - a[1]) * u
        if bx[0] - pad <= x <= bx[0] + bx[2] + pad and bx[1] - pad <= y <= bx[1] + bx[3] + pad: return True
    return False


def seg_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]; L = dx * dx + dy * dy
    u = 0 if not L else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L))
    return math.dist(p, (a[0] + dx * u, a[1] + dy * u))


def pick_box(cands, taken, lines=(), bounds=None, pad=4):
    """first candidate box that misses every taken box and polyline and stays in bounds (x0, y0, x1, y1) -> box | None."""
    for c in cands:
        if bounds and (c[0] < bounds[0] or c[1] < bounds[1] or c[0] + c[2] > bounds[2] or c[1] + c[3] > bounds[3]): continue
        if any(hit(c, o, pad) for o in taken): continue
        if any(seg_hit(c, ln[i], ln[i + 1]) for ln in lines for i in range(len(ln) - 1)): continue
        return c
    return None


def bezier(p0, p1, p2, p3, n=16):
    """sample a cubic bezier -> list of (x, y)."""
    out = []
    for i in range(n + 1):
        u = i / n; a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u ** 2; e = u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + e * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + e * p3[1]))
    return out


def travel(X, sel, pts, t, dur, repeat=0, delay_each=0.0):
    """move an absolutely-positioned element (left:0; top:0) along sampled points with keyframes (deterministic)."""
    seg = dur / max(1, len(pts) - 1)
    kf = ", ".join(f"{{x:{x:.1f}, y:{y:.1f}, duration:{seg:.3f}, ease:\"none\"}}" for x, y in pts[1:])
    X.tw(f'tl.fromTo("{sel}", {{x:{pts[0][0]:.1f}, y:{pts[0][1]:.1f}, opacity:1}}, {{keyframes:[{kf}], repeat:{repeat}, immediateRender:false}}, {t:.3f});')
