"""papercut · 剪纸风 —— 层叠纸艺：中国窗花、祥云、灯笼的镂空剪纸，加上纸雕 diorama 那种层层叠叠的立体纸景。
底色是三种纸：朱砂红 #b3151b（默认）、金箔纸 #d9a441、靛蓝 #1d2a5e；米色 #f4ead8 只用作剪下来的纸片，不做底。
每页至少四层纸、各有纤维和软阴影，镜头漂移时按远近视差移动：远（日轮、祥云）· 中（主题纹样）· 近（标题纸版）·
前（花边、灯笼穗）；画面下 22% 永远是两三层剪出来的海水 / 屋檐 / 祥云。
大字是宋体 900 剪出来的：红底上贴米色纸字，或在红纸上镂空、透出下面的金纸。图表也是纸做的：占比 = 一朵窗花被剪掉一块，
排行 = 折出来的纸台阶，数字 = 纸票根。纸片按铰链展开、从别的纸层后面滑出、翻面；换页是整张纸折过来盖住上一页。

场景全部自己实现（SCENES）：hook 大数字开场 · tickets 两张票根 + 纪录印章 · calendar 撕日历 + 鞭炮 ·
share 窗花剪掉一块 · banner 卷轴横幅 + 纸火焰 · stacks 纸台阶排行 · thesis 判断句 · outro 印章落版。
每页底色：beat 写 "ground": "red" | "gold" | "indigo"；不写时按场景（GROUND_OF）。横屏竖屏各自排版；文字、条数按 scripts/h9/fit.py 自适应。
"""
import math

RED, RED2, DEEP, GOLD, GOLD2, INDIGO, IND2, CREAM, INK = "#b3151b", "#d8342b", "#6e0b0f", "#d9a441", "#b9832a", "#1d2a5e", "#2f4386", "#f4ead8", "#1e1b18"
GROUNDS = {   # page, far layer, mid tone, cut-letter colour, the land strip's three layers (back → front)
    "red":    {"bg": RED, "far": "#c9302a", "sun": GOLD, "mid": "#e0473a", "cut": CREAM, "land": ["#8f0f14", "#d9a441", "#f4ead8"], "fg": CREAM},
    "gold":   {"bg": GOLD, "far": "#e6b85c", "sun": CREAM, "mid": "#c48a2c", "cut": RED, "land": ["#b9832a", "#b3151b", "#f4ead8"], "fg": DEEP},
    "indigo": {"bg": INDIGO, "far": "#26367a", "sun": GOLD, "mid": "#34489a", "cut": CREAM, "land": ["#2f4386", "#b3151b", "#f4ead8"], "fg": CREAM},
}
GROUND_OF = {"tickets": "gold", "calendar": "indigo", "share": "gold", "stacks": "indigo", "outro": "gold"}

STYLE = {
    "name": "剪纸风", "en": "Papercut", "benchmarks": ["中国窗花剪纸", "纸雕 diorama / 层叠纸艺广告", "木版年画"],
    "tokens": {
        "bg": RED, "fg": CREAM, "muted": "#f0d9c8", "accent": CREAM, "accent2": GOLD, "alert": RED,
        "line": "#e6dccb", "paper": CREAM, "ink": INK, "card": CREAM, "card-fg": INK,
        "red": RED, "red2": RED2, "deep": DEEP, "gold": GOLD, "cream": CREAM, "indigo": INDIGO,
        # caption: a cream paper strip with a scalloped left end, vermilion Song text (CSS at the end of the file)
        "cap-bg": CREAM, "cap-fg": RED, "cap-size": "38px", "cap-weight": "700", "cap-pad": "10px 26px 12px 36px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "70px", "cap-em": DEEP,
        "punch-top": "70%", "punch-size": "72px",
    },
    # one bold Song (思源宋体 900) for every cut letter and numeral: woodblock weight, cuts cleanly at any size
    "fonts": {"display": "noto-serif-sc", "body": "noto-sans-sc", "num": "noto-serif-sc", "hand": "lxgw-wenkai",
              "mono": "jetbrains-mono", "serif": "noto-serif-sc", "cap": "noto-serif-sc"},
    "motion": {"ease": "expo.out", "dur": 0.55, "stagger": 0.04, "cut": "hard", "transition": "paper", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.08})],
    # the host becomes a single-colour paper-cut silhouette (SVG filter in the outro, CSS at the end of the file)
    "mascot": {"mode": "cameo", "frame": "papercut", "landscape": {"right": 40, "bottom": 20, "h": 640}, "portrait": {"right": -10, "bottom": 400, "h": 640}},
    "outro": {"move": False},
    "sfx": {"transition": ("paper", 0.5), "enter": ("paper", 0.45), "pop": ("pop", 0.45), "hit": ("hit", 0.4), "slam": ("slam", 0.5),
            "count": ("type", 0.3), "click": ("click", 0.3), "mascot": ("whoosh_soft", 0.3), "tear": ("paper", 0.6), "line": ("click", 0.3)},
}

FIBRE = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='420' height='420'>"
         "<filter id='f'><feTurbulence type='fractalNoise' baseFrequency='.045 .16' numOctaves='3' seed='4'/>"
         "<feColorMatrix values='0 0 0 0 .35  0 0 0 0 .22  0 0 0 0 .12  0 0 0 -1.6 1.05'/></filter><rect width='100%' height='100%' filter='url(%23f)'/></svg>")
# the host as a paper cut: dark parts become one sheet of vermilion, bright parts (skin highlights, shirt) are cut away
FACE = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100' preserveAspectRatio='none'>"
        "<g fill='%23000'><path d='M38.6 43.2 Q42.5 39.6 46.4 43.2 Q42.5 45.4 38.6 43.2 Z'/><path d='M53.6 43.2 Q57.5 39.6 61.4 43.2 Q57.5 45.4 53.6 43.2 Z'/>"
        "<path d='M45.5 49.6 Q50 53.4 54.5 49.6 L54.5 50.8 Q50 55.2 45.5 50.8 Z'/></g>"
        "<path d='M33 73.5 Q50 80 67 73.5' fill='none' stroke='%23000' stroke-width='1.6'/></svg>")
SILHOUETTE = ('<svg class="pcfx" width="0" height="0" style="position:absolute"><filter id="pcsil" x="0" y="0" width="1" height="1" primitiveUnits="objectBoundingBox" color-interpolation-filters="sRGB">'
              '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -2.4 -4.7 -.9 0 7.1" result="a"/>'
              '<feComposite in="a" in2="SourceAlpha" operator="in" result="m"/>'
              f'<feImage href="{FACE}" x="0" y="0" width="1" height="1" preserveAspectRatio="none" result="face"/>'
              '<feComposite in="m" in2="face" operator="out" result="cut"/>'
              f'<feFlood flood-color="{RED}"/><feComposite in2="cut" operator="in"/></filter></svg>')

# ---------------------------------------------------------------- paper vocabulary
CSS = r"""
.st-papercut .em .emb { display:none; } .st-papercut .stage { perspective:2200px; }
.pcw { position:absolute; inset:-8px; filter:drop-shadow(0 -6px 14px rgba(0,0,0,.35)); }
.pc { position:absolute; inset:0; overflow:hidden; color:var(--pfg); }
.pc .cam { position:absolute; inset:0; }
.pc .sheet { position:absolute; inset:-40px; background-color:var(--pbg); }
.pc .fib { position:absolute; inset:-40px; background-image:url("__FIBRE__"); background-size:420px; mix-blend-mode:multiply; opacity:.24; pointer-events:none; z-index:40; }
.pc .lay { position:absolute; }
.pc .sh1, .pc .sh2, .pc .sh3 { filter:drop-shadow(0 6px 14px rgba(0,0,0,.28)); }
.pc .sh2 { filter:drop-shadow(0 6px 14px rgba(0,0,0,.28)) drop-shadow(0 2px 0 rgba(0,0,0,.18)); }
.pc .sh3 { filter:drop-shadow(0 6px 14px rgba(0,0,0,.28)) drop-shadow(0 14px 26px rgba(0,0,0,.22)); }
.pc svg { display:block; overflow:visible; }
.pc .cut { font-family:var(--f-display); font-weight:900; color:var(--pcut); line-height:1; white-space:nowrap;
  filter:drop-shadow(0 4px 0 rgba(60,5,5,.35)) drop-shadow(0 6px 14px rgba(0,0,0,.28)); }
.pc .cut.hole { color:var(--gold); filter:none; text-shadow:0 -5px 0 rgba(70,6,6,.55), 0 -10px 12px rgba(0,0,0,.3); }
.pc .cut .c, .pc .cut .n { display:inline-block; font-style:normal; }
.pc .cut .u { display:inline-block; font-size:.42em; vertical-align:.9em; margin-left:.06em; }
.pc .chip { position:absolute; display:inline-flex; align-items:center; gap:12px; padding:10px 24px 12px; background:var(--cream); color:var(--red);
  font-family:var(--f-display); font-weight:900; font-size:34px; white-space:nowrap; filter:drop-shadow(0 6px 14px rgba(0,0,0,.28)); }
.pc .chip.rd { background:var(--red); color:var(--cream); }
.pc .note { position:absolute; font-family:var(--f-hand); white-space:nowrap; }
.pc .land { position:absolute; left:-60px; right:-60px; bottom:-30px; }
.pc .land svg { width:100%; height:100%; }
/* furniture */
.pc-hd { position:absolute; left:84px; right:84px; top:34px; height:52px; display:flex; justify-content:space-between; align-items:center; z-index:30; }
.pc-hd .tag { background:var(--cream); color:var(--ink); font-family:var(--f-display); font-weight:700; font-size:28px; padding:7px 16px 9px; filter:drop-shadow(0 4px 8px rgba(0,0,0,.25)); }
.pc-hd .tag b { color:var(--red); font-weight:900; margin-right:10px; }
.pc-hd .pg { font-family:var(--f-num); font-weight:900; font-size:28px; color:var(--cream); background:var(--deep); padding:6px 12px; }
.pc-ft { position:absolute; left:84px; bottom:18px; z-index:30; font-family:var(--f-body); font-size:22px; color:var(--ink); background:rgba(244,234,216,.94); padding:4px 12px 5px;
  white-space:nowrap; }
#root.v .pc-hd { left:56px; right:56px; top:206px; } #root.v .pc-ft { left:56px; bottom:400px; top:auto; font-size:26px; }   /* 9:16: just above the platform's bottom bar, under the caption */
"""


