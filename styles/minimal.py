"""minimal · 极简讲述 —— 观点 / 心理 / 认知类口播的「高级极简」讲述风格。十条原则提炼自一批同类讲解片的共同做法：
两种字体各司其职（无衬线正文，斜体衬线只给每屏一个重音词）、暖白纸或深炭灰底 + 纸纹 + 柔和暗角、剪影插画、
**一条细蓝线贯穿全片**、竖卡式的几种固定版式、慢而不停（每 2–4 秒有新东西）。

招牌：蓝线。每一页的线都从上一页线停下的那个点接着画（ENTRY 登记每种版式的入口点，场景把线画到下一页的入口点），
切镜头时旧线收回到这个点、新线从这里长出来——线在剪辑点上不断。线在不同页面里是地平线、钟面上走过的 15 分钟、
图表的纵轴和趋势线、柱子的轮廓、分隔线、重音词下面的线、绕住物件的圈。镜头的慢推以出口点为中心，所以推镜头时接点也不动。

场景（SCENES，全部自写，横竖屏各自排版）：object 物件居中 · year 时间轴年份 · side 插画一侧 + 文字一侧 ·
scatter 线变成坐标轴和趋势线（示意） · words 文字居中 + 重音下划线 / 划掉 · split 线是分隔线的左右对照 ·
bars 线画出柱子轮廓 · paper 真实文献卡片 + 文字 · ratio 一段线剪掉一部分 · card 物件 + 文字收尾。
剪影插画（孩子、闹钟、画笔、盘子里的棉花糖）全部是本文件里的 SVG，不用外部图片。
文字标记：*词* = 斜体衬线重音（每屏一个）；| = 换行。beat 写 "ground": "dark" 换深炭灰底。
"""
import math, random

from h9 import fit, fonts as h9fonts

PAPER, INK, MUTED, BLUE = "#efe9de", "#2b2925", "#625c51", "#2f56c4"
CHAR, BONE, BLUE_D = "#22211e", "#e9e2d4", "#86a2f2"

STYLE = {
    "name": "极简讲述", "en": "Minimal", "benchmarks": ["高级极简讲解片的十条原则", "18 世纪剪影肖像", "瑞士式留白排版"],
    "tokens": {
        "bg": PAPER, "fg": INK, "muted": MUTED, "accent": BLUE, "accent2": "#8d867a", "alert": BLUE,
        "line": "#d8d0c2", "paper": PAPER, "ink": INK, "card": "#f7f3eb", "card-fg": INK, "thread": BLUE, "sil": "#2e2b27",
        "cap-bg": "rgba(239,233,222,0)", "cap-fg": INK, "cap-size": "46px", "cap-weight": "500", "cap-pad": "0 8px",
        "cap-radius": "0", "cap-shadow": "0 0 14px rgba(239,233,222,.95), 0 0 4px rgba(239,233,222,.9)", "cap-em": BLUE, "cap-bottom": "64px",
        "punch-top": "70%", "punch-size": "60px", "punch-stroke": "0",
    },
    # two families only: a clean sans for everything, an italic serif (Garamond italic for Latin + digits, Song for 汉字) for the stressed word
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "cap": "noto-sans-sc", "latin": "noto-sans-sc", "mono": "noto-sans-sc",
              "num": "noto-sans-sc", "em": ["eb-garamond-italic", "noto-serif-sc"], "serif": ["eb-garamond-italic", "noto-serif-sc"],
              "quote": ["eb-garamond-italic", "noto-serif-sc"]},
    # effect pages: warm paper, deep charcoal, a stone ground, and the card white; the accent is always the thread blue
    "fx_themes": {
        "paper": {"bg": PAPER, "fg": INK, "muted": "#6f695e", "accent": BLUE, "card": "#f7f3eb", "card-fg": INK, "line": "#d8d0c2"},
        "ink":   {"bg": CHAR, "fg": BONE, "muted": "#a39c8f", "accent": BLUE_D, "card": "#2c2b28", "card-fg": BONE, "line": "#3a3834"},
        "red":   {"bg": "#e2ddd2", "fg": INK, "muted": "#6a645a", "accent": BLUE, "card": "#f4f0e8", "card-fg": INK, "line": "#c9c1b2"},
        "lemon": {"bg": "#f7f3eb", "fg": INK, "muted": "#6f695e", "accent": BLUE, "card": "#efe9de", "card-fg": INK, "line": "#d8d0c2"},
    },
    "motion": {"ease": "power2.out", "dur": 0.9, "stagger": 0.08, "cut": "hard", "transition": "hard", "em": "underline", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07, "fps": 8, "blend": "multiply"})],
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 90, "bottom": 40, "h": 300}, "portrait": {"left": 400, "bottom": 600, "h": 260}},
    "sfx": {"enter": ("whoosh_soft", 0.12), "draw": ("brush", 0.10), "pop": ("tick", 0.18), "tick": ("tick", 0.2), "paper": ("paper", 0.22),
            "mascot": ("whoosh_soft", 0.15), "cut": None, "transition": None, "count": ("tick", 0.15), "hit": ("tick", 0.25)},
    "css": """
.st-minimal .cap .cp { letter-spacing:.05em; }
#root.v.st-minimal { --cap-bottom:430px; --cap-size:48px; }
.st-minimal .cap .em .emt { font-family:var(--f-em); font-style:italic; font-synthesis:none; color:inherit; }
""",
}

CSS = r"""
.mn { position:absolute; inset:0; overflow:hidden; background:var(--paper); color:var(--ink); --th:var(--thread); --mut:var(--muted); --sl:var(--sil); }
.mn.dark { background:#22211e; color:#e9e2d4; --th:#86a2f2; --mut:#b5ae9f; --sl:#d9d1c1; --paper:#22211e; }
.mn .cam { position:absolute; inset:0; }
.mn .grain { position:absolute; inset:0; pointer-events:none; }
.mn .grain svg { position:absolute; inset:0; width:100%; height:100%; }
.mn .vig { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 78% 72% at 50% 46%, rgba(0,0,0,0) 52%, rgba(70,55,35,.16) 100%); }
.mn.dark .vig { background:radial-gradient(ellipse 78% 72% at 50% 46%, rgba(255,240,215,.035), rgba(0,0,0,.45) 100%); }
.mn .ln { position:absolute; white-space:nowrap; line-height:1; }
.mn .b { font-family:var(--f-body); font-weight:300; }
.mn .s { font-family:var(--f-em); font-style:italic; font-weight:300; font-synthesis:none; }
.mn .k { font-family:var(--f-body); font-weight:400; color:var(--mut); letter-spacing:.06em; }
.mn .hd { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-body); font-weight:400; color:var(--mut); letter-spacing:.16em; z-index:6; }
.mn .hd i { display:block; width:34px; height:1px; background:currentColor; opacity:.7; }
.mn .pg { position:absolute; font-family:var(--f-body); font-weight:400; color:var(--mut); letter-spacing:.14em; z-index:6; }
.mn .ft { position:absolute; font-family:var(--f-body); font-weight:400; color:var(--mut); letter-spacing:.04em; white-space:nowrap; z-index:6; }
.mn svg.thr, .mn-tail svg { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.mn .th, .mn-tail .th { fill:none; stroke:var(--th, #2f56c4); stroke-linecap:round; stroke-linejoin:round; }
.mn .art { position:absolute; overflow:visible; filter:drop-shadow(0 12px 16px rgba(50,35,20,.16)); }
.mn.dark .art { filter:drop-shadow(0 12px 18px rgba(0,0,0,.45)); }
.mn .sil { fill:var(--sl); } .mn .cut { fill:var(--paper); }
.mn .hair { position:absolute; background:var(--sl); opacity:.55; transform-origin:0 50%; }
.mn .dot { fill:var(--sl); }
.mn .tick { position:absolute; font-family:var(--f-body); font-weight:400; color:var(--mut); letter-spacing:.06em; white-space:nowrap; }
.mn .sheet { position:absolute; background:#f8f5ee; box-shadow:0 1px 0 rgba(0,0,0,.05), 0 24px 50px rgba(50,35,20,.18), 0 4px 10px rgba(50,35,20,.08); }
.mn .sheet .bar { position:absolute; height:3px; background:#d9d2c5; border-radius:2px; }
.mn .fill { position:absolute; background:color-mix(in srgb, var(--th) 10%, transparent); transform-origin:50% 100%; }
"""

# ---------------------------------------------------------------- small helpers
def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def font_file(fid):
    meta = h9fonts.REG.get(fid, {})
    return h9fonts.find(meta.get("file", "")) if meta else None


_FONTS = {}


def _cmap(fid):
    if fid not in _FONTS:
        p = font_file(fid)
        if not p: _FONTS[fid] = None
        else:
            from fontTools.ttLib import TTFont
            f = TTFont(str(p), lazy=True)
            _FONTS[fid] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    return _FONTS[fid]


def adv(s, stress=False):
    """advance width of s in em, measured from the real fonts (the stressed run: Garamond italic, Song for 汉字)."""
    chain = ["eb-garamond-italic", "noto-serif-sc"] if stress else ["noto-sans-sc"]
    w = 0.0
    for ch in fit.plain(s):
        got = None
        for fid in chain:
            c = _cmap(fid)
            if not c: continue
            name = c[0].get(ord(ch))
            if name:
                got = c[1][name][0] / c[2]; break
        w += got if got is not None else fit.gw(ch)
    return w


SK = 1.06    # the stressed run sits a touch bigger so the serif's smaller x-height matches the sans


def runs(text):
    """'a*b*c' -> [(a, False), (b, True), (c, False)]"""
    out, em = [], False
    for part in str(text).split("*"):
        if part: out.append((part, em))
        em = not em
    return out


def line_w(line, px):
    return sum(adv(s, e) * px * (SK if e else 1) for s, e in runs(line))


def textblock(X, text, x, y, px, align="center", box_w=None, lh=1.4, cls="", weight=None, color=None):
    """lines (split at |) placed absolutely; returns (html, geometry). geometry: lines [(x0, x1, top)], stress [(x0, x1, top)], px, h.
    The size shrinks until the widest line fits box_w."""
    lines = [l for l in str(text).split("|")]
    if box_w:
        widest = max(line_w(l, px) for l in lines)
        if widest > box_w: px = px * box_w / widest
    html, geo, st = [], [], []
    for k, l in enumerate(lines):
        w = line_w(l, px)
        x0 = x - w / 2 if align == "center" else (x - w if align == "right" else x)
        top = y + k * px * lh
        spans, cx = [], x0
        for s, e in runs(l):
            ww = adv(s, e) * px * (SK if e else 1)
            if e:
                st.append((cx, cx + ww, top))
                spans.append(f'<span class="s" style="font-size:{SK}em">{X.rich(s)}</span>')
            else:
                wt = weight or (300 if px >= 64 else 400)
                spans.append(f'<span class="b" style="font-weight:{wt}">{X.rich(s)}</span>')
            cx += ww
        geo.append((x0, x0 + w, top))
        sty = f"left:{x0:.0f}px; top:{top:.0f}px; font-size:{px:.0f}px" + (f"; color:{color}" if color else "")
        html.append(f'<div class="ln {cls}" style="{sty}">{"".join(spans)}</div>')
    return "".join(html), {"lines": geo, "stress": st, "px": px, "h": len(lines) * px * lh}


