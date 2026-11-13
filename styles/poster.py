"""poster · 瑞士海报 —— 国际主义字体排印（Müller-Brockmann 的网格、Experimental Jetset / Pentagram 的动态识别）做观点口播。
冷白纸 #f2f2ef、墨黑 #0a0a0a、一个信号蓝 #1f3bff；超窄 Archivo 数字 + 思源黑体 900，巨字贴 56 px 边距左齐，可以出血裁掉右边或底边。
每一页换一种版式，按顺序轮换：(a) 数字占满上 60%，下面一行字 + 6 px 粗线 · (b) 3–4 行大字从上排到下 · (c) 竖排：大字转 90° 占左 5 栏，
右边一小块文字 · (d) 上墨下纸对半分，字跨过分界线、过线就变色 · (e) 12 栏网格画出来，内容卡进格子，底部 01–12 栏号。
转折处整屏反色（墨底、蓝底）；底部永远有家具：6 px 粗线 + 页码 "03 / 07" + 出处。字幕无底框：墨色 40 px 左齐，左边一根 6 px 蓝条。
动作是机械的：expo.out 0.45 s，字从基线遮罩擦出，网格栏线滑开；只有换底色（章节）时才用栏条转场；不淡入、不模糊、不回弹。没有照片，没有角色。

场景（SCENES，全部自写）：hundred 一百个答案 (a) · problem 问题反转 (b) · quote 引语 (c) · price 生成与判断的跷跷板 (d) ·
keep 做出多少 / 扔掉多少 (e) · thesis 判断句 (b, 蓝底) · outro 落版。横屏竖屏各自排版。
"""

STYLE = {
    "name": "瑞士海报", "en": "Poster", "benchmarks": ["Josef Müller-Brockmann", "Experimental Jetset", "Pentagram motion identities"],
    "tokens": {
        "bg": "#f2f2ef", "fg": "#0a0a0a", "muted": "#8d8d88", "accent": "#1f3bff", "accent2": "#1f3bff", "alert": "#1f3bff",
        "line": "#d6d6d1", "paper": "#f2f2ef", "ink": "#0a0a0a", "card": "#ffffff", "card-fg": "#0a0a0a", "blue": "#1f3bff",
        "cap-bg": "none", "cap-fg": "#0a0a0a", "cap-bar": "#1f3bff", "cap-size": "40px", "cap-weight": "700", "cap-pad": "0", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "40px", "cap-em": "#1f3bff",
    },
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "num": "archivo", "latin": "archivo", "mono": "archivo"},
    "motion": {"ease": "expo.out", "dur": 0.45, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [],
    # no characters in a poster: the host is off (build.py still places it on cameo beats, so it is also hidden in css)
    "mascot": {"mode": "none"},
    "sfx": {"enter": ("whoosh_soft", 0.25), "pop": ("tick", 0.4), "hit": ("hit", 0.4), "slam": ("slam", 0.4), "count": ("type", 0.25),
            "click": ("click", 0.3), "mascot": None, "wipe": ("whoosh", 0.25), "line": ("click", 0.3)},
    "css": """
.st-poster .mascot { display:none !important; }
/* caption: no box. flush left on the margin, a 6 px bar hangs 14 px left of it; colours follow the page ground (--cap-fg / --cap-bar) */
#root.st-poster .clip.cap { left:80px; right:80px; top:872px; bottom:auto; height:auto; text-align:left; padding:0; }
#root.v.st-poster .clip.cap { left:56px; right:120px; top:1392px; padding:0; }   /* 9:16: under the content (ends 1374), above the source line */
.st-poster .cap .cp { position:relative; display:inline-block; background:none; padding:0; border-radius:0; text-shadow:none; box-shadow:none;
  color:var(--cap-fg); font-size:40px; font-weight:700; line-height:1.25; letter-spacing:0; }
.st-poster .cap .cp::before { content:""; position:absolute; left:-20px; top:.14em; bottom:.1em; width:6px; background:var(--cap-bar); }
.st-poster .cap .em .emt { color:inherit; box-shadow:inset 0 -.14em 0 var(--cap-bar); }
/* effect internals, poster-cut: flush-left type on the grid margin, rules instead of boxes, square corners, condensed numerals */
.st-poster .fx > .stage > .col { width:100%; box-sizing:border-box; padding:0 80px; align-items:flex-start; }
.st-poster .fx > .stage > .col .big, .st-poster .fx > .stage > .col .sub { text-align:left; }
.st-poster .fx > .stage > .f3 { width:100%; box-sizing:border-box; padding:0 80px; text-align:left; }
#root.v.st-poster .fx > .stage > .col, #root.v.st-poster .fx > .stage > .f3 { padding:0 120px 0 56px; }
.st-poster .fx .big { letter-spacing:-.03em; line-height:.96; }
.st-poster .fx .sub { align-self:stretch; font-family:var(--f-latin); font-weight:700; font-size:2.6vmin; letter-spacing:.02em; color:var(--accent);
  border-top:6px solid var(--fg); padding-top:1.3vmin; margin-top:2.4vmin; max-width:none; }
.st-poster .fx .sw { justify-content:flex-start; padding:0 80px; text-align:left; letter-spacing:-.03em; }
#root.v.st-poster .fx .sw { padding:0 120px 0 56px; }
.st-poster .fx .sw.s2 { color:#fff; -webkit-text-stroke:0; }
.st-poster .fx .an { font-family:var(--f-latin); color:var(--fg); } .st-poster .fx .an i { height:2px; background:var(--fg); }
.st-poster .fx .w3k, .st-poster .fx .dtc-eq b, .st-poster .fx .cov { font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; letter-spacing:-.03em; }
.st-poster .fx .w3t, .st-poster .fx .coq, .st-poster .fx .dtc-h { letter-spacing:-.025em; }
.st-poster .fx .ws .ws-slot .ws-bg { border-radius:0; inset:.02em -.06em; background:var(--fg); } .st-poster .fx .ws .ws-u { height:.1em; }
.st-poster .fx .ws .ws-reel span, .st-poster .fx .ws .ws-reel span.last { color:var(--bg); } .st-poster .fx .ws .ws-x { background:var(--accent); }
.st-poster .fx .qd .qd-d i, .st-poster .fx .qd .qd-d .rg { border-radius:0; } .st-poster .fx .qd .qd-q.hot { background:color-mix(in srgb, var(--accent) 22%, transparent); }
.st-poster .fx .dtc .sp { stroke-linecap:butt; } .st-poster .fx .dtc .glb { stroke-width:.5; }
.st-poster .fx .bs .bs-t .em .emb { background:var(--accent); } .st-poster .fx .bs .bs-vig { display:none; } .st-poster .fx .bs .bs-s { font-family:var(--f-latin); letter-spacing:.02em; }
.st-poster .fx .co .coc { border-radius:0; border:0; border-top:6px solid var(--card-fg); } .st-poster .fx .co .coc.pk { border-top-color:var(--accent); }
.st-poster .fx .co .cok { font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; font-size:28px; color:var(--card-fg); }
.st-poster .fx .co .coy { border-radius:0; } .st-poster .fx .co .cosel { border-radius:0; box-shadow:none; border-width:4px; }
.st-poster .fx .cv .cvs { border-radius:0; box-shadow:inset 0 4px 0 var(--card-fg); } .st-poster .fx .cv .cvt { border-radius:0; box-shadow:inset 0 0 0 4px var(--accent); }
.st-poster .fx .cv .cvd { border-radius:0; box-shadow:none; } .st-poster .fx .cv .cvp { stroke-linecap:butt; }
.st-poster .fx .sl-scr { border-radius:0; box-shadow:0 0 0 3px var(--fg); } .st-poster .fx .sl-t, .st-poster .fx .sl-cur { border-radius:0; }
""",
    # the four effect grounds: cool white, ink, signal blue, white-on-paper. No grey ground: the poster has three colours.
    "fx_themes": {
        "paper": {"bg": "#f2f2ef", "fg": "#0a0a0a", "muted": "#8d8d88", "accent": "#1f3bff", "card": "#ffffff", "card-fg": "#0a0a0a", "line": "#d6d6d1",
                  "pc-fg": "#0a0a0a", "pc-bar": "#1f3bff", "pc-em": "#1f3bff"},
        "ink":   {"bg": "#0a0a0a", "fg": "#f2f2ef", "muted": "#8d8d88", "accent": "#1f3bff", "card": "#161616", "card-fg": "#f2f2ef", "line": "#2a2a2a",
                  "pc-fg": "#f2f2ef", "pc-bar": "#1f3bff", "pc-em": "#f2f2ef"},
        "red":   {"bg": "#1f3bff", "fg": "#f2f2ef", "muted": "rgba(242,242,239,.78)", "accent": "#0a0a0a", "card": "#f2f2ef", "card-fg": "#0a0a0a", "line": "rgba(242,242,239,.35)",
                  "pc-fg": "#f2f2ef", "pc-bar": "#0a0a0a", "pc-em": "#f2f2ef"},
        "lemon": {"bg": "#ffffff", "fg": "#0a0a0a", "muted": "#8d8d88", "accent": "#1f3bff", "card": "#f2f2ef", "card-fg": "#0a0a0a", "line": "rgba(10,10,10,.18)",
                  "pc-fg": "#0a0a0a", "pc-bar": "#1f3bff", "pc-em": "#1f3bff"},
    },
}

