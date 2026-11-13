"""riso · 孔版印刷 —— 三色孔版（risograph）海报：暖白未涂布纸，荧光粉 / 蓝 / 黄三块版各自一层，正片叠底套印出二次色
（粉 + 蓝 = 紫、蓝 + 黄 = 绿、粉 + 黄 = 橙红）；没有黑墨，"黑"字是蓝版 + 粉版叠出来的。每块版都有大豆油墨的斑驳颗粒、
大实地的滚筒条纹，和每页方向不同的套印偏移（3–7 px）。层次只用网点（粉 45°、蓝 75°、黄 15°，网距 12 px），不用透明度。

版式：每页一个占满半个画面以上、至少两边出血、压到底边的大色块；数字压在色块上或从色块里镂空；
中文大标题左上 x 72，数字 x 72 左齐（Anton 一种墨，另一种墨偏 12 px 做"影子"）；页眉是印厂小签 + 三个色票，
四角套准十字，最底下一条色带。图表都是印刷品：对比 = 面积按真实比例的两个叠印圆，占比 = 10×10 网点格，
增长 = 刮板拉出来的色带，排行 = 按长度裁的色纸条。

动作：每页三块版一块一块印上去（黄 → 粉 → 蓝，每块 5 帧从上往下硬边擦出，间隔 2 帧，上一张纸被抽走时下一张已经在印），每页第 17 帧前印完；
停住时某块版每 6 帧抖 1 px；所有版的动作按 12 fps 走格；数字印好就是终值，只有讲变化的那页先印旧值、停 10 帧再一帧换新；印好后只加第二遍加深、盖章、套准抖动；换页是整张纸 7 帧被抽走（向上 110%），
露出下一张白纸再开印。

场景（SCENES）：hero 大数字 · circles 叠印圆对比 · bands 刮板色带增长 · grid 网点占比 · strips 色纸条排行 ·
swap 数字换版 · statement 判断句 + 拆分条 · outro 三圆套准落版。
"""
import math

PAPER, PINK, BLUE, YEL = "#f2efe6", "#ff48b0", "#0078bf", "#ffe800"
BLUE2 = "#00388f"      # blue printed twice (double hit): small text and the caption strip, where single-hit blue is too light to read
NAVY = "#002183"       # what blue over pink multiplies to: this style's "black"
INK = {"y": YEL, "p": PINK, "b": BLUE}
ANGLE = {"p": 45, "b": 75, "y": 15}
PITCH = 12
ORDER = "ypb"          # print order: yellow, pink, blue
FPS = 30

STYLE = {
    "name": "孔版印刷", "en": "Risograph", "benchmarks": ["Risotto Studio（格拉斯哥）", "Hato Press", "Colorama（柏林）", "孔版 zine 海报"],
    "tokens": {
        "bg": PAPER, "fg": NAVY, "muted": "#3a4a8a", "accent": BLUE, "accent2": PINK, "alert": PINK,
        "line": "#d9d3c4", "paper": PAPER, "ink": NAVY, "card": PAPER, "card-fg": NAVY,
        "pink": PINK, "blue": BLUE, "yellow": YEL, "blue2": BLUE2, "navy": NAVY,
        # caption: a strip of the same paper printed solid blue (double hit), paper-white knocked-out text
        "cap-bg": BLUE2, "cap-fg": PAPER, "cap-size": "40px", "cap-weight": "700", "cap-pad": "16px 28px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "110px", "cap-em": YEL,
        "punch-top": "68%", "punch-size": "72px",
    },
    "fonts": {"display": ["alibaba-puhuiti-heavy", "noto-sans-sc"], "body": ["alibaba-puhuiti", "noto-sans-sc"],
              "cap": ["alibaba-puhuiti", "noto-sans-sc"], "num": ["anton", "alibaba-puhuiti-heavy"],
              "mono": ["space-mono", "alibaba-puhuiti"]},
    "motion": {"ease": "power2.out", "dur": 0.33, "stagger": 0.13, "cut": "hard", "transition": None, "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "none"},
    "caption_plate": False,
    "outro": {"move": False},
    "sfx": {"transition": ("paper", 0.45), "enter": ("click", 0.35), "pass": ("click", 0.28), "pop": ("pop", 0.35), "hit": ("hit", 0.35),
            "slam": ("slam", 0.4), "count": ("tick", 0.18), "click": ("click", 0.3), "mascot": None, "cut": None, "line": ("click", 0.25)},
    "safe_exempt": [".rz-slug", ".rz-sw"],
}

# ---------------------------------------------------------------- textures (all deterministic SVG noise)
FIBRE = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='480' height='480'>"
         "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.035 .11' numOctaves='3' seed='7'/>"
         "<feColorMatrix values='0 0 0 0 .42  0 0 0 0 .36  0 0 0 0 .26  0 0 0 -2.2 1.25'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")


def grain(seed):
    """soy-ink mottling: white specks of paper showing through the ink (white is invisible on paper under multiply)."""
    return ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='360' height='360'>"
            f"<filter id='g'><feTurbulence type='fractalNoise' baseFrequency='.55' numOctaves='2' seed='{seed}'/>"
            "<feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  3.4 0 0 0 -1.35'/></filter><rect width='100%' height='100%' filter='url(%23g)'/></svg>")


def mottle(seed):
    """large soft blotches of uneven ink coverage."""
    return ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='700' height='700'>"
            f"<filter id='m'><feTurbulence type='fractalNoise' baseFrequency='.008' numOctaves='3' seed='{seed}'/>"
            "<feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.2 0 0 0 -1.0'/></filter><rect width='100%' height='100%' filter='url(%23m)'/></svg>")


GRAIN = {"y": grain(11), "p": grain(23), "b": grain(37)}
MOTTLE = {"y": mottle(5), "p": mottle(17), "b": mottle(29)}
GRAIN_OP = {"y": 0.2, "p": 0.24, "b": 0.26}

