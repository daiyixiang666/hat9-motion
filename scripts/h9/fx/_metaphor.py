"""shared helpers for the "number as a visual metaphor" effects (mosaic_number, seat_swarm, dial, log_scroll,
one_to_many, scan_field, card_fan). Not an effect: files starting with _ are skipped by the loader.

skin()      — per-style shape tokens (corner radius, stroke, shadow, dot shape, entrance ease) as CSS variables, so
              the same effect re-skins across every style; colours and fonts come from the style's own variables
regions()   — the graphic box, the optional subject card and the space beside it, for 16:9 and 9:16
subject()   — the presenter / subject in a small card (still or clip), the way a 口播 keeps the speaker in view
pool()      — the pictures for walls and fans: `items` / `images` / `folder` (stills and clips mixed)
glyph_mask() — a number set in the style's numeral font: its outline as an SVG path and a coverage grid for tiles
stepper()   — a counter that steps through anchors (28 → 88 → 174), each step landing with a punch
"""
import importlib.util
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).parent


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, HERE / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


W3 = load("_w3")
MD = load("_media")


# ---------------------------------------------------------------- style skin
# r: corner radius of panels/cards (px) · tr: radius of small tiles · sw: stroke width · dot: border-radius of dots
# shadow: panel/card shadow · flat: true = no gradients or glows · tilt: cards sit slightly askew (collage styles)
SKINS = {
    "default":  {"r": 14, "tr": 4, "sw": 4, "dot": "50%", "shadow": "0 24px 60px rgba(0,0,0,.30)", "tilt": 0, "panel": "card"},
    "poster":   {"r": 0, "tr": 0, "sw": 6, "dot": "50%", "shadow": "none", "tilt": 0, "panel": "rule"},
    "minimal":  {"r": 2, "tr": 0, "sw": 2, "dot": "50%", "shadow": "none", "tilt": 0, "panel": "rule"},
    "zine":     {"r": 0, "tr": 0, "sw": 5, "dot": "50%", "shadow": "8px 8px 0 var(--fg)", "tilt": 2.2, "panel": "card"},
    "pixel":    {"r": 0, "tr": 0, "sw": 6, "dot": "0", "shadow": "6px 6px 0 rgba(0,0,0,.55)", "tilt": 0, "panel": "card"},
    "sketch":   {"r": 6, "tr": 2, "sw": 4, "dot": "50%", "shadow": "none", "tilt": 1.2, "panel": "card"},
    "ink":      {"r": 2, "tr": 0, "sw": 3, "dot": "50%", "shadow": "none", "tilt": 0, "panel": "rule"},
    "hud":      {"r": 2, "tr": 0, "sw": 2, "dot": "50%", "shadow": "0 0 30px color-mix(in srgb, var(--accent) 35%, transparent)", "tilt": 0, "panel": "card"},
    "screen":   {"r": 14, "tr": 6, "sw": 3, "dot": "50%", "shadow": "0 30px 70px rgba(0,0,0,.45)", "tilt": 0, "panel": "card"},
    "flat":     {"r": 26, "tr": 10, "sw": 5, "dot": "50%", "shadow": "none", "tilt": 0, "panel": "card"},
    "papercut": {"r": 6, "tr": 3, "sw": 4, "dot": "50%", "shadow": "0 8px 0 rgba(0,0,0,.16), 0 18px 32px rgba(0,0,0,.22)", "tilt": 0.8, "panel": "card"},
    "press":    {"r": 4, "tr": 2, "sw": 3, "dot": "50%", "shadow": "0 14px 34px rgba(0,0,0,.18)", "tilt": 0, "panel": "card"},
    "doc":      {"r": 2, "tr": 0, "sw": 2, "dot": "50%", "shadow": "0 30px 80px rgba(0,0,0,.6)", "tilt": 0, "panel": "card"},
    "atlas":    {"r": 4, "tr": 2, "sw": 3, "dot": "50%", "shadow": "0 20px 50px rgba(0,0,0,.4)", "tilt": 0, "panel": "card"},
    "clay":     {"r": 24, "tr": 10, "sw": 5, "dot": "50%", "shadow": "0 18px 40px rgba(60,40,30,.28), inset 0 -6px 0 rgba(0,0,0,.08)", "tilt": 0, "panel": "card"},
    "iso3d":    {"r": 20, "tr": 8, "sw": 5, "dot": "50%", "shadow": "0 18px 0 rgba(0,0,0,.10), 0 30px 50px rgba(80,40,120,.22)", "tilt": 0, "panel": "card"},
    "chrome3d": {"r": 12, "tr": 4, "sw": 3, "dot": "50%", "shadow": "0 0 40px color-mix(in srgb, var(--accent) 40%, transparent)", "tilt": 0, "panel": "card"},
    "studio":   {"r": 10, "tr": 4, "sw": 3, "dot": "50%", "shadow": "0 30px 80px rgba(0,0,0,.55)", "tilt": 0, "panel": "card"},
    "reel":     {"r": 12, "tr": 4, "sw": 4, "dot": "50%", "shadow": "0 24px 60px rgba(0,0,0,.35)", "tilt": 0, "panel": "card"},
}