def deckle(rnd, n=36, amp=0.5, sides="tblr"):
    """clip-path polygon (percent) with torn / deckled paper edges."""
    pts = []
    j = lambda s: rnd.uniform(0, amp) if s in sides else 0.0
    for i in range(n + 1): pts.append((100 * i / n, j("t")))
    for i in range(1, n): pts.append((100 - j("r"), 100 * i / n))
    for i in range(n, -1, -1): pts.append((100 * i / n, 100 - j("b")))
    for i in range(n - 1, 0, -1): pts.append((j("l"), 100 * i / n))
    return "polygon(" + ",".join(f"{x:.2f}% {y:.2f}%" for x, y in pts) + ")"


def noise_bg(alpha=0.16, seed=3):
    from h9 import fx as FXM
    return FXM.noise_svg(0.7, 3, alpha, seed=seed, tint="0.35 0.25 0.18")


def flower(uid, color, petals=8, holes=True, cutaway=None):
    """窗花: a scalloped paper disc with symmetric hollow cuts (mask), 200×200 viewBox. cutaway = a path cut out of it too."""
    r = []
    for k in range(petals * 3):
        a = 2 * math.pi * k / (petals * 3)
        r.append(f'<circle cx="{100 + 88 * math.cos(a):.2f}" cy="{100 + 88 * math.sin(a):.2f}" r="9.5"/>')
    cuts = []
    if holes:
        for k in range(petals):
            a = 360 * k / petals
            cuts.append(f'<ellipse cx="100" cy="52" rx="11" ry="26" transform="rotate({a:.1f} 100 100)"/>')
            cuts.append(f'<path d="M100 18 l6 9 l-6 9 l-6 -9 z" transform="rotate({a + 180 / petals:.1f} 100 100)"/>')
            cuts.append(f'<circle cx="100" cy="80" r="3.6" transform="rotate({a + 180 / petals:.1f} 100 100)"/>')
        for k in range(6):
            cuts.append(f'<ellipse cx="100" cy="88" rx="5" ry="11" transform="rotate({60 * k} 100 100)"/>')
        cuts.append('<circle cx="100" cy="100" r="4.5"/>')
    if cutaway: cuts.append(f'<path d="{cutaway}"/>')
    return (f'<svg viewBox="0 0 200 200"><defs><mask id="m{uid}"><rect x="-20" y="-20" width="240" height="240" fill="#fff"/>'
            f'<g fill="#000">{"".join(cuts)}</g></mask></defs>'
            f'<g fill="{color}" mask="url(#m{uid})"><circle cx="100" cy="100" r="88"/>{"".join(r)}</g></svg>')


CLOUD = ("M14 64 C10 46 28 36 42 42 C46 22 76 16 88 34 C100 24 124 28 126 46 C142 44 152 56 146 68 Z")


def cloud(uid, color):
    return (f'<svg viewBox="0 0 160 80"><defs><mask id="c{uid}"><rect width="160" height="80" fill="#fff"/>'
            f'<g fill="none" stroke="#000" stroke-width="3"><path d="M44 54 a8 8 0 1 1 10 -8"/><path d="M86 50 a9 9 0 1 1 12 -9"/><path d="M118 58 a6 6 0 1 1 8 -6"/></g></mask></defs>'
            f'<path d="{CLOUD}" fill="{color}" mask="url(#c{uid})"/></svg>')


def lantern(body="#d8342b", cap=GOLD, rib=DEEP):
    return (f'<svg viewBox="0 0 120 190"><line x1="60" y1="0" x2="60" y2="26" stroke="#3b2a18" stroke-width="3"/>'
            f'<rect x="40" y="24" width="40" height="12" rx="3" fill="{cap}"/>'
            f'<ellipse cx="60" cy="86" rx="52" ry="52" fill="{body}"/>'
            f'<g fill="none" stroke="{rib}" stroke-width="2.4" opacity=".7"><ellipse cx="60" cy="86" rx="34" ry="52"/><ellipse cx="60" cy="86" rx="14" ry="52"/></g>'
            f'<rect x="40" y="134" width="40" height="12" rx="3" fill="{cap}"/>'
            f'<g stroke="{cap}" stroke-width="3"><line x1="50" y1="146" x2="48" y2="186"/><line x1="60" y1="146" x2="60" y2="190"/><line x1="70" y1="146" x2="72" y2="186"/></g></svg>')


def scallop_strip(color, n=40, w=1000, h=40, down=True):
    """a paper band with a row of scallops hanging off it (bunting / lace edge); down=False points them up."""
    r, band = w / n / 2, h * 0.4
    arcs = "".join(f"A{r:.2f},{h - band:.2f} 0 0 1 {w - (k + 1) * 2 * r:.2f},{band:.2f} " for k in range(n))
    flip = "" if down else "transform:scaleY(-1);"
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="width:100%;height:100%;{flip}"><path d="M0,0 H{w} V{band:.2f} {arcs} Z" fill="{color}"/></svg>'


def waves(uid, w, h, color, n=9, ph=0.0):
    """海水纹: a band whose top is a row of round wave crests, each with three concentric cut arcs."""
    r = w / n / 2
    top = h * 0.32
    d = f"M0 {h} L0 {top + r:.1f} "
    cuts = []
    for k in range(n + 1):
        cx = (k + ph) * 2 * r
        d += f"A{r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {top + r:.1f} " if k == 0 else f"A{r:.1f} {r:.1f} 0 0 1 {cx + r:.1f} {top + r:.1f} "
        for j in (0.72, 0.48, 0.24):
            cuts.append(f'<path d="M{cx + r - r * j:.1f} {top + r:.1f} A{r * j:.1f} {r * j:.1f} 0 0 1 {cx + r + r * j:.1f} {top + r:.1f}"/>')
    d += f"L{w} {h} Z"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs><mask id="w{uid}"><rect width="{w}" height="{h}" fill="#fff"/>'
            f'<g fill="none" stroke="#000" stroke-width="{max(4, r * 0.08):.1f}">{"".join(cuts)}</g></mask></defs><path d="{d}" fill="{color}" mask="url(#w{uid})"/></svg>')


def roofs(uid, rnd, w, h, color):
    """a row of roofs with upturned eaves, cut windows and a lantern hole each."""
    x, d, cuts = -40.0, f"M-40 {h} ", []
    while x < w + 40:
        bw = rnd.uniform(170, 300); top = h * rnd.uniform(0.05, 0.35); eave = top + h * 0.2; wall = eave + 10
        d += (f"L{x:.0f} {wall:.0f} Q{x + bw * 0.04:.0f} {eave:.0f} {x - bw * 0.05:.0f} {eave - 18:.0f} "
              f"Q{x + bw * 0.22:.0f} {eave - 8:.0f} {x + bw * 0.36:.0f} {top:.0f} L{x + bw * 0.64:.0f} {top:.0f} "
              f"Q{x + bw * 0.78:.0f} {eave - 8:.0f} {x + bw * 1.05:.0f} {eave - 18:.0f} Q{x + bw * 0.96:.0f} {eave:.0f} {x + bw:.0f} {wall:.0f} ")
        for k in range(2):
            wx = x + bw * (0.24 + 0.36 * k)
            cuts.append(f'<rect x="{wx:.0f}" y="{wall + 30:.0f}" width="{bw * 0.16:.0f}" height="{bw * 0.2:.0f}" rx="{bw * 0.08:.0f}"/>')
        x += bw + rnd.uniform(-20, 30)
    d += f"L{w + 40} {h} Z"
    return (f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none"><defs><mask id="r{uid}"><rect x="-60" width="{w + 120}" height="{h}" fill="#fff"/>'
            f'<g fill="#000">{"".join(cuts)}</g></mask></defs><path d="{d}" fill="{color}" mask="url(#r{uid})"/></svg>')


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def counter(X, sel, t, a, b, dur=1.0, dec=0):
    js = f"o.v.toFixed({dec})" if dec else "Math.round(o.v).toLocaleString('en-US')"
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power3.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def cutword(X, text, cls="cut", num_cls="n"):
    """paper-cut letters: every glyph its own piece of paper with a slight seeded tilt."""
    out = []
    for ch in str(text):
        if not ch.strip(): out.append(" "); continue
        rot = X.rand.uniform(-2.5, 2.5)
        k = num_cls if (ch.isdigit() or ch in ".,%") else "c"
        out.append(f'<i class="{k}" style="transform:rotate({rot:.2f}deg)">{X.rich(ch)}</i>')
    return "".join(out)


def split_num(s):
    """'48.39亿' → ('48.39', '亿'): the figure is cut huge, the unit as a small piece tucked at its shoulder."""
    s = str(s); k = len(s)
    while k > 0 and not (s[k - 1].isdigit() or s[k - 1] in ".,"): k -= 1
    j = 0
    while j < k and not (s[j].isdigit() or s[j] in "+-−"): j += 1
    return s[j:k], s[k:], s[:j]


def bignum(X, text, w, lo, hi, cls="", ign=False):
    """a cut-paper numeral that fills width w, between lo and hi px tall; returns (html, px, est_width)."""
    from h9 import fit
    num, unit, pre = split_num(text)
    em = fit.width(pre + num) * 1.1 + (fit.width(unit) * 0.42 + 0.06 if unit else 0)
    shoulder = bool(unit) and w / max(0.5, em) < lo          # no room beside it: the unit rides on the figure's shoulder
    if shoulder: em = fit.width(pre + num) * 1.1
    px = max(lo, min(hi, w / max(0.5, em)))
    X.used_text.update(str(text))
    us = f' style="position:absolute;right:0;top:{-0.42 * px:.0f}px;margin:0;font-size:{0.4 * px:.0f}px"' if shoulder else ""
    html = (f'<div class="cut {cls}"{' data-safe="ignore"' if ign else ''} style="font-size:{px:.0f}px">{cutword(X, pre + num)}'
            + (f'<span class="u"{us}>{cutword(X, unit)}</span>' if unit else "") + '</div>')
    return html, px, em * px


def ground(X, i=None):
    i = X.beat["i"] if i is None else i
    bs = X.v.get("beats", [])
    if not 0 <= i < len(bs): return "red"
    g = bs[i].get("ground") or GROUND_OF.get(bs[i].get("scene"), "red")
    return g if g in GROUNDS else "red"


