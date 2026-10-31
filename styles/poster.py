"""poster · 瑞士海报 —— 国际主义字体排印（Müller-Brockmann 的网格、Experimental Jetset / Pentagram 的动态识别）做观点口播。
冷白与墨黑两种页面、一个信号蓝；12 栏网格在转折处显形；超大 Archivo 数字 + 思源黑体 900；每一句话网格重排一次。
转场是"栏条"：12 根栏条错落收起，露出下一页。没有照片，只有字、线、格。

场景（SCENES，全部自写）：hundred 一百个答案 · problem 问题反转 · quote 引语（年份 + 中英原文 + 出处）·
price 生成与判断的跷跷板 · keep 做出多少 / 扔掉多少 · thesis 判断句 · outro 落版。横屏竖屏各自排版。
"""

STYLE = {
    "name": "瑞士海报", "en": "Poster", "benchmarks": ["Josef Müller-Brockmann", "Experimental Jetset", "Pentagram motion identities"],
    "tokens": {
        "bg": "#f2f2ef", "fg": "#0a0a0a", "muted": "#8d8d88", "accent": "#1f3bff", "accent2": "#1f3bff", "alert": "#1f3bff",
        "line": "#d6d6d1", "paper": "#f2f2ef", "ink": "#0a0a0a", "card": "#ffffff", "card-fg": "#0a0a0a", "blue": "#1f3bff",
        "cap-bg": "#0a0a0a", "cap-fg": "#f2f2ef", "cap-size": "34px", "cap-weight": "700", "cap-pad": "8px 18px 10px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "40px", "cap-em": "#7f93ff",
    },
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "num": "archivo", "latin": "inter", "mono": "jetbrains-mono"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.035})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 96, "bottom": 60, "h": 360}, "portrait": {"right": 70, "bottom": 560, "h": 300}},
    "sfx": {"enter": ("whoosh_soft", 0.25), "pop": ("tick", 0.4), "hit": ("hit", 0.4), "slam": ("slam", 0.4), "count": ("type", 0.25),
            "click": ("click", 0.3), "mascot": ("whoosh_soft", 0.25), "wipe": ("whoosh", 0.25), "line": ("click", 0.3)},
    "css": """
.st-poster .cap { text-align:left; left:80px; right:80px; }
#root.v.st-poster .cap { left:56px; right:56px; bottom:540px; }
.st-poster .cap .cp { letter-spacing:.01em; }
""",
}

CSS = r"""
.st-poster .em .emb { display:none; }
.po { position:absolute; inset:0; overflow:hidden; }
.po .cam { position:absolute; inset:0; }
.po.dark { background:var(--ink); color:var(--paper); }
.po.light { background:var(--paper); color:var(--ink); }
/* the grid: 12 hairlines, drawn in when a page wants to show its structure */
.po .grid i { position:absolute; top:0; bottom:0; width:1px; background:currentColor; opacity:.13; transform-origin:50% 0; }
.po .grid b { position:absolute; left:0; right:0; height:1px; background:currentColor; opacity:.1; transform-origin:0 50%; }
/* furniture */
.po .hd { position:absolute; display:flex; justify-content:space-between; align-items:flex-end; font-family:var(--f-latin); font-weight:700; letter-spacing:.02em; z-index:6; }
.po .hd .l b { font-family:var(--f-display); font-weight:900; margin-right:14px; }
.po .hd .l span, .po .hd .r span { opacity:.55; font-weight:500; }
.po .hd .r { font-family:var(--f-num); font-variation-settings:"wdth" 100, "wght" 700; font-variant-numeric:tabular-nums; }
.po .hd .r em { font-style:normal; color:var(--blue); }
.po .hr { position:absolute; height:3px; background:currentColor; transform-origin:0 50%; z-index:6; }
.po .prog { position:absolute; height:3px; background:var(--blue); transform-origin:0 50%; z-index:7; }
.po .ft { position:absolute; font-family:var(--f-mono); letter-spacing:.04em; opacity:.6; z-index:6; white-space:nowrap; }
/* type */
.po .zh { position:absolute; font-family:var(--f-display); font-weight:900; line-height:.98; letter-spacing:-.035em; white-space:nowrap; }
.po .zh.m { font-weight:700; letter-spacing:-.01em; line-height:1.18; }
.po .nm { position:absolute; font-family:var(--f-num); font-variation-settings:"wdth" 72, "wght" 900; line-height:.78; letter-spacing:-.03em; font-variant-numeric:tabular-nums; white-space:nowrap; }
.po .la { position:absolute; font-family:var(--f-latin); font-weight:600; letter-spacing:.01em; white-space:nowrap; }
.po .mo { position:absolute; font-family:var(--f-mono); letter-spacing:.06em; white-space:nowrap; }
.po .blue { color:var(--blue); }
.po .out { color:rgba(10,10,10,.09); -webkit-text-stroke:3px currentColor; }
.po.dark .out { color:rgba(242,242,239,.09); -webkit-text-stroke:3px var(--paper); }
.po .ln { display:block; overflow:hidden; padding-bottom:.04em; } .po .ln > span { display:inline-block; }
.po .rule { position:absolute; height:3px; background:currentColor; transform-origin:0 50%; }
.po .vrule { position:absolute; width:3px; background:currentColor; transform-origin:50% 0; }
.po .blk { position:absolute; background:var(--blue); transform-origin:0 50%; }
/* the column wipe that opens every page */
.po .wipe { position:absolute; inset:0; z-index:20; pointer-events:none; }
.po .wipe i { position:absolute; top:0; bottom:0; transform-origin:50% 0; }
"""


