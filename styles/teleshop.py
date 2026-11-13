"""teleshop · 电视购物 —— 一条 1990 年代电视购物广告，一本正经地播：真实公司的年度数字被当成「奇迹商品」来卖，数字本身一个不改。

画面是一台显像管电视里的广告：底是揉皱的金箔（湍流 + 光照做出的褶皱高光和暗折痕，左上来光），红绸带波动的题版，
立体金红字（金面渐变 + 3 px 暗红描边 + 10–14 px 右下阶梯挤出 + 左上 2 px 白色高光），红色爆炸价签、圆形印章、底部滚动字幕条。
整屏带扫描线（2 px 周期）、桶形暗角、高对比边缘 1.5 px 红青色散、每 5 秒下行一次的同步条、逐帧重撒的噪点，四角 46 px 圆角显像管遮罩。
第一页是开机：一条白线 7 帧张满全屏、3 帧雪花、出画面；最后一页收成一条线再缩成一个点（9 帧）。

竖屏固定版式：y 210–330 红绸题版写本页标题（立体金字 76–92 px）；y 360–1240 是「商品台」= 这一页的图表物件，左上打光，
最多 3 个四角星在主角上闪；y 1270–1350 奶油色卖点牌写一句解释数字的话；y 1376–1456 红色飘带字幕（奶油色 44 px，上下金线）；
y 1470–1508 出处条（70% 黑底奶油字）；y 1560–1620 红色滚动字幕条（家具，内容取自本片字幕，用 ★ 隔开），下面是金箔和红绸垂幔。
横屏：商品台在左 58%，题版、卖点牌、字幕、出处在右侧叠放，滚动条在底部 y 1000–1050。

图表都是电视购物里的东西：burst 爆炸价签大数字（去年的「原价」在后面被两道红杠划掉）· versus 去年 vs 今年分屏，闪电金分割线，
台子高度按真实比例，输的一边褪色发冷 · bundle 礼盒按真实比例的宽度一个个砸下来叠成一摞，最后一张合计价签 ·
seal 圆形红印章「认准此数」盖在百个圆点环上（亮起的点数 = 真实百分比）· countdown 销量榜式金牌匾，从末名翻到第一名，宽度按真实比例 ·
endcard 三个数的总结牌（不出现任何电话号码）。
动作：砸（2.2 → 0.94 → 1.0，9 帧，1 帧白闪 + 6 px 震屏）、盖章、爆开、价格两帧金白闪两次、停留时慢推 1.00 → 1.05；
换页是一道红绸幕 10 帧横扫过去，前缘带金流苏，新画面已经在幕后面。

每个 beat 写 "head"（题版标题）、"claim"（卖点牌一句话）、"src"（出处）；场景参数见各场景函数说明。不出主持人。
"""
import math
from urllib.parse import quote

GOLD, GOLD_HI, GOLD_LO = "#d9a441", "#f6dc8a", "#a8741f"
SILK, SILK_HI, SILK_LO = "#b3121b", "#e0453a", "#6f0a10"
CREAM, BLACK, COLD = "#fff3cf", "#1a0d08", "#3d6f8f"
DEEP = "#4a0508"
NUM_HI, NUM_LO = "#ff5a3c", "#c8141c"
BW, BH = 960, 880          # every product shot is drawn in a 960 × 880 box (the 9:16 stage), scaled into place in 16:9
ANTON = {"1": 0.331, ".": 0.229, ",": 0.236, "%": 1.057, "+": 0.355, "-": 0.311, " ": 0.234}
FPS = 30.0
F = 1 / FPS
WIPE = 10 * F              # the silk curtain crosses the frame in 10 frames
CURT_W = 380

STYLE = {
    "name": "电视购物", "en": "Teleshop", "benchmarks": ["1990 年代电视购物广告", "促销爆炸贴与价签", "显像管电视画面"],
    "tokens": {
        "bg": GOLD, "fg": BLACK, "muted": "#4a2a10", "accent": SILK, "accent2": SILK_LO, "alert": NUM_LO,
        "line": "rgba(26,13,8,.3)", "paper": CREAM, "ink": BLACK, "card": CREAM, "card-fg": SILK_LO,
        "gold": GOLD, "silk": SILK, "cream": CREAM, "cold": COLD,
        # caption: a red silk ribbon with notched ends and gold rules, cream weight-900 text (CSS below)
        "cap-bg": SILK, "cap-fg": CREAM, "cap-size": "44px", "cap-weight": "900", "cap-pad": "0 64px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "464px", "cap-em": GOLD_HI,
        "punch-top": "70%", "punch-size": "72px",
    },
    "fonts": {"display": ["zcool-kuhei", "alibaba-puhuiti"], "body": "alibaba-puhuiti", "cap": "alibaba-puhuiti",
              "num": ["anton", "alibaba-puhuiti"], "latin": ["anton", "alibaba-puhuiti"], "mono": "jetbrains-mono"},
    "motion": {"ease": "power4.out", "dur": 0.25, "stagger": 0.05, "cut": "hard", "transition": "dip", "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "none"},
    "caption_plate": False,
    "safe_exempt": [".tsv", ".tsk", ".tsb", ".crt"],      # valance, ticker, bottom swag, the CRT glass: furniture
    "sfx": {"transition": ("whoosh", 0.4), "enter": ("pop", 0.3), "pop": ("pop", 0.35), "hit": ("hit", 0.45), "slam": ("slam", 0.45),
            "stamp": ("boom", 0.35), "thud": ("hit", 0.35), "count": ("tick", 0.25), "click": ("click", 0.3), "on": ("glitch", 0.3),
            "mascot": None, "line": ("click", 0.25)},
}


# ---------------------------------------------------------------- textures
def _uri(svg):
    return "url('data:image/svg+xml," + quote(svg, safe="") + "')"


def _ramp(cols):
    """hex colours -> three feFunc tableValues strings (r, g, b)."""
    rs, gs, bs = [], [], []
    for c in cols:
        rs.append(f"{int(c[1:3], 16) / 255:.3f}")
        gs.append(f"{int(c[3:5], 16) / 255:.3f}")
        bs.append(f"{int(c[5:7], 16) / 255:.3f}")
    return " ".join(rs), " ".join(gs), " ".join(bs)


FOIL_RAMP = _ramp(["#3e2606", "#563509", "#6e4510", "#8a5a16", GOLD_LO, "#c28b30", GOLD, "#ecc56a", GOLD_HI, "#fff1bf"])


def foil_svg(W, H, seed):
    """crumpled gold foil: two creased height fields (turbulence, different grain directions) averaged, lit from the
    top-left (diffuse + specular), mapped onto the gold ramp."""
    r, g, b = FOIL_RAMP
    return (f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}'>"
            f"<filter id='f' x='0' y='0' width='100%' height='100%' color-interpolation-filters='sRGB'>"
            f"<feTurbulence type='turbulence' baseFrequency='0.0042 0.0068' numOctaves='3' seed='{seed}' result='t1'/>"
            f"<feTurbulence type='turbulence' baseFrequency='0.0071 0.0038' numOctaves='3' seed='{seed + 50}' result='t2'/>"
            "<feComposite in='t1' in2='t2' operator='arithmetic' k1='0' k2='.5' k3='.5' k4='0' result='t'/>"
            "<feColorMatrix in='t' values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  .5 .3 .2 0 0' result='h'/>"
            "<feDiffuseLighting in='h' surfaceScale='17' diffuseConstant='1.0' lighting-color='#ffffff' result='d'><feDistantLight azimuth='225' elevation='40'/></feDiffuseLighting>"
            "<feSpecularLighting in='h' surfaceScale='17' specularConstant='.75' specularExponent='28' lighting-color='#fff4c8' result='s'><feDistantLight azimuth='225' elevation='50'/></feSpecularLighting>"
            f"<feComponentTransfer in='d' result='g'><feFuncR type='table' tableValues='{r}'/><feFuncG type='table' tableValues='{g}'/><feFuncB type='table' tableValues='{b}'/></feComponentTransfer>"
            "<feComposite in='s' in2='g' operator='arithmetic' k1='0' k2='.5' k3='1' k4='0'/>"
            f"</filter><rect width='{W}' height='{H}' filter='url(#f)'/></svg>")


def foil_uri(W, H, seed):
    return _uri(foil_svg(W, H, seed))


NOISE = _uri("<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n' x='0' y='0' width='100%' height='100%'>"
             "<feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' seed='4' stitchTiles='stitch'/>"
             "<feColorMatrix values='.33 .33 .33 0 0  .33 .33 .33 0 0  .33 .33 .33 0 0  0 0 0 0 1'/></filter><rect width='300' height='300' filter='url(#n)'/></svg>")
STATIC = _uri("<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240'><filter id='n' x='0' y='0' width='100%' height='100%'>"
              "<feTurbulence type='fractalNoise' baseFrequency='1.4 .35' numOctaves='1' seed='11' stitchTiles='stitch'/>"
              "<feColorMatrix values='1.4 0 0 0 -.2  1.4 0 0 0 -.2  1.4 0 0 0 -.2  0 0 0 0 1'/></filter><rect width='240' height='240' filter='url(#n)'/></svg>")
FOLDS = (f"repeating-linear-gradient(90deg, {SILK_LO} 0px, {SILK} 30px, {SILK_HI} 52px, {SILK} 74px, {SILK_LO} 104px)")
# the caption ribbon keeps its folds dark enough for 6:1 cream text everywhere
CAP_FOLDS = f"repeating-linear-gradient(90deg, #8c0d15 0px, {SILK} 36px, #a8101a 60px, #8c0d15 96px)"
SEEDS = [7, 23, 41, 58, 73, 89, 104, 131]


def anton_w(s):
    """width of a string in Anton, in em (CJK glyphs count 1)."""
    w = 0.0
    for c in str(s):
        if c.isdigit(): w += 0.494
        elif c in ANTON: w += ANTON[c]
        else: w += 1.0
    return w


