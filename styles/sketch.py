"""sketch · 手绘白板风 —— RSA Animate / Minute Physics / 国内手绘科普的语言：一张方格本，一支马克笔，讲到哪画到哪。

所有图形都是"画"出来的：线条有起笔和收笔的超出、轻微的弯曲和抖动，圆圈画过头一点再收住，箭头是两笔勾出来的；
框、柱、刻度、问号、购物车、会员卡、小人都由同一支笔按讲解顺序一笔一笔画出，笔尖跟着线走。
荧光笔垫在字下面（正片叠底），红笔负责划掉和圈重点，蓝笔负责连线。字是手写体（霞鹜文楷 / Caveat / Kalam），
写字时从左往右露出，笔尖沿着字行移动。

几何全部在构建时用带种子的随机数算好（同一份 video.json 每次画出完全一样的线），不依赖浏览器里的 rough.js；
每条线用 pathLength=1 + stroke-dashoffset 画出来，所以任何长度、任何形状都能"写"。

场景（SCENES）：hook 大数字 + 涂鸦 · bar 一根条拆成两段 · question 问号和候选答案 · ratio 两个量比一比 · tag 价签划掉改价 ·
dots 100 个小人里有几个 · loop 循环箭头 · thesis 划掉一个词、圈出另一个 · outro 便利贴落版。横屏竖屏各自排版。
"""
import math, random
from h9 import fit

STYLE = {
    "name": "手绘白板", "en": "Sketch", "benchmarks": ["RSA Animate", "Minute Physics", "国内手绘科普"],
    "tokens": {
        "bg": "#f7f6f1", "fg": "#1f1f22", "paper": "#f7f6f1", "ink": "#1f1f22", "muted": "#6d6b66", "accent": "#e2483b", "accent2": "#ffd84a",
        "alert": "#e2483b", "line": "#d9dde3", "card": "#fffdf6", "card-fg": "#1f1f22",
        "red": "#e2483b", "blue": "#2b67d1", "green": "#2f9a5c", "hl": "#ffd84a", "grid": "rgba(66,118,190,.13)", "grid2": "rgba(66,118,190,.22)",
        "cap-bg": "#ffd84a", "cap-fg": "#1f1f22", "cap-size": "40px", "cap-weight": "500", "cap-pad": "6px 20px 8px", "cap-radius": "3px",
        "cap-shadow": "none", "cap-bottom": "58px", "cap-em": "#e2483b", "punch-top": "71%", "punch-size": "70px", "punch-stroke": "0",
    },
    "fonts": {"display": "lxgw-wenkai", "body": "lxgw-wenkai", "hand": ["caveat", "lxgw-wenkai"], "num": ["kalam", "lxgw-wenkai"],
              "latin": ["patrick-hand", "lxgw-wenkai"], "punch": "lxgw-wenkai", "cap": "lxgw-wenkai"},
    "motion": {"ease": "power2.out", "dur": 0.5, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.05})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 70, "bottom": 0, "h": 380}, "portrait": {"left": 390, "bottom": 600, "h": 300}},
    "sfx": {"transition": ("paper", 0.35), "enter": ("paper", 0.3), "pop": ("pop", 0.4), "hit": ("tick", 0.45), "brush": ("brush", 0.28),
            "line": ("brush", 0.22), "mascot": ("whoosh_soft", 0.25), "title": ("paper", 0.35), "write": ("type", 0.18)},
}

CSS = r"""
.sk { position:absolute; inset:0; background-color:var(--paper); }
.sk .paper { position:absolute; inset:-40%; background-color:var(--paper);
  background-image:linear-gradient(var(--grid2) 1.5px, transparent 1.5px), linear-gradient(90deg, var(--grid2) 1.5px, transparent 1.5px),
                   linear-gradient(var(--grid) 1px, transparent 1px), linear-gradient(90deg, var(--grid) 1px, transparent 1px);
  background-size:200px 200px, 200px 200px, 40px 40px, 40px 40px; background-position:-1px -1px; }
.sk .paper::after { content:""; position:absolute; top:0; bottom:0; left:calc(40% / 1.8 + var(--mx, 70px)); width:2px; background:rgba(226,72,59,.28); }
.sk .cam { position:absolute; inset:0; }
.sk svg.ink { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.sk svg.ink path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.sk svg.under path { mix-blend-mode:multiply; }
.sk svg.ink .solid { stroke:none; }
.sk .t { position:absolute; white-space:nowrap; line-height:1.15; color:var(--ink); font-family:var(--f-display); font-weight:500; transform-origin:0 70%; }
.sk .t.hand { font-family:var(--f-hand); font-weight:700; }
.sk .t.num { font-family:var(--f-num); font-weight:700; letter-spacing:-.01em; }
.sk .t.lat { font-family:var(--f-latin); }
.sk .pen { position:absolute; left:0; top:0; width:0; height:0; z-index:8; pointer-events:none; }
.sk .pen svg { position:absolute; left:-6px; top:-148px; width:120px; height:160px; overflow:visible; filter:drop-shadow(6px 10px 6px rgba(0,0,0,.18)); }
.sk .hd { position:absolute; left:96px; right:96px; top:34px; display:flex; justify-content:space-between; align-items:flex-start; z-index:6; pointer-events:none; }
.sk .hd .l { font-family:var(--f-display); font-size:30px; color:var(--ink); }
.sk .hd .l small { font-size:28px; color:var(--muted); margin-left:12px; }
.sk .hd .r { font-family:var(--f-num); font-weight:700; font-size:30px; color:var(--red); }
.sk .ft { position:absolute; left:96px; right:330px; bottom:16px; font-family:var(--f-display); font-size:28px; color:var(--muted); z-index:6; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sk .note { position:absolute; background:#fff3a6; box-shadow:0 18px 30px rgba(0,0,0,.14), inset 0 -30px 40px rgba(0,0,0,.03); }
.sk .tape { position:absolute; background:rgba(214,206,186,.72); }
#root.v .sk { --mx:34px; } #root.v .sk .hd { left:60px; right:60px; top:206px; } #root.v .sk .hd .l { font-size:30px; }
#root.v .sk .ft { left:60px; right:60px; bottom:auto; top:1470px; font-size:28px; white-space:normal; }
"""

PEN = """<svg viewBox="0 0 120 160"><g transform="rotate(28 6 148)">
<path d="M6 148 L0 128 L12 128 Z" fill="#1f1f22"/>
<rect x="-2" y="70" width="16" height="58" rx="3" fill="#2b2b30"/>
<rect x="-6" y="-8" width="24" height="84" rx="8" fill="#e2483b"/>
<rect x="-6" y="40" width="24" height="10" fill="#fbfaf6" opacity=".85"/>
<rect x="-1" y="-8" width="5" height="78" rx="2" fill="#fff" opacity=".28"/></g></svg>"""


# ---------------------------------------------------------------- geometry (seeded, build time)
def _c(p): return f"{p[0]:.1f},{p[1]:.1f}"


def _bez(p0, p1, p2, p3, n=8):
    out = []
    for i in range(n + 1):
        s = i / n; u = 1 - s
        out.append((u ** 3 * p0[0] + 3 * u * u * s * p1[0] + 3 * u * s * s * p2[0] + s ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * s * p1[1] + 3 * u * s * s * p2[1] + s ** 3 * p3[1]))
    return out