def style_id(X):
    mod = X.S.get("_mod")
    name = getattr(mod, "__name__", "")
    return name.rsplit(".", 1)[-1]


def skin(X):
    sid = style_id(X)
    base = dict(SKINS["default"])
    own = SKINS.get(sid)
    if own is None:
        tok = X.S.get("tokens", {})
        cr = str(tok.get("cap-radius", "")).replace("px", "")
        try:
            base["r"] = min(28, float(cr))
        except ValueError:
            pass
    else:
        base.update(own)
    base["id"] = sid
    ease = X.M.get("ease", "expo.out")
    base["ease"] = ease
    base["stepped"] = ease.startswith("steps")
    return base


def skin_vars(sk):
    parts = [
        f"--mt-r:{sk['r']}px",
        f"--mt-tr:{sk['tr']}px",
        f"--mt-sw:{sk['sw']}px",
        f"--mt-dot:{sk['dot']}",
        f"--mt-shadow:{sk['shadow']}",
    ]
    return "; ".join(parts)


def ease_in(sk, fallback="expo.out"):
    """the style's entrance ease (stepped for pixel / zine, springy for flat / iso3d)."""
    e = sk.get("ease") or fallback
    return e


BASE_CSS = """
.fx .mt { position:absolute; inset:0; }
.fx .mt .mt-card { position:absolute; background:var(--card); color:var(--card-fg); border-radius:var(--mt-r); box-shadow:var(--mt-shadow); overflow:hidden; }
.fx .mt .mt-rule { position:absolute; border-top:var(--mt-sw) solid var(--fg); border-bottom:1px solid var(--line); }
.fx .mt .mt-k { font-family:var(--f-num, var(--f-display)); font-weight:900; font-variant-numeric:tabular-nums; letter-spacing:-.02em; line-height:1; white-space:nowrap; }
.fx .mt .mt-t { font-family:var(--f-display); font-weight:900; line-height:1.12; color:var(--fg); }
.fx .mt .mt-t .fl { display:block; white-space:nowrap; }
.fx .mt .mt-s { font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.35; }
.fx .mt .mt-s .fl { display:block; white-space:nowrap; }
.fx .mt .mt-pill { position:absolute; display:inline-flex; align-items:center; gap:.4em; white-space:nowrap; font-family:var(--f-body); font-weight:800;
  color:var(--bg); background:var(--fg); padding:.28em .7em; border-radius:calc(var(--mt-r) * 2.5); }
.fx .mt .mt-pill.acc { background:var(--accent); color:var(--card); }
.fx .mt .mt-sub { position:absolute; overflow:hidden; border-radius:var(--mt-r); box-shadow:var(--mt-shadow); background:var(--card); }
.fx .mt .mt-sub > img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .mt .mt-subf { position:absolute; border-radius:calc(var(--mt-r) + 4px); background:var(--card); box-shadow:var(--mt-shadow); }
.fx .mt .mt-subl { position:absolute; transform:translateX(-50%); white-space:nowrap; font:800 26px var(--f-body); color:var(--bg); background:var(--fg); padding:4px 14px; border-radius:calc(var(--mt-r) * 2); }
.fx .mt .mt-mock { position:absolute; font:700 18px var(--f-body); color:var(--bg); background:var(--muted); padding:3px 10px; border-radius:4px; }
.st-sketch .fx .mt .mt-card, .st-sketch .fx .mt .mt-sub, .st-sketch .fx .mt .mt-subf { border:3px solid var(--fg); }
.st-pixel .fx .mt .mt-card, .st-pixel .fx .mt .mt-subf { border:4px solid var(--fg); }
.st-zine .fx .mt .mt-card, .st-zine .fx .mt .mt-subf { border:3px solid var(--fg); }
.st-hud .fx .mt .mt-card, .st-screen .fx .mt .mt-card { border:1px solid color-mix(in srgb, var(--accent) 40%, transparent); }
"""


