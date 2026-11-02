"""zine · 拼贴杂志风 —— DIY zine / 剪贴报的整套视觉语言：勒索信式剪字（每个字一块纸片、一种字体）、
复印机颗粒与网点、美纹纸胶带、订书钉、撕边、贴纸标签、马克笔涂画、邮票和邮戳。
动作按「一拍二」走（stop-motion：steps 缓动，每 2 帧一个位置），贴上去的纸片一直轻微抖动（boil）；镜头也一格一格地推。
三色孔版印刷（risograph）配色：荧光粉、孔雀绿、墨黑，印在复印纸上。每页开场是一张孔版色纸被撕走。

场景（SCENES，全部自写，输入长短 / 条目数自适应，横屏竖屏各自排版）：
cover 封面剪字 + 剪纸小怪兽 · versus 两个数字前后对比 + 印章 · pie 撕纸饼图 · bars 胶带纸条柱 · stamps 邮票墙 + 邮戳 ·
clip 报纸剪报 + 马克笔圈 · note 笔记本纸 + 跷跷板涂鸦 · thesis 剪字判断句（划掉一词、另一词砸下）· outro 封底。
剪字标记：*字* = 荧光粉纸片；~字~ = 马克笔标记（clip 里是圈，thesis 里是划掉）。
"""
import math, random
from h9 import fit

STYLE = {
    "name": "拼贴杂志风", "en": "Zine", "benchmarks": ["DIY punk / riot-grrrl zines", "Risograph print studios", "ransom-note collage typography"],
    "tokens": {
        "bg": "#ece7dc", "fg": "#141414", "muted": "#6d6860", "accent": "#ff3fa0", "accent2": "#00857f", "alert": "#ff3fa0",
        "line": "#cfc8ba", "paper": "#ece7dc", "ink": "#141414", "card": "#fbf8f0", "card-fg": "#141414",
        "pink": "#ff3fa0", "teal": "#00857f", "news": "#e2dccd", "white": "#fbf8f0",
        "cap-bg": "#141414", "cap-fg": "#fbf8f0", "cap-size": "38px", "cap-weight": "800", "cap-pad": "6px 18px 8px", "cap-radius": "0",
        "cap-shadow": "4px 5px 0 rgba(255,63,160,.85)", "cap-bottom": "46px", "cap-em": "#ff7cc0",
        "punch-top": "69%", "punch-size": "70px", "mascot-bg": "#ff3fa0",
    },
    # ransom letters draw on many faces; the free-commercial ones (kuhei, puhuiti) are not shipped, so every stack ends in an OFL face
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "serif": "noto-serif-sc", "kuhei": ["zcool-kuhei", "noto-sans-sc"],
              "qing": ["zcool-qingke", "noto-sans-sc"], "smiley": ["smiley-sans", "noto-sans-sc"], "xiaowei": ["zcool-xiaowei", "noto-serif-sc"],
              "puhui": ["alibaba-puhuiti-heavy", "zcool-kuhei", "noto-sans-sc"], "hand": ["lxgw-marker", "noto-sans-sc"],
              "brush": ["ma-shan-zheng", "noto-serif-sc"],
              "abril": ["abril-fatface", "zcool-kuhei", "noto-sans-sc"], "anton": ["anton", "zcool-kuhei", "noto-sans-sc"],
              "archivo": ["archivo-black", "zcool-kuhei", "noto-sans-sc"], "bebas": ["bebas", "zcool-kuhei", "noto-sans-sc"],
              "oswald": ["oswald", "zcool-kuhei", "noto-sans-sc"], "playfair": ["playfair", "noto-serif-sc"],
              "type": ["special-elite", "noto-sans-sc"], "courier": ["courier-prime", "noto-sans-sc"], "marker": ["permanent-marker", "zcool-kuhei", "noto-sans-sc"],
              "mono": ["courier-prime", "noto-sans-sc"]},
    "motion": {"ease": "steps(4)", "dur": 0.4, "stagger": 0.067, "cut": "hard", "transition": "hard", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.09})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 110, "bottom": 40, "h": 400}, "portrait": {"left": 390, "bottom": 600, "h": 310}},
    "outro": {"move": False},
    # effect pages as riso prints: photocopy paper, black toner, fluorescent pink, teal. hl = highlighter under keywords, zsh = hard print shadow
    "fx_themes": {
        "paper": {"bg": "#ece7dc", "fg": "#141414", "muted": "#5e5950", "accent": "#e0007a", "card": "#fbf8f0", "card-fg": "#141414", "line": "#cfc8ba",
                  "hl": "#ff3fa0", "zsh": "rgba(20,20,20,.85)"},
        "ink":   {"bg": "#1b1a19", "fg": "#f4efe4", "muted": "#a39b8d", "accent": "#ff3fa0", "card": "#fbf8f0", "card-fg": "#141414", "line": "#3a3734",
                  "hl": "#e8158a", "zsh": "#ff3fa0"},
        "red":   {"bg": "#ff3fa0", "fg": "#141414", "muted": "#5a1636", "accent": "#141414", "card": "#fbf8f0", "card-fg": "#141414", "line": "rgba(20,20,20,.25)",
                  "hl": "#ffe14a", "zsh": "#141414"},
        "lemon": {"bg": "#00857f", "fg": "#fbf8f0", "muted": "#f0f7f5", "accent": "#ffe14a", "card": "#fbf8f0", "card-fg": "#141414", "line": "rgba(251,248,240,.3)",
                  "hl": "#e8158a", "zsh": "#141414"},
    },
    "sfx": {"transition": ("paper", 0.4), "enter": ("paper", 0.45), "pop": ("pop", 0.4), "hit": ("slam", 0.45), "slam": ("slam", 0.5),
            "count": ("type", 0.3), "click": ("click", 0.35), "mascot": ("pop", 0.35), "tear": ("paper", 0.55), "stamp": ("hit", 0.55),
            "type": ("type", 0.35), "tape": ("tape", 0.4)},
    "css": """
.st-zine .cap .cp { font-family:var(--f-display); transform:rotate(-1deg); letter-spacing:.01em; }
.st-zine .cap .em .emt { color:var(--cap-em); }
#root.v.st-zine .cap-punch .cp { -webkit-text-stroke:0; padding:4px 18px 8px; background:#141414; color:#fbf8f0; box-shadow:5px 6px 0 rgba(255,63,160,.9); }
""",
}

INK, PAPER, PINK, TEAL, NEWS, WHITE = "#141414", "#ece7dc", "#ff3fa0", "#00857f", "#e2dccd", "#fbf8f0"
GLYPH_ROLES = ["display", "serif", "kuhei", "qing", "smiley", "xiaowei", "puhui", "hand", "brush", "display", "kuhei"]
NUM_ROLES = ["abril", "anton", "archivo", "bebas", "oswald", "playfair", "archivo", "anton", "type"]
SCRAPS = [(WHITE, INK), (WHITE, INK), (INK, WHITE), (NEWS, INK), (PINK, INK), (TEAL, WHITE), (WHITE, PINK), (NEWS, TEAL)]
PATTERNS = ["", "", "", "", "repeating-linear-gradient(45deg, rgba(0,0,0,.13) 0 2px, transparent 2px 7px)",
            "repeating-linear-gradient(0deg, rgba(0,0,0,.12) 0 2px, transparent 2px 6px)"]

NOISE = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'>"
         "<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='7'/>"
         "<feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .55 0'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")

CSS = r"""
.zn { position:absolute; inset:0; overflow:hidden; background:var(--paper); color:var(--ink); }
.zn.dark { background:#1b1a19; }
.zn .cam { position:absolute; inset:0; }
.zn .tex { position:absolute; inset:-60px; background-image:url("__NOISE__"); background-size:240px; opacity:.32; mix-blend-mode:multiply; pointer-events:none; }
.zn.dark > .tex { opacity:.5; mix-blend-mode:screen; filter:invert(1); }
.zn .xer { position:absolute; inset:0; pointer-events:none; box-shadow:inset 0 0 140px rgba(0,0,0,.28), inset 0 0 18px rgba(0,0,0,.35); }
.zn .streak { position:absolute; left:0; right:0; height:2px; background:rgba(0,0,0,.08); }
.zn .bo { position:absolute; }
.zn .sc { position:absolute; box-shadow:3px 5px 0 rgba(0,0,0,.16), 0 12px 26px rgba(0,0,0,.18); }
.zn .rlines { display:flex; flex-direction:column; align-items:flex-start; gap:.04em; }
.zn .rline { white-space:nowrap; }
.zn .rl { display:inline-block; line-height:1; margin:0 .025em .05em 0; font-style:normal; box-shadow:2px 3px 0 rgba(0,0,0,.24); }
.zn .rl.sp { background:none !important; box-shadow:none; width:.3em; }
.zn .mkw { position:relative; display:inline-block; white-space:nowrap; }
.zn .tape { position:absolute; height:30px; background:rgba(238,228,188,.8); box-shadow:0 1px 2px rgba(0,0,0,.18); }
.zn .tape.pk { background:rgba(255,63,160,.6); }
.zn .staple { position:absolute; width:46px; height:7px; border-radius:3px; background:linear-gradient(180deg,#d9d9d9,#8c8c8c); box-shadow:0 1px 1px rgba(0,0,0,.4); }
.zn .stamp { display:inline-block; border:7px solid currentColor; padding:.04em .3em .08em; font-family:var(--f-archivo); color:var(--pink); line-height:1; mix-blend-mode:multiply; white-space:nowrap; }
.zn.dark .stamp { mix-blend-mode:normal; }
.zn .stamp small { display:block; font-family:var(--f-type); font-size:.26em; letter-spacing:.12em; margin-top:.15em; }
.zn .stk { display:inline-block; padding:.18em .6em .24em; border-radius:999px; font-family:var(--f-puhui); white-space:nowrap; line-height:1;
  box-shadow:0 0 0 6px #fbf8f0, 5px 7px 0 6px rgba(0,0,0,.18); }
.zn .typed { font-family:var(--f-type); letter-spacing:.02em; white-space:nowrap; }
.zn .hand { font-family:var(--f-hand); white-space:nowrap; line-height:1.2; }
.zn .ht { position:absolute; inset:0; background-image:radial-gradient(circle, rgba(20,20,20,.42) 30%, transparent 33%); background-size:9px 9px; mix-blend-mode:multiply; pointer-events:none; }
.zn svg.mk { position:absolute; overflow:visible; pointer-events:none; }
.zn svg.mk path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.zn .peel { position:absolute; inset:-4% -14% -4% -4%; z-index:30; }
.zn .mast { position:absolute; z-index:8; background:#141414; color:#fbf8f0; font-family:var(--f-type); letter-spacing:.06em; white-space:nowrap; padding:6px 16px 7px; transform:rotate(-1.4deg); }
.zn .mast b { color:var(--pink); font-weight:400; }
.zn .pg { position:absolute; z-index:8; width:78px; height:78px; border-radius:50%; background:var(--pink); color:#141414; display:grid; place-items:center;
  font-family:var(--f-archivo); font-size:24px; transform:rotate(9deg); box-shadow:0 0 0 5px #fbf8f0, 4px 6px 0 5px rgba(0,0,0,.2); }
.zn .src { position:absolute; z-index:8; background:#fbf8f0; color:#141414; padding:5px 12px 6px; font-family:var(--f-type); white-space:nowrap;
  box-shadow:2px 3px 0 rgba(0,0,0,.18); transform:rotate(.8deg); }
.zn .src i { font-style:normal; color:#c4126b; margin-right:8px; }
"""