# the three grounds: (page background, type colour, accent on it, caption text, caption bar)
GROUNDS = {
    "paper": ("#f2f2ef", "#0a0a0a", "#1f3bff", "#0a0a0a", "#1f3bff"),
    "ink":   ("#0a0a0a", "#f2f2ef", "#1f3bff", "#f2f2ef", "#1f3bff"),
    "blue":  ("#1f3bff", "#f2f2ef", "#0a0a0a", "#f2f2ef", "#0a0a0a"),
}

CSS = r"""
.st-poster .em .emb { display:none; }
.po { position:absolute; inset:0; overflow:hidden; background:var(--pg); color:var(--pf); }
.po.g-paper { --pg:#f2f2ef; --pf:#0a0a0a; --pa:#1f3bff; }
.po.g-ink { --pg:#0a0a0a; --pf:#f2f2ef; --pa:#1f3bff; }
.po.g-blue { --pg:#1f3bff; --pf:#f2f2ef; --pa:#0a0a0a; }
.po .acc { color:var(--pa); }
.po .ink { color:#0a0a0a; }
/* the grid: 2 px column lines, drawn when a page shows its structure */
.po .grid i { position:absolute; width:2px; background:currentColor; opacity:.2; }
.po .ix { position:absolute; font-family:var(--f-num); font-variation-settings:"wdth" 75, "wght" 700; color:#8d8d88; letter-spacing:0; white-space:nowrap; }
/* bottom furniture: the 6 px rule with the page's place on it, the folio, the source */
.po .rl { position:absolute; height:6px; background:currentColor; transform-origin:0 50%; }
.po .seg { position:absolute; height:6px; background:var(--pa); transform-origin:0 50%; }
.po .folio { position:absolute; font-family:var(--f-num); font-variation-settings:"wdth" 75, "wght" 900; line-height:1; letter-spacing:-.01em; white-space:nowrap; }
.po .folio span { color:#8d8d88; }
.po .src { position:absolute; font-family:var(--f-latin), var(--f-body); font-weight:600; line-height:1.3; letter-spacing:0; }
/* type */
.po .zh { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1; letter-spacing:-.03em; white-space:nowrap; }
.po .tx { position:absolute; font-family:var(--f-display); font-weight:700; line-height:1.12; letter-spacing:-.01em; white-space:nowrap; }
.po .la { position:absolute; font-family:var(--f-latin); font-variation-settings:"wdth" 82, "wght" 700; letter-spacing:0; line-height:1.15; }
/* the box hugs the figures (line-height .78) */
.po .nm { position:absolute; font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; line-height:.78; letter-spacing:-.03em;
  font-variant-numeric:tabular-nums; white-space:nowrap; }
.po .bar { position:absolute; background:var(--pa); transform-origin:0 50%; }
/* the column wipe: 12 bars in the previous ground retract upward, one column after another (chapter changes only) */
.po .wipe { position:absolute; inset:0; z-index:20; pointer-events:none; }
.po .wipe i { position:absolute; top:0; bottom:0; transform-origin:50% 100%; }
"""


# ---------------------------------------------------------------- grid geometry
class G:
    """12-column grid in px for the current canvas, plus the fixed zones (content, caption, bottom furniture)."""
    def __init__(self, X):
        self.v = X.portrait
        self.W, self.H = X.W, X.H
        self.m = 56 if self.v else 80
        self.g = 12 if self.v else 20
        self.cw = (self.W - 2 * self.m - 11 * self.g) / 12
        self.top = 240 if self.v else 90            # content starts under the platform's top band
        self.bot = 1374 if self.v else 840          # text ends here (9:16: the caption takes 1392-1440, the source line 1452-1514, the platform's bottom band starts at 1520)
        self.rule = 1790 if self.v else 966         # the 6 px rule of the bottom furniture
        self.R = self.W - self.m                    # right margin line (pictures and the cropped numerals)
        self.tr = 960 if self.v else self.R          # right edge for readable text (9:16: clear of the platform buttons)
        self.tw = self.tr - self.m

    def x(self, c): return round(self.m + c * (self.cw + self.g))
    def w(self, n): return round(n * self.cw + (n - 1) * self.g)


from h9 import fit

DIG = 0.4325        # advance of one Archivo figure at wdth 62 / wght 900, in em (before tracking)
TRACK = 0.03
NUM_TOP = 0.026   # figure top below the element top at line-height .78, in em
NUM_H = 0.71      # figure height in em


def numw(txt):
    """em width of a run of figures in Archivo wdth 62 / 900 with -.03em tracking."""
    w = 0.0
    for c in str(txt):
        if c.isdigit(): w += DIG
        elif c in ".,:": w += 0.24
        elif c == "%": w += 0.62
        elif c in "-+": w += 0.36
        elif c.isascii() and c.isalpha(): w += 0.46
        else: w += fit.gw(c)
        w -= TRACK
    return max(w, 0.3)


def zhw(txt):
    """em width of a Chinese line at -.03em tracking."""
    return max(fit.width(txt) * 0.97, 0.5)


