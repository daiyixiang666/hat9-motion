"""flat · 扁平插画风 —— 矢量插画式的讲解片：Kurzgesagt / Headspace 一路的几何造型和饱和配色。
城市、骑手、包裹、硬币、路牌全部用 SVG 基本形状现画，柔和渐变 + 细颗粒；角色有挤压回弹，前中后景分层视差，
场景之间用「色盘转场」（一个色盘吞掉旧画面，新画面从同一点开圆）；数据图也画成插画：
包裹堆 = 柱状图，小人点阵 = 人数，跑道 = 月度，硬币堆 = 区间，上坡公路 = 增长曲线，城市路网 = 收束。

场景全部自写（SCENES）：city 城市开场 · grow 包裹堆对比 · hero 骑手特写 · crowd 小人点阵 · month 月度跑道 ·
wallet 收入区间 · climb 增长公路 · network 城市路网 · outro 落版。横竖屏各自排版；标题、数字、卡片放在镜头层之外，
插画世界在镜头层里推拉。文字走 h9.fit 自适应；包裹、小人、硬币、路牌、路线数量都按输入计算。
"""
import math, random
from h9 import fit as F

STYLE = {
    "name": "扁平插画", "en": "Flat", "benchmarks": ["Kurzgesagt", "Headspace", "Google Doodle", "Duolingo 插画系统"],
    "tokens": {
        "bg": "#2b2c6b", "fg": "#fff6ea", "muted": "#c9c3e6", "accent": "#ff7a59", "accent2": "#ffc94a", "alert": "#ff5d5d",
        "line": "rgba(255,246,234,.18)", "paper": "#fff6ea", "ink": "#24255a", "card": "#fff6ea", "card-fg": "#24255a",
        "coral": "#ff7a59", "sun": "#ffc94a", "mint": "#48d1b2", "lilac": "#a68bfa", "sky": "#6c8cff", "night": "#24255a", "cream": "#fff6ea",
        "cap-bg": "#fff6ea", "cap-fg": "#24255a", "cap-size": "40px", "cap-weight": "700", "cap-pad": "10px 28px 12px", "cap-radius": "999px",
        "cap-shadow": "0 6px 0 rgba(36,37,90,.35)", "cap-em": "#ff7a59", "cap-bottom": "60px", "punch-top": "70%", "punch-size": "68px",
        "mascot-bg": "#ffc94a",
    },
    "fonts": {"display": ["alibaba-puhuiti-heavy", "noto-sans-sc"], "body": ["misans", "noto-sans-sc"], "num": ["space-grotesk", "noto-sans-sc"],
              "hand": ["zcool-kuaile", "noto-sans-sc"]},
    "motion": {"ease": "back.out(1.7)", "dur": 0.6, "stagger": 0.04, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 90, "bottom": 0, "h": 400}, "portrait": {"left": 620, "bottom": 600, "h": 330}},
    "sfx": {"transition": ("whoosh_soft", 0.35), "enter": ("whoosh_soft", 0.3), "pop": ("pop", 0.4), "hit": ("hit", 0.4), "boing": ("boing", 0.35),
            "count": ("type", 0.25), "click": ("click", 0.3), "mascot": ("whoosh_soft", 0.3), "slam": ("slam", 0.35), "cut": ("whoosh_soft", 0.3)},
}

PAL = ["#ffc94a", "#ff7a59", "#48d1b2", "#a68bfa", "#6c8cff"]
INK, CREAM = "#24255a", "#fff6ea"

CSS = r"""
.fl { position:absolute; inset:0; overflow:hidden; }
.fl .cam { position:absolute; inset:0; }
.fl .ui { position:absolute; inset:0; z-index:5; pointer-events:none; }
.fl svg.ill { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.fl .hd { position:absolute; left:80px; top:44px; display:flex; align-items:center; gap:12px; font-family:var(--f-display); font-size:24px; color:var(--cream); z-index:6; }
.fl .hd i { display:inline-block; width:30px; height:30px; border-radius:50%; background:var(--sun); box-shadow:inset -6px -6px 0 rgba(0,0,0,.14); }
.fl .hd span { opacity:.82; font-family:var(--f-body); font-weight:600; }
.fl .ft { position:absolute; left:80px; right:80px; bottom:22px; font-family:var(--f-body); font-weight:500; font-size:19px; color:var(--cream); opacity:.8; z-index:6; }
.fl.light .hd, .fl.light .ft { color:var(--ink); }
.fl .ttl { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--cream); line-height:1.12; text-shadow:0 5px 0 rgba(36,37,90,.28); }
.fl .ttl .ln { display:block; overflow:hidden; padding:0 .04em .1em 0; } .fl .ttl .ln > span { display:inline-block; }
.fl .ttl .em .emt { color:var(--sun); }
.fl.light .ttl { color:var(--ink); text-shadow:none; } .fl.light .ttl .em .emt { color:var(--ink); }
.fl.light .ttl .em .emb { display:block; left:-.06em; right:-.06em; top:.52em; bottom:.06em; background:var(--cream); border-radius:.18em; }
.fl .card .ttl { color:var(--ink); text-shadow:none; } .fl .card .ttl .em .emt { color:var(--coral); }
.fl .em .emb { display:none; }
.fl.light .ttl .em .emb { display:block; }
.fl .kick { position:absolute; font-family:var(--f-hand); font-size:28px; color:var(--ink); background:var(--sun); padding:6px 20px 8px; border-radius:999px;
  box-shadow:0 5px 0 rgba(36,37,90,.3); white-space:nowrap; }
.fl .num { font-family:var(--f-num); font-weight:700; letter-spacing:-.03em; line-height:.9; font-variant-numeric:tabular-nums; }
.fl .card { position:absolute; background:var(--cream); color:var(--ink); border-radius:34px; box-shadow:0 12px 0 rgba(36,37,90,.3); }
.fl .card .k { font:700 30px/1.2 var(--f-body); opacity:.8; }
.fl .card .u { font:900 60px/1 var(--f-display); }
.fl .badge { position:absolute; font-family:var(--f-num); font-weight:700; color:var(--ink); background:var(--sun); border-radius:999px; padding:8px 24px 10px;
  box-shadow:0 6px 0 rgba(36,37,90,.3); white-space:nowrap; }
.fl .lab { text-align:center; border-radius:24px; padding:14px 0 16px; }
.fl .lab .k { font-size:26px; } .fl .lab .num { font-size:58px; margin-top:4px; } .fl .lab small { font:900 26px var(--f-display); letter-spacing:0; }
#root.v .fl .hd { left:56px; top:214px; }
#root.v .fl .ft { left:56px; right:56px; bottom:auto; top:1432px; font-size:21px; }
#root.v.st-flat { --cap-bottom:516px; }
"""


# ---------------------------------------------------------------- the SVG kit: everything is a primitive in the palette
def rnd(seed): return random.Random(seed)


def grad(gid, a, b, vertical=True):
    x2, y2 = ("0", "1") if vertical else ("1", "0")
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'


def sky(X, cid, a, b):
    return f'<defs>{grad(cid + "g", a, b)}</defs><rect width="{X.W}" height="{X.H}" fill="url(#{cid}g)"/>'


