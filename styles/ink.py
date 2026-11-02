"""ink · 水墨国风 —— 宣纸、墨的晕染、书法落笔、朱红印章、层叠远山和大面积留白。参照故宫、敦煌数字展陈与当代国风动态设计：
克制、透气、墨色有层次，不用渐变金、不用祥云贴图。墨的边缘用 SVG 湍流 + 位移滤镜做出洇开和飞白（固定种子，逐帧确定）。

场景（SCENES，全部自写）：brush 书法大字落笔 · column 竖排日期 + 题名 · drops 墨点洇开成人群 · scrolls 立轴展开的数字 ·
wash 一笔被水冲淡 · handscroll 手卷横移的年份 · splash 泼墨数字 · couplet 竖排对句 + 盖章 · seal 落款。
横屏竖屏各自排版；所有文字走 fit.py 自适应字号与断行。
"""
import math, random, re

from h9 import fit, fonts as h9fonts

STYLE = {
    "name": "水墨国风", "en": "Ink", "benchmarks": ["故宫数字展陈", "数字敦煌", "当代国风动态设计"],
    "tokens": {
        "bg": "#ebe3d1", "fg": "#171612", "muted": "#5a544a", "accent": "#b03a2e", "accent2": "#3d4a52", "alert": "#b03a2e",
        "line": "#cfc5ae", "paper": "#ebe3d1", "ink": "#171612", "card": "#f2ecdd", "card-fg": "#171612",
        "seal": "#b03a2e", "wash": "rgba(23,22,18,.10)", "mist": "rgba(245,240,229,.85)",
        "cap-bg": "rgba(239,232,216,.92)", "cap-fg": "#171612", "cap-size": "38px", "cap-weight": "600", "cap-pad": "6px 22px 9px",
        "cap-radius": "2px", "cap-shadow": "0 0 0 1px rgba(23,22,18,.12)", "cap-em": "#b03a2e", "cap-bottom": "46px",
        "punch-top": "70%", "punch-size": "60px", "punch-stroke": "0",
    },
    "fonts": {"display": "ma-shan-zheng", "body": "noto-serif-sc", "cap": "noto-serif-sc", "serif": "noto-serif-sc",
              "xing": "zhi-mang-xing", "cao": "liu-jian-mao-cao", "kai": "long-cang", "num": "eb-garamond", "latin": "eb-garamond"},
    "motion": {"ease": "power3.out", "dur": 0.8, "stagger": 0.05, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 110, "bottom": 70, "h": 300}, "portrait": {"left": 400, "bottom": 640, "h": 260}},
    "sfx": {"enter": ("whoosh_soft", 0.22), "brush": ("brush", 0.45), "stamp": ("hit", 0.35), "drop": ("pop", 0.25), "paper": ("paper", 0.35),
            "count": ("type", 0.2), "mascot": ("whoosh_soft", 0.22), "wash": ("whoosh_deep", 0.3)},
    "css": """
.st-ink .cap .cp { letter-spacing:.06em; }
#root.v.st-ink { --cap-bottom:516px; }
.st-ink .cap .em .emt { color:var(--seal); }
#root.v.st-ink .cap-punch .cp { font-weight:700; }
""",
}

CSS = r"""
.st-ink .em .emb { display:none; }
.ik { position:absolute; inset:0; overflow:hidden; background:var(--paper); color:var(--ink); }
.ik .cam { position:absolute; inset:0; }
.ik .paper { position:absolute; inset:0; pointer-events:none; }
.ik .paper svg { position:absolute; inset:0; width:100%; height:100%; }
.ik .vig { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 75% 70% at 50% 46%, rgba(0,0,0,0) 55%, rgba(60,45,20,.16) 100%); }
.ik .mist { position:absolute; border-radius:50%; background:radial-gradient(closest-side, var(--mist), rgba(245,240,229,0)); pointer-events:none; }
.ik .svgl { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.ik .bt { position:relative; }
.ik .bt .gl { position:absolute; overflow:visible; --m:0%;
  -webkit-mask-image:linear-gradient(176deg, #000 40%, rgba(0,0,0,0) 60%); mask-image:linear-gradient(176deg, #000 40%, rgba(0,0,0,0) 60%);
  -webkit-mask-size:100% 320%; mask-size:100% 320%; -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat;
  -webkit-mask-position:0 var(--m); mask-position:0 var(--m); }
.ik .bt path { fill:var(--ink); }
.ik .bt.red path { fill:var(--seal); }
.ik .serif { position:absolute; font-family:var(--f-serif); color:var(--ink); }
.ik .halo { text-shadow:0 0 10px var(--paper), 0 0 18px var(--paper), 0 0 3px var(--paper); }
.ik .vt { position:absolute; writing-mode:vertical-rl; font-family:var(--f-serif); letter-spacing:.18em; color:var(--ink); white-space:nowrap; }
.ik .num { position:absolute; font-family:var(--f-num); font-weight:600; color:var(--ink); font-variant-numeric:oldstyle-nums proportional-nums; white-space:nowrap; letter-spacing:.01em; }
.ik .seal { position:absolute; display:grid; place-items:center; background:var(--seal); color:var(--paper); border-radius:6px;
  font-family:var(--f-serif); font-weight:900; line-height:1; box-shadow:0 0 0 2px rgba(176,58,46,.25); }
.ik .seal .si { display:grid; grid-auto-flow:column; grid-template-rows:repeat(2, 1fr); direction:rtl; gap:2px 4px; }
.ik .seal.out { background:transparent; color:var(--seal); box-shadow:inset 0 0 0 5px var(--seal); }
.ik .hd { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-serif); color:var(--ink); z-index:6; }
.ik .hd b { font-weight:700; letter-spacing:.24em; } .ik .hd span { opacity:.55; letter-spacing:.2em; }
.ik .hd i { display:block; width:42px; height:2px; background:var(--ink); opacity:.6; }
.ik .idx { position:absolute; z-index:6; width:46px; height:46px; display:grid; place-items:center; font-family:var(--f-serif); font-weight:900;
  color:var(--paper); background:var(--seal); border-radius:4px; font-size:24px; }
.ik .ft { position:absolute; font-family:var(--f-serif); color:var(--muted); letter-spacing:.06em; z-index:6; white-space:nowrap;
  background:rgba(235,227,209,.85); padding:3px 10px; margin-left:-10px; border-radius:2px; }
.ik .rule { position:absolute; background:var(--ink); transform-origin:50% 0; }
.ik .card { position:absolute; background:var(--card); box-shadow:0 18px 40px rgba(60,45,20,.18), 0 0 0 1px rgba(23,22,18,.08); }
.ik .rod { position:absolute; background:linear-gradient(180deg, #4a3a2a, #2a2018); border-radius:6px; box-shadow:0 4px 10px rgba(0,0,0,.25); }
"""

NUMZH = "零壹贰叁肆伍陆柒捌玖拾"


# ---------------------------------------------------------------- helpers
def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def font_file(fid):
    meta = h9fonts.REG.get(fid, {})
    return h9fonts.find(meta.get("file", "")) if meta else None


_FONTS = {}