# ---------------------------------------------------------------- helpers
def R(X, key):
    seed = sum((i + 1) * ord(c) for i, c in enumerate(str(key))) + int(X.v.get("meta", {}).get("seed", 9)) * 7919
    return random.Random(seed)


def torn(r, amp=1.4, n=9):
    """a clip-path polygon with ragged edges (percent), so every scrap looks hand-torn."""
    pts = []
    for k in range(n + 1): pts.append((k * 100 / n, r.uniform(0, amp)))
    for k in range(1, n + 1): pts.append((100 - r.uniform(0, amp), k * 100 / n))
    for k in range(1, n + 1): pts.append((100 - k * 100 / n, 100 - r.uniform(0, amp)))
    for k in range(1, n): pts.append((r.uniform(0, amp), 100 - k * 100 / n))
    return "polygon(" + ",".join(f"{x:.1f}% {y:.1f}%" for x, y in pts) + ")"


def st(**k):
    return "; ".join(f"{a.replace('_', '-')}:{v:.0f}px" if isinstance(v, (int, float)) else f"{a.replace('_', '-')}:{v}" for a, v in k.items())


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def isnum(ch): return ch.isdigit() or ch in ".,+-%×$¥/:#" or ("A" <= ch <= "Z") or ("a" <= ch <= "z")


def scrap_em(ch): return 0.3 if ch == " " else fit.gw(ch) + 0.27


def smooth(pts):
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for k in range(1, len(pts)):
        (ax, ay), (bx, by) = pts[k - 1], pts[k]
        d += f" Q{ax:.1f} {ay:.1f} {(ax + bx) / 2:.1f} {(ay + by) / 2:.1f}"
    return d + f" L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"


def mark_svg(kind, w, h, cls):
    """a marker stroke sized to an estimated w × h word box (ring around it, or a strike through it)."""
    if kind == "ring":
        n = [(.1, .1), (.55, -.12), (1.06, .12), (1.1, .7), (.62, 1.16), (.06, 1.02), (-.08, .45), (.16, .02), (.4, -.1)]
        sw = max(7, h * 0.07)
    else:
        n = [(-.05, .6), (.35, .5), (.7, .55), (1.06, .44)]
        sw = max(9, h * 0.11)
    d = smooth([(x * w, y * h) for x, y in n])
    return (f'<svg class="mk {cls}" style="left:0; top:0; width:100%; height:100%" viewBox="0 0 {w:.0f} {h:.0f}" preserveAspectRatio="none">'
            f'<path pathLength="1" d="{d}" stroke="{PINK}" stroke-width="{sw:.0f}" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')


def ransom(X, r, text, w, h, max_px, max_lines=2, hot_bg=PINK, min_px=None, mark="ring"):
    """ransom-note lettering that fits w × h: each glyph its own scrap, font, colour, cut and tilt.
    *x* glyphs go on hot scraps; ~x~ wraps glyphs in a marker mark (ring / strike). Returns (html, px, n_lines)."""
    raw = fit.as_text(text)
    plain = fit.plain(raw).replace("~", "")
    ratio = sum(scrap_em(c) for c in plain) / max(0.1, fit.width(plain))
    f = fit.fit_text(raw, w / ratio, h, max_px, min_px or max_px * 0.3, lh=1.27, max_lines=max_lines)
    px = f.px
    rows = []
    for line in f.lines:
        hot, out, inmk, mk_chars, buf = False, [], False, "", []
        for ch in line:
            if ch == "*": hot = not hot; continue
            if ch == "~":
                if inmk:
                    wm = sum(scrap_em(c) for c in mk_chars) * px
                    out.append(f'<span class="mkw">{"".join(buf)}{mark_svg(mark, wm, 1.22 * px, "mkr")}</span>'); buf = []
                inmk = not inmk; mk_chars = ""; continue
            tgt = buf if inmk else out
            if inmk: mk_chars += ch
            if ch == " ": tgt.append('<i class="rl sp"></i>'); continue
            X.used_text.update(ch)
            role = r.choice(NUM_ROLES if isnum(ch) else GLYPH_ROLES)
            bg, fg = (hot_bg, INK if hot_bg == PINK else WHITE) if hot else r.choice(SCRAPS)
            pat = r.choice(PATTERNS)
            rot = r.uniform(-7, 7); dy = r.uniform(-.07, .07); sz = r.uniform(.9, 1.1)
            tgt.append(f'<i class="rl" data-r="{rot:.1f}" style="font-family:var(--f-{role}); background:{pat + ", " if pat else ""}{bg}; color:{fg}; '
                       f'padding:{r.uniform(.04, .1):.2f}em {r.uniform(.08, .14):.2f}em {r.uniform(.07, .13):.2f}em {r.uniform(.08, .14):.2f}em; transform:translateY({dy:.2f}em) rotate({rot:.1f}deg); font-size:{sz:.2f}em">{X.rich(ch)}</i>')
        if buf: out.append("".join(buf))
        rows.append(f'<div class="rline">{"".join(out)}</div>')
    return f'<div class="rlines" style="font-size:{px:.0f}px">{"".join(rows)}</div>', px, len(rows)


def rw(text, px):
    """estimated rendered width of one ransom line."""
    return sum(scrap_em(c) for c in fit.plain(fit.as_text(text)).replace("~", "")) * px


def tape(r, x, y, w=150, rot=None, pink=False):
    rot = r.uniform(-24, 24) if rot is None else rot
    return f'<i class="tape{" pk" if pink else ""}" style="{st(left=x, top=y, width=w)}; transform:rotate({rot:.0f}deg)"></i>'


def marker(points, color=INK, width=9, cls=""):
    """a hand-drawn marker stroke through points [(x,y),...] in page px."""
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    x0, y0, x1, y1 = min(xs) - 20, min(ys) - 20, max(xs) + 20, max(ys) + 20
    d = smooth([(x - x0, y - y0) for x, y in points])
    return (f'<svg class="mk {cls}" style="{st(left=x0, top=y0, width=x1 - x0, height=y1 - y0)}" viewBox="0 0 {x1 - x0:.0f} {y1 - y0:.0f}">'
            f'<path pathLength="1" d="{d}" stroke="{color}" stroke-width="{width}" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')


def arrow(points, color=INK, width=9, cls=""):
    """a marker arrow: the shaft through points, then a two-stroke head (class cls + 'h') along the last segment."""
    (ax, ay), (bx, by) = points[-2], points[-1]
    a = math.atan2(by - ay, bx - ax); k = 16 + width * 2
    head = [(bx - k * math.cos(a - 0.55), by - k * math.sin(a - 0.55)), (bx, by), (bx - k * math.cos(a + 0.55), by - k * math.sin(a + 0.55))]
    return marker(points, color, width, cls) + marker(head, color, width, cls + "h")


def draw(X, sel, t, dur=0.45):
    """marker strokes draw on, on twos."""
    X.tw(f'tl.to("{sel} path", {{strokeDashoffset:0, duration:{dur:.2f}, ease:"steps({max(3, round(dur * 15))})"}}, {t:.3f});')


def slap(X, sel, t, st_=0.067, big=1.0):
    """stop-motion entrance: scraps arrive in 3 steps from a bigger size and a harder tilt."""
    X.tw(f'tl.from("{sel}", {{scale:{1.6 * big:.2f}, opacity:0, rotation:(i,el)=>(+el.dataset.r||8)*2.4, duration:0.2, ease:"steps(3)", stagger:(i,el,l)=>i*Math.min({st_}, 0.6/l.length)}}, {t:.3f});')


def thud(X, sel, t):
    """a rubber stamp hits: oversize to size in two frames."""
    X.tw(f'tl.from("{sel}", {{scale:2.6, opacity:0, duration:0.134, ease:"steps(2)"}}, {t:.3f});')


def boil(X, sel, t, d, rot=True):
    """everything stuck down still trembles a little, two frames at a time (the stop-motion 'boil').
    rot=False for pieces tilted with the CSS rotate property (GSAP folds it into its rotation, so a boil would flatten them)."""
    n = max(1, int(d / 0.134))
    r0, r1 = (", rotation:-0.35", ", rotation:0.35") if rot else ("", "")
    X.tw(f'tl.fromTo("{sel}", {{x:-1.3, y:0.8{r0}}}, {{x:1.3, y:-0.8{r1}, duration:0.134, ease:"steps(1)", repeat:{n}, yoyo:true, immediateRender:false, stagger:{{each:0.067}}}}, {t:.3f});')


