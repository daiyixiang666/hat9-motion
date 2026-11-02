"""pixel · 像素复古游戏风 —— 8/16-bit 游戏的视觉语言做口播：Celeste / Stardew 式的克制像素美术，不是糊成一片的马赛克。
一个 16 色调色板（Sweetie 16），逻辑分辨率 320×180（竖屏 180×320）、每个像素放大 6 倍；所有精灵都在构建时用 Pillow 无抗锯齿画出、
自动描边、最近邻放大；中文用缝合像素 Fusion Pixel 12 栅格成 1-bit 位图（只用 12 / 24 px，放不下就换行，不缩小），
英文和数字用 Press Start 2P / VT323。
动作一律走「整像素、整帧」：步进缓动、精灵帧动画、镜头按像素格平移；HUD（金币、计时、关卡）每页常驻。

场景（SCENES，全部自写）：stage 横版关卡开场（视差山脉 + 奔跑角色 + 销量计数）· online 在线人数（像素人潮 + 血条式仪表）·
treasure 宝箱金币（市场规模）· crowd 每两人一个（像素小人点阵）· world 像素世界地图（海外收入流向）·
levelup 两条经验条对比 + 升级横幅 · dialog RPG 对话框（打字机 + 选项光标）· outro 继续游戏落版（像素柴犬主持人）。
输入自适应：标题 / 台词长短、条目数、地图高亮国家数都按 scripts/h9/fit.py 和本文件的位图排版自动缩放。
"""
import hashlib, json, math
from pathlib import Path

from h9 import fit, fonts

STYLE = {
    "name": "像素复古游戏风", "en": "Pixel", "benchmarks": ["Celeste", "Stardew Valley", "Shovel Knight", "GBA / SNES UI"],
    "tokens": {
        "bg": "#1a1c2c", "fg": "#f4f4f4", "muted": "#94b0c2", "accent": "#ffcd75", "accent2": "#73eff7", "alert": "#b13e53",
        "line": "#333c57", "paper": "#1a1c2c", "ink": "#1a1c2c", "card": "#29366f", "card-fg": "#f4f4f4",
        "cap-bg": "#1a1c2c", "cap-fg": "#f4f4f4", "cap-size": "38px", "cap-weight": "700", "cap-pad": "10px 22px 12px", "cap-radius": "0",
        "cap-shadow": "0 0 0 6px #f4f4f4, 0 0 0 12px #1a1c2c", "cap-bottom": "60px", "cap-em": "#ffcd75",
        "punch-top": "70%", "punch-size": "64px",
    },
    "fonts": {"display": "fusion-pixel", "body": "fusion-pixel", "pixel": "press-start-2p", "vt": "vt323", "mono": "vt323"},
    "motion": {"ease": "steps(6)", "dur": 0.4, "stagger": 0.05, "cut": "hard", "transition": "cut", "em": "static", "camera": "none"},
    "layers": [],
    "captions": False,          # the style draws its own bitmap captions (see captions()); beats with "cap": false skip them
    "mascot": {"mode": "none"},
    # the shared realistic SFX would break the 8-bit world: scenes synthesise chip sounds instead (see chip())
    "sfx": {k: None for k in ("enter", "pop", "hit", "click", "count", "type", "transition", "cut", "wipe", "whoosh", "mascot", "tick")},
    "css": """
.st-pixel .cap .cp { font-family:var(--f-display); letter-spacing:.04em; }
#root.v.st-pixel .cap { padding:0 140px 0 60px; }
/* effects drawn in this style: square corners, no blur, hard stepped type shadows, a 6-px dither on the ground,
   photos and video mosaicked + posterised through the #pxmo filter that FX_FRAME puts on the page */
.st-pixel .fx { background-image:repeating-conic-gradient(rgba(26,28,44,.07) 0 25%, transparent 0 50%) !important; background-size:12px 12px !important; }
.st-pixel .fx * { border-radius:0 !important; }
.st-pixel .fx .big { text-shadow:.07em .07em 0 var(--line); }
.st-pixel .fx .c, .st-pixel .fx .w, .st-pixel .fx .ln, .st-pixel .fx .big, .st-pixel .fx .fw-w { filter:none !important; }
.st-pixel .fx img:not(.mx-cov), .st-pixel .fx video:not(.mx-cov) { filter:url(#pxmo) !important; image-rendering:pixelated; }
""",
    # the four page themes an effect can ask for, all from Sweetie 16: menu grey, night, boss red, desert sand
    "fx_themes": {
        "paper": {"bg": "#f4f4f4", "fg": "#1a1c2c", "muted": "#333c57", "accent": "#b13e53", "card": "#94b0c2", "card-fg": "#1a1c2c", "line": "#94b0c2"},
        "ink":   {"bg": "#1a1c2c", "fg": "#f4f4f4", "muted": "#94b0c2", "accent": "#ffcd75", "card": "#29366f", "card-fg": "#f4f4f4", "line": "#333c57"},
        "red":   {"bg": "#b13e53", "fg": "#f4f4f4", "muted": "#f4f4f4", "accent": "#ffcd75", "card": "#1a1c2c", "card-fg": "#f4f4f4", "line": "#5d275d"},
        "lemon": {"bg": "#ffcd75", "fg": "#1a1c2c", "muted": "#5d275d", "accent": "#b13e53", "card": "#f4f4f4", "card-fg": "#1a1c2c", "line": "#ef7d57"},
    },
}

# ------------------------------------------------------------------ palette: Sweetie 16 (GrafxKid)
PAL = {"k": "#1a1c2c", "p": "#5d275d", "r": "#b13e53", "o": "#ef7d57", "y": "#ffcd75", "l": "#a7f070", "g": "#38b764", "t": "#257179",
       "b": "#29366f", "u": "#3b5dc9", "s": "#41a6f6", "c": "#73eff7", "w": "#f4f4f4", "e": "#94b0c2", "m": "#566c86", "d": "#333c57"}
P = 6                      # screen pixels per art pixel


def rgb(c):
    c = PAL.get(c, c).lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


# ------------------------------------------------------------------ sprite factory (build time, Pillow, no antialiasing)
def _canvas(w, h):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    return im, ImageDraw.Draw(im)


def outline(im, col="k", diag=False):
    """1-art-pixel outline around everything opaque (the clean Celeste-style edge)."""
    from PIL import Image
    w, h = im.size
    src = im.load()
    out = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0)); out.paste(im, (1, 1))
    o = out.load(); c = rgb(col)
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (1, 1), (-1, 1), (1, -1)] if diag else [])
    for y in range(h + 2):
        for x in range(w + 2):
            if o[x, y][3]: continue
            for dx, dy in nb:
                sx, sy = x - 1 + dx, y - 1 + dy
                if 0 <= sx < w and 0 <= sy < h and src[sx, sy][3]:
                    o[x, y] = c; break
    return out


def shiba(frame=0):
    """the channel host: a shiba in round glasses and a top hat, 26×28 art px (frame 1 = blink)."""
    im, d = _canvas(26, 28)
    # top hat
    d.rectangle([8, 0, 17, 7], fill=rgb("d")); d.rectangle([9, 1, 10, 6], fill=rgb("m"))
    d.rectangle([8, 6, 17, 7], fill=rgb("r"))
    d.rectangle([5, 8, 20, 9], fill=rgb("d"))
    # ears
    d.polygon([(3, 15), (5, 7), (10, 12)], fill=rgb("o")); d.polygon([(22, 15), (20, 7), (15, 12)], fill=rgb("o"))
    d.polygon([(5, 13), (6, 10), (8, 12)], fill=rgb("y")); d.polygon([(20, 13), (19, 10), (17, 12)], fill=rgb("y"))
    # head
    d.ellipse([3, 10, 22, 26], fill=rgb("o"))
    d.ellipse([6, 17, 19, 26], fill=rgb("w"))
    d.ellipse([5, 15, 9, 19], fill=rgb("w")); d.ellipse([16, 15, 20, 19], fill=rgb("w"))
    # glasses + eyes
    for x0 in (6, 14):
        d.rectangle([x0, 14, x0 + 4, 17], outline=rgb("k"))
        if frame == 1: d.line([x0 + 1, 16, x0 + 3, 16], fill=rgb("k"))
        else: d.rectangle([x0 + 2, 15, x0 + 3, 16], fill=rgb("k"))
    d.line([11, 15, 13, 15], fill=rgb("k"))
    d.rectangle([12, 19, 13, 20], fill=rgb("k"))           # nose
    d.line([11, 22, 12, 23], fill=rgb("k")); d.line([13, 23, 14, 22], fill=rgb("k"))
    d.point([(7, 21), (18, 21)], fill=rgb("r"))             # blush
    # collar / shirt
    d.rectangle([7, 25, 18, 27], fill=rgb("b"))
    return outline(im)


def monkey(frame=0):
    """a generic running monkey with a staff (side view), 28×24 art px, 4-frame run."""
    im, d = _canvas(30, 24)
    bob = (0, -1, 0, -1)[frame % 4]
    leg = frame % 4
    y0 = 4 + bob
    # staff
    d.line([2, y0 + 12, 28, y0 + 4], fill=rgb("r"), width=1); d.line([2, y0 + 13, 28, y0 + 5], fill=rgb("r"))
    d.rectangle([1, y0 + 12, 3, y0 + 13], fill=rgb("y")); d.rectangle([27, y0 + 4, 29, y0 + 5], fill=rgb("y"))
    # body
    d.ellipse([9, y0 + 6, 19, y0 + 15], fill=rgb("o"))
    d.ellipse([11, y0 + 9, 17, y0 + 15], fill=rgb("y"))
    # head
    d.ellipse([13, y0 - 2, 23, y0 + 7], fill=rgb("o"))
    d.ellipse([16, y0 + 1, 23, y0 + 7], fill=rgb("y"))
    d.rectangle([13, y0, 23, y0 + 1], fill=rgb("y"))        # golden headband
    d.point([(20, y0 + 3)], fill=rgb("k")); d.point([(22, y0 + 5)], fill=rgb("k"))
    d.ellipse([12, y0 + 1, 14, y0 + 4], fill=rgb("o"))       # ear
    # tail
    d.arc([3, y0 + 4, 11, y0 + 12], 120, 300, fill=rgb("o"))
    # legs (run cycle)
    L = [((10, 15, 7, 20), (16, 15, 19, 20)), ((11, 15, 11, 20), (15, 15, 16, 20)), ((10, 15, 13, 20), (16, 15, 14, 20)), ((11, 15, 9, 19), (15, 15, 18, 19))][leg]
    for x1, y1, x2, y2 in L:
        d.line([x1, y0 + y1 - 4 + 4, x2, y0 + y2], fill=rgb("o"), width=2)
    return outline(im)


def coin(frame=0):
    im, d = _canvas(8, 8)
    w = (6, 4, 1, 4)[frame % 4]
    x0 = 4 - w // 2 - (1 if w > 1 else 0)
    d.ellipse([x0, 0, x0 + w + (1 if w > 1 else 0), 7], fill=rgb("y"))
    if w > 2: d.line([x0 + 2, 2, x0 + 2, 5], fill=rgb("w"))
    return outline(im)


def chest(open_=False):
    im, d = _canvas(18, 15)
    d.rectangle([1, 7, 16, 14], fill=rgb("o")); d.rectangle([1, 7, 16, 8], fill=rgb("r"))
    d.rectangle([1, 12, 16, 12], fill=rgb("r"))
    if open_:
        d.rectangle([1, 1, 16, 4], fill=rgb("r")); d.rectangle([2, 2, 15, 3], fill=rgb("o"))
        d.rectangle([3, 5, 14, 7], fill=rgb("y"))
    else:
        d.rectangle([1, 3, 16, 7], fill=rgb("o")); d.rectangle([1, 3, 16, 4], fill=rgb("r"))
    d.rectangle([8, 7, 9, 10], fill=rgb("y"))
    return outline(im)


def person(variant=0):
    im, d = _canvas(5, 8)
    skin = ("y", "o", "y", "w")[variant % 4]; shirt = ("u", "g", "r", "s", "p", "l")[variant % 6]
    d.rectangle([1, 0, 3, 2], fill=rgb(skin)); d.rectangle([0, 3, 4, 6], fill=rgb(shirt)); d.rectangle([1, 7, 3, 7], fill=rgb("d"))
    return im


def heart():
    im, d = _canvas(7, 6)
    d.polygon([(0, 1), (1, 0), (2, 0), (3, 1), (4, 0), (5, 0), (6, 1), (6, 2), (3, 5), (0, 2)], fill=rgb("r"))
    d.point([(1, 1)], fill=rgb("w"))
    return outline(im)


def star():
    im, d = _canvas(9, 9)
    d.polygon([(4, 0), (5, 3), (8, 3), (6, 5), (7, 8), (4, 6), (1, 8), (2, 5), (0, 3), (3, 3)], fill=rgb("y"))
    return outline(im)


def phone():
    im, d = _canvas(12, 19)
    d.rectangle([0, 0, 11, 18], fill=rgb("d")); d.rectangle([1, 2, 10, 15], fill=rgb("c"))
    d.rectangle([3, 9, 4, 10], fill=rgb("r")); d.rectangle([6, 6, 7, 7], fill=rgb("y")); d.rectangle([2, 12, 9, 12], fill=rgb("g"))
    d.point([(5, 17), (6, 17)], fill=rgb("m"))
    return outline(im)


def pad():
    im, d = _canvas(18, 10)
    d.rounded_rectangle([0, 0, 17, 9], radius=3, fill=rgb("e"))
    d.rectangle([3, 4, 6, 5], fill=rgb("k")); d.rectangle([4, 3, 5, 6], fill=rgb("k"))
    d.point([(12, 3), (14, 5)], fill=rgb("r")); d.point([(12, 5)], fill=rgb("u")); d.point([(14, 3)], fill=rgb("g"))
    return outline(im)


def trophy():
    im, d = _canvas(14, 15)
    d.rectangle([3, 0, 10, 6], fill=rgb("y")); d.ellipse([3, 2, 10, 9], fill=rgb("y"))
    d.arc([0, 1, 4, 6], 90, 270, fill=rgb("y")); d.arc([9, 1, 13, 6], 270, 90, fill=rgb("y"))
    d.rectangle([6, 9, 7, 11], fill=rgb("o")); d.rectangle([3, 12, 10, 14], fill=rgb("o"))
    d.line([5, 1, 5, 5], fill=rgb("w"))
    return outline(im)


def scaled(im, k=P):
    from PIL import Image
    return im.resize((im.width * k, im.height * k), Image.NEAREST)


# ------------------------------------------------------------------ bitmap text (CJK and Latin, 1-bit, outlined)
# Chinese is set in 缝合像素 Fusion Pixel 12 (a real 12-px pixel font, OFL) at 12 or 24 px only — the sizes where its grid
# lands on whole pixels; text that does not fit wraps onto more lines instead of shrinking. Without the font installed it
# falls back to Noto Sans SC rasterised 1-bit at any size.
_FONT = {}
SIZES = (24, 12)


def cjk_font():
    if "cjk" not in _FONT:
        meta = fonts.REG.get("fusion-pixel")
        _FONT["cjk"] = "fusion-pixel" if meta and fonts.find(meta["file"]) else "noto-sans-sc"
    return _FONT["cjk"]