def building(x, base, w, h, col, win, r, lit=0.55, roof=0):
    """one flat building: body, a roof cap or gable, a grid of windows with a seeded lit pattern."""
    s = [f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h + 4:.0f}" rx="6" fill="{col}"/>']
    if roof == 1: s.append(f'<rect x="{x + w * .2:.0f}" y="{base - h - 18:.0f}" width="{w * .6:.0f}" height="22" rx="4" fill="{col}"/>')
    if roof == 2: s.append(f'<path d="M{x:.0f} {base - h + 1:.0f} L{x + w / 2:.0f} {base - h - w * .28:.0f} L{x + w:.0f} {base - h + 1:.0f} Z" fill="{col}"/>')
    cols = max(1, int(w // 34)); rows = max(1, int((h - 30) // 40))
    gx = (w - cols * 18) / (cols + 1)
    for i in range(rows):
        for j in range(cols):
            on = r.random() < lit
            s.append(f'<rect x="{x + gx + j * (18 + gx):.0f}" y="{base - h + 22 + i * 40:.0f}" width="18" height="22" rx="3" fill="{win if on else "rgba(0,0,0,.16)"}"/>')
    return "".join(s)


def skyline(W, base, r, cols, win, hmin=160, hmax=420, x0=-60, x1=None):
    s, x = [], x0
    while x < (x1 or W + 160):
        w = r.randint(90, 170); h = r.randint(hmin, hmax)
        s.append(building(x, base, w, h, r.choice(cols), win, r, roof=r.choice([0, 0, 1, 2])))
        x += w + r.randint(6, 22)
    return "".join(s)


def cloud(x, y, k=1.0, col=CREAM, op=.9):
    return (f'<g opacity="{op:.2f}"><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{70 * k:.0f}" ry="{26 * k:.0f}" fill="{col}"/>'
            f'<circle cx="{x - 24 * k:.0f}" cy="{y - 14 * k:.0f}" r="{28 * k:.0f}" fill="{col}"/><circle cx="{x + 22 * k:.0f}" cy="{y - 20 * k:.0f}" r="{34 * k:.0f}" fill="{col}"/></g>')


def tree(x, base, k, col="#2fb39a"):
    return (f'<g transform="translate({x:.0f},{base:.0f}) scale({k:.2f})"><rect x="-6" y="-46" width="12" height="46" rx="4" fill="#7a4b3a"/>'
            f'<circle cx="0" cy="-70" r="34" fill="{col}"/><circle cx="-18" cy="-56" r="22" fill="{col}"/><circle cx="12" cy="-90" r="10" fill="rgba(255,255,255,.18)"/></g>')


def rider(k=1.0, jacket="#48d1b2", box="#ffc94a", body="#ff7a59", flip=False):
    """a delivery rider on a scooter. Origin = the ground between the wheels. Wheels (.wh), rider+box (.pp) and the box (.bx)
    are separate groups so they can spin / bob / squash."""
    return (f'<g class="rider" transform="scale({-k if flip else k},{k})">'
            f'<ellipse cx="0" cy="4" rx="112" ry="11" fill="rgba(0,0,0,.2)"/>'
            f'<g class="wh"><circle cx="-62" cy="-24" r="24" fill="{INK}"/><circle cx="-62" cy="-24" r="9" fill="{CREAM}"/><rect x="-64" y="-46" width="4" height="44" fill="{CREAM}" opacity=".35"/></g>'
            f'<g class="wh"><circle cx="66" cy="-24" r="24" fill="{INK}"/><circle cx="66" cy="-24" r="9" fill="{CREAM}"/><rect x="64" y="-46" width="4" height="44" fill="{CREAM}" opacity=".35"/></g>'
            f'<path d="M-92 -40 Q-92 -62 -70 -62 L40 -62 Q58 -62 66 -46 L78 -24 L-40 -24 Q-60 -24 -70 -34 Z" fill="{body}"/>'
            f'<path d="M-80 -58 L30 -58" stroke="rgba(255,255,255,.3)" stroke-width="5" stroke-linecap="round"/>'
            f'<path d="M50 -62 L76 -132" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><path d="M64 -132 L96 -136" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>'
            f'<circle cx="86" cy="-74" r="9" fill="#ffc94a"/>'
            f'<g class="pp"><g class="bx"><rect x="-122" y="-152" width="80" height="72" rx="10" fill="{box}"/><rect x="-122" y="-130" width="80" height="12" fill="rgba(0,0,0,.12)"/>'
            f'<rect x="-90" y="-152" width="14" height="72" fill="rgba(255,255,255,.35)"/></g>'
            f'<path d="M-30 -62 L-6 -112" stroke="{INK}" stroke-width="16" stroke-linecap="round"/>'
            f'<rect x="-40" y="-170" width="58" height="72" rx="22" fill="{jacket}"/>'
            f'<path d="M6 -150 L62 -128" stroke="{jacket}" stroke-width="15" stroke-linecap="round"/>'
            f'<circle cx="-6" cy="-190" r="22" fill="#ffd3b4"/>'
            f'<path d="M-31 -192 A26 26 0 0 1 21 -192 Z" fill="#ffc94a"/><rect x="-33" y="-196" width="56" height="8" rx="4" fill="#ff7a59"/>'
            f'<circle cx="6" cy="-184" r="3" fill="{INK}"/></g></g>')


def parcel(x, y, s, col, tilt, cls, frac=1.0):
    """a box standing on (x, y); frac < 1 draws a part-filled box (the remainder of a value)."""
    h = s * frac
    return (f'<g transform="translate({x:.0f},{y:.0f}) rotate({tilt:.1f})"><g class="{cls}"><rect x="{-s / 2:.0f}" y="{-h:.0f}" width="{s:.0f}" height="{h:.0f}" rx="{s * .12:.0f}" fill="{col}"/>'
            f'<rect x="{-s * .08:.0f}" y="{-h:.0f}" width="{s * .16:.0f}" height="{h:.0f}" fill="rgba(255,255,255,.4)"/>'
            f'<rect x="{-s / 2:.0f}" y="{-h:.0f}" width="{s:.0f}" height="{min(h, s * .14):.0f}" rx="{s * .1:.0f}" fill="rgba(0,0,0,.1)"/></g></g>')


def purse(x, y, k):
    """a flat wallet with notes and coins peeking out (.wc pop up out of it)."""
    coins = "".join(f'<g transform="translate({cx},{-150})"><g class="wc">{coin(0, 0, 30, "")}</g></g>' for cx in (-70, -10, 50))
    return (f'<g transform="translate({x:.0f},{y:.0f}) scale({k:.2f})"><g class="ps">{coins}'
            f'<rect x="-96" y="-196" width="120" height="70" rx="10" fill="#48d1b2" transform="rotate(-8)"/><rect x="-60" y="-200" width="120" height="70" rx="10" fill="#7be0c8" transform="rotate(6)"/>'
            f'<rect x="-130" y="-160" width="260" height="176" rx="34" fill="#6c4cc9"/>'
            f'<rect x="-130" y="-160" width="260" height="62" rx="30" fill="#7d5ee0"/>'
            f'<rect x="58" y="-108" width="92" height="72" rx="22" fill="#5a3db3"/><circle cx="104" cy="-72" r="14" fill="#ffc94a"/>'
            f'<rect x="-100" y="-26" width="150" height="10" rx="5" fill="rgba(255,255,255,.2)"/></g></g>')


def person(x, y, k, col, helmet="#ffc94a"):
    return (f'<g transform="translate({x:.1f},{y:.1f}) scale({k:.3f})"><g class="pr"><rect x="-11" y="-30" width="22" height="30" rx="9" fill="{col}"/>'
            f'<circle cx="0" cy="-41" r="10" fill="#ffd3b4"/><path d="M-11 -42 A11 11 0 0 1 11 -42 Z" fill="{helmet}"/></g></g>')


def coin(x, y, s, cls):
    return (f'<g transform="translate({x:.0f},{y:.0f})"><g class="{cls}"><ellipse cx="0" cy="{s * .18:.0f}" rx="{s:.0f}" ry="{s * .34:.0f}" fill="#d99a1e"/>'
            f'<ellipse cx="0" cy="0" rx="{s:.0f}" ry="{s * .34:.0f}" fill="#ffc94a"/><ellipse cx="0" cy="0" rx="{s * .68:.0f}" ry="{s * .2:.0f}" fill="none" stroke="#d99a1e" stroke-width="3"/></g></g>')


def street(X, y0, flip=False):
    """a road band from y0 to the bottom edge: kerb, two lanes of dashes, a rider each way. 9:16 uses it under the caption band
    (the platform's own UI covers that area, so it carries motion, never information)."""
    W, H = X.W, X.H
    h = H - y0
    dash = lambda y: "".join(f'<rect x="{x}" y="{y:.0f}" width="80" height="10" rx="5" fill="{CREAM}" opacity=".45"/>' for x in range(-180, W + 360, 180))
    return (f'<g class="street"><rect x="0" y="{y0:.0f}" width="{W}" height="{h + 4:.0f}" fill="{INK}"/><rect x="0" y="{y0:.0f}" width="{W}" height="14" fill="#48d1b2"/>'
            f'<g class="sd1">{dash(y0 + h * .4)}</g><g class="sd2">{dash(y0 + h * .78)}</g>'
            f'<g transform="translate(0,{y0 + h * .36:.0f})"><g class="sr1">{rider(.62, jacket="#a68bfa", box="#ff7a59", body="#6c8cff", flip=not flip)}</g></g>'
            f'<g transform="translate(0,{y0 + h * .72:.0f})"><g class="sr2">{rider(.8, flip=flip)}</g></g></g>')


def street_go(X, s, t, d):
    W = X.W
    X.tw(f'tl.fromTo("{s} .sr1", {{x:{W + 200}}}, {{x:-200, duration:{max(2.4, d):.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .sr2", {{x:-260}}, {{x:{W + 260}, duration:{max(2.0, d * .9):.2f}, ease:"none"}}, {t + .2:.3f});')
    X.tw(f'tl.fromTo("{s} .sd1", {{x:0}}, {{x:180, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .sd2", {{x:0}}, {{x:-360, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    spin(X, f"{s} .street .wh", t, d, 2.0)
    bob(X, f"{s} .street .pp", t, d, 4, .32)


def floaters(X, r, n=18, cols=(CREAM,), area=(0, 0, 1, 1)):
    """floating particles in three depth groups (dots, rings, plus signs); drift() moves each group at its own speed."""
    g = [[], [], []]
    for i in range(n):
        x = r.uniform(area[0], area[2]) * X.W; y = r.uniform(area[1], area[3]) * X.H
        s = r.uniform(5, 13); c = r.choice(cols); op = r.uniform(.35, .8); kind = r.choice("ddrp")
        if kind == "d": e = f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s * .6:.1f}" fill="{c}" opacity="{op:.2f}"/>'
        elif kind == "r": e = f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{s:.1f}" fill="none" stroke="{c}" stroke-width="3.5" opacity="{op:.2f}"/>'
        else: e = f'<path d="M{x - s:.0f} {y:.0f} H{x + s:.0f} M{x:.0f} {y - s:.0f} V{y + s:.0f}" stroke="{c}" stroke-width="4" stroke-linecap="round" opacity="{op:.2f}"/>'
        g[i % 3].append(e)
    return "".join(f'<g class="fz fz{k}">{"".join(v)}</g>' for k, v in enumerate(g))


def drift(X, s, t, d):
    for k, (dx, dy) in enumerate([(-40, -70), (30, -110), (-15, -45)]):
        X.tw(f'tl.fromTo("{s} .fz{k}", {{x:0, y:0}}, {{x:{dx}, y:{dy}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .fz > *", {{scale:0, transformOrigin:"50% 50%", duration:0.4, ease:"back.out(3)", stagger:0.025}}, {t + .1:.3f});')


# ---------------------------------------------------------------- layout + motion helpers
def L(X): return 56 if X.portrait else 96


def title(X, text, left, top, box_w, box_h, max_px, min_px=40, lines=3, cls="ttl", sty=""):
    """an adaptive title block → (html, px, height)."""
    f = F.fit_text(text, box_w, box_h, max_px, min_px, lh=1.12, max_lines=lines)
    body = "".join(f'<span class="ln"><span>{X.rich(l)}</span></span>' for l in f.lines)
    return f'<div class="{cls}" style="left:{left:.0f}px; top:{top:.0f}px; font-size:{f.px}px; {sty}">{body}</div>', f.px, f.n * f.px * 1.12


def frame(X, b, cid, world, ui="", light=False):
    """world = the illustration (inside the camera); ui = titles/cards/numbers (fixed, outside the camera)."""
    X.css("flat", CSS)
    meta = X.v.get("meta", {})
    src = b.get("src", "")
    hd = f'<div class="hd"><i></i><b>{X.rich(X.channel)}</b><span>{X.rich(meta.get("section", "生意图鉴"))}</span></div>'
    ft = f'<div class="ft">{"来源：" + X.rich(src) if src else ""}</div>'
    return f'<div class="fl{" light" if light else ""}"><div class="cam">{world}</div><div class="ui">{ui}</div>{hd}{ft}</div>'


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def counter(X, sel, t, a, b, dur=1.0, dec=0, ease="power3.out"):
    js = f"o.v.toFixed({dec})" if dec else "String(Math.round(o.v))"
    X.used_text.update("0123456789.")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"{ease}", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def numpx(v, dec, box_w, max_px, unit="", unit_px=60):
    """the biggest numeral size whose final value (plus its unit) fits box_w — the counter never outgrows its card."""
    digits = len(f"{float(v):.{dec}f}" if dec else str(int(round(float(v)))))
    room = box_w - F.width(unit) * unit_px - 16
    return int(max(48, min(max_px, room / (digits * .62))))


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
            x2, y2 = xy(sc * 1.025, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{sc * 1.025:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - h0:.2f}, ease:"none"}}, {h0:.3f});')


