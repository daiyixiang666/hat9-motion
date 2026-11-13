"""ink · 水墨国风 —— 宣纸、墨的晕染、书法落笔、朱红印章、层叠远山和大面积留白。参照故宫、敦煌数字展陈与当代国风动态设计：
克制、透气、墨色有层次，不用渐变金、不用祥云贴图。墨的边缘用 SVG 湍流 + 位移滤镜做出洇开和飞白（固定种子，逐帧确定）。

场景（SCENES，全部自写）：brush 书法大字落笔 · column 竖排日期 + 题名 · drops 墨点洇开成人群 · scrolls 立轴展开的数字 ·
wash 一笔被水冲淡 · handscroll 手卷横移的年份 · splash 泼墨数字 · bars 一笔一柱的干笔柱图 · share 圆相墨晕占比 ·
couplet 竖排对句 + 盖章 · seal 落款。数字一律刻进朱红印块（#b2271f）。
横屏竖屏各自排版；所有文字走 fit.py 自适应字号与断行。
"""
import math, random, re

from h9 import fit, fonts as h9fonts

STYLE = {
    "name": "水墨国风", "en": "Ink", "benchmarks": ["故宫数字展陈", "数字敦煌", "当代国风动态设计"],
    "tokens": {
        "bg": "#ebe3d1", "fg": "#171612", "muted": "#5a544a", "accent": "#b2271f", "accent2": "#3d4a52", "alert": "#b2271f",
        "line": "#cfc5ae", "paper": "#ebe3d1", "ink": "#171612", "card": "#f2ecdd", "card-fg": "#171612",
        "seal": "#b2271f", "wash": "rgba(23,22,18,.10)", "mist": "rgba(245,240,229,.85)",
        "cap-bg": "none", "cap-fg": "#1c1a17", "cap-size": "40px", "cap-weight": "600", "cap-pad": "0 20px",
        "cap-radius": "0", "cap-shadow": "none", "cap-em": "#b2271f", "cap-bottom": "40px",
        "punch-top": "70%", "punch-size": "60px", "punch-stroke": "0",
    },
    "fonts": {"display": "ma-shan-zheng", "body": "noto-serif-sc", "cap": "noto-serif-sc", "serif": "noto-serif-sc",
              "xing": "zhi-mang-xing", "cao": "liu-jian-mao-cao", "kai": "long-cang", "num": "eb-garamond", "latin": "eb-garamond",
              "quote": "eb-garamond", "mono": "eb-garamond"},
    # the four grounds an effect beat can ask for: 宣纸 xuan paper, 墨 ink wash, 朱砂 vermilion, 天青 celadon
    "fx_themes": {
        "paper": {"bg": "#ebe3d1", "fg": "#171612", "muted": "#5a544a", "accent": "#b03a2e", "card": "#f4efe2", "card-fg": "#171612", "line": "#cfc5ae"},
        "ink":   {"bg": "#1d1b17", "fg": "#ece4d2", "muted": "#a89f8c", "accent": "#d9614f", "card": "#2a2721", "card-fg": "#ece4d2", "line": "#3d3a32"},
        "red":   {"bg": "#9e3327", "fg": "#f4ecd9", "muted": "#ead8c4", "accent": "#171612", "card": "#f4ecd9", "card-fg": "#171612", "line": "rgba(244,236,217,.35)"},
        "lemon": {"bg": "#cfd9d0", "fg": "#13201c", "muted": "#44564f", "accent": "#b03a2e", "card": "#edf1ec", "card-fg": "#13201c", "line": "#a7b8ae"},
    },
    "motion": {"ease": "power3.out", "dur": 0.8, "stagger": 0.05, "cut": "hard", "transition": "hard", "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "none", "frame": "none", "landscape": {"right": 110, "bottom": 70, "h": 300}, "portrait": {"left": 400, "bottom": 640, "h": 260}},
    "sfx": {"enter": ("whoosh_soft", 0.22), "brush": ("brush", 0.45), "stamp": ("hit", 0.35), "drop": ("pop", 0.25), "paper": ("paper", 0.35),
            "count": ("type", 0.2), "mascot": ("whoosh_soft", 0.22), "wash": ("whoosh_deep", 0.3)},
    "css": """
.st-ink .cap .cp { position:relative; display:inline-block; color:#1c1a17; letter-spacing:.1em; text-shadow:0 0 4px #efe8d8, 0 0 10px #efe8d8, 0 0 20px #efe8d8; }
.st-ink .cap .cp::before { content:""; position:absolute; z-index:-1; left:-30%; right:-30%; top:-85%; bottom:-120%; pointer-events:none;
  background:radial-gradient(ellipse 50% 50% at 50% 50%, rgba(241,235,222,.97) 0, rgba(241,235,222,.92) 34%, rgba(241,235,222,.58) 62%, rgba(241,235,222,.18) 84%, rgba(241,235,222,0) 100%); }
.st-ink .cap .cp::after { content:""; position:absolute; left:50%; bottom:-20px; width:120px; height:16px; margin-left:-60px; pointer-events:none; background:url("BRUSH") center / 120px 16px no-repeat; }
#root.v.st-ink { --cap-bottom:456px; --cap-size:40px; --cap-pad:0 20px; }
#root.v.st-ink .cap { padding-left:110px; padding-right:110px; }
.st-ink .mascot { display:none !important; }
.st-ink .cap .em .emt { color:var(--seal); }
#root.v.st-ink .cap-punch .cp { font-weight:700; }
""",
}

# the dry-brush stroke under the caption: one tapered mark, its body broken into hair streaks (flying white)
_DRY = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='240' height='32' viewBox='0 0 240 32'><defs>"
        "<filter id='d' x='-5%' y='-40%' width='110%' height='180%'><feTurbulence type='fractalNoise' baseFrequency='0.012 0.55' numOctaves='2' seed='4' result='t'/>"
        "<feColorMatrix in='t' type='matrix' values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -2.4 1.75' result='m'/><feComposite in='SourceGraphic' in2='m' operator='in'/></filter></defs>"
        "<path d='M3 17 C 30 7, 90 6, 160 8 C 200 9, 226 10, 238 14 C 214 19, 170 22, 110 24 C 60 26, 22 25, 3 17 Z' fill='%231c1a17' filter='url(%23d)'/></svg>")
STYLE["css"] = STYLE["css"].replace("BRUSH", _DRY)

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
.ik .num.gl { --m:0%; -webkit-mask-image:linear-gradient(100deg, #000 40%, rgba(0,0,0,0) 60%); mask-image:linear-gradient(100deg, #000 40%, rgba(0,0,0,0) 60%);
  -webkit-mask-size:320% 100%; mask-size:320% 100%; -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat; -webkit-mask-position:var(--m) 0; mask-position:var(--m) 0; }
.ik .bt path { fill:var(--ink); }
.ik .bt.red path { fill:var(--seal); }
.ik .serif { position:absolute; font-family:var(--f-serif); color:var(--ink); }
.ik .halo { text-shadow:0 0 10px var(--paper), 0 0 18px var(--paper), 0 0 3px var(--paper); }
.ik .vt { position:absolute; writing-mode:vertical-rl; font-family:var(--f-serif); letter-spacing:.18em; color:var(--ink); white-space:nowrap; }
.ik .num { position:absolute; font-family:var(--f-num); font-weight:600; color:var(--ink); font-variant-numeric:oldstyle-nums proportional-nums; white-space:nowrap; letter-spacing:.01em; }
.ik .seal { position:absolute; display:grid; place-items:center; background:var(--seal); color:var(--paper); border-radius:6px;
  font-family:var(--f-serif); font-weight:900; line-height:1; box-shadow:0 0 0 2px rgba(178,39,31,.22); }
/* a figure carved into a vermilion seal: paper-coloured numerals, an inner carved rule, uneven ink (paper specks show through) */
.ik .fsw { position:absolute; }
.ik .fseal { position:relative; display:flex; align-items:baseline; justify-content:center; gap:.06em; background:var(--seal); color:#f3ead6;
  font-family:var(--f-serif); font-weight:900; line-height:1; white-space:nowrap; border-radius:5px; font-variant-numeric:lining-nums proportional-nums; letter-spacing:-.03em;
  box-shadow:inset 0 0 0 9px var(--seal), inset 0 0 0 13px rgba(243,234,214,.9); }
.ik .fseal::after { content:""; position:absolute; inset:0; border-radius:5px; pointer-events:none; background:url("SPECK") 0 0 / 260px 260px; }
.ik .fseal .u { font-size:.36em; letter-spacing:.04em; }

.ik .seal .si { display:grid; grid-auto-flow:column; grid-template-rows:repeat(2, 1fr); direction:rtl; gap:2px 4px; }
.ik .seal.out { background:transparent; color:var(--seal); box-shadow:inset 0 0 0 5px var(--seal); }
.ik .hd { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-serif); color:var(--ink); z-index:6; }
.ik .hd b { font-weight:700; letter-spacing:.24em; } .ik .hd span { opacity:.55; letter-spacing:.2em; }
.ik .hd i { display:block; width:42px; height:2px; background:var(--ink); opacity:.6; }
.ik .idx { position:absolute; z-index:6; width:58px; height:58px; display:grid; place-items:center; font-family:var(--f-serif); font-weight:900;
  color:var(--paper); background:var(--seal); border-radius:5px; font-size:30px; transform:rotate(-2deg); }