def snap(px):
    """the size actually drawn: 24 or 12 with the pixel font, anything with the fallback."""
    if cjk_font() != "fusion-pixel": return px
    return 24 if px >= 18 else 12


def _font(px, fid=None):
    from PIL import ImageFont
    fid = fid or cjk_font()
    px = snap(px) if fid == cjk_font() else px
    key = (px, fid)
    if key not in _FONT:
        f = ImageFont.truetype(str(fonts.find(fonts.REG[fid]["file"])), px)
        if fid == "noto-sans-sc":                 # the variable fallback is set heavy; the pixel font is static
            try: f.set_variation_by_axes([900 if px <= 14 else 800])
            except Exception: pass
        _FONT[key] = f
    return _FONT[key]


def bitmap_text(text, px=12, col="w", edge="k", shadow="b", fid=None):
    """a string as crisp 1-bit art pixels: a 1-px outline (4-neighbour, so 1-px counters stay open) and a 1-px drop
    shadow 2 px down-right. returns RGBA at art scale."""
    from PIL import Image, ImageDraw
    f = _font(px, fid)
    l, t, r, b = f.getbbox(text)
    w, h = max(1, r - l), max(1, b - t)
    mask = Image.new("1", (w + 2, h + 2), 0)
    dr = ImageDraw.Draw(mask); dr.fontmode = "1"
    dr.text((1 - l, 1 - t), text, font=f, fill=1)
    W, H = mask.size
    im = Image.new("RGBA", (W + 3, H + 3), (0, 0, 0, 0))
    m = mask.load(); o = im.load()
    ce, cf, cs = rgb(edge) if edge else None, rgb(col), rgb(shadow) if shadow else None
    on = [(x, y) for y in range(H) for x in range(W) if m[x, y]]
    if cs:
        for x, y in on: o[x + 3, y + 3] = cs
    if ce:
        for x, y in on:
            for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)): o[x + 1 + dx, y + 1 + dy] = ce
    for x, y in on: o[x + 1, y + 1] = cf
    return im


def bitmap_lines(text, max_w_art, px_max=24, max_lines=3, **kw):
    """a (possibly long) line in a width of art px: the biggest of 24 / 12 whose word-wrapped lines fit max_lines,
    else 12 px on as many lines as it takes. returns ([RGBA lines], px)."""
    for px in SIZES:
        if px > max(px_max, 12): continue
        lines = wrap(text, max_w_art, px)
        if len(lines) <= max_lines: return [bitmap_text(x, px, **kw) for x in lines], px
    return [bitmap_text(x, 12, **kw) for x in wrap(text, max_w_art, 12)], 12


# ------------------------------------------------------------------ world map raster (Natural Earth, Chinese view, public domain)
def _topo_rings(path):
    d = json.loads(Path(path).read_text())
    sx, sy = d["transform"]["scale"]; tx, ty = d["transform"]["translate"]
    arcs = []
    for a in d["arcs"]:
        x = y = 0; pts = []
        for dx, dy in a:
            x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)
    def ring(ix):
        pts = []
        for i in ix:
            seg = arcs[i] if i >= 0 else arcs[~i][::-1]
            pts += seg if not pts else seg[1:]
        return pts
    out = []
    for g in d["objects"]["countries"]["geometries"]:
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]] if g["type"] == "Polygon" else []
        out.append((g.get("properties", {}).get("ISO_A2", ""), [[ring(r) for r in poly] for poly in polys]))
    return out


# ------------------------------------------------------------------ build-time asset cache (any edit of this file re-draws every PNG)
SRCV = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:6]


def asset_png(X, name, im_fn):
    """make a PNG once per build (cached by name) under assets/px/ and return its url."""
    out = X.out / "assets" / "px"; out.mkdir(parents=True, exist_ok=True)
    p = out / f"{name}-{SRCV}.png"
    if not p.exists():
        im = im_fn()
        im.save(p)
    return f"assets/px/{p.name}"


def png_size(X, url):
    from PIL import Image
    with Image.open(X.out / url) as im: return im.size


def hkey(*a): return hashlib.sha1(json.dumps(a, ensure_ascii=False).encode()).hexdigest()[:10]


def sheet(X, name, frames_fn, n):
    """horizontal sprite sheet of n frames (art scale) -> (url, frame_w, frame_h) at art scale."""
    from PIL import Image
    def mk():
        fr = [frames_fn(i) for i in range(n)]
        W, H = max(f.width for f in fr), max(f.height for f in fr)
        s = Image.new("RGBA", (W * n, H), (0, 0, 0, 0))
        for i, f in enumerate(fr): s.paste(f, (i * W + (W - f.width) // 2, H - f.height))
        return s
    url = asset_png(X, name, mk)
    w, h = png_size(X, url)
    return url, w // n, h


# ------------------------------------------------------------------ backgrounds (art scale PNGs)
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def sky(w, h, cols=("b", "u", "s"), bands=None):
    """vertical gradient through palette colours with 4×4 ordered dithering at each seam (no smooth gradients ever)."""
    from PIL import Image
    im = Image.new("RGBA", (w, h)); o = im.load()
    n = len(cols) - 1
    for y in range(h):
        f = y / max(h - 1, 1) * n; i = min(int(f), n - 1); fr = f - i
        for x in range(w):
            o[x, y] = rgb(cols[i + 1] if fr * 16 > BAYER[y % 4][x % 4] else cols[i])
    return im


def ridge(w, h, col, seed=1, amp=0.45, base=0.55, rough=1.0, cap=None):
    """a stepped mountain / hill silhouette (deterministic sum of sines), optional snow-cap colour."""
    from PIL import Image
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); o = im.load()
    for x in range(w):
        v = 0.0
        for k, (f, a) in enumerate(((1.0, 1.0), (2.3, 0.5), (5.1, 0.22 * rough), (11.7, 0.1 * rough))):
            v += a * math.sin(x / w * math.tau * f + seed * (k + 1) * 1.7)
        top = int(h * (base - amp * v / 1.8))
        top = max(0, min(h - 1, top))
        for y in range(top, h):
            o[x, y] = rgb(cap) if cap and y < top + 2 and v > 0.9 else rgb(col)
    return im


def clouds(w, h, seed=3, n=6, col="w", shade="e"):
    from PIL import ImageDraw, Image
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in range(n):
        x = int((k + 0.5) / n * w + 18 * math.sin(seed + k * 2.1)); y = int(h * (0.15 + 0.5 * ((k * 37 + seed) % 7) / 7))
        cw = 18 + (k * 13 + seed) % 16
        d.rectangle([x, y + 3, x + cw, y + 7], fill=rgb(shade))
        d.rectangle([x + 2, y + 1, x + cw - 3, y + 5], fill=rgb(col)); d.rectangle([x + 6, y - 2, x + cw - 8, y + 2], fill=rgb(col))
    return im


def ground(w, h, top="l", grass="g", dirt="p", speck="r"):
    from PIL import Image
    im = Image.new("RGBA", (w, h), rgb(dirt)); o = im.load()
    for x in range(w):
        g = 3 + (1 if (x // 3) % 4 == 0 else 0)
        for y in range(min(h, g + 2)):
            o[x, y] = rgb(top if y < 1 or (y < g and (x + y) % 5 == 0) else grass)
        for y in range(g + 2, h):
            if (x * 7 + y * 13) % 29 == 0: o[x, y] = rgb(speck)
    return im


def soil(w, h, seed=3):
    """grass lip + dirt strata with buried stones, darkening with depth (dithered) — fills the tall 9:16 ground."""
    from PIL import ImageDraw
    im = ground(w, h); d = ImageDraw.Draw(im); o = im.load()
    for y in range(8, h):
        f = min(1.0, (y - 8) / max(h * 0.8, 1))
        for x in range(w):
            if f * 16 > BAYER[y % 4][x % 4] + 4: o[x, y] = rgb("k")
    for k in range(int(w * h / 260)):
        x = (k * 97 + seed * 31) % w; y = 10 + (k * 61 + seed * 7) % max(1, h - 14)
        r = 2 + (k % 3)
        d.rectangle([x, y, x + r * 2, y + r], fill=rgb("d")); d.line([x + 1, y, x + r * 2 - 1, y], fill=rgb("m"))
    return im


def block(kind="q"):
    """the ? block (16×16) and its spent state."""
    im, d = _canvas(16, 16)
    if kind == "q":
        d.rectangle([0, 0, 15, 15], fill=rgb("o")); d.rectangle([1, 1, 14, 14], fill=rgb("y")); d.line([1, 14, 14, 14], fill=rgb("o")); d.line([14, 1, 14, 14], fill=rgb("o"))
        for (x, y) in ((2, 2), (12, 2), (2, 12), (12, 12)): d.point([(x, y)], fill=rgb("r"))
        q = [(6, 3), (7, 3), (8, 3), (9, 3), (5, 4), (6, 4), (9, 4), (10, 4), (9, 5), (10, 5), (8, 6), (9, 6), (7, 7), (8, 7), (7, 8), (8, 8), (7, 10), (8, 10), (7, 11), (8, 11)]
        d.point([(x + 1, y + 1) for x, y in q], fill=rgb("r")); d.point(q, fill=rgb("w"))
    else:
        d.rectangle([0, 0, 15, 15], fill=rgb("r")); d.rectangle([1, 1, 14, 14], fill=rgb("o"))
    return outline(im)


def person2(variant=0, grey=False):
    """a 9×14 villager (bigger than person()); grey = the unlit silhouette."""
    im, d = _canvas(9, 14)
    if grey: skin, hair, shirt, legs = "e", "m", "m", "d"
    else:
        skin = ("y", "o", "y", "w")[variant % 4]; hair = ("k", "p", "r", "d", "o")[variant % 5]
        shirt = ("u", "g", "r", "s", "p", "o", "c", "l")[variant % 8]; legs = ("b", "d", "t")[variant % 3]
    d.rectangle([2, 1, 6, 5], fill=rgb(skin)); d.rectangle([2, 0, 6, 1], fill=rgb(hair)); d.point([(2, 2), (6, 2)], fill=rgb(hair))
    if not grey: d.point([(3, 3), (5, 3)], fill=rgb("k"))
    d.rectangle([1, 6, 7, 10], fill=rgb(shirt)); d.rectangle([0, 7, 0, 9], fill=rgb(skin)); d.rectangle([8, 7, 8, 9], fill=rgb(skin))
    d.rectangle([2, 11, 3, 13], fill=rgb(legs)); d.rectangle([5, 11, 6, 13], fill=rgb(legs))
    return outline(im)


def chest2(open_=False):
    """the big treasure chest, 34×27 art px."""
    im, d = _canvas(34, 27)
    d.rectangle([1, 13, 32, 26], fill=rgb("o"))
    for y in (17, 21): d.line([1, y, 32, y], fill=rgb("r"))
    d.rectangle([4, 13, 6, 26], fill=rgb("y")); d.rectangle([27, 13, 29, 26], fill=rgb("y"))
    if open_:
        d.rectangle([1, 2, 32, 9], fill=rgb("r")); d.rectangle([3, 4, 30, 8], fill=rgb("p"))
        d.rectangle([4, 2, 6, 9], fill=rgb("y")); d.rectangle([27, 2, 29, 9], fill=rgb("y"))
        d.rectangle([2, 10, 31, 13], fill=rgb("y")); d.rectangle([7, 9, 26, 11], fill=rgb("w"))
        for x in (9, 15, 21): d.rectangle([x, 8, x + 3, 9], fill=rgb("y"))
    else:
        d.rounded_rectangle([1, 3, 32, 13], radius=4, fill=rgb("o"))
        d.line([1, 8, 32, 8], fill=rgb("r")); d.line([3, 4, 30, 4], fill=rgb("y"))
        d.rectangle([4, 3, 6, 13], fill=rgb("y")); d.rectangle([27, 3, 29, 13], fill=rgb("y"))
    d.rectangle([14, 11, 19, 17], fill=rgb("y")); d.rectangle([16, 13, 17, 15], fill=rgb("k"))
    return outline(im)


def bricks(w, h, col="d", mortar="k", hi="m"):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (w, h), rgb(mortar)); d = ImageDraw.Draw(im)
    for r in range(0, h, 8):
        off = 8 if (r // 8) % 2 else 0
        for x in range(-off, w, 16):
            d.rectangle([x + 1, r + 1, x + 15, r + 7], fill=rgb(col)); d.line([x + 1, r + 1, x + 14, r + 1], fill=rgb(hi))
    return im


def rays(w, h, n=9, col="y", alt="o"):
    """light fanning up out of the chest (hard-edged wedges)."""
    from PIL import ImageDraw, Image
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy = w / 2, h
    for k in range(n):
        a0 = math.pi * (0.08 + 0.84 * k / n); a1 = a0 + math.pi * 0.84 / n * 0.5
        R = h * 1.3
        d.polygon([(cx, cy), (cx - R * math.cos(a0), cy - R * math.sin(a0)), (cx - R * math.cos(a1), cy - R * math.sin(a1))], fill=rgb(col if k % 2 else alt))
    return im


def flame(frame=0):
    im, d = _canvas(7, 11)
    if frame % 2 == 0:
        d.polygon([(3, 0), (6, 6), (5, 9), (1, 9), (0, 6)], fill=rgb("o")); d.polygon([(3, 3), (5, 7), (4, 9), (2, 9), (1, 7)], fill=rgb("y"))
    else:
        d.polygon([(2, 0), (6, 5), (5, 9), (1, 9), (0, 5)], fill=rgb("o")); d.polygon([(3, 2), (5, 6), (4, 9), (2, 9), (1, 6)], fill=rgb("y"))
    d.rectangle([2, 9, 4, 10], fill=rgb("w"))
    return outline(im)


def torch():
    im, d = _canvas(5, 10)
    d.rectangle([1, 0, 3, 2], fill=rgb("m")); d.rectangle([2, 3, 2, 9], fill=rgb("r"))
    return outline(im)


def coin_stack():
    im, d = _canvas(18, 14)
    for cx, n in ((3, 3), (9, 5), (15, 2)):
        for k in range(n):
            y = 12 - k * 2
            d.rectangle([cx - 3, y - 1, cx + 2, y], fill=rgb("y")); d.line([cx - 3, y, cx + 2, y], fill=rgb("o"))
    return outline(im)


def bag():
    """a money bag with a yuan sign, 16×18 art px."""
    im, d = _canvas(16, 18)
    d.ellipse([1, 5, 14, 17], fill=rgb("y")); d.polygon([(4, 0), (11, 0), (9, 4), (6, 4)], fill=rgb("y"))
    d.rectangle([5, 4, 10, 5], fill=rgb("o"))
    for x, y in ((5, 8), (6, 9), (10, 8), (9, 9)): d.point([(x, y)], fill=rgb("o"))
    d.rectangle([7, 10, 8, 15], fill=rgb("o")); d.line([5, 11, 10, 11], fill=rgb("o")); d.line([5, 13, 10, 13], fill=rgb("o"))
    d.point([(3, 8), (3, 9), (4, 7)], fill=rgb("w"))
    return outline(im)


def bang():
    im, d = _canvas(3, 9)
    d.rectangle([0, 0, 2, 5], fill=rgb("y")); d.rectangle([0, 7, 2, 8], fill=rgb("y"))
    return outline(im)


def field(w, h, seed=4):
    """a grass field with blades and flowers (dialog scene ground)."""
    from PIL import Image
    im = Image.new("RGBA", (w, h), rgb("g")); o = im.load()
    for y in range(h):
        for x in range(w):
            v = (x * 73 + y * 151 + seed * 17) % 97
            if v < 9: o[x, y] = rgb("l")
            elif v < 12 and y > 2: o[x, y] = rgb("t")
    for k in range(w // 14):
        x = (k * 37 + seed * 11) % (w - 3); y = 3 + (k * 23) % max(1, h - 6)
        c = ("w", "y", "r", "c")[k % 4]
        o[x + 1, y] = rgb(c); o[x, y + 1] = rgb(c); o[x + 2, y + 1] = rgb(c); o[x + 1, y + 2] = rgb(c); o[x + 1, y + 1] = rgb("y" if c != "y" else "o")
    for x in range(w): o[x, 0] = rgb("l")
    return im


def tree():
    im, d = _canvas(16, 22)
    d.rectangle([7, 14, 9, 21], fill=rgb("r"))
    d.ellipse([0, 2, 15, 16], fill=rgb("t")); d.ellipse([2, 0, 13, 12], fill=rgb("g")); d.ellipse([4, 2, 9, 7], fill=rgb("l"))
    return outline(im)


def starfield(w, h, n=70, seed=9):
    from PIL import Image
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); o = im.load()
    for k in range(n):
        x = (k * 131 + seed * 37) % w; y = (k * 197 + seed * 53) % h
        o[x, y] = rgb(("w", "e", "c", "m")[k % 4])
        if k % 9 == 0 and 0 < x < w - 1 and 0 < y < h - 1:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): o[x + dx, y + dy] = rgb("m")
    return im


def bleachers(w, h, rows):
    from PIL import ImageDraw, Image
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rh = h / rows
    for r in range(rows):
        y = round(r * rh + rh * 0.78)
        d.rectangle([0, y, w - 1, y + 1], fill=rgb("d")); d.line([0, y, w - 1, y], fill=rgb("m"))
    return im


def pacific(w, h, colors, lon=(40, 400), lat=(75, -50), land="t", sea=None):
    """world map at any longitude window (wraps past 180°, so a Pacific-centred view works). colors = {ISO_A2: palette char}."""
    from PIL import Image, ImageDraw
    src = Path(__file__).resolve().parent.parent / "scripts" / "h9" / "fx" / "data" / "world-chn-50m.topo.json"
    im = Image.new("RGBA", (w, h), rgb(sea) if sea else (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    sx = w / (lon[1] - lon[0]); sy = h / (lat[0] - lat[1])
    for iso, polys in _topo_rings(src):
        col = rgb(colors.get(iso, land))
        for poly in polys:
            if not poly or len(poly[0]) < 3: continue
            for off in (-360, 0, 360):
                d.polygon([((x + off - lon[0]) * sx, (lat[0] - y) * sy) for x, y in poly[0]], fill=col)
    return im


def proj(lonlat, w, h, lon=(40, 400), lat=(75, -50)):
    x, y = lonlat
    while x < lon[0]: x += 360
    while x > lon[1]: x -= 360
    return (x - lon[0]) * w / (lon[1] - lon[0]), (lat[0] - y) * h / (lat[0] - lat[1])


# ------------------------------------------------------------------ chip sound (NES-style square / triangle / noise, synthesised at build time)
SR = 22050
NOTE = lambda n: 440.0 * 2 ** ((n - 69) / 12)       # MIDI note -> Hz


def _arp(notes, dur, v=0.4, duty=0.5, w="sq"): return [(w, NOTE(n), NOTE(n), dur, v, v * 0.6, duty) for n in notes]


CHIP = {
    "coin":   [("sq", 988, 988, .07, .5, .5, .5), ("sq", 1319, 1319, .26, .5, 0, .5)],
    "jump":   [("sq", 260, 820, .16, .45, .1, .25)],
    "bump":   [("tri", 190, 60, .12, .9, 0, .5), ("noise", 3000, 1200, .07, .3, 0, .5)],
    "type":   [("sq", 1175, 1175, .028, .22, .05, .125)],
    "blip":   [("sq", 1568, 1568, .03, .25, .08, .25)],
    "select": [("sq", 660, 660, .05, .4, .4, .25), ("sq", 990, 990, .09, .4, 0, .25)],
    "up":     _arp([72, 76, 79, 84, 88, 91, 96], .045, .38),
    "chest":  [("noise", 9000, 2500, .09, .3, 0, .5)] + _arp([67, 72, 76, 79, 84], .06, .4, .25) + [("sq", NOTE(88), NOTE(88), .2, .35, 0, .25)],
    "boom":   [("noise", 2600, 300, .45, .55, 0, .5)],
    "warp":   [("sq", 1500, 160, .22, .28, .04, .5)],
    "start":  _arp([72, 79], .09, .4) + [("sq", NOTE(84), NOTE(84), .32, .4, 0, .5)],
    "pop":    [("sq", 520, 1500, .06, .4, 0, .5)],
    "tick":   [("noise", 14000, 14000, .025, .3, 0, .5)],
}


def chip_samples(segs):
    """render (wave, f0, f1, dur, v0, v1, duty) segments; 4-bit volume steps like the real chips."""
    out, ph, lfsr, nz = [], 0.0, 1, 1.0
    for w, f0, f1, dur, v0, v1, duty in segs:
        n = int(dur * SR)
        for i in range(n):
            a = i / max(n - 1, 1)
            f = f0 * (f1 / f0) ** a
            ph += f / SR
            if w == "noise":
                while ph >= 1.0:
                    ph -= 1.0
                    bit = (lfsr ^ (lfsr >> 1)) & 1; lfsr = (lfsr >> 1) | (bit << 14); nz = 1.0 if lfsr & 1 else -1.0
                s = nz
            else:
                ph %= 1.0
                s = (1.0 if ph < duty else -1.0) if w == "sq" else 4 * abs(ph - 0.5) - 1
            v = round((v0 + (v1 - v0) * a) * 15) / 15
            out.append(s * v)
    return out


def write_wav(path, samples, sr=SR):
    import struct, wave
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
        f.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 26000)) for s in samples))