def zpx(txt, w, hi=260, lo=96):
    """the biggest headline size ≤ hi at which txt fits w on one line (never under lo)."""
    return round(max(lo, min(hi, w / zhw(txt))))


def zfit(txt, w, hi=260, lo=96, lines=2):
    """(px, text with | breaks, n lines) for a headline line in width w: the biggest size <= hi on one line; under lo it
    wraps into up to `lines` balanced lines; if even that needs less than lo, it sets lo and ellipsizes the last line."""
    txt = str(txt)
    px = min(hi, w / zhw(txt))
    if px >= lo or lines <= 1 and px >= lo * 0.6:
        return round(px), txt, 1
    n_ch = len(txt)
    for k in range(2, max(lines, 1) + 1):
        step = -(-n_ch // k)
        parts = [txt[i:i + step] for i in range(0, n_ch, step)]
        pk = min(hi, w / max(zhw(x) for x in parts))
        if pk >= lo:
            return round(pk), "|".join(parts), len(parts)
    per = max(1, int(w / (lo * 0.97)))
    k = max(lines, 1)
    parts = [txt[i:i + per] for i in range(0, per * k, per)]
    parts = [x for x in parts if x]
    if per * k < n_ch:
        parts[-1] = parts[-1][:-1] + "…"
    return round(lo), "|".join(parts), len(parts)


def bare(s):
    """headline copy without trailing / leading punctuation (posters set the words; the caption carries the sentence)."""
    return str(s).strip().strip("，。、！？；：,.!?;:")


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def st(**k):
    return "; ".join(f"{a.replace('_', '-')}:{v}px" if isinstance(v, (int, float)) else f"{a.replace('_', '-')}:{v}" for a, v in k.items())


def num(X, txt, x, y, f, cls="", inner=None):
    """a figure run whose ink top sits at y (line-height 1 box placed so)."""
    X.used_text.update(str(txt))
    return f'<div class="nm {cls}" data-safe="ignore" style="{st(left=round(x - 0.02 * f), top=round(y - NUM_TOP * f), font_size=round(f))}">{inner if inner is not None else X.rich(txt)}</div>'


def zh(X, txt, x, y, px, cls="", extra=""):
    return f'<div class="zh {cls}" style="{st(left=x, top=round(y), font_size=px)}{extra}">{X.rich(txt)}</div>'


# ---------------------------------------------------------------- motion helpers (mechanical: expo.out .45 s, masks, no fades)
def wipe_in(X, sel, t, dur=0.45, stg=0.0):
    """type enters by a mask wiping up from its baseline; the clip is released afterwards so nothing stays cropped."""
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(100% 0% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{dur}, ease:"expo.out", stagger:{stg}}}, {t:.3f});')
    X.tw(f'tl.set("{sel}", {{clipPath:"none"}}, {t + dur + stg * 12 + 0.02:.3f});')


def wipe_out(X, sel, t, dur=0.3):
    """leaves by the mask closing down onto the baseline."""
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(0% 0% 0% 0%)"}}, {{clipPath:"inset(100% 0% 0% 0%)", duration:{dur}, ease:"power3.in", immediateRender:false}}, {t:.3f});')


def hide_until(X, sel, t0, t):
    X.tw(f'tl.set("{sel}", {{clipPath:"inset(100% 0% 0% 0%)"}}, {t0:.3f});')
    wipe_in(X, sel, t)


def draw(X, sel, t, dur=0.45):
    X.tw(f'tl.from("{sel}", {{scaleX:0, duration:{dur}, ease:"expo.out"}}, {t:.3f});')


def counter(X, sel, t, a, b, dur=1.0, pad=0):
    js = f"String(Math.round(o.v)).padStart({pad}, '0')" if pad else "String(Math.round(o.v))"
    X.used_text.update("0123456789")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power2.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


# ---------------------------------------------------------------- the page
def frame(X, b, t, d, cid, ground="paper", src=None, grid=False, index=False):
    """page furniture: the bottom 6 px rule with this page's slot on it, the folio, the source (or the title);
    the 12 column lines when the page shows its grid; the column wipe when the ground changes (a chapter turn);
    the caption colours for this ground."""
    X.css("poster", CSS)
    g = G(X)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    s = f"#{cid}"
    fs = 44
    fy = g.rule + (22 if g.v else 16)
    X.used_text.update("0123456789/ ")
    seg_x = g.m + (g.W - 2 * g.m) * i / max(n, 1)
    seg_w = (g.W - 2 * g.m) / max(n, 1)
    furn = (f'<i class="rl rlb" style="{st(left=g.m, top=g.rule, width=g.W - 2 * g.m)}"></i>'
            f'<i class="seg" style="{st(left=round(seg_x), top=g.rule, width=round(seg_w))}"></i>'
            f'<div class="folio" style="{st(left=g.m, top=fy, font_size=fs)}">{i + 1:02d}<span> / {n:02d}</span></div>')
    text = src or b.get("src") or (f'{X.channel} — {meta.get("section", "")}'.strip(" —"))
    if text:
        if g.v:
            sf = fit.fit_text(fit.as_text(text, " "), g.tw, 24 * 1.3 * 2, 24, 22, lh=1.3, max_lines=2)
            sy = 1514 - len(sf.lines) * sf.px * 1.3
            furn += (f'<div class="src" style="{st(left=g.m, top=round(sy), width=g.tw, font_size=sf.px)}">'
                     + "<br>".join(X.rich(l) for l in sf.lines) + '</div>')
        else:
            sx = g.m + 230
            sw = g.R - sx
            sf = fit.fit_text(fit.as_text(text, " "), sw, 24 * 1.3, 24, 22, lh=1.3, max_lines=1)
            furn += f'<div class="src" style="{st(left=sx, top=fy + 2, width=sw, font_size=sf.px)}; white-space:nowrap">{X.rich(sf.lines[0])}</div>'
    lines = ""
    if grid:
        top, bot = (g.top - 20, g.rule - 60) if g.v else (g.top - 30, g.rule - 50)
        xs = [g.x(c) for c in range(12)] + [g.R]
        lines = "".join(f'<i style="{st(left=x - 1, top=top, height=bot - top)}"></i>' for x in xs)
        if index:
            iy = g.bot - 34 if g.v else (g.rule - 36)
            lines += "".join(f'<div class="ix tick" style="{st(left=g.x(c) + 6, top=iy, font_size=28)}">{c + 1:02d}</div>' for c in range(12))
        lines = f'<div class="grid">{lines}</div>'
    prev = getattr(X, "_po_prev", None)
    wipe = ""
    if prev is not None and prev != ground:
        col = GROUNDS[prev][0]
        strips = "".join(f'<i style="left:{(g.x(c) - g.g // 2 - 1) if c else 0}px; width:{round(g.cw + g.g) + 2 + (g.m if c in (0, 11) else 0)}px; background:{col}"></i>' for c in range(12))
        wipe = f'<div class="wipe">{strips}</div>'
        X.tw(f'tl.to("{s} .wipe i", {{scaleY:0, duration:0.3, ease:"power3.inOut", stagger:{{each:0.012, from:"start"}}}}, {t:.3f});')
        X.sfx(t, "wipe")
    X._po_prev = ground
    _, _, _, cf, cb = GROUNDS[ground]
    X.tw(f'tl.set("#root", {{"--cap-fg":"{cf}", "--cap-bar":"{cb}"}}, {t + (0.3 if wipe else 0):.3f});')   # flips as the bars clear the caption
    draw(X, f"{s} .rlb", t + 0.05, 0.6)
    X.tw(f'tl.from("{s} .seg", {{scaleX:0, duration:0.45, ease:"expo.out"}}, {t + 0.3:.3f});')
    wipe_in(X, f"{s} .folio", t + 0.1)
    if text: wipe_in(X, f"{s} .src", t + 0.2)
    if grid:
        # the columns slide out from the left margin to their places
        X.tw(f'tl.from("{s} .grid i", {{x:(k, el)=>{g.m} - parseFloat(el.style.left), duration:0.6, ease:"expo.out", stagger:0.015}}, {t + 0.05:.3f});')
        if index: wipe_in(X, f"{s} .grid .ix", t + 0.25, stg=0.02)
    return g, furn, lines, wipe