def _len(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _smooth(pts, closed=False):
    """catmull-rom through the points -> one cubic path."""
    if len(pts) < 3: return "M" + " L".join(_c(p) for p in pts)
    P = ([pts[-1]] + pts + [pts[0], pts[1]]) if closed else ([pts[0]] + pts + [pts[-1]])
    d = "M" + _c(P[1])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{_c(c1)} {_c(c2)} {_c(p2)}"
    return d


class Hand:
    """one marker: every mark it makes wobbles a little, overshoots a little, never repeats."""
    def __init__(self, seed, rough=1.0):
        self.r = random.Random(seed); self.k = rough

    def j(self, a): return self.r.uniform(-a, a) * self.k

    def line(self, x1, y1, x2, y2, over=None):
        L = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
        o = (over if over is not None else self.r.uniform(3, 8)) * self.k
        a = (x1 - ux * o * 0.4 + self.j(1.5), y1 - uy * o * 0.4 + self.j(1.5))
        b = (x2 + ux * o + self.j(1.5), y2 + uy * o + self.j(1.5))
        bow = L * self.r.uniform(-0.022, 0.022) * self.k
        c1 = (a[0] + (b[0] - a[0]) / 3 + nx * bow * self.r.uniform(0.5, 1.3), a[1] + (b[1] - a[1]) / 3 + ny * bow * self.r.uniform(0.5, 1.3))
        c2 = (a[0] + 2 * (b[0] - a[0]) / 3 + nx * bow * self.r.uniform(0.5, 1.3), a[1] + 2 * (b[1] - a[1]) / 3 + ny * bow * self.r.uniform(0.5, 1.3))
        pts = _bez(a, c1, c2, b, 6)
        return f"M{_c(a)} C{_c(c1)} {_c(c2)} {_c(b)}", pts

    def poly(self, pts, closed=False):
        """a pen line through points: straight-ish segments, each with its own wobble."""
        seq = list(pts) + ([pts[0]] if closed else [])
        ds, allp = [], []
        for a, b in zip(seq, seq[1:]):
            d, p = self.line(a[0], a[1], b[0], b[1], over=self.r.uniform(1, 4)); ds.append(d); allp += p
        return " ".join(ds), allp

    def rect(self, x, y, w, h):
        return self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], closed=True)

    def ellipse(self, cx, cy, rx, ry, a0=None, over=0.32, n=30):
        a0 = self.r.uniform(-2.6, -0.6) if a0 is None else a0
        f1, f2 = self.r.uniform(0, 6.3), self.r.uniform(0, 6.3)
        sweep = 2 * math.pi + over * self.r.uniform(0.7, 1.3)
        dx, dy = self.j(rx * 0.06), self.j(ry * 0.08)
        pts = []
        for i in range(n + 1):
            s = i / n; a = a0 + sweep * s
            k = 1 + 0.035 * self.k * math.sin(2 * a + f1) + 0.02 * self.k * math.sin(3 * a + f2)
            pts.append((cx + dx * s + rx * k * math.cos(a), cy + dy * s + ry * k * math.sin(a)))
        return _smooth(pts), pts

    def arrow(self, x1, y1, x2, y2, curve=0.12, head=None):
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        bend = L * curve * (1 if self.r.random() < 0.5 else -1) if curve else 0
        c = ((x1 + x2) / 2 + nx * bend + self.j(4), (y1 + y2) / 2 + ny * bend + self.j(4))
        pts = []
        for i in range(13):
            s = i / 12
            pts.append(((1 - s) ** 2 * x1 + 2 * (1 - s) * s * c[0] + s * s * x2, (1 - s) ** 2 * y1 + 2 * (1 - s) * s * c[1] + s * s * y2))
        tx, ty = x2 - c[0], y2 - c[1]; tl_ = math.hypot(tx, ty) or 1; tx, ty = tx / tl_, ty / tl_
        hl = head or max(16, min(30, L * 0.12))
        hs = []
        for sgn in (1, -1):
            a = math.radians(152 * sgn)
            hx, hy = tx * math.cos(a) - ty * math.sin(a), tx * math.sin(a) + ty * math.cos(a)
            d, p = self.line(x2, y2, x2 + hx * hl, y2 + hy * hl, over=1); hs.append((d, p))
        shaft = _smooth(pts)
        return shaft + " " + hs[0][0] + " " + hs[1][0], pts + hs[0][1] + hs[1][1]

    def hatch(self, x, y, w, h, gap=16, slope=0.9):
        """diagonal fill strokes clipped to the box, drawn as one zig-zag pass of the pen."""
        ds, allp = [], []
        k = 0; c = -h * slope
        while c < w:
            xa, ya = x + max(c, 0), y + (0 if c >= 0 else -c / slope)
            xb, yb = x + min(c + h * slope, w), y + (h if c + h * slope <= w else (w - c) / slope)
            if (xb - xa) > 4:
                a, b = ((xa, ya), (xb, yb)) if k % 2 == 0 else ((xb, yb), (xa, ya))
                d, p = self.line(a[0], a[1], b[0], b[1], over=self.r.uniform(-2, 2)); ds.append(d); allp += p
            c += gap; k += 1
        return " ".join(ds), allp

    def underline(self, x1, x2, y, wave=0.0):
        if not wave: return self.line(x1, y, x2, y)
        n = max(4, int((x2 - x1) / 38)); pts = [(x1 + (x2 - x1) * i / n, y + (wave if i % 2 else -wave) + self.j(2)) for i in range(n + 1)]
        return _smooth(pts), pts

    def strike(self, x1, x2, y, h=10):
        """a scribbled-out word: three fast passes."""
        pts = [(x1 - 6, y + self.j(3)), (x2 + 6, y - h * 0.3 + self.j(3)), (x1 + 4, y + h * 0.4 + self.j(3)), (x2 + 2, y + h * 0.1 + self.j(3))]
        return self.poly(pts)

    def brace(self, x1, x2, y, depth=26, down=True):
        s = 1 if down else -1; m = (x1 + x2) / 2
        pts = [(x1, y), (x1 + 8, y + s * depth * 0.5), (m - 10, y + s * depth * 0.55), (m, y + s * depth), (m + 10, y + s * depth * 0.55), (x2 - 8, y + s * depth * 0.5), (x2, y)]
        pts = [(p[0] + self.j(1.5), p[1] + self.j(1.5)) for p in pts]
        return _smooth(pts), pts

    def qmark(self, cx, cy, s):
        hook = [(cx - 0.42 * s, cy - 0.45 * s), (cx - 0.3 * s, cy - 0.82 * s), (cx + 0.1 * s, cy - 0.95 * s), (cx + 0.42 * s, cy - 0.72 * s),
                (cx + 0.4 * s, cy - 0.38 * s), (cx + 0.05 * s, cy - 0.15 * s), (cx + 0.02 * s, cy + 0.2 * s)]
        hook = [(p[0] + self.j(s * 0.02), p[1] + self.j(s * 0.02)) for p in hook]
        dot_d, dot_p = self.ellipse(cx + 0.02 * s, cy + 0.48 * s, 0.06 * s, 0.06 * s, over=0.6, n=10)
        return _smooth(hook) + " " + dot_d, hook + dot_p

    def check(self, x, y, s):
        return self.poly([(x, y), (x + 0.35 * s, y + 0.38 * s), (x + s, y - 0.45 * s)])

    def star(self, cx, cy, r):
        pts = []
        for i in range(11):
            a = -math.pi / 2 + i * math.pi / 5 * 2
            pts.append((cx + r * math.cos(a) + self.j(r * 0.06), cy + r * math.sin(a) + self.j(r * 0.06)))
        return self.poly(pts)


# doodles: each returns [(d, pts, colour, width)], drawn in order
def cart(h, x, y, s):
    out = [h.poly([(x - 0.15 * s, y - 0.05 * s), (x, y - 0.05 * s), (x + 0.12 * s, y + 0.5 * s), (x + 0.86 * s, y + 0.5 * s), (x + 0.98 * s, y + 0.1 * s), (x + 0.06 * s, y + 0.1 * s)])]
    out.append(h.line(x + 0.14 * s, y + 0.62 * s, x + 0.84 * s, y + 0.62 * s))
    out.append(h.ellipse(x + 0.24 * s, y + 0.74 * s, 0.07 * s, 0.07 * s, n=12))
    out.append(h.ellipse(x + 0.74 * s, y + 0.74 * s, 0.07 * s, 0.07 * s, n=12))
    boxes = [h.rect(x + 0.18 * s, y - 0.18 * s, 0.26 * s, 0.26 * s), h.rect(x + 0.48 * s, y - 0.3 * s, 0.3 * s, 0.38 * s), h.rect(x + 0.32 * s, y - 0.5 * s, 0.22 * s, 0.24 * s)]
    return [(d, p, "ink", 6) for d, p in out] + [(d, p, "blue", 5) for d, p in boxes]


