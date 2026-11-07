"""作品拼数字 Mosaic number (the "a big number made of the work" shot): a wall of real thumbnails fills the frame, close up,
while a counter climbs; the camera pulls back until the wall is hundreds of tiny tiles, then every tile outside the
glyphs of the final number goes dark and the tiles inside stay lit, the number's outline draws on in the accent colour
and a sub-caption lands under it — the number is literally made of the work.

Adapts: any number of pictures (1–400 distinct, stills and clips mixed; recycled to fill ~1,000–2,600 tiles, never the
same picture beside itself), a folder instead of a list, any number string ("174", "2.6万", "300"); the numeral face,
colours, corners and outline weight come from the style; 9:16 sizes tiles so each glyph stroke is several tiles wide.
p: items | images | folder · value (what the counter reaches; default from text) · text (the number as drawn, e.g.
   "174") · sub · from (counter start, default 0) · tiles (max tiles) · tile_ar (default 0.8) · zoom (start
   close-up, default 3.2) · subject · subject_label · mock
"""
import importlib.util
import math
import pathlib
import random
import sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _load("_metaphor")
MD = M.MD

CSS = """
.fx .mn .mn-cam { position:absolute; left:0; top:0; transform-origin:50% 50%; }
.fx .mn .mn-t { position:absolute; border-radius:var(--mt-tr); background-repeat:no-repeat; background-color:color-mix(in srgb, var(--fg) 12%, var(--bg)); }
.fx .mn .mn-dim { position:absolute; inset:0; background:var(--bg); opacity:0; }
.fx .mn .mn-ol { position:absolute; left:0; top:0; overflow:visible; }
.fx .mn .mn-ol path { fill:none; stroke:var(--accent); stroke-linejoin:round; stroke-linecap:round; }
.fx .mn .mn-ol path.gl { stroke:var(--card); }
.fx .mn .mn-ctr { position:absolute; transform:translate(-50%, -50%); color:var(--bg); background:var(--fg); border-radius:var(--mt-r);
  padding:.06em .32em .1em; box-shadow:var(--mt-shadow); }
.fx .mn .mn-ctr .mt-k { display:block; }
.fx .mn .mn-sub { position:absolute; text-align:center; font-family:var(--f-body); font-weight:700; color:var(--fg); line-height:1.3; }
.fx .mn .mn-sub .fl { display:block; white-space:nowrap; }
.fx .mn .mn-sub i.bar { display:block; margin:0 auto 14px; width:64px; height:var(--mt-sw); background:var(--accent); }
"""


