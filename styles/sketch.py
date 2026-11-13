"""sketch · 手绘白板风 —— RSA Animate / Minute Physics / 国内手绘科普的语言，换到一张牛皮纸上：一支黑色马克笔，一支白色油漆笔，讲到哪画到哪。

底是牛皮纸（#c9a877，带纤维和斑点，不是方格本）；黑马克笔（10–14 px）负责线和字，白油漆笔负责填色和高光，红笔圈重点、划掉，
蓝笔连线。每一笔都经过一层湍流位移，边缘毛糙、粗细不匀，不是均匀的矢量线。线条有起笔和收笔的超出、轻微的弯曲和抖动，
圆圈画过头一点再收住，箭头是两笔勾出来的；柱子一笔一笔排线，坐标轴带刻度。

竖屏整页都用上：上面是手写大标题（150–220 px），中间是主图（≥ 800 px 宽）和白底黑边的关键数字（320–480 px，画完再补两道下划线），
下面是一条手画的标尺：同一章里前面每一页的主图画完后缩小、滑到标尺上排成一行（不擦掉），所以纸面越讲越满。字幕是一条撕开的美纹纸胶带。

几何全部在构建时用带种子的随机数算好（同一份 video.json 每次画出完全一样的线），不依赖浏览器里的 rough.js；
每条线用 pathLength=1 + stroke-dashoffset 画出来，笔尖跟着线走，镜头跟着笔，每页最后拉远看全页。

场景（SCENES）：hook 大数字 + 涂鸦 · bar 一根条拆成两段 · question 问号和候选答案 · ratio 两个量比一比 · tag 价签划掉改价 ·
dots 100 个小人里有几个 · loop 循环箭头 · thesis 划掉一个词、圈出另一个 · outro 白卡落版。横屏竖屏各自排版。
每个场景都可以加 "head"（手写大标题）；beat 写 "chapter" 时标尺清空，从新的一章开始攒。
"""
import math, random
from urllib.parse import quote
from h9 import fit

KRAFT = "#c9a877"
STYLE = {
    "name": "手绘白板", "en": "Sketch", "benchmarks": ["RSA Animate", "Minute Physics", "国内手绘科普"],
    "tokens": {
        "bg": KRAFT, "fg": "#161616", "paper": KRAFT, "ink": "#161616", "muted": "#3e2c14", "accent": "#a51f17", "accent2": "#fdfdf8",
        "alert": "#a51f17", "line": "rgba(22,22,22,.35)", "card": "#fdfdf8", "card-fg": "#161616",
        "red": "#e23a2e", "blue": "#2456c8", "blue-ink": "#1b3f99", "green": "#2f7a4a", "hl": "#fdfdf8", "white": "#fdfdf8", "tape": "rgba(239,230,207,.9)",
        "cap-bg": "transparent", "cap-fg": "#161616", "cap-size": "38px", "cap-weight": "400", "cap-pad": "12px 44px 15px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "40px", "cap-em": "#e23a2e", "punch-top": "71%", "punch-size": "70px", "punch-stroke": "0",
    },
    "fonts": {"display": "lxgw-marker", "body": "lxgw-marker", "hand": ["caveat", "lxgw-marker"], "num": ["permanent-marker", "lxgw-marker"],
              "latin": ["patrick-hand", "lxgw-marker"], "punch": "lxgw-marker", "cap": "lxgw-marker", "quiet": "lxgw-marker",
              "mono": ["patrick-hand", "lxgw-marker"], "quote": ["caveat", "lxgw-marker"]},
    "motion": {"ease": "power2.out", "dur": 0.5, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07})],
    # the host is redrawn as a marker doodle: posterised to black and white, then a thick black outline (CSS below)
    "safe_exempt": [".hd"],     # 9:16 page furniture (header / HUD / legend / scale bar) may sit under the platform chrome
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 80, "bottom": 70, "h": 360}, "portrait": {"right": 30, "bottom": 470, "h": 330}},
    "sfx": {"transition": ("paper", 0.35), "enter": ("paper", 0.3), "pop": ("pop", 0.4), "hit": ("tick", 0.45), "brush": ("brush", 0.28),
            "line": ("brush", 0.22), "mascot": ("whoosh_soft", 0.25), "title": ("paper", 0.35), "write": ("type", 0.18)},
}


def _svgurl(svg):
    return 'url("data:image/svg+xml,' + quote(svg, safe="") + '")'


# kraft paper: long fibres (dark and light), soft mottling, a few dark specks — all seeded SVG noise, tiled
_FIBRE = _svgurl("<svg xmlns='http://www.w3.org/2000/svg' width='900' height='900'><filter id='f' x='0' y='0' width='100%' height='100%'>"
                 "<feTurbulence type='fractalNoise' baseFrequency='0.045 0.26' numOctaves='3' seed='11' stitchTiles='stitch'/>"
                 "<feColorMatrix values='0 0 0 0 0.33  0 0 0 0 0.22  0 0 0 0 0.10  2.6 0 0 0 -1.52'/></filter>"
                 "<filter id='g' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='0.05 0.32' numOctaves='2' seed='4' stitchTiles='stitch'/>"
                 "<feColorMatrix values='0 0 0 0 0.93  0 0 0 0 0.84  0 0 0 0 0.66  0 2.4 0 0 -1.5'/></filter>"
                 "<rect width='900' height='900' filter='url(#f)'/><rect width='900' height='900' filter='url(#g)'/></svg>")
_MOTTLE = _svgurl("<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='1200'><filter id='m' x='0' y='0' width='100%' height='100%'>"
                  "<feTurbulence type='fractalNoise' baseFrequency='0.006' numOctaves='3' seed='23' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 0.45  0 0 0 0 0.31  0 0 0 0 0.14  1.3 0 0 0 -0.52'/></filter>"
                  "<filter id='s' x='0' y='0' width='100%' height='100%'><feTurbulence type='fractalNoise' baseFrequency='0.55' numOctaves='1' seed='5' stitchTiles='stitch'/>"
                  "<feColorMatrix values='0 0 0 0 0.16  0 0 0 0 0.10  0 0 0 0 0.04  9 0 0 0 -6.1'/></filter>"
                  "<rect width='1200' height='1200' filter='url(#m)'/><rect width='1200' height='1200' filter='url(#s)'/></svg>")
KRAFT_BG = f"{_FIBRE}, {_MOTTLE}"
KRAFT_SIZE = "900px 900px, 1200px 1200px"

CSS = r"""
.sk { position:absolute; inset:0; background-color:var(--paper); overflow:hidden; }
.sk .paper { position:absolute; inset:-40%; background-color:var(--paper); background-image:""" + KRAFT_BG + """; background-size:""" + KRAFT_SIZE + """; }
.sk .cam { position:absolute; inset:0; }
.sk svg.ink { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.sk svg.ink path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.sk svg.ink .solid { stroke:none; }
.sk .t { position:absolute; white-space:nowrap; line-height:1.15; color:var(--ink); font-family:var(--f-display); font-weight:400; transform-origin:0 70%; font-synthesis:none; }
.sk .t.hd1 { -webkit-text-stroke:.026em currentColor; paint-order:stroke fill; letter-spacing:.01em; }
.sk .t.hand { font-family:var(--f-hand); font-weight:700; }
.sk .t.num { font-family:var(--f-num); font-weight:400; letter-spacing:.005em; }
.sk .t.big { color:var(--white); -webkit-text-stroke:.05em var(--ink); paint-order:stroke fill; filter:drop-shadow(.025em .03em 0 rgba(22,22,22,.55)); }
.sk .t.lat { font-family:var(--f-latin); }
.sk .pen { position:absolute; left:0; top:0; width:0; height:0; z-index:8; pointer-events:none; }
.sk .pen svg { position:absolute; left:-6px; top:-148px; width:120px; height:160px; overflow:visible; filter:drop-shadow(8px 12px 6px rgba(40,24,6,.35)); }
.sk .hd { position:absolute; left:96px; right:96px; top:30px; display:flex; justify-content:space-between; align-items:flex-start; z-index:6; pointer-events:none; }
.sk .hd .l { font-family:var(--f-display); font-size:30px; color:var(--ink); }
.sk .hd .l small { font-size:28px; color:var(--muted); margin-left:14px; }
.sk .hd .r { font-family:var(--f-num); font-size:32px; color:var(--accent); }
.sk .ft { position:absolute; left:96px; right:640px; bottom:18px; font-family:var(--f-display); font-size:28px; color:var(--muted); z-index:6; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sk .card { position:absolute; background:var(--white); box-shadow:10px 14px 0 rgba(40,24,6,.28); }
.sk .tape { position:absolute; background:var(--tape); }
#root.v .sk .hd { left:60px; right:60px; top:150px; }
#root.v .sk .ft { left:60px; right:60px; bottom:auto; top:192px; font-size:28px; white-space:nowrap; line-height:1.3; }
/* caption: a strip of cream masking tape with torn ends, black marker text, a slight tilt */
.st-sketch .clip.cap .cp { font-family:var(--f-cap); font-size:38px; font-weight:400; color:#161616; line-height:1.25; text-shadow:none; border-radius:0;
  background:linear-gradient(90deg, rgba(255,255,255,.10), rgba(255,255,255,0) 30%, rgba(120,90,40,.06) 70%, rgba(255,255,255,.08)), rgba(239,230,207,.9);
  padding:12px 46px 15px; transform:rotate(-1.4deg);
  clip-path:polygon(0 9%, 1.6% 0, 97.9% 3%, 100% 12%, 98.6% 27%, 100% 44%, 98.4% 61%, 99.8% 79%, 98.7% 100%, 1.8% 97%, .3% 84%, 1.7% 67%, 0 50%, 1.5% 31%); }
.st-sketch .clip.cap { filter:drop-shadow(0 6px 4px rgba(40,24,6,.28)); }
.st-sketch .clip.cap .cp .em .emt { color:#a51f17; }
#root.v.st-sketch { --cap-bottom:424px; }
#root.v.st-sketch .clip.cap { padding-left:90px; padding-right:90px; }
/* the host as a marker doodle */
.st-sketch .mascot { filter:grayscale(1) contrast(7) brightness(1.3) drop-shadow(5px 0 0 #161616) drop-shadow(-5px 0 0 #161616) drop-shadow(0 5px 0 #161616) drop-shadow(0 -5px 0 #161616) drop-shadow(10px 12px 0 rgba(40,24,6,.3)); }
"""

# ---------------------------------------------------------------- effect cards (gallery effects drawn on the board)
# four grounds, one per page theme: graph-paper notebook · chalkboard · pink sticky-note dot grid · yellow legal pad.
# The extra keys (tex / tex-size / capbg / capfg / tape) ride along as CSS variables on each effect clip and its frame.
_GRID = "linear-gradient({a} 1.5px, transparent 1.5px), linear-gradient(90deg, {a} 1.5px, transparent 1.5px), linear-gradient({b} 1px, transparent 1px), linear-gradient(90deg, {b} 1px, transparent 1px)"
STYLE["fx_themes"] = {
    "paper": {"bg": KRAFT, "fg": "#161616", "muted": "#3e2c14", "accent": "#e23a2e", "card": "#fdfdf8", "card-fg": "#161616", "line": "rgba(22,22,22,.3)",
              "tex": KRAFT_BG, "tex-size": KRAFT_SIZE, "capbg": "#efe6cf", "capfg": "#161616", "tape": "rgba(239,230,207,.9)"},
    "ink":   {"bg": "#24312c", "fg": "#f1eee4", "muted": "#a9b4ac", "accent": "#ffd84a", "card": "#2d3b35", "card-fg": "#f1eee4", "line": "rgba(241,238,228,.2)",
              "tex": "radial-gradient(ellipse 40% 30% at 22% 30%, rgba(255,255,255,.07), transparent 70%), radial-gradient(ellipse 35% 28% at 78% 72%, rgba(255,255,255,.05), transparent 70%), "
                     + _GRID.format(a="rgba(241,238,228,.09)", b="rgba(241,238,228,.045)"),
              "tex-size": "100% 100%, 100% 100%, 200px 200px, 200px 200px, 40px 40px, 40px 40px", "capbg": "#ffd84a", "capfg": "#1f1f22", "tape": "rgba(241,238,228,.22)"},
    "red":   {"bg": "#ffd9d2", "fg": "#2a1714", "muted": "#7a4a43", "accent": "#c8261b", "card": "#fff6f3", "card-fg": "#2a1714", "line": "rgba(200,38,27,.25)",
              "tex": "radial-gradient(circle, rgba(200,38,27,.28) 1.8px, transparent 2.4px)", "tex-size": "32px 32px",
              "capbg": "#fff6f3", "capfg": "#2a1714", "tape": "rgba(255,255,255,.6)"},
    "lemon": {"bg": "#fff3b0", "fg": "#1f1f22", "muted": "#66592a", "accent": "#e2483b", "card": "#fffdf2", "card-fg": "#1f1f22", "line": "rgba(43,103,209,.25)",
              "tex": "linear-gradient(90deg, transparent 26px, rgba(226,72,59,.45) 26px, rgba(226,72,59,.45) 28px, transparent 28px, transparent 34px, rgba(226,72,59,.45) 34px, rgba(226,72,59,.45) 36px, transparent 36px), "
                     "linear-gradient(transparent 43px, rgba(43,103,209,.28) 43px, rgba(43,103,209,.28) 45px, transparent 45px)",
              "tex-size": "100% 100%, 100% 45px", "capbg": "#a8dcff", "capfg": "#1f1f22", "tape": "rgba(214,206,186,.85)"},
}
for _k, _v in STYLE["fx_themes"]["paper"].items():          # an effect beat without a theme sits on the notebook
    if _k in ("tex", "tex-size", "capbg", "capfg", "tape"): STYLE["tokens"].setdefault(_k, _v)

