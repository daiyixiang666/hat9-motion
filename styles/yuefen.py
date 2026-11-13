"""yuefen · 月份牌国货 —— 1920–30 年代上海月份牌和国货包装的语言：一张老石印卡片，每一页都是同一套版式重新装扮。

底是石印卡纸：玉绿 #2f6f62（默认），轮换淡青瓷 #cfe0d2 和深枣红 #6b1f2a；金色只用于细线。色块是石印的柔和砂点
（湍流驱动的细点，不是平涂矢量，也不是网点），色块和轮廓线错开 2–3 px 套印；纸上有零星霉斑和一道横向折痕，暗角不超过 6%。

竖屏固定结构：外框是两道金线（4 px + 1.5 px，相距 14 px，内缩 36 px），四角是 Art Deco 阶梯角和扇形放射纹；
上方 y 210–430 是一块象牙色阶梯端头题版，写民国美术字味的粗宋标题（110–150 px，字距 0.08em，6 px 枣红内影）；
中间 y 470–1230 是一扇椭圆或拱形窗（象牙色 10 px 窗框 + 金色内线），窗后 24 道放射光，窗里是这一页的物件插画或大数字；
下方 y 1250–1500 是一块商品标签票版，装字幕（象牙色小票，枣红宋体）和出处；y 1520 以下是一条月历格子花纹和外框的下角。

图表都是这个世界里的东西：占比 = 俯视的圆铁盒盖，盖沿上那一段上了桃粉珐琅；对比 = 柜台上同一种瓶子按真实比例的高矮；
排行 = 一列火柴盒贴，宽度按真实比例；增长 = 撕页日历，一页一年；比率 = 药房天平按真实比例倾斜。
动作：先画轮廓线（10 帧），各色版再滑 6 px 套准落定；放射光每秒转 2°；窗像相机光圈一样打开；数字是撕掉写着旧数的一页日历露出来的；
换页是整张卡片像翻月历一样从上沿翻走，背面是下一页的底色。

场景（SCENES）：hero 撕页大数字 · leaves 撕页日历增长 · bottles 柜台瓶子对比 · tinlid 铁盒盖占比 · scale 药房天平 ·
matchbox 火柴盒排行 · statement 大数字 + 判断 · label 国货圆标落版。每个 beat 写 "head"（题版标题）、"sub"（题版小字）、
"src"（出处）、"ground": "jade" | "celadon" | "maroon"。横屏另排：窗在左，题版和标签票版在右。
"""
import math

JADE, CEL, IVORY, MAROON, PEACH, GOLD, INK = "#2f6f62", "#cfe0d2", "#f4ecd6", "#6b1f2a", "#f2b8a2", "#b8923a", "#2b1d14"
GROUNDS = {   # page ground, the second ray tone, window interior, foot plate, pattern ink on the ground
    "jade":    {"bg": JADE, "ray": "#3a7a6c", "win": MAROON, "win2": "#82303c", "plate": MAROON, "pat": IVORY, "back": CEL},
    "celadon": {"bg": CEL, "ray": "#bfd4c4", "win": JADE, "win2": "#3d7e70", "plate": JADE, "pat": INK, "back": MAROON},
    "maroon":  {"bg": MAROON, "ray": "#7a2935", "win": JADE, "win2": "#3d7e70", "plate": JADE, "pat": IVORY, "back": JADE},
}
GROUND_OF = {"hero": "jade", "leaves": "celadon", "bottles": "maroon", "tinlid": "jade", "scale": "celadon",
             "matchbox": "jade", "statement": "maroon", "label": "jade"}
ABRIL = {"0": .664, "1": .425, "2": .552, "3": .573, "4": .603, "5": .54, "6": .616, "7": .51, "8": .611, "9": .616,
         ".": .265, ",": .262, "%": .768, "+": .53, "-": .4, " ": .25}
BOX = 760           # every window is drawn in a 760 × 760 box (scaled to the window in 16:9)