# ---------------------------------------------------------------- the lettering
def g3(X, text, px, kind="gold", cls="", num=False, depth=None):
    """3D lettering: extrusion (stepped down-right) + outline + white top-left highlight + gradient face.
    kind "gold": gold face, dark-red outline; "red": red face, cream outline (numerals)."""
    t = X.rich(text)
    dp = depth if depth is not None else max(3, min(14, round(px * 0.11)))
    ex = SILK_LO
    sw = 6 if px >= 60 else 4
    ol = SILK_LO
    if kind == "red":               # red numerals on cream: dark-red outline so the edge holds against the plate
        ol, ex = DEEP, DEEP
    if kind == "title":             # banner titles: near-white gold face, 4 px deep outline, 12 px extrusion
        ol, ex, sw, dp = DEEP, DEEP, 8, 12
    steps = ", ".join(f"{k}px {k}px 0 {ex}" for k in range(1, dp + 1))
    steps += f", {dp + 4}px {dp + 6}px {max(6, dp)}px rgba(40,8,0,.45)"
    fam = "var(--f-num)" if num else "var(--f-display)"
    return (f'<span class="g3 {kind} {cls}" data-layout-allow-overlap style="font-size:{px:.0f}px;font-family:{fam}">'
            f'<span class="x" aria-hidden="true" style="-webkit-text-stroke:{sw}px {ex};text-shadow:{steps}">{t}</span>'
            f'<span class="o" aria-hidden="true" style="-webkit-text-stroke:{sw}px {ol};color:{ol}">{t}</span>'
            f'<span class="h" aria-hidden="true">{t}</span><span class="f">{t}</span></span>')


def starburst(n, R, r, cx=0.0, cy=0.0, rot=-90.0):
    pts = []
    for k in range(2 * n):
        a = math.radians(rot + 180.0 * k / n)
        rr = R if k % 2 == 0 else r
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return " ".join(pts)


def sparkle(cls, x, y, s=1.0):
    """a 4-point glint (white core, gold glow) centred on (x, y) in box coordinates."""
    return (f'<svg class="spk {cls}" viewBox="-50 -50 100 100" style="left:{x - 50 * s:.0f}px;top:{y - 50 * s:.0f}px;width:{100 * s:.0f}px;height:{100 * s:.0f}px">'
            '<path d="M0,-48 C4,-8 8,-4 48,0 C8,4 4,8 0,48 C-4,8 -8,4 -48,0 C-8,-4 -4,-8 0,-48Z" fill="#fffbe8"/>'
            '<circle r="7" fill="#ffffff"/></svg>')


def silk_svg(w, h, uid, amp=7.0, wl=260.0, ph=0.0, tail=30, cls="silk", deep=True):
    """a red silk band: wavy top and bottom edges, swallowtail ends, soft vertical folds (a fold rect slides to make it wave), gold piping."""
    top, bot = [], []
    n = int(w // 20) + 1
    for k in range(n + 1):
        x = min(w, k * 20)
        yt = amp + amp * math.sin(2 * math.pi * x / wl + ph)
        yb = h - amp + amp * math.sin(2 * math.pi * x / wl + ph + 0.9)
        top.append((x, yt))
        bot.append((x, yb))
    d = f"M0,{top[0][1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in top[1:])
    d += f" L{w - tail},{h / 2:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in reversed(bot)) + f" L{tail},{h / 2:.1f} Z"
    pt = "M" + " L".join(f"{x:.1f},{y + 3:.1f}" for x, y in top)
    pb = "M" + " L".join(f"{x:.1f},{y - 3:.1f}" for x, y in bot)
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" style="overflow:visible">'
            f'<defs><linearGradient id="fo{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="110" y2="0" spreadMethod="repeat">'
            + (f'<stop offset="0" stop-color="#6a0910"/><stop offset=".3" stop-color="#860c15"/><stop offset=".5" stop-color="#981019"/>'
               f'<stop offset=".7" stop-color="#860c15"/><stop offset="1" stop-color="#6a0910"/></linearGradient>' if deep else
               f'<stop offset="0" stop-color="{SILK_LO}"/><stop offset=".28" stop-color="{SILK}"/><stop offset=".5" stop-color="{SILK_HI}"/>'
               f'<stop offset=".7" stop-color="{SILK}"/><stop offset="1" stop-color="{SILK_LO}"/></linearGradient>')
            + f'<linearGradient id="sh{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="{".1" if deep else ".22"}"/>'
            f'<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#2a0004" stop-opacity=".38"/></linearGradient>'
            f'<clipPath id="cp{uid}"><path d="{d}"/></clipPath></defs>'
            f'<path d="{d}" transform="translate(10 12)" fill="{SILK_LO}" opacity=".55"/>'
            f'<g clip-path="url(#cp{uid})"><rect class="fold" x="-440" y="0" width="{w + 880}" height="{h}" fill="url(#fo{uid})"/>'
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="url(#sh{uid})"/></g>'
            f'<path d="{pt}" fill="none" stroke="#f2b61e" stroke-width="3"/><path d="{pb}" fill="none" stroke="#f2b61e" stroke-width="3"/></svg>')