def under(px):
    """the underline sits this far below a line's top (line-height 1)."""
    return px * 1.16


# ---------------------------------------------------------------- the thread: one pen, many pages
class Pen:
    """an SVG path with its running length, so the drawing can be timed to points on it (marks)."""

    def __init__(self, x, y):
        self.d = [f"M{x:.1f} {y:.1f}"]
        self.x, self.y, self.L, self.marks = x, y, 0.0, {}

    def to(self, x, y):
        if abs(x - self.x) < 0.05 and abs(y - self.y) < 0.05: return self
        self.d.append(f"L{x:.1f} {y:.1f}")
        self.L += math.hypot(x - self.x, y - self.y)
        self.x, self.y = x, y
        return self

    def poly(self, pts, r=22):
        """straight runs with rounded corners."""
        P = [(self.x, self.y)] + list(pts)
        for k in range(1, len(P)):
            x, y = P[k]
            if k == len(P) - 1:
                self.to(x, y); break
            ax, ay = P[k - 1]; bx, by = P[k + 1]
            l1 = math.hypot(x - ax, y - ay); l2 = math.hypot(bx - x, by - y)
            rr = min(r, l1 / 2, l2 / 2)
            if rr < 1:
                self.to(x, y); continue
            p1 = (x + (ax - x) * rr / l1, y + (ay - y) * rr / l1)
            p2 = (x + (bx - x) * rr / l2, y + (by - y) * rr / l2)
            self.to(*p1)
            self.d.append(f"Q{x:.1f} {y:.1f} {p2[0]:.1f} {p2[1]:.1f}")
            self.L += rr * 1.6
            self.x, self.y = p2
        return self

    def curve(self, c1, c2, p):
        x0, y0 = self.x, self.y
        L, px_, py_ = 0.0, x0, y0
        for i in range(1, 25):
            u = i / 24
            a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; c = 3 * (1 - u) * u * u; e = u ** 3
            qx = a * x0 + b * c1[0] + c * c2[0] + e * p[0]; qy = a * y0 + b * c1[1] + c * c2[1] + e * p[1]
            L += math.hypot(qx - px_, qy - py_); px_, py_ = qx, qy
        self.d.append(f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p[0]:.1f} {p[1]:.1f}")
        self.L += L
        self.x, self.y = p
        return self

    def glide(self, x, y, k=0.5):
        """a soft S from here to (x, y): leaves horizontally, arrives horizontally."""
        dx = (x - self.x) * k
        return self.curve((self.x + dx, self.y), (x - dx, y), (x, y))

    def drop(self, x, y, k=0.55):
        """a soft S that leaves vertically and arrives horizontally."""
        return self.curve((self.x, self.y + (y - self.y) * k), (x - (x - self.x) * 0.4, y), (x, y))

    def ellipse(self, cx, cy, rx, ry, a0, a1):
        """along an ellipse from angle a0 to a1 (degrees, screen coords: 90 = down); moves to the start point first."""
        def P(a): return cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a))
        self.to(*P(a0))
        n = max(1, int(math.ceil(abs(a1 - a0) / 89)))
        sweep = 1 if a1 > a0 else 0
        for i in range(1, n + 1):
            a = a0 + (a1 - a0) * i / n
            x, y = P(a)
            self.d.append(f"A{rx:.1f} {ry:.1f} 0 0 {sweep} {x:.1f} {y:.1f}")
            self.x, self.y = x, y
        L, q = 0.0, P(a0)
        for i in range(1, 97):
            r = P(a0 + (a1 - a0) * i / 96); L += math.hypot(r[0] - q[0], r[1] - q[1]); q = r
        self.L += L
        return self

    def mark(self, name):
        self.marks[name] = self.L
        return self

    def f(self, name):
        return min(1.0, self.marks.get(name, self.L) / max(self.L, 1))

    def svg(self, W, H, w, cls="th", extra=""):
        return (f'<svg class="thr" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f'<path class="{cls}" d="{" ".join(self.d)}" pathLength="1" stroke-width="{w}" stroke-dasharray="1 2" stroke-dashoffset="1"{extra}/></svg>')


def tw_draw(X, sel, steps, t0=None, t1=None):
    """steps = [(t, fraction_reached, duration, ease)]: the thread grows along its path in timed strokes. Strokes never overlap
    (each starts when the previous one ends) and, given the beat window, the last one finishes before the cut.
    Animated as the dash attribute (CSS px would be rounded to whole units on a pathLength=1 path)."""
    fixed, end = [], None
    if t0 is not None and local_i(X) > 0 and steps and steps[0][0] < t0 + LEG:
        steps = [(t0 + LEG, *steps[0][1:])] + list(steps[1:])
    for t, f, dur, ease in steps:
        if end is not None and t < end: t = end
        fixed.append([t, f, dur, ease]); end = t + dur
    if t1 is not None and fixed and end > t1 - 0.02:
        a = fixed[0][0]
        k = max(0.05, (t1 - 0.02 - a) / max(end - a, 1e-3))
        for st in fixed: st[0] = a + (st[0] - a) * k; st[2] *= k
    for k, (t, f, dur, ease) in enumerate(fixed):
        if k == 0:
            X.tw(f'tl.fromTo("{sel}", {{attr:{{"stroke-dashoffset":1}}}}, {{attr:{{"stroke-dashoffset":{1 - f:.4f}}}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.3f});')
        else:
            X.tw(f'tl.to("{sel}", {{attr:{{"stroke-dashoffset":{1 - f:.4f}}}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.3f});')


def TW(X):
    return 3.4 if X.portrait else 3.0


def local_i(X):
    return X.beat["i"] - int(X.v.get("meta", {}).get("beat_offset", 0))


def next_beat(X):
    bs = X.v.get("beats", [])
    i = local_i(X)
    return bs[i + 1] if i + 1 < len(bs) else None


def exit_point(X):
    """where the next page's thread starts: the cut happens on this point."""
    nb = next_beat(X)
    if not nb: return None
    if nb.get("scene") == "fx": return fx_entry(X)
    fn = ENTRY.get(nb.get("scene"))
    return fn(X, nb) if fn else None


def thread_out(X, pen, cid, t, d, final_scale, origin, dark):
    """the seam. The page ends with the thread resting at its last point (the camera pushes in around that point, so it
    does not move). After the cut, on the new, still empty page: the old thread is pulled back into that point, a short
    leg glides from it to where the new page's thread starts, and is pulled in behind it as the new one grows."""
    E = exit_point(X)
    if not E: return
    W, H = X.W, X.H
    ox, oy = origin
    leg = Pen(ox, oy)
    if math.hypot(E[0] - ox, E[1] - oy) > 2:
        if abs(E[1] - oy) < 6 or abs(E[0] - ox) < 6: leg.to(*E)
        elif E[0] <= M(X) + 12 and ox - E[0] > 300:     # back to the left margin: round the bottom band, not across the page
            by = 1400 if X.portrait else H - 34
            leg.poly([(ox, max(by, oy)), (E[0], max(by, oy)), E], 40)
        else: leg.glide(*E, 0.55)
    tid = f"{cid}tl"
    tr = f'transform="translate({ox:.1f} {oy:.1f}) scale({final_scale}) translate({-ox:.1f} {-oy:.1f})"'
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><g {tr}><path class="th old" d="{" ".join(pen.d)}" pathLength="1" stroke-width="{TW(X)}" '
           f'stroke-dasharray="1 2" stroke-dashoffset="0"/></g>'
           f'<path class="th leg" d="{" ".join(leg.d)}" pathLength="1" stroke-width="{TW(X)}" stroke-dasharray="1 2" stroke-dashoffset="1"/></svg>')
    X.clip(tid, t + d, 0.62, svg, "mn-tail", 15, track=26 + local_i(X) % 2, sty=f"--th:{BLUE_D if next_dark(X) else BLUE}")
    s = f"#{tid}"
    X.tw(f'tl.set("{s} .old", {{opacity:0}}, {t + d:.3f});')
    X.tw(f'tl.fromTo("{s} .leg", {{attr:{{"stroke-dashoffset":1}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:0.26, ease:"power2.inOut"}}, {t + d:.3f});')
    X.tw(f'tl.to("{s} .leg", {{attr:{{"stroke-dashoffset":-0.999}}, duration:0.3, ease:"power2.inOut"}}, {t + d + 0.28:.3f});')


def next_dark(X):
    nb = next_beat(X)
    return bool(nb and (nb.get("ground") == "dark" or (nb.get("scene") == "fx" and nb.get("theme") == "ink")))


LEG = 0.28     # a page's own thread starts growing once the leg from the previous page has arrived


# ---------------------------------------------------------------- paper, page furniture
def grain(X, cid, dark):
    W, H = X.W, X.H
    r = random.Random(17)
    tint = "0 0 0 0 .92  0 0 0 0 .88  0 0 0 0 .8  0 0 0 .07 0" if dark else "0 0 0 0 .33  0 0 0 0 .27  0 0 0 0 .2  0 0 0 .16 0"
    fc = "rgba(236,228,210,.035)" if dark else "rgba(110,90,60,.06)"
    fib = "".join(f'<path d="M{r.uniform(0, W):.0f} {r.uniform(0, H):.0f} q {r.uniform(-50, 50):.0f} {r.uniform(-20, 20):.0f} {r.uniform(-130, 130):.0f} {r.uniform(-40, 40):.0f}" '
                  f'stroke="{fc}" stroke-width="{r.uniform(.6, 1.2):.1f}" fill="none"/>' for _ in range(40))
    return (f'<div class="grain"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><defs><filter id="{cid}gr"><feTurbulence type="fractalNoise" baseFrequency="0.78" numOctaves="3" seed="11"/>'
            f'<feColorMatrix type="matrix" values="{tint}"/></filter>'
            f'<filter id="{cid}tx" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency="1.1" numOctaves="2" seed="4" result="n"/>'
            f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.4 1.25" result="a"/><feComposite in="SourceGraphic" in2="a" operator="in"/></filter>'
            f'</defs><rect width="{W}" height="{H}" filter="url(#{cid}gr)"/>{fib}</svg></div><div class="vig"></div>')


