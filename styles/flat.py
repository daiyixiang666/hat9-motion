"""flat · 扁平插画风 —— 招贴画式的讲解片：Charley Harper / Mary Blair / 当代扁平海报一路，严格五色、几何造型、45° 长投影。

只用五种颜色：奶油 #f6efe2、墨蓝 #17203d、番茄 #f0502f、芥黄 #f2b632、青绿 #1f8a80；除了天空的两段色带不用渐变；
整片 7% 颗粒，色块带 1–2 px 的套色错位（番茄色从右下角露出一线）。造型全是圆、半圆、矩形和 45° 斜切，没有细描边，
人物由 4–6 块形状拼成，脚下拖一条 45° 长投影。白天的场景铺奶油底，夜里的铺墨蓝底，每个画面一种颜色占一半以上。

竖屏按海报构图：一个 ≥ 800 px 的大主体横穿画面中部，标题写在画面里的墙、招牌、横幅上，
数字（300–480 px，芥黄或番茄）是画面里的东西——夜空里的月亮、招牌、包裹；最下面 25% 是前景层（路、柜台、人群），
一直铺到画面底边。字幕是奶油色斜切角色块、墨蓝字，靠左下。动效由形状带：形状滑入、旋转、互相揭开，
挤压回弹不超过 8%，远中近三层视差；场景之间一个色盘吞掉旧画面、新画面从同一点开圆。

场景（SCENES）：city 城市开场 · grow 包裹堆对比 · hero 骑手特写 · crowd 人群 · month 月度 · wallet 收入区间 ·
climb 增长公路 · network 城市路网 · outro 落版。横竖屏各自排版；包裹、小人、硬币、路牌、路线数量都按输入计算。
"""
import math, random
from h9 import fit as F

CREAM, NAVY, TOMATO, MUSTARD, TEAL = "#f6efe2", "#17203d", "#f0502f", "#f2b632", "#1f8a80"
INK = NAVY
PAL = [MUSTARD, TOMATO, TEAL]
SH = "rgba(23,32,61,.24)"          # the 45° long shadow: navy laid over the ground

STYLE = {
    "name": "扁平插画", "en": "Flat", "benchmarks": ["Charley Harper", "Mary Blair", "当代扁平招贴", "Tom Haugomat"],
    "tokens": {
        "bg": CREAM, "fg": NAVY, "muted": TEAL, "accent": TOMATO, "accent2": MUSTARD, "alert": TOMATO,
        "line": "rgba(23,32,61,.2)", "paper": CREAM, "ink": NAVY, "card": CREAM, "card-fg": NAVY,
        "coral": TOMATO, "sun": MUSTARD, "mint": TEAL, "lilac": TEAL, "sky": TEAL, "night": NAVY, "cream": CREAM,
        "navy": NAVY, "tomato": TOMATO, "mustard": MUSTARD, "teal": TEAL,
        "cap-bg": CREAM, "cap-fg": NAVY, "cap-size": "38px", "cap-weight": "800", "cap-pad": "14px 46px 16px 26px", "cap-radius": "0",
        "cap-shadow": "none", "cap-em": TOMATO, "cap-bottom": "64px", "punch-top": "70%", "punch-size": "68px",
        "mascot-bg": MUSTARD,
    },
    "fonts": {"display": ["alibaba-puhuiti-heavy", "noto-sans-sc"], "body": ["alibaba-puhuiti", "noto-sans-sc"], "num": ["archivo-black", "noto-sans-sc"],
              "hand": ["alibaba-puhuiti-heavy", "noto-sans-sc"]},
    "motion": {"ease": "back.out(1.4)", "dur": 0.6, "stagger": 0.04, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07})],
    "safe_exempt": [".fl .hd"],     # 9:16 page furniture (header / HUD / legend / scale bar) may sit under the platform chrome
    "mascot": {"mode": "none"},          # people are drawn in the scenes, in the palette; the stock host sticker stays out
    "sfx": {"transition": ("whoosh_soft", 0.35), "enter": ("whoosh_soft", 0.3), "pop": ("pop", 0.4), "hit": ("hit", 0.4), "boing": ("boing", 0.35),
            "count": ("type", 0.25), "click": ("click", 0.3), "mascot": ("whoosh_soft", 0.3), "slam": ("slam", 0.35), "cut": ("whoosh_soft", 0.3)},
}

CSS = r"""
.fl { position:absolute; inset:0; overflow:hidden; background:var(--cream); }
.fl.night { background:var(--navy); }
.fl .cam { position:absolute; inset:0; }
.fl .ui { position:absolute; inset:0; z-index:5; pointer-events:none; }
.fl svg.ill { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.fl .hd { position:absolute; left:80px; top:40px; display:flex; align-items:center; gap:14px; font-family:var(--f-display); font-size:28px; color:var(--navy); z-index:6; }
.fl .hd i { display:inline-block; width:30px; height:30px; background:var(--tomato); clip-path:polygon(0 0, 100% 0, 100% 100%); }
.fl .hd span { font-family:var(--f-body); font-weight:700; opacity:.85; }
.fl.night .hd, .fl.dk .hd { color:var(--cream); }
.fl .ft { position:absolute; left:80px; right:80px; bottom:20px; font-family:var(--f-body); font-weight:700; font-size:28px; color:var(--cream); z-index:6; text-align:right; }
.fl .tx { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.18; white-space:nowrap; }
.fl .tx .em .emt { color:var(--emc, var(--tomato)); } .fl .tx .em .emb { display:none; }
.fl .tx .ln { display:block; overflow:hidden; padding:0 .04em .06em 0; } .fl .tx .ln > span { display:inline-block; }
.fl .num { position:absolute; font-family:var(--f-num); font-weight:400; line-height:1; letter-spacing:-.02em; white-space:nowrap; }
.fl .tag { position:absolute; font-family:var(--f-display); font-weight:900; white-space:nowrap; padding:10px 30px 12px 20px; clip-path:polygon(0 0, calc(100% - 22px) 0, 100% 22px, 100% 100%, 0 100%); }
#root.v .fl .hd { left:56px; top:150px; }
#root.v .fl .ft { left:56px; right:120px; bottom:400px; top:auto; text-align:left; font-size:28px; }
/* caption: a cream block with a 45° cut corner, navy text, bottom-left */
#root.st-flat .clip.cap { left:96px !important; right:auto !important; text-align:left !important; }
#root.st-flat .clip.cap .cp { font-family:var(--f-display); font-size:40px; font-weight:900; line-height:1.3; color:var(--navy); background:var(--cream);
  padding:14px 48px 16px 26px; border-radius:0; text-shadow:none; clip-path:polygon(0 0, calc(100% - 26px) 0, 100% 26px, 100% 100%, 0 100%); }
#root.st-flat .clip.cap .cp .em .emt { color:var(--tomato); }
#root.v.st-flat { --cap-bottom:480px; }   /* 9:16: caption above the source line, both above the platform's bottom bar */
#root.v.st-flat .clip.cap { left:56px !important; max-width:900px; }
.st-flat .mascot { display:none !important; }
"""


# ---------------------------------------------------------------- metrics
_NM = {}


def numem(s):
    """advance of a figure set in the number face (Archivo Black), in em; CJK falls back to 1 em."""
    if "m" not in _NM:
        _NM["m"] = None
        try:
            from fontTools.ttLib import TTFont
            from h9 import fonts
            f = TTFont(str(fonts.find(fonts.REG["archivo-black"]["file"])), lazy=True)
            _NM["m"] = (f.getBestCmap(), f["hmtx"].metrics, f["head"].unitsPerEm)
        except Exception:
            _NM["m"] = None
    m = _NM["m"]
    tot = 0.0
    for ch in F.plain(str(s)):
        if m and ord(ch) in m[0]: tot += m[1][m[0][ord(ch)]][0] / m[2] - 0.02
        else: tot += 1.0 if ord(ch) > 0x2e7f else 0.62
    return tot


def numpx(s, width, mx=480, mn=300):
    return int(max(mn, min(mx, width / max(numem(s), 0.5))))


# ---------------------------------------------------------------- the SVG kit: circles, half-circles, rectangles, 45° cuts
def rnd(seed): return random.Random(seed)


def defs(cid):
    """per-scene SVG defs: the misregistration filter (a tomato fringe 2 px down-right of every shape)."""
    return (f'<defs><filter id="{cid}mr" x="-2%" y="-2%" width="104%" height="104%"><feOffset in="SourceAlpha" dx="2" dy="1.5" result="o"/>'
            f'<feFlood flood-color="{TOMATO}" flood-opacity=".7"/><feComposite in2="o" operator="in" result="f"/>'
            f'<feMerge><feMergeNode in="f"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')


def ill(X, cid, body, cls="ill"):
    return f'<svg class="{cls}" viewBox="0 0 {X.W} {X.H}">{defs(cid)}<g filter="url(#{cid}mr)">{body}</g></svg>'


def R(x, y, w, h, c, cls="", extra=""):
    return f'<rect{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" fill="{c}"{extra}/>'


def C(x, y, r, c, cls=""):
    return f'<circle{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{c}"/>'


def half(x, y, r, c, up=True, cls=""):
    """a half-circle standing on (x, y) (up) or hanging from it."""
    s = 1 if up else 0
    return f'<path{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} d="M{x - r:.0f} {y:.0f} A{r:.0f} {r:.0f} 0 0 {s} {x + r:.0f} {y:.0f} Z" fill="{c}"/>'


def poly(pts, c, cls=""):
    return f'<path{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} d="M{" L".join(f"{x:.0f} {y:.0f}" for x, y in pts)} Z" fill="{c}"/>'


def cutrect(x, y, w, h, c, k=None, corner="tr", cls=""):
    """a rectangle with one corner cut at 45°."""
    k = k if k is not None else min(w, h) * 0.22
    pts = {"tr": [(x, y), (x + w - k, y), (x + w, y + k), (x + w, y + h), (x, y + h)],
           "tl": [(x + k, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y + k)],
           "br": [(x, y), (x + w, y), (x + w, y + h - k), (x + w - k, y + h), (x, y + h)],
           "bl": [(x, y), (x + w, y), (x + w, y + h), (x + k, y + h), (x, y + h - k)]}[corner]
    return poly(pts, c, cls)


def lshadow(x, y, w, h, L=None, c=SH):
    """the long 45° shadow of a box standing on the ground, falling down-right off its right face."""
    L = L if L is not None else h * 1.2
    return poly([(x + w, y), (x + w + L, y + L), (x + w + L, y + h + L * 0.0 + L), (x + L, y + h + L), (x, y + h)], c) if False else \
        poly([(x + w, y), (x + w + L, y + L), (x + w + L, y + h + L), (x + L, y + h + L), (x, y + h)], c)


def cast(inner, x, base, k=0.9):
    """a shadow cast on the ground at 45° (down-right) by everything in `inner` (drawn with its origin on the ground)."""
    return f'<g transform="matrix(1,0,{-k:.2f},{-k * 0.5:.2f},{x:.0f},{base:.0f})" class="shd">{inner}</g>'