def base(X):
    W3.base(X)
    X.css("fx-mt", BASE_CSS)


def wrap(X, sk, inner, extra_cls=""):
    return f'<div class="mt {extra_cls}" style="{skin_vars(sk)}">{inner}</div>'


# ---------------------------------------------------------------- colours (literal, for GSAP)
def colors(X, p):
    from h9.aefx import THEMES
    tok = dict(X.S.get("tokens", {}))
    th = THEMES.get(p.get("theme")) or {}
    out = {}
    defaults = {"fg": "#111111", "bg": "#f0ece3", "accent": "#e2321f", "muted": "#625d56", "card": "#fbfaf6", "line": "#d3ccbf", "card-fg": "#111111"}
    for key in defaults:
        v = th.get(key, tok.get(key))
        if isinstance(v, str) and v.startswith("#"):
            out[key] = v
        else:
            out[key] = defaults[key]
    return out


# ---------------------------------------------------------------- layout
def regions(X, p, has_sub, sub_ar=0.8, graphic_share=None, hero_ar=1.2, row=None):
    """{"g": graphic box, "s": subject box | None, "side": the free space beside the subject | None} as (x0, y0, x1, y1).
    9:16: the hero spans ~90 % of the width; under it a row holds the subject card (and, with row="info", a block beside
    it); the whole group is centred between the header and the caption. row="center" puts a lone subject in the middle.
    16:9: the subject sits in a right-hand column. Boxes keep clear of the header, the caption and the platform buttons."""
    x0, y0, x1, y1 = W3.box(X)
    gap = 36
    if X.portrait:
        ax0 = 56
        ax1 = X.W - 56
        top = 250
        bottom = 1270 if p.get("line") else 1460
        avail = bottom - top
        hero_w = ax1 - ax0
        hero_h = hero_w / hero_ar
        has_row = has_sub or row == "info"
        row_h = 0
        if has_sub:
            row_h = 400
        elif row == "info":
            row_h = 300
        total = hero_h
        if has_row:
            total = hero_h + gap + row_h
        if total > avail:
            hero_h = max(300.0, avail - (gap + row_h if has_row else 0))
            total = hero_h + (gap + row_h if has_row else 0)
        gy0 = top + (avail - total) / 2
        g = (ax0, gy0, ax1, gy0 + hero_h)
        if not has_row:
            return {"g": g, "s": None, "side": None}
        ry0 = gy0 + hero_h + gap
        ry1 = ry0 + row_h
        if not has_sub:
            return {"g": g, "s": None, "side": (ax0, ry0, X.W - 120, ry1)}
        sw = row_h * sub_ar
        if row == "info":
            sx1 = X.W - 120
            sx0 = sx1 - sw
            return {"g": g, "s": (sx0, ry0, sx1, ry1), "side": (ax0, ry0, sx0 - gap, ry1)}
        sx0 = (X.W - sw) / 2
        return {"g": g, "s": (sx0, ry0, sx0 + sw, ry1), "side": None}
    if not has_sub:
        return {"g": (x0, y0, x1, y1), "s": None, "side": None}
    share = graphic_share or 0.64
    gx1 = x0 + (x1 - x0) * share
    cx0 = gx1 + gap * 1.5
    cw = x1 - cx0
    sh = min((y1 - y0) * 0.62, cw / sub_ar)
    sw = sh * sub_ar
    sx0 = cx0 + (cw - sw) / 2
    sub = (sx0, y1 - sh, sx0 + sw, y1)
    side = (cx0, y0, x1, y1 - sh - gap)
    return {"g": (x0, y0, gx1, y1), "s": sub, "side": side}