_W1 = "10px 22px 9px 26px / 20px 9px 24px 11px"             # wobbly radii: boxes that were drawn, not set
_W2 = "47% 53% 50% 46% / 53% 46% 54% 47%"
_HATCH = "repeating-linear-gradient(-52deg, transparent 0 7px, rgba(255,255,255,.26) 7px 9px)"
STYLE["css"] = r"""
/* every effect sits on its theme's paper; marker faces stay single-weight (no faux bold) */
#root .fx { background-image:var(--tex) !important; background-size:var(--tex-size) !important; background-position:0 0 !important; }
#root .fx, #root .fx *, #root .ctx, #root .ctx * { font-synthesis:none; }
/* hand-drawn internals: wobbly radii, ink outlines, flat offset shadows, pencil hatching on filled shapes */
#root .fx .qc .qc-face { border-radius:""" + _W1 + """; box-shadow:8px 10px 0 color-mix(in srgb, var(--fg) 16%, transparent), inset 0 0 0 3.5px var(--fg); }
#root .fx .qc .qc-o { border-radius:""" + _W1 + """; box-shadow:inset 0 0 0 2.5px color-mix(in srgb, var(--fg) 60%, transparent); }
#root .fx .qc .qc-o b, #root .fx .pc .pc-h i, #root .fx .sp .sp-n, #root .fx .sp .sp-n .ring, #root .fx .sp .sp-n .fill, #root .fx .sp .sp-n .done,
#root .fx .ls .ls-n, #root .fx .dt .dtdot, #root .fx .sp .sp-tok { border-radius:""" + _W2 + """; }
#root .fx .dt .dtn { border-radius:""" + _W1 + """; box-shadow:inset 0 0 0 3px var(--fg), 5px 6px 0 color-mix(in srgb, var(--fg) 14%, transparent); }
#root .fx .dt .dtn.on { box-shadow:inset 0 0 0 5px var(--accent), 5px 6px 0 color-mix(in srgb, var(--fg) 14%, transparent); }
#root .fx .dt .dtn.lf.on { box-shadow:5px 6px 0 color-mix(in srgb, var(--fg) 18%, transparent); background-image:""" + _HATCH + """; }
#root .fx .dt .dte { stroke-linecap:round; stroke-dasharray:none; }
#root .fx .gt .gtb { border-radius:4px 11px 5px 12px / 9px 4px 11px 5px; background-image:""" + _HATCH + """ !important; }
#root .fx .ls .ls-hi { border-radius:""" + _W1 + """; background-image:""" + _HATCH + """; }
#root .fx .pc .pc-v { border-radius:""" + _W1 + """; background-image:""" + _HATCH + """; }
#root .fx .tc .tc-p { border-radius:""" + _W1 + """; }
#root .fx .lc .lcl { stroke-width:6; }
#root .fx .lc .lca { opacity:.22; }
/* the frame around an effect */
.ctx.skx .hd { position:absolute; left:96px; right:96px; top:30px; height:auto; border:0; display:flex; align-items:flex-end; justify-content:space-between; }
.ctx.skx .hd .l { font-family:var(--f-display); font-size:32px; color:var(--fg); line-height:1.1; white-space:nowrap; }
.ctx.skx .hd .l small { font-family:var(--f-quiet); font-size:28px; color:var(--muted); margin-left:14px; }
.ctx.skx .hd .tag { font-family:var(--f-latin); font-size:28px; color:var(--fg); background:var(--tape); padding:2px 16px 4px; transform:rotate(2.5deg); }
.ctx.skx svg.rule { position:absolute; left:0; top:0; overflow:visible; }
.ctx.skx svg.rule path { fill:none; stroke-linecap:round; }
.ctx.skx .cap { position:absolute; left:0; right:0; bottom:62px; text-align:center; }
.ctx.skx .cap > span.cs { position:relative; display:inline-block; max-width:80%; padding:6px 22px 10px; transform:rotate(-.7deg); background:none; border-radius:0;
  color:var(--capfg); font-weight:400; }
.ctx.skx .cs .hlb { position:absolute; inset:2px -4px 0 -2px; background:var(--capbg); transform-origin:0 50%; transform:skewX(-6deg);
  border-radius:3px 16px 4px 22px / 14px 4px 18px 5px; }
.ctx.skx .cs .ct { position:relative; display:inline-block; font-family:var(--f-cap); line-height:1.3; color:var(--capfg); }
.ctx.skx .cs .em .emt { background:none; padding:0; color:#d13a2c; text-decoration:underline wavy #d13a2c; text-decoration-thickness:3px; text-underline-offset:.2em; }
.ctx.skx .cs .em .emb { display:none; }
.ctx.skx .ft { position:absolute; left:96px; right:96px; bottom:16px; display:flex; justify-content:space-between; gap:40px; font-family:var(--f-quiet); font-size:28px; color:var(--muted); opacity:1; }
.ctx.skx .ft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:58%; }
.ctx.skx .tp { position:absolute; width:170px; height:42px; background:var(--tape); }
#root.h .ctx.skx.host .ft { right:440px; }
#root.v .ctx.skx.host .hd .tag { margin-right:250px; }      /* 9:16: the host sits top-right, the effect label steps left of it */
#root.v .ctx.skx .hd { left:56px; right:56px; top:206px; } #root.v .ctx.skx .hd .l { font-size:30px; }
#root.v .ctx.skx .cap { bottom:auto; top:1330px; padding:0 120px; } #root.v .ctx.skx .cap > span.cs { max-width:100%; }
#root.v .ctx.skx .ft { left:56px; right:120px; bottom:auto; top:1478px; font-size:28px; }
"""


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around a gallery effect, drawn the board's way: marker header with a taped effect label and a hand-drawn
    rule, the spoken line on a torn highlighter strip (keyword in red with a wavy underline), a quiet source line,
    tape on the top corners (16:9). The effect itself gets a light marker wobble through an SVG displacement filter."""
    W, P = X.W, X.portrait
    h = Hand(sum(map(ord, cid)) * 13 + 5)
    ry = 252 if P else 80
    x0, x1 = (56, W - 56) if P else (96, W - 96)
    rd, _ = h.line(x0, ry, x1, ry, over=4)
    rid = f"{cid}rl"
    rule = f'<svg class="rule" width="{W}" height="{X.H}"><path id="{rid}" d="{rd}" pathLength="1" stroke-dasharray="1 2" stroke-dashoffset="1.05" style="stroke:var(--fg);stroke-width:3px;opacity:.75"/></svg>'
    fid = f"{cid}rough"
    defs = (f'<svg width="0" height="0" style="position:absolute"><filter id="{fid}" x="-2%" y="-2%" width="104%" height="104%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="{sum(map(ord, cid)) % 97}"/>'
            f'<feDisplacementMap in="SourceGraphic" scale="3.2" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')
    if not parts["photo"]: X.css(f"skr-{cid}", f"#{cid} > .stage {{ filter:url(#{fid}); }}")
    tapes = "" if P else ('<i class="tp" style="left:-34px; top:22px; transform:rotate(-38deg)"></i>'
                          f'<i class="tp" style="left:{W - 136}px; top:22px; transform:rotate(38deg)"></i>')
    hd = (f'<div class="hd"><div class="l">{X.rich(X.channel)}<small>{parts["topic"]}</small></div>'
          f'<div class="tag">{parts["fxid"]}</div></div>')
    cap = f'<div class="cap"><span class="cs"><i class="hlb"></i><span class="ct" style="font-size:{parts["cap_px"]}px">{parts["cap"]}</span></span></div>'
    ft = f'<div class="ft"><div>{parts["foot"]}</div><div>{parts["src"]}</div></div>'
    X.used_text.update(X.channel)
    host = " host" if p.get("host") else ""
    X.clip(f"{cid}c", t, d, defs + tapes + rule + hd + cap + ft, "ctx skx" + host, 30, track=20, sty=parts["sty"])
    X.tw(f'tl.fromTo("#{rid}", {{strokeDashoffset:1.05}}, {{strokeDashoffset:0, duration:0.5, ease:"power1.inOut"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid}c .hd .tag", {{scale:0.6, rotation:-8, opacity:0, duration:0.3, ease:"back.out(2)"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("#{cid}c .cs .hlb", {{scaleX:0, duration:0.3, ease:"power2.out"}}, {t + 0.08:.3f});')
    X.tw(f'tl.from("#{cid}c .cs .ct", {{x:-14, opacity:0, duration:0.35, ease:"power2.out"}}, {t + 0.2:.3f});')
    if tapes: X.tw(f'tl.from("#{cid}c .tp", {{scaleX:0, opacity:0, duration:0.25, ease:"power2.out", stagger:0.08}}, {t + 0.1:.3f});')


PEN = """<svg viewBox="0 0 120 160"><g transform="rotate(28 6 148)">
<path d="M6 148 L-1 126 L13 126 Z" fill="#161616"/>
<rect x="-3" y="68" width="18" height="60" rx="3" fill="#2a2a2a"/>
<rect x="-7" y="-10" width="26" height="86" rx="9" fill="#161616"/>
<rect x="-7" y="18" width="26" height="30" fill="#fdfdf8" opacity=".92"/>
<rect x="-3" y="24" width="18" height="5" fill="#e23a2e"/>
<rect x="-1" y="-8" width="5" height="78" rx="2" fill="#fff" opacity=".28"/></g></svg>"""


# ---------------------------------------------------------------- geometry (seeded, build time)
def _c(p): return f"{p[0]:.1f},{p[1]:.1f}"


def _bez(p0, p1, p2, p3, n=8):
    out = []
    for i in range(n + 1):
        s = i / n; u = 1 - s
        out.append((u ** 3 * p0[0] + 3 * u * u * s * p1[0] + 3 * u * s * s * p2[0] + s ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * s * p1[1] + 3 * u * s * s * p2[1] + s ** 3 * p3[1]))
    return out


def _len(pts): return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def _smooth(pts, closed=False):
    """catmull-rom through the points -> one cubic path."""
    if len(pts) < 3: return "M" + " L".join(_c(p) for p in pts)
    P = ([pts[-1]] + pts + [pts[0], pts[1]]) if closed else ([pts[0]] + pts + [pts[-1]])
    d = "M" + _c(P[1])
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{_c(c1)} {_c(c2)} {_c(p2)}"
    return d


class Hand:
    """one marker: every mark it makes wobbles a little, overshoots a little, never repeats."""
    def __init__(self, seed, rough=1.0):
        self.r = random.Random(seed); self.k = rough

    def j(self, a): return self.r.uniform(-a, a) * self.k

    def line(self, x1, y1, x2, y2, over=None):
        L = math.hypot(x2 - x1, y2 - y1) or 1
        ux, uy = (x2 - x1) / L, (y2 - y1) / L; nx, ny = -uy, ux
        o = (over if over is not None else self.r.uniform(3, 8)) * self.k
        a = (x1 - ux * o * 0.4 + self.j(1.5), y1 - uy * o * 0.4 + self.j(1.5))
        b = (x2 + ux * o + self.j(1.5), y2 + uy * o + self.j(1.5))
        bow = L * self.r.uniform(-0.022, 0.022) * self.k
        c1 = (a[0] + (b[0] - a[0]) / 3 + nx * bow * self.r.uniform(0.5, 1.3), a[1] + (b[1] - a[1]) / 3 + ny * bow * self.r.uniform(0.5, 1.3))
        c2 = (a[0] + 2 * (b[0] - a[0]) / 3 + nx * bow * self.r.uniform(0.5, 1.3), a[1] + 2 * (b[1] - a[1]) / 3 + ny * bow * self.r.uniform(0.5, 1.3))
        pts = _bez(a, c1, c2, b, 6)
        return f"M{_c(a)} C{_c(c1)} {_c(c2)} {_c(b)}", pts

    def poly(self, pts, closed=False):
        """a pen line through points: straight-ish segments, each with its own wobble."""
        seq = list(pts) + ([pts[0]] if closed else [])
        ds, allp = [], []
        for a, b in zip(seq, seq[1:]):
            d, p = self.line(a[0], a[1], b[0], b[1], over=self.r.uniform(1, 4)); ds.append(d); allp += p
        return " ".join(ds), allp

    def rect(self, x, y, w, h):
        return self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], closed=True)

    def ellipse(self, cx, cy, rx, ry, a0=None, over=0.32, n=30):
        a0 = self.r.uniform(-2.6, -0.6) if a0 is None else a0
        f1, f2 = self.r.uniform(0, 6.3), self.r.uniform(0, 6.3)
        sweep = 2 * math.pi + over * self.r.uniform(0.7, 1.3)
        dx, dy = self.j(rx * 0.06), self.j(ry * 0.08)
        pts = []
        for i in range(n + 1):
            s = i / n; a = a0 + sweep * s
            k = 1 + 0.035 * self.k * math.sin(2 * a + f1) + 0.02 * self.k * math.sin(3 * a + f2)
            pts.append((cx + dx * s + rx * k * math.cos(a), cy + dy * s + ry * k * math.sin(a)))
        return _smooth(pts), pts

    def arrow(self, x1, y1, x2, y2, curve=0.12, head=None):
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        bend = L * curve * (1 if self.r.random() < 0.5 else -1) if curve else 0
        c = ((x1 + x2) / 2 + nx * bend + self.j(4), (y1 + y2) / 2 + ny * bend + self.j(4))
        pts = []
        for i in range(13):
            s = i / 12
            pts.append(((1 - s) ** 2 * x1 + 2 * (1 - s) * s * c[0] + s * s * x2, (1 - s) ** 2 * y1 + 2 * (1 - s) * s * c[1] + s * s * y2))
        tx, ty = x2 - c[0], y2 - c[1]; tl_ = math.hypot(tx, ty) or 1; tx, ty = tx / tl_, ty / tl_
        hl = head or max(16, min(30, L * 0.12))
        hs = []
        for sgn in (1, -1):
            a = math.radians(152 * sgn)
            hx, hy = tx * math.cos(a) - ty * math.sin(a), tx * math.sin(a) + ty * math.cos(a)
            d, p = self.line(x2, y2, x2 + hx * hl, y2 + hy * hl, over=1); hs.append((d, p))
        shaft = _smooth(pts)
        return shaft + " " + hs[0][0] + " " + hs[1][0], pts + hs[0][1] + hs[1][1]

    def hatch(self, x, y, w, h, gap=16, slope=0.9):
        """diagonal fill strokes clipped to the box, drawn as one zig-zag pass of the pen."""
        ds, allp = [], []
        k = 0; c = -h * slope
        while c < w:
            xa, ya = x + max(c, 0), y + (0 if c >= 0 else -c / slope)
            xb, yb = x + min(c + h * slope, w), y + (h if c + h * slope <= w else (w - c) / slope)
            if (xb - xa) > 4:
                a, b = ((xa, ya), (xb, yb)) if k % 2 == 0 else ((xb, yb), (xa, ya))
                d, p = self.line(a[0], a[1], b[0], b[1], over=self.r.uniform(-2, 2)); ds.append(d); allp += p
            c += gap; k += 1
        return " ".join(ds), allp

    def underline(self, x1, x2, y, wave=0.0):
        if not wave: return self.line(x1, y, x2, y)
        n = max(4, int((x2 - x1) / 38)); pts = [(x1 + (x2 - x1) * i / n, y + (wave if i % 2 else -wave) + self.j(2)) for i in range(n + 1)]
        return _smooth(pts), pts

    def strike(self, x1, x2, y, h=10):
        """a scribbled-out word: three fast passes."""
        pts = [(x1 - 6, y + self.j(3)), (x2 + 6, y - h * 0.3 + self.j(3)), (x1 + 4, y + h * 0.4 + self.j(3)), (x2 + 2, y + h * 0.1 + self.j(3))]
        return self.poly(pts)

    def brace(self, x1, x2, y, depth=26, down=True):
        s = 1 if down else -1; m = (x1 + x2) / 2
        pts = [(x1, y), (x1 + 8, y + s * depth * 0.5), (m - 10, y + s * depth * 0.55), (m, y + s * depth), (m + 10, y + s * depth * 0.55), (x2 - 8, y + s * depth * 0.5), (x2, y)]
        pts = [(p[0] + self.j(1.5), p[1] + self.j(1.5)) for p in pts]
        return _smooth(pts), pts

    def qmark(self, cx, cy, s):
        hook = [(cx - 0.42 * s, cy - 0.45 * s), (cx - 0.3 * s, cy - 0.82 * s), (cx + 0.1 * s, cy - 0.95 * s), (cx + 0.42 * s, cy - 0.72 * s),
                (cx + 0.4 * s, cy - 0.38 * s), (cx + 0.05 * s, cy - 0.15 * s), (cx + 0.02 * s, cy + 0.2 * s)]
        hook = [(p[0] + self.j(s * 0.02), p[1] + self.j(s * 0.02)) for p in hook]
        dot_d, dot_p = self.ellipse(cx + 0.02 * s, cy + 0.48 * s, 0.06 * s, 0.06 * s, over=0.6, n=10)
        return _smooth(hook) + " " + dot_d, hook + dot_p

    def check(self, x, y, s):
        return self.poly([(x, y), (x + 0.35 * s, y + 0.38 * s), (x + s, y - 0.45 * s)])

    def star(self, cx, cy, r):
        pts = []
        for i in range(11):
            a = -math.pi / 2 + i * math.pi / 5 * 2
            pts.append((cx + r * math.cos(a) + self.j(r * 0.06), cy + r * math.sin(a) + self.j(r * 0.06)))
        return self.poly(pts)


# doodles: each returns [(d, pts, colour, width)], drawn in order. Main lines are 11 px of black marker.
def cart(h, x, y, s, sy=1.0):
    """a shopping cart with three parcels in it; sy < 1 squashes it into a wide, low cart."""
    Y = lambda v: y + v * s * sy
    out = [h.poly([(x - 0.15 * s, Y(-0.05)), (x, Y(-0.05)), (x + 0.12 * s, Y(0.5)), (x + 0.86 * s, Y(0.5)), (x + 0.98 * s, Y(0.1)), (x + 0.06 * s, Y(0.1))])]
    out.append(h.line(x + 0.14 * s, Y(0.62), x + 0.84 * s, Y(0.62)))
    out.append(h.ellipse(x + 0.24 * s, Y(0.62) + 0.075 * s, 0.07 * s, 0.07 * s, n=12))
    out.append(h.ellipse(x + 0.74 * s, Y(0.62) + 0.075 * s, 0.07 * s, 0.07 * s, n=12))
    boxes = [h.rect(x + 0.18 * s, Y(-0.18), 0.26 * s, 0.26 * s * sy), h.rect(x + 0.48 * s, Y(-0.3), 0.3 * s, 0.38 * s * sy), h.rect(x + 0.32 * s, Y(-0.5), 0.22 * s, 0.24 * s * sy)]
    return [(d, p, "ink", 11) for d, p in out] + [(d, p, "blue", 8) for d, p in boxes]


def card(h, x, y, w, hgt):
    r = []
    r.append((*h.rect(x, y, w, hgt), "ink", 11))
    r.append((*h.line(x, y + hgt * 0.24, x + w, y + hgt * 0.24, over=2), "ink", 9))
    r.append((*h.hatch(x + 6, y + 6, w - 12, hgt * 0.24 - 12, gap=16), "blue", 6))
    r.append((*h.rect(x + w * 0.08, y + hgt * 0.44, w * 0.18, hgt * 0.22), "ink", 7))
    r.append((*h.line(x + w * 0.08, y + hgt * 0.8, x + w * 0.6, y + hgt * 0.8, over=2), "ink", 7))
    return r


def person(h, cx, cy, s, colour="ink"):
    head = h.ellipse(cx, cy - 0.32 * s, 0.16 * s, 0.16 * s, n=14)
    body = h.poly([(cx - 0.3 * s, cy + 0.45 * s), (cx - 0.26 * s, cy + 0.02 * s), (cx + 0.26 * s, cy + 0.02 * s), (cx + 0.3 * s, cy + 0.45 * s)])
    return [(head[0], head[1], colour, 9), (body[0], body[1], colour, 9)]


def coin(h, cx, cy, r, sym="$"):
    c = h.ellipse(cx, cy, r, r, n=18)
    s1 = h.line(cx, cy - r * 0.62, cx, cy + r * 0.62, over=1)
    sp = [(cx + r * 0.3, cy - r * 0.32), (cx, cy - r * 0.42), (cx - r * 0.3, cy - r * 0.24), (cx - r * 0.18, cy - r * 0.02), (cx + r * 0.2, cy + r * 0.06),
          (cx + r * 0.32, cy + r * 0.28), (cx, cy + r * 0.42), (cx - r * 0.32, cy + r * 0.3)]
    s2 = (_smooth(sp), sp)
    return [(c[0], c[1], "ink", 10), (s2[0], s2[1], "ink", 11), (s1[0], s1[1], "ink", 8)]


def tagd(h, x, y, w, hgt):
    pts = [(x, y + hgt * 0.5), (x + hgt * 0.45, y), (x + w, y), (x + w, y + hgt), (x + hgt * 0.45, y + hgt)]
    t = h.poly(pts, closed=True)
    hole = h.ellipse(x + hgt * 0.42, y + hgt * 0.5, hgt * 0.09, hgt * 0.09, n=12)
    return [(t[0], t[1], "ink", 11), (hole[0], hole[1], "ink", 7)]


def tophat(h, cx, cy, s):
    crown = h.poly([(cx - 0.32 * s, cy), (cx - 0.28 * s, cy - 0.7 * s), (cx + 0.28 * s, cy - 0.7 * s), (cx + 0.32 * s, cy)])
    brim = h.ellipse(cx, cy + 0.02 * s, 0.55 * s, 0.12 * s, n=22)
    band = h.line(cx - 0.3 * s, cy - 0.16 * s, cx + 0.3 * s, cy - 0.16 * s, over=2)
    return [(crown[0], crown[1], "ink", 11), (brim[0], brim[1], "ink", 11), (band[0], band[1], "red", 14)]


# ---------------------------------------------------------------- the board: marks, writing, the pen and the camera
class Board:
    """collects every mark and line of writing in drawing order, then times them: an op with `at` starts on that cue,
    the ops between two cues share the time between them (faster when there is a lot to draw, never slower than 1.2×),
    and the pen follows whatever is being drawn."""
    SPEED = 1500        # px of ink per second at natural speed

    def __init__(self, X, cid, t, d, seed=None, tail=0.6):
        self.X, self.cid, self.t, self.d, self.tail = X, cid, t, d, tail
        self.h = Hand(seed if seed is not None else (sum(map(ord, cid)) * 7 + int(t * 100)))
        self.under, self.over, self.html, self.ops = [], [], [], []
        self.n = 0
        self.end = t
        self.keeping = None     # while a list: marks also go to the chapter's ruler (the page's main drawing)
        self.kept = []

    def _id(self):
        self.n += 1
        return f"{self.cid}k{self.n}"

    def _op(self, dur, at, lag, pts, emit, pen=True):
        o = {"dur": dur, "at": at, "lag": lag, "pts": pts, "emit": emit, "pen": pen, "t": None}
        self.ops.append(o)
        return o

    def mark(self, d, pts, colour="ink", w=5, at=None, dur=None, layer="over", pen=True, op=1.0, lag=0.04, cap=None, keepit=None):
        dur = dur if dur is not None else min(0.9, max(0.15, max(_len(pts), 1) / self.SPEED))
        i = self._id()
        st = f"stroke:var(--{colour});stroke-width:{w}px;opacity:{op}" + (f";stroke-linecap:{cap}" if cap else "")
        (self.under if layer == "under" else self.over).append(f'<path id="{i}" d="{d}" pathLength="1" stroke-dasharray="1 2" stroke-dashoffset="1.05" style="{st}"/>')
        if self.keeping is not None and (keepit if keepit is not None else layer != "under"): self.kept.append((d, colour, w, pts))
        emit = lambda t0, du: self.X.tw(f'tl.fromTo("#{i}", {{strokeDashoffset:1.05}}, {{strokeDashoffset:0, duration:{du:.3f}, ease:"power1.inOut"}}, {t0:.3f});')
        return self._op(dur, at, lag, pts, emit, pen)

    def doodle(self, items, at=None, speed=1.0, lag=0.04):
        ops = [self.mark(d, p, c, w, at=at if k == 0 else None, lag=lag if k == 0 else 0.02, dur=min(0.8, max(0.12, _len(p) / (self.SPEED * speed))))
               for k, (d, p, c, w) in enumerate(items)]
        return ops[0] if ops else None

    def hl(self, x1, x2, y, thick, at=None, dur=None, colour="white", lag=0.04):
        """a paint-marker swash under words or inside a shape (white by default; opaque, not a highlighter)."""
        d, p = self.h.underline(x1, x2, y)
        return self.mark(d, p, colour, thick, at=at, dur=dur or min(0.6, max(0.2, (x2 - x1) / 1800)), layer="under", op=0.96, lag=lag, cap="butt")

    def fill(self, x, y, w, h, colour="white", at=None, dur=None, lag=0.04, gap=None):
        """fill a box with paint-marker strokes: back-and-forth passes as wide as the gap between them."""
        gap = gap or max(18, min(34, h / 4))
        n = max(1, int(math.ceil(h / gap)))
        pts = []
        for k in range(n):
            yy = y + gap * (k + 0.5) + self.h.j(2)
            a, b = (x + 4, x + w - 4) if k % 2 == 0 else (x + w - 4, x + 4)
            pts += [(a, yy), (b, yy + self.h.j(3))]
        d = "M" + " L".join(_c(p) for p in pts)
        return self.mark(d, pts, colour, gap * 1.25, at=at, dur=dur or min(0.7, max(0.2, w * n / 5200)), layer="under", op=0.96, lag=lag, cap="round")

    def keep(self, on=True):
        """marks made while keeping is on are the page's main drawing: they slide down onto the ruler next beat."""
        self.keeping = [] if on else None

    def custom(self, dur, emit, at=None, lag=0.04):
        """anything else that takes time on the board (a fill, a stamp): emit(t0, dur) writes its tweens."""
        return self._op(dur, at, lag, None, emit, pen=False)

    def text(self, s, x, y, px, cls="", colour="ink", at=None, dur=None, anchor="start", rot=None, pen=True, w=None, max_w=None, lag=0.04):
        X = self.X
        txt = str(s or "")
        if not txt.strip():
            return {"left": x, "top": y, "w": 0, "px": px, "base": y + px * 0.95, "mid": y + px * 0.55, "gh": px * 0.8, "op": None}
        em = text_em(txt, cls)
        if max_w and em * px > max_w: px = max(28, int(max_w / em))
        width = w or em * px
        left = x - width / 2 if anchor == "middle" else (x - width if anchor == "end" else x)
        rot = self.h.j(1.2) if rot is None else rot
        dur = dur if dur is not None else min(1.0, max(0.25, len(txt.replace(" ", "")) * 0.07))
        i = self._id()
        X.used_text.update(txt)
        ign = ' data-safe="ignore"' if "big" in cls.split() else ""      # a hero number: its line box runs past its ink (the ink is checked on stills)
        self.html.append(f'<div id="{i}" class="t {cls}"{ign} style="left:{left:.0f}px; top:{y:.0f}px; font-size:{px:.0f}px; color:var(--{colour}); transform:rotate({rot:.2f}deg)">{X.rich(txt)}</div>')
        emit = lambda t0, du: X.tw(f'tl.fromTo("#{i}", {{clipPath:"inset(-30% 100% -30% -4%)"}}, {{clipPath:"inset(-30% -4% -30% -4%)", duration:{du:.3f}, ease:"none"}}, {t0:.3f});')
        gt, gb = vbox(txt, cls); gt, gb = y + gt * px, y + gb * px
        n = max(3, min(10, len(txt)))
        pts = [(left + width * k / n, gb - ((gb - gt) * 0.45 if k % 2 else 0)) for k in range(n + 1)]
        o = self._op(dur, at, lag, pts, emit, pen)
        return {"left": left, "top": y, "w": width, "px": px, "base": gb, "mid": (gt + gb) / 2, "gh": gb - gt, "op": o}

    def para(self, s, x, y, mx, width, mn=30, anchor="start", lh=1.22, at=None, **kw):
        """a title that may need two lines: one line while it fits at ≥ 62% of mx, else split at the best break
        near the middle (after punctuation if there is one). Returns the line dicts (empty list for no text)."""
        s = str(s or "").strip()
        if not s: return []
        px = fsz(s, width, mx, 1)
        if px >= max(mn, mx * 0.62) or len(s) < 8:
            return [self.text(s, x, y, max(px, mn), anchor=anchor, max_w=width, at=at, **kw)]
        mid = len(s) / 2
        cuts = [i + 1 for i, ch in enumerate(s[:-1]) if ch in "，、：；。,:; ）)" and abs(i + 1 - mid) < len(s) * 0.3]
        cut = min(cuts, key=lambda i: abs(i - mid)) if cuts else int(round(mid))
        a_, b_ = s[:cut].rstrip(), s[cut:].lstrip()
        px = max(mn, min(fsz(a_, width, mx, 1), fsz(b_, width, mx, 1)))
        l1 = self.text(a_, x, y, px, anchor=anchor, max_w=width, at=at, **kw)
        l2 = self.text(b_, x, y + px * lh, px, anchor=anchor, max_w=width, **kw)
        return [l1, l2]

    def schedule(self):
        ops = self.ops
        if not ops: return
        S, E = self.t + 0.1, self.t + self.d - self.tail
        starts = [] if ops[0]["at"] is not None else [(0, S)]
        starts += [(i, max(self.t, float(o["at"]))) for i, o in enumerate(ops) if o["at"] is not None]
        prev_end = self.t
        for k, (i0, a) in enumerate(starts):
            i1 = starts[k + 1][0] if k + 1 < len(starts) else len(ops)
            end = (starts[k + 1][1] - 0.03) if k + 1 < len(starts) else E
            a = max(a, prev_end)
            seg = ops[i0:i1]
            nat = seg[0]["dur"] + sum(max(0.0, o["lag"]) + o["dur"] for o in seg[1:])
            sc = max(0.12, min(1.6, (end - a) / nat)) if nat > 0 else 1.0
            cur = a; fin = a
            for j, o in enumerate(seg):
                if j: cur = max(a, cur + o["lag"] * sc)
                o["dur"] = max(0.05, o["dur"] * sc); o["t"] = cur
                cur += o["dur"]; fin = max(fin, cur)
            prev_end = fin
        self.end = max(o["t"] + o["dur"] for o in ops)
        for o in ops: o["emit"](o["t"], o["dur"])

    def build(self, extra_under="", extra_html="", extra_over=""):
        self.schedule()
        X, W, H = self.X, self.X.W, self.X.H
        pid = f"{self.cid}pen"
        pen_ops, free = [], self.t
        for o in sorted((o for o in self.ops if o["pen"] and o["pts"]), key=lambda o: o["t"]):
            if o["t"] >= free - 1e-3:
                pen_ops.append((o["t"], o["dur"], o["pts"])); free = o["t"] + o["dur"]
        if pen_ops:
            x0, y0 = pen_ops[0][2][0]
            X.tw(f'tl.set("#{pid}", {{x:{x0 + 260:.0f}, y:{y0 + 320:.0f}, opacity:0}}, {self.t:.3f});')
            ent = max(0.1, min(0.3, pen_ops[0][0] - self.t - 0.01))
            X.tw(f'tl.to("#{pid}", {{x:{x0:.0f}, y:{y0:.0f}, opacity:1, duration:{ent:.3f}, ease:"power2.out"}}, {pen_ops[0][0] - ent - 0.005:.3f});')
            last_end = pen_ops[0][0]
            for t0, dur, pts in pen_ops:
                if t0 - last_end > 0.05:   # lift and travel to the next stroke
                    tv = min(0.25, t0 - last_end - 0.01)
                    X.tw(f'tl.to("#{pid}", {{x:{pts[0][0]:.0f}, y:{pts[0][1]:.0f}, duration:{tv:.3f}, ease:"power2.inOut"}}, {t0 - tv - 0.005:.3f});')
                step = max(1, len(pts) // 9)
                sel = pts[::step] + ([pts[-1]] if (len(pts) - 1) % step else [])
                L = max(_len(sel), 1); acc = 0.0
                for p0, p in zip(sel, sel[1:]):
                    s0 = round(t0 + acc / L * dur, 3); acc += math.hypot(p[0] - p0[0], p[1] - p0[1]); s1 = round(t0 + acc / L * dur, 3)
                    if s1 - s0 < 0.006: continue
                    X.tw(f'tl.to("#{pid}", {{x:{p[0]:.0f}, y:{p[1]:.0f}, duration:{s1 - s0 - 0.001:.3f}, ease:"none"}}, {s0:.3f});')
                last_end = t0 + dur
            X.tw(f'tl.to("#{pid}", {{x:{W + 200}, y:{H * 0.8:.0f}, opacity:0, duration:0.4, ease:"power2.in"}}, {max(last_end + 0.15, self.t + self.d - 0.45):.3f});')
        fid = f"{self.cid}rf"
        rough = (f'<defs><filter id="{fid}" x="-5%" y="-5%" width="110%" height="110%" filterUnits="objectBoundingBox">'
                 f'<feTurbulence type="fractalNoise" baseFrequency="0.09" numOctaves="2" seed="{sum(map(ord, self.cid)) % 89}" result="n"/>'
                 f'<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/></filter></defs>')
        u = f'<svg class="ink under" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#{fid})">{rough}{"".join(self.under)}{extra_under}</svg>'
        o = f'<svg class="ink over" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#{fid})">{"".join(self.over)}{extra_over}</svg>'
        return u + extra_html + "".join(self.html) + o + f'<div class="pen" id="{pid}">{PEN}</div>'


# ---------------------------------------------------------------- helpers
_FM = {}
CHAINS = {"num": ("permanent-marker", "lxgw-marker"), "hand": ("caveat", "lxgw-marker"), "lat": ("patrick-hand", "lxgw-marker"), "": ("lxgw-marker",)}


def _metrics(fid):
    if fid not in _FM:
        _FM[fid] = None
        try:
            from fontTools.ttLib import TTFont
            from h9 import fonts
            fp = fonts.find(fonts.REG[fid]["file"])
            if fp:
                f = TTFont(str(fp), lazy=True)
                _FM[fid] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        except Exception:
            _FM[fid] = None
    return _FM[fid]


_VM = {}


def _vmetrics(fid):
    """(baseline offset in a 1.15 line box, ideograph yMin/yMax, digit yMin/yMax) in em, or None."""
    if fid not in _VM:
        _VM[fid] = None
        m = _metrics(fid)
        try:
            from fontTools.ttLib import TTFont
            from fontTools.pens.boundsPen import BoundsPen
            from h9 import fonts
            f = TTFont(str(fonts.find(fonts.REG[fid]["file"])), lazy=True)
            u = f["head"].unitsPerEm; asc, desc = f["hhea"].ascent / u, -f["hhea"].descent / u
            gs, cmap = f.getGlyphSet(), m[0]
            def ext(ch):
                if ord(ch) not in cmap: return None
                bp = BoundsPen(gs); gs[cmap[ord(ch)]].draw(bp)
                return (bp.bounds[1] / u, bp.bounds[3] / u) if bp.bounds else None
            lat = {}
            for c in map(chr, range(33, 127)):
                e = ext(c)
                if e: lat[c] = e
            _VM[fid] = ((1.15 - asc - desc) / 2 + asc, ext("会"), ext("8"), lat)
        except Exception:
            _VM[fid] = None
    return _VM[fid]


def vbox(txt, cls=""):
    """(top, bottom) of the inked glyphs in em from the top of the text box — so circles, strikes and underlines hug
    the words whatever face draws them."""
    chain = next((CHAINS[k] for k in ("num", "hand", "lat") if k in cls.split()), CHAINS[""])
    prim = _vmetrics(chain[0])
    if not prim: return 0.12, 1.02
    bl = prim[0]; lo, hi = [], []
    t = fit.plain(txt)
    if any(ord(c) > 0x2e7f for c in t):
        e = next((v[1] for v in map(_vmetrics, chain) if v and v[1]), None)
        if e: lo.append(e[0]); hi.append(e[1])
    for c in t:
        e = prim[3].get(c) if c.isascii() else None
        if e: lo.append(max(e[0], -0.18)); hi.append(e[1])
    if not hi: return 0.12, 1.02
    return bl - max(hi), bl - min(lo)


def text_em(txt, cls=""):
    """advance of a line in em, from the font that will draw it (falls back along the role's stack)."""
    chain = next((CHAINS[k] for k in ("num", "hand", "lat") if k in cls.split()), CHAINS[""])
    tot = 0.0
    for ch in fit.plain(txt):
        for fid in chain:
            m = _metrics(fid)
            if m and ord(ch) in m[0]:
                tot += m[1][m[0][ord(ch)]][0] / m[2] + (-0.01 if "num" in cls.split() else 0); break
        else:
            tot += fit.gw(ch)
    return tot


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def geo(X):
    """the page grid per aspect: text column x0..x1, headline top hy, main drawing band m0..m1."""
    if X.portrait:
        return {"x0": 60, "x1": 960, "w": 900, "hy": 248, "m0": 620, "m1": 1390, "cx": 510}     # m1: the drawing ends above the caption (1420–1500); x1: clear of the right-hand buttons
    return {"x0": 110, "x1": 1810, "w": 1700, "hy": 150, "m0": 330, "m1": 930, "cx": 960}


def page(X, b, inner):
    X.css("sketch", CSS)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "白板课"); src = b.get("src", meta.get("src", ""))
    X.used_text.update(sec + src + "" + X.channel + "0123456789/来源：")
    hd = f'<div class="hd" data-layout-allow-overlap><div class="l">{X.rich(X.channel)}<small>{X.rich(sec)}</small></div><div class="r">{i + 1}/{n}</div></div>'
    ft = f'<div class="ft" data-layout-allow-overlap>{"来源：" + X.rich(src) if src else ""}</div>'
    return f'<div class="sk"><div class="cam"><div class="paper"></div>{inner}</div>{hd}{ft}</div>'