.ik .ft { position:absolute; font-family:var(--f-serif); font-weight:600; color:#4a443a; letter-spacing:.08em; z-index:6; white-space:nowrap;
  text-shadow:0 0 5px var(--paper), 0 0 12px var(--paper), 0 0 20px var(--paper); }
.ik .ft::after { content:""; position:absolute; z-index:-1; left:-60px; right:-90px; top:-22px; bottom:-22px; pointer-events:none;
  background:radial-gradient(ellipse 50% 50% at 50% 50%, rgba(241,235,222,.9) 0, rgba(241,235,222,.72) 45%, rgba(241,235,222,0) 100%); }
.ik .ft::before { content:""; display:inline-block; width:9px; height:9px; margin-right:12px; background:var(--seal); transform:translateY(-3px) rotate(45deg); }
.ik .mount { position:absolute; background:linear-gradient(90deg, #a9ad9b, #bcc0ae 18%, #bcc0ae 82%, #a4a896); box-shadow:0 14px 30px rgba(60,45,20,.16); }
.ik .heart { position:absolute; background:var(--card); box-shadow:0 0 0 1px rgba(23,22,18,.22); overflow:hidden; }
.ik .rule { position:absolute; background:var(--ink); transform-origin:50% 0; }
.ik .card { position:absolute; background:var(--card); box-shadow:0 18px 40px rgba(60,45,20,.18), 0 0 0 1px rgba(23,22,18,.08); }
.ik .rod { position:absolute; background:linear-gradient(180deg, #4a3a2a, #2a2018); border-radius:6px; box-shadow:0 4px 10px rgba(0,0,0,.25); }
"""

# where the seal paste did not take: small paper-coloured specks and a worn edge (seeded noise, thresholded)
_SPECK = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='260' height='260'><filter id='s'>"
          "<feTurbulence type='fractalNoise' baseFrequency='0.09' numOctaves='3' seed='12'/>"
          "<feColorMatrix type='matrix' values='0 0 0 0 .953  0 0 0 0 .918  0 0 0 0 .839  0 0 0 -24 5.9'/></filter>"
          "<rect width='260' height='260' filter='url(%23s)'/></svg>")
CSS = CSS.replace("SPECK", _SPECK)

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


def brush_col(X, text, fid, px, flt=None, lead=0.98):
    """a short word written top-to-bottom, one glyph under the other (how a hanging scroll carries its title).
    Returns (html, width_px, height_px)."""
    out, y, w = [], 0.0, 0.0
    for ch in text:
        g, gw_, gh = brush(X, ch, fid, px, flt=flt)
        out.append((g, gw_, y))
        w = max(w, gw_)
        y += px * lead
    html = "".join(f'<div style="position:absolute; left:{(w - gw_) / 2:.0f}px; top:{yy:.0f}px">{g}</div>' for g, gw_, yy in out)
    return f'<div class="bc" style="position:relative; width:{w:.0f}px; height:{y:.0f}px">{html}</div>', w, y


def fig_seal(X, val, unit, px, cid, cls="", width=None, num_cls="n"):
    """a figure carved into a vermilion seal block (#b2271f): numerals in paper colour at `px`, the unit small beside
    them. Returns (html, width_px, height_px); the block keeps a fixed width so a running counter does not jitter it."""
    X.used_text.update(str(val) + str(unit) + "0123456789,.+")
    tw = sum(0.6 if c.isdigit() else fit.gw(c) for c in str(val)) * px + (len(unit) * px * 0.36 + px * 0.06 if unit else 0)
    padx, pady = px * 0.17, px * 0.2
    bw = width or tw + 2 * padx
    bh = px * 0.78 + 2 * pady
    u = f'<span class="u">{X.rich(unit)}</span>' if unit else ""
    html = (f'<div class="fsw {cls}" style="width:{bw:.0f}px; height:{bh:.0f}px; filter:url(#{cid}k)">'
            f'<div class="fseal" style="width:{bw:.0f}px; height:{bh:.0f}px; font-size:{px:.0f}px; padding-top:{pady * 0.9:.0f}px; box-sizing:border-box">'
            f'<span class="{num_cls}">{X.rich(str(val))}</span>{u}</div></div>')
    return html, bw, bh


def can_write(fid, text):
    """True when the calligraphy font has every glyph of `text` (most of them carry no digits or Latin)."""
    path = font_file(fid)
    if not path: return False
    cmap = _font(path)[1]
    return all(ord(c) in cmap for c in text if not c.isspace())


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
            f'<filter id="{cid}h" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.42 0.012" numOctaves="2" seed="{seed + 5}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -12.5 8.4" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>'
            f'<filter id="{cid}r" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency="0.16" numOctaves="2" seed="{seed + 9}" result="t"/>'
            f'<feColorMatrix in="t" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -12.5 8.4" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter>'
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


def mountains(cid, X, seed, layers=3, top=0.45, amp=0.12, dark=0.85, width=None, color="#171612"):
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
            x = -160 + (W + 400) * i / n              # wider than the page: the parallax drift never shows an end
            u = x / W * 6.283
            y = base - a * sum(am[j] * (0.5 + 0.5 * math.sin(fr[j] * u + ph[j])) for j in range(5)) / sum(am)
            pts.append(f"{x:.0f},{y:.0f}")
        op = dark * (0.35 + 0.65 * (k + 1) / layers)
        gid = f"{cid}g{k}"
        out.append(f'<g class="mt mt{k}"><defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                   f'<stop offset="0" stop-color="{color}" stop-opacity="{op:.2f}"/><stop offset="0.28" stop-color="{color}" stop-opacity="{op * 0.45:.2f}"/>'
                   f'<stop offset="0.7" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>'
                   f'<path d="M-160,{H} L{" L".join(pts)} L{W + 240},{H} Z" fill="url(#{gid})" filter="url(#{cid}b)"/></g>')
    return f'<svg class="svgl" viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="width:{W}px">{"".join(out)}</svg>'


def shore(cid, X, seed, mode="bank"):
    """the near ground that closes the bottom edge, so a page is a whole painting and not a picture with a blank foot:
    a pale far ridge standing in water mist and (mode "bank") a dark near bank rising on
    one side with reeds. Everything is a brush mark with the scene's bleed / flying-white filters; seeded per page."""
    W, H, P = X.W, X.H, X.portrait
    r = random.Random(300 + seed)
    flip = seed % 2
    ph = [r.uniform(0, 6.283) for _ in range(4)]
    base, a = H * (0.925 if P else 0.93), H * (0.04 if P else 0.06)
    far = " L".join(f"{W * i / 80:.0f},{base - a * (0.5 + 0.3 * math.sin(i / 80 * 5 + ph[0]) + 0.2 * math.sin(i / 80 * 13 + ph[1])):.0f}" for i in range(81))
    out = [f'<g class="sf"><defs><linearGradient id="{cid}sf" gradientUnits="userSpaceOnUse" x1="0" y1="{base - a:.0f}" x2="0" y2="{H}">'
           f'<stop offset="0" stop-color="#171612" stop-opacity=".26"/><stop offset=".5" stop-color="#171612" stop-opacity=".12"/><stop offset="1" stop-color="#171612" stop-opacity=".2"/></linearGradient></defs>'
           f'<path d="M-80,{H + 40} L-80,{base:.0f} L{far} L{W + 80},{base:.0f} L{W + 80},{H + 40} Z" fill="url(#{cid}sf)" filter="url(#{cid}b)"/></g>']
    if mode == "bank":
        hi, lo = H * (0.105 if P else 0.17), H * 0.012
        prof = []
        for i in range(101):
            u = i / 100
            v = 1 - u if flip else u                       # v = 0 on the side where the bank stands high
            k = max(0.0, 1 - v / 0.78) ** 1.7
            prof.append((W * u, H - lo - (hi - lo) * k - H * 0.006 * math.sin(u * 23 + ph[2]) * (0.3 + k) - H * 0.003 * math.sin(u * 61 + ph[3])))
        line = " L".join(f"{x:.0f},{y:.0f}" for x, y in prof)
        reeds = []
        for _ in range(9 if P else 11):
            v = r.uniform(0.02, 0.26 if P else 0.4)
            u = 1 - v if flip else v
            x, y = min(prof, key=lambda q: abs(q[0] - W * u))
            ln = H * r.uniform(0.025, 0.06) * (1 if P else 1.5)
            lean = r.uniform(-0.5, 0.5) * ln + (ln * 0.25 if flip else -ln * 0.25)
            reeds.append(f'<path d="M{x:.0f} {y + 8:.0f} q {lean * 0.2:.0f} {-ln * 0.6:.0f} {lean:.0f} {-ln:.0f}" fill="none" stroke="#171612" stroke-opacity="{r.uniform(.6, .9):.2f}" '
                         f'stroke-width="{r.uniform(2, 4.5):.1f}" stroke-linecap="round"/>')
        out.append(f'<g class="sb"><defs><linearGradient id="{cid}sb" gradientUnits="userSpaceOnUse" x1="0" y1="{H - hi:.0f}" x2="0" y2="{H}">'
                   f'<stop offset="0" stop-color="#171612" stop-opacity=".92"/><stop offset="1" stop-color="#171612" stop-opacity=".62"/></linearGradient></defs>'
                   f'<path d="M-80,{H + 60} L-80,{prof[0][1]:.0f} L{line} L{W + 80},{prof[-1][1]:.0f} L{W + 80},{H + 60} Z" fill="url(#{cid}sb)" filter="url(#{cid}b)"/>'
                   f'<g filter="url(#{cid}k)">{"".join(reeds)}</g></g>')
    return f'<svg class="svgl shore" viewBox="0 0 {W} {H}">{"".join(out)}</svg>'


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


def furn(X, b, cid, inner, t=None, d=None, ground="bank", extra_cls=""):
    """page: paper, the near ground that carries the picture to the bottom edge, header (channel + section), index seal,
    footnote, then the scene; opens through an ink bleed from the previous page."""
    X.css("ink", CSS)
    P = X.portrait
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "国风 · 商业")
    X.used_text.update(sec + X.channel + NUMZH + "来源：")
    hx, hy, fs = (56, 204, 28) if P else (80, 44, 24)
    idx = NUMZH[(i + 1) % 11] if i + 1 <= 10 else str(i + 1)
    hd = (f'<div class="hd" style="left:{hx}px; top:{hy}px; font-size:{fs}px"><b>{X.rich(X.channel)}</b><i></i><span>{X.rich(sec)}</span></div>'
          f'<div class="idx" style="right:{hx}px; top:{hy - 12}px">{idx}</div>')
    ft = ""
    src = b.get("src")
    if src:
        fy = 1478 if P else 1030
        ft = f'<div class="ft" style="left:{hx}px; top:{fy}px; font-size:{28 if P else 22}px">来源：{X.rich(src)}</div>'
    foot = shore(cid, X, i, ground) if ground else ""
    if foot and t is not None:
        sx = 36 if i % 2 else -36
        X.tw(f'tl.fromTo("#{cid} .shore .sf", {{x:{-sx * 0.5:.0f}}}, {{x:{sx * 0.5:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        if ground == "bank":
            X.tw(f'tl.fromTo("#{cid} .shore .sb", {{x:{sx * 1.5:.0f}, y:26}}, {{x:{-sx * 1.5:.0f}, y:0, duration:{d:.2f}, ease:"power1.out"}}, {t:.3f});')
    return f'<div class="ik {extra_cls}">{filters(cid)}{paper(X)}<div class="cam">{foot}{inner}</div>{hd}{ft}</div>'


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
    """hook: far mountains drift; a huge calligraphy word is written; a vertical kicker and a seal frame it.
    9:16 with a 1–2 glyph word: the word hangs as one tall column (each glyph ~half the frame wide), kicker and
    sub as narrow columns either side, like the title and colophon of a hanging scroll."""
    P = X.portrait; W, H = X.W, X.H
    word = b.get("big", "千万")
    kick = b.get("kicker", "")
    sub = b.get("sub", "")
    fid = b.get("font", "ma-shan-zheng")
    ssz = 92 if P else 104
    if P and len(word) <= 2:
        px = 650 if len(word) == 2 else 720
        svg, bw, bh = brush_col(X, word, fid, px, flt=f"{cid}k", lead=0.92)
        bx, by = (W - bw) / 2 + 10, H * 0.12
        kx, ky = 70, max(300, by + 40)
        vt_fs = min(46, bh * 0.55 / max(1, len(kick)) / 1.2)
        sl = "" if not b.get("seal") else seal(X, b["seal"], ssz, style=f"left:{bx - ssz * 0.35:.0f}px; top:{min(by + bh - ssz * 0.6, 1478 - ssz - 34):.0f}px; transform:rotate(-3deg)")
        if sub:
            sfs = min(36, (bh * 0.9) / max(1, len(sub)) / 1.12)
            subh = f'<div class="vt sub halo" style="right:72px; top:{max(300, by + 60):.0f}px; font-size:{sfs:.0f}px; font-weight:600; letter-spacing:.12em">{X.rich(sub)}</div>'
        else: subh = ""
    else:
        box_w = W * (0.70 if P else 0.54)
        px = min(H * (0.24 if P else 0.36), box_w / max(1, sum(fit.gw(c) for c in word)))
        svg, bw, bh = brush(X, word, fid, px, flt=f"{cid}k")
        bx = W - bw - 70 if P else W * 0.40
        by = H * 0.25 if P else H * 0.15
        kx = 80 if P else W * 0.16
        ky = by - (110 if P else -20)
        vt_fs = min(46 if P else 44, ((by + bh - ky) if P else H * 0.6) / max(1, len(kick)) / 1.2)
        sl = "" if not b.get("seal") else seal(X, b["seal"], ssz, style=f"left:{min(bx + bw - ssz * 0.55, W - 60 - ssz):.0f}px; top:{by + bh - ssz * 0.7:.0f}px; transform:rotate(-3deg)")
        if sub:
            sfs, shtml = ftext(X, sub, W - 160 if P else box_w, 38 if P else 34, 24, ls=0.14)
            subh = (f'<div class="serif sub halo" style="left:80px; right:80px; top:{by + bh + (90 if P else 60):.0f}px; font-size:{sfs}px; font-weight:600; letter-spacing:.14em; line-height:1.3; text-align:center">{shtml}</div>'
                    if P else f'<div class="serif sub halo" style="left:{bx:.0f}px; top:{by + bh + 50:.0f}px; width:{box_w:.0f}px; font-size:{sfs}px; font-weight:600; letter-spacing:.14em; line-height:1.3">{shtml}</div>')
        else: subh = ""
    inner = (f'<div class="mtl" style="position:absolute;inset:0">{mountains(cid, X, 11, layers=3, top=0.62 if P else 0.64, amp=0.13)}</div>{mist(X, 3)}'
             f'<div class="vt kick" style="left:{kx:.0f}px; top:{ky:.0f}px; font-size:{vt_fs:.0f}px; font-weight:600">{X.rich(kick)}</div>'
             f'<div class="word" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>{sl}{subh}')
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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
    if sub: X.tw(f'tl.from("{s} .sub", {{opacity:0, y:16, duration:0.7}}, {min(ts + 0.2, tw_ + 0.6):.3f});')
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
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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
    cx, cy = (W * 0.5, H * 0.395) if P else (W * 0.655, H * 0.50)
    R = (W * 0.35) if P else (H * 0.40)
    pts = []
    for k in range(n):
        a = r.uniform(0, 6.283)
        rr = R * math.sqrt(r.random()) * (0.9 + 0.07 * math.sin(3 * a + 1.3) + 0.04 * math.sin(7 * a))
        pts.append((cx + rr * math.cos(a) * (1.25 if not P else 1.0), cy + rr * math.sin(a) * (0.9 if not P else 0.95), rr))
    pts.sort(key=lambda p: p[2])
    dots = "".join(f'<circle class="dp" cx="{x:.1f}" cy="{y:.1f}" r="{r.uniform(2.2, 4.6):.1f}" fill="#171612" fill-opacity="{r.uniform(.45, .95):.2f}"/>' for x, y, _ in pts)
    unit = b.get("unit", "万人"); label = b.get("label", ""); kicker = b.get("kicker", "")
    show = float(b.get("show", total / 10000)); dec = int(b.get("dec", 0))
    final = f"{show:,.{dec}f}"
    col_w = W - 160 if P else W * 0.29
    fpx = min(240 if P else 200, (col_w - 40) / (sum(0.6 if c.isdigit() else fit.gw(c) for c in final) + len(unit) * 0.36 + 0.4))
    fs_html, fbw, fbh = fig_seal(X, final, unit, fpx, cid, cls="big")
    lfs, lhtml = ftext(X, label, col_w, 32 if P else 26, 24, ls=0.12)
    if P:
        fx_, fy_ = (W - fbw) / 2, cy + R * 0.95 - fbh * 0.35       # stamped over the lower rim of the crowd
    else:
        fx_, fy_ = W * 0.10, H * 0.40
    nx = fx_
    kk_top = 292 if P else fy_ - 80
    lb_top = fy_ + fbh + 26
    align = "center" if P else "left"
    inner = (f'<svg class="svgl" viewBox="0 0 {W} {H}"><g filter="url(#{cid}b)">{dots}</g>'
             f'<circle class="core" cx="{cx:.0f}" cy="{cy:.0f}" r="26" fill="#171612" filter="url(#{cid}b)"/></svg>'
             f'<div class="serif kk halo" style="left:{0 if P else nx:.0f}px; {"right:0;" if P else ""} top:{kk_top:.0f}px; font-size:{40 if P else 32}px; font-weight:600; letter-spacing:.2em; text-align:{align}">{X.rich(kicker)}</div>'
             f'<div style="position:absolute; left:{fx_:.0f}px; top:{fy_:.0f}px; transform:rotate(-1.5deg)">{fs_html}</div>'
             f'<div class="serif lb halo" style="left:{0 if P else nx:.0f}px; {"right:0;" if P else ""} top:{lb_top:.0f}px; {"" if P else f"width:{col_w:.0f}px; "}font-size:{lfs}px; font-weight:600; line-height:1.3; letter-spacing:.12em; color:#4a443a; text-align:{align}">{lhtml}</div>')
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + 0.6)
    opening(X, cid, t)
    X.tw(f'tl.from("{s} .core", {{attr:{{r:0}}, duration:0.5, ease:"back.out(2)"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "drop")
    spread = max(1.2, min(d - 0.8, tn - t + 1.0))
    X.tw(f'tl.from("{s} .dp", {{attr:{{r:0}}, duration:0.5, ease:"power2.out", stagger:{{each:{spread / n:.5f}}}}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .kk", {{opacity:0, y:12, duration:0.6}}, {t + 0.1:.3f});')
    tc = max(t + 0.3, tn - 0.5)
    X.tw(f'tl.fromTo("{s} .big", {{scale:1.3, opacity:0, rotation:-6}}, {{scale:1, opacity:1, rotation:0, duration:0.32, ease:"back.out(2.2)"}}, {tc:.3f});')
    X.sfx(tc + 0.08, "stamp")
    counter(X, f"{s} .big .n", tc + 0.1, 0, show, dur=1.3, dec=dec)
    X.sfx(tn - 0.4, "count")
    X.tw(f'tl.from("{s} .lb", {{opacity:0, duration:0.5}}, {tn + 0.3:.3f});')
    drift(X, f"{s} .cam", t, d, 1.05, 0, 0)


def scrolls(b, X, t, d, cid):
    """1–3 hanging scrolls (立轴) unroll from their top rods: silk mount, a paper heart, a vertical label; the figure is
    carved into a vermilion seal stamped across heart and mount (骑缝章), the unit written under it with a brush.
    All figures share one size so the comparison is fair."""
    P = X.portrait; W, H = X.W, X.H
    items = b.get("items", [])[:3] or [{"value": "—", "label": ""}]
    n = len(items)
    gap = 34 if P else 80
    sw = min((W - (2 * 34 if P else 2 * 180) - gap * (n - 1)) / n, 560)
    sh = H * (0.47 if P else 0.62)
    x0 = (W - (n * sw + (n - 1) * gap)) / 2
    y0 = H * (0.165 if P else 0.13)
    hx, hw = sw * 0.075, sw * 0.85                     # the paper heart inside the mount: wide head (天头), short foot (地头)
    hy, hh = sh * 0.125, sh * 0.80
    fid = b.get("font", "ma-shan-zheng")
    vals = [str(it.get("value", "")) for it in items]
    fpx = min(250 if P else 220, hh * 0.3, min((sw * 1.02) / (sum(0.6 if c.isdigit() else fit.gw(c) for c in v) + 0.34) for v in vals))
    html = []
    for k, it in enumerate(items):
        x = x0 + k * (sw + gap)
        val = vals[k]; unit = it.get("unit", ""); lab = it.get("label", ""); sl = it.get("seal", "")
        fs_html, fbw, fbh = fig_seal(X, val, "", fpx, cid, cls="val")
        upx = min(fpx * 0.5, 76 if P else 72, hw * 0.8 / max(1, len(unit)))
        usvg, uw, uh = brush(X, unit, fid, upx, flt=f"{cid}k") if unit else ("", 0, 0)
        vy = sh * (0.54 if P else 0.42)                 # in scroll coordinates: the seal rides the heart's edges
        lfs = min(38 if P else 34, hh * 0.3 / max(1, len(lab)) * 1.6)
        blot = (f'<svg class="svgl" viewBox="0 0 {hw:.0f} {hh:.0f}"><ellipse class="bl" cx="{hw * 0.5:.0f}" cy="{vy - hy + fbh + uh * 0.6:.0f}" rx="{hw * 0.42:.0f}" ry="{uh * 0.9 + 20:.0f}" '
                f'fill="#171612" fill-opacity=".1" filter="url(#{cid}s)"/></svg>')
        html.append(f'<div class="scr s{k}" style="position:absolute; left:{x:.0f}px; top:{y0:.0f}px; width:{sw:.0f}px; height:{sh:.0f}px">'
                    f'<svg class="cord" width="{sw:.0f}" height="{sh * 0.08:.0f}" viewBox="0 0 {sw:.0f} {sh * 0.08:.0f}" style="position:absolute; left:0; top:{-sh * 0.08 - 6:.0f}px; overflow:visible">'
                    f'<path d="M{sw * 0.16:.0f} {sh * 0.08:.0f} L{sw * 0.5:.0f} 4 L{sw * 0.84:.0f} {sh * 0.08:.0f}" fill="none" stroke="#3a2e22" stroke-width="2.5"/>'
                    f'<circle cx="{sw * 0.5:.0f}" cy="4" r="6" fill="#3a2e22"/></svg>'
                    f'<div class="body mount" style="left:0; right:0; top:0; height:{sh:.0f}px">'
                    f'<div class="heart" style="left:{hx:.0f}px; top:{hy:.0f}px; width:{hw:.0f}px; height:{hh:.0f}px">{blot}'
                    f'<div class="vt lab" style="right:{hw * 0.07:.0f}px; top:{hh * 0.05:.0f}px; font-size:{lfs:.0f}px; font-weight:700">{X.rich(lab)}</div>'
                    + (f'<div class="unit" style="position:absolute; left:{(hw - uw) / 2:.0f}px; top:{vy - hy + fbh + 18:.0f}px">{usvg}</div>' if unit else "")
                    + (seal(X, sl, int(min(84, hw * 0.2)), style=f"left:{hw * 0.08:.0f}px; top:{hh * 0.05:.0f}px; transform:rotate(-3deg)") if sl else "") +
                    f'</div>'
                    f'<div class="vw" style="position:absolute; left:{(sw - fbw) / 2:.0f}px; top:{vy:.0f}px; transform:rotate({-1.2 if k % 2 == 0 else 1.0}deg)">{fs_html}</div></div>'
                    f'<div class="rod rt" style="left:-6px; right:-6px; top:-9px; height:14px; border-radius:3px"></div>'
                    f'<div class="rod rb" style="left:-20px; right:-20px; top:{sh - 10:.0f}px; height:24px"></div></div>')
    note = b.get("note", "")
    flt = (f'<svg width="0" height="0" style="position:absolute"><defs><filter id="{cid}s" x="-40%" y="-40%" width="180%" height="180%">'
           f'<feTurbulence type="fractalNoise" baseFrequency="0.011" numOctaves="3" seed="29" result="n"/>'
           f'<feDisplacementMap in="SourceGraphic" in2="n" scale="90" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="3"/></filter></defs></svg>')
    inner = (flt + mist(X, 2, 12) + "".join(html)
             + (f'<div class="serif nt halo" style="left:0; right:0; top:{y0 + sh + (46 if P else 40):.0f}px; text-align:center; font-size:{31 if P else 26}px; font-weight:600; letter-spacing:.14em; color:#4a443a">{X.rich(note)}</div>' if note else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    ats = [T(X, b, f"at_{k}", t, t + 0.4 + k * 0.9) for k in range(n)]
    for k, ta in enumerate(ats):
        st = min(t + 0.12 + k * 0.35, ta - 1.0)                    # the scroll hangs and unrolls straight away …
        X.tw(f'tl.from("{s} .s{k} .cord, {s} .s{k} .rt", {{opacity:0, y:-40, duration:0.4, ease:"power3.out"}}, {st:.3f});')
        X.tw(f'tl.fromTo("{s} .s{k} .body", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.9, ease:"power3.inOut"}}, {st + 0.1:.3f});')
        X.tw(f'tl.fromTo("{s} .s{k} .rb", {{y:{-sh + 8:.0f}, opacity:0}}, {{y:0, opacity:1, duration:0.9, ease:"power3.inOut"}}, {st + 0.1:.3f});')
        X.tw(f'tl.from("{s} .s{k} .lab", {{opacity:0, y:-14, duration:0.6}}, {st + 0.7:.3f});')
        X.tw(f'tl.fromTo("{s} .s{k} .bl", {{scale:0.2, opacity:0, transformOrigin:"50% 50%"}}, {{scale:1, opacity:1, duration:0.9, ease:"power2.out"}}, {ta - 0.35:.3f});')
        X.tw(f'tl.fromTo("{s} .s{k} .vw", {{scale:1.3, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(2.2)"}}, {ta - 0.1:.3f});')   # … the seal is stamped on its word
        if unit: write_on(X, f"{s} .s{k} .unit", ta + 0.1, dur=0.6, stagger=0.06)
        X.tw(f'tl.from("{s} .s{k} .seal", {{scale:1.35, opacity:0, duration:0.3, ease:"back.out(2.4)"}}, {ta + 0.75:.3f});')
        X.sfx(st + 0.1, "paper"); X.sfx(ta - 0.05, "stamp"); X.sfx(ta + 0.15, "brush")
    if note: X.tw(f'tl.from("{s} .nt", {{opacity:0, y:10, duration:0.6}}, {t + 0.5:.3f});')
    X.tw(f'tl.fromTo("{s} .scr", {{rotation:-0.5}}, {{rotation:0.5, duration:{d:.2f}, ease:"sine.inOut", transformOrigin:"50% -8%"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.035, 0, -8)


def wash(b, X, t, d, cid):
    """a word is written, held, then water washes through it: the ink loosens (displacement + blur) and fades."""
    P = X.portrait; W, H = X.W, X.H
    word = b.get("big", "运气"); kick = b.get("kicker", "")
    if P and len(word) <= 2:
        svg, bw, bh = brush_col(X, word, b.get("font", "liu-jian-mao-cao"), 690 if len(word) == 2 else 720, flt=f"{cid}k", lead=0.9)
        bx, by = (W - bw) / 2 + 30, H * 0.12
        kfs = min(42, bh * 0.6 / max(1, len(kick)) / 1.2)
        kk = f'<div class="vt kk halo" style="left:76px; top:{max(300, by + 30):.0f}px; font-size:{kfs:.0f}px; font-weight:600; letter-spacing:.24em">{X.rich(kick)}</div>'
    else:
        box = W * (0.7 if P else 0.5)
        px = min(H * (0.28 if P else 0.38), box / max(1, sum(fit.gw(c) for c in word)))
        svg, bw, bh = brush(X, word, b.get("font", "liu-jian-mao-cao"), px, flt=f"{cid}k")
        bx, by = (W - bw) / 2, H * (0.30 if P else 0.26)
        kk = f'<div class="serif kk" style="left:0; right:0; top:{by - (110 if P else 90):.0f}px; text-align:center; font-size:{40 if P else 38}px; letter-spacing:.3em">{X.rich(kick)}</div>'
    inner = (kk +
             f'<div class="wd" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px; filter:url(#{cid}w)">{svg}</div>{mist(X, 2, 21)}')
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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
    base = H * (0.63 if P else 0.56)
    pts = []
    for i in range(161):
        x = LW * i / 160
        y = base - H * 0.08 * (0.5 + 0.5 * math.sin(x / LW * 9.4 + 0.7)) - H * 0.03 * math.sin(x / LW * 31 + 2)
        pts.append((x, y))
    line = "M" + " L".join(f"{x:.0f} {y:.0f}" for x, y in pts)
    big = b.get("big", "六年"); kick = b.get("kicker", "")
    px = min(H * (0.27 if P else 0.30), W * (0.92 if P else 0.42) / max(1, sum(fit.gw(c) for c in big)))
    svg, bw, bh = brush(X, big, b.get("font", "ma-shan-zheng"), px, flt=f"{cid}k")
    bx, by = ((W - bw) / 2, H * 0.19) if P else (W * 0.56, H * 0.14)
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
             f'<g filter="url(#{cid}b)"><path class="trail" d="{line}" fill="none" stroke="#171612" stroke-width="17" stroke-linecap="round" filter="url(#{cid}d)"/>'
             f'<path d="{line}" fill="none" stroke="#171612" stroke-opacity=".55" stroke-width="5" stroke-linecap="round" transform="translate(0 5)"/></g></svg></div>'
             f'{"".join(marks)}</div>'
             f'<div class="big" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>'
             + ((f'<div class="serif kk halo" style="left:0; right:0; top:{by - 50:.0f}px; text-align:center; font-size:40px; font-weight:600; letter-spacing:.3em">{X.rich(kick)}</div>' if P
                 else f'<div class="vt kk halo" style="left:150px; top:{H * 0.15:.0f}px; font-size:38px; font-weight:600">{X.rich(kick)}</div>') if kick else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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


def bars(b, X, t, d, cid):
    """a bar chart painted, not drawn: each bar is one vertical dry-brush stroke (the brush lands at the value and drags
    down to the ground line, the tail breaking into flying white); the figures sit in vermilion seals over the strokes."""
    P = X.portrait; W, H = X.W, X.H
    items = (b.get("items") or [{"label": "", "value": 1}])[:6]
    n = len(items)
    kick = b.get("kicker", ""); unit = b.get("unit", "")
    vals = [float(it.get("value", 0)) for it in items]
    vmax = max(vals) or 1.0
    x0, x1 = (80, W - 80) if P else (W * 0.30, W - 160)
    top, base = (H * 0.30, H * 0.68) if P else (H * 0.24, H * 0.80)
    slot = (x1 - x0) / n
    sw_ = min(slot * 0.5, 150)
    r = random.Random(61)
    strokes, labs, seals = [], [], []
    for k, (it, v) in enumerate(zip(items, vals)):
        cx = x0 + slot * (k + 0.5)
        hgt = max(40.0, (base - top) * v / vmax)
        y_top = base - hgt
        w0 = sw_ * r.uniform(0.92, 1.05)
        lean = r.uniform(-0.04, 0.04) * hgt
        # one tapered stroke: a heavy head where the brush lands, the body narrowing a little, a split tail at the ground
        d_ = (f"M{cx - w0 * 0.5:.0f} {y_top + w0 * 0.18:.0f} Q {cx:.0f} {y_top - w0 * 0.22:.0f} {cx + w0 * 0.52:.0f} {y_top + w0 * 0.12:.0f} "
              f"L {cx + w0 * 0.44 + lean:.0f} {base - 6:.0f} Q {cx + lean:.0f} {base + 14:.0f} {cx - w0 * 0.42 + lean:.0f} {base - 2:.0f} Z")
        strokes.append(f'<g class="br b{k}"><path d="{d_}" fill="#171612" fill-opacity="{0.94 - 0.08 * (k % 2):.2f}" filter="url(#{cid}h)"/></g>')
        val_s = it.get("show", f"{v:g}")
        fpx = min(96 if P else 84, slot * 0.8 / max(1.0, sum(0.6 if c.isdigit() else fit.gw(c) for c in str(val_s)) + 0.34))
        sh_, sbw, sbh = fig_seal(X, val_s, "", fpx, cid, cls=f"fv v{k}")
        seals.append(f'<div style="position:absolute; left:{cx - sbw / 2:.0f}px; top:{y_top - sbh - 22:.0f}px; transform:rotate({(-1.5 if k % 2 else 1.2)}deg)">{sh_}</div>')
        lab = it.get("label", "")
        lfs = min(34 if P else 30, slot * 0.9 / max(1, len(lab)))
        labs.append(f'<div class="serif blab l{k}" style="left:{cx - slot / 2:.0f}px; width:{slot:.0f}px; top:{base + 26:.0f}px; text-align:center; font-size:{max(26, lfs):.0f}px; font-weight:700; letter-spacing:.08em">{X.rich(lab)}</div>')
    ground = (f'<path class="gl0" d="M{x0 - 30:.0f} {base + 4:.0f} C {x0 + (x1 - x0) * 0.3:.0f} {base - 4:.0f}, {x0 + (x1 - x0) * 0.7:.0f} {base + 10:.0f}, {x1 + 30:.0f} {base + 2:.0f}" '
              f'fill="none" stroke="#171612" stroke-width="7" stroke-linecap="round" filter="url(#{cid}r)"/>')
    kk = (f'<div class="serif kk halo" style="left:0; right:0; top:292px; text-align:center; font-size:42px; font-weight:700; letter-spacing:.24em">{X.rich(kick)}</div>' if P
          else f'<div class="vt kk halo" style="left:{W * 0.14:.0f}px; top:{top:.0f}px; font-size:42px; font-weight:700">{X.rich(kick)}</div>') if kick else ""
    un = f'<div class="serif un" style="left:{x0:.0f}px; top:{base + 90:.0f}px; font-size:26px; color:#4a443a; letter-spacing:.12em">{X.rich(unit)}</div>' if unit else ""
    inner = (f'<div style="position:absolute;inset:0;opacity:.4">{mountains(cid, X, 71, layers=2, top=0.74, amp=0.07, dark=0.45)}</div>'
             f'<svg class="svgl" viewBox="0 0 {W} {H}"><g filter="url(#{cid}b)">{ground}{"".join(strokes)}</g></svg>' + "".join(seals) + "".join(labs) + kk + un)
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    X.tw(f'tl.fromTo("{s} .gl0", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.6, ease:"power2.inOut"}}, {t + 0.1:.3f});')
    if kick: X.tw(f'tl.from("{s} .kk", {{opacity:0, y:-12, duration:0.6}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .blab", {{opacity:0, y:10, duration:0.5, stagger:0.08}}, {t + 0.35:.3f});')
    ats = [T(X, b, f"at_{k}", t, t + 0.5 + k * min(0.45, (d - 1.6) / max(1, n))) for k in range(n)]
    for k, ta in enumerate(ats):
        X.tw(f'tl.fromTo("{s} .b{k}", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power2.in"}}, {ta - 0.35:.3f});')
        X.tw(f'tl.fromTo("{s} .v{k}", {{scale:1.3, opacity:0}}, {{scale:1, opacity:1, duration:0.28, ease:"back.out(2.2)"}}, {ta + 0.1:.3f});')
        X.sfx(ta - 0.35, "brush"); X.sfx(ta + 0.12, "stamp")
    drift(X, f"{s} .cam", t, d, 1.03, 0, -6)


def share(b, X, t, d, cid):
    """a share as an ink-wash circle: a dry-brush ring (圆相) is drawn in one sweep, then wash floods the part that is
    the share; the figure is carved in a vermilion seal stamped across the rim."""
    P = X.portrait; W, H = X.W, X.H
    v = max(0.0, min(100.0, float(b.get("value", 50))))
    kick = b.get("kicker", ""); label = b.get("label", "")
    show = b.get("show", f"{v:g}%")
    cx, cy, R = (W / 2, H * 0.40, W * 0.36) if P else (W * 0.62, H * 0.47, H * 0.33)
    C = 2 * math.pi * (R * 0.5)
    ring_c = 2 * math.pi * R
    sector = (f'<circle class="sec" cx="{cx:.0f}" cy="{cy:.0f}" r="{R * 0.5:.0f}" fill="none" stroke="#171612" stroke-opacity=".34" stroke-width="{R * 0.86:.0f}" '
              f'stroke-dasharray="{C * v / 100:.1f} {C:.1f}" transform="rotate(-90 {cx:.0f} {cy:.0f})" filter="url(#{cid}sw)"/>')
    wf = (f'<defs><filter id="{cid}sw" x="-30%" y="-30%" width="160%" height="160%"><feTurbulence type="fractalNoise" baseFrequency="0.014" numOctaves="3" seed="37" result="n"/>'
          f'<feDisplacementMap in="SourceGraphic" in2="n" scale="38" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="7"/></filter></defs>')
    ring = (f'<circle class="ring" cx="{cx:.0f}" cy="{cy:.0f}" r="{R:.0f}" fill="none" stroke="#171612" stroke-width="{R * 0.09:.0f}" stroke-linecap="round" '
            f'stroke-dasharray="{ring_c * 0.97:.0f} {ring_c:.0f}" transform="rotate(-80 {cx:.0f} {cy:.0f})" filter="url(#{cid}r)"/>')
    fpx = min(200 if P else 170, R * 1.2 / max(1.0, sum(0.6 if c.isdigit() else fit.gw(c) for c in str(show)) + 0.34))
    sh_, sbw, sbh = fig_seal(X, show, "", fpx, cid, cls="fv")
    sx, sy = (cx - sbw / 2, cy + R - sbh * 0.45) if P else (W * 0.12, cy - sbh / 2)
    lfs, lhtml = ftext(X, label, W - 200 if P else W * 0.3, 36 if P else 32, 26, ls=0.12)
    lab = (f'<div class="serif lb halo" style="left:{100 if P else W * 0.12:.0f}px; {"right:100px; text-align:center;" if P else f"width:{W * 0.3:.0f}px;"} top:{(sy + sbh + 30) if P else (sy + sbh + 30):.0f}px; '
           f'font-size:{lfs}px; font-weight:600; line-height:1.3; letter-spacing:.12em; color:#4a443a">{lhtml}</div>') if label else ""
    kk = (f'<div class="serif kk halo" style="left:0; right:0; top:{cy - R - 110:.0f}px; text-align:center; font-size:42px; font-weight:700; letter-spacing:.24em">{X.rich(kick)}</div>' if P
          else f'<div class="serif kk halo" style="left:{W * 0.12:.0f}px; top:{sy - 90:.0f}px; font-size:40px; font-weight:700; letter-spacing:.2em">{X.rich(kick)}</div>') if kick else ""
    inner = (f'<div style="position:absolute;inset:0;opacity:.4">{mountains(cid, X, 83, layers=2, top=0.74, amp=0.07, dark=0.45)}</div>'
             f'<svg class="svgl" viewBox="0 0 {W} {H}">{wf}<g filter="url(#{cid}b)">{sector}{ring}</g></svg>'
             f'<div style="position:absolute; left:{sx:.0f}px; top:{sy:.0f}px; transform:rotate(-2deg)">{sh_}</div>' + lab + kk)
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    ta = T(X, b, "at_num", t, t + 0.9)
    if kick: X.tw(f'tl.from("{s} .kk", {{opacity:0, y:-12, duration:0.6}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .ring", {{attr:{{"stroke-dashoffset":{ring_c * 0.97:.0f}}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:0.8, ease:"power2.inOut"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "brush")
    X.tw(f'tl.fromTo("{s} .sec", {{attr:{{"stroke-dasharray":"0 {C:.1f}"}}}}, {{attr:{{"stroke-dasharray":"{C * v / 100:.1f} {C:.1f}"}}, duration:1.0, ease:"power2.out"}}, {ta - 0.6:.3f});')
    X.sfx(ta - 0.6, "wash")
    X.tw(f'tl.fromTo("{s} .fv", {{scale:1.3, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(2.2)"}}, {ta:.3f});')
    X.sfx(ta + 0.05, "stamp")
    if label: X.tw(f'tl.from("{s} .lb", {{opacity:0, duration:0.5}}, {ta + 0.3:.3f});')
    drift(X, f"{s} .cam", t, d, 1.035)


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
    px = min(colh / maxlen / 1.02, (W * (0.80 if P else 0.46)) / max(1, len(lines)) / 1.4, 158 if P else 120)
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
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
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
    name = b.get("title", X.channel); sub = b.get("sub", ""); cta = b.get("cta", "")
    px = min(H * (0.13 if P else 0.16), W * (0.8 if P else 0.5) / max(1, sum(fit.gw(c) for c in name)))
    svg, bw, bh = brush(X, name, b.get("font", "zhi-mang-xing"), px, flt=f"{cid}k")
    bx, by = (W - bw) / 2, H * (0.30 if P else 0.30)
    ssz = 128 if P else 140
    inner = (f'<div style="position:absolute;inset:0;opacity:.45">{mountains(cid, X, 61, layers=3, top=0.66, amp=0.1, dark=0.6)}</div>{mist(X, 3, 31)}'
             + seal(X, b.get("seal", "九帽"), ssz, style=f"left:{(W - ssz) / 2:.0f}px; top:{by - ssz - 40:.0f}px; transform:rotate(-3deg)")
             + f'<div class="nm" style="position:absolute; left:{bx:.0f}px; top:{by:.0f}px">{svg}</div>'
             + (f'<div class="serif sb" style="left:0; right:0; top:{by + bh + 30:.0f}px; text-align:center; font-size:{34 if P else 32}px; letter-spacing:.3em">{X.rich(sub)}</div>' if sub else "")
             + (f'<div class="serif ct" style="left:0; right:0; top:{by + bh + 100:.0f}px; text-align:center; font-size:{28 if P else 26}px; letter-spacing:.2em; color:var(--seal)">{X.rich(cta)}</div>' if cta else ""))
    X.clip(cid, t, d, furn(X, b, cid, inner, t, d), "scene", 2)
    s = f"#{cid}"
    opening(X, cid, t)
    stamp(X, f"{s} .seal", t + 0.15)
    write_on(X, f"{s} .nm", t + 0.4, dur=1.1, stagger=0.1)
    X.sfx(t + 0.45, "brush")
    X.tw(f'tl.from("{s} .sb, {s} .ct", {{opacity:0, y:12, duration:0.7, stagger:0.2}}, {t + 1.1:.3f});')
    X.tw(f'tl.fromTo("{s} .mist", {{x:-50}}, {{x:70, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    drift(X, f"{s} .cam", t, d, 1.03)


# ---------------------------------------------------------------- effects drawn in ink (aefx.FX_FRAME + .fx overrides)
FX_CSS = r"""
.ikg { overflow:hidden; }
.ikg .paper, .ikg svg { position:absolute; inset:0; width:100%; height:100%; }
.ikg .vig { position:absolute; inset:0; }
.ikg .mist { position:absolute; border-radius:50%; }
.st-ink .fx.ik-under { background:transparent !important; }
.ctx.ikf .ikh { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-serif); color:var(--fg);
  background:color-mix(in srgb, var(--bg) 86%, transparent); padding:3px 14px 3px 3px; border-radius:3px; }
.ctx.ikf .ikh b { font-weight:700; letter-spacing:.24em; } .ctx.ikf .ikh span { opacity:.62; letter-spacing:.2em; }
.ctx.ikf .ikh i { display:block; width:38px; height:2px; background:currentColor; opacity:.55; }
.ctx.ikf .ikh .sl { width:40px; height:40px; display:grid; place-items:center; background:var(--accent); color:#f4ecd9; border-radius:4px; font-weight:900; font-size:15px;
  line-height:1.05; writing-mode:vertical-rl; letter-spacing:.02em; transform:rotate(-3deg); }
.ctx.ikf .ikx { position:absolute; font-family:var(--f-latin); font-size:17px; letter-spacing:.12em; color:var(--accent); border:2px solid var(--accent);
  padding:3px 12px 4px; border-radius:3px; font-variant:small-caps; background:color-mix(in srgb, var(--bg) 86%, transparent); }
.ctx.ikf .ikc { position:absolute; left:0; right:0; text-align:center; }
.ctx.ikf .ikc .slip { display:inline-block; font-family:var(--f-cap); font-weight:600; line-height:1.3; color:#171612; white-space:nowrap;
  background:rgba(240,233,217,.95); padding:6px 22px 9px 28px; border-top:1.5px solid rgba(23,22,18,.6); border-bottom:1.5px solid rgba(23,22,18,.6);
  box-shadow:inset 7px 0 0 #b03a2e, 0 10px 28px rgba(30,20,10,.18); }
.ctx.ikf .ikc .em .emt { color:#a32f24; background-image:linear-gradient(transparent 80%, rgba(176,58,46,.38) 80%, rgba(176,58,46,.38) 94%, transparent 94%); }
.ctx.ikf .ikc .em .emb { display:none; }
.ctx.ikf .ikft { position:absolute; display:flex; justify-content:space-between; gap:24px; font-family:var(--f-serif); font-size:16px; color:var(--muted); letter-spacing:.06em; }
.ctx.ikf .ikft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; }
.ctx.ikf.photo .ikh, .ctx.ikf.photo .ikft { color:#f4ecd9; text-shadow:0 1px 8px rgba(0,0,0,.6); }
#root.v .ctx.ikf .ikc { padding:0 112px; } #root.v .ctx.ikf .ikc .slip { padding:6px 18px 9px 24px; }
/* effect internals, in ink */
.st-ink .fx .sub { font-family:var(--f-latin); font-style:italic; text-transform:none; letter-spacing:.26em; }
.st-ink .fx .sh { background-image:linear-gradient(110deg, var(--fg) 0%, var(--fg) 40%, var(--accent) 50%, var(--fg) 60%, var(--fg) 100%); }
.st-ink .fx .tw { font-family:var(--f-display) !important; }
.st-ink .fx .caret { color:var(--accent); }
.st-ink .fx .dfw { filter:blur(6vmin); }
.st-ink .fx .bl { opacity:.5; border-radius:46% 54% 41% 59% / 52% 44% 56% 48%; }
.st-ink .fx .bl:nth-child(3n+1) { background:color-mix(in srgb, var(--fg) 60%, transparent) !important; }
.st-ink .fx .bl:nth-child(3n+2) { background:color-mix(in srgb, var(--accent) 70%, transparent) !important; }
.st-ink .fx .bl:nth-child(3n) { background:color-mix(in srgb, var(--fg) 30%, transparent) !important; }
.st-ink .ct-root .em .emb, .st-ink .d2 .em .emb { display:block; background:color-mix(in srgb, var(--accent) 42%, transparent); border-radius:0; box-shadow:inset 0 -.1em 0 var(--accent); }
.st-ink .ct-root .em .emt, .st-ink .d2 .em .emt { color:var(--fg) !important; }
.st-ink .cp-sheet .em .emb { background:#ecc0b2; box-shadow:inset 0 -.1em 0 #b03a2e; } .st-ink .cp-sheet .em .emt { color:#111 !important; }
.st-ink .ct-mk, .st-ink .d2-mk { background:rgba(205,72,56,.45); border-radius:0; }
.st-ink .ct-view { border-radius:2px; background:color-mix(in srgb, var(--fg) 5%, var(--bg)); box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fg) 28%, transparent); }
.st-ink .ct-vbar b, .st-ink .ct-kick, .st-ink .d2-kick { background:#b03a2e; color:#f4ecd9; border-radius:2px; }
.st-ink .ct-sheet, .st-ink .cp-sheet, .st-ink .d2-sheet.dp-flat, .st-ink .dp-ph { border-radius:0;
  box-shadow:0 0 0 12px #d9ccae, 0 0 0 13px rgba(70,50,25,.35), 0 26px 54px rgba(25,15,5,.35); }
.st-ink .d2-sheet, .st-ink .df-p { border-radius:0; }
.st-ink .cp-ghost { border-radius:0; background:#d9ccae; }
.st-ink .cp-chip { border-radius:2px; border-color:#b03a2e; color:#b03a2e; font-family:var(--f-latin); }
.st-ink .ct-mono { border-radius:5px !important; background:#b03a2e !important; color:#f4ecd9 !important; font-family:var(--f-serif) !important; transform:rotate(-2deg); }
.st-ink .cp-year, .st-ink .cq-year { font-family:var(--f-display); font-weight:400; -webkit-text-stroke:0; color:color-mix(in srgb, var(--fg) 13%, transparent); }
.st-ink .cq-mark { font-family:var(--f-display); font-weight:400; }
.st-ink .ck-card { border-radius:2px; box-shadow:0 0 0 7px #d9ccae, 0 0 0 8px rgba(70,50,25,.3), 0 18px 40px rgba(25,15,5,.28); }
.st-ink .ck-hd i { border-radius:2px; }
.st-ink .ck-v { border-radius:4px; font-family:var(--f-serif); }
.st-ink .ck-v[style*="1f8a5b"] { --vc:#b03a2e !important; }
.st-ink .ck-tally b { color:var(--accent); font-family:var(--f-display); font-weight:400; }
.st-ink .fx .cb .cb-s { border-radius:1.4vmin .3vmin 1.4vmin .3vmin; }
.st-ink .fx .cb .cb-pin { border-radius:3px; font-family:var(--f-serif); }
.st-ink .fx .tp .tp-k { font-family:var(--f-serif); text-transform:none; letter-spacing:.2em; }
.st-ink .fx .tp .tp-pg { font-family:var(--f-serif); font-weight:600; }
.st-ink .fx .vt .vt-rule { background:color-mix(in srgb, var(--accent) 60%, transparent); }
.st-ink .fx .vt .vt-seal { background:#b03a2e; }
.st-ink .dp-q polygon { fill:rgba(176,58,46,.1); stroke:#c8463a; }
.st-ink .dp-cn { background:#c8463a; box-shadow:0 0 0 5px rgba(200,70,58,.3); }
.st-ink .dp-scan { background:linear-gradient(180deg, rgba(200,70,58,0), rgba(200,70,58,.28) 85%, #c8463a); }
.st-ink .d2-tag { font-family:var(--f-serif); border-radius:2px; }
.st-ink .d2-ttl, .st-ink .ck-ct, .st-ink .fx .cb .cb-k, .st-ink .fx .cb .cb-t { font-weight:400; }
"""


def _ground(X, cid, dark):
    """the paper under an effect: grain + fibres, layered mountains in the ground's own ink colour, mist, a vignette."""
    W, H, P = X.W, X.H, X.portrait
    r = random.Random(41)
    tint = "0 0 0 0 .92  0 0 0 0 .86  0 0 0 0 .74  0 0 0 .09 0" if dark else "0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .18  0 0 0 .22 0"
    fib_c = "rgba(236,228,210,.06)" if dark else "rgba(120,100,70,.09)"
    fib = "".join(f'<path d="M{r.uniform(0, W):.0f} {r.uniform(0, H):.0f} q {r.uniform(-60, 60):.0f} {r.uniform(-30, 30):.0f} {r.uniform(-160, 160):.0f} {r.uniform(-50, 50):.0f}" '
                  f'stroke="{fib_c}" stroke-width="{r.uniform(.6, 1.4):.1f}" fill="none"/>' for _ in range(50))
    grain = (f'<div class="paper"><svg viewBox="0 0 {W} {H}" preserveAspectRatio="none"><defs><filter id="{cid}gp"><feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="5"/>'
             f'<feColorMatrix type="matrix" values="{tint}"/></filter></defs><rect width="{W}" height="{H}" filter="url(#{cid}gp)" opacity=".6"/>{fib}</svg></div>')
    mts = (f'<div class="mtl" style="position:absolute; inset:0; color:var(--fg); opacity:{.5 if dark else .42}">'
           f'{mountains(cid + "g", X, 7 + X.beat["i"], layers=2, top=0.78 if P else 0.74, amp=0.11, dark=0.5, color="currentColor")}</div>')
    mc = "rgba(236,228,210,.07)" if dark else "rgba(250,246,236,.85)"
    m = random.Random(9 + X.beat["i"])
    mist_html = "".join(f'<i class="mist m{k}" style="left:{m.uniform(-.2, .6) * W:.0f}px; top:{m.uniform(.3, .75) * H:.0f}px; width:{m.uniform(.5, .8) * W:.0f}px; '
                        f'height:{m.uniform(.12, .2) * H:.0f}px; background:radial-gradient(closest-side, {mc}, rgba(0,0,0,0))"></i>' for k in range(2))
    vig = ("radial-gradient(ellipse 80% 75% at 50% 45%, rgba(255,240,210,.05), rgba(0,0,0,.42) 100%)" if dark
           else "radial-gradient(ellipse 75% 70% at 50% 46%, rgba(0,0,0,0) 55%, rgba(60,45,20,.16) 100%)")
    return f'{filters(cid + "g")}{grain}{mts}{mist_html}<div class="vig" style="background:{vig}"></div>'


def FX_FRAME(X, cid, t, d, p, k):
    """an effect card in ink: the effect sits on xuan paper (or an ink / vermilion / celadon wash) with mountains and mist
    under it, a seal + serif header, the spoken line on a paper slip with a vermilion edge, and a serif footnote.
    Calligraphic titles inside the effect pick up the ink-bleed edge."""
    X.css("ink", CSS); X.css("ink-fx", FX_CSS)
    P, W, H = X.portrait, X.W, X.H
    dark = p.get("theme") in ("ink", "red")
    eff = next((e for e in reversed(X.els) if e.startswith(f'<div id="{cid}"')), "")
    if "background:var(--bg)" in eff and not k["photo"]:      # the effect paints a flat ground: draw ours under it instead
        X.els[X.els.index(eff)] = eff.replace('class="clip scene fx', 'class="clip scene fx ik-under', 1)
        X.clip(f"{cid}g", t, d, _ground(X, cid, dark), "ikg", 2, track=19, sty=k["sty"] + ";background:var(--bg)")
        X.css(f"ink-fx-{cid}", f"#{cid} .big, #{cid} .d2-ttl, #{cid} .ck-ct, #{cid} .cb-k, #{cid} .vt-col {{ filter:url(#{cid}gk); }} "
                               f"#{cid} .cb-s i {{ filter:url(#{cid}gd); }}")
        X.tw(f'tl.fromTo("#{cid}g .mt0", {{x:0}}, {{x:-40, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("#{cid}g .mt1", {{x:0}}, {{x:-90, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("#{cid}g .mist", {{x:-50}}, {{x:70, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    hx, hy = (56, 206) if P else (80, 40)
    X.used_text.update("" + X.channel + "九帽")
    hd = (f'<div class="ikh" style="left:{hx}px; top:{hy}px; font-size:{22 if P else 20}px"><b>{X.rich(X.channel)}</b><i></i><span>{k["topic"]}</span></div>'
          f'<div class="ikx" style="right:{hx}px; top:{hy + 5}px">{k["fxid"]}</div>')
    cap_pos = "top:1330px" if P else "bottom:62px"
    cap = f'<div class="ikc" style="{cap_pos}"><span class="slip" style="font-size:{k["cap_px"]}px">{k["cap"]}</span></div>'
    ft_pos = f"left:{hx}px; right:120px; top:1478px" if P else "left:80px; right:80px; bottom:20px"     # 9:16: the source ends clear of the right-hand buttons
    ft = f'<div class="ikft" style="{ft_pos}; font-size:{17 if P else 16}px"><div>{k["foot"]}</div><div>{k["src"]}</div></div>' if (k["foot"] or k["src"]) else ""
    X.clip(f"{cid}c", t, d, hd + cap + ft, f"ctx ikf{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
    X.tw(f'tl.fromTo("#{cid}c .slip", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power2.inOut"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid}c .ikh .sl", {{scale:1.4, opacity:0, duration:0.3, ease:"back.out(2.4)"}}, {t + 0.1:.3f});')


SCENES = {"brush": brush_scene, "column": column, "drops": drops, "scrolls": scrolls, "wash": wash,
          "handscroll": handscroll, "splash": splash, "bars": bars, "share": share, "couplet": couplet, "seal": seal_outro}