def subject(X, cid, t, d, p, box, sk, at=None):
    """the subject card (p.subject: a still or a clip; p.subject_label: a name chip). Returns html for the clip.
    A clip plays in a root-level wrapper above the effect (HyperFrames seeks only top-level timed media)."""
    from h9 import fit
    src = p.get("subject")
    if not src or not box:
        return ""
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0
    at = t + 0.35 if at is None else at
    focus = p.get("subject_focus")
    frame = f'<div class="mt-subf" style="left:{x0 - 5:.0f}px; top:{y0 - 5:.0f}px; width:{w + 10:.0f}px; height:{h + 10:.0f}px"></div>'
    html = frame
    rect = (f"inset:auto; left:{x0:.0f}px; top:{y0:.0f}px; width:{w:.0f}px; height:{h:.0f}px; "
            f"border-radius:var(--mt-r, 14px); overflow:hidden; {skin_vars(sk)}")
    if fit.is_video(src):
        _, sel = fit.media(X, cid, "subj", src, t, d, "mt-subv", focus=focus, fill="cover", z=4, start=float(p.get("subject_start", 0)), extra_style=rect)
        if str(src).lower().endswith(".webm"):
            X.css(f"mt-subfit-{cid}", f"{sel} video {{ object-fit:contain !important; object-position:50% 100% !important; }} "
                                      f"{sel} {{ background:radial-gradient(ellipse 70% 70% at 50% 40%, color-mix(in srgb, var(--card) 85%, var(--accent) 15%), var(--card)); }}")
    else:
        url = X.asset(src)
        pos = fit.focus_css(focus)
        html += f'<div class="mt-sub" style="left:{x0:.0f}px; top:{y0:.0f}px; width:{w:.0f}px; height:{h:.0f}px"><img src="{url}" alt="" style="object-position:{pos}"></div>'
        sel = f"#{cid} .mt-sub"
    e = ease_in(sk)
    X.tw(f'tl.from("#{cid} .mt-subf", {{y:80, opacity:0, duration:0.6, ease:"{e}"}}, {at:.3f});')
    X.tw(f'tl.from("{sel}", {{y:80, opacity:0, duration:0.6, ease:"{e}"}}, {at:.3f});')
    lab = p.get("subject_label")
    if lab:
        chip = f'<div class="mt-subl" style="left:{x0 + w / 2:.0f}px; top:{y1 - 22:.0f}px">{X.rich(lab)}</div>'
        label_over(X, cid, t, d, sk, chip, at + 0.45)
    return html


def over(X, cid, key, t, d, sk, html, cls="", track=25):
    """html in its own clip above the effect (and above any subject clip); select it with '#<cid><key> …'."""
    X.clip(f"{cid}{key}", t, d, f'<div class="mt {cls}" style="{skin_vars(sk)}">{html}</div>', "fx mt-over", 6, track=track)
    return f"#{cid}{key}"


def label_over(X, cid, t, d, sk, chip_html, at):
    """a name chip in its own clip above the effect, so it also sits over a subject clip (which plays above the effect)."""
    X.clip(f"{cid}sl", t, d, f'<div class="mt" style="{skin_vars(sk)}">{chip_html}</div>', "fx mt-over", 5, track=24)
    X.tw(f'tl.from("#{cid}sl .mt-subl", {{y:16, opacity:0, duration:0.35, ease:"back.out(2)"}}, {at:.3f});')


def mock_tag(X, p, x, y):
    if not p.get("mock"):
        return ""
    lab = p["mock"] if isinstance(p["mock"], str) else "示意"
    X.used_text.update(lab)
    return f'<div class="mt-mock" style="left:{x:.0f}px; top:{y:.0f}px">{X.rich(lab)}</div>'


# ---------------------------------------------------------------- pictures
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp"}
VID_EXT = {".mp4", ".mov", ".webm", ".m4v"}