def spin(X, sel, t, d, rate=1.6):
    X.tw(f'tl.fromTo("{sel}", {{rotation:0, transformOrigin:"50% 50%"}}, {{rotation:{360 * d * rate:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def bob(X, sel, t, d, amp=7, per=0.42):
    n = max(1, int(d / per))
    X.tw(f'tl.fromTo("{sel}", {{y:0}}, {{y:{-amp}, duration:{per / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:{n * 2 - 1}}}, {t:.3f});')


def drop(X, sel, t, st=0.05, dur=0.55, h=280):
    """squash-and-stretch landing: falls in stretched, squashes flat on contact, springs back."""
    a = dur * .5
    X.tw(f'tl.fromTo("{sel}", {{y:{-h}, scaleY:1.3, scaleX:.82, opacity:0, transformOrigin:"50% 100%"}}, {{y:0, scaleY:1.1, scaleX:.92, opacity:1, duration:{a:.2f}, ease:"power2.in", stagger:{st:.3f}}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel}", {{scaleY:.68, scaleX:1.22, transformOrigin:"50% 100%"}}, {{scaleY:1, scaleX:1, duration:{dur * .7:.2f}, ease:"elastic.out(1, .45)", stagger:{st:.3f}, immediateRender:false}}, {t + a:.3f});')


def lines_in(X, sel, t, st=0.08):
    X.tw(f'tl.from("{sel} .ln > span", {{yPercent:110, rotation:4, duration:0.6, ease:"back.out(1.6)", stagger:{st}}}, {t:.3f});')


def pop(X, sel, t, rot=-10, st=0.0):
    X.tw(f'tl.from("{sel}", {{scale:0, rotation:{rot}, duration:0.5, ease:"back.out(2.6)", stagger:{st}}}, {t:.3f});')


def bubble(X, cid, t, fx=.5, fy=.5):
    """the style's seam: a palette disc swallows the old frame from (fx, fy), the new frame opens as a circle from the same point,
    with a ring burst. Skipped on the first beat."""
    if X.beat.get("i", 0) == 0: return
    W, H = X.W, X.H
    col = PAL[X.beat["i"] % len(PAL)]
    cx, cy = fx * W, fy * H
    R = math.hypot(max(cx, W - cx), max(cy, H - cy)) + 20
    a = X.uid("fb"); u = X.uid("fb")
    X.clip(a, t - 0.3, 0.32, f'<svg class="ill" viewBox="0 0 {W} {H}" style="position:absolute; inset:0; width:100%; height:100%"><circle class="dk" cx="{cx:.0f}" cy="{cy:.0f}" r="{R:.0f}" fill="{col}"/>'
                               f'<circle class="dk2" cx="{cx:.0f}" cy="{cy:.0f}" r="{R * .55:.0f}" fill="rgba(255,255,255,.18)"/></svg>', "tr-bub", 38)
    X.tw(f'tl.from("#{a} .dk, #{a} .dk2", {{scale:0, transformOrigin:"50% 50%", duration:0.3, ease:"power3.in", stagger:0.04}}, {t - 0.3:.3f});')
    X.clip(u, t, 0.6, f'<div style="position:absolute; inset:0; background:{col}"></div>'
                      f'<svg viewBox="0 0 {W} {H}" style="position:absolute; inset:0; width:100%; height:100%"><circle class="rg" cx="{cx:.0f}" cy="{cy:.0f}" r="{R * .5:.0f}" fill="none" stroke="{CREAM}" stroke-width="18"/></svg>', "tr-bub", 1)
    X.tw(f'tl.fromTo("#{cid} > .stage", {{clipPath:"circle(0% at {fx * 100:.0f}% {fy * 100:.0f}%)"}}, {{clipPath:"circle(150% at {fx * 100:.0f}% {fy * 100:.0f}%)", duration:0.55, ease:"power3.out"}}, {t:.3f});')
    X.tw(f'tl.set("#{cid} > .stage", {{clipPath:"none"}}, {t + 0.56:.3f});')
    X.tw(f'tl.fromTo("#{u} .rg", {{scale:0.1, opacity:1, transformOrigin:"50% 50%"}}, {{scale:1.6, opacity:0, duration:0.55, ease:"power2.out"}}, {t:.3f});')
    X.sfx(t - 0.3, "transition")


# ---------------------------------------------------------------- scenes
def city(b, X, t, d, cid):
    """dusk city in three parallax layers, riders crossing both ways, an order pops on a phone; the headline number counts up on a card."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(b.get("seed", 7))
    base = H * (.72 if not P else .62)
    ground = base + (H - base) * .45 if not P else base + 120
    far = skyline(W, base - 40, r, ["#4b4a93", "#5a55a3", "#463f8c"], "#ffd98a", hmin=170 if not P else 200, hmax=330 if not P else 460)
    mid = skyline(W, base, r, ["#ff7a59", "#e8664c", "#f08a5d"], "#ffe3a3", hmin=100, hmax=240 if not P else 300)
    clouds = "".join(cloud(r.uniform(0, W), r.uniform(H * .1, H * .34), r.uniform(.7, 1.3), op=r.uniform(.45, .8)) for _ in range(6))
    road = (f'<rect x="0" y="{base:.0f}" width="{W}" height="{H - base:.0f}" fill="{INK}"/><rect x="0" y="{base:.0f}" width="{W}" height="10" fill="#48d1b2"/>'
            + "".join(f'<rect x="{x}" y="{yy:.0f}" width="80" height="10" rx="5" fill="{CREAM}" opacity=".5"/>' for x in range(-160, W + 320, 180)
                      for yy in ((ground + 46,) if not P else (ground + 60, H * .9))))
    sun = f'<circle class="sun" cx="{W * (.74 if not P else .76):.0f}" cy="{H * (.3 if not P else .36):.0f}" r="{min(W, H) * .11:.0f}" fill="#ffc94a"/>'
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#2b2c6b", "#ff8f6b")}{sun}<g class="far">{far}</g><g class="cl">{clouds}</g>'
             f'<g class="mid">{mid}</g><g class="road">{road}</g>'
             f'<g transform="translate(0,{base + (ground - base) * .35 if not P else H * .84:.0f})"><g class="r2">{rider(.55 if not P else .9, jacket="#a68bfa", box="#ff7a59", body="#6c8cff", flip=True)}</g></g>'
             f'<g transform="translate(0,{ground:.0f})"><g class="r1">{rider(1.25 if not P else 1.1)}</g></g>'
             f'{floaters(X, r, 16, (CREAM, "#ffc94a"), (0, .05, 1, .6))}</svg>')
    phone = (f'<div class="card ph" style="left:{W * (.6 if not P else .5):.0f}px; top:{(base - 330) if not P else base - 240:.0f}px; width:250px; padding:16px 20px 18px; border-radius:24px">'
             f'<div style="font:900 22px var(--f-display)">{X.rich(b.get("ping", "新订单 · 叮"))}</div>'
             f'<div style="font:600 18px/1.3 var(--f-body); opacity:.7; margin-top:6px">{X.rich(b.get("order", ""))}</div></div>')
    x0 = L(X)
    th, px, hh = title(X, b.get("title", ""), x0, 140 if not P else 290, W * (.5 if not P else .86), 190, 74 if not P else 72, 40, 2)
    cw, chh = (640, 290) if not P else (W - 2 * x0, 320)
    cy0 = (140 + hh + 34) if not P else 290 + hh + 40
    card = (f'<div class="card ck" style="left:{x0}px; top:{cy0:.0f}px; width:{cw}px; height:{chh}px; padding:30px 44px">'
            f'<div class="k">{X.rich(b.get("kicker", ""))}</div>'
            f'<div style="display:flex; align-items:flex-end; gap:14px; margin-top:12px"><span class="num n" style="font-size:{numpx(b.get("value", 0) or 0, int(b.get("dec", 0)), cw - 88, 168 if not P else 186, b.get("unit", ""))}px; color:#ff7a59">0</span>'
            f'<span class="u" style="padding-bottom:14px">{X.rich(b.get("unit", ""))}</span></div></div>')
    X.clip(cid, t, d, frame(X, b, cid, world + phone, th + card), "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + .8)
    X.tw(f'tl.from("{s} .far", {{y:80, duration:1.0, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .mid", {{y:140, duration:1.0, ease:"expo.out"}}, {t + .08:.3f});')
    for sel, dx in ((".far", -40), (".mid", -110), (".cl", -170)):
        X.tw(f'tl.to("{s} {sel}", {{x:{dx}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .sun", {{scale:0, transformOrigin:"50% 50%", duration:0.8, ease:"back.out(2)"}}, {t + .1:.3f});')
    X.tw(f'tl.fromTo("{s} .r1", {{x:-300}}, {{x:{W + 300}, duration:{max(2.2, d * .8):.2f}, ease:"power1.inOut"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .r2", {{x:{W + 120}}}, {{x:-160, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    spin(X, f"{s} .r1 .wh", t, d); spin(X, f"{s} .r2 .wh", t, d, -2.2)
    bob(X, f"{s} .r1 .pp", t, d); bob(X, f"{s} .r2 .pp", t, d, 4, .34)
    X.tw(f'tl.from("{s} .ph", {{scale:0, rotation:-14, transformOrigin:"0% 100%", duration:0.45, ease:"back.out(2.6)"}}, {t + .5:.3f});')
    X.tw(f'tl.to("{s} .ph", {{rotation:3, duration:0.12, yoyo:true, repeat:3, ease:"sine.inOut"}}, {t + .95:.3f});')
    X.sfx(t + .5, "pop")
    X.tw(f'tl.from("{s} .ck", {{y:70, scaleY:.6, scaleX:1.1, transformOrigin:"50% 100%", opacity:0, duration:0.6, ease:"elastic.out(1, .55)"}}, {max(t + .15, tn - .6):.3f});')
    counter(X, f"{s} .n", max(t + .25, tn - .35), 0, float(b.get("value", 0) or 0), dur=1.2, dec=int(b.get("dec", 0)))
    X.sfx(max(t + .25, tn - .35), "count")
    lines_in(X, s + " .ttl", t + .2)
    drift(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.12, .5, .75), (t + 1.0, 1.0, .5, .5)])


def grow(b, X, t, d, cid):
    """two parcel stacks (1 box = `per`), a remainder drawn as a part-box; boxes drop in with squash; a dashed arrow and the badge."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(4)
    A, B = b["a"], b["b"]
    va, vb, per = float(A["v"]), float(B["v"]), float(b.get("per", 500))
    cols = int(b.get("cols", 3))
    s = (72 if not P else 80) * min(1.0, 3 / cols)
    gx = [W * .34, W * .64] if not P else [W * .27, W * .73]
    base = H * .8 if not P else H * .69
    step = s * 1.06
    def stack(v, x0, col, tag):
        n_full = int(v // per + 1e-9); frac = v / per - n_full
        n = n_full + (1 if frac > .05 else 0)
        out = []
        for i in range(n):
            c, rw = i % cols, i // cols
            out.append(parcel(x0 + (c - (cols - 1) / 2) * (s + 8), base - rw * step, s, col, r.uniform(-3, 3), f"pc {tag}", frac if i == n_full else 1.0))
        return "".join(out), math.ceil(n / cols)
    sa, ra = stack(va, gx[0], "#ffc94a", "pa"); sb, rb = stack(vb, gx[1], "#ff7a59", "pb")
    ground = f'<rect x="0" y="{base:.0f}" width="{W}" height="{H - base:.0f}" fill="{INK}"/><rect x="0" y="{base:.0f}" width="{W}" height="12" fill="#48d1b2"/>'
    hills = (f'<path d="M0 {base:.0f} Q{W * .2:.0f} {base - 120:.0f} {W * .45:.0f} {base:.0f} Z" fill="#8d74f0"/>'
             f'<path d="M{W * .4:.0f} {base:.0f} Q{W * .75:.0f} {base - 190:.0f} {W * 1.05:.0f} {base:.0f} Z" fill="#8d74f0"/>')
    trees = "".join(tree(x, base, k) for x, k in ((W * .08, 1.1), (W * .92, 1.3), (W * .49, .8)))
    lab_top = lambda rows: base - rows * step - 150
    ya, yb = lab_top(ra), lab_top(rb)
    arrow = (f'<path class="ar" d="M{gx[0] + 120:.0f} {ya + 30:.0f} Q{(gx[0] + gx[1]) / 2:.0f} {min(ya, yb) - 90:.0f} {gx[1] - 160:.0f} {yb + 20:.0f}" fill="none" stroke="{CREAM}" stroke-width="6" stroke-linecap="round" stroke-dasharray="14 14"/>'
             f'<path class="ah" d="M{gx[1] - 182:.0f} {yb + 2:.0f} L{gx[1] - 156:.0f} {yb + 22:.0f} L{gx[1] - 186:.0f} {yb + 36:.0f}" fill="none" stroke="{CREAM}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>')
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#6c8cff", "#a68bfa")}'
             + "".join(cloud(r.uniform(0, W), r.uniform(H * .12, H * .32), r.uniform(.6, 1.1), op=.55) for _ in range(5))
             + hills + trees + ground + (street(X, base + 160) if P else "") + sa + sb + floaters(X, r, 14, (CREAM,), (0, .1, 1, .6)) + "</svg>")
    unit = b.get("unit", "")
    def lab(x, top, name, v, cls):
        return (f'<div class="card lab {cls}" style="left:{x - 150:.0f}px; top:{top:.0f}px; width:300px">'
                f'<div class="k">{X.rich(name)}</div><div class="num">{X.rich(F.fmt_num(v, zh=False))}<small> {X.rich(unit)}</small></div></div>')
    x0 = L(X)
    th, px, hh = title(X, b.get("title", ""), x0, 140 if not P else 290, W * (.6 if not P else .86), 170, 76, 40, 2)
    legend = b.get("legend") or f"1 个包裹 = {F.fmt_num(per, zh=False)} {unit}"
    kick = f'<div class="kick lg" style="left:{x0}px; top:{(140 if not P else 290) + hh + 22:.0f}px; font-size:24px">{X.rich(legend)}</div>'
    bl, bt = (gx[1] + 100, yb - 44) if not P else (gx[1] - 40, yb - 92)
    badge = f'<div class="badge bd" style="left:{bl:.0f}px; top:{bt:.0f}px; font-size:44px; transform:rotate(-6deg)">{X.rich(b.get("badge", ""))}</div>'
    arrow_svg = f'<svg class="ill" viewBox="0 0 {W} {H}">{arrow}</svg>'
    ui = th + kick + arrow_svg + lab(gx[0], ya, A["name"], va, "la") + lab(gx[1], yb, B["name"], vb, "lb") + badge
    X.clip(cid, t, d, frame(X, b, cid, world, ui), "scene", 2)
    s = f"#{cid}"
    tb = T(X, b, "at_b", t, t + d * .4)
    drop(X, s + " .pa", t + .1, st=min(.06, .9 / max(1, va / per)))
    drop(X, s + " .pb", max(t + .5, tb - .7), st=min(.05, 1.0 / max(1, vb / per)))
    X.tw(f'tl.from("{s} .la", {{y:30, scale:.8, opacity:0, duration:0.5, ease:"back.out(2)"}}, {t + .6:.3f});')
    X.tw(f'tl.from("{s} .lb", {{y:30, scale:.8, opacity:0, duration:0.5, ease:"back.out(2)"}}, {tb + .2:.3f});')
    X.tw(f'tl.from("{s} .ar", {{strokeDashoffset:600, opacity:0, duration:0.7, ease:"power2.out"}}, {tb - .2:.3f});')
    X.tw(f'tl.from("{s} .ah", {{opacity:0, duration:0.2}}, {tb + .4:.3f});')
    X.tw(f'tl.from("{s} .bd", {{scale:0, rotation:-40, duration:0.55, ease:"back.out(3)"}}, {tb + .45:.3f});')
    X.tw(f'tl.to("{s} .bd", {{y:-12, duration:0.35, ease:"sine.inOut", yoyo:true, repeat:{max(1, int((t + d - tb - 1.1) / .35)) | 1}}}, {tb + 1.0:.3f});')
    X.sfx(tb + .45, "boing")
    X.sfx(t + .35, "pop"); X.sfx(max(t + .5, tb - .7) + .3, "pop")
    lines_in(X, s + " .ttl", t)
    pop(X, s + " .lg", t + .35, -6)
    drift(X, s, t, d)
    if P: street_go(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.1, .3, .7), (tb - .4, 1.0, .5, .55)])