def page(X, cid, t, d, ground, furn, grid, wipe, body):
    X.clip(cid, t, d, f'<div class="po g-{ground}">{grid}{body}{furn}{wipe}</div>', "scene", 2)


# ---------------------------------------------------------------- scenes
def hundred(b, X, t, d, cid):
    """(a) the count fills the top 60 % edge to edge and rolls up to 100; one line of type under it; 100 ticks fill the rule."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "paper")
    tg = T(X, b, "at_n", t, t + 1.8)
    cnt_n = int(b.get("count", 100))
    pad = max(3, len(str(cnt_n)))
    unit = bare(b.get("unit") or fit.as_list(b.get("big", "答案"))[-1])
    X.css("po-hundred", """
.po .tk { position:absolute; }
.po .tk i { position:absolute; bottom:0; width:2px; background:currentColor; transform-origin:50% 100%; }
.po .tk i.hot { background:var(--pa); width:6px; }
.po .fd { position:absolute; display:grid; grid-template-columns:repeat(10, 1fr); }
.po .fd i { display:block; background:currentColor; }
.po .fd i.hot { background:var(--pa); }
""")
    if g.v:
        f = min(845, (g.W - g.m) * 1.1 / numw("0" * pad))      # may run 10 % past the right edge
        ny = 230
        upx, unit, un = zfit(unit, g.tw, 150, 72, 2)
        ux, uy = g.x(0), ny + NUM_H * f + 24
        tk = None                                         # 9:16: the 100 answers are a 10 x 10 field, not a tick strip
        ft = round(uy + un * upx + 30)
        fd = (g.m, ft, g.W - 2 * g.m, g.bot - ft)
        rl = None
        pre = None
    else:
        f = min(873, (g.x(8) - g.g - g.m) / numw("0" * pad))     # the count stops short of the text column
        ny = 110
        upx, unit, un = zfit(unit, g.R - g.x(8), 200, 60, 2)
        ux, uy = g.x(8), ny + NUM_H * f - upx * un * 0.98
        tk = (g.m, 776, g.W - 2 * g.m, 40)
        fd = None
        rl = 820
        pre = (g.x(8), 130)
    hot = min(36, cnt_n - 1)
    nt = min(cnt_n, 100)
    body = num(X, "0" * pad, g.m, ny, f, "cnt", f'<span class="cn">{"0" * pad}</span>') + zh(X, unit, ux, uy, upx, "unit")
    if tk:
        ticks = "".join(f'<i class="{"hot" if k == hot else ""}" style="left:{(tk[2] - 2) * k / max(nt - 1, 1):.1f}px; height:{tk[3] if k % 10 == 0 or k == hot else tk[3] * 0.55:.0f}px"></i>' for k in range(nt))
        body += (f'<div class="tk" style="{st(left=tk[0], top=tk[1], width=tk[2], height=tk[3])}">{ticks}</div>'
                 f'<i class="rl r2" style="{st(left=g.m, top=rl, width=g.W - 2 * g.m)}"></i>')
    if fd:
        cells = "".join(f'<i class="{"hot" if k == hot else ""}"></i>' for k in range(nt))
        body += f'<div class="fd" style="{st(left=fd[0], top=fd[1], width=fd[2], height=fd[3])}; gap:{g.g}px">{cells}</div>'

    if pre:
        ppx, ptxt, pn = zfit(bare(b.get("pre", "")), g.R - pre[0], 72, 36, 3) if b.get("pre") else (0, "", 0)
        if ppx: body += f'<div class="tx pre" style="{st(left=pre[0], top=pre[1], font_size=ppx)}">{X.rich(ptxt)}</div>'
    page(X, cid, t, d, "paper", furn, grid, wipe, body)
    s = f"#{cid}"
    wipe_in(X, f"{s} .nm", t + 0.08)
    counter(X, f"{s} .cn", t + 0.15, 0, cnt_n, dur=max(1.2, tg - t - 0.1), pad=pad)
    X.sfx(t + 0.15, "count")
    each = max(1.1, tg - t - 0.2) / max(nt, 1)
    if tk:
        draw(X, f"{s} .r2", t + 0.1, 0.45)
        X.tw(f'tl.from("{s} .tk i", {{scaleY:0, duration:0.12, ease:"none", stagger:{{each:{each:.4f}}}}}, {t + 0.15:.3f});')
    if fd:      # one cell per answer, in step with the count, row by row from the top
        X.tw(f'tl.from("{s} .fd i", {{scaleY:0, transformOrigin:"50% 100%", duration:0.12, ease:"none", stagger:{{each:{each:.4f}}}}}, {t + 0.15:.3f});')
    hide_until(X, f"{s} .unit", t, tg - 0.1)
    if pre: wipe_in(X, f"{s} .pre", t + 0.2)
    X.sfx(tg, "hit")


def problem(b, X, t, d, cid):
    """(b) on ink: the sentence stacked down the page in four lines; a blue bar strikes the claim on its word."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "ink")
    tk = T(X, b, "at_strike", t, t + d * 0.6)
    big, q, claim, strike = bare(b.get("big", "问题")), bare(b.get("q", "从来不是")), b.get("claim", "答案|不够多"), bare(b.get("strike", "不够多"))
    cl = [bare(c) for c in fit.as_list(claim)] if g.v else [bare(fit.plain(claim))]
    rows = [(big, 260), (q, 190)] + [(c, 260) for c in cl]
    wmax = g.tw
    fits = [zfit(r, wmax, hi, 96, 2) for r, hi in rows]
    rows = [(f_[1], hi) for f_, (r, hi) in zip(fits, rows)]
    sizes = [f_[0] for f_ in fits]
    nls = [f_[2] for f_ in fits]
    y0, y1 = (260, g.bot) if g.v else (g.top + 10, g.bot)
    total = sum(p * n for p, n in zip(sizes, nls))
    if total > y1 - y0:
        k = (y1 - y0) / total
        sizes = [round(p * k) for p in sizes]
        total = sum(p * n for p, n in zip(sizes, nls))
    gap = (y1 - y0 - total) / max(len(rows) - 1, 1)
    body, y = "", y0
    for j, ((r, _), px, nl) in enumerate(zip(rows, sizes, nls)):
        inner = X.rich(r)
        if strike and strike in r and "|" not in r:
            inner = X.rich(r).replace(X.rich(strike), f'<span class="sk" style="position:relative; display:inline-block">{X.rich(strike)}'
                                      f'<i class="bar" style="left:-3%; right:-3%; top:44%; height:.16em"></i></span>', 1)
        body += f'<div class="zh r{j}" style="{st(left=g.m - round(px * 0.04), top=round(y), font_size=px)}">{inner}</div>'
        y += px * nl + gap
    page(X, cid, t, d, "ink", furn, grid, wipe, body)
    s = f"#{cid}"
    for j in range(len(rows)):
        wipe_in(X, f"{s} .zh.r{j}", t + 0.22 + 0.09 * j)
    X.tw(f'tl.from("{s} .bar", {{scaleX:0, duration:0.45, ease:"expo.out"}}, {tk - 0.08:.3f});')
    X.sfx(tk, "slam")