def pool(X, p, cap=400):
    """the pictures for a wall / fan: p.items | p.images | p.media, or p.folder (every still and clip in it, sorted)."""
    from h9 import fit
    folder = p.get("folder")
    if folder:
        root = pathlib.Path(folder)
        if not root.is_absolute():
            root = X.src / folder
        if not root.exists():
            raise SystemExit(f"folder not found: {root}")
        found = []
        for f in sorted(root.iterdir()):
            ext = f.suffix.lower()
            if ext in IMG_EXT or ext in VID_EXT:
                found.append(str(f))
        q = dict(p)
        q["items"] = found
        its = MD.items(X, q)
    else:
        its = MD.items(X, p)
    if len(its) > cap:
        step = len(its) / cap
        picked = []
        for i in range(cap):
            picked.append(its[int(i * step)])
        its = picked
    return its


def tile_order(n_tiles, n_items, cols, rand):
    """which picture each tile shows: recycled when there are fewer pictures than tiles, never the same picture as the
    tile to its left or above (seeded)."""
    out = []
    for i in range(n_tiles):
        tries = 0
        while True:
            k = rand.randrange(n_items)
            left = out[i - 1] if i % cols else -1
            up = out[i - cols] if i >= cols else -1
            if n_items < 3 or (k != left and k != up) or tries > 6:
                break
            tries += 1
        out.append(k)
    return out


# ---------------------------------------------------------------- numerals as shapes
def num_font(X):
    """(font id, font file) of the style's numeral face (fonts.num, else display), the first file that exists."""
    from h9 import fonts
    roles = X.S.get("fonts", {})
    for role in ("num", "display", "body"):
        ids = roles.get(role)
        if not ids:
            continue
        if not isinstance(ids, list):
            ids = [ids]
        for fid in ids:
            meta = fonts.REG.get(fid)
            if not meta:
                continue
            path = fonts.find(meta["file"])
            if path:
                return fid, path
    meta = fonts.REG["noto-sans-sc"]
    return "noto-sans-sc", fonts.find(meta["file"])


def _axes(path):
    from fontTools.ttLib import TTFont
    f = TTFont(str(path), lazy=True)
    if "fvar" not in f:
        return None
    axes = {}
    for ax in f["fvar"].axes:
        if ax.axisTag == "wght":
            axes["wght"] = min(ax.maxValue, 900)
    return axes or None


def _flatten(cmds, fs, ox, base):
    """glyph commands (em units, y up) -> contours of (x, y) px points."""
    contours = []
    cur = []
    px, py = 0.0, 0.0
    for c in cmds:
        op = c[0]
        if op == "M":
            if len(cur) > 2:
                contours.append(cur)
            px, py = c[1], c[2]
            cur = [(ox + px * fs, base - py * fs)]
        elif op == "L":
            px, py = c[1], c[2]
            cur.append((ox + px * fs, base - py * fs))
        elif op == "Q":
            for k in range(1, 7):
                u = k / 6
                a = (1 - u) * (1 - u)
                b = 2 * (1 - u) * u
                e = u * u
                x = a * px + b * c[1] + e * c[3]
                y = a * py + b * c[2] + e * c[4]
                cur.append((ox + x * fs, base - y * fs))
            px, py = c[3], c[4]
        elif op == "C":
            for k in range(1, 9):
                u = k / 8
                a = (1 - u) ** 3
                b = 3 * (1 - u) ** 2 * u
                e = 3 * (1 - u) * u * u
                g = u ** 3
                x = a * px + b * c[1] + e * c[3] + g * c[5]
                y = a * py + b * c[2] + e * c[4] + g * c[6]
                cur.append((ox + x * fs, base - y * fs))
            px, py = c[5], c[6]
        elif op == "Z":
            if len(cur) > 2:
                contours.append(cur)
            cur = []
    if len(cur) > 2:
        contours.append(cur)
    return contours