def swags(W, h, uid, n, up=False, cls=""):
    """theatre swags: a straight rail with n hanging (or, up=True, rising) silk swags edged in gold fringe, tassels at the joins."""
    rail = h * 0.3
    seg = W / n
    paths, fr = [], []
    for k in range(n):
        x0, x1 = k * seg, (k + 1) * seg
        xm = (x0 + x1) / 2
        if not up:
            paths.append(f"M{x0:.0f},{rail:.0f} Q{xm:.0f},{h * 1.32:.0f} {x1:.0f},{rail:.0f} Z")
            fr.append(f"M{x0:.0f},{rail:.0f} Q{xm:.0f},{h * 1.32:.0f} {x1:.0f},{rail:.0f}")
        else:
            paths.append(f"M{x0:.0f},{h - rail:.0f} Q{xm:.0f},{-h * 0.32:.0f} {x1:.0f},{h - rail:.0f} Z")
            fr.append(f"M{x0:.0f},{h - rail:.0f} Q{xm:.0f},{-h * 0.32:.0f} {x1:.0f},{h - rail:.0f}")
    ry = 0 if not up else h - rail
    tas = ""
    for k in range(n + 1):
        x = k * seg
        y = rail if not up else h - rail
        dy = 1 if not up else -1
        tas += (f'<path d="M{x - 9:.0f},{y:.0f} L{x + 9:.0f},{y:.0f} L{x + 14:.0f},{y + dy * 46:.0f} L{x - 14:.0f},{y + dy * 46:.0f} Z" fill="#f2b61e" stroke="{SILK_LO}" stroke-width="2"/>'
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="11" fill="{GOLD_HI}" stroke="{SILK_LO}" stroke-width="2"/>')
    return (f'<svg class="{cls}" width="{W}" height="{h}" viewBox="0 0 {W} {h}" style="position:absolute;left:0;overflow:visible">'
            f'<defs><linearGradient id="vf{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="70" y2="0" spreadMethod="repeat">'
            f'<stop offset="0" stop-color="{SILK_LO}"/><stop offset=".3" stop-color="{SILK}"/><stop offset=".52" stop-color="{SILK_HI}"/>'
            f'<stop offset=".74" stop-color="{SILK}"/><stop offset="1" stop-color="{SILK_LO}"/></linearGradient></defs>'
            + "".join(f'<path d="{p}" fill="url(#vf{uid})" stroke="{SILK_LO}" stroke-width="2"/>' for p in paths)
            + "".join(f'<path d="{p}" fill="none" stroke="#f2b61e" stroke-width="12" stroke-dasharray="2 3"/>'
                      f'<path d="{p}" fill="none" stroke="{GOLD_HI}" stroke-width="3"/>' for p in fr)
            + f'<rect x="0" y="{ry:.0f}" width="{W}" height="{rail:.0f}" fill="url(#vf{uid})"/>'
            + f'<rect x="0" y="{(rail - 6) if not up else (h - rail):.0f}" width="{W}" height="6" fill="#f2b61e"/>'
            + tas + '</svg>')


CSS = r"""
.st-teleshop .scene > .stage { overflow:visible; }
.tsw { position:absolute; inset:0; overflow:hidden; }
.tsf { position:absolute; inset:0; overflow:hidden; background-color:#d9a441; color:#1a0d08; }
.tsf .foil { position:absolute; inset:0; background-size:100% 100%; }
.tsf .lit { position:absolute; inset:0; pointer-events:none;
  background:radial-gradient(ellipse 70% 55% at 22% 18%, rgba(255,244,200,.28), rgba(255,244,200,0) 70%),
             radial-gradient(ellipse 80% 60% at 85% 95%, rgba(70,30,0,.28), rgba(70,30,0,0) 70%); }
.tsf svg { display:block; overflow:visible; }
.tsf .bn { position:absolute; }
.tsf .bn > svg { position:absolute; left:0; top:0; }
.tsf .bt { position:absolute; left:0; right:0; top:0; bottom:0; display:flex; align-items:center; justify-content:center; padding-bottom:6px; }
.tsf .stg { position:absolute; width:960px; height:880px; transform-origin:0 0; }
.tsf .zm { position:absolute; inset:0; transform-origin:50% 50%; }
.tsf .stg .a { position:absolute; }
.tsf .stg svg.a { overflow:visible; }
.tsf .op { position:absolute; background:#fff3cf; color:#6f0a10; border:4px solid #6f0a10; box-shadow:inset 0 0 0 4px #fff3cf, inset 0 0 0 6px #d9a441, 8px 8px 0 rgba(111,10,16,.85);
  font-family:var(--f-body); font-weight:900; font-size:34px; line-height:1.2; display:flex; align-items:center; justify-content:center; white-space:nowrap; letter-spacing:.02em; }
.tsf .op .n { font-family:var(--f-num); font-weight:400; color:#c8141c; letter-spacing:0; }
.tsf .srcs { position:absolute; background:rgba(26,13,8,.7); color:#fff3cf; font-family:var(--f-body); font-weight:700; font-size:24px; line-height:38px;
  padding:0 16px; white-space:nowrap; overflow:hidden; }
.tsf .flash { position:absolute; inset:0; background:#fffbe8; opacity:0; pointer-events:none; }
.tsf .spk { position:absolute; transform:scale(0); filter:drop-shadow(0 0 10px rgba(255,236,150,.95)) drop-shadow(0 0 3px #fff); }
.fr3 { filter:drop-shadow(1.5px 0 0 rgba(255,30,40,.45)) drop-shadow(-1.5px 0 0 rgba(0,225,255,.4)); }
/* 3D lettering */
.g3 { position:relative; display:inline-block; white-space:nowrap; line-height:1.15; font-weight:400; }
.g3 > span { display:block; }
.g3 .x { color:#6f0a10; }
.g3 .o, .g3 .h, .g3 .f { position:absolute; left:0; top:0; }
.g3 .h { color:#ffffff; transform:translate(-2px,-2px); }
.g3 .f { background:linear-gradient(180deg, #fff0a8 18%, #f2b61e 55%, #b86a00 88%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.g3.red .f { background:linear-gradient(180deg, #ff5a3c 20%, #c8141c 85%); -webkit-background-clip:text; background-clip:text; }
.g3.red .h { color:#ffe6d0; }
.g3.title .f { background:linear-gradient(180deg, #fff6c8 18%, #ffd24a 86%); -webkit-background-clip:text; background-clip:text; }
.g3.title .h { color:#ffffff; transform:translate(-2px,-2px); }
.tsf .bl { position:absolute; left:0; top:0; color:#fffdf2; opacity:0; text-shadow:0 0 18px #fff6c8; }
/* silk curtain (the beat-to-beat wipe) */
.tsc { position:absolute; left:0; top:0; height:100%; pointer-events:none; box-shadow:26px 0 40px rgba(40,4,0,.55), -18px 0 30px rgba(40,4,0,.4); }
.tsc .cf { position:absolute; inset:0; background:__FOLDS__; }
.tsc .cs { position:absolute; inset:0; background:linear-gradient(180deg, rgba(255,255,255,.16), rgba(255,255,255,0) 40%, rgba(30,0,4,.35)); }
.tsc .fringe { position:absolute; top:0; right:-30px; width:34px; height:100%;
  background:repeating-linear-gradient(180deg, #fff0a8 0 4px, #f2b61e 4px 9px, #a8741f 9px 12px);
  clip-path:polygon(0 0, 60% 0, 100% 1%, 60% 2%, 100% 3%, 60% 4%, 100% 5%, 60% 6%, 100% 7%, 60% 8%, 100% 9%, 60% 10%, 60% 100%, 0 100%); }
.tsc .cord { position:absolute; top:0; right:-6px; width:9px; height:100%; background:linear-gradient(90deg, #a8741f, #fff0a8 45%, #b86a00); }
/* furniture: valance, ticker, bottom swag */
.tsv, .tsb { position:absolute; left:0; }
.tsk { position:absolute; left:0; overflow:hidden; background:linear-gradient(180deg, #d31a24, #b3121b 45%, #7e0b12); border-top:3px solid #f2b61e; border-bottom:3px solid #f2b61e; }
.tsk .tx { position:absolute; left:0; top:0; height:100%; display:flex; align-items:center; white-space:nowrap; color:#fff3cf;
  font-family:var(--f-body); font-weight:900; font-size:30px; letter-spacing:.06em; }
.tsk .tx b { color:#f6dc8a; font-weight:900; margin:0 22px; }
/* the CRT glass */
.crt { pointer-events:none; }
.crt > i { position:absolute; display:block; }
.crt .scan { inset:0; background:repeating-linear-gradient(180deg, rgba(0,0,0,.10) 0px, rgba(0,0,0,.10) 1px, rgba(0,0,0,0) 1px, rgba(0,0,0,0) 2px); }
.crt .vig { inset:0; background:radial-gradient(ellipse 78% 72% at 50% 50%, rgba(15,6,0,0) 60%, rgba(15,6,0,.34) 100%); }
.crt .sync { left:0; right:0; top:0; height:170px; background:linear-gradient(180deg, rgba(255,250,230,0), rgba(255,250,230,.07) 45%, rgba(0,0,0,.06) 70%, rgba(0,0,0,0)); }
.crt .noi { inset:-300px; background-image:__NOISE__; background-size:300px; opacity:.07; mix-blend-mode:overlay; }
.crt .tube { inset:0; border-radius:46px; box-shadow:0 0 0 120px #0d0705, inset 0 0 90px rgba(20,8,0,.5), inset 0 0 14px rgba(0,0,0,.55); }
.crt .on-k { inset:0; background:#050302; }
.crt .on-l { left:0; right:0; top:50%; height:6px; margin-top:-3px; background:#fffef6; box-shadow:0 0 22px 6px rgba(255,255,240,.8); }
.crt .on-s { inset:0; background-image:__STATIC__; background-size:240px; opacity:0; }
.crt .off-t, .crt .off-b { left:0; right:0; height:50%; background:#050302; }
.crt .off-t { top:0; transform-origin:50% 0%; } .crt .off-b { bottom:0; transform-origin:50% 100%; }
.crt .off-l { left:0; right:0; top:50%; height:6px; margin-top:-3px; background:#fffef6; box-shadow:0 0 26px 8px rgba(255,255,240,.85); opacity:0; }
"""

CAP_CSS = """
#root.st-teleshop .clip.cap { text-align:left; padding-left:90px; padding-right:120px; }
#root.st-teleshop .clip.cap .cp { display:block; box-sizing:border-box; height:80px; line-height:76px; padding:0 66px; text-align:center;
  font-family:var(--f-cap); font-size:44px; font-weight:900; color:#fff3cf; letter-spacing:.04em; white-space:nowrap;
  background:__CAP__; border-top:2px solid #f2b61e; border-bottom:2px solid #f2b61e; border-radius:0;
  clip-path:polygon(0 0, 100% 0, calc(100% - 30px) 50%, 100% 100%, 0 100%, 30px 50%);
  text-shadow:0 3px 0 #5a070c, 1.5px 0 0 rgba(255,30,40,.35), -1.5px 0 0 rgba(0,225,255,.3); }
#root.st-teleshop .clip.cap .cp .em .emt { color:#f6dc8a; } #root.st-teleshop .clip.cap .cp .em .emb { display:none; }
#root.v.st-teleshop { --cap-bottom:464px; }
#root.h.st-teleshop { --cap-bottom:400px; }
#root.h.st-teleshop .clip.cap { padding-left:1080px; padding-right:80px; }
"""


# ---------------------------------------------------------------- layout
def L(X):
    """the fixed architecture per aspect (page px): banner, stage (x, y, scale), offer plate, source strip, ticker, valance, swag."""
    if X.portrait:
        return {"bn": (60, 210, 960, 120), "stg": (60, 360, 1.0), "op": (90, 1270, 870, 80), "src": (90, 1470, 870, 38),
                "tk": (1560, 60), "val": (170, 3), "swag": (1652, 268, 3), "title": 128}
    return {"bn": (1060, 150, 800, 140), "stg": (40, 104, 1.0), "op": (1080, 400, 760, 90), "src": (1080, 790, 760, 38),
            "tk": (1000, 50), "val": (88, 5), "swag": None, "title": 108}


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def captions_text(X):
    """the film's own caption sentences (for the ticker)."""
    s = getattr(X, "text", "") or ""
    out, cur = [], ""
    for c in s:
        if c in "。？！":
            if cur.strip(): out.append(cur.strip("，、 "))
            cur = ""
        else:
            cur += c
    if cur.strip(): out.append(cur.strip())
    return out or [str(X.v.get("meta", {}).get("title", ""))]


# ---------------------------------------------------------------- the set (built once per film)
def world(X):
    """persistent furniture (valance, ticker, bottom swag) and the CRT glass over everything, with switch-on and switch-off."""
    if getattr(X, "_ts_world", False): return
    X._ts_world = True
    X.css("teleshop", CSS.replace("__FOLDS__", FOLDS).replace("__NOISE__", NOISE).replace("__STATIC__", STATIC))
    W, H, D = X.W, X.H, X.duration or 30.0
    l = L(X)
    # furniture
    vh, vn = l["val"]
    ty, th = l["tk"]
    sents = captions_text(X)
    X.used_text.update("".join(sents) + "★")
    unit = "".join(f'<span>{X.rich(s)}</span><b>★</b>' for s in sents)
    per = sum(len(s) for s in sents) * 32 + len(sents) * 80
    reps = max(2, int((W + 140 * D) / max(per, 200)) + 2)
    ticker = (f'<div class="tsk" data-safe="ignore" style="top:{ty}px;width:{W}px;height:{th}px">'
              f'<div class="tx" data-safe="ignore">{unit * reps}</div></div>')
    sw = ""
    if l["swag"]:
        sy, sh, sn = l["swag"]
        sw = f'<div class="tsb" style="top:{sy}px;width:{W}px;height:{sh}px">{swags(W, sh, "b", sn, up=True)}</div>'
    val = f'<div class="tsv" style="top:0;width:{W}px;height:{vh}px">{swags(W, vh, "v", vn)}</div>'
    X.clip("ts-set", 0, D, val + ticker + sw, "ts-set", 44, track=24, attrs="data-layout-allow-overflow")
    X.tw(f'tl.fromTo("#ts-set .tsk .tx", {{x:0}}, {{x:{-140 * D:.0f}, duration:{D:.3f}, ease:"none"}}, 0);')
    # CRT glass
    glass = ('<i class="scan"></i><i class="sync"></i><i class="noi"></i><i class="vig"></i><i class="tube"></i>'
             '<i class="on-k"></i><i class="on-s"></i><i class="on-l"></i><i class="off-t"></i><i class="off-b"></i><i class="off-l"></i>')
    X.clip("ts-crt", 0, D, glass, "crt", 60, track=25, attrs="data-layout-allow-overflow")
    c = "#ts-crt"
    # noise re-seeded every frame (deterministic)
    k = int(D * FPS)
    for i in range(k):
        X.tw(f'tl.set("{c} .noi", {{x:{X.rand.randint(-150, 150)}, y:{X.rand.randint(-150, 150)}}}, {i * F:.3f});')
    # the sync bar drifts down once every 5 s
    p = 0.0
    while p < D:
        X.tw(f'tl.fromTo("{c} .sync", {{y:-170}}, {{y:{H + 10}, duration:{min(5.0, D - p):.3f}, ease:"none"}}, {p:.3f});')
        p += 5.0
    # switch-on: a white line opens to full frame in 7 frames, 3 frames of static, then picture
    X.tw(f'tl.set("{c} .on-l", {{scaleY:1}}, 0);')
    X.tw(f'tl.set("{c} .off-t, {c} .off-b", {{scaleY:0}}, 0);')
    X.tw(f'tl.to("{c} .on-l", {{scaleY:{H / 6:.1f}, duration:{7 * F:.3f}, ease:"power2.in"}}, {F:.3f});')
    X.tw(f'tl.set("{c} .on-k", {{opacity:0}}, {8 * F:.3f});')
    X.tw(f'tl.set("{c} .on-l", {{opacity:0}}, {8 * F:.3f});')
    for j in range(3):
        X.tw(f'tl.set("{c} .on-s", {{opacity:{.92 - .2 * j:.2f}, backgroundPosition:"{X.rand.randint(0, 240)}px {X.rand.randint(0, 240)}px"}}, {(8 + j) * F:.3f});')
    X.tw(f'tl.set("{c} .on-s", {{opacity:0}}, {11 * F:.3f});')
    X.sfx(0.02, "on")
    # switch-off: the picture collapses to a line (5 frames), the line to a dot (4 frames)
    t0 = D - 10 * F
    X.tw(f'tl.to("{c} .off-t, {c} .off-b", {{scaleY:1, duration:{5 * F:.3f}, ease:"power3.in"}}, {t0:.3f});')
    X.tw(f'tl.set("{c} .off-l", {{opacity:1}}, {t0 + 4 * F:.3f});')
    X.tw(f'tl.to("{c} .off-l", {{scaleX:0.006, duration:{4 * F:.3f}, ease:"power3.in"}}, {t0 + 5 * F:.3f});')
    X.tw(f'tl.to("{c} .off-l", {{opacity:0.35, duration:{F:.3f}, ease:"none"}}, {t0 + 9 * F:.3f});')


# ---------------------------------------------------------------- motion verbs
def slam(X, sel, t, frm=2.2, dip=0.94, flash=None, shake=None, snd="slam"):
    """scale frm -> dip -> 1.0 in 9 frames (6 in, 3 settle); optional 1-frame white flash and 6 px shake on impact.
    The element is hidden from the start of the beat until it lands."""
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {X.beat["t"]:.3f});')
    X.tw(f'tl.set("{sel}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel}", {{scale:{frm}, opacity:0}}, {{scale:{dip}, opacity:1, duration:{6 * F:.3f}, ease:"power2.in", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.to("{sel}", {{scale:1, duration:{3 * F:.3f}, ease:"power1.out"}}, {t + 6 * F:.3f});')
    hit = t + 6 * F
    if flash:
        X.tw(f'tl.set("{flash}", {{opacity:.72}}, {hit:.3f});')
        X.tw(f'tl.set("{flash}", {{opacity:0}}, {hit + F:.3f});')
    if shake:
        for j, dx in enumerate((6, -6, 4, -3, 2, 0)):
            X.tw(f'tl.set("{shake}", {{x:{dx}, y:{-dx // 2}}}, {hit + j * F:.3f});')
    X.sfx(hit - 0.02, snd)
    return hit