def shots(X, sel, t, d, keys):
    """the camera follows the pen: keys = [(time, scale, fx, fy)]; between moves it keeps creeping so nothing sits still.
    The last key of a beat should be the pull-back to the whole page (scale 1)."""
    W, H = X.W, X.H
    def xy(sc, fx, fy):
        x = min(0, max(W - sc * W, W / 2 - sc * fx * W)); y = min(0, max(H - sc * H, H / 2 - sc * fy * H))
        return x, y
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    mx = 1.05 if X.portrait else 1.06     # a headline being written never loses more than ~10 % off-frame
    fin = keys[-1]                       # the last key passed is the pull-back; it stays last and lands by 65 % of the beat
    fin = (min(float(fin[0]), t + d * 0.65 - 0.55),) + tuple(fin[1:])
    keys = sorted(keys[:-1]) + [fin]
    lim = max(t + 0.3, min(float(fin[0]), t + d - 0.9))
    keys = [k for k in keys[:-1] if float(k[0]) < lim - 0.4] + [(lim,) + tuple(fin[1:])]
    ks = []
    for k in keys:
        tk = min(max(float(k[0]), t), t + d - 0.9)
        k = (tk, min(mx, k[1])) + tuple(k[2:])
        if len(ks) > 1 and tk < ks[-1][0] + 0.45: ks[-1] = k        # too close: the later key (the overview) wins
        elif ks and tk < ks[-1][0] + 0.45: continue
        else: ks.append(k)
    keys = ks
    for k, (tk, sc, fx, fy) in enumerate(keys):
        x, y = xy(sc, fx, fy)
        nxt = keys[k + 1][0] if k + 1 < len(keys) else t + d
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});'); hold0 = tk
        else:
            mv = min(0.85, max(0.3, nxt - tk - 0.05)) if k + 1 < len(keys) else 0.55
            X.tw(f'tl.to("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"power3.inOut"}}, {tk:.3f});'); hold0 = tk + mv
        if nxt - hold0 > 0.25 and k + 1 < len(keys):
            x2, y2 = xy(sc * 1.015, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{sc * 1.015:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - hold0 - 0.01:.3f}, ease:"none"}}, {hold0:.3f});')