def building(x, base, w, h, col, win, r, lit=0.5, roof=0, cls="bd"):
    """one flat building: body, a 45° roof cut or a flat cap, a grid of square windows (lit ones in `win`)."""
    s = [f'<g class="{cls}">']
    if roof == 1:
        s.append(cutrect(x, base - h, w, h + 4, col, k=min(w * 0.45, 70), corner="tr"))
    elif roof == 2:
        s.append(poly([(x, base - h), (x + w / 2, base - h - w / 2), (x + w, base - h), (x + w, base + 4), (x, base + 4)], col))
    else:
        s.append(R(x, base - h, w, h + 4, col))
    cols = max(1, int((w - 20) // 44)); rows = max(1, int((h - 50) // 54))
    gx = (w - cols * 24) / (cols + 1)
    for i in range(rows):
        for j in range(cols):
            on = r.random() < lit
            s.append(R(x + gx + j * (24 + gx), base - h + 36 + i * 54, 24, 30, win if on else NAVY, cls="wn" + (" on" if on else "")))
    s.append("</g>")
    return "".join(s)


def skyline(W, base, r, cols, win, hmin=200, hmax=480, x0=-40, x1=None, lit=0.5):
    s, x = [], x0
    while x < (x1 or W + 120):
        w = r.randint(110, 190); h = r.randint(hmin, hmax)
        s.append(building(x, base, w, h, r.choice(cols), win, r, lit=lit, roof=r.choice([0, 1, 1, 2])))
        x += w + r.randint(0, 14)
    return "".join(s)


def rider(k=1.0, jacket=TOMATO, box=MUSTARD, scoot=NAVY, flip=False, helmet=MUSTARD, skin=CREAM):
    """a courier on a scooter from circles, half-circles and 45° cuts. Origin = the ground under the scooter.
    Groups: .wh wheels, .pp rider + box (bobs), .bx box (squashes)."""
    body = (f'<g class="wh">{C(-70, -30, 30, NAVY)}{C(-70, -30, 12, CREAM)}</g><g class="wh">{C(78, -30, 30, NAVY)}{C(78, -30, 12, CREAM)}</g>'
            + poly([(-110, -40), (-110, -66), (40, -66), (70, -96), (92, -96), (100, -40)], scoot)
            + poly([(60, -96), (84, -170), (100, -170), (78, -96)], scoot)
            + R(84, -178, 44, 14, scoot)
            + f'<g class="pp"><g class="bx">{cutrect(-150, -176, 96, 96, box, k=22, corner="tl")}{R(-150, -140, 96, 16, NAVY)}</g>'
            + poly([(-46, -66), (-8, -66), (10, -150), (-28, -150)], NAVY)
            + cutrect(-44, -226, 70, 90, jacket, k=26, corner="tr")
            + poly([(14, -210), (88, -176), (80, -160), (8, -186)], jacket)
            + C(-8, -254, 30, skin) + half(-8, -256, 34, helmet) + R(-44, -260, 72, 9, helmet) + "</g>")
    sx = -k if flip else k
    return f'<g class="rider" transform="scale({sx},{k})">{body}</g>'


def rider_shadow(k=1.0, flip=False):
    """the rider's 45° ground shadow: the same silhouette sheared onto the road."""
    sil = (C(-70, -30, 30, SH) + C(78, -30, 30, SH) + R(-150, -176, 96, 96, SH) + R(-110, -96, 210, 56, SH)
           + R(-44, -226, 70, 160, SH) + C(-8, -254, 34, SH))
    sx = -k if flip else k
    return f'<g transform="scale({sx},{k})"><g transform="matrix(1,0,-0.9,-0.42,0,0)">{sil}</g></g>'


def person(x, y, k, body, helmet=MUSTARD, skin=CREAM, shadow=True, cls="pr"):
    """a figure from 4 shapes standing on (x, y): shoulders half-circle, neck block, head circle, helmet half-circle;
    plus its 45° shadow."""
    sh = ""
    if shadow:
        sh = f'<path d="M{-26:.0f} 0 L26 0 L{26 + 60:.0f} {30:.0f} L{-26 + 60:.0f} {30:.0f} Z" fill="{SH}"/>'
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})"><g class="{cls}">{sh}{half(0, 0, 30, body)}{R(-8, -40, 16, 14, skin)}'
            f'{C(0, -52, 17, skin)}{half(0, -54, 19, helmet)}</g></g>')


def parcel(x, base, s, col, cls, frac=1.0):
    """a box standing on (x, base) with a navy tape band and its 45° shadow; frac < 1 = a part-filled box."""
    h = s * frac
    return (f'<g transform="translate({x:.0f},{base:.0f})"><g class="{cls}">{poly([(s / 2, -h), (s / 2 + h * .5, -h * .5), (s / 2 + h * .5, 0), (s / 2, 0)], SH)}'
            f'{R(-s / 2, -h, s, h, col)}{R(-s * .09, -h, s * .18, h, NAVY)}</g></g>')


def coin(x, y, w, cls=""):
    """a coin seen from the side in a stack: a mustard bar with a navy rim line."""
    return f'<g class="{cls}" transform="translate({x:.0f},{y:.0f})">{R(-w / 2, -16, w, 16, MUSTARD)}{R(-w / 2, -4, w, 4, NAVY)}</g>'


def tree(x, base, k=1.0, col=TEAL, trunk=NAVY):
    return (f'<g transform="translate({x:.0f},{base:.0f}) scale({k:.2f})"><g class="tr">{R(-7, -50, 14, 50, trunk)}'
            f'{poly([(-46, -50), (0, -140), (46, -50)], col)}{poly([(-36, -100), (0, -172), (36, -100)], col)}</g></g>')


def road(X, y0, col=NAVY, kerb=TOMATO, dash=CREAM, lanes=(0.42, 0.8)):
    """the foreground road from y0 to the bottom edge: kerb, lane dashes in groups (.ld0, .ld1) that slide."""
    W, H = X.W, X.H
    h = H - y0
    out = [R(0, y0, W, h + 4, col), R(0, y0, W, 16, kerb)]
    for i, f in enumerate(lanes):
        yy = y0 + h * f
        out.append(f'<g class="ld ld{i}">' + "".join(R(x, yy, 90, 12, dash) for x in range(-360, W + 360, 180)) + "</g>")
    return "".join(out)


def road_go(X, s, t, d):
    X.tw(f'tl.fromTo("{s} .ld0", {{x:0}}, {{x:-360, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .ld1", {{x:0}}, {{x:-540, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def stars(W, H, r, n=26, y1=0.45):
    out = []
    for _ in range(n):
        x, y, s = r.uniform(0, W), r.uniform(H * 0.04, H * y1), r.uniform(4, 9)
        if r.random() < 0.6: out.append(C(x, y, s * 0.5, CREAM))
        else: out.append(R(x - s, y - 2, s * 2, 4, CREAM) + R(x - 2, y - s, 4, s * 2, CREAM))
    return f'<g class="stz">{"".join(out)}</g>'


# ---------------------------------------------------------------- layout + motion helpers
def L(X): return 56 if X.portrait else 96


def FG(X): return X.H * (0.75 if X.portrait else 0.8)


def title(X, text, left, top, box_w, box_h, max_px, min_px=40, lines=3, cls="tx", sty="", col=None, emc=None):
    """an adaptive headline block → (html, px, height)."""
    f = F.fit_text(text, box_w, box_h, max_px, min_px, lh=1.18, max_lines=lines)
    body = "".join(f'<span class="ln"><span>{X.rich(l)}</span></span>' for l in f.lines)
    c = f"color:{col};" if col else ""
    e = f"--emc:{emc};" if emc else ""
    return f'<div class="{cls}" style="left:{left:.0f}px; top:{top:.0f}px; font-size:{f.px}px; {c}{e}{sty}">{body}</div>', f.px, f.n * f.px * 1.18


def frame(X, b, cid, world, ui="", night=False, dk=False):
    """world = the illustration (inside the camera); ui = text that is fixed to the picture plane."""
    X.css("flat", CSS)
    meta = X.v.get("meta", {})
    src = b.get("src", "")
    X.used_text.update("来源：" + src + X.channel + meta.get("section", ""))
    hd = f'<div class="hd"><i></i><b>{X.rich(X.channel)}</b><span>{X.rich(meta.get("section", "生意图鉴"))}</span></div>'
    ft = f'<div class="ft">{"来源：" + X.rich(src) if src else ""}</div>'
    cls = "fl" + (" night" if night else "") + (" dk" if dk else "")
    return f'<div class="{cls}"><div class="cam">{world}</div><div class="ui">{ui}</div>{hd}{ft}</div>'


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def counter(X, sel, t, a, b, dur=1.0, dec=0, ease="power3.out", sep=False):
    if dec: js = f"o.v.toFixed({dec})"
    elif sep: js = "Math.round(o.v).toLocaleString('en-US')"
    else: js = "String(Math.round(o.v))"
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"{ease}", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def cam(X, sel, t, d, keys):
    """keys = [(time, scale, fx, fy)]: expo.inOut moves, a slow creep between, frame edges never show."""
    W, H = X.W, X.H
    def xy(sc, fx, fy):
        return min(0, max(W - sc * W, W / 2 - sc * fx * W)), min(0, max(H - sc * H, H / 2 - sc * fy * H))
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    keys = sorted(keys)
    for k, (tk, sc, fx, fy) in enumerate(keys):
        x, y = xy(sc, fx, fy); nxt = keys[k + 1][0] if k + 1 < len(keys) else t + d
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});'); h0 = tk
        else:
            mv = min(0.9, max(0.3, nxt - tk - 0.05))
            X.tw(f'tl.to("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"expo.inOut"}}, {tk:.3f});'); h0 = tk + mv
        if nxt - h0 > 0.25:
            x2, y2 = xy(sc * 1.02, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{sc * 1.02:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - h0:.2f}, ease:"none"}}, {h0:.3f});')