def blink(X, sel, t):
    """flashing price: a white copy over the number on for 2 frames, off for 2, twice."""
    for j in range(2):
        X.tw(f'tl.set("{sel}", {{opacity:1}}, {t + 4 * j * F:.3f});')
        X.tw(f'tl.set("{sel}", {{opacity:0}}, {t + (4 * j + 2) * F:.3f});')


def glint(X, sel, t):
    X.tw(f'tl.fromTo("{sel}", {{scale:0, rotation:-30}}, {{scale:1.15, rotation:15, duration:0.2, ease:"power2.out", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.to("{sel}", {{scale:0, rotation:60, duration:0.25, ease:"power2.in"}}, {t + 0.2:.3f});')


def thud_drop(X, sel, t, dy=120):
    """drop 120 px, land with a 6% squash, settle: 7 frames."""
    X.tw(f'tl.set("{sel}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel}", {{y:{-dy}, opacity:0}}, {{y:0, opacity:1, duration:{4 * F:.3f}, ease:"power2.in", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.to("{sel}", {{scaleY:0.94, scaleX:1.03, transformOrigin:"50% 100%", duration:{F:.3f}, ease:"none"}}, {t + 4 * F:.3f});')
    X.tw(f'tl.to("{sel}", {{scaleY:1, scaleX:1, duration:{2 * F:.3f}, ease:"power1.out"}}, {t + 5 * F:.3f});')
    X.sfx(t + 4 * F - 0.02, "thud")


def wipe_in(X, sel, t, dur=6 * F):
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{dur:.3f}, ease:"none"}}, {t:.3f});')


def hidden(X, sel, t):
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {t:.3f});')