def cam(X, sel, t, d, keys):
    """stepped camera: keys = [(time, scale, fx, fy)]; each move happens on twos, then a slow stepped creep holds it alive.
    Moves are half-strength and clamped so the page's margins stay in frame and nothing slides under the masthead strip."""
    W, H = X.W, X.H
    m, top, mast, bot = (56, 300, 262, 1290) if X.portrait else (80, 130, 76, 960)
    def xy(sc, fx, fy):
        x, y = W / 2 - sc * fx * W, H / 2 - sc * fy * H
        lo, hi = 30 - m * sc, (W - 30) - (W - m) * sc
        x = min(max(x, lo), hi) if lo <= hi else (lo + hi) / 2
        lo, hi = mast - top * sc, (H - 20) - bot * sc
        y = min(max(y, lo), hi) if lo <= hi else (lo + hi) / 2
        return min(0, max(W - sc * W, x)), min(0, max(H - sc * H, y))
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    keys = sorted((tk, 1 + (sc - 1) * 0.5, fx, fy) for tk, sc, fx, fy in keys)
    for k, (tk, sc, fx, fy) in enumerate(keys):
        x, y = xy(sc, fx, fy)
        nxt = (keys[k + 1][0] if k + 1 < len(keys) else t + d) - 0.02
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc:.4f}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});'); h0 = tk
        else:
            mv = min(0.8, max(0.3, nxt - tk - 0.05))
            X.tw(f'tl.to("{sel}", {{scale:{sc:.4f}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"steps({max(4, round(mv * 15))})"}}, {tk:.3f});'); h0 = tk + mv
        if nxt - h0 > 0.3:
            s2 = sc * 1.015
            x2, y2 = xy(s2, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{s2:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - h0:.2f}, ease:"steps({max(3, round((nxt - h0) * 7.5))})"}}, {h0:.3f});')


class L:
    """the page box for the current aspect (9:16 keeps text off the top 200, the bottom 400 and the lower-right 120 px)."""
    def __init__(self, X):
        self.v = X.portrait; self.W, self.H = X.W, X.H
        self.m = 56 if self.v else 80
        self.top = 300 if self.v else 130
        self.bot = 1290 if self.v else 940
        self.cw = self.W - 2 * self.m
        self.lw = self.cw - (100 if self.v else 0)       # width that is safe in the lower half


def page(X, b, t, d, cid, body, dark=False):
    """furniture (masthead strip, page sticker, source scrap, staple, xerox texture) + the torn riso sheet that opens the page."""
    X.css("zine", CSS.replace("__NOISE__", NOISE))
    g = L(X); i = X.beat["i"]
    meta = X.v.get("meta", {})
    r = R(X, f"{cid}-page")
    mast, sec = meta.get("mast", "HAT9 ZINE"), meta.get("section", "商业拆解")
    src = b.get("src", meta.get("src", ""))
    X.used_text.update(mast + sec + src + "SRCP.0123456789ISSUE·")
    if g.v:
        mastd = f'<div class="mast" style="{st(left=g.m, top=212, font_size=24)}">{X.rich(mast)} <b>·</b> ISSUE {int(meta.get("issue", 9)):02d} <b>·</b> {X.rich(sec)}</div>'
        pg = f'<div class="pg" style="{st(right=g.m, top=204)}">P.{i + 1:02d}</div>'
        srcd = f'<div class="src" style="{st(left=g.m, top=1430, font_size=24)}"><i>SRC</i>{X.rich(src)}</div>' if src else ""
        staple = ""
    else:
        mastd = f'<div class="mast" style="{st(left=g.m, top=32, font_size=22)}">{X.rich(mast)} <b>·</b> ISSUE {int(meta.get("issue", 9)):02d} <b>·</b> {X.rich(sec)}</div>'
        pg = f'<div class="pg" style="{st(right=g.m, top=20)}">P.{i + 1:02d}</div>'
        srcd = f'<div class="src" style="{st(right=g.m + 110, top=40, font_size=22)}"><i>SRC</i>{X.rich(src)}</div>' if src else ""
        staple = f'<i class="staple" style="{st(left=24, top=330)}; transform:rotate(-84deg)"></i><i class="staple" style="{st(left=24, top=760)}; transform:rotate(-96deg)"></i>'
    streaks = "".join(f'<i class="streak" style="top:{r.randint(0, g.H)}px; opacity:{r.uniform(.3, 1):.2f}"></i>' for _ in range(3))
    col = [PINK, TEAL, INK][i % 3]
    peel = f'<div class="peel" style="background:{col}; clip-path:{torn(r, 2.2, 14)}"><div class="tex"></div></div>' if i > 0 else ""
    X.clip(cid, t, d, f'<div class="zn{" dark" if dark else ""}"><div class="cam">{body}</div><div class="tex"></div>{streaks}<div class="xer"></div>{mastd}{pg}{srcd}{staple}{peel}</div>', "scene", 2)
    s = f"#{cid}"
    if peel:
        X.tw(f'tl.to("{s} .peel", {{xPercent:-118, rotation:-4, duration:0.33, ease:"steps(5)"}}, {t:.3f});')
        X.sfx(t, "tear")
    X.tw(f'tl.from("{s} .mast, {s} .pg, {s} .src", {{scale:1.3, opacity:0, duration:0.2, ease:"steps(3)", stagger:0.07}}, {t + 0.1:.3f});')
    boil(X, f"{s} .bo", t, d)
    return g, s


def critter(r, w, color=TEAL):
    """a generic cut-paper critter (deliberately not any real toy character): one horn, two eyes, a stitched grin."""
    pts = []
    for k in range(28):
        a = 2 * math.pi * k / 28; rr = 1 + r.uniform(-.05, .05) + (.06 if k % 2 else 0)
        pts.append((50 + 40 * rr * math.cos(a), 58 + 36 * rr * math.sin(a)))
    body = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"
    return (f'<svg viewBox="0 0 100 100" style="width:{w:.0f}px; height:{w:.0f}px; overflow:visible; filter:drop-shadow(4px 0 0 #fbf8f0) drop-shadow(-4px 0 0 #fbf8f0) drop-shadow(0 4px 0 #fbf8f0) drop-shadow(0 -4px 0 #fbf8f0) drop-shadow(6px 9px 0 rgba(0,0,0,.2))">'
            f'<path d="M44 26 L50 4 L57 26 Z" fill="{PINK}" stroke="#141414" stroke-width="2"/>'
            f'<path d="{body}" fill="{color}" stroke="#141414" stroke-width="2.4"/>'
            f'<ellipse cx="38" cy="52" rx="8" ry="10" fill="#fbf8f0" stroke="#141414" stroke-width="2"/><circle cx="40" cy="54" r="4" fill="#141414"/>'
            f'<ellipse cx="62" cy="52" rx="8" ry="10" fill="#fbf8f0" stroke="#141414" stroke-width="2"/><circle cx="60" cy="54" r="4" fill="#141414"/>'
            f'<path d="M34 70 Q50 84 66 70" fill="none" stroke="#141414" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M38 71 l2 5 M44 74 l1 5 M50 76 l0 5 M56 74 l-1 5 M62 71 l-2 5" stroke="#141414" stroke-width="2" stroke-linecap="round"/>'
            f'<path d="M20 70 Q12 78 16 86 M80 70 Q88 78 84 86" fill="none" stroke="#141414" stroke-width="3" stroke-linecap="round"/></svg>')


def stamp(X, text, sub, px, rot):
    X.used_text.update(str(text) + str(sub))
    return f'<div class="stamp" style="font-size:{px:.0f}px; transform:rotate({rot}deg)">{X.rich(text)}{f"<small>{X.rich(sub)}</small>" if sub else ""}</div>'


# ---------------------------------------------------------------- scenes
def cover(b, X, t, d, cid):
    """the zine cover: ransom headline, a cut-paper critter sticker, the big figure in cut-out digits, a label sticker and tape."""
    r = R(X, cid); g = L(X)
    tn = T(X, b, "at_num", t, t + d * 0.45)
    if g.v:
        hx, hy, hw, hh = g.m, 350, g.cw, 260
        cx, cy, cs = 620, 610, 290
        nx, ny, nw, nh = g.m, 930, g.lw, 220
        sx, sy = g.m + 10, 1186
    else:
        hx, hy, hw, hh = g.m + 10, 170, 1040, 330
        cx, cy, cs = 1280, 200, 470
        nx, ny, nw, nh = g.m + 10, 540, 1080, 300
        sx, sy = 1200, 760
    head, hpx, hn = ransom(X, r, b.get("title", ""), hw, hh, 150, max_lines=3)
    num, npx, _ = ransom(X, r, b.get("num", ""), nw, nh, 230, max_lines=1)
    kick = b.get("kicker", ""); stk = b.get("sticker", "")
    X.used_text.update(kick + stk)
    uy = ny + npx * 1.27 + 10
    nwr = min(nw, rw(b.get("num", ""), npx))
    body = (f'<div class="bo bh" style="{st(left=hx, top=hy)}">{head}</div>'
            f'<div class="bo bnum" style="{st(left=nx, top=ny)}">{num}</div>'
            f'<div class="bo crit" style="{st(left=cx, top=cy)}">{critter(r, cs)}</div>'
            + (f'<div class="bo bstk" style="{st(left=sx, top=sy)}"><div class="stk" style="{st(font_size=30 if g.v else 34)}; background:{TEAL}; color:{WHITE}; transform:rotate(-4deg)">{X.rich(stk)}</div></div>' if stk else "")
            + tape(r, cx + cs * 0.1, cy - 6, 170) + tape(r, cx + cs * 0.6, cy + cs * 0.84, 150, pink=True)
            + (f'<div class="bo typed kick" style="{st(left=hx + 6, top=hy - (52 if g.v else 50), font_size=24 if g.v else 22)}">{X.rich(kick)}</div>' if kick else "")
            + marker([(nx + 10, uy), (nx + nwr * 0.5, uy + 14), (nx + nwr * 0.95, uy - 4)], PINK, 12, "u1"))
    gg, s = page(X, b, t, d, cid, body)
    X.tw(f'tl.from("{s} .crit svg", {{scale:0.3, rotation:-30, opacity:0, duration:0.27, ease:"steps(4)"}}, {t + 0.1:.3f});')
    if kick: X.tw(f'tl.from("{s} .kick", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.15:.3f});')
    slap(X, f"{s} .bh .rl", t + 0.2)
    X.sfx(t + 0.2, "type")
    slap(X, f"{s} .bnum .rl", tn - 0.25, 0.08, 1.3)
    X.sfx(tn - 0.1, "hit")
    draw(X, f"{s} .u1", tn + 0.5)
    if stk: X.tw(f'tl.from("{s} .stk", {{scale:0, rotation:-40, duration:0.2, ease:"steps(3)"}}, {tn + 0.35:.3f});')
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)", stagger:0.1}}, {t + 0.3:.3f});')
    X.sfx(t + 0.3, "tape")
    cam(X, f"{s} .cam", t, d, [(t, 1.06, 0.35, 0.35), (tn - 0.3, 1.0, 0.5, 0.5)])