def chip(X, t, kind, vol=0.45):
    """a chip sound effect at t (the style's own SFX; the shared realistic library would break the 8-bit world)."""
    if t is None or kind not in CHIP: return
    d = X.out / "assets" / "sfx"; d.mkdir(parents=True, exist_ok=True)
    p = d / f"px_{kind}-{SRCV}.wav"
    if not p.exists(): write_wav(p, chip_samples(CHIP[kind]) + [0.0] * int(SR * 0.03))
    X.audio.append((max(0.0, float(t)), f"assets/sfx/{p.name}", vol))


# ------------------------------------------------------------------ html helpers
UK = 3        # the UI layer (HUD, labels, captions) is drawn at half the world pixel size: a two-tier pixel grid

CSS = r"""
.pxs { position:absolute; inset:0; overflow:hidden; background:var(--bg); }
.pxs img, .pxs .spr { position:absolute; image-rendering:pixelated; display:block; max-width:none; }
.pxs .spr { background-repeat:no-repeat; }
.pxs .lay { position:absolute; left:0; top:0; }
.pxs .pf { position:absolute; font-family:var(--f-pixel); color:var(--fg); white-space:nowrap; line-height:1; }
.pxs .s24 { font-size:24px; text-shadow:3px 3px 0 var(--ink); }
.pxs .s32 { font-size:32px; text-shadow:4px 4px 0 var(--ink); }
.pxs .s48 { font-size:48px; text-shadow:6px 6px 0 var(--ink); }
.pxs .s72 { font-size:72px; text-shadow:6px 6px 0 var(--ink); }
.pxs .vt { position:absolute; font-family:var(--f-body); color:var(--muted); white-space:nowrap; line-height:1; font-size:36px; text-shadow:3px 3px 0 var(--ink); }
.pxs .row { position:absolute; display:flex; align-items:flex-end; white-space:nowrap; }
.pxs .row > * { position:relative !important; left:auto !important; top:auto !important; flex:none; }
.pxs .hud { position:absolute; z-index:20; display:flex; align-items:center; gap:15px; font-family:var(--f-pixel); font-size:24px; color:var(--fg);
  text-shadow:3px 3px 0 var(--ink); white-space:nowrap; line-height:1; }
.pxs .hud > * { position:relative !important; flex:none; }
.pxs .ft { position:absolute; z-index:20; font-family:var(--f-body); font-size:36px; color:var(--muted); white-space:nowrap; text-shadow:3px 3px 0 var(--ink); line-height:1; }
.pxs .box { position:absolute; background:var(--ink); box-shadow:0 0 0 6px var(--fg), 0 0 0 12px var(--ink); }
.pxs .box.blue { background:#29366f; }
.pxs .box > *, .pxs .tag > * { position:relative !important; left:auto !important; top:auto !important; flex:none; }
.pxs .tag { position:absolute; background:var(--ink); box-shadow:0 0 0 3px var(--fg), 0 0 0 6px var(--ink); padding:9px 12px 6px; }
.pxs .bar { position:absolute; background:#333c57; box-shadow:0 0 0 6px var(--fg), 0 0 0 12px var(--ink); overflow:hidden; }
.pxs .bar i { position:absolute; left:0; top:0; bottom:0; width:100%; transform-origin:0 50%; display:block; }
.pxs .bar i::after { content:""; position:absolute; left:0; right:0; top:0; height:6px; background:rgba(255,255,255,.45); }
.pxs .bar b { position:absolute; top:0; bottom:0; width:6px; background:#1a1c2c; opacity:.4; display:block; z-index:2; }
.pxs .dz { position:absolute; inset:0; z-index:40; pointer-events:none; }
.pxs .dz i { position:absolute; background:var(--ink); display:block; }
.pxs .scan { position:absolute; inset:0; z-index:30; pointer-events:none; background:repeating-linear-gradient(0deg, rgba(10,10,20,.12) 0 1px, transparent 1px 3px); }
.pxs .vt.hi { color:var(--fg); }
.clip.pxcap { top:auto; height:auto; left:0; right:0; display:flex; justify-content:center; pointer-events:none; }
.pxcap .in { display:flex; align-items:flex-end; background:var(--ink); padding:12px 21px 15px; box-shadow:0 0 0 6px var(--fg), 0 0 0 12px var(--ink); }
.pxcap img { image-rendering:pixelated; display:block; }
"""


def art(X): return (180, 320) if X.portrait else (320, 180)


def S(v): return f"{round(v)}px"


def img(url, x, y, w, h, cls="", k=P, sty=""):
    """an art-scale PNG at art coordinates (x, y), drawn k screen px per art px."""
    return f'<img class="{cls}" src="{url}" alt="" style="left:{round(x * P)}px;top:{round(y * P)}px;width:{w * k}px;height:{h * k}px;{sty}">'


def sprite(X, name, fn, x, y, cls="", k=P, sty=""):
    url = asset_png(X, name, fn); w, h = png_size(X, url)
    return img(url, x, y, w, h, cls, k, sty), w, h


def spr(url, fw, fh, n, x, y, cls="", k=P, sty=""):
    """sprite-sheet element showing frame 0; animate with run_frames()."""
    return (f'<div class="spr {cls}" style="left:{round(x * P)}px;top:{round(y * P)}px;width:{fw * k}px;height:{fh * k}px;'
            f'background-image:url({url});background-size:{fw * n * k}px {fh * k}px;{sty}"></div>')


def run_frames(X, sel, fw, n, t, d, fps=8, k=P):
    cyc = n / fps; reps = max(0, int(d / cyc))
    X.tw(f'tl.fromTo("{sel}", {{backgroundPositionX:"0px"}}, {{backgroundPositionX:"-{fw * n * k}px", duration:{cyc:.3f}, ease:"steps({n})", repeat:{reps}}}, {t:.3f});')


def btext(X, text, px=16, col="w", edge="k", shadow="b"):
    url = asset_png(X, "t" + hkey(text, px, col, edge, shadow), lambda: bitmap_text(text, px, col=col, edge=edge, shadow=shadow))
    w, h = png_size(X, url)
    return url, w, h


def fitpx(text, max_w, px_max, px_min=12):
    """the biggest drawable size (24 / 12 with the pixel font) whose line fits max_w bitmap px; never below 12 — callers
    wrap instead."""
    sizes = [z for z in SIZES if z <= max(px_max, 12)] if cjk_font() == "fusion-pixel" else range(px_max, px_min - 1, -1)
    for px in sizes:
        if _font(px).getlength(text) + 5 <= max_w: return px
    return 12 if cjk_font() == "fusion-pixel" else px_min


def bimg(X, text, x, y, px=16, col="w", k=P, cls="", anchor="l", edge="k", shadow="b", sty=""):
    """bitmap text at art coords; anchor l / c / r on x. returns (html, screen_w, screen_h)."""
    url, w, h = btext(X, text, px, col, edge, shadow)
    L = x * P - (w * k / 2 if anchor == "c" else w * k if anchor == "r" else 0)
    L = round(L / k) * k
    return f'<img class="{cls}" src="{url}" alt="" style="left:{L}px;top:{round(y * P)}px;width:{w * k}px;height:{h * k}px;{sty}">', w * k, h * k


def wrap(text, max_w, px):
    """break a line at word boundaries (jieba) to max_w bitmap px, evenly (no orphan last line), never truncating;
    punctuation never starts a line."""
    from h9 import core
    f = _font(snap(px))
    def greedy(W):
        toks = []
        for w in core.words(text): toks += list(w) if f.getlength(w) + 5 > W else [w]
        out = [""]
        for w in toks:
            if not out[-1] or f.getlength(out[-1] + w) + 5 <= W or w in "，。、；：！？,.;:!?）》」』": out[-1] += w
            else: out.append(w)
        return out
    lines = greedy(max_w); W = max_w
    while W > 40 and len(greedy(W - 4)) == len(lines): W -= 4
    return greedy(W)


def btitle(X, text, x, y, max_w, px_max=16, px_min=9, k=P, col="w", cls="tt", anchor="l", max_lines=2, gap=2, edge="k", shadow="b"):
    """a title of any length: one line when it fits, else up to max_lines even lines (two big lines beat one tiny one),
    each a bitmap. returns (html, bottom_y art)."""
    W = max_w * P / k
    sizes = [z for z in SIZES if z <= max(px_max, 12)] if cjk_font() == "fusion-pixel" else [fitpx(text, W, px_max, px_min)]
    px, lines = sizes[-1], wrap(text, W, sizes[-1])
    for z in sizes:                        # biggest size whose (wrapped) lines stay within max_lines
        ls = [text] if _font(z).getlength(text) + 5 <= W else wrap(text, W, z)
        if len(ls) <= max_lines: px, lines = z, ls; break
    h, yy = "", y
    for j, ln in enumerate(lines):
        hh, w, hgt = bimg(X, ln, x, yy, px, col, k, f"{cls} {cls}{j}", anchor, edge, shadow)
        h += hh; yy += hgt / P + gap
    return h, yy


