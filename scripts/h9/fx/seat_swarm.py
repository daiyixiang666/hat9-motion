"""一个空位 · 一群人 Seat swarm (scarcity / demand): a grid of seats, almost all taken; one empty seat gets a dashed
ring and a label ("1 个空位"), then wave after wave of coloured dots rushes in and circles it while the counter beside
steps through its anchors (52 → 98 → 100+), each step landing with a punch.

Adapts: any anchors (1–6, "100+" style suffixes kept), any seat grid size (from the panel), labels from a word to a
line (fitted), 0–300 dots; with a subject the counter sits beside the subject card. Seats, dots and the ring take the
style's colours, corner shape (square dots in pixel) and stroke.
p: steps [[value, at], ...] (or `value`) · unit · kicker · seat_label (on the empty seat) · dots · rows · subject ·
   subject_label · mock
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

CSS = """
.fx .ss .ss-pan { position:absolute; overflow:hidden; }
.fx .ss .ss-pan.rule { background:transparent; box-shadow:none; border-top:var(--mt-sw) solid var(--fg); border-radius:0; }
.fx .ss .ss-seat { position:absolute; border-radius:var(--mt-dot); background:color-mix(in srgb, var(--card-fg) 16%, var(--card)); }
.fx .ss .ss-pan.rule .ss-seat { background:color-mix(in srgb, var(--fg) 16%, var(--bg)); }
.fx .ss .ss-seat.e { background:transparent; box-shadow:inset 0 0 0 calc(var(--d) * .16) color-mix(in srgb, var(--card-fg) 10%, transparent); }
.fx .ss .ss-seat.tg { background:transparent; box-shadow:inset 0 0 0 calc(var(--d) * .16) color-mix(in srgb, var(--card-fg) 26%, transparent); }
.fx .ss .ss-pan.rule .ss-seat.e { box-shadow:inset 0 0 0 calc(var(--d) * .16) color-mix(in srgb, var(--fg) 10%, transparent); }
.fx .ss .ss-pan.rule .ss-seat.tg { box-shadow:inset 0 0 0 calc(var(--d) * .16) color-mix(in srgb, var(--fg) 26%, transparent); }
.fx .ss .ss-ring { position:absolute; overflow:visible; }
.fx .ss .ss-ring circle { fill:none; stroke:var(--accent); stroke-dasharray:6 7; }
.fx .ss .ss-orb { position:absolute; width:0; height:0; }
.fx .ss .ss-dot { position:absolute; border-radius:var(--mt-dot); }
.fx .ss .ss-lab { font-size:30px; color:var(--card-fg); background:var(--card); box-shadow:inset 0 0 0 3px var(--card-fg); }
.fx .ss .ss-pan.rule .ss-lab { color:var(--fg); background:var(--bg); box-shadow:inset 0 0 0 3px var(--fg); }
.fx .ss .ss-seats { position:absolute; inset:0; }
.fx .ss.v-hud .ss-seat { background:transparent; box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--accent) 45%, transparent); }
.fx .ss.v-hud .ss-seat.e { box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--accent) 22%, transparent); }
.fx .ss.v-hud .ss-seat.tg { box-shadow:inset 0 0 0 3px var(--accent); }
.fx .ss .ss-xh, .fx .ss .ss-xv { position:absolute; background:color-mix(in srgb, var(--accent) 55%, transparent); }
.fx .ss .ss-xh { height:1px; } .fx .ss .ss-xv { width:1px; }
.fx .ss .ss-ro { position:absolute; font:700 20px/1.5 var(--f-mono, monospace); letter-spacing:.12em; color:var(--accent); }
.fx .ss.v-poster .ss-seat, .fx .ss.v-poster .ss-dot { border-radius:0; }
.fx .ss.v-poster .ss-pan.rule .ss-seat { background:var(--fg); }
.fx .ss.v-poster .ss-pan.rule .ss-seat.e { background:transparent; box-shadow:inset 0 0 0 calc(var(--d) * .12) var(--fg); }
.fx .ss.v-poster .ss-pan.rule .ss-seat.tg { background:transparent; box-shadow:inset 0 0 0 calc(var(--d) * .12) var(--accent); }
.fx .ss.v-ink .ss-pan.rule .ss-seat { background:color-mix(in srgb, var(--fg) 30%, var(--bg)); }
.fx .ss .ss-info { position:absolute; display:flex; flex-direction:column; justify-content:center; }
.fx .ss .ss-kick { font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.15; margin-bottom:.35em; }
.fx .ss .ss-kick .fl { display:block; white-space:nowrap; }
.fx .ss .ss-num { color:var(--accent); transform-origin:0 70%; display:inline-block; }
.fx .ss .ss-unit { font-family:var(--f-body); font-weight:800; color:var(--fg); margin-top:.3em; line-height:1.2; }
.fx .ss .ss-unit .fl { display:block; white-space:nowrap; }
"""



def seat_swarm(X, cid, t, d, p):
    M.base(X)
    X.css("fx-ss", CSS)
    sk = M.skin(X)
    P = X.portrait
    rnd = random.Random(int(p.get("seed", 9)) * 7919 + 77)
    raw = p.get("steps") or [p.get("value", 100)]
    steps = M.anchors(X, raw, t, d, first=0.32, last=0.74)
    has_sub = bool(p.get("subject"))
    R = M.regions(X, p, has_sub, graphic_share=0.6, hero_ar=1.1, row="info")
    gx0, gy0, gx1, gy1 = R["g"]
    # panel + info boxes
    if R["side"]:
        pan = (gx0, gy0, gx1, gy1)
        info = R["side"]
    elif P:
        split = gy0 + (gy1 - gy0) * 0.6
        pan = (gx0, gy0, gx1, split)
        info = (gx0, split + 40, gx1, gy1)
    else:
        split = gx0 + (gx1 - gx0) * 0.6
        pan = (gx0, gy0, split, gy1)
        info = (split + 70, gy0, gx1, gy1)
    px0, py0, px1, py1 = pan
    pw = px1 - px0
    ph = py1 - py0
    # seats: big discs, the grid bleeding past the panel edges
    rows = int(p.get("rows", 4 if P else 3))
    pitch = ph / (rows - 0.3)
    dd = pitch * 0.78
    cols = int(math.ceil(pw / pitch)) + 1
    ox = (pw - (cols - 1) * pitch) / 2 - dd / 2
    oy = (ph - (rows - 1) * pitch) / 2 - dd / 2
    tc = cols // 2
    tr = rows // 2 if rows > 2 else 1
    if (ox + tc * pitch + dd / 2) > pw * 0.62 and tc > 1:
        tc -= 1
    seats = []
    for r in range(rows):
        for c in range(cols):
            x = ox + c * pitch
            y = oy + r * pitch
            cls = "ss-seat"
            if r == tr and c == tc:
                cls += " tg"
            elif rnd.random() < 0.12:
                cls += " e"
            seats.append(f'<i class="{cls}" data-r="{r}" style="left:{x:.1f}px; top:{y:.1f}px; width:{dd:.1f}px; height:{dd:.1f}px"></i>')
    tx = ox + tc * pitch + dd / 2
    ty = oy + tr * pitch + dd / 2
    ring_r = dd * 0.62
    ring = (f'<svg class="ss-ring" style="left:{tx - ring_r - 6:.1f}px; top:{ty - ring_r - 6:.1f}px" width="{2 * ring_r + 12:.0f}" height="{2 * ring_r + 12:.0f}">'
            f'<circle cx="{ring_r + 6:.1f}" cy="{ring_r + 6:.1f}" r="{ring_r:.1f}" style="stroke-width:{max(3, dd * 0.05):.1f}px"/></svg>')
    lab = p.get("seat_label", "1 个空位")
    X.used_text.update(lab)
    lab_html = f'<div class="mt-pill ss-lab" style="left:{tx:.0f}px; top:{ty - ring_r - 18:.0f}px">{X.rich(lab)}</div>'
    # the swarm: dots in waves, one wave per anchor, in proportion to the step
    n = int(p.get("dots", 130))
    pal = M.swarm_palette(X, p, sk)
    vals = []
    for _, v in steps:
        vals.append(max(0.0, M.split_num(v)[0]))
    last = max(vals[-1], 1.0)
    bounds = []
    acc = 0
    for i, v in enumerate(vals):
        share = v / last
        upto = int(round(n * share)) if i < len(vals) - 1 else n
        bounds.append(max(acc, upto))
        acc = bounds[-1]
    dots = []
    wave_of = []
    w = 0
    far = max(pw, ph) * 0.9
    ds = max(8.0, dd * 0.12)
    moves = []
    for i in range(n):
        while w < len(bounds) - 1 and i >= bounds[w]:
            w += 1
        wave_of.append(w)
        a0 = rnd.uniform(0, math.tau)
        r0 = far * rnd.uniform(0.7, 1.15)
        a1 = rnd.uniform(0, math.tau)
        r1 = ring_r * rnd.uniform(0.95, 1.55)
        col = pal[rnd.randrange(len(pal))]
        sz = ds * rnd.uniform(0.8, 1.25)
        dots.append(f'<i class="ss-dot" data-i="{i}" style="left:{-sz / 2:.1f}px; top:{-sz / 2:.1f}px; width:{sz:.1f}px; height:{sz:.1f}px; background:{col}"></i>')
        moves.append((r0 * math.cos(a0), r0 * math.sin(a0), r1 * math.cos(a1), r1 * math.sin(a1), rnd.uniform(0, 0.55), rnd.uniform(0.7, 1.15)))
    orb = f'<div class="ss-orb" style="left:{tx:.1f}px; top:{ty:.1f}px">{"".join(dots)}</div>'
    # style-specific structure: hud draws a crosshair and a readout on the free seat; ink roughens the seats like a brush
    hud_html = ""
    brush = ""
    if sk["id"] == "hud":
        X.used_text.update("SEAT FREE 0123456789·R C")
        hud_html = (f'<i class="ss-xh" style="left:0; right:0; top:{ty:.1f}px"></i><i class="ss-xv" style="top:0; bottom:0; left:{tx:.1f}px"></i>'
                    f'<div class="ss-ro" style="left:{tx + ring_r * 1.9:.0f}px; top:{ty - ring_r * 1.4:.0f}px">SEAT R{tr + 1}·C{tc + 1}<br>FREE</div>')
    if sk["id"] == "ink":
        brush, bid = M.brush_filter(cid, 7)
        X.css(f"fx-ss-brush-{cid}", f"#{cid} .ss-seats {{ filter:url(#{bid}); }}")
    pan_cls = "mt-card ss-pan" + (" rule" if sk["panel"] == "rule" else "")
    panel = (f'<div class="{pan_cls}" style="left:{px0:.0f}px; top:{py0:.0f}px; width:{pw:.0f}px; height:{ph:.0f}px; --d:{dd:.1f}px">'
             f'<div class="ss-seats">{"".join(seats)}</div>{hud_html}{ring}{orb}{lab_html}</div>{brush}')
    # info: kicker · counter · unit
    ix0, iy0, ix1, iy1 = info
    iw = ix1 - ix0
    ih = iy1 - iy0
    num_html, sufs = M.stepper_html(X, steps)
    longest = max(len(v) for _, v in steps)
    n_px = min(ih * 0.5, iw / max(1.0, longest * 0.62), 240 if not P else 270)
    kick = p.get("kicker", "")
    unit = p.get("unit", "")
    k_html = ""
    if kick:
        k_px, k_lines, _ = M.fit_text(X, kick, iw, ih * 0.3, min(64, n_px * 0.42), 24, 2)
        k_html = f'<div class="ss-kick" style="font-size:{k_px:.0f}px">{k_lines}</div>'
    u_html = ""
    if unit:
        u_px, u_lines, _ = M.fit_text(X, unit, iw, ih * 0.25, min(46, n_px * 0.3), 22, 2)
        u_html = f'<div class="ss-unit" style="font-size:{u_px:.0f}px">{u_lines}</div>'
    info_html = (f'<div class="ss-info" style="left:{ix0:.0f}px; top:{iy0:.0f}px; width:{iw:.0f}px; height:{ih:.0f}px">'
                 f'{k_html}<div><span class="ss-num" style="font-size:{n_px:.0f}px">{num_html}</span></div>{u_html}</div>')
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=t + 0.3)
    mock = M.mock_tag(X, p, px1 - 80, py0 + 12)
    _clip(X, cid, t, d, M.wrap(X, sk, panel + info_html + subj + mock, "ss v-" + sk["id"]), p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    # 1 · the hall fills in
    X.tw(f'tl.from("{s} .ss-pan", {{y:50, opacity:0, duration:0.55, ease:"{e}"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .ss-seat", {{scale:0, duration:0.4, ease:"back.out(2)", stagger:{{grid:[{rows},{cols}], from:[{tr},{tc}], amount:0.45}}}}, {t + 0.12:.3f});')
    X.tw(f'tl.from("{s} .ss-info > *", {{x:-30, opacity:0, duration:0.5, ease:"{e}", stagger:0.1}}, {t + 0.35:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # 2 · the empty seat is marked
    t_mark = t + 0.6
    X.tw(f'tl.from("{s} .ss-ring", {{scale:2.2, opacity:0, duration:0.5, ease:"expo.out"}}, {t_mark:.3f});')
    X.tw(f'tl.fromTo("{s} .ss-ring", {{rotation:0}}, {{rotation:200, duration:{d:.2f}, ease:"none", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.set("{s} .ss-lab", {{xPercent:-50, yPercent:-100}}, 0);')   # centring through GSAP, so its y tweens keep it
    X.tw(f'tl.from("{s} .ss-lab", {{y:20, scale:0.6, opacity:0, duration:0.4, ease:"back.out(2.4)"}}, {t_mark + 0.15:.3f});')
    X.sfx(t_mark, "pop")
    # 3 · the swarm, one wave per step, circling the seat
    X.tw(f'tl.fromTo("{s} .ss-orb", {{rotation:0}}, {{rotation:150, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    for i in range(n):
        x0, y0, x1, y1, delay, dur = moves[i]
        when = steps[wave_of[i]][0] - 0.35 + delay
        X.tw(f'tl.fromTo("{s} .ss-dot[data-i=\'{i}\']", {{x:{x0:.0f}, y:{y0:.0f}, opacity:0}}, {{x:{x1:.1f}, y:{y1:.1f}, opacity:1, duration:{dur:.2f}, ease:"power3.out"}}, {when:.3f});')
    for when, _ in steps:
        X.tw(f'tl.fromTo("{s} .ss-ring", {{scale:1}}, {{keyframes:[{{scale:1.12, duration:0.1}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {when + 0.4:.3f});')
    M.stepper(X, f"{s} .ss-num", steps, sufs)
    # hold: the label nudges, the hall drifts
    X.tw(f'tl.to("{s} .ss-lab", {{y:-8, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:{max(1, int((d - 1.5) / 0.5))}}}, {t_mark + 0.6:.3f});')


FX = {"seat_swarm": seat_swarm}