def put(X, cid, t, d, html):
    """same sheet of kraft all the way through a chapter: a hard cut, the page carries on (the ruler keeps what was drawn)."""
    X.clip(cid, t, d, html, "scene", 2 + X.beat["i"] % 3, track=1 + X.beat["i"] % 2)


def box(X):
    g = geo(X)
    return (g["x0"], g["hy"], g["w"], g["m1"] - g["hy"])


def fsz(text, w, mx, mn=30, lines=1, hand=False):
    em = text_em(text, "num" if hand else "")
    return int(max(mn, min(mx, w / max(em, 0.5))))


_OPEN, _CLOSE = "（(《“‘[", "，。、：；！？）)》”’],.:;!?%"


def _wrap(s, width, mx, mn, maxl=2, cls=""):
    """break a headline into ≤ maxl lines at the biggest size that fits: breaks at spaces / after punctuation cost nothing,
    between two CJK characters a little, inside a Latin word never. Returns (lines, px)."""
    s = " ".join(str(s or "").split())
    if not s: return [], mx
    cand = {}
    for i in range(1, len(s)):
        a_, b_ = s[i - 1], s[i]
        if b_ in _CLOSE or a_ in _OPEN: continue
        if a_ == " " or b_ == " ": cand[i] = 0.0
        elif a_ in _CLOSE: cand[i] = 0.0
        elif ord(a_) > 0x2e7f or ord(b_) > 0x2e7f: cand[i] = 0.35
    def splits(start, k):
        if k == 1:
            yield [s[start:]]
            return
        for i in sorted(cand):
            if i <= start: continue
            for rest in splits(i, k - 1): yield [s[start:i]] + rest
    best = None
    for n in range(1, maxl + 1):
        nb = None
        for parts in splits(0, n):
            ends, acc = [], 0
            for q in parts[:-1]:
                acc += len(q); ends.append(acc)
            parts = [q.strip() for q in parts]
            if not all(parts): continue
            m = max(text_em(q, cls) for q in parts)
            score = m + 0.4 * sum(cand.get(e, 0) for e in ends)
            if nb is None or score < nb[2]: nb = (parts, min(mx, width / m), score)
        if nb is None: continue
        if nb[1] >= mn: return nb[0], nb[1]
        if best is None or nb[1] > best[1]: best = nb
    return best[0], best[1]


