"""bauhaus · 包豪斯构成 —— 1923 年魏玛包豪斯展一路的抽象构成：Herbert Bayer 的通用字母、Joost Schmidt 的展览海报、
Moholy-Nagy 的构成与字体摄影、Schlemmer《三元芭蕾》的机械动作、Kandinsky 的点线面练习。没有插画、没有人、没有建筑和物件，
画面里只有圆、方、三角、粗条、四分之一圆弧和细线。

材料：整页纯色满版，每一两页换一次底——信号红 #d7261e、钴蓝 #1c3faa、铬黄 #f5c400、墨黑 #111111、本白 #e4e2da（全片最多 3 页）。
平涂，只有一层极细的胶印颗粒，没有渐变、阴影和暗角。形状只用这五色，叠在一起的地方涂成第三种颜色（不用透明度）。
红底上：大字（≥130 px）用本白（3.9:1，大字够用），小字一律放在黑色色条上（本白对红只有 3.9:1，不到 4.5:1）。

字：拉丁字母和数字小写、几何无衬线（库里最几何的 Space Grotesk，只用 300 和 700）；中文是站酷酷黑。
大数字是**搭出来的**：digit() 用同一套模块（圆、半圆、四分之一圆弧、直条，笔画 = 0.22 × 字高）拼出 0–9、% 和小数点（一个方块），
高 460–640 px；数字出场时弧线一笔扫出、直条从画面边上滑进来；换数值时旧模块向外甩出、新模块再进来，不是字体滚动。
标题 130–180 px，压在一根 24 px 粗条上；位置在上方带（y 220–520）和左下（y 900–1280）之间逐页交替，每页最多一个旋转元素。

构图（9:16，6×10 模块网格，180×192）：每页一个占画宽 ≥60% 的主形、对角一个 1/3 大小的副形、一根 24 px 粗条和一根 4 px 细线
（0° / 90° / 45°）横穿画面；形状出血、压进底部 400 px。页眉在 y 204：28 px 方块 + 小写题签；出处 24 px 细体在 y 1450–1500。
字幕是一根实心色条：从左边出血到 x 900、高 96、42 px 酷黑，右端 45° 切角，在 y 1300–1396；底色浅（本白、黄）时是黑条白字，
底色深（红、蓝、黑）时是本白条黑字（每页开头用 CSS 变量切换）。

图表就是构成本身：占比 = 主圆上按真实角度切出一块；对比 = 共用一个角的两个正方形，面积成真实比例；增长 = 共用底线的柱子台阶，
一个球按真实高度一级一级跳过去；排行 = 同心圆环，环宽正比于数值，横细线引出标注；构成 = 一个正方形按真实面积切成几块。

动作（Schlemmer：机械、旋转、分级）：形状像舞台机械，绕偏心支点按 45° / 90° 一步一步转（每步 10 帧，三次方缓入缓出，停 2 帧），
沿网格轴滑动，从不漂；圆滚动（转角和位移对得上），方块绕一个角翻转。
换页：下一页的底色以一个长大的形状进场（从角上长出的圆、绕角翻过来的大方块、45° 斜条擦过），13 帧；
上一页的主形缩成新一页的副形（能接上时）。

场景（SCENES，全部自写，横竖屏各自排版）：hero 搭出来的大数字 · stairs 柱子台阶 + 跳球 · slice 主圆切一块 ·
quote 引语 + 63 格 · rings 同心圆环排行 · squares 两个正方形面积对比 · blocks 正方形切块（构成） · chain 三角形因果链。
每页底色写在 beat 的 "ground"：red | cobalt | yellow | black | white。
"""
import math

RED, COB, YEL, BLK, GW = "#d7261e", "#1c3faa", "#f5c400", "#111111", "#e4e2da"
GROUNDS = {      # ground colour, its legal text colour, caption bar colour, caption text colour
    "red":    {"bg": RED, "tx": GW, "cap": GW, "capfg": BLK, "small": "band"},
    "cobalt": {"bg": COB, "tx": GW, "cap": GW, "capfg": BLK},
    "yellow": {"bg": YEL, "tx": BLK, "cap": BLK, "capfg": GW},
    "black":  {"bg": BLK, "tx": GW, "cap": GW, "capfg": BLK},
    "white":  {"bg": GW, "tx": BLK, "cap": BLK, "capfg": GW},
}
F = 1 / 30           # one frame
STEP = 10 * F        # one mechanical step
HOLD = 2 * F
TR = 13 * F          # page change

STYLE = {
    "name": "包豪斯构成", "en": "Bauhaus", "benchmarks": ["Herbert Bayer 通用字母（1923–25）", "Joost Schmidt 1923 包豪斯展海报",
                                                     "Moholy-Nagy 构成", "Schlemmer《三元芭蕾》", "Kandinsky《点线面》"],
    "tokens": {
        "bg": COB, "fg": GW, "muted": GW, "accent": YEL, "accent2": RED, "alert": RED,
        "line": BLK, "paper": GW, "ink": BLK, "card": GW, "card-fg": BLK,
        "red": RED, "cobalt": COB, "yellow": YEL, "black": BLK, "white": GW,
        "cap-bg": GW, "cap-fg": BLK, "cap-size": "42px", "cap-weight": "900", "cap-pad": "0", "cap-radius": "0",
        "cap-shadow": "none", "cap-em": BLK, "cap-bottom": "84px",
        "punch-top": "68%", "punch-size": "72px",
    },
    # one geometric sans for Latin and numerals (300 / 700 only), one square heavy 黑体 for every Chinese headline and the caption,
    # a light 黑体 for Chinese inside lowercase labels
    "fonts": {"display": ["space-grotesk", "zcool-kuhei"], "zh": ["zcool-kuhei", "noto-sans-sc"], "body": ["space-grotesk", "noto-sans-sc"],
              "cap": ["space-grotesk", "zcool-kuhei"], "num": ["space-grotesk", "zcool-kuhei"], "latin": "space-grotesk",
              "mono": ["space-grotesk", "noto-sans-sc"]},
    "motion": {"ease": "power2.inOut", "dur": STEP, "stagger": 2 * F, "cut": "hard", "transition": "hard", "em": "static", "camera": "none"},
    "layers": [],          # the grain lives in the page itself (flat ink, no vignette)
    "mascot": {"mode": "none"},
    "caption_plate": False,
    "safe_exempt": [".bh-hd"],
    "sfx": {"enter": None, "hit": None, "pop": None, "slam": None, "count": None, "click": None, "mascot": None, "transition": None,
            "cut": None, "line": None, "tick": None, "draw": None, "paper": None, "whoosh": None, "title": None},
}

GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'>"
         "<filter id='g'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='7' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.6 -.55'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23g)'/></svg>")

CSS = r"""
.bh { position:absolute; inset:0; overflow:hidden; background:var(--g); color:var(--tx); }
.bh .grn { position:absolute; inset:0; background-image:url("__GRAIN__"); background-size:300px; opacity:.05; pointer-events:none; z-index:20; }
.bh svg.cs { position:absolute; left:0; top:0; overflow:visible; }
.bh .t { position:absolute; white-space:nowrap; line-height:1; }
.bh .hl { font-family:var(--f-display); font-weight:700; letter-spacing:.05em; line-height:1; }
.bh .hl .c { display:inline-block; font-style:normal; }
.bh .lb { font-family:var(--f-body); font-weight:300; font-size:28px; letter-spacing:.06em; text-transform:lowercase; line-height:1.15; }
.bh .vl { font-family:var(--f-display); font-weight:700; line-height:1; letter-spacing:-.01em; }
.bh .msk { position:absolute; overflow:hidden; }
.bh-hd { position:absolute; display:flex; align-items:center; gap:16px; z-index:25; font-family:var(--f-body); font-weight:300; font-size:26px;
  letter-spacing:.06em; text-transform:lowercase; line-height:28px; white-space:nowrap; }
.bh-hd i { display:block; width:28px; height:28px; background:currentColor; }
.bh-hd.band { background:#111111; color:#e4e2da; padding:6px 22px 6px 0; }
.bh-src { position:absolute; z-index:25; font-family:var(--f-body); font-weight:300; font-size:24px; letter-spacing:.02em; line-height:40px; height:40px;
  white-space:nowrap; background:var(--g); color:var(--tx); padding-right:24px; }
.bh-src.band { background:#111111; color:#e4e2da; }
.bhk { position:absolute; }
"""

CAP_CSS = r"""
#root.st-bauhaus { --bhcb:#e4e2da; --bhcf:#111111; }
#root.st-bauhaus .clip.cap { top:auto; bottom:84px; left:0; right:auto; width:900px; height:96px; padding:0; text-align:left; }
#root.v.st-bauhaus .clip.cap { top:1300px; bottom:auto; left:0; padding:0; }
.st-bauhaus .cap .cp { display:flex; align-items:center; width:900px; height:96px; padding:0 110px 0 72px; background:var(--bhcb); color:var(--bhcf);
  font-family:var(--f-cap); font-weight:700; font-size:42px; letter-spacing:.02em; line-height:1; text-shadow:none; border-radius:0; white-space:nowrap;
  clip-path:polygon(0 0, 900px 0, 804px 96px, 0 96px); }
.st-bauhaus .cap .em .emt { color:inherit; }
.st-bauhaus .mascot { display:none !important; }
"""