def hero(b, X, t, d, cid):
    """the rider up close: a big character skids in, speed lines and a city strip rush past behind; the line lands beside."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(11)
    k = 2.3 if not P else 2.1
    gx, gy = (W * .66, H * .86) if not P else (W * .5, H * .66)
    streaks = "".join(f'<rect x="{r.uniform(-200, W):.0f}" y="{r.uniform(H * .12, H * .92):.0f}" width="{r.randint(140, 420)}" height="{r.choice([6, 8, 12])}" rx="6" fill="{CREAM}" opacity="{r.uniform(.15, .4):.2f}"/>' for _ in range(28))
    strip = skyline(W * 2.2, gy - 10, r, ["#2fb39a", "#33c2a4", "#2aa58e"], "#bff3e6", hmin=110, hmax=260, x1=W * 2.3)
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#24255a", "#48d1b2")}<g class="strip" opacity=".9">{strip}</g>'
             f'<rect x="0" y="{gy - 10:.0f}" width="{W}" height="{H - gy + 10:.0f}" fill="{INK}"/>'
             + (f'<g class="hd2">{"".join(f"<rect x={chr(34)}{x}{chr(34)} y={chr(34)}{yy:.0f}{chr(34)} width={chr(34)}120{chr(34)} height={chr(34)}12{chr(34)} rx={chr(34)}6{chr(34)} fill={chr(34)}{CREAM}{chr(34)} opacity={chr(34)}.4{chr(34)}/>" for x in range(-240, W * 2 + 240, 240) for yy in (H * .78, H * .9))}</g>' if P else "")
             + f'<g class="sl">{streaks}</g><circle class="halo" cx="{gx:.0f}" cy="{gy - 250 * k / 2:.0f}" r="{300 if not P else 340}" fill="#ffc94a"/>'
             f'<circle class="halo2" cx="{gx:.0f}" cy="{gy - 250 * k / 2:.0f}" r="{380 if not P else 420}" fill="none" stroke="#ffc94a" stroke-width="10" stroke-dasharray="4 26" stroke-linecap="round"/>'
             f'<g transform="translate({gx:.0f},{gy:.0f})"><g class="hr">{rider(k, jacket="#ff7a59", box="#48d1b2", body="#6c8cff")}</g></g>'
             f'{floaters(X, r, 14, (CREAM, "#ffc94a"))}</svg>')
    x0 = L(X)
    top = H * .3 if not P else 330
    th, px, hh = title(X, b.get("title", ""), x0, top, W * (.42 if not P else .86), 330 if not P else 300, 112 if not P else 104, 50, 3)
    ktop = top - 74 if not P else top + hh + 26
    kick = f'<div class="kick" style="left:{x0}px; top:{ktop:.0f}px">{X.rich(b.get("kicker", ""))}</div>'
    X.clip(cid, t, d, frame(X, b, cid, world, th + kick), "scene", 2)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .sl", {{x:300}}, {{x:-700, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .strip", {{x:0}}, {{x:{-W * 1.1:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if P: X.tw(f'tl.fromTo("{s} .hd2", {{x:0}}, {{x:{-W:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .halo", {{scale:0, transformOrigin:"50% 50%", duration:0.7, ease:"back.out(1.6)"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .halo2", {{rotation:0, scale:.6, transformOrigin:"50% 50%"}}, {{rotation:90, scale:1, duration:{d:.2f}, ease:"power2.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hr", {{x:-1100, duration:0.6, ease:"expo.out"}}, {t + .05:.3f});')
    X.tw(f'tl.fromTo("{s} .hr", {{skewX:-14}}, {{skewX:0, duration:0.55, ease:"elastic.out(1, .4)", immediateRender:false}}, {t + .5:.3f});')
    spin(X, f"{s} .wh", t, d, 2.2)
    bob(X, f"{s} .pp", t + .6, d - .6, 9, .36)
    X.tw(f'tl.fromTo("{s} .bx", {{scaleY:1, scaleX:1, transformOrigin:"50% 100%"}}, {{scaleY:.86, scaleX:1.08, duration:0.12, yoyo:true, repeat:1, ease:"sine.inOut", immediateRender:false}}, {t + .55:.3f});')
    lines_in(X, s + " .ttl", t + .25, .1)
    pop(X, s + " .kick", t + .15, -8)
    X.sfx(t + .05, "enter"); X.sfx(t + .55, "slam")
    drift(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.0, .5, .5), (t + d * .4, 1.08, .64 if not P else .5, .6)])


def crowd(b, X, t, d, cid):
    """a crowd of helmeted figures (1 figure = `per` units) marching in by rows; the counter rides the fill; a wave runs through it."""
    W, H, P = X.W, X.H, X.portrait
    nv, per = float(b["n"]), float(b.get("per", 5))
    n = max(1, min(600, round(nv / per)))
    r = rnd(23)
    box = (W * .45, H * .22, W * .5, H * .6) if not P else (W * .08, H * .4, W * .84, H * .28)
    cols, rows = F.grid(n, box[2], box[3], 0.6)
    cw, ch = box[2] / cols, box[3] / rows
    k = min(cw / 28, ch / 54) * .95
    figs = "".join(person(box[0] + (i % cols + .5) * cw, box[1] + (i // cols + 1) * ch, k, PAL[1 + r.randrange(4)]) for i in range(n))
    pad = f'<rect x="{box[0] - 30:.0f}" y="{box[1] - 26:.0f}" width="{box[2] + 60:.0f}" height="{box[3] + 52:.0f}" rx="40" fill="rgba(255,255,255,.07)"/>'
    world = f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#2b2c6b", "#3f418f")}{pad}<g class="crowd">{figs}</g>{floaters(X, r, 12, ("#ffc94a", CREAM))}</svg>'
    x0 = L(X)
    top = H * .3 if not P else 300
    unit = b.get("unit", "")
    big = (f'<div class="bigc" style="position:absolute; left:{x0}px; top:{top:.0f}px; color:var(--cream)">'
           f'<div style="font:700 32px var(--f-body); opacity:.85">{X.rich(b.get("kicker", ""))}</div>'
           f'<div style="display:flex; align-items:flex-end; gap:12px"><span class="num n" style="font-size:{numpx(nv, int(b.get("dec", 0)), W * .4 if not P else W - 2 * x0, 210 if not P else 196, unit, 72)}px; color:#ffc94a">0</span>'
           f'<span style="font:900 72px var(--f-display); padding-bottom:18px">{X.rich(unit)}</span></div>'
           f'<div style="font:900 36px/1.3 var(--f-display); margin-top:12px; max-width:{W * .36 if not P else W * .84:.0f}px">{X.rich(b.get("sub", ""))}</div></div>')
    legend = b.get("legend") or f"每个小人 = {F.fmt_num(per, zh=False)} {unit}"
    big = big[:-len("</div>")] + f'<div class="kick lg" style="position:relative; display:inline-block; margin-top:22px; font-size:24px">{X.rich(legend)}</div></div>'
    X.clip(cid, t, d, frame(X, b, cid, world, big), "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_n", t, t + .5)
    t0 = t + .2                                # the crowd starts gathering at once and lands on the cue
    amt = min(max(.6, tn + .3 - t0), d - 1.0)
    X.tw(f'tl.fromTo("{s} .pr", {{y:46, scaleY:0, opacity:0, transformOrigin:"50% 100%"}}, {{y:0, scaleY:1, opacity:1, duration:0.4, ease:"back.out(3)", stagger:{{grid:[{rows},{cols}], from:"start", axis:"y", amount:{amt:.2f}}}}}, {t0:.3f});')
    wv = t0 + amt + .3
    if t + d - wv > .6:
        X.tw(f'tl.to("{s} .pr", {{keyframes:[{{y:-14, duration:0.16, ease:"power2.out"}}, {{y:0, duration:0.3, ease:"bounce.out"}}], stagger:{{grid:[{rows},{cols}], from:"start", axis:"x", amount:0.8}}}}, {wv:.3f});')
    counter(X, f"{s} .n", t0, 0, nv, dur=amt + .3, dec=int(b.get("dec", 0)), ease="power2.inOut")
    X.sfx(t0, "count")
    X.tw(f'tl.from("{s} .bigc > div:not(.lg)", {{x:-50, opacity:0, duration:0.5, ease:"back.out(1.8)", stagger:0.12}}, {t:.3f});')
    pop(X, s + " .lg", t + .5, -6)
    drift(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.12, .72 if not P else .5, .55 if not P else .6), (tn + .5, 1.0, .5, .5)])


def month(b, X, t, d, cid):
    """an oval track seen from the stands: riders lap it (nearer = bigger, they flip at the turns), a 30-day ring of tiles lights up;
    the monthly figure sits in the infield."""
    W, H, P = X.W, X.H, X.portrait
    cx, cy = (W * .64, H * .53) if not P else (W * .5, H * .5)
    rx, ry = (W * .27, H * .27) if not P else (W * .38, H * .15)
    days = int(b.get("days", 30))
    tiles = ""
    for i in range(days):
        a = -math.pi / 2 + 2 * math.pi * i / days
        x, y = cx + (rx + 52) * math.cos(a), cy + (ry + 44) * math.sin(a)
        tiles += f'<rect class="dy" x="{x - 14:.0f}" y="{y - 14:.0f}" width="28" height="28" rx="8" fill="{CREAM}" opacity=".3"/>'
    nr = int(b.get("riders", 6))
    lap = float(b.get("lap", 3.4))
    track = (f'<ellipse class="tk" cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="#1d8a76" stroke="{INK}" stroke-width="70"/>'
             f'<ellipse class="tk" cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="none" stroke="{CREAM}" stroke-width="3" stroke-dasharray="18 16" opacity=".6"/>')
    riders = "".join(f'<g class="lp lp{i}"><g transform="scale({.4 if not P else .36})">{rider(1, jacket=PAL[i % 4], box=PAL[(i + 2) % 5], body=PAL[(i + 1) % 5])}</g></g>' for i in range(nr))
    r = rnd(17)
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#7be0c8", "#48d1b2")}'
             f'{"".join(tree(x, y, k, "#2fb39a") for x, y, k in ((W * .06, H * .95, 1.4), (W * .95, H * .3, 1.0), (W * .3, H * .97, 1.1)))}'
             f'{track}{tiles}{riders}{floaters(X, r, 12, (CREAM, "#ffc94a"))}</svg>')
    mid = (f'<div class="mid" style="position:absolute; left:{cx - 320:.0f}px; top:{cy - 120:.0f}px; width:640px; text-align:center; color:var(--cream)">'
           f'<div style="font:700 30px var(--f-body)">{X.rich(b.get("kicker", ""))}</div>'
           f'<div><span class="num n" style="font-size:{numpx(b["n"], int(b.get("dec", 0)), min(560, rx * 1.5), 150 if not P else 136, b.get("unit", ""), 56)}px; color:var(--cream); text-shadow:0 6px 0 rgba(36,37,90,.35)">0</span>'
           f'<span style="font:900 56px var(--f-display)">{X.rich(b.get("unit", ""))}</span></div></div>')
    x0 = L(X)
    th, px, hh = title(X, b.get("title", ""), x0, H * .3 if not P else 290, W * (.28 if not P else .86), 300 if not P else 230, 76, 40, 3)
    X.clip(cid, t, d, frame(X, b, cid, world, th + mid, light=True), "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_n", t, t + .5)
    X.tw(f'tl.from("{s} .tk", {{scale:.5, opacity:0, transformOrigin:"50% 50%", duration:0.7, ease:"back.out(1.7)", stagger:0.08}}, {t:.3f});')
    X.tw(f'tl.to("{s} .dy", {{opacity:1, fill:"#ffc94a", duration:0.12, stagger:{max(.02, (d - 1.2) / days):.3f}}}, {t + .45:.3f});')
    K = 24
    for i in range(nr):
        th0 = 2 * math.pi * i / nr
        kfs = []
        for j in range(1, K + 1):     # clockwise from the viewer: the near (bottom) side runs left → right
            a = th0 - 2 * math.pi * j / K
            x, y = cx + rx * math.cos(a), cy + ry * math.sin(a)
            sc = .82 + .22 * (1 + math.sin(a)) / 2
            kfs.append(f'{{x:{x:.1f}, y:{y:.1f}, scaleX:{sc * (1 if math.sin(a) >= 0 else -1):.3f}, scaleY:{sc:.3f}, duration:{lap / K:.3f}, ease:"none"}}')
        x_0, y_0 = cx + rx * math.cos(th0), cy + ry * math.sin(th0)
        s0 = .82 + .22 * (1 + math.sin(th0)) / 2
        X.tw(f'tl.set("{s} .lp{i}", {{svgOrigin:"0 0", x:{x_0:.1f}, y:{y_0:.1f}, scaleX:{s0 * (1 if math.sin(th0) >= 0 else -1):.3f}, scaleY:{s0:.3f}}}, {t:.3f});')
        X.tw(f'tl.to("{s} .lp{i}", {{keyframes:[{", ".join(kfs)}], repeat:{max(0, int(d / lap))}}}, {t:.3f});')
        X.tw(f'tl.from("{s} .lp{i} > g", {{opacity:0, duration:0.2}}, {t + .2 + i * .08:.3f});')
    spin(X, f"{s} .wh", t, d, 2.0)
    counter(X, f"{s} .n", max(t + .2, tn - .4), 0, float(b["n"]), dur=1.0, dec=int(b.get("dec", 0)))
    X.sfx(max(t + .2, tn - .4), "count")
    X.tw(f'tl.from("{s} .mid", {{scale:.5, opacity:0, duration:0.55, ease:"back.out(2.2)"}}, {t + .25:.3f});')
    lines_in(X, s + " .ttl", t + .1)
    drift(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.06, .6 if not P else .5, .5), (t + d * .45, 1.0, .5, .5)])


def wallet(b, X, t, d, cid):
    """an income range: coins rain onto a low and a high stack (heights ∝ value), a range bar springs between them."""
    W, H, P = X.W, X.H, X.portrait
    lo, hi = float(b["lo"]), float(b["hi"])
    base = H * .7 if not P else H * .62
    xl, xh = (W * .52, W * .82) if not P else (W * .26, W * .74)
    cs = 60 if not P else 64
    stepc = cs * .42
    nh = int(b.get("coins", 14)); nl = max(1, round(nh * lo / hi))
    stack = lambda x, n, tag: "".join(coin(x + (-1) ** i * 3, base - i * stepc, cs, f"cn {tag}") for i in range(n))
    bar_y = base + 50
    bar = (f'<rect x="{xl:.0f}" y="{bar_y:.0f}" width="{xh - xl:.0f}" height="24" rx="12" fill="{INK}" opacity=".25"/>'
           f'<rect class="rb" x="{xl:.0f}" y="{bar_y:.0f}" width="{xh - xl:.0f}" height="24" rx="12" fill="#ff7a59"/>'
           f'<circle class="rk" cx="{xl:.0f}" cy="{bar_y + 12:.0f}" r="22" fill="{CREAM}" stroke="#ff7a59" stroke-width="8"/>'
           f'<circle class="rk" cx="{xh:.0f}" cy="{bar_y + 12:.0f}" r="22" fill="{CREAM}" stroke="#ff7a59" stroke-width="8"/>')
    r = rnd(29)
    spark = "".join(f'<path class="sk" d="M{x:.0f} {y - 16:.0f} L{x + 5:.0f} {y - 5:.0f} L{x + 16:.0f} {y:.0f} L{x + 5:.0f} {y + 5:.0f} L{x:.0f} {y + 16:.0f} L{x - 5:.0f} {y + 5:.0f} L{x - 16:.0f} {y:.0f} L{x - 5:.0f} {y - 5:.0f} Z" fill="{CREAM}"/>'
                    for x, y in ((xh + 80, base - nh * stepc - 20), (xh - 90, base - nh * stepc + 40), (xl + 70, base - nl * stepc - 10)))
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#ffd76a", "#ff9e6b")}'
             f'<circle cx="{W * .1:.0f}" cy="{H * .92:.0f}" r="{H * .3:.0f}" fill="#ffb35c" opacity=".6"/><circle cx="{W * .95:.0f}" cy="{H * .1:.0f}" r="{H * .2:.0f}" fill="#ffe08a" opacity=".6"/>'
             f'{street(X, H * .76, True) if P else purse(W * .17, H * .87, 1.0)}{stack(xl, nl, "cl")}{stack(xh, nh, "ch")}{bar}{spark}{floaters(X, r, 12, (CREAM, "#ff7a59"))}</svg>')
    unit = b.get("unit", "元")
    def lab(x, v, top, cls):
        return (f'<div class="card lab {cls}" style="left:{x - 140:.0f}px; top:{top:.0f}px; width:280px; padding:12px 0 14px">'
                f'<span class="num" style="font-size:56px">{X.rich(F.fmt_num(v, zh=False))}</span><small style="font:900 26px var(--f-display)"> {X.rich(unit)}</small></div>')
    labs = lab(xl, lo, base - nl * stepc - 140, "ll") + lab(xh, hi, base - nh * stepc - 140, "lh")
    x0 = L(X)
    top = H * .3 if not P else 290
    th, px, hh = title(X, b.get("title", ""), x0, top, W * (.36 if not P else .86), 300 if not P else 230, 84, 40, 3)
    ktop = top - 74 if not P else top + hh + 26
    kick = f'<div class="kick" style="left:{x0}px; top:{ktop:.0f}px; background:var(--cream)">{X.rich(b.get("kicker", ""))}</div>'
    X.clip(cid, t, d, frame(X, b, cid, world, labs + th + kick, light=True), "scene", 2)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .cl", {{y:-600, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"bounce.out", stagger:0.07}}, {t + .15:.3f});')
    X.tw(f'tl.fromTo("{s} .ch", {{y:-600, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"bounce.out", stagger:0.06}}, {t + .45:.3f});')
    X.tw(f'tl.fromTo("{s} .rb", {{scaleX:0, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:0.8, ease:"elastic.out(1, .6)"}}, {t + 1.2:.3f});')
    X.tw(f'tl.from("{s} .rk", {{scale:0, transformOrigin:"50% 50%", duration:0.4, ease:"back.out(3)", stagger:0.3}}, {t + 1.1:.3f});')
    X.tw(f'tl.from("{s} .ll", {{y:30, scale:.7, opacity:0, duration:0.45, ease:"back.out(2.4)"}}, {t + .15 + nl * .07:.3f});')
    X.tw(f'tl.from("{s} .lh", {{y:30, scale:.7, opacity:0, duration:0.45, ease:"back.out(2.4)"}}, {t + .45 + nh * .06:.3f});')
    X.tw(f'tl.fromTo("{s} .sk", {{scale:0, rotation:0, transformOrigin:"50% 50%"}}, {{scale:1, rotation:90, duration:0.5, ease:"back.out(3)", stagger:0.2, yoyo:true, repeat:{max(1, int((d - 1.6) / .5)) | 1}}}, {t + 1.4:.3f});')
    for k in range(4): X.sfx(t + .3 + k * .22, "click")
    if not P:
        drop(X, s + " .ps", t + .25, dur=.6)
        X.tw(f'tl.fromTo("{s} .wc", {{y:40, rotation:0}}, {{y:-70, rotation:200, duration:0.42, ease:"power2.out", yoyo:true, repeat:{max(1, int((d - 1.2) / .42)) | 1}, stagger:0.21}}, {t + .9:.3f});')
        X.tw(f'tl.to("{s} .ps", {{scaleY:.94, scaleX:1.04, transformOrigin:"50% 100%", duration:0.21, yoyo:true, repeat:{max(1, int((d - 1.2) / .42)) | 1}, ease:"sine.inOut"}}, {t + 1.0:.3f});')
    lines_in(X, s + " .ttl", t)
    pop(X, s + " .kick", t + .2, -6)
    drift(X, s, t, d)
    if P: street_go(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.1, .66 if not P else .5, .62), (t + 1.3, 1.0, .5, .5)])


def _spline(pts, n=14):
    """Catmull-Rom through pts → a dense polyline."""
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
    """the growth curve as a road up a hill: the area under it is the hillside, milestone signs stand at each year,
    a rider climbs while the camera follows; the forecast part of the road has a dashed gold centre line."""
    W, H, P = X.W, X.H, X.portrait
    marks = b["steps"]                       # [[year, value, label, future?], ...]  ("marks" is the engine's pointer key)
    ys = [float(m[0]) for m in marks]; vs = [float(m[1]) for m in marks]
    y0, y1 = ys[0] - .6, ys[-1] + .5
    xa, xb = (W * .04, W * .9) if not P else (W * .04, W * .86)
    ylo, yhi = (H * .86, H * .4) if not P else (H * .66, H * .44)
    vmax = max(vs)
    X_ = lambda yr: xa + (xb - xa) * (yr - y0) / (y1 - y0)
    Y_ = lambda v: ylo - (ylo - yhi) * v / vmax
    pts = [(xa - 80, Y_(vs[0] * .8))] + [(X_(y), Y_(v)) for y, v in zip(ys, vs)]
    poly = _spline(pts)
    seg = [0.0]
    for i in range(1, len(poly)): seg.append(seg[-1] + math.dist(poly[i - 1], poly[i]))
    Ltot = seg[-1]
    dpath = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly)
    fut = next((i for i, m in enumerate(marks) if len(m) > 3 and m[3]), len(marks))
    fi = min(range(len(poly)), key=lambda i: abs(poly[i][0] - X_(ys[fut - 1]))) if 0 < fut < len(marks) else len(poly) - 1
    dfut = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in poly[fi:])
    area = dpath + f" C{poly[-1][0] + 60:.0f} {poly[-1][1] - 6:.0f} {poly[-1][0] + 120:.0f} {poly[-1][1] + 10:.0f} {W + 40} {poly[-1][1] + 30:.0f} L{W + 40} {H} L{poly[0][0]:.0f} {H} Z"
    r = rnd(41)
    hills = (f'<path d="M0 {H * .62:.0f} Q{W * .25:.0f} {H * .44:.0f} {W * .5:.0f} {H * .6:.0f} T{W} {H * .5:.0f} L{W} {H} L0 {H} Z" fill="#b6a3ff" opacity=".7"/>'
             f'<path d="M0 {H * .74:.0f} Q{W * .3:.0f} {H * .6:.0f} {W * .6:.0f} {H * .72:.0f} T{W} {H * .66:.0f} L{W} {H} L0 {H} Z" fill="#8d74f0" opacity=".8"/>')
    signs = ""
    gap = min([X_(ys[i + 1]) - X_(ys[i]) for i in range(len(ys) - 1)] or [W])
    kb = max(.62, min(.9, gap / 230))        # crowded years → smaller signs, and alternate poles grow taller (below)
    tall = gap < 215 * kb
    for i, m in enumerate(marks):
        x, y = X_(ys[i]), Y_(vs[i])
        hot = i == len(marks) - 1
        k = min(1.25, kb * 1.4) if hot else kb
        fc, tc = ("#ff7a59", CREAM) if hot else (CREAM, INK)
        lift = 150 if tall and i % 2 == 1 and not hot else 0
        signs += (f'<g transform="translate({x:.0f},{y - 24:.0f}) scale({k:.2f})"><g class="sg sg{i}"><rect x="-5" y="{-120 - lift}" width="10" height="{120 + lift}" fill="{INK}"/>'
                  f'<rect x="-104" y="{-214 - lift}" width="208" height="102" rx="22" fill="{fc}"/>'
                  f'<text x="0" y="{-174 - lift}" text-anchor="middle" style="font-family:var(--f-num); font-weight:700; font-size:30px" fill="{tc}">{m[0]}{" · 预测" if i >= fut else ""}</text>'
                  f'<text x="0" y="{-128 - lift}" text-anchor="middle" style="font-family:var(--f-display); font-weight:900; font-size:38px" fill="{tc}">{m[2]}</text></g></g>')
        X.used_text.update(f"{m[0]}{m[2]} · 预测")
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#a68bfa", "#ffb38a")}'
             f'<circle class="sun" cx="{W * (.82 if not P else .22):.0f}" cy="{H * (.2 if not P else .36):.0f}" r="{min(W, H) * .1:.0f}" fill="#ffd76a"/>'
             + "".join(cloud(r.uniform(0, W), r.uniform(H * .08, H * .3), r.uniform(.6, 1.2), op=.6) for _ in range(5))
             + f'<g class="hh">{hills}</g><path d="{area}" fill="#48d1b2"/>'
             + "".join(tree(xa + 120 + j * 170, Y_(vs[0] * .8) + 150 + j * 40, .9, "#2fb39a") for j in range(2))
             + f'<path class="rd" d="{dpath}" fill="none" stroke="{INK}" stroke-width="54" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{Ltot:.0f} {Ltot + 10:.0f}" stroke-dashoffset="{Ltot:.0f}"/>'
             f'<g class="rcg" opacity="0"><path d="{dpath}" fill="none" stroke="{CREAM}" stroke-width="5" stroke-dasharray="22 18" opacity=".8"/>'
             f'<path d="{dfut}" fill="none" stroke="#ffc94a" stroke-width="7" stroke-dasharray="22 18"/></g>'
             f'{signs}<g class="rr"><g transform="scale({.5 if not P else .44})">{rider(1)}</g></g>'
             f'{floaters(X, r, 14, (CREAM,), (0, 0, 1, .5))}</svg>')
    x0 = L(X)
    th, px, hh = title(X, b.get("title", ""), x0, 140 if not P else 290, W * (.56 if not P else .86), 170, 78, 40, 2)
    X.clip(cid, t, d, frame(X, b, cid, world, th, light=True), "scene", 2)
    s = f"#{cid}"
    ride_d = min(d - .5, float(b.get("ride", d * .8)))
    t0 = t + .15
    X.tw(f'tl.to("{s} .rd", {{strokeDashoffset:0, duration:{ride_d:.2f}, ease:"sine.inOut"}}, {t0:.3f});')
    X.tw(f'tl.to("{s} .rcg", {{opacity:1, duration:0.3}}, {t0 + ride_d - .1:.3f});')
    def at(f):      # point + heading at fraction f of the road's length
        Lf = f * Ltot
        i = max(1, next((q for q in range(len(seg)) if seg[q] >= Lf), len(seg) - 1))
        u = (Lf - seg[i - 1]) / max(1e-6, seg[i] - seg[i - 1])
        x = poly[i - 1][0] + (poly[i][0] - poly[i - 1][0]) * u; y = poly[i - 1][1] + (poly[i][1] - poly[i - 1][1]) * u
        return x, y, math.degrees(math.atan2(poly[i][1] - poly[i - 1][1], poly[i][0] - poly[i - 1][0]))
    ease = lambda u: -(math.cos(math.pi * u) - 1) / 2     # sine.inOut, the road's own reveal ease → the rider leads the asphalt
    K = 30
    xs0, ys0, a0 = at(0)
    kfs = []
    for j in range(1, K + 1):
        x, y, ang = at(ease(j / K))
        kfs.append(f'{{x:{x:.1f}, y:{y:.1f}, rotation:{ang:.1f}, duration:{ride_d / K:.3f}, ease:"none"}}')
    X.tw(f'tl.set("{s} .rr", {{x:{xs0:.1f}, y:{ys0:.1f}, rotation:{a0:.1f}, svgOrigin:"0 0"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .rr", {{keyframes:[{", ".join(kfs)}]}}, {t0:.3f});')
    spin(X, f"{s} .wh", t, d, 1.8)
    bob(X, f"{s} .pp", t, d, 5, .3)
    for i in range(len(marks)):
        xi = X_(ys[i])
        q = min(range(len(poly)), key=lambda q: abs(poly[q][0] - xi))
        frac = seg[q] / Ltot
        u = math.acos(1 - 2 * min(1, max(0, frac))) / math.pi     # invert sine.inOut: when the rider reaches this sign
        ti = t0 + ride_d * u - .15
        X.tw(f'tl.from("{s} .sg{i}", {{scaleY:0, scaleX:.4, transformOrigin:"50% 100%", duration:0.5, ease:"elastic.out(1, .5)"}}, {ti:.3f});')
        X.sfx(ti, "pop" if i < len(marks) - 1 else "hit")
    X.tw(f'tl.to("{s} .hh", {{x:-60, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    lines_in(X, s + " .ttl", t)
    drift(X, s, t, d)
    cam(X, f"{s} .cam", t, d, [(t, 1.35, .14, .78 if not P else .7), (t0 + ride_d * .45, 1.18, .5, .6), (t0 + ride_d * .85, 1.0, .5, .5)])


def network(b, X, t, d, cid):
    """a top-down flat city: blocks, parks, a river; delivery routes draw on one by one with a courier dot running each,
    stores at the start, homes pulsing at the end."""
    W, H, P = X.W, X.H, X.portrait
    r = rnd(31)
    gx, gy = (12, 7) if not P else (7, 12)
    bw, bh = W / gx, H / gy
    blocks = ""
    for i in range(gx):
        for j in range(gy):
            c = r.choice(["#3a3c86", "#43459a", "#34367a", "#4b4fa8"])
            park = r.random() < .12
            blocks += f'<rect x="{i * bw + 12:.0f}" y="{j * bh + 12:.0f}" width="{bw - 24:.0f}" height="{bh - 24:.0f}" rx="14" fill="{"#2fb39a" if park else c}"/>'
            if park:
                blocks += "".join(f'<circle cx="{i * bw + r.uniform(34, bw - 34):.0f}" cy="{j * bh + r.uniform(34, bh - 34):.0f}" r="{r.uniform(12, 22):.0f}" fill="#5fe0c0"/>' for _ in range(4))
            if not park and r.random() < .6:
                blocks += f'<rect x="{i * bw + 30:.0f}" y="{j * bh + 30:.0f}" width="{(bw - 60) * r.uniform(.4, .9):.0f}" height="{(bh - 60) * r.uniform(.4, .9):.0f}" rx="8" fill="rgba(255,255,255,.07)"/>'
    river = (f'<path d="M-50 {H * .62:.0f} C{W * .3:.0f} {H * .5:.0f} {W * .6:.0f} {H * .85:.0f} {W + 50} {H * .7:.0f}" fill="none" stroke="#6c8cff" stroke-width="56" opacity=".8"/>'
             if not P else f'<path d="M{W * .7:.0f} -50 C{W * .5:.0f} {H * .3:.0f} {W * .9:.0f} {H * .6:.0f} {W * .6:.0f} {H + 50}" fill="none" stroke="#6c8cff" stroke-width="48" opacity=".8"/>')
    nr = int(b.get("routes", 14))
    routes, dots, pins, stores, paths = "", "", "", "", []
    for k in range(nr):
        i0, j0 = r.randrange(1, gx), r.randrange(1, gy)
        i1, j1 = min(gx - 1, max(1, i0 + r.choice([-4, -3, -2, 2, 3, 4]))), min(gy - 1, max(1, j0 + r.choice([-3, -2, 2, 3])))
        x0, y0, x1, y1 = i0 * bw, j0 * bh, i1 * bw, j1 * bh
        Ln = abs(x1 - x0) + abs(y1 - y0) + 1
        col = PAL[k % 4]
        routes += f'<path class="rt rt{k}" d="M{x0:.0f} {y0:.0f} L{x1:.0f} {y0:.0f} L{x1:.0f} {y1:.0f}" fill="none" stroke="{col}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{Ln:.0f} {Ln + 10:.0f}" stroke-dashoffset="{Ln:.0f}"/>'
        dots += f'<circle class="dt dt{k}" cx="0" cy="0" r="13" fill="{CREAM}" stroke="{col}" stroke-width="6" opacity="0"/>'
        stores += f'<g transform="translate({x0:.0f},{y0:.0f})"><g class="so so{k}"><rect x="-16" y="-16" width="32" height="32" rx="8" fill="{col}"/><rect x="-16" y="-16" width="32" height="10" rx="4" fill="{CREAM}" opacity=".7"/></g></g>'
        pins += (f'<g transform="translate({x1:.0f},{y1:.0f})"><g class="pn pn{k}"><circle class="pr{k}" r="30" fill="{col}" opacity=".35"/>'
                 f'<path d="M-14 4 L0 -12 L14 4 V16 H-14 Z" fill="{col}" stroke="{CREAM}" stroke-width="4" stroke-linejoin="round"/></g></g>')
        paths.append(((x0, y0, x1, y1), Ln))
    world = f'<svg class="ill" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="{INK}"/>{river}{blocks}{routes}{stores}{pins}{dots}</svg>'
    x0 = L(X)
    cw = W * .5 if not P else W - 2 * x0
    top = H * .5 if not P else 300
    th, px, hh = title(X, b.get("title", ""), 0, 0, cw - 80, 300 if not P else 330, 86 if not P else 92, 44, 3, sty="position:relative")
    card = f'<div class="card tc" style="left:{x0}px; top:{top:.0f}px; padding:30px 40px 34px; width:{cw:.0f}px">{th}</div>'
    X.clip(cid, t, d, frame(X, b, cid, world, card), "scene", 2)
    s = f"#{cid}"
    span = min(.38, max(.04, (d - 1.5) / nr))
    for k, ((ax, ay, bx, by), Ln) in enumerate(paths):
        tk = t + .15 + k * span
        X.tw(f'tl.from("{s} .so{k}", {{scale:0, transformOrigin:"50% 50%", duration:0.35, ease:"back.out(3)"}}, {tk - .1:.3f});')
        X.tw(f'tl.to("{s} .rt{k}", {{strokeDashoffset:0, duration:0.9, ease:"none"}}, {tk:.3f});')
        s1 = abs(bx - ax) / Ln
        X.tw(f'tl.set("{s} .dt{k}", {{x:{ax:.0f}, y:{ay:.0f}, opacity:1}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .dt{k}", {{keyframes:[{{x:{bx:.0f}, y:{ay:.0f}, duration:{.9 * s1 + .01:.2f}, ease:"none"}}, {{x:{bx:.0f}, y:{by:.0f}, duration:{.9 * (1 - s1) + .01:.2f}, ease:"none"}}]}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .dt{k}", {{scale:0, transformOrigin:"50% 50%", duration:0.2}}, {tk + .92:.3f});')
        X.tw(f'tl.from("{s} .pn{k}", {{scale:0, transformOrigin:"50% 100%", duration:0.45, ease:"back.out(3)"}}, {tk + .85:.3f});')
        reps = max(0, int((t + d - tk - 1.1) / .8))
        if reps: X.tw(f'tl.fromTo("{s} .pr{k}", {{scale:.6, opacity:.5, transformOrigin:"50% 50%"}}, {{scale:1.8, opacity:0, duration:0.8, ease:"sine.out", repeat:{reps - 1}}}, {tk + 1.1:.3f});')
    X.tw(f'tl.from("{s} .tc", {{y:60, scaleY:.6, transformOrigin:"50% 100%", opacity:0, duration:0.6, ease:"elastic.out(1, .55)"}}, {t + .3:.3f});')
    lines_in(X, s + " .tc", t + .45)
    X.sfx(t + .3, "enter")
    for k in range(0, nr, 3): X.sfx(t + .15 + k * span + .85, "pop")
    cam(X, f"{s} .cam", t, d, [(t, 1.25, .62, .45), (t + d * .45, 1.0, .5, .5)])


def outro(b, X, t, d, cid):
    W, H, P = X.W, X.H, X.portrait
    r = rnd(5)
    gl = H * (.86 if not P else .7)
    stars = "".join(f'<circle class="st" cx="{r.uniform(0, W):.0f}" cy="{r.uniform(0, H * .6):.0f}" r="{r.uniform(2, 5):.1f}" fill="{CREAM}" opacity="{r.uniform(.3, .9):.2f}"/>' for _ in range(60))
    city_ = skyline(W, gl, r, ["#3a3c86", "#43459a", "#34367a"], "#ffd98a", hmin=140, hmax=340)
    mr = min(W, H) * .08
    moon = (f'<g class="mo"><circle cx="{W * .8:.0f}" cy="{H * .22:.0f}" r="{mr:.0f}" fill="#ffc94a"/>'
            f'<circle cx="{W * .8 + mr * .45:.0f}" cy="{H * .22 - mr * .25:.0f}" r="{mr * .85:.0f}" fill="#34306f"/></g>')
    world = (f'<svg class="ill" viewBox="0 0 {W} {H}">{sky(X, cid, "#2b2c6b", "#5b4fa8")}{stars}{moon}<g class="oc">{city_}</g>'
             + (street(X, gl) if P else f'<rect x="0" y="{gl:.0f}" width="{W}" height="{H - gl:.0f}" fill="{INK}"/>'
                                         f'<g transform="translate(0,{gl + 70:.0f})"><g class="r1">{rider(.7)}</g></g>') + '</svg>')
    x0 = L(X)
    ui = (f'<div class="ob" style="position:absolute; left:{x0}px; top:{H * .26 if not P else 420:.0f}px">'
          f'<div class="ot" style="font:900 {136 if not P else 120}px/1.1 var(--f-display); color:var(--cream); text-shadow:0 8px 0 rgba(0,0,0,.25)">{X.rich(b.get("title", X.channel), split="chars")}</div>'
          f'<div class="os" style="font:700 40px var(--f-body); color:var(--cream); opacity:.85; margin-top:16px">{X.rich(b.get("sub", ""))}</div>'
          f'<div class="kick" style="position:relative; display:inline-block; margin-top:28px">{X.rich(b.get("cta", ""))}</div></div>')
    X.clip(cid, t, d, frame(X, b, cid, world, ui), "scene", 2)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .ot .c", {{y:80, scaleY:1.4, scaleX:.8, opacity:0, transformOrigin:"50% 100%", duration:0.55, ease:"back.out(2.6)", stagger:0.06}}, {t + .1:.3f});')
    X.tw(f'tl.from("{s} .os, {s} .ob .kick", {{y:30, opacity:0, duration:0.5, ease:"back.out(2)", stagger:0.15}}, {t + .5:.3f});')
    X.tw(f'tl.to("{s} .st", {{opacity:.15, duration:0.5, yoyo:true, repeat:{max(1, int(d / .5)) | 1}, stagger:{{each:0.03, from:"center"}}}}, {t:.3f});')
    X.tw(f'tl.from("{s} .oc", {{y:200, duration:0.9, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .mo", {{scale:0, transformOrigin:"50% 50%", duration:0.7, ease:"back.out(2)"}}, {t + .2:.3f});')
    if P: street_go(X, s, t, d)
    else:
        X.tw(f'tl.fromTo("{s} .r1", {{x:-300}}, {{x:{W + 300}, duration:{max(2.0, d):.2f}, ease:"none"}}, {t:.3f});')
        spin(X, f"{s} .r1 .wh", t, d); bob(X, f"{s} .r1 .pp", t, d)
    X.sfx(t + .1, "hit")


def _wrap(fn, focus):
    """every scene opens with the style's circle seam from its own focal point."""
    def run(b, X, t, d, cid):
        fx, fy = b.get("focus") or focus(X)
        bubble(X, cid, t, fx, fy)
        fn(b, X, t, d, cid)
    run.__doc__ = fn.__doc__
    return run