def head(B, s, x, y, width, mx=200, mn=150, maxl=2, anchor="start", at=None, colour="ink", lh=1.1, ul="red"):
    """the hand-lettered headline (marker face thickened by a stroke): ≤ maxl lines, 150–220 px; a wavy underline under
    the last line. Returns the line dicts."""
    lines, px = _wrap(s, width, mx, mn, maxl)
    px = int(px)
    out = []
    for k, ln in enumerate(lines):
        out.append(B.text(ln, x, y + k * px * lh, px, cls="hd1", colour=colour, anchor=anchor, at=at if k == 0 else None,
                          dur=min(0.6, max(0.25, len(ln) * 0.05))))
    if out and ul:
        L_ = out[-1]
        d0, p0 = B.h.underline(L_["left"] - 6, L_["left"] + L_["w"] + 10, L_["base"] + max(10, px * 0.08), wave=5)
        B.mark(d0, p0, ul, 9, lag=-0.05)
    return out


CAP_TOP_V = 1405       # 9:16: the caption tape sits at y 1420–1500, above the platform's bottom bar


def big(B, s, x, y, width, mx=440, mn=320, anchor="middle", at=None, dur=0.7, rot=None, ul="red"):
    """a key number in white paint marker with a black outline, then two underlines drawn after it."""
    em = text_em(s, "num")
    px = int(max(mn, min(mx, width / max(em, 0.5))))
    if B.X.portrait and y + px * 0.96 > CAP_TOP_V:     # 9:16: the number and its underlines end above the caption (1420)
        px = int(max(min(px, 540 / max(em, 0.5)), (CAP_TOP_V - y) / 0.96))     # smaller first, never under 540 px wide
        y = min(y, CAP_TOP_V - px * 0.96)                                       # then up
    y -= px * 0.12                       # the face sits low in its line box
    nt = B.text(s, x, y, px, cls="num big", colour="white", anchor=anchor, at=at, dur=dur, rot=0 if rot is None else rot)
    if ul:
        L, R = nt["left"] + px * 0.04, nt["left"] + nt["w"] - px * 0.02
        y1 = nt["base"] + px * 0.07
        d1, p1 = B.h.line(L, y1, R, y1 + B.h.j(4), over=6); B.mark(d1, p1, ul, 12, lag=-0.05, dur=0.22)
        d2, p2 = B.h.line(L + px * 0.08, y1 + px * 0.075, R - px * 0.12, y1 + px * 0.075 + B.h.j(4), over=4); B.mark(d2, p2, ul, 10, lag=0.0, dur=0.18)
        nt["ul"] = y1 + px * 0.075
    else:
        nt["ul"] = nt["base"]
    return nt


# ---------------------------------------------------------------- the ruler: earlier drawings of the chapter stay on the page
def _ruler_geo(X):
    if X.portrait: return {"x0": 60, "x1": 1020, "y": 1724, "n": 8, "box": 100}
    return {"x0": 1060, "x1": 1700, "y": 120, "n": 8, "box": 66}