# ---------------------------------------------------------------- the page
def page(X, b, cid, t, d, stage, under="", over=""):
    """one commercial shot: foil ground, silk title band, the product shot (stage box), offer plate, source strip;
    the next shot arrives under a red silk curtain that sweeps across this one."""
    world(X)
    W, H, P = X.W, X.H, X.portrait
    i, n = X.beat["i"], len(X.v.get("beats", []))
    l = L(X)
    seed = SEEDS[i % len(SEEDS)]
    head, claim, src = b.get("head", ""), b.get("claim", ""), b.get("src", "")
    X.used_text.update(head + claim + src)
    bx, by, bw, bh = l["bn"]
    sx, sy, ss = l["stg"]
    ox, oy, ow, oh = l["op"]
    rx, ry, rw, rh = l["src"]
    from h9 import fit
    tp = l["title"]
    while fit.width(head) * tp > bw - 150 and tp > 60: tp -= 2
    banner = (f'<div class="bn shk" style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px">{silk_svg(bw, bh, cid, ph=i * 1.3)}'
              f'<div class="bt"><span class="fr3">{g3(X, head, tp, "title", "ht")}</span></div></div>')
    op = (f'<div class="op shk" style="left:{ox}px;top:{oy}px;width:{ow}px;height:{oh}px">{rich_claim(X, claim)}</div>' if claim else "")
    wrap = "" if P else "white-space:normal;line-height:32px;padding:3px 16px;"
    srcs = f'<div class="srcs" style="left:{rx}px;top:{ry}px;max-width:{rw}px;{"height:%dpx;" % rh if P else ""}{wrap}">{X.rich(src)}</div>' if src else ""
    stg = (f'<div class="stg shk" data-layout-allow-overlap style="left:{sx}px;top:{sy}px;transform:scale({ss})"><div class="zm">{stage}</div></div>')
    hx, hy = sx + BW / 2 * ss, sy + BH / 2 * ss          # the hero's centre: the stage's centre
    # inside the stage the foil relief is calmed ~40 % (flat gold over it, soft-edged) and the hero sits in a pool of light
    calm = (f'<div class="calm" style="position:absolute;inset:0;background:{GOLD};opacity:.42;'
            f'-webkit-mask-image:radial-gradient(ellipse {BW * ss * 0.62:.0f}px {BH * ss * 0.6:.0f}px at {hx:.0f}px {hy:.0f}px, #000 62%, transparent 100%);'
            f'mask-image:radial-gradient(ellipse {BW * ss * 0.62:.0f}px {BH * ss * 0.6:.0f}px at {hx:.0f}px {hy:.0f}px, #000 62%, transparent 100%)"></div>')
    spot = (f'<div class="spot" style="position:absolute;inset:0;pointer-events:none;'
            f'background:radial-gradient(circle 450px at {hx:.0f}px {hy:.0f}px, rgba(255,250,228,.26) 0%, rgba(255,250,228,.12) 55%, rgba(255,250,228,0) 100%),'
            f'radial-gradient(ellipse 75% 70% at {hx:.0f}px {hy:.0f}px, rgba(35,14,0,0) 48%, rgba(35,14,0,.3) 100%)"></div>')
    face = (f'<div class="tsf"><div class="foil" style="background-image:{foil_uri(W, H, seed)}"></div><div class="lit"></div>{calm}{spot}'
            f'{under}{banner}{stg}{op}{srcs}{over}<div class="flash"></div></div>')
    last = i + 1 >= n
    curtain = ("" if last else
               f'<div class="tsc" style="width:{CURT_W}px;transform:translateX({-CURT_W - 40}px)"><i class="cf"></i><i class="cs"></i><i class="cord"></i><i class="fringe"></i></div>')
    html = f'<div class="tsw">{face}</div>{curtain}'
    D = X.duration or (t + d)
    ext = d if last else min(d + WIPE + F, max(d, D - t))
    X.clip(cid, t, ext, html, "scene", 40 - i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    t0 = t + (12 * F if i == 0 else 0.0)            # the first shot appears after the switch-on
    # the silk band waves: its folds slide slowly the whole shot
    X.tw(f'tl.fromTo("{s} .bn .fold", {{x:0}}, {{x:{110 * max(1, round(ext / 2.2))}, duration:{ext:.3f}, ease:"none"}}, {t:.3f});')
    # the title slams onto the band
    slam(X, f"{s} .bn .ht", t0 + 0.12, frm=1.7, dip=0.96, snd="hit")
    if op:
        hidden(X, f"{s} .op", t)
    if srcs:      # the source strip is up from the start of the shot, under the title
        hidden(X, f"{s} .srcs", t)
        X.tw(f'tl.set("{s} .srcs", {{visibility:"visible"}}, {t0 + 0.3:.3f});')
        wipe_in(X, f"{s} .srcs", t0 + 0.3, 6 * F)
    if not last:       # the silk curtain sweeps across in 10 frames; the next shot is already under it
        te = t + d
        X.tw(f'tl.fromTo("{s} .tsc", {{x:{-CURT_W - 40}}}, {{x:{W}, duration:{WIPE:.3f}, ease:"none"}}, {te:.3f});')
        X.tw(f'tl.fromTo("{s} > .stage > .tsw", {{clipPath:"inset(0px 0px 0px 0px)"}}, {{clipPath:"inset(0px 0px 0px {W}px)", '
             f'duration:{WIPE * W / (W + CURT_W + 40):.3f}, ease:"none"}}, {te + WIPE * 40 / (W + CURT_W + 40):.3f});')
        X.sfx(te - 0.03, "transition")
    return s, t0


def claim_in(X, s, t, d):
    """the offer plate (plate and text together) slams on, never later than 1.4 s into the shot, and stays."""
    b0 = X.beat["t"] + (12 * F if X.beat["i"] == 0 else 0.0)
    t = min(t, b0 + 1.4 - 6 * F)
    slam(X, f"{s} .op", t, frm=1.25, dip=0.98, snd="click")


def hold_zoom(X, s, t, t_end):
    if t_end - t > 0.3:
        X.tw(f'tl.fromTo("{s} .zm", {{scale:1}}, {{scale:1.05, duration:{t_end - t:.3f}, ease:"none"}}, {t:.3f});')


def rich_claim(X, claim):
    """the claim with numerals set in red Anton."""
    import re
    out = []
    for part in re.split(r"([+\-−]?[\d][\d,.]*%?)", str(claim)):
        if not part: continue
        if re.fullmatch(r"[+\-−]?[\d][\d,.]*%?", part):
            out.append(f'<span class="n" style="font-size:42px;margin:0 .12em">{X.rich(part)}</span>')
        else:
            out.append(X.rich(part))
    return "".join(out)


def num_block(X, big, unit, px, kind="gold", cls="hn", upx=None, ucol=CREAM, gap=12, blinkable=True):
    """a 3D numeral with its unit at the shoulder; a hidden white copy for the price blink."""
    upx = upx or max(34, round(px * 0.26))
    # the price blink: white over gold numerals; on red numerals (cream plates) a gold copy with the deep outline, so it stays legible
    blc = f"color:#ffd24a;-webkit-text-stroke:4px {DEEP};text-shadow:none;" if kind == "red" else ""
    bl = f'<span class="bl" aria-hidden="true" style="font-size:{px:.0f}px;font-family:var(--f-num);line-height:1.15;{blc}">{X.rich(big)}</span>' if blinkable else ""
    u = (f'<span class="u" style="display:inline-block;vertical-align:top;margin-left:{gap}px;margin-top:{px * 0.22:.0f}px;font-family:var(--f-display);'
         f'font-size:{upx}px;color:{ucol};line-height:1.1">{X.rich(unit)}</span>') if unit else ""
    X.used_text.update(big + unit)
    return (f'<span class="{cls} fr3" style="display:inline-block;position:relative;white-space:nowrap">'
            f'<span style="position:relative;display:inline-block">{g3(X, big, px, kind, num=True)}{bl}</span>{u}</span>')


# ---------------------------------------------------------------- scenes (box coordinates, 960 × 880)
def burst(b, X, t, d, cid):
    """爆炸价签大数字：「原价」奶油价签先出、停留半秒后被一道红杠划掉（数字仍可读），820 px 的红色 24 角爆炸签带着今年的数砸下来
    （白闪 + 震屏），价格金白闪两下。参数：big、unit、tag（签上小字）、old {label, value, unit}、at_slam。"""
    big, unit = str(b.get("big", "")), b.get("unit", "")
    o = b.get("old", {})
    cx, cy, R, r = 500, 478, 410, 352
    px = min(262, 620 / max(0.5, anton_w(big)))
    tag = b.get("tag", "")
    X.used_text.update(tag)
    # the old price tag (cream, tilted) in front of the burst's corner; one strike bar at 30 % of the digit height
    ov, ou, ol = str(o.get("value", "")), o.get("unit", ""), o.get("label", "")
    X.used_text.update(ov + ou + ol)
    opx = min(84, 280 / max(0.5, anton_w(ov)))      # flat old price: glyph >= 64 px
    ntop = 66
    dtop = ntop + 0.1315 * opx               # Anton digit top inside a 1.15 line box
    bar_y = dtop + 0.5 * 0.875 * opx - 4     # the strike bar crosses at mid-height
    old = (f'<div class="a oldt" style="left:-30px;top:2px;width:420px;height:200px;transform:rotate(-7deg);transform-origin:50% 50%">'
           f'<div style="position:absolute;inset:0;background:{CREAM};border:5px solid {SILK_LO};box-shadow:inset 0 0 0 5px {CREAM}, inset 0 0 0 8px {GOLD}, 10px 12px 0 {SILK_LO}"></div>'
           f'<div style="position:absolute;left:0;right:0;top:16px;text-align:center;font-family:var(--f-body);font-weight:900;font-size:34px;color:{DEEP}">{X.rich(ol)}</div>'
           f'<div class="ov" style="position:absolute;left:0;right:0;top:{ntop}px;text-align:center;white-space:nowrap;color:{DEEP};opacity:.7;line-height:1.15">'
           f'<span style="font-family:var(--f-num);font-size:{opx:.0f}px">{X.rich(ov)}</span>'
           f'<span style="font-family:var(--f-display);font-size:36px;margin-left:10px">{X.rich(ou)}</span></div>'
           f'<i class="sb sb1" style="position:absolute;left:44px;right:44px;top:{bar_y:.0f}px;height:8px;background:{NUM_LO};transform:rotate(-3deg);transform-origin:0 50%;'
           f'box-shadow:0 0 0 2px {CREAM}"></i></div>')
    # the starburst
    pts = starburst(24, R, r, cx, cy)
    pts2 = starburst(24, R - 28, r - 24, cx, cy)
    bs = (f'<svg class="a bsv" viewBox="0 0 {BW} {BH}" style="left:0;top:0;width:{BW}px;height:{BH}px">'
          f'<defs><radialGradient id="bg{cid}" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="{SILK_HI}"/><stop offset=".55" stop-color="{SILK}"/>'
          f'<stop offset="1" stop-color="#7d0b12"/></radialGradient></defs>'
          f'<polygon points="{pts}" transform="translate(16 18)" fill="{SILK_LO}"/>'
          f'<polygon points="{pts}" fill="url(#bg{cid})" stroke="{CREAM}" stroke-width="8" stroke-linejoin="round"/>'
          f'<polygon points="{pts2}" fill="none" stroke="#f2b61e" stroke-width="3" stroke-linejoin="round" opacity=".9"/>'
          f'<circle cx="{cx}" cy="{cy}" r="{r - 40}" fill="none" stroke="{CREAM}" stroke-width="2.5" stroke-dasharray="3 9" opacity=".7"/></svg>')
    gc = cy - 18                                # glyph centre
    g_top = gc - 0.4375 * px
    inner = (f'<div class="a" style="left:{cx - 320}px;top:{g_top - 60:.0f}px;width:640px;text-align:center;font-family:var(--f-body);font-weight:900;font-size:38px;'
             f'color:{CREAM};letter-spacing:.06em;line-height:1.2;text-shadow:3px 3px 0 {SILK_LO}">{X.rich(tag)}</div>'
             f'<div class="a" style="left:{cx - 340}px;top:{gc - 0.569 * px:.0f}px;width:680px;text-align:center">{num_block(X, big, "", px, "gold", "hn")}</div>'
             f'<div class="a" style="left:{cx - 200}px;top:{gc + 0.4375 * px + 10:.0f}px;width:400px;text-align:center;font-family:var(--f-display);font-size:62px;'
             f'line-height:1.1;color:{CREAM};text-shadow:4px 4px 0 {SILK_LO}">{X.rich(unit)}</div>')
    burstw = (f'<div class="a bw" style="left:0;top:0;width:{BW}px;height:{BH}px;transform-origin:{cx}px {cy}px;visibility:hidden">{bs}{inner}</div>')
    stage = burstw + old + sparkle("k1", cx + 310, cy - 290, 1.3) + sparkle("k2", cx - 330, cy + 230, 0.9)
    s, t0 = page(X, b, cid, t, d, stage)
    # old tag slams on and is readable for 0.5 s; then one strike bar swipes through the top of its digits
    slam(X, f"{s} .oldt", t0 + 0.15, frm=1.5, dip=0.97, snd="hit")
    X.tw(f'tl.fromTo("{s} .sb1", {{scaleX:0}}, {{scaleX:1, duration:{5 * F:.3f}, ease:"none"}}, {t0 + 0.88:.3f});')
    X.sfx(t0 + 0.88, "click")
    ts = max(t0 + 1.05, T(X, b, "at_slam", t, t0 + 1.08) - 6 * F)
    hit = slam(X, f"{s} .bw", ts, flash=f"{s} .flash", shake=f"{s} .shk")
    blink(X, f"{s} .hn .bl", hit + 0.2)
    glint(X, f"{s} .k1", hit + 0.55)
    glint(X, f"{s} .k2", hit + 1.6)
    claim_in(X, s, hit + 0.3, d)
    hold_zoom(X, s, hit + 0.4, t + d + WIPE)


def versus(b, X, t, d, cid):
    """去年 vs 今年：闪电金分割线劈开画面；左边褪色发冷，右边打亮；两座台子的高度按真实比例，数写在奶油色牌子上。
    参数：left / right {name, value, unit, at}。"""
    Lf, Rt = b.get("left", {}), b.get("right", {})
    lv, rv = float(Lf.get("value", 1)), float(Rt.get("value", 1))
    vmax = max(lv, rv) or 1
    hmax, base = 470, 830
    xs = [245, 720]
    pw = 300
    X.used_text.update("".join(str(v.get(k, "")) for v in (Lf, Rt) for k in ("name", "value", "unit")))
    # lightning divider (box coords)
    zz = [(486, -10), (448, 120), (512, 210), (456, 330), (522, 450), (462, 560), (526, 670), (470, 780), (500, 900)]
    left_e = " ".join(f"{x - 16},{y}" for x, y in zz)
    right_e = " ".join(f"{x + 16},{y}" for x, y in reversed(zz))
    bolt = (f'<svg class="a bolt" viewBox="0 0 {BW} {BH}" style="left:0;top:0;width:{BW}px;height:{BH}px">'
            f'<polygon points="{left_e} {right_e}" transform="translate(8 8)" fill="{SILK_LO}" opacity=".7"/>'
            f'<polygon points="{left_e} {right_e}" fill="#f2b61e" stroke="{SILK_LO}" stroke-width="4" stroke-linejoin="miter"/>'
            f'<polyline points="{" ".join(f"{x - 6},{y}" for x, y in zz)}" fill="none" stroke="#fff6c8" stroke-width="4"/></svg>')
    peds = ""
    for k, (it, v) in enumerate(((Lf, lv), (Rt, rv))):
        h = hmax * v / vmax
        x0 = xs[k] - pw / 2
        win = k == 1
        if win:
            body = (f'background:{FOLDS};box-shadow:inset 0 0 0 4px {SILK_LO}, 14px 14px 0 {SILK_LO};')
            trim = f'background:linear-gradient(180deg,#fff0a8,#f2b61e 50%,#b86a00);border:3px solid {SILK_LO};'
            ncol = CREAM
        else:
            body = (f'background:repeating-linear-gradient(90deg,#2c5670 0 26px,{COLD} 26px 58px,#5a87a4 58px 74px,{COLD} 74px 100px);'
                    f'box-shadow:inset 0 0 0 4px #1f3d50, 14px 14px 0 #1f3d50;')
            trim = 'background:linear-gradient(180deg,#c9d8e2,#8fb0c4 50%,#5b7f96);border:3px solid #1f3d50;'
            ncol = "#eef4f8"
        val = str(it.get("value", ""))
        vpx = min(140, (pw - 34) / max(0.5, anton_w(val)))     # glyph >= 110 px for the values in this film
        ph = round(vpx * 1.15 + 48)
        plq_bg = CREAM if win else "#e9eef0"
        plq_bd = SILK_LO if win else "#1f3d50"
        if win:
            num = num_block(X, val, "", vpx, "red", f"pv pv{k}", blinkable=True)
        else:
            num = (f'<span class="pv pv{k}" style="font-family:var(--f-num);font-size:{vpx:.0f}px;line-height:1.15;color:#2f5a75;'
                   f'text-shadow:5px 5px 0 #b9c9d3">{X.rich(val)}</span>')
        peds += (f'<div class="a pd pd{k}" style="left:{x0:.0f}px;top:{base - h:.0f}px;width:{pw}px;height:{h:.0f}px;transform-origin:50% 100%">'
                 f'<div style="position:absolute;inset:0;{body}"></div>'
                 f'<div style="position:absolute;left:-14px;right:-14px;top:-8px;height:34px;{trim}"></div>'
                 f'<div style="position:absolute;left:0;right:0;top:56px;text-align:center;font-family:var(--f-display);font-size:46px;color:{ncol};'
                 f'text-shadow:3px 3px 0 {SILK_LO if win else "#1f3d50"}">{X.rich(it.get("name", ""))}</div></div>'
                 f'<div class="a pq pq{k}" style="left:{x0 - 10:.0f}px;top:{base - h - ph - 22:.0f}px;width:{pw + 20}px;height:{ph}px;transform-origin:50% 100%;display:flex;flex-direction:column;align-items:center;justify-content:center;'
                 f'background:{plq_bg};border:5px solid {plq_bd};box-shadow:inset 0 0 0 4px {plq_bg}, inset 0 0 0 7px {GOLD if win else "#9fb6c4"}, 10px 10px 0 {plq_bd};'
                 f'box-sizing:border-box">{num}'
                 f'<div style="font-family:var(--f-body);font-weight:900;font-size:32px;line-height:1.1;color:{DEEP if win else "#1f3d50"};margin-top:-14px;white-space:nowrap">{X.rich(it.get("unit", ""))}</div></div>')
    # stage-local light: the winner sits in a warm spotlight, the loser in a cold wash (box coords)
    light = (f'<div class="a" style="left:500px;top:-60px;width:470px;height:960px;background:radial-gradient(ellipse 60% 70% at 50% 30%, rgba(255,246,200,.5), rgba(255,246,200,0) 72%)"></div>')
    stage = light + peds + bolt + sparkle("k1", xs[1] + 120, base - hmax - 170, 1.2)
    # the cold side: a desaturated, blue-washed copy of the foil under the left half of the stage (page coords)
    l = L(X)
    sx, sy, ss = l["stg"]
    cw = 486 * ss
    under = (f'<div class="cold" style="position:absolute;left:0;top:0;width:{sx + cw:.0f}px;height:{X.H}px;overflow:hidden;isolation:isolate;'
             f'clip-path:inset({sy - 10:.0f}px 0px {X.H - sy - BH * ss - 10:.0f}px {sx - 30 if X.portrait else 0:.0f}px)">'
             f'<div style="position:absolute;left:0;top:0;width:{X.W}px;height:{X.H}px;background-image:{foil_uri(X.W, X.H, SEEDS[X.beat["i"] % len(SEEDS)])};'
             f'background-size:100% 100%;filter:grayscale(1) brightness(.92) contrast(.85)"></div>'
             f'<div style="position:absolute;inset:0;background:{COLD};mix-blend-mode:color;opacity:.9"></div>'
             f'<div style="position:absolute;inset:0;background:rgba(30,60,80,.18)"></div></div>')
    s, t0 = page(X, b, cid, t, d, stage, under=under)
    # the bolt strikes top to bottom (4 frames), the cold half washes in with it
    X.tw(f'tl.fromTo("{s} .bolt", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{4 * F:.3f}, ease:"none"}}, {t0 + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .cold", {{opacity:0}}, {{opacity:1, duration:{3 * F:.3f}, ease:"none"}}, {t0 + 0.36:.3f});')
    X.sfx(t0 + 0.3, "hit")
    # loser rises (8 frames), its plaque slams; then the winner, higher, with the blink and a glint
    for k in (0, 1):
        tk = t0 + 0.5 if k == 0 else max(t0 + 1.0, T(X, Rt, "at", t, t0 + 1.05) - 8 * F)
        X.tw(f'tl.set("{s} .pd{k}, {s} .pq{k}", {{visibility:"hidden"}}, {t:.3f});')
        X.tw(f'tl.set("{s} .pd{k}", {{visibility:"visible"}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .pd{k}", {{scaleY:0}}, {{scaleY:{1.05 if k else 1.0}, duration:{6 * F:.3f}, ease:"power4.out", immediateRender:false}}, {tk:.3f});')
        if k:
            X.tw(f'tl.to("{s} .pd{k}", {{scaleY:1, duration:{2 * F:.3f}, ease:"none"}}, {tk + 6 * F:.3f});')
        X.sfx(tk, "thud")
        hit = slam(X, f"{s} .pq{k}", tk + 6 * F, frm=1.8, dip=0.95, flash=(f"{s} .flash" if k else None), shake=(f"{s} .shk" if k else None))
        if k:
            blink(X, f"{s} .pv1 .bl", hit + 0.16)
            glint(X, f"{s} .k1", hit + 0.5)
            claim_in(X, s, hit + 0.45, d)
            hold_zoom(X, s, hit + 0.3, t + d + WIPE)


def countdown(b, X, t, d, cid):
    """销量榜：金牌匾从末名一块块翻上来，第一名最后到、带闪光和金边；匾的宽度按真实比例。参数：items [{name, value, label}]、unit。"""
    items = b.get("items", [])[:5]
    n = max(1, len(items))
    vmax = max(float(it.get("value", 0) or 0) for it in items) or 1
    x0, wmax = 128, 790
    rowh = 150 if n >= 5 else min(170, 760 / n)
    top = (BH - n * rowh) / 2 + 12
    bh = 110
    unit = b.get("unit", "")
    rows = ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = max(14.0, wmax * v / vmax)
        y = top + k * rowh + (rowh - bh) / 2
        nm, lv = it.get("name", ""), str(it.get("label", it.get("value", "")))
        X.used_text.update(nm + lv + str(k + 1))
        npx = 34
        chip_w = fit_w(nm) * npx + anton_w(lv) * 54 + 14 + 40
        inside = chip_w + 36 <= w
        win = k == 0
        bd = (f"box-shadow:0 0 0 5px {CREAM}, 0 0 0 9px {SILK_LO}, 12px 12px 0 9px {SILK_LO};" if win else f"box-shadow:inset 0 3px 0 rgba(255,255,255,.7), 9px 9px 0 {SILK_LO};")
        lab_html = (f'<span style="font-family:var(--f-display);font-size:{npx}px;color:{DEEP}">{X.rich(nm)}</span>'
                    f'<span style="font-family:var(--f-num);font-size:54px;color:{NUM_LO};margin-left:14px">{X.rich(lv)}</span>')
        chip = (f'height:84px;padding:0 20px;display:flex;align-items:center;white-space:nowrap;box-sizing:border-box;'
                f'background:{CREAM};border:4px solid {DEEP};box-shadow:6px 6px 0 {DEEP};')
        bar = (f'<div class="a pl pl{k}" style="left:{x0}px;top:{y:.0f}px;width:{w:.0f}px;height:{bh:.0f}px;transform-origin:50% 100%;'
               f'background:linear-gradient(180deg,#fff0a8 0%,#f2b61e 42%,#d18a12 70%,#b86a00 100%);border:3px solid {SILK_LO};{bd}">'
               + (f'<div style="position:absolute;left:18px;top:{(bh - 6 - 84) / 2:.0f}px;{chip}">{lab_html}</div>' if inside else "")
               + '</div>')
        if not inside:
            bar += (f'<div class="a pl pt{k}" style="left:{x0 + w + 26:.0f}px;top:{y + (bh - 84) / 2:.0f}px;{chip}transform-origin:0% 100%">{lab_html}</div>')
        bar += (f'<div class="a rk rk{k}" style="left:14px;top:{y + bh / 2 - 46:.0f}px;width:92px;height:92px;border-radius:50%;background:radial-gradient(circle at 35% 30%, {SILK_HI}, {SILK} 60%, #7d0b12);'
                f'border:4px solid {CREAM};box-shadow:0 0 0 3px {SILK_LO}, 6px 6px 0 3px {SILK_LO};text-align:center;line-height:92px;font-family:var(--f-num);font-size:56px;color:{CREAM}">{k + 1}</div>')
        rows += bar
    X.used_text.update("单位" + unit)
    utag = (f'<div class="a ut" style="right:30px;top:6px;padding:6px 18px;background:{CREAM};border:3px solid {SILK_LO};font-family:var(--f-body);font-weight:900;'
            f'font-size:28px;color:{SILK_LO}">单位：{X.rich(unit)}</div>') if unit else ""
    win_y = top + (rowh - bh) / 2
    stage = rows + utag + sparkle("k1", x0 + wmax * float(items[0].get("value", 0)) / vmax - 30, win_y - 6, 1.2) if items else ""
    s, t0 = page(X, b, cid, t, d, stage)
    # flip in from the bottom rank to the top, 6 frames each, with a thud
    tk = t0 + 0.35
    for k in range(n - 1, -1, -1):
        sel = f"{s} .pl{k}, {s} .pt{k}, {s} .rk{k}"
        X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {t:.3f});')
        X.tw(f'tl.set("{sel}", {{visibility:"visible"}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .pl{k}, {s} .pt{k}", {{rotationX:-95, y:50}}, {{rotationX:0, y:0, duration:{6 * F:.3f}, ease:"power3.in", immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .rk{k}", {{scale:1.8}}, {{scale:1, duration:{5 * F:.3f}, ease:"power2.in", immediateRender:false}}, {tk + 2 * F:.3f});')
        X.sfx(tk + 5 * F, "thud")
        if k == 0:
            hit = tk + 6 * F
            X.tw(f'tl.set("{s} .flash", {{opacity:.6}}, {hit:.3f});')
            X.tw(f'tl.set("{s} .flash", {{opacity:0}}, {hit + F:.3f});')
            for j, dx in enumerate((6, -6, 4, -2, 0)):
                X.tw(f'tl.set("{s} .shk", {{x:{dx}}}, {hit + j * F:.3f});')
            glint(X, f"{s} .k1", hit + 0.35)
            claim_in(X, s, hit + 0.4, d)
            hold_zoom(X, s, hit + 0.3, t + d + WIPE)
        tk += 0.22 if k > 1 else 0.3
    if utag:
        wipe_in(X, f"{s} .ut", t0 + 0.2)