# ---------------------------------------------------------------- the constructed numerals
S_ = 0.22                       # stroke = 0.22 × height
R_ = (1 - S_) / 4               # bowl radius (centre line): two stacked bowls fill the height
W_ = 2 * R_ + S_                # digit width 0.61
L_, RR_, T_, B_ = S_ / 2, W_ - S_ / 2, S_ / 2, 1 - S_ / 2
CX_, C1_, C2_, M_ = W_ / 2, S_ / 2 + R_, 1 - S_ / 2 - R_, 0.5
GAP = 0.12


def digit(ch):
    """the modules of one glyph in a 1-unit-high box: [(kind, ...)], advance.
    kinds: ("arc", cx, cy, r, a0, a1) a stroked arc (degrees, clockwise, 0 = 3 o'clock) · ("bar", x1, y1, x2, y2) a stroked bar ·
    ("dot", cx, cy, r) a disc · ("sq", x, y, side) a square."""
    a, b = (CX_, C1_), (CX_, C2_)
    if ch == "0":
        return [("arc", *a, R_, 180, 360), ("bar", L_, C1_, L_, C2_), ("bar", RR_, C1_, RR_, C2_), ("arc", *b, R_, 0, 180)], W_
    if ch == "1":
        x = 0.30
        return [("bar", x, 0, x, 1), ("bar", 0.02, 0.30, x - 0.02, 0.06)], 0.42
    if ch == "2":
        e = (CX_ + R_ * math.cos(math.radians(40)), C1_ + R_ * math.sin(math.radians(40)))
        return [("arc", *a, R_, 180, 400), ("bar", e[0], e[1], L_ + 0.02, B_ - 0.02), ("bar", 0, B_, W_, B_)], W_
    if ch == "3":
        return [("arc", *a, R_, 180, 450), ("arc", *b, R_, 270, 540)], W_
    if ch == "4":
        vx = 0.42
        return [("bar", vx - 0.03, 0.05, L_, 0.68), ("bar", 0, 0.68, W_, 0.68), ("bar", vx, 0, vx, 1)], W_
    if ch == "5":
        return [("bar", 0, T_, W_, T_), ("bar", L_, 0, L_, M_ + S_ / 2), ("bar", L_ - S_ / 2, M_, CX_, M_), ("arc", *b, R_, 270, 500)], W_
    if ch == "6":
        return [("arc", *b, R_, 0, 360), ("bar", L_, C2_, L_, C1_), ("arc", *a, R_, 180, 300)], W_
    if ch == "7":
        return [("bar", 0, T_, W_, T_), ("bar", RR_, 0.02, 0.16, 1)], W_
    if ch == "8":
        return [("arc", *a, R_, 0, 360), ("arc", *b, R_, 0, 360)], W_
    if ch == "9":
        return [("arc", *a, R_, 0, 360), ("bar", RR_, C1_, RR_, C2_), ("arc", *b, R_, 0, 120)], W_
    if ch == "%":
        return [("dot", 0.15, 0.18, 0.15), ("bar", 0.60, 0.0, 0.02, 1.0), ("dot", 0.47, 0.82, 0.15)], 0.62
    if ch in ".,":
        return [("sq", 0, 1 - S_, S_)], S_
    if ch in "-−":
        return [("bar", 0, M_, 0.40, M_)], 0.40
    if ch == "+":
        return [("bar", 0, M_, 0.44, M_), ("bar", 0.22, M_ - 0.22, 0.22, M_ + 0.22)], 0.44
    return [], 0.3


def numeral_width(text, h, gap=GAP):
    w = 0.0
    for k, ch in enumerate(str(text)):
        w += digit(ch)[1] + (gap if k else 0)
    return w * h


def _arc_d(cx, cy, r, a0, a1):
    def p(a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    if a1 - a0 >= 359.9:       # a whole circle: two half arcs
        x0, y0 = p(a0); x1, y1 = p(a0 + 180)
        return f"M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 0 1 {x1:.1f} {y1:.1f}A{r:.1f} {r:.1f} 0 0 1 {x0:.1f} {y0:.1f}"
    x0, y0 = p(a0); x1, y1 = p(a1)
    big = 1 if a1 - a0 > 180 else 0
    return f"M{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 {big} 1 {x1:.1f} {y1:.1f}"


def numeral(text, h, x, y, color, cls, W=1080, H=1920, gap=GAP):
    """SVG group of a constructed numeral (top-left at x, y, h tall). Every module carries data-k (its order) and, for bars,
    data-dx / data-dy: the slide that brings it in from the nearest frame edge along its own axis. data-ox / data-oy throw it out."""
    s = S_ * h
    out, ox, k = [], 0.0, 0
    tw = numeral_width(text, h, gap)
    ncx, ncy = x + tw / 2, y + h / 2
    for i, ch in enumerate(str(text)):
        mods, adv = digit(ch)
        for m in mods:
            kind = m[0]
            if kind == "arc":
                _, cx, cy, r, a0, a1 = m
                d = _arc_d(ox + cx * h, cy * h, r * h, a0, a1)
                mx, my = x + ox + cx * h, y + cy * h
                el = f'<path class="md ma" d="{d}" fill="none" stroke="{color}" stroke-width="{s:.1f}" pathLength="1" stroke-dasharray="1 1"'
            elif kind == "bar":
                _, x1, y1, x2, y2 = m
                X1, Y1, X2, Y2 = ox + x1 * h, y1 * h, ox + x2 * h, y2 * h
                ln = math.hypot(X2 - X1, Y2 - Y1) or 1
                ex, ey = (X2 - X1) / ln * 1.5, (Y2 - Y1) / ln * 1.5
                X1, Y1, X2, Y2 = X1 - ex, Y1 - ey, X2 + ex, Y2 + ey
                mx, my = x + (X1 + X2) / 2, y + (Y1 + Y2) / 2
                if abs(Y1 - Y2) < 1:            # horizontal: slides in from the left edge
                    dx, dy = -(x + max(X1, X2) + 40), 0
                elif abs(X1 - X2) < 1:          # vertical: rises from the bottom edge
                    dx, dy = 0, H - (y + min(Y1, Y2)) + 40
                else:                           # diagonal: drops from the top edge
                    dx, dy = 0, -(y + max(Y1, Y2) + 40)
                el = (f'<path class="md mb" d="M{X1:.1f} {Y1:.1f}L{X2:.1f} {Y2:.1f}" stroke="{color}" stroke-width="{s:.1f}" fill="none" '
                      f'data-dx="{dx:.0f}" data-dy="{dy:.0f}"')
            elif kind == "dot":
                _, cx, cy, r = m
                mx, my = x + ox + cx * h, y + cy * h
                el = f'<circle class="md mf" cx="{ox + cx * h:.1f}" cy="{cy * h:.1f}" r="{r * h:.1f}" fill="{color}"'
            else:
                _, sx, sy, sd = m
                mx, my = x + ox + (sx + sd / 2) * h, y + (sy + sd / 2) * h
                el = f'<rect class="md mf" x="{ox + sx * h:.1f}" y="{sy * h:.1f}" width="{sd * h:.1f}" height="{sd * h:.1f}" fill="{color}"'
            vx, vy = mx - ncx, my - ncy
            n = math.hypot(vx, vy) or 1
            out.append(el + f' data-k="{k}" data-ox="{vx / n * 1500:.0f}" data-oy="{vy / n * 1500:.0f}"/>')
            k += 1
        ox += (adv + gap) * h
    return f'<g class="{cls}" transform="translate({x:.1f} {y:.1f})">{"".join(out)}</g>'


def assemble(X, sel, t):
    """arcs sweep in (10-frame stroke draw), bars slide in from the frame edge, discs / squares snap open; 2-frame stagger."""
    X.tw(f'tl.fromTo("{sel} .ma", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{STEP:.3f}, ease:"power2.inOut", '
         f'delay:(i,el)=>+el.dataset.k*{2 * F:.4f}}}, {t:.3f});')
    X.tw(f'tl.from("{sel} .mb", {{x:(i,el)=>+el.dataset.dx, y:(i,el)=>+el.dataset.dy, duration:{STEP * 1.3:.3f}, ease:"power3.out", '
         f'delay:(i,el)=>+el.dataset.k*{2 * F:.4f}}}, {t:.3f});')
    X.tw(f'tl.from("{sel} .mf", {{scale:0, transformOrigin:"50% 50%", duration:{STEP:.3f}, ease:"power2.out", '
         f'delay:(i,el)=>+el.dataset.k*{2 * F:.4f}}}, {t:.3f});')


def scatter(X, sel, t):
    """the old value's modules are thrown outward (8 frames), then the group is gone."""
    X.tw(f'tl.to("{sel} .md", {{x:(i,el)=>+el.dataset.ox, y:(i,el)=>+el.dataset.oy, duration:{8 * F:.3f}, ease:"power2.in"}}, {t:.3f});')
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {t + 8 * F:.3f});')


# ---------------------------------------------------------------- shapes
def circ(cx, cy, r, fill, cls=""):
    return f'<g class="{cls}"><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"/></g>'


def rect(x, y, w, h, fill, cls=""):
    return f'<g class="{cls}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"/></g>'


def poly(pts, fill, cls=""):
    return f'<g class="{cls}"><polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"/></g>'


def line(x1, y1, x2, y2, col, w, cls=""):
    return f'<g class="{cls}"><line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}"/></g>'