# ---------------------------------------------------------------- grid geometry
class G:
    """12-column grid in px for the current canvas."""
    def __init__(self, X):
        self.v = X.portrait
        self.W, self.H = X.W, X.H
        self.m = 56 if self.v else 80
        self.g = 12 if self.v else 20
        self.cw = (self.W - 2 * self.m - 11 * self.g) / 12
        self.top = 236 if self.v else 112           # first content line under the header
        self.bot = 1250 if self.v else 960          # last content line above captions

    def x(self, c): return round(self.m + c * (self.cw + self.g))
    def w(self, n): return round(n * self.cw + (n - 1) * self.g)


from h9 import fit


def numw(txt):
    """em width of figures in Archivo at wdth 72."""
    return sum(0.48 if c.isdigit() else 0.24 if c in ".,:" else 0.7 if c == "%" else 0.38 if c in "-+" else fit.gw(c) * 0.85 for c in str(txt)) or 1


def fz(X, text, w, max_px, min_px=None, lines=2, h=None, lh=1.0):
    """fit `text` into a column: (px, line-masked html). Keeps explicit | breaks, adds balanced ones when needed."""
    f = fit.fit_text(fit.as_text(text), w, h or max_px * lh * lines, max_px, min_px or max_px * 0.35, lh=lh, max_lines=lines)
    return f.px, "".join(f'<span class="ln"><span>{X.rich(l)}</span></span>' for l in f.lines), f


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def frame(X, b, t, d, cid, dark=False, grid_at=None, src=None, rows=False):
    """page furniture: header with index, progress rule, optional footnote, the 12-column grid, the opening column wipe."""
    X.css("poster", CSS)
    g = G(X)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    hd_top, fs = (150, 24) if g.v else (34, 20)
    sec = meta.get("section", "判断")
    X.used_text.update(sec + "0123456789/—")
    hd = (f'<div class="hd" style="left:{g.m}px; right:{g.m}px; top:{hd_top}px; font-size:{fs}px">'
          f'<div class="l"><b>第九顶帽子</b><span>HAT 9 · {X.rich(sec)}</span></div>'
          f'<div class="r"><em>{i + 1:02d}</em><span> / {n:02d}</span></div></div>'
          f'<i class="hr" style="left:{g.m}px; right:{g.m}px; top:{hd_top + fs + 14}px"></i>')
    D = X.duration or 30
    prog = f'<i class="prog" style="left:{g.m}px; top:{hd_top + fs + 14}px; width:{g.W - 2 * g.m}px"></i>'
    lines = "".join(f'<i style="left:{g.x(c) - 1 if c < 12 else g.x(11) + g.w(1)}px"></i>' for c in range(13))
    hl = "".join(f'<b style="top:{y}px"></b>' for y in range(g.top, g.bot + 1, 120)) if rows else ""
    grid = f'<div class="grid">{lines}{hl}</div>'
    ft = ""
    if src or b.get("src"):
        fy = 1478 if g.v else 1040
        ft = f'<div class="ft" style="left:{g.m}px; top:{fy}px; font-size:{16 if not g.v else 18}px">{X.rich(src or b["src"])}</div>'
    # wipe: 12 strips in the previous page's colour retract from the top, one column after another
    prev = getattr(X, "_po_prev", None)
    wipe = ""
    if prev is not None:
        col = "var(--blue)" if prev == dark else ("var(--ink)" if prev else "var(--paper)")   # same-colour pages wipe in blue
        strips = "".join(f'<i style="left:{g.x(c) - g.g // 2 - 1}px; width:{round(g.cw + g.g) + 2}px; background:{col}"></i>' for c in range(12))
        wipe = f'<div class="wipe">{strips}</div>'
    X._po_prev = dark
    X._po_grid_t = grid_at
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .prog", {{scaleX:{t / D:.4f}}}, {{scaleX:{(t + d) / D:.4f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if wipe:
        X.tw(f'tl.to("{s} .wipe i", {{scaleY:0, duration:0.42, ease:"power4.inOut", stagger:{{each:0.025, from:"start"}}}}, {t:.3f});')
        X.sfx(t, "wipe")
    if grid_at is not None:
        X.tw(f'tl.from("{s} .grid i", {{scaleY:0, duration:0.6, ease:"expo.out", stagger:0.02}}, {grid_at:.3f});')
        if rows: X.tw(f'tl.from("{s} .grid b", {{scaleX:0, duration:0.6, ease:"expo.out", stagger:0.03}}, {grid_at + 0.1:.3f});')
    else:
        X.tw(f'tl.set("{s} .grid", {{opacity:0}}, {t:.3f});')
    return grid, hd + prog + ft, wipe, g