def fit_w(s):
    from h9 import fit
    return fit.width(s)


def bundle(b, X, t, d, cid):
    """买一送三：礼盒的宽度按各部分的真实比例，一个个砸下来摞成一摞（下落 120 px、压扁 6%、7 帧），最后合计价签砸在顶上。
    参数：items [{name, value}]（从下往上）、total {label, value, unit, at}。"""
    items = b.get("items", [])[:5]
    n = max(1, len(items))
    vmax = max(float(it.get("value", 0) or 0) for it in items) or 1
    cx, wmax, bh, base = 290, 640, 104, 846
    boxes = ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = max(16.0, wmax * v / vmax)
        y = base - (k + 1) * bh
        x = cx - w / 2
        nm = it.get("name", "")
        X.used_text.update(nm + str(it.get("value", "")))
        rib = min(26, max(6, w * 0.08))
        lid = (f'<div style="position:absolute;left:-7px;right:-7px;top:0;height:26px;background:linear-gradient(180deg,#d3242c,{SILK} 60%,#7d0b12);'
               f'border:3px solid {SILK_LO};box-sizing:border-box"></div>')
        bow = ""
        if k == n - 1:
            bow = (f'<svg style="position:absolute;left:{w / 2 - 60:.0f}px;top:-56px;width:120px;height:62px;overflow:visible" viewBox="0 0 120 62">'
                   f'<path d="M60,54 C30,10 4,18 8,40 C12,58 40,58 60,54 Z" fill="#f2b61e" stroke="{SILK_LO}" stroke-width="3"/>'
                   f'<path d="M60,54 C90,10 116,18 112,40 C108,58 80,58 60,54 Z" fill="#f2b61e" stroke="{SILK_LO}" stroke-width="3"/>'
                   f'<circle cx="60" cy="52" r="10" fill="{GOLD_HI}" stroke="{SILK_LO}" stroke-width="3"/></svg>')
        boxes += (f'<div class="a gb gb{k}" style="left:{x:.0f}px;top:{y}px;width:{w:.0f}px;height:{bh - 4}px;transform-origin:50% 100%">'
                  f'<div style="position:absolute;inset:0;background:linear-gradient(90deg,#8c0d15,{SILK} 30%,#cf2a2f 52%,{SILK} 75%,#8c0d15);'
                  f'border:3px solid {SILK_LO};box-shadow:10px 10px 0 rgba(111,10,16,.8);box-sizing:border-box"></div>'
                  f'<div style="position:absolute;left:{w / 2 - rib / 2:.0f}px;width:{rib:.0f}px;top:0;bottom:0;background:linear-gradient(90deg,#b86a00,#fff0a8 50%,#b86a00)"></div>'
                  f'<div style="position:absolute;left:0;right:0;top:{bh / 2 - 9:.0f}px;height:18px;background:linear-gradient(180deg,#b86a00,#fff0a8 50%,#b86a00)"></div>'
                  f'{lid}{bow}</div>'
                  f'<div class="a gl gl{k}" style="left:{max(cx + wmax / 2, x + w) + 26:.0f}px;top:{y + 10}px;height:{bh - 24}px;padding:0 16px;display:flex;align-items:center;gap:12px;white-space:nowrap;'
                  f'background:{CREAM};border:4px solid {SILK_LO};box-shadow:6px 6px 0 {SILK_LO};transform-origin:0 50%">'
                  f'<span style="font-family:var(--f-body);font-weight:900;font-size:28px;color:{SILK_LO}">{X.rich(nm)}</span>'
                  f'<span style="font-family:var(--f-num);font-size:46px;color:{NUM_LO}">{X.rich(str(it.get("value", "")))}</span></div>')
    tot = b.get("total", {})
    tl_, tv, tu = tot.get("label", ""), str(tot.get("value", "")), tot.get("unit", "")
    X.used_text.update(tl_ + tv + tu)
    ty = base - n * bh - 70 - 250
    tpx = min(185, (660 - 150 - 46 * len(tl_) - 56 * len(tu)) / max(0.5, anton_w(tv)))
    total = (f'<div class="a tt" style="left:{cx - 320}px;top:{max(10, ty):.0f}px;width:660px;height:250px;transform-origin:50% 100%;visibility:hidden">'
             f'<svg viewBox="0 0 660 250" style="position:absolute;inset:0;width:660px;height:250px;overflow:visible">'
             f'<path d="M40,10 H620 L650,125 L620,240 H40 L10,125 Z" transform="translate(12 12)" fill="{SILK_LO}"/>'
             f'<path d="M40,10 H620 L650,125 L620,240 H40 L10,125 Z" fill="{CREAM}" stroke="{SILK_LO}" stroke-width="6"/>'
             f'<path d="M50,24 H610 L634,125 L610,226 H50 L26,125 Z" fill="none" stroke="{GOLD}" stroke-width="3"/>'
             f'<circle cx="62" cy="125" r="13" fill="{SILK_LO}"/></svg>'
             f'<div style="position:absolute;left:84px;top:0;bottom:0;display:flex;align-items:center;font-family:var(--f-display);font-size:46px;color:{SILK_LO}">{X.rich(tl_)}</div>'
             f'<div style="position:absolute;left:{104 + 46 * len(tl_)}px;top:{125 - tpx * 0.64:.0f}px;white-space:nowrap">{num_block(X, tv, tu, tpx, "red", "hn", upx=52, ucol=SILK_LO)}</div></div>')
    stage = boxes + total + sparkle("k1", cx + 250, max(10, ty) + 30, 1.2)
    s, t0 = page(X, b, cid, t, d, stage)
    tk = t0 + 0.35
    for k in range(n):
        X.tw(f'tl.set("{s} .gb{k}, {s} .gl{k}", {{visibility:"hidden"}}, {t:.3f});')
        thud_drop(X, f"{s} .gb{k}", tk)
        X.tw(f'tl.set("{s} .gl{k}", {{visibility:"visible"}}, {tk + 4 * F:.3f});')
        wipe_in(X, f"{s} .gl{k}", tk + 4 * F, 5 * F)
        tk += 0.26
    tt = max(tk + 0.1, T(X, tot, "at", t, tk + 0.2) - 6 * F)
    hit = slam(X, f"{s} .tt", tt, flash=f"{s} .flash", shake=f"{s} .shk")
    blink(X, f"{s} .tt .bl", hit + 0.18)
    glint(X, f"{s} .k1", hit + 0.5)
    claim_in(X, s, hit + 0.6, d)
    hold_zoom(X, s, hit + 0.3, t + d + WIPE)