def sector(cx, cy, r, a0, a1, fill, cls=""):
    def p(a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    x0, y0 = p(a0); x1, y1 = p(a1)
    big = 1 if a1 - a0 > 180 else 0
    return f'<g class="{cls}"><path d="M{cx:.1f} {cy:.1f}L{x0:.1f} {y0:.1f}A{r:.1f} {r:.1f} 0 {big} 1 {x1:.1f} {y1:.1f}Z" fill="{fill}"/></g>'


def qarc(cx, cy, r, a0, a1, col, w, cls=""):
    return f'<g class="{cls}"><path d="{_arc_d(cx, cy, r, a0, a1)}" fill="none" stroke="{col}" stroke-width="{w}" pathLength="1" stroke-dasharray="1 1"/></g>'


def clipdef(cid, inner):
    return f'<clipPath id="{cid}">{inner}</clipPath>'


def overlap(clip_id, svg, cls="ov"):
    """the part of `svg` that lies over another form, painted in a third colour: the copy keeps the original's classes, so every
    tween on the original moves it too, and it is clipped by the other form's (resting) geometry."""
    return f'<g class="{cls}" clip-path="url(#{clip_id})">{svg}</g>'


def steps(X, sel, t, n, deg, origin, svg=True):
    """stage machinery: n rotations of `deg` each around an off-centre pivot, 10 frames per step, 2-frame hold."""
    key = "svgOrigin" if svg else "transformOrigin"
    for k in range(n):
        X.tw(f'tl.to("{sel}", {{rotation:"+={deg}", {key}:"{origin}", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t + k * (STEP + HOLD):.3f});')
    return t + n * (STEP + HOLD)


def pivot_in(X, sel, t, n, deg, origin, svg=True):
    """a square pivots on a corner into place: starts n × deg away, comes back in steps."""
    key = "svgOrigin" if svg else "transformOrigin"
    X.tw(f'tl.set("{sel}", {{rotation:{n * deg}, {key}:"{origin}"}}, {max(0, t - 0.01):.3f});')
    return steps(X, sel, t, n, -deg, origin, svg)


def slide(X, sel, t, dx=0, dy=0, n=1, dur=None):
    """slides along a grid axis, in n mechanical steps (each 10 frames + 2-frame hold)."""
    X.tw(f'tl.set("{sel}", {{x:"+={dx}", y:"+={dy}"}}, {max(0, t - 0.01):.3f});')
    for k in range(n):
        X.tw(f'tl.to("{sel}", {{x:"-={dx / n:.1f}", y:"-={dy / n:.1f}", duration:{dur or STEP:.3f}, ease:"power2.inOut"}}, {t + k * ((dur or STEP) + HOLD):.3f});')
    return t + n * ((dur or STEP) + HOLD)


def roll(X, sel, t, dx, r, cx, cy, dur=0.6):
    """a circle rolls dx px along x: the group travels, its inner .spin turns dx / 2πr turns about the centre."""
    deg = dx / (2 * math.pi * r) * 360
    X.tw(f'tl.fromTo("{sel}", {{x:{-dx:.1f}}}, {{x:0, duration:{dur:.3f}, ease:"power2.inOut"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel} .spin", {{rotation:{-deg:.1f}, svgOrigin:"{cx:.1f} {cy:.1f}"}}, {{rotation:0, svgOrigin:"{cx:.1f} {cy:.1f}", duration:{dur:.3f}, ease:"power2.inOut"}}, {t:.3f});')
    return t + dur


def draw(X, sel, t, dur=STEP, ease="power2.inOut"):
    X.tw(f'tl.fromTo("{sel} path, {sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{dur:.3f}, ease:"{ease}"}}, {t:.3f});')


def grow(X, sel, t, axis="x", origin="0 0", dur=STEP):
    """a bar or hairline is pushed across the frame from one end (scale from 0 along its axis)."""
    X.tw(f'tl.from("{sel}", {{scale{axis.upper()}:0, svgOrigin:"{origin}", duration:{dur:.3f}, ease:"power2.inOut"}}, {t:.3f});')


def show(X, sel, t):
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, 0); tl.set("{sel}", {{visibility:"visible"}}, {t:.3f});')


def hl(X, text, px, x, y, col, cls="", rot=0, origin="0 100%"):
    """a heavy 黑体 headline set on its baseline (y = baseline); every glyph is its own block so it can rise off the bar."""
    X.used_text.update(text)
    glyphs = "".join(f'<i class="c">{X.rich(ch)}</i>' if ch.strip() else '<i class="c">&nbsp;</i>' for ch in text)
    tr = f"transform:rotate({rot}deg);transform-origin:{origin};" if rot else ""
    return (f'<div class="msk {cls}" style="left:{x:.0f}px;top:{y - px * 1.0:.0f}px;height:{px * 1.0 + 4:.0f}px;{tr}">'
            f'<div class="t hl" style="position:relative;font-size:{px}px;color:{col}">{glyphs}</div></div>')


def hl_rot(X, text, px, x, y, col, cls=""):
    """a headline on a baseline turned -90° (reads bottom to top): (x, y) is the bottom-left corner of its ink box on screen;
    the baseline is the right edge, where the heavy bar stands."""
    X.used_text.update(text)
    glyphs = "".join(f'<i class="c">{X.rich(ch)}</i>' if ch.strip() else '<i class="c">&nbsp;</i>' for ch in text)
    return (f'<div class="msk {cls}" style="left:{x:.0f}px;top:{y:.0f}px;height:{px + 4:.0f}px;transform:rotate(-90deg);transform-origin:0 0">'
            f'<div class="t hl" style="position:relative;font-size:{px}px;color:{col}">{glyphs}</div></div>')


def rise(X, sel, t):
    """glyphs push up out of the bar they sit on (each in a 2-frame stagger)."""
    X.tw(f'tl.from("{sel} .c", {{yPercent:105, duration:{STEP * 1.2:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {t:.3f});')


def lab(X, text, x, y, col, px=28, cls="", align="left", extra=""):
    X.used_text.update(text)
    a = "transform:translateX(-100%);" if align == "right" else ("transform:translateX(-50%);" if align == "center" else "")
    return f'<div class="t lb {cls}" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px}px;color:{col};{a}{extra}">{X.rich(text)}</div>'


def val(X, text, px, x, y, col, cls="", align="left"):
    X.used_text.update(text)
    a = "transform:translateX(-100%);" if align == "right" else ("transform:translateX(-50%);" if align == "center" else "")
    return f'<div class="t vl {cls}" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px}px;color:{col};{a}">{X.rich(text)}</div>'


def slide_in(X, sel, t, dx=-1200, dy=0):
    X.tw(f'tl.from("{sel}", {{x:{dx}, y:{dy}, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {t:.3f});')


# ---------------------------------------------------------------- the page
def ground(X, i=None):
    i = X.beat["i"] if i is None else i
    bs = X.v.get("beats", [])
    g = bs[i].get("ground", "red") if 0 <= i < len(bs) else "red"
    return g if g in GROUNDS else "red"


def _reveal(X, sel, t, kind):
    """the next page's ground arrives as a growing form, 13 frames: a circle from a corner, a giant square pivoting over
    from the bottom-left corner, or a 45° bar wiping across."""
    W, H = X.W, X.H
    D = math.hypot(W, H) + 40
    if kind == "circle":
        cx, cy = (W, H) if X.beat["i"] % 2 else (0, H)
        X.tw(f'tl.fromTo("{sel}", {{clipPath:"circle(0px at {cx}px {cy}px)"}}, {{clipPath:"circle({D:.0f}px at {cx}px {cy}px)", '
             f'duration:{TR:.3f}, ease:"power2.inOut"}}, {t:.3f});')
    elif kind == "wipe":
        S = W + H + 40
        X.tw(f'tl.fromTo("{sel}", {{clipPath:"polygon(0px 0px, 0px 0px, 0px 0px)"}}, {{clipPath:"polygon(0px 0px, {2 * S}px 0px, 0px {2 * S}px)", '
             f'duration:{TR:.3f}, ease:"power2.inOut"}}, {t:.3f});')
    else:      # pivot: a square of side W+H turns 90° about the bottom-left corner and lands as the new ground
        Lq = W + H
        X.tw(f'(()=>{{const o={{a:-90}}, el=document.querySelector("{sel}"); const f=()=>{{const a=o.a*Math.PI/180, c=Math.cos(a), s=Math.sin(a);'
             f'const p=[[0,{H}],[{Lq}*c,{H}+{Lq}*s],[{Lq}*c+{Lq}*s,{H}+{Lq}*s-{Lq}*c],[{Lq}*s,{H}-{Lq}*c]];'
             f'el.style.clipPath="polygon("+p.map(q=>q[0].toFixed(1)+"px "+q[1].toFixed(1)+"px").join(",")+")";}};'
             f'tl.fromTo(o, {{a:-90}}, {{a:0, duration:{TR:.3f}, ease:"power2.inOut", onUpdate:f, onStart:f}}, {t:.3f});}})();')
    X.tw(f'tl.set("{sel}", {{clipPath:"none"}}, {t + TR + 0.01:.3f});')