def furn(X, b, cid, t, d, inner, origin, dark=False, push=1.035):
    """one page: ground + grain + vignette, a quiet header (channel · section, page number), the source line, and the camera
    that pushes in slowly around the exit point (so the seam stays put)."""
    X.css("minimal", CSS)
    P = X.portrait
    meta = X.v.get("meta", {})
    sec = meta.get("section", "认知")
    i, n = X.beat["i"], X.beat["n"]
    X.used_text.update(sec + "" + X.channel + "来源 0123456789/·")
    hx, hy, fs = (64, 206, 26) if P else (96, 52, 22)
    hd = (f'<div class="hd" style="left:{hx}px; top:{hy}px; font-size:{fs}px"><span>{X.rich(X.channel)}</span><i></i><span>{X.rich(sec)}</span></div>'
          f'<div class="pg" style="right:{hx}px; top:{hy}px; font-size:{fs}px">{i + 1:02d} / {n:02d}</div>')
    ft = ""
    if b.get("src"):
        fy = 1528 if P else 1030
        ft = (f'<div class="ft" style="left:{hx}px; top:{fy}px; width:{X.W - 2 * hx}px; white-space:normal; line-height:1.45; '
              f'font-size:{SP(X)}px">来源 · {X.rich(b["src"])}</div>')
    ox, oy = origin
    html = (f'<div class="mn{" dark" if dark else ""}">{grain(X, cid, dark)}'
            f'<div class="cam" style="transform-origin:{ox:.0f}px {oy:.0f}px">{inner}</div>{hd}{ft}</div>')
    X.clip(cid, t, d, html, "scene", 2)
    X.tw(f'tl.fromTo("#{cid} .cam", {{scale:1}}, {{scale:{push}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .hd, #{cid} .pg", {{opacity:0, duration:0.6, ease:"power1.out"}}, {t + 0.1:.3f});')
    if ft: X.tw(f'tl.from("#{cid} .ft", {{opacity:0, y:6, duration:0.7, ease:"power2.out"}}, {t + 0.8:.3f});')
    if dark:     # captions turn bone-white over a charcoal page and back afterwards
        X.tw(f'tl.set("#root", {{"--cap-fg":"{BONE}", "--cap-shadow":"0 0 14px rgba(34,33,30,.95), 0 0 4px rgba(34,33,30,.9)"}}, {t:.3f});')
        X.tw(f'tl.set("#root", {{"--cap-fg":"{INK}", "--cap-shadow":"0 0 14px rgba(239,233,222,.95), 0 0 4px rgba(239,233,222,.9)"}}, {t + d:.3f});')


def reveal(X, sel, t, dur=0.9, y=14, stagger=0.0):
    """the house entrance: a soft focus pull + a short rise."""
    X.tw(f'tl.from("{sel}", {{opacity:0, y:{y}, filter:"blur(8px)", duration:{dur:.2f}, ease:"power2.out", stagger:{stagger}}}, {t:.3f});')


def stress_in(X, sel, t):
    """the stressed word arrives a beat later and a little slower — the one moment on the page."""
    X.tw(f'tl.from("{sel} .s", {{opacity:0, y:10, filter:"blur(10px)", duration:1.1, ease:"power3.out"}}, {t:.3f});')


# ---------------------------------------------------------------- silhouettes (cut paper, code-drawn)
CHILD = """<g class="sil">
<path d="M66 156 C62 142 80 138 84 152 L96 298 L252 298 L252 312 L240 312 L248 470 L234 470 L226 312 L104 312 L88 470 L74 470 L84 310 Z"/>
<path d="M58 168 C70 154 98 154 104 168 L102 182 C92 172 72 172 62 182 Z"/>
<circle cx="178" cy="110" r="56"/>
<path d="M206 62 C228 70 238 88 238 104 C238 110 241 116 245 122 C247 126 243 129 238 129 C240 133 239 137 236 139 C238 143 236 148 231 152 C222 164 204 168 192 160 Z"/>
<path d="M120 120 C114 74 146 50 182 52 C214 53 236 70 238 92 C226 84 214 84 206 90 C196 100 188 118 184 136 C178 160 162 172 136 168 C124 156 120 138 120 120 Z"/>
<path d="M126 74 C110 56 94 58 94 70 C94 82 112 84 124 82 C112 92 104 106 114 110 C124 112 130 96 132 84 Z"/>
<path d="M182 150 L208 150 L210 186 L180 186 Z"/>
<path d="M152 196 C164 182 206 180 222 192 C232 216 238 256 240 292 L146 300 C136 262 138 224 152 196 Z"/>
<path d="M142 266 L268 260 C282 260 290 272 288 288 L286 304 L142 312 Z"/>
<path d="M256 286 L288 286 L292 394 L260 396 Z"/>
<path d="M256 388 L294 388 C308 390 316 400 310 410 L256 412 Z"/>
<path d="M182 200 C200 194 218 204 222 222 L230 252 L300 236 C312 234 318 248 308 254 L230 278 C214 282 202 274 199 262 L184 220 Z"/>
<path d="M286 250 L424 250 L424 262 L412 262 L414 470 L400 470 L398 262 L302 262 L304 470 L290 470 L288 262 Z"/>
<ellipse cx="356" cy="249" rx="40" ry="6"/>
</g>
<path d="M342 230 C342 223 370 223 370 230 L370 241 C370 248 342 248 342 241 Z" fill="#f3eee4"/>
<ellipse cx="356" cy="228.5" rx="13.5" ry="3.6" fill="#fffdf7"/>"""


def _clock(k=0):
    ticks = []
    for j in range(12):
        a = math.radians(j * 30)
        r0, w = (56, 6) if j % 3 == 0 else (63, 3)
        ticks.append(f'<line x1="{120 + r0 * math.sin(a):.1f}" y1="{136 - r0 * math.cos(a):.1f}" x2="{120 + 74 * math.sin(a):.1f}" y2="{136 - 74 * math.cos(a):.1f}" '
                     f'style="stroke:var(--sl)" stroke-width="{w}"/>')
    return (f'<g class="sil"><path d="M40 74 C40 34 78 14 104 30 Z" transform="rotate(-8 70 60)"/><path d="M200 74 C200 34 162 14 136 30 Z" transform="rotate(8 170 60)"/>'
            f'<rect x="114" y="12" width="12" height="24" rx="3"/><circle cx="120" cy="136" r="96"/>'
            f'<path d="M58 214 L36 252 L52 252 L76 222 Z"/><path d="M182 214 L204 252 L188 252 L164 222 Z"/></g>'
            f'<circle cx="120" cy="136" r="80" fill="#f4efe6"/>{"".join(ticks)}'
            f'<g class="sil"><path class="hm" d="M117 136 L120 84 L123 136 Z"/><path class="hh" d="M120 133 L156 136 L120 139 Z"/><circle cx="120" cy="136" r="6"/></g>')


def _pencils(empty=False):
    shapes = [(-22, 90, 50), (-4, 70, 30), (16, 84, 44)]
    if empty:     # where the promised set should be: only its outline, dashed
        return "".join(f'<g transform="rotate({a} 150 280)"><path d="M136 {y0} L150 {y1} L164 {y0} L164 270 L136 270 Z" fill="none" '
                       f'style="stroke:var(--sl)" stroke-width="3" stroke-dasharray="9 9" opacity=".6"/></g>' for a, y0, y1 in shapes)
    body = "".join(f'<g transform="rotate({a} 150 280)"><path d="M136 {y0} L150 {y1} L164 {y0} L164 270 L136 270 Z"/></g>' for a, y0, y1 in shapes)
    bands = "".join(f'<g transform="rotate({a} 150 280)"><rect x="136" y="{y0 + 6}" width="28" height="5"/></g>' for a, y0, _ in shapes)
    return f'<g class="sil">{body}</g><g class="cut">{bands}</g>'


def _plate(n=1, k=0):
    """a dark glazed saucer with soft marshmallows on it: the 'real object' of this film."""
    defs = (f'<defs><filter id="sf{k}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>'
            f'<linearGradient id="sd{k}" x1="0" x2="1"><stop offset="0" stop-color="#d4ccbe"/><stop offset=".32" stop-color="#f8f4ec"/><stop offset=".68" stop-color="#ece6da"/><stop offset="1" stop-color="#c4bcad"/></linearGradient>'
            f'<radialGradient id="tp{k}" cx=".42" cy=".38" r=".75"><stop offset="0" stop-color="#fffdf9"/><stop offset="1" stop-color="#e6dfd2"/></radialGradient>'
            f'<radialGradient id="gl{k}" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#57524a"/><stop offset="1" stop-color="#2c2925"/></radialGradient></defs>')
    out = [defs, f'<ellipse cx="230" cy="222" rx="206" ry="50" fill="rgba(45,32,18,.28)" filter="url(#sf{k})"/>',
           f'<ellipse class="sil" cx="230" cy="208" rx="200" ry="46"/>', f'<ellipse cx="230" cy="205" rx="146" ry="29" fill="url(#gl{k})"/>']
    spots = [(230, 0)] if n == 1 else [(176, 0), (292, 8)]
    for cx, dy in spots:
        w, h = 104, 58
        rx, ry = w / 2, w * 0.24
        top = 200 + dy - h - ry * 0.4
        out.append(f'<ellipse cx="{cx}" cy="{200 + dy + 4}" rx="{rx * 1.05}" ry="{ry * 0.8}" fill="rgba(20,14,8,.35)" filter="url(#sf{k})"/>'
                   f'<path d="M{cx - rx} {top + 6} Q{cx - rx - 1} {top + h * .6} {cx - rx + 5} {top + h} A{rx - 5} {ry * .9} 0 0 0 {cx + rx - 5} {top + h} '
                   f'Q{cx + rx + 1} {top + h * .6} {cx + rx} {top + 6} Z" fill="url(#sd{k})"/>'
                   f'<ellipse cx="{cx}" cy="{top + 4}" rx="{rx}" ry="{ry}" fill="url(#tp{k})"/>')
    return "".join(out)


ART = {   # name: (view w, view h, svg maker, anchors in view coords)
    "child": (430, 480, lambda k: CHILD, {"floor": (0, 470), "floor_r": (430, 470), "plate": (356, 236), "head": (178, 110)}),
    "clock": (240, 260, _clock, {"c": (120, 136), "r": (80, 0)}),
    "pencils": (300, 300, lambda k: _pencils(), {"c": (150, 168), "r": (150, 0)}),
    "pencils_empty": (300, 300, lambda k: _pencils(True), {"c": (150, 168), "r": (150, 0)}),
    "mallow1": (460, 280, lambda k: _plate(1, k), {"c": (230, 176), "r": (232, 96)}),
    "mallow2": (460, 280, lambda k: _plate(2, k), {"c": (230, 176), "r": (232, 96)}),
}


def art(X, name, x, y, w, cls=""):
    """place a silhouette with its top-left at (x, y), w px wide. Returns (html, anchor(px) function, height)."""
    vw, vh, mk, an = ART[name]
    k = w / vw
    uid = X.uid("art")
    html = f'<svg class="art {cls}" style="left:{x:.0f}px; top:{y:.0f}px" width="{w:.0f}" height="{vh * k:.0f}" viewBox="0 0 {vw} {vh}">{mk(uid)}</svg>'

    def A(key):
        ax, ay = an[key]
        return (x + ax * k, y + ay * k) if key not in ("r",) else (ax * k, ay * k)
    return html, A, vh * k


def first(X, sel, t, dur=0.6):
    """the page's main element on a cut: already on screen in the first frame (40 %, soft), settling in 0.6 s, so no frame
    of the film is empty paper."""
    X.tw(f'tl.from("{sel}", {{opacity:0.4, y:8, filter:"blur(4px)", duration:{dur:.2f}, ease:"power2.out"}}, {t:.3f});')


def art_in(X, sel, t, dur=1.2):
    """cut paper laid down: a slow rise out of soft focus, settling."""
    X.tw(f'tl.from("{sel}", {{opacity:0, y:26, scale:0.97, filter:"blur(10px)", transformOrigin:"50% 100%", duration:{dur:.2f}, ease:"power3.out"}}, {t:.3f});')