class Trail:
    """each page's main drawing (the marks made between B.keep() and B.keep(False)) shrinks and slides onto a hand-drawn
    ruler at the start of the next beat; the ruler and everything on it stays for the whole chapter, so the sheet fills up."""
    def __init__(self, X, b, cid, t):
        self.X, self.cid, self.t = X, cid, t
        st = getattr(X, "_sk_trail", None)
        if st is None or b.get("chapter"):
            st = {"items": [], "seed": int(t * 10) + 3}; X._sk_trail = st
        self.st = st
        self.items = list(st["items"])[-_ruler_geo(X)["n"]:]
        self.first = not st["items"] and not st.get("drawn")

    def slot(self, k):
        g = _ruler_geo(self.X)
        sw = (g["x1"] - g["x0"]) / g["n"]
        return g["x0"] + sw * (k + 0.5), g["y"] - 16 - g["box"] / 2, g["box"]

    def ruler_marks(self, h):
        """the ruler: a long strip with ticks (seeded per chapter, so it is the same line on every page)."""
        g = _ruler_geo(self.X)
        hh = Hand(self.st["seed"])
        out = []
        out.append(hh.line(g["x0"], g["y"], g["x1"], g["y"] + hh.j(3), over=8))
        out.append(hh.line(g["x0"], g["y"] + 24, g["x1"], g["y"] + 24 + hh.j(3), over=6))
        sw = (g["x1"] - g["x0"]) / g["n"]
        ticks = []
        for k in range(g["n"] * 4 + 1):
            x = g["x0"] + sw / 4 * k
            ln = 20 if k % 4 == 0 else 10
            ticks.append((x + hh.j(1.5), g["y"] + 24, x + hh.j(1.5), g["y"] + 24 - ln))
        tp = []
        for x1, y1, x2, y2 in ticks: tp += [(x1, y1), (x2, y2)]
        td = " ".join(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" for x1, y1, x2, y2 in ticks)
        return [(out[0][0], out[0][1], "ink", 7), (out[1][0], out[1][1], "ink", 5), (td, tp, "ink", 4)]

    def draw(self, B, at=None):
        """put the ruler on the board: drawn by the pen on the chapter's first page, already there after that;
        a small red arrow marks the slot this page's drawing will take."""
        marks = self.ruler_marks(B.h)
        self.static = ""
        if self.first:
            B.doodle(marks, at=at, speed=3.0)
            self.st["drawn"] = True
        else:
            self.static = "".join(f'<path d="{d}" style="stroke:var(--{c});stroke-width:{w}px"/>' for d, _, c, w in marks)
        k = min(len(self.items), _ruler_geo(self.X)["n"] - 1)
        cx, cy, bx = self.slot(k)
        g = _ruler_geo(self.X)
        ay = g["y"] + 24 + (20 if self.X.portrait else 14)
        da, pa = B.h.arrow(cx, ay + (46 if self.X.portrait else 30), cx, ay, curve=0.0, head=14 if self.X.portrait else 10)
        B.mark(da, pa, "red", 6 if self.X.portrait else 5)

    def svg(self):
        """the drawings already on the ruler; the newest one (last page's) starts where it was and slides down."""
        X, out = self.X, []
        n = len(self.items)
        for k, it in enumerate(self.items):
            cx, cy, bxs = self.slot(k)
            x0, y0, x1, y1 = it["bbox"]
            sc = min(bxs / max(x1 - x0, 1), bxs / max(y1 - y0, 1))
            tx, ty = cx - sc * (x0 + x1) / 2, cy - sc * (y0 + y1) / 2
            gid = f"{self.cid}tr{k}"
            newest = k == n - 1 and it.get("beat") == X.beat["i"] - 1
            dense = sum(d.count("M") for d, _, _ in it["items"]) > 40
            sw = (2.2 if dense else 4.5) if X.portrait else (1.6 if dense else 3.2)
            paths = "".join(f'<path d="{d}" vector-effect="non-scaling-stroke" style="stroke:var(--{c});stroke-width:{(w if newest else sw)}px"/>' for d, c, w in it["items"])
            if newest:
                out.append(f'<g id="{gid}">{paths}</g>')
                X.tw(f'tl.fromTo("#{gid}", {{x:0, y:0, scale:1}}, {{x:{tx:.1f}, y:{ty:.1f}, scale:{sc:.4f}, svgOrigin:"0 0", duration:0.75, ease:"power3.inOut"}}, {self.t + 0.04:.3f});')
                X.tw(f'tl.to("#{gid} path", {{strokeWidth:{sw}, duration:0.75, ease:"power3.inOut"}}, {self.t + 0.04:.3f});')
                X.tw(f'tl.set("#{gid}", {{svgOrigin:"0 0"}}, {self.t:.3f});')
            else:
                out.append(f'<g transform="translate({tx:.1f},{ty:.1f}) scale({sc:.4f})">{paths}</g>')
        return "".join(out)

    def push(self, B):
        """after the page is built: its kept drawing joins the ruler for the pages that follow."""
        if not B.kept: return
        xs = [p[0] for _, _, _, pts in B.kept for p in pts]; ys = [p[1] for _, _, _, pts in B.kept for p in pts]
        self.st["items"].append({"items": [(d, c, w) for d, c, w, _ in B.kept], "bbox": (min(xs), min(ys), max(xs), max(ys)), "beat": self.X.beat["i"]})


def finish(X, b, B, tr, cid, t, d, extra_html="", extra_over="", extra_under=""):
    tr_svg = tr.svg()
    html = page(X, b, B.build(extra_under=getattr(tr, "static", "") + tr_svg + extra_under, extra_html=extra_html, extra_over=extra_over))
    put(X, cid, t, d, html)
    tr.push(B)
    return html


# ---------------------------------------------------------------- scenes
def _icon(h, icon, x, y, s):
    """a doodle that fits the box (x, y, s wide)."""
    f = {"cart": lambda: cart(h, x + 0.15 * s, y + 0.5 * s, s * 0.8), "card": lambda: card(h, x, y + s * 0.15, s, s * 0.63),
         "coin": lambda: coin(h, x + s / 2, y + s / 2, s * 0.4), "tag": lambda: tagd(h, x, y + s * 0.25, s, s * 0.45),
         "person": lambda: person(h, x + s / 2, y + s * 0.55, s * 0.9), "hat": lambda: tophat(h, x + s / 2, y + s * 0.8, s * 0.9)}.get(icon)
    return f() if f else []


def _wide_icon(h, icon, x, y, w, hgt):
    """the beat's doodle as a wide main drawing filling (x, y, w, hgt)."""
    if icon == "cart":
        s = min(w / 1.13, hgt / 0.45)
        sy = max(0.3, min(1.0, (hgt - 0.15 * s) / (1.12 * s)))
        return cart(h, x + 0.15 * s, y + 0.5 * s * sy, s, sy)
    if icon == "card": return card(h, x, y, w, min(hgt, w * 0.6))
    if icon == "tag": return tagd(h, x, y, w, min(hgt, w * 0.4))
    s = min(w, hgt)
    return _icon(h, icon, x + (w - s) / 2, y + (hgt - s) / 2, s)


def hook(b, X, t, d, cid):
    """a big figure in white paint marker, the unit and a note beside it, the beat's doodle drawn wide underneath."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    kick, num, unit, note = b.get("head") or b.get("kicker", ""), str(b.get("value", "")), b.get("unit", ""), b.get("note", "")
    tn = T(X, b, "at_num", t, t + 1.0)
    if P:
        hl_ = head(B, kick, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        ny = (hl_[-1]["base"] + 40) if hl_ else g["m0"]
        nt = big(B, num, g["cx"], ny - 30, g["w"], 440, 320, at=tn - 0.35)
        uy = nt["ul"] + 34
        ut = B.text(unit, g["x1"], uy, 112, cls="hd1", anchor="end", lag=-0.1)
        B.hl(ut["left"] - 14, ut["left"] + ut["w"] + 12, ut["mid"] + 6, ut["gh"] * 0.7, lag=-0.3)
        top = ut["top"] + ut["px"] * 1.2 + 20
        if note:
            nn = B.text(note, g["x0"] + 10, top, 58, cls="hd1", max_w=g["w"] - 20)
            d0, p0 = h.underline(nn["left"], nn["left"] + nn["w"], nn["base"] + 14, wave=4); B.mark(d0, p0, "red", 7, lag=-0.05)
            da, pa = h.arrow(nn["left"] + nn["w"] + 30, nn["mid"], nt["left"] + nt["w"] * 0.8, nt["ul"] + 16, curve=0.3); B.mark(da, pa, "blue", 7)
            top = nn["base"] + 60
        B.keep(); B.doodle(_wide_icon(h, b.get("icon", "cart"), g["x0"] + 110, top, g["w"] - 220, g["m1"] + 30 - top), speed=2.4); B.keep(False)
    else:
        hl_ = head(B, kick, g["x0"], g["hy"] - 10, g["w"] * 0.6, 120, 100, 2, at=t + 0.1)
        ny = (hl_[-1]["base"] + 30) if hl_ else g["m0"]
        nt = big(B, num, g["x0"] - 10, ny, g["w"] * 0.5, 340, 280, anchor="start", at=tn - 0.35)
        uy = nt["ul"] + 24
        ut = B.text(unit, g["x0"], uy, 100, cls="hd1")
        B.hl(ut["left"] - 14, ut["left"] + ut["w"] + 12, ut["mid"] + 6, ut["gh"] * 0.7, lag=-0.3)
        if note:
            nn = B.text(note, ut["left"] + ut["w"] + 50, uy + 30, 44)
        B.keep(); B.doodle(_wide_icon(h, b.get("icon", "cart"), g["x0"] + g["w"] * 0.6, g["hy"] + 80, g["w"] * 0.4, 700), speed=2.4); B.keep(False)
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(t + 0.1, "title"); X.sfx(nt["op"]["t"], "write")
    tw = nt["op"]["t"]
    shots(X, f"#{cid} .cam", t, d, [(t, 1.16, 0.3, 0.16 if P else 0.22), (tw - 0.3, 1.1, 0.5, 0.4), (tw + 0.9, 1.08, 0.5, 0.66), (t + d - 0.9, 1.0, 0.5, 0.5)])


def bar(b, X, t, d, cid):
    """one long bar = 100: the cost part hatched stroke by stroke, the thin slice that matters filled red; an axis with
    ticks under it; the share in white paint marker, pointed at the slice."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    pct = max(2.0, min(60.0, float(b.get("pct", 10)))); title = b.get("head") or b.get("title", ""); bigs = str(b.get("big", f"{pct:g}%"))
    labels = (list(b.get("labels") or []) + ["", ""])[:2]
    tp = T(X, b, "at_pct", t, t + 1.2)
    if P:
        hl_ = head(B, title, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        x0, w = g["x0"], g["w"]
        ly = (hl_[-1]["base"] + 56) if hl_ else g["m0"]
        y0, hh = ly + 96, 160
    else:
        hl_ = head(B, title, g["x0"], g["hy"] - 10, g["w"], 130, 110, 1, at=t + 0.1)
        x0, w = g["x0"], g["w"]
        ly = (hl_[-1]["base"] + 50) if hl_ else g["m0"]
        y0, hh = ly + 84, 140
    sx = x0 + w * (1 - pct / 100)
    B.text(labels[0], x0, ly, fsz(labels[0], sx - x0 - 40, 64, 40))
    B.keep()
    dr, pr = h.rect(x0, y0, w, hh); B.mark(dr, pr, "ink", 11)
    dh, ph = h.hatch(x0 + 8, y0 + 8, sx - x0 - 16, hh - 16, gap=24); B.mark(dh, ph, "ink", 5, dur=0.6, op=0.85, keepit=False)
    dl, pl = h.line(sx, y0 - 18, sx, y0 + hh + 18, over=2); B.mark(dl, pl, "ink", 11)
    ay = y0 + hh + 46
    da_, pa_ = h.line(x0, ay, x0 + w, ay, over=4); B.mark(da_, pa_, "ink", 6)
    tk = []
    for k in range(11):
        xx = x0 + w * k / 10; ln = 26 if k in (0, 5, 10) else 14
        tk.append((xx + h.j(1.5), ay, xx + h.j(1.5), ay - ln))
    tpts = [q for x1, y1, x2, y2 in tk for q in ((x1, y1), (x2, y2))]
    B.mark(" ".join(f"M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" for x1, y1, x2, y2 in tk), tpts, "ink", 5, dur=0.2)
    fl = B.fill(sx + 10, y0 + 10, x0 + w - sx - 20, hh - 20, colour="red", at=tp - 0.4)
    B.keep(False)
    for k, lab in ((0, "0"), (5, "50"), (10, "100")):
        B.text(lab, x0 + w * k / 10, ay + 12, 40, cls="num", anchor="middle" if k == 5 else ("start" if k == 0 else "end"), dur=0.12, lag=0.0)
    B.text(labels[1], x0 + w - 4, ly - 46, fsz(labels[1], max(160, x0 + w - sx + 120), 92, 60), cls="hd1", anchor="end", colour="accent", lag=-0.1)
    mid = sx + (x0 + w - sx) / 2
    de, pe = h.ellipse(mid, y0 + hh / 2, (x0 + w - sx) / 2 + 36, hh / 2 + 30, over=0.35); B.mark(de, pe, "red", 8)
    if P:
        nb = ay + 80
        if b.get("note"):
            nl = B.para(b["note"], g["x0"], ay + 76, 36, g["w"], mn=32, colour="muted")
            nb = nl[-1]["base"] + 40 if nl else nb
        bg = big(B, bigs, g["x0"] - 6, nb, g["w"] * 0.86, 440, 320, anchor="start", dur=0.55)
        da, pa = h.arrow(bg["left"] + bg["w"] + 10, bg["top"] + bg["px"] * 0.35, mid + 10, y0 + hh + 60, curve=0.3)
    else:
        bg = big(B, bigs, sx - 80, ay + 40, w * 0.42, 320, 280, anchor="end", dur=0.55)
        da, pa = h.arrow(bg["left"] + bg["w"] + 20, bg["top"] + bg["px"] * 0.45, mid, y0 + hh + 60, curve=0.3)
    B.mark(da, pa, "blue", 8)
    if b.get("note"):
        if P: pass
        else: B.para(b["note"], g["x0"], ay + 70, 34, bg["left"] - g["x0"] - 60, mn=30, colour="muted")
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(fl["t"], "brush"); X.sfx(bg["op"]["t"], "write")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.18), (fl["t"] - 0.3, 1.14, 0.8, 0.42 if P else 0.5), (bg["op"]["t"] + 0.3, 1.08, 0.4, 0.62), (t + d - 0.9, 1.0, 0.5, 0.5)])


def _qsmall(h, cx, cy, s, colour):
    q = h.qmark(cx, cy, s)
    return (q[0], q[1], colour, 7)