def pf(X, text, x, y, size=48, col=None, cls="", anchor="l", width=None, sty=""):
    """Press Start 2P text (sizes 24 / 48 / 72 keep its 8-px grid on whole screen pixels)."""
    X.used_text.update(str(text))
    w = width or len(str(text)) * size
    L = x * P - (w / 2 if anchor == "c" else w if anchor == "r" else 0)
    al = {"l": "left", "c": "center", "r": "right"}[anchor]
    c = f"color:{col};" if col else ""
    return f'<div class="pf s{size} {cls}" style="left:{round(L)}px;top:{round(y * P)}px;width:{round(w)}px;text-align:{al};{c}{sty}">{core_esc(text)}</div>'


def core_esc(s):
    import html
    return html.escape(str(s))


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else float(dflt)


def step_in(X, sel, t, dy=-6, dur=0.24, n=4, st=0.0):
    """stepped entrance: a few whole-pixel jumps, never a smooth slide."""
    X.tw(f'tl.from("{sel}", {{y:{dy * P}, opacity:0, duration:{dur}, ease:"steps({n})", stagger:{st}}}, {t:.3f});')


def pop_in(X, sel, t, st=0.0):
    X.tw(f'tl.from("{sel}", {{scale:0, duration:0.15, ease:"steps(3)", stagger:{st}}}, {t:.3f});')


def toggle(X, sel, t, d, period, a, b, prop="opacity"):
    """flip a property between a and b every period (explicit sets: exact under any seek)."""
    n = max(1, int(d / period))
    for k in range(n): X.tw(f'tl.set("{sel}", {{{prop}:{a if k % 2 == 0 else b}}}, {t + k * period:.3f});')
    if n % 2: X.tw(f'tl.set("{sel}", {{{prop}:{b}}}, {t + n * period:.3f});')


def blink(X, sel, t, d, hz=2.0):
    toggle(X, sel, t, d, 0.5 / hz, 0, 1)


def pan(X, sel, t, d, dx=0, dy=0, x0=0, y0=0):
    """camera / layer move in whole art pixels (steps = distance), constant speed."""
    n = max(1, int(abs(dx) + abs(dy)))
    X.tw(f'tl.fromTo("{sel}", {{x:{x0 * P}, y:{y0 * P}}}, {{x:{(x0 + dx) * P}, y:{(y0 + dy) * P}, duration:{d:.3f}, ease:"steps({n})"}}, {t:.3f});')