def page(X, b, cid, t, d, svg, html, gnd=None, counter=None, dom=None, reveal="circle"):
    """one construction page: full-bleed ground + grain, the SVG construction, the type, the header and the source line.
    counter = the 1/3 counter-form (dict k, x, y, w, h, fill) — when the previous page left a circle or square, that form
    shrinks into this counter-form while the new ground grows in. dom = this page's dominant form, for the next page."""
    X.css("bauhaus", CSS.replace("__GRAIN__", GRAIN))
    X.css("bauhaus-cap", CAP_CSS)
    P, W, H = X.portrait, X.W, X.H
    i, n = X.beat["i"], X.beat["n"]
    gnd = gnd or ground(X)
    G = GROUNDS[gnd]
    meta = X.v.get("meta", {})
    slug = b.get("slug") or meta.get("slug", "ikea fy24")
    src = b.get("src", "")
    band = " band" if G.get("small") == "band" else ""
    hx, hy = (72, 204) if P else (72, 48)
    X.used_text.update(slug + "0123456789/· ")
    hd = f'<div class="bh-hd{band}" style="left:{0 if band else hx}px;top:{hy - (6 if band else 0)}px;{"padding-left:" + str(hx) + "px;" if band else ""}"><i></i><span>{X.rich(slug)} · {i + 1:02d}/{n:02d}</span></div>'
    sy = 1452 if P else 892
    sr = f'<div class="bh-src{band}" style="left:0;top:{sy}px;padding-left:72px;max-width:{900 if P else 1300}px">{X.rich(src)}</div>' if src else ""
    X.used_text.update(src)
    body = (f'<div class="bh g-{gnd}" style="--g:{G["bg"]};--tx:{G["tx"]}">'
            f'<svg class="cs" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{svg}</svg>{html}{hd}{sr}<div class="grn"></div></div>')
    D = X.duration or (t + d)
    ext = min(d + TR + 0.1, max(d, D - t))
    X.clip(cid, t, ext, body, "scene", 2 + 3 * i, track=1 + i % 2)
    s = f"#{cid}"
    X.tw(f'tl.set("#root", {{"--bhcb":"{G["cap"]}", "--bhcf":"{G["capfg"]}"}}, {t:.3f});')
    if i > 0:
        _reveal(X, f"{s} .bh", t, reveal)
    prev = getattr(X, "_bh_dom", None)
    if counter:
        k = counter
        rad = "50%" if k["k"] == "circle" else "0"
        X.clip(f"{cid}k", t, ext, f'<div class="bhk" style="left:{k["x"]:.0f}px;top:{k["y"]:.0f}px;width:{k["w"]:.0f}px;height:{k["h"]:.0f}px;'
                                  f'background:{k["fill"]};border-radius:{rad}"></div>', "scene", 3 + 3 * i, track=40 + i % 2)
        ks = f"#{cid}k .bhk"
        if prev and prev.get("i") == i - 1 and i > 0:
            pr = "50%" if prev["k"] == "circle" else "0"
            X.tw(f'tl.fromTo("{ks}", {{x:{prev["x"] - k["x"]:.0f}, y:{prev["y"] - k["y"]:.0f}, scaleX:{prev["w"] / k["w"]:.4f}, scaleY:{prev["h"] / k["h"]:.4f}, transformOrigin:"0 0", backgroundColor:"{prev["fill"]}", borderRadius:"{pr}"}}, '
                 f'{{x:0, y:0, scaleX:1, scaleY:1, transformOrigin:"0 0", backgroundColor:"{k["fill"]}", borderRadius:"{rad}", duration:{TR + 4 * F:.3f}, ease:"power2.inOut"}}, {t:.3f});')
            X.tw(f'tl.set("{prev["sel"]}, {prev["page"]} .ov", {{visibility:"hidden"}}, {t:.3f});')
        else:
            X.tw(f'tl.from("{ks}", {{rotation:{90 if i % 2 else -90}, transformOrigin:"0% 100%", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t + TR:.3f});')
    X._bh_dom = dict(dom, i=i, page=s) if dom else None
    return s


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def C(gnd):
    return GROUNDS[gnd]


# ---------------------------------------------------------------- scenes
def hero(b, X, t, d, cid):
    """搭出来的大数字：黑色主圆从底下分两步升上来，黄方块绕角翻进右上角，粗条从左边推进来、标题从粗条里顶出来；
    然后数字一个模块一个模块搭起来，压在圆上的那一截涂成黄色；最后圆里的四分之一圆弧按 90° 两步转动。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    big = str(b.get("big", "451")); unit = b.get("unit", ""); title = b.get("title", "")
    if P:
        cx, cy, r = 560, 1470, 470
        nh, nx, ny = 460, 72, 690
        by, tpx = 414, 150
        sq = (828, 150, 300)
        hx = 960
        ux, uy, upx = 72, 1176, 88
    else:
        cx, cy, r = 1360, 790, 470
        nh, nx, ny = 460, 120, 330
        by, tpx = 250, 130
        sq = (1660, -60, 300)
        hx = 1060
        ux, uy, upx = 120, 812, 80
    svg = clipdef(f"{cid}c", f'<circle cx="{cx}" cy="{cy}" r="{r}"/>') + clipdef(f"{cid}s", f'<rect x="{sq[0]}" y="{sq[1]}" width="{sq[2]}" height="{sq[2]}"/>')
    svg += circ(cx, cy, r, BLK, "dom")
    svg += qarc(cx, cy, r - 110, 270, 360, GW, 28, "dom qa")
    svg += rect(*sq[:2], sq[2], sq[2], YEL, "ctr")
    svg += rect(0, by, W, 24, BLK, "hb")
    svg += overlap(f"{cid}s", rect(0, by, W, 24, COB, "hb"))
    svg += line(hx, 0, hx, H, BLK, 4, "hair")
    svg += overlap(f"{cid}c", line(hx, 0, hx, H, YEL, 4, "hair"))
    svg += numeral(big, nh, nx, ny, GW, "num", W, H)
    svg += overlap(f"{cid}c", numeral(big, nh, nx, ny, YEL, "num", W, H), "ov ovn")
    html = hl(X, title, tpx, 72, by, G["tx"], "ttl") + (f'<div class="t hl unit" style="left:{ux}px;top:{uy}px;font-size:{upx}px;color:{GW}">{X.rich(unit)}</div>' if unit else "")
    X.used_text.update(unit)
    s = page(X, b, cid, t, d, svg, html, gnd, dom={"k": "circle", "x": cx - r, "y": cy - r, "w": 2 * r, "h": 2 * r, "fill": BLK, "sel": f"#{cid} .dom"})
    t0 = t + 0.1
    show(X, f"{s} .ov", t0 + 2 * STEP + HOLD + 0.02)
    slide(X, f"{s} .dom", t0, dy=H - cy + r + 40, n=2)
    pivot_in(X, f"{s} .ctr", t0 + 0.25, 2, -45, f"{sq[0]} {sq[1] + sq[2]}")
    grow(X, f"{s} .hb", t0 + 0.15, "x", f"0 {by}")
    rise(X, f"{s} .ttl", t0 + 0.4)
    grow(X, f"{s} .hair", t0 + 0.3, "y", f"{hx} 0")
    tn = T(X, b, "at_big", t, t0 + 0.75)
    assemble(X, f"{s} .num", max(t0 + 0.6, tn - 0.25))
    if unit: slide_in(X, f"{s} .unit", max(t0 + 0.9, tn + 0.3))
    steps(X, f"{s} .qa", t + d * 0.62, 2, 90, f"{cx} {cy}")


def stairs(b, X, t, d, cid):
    """增长 / 时间线：三根柱子共用一条底线（在画面外），高度按真实比例；黑球一级一级跳上去，落在哪根柱子上，
    上面的搭字数字就拆掉重搭成哪一年的值；粗条竖着穿过画面，标题转 90° 贴在粗条上。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    items = b.get("items", [])[:4]
    title = b.get("title", "")
    vmax = max(float(it["value"]) for it in items)
    n = len(items)
    if P:
        bw, gap, x0 = 220, 18, 270
        base = H + 40
        scale = 1100 / vmax
        nh, nx, ny = 460, 72, 236
        bx, tpx = 252, 140
        ty = 1290
        cc = {"k": "circle", "x": -70, "y": 1540, "w": 300, "h": 300, "fill": BLK}
    else:
        bw, gap, x0 = 222, 20, 1196
        base = H + 40
        scale = 760 / vmax
        nh, nx, ny = 460, 290, 300
        bx, tpx = 252, 130
        ty = 820
        cc = {"k": "circle", "x": 1700, "y": -80, "w": 260, "h": 260, "fill": BLK}
    cols = [COB] * (n - 1) + [BLK]          # the latest year in black: grey-white labels read on every bar
    tops, xs = [], []
    svg = ""
    for k, it in enumerate(items):
        v = float(it["value"])
        hgt = v * scale
        x = x0 + k * (bw + gap)
        top = base - hgt
        tops.append(top); xs.append(x)
        svg += rect(x, top, bw, hgt + 200, cols[k], f"bar b{k}")
    hx1, hy1 = (0, H) if P else (700, H)
    hx2 = hx1 + 1700
    if P:
        ha, hb_ = (380, 1420), (700, 1100)        # under the labels, above the source line
    else:
        ha, hb_ = (1000, 860), (1320, 540)
    svg += line(*ha, *hb_, BLK, 4, "hair")
    svg += clipdef(f"{cid}bars", "".join(f'<rect x="{xs[k]}" y="{tops[k]}" width="{bw}" height="{base - tops[k] + 200}"/>' for k in range(n)))
    svg += overlap(f"{cid}bars", line(*ha, *hb_, GW, 4, "hair"))
    svg += rect(bx - 24, 252 if P else 96, 24, H, BLK, "hb")      # 9:16: starts under the header so the slug stays legible
    br = 90
    ball = f'<g class="ball"><circle cx="0" cy="0" r="{br}" fill="{BLK}"/><path d="M0 0L{br} 0A{br} {br} 0 0 1 0 {br}Z" fill="{GW}"/></g>'
    svg += ball
    for k, it in enumerate(items):
        svg += numeral(str(it.get("show", it["value"])), nh, nx, ny, BLK, f"num n{k}", W, H)
    labels = ""
    for k, it in enumerate(items):
        labels += lab(X, it.get("label", ""), xs[k] + 20, tops[k] + 22, GW, 28, f"bl bl{k}")
        labels += val(X, it.get("tag", ""), 48, xs[k] + 20, tops[k] + 62, GW, f"bv bv{k}")
    html = labels + hl_rot(X, title, tpx, bx - 24 - tpx - 4, ty, G["tx"], "ttl")
    s = page(X, b, cid, t, d, svg, html, gnd, reveal=b.get("reveal", "circle"), counter=cc)
    t0 = t + TR
    for k in range(n):
        slide(X, f"{s} .b{k}", t0 + k * 2 * F, dy=base - tops[k] + 60, n=1, dur=STEP * 1.4)
    grow(X, f"{s} .hb", t0, "y", f"{bx} 0")
    rise(X, f"{s} .ttl", t0 + 0.25)
    grow(X, f"{s} .hair", t0 + 0.2, "x", f"{ha[0]} {ha[1]}")
    show(X, f"{s} .ov", t0 + 0.6)
    # the ball: drops onto the first step, then hops step to step (x linear, y up-and-down), rolling as it travels
    hop = [T(X, it, "at", t, t0 + 0.6 + k * 0.95) for k, it in enumerate(items)]
    cxs = [xs[k] + bw / 2 for k in range(n)]
    cys = [tops[k] - br for k in range(n)]
    X.tw(f'tl.set("{s} .ball", {{x:{cxs[0]:.1f}, y:{-br * 2}}}, 0);')
    X.tw(f'tl.to("{s} .ball", {{y:{cys[0]:.1f}, duration:{STEP * 1.3:.3f}, ease:"power2.in"}}, {hop[0] - STEP * 1.3:.3f});')
    for k in range(n):
        X.tw(f'tl.set("{s} .n{k}", {{visibility:"hidden"}}, 0);')
        X.tw(f'tl.set("{s} .n{k}", {{visibility:"visible"}}, {hop[k]:.3f});')
        assemble(X, f"{s} .n{k}", hop[k])
        X.tw(f'tl.from("{s} .bl{k}, {s} .bv{k}", {{y:40, opacity:0, duration:{STEP:.3f}, ease:"power2.out"}}, {hop[k]:.3f});')
        if k:
            scatter(X, f"{s} .n{k - 1}", hop[k] - 0.02)
            dur = max(0.3, min(0.6, hop[k] - hop[k - 1] - 0.15))
            dist = cxs[k] - cxs[k - 1]
            apex = min(cys[k], cys[k - 1]) - 160
            deg = dist / (2 * math.pi * br) * 360
            t1 = hop[k] - dur
            X.tw(f'tl.to("{s} .ball", {{x:{cxs[k]:.1f}, rotation:"+={deg:.1f}", transformOrigin:"50% 50%", duration:{dur:.3f}, ease:"none"}}, {t1:.3f});')
            X.tw(f'tl.to("{s} .ball", {{y:{apex:.1f}, duration:{dur / 2:.3f}, ease:"power2.out"}}, {t1:.3f});')
            X.tw(f'tl.to("{s} .ball", {{y:{cys[k]:.1f}, duration:{dur / 2:.3f}, ease:"power2.in"}}, {t1 + dur / 2:.3f});')
    X._bh_dom = None