def card(h, x, y, w, hgt):
    r = []
    r.append((*h.rect(x, y, w, hgt), "ink", 6))
    r.append((*h.line(x, y + hgt * 0.24, x + w, y + hgt * 0.24, over=2), "ink", 5))
    r.append((*h.hatch(x + 4, y + 4, w - 8, hgt * 0.24 - 8, gap=14), "blue", 4))
    r.append((*h.rect(x + w * 0.08, y + hgt * 0.44, w * 0.18, hgt * 0.22), "ink", 4))
    r.append((*h.line(x + w * 0.08, y + hgt * 0.8, x + w * 0.6, y + hgt * 0.8, over=2), "ink", 4))
    return r


def person(h, cx, cy, s, colour="ink"):
    head = h.ellipse(cx, cy - 0.32 * s, 0.16 * s, 0.16 * s, n=14)
    body = h.poly([(cx - 0.3 * s, cy + 0.45 * s), (cx - 0.26 * s, cy + 0.02 * s), (cx + 0.26 * s, cy + 0.02 * s), (cx + 0.3 * s, cy + 0.45 * s)])
    return [(head[0], head[1], colour, 5), (body[0], body[1], colour, 5)]


def coin(h, cx, cy, r, sym="$"):
    c = h.ellipse(cx, cy, r, r, n=18)
    s1 = h.line(cx, cy - r * 0.62, cx, cy + r * 0.62, over=1)
    sp = [(cx + r * 0.3, cy - r * 0.32), (cx, cy - r * 0.42), (cx - r * 0.3, cy - r * 0.24), (cx - r * 0.18, cy - r * 0.02), (cx + r * 0.2, cy + r * 0.06),
          (cx + r * 0.32, cy + r * 0.28), (cx, cy + r * 0.42), (cx - r * 0.32, cy + r * 0.3)]
    s2 = (_smooth(sp), sp)
    return [(c[0], c[1], "ink", 5), (s2[0], s2[1], "ink", 6), (s1[0], s1[1], "ink", 4)]


def tagd(h, x, y, w, hgt):
    pts = [(x, y + hgt * 0.5), (x + hgt * 0.45, y), (x + w, y), (x + w, y + hgt), (x + hgt * 0.45, y + hgt)]
    t = h.poly(pts, closed=True)
    hole = h.ellipse(x + hgt * 0.42, y + hgt * 0.5, hgt * 0.09, hgt * 0.09, n=12)
    return [(t[0], t[1], "ink", 6), (hole[0], hole[1], "ink", 4)]


def tophat(h, cx, cy, s):
    crown = h.poly([(cx - 0.32 * s, cy), (cx - 0.28 * s, cy - 0.7 * s), (cx + 0.28 * s, cy - 0.7 * s), (cx + 0.32 * s, cy)])
    brim = h.ellipse(cx, cy + 0.02 * s, 0.55 * s, 0.12 * s, n=22)
    band = h.line(cx - 0.3 * s, cy - 0.16 * s, cx + 0.3 * s, cy - 0.16 * s, over=2)
    return [(crown[0], crown[1], "ink", 6), (brim[0], brim[1], "ink", 6), (band[0], band[1], "red", 8)]