def question(b, X, t, d, cid):
    """the figure as a headline, a huge red question mark, arrows out to the candidate answers, each circled."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    hd_, cands = b.get("head", ""), (fit.as_list(b.get("options")) or ["?"])[:4]
    tq = T(X, b, "at_q", t, t + 1.4)
    n = len(cands)
    if P:
        hl_ = head(B, hd_, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        top = (hl_[-1]["base"] + 60) if hl_ else g["m0"]
        qs = 230; qx, qy = g["cx"], top + qs * 0.98      # 9:16: question mark + answers end above the caption (1420)
    else:
        hl_ = head(B, hd_, g["x0"], g["hy"], g["w"] * 0.9, 160, 120, 1, at=t + 0.1)
        top = (hl_[-1]["base"] + 50) if hl_ else g["m0"]
        qs = 290; qx, qy = g["x0"] + 300, top + qs * 0.98
    B.keep()
    q = h.qmark(qx, qy, qs); qo = B.mark(*q, "red", 22, at=tq - 0.45, dur=0.6)
    out = []
    for k, c in enumerate(cands):
        if P:
            cy = qy + qs * 0.75 + 100 + (k // 2) * 170
            cx = g["x0"] + g["w"] * ((k % 2) * 0.5 + 0.25) if n > 1 else g["cx"]
            px = fsz(c, g["w"] / min(n, 2) - 110, 110, 60)
            sx, sy, ex, ey = qx + (-50 if k % 2 == 0 else 50), qy + qs * 0.62, cx, cy - 26
            anc = "middle"
        else:
            cx, cy = g["x0"] + g["w"] * 0.52, top + 60 + k * (min(230, 520 / max(n - 1, 1)) if n > 1 else 0)
            px = fsz(c, g["w"] * 0.42, 120, 60)
            sx, sy, ex, ey = qx + qs * 0.55, qy - qs * 0.4 + k * 60, cx - 60, cy + px * 0.55
            anc = "start"
        da, pa = h.arrow(sx, sy, ex, ey, curve=0.22); B.mark(da, pa, "blue", 8)
        ct = B.text(c, cx, cy, px, cls="hd1", anchor=anc)
        B.hl(ct["left"] - 10, ct["left"] + ct["w"] + 10, ct["mid"] + 8, ct["gh"] * 0.62, lag=-0.25)
        de, pe = h.ellipse(ct["left"] + ct["w"] / 2, ct["mid"], ct["w"] / 2 + 44, ct["gh"] * 0.98, over=0.25); B.mark(de, pe, "ink", 8)
        out.append(ct)
    B.keep(False)
    # little question marks around the big one: the doubt, scribbled
    sm = [(-0.92, -0.55, 0.32, "blue"), (0.95, -0.35, 0.26, "ink"), (-0.75, 0.3, 0.22, "ink"), (0.82, 0.38, 0.3, "blue")] if P else \
         [(-0.85, -0.6, 0.28, "blue"), (0.85, -0.2, 0.22, "ink"), (-0.7, 0.35, 0.2, "ink")]
    for fx_, fy_, ss, col in sm:
        B.mark(*_qsmall(h, qx + fx_ * qs * 1.25, qy + fy_ * qs, qs * ss, col)[:2], col, 7, dur=0.18, lag=0.0)
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(qo["t"], "brush")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.16), (qo["t"] - 0.2, 1.12, 0.5, 0.42 if P else 0.5), (qo["t"] + 0.9, 1.06, 0.5, 0.62), (t + d - 0.9, 1.0, 0.5, 0.5)])


def ratio(b, X, t, d, cid):
    """two quantities as two drawn bars: the whole (outlined, hatched) and the one that matters (white paint fill), a red
    guide where the shorter one stops, the share in white paint marker. For "X is about 2/3 of Y"."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    total, part = float(b.get("total", 100)), float(b.get("part", 50))
    tl_, pl_ = b.get("total_label", ""), b.get("part_label", "")
    frac = max(0.06, min(1.0, part / total))
    tpart, tfrac = T(X, b, "at_part", t, t + 1.0), T(X, b, "at_frac", t, t + 2.2)
    ttot = T(X, b, "at_total", t, None)
    if P:
        hl_ = head(B, b.get("head") or pl_, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        x0, w, hh = g["x0"], g["w"], 130
        y2 = (hl_[-1]["base"] + 60) if hl_ else g["m0"]
        y1 = y2 + hh + 120
    else:
        hl_ = head(B, b.get("head") or pl_, g["x0"], g["hy"], g["w"], 160, 120, 1, at=t + 0.1)
        x0, w, hh = g["x0"], g["w"] * 0.5, 130
        y2 = (hl_[-1]["base"] + 70) if hl_ else g["m0"]
        y1 = y2 + hh + 110
    xs = x0 + w * frac
    B.keep()
    d2, p2 = h.rect(x0, y2, xs - x0, hh); B.mark(d2, p2, "ink", 11)
    fl = B.fill(x0 + 10, y2 + 10, xs - x0 - 20, hh - 20, at=tpart - 0.15)
    B.keep(False)
    B.text(tl_, x0, y1 - 74, fsz(tl_, w, 56, 40), at=(ttot - 0.2) if ttot is not None else None)
    B.keep()
    dr, pr = h.rect(x0, y1, w, hh); B.mark(dr, pr, "ink", 11)
    dh, ph = h.hatch(x0 + 8, y1 + 8, w - 16, hh - 16, gap=24); B.mark(dh, ph, "ink", 5, op=0.8, dur=0.45, keepit=False)
    dg, pg = h.line(xs, y2 - 30, xs, y1 + hh + 30, over=2); B.mark(dg, pg, "red", 8)
    B.keep(False)
    fl_ = b.get("frac_label", f"{frac * 100:.1f}%")
    if P:
        ft_ = big(B, fl_, g["x0"] - 6, y1 + hh + 70, g["w"] * 0.9, 440, 320, anchor="start", at=tfrac - 0.3, dur=0.5)
        da, pa = h.arrow(xs + 30, ft_["top"] + ft_["px"] * 0.3, xs + 6, y1 + hh + 36, curve=0.3); B.mark(da, pa, "red", 7)
        if b.get("frac_note"):
            room = g["x1"] - xs - 40
            fpx = fsz(b["frac_note"], room, 84, 52)
            fn = B.text(b["frac_note"], xs + 34, y2 + hh / 2 - fpx * 0.62, fpx, cls="hd1", colour="accent")
    else:
        ft_ = big(B, fl_, x0 + w + 70, y2 - 20, g["x1"] - x0 - w - 90, 340, 280, anchor="start", at=tfrac - 0.3, dur=0.5)
        da, pa = h.arrow(ft_["left"] - 20, ft_["top"] + ft_["px"] * 0.7, xs + 20, y2 + hh / 2, curve=0.3); B.mark(da, pa, "red", 7)
        if b.get("frac_note"):
            fn = B.text(b["frac_note"], ft_["left"] + 10, ft_["ul"] + 30, 88, cls="hd1")
            B.hl(fn["left"] - 12, fn["left"] + fn["w"] + 12, fn["mid"] + 6, fn["gh"] * 0.7, lag=-0.25)
        B.doodle(_icon(h, b.get("icon", "card"), g["x1"] - 300, ft_["ul"] + 120, 280), speed=2.4)
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(fl["t"], "brush"); X.sfx(ft_["op"]["t"], "pop")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.16), (fl["t"] - 0.3, 1.1, 0.4, 0.36), (ft_["op"]["t"] - 0.1, 1.08, 0.45, 0.6), (t + d - 0.9, 1.0, 0.5, 0.5)])


def tag(b, X, t, d, cid):
    """a price tag tied to a doodled member card: the old price is scribbled out in red, the new one written big beside it."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    old, new, date, sub = str(b.get("old", "")), str(b.get("new", "")), b.get("date", ""), b.get("sub", "")
    to = T(X, b, "at_new", t, t + 1.6)
    if P:
        hl_ = head(B, b.get("head", ""), g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        top = (hl_[-1]["base"] + 70) if hl_ else g["m0"]
        cx, cy, cw, ch = g["x0"] + 10, top, 620, 320          # 9:16: card + tag a little shorter so the new price clears the caption
        tx_, ty_, tw_, th_ = g["x0"] + 300, top + 250, 640, 220
    else:
        hl_ = head(B, b.get("head", ""), g["x0"], g["hy"], g["w"] * 0.9, 160, 120, 1, at=t + 0.1)
        top = (hl_[-1]["base"] + 60) if hl_ else g["m0"]
        cx, cy, cw, ch = g["x0"], top, 620, 370
        tx_, ty_, tw_, th_ = g["x0"] + 700, top + 40, 560, 230
    B.keep()
    B.doodle(card(h, cx, cy, cw, ch), speed=2.4)
    B.keep(False)
    B.text(b.get("card_text", "MEMBER"), cx + cw * 0.32, cy + ch * 0.42, int(ch * 0.17), cls="lat")
    if P: da, pa = h.arrow(cx + cw * 0.12, cy + ch + 10, tx_ - 10, ty_ + th_ * 0.62, curve=0.35)
    else: da, pa = h.arrow(cx + cw + 16, cy + ch * 0.35, tx_ - 16, ty_ + th_ * 0.45, curve=0.3)
    B.mark(da, pa, "blue", 7)
    B.keep()
    B.doodle(tagd(h, tx_, ty_, tw_, th_), speed=2.4)
    B.keep(False)
    B.fill(tx_ + th_ * 0.5, ty_ + 14, tw_ - th_ * 0.5 - 14, th_ - 28)
    o = B.text(old, tx_ + th_ * 0.62, ty_ + th_ * 0.12, int(th_ * 0.62), cls="num")
    dk, pk = h.strike(o["left"], o["left"] + o["w"], o["mid"], h=o["gh"] * 0.6); sk = B.mark(dk, pk, "red", 14, at=to - 0.55, dur=0.3)
    if P:
        sl = B.para(sub, g["x0"], ty_ + th_ + 34, 40, g["w"] - 40, mn=34, colour="muted")
        ny_ = (sl[-1]["base"] + 10) if sl else ty_ + th_ + 40
        n = big(B, new, g["x1"] - 10, ny_, g["w"] * 0.62, 440, 340, anchor="end", rot=-5, dur=0.45)
        if date:
            dt = B.text(date, g["x0"], n["mid"] - 40, 64, cls="hd1", colour="blue-ink")
            da2, pa2 = h.arrow(dt["left"] + dt["w"] + 14, dt["mid"], n["left"] - 10, n["mid"], curve=0.18); B.mark(da2, pa2, "blue", 7)
    else:
        n = big(B, new, tx_ + tw_ + 40, ty_ - 40, g["x1"] - tx_ - tw_ - 20, 380, 300, anchor="start", rot=-5, dur=0.45)
        if date: B.text(date, tx_ + 40, ty_ + th_ + 30, 60, cls="hd1", colour="blue-ink")
        B.para(sub, g["x0"], cy + ch + 90, 40, g["w"] * 0.8, mn=32, colour="muted")
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(sk["t"], "hit"); X.sfx(n["op"]["t"], "write")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.2), (sk["t"] - 0.3, 1.12, 0.6, 0.45), (n["op"]["t"] + 0.5, 1.08, 0.6, 0.62), (t + d - 0.9, 1.0, 0.5, 0.5)])


def dots(b, X, t, d, cid):
    """a 10×10 crowd of circles drawn row by row; the share that matters gets filled in blue, the rest ringed red;
    the figure is written across the grid in white paint marker."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    pct = max(0.0, min(100.0, float(b.get("pct", 50)))); n_on = int(round(pct))
    bigs = str(b.get("big", f"{pct:g}%")); label = b.get("label", "")
    tp = T(X, b, "at_pct", t, t + 1.6)
    cols = 10
    if P:
        hl_ = head(B, b.get("head", ""), g["x0"], g["hy"], g["w"], 200, 150, 1, at=t + 0.1)
        gy = (hl_[-1]["base"] + 60) if hl_ else g["m0"]
        cell = min(90, (g["m1"] - 90 - gy) / 10); gx = g["cx"] - 5 * cell
    else:
        hl_ = head(B, b.get("head", ""), g["x0"], g["hy"], g["w"] * 0.45, 160, 120, 2, at=t + 0.1)
        cell = 66; gx, gy = g["x0"] + g["w"] - 10 * cell, g["hy"] + 10
    rings, fill_c = [], []
    B.keep()
    for i in range(100):
        r_, c_ = divmod(i, cols)
        cx, cy = gx + c_ * cell + cell / 2 + h.j(2), gy + r_ * cell + cell / 2 + h.j(2)
        dd, pp = h.ellipse(cx, cy, cell * 0.33, cell * 0.33, n=10, over=0.25)
        rings.append((dd, pp, i >= n_on))
        if i < n_on: fill_c.append((cx, cy))
    for row in range(10):
        seg = rings[row * cols:(row + 1) * cols]
        p = [q for _, ps, _ in (seg if row % 2 == 0 else seg[::-1]) for q in ps[:1]]
        B.mark(" ".join(dd for dd, _, off in seg if not off), p, "ink", 6, dur=0.12, lag=0.0, at=t + 0.12 if row == 0 else None, layer="under", keepit=True)
        offs = [dd for dd, _, off in seg if off]
        if offs: B.mark(" ".join(offs), p, "red", 7, dur=0.08, lag=0.0, layer="under", keepit=True)
    B.keep(False)
    fid = f"{cid}fd"
    dots_html = "".join(f'<circle class="solid {fid}" cx="{x:.0f}" cy="{y:.0f}" r="{cell * 0.25:.0f}" style="fill:var(--blue)"/>' for x, y in fill_c)
    each = max(0.004, min(0.012, 0.8 / max(n_on, 1)))
    fill = B.custom(0.25 + each * n_on, lambda t0, du: X.tw(f'tl.from(".{fid}", {{scale:0, transformOrigin:"50% 50%", duration:0.22, ease:"back.out(2.5)", stagger:{{each:{each * du / (0.25 + each * n_on):.4f}}}}}, {t0:.3f});'),
                    at=tp - 0.95) if fill_c else None
    if P:
        nt = big(B, bigs, g["cx"], gy + cell * 2.6, g["w"], 440, 340, at=tp - 0.3, dur=0.5, rot=-6)
        if label: B.para(label, g["x0"], gy + 10 * cell + 26, 44, g["w"], mn=36)
    else:
        nt = big(B, bigs, g["x0"], g["hy"] + 330, gx - g["x0"] - 40, 360, 280, anchor="start", at=tp - 0.3, dur=0.5)
        if label: B.para(label, g["x0"], nt["ul"] + 40, 44, gx - g["x0"] - 60, mn=34)
    if b.get("note"): B.text(b["note"], gx, gy + 10 * cell + 90, 32, colour="muted")
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d, extra_under=dots_html)
    X.sfx(nt["op"]["t"], "write")
    if fill: X.sfx(fill["t"], "pop")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.16), (nt["op"]["t"] - 0.3, 1.08, 0.5, 0.42), (t + d - 0.9, 1.0, 0.5, 0.5)])