CSS = r"""
.st-riso .em .emb { display:none; }
.rzw { position:absolute; inset:0; }
.rz { position:absolute; inset:0; overflow:hidden; background:__PAPER__; }
.rz .fib { position:absolute; inset:0; background-image:url("__FIBRE__"); background-size:480px; opacity:.12; }
.rz .ink { position:absolute; inset:0; mix-blend-mode:multiply; isolation:isolate; }
.rz .ink > .pl { position:absolute; inset:0; }
.rz .ink > .grn { position:absolute; inset:0; background-size:360px; pointer-events:none; }
.rz .ink > .mot { position:absolute; inset:0; background-size:700px; opacity:.16; pointer-events:none; }
.rz .ink > .band { position:absolute; inset:0; pointer-events:none;
  background:repeating-linear-gradient(180deg, rgba(255,255,255,0) 0 118px, rgba(255,255,255,.07) 118px 126px, rgba(255,255,255,.13) 126px 134px, rgba(255,255,255,.07) 134px 140px); }
.rz .ink2 { position:absolute; inset:0; mix-blend-mode:multiply; isolation:isolate; }
.rz .ink2 > .pl { position:absolute; inset:0; }
.rz .ink2 > .grn { position:absolute; inset:0; background-size:360px; pointer-events:none; }
.rz .e { position:absolute; display:block; }
.rz svg.e { overflow:visible; }
.rz .t { position:absolute; white-space:nowrap; line-height:1.15; font-family:var(--f-display); font-weight:900; }
.rz .t.cn { letter-spacing:0; }
.rz .t.nm { font-family:var(--f-num); font-weight:400; line-height:1; letter-spacing:-.015em; }
.rz .t.nm .u { font-size:.42em; letter-spacing:0; margin-left:.04em; }
.rz .t.bd { font-family:var(--f-body); font-weight:700; }
.rz .t.mo { font-family:var(--f-mono); font-weight:400; letter-spacing:.06em; }
.rz .t.src { font-family:var(--f-body); font-weight:700; font-size:24px; line-height:1.3; }
"""


def anton_w(s):
    """width of a string in Anton, in em."""
    W = {"1": 0.331, ".": 0.229, ",": 0.236, "%": 1.057, "+": 0.355, "-": 0.311, " ": 0.234, "x": 0.459}
    tot = 0.0
    for c in str(s):
        if c.isdigit(): tot += W.get(c, 0.494)
        elif c in W: tot += W[c]
        else: tot += 1.0
    return tot


def misreg(i):
    """the per-beat registration error of each plate: 3–7 px, each in its own direction (deterministic from the beat index)."""
    out = {}
    for k, ink in enumerate(ORDER):
        a = math.radians((i * 137 + k * 121 + 30) % 360)
        r = 3 + (i * 3 + k * 2) % 5
        out[ink] = (round(r * math.cos(a), 1), round(r * math.sin(a), 1))
    return out


# ---------------------------------------------------------------- one printed sheet = three plates
class Sheet:
    def __init__(self, X, cid):
        self.X, self.cid = X, cid
        self.pl = {"y": [], "p": [], "b": []}
        self.hit = {"y": [], "p": [], "b": []}      # second hits: the same ink run through the drum again, later

    def put(self, inks, html):
        """html with {c} (that plate's ink colour) and {k} (the plate letter); added to every plate in `inks`."""
        for k in inks:
            self.pl[k].append(html.replace("{c}", INK[k]).replace("{k}", k))

    def ko(self, inks, html):
        """knock out: white in those plates (white multiplies to nothing, so the paper shows)."""
        for k in inks:
            self.pl[k].append(html.replace("{c}", "#fff").replace("{k}", k))

    def pat(self, k, tint):
        return f"{self.cid}h{k}{int(tint * 100)}"

    def defs(self, k):
        """halftone screens of this plate's ink: 15 / 30 / 50 / 70 % at the ink's own screen angle."""
        out = []
        for tint in (0.15, 0.3, 0.5, 0.7):
            r = PITCH * math.sqrt(tint / math.pi)
            out.append(f'<pattern id="{self.pat(k, tint)}" width="{PITCH}" height="{PITCH}" patternUnits="userSpaceOnUse" patternTransform="rotate({ANGLE[k]})">'
                       f'<circle cx="{PITCH / 2}" cy="{PITCH / 2}" r="{r:.2f}" fill="{INK[k]}"/></pattern>')
        return f'<svg width="0" height="0" style="position:absolute"><defs>{"".join(out)}</defs></svg>'

    # shapes -----------------------------------------------------------
    def rect(self, inks, x, y, w, h, cls="", tint=None, ko=False, hit=False):
        for k in inks:
            fill = "#fff" if ko else (f"url(#{self.pat(k, tint)})" if tint else INK[k])
            (self.hit if hit else self.pl)[k].append(f'<svg class="e {cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px" viewBox="0 0 {w:.0f} {h:.0f}">'
                              f'<rect width="{w:.0f}" height="{h:.0f}" fill="{fill}"/></svg>')

    def circle(self, inks, cx, cy, r, cls="", tint=None, ko=False, hit=False):
        for k in inks:
            fill = "#fff" if ko else (f"url(#{self.pat(k, tint)})" if tint else INK[k])
            (self.hit if hit else self.pl)[k].append(f'<svg class="e {cls}" style="left:{cx - r:.0f}px;top:{cy - r:.0f}px;width:{2 * r:.0f}px;height:{2 * r:.0f}px" viewBox="0 0 {2 * r:.0f} {2 * r:.0f}">'
                              f'<circle cx="{r:.0f}" cy="{r:.0f}" r="{r:.0f}" fill="{fill}"/></svg>')

    def text(self, inks, x, y, px, s, cls="cn", color=None, extra="", style=""):
        X = self.X
        X.used_text.update(str(s))
        for k in inks:
            c = color or INK[k]
            self.pl[k].append(f'<div class="t {cls}" {extra} style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px:.0f}px;color:{c};{style}">{X.rich(s)}</div>')

    def small(self, x, y, px, s, cls="bd", style=""):
        """small type (under ~70 px) goes on one plate only, in double-hit blue: misregistered overprint would blur it."""
        self.text("b", x, y, px, s, cls, color=BLUE2, style=style)

    def black(self, x, y, px, s, cls="cn", extra="", style=""):
        """"black" type: the same glyphs on the pink and the blue plate; they overprint to navy (and misregister)."""
        self.text("pb", x, y, px, s, cls, extra=extra, style=style)

    def numeral(self, x, y, px, value, suffix="", main="b", ghost="p", cls="", knock="", g=12, start=None):
        """a hero numeral: one ink, a second ink offset g px as a drop ghost; knock = plates the figure is cut out of."""
        X = self.X
        X.used_text.update(str(value) + suffix + "0123456789.,+")
        body = f'<span class="nv">{value if start is None else start}</span>' + (f'<span class="u">{X.rich(suffix)}</span>' if suffix else "")
        for k in knock:
            self.pl[k].append(f'<div class="t nm {cls}" data-safe="ignore" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px:.0f}px;color:#fff">{body}</div>')
        if main and main not in knock:
            self.pl[main].append(f'<div class="t nm {cls}" data-safe="ignore" style="left:{x:.0f}px;top:{y:.0f}px;font-size:{px:.0f}px;color:{INK[main]}">{body}</div>')
        if ghost:
            self.pl[ghost].append(f'<div class="t nm {cls} gh" data-safe="ignore" style="left:{x + g:.0f}px;top:{y + g:.0f}px;font-size:{px:.0f}px;color:{INK[ghost]}">{body}</div>')

    def source(self, x, y, s, maxw):
        """the source line: double-hit blue on a knocked-out paper slip (a 24 px line cannot survive misregistered overprint)."""
        from h9 import fit
        if not s: return
        f = fit.fit_text(s, maxw - 24, 40, 24, 22, max_lines=1)
        txt = f.lines[0] if f.lines else s
        w = min(maxw, fit.width(txt) * f.px + 28)
        self.ko("yp", f'<div class="e srcslip" style="left:{x - 12:.0f}px;top:{y - 6:.0f}px;width:{w:.0f}px;height:{f.px * 1.3 + 12:.0f}px;background:{{c}}"></div>')
        self.ko("b", f'<div class="e srcslip" style="left:{x - 12:.0f}px;top:{y - 6:.0f}px;width:{w:.0f}px;height:{f.px * 1.3 + 12:.0f}px;background:{{c}}"></div>')
        for k in ORDER:          # second hits stop at the slip too
            self.hit[k].append(f'<div class="e srcslip" style="left:{x - 12:.0f}px;top:{y - 6:.0f}px;width:{w:.0f}px;height:{f.px * 1.3 + 12:.0f}px;background:#fff"></div>')
        self.text("b", x, y, f.px, txt, "src", color=BLUE2)

    def html(self, i):
        reg = misreg(i)
        out = []
        for k in ORDER:
            dx, dy = reg[k]
            out.append(f'<div class="ink i{k}" data-layout-allow-overlap style="translate:{dx}px {dy}px">{self.defs(k)}<div class="pl">{"".join(self.pl[k])}</div>'
                       f'<div class="mot" style="background-image:url(&quot;{MOTTLE[k]}&quot;);background-position:{(i * 173) % 700}px {(i * 91) % 700}px"></div>'
                       f'<div class="grn" style="background-image:url(&quot;{GRAIN[k]}&quot;);opacity:{GRAIN_OP[k]};background-position:{(i * 61) % 360}px {(i * 37) % 360}px"></div>'
                       f'<div class="band" style="background-position:0 {(i * 47) % 140}px"></div></div>')
        for k in ORDER:
            if not self.hit[k]: continue
            dx, dy = reg[k]
            out.append(f'<div class="ink2 h{k}" data-layout-allow-overlap style="translate:{dx}px {dy}px"><div class="pl">{"".join(self.hit[k])}</div>'
                       f'<div class="grn" style="background-image:url(&quot;{GRAIN[k]}&quot;);opacity:{GRAIN_OP[k]};background-position:{(i * 29) % 360}px {(i * 53) % 360}px"></div></div>')
        return "".join(out)