# ---------------------------------------------------------------- layouts (pure: the same numbers for ENTRY and for the scene)
def M(X): return 80 if X.portrait else 128


def LP(X): return 38 if X.portrait else 36       # labels: axis names, units, row keys, notes
def KP(X): return 42 if X.portrait else 40       # kickers above a headline
def SP(X): return 24 if X.portrait else 22       # source lines, journal meta


def L_object(X, b):
    P, W, H = X.portrait, X.W, X.H
    aw = 920 if P else 640
    vw, vh = ART[b.get("art", "mallow1")][:2]
    ah = vh * aw / vw
    ay = (720 if P else 420) - ah / 2
    ax = (W - aw) / 2
    c = (ax + ART[b.get("art", "mallow1")][3]["c"][0] * aw / vw, ay + ART[b.get("art", "mallow1")][3]["c"][1] * aw / vw)
    r = ART[b.get("art", "mallow1")][3]["r"]
    rx, ry = min(r[0] * aw / vw * 1.04, W / 2 - M(X) - 24), (r[1] or r[0]) * aw / vw * 1.25
    ty = ay + ah + (60 if P else 40)
    return {"ax": ax, "ay": ay, "aw": aw, "c": c, "rx": rx, "ry": ry, "ty": ty, "px": 92 if P else 60,
            "entry": (M(X), c[1])}


def L_year(X, b):
    P, W = X.portrait, X.W
    m = M(X)
    ay = 860 if P else 720
    y0, y1 = b.get("axis", [1960, 2025])
    def xa(yr): return m + 40 + (yr - y0) / (y1 - y0) * (W - 2 * m - 80)
    return {"ay": ay, "xa": xa, "y0": y0, "y1": y1, "entry": (m, ay)}


def L_side(X, b):
    P, W, H = X.portrait, X.W, X.H
    name = b.get("art", "child")
    vw, vh = ART[name][:2]
    if P:
        aw = 660 if name == "child" else 560
        ax, ay = (80 if name == "child" else (W - aw) / 2 - 100), (330 if name == "child" else 350)
        tx, ty = 80, (1100 if name == "child" else 950)
    else:
        aw = 620 if name == "child" else 520
        ax, ay = 170, 540 - vh * aw / vw / 2
        tx, ty = 1010, 330
    ah = vh * aw / vw
    floor = ay + (470 / 480 * ah if name == "child" else ah * 0.94)
    ent = (M(X), floor) if name == "child" else (M(X), ay + ART[name][3]["c"][1] * aw / vw)
    return {"ax": ax, "ay": ay, "aw": aw, "ah": ah, "tx": tx, "ty": ty, "floor": floor, "entry": ent}


def L_scatter(X, b):
    P = X.portrait
    x0, x1, y0, y1 = (160, 970, 480, 1270) if P else (520, 1560, 330, 840)
    return {"x0": x0, "x1": x1, "y0": y0, "y1": y1, "entry": (x0, y0 - (70 if P else 60))}


def L_words(X, b):
    P, W = X.portrait, X.W
    px = b.get("px") or (124 if P else 112)
    lines = str(b.get("text", "")).split("|")
    box = W - 2 * M(X) - (40 if P else 300)
    widest = max(line_w(l, px) for l in lines)
    if widest > box: px = px * box / widest
    lh = 1.42
    h = len(lines) * px * lh
    top = (830 if P else 520) - h / 2
    # where the stressed run sits (first one), for the entry drop
    sx = W / 2
    for k, l in enumerate(lines):
        w = line_w(l, px); x0 = W / 2 - w / 2; cx = x0
        for s, e in runs(l):
            ww = adv(s, e) * px * (SK if e else 1)
            if e: return {"px": px, "top": top, "lh": lh, "box": box, "sx": cx, "ex": cx + ww, "sy": top + k * px * lh,
                          "entry": (cx, 300 if P else 170)}
            cx += ww
    return {"px": px, "top": top, "lh": lh, "box": box, "sx": sx - 40, "ex": sx + 40, "sy": top, "entry": (sx, 300 if P else 170)}


def L_split(X, b):
    P, W = X.portrait, X.W
    if P: return {"dv": 850, "entry": (M(X), 850)}
    return {"dv": W / 2, "entry": (W / 2, 168)}


def L_bars(X, b):
    P, W = X.portrait, X.W
    m = M(X)
    if P: return {"base": 1270, "xs": [320, 760], "bw": 250, "hmax": 690, "entry": (m, 1270), "x_end": W - m}
    return {"base": 830, "xs": [770, 1170], "bw": 230, "hmax": 520, "entry": (m, 830), "x_end": W - m}


def L_paper(X, b):
    P, W = X.portrait, X.W
    m = M(X)
    if P: return {"tx": m + 16, "ty": 320, "card": (90, 680, 900, 700), "entry": (m, 320 + 260)}
    return {"tx": 190, "ty": 360, "card": (1010, 210, 720, 640), "entry": (m, 360 + 270)}


def L_ratio(X, b):
    P, W = X.portrait, X.W
    m = M(X)
    if b.get("ref"):
        if P: return {"ky": 320, "yr": 720, "y": 1030, "x0": m + 20, "x1": W - m - 20, "entry": (m, 1030)}
        return {"ky": 160, "yr": 480, "y": 720, "x0": 300, "x1": 1620, "entry": (m, 720)}
    if P: return {"ky": 320, "yr": 0, "y": 900, "x0": m + 40, "x1": W - m - 40, "entry": (m, 900)}
    return {"ky": 160, "yr": 0, "y": 610, "x0": 300, "x1": 1620, "entry": (m, 610)}


def L_card(X, b):
    P, W = X.portrait, X.W
    if P: return {"tx": W / 2, "ty": 360, "ax": 160, "ay": 830, "aw": 760, "entry": (M(X), 360 + 230)}
    return {"tx": 500, "ty": 330, "ax": 980, "ay": 300, "aw": 820, "entry": (M(X), 330 + 280)}


def fx_entry(X):
    return (64, 300) if X.portrait else (96, 120)


# ---------------------------------------------------------------- scenes
def gutter(X):
    """the free band between the content and the captions, where the thread travels to the next page's start."""
    return 1290 if X.portrait else 905


def _end(X, pen, E=None, last_t=None, d_t=None):
    """a page's thread ends where its job ends; the way to the next page is drawn after the cut (thread_out)."""
    pen.mark("end")