def versus(b, X, t, d, cid):
    """before → after as cut-out numbers: the old figure small, the new one big and hot, a marker arrow and a rubber stamp."""
    r = R(X, cid); g = L(X)
    A, B = b["a"], b["b"]
    ta, tb, tp = T(X, b, "at_a", t, t + 0.3), T(X, b, "at_b", t, t + 1.2), T(X, b, "at_pct", t, t + 2.2)
    if g.v: ax, ay, aw, ah_ = g.m, 330, 700, 150;  bx, by, bw, bh_ = g.m, 640, g.cw, 300
    else:   ax, ay, aw, ah_ = g.m + 10, 230, 640, 170; bx, by, bw, bh_ = 740, 330, 1100, 330
    ah, apx, _ = ransom(X, r, A["v"], aw, ah_, 130, 1)
    bh, bpx, _ = ransom(X, r, "*" + B["v"] + "*", bw, bh_, 260, 1)
    X.used_text.update(A.get("label", "") + B.get("label", ""))
    if g.v: spx, sx_, sy_ = 84, g.m + 300, by + 44 + bpx * 1.27 + 30
    else:   spx, sx_, sy_ = 110, 1240, by + 50 + bpx * 1.27 + 40
    body = (f'<div class="bo ba" style="{st(left=ax, top=ay)}"><div class="typed" style="font-size:{26 if g.v else 24}px; margin-bottom:10px">{X.rich(A.get("label", ""))}</div>{ah}</div>'
            f'<div class="bo bb" style="{st(left=bx, top=by)}"><div class="typed" style="font-size:{30 if g.v else 28}px; margin-bottom:12px; color:{PINK}">{X.rich(B.get("label", ""))}</div>{bh}</div>'
            + (f'<div class="bo bs" style="{st(left=sx_, top=sy_)}">{stamp(X, b.get("stamp", ""), b.get("stamp_sub", ""), spx, -12)}</div>' if b.get("stamp") else ""))
    ae = ay + 40 + apx * 1.3
    aw_ = min(aw, rw(A["v"], apx))
    if g.v: body += arrow([(ax + aw_ + 16, ay + 40 + apx * 0.5), (ax + aw_ + 80, (ae + by) / 2), (ax + aw_ + 30, by + 20)], PINK, 12, "ar")
    else:   body += arrow([(ax + aw_ * 0.6, ae + 16), (ax + aw_ + 60, ae + 60), (bx - 30, by + 150)], PINK, 12, "ar")
    body += tape(r, ax + aw_ * 0.7, ay + 30, 120) + tape(r, bx + min(bw, rw(B["v"], bpx)) * 0.5, by - 18, 180, pink=True)
    gg, s = page(X, b, t, d, cid, body)
    X.tw(f'tl.from("{s} .ba .typed", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {max(t + 0.1, ta - 0.3):.3f});')
    slap(X, f"{s} .ba .rl", ta - 0.2)
    X.sfx(ta - 0.2, "type")
    draw(X, f"{s} .ar", tb - 0.5, 0.4); draw(X, f"{s} .arh", tb - 0.1, 0.134)
    X.tw(f'tl.from("{s} .bb .typed", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {tb - 0.3:.3f});')
    slap(X, f"{s} .bb .rl", tb - 0.25, 0.08, 1.2)
    X.sfx(tb - 0.1, "hit")
    if b.get("stamp"):
        thud(X, f"{s} .stamp", tp - 0.1)
        X.sfx(tp - 0.05, "stamp")
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)", stagger:0.12}}, {t + 0.25:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.08, 0.3, 0.32), (tb - 0.4, 1.0, 0.5, 0.5), (tp, 1.05, 0.55, 0.6)])


def pie(b, X, t, d, cid):
    """a torn-paper pie: a newsprint disc, the share cut out in hot pink and slapped on, the figure and label in cut-out letters."""
    r = R(X, cid); g = L(X)
    p = max(1.0, min(99.0, float(b.get("pct", 38.1))))
    tp, ti = T(X, b, "at_pct", t, t + 0.6), T(X, b, "at_ip", t, t + 1.6)
    if g.v: cx, cy, rad = 540, 610, 230; lx, ly, lw = g.m, 892, g.lw
    else:   cx, cy, rad = 560, 530, 330; lx, ly, lw = 1000, 250, 840
    a1 = -90; a2 = -90 + 360 * p / 100
    def arc(a, k=1.0): return cx + rad * k * math.cos(math.radians(a)), cy + rad * k * math.sin(math.radians(a))
    (x1, y1), (x2, y2) = arc(a1), arc(a2)
    jag = " ".join(f"L{cx + rad * (1 + r.uniform(-.03, .03)) * math.cos(math.radians(a)):.0f} {cy + rad * (1 + r.uniform(-.03, .03)) * math.sin(math.radians(a)):.0f}" for a in range(int(a1) + 4, int(a2), 5))
    wedge = f"M{cx} {cy} L{x1:.0f} {y1:.0f} {jag} L{x2:.0f} {y2:.0f} Z"
    big, bpx, _ = ransom(X, r, "*" + b.get("big", f"{p:g}%") + "*", lw, 190 if g.v else 240, 210, 1)
    lab, lpx, ln = ransom(X, r, b.get("label", ""), lw, 150 if g.v else 170, 64 if g.v else 72, 2, hot_bg=TEAL)
    note, rest = b.get("note", ""), b.get("rest", "")
    X.used_text.update(note + rest)
    lines_ = "".join(f'<line x1="{cx - rad}" y1="{cy - rad + 30 + k * 26}" x2="{cx + rad}" y2="{cy - rad + 30 + k * 26}" stroke="#141414" stroke-opacity=".1" stroke-width="9"/>' for k in range(int(rad * 2 / 26) - 1))
    svg = (f'<svg class="pz" style="position:absolute; left:0; top:0; width:{g.W}px; height:{g.H}px; overflow:visible">'
           f'<defs><clipPath id="{cid}c"><circle cx="{cx}" cy="{cy}" r="{rad}"/></clipPath></defs>'
           f'<g class="disc"><circle cx="{cx}" cy="{cy}" r="{rad}" fill="{NEWS}" stroke="#141414" stroke-width="3"/><g clip-path="url(#{cid}c)">{lines_}</g></g>'
           f'<g class="wd"><path d="{wedge}" fill="{PINK}" stroke="#141414" stroke-width="3"/></g></svg>')
    ly2 = ly + bpx * 1.27 + 14
    rx, ry = arc((a2 + 270) / 2, 0.5)   # middle of the rest of the disc
    body = (f'<div class="bo bpz" style="left:0; top:0; width:{g.W}px; height:{g.H}px">{svg}</div>'
            f'<div class="bo bbig" style="{st(left=lx, top=ly)}">{big}</div>'
            f'<div class="bo blab" style="{st(left=lx, top=ly2)}">{lab}</div>')
    if note:
        ny_ = (g.top + 10) if g.v else ly2 + lpx * 1.27 * ln + 34
        body += f'<div class="bo hand bnote" style="{st(left=(g.m if g.v else lx + 4), top=ny_, font_size=32)}; transform:rotate(-2deg)">{X.rich(note)}</div>'
    if rest:
        body += f'<div class="bo brest" style="{st(left=rx - 90, top=ry - 30)}"><div class="stk" style="font-size:{26 if g.v else 30}px; background:{WHITE}; color:{INK}; transform:rotate(-6deg)">{X.rich(rest)}</div></div>'
    body += tape(r, cx - 80, cy - rad - 18, 160) + tape(r, cx + rad * 0.45, cy + rad * 0.82, 140, pink=True)
    mx, my = arc((a1 + a2) / 2, 1.1)
    pointer = not g.v and mx < lx - 80 and math.cos(math.radians((a1 + a2) / 2)) > 0.6
    if pointer: body += arrow([(mx, my), ((mx + lx) / 2 - 10, (my + ly + bpx * 0.6) / 2 - 24), (lx - 26, ly + bpx * 0.6)], INK, 8, "pa")
    gg, s = page(X, b, t, d, cid, body)
    X.tw(f'tl.from("{s} .disc", {{scale:0.2, svgOrigin:"{cx} {cy}", opacity:0, duration:0.27, ease:"steps(4)"}}, {t + 0.1:.3f});')
    if note: X.tw(f'tl.from("{s} .bnote", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .wd", {{x:180, y:-140, rotation:40, svgOrigin:"{cx} {cy}", opacity:0, duration:0.27, ease:"steps(4)"}}, {tp - 0.2:.3f});')
    X.sfx(tp - 0.1, "hit")
    slap(X, f"{s} .bbig .rl", tp - 0.1, 0.08, 1.2)
    slap(X, f"{s} .blab .rl", ti - 0.25, 0.05)
    if pointer: draw(X, f"{s} .pa", tp + 0.15, 0.3); draw(X, f"{s} .pah", tp + 0.45, 0.134)
    if rest: X.tw(f'tl.from("{s} .brest .stk", {{opacity:0, scale:1.4, duration:0.2, ease:"steps(3)"}}, {ti + 0.3:.3f});')
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)", stagger:0.1}}, {t + 0.3:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.05, 0.4, 0.5), (ti - 0.3, 1.0, 0.5, 0.5)])