# ---------------------------------------------------------------- print-shop furniture
CROSS = ('<svg class="e rzx" style="left:{x}px;top:{y}px;width:40px;height:40px" viewBox="0 0 40 40"><g fill="none" stroke="{c}" stroke-width="2.4">'
         '<circle cx="20" cy="20" r="11"/><line x1="0" y1="20" x2="40" y2="20"/><line x1="20" y1="0" x2="20" y2="40"/></g></svg>')


def furniture(sh, i, n):
    """slug + ink swatches (y 204 in 9:16), registration crosses in the corners (all three plates), colour bar on the bottom edge."""
    X = sh.X
    W, H, P = X.W, X.H, X.portrait
    sx, sy = (72, 213) if P else (96, 34)      # 9:16: the slug's ink stays below y 204 whatever the plate's registration error
    slug = f"RISO · 3 COLOUR · {i + 1:02d}/{n:02d}"
    sh.text("b", sx, sy, 26, slug, "mo rz-slug", color=BLUE2, style="line-height:30px")
    sw0 = sx + 26 * 0.6 * len(slug) + 26 * 0.06 * len(slug) + 22
    for k, ink in enumerate(ORDER):
        sh.put(ink, f'<div class="e rz-sw" style="left:{sw0 + k * 40:.0f}px;top:{sy + 1}px;width:28px;height:28px;border-radius:50%;background:{{c}}"></div>')
    m = 22
    for (x, y) in ((m, m if not P else 150), (W - 40 - m, m if not P else 150), (m, H - 40 - (72 if P else 44)), (W - 40 - m, H - 40 - (72 if P else 44))):
        sh.put("ypb", CROSS.replace("{x}", str(x)).replace("{y}", str(y)))
    # colour bar: solids, overprints, then each ink at 70 / 50 / 30 / 15 %
    bh = 60 if P else 36
    y0 = H - bh
    pw = 60 if P else 80
    cells = ["y", "p", "b", "yp", "pb", "yb", "ypb"]
    x = 0
    for c in cells:
        sh.rect(c, x, y0, pw, bh, "cbar")
        x += pw
    for k in "pby":
        for tint in (0.7, 0.5, 0.3, 0.15):
            if x >= W: break
            sh.rect(k, x, y0, pw, bh, "cbar", tint=tint)
            x += pw
    while x < W:
        sh.rect("ypb"[(x // pw) % 3], x, y0, pw, bh, "cbar", tint=0.15)
        x += pw


def headline(sh, s, x=None, y=None, w=None, hi=170, lo=120):
    """the Chinese headline: heaviest CJK sans, 120–170 px, at most two lines, top-left; overprint black."""
    from h9 import fit
    X = sh.X
    P = X.portrait
    x = x if x is not None else (72 if P else 96)
    y = y if y is not None else (236 if P else 82)
    w = w or ((X.W - 144) if P else 1100)
    f = fit.fit_text(s, w, hi * 2.4, hi, lo, lh=1.15, max_lines=2 if "|" in str(s) else 1)
    for j, line in enumerate(f.lines):
        sh.black(x, y + j * f.px * 1.15, f.px, line, "cn hd")
    return f.px, y + len(f.lines) * f.px * 1.15


# ---------------------------------------------------------------- page, passes, pull-off
PASS = 5          # frames per pass (a hard-edged wipe, top → bottom)
GAP = 2           # frames between passes


def page(X, b, cid, t, d, sh, src=True):
    """one sheet. It slides in under the previous sheet; while that one is pulled off (7 frames) the drum is already
    printing, so the page is complete by frame 17 of the beat: yellow −2…3, pink 5…10, blue 12…17 (beat 1: 0…5, 6…11, 12…17)."""
    X.css("riso", CSS.replace("__PAPER__", PAPER).replace("__FIBRE__", FIBRE))
    i, n = X.beat["i"], X.beat["n"]
    furniture(sh, i, n)
    if src:
        s_ = b.get("src", X.v.get("meta", {}).get("src", ""))
        if X.portrait: sh.source(72, 1452, s_, 828)
        else: sh.source(96, X.H - 36 - 52, s_, 1100)
    D = X.duration or (t + d)
    last = t + d >= D - 0.01
    first = i == 0
    t_in = t if first else t - 2 / FPS
    end = t + d if last else t + d + 0.25          # stays on top while it is pulled off
    html = f'<div class="rzw"><div class="rz"><div class="fib"></div>{sh.html(i)}</div></div>'
    X.clip(cid, t_in, end - t_in, html, "scene", 40 - i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    if not last:
        X.tw(f'tl.to("{s} .rzw", {{yPercent:-110, duration:{7 / FPS:.3f}, ease:"power2.in"}}, {t + d:.3f});')
        X.sfx(t + d - 0.02, "transition")
    land = passes(X, s, t_in, 1 if first else GAP)
    # the source slip is knocked out of every plate: it shows up with the blue pass that carries its type, never as an empty bar
    X.tw(f'tl.from("{s} .srcslip", {{autoAlpha:0, duration:0.01}}, {land - 2 / FPS:.3f});')
    return s, land


def passes(X, s, t0, gap):
    t = t0
    for k in ORDER:
        X.tw(f'tl.fromTo("{s} .ink.i{k}", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{PASS / FPS:.3f}, ease:"steps(3)"}}, {t:.3f});')
        X.sfx(t, "pass")
        t += (PASS + gap) / FPS
    return t - gap / FPS


def second(X, s, ink, t, dur=0.33):
    """a second hit: the same drum runs again over one shape (pulled left → right), the ink deepens under multiply."""
    X.tw(f'tl.fromTo("{s} .ink2.h{ink}", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{dur:.3f}, ease:"steps({max(2, round(dur * 12))})"}}, {t:.3f});')
    X.sfx(t, "line")


def jitter(X, s, t, d, ink):
    """held frame: one plate jumps 1 px every 6 frames."""
    if d < 0.5: return
    per = 6 / FPS
    rep = max(1, int(d / per) - 1)
    X.tw(f'tl.to("{s} .ink.i{ink} > .pl", {{x:1, duration:{per:.3f}, ease:"steps(1)", repeat:{rep}, yoyo:true}}, {t:.3f});')


def stamp(X, sel, t):
    """a stamp hits the sheet: two stepped frames from oversize to flat (4 frames)."""
    X.tw(f'tl.from("{sel}", {{scale:1.3, rotation:-4, duration:{4 / FPS:.3f}, ease:"steps(2)", transformOrigin:"0% 50%"}}, {t:.3f});')
    X.tw(f'tl.from("{sel}", {{autoAlpha:0, duration:0.01}}, {t:.3f});')
    X.sfx(t, "slam")


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def numfit(value, suffix, w, lo, hi):
    """the biggest Anton size ≤ hi whose figure (+ small suffix) fits w; never below lo."""
    em = anton_w(value) * 0.985 + (anton_w(suffix) * 0.42 + 0.04 if suffix and all(c in "%+-." for c in suffix) else (0.42 * len(suffix) + 0.04 if suffix else 0))
    return max(lo, min(hi, w / max(0.5, em))), em


def parse(v):
    s = str(v).replace(",", "")
    dec = len(s.split(".")[1]) if "." in s else 0
    try: return float(s), dec
    except ValueError: return None, 0


def black_tag(sh, x, y, tp, text, cls="tg"):
    """a label block: double-hit blue on one plate with the words knocked out to paper; yellow, pink and every
    second hit are knocked out under it, so nothing offsets or ghosts the type (≥ 9:1 against the block)."""
    from h9 import fit
    X = sh.X
    tw = fit.width(text) * tp + 2 * tp * 0.5
    box = f'<div class="e {cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{tw:.0f}px;height:{tp * 1.5:.0f}px;background:{{c}}"></div>'
    sh.ko("yp", box)
    for k in ORDER:
        sh.hit[k].append(box.replace("{c}", "#fff"))
    sh.pl["b"].append(box.replace("{c}", BLUE2))
    sh.pl["b"].append(f'<div class="t cn {cls}" style="left:{x + tp * 0.5:.0f}px;top:{y + tp * 0.16:.0f}px;font-size:{tp}px;color:#fff">{X.rich(text)}</div>')
    X.used_text.update(text)


# ---------------------------------------------------------------- scenes
# every beat: complete by frame 17 (all primaries on the three passes); after that only secondary print events
# (a stamp, a second hit that deepens one shape, registration jitter) — nothing the viewer needs arrives late.
def hero(b, X, t, d, cid):
    """大数字：黄色大版压到底、粉色网点大圆从右下出血；数字蓝版 + 粉色影子，印好就是终值；然后叠印黑签盖下，粉圆第二遍加深。"""
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    big, suf = str(b.get("big", "")), b.get("suffix", "")
    if P:
        sh.rect("y", 0, 400, W, H - 400, "slab")
        sh.circle("p", 930, 1330, 600, "disc", tint=0.5)
        sh.circle("p", 930, 1330, 600, "disc2", tint=0.3, hit=True)
        headline(sh, b.get("head", ""))
        px, em = numfit(big, suf, 900, 380, 560)
        nx, ny = 72, 470
    else:
        sh.rect("y", 760, 0, W - 760, H, "slab")
        sh.circle("p", 1620, 760, 520, "disc", tint=0.5)
        sh.circle("p", 1620, 760, 520, "disc2", tint=0.3, hit=True)
        headline(sh, b.get("head", ""), w=1000)
        px, em = numfit(big, suf, 1000, 300, 460)
        nx, ny = 96, 300
    sh.numeral(nx, ny, px, big, suf, "b", "p", "hn")
    unit = b.get("unit", "")
    uy = ny + px * 1.0 + 6
    if unit: sh.black(nx + 6, uy, 96 if P else 80, unit, "cn un")
    tag = b.get("tag", "")
    if tag:
        from h9 import fit
        black_tag(sh, nx + (fit.width(unit) * (96 if P else 80) + 44 if unit else 0), uy + (14 if P else 10), 56 if P else 48, tag)
    s, land = page(X, b, cid, t, d, sh)
    if tag: stamp(X, f"{s} .tg", land + 4 / FPS)
    second(X, s, "p", t + 1.4)
    jitter(X, s, t + 1.0, d - 1.0, "p")


def circles(b, X, t, d, cid):
    """对比 = 两个叠印圆，面积按真实比例：蓝圆、粉圆各印一版，重叠处是二次色紫；数字印好就是终值，之后粉圆第二遍加深、重叠更紫。"""
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    a, c = b.get("a", {}), b.get("b", {})
    va, vb = float(a.get("value", 1)), float(c.get("value", 1))
    big = max(va, vb)
    headline(sh, b.get("head", ""), w=(W - 144) if P else 900)
    if P:
        R = 600
        ca, cb = (290, 1440), (800, 1000)
        la, lb = (72, 1010), (72, 470)
        npx = 300
    else:
        R = 470
        ca, cb = (1180, 780), (1600, 420)
        la, lb = (96, 590), (96, 290)
        npx = 210
    ra, rb = R * math.sqrt(va / big), R * math.sqrt(vb / big)
    sh.circle("b", ca[0], ca[1], ra, "ca")
    sh.circle("p", cb[0], cb[1], rb, "cb")
    sh.circle("p", cb[0], cb[1], rb, "cb2", tint=0.5, hit=True)
    sh.circle("b", ca[0], ca[1], ra, "ca2", tint=0.3, hit=True)
    lp = 60 if P else 52
    sh.small(lb[0], lb[1], lp, c.get("label", ""), "cn lbb")
    sh.numeral(lb[0], lb[1] + lp * 1.2, npx, c.get("show", ""), c.get("unit", ""), "b", "p", "nb")
    if P:
        sh.ko("b", f'<div class="t cn lba" style="left:{la[0]:.0f}px;top:{la[1]:.0f}px;font-size:{lp}px;color:{{c}}">{X.rich(a.get("label", ""))}</div>')
        sh.numeral(la[0], la[1] + lp * 1.2, npx, a.get("show", ""), a.get("unit", ""), None, "p", "na", knock="b")
    else:
        sh.small(la[0], la[1], lp, a.get("label", ""), "cn lba")
        sh.numeral(la[0], la[1] + lp * 1.2, npx, a.get("show", ""), a.get("unit", ""), "b", "y", "na")
    X.used_text.update(a.get("label", "") + c.get("label", ""))
    s, land = page(X, b, cid, t, d, sh)
    second(X, s, "p", t + 1.3)
    second(X, s, "b", t + 2.9)          # then the blue disc gets its own half-tone hit
    jitter(X, s, t + 1.0, d - 1.0, "b")


def bands(b, X, t, d, cid):
    """增长 = 刮板色带：整摞是黄版，今年多出来的那一截再压一遍粉（粉压黄成橙红），高度按真实数值从底边往上叠；
    涨幅蓝版大数字印好就是终值；之后粉带第二遍加深。"""
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    lo_, hi_ = b.get("base", {}), b.get("top", {})
    v0, v1 = float(lo_.get("value", 1)), float(hi_.get("value", 1))
    headline(sh, b.get("head", ""), w=(W - 144) if P else 820)
    big, suf = str(b.get("big", "")), b.get("suffix", "")
    if P:
        top = 820
        tot = H - top
        h0 = tot * v0 / v1
        sh.rect("y", -10, top, W + 20, tot, "bd0")                 # the whole stack: one yellow band
        sh.rect("p", -10, top, W + 20, tot - h0, "bd1")            # this year's extra: pink pulled over the yellow
        sh.rect("p", -10, top, W + 20, tot - h0, "bd2", hit=True)
        sh.rect("y", -10, top, W + 20, tot, "bd3", tint=0.3, hit=True)
        px, em = numfit(big, suf, 900, 340, 460)
        nx, ny = 72, 430
        lx, lp = 72, 64
        y1 = top + 34; y0 = H - h0 + 34
    else:
        left = 900
        tot = H - 150
        h0 = tot * v0 / v1
        sh.rect("y", left, 150, W - left + 10, tot, "bd0")
        sh.rect("p", left, 150, W - left + 10, tot - h0, "bd1")
        sh.rect("p", left, 150, W - left + 10, tot - h0, "bd2", hit=True)
        sh.rect("y", left, 150, W - left + 10, tot, "bd3", tint=0.3, hit=True)
        px, em = numfit(big, suf, 760, 260, 400)
        nx, ny = 96, 300
        lx, lp = left + 48, 60
        y1 = 150 + 30; y0 = H - h0 + 30
    sh.numeral(nx, ny, px, big, suf, "b", "p", "gn")
    for (lab, yy, cls) in ((hi_, y1, "l1"), (lo_, y0, "l0")):
        sh.text("b", lx, yy, lp, f'{lab.get("label", "")}', "nm " + cls, color=BLUE2, style="letter-spacing:0")
        sh.small(lx + anton_w(lab.get("label", "")) * lp + 28, yy + lp * 0.08, lp * 0.9, lab.get("show", ""), "cn " + cls)
    note = b.get("note", "")
    if note:
        sh.small(lx, y0 + lp * 1.35 if P else y0 + lp * 1.4, 40, note, "bd l0n")
    s, land = page(X, b, cid, t, d, sh)
    second(X, s, "p", t + 1.3, 0.42)
    second(X, s, "y", t + 3.0)           # then the yellow stack gets a half-tone second hit
    jitter(X, s, t + 1.0, d - 1.0, "y")


def grid(b, X, t, d, cid):
    """占比 = 10×10 网点格：蓝版 100 个网点，粉版压在占比那几格上（粉压蓝成紫），印好即是终值；之后粉版第二遍把占比压得更深。"""
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    pct = max(0.0, min(100.0, float(b.get("pct", 50))))
    headline(sh, b.get("head", ""), w=(W - 144) if P else 820)
    big, suf = str(b.get("big", f"{pct:g}")), b.get("suffix", "%")
    if P:
        sh.rect("b", 0, 740, W, H - 740, "slab")
        px, em = numfit(big, suf, 900, 340, 360)
        nx, ny = 72, 400
        gx, gy, pitch = 72, 758, 55
        lgx, lgy = 72 + 10 * pitch + 36, 790
    else:
        sh.rect("b", 1000, 0, W - 1000, H, "slab")
        px, em = numfit(big, suf, 780, 260, 380)
        nx, ny = 96, 300
        gx, gy, pitch = 1100, 150, 68
        lgx, lgy = 1100, 150 + 10 * 68 + 30
    sh.numeral(nx, ny, px, big, suf, "b", "p", "sn")
    r = pitch * 0.43
    full = int(pct)
    part = pct - full
    dots_b, dots_p = [], []
    for j in range(100):
        cx = (j % 10) * pitch + pitch / 2
        cy = (j // 10) * pitch + pitch / 2
        dots_b.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>')
        if j < full:
            dots_p.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>')
        elif j == full and part > 0:
            dots_p.append(f'<clipPath id="{cid}pc{{k}}"><rect x="{cx - r:.1f}" y="{cy - r:.1f}" width="{2 * r * part:.1f}" height="{2 * r:.1f}"/></clipPath>'
                          f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" clip-path="url(#{cid}pc{{k}})"/>')
    gw = 10 * pitch
    ww = (lgx + 300 - gx + 36) if P else gw + 36
    wh = gw + 36 if P else gw + 36 + 150
    sh.rect("b", gx - 18, gy - 18, ww, wh, "gwin", ko=True)       # grid + legend sit in a paper window cut out of the blue slab
    sh.put("b", f'<svg class="e gb" style="left:{gx}px;top:{gy}px;width:{gw}px;height:{gw}px" viewBox="0 0 {gw} {gw}"><g fill="{{c}}">{"".join(dots_b)}</g></svg>')
    share = "".join(dots_p)
    sh.put("p", f'<svg class="e gp" style="left:{gx}px;top:{gy}px;width:{gw}px;height:{gw}px" viewBox="0 0 {gw} {gw}"><g fill="{{c}}">{share.replace("{k}", "a")}</g></svg>')
    sh.hit["p"].append(f'<svg class="e gp2" style="left:{gx}px;top:{gy}px;width:{gw}px;height:{gw}px" viewBox="0 0 {gw} {gw}"><g fill="{PINK}">{share.replace("{k}", "b")}</g></svg>')
    lp = 40 if P else 38
    for k, it in enumerate(b.get("legend", [])[:2]):
        yy = lgy + k * (lp * 3.2) if P else lgy
        xx = lgx if P else lgx + k * 340
        sh.circle("pb" if k == 0 else "b", xx + 22, yy + lp * 0.62, 22, f"lg{k}")
        sh.small(xx + 58, yy, lp, it.get("label", ""), f"bd lg{k}")
        sh.text("b", xx + 58, yy + lp * 1.25, lp * 1.5, it.get("value", ""), f"nm lg{k}", color=BLUE2, style="letter-spacing:0")
    s, land = page(X, b, cid, t, d, sh)
    second(X, s, "p", t + 1.3)
    jitter(X, s, t + 1.0, d - 1.0, "p")


def strips(b, X, t, d, cid):
    """排行 = 色纸条：粉色网点大底上，每条按数值裁长度、从左边出血（底下的粉被镂掉），纸条各是一种墨或叠印色；
    之后每条按顺序再过一遍墨加深。"""
    from h9 import fit
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    items = b.get("items", [])[:5]
    vmax = max(float(it.get("value", 1)) for it in items) if items else 1
    headline(sh, b.get("head", ""), w=(W - 144) if P else 1500)
    if P:
        sh.rect("p", 0, 400, W, H - 400, "field", tint=0.3)
        y0, hh, gap, full, x0 = 446, 150, 22, W + 30, 72
    else:
        sh.rect("p", 0, 250, W, H - 250, "field", tint=0.3)
        y0, hh, gap, full, x0 = 290, 118, 18, 1700, 96
    inks = ["B", "pb", "yb", "b", "y"]       # B = double-hit blue; type is knocked out only of the dark swatches (≥ 5.7:1)
    for k, it in enumerate(items):
        v = float(it.get("value", 0))
        L = max(60.0, full * v / vmax)
        y = y0 + k * (hh + gap)
        sh.rect("p", -20, y, L + 20, hh, f"sp sp{k}", ko=True)            # the swatch replaces the pink field under it
        if inks[k] == "B":
            sh.pl["b"].append(f'<svg class="e sp sp{k}" style="left:-20px;top:{y:.0f}px;width:{L + 20:.0f}px;height:{hh}px" viewBox="0 0 {L + 20:.0f} {hh}"><rect width="{L + 20:.0f}" height="{hh}" fill="{BLUE2}"/></svg>')
        else:
            sh.rect(inks[k], -20, y, L + 20, hh, f"sp sp{k}")
        hk = inks[k][-1].lower()
        sh.rect(hk, -20, y, L + 20, hh, f"sx sx{k}", tint=0.5, hit=True)
        nm, fig = it.get("name", ""), it.get("show", str(it.get("value", "")))
        npx = 52 if P else 46
        fpx = 104 if P else 92
        need = fit.width(nm) * npx + anton_w(fig) * fpx + 90
        inside = L - x0 > need and inks[k] == "B"       # one plate only: knocked-out type cannot fringe
        tx = x0 if inside else L + 24
        ty = y + (hh - fpx) / 2
        if inside:
            sh.ko("b", f'<div class="t nm sf{k}" style="left:{tx:.0f}px;top:{ty:.0f}px;font-size:{fpx}px;color:{{c}};letter-spacing:0">{fig}</div>')
            sh.ko("b", f'<div class="t cn sn{k}" style="left:{tx + anton_w(fig) * fpx + 26:.0f}px;top:{y + (hh - npx * 1.15) / 2:.0f}px;font-size:{npx}px;color:{{c}}">{X.rich(nm)}</div>')
            # the swatch's second hit keeps its knocked-out type clean: these knock-outs are in the hit layer from frame 0,
            # outside the wipe, so no dot ever prints over the type
            sh.hit[hk].append(f'<div class="t nm sxk" style="left:{tx:.0f}px;top:{ty:.0f}px;font-size:{fpx}px;color:#fff;letter-spacing:0">{fig}</div>')
            sh.hit[hk].append(f'<div class="t cn sxk" style="left:{tx + anton_w(fig) * fpx + 26:.0f}px;top:{y + (hh - npx * 1.15) / 2:.0f}px;font-size:{npx}px;color:#fff">{X.rich(nm)}</div>')
        else:
            sh.black(tx, ty, fpx, fig, f"nm sf{k}", style="letter-spacing:0")
            sh.small(tx + anton_w(fig) * fpx + 22, y + (hh - npx * 1.15) / 2, npx, nm, f"bd sn{k}")
        X.used_text.update(nm + fig)
    s, land = page(X, b, cid, t, d, sh)
    # second hits: each swatch gets a half-tone pass of its own ink, in rank order, from 1.1 s
    for k in range(len(items)):
        X.tw(f'tl.from("{s} .sx{k}", {{clipPath:"inset(0% 100% 0% 0%)", duration:{6 / FPS:.3f}, ease:"steps(2)"}}, {t + 1.1 + k * 0.3:.3f});')
        X.sfx(t + 1.1 + k * 0.3, "line")
    X.tw(f'tl.set("{s} .ink2", {{clipPath:"inset(0% 0% 0% 0%)"}}, {t:.3f});')
    jitter(X, s, t + 1.0, d - 1.0, "b")


def swap(b, X, t, d, cid):
    """数字换版：去年的数字印好、停 10 帧，然后一帧换成今年的，黄色大圆按新数值重印变大，"历史新高"叠印黑签同时盖下；之后黄圆第二遍加深。"""
    from h9 import fit
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    a, z = str(b.get("from", "")), str(b.get("to", ""))
    suf = b.get("suffix", "%")
    headline(sh, b.get("head", ""), w=(W - 144) if P else 820)
    va, da = parse(a)
    vz, dz = parse(z)
    k = math.sqrt(va / vz) if va and vz else 0.9
    if P:
        disc = (720, 1480, 840)
        px, em = numfit(z, suf, 920, 380, 560)
        nx, ny = 72, 440
        wy = 1010
    else:
        disc = (1500, 760, 620)
        px, em = numfit(z, suf, 860, 300, 460)
        nx, ny = 96, 290
        wy = 800
    sh.circle("y", disc[0], disc[1], disc[2], "disc")
    sh.circle("y", disc[0], disc[1], disc[2], "disc2", tint=0.7, hit=True)
    sh.numeral(nx, ny, px, a, suf, "b", "p", "mn", g=13)
    was = b.get("was", "")
    wp = 44 if P else 40
    if was:
        sh.rect("p", nx - 12, wy - 8, fit.width(was) * wp + 24, wp * 1.3 + 16, "was")
        sh.small(nx, wy, wp, was, "bd was")
    tag = b.get("tag", "")
    if tag: black_tag(sh, nx, wy + wp * 1.3 + 40, 64 if P else 56, tag)
    s, land = page(X, b, cid, t, d, sh)
    tc = land + 10 / FPS                       # the old figure holds 10 frames, then the plate is swapped in one frame
    X.tw(f'tl.set("{s} .mn .nv", {{textContent:"{z}"}}, {tc:.3f});')
    X.tw(f'tl.fromTo("{s} .disc, {s} .disc2", {{scale:{k:.3f}, transformOrigin:"50% 50%"}}, {{scale:1, duration:{2 / FPS:.3f}, ease:"steps(1)"}}, {tc:.3f});')
    X.used_text.update(z)
    X.sfx(tc, "hit")
    if tag: stamp(X, f"{s} .tg", tc)
    second(X, s, "y", t + 1.5)
    jitter(X, s, t + 1.2, d - 1.2, "b")


def statement(b, X, t, d, cid):
    """判断句：蓝色大实地压到底，判断句从蓝版里镂空；拆分条粉压蓝成紫、黄压蓝成绿，印好即完整；之后紫那一段第二遍加深，粉色网点再扫一遍。"""
    from h9 import fit
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    headline(sh, b.get("head", ""), w=(W - 144) if P else 1500)
    lines = [x for x in str(b.get("say", "")).split("|") if x]
    pct = float(b.get("pct", 50))
    parts = b.get("parts", [])
    if P:
        top = 560
        sh.rect("b", 0, top, W, H - top, "slab")
        sh.circle("p", 930, 1640, 460, "dot", tint=0.3)
        sx, sy, sw = 72, 620, W - 144
        bx, by, bw, bh = 72, 1000, 936, 130
    else:
        top = 250
        sh.rect("b", 0, top, W, H - top, "slab")
        sh.circle("p", 640, 1000, 420, "dot", tint=0.3)
        sx, sy, sw = 96, 300, 1000
        bx, by, bw, bh = 1100, 330, 720, 200
    f = fit.fit_text("|".join(lines), sw, 400, 170, 120, lh=1.15, max_lines=2)
    for j, line in enumerate(f.lines):
        sh.ko("b", f'<div class="t cn say" style="left:{sx:.0f}px;top:{sy + j * f.px * 1.15:.0f}px;font-size:{f.px:.0f}px;color:{{c}}">{X.rich(line)}</div>')
        X.used_text.update(line)
    cut = bw * pct / 100
    sh.rect("p", bx, by, cut, bh, "bp")
    sh.rect("y", bx + cut, by, bw - cut, bh, "by")
    sh.rect("p", bx, by, cut, bh, "bp2", hit=True)
    lp = 40 if P else 38
    for k, it in enumerate(parts[:2]):
        xx = bx if k == 0 else bx + cut + 16
        sh.ko("b", f'<div class="t cn pl{k}" style="left:{xx:.0f}px;top:{by + bh + 18:.0f}px;font-size:{lp}px;color:{{c}}">{X.rich(it)}</div>')
        X.used_text.update(it)
    s, land = page(X, b, cid, t, d, sh)
    second(X, s, "p", t + 1.3)
    jitter(X, s, t + 1.0, d - 1.0, "y")


def outro(b, X, t, d, cid):
    """落版：三个圆各在一块版上，随三遍印刷到位（0.6 s 内全在），然后从套不准一格一格挪进套准；示例频道名叠印黑，停到片尾。"""
    P, W, H = X.portrait, X.W, X.H
    sh = Sheet(X, cid)
    title, sub = b.get("title", ""), b.get("sub", "")
    if P:
        r = 450
        cs = [(300, 1260), (800, 1260), (550, 1660)]
        headline(sh, title, hi=170, lo=150)
        if sub: sh.small(72, 236 + 170 * 1.15 + 12, 72, sub, "cn sub")
    else:
        r = 360
        cs = [(1250, 420), (1650, 420), (1450, 780)]
        headline(sh, title, w=900, hi=170, lo=150)
        if sub: sh.small(96, 82 + 170 * 1.15 + 16, 64, sub, "cn sub")
    for k, ink in enumerate(ORDER):
        sh.circle(ink, cs[k][0], cs[k][1], r, f"oc oc{k}")
    s, land = page(X, b, cid, t, d, sh, src=False)
    offs = [(-36, -22), (40, -16), (0, 42)]
    for k in range(3):
        ox, oy = offs[k]
        X.tw(f'tl.fromTo("{s} .oc{k}", {{x:{ox}, y:{oy}}}, {{x:0, y:0, duration:{4 / 12:.3f}, ease:"steps(4)"}}, {t + 0.62 + k * 0.1:.3f});')
    X.sfx(t + 1.0, "slam")
    jitter(X, s, t + 1.3, d - 1.3, "p")


SCENES = {"hero": hero, "circles": circles, "bands": bands, "grid": grid, "strips": strips, "swap": swap,
          "statement": statement, "outro": outro}


# ---------------------------------------------------------------- effects in this style (fx beats / gallery cards)
STYLE["fx_themes"] = {
    "paper": {"bg": PAPER, "fg": NAVY, "muted": "#3a4a8a", "accent": BLUE, "card": "#fbf9f3", "card-fg": NAVY, "line": "#d9d3c4"},
    "red":   {"bg": PINK, "fg": NAVY, "muted": "#3a1f6e", "accent": "#fff6a8", "card": PAPER, "card-fg": NAVY, "line": "rgba(0,33,131,.25)"},
    "ink":   {"bg": BLUE2, "fg": PAPER, "muted": "#c9d4ee", "accent": YEL, "card": "#123f96", "card-fg": PAPER, "line": "rgba(242,239,230,.25)"},
    "lemon": {"bg": YEL, "fg": NAVY, "muted": "#2b3a7a", "accent": "#c7007a", "card": PAPER, "card-fg": NAVY, "line": "rgba(0,33,131,.2)"},
}

FX_CSS = r"""
/* the effect's ground is the same uncoated sheet: fibre + soy-ink mottling, no vignette */
.fx { background-image:url("__FIBREFX__") !important; background-size:480px !important; }
.fx .big, .fx .op .op-t { text-shadow:.035em .035em 0 color-mix(in srgb, var(--accent) 70%, transparent); }
.fx .col > .sub { background:var(--card); color:var(--card-fg); padding:.6vmin 1.8vmin .7vmin; letter-spacing:.2em; font-family:var(--f-mono); font-weight:400; }
.fx .sc .sc-c, .fx .nt .nt-cv, .fx .wp-mock { border-radius:0 !important; }
.fx .bu .dot, .fx .iu .iulg i { border-radius:50%; }
.fx .dn .dntr { stroke:color-mix(in srgb, var(--accent) 22%, var(--bg)); }
/* the page around an effect card (FX_FRAME): slug + swatches, registration crosses, colour bar, blue caption strip */
.ctx.rzc .hd { left:96px; right:96px; top:34px; height:auto; border:none; display:flex; justify-content:space-between; align-items:center; }
.ctx.rzc .hd .slug { font-family:var(--f-mono); font-size:24px; letter-spacing:.06em; color:#00388f; background:#fff8; padding:2px 10px; }
.ctx.rzc .hd .sw { display:flex; gap:12px; } .ctx.rzc .hd .sw i { width:26px; height:26px; border-radius:50%; mix-blend-mode:multiply; }
.ctx.rzc .cross { position:absolute; width:40px; height:40px; mix-blend-mode:multiply; }
.ctx.rzc .cbar { position:absolute; left:0; right:0; bottom:0; height:36px; display:flex; }
.ctx.rzc .cbar i { flex:1; mix-blend-mode:multiply; }
.ctx.rzc .cap { left:96px; right:auto; bottom:96px; text-align:left; }
.ctx.rzc .cap > span { display:inline-block; background:#00388f; color:#f2efe6; font-family:var(--f-body); font-weight:700; padding:16px 28px; border-radius:0;
  -webkit-mask:linear-gradient(#000 0 0) left/calc(100% - 12px) 100% no-repeat, radial-gradient(circle, #000 3.6px, transparent 4.2px) right top/12px 12px repeat-y; }
.ctx.rzc .cap .em .emt { color:#ffe800; background:none !important; box-shadow:none !important; padding:0; }
.ctx.rzc .cap .em .emb { display:none !important; }
.ctx.rzc .ft { left:96px; right:96px; bottom:44px; opacity:1; color:#00388f; font-size:17px; }
#root.v .ctx.rzc .hd { left:72px; right:120px; top:204px; }
#root.v .ctx.rzc .cap { left:72px; right:auto; top:auto; bottom:520px; padding:0; max-width:860px; }
#root.v .ctx.rzc .ft { left:72px; right:180px; top:1452px; bottom:auto; flex-direction:column; align-items:flex-start; gap:6px; }
"""
FIBRE_FX = FIBRE.replace("0 0 0 -2.2 1.25", "0 0 0 -.3 .17")       # the same fibre at ~ 13 % for effect pages
STYLE["css"] = FX_CSS.replace("__FIBREFX__", FIBRE_FX)


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect in riso: print-shop slug + ink swatches, four registration crosses, the colour bar on the
    bottom edge, the spoken line as a solid-blue strip with knocked-out paper type and a halftone right edge."""
    P, W, H = X.portrait, X.W, X.H
    cross = ('<svg class="cross" style="left:{x}px;top:{y}px" viewBox="0 0 40 40"><g fill="none" stroke="{c}" stroke-width="2.4">'
             '<circle cx="20" cy="20" r="11"/><line x1="0" y1="20" x2="40" y2="20"/><line x1="20" y1="0" x2="20" y2="40"/></g></svg>')
    by = H - 36 - 52
    crosses = ""
    for (x, y) in ((22, 150 if P else 22), (W - 62, 150 if P else 22), (22, by), (W - 62, by)):
        for k, c in enumerate((YEL, PINK, BLUE)):
            crosses += cross.replace("{x}", str(x + (k - 1) * 3)).replace("{y}", str(y + (1 - k) * 2)).replace("{c}", c)
    bar = "".join(f'<i style="background:{c}"></i>' for c in (YEL, PINK, BLUE, "#ff4800", NAVY, "#007800", "#ff48b0", "#0078bf"))
    sw = "".join(f'<i style="background:{c}"></i>' for c in (YEL, PINK, BLUE))
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (crosses + f'<div class="cbar">{bar}</div>'
             + f'<div class="hd"><div class="slug">RISO · {parts["topic"]}</div><div class="sw">{sw}</div></div>'
             + f'<div class="cap"><span style="font-size:{max(40, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update("RISO · ")
    X.clip(f"{cid}c", t, d, inner, f"ctx rzc{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .cap > span", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{4 / 12:.3f}, ease:"steps(4)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .hd", {{clipPath:"inset(0% 0% 100% 0%)", duration:{3 / 12:.3f}, ease:"steps(3)"}}, {t + 0.02:.3f});')


# the subtitle: a strip of the same paper printed solid blue (double hit, so paper type reads at ≥ 4.5:1),
# squared ends, a one-step halftone edge on the right; 9:16 at y 1316–1400, left at x 72
STYLE["css"] += """
.st-riso .cap { text-align:left; }
.st-riso .cap .cp { line-height:1.3; letter-spacing:.02em; max-width:860px;
  -webkit-mask:linear-gradient(#000 0 0) left/calc(100% - 12px) 100% no-repeat, radial-gradient(circle, #000 3.6px, transparent 4.2px) right 0 top 2px/12px 12px repeat-y;
  mask:linear-gradient(#000 0 0) left/calc(100% - 12px) 100% no-repeat, radial-gradient(circle, #000 3.6px, transparent 4.2px) right 0 top 2px/12px 12px repeat-y; }
#root.h.st-riso .clip.cap { padding-left:96px; padding-right:96px; }
#root.v.st-riso { --cap-bottom:520px; }
#root.v.st-riso .clip.cap { padding-left:72px; padding-right:148px; }
.st-riso .mascot { display:none !important; }
"""