def glyph_layout(X, text, box_w, box_h, cx, cy, track=0.02):
    """set `text` in the style's numeral face, as large as fits box_w × box_h, centred on (cx, cy).
    Returns {"d": svg path, "contours": [...], "fs": font px, "bbox": (x0, y0, x1, y1), "font": id}."""
    from h9 import glyphs
    fid, path = num_font(X)
    axes = _axes(path)
    out = glyphs.outlines(path, text, axes)
    if not out:
        fid = "noto-sans-sc"
        from h9 import fonts
        path = fonts.find(fonts.REG[fid]["file"])
        out = glyphs.outlines(path, text, _axes(path))
    # measure in em: advances, ink top / bottom
    adv = 0.0
    top = 0.0
    bot = 0.0
    for ch in text:
        g = out.get(ch)
        if not g:
            adv += 0.3
            continue
        for c in g["p"]:
            ys = c[2::2] if len(c) > 2 else []
            for y in ys:
                top = max(top, y)
                bot = min(bot, y)
        adv += g["a"] + track
    adv -= track
    ink_h = max(0.5, top - bot)
    fs = min(box_w / max(adv, 0.3), box_h / ink_h)
    ox = cx - adv * fs / 2
    base = cy + (top + bot) / 2 * fs
    pen = 0.0
    contours = []
    for ch in text:
        g = out.get(ch)
        if not g:
            pen += 0.3
            continue
        contours += _flatten(g["p"], fs, ox + pen * fs, base)
        pen += g["a"] + track
    parts = []
    for ring in contours:
        pts = []
        for x, y in ring:
            pts.append(f"{x:.1f},{y:.1f}")
        parts.append("M" + "L".join(pts) + "Z")
    bbox = (ox, base - top * fs, ox + adv * fs, base - bot * fs)
    return {"d": "".join(parts), "contours": contours, "fs": fs, "bbox": bbox, "font": fid}


def coverage(contours, gx0, gy0, pitch_x, pitch_y, cols, rows, W, H):
    """fraction of each grid cell inside the glyphs (even-odd fill) -> [rows][cols] floats. Rasterised with Pillow."""
    from PIL import Image, ImageChops, ImageDraw
    k = 4                                   # supersampling per cell side
    mw = cols * k
    mh = rows * k
    acc = Image.new("1", (mw, mh), 0)
    sx = k / pitch_x
    sy = k / pitch_y
    for ring in contours:
        pts = []
        for x, y in ring:
            pts.append(((x - gx0) * sx, (y - gy0) * sy))
        layer = Image.new("1", (mw, mh), 0)
        ImageDraw.Draw(layer).polygon(pts, fill=1)
        acc = ImageChops.logical_xor(acc, layer)
    small = acc.convert("L").resize((cols, rows), Image.BOX)
    px = small.load()
    grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(px[c, r] / 255.0)
        grid.append(row)
    return grid


# ---------------------------------------------------------------- numbers
def split_num(v):
    """"100+" -> (100.0, "", "+", 0) · "¥4.8万" -> (4.8, "¥", "万", 1) · 52 -> (52.0, "", "", 0)."""
    s = str(v).strip()
    i = 0
    while i < len(s) and not (s[i].isdigit() or (s[i] == "-" and i + 1 < len(s) and s[i + 1].isdigit())):
        i += 1
    j = i
    while j < len(s) and (s[j].isdigit() or s[j] in ".,"):
        j += 1
    pre = s[:i]
    core = s[i:j].replace(",", "")
    suf = s[j:]
    try:
        val = float(core) if core else 0.0
    except ValueError:
        val = 0.0
    dec = 0
    if "." in core:
        dec = len(core.split(".")[1])
    return val, pre, suf, dec


def anchors(X, raw, t, d, first=0.25, last=0.72):
    """[[value, at], ...] or [value, ...] -> [(time, value_str)] inside the beat; missing times follow the narration, else spread evenly."""
    U = load("_ui")
    items = []
    for a in raw:
        if isinstance(a, (list, tuple)):
            items.append([a[0], a[1] if len(a) > 1 else None])
        else:
            items.append([a, None])
    n = len(items)
    auto = U.spread(n, t + d * first, t + d * last)
    times = []
    fixed = []
    texts = []
    for i in range(n):
        v = items[i][0]
        at = items[i][1]
        times.append(U.when(X, at, t, auto[i]))
        fixed.append(at is not None)
        texts.append(str(v))
    times = U.follow(X, texts, t, d, times, fixed, gap=0.2)      # a value lands when it is said, when it is said
    out = []
    for i in range(n):
        when = min(max(times[i], t + 0.05), t + d - 0.3)
        out.append((when, texts[i]))
    out.sort()
    return out