def _font(path):
    if path not in _FONTS:
        from fontTools.ttLib import TTFont
        f = TTFont(str(path))
        _FONTS[path] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    return _FONTS[path]


def glyph_d(path, ch, px, ox, oy):
    """one glyph as SVG path data in px, origin (ox, oy) = left end of the baseline; composites are decomposed.
    Returns (d, advance_px) or None when the font lacks the glyph."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    gs, cmap, upm = _font(path)
    name = cmap.get(ord(ch))
    if not name: return None
    k = px / upm
    pen = SVGPathPen(gs)
    gs[name].draw(TransformPen(pen, (k, 0, 0, -k, ox, oy)))
    return re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}", pen.getCommands()), gs[name].width * k


def brush(X, text, fid, px, cls="", flt=None):
    """text as real glyph outlines, one small <svg> per glyph, so each can be written on (a soft mask sweeps down
    the glyph like a loaded brush) and soaked with the scene's bleed filter. Returns (html, width_px, height_px).
    Glyphs the calligraphy font lacks come from the serif; a missing font file falls back to live text."""
    X.used_text.update(text)
    path = font_file(fid)
    h = px * 1.04
    if not path:
        w = sum(fit.gw(c) for c in text) * px
        spans = "".join(f'<span class="gl" style="position:relative">{X.rich(c)}</span>' for c in text)
        return f'<div class="bt {cls}" style="font-family:var(--f-display);font-size:{px}px;line-height:1;white-space:nowrap">{spans}</div>', w, h
    alt = font_file("noto-serif-sc")
    pad = px * 0.3
    x, out = 0.0, []
    for ch in text:
        if ch.isspace():
            x += px * 0.35; continue
        g = glyph_d(path, ch, px, pad, pad + px * 0.88) or (alt and glyph_d(alt, ch, px, pad, pad + px * 0.88))
        if not g:
            x += px * 0.5; continue
        d, adv = g
        f = f' filter="url(#{flt})"' if flt else ""
        out.append(f'<svg class="gl" width="{adv + 2 * pad:.0f}" height="{h + 2 * pad:.0f}" viewBox="0 0 {adv + 2 * pad:.0f} {h + 2 * pad:.0f}" '
                   f'style="left:{x - pad:.0f}px; top:{-pad:.0f}px"><path d="{d}"{f}/></svg>')
        x += adv
    return f'<div class="bt {cls}" style="width:{x:.0f}px; height:{h:.0f}px">{"".join(out)}</div>', x, h


def write_on(X, sel, t, dur=1.2, stagger=None):
    """calligraphy: each glyph is uncovered top-to-bottom by a soft-edged mask (the brush travelling down), settling
    from a slight swell and a wet blur into a crisp mark."""
    st = stagger if stagger is not None else 0.12
    X.tw(f'tl.fromTo("{sel} .gl", {{"--m":"100%"}}, {{"--m":"0%", duration:{dur * 0.75:.2f}, ease:"power1.inOut", stagger:{st}}}, {t:.3f});')
    X.tw(f'tl.fromTo("{sel} .gl", {{scale:1.05, filter:"blur(2.5px)"}}, {{scale:1, filter:"blur(0px)", duration:{dur:.2f}, ease:"power2.out", stagger:{st}}}, {t:.3f});')


def filters(cid, seed=3, scale=10, freq=0.03):
    """bleed: soft displaced edge (ink soaking into xuan paper); dry: broken flying-white edge for brush marks."""
    return (f'<svg width="0" height="0" style="position:absolute"><defs>'
            f'<filter id="{cid}b" x="-25%" y="-25%" width="150%" height="150%"><feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{scale}" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="0.6"/></filter>'
            f'<filter id="{cid}d" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.9 0.05" numOctaves="2" seed="{seed + 7}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.2 1.6" result="m"/>'
            f'<feComposite in="SourceGraphic" in2="m" operator="in"/></filter>'
            f'<filter id="{cid}w" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" seed="{seed + 3}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="0" xChannelSelector="R" yChannelSelector="G" class="wd"/><feGaussianBlur stdDeviation="0" class="wb"/></filter>'
            f'<filter id="{cid}k" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="2" seed="{seed + 11}" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G"/></filter>'
            f'</defs></svg>')


def paper(X):
    """xuan paper: fine fractal grain + a few long fibres + a soft vignette (same seed on every page so hard cuts feel continuous)."""
    W, H = X.W, X.H
    r = random.Random(41)
    fib = "".join(f'<path d="M{r.uniform(0, W):.0f} {r.uniform(0, H):.0f} q {r.uniform(-60, 60):.0f} {r.uniform(-30, 30):.0f} {r.uniform(-160, 160):.0f} {r.uniform(-50, 50):.0f}" '
                  f'stroke="rgba(120,100,70,{r.uniform(.05, .12):.2f})" stroke-width="{r.uniform(.6, 1.4):.1f}" fill="none"/>' for _ in range(70))
    return (f'<div class="paper"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><defs><filter id="pgrain"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="5"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .18  0 0 0 .22 0"/></filter></defs>'
            f'<rect width="{W}" height="{H}" filter="url(#pgrain)" opacity=".55"/>{fib}</svg></div><div class="vig"></div>')


def mountains(cid, X, seed, layers=3, top=0.45, amp=0.12, dark=0.85, width=None):
    """layered far mountains: noisy ridges filled with a wash that fades downward; each layer is a parallax group."""
    W, H = (width or X.W), X.H
    r = random.Random(seed)
    out = []
    for k in range(layers):
        base = H * (top + k * 0.09)
        a = H * amp * (1 - 0.18 * k)
        ph = [r.uniform(0, 6.283) for _ in range(5)]
        fr = [r.uniform(0.6, 1.4) * f for f in (1.5, 3.1, 6.3, 11.0, 23.0)]
        am = [1.0, 0.45, 0.22, 0.09, 0.04]
        pts = []
        n = 140
        for i in range(n + 1):
            x = W * i / n
            u = x / W * 6.283
            y = base - a * sum(am[j] * (0.5 + 0.5 * math.sin(fr[j] * u + ph[j])) for j in range(5)) / sum(am)
            pts.append(f"{x:.0f},{y:.0f}")
        op = dark * (0.35 + 0.65 * (k + 1) / layers)
        gid = f"{cid}g{k}"
        out.append(f'<g class="mt mt{k}"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                   f'<stop offset="0" stop-color="#171612" stop-opacity="{op:.2f}"/><stop offset="0.28" stop-color="#171612" stop-opacity="{op * 0.45:.2f}"/>'
                   f'<stop offset="0.7" stop-color="#171612" stop-opacity="0"/></linearGradient></defs>'
                   f'<path d="M0,{H} L{" L".join(pts)} L{W},{H} Z" fill="url(#{gid})" filter="url(#{cid}b)"/></g>')
    return f'<svg class="svgl" viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="width:{W}px">{"".join(out)}</svg>'


def mini_mts(cid, w, h, seed):
    """a small painted landscape for the head of a hanging scroll: two washed ridges and a vermilion sun."""
    r = random.Random(seed)
    out = []
    for k, (base, a, op) in enumerate(((0.62, 0.30, 0.13), (0.82, 0.24, 0.24))):
        ph = [r.uniform(0, 6.283) for _ in range(3)]
        pts = " L".join(f"{w * i / 40:.0f},{h * (base - a * (0.5 + 0.3 * math.sin(i / 40 * 7 + ph[0]) + 0.2 * math.sin(i / 40 * 17 + ph[1]))):.0f}" for i in range(41))
        out.append(f'<path d="M0,{h} L{pts} L{w:.0f},{h} Z" fill="#171612" fill-opacity="{op}" filter="url(#{cid}b)"/>')
    sun = f'<circle cx="{w * r.uniform(.22, .4):.0f}" cy="{h * 0.3:.0f}" r="{h * 0.09:.0f}" fill="#b03a2e" fill-opacity=".75"/>'
    return f'<svg class="mini" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" style="position:absolute; left:0; top:0">{sun}{"".join(out)}</svg>'


def mist(X, n=3, seed=9):
    r = random.Random(seed)
    W, H = X.W, X.H
    return "".join(f'<i class="mist m{k}" style="left:{r.uniform(-.2, .7) * W:.0f}px; top:{r.uniform(.25, .7) * H:.0f}px; width:{r.uniform(.5, .9) * W:.0f}px; height:{r.uniform(.12, .22) * H:.0f}px"></i>' for k in range(n))


def seal(X, text, size, cls="", style=""):
    """square vermilion seal; 1 glyph = big, 2 = stacked, 3–4 = right-to-left two columns."""
    X.used_text.update(text)
    n = len(text)
    if n <= 1: inner = f'<span style="font-size:{size * 0.62:.0f}px">{X.rich(text)}</span>'
    elif n == 2: inner = f'<span style="font-size:{size * 0.4:.0f}px; writing-mode:vertical-rl; letter-spacing:.06em">{X.rich(text)}</span>'
    else: inner = f'<span class="si" style="font-size:{size * 0.33:.0f}px">' + "".join(f"<i style='font-style:normal'>{X.rich(c)}</i>" for c in text[:4]) + "</span>"
    return f'<div class="seal {cls}" style="width:{size}px; height:{size}px; {style}">{inner}</div>'


def ganzhi(y):
    """a year as its sexagenary name (2018 → 戊戌), the way a seal or colophon would date it; non-years pass through."""
    try: y = int(y)
    except (TypeError, ValueError): return str(y)
    return "甲乙丙丁戊己庚辛壬癸"[(y - 4) % 10] + "子丑寅卯辰巳午未申酉戌亥"[(y - 4) % 12]


def stamp(X, sel, t):
    X.tw(f'tl.fromTo("{sel}", {{scale:1.35, opacity:0, rotation:-8}}, {{scale:1, opacity:1, rotation:-3, duration:0.32, ease:"back.out(2.4)"}}, {t:.3f});')
    X.sfx(t + 0.08, "stamp")


def counter(X, sel, t, a, b, dur=1.0, dec=0, sep=True):
    js = f"o.v.toFixed({dec})" if dec else ("Math.round(o.v).toLocaleString('en-US')" if sep else "String(Math.round(o.v))")
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power2.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def drift(X, sel, t, d, s=1.04, x=0, y=0):
    X.tw(f'tl.fromTo("{sel}", {{scale:1, x:0, y:0}}, {{scale:{s}, x:{x}, y:{y}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


def furn(X, b, cid, inner, extra_cls=""):
    """page: paper, header (channel + section), index seal, footnote, then the scene; opens through an ink bleed from the previous page."""
    X.css("ink", CSS)
    P = X.portrait
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "国风 · 商业")
    X.used_text.update(sec + "第九顶帽子" + NUMZH + "来源：")
    hx, hy, fs = (56, 206, 22) if P else (80, 44, 20)
    idx = NUMZH[(i + 1) % 11] if i + 1 <= 10 else str(i + 1)
    hd = (f'<div class="hd" style="left:{hx}px; top:{hy}px; font-size:{fs}px"><b>第九顶帽子</b><i></i><span>{X.rich(sec)}</span></div>'
          f'<div class="idx" style="right:{hx}px; top:{hy - 8}px">{idx}</div>')
    ft = ""
    src = b.get("src")
    if src:
        fy = 1470 if P else 1036
        ft = f'<div class="ft" style="left:{hx}px; top:{fy}px; font-size:{18 if P else 16}px">来源：{X.rich(src)}</div>'
    return f'<div class="ik {extra_cls}">{filters(cid)}{paper(X)}<div class="cam">{inner}</div>{hd}{ft}</div>'


def opening(X, cid, t):
    """the seam, drawn on top of the cut (no overlap needed): odd beats = an ink drop blooms over the old page and a hole
    opens in its centre onto the new one; even beats = one giant dry brush stroke sweeps across. Edges are displaced
    by low-frequency noise (blot) or streaky noise (brush hairs), seeded per beat so no two seams look alike."""
    i = X.beat["i"]
    if i == 0: return
    W, H = X.W, X.H
    tid = f"{cid}t"
    r = random.Random(100 + i)
    if i % 2:
        cx, cy = W * r.uniform(0.35, 0.65), H * r.uniform(0.38, 0.6)
        R = math.hypot(max(cx, W - cx), max(cy, H - cy)) + 160
        sat = "".join(f'<circle class="sa" cx="{cx + math.cos(a) * d:.0f}" cy="{cy + math.sin(a) * d:.0f}" r="{rr:.0f}" fill="white"/>'
                      for a, d, rr in ((r.uniform(0, 6.28), r.uniform(.25, .5) * min(W, H), r.uniform(18, 60)) for _ in range(7)))
        body = (f'<g filter="url(#{tid}f)"><circle class="o" cx="{cx:.0f}" cy="{cy:.0f}" r="0" fill="white"/>{sat}'
                f'<circle class="h" cx="{cx:.0f}" cy="{cy:.0f}" r="0" fill="black"/></g>')
        turb = f'<feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="3" seed="{20 + i}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="150" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="1.2"/>'
    else:
        L = W * 1.9
        body = (f'<g filter="url(#{tid}f)"><rect class="sw" x="{-L:.0f}" y="-80" width="{L:.0f}" height="{H + 160}" rx="{H * 0.4:.0f}" fill="white"/></g>')
        turb = f'<feTurbulence type="fractalNoise" baseFrequency="0.002 0.09" numOctaves="2" seed="{20 + i}" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="190" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="1.5"/>'
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;inset:0"><defs>'
           f'<filter id="{tid}f" x="-30%" y="-30%" width="160%" height="160%">{turb}</filter>'
           f'<radialGradient id="{tid}g" cx="50%" cy="50%" r="70%"><stop offset="0" stop-color="#121110"/><stop offset="1" stop-color="#2a2722"/></radialGradient>'
           f'<mask id="{tid}m" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="black"/>{body}</mask></defs>'
           f'<rect width="{W}" height="{H}" fill="url(#{tid}g)" mask="url(#{tid}m)"/></svg>')
    X.clip(tid, t - 0.36, 0.86, svg, "tr-ik", 40, track=7)
    s = f"#{tid}"
    if i % 2:
        X.tw(f'tl.fromTo("{s} .o", {{attr:{{r:0}}}}, {{attr:{{r:{R:.0f}}}, duration:0.36, ease:"power2.in"}}, {t - 0.36:.3f});')
        X.tw(f'tl.fromTo("{s} .sa", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.3, ease:"power2.out", stagger:0.02}}, {t - 0.3:.3f});')
        X.tw(f'tl.fromTo("{s} .h", {{attr:{{r:0}}}}, {{attr:{{r:{R + 200:.0f}}}, duration:0.48, ease:"power2.out"}}, {t + 0.02:.3f});')
        X.tw(f'tl.to("{s} .sa", {{opacity:0, duration:0.2}}, {t + 0.1:.3f});')
        X.sfx(t - 0.3, "drop")
    else:
        L = W * 1.9; dirn = 1 if (i // 2) % 2 else -1
        x0, x1 = (0, W + L) if dirn > 0 else (W + L, 0)
        if dirn < 0: X.tw(f'tl.set("{s} .sw", {{attr:{{x:{W:.0f}}}}}, {t - 0.36:.3f});')
        X.tw(f'tl.fromTo("{s} .sw", {{x:{(0 if dirn > 0 else 0):.0f}}}, {{x:{(W + L) * dirn:.0f}, duration:0.82, ease:"power2.inOut"}}, {t - 0.36:.3f});')
        X.sfx(t - 0.3, "brush")
    X.tw(f'tl.from("#{cid} > .stage > .ik .cam", {{scale:1.04, duration:0.7, ease:"power3.out"}}, {t:.3f});')


def ftext(X, text, box_w, max_px, min_px=None, lines=2, ls=0.0):
    """serif copy fitted to a width: (px, html with <br> between balanced lines)."""
    f = fit.fit_text(fit.as_text(text), box_w, max_px * 1.3 * lines, max_px, min_px or max_px * 0.65, lh=1.3, max_lines=lines, ls=ls)
    return f.px, "<br>".join(X.rich(l) for l in f.lines)


def fitpx(text, box_w, max_px, min_px=None, lines=1, lh=1.1):
    f = fit.fit_text(fit.as_text(text), box_w, max_px * lh * lines, max_px, min_px or max_px * 0.4, lh=lh, max_lines=lines)
    return f


# ---------------------------------------------------------------- scenes
def brush_scene(b, X, t, d, cid):
    """hook: far mountains drift; a huge calligraphy word is written; a vertical kicker and a seal frame it."""
    P = X.portrait; W, H = X.W, X.H
    word = b.get("big", "千万")
    kick = b.get("kicker", "")
    sub = b.get("sub", "")
    box_w = W * (0.70 if P else 0.54)
    px = min(H * (0.24 if P else 0.36), box_w / max(1, sum(fit.gw(c) for c in word)))
    svg, bw, bh = brush(X, word, b.get("font", "ma-shan-zheng"), px, flt=f"{cid}k")
    bx = W - bw - 70 if P else W * 0.40
    by = H * 0.25 if P else H * 0.15
    kx = 80 if P else W * 0.16
    ky = by - (110 if P else -20)
    vt_fs = min(46 if P else 44, ((by + bh - ky) if P else H * 0.6) / max(1, len(kick)) / 1.2)
    ssz = 92 if P else 104
    sl = "" if not b.get("seal") else seal(X, b["seal"], ssz, style=f"left:{min(bx + bw - ssz * 0.55, W - 60 - ssz):.0f}px; top:{by + bh - ssz * 0.7:.0f}px; transform:rotate(-3deg)")
    if sub:
        sfs, shtml = ftext(X, sub, W - 160 if P else box_w, 38 if P else 34, 24, ls=0.14)
        subh = (f'<div class="serif sub halo" style="left:80px; right:80px; top:{by + bh + (90 if P else 60):.0f}px; font-size:{sfs}px; font-weight:600; letter-spacing:.14em; line-height:1.3; text-align:center">{shtml}</div>'
                if P else f'<div class="serif sub halo" style="left:{bx:.0f}px; top:{by + bh + 50:.0f}px; width:{box_w:.0f}px; font-size:{sfs}px; font-weight:600; letter-spacing:.14em; line-height:1.3">{shtml}</div>')
    else: subh = ""
    inner = (f'<div class="mtl" style="position:absolute;inset:0">{mountains(cid, X, 11, layers=3, top=0.62 if P else 0.64, amp=0.13)}</div>{mist(X, 3)}'
             f'<div class="vt kick" style="left:{kx:.0f}px; top:{ky:.0f}px; font-size:{vt_fs}px; font-weight:600">{X.rich(kick)}</div>'
             f'<div class="word" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>{sl}{subh}')
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    tw_ = T(X, b, "at_big", t, t + 0.6)
    ts = T(X, b, "at_seal", t, tw_ + 0.9)
    opening(X, cid, t)
    for k in range(3):
        X.tw(f'tl.fromTo("{s} .mt{k}", {{x:0}}, {{x:{-30 - 30 * k}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .mtl", {{opacity:0, y:40, duration:1.4, ease:"power2.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .mist", {{x:-60, opacity:0}}, {{x:80, opacity:1, duration:{d:.2f}, ease:"sine.inOut", stagger:0.3}}, {t:.3f});')
    X.tw(f'tl.from("{s} .kick", {{opacity:0, y:-30, duration:0.8, ease:"power3.out"}}, {t + 0.15:.3f});')
    write_on(X, f"{s} .word", tw_ - 0.25, dur=1.3, stagger=0.18)
    X.sfx(tw_ - 0.2, "brush")
    if sl: stamp(X, f"{s} .seal", ts)
    if sub: X.tw(f'tl.from("{s} .sub", {{opacity:0, y:16, duration:0.7}}, {ts + 0.2:.3f});')
    drift(X, f"{s} .cam", t, d, 1.05, -20 if not P else 0, -10)


def column(b, X, t, d, cid):
    """a date runs down a vertical column glyph by glyph; the title is written in running script beside it; a red hairline drops."""
    P = X.portrait; W, H = X.W, X.H
    date = b.get("date", "")
    title = b.get("title", "")
    vfs = 52 if P else 48
    title_box = W * (0.82 if P else 0.6)
    px = min(H * (0.16 if P else 0.22), title_box / max(1, sum(fit.gw(c) for c in title)))
    svg, tw, th = brush(X, title, b.get("font", "zhi-mang-xing"), px, flt=f"{cid}k")
    cx = W * 0.78 if not P else W * 0.80
    tx = (W - tw) / 2 if P else W * 0.12
    ty = H * 0.53 if P else H * 0.36
    dchars = "".join(f'<span class="dc">{X.rich(c)}</span>' for c in date)
    note = b.get("note", "")
    inner = (f'<div class="mtl" style="position:absolute;inset:0;opacity:.55">{mountains(cid, X, 23, layers=2, top=0.66, amp=0.09, dark=0.6)}</div>{mist(X, 2, 4)}'
             f'<i class="rule" style="left:{cx - 34:.0f}px; top:{H * (0.17 if P else 0.18):.0f}px; width:2px; height:{H * (0.33 if P else 0.6):.0f}px; background:var(--seal)"></i>'
             f'<div class="vt dt" style="left:{cx:.0f}px; top:{H * (0.17 if P else 0.18):.0f}px; font-size:{vfs}px; font-weight:600">{dchars}</div>'
             f'<div class="title" style="position:absolute; left:{tx:.0f}px; top:{ty:.0f}px">{svg}</div>'
             + (f'<div class="serif note" style="left:{tx:.0f}px; top:{ty + th + 30:.0f}px; font-size:{30 if P else 28}px; letter-spacing:.14em; color:var(--muted)">{X.rich(note)}</div>' if note else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    ttl = T(X, b, "at_title", t, t + d * 0.45)
    opening(X, cid, t)
    X.tw(f'tl.from("{s} .rule", {{scaleY:0, duration:0.9, ease:"power3.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .dc", {{opacity:0, y:-18, filter:"blur(6px)", duration:0.45, ease:"power2.out", stagger:{min(0.12, (ttl - t - 0.2) / max(1, len(date))):.3f}}}, {t + 0.2:.3f});')
    write_on(X, f"{s} .title", ttl - 0.3, dur=1.4, stagger=0.09)
    X.sfx(ttl - 0.25, "brush")
    if note: X.tw(f'tl.from("{s} .note", {{opacity:0, x:-20, duration:0.6}}, {ttl + 0.9:.3f});')
    X.tw(f'tl.fromTo("{s} .mist", {{x:60}}, {{x:-90, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.04, 0, -12)


def drops(b, X, t, d, cid):
    """people as ink drops: each dot is N people; they bleed outward from one point like ink soaking into paper; a counter runs."""
    P = X.portrait; W, H = X.W, X.H
    total = float(b.get("value", 3000000)); per = float(b.get("per", 1000))
    n = int(min(3200, max(30, round(total / per))))
    r = random.Random(7)
    cx, cy = (W * 0.5, H * 0.33) if P else (W * 0.655, H * 0.50)
    R = (W * 0.34) if P else (H * 0.40)
    pts = []
    for k in range(n):
        a = r.uniform(0, 6.283)
        rr = R * math.sqrt(r.random()) * (0.85 + 0.15 * math.sin(3 * a + 1.3) + 0.08 * math.sin(7 * a))
        pts.append((cx + rr * math.cos(a) * (1.25 if not P else 1.0), cy + rr * math.sin(a) * (0.9 if not P else 0.95), rr))
    pts.sort(key=lambda p: p[2])
    dots = "".join(f'<circle class="dp" cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(2.2, 4.6):.1f}" fill="#171612" fill-opacity="{r.uniform(.45, .95):.2f}"/>' for x, y, _ in pts)
    unit = b.get("unit", "万人"); label = b.get("label", ""); kicker = b.get("kicker", "")
    show = float(b.get("show", total / 10000)); dec = int(b.get("dec", 0))
    col_w = W - 160 if P else W * 0.29
    nfs = min(160 if P else 190, col_w / (sum(fit.gw(c) for c in f"{show:,.{dec}f}") * 1.05 + 0.42 * len(unit) + 0.12))
    lfs, lhtml = ftext(X, label, col_w, 26 if P else 24, 18, ls=0.12)
    nx, ny = (W * 0.5, H * 0.565) if P else (W * 0.10, H * 0.40)
    align = "center" if P else "left"
    inner = (f'<svg class="svgl" viewBox="0 0 {W} {H}"><g filter="url(#{cid}b)">{dots}</g>'
             f'<circle class="core" cx="{cx:.0f}" cy="{cy:.0f}" r="26" fill="#171612" filter="url(#{cid}b)"/></svg>'
             f'<div class="serif kk" style="left:{0 if P else nx:.0f}px; {"right:0;" if P else ""} top:{ny - (70 if P else 80):.0f}px; font-size:{34 if P else 32}px; letter-spacing:.2em; text-align:{align}">{X.rich(kicker)}</div>'
             f'<div class="num big" style="left:{0 if P else nx:.0f}px; {"right:0;" if P else ""} top:{ny:.0f}px; font-size:{nfs:.0f}px; line-height:.9; text-align:{align}"><span class="n">0</span>'
             f'<span style="font-family:var(--f-serif); font-weight:900; font-size:.42em; margin-left:.12em">{X.rich(unit)}</span></div>'
             f'<div class="serif lb" style="left:{0 if P else nx:.0f}px; {"right:0;" if P else ""} top:{ny + nfs * 0.9 + 22:.0f}px; {"" if P else f"width:{col_w:.0f}px; "}font-size:{lfs}px; line-height:1.3; letter-spacing:.12em; color:var(--muted); text-align:{align}">{lhtml}</div>')
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + 0.6)
    opening(X, cid, t)
    X.tw(f'tl.from("{s} .core", {{attr:{{r:0}}, duration:0.5, ease:"back.out(2)"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "drop")
    spread = max(1.2, min(d - 0.8, tn - t + 1.0))
    X.tw(f'tl.from("{s} .dp", {{attr:{{r:0}}, duration:0.5, ease:"power2.out", stagger:{{each:{spread / n:.5f}}}}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .kk", {{opacity:0, y:12, duration:0.6}}, {t + 0.1:.3f});')
    tc = max(t + 0.3, tn - 0.5)
    X.tw(f'tl.from("{s} .big", {{opacity:0, y:20, duration:0.4, ease:"power2.out"}}, {tc:.3f});')
    counter(X, f"{s} .n", tc, 0, show, dur=1.3, dec=dec)
    X.sfx(tn - 0.4, "count")
    X.tw(f'tl.from("{s} .lb", {{opacity:0, duration:0.6}}, {tn + 0.8:.3f});')
    drift(X, f"{s} .cam", t, d, 1.05, 0, 0)


def scrolls(b, X, t, d, cid):
    """1–3 hanging scrolls unroll from their top rods; each holds a figure and a vertical label; seals mark estimates."""
    P = X.portrait; W, H = X.W, X.H
    items = b.get("items", [])[:3] or [{"value": "—", "label": ""}]
    n = len(items)
    gap = 40 if P else 70
    sw = min((W - (2 * 70 if P else 2 * 180) - gap * (n - 1)) / n, 520)
    sh = H * (0.46 if P else 0.58)
    x0 = (W - (n * sw + (n - 1) * gap)) / 2
    y0 = H * (0.17 if P else 0.12)
    html = []
    for k, it in enumerate(items):
        x = x0 + k * (sw + gap)
        val = str(it.get("value", "")); unit = it.get("unit", ""); lab = it.get("label", ""); sl = it.get("seal", "")
        fpx = fitpx(val, sw * 0.78, 132 if P else 150, 48).px
        html.append(f'<div class="scr s{k}" style="position:absolute; left:{x:.0f}px; top:{y0:.0f}px; width:{sw:.0f}px; height:{sh:.0f}px">'
                    f'<div class="rod rt" style="left:-16px; right:-16px; top:-14px; height:22px"></div>'
                    f'<div class="body card" style="left:0; right:0; top:0; height:{sh:.0f}px; transform-origin:50% 0">'
                    f'<div style="position:absolute; left:{sw * 0.06:.0f}px; top:{sh * 0.05:.0f}px; width:{sw * 0.88:.0f}px; height:{sh * 0.34:.0f}px; overflow:hidden">{mini_mts(cid, sw * 0.88, sh * 0.34, 70 + k)}</div>'
                    f'<div class="vt lab halo" style="right:{sw * 0.1:.0f}px; top:{sh * 0.08:.0f}px; font-size:{30 if P else 30}px; font-weight:600">{X.rich(lab)}</div>'
                    f'<div class="num" style="left:{sw * 0.08:.0f}px; top:{sh * 0.50:.0f}px; font-size:{fpx:.0f}px; line-height:1">{X.rich(val)}</div>'
                    f'<div class="serif" style="left:{sw * 0.09:.0f}px; top:{sh * 0.50 + fpx * 1.05:.0f}px; font-size:{40 if P else 42}px; font-weight:900">{X.rich(unit)}</div>'
                    + (seal(X, sl, 64, style=f"right:{sw * 0.08:.0f}px; top:{sh * 0.76:.0f}px; transform:rotate(-3deg)") if sl else "") +
                    f'</div><div class="rod rb" style="left:-12px; right:-12px; top:{sh - 8:.0f}px; height:20px"></div></div>')
    note = b.get("note", "")
    inner = (mist(X, 2, 12) + "".join(html) + (f'<div class="serif nt" style="left:0; right:0; top:{y0 + sh + 50:.0f}px; text-align:center; font-size:{26 if P else 24}px; letter-spacing:.12em; color:var(--muted)">{X.rich(note)}</div>' if note else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    ats = [T(X, b, f"at_{k}", t, t + 0.4 + k * 0.9) for k in range(n)]
    for k, ta in enumerate(ats):
        st = min(t + 0.12 + k * 0.35, ta - 1.0)                    # the scroll hangs and unrolls straight away …
        X.tw(f'tl.from("{s} .s{k}", {{opacity:0, y:-30, duration:0.4}}, {st:.3f});')
        X.tw(f'tl.from("{s} .s{k} .body", {{scaleY:0, duration:0.9, ease:"power3.inOut"}}, {st + 0.1:.3f});')
        X.tw(f'tl.from("{s} .s{k} .rb", {{y:{-sh + 8:.0f}, duration:0.9, ease:"power3.inOut"}}, {st + 0.1:.3f});')
        X.tw(f'tl.from("{s} .s{k} .lab", {{opacity:0, y:-14, duration:0.6}}, {st + 0.7:.3f});')
        X.tw(f'tl.from("{s} .s{k} .num, {s} .s{k} .serif", {{opacity:0, y:18, filter:"blur(6px)", duration:0.55, ease:"power3.out", stagger:0.1}}, {ta - 0.15:.3f});')   # … the figure lands on its word
        X.tw(f'tl.from("{s} .s{k} .seal", {{scale:1.35, opacity:0, duration:0.3, ease:"back.out(2.4)"}}, {ta + 0.45:.3f});')
        X.sfx(st + 0.1, "paper"); X.sfx(ta + 0.5, "stamp")
    if note: X.tw(f'tl.from("{s} .nt", {{opacity:0, y:10, duration:0.6}}, {t + 0.5:.3f});')
    X.tw(f'tl.fromTo("{s} .scr", {{rotation:0}}, {{rotation:0.6, duration:{d / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1, transformOrigin:"50% 0"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.035, 0, -8)


def wash(b, X, t, d, cid):
    """a word is written, held, then water washes through it: the ink loosens (displacement + blur) and fades."""
    P = X.portrait; W, H = X.W, X.H
    word = b.get("big", "运气"); kick = b.get("kicker", "")
    box = W * (0.7 if P else 0.5)
    px = min(H * (0.28 if P else 0.38), box / max(1, sum(fit.gw(c) for c in word)))
    svg, bw, bh = brush(X, word, b.get("font", "liu-jian-mao-cao"), px, flt=f"{cid}k")
    bx, by = (W - bw) / 2, H * (0.30 if P else 0.26)
    inner = (f'<div class="serif kk" style="left:0; right:0; top:{by - (110 if P else 90):.0f}px; text-align:center; font-size:{40 if P else 38}px; letter-spacing:.3em">{X.rich(kick)}</div>'
             f'<div class="wd" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px; filter:url(#{cid}w)">{svg}</div>{mist(X, 2, 21)}')
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    tw_ = T(X, b, "at_big", t, t + 0.5)
    X.tw(f'tl.from("{s} .kk", {{opacity:0, y:-14, filter:"blur(6px)", duration:0.8, ease:"power2.out"}}, {t + 0.1:.3f});')
    write_on(X, f"{s} .wd", tw_ - 0.25, dur=1.0, stagger=0.15)
    X.sfx(tw_ - 0.2, "brush")
    tx = T(X, b, "at_wash", t, min(t + d - 0.9, tw_ + 1.2))
    X.tw(f'tl.to("{s} .wd", {{opacity:0.08, duration:0.9, ease:"power2.in"}}, {tx:.3f});')
    X.tw(f'tl.to("{s} feDisplacementMap.wd", {{attr:{{scale:90}}, duration:0.9, ease:"power2.in"}}, {tx:.3f});')
    X.tw(f'tl.to("{s} feGaussianBlur.wb", {{attr:{{stdDeviation:10}}, duration:0.9, ease:"power2.in"}}, {tx:.3f});')
    X.tw(f'tl.fromTo("{s} .mist", {{x:-W * 0.4, opacity:0}}, {{x:W * 0.2, opacity:1, duration:1.2, ease:"power2.out", stagger:0.15}}, {tx - 0.2:.3f});'.replace("W * 0.4", f"{W * 0.4:.0f}").replace("W * 0.2", f"{W * 0.2:.0f}"))
    X.sfx(tx, "wash")
    drift(X, f"{s} .cam", t, d, 1.05)


def handscroll(b, X, t, d, cid):
    """a long handscroll pans right-to-left: a ridge with year seals along it, an ink line travels the ridge, then the span is written big."""
    P = X.portrait; W, H = X.W, X.H
    years = [str(y) for y in b.get("years", [2018, 2024])]
    labels = {str(k): v for k, v in (b.get("labels") or {}).items()}
    n = len(years)
    LW = W * (2.4 if not P else 3.0)
    r = random.Random(31)
    base = H * (0.52 if P else 0.56)
    pts = []
    for i in range(161):
        x = LW * i / 160
        y = base - H * 0.08 * (0.5 + 0.5 * math.sin(x / LW * 9.4 + 0.7)) - H * 0.03 * math.sin(x / LW * 31 + 2)
        pts.append((x, y))
    line = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    big = b.get("big", "六年"); kick = b.get("kicker", "")
    px = min(H * (0.19 if P else 0.30), W * (0.70 if P else 0.42) / max(1, sum(fit.gw(c) for c in big)))
    svg, bw, bh = brush(X, big, b.get("font", "ma-shan-zheng"), px, flt=f"{cid}k")
    bx, by = (W - bw) / 2 + (40 if P else 0) if P else W * 0.56, H * (0.20 if P else 0.14)
    marks = []
    for k, yv in enumerate(years):
        x = LW * (0.12 + 0.76 * k / max(1, n - 1))
        y = min(pts, key=lambda p: abs(p[0] - x))[1]
        up = (not P) and k % 2 and x - (LW - W) + 70 < bx - 30      # never park a seal under the title where the pan ends
        lab = labels.get(yv, "")
        gz = ganzhi(yv)
        marks.append(f'<div class="ym y{k}" style="position:absolute; left:{x - 70:.0f}px; top:{y + (-225 if up else 34 + (30 * (k % 2) if P else 0)):.0f}px; width:140px; text-align:center">'
                     f'{seal(X, gz, 90, cls="" if lab else "out", style="position:relative; margin:0 auto")}'
                     f'<div class="num" style="position:relative; font-size:40px; margin-top:8px">{X.rich(yv)}</div>'
                     + (f'<div class="serif" style="position:relative; font-size:28px; font-weight:700; letter-spacing:.2em; color:var(--seal)">{X.rich(lab)}</div>' if lab else "")
                     + '</div>')
    inner = (f'<div class="strip" style="position:absolute; left:0; top:0; width:{LW:.0f}px; height:{H}px">'
             f'<div style="position:absolute;inset:0;opacity:.5">{mountains(cid, X, 37, layers=2, top=0.62, amp=0.1, dark=0.55, width=LW)}</div>'
             f'<div class="trw" style="position:absolute; left:0; top:0; width:{LW:.0f}px; height:{H}px"><svg class="svgl" viewBox="0 0 {LW:.0f} {H}" style="width:{LW:.0f}px">'
             f'<path class="trail" d="{line}" fill="none" stroke="#171612" stroke-width="6" stroke-linecap="round" filter="url(#{cid}b)"/></svg></div>'
             f'{"".join(marks)}</div>'
             f'<div class="big" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>'
             + (f'<div class="vt kk halo" style="left:{80 if P else 150}px; top:{H * (0.17 if P else 0.15):.0f}px; font-size:{40 if P else 38}px; font-weight:600">{X.rich(kick)}</div>' if kick else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    tb = T(X, b, "at_big", t, t + d * 0.6)
    pan = min(d - 0.4, max(1.5, tb - t + 0.6))
    X.tw(f'tl.fromTo("{s} .strip", {{x:0}}, {{x:{-(LW - W):.0f}, duration:{pan:.2f}, ease:"power1.inOut"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .trw", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{pan:.2f}, ease:"power1.inOut"}}, {t:.3f});')
    if kick: X.tw(f'tl.from("{s} .kk", {{opacity:0, y:-20, filter:"blur(6px)", duration:0.7, ease:"power2.out"}}, {t + 0.2:.3f});')
    for k in range(n):
        tk = t + pan * (0.12 + 0.76 * k / max(1, n - 1)) * 0.9
        X.tw(f'tl.from("{s} .y{k}", {{scale:1.4, opacity:0, duration:0.3, ease:"back.out(2.2)"}}, {tk:.3f});')
        X.sfx(tk + 0.05, "stamp")
    write_on(X, f"{s} .big", tb - 0.3, dur=1.2, stagger=0.2)
    X.sfx(tb - 0.25, "brush")


def splash(b, X, t, d, cid):
    """a figure lands with a splash of ink behind it; a quiet serif note gives the source."""
    P = X.portrait; W, H = X.W, X.H
    big = b.get("big", ""); kick = b.get("kicker", ""); note = b.get("note", "")
    px = min(H * (0.22 if P else 0.30), W * (0.82 if P else 0.6) / max(1, sum(fit.gw(c) for c in big)))
    svg, bw, bh = brush(X, big, b.get("font", "ma-shan-zheng"), px, flt=f"{cid}k")
    bx, by = (W - bw) / 2, H * (0.32 if P else 0.30)
    r = random.Random(17)
    cx, cy = W / 2, by + bh * 0.52
    ex, ey = bw * 0.56, bh * 0.62                       # the splash core; drops fly out past its rim
    drops = []
    for _ in range(int(b.get("drops", 72))):
        a = r.uniform(0, 6.283)
        u = r.random() ** 1.8                           # most drops land near the core, a few fly far
        x, y = cx + math.cos(a) * ex * (1 + u * 1.25), cy + math.sin(a) * ey * (1 + u * 1.25)
        rr = max(1.6, (15 - 10 * u) * r.uniform(0.35, 1.0))
        op = r.uniform(.55, .92)
        if r.random() < 0.28:                          # a streak pointing away from the centre
            ang = math.degrees(math.atan2(math.sin(a) * ey, math.cos(a) * ex))
            drops.append(f'<ellipse class="sp" cx="{x:.0f}" cy="{y:.0f}" rx="{rr * 2.8:.1f}" ry="{rr * 0.7:.1f}" transform="rotate({ang:.0f} {x:.0f} {y:.0f})" fill="#171612" fill-opacity="{op:.2f}"/>')
        else:
            drops.append(f'<circle class="sp" cx="{x:.0f}" cy="{y:.0f}" r="{rr:.1f}" fill="#171612" fill-opacity="{op:.2f}"/>')
    blot = (f'<filter id="{cid}s" x="-30%" y="-40%" width="160%" height="180%"><feTurbulence type="fractalNoise" baseFrequency="0.009" numOctaves="3" seed="23" result="n"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="n" scale="110" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="2.5"/></filter>'
            f'<ellipse class="blot" cx="{cx:.0f}" cy="{cy:.0f}" rx="{ex * 1.08:.0f}" ry="{ey:.0f}" fill="#171612" fill-opacity=".13" filter="url(#{cid}s)"/>')
    fall = f'<ellipse class="fall" cx="{cx:.0f}" cy="{cy:.0f}" rx="16" ry="22" fill="#171612"/>'
    inner = (f'<svg class="svgl" viewBox="0 0 {W} {H}">{blot}<g filter="url(#{cid}k)">{"".join(drops)}{fall}</g></svg>'
             f'<div class="serif kk halo" style="left:0; right:0; top:{by - (100 if P else 90):.0f}px; text-align:center; font-size:{36 if P else 34}px; letter-spacing:.24em">{X.rich(kick)}</div>'
             f'<div class="big" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>'
             + (f'<div class="serif nt halo" style="left:0; right:0; top:{by + bh + 70:.0f}px; text-align:center; font-size:{28 if P else 26}px; letter-spacing:.14em; color:var(--muted)">{X.rich(note)}</div>' if note else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    tb = T(X, b, "at_big", t, t + 0.5)
    X.tw(f'tl.from("{s} .kk", {{opacity:0, y:-12, duration:0.6}}, {t + 0.1:.3f});')
    tl0 = t + 0.15; land = tl0 + 0.42
    X.tw(f'tl.fromTo("{s} .fall", {{y:{-cy - 60:.0f}, scaleY:1.6, opacity:1}}, {{y:0, scaleY:1, duration:0.42, ease:"power2.in"}}, {tl0:.3f});')
    X.tw(f'tl.to("{s} .fall", {{scaleX:2.4, scaleY:0.4, opacity:0, duration:0.25, ease:"power2.out", transformOrigin:"50% 50%"}}, {land:.3f});')
    X.sfx(land, "drop")
    X.tw(f'tl.fromTo("{s} .blot", {{attr:{{rx:8, ry:8}}}}, {{attr:{{rx:{ex * 0.55:.0f}, ry:{ey * 0.5:.0f}}}, duration:{max(0.3, tb - 0.15 - land):.2f}, ease:"power1.out"}}, {land:.3f});')
    X.tw(f'tl.to("{s} .blot", {{attr:{{rx:{ex * 1.08:.0f}, ry:{ey:.0f}}}, duration:0.6, ease:"expo.out"}}, {tb - 0.15:.3f});')
    X.tw(f'tl.from("{s} .sp", {{scale:0, svgOrigin:"{cx:.0f} {cy:.0f}", duration:0.5, ease:"expo.out", stagger:0.003}}, {tb - 0.12:.3f});')
    write_on(X, f"{s} .big", tb - 0.2, dur=1.0, stagger=0.1)
    X.sfx(tb - 0.1, "brush")
    if note: X.tw(f'tl.from("{s} .nt", {{opacity:0, duration:0.6}}, {tb + 0.9:.3f});')
    X.tw(f'tl.fromTo("{s} .big", {{y:0}}, {{y:-10, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.05)


def couplet(b, X, t, d, cid):
    """two vertical lines read right-to-left, written brush-first; a seal lands on the key phrase; wide 留白 around them."""
    P = X.portrait; W, H = X.W, X.H
    src_lines = [str(x) for x in (b.get("lines") or ["", ""])][:3]
    per_col = 8 if P else 7                                   # longer lines wrap into extra columns, still right-to-left
    lines, owner = [], []
    for k, ln in enumerate(src_lines):
        m = max(1, math.ceil(len(ln) / per_col)); step = math.ceil(len(ln) / m)
        for j in range(m):
            lines.append(ln[j * step:(j + 1) * step]); owner.append((k, j))
    lines = lines[:5]; owner = owner[:5]
    maxlen = max(len(x) for x in lines) or 1
    colh = H * (0.56 if P else 0.72)
    px = min(colh / maxlen / 1.02, (W * (0.72 if P else 0.46)) / max(1, len(lines)) / 1.4, 128 if P else 120)
    gap = px * 0.55
    total_w = len(lines) * px + (len(lines) - 1) * gap
    x_right = (W + total_w + (px * 1.2 if b.get("seal") else 0)) / 2
    y0 = H * (0.17 if P else 0.13)
    cols = []
    for k, ln in enumerate(lines):
        x = x_right - px - k * (px + gap)
        glyphs_html = []
        for j, ch in enumerate(ln):
            svg, gw_, gh = brush(X, ch, b.get("font", "ma-shan-zheng"), px, flt=f"{cid}k")
            glyphs_html.append(f'<div class="gc" style="position:absolute; left:{(px - gw_) / 2:.0f}px; top:{j * px * 1.02:.0f}px">{svg}</div>')
        cols.append(f'<div class="col c{k}" style="position:absolute; left:{x:.0f}px; top:{y0:.0f}px; width:{px:.0f}px; height:{len(ln) * px * 1.02:.0f}px">{"".join(glyphs_html)}</div>')
    sl = b.get("seal", "")
    sl_html = seal(X, sl, int(px * 0.9), style=f"left:{x_right - total_w - px * 1.2:.0f}px; top:{y0 + colh * 0.72:.0f}px; transform:rotate(-3deg)") if sl else ""
    inner = f'<div style="position:absolute;inset:0;opacity:.35">{mountains(cid, X, 53, layers=2, top=0.74, amp=0.08, dark=0.45)}</div>' + "".join(cols) + sl_html
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    line_at = [T(X, b, f"at_{k}", t, t + 0.3 + k * d * 0.3) for k in range(len(src_lines))]
    line_end = line_at[1:] + [t + d - 0.6]
    ats = []
    for c, (k, j) in enumerate(owner):                       # columns of one line share its time slot, one after another
        cols_k = [cc for cc, (kk, _) in enumerate(owner) if kk == k]
        n_k = sum(len(lines[cc]) for cc in cols_k)
        done = sum(len(lines[cc]) for cc in cols_k if cc < c)
        per = max(0.05, min(0.16, (line_end[k] - line_at[k] - 0.4) / max(1, n_k)))
        ta = line_at[k] + done * per
        ats.append(ta)
        write_on(X, f"{s} .c{c}", ta - 0.2, dur=0.9, stagger=per)
        if j == 0: X.sfx(ta - 0.15, "brush")
    if sl: stamp(X, f"{s} .seal", T(X, b, "at_seal", t, ats[-1] + 1.0))
    drift(X, f"{s} .cam", t, d, 1.04, 0, -10)


def seal_outro(b, X, t, d, cid):
    P = X.portrait; W, H = X.W, X.H
    name = b.get("title", "第九顶帽子"); sub = b.get("sub", ""); cta = b.get("cta", "")
    px = min(H * (0.13 if P else 0.16), W * (0.8 if P else 0.5) / max(1, sum(fit.gw(c) for c in name)))
    svg, bw, bh = brush(X, name, b.get("font", "zhi-mang-xing"), px, flt=f"{cid}k")
    bx, by = (W - bw) / 2, H * (0.30 if P else 0.30)
    ssz = 128 if P else 140
    inner = (f'<div style="position:absolute;inset:0;opacity:.45">{mountains(cid, X, 61, layers=3, top=0.66, amp=0.1, dark=0.6)}</div>{mist(X, 3, 31)}'
             + seal(X, b.get("seal", "九帽"), ssz, style=f"left:{(W - ssz) / 2:.0f}px; top:{by - ssz - 40:.0f}px; transform:rotate(-3deg)")
             + f'<div class="nm" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>'
             + (f'<div class="serif sb" style="left:0; right:0; top:{by + bh + 30:.0f}px; text-align:center; font-size:{34 if P else 32}px; letter-spacing:.3em">{X.rich(sub)}</div>' if sub else "")
             + (f'<div class="serif ct" style="left:0; right:0; top:{by + bh + 100:.0f}px; text-align:center; font-size:{28 if P else 26}px; letter-spacing:.2em; color:var(--seal)">{X.rich(cta)}</div>' if cta else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    stamp(X, f"{s} .seal", t + 0.15)
    write_on(X, f"{s} .nm", t + 0.4, dur=1.1, stagger=0.1)
    X.sfx(t + 0.45, "brush")
    X.tw(f'tl.from("{s} .sb, {s} .ct", {{opacity:0, y:12, duration:0.7, stagger:0.2}}, {t + 1.1:.3f});')
    X.tw(f'tl.fromTo("{s} .mist", {{x:-50}}, {{x:70, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.03)


SCENES = {"brush": brush_scene, "column": column, "drops": drops, "scrolls": scrolls, "wash": wash,
          "handscroll": handscroll, "splash": splash, "couplet": couplet, "seal": seal_outro}
