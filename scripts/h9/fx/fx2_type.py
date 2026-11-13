"""fx2 · type as image: word_mosaic · type_mask · weight_breath · unroll — the letters are the picture. Headline glyph
shapes are rasterised at build time with the style's own display font (so the mosaic / the window point match what
the browser draws); colours / fonts only from the style tokens.
"""
import importlib.util
import math
import pathlib
import sys

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]
K = A.K

CSS = r"""
.f2 .wm-g { position:absolute; left:0; top:0; display:flex; align-items:center; justify-content:center; line-height:1; font-family:var(--f-body); font-weight:900;
  background:var(--fg); color:var(--bg); border-radius:3px; will-change:transform; }
.f2 .wm-a { position:absolute; left:0; top:0; line-height:1; font-family:var(--f-body); font-weight:700; color:var(--fg); opacity:.17; }
.f2 .wm-under { position:absolute; inset:0; opacity:0; }
.f2 .wm-ul { position:absolute; left:0; right:0; text-align:center; font-weight:900; line-height:1.02; color:var(--accent); white-space:nowrap; }
.f2 .wm-k { position:absolute; font:800 34px var(--f-body); color:var(--muted); letter-spacing:.1em; white-space:nowrap; }
.f2 .tm-svg { position:absolute; left:0; top:0; overflow:visible; }
.f2 .tm-k { position:absolute; font:800 34px var(--f-body); letter-spacing:.14em; color:var(--fg); white-space:nowrap; }
.f2 .wb-l { position:absolute; white-space:nowrap; font-family:var(--f-display); line-height:1.12; color:var(--fg); }
.f2 .wb-l i { display:inline-block; font-style:normal; transform-origin:50% 75%; -webkit-text-stroke:var(--sw, 0px) currentColor; }
.f2 .wb-bar { position:absolute; border-radius:999px; background:var(--accent); transform-origin:50% 100%; }
.f2 .wb-base { position:absolute; height:4px; background:color-mix(in srgb, var(--fg) 30%, transparent); }
.f2 .ur-rod { position:absolute; border-radius:24px; background:linear-gradient(180deg, color-mix(in srgb, var(--fg) 55%, var(--bg)), var(--fg) 45%, color-mix(in srgb, var(--fg) 40%, #000)); }
.f2 .ur-paper { position:absolute; background:var(--card); color:var(--card-fg); overflow:hidden; box-shadow:0 20px 60px rgba(0,0,0,.28); }
.f2 .ur-paper::after { content:""; position:absolute; inset:0; background:repeating-linear-gradient(180deg, transparent 0 46px, color-mix(in srgb, var(--card-fg) 13%, transparent) 46px 49px); pointer-events:none; }
.f2 .ur-roll { position:absolute; border-radius:999px; overflow:hidden;
  background:linear-gradient(180deg, color-mix(in srgb, var(--card) 70%, #000), var(--card) 40%, color-mix(in srgb, var(--card) 60%, #000)); box-shadow:0 14px 30px rgba(0,0,0,.35); }
.f2 .ur-roll i { position:absolute; inset:0; background:repeating-linear-gradient(180deg, transparent 0 10px, color-mix(in srgb, var(--card-fg) 14%, transparent) 10px 12px); }
.f2 .ur-hd { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.1; text-align:center; }
.f2 .ur-hd .sl { display:block; white-space:nowrap; }
.f2 .ur-row { position:absolute; display:flex; justify-content:space-between; align-items:baseline; gap:20px; font:700 40px var(--f-body); white-space:nowrap;
  border-bottom:3px dotted color-mix(in srgb, var(--card-fg) 35%, transparent); padding-bottom:8px; }
.f2 .ur-row b { font-family:var(--f-num, var(--f-display)); font-weight:900; }
.f2 .ur-val { position:absolute; text-align:center; color:var(--accent); white-space:nowrap; line-height:1; }
"""


def _css(X):
    X.css("fx-f2-type", CSS)