SCENES = {
    "city": _wrap(city, lambda X: (.5, .5)),
    "grow": _wrap(grow, lambda X: (.64, .7) if not X.portrait else (.72, .6)),
    "hero": _wrap(hero, lambda X: (.66, .6) if not X.portrait else (.5, .55)),
    "crowd": _wrap(crowd, lambda X: (.7, .5) if not X.portrait else (.5, .5)),
    "month": _wrap(month, lambda X: (.64, .53) if not X.portrait else (.5, .5)),
    "wallet": _wrap(wallet, lambda X: (.82, .5) if not X.portrait else (.74, .5)),
    "climb": _wrap(climb, lambda X: (.1, .8) if not X.portrait else (.1, .66)),
    "network": _wrap(network, lambda X: (.5, .5)),
    "outro": _wrap(outro, lambda X: (.5, .4)),
}


# ---------------------------------------------------------------- effects in this style (aefx beats: "scene": "fx")
# Four page themes, each a different illustrated world drawn behind the effect by FX_FRAME:
#   paper = dusk city · ink = night city · lemon = sunny park · red = coral sunset
STYLE["fx_themes"] = {
    "paper": {"bg": "#2b2c6b", "fg": "#fff6ea", "muted": "#c9c3e6", "accent": "#ff7a59", "card": "#fff6ea", "card-fg": "#24255a", "line": "rgba(255,246,234,.22)"},
    "ink":   {"bg": "#15173f", "fg": "#fff6ea", "muted": "#a3a7dc", "accent": "#48d1b2", "card": "#262a63", "card-fg": "#fff6ea", "line": "rgba(255,246,234,.16)"},
    "lemon": {"bg": "#ffe9b0", "fg": "#24255a", "muted": "#6b5a3a", "accent": "#e2553a", "card": "#ffffff", "card-fg": "#24255a", "line": "rgba(36,37,90,.18)"},
    "red":   {"bg": "#ff7a59", "fg": "#24255a", "muted": "rgba(36,37,90,.72)", "accent": "#24255a", "card": "#fff6ea", "card-fg": "#24255a", "line": "rgba(36,37,90,.25)"},
}
FX_WORLD = {"paper": ("#a68bfa", "dusk"), "ink": ("#2b2c6b", "night"), "lemon": ("#ffc58f", "park"), "red": ("#ffc94a", "sunset")}