# ---------------------------------------------------------------- the board: marks, writing, the pen and the camera
class Board:
    """collects every mark and line of writing in drawing order, then times them: an op with `at` starts on that cue,
    the ops between two cues share the time between them (faster when there is a lot to draw, never slower than 1.2×),
    and the pen follows whatever is being drawn."""
    SPEED = 1500        # px of ink per second at natural speed

    def __init__(self, X, cid, t, d, seed=None, tail=0.6):
        self.X, self.cid, self.t, self.d, self.tail = X, cid, t, d, tail
        self.h = Hand(seed if seed is not None else (sum(map(ord, cid)) * 7 + int(t * 100)))
        self.under, self.over, self.html, self.ops = [], [], [], []
        self.n = 0
        self.end = t

    def _id(self):
        self.n += 1
        return f"{self.cid}k{self.n}"

    def _op(self, dur, at, lag, pts, emit, pen=True):
        o = {"dur": dur, "at": at, "lag": lag, "pts": pts, "emit": emit, "pen": pen, "t": None}
        self.ops.append(o)
        return o

    def mark(self, d, pts, colour="ink", w=5, at=None, dur=None, layer="over", pen=True, op=1.0, lag=0.04, cap=None):
        dur = dur if dur is not None else min(0.9, max(0.15, max(_len(pts), 1) / self.SPEED))
        i = self._id()
        st = f"stroke:var(--{colour});stroke-width:{w}px;opacity:{op}" + (f";stroke-linecap:{cap}" if cap else "")
        (self.under if layer == "under" else self.over).append(f'<path id="{i}" d="{d}" pathLength="1" stroke-dasharray="1 2" stroke-dashoffset="1.05" style="{st}"/>')
        emit = lambda t0, du: self.X.tw(f'tl.fromTo("#{i}", {{strokeDashoffset:1.05}}, {{strokeDashoffset:0, duration:{du:.3f}, ease:"power1.inOut"}}, {t0:.3f});')
        return self._op(dur, at, lag, pts, emit, pen)

    def doodle(self, items, at=None, speed=1.0, lag=0.04):
        ops = [self.mark(d, p, c, w, at=at if k == 0 else None, lag=lag if k == 0 else 0.02, dur=min(0.8, max(0.12, _len(p) / (self.SPEED * speed))))
               for k, (d, p, c, w) in enumerate(items)]
        return ops[0] if ops else None

    def hl(self, x1, x2, y, thick, at=None, dur=None, colour="hl", lag=0.04):
        d, p = self.h.underline(x1, x2, y)
        return self.mark(d, p, colour, thick, at=at, dur=dur or min(0.6, max(0.2, (x2 - x1) / 1800)), layer="under", op=0.9, lag=lag, cap="butt")

    def custom(self, dur, emit, at=None, lag=0.04):
        """anything else that takes time on the board (a fill, a stamp): emit(t0, dur) writes its tweens."""
        return self._op(dur, at, lag, None, emit, pen=False)

    def text(self, s, x, y, px, cls="", colour="ink", at=None, dur=None, anchor="start", rot=None, pen=True, w=None, max_w=None, lag=0.04):
        X = self.X
        txt = str(s or "")
        if not txt.strip():
            return {"left": x, "top": y, "w": 0, "px": px, "base": y + px * 0.95, "op": None}
        em = text_em(txt, cls)
        if max_w and em * px > max_w: px = max(28, int(max_w / em))
        width = w or em * px
        left = x - width / 2 if anchor == "middle" else (x - width if anchor == "end" else x)
        rot = self.h.j(1.2) if rot is None else rot
        dur = dur if dur is not None else min(1.0, max(0.25, len(txt.replace(" ", "")) * 0.07))
        i = self._id()
        X.used_text.update(txt)
        self.html.append(f'<div id="{i}" class="t {cls}" style="left:{left:.0f}px; top:{y:.0f}px; font-size:{px:.0f}px; color:var(--{colour}); transform:rotate({rot:.2f}deg)">{X.rich(txt)}</div>')
        emit = lambda t0, du: X.tw(f'tl.fromTo("#{i}", {{clipPath:"inset(-30% 100% -30% -4%)"}}, {{clipPath:"inset(-30% -4% -30% -4%)", duration:{du:.3f}, ease:"none"}}, {t0:.3f});')
        base = y + px * 0.92; n = max(3, min(10, len(txt)))
        pts = [(left + width * k / n, base - (px * 0.32 if k % 2 else 0)) for k in range(n + 1)]
        o = self._op(dur, at, lag, pts, emit, pen)
        return {"left": left, "top": y, "w": width, "px": px, "base": y + px * 0.95, "op": o}

    def para(self, s, x, y, mx, width, mn=30, anchor="start", lh=1.22, at=None, **kw):
        """a title that may need two lines: one line while it fits at ≥ 62% of mx, else split at the best break
        near the middle (after punctuation if there is one). Returns the line dicts (empty list for no text)."""
        s = str(s or "").strip()
        if not s: return []
        px = fsz(s, width, mx, 1)
        if px >= max(mn, mx * 0.62) or len(s) < 8:
            return [self.text(s, x, y, max(px, mn), anchor=anchor, max_w=width, at=at, **kw)]
        mid = len(s) / 2
        cuts = [i + 1 for i, ch in enumerate(s[:-1]) if ch in "，、：；。,:; ）)" and abs(i + 1 - mid) < len(s) * 0.3]
        cut = min(cuts, key=lambda i: abs(i - mid)) if cuts else int(round(mid))
        a_, b_ = s[:cut].rstrip(), s[cut:].lstrip()
        px = max(mn, min(fsz(a_, width, mx, 1), fsz(b_, width, mx, 1)))
        l1 = self.text(a_, x, y, px, anchor=anchor, max_w=width, at=at, **kw)
        l2 = self.text(b_, x, y + px * lh, px, anchor=anchor, max_w=width, **kw)
        return [l1, l2]

    def schedule(self):
        ops = self.ops
        if not ops: return
        S, E = self.t + 0.1, self.t + self.d - self.tail
        starts = [] if ops[0]["at"] is not None else [(0, S)]
        starts += [(i, max(self.t, float(o["at"]))) for i, o in enumerate(ops) if o["at"] is not None]
        prev_end = self.t
        for k, (i0, a) in enumerate(starts):
            i1 = starts[k + 1][0] if k + 1 < len(starts) else len(ops)
            end = (starts[k + 1][1] - 0.03) if k + 1 < len(starts) else E
            a = max(a, prev_end)
            seg = ops[i0:i1]
            nat = seg[0]["dur"] + sum(max(0.0, o["lag"]) + o["dur"] for o in seg[1:])
            sc = max(0.12, min(1.6, (end - a) / nat)) if nat > 0 else 1.0
            cur = a; fin = a
            for j, o in enumerate(seg):
                if j: cur = max(a, cur + o["lag"] * sc)
                o["dur"] = max(0.05, o["dur"] * sc); o["t"] = cur
                cur += o["dur"]; fin = max(fin, cur)
            prev_end = fin
        self.end = max(o["t"] + o["dur"] for o in ops)
        for o in ops: o["emit"](o["t"], o["dur"])

    def build(self, extra_under="", extra_html="", extra_over=""):
        self.schedule()
        X, W, H = self.X, self.X.W, self.X.H
        pid = f"{self.cid}pen"
        pen_ops, free = [], self.t
        for o in sorted((o for o in self.ops if o["pen"] and o["pts"]), key=lambda o: o["t"]):
            if o["t"] >= free - 1e-3:
                pen_ops.append((o["t"], o["dur"], o["pts"])); free = o["t"] + o["dur"]
        if pen_ops:
            x0, y0 = pen_ops[0][2][0]
            X.tw(f'tl.set("#{pid}", {{x:{x0 + 260:.0f}, y:{y0 + 320:.0f}, opacity:0}}, {self.t:.3f});')
            ent = max(0.1, min(0.3, pen_ops[0][0] - self.t - 0.01))
            X.tw(f'tl.to("#{pid}", {{x:{x0:.0f}, y:{y0:.0f}, opacity:1, duration:{ent:.3f}, ease:"power2.out"}}, {pen_ops[0][0] - ent - 0.005:.3f});')
            last_end = pen_ops[0][0]
            for t0, dur, pts in pen_ops:
                if t0 - last_end > 0.05:   # lift and travel to the next stroke
                    tv = min(0.25, t0 - last_end - 0.01)
                    X.tw(f'tl.to("#{pid}", {{x:{pts[0][0]:.0f}, y:{pts[0][1]:.0f}, duration:{tv:.3f}, ease:"power2.inOut"}}, {t0 - tv - 0.005:.3f});')
                step = max(1, len(pts) // 9)
                sel = pts[::step] + ([pts[-1]] if (len(pts) - 1) % step else [])
                L = max(_len(sel), 1); acc = 0.0
                for p0, p in zip(sel, sel[1:]):
                    s0 = round(t0 + acc / L * dur, 3); acc += math.hypot(p[0] - p0[0], p[1] - p0[1]); s1 = round(t0 + acc / L * dur, 3)
                    if s1 - s0 < 0.006: continue
                    X.tw(f'tl.to("#{pid}", {{x:{p[0]:.0f}, y:{p[1]:.0f}, duration:{s1 - s0 - 0.001:.3f}, ease:"none"}}, {s0:.3f});')
                last_end = t0 + dur
            X.tw(f'tl.to("#{pid}", {{x:{W + 200}, y:{H * 0.8:.0f}, opacity:0, duration:0.4, ease:"power2.in"}}, {max(last_end + 0.15, self.t + self.d - 0.45):.3f});')
        u = f'<svg class="ink under" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(self.under)}{extra_under}</svg>'
        o = f'<svg class="ink over" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(self.over)}{extra_over}</svg>'
        return u + extra_html + "".join(self.html) + o + f'<div class="pen" id="{pid}">{PEN}</div>'


# ---------------------------------------------------------------- helpers
_FM = {}
CHAINS = {"num": ("kalam", "lxgw-wenkai"), "hand": ("caveat", "lxgw-wenkai"), "lat": ("patrick-hand", "lxgw-wenkai"), "": ("lxgw-wenkai",)}


def _metrics(fid):
    if fid not in _FM:
        _FM[fid] = None
        try:
            from fontTools.ttLib import TTFont
            from h9 import fonts
            fp = fonts.find(fonts.REG[fid]["file"])
            if fp:
                f = TTFont(str(fp), lazy=True)
                _FM[fid] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        except Exception:
            _FM[fid] = None
    return _FM[fid]


def text_em(txt, cls=""):
    """advance of a line in em, from the font that will draw it (falls back along the role's stack)."""
    chain = next((CHAINS[k] for k in ("num", "hand", "lat") if k in cls.split()), CHAINS[""])
    tot = 0.0
    for ch in fit.plain(txt):
        for fid in chain:
            m = _metrics(fid)
            if m and ord(ch) in m[0]:
                tot += m[1][m[0][ord(ch)]][0] / m[2] + (-0.01 if "num" in cls.split() else 0); break
        else:
            tot += fit.gw(ch)
    return tot


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def page(X, b, inner):
    X.css("sketch", CSS)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "白板课"); src = b.get("src", meta.get("src", ""))
    X.used_text.update(sec + src + "第九顶帽子0123456789/来源：")
    hd = f'<div class="hd" data-layout-allow-overlap><div class="l">第九顶帽子<small>{X.rich(sec)}</small></div><div class="r">{i + 1}/{n}</div></div>'
    ft = f'<div class="ft" data-layout-allow-overlap>{"来源：" + X.rich(src) if src else ""}</div>'
    return f'<div class="sk"><div class="cam"><div class="paper"></div>{inner}</div>{hd}{ft}</div>'


