"""press · 财经刊 —— 商业拆解口播的版式：Bloomberg Businessweek 的大字 + 色块，FT / 经济学人图表的数据规矩，
小Lin说 / 所长林超的"一句一图"节奏。暖白纸底、墨黑大字、一个信号红、一个柠檬黄色块；每页固定的页眉页脚
（栏目名、章节号、数据来源），所以哪怕硬切，观众也觉得在翻同一本刊物。

画面全部是矢量和数据：插画、图标、点阵、条形、流程、飞轮，不依赖生图。
场景全部自己实现（SCENES）：hook 价格对利润 · stores 点阵对比 · turn 色块反转 · split 收入构成 + 推进到小数 ·
chain 钱和货两条线 · wheel 飞轮 · thesis 判断句 · outro 账号落版。横屏竖屏各自排版（不是缩放）。
"""

STYLE = {
    "name": "财经刊", "en": "Press", "benchmarks": ["Bloomberg Businessweek", "FT / The Economist 图表", "小Lin说", "所长林超"],
    "tokens": {
        "bg": "#f0ece3", "fg": "#111111", "muted": "#625d56", "accent": "#e2321f", "accent2": "#f6ce3a", "alert": "#e2321f",
        "line": "#d3ccbf", "paper": "#f0ece3", "ink": "#111111", "card": "#fbfaf6", "card-fg": "#111111",
        "red": "#e2321f", "lemon": "#f6ce3a", "white": "#fbfaf6", "mcd": "#3b3834",
        "cap-bg": "#111111", "cap-fg": "#fbfaf6", "cap-size": "40px", "cap-weight": "700", "cap-pad": "10px 24px 12px", "cap-radius": "8px",
        "cap-shadow": "none", "cap-bottom": "64px", "cap-em": "#f6ce3a",
        "punch-top": "70%", "punch-size": "72px",
    },
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "serif": "noto-serif-sc", "num": "archivo", "mono": "jetbrains-mono"},
    "motion": {"ease": "expo.out", "dur": 0.55, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.06})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 70, "bottom": 0, "h": 420}, "portrait": {"left": 380, "bottom": 600, "h": 320}},
    "sfx": {"transition": ("whoosh", 0.3), "enter": ("whoosh_soft", 0.3), "pop": ("pop", 0.45), "hit": ("hit", 0.45), "slam": ("slam", 0.45),
            "count": ("type", 0.3), "click": ("click", 0.35), "mascot": ("whoosh_soft", 0.3), "zoom": ("whoosh_deep", 0.45), "line": ("click", 0.3)},
}

CSS = r"""
.st-press .em .emb { display:none; } .pr .em .emt { color:var(--red); }
.pr { position:absolute; inset:0; }
.pr .cam { position:absolute; inset:0; }
/* furniture: header + footer on every page */
.pr-hd { position:absolute; left:96px; right:96px; top:40px; height:44px; display:flex; align-items:center; justify-content:space-between; border-bottom:2px solid var(--ink);
  font-family:var(--f-display); font-size:22px; color:var(--ink); z-index:5; }
.pr-hd b { font-weight:900; letter-spacing:.04em; } .pr-hd span { color:var(--muted); font-weight:500; margin-left:14px; }
.pr-hd .r { font-family:var(--f-mono); font-size:18px; letter-spacing:.08em; }
.pr-hd .r i { font-style:normal; display:inline-block; background:var(--ink); color:var(--white); padding:2px 8px; margin-left:14px; }
.pr-ft { position:absolute; left:96px; right:96px; bottom:24px; display:flex; justify-content:space-between; align-items:center; z-index:5;
  font-family:var(--f-mono); font-size:16px; letter-spacing:.04em; color:var(--muted); }
.pr-ft .pg { display:flex; gap:6px; } .pr-ft .pg i { width:26px; height:4px; background:var(--line); } .pr-ft .pg i.on { background:var(--ink); }
.pr.inv .pr-hd, .pr.inv .pr-hd span { color:var(--white); border-color:var(--white); } .pr.inv .pr-hd .r i { background:var(--white); color:var(--red); }
.pr.inv .pr-ft { color:rgba(251,250,246,.8); } .pr.inv .pr-ft .pg i { background:rgba(255,255,255,.3); } .pr.inv .pr-ft .pg i.on { background:var(--white); }
.pr.dark .pr-hd, .pr.dark .pr-hd span { color:var(--white); border-color:rgba(255,255,255,.5); } .pr.dark .pr-hd .r i { background:var(--lemon); color:var(--ink); }
.pr.dark .pr-ft { color:rgba(251,250,246,.55); } .pr.dark .pr-ft .pg i { background:rgba(255,255,255,.18); } .pr.dark .pr-ft .pg i.on { background:var(--lemon); }
/* type */
.pr .kick { position:absolute; font-family:var(--f-display); font-weight:700; font-size:26px; color:var(--ink); display:flex; align-items:center; gap:12px; letter-spacing:.06em; }
.pr .kick::before { content:''; width:16px; height:16px; background:var(--red); }
.pr .hl { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--ink); line-height:1.08; letter-spacing:-.01em; }
.pr .ln { display:block; overflow:hidden; padding-bottom:.06em; } .pr .ln > span { display:inline-block; }
.pr .num { font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; line-height:.8; letter-spacing:-.01em; font-variant-numeric:tabular-nums; }
.pr .mono { font-family:var(--f-mono); }
.pr .red { color:var(--red); }
.pr svg.ic { fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
#root.v .pr-hd { left:56px; right:56px; top:176px; font-size:24px; } #root.v .pr-hd .r { font-size:17px; }
#root.v .pr-ft { left:56px; right:56px; bottom:auto; top:1478px; font-size:17px; }
"""

ICONS = {
    "lemon": '<path d="M9 24c0-8.3 6.7-15 15-15s15 6.7 15 15-6.7 15-15 15S9 32.3 9 24z"/><path d="M24 13v22M14.5 18.5l19 11M33.5 18.5l-19 11"/><circle cx="24" cy="24" r="10"/>',
    "factory": '<path d="M5 41V22l10 6v-6l10 6v-6l10 6V7h7v34z"/><path d="M11 35h5M21 35h5M31 35h5"/>',
    "truck": '<path d="M3 13h25v21H3zM28 19h9l7 8v7H28z"/><circle cx="11" cy="36" r="4.5"/><circle cx="35" cy="36" r="4.5"/>',
    "store": '<path d="M8 21v20h32V21"/><path d="M5 21l4-13h30l4 13z"/><path d="M5 21c0 3.3 2.9 5.5 6.5 5.5S18 24.3 18 21c0 3.3 2.7 5.5 6 5.5s6-2.2 6-5.5c0 3.3 2.9 5.5 6.5 5.5S43 24.3 43 21"/><path d="M20 41V31h8v10"/>',
    "person": '<circle cx="24" cy="15" r="7.5"/><path d="M9 43c0-8.8 6.7-15 15-15s15 6.2 15 15"/>',
    "cup": '<path d="M13 16h22l-3.2 27H16.2z"/><path d="M10 16h28M26 16l5-11"/><path d="M14.5 27h19"/>',
    "box": '<path d="M5 15l19-8 19 8v19l-19 8-19-8z"/><path d="M5 15l19 8 19-8M24 23v19"/>',
    "machine": '<rect x="10" y="5" width="28" height="38" rx="3"/><rect x="16" y="11" width="16" height="9"/><path d="M19 30h10M24 25v10"/><path d="M14 43v3M34 43v3"/>',
    "pack": '<path d="M12 19h24l-3 24H15z"/><path d="M9 19c2.5-7 27.5-7 30 0z"/><path d="M24 12V6"/>',
    "coin": '<circle cx="24" cy="24" r="17"/><path d="M17.5 15.5l6.5 8 6.5-8M24 23.5V35M18 26h12M18 31h12"/>',
}


def ic(k, cls="ic"): return f'<svg class="{cls}" viewBox="0 0 48 48">{ICONS[k]}</svg>'


# a flat, ink-outlined editorial illustration: one cup of iced lemon water (no brand)
CUP = """<svg class="cupsvg" viewBox="0 0 320 580" xmlns="http://www.w3.org/2000/svg">
<defs><clipPath id="cupclip"><path d="M46 138 L86 522 Q160 540 234 522 L274 138 Z"/></clipPath>
<linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff6c9"/><stop offset="1" stop-color="#f7d95a"/></linearGradient></defs>
<ellipse cx="160" cy="556" rx="118" ry="14" fill="#111" opacity=".16"/>
<g class="straw"><path d="M178 -6 L206 -2 L184 330 L160 328 Z" fill="#e2321f" stroke="#111" stroke-width="5" stroke-linejoin="round"/>
<path d="M175 40 L203 44 M171 100 L199 104 M167 160 L195 164" stroke="#fbfaf6" stroke-width="9"/></g>
<path d="M46 138 L86 522 Q160 540 234 522 L274 138 Z" fill="url(#water)"/>
<g clip-path="url(#cupclip)">
 <g class="ice" fill="#ffffff" fill-opacity=".62" stroke="#111" stroke-opacity=".35" stroke-width="3">
  <rect x="70" y="150" width="70" height="62" rx="12" transform="rotate(-14 105 181)"/><rect x="170" y="160" width="74" height="64" rx="12" transform="rotate(12 207 192)"/>
  <rect x="122" y="214" width="64" height="58" rx="11" transform="rotate(6 154 243)"/></g>
 <g class="lem" stroke="#111" stroke-width="4">
  <g transform="translate(118 318) rotate(-12)"><circle r="64" fill="#f2bf12"/><circle r="55" fill="#ffe27a"/>
   <path d="M0 -51V51M-44 -25.5L44 25.5M44 -25.5L-44 25.5" stroke="#fff6c9" stroke-width="5"/><circle r="9" fill="#fff6c9" stroke="none"/></g>
  <g transform="translate(214 430) rotate(20)"><circle r="56" fill="#f2bf12"/><circle r="48" fill="#ffe27a"/>
   <path d="M0 -44V44M-38 -22L38 22M38 -22L-38 22" stroke="#fff6c9" stroke-width="5"/><circle r="8" fill="#fff6c9" stroke="none"/></g></g>
 <path d="M66 150 L98 512" stroke="#ffffff" stroke-opacity=".7" stroke-width="16" stroke-linecap="round"/>
 <g fill="#ffffff" opacity=".9"><circle cx="252" cy="250" r="5"/><circle cx="240" cy="300" r="3.5"/><circle cx="256" cy="352" r="4.5"/><circle cx="92" cy="420" r="4"/><circle cx="230" cy="500" r="3.5"/><circle cx="110" cy="250" r="3"/></g>
</g>
<path d="M46 138 L86 522 Q160 540 234 522 L274 138 Z" fill="none" stroke="#111" stroke-width="6" stroke-linejoin="round"/>
<path d="M38 132 Q160 38 282 132 Z" fill="#fbfaf6" stroke="#111" stroke-width="6" stroke-linejoin="round"/>
<rect x="30" y="122" width="260" height="24" rx="11" fill="#fbfaf6" stroke="#111" stroke-width="6"/>
<path d="M92 92 Q160 62 228 92" fill="none" stroke="#111" stroke-opacity=".25" stroke-width="5" stroke-linecap="round"/>
</svg>"""