def page(X, cid, t, d, dark, grid, furn, wipe, body):
    X.clip(cid, t, d, f'<div class="po {"dark" if dark else "light"}"><div class="cam">{grid}{body}</div>{furn}{wipe}</div>', "scene", 2)
    # continuous creep so no frame is dead; the grid itself stays put relative to the page
    X.tw(f'tl.fromTo("#{cid} .cam", {{scale:1}}, {{scale:1.025, duration:{d:.2f}, ease:"none", transformOrigin:"50% 50%"}}, {t:.3f});')


def lines(X, text, cls=""):
    return "".join(f'<span class="ln {cls}"><span>{X.rich(p)}</span></span>' for p in str(text).split("|"))


def lift(X, sel, t, dur=0.6, st=0.07):
    X.tw(f'tl.from("{sel}", {{yPercent:105, duration:{dur}, ease:"expo.out", stagger:{st}}}, {t:.3f});')


def counter(X, sel, t, a, b, dur=1.0, pad=0):
    js = f"String(Math.round(o.v)).padStart({pad}, '0')" if pad else "String(Math.round(o.v))"
    X.used_text.update("0123456789")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power2.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def st(**k):
    return "; ".join(f"{a.replace('_', '-')}:{v}px" if isinstance(v, (int, float)) else f"{a.replace('_', '-')}:{v}" for a, v in k.items())


# ---------------------------------------------------------------- scenes
def hundred(b, X, t, d, cid):
    """一百个答案: the headline stacks on the left five columns, a 10×10 answer matrix fills the right seven."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=False, grid_at=t + 0.05, rows=False)
    tg = T(X, b, "at_n", t, t + 1.8)
    X.css("po-hundred", """