def shots(X, sel, t, d, keys):
    """the camera follows the pen: keys = [(time, scale, fx, fy)]; between moves it keeps creeping so nothing sits still."""
    W, H = X.W, X.H
    bx, by, bw, bh = box(X)
    def xy(sc, fx, fy):
        x = min(0, max(W - sc * W, W / 2 - sc * fx * W)); y = min(0, max(H - sc * H, H / 2 - sc * fy * H))
        y = max(y, by * (1 - sc) - (0 if X.portrait else 30))                                    # the board's top stays clear of the header
        y = min(y, (by + bh) * (1 - sc) + (40 if X.portrait else 30))       # and its bottom clear of the captions
        return x, y
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    mx = 1.06 if X.portrait else 1.12
    ks = []
    for k in sorted(keys):
        tk = min(max(float(k[0]), t), t + d - 1.2)
        k = (tk, min(mx, k[1])) + tuple(k[2:])
        if len(ks) > 1 and tk < ks[-1][0] + 0.45: ks[-1] = k        # too close: the later key (the overview) wins
        elif ks and tk < ks[-1][0] + 0.45: continue
        else: ks.append(k)
    keys = ks
    for k, (tk, sc, fx, fy) in enumerate(keys):
        x, y = xy(sc, fx, fy)
        nxt = keys[k + 1][0] if k + 1 < len(keys) else t + d
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});'); hold0 = tk
        else:
            mv = min(0.85 if k + 1 < len(keys) else 0.6, max(0.3, nxt - tk - 0.05))
            X.tw(f'tl.to("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"power3.inOut"}}, {tk:.3f});'); hold0 = tk + mv
        if nxt - hold0 > 0.25:
            x2, y2 = xy(sc * 1.018, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{sc * 1.018:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - hold0 - 0.01:.3f}, ease:"none"}}, {hold0:.3f});')


def sheet(X, cid, t, d, html):
    """a new sheet goes over the last one: pulled across, flipped down like a flip chart, or dropped on top —
    the scene starts 0.36 s early, above the previous page, so the old drawing is still there underneath."""
    i = X.beat["i"]
    if i == 0 or t < 0.4:
        X.clip(cid, t, d, html, "scene", 2); return
    a = 0.36; t0 = t - a
    X.clip(cid, t0, d + a, html, "scene", min(2 + i, 20), track=1 + i % 2)
    kind = ("slide", "flip", "drop")[i % 3]
    sel = f"#{cid} .sk"
    X.tw(f'tl.set("{sel}", {{boxShadow:"-30px 0 60px rgba(0,0,0,.22)"}}, {t0:.3f});')
    if kind == "slide":
        X.tw(f'tl.from("{sel}", {{xPercent:102, rotation:1.5, duration:{a:.2f}, ease:"power3.out"}}, {t0:.3f});')
    elif kind == "flip":
        X.tw(f'tl.from("{sel}", {{rotationX:-96, transformPerspective:2400, transformOrigin:"50% 0%", duration:{a + 0.06:.2f}, ease:"power2.out"}}, {t0:.3f});')
    else:
        X.tw(f'tl.from("{sel}", {{yPercent:-104, rotation:-2.5, duration:{a:.2f}, ease:"back.out(1.1)"}}, {t0:.3f});')
    X.tw(f'tl.to("{sel}", {{boxShadow:"0 0 0 rgba(0,0,0,0)", duration:0.3}}, {t:.3f});')
    X.sfx(t0, "transition")


def box(X):
    """content area (x, y, w, h) inside the furniture, per aspect."""
    return (70, 290, X.W - 140, 960) if X.portrait else (150, 150, X.W - 300, 760)


def fsz(text, w, mx, mn=30, lines=1, hand=False):
    em = text_em(text, "num" if hand else "")
    return int(max(mn, min(mx, w / max(em, 0.5))))


# ---------------------------------------------------------------- scenes
def _icon(h, icon, x, y, s):
    """a doodle that fits the box (x, y, s wide)."""
    f = {"cart": lambda: cart(h, x + 0.15 * s, y + 0.5 * s, s * 0.8), "card": lambda: card(h, x, y + s * 0.15, s, s * 0.63),
         "coin": lambda: coin(h, x + s / 2, y + s / 2, s * 0.4), "tag": lambda: tagd(h, x, y + s * 0.25, s, s * 0.45),
         "person": lambda: person(h, x + s / 2, y + s * 0.55, s * 0.9), "hat": lambda: tophat(h, x + s / 2, y + s * 0.8, s * 0.9)}.get(icon)
    return f() if f else []


def hook(b, X, t, d, cid):
    """a big handwritten figure with a doodle drawn beside it (cart / card / coin / tag / person / hat)."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    kick, num, unit, note = b.get("kicker", ""), str(b.get("value", "")), b.get("unit", ""), b.get("note", "")
    tn = T(X, b, "at_num", t, t + 1.0)
    if P:
        ix, iy, isz = bx + bw / 2 - 210, by + 70, 420
        cx_, ky, ny_, nw = bx + bw / 2, by + 0, by + 560, bw - 60
    else:
        ix, iy, isz = bx + 30, by + 60, 600
        cx_, ky, ny_, nw = bx + bw * 0.71, by + 70, by + 160, bw * 0.52
    for k in B.para(kick, cx_, ky - (0 if P or len(str(kick)) < 16 else 24), 46, nw, mn=28, anchor="middle", at=t + 0.1):
        d0, p0 = h.underline(k["left"], k["left"] + k["w"], k["base"] + 4, wave=3); B.mark(d0, p0, "red", 4, lag=-0.05)
    B.doodle(_icon(h, b.get("icon", "cart"), ix, iy, isz), speed=1.6)
    px = fsz(num, nw * 0.86, 240 if not P else 210, 90, hand=True)
    nt = B.text(num, cx_, ny_, px, cls="num", anchor="middle", at=tn - 0.3, dur=0.7)
    d1, p1 = h.underline(nt["left"] - 10, nt["left"] + nt["w"] + 10, ny_ + px * 1.02, wave=6); B.mark(d1, p1, "red", 7, lag=-0.15)
    ut = B.text(unit, cx_, ny_ + px * 1.16, min(76, int(px * 0.36)), anchor="middle")
    if note: B.text(note, cx_, ut["top"] + ut["px"] * 1.5, 34, anchor="middle", colour="muted", max_w=nw)
    html = page(X, b, B.build())
    X.sfx(t + 0.1, "title"); X.sfx(nt["op"]["t"], "write")
    sheet(X, cid, t, d, html)
    tw = nt["op"]["t"]
    shots(X, f"#{cid} .cam", t, d, [(t, 1.1, *((0.5, 0.25) if P else (0.3, 0.45))), (tw - 0.35, 1.08, *((0.5, 0.6) if P else (0.7, 0.4))), (tw + 1.0, 1.0, 0.5, 0.5)])


def bar(b, X, t, d, cid):
    """one long bar = 100; the thin slice that matters is filled in red, labelled above, pointed at and circled below."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    pct = max(2.0, min(60.0, float(b.get("pct", 10)))); title = b.get("title", ""); big = str(b.get("big", f"{pct:g}%"))
    labels = (list(b.get("labels") or []) + ["", ""])[:2]
    tp = T(X, b, "at_pct", t, t + 1.2)
    x0, w = (bx + 10, bw - 20) if P else (bx + 40, bw - 80)
    y0, hh = (by + 300, 150) if P else (by + 270, 170)
    tls = B.para(title, bx + bw / 2 if P else x0, by, 56, bw * 0.92, mn=30, anchor="middle" if P else "start", at=t + 0.1)
    if tls: y0 = max(y0, tls[-1]["top"] + tls[-1]["px"] * 1.2 + 120)
    dr, pr = h.rect(x0, y0, w, hh); B.mark(dr, pr, "ink", 6)
    sx = x0 + w * (1 - pct / 100)
    dl, pl = h.line(sx, y0 - 14, sx, y0 + hh + 14, over=2); B.mark(dl, pl, "ink", 6)
    dh, ph = h.hatch(x0 + 6, y0 + 6, sx - x0 - 12, hh - 12, gap=28); B.mark(dh, ph, "muted", 3, dur=0.5, op=0.55)
    B.text(labels[0], x0 + (sx - x0) / 2, y0 - 88, fsz(labels[0], sx - x0 - 40, 50, 30), anchor="middle")
    hl = B.hl(sx + 8, x0 + w - 8, y0 + hh / 2, hh - 22, at=tp - 0.35, colour="red")
    B.text(labels[1], sx + (x0 + w - sx) / 2, y0 - 88, fsz(labels[1], max(90, x0 + w - sx + 60), 50, 28), anchor="middle", colour="red", lag=-0.1)
    mid = sx + (x0 + w - sx) / 2
    if P:
        bx_, by_ = bx + bw * 0.42, y0 + hh + 220
        bg = B.text(big, bx_, by_, 150, cls="num", colour="red", anchor="middle", dur=0.5)
        da, pa = h.arrow(bg["left"] + bg["w"] + 40, by_ + 70, mid, y0 + hh + 18, curve=0.3)
    else:
        bx_, by_ = sx - 300, y0 + hh + 110
        bg = B.text(big, bx_, by_, 150, cls="num", colour="red", anchor="end", dur=0.5)
        da, pa = h.arrow(bx_ + 30, by_ + 90, mid, y0 + hh + 18, curve=0.32)
    B.mark(da, pa, "blue", 6)
    de, pe = h.ellipse(bg["left"] + bg["w"] / 2, bg["top"] + bg["px"] * 0.62, bg["w"] / 2 + 40, bg["px"] * 0.62, over=0.4); B.mark(de, pe, "red", 6)
    if b.get("note"):
        if P: B.para(b["note"], bx + bw / 2, by + bh - 110, 34, bw * 0.95, mn=28, anchor="middle", colour="muted")
        else: B.para(b["note"], x0, y0 + hh + 36, 34, max(360, bg["left"] - x0 - 60), mn=28, colour="muted")
    html = page(X, b, B.build())
    X.sfx(hl["t"], "brush"); X.sfx(bg["op"]["t"], "write")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.06, 0.4, 0.35), (hl["t"] - 0.3, 1.12, *((0.7, 0.45) if P else (0.78, 0.5))), (bg["op"]["t"] + 0.6, 1.0, 0.5, 0.5)])