def loop(b, X, t, d, cid):
    """3–6 stations on a hand-drawn loop of arrows; once it is closed, a red dot runs the lap."""
    B = Board(X, cid, t, d, tail=1.0); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    st = (fit.as_list(b.get("stations")) or ["A", "B", "C"])[:6]
    n = max(3, len(st))
    title = b.get("head") or b.get("title", "")
    if P:
        hl_ = head(B, title, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1)
        top = (hl_[-1]["base"] + 40) if hl_ else g["m0"]
        cx, cy = g["cx"], (top + g["m1"]) / 2 + 10
        rx, ry = 380, min(330, (g["m1"] - top) / 2 - 110)
        lw = 460
    else:
        hl_ = head(B, title, g["x0"], g["hy"], g["w"] * 0.4, 150, 110, 2, at=t + 0.1)
        cx, cy = g["x0"] + g["w"] * 0.68, 600
        rx, ry = 440, 230
        lw = 400
    A0 = -math.pi / 2 - math.pi / n
    pos = [(cx + rx * math.cos(A0 + 2 * math.pi * k / n), cy + ry * math.sin(A0 + 2 * math.pi * k / n)) for k in range(n)]
    labels = []
    for k, (x, y) in enumerate(pos):
        px = fsz(st[k], lw, 66, 40)
        wdt = text_em(st[k]) * px
        left = max(g["x0"], min(g["x1"] - wdt, x - wdt / 2))
        ly_ = y - px * 1.45 if y < cy - 1 else (y + px * 0.25 if y > cy + 1 else y - px * 0.62)
        lt = B.text(st[k], left, ly_, px, cls="hd1")
        B.hl(lt["left"] - 10, lt["left"] + lt["w"] + 10, lt["mid"] + 6, lt["gh"] * 0.66, lag=-0.25)
        labels.append(lt)
        a0 = A0 + 2 * math.pi * k / n; a1 = A0 + 2 * math.pi * (k + 1) / n
        off = math.pi / n * 0.5
        s = (cx + rx * math.cos(a0 + off), cy + ry * math.sin(a0 + off)); e = (cx + rx * math.cos(a1 - off), cy + ry * math.sin(a1 - off))
        B.keep()
        da, pa = h.arrow(s[0], s[1], e[0], e[1], curve=0.22, head=34); B.mark(da, pa, "blue", 10)
        B.keep(False)
    for k in fit.as_list(b.get("hl")) or []:
        try: k = int(k)
        except (TypeError, ValueError): continue
        if 0 <= k < len(labels):
            lt = labels[k]
            de, pe = h.ellipse(lt["left"] + lt["w"] / 2, lt["mid"], lt["w"] / 2 + 40, lt["gh"] * 1.05, over=0.35); B.mark(de, pe, "red", 8)
    if b.get("center"):
        ct = B.text(b["center"], cx, cy - 46, fsz(b["center"], rx * 0.9, 80, 34), anchor="middle", colour="accent")
        de, pe = h.ellipse(cx, ct["mid"], ct["w"] / 2 + 36, ct["gh"] * 1.0, over=0.35); B.mark(de, pe, "red", 5)
    else:   # the engine in the middle: a doodled coin (money keeps going round)
        B.doodle(coin(h, cx, cy, min(rx, ry) * 0.32), speed=2.4)
    tr.draw(B)
    dot = '<g class="lapdot" style="opacity:0"><circle class="solid" cx="0" cy="0" r="20" style="fill:var(--red)"/></g>'
    finish(X, b, B, tr, cid, t, d, extra_over=dot)
    lap0 = B.end + 0.05
    if lap0 < t + d - 0.6:
        lap = min(2.2, max(0.6, t + d - lap0 - 0.3)); m = 32
        X.tw(f'tl.set("#{cid} .lapdot", {{x:{cx + rx * math.cos(A0):.0f}, y:{cy + ry * math.sin(A0):.0f}}}, {t:.3f});')
        X.tw(f'tl.to("#{cid} .lapdot", {{opacity:1, duration:0.15}}, {lap0:.3f});')
        for k in range(1, m + 1):
            a = A0 + 2 * math.pi * k / m
            X.tw(f'tl.to("#{cid} .lapdot", {{x:{cx + rx * math.cos(a):.0f}, y:{cy + ry * math.sin(a):.0f}, duration:{lap / m:.3f}, ease:"none"}}, {lap0 + lap * (k - 1) / m:.3f});')
        X.tw(f'tl.to("#{cid} .lapdot", {{opacity:0, duration:0.2}}, {lap0 + lap:.3f});')
    X.sfx(t + 0.2, "brush")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.16), (t + 0.9, 1.06, 0.5, 0.5), (B.end, 1.0, 0.5, 0.5)])


def thesis(b, X, t, d, cid):
    """the judgment written out by hand: one word struck out in red, the other on a white swash and circled;
    the thing it is about doodled underneath."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    pre, no, yes = b.get("pre", ""), b.get("no", ""), b.get("yes", "")
    neg, pos_ = b.get("neg", "不是"), b.get("pos", "是")
    tn, ty = T(X, b, "at_no", t, t + 1.2), T(X, b, "at_yes", t, t + 2.2)
    if P:
        hl_ = head(B, pre, g["x0"], g["hy"], g["w"], 200, 150, 2, at=t + 0.1, ul=None)
        y2 = (hl_[-1]["base"] + 60) if hl_ else g["m0"]
        bigp, y3 = 210, y2 + 290
    else:
        hl_ = head(B, pre, g["x0"], g["hy"], g["w"] * 0.9, 160, 120, 1, at=t + 0.1, ul=None)
        y2 = (hl_[-1]["base"] + 50) if hl_ else g["m0"]
        bigp, y3 = 190, y2 + 240
    x0 = g["x0"]
    a = B.text(neg, x0, y2 + bigp * 0.3, int(bigp * 0.5), cls="hd1")
    nw_ = g["w"] - a["w"] - 60
    nn = B.text(no, a["left"] + a["w"] + 40, y2, fsz(no, nw_ * (0.8 if P else 0.5), bigp, 80), cls="hd1", at=tn - 0.45)
    dk, pk = h.strike(nn["left"], nn["left"] + nn["w"], nn["mid"], h=nn["gh"] * 0.45); sk = B.mark(dk, pk, "red", 16, dur=0.3, lag=0.08)
    c = B.text(pos_, x0, y3 + bigp * 0.3, int(bigp * 0.5), cls="hd1")
    ypx = fsz(yes, nw_ * (0.9 if P else 0.55), int(bigp * 1.05), 80)
    yl = c["left"] + c["w"] + 56
    vt, vb = vbox(yes)
    hl = B.hl(yl - 14, yl + text_em(yes) * ypx + 14, y3 + ypx * (vt + (vb - vt) * 0.6), ypx * (vb - vt) * 0.66, at=ty - 0.4)
    yy = B.text(yes, yl, y3, ypx, cls="hd1", lag=-0.15)
    de, pe = h.ellipse(yy["left"] + yy["w"] / 2, yy["mid"], yy["w"] / 2 + 50, yy["gh"] * 0.92, over=0.4); B.mark(de, pe, "red", 10)
    for k in range(3):
        sx = min(yy["left"] + yy["w"] + 72, X.W - 70); sy = yy["top"] + yy["px"] * (0.15 + 0.38 * k)
        dd, pp = h.line(sx, sy, sx + 46, sy + (-24, 0, 24)[k], over=1); B.mark(dd, pp, "ink", 8, dur=0.08, lag=0.0)
    if P:
        top = yy["base"] + 90
        B.keep(); B.doodle(card(h, g["x0"] + 10, top, 600, min(360, g["m1"] - top)), speed=2.4); B.keep(False)
        B.text(b.get("card_text", "MEMBER"), g["x0"] + 10 + 600 * 0.32, top + min(360, g["m1"] - top) * 0.42, 58, cls="lat")
    else:
        B.keep(); B.doodle(card(h, g["x0"] + g["w"] * 0.56, y3 - 20, 460, 280), speed=2.4); B.keep(False)
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d)
    X.sfx(sk["t"], "hit"); X.sfx(hl["t"], "brush")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.12, 0.3, 0.16), (nn["op"]["t"] - 0.2, 1.1, 0.4, 0.34), (hl["t"] - 0.2, 1.08, 0.45, 0.5), (t + d - 0.9, 1.0, 0.5, 0.5)])


def outro(b, X, t, d, cid):
    """a white card taped to the kraft; the top hat is drawn above the channel name. The ruler below holds the whole talk."""
    B = Board(X, cid, t, d); h = B.h; P = X.portrait; g = geo(X)
    tr = Trail(X, b, cid, t)
    title, sub = b.get("title", X.channel), b.get("sub", "")
    nw, nh = (900, 1040) if P else (1320, 640)
    nx_, ny_ = (g["cx"] - nw / 2, g["hy"] + 40) if P else (g["x0"] + 80, g["hy"] + 30)
    note = (f'<div class="card sn" style="left:{nx_:.0f}px; top:{ny_:.0f}px; width:{nw}px; height:{nh}px; transform:rotate(-2deg)"></div>'
            f'<div class="tape tp" style="left:{nx_ + nw / 2 - 110:.0f}px; top:{ny_ - 26:.0f}px; width:220px; height:54px; transform:rotate(3deg)"></div>')
    X.tw(f'tl.from("#{cid} .sn", {{y:-90, rotation:-9, opacity:0, duration:0.45, ease:"back.out(1.6)"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("#{cid} .tp", {{scaleX:0, opacity:0, duration:0.22, ease:"power2.out"}}, {t + 0.38:.3f});')
    B.keep()
    if P: hx, hy_, hs = nx_ + nw / 2, ny_ + 500, 600
    else: hx, hy_, hs = nx_ + 340, ny_ + 520, 560
    B.doodle(tophat(h, hx, hy_, hs), at=t + 0.45, speed=3.0)
    B.keep(False)
    if P: lines = head(B, title, nx_ + nw / 2, hy_ + 130, nw * 0.88, 200, 150, 1, anchor="middle")
    else: lines = head(B, title, nx_ + 700, ny_ + 150, 560, 180, 140, 1)
    sx_ = nx_ + nw / 2 if P else nx_ + 700
    B.para(sub, sx_, (lines[-1]["base"] + 70) if lines else ny_ + 900, 56, nw * 0.86 if P else 560, mn=44, anchor="middle" if P else "start", colour="muted")
    tr.draw(B)
    finish(X, b, B, tr, cid, t, d, extra_html=note)
    X.sfx(t + 0.1, "title"); X.sfx(t + 0.38, "tape")
    shots(X, f"#{cid} .cam", t, d, [(t, 1.08, 0.5, 0.35), (t + d * 0.45, 1.0, 0.5, 0.5)])


SCENES = {"hook": hook, "bar": bar, "question": question, "ratio": ratio, "tag": tag, "dots": dots, "loop": loop, "thesis": thesis, "outro": outro}