def slice_(b, X, t, d, cid):
    """占比：黄色主圆从右边滚进来（转角对得上位移），按真实角度切出的红色扇形被拉出去；搭字数字压在圆的上沿，
    压在圆上的那一截变成黑色，所以字在蓝底和黄圆上都读得清。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    pct = float(b.get("pct", 10)); big = str(b.get("big", f"{pct:g}%"))
    title = b.get("title", ""); note = b.get("note", "")
    a1 = 360 * pct / 100
    if P:
        cx, cy, r = 560, 1350, 430
        nh, nx, ny, gap = 460, 64, 640, 0.08
        by, tpx = 392, 150
        hy0, hy1 = (180, 1920), (1080, 1020)
        sq = {"k": "square", "x": 846, "y": 196, "w": 290, "h": 290, "fill": GW}
        nlx, nly = 72, 446
    else:
        cx, cy, r = 1380, 640, 420
        nh, nx, ny, gap = 460, 110, 380, 0.1
        by, tpx = 260, 130
        hy0, hy1 = (900, 1080), (1920, 60)
        sq = {"k": "square", "x": 1680, "y": -80, "w": 280, "h": 280, "fill": GW}
        nlx, nly = 110, 296
    sa0, sa1 = -a1, 0
    svg = clipdef(f"{cid}c", f'<circle cx="{cx}" cy="{cy}" r="{r}"/>')
    svg += f'<g class="disc"><g class="spin">{circ(cx, cy, r, YEL)}</g></g>'
    svg += f'<g class="cut"><g class="spin">{sector(cx, cy, r, sa0, sa1, RED)}</g></g>'
    svg += line(*hy0, *hy1, GW, 4, "hair")
    svg += overlap(f"{cid}c", line(*hy0, *hy1, COB, 4, "hair"))
    svg += rect(0, by, W, 24, YEL, "hb")
    svg += numeral(big, nh, nx, ny, GW, "num", W, H, gap)
    svg += overlap(f"{cid}c", numeral(big, nh, nx, ny, BLK, "num", W, H, gap), "ov ovn")
    html = hl(X, title, tpx, 72 if P else 110, by, G["tx"], "ttl") + (lab(X, note, nlx, nly, G["tx"], 28, "note") if note else "")
    s = page(X, b, cid, t, d, svg, html, gnd, counter=sq, reveal=b.get("reveal", "pivot"),
             dom={"k": "circle", "x": cx - r, "y": cy - r, "w": 2 * r, "h": 2 * r, "fill": YEL, "sel": f"#{cid} .disc, #{cid} .cut"})
    t0 = t + TR
    roll(X, f"{s} .disc", t0, W - cx + r + 40, r, cx, cy, 0.6)
    roll(X, f"{s} .cut", t0, W - cx + r + 40, r, cx, cy, 0.6)
    grow(X, f"{s} .hb", t0 + 0.1, "x", f"0 {by}")
    rise(X, f"{s} .ttl", t0 + 0.3)
    grow(X, f"{s} .hair", t0 + 0.25, "x", f"{hy0[0]} {hy0[1]}")
    show(X, f"{s} .ov", t0 + 0.62)
    tn = T(X, b, "at_big", t, t0 + 0.65)
    assemble(X, f"{s} .num", max(t0 + 0.62, tn - 0.25))
    tc = T(X, b, "at_cut", t, t0 + 1.5)
    X.tw(f'tl.to("{s} .cut", {{x:{70 if P else 80}, duration:{STEP:.3f}, ease:"power2.inOut"}}, {tc:.3f});')
    X.tw(f'tl.to("{s} .cut", {{y:{-48}, duration:{STEP:.3f}, ease:"power2.inOut"}}, {tc + STEP + HOLD:.3f});')
    if note: X.tw(f'tl.from("{s} .note", {{x:-900, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {t0 + 0.5:.3f});')


def quote(b, X, t, d, cid):
    """引语：63 个小方格（每格一个市场）一行一行从左边滑进来，然后一道 45° 的波把每一格翻成红色、往下压一格的四分之一
    （降价）；引语压在粗条上，引号是两块四分之一圆。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    cols_, rows_ = int(b.get("cols", 9)), int(b.get("rows", 7))
    l1, l2 = b.get("l1", ""), b.get("l2", ""); by_ = b.get("by", "")
    if P:
        cell, gx, gy = 80, 72, 290
        by, tpx = 1206, 128
        q = (800, 290, 90)
        tri = None
        cc = {"k": "circle", "x": 730, "y": 1470, "w": 300, "h": 300, "fill": COB}
        hx0, hx1 = (560, 1920), (1080, 1400)
        byx, byy = 72, 1244
    else:
        cell, gx, gy = 64, 1080, 150
        by, tpx = 760, 120
        q = (100, 150, 90)
        cc = {"k": "circle", "x": 1640, "y": 790, "w": 300, "h": 300, "fill": COB}
        hx0, hx1 = (1400, 1080), (1920, 560)
        byx, byy = 110, 790
    svg = ""
    gw_, gh_ = cols_ * cell, rows_ * cell
    for r in range(rows_):
        cells = "".join(f'<rect class="cl" data-d="{c + r}" x="{gx + c * cell + 6}" y="{gy + r * cell + 6}" width="{cell - 12}" height="{cell - 12}" fill="{BLK}"/>' for c in range(cols_))
        svg += f'<g class="row r{r}">{cells}</g>'
    # the quote mark: two quarter discs
    qx, qy, qs = q
    svg += f'<g class="qm"><path d="M{qx} {qy + qs}A{qs} {qs} 0 0 1 {qx + qs} {qy}L{qx + qs} {qy + qs}Z" fill="{RED}"/>' \
           f'<path d="M{qx + qs + 20} {qy + qs}A{qs} {qs} 0 0 1 {qx + 2 * qs + 20} {qy}L{qx + 2 * qs + 20} {qy + qs}Z" fill="{RED}"/></g>'
    svg += rect(0, by, W, 24, BLK, "hb")
    svg += line(*hx0, *hx1, BLK, 4, "hair")
    html = (hl(X, l1, tpx, 72 if P else 110, by - tpx * 1.12, G["tx"], "l1") + hl(X, l2, tpx, 72 if P else 110, by, G["tx"], "l2")
            + lab(X, by_, byx, byy, G["tx"], 28, "by") + lab(X, b.get("key", ""), gx, gy + gh_ + 16, G["tx"], 28, "key"))
    s = page(X, b, cid, t, d, svg, html, gnd, counter=cc, reveal=b.get("reveal", "wipe"),
             dom={"k": "square", "x": gx, "y": gy, "w": gw_, "h": gh_, "fill": RED, "sel": f"#{cid} .row"})
    # the hairline crossing the counter disc is painted yellow there: an overlay above the counter clip
    ccx, ccy = cc["x"] + cc["w"] / 2, cc["y"] + cc["h"] / 2
    ov = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">'
          f'<defs><clipPath id="{cid}cc2"><circle cx="{ccx:.0f}" cy="{ccy:.0f}" r="{cc["w"] / 2:.0f}"/></clipPath></defs>'
          f'<g clip-path="url(#{cid}cc2)">{line(*hx0, *hx1, YEL, 4, "hair2")}</g></svg>')
    X.clip(f"{cid}o", t, d, ov, "scene", 4 + 3 * X.beat["i"], track=44)
    t0 = t + TR
    for r in range(rows_):
        slide(X, f"{s} .r{r}", t0 + r * 2 * F, dx=-(gx + gw_ + 40), n=1, dur=STEP * 1.2)
    grow(X, f"{s} .hb", t0 + 0.1, "x", f"0 {by}")
    rise(X, f"{s} .l1", t0 + 0.35)
    rise(X, f"{s} .l2", t0 + 0.5)
    X.tw(f'tl.from("{s} .qm path", {{rotation:-90, svgOrigin:"{qx + qs} {qy + qs}", duration:{STEP:.3f}, ease:"power2.inOut", stagger:{2 * F:.4f}}}, {t0 + 0.2:.3f});')
    grow(X, f"{s} .hair", t0 + 0.4, "x", f"{hx0[0]} {hx0[1]}")
    X.tw(f'tl.from("#{cid}o .hair2", {{scaleX:0, svgOrigin:"{hx0[0]} {hx0[1]}", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t0 + 0.4:.3f});')
    X.tw(f'tl.from("{s} .by", {{x:-900, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {t0 + 0.7:.3f});')
    X.tw(f'tl.from("{s} .key", {{x:900, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {t0 + 0.5:.3f});')
    tw = T(X, b, "at_wave", t, t0 + 1.3)
    X.tw(f'tl.to("{s} .cl", {{fill:"{RED}", y:{cell * 0.25:.0f}, duration:{STEP:.3f}, ease:"power2.inOut", delay:(i,el)=>+el.dataset.d*{F:.4f}}}, {tw:.3f});')