def question(b, X, t, d, cid):
    """a figure, a big drawn question mark, arrows out to the candidate answers, each circled."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    head, cands = b.get("head", ""), (fit.as_list(b.get("options")) or ["?"])[:4]
    tq = T(X, b, "at_q", t, t + 1.4)
    for ht in B.para(head, bx + bw / 2, by - 10, 80, bw * 0.92, mn=34, anchor="middle", at=t + 0.1):
        B.hl(ht["left"] - 6, ht["left"] + ht["w"] + 6, ht["base"] - ht["px"] * 0.12, ht["px"] * 0.32, lag=-0.2)
    qx, qy, qs = (bx + bw / 2, by + 470, 250) if P else (bx + bw * 0.22, by + 470, 290)
    q = h.qmark(qx, qy, qs); qo = B.mark(*q, "red", 15, at=tq - 0.45, dur=0.6)
    n = len(cands)
    for k, c in enumerate(cands):
        if P:
            per = n if n <= 3 else 2                     # four answers: two rows of two
            r_, c_ = divmod(k, per)
            cx, cy = bx + bw * (c_ + 0.5) / per, by + 800 + r_ * 150
            sx, sy, ex, ey = qx + (k - (n - 1) / 2) * 50, qy + qs * 0.75, cx + (c_ - (per - 1) / 2) * -60, cy - 30
        else:
            cx, cy = bx + bw * 0.62, by + 420 + (k - (n - 1) / 2) * (min(400, 480 / max(n - 1, 1)) if n > 1 else 0)
            sx, sy, ex, ey = qx + qs * 0.6, qy - qs * 0.35 + k * 40, cx - 50, cy + 40
        da, pa = h.arrow(sx, sy, ex, ey, curve=0.2); B.mark(da, pa, "blue", 5)
        ct = B.text(c, cx, cy, fsz(c, bw / (n if n <= 3 else 2) - 90, 64, 30) if P else fsz(c, bw * 0.34, 72, 34), anchor="middle" if P else "start")
        de, pe = h.ellipse(ct["left"] + ct["w"] / 2, ct["top"] + ct["px"] * 0.6, ct["w"] / 2 + 40, ct["px"] * 0.8, over=0.25); B.mark(de, pe, "ink", 4)
    html = page(X, b, B.build())
    X.sfx(qo["t"], "brush")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.08, 0.5, 0.22), (qo["t"] - 0.2, 1.1, *((0.5, 0.45) if P else (0.25, 0.55))), (qo["t"] + 0.9, 1.0, 0.5, 0.5)])


def ratio(b, X, t, d, cid):
    """two quantities as two drawn bars: the whole (outlined, hatched) and the one that matters (highlighted), a red guide
    where the shorter one stops, the share written and circled. For "X is about 2/3 of Y" — a comparison, not a breakdown."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    total, part = float(b.get("total", 100)), float(b.get("part", 50))
    tl_, pl_ = b.get("total_label", ""), b.get("part_label", "")
    frac = max(0.06, min(1.0, part / total))
    tpart, tfrac = T(X, b, "at_part", t, t + 1.0), T(X, b, "at_frac", t, t + 2.2)
    x0, w = (bx + 10, bw - 20) if P else (bx + 40, bw * 0.68)
    hh = 130 if P else 140
    y1, y2 = (by + 110, by + 400) if P else (by + 100, by + 380)
    xs = x0 + w * frac
    # drawn in the order it is said: the part first (highlighted on its number), then the whole, then the guide
    if x0 + w - xs - 40 >= text_em(pl_) * 40:
        B.text(pl_, xs + 30, y2 + hh / 2 - 30, fsz(pl_, x0 + w - xs - 40, 52, 30), at=t + 0.1)
    else:
        B.text(pl_, x0, y2 - 76, fsz(pl_, max(xs - x0 - 30, w * 0.5), 52, 30), at=t + 0.1)
    d2, p2 = h.rect(x0, y2, xs - x0, hh); B.mark(d2, p2, "ink", 6)
    hl = B.hl(x0 + 8, xs - 8, y2 + hh / 2, hh - 22, dur=0.45, at=tpart - 0.15)
    ttot = T(X, b, "at_total", t, None)
    B.text(tl_, x0, y1 - 76, fsz(tl_, w, 52, 30), at=(ttot - 0.2) if ttot is not None else None)
    dr, pr = h.rect(x0, y1, w, hh); B.mark(dr, pr, "ink", 6)
    dh, ph = h.hatch(x0 + 6, y1 + 6, w - 12, hh - 12, gap=26); B.mark(dh, ph, "muted", 3, op=0.5, dur=0.45)
    dg, pg = h.line(xs, y1 - 26, xs, y2 + hh + 26, over=2); B.mark(dg, pg, "red", 4)
    if P: ix, iy, isz = bx + bw - 320, y2 + hh + 90, 300
    else: ix, iy, isz = bx + bw * 0.75, y1 + 30, bw * 0.24
    B.doodle(_icon(h, b.get("icon", "card"), ix, iy, isz), speed=2.2)
    fl = b.get("frac_label", f"{frac * 100:.1f}%")
    if P: fx_, fy_, anc = bx + bw * 0.36, y2 + hh + 70, "middle"
    else: fx_, fy_, anc = min(xs + 40, x0 + w - 200), y2 + hh + 50, "start"
    ft_ = B.text(fl, fx_, fy_, 120 if not P else 110, cls="num", colour="red", anchor=anc, at=tfrac - 0.3, dur=0.5)
    de, pe = h.ellipse(ft_["left"] + ft_["w"] / 2, ft_["top"] + ft_["px"] * 0.6, ft_["w"] / 2 + 40, ft_["px"] * 0.68, over=0.4); B.mark(de, pe, "red", 6)
    if b.get("frac_note"):
        B.text(b["frac_note"], ft_["left"] + ft_["w"] / 2, ft_["top"] + ft_["px"] * 1.34, 48, anchor="middle")
    html = page(X, b, B.build())
    X.sfx(hl["t"], "brush"); X.sfx(ft_["op"]["t"], "pop")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.06, 0.4, 0.25), (hl["t"] - 0.3, 1.1, *((0.4, 0.45) if P else (0.35, 0.55))), (ft_["op"]["t"] - 0.1, 1.0, 0.5, 0.5)])