STYLE = {
    "name": "月份牌国货", "en": "Yuefen", "benchmarks": ["杭穉英画室月份牌", "民国美术字", "老国货铁盒与火花"],
    "tokens": {
        "bg": JADE, "fg": IVORY, "muted": "#dfe7da", "accent": PEACH, "accent2": GOLD, "alert": MAROON,
        "line": "rgba(244,236,214,.35)", "paper": IVORY, "ink": INK, "card": IVORY, "card-fg": INK,
        "jade": JADE, "celadon": CEL, "ivory": IVORY, "maroon": MAROON, "peach": PEACH, "gold": GOLD,
        # caption: an ivory ticket inside the foot plate, maroon bold Song, gold diamonds at both ends (CSS below)
        "cap-bg": IVORY, "cap-fg": MAROON, "cap-size": "42px", "cap-weight": "800", "cap-pad": "10px 62px 12px", "cap-radius": "6px",
        "cap-shadow": "none", "cap-bottom": "190px", "cap-em": "#8a2a37",
        "punch-top": "68%", "punch-size": "72px",
    },
    "fonts": {"display": "noto-serif-sc", "body": "noto-serif-sc", "num": ["abril-fatface", "noto-serif-sc"], "serif": "noto-serif-sc",
              "cap": "noto-serif-sc", "hand": "lxgw-wenkai", "mono": "jetbrains-mono", "latin": ["abril-fatface", "noto-serif-sc"]},
    "motion": {"ease": "power2.out", "dur": 0.45, "stagger": 0.1, "cut": "hard", "transition": "dip", "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "none"},
    "safe_exempt": [".yf-cal", ".yf-bd", ".yf-orn"],      # the calendar-grid strip and the border are pattern / furniture
    "sfx": {"transition": ("paper", 0.45), "enter": ("paper", 0.3), "pop": ("pop", 0.35), "hit": ("tick", 0.4), "tear": ("paper", 0.55),
            "count": ("type", 0.25), "click": ("click", 0.3), "mascot": None, "line": ("click", 0.25), "slam": ("hit", 0.4)},
}


# ---------------------------------------------------------------- litho textures
def _uri(svg):
    from urllib.parse import quote
    return 'url("data:image/svg+xml,' + quote(svg, safe="") + '")'


# litho stipple: dark ink-brown specks and pale ivory specks from one turbulence field (not halftone dots)
STIP = _uri("<svg xmlns='http://www.w3.org/2000/svg' width='520' height='520'><filter id='f' x='0' y='0' width='100%' height='100%' color-interpolation-filters='sRGB'>"
            "<feTurbulence type='fractalNoise' baseFrequency='.82' numOctaves='2' seed='7' stitchTiles='stitch' result='n'/>"
            "<feColorMatrix in='n' values='0 0 0 0 .17  0 0 0 0 .11  0 0 0 0 .08  3.0 0 0 0 -1.75' result='d'/>"
            "<feColorMatrix in='n' values='0 0 0 0 .96  0 0 0 0 .93  0 0 0 0 .84  -3.0 0 0 0 1.25' result='l'/>"
            "<feMerge><feMergeNode in='d'/><feMergeNode in='l'/></feMerge></filter><rect width='520' height='520' filter='url(#f)'/></svg>")
# soft card mottling (the aged lithograph card), very low frequency
MOTTLE = _uri("<svg xmlns='http://www.w3.org/2000/svg' width='900' height='900'><filter id='m' x='0' y='0' width='100%' height='100%' color-interpolation-filters='sRGB'>"
              "<feTurbulence type='fractalNoise' baseFrequency='.008' numOctaves='3' seed='31' stitchTiles='stitch'/>"
              "<feColorMatrix values='0 0 0 0 .42  0 0 0 0 .30  0 0 0 0 .16  .55 0 0 0 -.2'/></filter><rect width='900' height='900' filter='url(#m)'/></svg>")


MOTTLE_FX = MOTTLE.replace("%20.55%200%200%200%20-.2", "%20.22%200%200%200%20-.08")


def stip_filter(fid):
    """SVG filter: the fill keeps its colour and gains litho speckle (dark + pale, alpha ~.12–.2) inside its own shape."""
    return (f'<filter id="{fid}" x="-60" y="-60" width="880" height="880" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">'
            '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="5" result="n"/>'
            '<feColorMatrix in="n" values="0 0 0 0 .17  0 0 0 0 .11  0 0 0 0 .08  .62 0 0 0 -.33" result="d"/>'
            '<feComposite in="d" in2="SourceAlpha" operator="in" result="dd"/>'
            '<feColorMatrix in="n" values="0 0 0 0 .97  0 0 0 0 .94  0 0 0 0 .86  -.6 0 0 0 .27" result="l"/>'
            '<feComposite in="l" in2="SourceAlpha" operator="in" result="ll"/>'
            '<feMerge><feMergeNode in="SourceGraphic"/><feMergeNode in="dd"/><feMergeNode in="ll"/></feMerge></filter>')


CSS = r"""
.st-yuefen .scene > .stage { perspective:2600px; perspective-origin:50% 0%; }
.yfw { position:absolute; inset:0; transform-style:preserve-3d; transform-origin:50% 0%; }
.yf { position:absolute; inset:0; overflow:hidden; background-color:var(--g); color:var(--ink); backface-visibility:hidden; -webkit-backface-visibility:hidden; }
.yf-back { position:absolute; inset:0; background-color:var(--gn); transform:rotateX(180deg); backface-visibility:hidden; -webkit-backface-visibility:hidden;
  background-image:__STIP__; background-size:520px; }
.yf .card { position:absolute; inset:0; background-image:__MOTTLE__; background-size:900px; opacity:.6; mix-blend-mode:multiply; }
.yf .rays { position:absolute; left:0; top:0; overflow:visible; }
.yf .box { position:absolute; width:760px; height:760px; transform-origin:0 0; }
.yf .wclip { position:absolute; inset:0; overflow:hidden; }
.yf .wbg { position:absolute; inset:0; background:radial-gradient(circle at 50% 36%, var(--w2) 0%, var(--w) 62%); }
.yf .wtex { position:absolute; inset:0; background-image:__STIP__; background-size:520px; opacity:.32; pointer-events:none; }
.yf svg { display:block; overflow:visible; }
.yf svg.art { position:absolute; left:0; top:0; width:760px; height:760px; }
.yf .kl { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.yf .kl * { stroke-dasharray:1; stroke-dashoffset:0; }
.yf .frame { position:absolute; left:0; top:0; width:760px; height:760px; pointer-events:none; }
.yf .tex { position:absolute; inset:0; background-image:__STIP__; background-size:520px; opacity:.4; pointer-events:none; }
.yf .age { position:absolute; inset:0; pointer-events:none; }
.yf .fold { position:absolute; left:0; right:0; height:5px; background:linear-gradient(rgba(255,250,235,.16) 0 2px, rgba(43,29,20,.12) 2px 5px); }
/* cartouche */
.yf .cart { position:absolute; }
.yf .cart svg { position:absolute; inset:0; width:100%; height:100%; }
.yf .cart .pl { position:absolute; inset:0; }
.yf .hl { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; letter-spacing:.08em; line-height:1.05; white-space:nowrap; }
.yf .hl .hs { position:absolute; left:6px; right:-6px; top:6px; color:var(--maroon); }
.yf .hl .hf { position:relative; color:var(--jade); }
.yf .sl { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-body); font-weight:600; font-size:28px; color:var(--ink); letter-spacing:.12em; white-space:nowrap; }
/* foot plate + source */
.yf .foot { position:absolute; }
.yf .foot svg { position:absolute; inset:0; width:100%; height:100%; }
.yf .src { position:absolute; font-family:var(--f-body); font-weight:600; font-size:24px; color:var(--ink); white-space:nowrap; line-height:1.3; }
/* things printed in a window */
.yf .num { position:absolute; font-family:var(--f-num); color:var(--ivory); line-height:1; white-space:nowrap; text-shadow:6px 6px 0 var(--nsh); }
.yf .num .u { font-family:var(--f-display); font-weight:900; }
.yf .lab { position:absolute; font-family:var(--f-display); font-weight:900; white-space:nowrap; line-height:1.2; }
.yf .tag { position:absolute; background:var(--ivory); color:var(--maroon); font-family:var(--f-display); font-weight:900; white-space:nowrap; line-height:1.15;
  padding:8px 18px 10px; border-radius:6px; box-shadow:inset 0 0 0 2px var(--gold), 3px 3px 0 rgba(43,29,20,.35); }
.yf .tag .v { font-family:var(--f-num); font-weight:400; color:var(--ink); }
.yf .rib { position:absolute; background:var(--peach); color:var(--maroon); font-family:var(--f-display); font-weight:900; white-space:nowrap; line-height:1;
  padding:14px 54px 16px; clip-path:polygon(0 0, 100% 0, calc(100% - 26px) 50%, 100% 100%, 0 100%, 26px 50%); transform-origin:50% 50%; }
.yf .rib .v { font-family:var(--f-num); font-weight:400; }
.yf .leaf { position:absolute; background:var(--ivory); color:var(--maroon); transform-origin:12% 0%; box-shadow:4px 6px 0 rgba(43,29,20,.3);
  -webkit-mask:radial-gradient(circle at 50% 0, transparent 6px, #000 6.5px) 0 0/22px 100% repeat-x; }
.yf .leaf .band { position:absolute; left:0; right:0; top:0; background:var(--maroon); color:var(--ivory); font-family:var(--f-num); text-align:center; line-height:1; }
.yf .leaf .ov { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-num); line-height:1; white-space:nowrap; }
.yf .leaf .ov .u { font-family:var(--f-display); font-weight:900; }
.yf .yf-cal { position:absolute; }
"""


# ---------------------------------------------------------------- helpers
def ground(X, i=None):
    i = X.beat["i"] if i is None else i
    bs = X.v.get("beats", [])
    if not 0 <= i < len(bs): return "jade"
    g = bs[i].get("ground") or GROUND_OF.get(bs[i].get("scene"), "jade")
    return g if g in GROUNDS else "jade"


def aw(s):
    """Abril Fatface advance width in em (CJK units counted at 1em)."""
    w = 0.0
    for c in str(s):
        w += ABRIL.get(c, 1.0 if ord(c) > 0x2e80 else 0.55)
    return w


def L(X):
    """the fixed architecture, per aspect: window box (x, y, scale), cartouche, foot plate, calendar strip, ray centre."""
    if X.portrait:
        return {"wx": 160, "wy": 470, "ws": 1.0, "cart": (80, 214, 920, 212), "foot": (72, 1252, 936, 256),
                "src": (128, 1452, 830), "cal": (110, 1532, 860, 330), "rc": (540, 850)}
    return {"wx": 170, "wy": 205, "ws": 700 / BOX, "cart": (930, 104, 880, 214), "foot": (930, 790, 880, 214),
            "src": (980, 942, 780), "cal": (980, 446, 780, 300), "rc": (520, 555)}


def stepped(x0, y0, x1, y1, s):
    """a rectangle whose four corners step inward twice (Art Deco)."""
    h = s / 2
    return (f"M{x0 + s},{y0} H{x1 - s} V{y0 + h} H{x1 - h} V{y0 + s} H{x1} V{y1 - s} H{x1 - h} V{y1 - h} H{x1 - s} V{y1} "
            f"H{x0 + s} V{y1 - h} H{x0 + h} V{y1 - s} H{x0} V{y0 + s} H{x0 + h} V{y0 + h} H{x0 + s} Z")


def border(W, H, cid):
    """double gold rule inset 36 px (4 px + 1.5 px, 14 px apart) with stepped corners and a 150 px sunburst fan in each."""
    o, i = 36, 50
    fans = ""
    for k, (cx, cy, a0) in enumerate([(i, i, 0), (W - i, i, 90), (W - i, H - i, 180), (i, H - i, 270)]):
        rays = ""
        for j in range(10):
            a = math.radians(a0 + 9 * j + 4.5)
            rays += f'<line class="bk" pathLength="1" x1="{cx + 22 * math.cos(a):.1f}" y1="{cy + 22 * math.sin(a):.1f}" x2="{cx + 150 * math.cos(a):.1f}" y2="{cy + 150 * math.sin(a):.1f}"/>'
        arcs = ""
        for r in (34, 92, 150):
            p0 = (cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
            p1 = (cx + r * math.cos(math.radians(a0 + 90)), cy + r * math.sin(math.radians(a0 + 90)))
            arcs += f'<path class="bk" pathLength="1" d="M{p0[0]:.1f},{p0[1]:.1f} A{r},{r} 0 0 1 {p1[0]:.1f},{p1[1]:.1f}"/>'
        fans += f'<g stroke="{GOLD}" stroke-width="1.6" fill="none" opacity=".9">{rays}{arcs}</g>'
    return (f'<svg class="yf-bd" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0;top:0">'
            f'<path class="bk" pathLength="1" d="{stepped(o, o, W - o, H - o, 44)}" fill="none" stroke="{GOLD}" stroke-width="4"/>'
            f'<path class="bk" pathLength="1" d="{stepped(i, i, W - i, H - i, 30)}" fill="none" stroke="{GOLD}" stroke-width="1.5"/>{fans}</svg>')


def rays_svg(W, H, cx, cy, tone):
    """24 Deco rays behind the window: 12 wedges of the second ground tone over the ground."""
    R = 2400
    d = ""
    for k in range(12):
        a0 = math.radians(k * 30); a1 = math.radians(k * 30 + 15)
        d += f"M{cx},{cy} L{cx + R * math.cos(a0):.0f},{cy + R * math.sin(a0):.0f} L{cx + R * math.cos(a1):.0f},{cy + R * math.sin(a1):.0f} Z "
    return (f'<svg class="rays" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><g class="rg"><path d="{d}" fill="{tone}"/></g></svg>')


def frame_svg(kind):
    """the window frame in box coordinates: 10 px ivory frame, gold inner rule, hairline gold outer rule."""
    if kind == "arch":
        def arch(m):
            r = 380 - m
            return f"M{m},{BOX - m} V380 A{r},{r} 0 0 1 {BOX - m},380 V{BOX - m} Z"
        return (f'<svg class="frame" viewBox="0 0 {BOX} {BOX}"><path d="{arch(-8)}" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
                f'<path d="{arch(5)}" fill="none" stroke="{IVORY}" stroke-width="10"/><path d="{arch(15)}" fill="none" stroke="{GOLD}" stroke-width="2"/></svg>')
    return (f'<svg class="frame" viewBox="0 0 {BOX} {BOX}"><circle cx="380" cy="380" r="388" fill="none" stroke="{GOLD}" stroke-width="1.5"/>'
            f'<circle cx="380" cy="380" r="375" fill="none" stroke="{IVORY}" stroke-width="10"/><circle cx="380" cy="380" r="365" fill="none" stroke="{GOLD}" stroke-width="2"/></svg>')


def cal_strip(X, x, y, w, h, gnd):
    """月历格子: 7 columns of small numerals as pattern (35 % contrast), framed by gold rules. Furniture, not content."""
    G = GROUNDS[gnd]
    cols, rows = 7, 6
    cw = w / cols
    rh = (h - 30) / rows
    head = "日一二三四五六"
    t = ""
    for c in range(cols):
        t += f'<text x="{cw * (c + 0.5):.0f}" y="44" text-anchor="middle">{head[c]}</text>'
    day = 1
    off = 3
    for r in range(1, rows):
        for c in range(cols):
            k = (r - 1) * cols + c - off + 1
            if 1 <= k <= 31:
                t += f'<text x="{cw * (c + 0.5):.0f}" y="{44 + rh * r:.0f}" text-anchor="middle">{k}</text>'
    X.used_text.update(head + "0123456789")
    return (f'<svg class="yf-cal" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="left:{x}px;top:{y}px">'
            f'<line x1="0" y1="8" x2="{w}" y2="8" stroke="{GOLD}" stroke-width="1.5"/><line x1="0" y1="{h - 4}" x2="{w}" y2="{h - 4}" stroke="{GOLD}" stroke-width="1.5"/>'
            f'<g fill="{G["pat"]}" opacity=".35" font-family="var(--f-num)" font-size="20">{t}</g></svg>')


def cartouche(X, x, y, w, h, head, sub):
    """the banner plate with stepped Deco ends holding the headline (美术字: jade face, 6 px maroon inline shadow)."""
    from h9 import fit
    X.used_text.update(head + sub)
    s = 26
    d = (f"M{s * 2},0 H{w - s * 2} V{s} H{w - s} V{s * 2} H{w} V{h - s * 2} H{w - s} V{h - s} H{w - s * 2} V{h} "
         f"H{s * 2} V{h - s} H{s} V{h - s * 2} H0 V{s * 2} H{s} V{s} H{s * 2} Z")
    di = (f"M{s * 2 + 4},12 H{w - s * 2 - 4} V{s + 12} H{w - s - 12} V{s * 2 + 4} H{w - 12} V{h - s * 2 - 4} H{w - s - 12} V{h - s - 12} H{w - s * 2 - 4} V{h - 12} "
          f"H{s * 2 + 4} V{h - s - 12} H{s + 12} V{h - s * 2 - 4} H12 V{s * 2 + 4} H{s + 12} V{s + 12} H{s * 2 + 4} Z")
    top = 132 if sub else 150
    f = fit.fit_text(head, (w - 150) / 1.08, 160, top, 110 if X.portrait else 96, max_lines=1)
    px = f.px
    line = f.lines[0] if f.lines else ""
    hy = (h - 46 - px * 1.05) / 2 + 4 if sub else (h - px * 1.05) / 2
    sub_html = f'<div class="sl" style="top:{h - 58}px">{X.rich(sub)}</div>' if sub else ""
    return (f'<div class="cart" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<svg class="pl" viewBox="0 0 {w} {h}"><path class="plf" d="{d}" fill="{IVORY}"/></svg>'
            f'<svg class="kl2" viewBox="0 0 {w} {h}"><g class="kl" stroke="{GOLD}"><path d="{d}" stroke-width="3" pathLength="1"/><path d="{di}" stroke-width="1.5" pathLength="1"/></g></svg>'
            f'<div class="hl" data-layout-allow-overlap style="top:{hy:.0f}px;font-size:{px}px"><span class="hs" aria-hidden="true">{X.rich(line)}</span><span class="hf">{X.rich(line)}</span></div>'
            f'{sub_html}</div>')


def foot_plate(X, x, y, w, h, gnd, src):
    """the product-label plate: a ticket with notched sides and a gold double rule; an ivory strip at its foot carries the source."""
    G = GROUNDS[gnd]
    r = 26
    d = (f"M14,0 H{w - 14} Q{w},0 {w},14 V{h / 2 - r} A{r},{r} 0 0 0 {w},{h / 2 + r} V{h - 14} Q{w},{h} {w - 14},{h} "
         f"H14 Q0,{h} 0,{h - 14} V{h / 2 + r} A{r},{r} 0 0 0 0,{h / 2 - r} V14 Q0,0 14,0 Z")
    sx, sy, sw = L(X)["src"]
    strip_y = sy - y - 8
    strip = f'<rect x="{sx - x - 22}" y="{strip_y}" width="{sw + 44}" height="52" rx="6" fill="{IVORY}"/>' if src else ""
    X.used_text.update(src)
    return (f'<div class="foot" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><svg viewBox="0 0 {w} {h}">'
            f'<path d="{d}" fill="{G["plate"]}"/><path d="{d}" fill="none" stroke="{GOLD}" stroke-width="2" transform="translate(9 9) scale({(w - 18) / w:.4f} {(h - 18) / h:.4f})"/>'
            f'{strip}</svg></div>'
            + (f'<div class="src" style="left:{sx}px;top:{sy - 1}px;max-width:{sw}px">{X.rich(src)}</div>' if src else ""))


def ageing(X, cid):
    """foxing spots, one horizontal fold, a vignette no darker than 6 %."""
    W, H = X.W, X.H
    rnd = X.rand
    spots = ",".join(f"radial-gradient(circle at {rnd.uniform(4, 96):.1f}% {rnd.uniform(3, 97):.1f}%, rgba(120,78,32,{rnd.uniform(.06, .13):.2f}) 0, rgba(120,78,32,0) {rnd.uniform(5, 16):.0f}px)"
                     for _ in range(16))
    fy = H * (0.41 if X.portrait else 0.37)
    return (f'<div class="age" style="background:{spots}, radial-gradient(ellipse at 50% 48%, rgba(30,18,10,0) 58%, rgba(30,18,10,.06) 100%)"></div>'
            f'<div class="fold" style="top:{fy:.0f}px"></div>')


def wrap_box(X, cls, inner, z=""):
    l = L(X)
    return f'<div class="box {cls}" data-layout-allow-overlap style="left:{l["wx"]}px;top:{l["wy"]}px;transform:scale({l["ws"]:.4f});{z}">{inner}</div>'


def art(cid, fills, keys, extra_defs=""):
    """a litho illustration: colour plates (each its own group, sitting 2.5 / 2 px off the key, speckled) under the keyline plate.
    fills = list of svg strings (one per colour plate); keys = svg string of strokes (each element gets pathLength=1)."""
    fid = f"st{cid}"
    plates = "".join(f'<g transform="translate(2.5 2)"><g class="cl" filter="url(#{fid})">{f}</g></g>' for f in fills)
    return (f'<svg class="art" viewBox="0 0 {BOX} {BOX}"><defs>{stip_filter(fid)}{extra_defs}</defs>{plates}'
            f'<g class="kl" stroke="{INK}" stroke-width="3.2">{keys}</g></svg>')


def pl(s):
    """add pathLength=1 to every svg element in s that draws a stroke (so the keyline can be drawn on)."""
    for tag in ("<path ", "<line ", "<circle ", "<ellipse ", "<rect ", "<polyline "):
        s = s.replace(tag, tag + 'pathLength="1" ')
    return s


# ---------------------------------------------------------------- motion verbs
def draw_keys(X, sel, t, dur=0.33):
    """keyline plate first: every stroke draws on in 10 frames."""
    X.tw(f'tl.fromTo("{sel} .kl > *", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{dur:.2f}, ease:"sine.inOut", stagger:0.02}}, {t:.3f});')


def register(X, sel, t, stagger=0.1, dx=6, dy=-4):
    """each colour plate slides 6 px into register and settles (soft, no bounce), 3 frames apart."""
    X.tw(f'tl.fromTo("{sel}", {{x:{dx}, y:{dy}, opacity:0}}, {{x:0, y:0, opacity:1, duration:0.42, ease:"power2.out", stagger:{stagger}}}, {t:.3f});')


def tear(X, sel, t):
    """a calendar leaf tears away upward (rotate -8°) and falls out of the frame."""
    X.tw(f'tl.to("{sel}", {{y:-34, rotation:-8, duration:0.14, ease:"power2.out"}}, {t:.3f});')
    X.tw(f'tl.to("{sel}", {{y:1500, rotation:-26, x:-60, duration:0.62, ease:"power2.in"}}, {t + 0.14:.3f});')
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {t + 0.8:.3f});')
    X.sfx(t, "tear")


def leaf(X, x, y, w, h, year, old, unit="", px=None, cls="lf", band=64):
    """a tear-off calendar leaf: maroon year band, the previous value printed in maroon Abril."""
    X.used_text.update(str(year) + str(old) + unit)
    px = px or min(h - band - 70, (w - 60) / max(0.5, aw(old) + (0.45 * len(unit) if unit else 0)))
    ux = f'<span class="u" style="font-size:{px * 0.36:.0f}px;margin-left:.12em">{X.rich(unit)}</span>' if unit else ""
    return (f'<div class="leaf {cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="band" style="height:{band}px;line-height:{band}px;font-size:{band * 0.62:.0f}px;padding-top:4px">{X.rich(str(year))}</div>'
            f'<div class="ov" style="top:{band + (h - band - px) / 2:.0f}px;font-size:{px:.0f}px">{X.rich(str(old))}{ux}</div></div>')


def number(X, x, y, big, small="", unit="", px=300, cls="hn", align="center", w=BOX, ign=False):
    """the hero numeral: ivory Abril with a 6 px inline shadow; decimals and unit stacked at its shoulder."""
    X.used_text.update(big + small + unit)
    stack = ""
    if small or unit:
        stack = (f'<span style="display:inline-flex;flex-direction:column;align-items:flex-start;vertical-align:top;margin-left:.06em;margin-top:.1em">'
                 + (f'<span style="font-size:{px * 0.4:.0f}px;line-height:1">{X.rich(small)}</span>' if small else "")
                 + (f'<span class="u" style="font-size:{px * 0.2:.0f}px;line-height:1.3;margin-top:.15em;letter-spacing:.06em">{X.rich(unit)}</span>' if unit else "")
                 + '</span>')
    safe = ' data-safe="ignore"' if ign else ""
    return (f'<div class="num {cls}"{safe} style="left:{x}px;top:{y}px;width:{w}px;text-align:{align};font-size:{px}px">'
            f'<span style="display:inline-block">{X.rich(big)}{stack}</span></div>')


def num_width(big, small, unit, px):
    return aw(big) * px + max(aw(small) * px * 0.4 if small else 0, len(unit) * px * 0.2 * 1.06 if unit else 0) + (0.06 * px if small or unit else 0)


# ---------------------------------------------------------------- the page
def page(X, b, cid, t, d, gnd, win, ovr="", kind="circle", note=None, opening=False):
    """one calendar card: ground + stipple + mottling, rays, window (iris), cartouche, foot plate, calendar strip, border,
    ageing; the card flips up off the top edge when the next beat starts (its back is the next page's ground)."""
    X.css("yuefen", CSS.replace("__STIP__", STIP).replace("__MOTTLE__", MOTTLE))
    W, H, P = X.W, X.H, X.portrait
    i, n = X.beat["i"], len(X.v.get("beats", []))
    G = GROUNDS[gnd]
    l = L(X)
    nxt = ground(X, i + 1) if i + 1 < n else gnd
    head, sub, src = b.get("head", ""), b.get("sub", ""), b.get("src", "")
    rcx, rcy = l["rc"]
    rnd = "50%" if kind == "circle" else "380px 380px 0px 0px"
    clip0 = f"inset(50% 50% 50% 50% round {rnd})"
    window = wrap_box(X, "win", f'<div class="wclip" style="clip-path:{clip0}"><div class="wbg"></div>{win}<div class="wtex"></div></div>{frame_svg(kind)}')
    over = wrap_box(X, "ovr", ovr)
    cx, cy, cw, ch = l["cart"]
    fx_, fy_, fw_, fh_ = l["foot"]
    kx, ky, kw, khh = l["cal"]
    rib = ""
    if note and not P:          # 16:9: the beat's note rides on a ribbon in the right-hand column
        X.used_text.update(note)
        rib = f'<div class="rib nt" style="left:{cx + cw / 2:.0f}px;top:{cy + ch + 34:.0f}px;font-size:40px;transform:translateX(-50%)">{X.rich(note)}</div>'
    orn = ""
    if P:   # a small Deco ornament in the top band (furniture)
        orn = (f'<svg class="yf-orn" width="{W}" height="200" style="position:absolute;left:0;top:0"><g stroke="{GOLD}" stroke-width="1.6" fill="none">'
               f'<line x1="250" y1="128" x2="470" y2="128"/><line x1="610" y1="128" x2="830" y2="128"/>'
               f'<path d="M540,96 L572,128 L540,160 L508,128 Z"/><path d="M540,110 L558,128 L540,146 L522,128 Z" fill="{GOLD}"/>'
               f'<circle cx="488" cy="128" r="5" fill="{GOLD}"/><circle cx="592" cy="128" r="5" fill="{GOLD}"/></g></svg>')
    cal = cal_strip(X, kx, ky, kw, khh, gnd)
    face = (f'<div class="yf g-{gnd}" style="--g:{G["bg"]};--w:{G["win"]};--w2:{G["win2"]};--nsh:{INK if G["win"] == MAROON else MAROON}">'
            f'<div class="card"></div>{rays_svg(W, H, rcx, rcy, G["ray"])}<div class="tex"></div>{orn}'
            f'{window}{cartouche(X, cx, cy, cw, ch, head, sub)}{foot_plate(X, fx_, fy_, fw_, fh_, gnd, src)}{cal}{rib}{over}'
            f'{border(W, H, cid)}{ageing(X, cid)}</div>')
    html = f'<div class="yfw">{face}<div class="yf-back" style="--gn:{GROUNDS[nxt]["bg"]}"></div></div>'
    D = X.duration or (t + d)
    last = i + 1 >= n
    ext = d if last else min(d + 0.4, max(d, D - t))       # stay over the next card while it flips away
    X.clip(cid, t, ext, html, "scene", 40 - i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    # rays turn 2°/s the whole beat
    X.tw(f'tl.fromTo("{s} .rays .rg", {{rotation:0}}, {{rotation:{2 * ext:.2f}, svgOrigin:"{rcx} {rcy}", duration:{ext:.2f}, ease:"none"}}, {t:.3f});')
    # the window opens like an iris: oval scale-clip 0 → 1 in 12 frames
    c0, w0 = t, t + 0.12
    if opening:      # the film's first card: border keylines draw (10 frames), then the cartouche, then the window opens
        X.tw(f'tl.fromTo("{s} .yf-bd .bk", {{strokeDasharray:"0 1"}}, {{strokeDasharray:"1 0", duration:0.33, ease:"sine.inOut"}}, {t:.3f});')
        c0, w0 = t + 0.33, t + 0.8
    X.tw(f'tl.fromTo("{s} .wclip", {{clipPath:"{clip0}"}}, {{clipPath:"inset(0% 0% 0% 0% round {rnd})", duration:0.4, ease:"power2.out"}}, {w0:.3f});')
    X.tw(f'tl.from("{s} .win .frame", {{scale:0.86,{" opacity:0," if opening else ""} transformOrigin:"50% 50%", duration:0.4, ease:"power2.out"}}, {w0:.3f});')
    # cartouche: gold keyline draws, the ivory plate slides into register, then the headline's two colours register
    draw_keys(X, f"{s} .cart .kl2", c0 + 0.05)
    register(X, f"{s} .cart .pl", c0 + 0.2, dx=0, dy=6)
    register(X, f"{s} .cart .hs", c0 + 0.3, dx=6, dy=6)
    register(X, f"{s} .cart .hf, {s} .cart .sl", c0 + 0.38, dx=-6, dy=0)
    if rib: X.tw(f'tl.from("{s} .nt", {{scaleX:0, duration:0.4, ease:"power2.out"}}, {t + 0.9:.3f});')
    if not last:      # turn the calendar page: the whole card flips up from its top edge in 10 frames
        X.tw(f'tl.fromTo("{s} .yfw", {{rotationX:0}}, {{rotationX:-178, duration:0.34, ease:"power2.in"}}, {t + d:.3f});')
        X.tw(f'tl.set("{s} .yfw", {{visibility:"hidden"}}, {t + d + 0.36:.3f});')
        X.sfx(t + d - 0.02, "transition")
    return s


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


# ---------------------------------------------------------------- object drawings (box coordinates)
def bottle_paths(x, base, h):
    """a plain white ceramic bottle (cylinder body, rounded shoulder, short neck, cap) of height h standing at (x, base)."""
    w = h * 0.36
    bx0, bx1 = x - w / 2, x + w / 2
    sh = base - h * 0.66            # shoulder
    nk = base - h * 0.84            # neck top
    nw = w * 0.3
    body = (f"M{bx0:.1f},{base - h * 0.03:.1f} Q{bx0:.1f},{base:.1f} {bx0 + w * 0.08:.1f},{base:.1f} H{bx1 - w * 0.08:.1f} Q{bx1:.1f},{base:.1f} {bx1:.1f},{base - h * 0.03:.1f} "
            f"V{sh:.1f} Q{bx1:.1f},{sh - h * 0.1:.1f} {x + nw / 2:.1f},{sh - h * 0.12:.1f} V{nk:.1f} H{x - nw / 2:.1f} V{sh - h * 0.12:.1f} Q{bx0:.1f},{sh - h * 0.1:.1f} {bx0:.1f},{sh:.1f} Z")
    cap = f"M{x - nw * 0.62:.1f},{nk:.1f} V{base - h:.1f} H{x + nw * 0.62:.1f} V{nk:.1f} Z"
    ribbon = f"M{bx0 + w * 0.06:.1f},{base - h * 0.42:.1f} H{bx1 - w * 0.06:.1f} V{base - h * 0.24:.1f} H{bx0 + w * 0.06:.1f} Z"
    neckband = f"M{x - nw / 2 - 2:.1f},{nk + h * 0.05:.1f} H{x + nw / 2 + 2:.1f} V{nk + h * 0.085:.1f} H{x - nw / 2 - 2:.1f} Z"
    hi = f"M{bx0 + w * 0.2:.1f},{sh + h * 0.02:.1f} V{base - h * 0.08:.1f}"
    return body, cap, ribbon, neckband, hi


def jar_paths(x, base, h):
    w = h * 0.8
    d = (f"M{x - w * 0.42:.1f},{base:.1f} Q{x - w * 0.56:.1f},{base - h * 0.5:.1f} {x - w * 0.36:.1f},{base - h * 0.82:.1f} H{x + w * 0.36:.1f} "
         f"Q{x + w * 0.56:.1f},{base - h * 0.5:.1f} {x + w * 0.42:.1f},{base:.1f} Z")
    lid = f"M{x - w * 0.4:.1f},{base - h * 0.82:.1f} H{x + w * 0.4:.1f} V{base - h:.1f} H{x - w * 0.4:.1f} Z"
    return d, lid


# ---------------------------------------------------------------- scenes
def hero(b, X, t, d, cid):
    """开场：撕页大数字。窗是一本挂历：装订条上挂着写着上一年数的一页，撕掉，露出今年的大数字；柜台上一只瓶、一只罐。"""
    gnd = ground(X)
    big, small, unit = b.get("big", ""), b.get("small", ""), b.get("unit", "")
    px = 300
    while num_width(big, small, unit, px) > 780 and px > 200: px -= 10
    nw = num_width(big, small, unit, px)
    o = b.get("old", {})
    # window: shop counter at the foot with a bottle and a jar (product at the foot of the poster), gold arcs behind
    body, cap, rib, nb, hi = bottle_paths(250, 690, 230)
    jar, lid = jar_paths(520, 690, 120)
    fills = [f'<rect x="0" y="690" width="760" height="70" fill="{INK}"/><rect x="0" y="684" width="760" height="8" fill="{GOLD}"/>',
             f'<path d="{body}" fill="{IVORY}"/><path d="{jar}" fill="{IVORY}"/>',
             f'<path d="{cap}" fill="{PEACH}"/><path d="{rib}" fill="{PEACH}"/><path d="{lid}" fill="{PEACH}"/>']
    keys = pl(f'<path d="{body}"/><path d="{cap}"/><path d="{rib}"/><path d="{jar}"/><path d="{lid}"/><path d="{hi}" stroke="{GOLD}" stroke-width="2"/>'
              f'<circle cx="380" cy="380" r="300" stroke="{GOLD}" stroke-width="1.5"/><circle cx="380" cy="380" r="250" stroke="{GOLD}" stroke-width="1"/>')
    win = art(cid, fills, keys)
    ny = 200
    ovr = (f'<div class="bind" style="position:absolute;left:150px;top:120px;width:460px;height:34px;background:{INK};border-radius:6px;box-shadow:inset 0 -6px 0 {GOLD}"></div>'
           + number(X, (BOX - nw) / 2 - 10, ny, big, small, unit, px, w=nw + 40, align="left")
           + leaf(X, (BOX - max(nw, 560)) / 2 - 20, 150, max(nw, 560) + 40, 470, o.get("year", ""), o.get("value", ""), o.get("unit", ""))
           + (f'<div class="rib nt9" style="left:380px;top:{ny + px * 1.02 + 20:.0f}px;font-size:40px;transform:translateX(-50%)">{X.rich(b.get("note", ""))}</div>'
              if X.portrait and b.get("note") else ""))
    X.used_text.update(b.get("note", ""))
    s = page(X, b, cid, t, d, gnd, win, ovr, "circle", b.get("note"), opening=(X.beat["i"] == 0))
    # order on the first card: border keylines -> cartouche -> window iris (page) -> the 2023 leaf
    draw_keys(X, f"{s} .win .art", t + 1.0)
    register(X, f"{s} .win .art .cl", t + 1.25)
    X.tw(f'tl.from("{s} .bind", {{scaleX:0, duration:0.35, ease:"power2.out"}}, {t + 1.05:.3f});')
    X.tw(f'tl.set("{s} .leaf", {{visibility:"hidden"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .leaf", {{visibility:"visible"}}, {t + 1.2:.3f});')
    X.tw(f'tl.fromTo("{s} .leaf", {{y:-700, rotation:4}}, {{y:0, rotation:0, duration:0.45, ease:"power3.out", immediateRender:false}}, {t + 1.2:.3f});')
    tt = T(X, b, "at_tear", t, t + 2.1)
    tear(X, f"{s} .leaf", tt)
    register(X, f"{s} .hn", tt + 0.04, dx=6, dy=6)
    if X.portrait and b.get("note"):
        X.tw(f'tl.from("{s} .nt9", {{scaleX:0, duration:0.4, ease:"power2.out"}}, {tt + 0.55:.3f});')


def leaves(b, X, t, d, cid):
    """增长 = 撕页日历：一页一年，数印在页上；撕掉一页翻到下一年，撕下的页缩成小票排在窗脚，记下走过的路。"""
    gnd = ground(X)
    items = b.get("items", [])[:3]
    n = len(items)
    unit = b.get("unit", "")
    # window: the pad's backing board and binding, with gold arcs
    fills = [f'<rect x="96" y="112" width="568" height="520" rx="10" fill="{INK}"/>',
             f'<rect x="96" y="112" width="568" height="56" rx="10" fill="{MAROON}"/>']
    keys = pl(f'<rect x="96" y="112" width="568" height="520" rx="10" stroke="{GOLD}" stroke-width="2"/>'
              f'<line x1="96" y1="168" x2="664" y2="168" stroke="{GOLD}" stroke-width="2"/>'
              f'<circle cx="380" cy="380" r="330" stroke="{GOLD}" stroke-width="1.2"/>')
    win = art(cid, fills, keys)
    lx, ly, lw, lh = 110, 176, 540, 440
    sheets = ""
    for k in range(n - 1, -1, -1):           # the newest leaf at the bottom of the stack
        it = items[k]
        X.used_text.update(str(it.get("year", "")) + str(it.get("value", "")))
        sheets += leaf(X, lx, ly, lw, lh, f'{it.get("year", "")} 年', it.get("value", ""), unit, cls=f"lf lf{k}", band=78)
    rings = "".join(f'<i style="position:absolute;left:{x}px;top:150px;width:22px;height:52px;border-radius:11px;background:{GOLD};box-shadow:inset -5px 0 0 #8a6a26"></i>' for x in (210, 369, 528))
    slots = ""
    for k in range(n - 1):
        it = items[k]
        sx = 380 - (n - 1) * 130 + k * 260
        slots += (f'<div class="tag stub st{k}" style="left:{sx - 115}px;top:640px;width:230px;text-align:center;font-size:28px">'
                  f'{X.rich(str(it.get("year", "")))}<br><span class="v" style="font-size:40px">{X.rich(str(it.get("value", "")))}</span></div>')
    ovr = sheets + rings + slots
    s = page(X, b, cid, t, d, gnd, win, ovr, "circle", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.35)
    register(X, f"{s} .win .art .cl", t + 0.6)
    X.tw(f'tl.from("{s} .lf", {{y:-600, duration:0.5, ease:"power3.out", stagger:0.06}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .ovr > i", {{scaleY:0, duration:0.3, ease:"power2.out", stagger:0.05}}, {t + 0.6:.3f});')
    for k in range(n - 1):
        tk = T(X, items[k + 1], "at", t, t + 1.3 + 1.05 * k)
        sel = f"{s} .lf{k}"
        sx = 380 - (n - 1) * 130 + k * 260
        # the leaf tears off, shrinks and lands in its slot as a stub
        X.tw(f'tl.to("{sel}", {{y:-34, rotation:-8, duration:0.14, ease:"power2.out"}}, {tk:.3f});')
        X.tw(f'tl.to("{sel}", {{x:{sx - (lx + lw / 2):.0f}, y:{640 + 55 - (ly + lh / 2):.0f}, scale:0.42, rotation:{-6 + 10 * k}, duration:0.5, ease:"power2.inOut"}}, {tk + 0.14:.3f});')
        X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {tk + 0.64:.3f});')
        X.tw(f'tl.from("{s} .st{k}", {{scale:0.6, opacity:0, duration:0.2, ease:"power2.out"}}, {tk + 0.6:.3f});')
        X.sfx(tk, "tear")


def bottles(b, X, t, d, cid):
    """对比 = 柜台上同一种瓶子按真实比例的高矮：瓶子从柜台后面升起来，标签上的数随之跳到真值；最后一条丝带写出倍数。"""
    gnd = ground(X)
    items = b.get("items", [])[:2]
    vals = [float(it.get("value", 1)) for it in items]
    vmax = max(vals) or 1
    hmax = 500
    xs = [230, 560]
    base = 600
    fills_b, fills_c, keys = "", "", ""
    for k, v in enumerate(vals):
        h = hmax * v / vmax
        body, cap, rib, nb, hi = bottle_paths(xs[k], base, h)
        fills_b += f'<g class="bt bt{k}"><path d="{body}" fill="{IVORY}"/></g>'
        fills_c += f'<g class="bt bt{k}"><path d="{cap}" fill="{PEACH}"/><path d="{rib}" fill="{PEACH}"/><path d="{nb}" fill="{GOLD}"/></g>'
        keys += f'<g class="bt bt{k}">' + pl(f'<path d="{body}"/><path d="{cap}"/><path d="{rib}" stroke-width="2.4"/><path d="{hi}" stroke="{GOLD}" stroke-width="2"/>') + '</g>'
    counter = (f'<rect x="-20" y="{base}" width="800" height="200" fill="{INK}"/><rect x="-20" y="{base - 6}" width="800" height="12" fill="{GOLD}"/>'
               + "".join(f'<rect x="{40 + 120 * j}" y="{base + 40}" width="80" height="140" rx="6" fill="#3a2a1e"/>' for j in range(6)))
    fid = f"st{cid}"
    win = (f'<svg class="art" viewBox="0 0 {BOX} {BOX}"><defs>{stip_filter(fid)}<clipPath id="cc{cid}"><rect x="-40" y="-40" width="840" height="{base + 40}"/></clipPath></defs>'
           f'<g clip-path="url(#cc{cid})"><g transform="translate(2.5 2)"><g class="cl" filter="url(#{fid})">{fills_b}</g></g>'
           f'<g transform="translate(2.5 2)"><g class="cl" filter="url(#{fid})">{fills_c}</g></g>'
           f'<g class="kl" stroke="{INK}" stroke-width="3.2">{keys}</g></g>'
           f'<g filter="url(#{fid})">{counter}</g></svg>')
    tags = ""
    for k, it in enumerate(items):
        X.used_text.update(it.get("name", "") + str(it.get("value", "")) + it.get("unit", ""))
        tags += (f'<div class="tag tg{k}" style="left:{xs[k] - 150}px;top:{base + 34}px;width:300px;text-align:center;font-size:30px">{X.rich(it.get("name", ""))}'
                 f'<br><span class="v" style="font-size:46px"><span class="cv">{X.rich(str(it.get("value", "")))}</span></span>'
                 f'<span style="font-size:24px"> {X.rich(it.get("unit", ""))}</span></div>')
    rt = b.get("ratio", "")
    X.used_text.update(rt)
    hs = hmax * vals[1] / vmax if len(vals) > 1 else 0
    ovr = tags + (f'<div class="rib rt" style="left:{xs[1]}px;top:{base - hs - 150:.0f}px;font-size:56px;transform:translateX(-50%) rotate(-4deg)">{X.rich(rt)}</div>' if rt else "")
    s = page(X, b, cid, t, d, gnd, win, ovr, "arch", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.4)
    register(X, f"{s} .win .art .cl", t + 0.55)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.6 + 0.7 * k)
        h = hmax * vals[k] / vmax
        X.tw(f'tl.from("{s} .bt{k}", {{y:{h + 20:.0f}, duration:0.7, ease:"power3.out"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .tg{k}", {{rotationX:-90, transformOrigin:"50% 0%", duration:0.45, ease:"power2.out"}}, {tk + 0.1:.3f});')
        v = str(it.get("value", ""))
        dec = len(v.split(".")[1]) if "." in v else 0
        X.used_text.update("0123456789.")
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .tg{k} .cv"); tl.to(o, {{v:{float(v)}, duration:0.7, ease:"power3.out", onUpdate:()=>{{el.textContent=o.v.toFixed({dec});}}}}, {tk:.3f});}})();')
        X.sfx(tk, "enter")
    if rt:
        tr = T(X, b, "at_ratio", t, t + 2.2)
        X.tw(f'tl.from("{s} .rt", {{scaleX:0, duration:0.4, ease:"power2.out"}}, {tr:.3f});')
        X.sfx(tr, "pop")