def spin(X, sel, t, d, rate=1.6):
    X.tw(f'tl.fromTo("{sel}", {{rotation:0, transformOrigin:"50% 50%"}}, {{rotation:{360 * d * rate:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def bob(X, sel, t, d, amp=6, per=0.42):
    n = max(1, int(d / per))
    X.tw(f'tl.fromTo("{sel}", {{y:0}}, {{y:{-amp}, duration:{per / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:{n * 2 - 1}}}, {t:.3f});')


def drop(X, sel, t, st=0.05, dur=0.5, h=260):
    """lands with a squash: falls in, squashes 8 % on contact, springs back (squash-and-stretch ≤ 8 %)."""
    a = dur * .5
    X.tw(f'tl.fromTo("{sel}", {{y:{-h}, scaleY:1.08, scaleX:.94, opacity:0, transformOrigin:"50% 100%"}}, {{y:0, scaleY:1, scaleX:1, opacity:1, duration:{a:.2f}, ease:"power2.in", stagger:{st:.3f}}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel}", {{scaleY:.92, scaleX:1.06, transformOrigin:"50% 100%"}}, {{scaleY:1, scaleX:1, duration:{dur * .6:.2f}, ease:"back.out(2)", stagger:{st:.3f}, immediateRender:false}}, {t + a:.3f});')


def rise(X, sel, t, st=0.05, dur=0.6):
    """buildings / signs grow up out of the ground with a small overshoot."""
    X.tw(f'tl.from("{sel}", {{scaleY:0, transformOrigin:"50% 100%", duration:{dur:.2f}, ease:"back.out(1.5)", stagger:{st:.3f}}}, {t:.3f});')


def lines_in(X, sel, t, st=0.08):
    X.tw(f'tl.from("{sel} .ln > span", {{yPercent:110, duration:0.55, ease:"back.out(1.4)", stagger:{st}}}, {t:.3f});')


def slide(X, sel, t, dx=0, dy=0, rot=0, dur=0.6, ease="expo.out"):
    X.tw(f'tl.from("{sel}", {{x:{dx}, y:{dy}, rotation:{rot}, duration:{dur:.2f}, ease:"{ease}"}}, {t:.3f});')


def swing(X, sel, t, origin="50% 0%"):
    """a sign swings down from its hinge and settles."""
    X.tw(f'tl.fromTo("{sel}", {{rotation:-90, transformOrigin:"{origin}"}}, {{rotation:0, duration:0.8, ease:"back.out(1.6)"}}, {t:.3f});')


SEAM = 0.32


def bubble(X, cid, t, fx=.5, fy=.5):
    """the style's seam: the new scene opens as a circle from its focal point over the old one, which keeps playing
    underneath (the scene clip starts SEAM s early, see put()); a palette ring rides the edge. No flat-colour frames."""
    if X.beat.get("i", 0) == 0: return
    W, H = X.W, X.H
    col = PAL[X.beat["i"] % len(PAL)]
    t0 = t - SEAM
    X.tw(f'tl.fromTo("#{cid} > .stage", {{clipPath:"circle(0% at {fx * 100:.0f}% {fy * 100:.0f}%)"}}, {{clipPath:"circle(120% at {fx * 100:.0f}% {fy * 100:.0f}%)", duration:{SEAM + 0.06:.2f}, ease:"power2.in"}}, {t0:.3f});')
    X.tw(f'tl.set("#{cid} > .stage", {{clipPath:"none"}}, {t + 0.08:.3f});')
    X.sfx(t0, "transition")


def put(X, cid, t, d, html):
    """a scene clip; after the first beat it starts SEAM s early, above the previous one, so the circle can open over it."""
    i = X.beat.get("i", 0)
    if i == 0 or t < SEAM + 0.05:
        X.clip(cid, t, d, html, "scene", 2); return
    X.clip(cid, t - SEAM, d + SEAM, html, "scene", min(3 + i, 20), track=1 + i % 2)


def numdiv(X, cls, s, x, y, px, col, anchor="start", extra="", final=None):
    """a figure in the number face; `final` = the text it will end on (a counter starts from s), used for the layout."""
    w = numem(final if final is not None else s) * px
    left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
    X.used_text.update(str(s))
    return f'<div class="num {cls}" style="left:{left:.0f}px; top:{y:.0f}px; font-size:{px}px; color:{col};{extra}">{X.rich(str(s))}</div>', left, w


# ---------------------------------------------------------------- scenes
def city(b, X, t, d, cid):
    """night city on navy: the year's figure hangs in the sky in mustard, the headline is a billboard on the tallest
    building, a courier crosses the road in front; three layers of parallax."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(b.get("seed", 7))
    base = FG(X)
    x0 = L(X)
    sky = R(0, 0, W, H * (0.5 if P else 0.45), NAVY) + R(0, H * (0.5 if P else 0.45), W, H, NAVY)
    moon = f'<g class="mo">{C(W - x0 - 70, H * (0.12 if P else 0.16), 64, MUSTARD)}{C(W - x0 - 40, H * (0.12 if P else 0.16) - 22, 56, NAVY)}</g>'
    if P:
        far = skyline(W, base - 260, r, [TEAL], MUSTARD, 120, 260, lit=0.25)
        bx, bw, bh = 120, 840, 300
        mid = (skyline(W, base, r, [TOMATO, TEAL], MUSTARD, 200, 340, lit=0.45)
               + building(bx, base, bw, bh, CREAM, MUSTARD, r, lit=0.0, cls="bd main"))
        bb = (bx + 30, base - bh - 280, bw - 60, 250)
    else:
        far = skyline(W, base - 220, r, [TEAL], MUSTARD, 120, 240, lit=0.25)
        bx, bw, bh = W * 0.6, 700, 330
        mid = (skyline(W, base, r, [TOMATO, TEAL], MUSTARD, 160, 300, lit=0.45)
               + building(bx, base, bw, bh, CREAM, MUSTARD, r, lit=0.0, cls="bd main"))
        bb = (bx + 20, base - bh - 250, bw - 40, 230)
    poles = R(bb[0] + bb[2] * 0.2, bb[1] + bb[3], 22, base - bh - bb[1] - bb[3], NAVY) + R(bb[0] + bb[2] * 0.8 - 22, bb[1] + bb[3], 22, base - bh - bb[1] - bb[3], NAVY)
    board = f'<g class="bb">{poles}{cutrect(*bb, MUSTARD, k=46, corner="tr")}{R(bb[0] + 16, bb[1] + 16, bb[2] - 32, bb[3] - 32, CREAM)}</g>'
    front = road(X, base) + f'<g transform="translate(0,{base + (H - base) * 0.62:.0f})"><g class="r1">{rider_shadow(0.95 if P else 0.8)}{rider(0.95 if P else 0.8)}</g></g>'
    world = ill(X, cid, sky + stars(W, H, r, 24, 0.3) + moon + f'<g class="far">{far}</g><g class="mid">{mid}{board}</g><g class="front">{front}</g>')
    th, px, hh = title(X, b.get("title", ""), bb[0] + 40, bb[1] + 34, bb[2] - 80, bb[3] - 60, 92 if P else 84, 40, 2, col=NAVY, cls="tx ttl")
    val = b.get("value", 0) or 0
    unit = b.get("unit", "")
    if P:
        npx = numpx(str(int(val)), W - 2 * x0, 480, 300)
        nd, nl, nw = numdiv(X, "n", "0", x0 - 6, 350, npx, MUSTARD, final=str(int(val)))
        ui = (f'<div class="tx kk" style="left:{x0}px; top:270px; font-size:44px; color:{CREAM}">{X.rich(b.get("kicker", ""))}</div>' + nd
              + f'<div class="tx un" style="right:{x0}px; top:{350 + npx * 0.86:.0f}px; font-size:104px; color:{CREAM}">{X.rich(unit)}</div>')
        tg = f'<div class="tag ping" style="right:{x0 + 20}px; top:{bb[1] + bb[3] + 30:.0f}px; font-size:34px; background:{TOMATO}; color:{CREAM}">{X.rich(b.get("ping", ""))}</div>'
    else:
        npx = numpx(str(int(val)), W * 0.44, 380, 280)
        nd, nl, nw = numdiv(X, "n", "0", x0 - 6, 230, npx, MUSTARD, final=str(int(val)))
        ui = (f'<div class="tx kk" style="left:{x0}px; top:150px; font-size:40px; color:{CREAM}">{X.rich(b.get("kicker", ""))}</div>' + nd
              + f'<div class="tx un" style="left:{x0 + numem(str(int(val))) * npx - 200:.0f}px; top:{230 + npx * 0.9:.0f}px; font-size:96px; color:{CREAM}">{X.rich(unit)}</div>')
        tg = f'<div class="tag ping" style="left:{bx + bw - 260:.0f}px; top:{bb[1] + bb[3] + 30:.0f}px; font-size:30px; background:{TOMATO}; color:{CREAM}">{X.rich(b.get("ping", ""))}</div>'
    X.used_text.update("0123456789")
    put(X, cid, t, d, frame(X, b, cid, world, th + ui + tg, night=True))
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + .8)
    rise(X, f"{s} .far .bd", t, 0.03, 0.6); rise(X, f"{s} .mid .bd", t + 0.15, 0.04, 0.6)
    swing(X, f"{s} .bb", t + 0.55)
    lines_in(X, f"{s} .ttl", t + 0.9)
    slide(X, f"{s} .mo", t + 0.1, dx=200, dur=0.8)
    for sel, dx in ((".far", -30), (".mid", -80), (".stz", -15)):
        X.tw(f'tl.to("{s} {sel}", {{x:{dx}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .r1", {{x:-300}}, {{x:{W + 300}, duration:{max(2.4, d * .85):.2f}, ease:"power1.inOut"}}, {t + .2:.3f});')
    spin(X, f"{s} .r1 .wh", t, d); bob(X, f"{s} .r1 .pp", t, d)
    road_go(X, s, t, d)
    X.tw(f'tl.from("{s} .n", {{yPercent:40, duration:0.4, ease:"expo.out"}}, {t + .02:.3f});')
    counter(X, f"{s} .n", max(t + .2, tn - .4), 0, float(val), dur=1.2, dec=int(b.get("dec", 0)))
    X.sfx(max(t + .2, tn - .4), "count")
    slide(X, f"{s} .kk, {s} .un", t + .3, dx=-60, dur=0.5)
    X.tw(f'tl.from("{s} .ping", {{scale:0, rotation:-20, transformOrigin:"0% 100%", duration:0.45, ease:"back.out(2.2)"}}, {t + 1.3:.3f});')
    X.sfx(t + 1.3, "pop")
    cam(X, f"{s} .cam", t, d, [(t, 1.06, .5, .7), (t + 1.2, 1.0, .5, .5)])


def grow(b, X, t, d, cid):
    """daylight on cream: two stacks of parcels (1 box = `per`) drop in with a squash, the gain hangs on a navy banner
    across the top, the growth figure in tomato between."""
    W, H, P = X.W, X.H, X.portrait
    A, B = b["a"], b["b"]
    va, vb, per = float(A["v"]), float(B["v"]), float(b.get("per", 500))
    cols = int(b.get("cols", 3))
    base = FG(X)
    x0 = L(X)
    s = 104 if P else 84
    gx = [W * .27, W * .73] if P else [W * .58, W * .82]
    step = s
    def stack(v, xc, col, tag):
        n_full = int(v // per + 1e-9); frac = v / per - n_full
        n = n_full + (1 if frac > .05 else 0)
        out = []
        for i in range(n):
            c, rw = i % cols, i // cols
            out.append(parcel(xc + (c - (cols - 1) / 2) * (s + 4), base - rw * step, s, col, f"pc {tag}", frac if i == n_full else 1.0))
        return "".join(out), math.ceil(n / cols)
    sa, ra = stack(va, gx[0], MUSTARD, "pa"); sb, rb = stack(vb, gx[1], TOMATO, "pb")
    sun = f'<g class="sun">{C(W - 40, H * (0.2 if P else 0.18), 230 if P else 200, MUSTARD)}</g>'
    if P:
        ban = (x0 - 70, 270, W - 2 * x0 + 140, 230)
    else:
        ban = (x0 - 70, 140, W * 0.5, 210)
    banner = f'<g class="ban">{cutrect(*ban, NAVY, k=60, corner="br")}{R(ban[0], ban[1] + ban[3] - 14, ban[2] - 60, 14, TEAL)}</g>'
    ground = R(0, base, W, H - base + 4, TEAL) + R(0, base, W, 14, NAVY)
    counter_ = "".join(R(x, base + (H - base) * .55, 120, 18, CREAM) for x in range(-200, W + 240, 240))
    world = ill(X, cid, R(0, 0, W, H, CREAM) + sun + banner + ground + f'<g class="belt">{counter_}</g>' + sa + sb)
    th, px, hh = title(X, b.get("title", ""), ban[0] + 70 + 20, ban[1] + 36, ban[2] - 200, ban[3] - 70, 92 if P else 80, 40, 2, col=CREAM, emc=MUSTARD, cls="tx ttl")
    unit = b.get("unit", "")
    def lab(xc, name, v, cls, rows):
        return (f'<div class="tag {cls}" style="left:{xc - 170:.0f}px; top:{base - rows * step - 84:.0f}px; font-size:{40 if P else 34}px; background:{CREAM}; color:{NAVY}">'
                f'{X.rich(name)} · {X.rich(F.fmt_num(v, zh=False))} {X.rich(unit)}</div>')
    badge = str(b.get("badge", ""))
    if P:
        bpx = int(min(480, (W - 2 * x0) / max(numem(badge), .5)))
        nd, _, _ = numdiv(X, "bdg", badge, W / 2, 540, bpx, TOMATO, anchor="middle")
    else:
        bpx = int(min(400, W * 0.42 / max(numem(badge), .5)))
        nd, _, _ = numdiv(X, "bdg", badge, x0, 420, bpx, TOMATO)
    legend = b.get("legend") or f"1 个包裹 = {F.fmt_num(per, zh=False)} {unit}"
    lg = f'<div class="tx lg" style="left:{x0}px; top:{(540 + bpx + 10) if P else 420 + bpx + 20:.0f}px; font-size:36px; color:{NAVY}">{X.rich(legend)}</div>'
    ui = th + nd + lg + lab(gx[0], A["name"], va, "la", ra) + lab(gx[1], B["name"], vb, "lb", rb)
    put(X, cid, t, d, frame(X, b, cid, world, ui))
    sel = f"#{cid}"
    tb = T(X, b, "at_b", t, t + d * .4)
    X.tw(f'tl.from("{sel} .ban", {{xPercent:-110, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    lines_in(X, f"{sel} .ttl", t + .3)
    X.tw(f'tl.from("{sel} .sun", {{y:300, duration:0.9, ease:"expo.out"}}, {t + .1:.3f});')
    drop(X, f"{sel} .pa", t + .15, st=min(.05, .8 / max(1, va / per)))
    drop(X, f"{sel} .pb", max(t + .5, tb - .7), st=min(.045, .9 / max(1, vb / per)))
    slide(X, f"{sel} .la", t + .5, dy=80, dur=.45); slide(X, f"{sel} .lb", tb + .1, dy=80, dur=.45)
    X.tw(f'tl.from("{sel} .bdg", {{scale:0, rotation:-12, transformOrigin:"50% 60%", duration:0.55, ease:"back.out(1.8)"}}, {tb + .35:.3f});')
    slide(X, f"{sel} .lg", t + .6, dx=-80, dur=.5)
    X.tw(f'tl.fromTo("{sel} .belt", {{x:0}}, {{x:-240, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.sfx(tb + .35, "boing"); X.sfx(t + .35, "pop"); X.sfx(max(t + .5, tb - .7) + .3, "pop")
    cam(X, f"{sel} .cam", t, d, [(t, 1.06, .5, .7), (tb - .4, 1.0, .5, .5)])


def hero(b, X, t, d, cid):
    """the courier up close on a teal field: a huge rider built from shapes skids in in front of a mustard half-sun,
    a long 45° shadow on the road; the headline is a road sign."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(11)
    base = FG(X)
    x0 = L(X)
    k = 2.5 if P else 2.0
    gx = W * (0.52 if P else 0.64)
    sun = f'<g class="sun">{half(gx, base, 440 if P else 360, MUSTARD)}</g>'
    streaks = "".join(R(r.uniform(-200, W), r.uniform(H * .45, base - 40), r.randint(160, 420), 14, CREAM) for _ in range(12))
    if P:
        sg = (x0 - 10, 340, W - 2 * x0 + 20, 300)
    else:
        sg = (x0, 150, W * 0.42, 280)
    sign = (f'<g class="sg">{R(sg[0] + 60, sg[1] + sg[3], 24, base - sg[1] - sg[3], NAVY)}'
            f'{cutrect(*sg, NAVY, k=60, corner="tr")}{R(sg[0] + 18, sg[1] + 18, sg[2] - 36, sg[3] - 36, TEAL)}{R(sg[0] + 30, sg[1] + 30, sg[2] - 60, sg[3] - 60, NAVY)}</g>')
    front = road(X, base) + f'<g transform="translate({gx:.0f},{base + 14:.0f})"><g class="hr">{rider_shadow(k)}{rider(k, jacket=TOMATO, box=MUSTARD)}</g></g>'
    world = ill(X, cid, R(0, 0, W, H, TEAL) + sun + f'<g class="sl">{streaks}</g>' + sign + front)
    th, px, hh = title(X, b.get("title", ""), sg[0] + 54, sg[1] + 50, sg[2] - 110, sg[3] - 90, 100 if P else 88, 44, 2, col=CREAM, emc=MUSTARD, cls="tx ttl")
    kick = f'<div class="tag kick" style="left:{sg[0] + 30:.0f}px; top:{sg[1] - 76:.0f}px; font-size:36px; background:{MUSTARD}; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>'
    put(X, cid, t, d, frame(X, b, cid, world, th + kick, dk=True))
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .sl", {{x:300}}, {{x:-700, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .sun", {{scale:0, transformOrigin:"50% 100%", duration:0.7, ease:"back.out(1.4)"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hr", {{x:-1300, duration:0.6, ease:"expo.out"}}, {t + .05:.3f});')
    X.tw(f'tl.fromTo("{s} .hr", {{skewX:-8}}, {{skewX:0, duration:0.5, ease:"back.out(2)", immediateRender:false}}, {t + .5:.3f});')
    spin(X, f"{s} .wh", t, d, 2.2); bob(X, f"{s} .pp", t + .6, d - .6, 8, .36)
    X.tw(f'tl.fromTo("{s} .bx", {{scaleY:1, scaleX:1, transformOrigin:"50% 100%"}}, {{scaleY:.92, scaleX:1.06, duration:0.12, yoyo:true, repeat:1, ease:"sine.inOut", immediateRender:false}}, {t + .55:.3f});')
    rise(X, f"{s} .sg", t + .1, dur=.55)
    lines_in(X, f"{s} .ttl", t + .45, .1)
    X.tw(f'tl.from("{s} .kick", {{scale:0, rotation:-10, transformOrigin:"0% 100%", duration:0.45, ease:"back.out(2.2)"}}, {t + .3:.3f});')
    road_go(X, s, t, d)
    X.sfx(t + .05, "enter"); X.sfx(t + .55, "slam")
    cam(X, f"{s} .cam", t, d, [(t, 1.06, .5, .8), (t + d * .4, 1.0, .5, .5)])


def crowd(b, X, t, d, cid):
    """a crowd of helmeted figures (1 figure = `per` units) fills the bottom of a cream poster to the edge, rows marching in;
    the figure in tomato above them, a wave runs through the crowd."""
    W, H, P = X.W, X.H, X.portrait
    nv, per = float(b["n"]), float(b.get("per", 5))
    n = max(1, min(600, round(nv / per)))
    r = rnd(23)
    x0 = L(X)
    if P:
        cols, cell = 13, W / 13
        y_top = 1010
        cap = (0, 1440, 760, 1640)          # keep the caption corner clear of heads
    else:
        cols, cell = 22, (W * 0.56) / 22
        y_top = 330
        cap = (0, 930, 900, 1080)
    figs, i, row = [], 0, 0
    while i < n:
        y = y_top + (row + 1) * cell * 0.92
        for c in range(cols):
            if i >= n: break
            x = (W - cols * cell if not P else 0) + (c + .5) * cell + (cell * .5 if row % 2 else 0) - (0 if P else 40)
            if cap[0] <= x <= cap[2] and cap[1] - cell * .6 <= y <= cap[3] + cell: continue
            if x > W - cell * .3: continue
            figs.append(person(x, y, cell / 64, [TEAL, TOMATO, NAVY][r.randrange(3)], helmet=[MUSTARD, CREAM, TOMATO][r.randrange(3)]))
            i += 1
        row += 1
    world = ill(X, cid, R(0, 0, W, H, CREAM) + f'<g class="crowd">{"".join(figs)}</g>')
    unit = b.get("unit", "")
    val = str(int(nv)) if float(nv).is_integer() else str(nv)
    if P:
        npx = numpx(val, W - 2 * x0 - 300, 480, 300)
        nd, nl, nw = numdiv(X, "n", "0", x0 - 8, 400, npx, TOMATO, final=val)
        ui = (f'<div class="tx kk" style="left:{x0}px; top:300px; font-size:46px; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>' + nd
              + f'<div class="tx un" style="left:{x0 + nw + 24:.0f}px; top:{400 + npx * .52:.0f}px; font-size:120px; color:{NAVY}">{X.rich(unit)}</div>'
              + f'<div class="tag sub" style="left:{x0}px; top:{400 + npx + 30:.0f}px; font-size:44px; background:{NAVY}; color:{CREAM}">{X.rich(b.get("sub", ""))}</div>')
    else:
        npx = numpx(val, W * 0.3, 400, 300)
        nd, nl, nw = numdiv(X, "n", "0", x0 - 8, 260, npx, TOMATO, final=val)
        ui = (f'<div class="tx kk" style="left:{x0}px; top:170px; font-size:42px; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>' + nd
              + f'<div class="tx un" style="left:{x0}px; top:{260 + npx + 10:.0f}px; font-size:100px; color:{NAVY}">{X.rich(unit)}</div>'
              + f'<div class="tag sub" style="left:{x0}px; top:{260 + npx + 150:.0f}px; font-size:38px; background:{NAVY}; color:{CREAM}">{X.rich(b.get("sub", ""))}</div>')
    legend = b.get("legend") or f"每个小人 = {F.fmt_num(per, zh=False)} {unit}"
    ui += f'<div class="tag lg" style="right:{max(x0, 120) if P else x0}px; top:{y_top - 70 if P else 170:.0f}px; font-size:34px; background:{MUSTARD}; color:{NAVY}">{X.rich(legend)}</div>'
    put(X, cid, t, d, frame(X, b, cid, world, ui))
    s = f"#{cid}"
    tn = T(X, b, "at_n", t, t + .5)
    t0 = t + .2
    amt = min(max(.6, tn + .3 - t0), d - 1.0)
    X.tw(f'tl.fromTo("{s} .pr", {{y:50, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"back.out(1.6)", stagger:{{each:{amt / max(n, 1):.4f}}}}}, {t0:.3f});')
    wv = t0 + amt + .3
    if t + d - wv > .6:
        X.tw(f'tl.to("{s} .pr", {{keyframes:[{{y:-12, duration:0.16, ease:"power2.out"}}, {{y:0, duration:0.3, ease:"back.out(2)"}}], stagger:{{each:{0.8 / max(n, 1):.4f}}}}}, {wv:.3f});')
    counter(X, f"{s} .n", t0, 0, nv, dur=amt + .3, dec=int(b.get("dec", 0)), ease="power2.inOut")
    X.sfx(t0, "count")
    slide(X, f"{s} .kk, {s} .un", t, dx=-60, dur=.5)
    X.tw(f'tl.from("{s} .sub, {s} .lg", {{scaleX:0, transformOrigin:"0% 50%", duration:0.45, ease:"expo.out", stagger:0.15}}, {t + .5:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.06, .5, .8), (tn + .5, 1.0, .5, .5)])


def month(b, X, t, d, cid):
    """night on navy: the monthly figure is cut out of a huge mustard moon; below, a tomato building whose 30 windows
    light up one a day carries the headline; headlights run along the teal road in front."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(17)
    base = FG(X)
    x0 = L(X)
    days = int(b.get("days", 30))
    if P:
        mx, my, mr = W / 2, 720, 380
        bx, bw, bt = 70, W - 140, 1020
    else:
        mx, my, mr = W * 0.74, 380, 300
        bx, bw, bt = 80, W * 0.48, 470
    moon = f'<g class="mo">{C(mx, my, mr, MUSTARD)}</g>'
    side = skyline(W, base, r, [TEAL], MUSTARD, 160, 300, lit=0.3)
    bh = base - bt
    bld = R(bx, bt, bw, bh + 4, TOMATO) + poly([(bx, bt), (bx + 70, bt - 70), (bx + bw - 70, bt - 70), (bx + bw, bt)], TOMATO)
    gc, gr = 10, 3
    cw = (bw - 60) / gc
    tiles = "".join(R(bx + 30 + (i % gc) * cw + 6, bt + bh - 40 - (gr - i // gc) * 64 + 6, cw - 12, 44, NAVY, cls="dy") for i in range(days))
    front = R(0, base, W, H - base + 4, TEAL) + R(0, base, W, 16, CREAM) + f'<g class="ld ld0">{"".join(R(x, base + (H - base) * .45, 90, 12, CREAM) for x in range(-360, W + 360, 180))}</g>'
    lights = "".join(f'<g class="hl hl{i}">{C(0, 0, 18, MUSTARD)}{R(-90, -8, 70, 16, CREAM)}</g>' for i in range(5))
    world = ill(X, cid, R(0, 0, W, H, NAVY) + stars(W, H, r, 30, 0.5) + moon + f'<g class="side">{side}</g><g class="bld">{bld}{tiles}</g>' + front + lights)
    val = str(int(float(b["n"])))
    npx = int(min(480, max(300, mr * 1.5 / max(numem(val), .5))))
    nd, nl, nw = numdiv(X, "n", "0", mx, my - npx * 0.52, npx, NAVY, anchor="middle", final=val)
    th, px, hh = title(X, b.get("title", ""), bx + 40, bt + 30, bw - 80, bh - gr * 64 - 90, 84 if P else 70, 40, 3, col=CREAM, emc=MUSTARD, cls="tx ttl")
    ui = (nd + f'<div class="tx un" style="left:{mx + mr * 0.55:.0f}px; top:{my + mr * 0.45:.0f}px; font-size:110px; color:{CREAM}">{X.rich(b.get("unit", ""))}</div>'
          + f'<div class="tag kk" style="left:{mx - mr:.0f}px; top:{my - mr - 40:.0f}px; font-size:38px; background:{CREAM}; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>' + th)
    put(X, cid, t, d, frame(X, b, cid, world, ui, night=True))
    s = f"#{cid}"
    tn = T(X, b, "at_n", t, t + .5)
    X.tw(f'tl.from("{s} .mo", {{y:500, scale:.6, transformOrigin:"50% 50%", duration:0.8, ease:"expo.out"}}, {t:.3f});')
    rise(X, f"{s} .side .bd", t + .1, .03); rise(X, f"{s} .bld", t + .2, dur=.6)
    X.tw(f'tl.to("{s} .dy", {{fill:"{MUSTARD}", duration:0.08, stagger:{max(.02, (d - 1.4) / days):.3f}}}, {t + .7:.3f});')
    lines_in(X, f"{s} .ttl", t + .5)
    counter(X, f"{s} .n", max(t + .2, tn - .4), 0, float(b["n"]), dur=1.0, dec=int(b.get("dec", 0)))
    X.sfx(max(t + .2, tn - .4), "count")
    X.tw(f'tl.from("{s} .un, {s} .kk", {{scale:0, transformOrigin:"0% 50%", duration:0.45, ease:"back.out(2)", stagger:.12}}, {t + .6:.3f});')
    for i in range(5):
        y = base + (H - base) * (0.25 + 0.14 * i)
        X.tw(f'tl.fromTo("{s} .hl{i}", {{x:{-200 - i * 260}, y:{y:.0f}}}, {{x:{W + 300 - i * 120}, y:{y:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    road_go(X, s, t, d)
    X.tw(f'tl.to("{s} .stz", {{x:-30, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    cam(X, f"{s} .cam", t, d, [(t, 1.05, .5, .4), (t + d * .45, 1.0, .5, .5)])


def wallet(b, X, t, d, cid):
    """an income range on cream: a giant teal wallet on a navy counter, two coin stacks rise out of it (heights ∝ value),
    a tomato range bar springs between; the headline is the shop's awning sign."""
    W, H, P = X.W, X.H, X.portrait
    lo, hi = float(b["lo"]), float(b["hi"])
    base = FG(X)
    x0 = L(X)
    if P:
        wx, wy, ww, wh = 90, 920, W - 180, 470
        aw = (0, 250, W, 250)
    else:
        wx, wy, ww, wh = W * 0.5, 470, 820, 380
        aw = (0, 120, W * 0.46, 280)
    stripes = "".join(poly([(aw[0] + i * 120, aw[1] + aw[3] - 70), (aw[0] + i * 120 + 120, aw[1] + aw[3] - 70), (aw[0] + i * 120 + 60, aw[1] + aw[3])], TOMATO if i % 2 == 0 else CREAM) for i in range(int(aw[2] // 120) + 1))
    awning = f'<g class="aw">{R(aw[0], aw[1], aw[2], aw[3] - 70, NAVY)}{stripes}</g>'
    counter_ = R(0, base, W, H - base + 4, NAVY) + R(0, base, W, 18, TOMATO)
    nh = int(b.get("coins", 14)); nl = max(1, round(nh * lo / hi))
    cw_ = 170 if P else 150
    xl, xh = wx + ww * 0.27, wx + ww * 0.73
    stepc = 15
    stack = lambda xc, n, tag: "".join(coin(xc, wy + 40 - i * stepc, cw_, f"cn {tag}") for i in range(n))
    coins = "" if P else f'<g class="cs">{stack(xl, nl, "cl")}{stack(xh, nh, "ch")}</g>'
    wal = (f'<g class="wl">{lshadow(wx, wy, ww, wh, L=180)}{R(wx, wy, ww, wh, TEAL)}'
           f'{cutrect(wx, wy, ww, wh * 0.42, MUSTARD, k=80, corner="br")}{R(wx + ww - 150, wy + wh * 0.28, 150, 110, NAVY)}{C(wx + ww - 80, wy + wh * 0.28 + 55, 26, MUSTARD)}</g>')
    bar_y = wy + wh - 70
    bar = (f'<g class="rg">{R(xl, bar_y, xh - xl, 26, TOMATO, cls="rb")}{C(xl, bar_y + 13, 30, CREAM, cls="rk")}{C(xh, bar_y + 13, 30, CREAM, cls="rk")}</g>')
    world = ill(X, cid, R(0, 0, W, H, CREAM) + awning + counter_ + coins + wal + bar)
    th, px, hh = title(X, b.get("title", ""), aw[0] + x0, aw[1] + 34, aw[2] - 2 * x0, aw[3] - 120, 84 if P else 72, 40, 2, col=CREAM, emc=MUSTARD, cls="tx ttl")
    unit = b.get("unit", "元")
    hs, ls_ = F.fmt_num(hi, zh=False), F.fmt_num(lo, zh=False)
    if P:
        hpx = numpx(hs, W - 2 * x0 - 120, 400, 300)
        hpx = numpx(hs, W - 2 * x0 - 100, 400, 300)
        ny0 = wy - hpx * 0.98
        nd, _, hw = numdiv(X, "nh", hs, W / 2 - 40, ny0, hpx, TOMATO, anchor="middle")
        lo_ = f'<div class="tag nl" style="left:{xl - 150:.0f}px; top:{wy + wh * 0.5:.0f}px; font-size:56px; background:{NAVY}; color:{CREAM}">{X.rich(ls_)} –</div>'
        un = f'<div class="tx un" style="left:{W / 2 - 40 + hw / 2 + 12:.0f}px; top:{ny0 + hpx * .45:.0f}px; font-size:80px; color:{NAVY}">{X.rich(unit)}</div>'
        kick = f'<div class="tag kick" style="left:{x0}px; top:{aw[1] + aw[3] + 10:.0f}px; font-size:36px; background:{MUSTARD}; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>'
    else:
        hpx = numpx(hs, W * 0.38, 340, 280)
        nd, _, hw = numdiv(X, "nh", hs, x0, 520, hpx, TOMATO)
        lo_ = f'<div class="tag nl" style="left:{xl - 130:.0f}px; top:{wy + wh * 0.5:.0f}px; font-size:48px; background:{NAVY}; color:{CREAM}">{X.rich(ls_)} –</div>'
        un = f'<div class="tx un" style="left:{x0 + hw + 20:.0f}px; top:{520 + hpx * .45:.0f}px; font-size:72px; color:{NAVY}">{X.rich(unit)}</div>'
        kick = f'<div class="tag kick" style="left:{x0}px; top:{aw[1] + aw[3] + 20:.0f}px; font-size:34px; background:{MUSTARD}; color:{NAVY}">{X.rich(b.get("kicker", ""))}</div>'
    X.used_text.update(hs + ls_ + " –")
    put(X, cid, t, d, frame(X, b, cid, world, th + nd + lo_ + un + kick))
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .aw", {{yPercent:-100, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    lines_in(X, f"{s} .ttl", t + .3)
    X.tw(f'tl.from("{s} .wl", {{y:240, duration:0.6, ease:"expo.out"}}, {t + .1:.3f});')
    X.tw(f'tl.from("{s} .cl", {{y:160, opacity:0, duration:0.4, ease:"back.out(1.6)", stagger:0.06}}, {t + .45:.3f});')
    X.tw(f'tl.from("{s} .ch", {{y:160, opacity:0, duration:0.4, ease:"back.out(1.6)", stagger:0.05}}, {t + .65:.3f});')
    X.tw(f'tl.from("{s} .rb", {{scaleX:0, transformOrigin:"0% 50%", duration:0.7, ease:"back.out(1.4)"}}, {t + 1.3:.3f});')
    X.tw(f'tl.from("{s} .rk", {{scale:0, transformOrigin:"50% 50%", duration:0.35, ease:"back.out(2.5)", stagger:0.3}}, {t + 1.2:.3f});')
    if P:   # the figure rises out of the wallet's mouth
        X.tw(f'tl.fromTo("{s} .nh", {{y:{hpx * 0.9:.0f}, clipPath:"inset(-20% -5% 100% -5%)"}}, {{y:0, clipPath:"inset(-20% -5% -2% -5%)", duration:0.7, ease:"back.out(1.3)"}}, {t + 0.45:.3f});')
    else:
        X.tw(f'tl.from("{s} .nh", {{scale:.5, opacity:0, transformOrigin:"100% 100%", duration:0.5, ease:"back.out(1.6)"}}, {t + 1.1:.3f});')
    slide(X, f"{s} .nl, {s} .un", t + .8, dx=-80, dur=.5)
    X.tw(f'tl.from("{s} .kick", {{scaleX:0, transformOrigin:"0% 50%", duration:0.4, ease:"expo.out"}}, {t + .5:.3f});')
    for k in range(4): X.sfx(t + .5 + k * .2, "click")
    cam(X, f"{s} .cam", t, d, [(t, 1.06, .5, .65), (t + 1.3, 1.0, .5, .5)])


def _spline(pts, n=14):
    out = []
    Q = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for j in range(n):
            u = j / n
            out.append(tuple(.5 * (2 * p1[q] + (-p0[q] + p2[q]) * u + (2 * p0[q] - 5 * p1[q] + 4 * p2[q] - p3[q]) * u * u + (-p0[q] + 3 * p1[q] - 3 * p2[q] + p3[q]) * u ** 3) for q in (0, 1)))
    out.append(pts[-1])
    return out


def climb(b, X, t, d, cid):
    """the growth as a road up a teal hill under a two-band sky: milestone signs at each year, a courier climbs, the
    forecast stretch has a mustard centre line; the target figure is a navy billboard at the top."""
    W, H, P = X.W, X.H, X.portrait
    marks = b["steps"]
    ys = [float(m[0]) for m in marks]; vs = [float(m[1]) for m in marks]
    y0, y1 = ys[0] - .6, ys[-1] + .3
    xa, xb = (W * .16, W * .7) if P else (W * .1, W * .62)
    ylo, yhi = (H * .9, H * .58) if P else (H * .9, H * .5)
    vmax = max(vs)
    X_ = lambda yr: xa + (xb - xa) * (yr - y0) / (y1 - y0)
    Y_ = lambda v: ylo - (ylo - yhi) * v / vmax
    pts = [(xa - 80, Y_(vs[0] * .8))] + [(X_(y), Y_(v)) for y, v in zip(ys, vs)] + [(W + 80, Y_(vmax) - 30)]
    poly_ = _spline(pts)
    seg = [0.0]
    for i in range(1, len(poly_)): seg.append(seg[-1] + math.dist(poly_[i - 1], poly_[i]))
    Ltot = seg[-1]
    dpath = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly_)
    fut = next((i for i, m in enumerate(marks) if len(m) > 3 and m[3]), len(marks))
    fi = min(range(len(poly_)), key=lambda i: abs(poly_[i][0] - X_(ys[fut - 1]))) if 0 < fut < len(marks) else len(poly_) - 1
    dfut = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly_[fi:])
    area = dpath + f" L{W + 80} {H + 10} L{poly_[0][0]:.0f} {H + 10} Z"
    sky = R(0, 0, W, H * .42, CREAM) + R(0, H * .42, W, H, MUSTARD)
    signs = ""
    for i, m in enumerate(marks[:-1]):
        x, y = X_(ys[i]), Y_(vs[i])
        sc = 0.9 if P else 0.8
        lift = 240 if i % 2 == 1 else 0
        signs += (f'<g transform="translate({x:.0f},{y - 30:.0f}) scale({sc})"><g class="sg sg{i}">{R(-6, -130 - lift, 12, 130 + lift, NAVY)}'
                  f'{cutrect(-110, -250 - lift, 220, 124, CREAM, k=30, corner="tr")}'
                  f'<text x="0" y="{-202 - lift}" text-anchor="middle" style="font-family:var(--f-num); font-size:34px" fill="{NAVY}">{m[0]}{" 预测" if i >= fut else ""}</text>'
                  f'<text x="0" y="{-150 - lift}" text-anchor="middle" style="font-family:var(--f-display); font-weight:900; font-size:40px" fill="{TOMATO}">{m[2]}</text></g></g>')
        X.used_text.update(f"{m[0]}{m[2]} 预测")
    last = marks[-1]
    lx, ly = X_(ys[-1]), Y_(vs[-1])
    bbw, bbh = (660, 380) if P else (440, 260)
    bbx, bby = min(W - 30 - bbw, lx - bbw * 0.5), ly - bbh - (200 if P else 120)
    if not P: bbx = max(bbx, W * 0.6)
    bill = (f'<g class="bill">{R(bbx + 60, bby + bbh, 22, ly - bby - bbh, NAVY)}{R(bbx + bbw - 82, bby + bbh, 22, ly - bby - bbh, NAVY)}'
            f'{cutrect(bbx, bby, bbw, bbh, NAVY, k=60, corner="tr")}</g>')
    trees = "".join(tree(x, H * .97, 1.3, NAVY) for x in (W * .08, W * .2, W * .9))
    world = ill(X, cid, sky + C(W * (.8 if P else .9), H * (.3 if P else .25), 120, CREAM, cls="sun") + f'<path d="{area}" fill="{TEAL}"/>'
                + f'<path class="rd" d="{dpath}" fill="none" stroke="{NAVY}" stroke-width="60" stroke-linecap="butt" stroke-linejoin="round" stroke-dasharray="{Ltot:.0f} {Ltot + 10:.0f}" stroke-dashoffset="{Ltot:.0f}"/>'
                f'<g class="rcg" opacity="0"><path d="{dpath}" fill="none" stroke="{CREAM}" stroke-width="7" stroke-dasharray="26 22"/>'
                f'<path d="{dfut}" fill="none" stroke="{MUSTARD}" stroke-width="9" stroke-dasharray="26 22"/></g>'
                + signs + bill + trees + f'<g class="rr"><g transform="scale({.55 if P else .45})">{rider(1)}</g></g>')
    lab = str(last[2])
    lpx = int(min(400, max(120, (bbw - 60) / max(numem(lab), .5))))
    nd, _, _ = numdiv(X, "big", lab, bbx + bbw / 2, bby + bbh / 2 - lpx * 0.55, lpx, MUSTARD, anchor="middle")
    yr = f'<div class="tx yr" style="left:{bbx + 30:.0f}px; top:{bby + 20:.0f}px; font-size:40px; color:{CREAM}">{last[0]}{" 预测" if len(marks) - 1 >= fut else ""}</div>'
    X.used_text.update(f"{last[0]} 预测")
    x0 = L(X)
    sb = (x0 - 10, 290, W - 2 * x0 + 20, 220) if P else (x0, 140, W * .5, 200)
    signb = f'<div style="position:absolute; left:{sb[0]}px; top:{sb[1]}px; width:{sb[2]:.0f}px; height:{sb[3]}px; background:{NAVY}; clip-path:polygon(0 0, calc(100% - 50px) 0, 100% 50px, 100% 100%, 0 100%)" class="sb"></div>'
    th, px, hh = title(X, b.get("title", ""), sb[0] + 40, sb[1] + 36, sb[2] - 90, sb[3] - 70, 92 if P else 80, 40, 2, col=CREAM, emc=MUSTARD, cls="tx ttl")
    put(X, cid, t, d, frame(X, b, cid, world, signb + th + nd + yr))
    s = f"#{cid}"
    ride_d = min(d - .5, float(b.get("ride", d * .8)))
    t0 = t + .15
    X.tw(f'tl.to("{s} .rd", {{strokeDashoffset:0, duration:{ride_d:.2f}, ease:"sine.inOut"}}, {t0:.3f});')
    X.tw(f'tl.to("{s} .rcg", {{opacity:1, duration:0.3}}, {t0 + ride_d - .1:.3f});')
    def at(f):
        Lf = f * Ltot
        i = max(1, next((q for q in range(len(seg)) if seg[q] >= Lf), len(seg) - 1))
        u = (Lf - seg[i - 1]) / max(1e-6, seg[i] - seg[i - 1])
        x = poly_[i - 1][0] + (poly_[i][0] - poly_[i - 1][0]) * u; y = poly_[i - 1][1] + (poly_[i][1] - poly_[i - 1][1]) * u
        return x, y, math.degrees(math.atan2(poly_[i][1] - poly_[i - 1][1], poly_[i][0] - poly_[i - 1][0]))
    def ease(u): return -(math.cos(math.pi * u) - 1) / 2
    K = 30
    xs0, ys0, a0 = at(0)
    kfs = []
    for j in range(1, K + 1):
        x, y, ang = at(ease(j / K) * 0.93)
        kfs.append(f'{{x:{x:.1f}, y:{y - 20:.1f}, rotation:{ang:.1f}, duration:{ride_d / K:.3f}, ease:"none"}}')
    X.tw(f'tl.set("{s} .rr", {{x:{xs0:.1f}, y:{ys0 - 20:.1f}, rotation:{a0:.1f}, svgOrigin:"0 0"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .rr", {{keyframes:[{", ".join(kfs)}]}}, {t0:.3f});')
    spin(X, f"{s} .wh", t, d, 1.8); bob(X, f"{s} .pp", t, d, 4, .3)
    for i in range(len(marks) - 1):
        xi = X_(ys[i])
        q = min(range(len(poly_)), key=lambda q: abs(poly_[q][0] - xi))
        frac = seg[q] / Ltot
        u = math.acos(1 - 2 * min(1, max(0, frac / .93))) / math.pi
        ti = t0 + ride_d * u - .15
        X.tw(f'tl.from("{s} .sg{i}", {{scaleY:0, transformOrigin:"50% 100%", duration:0.45, ease:"back.out(1.8)"}}, {ti:.3f});')
        X.sfx(ti, "pop")
    tb = t0 + ride_d * 0.8
    rise(X, f"{s} .bill", tb - .3, dur=.5)
    X.tw(f'tl.from("{s} .big, {s} .yr", {{scale:0, transformOrigin:"50% 50%", duration:0.5, ease:"back.out(1.8)"}}, {tb:.3f});')
    X.sfx(tb, "hit")
    X.tw(f'tl.from("{s} .sb", {{xPercent:-110, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    lines_in(X, f"{s} .ttl", t + .25)
    cam(X, f"{s} .cam", t, d, [(t, 1.18, .2, .75), (t0 + ride_d * .45, 1.08, .5, .62), (t0 + ride_d * .85, 1.0, .5, .5)])


def network(b, X, t, d, cid):
    """a top-down city at night: teal blocks on navy, delivery routes draw on in tomato and mustard with a cream courier
    running each; the headline is the map's legend card; a cream avenue with a queue of helmets runs along the bottom."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(31)
    gx, gy = (12, 6) if not P else (7, 9)
    top = 0 if not P else 0
    mh = FG(X)
    bw, bh = W / gx, mh / gy
    blocks = ""
    for i in range(gx):
        for j in range(gy):
            blocks += R(i * bw + 14, top + j * bh + 14, bw - 28, bh - 28, TEAL if r.random() > .15 else CREAM, cls="bk")
    nr = int(b.get("routes", 14))
    routes, dots, pins, paths = "", "", "", []
    for k in range(nr):
        i0, j0 = r.randrange(1, gx), r.randrange(1, gy)
        i1, j1 = min(gx - 1, max(1, i0 + r.choice([-4, -3, -2, 2, 3, 4]))), min(gy - 1, max(1, j0 + r.choice([-3, -2, 2, 3])))
        x0_, y0_, x1, y1 = i0 * bw, j0 * bh, i1 * bw, j1 * bh
        Ln = abs(x1 - x0_) + abs(y1 - y0_) + 1
        col = [TOMATO, MUSTARD][k % 2]
        routes += f'<path class="rt rt{k}" d="M{x0_:.0f} {y0_:.0f} L{x1:.0f} {y0_:.0f} L{x1:.0f} {y1:.0f}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="square" stroke-dasharray="{Ln:.0f} {Ln + 10:.0f}" stroke-dashoffset="{Ln:.0f}"/>'
        dots += f'<g class="dt dt{k}" opacity="0">{C(0, 0, 16, CREAM)}</g>'
        pins += f'<g transform="translate({x1:.0f},{y1:.0f})"><g class="pn pn{k}">{poly([(-20, 0), (0, -34), (20, 0)], col)}{R(-20, 0, 40, 26, col)}</g></g>'
        paths.append(((x0_, y0_, x1, y1), Ln))
    ave = R(0, mh, W, H - mh + 4, CREAM) + R(0, mh, W, 16, TOMATO)
    q = "".join(person(x, H - (H - mh) * 0.25, 1.6, [TEAL, TOMATO, NAVY][i % 3], helmet=MUSTARD, cls="qp") for i, x in enumerate(range(60, W + 60, 120)))
    world = ill(X, cid, R(0, 0, W, H, NAVY) + blocks + routes + pins + dots + ave + q)
    x0 = L(X)
    cw = W - 2 * x0 if P else W * .46
    ctop = 300 if P else 160
    th, px, hh = title(X, b.get("title", ""), x0 + 36, ctop + 34, cw - 100, 340 if P else 300, 92 if P else 84, 44, 3, col=NAVY, cls="tx ttl")
    card = f'<div class="lgc" style="position:absolute; left:{x0}px; top:{ctop}px; width:{cw:.0f}px; height:{hh + 70:.0f}px; background:{CREAM}; clip-path:polygon(0 0, calc(100% - 60px) 0, 100% 60px, 100% 100%, 0 100%)"></div>'
    put(X, cid, t, d, frame(X, b, cid, world, card + th, night=True))
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .bk", {{scale:0, transformOrigin:"50% 50%", duration:0.35, ease:"back.out(1.6)", stagger:{{each:0.006, from:"center"}}}}, {t:.3f});')
    span = min(.38, max(.04, (d - 1.5) / nr))
    for k, ((ax, ay, bx, by), Ln) in enumerate(paths):
        tk = t + .3 + k * span
        X.tw(f'tl.to("{s} .rt{k}", {{strokeDashoffset:0, duration:0.9, ease:"none"}}, {tk:.3f});')
        s1 = abs(bx - ax) / Ln
        X.tw(f'tl.set("{s} .dt{k}", {{x:{ax:.0f}, y:{ay:.0f}, opacity:1}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .dt{k}", {{keyframes:[{{x:{bx:.0f}, y:{ay:.0f}, duration:{.9 * s1 + .01:.2f}, ease:"none"}}, {{x:{bx:.0f}, y:{by:.0f}, duration:{.9 * (1 - s1) + .01:.2f}, ease:"none"}}]}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .dt{k}", {{scale:0, transformOrigin:"50% 50%", duration:0.2}}, {tk + .92:.3f});')
        X.tw(f'tl.from("{s} .pn{k}", {{scale:0, transformOrigin:"50% 100%", duration:0.4, ease:"back.out(2)"}}, {tk + .85:.3f});')
    X.tw(f'tl.from("{s} .lgc", {{scaleX:0, transformOrigin:"0% 50%", duration:0.5, ease:"expo.out"}}, {t + .2:.3f});')
    lines_in(X, f"{s} .ttl", t + .4)
    X.tw(f'tl.from("{s} .qp", {{y:120, duration:0.45, ease:"back.out(1.5)", stagger:0.05}}, {t + .3:.3f});')
    X.sfx(t + .3, "enter")
    for k in range(0, nr, 3): X.sfx(t + .3 + k * span + .85, "pop")
    cam(X, f"{s} .cam", t, d, [(t, 1.12, .5, .4), (t + d * .45, 1.0, .5, .5)])


def outro(b, X, t, d, cid):
    """night: the channel name stands on a mustard plinth over a teal-and-tomato skyline, the road runs out underneath."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(5)
    base = FG(X)
    x0 = L(X)
    city_ = skyline(W, base, r, [TEAL, TOMATO], MUSTARD, 180, 380 if P else 300, lit=0.4)
    mr = 90
    moon = f'<g class="mo">{C(W * .8, H * .2, mr, MUSTARD)}{C(W * .8 + mr * .45, H * .2 - mr * .3, mr * .85, NAVY)}</g>'
    front = road(X, base) + f'<g transform="translate(0,{base + (H - base) * .62:.0f})"><g class="r1">{rider_shadow(.8)}{rider(.8)}</g></g>'
    world = ill(X, cid, R(0, 0, W, H, NAVY) + stars(W, H, r, 40, .5) + moon + f'<g class="oc">{city_}</g>' + front)
    tt = b.get("title", X.channel)
    tpx = 150 if P else 140
    ty = H * .3 if P else 230
    plinth = f'<div class="pl" style="position:absolute; left:{x0 - 20}px; top:{ty - 30:.0f}px; width:{min(W - 2 * x0 + 40, F.width(tt) * tpx + 120):.0f}px; height:{tpx * 1.5:.0f}px; background:{MUSTARD}; clip-path:polygon(0 0, calc(100% - 60px) 0, 100% 60px, 100% 100%, 0 100%)"></div>'
    ui = (plinth + f'<div class="tx ot" style="left:{x0 + 20}px; top:{ty:.0f}px; font-size:{tpx}px; color:{NAVY}">{X.rich(tt, split="chars")}</div>'
          f'<div class="tx os" style="left:{x0}px; top:{ty + tpx * 1.6:.0f}px; font-size:48px; color:{CREAM}">{X.rich(b.get("sub", ""))}</div>'
          f'<div class="tag oc2" style="left:{x0}px; top:{ty + tpx * 1.6 + 90:.0f}px; font-size:40px; background:{TOMATO}; color:{CREAM}">{X.rich(b.get("cta", ""))}</div>')
    put(X, cid, t, d, frame(X, b, cid, world, ui, night=True))
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .pl", {{scaleX:0, transformOrigin:"0% 50%", duration:0.5, ease:"expo.out"}}, {t + .05:.3f});')
    X.tw(f'tl.from("{s} .ot .c", {{yPercent:110, opacity:0, duration:0.45, ease:"back.out(1.6)", stagger:0.06}}, {t + .3:.3f});')
    X.tw(f'tl.from("{s} .os, {s} .oc2", {{x:-60, opacity:0, duration:0.45, ease:"expo.out", stagger:0.15}}, {t + .6:.3f});')
    rise(X, f"{s} .oc .bd", t, .03)
    X.tw(f'tl.from("{s} .mo", {{y:300, duration:0.8, ease:"expo.out"}}, {t + .2:.3f});')
    X.tw(f'tl.fromTo("{s} .r1", {{x:-300}}, {{x:{W + 300}, duration:{max(2.0, d):.2f}, ease:"none"}}, {t:.3f});')
    spin(X, f"{s} .r1 .wh", t, d); bob(X, f"{s} .r1 .pp", t, d)
    road_go(X, s, t, d)
    X.sfx(t + .1, "hit")


def _wrap(fn, focus):
    def run(b, X, t, d, cid):
        fx, fy = b.get("focus") or focus(X)
        bubble(X, cid, t, fx, fy)
        fn(b, X, t, d, cid)
    run.__doc__ = fn.__doc__
    return run


SCENES = {
    "city": _wrap(city, lambda X: (.5, .5)),
    "grow": _wrap(grow, lambda X: (.5, .7)),
    "hero": _wrap(hero, lambda X: (.5, .6)),
    "crowd": _wrap(crowd, lambda X: (.5, .7)),
    "month": _wrap(month, lambda X: (.5, .38) if X.portrait else (.74, .35)),
    "wallet": _wrap(wallet, lambda X: (.5, .6)),
    "climb": _wrap(climb, lambda X: (.1, .8)),
    "network": _wrap(network, lambda X: (.5, .5)),
    "outro": _wrap(outro, lambda X: (.5, .4)),
}


# ---------------------------------------------------------------- effects in this style (aefx beats: "scene": "fx")
# Four page themes, each a different illustrated world drawn behind the effect by FX_FRAME:
#   paper = dusk city · ink = night city · lemon = sunny park · red = coral sunset
STYLE["fx_themes"] = {
    "paper": {"bg": "#17203d", "fg": "#f6efe2", "muted": "#f6efe2", "accent": "#f0502f", "card": "#f6efe2", "card-fg": "#17203d", "line": "rgba(255,246,234,.22)"},
    "ink":   {"bg": "#17203d", "fg": "#f6efe2", "muted": "#f6efe2", "accent": "#1f8a80", "card": "#1f8a80", "card-fg": "#f6efe2", "line": "rgba(255,246,234,.16)"},
    "lemon": {"bg": "#f6efe2", "fg": "#17203d", "muted": "#1f8a80", "accent": "#f0502f", "card": "#f6efe2", "card-fg": "#17203d", "line": "rgba(36,37,90,.18)"},
    "red":   {"bg": "#f0502f", "fg": "#17203d", "muted": "rgba(36,37,90,.72)", "accent": "#17203d", "card": "#f6efe2", "card-fg": "#17203d", "line": "rgba(36,37,90,.25)"},
}
FX_WORLD = {"paper": ("#1f8a80", "dusk"), "ink": ("#17203d", "night"), "lemon": ("#f2b632", "park"), "red": ("#f2b632", "sunset")}

STYLE["css"] = r"""
/* ---- effects (aefx) in flat: grounds come from FX_FRAME; the effect's own page paint goes transparent over them */
.st-flat .fx, .st-flat .ctx, .st-flat .flg { --f-mono: var(--f-num); }
.st-flat .flg { overflow:hidden; background:linear-gradient(180deg, var(--bg) 0%, var(--bg) 30%, color-mix(in srgb, var(--bg) 62%, var(--g2)) 100%); }
.st-flat .flg svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.st-flat .flg .s1 { fill:color-mix(in srgb, var(--fg) 6%, transparent); }
.st-flat .flg .s2 { fill:color-mix(in srgb, var(--fg) 11%, transparent); }
.st-flat .flg .wn { fill:color-mix(in srgb, #f2b632 60%, transparent); }
.st-flat .flg .sun { fill:color-mix(in srgb, var(--g2) 70%, var(--bg)); }
.st-flat .flg .sun2 { fill:none; stroke:color-mix(in srgb, var(--g2) 60%, transparent); stroke-width:8; stroke-dasharray:4 30; stroke-linecap:round; }
.st-flat .flg .cl { fill:color-mix(in srgb, #f6efe2 72%, transparent); }
.st-flat .flg .h1 { fill:color-mix(in srgb, #1f8a80 30%, var(--bg)); } .st-flat .flg .h2 { fill:color-mix(in srgb, #1f8a80 55%, var(--bg)); }
.st-flat .flg .h3 { fill:color-mix(in srgb, #17203d 16%, var(--bg)); } .st-flat .flg .h4 { fill:color-mix(in srgb, #17203d 30%, var(--bg)); }
.st-flat .flg .tr { fill:color-mix(in srgb, #1f8a80 70%, var(--bg)); } .st-flat .flg .tk { fill:color-mix(in srgb, #17203d 70%, var(--bg)); }
.st-flat .flg .st { fill:var(--fg); }
.st-flat .flg .pt { fill:none; stroke:var(--fg); stroke-width:3.5; stroke-linecap:round; opacity:.35; }
.st-flat .flg .bd { fill:none; stroke:color-mix(in srgb, var(--fg) 60%, transparent); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
/* ---- the page around an effect */
.st-flat .ctx .flh { position:absolute; left:80px; right:80px; top:40px; height:48px; display:flex; align-items:center; justify-content:space-between; color:var(--fg); }
.st-flat .ctx .flh .l { display:flex; align-items:center; gap:12px; font:900 28px var(--f-display); }
.st-flat .ctx .flh .l i { width:30px; height:30px; border-radius:50%; background:#f2b632; box-shadow:inset -6px -6px 0 rgba(0,0,0,.14); }
.st-flat .ctx .flh .tp { font:700 28px var(--f-body); padding:5px 16px 7px; border-radius:999px; background:color-mix(in srgb, var(--fg) 12%, transparent); }
.st-flat .ctx .flh .id { font:700 28px var(--f-num); color:#17203d; background:#f2b632; padding:5px 16px 7px; border-radius:999px; box-shadow:0 4px 0 rgba(36,37,90,.3); }
.st-flat .ctx .cap { position:absolute; left:0; right:0; bottom:66px; text-align:center; }
.st-flat .ctx .cap > span { display:inline-block; font-family:var(--f-body); font-weight:700; line-height:1.3; color:#17203d; background:#f6efe2; padding:9px 30px 11px;
  border-radius:999px; box-shadow:0 6px 0 rgba(36,37,90,.32); max-width:80%; }
.st-flat .ctx .cap .em .emt { color:#17203d; padding:0 .12em; background:linear-gradient(#f2b632, #f2b632) no-repeat 0 82% / 100% 46%; }
.st-flat .ctx .cap .em .emb { display:none; }
.st-flat .ctx .flf { position:absolute; left:80px; right:80px; bottom:22px; display:flex; justify-content:space-between; gap:32px; font:600 28px var(--f-body); color:var(--fg); opacity:.9; }
.st-flat .ctx .flf > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; }
.st-flat .ctx.photo .flh, .st-flat .ctx.photo .flf { color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.6); opacity:1; }
.st-flat .ctx.photo .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(20,20,60,.55), rgba(0,0,0,0) 18%, rgba(0,0,0,0) 72%, rgba(20,20,60,.6)); }
#root.v.st-flat .ctx .flh { left:56px; right:56px; top:206px; } #root.v.st-flat .ctx .flf { left:56px; right:120px; bottom:auto; top:1478px; font-size:28px; }
#root.v.st-flat .ctx .cap { bottom:auto; top:1330px; padding:0 120px; } #root.v.st-flat .ctx .cap > span { max-width:100%; }
/* ---- effect internals, flat: rounder corners, flat offset shadows instead of blurred ones, palette blocks */
.st-flat .fx .cw, .st-flat .fx .wpi, .st-flat .fx .wpp-cd, .st-flat .fx .aq-card, .st-flat .fx .hp-card, .st-flat .fx .dl-c, .st-flat .fx .iv-q {
  border-radius:3.4vmin !important; box-shadow:0 1.3vmin 0 rgba(20,20,60,.26) !important; }
.st-flat .fx .pc-art, .st-flat .fx .th-pol, .st-flat .fx .iv-f, .st-flat .fx .iv-nb, .st-flat .fx .mx-card, .st-flat .fx .mx-c { border-radius:2.4vmin !important; box-shadow:0 1.3vmin 0 rgba(20,20,60,.28) !important; }
.st-flat .fx .mx-card img, .st-flat .fx .mx-c img, .st-flat .fx .iv-f video, .st-flat .fx .th-pol img { border-radius:inherit; }
.st-flat .fx .mx-hl { border-radius:2.4vmin !important; box-shadow:0 0 0 .8vmin #f2b632, 0 1.6vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .pc-disc { box-shadow:0 1.3vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .wpr-pp { box-shadow:0 1.3vmin 0 rgba(20,20,60,.22) !important; border-radius:1.6vmin 1.6vmin 0 0; }
.st-flat .fx .wpr-slot { border-radius:2.4vmin !important; box-shadow:0 1vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .hp-bub b, .st-flat .fx .th-st.bubble b { border-radius:999px !important; box-shadow:0 .6vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .cw .bar i:nth-child(1) { background:#f0502f; } .st-flat .fx .cw .bar i:nth-child(2) { background:#f2b632; } .st-flat .fx .cw .bar i:nth-child(3) { background:#1f8a80; }
.st-flat .fx .cw .u { border-radius:3vmin 3vmin .8vmin 3vmin; } .st-flat .fx .cw .in { border:none; background:color-mix(in srgb, var(--card-fg) 7%, transparent); }
.st-flat .fx .cw .ab .hlm::before { background:#f2b632; height:.5em; border-radius:.12em; }
.st-flat .fx .wpi-bb { border-radius:2.2vmin !important; } .st-flat .fx .wpi-av { border-radius:50% !important; }
.st-flat .fx .wpp-tg { border-radius:999px !important; padding-left:1.2vmin; padding-right:1.2vmin; }
.st-flat .fx .l3 .bar { width:1.4vmin; border-radius:1vmin; background:#f2b632; }
.st-flat .fx .l3 .nm span { text-shadow:0 .6vmin 0 rgba(20,20,60,.25); }
.st-flat .fx .l3 .rl span { font-family:var(--f-body); font-weight:600; letter-spacing:.06em; }
.st-flat .fx .ti svg { fill:color-mix(in srgb, var(--fg) 14%, transparent); stroke-width:1.9; padding:1.4vmin; border-radius:50%; background:color-mix(in srgb, var(--fg) 9%, transparent); box-sizing:content-box; }
.st-flat .fx .ti .rg { border-color:#f2b632; }
.st-flat .fx .aq-kick, .st-flat .fx .ct-kick { border-radius:999px !important; }
.st-flat .fx .th-set { background:radial-gradient(ellipse 50% 60% at var(--hx, 32%) 58%, color-mix(in srgb, #f2b632 45%, transparent), transparent 70%) !important; }
.st-flat .fx .th-set::before { display:none; }
.st-flat .fx .th-st.tag b { color:#17203d; background:#f2b632; border-radius:999px; box-shadow:0 .14em 0 rgba(36,37,90,.35); padding:.2em .7em; }
.st-flat .fx .th-pol { border-radius:1.6vmin; }
.st-flat .fx .dl-ring, .st-flat .fx .hp-ring { border-radius:3.4vmin !important; }
"""


def _sil(W, base, r, cls, hmin, hmax, win=False, x0=-80):
    """flat skyline silhouette for the effect grounds: rects (+ gables) in one CSS class, optional lit windows."""
    s, x = [], x0
    while x < W + 160:
        w = r.randint(80, 160); h = r.randint(hmin, hmax)
        s.append(f'<rect class="{cls}" x="{x}" y="{base - h:.0f}" width="{w}" height="{h + 6:.0f}" rx="6"/>')
        if r.random() < .3: s.append(f'<path class="{cls}" d="M{x} {base - h + 1:.0f} L{x + w / 2:.0f} {base - h - w * .3:.0f} L{x + w} {base - h + 1:.0f} Z"/>')
        if win:
            for i in range(max(1, (h - 40) // 44)):
                for j in range(max(1, w // 40)):
                    if r.random() < .35: s.append(f'<rect class="wn" x="{x + 14 + j * 38}" y="{base - h + 22 + i * 44:.0f}" width="14" height="18" rx="3"/>')
        x += w + r.randint(4, 20)
    return "".join(s)


def _fx_world(X, kind, r):
    """the illustrated ground of one effect card: four worlds, each laid out from a seed so no two cards match."""
    W, H, P = X.W, X.H, X.portrait
    base = H * (.97 if not P else .82)       # 9:16: the skyline stands just under the caption band, the rest is the platform's
    stars = "".join(f'<circle class="st tw" cx="{r.uniform(0, W):.0f}" cy="{r.uniform(H * .02, H * .45):.0f}" r="{r.uniform(1.5, 4):.1f}" opacity="{r.uniform(.25, .7):.2f}"/>' for _ in range(34))
    pts = "".join((f'<circle class="pt" cx="{x:.0f}" cy="{y:.0f}" r="{r.uniform(6, 12):.0f}"/>' if r.random() < .5 else
                   f'<path class="pt" d="M{x - 9:.0f} {y:.0f} H{x + 9:.0f} M{x:.0f} {y - 9:.0f} V{y + 9:.0f}"/>')
                  for x, y in ((r.uniform(0, W), r.uniform(H * .1, H * .8)) for _ in range(10)))
    sx = r.choice([.1, .9]) * W              # sun / moon keep to the upper corners, away from the effect in the middle
    sy = H * (.17 if not P else .2)
    ground = ""
    if P:                        # 9:16: the band under the skyline is a street (the platform UI sits over it)
        ground = (f'<rect class="s2" x="0" y="{base + 4:.0f}" width="{W}" height="{H - base:.0f}"/><g class="fw-ln">'
                  + "".join(f'<rect class="s2" x="{x}" y="{base + (H - base) * .45:.0f}" width="80" height="10" rx="5"/>' for x in range(-180, W + 360, 180)) + "</g>"
                  + f'<g transform="translate(0,{base + (H - base) * .38:.0f})"><g class="fw-r">{rider(.72)}</g></g>')
    if kind == "dusk":
        sun = f'<circle class="sun fw-sun" cx="{sx:.0f}" cy="{sy:.0f}" r="{min(W, H) * .07:.0f}"/>'
        body = (stars + sun + f'<g class="fw-1">{_sil(W, base - 30, r, "s1", 160, 360)}</g><g class="fw-2">{_sil(W, base + 10, r, "s2", 70, 210, win=True)}</g>' + ground)
    elif kind == "night":
        mr = min(W, H) * .06
        mx = W * .9
        moon = (f'<g class="fw-sun"><circle class="sun" cx="{mx:.0f}" cy="{sy:.0f}" r="{mr:.0f}" style="fill:#f2b632"/>'
                f'<circle cx="{mx + mr * .42:.0f}" cy="{sy - mr * .26:.0f}" r="{mr * .86:.0f}" style="fill:var(--bg)"/></g>')
        body = (stars + moon + f'<g class="fw-1">{_sil(W, base - 10, r, "s1", 120, 300, win=True)}</g>'
                f'<g class="fw-2">{_sil(W, base + 20, r, "s2", 50, 150)}</g>' + ground)
    elif kind == "park":
        sun = (f'<g class="fw-sun"><circle class="sun" cx="{sx:.0f}" cy="{H * .16:.0f}" r="{min(W, H) * .09:.0f}" style="fill:#f2b632"/>'
               f'<circle class="sun2 rays" cx="{sx:.0f}" cy="{H * .16:.0f}" r="{min(W, H) * .13:.0f}"/></g>')
        clouds = ""
        for _ in range(4):
            cx, cy, k = r.uniform(0, W), r.uniform(H * .08, H * .34), r.uniform(.7, 1.3)
            clouds += (f'<g class="cl"><ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{70 * k:.0f}" ry="{26 * k:.0f}"/><circle cx="{cx - 24 * k:.0f}" cy="{cy - 14 * k:.0f}" r="{28 * k:.0f}"/>'
                       f'<circle cx="{cx + 22 * k:.0f}" cy="{cy - 20 * k:.0f}" r="{34 * k:.0f}"/></g>')
        hills = (f'<path class="h1" d="M-40 {base - 60:.0f} Q{W * .25:.0f} {base - 230:.0f} {W * .52:.0f} {base - 70:.0f} T{W + 40} {base - 110:.0f} V{H + 10} H-40 Z"/>'
                 f'<path class="h2" d="M-40 {base:.0f} Q{W * .3:.0f} {base - 130:.0f} {W * .62:.0f} {base - 20:.0f} T{W + 40} {base - 40:.0f} V{H + 10} H-40 Z"/>')
        trees = "".join(f'<g transform="translate({x:.0f},{base - 40 + r.uniform(-20, 20):.0f}) scale({r.uniform(.7, 1.2):.2f})"><rect class="tk" x="-6" y="-46" width="12" height="46" rx="4"/>'
                        f'<circle class="tr" cx="0" cy="-70" r="34"/><circle class="tr" cx="-18" cy="-56" r="22"/></g>' for x in (r.uniform(.03, .2) * W, r.uniform(.8, .97) * W))
        body = sun + f'<g class="fw-cl">{clouds}</g><g class="fw-1">{hills}</g><g class="fw-2">{trees}</g>'
    else:   # sunset
        sun = f'<circle class="sun fw-sun" cx="{sx:.0f}" cy="{base - H * .14:.0f}" r="{min(W, H) * .2:.0f}" style="fill:#f2b632; opacity:.75"/>'
        hills = (f'<path class="h3" d="M-40 {base - 80:.0f} Q{W * .2:.0f} {base - 200:.0f} {W * .45:.0f} {base - 90:.0f} T{W + 40} {base - 120:.0f} V{H + 10} H-40 Z"/>'
                 f'<path class="h4" d="M-40 {base - 10:.0f} Q{W * .35:.0f} {base - 110:.0f} {W * .7:.0f} {base - 30:.0f} T{W + 40} {base - 50:.0f} V{H + 10} H-40 Z"/>')
        birds = "".join(f'<path class="bd" d="M{x - 18:.0f} {y:.0f} q9 -10 18 0 q9 -10 18 0"/>' for x, y in ((r.uniform(.2, .8) * W, r.uniform(.1, .3) * H) for _ in range(4)))
        far, near = hills.split("/>", 1)
        body = sun + f'<g class="fw-cl">{birds}</g><g class="fw-1">{far}/></g><g class="fw-2">{near}</g>'
    return f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="none">{body}<g class="fw-pt">{pts}</g></svg>'


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect in flat: an illustrated ground behind it (city / night / park / sunset by theme),
    a pill header, the spoken line as a cream pill caption with a highlighter keyword, and a soft footer."""
    th = p.get("theme") if p.get("theme") in FX_WORLD else "paper"
    g2, kind = FX_WORLD[th]
    r = rnd(sum(map(ord, cid)) * 7 + X.beat.get("i", 0))
    if not parts["photo"]:
        X.css(f"flg-{cid}", f"#{cid} {{ background:transparent !important; }}")
        X.clip(f"{cid}g", t, d, _fx_world(X, kind, r), "flg", 2, track=19, sty=parts["sty"] + f";--g2:{g2}")
        g = f"#{cid}g"
        X.tw(f'tl.from("{g} .fw-1, {g} .fw-2", {{y:90, duration:0.8, ease:"expo.out", stagger:0.08}}, {t:.3f});')
        X.tw(f'tl.fromTo("{g} .fw-1", {{x:0}}, {{x:-36, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{g} .fw-2", {{x:0}}, {{x:-80, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{g} .fw-pt", {{y:0}}, {{y:-90, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.from("{g} .fw-sun", {{scale:0, transformOrigin:"50% 50%", duration:0.7, ease:"back.out(2)"}}, {t + .1:.3f});')
        if kind in ("park", "sunset"):
            X.tw(f'tl.fromTo("{g} .fw-cl", {{x:0}}, {{x:70, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        if kind == "park":
            X.tw(f'tl.fromTo("{g} .rays", {{rotation:0, transformOrigin:"50% 50%"}}, {{rotation:60, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        if kind in ("dusk", "night"):
            X.tw(f'tl.to("{g} .tw", {{opacity:.1, duration:0.6, yoyo:true, repeat:{max(1, int(d / .6)) | 1}, stagger:{{each:0.05, from:"center"}}}}, {t:.3f});')
            if X.portrait:      # the street band under the caption: dashes slide, a courier crosses
                X.tw(f'tl.fromTo("{g} .fw-ln", {{x:0}}, {{x:-180, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
                X.tw(f'tl.fromTo("{g} .fw-r", {{x:-200}}, {{x:{X.W + 200}, duration:{max(2.4, d):.2f}, ease:"none"}}, {t:.3f});')
                spin(X, f"{g} .fw-r .wh", t, d, 2.0)
                bob(X, f"{g} .fw-r .pp", t, d, 4, .32)
    topic = f'<span class="tp">{parts["topic"]}</span>' if parts["topic"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + f'<div class="flh"><div class="l"><i></i><b>{X.rich(X.channel)}</b>{topic}</div>'
             f'<div class="id">{parts["fxid"]}</div></div>'
             + f'<div class="cap"><span style="font-size:{parts["cap_px"]}px">{parts["cap"]}</span></div>'
             + f'<div class="flf"><div>{parts["foot"]}</div><div>{parts["src"]}</div></div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    c = f"#{cid}c"
    X.tw(f'tl.from("{c} .flh > div", {{y:-24, opacity:0, duration:0.45, ease:"back.out(2)", stagger:0.1}}, {t + .05:.3f});')
    X.tw(f'tl.from("{c} .cap > span", {{y:24, scale:.86, opacity:0, duration:0.45, ease:"back.out(2.2)"}}, {t + 0.08:.3f});')
    X.tw(f'tl.fromTo("{c} .cap .em .emt", {{backgroundSize:"0% 46%"}}, {{backgroundSize:"100% 46%", duration:0.4, ease:"power2.out"}}, {t + 0.5:.3f});')
