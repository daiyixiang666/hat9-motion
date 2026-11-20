"""card_wall · 作品墙 — a tilted, moving wall of real thumbnails as the ground of a headline.

A perspective plane larger than the frame carries rows of 16:10 cards (14 px radius, the style's card border); the rows
drift along their length at 40 px/s, alternating direction, so the wall reads as a diagonal river of work. Cards flip
in by column wave (rotateY 90° → 0, 2 frames apart). The wall is dimmed to 38 % under the headline with a radial
falloff (towards the page colour: darker on dark styles, paler on light ones), and stays brightest where the headline is
not: the right third in 16:9, the bottom 400 px in 9:16. At the end (resolve "blur") the wall blurs 24 px and dims so
the next beat's question can sit on it.

p: media (6–60 image / video paths; fewer are repeated by rule, more are sampled evenly; clips show a poster frame)
   title (headline, required unless value is given) · value (optional big number, counted up) · sub
   tilt ([rotateX, rotateZ] degrees; default 16:9 [52, -24], 9:16 [46, -16]) · resolve "blur" | "none"
With no media the cards are style-coloured placeholders (a picture block and 2–3 skeleton lines), never an empty frame.

16:9: headline left-centre (x 110…, block around y 380–620, title 120–150 px; value numeral 200 px), the wall fills
      the frame, brightest on the right third; the headline lines wipe in from the left.
9:16: headline at y 520–900 left-aligned at x 80 (≤ 880 px wide), title 120–150 px, value 250 px; the bottom 400 px
      is wall only; rows run steeper and the plane also creeps upward; the headline lines rise out of masks.
"""
import importlib.util
import math
import pathlib
import re
import sys

from h9 import fit as FT


def _load(name, key):
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A = _load("_fx2", "h9fx__fx2")
MD = _load("_media", "h9fx__media")

F = 1 / 30
DRIFT = 40.0           # px per second along each row
MAX_MEDIA = 60

CSS = r"""
.cw .cw-view { position:absolute; inset:0; overflow:hidden; perspective:1500px; }
.cw .cw-plane { position:absolute; transform-style:preserve-3d; }
.cw .cw-row { position:absolute; left:0; transform-style:preserve-3d; }
.cw .cw-card { position:absolute; top:0; border-radius:14px; overflow:hidden; backface-visibility:hidden;
  box-sizing:border-box; border:var(--cw-bw) solid var(--cw-bc); background-color:var(--card); background-repeat:no-repeat; }
.cw .cw-card.ph i { position:absolute; display:block; border-radius:6px; background:var(--cw-sk); }
.cw .cw-card.ph i.pic { border-radius:8px; background:color-mix(in srgb, var(--accent) 22%, var(--card)); }
.cw .cw-dim { position:absolute; inset:0; pointer-events:none; }
.cw .cw-veil { position:absolute; inset:0; pointer-events:none; background:var(--cw-ground); opacity:0; }
.cw .cw-hl { position:absolute; color:var(--cw-ink); }
.cw .cw-val { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; white-space:nowrap; letter-spacing:-.02em;
  color:var(--cw-mark); font-variant-numeric:tabular-nums; }
.cw .cw-tt { font-family:var(--f-display); font-weight:var(--display-weight, 900); line-height:1.16; }
.cw .cw-tt .ln { display:block; overflow:hidden; white-space:nowrap; padding:.04em 0 .1em; margin:-.04em 0 -.1em; }
.cw .cw-tt .ln > span { display:inline-block; }
.cw .cw-sub { font-family:var(--f-body); font-weight:700; white-space:nowrap; opacity:.88; }
.cw .cw-hl { text-shadow:0 2px 28px var(--cw-shadow); }
"""


def _rgb(c, dflt=(18, 18, 18)):
    c = str(c).strip()
    if c.startswith("#") and len(c) in (4, 7):
        if len(c) == 4:
            c = "#" + c[1] * 2 + c[2] * 2 + c[3] * 2
        return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))
    m = re.match(r"rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+)", c)
    if m:
        return (int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3))))
    return dflt