def tinlid(b, X, t, d, cid):
    """占比 = 俯视的圆铁盒盖：盖沿上那一段上了桃粉珐琅（从 12 点顺时针，按真实比例）；盖心的数字由上一年那页撕掉露出。"""
    gnd = ground(X)
    pct = max(0.5, min(99.5, float(b.get("pct", 50))))
    cx, cy, R = 380, 340, 292
    rr = (R + 236) / 2          # enamel band centre radius
    bw = R - 236
    fills = [f'<circle cx="{cx}" cy="{cy + 10}" r="{R + 4}" fill="{INK}" opacity=".55"/><circle cx="{cx}" cy="{cy}" r="{R}" fill="{IVORY}"/>',
             f'<circle cx="{cx}" cy="{cy}" r="228" fill="{JADE if GROUNDS[gnd]["win"] == MAROON else MAROON}"/>']
    deco = "".join(f'<line x1="{cx + 150 * math.cos(math.radians(a)):.1f}" y1="{cy + 150 * math.sin(math.radians(a)):.1f}" x2="{cx + 214 * math.cos(math.radians(a)):.1f}" y2="{cy + 214 * math.sin(math.radians(a)):.1f}" stroke="{GOLD}" stroke-width="1.6"/>'
                   for a in range(0, 360, 15))
    keys = pl(f'<circle cx="{cx}" cy="{cy}" r="{R}"/><circle cx="{cx}" cy="{cy}" r="236"/><circle cx="{cx}" cy="{cy}" r="220" stroke="{GOLD}" stroke-width="2"/>'
              f'<circle cx="{cx}" cy="{cy}" r="150" stroke="{GOLD}" stroke-width="1.5"/>{deco}')
    fid = f"st{cid}"
    enamel = (f'<g transform="translate(2.5 2)"><g class="en" filter="url(#{fid})"><circle class="arc" cx="{cx}" cy="{cy}" r="{rr}" fill="none" stroke="{PEACH}" stroke-width="{bw - 4}" '
              f'pathLength="100" stroke-dasharray="{pct:.2f} 100" transform="rotate(-90 {cx} {cy})"/></g></g>')
    win = art(cid, fills, keys).replace('<g class="kl"', enamel + '<g class="kl"', 1)
    big = b.get("big", f"{pct:g}%")
    px = 150
    while aw(big) * px > 410 and px > 100: px -= 6
    o = b.get("old", {})
    a_mid = math.radians(-90 + 360 * pct / 200)
    lab = b.get("labels", [])
    tags = ""
    for k, it in enumerate(lab[:2]):
        X.used_text.update(it.get("name", "") + str(it.get("value", "")))
        sw = PEACH if k == 0 else IVORY
        tags += (f'<div class="tag lb{k}" style="left:{[40, 400][k]}px;top:668px;width:320px;font-size:28px;display:flex;align-items:center;gap:12px">'
                 f'<i style="display:inline-block;width:30px;height:30px;border-radius:50%;background:{sw};box-shadow:inset 0 0 0 2px {INK}"></i>'
                 f'<span>{X.rich(it.get("name", ""))} <span class="v" style="font-size:36px">{X.rich(str(it.get("value", "")))}</span></span></div>')
    ovr = (f'<div class="num pn" style="left:0;top:{cy - px * 0.52:.0f}px;width:{BOX}px;text-align:center;font-size:{px}px">{X.rich(big)}</div>'
           + leaf(X, cx - 230, cy - 120, 460, 240, o.get("year", ""), o.get("value", ""), "", band=56)
           + tags)
    X.used_text.update(big)
    s = page(X, b, cid, t, d, gnd, win, ovr, "circle", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.4)
    register(X, f"{s} .win .art .cl", t + 0.65)
    X.tw(f'tl.from("{s} .leaf", {{y:-500, rotation:5, duration:0.45, ease:"power3.out"}}, {t + 0.45:.3f});')
    th = T(X, b, "at_hot", t, t + 1.4)
    X.tw(f'tl.fromTo("{s} .en", {{opacity:0, x:6, y:-4}}, {{opacity:1, x:0, y:0, duration:0.3, ease:"power2.out"}}, {th - 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .arc", {{strokeDasharray:"0 100"}}, {{strokeDasharray:"{pct:.2f} 100", duration:0.8, ease:"sine.inOut"}}, {th - 0.3:.3f});')
    tear(X, f"{s} .leaf", th + 0.4)
    register(X, f"{s} .pn", th + 0.44, dx=6, dy=6)
    X.tw(f'tl.from("{s} .lb0, {s} .lb1", {{rotationX:-90, transformOrigin:"50% 0%", duration:0.4, ease:"power2.out", stagger:0.12}}, {th + 0.9:.3f});')