def stepper_html(X, steps, cls="mt-k"):
    """<span class=cls><b class=n>first</b><i class="sf" data-k=..>suffix</i>…</span>: one suffix span per distinct suffix."""
    sufs = []
    for _, v in steps:
        _, pre, suf, _ = split_num(v)
        if suf and suf not in sufs:
            sufs.append(suf)
    pre0 = split_num(steps[0][1])[1] if steps else ""
    v0, _, _, dec0 = split_num(steps[0][1]) if steps else (0, "", "", 0)
    X.used_text.update("0123456789.,+-%" + "".join(sufs) + pre0)
    sf_html = ""
    for k, s in enumerate(sufs):
        sf_html += f'<i class="sf" data-k="{k}" style="font-style:normal; opacity:0">{X.rich(s)}</i>'
    first = f"{0:,.{dec0}f}"
    return f'<span class="{cls}">{X.rich(pre0)}<b class="n" style="font-weight:inherit">{first}</b>{sf_html}</span>', sufs


def stepper(X, sel, steps, sufs, start=0.0, dur=0.5, punch=True, sfx="count"):
    """count the number in `sel` through the anchor values; each step eases in and lands with a scale punch."""
    prev = start
    for i, (when, v) in enumerate(steps):
        val, pre, suf, dec = split_num(v)
        js_f = f'(x)=>x.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})'
        X.tw(f'(()=>{{const o={{v:{prev}}}, el=document.querySelector("{sel} .n"), f={js_f}; if(!el) return; '
             f'tl.to(o, {{v:{val}, duration:{dur:.2f}, ease:"power3.out", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {when:.3f});}})();')
        for k, s in enumerate(sufs):
            op = 1 if s == suf else 0
            X.tw(f'tl.set("{sel} .sf[data-k=\'{k}\']", {{opacity:{op}}}, {when + dur * 0.8:.3f});')
        if punch:
            X.tw(f'tl.fromTo("{sel}", {{scale:1}}, {{keyframes:[{{scale:1.12, duration:0.08, ease:"power2.out"}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], immediateRender:false}}, {when + dur * 0.75:.3f});')
        if sfx:
            X.sfx(when, sfx)
        prev = val


def fit_text(X, text, w, h, max_px, min_px=20, max_lines=2):
    s, lines = W3.fit_px(X, text, w, h, max_px, min_px, max_lines)
    return s, W3.lines_html(X, lines), len(lines)


def swarm_palette(X, p, sk):
    """3–4 accent colours for swarms (hex): the accent, two hue turns of it at the same lightness and saturation, and the
    ink colour. Ink-wash styles keep to the accent and ink tones."""
    import colorsys
    col = colors(X, p)
    acc = col["accent"].lstrip("#")
    if len(acc) == 3:
        acc = acc[0] * 2 + acc[1] * 2 + acc[2] * 2
    r = int(acc[0:2], 16) / 255
    g = int(acc[2:4], 16) / 255
    b = int(acc[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out = [col["accent"]]
    if sk.get("id") in ("ink", "minimal", "doc"):
        out.append(col["card-fg"])
        out.append(col["muted"])
        return out
    s2 = max(0.55, s)
    l2 = min(0.6, max(0.42, l))
    for turn in (0.36, 0.5):
        rr, gg, bb = colorsys.hls_to_rgb((h + turn) % 1.0, l2, s2)
        out.append(f"#{int(rr * 255):02x}{int(gg * 255):02x}{int(bb * 255):02x}")
    out.append(col["card-fg"])
    return out


BRUSH_SVG = ('<svg width="0" height="0" style="position:absolute"><filter id="{fid}" x="-10%" y="-10%" width="120%" height="120%">'
             '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7" result="n"/>'
             '<feDisplacementMap in="SourceGraphic" in2="n" scale="{k}" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')


def brush_filter(cid, k=9):
    """an SVG displacement filter that roughens edges like a loaded brush (ink styles); use filter:url(#<cid>-brush)."""
    fid = f"{cid}-brush"
    return BRUSH_SVG.replace("{fid}", fid).replace("{k}", str(k)), fid