def seal(b, X, t, d, cid):
    """认准此数：一圈 100 个圆点按真实百分比逐个亮起，数字跟着数上去，最后一枚红印章旋转着盖下来（−18° → −8°）。
    参数：pct、big、seal（印文四字）、at_stamp。"""
    pct = max(0.0, min(100.0, float(b.get("pct", 50))))
    big = str(b.get("big", f"{pct:g}%"))
    cx, cy, R = 480, 440, 418          # the ring is 860 px across (dot edge to dot edge)
    lit_full = int(pct)
    frac = pct - lit_full
    dots_off, dots_on = "", ""
    for k in range(100):
        a = math.radians(-90 + 3.6 * k)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        dots_off += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{CREAM}" stroke="{SILK_LO}" stroke-width="2.5"/>'
        if k < lit_full:
            dots_on += f'<circle class="dt" cx="{x:.1f}" cy="{y:.1f}" r="11.5" fill="{NUM_LO}" stroke="{GOLD_HI}" stroke-width="2.5"/>'
        elif k == lit_full and frac > 0.05:
            # a part-lit dot: the lit share is the left part of the dot, in the travel direction
            dots_on += (f'<g class="dt"><clipPath id="hc{cid}"><rect x="{x - 12:.1f}" y="{y - 12:.1f}" width="{24 * frac:.1f}" height="24" '
                        f'transform="rotate({3.6 * k:.1f} {x:.1f} {y:.1f})"/></clipPath>'
                        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11.5" fill="{NUM_LO}" clip-path="url(#hc{cid})"/></g>')
    ring = (f'<svg class="a ring" viewBox="0 0 {BW} {BH}" style="left:0;top:0;width:{BW}px;height:{BH}px">'
            f'<circle cx="{cx}" cy="{cy}" r="{R + 30}" fill="none" stroke="{SILK_LO}" stroke-width="3" opacity=".6"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R - 30}" fill="none" stroke="{SILK_LO}" stroke-width="2" opacity=".5"/>'
            f'<g transform="translate(4 5)" opacity=".35">{dots_off.replace(CREAM, SILK_LO)}</g>{dots_off}<g class="on">{dots_on}</g>'
            f'<circle cx="{cx + 10}" cy="{cy + 12}" r="{R - 62}" fill="{SILK_LO}" opacity=".55"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R - 62}" fill="{CREAM}" stroke="{DEEP}" stroke-width="5"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{R - 76}" fill="none" stroke="{GOLD}" stroke-width="3"/></svg>')
    px = min(210, 580 / max(0.5, anton_w(big)))
    X.used_text.update(big + "0123456789.%")
    gcy = cy - 80                       # number glyph centre, the seal sits under it on the same cream disc
    num = (f'<div class="a nb" style="left:{cx - 330}px;top:{gcy - 0.569 * px:.0f}px;width:660px;text-align:center">'
           f'{num_block(X, big, "", px, "red", "hn")}</div>')
    lab = b.get("label", "")
    word = str(b.get("seal", "认准此数"))[:4]
    X.used_text.update(word)
    # the seal: uneven ink edge (displacement), cream inner ring, four characters in a 2 × 2 grid
    sx_, sy_, sr = cx, cy + 190, 108
    # two horizontal rows reading left to right: 认准 / 此数
    chars = "".join(f'<text x="{sx_ + (-32 if j % 2 == 0 else 32)}" y="{sy_ + (-8 if j < 2 else 54)}" text-anchor="middle">{c}</text>'
                    for j, c in enumerate(word))
    sealsvg = (f'<svg class="a sl" viewBox="0 0 {BW} {BH}" style="left:0;top:0;width:{BW}px;height:{BH}px;transform-origin:{sx_}px {sy_}px;visibility:hidden">'
               f'<defs><filter id="ink{cid}" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="3"/>'
               f'<feDisplacementMap in="SourceGraphic" scale="7"/></filter></defs>'
               f'<g filter="url(#ink{cid})"><circle cx="{sx_}" cy="{sy_}" r="{sr}" fill="{SILK}"/>'
               f'<circle cx="{sx_}" cy="{sy_}" r="{sr - 13}" fill="none" stroke="{CREAM}" stroke-width="6"/>'
               f'<g fill="{CREAM}" font-family="var(--f-display)" font-size="58">{chars}</g></g></svg>')
    ink = (f'<svg class="a ink" viewBox="0 0 {BW} {BH}" style="left:0;top:0;width:{BW}px;height:{BH}px;opacity:0;transform-origin:{sx_}px {sy_}px">'
           f'<circle cx="{sx_}" cy="{sy_}" r="{sr + 10}" fill="none" stroke="{SILK}" stroke-width="5"/></svg>')
    stage = ring + num + ink + sealsvg + sparkle("k1", cx + 300, cy - 300, 1.1)
    s, t0 = page(X, b, cid, t, d, stage)
    # dots light clockwise while the number counts up
    tc = t0 + 0.3
    dur = 0.9
    n_on = lit_full + (1 if frac > 0.05 else 0)
    X.tw(f'tl.fromTo("{s} .dt", {{opacity:0}}, {{opacity:1, duration:0.01, ease:"none", stagger:{dur / max(1, n_on):.4f}, immediateRender:false}}, {tc:.3f});')
    X.tw(f'tl.set("{s} .dt", {{opacity:0}}, {t:.3f});')
    suf = "%" if big.endswith("%") else ""
    core = big[:-1] if suf else big
    dec = len(core.split(".")[1]) if "." in core else 0
    try:
        val = float(core)
    except ValueError:
        val = pct
    X.tw(f'(()=>{{const o={{v:0}}, els=document.querySelectorAll("{s} .hn .g3 > span, {s} .hn .bl"); tl.fromTo(o, {{v:0}}, {{v:{val}, duration:{dur:.2f}, ease:"none", '
         f'onUpdate:()=>{{const s=o.v.toFixed({dec})+"{suf}"; els.forEach(e=>e.textContent=s);}}, immediateRender:false}}, {tc:.3f});}})();')
    for k in range(5):
        X.sfx(tc + k * 0.2, "count")
    blink(X, f"{s} .hn .bl", tc + dur + 0.02)
    tst = max(tc + dur + 0.3, T(X, b, "at_stamp", t, tc + dur + 0.35) - 5 * F)
    X.tw(f'tl.set("{s} .sl", {{visibility:"visible"}}, {tst:.3f});')
    X.tw(f'tl.fromTo("{s} .sl", {{scale:1.75, rotation:-18, opacity:0}}, {{scale:1, rotation:-8, opacity:1, duration:{5 * F:.3f}, ease:"power3.in", immediateRender:false}}, {tst:.3f});')
    hit = tst + 5 * F
    X.tw(f'tl.fromTo("{s} .ink", {{opacity:.8, scale:1}}, {{opacity:0, scale:1.22, duration:0.3, ease:"power2.out", immediateRender:false}}, {hit:.3f});')
    for j, dx in enumerate((4, -4, 3, -1, 0)):
        X.tw(f'tl.set("{s} .shk", {{x:{dx}, y:{dx}}}, {hit + j * F:.3f});')
    X.sfx(hit - 0.02, "stamp")
    glint(X, f"{s} .k1", hit + 0.3)
    claim_in(X, s, hit + 0.4, d)
    hold_zoom(X, s, hit + 0.2, t + d)


def endcard(b, X, t, d, cid):
    """总结牌（代替「拨打热线」那一镜，不出现任何电话号码）：奶油色大牌子上三行数逐行砸上，角上一枚爆炸签。参数：rows [{k, v, u}]。"""
    rows = b.get("rows", [])[:3]
    X.used_text.update("".join(r.get("k", "") + r.get("v", "") + r.get("u", "") for r in rows))
    px0, py0, pw, ph = 40, 60, 880, 760
    plate = (f'<div class="a ep" style="left:{px0}px;top:{py0}px;width:{pw}px;height:{ph}px;background:{CREAM};border:7px solid {SILK_LO};'
             f'box-shadow:inset 0 0 0 7px {CREAM}, inset 0 0 0 11px {GOLD}, inset 0 0 0 15px {CREAM}, inset 0 0 0 17px {GOLD}, 16px 16px 0 {SILK_LO};transform-origin:50% 50%"></div>')
    rh = (ph - 80) / max(1, len(rows))
    html = ""
    for k, r in enumerate(rows):
        y = py0 + 40 + k * rh
        v, u = r.get("v", ""), r.get("u", "")
        vpx = min(150, 470 / max(0.5, anton_w(v)))
        html += (f'<div class="a er er{k}" style="left:{px0 + 50}px;top:{y:.0f}px;width:{pw - 100}px;height:{rh:.0f}px;transform-origin:50% 50%">'
                 f'<div style="position:absolute;left:0;top:{rh / 2 - 34:.0f}px;font-family:var(--f-display);font-size:56px;color:{SILK_LO};line-height:1.2">{X.rich(r.get("k", ""))}</div>'
                 f'<div style="position:absolute;right:0;top:{rh / 2 - vpx * 0.62:.0f}px;text-align:right">{num_block(X, v, u, vpx, "red", "en", upx=40, ucol=SILK_LO, blinkable=False)}</div>'
                 + (f'<i style="position:absolute;left:0;right:0;bottom:0;height:4px;background:linear-gradient(90deg,{GOLD},#f2b61e,{GOLD})"></i>' if k < len(rows) - 1 else "")
                 + '</div>')
    pts = starburst(16, 92, 74, 0, 0)
    badge = (f'<svg class="a eb" viewBox="-110 -110 220 220" style="left:{px0 - 70}px;top:{py0 - 90}px;width:220px;height:220px;visibility:hidden">'
             f'<polygon points="{pts}" transform="translate(7 8)" fill="{SILK_LO}"/><polygon points="{pts}" fill="{SILK}" stroke="{CREAM}" stroke-width="5"/>'
             f'<text x="0" y="20" text-anchor="middle" font-family="var(--f-num)" font-size="58" fill="{GOLD_HI}" stroke="{SILK_LO}" stroke-width="2">2024</text></svg>')
    X.used_text.update("2024")
    stage = plate + html + badge + sparkle("k1", px0 + 120, py0 - 40, 1.0)
    s, t0 = page(X, b, cid, t, d, stage)
    X.tw(f'tl.fromTo("{s} .ep", {{scaleY:0.02}}, {{scaleY:1, duration:{6 * F:.3f}, ease:"power4.out"}}, {t0 + 0.3:.3f});')
    tk = t0 + 0.55
    for k in range(len(rows)):
        X.tw(f'tl.set("{s} .er{k}", {{visibility:"hidden"}}, {t:.3f});')
        slam(X, f"{s} .er{k}", tk, frm=1.6, dip=0.96, snd="slam")
        tk += 0.42
    hit = slam(X, f"{s} .eb", tk + 0.05, frm=2.2, flash=f"{s} .flash", shake=f"{s} .shk")
    glint(X, f"{s} .k1", hit + 0.35)
    claim_in(X, s, hit + 0.45, d)
    hold_zoom(X, s, hit + 0.2, t + d - 10 * F)


SCENES = {"burst": burst, "versus": versus, "countdown": countdown, "bundle": bundle, "seal": seal, "endcard": endcard}


# ---------------------------------------------------------------- effects in this style (shared fx beats)
STYLE["fx_themes"] = {
    "paper": {"bg": GOLD, "fg": BLACK, "muted": "#4a2a10", "accent": SILK, "card": CREAM, "card-fg": SILK_LO, "line": "rgba(26,13,8,.3)"},
    "ink":   {"bg": "#5a0a10", "fg": CREAM, "muted": "#f0d9b0", "accent": "#f2b61e", "card": CREAM, "card-fg": SILK_LO, "line": "rgba(255,243,207,.3)"},
    "red":   {"bg": SILK, "fg": CREAM, "muted": "#f6dcc0", "accent": "#f2b61e", "card": CREAM, "card-fg": SILK_LO, "line": "rgba(255,243,207,.3)"},
    "lemon": {"bg": CREAM, "fg": BLACK, "muted": "#5a3a1a", "accent": SILK, "card": "#fffaf0", "card-fg": SILK_LO, "line": "rgba(26,13,8,.2)"},
}

FX_CSS = r"""
/* an effect's ground: the same crumpled foil relief, in the theme's colour */
.st-teleshop .fx { background-image:__FOIL__ !important; background-size:100% 100% !important; background-blend-mode:soft-light; }
.st-teleshop .fx .big, .st-teleshop .fx .op .op-t { font-family:var(--f-display); font-weight:400; text-shadow:2px 2px 0 #6f0a10, 4px 4px 0 #6f0a10, 6px 6px 0 #6f0a10, 8px 8px 0 #6f0a10; }
/* the page around an effect (FX_FRAME): silk title band, red ribbon caption, source strip */
.ctx.tsx .hd { left:60px; right:60px; top:210px; height:120px; border:none; display:block; }
.ctx.tsx .hd > svg { position:absolute; left:0; top:0; }
.ctx.tsx .hd .bt { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; padding-bottom:6px; }
.ctx.tsx .cap { left:0; right:0; bottom:auto; top:1376px; padding:0 120px 0 90px; text-align:left; }
.ctx.tsx .cap > span { display:block; box-sizing:border-box; height:80px; line-height:76px; padding:0 66px; text-align:center; font-family:var(--f-cap); font-weight:900;
  color:#fff3cf; background:__CAP__; border-top:2px solid #f2b61e; border-bottom:2px solid #f2b61e; border-radius:0; white-space:nowrap;
  clip-path:polygon(0 0, 100% 0, calc(100% - 30px) 50%, 100% 100%, 0 100%, 30px 50%); text-shadow:0 3px 0 #5a070c; }
.ctx.tsx .cap .em .emt { background:none; color:#f6dc8a; padding:0; } .ctx.tsx .cap .em .emb { display:none; }
.ctx.tsx .ft { left:90px; right:120px; top:1470px; bottom:auto; opacity:1; color:#fff3cf; font-size:24px; background:rgba(26,13,8,.7); padding:4px 16px;
  flex-direction:column; align-items:flex-start; gap:2px; }
#root.h .ctx.tsx .hd { left:560px; right:560px; top:104px; }
#root.h .ctx.tsx .cap { top:850px; padding:0 520px; }
#root.h .ctx.tsx .ft { left:520px; right:520px; top:944px; }
"""
STYLE["css"] = (FX_CSS.replace("__FOIL__", foil_uri(1080, 1920, 7)).replace("__FOLDS__", FOLDS).replace("__CAP__", CAP_FOLDS)
                + CAP_CSS.replace("__CAP__", CAP_FOLDS))


def FX_FRAME(X, cid, t, d, p, parts):
    """the commercial around a shared effect: the silk title band with the topic in 3D gold, the spoken line on the red
    ribbon, the source on the dark strip; the valance, ticker and CRT glass of the set stay on."""
    world(X)
    X.css("teleshop", CSS.replace("__FOLDS__", FOLDS).replace("__NOISE__", NOISE).replace("__STATIC__", STATIC))
    l = L(X)
    bx, by, bw, bh = l["bn"]
    topic = parts["topic"] or X.rich(X.channel)
    X.used_text.update(X.channel)
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + f'<div class="hd">{silk_svg(bw, bh, cid + "x")}<div class="bt"><span class="fr3"><span class="g3 title" data-layout-allow-overlap style="font-size:{min(110, l["title"])}px;font-family:var(--f-display)">'
               f'<span class="x" style="-webkit-text-stroke:8px {DEEP};text-shadow:{", ".join(f"{k}px {k}px 0 {DEEP}" for k in range(1, 13))}">{topic}</span>'
               f'<span class="o" style="-webkit-text-stroke:8px {DEEP};color:{DEEP}">{topic}</span><span class="h">{topic}</span><span class="f">{topic}</span></span></span></div></div>'
             + f'<div class="cap"><span style="font-size:44px">{parts["cap"]}</span></div>'
             + (f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>' if (parts["foot"] or parts["src"]) else ""))
    X.clip(f"{cid}c", t, d, inner, f"ctx tsx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .hd .g3", {{scale:1.7, opacity:0}}, {{scale:1, opacity:1, duration:{6 * F:.3f}, ease:"power2.in"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .cap > span", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:{6 * F:.3f}, ease:"power4.out"}}, {t + 0.2:.3f});')