def _num_parts(v):
    """'197' → ('', 197.0, '', 0) · '4.6万' → ('', 4.6, '万', 1) · 'AI' → None."""
    s = str(v).strip()
    m = re.match(r"^([^\d\-]*)(-?\d[\d,]*(?:\.\d+)?)(.*)$", s)
    if not m:
        return None
    num = m.group(2).replace(",", "")
    dec = 0
    if "." in num:
        dec = len(num.split(".")[1])
    return (m.group(1), float(num), m.group(3), dec, "," in m.group(2))


def _media_list(X, p):
    its = MD.items(X, {"media": p.get("media") or p.get("items") or p.get("images")})
    if len(its) > MAX_MEDIA:
        picked = []
        for k in range(MAX_MEDIA):
            picked.append(its[int(k * len(its) / MAX_MEDIA)])
        its = picked
    return its


def _title_fit(title, w, P, has_value):
    """(px, lines): one line at 150→120 px, else two lines down to 96, else three lines down to 72 (ellipsis last)."""
    mx = 150
    if has_value:
        mx = 120
    f = FT.fit_text(title, w, mx * 1.16 + 1, mx, 120 if not has_value else 96, lh=1.16, max_lines=1)
    if FT.width(f.lines[0]) * f.px <= w * 0.97 and not f.lines[0].endswith("…"):
        return f.px, f.lines
    f = FT.fit_text(title, w, 2 * 120 * 1.16 + 1, 120, 96, lh=1.16, max_lines=2)
    if not any(l.endswith("…") for l in f.lines):
        return f.px, f.lines
    f = FT.fit_text(title, w, 3 * 96 * 1.16 + 1, 96, 72, lh=1.16, max_lines=3)
    return f.px, f.lines