def object_scene(b, X, t, d, cid):
    """illustration-centred: the object on its own, the thread comes in and circles it, then drops under the one word."""
    P, W, H = X.portrait, X.W, X.H
    g = L_object(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    a_html, A, ah = art(X, b.get("art", "mallow1"), g["ax"], g["ay"], g["aw"], "obj")
    kick = b.get("kicker", "")
    k_html = f'<div class="ln k kk" style="left:0; right:0; text-align:center; top:{(330 if P else 150)}px; font-size:{KP(X)}px">{X.rich(kick)}</div>' if kick else ""
    t_html, tg = textblock(X, b.get("text", ""), W / 2, g["ty"], g["px"], box_w=W - 2 * M(X) - 60)
    cx, cy = g["c"]
    t_wrap = T(X, b, "at_wrap", t, t + 0.9)
    t_text = T(X, b, "at_text", t, t + min(1.8, d * 0.45))
    pen = Pen(*g["entry"])
    pen.mark("in")
    pen.ellipse(cx, cy, g["rx"], g["ry"], 180, 540).mark("loop")
    if tg["stress"]:
        sx, ex, top = tg["stress"][0]
        uy = top + under(tg["px"])
        pen.poly([(pen.x, uy), (ex, uy)], 40).mark("toword")
        pen.mark("word")
    _end(X, pen, E, t, d)
    inner = a_html + k_html + f'<div class="tx">{t_html}</div>' + pen.svg(W, H, TW(X))
    furn(X, b, cid, t, d, inner, (pen.x, pen.y), dark)
    s = f"#{cid}"
    first(X, f"{s} .obj", t)
    if kick: reveal(X, f"{s} .kk", t + 0.2)
    reveal(X, f"{s} .tx .ln", t_text, 0.9)
    stress_in(X, f"{s} .tx", t_text + 0.35)
    steps = [(t + 0.05, pen.f("in"), 0.6, "power1.in"), (t_wrap, pen.f("loop"), 1.5, "power2.inOut")]
    if tg["stress"]:
        steps.append((max(t_text + 0.5, t_wrap + 1.5), pen.f("word"), 0.9, "power2.inOut"))
    if E: steps.append((t + d - 0.9, 1.0, 0.85, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, (pen.x, pen.y), dark)


def year_scene(b, X, t, d, cid):
    """the thread becomes a time axis; a node opens on the year, which is the page's one italic word."""
    P, W, H = X.portrait, X.W, X.H
    g = L_year(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    yr = int(b.get("year", 1972))
    ay, xa = g["ay"], g["xa"]
    nx = xa(yr)
    m = M(X)
    ticks = []
    for dec in range((g["y0"] // 10 + 1) * 10, g["y1"], 10):
        x = xa(dec)
        ticks.append(f'<div class="hair tk" style="left:{x:.0f}px; top:{ay - 9}px; width:1px; height:18px"></div>'
                     f'<div class="tick tkl" style="left:{x - 50:.0f}px; width:100px; text-align:center; top:{ay + 22}px; font-size:{26 if P else 22}px">{dec}</div>')
    prev = "".join(f'<svg class="thr pv" width="{W}" height="{H}"><circle cx="{xa(p):.0f}" cy="{ay}" r="7" style="fill:var(--mut)" opacity=".7"/></svg>'
                   f'<div class="tick pv" style="left:{xa(p) - 60:.0f}px; width:120px; text-align:center; top:{ay - LP(X) - 22}px; font-size:{LP(X)}px">{p}</div>' for p in b.get("prev", []))
    ypx = 300 if P else 270
    yx = min(max(nx, m + ypx * 1.2), W - m - ypx * 1.2)
    y_html, yg = textblock(X, f"*{yr}*", yx, ay - ypx * 1.18 - 40, ypx)
    place, who = b.get("place", ""), b.get("who", "")
    lx = W / 2 if P else min(max(nx, m + 360), W - m - 360)
    p_html, _ = textblock(X, place, lx, ay + (96 if P else 84), 54 if P else 44, box_w=W - 2 * m)
    w_html = f'<div class="ln k wh" style="left:0; right:0; text-align:center; top:{ay + (186 if P else 150)}px; font-size:{LP(X) - 2}px">{X.rich(who)}</div>' if who else ""
    a_html = ""
    if b.get("art"):      # the second event: what was on the table that year
        an = b["art"]
        vw_, vh_ = ART[an][:2]
        if P:
            aw_ = 420 if vw_ > vh_ else 280
            a_html = art(X, an, (W - aw_) / 2, ay + 270, aw_, "ya")[0]
        else:
            aw_ = 420 if vw_ > vh_ else 300
            ax_ = W - m - aw_ - 40 if yx < W / 2 else m + 60
            a_html = art(X, an, ax_, ay - 140 - vh_ * aw_ / vw_, aw_, "ya")[0]
    if not P: w_html = w_html.replace("left:0; right:0;", f"left:{lx - 500:.0f}px; width:1000px;")
    pen = Pen(*g["entry"])
    pen.to(nx - 18, ay).mark("node0")
    pen.ellipse(nx, ay, 18, 18, 180, 540).mark("node")
    pen.to(W - m - (0 if E else 0), ay).mark("axis")
    inner = (f'<div class="hair ax" style="left:{m}px; top:{ay}px; width:{W - 2 * m}px; height:1px; opacity:.25"></div>' + "".join(ticks) + prev
             + f'<div class="yr">{y_html}</div><div class="pl">{p_html}</div>{w_html}{a_html}' + pen.svg(W, H, TW(X)))
    furn(X, b, cid, t, d, inner, (pen.x, pen.y), dark)
    s = f"#{cid}"
    t_year = T(X, b, "at_year", t, t + 0.6)
    X.tw(f'tl.from("{s} .ax", {{scaleX:0, duration:0.6, ease:"power2.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .tk, {s} .tkl", {{opacity:0, duration:0.4, stagger:0.04}}, {t + 0.1:.3f});')
    if b.get("prev"): reveal(X, f"{s} .pv", t + 0.2, 0.6, 0)
    t_year = min(t_year, t + 0.1)       # the year is the page: on screen before the thread arrives
    first(X, f"{s} .yr .s", t)
    reveal(X, f"{s} .pl .ln", t + 0.9)
    if who: reveal(X, f"{s} .wh", t + 1.4)
    if a_html: art_in(X, f"{s} .ya", T(X, b, "at_art", t, t + d * 0.5), 1.0)
    steps = [(t + 0.05, pen.f("node0"), max(0.7, t_year - t), "power2.inOut"), (t_year + 0.1, pen.f("node"), 0.8, "power2.out")]
    steps.append((t_year + 1.0, pen.f("axis"), max(0.8, d - (t_year - t) - 1.9), "sine.inOut"))
    if E: steps.append((t + d - 0.7, 1.0, 0.65, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    X.sfx(t_year, "tick")
    thread_out(X, pen, cid, t, d, 1.035, (pen.x, pen.y), dark)


def side_scene(b, X, t, d, cid):
    """illustration on one side, text on the other. With art "child" the thread is the floor and then runs round the
    clock face for the 15 minutes; otherwise it circles the object. Rows = [{k, v}] (v may hold the one *stress*)."""
    P, W, H = X.portrait, X.W, X.H
    g = L_side(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    name = b.get("art", "child")
    a_html, A, ah = art(X, name, g["ax"], g["ay"], g["aw"], "sa")
    m = M(X)
    pen = Pen(*g["entry"])
    parts = [a_html]
    t_rows = [T(X, b, f"at_{k}", t, t + 0.9 + k * 1.2) for k in range(len(b.get("rows", [])))]
    clock = b.get("clock")
    if name == "child":
        fr = A("floor_r")
        pen.to(fr[0] + 40, g["floor"]).mark("floor")
    else:
        c = A("c"); r = A("r")[0] * 0.98
        pen.to(c[0] - r - 40, c[1]).mark("floor")
        pen.ellipse(c[0], c[1], r, r * 0.95, 180, 520).mark("wrap")
    if clock:
        cw = 210 if P else 220
        cxp, cyp = (W - m - cw, 380) if P else (W - m - cw - 40, 300)
        c_html, CA, ch = art(X, "clock", cxp, cyp, cw, "ck")
        parts.append(c_html)
        cc = CA("c"); cr = 80 * cw / 240 * 0.82
        if P: pen.drop(cc[0], cc[1] - cr - 2)
        else: pen.poly([(W - m + 10, pen.y), (W - m + 10, cc[1] - cr - 80), (cc[0], cc[1] - cr - 80), (cc[0], cc[1] - cr - 2)], 40)
        pen.mark("clock0")
        pen.ellipse(cc[0], cc[1], cr, cr, 270, 360).mark("clock")
    # rows of text
    rows = b.get("rows", [])
    stress = None
    if rows:
        for k, row in enumerate(rows):
            if P:
                cw_ = (W - 2 * m) / len(rows)
                x, y = m + k * cw_, g["ty"]
            else:
                x, y = g["tx"], g["ty"] + 40 + k * 230
            kh = f'<div class="ln k rk{k}" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{LP(X)}px">{X.rich(row.get("k", ""))}</div>'
            vh, vg = textblock(X, row.get("v", ""), x, y + 54, 104 if P else 112, align="left", cls=f"rv{k}")
            parts.append(kh + vh)
            if vg["stress"] and not stress: stress = (vg["stress"][0], vg["px"], k)
    else:
        kick = b.get("kicker", "")
        if kick: parts.append(f'<div class="ln k rk0" style="left:{g["tx"]:.0f}px; top:{g["ty"] + (0 if P else 60):.0f}px; font-size:30px">{X.rich(kick)}</div>')
        th, tg = textblock(X, b.get("text", ""), g["tx"], g["ty"] + (60 if P else 130), 96 if P else 100, align="left", cls="rv0",
                           box_w=(W - 2 * m) if P else (W - g["tx"] - m))
        parts.append(th)
        if b.get("sub"):
            parts.append(f'<div class="ln k rs" style="left:{g["tx"]:.0f}px; top:{g["ty"] + (60 if P else 130) + tg["h"] + 20:.0f}px; font-size:{LP(X)}px; letter-spacing:.06em">{X.rich(b["sub"])}</div>')
        if tg["stress"]: stress = (tg["stress"][0], tg["px"], 0)
    if stress:
        (sx, ex, top), px, k = stress
        uy = top + under(px)
        if clock and not P: pen.poly([(pen.x, uy), (sx, uy)], 40)
        elif clock or P and name == "child": pen.drop(sx, uy)
        elif P: pen.poly([(g["tx"] - 44, pen.y), (g["tx"] - 44, uy), (sx, uy)], 40)
        else: pen.poly([(pen.x, uy)], 40)
        pen.mark("toword"); pen.to(ex, uy).mark("word")
    _end(X, pen, E, t, d)
    parts.append(pen.svg(W, H, TW(X)))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, "".join(parts), origin, dark)
    s = f"#{cid}"
    first(X, f"{s} .sa", t)
    if clock:
        art_in(X, f"{s} .ck", t + 0.2, 0.8)
        X.tw(f'tl.fromTo("{s} .ck .hm", {{rotation:0, svgOrigin:"120 136"}}, {{rotation:90, svgOrigin:"120 136", duration:{max(1.5, d - 1.6):.2f}, ease:"power1.inOut"}}, {t + 1.0:.3f});')
    for k in range(max(1, len(rows))):
        tk = t_rows[k] if rows else T(X, b, "at_text", t, t + 0.9)
        reveal(X, f"{s} .rk{k}", tk - 0.1, 0.7)
        reveal(X, f"{s} .rv{k}", tk, 0.9)
    if not rows and b.get("sub"): reveal(X, f"{s} .rs", T(X, b, "at_text", t, t + 0.9) + 0.6)
    t_last = t_rows[-1] if rows else T(X, b, "at_text", t, t + 0.9)
    steps = [(t + 0.1, pen.f("floor"), 1.2 if name == "child" else 0.6, "power2.inOut")]
    if name != "child": steps.append((t + 0.7, pen.f("wrap"), 1.3, "power2.inOut"))
    if clock:
        t_ck = T(X, b, "at_clock", t, t + 1.4)
        steps.append((max(steps[-1][0] + steps[-1][2], t_ck - 0.6), pen.f("clock0"), 0.6, "power1.inOut"))
        steps.append((max(t_ck, steps[-1][0] + 0.6), pen.f("clock"), 1.0, "power2.inOut"))
    if stress:
        ts = max(t_last + 0.3, steps[-1][0] + steps[-1][2])
        steps.append((ts, pen.f("word"), 0.9, "power2.inOut"))
    if E: steps.append((max(t + d - 0.8, steps[-1][0] + steps[-1][2]), 1.0, 0.7, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


def scatter_scene(b, X, t, d, cid):
    """the thread draws the y axis and then the trend through the dots. A schematic: it says so on the page."""
    P, W, H = X.portrait, X.W, X.H
    g = L_scatter(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    x0, x1, y0, y1 = g["x0"], g["x1"], g["y0"], g["y1"]
    r = random.Random(int(b.get("seed", 5)))
    n = int(b.get("n", 26))
    dots = []
    for k in range(n):
        u = (k + r.uniform(0.1, 0.9)) / n
        v = 0.12 + 0.62 * u + r.gauss(0, 0.11)
        v = min(0.95, max(0.04, v))
        dots.append((x0 + 30 + u * (x1 - x0 - 60), y1 - v * (y1 - y0)))
    dsvg = "".join(f'<circle class="dot dt" cx="{x:.0f}" cy="{y:.0f}" r="{9 if P else 9}"/>' for x, y in dots)
    lab_px = 30 if P else 28
    ylab, yg = textblock(X, b.get("ylab", ""), x0 + 26, y0 - (78 if P else 70), lab_px + 8, align="left", cls="yl")
    xlab = f'<div class="ln k xl" style="left:{x1 - 400:.0f}px; width:400px; text-align:right; top:{y1 + 28:.0f}px; font-size:{lab_px}px">{X.rich(b.get("xlab", ""))}</div>'
    kick = b.get("kicker", "")
    k_html, kg = textblock(X, kick, x0 if P else M(X) + 40, (300 if P else 150), 52 if P else 50, align="left", cls="kk") if kick else ("", None)
    note = f'<div class="ln k nt" style="left:{x1 - 400:.0f}px; width:400px; text-align:right; top:{y0 - 40:.0f}px; font-size:{SP(X) + 2}px">{X.rich(b.get("note", "示意"))}</div>'
    co = b.get("callouts") or []      # the second event: the two ends of the cloud, named
    co_html = ""
    if co:
        lo = min(dots[:n // 3], key=lambda q: -q[1])
        hi = min(dots[-n // 3:], key=lambda q: q[1])
        for k, ((qx, qy), txt) in enumerate(zip((lo, hi), co[:2])):
            lx_ = qx + 34 if k == 0 else qx - 34
            ly_ = qy + 18 if k == 0 else qy - LP(X) - 40
            al = "left" if k == 0 else "right"
            pos = f"left:{lx_:.0f}px" if k == 0 else f"left:{lx_ - 500:.0f}px; width:500px; text-align:right"
            co_html += (f'<svg class="thr co co{k}" width="{W}" height="{H}"><circle cx="{qx:.0f}" cy="{qy:.0f}" r="22" fill="none" style="stroke:var(--sl)" stroke-width="2"/></svg>'
                        f'<div class="ln k co co{k}" style="{pos}; top:{ly_:.0f}px; font-size:{LP(X)}px; color:var(--ink)">{X.rich(txt)}</div>')
    pen = Pen(*g["entry"])
    pen.poly([(x0, y1)], 26).mark("axis")
    # trend: a gentle rising curve from the origin through the cloud
    pen.curve((x0 + (x1 - x0) * 0.35, y1 - (y1 - y0) * 0.16), (x0 + (x1 - x0) * 0.65, y1 - (y1 - y0) * 0.56), (x1, y0 + (y1 - y0) * 0.14)).mark("trend")
    _end(X, pen, E, t, d)
    inner = (f'<div class="hair xa" style="left:{x0}px; top:{y1}px; width:{x1 - x0}px; height:1.5px"></div>'
             f'<svg class="thr" width="{W}" height="{H}">{dsvg}</svg>' + ylab + xlab + k_html + note + co_html + pen.svg(W, H, TW(X)))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, inner, origin, dark)
    s = f"#{cid}"
    t_dots = T(X, b, "at_dots", t, t + 1.0)
    t_trend = T(X, b, "at_trend", t, t + 2.2)
    if kick: first(X, f"{s} .kk", t)
    first(X, f"{s} .xa, {s} .yl, {s} .xl", t)
    order = sorted(range(n), key=lambda k: dots[k][0])
    X.tw(f'tl.from("{s} .dt", {{attr:{{r:0}}, duration:0.35, ease:"back.out(2)", stagger:{{each:{min(0.12, 2.4 / n):.3f}}}}}, {t_dots:.3f});')
    reveal(X, f"{s} .nt", t_trend + 0.8, 0.7, 0)
    for k in range(min(2, len(co))):
        reveal(X, f"{s} .co{k}", max(t_trend + 1.5 + 0.7 * k, t + d - 2.0 + 0.7 * k), 0.6, 8, 0)
    steps = [(t + 0.05, pen.f("axis"), 0.9, "power2.inOut"), (t_trend, pen.f("trend"), 1.4, "power2.inOut")]
    if E: steps.append((max(t + d - 0.7, t_trend + 1.4), 1.0, 0.6, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


def words_scene(b, X, t, d, cid):
    """text-centred: the line drops in from above onto the stressed word and underlines it; "strike": true lifts it
    through the word instead (the claim crossed out)."""
    P, W, H = X.portrait, X.W, X.H
    g = L_words(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    t_html, tg = textblock(X, b.get("text", ""), W / 2, g["top"], g["px"], lh=g["lh"])
    kick = b.get("kicker", "")
    k_html = f'<div class="ln k kk" style="left:0; right:0; text-align:center; top:{g["top"] - (110 if P else 100):.0f}px; font-size:{KP(X)}px">{X.rich(kick)}</div>' if kick else ""
    sub = b.get("sub", "")
    s_html = f'<div class="ln k sb" style="left:0; right:0; text-align:center; top:{g["top"] + tg["h"] + 40:.0f}px; font-size:{LP(X)}px; letter-spacing:.06em">{X.rich(sub)}</div>' if sub else ""
    pen = Pen(*g["entry"])
    sx, ex, top = (tg["stress"][0] if tg["stress"] else (g["sx"], g["ex"], g["sy"]))
    uy = top + under(tg["px"])
    pen.to(sx, uy - 40).mark("drop")
    pen.poly([(sx, uy), (ex, uy)], 18).mark("word")
    if b.get("strike"):
        my = top + tg["px"] * 0.56
        pen.curve((ex + 50, uy), (ex + 50, my), (ex + 10, my)).to(sx - 24, my).mark("strike")
    _end(X, pen, E, t, d)
    inner = k_html + f'<div class="tx">{t_html}</div>' + s_html + pen.svg(W, H, TW(X))
    origin = (pen.x, pen.y)
    push = 1.09 if b.get("strike") else 1.05
    furn(X, b, cid, t, d, inner, origin, dark, push)
    s = f"#{cid}"
    t_text = T(X, b, "at_text", t, t + 0.02)
    t_st = T(X, b, "at_stress", t, t_text + 0.7)
    if kick: reveal(X, f"{s} .kk", t + (1.4 if b.get("strike") else 0.1), 0.7)
    first(X, f"{s} .tx .b", t_text)
    X.tw(f'tl.from("{s} .tx .s", {{opacity:0, y:12, filter:"blur(12px)", duration:1.2, ease:"power3.out"}}, {t_st:.3f});')
    if sub: reveal(X, f"{s} .sb", t_st + 0.8)
    steps = [(t + 0.1, pen.f("drop"), max(0.6, t_st - t - 0.1), "power1.inOut"), (t_st + 0.3, pen.f("word"), 0.8, "power2.inOut")]
    if b.get("strike"):
        t_k = T(X, b, "at_strike", t, t_st + 1.6)
        steps.append((max(t_k, t_st + 1.1), pen.f("strike"), 0.7, "power3.inOut"))
        X.tw(f'tl.to("{s} .tx .s", {{opacity:0.45, duration:0.5}}, {max(t_k, t_st + 1.1) + 0.4:.3f});')
    if E: steps.append((max(t + d - 0.7, steps[-1][0] + steps[-1][2]), 1.0, 0.6, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, push, origin, dark)


def split_scene(b, X, t, d, cid):
    """two outcomes side by side; the thread is the dividing line. A side may have art or "empty" (dashed outline)."""
    P, W, H = X.portrait, X.W, X.H
    g = L_split(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    m = M(X)
    parts = []
    for k, key in enumerate(("left", "right")):
        it = b.get(key, {})
        name = it.get("art", "pencils")
        if P:
            y0 = 330 if k == 0 else 900
            ahtml, A, ah = art(X, name, m, y0 + 20, 430, f"a{k}")
            tx, ty = 560, y0 + 120
            th, tg = textblock(X, it.get("word", ""), tx, ty, 140, align="left", cls=f"w{k}")
            nh = f'<div class="ln k n{k}" style="left:{tx}px; top:{ty + 200:.0f}px; font-size:{LP(X)}px">{X.rich(it.get("note", ""))}</div>'
        else:
            cx = W / 4 if k == 0 else W * 3 / 4
            ahtml, A, ah = art(X, name, cx - 170, 200, 340, f"a{k}")
            th, tg = textblock(X, it.get("word", ""), cx, 600, 120, cls=f"w{k}")
            nh = f'<div class="ln k n{k}" style="left:{cx - 400:.0f}px; width:800px; text-align:center; top:780px; font-size:{LP(X)}px">{X.rich(it.get("note", ""))}</div>'
        parts.append(ahtml + th + nh)
    pen = Pen(*g["entry"])
    if P: pen.to(W - m, g["dv"]).mark("div")
    else: pen.to(W / 2, 880).mark("div")
    _end(X, pen, E, t, d)
    parts.append(pen.svg(W, H, TW(X)))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, "".join(parts), origin, dark)
    s = f"#{cid}"
    tl_ = min(T(X, b, "at_left", t, t + 0.4), t + 0.02)
    tr_ = T(X, b, "at_right", t, t + 1.4)
    first(X, f"{s} .a0", t); reveal(X, f"{s} .w0", tl_ + 0.25); reveal(X, f"{s} .n0", tl_ + 0.6)
    X.tw(f'tl.from("{s} .a1", {{opacity:0, duration:1.0, ease:"power1.inOut"}}, {tr_:.3f});')
    reveal(X, f"{s} .w1 .b", tr_ + 0.2); stress_in(X, f"{s} .w1", tr_ + 0.3); reveal(X, f"{s} .n1", tr_ + 0.7)
    steps = [(t + 0.05, pen.f("div"), max(1.0, tr_ - t), "power2.inOut")]
    if E: steps.append((max(t + d - 0.6, steps[-1][0] + steps[-1][2]), 1.0, 0.55, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


def bars_scene(b, X, t, d, cid):
    """the thread outlines the bars itself (up, across, down), then they take a faint wash. One value can be the *stress*."""
    P, W, H = X.portrait, X.W, X.H
    g = L_bars(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    items = b.get("items", [])[:2]
    mx_ = float(b.get("max") or max(float(it["value"]) for it in items))
    base, bw = g["base"], g["bw"]
    pen = Pen(*g["entry"])
    parts = []
    for k, it in enumerate(items):
        xc = g["xs"][k]; h = g["hmax"] * float(it["value"]) / mx_
        xl, xr, ytop = xc - bw / 2, xc + bw / 2, base - h
        pen.to(xl, base).mark(f"b{k}a")
        pen.poly([(xl, ytop), (xr, ytop), (xr, base)], 10).mark(f"b{k}")
        parts.append(f'<div class="fill f{k}" style="left:{xl:.0f}px; top:{ytop:.0f}px; width:{bw}px; height:{h:.0f}px"></div>')
        val = str(it.get("v", it["value"]))
        vpx = 150 if P else 150
        vh, vg = textblock(X, val, xc - 20, ytop - vpx * 1.12, vpx, cls=f"v{k}", weight=200)
        uw = adv(fit.plain(val), "*" in val) * vpx * (SK if "*" in val else 1)
        parts.append(vh + f'<div class="ln k u{k}" style="left:{xc - 20 + uw / 2 + 12:.0f}px; top:{ytop - vpx * 0.36:.0f}px; font-size:{LP(X)}px">{X.rich(it.get("unit", ""))}</div>')
        parts.append(f'<div class="ln k l{k}" style="left:{xc - 200:.0f}px; width:400px; text-align:center; top:{base + 30:.0f}px; font-size:{LP(X) + 2}px; color:var(--ink)">{X.rich(it.get("label", ""))}</div>')
    pen.to(g["x_end"], base).mark("base")
    parts.append(f'<div class="hair bl" style="left:{g["entry"][0]}px; top:{base - 1}px; width:{g["x_end"] - g["entry"][0]}px; height:2px; opacity:.4"></div>')
    for k, it in enumerate(items):      # ghost outlines of the bars, so the chart is on the page before the thread draws it
        xc = g["xs"][k]; h = g["hmax"] * float(it["value"]) / mx_
        parts.append(f'<div class="gb" style="position:absolute; left:{xc - bw / 2:.0f}px; top:{base - h:.0f}px; width:{bw}px; height:{h:.0f}px; '
                     f'border:2px dashed color-mix(in srgb, var(--mut) 45%, transparent); border-bottom:0"></div>')
    _end(X, pen, E, t, d)
    kick = b.get("kicker", "")
    if kick: parts.append(f'<div class="ln k kk" style="left:{M(X) + (0 if P else 0)}px; top:{300 if P else 150}px; font-size:{KP(X)}px">{X.rich(kick)}</div>')
    parts.append(pen.svg(W, H, TW(X)))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, "".join(parts), origin, dark)
    s = f"#{cid}"
    if kick: first(X, f"{s} .kk", t)
    first(X, f"{s} .bl, {s} .gb", t)
    tk = [T(X, b, f"at_{k}", t, t + 0.6 + 1.6 * k) for k in range(len(items))]
    steps = []
    for k in range(len(items)):
        start = max(tk[k] - 0.9, steps[-1][0] + steps[-1][2] if steps else t + 0.05)
        steps.append((start, pen.f(f"b{k}a"), 0.35, "power1.in"))
        steps.append((start + 0.35, pen.f(f"b{k}"), 0.9, "power2.inOut"))
        X.tw(f'tl.from("{s} .f{k}", {{scaleY:0, opacity:0, duration:0.8, ease:"power2.out"}}, {start + 1.1:.3f});')
        reveal(X, f"{s} .v{k}, {s} .u{k}", start + 0.8, 0.9)
        first(X, f"{s} .l{k}", t)
    steps.append((steps[-1][0] + steps[-1][2], pen.f("base"), 0.6, "power1.inOut"))
    if E: steps.append((max(t + d - 0.6, steps[-1][0] + steps[-1][2]), 1.0, 0.55, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


def paper_scene(b, X, t, d, cid):
    """real object + text: the paper itself (journal, year, title, authors) on a sheet; the thread underlines our line and
    then the title on the sheet."""
    P, W, H = X.portrait, X.W, X.H
    g = L_paper(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    m = M(X)
    cx, cy, cw, chh = g["card"]
    title = b.get("title", "")
    pad = 64 if P else 60
    jt = f'<div class="ln k" style="left:{pad}px; top:{pad}px; font-size:{SP(X)}px; letter-spacing:.2em">{X.rich(b.get("journal", ""))}</div>'
    th, tg = textblock(X, "|".join(f"*{l}*" for l in title.split("|")) if "*" not in title else title, pad, pad + 70, 66 if P else 60, align="left", lh=1.18, box_w=cw - 2 * pad, color="var(--ink)")
    au_y = pad + 70 + tg["h"] + 26
    au = f'<div class="ln" style="left:{pad}px; top:{au_y:.0f}px; font-size:{SP(X) + 4}px; font-family:var(--f-body); font-weight:400; color:#55504a">{X.rich(b.get("authors", ""))}</div>'
    r = random.Random(3)
    bars = "".join(f'<i class="bar" style="left:{pad}px; top:{au_y + 74 + k * 26:.0f}px; width:{(cw - 2 * pad) * (r.uniform(.78, 1) if k % 5 != 4 else r.uniform(.3, .6)):.0f}px"></i>'
                   for k in range(int((chh - au_y - 74 - pad) / 26)))
    sheet = f'<div class="sheet sh" style="left:{cx}px; top:{cy}px; width:{cw}px; height:{chh}px">{jt}{th}{au}{bars}</div>'
    kick = b.get("kicker", "")
    k_html = f'<div class="ln k kk" style="left:{g["tx"]:.0f}px; top:{g["ty"]:.0f}px; font-size:{KP(X)}px">{X.rich(kick)}</div>' if kick else ""
    tx_html, txg = textblock(X, b.get("text", ""), g["tx"], g["ty"] + 64, 84 if P else 80, align="left", cls="tx",
                             box_w=(W - 2 * m) if P else (cx - g["tx"] - 80))
    # the thread: under our line, then across to the paper's title
    pen = Pen(*g["entry"])
    ly = g["ty"] + 64 + txg["h"] + 14
    x_l1 = max(x1 for _, x1, _ in txg["lines"])
    pen.to(x_l1, ly).mark("ours")
    if tg["stress"]:
        sx, ex, top = tg["stress"][-1]
        uy = cy + top + under(tg["px"]) * 0.98
        if P:
            pen.poly([(W - 50, ly), (W - 50, uy), (cx + ex, uy)], 30).mark("to")
            pen.to(cx + sx, uy).mark("title")
        else:
            pen.glide(cx + sx, uy, 0.5)
            pen.mark("to"); pen.to(cx + ex, uy).mark("title")
    _end(X, pen, E, t, d)
    inner = k_html + tx_html + sheet + pen.svg(W, H, TW(X))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, inner, origin, dark)
    s = f"#{cid}"
    t_t = T(X, b, "at_title", t, t + 1.6)
    if kick: reveal(X, f"{s} .kk", t)
    first(X, f"{s} .tx", t)
    first(X, f"{s} .sh", t)
    X.sfx(t + 0.5, "paper")
    steps = [(t + 0.6, pen.f("ours"), 0.9, "power2.inOut")]
    if tg["stress"]: steps.append((max(t_t, t + 1.6), pen.f("title"), 1.2, "power2.inOut"))
    if E: steps.append((max(t + d - 0.7, steps[-1][0] + steps[-1][2]), 1.0, 0.6, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


def ratio_scene(b, X, t, d, cid):
    """lengths of thread as sizes of an effect. Optional "ref": {"label", "of"} = a grey reference row (the original
    finding) and the thread row at `of` of its length; at the cue the far part of the thread row goes grey and dashed,
    a bracket names the share that went (the page's italic), and the thread carries on from what is left."""
    P, W, H = X.portrait, X.W, X.H
    g = L_ratio(X, b)
    dark = b.get("ground") == "dark"
    y, x0, x1 = g["y"], g["x0"], g["x1"]
    ref = b.get("ref")
    lrow = (x1 - x0) * float(ref.get("of", 1)) if ref else (x1 - x0)
    xe = x0 + lrow
    keep = float(b.get("keep", 1 / 3))
    xk = x0 + lrow * keep
    m = M(X)
    tw_ = TW(X)
    lp = LP(X)
    parts = []
    kick = b.get("kicker", "")
    if kick:
        k_html, kg = textblock(X, kick, m + (0 if P else 172), g["ky"], 60 if P else 58, align="left", cls="kk", box_w=W - 2 * m)
        parts.append(k_html)
    parts.append(f'<div class="ln k lb" style="left:{m + (0 if P else 172)}px; top:{g["ky"] + (100 if P else 92):.0f}px; font-size:{lp}px">{X.rich(b.get("label", ""))}</div>')
    if ref:
        yr = g["yr"]
        parts.append(f'<div class="hair rf" style="left:{x0}px; top:{yr - 2}px; width:{x1 - x0}px; height:4px; opacity:.7"></div>'
                     f'<div class="ln k rfl" style="left:{x0}px; top:{yr - lp - 22}px; font-size:{lp}px">{X.rich(ref.get("label", ""))}</div>')
    if b.get("row"):
        parts.append(f'<div class="ln k rwl" style="left:{x0}px; top:{y - lp - 22}px; font-size:{lp}px">{X.rich(b["row"])}</div>')
    pen = Pen(*g["entry"])
    pen.to(x0, y).mark("start")
    pen.to(xe, y).mark("full")
    by = y - (96 if P else 80)
    parts.append(pen.svg(W, H, tw_))
    parts.append(f'<svg class="thr gh" width="{W}" height="{H}"><line x1="{xk:.0f}" y1="{y}" x2="{xe + 4:.0f}" y2="{y}" stroke="var(--paper)" stroke-width="{tw_ + 4}"/>'
                 f'<line x1="{xk + 10:.0f}" y1="{y}" x2="{xe:.0f}" y2="{y}" style="stroke:var(--mut)" stroke-width="2.5" stroke-dasharray="10 10"/></svg>')
    parts.append(f'<svg class="thr bk" width="{W}" height="{H}"><path d="M{xk + 6:.0f} {by + 18} L{xk + 6:.0f} {by} L{xe:.0f} {by} L{xe:.0f} {by + 18}" fill="none" style="stroke:var(--mut)" stroke-width="2"/></svg>')
    vpx = 150 if P else 140
    vw_ = line_w(b.get("value", "*约 2/3*"), vpx)
    vx = min(max((xk + xe) / 2, x0 + vw_ / 2), W - m - vw_ / 2)
    v_html, vg = textblock(X, b.get("value", "*约 2/3*"), vx, by - vpx * 1.2, vpx, cls="vv")
    parts.append(v_html)
    parts.append(f'<div class="ln k kp" style="left:{xk + 30:.0f}px; top:{y + 26}px; font-size:{lp}px; color:var(--th)">{X.rich(b.get("kept", ""))}</div>')
    if b.get("note"):
        parts.append(f'<div class="ln k nt" style="left:{xk + 30:.0f}px; top:{y + 26 + lp * 1.7:.0f}px; width:{W - m - xk - 30:.0f}px; white-space:normal; line-height:1.55; '
                     f'font-size:{lp - 2}px; letter-spacing:.04em">{X.rich(b["note"])}</div>')
    pen2 = Pen(xk, y)
    pen2.poly([(xk, y + (300 if P else 200)), (x0 - 20, y + (300 if P else 200))], 40).mark("go")
    pen2.mark("end")
    parts.append(pen2.svg(W, H, tw_, cls="th t2"))
    origin = (pen2.x, pen2.y)
    furn(X, b, cid, t, d, "".join(parts), origin, dark)
    s = f"#{cid}"
    t_cut = T(X, b, "at_cut", t, t + 1.8)
    if kick: first(X, f"{s} .kk", t)
    reveal(X, f"{s} .lb", t + 0.2, 0.6)
    if ref:
        first(X, f"{s} .rf", t)
        reveal(X, f"{s} .rfl", t + 0.15, 0.6)
    if b.get("row"): reveal(X, f"{s} .rwl", t + 0.6, 0.6)
    tw_draw(X, f"{s} .th:not(.t2)", [(t + 0.05, pen.f("start"), 0.3, "power1.in"), (t + 0.4, 1.0, max(0.9, min(1.6, t_cut - t - 0.6)), "power2.inOut")], t, t + d)
    X.tw(f'tl.from("{s} .gh", {{opacity:0, duration:0.6, ease:"power2.inOut"}}, {t_cut:.3f});')
    X.tw(f'tl.from("{s} .bk", {{opacity:0, y:10, duration:0.6, ease:"power2.out"}}, {t_cut + 0.3:.3f});')
    X.tw(f'tl.from("{s} .vv .b", {{opacity:0, duration:0.8, ease:"power1.out"}}, {t_cut + 0.35:.3f});')
    X.tw(f'tl.from("{s} .vv .s", {{opacity:0, y:16, filter:"blur(12px)", duration:1.1, ease:"power3.out"}}, {t_cut + 0.45:.3f});')
    reveal(X, f"{s} .kp", t_cut + 0.9, 0.7)
    if b.get("note"): reveal(X, f"{s} .nt", t_cut + 1.4, 0.7)
    X.sfx(t_cut, "tick")
    tw_draw(X, f"{s} .t2", [(t_cut + 1.1, pen2.f("go"), 0.8, "power2.inOut")], t, t + d)
    thread_out(X, pen2, cid, t, d, 1.035, origin, dark)


def card_scene(b, X, t, d, cid):
    """the close: the object and the one word. The thread underlines the word, travels to the object and closes a loop round it."""
    P, W, H = X.portrait, X.W, X.H
    g = L_card(X, b)
    dark = b.get("ground") == "dark"
    E = exit_point(X)
    a_html, A, ah = art(X, b.get("art", "mallow2"), g["ax"], g["ay"], g["aw"], "ca")
    align = "center" if P else "center"
    kick = b.get("kicker", "")
    k_html, _ = textblock(X, kick, g["tx"], g["ty"], 44 if P else 42, align=align, cls="kk") if kick else ("", None)
    w_html, wg = textblock(X, b.get("text", "*相信*"), g["tx"], g["ty"] + (90 if P else 84), 230 if P else 210, align=align, cls="ww")
    sub = b.get("sub", "")
    s_html, sg = textblock(X, sub, g["tx"], g["ty"] + (90 if P else 84) + wg["h"] + 10, 48 if P else 46, align=align, cls="sb") if sub else ("", None)
    c = A("c"); r = A("r")
    rx, ry = r[0] * 1.04, r[1] * 1.3
    pen = Pen(*g["entry"])
    if wg["stress"]:
        sx, ex, top = wg["stress"][0]
        uy = top + under(wg["px"]) * 0.95
        pen.glide(sx, uy, 0.4).mark("toword"); pen.to(ex, uy).mark("word")
    if P:
        rx = min(rx, W / 2 - M(X) - 24)
        pen.poly([(c[0] + rx, pen.y), (c[0] + rx, c[1])], 40).mark("toobj")
        pen.ellipse(c[0], c[1], rx, ry, 0, 340).mark("loop")
    else:
        pen.glide(c[0] - rx, c[1], 0.5)
        pen.mark("toobj")
        pen.ellipse(c[0], c[1], rx, ry, 180, 520).mark("loop")
    if E: _end(X, pen, E, t, d)
    inner = a_html + k_html + w_html + s_html + pen.svg(W, H, TW(X))
    origin = (pen.x, pen.y)
    furn(X, b, cid, t, d, inner, origin, dark)
    s = f"#{cid}"
    t_w = T(X, b, "at_text", t, t + 0.6)
    if kick: first(X, f"{s} .kk", t)
    X.tw(f'tl.from("{s} .ww .s", {{opacity:0, y:20, filter:"blur(16px)", duration:1.4, ease:"power3.out"}}, {t_w:.3f});')
    if sub: reveal(X, f"{s} .sb", t_w + 0.9, 1.0)
    first(X, f"{s} .ca", t)
    t_loop = T(X, b, "at_wrap", t, t_w + 2.0)
    steps = [(t + 0.05, pen.f("toword"), max(0.8, t_w - t + 0.3), "power2.inOut"), (t_w + 0.5, pen.f("word"), 0.7, "power2.inOut"),
             (max(t_loop - 0.5, t_w + 1.2), pen.f("toobj"), 0.9, "power2.inOut"), (max(t_loop + 0.4, t_w + 2.1), pen.f("loop"), 2.0, "power2.inOut")]
    if E: steps.append((max(t + d - 0.6, steps[-1][0] + steps[-1][2]), 1.0, 0.55, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.035, origin, dark)


ENTRY = {"object": lambda X, b: L_object(X, b)["entry"], "year": lambda X, b: L_year(X, b)["entry"], "side": lambda X, b: L_side(X, b)["entry"],
         "scatter": lambda X, b: L_scatter(X, b)["entry"], "words": lambda X, b: L_words(X, b)["entry"], "split": lambda X, b: L_split(X, b)["entry"],
         "bars": lambda X, b: L_bars(X, b)["entry"], "paper": lambda X, b: L_paper(X, b)["entry"], "ratio": lambda X, b: L_ratio(X, b)["entry"],
         "card": lambda X, b: L_card(X, b)["entry"]}


# ---------------------------------------------------------------- effects (scenes/fx) in this style
FX_CSS = r"""
.mng { position:absolute; inset:0; overflow:hidden; }
.st-minimal .fx.mn-under { background:transparent !important; }
.ctx.mnf .mnh { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-body); font-weight:400; color:var(--muted); letter-spacing:.16em; }
.ctx.mnf .mnh i { display:block; width:34px; height:1px; background:currentColor; opacity:.7; }
.ctx.mnf .mnx { position:absolute; font-family:var(--f-body); font-weight:300; letter-spacing:.14em; color:var(--muted); }
.ctx.mnf .mnc { position:absolute; left:0; right:0; text-align:center; }
.ctx.mnf .mnc .cl { display:inline-block; font-family:var(--f-cap); font-weight:500; line-height:1.35; color:var(--fg); letter-spacing:.04em; white-space:nowrap;
  text-shadow:0 0 14px color-mix(in srgb, var(--bg) 92%, transparent), 0 0 4px color-mix(in srgb, var(--bg) 92%, transparent); }
.ctx.mnf .mnc .em .emt { font-family:var(--f-em); font-style:italic; font-synthesis:none; color:var(--fg); }
.ctx.mnf .mnc .em .emb { display:none; }
.ctx.mnf .mnft { position:absolute; display:flex; justify-content:space-between; gap:24px; font-family:var(--f-body); font-weight:400; color:var(--muted); letter-spacing:.04em; }
.ctx.mnf .mnft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; }
.ctx.mnf.photo .mnh, .ctx.mnf.photo .mnft, .ctx.mnf.photo .mnx { color:#f3eee4; text-shadow:0 1px 8px rgba(0,0,0,.6); }
.ctx.mnf.photo .mnc .cl { color:#f7f3eb; text-shadow:0 1px 3px rgba(0,0,0,.8), 0 0 18px rgba(0,0,0,.55); }
.ctx.mnf.photo .mnc .em .emt { color:#f7f3eb; }
#root.v .ctx.mnf .mnc { padding:0 120px; }
/* effect internals, minimal: light sans for headlines, the stressed word in italic serif, hairlines, almost no radius */
.st-minimal .fx .big { font-family:var(--f-body); font-weight:300; letter-spacing:0; }
.st-minimal .fx .big .em .emt, .st-minimal .fx .em .emt { font-family:var(--f-em); font-style:italic; font-weight:400; font-synthesis:none; color:var(--fg) !important; }
.st-minimal .fx .em .emb { display:block; background:var(--accent) !important; height:3px !important; top:auto !important; bottom:-.06em !important; border-radius:0 !important; box-shadow:none !important; }
.st-minimal .fx .sub { font-family:var(--f-body); font-weight:300; text-transform:none; letter-spacing:.14em; }
.st-minimal .fx .sh { background-image:linear-gradient(110deg, var(--fg) 0%, var(--fg) 42%, var(--accent) 50%, var(--fg) 58%, var(--fg) 100%); }
.st-minimal .fx .caret { color:var(--accent); }
.st-minimal .fx .bl { opacity:.28; filter:blur(12vmin); }
.st-minimal .ct-view, .st-minimal .ct-sheet, .st-minimal .cp-sheet, .st-minimal .d2-sheet, .st-minimal .dp-ph, .st-minimal .ck-card { border-radius:2px !important;
  box-shadow:0 24px 50px rgba(50,35,20,.18), 0 4px 10px rgba(50,35,20,.08) !important; }
.st-minimal .ct-mk, .st-minimal .d2-mk { background:color-mix(in srgb, var(--accent) 22%, transparent); border-radius:0; }
.st-minimal .ct-vbar b, .st-minimal .ct-kick, .st-minimal .d2-kick { background:var(--accent); color:#f7f3eb; border-radius:0; }
.st-minimal .cp-chip, .st-minimal .d2-tag { border-radius:0; font-family:var(--f-body); }
.st-minimal .cp-year, .st-minimal .cq-year { font-family:var(--f-em); font-style:italic; font-weight:400; -webkit-text-stroke:0; color:color-mix(in srgb, var(--fg) 10%, transparent); }
.st-minimal .ck-v { border-radius:0; } .st-minimal .ck-tally b { color:var(--accent); font-family:var(--f-em); font-style:italic; font-weight:400; }
.st-minimal .fx .tp .tp-k { font-family:var(--f-body); text-transform:none; letter-spacing:.16em; }
.st-minimal .d2-ttl, .st-minimal .ck-ct, .st-minimal .fx .cb .cb-k, .st-minimal .fx .cb .cb-t { font-weight:300; }
.st-minimal .fx .cb .cb-s { border-radius:0; }
"""


def FX_FRAME(X, cid, t, d, p, k):
    """an effect on paper (or charcoal): grain + vignette under it, a quiet header, the spoken line as a plain sans caption
    with its keyword in italic serif, the source line — and the thread, which comes in at the top left, runs down the
    margin, underlines the caption and leaves for the next page."""
    X.css("minimal", CSS); X.css("minimal-fx", FX_CSS)
    P, W, H = X.portrait, X.W, X.H
    dark = p.get("theme") == "ink"
    eff = next((e for e in reversed(X.els) if e.startswith(f'<div id="{cid}"')), "")
    if "background:var(--bg)" in eff and not k["photo"]:
        X.els[X.els.index(eff)] = eff.replace('class="clip scene fx', 'class="clip scene fx mn-under', 1)
        X.clip(f"{cid}g", t, d, f'<div class="mn{" dark" if dark else ""}" style="background:var(--bg)">{grain(X, cid, dark)}</div>', "mng", 2, track=19, sty=k["sty"])
    hx, hy = (64, 206) if P else (96, 52)
    X.used_text.update(X.channel)
    hd = (f'<div class="mnh" style="left:{hx}px; top:{hy}px; font-size:{24 if P else 20}px"><span>{X.rich(X.channel)}</span><i></i><span>{k["topic"]}</span></div>'
          f'<div class="mnx" style="right:{hx}px; top:{hy}px; font-size:{22 if P else 18}px">{k["fxid"]}</div>')
    cap_top = 1330 if P else H - 64 - k["cap_px"] * 1.35 * len(k["cap_lines"])
    cap = f'<div class="mnc" style="top:{cap_top:.0f}px"><span class="cl" style="font-size:{k["cap_px"]}px">{k["cap"]}</span></div>'
    ft_pos = f"left:{hx}px; right:{hx}px; top:1478px" if P else "left:96px; right:96px; bottom:22px"
    ft = f'<div class="mnft" style="{ft_pos}; font-size:{SP(X)}px"><div>{k["foot"]}</div><div>{k["src"]}</div></div>' if (k["foot"] or k["src"]) else ""
    # the thread for this page
    from h9 import fit as _fit
    E = exit_point(X)
    lines = [_fit.plain(l) for l in k["cap_lines"]] or [""]
    cw = max(len(l) for l in lines) * k["cap_px"] * 1.04
    uy = cap_top + k["cap_px"] * 1.35 * len(lines) + 6
    x0 = W / 2 - min(cw, W - 2 * hx) / 2
    pen = Pen(*fx_entry(X))
    pen.poly([(fx_entry(X)[0], uy), (x0, uy)], 30).mark("margin")
    pen.to(W / 2 + min(cw, W - 2 * hx) / 2, uy).mark("cap")
    pen.mark("end")
    svg = pen.svg(W, H, TW(X)).replace('class="thr"', 'class="thr" style="position:absolute;left:0;top:0;overflow:visible"')
    thr = f'<div style="--th:{BLUE_D if dark else BLUE}">{svg}</div>'
    X.clip(f"{cid}c", t, d, hd + cap + ft + thr, f"ctx mnf{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
    X.css("minimal-fx-th", ".ctx.mnf .th { fill:none; stroke:var(--th); stroke-linecap:round; stroke-linejoin:round; }")
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .cl", {{opacity:0, y:10, filter:"blur(6px)", duration:0.6, ease:"power2.out"}}, {t + 0.05:.3f});')
    steps = [(t + 0.05, pen.f("margin"), min(1.0, d * 0.35), "power2.inOut"), (t + 0.5, pen.f("cap"), min(0.9, d * 0.3), "power2.inOut")]
    if E: steps.append((max(t + d - 0.55, t + 1.0), 1.0, 0.5, "power2.inOut"))
    tw_draw(X, f"{s} .th", steps, t, t + d)
    thread_out(X, pen, cid, t, d, 1.0, (pen.x, pen.y), dark)


SCENES = {"object": object_scene, "year": year_scene, "side": side_scene, "scatter": scatter_scene, "words": words_scene,
          "split": split_scene, "bars": bars_scene, "paper": paper_scene, "ratio": ratio_scene, "card": card_scene}