def quote(b, X, t, d, cid):
    """(c) vertical: the quote turned 90° runs the full height of the left five columns, the year and the speaker
    sit as a small block on the right; the last words land in blue on their cue."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "paper", src=b.get("src"))
    tq, tn = T(X, b, "at_quote", t, t + d * 0.55), T(X, b, "at_no", t, t + d * 0.85)
    who, wsub = b.get("who", "乔布斯 · 苹果开发者大会"), b.get("who_sub", "WWDC CLOSING CHAT · 13 MAY 1997")
    yr = str(b.get("year", "1997"))
    l1 = bare(b.get("q1", "专注，")) + bare(b.get("q2", "就是学会"))
    l2 = bare(b.get("q3", "说不。"))
    en = b.get("en", "")
    X.css("po-quote", ".po .rot { position:absolute; transform-origin:0 0; transform:rotate(-90deg); } .po .rot .zh { position:absolute; left:0; }")
    if g.v:
        y0r = g.bot - 40                               # the turned lines run up from here
        L = y0r - g.top
        p1, l1, n1 = zfit(l1, L, 200, 100, 2)
        p2, l2, n2 = zfit(l2, L, min(p1, 200), 90, 2)
        bw = p1 * n1 + p2 * n2
        if bw > 440:                                   # the turned block keeps to the left columns
            k = 440 / bw
            p1, p2 = round(p1 * k), round(p2 * k)
            bw = p1 * n1 + p2 * n2
        rot = (f'<div class="rot" data-layout-allow-overlap style="{st(left=g.m - round(p1 * 0.06), top=y0r, width=L, height=bw)}">'
               + zh(X, l1, 0, 0, p1, "q1") + zh(X, l2, 0, p1 * n1, p2, "acc q2") + '</div>')
        rx = g.m + bw + 24                             # the year block runs from the turned lines to the right margin
        rw = g.tr + 30 - rx                            # the year's ink keeps clear of the platform buttons too
        tw_ = g.tr - rx
        enf = fit.fit_text(fit.as_text(en, " "), tw_, 56 * 1.12 * 3, 56, 30, lh=1.12, max_lines=3) if en else None
        wpx, who_t, wn = zfit(who, tw_, 40, 26, 2)
        wsf = fit.fit_text(fit.as_text(wsub, " "), tw_, 28 * 1.2 * 2, 28, 24, lh=1.2, max_lines=2) if wsub else None
        side_h = (enf.px * 1.12 * len(enf.lines) + 28 if enf else 0) + wpx * 1.12 * wn + 10 + (wsf.px * 1.2 * len(wsf.lines) if wsf else 0)
        digits = yr.isdigit() and len(yr) >= 4
        half = [yr[:len(yr) // 2], yr[len(yr) // 2:]] if digits else [yr]
        gap = 20
        if digits:
            f = min(660, rw * 1.05 / (0.4025 * len(max(half, key=len))))     # .4025 em: measured advance of one figure (wdth 62, -.03em)
        else:
            f = min(560, tw_ / numw(yr))              # a label, not a year: fits the text width
        room = g.bot - g.top - side_h - 24 - gap * len(half)
        f = max(120, min(f, room / (NUM_H * len(half))))
        yrs = "".join(num(X, h, rx, g.top + k * (NUM_H * f + gap), f, f"yr y{k}") for k, h in enumerate(half))
        by = g.top + len(half) * (NUM_H * f + gap) + 24
        side = ""
        if enf:
            side += f'<div class="la en" style="{st(left=rx, top=round(by), font_size=enf.px, width=tw_)}; line-height:1.12">{"<br>".join(X.rich(l) for l in enf.lines)}</div>'
            by += enf.px * 1.12 * len(enf.lines) + 28
        side += f'<div class="tx who" style="{st(left=rx, top=round(by), font_size=round(wpx))}">{X.rich(who_t)}</div>'
        by += wpx * 1.12 * wn + 10
        if wsf:
            side += f'<div class="la wsub" style="{st(left=rx, top=round(by), font_size=wsf.px, width=tw_)}; line-height:1.2">{"<br>".join(X.rich(l) for l in wsf.lines)}</div>'
        body = rot + yrs + side
    else:
        lw = g.w(5) - 40
        f = min(560, lw * 0.92 / numw(yr))
        yrs = num(X, yr, g.m, g.top + 10, f, "yr y0")
        by = g.top + 10 + NUM_H * f + 50
        wpx, who_t, wn = zfit(who, lw, 40, 24, 2)
        wsf = fit.fit_text(fit.as_text(wsub, " "), lw, 28 * 1.2, 28, 22, lh=1.2, max_lines=1) if wsub else None
        side = f'<div class="tx who" style="{st(left=g.m, top=round(by), font_size=round(wpx))}">{X.rich(who_t)}</div>'
        by += wpx * 1.12 * wn + 10
        if wsf:
            side += f'<div class="la wsub" style="{st(left=g.m, top=round(by), font_size=wsf.px, width=lw)}; white-space:nowrap">{X.rich(wsf.lines[0])}</div>'
            by += wsf.px * 1.2 + 30
        enf = fit.fit_text(fit.as_text(en, " "), lw, max(60, g.bot - by), 36, 22, lh=1.15, max_lines=4) if en else None
        if enf:
            side += f'<div class="la en" style="{st(left=g.m, top=round(by), font_size=enf.px, width=lw)}">{"<br>".join(X.rich(l) for l in enf.lines)}</div>'
        qx = g.x(5) + 44
        qw = g.R - qx
        p2, l2, n2 = zfit(l2, qw, 260, 100, 2)
        p1, l1, n1 = zfit(l1, qw, 170, 70, 2)
        body = (yrs + side + f'<i class="bar vr" style="{st(left=g.x(5) - 4, top=g.top, width=6, height=g.bot - g.top)}; transform-origin:50% 0"></i>'
                + zh(X, l1, qx, g.top + 20, p1, "q1") + zh(X, l2, qx, g.bot - p2 * n2, p2, "acc q2"))
    page(X, cid, t, d, "paper", furn, grid, wipe, body)
    s = f"#{cid}"
    # the side block builds on the narration: year, then the speaker, then the occasion, then the original line
    tw_, tm_ = T(X, b, "at_who", t, t + 0.6), T(X, b, "at_meta", t, t + 0.9)
    te_ = T(X, b, "at_en", t, min(tq - 0.5, tm_ + 0.8))
    wipe_in(X, f"{s} .yr", t + 0.1, stg=0.35)
    hide_until(X, f"{s} .who", t, tw_ - 0.1)
    hide_until(X, f"{s} .wsub", t, tm_ - 0.1)
    if en: hide_until(X, f"{s} .en", t, te_)
    if not g.v: X.tw(f'tl.from("{s} .vr", {{scaleY:0, duration:0.6, ease:"expo.out"}}, {t + 0.2:.3f});')
    hide_until(X, f"{s} .q1", t, tq - 0.12)
    hide_until(X, f"{s} .q2", t, tn - 0.1)
    X.sfx(tq, "click")
    X.sfx(tn, "hit")


def price(b, X, t, d, cid):
    """(d) the split: ink above, paper below. The two words start level on the line, half in each colour; on 便宜
    generation drops through the line into the paper, on 变贵 judgment rises into the ink and turns blue."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "paper")
    tl_, tr_ = T(X, b, "at_low", t, t + 0.8), T(X, b, "at_high", t, t + 2.0)
    lw, rw = (list(fit.as_list(b.get("left", ["生成", "变便宜"]))) + ["", ""])[:2], (list(fit.as_list(b.get("right", ["判断", "变贵"]))) + ["", ""])[:2]
    lw, rw = [bare(x) for x in lw], [bare(x) for x in rw]
    X.css("po-price", """
.po .half { position:absolute; inset:0; }
.po .half.top { clip-path:inset(0 0 calc(100% - var(--split)) 0); color:#f2f2ef; }
.po .half.bot { clip-path:inset(var(--split) 0 0 0); color:#0a0a0a; }
.po .half.top .jd { color:#1f3bff; }
.po .inkp { position:absolute; left:0; right:0; top:0; background:#0a0a0a; transform-origin:50% 0; }
""")
    sp = g.H // 2
    cw = g.w(6) - 10
    px = min(zpx(lw[0], cw, 260), zpx(rw[0], cw, 260))
    lab = min(64, (g.w(6) - 20) / max(zhw(lw[1]), zhw(rw[1]), 1))
    gx, jx = g.m, g.x(6)
    lvl = sp - px // 2                                  # level: both words straddle the line
    jy0 = lvl
    if g.v:
        # 9:16: the pair fills the diagonal. generation starts across the line and sinks to the lower left;
        # judgment rises from under the page to the upper right. Both at ~300 px glyphs.
        px = min(zpx(lw[0], g.w(12) * 0.68, 340), zpx(rw[0], g.w(12) * 0.68, 340))
        lvl = sp - px // 2
        jx = g.R - round(px * zhw(rw[0]))
        jy0 = g.H + 40
        gy1, jy1 = g.bot - px, g.top + 20
        glab = (g.m, gy1 - lab * 1.35)
        jlab = (g.R - lab * zhw(rw[1]), jy1 + px + 20)
    else:
        # 16:9: judgment right-aligned on the margin; each label sits on the far side of its word from the split
        jx = g.R - round(px * zhw(rw[0]))
        gy1, jy1 = g.bot - px, g.top + 20
        gend = gx + round(px * zhw(lw[0])) + 30
        glab = (gend, gy1 + px - lab * 1.05) if gend + lab * zhw(lw[1]) <= g.R else (gx, gy1 - lab * 1.35)
        jlab = (g.R - lab * zhw(rw[1]), jy1 + px + 16)
    def layer(cls):
        return (f'<div class="half {cls}" data-layout-allow-overlap>'
                + zh(X, lw[0], gx - round(px * 0.04), lvl, px, "gen")
                + zh(X, rw[0], jx - round(px * 0.04), jy0, px, "jd")
                + f'<div class="tx glab" style="{st(left=round(glab[0]), top=round(glab[1]), font_size=round(lab))}">{X.rich(lw[1])}</div>'
                + f'<div class="tx jlab" style="{st(left=round(jlab[0]), top=round(jlab[1]), font_size=round(lab))}">{X.rich(rw[1])}</div>'
                + '</div>')
    body = (f'<div class="inkp" style="{st(height=sp)}"></div>' + layer("top") + layer("bot"))
    X.css(f"po-price-split-{sp}", f".po .half {{ --split:{sp}px; }}")
    page(X, cid, t, d, "paper", furn, grid, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .inkp", {{scaleY:0, duration:0.45, ease:"expo.out"}}, {t + 0.02:.3f});')
    wipe_in(X, f"{s} .gen" if g.v else f"{s} .gen, {s} .jd", t + 0.18, stg=0.08)
    X.tw(f'tl.set("{s} .glab, {s} .jlab", {{clipPath:"inset(100% 0% 0% 0%)"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .gen", {{y:{gy1 - lvl}, duration:0.5, ease:"expo.inOut"}}, {tl_ - 0.25:.3f});')
    wipe_in(X, f"{s} .glab", tl_ + 0.15)
    X.tw(f'tl.to("{s} .jd", {{y:{jy1 - jy0}, duration:{0.55 if g.v else 0.5}, ease:"expo.inOut"}}, {tr_ - 0.3:.3f});')
    if g.v:      # 9:16: judgment waits under the page edge before it rises; only its risen state is text to read
        X.tw(f'tl.set("{s} .jd", {{attr:{{"data-safe":"ignore"}}}}, {t:.3f});')
        X.tw(f'tl.set("{s} .jd", {{attr:{{"data-safe":"read"}}}}, {tr_ + 0.25:.3f});')
    wipe_in(X, f"{s} .jlab", tr_ + 0.15)
    X.sfx(tl_, "click"); X.sfx(tr_, "hit")


def keep(b, X, t, d, cid):
    """(e) the grid shows: 24 frames sit in the 12 columns, the count above them; on 扔掉 all but one fall out of the
    page and the count runs down to 1; on 才重要 the kept frame snaps across four columns."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "paper", grid=True, index=True)
    tm, tt, tk = T(X, b, "at_make", t, t + 0.4), T(X, b, "at_toss", t, t + d * 0.55), T(X, b, "at_keep", t, t + d * 0.85)
    a1 = [bare(x) for x in (list(fit.as_list(b.get("a", ["做出", "多少张图", "不重要"]))) + ["", "", ""])[:3]]
    a2 = [bare(x) for x in (list(fit.as_list(b.get("b", ["扔掉", "多少张", "才重要"]))) + ["", "", ""])[:3]]
    X.css("po-keep", """
.po .fr { position:absolute; background:#0a0a0a; }
.po .fr.k { background:#1f3bff; }
""")
    nf = max(2, min(int(b.get("frames", 24)), 36))
    cols = min(12, nf)
    rows = -(-nf // cols)
    kk = min(int(b.get("keep_i", 13)), nf - 1)
    if g.v:
        sy, f, ny = 250, 0, 0
        small_w = g.tw
        f = min(780, g.w(9) / numw(str(nf)))
        ny = 350
        bigx, bigy, bigw = g.m, ny + NUM_H * f + 50, g.tw
        fy, fh = 1130, 196          # the frames end above the caption (1392); the column numbers sit right under them
    else:
        sy = g.top + 20
        small_w = g.w(6)
        f = min(760, g.w(6) / numw(str(nf)))
        ny = g.top + 10
        bigx, bigy, bigw = g.x(6), 0, g.w(6)
        fy, fh = 668, 172
    cell_h = (fh - (rows - 1) * g.g) / rows
    cells = ""
    for k in range(nf):
        r, c = divmod(k, cols)
        cells += f'<i class="fr f{k}{" k" if k == kk else ""}" style="{st(left=g.x(c), top=round(fy + r * (cell_h + g.g)), width=round(g.cw), height=round(cell_h))}"></i>'
    s1 = a1[0] + a1[1]
    s2 = a2[0] + a2[1]
    sp1, s1, sn1 = zfit(s1, small_w, 64, 36, 2)
    sp2, s2, sn2 = zfit(s2, small_w, 64, 36, 2)
    spx = min(sp1, sp2)
    sn = max(sn1, sn2)
    b1 = zfit(a1[2], bigw, 260, 100, 2)
    b2 = zfit(a2[2], bigw, 260, 100, 2)
    bpx = min(b1[0], b2[0])
    bn = max(b1[2], b2[2])
    a1[2], a2[2] = b1[1], b2[1]
    if not g.v:
        sx = g.x(6)
        bigy = sy + spx * 1.12 * sn + 70
    else:
        sx = g.m
        if sn > 1:
            ny += spx * 1.12 * (sn - 1)
        f = min(f, (fy - 30 - bpx * bn - 50 - ny) / NUM_H)      # the count gives way so the verdict clears the frames
        bigy = ny + NUM_H * f + 50
    body = (f'<div class="tx sA" style="{st(left=sx, top=sy, font_size=spx)}">{X.rich(s1)}</div>'
            f'<div class="tx sB" style="{st(left=sx, top=sy, font_size=spx)}">{X.rich(s2)}</div>'
            + num(X, str(nf), g.m, ny, f, "cnt", f'<span class="cv">{nf}</span>')
            + zh(X, a1[2], bigx - round(bpx * 0.04), bigy, bpx, "bA")
            + zh(X, a2[2], bigx - round(bpx * 0.04), bigy, bpx, "acc bB")
            + cells)
    page(X, cid, t, d, "paper", furn, grid, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.set("{s} .sB, {s} .bB", {{clipPath:"inset(100% 0% 0% 0%)"}}, {t:.3f});')
    wipe_in(X, f"{s} .sA", t + 0.12)
    wipe_in(X, f"{s} .nm", t + 0.15)
    wipe_in(X, f"{s} .bA", t + 0.3)
    tf = min(tm, t + 0.25)
    X.tw(f'tl.from("{s} .fr", {{scaleY:0, transformOrigin:"50% 100%", duration:0.3, ease:"expo.out", stagger:{{each:{min(0.03, 0.7 / nf):.3f}, from:"start"}}}}, {tf:.3f});')
    counter(X, f"{s} .cv", tf, 0, nf, dur=0.8)
    X.sfx(tf, "count")
    # toss: the words swap, every frame but one falls out of the bottom of the page, the count runs down
    wipe_out(X, f"{s} .sA, {s} .bA", tt - 0.3)
    wipe_in(X, f"{s} .sB", tt)
    X.tw(f'tl.to("{s} .fr:not(.k)", {{y:{g.H - fy + 40}, duration:0.55, ease:"power3.in", stagger:{{each:0.02, from:"edges"}}}}, {tt + 0.05:.3f});')
    counter(X, f"{s} .cv", tt + 0.05, nf, 1, dur=0.9)
    X.sfx(tt + 0.1, "wipe")
    # keep: the frame snaps across four columns and both rows; the count and the verdict go blue
    kc = kk % cols
    c0 = min(kc, 12 - 4)
    kr = kk // cols
    ky = fy + kr * (cell_h + g.g)
    X.tw(f'tl.to("{s} .fr.k", {{x:{g.x(c0) - g.x(kc)}, y:{fy - ky:.1f}, scaleX:{g.w(4) / g.cw:.4f}, scaleY:{fh / cell_h:.4f}, transformOrigin:"0 0", duration:0.45, ease:"expo.out"}}, {tk - 0.08:.3f});')
    X.tw(f'tl.set("{s} .cnt", {{color:"#1f3bff"}}, {tk - 0.08:.3f});')
    wipe_in(X, f"{s} .bB", tk - 0.1)
    X.sfx(tk, "hit")


def thesis(b, X, t, d, cid):
    """(b) on blue: the verdict word in paper at the top, the rest in ink; the last line anchors the bottom on a rule."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "blue")
    te = T(X, b, "at_rest", t, t + d * 0.45)
    big = bare(fit.plain(b.get("big", "选择")))
    rest = [bare(r) for r in fit.as_list(b.get("rest", "才是|新的创作"))]
    if not g.v: rest = ["".join(rest)]
    bpx, big, bn = zfit(big, g.tw, 260, 120, 2)
    body = zh(X, big, g.m - round(bpx * 0.04), 260 if g.v else g.top + 10, bpx, "bg1")
    y = (260 if g.v else g.top + 10) + bpx * bn + 20
    for j, r in enumerate(rest):
        px, r, rn = zfit(r, g.tw, 260, 100 if g.v else 80, 2)
        last = j == len(rest) - 1
        yy = (g.bot - px * rn) if last else y
        if last:
            body += f'<i class="rl r3" style="{st(left=g.m, top=round(yy - (60 if g.v else 44)), width=g.W - 2 * g.m)}; background:#0a0a0a"></i>'
        body += zh(X, r, g.m - round(px * 0.04), yy, px, f"ink rs r{j}")
        y += px * rn + 20
    page(X, cid, t, d, "blue", furn, grid, wipe, body)
    s = f"#{cid}"
    wipe_in(X, f"{s} .bg1", t + 0.12, 0.45)
    X.tw(f'tl.set("{s} .rs", {{clipPath:"inset(100% 0% 0% 0%)"}}, {t:.3f});')
    wipe_in(X, f"{s} .rs", te - 0.15, stg=0.12)
    draw(X, f"{s} .r3", te - 0.2, 0.5)
    X.sfx(t + 0.12, "slam")


def outro(b, X, t, d, cid):
    """the last page: the grid slides open, FIN at full width, the show's name under it."""
    g, furn, grid, wipe = frame(X, b, t, d, cid, "paper", grid=True)
    nm = str(b.get("nm", "FIN"))
    title = b.get("title", X.channel)
    if g.v:
        f = min(845, (g.W - g.m) * 1.08 / numw(nm))
        ny = 300
        tpx, title, tn = zfit(title, g.tw, 200, 80, 2)
        ty = ny + NUM_H * f + 90
        tx_ = g.m
    else:
        f = min(800, g.w(8) / numw(nm))
        ny = g.top + 10
        tx_ = g.x(8)
        tpx, title, tn = zfit(title, g.R - tx_, 140, 56, 2)
        ty = ny + NUM_H * f - tpx * tn
    sub, mo = b.get("sub", ""), b.get("mo", "")
    body = num(X, nm, g.m, ny, f, "fin") + zh(X, title, tx_ - round(tpx * 0.04), ty, tpx, "ttl")
    yy = ty + tpx * tn + 30
    if sub:
        sp_, sub, sn = zfit(sub, g.tr - tx_, 48, 30, 2)
        body += f'<div class="tx sub" style="{st(left=tx_, top=round(yy), font_size=sp_)}">{X.rich(sub)}</div>'
        yy += sp_ * 1.12 * sn + 12
    if mo:
        mpx, mo, _ = zfit(mo, g.tr - tx_, 40, 26, 1)
        body += f'<div class="tx acc mo" style="{st(left=tx_, top=round(yy), font_size=mpx)}">{X.rich(mo)}</div>'
    page(X, cid, t, d, "paper", furn, grid, wipe, body)
    s = f"#{cid}"
    wipe_in(X, f"{s} .fin", t + 0.1, 0.45)
    wipe_in(X, f"{s} .ttl", t + 0.35)
    wipe_in(X, f"{s} .sub, {s} .mo", t + 0.55, stg=0.1)
    X.sfx(t + 0.35, "hit")


# ---------------------------------------------------------------- the page around a library effect
FX_CSS = r"""
.pf .pf-grid i { position:absolute; width:2px; background:var(--fg); opacity:.08; }
.pf .pf-rl, .pf .pf-sg { position:absolute; height:6px; transform-origin:0 50%; } .pf .pf-rl { background:var(--fg); } .pf .pf-sg { background:var(--pc-bar, var(--accent)); }
.pf .pf-fo { position:absolute; font-family:var(--f-num); font-variation-settings:"wdth" 75, "wght" 900; line-height:1; color:var(--fg); white-space:nowrap; }
.pf .pf-fo span { color:#8d8d88; }
.pf .pf-cap { position:absolute; }
.pf .pf-cap .tx { position:relative; display:inline-block; color:var(--pc-fg, var(--fg)); font-family:var(--f-body); font-weight:700; line-height:1.25; text-align:left; }
.pf .pf-cap .tx::before { content:""; position:absolute; left:-20px; top:.14em; bottom:.1em; width:6px; background:var(--pc-bar, var(--accent)); }
.pf .pf-cap .em .emt { color:var(--pc-em, var(--accent)); font-weight:900; } .pf .pf-cap .em .emb { display:none; }
.pf .pf-ft { position:absolute; display:flex; justify-content:space-between; gap:32px; font-family:var(--f-latin), var(--f-body); font-weight:600; font-size:24px; color:var(--fg); }
.pf .pf-ft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; } .pf .pf-ft > div:last-child { text-align:right; }
.pf .pf-wipe i { position:absolute; top:0; bottom:0; transform-origin:50% 100%; }
.pf.photo .pf-fo, .pf.photo .pf-ft, .pf.photo .pf-cap .tx { color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.55); }
.pf.photo .pf-rl { background:#fff; } .pf.photo .pf-grid { display:none; }
.pf.photo .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.4), rgba(0,0,0,0) 18%, rgba(0,0,0,0) 62%, rgba(0,0,0,.7)); }
"""


def FX_FRAME(X, cid, t, d, p, parts):
    """a library effect set as a poster page: faint column lines, the spoken line flush left with the 6 px bar (no box),
    and the poster's bottom furniture: the 6 px rule with this page's slot, the folio, the label and source.
    Pages open with the column wipe only when the ground changes."""
    from h9 import aefx
    X.css("po-fx", FX_CSS)
    g = G(X)
    i, n = X.beat["i"], X.beat["n"]
    v, photo = g.v, parts["photo"]
    cols = "".join(f'<i style="left:{(g.x(c) if c < 12 else g.R) - 1}px; top:{g.top - 20}px; height:{g.rule - g.top - 20}px"></i>' for c in range(13))
    X.used_text.update(f"{i + 1:02d}{n:02d}/ ")
    seg_w = (g.W - 2 * g.m) / max(n, 1)
    fy = g.rule + (22 if v else 16)
    furn = (f'<i class="pf-rl" style="left:{g.m}px; right:{g.m}px; top:{g.rule}px"></i>'
            f'<i class="pf-sg" style="left:{round(g.m + seg_w * i)}px; width:{round(seg_w)}px; top:{g.rule}px"></i>'
            f'<div class="pf-fo" style="left:{g.m}px; top:{fy}px; font-size:44px">{i + 1:02d}<span> / {n:02d}</span></div>')
    px = max(34, min(44, parts["cap_px"]))
    maxw = (g.W - g.m - 120) if v else (g.W - 2 * g.m - (430 if p.get("host") else 0))
    pos = f"left:{g.m}px; top:{1392 if v else 872}px"      # 9:16: same band as the film's caption, above the platform's bottom bar
    cap = f'<div class="pf-cap" style="{pos}"><div class="tx" style="font-size:{px}px; max-width:{maxw}px">{parts["cap"]}</div></div>'
    ft = (f'<div class="pf-ft" style="left:{g.m + 230 if not v else g.m}px; right:{120 if v else g.m}px; top:{1462 if v else fy + 2}px"><div>{parts["foot"]}</div><div>{parts["src"]}</div></div>'
          if parts["foot"] or parts["src"] else "")
    th = aefx.THEMES.get(p.get("theme")) or {}
    bg = th.get("bg", X.S["tokens"]["bg"])
    prev = getattr(X, "_pf_prev", None)
    wipe = ""
    if prev and abs(prev[1] - t) < 0.05 and prev[0] != bg:
        wipe = '<div class="pf-wipe">' + "".join(f'<i style="left:{g.x(c) - g.g // 2 - 1 if c else 0}px; width:{round(g.cw + g.g) + 2 + (g.m if c in (0, 11) else 0)}px; background:{prev[0]}"></i>' for c in range(12)) + "</div>"
    X._pf_prev = (bg, t + d)
    inner = ('<div class="scrim"></div>' if photo else "") + f'<div class="pf-grid">{cols}</div>{wipe}{furn}{cap}{ft}'
    X.clip(f"{cid}c", t, d, inner, f"ctx pf{' photo' if photo else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    if wipe:
        X.tw(f'tl.to("{s} .pf-wipe i", {{scaleY:0, duration:0.3, ease:"power3.inOut", stagger:0.012}}, {t:.3f});')
    X.tw(f'tl.from("{s} .pf-grid i", {{x:(k, el)=>{g.m} - parseFloat(el.style.left), duration:0.6, ease:"expo.out", stagger:0.015}}, {t:.3f});')
    X.tw(f'tl.from("{s} .pf-rl", {{scaleX:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .pf-sg", {{scaleX:0, duration:0.45, ease:"expo.out"}}, {t + 0.25:.3f});')
    for sel, dt in ((".pf-fo", 0.1), (".pf-cap .tx", 0.16), (".pf-ft", 0.2)):
        X.tw(f'tl.fromTo("{s} {sel}", {{clipPath:"inset(100% 0% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.45, ease:"expo.out"}}, {t + dt:.3f});')


SCENES = {"hundred": hundred, "problem": problem, "quote": quote, "price": price, "keep": keep, "thesis": thesis, "outro": outro}
