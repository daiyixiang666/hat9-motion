"""fx3 · three scene effects: glyph_sphere · wire_resolve · cube_number.

glyph_sphere   a rotating sphere of small code glyphs condenses into the hero number / word, then the solid text takes over
wire_resolve   2–5 cards drawn first as a glowing wireframe; a bright line sweeps down and resolves them into real cards
cube_number    a big figure built from accent cubes that fall onto an isometric tile board (optional `from` value first)

Every motion is a pure function of timeline time (GSAP tweens or one proxy tween whose onUpdate redraws from the time),
so any frame can be rendered on its own. Colours come only from the style tokens (--bg --fg --muted --accent --card
--card-fg --line and the --k-* skin variables), so the effects re-skin in every style; both 16:9 and 9:16 are laid out.
"""
import html as HTML
import importlib.util
import math
import pathlib
import re
import sys

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]
K = A.K

CSS = r"""
.f3 .gs-field { position:absolute; inset:0; }
.f3 .gs-g { position:absolute; left:0; top:0; font:700 28px var(--f-mono, var(--f-body)); line-height:1; color:var(--fg); white-space:nowrap; will-change:transform, opacity; }
.f3 .gs-core { position:absolute; border-radius:50%;
  background:radial-gradient(circle, color-mix(in srgb, var(--accent) 55%, #fff) 0%, var(--accent) 22%, color-mix(in srgb, var(--accent) 35%, transparent) 48%, transparent 70%); }
.f3 .gs-solid { position:absolute; left:0; right:0; text-align:center; font-weight:900; color:var(--fg); white-space:nowrap; opacity:0; }
.f3 .gs-label { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-body); font-weight:800; color:var(--muted); letter-spacing:.08em; white-space:nowrap; }
.f3 .gs-sub { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; opacity:0; }

.f3 .wr-dim { position:absolute; inset:0; background:rgba(0,0,0,.55); }
.f3 .wr-rain { position:absolute; inset:0; overflow:hidden; opacity:.12; }
.f3 .wr-col { position:absolute; top:0; width:40px; font:700 30px var(--f-mono, var(--f-body)); line-height:1.15; color:var(--accent); text-align:center; word-break:break-all; }
.f3 .wr-layer { position:absolute; inset:0; }
.f3 .wr-cards { position:absolute; inset:0; }
.f3 .wr-card { position:absolute; box-sizing:border-box; }
.f3 .wr-real .wr-card { background:var(--card); color:var(--card-fg); border-radius:var(--k-r); box-shadow:var(--k-sh);
  border:var(--k-bw) solid color-mix(in srgb, var(--card-fg) 14%, transparent); }
.f3 .wr-real .wr-card.hero { box-shadow:0 26px 60px rgba(0,0,0,.34), 0 0 0 3px var(--mark, var(--accent)); }
.f3 .wr-t { position:absolute; font-family:var(--f-body); font-weight:800; white-space:nowrap; }
.f3 .wr-v { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; white-space:nowrap; font-variant-numeric:tabular-nums; line-height:1; }
.f3 .wr-track { position:absolute; border-radius:999px; }
.f3 .wr-fill { position:absolute; left:0; top:0; bottom:0; border-radius:999px; }
.f3 .wr-real .wr-track { background:color-mix(in srgb, var(--card-fg) 12%, transparent); }
.f3 .wr-real .wr-fill { background:var(--mark, var(--accent)); }
.f3 .wr-real .wr-v { color:var(--card-fg); }
.f3 .wr-real .hero .wr-v { color:var(--mark, var(--accent)); }
.f3 .wr-wire .wr-t, .f3 .wr-wire .wr-v { color:transparent; -webkit-text-stroke:2px var(--accent); filter:drop-shadow(0 0 6px var(--accent)); }
.f3 .wr-svg { position:absolute; left:0; top:0; overflow:visible; filter:drop-shadow(0 0 8px var(--accent)); }
.f3 .wr-svg rect { fill:none; stroke:var(--accent); stroke-width:3; }
.f3 .wr-line { position:absolute; left:0; right:0; height:6px; margin-top:-3px; background:color-mix(in srgb, var(--accent) 40%, #fff);
  box-shadow:0 0 60px 18px color-mix(in srgb, var(--accent) 70%, transparent), 0 0 14px 4px var(--accent); opacity:0; }

.f3 .cn-label { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; }
.f3 .cn-sub { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-body); font-weight:700; color:var(--muted); white-space:nowrap; }
.f3 .cn-view { position:absolute; perspective:2000px; perspective-origin:50% 50%; }
.f3 .cn-board { position:absolute; left:0; top:0; transform-style:preserve-3d; transform-origin:50% 50%; }
.f3 .cn-top { position:absolute; inset:0; background-color:var(--board);
  background-image:linear-gradient(to right, var(--gap) 2px, transparent 2px), linear-gradient(to bottom, var(--gap) 2px, transparent 2px); }
.f3 .cn-edge { position:absolute; left:0; background:color-mix(in srgb, var(--board) 70%, #000); transform-origin:50% 0; }
.f3 .cn-cube { position:absolute; transform-style:preserve-3d; --z:0; --sz:1;
  transform:translateZ(calc(var(--z) * 1px)) scale3d(1, 1, var(--sz)); transform-origin:50% 50% 0; }
.f3 .cn-cube.new { opacity:0; }
.f3 .cn-cube i { position:absolute; display:block; left:0; top:0; }
.f3 .cn-cube .ft { background:var(--cube); }
.f3 .cn-cube .fr { background:color-mix(in srgb, var(--cube) 74%, #000); transform-origin:50% 0; }
.f3 .cn-cube .sh { background:radial-gradient(closest-side, rgba(0,0,0,.6), rgba(0,0,0,0)); opacity:calc(0.8 - var(--z) * 0.0013); }
.f3 .cn-unit { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1; white-space:nowrap; opacity:0; }
"""


def _css(X):
    X.css("fx-f3-scene", CSS)


def _num(s):
    """the first number in a string ("77.56 亿" → 77.56, "46,479 家" → 46479), or None."""
    m = re.search(r"-?\d[\d,]*(?:\.\d+)?", str(s))
    if not m:
        return None
    return float(m.group(0).replace(",", ""))