def scale(b, X, t, d, cid):
    """比率 = 药房天平：两只砝码先后落到秤盘上，横梁先压到底再回到真实比例的倾角；毛利率印在秤脚下。"""
    gnd = ground(X)
    L_, R_ = b.get("left", {}), b.get("right", {})
    lv, rv = float(L_.get("value", 1)), float(R_.get("value", 1))
    ratio = (lv - rv) / max(1e-6, lv + rv)
    ang = max(3.0, min(20.0, 20.0 * abs(ratio)))       # angle = clamp of the ratio
    px0, py0, arm, chain = 380, 128, 250, 150

    def ends(a):
        r = math.radians(a)
        return (py0 + arm * math.sin(r), py0 - arm * math.sin(r))       # left end y, right end y (left heavier = left down)

    beam = (f'<rect x="{px0 - arm - 6}" y="{py0 - 7}" width="{2 * arm + 12}" height="14" rx="7" fill="{GOLD}"/>'
            f'<circle cx="{px0 - arm}" cy="{py0}" r="10" fill="{GOLD}"/><circle cx="{px0 + arm}" cy="{py0}" r="10" fill="{GOLD}"/>')
    beam_k = pl(f'<rect x="{px0 - arm - 6}" y="{py0 - 7}" width="{2 * arm + 12}" height="14" rx="7"/>')

    def pan(x, w_):
        return (f'<line x1="{x}" y1="0" x2="{x - 92}" y2="{chain}" stroke="{GOLD}" stroke-width="2.4"/><line x1="{x}" y1="0" x2="{x + 92}" y2="{chain}" stroke="{GOLD}" stroke-width="2.4"/>'
                f'<path d="M{x - 104},{chain} Q{x},{chain + 58} {x + 104},{chain} Z" fill="{IVORY}" stroke="{INK}" stroke-width="3"/>')

    lw_ = 150
    rw_ = lw_ * math.sqrt(rv / lv)
    wt = lambda x, w_, cls: (f'<g class="{cls}"><rect x="{x - w_ / 2:.1f}" y="{chain - w_ * 0.62:.1f}" width="{w_:.1f}" height="{w_ * 0.62:.1f}" rx="{w_ * 0.08:.1f}" fill="{PEACH}" stroke="{INK}" stroke-width="3"/>'
                             f'<rect x="{x - w_ * 0.18:.1f}" y="{chain - w_ * 0.78:.1f}" width="{w_ * 0.36:.1f}" height="{w_ * 0.16:.1f}" rx="3" fill="{PEACH}" stroke="{INK}" stroke-width="2.4"/></g>')
    fid = f"st{cid}"
    stand_f = (f'<path d="M{px0 - 130},470 H{px0 + 130} L{px0 + 96},432 H{px0 - 96} Z" fill="{INK}"/>'
               f'<rect x="{px0 - 12}" y="{py0}" width="24" height="304" fill="{IVORY}"/><path d="M{px0 - 26},{py0 + 6} L{px0},{py0 - 40} L{px0 + 26},{py0 + 6} Z" fill="{GOLD}"/>')
    stand_k = pl(f'<path d="M{px0 - 130},470 H{px0 + 130} L{px0 + 96},432 H{px0 - 96} Z"/><rect x="{px0 - 12}" y="{py0}" width="24" height="304"/>')
    yl0, yr0 = ends(0)
    win = (f'<svg class="art" viewBox="0 0 {BOX} {BOX}"><defs>{stip_filter(fid)}</defs>'
           f'<circle cx="380" cy="380" r="330" fill="none" stroke="{GOLD}" stroke-width="1.2"/>'
           f'<g transform="translate(2.5 2)"><g class="cl" filter="url(#{fid})">{stand_f}</g></g>'
           f'<g class="kl" stroke="{INK}" stroke-width="3.2">{stand_k}</g>'
           f'<g class="beam"><g filter="url(#{fid})">{beam}</g><g class="kl" stroke="{INK}" stroke-width="2.4">{beam_k}</g></g>'
           f'<g class="pan pnl" transform="translate(0 {yl0:.1f})"><g filter="url(#{fid})">{pan(px0 - arm, 0)}{wt(px0 - arm, lw_, "wl")}</g></g>'
           f'<g class="pan pnr" transform="translate(0 {yr0:.1f})"><g filter="url(#{fid})">{pan(px0 + arm, 0)}{wt(px0 + arm, rw_, "wr")}</g></g></svg>')
    X.used_text.update(L_.get("name", "") + str(L_.get("value", "")) + R_.get("name", "") + str(R_.get("value", "")))
    big = b.get("big", "")
    bpx = 216                      # Abril digits are 0.711 em tall: 216 px font = 154 px glyphs (9:16)
    while aw(big) * bpx > 700 and bpx > 150: bpx -= 4
    X.used_text.update(big + b.get("big_label", ""))
    ylf, yrf = ends(ang)
    # the margin sits on its own ivory plate (stepped Deco ends, gold rule), box y 534–714: clear of the tags above
    # (left tag ends ≈ 498) and of the foot plate below (page y 1184 vs 1252 in 9:16)
    py_, ph_ = 534, 180
    plate = (f'<svg class="mpl" viewBox="0 0 760 {ph_}" style="position:absolute;left:0;top:{py_}px;width:760px;height:{ph_}px">'
             f'<path d="M30,0 H730 V18 H748 V36 H760 V{ph_ - 36} H748 V{ph_ - 18} H730 V{ph_} H30 V{ph_ - 18} H12 V{ph_ - 36} H0 V36 H12 V18 H30 Z" fill="{IVORY}"/>'
             f'<path d="M40,10 H720 V26 H738 V44 H750 V{ph_ - 44} H738 V{ph_ - 26} H720 V{ph_ - 10} H40 V{ph_ - 26} H22 V{ph_ - 44} H10 V44 H22 V26 H40 Z" fill="none" stroke="{GOLD}" stroke-width="2"/></svg>')
    ovr = (f'<div class="tag tl" style="left:24px;top:{ylf + chain + 46:.0f}px;font-size:28px;text-align:center">{X.rich(L_.get("name", ""))}<br><span class="v" style="font-size:40px">{X.rich(str(L_.get("value", "")))}</span></div>'
           f'<div class="tag tr" style="right:24px;top:{yrf + chain + 46:.0f}px;font-size:28px;text-align:center">{X.rich(R_.get("name", ""))}<br><span class="v" style="font-size:40px">{X.rich(str(R_.get("value", "")))}</span></div>'
           f'<div class="mplw" style="position:absolute;left:0;top:0;width:760px;height:760px">{plate}'
           f'<div class="sn" style="position:absolute;left:0;top:{py_ + ph_ / 2 - 0.528 * bpx:.0f}px;width:{BOX}px;text-align:center;font-family:var(--f-num);'
           f'font-size:{bpx}px;line-height:1;color:{MAROON};white-space:nowrap">{X.rich(big)}</div></div>')
    s = page(X, b, cid, t, d, gnd, win, ovr, "circle", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.4)
    register(X, f"{s} .win .art .cl", t + 0.6)
    t1 = T(X, b, "at_left", t, t + 0.9)
    t2 = T(X, b, "at_right", t, t + 1.7)
    so = f'svgOrigin:"{px0} {py0}"'
    X.tw(f'tl.from("{s} .wl", {{y:-420, duration:0.4, ease:"power2.in"}}, {t1 - 0.4:.3f});')
    yl1, yr1 = ends(20)
    X.tw(f'tl.to("{s} .beam", {{rotation:-20, {so}, duration:0.5, ease:"back.out(1.6)"}}, {t1:.3f});')
    X.tw(f'tl.to("{s} .pnl", {{y:{yl1:.1f}, duration:0.5, ease:"back.out(1.6)"}}, {t1:.3f});')
    X.tw(f'tl.to("{s} .pnr", {{y:{yr1:.1f}, duration:0.5, ease:"back.out(1.6)"}}, {t1:.3f});')
    X.sfx(t1, "hit")
    X.tw(f'tl.from("{s} .wr", {{y:-420, duration:0.4, ease:"power2.in"}}, {t2 - 0.4:.3f});')
    X.tw(f'tl.to("{s} .beam", {{rotation:{-ang:.2f}, {so}, duration:0.6, ease:"power2.out"}}, {t2:.3f});')
    X.tw(f'tl.to("{s} .pnl", {{y:{ylf:.1f}, duration:0.6, ease:"power2.out"}}, {t2:.3f});')
    X.tw(f'tl.to("{s} .pnr", {{y:{yrf:.1f}, duration:0.6, ease:"power2.out"}}, {t2:.3f});')
    X.sfx(t2, "hit")
    X.tw(f'tl.from("{s} .tl", {{rotationX:-90, transformOrigin:"50% 0%", duration:0.4, ease:"power2.out"}}, {t1 + 0.3:.3f});')
    X.tw(f'tl.from("{s} .tr", {{rotationX:-90, transformOrigin:"50% 0%", duration:0.4, ease:"power2.out"}}, {t2 + 0.3:.3f});')
    register(X, f"{s} .mpl", t2 + 0.5, dx=0, dy=6)
    register(X, f"{s} .sn", t2 + 0.62, dx=6, dy=6)