def tag(b, X, t, d, cid):
    """a price tag tied to a doodled card: the old price is scribbled out in red, the new one written above it."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    old, new, date, sub = str(b.get("old", "")), str(b.get("new", "")), b.get("date", ""), b.get("sub", "")
    to = T(X, b, "at_new", t, t + 1.6)
    if P:
        cx, cy, cw, ch = bx + bw / 2 - 270, by + 40, 540, 330
        tx_, ty_, tw_, th_ = bx + bw / 2 - 250, by + 560, 500, 220
    else:
        cx, cy, cw, ch = bx + 40, by + 150, 640, 390
        tx_, ty_, tw_, th_ = bx + bw * 0.53, by + 250, 600, 260
    B.doodle(card(h, cx, cy, cw, ch), speed=2.2)
    B.text(b.get("card_text", "MEMBER"), cx + cw * 0.32, cy + ch * 0.42, int(ch * 0.15), cls="lat")
    if P: da, pa = h.arrow(cx + cw * 0.16, cy + ch + 16, tx_ + th_ * 0.18, ty_ + th_ * 0.3, curve=0.3)
    else: da, pa = h.arrow(cx + cw + 16, cy + ch * 0.35, tx_ - 16, ty_ + th_ * 0.45, curve=0.3)
    B.mark(da, pa, "ink", 4)
    B.doodle(tagd(h, tx_, ty_, tw_, th_), speed=2.2)
    o = B.text(old, tx_ + th_ * 0.62, ty_ + th_ * 0.16, int(th_ * 0.56), cls="num")
    if date: B.text(date, tx_ + tw_ / 2, ty_ + th_ + 20, 42, anchor="middle", colour="blue")
    B.para(sub, bx + bw / 2, by + bh - (60 if P else 80), 38, bw * 0.92, mn=28, anchor="middle", colour="muted")
    dk, pk = h.strike(o["left"], o["left"] + o["w"], o["top"] + o["px"] * 0.62, h=o["px"] * 0.5); sk = B.mark(dk, pk, "red", 10, at=to - 0.55, dur=0.3)
    n = B.text(new, o["left"] + o["w"] * 0.55, ty_ - th_ * 0.62, int(th_ * 0.7), cls="num", colour="red", rot=-5, dur=0.45)
    d2, p2 = h.underline(n["left"], n["left"] + n["w"], n["base"] + 2, wave=5); B.mark(d2, p2, "red", 6)
    html = page(X, b, B.build())
    X.sfx(sk["t"], "hit"); X.sfx(n["op"]["t"], "write")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.08, *((0.5, 0.22) if P else (0.27, 0.45))), (sk["t"] - 0.3, 1.1, *((0.5, 0.55) if P else (0.68, 0.42))), (n["op"]["t"] + 0.8, 1.0, 0.5, 0.5)])


def dots(b, X, t, d, cid):
    """a 10×10 crowd of circles drawn row by row; the share that matters gets filled in, the figure is written and circled."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    pct = max(0.0, min(100.0, float(b.get("pct", 50)))); n_on = int(round(pct))
    big = str(b.get("big", f"{pct:g}%")); label = b.get("label", "")
    tp = T(X, b, "at_pct", t, t + 1.6)
    cols = 10
    if P: cell = 62; gx, gy = bx + bw / 2 - 5 * cell, by + 20; nx_, ny_ = bx + bw / 2, by + 20 + 10 * cell + 30
    else: cell = 68; gx, gy = bx + 30, by + 20; nx_, ny_ = bx + bw * 0.73, by + 190
    rings, pts_rows, fill_c = [], [], []
    for i in range(100):
        r_, c_ = divmod(i, cols)
        cx, cy = gx + c_ * cell + cell / 2 + h.j(2), gy + r_ * cell + cell / 2 + h.j(2)
        dd, pp = h.ellipse(cx, cy, cell * 0.3, cell * 0.3, n=10, over=0.25)
        rings.append((dd, pp))
        if i < n_on: fill_c.append((cx, cy))
    for row in range(10):
        seg = rings[row * cols:(row + 1) * cols]
        p = [q for _, ps in (seg if row % 2 == 0 else seg[::-1]) for q in ps[:1]]
        B.mark(" ".join(dd for dd, _ in seg), p, "ink", 3, dur=0.12, lag=0.0, at=t + 0.12 if row == 0 else None)
    fid = f"{cid}fd"
    dots_html = "".join(f'<circle class="solid {fid}" cx="{x:.0f}" cy="{y:.0f}" r="{cell * 0.22:.0f}" style="fill:var(--blue)"/>' for x, y in fill_c)
    each = max(0.004, min(0.012, 0.8 / max(n_on, 1)))
    npx = 160 if not P else 140
    B.para(label, nx_, ny_ + npx * 1.38, 46, bw * (0.92 if P else 0.42), mn=28, anchor="middle")
    fill = B.custom(0.25 + each * n_on, lambda t0, du: X.tw(f'tl.from(".{fid}", {{scale:0, transformOrigin:"50% 50%", duration:0.22, ease:"back.out(2.5)", stagger:{{each:{each * du / (0.25 + each * n_on):.4f}}}}}, {t0:.3f});'),
                    at=tp - 0.95) if fill_c else None
    nt = B.text(big, nx_, ny_, npx, cls="num", colour="red", anchor="middle", at=tp - 0.3, dur=0.5)
    de, pe = h.ellipse(nx_, nt["top"] + nt["px"] * 0.62, nt["w"] / 2 + 40, nt["px"] * 0.66, over=0.4); B.mark(de, pe, "red", 7)
    if b.get("note"): B.text(b["note"], gx, gy + 10 * cell + 6, 28, colour="muted") if not P else None
    html = page(X, b, B.build(extra_under=dots_html))
    if fill: X.sfx(fill["t"], "pop")
    X.sfx(nt["op"]["t"], "write")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.1, *((0.5, 0.3) if P else (0.3, 0.45))), (nt["op"]["t"] - 0.3, 1.06, *((0.5, 0.62) if P else (0.72, 0.42))), (nt["op"]["t"] + 0.8, 1.0, 0.5, 0.5)])