def stage(X, cid, gnd, sun=True, tassels=True):
    """the layers every page shares: far (sun disc, clouds), the land strip along the bottom 22 % in three cut layers
    (waves, roofs, a cloud-wave front), and the front edge (scalloped border, lantern tassels)."""
    G = GROUNDS[gnd]; W, H = X.W, X.H; P = X.portrait
    lh = H * 0.22
    far = ""
    if sun:
        sz = 520 if P else 460
        far += f'<div class="lay far sun sh1" style="left:{W * (0.58 if P else 0.7):.0f}px;top:{H * (0.2 if P else 0.12):.0f}px;width:{sz}px;height:{sz}px;border-radius:50%;background:{G["sun"]};opacity:.9"></div>'
    far += (f'<div class="lay far cl sh1" style="left:{W * 0.04:.0f}px;top:{H * (0.36 if P else 0.4):.0f}px;width:300px;height:150px">{cloud(cid + "fa", G["far"])}</div>'
            f'<div class="lay far cl sh1" style="left:{W * 0.6:.0f}px;top:{H * (0.5 if P else 0.6):.0f}px;width:260px;height:130px">{cloud(cid + "fb", G["far"])}</div>')
    l1, l2, l3 = G["land"]
    land = (f'<div class="land ld1 sh1" style="height:{lh + 40:.0f}px">{waves(cid + "w1", 1200, 400, l1, 7 if P else 11, X.rand.uniform(0, 1))}</div>'
            f'<div class="land ld2 sh2" style="height:{lh * 0.74:.0f}px">{roofs(cid, X.rand, 1600, 300, l2)}</div>'
            f'<div class="land ld3 sh2" style="height:{lh * 0.42:.0f}px">{waves(cid + "w3", 1200, 220, l3, 9 if P else 16, X.rand.uniform(0, 1))}</div>')
    front = f'<div class="lay front edge sh2" style="left:-20px;right:-20px;top:{-6 if P else -6}px;height:{58 if P else 46}px">{scallop_strip(G["land"][2] if gnd != "gold" else RED, 22 if P else 34, 1000, 46)}</div>'
    if tassels:
        for k, x in enumerate((0.04, 0.84) if P else (0.03, 0.9)):
            front += f'<div class="lay front tas sh2" data-k="{k}" style="left:{W * x:.0f}px;top:{20 + 40 * k}px;width:{120 if P else 100}px;height:{190 if P else 158}px">{lantern(RED2 if gnd != "red" else GOLD, GOLD if gnd != "red" else CREAM)}</div>'
    return far, land, front