def bars(b, X, t, d, cid):
    """paper-strip bars taped to the page, heights to scale; each strip can arrive on its own cue; a multiplier stamp."""
    r = R(X, cid); g = L(X)
    items = b["items"]; n = len(items)
    tm = T(X, b, "at_mul", t, t + d * 0.8)
    vmax = max(float(it["v"]) for it in items) or 1
    if g.v:
        avail = g.lw - 380 if n <= 3 else g.lw - 40
        gap = 40; bw = min(260, (avail - gap * (n - 1)) / n); x0, base, top = g.m + 30, 1170, (470 if n <= 3 or not b.get("stamp") else 640)
    else:
        avail = 1160; gap = 70; bw = min(320, (avail - gap * (n - 1)) / n); x0, base, top = g.m + 120, 860, 250
    strips, labs = [], []
    for k, it in enumerate(items):
        h = max(40, (base - top) * float(it["v"]) / vmax); x = x0 + k * (bw + gap)
        col = PINK if it.get("hot") else (TEAL if k % 2 else NEWS)
        strips.append(f'<div class="bo bs{k}" style="{st(left=x, top=base - h, width=bw, height=h)}"><div class="sc" style="position:absolute; inset:0; background:{col}; clip-path:{torn(r, 2.5, 8)}"><div class="ht" style="opacity:.25"></div></div></div>')
        strips.append(tape(r, x + bw * 0.2, base - h - 14, bw * 0.6, rot=r.uniform(-8, 8)).replace('class="tape', f'class="tp{k} tape'))
        vh, vpx, _ = ransom(X, r, it.get("label_v", str(it["v"])), bw * (1.5 if it.get("hot") else 1.2), 110 if g.v else 130, 96, 1, hot_bg=PINK)
        labs.append(f'<div class="bo bl{k}" style="{st(left=x - 6, top=base - h - vpx * 1.27 - 22)}">{vh}</div>'
                    f'<div class="bo typed by{k}" style="{st(left=x, top=base + 16, font_size=28 if g.v else 26)}">{X.rich(it.get("year", ""))}</div>')
        X.used_text.update(str(it.get("year", "")))
    if g.v: sx, sy, spx = (x0 + n * (bw + gap) + 10, 640, 96) if n <= 3 else (g.m + g.lw - 330, g.top + 70, 90)
    else:   sx, sy, spx = 1400, 330, 140
    stp = f'<div class="bo bm" style="{st(left=sx, top=sy)}">{stamp(X, b.get("stamp", ""), b.get("stamp_sub", ""), spx, 10)}</div>' if b.get("stamp") else ""
    title = b.get("title", "")
    X.used_text.update(title)
    tt = f'<div class="bo typed bt" style="{st(left=g.m, top=g.top, font_size=30)}">{X.rich(title)}</div>' if title else ""
    floor = marker([(x0 - 40, base + 4), (x0 + n * (bw + gap) - gap + 40, base + 2)], INK, 7, "fl")
    gg, s = page(X, b, t, d, cid, tt + "".join(strips) + "".join(labs) + floor + stp)
    draw(X, f"{s} .fl", t + 0.1, 0.3)
    if title: X.tw(f'tl.from("{s} .bt", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.1:.3f});')
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.25 + k * 0.3) - (0.15 if it.get("at") else 0)
        X.tw(f'tl.from("{s} .bs{k} .sc", {{scaleY:0, transformOrigin:"50% 100%", duration:0.33, ease:"steps(5)"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .tp{k}", {{scaleX:0, duration:0.134, ease:"steps(2)"}}, {tk + 0.3:.3f});')
        slap(X, f"{s} .bl{k} .rl", tk + 0.25, 0.05)
        X.tw(f'tl.from("{s} .by{k}", {{opacity:0, duration:0.2, ease:"steps(2)"}}, {tk:.3f});')
        X.sfx(tk, "tear")
    if stp:
        thud(X, f"{s} .stamp", tm)
        X.sfx(tm, "stamp")
    cam(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5), (tm - 0.2, 1.05, 0.6, 0.45)])