def mosaic_number(X, cid, t, d, p):
    M.base(X)
    X.css("fx-mn", CSS)
    sk = M.skin(X)
    its = M.pool(X, p, cap=int(p.get("distinct", 300)))
    if not its:
        raise SystemExit(f"mosaic_number at {t:.2f}s: give `items`, `images` or `folder` (the work the number is made of)")
    text = str(p.get("text") or p.get("value") or len(its))
    target, pre, suf, dec = M.split_num(p.get("value", text))
    has_sub = bool(p.get("subject"))
    R = M.regions(X, p, has_sub, graphic_share=0.62, hero_ar=1.5, row="center")
    gx0, gy0, gx1, gy1 = R["g"]
    W = X.W
    H = X.H
    P = X.portrait
    # 1 · the number, set in the style's numeral face, as large as the graphic box allows (room for the sub below)
    sub = p.get("sub", "")
    sub_room = 0
    if sub:
        sub_room = 120 if P else 110
    nb_w = (gx1 - gx0) * (0.98 if P else 0.92)
    nb_h = (gy1 - gy0 - sub_room) * (0.85 if P else 0.72)
    ncx = (gx0 + gx1) / 2
    ncy = gy0 + (gy1 - gy0 - sub_room) / 2
    G = M.glyph_layout(X, text, nb_w, nb_h, ncx, ncy)
    fs = G["fs"]
    bx0, by0, bx1, by1 = G["bbox"]
    # 2 · the tile grid over the whole frame: strokes several tiles wide, capped for render time
    ar = float(p.get("tile_ar", 0.8))
    cap = int(p.get("tiles", 2600 if P else 2200))
    cw = max(12.0, fs * 0.042)
    while True:
        gap = max(2.0, round(cw * 0.08))
        pitch_x = cw + gap
        pitch_y = cw / ar + gap
        cols = int(math.ceil(W / pitch_x)) + 1
        rows = int(math.ceil(H / pitch_y)) + 1
        if cols * rows <= cap:
            break
        cw = cw * 1.06
    ch = cw / ar
    ox = (W - cols * pitch_x) / 2
    oy = (H - rows * pitch_y) / 2
    cover = M.coverage(G["contours"], ox, oy, pitch_x, pitch_y, cols, rows, W, H)
    # 3 · pictures: one atlas, each tile a background-position into it
    tw = 96
    th = int(round(tw / ar))
    url, acols, aw, ah = MD.atlas(X, its, tw, th)
    sx = cw / tw
    sy = ch / th
    X.css(f"fx-mn-bg-{cid}", f"#{cid} .mn-t {{ background-image:url({url}); background-size:{aw * sx:.1f}px {ah * sy:.1f}px; }}")
    rnd = random.Random(int(p.get("seed", 9)) * 7919 + 31)
    order = M.tile_order(cols * rows, len(its), cols, rnd)
    wall = []
    lit = []
    n_lit = 0
    cx = W / 2
    cy = H / 2
    maxd = math.hypot(cx, cy)
    for r in range(rows):
        for c in range(cols):
            i = r * cols + c
            k = order[i]
            ar_r, ar_c = divmod(k, acols)
            x = ox + c * pitch_x
            y = oy + r * pitch_y
            bpx = -ar_c * tw * sx
            bpy = -ar_r * th * sy
            dist = math.hypot(x + cw / 2 - cx, y + ch / 2 - cy) / maxd
            ring = min(7, int(dist * 9))
            inside = cover[r][c] >= 0.5
            grp = f"r{ring}"
            if not inside:
                grp += f" o{rnd.randrange(6)}"
            style = f"left:{x:.1f}px; top:{y:.1f}px; width:{cw:.1f}px; height:{ch:.1f}px; background-position:{bpx:.1f}px {bpy:.1f}px"
            wall.append(f'<i class="mn-t {grp}" style="{style}"></i>')
            if inside:
                lit.append(f'<i class="mn-t" style="{style}"></i>')
                n_lit += 1
    if n_lit < 20:
        print(f"  mosaic_number {t:.2f}s: only {n_lit} tiles fall inside \"{text}\" — use fewer characters or a bigger beat")
    # 4 · counter, sub-caption, outline
    ctr_steps = [(t, str(p.get("from", 0))), (t, f"{pre}{target:.{dec}f}{suf}")]
    ctr_html, sufs = M.stepper_html(X, ctr_steps)
    ctr_px = min(fs * 0.42, (gx1 - gx0) * 0.6 / max(1.0, len(text) * 0.62))
    sw = max(2.5, fs * 0.012)
    glints = ""
    for ring_d in G["d"].split("Z"):
        if not ring_d:
            continue
        # one path per contour: a dash pattern restarts on every sub-path, so a single path would glint everywhere at once
        glints += f'<path class="gl" d="{ring_d}Z" pathLength="1" stroke-dasharray="0.14 1" stroke-dashoffset="0.14" style="stroke-width:{sw * 1.5:.1f}px; opacity:0"/>'
    outline = (f'<svg class="mn-ol" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
               f'<path class="ol" d="{G["d"]}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" style="stroke-width:{sw:.1f}px"/>'
               f'{glints}</svg>')
    sub_html = ""
    if sub:
        sub_w = min(gx1 - gx0, W - 2 * 120) if P else gx1 - gx0
        s_px, s_lines, s_n = M.fit_text(X, sub, sub_w, 120, 40 if P else 36, 22, 2)
        sub_html = (f'<div class="mn-sub" style="left:{ncx - sub_w / 2:.0f}px; top:{by1 + 34:.0f}px; width:{sub_w:.0f}px; font-size:{s_px:.0f}px">'
                    f'<i class="bar"></i>{s_lines}</div>')
    cam = (f'<div class="mn-cam" style="width:{W}px; height:{H}px">'
           f'<div class="mn-wall">{"".join(wall)}</div><div class="mn-dim"></div><div class="mn-lit">{"".join(lit)}</div>{outline}</div>')
    ctr = f'<div class="mn-ctr" style="left:{ncx:.0f}px; top:{ncy:.0f}px; font-size:{ctr_px:.0f}px">{ctr_html}</div>'
    tz = t + 0.15 + min(2.4, max(1.2, d * 0.42))
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=tz + 0.45)     # the subject card lands after the reveal
    mock = M.mock_tag(X, p, gx1 - 80, gy0)
    inner = M.wrap(X, sk, cam + ctr + sub_html + mock + subj, "mn")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    z0 = float(p.get("zoom", 3.2))
    # open: tiles pop in from the centre outwards while we are close up
    X.tw(f'tl.set("{s} .mn-cam", {{scale:{z0}, x:{W * 0.04:.0f}}}, {t:.3f});')
    for ring in range(8):
        X.tw(f'tl.from("{s} .mn-wall .r{ring}", {{opacity:0, scale:0.4, duration:0.35, ease:"back.out(2)"}}, {t + 0.04 + ring * 0.07:.3f});')
    X.tw(f'tl.from("{s} .mn-ctr", {{scale:0.6, opacity:0, duration:0.45, ease:"{e}"}}, {t + 0.12:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # the pull-back, the counter climbing with it
    X.tw(f'tl.to("{s} .mn-cam", {{scale:1, x:0, duration:{tz - t - 0.15:.2f}, ease:"power2.inOut"}}, {t + 0.15:.3f});')
    sel_n = f"{s} .mn-ctr"
    js_f = f'(x)=>x.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})'
    start = M.split_num(p.get("from", 0))[0]
    X.tw(f'(()=>{{const o={{v:{start}}}, el=document.querySelector("{sel_n} .n"), f={js_f}; if(!el) return; '
         f'tl.to(o, {{v:{target}, duration:{tz - t - 0.25:.2f}, ease:"power1.inOut", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {t + 0.2:.3f});}})();')
    for k, sfx_ in enumerate(sufs):
        X.tw(f'tl.set("{sel_n} .sf[data-k=\'{k}\']", {{opacity:1}}, {tz - 0.1:.3f});')
    X.sfx(t + 0.2, "count")
    # reveal: tiles outside the glyphs go out in uneven waves, the inside stays lit, the outline draws on
    for k in range(6):
        X.tw(f'tl.to("{s} .mn-wall .o{k}", {{opacity:0.3, duration:0.18, ease:"power2.in"}}, {tz + k * 0.07:.3f});')
    X.tw(f'tl.to("{s} .mn-dim", {{opacity:0.84, duration:0.55, ease:"power2.inOut"}}, {tz + 0.1:.3f});')
    X.tw(f'tl.to("{s} .mn-ctr", {{scale:0.7, opacity:0, duration:0.3, ease:"power2.in"}}, {tz - 0.02:.3f});')
    X.tw(f'tl.fromTo("{s} .mn-lit .mn-t", {{scale:1}}, {{keyframes:[{{scale:1.3, duration:0.12}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], '
         f'stagger:{{amount:0.45, from:"start"}}, immediateRender:false}}, {tz + 0.18:.3f});')
    X.tw(f'tl.to("{s} .mn-ol path.ol", {{strokeDashoffset:0, duration:0.9, ease:"power2.inOut"}}, {tz + 0.25:.3f});')
    X.sfx(tz + 0.1, "hit")
    if sub:
        X.tw(f'tl.from("{s} .mn-sub i.bar", {{scaleX:0, duration:0.4, ease:"{e}"}}, {tz + 0.6:.3f});')
        X.tw(f'tl.from("{s} .mn-sub .fl", {{yPercent:80, opacity:0, duration:0.5, ease:"{e}", stagger:0.08}}, {tz + 0.7:.3f});')
    # hold: a glint runs round the outline, the camera keeps creeping in
    glint = tz + 1.5
    if glint < t + d - 0.4:
        X.tw(f'tl.set("{s} .mn-ol path.gl", {{opacity:1}}, {glint:.3f});')
        X.tw(f'tl.fromTo("{s} .mn-ol path.gl", {{strokeDashoffset:0.14}}, {{strokeDashoffset:-1, duration:1.1, ease:"power1.inOut", immediateRender:false}}, {glint:.3f});')
        X.tw(f'tl.set("{s} .mn-ol path.gl", {{opacity:0}}, {glint + 1.1:.3f});')
    X.tw(f'tl.to("{s} .mn-cam", {{scale:1.035, duration:{max(0.3, t + d - tz - 0.2):.2f}, ease:"none"}}, {tz + 0.2:.3f});')


FX = {"mosaic_number": mosaic_number}