def counter(X, sel, t, a, b, dur=1.0, dec=0, steps=14, pad_to=None):
    js = f"o.v.toFixed({dec})" if dec else "Math.round(o.v).toLocaleString('en-US')"
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); if(!el) return; tl.to(o, {{v:{b}, duration:{max(dur, 0.1):.3f}, ease:"steps({steps})", '
         f'onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def ticker(X, sel, t, d, js):
    """text driven by absolute time (T) for any seek: js is an expression of T."""
    X.tw(f'(()=>{{const o={{T:{t:.3f}}}, el=document.querySelector("{sel}"); if(!el) return; tl.to(o, {{T:{t + d:.3f}, duration:{d:.3f}, ease:"none", '
         f'onUpdate:()=>{{const T=o.T; el.textContent={js};}}}}, {t:.3f});}})();')


def slam(X, sel, t, k=1.35):
    X.tw(f'tl.fromTo("{sel}", {{scale:{k}}}, {{scale:1, duration:0.18, ease:"steps(3)", immediateRender:false}}, {t:.3f});')


def flash(X, sel, t, n=3):
    X.tw(f'tl.to("{sel}", {{filter:"brightness(2.2)", duration:0.06, ease:"steps(1)", repeat:{n * 2 - 1}, yoyo:true}}, {t:.3f});')


def bar(X, cid, cls, x, y, w, h, col, ticks=10):
    tk = "".join(f'<b style="left:{round(w * P * j / ticks) - 3}px"></b>' for j in range(1, ticks))
    return f'<div class="bar {cls}" style="left:{x * P}px;top:{y * P}px;width:{w * P}px;height:{h * P}px"><i style="background:{PAL.get(col, col)}"></i>{tk}</div>'


def fill(X, sel, t, dur, frac, n=12):
    X.tw(f'tl.fromTo("{sel} i", {{scaleX:0}}, {{scaleX:{frac:.4f}, duration:{max(dur, 0.1):.3f}, ease:"steps({n})"}}, {t:.3f});')


# ------------------------------------------------------------------ seams: the tile dissolve (three patterns, alternating)
SEAMS = (("start", None), ("center", None), ("end", "y"))


def _tiles(X, cls, s=20):
    AW, AH = art(X); cols, rows = -(-AW // s), -(-AH // s)
    h = "".join(f'<i style="left:{c * s * P}px;top:{r * s * P}px;width:{s * P}px;height:{s * P}px"></i>' for r in range(rows) for c in range(cols))
    return f'<div class="dz {cls}">{h}</div>', rows, cols


def _span(rows, cols, frm, axis):
    if axis == "y": return rows - 1
    if frm == "center": return math.hypot((rows - 1) / 2, (cols - 1) / 2)
    return math.hypot(rows - 1, cols - 1)


def seam_in(X, cid, t, i):
    h, rows, cols = _tiles(X, "dzi")
    frm, axis = SEAMS[i % len(SEAMS)]
    ax = f', axis:"{axis}"' if axis else ""
    X.tw(f'tl.fromTo("#{cid} .dzi i", {{scale:1}}, {{scale:0, duration:0.1, ease:"steps(2)", stagger:{{amount:0.14, grid:[{rows},{cols}], from:"{frm}"{ax}}}}}, {t:.3f});')
    return h


def seam_out(X, cid, t_end, i):
    h, rows, cols = _tiles(X, "dzo")
    frm, axis = SEAMS[i % len(SEAMS)]
    ax = f', axis:"{axis}"' if axis else ""
    X.tw(f'tl.fromTo("#{cid} .dzo i", {{scale:0}}, {{scale:1, duration:0.08, ease:"steps(2)", stagger:{{amount:0.12, grid:[{rows},{cols}], from:"{frm}"{ax}}}}}, {t_end - 0.2:.3f});')
    chip(X, t_end - 0.2, "warp", 0.22)
    X.tw(f'tl.set("#{cid} > .stage > .pxs", {{opacity:0}}, {t_end:.3f});')      # covered: the next page (on top) takes over
    return h


# ------------------------------------------------------------------ page furniture: HUD, footer, pixel captions
def hud(X, b, t, d, cid):
    """lives + channel, world number, coin count, countdown timer — persistent on every page."""
    i = X.beat["i"]
    hu = asset_png(X, "heart", heart); cu, cw, ch = sheet(X, "coin", coin, 4)
    world = b.get("world", f"1-{i + 1}")
    hearts = "".join(f'<img src="{hu}" alt="" style="width:{9 * UK}px;height:{8 * UK}px">' for _ in range(3))
    coins = getattr(X, "_px_coins", 0)
    D = X.duration or (t + d)
    top = 36 if X.portrait else 6
    X.used_text.update(f"HAT9 WORLD {world} TIME 0123456789×")
    h = f'<div class="hud" style="left:{8 * P}px;top:{top * P}px">{hearts}<span style="margin-left:6px">HAT9</span></div>'
    if X.portrait:
        h += f'<div class="hud" style="left:{8 * P}px;top:{(top + 8) * P}px;color:{PAL["c"]}">WORLD {core_esc(world)}</div>'
    else:
        h += f'<div class="hud" style="left:0;right:0;top:{top * P}px;justify-content:center;color:{PAL["c"]}">WORLD {core_esc(world)}</div>'
    h += (f'<div class="hud" style="right:{8 * P}px;top:{top * P}px"><span class="spr coinic" style="width:{cw * UK}px;height:{ch * UK}px;'
          f'background-image:url({cu});background-size:{cw * UK * 4}px {ch * UK}px;display:block"></span><span class="cn">×{coins:02d}</span>'
          f'<span style="margin-left:18px;color:{PAL["e"]}">TIME</span><span class="tm">{max(0, math.ceil(D - t)):03d}</span></div>')
    run_frames(X, f"#{cid} .coinic", cw, 4, t, d, fps=8, k=UK)
    ticker(X, f"#{cid} .tm", t, d, f"String(Math.max(0, Math.ceil({D:.3f} - T))).padStart(3, '0')")
    got = [round(x, 3) for x in getattr(X, "_px_got", []) if t <= x < t + d]
    if got:
        ticker(X, f"#{cid} .cn", t, d, f"'×' + String({coins} + {json.dumps(got)}.filter(x => x <= T).length).padStart(2, '0')")
    X._px_coins = coins + len(got)
    src = b.get("src")
    if src:
        X.used_text.update(src)
        txt = f"SOURCE · {src}"
        AW = art(X)[0]
        W = (AW - 16) * P / 3                           # the footer is 36 px pixel type (12-px font, 3×)
        lines = [txt] if _font(12).getlength(txt) <= W else wrap(txt, W, 12)
        y = (249 if X.portrait else 172) - 6 * (len(lines) - 1)
        h += f'<div class="ft" style="left:{8 * P}px;top:{y * P}px">{"<br>".join(core_esc(x) for x in lines)}</div>'
    return h


NUMS = set("零一二三四五六七八九十百千万亿两点")


def pages(ws, mx, pun):
    """caption pages: one per spoken phrase (split at punctuation and pauses); a phrase longer than mx glyphs is cut
    into the fewest, most even pieces at word boundaries (差不多每两个 | 中国人里就有一个, never 中国 | 人)."""
    import itertools
    phrases, cur = [], []
    for w in ws:
        tok = str(w["w"]).strip()
        if not tok: continue
        if all(c in pun for c in tok):
            if cur: phrases.append(cur); cur = []
            continue
        if cur and w["s"] - cur[-1]["e"] > 0.45: phrases.append(cur); cur = []
        cur.append(dict(w, w=tok))
    if cur: phrases.append(cur)
    out = []
    for ph in phrases:
        L = [len(w["w"]) for w in ph]; n = sum(L); m = max(mx, max(L))     # a single word longer than mx keeps a page to itself
        best = [len(ph)]
        for k in range(-(-n // m), len(ph) + 1):
            cands = []
            for cut in itertools.combinations(range(1, len(ph)), k - 1):
                b = (0,) + cut + (len(ph),)
                seg = [sum(L[b[i]:b[i + 1]]) for i in range(k)]
                lone = sum(ph[i]["w"][0] in "了的着过吧呢啊" for i in cut)     # never start a page on a particle
                if max(seg) <= m: cands.append((lone, max(seg) - min(seg), list(b[1:])))
            if cands: best = min(cands)[2]; break
        a = 0
        for z in best:
            grp = ph[a:z]; a = z
            out.append([grp[0]["s"], grp[-1]["e"], "".join(w["w"] for w in grp)])
    return out


def captions(X):
    """the style's own captions: bitmap glyphs in a dialogue box (the default caption font would break the pixel grid)."""
    if getattr(X, "_px_cap", False) or not X.chars: return
    X._px_cap = True
    from h9 import captions as C
    meta = X.v.get("meta", {})
    fr = 1 / X.fps
    mx = int(meta.get("caption_len") or (8 if X.portrait else 12))
    ws = []
    for w in C.regroup(X._words):        # 六亿 + 七千 + 四百万 → one token, so a page never breaks inside a spoken number
        tok = str(w["w"]).strip()
        if ws and tok and tok[0] in NUMS and str(ws[-1]["w"]).strip()[-1:] in NUMS: ws[-1] = dict(ws[-1], w=ws[-1]["w"] + tok, e=w["e"])
        else: ws.append(dict(w))
    pg = pages(ws, mx, C.PUN)
    for p in pg:
        for a, z in (meta.get("caption_fix") or {}).items(): p[2] = p[2].replace(a, z)
    for i, p in enumerate(pg):
        p[0] = max(0, p[0] - 2 * fr); p[1] = p[1] + 5 * fr
        if i + 1 < len(pg):
            nxt = pg[i + 1][0] - 2 * fr
            p[1] = nxt if nxt - p[1] < 0.3 else min(p[1], nxt)
        p[1] = max(p[1], p[0] + 0.8)
        if i + 1 < len(pg): p[1] = min(p[1], pg[i + 1][0] - 2 * fr)
    beats = X.v.get("beats", []); off = []          # beats with "cap": false show the words themselves (dialogue box, title)
    for k, b in enumerate(beats):
        if b.get("cap") is False:
            a = X.T(b.get("t", 0)); z = X.T(beats[k + 1]["t"]) if k + 1 < len(beats) else X.duration + 99
            off.append((a, z))
    hl = meta.get("caption_hl") or []
    cpx = 24                     # pixel font at 24 px, 3 screen px per art px: 72-px glyphs
    for i, (a, z, txt) in enumerate(pg):
        mid = (a + z) / 2
        if any(o0 - 0.05 <= mid < o1 for o0, o1 in off): continue
        runs = [(txt, "w")]
        mark = next((m for m in hl if m in txt), None)
        if mark:
            j = txt.index(mark); runs = [r for r in ((txt[:j], "w"), (mark, "y"), (txt[j + len(mark):], "w")) if r[0]]
        body = ""
        for s, col in runs:
            url, w, h = btext(X, s, cpx, col, "k", "b")
            body += f'<img src="{url}" alt="" style="width:{w * UK}px;height:{h * UK}px">'
        cid = f"pxc{i}"
        bot = 520 if X.portrait else 66
        X.clip(cid, a, z - a, f'<div class="in">{body}</div>', "pxcap", 35, track=9, sty=f"bottom:{bot}px")
        X.tw(f'tl.from("#{cid} .in", {{scale:0.7, duration:0.08, ease:"steps(2)"}}, {a:.3f});')


def lead(X, k=None):
    """pre-roll of page k (default: this page): it starts this much before its beat — beat "lead", else meta.seam_lead,
    default 0.3 s — so the seam plays in the breath before the line and the page is up on its first spoken word.
    Use a short lead (≈0.1) on a page cut in mid-sentence, where there is no breath to hide the seam in."""
    meta = X.v.get("meta", {})
    k = X.beat["i"] - int(meta.get("beat_offset", 0)) if k is None else k
    beats = X.v.get("beats", [])
    if k <= 0 or k >= len(beats): return 0.0
    return float(beats[k].get("lead", meta.get("seam_lead", 0.3)))


def t_in(X, t):
    """when a page's standing content (titles, boxes, labels) enters: inside the pre-roll, landed by the first word."""
    return t - lead(X) * 0.75 if X.beat["i"] > 0 else t


def page(X, b, t, d, cid, body):
    """wrap a scene: background + content, HUD, seams in / out (in the pre-roll), optional CRT scanlines."""
    X.css("pixel", CSS)
    captions(X)
    i, n = X.beat["i"], X.beat["n"]
    k = i - int(X.v.get("meta", {}).get("beat_offset", 0))
    beats = X.v.get("beats", [])
    cut_in = b.get("seam") == "cut"                                              # "seam": "cut" = a hard cut on the word
    cut_out = k + 1 < len(beats) and beats[k + 1].get("seam") == "cut"          # (for a page split in mid-sentence)
    t0 = t - lead(X)
    dz = (seam_in(X, cid, t0, i) if i > 0 and not cut_in else "") + (seam_out(X, cid, t + d - lead(X, k + 1), i + 1) if i < n - 1 and not cut_out else "")
    scan = '<div class="scan"></div>' if X.v.get("meta", {}).get("crt", False) else ""
    X.clip(cid, t0, t + d - t0, f'<div class="pxs">{body}{hud(X, b, t, d, cid)}{scan}{dz}</div>', "scene", 2, track=1 + i % 2)


def got_coin(X, tc):
    X._px_got = getattr(X, "_px_got", []) + [tc]


# ------------------------------------------------------------------ scenes
def stage(b, X, t, d, cid):
    """横版关卡开场：视差山脉 + 奔跑角色吃金币 + 顶问号砖时销量计数落定。
    keys: pre（数字上方一行字）· value（终值）· unit（单位，位图字）· at_hit（顶砖那一刻，默认 2/3 处）。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    gy = 204 if V else 150
    LW = AW * 3; spd = 64.0
    T1 = T(X, b, "at_hit", t, t + d * 0.62)
    h = sprite(X, f"sky{AW}x{AH}", lambda: sky(AW, AH, ("b", "u", "s", "c")), 0, 0)[0]

    def layer(cls, name, fn, y, v, inner=""):
        url = asset_png(X, name, fn); w, hh = png_size(X, url)
        pan(X, f"{s} .{cls}", t, d, dx=-round(v * d))
        return f'<div class="lay {cls}" style="top:{y * P}px;width:{w * P}px">{img(url, 0, 0, w, hh)}{inner}</div>'

    h += layer("lc", f"clouds{LW}", lambda: clouds(LW, 50, n=10), 62 if V else 14, 5)
    h += layer("lf", f"far{LW}", lambda: ridge(LW, 84, "m", seed=2, amp=.55, base=.55, cap="e"), gy - 84 + 8, 12)
    h += layer("lm", f"mid{LW}", lambda: ridge(LW, 46, "t", seed=5, amp=.35, base=.5, rough=.6), gy - 42, 28)
    mu, mw, mh = sheet(X, "monkey", monkey, 4)
    mx = 30 if V else 44
    my = gy - mh + 1
    # ground layer carries coins and the ? block (they scroll with it)
    inner = ""
    cu, cw, ch = sheet(X, "coin", coin, 4)
    tcs = [t + 0.42 + 0.28 * k for k in range(12) if t + 0.42 + 0.28 * k < T1 - 0.3]
    for k, tc in enumerate(tcs):
        cx = mx + 18 + spd * (tc - t)
        inner += spr(cu, cw, ch, 4, cx - cw / 2, -16 - (k % 2) * 4, f"gc gc{k}")
        X.tw(f'tl.to("{s} .gc{k}", {{y:{-8 * P}, opacity:0, duration:0.18, ease:"steps(3)"}}, {tc:.3f});')
        chip(X, tc, "coin", 0.22); got_coin(X, tc)
    run_frames(X, f"{s} .gc", cw, 4, t, d, fps=8)
    jump = 24
    bx = mx + 16 + spd * (T1 - t) - 9
    btop = -(mh + jump + 18) + 3
    qu = asset_png(X, "qblock", lambda: block("q")); eu = asset_png(X, "eblock", lambda: block("e"))
    inner += img(qu, bx, btop, 18, 18, "qb") + img(eu, bx, btop, 18, 18, "eb", sty="opacity:0")
    inner += spr(cu, cw, ch, 4, bx + 4, btop - 2, "bc", sty="opacity:0")
    h += layer("lg", f"ground{LW}x{AH - gy}", lambda: (soil if V else ground)(LW, AH - gy), gy, spd, inner)
    h += spr(mu, mw, mh, 4, mx, my, "mk")
    run_frames(X, f"{s} .mk", mw, 4, t, d, fps=10)
    X.tw(f'tl.to("{s} .mk", {{y:{-jump * P}, duration:0.2, ease:"steps(5)"}}, {T1 - 0.2:.3f});')
    X.tw(f'tl.to("{s} .mk", {{y:0, duration:0.26, ease:"steps(6)"}}, {T1 + 0.04:.3f});')
    X.tw(f'tl.to("{s} .qb, {s} .eb", {{y:{-4 * P}, duration:0.06, ease:"steps(1)", yoyo:true, repeat:1}}, {T1:.3f});')
    X.tw(f'tl.set("{s} .qb", {{opacity:0}}, {T1 + 0.06:.3f}); tl.set("{s} .eb", {{opacity:1}}, {T1 + 0.06:.3f});')
    X.tw(f'tl.fromTo("{s} .bc", {{opacity:1, y:0}}, {{y:{-22 * P}, duration:0.3, ease:"steps(6)", immediateRender:false}}, {T1:.3f}); tl.set("{s} .bc", {{opacity:0}}, {T1 + 0.36:.3f});')
    run_frames(X, f"{s} .bc", cw, 4, T1, 0.4, fps=16)
    chip(X, T1 - 0.2, "jump", 0.3); chip(X, T1, "bump", 0.5); chip(X, T1 + 0.02, "coin", 0.35); got_coin(X, T1)
    # title + counter
    pre = b.get("pre", ""); unit = b.get("unit", ""); val = float(b.get("value", 0))
    final = f"{val:,.0f}" if val == int(val) else f"{val:,.2f}"
    ty = 54 if V else 24
    if pre:
        th, ty2 = btitle(X, pre, AW / 2, ty, AW - 24, px_max=16, anchor="c", cls="pre")
        h += th; step_in(X, f"{s} .pre", t + 0.06)
    else: ty2 = ty
    uh, uw, uhh = bimg(X, unit, 0, 0, 24, "y", UK, "un") if unit else ("", 0, 0)
    big = (72, 48) if V or ty2 - ty < 26 else (48,)        # a two-line title on 16:9 leaves room for a 48-px counter only
    size = next((z for z in big + (32, 24) if len(final) * z + uw + 12 <= (AW - 16) * P), 24)
    tot = len(final) * size + (12 + uw if unit else 0)
    row = (f'<div class="row cr" style="left:{round(((AW * P - tot) / 2) / P) * P}px;top:{round((ty2 + 2) * P)}px;gap:12px">'
           f'<div class="pf s{size} num" style="width:{len(final) * size}px;text-align:right;color:{PAL["y"]}">0</div>{uh}</div>')
    X.used_text.update(final)
    h += row
    step_in(X, f"{s} .cr", t + 0.14)
    counter(X, f"{s} .num", t + 0.3, 0, val, T1 - t - 0.3, dec=0 if val == int(val) else 2, steps=16)
    slam(X, f"{s} .cr", T1); flash(X, f"{s} .num", T1 + 0.02, 2)
    if b.get("badge"):                      # e.g. HI-SCORE! on 「再创新高」
        tB = T(X, b, "at_badge", t, min(t + d - 0.6, T1 + 0.8))
        bs = 48 if len(b["badge"]) * 48 <= (AW - 16) * P else 32
        h += pf(X, b["badge"], AW / 2, ty2 + 2 + size / P + 5, bs, PAL["y"], "bd", anchor="c", sty="opacity:0")
        X.tw(f'tl.set("{s} .bd", {{opacity:1}}, {tB:.3f});'); slam(X, f"{s} .bd", tB, 2.0)
        toggle(X, f"{s} .bd", tB + 0.2, min(0.8, t + d - tB - 0.3), 0.1, f'"{PAL["w"]}"', f'"{PAL["y"]}"', "color")
        chip(X, tB, "up", 0.32)
    page(X, b, t, d, cid, h)


def online(b, X, t, d, cid):
    """在线人数：日期打字 + 标题 + 血条式仪表 + 像素人潮按比例坐满看台。
    keys: date · title · label · value · at_title · at_peak · unit_label（图例模板，{n} = 每个小人代表的人数）。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    ti = t_in(X, t)
    tT = T(X, b, "at_title", t, ti); tV = T(X, b, "at_peak", t, t + d * 0.8)
    val = float(b.get("value", 3000000)); dec = int(b.get("dec", 0)); unit = b.get("unit", "")
    h = sprite(X, f"night{AW}x{AH}", lambda: sky(AW, AH, ("k", "k", "b", "d")), 0, 0)[0]
    lx = 12 if V else 14
    ys = dict(date=50, title=58, label=82, bar=94, num=106, leg=120) if V else dict(date=26, title=36, label=70, bar=84, num=98, leg=114)
    h += pf(X, b.get("date", ""), lx, ys["date"], 32, PAL["c"], "dt")
    th, tb = btitle(X, b.get("title", ""), lx, ys["title"], (AW - 2 * lx) if V else 140, px_max=16, cls="ti", max_lines=2)
    h += th
    sh_ = max(0, round(tb + 1 - ys["label"]))           # a two-line title pushes the meter (and, on 9:16, the stand) down
    for k_ in ("label", "bar", "num", "leg"): ys[k_] += sh_
    cols, rows = (15, 8) if V else (20, 12)
    sx_, sy_ = (10, 10) if V else (7, 9)
    gx, gy = ((AW - cols * sx_) // 2 + 2, 130 + sh_) if V else (166, 38)
    h += sprite(X, f"bleach{cols}x{rows}", lambda: bleachers(cols * sx_ + 6, rows * sy_, rows), gx - 3, gy)[0]
    ppl = ""
    for r in range(rows):
        for c in range(cols):
            v = (r * 7 + c * 3 + (r * c) % 5) % 6
            u = asset_png(X, f"p{v}", lambda v=v: outline(person(v)))
            ppl += img(u, gx + c * sx_, gy + r * sy_ + 1, 7, 10, "pp")
    h += f'<div class="lay crowd">{ppl}</div>'
    bw = AW - 2 * lx if V else 140
    lh, lw, _ = bimg(X, b.get("label", ""), lx, ys["label"], 16, "e", UK, "lb")
    h += lh + bar(X, cid, "hp", lx, ys["bar"], bw, 7, "l")
    final = f"{val:,.{dec}f}" if not dec else f"{val:.{dec}f}"
    X.used_text.update(final)
    uh, uw, _ = bimg(X, unit, 0, 0, 12, "y", UK, "un") if unit else ("", 0, 0)
    h += (f'<div class="row nm" style="left:{lx * P}px;top:{ys["num"] * P}px;gap:12px"><div class="pf s48 num" style="width:{len(final) * 48}px;'
          f'text-align:right;color:{PAL["y"]}">0</div>{uh}</div>')
    tag = b.get("peak_tag", "MAX")
    if tag: h += pf(X, tag, lx + bw, ys["num"] + 1, 32, PAL["r"] if tag == "MAX" else PAL["l"], "mx", anchor="r", sty="opacity:0")
    per = float(b.get("count", val)) / (cols * rows)
    leg = b.get("unit_label", "每个小人 ≈ {n}人").replace("{n}", f"{per:,.0f} " if per < 1e5 else f"{per / 1e4:,.0f} 万")
    X.used_text.update(leg)
    h += f'<div class="vt hi lg" style="left:{lx * P}px;top:{ys["leg"] * P}px">{core_esc(leg)}</div>'
    n_ = len(final)
    if b.get("date"):
        X.tw(f'tl.fromTo("{s} .dt", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.3, ease:"steps({max(len(b.get("date", "")), 1)})"}}, {ti:.3f});')
        for k in range(4): chip(X, ti + 0.02 + k * 0.07, "type", 0.18)
    step_in(X, f"{s} .ti", tT); chip(X, tT, "select", 0.3)
    step_in(X, f"{s} .lb, {s} .hp, {s} .nm, {s} .lg", ti + 0.06, dy=4, st=0.03)
    a0 = max(t, ti + 0.25)
    frac = min(1.0, float(b.get("fill", 1.0)))
    fill(X, f"{s} .hp", a0, tV - a0, frac, n=12)
    counter(X, f"{s} .num", a0, 0, val, tV - a0, dec=dec, steps=12)
    X.tw(f'tl.from("{s} .pp", {{y:{3 * P}, opacity:0, duration:0.08, ease:"steps(2)", stagger:{{amount:{max(tV - a0 - 0.1, 0.2):.3f}, grid:[{rows},{cols}], from:"end", axis:"y"}}}}, {a0:.3f});')
    for k in range(6): chip(X, a0 + (tV - a0) * k / 6, "tick", 0.18)
    if tag: X.tw(f'tl.set("{s} .mx", {{opacity:1}}, {tV:.3f});'); slam(X, f"{s} .mx", tV, 1.8)
    flash(X, f"{s} .num", tV, 3)
    X.tw(f'tl.to("{s} .pp", {{y:{-2 * P}, duration:0.07, ease:"steps(1)", yoyo:true, repeat:3, stagger:{{each:0.012, grid:[{rows},{cols}], from:"start", axis:"x"}}}}, {tV:.3f});')
    chip(X, tV, "up", 0.32)
    page(X, b, t, d, cid, h)


def treasure(b, X, t, d, cid):
    """宝箱：地牢墙、火把、宝箱抖动后打开，金币喷出，金额计数 + 同比标签。
    keys: banner · label · value · dec · unit · tag · at_open · at_end。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    tO = T(X, b, "at_open", t, t + d * 0.3); tE = T(X, b, "at_end", t, t + d * 0.75)
    fy = 204 if V else 138
    h = sprite(X, f"bricks{AW}x{AH}", lambda: bricks(AW, AH), 0, 0)[0]
    h += sprite(X, f"floor{AW}", lambda: ground(AW, AH - fy, top="e", grass="m", dirt="d", speck="k"), 0, fy)[0]
    cxs = (18, 150) if V else (22, 118)
    tyy = 150 if V else 62
    fu, fw, fh = sheet(X, "flame", flame, 2)
    for k, x in enumerate(cxs):
        h += sprite(X, "torch", torch, x, tyy, "tc")[0] + spr(fu, fw, fh, 2, x - 1, tyy - fh + 1, f"fl fl{k}")
        run_frames(X, f"{s} .fl{k}", fw, 2, t + k * 0.07, d, fps=7)
    chx, chy = ((AW - 36) // 2, fy - 28) if V else (52, fy - 28)
    ru = asset_png(X, "rays", lambda: rays(90, 64)); rw, rh = png_size(X, ru)
    h += img(ru, chx + 18 - rw / 2, chy + 12 - rh, rw, rh, "ry", sty="opacity:0")
    cu_ = asset_png(X, "chestc", lambda: chest2(False)); co = asset_png(X, "chesto", lambda: chest2(True))
    h += img(cu_, chx, chy, 36, 29, "ch0") + img(co, chx, chy, 36, 29, "ch1", sty="opacity:0")
    cu, cw, ch = sheet(X, "coin", coin, 4)
    burst = ""
    for k in range(16):
        burst += spr(cu, cw, ch, 4, chx + 13, chy + 6, f"bz bz{k}", sty="opacity:0")
    h += burst
    # shake, open, burst
    for k in range(int((tO - t) / 0.12)):
        tk = t + k * 0.12
        X.tw(f'tl.set("{s} .ch0", {{x:{(1 if k % 2 else -1) * P}}}, {tk:.3f});')
    X.tw(f'tl.set("{s} .ch0", {{x:0, opacity:0}}, {tO:.3f}); tl.set("{s} .ch1", {{opacity:1}}, {tO:.3f});')
    X.tw(f'tl.fromTo("{s} .ry", {{opacity:0, scale:0.4, transformOrigin:"50% 100%"}}, {{opacity:0.85, scale:1, duration:0.2, ease:"steps(4)"}}, {tO:.3f});')
    toggle(X, f"{s} .ry", tO + 0.2, t + d - tO - 0.2, 0.12, 0.55, 0.85)
    for k in range(16):
        a = math.pi * (0.15 + 0.7 * ((k * 7) % 16) / 15)
        r = 34 + (k * 13) % 26
        dx, dy = -math.cos(a) * r * (1.25 if not V else 0.9), -math.sin(a) * r
        t0 = tO + 0.02 * (k % 5)
        X.tw(f'tl.set("{s} .bz{k}", {{opacity:1}}, {t0:.3f}); tl.to("{s} .bz{k}", {{x:{round(dx) * P}, y:{round(dy) * P}, duration:0.32, ease:"steps(6)"}}, {t0:.3f});'
             f'tl.to("{s} .bz{k}", {{y:{round(dy + 26) * P}, opacity:0, duration:0.4, ease:"steps(6)"}}, {t0 + 0.34:.3f});')
    run_frames(X, f"{s} .bz", cw, 4, tO, d - (tO - t), fps=12)
    chip(X, tO, "chest", 0.45); chip(X, tO + 0.12, "boom", 0.18)
    for k in range(3): chip(X, tO + 0.36 + k * 0.1, "coin", 0.16); got_coin(X, tO + 0.36 + k * 0.1)
    # info
    val = float(b.get("value", 0)); dec = int(b.get("dec", 2 if val != int(val) else 0))
    final = f"{val:.{dec}f}"
    if V: ix, anc, yb, yl, yn, yt = AW / 2, "c", 56, 68, 82, 100
    else: ix, anc, yb, yl, yn, yt = 150, "l", 30, 44, 58, 80
    h += pf(X, b.get("banner", "ITEM GET!"), ix, yb, 32, PAL["c"], "bn", anchor=anc, sty="opacity:0")
    lh, lb_ = btitle(X, b.get("label", ""), ix, yl, (AW - 16) if V else AW - ix - 8, px_max=16, k=UK, anchor=anc, cls="lb", max_lines=2, gap=1)
    h += lh
    if lb_ + 1 > yn: yt += round(lb_ + 1 - yn); yn = round(lb_ + 1)
    uh, uw, _ = bimg(X, b.get("unit", ""), 0, 0, 12, "y", UK, "un") if b.get("unit") else ("", 0, 0)
    size = 48 if len(final) * 48 + uw + 12 <= ((AW - 12) if V else AW - ix - 6) * P else 24
    tot = len(final) * size + uw + 12
    L = (AW * P - tot) / 2 if V else ix * P
    X.used_text.update(final)
    h += (f'<div class="row cr" style="left:{round(L / P) * P}px;top:{yn * P}px;gap:12px"><div class="pf s{size} num" '
          f'style="width:{len(final) * size}px;text-align:right;color:{PAL["y"]}">0</div>{uh}</div>')
    tag = b.get("tag", "")
    if tag:
        X.used_text.update(tag)
        tw_ = len(tag) * 32 + 24
        L2 = (AW * P - tw_) / 2 if V else ix * P
        h += f'<div class="tag tg" style="left:{round(L2)}px;top:{yt * P}px"><span class="pf s32" style="position:relative;color:{PAL["l"]}">{core_esc(tag)}</span></div>'
    ti = t_in(X, t)
    step_in(X, f"{s} .lb", ti)
    X.tw(f'tl.set("{s} .bn", {{opacity:1}}, {tO:.3f}); tl.from("{s} .bn", {{scale:2, duration:0.15, ease:"steps(3)"}}, {tO:.3f});')
    pile = [(chx - 22, 0), (chx + 40, 0), (chx - 40, 0), (chx + 58, 0)] if V else [(chx + 44 + 22 * k, 0) for k in range(int((AW - chx - 64) / 22) + 1)]
    su_ = asset_png(X, "stack", coin_stack)
    for k, (x, _) in enumerate(pile):
        h += img(su_, x, fy - 15, 20, 16, f"pl pl{k}")
    X.tw(f'tl.from("{s} .pl", {{y:{8 * P}, opacity:0, duration:0.12, ease:"steps(2)", stagger:{max(0.05, (tE - tO) / max(len(pile), 1)):.3f}}}, {tO + 0.2:.3f});')
    step_in(X, f"{s} .cr", ti + 0.06, dy=4)
    counter(X, f"{s} .num", tO, 0, val, tE - tO, dec=dec, steps=14)
    flash(X, f"{s} .num", tE, 2)
    if tag: pop_in(X, f"{s} .tg", tE + 0.05); chip(X, tE + 0.05, "select", 0.3)
    page(X, b, t, d, cid, h)


def crowd(b, X, t, d, cid):
    """每两个人里有一个：灰色小人方阵，按「隔一个点亮一个」亮起 + 感叹号 + 比例。
    keys: label · value · dec · unit · ratio（大字）· note（小字算式）· at_n · at_lit · at_hop。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    tN = T(X, b, "at_n", t, t + 0.1); tL = T(X, b, "at_lit", t, t + d * 0.45); tH = T(X, b, "at_hop", t, t + d * 0.8)
    fy = 214 if V else 152
    h = sprite(X, f"dusk{AW}x{AH}", lambda: sky(AW, AH, ("k", "b", "p", "r")), 0, 0)[0]
    h += sprite(X, f"street{AW}", lambda: ground(AW, AH - fy, top="m", grass="d", dirt="k", speck="d"), 0, fy)[0]
    cols, rows = (6, 4) if V else (12, 3)
    sx_, sy_ = (26, 22) if V else (24, 22)
    gw = (cols - 1) * sx_ + 11
    gx, gy = (AW - gw) // 2, (fy - (rows - 1) * sy_ - 16 - (14 if V else 6))
    bu = asset_png(X, "bang", bang)
    try: num, den = (int(v) for v in str(b.get("lit", b.get("ratio", "1/2"))).strip("~≈ ").split("/"))
    except ValueError: num, den = 1, 2
    ppl = ""
    for r in range(rows):
        for c in range(cols):
            v = (r * 5 + c * 3) % 8
            x, y = gx + c * sx_, gy + r * sy_
            gu = asset_png(X, "gp", lambda: person2(0, True)); lu = asset_png(X, f"lp{v}", lambda v=v: person2(v))
            lit = (r + c) % den < num
            ppl += f'<div class="lay pc {"lit" if lit else "dim"}" style="left:{x * P}px;top:{y * P}px">{img(gu, 0, 0, 11, 16, "g")}'
            if lit: ppl += img(lu, 0, 0, 11, 16, "c", sty="opacity:0") + img(bu, 4, -12, 5, 11, "bg", sty="opacity:0")
            ppl += "</div>"
    h += ppl
    val = float(b.get("value", 0)); dec = int(b.get("dec", 2 if val != int(val) else 0)); final = f"{val:.{dec}f}"
    uh, uw, _ = bimg(X, b.get("unit", ""), 0, 0, 12, "y", UK, "un") if b.get("unit") else ("", 0, 0)
    if V: lx, anc, yl, yn, yr, yno = AW / 2, "c", 56, 68, 88, 102
    else: lx, anc, yl, yn, yr, yno = 14, "l", 26, 38, 32, 50
    lh, _ = btitle(X, b.get("label", ""), lx, yl, AW - 20 if V else 150, px_max=16, k=UK, anchor=anc, cls="lb", max_lines=1)
    h += lh
    tot = len(final) * 48 + 12 + uw
    L = (AW * P - tot) / 2 if V else lx * P
    X.used_text.update(final)
    h += (f'<div class="row cr" style="left:{round(L / P) * P}px;top:{yn * P}px;gap:12px"><div class="pf s48 num" '
          f'style="width:{len(final) * 48}px;text-align:right;color:{PAL["y"]}">0</div>{uh}</div>')
    ratio = b.get("ratio", ""); note = b.get("note", "")
    if ratio: h += pf(X, ratio, AW / 2 if V else AW - 14, yr, 48, PAL["c"], "rt", anchor="c" if V else "r", sty="opacity:0")
    if note:
        X.used_text.update(note)
        sty = f"left:0;right:0;text-align:center" if V else f"right:{14 * P}px"
        h += f'<div class="vt hi no" style="{sty};top:{yno * P}px">{core_esc(note)}</div>'
    ti = t_in(X, t)
    step_in(X, f"{s} .lb", ti); step_in(X, f"{s} .cr", ti + 0.05, dy=4)
    counter(X, f"{s} .num", tN, 0, val, max(0.5, min(1.2, tL - tN - 0.2)), dec=dec, steps=12)
    X.tw(f'tl.from("{s} .pc", {{x:{-6 * P}, opacity:0, duration:0.16, ease:"steps(3)", stagger:{{amount:{min(0.7, max(0.2, (tL - ti) * 0.6)):.2f}, grid:[{rows},{cols}], from:"start", axis:"x"}}}}, {ti + 0.04:.3f});')
    X.tw(f'tl.to("{s} .pc.lit .c", {{opacity:1, duration:0.05, ease:"steps(1)", stagger:{{amount:0.5, from:"start"}}}}, {tL:.3f});')
    X.tw(f'tl.to("{s} .pc.lit .bg", {{opacity:1, duration:0.05, ease:"steps(1)", stagger:{{amount:0.5, from:"start"}}}}, {tL + 0.04:.3f});')
    X.tw(f'tl.to("{s} .pc.lit .bg", {{opacity:0, duration:0.05, ease:"steps(1)", stagger:{{amount:0.5, from:"start"}}}}, {tL + 0.9:.3f});')
    X.tw(f'tl.to("{s} .pc.dim", {{opacity:0.55, duration:0.1, ease:"steps(1)"}}, {tL + 0.5:.3f});')
    for k in range(4): chip(X, tL + k * 0.13, "blip", 0.22)
    if ratio: X.tw(f'tl.set("{s} .rt", {{opacity:1}}, {tL:.3f});'); slam(X, f"{s} .rt", tL, 1.6); chip(X, tL, "select", 0.3)
    if note: step_in(X, f"{s} .no", max(ti + 0.1, tL - 0.3), dy=2)
    X.tw(f'tl.to("{s} .pc.lit", {{y:{-4 * P}, duration:0.1, ease:"steps(2)", yoyo:true, repeat:1, stagger:{{each:0.04, from:"start"}}}}, {tH:.3f});')
    chip(X, tH, "jump", 0.2)
    page(X, b, t, d, cid, h)


TARGETS = [{"iso": "US", "name": "美国", "v": "31.06%", "ll": [-98, 39], "lab": [6, -14], "lab_v": [-6, -20]},
           {"iso": "JP", "name": "日本", "v": "17.32%", "ll": [138, 36], "lab": [10, -10]},
           {"iso": "KR", "name": "韩国", "v": "8.89%", "ll": [128, 36.5], "lab": [6, 12]}]


def world(b, X, t, d, cid):
    """像素世界地图（太平洋居中，中国视图）：海外市场亮起、虚线航路上金币一格一格跳回中国、总额计数。
    keys: label · value · dec · unit · note · targets[{iso,name,v,ll,lab}] · home [lon,lat] · at_paths · at_end。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    tP = T(X, b, "at_paths", t, t + 0.6); tE = T(X, b, "at_end", t, t + d * 0.8)
    tg = b.get("targets") or TARGETS
    home = b.get("home", [104, 34])
    # the window holds home and every target (each on its shorter way round), 1 art px per degree, wider than the screen by the pan
    lons = [home[0]] + [min((x["ll"][0] + o for o in (-360, 0, 360)), key=lambda L: abs(L - home[0])) for x in tg]
    lats = [home[1]] + [x["ll"][1] for x in tg]
    span = max(max(lons) - min(lons) + 30, 230 if V else 360); c0 = (max(lons) + min(lons)) / 2
    lon = tuple(b.get("lon") or (round(c0 - span / 2), round(c0 + span / 2)))
    top_, bot_ = (62, -16) if V else (75, -50)
    lat = tuple(b.get("lat") or (max(top_, max(lats) + 14), min(bot_, min(lats) - 12)))
    MW, MH, my = round(lon[1] - lon[0]), round(lat[0] - lat[1]), (118 if V else 34)
    cols = {"CN": "r", **{x["iso"]: "y" for x in tg}}
    key = hkey(cols, lon, lat, MW, MH)
    h = sprite(X, f"sea{AW}x{AH}", lambda: sky(AW, AH, ("k", "b", "b")), 0, 0)[0]
    mu = asset_png(X, f"map{key}", lambda: pacific(MW, MH, cols, lon, lat, land="t"))
    inner = img(mu, 0, 0, MW, MH)
    hx, hy = proj(home, MW, MH, lon, lat)
    inner += f'<i class="hm" style="position:absolute;left:{round(hx - 2) * P}px;top:{round(hy - 2) * P}px;width:{4 * P}px;height:{4 * P}px;background:{PAL["w"]};box-shadow:0 0 0 {P}px {PAL["k"]}"></i>'
    cu, cw, ch = sheet(X, "coin", coin, 4)
    for j, x in enumerate(tg):
        px_, py_ = proj(x["ll"], MW, MH, lon, lat)
        dist = math.hypot(px_ - hx, py_ - hy)
        cx_, cy_ = (px_ + hx) / 2, (py_ + hy) / 2 - dist * 0.32
        n = max(4, int(dist / 5))
        pts = [((1 - u) ** 2 * px_ + 2 * (1 - u) * u * cx_ + u * u * hx, (1 - u) ** 2 * py_ + 2 * (1 - u) * u * cy_ + u * u * hy) for u in (k / n for k in range(1, n))]
        inner += "".join(f'<i class="dt dt{j}" style="position:absolute;left:{round(a - 1) * P}px;top:{round(c - 1) * P}px;width:{2 * P}px;height:{2 * P}px;background:{PAL["w"]};opacity:0"></i>' for a, c in pts)
        inner += f'<i class="mk mk{j}" style="position:absolute;left:{round(px_ - 3) * P}px;top:{round(py_ - 3) * P}px;width:{6 * P}px;height:{6 * P}px;box-shadow:inset 0 0 0 {P}px {PAL["w"]}, 0 0 0 {P}px {PAL["k"]};opacity:0"></i>'
        lab = x.get("lab_v", x.get("lab", [6, -14])) if V else x.get("lab", [6, -14])
        nh, nw, nhh = bimg(X, x["name"], 0, 0, 16, "w", UK)
        X.used_text.update(x["v"])
        bw = max(nw, len(x["v"]) * 32) + 24
        lx = px_ + lab[0] if lab[0] >= 0 else px_ + lab[0] - bw / P
        if lx + bw / P > MW - 2: lx = px_ - abs(lab[0]) - bw / P        # keep the tag on the map
        if lx < 2: lx = px_ + abs(lab[0])
        inner += (f'<div class="tag lab lab{j}" style="left:{round(lx) * P}px;top:{round(py_ + lab[1]) * P}px;opacity:0;display:flex;flex-direction:column;gap:6px;align-items:flex-start">'
                  f'{nh}<span class="pf s32" style="color:{PAL["y"]}">{core_esc(x["v"])}</span></div>')
        for q in range(2):
            inner += spr(cu, cw, ch, 4, 0, 0, f"fc fc{j}{q}", sty="opacity:0")
        tj = tP + 0.28 * j
        X.tw(f'tl.to("{s} .dt{j}", {{opacity:1, duration:0.02, ease:"steps(1)", stagger:{0.32 / n:.4f}}}, {tj:.3f});')
        X.tw(f'tl.set("{s} .mk{j}, {s} .lab{j}", {{opacity:1}}, {tj:.3f});')
        pop_in(X, f"{s} .lab{j}", tj); blink(X, f"{s} .mk{j}", tj + 0.1, t + d - tj - 0.2, 3)
        chip(X, tj, "select", 0.25)
        # coins hop dot to dot back home (stepped motion)
        route = pts[::2] + [(hx, hy)]
        for q in range(2):
            t0 = tj + 0.4 + q * 0.55
            while t0 < t + d - 0.3:
                X.tw(f'tl.set("{s} .fc{j}{q}", {{opacity:1}}, {t0:.3f});')
                for k, (a, c) in enumerate(route):
                    X.tw(f'tl.set("{s} .fc{j}{q}", {{x:{round(a - cw / 2) * P}, y:{round(c - ch / 2) * P}}}, {t0 + k * 0.06:.3f});')
                X.tw(f'tl.set("{s} .fc{j}{q}", {{opacity:0}}, {t0 + len(route) * 0.06:.3f});')
                got_coin(X, t0 + len(route) * 0.06)
                t0 += 1.1 + len(route) * 0.06
    run_frames(X, f"{s} .fc", cw, 4, t, d, fps=10)
    h += f'<div class="lay mp" style="top:{my * P}px;width:{MW * P}px;height:{MH * P}px">{inner}</div>'
    pan(X, f"{s} .mp", t, d, dx=-(MW - AW))
    toggle(X, f"{s} .hm", t, d, 0.2, 1.5, 1, "scale")
    # total
    val = float(b.get("value", 0)); dec = int(b.get("dec", 2 if val != int(val) else 0)); final = f"{val:.{dec}f}"
    uh, uw, _ = bimg(X, b.get("unit", ""), 0, 0, 16, "y", UK, "un") if b.get("unit") else ("", 0, 0)
    lab_ = b.get("label", "")
    lh_, lw_, _ = bimg(X, lab_, 0, 0, 16, "w", UK)
    X.used_text.update(final)
    rowc = (f'<div class="row" style="gap:12px"><div class="pf s48 num" style="width:{len(final) * 48}px;text-align:right;color:{PAL["y"]}">0</div>{uh}</div>')
    note = b.get("note", "")
    X.used_text.update(note)
    nt = f'<div class="vt">{core_esc(note)}</div>' if note else ""
    if V: L, top = 8 * P, 54 * P
    else: L, top = 10 * P, 20 * P
    h += (f'<div class="box tot" style="left:{L}px;top:{top}px;padding:15px 18px;display:flex;flex-direction:column;gap:12px;align-items:flex-start">'
          f'{lh_}{rowc}{nt}</div>')
    step_in(X, f"{s} .tot", t_in(X, t))
    counter(X, f"{s} .num", tP, 0, val, tE - tP, dec=dec, steps=14)
    flash(X, f"{s} .num", tE, 2); chip(X, tE, "up", 0.28)
    page(X, b, t, d, cid, h)


def levelup(b, X, t, d, cid):
    """经验条对比：菜单窗口里两条（或多条）经验条按增速涨满，最快的一条触发 LEVEL UP 横幅 + 星星。
    keys: head · rows[{name,icon(pad|phone|trophy|coin),v(百分比数字),sub,at}] · max · banner · at_up。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    rows_ = b.get("rows", [])
    tU = T(X, b, "at_up", t, t + d * 0.8)
    h = sprite(X, f"menu{AW}x{AH}", lambda: sky(AW, AH, ("k", "p", "k")), 0, 0)[0]
    h += sprite(X, f"stars{AW}x{AH}", lambda: starfield(AW, AH, 50, 3), 0, 0, "sf")[0]
    if V: bx, by, bw, bh = 8, 58, 164, 150
    else: bx, by, bw, bh = 16, 26, 288, 124
    h += f'<div class="box blue win" style="left:{bx * P}px;top:{by * P}px;width:{bw * P}px;height:{bh * P}px"></div>'
    hh, _ = btitle(X, b.get("head", ""), bx + 8, by + 5, bw - 16, px_max=16, k=UK, cls="hd", max_lines=1)
    h += hh
    vmax = float(b.get("max", max([float(r["v"]) for r in rows_] + [100])))
    icons = {"pad": pad, "phone": phone, "trophy": trophy, "coin": coin_stack, "heart": heart, "star": star}
    n = max(1, len(rows_))
    gap = (bh - 22 - 18) / n                 # the bottom 18 art px stay free for the banner
    compact = gap < (44 if V else 19)        # many rows: label and value share a line, thinner bar, no sub line
    best = max(range(n), key=lambda k: float(rows_[k]["v"])) if rows_ else 0
    for k, r in enumerate(rows_):
        y = by + 20 + k * gap
        ih, iw, ihh = sprite(X, f"ic_{r.get('icon', 'star')}", icons.get(r.get("icon"), star), bx + 8, y + 2, f"ic ic{k}")
        h += ih
        nx = bx + 8 + iw + 6
        nh, nw, _ = bimg(X, r["name"], nx, y, 16, "w", UK, f"nm nm{k}")
        h += nh
        val = float(r["v"]); txt = f"+{val:.2f}%"
        X.used_text.update(txt + "+%")
        vs = 48
        if compact:
            vs = 32 if V else 24
            barx, bary, barw = (bx + 8, y + 13, bw - 16) if V else (nx, y + 11, bw - (nx - bx) - 8 - len(txt) * 4 - 6)
            vx, vy, vanc = bx + bw - 8, (y + 2) if V else (y + 10), "r"
            r = dict(r, sub=None)
        elif V:
            barx, bary, barw = bx + 8, y + 24, bw - 16
            vx, vy, vanc = bx + bw - 8, y + 34, "r"
            if r.get("sub"): h += f'<div class="vt sb sb{k}" style="left:{(bx + 8) * P}px;top:{(y + 37) * P}px">{core_esc(r["sub"])}</div>'
        else:
            barx, bary, barw = nx, y + 13, bw - (nx - bx) - 8 - len(txt) * 8 - 6
            vx, vy, vanc = bx + bw - 8, y + 9, "r"
            if r.get("sub"): h += f'<div class="vt sb sb{k}" style="left:{(nx + nw / P + 4) * P}px;top:{(y + 3) * P}px">{core_esc(r["sub"])}</div>'
        if r.get("sub"): X.used_text.update(r["sub"])
        h += bar(X, cid, f"xb xb{k}", barx, bary, barw, 4 if compact else 6, "l" if k == best else "o")
        h += f'<div class="pf s{vs} vv vv{k}" style="left:{round(vx * P - len(txt) * vs)}px;top:{vy * P}px;width:{len(txt) * vs}px;text-align:right;color:{PAL["y"] if k == best else PAL["w"]}">+0.00%</div>'
        ta = T(X, r, "at", t, t + 0.6 + k * 1.2)
        steps_ = max(4, int(val / vmax * 20))
        fill(X, f"{s} .xb{k}", ta, 0.7, val / vmax, n=steps_)
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .vv{k}"); if(!el) return; tl.to(o, {{v:{val}, duration:0.7, ease:"steps({steps_})", onUpdate:()=>{{el.textContent="+"+o.v.toFixed(2)+"%";}}}}, {ta:.3f});}})();')
        for q in range(min(steps_, 8)): chip(X, ta + q * 0.7 / min(steps_, 8), "tick", 0.15)
        step_in(X, f"{s} .ic{k}, {s} .nm{k}, {s} .xb{k}, {s} .vv{k}" + (f", {s} .sb{k}" if r.get("sub") else ""), t_in(X, t) + 0.08 + k * 0.06, dy=3, st=0.02)
        toggle(X, f"{s} .ic{k}", t + k * 0.12, d - k * 0.12, 0.25, -P, 0, "y")
    step_in(X, f"{s} .win", t_in(X, t), dy=0, dur=0.12, n=2); step_in(X, f"{s} .hd", t_in(X, t) + 0.04)
    banner = b.get("banner", "LEVEL UP!")
    X.used_text.update(banner)
    yb = by + bh - 15 if V else by + bh - 19
    bz = next((z for z in ((48,) if V or n > 2 else (72, 48)) + (32, 24) if len(banner) * z <= (AW - 12) * P), 24)
    h += pf(X, banner, AW / 2, yb, bz, PAL["y"], "lv", anchor="c", sty="opacity:0")
    su = asset_png(X, "star", star)
    sx0, yb_ = AW / 2 - 5, yb
    h += "".join(img(su, sx0, yb_, 11, 11, f"st st{k}", sty="opacity:0") for k in range(8))
    X.tw(f'tl.set("{s} .lv", {{opacity:1}}, {tU:.3f}); tl.fromTo("{s} .lv", {{scale:2.2}}, {{scale:1, duration:0.2, ease:"steps(4)"}}, {tU:.3f});')
    toggle(X, f"{s} .lv", tU + 0.25, t + d - tU - 0.3, 0.16, f'"{PAL["w"]}"', f'"{PAL["y"]}"', "color")
    flash(X, f"{s} .xb{best}", tU, 3)
    for k in range(8):
        a = math.tau * k / 8
        X.tw(f'tl.set("{s} .st{k}", {{opacity:1}}, {tU:.3f}); tl.to("{s} .st{k}", {{x:{round(math.cos(a) * (40 if V else 70)) * P}, y:{round(math.sin(a) * 16) * P}, duration:0.36, ease:"steps(6)"}}, {tU:.3f});'
             f'tl.set("{s} .st{k}", {{opacity:0}}, {tU + 0.42:.3f});')
    chip(X, tU, "up", 0.4)
    toggle(X, f"{s} .sf", t, d, 0.2, 0.4, 1)
    page(X, b, t, d, cid, h)


def _char_times(X, text, t, d):
    """when each glyph of text is spoken (narration word times); falls back to an even typewriter."""
    plain = text.replace("|", "")
    i = X.text.find(plain) if getattr(X, "text", "") else -1
    while i >= 0 and X.chars[i][1] < t - 0.3:
        i = X.text.find(plain, i + 1)
    if i >= 0: return [X.chars[i + k][1] for k in range(len(plain))]
    return [t + 0.2 + k * min(0.12, d * 0.7 / max(len(plain), 1)) for k in range(len(plain))]


def dialog(b, X, t, d, cid):
    """RPG 对话框：主持人柴犬站在草地上，台词逐字打出（与口播逐字同步）+ 说到的道具跳出来 + ▼ 光标。
    keys: name（名牌）· text（| 换行）· items[{icon,label,at}]。建议该页 "cap": false（字已在框里）。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    if V: fy, fh, sx, boxy, boxh = 120, 46, 18, 178, 66
    else: fy, fh, sx, boxy, boxh = 66, 46, 34, 116, 52
    h = sprite(X, f"day{AW}x{fy}", lambda: sky(AW, fy, ("u", "s", "c")), 0, 0)[0]
    h += sprite(X, f"cl{AW}", lambda: clouds(AW * 2, 40, seed=7, n=6), 0, 12 if not V else 50, "cl")[0]
    h += sprite(X, f"field{AW}x{fh}", lambda: field(AW, fh), 0, fy)[0]
    for k, x in enumerate((AW - 38, AW - 22) if not V else (AW - 20,)):
        h += sprite(X, "tree", tree, x, fy - 16 + k * 3, "tr")[0]
    shu, shw, shh = sheet(X, "shiba", shiba, 2)
    h += spr(shu, shw, shh, 2, sx, fy + 14 - shh, "sh")
    toggle(X, f"{s} .sh", t, d, 0.3, -P, 0, "y")
    pan(X, f"{s} .cl", t, d, dx=-int(6 * d))
    # items said in the line
    icons = {"trophy": trophy, "coin": coin_stack, "bag": bag, "heart": heart, "star": star, "pad": pad, "phone": phone, "chest": lambda: chest(True)}
    holders = {"monkey": lambda: monkey(0), "phone": phone, "pad": pad, "chest": lambda: chest2(False), "shiba": lambda: shiba(0)}
    items = b.get("items", [])
    span = (AW - (sx + shw) - (44 if not V else 10)) / max(len(items), 1)
    for k, it in enumerate(items):
        cx = sx + shw + span * (k + 0.5) + (6 if not V else 4)
        ground_y = fy + (22 if not V else 24)
        top = ground_y - 2
        if it.get("with") in holders:      # who / what the item belongs to, standing on the grass (faces the host)
            wu = asset_png(X, f"w_{it['with']}", holders[it["with"]]); ww, wh = png_size(X, wu)
            h += img(wu, round(cx - ww / 2), ground_y - wh, ww, wh, f"wh wh{k}", sty="transform:scaleX(-1)" if it["with"] == "monkey" else "")
            step_in(X, f"{s} .wh{k}", t_in(X, t) + 0.06 * k, dy=4)
            top = ground_y - wh - 3
        iu = asset_png(X, f"ic_{it.get('icon', 'star')}", icons.get(it.get("icon"), star)); iw, ihh = png_size(X, iu)
        h += img(iu, round(cx - iw / 2), top - ihh, iw, ihh, f"it it{k}", sty="opacity:0")
        lh, lw, _ = bimg(X, it.get("label", ""), cx, ground_y + 1, 16, "w", UK, f"il il{k}", anchor="c", sty="opacity:0")
        h += lh
        ta = T(X, it, "at", t, t + 0.5 + k)
        X.tw(f'tl.set("{s} .it{k}, {s} .il{k}", {{opacity:1}}, {ta:.3f}); tl.from("{s} .it{k}", {{y:{-14 * P}, duration:0.24, ease:"steps(4)"}}, {ta:.3f});')
        toggle(X, f"{s} .it{k}", ta + 0.3, t + d - ta - 0.3, 0.2, -2 * P, 0, "y")
        chip(X, ta, "select", 0.28)
    # dialogue box + typewriter on the spoken glyph times
    bxx, bw = (6, AW - 12) if V else (10, AW - 20)
    text = b.get("text", "")
    px = 12                              # 12-px pixel font at world scale (72-px glyphs); long text wraps
    lines = [w_ for ln in text.split("|") for w_ in wrap(ln, bw - 14, px)]
    need = len(lines) * (px + 9) + 6
    if need > boxh: boxy -= need - boxh; boxh = need        # more text: the box grows upward over the field
    h += f'<div class="box db" style="left:{bxx * P}px;top:{boxy * P}px;width:{bw * P}px;height:{boxh * P}px"></div>'
    name = b.get("name", "HAT9")
    X.used_text.update(name)
    h += f'<div class="tag nt" style="left:{(bxx + 6) * P}px;top:{(boxy - 9) * P}px"><span class="pf s24" style="position:relative;color:{PAL["y"]}">{core_esc(name)}</span></div>'
    times = _char_times(X, text, t, d)
    k0 = 0
    ly = boxy + 5
    for j, ln in enumerate(lines):
        url, w, hh = btext(X, ln, px, "w", "k", "b")
        h += f'<img class="ln ln{j}" src="{url}" alt="" style="left:{(bxx + 7) * P}px;top:{round(ly * P)}px;width:{w * P}px;height:{hh * P}px;clip-path:inset(0 100% 0 0)">'
        f = _font(px)
        for k in range(1, len(ln) + 1):
            shown = 1 + f.getlength(ln[:k]) + 3
            tk = times[k0 + k - 1]
            X.tw(f'tl.set("{s} .ln{j}", {{clipPath:"inset(0 {max(0, round((w - shown) * P))}px 0 0)"}}, {tk:.3f});')
            if ln[k - 1] not in "，。、！？,.!?": chip(X, tk, "type", 0.16)
        k0 += len(ln); ly += hh + 3
    X.used_text.update("▼")
    h += f'<div class="pf s24 cur" style="left:{(bxx + bw - 14) * P}px;top:{(boxy + boxh - 9) * P}px;color:{PAL["y"]};opacity:0">▼</div>'
    tend = times[-1] + 0.15 if times else t + d * 0.7
    X.tw(f'tl.set("{s} .cur", {{opacity:1}}, {tend:.3f});'); blink(X, f"{s} .cur", tend + 0.25, t + d - tend - 0.3, 3)
    step_in(X, f"{s} .db, {s} .nt", t_in(X, t), dy=6, dur=0.16, n=2, st=0.04)
    page(X, b, t, d, cid, h)


def outro(b, X, t, d, cid):
    """落版：星空 + 逐字掉落的像素标题 + 眨眼的柴犬主持人 + PRESS START。
    keys: title · sub（英文小字）· prompt（闪烁提示，默认 PRESS START）。建议 "cap": false。"""
    AW, AH = art(X); V = X.portrait; s = f"#{cid}"
    h = sprite(X, f"sky_o{AW}x{AH}", lambda: sky(AW, AH, ("k", "k", "b", "p")), 0, 0)[0]
    h += sprite(X, f"stars_o{AW}x{AH}", lambda: starfield(AW, AH, 80, 11), 0, 0, "s1")[0]
    h += sprite(X, f"stars_o2{AW}x{AH}", lambda: starfield(AW, AH, 40, 23), 0, 0, "s2")[0]
    hy = AH - 34 if not V else 196
    h += sprite(X, f"hills_o{AW}", lambda: ridge(AW, 40, "d", seed=8, amp=.4, base=.5), 0, hy)[0]
    title = b.get("title", "第九顶帽子")
    px = fitpx(title, AW - 16, 24, 12)
    gl = [btext(X, c, px, "y", "k", "p") for c in title]
    adv = [_font(px).getlength(c) for c in title]
    tops = [_font(px).getbbox(c)[1] if c.strip() else 0 for c in title]; t0 = min(tops)
    tot = sum(adv) + 4
    x = (AW - tot) / 2
    ty = 64 if V else 22
    for k, (url, w, hh) in enumerate(gl):
        h += img(url, round(x), ty + tops[k] - t0, w, hh, f"g g{k}")
        tg_ = t_in(X, t) + k * 0.06
        X.tw(f'tl.from("{s} .g{k}", {{y:{-40 * P}, opacity:0, duration:0.24, ease:"steps(4)"}}, {tg_:.3f});')
        X.tw(f'tl.to("{s} .g{k}", {{y:{-2 * P}, duration:0.08, ease:"steps(1)", yoyo:true, repeat:1}}, {tg_ + 0.24:.3f});')
        chip(X, tg_ + 0.24, "blip", 0.18)
        x += adv[k]
    sub = b.get("sub", "HAT 9")
    yy = ty + max(g[2] + tops[k] - t0 for k, g in enumerate(gl)) + 4
    h += pf(X, sub, AW / 2, yy, 24, PAL["c"], "sb", anchor="c")
    shu, shw, shh = sheet(X, "shiba", shiba, 2)
    K = 2 * P                                 # the end card is a close-up: the host at twice the world pixel size
    sy = (yy + 9) if not V else yy + 14
    h += spr(shu, shw, shh, 2, (AW - shw * 2) / 2, sy, "sh", k=K)
    shh = shh * 2
    for tb in (t + 0.8, t + 1.9):
        if tb < t + d - 0.1:
            X.tw(f'tl.set("{s} .sh", {{backgroundPositionX:"-{shw * K}px"}}, {tb:.3f}); tl.set("{s} .sh", {{backgroundPositionX:"0px"}}, {tb + 0.14:.3f});')
    X.tw(f'tl.from("{s} .sh", {{y:{20 * P}, opacity:0, duration:0.2, ease:"steps(4)"}}, {t_in(X, t) + 0.12:.3f});')
    X.tw(f'tl.to("{s} .sh", {{y:{-3 * P}, duration:0.1, ease:"steps(2)", yoyo:true, repeat:1}}, {t + 0.6:.3f});')
    prompt = b.get("prompt", "PRESS START")
    h += pf(X, prompt, AW / 2, sy + shh + 6, 32, PAL["w"], "ps", anchor="c")
    step_in(X, f"{s} .sb", t_in(X, t) + 0.35, dy=3)
    blink(X, f"{s} .ps", t + 0.4, max(0.5, d - 2.5), 2)          # blinks, then holds for the last 2 s
    toggle(X, f"{s} .s2", t, d, 0.25, 0, 1)
    chip(X, t_in(X, t), "start", 0.35)
    page(X, b, t, d, cid, h)


# ------------------------------------------------------------------ effects in this style: the game screen around any effect
FX_CSS = r"""
.pxf { pointer-events:none; }
.pxf .bz { position:absolute; inset:12px; box-shadow:0 0 0 6px var(--fg), 0 0 0 60px var(--bg); }
.pxf .bz b, .pxf .bz i { position:absolute; width:6px; height:6px; display:block; }
.pxf .bz b { background:var(--bg); } .pxf .bz i { background:var(--fg); }
.pxf .bar { position:absolute; left:18px; right:18px; background:#1a1c2c; box-shadow:0 6px 0 #333c57; }
.pxf .bar .hud { top:50%; transform:translateY(-50%); }
.pxf .plate { position:absolute; left:0; right:0; display:flex; justify-content:center; }
.pxf .plate .in { position:relative; display:flex; flex-direction:column; gap:6px; background:#1a1c2c; padding:18px 30px 18px;
  box-shadow:0 0 0 6px #f4f4f4, 0 0 0 12px #1a1c2c, 12px 12px 0 12px rgba(26,28,44,.45); }
.pxf .plate .row { position:relative; display:flex; align-items:flex-end; }
.pxf .plate .row > img { position:relative; image-rendering:pixelated; display:block; }
.pxf .plate .nt { position:absolute; left:24px; top:-18px; background:#1a1c2c; box-shadow:0 0 0 3px #f4f4f4, 0 0 0 6px #1a1c2c; padding:6px 9px 3px;
  font-family:var(--f-pixel); font-size:24px; color:#ffcd75; line-height:1; white-space:nowrap; }
.pxf .plate .cur { position:absolute; right:12px; bottom:6px; font-family:var(--f-pixel); font-size:24px; color:#ffcd75; line-height:1; }
.pxf .stat { position:absolute; display:flex; justify-content:space-between; gap:36px; background:#1a1c2c; padding:3px 12px 0;
  font-family:var(--f-body); font-size:24px; line-height:30px; color:#94b0c2; white-space:nowrap; }
.pxf .stat b { font-weight:400; color:#f4f4f4; }
.pxf .scan { position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(10,10,20,.10) 0 1px, transparent 1px 3px); }
"""


def _cut(text, max_px, size=24):
    """fit a line of 12-px pixel type drawn at `size` px into max_px, with an ellipsis."""
    f = _font(12); k = size / 12
    if f.getlength(text) * k <= max_px: return text
    while text and f.getlength(text + "…") * k > max_px: text = text[:-1]
    return text + "…"


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect drawn as a game screen: a bezel in the theme's ink, a status bar with the HUD (hearts,
    topic, world, coin, countdown), the spoken line in an RPG text box (Fusion Pixel, the keyword in gold, typed on, a
    name tag with the effect id, a ▼ cursor) and a status line with label and source. The effect keeps the middle."""
    from h9 import core
    X.css("pixel", CSS); X.css("pixel-fx", FX_CSS)
    V = X.portrait; W, H = X.W, X.H
    s = f"#{cid}c"
    i = X.beat["i"]
    # bezel with stepped (one-pixel-rounded) corners
    e = 12
    cn = (f'<b style="left:-6px;top:-6px"></b><b style="right:-6px;top:-6px"></b><b style="left:-6px;bottom:-6px"></b><b style="right:-6px;bottom:-6px"></b>'
          f'<i style="left:0;top:0"></i><i style="right:0;top:0"></i><i style="left:0;bottom:0"></i><i style="right:0;bottom:0"></i>')
    h = f'<div class="bz">{cn}</div>'
    # status bar + HUD
    bt, bh = (202, 48) if V else (18, 54)
    hu = asset_png(X, "heart", heart); cu, cw, ch = sheet(X, "coin", coin, 4)
    hearts = "".join(f'<img src="{hu}" alt="" style="width:{9 * UK}px;height:{8 * UK}px">' for _ in range(3))
    topic = fit.plain(p.get("topic", ""))
    th = ""
    if topic:
        url, tw, thh = btext(X, topic, 12, "w", "k", None)
        th = f'<img src="{url}" alt="" style="width:{tw * UK}px;height:{thh * UK}px;margin-left:12px">'
    world = f"WORLD {i // 4 + 1}-{i % 4 + 1}"
    X.used_text.update(world + " HAT9 TIME 0123456789×")
    hud_l = f'<div class="hud" style="left:18px">{hearts}<span style="margin-left:6px;color:#f4f4f4">HAT9</span>{th}</div>'
    hud_c = "" if V else f'<div class="hud" style="left:0;right:0;justify-content:center;color:#73eff7">{world}</div>'
    hud_r = (f'<div class="hud" style="right:18px;color:#f4f4f4"><span class="spr coinic" style="width:{cw * UK}px;height:{ch * UK}px;display:block;'
             f'background-image:url({cu});background-size:{cw * UK * 4}px {ch * UK}px"></span><span>×{(i + 1) * 7:02d}</span>'
             f'<span style="margin-left:18px;color:#94b0c2">TIME</span><span class="tm">{math.ceil(d):03d}</span></div>')
    h += f'<div class="bar" style="top:{bt}px;height:{bh}px">{hud_l}{hud_c}{hud_r}</div>'
    run_frames(X, f"{s} .coinic", cw, 4, t, d, fps=8, k=UK)
    ticker(X, f"{s} .tm", t, d, f"String(Math.max(0, Math.ceil({t + d:.3f} - T))).padStart(3, '0')")
    # the spoken line in a text box: keyword (between *) in gold, 24-px pixel type, wrapped, never shrunk below 12
    line = str(p.get("line", "")).replace("|", "")
    plain, gold = "", set()
    for j, seg in enumerate(line.split("*")):
        if j % 2: gold.update(range(len(plain), len(plain) + len(seg)))
        plain += seg
    k = 2                                  # 24-px type at 2× = 48-px glyphs: fits the band effects leave for a caption
    inner_w = (W - 2 * 120 - 60) if V else 1800 - 60
    fpx = 24
    lines = wrap(plain, inner_w / k, fpx)
    if len(lines) > 2: fpx = 12; lines = wrap(plain, inner_w / k, fpx)
    rows, pos, n_all = "", 0, 0
    for j, ln in enumerate(lines):
        runs = []
        for ch_ in ln:
            while pos < len(plain) and plain[pos] != ch_: pos += 1
            col = "y" if pos in gold else "w"
            if runs and runs[-1][1] == col: runs[-1][0] += ch_
            else: runs.append([ch_, col])
            pos += 1
        imgs = ""
        for txt, col in runs:
            url, w_, hh = btext(X, txt, fpx, col, "k", "b")
            imgs += f'<img src="{url}" alt="" style="width:{w_ * k}px;height:{hh * k}px">'
        rows += f'<div class="row r{j}">{imgs}</div>'
        n = len(ln.strip())
        X.tw(f'tl.fromTo("{s} .r{j}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{max(0.1, n * 0.035):.3f}, ease:"steps({max(n, 1)})"}}, {t + 0.2 + n_all * 0.035:.3f});')
        n_all += n
    fxid = str(p.get("fxid") or p.get("fx", "")).upper()
    X.used_text.update(fxid + "▼")
    plate_pos = "top:1326px" if V else "bottom:54px"
    h += (f'<div class="plate" style="{plate_pos}"><div class="in"><div class="nt">{core_esc(fxid)}</div>{rows}'
          f'<div class="cur">▼</div></div></div>')
    X.tw(f'tl.from("{s} .plate .in", {{y:30, opacity:0, duration:0.16, ease:"steps(4)"}}, {t + 0.04:.3f});')
    tend = t + 0.2 + n_all * 0.035
    X.tw(f'tl.set("{s} .cur", {{opacity:0}}, {t:.3f});')
    blink(X, f"{s} .cur", tend, max(0.4, t + d - tend - 0.1), 2)
    chip(X, t + 0.04, "select", 0.22)
    # status line: label (effect name) and source, 24-px pixel type on the ink strip
    lab = fit.plain(p.get("label", "")); src = fit.plain(p.get("src", ""))
    if lab or src:
        if V:
            ft = f'<b>{core_esc(_cut("SOURCE · " + src if src else lab, W - 2 * 56 - 24))}</b>'
            sty = f"left:56px;right:56px;top:1494px;line-height:24px;padding:0 12px"
        else:
            half = (W - 36 - 24 - 36) / 2
            ft = f'<span>{core_esc(_cut(lab, half))}</span><b>{core_esc(_cut("SOURCE · " + src, half) if src else "")}</b>'
            sty = "left:18px;right:18px;bottom:18px"
        X.used_text.update(lab + src + "SOURCE ·…")
        h += f'<div class="stat" style="{sty}">{ft}</div>'
    # the photo mosaic filter for this page: average (pre-blur), sample one pixel per 12-px cell, grow it to the cell,
    # posterise to eight levels a channel
    lv = " ".join(f"{v / 7:.3f}" for v in range(8))
    h += ('<svg width="0" height="0" style="position:absolute"><filter id="pxmo" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">'
          '<feGaussianBlur in="SourceGraphic" stdDeviation="4" edgeMode="duplicate" result="s"/>'
          '<feFlood x="5" y="5" width="2" height="2"/><feComposite width="12" height="12"/><feTile result="a"/>'
          '<feComposite in="s" in2="a" operator="in"/><feMorphology operator="dilate" radius="6"/>'
          f'<feComponentTransfer><feFuncR type="discrete" tableValues="{lv}"/><feFuncG type="discrete" tableValues="{lv}"/><feFuncB type="discrete" tableValues="{lv}"/></feComponentTransfer>'
          '</filter></svg>')
    if X.v.get("meta", {}).get("crt", True): h += '<div class="scan"></div>'
    X.clip(f"{cid}c", t, d, f'<div class="pxs pxo pxf" style="position:absolute;inset:0;background:transparent">{h}</div>', "ctx", 30, track=20, sty=parts["sty"])


SCENES = {"stage": stage, "online": online, "treasure": treasure, "crowd": crowd, "world": world, "levelup": levelup, "dialog": dialog, "outro": outro}