def burst(n=14, r1=50, r2=40):
    import math
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n - math.pi / 2
        r = r1 if k % 2 == 0 else r2
        pts.append(f"{50 + r * math.cos(a):.2f},{50 + r * math.sin(a):.2f}")
    return f'<svg viewBox="0 0 100 100"><polygon points="{" ".join(pts)}" fill="#e2321f" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>'


# ---------------------------------------------------------------- helpers
from h9 import fit


def numw(s):
    """width in em of a figure set in Archivo at wdth 62 (the condensed numerals used everywhere here)."""
    return sum(0.42 if c.isdigit() else 0.2 if c in ".,:" else 0.62 if c == "%" else 0.34 if c in "-+−" else fit.gw(c) * 0.8 for c in str(s)) or 1


def fs(text, box_w, max_px, min_px=None, box_h=None, lines=1, lh=1.1, num=False):
    """the font size (and the balanced lines) at which `text` fits box_w × box_h — numbers use the condensed figure widths."""
    if num:
        return int(min(max_px, box_w / numw(text))), [str(text)]
    f = fit.fit_text(fit.as_text(text), box_w, box_h or max_px * lh * lines, max_px, min_px or max_px * 0.4, lh=lh, max_lines=lines)
    return f.px, f.lines


def decs(v):
    """decimals a counter should show for a value as written (44.5 → 1, 46479 → 0, "97.50" → 2)."""
    s = str(v)
    return len(s.split(".")[1]) if "." in s and not isinstance(v, int) else 0


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def furn(X, b, extra=""):
    X.css("press", CSS)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "商业拆解"); case = meta.get("case", "")
    src = b.get("src", meta.get("src", ""))
    pg = "".join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(n))
    X.used_text.update(sec + case + src + "0123456789/")
    return (f'<div class="pr-hd"><div><b>第九顶帽子</b><span>{X.rich(sec)}</span></div><div class="r">{X.rich(case)}<i>{i + 1:02d}/{n:02d}</i></div></div>'
            f'<div class="pr-ft"><div>{"来源：" + X.rich(src) if src else ""}</div><div class="pg">{pg}</div></div>{extra}')


def lines(X, text, cls=""):
    """'第一行|第二行' -> line-masked spans (each line lifts out of its own clip)."""
    return "".join(f'<span class="ln {cls}"><span>{X.rich(p)}</span></span>' for p in str(text).split("|"))


def lift(X, sel, t, dur=0.7, st=0.08):
    X.tw(f'tl.from("{sel}", {{yPercent:110, duration:{dur}, ease:"expo.out", stagger:{st}}}, {t:.3f});')


def counter(X, sel, t, a, b, dur=1.0, dec=0, sep=True, ease="power3.out"):
    js = f"o.v.toFixed({dec})" if dec else ("Math.round(o.v).toLocaleString('en-US')" if sep else "String(Math.round(o.v))")
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"{ease}", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def drift(X, sel, t, d, s=1.035):
    X.tw(f'tl.fromTo("{sel}", {{scale:1}}, {{scale:{s}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def shots(X, sel, t, d, keys):
    """camera choreography on a page: keys = [(time, scale, fx, fy), ...] with fx/fy the point to centre (0–1 of the frame).
    Moves are expo.inOut 0.9 s; between moves the camera keeps creeping (+1.5%) so no second is dead.
    The page's own text must stay readable, so the push is capped (1.08, less if the side margins would go), the kicker line never slides under the
    header rule, and the left/right margins stay on screen (an impossible pan falls back to a centred push)."""
    W, H = X.W, X.H
    P = X.portrait
    hb, top0, m = (226, 262, 56) if P else (96, 136, 96)
    cap = min(1.08, (W - 80) / (W - 2 * m))                  # the push may never cost the side margins (≈1.03 portrait, 1.065 landscape)
    def xy(sc, fx, fy):
        sc = min(sc, cap)
        x = min(0, max(W - sc * W, W / 2 - sc * fx * W)); y = min(0, max(H - sc * H, H / 2 - sc * fy * H))
        lo, hi = 40 - sc * m, (W - 40) - sc * (W - m)
        x = (lo + hi) / 2 if lo > hi else min(max(x, lo), hi)
        y = max(y, hb - sc * top0)
        return sc, x, y
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    keys = sorted(keys)
    for k, (tk, sc, fx, fy) in enumerate(keys):
        sc, x, y = xy(sc, fx, fy)
        nxt = keys[k + 1][0] if k + 1 < len(keys) else t + d
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});')
            hold0 = tk
        else:
            mv = min(0.9, max(0.3, nxt - tk - 0.05))
            X.tw(f'tl.to("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"expo.inOut"}}, {tk:.3f});')
            hold0 = tk + mv
        if nxt - hold0 > 0.25:     # creep toward the same focus while holding
            sc2, x2, y2 = xy(min(sc * 1.015, cap), fx, fy)
            if (sc2, round(x2), round(y2)) != (sc, round(x), round(y)):
                X.tw(f'tl.to("{sel}", {{scale:{sc2:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - hold0:.2f}, ease:"none"}}, {hold0:.3f});')