def _thin_display(X):
    """True when the style's display face is a hairline brush / serif one (a mosaic of it would not read)."""
    disp = (X.S.get("fonts") or {}).get("display") or ""
    if isinstance(disp, list):
        disp = disp[0] if disp else ""
    return str(disp).startswith(("ma-shan", "long-cang", "zhi-mang", "liu-jian", "lxgw", "zcool-xiaowei", "noto-serif"))


def _hex(c):
    """#rgb / #rrggbb → (r, g, b) 0–255, or None for anything else."""
    c = str(c).strip()
    if not c.startswith("#") or len(c) not in (4, 7):
        return None
    if len(c) == 4:
        c = "#" + c[1] * 2 + c[2] * 2 + c[3] * 2
    return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))


def _mix(a, b, w):
    """w of colour a over colour b, as #rrggbb (a or b unreadable → a)."""
    pa = _hex(a)
    pb = _hex(b)
    if pa is None or pb is None:
        return a
    out = "#"
    for i in range(3):
        out += f"{round(pa[i] * w + pb[i] * (1 - w)):02x}"
    return out


def _mark_on(X, p, ground_key):
    """the colour that marks the stressed thing (hero value, bar fill, cube) on the `ground_key` colour: the accent when
    it stands out there (≥ 3:1), else the page ground, else the text colour. Some styles' accent IS the card colour."""
    from h9.aefx import _contrast
    pal = A.pal(X, p)
    ground = pal.get(ground_key, "#ffffff")
    for key in ("accent", "bg", "card-fg", "fg"):
        c = pal.get(key)
        if c and _contrast(c, ground) >= 3.0:
            return c
    return pal.get("accent", "#e2321f")


# ------------------------------------------------------------------------------------------------ glyph_sphere
GLYPHS = "0123456789ABCDEF{}[]<>/=+"


def _sphere_points(n):
    """n unit vectors on a Fibonacci sphere (even spread, deterministic)."""
    golden = math.pi * (3 - math.sqrt(5))
    pts = []
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1 - y * y))
        a = i * golden
        x = math.cos(a) * r
        z = math.sin(a) * r
        pts.append((x, y, z))
    return pts


def _project(pt, ang, tilt, R, F, cx, cy):
    """a unit point turned `ang` radians about Y, tilted `tilt` about X, then perspective-projected → (x, y, depth −1..1, k)."""
    x, y, z = pt
    x1 = x * math.cos(ang) + z * math.sin(ang)
    z1 = -x * math.sin(ang) + z * math.cos(ang)
    y2 = y * math.cos(tilt) - z1 * math.sin(tilt)
    z2 = y * math.sin(tilt) + z1 * math.cos(tilt)
    k = (F + R) / (F + R - R * z2)           # the silhouette (z2 = 0) sits exactly at radius R; the near side grows
    return cx + x1 * R * k, cy + y2 * R * k, z2, k