def _pil_font(X, px, bold_cells=False):
    from PIL import ImageFont
    f = A.font_file(X, "display")
    if bold_cells:                       # a mosaic of a hairline brush face is unreadable: take the cells from a heavy sans
        from h9 import fonts as FO
        g = FO.find((FO.REG.get("noto-sans-sc") or {}).get("file", "NotoSansSC-VF.ttf"))
        if g:
            f = g
    font = ImageFont.truetype(str(f), int(px))
    try:
        axes = font.get_variation_axes()
        vals = []
        for ax in axes:
            nm = ax.get("name", b"")
            nm = nm.decode() if isinstance(nm, bytes) else str(nm)
            if "eight" in nm or nm.lower().startswith("wght"):
                vals.append(min(900, ax.get("maximum", 900)))
            else:
                vals.append(ax.get("default", ax.get("minimum", 0)))
        if vals:
            font.set_variation_by_axes(vals)
    except Exception:
        pass
    return font


def _raster(X, lines, px, lh, W, H, top, bold_cells=False):
    """the headline lines drawn white on black, centred on W, first line top at `top` → PIL L image."""
    from PIL import Image, ImageDraw
    im = Image.new("L", (int(W), int(H)), 0)
    dr = ImageDraw.Draw(im)
    font = _pil_font(X, px, bold_cells)
    for i, ln in enumerate(lines):
        base = top + px * 0.88 + i * px * lh
        dr.text((W / 2, base), A.strip(ln), font=font, fill=255, anchor="ms")
    return im