def rings(b, X, t, d, cid):
    """排行：同心圆环，环宽正比于数值；每个环一笔扫出来（从 12 点顺时针），然后一根横细线从环里伸出去，标注从左边滑进来。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    items = b.get("items", [])
    title = b.get("title", ""); note = b.get("note", "")
    k_ = float(b.get("k", 7.5))
    if P:
        cx, cy, r0 = 760, 920, 120
        by, tpx = 384, 150
        cc = {"k": "square", "x": -40, "y": 1560, "w": 280, "h": 280, "fill": GW}
        hx = 1010
        ly = [690, 875, 1060]
        nx, ny = 72, 430
    else:
        cx, cy, r0 = 1400, 560, 110
        by, tpx = 300, 130
        cc = {"k": "square", "x": 1700, "y": 820, "w": 280, "h": 280, "fill": GW}
        hx = 1180
        ly = [500, 670, 840]
        nx, ny = 110, 344
    cols = [RED, GW, YEL]          # inner → outer
    # items are listed biggest first; draw from the inside out (smallest innermost)
    order = list(reversed(items))
    radii = []
    r = r0
    for it in order:
        th = float(it["value"]) * k_
        radii.append((r, r + th))
        r += th
    rout = r
    svg = clipdef(f"{cid}o", f'<circle cx="{cx}" cy="{cy}" r="{rout:.1f}"/>')
    for j, it in enumerate(order):
        a, bb = radii[j]
        rm, th = (a + bb) / 2, bb - a
        svg += f'<g class="rg g{j}"><circle cx="{cx}" cy="{cy}" r="{rm:.1f}" fill="none" stroke="{cols[j % 3]}" stroke-width="{th + 0.6:.1f}" pathLength="1" stroke-dasharray="1 1" transform="rotate(-90 {cx} {cy})"/></g>'
    svg += line(hx, 0, hx, H, GW, 4, "hair")
    svg += overlap(f"{cid}o", line(hx, 0, hx, H, BLK, 4, "hair"))
    svg += rect(0, by, W, 24, RED, "hb")
    html = hl(X, title, tpx, 72 if P else 110, by, G["tx"], "ttl") + (lab(X, note, nx, ny, G["tx"], 28, "note") if note else "")
    for k, it in enumerate(items):          # labels: biggest on top
        j = len(items) - 1 - k
        a, bb = radii[j]
        rm = (a + bb) / 2
        y = ly[k]
        dy = y - cy
        x_end = cx - math.sqrt(max(0.0, rm * rm - dy * dy))
        svg += line(72, y, x_end, y, GW, 4, f"lead ld{k}")
        svg += overlap(f"{cid}o", line(72, y, x_end, y, BLK, 4, f"lead ld{k}"))
        html += val(X, str(it.get("show", it["value"])), 96, 72, y - 104, G["tx"], f"lv lv{k}")
        html += lab(X, it.get("label", ""), 72, y + 14, G["tx"], 30, f"ll ll{k}")
    s = page(X, b, cid, t, d, svg, html, gnd, counter=cc, reveal=b.get("reveal", "circle"),
             dom={"k": "circle", "x": cx - rout, "y": cy - rout, "w": 2 * rout, "h": 2 * rout, "fill": YEL, "sel": f"#{cid} .rg"})
    t0 = t + TR
    grow(X, f"{s} .hb", t0, "x", f"0 {by}")
    rise(X, f"{s} .ttl", t0 + 0.2)
    if note: slide_in(X, f"{s} .note", t0 + 0.4)
    grow(X, f"{s} .hair", t0 + 0.15, "y", f"{hx} 0")
    for j in range(len(order)):
        X.tw(f'tl.fromTo("{s} .g{len(order) - 1 - j} circle", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{STEP * 2:.3f}, ease:"power2.inOut"}}, {t0 + 0.3 + j * (STEP + HOLD):.3f});')
    show(X, f"{s} .ov", t0 + 0.3 + len(order) * (STEP + HOLD) + STEP)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t0 + 1.0 + k * 0.45)
        X.tw(f'tl.from("{s} .ld{k}", {{scaleX:0, svgOrigin:"{cx} {ly[k]}", duration:{STEP:.3f}, ease:"power2.inOut"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .lv{k}, {s} .ll{k}", {{x:-600, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {tk + STEP:.3f});')
    steps(X, f"{s} .rg", t + d * 0.7, 1, 90, f"{cx} {cy}")


def squares(b, X, t, d, cid):
    """对比：两个正方形共用左下角，面积是真实比例；大方块绕这个角分两步翻进来，小方块再从同一个角翻出来；
    一根 45° 细线正好穿过两个方块的对角线。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    A, B = b.get("a", {}), b.get("b", {})          # a = the big one
    va, vb = float(A["value"]), float(B["value"])
    title = b.get("title", "")
    if P:
        La = 760
        x0, y1 = 230, 1060
        by, tpx = 1254, 140
        cc = {"k": "circle", "x": 760, "y": 1530, "w": 260, "h": 260, "fill": YEL}
    else:
        La = 760
        x0, y1 = 1080, 900
        by, tpx = 720, 130
        cc = {"k": "circle", "x": 800, "y": -70, "w": 220, "h": 220, "fill": YEL}
    Lb = La * math.sqrt(vb / va)
    svg = clipdef(f"{cid}a", f'<rect x="{x0}" y="{y1 - La}" width="{La}" height="{La}"/>') + clipdef(f"{cid}b", f'<rect x="{x0}" y="{y1 - Lb:.1f}" width="{Lb:.1f}" height="{Lb:.1f}"/>')
    svg += rect(x0, y1 - La, La, La, BLK, "sqa")
    svg += rect(x0, y1 - Lb, Lb, Lb, YEL, "sqb")
    hx = x0 + La + 20            # a vertical hairline just right of the big square, crossing the whole frame
    h0, h1 = (hx, 0), (hx, H)
    svg += line(*h0, *h1, GW, 4, "hair")
    svg += rect(0, by, W, 24, BLK, "hb")
    # the ratio is the hero: a constructed numeral in the big square's free top band, "倍" beside it
    rh = 340 if P else 320
    rx, ry = x0 + 40, y1 - La + 60 if P else y1 - La + 60
    rtxt = str(b.get("ratio_num", "5.1"))
    svg += numeral(rtxt, rh, rx, ry, GW, "rnum", W, H)
    rw = numeral_width(rtxt, rh)
    html = hl(X, title, tpx, 72 if P else 110, by, G["tx"], "ttl")
    # labels: the big square's in its free top-right corner (grey-white on black), the small one's inside it (black on yellow)
    # labels sit clear of the 45° hairline: the big one in the square's free bottom-right, the small one at its top-left, the ratio top-left
    html += val(X, A.get("show", ""), 96, x0 + La - 36, y1 - 190, GW, "va", "right")
    html += lab(X, A.get("label", ""), x0 + La - 36, y1 - 76, GW, 28, "la", "right")
    html += val(X, B.get("show", ""), 64, x0 + 28, y1 - Lb + 28, BLK, "vb")
    html += lab(X, B.get("label", ""), x0 + 28, y1 - Lb + 104, BLK, 28, "lb2")
    html += lab(X, b.get("ratio_label", ""), rx, y1 - La + 18, GW, 28, "rt")
    html += f'<div class="t hl rtu" style="left:{rx + rw + 24:.0f}px;top:{ry + rh - 120:.0f}px;font-size:120px;color:{GW}">{X.rich(b.get("ratio_unit", "倍"))}</div>'
    X.used_text.update(b.get("ratio_unit", "倍"))
    s = page(X, b, cid, t, d, svg, html, gnd, counter=cc, reveal=b.get("reveal", "pivot"),
             dom={"k": "square", "x": x0, "y": y1 - La, "w": La, "h": La, "fill": BLK, "sel": f"#{cid} .sqa, #{cid} .sqb"})
    t0 = t + TR
    show(X, f"{s} .ov", t0 + 2 * (STEP + HOLD) + 0.3)
    pivot_in(X, f"{s} .sqa", t0, 2, -45, f"{x0} {y1}")
    pivot_in(X, f"{s} .sqb", t0 + 2 * (STEP + HOLD), 2, 45, f"{x0} {y1}")
    grow(X, f"{s} .hb", t0 + 0.1, "x", f"0 {by}")
    rise(X, f"{s} .ttl", t0 + 0.3)
    grow(X, f"{s} .hair", t0 + 0.6, "y", f"{h0[0]} {h0[1]}")
    ta = T(X, A, "at", t, t0 + 1.2); tb = T(X, B, "at", t, t0 + 0.6)
    X.tw(f'tl.from("{s} .vb, {s} .lb2", {{x:-700, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {max(t0 + 0.6, tb):.3f});')
    X.tw(f'tl.from("{s} .va, {s} .la", {{x:-900, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {max(t0 + 0.8, ta):.3f});')
    tr_ = max(t0 + 1.2, ta + 0.45)
    assemble(X, f"{s} .rnum", tr_)
    X.tw(f'tl.from("{s} .rt", {{x:-900, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {tr_:.3f});')
    X.tw(f'tl.from("{s} .rtu", {{y:-700, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {tr_ + 0.3:.3f});')