def card_wall(X, cid, t, d, p):
    """作品墙 Card Wall: a tilted moving wall of real thumbnails under a headline (16:9 and 9:16 composed apart)."""
    F_ = "card_wall"
    title = str(p.get("title") or p.get("text") or "").strip()
    value = p.get("value")
    value = "" if value is None else str(value).strip()
    A.need(F_, t, p, [] if (title or value) else ["title (the headline over the wall)"])
    sub = str(p.get("sub") or "").strip()
    resolve = A.choice(F_, p, "resolve", ("blur", "none"), "blur")
    P = X.portrait
    W = X.W
    H = X.H
    tilt = p.get("tilt")
    if isinstance(tilt, (list, tuple)) and len(tilt) == 2:
        rx = float(tilt[0])
        rz = float(tilt[1])
    elif isinstance(tilt, (int, float)) and not isinstance(tilt, bool):
        rx = float(tilt)
        rz = -16.0 if P else -24.0
    else:
        rx = 46.0 if P else 52.0
        rz = -16.0 if P else -24.0
    rx = max(0.0, min(70.0, rx))
    rz = max(-45.0, min(45.0, rz))

    pal = A.pal(X, p)
    ground = pal.get("bg", "#121212")
    ink = pal.get("fg", "#f2f2f2")
    from h9.aefx import _contrast, _lum
    light_ground = (_lum(ground) or 0) > 0.4
    mark = ink
    acc = pal.get("accent")
    if acc and _contrast(acc, ground) >= 4.5:
        mark = acc
    k = A.K.skin(X)
    bw = max(1, int(k.get("bw", 0)) or 1)
    if k.get("bw", 0) >= 3:
        bw = 3
    bc = "color-mix(in srgb, var(--card-fg) 18%, transparent)"
    if k.get("bw", 0) >= 3:
        bc = "var(--k-ink, var(--fg))"

    # ---- the wall
    if P:
        cw_, ch_, gap = 300, 188, 24
        pw, ph = 2900, 5600
        cx_, cy_ = W / 2 + 40, H / 2 - 260      # the far rows reach the top edge (no plain band above the wall)
    else:
        cw_, ch_, gap = 320, 200, 26
        pw, ph = 3900, 3300
        cx_, cy_ = W / 2 + 120, H / 2 - 40
    pitch_x = cw_ + gap
    pitch_y = ch_ + gap
    rows = int(math.ceil(ph / pitch_y))
    travel = DRIFT * d + pitch_x
    cols = int(math.ceil((pw + travel) / pitch_x)) + 1
    its = _media_list(X, p)
    n = len(its)
    atlas = None
    if n:
        atlas = MD.atlas(X, its, 320, 200)
    cards = []
    for r in range(rows):
        row = []
        for c in range(cols):
            x = c * pitch_x
            if n:
                idx = (r * 5 + c * 3 + (r * r) % 7) % n
                url, acols, aw, ah = atlas
                bg = MD.atlas_bg(url, acols, aw, ah, 320, 200, idx, cw_, ch_)
                row.append(f'<div class="cw-card" style="left:{x}px; width:{cw_}px; height:{ch_}px; {bg}"></div>')
            else:
                row.append(_placeholder(r, c, x, cw_, ch_))
        off = -(r % 3) * pitch_x * 0.37
        cards.append(f'<div class="cw-row" data-r="{r}" style="top:{r * pitch_y}px; transform:translateX({off - travel / 2:.0f}px)">{"".join(row)}</div>')
    plane = (f'<div class="cw-plane" style="left:{cx_ - pw / 2:.0f}px; top:{cy_ - ph / 2:.0f}px; width:{pw}px; height:{ph}px; '
             f'transform:rotateX({rx:.1f}deg) rotateZ({rz:.1f}deg)">{"".join(cards)}</div>')

    # ---- the dim: 38 % of the wall's light left under the headline, falling off to the bright side
    g = _rgb(ground)
    core, mid = 0.74, 0.62
    if P:
        core, mid = 0.78, 0.68          # the tall frame puts brighter rows right behind the title's right half
    need = _dim_needed(X, atlas, ground, ink)
    if need > mid:                      # a bright (or, on light styles, a dark) set of pictures: dim harder
        core = min(0.94, need + (core - mid))
        mid = need
    def rgba(a):
        return f"rgba({g[0]},{g[1]},{g[2]},{a:.2f})"
    if P:
        hx, hy = 80, 520
        hw = 880
        dim = (f"radial-gradient(ellipse 860px 620px at 400px 710px, {rgba(core)} 0%, {rgba(mid)} 55%, {rgba(0.3)} 82%, {rgba(0)} 100%),"
               f" linear-gradient(180deg, {rgba(0)} 1220px, {rgba(0.62)} 1320px, {rgba(0.62)} 1470px, {rgba(0)} 1540px),"
               f" linear-gradient(180deg, {rgba(0.35)} 0px, {rgba(0.2)} 420px, {rgba(0.12)} 1100px, {rgba(0)} 1420px, {rgba(0)} 1920px)")
    else:
        hx, hy = 110, 380
        hw = 1000
        dim = (f"radial-gradient(ellipse 900px 520px at 560px 520px, {rgba(core)} 0%, {rgba(mid)} 56%, {rgba(0.3)} 84%, {rgba(0)} 100%),"
               f" linear-gradient(180deg, {rgba(0)} 860px, {rgba(0.6)} 990px, {rgba(0.6)} 1080px),"
               f" linear-gradient(90deg, {rgba(0.4)} 0px, {rgba(0.3)} 900px, {rgba(0)} 1280px, {rgba(0)} 1920px)")

    # ---- the headline
    parts = _num_parts(value) if value else None
    vpx = 0
    vh = 0
    val_html = ""
    if value:
        vmax = 250 if P else 200
        vf = FT.fit_text(value, hw, vmax * 1.05, vmax, 120, lh=1.0, max_lines=1)
        vpx = vf.px
        vh = vpx * 1.0
        shown = value
        if parts:
            pre, num, post, dec, comma = parts
            digits = A.fmt(num, dec) if comma else f"{num:.{dec}f}"
            shown = f'{X.rich(pre)}<b class="cw-n">{digits}</b>{X.rich(post)}'
            X.used_text.update("0123456789.,-" + pre + post)
        else:
            shown = X.rich(vf.lines[0])
            X.used_text.update(vf.lines[0])
        val_html = f'<div class="cw-val" style="font-size:{vpx}px; height:{vh:.0f}px">{shown}</div>'
    tt_html = ""
    tpx = 0
    tlines = []
    if title:
        tpx, tlines = _title_fit(title, hw, P, bool(value))
        ls = ""
        for ln in tlines:
            ls += f'<span class="ln"><span>{A.K.hl_html(X, ln)}</span></span>'
        tt_html = f'<div class="cw-tt" style="font-size:{tpx}px; margin-top:{(18 if value else 0)}px">{ls}</div>'
    sub_html = ""
    spx = 0
    if sub:
        spx = 42 if P else 36
        sf = FT.fit_text(sub, hw, spx * 1.4, spx, 32 if P else 28, max_lines=1)
        spx = sf.px
        sub_html = f'<div class="cw-sub" style="font-size:{spx}px; margin-top:{24 if P else 20}px">{X.rich(sf.lines[0])}</div>'
    block_h = vh + (18 if value and title else 0) + len(tlines) * tpx * 1.16 + ((24 if P else 20) + spx * 1.3 if sub else 0)
    if P:
        mid_y = 710
    else:
        mid_y = 500
    top = mid_y - block_h / 2
    if P:
        top = max(250, min(top, 1300 - block_h))
    else:
        top = max(120, min(top, 900 - block_h))
    hl = f'<div class="cw-hl" style="left:{hx}px; top:{top:.0f}px; width:{hw}px">{val_html}{tt_html}{sub_html}</div>'

    inner = (f'<div class="cw" style="--cw-bw:{bw}px; --cw-bc:{bc}; --cw-sk:color-mix(in srgb, var(--card-fg) 22%, var(--card));'
             f' --cw-ink:{ink}; --cw-mark:{mark}; --cw-ground:{ground}; --cw-shadow:{rgba(0.55)}; position:absolute; inset:0">'
             f'<div class="cw-view">{plane}</div><div class="cw-dim" style="background:{dim}"></div><div class="cw-veil"></div>{hl}</div>')
    X.css("fx-cardwall", CSS)
    s, _k = A.stage(X, cid, t, d, p, inner)
    S = f"{s} .cw"

    # ---- motion
    # rows drift along their length, alternating direction (a pure function of time)
    for r in range(rows):
        off = -(r % 3) * pitch_x * 0.37 - travel / 2
        sign = 1 if r % 2 == 0 else -1
        a = off - sign * DRIFT * d / 2
        b = off + sign * DRIFT * d / 2
        X.tw(f'tl.fromTo("{S} .cw-row[data-r=\'{r}\']", {{x:{a:.1f}}}, {{x:{b:.1f}, duration:{d:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')
    # cards flip in by column wave: rotateY 90° → 0, 2 frames per column
    wave_from = "start"
    X.tw(f'tl.fromTo("{S} .cw-card", {{rotationY:90}}, {{rotationY:0, duration:0.42, ease:"power3.out", immediateRender:true, '
         f'stagger:{{each:{2 * F:.4f}, grid:[{rows},{cols}], axis:"x", from:"{wave_from}"}}}}, {t + 0.02:.3f});')
    if P:
        # 9:16: the plane creeps upward the whole beat (the rows run steeper on the tall frame)
        X.tw(f'tl.fromTo("{S} .cw-plane", {{y:60}}, {{y:-60, duration:{d:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')
    else:
        X.tw(f'tl.fromTo("{S} .cw-plane", {{z:-80}}, {{z:40, duration:{d:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')
    # the dim settles in as the wave passes (the wall is bright for a beat, then the headline claims its side)
    X.tw(f'tl.fromTo("{S} .cw-dim", {{opacity:0.35}}, {{opacity:1, duration:0.5, ease:"power2.out", immediateRender:true}}, {t + 0.3:.3f});')
    t_hl = t + min(0.55, d * 0.18)
    if P:
        X.tw(f'tl.fromTo("{S} .cw-tt .ln > span", {{yPercent:110}}, {{yPercent:0, duration:0.5, ease:"expo.out", stagger:0.08, immediateRender:true}}, {t_hl + 0.12:.3f});')
        if val_html:
            X.tw(f'tl.fromTo("{S} .cw-val", {{y:70, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 -10% 0)", duration:0.5, ease:"expo.out", immediateRender:true}}, {t_hl:.3f});')
    else:
        X.tw(f'tl.fromTo("{S} .cw-tt .ln > span", {{x:-80, clipPath:"inset(0 100% 0 0)"}}, {{x:0, clipPath:"inset(0 -4% 0 0)", duration:0.55, ease:"expo.out", stagger:0.08, immediateRender:true}}, {t_hl + 0.12:.3f});')
        if val_html:
            X.tw(f'tl.fromTo("{S} .cw-val", {{x:-60, clipPath:"inset(0 100% 0 0)"}}, {{x:0, clipPath:"inset(0 -4% 0 0)", duration:0.5, ease:"expo.out", immediateRender:true}}, {t_hl:.3f});')
    if sub_html:
        X.tw(f'tl.fromTo("{S} .cw-sub", {{y:24, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 -20% 0)", duration:0.4, ease:"power3.out", immediateRender:true}}, {t_hl + 0.35:.3f});')
    if parts and val_html:
        pre, num, post, dec, comma = parts
        A.count(X, f"{S} .cw-n", 0, num, t_hl, min(1.4, max(0.6, d * 0.3)), dec=dec, comma=comma)
    X.sfx(t + 0.02, "whoosh_soft", 0.3)
    # resolve: the wall blurs 24 px and sinks into the page colour for the next beat's question
    if resolve == "blur" and d >= 2.0:
        r0 = t + d - 0.8
        X.tw(f'tl.fromTo("{S} .cw-view", {{filter:"blur(0px)"}}, {{filter:"blur(24px)", duration:0.7, ease:"power2.inOut", immediateRender:false}}, {r0:.3f});')
        X.tw(f'tl.fromTo("{S} .cw-veil", {{opacity:0}}, {{opacity:0.45, duration:0.7, ease:"power2.inOut", immediateRender:false}}, {r0:.3f});')