STYLE["css"] = r"""
/* ---- effects (aefx) in flat: grounds come from FX_FRAME; the effect's own page paint goes transparent over them */
.st-flat .fx, .st-flat .ctx, .st-flat .flg { --f-mono: var(--f-num); }
.st-flat .flg { overflow:hidden; background:linear-gradient(180deg, var(--bg) 0%, var(--bg) 30%, color-mix(in srgb, var(--bg) 62%, var(--g2)) 100%); }
.st-flat .flg svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.st-flat .flg .s1 { fill:color-mix(in srgb, var(--fg) 6%, transparent); }
.st-flat .flg .s2 { fill:color-mix(in srgb, var(--fg) 11%, transparent); }
.st-flat .flg .wn { fill:color-mix(in srgb, #ffc94a 60%, transparent); }
.st-flat .flg .sun { fill:color-mix(in srgb, var(--g2) 70%, var(--bg)); }
.st-flat .flg .sun2 { fill:none; stroke:color-mix(in srgb, var(--g2) 60%, transparent); stroke-width:8; stroke-dasharray:4 30; stroke-linecap:round; }
.st-flat .flg .cl { fill:color-mix(in srgb, #ffffff 72%, transparent); }
.st-flat .flg .h1 { fill:color-mix(in srgb, #48d1b2 30%, var(--bg)); } .st-flat .flg .h2 { fill:color-mix(in srgb, #48d1b2 55%, var(--bg)); }
.st-flat .flg .h3 { fill:color-mix(in srgb, #24255a 16%, var(--bg)); } .st-flat .flg .h4 { fill:color-mix(in srgb, #24255a 30%, var(--bg)); }
.st-flat .flg .tr { fill:color-mix(in srgb, #2fb39a 70%, var(--bg)); } .st-flat .flg .tk { fill:color-mix(in srgb, #7a4b3a 70%, var(--bg)); }
.st-flat .flg .st { fill:var(--fg); }
.st-flat .flg .pt { fill:none; stroke:var(--fg); stroke-width:3.5; stroke-linecap:round; opacity:.35; }
.st-flat .flg .bd { fill:none; stroke:color-mix(in srgb, var(--fg) 60%, transparent); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
/* ---- the page around an effect */
.st-flat .ctx .flh { position:absolute; left:80px; right:80px; top:40px; height:48px; display:flex; align-items:center; justify-content:space-between; color:var(--fg); }
.st-flat .ctx .flh .l { display:flex; align-items:center; gap:12px; font:900 24px var(--f-display); }
.st-flat .ctx .flh .l i { width:30px; height:30px; border-radius:50%; background:#ffc94a; box-shadow:inset -6px -6px 0 rgba(0,0,0,.14); }
.st-flat .ctx .flh .tp { font:700 20px var(--f-body); padding:5px 16px 7px; border-radius:999px; background:color-mix(in srgb, var(--fg) 12%, transparent); }
.st-flat .ctx .flh .id { font:700 18px var(--f-num); color:#24255a; background:#ffc94a; padding:5px 16px 7px; border-radius:999px; box-shadow:0 4px 0 rgba(36,37,90,.3); }
.st-flat .ctx .cap { position:absolute; left:0; right:0; bottom:66px; text-align:center; }
.st-flat .ctx .cap > span { display:inline-block; font-family:var(--f-body); font-weight:700; line-height:1.3; color:#24255a; background:#fff6ea; padding:9px 30px 11px;
  border-radius:999px; box-shadow:0 6px 0 rgba(36,37,90,.32); max-width:80%; }
.st-flat .ctx .cap .em .emt { color:#24255a; padding:0 .12em; background:linear-gradient(#ffc94a, #ffc94a) no-repeat 0 82% / 100% 46%; }
.st-flat .ctx .cap .em .emb { display:none; }
.st-flat .ctx .flf { position:absolute; left:80px; right:80px; bottom:22px; display:flex; justify-content:space-between; gap:32px; font:500 16px var(--f-body); color:var(--fg); opacity:.72; }
.st-flat .ctx .flf > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; }
.st-flat .ctx.photo .flh, .st-flat .ctx.photo .flf { color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.6); opacity:1; }
.st-flat .ctx.photo .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(20,20,60,.55), rgba(0,0,0,0) 18%, rgba(0,0,0,0) 72%, rgba(20,20,60,.6)); }
#root.v.st-flat .ctx .flh { left:56px; right:56px; top:206px; } #root.v.st-flat .ctx .flf { left:56px; right:56px; bottom:auto; top:1478px; font-size:17px; }
#root.v.st-flat .ctx .cap { bottom:auto; top:1330px; padding:0 120px; } #root.v.st-flat .ctx .cap > span { max-width:100%; }
/* ---- effect internals, flat: rounder corners, flat offset shadows instead of blurred ones, palette blocks */
.st-flat .fx .cw, .st-flat .fx .wpi, .st-flat .fx .wpp-cd, .st-flat .fx .aq-card, .st-flat .fx .hp-card, .st-flat .fx .dl-c, .st-flat .fx .iv-q {
  border-radius:3.4vmin !important; box-shadow:0 1.3vmin 0 rgba(20,20,60,.26) !important; }
.st-flat .fx .pc-art, .st-flat .fx .th-pol, .st-flat .fx .iv-f, .st-flat .fx .iv-nb, .st-flat .fx .mx-card, .st-flat .fx .mx-c { border-radius:2.4vmin !important; box-shadow:0 1.3vmin 0 rgba(20,20,60,.28) !important; }
.st-flat .fx .mx-card img, .st-flat .fx .mx-c img, .st-flat .fx .iv-f video, .st-flat .fx .th-pol img { border-radius:inherit; }
.st-flat .fx .mx-hl { border-radius:2.4vmin !important; box-shadow:0 0 0 .8vmin #ffc94a, 0 1.6vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .pc-disc { box-shadow:0 1.3vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .wpr-pp { box-shadow:0 1.3vmin 0 rgba(20,20,60,.22) !important; border-radius:1.6vmin 1.6vmin 0 0; }
.st-flat .fx .wpr-slot { border-radius:2.4vmin !important; box-shadow:0 1vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .hp-bub b, .st-flat .fx .th-st.bubble b { border-radius:999px !important; box-shadow:0 .6vmin 0 rgba(20,20,60,.3) !important; }
.st-flat .fx .cw .bar i:nth-child(1) { background:#ff7a59; } .st-flat .fx .cw .bar i:nth-child(2) { background:#ffc94a; } .st-flat .fx .cw .bar i:nth-child(3) { background:#48d1b2; }
.st-flat .fx .cw .u { border-radius:3vmin 3vmin .8vmin 3vmin; } .st-flat .fx .cw .in { border:none; background:color-mix(in srgb, var(--card-fg) 7%, transparent); }
.st-flat .fx .cw .ab .hlm::before { background:#ffc94a; height:.5em; border-radius:.12em; }
.st-flat .fx .wpi-bb { border-radius:2.2vmin !important; } .st-flat .fx .wpi-av { border-radius:50% !important; }
.st-flat .fx .wpp-tg { border-radius:999px !important; padding-left:1.2vmin; padding-right:1.2vmin; }
.st-flat .fx .l3 .bar { width:1.4vmin; border-radius:1vmin; background:#ffc94a; }
.st-flat .fx .l3 .nm span { text-shadow:0 .6vmin 0 rgba(20,20,60,.25); }
.st-flat .fx .l3 .rl span { font-family:var(--f-body); font-weight:600; letter-spacing:.06em; }
.st-flat .fx .ti svg { fill:color-mix(in srgb, var(--fg) 14%, transparent); stroke-width:1.9; padding:1.4vmin; border-radius:50%; background:color-mix(in srgb, var(--fg) 9%, transparent); box-sizing:content-box; }
.st-flat .fx .ti .rg { border-color:#ffc94a; }
.st-flat .fx .aq-kick, .st-flat .fx .ct-kick { border-radius:999px !important; }
.st-flat .fx .th-set { background:radial-gradient(ellipse 50% 60% at var(--hx, 32%) 58%, color-mix(in srgb, #ffc94a 45%, transparent), transparent 70%) !important; }
.st-flat .fx .th-set::before { display:none; }
.st-flat .fx .th-st.tag b { color:#24255a; background:#ffc94a; border-radius:999px; box-shadow:0 .14em 0 rgba(36,37,90,.35); padding:.2em .7em; }
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
        moon = (f'<g class="fw-sun"><circle class="sun" cx="{mx:.0f}" cy="{sy:.0f}" r="{mr:.0f}" style="fill:#ffc94a"/>'
                f'<circle cx="{mx + mr * .42:.0f}" cy="{sy - mr * .26:.0f}" r="{mr * .86:.0f}" style="fill:var(--bg)"/></g>')
        body = (stars + moon + f'<g class="fw-1">{_sil(W, base - 10, r, "s1", 120, 300, win=True)}</g>'
                f'<g class="fw-2">{_sil(W, base + 20, r, "s2", 50, 150)}</g>' + ground)
    elif kind == "park":
        sun = (f'<g class="fw-sun"><circle class="sun" cx="{sx:.0f}" cy="{H * .16:.0f}" r="{min(W, H) * .09:.0f}" style="fill:#ffc94a"/>'
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
        sun = f'<circle class="sun fw-sun" cx="{sx:.0f}" cy="{base - H * .14:.0f}" r="{min(W, H) * .2:.0f}" style="fill:#ffc94a; opacity:.75"/>'
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