def glyph_sphere(X, cid, t, d, p):
    """代码球成字 Glyph Sphere: a sphere of ~1,100 small code glyphs (0–9 A–F {}[]<>/=+) turns slowly around a bright core;
    at the key moment every glyph flies into the pixel shape of the hero number or word, and the solid text takes over
    so it reads cleanly. Glyphs that are not needed fly outwards and fade."""
    F_ = "glyph_sphere"
    value = str(p.get("value") or p.get("text") or "")
    A.need(F_, t, p, [] if value else ["value (the number or word the glyphs form)"])
    value = value or "0"
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    fps = X.fps
    label = str(p.get("label") or "")
    sub = str(p.get("sub") or "")

    # layout: the sphere fills the content area (9:16: diameter 860 px centred at y 760; 16:9: 70 % of the frame height,
    # centred between header and caption); the text forms where the sphere was, label above it, sub line under it
    cx = W / 2
    if P:
        R = 430.0
        cy = 760.0
    else:
        R = H * 0.35
        cy = (G["y0"] + G["y1"]) / 2
    hero_w = 900.0 if P else min(G["w"], 1300.0)
    px, lines = A.fit_px(A.strip(value), hero_w, R * 1.5, 640 if P else 520, 200, max_lines=1, lh=1.0)
    lh = 1.0
    block_h = px * lh * len(lines)
    ty0 = cy - block_h / 2
    label_html = ""
    lpx = 0
    if label:
        lpx, ll = A.fit_px(A.strip(label), G["w"], 70, 44 if P else 36, 28, max_lines=1)
        label_html = f'<div class="gs-label" style="top:{ty0 - 48 - lpx * 1.2:.0f}px; font-size:{lpx:.0f}px">{X.rich(ll[0])}</div>'

    # rasterise the text with the style's display face (a heavy sans for hairline faces) and sample it on a coarse grid
    T2 = A.load("fx2_type")
    thin = _thin_display(X)
    im = T2._raster(X, lines, px, lh, W, H, ty0, bold_cells=thin)
    N = 1200
    cell = max(10, int(px / 13))
    targets = []
    for _ in range(10):
        targets = []
        sw = max(1, W // cell)
        sh = max(1, H // cell)
        small = im.resize((sw, sh), 2)
        dat = small.load()
        for yy in range(sh):
            for xx in range(sw):
                if dat[xx, yy] > 100:
                    targets.append((xx * cell + cell / 2, yy * cell + cell / 2))
        if len(targets) > N * 0.78:
            cell += 1
        elif len(targets) < N * 0.55 and cell > 10:
            cell -= 1
        else:
            break
    if len(targets) > int(N * 0.78):
        targets = targets[:int(N * 0.78)]

    # the moment the glyphs leave the sphere
    at = K.U.when(X, p.get("at"), t, None)
    if at is None:
        at = t + d * 0.45
    if at < t + 0.6:
        at = t + 0.6
    if at > t + d - 1.6:
        at = t + d - 1.6
    fly = 0.9
    spread = 0.25

    # pair each target with the sphere glyph nearest to it in screen x at the moment of flight (no criss-crossing)
    pts = _sphere_points(N)
    ang_at = math.radians(24.0) * (at - t)
    tilt = math.radians(12.0)
    order = []
    for i in range(N):
        sx, sy, sz, sk = _project(pts[i], ang_at, tilt, R, 900.0, cx, cy)
        order.append((sx, i))
    order.sort()
    by_x = []
    for j in range(len(targets)):
        by_x.append((targets[j][0], j))
    by_x.sort()
    tgt_sorted = []
    for item in by_x:
        tgt_sorted.append(item[1])
    M = len(targets)
    # spread the M flying glyphs evenly through the x-sorted sphere list
    assign = {}
    for k in range(M):
        pos = int(k * N / M)
        sphere_i = order[pos][1]
        while sphere_i in assign:
            pos = (pos + 1) % N
            sphere_i = order[pos][1]
        assign[sphere_i] = tgt_sorted[k]

    maxd = 1.0
    for (tx, ty) in targets:
        dd = math.hypot(tx - cx, ty - cy)
        if dd > maxd:
            maxd = dd
    R_ = X.rand
    glyph_html = []
    data = []
    tsz = (cell - 1) / 28.0               # the landed glyph's scale (fills its grid cell)
    for i in range(N):
        g = GLYPHS[R_.randrange(len(GLYPHS))]
        glyph_html.append(f'<i class="gs-g">{HTML.escape(g)}</i>')
        x, y, z = pts[i]
        if i in assign:
            tx, ty = targets[assign[i]]
            delay = spread * math.hypot(tx - cx, ty - cy) / maxd
            data.append([round(x, 4), round(y, 4), round(z, 4), round(tx, 1), round(ty, 1), round(delay, 3)])
        else:
            delay = spread * R_.random()
            ring_a = R_.uniform(0, 2 * math.pi)        # its place on the ring that keeps orbiting the settled text
            data.append([round(x, 4), round(y, 4), round(z, 4), None, round(ring_a, 4), round(delay, 3)])
    X.used_text.update(GLYPHS)

    solid = ""
    font = "var(--f-body)" if thin else "var(--f-display)"
    for i, ln in enumerate(lines):
        solid += (f'<div class="gs-solid" data-anchor="value" style="top:{ty0 + i * px * lh:.0f}px; height:{px * lh:.0f}px; line-height:{lh}; '
                  f'font-size:{px:.0f}px; font-family:{font}">{X.rich(A.strip(ln))}</div>')
    sub_html = ""
    if sub:
        spx, sl = A.fit_px(A.strip(sub), G["w"], 70, 44 if P else 36, 28, max_lines=1)
        sub_html = f'<div class="gs-sub" style="top:{ty0 + block_h + 40:.0f}px; font-size:{spx:.0f}px">{X.rich(sl[0])}</div>'
    block_w = 0.0
    for (tx, ty) in targets:
        if abs(tx - cx) * 2 > block_w:
            block_w = abs(tx - cx) * 2
    ring_rx = max(block_w / 2 + 70, R * 0.95)
    ring_ry = min(block_h * 0.35, ring_rx * 0.2)        # flat enough to pass behind the text, clear of label and sub
    core_r = 180
    core = f'<div class="gs-core" style="left:{cx - core_r:.0f}px; top:{cy - core_r:.0f}px; width:{core_r * 2}px; height:{core_r * 2}px"></div>'
    inner = (label_html + core + f'<div class="gs-field" data-safe="ignore" data-layout-ignore>{"".join(glyph_html)}</div>' + solid + sub_html)
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body f3">{inner}</div>')

    # one proxy tween drives the whole field: draw() computes every glyph from the beat time alone
    X.tw(f'''(()=>{{
  const R = document.querySelector("{s}");
  if (!R) return;
  const els = [...R.querySelectorAll(".gs-g")];
  const D = {A.js(data)};
  const cx = {cx:.1f}, cy = {cy:.1f}, rad = {R:.1f}, focal = 900, tilt = {tilt:.5f};
  const speed = {math.radians(24.0):.5f}, flyAt = {at - t:.3f}, flyDur = {fly}, landScale = {tsz:.4f};
  const landed = {at - t + spread + fly:.3f}, fade = {6.0 / fps:.3f}, ringX = {ring_rx:.1f}, ringY = {ring_ry:.1f};
  function expoInOut(u) {{
    if (u <= 0) return 0;
    if (u >= 1) return 1;
    if (u < 0.5) return Math.pow(2, 20 * u - 10) / 2;
    return (2 - Math.pow(2, -20 * u + 10)) / 2;
  }}
  function draw(time) {{
    const ang = speed * time;
    const ca = Math.cos(ang), sa = Math.sin(ang), ct = Math.cos(tilt), st = Math.sin(tilt);
    for (let i = 0; i < els.length; i++) {{
      const g = D[i];
      const x1 = g[0] * ca + g[2] * sa;
      const z1 = -g[0] * sa + g[2] * ca;
      const y2 = g[1] * ct - z1 * st;
      const z2 = g[1] * st + z1 * ct;
      const k = (focal + rad) / (focal + rad - rad * z2);
      const sx = cx + x1 * rad * k;
      const sy = cy + y2 * rad * k;
      const depth = (z2 + 1) / 2;
      let size = (18 + 16 * depth) / 28;
      let op = 0.25 + 0.75 * depth;
      if (z2 < 0) op = op * 0.6;
      let u = (time - flyAt - g[5]) / flyDur;
      u = expoInOut(u);
      let x = sx, y = sy;
      if (g[3] !== null) {{
        // a glyph of the text: flies to its cell, then dims once the solid text is in
        x = sx + (g[3] - sx) * u;
        y = sy + (g[4] - sy) * u;
        size = size + (landScale - size) * u;
        op = op + (1 - op) * u;
        let after = (time - landed) / fade;
        if (after > 0) {{
          if (after > 1) after = 1;
          op = op * (1 - 0.84 * after);
        }}
      }} else {{
        // a ring glyph: settles on a tilted ring around the text and keeps orbiting, faintly
        const ra = g[4] + speed * 0.5 * time;
        const rz = Math.sin(ra);
        const rx = cx + Math.cos(ra) * ringX;
        const ry = cy + rz * ringY;
        const ringOp = rz > 0 ? 0.42 : 0.16;
        x = sx + (rx - sx) * u;
        y = sy + (ry - sy) * u;
        size = size + (0.75 + 0.25 * rz - size) * u;
        op = op + (ringOp - op) * u;
      }}
      els[i].style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px) translate(-50%,-50%) scale(" + size.toFixed(3) + ")";
      els[i].style.opacity = op.toFixed(3);
    }}
  }}
  const V = {{ t: 0 }};
  draw(0);
  tl.fromTo(V, {{ t: 0 }}, {{ t: {d:.3f}, duration: {d:.3f}, ease: "none", immediateRender: false, onUpdate: () => draw(V.t) }}, {t:.3f});
}})();''')
    landed = at + spread + fly
    frame6 = 6.0 / fps
    X.tw(f'tl.fromTo("{s} .gs-core", {{opacity:0, scale:0.6}}, {{opacity:0.9, scale:1, duration:0.5, ease:"power2.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.to("{s} .gs-core", {{opacity:0.22, scale:1.5, duration:{fly:.2f}, ease:"power2.inOut"}}, {at:.3f});')
    X.tw(f'tl.fromTo("{s} .gs-solid", {{opacity:0}}, {{opacity:1, duration:{frame6:.3f}, ease:"none", immediateRender:true}}, {landed:.3f});')
    if label:
        # the label would sit on the glyphs while the sphere turns: it arrives with the text
        X.tw(f'tl.fromTo("{s} .gs-label", {{opacity:0, y:-24}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out", immediateRender:true}}, {at + spread + fly * 0.6:.3f});')
    if sub:
        X.tw(f'tl.fromTo("{s} .gs-sub", {{opacity:0, y:14}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out", immediateRender:true}}, {landed + 0.1:.3f});')
    A.hold_push(X, f"{s} .f3", landed + 0.3, t + d, 1.03, origin=f"50% {cy:.0f}px")
    X.sfx(at, "whoosh_soft")
    X.sfx(landed, "pop")


# ------------------------------------------------------------------------------------------------ wire_resolve
def wire_resolve(X, cid, t, d, p):
    """线框成形 Wire Resolve: the cards appear first as a glowing wireframe on a dimmed ground — outlines and bars draw on
    in reading order over a faint rain of code glyphs; then a bright line sweeps down the frame and everything above it
    is the finished card, everything below still wire. The leading card lifts at the end."""
    F_ = "wire_resolve"
    items = A.texts(F_, p, "items", 2, 5, text_keys=("title", "text", "label", "name"))
    miss = []
    if len(items) < 2:
        miss.append("items (2–5 cards, each {title, value})")
    A.need(F_, t, p, miss)
    if len(items) < 2:
        items = [{"text": "A", "value": 1}, {"text": "B", "value": 2}]
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    n = len(items)

    vals = []
    for it in items:
        v = _num(it.get("value"))
        if v is None:
            v = 0.0
        vals.append(v)
    vmax = max(vals) if max(vals) > 0 else 1.0
    hero_i = None
    for i, it in enumerate(items):
        if it.get("hero") is True:
            hero_i = i
    if hero_i is None:
        hero_i = vals.index(max(vals))

    head, hh = "", 0
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"], align="left")
    x0 = G["x0"]
    x1 = G["x1"]
    if P and x1 > W - 120:
        x1 = W - 120                         # 9:16: clear of the platform buttons on the lower right
    gap = 28 if P else 32
    rects = []
    if P:
        # 9:16: the cards fill y 300–1260 (under the title when there is one)
        y0 = max(300.0, G["y0"] + hh + 10)
        y1 = min(1260.0, G["y1"])
        ch = (y1 - y0) / n - gap
        if ch < 190:
            ch = 190.0
        if ch > 320:
            ch = 320.0
        if ch * n + gap * (n - 1) > y1 - y0 + 40:          # five cards: shrink below the minimum rather than run into the caption
            ch = (y1 - y0 + 40 - gap * (n - 1)) / n
        total = ch * n + gap * (n - 1)
        top = y0 + (y1 - y0 - total) / 2
        for i in range(n):
            rects.append((x0, top + i * (ch + gap), x1 - x0, ch))
    else:
        # 16:9: one row of up to 3 cards, else two rows, filling the width and the height between header and caption
        y0 = G["y0"] + hh + 16
        y1 = G["y1"] - 10
        rows = 1 if n <= 3 else 2
        per_row = [n] if rows == 1 else [(n + 1) // 2, n // 2]
        ch = (y1 - y0 - gap * (rows - 1)) / rows
        if ch > 460:
            ch = 460.0
        top = y0 + (y1 - y0 - ch * rows - gap * (rows - 1)) / 2
        for r in range(rows):
            k = per_row[r]
            cw = (x1 - x0 - gap * (k - 1)) / k
            for c in range(k):
                rects.append((x0 + c * (cw + gap), top + r * (ch + gap), cw, ch))

    def card_parts(i, rx, ry, rw, rh):
        """inner geometry of one card (relative to the card) → dict of boxes and font sizes. Tall cards: title, then
        the big value under it, bar at the bottom; short cards: title and value on one row."""
        pad = 32 if P else 28
        tpx = 40 if P else 32
        bar_h = 18 if P else 20
        stacked = rh >= pad * 2 + tpx * 1.3 + 104 * 1.05 + bar_h + 16
        if stacked:
            vpx = 104.0
            if not P and vpx > rw * 0.22:
                vpx = rw * 0.22
            return {"pad": pad, "tpx": tpx, "vpx": vpx, "tx": pad, "ty": pad, "vx": pad, "vy": pad + tpx * 1.3 + 6,
                    "bx": pad, "by": rh - pad - bar_h, "bw": rw - 2 * pad, "bh": bar_h, "v_right": False}
        vpx = min(104.0, rh - pad * 2 - bar_h - 20)
        return {"pad": pad, "tpx": tpx, "vpx": vpx, "tx": pad, "ty": pad, "vx": pad, "vy": pad,
                "bx": pad, "by": rh - pad - bar_h, "bw": rw - 2 * pad, "bh": bar_h, "v_right": True}

    # arriving by an anchor_match cut, the hero card is the persistent element: it is finished from the first frame
    keep = p.get("tr") == "anchor_match"

    def layer(kind, only=None, skip=None):
        out = ""
        for i, it in enumerate(items):
            if only is not None and i != only:
                continue
            if skip is not None and i == skip:
                continue
            rx, ry, rw, rh = rects[i]
            q = card_parts(i, rx, ry, rw, rh)
            title_fit = A.fit_px(A.strip(it["text"]), rw - 2 * q["pad"], q["tpx"] * 1.3, q["tpx"], 28 if P else 22, max_lines=1)
            vtxt = str(it.get("value", ""))
            vfit = A.fit_px(vtxt, rw - 2 * q["pad"], q["vpx"] * 1.2, q["vpx"], 34, max_lines=1, lh=1.0)
            fill_w = q["bw"] * max(0.0, vals[i]) / vmax
            hero = " hero" if i == hero_i else ""
            anchor = ' data-anchor="value"' if (i == hero_i and kind == "real" and (only is not None or not keep)) else ""
            vpos = f"right:{q['pad']}px; top:{q['ty'] - 4:.0f}px" if q["v_right"] else f"left:{q['vx']}px; top:{q['vy']:.0f}px"
            if q["v_right"]:
                title_pos = f"left:{q['tx']}px; top:{q['ty'] + 6:.0f}px; max-width:{rw * 0.5:.0f}px"
            else:
                title_pos = f"left:{q['tx']}px; top:{q['ty']:.0f}px"
            out += (f'<div class="wr-card c{i}{hero}" style="left:{rx:.0f}px; top:{ry:.0f}px; width:{rw:.0f}px; height:{rh:.0f}px">'
                    f'<div class="wr-t" style="{title_pos}; font-size:{title_fit[0]:.0f}px">{X.rich(title_fit[1][0])}</div>'
                    f'<div class="wr-v"{anchor} style="{vpos}; font-size:{vfit[0]:.0f}px">{X.rich(vfit[1][0])}</div>'
                    f'<div class="wr-track" style="left:{q["bx"]}px; top:{q["by"]:.0f}px; width:{q["bw"]:.0f}px; height:{q["bh"]}px">'
                    f'<div class="wr-fill" style="width:{fill_w:.0f}px"></div></div></div>')
        return out

    # the wire outlines (card, bar track, bar fill) as one svg; each rect draws on via its dash offset
    rect_svg = ""
    order = 0
    for i, it in enumerate(items):
        if keep and i == hero_i:
            continue
        rx, ry, rw, rh = rects[i]
        q = card_parts(i, rx, ry, rw, rh)
        fill_w = q["bw"] * max(0.0, vals[i]) / vmax
        rect_svg += f'<rect class="w{order}" x="{rx:.0f}" y="{ry:.0f}" width="{rw:.0f}" height="{rh:.0f}" rx="16" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
        order += 1
        rect_svg += f'<rect class="w{order}" x="{rx + q["bx"]:.0f}" y="{ry + q["by"]:.0f}" width="{q["bw"]:.0f}" height="{q["bh"]}" rx="{q["bh"] / 2:.0f}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
        order += 1
        if fill_w > 4:
            rect_svg += f'<rect class="w{order}" x="{rx + q["bx"]:.0f}" y="{ry + q["by"]:.0f}" width="{fill_w:.0f}" height="{q["bh"]}" rx="{q["bh"] / 2:.0f}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
            order += 1
    n_rects = order
    svg = f'<svg class="wr-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{rect_svg}</svg>'

    # a faint rain of code glyphs behind the wire
    R_ = X.rand
    rain = ""
    cols = 14 if P else 22
    for c in range(cols):
        s_ = ""
        for _ in range(int(H / 34) * 2):
            s_ += GLYPHS[R_.randrange(len(GLYPHS))]
        cx_ = (c + 0.5) * W / cols
        rain += f'<div class="wr-col r{c}" style="left:{cx_ - 20:.0f}px">{HTML.escape(s_)}</div>'
    X.used_text.update(GLYPHS)

    inner = (f'<div class="wr-dim"></div><div class="wr-rain" data-safe="ignore" data-layout-ignore>{rain}</div>'
             f'<div class="wr-cards"><div class="wr-layer wr-real">{layer("real", skip=hero_i if keep else None)}</div>'
             f'<div class="wr-layer wr-wire" data-safe="ignore">{layer("wire", skip=hero_i if keep else None)}{svg}</div>'
             + (f'<div class="wr-layer wr-real wr-keep">{layer("real", only=hero_i)}</div>' if keep else "") + '</div>'
             f'<div class="wr-line"></div>' + head)
    _css(X)
    mark = _mark_on(X, p, "card")
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body f3" style="--mark:{mark}">{inner}</div>')
    if head:
        A.head_in(X, s, t, k_)

    # phase A: outlines draw on in reading order; the last one is complete 0.55 s before the resolve line starts, so
    # every card is seen as a wire for at least 0.6 s before the line reaches it
    tb = t + d * 0.42
    a0 = t + min(0.15, d * 0.04)
    draw_d = 0.35
    a1 = tb - 0.55 - draw_d
    if a1 < a0:
        a1 = a0
    step = (a1 - a0) / max(1, n_rects - 1)
    for j in range(n_rects):
        X.tw(f'tl.fromTo("{s} .wr-svg .w{j}", {{attr:{{"stroke-dashoffset":1}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:{draw_d}, ease:"power2.inOut", immediateRender:true}}, {a0 + j * step:.3f});')
    X.tw(f'tl.fromTo("{s} .wr-wire .wr-t, {s} .wr-wire .wr-v", {{opacity:0}}, {{opacity:1, duration:0.3, stagger:{step:.3f}, immediateRender:true}}, {a0 + step:.3f});')
    for c in range(cols):
        speed = 90 + (c * 37) % 80
        start_y = -((c * 211) % 700)
        X.tw(f'tl.fromTo("{s} .wr-col.r{c}", {{y:{start_y}}}, {{y:{start_y + speed * d:.0f}, duration:{d:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')

    # phase B: the resolve line sweeps 0 → H; clip the layers to it (one proxy tween, redrawn from its value)
    sweep = 0.7
    X.tw(f'''(()=>{{
  const R = document.querySelector("{s}");
  if (!R) return;
  const real = R.querySelector(".wr-real"), wire = R.querySelector(".wr-wire"), dim = R.querySelector(".wr-dim");
  const rain = R.querySelector(".wr-rain"), line = R.querySelector(".wr-line");
  const H = {H}, dimTop = {(y0 - 12) if head else 0:.0f};    // the title above the cards stays on the bright ground
  const dimBottom = {max(0, H - y1 - 16):.0f};                   // and so does the caption band under them
  function draw(y) {{
    const yd = Math.max(y, dimTop);
    real.style.clipPath = "inset(0px 0px " + (H - y).toFixed(1) + "px 0px)";
    wire.style.clipPath = "inset(" + y.toFixed(1) + "px 0px 0px 0px)";
    dim.style.clipPath = "inset(" + yd.toFixed(1) + "px 0px " + dimBottom + "px 0px)";
    rain.style.clipPath = "inset(" + yd.toFixed(1) + "px 0px " + dimBottom + "px 0px)";
    line.style.top = y.toFixed(1) + "px";
  }}
  const V = {{ y: 0 }};
  draw(0);
  tl.fromTo(V, {{ y: 0 }}, {{ y: H, duration: {sweep}, ease: "power1.inOut", immediateRender: false, onUpdate: () => draw(V.y) }}, {tb:.3f});
}})();''')
    X.tw(f'tl.fromTo("{s} .wr-line", {{opacity:0}}, {{opacity:1, duration:0.06, immediateRender:true}}, {tb - 0.03:.3f});')
    X.tw(f'tl.to("{s} .wr-line", {{opacity:0, duration:0.12}}, {tb + sweep - 0.08:.3f});')

    # phase C: settled; slow drift, the hero card lifts
    tc = tb + sweep
    X.tw(f'tl.fromTo("{s} .wr-cards", {{scale:1}}, {{scale:1.03, transformOrigin:"50% 50%", duration:{max(0.5, t + d - tc):.2f}, ease:"sine.inOut", immediateRender:false}}, {tc:.3f});')
    X.tw(f'tl.fromTo("{s} .wr-real .c{hero_i}", {{y:0}}, {{y:-14, duration:0.45, ease:"power3.out", immediateRender:false}}, {tc + 0.05:.3f});')
    X.sfx(a0, "click", 0.4)
    X.sfx(tb, "whoosh_soft")


# ------------------------------------------------------------------------------------------------ cube_number
# the cube font: digits and marks drawn on a 3 × 5 skeleton and doubled in both directions, so every stroke is 2 cells
# thick and every glyph is 10 rows tall. "#" = a cube. Units (亿, 万, …) are not cubes: they are set as flat type.
SKELETON = {
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", "..#", "..#"],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    ".": [".", ".", ".", ".", "#"],
    ",": [".", ".", ".", "#", "#"],
    "%": ["#.#", "..#", ".#.", "#..", "#.#"],
}
GLYPH_ROWS = 10


def _split_value(fx, text):
    """"66.7亿" → ("66.7", "亿"): the leading run of digits and marks becomes cubes, the rest is the unit (flat type)."""
    s_ = str(text).strip()
    digits = ""
    i = 0
    while i < len(s_) and s_[i] in SKELETON:
        digits += s_[i]
        i += 1
    unit = s_[i:].strip()
    if not digits:
        raise SystemExit(f"{fx}: {text!r} must start with a number (0-9 . , %); units such as 亿 or 万 follow it")
    return digits, unit


def _cells(text):
    """the cube cells of `text` (digits and marks only) → (set of (col, row), width in columns)."""
    cells = set()
    col = 0
    first = True
    for ch in str(text):
        if not first:
            col += 1                        # one empty column between characters
        first = False
        sk = SKELETON[ch]
        for r in range(5):
            for c in range(len(sk[r])):
                if sk[r][c] == "#":
                    for dr in range(2):
                        for dc in range(2):
                            cells.add((col + c * 2 + dc, r * 2 + dr))
        col += len(sk[0]) * 2
    return cells, col


def _lstar(c):
    """CIE L* (0–100) of a #hex colour, or None."""
    rgb = _hex(c)
    if rgb is None:
        return None
    lin = []
    for v in rgb:
        v = v / 255.0
        if v <= 0.04045:
            lin.append(v / 12.92)
        else:
            lin.append(((v + 0.055) / 1.055) ** 2.4)
    y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    if y > 0.008856:
        return 116 * y ** (1 / 3) - 16
    return 903.3 * y


def _tile_colour(ground):
    """the tile top: the page ground lightened (dark grounds) or darkened (light grounds) until it differs by ≥ 14 L*."""
    l0 = _lstar(ground)
    if l0 is None:
        return "#808080"
    towards = "#ffffff" if l0 < 55 else "#000000"
    w = 0.0
    tile = ground
    while w < 0.9:
        w += 0.02
        tile = _mix(towards, ground, w)
        if abs(_lstar(tile) - l0) >= 14:
            break
    return tile


def cube_number(X, cid, t, d, p):
    """方块落数 Cube Number: a tile board seen straight on from above-front; the digits of the number are built from accent
    cubes (2 cells per stroke) that fall onto it column by column, each landing with a little squash and a contact shadow.
    The unit (亿, 万 …) is set as flat type under the right end of the digits and arrives with the last cube. With
    `from`, the board first shows the old number, its cubes sink through the board, and the new number's cubes fall in —
    a real change, no made-up in-between values."""
    F_ = "cube_number"
    value = str(p.get("value") if p.get("value") is not None else "")
    A.need(F_, t, p, [] if value else ["value (the number, e.g. \"77.56亿\")"])
    value = value or "0"
    old = p.get("from")
    old = str(old) if old not in (None, "") else ""
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    fps = X.fps

    digits, unit = _split_value(F_, value)
    cells, width = _cells(digits)
    old_digits, old_unit = "", ""
    old_cells, old_width = (set(), 0)
    if old:
        old_digits, old_unit = _split_value(F_, old)
        old_cells, old_width = _cells(old_digits)
    cols = max(width, old_width) + 2       # the grid is sized to the digits only, so the cells come out large
    if cols < 14:
        cols = 14
    tilt = 40.0
    ct = math.cos(math.radians(tilt))
    st = math.sin(math.radians(tilt))
    focal = 2000.0

    # sizes: 9:16 board 920 px wide, about 560 px tall on screen, centred at y 740; 16:9 fills the height between header
    # and caption after the label, the unit and the sub line
    label = str(p.get("label") or "")
    sub = str(p.get("sub") or "")
    lpx = 56 if P else 44
    spx = 36 if P else 30
    upx = 120 if P else 90
    unit_room = upx * 1.1 if (unit or old_unit) and P else 0       # 16:9 sets the unit beside the board instead
    if P:
        board_w = 920.0
        cy = 740.0
        proj_target = 520.0
    else:
        board_w = min(G["w"] * 0.7, 1300.0)
        label_room = lpx * 1.6 if label else 0
        sub_room = spx * 2.2 if sub else 0
        room = G["y1"] - G["y0"] - label_room - sub_room - unit_room
        proj_target = min(room - 60, board_w * 0.45)
        cy = G["y0"] + label_room + 20 + proj_target / 2
    cell = board_w / cols
    rows = int(round(proj_target / (cell * ct)))
    if rows < GLYPH_ROWS + 4:
        rows = GLYPH_ROWS + 4
    board_d = rows * cell
    half = board_d / 2
    # where the board's far and near edges land on screen (perspective about the board centre)
    far_y = cy - half * ct * focal / (focal + half * st)
    near_y = cy + half * ct * focal / (focal - half * st)
    left = (W - board_w) / 2

    def origin(w):
        return (cols - w) // 2, (rows - GLYPH_ROWS) // 2

    def screen_y(row):
        """screen y of a board row's centre (for the fall heights: cubes never rise into the header)."""
        yb = (row + 0.5) * cell - half
        return cy + yb * ct * focal / (focal - yb * st)

    def drop_for(col, row):
        """the fall height of the cube at (col, row): up to 600 px, lowered until its starting point is inside the frame
        and below the header (a raised cube comes toward the lens, so outer columns also spread outward)."""
        xb = (col + 0.5) * cell - board_w / 2
        yb = (row + 0.5) * cell - half
        z = 600.0
        while z > 100:
            k = focal / (focal - yb * st - z * ct)
            sx = W / 2 + xb * k
            sy = cy + (yb * ct - z * st) * k
            half_w = cell * k * 0.6
            if 30 + half_w <= sx <= W - 30 - half_w and sy >= 330:
                break
            z -= 20
        return round(z)

    def cube_html(cells_, c0, r0, cls):
        out = ""
        drops = []
        order = sorted(cells_)              # (column, row): left to right, top to bottom inside a column
        for k, (c, r) in enumerate(order):
            x = (c0 + c) * cell
            y = (r0 + r) * cell
            w = cell - 2.0                  # the 2 px gap between tiles shows between cubes too
            out += (f'<div class="cn-cube {cls} {cls[0]}{k}" style="left:{x + 1:.1f}px; top:{y + 1:.1f}px; width:{w:.1f}px; height:{w:.1f}px">'
                    f'<i class="sh" style="left:{-w * 0.3:.1f}px; top:{-w * 0.15:.1f}px; width:{w * 1.6:.1f}px; height:{w * 1.55:.1f}px; transform:translateZ(calc(var(--z) * -1px + 0.5px))"></i>'
                    f'<i class="ft" style="width:{w:.1f}px; height:{w:.1f}px; transform:translateZ({w:.1f}px)"></i>'
                    f'<i class="fr" style="width:{w:.1f}px; height:{w:.1f}px; top:{w:.1f}px; transform:rotateX(90deg)"></i></div>')
            drops.append(drop_for(c0 + c, r0 + r))

        return out, len(order), drops

    c0, r0 = origin(width)
    new_html, n_new, drops = cube_html(cells, c0, r0, "new")
    old_html, n_old = "", 0
    if old:
        oc0, or0 = origin(old_width)
        old_html, n_old, unused = cube_html(old_cells, oc0, or0, "old")
    edge = max(14.0, cell * 0.5)
    board = (f'<div class="cn-board" style="width:{board_w:.0f}px; height:{board_d:.0f}px; transform:rotateX({tilt}deg)">'
             f'<div class="cn-top" style="background-size:{cell:.3f}px {cell:.3f}px, {cell:.3f}px {cell:.3f}px"></div>'
             f'<div class="cn-edge" style="top:{board_d:.0f}px; width:{board_w:.0f}px; height:{edge:.0f}px; transform:rotateX(-90deg)"></div>'
             f'{old_html}{new_html}</div>')
    view = f'<div class="cn-view" style="left:{left:.0f}px; top:{cy - half:.0f}px; width:{board_w:.0f}px; height:{board_d:.0f}px">{board}</div>'

    # the unit: flat type right-aligned under the right end of the digit block (front rows are drawn a little larger)
    near_k = focal / (focal - half * st)
    unit_y = near_y + edge + 10
    unit_html = ""
    for key, txt, w_ in (("u-new", unit, width), ("u-old", old_unit, old_width)):
        if not txt:
            continue
        uf = A.fit_px(A.strip(txt), G["w"] * 0.6, upx * 1.2, upx, 40, max_lines=1, lh=1.0)
        if P:
            # 9:16: right-aligned under the right end of the digit block
            right_x = W / 2 + (w_ * cell / 2) * near_k
            if right_x > G["x1"]:
                right_x = G["x1"]
            if right_x > W - 120:
                right_x = W - 120            # clear of the platform buttons on the lower right
            pos = f"right:{W - right_x:.0f}px; top:{unit_y:.0f}px"
        else:
            # 16:9: beside the board, its foot on the digits' baseline
            base_row = (rows - GLYPH_ROWS) // 2 + GLYPH_ROWS
            yb = base_row * cell - half
            k_row = focal / (focal - yb * st)
            base_y = cy + yb * ct * k_row
            pos = f"left:{W / 2 + board_w / 2 * k_row + 28:.0f}px; top:{base_y - uf[0] * 0.95:.0f}px"
        unit_html += f'<div class="cn-unit {key}" style="{pos}; font-size:{uf[0]:.0f}px">{X.rich(uf[1][0])}</div>'
    label_html = ""
    if label:
        lf = A.fit_px(A.strip(label), G["w"], lpx * 1.3, lpx, 32, max_lines=1)
        label_html = (f'<div class="cn-label" style="left:{G["x0"]:.0f}px; right:{W - G["x1"]:.0f}px; top:{far_y - 40 - lf[0] * 1.3:.0f}px; '
                      f'font-size:{lf[0]:.0f}px">{K.hl_html(X, lf[1][0])}</div>')
    sub_html = ""
    if sub:
        sf = A.fit_px(A.strip(sub), G["w"], spx * 1.4, spx, 28, max_lines=1)
        sub_y = near_y + edge + 34
        if (unit or old_unit) and P:
            sub_y = unit_y + upx * 1.05 + 24
        sub_html = f'<div class="cn-sub" style="top:{sub_y:.0f}px; font-size:{sf[0]:.0f}px">{X.rich(sf[1][0])}</div>'
    inner = label_html + view + unit_html + sub_html

    # colours: the tiles are the page ground shifted ≥ 14 L* (lighter on dark grounds, darker on light ones) with 2 px
    # gaps in the ground colour, so the board reads before any cube lands; cubes in the accent, or the colour that
    # stands out best on the tiles when the accent does not
    from h9.aefx import _contrast
    pal = A.pal(X, p)
    ground = pal.get("bg", "#f0ece3")
    tile = _tile_colour(ground)
    cube = pal.get("accent", "#e2321f")
    if _contrast(cube, tile) < 2.2:
        best = cube
        best_c = _contrast(cube, tile)
        for key in ("fg", "card-fg", "card", "bg"):
            c = pal.get(key)
            if c and _contrast(c, tile) > best_c:
                best = c
                best_c = _contrast(c, tile)
        cube = best
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body f3" style="--cube:{cube}; --board:{tile}; --gap:{ground}">{inner}</div>')
    if label:
        K.hl_tween(X, f"{s} .cn-label", t + 0.5, k_)
        X.tw(f'tl.fromTo("{s} .cn-label", {{opacity:0, y:-20}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .cn-view", {{opacity:0, y:40}}, {{opacity:1, y:0, duration:0.45, ease:"power3.out", immediateRender:true}}, {t + 0.05:.3f});')

    # timing: with `from` the old number holds, then sinks; the new build takes 1.2 s
    frame = 1.0 / fps
    fall = 0.36
    squash = 4 * frame
    if old:
        swap = t + max(0.9, d * 0.32)
        X.tw(f'tl.to("{s} .cn-cube.old", {{"--z":-260, opacity:0, duration:0.3, ease:"power2.in", stagger:{0.25 / max(1, n_old):.4f}}}, {swap:.3f});')
        same_unit = old_unit == unit and old_width == width     # the same unit in the same place simply stays
        if old_unit:
            X.tw(f'tl.fromTo("{s} .u-old", {{opacity:0}}, {{opacity:1, duration:0.3, immediateRender:true}}, {t + 0.3:.3f});')
            if not same_unit:
                X.tw(f'tl.to("{s} .u-old", {{opacity:0, duration:0.2}}, {swap:.3f});')
        build = swap + 0.35
    else:
        build = t + 0.35
    if build + 1.2 > t + d - 0.6:
        build = t + d - 1.8
    spread = 1.2 - fall - squash
    js = """(()=>{
  const S = "__S__";
  const n = __N__;
  const drops = __DROPS__;
  for (let k = 0; k < n; k++) {
    const e = S + " .cn-cube.n" + k;
    const start = __BUILD__ + (n > 1 ? k / (n - 1) : 0) * __SPREAD__;
    const land = start + __FALL__;
    tl.fromTo(e, { opacity: 0 }, { opacity: 1, duration: __FADE__, ease: "none", immediateRender: false }, start);
    tl.fromTo(e, { "--z": drops[k] }, { "--z": 0, duration: __FALL__, ease: "power2.in", immediateRender: true }, start);
    tl.to(e, { keyframes: [{ "--sz": 0.8, duration: __F15__ }, { "--sz": 1.05, duration: __F15__ }, { "--sz": 1, duration: __F1__ }], ease: "none" }, land);
  }
})();"""
    js = (js.replace("__S__", s).replace("__N__", str(n_new)).replace("__DROPS__", A.js(drops))
            .replace("__BUILD__", f"{build:.3f}").replace("__SPREAD__", f"{spread:.3f}").replace("__FALL__", f"{fall}")
            .replace("__FADE__", f"{3 * frame:.4f}").replace("__F15__", f"{frame * 1.5:.4f}").replace("__F1__", f"{frame:.4f}"))
    X.tw(js)
    done = build + 1.2                      # the last cube has landed
    if unit and not (old and old_unit == unit and old_width == width):
        X.tw(f'tl.fromTo("{s} .u-new", {{opacity:0, y:-18}}, {{opacity:1, y:0, duration:0.3, ease:"power3.out", immediateRender:true}}, {done - 0.05:.3f});')
    if sub:
        X.tw(f'tl.fromTo("{s} .cn-sub", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out", immediateRender:true}}, {done + 0.15:.3f});')
    A.hold_push(X, f"{s} .f3", done + 0.3, t + d, 1.03, origin=f"50% {cy:.0f}px")
    X.sfx(build, "tick", 0.4)
    X.sfx(done - 0.1, "hit", 0.5)


FX = {"glyph_sphere": glyph_sphere, "wire_resolve": wire_resolve, "cube_number": cube_number}