# ------------------------------------------------------------------------------------------------ word_mosaic
def word_mosaic(X, cid, t, d, p):
    """字海成形 Word Mosaic: hundreds of small glyphs related to the word drift over the whole frame as noise, then fly into
    the cells of the headline's real letter shapes (rasterised from the style's font) and assemble it, left to right;
    the leftover glyphs stay as a faint field to the bottom edge."""
    F = "word_mosaic"
    text = str(p.get("text") or "")
    A.need(F, t, p, [] if text else ["text (the headline to assemble)"])
    text = text or "示例"
    glyphs = [g for g in A.strip(p.get("glyphs") or text) if g.strip() and g != "|"]
    if not glyphs:
        glyphs = ["·"]
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"], align="center")
    top = G["y0"] + hh + 20
    box_h = G["y1"] - top - 20
    px, lines = A.fit_px(A.strip(text), G["w"], box_h, 420 if P else 380, 80, max_lines=3 if P else 2, lh=1.02)
    block_h = px * 1.02 * len(lines)
    ty0 = top + (box_h - block_h) / 2
    from PIL import ImageFilter
    disp = (X.S.get("fonts") or {}).get("display") or ""
    disp = disp[0] if isinstance(disp, list) else disp
    thin = str(disp).startswith(("ma-shan", "long-cang", "zhi-mang", "liu-jian", "lxgw", "zcool-xiaowei", "noto-serif"))
    im = _raster(X, lines, px, 1.02, W, H, ty0, bold_cells=thin)
    grow = int(px / 80) * 2 + 1                    # a little dilation so cells cover the strokes fully
    if grow >= 3:
        im = im.filter(ImageFilter.MaxFilter(grow))
    targets = []
    cell = max(14, int(px / 14))
    for _ in range(8):
        targets = []
        small = im.resize((max(1, W // cell), max(1, H // cell)), 2)
        sw, sh = small.size
        dat = small.load()
        for yy in range(sh):
            for xx in range(sw):
                if dat[xx, yy] > 110:
                    targets.append((xx * cell + cell / 2, yy * cell + cell / 2))
        if len(targets) > 1400:
            cell += 2
        elif len(targets) < 420 and cell > 14:
            cell -= 2
        else:
            break
    R = X.rand
    html = [head]
    # a faint solid copy of the word under the tiles (15 %), so the letterforms read even where cells are coarse
    ul = ""
    for i, ln in enumerate(lines):
        ul += f'<div class="wm-ul" style="top:{ty0 + i * px * 1.02:.0f}px; font-size:{px:.0f}px; height:{px * 1.02:.0f}px">{X.rich(A.strip(ln))}</div>'
    html.append(f'<div class="wm-under" style="font-family:{"var(--f-body)" if thin else "var(--f-display)"}">{ul}</div>')
    data = []
    ts_ = cell - 2
    for i, (tx, ty) in enumerate(targets):
        g = glyphs[i % len(glyphs)]
        html.append(f'<i class="wm-g g{i}" style="width:{ts_:.0f}px; height:{ts_:.0f}px; margin:{-ts_ / 2:.0f}px 0 0 {-ts_ / 2:.0f}px; font-size:{ts_ * 0.66:.0f}px">{X.rich(g)}</i>')
        sx = R.uniform(0, W)
        sy = R.uniform(G["y0"], H)
        delay = (tx - G["x0"]) / max(1, G["w"]) * 0.45 + R.uniform(0, 0.15)
        data.append([round(sx), round(sy), round(tx), round(ty), round(R.uniform(-120, 120)), round(delay, 3)])
    n_amb = 240 if P else 180
    for j in range(n_amb):
        g = glyphs[(j * 7) % len(glyphs)]
        sz = R.uniform(cell * 0.7, cell * 1.3)
        ax_, ay_ = R.uniform(0, W), R.uniform(G["y0"] - 40, H)
        html.append(f'<i class="wm-a a{j}" style="left:{ax_:.0f}px; top:{ay_:.0f}px; font-size:{sz:.0f}px; rotate:{R.uniform(-30, 30):.0f}deg">{X.rich(g)}</i>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    ta = K.U.when(X, p.get("at"), t, None)
    if ta is None:
        hit = X.spoken_at(A.strip(text), t, t + d) if getattr(X, "chars", None) else None
        ta = (hit - 0.6) if hit is not None else t + min(0.45, d * 0.1)
    ta = max(t + 0.15, min(ta, t + d - 2.1))
    X.tw(f'(()=>{{const S="{s}", D={A.js(data)}; D.forEach((g,i)=>{{const e=S+" .g"+i;'
         f'tl.set(e,{{x:g[0],y:g[1],rotation:g[4],opacity:.2,scale:.55}},{t:.3f});'
         f'tl.to(e,{{x:g[2],y:g[3],rotation:0,opacity:1,scale:1,duration:.7,ease:"expo.out"}},{ta:.3f}+g[5]);}});}})();')
    X.tw(f'tl.fromTo("{s} .wm-a", {{y:0}}, {{y:-60, duration:{d:.2f}, ease:"none", immediateRender:false}}, {t:.3f});')
    crisp = ta + 1.32                  # every tile has landed: the word holds, crisp, from here
    X.tw(f'tl.fromTo("{s} .wm-under", {{opacity:0}}, {{opacity:0.15, duration:0.35, immediateRender:true}}, {crisp - 0.35:.3f});')
    A.hold_push(X, f"{s} .f2-body", crisp + 0.6, t + d, 1.035)
    X.sfx(ta, "whoosh_soft")
    X.sfx(crisp, "pop")


# ------------------------------------------------------------------------------------------------ type_mask
def _focal(im):
    """the point deepest inside the letters (iterated erosion), nearest the centre → (x, y, depth px)."""
    from PIL import ImageFilter
    k = 4
    small = im.resize((im.width // k, im.height // k))
    cur = small.point(lambda v: 255 if v > 128 else 0)
    depth = 0
    last = cur
    while True:
        nxt = cur.filter(ImageFilter.MinFilter(3))
        if nxt.getbbox() is None:
            break
        last = nxt
        cur = nxt
        depth += 1
        if depth > 60:
            break
    dat = last.load()
    cx, cy = small.width / 2, small.height / 2
    best = None
    for y in range(small.height):
        for x in range(small.width):
            if dat[x, y] > 0:
                dd = (x - cx) ** 2 + (y - cy) ** 2
                if best is None or dd < best[0]:
                    best = (dd, x, y)
    if best is None:
        return im.width / 2, im.height / 2, 10
    return best[1] * k + k / 2, best[2] * k + k / 2, max(6, depth * k)


def type_mask(X, cid, t, d, p):
    """字形窗口 Type Mask: the headline, huge, is a window cut in the page — the beat's photo or footage plays through the
    letters. Then the camera dives into a stroke (the point deepest inside the letters, found from the real glyph
    shapes) and the window opens to the full frame."""
    F = "type_mask"
    text = str(p.get("text") or "")
    src = K.src_of(p)
    miss = []
    if not text:
        miss.append("text (the headline that becomes the window)")
    if not src:
        miss.append("image / video (what is seen through the letters)")
    A.need(F, t, p, miss)
    text = text or "示例"
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    top = G["y0"] + 40
    box_h = (H - 140 - top) if P else (G["y1"] - top)
    px, lines = A.fit_px(A.strip(text), G["w"] + (40 if P else 0), box_h, 480 if P else 400, 90, max_lines=3 if P else 2, lh=1.0)
    block_h = px * 1.0 * len(lines)
    ty0 = top + (box_h - block_h) / 2
    im = _raster(X, lines, px, 1.0, W, H, ty0)
    fx_, fy_, depth = _focal(im)
    k = K.skin(X)
    media = K.subject(X, p, 0, 0, W, H, t, d, k, cls="tm-media", full=True) if src else ""
    texts = ""
    outl = ""
    for i, ln in enumerate(lines):
        base = ty0 + px * 0.88 + i * px
        texts += f'<text x="{W / 2:.0f}" y="{base:.0f}" text-anchor="middle" style="font-family:var(--f-display); font-weight:900; font-size:{px:.0f}px">{X.rich(A.strip(ln))}</text>'
    outl = texts.replace("<text ", '<text fill="none" stroke="var(--fg)" stroke-width="4" ')
    texts = texts.replace("<text ", '<text fill="black" ')
    kick = str(p.get("kicker") or "")
    kh = f'<div class="tm-k" style="left:{G["x0"]:.0f}px; top:{G["y0"] - 4:.0f}px">{X.rich(kick)}</div>' if kick else ""
    svg = (f'<svg class="tm-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><mask id="TM_{cid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
           f'<rect x="-10" y="-10" width="{W + 20}" height="{H + 20}" fill="white"/><g class="tm-g">{texts}</g></mask></defs>'
           f'<rect x="-10" y="-10" width="{W + 20}" height="{H + 20}" fill="var(--bg)" mask="url(#TM_{cid})"/><g class="tm-g tm-o">{outl}</g></svg>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'{media}{svg}{kh}')
    te = K.U.when(X, p.get("at"), t, t + d * 0.55)
    te = max(t + 1.2, min(te, t + d - 1.1))
    scale = max(W, H) * 1.6 / depth
    X.tw(f'tl.fromTo("{s} .tm-g", {{scale:0.94, svgOrigin:"{fx_:.0f} {fy_:.0f}"}}, {{scale:1, duration:0.8, ease:"expo.out", immediateRender:true}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .tm-media", {{scale:1.14}}, {{scale:1.0, duration:{te - t + 0.6:.2f}, ease:"power1.out", immediateRender:true}}, {t:.3f});')
    X.tw(f'tl.to("{s} .tm-g", {{scale:{scale:.1f}, svgOrigin:"{fx_:.0f} {fy_:.0f}", duration:0.95, ease:"power3.in"}}, {te:.3f});')
    X.tw(f'tl.to("{s} .tm-o", {{opacity:0, duration:0.3}}, {te + 0.4:.3f});')
    X.tw(f'tl.to("{s} .tm-svg", {{opacity:0, duration:0.15}}, {te + 0.9:.3f});')
    X.sfx(te + 0.1, "whoosh_deep")


# ------------------------------------------------------------------------------------------------ weight_breath
def weight_breath(X, cid, t, d, p):
    """字重呼吸 Weight Breath: the headline is set thin and grey; as the narration says each syllable, that glyph inhales —
    weight swells to black and width stretches, then settles to bold — while a syllable meter along the bottom pulses
    in step. Uses the style's variable-weight font when it has one; otherwise thickens the strokes."""
    F = "weight_breath"
    text = str(p.get("text") or "")
    A.need(F, t, p, [] if text else ["text (the headline to breathe)"])
    text = text or "示例"
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    top = G["y0"] + hh + 20
    box_h = G["y1"] - top - 20
    px, lines = A.fit_px(A.strip(text), G["w"] - 30, box_h, 230 if P else 200, 60, max_lines=3, lh=1.12)
    vf = A.variable_weight(X)
    block_h = px * 1.12 * len(lines)
    y = top + (box_h - block_h) / 2
    html = [head]
    units = []
    k = 0
    for ln in lines:
        us = A.chars_of(ln)
        body = ""
        for u in us:
            body += f'<i class="u{k}">{X.rich(u)}</i>'
            units.append(u)
            k += 1
        html.append(f'<div class="wb-l" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:{y:.0f}px; font-size:{px:.0f}px">{body}</div>')
        y += px * 1.12
    n = len(units)
    # syllable meter along the bottom edge
    mb = H - (80 if P else 46)
    mh = (330 if P else 150)
    bw = min(46.0, (G["w"] - (n - 1) * 12) / max(n, 1))
    step = (G["w"] - bw) / max(1, n - 1)
    for i in range(n):
        html.append(f'<i class="wb-bar m{i}" style="left:{G["x0"] + i * step:.0f}px; top:{mb - mh:.0f}px; width:{bw:.0f}px; height:{mh}px"></i>')
    html.append(f'<i class="wb-base" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:{mb + 4:.0f}px"></i>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    times = A.spoken_units_times(X, text, t, d)
    if times is None or len(times) != n:
        rate = A.number(F, p, "rate", 4.4, 1.5, 9.0)
        start = K.U.when(X, p.get("at"), t, t + min(0.45, d * 0.12))
        span = (n - 1) / rate
        if start + span > t + d - 0.9:
            span = max(0.3, t + d - 0.9 - start)
        times = [start + span * i / max(1, n - 1) for i in range(n)]
    C = A.pal(X, p)
    if vf:
        X.tw(f'tl.set("{s} .wb-l i", {{fontWeight:200, color:"{C['muted']}"}}, {t:.3f});')
    else:
        X.tw(f'tl.set("{s} .wb-l i", {{"--sw":"0px", opacity:0.45, color:"{C['muted']}"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .wb-bar", {{scaleY:0.08}}, {t:.3f});')
    sw_hi = px * 0.07
    sw_mid = px * 0.035
    for i, at in enumerate(times):
        e = f"{s} .u{i}"
        if vf:
            X.tw(f'tl.to("{e}", {{fontWeight:900, scaleX:1.14, color:"{C['accent']}", duration:0.13, ease:"power2.out"}}, {at:.3f});')
            X.tw(f'tl.to("{e}", {{fontWeight:700, scaleX:1, color:"{C['fg']}", duration:0.55, ease:"power2.inOut"}}, {at + 0.13:.3f});')
        else:
            X.tw(f'tl.to("{e}", {{"--sw":"{sw_hi:.1f}px", opacity:1, scaleX:1.14, color:"{C['accent']}", duration:0.13, ease:"power2.out"}}, {at:.3f});')
            X.tw(f'tl.to("{e}", {{"--sw":"{sw_mid:.1f}px", scaleX:1, color:"{C['fg']}", duration:0.55, ease:"power2.inOut"}}, {at + 0.13:.3f});')
        X.tw(f'tl.to("{s} .m{i}", {{scaleY:1, duration:0.12, ease:"power2.out"}}, {at:.3f});')
        X.tw(f'tl.to("{s} .m{i}", {{scaleY:0.34, duration:0.6, ease:"power2.inOut"}}, {at + 0.12:.3f});')
    A.hold_push(X, f"{s} .f2-body", times[0], t + d, 1.05, "30% 40%")
    # after the line is said it keeps breathing (slow, small) so the held frame is never frozen
    tb = times[-1] + 0.75
    if tb < t + d - 0.8:
        reps = max(0, int((t + d - tb) / 1.1) - 1)
        if vf:
            X.tw(f'tl.to("{s} .wb-l i", {{fontWeight:820, duration:0.55, ease:"sine.inOut", yoyo:true, repeat:{reps}, stagger:{{each:0.06, from:"start"}}}}, {tb:.3f});')
        else:
            X.tw(f'tl.to("{s} .wb-l i", {{"--sw":"{sw_hi * 0.8:.1f}px", duration:0.55, ease:"sine.inOut", yoyo:true, repeat:{reps}, stagger:{{each:0.06, from:"start"}}}}, {tb:.3f});')
        X.tw(f'tl.to("{s} .wb-bar", {{scaleY:0.6, duration:0.55, ease:"sine.inOut", yoyo:true, repeat:{reps}, stagger:{{each:0.06, from:"start"}}}}, {tb:.3f});')
    X.sfx(times[0], "whoosh_soft", 0.4)


# ------------------------------------------------------------------------------------------------ unroll
def unroll(X, cid, t, d, p):
    """卷轴展开 Unroll: a scroll hangs from a rod; its weighted roll drops and turns, paying out paper that runs to the bottom
    edge, and the headline, the rows and the total are printed on it in the order they are said — the roll reaches
    each line as the narration does."""
    F = "unroll"
    text = str(p.get("text") or "")
    rows = A.texts(F, p, "rows", 0, 6)
    val = p.get("value")
    A.need(F, t, p, [] if (text or val not in (None, "")) else ["text and/or value (what is printed on the strip)"])
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    sw_ = 780.0 if P else 720.0
    sx = (W - sw_) / 2
    rod_y = G["y0"] - (10 if P else 30)
    rod_h = 46
    py0 = rod_y + rod_h / 2
    inner_w = sw_ - 90
    cur = py0 + 50
    html = []
    marks = []
    if text:
        hpx, hl = A.fit_px(text, inner_w, 260, 104 if P else 80, 40, max_lines=2, lh=1.1)
        html.append(f'<div class="ur-hd ur-m{len(marks)}" style="left:45px; width:{inner_w:.0f}px; top:{cur - py0:.0f}px; font-size:{hpx:.0f}px">{A.lines_html(X, hl)}</div>')
        cur += hpx * 1.1 * len(hl) + 30
        marks.append(("text", cur, text))
    rpx = 40 if P else 30
    for r in rows:
        v = r.get("value", "")
        X.used_text.update(str(v))
        html.append(f'<div class="ur-row ur-m{len(marks)}" style="left:45px; width:{inner_w:.0f}px; top:{cur - py0:.0f}px; font-size:{rpx}px"><span>{X.rich(r["text"])}</span><b>{X.rich(str(v))}</b></div>')
        cur += rpx * 1.75
        marks.append(("row", cur, r["text"]))
    if val not in (None, ""):
        vs = str(val)
        unit = str(p.get("unit") or "")
        X.used_text.update(vs + unit)
        upx = 46 if P else 36
        limit = (G["y1"] - cur - 30 - upx * 1.3) if P else (G["y1"] - cur - 10 - upx * 1.3)
        vpx, _ = A.fit_px(vs, inner_w * 0.92, max(80, limit), 300 if P else 220, 60, max_lines=1, lh=1.0)
        cur += 16
        html.append(f'<div class="ur-val ur-m{len(marks)}" style="left:45px; width:{inner_w:.0f}px; top:{cur - py0:.0f}px"><span class="f2-num" style="display:block; font-size:{vpx:.0f}px">{X.rich(vs)}</span>'
                    f'<span style="display:block; font:900 {upx}px var(--f-display); margin-top:10px">{X.rich(unit)}</span></div>')
        cur += vpx * 1.0 + upx * 1.3 + 10
        marks.append(("val", cur, vs))
    end_y = H + 10
    paper_h = end_y - py0
    roll_d0, roll_d1 = 130.0, 56.0
    inner = (f'<div class="ur-paper" style="left:{sx:.0f}px; top:{py0:.0f}px; width:{sw_:.0f}px; height:{paper_h:.0f}px">{"".join(html)}</div>'
             f'<div class="ur-rod" style="left:{sx - 40:.0f}px; top:{rod_y:.0f}px; width:{sw_ + 80:.0f}px; height:{rod_h}px"></div>'
             f'<div class="ur-roll" style="left:{sx - 16:.0f}px; top:0px; width:{sw_ + 32:.0f}px; height:{roll_d0:.0f}px"><i></i></div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, inner)
    cs = A.cues(X, p, [{"text": A.strip(m[2])} for m in marks] or [{"text": ""}], t, d, start=0.2, end=0.72, gap=0.3)
    # the weighted roll drops and pays the paper out to the bottom edge by half the beat; each line is printed on
    # the paper when the narration says it (never before the paper under it has arrived)
    a0 = t + 0.2
    dur = max(0.9, d * 0.5 - 0.2)
    X.tw(f'(()=>{{const R=document.querySelector("{s}"); if(!R) return; const pa=R.querySelector(".ur-paper"), ro=R.querySelector(".ur-roll"), st=R.querySelector(".ur-roll i");'
         f'const py0={py0:.1f}, end={end_y:.1f}, d0={roll_d0}, d1={roll_d1}; const V={{y:py0}};'
         f'const draw=()=>{{const f=Math.max(0,Math.min(1,(V.y-py0)/(end-py0))), dia=d0+(d1-d0)*f; pa.style.clipPath="inset(0 0 "+Math.max(0,end-V.y).toFixed(1)+"px 0)";'
         f'ro.style.top=(V.y-dia/2).toFixed(1)+"px"; ro.style.height=dia.toFixed(1)+"px"; st.style.backgroundPosition="0 "+(-(V.y-py0)*0.9).toFixed(1)+"px";}};'
         f'draw();'
         f'tl.fromTo(V,{{y:{py0 + 10:.1f}}},{{y:{end_y:.1f},duration:{dur:.3f},ease:"power2.in",immediateRender:false,onUpdate:draw}},{a0:.3f});'
         + '})();')
    for k, (m, c) in enumerate(zip(marks, cs)):
        frac = max(0.0, min(1.0, (m[1] - py0) / max(1.0, end_y - py0)))
        arrive = a0 + dur * math.sqrt(frac)
        at = max(c, arrive + 0.05)
        X.tw(f'tl.fromTo("{s} .ur-m{k}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.32, ease:"power2.out", immediateRender:true}}, {at:.3f});')
        if m[0] == "val":
            X.tw(f'tl.fromTo("{s} .ur-val", {{scale:1}}, {{keyframes:[{{scale:1.08, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {at + 0.3:.3f});')
        X.sfx(at, "type", 0.4)
    A.hold_push(X, s + " .ur-paper", a0 + dur, t + d, 1.02, "50% 30%")
    X.tw(f'tl.fromTo("{s} .ur-rod", {{scaleX:0.6, opacity:0}}, {{scaleX:1, opacity:1, duration:0.35, ease:"back.out(2)", immediateRender:true}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .ur-roll", {{opacity:0}}, {{opacity:1, duration:0.2, immediateRender:true}}, {t + 0.05:.3f});')
    X.sfx(t + 0.25, "paper")
    X.sfx(a0 + dur - 0.1, "tape", 0.5)


FX = {"word_mosaic": word_mosaic, "type_mask": type_mask, "weight_breath": weight_breath, "unroll": unroll}