def stamps(b, X, t, d, cid):
    """a sheet of postage stamps (one per item, any count) with a postmark slammed onto the hot one."""
    r = R(X, cid); g = L(X)
    items = b["items"]; n = len(items)
    th = T(X, b, "at_hot", t, t + d * 0.55)
    cols = min(n, 2 if g.v else (3 if n in (5, 6, 9) else 4)) if n > 1 else 1
    rows = math.ceil(n / cols)
    if g.v: ox, oy, W_, H_ = g.m + 10, 380, g.lw - 10, 860
    else:   ox, oy, W_, H_ = g.m + 40, 210, 1680, 640
    gap = 36
    sw = min(600, (W_ - gap * (cols - 1)) / cols); sh = min((H_ - gap * (rows - 1)) / rows, sw * 1.15)
    ox += (W_ - cols * sw - gap * (cols - 1)) / 2
    fn = min(46, sw / 7.5, sh / 6)
    html = []
    hot_k = next((k for k, it in enumerate(items) if it.get("hot")), 0)
    for k, it in enumerate(items):
        x = ox + (k % cols) * (sw + gap); y = oy + (k // cols) * (sh + gap)
        col = PINK if it.get("hot") else [TEAL, NEWS, WHITE][k % 3]
        fg = WHITE if col == TEAL else INK
        rot = r.uniform(-4, 4)
        sub = it.get("sub", "")
        iw, ih = sw - 42 - fn * 0.9, sh - 42 - fn * 0.8          # inside the perforated border, the inset and the padding
        fname = min(fn, iw / max(1, fit.width(it["name"])) * 0.96); fsub = max(16, fn * 0.45)
        vh, vpx, _ = ransom(X, r, it["v"], iw, max(24, min(sh * 0.4, ih - fname - (fsub * 1.3 + 6 if sub else 0) - 8)), 110, 1, hot_bg=INK)
        X.used_text.update(it["name"] + sub)
        html.append(f'<div class="bo st{k}" style="{st(left=x, top=y, width=sw, height=sh)}">'
                    f'<div class="sc" style="position:absolute; inset:0; background:{WHITE}; border:9px dotted {PAPER}; transform:rotate({rot:.1f}deg)">'
                    f'<div style="position:absolute; inset:12px; background:{col}; color:{fg}; padding:{fn * 0.4:.0f}px {fn * 0.45:.0f}px; overflow:hidden; display:flex; flex-direction:column">'
                    f'<div style="font-family:var(--f-puhui); font-size:{fname:.0f}px; line-height:1; white-space:nowrap">{X.rich(it["name"])}</div>'
                    + (f'<div class="typed" style="font-size:{fsub:.0f}px; line-height:1.3; opacity:.8; margin-top:6px">{X.rich(sub)}</div>' if sub else "")
                    + f'<div style="margin-top:auto">{vh}</div><div class="ht" style="opacity:.16"></div></div></div></div>')
    pz = min(240, sw * 0.55, sh * 0.55)
    hx = ox + (hot_k % cols) * (sw + gap) + sw * 0.5 - pz * 0.35; hy = oy + (hot_k // cols) * (sh + gap) + sh * 0.3 - pz * 0.5
    pm, pms = b.get("postmark", ""), b.get("postmark_sub", "")
    X.used_text.update(pm + pms)
    waves = "".join(f'<i style="position:absolute; left:{pz * 0.95 + k * 4:.0f}px; top:{pz * (0.3 + k * 0.13):.0f}px; width:{pz * 0.42:.0f}px; height:7px; border-radius:4px; background:{INK}; opacity:.8; transform:rotate(-14deg)"></i>' for k in range(4))
    post = (f'<div class="bo bp" style="{st(left=hx, top=hy)}"><div style="position:relative; width:{pz:.0f}px; height:{pz:.0f}px; border:8px solid {INK}; border-radius:50%; '
            f'color:{INK}; display:grid; place-items:center; transform:rotate(-14deg); text-align:center; opacity:.88">'
            f'<div><div style="font-family:var(--f-archivo); font-size:{pz * 0.27:.0f}px; line-height:1">{X.rich(pm)}</div><div class="typed" style="font-size:{min(pz * 0.075, pz * 0.75 / max(1, len(pms) * 0.72)):.0f}px; letter-spacing:.14em">{X.rich(pms)}</div></div></div>{waves}</div>') if pm else ""
    title = b.get("title", "")
    X.used_text.update(title)
    tt = f'<div class="bo typed bt" style="{st(left=g.m, top=g.top, font_size=30)}">{X.rich(title)}</div>' if title else ""
    gg, s = page(X, b, t, d, cid, tt + "".join(html) + post)
    if title: X.tw(f'tl.from("{s} .bt", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.1:.3f});')
    step = min(0.17, max(0.05, (th - t - 0.6) / max(1, n)))
    for k in range(n):
        X.tw(f'tl.from("{s} .st{k} .sc", {{y:-60, rotation:{r.choice([-18, 14, -10, 20])}, opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.15 + k * step:.3f});')
        if k < 6: X.sfx(t + 0.15 + k * step, "click")
    if post:
        thud(X, f"{s} .bp", th - 0.1)
        X.sfx(th - 0.05, "stamp")
    X.tw(f'tl.to("{s} .st{hot_k} .sc", {{scale:1.06, duration:0.134, ease:"steps(2)"}}, {th - 0.1:.3f});')
    fx_ = (ox + (hot_k % cols + 0.5) * (sw + gap)) / g.W; fy_ = (oy + (hot_k // cols + 0.5) * (sh + gap)) / g.H
    cam(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5), (th - 0.4, 1.1, fx_, fy_)])


def clip(b, X, t, d, cid):
    """a newspaper clipping torn out and taped down: ransom headline (~figure~ gets a marker ring), dek, body columns, a falling scribble."""
    r = R(X, cid); g = L(X)
    tdp = T(X, b, "at_drop", t, t + d * 0.5)
    if g.v: px_, py_, pw, ph = g.m, 340, g.lw - 10, 800
    else:   px_, py_, pw, ph = g.m + 60, 170, 1100, 700
    head, hpx, hn = ransom(X, r, b.get("headline", ""), pw - 110, ph * 0.42, 140, 3, mark="ring")
    date, dek = b.get("date", ""), b.get("dek", "")
    X.used_text.update(date + dek)
    dek_y = 78 + hpx * 1.38 * hn + 44
    dpx = min(30, (pw - 80) / max(1, fit.width(dek)) * 0.96) if dek else 0
    cols = 2 if g.v else 3
    colw = (pw - 80 - (cols - 1) * 30) / cols
    b0 = dek_y + (dpx * 1.5 if dek else 0) + 26
    rows_ = max(0, int((ph - b0 - 40) / 26))
    body_bars = "".join(f'<i style="position:absolute; left:{40 + c * (colw + 30):.0f}px; top:{b0 + k * 26:.0f}px; width:{colw * r.uniform(.7, 1):.0f}px; height:12px; background:rgba(20,20,20,.2)"></i>'
                        for c in range(cols) for k in range(rows_))
    paper = (f'<div class="bo bpp" style="{st(left=px_, top=py_, width=pw, height=ph)}"><div class="sc" style="position:absolute; inset:0; background:{NEWS}; clip-path:{torn(r, 1.8, 12)}; transform:rotate(-1.6deg)">'
             f'<div class="typed" style="position:absolute; left:40px; top:30px; font-size:22px">{X.rich(date)}</div>'
             f'<div class="bh" style="position:absolute; left:40px; top:78px">{head}</div>'
             + (f'<div style="position:absolute; left:40px; top:{dek_y:.0f}px; font-family:var(--f-serif); font-weight:700; font-size:{dpx:.0f}px; white-space:nowrap">{X.rich(dek)}</div>' if dek else "")
             + f'{body_bars}<div class="ht" style="opacity:.1"></div></div></div>')
    if g.v: fall = [(px_ + 420, py_ + ph - 220), (px_ + 560, py_ + ph - 150), (px_ + 660, py_ + ph - 190), (px_ + 800, py_ + ph - 40), (px_ + 860, py_ + ph - 70)]
    else:   fall = [(1270, 330), (1400, 450), (1500, 410), (1640, 640), (1760, 600)]
    tx_, ty_ = fall[-1]
    body = (paper + marker(fall, INK, 11, "fall") + marker([(tx_ - 54, ty_ - 6), (tx_, ty_), (tx_ - 8, ty_ - 56)], INK, 11, "tip")
            + tape(r, px_ + 30, py_ - 10, 160) + tape(r, px_ + pw - 200, py_ + ph - 30, 170))
    gg, s = page(X, b, t, d, cid, body)
    X.tw(f'tl.from("{s} .bpp .sc", {{y:-200, rotation:-14, opacity:0, duration:0.27, ease:"steps(4)"}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "tear")
    slap(X, f"{s} .bh .rl", t + 0.35, 0.05)
    X.sfx(t + 0.35, "type")
    draw(X, f"{s} .mkr", tdp - 0.1, 0.4)
    draw(X, f"{s} .fall", tdp + 0.1, 0.5); draw(X, f"{s} .tip", tdp + 0.6, 0.134)
    X.sfx(tdp, "hit")
    X.tw(f'tl.to("{s} .cam", {{keyframes:[{{x:-12, duration:0.067}}, {{x:9, duration:0.067}}, {{x:-5, duration:0.067}}, {{x:0, duration:0.067}}], ease:"none"}}, {tdp + 0.05:.3f});')
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)", stagger:0.1}}, {t + 0.35:.3f});')


def note(b, X, t, d, cid):
    """a torn notebook page with the worry handwritten, a sticky label, and a seesaw doodle tipping toward one critter."""
    r = R(X, cid); g = L(X)
    tb = T(X, b, "at_bet", t, t + d * 0.5)
    if g.v: nx, ny, nw, nh = g.m, 330, g.cw, 600; sx, sy, ss = 500, 1040, 1.0
    else:   nx, ny, nw, nh = g.m + 30, 160, 880, 720; sx, sy, ss = 1390, 600, 1.15
    txt = fit.as_text(b.get("text", ""))
    f = fit.fit_text(txt, nw - 160, nh - 130, 96, 40, lh=1.45, max_lines=4)
    lab, left_ = b.get("label", ""), b.get("left", "公司")
    X.used_text.update(fit.plain(txt) + lab + left_)
    lh = f.px * 1.45
    lines_ = "".join(f'<div class="nl">{X.rich(l)}</div>' for l in f.lines)
    # each ruled line lands just under the marker baseline (line-height 1.45, ascent .88 → baseline at .76 of a line)
    paper = (f'<div class="bo bnp" style="{st(left=nx, top=ny, width=nw, height=nh)}"><div class="sc" style="position:absolute; inset:0; transform:rotate(1.2deg); clip-path:{torn(r, 1.2, 10)};'
             f' background:repeating-linear-gradient(180deg, transparent 0 {lh - 3:.0f}px, rgba(0,95,170,.28) {lh - 3:.0f}px {lh:.0f}px) 0 {63 - lh * 0.142:.0f}px / 100% {lh:.0f}px, #fbf8f0">'
             f'<i style="position:absolute; left:88px; top:0; bottom:0; width:3px; background:rgba(255,63,160,.55)"></i>'
             f'<div class="nt" style="position:absolute; left:116px; top:60px; font-family:var(--f-hand); font-size:{f.px}px; line-height:1.45">{lines_}</div></div></div>')
    stick = (f'<div class="bo bsk" style="{st(left=nx + nw - (330 if g.v else 300), top=ny + nh - 60)}"><div class="sc" style="position:relative; background:{TEAL}; color:{WHITE}; padding:16px 22px; '
             f'font-family:var(--f-hand); font-size:{38 if g.v else 40}px; white-space:nowrap; transform:rotate(6deg)">{X.rich(lab)}</div></div>') if lab else ""
    bw = 420 * ss
    see = (f'<div class="bo bsee" style="{st(left=sx - bw / 2, top=sy)}">'
           f'<svg style="position:absolute; left:{bw / 2 - 40:.0f}px; top:40px; width:80px; height:70px; overflow:visible"><path d="M40 0 L80 70 L0 70 Z" fill="{INK}"/></svg>'
           f'<div class="beam" style="position:absolute; left:0; top:28px; width:{bw:.0f}px; height:12px; background:{INK}; border-radius:6px; transform-origin:50% 50%">'
           f'<div style="position:absolute; left:6px; bottom:12px; padding:{14 * ss:.0f}px {16 * ss:.0f}px; background:{NEWS}; border:3px solid {INK}; font-family:var(--f-hand); font-size:{32 * ss:.0f}px; white-space:nowrap">{X.rich(left_)}</div>'
           f'<div style="position:absolute; right:-10px; bottom:6px">{critter(r, 130 * ss, PINK)}</div></div></div>')
    gg, s = page(X, b, t, d, cid, paper + stick + see + tape(r, nx + nw * 0.4, ny - 14, 180))
    X.tw(f'tl.from("{s} .bnp .sc", {{x:-260, rotation:-12, opacity:0, duration:0.27, ease:"steps(4)"}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "tear")
    per = min(0.5, max(0.25, (tb - t - 0.4) / max(1, len(f.lines))))
    X.tw(f'tl.fromTo("{s} .nl", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{per:.2f}, ease:"steps({max(4, round(per * 15))})", stagger:{per:.2f}}}, {t + 0.35:.3f});')
    X.sfx(t + 0.35, "type")
    X.tw(f'tl.from("{s} .bsee svg, {s} .beam", {{opacity:0, y:40, duration:0.2, ease:"steps(3)"}}, {max(t + 0.4, tb - 0.6):.3f});')
    X.tw(f'tl.fromTo("{s} .beam", {{rotation:-4}}, {{rotation:14, duration:0.4, ease:"steps(6)", immediateRender:false}}, {tb:.3f});')
    X.sfx(tb, "hit")
    if lab: X.tw(f'tl.from("{s} .bsk .sc", {{scale:0, rotation:-30, duration:0.2, ease:"steps(3)"}}, {tb + 0.4:.3f});')
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)"}}, {t + 0.3:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.05, 0.3, 0.4), (tb - 0.3, 1.0, 0.5, 0.5)])


def thesis(b, X, t, d, cid):
    """the judgment as ransom lettering: the ~wrong word~ gets a marker strike, the right line slams in hot pink."""
    r = R(X, cid); g = L(X)
    tk, te = T(X, b, "at_strike", t, t + d * 0.4), T(X, b, "at_em", t, t + d * 0.6)
    if g.v: x1, y1, w1, w2 = g.m, 360, g.cw, g.lw
    else:   x1, y1, w1, w2 = g.m + 20, 190, 1500, 1240
    a, apx, an = ransom(X, r, b.get("a", ""), w1, 320, 150, 2, mark="strike")
    bb, bpx, bn = ransom(X, r, "*" + b.get("b", "") + "*", w2, 340, 260, 2)
    y2 = y1 + apx * 1.27 * an + (60 if g.v else 50)
    if g.v: cs = min(280, g.bot - (y2 + bpx * 1.3 * bn + 30)); ccx, ccy = g.W - 120 - cs * 1.3, y2 + bpx * 1.3 * bn + 30
    else:   cs = 330; ccx, ccy = g.W - 520, y2 + 10
    crit = f'<div class="bo tcr" style="{st(left=ccx, top=ccy)}">{critter(r, cs, PINK)}</div>' if cs > 140 else ""
    hpos = [(ccx + cs * 1.05, ccy + cs * 0.2), (ccx + cs * 1.2, ccy + cs * 0.55), (ccx - cs * 0.05, ccy + cs * 0.12)] if crit else []
    hearts = "".join(marker([(cx, cy), (cx - 26, cy - 30), (cx - 2, cy - 44), (cx, cy - 26), (cx + 2, cy - 44), (cx + 26, cy - 30), (cx, cy)], PINK, 7, f"hh hh{k}") for k, (cx, cy) in enumerate(hpos))
    body = (f'<div class="bo ta" style="{st(left=x1, top=y1)}">{a}</div><div class="bo tb2" style="{st(left=x1, top=y2)}">{bb}</div>'
            + crit + hearts + tape(r, x1 - 20, y2 - 10, 160, pink=True))
    gg, s = page(X, b, t, d, cid, body)
    slap(X, f"{s} .ta .rl", t + 0.15, 0.06)
    X.sfx(t + 0.15, "type")
    draw(X, f"{s} .mkr", tk - 0.05, 0.27)
    X.sfx(tk, "tear")
    slap(X, f"{s} .tb2 .rl", te - 0.2, 0.09, 1.4)
    X.sfx(te - 0.05, "slam")
    X.tw(f'tl.from("{s} .tcr svg", {{scale:0.3, rotation:24, opacity:0, duration:0.27, ease:"steps(4)"}}, {te + 0.05:.3f});')
    for k in range(len(hpos)): draw(X, f"{s} .hh{k}", te + 0.3 + k * 0.15, 0.27)
    X.tw(f'tl.from("{s} .tape", {{scaleX:0, duration:0.134, ease:"steps(2)"}}, {te:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5), (te - 0.3, 1.06, 0.4, 0.6)])


def outro(b, X, t, d, cid):
    """the back cover: the channel name as ransom letters on a dark page and a stamp; the host sticker joins (cameo)."""
    r = R(X, cid); g = L(X)
    if g.v: x, y, w = g.m, 400, g.cw
    else:   x, y, w = g.m + 40, 250, 1100
    name, npx, nn = ransom(X, r, b.get("title", "第九顶帽子"), w, 280, 170, 2)
    sub = b.get("sub", "")
    X.used_text.update(sub)
    ye = y + npx * 1.27 * nn
    body = (f'<div class="bo on" style="{st(left=x, top=y)}">{name}</div>'
            + (f'<div class="bo typed os" style="{st(left=x + 6, top=ye + 30, font_size=30)}; color:{WHITE}">{X.rich(sub)}</div>' if sub else "")
            + (f'<div class="bo ost" style="{st(left=x + 10, top=ye + 110)}">{stamp(X, b.get("stamp", ""), b.get("stamp_sub", ""), 70 if g.v else 80, -8)}</div>' if b.get("stamp") else "")
            + tape(r, x - 30, y - 20, 170, pink=True))
    gg, s = page(X, b, t, d, cid, body, dark=True)
    slap(X, f"{s} .on .rl", t + 0.15, 0.07)
    X.sfx(t + 0.15, "type")
    if sub: X.tw(f'tl.from("{s} .os", {{opacity:0, duration:0.2, ease:"steps(3)"}}, {t + 0.6:.3f});')
    if b.get("stamp"):
        thud(X, f"{s} .stamp", t + 0.85)
        X.sfx(t + 0.85, "stamp")
    cam(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5)])


# ---------------------------------------------------------------- effects drawn as zine pages
FX_CSS = r"""
#root.st-zine { --f-quote:var(--f-playfair); --f-num:var(--f-archivo); --f-latin:var(--f-type); }
.zf .zf-tex { position:absolute; inset:-60px; background-image:url("__NOISE__"); background-size:240px; opacity:.3; mix-blend-mode:multiply; }
.zf.dk .zf-tex { opacity:.45; mix-blend-mode:screen; filter:invert(1); }
.zf .zf-xer { position:absolute; inset:0; box-shadow:inset 0 0 140px rgba(0,0,0,.26), inset 0 0 18px rgba(0,0,0,.32); }
.zf .zf-streak { position:absolute; left:0; right:0; height:2px; background:rgba(0,0,0,.08); }
.zf.dk .zf-streak { background:rgba(255,255,255,.07); }
.zf .zf-mast { position:absolute; background:#141414; color:#fbf8f0; font-family:var(--f-type); letter-spacing:.06em; white-space:nowrap; padding:6px 16px 7px; rotate:-1.4deg; }
.zf.dk .zf-mast { box-shadow:4px 5px 0 #ff3fa0; }
.zf .zf-mast b { color:#ff3fa0; font-weight:400; }
.zf .zf-fx { position:absolute; background:rgba(238,228,188,.95); color:#141414; font-family:var(--f-type); white-space:nowrap; padding:6px 18px 7px; rotate:2.2deg;
  box-shadow:0 1px 2px rgba(0,0,0,.25); }
.zf .zf-fx i { font-style:normal; color:#a30d58; margin-right:8px; }
.zf .zf-tape { position:absolute; height:30px; background:rgba(238,228,188,.8); box-shadow:0 1px 2px rgba(0,0,0,.18); }
.zf .zf-tape.pk { background:rgba(255,63,160,.6); }
.zf .zf-staple { position:absolute; width:46px; height:7px; border-radius:3px; background:linear-gradient(180deg,#d9d9d9,#8c8c8c); box-shadow:0 1px 1px rgba(0,0,0,.4); }
.zf .zf-cap { position:absolute; left:0; right:0; display:flex; flex-direction:column; align-items:center; gap:4px; }
.zf .zf-cl { display:inline-block; background:#141414; color:#fbf8f0; font-family:var(--f-display); font-weight:800; line-height:1.22; padding:3px 20px 5px;
  box-shadow:5px 6px 0 #ff3fa0; white-space:nowrap; }
.zf .zf-cl .em .emt { background:#ff3fa0; color:#141414; padding:0 .12em; } .zf .zf-cl .em .emb { display:none; }
.zf .zf-ft { position:absolute; display:flex; justify-content:space-between; align-items:flex-end; gap:24px; }
.zf .zf-ft > div { background:#fbf8f0; color:#141414; font-family:var(--f-type); white-space:nowrap; padding:4px 12px 5px; box-shadow:2px 3px 0 rgba(0,0,0,.2); }
.zf .zf-ft .zf-src { rotate:.8deg; } .zf .zf-ft .zf-src i { font-style:normal; color:#c4126b; margin-right:8px; }
.zf .zf-ft .zf-lb { background:rgba(238,228,188,.95); rotate:-1deg; margin-left:auto; }
.zf .zf-peel { position:absolute; inset:-4% -14% -4% -4%; }
/* inside the effects: every card is a pasted scrap (square cut, hard print shadow, a tilt, tape), photos are photocopies,
   highlighter and accents come from the riso inks, and big type gets a pink misregistration */
#root.st-zine .fx :is(.ca-win, .cs-card, .cs-ghost, .cs-media, .wpc, .wpc-r, .wpc-hi, .wpc-rp, .wpc-in, .wpd-pl, .lw-t, .lw-ring, .ht-f, .ms-pic, .ms-pic img,
  .gf-st, .gf-win, .gf-ph, .sp-c, .sp-img, .sp-mk, .sp-code, .pl-c, .pl-o, .pl-o .hi, .pl-o .lt, .sc-img, .d2-sheet, .ca-box, .ca-bar span) { border-radius:0 !important; }
#root.st-zine .fx :is(.ca-win, .cs-card, .wpc, .lw-t, .ht-f, .ms-pic, .gf-st, .gf-win, .gf-ph, .sp-c, .sp-img, .pl-c, .sc-img, .d2-sheet, .cp .ph) { box-shadow:8px 10px 0 var(--zsh, rgba(20,20,20,.85)) !important; }
#root.st-zine .fx .cs-ghost { box-shadow:6px 7px 0 var(--zsh, rgba(20,20,20,.85)) !important; }
#root.st-zine .fx :is(.ca-win, .wpc, .pl-c, .ht-f) { rotate:-1.2deg; }
#root.st-zine .fx :is(.cs-card, .sp-c, .gf-fr) { rotate:1deg; }
#root.st-zine .fx .lw-t:nth-child(odd) { rotate:-2deg; } #root.st-zine .fx .lw-t:nth-child(even) { rotate:1.6deg; }
#root.st-zine .fx :is(.cs-card, .pl-c, .sp-c, .gf-fr, .ms-pic)::before { content:""; position:absolute; left:50%; top:-15px; width:130px; height:30px; margin-left:-65px;
  background:rgba(238,228,188,.85); rotate:-3deg; box-shadow:0 1px 2px rgba(0,0,0,.2); z-index:5; pointer-events:none; }
#root.st-zine .fx :is(.cp img, .cs-mimg, .sc-img, .ms-pic img, .sp-img img, .ca-shot img, .gf-fr img, .wpd-bg) { filter:grayscale(1) contrast(1.28) brightness(1.04); }
#root.st-zine .fx :is(.d2 .em .emb, .ct-root .em .emb, .d2-mk) { background:var(--hl, #ff3fa0) !important; border-radius:0 !important; }
#root.st-zine .fx :is(.d2-ttl, .lw-sub, .gf-cap, .pl-q, .sp-n, .sc .sc-t, .ca-h, .cs-stat b, .cs-zh) { text-shadow:3px 3px 0 rgba(255,63,160,.5); }
#root.st-zine .fx .d2-kick { border-radius:0; background:#141414; color:#fbf8f0; font-family:var(--f-type); rotate:-2deg; box-shadow:4px 5px 0 #ff3fa0; }
#root.st-zine .fx .d2-tag { border-radius:0; background:#fbf8f0; color:#141414; font-family:var(--f-type); box-shadow:2px 3px 0 rgba(0,0,0,.2); }
#root.st-zine .fx .ct-kick { border-radius:0; font-family:var(--f-type); rotate:-1.5deg; box-shadow:4px 5px 0 #ff3fa0; }
/* collage: torn photocopies on the zine ground, marker in riso pink */
#root.st-zine .fx .cbg { background:transparent; } #root.st-zine .fx .arw path { stroke:#e0007a; }
#root.st-zine .fx .cnote { color:#e0007a; font-family:var(--f-hand); }
/* article / post as clippings */
#root.st-zine .fx .ca-win { background:#fbf8f0; } #root.st-zine .fx .ca-bar { background:#e2dccd; border-bottom:2px solid #141414; }
#root.st-zine .fx .ca-bar i { background:#141414; } #root.st-zine .fx .ca-bar i:first-child { background:#ff3fa0; }
#root.st-zine .fx .ca-bar span { font-family:var(--f-type); background:#fbf8f0; }
#root.st-zine .fx .ca-top span { color:#b0105f; } #root.st-zine .fx .ca-ex { border-left-color:#ff3fa0; } #root.st-zine .fx .ca-box { border-color:#ff3fa0; }
#root.st-zine .fx .cs-ver circle { fill:#00857f; }
/* comments, danmaku, logos, polls, sponsor: plates, stickers, coupons */
#root.st-zine .fx .wpc-hd { background:#141414; color:#fbf8f0; font-family:var(--f-type); }
#root.st-zine .fx .wpc-hot { border-radius:0; background:#ff3fa0; color:#141414; }
#root.st-zine .fx .wpd-hn { border-radius:0; background:#ff3fa0; color:#141414; box-shadow:8px 10px 0 #141414; rotate:-2deg; }
#root.st-zine .fx .wpd-i.hl { color:#ff7cc0; }
#root.st-zine .fx .lw-t b { color:var(--card-fg); opacity:.6; }
#root.st-zine .fx .sp-ad { border-radius:0; background:#ff3fa0; color:#141414; rotate:-2deg; }
#root.st-zine .fx .sp-code { border-color:#141414; rotate:-1.5deg; background:#fbf8f0; }
#root.st-zine .fx :is(.sp-cta, .pl-cta) { border-radius:0; background:#141414; color:#fbf8f0; box-shadow:5px 6px 0 #ff3fa0; rotate:-1.5deg; }
#root.st-zine .fx .pl-o { border:3px solid var(--card-fg); }
#root.st-zine .fx .pl-o.win .fill { background:repeating-linear-gradient(45deg, #ff3fa0 0 10px, #ff70b9 10px 20px); }
#root.st-zine .fx .pl-k { font-family:var(--f-type); }
"""


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect, as a zine spread: photocopy grain over everything, the masthead strip, the effect id on
    masking tape, the spoken line as black cut-out plates with a pink offset, the source and label as typed scraps, tape and
    staples, and the torn riso sheet that opens the page."""
    from h9 import aefx
    X.css("zine-fx", FX_CSS.replace("__NOISE__", NOISE))
    r = R(X, f"{cid}-fx")
    v = X.portrait; W, H = X.W, X.H
    th = aefx.THEMES.get(p.get("theme")) or {}
    dark = (aefx._lum(th.get("bg", "#ece7dc")) or 1) < 0.2 or parts["photo"]
    host = bool(p.get("host"))
    # caption: 16:9 keeps the fitted lines; 9:16 refits so up to three plates end above the platform's bottom bar
    if v:
        line = fit.as_text(p.get("line", ""), " ")
        f = fit.fit_text(line, W - 2 * 120 - 48, 3 * 44 * 1.22, 44, 28, lh=1.22, max_lines=3)
        if len(f.lines) == 3: f = fit.fit_text(line, W - 2 * 120 - 48, 3 * 36 * 1.22, 36, 26, lh=1.22, max_lines=3)
        cap_lines, cpx = [X.rich(l) for l in f.lines], f.px
    else:
        cap_lines, cpx = parts["cap_lines"], parts["cap_px"]
    plates = "".join(f'<span class="zf-cl zf-b" style="font-size:{cpx}px; rotate:{(-0.9 if k % 2 == 0 else 0.8):.1f}deg'
                     + ("" if v else f'; margin-left:{(-14 if k % 2 == 0 else 18)}px') + f'">{l}</span>' for k, l in enumerate(cap_lines))
    cap_h = len(cap_lines) * (cpx * 1.22 + 8) + 4 * max(0, len(cap_lines) - 1)
    if v:
        cap = f'<div class="zf-cap" style="top:1318px; padding:0 120px">{plates}</div>'
        ft_pos = f"left:56px; right:120px; top:{1318 + cap_h + 12:.0f}px; font-size:17px"
        mast_pos, fx_pos = "left:56px; top:206px; font-size:20px", f"right:{340 if host else 56}px; top:208px; font-size:18px"
    else:
        cap = f'<div class="zf-cap" style="bottom:60px">{plates}</div>'
        ft_pos = "left:80px; right:80px; bottom:18px; font-size:16px"
        mast_pos, fx_pos = "left:80px; top:32px; font-size:20px", "right:80px; top:30px; font-size:18px"
    src_h, foot_h = parts["src"], parts["foot"]
    if v:     # 9:16: the row ends 120 px from the right edge (platform buttons), so source and label are refitted to share it
        mw = lambda s_: fit.width(s_, mono=True) * 17 * 1.04
        avail = W - 56 - 120 - 24
        src_s = fit.plain(p.get("src", ""))
        sw = min(mw(src_s), avail * 0.5) if src_s else 0
        if src_s: src_h = X.rich(fit.fit_text(src_s, sw, 24, 17, 17, max_lines=1, mono=True, ls=0.04).lines[0])
        lab_s = (fit.plain(p["label"]) + ("　" + fit.plain(p["ref"]) if p.get("ref") else "")) if p.get("label") else ""
        lw = avail - (sw + 24 + 44 if src_s else 0) - 24
        foot_h = X.rich(fit.fit_text(lab_s, lw, 24, 17, 17, max_lines=1, mono=True, ls=0.04).lines[0]) if lab_s else ""
    foot = (f'<div class="zf-src zf-b"><i>SRC</i>{src_h}</div>' if src_h else "") + (f'<div class="zf-lb zf-b">{foot_h}</div>' if foot_h else "")
    X.used_text.update("第九顶帽子ZINE·FXSRC")
    tapes = (f'<i class="zf-tape zf-b" style="{st(left=-34, top=118 if not v else 300, width=150)}; rotate:-38deg"></i>'
             f'<i class="zf-tape pk zf-b" style="{st(left=W - 120, top=(H - 230) if not v else 1180, width=150)}; rotate:-32deg"></i>')
    staples = "" if v else (f'<i class="zf-staple" style="{st(left=24, top=330)}; transform:rotate(-84deg)"></i>'
                            f'<i class="zf-staple" style="{st(left=24, top=760)}; transform:rotate(-96deg)"></i>')
    streaks = "".join(f'<i class="zf-streak" style="top:{r.randint(0, H)}px; opacity:{r.uniform(.3, 1):.2f}"></i>' for _ in range(3))
    col = [PINK, TEAL, INK][X.beat["i"] % 3]
    peel = f'<div class="zf-peel" style="background:{col}; clip-path:{torn(r, 2.2, 14)}"></div>' if X.beat["i"] > 0 else ""
    inner = (f'<div class="zf-tex"></div>{streaks}<div class="zf-xer"></div>{tapes}{staples}'
             f'<div class="zf-mast zf-b" data-layout-allow-overlap style="{mast_pos}">第九顶帽子 <b>·</b> ZINE <b>·</b> {parts["topic"]}</div>'
             f'<div class="zf-fx zf-b" data-layout-allow-overlap style="{fx_pos}"><i>FX</i>{parts["fxid"]}</div>'
             f'{cap}<div class="zf-ft" style="{ft_pos}">{foot}</div>{peel}')
    X.clip(f"{cid}c", t, d, inner, f"ctx zf{' dk' if dark else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    if peel:
        X.tw(f'tl.to("{s} .zf-peel", {{xPercent:-118, rotation:-4, duration:0.3, ease:"steps(5)"}}, {t:.3f});')
        X.sfx(t, "tear")
    X.tw(f'tl.from("{s} .zf-mast, {s} .zf-fx, {s} .zf-ft > div", {{scale:1.3, opacity:0, duration:0.2, ease:"steps(3)", stagger:0.07}}, {t + 0.08:.3f});')
    X.tw(f'tl.from("{s} .zf-tape", {{scaleX:0, duration:0.134, ease:"steps(2)", stagger:0.1}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .zf-cl", {{scale:1.25, opacity:0, rotation:(i)=>i % 2 ? 7 : -7, duration:0.2, ease:"steps(3)", stagger:0.08}}, {t + 0.05:.3f});')
    boil(X, f"{s} .zf-b", t, d, rot=False)


SCENES = {"cover": cover, "versus": versus, "pie": pie, "bars": bars, "stamps": stamps, "clip": clip, "note": note, "thesis": thesis, "outro": outro}