def page(X, b, cid, t, d, inner, gnd=None, cls="", far="", land="", front=""):
    """one paper page: fibre sheet, far / mid / near / land / front layers, furniture; it folds across over the previous page."""
    X.css("papercut", CSS.replace("__FIBRE__", FIBRE))
    i, n = X.beat["i"], X.beat["n"]
    gnd = gnd or ground(X)
    G = GROUNDS[gnd]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "节庆经济"); src = b.get("src", meta.get("src", ""))
    X.used_text.update(sec + src + "0123456789/·" + X.channel + "来源：")
    clip = deckle(X.rand, 48, 0.35)
    furn = (f'<div class="pc-hd"><div class="tag"><b>{X.rich(X.channel)}</b>{X.rich(sec)}</div><div class="pg">{i + 1:02d}/{n:02d}</div></div>'
            + (f'<div class="pc-ft">来源：{X.rich(src)}</div>' if src else ""))
    html = (f'<div class="pcw"><div class="pc g-{gnd} {cls}" style="clip-path:{clip}; --pbg:{G["bg"]}; --pcut:{G["cut"]}; --pfg:{G["fg"]}"><div class="sheet"></div>'
            f'<div class="cam">{far}{inner}{land}{front}</div><div class="fib"></div>{furn}</div></div>')
    D = X.duration or (t + d)
    ext = min(d + 0.7, max(d, D - t))           # stay under the next page while it folds across
    X.clip(cid, t, ext, html, "scene", 2 + i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    if i > 0:     # the whole sheet folds across: from the top edge on even pages, from the left edge on odd ones
        if i % 2:
            X.tw(f'tl.from("{s} .pcw", {{rotationY:96, transformOrigin:"0% 50%", duration:0.62, ease:"power3.out"}}, {t:.3f});')
        else:
            X.tw(f'tl.from("{s} .pcw", {{rotationX:-96, transformOrigin:"50% 0%", duration:0.62, ease:"power3.out"}}, {t:.3f});')
        X.sfx(t, "transition")
    X.tw(f'tl.from("{s} .land", {{yPercent:70, duration:0.7, ease:"expo.out", stagger:0.09}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .front.edge", {{yPercent:-120, duration:0.6, ease:"back.out(1.6)"}}, {t + 0.15:.3f});')
    for k in range(2): sway(X, f"{s} .tas[data-k='{k}']", t, ext, 3 + k, 1.5 + 0.3 * k)
    return s


def dolly(X, s, t, d, layers=(), push=(1.06, 1.0)):
    """the camera drifts through the paper: the page scales and pans, and each layer shifts by its depth
    (far = slow, front = fast), so the stack reads as real depth."""
    a, b_ = push
    X.tw(f'tl.fromTo("{s} .cam", {{scale:{a}, x:{-14 if X.beat["i"] % 2 else 14}}}, {{scale:{b_}, x:{14 if X.beat["i"] % 2 else -14}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    base = [(".far", 0.25), (".ld1", 0.5), (".ld2", 0.9), (".ld3", 1.4), (".front", 1.9)]
    for sel, depth in base + list(layers):
        X.tw(f'tl.fromTo("{s} {sel}", {{x:{-16 * depth:.1f}, y:{8 * depth:.1f}}}, {{x:{16 * depth:.1f}, y:{-6 * depth:.1f}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


def sway(X, sel, t, d, deg=4, period=1.6):
    rep = max(1, int(d / period))
    X.tw(f'tl.fromTo("{sel}", {{rotation:{-deg}}}, {{rotation:{deg}, duration:{period:.2f}, ease:"sine.inOut", yoyo:true, repeat:{rep}, transformOrigin:"50% 0%"}}, {t:.3f});')


def unfold(X, sel, t, dur=0.6, stagger=0.06):
    """pieces unfold on a hinge at their foot (rotateX), like a pop-up card opening."""
    X.tw(f'tl.from("{sel}", {{rotationX:-100, opacity:0, transformOrigin:"50% 100%", duration:{dur}, ease:"back.out(1.4)", stagger:{stagger}}}, {t:.3f});')


def flip(X, sel, t, dur=0.55):
    """a paper piece flips over to its printed side (rotateY)."""
    X.tw(f'tl.from("{sel}", {{rotationY:-180, opacity:0, duration:{dur}, ease:"power3.out"}}, {t:.3f});')


def bigwrap(html, left, top, cls="near"):
    return f'<div class="lay {cls}" style="left:{left:.0f}px;top:{top:.0f}px"><div style="position:relative;display:inline-block">{html}</div></div>'


# ---------------------------------------------------------------- scenes
def hook(b, X, t, d, cid):
    """开场：朱砂红纸景，窗花在背后转，灯笼穗摇；先翻出一个小签，再从铰链上展开巨大的剪纸数字。"""
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    sm, big = b.get("small", ""), b.get("big", "")
    X.used_text.update(sm)
    far, land, front = stage(X, cid, gnd)
    if P:
        num, px, nw = bignum(X, big, W - 170, 360, 520)      # 9:16: the figure ends clear of the right-hand buttons
        cy, ny = 340, 470
        fl = [(-300, 300, 900, "#c42a26"), (560, 900, 560, DEEP)]
    else:
        num, px, nw = bignum(X, big, 1100, 300, 460)
        cy, ny = 190, 290
        fl = [(-200, -260, 780, "#c42a26"), (W - 520, 380, 480, DEEP)]
    mid = "".join(f'<div class="lay mid fl fl{k} sh1" style="left:{x}px;top:{y}px;width:{s}px;height:{s}px">{flower(cid + f"f{k}", c, 8 + 2 * k)}</div>' for k, (x, y, s, c) in enumerate(fl))
    inner = (mid + (f'<div class="lay near"><div class="chip small" style="left:{56 if P else 96}px;top:{cy}px;transform:rotate(-3deg)">{X.rich(sm)}</div></div>' if sm else "")
             + bigwrap(num, 40 if P else 96, ny, "near big"))
    s = page(X, b, cid, t, d, inner, gnd, "pc-hook", far, land, front)
    ts, tb = T(X, b, "at_small", t, t + 0.1), T(X, b, "at_big", t, t + 0.6)
    flip(X, f"{s} .small", max(t, ts - 0.2))
    X.sfx(max(t, ts - 0.2), "pop")
    unfold(X, f"{s} .big .c, {s} .big .n", max(t + 0.15, tb - 0.35), 0.6, 0.08)
    X.sfx(max(t + 0.15, tb - 0.3), "slam")
    X.tw(f'tl.fromTo("{s} .fl0", {{rotation:0}}, {{rotation:24, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .fl1", {{rotation:0}}, {{rotation:-30, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    dolly(X, s, t, d + 0.7, [(".mid", 0.6), (".near", 1.2)], push=(1.08, 1.0))


def tickets(b, X, t, d, cid):
    """两张剪纸票根：数字随口播滚动，最后一枚"纪录"印章砸下来；票根从纸景后面滑出来。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    items = b.get("items", [])[:3] or [{"label": "票房", "value": 0, "unit": ""}]
    n = len(items)
    X.css("pc-tix", """
.pc-tix .tk { position:absolute; }
.pc-tix .tk .body { position:absolute; inset:0; background:var(--tkc, var(--red));
  -webkit-mask:radial-gradient(circle at 0 50%, transparent 34px, #000 35px) left/51% 100% no-repeat, radial-gradient(circle at 100% 50%, transparent 34px, #000 35px) right/51% 100% no-repeat; }
.pc-tix .tk .in { position:absolute; inset:22px 70px; border:4px dashed rgba(244,234,216,.6); display:flex; flex-direction:column; justify-content:center; padding:0 30px; }
.pc-tix .tk .lb { font-family:var(--f-display); font-weight:900; color:var(--cream); white-space:nowrap; }
.pc-tix .tk .vl { font-family:var(--f-num); font-weight:900; color:var(--cream); line-height:.95; white-space:nowrap; filter:drop-shadow(0 4px 0 rgba(60,5,5,.45)); }
.pc-tix .tk .un { position:absolute; right:84px; top:30px; }
.pc-tix .seal { position:absolute; width:220px; height:220px; border:10px double var(--red); color:var(--red); display:grid; place-items:center;
  font-family:var(--f-serif); font-weight:900; font-size:80px; line-height:.95; text-align:center; background:var(--cream); }
.pc-tix .nt { position:absolute; }
""")
    title, sub = b.get("title", ""), b.get("sub", "")
    X.used_text.update(title + sub)
    far, land, front = stage(X, cid, gnd, sun=False)
    if P:
        tf = fit.fit_text(title, 1040, 260, 240, 150, max_lines=1)
        tx, ty = 40, 300
        boxes = [(-40, 560, W + 80, 480)] + [(-40, 1070 + 0 * k, W + 80, 300) for k in range(1, n)]      # 9:16: the tickets end above the caption (1396)
        if n > 2: boxes = [(-40, 560, W + 80, 400), (-40, 980, W + 80, 200), (-40, 1190, W + 80, 190)]
    else:
        tf = fit.fit_text(title, 1100, 160, 150, 100, max_lines=1)
        tx, ty = 96, 150
        tw = min(820, (W - 192 - (n - 1) * 50) // n)
        boxes = [(96 + k * (tw + 50), 400, tw, 380) for k in range(n)]
    tix = ""
    for k, it in enumerate(items):
        x, y, w, h = boxes[k]
        lb = fit.fit_text(it.get("label", ""), w - 400, 60, 44, max_lines=1)
        vt = f'{it.get("value", "")}'
        hi = 360 if k == 0 else 210
        vpx = min(hi, (w - 260) / max(0.5, fit.width(vt) * 1.1 + fit.width(it.get("unit", "")) * 0.26 + 0.2), (h - 90) / 1.0)
        rot = [-2.0, 1.6, -1.2][k % 3]
        tix += (f'<div class="tk lay near sh3" data-k="{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg);--tkc:{[RED, DEEP, RED][k % 3]}">'
                f'<div class="body"></div><div class="in"><div class="lb" style="font-size:{lb.px}px">{X.rich(it.get("label", ""))}'
                + '</div>'
                f'<div class="vl" style="font-size:{vpx:.0f}px"><span class="v">0</span><small style="font-size:.26em;margin-left:.2em">{X.rich(it.get("unit", ""))}</small></div></div>'
                + (f'<div class="chip nt" style="right:{160 if X.portrait else 84}px;bottom:28px;font-size:32px">{X.rich(it["note"])}</div>' if it.get("note") else "")
                + '</div>')
        X.used_text.update(it.get("label", "") + it.get("unit", "") + it.get("note", ""))
    sx, sy = (W - 260, boxes[0][1] - 70) if P else (boxes[-1][0] + boxes[-1][2] - 160, boxes[-1][1] - 110)
    inner = (f'<div class="lay mid fl sh1" style="left:{W - 420 if P else W - 700}px;top:{180 if P else 60}px;width:{620 if P else 700}px;height:{620 if P else 700}px">{flower(cid + "f", G["mid"], 10)}</div>'
             f'<div class="lay near ttl cut" style="left:{tx}px;top:{ty}px;font-size:{tf.px}px">{cutword(X, tf.lines[0] if tf.lines else "")}</div>'
             + (f'<div class="lay near"><div class="chip rd sub" style="left:{tx + 10}px;top:{ty + tf.px * 1.08 + 18:.0f}px;font-size:{36 if P else 32}px">{X.rich(sub)}</div></div>' if sub else "")
             + f'{tix}<div class="seal sh3 lay near" style="left:{sx}px;top:{sy}px">{X.rich(b.get("seal", "纪录"))}</div>')
    s = page(X, b, cid, t, d, inner, gnd, "pc-tix", far, land, front)
    unfold(X, f"{s} .ttl .c, {s} .ttl .n", t + 0.2, 0.55, 0.05)
    flip(X, f"{s} .sub", t + 0.5)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.6 + k * 0.9)
        X.tw(f'tl.from("{s} .tk[data-k=\'{k}\']", {{y:{H * 0.5:.0f}, rotation:{(-8 if k % 2 == 0 else 8)}, duration:0.6, ease:"expo.out"}}, {max(t + 0.3, tk - 0.45):.3f});')
        X.sfx(max(t + 0.3, tk - 0.45), "enter")
        v = it.get("value", 0)
        try: fv = float(str(v).replace(",", "")); dec = len(str(v).split(".")[1]) if "." in str(v) else 0
        except ValueError: fv, dec = None, 0
        if fv is not None: counter(X, f"{s} .tk[data-k='{k}'] .v", max(t + 0.35, tk - 0.3), 0, fv, dur=1.0, dec=dec)
        else: X.tw(f'tl.set("{s} .tk[data-k=\'{k}\'] .v", {{textContent:"{v}"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .tk[data-k=\'{k}\'] .nt", {{rotationY:-180, opacity:0, duration:0.5, ease:"power3.out"}}, {max(t + 0.5, tk + 0.6):.3f});')
    tsl = T(X, b, "at_seal", t, t + d * 0.75)
    X.tw(f'tl.fromTo("{s} .seal", {{scale:2.6, rotation:-30, opacity:0}}, {{scale:1, rotation:-9, opacity:1, duration:0.32, ease:"expo.out"}}, {tsl - 0.12:.3f});')
    X.sfx(tsl + 0.15, "slam")
    dolly(X, s, t, d + 0.7, [(".mid", 0.6), (".near", 1.1)], push=(1.0, 1.04))


def calendar(b, X, t, d, cid):
    """撕日历：前一页"除夕"被撕掉飞走，露出"大年初一"；剪纸大数字从铰链上展开，纸屑飞，鞭炮串摇。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    X.css("pc-cal", """
.pc-cal .cal { position:absolute; }
.pc-cal .pgx { position:absolute; inset:0; background:var(--cream); }
.pc-cal .pgx .band { position:absolute; left:0; right:0; top:0; height:22%; background:var(--red); display:grid; place-items:center; font-family:var(--f-display); font-weight:900; color:var(--cream); }
.pc-cal .pgx .day { position:absolute; left:0; right:0; top:24%; text-align:center; font-family:var(--f-num); font-weight:900; color:var(--red); line-height:1; }
.pc-cal .pgx .lbl { position:absolute; left:0; right:0; bottom:9%; text-align:center; font-family:var(--f-display); font-weight:700; color:var(--ink); }
.pc-cal .ring { position:absolute; top:-26px; width:34px; height:58px; border-radius:17px; background:#3b2a18; }
.pc-cal .fc { position:absolute; width:70px; }
.pc-cal .fc i { display:block; width:46px; height:76px; margin:0 auto 6px; border-radius:9px; background:linear-gradient(90deg, #b3151b, #d8342b 45%, #8f0f14);
  box-shadow:inset 0 9px 0 #d9a441, inset 0 -9px 0 #d9a441; }
.pc-cal .fc .str { position:absolute; left:34px; top:-60px; bottom:0; width:3px; background:#3b2a18; }
.pc-cal .bits i { position:absolute; width:18px; height:18px; display:block; }
""")
    far, land, front = stage(X, cid, gnd, tassels=False)
    if P:
        cx, cy, cw, ch = 380, 256, 580, 520      # 9:16: the calendar sits a little higher so the figure below clears it
        num, px, nw = bignum(X, b.get("big", ""), 920, 330, 480)      # 9:16: clear of the right-hand buttons
        nx, ny = 40, 880          # 9:16: the figure and its chip end above the caption (1396)
        fcx, fcy = 120, 300
    else:
        cx, cy, cw, ch = 300, 200, 520, 600
        num, px, nw = bignum(X, b.get("big", ""), 900, 280, 400)
        nx, ny = 930, 300
        fcx, fcy = W - 150, 150
    front_, back_ = b.get("front", {}), b.get("back", {})
    def pg(p, cls):
        bf = fit.fit_text(p.get("band", ""), cw - 60, ch * 0.18, 70, max_lines=1)
        lf = fit.fit_text(p.get("label", ""), cw - 60, ch * 0.12, 46, max_lines=1)
        X.used_text.update(p.get("band", "") + p.get("day", "") + p.get("label", ""))
        return (f'<div class="pgx {cls}" style="clip-path:{deckle(X.rand, 30, 0.6, "b")}"><div class="band" style="font-size:{bf.px}px">{X.rich(p.get("band", ""))}</div>'
                f'<div class="day" style="font-size:{int(ch * 0.42)}px">{X.rich(p.get("day", ""))}</div><div class="lbl" style="font-size:{lf.px}px">{X.rich(p.get("label", ""))}</div></div>')
    sub = b.get("sub", "")
    X.used_text.update(sub)
    sf = fit.fit_text(sub, (W - 112) if P else 760, 60, 38, max_lines=1)
    rnd = X.rand
    bits = "".join(f'<i style="left:{rnd.uniform(0, 100):.1f}%;top:{rnd.uniform(0, 60):.1f}%;background:{rnd.choice([CREAM, GOLD, RED2])};'
                   f'transform:rotate({rnd.uniform(0, 90):.0f}deg)"></i>' for _ in range(26))
    inner = (f'<div class="lay mid fl sh1" style="width:640px;height:640px;left:{W - 520 if not P else -280}px;top:{H - 620 if not P else 560}px">{flower(cid + "f", G["mid"], 10)}</div>'
             f'<div class="lay mid fc sh1" style="left:{fcx}px;top:{fcy}px"><i class="str"></i>{"<i></i>" * (8 if not P else 7)}</div>'
             f'<div class="cal lay near sh3" data-layout-allow-overlap style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px;transform:rotate({3 if P else 0}deg)">{pg(back_, "back")}{pg(front_, "front")}'
             f'<i class="ring" style="left:{cw * 0.25 - 17:.0f}px"></i><i class="ring" style="left:{cw * 0.75 - 17:.0f}px"></i></div>'
             + bigwrap(num, nx, ny, "near num")
             + (f'<div class="lay near"><div class="chip subc" style="left:{nx + 10}px;top:{ny + px * 1.05 + 14:.0f}px;font-size:{sf.px}px">{X.rich(sf.lines[0] if sf.lines else "")}</div></div>' if sub else "")
             + f'<div class="bits lay near" style="left:{nx}px;top:{ny - 120}px;width:{min(nw, W - nx)}px;height:{px + 200:.0f}px">{bits}</div>')
    s = page(X, b, cid, t, d, inner, gnd, "pc-cal", far, land, front)
    tt, tn = T(X, b, "at_tear", t, t + 0.4), T(X, b, "at_big", t, t + d * 0.6)
    X.tw(f'tl.from("{s} .cal", {{y:{H * 0.4:.0f}, duration:0.6, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.to("{s} .cal .front", {{y:-80, x:-420, rotation:-28, opacity:0, duration:0.75, ease:"power2.in", transformOrigin:"20% 0%"}}, {max(t + 0.5, tt):.3f});')
    X.sfx(max(t + 0.5, tt), "tear")
    unfold(X, f"{s} .num .c, {s} .num .n", tn - 0.3, 0.55, 0.06)
    X.sfx(tn - 0.2, "slam")
    flip(X, f"{s} .subc", tn + 0.3)
    X.tw(f'tl.fromTo("{s} .bits i", {{y:-40, opacity:0, scale:0.4}}, {{y:"+=240", rotation:"+=220", opacity:1, scale:1, duration:1.6, ease:"power1.in", stagger:{{each:0.03, from:"center"}}}}, {tn - 0.2:.3f});')
    sway(X, f"{s} .fc", t, d + 0.7, 5, 1.2)
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0}}, {{rotation:-28, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    dolly(X, s, t, d + 0.7, [(".mid", 0.6), (".near", 1.1)], push=(1.0, 1.05))


def share(b, X, t, d, cid):
    """占比 = 一朵窗花被剪掉一块：那一块被拎起来、投下更深的影子，剩下的窗花上露出底下的纸；巨大的剪纸百分比压在窗花脚下。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    pct = max(1.0, min(99.0, float(b.get("pct", 50))))
    far, land, front = stage(X, cid, gnd, sun=False)
    a1 = -90 + 360 * pct / 100
    def pt(a, r=118): return 100 + r * math.cos(math.radians(a)), 100 + r * math.sin(math.radians(a))
    x1, y1 = pt(-90); x2, y2 = pt(a1)
    big_arc = 1 if pct > 50 else 0
    wedge = f"M100,100 L{x1:.2f},{y1:.2f} A118,118 0 {big_arc} 1 {x2:.2f},{y2:.2f} Z"
    mid = math.radians(-90 + 180 * pct / 100)
    ox, oy = math.cos(mid), math.sin(mid)
    disc_col = RED if gnd != "red" else CREAM
    disc = flower(cid + "d", disc_col, 10, cutaway=wedge)
    pf = flower(cid + "p", CREAM if gnd != "red" else GOLD, 10)
    pf = pf[pf.index(">") + 1:-len("</svg>")]
    piece = (f'<svg viewBox="0 0 200 200"><defs><clipPath id="k{cid}"><path d="{wedge}"/></clipPath></defs>'
             f'<g clip-path="url(#k{cid})">{pf}</g></svg>')
    lab = b.get("label", ""); restl = b.get("rest", ""); kick = b.get("kicker", "")
    X.used_text.update(lab + restl + kick)
    if P:
        dx, dy, dd = 210, 500, 640
        kf = fit.fit_text(kick, W - 112, 60, 40, max_lines=1)
        lf = fit.fit_text(lab, W - 80, 200, 120, max_lines=1)
        num, px, nw = bignum(X, b.get("big", f"{pct:g}%"), 960, 360, 440, ign=True)      # 9:16: clear of the right-hand buttons; its line box runs below the ink
        nx, ny = 18, dy + dd - 150      # 9:16: the figure ends above the caption (1392)
        kx, ky, lx, ly = 56, 292, 40, 372
    else:
        dx, dy, dd = 180, 190, 680
        kf = fit.fit_text(kick, 900, 60, 44, max_lines=1)
        lf = fit.fit_text(lab, 900, 140, 100, max_lines=1)
        num, px, nw = bignum(X, b.get("big", f"{pct:g}%"), 880, 280, 380)
        nx, ny = 960, 420
        kx, ky, lx, ly = 960, 170, 960, 240
    rx, ry = dx + dd / 2 - math.cos(mid) * dd * 0.28, dy + dd / 2 - math.sin(mid) * dd * 0.28
    inner = (f'<div class="lay near"><div class="chip kick" style="left:{kx}px;top:{ky}px;font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else "")}</div></div>'
             f'<div class="lay near lab cut" style="left:{lx}px;top:{ly}px;font-size:{lf.px}px">{cutword(X, lf.lines[0] if lf.lines else "")}</div>'
             f'<div class="lay mid disc sh2" style="left:{dx}px;top:{dy}px;width:{dd}px;height:{dd}px">{disc}</div>'
             f'<div class="lay near piece sh3" style="left:{dx}px;top:{dy}px;width:{dd}px;height:{dd}px">{piece}</div>'
             + bigwrap(num, nx, ny, "near num")
             + (f'<div class="lay near"><div class="chip rd rest" style="left:{rx - 150:.0f}px;top:{ry - 30:.0f}px;font-size:{30 if P else 28}px;transform:rotate(-5deg)">{X.rich(restl)}</div></div>' if restl else ""))
    s = page(X, b, cid, t, d, inner, gnd, "pc-share", far, land, front)
    th = T(X, b, "at_hot", t, t + d * 0.45)
    flip(X, f"{s} .kick", t + 0.2)
    unfold(X, f"{s} .lab .c", t + 0.3, 0.5, 0.04)
    X.tw(f'tl.from("{s} .disc, {s} .piece", {{scale:0.6, rotation:-90, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("{s} .piece", {{x:{dd * (0.16 if P else -0.06):.0f}, y:{-dd * (0.32 if P else 0.22):.0f}, rotation:12, scale:1.04, duration:0.6, ease:"back.out(1.6)"}}, {th - 0.2:.3f});')
    X.sfx(th - 0.2, "tear")
    unfold(X, f"{s} .num .c, {s} .num .n", th - 0.1, 0.55, 0.06)
    if restl: flip(X, f"{s} .rest", th + 0.6)
    X.tw(f'tl.fromTo("{s} .disc", {{rotation:0}}, {{rotation:6, duration:{d + 0.7:.2f}, ease:"none"}}, {t + 1.0:.3f});')
    dolly(X, s, t, d + 0.7, [(".mid", 0.6), (".near", 1.1)], push=(1.0, 1.05))


FLAME = "M50 160 C10 130 18 92 40 70 C38 92 50 100 56 96 C48 66 60 30 86 6 C80 40 96 58 102 78 C108 64 106 52 102 40 C128 70 132 116 104 144 C94 156 74 164 50 160 Z"


def banner(b, X, t, d, cid):
    """卷轴横幅从中间展开写出片名；下面的数字是在红纸上镂空、透出金纸；后面一排纸火焰从纸景里升起、轻轻摇。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    X.css("pc-ban", """
.pc-ban .scroll { position:absolute; }
.pc-ban .scroll .paper { position:absolute; inset:0; background:var(--cream); border-top:10px solid var(--gold); border-bottom:10px solid var(--gold);
  display:grid; place-items:center; font-family:var(--f-display); font-weight:900; color:var(--red); white-space:nowrap; }
.pc-ban .scroll .rod { position:absolute; top:-20px; bottom:-20px; width:38px; border-radius:19px; background:linear-gradient(90deg, #6e0b0f, #b3151b 50%, #6e0b0f); }
.pc-ban .fls { position:absolute; left:0; right:0; }
.pc-ban .fls svg { position:absolute; bottom:0; transform-origin:50% 100%; }
""")
    far, land, front = stage(X, cid, gnd)
    title = b.get("title", ""); sub = b.get("sub", "")
    X.used_text.update(title + sub)
    if P:
        tf = fit.fit_text(title, W - 260, 130, 96, max_lines=1)
        sw, sx, sy, sh = W - 120, 60, 320, 170
        num, px, nw = bignum(X, b.get("big", ""), 930, 340, 480, "hole")      # 9:16: clear of the right-hand buttons
        nx, ny = 10, 650
        flb, flh, k, fw_ = H * 0.2, H * 0.42, 5, 280
    else:
        tf = fit.fit_text(title, 1100, 120, 92, max_lines=1)
        sw, sx, sy, sh = 1300, (W - 1300) // 2, 180, 150
        num, px, nw = bignum(X, b.get("big", ""), 1000, 280, 380, "hole")
        nx, ny = (W - nw) / 2, 380
        flb, flh, k, fw_ = H * 0.14, H * 0.5, 7, 230
    cols = [GOLD, RED2, CREAM, "#8f0f14", GOLD, RED2, CREAM]
    fls = "".join(f'<svg class="sh1" data-k="{j}" viewBox="0 0 140 170" style="left:{(j + 0.5) * W / k - fw_ / 2:.0f}px;width:{fw_ + 60 * (j % 2)}px"><path d="{FLAME}" fill="{cols[j % len(cols)]}"/></svg>' for j in range(k))
    back = "".join(f'<svg data-k="{j}" viewBox="0 0 140 170" style="left:{j * W / (k - 1) - fw_ * 0.7:.0f}px;width:{fw_ * 1.4:.0f}px"><path d="{FLAME}" fill="{["#8f0f14", DEEP][j % 2]}"/></svg>' for j in range(k))
    sf = fit.fit_text(sub, W - 192, 60, 40, max_lines=1) if sub else None
    inner = (f'<div class="fls back mid" style="bottom:{flb:.0f}px;height:{flh * 1.2:.0f}px">{back}</div><div class="fls front mid2" style="bottom:{flb - 40:.0f}px;height:{flh:.0f}px">{fls}</div>'
             f'<div class="scroll lay near sh3" data-layout-allow-overlap style="left:{sx}px;top:{sy}px;width:{sw}px;height:{sh}px"><div class="paper" style="font-size:{tf.px}px">{X.rich(tf.lines[0] if tf.lines else "")}</div>'
             f'<i class="rod l" style="left:-19px"></i><i class="rod r" style="right:-19px"></i></div>'
             + bigwrap(num, nx, ny, "near num")
             + (f'<div class="lay near"><div class="chip subc" style="left:{nx + 10:.0f}px;top:{ny + px * 1.04 + 10:.0f}px;font-size:{sf.px}px">{X.rich(sf.lines[0] if sf.lines else "")}</div></div>' if sf else ""))
    s = page(X, b, cid, t, d, inner, gnd, "pc-ban", far, land, front)
    tn = T(X, b, "at_big", t, t + d * 0.55)
    X.tw(f'tl.fromTo("{s} .scroll .paper", {{clipPath:"inset(0 50% 0 50%)"}}, {{clipPath:"inset(0 0% 0 0%)", duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .scroll .l", {{x:{sw / 2:.0f}}}, {{x:0, duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .scroll .r", {{x:{-sw / 2:.0f}}}, {{x:0, duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.sfx(t + 0.3, "enter")
    X.tw(f'tl.from("{s} .fls.back svg", {{scaleY:0, duration:0.8, ease:"back.out(1.5)", stagger:{{each:0.05, from:"edges"}}}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .fls.front svg", {{scaleY:0, duration:0.7, ease:"back.out(1.7)", stagger:{{each:0.06, from:"center"}}}}, {t + 0.2:.3f});')
    rep = max(1, int((d + 0.7) / 0.9))
    for row, ph in (("front", 0.0), ("back", 0.22)):
        for j in range(k):
            X.tw(f'tl.fromTo("{s} .fls.{row} svg[data-k=\'{j}\']", {{scaleY:1, skewX:0}}, {{scaleY:{1.06 + 0.04 * (j % 3):.2f}, skewX:{(-3 if (j + (row == "back")) % 2 else 3)}, duration:0.45, ease:"sine.inOut", yoyo:true, repeat:{rep * 2}}}, {t + 0.9 + ph + 0.07 * j:.3f});')
    if sf: flip(X, f"{s} .subc", tn + 0.35)
    unfold(X, f"{s} .num .c, {s} .num .n", tn - 0.35, 0.55, 0.06)
    X.sfx(tn - 0.3, "slam")
    dolly(X, s, t, d + 0.7, [(".mid", 0.5), (".mid2", 0.8), (".near", 1.2)], push=(1.06, 1.0))


def stacks(b, X, t, d, cid):
    """排行 = 折出来的纸台阶：每一级是一条折过的纸（正面镂空花格、顶面浅、侧面深），高度按数值，从纸景后面升起来；冠军顶上一朵窗花。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    items = b.get("items", [])[:6] or [{"name": "—", "value": 1}]
    n = len(items)
    X.css("pc-stk", """
.pc-stk .col { position:absolute; }
.pc-stk .col svg { position:absolute; left:0; bottom:0; overflow:visible; }
.pc-stk .col .lb { position:absolute; left:-20px; right:-20px; text-align:center; }
.pc-stk .col .rk { display:inline-block; font-family:var(--f-num); font-weight:900; font-size:30px; color:var(--red); background:var(--cream); padding:2px 14px; }
.pc-stk .col .nm { font-family:var(--f-display); font-weight:900; color:var(--pfg); white-space:nowrap; margin-top:8px; }
.pc-stk .col .vl { margin-top:4px; }
.pc-stk .crown { position:absolute; width:120px; height:120px; }
""")
    far, land, front = stage(X, cid, gnd, tassels=False)
    vmax = max(float(it.get("value", 0) or 0) for it in items) or 1
    if P: base_y, hmax, area_x, area_w = 1520, 700, 50, W - 170      # 9:16: the steps end clear of the right-hand buttons
    else: base_y, hmax, area_x, area_w = 930, 330, 160, W - 320
    gap = 34 if P else 50
    cw = min(330, (area_w - gap * (n - 1)) / n)
    x0 = area_x + (area_w - n * cw - (n - 1) * gap) / 2
    kick = b.get("kicker", "")
    X.used_text.update(kick)
    kf = fit.fit_text(kick, (W - 112) if P else 1000, 60, 44 if P else 40, max_lines=1)
    faces = [(RED, "#e0473a", DEEP), (GOLD, "#ecc271", GOLD2), (CREAM, "#fffaf0", "#cbbd9f")]
    cols = ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        h = max(60, hmax * v / vmax); x = x0 + k * (cw + gap)
        fc, tc, sc = faces[k % 3]
        dep = 34
        lat = "".join(f'<path d="M{cw * (0.18 + 0.32 * c):.0f} {hh:.0f} l{cw * 0.07:.0f} 22 l-{cw * 0.07:.0f} 22 l-{cw * 0.07:.0f} -22 z"/>'
                      for c in range(3) for hh in range(70, int(h) - 30, 74))
        step = (f'<svg width="{cw + dep:.0f}" height="{h + dep:.0f}" viewBox="0 {-dep} {cw + dep:.0f} {h + dep:.0f}"><defs><mask id="s{cid}{k}"><rect x="0" y="0" width="{cw:.0f}" height="{h:.0f}" fill="#fff"/><g fill="#000">{lat}</g></mask></defs>'
                f'<path d="M0 0 L{dep} {-dep} L{cw + dep:.0f} {-dep} L{cw:.0f} 0 Z" fill="{tc}"/>'
                f'<path d="M{cw:.0f} 0 L{cw + dep:.0f} {-dep} L{cw + dep:.0f} {h - dep:.0f} L{cw:.0f} {h:.0f} Z" fill="{sc}"/>'
                f'<rect x="0" y="0" width="{cw:.0f}" height="{h:.0f}" fill="{fc}" mask="url(#s{cid}{k})"/></svg>')
        nm = it.get("name", ""); lv = str(it.get("label", it.get("value", "")))
        X.used_text.update(nm + lv)
        nf = fit.fit_text(nm, cw + 30, 100, 44 if P else 40, max_lines=2)
        vpx = min((200 if P else 150) if k == 0 else (110 if P else 90), (cw + 60) / max(0.5, fit.width(lv) * 1.1))
        crown = f'<div class="crown sh2" style="left:{cw / 2 - 60:.0f}px;bottom:{h + dep + 6:.0f}px">{flower(cid + "cr", GOLD if fc != GOLD else RED, 8)}</div>' if k == 0 else ""
        cols += (f'<div class="col lay near sh2" data-k="{k}" style="left:{x:.0f}px;top:{base_y - h:.0f}px;width:{cw:.0f}px;height:{h:.0f}px">{step}{crown}'
                 f'<div class="lb" style="bottom:{h + dep + (138 if k == 0 else 14):.0f}px"><span class="rk">{k + 1}</span>'
                 f'<div class="nm" style="font-size:{nf.px}px;line-height:1.12">{"<br>".join(X.rich(x_) for x_ in nf.lines)}</div>'
                 f'<div class="vl cut" style="font-size:{vpx:.0f}px">{cutword(X, lv)}</div></div></div>')
    inner = (f'<div class="lay mid fl sh1" style="width:760px;height:760px;left:{W - 520 if P else W - 640}px;top:{260 if P else 60}px">{flower(cid + "f", G["mid"], 12)}</div>'
             f'<div class="lay near"><div class="chip kick" style="left:{56 if P else 96}px;top:{290 if P else 150}px;font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else "")}</div></div>{cols}')
    s = page(X, b, cid, t, d, inner, gnd, "pc-stk", far, land, front)
    flip(X, f"{s} .kick", t + 0.3)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.5 + min(0.8, max(0.25, (d - 1.4) / n)) * k)     # uncued items share the beat
        X.tw(f'tl.from("{s} .col[data-k=\'{k}\']", {{y:{hmax + 300}, duration:0.7, ease:"expo.out"}}, {max(t + 0.3, tk - 0.5):.3f});')
        X.tw(f'tl.from("{s} .col[data-k=\'{k}\'] .lb", {{rotationY:-180, opacity:0, duration:0.55, ease:"power3.out"}}, {max(t + 0.5, tk):.3f});')
        X.sfx(max(t + 0.35, tk - 0.5), "paper" if k else "enter")
    X.tw(f'tl.from("{s} .crown", {{scale:0, rotation:-90, duration:0.6, ease:"back.out(2)"}}, {T(X, items[0], "at", t, t + 0.5) + 0.5:.3f});')
    X.tw(f'tl.fromTo("{s} .crown, {s} .fl", {{rotation:0}}, {{rotation:40, duration:{d + 0.7:.2f}, ease:"none"}}, {t + 1:.3f});')
    dolly(X, s, t, d + 0.7, [(".mid", 0.6), (".near", 1.0)], push=(1.04, 1.0))


def thesis(b, X, t, d, cid):
    """判断句：上一句贴米色纸字，"平均"被一条纸条划掉；下一句在红纸上镂空、透出金纸。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    X.css("pc-th", """
.pc-th .tx { position:absolute; }
.pc-th .ln { display:block; white-space:nowrap; }
.pc-th .st { position:relative; display:inline-block; }
.pc-th .st .strip { position:absolute; left:-4%; right:-4%; top:44%; height:.17em; background:var(--gold); transform-origin:0 50%; transform:rotate(-4deg);
  filter:drop-shadow(0 6px 14px rgba(0,0,0,.28)); }
""")
    far, land, front = stage(X, cid, gnd)
    l1, l2, stw = b.get("l1", ""), b.get("l2", ""), b.get("strike", "")
    X.used_text.update(l1 + l2)
    bw = (W - 100) if P else (W - 192)
    bh = 480 if P else 520          # 9:16: the two statements end above the caption (1392)
    f1 = fit.fit_text(l1, bw, bh, 240 if P else 170, 170 if P else 110, max_lines=2 if P else 1)
    f2 = fit.fit_text(l2, bw, bh, 240 if P else 170, 170 if P else 110, max_lines=2 if P else 1)
    def mark(line):
        h = cutword(X, line)
        if stw and stw in line:
            a = line.index(stw)
            h = cutword(X, line[:a]) + f'<span class="st">{cutword(X, stw)}<i class="strip"></i></span>' + cutword(X, line[a + len(stw):])
        return h
    x0 = 46 if P else 96
    y1 = 320 if P else int(H * 0.22); y2 = y1 + int(f1.px * 1.12 * f1.n) + (60 if P else 50)
    inner = (f'<div class="lay mid fl sh1" style="width:{1000 if P else 900}px;height:{1000 if P else 900}px;left:{(W - (1000 if P else 900)) // 2}px;top:{(H - 1000) // 2 if P else (H - 900) // 2}px">{flower(cid + "f", G["mid"], 12)}</div>'
             f'<div class="tx lay near cut t1" style="left:{x0}px;top:{y1}px;font-size:{f1.px}px;line-height:1.12">{"".join(f"<span class=ln>{mark(x)}</span>" for x in f1.lines)}</div>'
             f'<div class="tx lay near cut hole t2" style="left:{x0}px;top:{y2}px;font-size:{f2.px}px;line-height:1.12">{"".join(f"<span class=ln>{cutword(X, x)}</span>" for x in f2.lines)}</div>')
    s = page(X, b, cid, t, d, inner, gnd, "pc-th", far, land, front)
    ts, te = T(X, b, "at_strike", t, t + d * 0.35), T(X, b, "at_em", t, t + d * 0.7)
    unfold(X, f"{s} .t1 .c", t + 0.2, 0.55, 0.05)
    X.tw(f'tl.from("{s} .strip", {{scaleX:0, duration:0.35, ease:"power3.out"}}, {ts:.3f});')
    X.sfx(ts, "tear")
    X.tw(f'tl.from("{s} .t2 .c", {{clipPath:"inset(0 0 100% 0)", duration:0.4, ease:"power2.out", stagger:0.06}}, {max(t + 0.6, te - 0.5):.3f});')
    X.sfx(te, "pop")
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0, scale:0.9}}, {{rotation:30, scale:1.05, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    dolly(X, s, t, d + 0.7, [(".mid", 0.5), (".near", 1.1)], push=(1.0, 1.04))


def outro(b, X, t, d, cid):
    """落版：一枚红色剪纸印章 + 一句定位 + 关注纸签；主持人成了一张朱砂剪影贴上来。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    gnd = ground(X); G = GROUNDS[gnd]
    X.css("pc-out", """
.pc-out .seal { position:absolute; background:var(--red); color:var(--cream); display:grid; place-items:center; text-align:center;
  font-family:var(--f-display); font-weight:900; line-height:1.02; box-shadow:inset 0 0 0 12px var(--red), inset 0 0 0 17px var(--cream); }
.pc-out .sub { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--deep); white-space:nowrap; }
.pc-out .cta { position:absolute; font-size:44px; padding:14px 32px 16px; }
""")
    far, land, front = stage(X, cid, gnd, sun=False)
    sz = 650
    sx, sy = (150, 170) if not P else (40, 300)
    tl_ = b.get("title", X.channel)
    half = (len(tl_) + 1) // 2
    sub = b.get("sub", "")
    X.used_text.update(tl_ + sub + b.get("cta", ""))
    sf = fit.fit_text(sub, 520 if not P else (W - 112), 90, 64, max_lines=1)
    tx = sx if P else sx + sz + 70
    host = SILHOUETTE if X.v.get("meta", {}).get("mascot") else ""
    fs_ = 860 if not P else 1000
    inner = (f'<div class="lay mid fl sh1" style="left:{(W - 900) if not P else 260}px;top:{180 if not P else 740}px;width:{fs_}px;height:{fs_}px">{flower(cid + "f", G["mid"], 12)}</div>'
             f'<div class="seal lay near sh3" style="left:{sx}px;top:{sy}px;width:{sz}px;height:{sz}px;font-size:{int(sz * 0.27)}px">{X.rich(tl_[:half])}<br>{X.rich(tl_[half:])}</div>'
             f'<div class="sub lay near" style="left:{tx}px;top:{(sy + sz + 60) if P else 420}px;font-size:{sf.px}px">{X.rich(sf.lines[0] if sf.lines else "")}</div>'
             f'<div class="lay near"><div class="chip rd cta" style="left:{tx}px;top:{((sy + sz + 60) if P else 420) + sf.px + 50:.0f}px">{X.rich(b.get("cta", ""))}</div></div>{host}')
    s = page(X, b, cid, t, d, inner, gnd, "pc-out", far, land, front)
    X.tw(f'tl.fromTo("{s} .seal", {{scale:2.2, rotation:-20, opacity:0}}, {{scale:1, rotation:-4, opacity:1, duration:0.4, ease:"expo.out"}}, {t + 0.25:.3f});')
    X.sfx(t + 0.35, "slam")
    unfold(X, f"{s} .sub", t + 0.6, 0.5)
    flip(X, f"{s} .cta", t + 0.85)
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0}}, {{rotation:24, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    dolly(X, s, t, d, [(".mid", 0.6), (".near", 1.0)], push=(1.0, 1.03))


SCENES = {"hook": hook, "tickets": tickets, "calendar": calendar, "share": share, "banner": banner, "stacks": stacks, "thesis": thesis, "outro": outro}


# ---------------------------------------------------------------- effects in this style (gallery cards / fx beats)
# four paper stocks for the effect themes: rice paper, festive red, indigo-dyed (蓝印) and gold foil (金纸)
STYLE["fx_themes"] = {
    "paper": {"bg": "#d9a441", "fg": "#1e1b18", "muted": "#5e3f10", "accent": "#b3151b", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "#e2d6c2"},
    "red":   {"bg": "#b3151b", "fg": "#fbf7ee", "muted": "rgba(251,247,238,.82)", "accent": "#f2c14e", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "rgba(251,247,238,.3)"},
    "ink":   {"bg": "#1d2a5e", "fg": "#f3ede1", "muted": "#a9b3c6", "accent": "#e8543f", "card": "#26324d", "card-fg": "#f3ede1", "line": "#34405c"},
    "lemon": {"bg": "#e9b949", "fg": "#2a1a0e", "muted": "#5e3f10", "accent": "#b3221a", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "rgba(42,26,14,.2)"},
}
# the cut-paper frame around a card, per stock: frame band, corner flowers (角花), header tag, caption strip, keyword marker, effect-id stub
FRAME = {
    "paper": {"frame": "#b3151b", "corner": "#d6a23c", "tag": "#b3151b", "tag-fg": "#fbf7ee", "tag-b": "#ffd77a", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#b3151b", "em-fg": "#fbf7ee", "stub": "#1e1b18", "stub-fg": "#fbf7ee"},
    "red":   {"frame": "#fbf7ee", "corner": "#f2c14e", "tag": "#fbf7ee", "tag-fg": "#1e1b18", "tag-b": "#b3151b", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#b3151b", "em-fg": "#fbf7ee", "stub": "#1e1b18", "stub-fg": "#fbf7ee"},
    "ink":   {"frame": "#d6a23c", "corner": "#e8543f", "tag": "#d6a23c", "tag-fg": "#1d2a5e", "tag-b": "#8d1711", "cap": "#f3ede1", "cap-fg": "#1d2a5e",
              "em": "#e8543f", "em-fg": "#fbf7ee", "stub": "#f3ede1", "stub-fg": "#1d2a5e"},
    "lemon": {"frame": "#b3221a", "corner": "#fbf7ee", "tag": "#b3221a", "tag-fg": "#fbf7ee", "tag-b": "#ffd77a", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#b3221a", "em-fg": "#fbf7ee", "stub": "#2a1a0e", "stub-fg": "#fbf7ee"},
}


def _b64svg(svg):
    import base64
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'


_WM = _b64svg(flower("wm", "#000", 12).replace("<svg ", "<svg xmlns='http://www.w3.org/2000/svg' ", 1))
_LACE = _b64svg("<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><path fill='#000' fill-rule='evenodd' "
                "d='M0 0H40V40H0Z M10 4.5a5.5 5.5 0 1 0 .01 0Z M30 24.5a5.5 5.5 0 1 0 .01 0Z M30 9l3 3-3 3-3-3Z M10 29l3 3-3 3-3-3Z'/></svg>")
_SHADE = "color-mix(in srgb, var(--bg) 58%, #2a0a06)"      # the paper's own drop: a darker shade of whatever stock it sits on

FX_CSS = r"""
/* the effect's ground is a sheet of paper: fibre texture + a large faint 窗花 cut into the corner */
.fx { background-image:__NOISE__ !important; background-size:340px !important; }
.fx::before { content:""; position:absolute; width:86vmin; height:86vmin; right:-22vmin; bottom:-30vmin; background:var(--fg); opacity:.06;
  -webkit-mask:__WM__ center/contain no-repeat; mask:__WM__ center/contain no-repeat; pointer-events:none; }
#root.v .fx::before { right:-30vmin; bottom:auto; top:13%; }
/* type is cut from paper: every headline casts a solid paper drop plus a soft shadow */
.fx .big, .fx .op .op-ep, .fx .op .op-t, .fx .dn .dnc b, .fx .iu .iub, .fx .nt-t, .fx .dn .dnt strong, .fx .iu .iutx {
  text-shadow:0 .05em 0 __SHADE__, 0 .12em .2em rgba(40,10,5,.24); }
.fx .big { letter-spacing:.01em; }
.fx .col > .sub { background:var(--card); color:var(--card-fg); padding:.7vmin 2vmin .8vmin; letter-spacing:.24em; transform:rotate(-1deg);
  box-shadow:0 .5vmin 0 __SHADE__, 0 1.4vmin 2vmin rgba(40,10,5,.2); font-family:var(--f-body); font-weight:700; }
/* burst: rays become cut paper strips, the ring a punched lace circle, the dots little paper diamonds */
.fx .ray b { border-radius:0; width:1.3vmin; left:-.65vmin; box-shadow:0 .5vmin 0 __SHADE__; }
.fx .ray:nth-child(even) b { background:var(--fg); height:5vmin; }
.fx .bu .ring { border:1.5vmin dotted var(--accent); }
.fx .bu .dot { border-radius:.2vmin; background:var(--accent); width:2.4vmin; height:2.4vmin; transform:rotate(var(--a)) translateY(-22vmin) rotate(45deg); box-shadow:0 .4vmin 0 __SHADE__; }
/* gooey: two paper discs with hollow-cut lace, the merged neck stays paper */
.fx .gw { filter:drop-shadow(0 .7vmin 0 __SHADE__) drop-shadow(0 1.8vmin 1.6vmin rgba(40,10,5,.25)); }
.fx .go { -webkit-mask:__LACE__ 0 0/4.2vmin 4.2vmin repeat; mask:__LACE__ 0 0/4.2vmin 4.2vmin repeat; }
/* donut: the ring is a paper band with a scalloped lace border around it */
.fx .dn .dnr svg { filter:drop-shadow(0 .6vmin 0 __SHADE__) drop-shadow(0 1.6vmin 1.6vmin rgba(40,10,5,.22)); }
.fx .dn .dnr::before { content:""; position:absolute; inset:-5%; border-radius:50%; border:1.2vmin dotted var(--accent); opacity:.55; }
.fx .dn .dntr { stroke:color-mix(in srgb, var(--fg) 14%, var(--bg)); }
.fx .dn .dnlg div i, .fx .dn .dnt i.sw { border-radius:0; transform:rotate(45deg) scale(.86); }
/* maps: the country is a cut-out laid on the page; labels are paper tags; pins are diamonds */
.fx .wpm svg { filter:drop-shadow(0 .45vmin 0 color-mix(in srgb, __SHADE__ 55%, transparent)); }
.fx .wpm-p { fill:color-mix(in srgb, var(--card) 70%, var(--bg)); }
.fx .wpm-lb { border-radius:0; background:var(--card); color:var(--card-fg); box-shadow:0 .35vmin 0 __SHADE__; }
.fx .wpm-pin i { border-radius:.2vmin; transform:rotate(45deg); }
.fx .wpm-r i { border-radius:0; }
.fx .wp-mock { border-radius:0 !important; }
/* icon units: the lit share is stamped on a paper slip */
.fx .iu .iuper { background:var(--card); color:var(--card-fg); padding:.4em .8em; box-shadow:0 .4vmin 0 __SHADE__; }
.fx .iu .iulg i { border-radius:0; transform:rotate(45deg) scale(.8); }
/* opener: no glossy sweep on paper; bars cast paper drops */
.fx .op .op-sweep { display:none; }
.fx .op .op-bar { box-shadow:0 .5vmin 0 __SHADE__; }
/* share card: a paper card with a printed red border line, no screen scanlines */
.fx .sc .sc-c { border-radius:0; box-shadow:0 .7vmin 0 __SHADE__, 0 3vmin 5vmin rgba(40,10,5,.25); outline:.45vmin solid var(--accent); outline-offset:-2.2vmin; }
.fx .sc .sc-c::before { background:__NOISE__; background-size:340px; }
/* next teaser: the cover is a mounted print with a paper border; the RGB glitch and scanline stay off */
.fx .nt .nt-cv { border-radius:0; border:1.1vmin solid #fbf7ee; box-shadow:0 .7vmin 0 __SHADE__, 0 3vmin 5vmin rgba(0,0,0,.3); }
.fx .nt .nt-cv .rgb, .fx .nt .nt-cv .scan { display:none; }
.fx .nt .nt-cv .ph { background:var(--accent); background-image:__NOISE__; }
.fx .nt .nt-cv .ph b { color:rgba(40,10,5,.16); }
.fx .nt .nt-cv .ph i { color:#fbf7ee; -webkit-text-stroke:0; text-shadow:0 .05em 0 rgba(60,10,5,.45), 0 .12em .2em rgba(40,10,5,.3); }
.fx .nt .nt-tape { opacity:.94; }
.fx .nt .nt-k { border-radius:0; box-shadow:0 .4vmin 0 __SHADE__; }
.fx .nt .nt-h span { border-radius:0; border-style:dashed; }
.fx .nt .nt-w { border-radius:0; transform:rotate(-2deg); box-shadow:0 .5vmin 0 __SHADE__; }
.fx .sc .sc-hint { border-radius:0; transform:rotate(2deg); box-shadow:0 .4vmin 0 __SHADE__; }
.fx .sc .sc-flash { border-radius:0; }

/* the card frame (FX_FRAME): scalloped paper border, 角花 corners, paper header tag, caption strip, footer slip */
.ctx.pcx .frm { position:absolute; inset:0; width:100%; height:100%; filter:drop-shadow(0 6px 0 rgba(40,10,5,.22)) drop-shadow(0 10px 12px rgba(40,10,5,.2)); }
.ctx.pcx .cf { position:absolute; filter:drop-shadow(0 4px 0 rgba(40,10,5,.25)); }
.ctx.pcx .hd { left:128px; right:128px; top:40px; height:auto; border:none; display:flex; justify-content:space-between; align-items:center; }
.ctx.pcx .hd .tag { background:var(--pc-tag); color:var(--pc-tag-fg); font-family:var(--f-display); font-weight:400; font-size:24px; padding:7px 16px 9px;
  box-shadow:0 4px 0 rgba(40,10,5,.25); transform:rotate(-1.2deg); white-space:nowrap; }
.ctx.pcx .hd .tag b { color:var(--pc-tag-b); font-weight:400; margin-right:10px; letter-spacing:0; }
.ctx.pcx .hd .tag span { opacity:1; margin-left:0; }
.ctx.pcx .hd .fxid { background:var(--pc-stub); color:var(--pc-stub-fg); font-family:var(--f-mono); font-size:17px; padding:4px 12px; transform:rotate(2deg);
  box-shadow:0 3px 0 rgba(40,10,5,.25); }
.ctx.pcx .cap { bottom:76px; }
.ctx.pcx .cap > span { background:var(--pc-cap); color:var(--pc-cap-fg); border-radius:2px; font-family:var(--f-body); font-weight:800; transform:rotate(-.8deg);
  box-shadow:0 5px 0 var(--pc-frame), 0 14px 20px rgba(40,10,5,.25); }
.ctx.pcx .cap .em .emt { background:var(--pc-em); color:var(--pc-em-fg); padding:0 .16em; box-shadow:0 3px 0 rgba(40,10,5,.25); }
.ctx.pcx .ft { left:128px; right:128px; bottom:38px; opacity:1; color:var(--fg); font-size:15px; }
.ctx.pcx .ft > div { background:color-mix(in srgb, var(--bg) 82%, transparent); box-shadow:0 0 0 5px color-mix(in srgb, var(--bg) 82%, transparent); }
#root.v .ctx.pcx .hd { left:56px; right:56px; top:206px; } #root.v .ctx.pcx .ft { left:56px; right:120px; top:1462px; bottom:auto; font-size:17px; flex-direction:column; align-items:flex-start; gap:6px; }   /* 9:16: label and source stacked, clear of the right-hand buttons */
#root.v .ctx.pcx .cap { top:1330px; bottom:auto; padding:0 120px; }
"""
STYLE["css"] = (FX_CSS.replace("__NOISE__", noise_bg(0.13, 9)).replace("__WM__", _WM).replace("__LACE__", _LACE)
                .replace("__SHADE__", _SHADE))


def frame_path(W, H, m, r):
    """a full-page band with a scalloped inner edge (evenodd): the paper border a 窗花 card is mounted in."""
    def edge(L):
        n = max(1, round(L / (2 * r)))
        return n, L / (2 * n)
    d = f"M0 0H{W}V{H}H0Z M{m} {m}"
    n, rr = edge(W - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 {2 * rr:.2f} 0" for _ in range(n))
    n, rr = edge(H - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 0 {2 * rr:.2f}" for _ in range(n))
    n, rr = edge(W - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 {-2 * rr:.2f} 0" for _ in range(n))
    n, rr = edge(H - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 0 {-2 * rr:.2f}" for _ in range(n))
    return d + "Z"


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect card in papercut: the effect is mounted in a red (cream / gold) paper border with
    scalloped edges and four 角花 corner flowers; the header is a paper tag, the spoken line a tilted paper strip with
    the keyword cut from red paper, the footnote a small slip."""
    P, W, H = X.portrait, X.W, X.H
    th = p.get("theme") if p.get("theme") in FRAME else "paper"
    fr = FRAME[th]
    m, r, R = (20, 12, 78) if P else (18, 12, 86)
    sty = parts["sty"] + ";" + ";".join(f"--pc-{k}:{v}" for k, v in fr.items())
    corners = "".join(f'<div class="cf" data-k="{k}" style="left:{x - R}px;top:{y - R}px;width:{2 * R}px;height:{2 * R}px">{flower(f"{cid}k{k}", fr["corner"], 8)}</div>'
                      for k, (x, y) in enumerate([(m, m), (W - m, m), (W - m, H - m), (m, H - m)]))
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + f'<svg class="frm" viewBox="0 0 {W} {H}" preserveAspectRatio="none"><path d="{frame_path(W, H, m, r)}" fill="{fr["frame"]}" fill-rule="evenodd"/></svg>{corners}'
             + f'<div class="hd"><div class="tag"><b>{X.rich(X.channel)}</b><span>{parts["topic"]}</span></div><div class="fxid">{parts["fxid"]}</div></div>'
             + f'<div class="cap"><span style="font-size:{parts["cap_px"]}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx pcx{' photo' if parts['photo'] else ''}", 30, track=20, sty=sty)
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .cap > span", {{y:28, rotation:-5, opacity:0, duration:0.42, ease:"back.out(1.8)"}}, {t + 0.08:.3f});')
    X.tw(f'tl.from("{s} .hd .tag", {{y:-90, rotation:-8, duration:0.45, ease:"back.out(1.8)"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .hd .fxid", {{y:-90, rotation:10, duration:0.45, ease:"back.out(1.8)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .cf", {{rotation:0}}, {{rotation:20, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


# the subtitle as a cream paper strip with a scalloped left end and vermilion Song text; 9:16 sits it on the land strip.
# the host as a vermilion paper-cut silhouette (filter #pcsil lives in the outro page)
STYLE["css"] += """
.st-papercut .cap .cp { font-family:var(--f-cap); letter-spacing:.04em; line-height:1.3;
  -webkit-mask:radial-gradient(circle at 0 50%, transparent 9px, #000 9.5px) 0 0/18px 24px repeat-y, linear-gradient(#000 0 0) 18px 0/calc(100% - 18px) 100% no-repeat; }
.st-papercut .cap .em .emt { color:var(--cap-em); }
#root.v.st-papercut { --cap-bottom:456px; }   /* 9:16: caption above the source line, both above the platform's bottom bar */
#root.st-papercut .mascot.mf-papercut { filter:url(#pcsil) drop-shadow(0 6px 14px rgba(0,0,0,.28)) drop-shadow(0 2px 0 rgba(60,5,5,.3)); }
"""