def loop(b, X, t, d, cid):
    """3–6 stations on a hand-drawn loop of arrows; once it is closed, a red dot runs the lap."""
    B = Board(X, cid, t, d, tail=1.0); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    st = (fit.as_list(b.get("stations")) or ["A", "B", "C"])[:6]
    n = max(3, len(st))
    title = b.get("title", "")
    B.para(title, bx + bw / 2, by + (0 if P else -10), 64, bw * 0.9, mn=34, anchor="middle", at=t + 0.1)
    cx, cy = (bx + bw / 2, by + 560) if P else (bx + bw / 2, by + 450)
    rx, ry = (300, 330) if P else (600, 270)
    lw = (300 if P else 380) if n <= 4 else (240 if P else 300)
    pos = [(cx + rx * math.cos(-math.pi / 2 + 2 * math.pi * k / n), cy + ry * math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(n)]
    labels = []
    for k, (x, y) in enumerate(pos):
        lt = B.text(st[k], x, y - 34, fsz(st[k], lw, 54, 28), anchor="middle")
        labels.append(lt)
        a0 = -math.pi / 2 + 2 * math.pi * k / n; a1 = -math.pi / 2 + 2 * math.pi * (k + 1) / n
        off = math.pi / n * 0.55
        s = (cx + rx * math.cos(a0 + off), cy + ry * math.sin(a0 + off)); e = (cx + rx * math.cos(a1 - off), cy + ry * math.sin(a1 - off))
        da, pa = h.arrow(s[0], s[1], e[0], e[1], curve=0.2); B.mark(da, pa, "blue", 6)
    for k in fit.as_list(b.get("hl")) or []:
        try: k = int(k)
        except (TypeError, ValueError): continue
        if 0 <= k < len(labels):
            lt = labels[k]; B.hl(lt["left"] - 8, lt["left"] + lt["w"] + 8, lt["top"] + lt["px"] * 0.66, lt["px"] * 0.62)
    if b.get("center"):
        ct = B.text(b["center"], cx, cy - 46, fsz(b["center"], rx * 0.9, 80, 34), anchor="middle", colour="red")
        de, pe = h.ellipse(cx, ct["top"] + ct["px"] * 0.6, ct["w"] / 2 + 36, ct["px"] * 0.85, over=0.35); B.mark(de, pe, "red", 5)
    dot = '<g class="lapdot" style="opacity:0"><circle class="solid" cx="0" cy="0" r="15" style="fill:var(--red)"/></g>'
    html = page(X, b, B.build(extra_over=dot))
    lap0 = B.end + 0.05
    if lap0 < t + d - 0.6:
        lap = min(2.2, max(0.6, t + d - lap0 - 0.3)); m = 32
        X.tw(f'tl.set("#{cid} .lapdot", {{x:{cx:.0f}, y:{cy - ry:.0f}}}, {t:.3f});')
        X.tw(f'tl.to("#{cid} .lapdot", {{opacity:1, duration:0.15}}, {lap0:.3f});')
        for k in range(1, m + 1):
            a = -math.pi / 2 + 2 * math.pi * k / m
            X.tw(f'tl.to("#{cid} .lapdot", {{x:{cx + rx * math.cos(a):.0f}, y:{cy + ry * math.sin(a):.0f}, duration:{lap / m:.3f}, ease:"none"}}, {lap0 + lap * (k - 1) / m:.3f});')
        X.tw(f'tl.to("#{cid} .lapdot", {{opacity:0, duration:0.2}}, {lap0 + lap:.3f});')
    X.sfx(t + 0.2, "brush")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.08, 0.5, 0.3), (t + 0.9, 1.04, 0.55, 0.55), (B.end, 1.0, 0.5, 0.5)])


def thesis(b, X, t, d, cid):
    """the judgment written out by hand: one word struck out in red, the other highlighted and circled."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    pre, no, yes = b.get("pre", ""), b.get("no", ""), b.get("yes", "")
    neg, pos_ = b.get("neg", "不是"), b.get("pos", "是")
    tn, ty = T(X, b, "at_no", t, t + 1.2), T(X, b, "at_yes", t, t + 2.2)
    if P: x0, y1, y2, y3, big = bx + 30, by + 60, by + 250, by + 500, 130
    else: x0, y1, y2, y3, big = bx + 70, by + 40, by + 200, by + 430, 150
    B.para(pre, x0, y1 - (30 if len(str(pre)) > 14 else 0), 66, bw * 0.9, mn=32, at=t + 0.1, colour="muted")
    a = B.text(neg, x0, y2 + big * 0.12, int(big * 0.62))
    nw_ = bw - (a["w"] + 60) - (150 if P else 420)
    nn = B.text(no, a["left"] + a["w"] + 30, y2, fsz(no, nw_, int(big * 0.9), 40), at=tn - 0.45)
    dk, pk = h.strike(nn["left"], nn["left"] + nn["w"], nn["top"] + nn["px"] * 0.6, h=nn["px"] * 0.4); sk = B.mark(dk, pk, "red", 12, dur=0.3, lag=0.08)
    c = B.text(pos_, x0, y3 + big * 0.12, int(big * 0.62))
    ypx = fsz(yes, nw_, big, 40)
    yl = c["left"] + c["w"] + 30
    hl = B.hl(yl - 10, yl + text_em(yes) * ypx + 10, y3 + ypx * 0.7, ypx * 0.55, at=ty - 0.4)
    yy = B.text(yes, yl, y3, ypx, lag=-0.15)
    de, pe = h.ellipse(yy["left"] + yy["w"] / 2, yy["top"] + yy["px"] * 0.62, yy["w"] / 2 + 46, yy["px"] * 0.72, over=0.4); B.mark(de, pe, "red", 8)
    for k in range(3):
        sx = min(yy["left"] + yy["w"] + 70, X.W - 80); sy = yy["top"] + yy["px"] * (0.1 + 0.4 * k)
        dd, pp = h.line(sx, sy, sx + 42, sy + (-22, 0, 22)[k], over=1); B.mark(dd, pp, "ink", 5, dur=0.08, lag=0.0)
    html = page(X, b, B.build())
    X.sfx(sk["t"], "hit"); X.sfx(hl["t"], "brush")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.06, 0.4, 0.25), (nn["op"]["t"] - 0.2, 1.08, 0.4, 0.42), (hl["t"] - 0.2, 1.06, 0.45, 0.6), (hl["t"] + 1.0, 1.0, 0.5, 0.5)])


def outro(b, X, t, d, cid):
    """a sticky note taped to the board; the top hat is drawn above the channel name."""
    B = Board(X, cid, t, d); h = B.h
    bx, by, bw, bh = box(X); P = X.portrait
    title, sub = b.get("title", "第九顶帽子"), b.get("sub", "")
    nw, nh = (620, 580) if P else (740, 580)
    nx_, ny_ = (bx + bw / 2 - nw / 2, by + 60) if P else (bx + bw * 0.38 - nw / 2, by + 70)
    note = (f'<div class="note sn" style="left:{nx_:.0f}px; top:{ny_:.0f}px; width:{nw}px; height:{nh}px; transform:rotate(-2.5deg)"></div>'
            f'<div class="tape tp" style="left:{nx_ + nw / 2 - 90:.0f}px; top:{ny_ - 22:.0f}px; width:180px; height:46px; transform:rotate(3deg)"></div>')
    X.tw(f'tl.from("#{cid} .sn", {{y:-70, rotation:-9, opacity:0, duration:0.45, ease:"back.out(1.6)"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("#{cid} .tp", {{scaleX:0, opacity:0, duration:0.22, ease:"power2.out"}}, {t + 0.38:.3f});')
    B.doodle(tophat(h, nx_ + nw / 2, ny_ + 240, 240), at=t + 0.55, speed=1.6)
    tt = B.text(title, nx_ + nw / 2, ny_ + 300, fsz(title, nw * 0.86, 96, 44), anchor="middle")
    d1, p1 = h.underline(tt["left"], tt["left"] + tt["w"], tt["base"] + 10, wave=4); B.mark(d1, p1, "red", 6, lag=-0.1)
    B.para(sub, nx_ + nw / 2, ny_ + 420, 42, nw * 0.86, mn=28, anchor="middle", colour="muted")
    html = page(X, b, B.build(extra_html=note))
    X.sfx(t + 0.1, "title"); X.sfx(t + 0.38, "tape")
    sheet(X, cid, t, d, html)
    shots(X, f"#{cid} .cam", t, d, [(t, 1.06, 0.45, 0.35), (t + d * 0.45, 1.0, 0.5, 0.5)])


SCENES = {"hook": hook, "bar": bar, "question": question, "ratio": ratio, "tag": tag, "dots": dots, "loop": loop, "thesis": thesis, "outro": outro}