def _lin(v):
    v = v / 255
    if v <= 0.03928:
        return v / 12.92
    return ((v + 0.055) / 1.055) ** 2.4


def _lum3(c):
    return 0.2126 * _lin(c[0]) + 0.7152 * _lin(c[1]) + 0.0722 * _lin(c[2])


def _dim_needed(X, atlas, ground, ink):
    """the veil strength (share of the page colour) at which the headline keeps >= 7.5:1 over the pictures' brightest
    5 % (dark styles) or darkest 5 % (light styles), measured on the atlas the wall is drawn from. 0 without media."""
    if not atlas:
        return 0.0
    try:
        from PIL import Image
        path = X.out / atlas[0]
        with Image.open(path) as im:
            small = im.convert("RGB").resize((160, max(1, int(160 * im.height / im.width))))
            px = list(small.getdata())
    except Exception:
        return 0.0
    g = _rgb(ground)
    f = _rgb(ink, (240, 240, 240))
    lf = _lum3(f)
    dark_text = lf < _lum3(g)
    ls = []
    for c in px:
        ls.append((_lum3(c), c))
    ls.sort(key=lambda q: q[0])
    probe = ls[int(len(ls) * (0.05 if dark_text else 0.95))][1]
    a = 0.0
    while a < 0.95:
        mixed = (probe[0] * (1 - a) + g[0] * a, probe[1] * (1 - a) + g[1] * a, probe[2] * (1 - a) + g[2] * a)
        lm = _lum3(mixed)
        hi = max(lm, lf)
        lo = min(lm, lf)
        if (hi + 0.05) / (lo + 0.05) >= 7.5:
            return a
        a += 0.02
    return 0.95


def _placeholder(r, c, x, w, h):
    """a style-coloured stand-in card: a picture block and 2–3 skeleton lines (widths vary by position)."""
    seed = (r * 7 + c * 13) % 5
    pic_w = int(w * (0.36 + 0.06 * (seed % 3)))
    lines = 2 + (seed % 2)
    out = f'<i class="pic" style="left:14px; top:14px; width:{pic_w}px; height:{h - 28}px"></i>'
    lx = 14 + pic_w + 16
    room = w - lx - 16
    for j in range(lines):
        lw = int(room * (0.92 - 0.22 * ((seed + j) % 3) / 2))
        out += f'<i style="left:{lx}px; top:{24 + j * 34}px; width:{lw}px; height:{16 if j == 0 else 12}px"></i>'
    return f'<div class="cw-card ph" style="left:{x}px; width:{w}px; height:{h}px">{out}</div>'


FX = {"card_wall": card_wall}