.po .mx { position:absolute; display:grid; grid-template-columns:repeat(10, 1fr); }
.po .mx i { position:relative; display:block; border-top:2px solid currentColor; font-style:normal; }
.po .mx i span { position:absolute; left:0; top:6px; font-family:var(--f-mono); letter-spacing:.02em; opacity:.75; }
.po .mx i u { position:absolute; left:0; bottom:4px; height:5px; background:currentColor; opacity:.18; text-decoration:none; }
.po .mx i.hot { color:var(--blue); }
.po .mx i.hot u { opacity:1; }
""")
    if g.v:
        L = dict(k=(g.x(0), 300), h1=(g.x(0), 352, 66), h2=(g.x(0), 456, 200), cnt=(g.x(8), 300, 150),
                 mx=(g.x(0), 880, g.w(12), 340), fs=14, en=(g.x(0), 1236, 24))
    else:
        L = dict(k=(g.x(0), 150), h1=(g.x(0), 210, 70), h2=(g.x(0), 300, 215), cnt=(g.x(0), 770, 150),
                 mx=(g.x(5), 160, g.w(7), 760), fs=15, en=(g.x(5), 940, 22))
    cnt_n = int(b.get("count", 100)); pad = max(3, len(str(cnt_n)))
    cells = "".join(f'<i class="{"hot" if k == 36 else ""}"><span style="font-size:{L["fs"]}px">{k + 1:03d}</span><u style="width:{30 + (k * 37) % 60}%"></u></i>' for k in range(100))
    colw = g.w(8) if g.v else g.w(5)
    h1px, h1h, _ = fz(X, b.get("pre", "人人一口气生成"), colw, L["h1"][2], 30, lines=2, lh=1.18)
    h2top = L["h2"][1] + (h1h.count('class="ln"') - 1) * h1px * 1.18
    h2px, h2h, _ = fz(X, b.get("big", "一百个|答案"), g.w(12) if g.v else g.w(5), L["h2"][2], 60, lines=3, h=(L["mx"][1] - 20 - h2top) if g.v else (L["cnt"][1] - 20 - h2top), lh=0.98)
    cpx = min(L["cnt"][2], (g.w(4) if g.v else g.w(5)) / numw("0" * pad))
    X.used_text.update("0123456789")
    mx, my, mw, mh = L["mx"]
    body = (f'<div class="mo" style="{st(left=L["k"][0], top=L["k"][1], font_size=22)}">01 — AI GENERATES</div>'
            f'<div class="zh m" style="{st(left=L["h1"][0], top=L["h1"][1], font_size=h1px)}">{h1h}</div>'
            f'<div class="zh" style="{st(left=L["h2"][0], top=round(h2top), font_size=h2px)}">{h2h}</div>'
            f'<div class="nm blue" style="{st(left=L["cnt"][0], top=L["cnt"][1], font_size=round(cpx))}"><span class="cn">{"0" * pad}</span></div>'
            f'<div class="mx" style="{st(left=mx, top=my, width=mw, height=mh)}; grid-auto-rows:{mh / 10:.1f}px; column-gap:{g.g}px">{cells}</div>'
            f'<div class="la" style="{st(left=L["en"][0], top=L["en"][1], font_size=L["en"][2])}; opacity:.55; white-space:normal; width:{g.w(12) if g.v else g.w(7)}px; line-height:1.25">{X.rich(b.get("en", "100 answers in one breath — generation is free now."))}</div>')
    page(X, cid, t, d, False, grid, furn, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .mo", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.1:.3f});')
    lift(X, f"{s} .zh.m .ln > span", t + 0.15)
    lift(X, f"{s} .zh:not(.m) .ln > span", tg - 0.35, dur=0.7, st=0.09)
    X.tw(f'tl.from("{s} .mx i", {{opacity:0, y:12, duration:0.25, ease:"power2.out", stagger:{{each:0.016, grid:[10,10], from:"start"}}}}, {t + 0.05:.3f});')
    counter(X, f"{s} .cn", t + 0.05, 0, cnt_n, dur=max(1.6, tg - t), pad=pad)
    X.sfx(t + 0.05, "count")
    X.tw(f'tl.from("{s} .la", {{opacity:0, duration:0.5}}, {tg:.3f});')
    X.tw(f'tl.to("{s} .grid", {{opacity:0.35, duration:0.6}}, {t + 1.0:.3f});')


def problem(b, X, t, d, cid):
    """the turn: black page, 问题 set across six columns, the claim struck by a blue bar; the 100 answers shrink to a strip."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=True, grid_at=None)
    tk = T(X, b, "at_strike", t, t + d * 0.6)
    X.css("po-problem", """
.po .strip { position:absolute; display:flex; gap:4px; }
.po .strip i { flex:1; height:100%; background:currentColor; opacity:.28; }
.po .strip i.hot { background:var(--blue); opacity:1; }
""")
    if g.v:
        L = dict(big=(g.x(0) - 10, 300, 420), q=(g.x(0), 820, 56), cl=(g.x(0), 900, 112), ix=(g.x(9), 300, 120), strip=(g.x(0), 1180, g.w(12), 34))
    else:
        L = dict(big=(g.x(0) - 14, 150, 470), q=(g.x(7), 250, 52), cl=(g.x(7), 330, 112), ix=(g.x(11), 150, 110), strip=(g.x(0), 900, g.w(12), 36))
    strip = "".join(f'<i class="{"hot" if k == 36 else ""}"></i>' for k in range(100))
    sx, sy, sw, sh = L["strip"]
    q, claim, strike = b.get("q", "从来不是"), b.get("claim", "答案|不够多"), b.get("strike", "不够多")
    bw = g.w(12) if g.v else (g.x(7) - g.x(0) - 40)
    bpx, bigh, bf = fz(X, b.get("big", "问题"), bw, L["big"][2], 120, lines=2, h=(L["q"][1] - L["big"][1] - 20) if g.v else 720)
    rw = g.w(12) if g.v else g.w(5)
    qpx, qh, qf = fz(X, q, rw, L["q"][2], 28, lines=2, lh=1.18)
    clf = fit.fit_text(fit.as_text(claim), rw, L["cl"][2] * 1.1 * 3, L["cl"][2], 44, lh=1.1, max_lines=3)
    def sk(line):
        rl = X.rich(line)
        return rl.replace(X.rich(strike), f'<span class="sk" data-layout-allow-occlusion style="position:relative; display:inline-block">{X.rich(strike)}<i class="blk" data-layout-allow-occlusion style="left:-2%; right:-2%; top:46%; height:.16em"></i></span>', 1) if strike and strike in fit.plain(line) else rl
    cl = "".join(f'<span class="ln"><span>{sk(l)}</span></span>' for l in clf.lines)
    cl_top = L["cl"][1] + (qf.n - 1) * qpx * 1.18
    body = (f'<div class="zh" style="{st(left=L["big"][0], top=L["big"][1], font_size=bpx)}">{bigh}</div>'
            f'<div class="nm out" style="{st(left=L["ix"][0], top=L["ix"][1], font_size=L["ix"][2])}">?</div>'
            f'<div class="zh m" style="{st(left=L["q"][0], top=L["q"][1], font_size=qpx)}">{qh}</div>'
            f'<div class="zh" style="{st(left=L["cl"][0], top=round(cl_top), font_size=clf.px)}; line-height:1.1">{cl}</div>'
            f'<div class="strip" style="{st(left=sx, top=sy, width=sw, height=sh)}">{strip}</div>')
    page(X, cid, t, d, True, grid, furn, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .zh:not(.m) .ln > span", {{yPercent:105, duration:0.6, ease:"expo.out", stagger:0.08}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .nm.out", {{x:60, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.3:.3f});')
    lift(X, f"{s} .zh.m .ln > span", t + 0.45)
    X.tw(f'tl.from("{s} .strip i", {{scaleY:0, duration:0.3, ease:"expo.out", stagger:{{each:0.006, from:"start"}}}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .blk", {{scaleX:0, duration:0.35, ease:"power4.out"}}, {tk - 0.1:.3f});')
    X.tw(f'tl.to("{s} .sk", {{opacity:0.45, duration:0.2}}, {tk + 0.15:.3f});')
    X.tw(f'tl.to("{s} .strip i:not(.hot)", {{opacity:0.08, duration:0.4, stagger:{{each:0.003, from:"end"}}}}, {tk + 0.1:.3f});')
    X.sfx(tk, "slam")


def quote(b, X, t, d, cid):
    """the quote: the year at architectural scale, the speaker line, the Chinese line lands word by word, the original + source."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=False, grid_at=t + 0.05, src=b.get("src"), rows=True)
    tq, tn = T(X, b, "at_quote", t, t + d * 0.55), T(X, b, "at_no", t, t + d * 0.85)
    if g.v:
        L = dict(yr=(g.x(0) - 8, 280, 330), who=(g.x(0), 590, 34), wsub=(g.x(0), 640, 20), q1=(g.x(0), 720, 120), q2=(g.x(0), 860, 120),
                 no=(g.x(0), 990, 230), en=(g.x(0), 1230, 26), vr=None)
    else:
        L = dict(yr=(g.x(0) - 10, 140, 400), who=(g.x(0), 470, 36), wsub=(g.x(0), 524, 20), q1=(g.x(5) + 24, 140, 132), q2=(g.x(5) + 24, 290, 132),
                 no=(g.x(5) + 24, 450, 290), en=(g.x(5) + 24, 790, 26), vr=(g.x(5) - g.g // 2 - 2, 140, 700))
    who, wsub = b.get("who", "乔布斯 · 苹果开发者大会"), b.get("who_sub", "WWDC CLOSING CHAT · 13 MAY 1997")
    vr = f'<i class="vrule" style="{st(left=L["vr"][0], top=L["vr"][1], height=L["vr"][2])}"></i>' if L["vr"] else ""
    lw_ = g.w(12) if g.v else g.w(5) - 20          # the year / speaker column
    qw = g.w(12) if g.v else g.w(7) - 24           # the quote column
    yr = str(b.get("year", "1997"))
    ypx = min(L["yr"][2], lw_ / numw(yr))
    wpx, _, _ = fz(X, who, lw_, L["who"][2], 22, lines=1)
    wspx = min(L["wsub"][2], lw_ / max(fit.width(wsub, mono=True), 1))
    q1px = min(L["q1"][2], qw / max(fit.width(b.get("q1", "专注，")), fit.width(b.get("q2", "就是学会")), 1))
    q3px = min(L["no"][2], qw / max(fit.width(b.get("q3", "说不。")), 1))
    enf = fit.fit_text(fit.as_text(b.get("en", ""), " "), qw, 300, L["en"][2] * 3, 30, lh=1.15, max_lines=5)
    en_scale = L["en"][2] / enf.px
    body = (f'<div class="nm out yr" style="{st(left=L["yr"][0], top=L["yr"][1], font_size=round(ypx))}">{X.rich(yr)}</div>'
            f'<div class="nm yr2" style="{st(left=L["yr"][0], top=L["yr"][1], font_size=round(ypx))}">{X.rich(yr)}</div>{vr}'
            f'<div class="zh m who" style="{st(left=L["who"][0], top=L["who"][1], font_size=wpx)}">{X.rich(who)}</div>'
            f'<div class="mo" style="{st(left=L["wsub"][0], top=L["wsub"][1], font_size=round(wspx))}; opacity:.6">{X.rich(wsub)}</div>'
            f'<div class="zh q1" style="{st(left=L["q1"][0], top=L["q1"][1], font_size=round(q1px))}">{X.rich(b.get("q1", "专注，"), split="chars")}</div>'
            f'<div class="zh q2" style="{st(left=L["q2"][0], top=L["q2"][1], font_size=round(q1px))}">{X.rich(b.get("q2", "就是学会"), split="chars")}</div>'
            f'<div class="zh blue q3" style="{st(left=L["no"][0], top=L["no"][1], font_size=round(q3px))}">{X.rich(b.get("q3", "说不。"), split="chars")}</div>'
            f'<div class="la en" style="{st(left=L["q1"][0], top=L["q1"][1], font_size=enf.px)}; font-style:italic; white-space:normal; width:{round(qw / 1)}px; line-height:1.15; transform-origin:0 0">{"<br>".join(X.rich(l) for l in enf.lines)}</div>')
    page(X, cid, t, d, False, grid, furn, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .yr2", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:1.4, ease:"power2.inOut"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .yr", {{x:-60, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .vrule", {{scaleY:0, duration:0.6, ease:"expo.out"}}, {t + 0.4:.3f});')
    X.tw(f'tl.from("{s} .who, {s} .mo", {{y:20, opacity:0, duration:0.5, ease:"expo.out", stagger:0.1}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("{s} .q1 .c, {s} .q2 .c", {{yPercent:60, opacity:0, duration:0.45, ease:"expo.out", stagger:0.06}}, {tq - 0.15:.3f});')
    X.tw(f'tl.from("{s} .q3 .c", {{scale:1.8, opacity:0, duration:0.4, ease:"expo.out", stagger:0.07, transformOrigin:"0% 80%"}}, {tn - 0.12:.3f});')
    X.sfx(tn, "hit")
    X.tw(f'tl.from("{s} .la.en", {{opacity:0, y:30, duration:0.6, ease:"expo.out"}}, {t + 0.9:.3f});')
    X.tw(f'tl.to("{s} .la.en", {{y:{L["en"][1] - L["q1"][1]}, scale:{en_scale:.4f}, opacity:0.75, duration:0.6, ease:"expo.inOut"}}, {tq - 0.45:.3f});')
    X.tw(f'tl.to("{s} .grid", {{opacity:0.5, duration:0.4}}, {tq:.3f});')


def price(b, X, t, d, cid):
    """the seesaw: two columns on a scale — generation sinks, judgment rises, on their words."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=False, grid_at=t + 0.05, rows=True)
    tl_, tr_ = T(X, b, "at_low", t, t + 0.8), T(X, b, "at_high", t, t + 2.0)
    X.css("po-price", """
.po .col { position:absolute; }
.po .col .cap2 { font-family:var(--f-mono); letter-spacing:.06em; opacity:.6; }
.po .col .bar { position:absolute; left:0; right:0; background:currentColor; }
.po .tick { position:absolute; font-family:var(--f-mono); opacity:.5; }
""")
    if g.v:
        A = dict(x=g.x(0), w=g.w(6), top=300); B = dict(x=g.x(6), w=g.w(6), top=300); fz, az, mid = 150, 300, 820
    else:
        A = dict(x=g.x(0), w=g.w(6), top=170); B = dict(x=g.x(6), w=g.w(6), top=210); fz, az, mid = 160, 260, 560
    lw, rw = (list(fit.as_list(b.get("left", ["生成", "变便宜"]))) + ["", ""])[:2], (list(fit.as_list(b.get("right", ["判断", "变贵"]))) + ["", ""])[:2]
    cw_ = A["w"] - 20
    fz = min(fz, cw_ / max(fit.width(lw[0]), fit.width(rw[0]), 1))
    sz = min(fz * 0.42, cw_ / max(fit.width(lw[1]), fit.width(rw[1]), 1))
    ticks = "".join(f'<div class="tick" style="{st(left=g.x(11) + g.w(1) - 60, top=mid - 300 + k * 100, font_size=16)}">{(6 - k) * 20:03d}</div>' for k in range(7))
    X.used_text.update("0123456789↓↑")
    body = (f'<i class="rule" style="{st(left=g.m, top=mid, width=g.W - 2 * g.m)}"></i>'
            f'<div class="col L" style="{st(left=A["x"], top=A["top"], width=A["w"])}"><div class="cap2" style="font-size:20px">A — GENERATION</div>'
            f'<div class="zh" style="position:relative; font-size:{fz:.0f}px; margin-top:20px">{X.rich(lw[0])}</div>'
            f'<div class="zh m" style="position:relative; font-size:{sz:.0f}px; margin-top:16px">{X.rich(lw[1])}</div>'
            f'<div class="nm arr" style="position:relative; font-size:{az}px; margin-top:46px; line-height:1">↓</div></div>'
            f'<div class="col R blue" style="{st(left=B["x"], top=B["top"], width=B["w"])}"><div class="cap2" style="font-size:20px">B — JUDGMENT</div>'
            f'<div class="zh" style="position:relative; font-size:{fz:.0f}px; margin-top:20px">{X.rich(rw[0])}</div>'
            f'<div class="zh m" style="position:relative; font-size:{sz:.0f}px; margin-top:16px">{X.rich(rw[1])}</div>'
            f'<div class="nm arr" style="position:relative; font-size:{az}px; margin-top:46px; line-height:1">↑</div></div>{ticks}')
    page(X, cid, t, d, False, grid, furn, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .rule", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .col", {{y:80, opacity:0, duration:0.6, ease:"expo.out", stagger:0.12}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .tick", {{opacity:0, x:20, duration:0.3, stagger:0.04}}, {t + 0.3:.3f});')
    sink = 140 if not g.v else 200
    X.tw(f'tl.to("{s} .col.L", {{y:{sink}, duration:0.7, ease:"power3.inOut"}}, {tl_ - 0.2:.3f});')
    X.tw(f'tl.to("{s} .col.L", {{opacity:0.35, duration:0.4}}, {tr_ - 0.2:.3f});')
    X.tw(f'tl.to("{s} .col.R", {{y:-{sink // 3}, duration:0.7, ease:"back.out(1.6)"}}, {tr_ - 0.2:.3f});')
    X.tw(f'tl.fromTo("{s} .col.R .arr", {{scale:1}}, {{scale:1.25, duration:0.5, ease:"back.out(2)", transformOrigin:"0% 100%"}}, {tr_:.3f});')
    X.sfx(tl_, "click"); X.sfx(tr_, "hit")


def keep(b, X, t, d, cid):
    """做出多少 / 扔掉多少: 24 frames tile the right columns; on 扔掉 they drop out of the grid until one, in blue, is left."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=False, grid_at=t + 0.05)
    tm, tt, tk = T(X, b, "at_make", t, t + 0.4), T(X, b, "at_toss", t, t + d * 0.55), T(X, b, "at_keep", t, t + d * 0.85)
    X.css("po-keep", """
.po .fr { position:absolute; display:grid; grid-template-columns:repeat(6, 1fr); }
.po .fr i { position:relative; display:block; background:#d9d9d4; border-top:3px solid currentColor; }
.po .fr i:nth-child(3n) { background:#c9c9c3; } .po .fr i:nth-child(5n) { background:#e4e4df; }
.po .fr i span { position:absolute; left:8px; top:8px; font-family:var(--f-mono); font-size:14px; letter-spacing:.04em; opacity:.6; }
.po .fr i.k { background:var(--blue); color:var(--paper); border-color:var(--ink); }
.po .swap { position:absolute; }
.po .swap > div { position:absolute; left:0; top:0; white-space:nowrap; }
""")
    if g.v:
        T1 = dict(x=g.x(0), y=290, z=128, s=52); FR = (g.x(0), 690, g.w(12), 520); CN = (g.x(8), 290, 150)
    else:
        T1 = dict(x=g.x(0), y=150, z=150, s=56); FR = (g.x(5), 150, g.w(7), 770); CN = (g.x(0), 680, 190)
    fx_, fy, fw, fh = FR
    nf = max(2, min(int(b.get("frames", 24)), 36))
    fcols = 6 if nf > 12 else 4 if nf > 6 else 3
    frows = -(-nf // fcols)
    kk = min(int(b.get("keep_i", 13)), nf - 1)
    frames = "".join(f'<i class="{"k" if k == kk else ""}"><span>IMG_{k + 1:04d}</span></i>' for k in range(nf))
    a1, a2 = (list(fit.as_list(b.get("a", ["做出", "多少张图", "不重要"]))) + ["", "", ""])[:3], (list(fit.as_list(b.get("b", ["扔掉", "多少张", "才重要"]))) + ["", "", ""])[:3]
    tcw = g.w(8) if g.v else g.w(5) - 20
    zpx = min(T1["z"], tcw / max(fit.width(a1[1]), fit.width(a2[1]), 1))
    spx_ = min(T1["s"], tcw / max(fit.width(a1[0]), fit.width(a1[2]), fit.width(a2[0]), 1))
    b3px = min(T1["z"] * 0.75, tcw / max(fit.width(a2[2]), 1))
    X.used_text.update("0123456789IMG_")
    body = (f'<div class="swap" style="{st(left=T1["x"], top=T1["y"])}">'
            f'<div class="A"><div class="zh m" style="position:relative; font-size:{spx_:.0f}px">{X.rich(a1[0])}</div>'
            f'<div class="zh" style="position:relative; font-size:{zpx:.0f}px">{lines(X, a1[1])}</div>'
            f'<div class="zh m a3" style="position:relative; font-size:{spx_:.0f}px; margin-top:18px; opacity:.45">{X.rich(a1[2])}</div></div>'
            f'<div class="B"><div class="zh m" style="position:relative; font-size:{spx_:.0f}px">{X.rich(a2[0])}</div>'
            f'<div class="zh" style="position:relative; font-size:{zpx:.0f}px">{lines(X, a2[1])}</div>'
            f'<div class="zh blue b3" style="position:relative; font-size:{b3px:.0f}px; margin-top:12px">{X.rich(a2[2])}</div></div></div>'
            f'<div class="nm cnt" style="{st(left=CN[0], top=CN[1], font_size=min(CN[2], round((g.w(4) if g.v else g.w(5)) / numw(str(nf)))))}"><span class="cv">0</span></div>'
            f'<div class="fr" style="{st(left=fx_, top=fy, width=fw, height=fh)}; grid-template-columns:repeat({fcols}, 1fr); grid-auto-rows:{(fh - (frows - 1) * g.g) / frows:.1f}px; gap:{g.g}px">{frames}</div>')
    page(X, cid, t, d, False, grid, furn, wipe, body)
    s = f"#{cid}"
    lift(X, f"{s} .A .ln > span", t + 0.1)
    X.tw(f'tl.from("{s} .A > div:not(:nth-child(2))", {{opacity:0, y:16, duration:0.4, stagger:0.3}}, {t + 0.1:.3f});')
    X.tw(f'tl.set("{s} .B", {{opacity:0}}, {t:.3f});')
    tf = min(tm, t + 0.2)
    X.tw(f'tl.from("{s} .fr i", {{scale:0.4, opacity:0, duration:0.35, ease:"expo.out", stagger:{{each:{min(0.03, 0.7 / nf):.3f}, grid:[{frows},{fcols}], from:"start"}}}}, {tf:.3f});')
    counter(X, f"{s} .cv", tf, 0, nf, dur=0.9)
    X.sfx(tf, "count")
    # toss: everything but one leaves the grid
    X.tw(f'tl.to("{s} .A", {{yPercent:-30, opacity:0, duration:0.4, ease:"power3.in"}}, {tt - 0.25:.3f});')
    X.tw(f'tl.to("{s} .B", {{opacity:1, duration:0.01}}, {tt - 0.05:.3f});')
    lift(X, f"{s} .B .ln > span", tt - 0.05)
    X.tw(f'tl.from("{s} .B > div:first-child", {{opacity:0, y:16, duration:0.4}}, {tt - 0.05:.3f});')
    X.tw(f'tl.to("{s} .fr i:not(.k)", {{y:{fh}, opacity:0, duration:0.55, ease:"power3.in", stagger:{{each:0.025, from:"edges"}}}}, {tt + 0.1:.3f});')
    counter(X, f"{s} .cv", tt + 0.1, nf, 1, dur=1.0)
    X.tw(f'tl.to("{s} .cnt", {{color:"#1f3bff", duration:0.2}}, {tk - 0.1:.3f});')
    X.tw(f'tl.from("{s} .b3", {{scale:1.6, opacity:0, duration:0.45, ease:"expo.out", transformOrigin:"0% 80%"}}, {tk - 0.12:.3f});')
    X.tw(f'tl.fromTo("{s} .fr i.k", {{scale:1}}, {{scale:1.35, duration:0.6, ease:"back.out(1.8)"}}, {tk - 0.1:.3f});')
    X.sfx(tt + 0.1, "wipe"); X.sfx(tk, "hit")


def thesis(b, X, t, d, cid):
    """选择 at full-width scale with the grid drawn over it; the rest of the sentence sits in the last columns."""
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=True, grid_at=t + 0.25, rows=False)
    te = T(X, b, "at_rest", t, t + d * 0.45)
    if g.v:
        L = dict(big=(g.x(0) - 12, 330, 470), big2=None, rest=(g.x(0), 880, 110), ix=(g.x(9), 300, 90), mo=(g.x(0), 290, 20))
    else:
        L = dict(big=(g.x(0) - 20, 150, 600), big2=None, rest=(g.x(8), 790, 84), ix=(g.x(11), 150, 90), mo=(g.x(8), 750, 20))
    w = b.get("big", "选择")
    bh_ = (L["rest"][1] - L["big"][1] - 30)
    tpx_, _, tf_ = fz(X, w, g.w(12) + 20, L["big"][2], 120, lines=2, h=bh_, lh=0.98)
    L["big"] = (L["big"][0], L["big"][1], tpx_)
    w = "|".join(tf_.lines)
    rpx_, _, rf_ = fz(X, b.get("rest", "才是|新的创作"), g.w(12) if g.v else g.w(4), L["rest"][2], 36, lines=3, lh=1.1)
    L["rest"] = (L["rest"][0], L["rest"][1], rpx_)
    if L["big2"]:
        bigs = (f'<div class="zh bg1" style="{st(left=L["big"][0], top=L["big"][1], font_size=L["big"][2])}">{lines(X, w[0])}</div>'
                f'<div class="zh bg2" style="{st(left=L["big2"][0], top=L["big2"][1], font_size=L["big2"][2])}">{lines(X, w[1:])}</div>')
    else:
        bigs = f'<div class="zh bg1" data-layout-bleed="true" style="{st(left=L["big"][0], top=L["big"][1], font_size=L["big"][2])}">{lines(X, w)}</div>'
    body = (bigs + f'<div class="mo" style="{st(left=L["mo"][0], top=L["mo"][1], font_size=L["mo"][2])}; opacity:.6">{X.rich(b.get("mo", "THESIS — CHOOSING IS CREATING"))}</div>'
            f'<div class="zh blue rest" style="{st(left=L["rest"][0], top=L["rest"][1], font_size=L["rest"][2])}; line-height:1.1">{lines(X, "|".join(rf_.lines))}</div>')
    page(X, cid, t, d, True, grid, furn, wipe, body)
    s = f"#{cid}"
    lift(X, f"{s} .bg1 .ln > span, {s} .bg2 .ln > span", t + 0.05, dur=0.75, st=0.1)
    X.tw(f'tl.to("{s} .grid", {{opacity:0.7, duration:0.3}}, {t + 0.3:.3f});')
    lift(X, f"{s} .rest .ln > span", te - 0.2, dur=0.6, st=0.1)
    X.tw(f'tl.from("{s} .mo", {{opacity:0, duration:0.4}}, {te - 0.2:.3f});')
    X.sfx(t + 0.05, "slam")


def outro(b, X, t, d, cid):
    grid, furn, wipe, g = frame(X, b, t, d, cid, dark=False, grid_at=t + 0.05, rows=True)
    if g.v:
        L = dict(nm=(g.x(0) - 8, 300, 340), zh=(g.x(0), 620, 112), sub=(g.x(0), 770, 36), mo=(g.x(0), 840, 20))
    else:
        L = dict(nm=(g.x(0) - 12, 150, 470), zh=(g.x(0), 560, 120), sub=(g.x(0), 720, 38), mo=(g.x(0), 790, 20))
    body = (f'<div class="nm out" style="{st(left=L["nm"][0], top=L["nm"][1], font_size=L["nm"][2])}">HAT 9</div>'
            f'<div class="zh" style="{st(left=L["zh"][0], top=L["zh"][1], font_size=round(min(L["zh"][2], g.w(12) / max(fit.width(b.get("title", "第九顶帽子")), 1))))}">{X.rich(b.get("title", "第九顶帽子"), split="chars")}</div>'
            f'<div class="zh m" style="{st(left=L["sub"][0], top=L["sub"][1], font_size=round(min(L["sub"][2], g.w(12) / max(fit.width(b.get("sub", "AI 时代的审美与判断")), 1))))}">{X.rich(b.get("sub", "AI 时代的审美与判断"))}</div>'
            f'<div class="mo blue" style="{st(left=L["mo"][0], top=L["mo"][1], font_size=L["mo"][2])}">{X.rich(b.get("mo", "FOLLOW · 关注"))}</div>')
    page(X, cid, t, d, False, grid, furn, wipe, body)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .nm.out", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.9, ease:"power3.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .zh:not(.m) .c", {{yPercent:70, opacity:0, duration:0.5, ease:"expo.out", stagger:0.05}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .zh.m, {s} .mo", {{opacity:0, y:16, duration:0.45, stagger:0.12}}, {t + 0.7:.3f});')
    X.sfx(t + 0.35, "hit")


SCENES = {"hundred": hundred, "problem": problem, "quote": quote, "price": price, "keep": keep, "thesis": thesis, "outro": outro}