def blocks(b, X, t, d, cid):
    """构成：一个正方形按真实面积切块——整块蓝方先从左边推进来，一根细线从上落下切开它，右边一列（红 + 黑）
    绕切线的顶端翻 90° 落进去。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    parts = b.get("parts", [])         # [{value, show, label}] — first = the big block, the rest stack in the right column
    title = b.get("title", "")
    tot = sum(float(p["value"]) for p in parts)
    if P:
        L, x0, y0 = 760, 72, 470
        by, tpx = 404, 150
        cc = {"k": "square", "x": 800, "y": 1540, "w": 250, "h": 250, "fill": RED}
        rx = 856
    else:
        L, x0, y0 = 760, 900, 150
        by, tpx = 600, 130
        cc = {"k": "square", "x": 440, "y": -90, "w": 250, "h": 250, "fill": RED}
        rx = None
    w0 = L * float(parts[0]["value"]) / tot
    xs = x0 + w0
    rest = parts[1:]
    rsum = sum(float(p["value"]) for p in rest)
    cols = [RED, BLK, COB]
    svg = rect(x0, y0, L, L, COB, "big")
    col = ""
    yy = y0
    geo = []
    for k, p_ in enumerate(reversed(rest)):        # the smallest on top
        hgt = L * float(p_["value"]) / rsum
        c = cols[(len(rest) - 1 - k) % 3]
        col += f'<rect x="{xs:.1f}" y="{yy:.1f}" width="{L - w0:.1f}" height="{hgt:.1f}" fill="{c}"/>'
        geo.append((p_, yy, hgt, c))
        yy += hgt
    svg += f'<g class="col">{col}</g>'
    svg += line(xs, 0, xs, H, BLK, 4, "hair")
    svg += rect(0, by, W, 24, BLK, "hb")
    html = hl(X, title, tpx, 72 if P else 110, by, G["tx"], "ttl")
    p0 = parts[0]
    html += val(X, p0.get("show", ""), 150, x0 + 40, y0 + 40, GW, "v0")
    html += lab(X, p0.get("label", ""), x0 + 44, y0 + 210, GW, 28, "l0")
    for k, (p_, yy, hgt, c) in enumerate(geo):
        ty = yy + (12 if hgt < 120 else 30)
        if P:
            html += val(X, p_.get("show", ""), 64 if hgt > 120 else 52, rx, ty, BLK, f"vr vr{k}")
            html += lab(X, p_.get("label", ""), rx, ty + (72 if hgt > 120 else 58), BLK, 28, f"lr lr{k}")
        else:
            html += val(X, p_.get("show", ""), 64 if hgt > 120 else 52, x0 + L + 28, ty, BLK, f"vr vr{k}")
            html += lab(X, p_.get("label", ""), x0 + L + 28, ty + (72 if hgt > 120 else 58), BLK, 28, f"lr lr{k}")
    s = page(X, b, cid, t, d, svg, html, gnd, counter=cc, reveal=b.get("reveal", "wipe"),
             dom={"k": "square", "x": x0, "y": y0, "w": L, "h": L, "fill": COB, "sel": f"#{cid} .big, #{cid} .col"})
    t0 = t + TR
    slide(X, f"{s} .big", t0, dx=-(x0 + L + 40), n=1, dur=STEP * 1.3)
    grow(X, f"{s} .hb", t0 + 0.05, "x", f"0 {by}")
    rise(X, f"{s} .ttl", t0 + 0.25)
    tc = T(X, b, "at_cut", t, t0 + 0.6)
    grow(X, f"{s} .hair", tc, "y", f"{xs:.1f} 0")
    pivot_in(X, f"{s} .col", tc + STEP, 2, -45, f"{xs:.1f} {y0}")
    X.tw(f'tl.from("{s} .v0, {s} .l0", {{x:-800, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {t0 + 0.45:.3f});')
    for k, (p_, *_r) in enumerate(geo):
        tk = T(X, p_, "at", t, tc + 2 * (STEP + HOLD) + k * 0.3)
        X.tw(f'tl.from("{s} .vr{k}, {s} .lr{k}", {{x:500, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {tk:.3f});')


def chain(b, X, t, d, cid):
    """因果链：三个三角形——黑色向下（价格）、蓝色向上（客流，主形）、红色向下（零售额）——沿一根 45° 细线排开，
    一个接一个绕自己的一个角翻进来；结果写在标题上，压在粗条上。"""
    P, W, H = X.portrait, X.W, X.H
    gnd = ground(X); G = C(gnd)
    a, m, z = b.get("a", {}), b.get("m", {}), b.get("z", {})
    title = b.get("title", "")
    if P:
        ta_ = [(72, 280), (552, 280), (312, 696)]
        tm = [(280, 1060), (1060, 1060), (670, 420)]
        tz = [(640, 1540), (1100, 1540), (870, 1940)]
        by, tpx = 1254, 128
        h0, h1 = (140, 280), (522, 662)      # a connector: from the black triangle's top edge to the blue triangle's edge
        alx, aly = 584, 300
    else:
        ta_ = [(110, 140), (530, 140), (320, 504)]
        tm = [(920, 940), (1580, 940), (1250, 300)]
        tz = [(1640, 500), (1960, 500), (1800, 780)]
        by, tpx = 880, 120
        h0, h1 = (440, 140), (1029, 729)
        alx, aly = 560, 160
    svg = clipdef(f"{cid}m", f'<polygon points="{" ".join(f"{x},{y}" for x, y in tm)}"/>') + clipdef(f"{cid}a", f'<polygon points="{" ".join(f"{x},{y}" for x, y in ta_)}"/>')
    svg += poly(ta_, BLK, "ta") + poly(tm, COB, "tm") + poly(tz, RED, "tz")
    svg += line(*h0, *h1, BLK, 4, "hair")
    svg += overlap(f"{cid}a", line(*h0, *h1, GW, 4, "hair"))
    svg += rect(0, by, W, 24, BLK, "hb")
    svg += overlap(f"{cid}m", rect(0, by, W, 24, YEL, "hb"))
    # inside the triangles
    acx = sum(x for x, _ in ta_) / 3
    mcx = sum(x for x, _ in tm) / 3
    html = val(X, a.get("show", ""), 64, acx + (30 if P else 0), ta_[0][1] + 28, GW, "va", "center")      # clear of the hairline
    html += lab(X, a.get("label", ""), alx, aly, G["tx"], 28, "la")
    my0 = tm[2][1] + (tm[0][1] - tm[2][1]) * (0.58 if P else 0.5)
    html += val(X, m.get("show", ""), 120, mcx, my0, GW, "vm", "center")
    html += lab(X, m.get("label", ""), mcx, my0 + 134, GW, 30, "lm", "center")
    html += lab(X, m.get("label2", ""), mcx, my0 + 178, GW, 30, "lm2", "center")
    html += hl(X, title, tpx, 72 if P else 110, by, G["tx"], "ttl")
    html += lab(X, b.get("sign", ""), 72 if P else 110, by + 40, G["tx"], 28, "sign")
    s = page(X, b, cid, t, d, svg, html, gnd, reveal=b.get("reveal", "circle"))
    t0 = t + TR
    pivot_in(X, f"{s} .ta", t0, 2, 45, f"{ta_[0][0]} {ta_[0][1]}")
    grow(X, f"{s} .hair", t0 + 0.2, "x", f"{h0[0]} {h0[1]}")
    X.tw(f'tl.from("{s} .va, {s} .la", {{x:-600, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {t0 + 0.4:.3f});')
    tm_ = T(X, m, "at", t, t0 + 1.0)
    pivot_in(X, f"{s} .tm", tm_ - 0.3, 2, -45, f"{tm[0][0]} {tm[0][1]}")
    show(X, f"{s} .ov", tm_ - 0.3 + 2 * (STEP + HOLD))
    X.tw(f'tl.from("{s} .vm, {s} .lm, {s} .lm2", {{x:-900, duration:{STEP * 1.3:.3f}, ease:"power3.out", stagger:{2 * F:.4f}}}, {tm_ + 0.2:.3f});')
    tz_ = T(X, z, "at", t, t0 + 2.0)
    slide(X, f"{s} .tz", tz_ - 0.4, dy=-(tz[0][1] + 40) * 0 + 500, n=2)
    grow(X, f"{s} .hb", tz_ - 0.3, "x", f"0 {by}")
    rise(X, f"{s} .ttl", tz_ - 0.15)
    X.tw(f'tl.from("{s} .sign", {{x:-500, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {tz_ + 0.2:.3f});')


SCENES = {"hero": hero, "stairs": stairs, "slice": slice_, "quote": quote, "rings": rings, "squares": squares, "blocks": blocks, "chain": chain}


# ---------------------------------------------------------------- effects in this style (gallery cards / fx beats)
# four of the five inks as effect grounds (no red ground for effects: grey-white on signal red is only 3.9:1 for small type)
STYLE["fx_themes"] = {
    "paper": {"bg": GW, "fg": BLK, "muted": "#3a3a3a", "accent": RED, "card": "#f1efe8", "card-fg": BLK, "line": BLK},
    "ink":   {"bg": BLK, "fg": GW, "muted": "#bdbab1", "accent": YEL, "card": "#262626", "card-fg": GW, "line": GW},
    "red":   {"bg": COB, "fg": GW, "muted": "#d0d4e6", "accent": YEL, "card": GW, "card-fg": BLK, "line": GW},
    "lemon": {"bg": YEL, "fg": BLK, "muted": "#3a3000", "accent": COB, "card": GW, "card-fg": BLK, "line": BLK},
}
FX_GROUND = {"paper": "white", "ink": "black", "red": "cobalt", "lemon": "yellow"}

FX_CSS = r"""
/* the effect's ground is flat ink + litho grain; every card is a square-cornered slab, every dot a disc or a square */
.fx { background-image:url("__GRAIN__") !important; background-size:300px !important; }
.fx .big { font-family:var(--f-zh); font-weight:900; letter-spacing:0; }
.fx .col > .sub { font-family:var(--f-body); font-weight:300; text-transform:lowercase; letter-spacing:.06em; }
.fx [class*="card"], .fx .sc .sc-c, .fx .nt .nt-cv, .fx .wp-mock, .fx .wpm-lb, .fx .nt .nt-k, .fx .nt .nt-w, .fx .sc .sc-hint { border-radius:0 !important; box-shadow:none !important; }
.fx .op .op-sweep, .fx .nt .nt-cv .rgb, .fx .nt .nt-cv .scan { display:none; }
.fx .dn .dnlg div i, .fx .dn .dnt i.sw, .fx .iu .iulg i { border-radius:0; }
.ctx.bhx .bhf { position:absolute; inset:0; pointer-events:none; }
.ctx.bhx .bhf svg { position:absolute; left:0; top:0; }
.ctx.bhx .hd { position:absolute; left:72px; right:auto; top:48px; display:flex; align-items:center; justify-content:flex-start; gap:16px; font-family:var(--f-body); font-weight:300; font-size:24px;
  letter-spacing:.06em; text-transform:lowercase; color:var(--fg); border:none; height:auto; }