# ---------------------------------------------------------------- scenes
def hook(b, X, t, d, cid):
    """price vs profit: a lemon panel with the cup and a ¥4 burst, against a counting profit figure."""
    X.css("pr-hook", """
.pr-hook .panel { position:absolute; left:0; top:0; bottom:0; width:800px; background:var(--lemon); }
.pr-hook .cup { position:absolute; left:220px; top:196px; width:350px; }
.pr-hook .cupsvg { width:100%; display:block; overflow:visible; }
.pr-hook .bst { position:absolute; left:500px; top:236px; width:260px; height:260px; }
.pr-hook .bst svg { position:absolute; inset:0; width:100%; height:100%; }
.pr-hook .bst .p { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--white); transform:rotate(8deg); }
.pr-hook .bst .p b { font-family:var(--f-num); font-variation-settings:"wdth" 70, "wght" 900; font-size:118px; line-height:.85; }
.pr-hook .bst .p small { font-family:var(--f-display); font-weight:900; font-size:28px; letter-spacing:.2em; }
.pr-hook .tag { position:absolute; left:96px; bottom:150px; }
.pr-hook .tag b { display:block; font-family:var(--f-display); font-weight:900; font-size:46px; color:var(--ink); }
.pr-hook .tag span { font-family:var(--f-mono); font-size:18px; letter-spacing:.2em; color:var(--ink); opacity:.7; }
.pr-hook .kick { left:900px; top:236px; }
.pr-hook .big { position:absolute; left:892px; top:300px; display:flex; align-items:flex-end; gap:14px; color:var(--ink); }
.pr-hook .big .num { font-size:420px; }
.pr-hook .big .u { font-family:var(--f-display); font-weight:900; font-size:150px; line-height:1; color:var(--red); padding-bottom:6px; }
.pr-hook .big .u small { font-size:64px; color:var(--ink); margin-left:6px; }
.pr-hook .rule { position:absolute; left:900px; right:96px; top:690px; height:3px; background:var(--ink); transform-origin:0 50%; }
.pr-hook .sub { position:absolute; left:900px; top:716px; font-family:var(--f-display); font-weight:700; font-size:36px; color:var(--ink); }
.pr-hook .sub b { color:var(--red); font-weight:900; }
.pr-hook .stats { position:absolute; left:900px; right:96px; top:716px; display:grid; grid-template-columns:repeat(3, 1fr); gap:24px; }
.pr-hook .stats div { border-left:3px solid var(--line); padding-left:18px; }
.pr-hook .stats span { display:block; font-family:var(--f-display); font-size:22px; font-weight:700; color:var(--muted); }
.pr-hook .stats b { font-family:var(--f-num); font-variation-settings:"wdth" 70, "wght" 800; font-size:68px; line-height:1; color:var(--ink); }
.pr-hook .stats b small { font-family:var(--f-display); font-size:26px; font-weight:900; margin-left:4px; }
.pr-hook .stats .up { color:var(--red); }
#root.v .pr-hook .panel { width:auto; right:0; bottom:auto; height:900px; }
#root.v .pr-hook .cup { left:250px; top:280px; width:300px; }
#root.v .pr-hook .bst { left:560px; top:330px; width:240px; height:240px; }
#root.v .pr-hook .tag { left:56px; bottom:auto; top:780px; } #root.v .pr-hook .tag b { font-size:40px; }
#root.v .pr-hook .kick { left:60px; top:946px; }
#root.v .pr-hook .big { left:52px; top:1000px; } #root.v .pr-hook .big .num { font-size:330px; } #root.v .pr-hook .big .u { font-size:120px; }
#root.v .pr-hook .rule { left:60px; right:60px; top:1290px; } #root.v .pr-hook .sub { display:none; }
""")
    c = str(b.get("price", "¥4"))
    val = b.get("value", 44.5); vs = fit.fmt_num(val, zh=False, dec=decs(val)) if isinstance(val, (int, float)) else str(val)
    u, u2 = str(b.get("unit", "亿")), str(b.get("unit2", "元"))
    P = X.portrait
    colw = (X.W - 104) if P else (X.W - 892 - 96)
    umax = 120 if P else 150
    upx = min(umax, colw * 0.34 / max(fit.width(u) + 0.43 * fit.width(u2), 0.5))
    npx = min(330 if P else 420, (colw - upx * (fit.width(u) + 0.43 * fit.width(u2)) - 14) / numw(vs))
    bpx = min(118, 190 / numw(c))
    ipx, il = fs(b.get("item", ""), (X.W - 112) if P else 640, 40 if P else 46, 26, lines=2)
    spx, sl = fs(b.get("sub", ""), colw, 36, 24, lines=2)
    inner = (f'<div class="pr pr-hook"><div class="cam"><div class="panel"></div><div class="cup">{CUP}</div>'
             f'<div class="bst">{burst()}<div class="p"><b style="font-size:{bpx:.0f}px">{X.rich(c)}</b><small>{X.rich(b.get("price_sub", "一杯"))}</small></div></div>'
             f'<div class="tag"><b style="font-size:{ipx}px">{"<br>".join(X.rich(l) for l in il)}</b><span>{X.rich(b.get("item_en", ""))}</span></div>'
             f'<div class="kick">{X.rich(b.get("kicker", ""))}</div>'
             f'<div class="big"><span class="num n" style="font-size:{npx:.0f}px">0</span><span class="u" style="font-size:{upx:.0f}px">{X.rich(u)}<small style="font-size:{upx * 0.43:.0f}px">{X.rich(u2)}</small></span></div>'
             f'<div class="rule"></div><div class="sub" style="font-size:{spx}px">{"<br>".join(X.rich(l) for l in sl)}</div></div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    tp, tn = T(X, b, "at_price", t, t + 0.8), T(X, b, "at_num", t, t + 1.6)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .panel", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.55, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .cup", {{y:140, rotation:-8, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("{s} .cup", {{y:0}}, {{y:-14, duration:{d:.2f}, ease:"sine.inOut"}}, {t + 0.95:.3f});')
    X.tw(f'tl.from("{s} .tag > *", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .bst", {{scale:0, rotation:-70, duration:0.55, ease:"back.out(2.2)"}}, {tp - 0.25:.3f});')
    X.tw(f'tl.fromTo("{s} .bst svg", {{rotation:0}}, {{rotation:24, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.sfx(tp - 0.1, "pop")
    X.tw(f'tl.from("{s} .kick", {{x:-30, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .big", {{y:60, opacity:0, duration:0.6, ease:"expo.out"}}, {tn - 0.45:.3f});')
    if isinstance(val, (int, float)): counter(X, f"{s} .n", tn - 0.4, 0, float(val), dur=1.1, dec=decs(val))
    else: X.tw(f'tl.set("{s} .n", {{textContent:"{vs}"}}, {tn - 0.4:.3f});'); X.used_text.update(vs)
    X.sfx(tn - 0.4, "count")
    X.tw(f'tl.from("{s} .big .u", {{scale:0.6, opacity:0, duration:0.4, ease:"back.out(2)"}}, {tn + 0.5:.3f});')
    X.sfx(tn + 0.55, "hit")
    X.tw(f'tl.from("{s} .rule", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {tn:.3f});')
    X.tw(f'tl.from("{s} .sub", {{y:24, opacity:0, duration:0.5, ease:"expo.out"}}, {tn + 0.2:.3f});')
    shots(X, f"{s} .cam", t, d, [(t, 1.1, *((0.5, 0.25) if X.portrait else (0.2, 0.5))), (tn - 0.5, 1.0, 0.5, 0.5)])


def stores(b, X, t, d, cid):
    """two dot fields (1 dot = 100 stores), the extra columns lit; counters run with the fill."""
    A, B = b["a"], b["b"]
    an, bn = float(A["n"]), float(B["n"])
    per = int(b.get("per") or fit.nice_unit(an, bn, lo=40, hi=640))
    na, nb = max(1, round(an / per)), max(1, round(bn / per))
    P = X.portrait
    rows = int(b.get("rows") or (min(15, max(6, -(-max(na, nb) // 48))) if P else min(18, max(8, -(-max(na, nb) // 36)))))
    ca, cb = -(-na // rows), -(-nb // rows)
    X.css("pr-stores", """
.pr-stores .kick { left:96px; top:136px; }
.pr-stores .hl { left:96px; top:178px; font-size:84px; }
.pr-stores .blk { position:absolute; top:330px; }
.pr-stores .lab { display:flex; align-items:baseline; gap:22px; height:150px; white-space:nowrap; }
.pr-stores .lab b { font-family:var(--f-display); font-weight:900; font-size:44px; color:var(--ink); }
.pr-stores .lab .num { font-size:150px; }
.pr-stores .dots { display:grid; grid-auto-flow:column; grid-template-rows:repeat(15, 16px); grid-auto-columns:16px; gap:6px; margin-top:14px; }
.pr-stores .dots i { display:block; width:16px; height:16px; border-radius:50%; }
.pr-stores .A .dots i { background:var(--red); } .pr-stores .B .dots i { background:var(--mcd); }
.pr-stores .dots i.x { box-shadow:0 0 0 0 var(--ink); }
.pr-stores .A .num { color:var(--red); } .pr-stores .B .num { color:var(--mcd); }
.pr-stores .diff { position:absolute; display:flex; flex-direction:column; align-items:center; }
.pr-stores .diff .br { width:100%; height:16px; border:3px solid var(--ink); border-top:0; transform-origin:50% 0; }
.pr-stores .diff b { margin-top:8px; font-family:var(--f-display); font-weight:900; font-size:30px; white-space:nowrap; background:var(--ink); color:var(--lemon); padding:2px 12px; }
.pr-stores .leg { position:absolute; right:96px; top:300px; font-family:var(--f-mono); font-size:18px; color:var(--muted); display:flex; align-items:center; gap:10px; }
.pr-stores .leg i { width:14px; height:14px; border-radius:50%; background:var(--ink); }
#root.v .pr-stores .kick { left:60px; top:262px; } #root.v .pr-stores .hl { left:56px; top:300px; font-size:76px; }
#root.v .pr-stores .leg { right:60px; top:270px; font-size:16px; }
#root.v .pr-stores .blk { left:60px !important; } #root.v .pr-stores .A { top:430px; } #root.v .pr-stores .B { top:930px; }
#root.v .pr-stores .lab { height:116px; } #root.v .pr-stores .lab .num { font-size:120px; } #root.v .pr-stores .lab b { font-size:38px; }
#root.v .pr-stores .dots { grid-template-rows:repeat(15, 14px); grid-auto-columns:14px; gap:5px; margin-top:8px; }
#root.v .pr-stores .dots i { width:14px; height:14px; }
""")
    gap, dot = (19, 14) if P else (22, 16)
    wa, wb = ca * gap - (gap - dot), cb * gap - (gap - dot)
    sp = 120
    lw = (X.W - 120) if P else (X.W - 192 - sp) / 2          # room for a block's label row
    ba, bb = (lw, lw) if P else (max(wa, min(lw, 520)), max(wb, min(lw, 520)))
    x0 = 60 if P else (X.W - ba - sp - bb) // 2
    big_is_a = na >= nb
    extra = abs(na - nb)
    xc = -(-extra // rows) if extra else 0                    # columns that hold the difference (in the larger block)
    cbig = ca if big_is_a else cb
    def dots(n, mine):
        lit = mine and xc
        return "".join(f'<i class="{"x" if lit and k >= (cbig - xc) * rows else ""}"></i>' for k in range(n))
    dots_a, dots_b = dots(na, big_is_a), dots(nb, not big_is_a)
    lab_h = 116 if P else 150
    top_a, top_b = (430, 930) if P else (330, 330)
    bx = x0 if big_is_a else (x0 if P else x0 + ba + sp)
    by = (top_a if big_is_a else top_b) + lab_h + (8 if P else 14) + rows * gap - 2
    da = f'left:{bx + (cbig - xc) * gap}px; top:{by}px; width:{max(xc * gap - (gap - dot), dot)}px'
    unit = b.get("unit", "家")
    diff = b.get("diff") if b.get("diff") is not None else (f"+{fit.fmt_num(abs(an - bn), zh=False)} {unit}" if an != bn else "")
    legend = b.get("legend") or f"= {fit.fmt_num(per, zh=False)} {b.get('per_label', '家门店')}"
    hpx, hl_ = fs(b.get("title", ""), X.W - (112 if P else 192), 76 if P else 84, 40, lines=1)   # one line: the blocks sit right under it
    def lab(name, n, cls):
        ns = fit.fmt_num(n, zh=False, dec=decs(n))
        npx = min(120 if P else 150, lw * 0.62 / numw(ns))
        nm_px = min(38 if P else 44, max(lw - npx * numw(ns) - 30, lw * 0.3) / max(fit.width(name), 1))
        return f'<div class="lab"><b style="font-size:{nm_px:.0f}px">{X.rich(name)}</b><span class="num {cls}" style="font-size:{npx:.0f}px">0</span></div>'
    inner = (f'<div class="pr pr-stores"><div class="cam"><div class="kick">{X.rich(b.get("kicker", ""))}</div>'
             f'<div class="hl" style="font-size:{hpx}px">{"".join(f"<span class=ln><span>{X.rich(l)}</span></span>" for l in hl_)}</div>'
             f'<div class="leg"><i></i>{X.rich(legend)}</div>'
             f'<div class="blk A" style="left:{x0}px; width:{ba:.0f}px">{lab(A["name"], A["n"], "na")}<div class="dots" style="grid-template-rows:repeat({rows}, {dot}px)">{dots_a}</div></div>'
             f'<div class="blk B" style="left:{x0 if P else x0 + ba + sp:.0f}px; width:{bb:.0f}px">{lab(B["name"], B["n"], "nb")}<div class="dots" style="grid-template-rows:repeat({rows}, {dot}px)">{dots_b}</div></div>'
             + (f'<div class="diff" data-layout-allow-overflow style="{da}"><div class="br"></div><b>{X.rich(diff)}</b></div>' if diff and xc else "") + f'</div>{furn(X, b)}</div>')
    X.used_text.update(legend)
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    ta, tb = T(X, b, "at_a", t, t + 0.6), T(X, b, "at_b", t, t + 2.0)
    X.tw(f'tl.from("{s} .kick, {s} .leg", {{opacity:0, x:-24, duration:0.5, ease:"expo.out", stagger:0.1}}, {t:.3f});')
    X.tw(f'tl.from("{s} .A .lab > *", {{yPercent:60, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .A .dots i", {{scale:0, duration:0.3, ease:"back.out(3)", stagger:{{grid:[{rows},{ca}], axis:null, from:[0,0], amount:1.1}}}}, {min(ta - 0.3, t + 0.15):.3f});')
    counter(X, f"{s} .na", min(ta - 0.3, t + 0.15), 0, an, dur=max(1.3, ta + 0.6 - t), dec=decs(A["n"]))
    X.sfx(min(ta - 0.3, t + 0.15), "count")
    X.tw(f'tl.from("{s} .B .lab > *", {{yPercent:60, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {tb - 0.5:.3f});')
    X.tw(f'tl.from("{s} .B .dots i", {{scale:0, duration:0.3, ease:"back.out(3)", stagger:{{grid:[{rows},{cb}], axis:null, from:[0,0], amount:0.9}}}}, {tb - 0.35:.3f});')
    counter(X, f"{s} .nb", tb - 0.35, 0, bn, dur=1.1, dec=decs(B["n"]))
    lift(X, f"{s} .hl .ln > span", tb - 0.1)
    X.sfx(tb, "enter")
    tx = tb + 0.3
    X.tw(f'tl.to("{s} .dots i.x", {{backgroundColor:"#f6ce3a", boxShadow:"0 0 0 2.5px #111", duration:0.25, stagger:{{each:0.006, from:"start"}}}}, {tx:.3f});')
    X.tw(f'tl.fromTo("{s} .dots i.x", {{scale:1}}, {{keyframes:[{{scale:1.6, duration:0.12}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], stagger:{{each:0.006, from:"start"}}, immediateRender:false}}, {tx:.3f});')
    X.tw(f'tl.from("{s} .diff .br", {{scaleY:0, opacity:0, duration:0.3}}, {tx + 0.2:.3f});')
    X.tw(f'tl.from("{s} .diff b", {{y:-14, opacity:0, duration:0.4, ease:"back.out(2)"}}, {tx + 0.3:.3f});')
    X.sfx(tx + 0.3, "hit")
    fa = (0.4, 0.36) if P else ((x0 + ba / 2) / X.W, 0.6)
    shots(X, f"{s} .cam", t, d, [(t, 1.18, *fa), (tb - 0.55, 1.0, 0.5, 0.5), (tx, 1.06, *((0.3, 0.45) if P else (0.3, 0.7)))])


def turn(b, X, t, d, cid):
    """colour slam: the page goes red, the wrong answer is struck through in ink."""
    X.css("pr-turn", """
.pr-turn { background:var(--red); }
.pr-turn .q { position:absolute; left:160px; top:300px; font-family:var(--f-display); font-weight:700; font-size:64px; color:var(--white); }
.pr-turn .big { position:absolute; left:148px; top:400px; font-family:var(--f-display); font-weight:900; font-size:270px; line-height:1.05; color:var(--white); letter-spacing:-.02em; white-space:nowrap; }
.pr-turn .big .s { position:relative; display:inline-block; }
.pr-turn .big .s i.k { position:absolute; left:-2%; right:-2%; top:50%; height:.13em; margin-top:-.04em; background:var(--ink); transform-origin:0 50%; transform:rotate(-3deg); }
.pr-turn .nb { position:absolute; right:110px; top:330px; font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; font-size:300px; line-height:.8; color:rgba(0,0,0,.14); }
#root.v .pr-turn .q { left:70px; top:560px; font-size:58px; }
#root.v .pr-turn .big { left:62px; top:650px; font-size:210px; }
#root.v .pr-turn .nb { right:60px; top:320px; font-size:240px; }
""")
    q, big, s_ = b.get("q", ""), b.get("pre", "不是"), b.get("struck", "")
    P = X.portrait
    room = (X.W - 124) if P else (X.W - 148 - 260)
    two = P or fit.width(big + s_) * 140 > room                   # long → pre and struck on their own lines
    if two:
        bpx = min(210 if P else 270, room / max(fit.width(big), fit.width(s_), 1) * 0.97, (X.H * (0.34 if P else 0.5)) / 2.1)
    else:
        bpx = min(270, room / max(fit.width(big + s_), 1) * 0.97)
    qpx, ql = fs(q, room, 58 if P else 64, 32, lines=2)
    br = "<br>" if two else ""
    inner = (f'<div class="pr pr-turn inv"><div class="cam"><div class="nb">?</div><div class="q" style="font-size:{qpx}px">{"<br>".join(X.rich(l) for l in ql)}</div>'
             f'<div class="big" data-layout-allow-occlusion style="font-size:{bpx:.0f}px; top:{(650 if P else 400) + (len(ql) - 1) * qpx * 1.1:.0f}px">{X.rich(big, split="chars")}{br}<span class="s">{X.rich(s_, split="chars")}<i class="k" data-layout-allow-occlusion></i></span></div></div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tk = T(X, b, "at_strike", t, t + d * 0.6)
    X.tw(f'tl.from("{s} .q", {{y:30, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .big .c", {{scale:1.6, opacity:0, filter:"blur(12px)", duration:0.45, ease:"expo.out", stagger:{min(0.05, d * 0.3 / max(len(fit.plain(big + s_)), 1)):.3f}}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .nb", {{x:80, opacity:0, duration:0.8, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .big .s i.k", {{scaleX:0}}, {{scaleX:1, duration:0.32, ease:"power4.out"}}, {tk - 0.12:.3f});')
    X.tw(f'tl.to("{s} .big .s .c", {{opacity:0.55, duration:0.2}}, {tk:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{x:0}}, {{keyframes:[{{x:-14, duration:0.04}}, {{x:10, duration:0.04}}, {{x:-5, duration:0.04}}, {{x:0, duration:0.05}}]}}, {tk + 0.18:.3f});')
    X.sfx(tk + 0.15, "slam")
    drift(X, f"{s} .cam", t, d, 1.04)


def split(b, X, t, d, cid):
    """revenue structure as one long bar; then the camera dives into the 2.5% sliver and it becomes the page."""
    p = float(b.get("pct", 97.5))
    X.css("pr-split", """
.pr-split .zm { position:absolute; inset:0; }
.pr-split .kick { left:96px; top:136px; }
.pr-split .hl { left:96px; top:178px; font-size:84px; }
.pr-split .pct { position:absolute; left:84px; top:318px; color:var(--red); display:flex; align-items:flex-end; }
.pr-split .pct .num { font-size:330px; } .pr-split .pct small { font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; font-size:150px; line-height:.8; }
.pr-split .pl { position:absolute; left:830px; top:350px; }
.pr-split .pl span { display:block; font-family:var(--f-display); font-weight:700; font-size:40px; color:var(--ink); }
.pr-split .pl b { display:block; font-family:var(--f-display); font-weight:900; font-size:96px; line-height:1.1; color:var(--ink); }
.pr-split .pl .mono { font-size:28px; color:var(--muted); margin-top:6px; }
.pr-split .bar { position:absolute; left:96px; right:96px; top:640px; height:120px; border:4px solid var(--ink); background:var(--white); }
.pr-split .bar .f { position:absolute; left:0; top:0; bottom:0; background:var(--red); transform-origin:0 50%; }
.pr-split .bar .sl { position:absolute; right:0; top:0; bottom:0; background:var(--lemon); border-left:4px solid var(--ink); }
.pr-split .tot { position:absolute; left:28px; top:50%; transform:translateY(-50%); font-family:var(--f-display); font-weight:900; font-size:34px; color:var(--white); white-space:nowrap; }
.pr-split .lead { position:absolute; right:113px; top:572px; width:3px; height:68px; background:var(--ink); transform-origin:50% 100%; }
.pr-split .flag { position:absolute; right:96px; top:520px; font-family:var(--f-display); font-weight:900; font-size:30px; color:var(--ink); background:var(--lemon); border:3px solid var(--ink); padding:0 12px; white-space:nowrap; }
.pr-split .chips { position:absolute; left:96px; top:796px; display:flex; gap:20px; align-items:center; }
.pr-split .chip { display:flex; align-items:center; gap:14px; height:76px; padding:0 26px 0 16px; background:var(--white); border:3px solid var(--ink); border-radius:12px; box-shadow:5px 5px 0 var(--ink); }
.pr-split .chip svg { width:46px; height:46px; color:var(--ink); }
.pr-split .chip b { font-family:var(--f-display); font-weight:900; font-size:38px; color:var(--ink); }
.pr-split .to { font-family:var(--f-display); font-weight:700; font-size:30px; color:var(--ink); margin-left:12px; }
.pr-split .z2 { position:absolute; inset:0; background:var(--lemon); opacity:0; }
.pr-split .z2 .q { position:absolute; left:96px; top:180px; font-family:var(--f-display); font-weight:900; font-size:80px; color:var(--ink); }
.pr-split .z2 .big { position:absolute; left:80px; top:300px; display:flex; align-items:flex-end; color:var(--ink); }
.pr-split .z2 .big .num { font-size:520px; } .pr-split .z2 .big small { font-family:var(--f-num); font-variation-settings:"wdth" 62, "wght" 900; font-size:220px; line-height:.8; }
.pr-split .z2 .lab { position:absolute; left:1060px; top:470px; }
.pr-split .z2 .lab b { display:block; font-family:var(--f-display); font-weight:900; font-size:72px; color:var(--ink); line-height:1.15; }
.pr-split .z2 .lab span { display:inline-block; margin-top:16px; font-family:var(--f-display); font-weight:900; font-size:40px; background:var(--ink); color:var(--lemon); padding:4px 16px; }
#root.v .pr-split .kick { left:60px; top:262px; } #root.v .pr-split .hl { left:56px; top:300px; font-size:70px; }
#root.v .pr-split .pct { left:48px; top:420px; } #root.v .pr-split .pct .num { font-size:280px; } #root.v .pr-split .pct small { font-size:120px; }
#root.v .pr-split .pl { left:60px; top:676px; } #root.v .pr-split .pl b { font-size:76px; } #root.v .pr-split .pl span { font-size:34px; }
#root.v .pr-split .bar { left:60px; right:60px; top:950px; height:100px; }
#root.v .pr-split .tot { font-size:28px; left:20px; } #root.v .pr-split .lead { right:72px; top:880px; height:70px; } #root.v .pr-split .flag { right:60px; top:830px; font-size:28px; }
#root.v .pr-split .chips { left:60px; right:60px; top:1090px; gap:14px; flex-wrap:wrap; } #root.v .pr-split .chip { height:70px; padding:0 20px 0 12px; } #root.v .pr-split .chip b { font-size:34px; }
#root.v .pr-split .to { display:none; }
#root.v .pr-split .z2 .q { left:60px; top:300px; font-size:72px; }
#root.v .pr-split .z2 .big { left:44px; top:420px; } #root.v .pr-split .z2 .big .num { font-size:400px; } #root.v .pr-split .z2 .big small { font-size:170px; }
#root.v .pr-split .z2 .lab { left:60px; top:880px; } #root.v .pr-split .z2 .lab b { font-size:64px; }
""")
    P = X.portrait
    p = min(99.9, max(0.1, p))
    dp, dr = decs(b.get("pct", 97.5)), max(decs(b.get("pct", 97.5)), 1 if (100 - p) % 1 else 0)
    items = [(it if isinstance(it, (list, tuple)) else ("box", it)) for it in fit.as_list(b.get("items", []))][:5]
    icons = [k if k in ICONS else "box" for k, _ in items]
    cw_ = (X.W - 120) if P else (X.W - 192 - 420)            # room for the chip row
    chip_px = min(34 if P else 38, max(20, (cw_ - len(items) * (78 + 20)) / max(sum(fit.width(w) for _, w in items), 1))) if items else 38
    chips = "".join(f'<div class="chip">{ic(k)}<b style="font-size:{chip_px:.0f}px">{X.rich(w)}</b></div>' for k, (_, w) in zip(icons, items))
    z2 = b.get("small", {})
    W_ = X.W
    pct_s = f"{p:.{dp}f}"
    pmax = 280 if P else 330
    ppx = min(pmax, ((W_ - 120) if P else 720) / (numw(pct_s) + 0.62 * 150 / 330))
    plx = 60 if P else int(84 + ppx * numw(pct_s) + ppx * 0.3 + 40)
    plw = (W_ - 120) if P else (W_ - plx - 96)
    pl_px, pl_l = fs(b.get("pl", ""), plw, 76 if P else 96, 40, lines=2)
    pre_px, _ = fs(b.get("pl_pre", ""), plw, 34 if P else 40, 24)
    hpx, hl_ = fs(b.get("title", ""), W_ - (112 if P else 192), 70 if P else 84, 44, lines=2)
    fill_w = (W_ - (120 if P else 192) - 8) * p / 100
    tpx, _ = fs(b.get("total", ""), max(fill_w - 56, 10), 28 if P else 34, 16)
    tot = f'<div class="tot" style="font-size:{tpx}px">{X.rich(b.get("total", ""))}</div>' if fill_w > 240 else ""
    rem_s = f"{100 - p:.{dr}f}"
    rpx = min(400 if P else 520, ((W_ - 104) if P else 940) / (numw(rem_s) + 0.62 * 220 / 520))
    lab_x = 60 if P else int(80 + rpx * numw(rem_s) + rpx * 0.42 + 60)
    lab_w = (W_ - 120) if P else max(W_ - lab_x - 96, 360)
    lpx, ll = fs(z2.get("label", ""), lab_w, 64 if P else 72, 36, lines=2)
    inner = (f'<div class="pr pr-split"><div class="cam"><div class="zm">'
             f'<div class="kick">{X.rich(b.get("kicker", ""))}</div><div class="hl" style="font-size:{hpx}px">{"".join(f"<span class=ln><span>{X.rich(l)}</span></span>" for l in hl_)}</div>'
             f'<div class="pct"><span class="num n" style="font-size:{ppx:.0f}px">0</span><small style="font-size:{ppx * 150 / 330:.0f}px">%</small></div>'
             f'<div class="pl" style="{"" if P else f"left:{plx}px;"}"><span style="font-size:{pre_px}px">{X.rich(b.get("pl_pre", ""))}</span><b style="font-size:{pl_px}px">{"<br>".join(X.rich(l) for l in pl_l)}</b><div class="mono">{X.rich(b.get("pl_sub", ""))}</div></div>'
             f'<div class="lead"></div><div class="flag">{X.rich(b.get("flag", ""))}</div>'
             f'<div class="bar"><div class="f" style="width:{p}%">{tot}</div><div class="sl" style="width:{100 - p:.2f}%"></div></div>'
             f'<div class="chips">{chips}<div class="to">{X.rich(b.get("to", ""))}</div></div></div>'
             f'<div class="z2"><div class="q">{X.rich(z2.get("q", ""))}</div><div class="big"><span class="num n2" style="font-size:{rpx:.0f}px">0</span><small style="font-size:{rpx * 220 / 520:.0f}px">%</small></div>'
             f'<div class="lab" style="{"" if P else f"left:{lab_x}px;"}"><b style="font-size:{lpx}px">{"<br>".join(X.rich(l) for l in ll)}</b><span>{X.rich(z2.get("tag", ""))}</span></div></div></div>{furn(X, b)}</div>')
    X.used_text.update("%")
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tt, tp = T(X, b, "at_total", t, t + 0.2), T(X, b, "at_pct", t, t + 1.4)
    ti = [T(X, b, f"at_i{j + 1}", t, tp + 1 + j * 0.4) for j in range(max(len(items), 1))]
    tz, ts = T(X, b, "at_zoom", t, t + d * 0.6), T(X, b, "at_small", t, t + d * 0.8)
    X.tw(f'tl.from("{s} .kick", {{x:-24, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    lift(X, f"{s} .hl .ln > span", t + 0.05)
    X.tw(f'tl.fromTo("{s} .bar", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.8, ease:"expo.inOut"}}, {tt:.3f});')
    X.tw(f'tl.from("{s} .bar .f", {{scaleX:0, duration:0.9, ease:"power3.inOut"}}, {tp - 0.3:.3f});')
    X.tw(f'tl.from("{s} .pct", {{y:50, opacity:0, duration:0.5, ease:"expo.out"}}, {tp - 0.35:.3f});')
    counter(X, f"{s} .n", tp - 0.3, 0, p, dur=0.9, dec=dp)
    X.sfx(tp - 0.3, "count")
    X.tw(f'tl.from("{s} .pl > *", {{x:40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {tp + 0.3:.3f});')
    X.tw(f'tl.from("{s} .bar .sl", {{opacity:0, duration:0.25}}, {tp + 0.55:.3f});')
    X.tw(f'tl.from("{s} .lead", {{scaleY:0, duration:0.35, ease:"expo.out"}}, {tp + 0.6:.3f});')
    X.tw(f'tl.from("{s} .flag", {{y:20, opacity:0, duration:0.4, ease:"back.out(2)"}}, {tp + 0.75:.3f});')
    X.tw(f'tl.from("{s} .tot", {{x:-30, opacity:0, duration:0.5, ease:"expo.out"}}, {tp + 0.3:.3f});')
    for j, tj in enumerate(ti[:len(items)]):
        X.tw(f'tl.from("{s} .chip:nth-child({j + 1})", {{y:40, scale:0.8, opacity:0, duration:0.45, ease:"back.out(2)"}}, {tj - 0.15:.3f});')
        X.sfx(tj - 0.1, "click")
    X.tw(f'tl.from("{s} .to", {{x:-20, opacity:0, duration:0.4}}, {ti[-1] + 0.3:.3f});')
    # the dive: origin on the sliver, accelerate in, swap to the lemon page when the sliver fills the frame
    bx = (X.W - 60 - 4 - (X.W - 120 - 8) * (100 - p) / 200) if X.portrait else (X.W - 96 - 4 - (X.W - 192 - 8) * (100 - p) / 200)
    by = (950 + 50) if X.portrait else (640 + 60)
    X.tw(f'tl.set("{s} .zm", {{transformOrigin:"{bx:.0f}px {by}px"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .zm", {{scale:70, duration:0.75, ease:"power3.in"}}, {tz - 0.2:.3f});')
    X.sfx(tz - 0.2, "zoom")
    X.tw(f'tl.set("{s} .z2", {{opacity:1}}, {tz + 0.53:.3f});')
    X.tw(f'tl.set("{s} .zm", {{opacity:0}}, {tz + 0.55:.3f});')
    X.tw(f'tl.from("{s} .z2 .q, {s} .z2 .big, {s} .z2 .lab", {{scale:0.86, opacity:0, duration:0.55, ease:"expo.out", stagger:0.08, transformOrigin:"0% 50%"}}, {tz + 0.55:.3f});')
    counter(X, f"{s} .n2", max(ts - 0.3, tz + 0.6), 0, 100 - p, dur=0.7, dec=dr)
    X.sfx(max(ts - 0.3, tz + 0.6), "hit")
    shots(X, f"{s} .cam", t, tz - 0.25 - t, [(t, 1.16, *((0.3, 0.25) if X.portrait else (0.25, 0.3))), (tt + 0.2, 1.0, 0.5, 0.5),
                                         (ti[0] - 0.3, 1.07, *((0.45, 0.55) if X.portrait else (0.42, 0.66)))])
    X.tw(f'tl.to("{s} .cam", {{scale:1, x:0, y:0, duration:0.3, ease:"power2.in"}}, {tz - 0.25:.3f});')


def chain(b, X, t, d, cid):
    """money one way, goods the other: five nodes on two rails; the franchisee turns red; the chain gets bracketed."""
    nodes = b["nodes"]
    n = len(nodes)
    X.css("pr-chain", """
.pr-chain .kick { left:96px; top:136px; }
.pr-chain .hl { left:96px; top:178px; font-size:84px; white-space:nowrap; }
.pr-chain .hl .ln + .ln { position:absolute; left:0; top:0; }
.pr-chain .nd { position:absolute; width:180px; display:flex; flex-direction:column; align-items:center; }
.pr-chain .nd .o { width:180px; height:180px; border-radius:50%; background:var(--white); border:4px solid var(--ink); display:grid; place-items:center; color:var(--ink); position:relative; z-index:2; }
.pr-chain .nd .o svg { width:48%; height:48%; }
.pr-chain .nd b { margin-top:20px; font-family:var(--f-display); font-weight:900; font-size:46px; color:var(--ink); white-space:nowrap; }
.pr-chain .nd > b, .pr-chain .nd > span { display:block; text-align:center; }
.pr-chain .nd span { margin-top:6px; font-family:var(--f-display); font-weight:500; font-size:26px; color:var(--muted); white-space:nowrap; }
.pr-chain .nd.hot .o { background:var(--red); border-color:var(--ink); color:var(--white); }
.pr-chain .rail { position:absolute; height:4px; transform-origin:0 50%; }
.pr-chain .rail.g { background:var(--ink); } .pr-chain .rail.m { background:repeating-linear-gradient(90deg, var(--ink) 0 14px, transparent 14px 24px); }
.pr-chain .rl { position:absolute; font-family:var(--f-display); font-weight:900; font-size:24px; color:var(--ink); }
.pr-chain .tok { position:absolute; left:0; top:0; width:46px; height:46px; margin:-23px 0 0 -23px; z-index:3; display:grid; place-items:center; }
.pr-chain .tok svg { width:40px; height:40px; }
.pr-chain .tok.bx { color:var(--ink); background:var(--lemon); border:3px solid var(--ink); border-radius:8px; }
.pr-chain .tok.bx svg { width:30px; height:30px; }
.pr-chain .tok.cn { color:var(--ink); background:var(--white); border:3px solid var(--ink); border-radius:50%; }
.pr-chain .tok.cn svg { width:34px; height:34px; }
.pr-chain .hotrail { position:absolute; height:8px; margin-top:-2px; background:var(--red); transform-origin:0 50%; z-index:1; }
.pr-chain .brk { position:absolute; height:26px; border:4px solid var(--red); border-top:0; transform-origin:50% 0; }
.pr-chain .brl { position:absolute; font-family:var(--f-display); font-weight:900; font-size:44px; color:var(--red); white-space:nowrap; }
.pr-chain .brl small { font-size:28px; color:var(--ink); margin-left:16px; font-weight:700; }
""")
    X.css("pr-chain-v", """
#root.v .pr-chain .kick { left:60px; top:262px; } #root.v .pr-chain .hl { left:56px; top:300px; font-size:68px; }
#root.v .pr-chain .nd { width:auto; flex-direction:row; align-items:center; gap:28px; }
#root.v .pr-chain .nd .o { width:120px; height:120px; flex:none; } #root.v .pr-chain .nd .o svg { width:58px; height:58px; }
#root.v .pr-chain .nd .tx { display:flex; flex-direction:column; } #root.v .pr-chain .nd b { margin-top:0; font-size:40px; }
#root.v .pr-chain .rail, #root.v .pr-chain .hotrail { width:4px; height:auto; transform-origin:50% 0; }
#root.v .pr-chain .hotrail { width:8px; margin:0 0 0 -2px; }
#root.v .pr-chain .rail.m { background:repeating-linear-gradient(180deg, var(--ink) 0 14px, transparent 14px 24px); }
#root.v .pr-chain .brk { height:auto; width:26px; border:4px solid var(--red); border-left:0; transform-origin:0 50%; }
#root.v .pr-chain .brl { writing-mode:vertical-rl; font-size:46px; letter-spacing:.12em; }
#root.v .pr-chain .brl small { display:none; }
""")
    P = X.portrait
    nodes = nodes[:7]; n = len(nodes)
    if P:
        sp_ = min(172, (1250 - 460) / max(n - 1, 1)); cx = 160; ys = [460 + k * sp_ for k in range(n)]
        pos = [(cx, y) for y in ys]
        r = min(60, sp_ * 0.36)
    else:
        sp_ = 1420 / max(n - 1, 1); y = 470; xs = [250 + k * sp_ for k in range(n)]
        pos = [(x, y) for x in xs]
        r = min(90, sp_ * 0.3)
    html = []
    lab_w = (900 - 160 - r - 40) if P else sp_ * 0.94
    lab_h = 0                                               # tallest label block under a circle (for the bracket)
    for k, nd in enumerate(nodes):
        x, y = pos[k]
        npx = min(40 if P else 46, lab_w / max(fit.width(nd["name"]), 1)); spx = min(26, lab_w / max(fit.width(nd.get("sub", "")), 1))
        nm = f'<b style="font-size:{npx:.0f}px">{X.rich(nd["name"])}</b><span style="font-size:{spx:.0f}px">{X.rich(nd.get("sub", ""))}</span>'
        lab_h = max(lab_h, 20 + npx * 1.4 + (6 + spx * 1.45 if nd.get("sub") else 0))
        tx = f'<div class="tx">{nm}</div>' if P else nm
        st = f"left:{x - r}px; top:{y - r}px" if P else f"left:{x - lab_w / 2:.0f}px; top:{y - r}px; width:{lab_w:.0f}px"   # label-wide box, circle centred
        html.append(f'<div class="nd" data-k="{k}" style="{st}"><div class="o" style="width:{2 * r:.0f}px; height:{2 * r:.0f}px">{ic(nd.get("icon", "box"))}</div>{tx}</div>')
    rails = []
    off_g, off_m = -round(r * 0.33), round(r * 0.33)
    for k in range(n - 1):
        (x1, y1), (x2, y2) = pos[k], pos[k + 1]
        if P:
            rails.append(f'<i class="rail g" data-k="{k}" style="left:{x1 + off_g}px; top:{y1 + r}px; height:{y2 - y1 - 2 * r}px"></i>')
            rails.append(f'<i class="rail m" data-k="{k}" style="left:{x1 + off_m}px; top:{y1 + r}px; height:{y2 - y1 - 2 * r}px"></i>')
        else:
            rails.append(f'<i class="rail g" data-k="{k}" style="left:{x1 + r}px; top:{y1 + off_g}px; width:{x2 - x1 - 2 * r}px"></i>')
            rails.append(f'<i class="rail m" data-k="{k}" style="left:{x1 + r}px; top:{y1 + off_m}px; width:{x2 - x1 - 2 * r}px"></i>')
    # hot rail: goods side, from the first node to the franchisee
    hk = min(max(int(b.get("hot", n - 2)), 0), n - 1)
    (hx1, hy1), (hx2, hy2) = pos[0], pos[hk]
    hot = (f'<i class="hotrail" style="left:{hx1 + off_g - 2}px; top:{hy1}px; height:{hy2 - hy1}px"></i>' if P
           else f'<i class="hotrail" style="left:{hx1}px; top:{hy1 + off_g}px; width:{hx2 - hx1}px"></i>')
    # tokens: boxes ride the goods rail toward the franchisee, a cup goes to "you", coins come back
    toks = '<div class="tok bx t1">' + ic("box") + '</div><div class="tok bx t2">' + ic("box") + '</div><div class="tok bx cupk">' + ic("cup") + '</div><div class="tok cn c1">' + ic("coin") + '</div><div class="tok cn c2">' + ic("coin") + "</div>"
    if P:
        brk = f'<div class="brk" style="left:{900}px; top:{pos[0][1] - r}px; height:{pos[hk][1] - pos[0][1] + 2 * r}px"></div><div class="brl" style="left:{946}px; top:{pos[0][1] - r + 10}px">{X.rich(b.get("bracket", ""))}</div>'
        rl = ""
    else:
        by_ = pos[0][1] + r + lab_h + 14
        brk = (f'<div class="brk" style="left:{pos[0][0] - r}px; top:{by_:.0f}px; width:{pos[hk][0] - pos[0][0] + 2 * r}px"></div>'
               f'<div class="brl" style="left:{pos[0][0] - r}px; top:{by_ + 36:.0f}px">{X.rich(b.get("bracket", ""))}<small>{X.rich(b.get("bracket_sub", ""))}</small></div>')
        rl = (f'<div class="rl" style="left:96px; top:{pos[0][1] + off_g - 18}px">货 →</div><div class="rl" style="left:96px; top:{pos[0][1] + off_m - 18}px">← 钱</div>')
        X.used_text.update("货钱→←")
    titles = b.get("title", "").split("||")
    hpx = min(fs(x, X.W - (112 if P else 192), 68 if P else 84, 40)[0] for x in titles)
    hl = "".join(f'<span class="ln"><span>{X.rich(x)}</span></span>' for x in titles)
    inner = (f'<div class="pr pr-chain"><div class="cam"><div class="kick">{X.rich(b.get("kicker", ""))}</div><div class="hl" style="font-size:{hpx}px">{hl}</div>'
             f'{rl}{"".join(rails)}{hot}{"".join(html)}{toks}{brk}</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    ty, tst, tc = T(X, b, "at_you", t, t + 0.6), T(X, b, "at_store", t, t + 2.0), T(X, b, "at_chain", t, t + 3.2)
    X.tw(f'tl.from("{s} .kick", {{x:-24, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hl .ln:nth-child(1) > span", {{yPercent:110, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    if len(titles) > 1:
        X.tw(f'tl.to("{s} .hl .ln:nth-child(1) > span", {{yPercent:-110, duration:0.5, ease:"expo.in"}}, {tst - 0.35:.3f});')
        X.tw(f'tl.from("{s} .hl .ln:nth-child(2) > span", {{yPercent:110, duration:0.6, ease:"expo.out"}}, {tst + 0.1:.3f});')
    X.tw(f'tl.from("{s} .nd", {{scale:0.5, opacity:0, duration:0.5, ease:"back.out(2)", stagger:0.07}}, {t + 0.1:.3f});')
    sc = "scaleY" if P else "scaleX"
    X.tw(f'tl.from("{s} .rail", {{{sc}:0, duration:0.5, ease:"expo.inOut", stagger:0.05}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .rl", {{opacity:0, duration:0.4, stagger:0.1}}, {t + 0.5:.3f});')
    X.sfx(t + 0.1, "enter")

    def at(k, side):
        x, y = pos[k]
        if P: return x + (off_g if side == "g" else off_m), y
        return x, y + (off_g if side == "g" else off_m)
    ax = "y" if P else "x"
    # you buy a cup (franchisee -> you), the coin goes back
    (sx, sy), (ex, ey) = at(hk, "g"), at(n - 1, "g")
    (mx, my), (nx, ny) = at(n - 1, "m"), at(hk, "m")
    X.tw(f'tl.set("{s} .tok", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .cupk", {{x:{sx}, y:{sy}, opacity:1}}, {{x:{ex}, y:{ey}, duration:0.9, ease:"power2.inOut"}}, {ty - 0.2:.3f});')
    X.tw(f'tl.to("{s} .cupk", {{opacity:0, duration:0.15}}, {ty + 0.75:.3f});')
    X.tw(f'tl.fromTo("{s} .c1", {{x:{mx}, y:{my}, opacity:1}}, {{x:{nx}, y:{ny}, duration:0.9, ease:"power2.inOut"}}, {ty + 0.3:.3f});')
    X.tw(f'tl.to("{s} .c1", {{opacity:0, duration:0.15}}, {ty + 1.2:.3f});')
    X.sfx(ty, "click")
    # the franchisee buys the chain: node goes red, hot rail floods along the goods side, boxes run it
    X.tw(f'tl.to("{s} .nd[data-k=\'{hk}\'] .o", {{backgroundColor:"#e2321f", color:"#fbfaf6", scale:1.12, duration:0.35, ease:"back.out(2)"}}, {tst:.3f});')
    X.sfx(tst, "pop")
    X.tw(f'tl.from("{s} .hotrail", {{{sc}:0, duration:0.9, ease:"power2.inOut"}}, {tst + 0.15:.3f});')
    (bx0, by0), (bx1, by1) = at(0, "g"), at(hk, "g")
    for j, cls in enumerate(("t1", "t2")):
        st0 = tst + 0.2 + j * 0.45
        X.tw(f'tl.fromTo("{s} .{cls}", {{x:{bx0}, y:{by0}, opacity:1}}, {{x:{bx1}, y:{by1}, duration:1.6, ease:"none", repeat:2}}, {st0:.3f});')
    X.tw(f'tl.fromTo("{s} .c2", {{x:{nx}, y:{ny}, opacity:1}}, {{x:{at(1, "m")[0]}, y:{at(1, "m")[1]}, duration:1.4, ease:"none", repeat:2}}, {tst + 0.5:.3f});')
    for k in range(hk + 1):
        X.tw(f'tl.to("{s} .nd[data-k=\'{k}\'] .o", {{borderColor:"#e2321f", duration:0.2}}, {tst + 0.15 + k * 0.2:.3f});')
    # the bracket
    X.tw(f'tl.from("{s} .brk", {{{"scaleX" if P else "scaleY"}:0, opacity:0, duration:0.4, ease:"expo.out"}}, {tc - 0.2:.3f});')
    X.tw(f'tl.from("{s} .brl", {{{ax}:{-20 if not P else -20}, opacity:0, duration:0.5, ease:"expo.out"}}, {tc:.3f});')
    X.sfx(tc, "hit")
    shots(X, f"{s} .cam", t, d, [(t, 1.22, *((0.3, 0.6) if X.portrait else (0.78, 0.45))), (tst - 0.4, 1.0, 0.5, 0.5),
                                 (tc - 0.1, 1.08, *((0.5, 0.45) if X.portrait else (0.35, 0.62)))])


def wheel(b, X, t, d, cid):
    """the flywheel: four stations on a ring, a red comet runs it and lights each station on its word."""
    import math
    st = [str(x) for x in fit.as_list(b.get("stations"))][:6] or ["价格更低", "卖得更多", "原料走量", "采购更便宜"]
    n = len(st)
    X.css("pr-wheel", """
.pr-wheel .kick { left:96px; top:136px; }
.pr-wheel .q { position:absolute; left:96px; top:300px; font-family:var(--f-display); font-weight:700; font-size:64px; color:var(--ink); }
.pr-wheel .big { position:absolute; left:88px; top:380px; font-family:var(--f-display); font-weight:900; font-size:180px; line-height:1.05; color:var(--ink); letter-spacing:-.02em; }
.pr-wheel .big .red { color:var(--red); }
.pr-wheel .sum { position:absolute; left:96px; top:640px; width:700px; font-family:var(--f-display); font-weight:700; font-size:28px; line-height:1.7; color:var(--muted); }
.pr-wheel .ring { position:absolute; border-radius:50%; border:4px solid var(--ink); }
.pr-wheel .ring2 { position:absolute; border-radius:50%; border:2px dashed var(--line); }
.pr-wheel .orb { position:absolute; }
.pr-wheel .orb i { position:absolute; left:50%; top:0; width:34px; height:34px; margin:-17px 0 0 -17px; border-radius:50%; background:var(--red); border:4px solid var(--ink); }
.pr-wheel .arw { position:absolute; width:0; height:0; border-left:13px solid transparent; border-right:13px solid transparent; border-top:20px solid var(--ink); margin:-10px 0 0 -13px; }
.pr-wheel .stn { position:absolute; transform:translate(-50%,-50%); white-space:nowrap; font-family:var(--f-display); font-weight:900; font-size:40px; color:var(--ink);
  background:var(--white); border:4px solid var(--ink); border-radius:999px; padding:10px 30px; box-shadow:5px 5px 0 var(--ink); }
.pr-wheel .stn .hot { position:absolute; inset:-4px; border-radius:999px; background:var(--red); border:4px solid var(--ink); color:var(--white); padding:10px 30px; opacity:0; }
.pr-wheel .ctr { position:absolute; transform:translate(-50%,-50%); text-align:center; }
.pr-wheel .ctr b { display:block; font-family:var(--f-display); font-weight:900; font-size:64px; color:var(--ink); }
.pr-wheel .ctr span { font-family:var(--f-mono); font-size:20px; letter-spacing:.3em; color:var(--muted); }
#root.v .pr-wheel .kick { left:60px; top:262px; }
#root.v .pr-wheel .q { left:60px; top:310px; font-size:56px; } #root.v .pr-wheel .big { left:52px; top:380px; font-size:150px; }
#root.v .pr-wheel .sum { display:none; }
#root.v .pr-wheel .stn { font-size:36px; padding:8px 24px; } #root.v .pr-wheel .stn .hot { padding:8px 24px; }
""")
    cx, cy, R = (540, 960, 255) if X.portrait else (1330, 560, 285)
    ring = f'<div class="ring" style="left:{cx - R}px; top:{cy - R}px; width:{2 * R}px; height:{2 * R}px"></div><div class="ring2" style="left:{cx - R - 34}px; top:{cy - R - 34}px; width:{2 * R + 68}px; height:{2 * R + 68}px"></div>'
    arws = ""
    step = 360 / n
    for k in range(n):
        a = math.radians((k + 0.5) * step)
        x, y = cx + R * math.sin(a), cy - R * math.cos(a)
        arws += f'<i class="arw" style="left:{x:.0f}px; top:{y:.0f}px; transform:rotate({90 + (k + 0.5) * step:.0f}deg)"></i>'
    stn = ""
    spx = min(36 if X.portrait else 40, R * (1.05 if n <= 4 else 0.8) / max(max(fit.width(w) for w in st), 1))
    for k, w in enumerate(st):
        a = math.radians(step * k)
        x, y = cx + R * math.sin(a), cy - R * math.cos(a)
        stn += f'<div class="stn" data-k="{k}" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{spx:.0f}px">{X.rich(w)}<span class="hot">{X.rich(w)}</span></div>'
    orb = f'<div class="orb" style="left:{cx - R}px; top:{cy - R}px; width:{2 * R}px; height:{2 * R}px"><i></i></div>'
    cpx = min(64, R * 0.9 / max(fit.width(b.get("center", "飞轮")), 1))
    bpx, bl = fs(b.get("big", ""), (X.W - 104) if X.portrait else 780, 150 if X.portrait else 180, 70, lines=2, lh=1.05)
    qpx, _ = fs(b.get("q", ""), (X.W - 104) if X.portrait else 780, 56 if X.portrait else 64, 30)
    sumpx, sl = fs(b.get("sum", ""), 700, 28, 18, lines=4, lh=1.7)
    ctr = f'<div class="ctr" style="left:{cx}px; top:{cy}px"><b style="font-size:{cpx:.0f}px">{X.rich(b.get("center", "飞轮"))}</b><span>{X.rich(b.get("center_en", "FLYWHEEL"))}</span></div>'
    inner = (f'<div class="pr pr-wheel"><div class="cam"><div class="kick">{X.rich(b.get("kicker", ""))}</div><div class="q" style="font-size:{qpx}px">{X.rich(b.get("q", ""))}</div>'
             f'<div class="big" style="font-size:{bpx}px">{"<br>".join(X.rich(l, split="chars") for l in bl)}</div><div class="sum" style="font-size:{sumpx}px; top:{max(640, 380 + len(bl) * bpx * 1.05 + 36):.0f}px">{"<br>".join(X.rich(l) for l in sl)}</div>'
             f'{ring}{arws}{orb}{stn}{ctr}</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tm, tr = T(X, b, "at_more", t, t + 1.5), T(X, b, "at_mat", t, t + 2.5)
    X.tw(f'tl.from("{s} .kick, {s} .q", {{x:-24, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t:.3f});')
    X.tw(f'tl.from("{s} .big .c", {{yPercent:40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.05}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .ring", {{scale:0.6, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .ring2", {{scale:1.2, opacity:0, duration:0.9, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .ring2", {{rotation:0}}, {{rotation:40, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .stn", {{scale:0, duration:0.45, ease:"back.out(2)", stagger:0.08}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .arw, {s} .ctr", {{opacity:0, duration:0.4, stagger:0.05}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .sum", {{opacity:0, y:20, duration:0.5}}, {t + 0.8:.3f});')
    X.sfx(t + 0.25, "enter")
    # comet: N at t, E on "卖得越多", S on "原料走得越多", then W, N, and keep going
    hits = [t + 0.35, tm] + ([tr] if n > 2 else [])
    while len(hits) < n: hits.append(hits[-1] + 0.75)
    hits = sorted(hits[:n])
    marks = [(h, k * step) for k, h in enumerate(hits)] + [(hits[-1] + 0.75, 360)]
    for (a0, r0), (a1, r1) in zip(marks, marks[1:]):
        X.tw(f'tl.fromTo("{s} .orb", {{rotation:{r0}}}, {{rotation:{r1}, duration:{max(0.2, a1 - a0):.3f}, ease:"power1.inOut", immediateRender:false}}, {a0:.3f});')
    end = t + d
    tail0 = marks[-1][0]
    if end > tail0:
        X.tw(f'tl.fromTo("{s} .orb", {{rotation:360}}, {{rotation:{360 + 220 * (end - tail0):.0f}, duration:{end - tail0:.3f}, ease:"none", immediateRender:false}}, {tail0:.3f});')
    for k, (tk, _) in enumerate(marks[:n]):
        X.tw(f'tl.fromTo("{s} .stn[data-k=\'{k}\'] .hot", {{opacity:0}}, {{opacity:1, duration:0.15, immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .stn[data-k=\'{k}\']", {{scale:1}}, {{keyframes:[{{scale:1.15, duration:0.15}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tk:.3f});')
        X.sfx(tk, "click")
    shots(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5), (tm - 0.2, 1.06, *((0.5, 0.5) if X.portrait else (0.62, 0.52)))])


def thesis(b, X, t, d, cid):
    """the judgment line, set big in Song; the money word gets a red bar, the selling word is struck."""
    X.css("pr-thesis", """
.pr-thesis .kick { left:160px; top:270px; }
.pr-thesis .l1 { position:absolute; left:150px; top:330px; font-family:var(--f-serif); font-weight:900; font-size:176px; line-height:1.15; color:var(--ink); letter-spacing:-.01em; }
.pr-thesis .l2 { position:absolute; left:160px; top:590px; font-family:var(--f-serif); font-weight:700; font-size:84px; line-height:1.2; color:var(--ink); }
#root .pr-thesis .em .emb { display:block; left:-2%; right:-2%; bottom:.08em; height:.26em; background:var(--red); transform-origin:0 50%; }
#root .pr-thesis .em .emt { color:var(--ink); }
.pr-thesis .st { position:relative; display:inline-block; color:var(--muted); }
.pr-thesis .st i { position:absolute; left:-3%; right:-3%; top:52%; height:6px; background:var(--muted); transform-origin:0 50%; }
.pr-thesis .qm { position:absolute; right:150px; top:150px; font-family:var(--f-serif); font-weight:900; font-size:300px; line-height:1; color:var(--lemon); }
#root.v .pr-thesis .qm { right:60px; top:300px; font-size:260px; }
#root.v .pr-thesis .kick { left:60px; top:480px; }
#root.v .pr-thesis .l1 { left:52px; top:530px; font-size:150px; }
#root.v .pr-thesis .l2 { left:60px; top:900px; font-size:66px; display:none; }
""")
    P = X.portrait
    l1, em = b.get("l1", ""), b.get("em", "")
    marked = l1.replace(em, f"*{em}*", 1) if em and "*" not in l1 else l1
    w1 = (X.W - 104) if P else (X.W - 150 - 96)
    p1, ln1 = fs(marked, w1, 150 if P else 176, 70, lines=3 if P else 2, lh=1.15)
    l2, st = b.get("l2", ""), b.get("struck", "")
    p2, ln2 = fs(l2, (X.W - 120) if P else (X.W - 160 - 96), 66 if P else 84, 40, lines=2, lh=1.2)
    def strike(line):
        if st and st in line:
            a_, _, z_ = line.partition(st)
            return f'{X.rich(a_)}<span class="st" data-layout-allow-occlusion>{X.rich(st)}<i data-layout-allow-occlusion></i></span>{X.rich(z_)}'
        return X.rich(line)
    top1 = 530 if P else 330
    top2 = top1 + len(ln1) * p1 * 1.15 + (40 if P else 50)
    inner = (f'<div class="pr pr-thesis"><div class="cam"><div class="qm">“</div><div class="kick">{X.rich(b.get("kicker", ""))}</div>'
             f'<div class="l1" style="font-size:{p1}px">{"".join(f"<span class=ln><span>{X.rich(l)}</span></span>" for l in ln1)}</div>'
             f'<div class="l2" style="font-size:{p2}px; top:{top2:.0f}px">{"".join(f"<span class=ln><span>{strike(l)}</span></span>" for l in ln2)}</div></div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    te, ts = T(X, b, "at_em", t, t + 0.8), T(X, b, "at_struck", t, t + 2.2)
    X.tw(f'tl.from("{s} .qm", {{y:-40, opacity:0, duration:0.7, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .kick", {{x:-24, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
    lift(X, f"{s} .l1 .ln > span", t + 0.1, dur=0.8)
    X.tw(f'tl.from("{s} .l1 .em .emb", {{scaleX:0, duration:0.45, ease:"power3.out"}}, {te - 0.05:.3f});')
    X.sfx(te, "line")
    lift(X, f"{s} .l2 .ln > span", min(ts - 0.6, t + 1.2), dur=0.7)
    X.tw(f'tl.from("{s} .l2 .st i", {{scaleX:0, duration:0.3, ease:"power3.out"}}, {ts + 0.1:.3f});')
    drift(X, f"{s} .cam", t, d, 1.03)


def outro(b, X, t, d, cid):
    X.css("pr-outro", """
.pr-outro { background:var(--ink); }
.pr-outro .ttl { position:absolute; left:150px; top:360px; font-family:var(--f-display); font-weight:900; font-size:150px; color:var(--white); letter-spacing:.02em; line-height:1.1; }
.pr-outro .sub { position:absolute; left:160px; top:560px; font-family:var(--f-display); font-weight:700; font-size:42px; color:rgba(251,250,246,.7); }
.pr-outro .cta { position:absolute; left:160px; top:660px; font-family:var(--f-display); font-weight:900; font-size:36px; color:var(--ink); background:var(--lemon); padding:12px 30px; border-radius:6px; }
.pr-outro .bar { position:absolute; left:160px; top:330px; width:120px; height:10px; background:var(--red); transform-origin:0 50%; }
#root.v .pr-outro .bar { left:60px; top:470px; } #root.v .pr-outro .ttl { left:52px; top:500px; font-size:130px; }
#root.v .pr-outro .sub { left:60px; top:690px; font-size:40px; } #root.v .pr-outro .cta { left:60px; top:780px; }
""")
    P = X.portrait
    tpx, tl_ = fs(b.get("title", "第九顶帽子"), X.W - (104 if P else 300), 130 if P else 150, 60, lines=2)
    spx, _ = fs(b.get("sub", ""), X.W - (120 if P else 320), 40 if P else 42, 24)
    cpx, _ = fs(b.get("cta", ""), X.W - (180 if P else 380), 36, 22)
    y_sub = (500 if P else 360) + len(tl_) * tpx * 1.1 + 30
    inner = (f'<div class="pr pr-outro dark"><div class="cam"><div class="bar"></div><div class="ttl" style="font-size:{tpx}px">{"<br>".join(X.rich(l, split="chars") for l in tl_)}</div>'
             f'<div class="sub" style="font-size:{spx}px; top:{y_sub:.0f}px">{X.rich(b.get("sub", ""))}</div><div class="cta" style="font-size:{cpx}px; top:{y_sub + spx * 1.4 + 40:.0f}px">{X.rich(b.get("cta", ""))}</div></div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .bar", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .ttl .c", {{yPercent:60, opacity:0, duration:0.55, ease:"expo.out", stagger:0.05}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .sub", {{opacity:0, y:20, duration:0.5, ease:"expo.out"}}, {t + 0.45:.3f});')
    X.tw(f'tl.from("{s} .cta", {{scale:0.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.7:.3f});')
    X.sfx(t + 0.1, "hit")


SCENES = {"hook": hook, "stores": stores, "turn": turn, "split": split, "chain": chain, "wheel": wheel, "thesis": thesis, "outro": outro}