def matchbox(b, X, t, d, cid):
    """排行 = 一列火柴盒贴：每只盒子先出外壳（左端一条擦火皮），再把内屉（桃粉）抽到真实比例的宽度；名字和数印在盒子上方的票签上。"""
    gnd = ground(X)
    items = b.get("items", [])[:5]
    n = len(items)
    vmax = max(float(it.get("value", 0) or 0) for it in items) or 1
    x0, wmax, bh, lab_h, gap = 150, 540, 66, 52, 30
    row = lab_h + bh + gap
    y0 = 744 - 40 - n * row + gap
    rows, fills1, fills2, keys = "", "", "", ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = max(12.0, wmax * v / vmax)
        y = y0 + k * row + lab_h
        fills1 += (f'<g class="sl{k}"><rect x="{x0}" y="{y}" width="{w:.1f}" height="{bh}" rx="3" fill="{IVORY}"/>'
                   f'<rect x="{x0}" y="{y}" width="{min(10, w / 3):.1f}" height="{bh}" fill="#5a3a26"/></g>')
        inner = ""
        if w > 60:
            inner = (f'<rect x="{x0 + 18}" y="{y + 12}" width="{w - 30:.1f}" height="{bh - 24}" fill="none" stroke="{JADE}" stroke-width="2.4"/>'
                     + "".join(f'<path d="M{x0 + 40 + 46 * j},{y + bh / 2} l7,-9 l7,9 l-7,9 Z" fill="{JADE}"/>' for j in range(int((w - 60) // 46))))
        fills2 += f'<g class="dr{k}"><rect x="{x0 + min(10, w / 3):.1f}" y="{y + 6}" width="{max(2, w - min(10, w / 3) - 4):.1f}" height="{bh - 12}" fill="{PEACH}"/>{inner}</g>'
        keys += pl(f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bh}" rx="3"/>')
        nm, lv = it.get("name", ""), str(it.get("label", it.get("value", "")))
        X.used_text.update(nm + lv + str(k + 1))
        rows += (f'<div class="lab rk{k}" style="left:{x0 - 74}px;top:{y + bh / 2 - 27}px;width:54px;height:54px;border-radius:50%;background:{GOLD};color:{INK};'
                 f'font-family:var(--f-num);font-weight:400;font-size:34px;text-align:center;line-height:56px">{k + 1}</div>'
                 f'<div class="lab nm{k}" style="left:{x0}px;top:{y - lab_h + 2}px;font-size:32px;color:{IVORY}">{X.rich(nm)}'
                 f'<span style="font-family:var(--f-num);font-weight:400;font-size:42px;margin-left:16px;color:{PEACH}">{X.rich(lv)}</span></div>')
    win = art(cid, [fills1, fills2], keys)
    s = page(X, b, cid, t, d, gnd, win, rows, "arch", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.4)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.55 + 0.32 * k)
        X.tw(f'tl.fromTo("{s} .sl{k}", {{opacity:0, x:6, y:-4}}, {{opacity:1, x:0, y:0, duration:0.3, ease:"power2.out"}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .dr{k}", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:0.5, ease:"power3.out"}}, {tk + 0.1:.3f});')
        X.tw(f'tl.from("{s} .rk{k}", {{scale:0, duration:0.3, ease:"back.out(1.6)"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .nm{k}", {{x:6, y:-4, opacity:0, duration:0.35, ease:"power2.out"}}, {tk + 0.2:.3f});')
        X.sfx(tk, "click")


def statement(b, X, t, d, cid):
    """判断：大数字由上一年那页撕掉露出；下面一条丝带把它说成一句话（每 100 元收入落下多少）。窗里一只素瓷大瓶。"""
    gnd = ground(X)
    big, small, unit = b.get("big", ""), b.get("small", ""), b.get("unit", "")
    px = 320
    while num_width(big, small, unit, px) > 760 and px > 200: px -= 10
    nw = num_width(big, small, unit, px)
    o = b.get("old", {})
    body, cap, rib, nb, hi = bottle_paths(380, 740, 640)
    fills = [f'<path d="{body}" fill="{IVORY}" opacity=".16"/>', f'<path d="{cap}" fill="{PEACH}" opacity=".22"/>']
    keys = pl(f'<path d="{body}" stroke="{GOLD}" stroke-width="2"/><path d="{cap}" stroke="{GOLD}" stroke-width="2"/>'
              f'<circle cx="380" cy="380" r="310" stroke="{GOLD}" stroke-width="1.2"/>')
    win = art(cid, fills, keys)
    ln = b.get("line", "")
    X.used_text.update(ln)
    ny = 170
    ovr = (number(X, (BOX - nw) / 2 - 10, ny, big, small, unit, px, w=nw + 40, align="left")
           + leaf(X, (BOX - max(nw, 560)) / 2 - 20, 130, max(nw, 560) + 40, 420, o.get("year", ""), o.get("value", ""), o.get("unit", ""))
           + (f'<div class="rib ln" style="left:380px;top:{ny + px * 1.04 + 40:.0f}px;font-size:44px;transform:translateX(-50%)">{X.rich(ln)}</div>' if ln else ""))
    s = page(X, b, cid, t, d, gnd, win, ovr, "circle", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.4)
    register(X, f"{s} .win .art .cl", t + 0.6)
    X.tw(f'tl.from("{s} .leaf", {{y:-700, rotation:4, duration:0.45, ease:"power3.out"}}, {t + 0.3:.3f});')
    tt = T(X, b, "at_tear", t, t + 1.4)
    tear(X, f"{s} .leaf", tt)
    register(X, f"{s} .hn", tt + 0.04, dx=6, dy=6)
    if ln:
        tl_ = T(X, b, "at_line", t, tt + 0.9)
        X.tw(f'tl.from("{s} .ln", {{scaleX:0, duration:0.45, ease:"power2.out"}}, {tl_:.3f});')
        X.sfx(tl_, "pop")


def label(b, X, t, d, cid):
    """落版：一张国货圆标（扇贝边、金线、三行数），每一行像印版一样套准落下；题版写示例频道。"""
    gnd = ground(X)
    rows = b.get("rows", [])[:3]
    cx, cy = 380, 372
    sc = "".join(f'<circle cx="{cx + 318 * math.cos(math.radians(a)):.1f}" cy="{cy + 318 * math.sin(math.radians(a)):.1f}" r="22"/>' for a in range(0, 360, 10))
    fills = [f'<g fill="{IVORY}"><circle cx="{cx}" cy="{cy}" r="318"/>{sc}</g>',
             f'<rect x="{cx - 300}" y="{cy - 40}" width="600" height="80" fill="{PEACH}" opacity="0"/>']
    keys = pl(f'<circle cx="{cx}" cy="{cy}" r="296" stroke="{GOLD}" stroke-width="2.4"/><circle cx="{cx}" cy="{cy}" r="282" stroke="{GOLD}" stroke-width="1.2"/>'
              f'<line x1="{cx - 230}" y1="{cy - 70}" x2="{cx + 230}" y2="{cy - 70}" stroke="{GOLD}" stroke-width="1.6"/>'
              f'<line x1="{cx - 230}" y1="{cy + 70}" x2="{cx + 230}" y2="{cy + 70}" stroke="{GOLD}" stroke-width="1.6"/>')
    win = art(cid, fills, keys)
    html = ""
    ys = [cy - 190, cy - 52, cy + 86]
    for k, r in enumerate(rows):
        X.used_text.update(r.get("k", "") + r.get("v", ""))
        html += (f'<div class="lab rw{k}" style="left:0;width:{BOX}px;top:{ys[k]}px;text-align:center;color:{MAROON};font-size:34px;line-height:1.1">'
                 f'{X.rich(r.get("k", ""))}<br><span style="font-family:var(--f-num);font-weight:400;font-size:66px;color:{INK}">{X.rich(r.get("v", ""))}</span></div>')
    bb = dict(b, sub=str((X.v.get("meta") or {}).get("channel") or ""))
    s = page(X, bb, cid, t, d, gnd, win, html, "circle", b.get("note"))
    draw_keys(X, f"{s} .win .art", t + 0.35)
    register(X, f"{s} .win .art .cl", t + 0.5)
    for k in range(len(rows)):
        register(X, f"{s} .rw{k}", t + 0.9 + 0.35 * k, dx=6, dy=6)
        X.sfx(t + 0.9 + 0.35 * k, "click")


SCENES = {"hero": hero, "leaves": leaves, "bottles": bottles, "tinlid": tinlid, "scale": scale,
          "matchbox": matchbox, "statement": statement, "label": label}


# ---------------------------------------------------------------- effects in this style (shared fx beats)
# four card stocks: celadon card, jade card, maroon card, ivory card
STYLE["fx_themes"] = {
    "paper": {"bg": CEL, "fg": INK, "muted": "#3f5a50", "accent": MAROON, "card": IVORY, "card-fg": INK, "line": "rgba(43,29,20,.22)"},
    "ink":   {"bg": JADE, "fg": IVORY, "muted": "#cfe0d2", "accent": PEACH, "card": IVORY, "card-fg": INK, "line": "rgba(244,236,214,.3)"},
    "red":   {"bg": MAROON, "fg": IVORY, "muted": "#efd7c8", "accent": PEACH, "card": IVORY, "card-fg": INK, "line": "rgba(244,236,214,.3)"},
    "lemon": {"bg": IVORY, "fg": INK, "muted": "#5a4632", "accent": MAROON, "card": "#fffaf0", "card-fg": INK, "line": "rgba(43,29,20,.2)"},
}
PLATE_OF = {"paper": JADE, "ink": MAROON, "red": JADE, "lemon": MAROON}

FX_CSS = r"""
/* an effect's ground is the same lithograph card: stipple + mottling over the stock colour */
.st-yuefen .fx { background-image:__STIP__, __MOTTLE__ !important; background-size:520px, 900px !important; }
.st-yuefen .fx .big, .st-yuefen .fx .op .op-t { font-family:var(--f-display); font-weight:900; letter-spacing:.06em; text-shadow:.04em .04em 0 color-mix(in srgb, var(--accent) 70%, #2b1d14); }
.st-yuefen .fx .col > .sub { background:var(--card); color:var(--card-fg); padding:.6vmin 2vmin .8vmin; letter-spacing:.2em; border-radius:4px; box-shadow:inset 0 0 0 2px #b8923a; }
/* the page around an effect (FX_FRAME): gold double border, stepped corners, cartouche header, foot plate caption */
.ctx.yfx .yf-bd { position:absolute; left:0; top:0; }
.ctx.yfx .hd { left:120px; right:120px; top:56px; height:auto; border:none; display:flex; justify-content:center; }
.ctx.yfx .hd .ct { background:#f4ecd6; color:#2f6f62; font-family:var(--f-display); font-weight:900; font-size:46px; letter-spacing:.08em; padding:12px 56px 14px;
  text-shadow:3px 3px 0 #6b1f2a; clip-path:polygon(16px 0, calc(100% - 16px) 0, calc(100% - 16px) 10px, 100% 10px, 100% calc(100% - 10px), calc(100% - 16px) calc(100% - 10px), calc(100% - 16px) 100%, 16px 100%, 16px calc(100% - 10px), 0 calc(100% - 10px), 0 10px, 16px 10px);
  white-space:nowrap; }
.ctx.yfx .cap { bottom:70px; padding:0 200px; }
.ctx.yfx .cap > span { background:#f4ecd6; color:#6b1f2a; font-family:var(--f-cap); font-weight:800; border-radius:6px; padding:10px 54px 12px;
  box-shadow:0 0 0 10px var(--yf-plate), 0 0 0 12px #b8923a; position:relative; }
.ctx.yfx .cap .em .emt { background:#f2b8a2; color:#6b1f2a; padding:0 .12em; } .ctx.yfx .cap .em .emb { display:none; }
.ctx.yfx .ft { left:120px; right:120px; bottom:24px; opacity:1; color:var(--fg); font-size:22px; }
#root.v .ctx.yfx .hd { top:226px; }
#root.v .ctx.yfx .cap { top:1300px; bottom:auto; padding:0 140px; }
#root.v .ctx.yfx .cap .em .emt { background:#f2b8a2; color:#6b1f2a; padding:0 .12em; } .ctx.yfx .cap .em .emb { display:none; }
.ctx.yfx .ft { left:120px; right:120px; top:1452px; bottom:auto; font-size:22px; flex-direction:column; align-items:flex-start; gap:4px; }
"""
STYLE["css"] = FX_CSS.replace("__STIP__", STIP).replace("__MOTTLE__", MOTTLE_FX)


def FX_FRAME(X, cid, t, d, p, parts):
    """the card around a shared effect in yuefen: the gold double border with Deco corner fans, the topic on an ivory
    cartouche, the spoken line on an ivory ticket set in a coloured foot plate, the footnote / source under it."""
    th = p.get("theme") if p.get("theme") in STYLE["fx_themes"] else "paper"
    sty = parts["sty"] + f";--yf-plate:{PLATE_OF[th]}"
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "") + border(X.W, X.H, cid)
             + f'<div class="hd"><div class="ct">{parts["topic"] or X.rich(X.channel)}</div></div>'
             + f'<div class="cap"><span style="font-size:{max(38, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx yfx{' photo' if parts['photo'] else ''}", 30, track=20, sty=sty)
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .hd .ct", {{x:6, y:-4, opacity:0}}, {{x:0, y:0, opacity:1, duration:0.42, ease:"power2.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .cap > span", {{x:6, y:-4, opacity:0}}, {{x:0, y:0, opacity:1, duration:0.42, ease:"power2.out"}}, {t + 0.12:.3f});')


# the subtitle: an ivory ticket with gold diamonds at both ends, maroon bold Song, set inside the foot plate
STYLE["css"] += """
.st-yuefen .clip.cap .cp { position:relative; letter-spacing:.06em; line-height:1.3; box-shadow:inset 0 0 0 2px #b8923a; }
.st-yuefen .clip.cap .cp::before, .st-yuefen .clip.cap .cp::after { content:""; position:absolute; top:50%; width:14px; height:14px; margin-top:-7px;
  background:#b8923a; transform:rotate(45deg); }
.st-yuefen .clip.cap .cp::before { left:22px; } .st-yuefen .clip.cap .cp::after { right:22px; }
#root.v.st-yuefen { --cap-bottom:520px; }
#root.v.st-yuefen .clip.cap { padding-left:120px; padding-right:120px; }
#root.h.st-yuefen .clip.cap { padding-left:950px; padding-right:130px; }
"""