.ctx.bhx .hd span { opacity:1; margin-left:0; }
.ctx.bhx .hd .fxid { background:none; color:var(--fg); font-family:var(--f-body); padding:0; }
.ctx.bhx .hd i { display:block; width:28px; height:28px; background:currentColor; }
.ctx.bhx .hd .fxid { margin-left:18px; font-weight:700; }
.ctx.bhx .cap { position:absolute; left:0; bottom:84px; top:auto; right:auto; width:900px; padding:0; text-align:left; }
.ctx.bhx .cap > span { display:block; width:900px; max-width:none; min-height:96px; padding:22px 110px 22px 72px; background:var(--bh-cap); color:var(--bh-capfg);
  font-family:var(--f-cap); font-weight:700; line-height:1.25; border-radius:0; box-shadow:none; text-shadow:none; clip-path:polygon(0 0, 900px 0, 804px 100%, 0 100%); }
.ctx.bhx .cap .em .emt { color:inherit; background:none; }
.ctx.bhx .ft { position:absolute; left:72px; bottom:32px; right:auto; font-family:var(--f-body); font-weight:300; font-size:22px; color:var(--fg); opacity:1; display:flex; gap:24px; letter-spacing:.02em; }
.ctx.bhx .ft > div { max-width:none; }
#root.v .ctx.bhx .hd { top:204px; font-size:26px; }
#root.v .ctx.bhx .cap { top:1300px; bottom:auto; }
#root.v .ctx.bhx .ft { top:1460px; bottom:auto; font-size:24px; flex-direction:column; gap:6px; max-width:828px; }
"""
def _fx_grain():
    from h9 import fx as FXM
    return FXM.noise_svg(0.9, 2, 0.1, seed=7, tint="0.5 0.5 0.5")


STYLE["css"] = FX_CSS.replace('url("__GRAIN__")', _fx_grain()) + CAP_CSS


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect card in bauhaus: header square + lowercase slug, the spoken line on the style's caption bar
    (full-bleed from the left, 45° cut), the source line, and the construction furniture in the corners only — a quarter disc
    and a heavy bar in the bottom zone that pivots / slides in, a hairline at 45° — so the effect keeps the middle of the frame."""
    P, W, H = X.portrait, X.W, X.H
    th = p.get("theme") if p.get("theme") in FX_GROUND else "paper"
    G = GROUNDS[FX_GROUND[th]]
    sty = parts["sty"] + f";--bh-cap:{G['cap']};--bh-capfg:{G['capfg']}"
    fg = G["tx"]
    accent = {"white": RED, "black": YEL, "cobalt": YEL, "yellow": COB}[FX_GROUND[th]]
    second = {"white": COB, "black": RED, "cobalt": GW, "yellow": BLK}[FX_GROUND[th]]
    if P:
        qd = f'<path class="q" d="M{W} {H}L{W - 420} {H}A420 420 0 0 1 {W} {H - 420}Z" fill="{accent}"/>'
        bar = f'<rect class="b" x="0" y="{H - 250}" width="{W}" height="24" fill="{second}"/>'
        hair = f'<line class="h" x1="0" y1="{H - 60}" x2="{560}" y2="{H - 620}" stroke="{fg}" stroke-width="4"/>'
    else:
        qd = f'<path class="q" d="M{W} {H}L{W - 300} {H}A300 300 0 0 1 {W} {H - 300}Z" fill="{accent}"/>'
        bar = f'<rect class="b" x="{W - 24 - 60}" y="0" width="24" height="{H}" fill="{second}"/>'
        hair = f'<line class="h" x1="{W - 520}" y1="{H}" x2="{W}" y2="{H - 520}" stroke="{fg}" stroke-width="4"/>'
    furn = f'<div class="bhf"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}">{qd}{bar}{hair}</svg></div>'
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "") + furn
             + f'<div class="hd"><i></i><span>{X.rich(X.channel)} · {parts["topic"]}</span><span class="fxid">{parts["fxid"]}</span></div>'
             + f'<div class="cap"><span style="font-size:{max(38, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx bhx{' photo' if parts['photo'] else ''}", 30, track=20, sty=sty)
    s = f"#{cid}c"
    q0 = f"{W} {H}"
    X.tw(f'tl.from("{s} .q", {{rotation:-90, svgOrigin:"{q0}", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .b", {{{"scaleX" if P else "scaleY"}:0, svgOrigin:"0 0", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .h", {{scale:0, svgOrigin:"{"0 " + str(H - 60) if P else str(W - 520) + " " + str(H)}", duration:{STEP:.3f}, ease:"power2.inOut"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .cap > span", {{x:-920, duration:{STEP * 1.3:.3f}, ease:"power3.out"}}, {t + 0.08:.3f});')
