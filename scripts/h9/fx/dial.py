"""仪表 / 时钟 Dial: a claim read off an instrument.
mode "gauge": a 240° gauge — the track and ticks draw on, the needle sweeps up to the value with a little overshoot,
  the value arc fills behind it and the label lands under (兼容性 / 满意度 / 风险).
mode "clock": a 24-hour (or 60-minute) dial — the hand runs round, the ring fills behind it while the centre counts
  up (0 → 24h), then a stamp lands ("处理好 ✓").
Both can open on an icon (inbox, chip, …) that drops in first and a note card falling into it, and can sit on a
background that drifts from day to night (sun down, moon up).

Adapts: any range (min / max / value, units), 0–8 tick labels, short or long labels (fitted), with or without a subject
card; colours, numeral face, stroke and corners follow the style.
p: mode (gauge | clock) · value · min · max · unit · text (the label under the dial) · lo / hi (gauge end labels) · hours (clock: 24 | 12 | 60)
   · stamp (clock) · icon (inbox | chip | person | … or an SVG path) · note (a card that drops into the icon) ·
   daynight (true) · subject · subject_label · mock
"""
import importlib.util
import math
import pathlib
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

ICONS = {
    "inbox": '<path d="M3 13l3-8h12l3 8v6H3z"/><path d="M3 13h5l1.5 2.5h5L16 13h5"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "bug": '<rect x="7" y="7" width="10" height="13" rx="5"/><path d="M12 7v13M7 12H3M21 12h-4M7 17l-3 2M17 17l3 2M8 6l-2-3M16 6l2-3"/>',
}

CSS = """
.fx .dl .dl-sky { position:absolute; overflow:hidden; border-radius:var(--mt-r); box-shadow:var(--mt-shadow); }
.fx .dl .dl-sky .day, .fx .dl .dl-sky .night { position:absolute; inset:0; }
.fx .dl .dl-sky .day { background:linear-gradient(180deg, color-mix(in srgb, var(--accent) 26%, #eef0f2), color-mix(in srgb, var(--accent) 8%, #f6f4ef)); }
.fx .dl .dl-sky .night { background:linear-gradient(180deg, color-mix(in srgb, #070a12 86%, var(--accent)), color-mix(in srgb, #11141c 92%, var(--accent))); opacity:0; }
.fx .dl .dl-sky.dk .day { background:linear-gradient(180deg, color-mix(in srgb, var(--accent) 30%, var(--bg)), color-mix(in srgb, var(--accent) 10%, var(--bg))); }
.fx .dl .dl-sky.dk .night { background:linear-gradient(180deg, #03050a, color-mix(in srgb, #06080e 90%, var(--accent))); }
.fx .dl .dl-sky .sun, .fx .dl .dl-sky .moon { position:absolute; border-radius:var(--mt-dot); }
.fx .dl .dl-sky .sun { background:var(--accent); }
.fx .dl .dl-sky .moon { background:#f1ede4; box-shadow:inset -14px -6px 0 #b9b4aa; opacity:0; }
.fx .dl svg.dl-g { position:absolute; overflow:visible; }
.fx .dl .trk { fill:none; stroke:color-mix(in srgb, var(--fg) 14%, transparent); }
.fx .dl .val { fill:none; stroke:var(--accent); }
.fx .dl .tk { stroke:var(--fg); }
.fx .dl .tk.mn { stroke:color-mix(in srgb, var(--fg) 40%, transparent); }
.fx .dl .face { fill:var(--card); stroke:var(--fg); }
.fx .dl .clock .tk, .fx .dl .clock .hand { stroke:var(--card-fg); }
.fx .dl .clock .tk.mn { stroke:color-mix(in srgb, var(--card-fg) 40%, transparent); }
.fx .dl .clock .trk { stroke:color-mix(in srgb, var(--card-fg) 12%, transparent); }
.fx .dl .dl-mid.on-face { color:var(--card-fg); background:var(--card); padding:.04em .22em .06em; border-radius:calc(var(--mt-r) * .8);
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 12%, transparent); }
.fx .dl .hub { fill:var(--fg); }
.fx .dl .hubr { fill:var(--bg); stroke:var(--accent); stroke-width:3px; }
.fx .dl .ndln { stroke:var(--accent); stroke-linecap:round; }
.fx .dl .tl.tn { font-family:var(--f-mono, monospace); font-weight:500; fill:color-mix(in srgb, var(--fg) 60%, transparent); }
.fx .dl .dotk { fill:var(--fg); }
.fx .dl .dl-ro { position:absolute; transform:translateX(-50%); white-space:nowrap; font:600 22px var(--f-mono, monospace); letter-spacing:.14em; color:var(--accent); }
.fx .dl .dl-ro b { color:var(--fg); font-weight:700; margin:0 .3em 0 .9em; }
.fx .dl .ndl { fill:var(--fg); }
.fx .dl .hand { stroke:var(--fg); stroke-linecap:round; }
.fx .dl .tl { font-family:var(--f-body); font-weight:700; fill:var(--muted); }
.fx .dl .dl-mid { position:absolute; transform:translate(-50%, -50%); text-align:center; color:var(--fg); }
.fx .dl .dl-mid small { font-family:var(--f-body); font-weight:800; font-size:.42em; margin-left:.06em; }
.fx .dl .dl-lab { position:absolute; text-align:center; }
.fx .dl .dl-mid.on-wedge { background:var(--bg); padding:.02em .2em .04em; }
.fx .dl .dl-lab.left { text-align:left; } .fx .dl .dl-lab.left.plate .fl { margin:0 0 .2em; }
.fx .dl .dl-lab.plate .fl { display:table; margin:0 auto; color:var(--bg); background:var(--fg); padding:.08em .5em .14em; border-radius:var(--mt-r); }
.fx .dl .dl-ico { position:absolute; display:grid; place-items:center; }
.fx .dl .dl-ico svg { width:100%; height:100%; fill:var(--card); stroke:var(--fg); stroke-linejoin:round; stroke-linecap:round; }
.fx .dl .dl-note { position:absolute; font-size:26px; }
.fx .dl .dl-stamp { position:absolute; transform:translate(-50%, -50%) rotate(-9deg); white-space:nowrap; font-family:var(--f-display); font-weight:900;
  color:var(--accent); border:calc(var(--mt-sw) * 1.4) solid var(--accent); border-radius:calc(var(--mt-r) * .6); padding:.08em .4em; background:color-mix(in srgb, var(--card) 88%, transparent); }
"""


GAUGE_BUILD = {"hud": "line", "screen": "line", "chrome3d": "line", "poster": "wedge", "pixel": "wedge", "ink": "brush", "sketch": "brush"}


def _arc(cx, cy, r, a0, a1):
    """SVG arc path from angle a0 to a1 (degrees, 0 = up, clockwise)."""
    x0 = cx + r * math.sin(math.radians(a0))
    y0 = cy - r * math.cos(math.radians(a0))
    x1 = cx + r * math.sin(math.radians(a1))
    y1 = cy - r * math.cos(math.radians(a1))
    large = 1 if (a1 - a0) > 180 else 0
    return f"M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}"


def dial(X, cid, t, d, p):
    W3 = M.W3
    M.base(X)
    X.css("fx-dl", CSS)
    sk = M.skin(X)
    P = X.portrait
    mode = p.get("mode", "gauge")
    has_sub = bool(p.get("subject"))
    icon = p.get("icon")
    hero_ar = 1.15 if mode == "gauge" else 1.0
    row = "info" if (icon and P) else "center"
    R = M.regions(X, p, has_sub, sub_ar=0.72, graphic_share=0.6, hero_ar=hero_ar, row=row)
    gx0, gy0, gx1, gy1 = R["g"]
    # where the dial and the icon go: 9:16 puts the icon in the row under the dial, 16:9 beside it
    lab = p.get("text", "")
    lab_h = 0
    if lab:
        lab_h = 96 if P else 90
    if mode == "gauge" and GAUGE_BUILD.get(sk["id"]) == "line":
        lab_h += 40
    ibox = None
    dbox = (gx0, gy0, gx1, gy1)
    lab_box = None
    if P and mode == "clock" and has_sub:
        # 9:16 clock + subject: the clock fills the upper frame (~70 % wide), the subject card overlaps its lower-right
        # rim the way a presenter card sits on a graphic; label and icon take the lower-left corner
        bottom = 1270 if p.get("line") else 1460
        dbox = (X.W / 2 - 400, 250, X.W / 2 + 400, 250 + 720)
        sw_ = 290
        sh_ = 360
        R["s"] = (X.W - 120 - sw_, bottom - sh_, X.W - 120, bottom)
        lab_box = (56, 250 + 760, X.W - 120 - sw_ - 30, 250 + 760 + 110)
        ibox = (56, lab_box[3] + 10, 56 + 260, bottom) if icon else None
        lab_h = 0
    elif icon and P and R["side"]:
        ibox = R["side"]
    elif icon and not P:
        ibox = (gx0, gy0, gx0 + (gx1 - gx0) * 0.3, gy1)
        dbox = (ibox[2] + 30, gy0, gx1, gy1)
    dx0, dy0, dx1, dy1 = dbox
    dw = dx1 - dx0
    dh = dy1 - dy0 - lab_h
    if mode == "gauge":
        r = min(dw * 0.42, dh / 1.75)
        cx = (dx0 + dx1) / 2
        cy = dy0 + (dh - r * 1.72) / 2 + r * 1.055
    else:
        r = min(dw * 0.42, dh * 0.47)
        cx = (dx0 + dx1) / 2
        cy = dy0 + dh / 2
    sw = max(10.0, r * 0.11)
    vmin = float(p.get("min", 0))
    vmax = float(p.get("max", 100 if mode == "gauge" else float(p.get("hours", 24))))
    value, pre, suf, dec = M.split_num(p.get("value", vmax * 0.8 if mode == "gauge" else vmax))
    frac = (value - vmin) / max(1e-9, vmax - vmin)
    frac = max(0.0, min(1.0, frac))
    sx0 = cx - r - sw * 2
    sy0 = cy - r - sw * 2
    size = 2 * r + sw * 4
    lx = cx - sx0
    ly = cy - sy0
    parts = []
    mid_html = ""
    ro_html = ""
    build = "default"
    if mode == "gauge":
        a0 = -120.0
        a1 = 120.0
        av = a0 + (a1 - a0) * frac
        # the gauge's build changes with the style, not only its colours:
        # line (hud / screen): hairline track, dense ticks with numbers, thin needle, a readout row
        # wedge (poster / pixel): a solid sector that fills from the centre, a slab needle, no ticks
        # brush (ink / sketch): one loaded-brush stroke, roughened edges, three dots for ticks
        build = GAUGE_BUILD.get(sk["id"], "default")
        cap = "butt" if sk["r"] < 4 else "round"
        tick_n = 40
        tick_major = 10
        if build == "line":
            parts.append(f'<path class="trk" d="{_arc(lx, ly, r, a0, a1)}" style="stroke-width:2px"/>')
            parts.append(f'<path class="val" d="{_arc(lx, ly, r, a0, a1)}" pathLength="1" stroke-dasharray="{frac:.4f} 2" stroke-dashoffset="{frac:.4f}" style="stroke-width:7px; stroke-linecap:butt"/>')
            tick_n = 60
            tick_major = 6
        elif build == "wedge":
            parts.append(f'<path class="trk" d="{_arc(lx, ly, r * 0.5, a0, a1)}" style="stroke-width:{r:.1f}px; stroke-linecap:butt"/>')
            parts.append(f'<path class="val" d="{_arc(lx, ly, r * 0.5, a0, a1)}" pathLength="1" stroke-dasharray="{frac:.4f} 2" stroke-dashoffset="{frac:.4f}" style="stroke-width:{r:.1f}px; stroke-linecap:butt"/>')
            tick_n = 0
        elif build == "brush":
            brush_svg, bid = M.brush_filter(cid, 10)
            parts.append(brush_svg.replace('<svg width="0" height="0" style="position:absolute">', "").replace("</svg>", ""))
            parts.append(f'<g style="filter:url(#{bid})"><path class="trk" d="{_arc(lx, ly, r, a0, a1)}" style="stroke-width:{sw * 1.6:.1f}px; stroke-linecap:round"/>'
                         f'<path class="val" d="{_arc(lx, ly, r, a0, a1)}" pathLength="1" stroke-dasharray="{frac:.4f} 2" stroke-dashoffset="{frac:.4f}" style="stroke-width:{sw * 1.6:.1f}px; stroke-linecap:round"/></g>')
            tick_n = 0
        else:
            parts.append(f'<path class="trk" d="{_arc(lx, ly, r, a0, a1)}" style="stroke-width:{sw:.1f}px; stroke-linecap:{cap}"/>')
            parts.append(f'<path class="val" d="{_arc(lx, ly, r, a0, a1)}" pathLength="1" stroke-dasharray="{frac:.4f} 2" stroke-dashoffset="{frac:.4f}" style="stroke-width:{sw:.1f}px; stroke-linecap:{cap}"/>')
        ticks = ""
        tick_px = max(18, r * 0.07)
        for k in range(0, tick_n + 1 if tick_n else 0):
            a = a0 + (a1 - a0) * k / tick_n
            major = k % tick_major == 0
            if build == "line":
                r_in = r - (r * 0.12 if major else r * 0.06)
                r_out = r - 8
            else:
                r_in = r - sw * (1.9 if major else 1.4)
                r_out = r - sw * 0.95
            x0 = lx + r_in * math.sin(math.radians(a))
            y0 = ly - r_in * math.cos(math.radians(a))
            x1 = lx + r_out * math.sin(math.radians(a))
            y1 = ly - r_out * math.cos(math.radians(a))
            cls = "tk" if major else "tk mn"
            wpx = 2 if build == "line" else (3 if major else 2)
            ticks += f'<line class="{cls}" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" style="stroke-width:{wpx}px"/>'
            if build == "line" and major:
                rt = r - r * 0.22
                tx_ = lx + rt * math.sin(math.radians(a))
                ty_ = ly - rt * math.cos(math.radians(a)) + tick_px * 0.35
                tv = vmin + (vmax - vmin) * k / tick_n
                ticks += f'<text class="tl tn" x="{tx_:.1f}" y="{ty_:.1f}" text-anchor="middle" style="font-size:{tick_px:.0f}px">{tv:g}</text>'
        if build == "brush":
            for a in (a0, 0.0, a1):
                rr_ = r - sw * 1.8
                ticks += f'<circle class="dotk" cx="{lx + rr_ * math.sin(math.radians(a)):.1f}" cy="{ly - rr_ * math.cos(math.radians(a)):.1f}" r="{max(4, sw * 0.28):.1f}"/>'
        parts.append(f'<g class="ticks">{ticks}</g>')
        lo = p.get("lo", "低")
        hi = p.get("hi", "高")
        tl_px = max(22, r * 0.11)
        X.used_text.update(str(lo) + str(hi) + "0123456789.")
        lo_x = lx + (r + sw * 0.2) * math.sin(math.radians(a0))
        lo_y = ly - (r + sw * 0.2) * math.cos(math.radians(a0)) + tl_px * 1.7
        hi_x = lx + (r + sw * 0.2) * math.sin(math.radians(a1))
        if build != "line":
            parts.append(f'<text class="tl" x="{lo_x:.1f}" y="{lo_y:.1f}" text-anchor="middle" style="font-size:{tl_px:.0f}px">{X.rich(lo)}</text>')
            parts.append(f'<text class="tl" x="{hi_x:.1f}" y="{lo_y:.1f}" text-anchor="middle" style="font-size:{tl_px:.0f}px">{X.rich(hi)}</text>')
        nl = r * 0.7
        nw = max(5.0, r * 0.045)
        if build == "line":
            nl = r * 0.86
            parts.append(f'<g class="ndg"><line class="ndln" x1="{lx:.1f}" y1="{ly + r * 0.08:.1f}" x2="{lx:.1f}" y2="{ly - nl:.1f}" style="stroke-width:3px"/></g>')
            parts.append(f'<circle class="hubr" cx="{lx:.1f}" cy="{ly:.1f}" r="{max(10, r * 0.05):.1f}"/>')
        elif build == "wedge":
            nb = max(10.0, r * 0.06)
            parts.append(f'<g class="ndg"><rect class="ndl" x="{lx - nb / 2:.1f}" y="{ly - r * 1.08:.1f}" width="{nb:.1f}" height="{r * 1.08:.1f}"/></g>')
            parts.append(f'<rect class="hub" x="{lx - nb * 1.4:.1f}" y="{ly - nb * 1.4:.1f}" width="{nb * 2.8:.1f}" height="{nb * 2.8:.1f}"/>')
        else:
            parts.append(f'<g class="ndg">'
                         f'<path class="ndl" d="M{lx - nw:.1f},{ly:.1f} L{lx:.1f},{ly - nl:.1f} L{lx + nw:.1f},{ly:.1f} Z"/></g>')
            parts.append(f'<circle class="hub" cx="{lx:.1f}" cy="{ly:.1f}" r="{max(10, r * 0.07):.1f}"/>')
        if p.get("show_value", True):
            v_px = r * 0.3
            mid_cls = "dl-mid mt-k" + (" on-wedge" if build == "wedge" else "")
            mid_html = (f'<div class="{mid_cls}" style="left:{cx:.0f}px; top:{cy + r * 0.5:.0f}px; font-size:{v_px:.0f}px">'
                        f'{X.rich(pre)}<span class="n">0</span><small>{X.rich(suf or p.get("unit", ""))}</small></div>')
            X.used_text.update(str(p.get("unit", "")))
        if build == "line":
            X.used_text.update("MIN MAX VAL 0123456789.%")
            ro_html = (f'<div class="dl-ro" style="left:{cx:.0f}px; top:{cy + r * 0.72:.0f}px">'
                       f'MIN<b>{vmin:g}</b>MAX<b>{vmax:g}</b>VAL<b>{value:g}</b></div>')
    else:
        hours = int(p.get("hours", 24))
        parts.append(f'<circle class="face" cx="{lx:.1f}" cy="{ly:.1f}" r="{r + sw * 1.2:.1f}" style="stroke-width:{max(3, sw * 0.35):.1f}px"/>')
        parts.append(f'<circle class="trk" cx="{lx:.1f}" cy="{ly:.1f}" r="{r * 0.78:.1f}" style="stroke-width:{sw * 1.3:.1f}px"/>')
        circ_d = _arc(lx, ly, r * 0.78, 0, 359.9)
        parts.append(f'<path class="val" d="{circ_d}" pathLength="1" stroke-dasharray="{frac:.4f} 2" stroke-dashoffset="{frac:.4f}" style="stroke-width:{sw * 1.3:.1f}px"/>')
        ticks = ""
        for k in range(hours):
            a = 360.0 * k / hours
            major = k % (6 if hours == 24 else (3 if hours == 12 else 5)) == 0
            r_in = r + sw * (0.15 if major else 0.45)
            r_out = r + sw * 0.95
            x0 = lx + r_in * math.sin(math.radians(a))
            y0 = ly - r_in * math.cos(math.radians(a))
            x1 = lx + r_out * math.sin(math.radians(a))
            y1 = ly - r_out * math.cos(math.radians(a))
            cls = "tk" if major else "tk mn"
            ticks += f'<line class="{cls}" x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" style="stroke-width:{4 if major else 2}px"/>'
        parts.append(f'<g class="ticks">{ticks}</g>')
        parts.append(f'<circle class="hub" cx="{lx:.1f}" cy="{ly:.1f}" r="{max(8, r * 0.05):.1f}"/>')
        parts.append(f'<g class="hdg">'
                     f'<line class="hand" x1="{lx:.1f}" y1="{ly + r * 0.12:.1f}" x2="{lx:.1f}" y2="{ly - r * 0.94:.1f}" style="stroke-width:{max(4, sw * 0.32):.1f}px"/></g>')
        unit = p.get("unit", "h" if hours != 60 else "min")
        v_px = r * 0.4
        X.used_text.update(str(unit))
        # the figure sits on a plate above the hand layer, below the hub, so the hand never runs over it
        mid_html = (f'<div class="dl-mid mt-k on-face" style="left:{cx:.0f}px; top:{cy + r * 0.4:.0f}px; font-size:{v_px:.0f}px">'
                    f'{X.rich(pre)}<span class="n">0</span><small>{X.rich(unit)}</small></div>')
    svg = f'<svg class="dl-g {mode}" style="left:{sx0:.0f}px; top:{sy0:.0f}px" width="{size:.0f}" height="{size:.0f}">{"".join(parts)}</svg>'
    lab_html = ""
    if lab:
        l_w = dw
        if mode == "gauge":
            l_w = min(dw, r * 1.35)            # between the two end labels
        l_lines_max = 2 if mode == "gauge" else 1
        l_px, l_lines, _ = M.fit_text(X, lab, l_w, lab_h * 1.2, 60 if P else 54, 26, l_lines_max)
        g_low = r * 0.65 + 18 if p.get("show_value", True) else r * 0.45
        if ro_html:
            g_low += 40
        l_top = (cy + g_low) if mode == "gauge" else (cy + r + sw * 1.2 + 26)
        l_top = min(l_top, dy1 - l_px * 1.2)
        l_left = cx - l_w / 2
        if lab_box:
            l_w = lab_box[2] - lab_box[0]
            l_px, l_lines, _ = M.fit_text(X, lab, l_w, lab_box[3] - lab_box[1], 64, 26, 2)
            l_top = lab_box[1]
            l_left = lab_box[0]
        plate = " plate" if p.get("daynight") else ""
        lab_html = f'<div class="dl-lab mt-t{plate}{" left" if lab_box else ""}" style="left:{l_left:.0f}px; top:{l_top:.0f}px; width:{l_w:.0f}px; font-size:{l_px:.0f}px">{l_lines}</div>'
    # icon (+ the note dropping into it)
    ico_html = ""
    if ibox:
        ix0, iy0, ix1, iy1 = ibox
        isz = min(ix1 - ix0, iy1 - iy0) * (0.85 if lab_box else 0.62)
        icx = (ix0 + ix1) / 2
        icy = (iy0 + iy1) / 2 + isz * 0.1
        body = ICONS.get(icon)
        if body is None:
            svg_i = W3.icon_svg(icon, "w3ic")
        else:
            svg_i = f'<svg viewBox="0 0 24 24">{body}</svg>'
        ico_html = (f'<div class="dl-ico" style="left:{icx - isz / 2:.0f}px; top:{icy - isz / 2:.0f}px; width:{isz:.0f}px; height:{isz:.0f}px; '
                    f'stroke-width:{max(1.2, 30 / isz * 1.6):.2f}px">{svg_i}</div>')
        if p.get("note"):
            X.used_text.update(str(p["note"]))
            ico_html += f'<div class="mt-pill acc dl-note" style="left:{icx:.0f}px; top:{icy - isz * 0.25:.0f}px">{X.rich(p["note"])}</div>'
    stamp_html = ""
    if mode == "clock" and p.get("stamp", "处理好 ✓"):
        st = p.get("stamp", "处理好 ✓")
        X.used_text.update(st)
        st_px = max(34, min(r * 0.2, dw / max(2, len(st)) * 0.7))
        # the stamp lands on the upper-right rim, clear of the figure, the label and the subject card
        stamp_html = f'<div class="dl-stamp" style="left:{cx + r * 0.58:.0f}px; top:{cy - r * 0.72:.0f}px; font-size:{st_px:.0f}px">{X.rich(st)}</div>'
    sky = ""
    sky_h = 0
    if p.get("daynight"):
        skw = X.W
        sky_h = X.H
        sun = min(skw, sky_h) * 0.1
        from h9.aefx import _lum
        bg_lum = _lum(M.colors(X, p)["bg"])
        if bg_lum is None:
            bg_lum = 1.0
        dark_page = bg_lum < 0.2
        sky = (f'<div class="dl-sky{" dk" if dark_page else ""}" style="left:0; top:0; width:{skw}px; height:{sky_h}px; border-radius:0; box-shadow:none"><div class="day"></div><div class="night"></div>'
               f'<i class="sun" style="left:{skw * 0.76:.0f}px; top:{sky_h * 0.1:.0f}px; width:{sun:.0f}px; height:{sun:.0f}px"></i>'
               f'<i class="moon" style="left:{skw * 0.1:.0f}px; top:{sky_h * 0.14:.0f}px; width:{sun * 0.8:.0f}px; height:{sun * 0.8:.0f}px"></i></div>')
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=t + 0.25)
    mock = M.mock_tag(X, p, gx1 - 80, gy0)
    _clip(X, cid, t, d, M.wrap(X, sk, sky + svg + mid_html + ro_html + lab_html + ico_html + stamp_html + subj + mock, "dl"), p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    t0 = t + 0.05
    if ibox:
        X.tw(f'tl.from("{s} .dl-ico", {{y:-120, opacity:0, duration:0.55, ease:"bounce.out"}}, {t0:.3f});')
        X.sfx(t0 + 0.3, "pop")
        if p.get("note"):
            X.tw(f'tl.set("{s} .dl-note", {{xPercent:-50}}, 0);')   # centring through GSAP, so its y / scale tweens keep it
            X.tw(f'tl.fromTo("{s} .dl-note", {{y:-260, opacity:0, rotation:-12}}, {{y:-40, opacity:1, rotation:4, duration:0.5, ease:"power2.in"}}, {t0 + 0.45:.3f});')
            X.tw(f'tl.to("{s} .dl-note", {{y:30, opacity:0, scale:0.7, duration:0.3, ease:"power2.in"}}, {t0 + 1.0:.3f});')
            X.tw(f'tl.fromTo("{s} .dl-ico", {{scale:1}}, {{keyframes:[{{scale:1.12, scaleY:0.9, duration:0.1}}, {{scale:1, scaleY:1, duration:0.3, ease:"back.out(3)"}}], immediateRender:false}}, {t0 + 1.12:.3f});')
            X.sfx(t0 + 1.12, "click")
        t0 = t0 + (0.9 if not p.get("note") else 1.25)
    # the dial arrives
    X.tw(f'tl.from("{s} .dl-g", {{scale:0.7, opacity:0, rotation:-20, transformOrigin:"50% 50%", duration:0.6, ease:"{e}"}}, {t0:.3f});')
    X.tw(f'tl.from("{s} .dl-g .tk", {{opacity:0, duration:0.18, stagger:{0.35 / 40:.4f}}}, {t0 + 0.1:.3f});')
    X.sfx(t0, "whoosh_soft")
    t_run = t0 + 0.5
    run = min(2.2, max(1.0, (t + d - t_run) * 0.5))
    if mode == "gauge":
        run = min(run, 1.15)
    if mode == "gauge":
        X.tw(f'tl.fromTo("{s} .val", {{strokeDashoffset:{frac:.4f}}}, {{strokeDashoffset:0, duration:{run:.2f}, ease:"power2.inOut"}}, {t_run:.3f});')
        a_v = -120 + 240 * frac
        X.tw(f'tl.set("{s} .ndg", {{rotation:-120, svgOrigin:"{lx:.1f} {ly:.1f}"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{s} .ndg", {{rotation:-120, svgOrigin:"{lx:.1f} {ly:.1f}"}}, {{rotation:{a_v:.1f}, svgOrigin:"{lx:.1f} {ly:.1f}", duration:{run:.2f}, ease:"back.out(1.4)", immediateRender:false}}, {t_run:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .val", {{strokeDashoffset:{frac:.4f}}}, {{strokeDashoffset:0, duration:{run:.2f}, ease:"power1.inOut"}}, {t_run:.3f});')
        X.tw(f'tl.fromTo("{s} .hdg", {{rotation:0, svgOrigin:"{lx:.1f} {ly:.1f}"}}, {{rotation:{360 * frac:.1f}, svgOrigin:"{lx:.1f} {ly:.1f}", duration:{run:.2f}, ease:"power1.inOut"}}, {t_run:.3f});')
    if mid_html:
        W3.count(X, f"{s} .dl-mid .n", t_run, value, dur=run, dec=dec, ease="power1.inOut" if mode == "clock" else "power2.inOut")
        X.tw(f'tl.from("{s} .dl-mid", {{opacity:0, duration:0.3}}, {t_run - 0.2:.3f});')
    X.sfx(t_run, "count")
    t_end = t_run + run
    if ro_html:
        X.tw(f'tl.from("{s} .dl-ro", {{opacity:0, y:10, duration:0.4, ease:"{e}"}}, {t_run + 0.2:.3f});')
    if lab:
        X.tw(f'tl.from("{s} .dl-lab .fl", {{yPercent:90, opacity:0, duration:0.5, ease:"{e}"}}, {t_run + 0.3:.3f});')
    if stamp_html:
        X.tw(f'tl.fromTo("{s} .dl-stamp", {{scale:2.6, opacity:0}}, {{scale:1, opacity:1, duration:0.32, ease:"power4.in"}}, {t_end + 0.05:.3f});')
        X.tw(f'tl.fromTo("{s} .dl-g", {{x:0}}, {{keyframes:[{{x:-7, duration:0.06}}, {{x:5, duration:0.06}}, {{x:0, duration:0.12}}], immediateRender:false}}, {t_end + 0.37:.3f});')
        X.sfx(t_end + 0.36, "slam")
    else:
        X.tw(f'tl.fromTo("{s} .dl-g", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.1}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], transformOrigin:"50% 50%", immediateRender:false}}, {t_end:.3f});')
        X.sfx(t_end, "hit")
    if p.get("daynight"):
        X.tw(f'tl.to("{s} .dl-sky .night", {{opacity:1, duration:{run:.2f}, ease:"power1.inOut"}}, {t_run:.3f});')
        X.tw(f'tl.to("{s} .dl-sky .day", {{opacity:0, duration:{run:.2f}, ease:"power1.inOut"}}, {t_run:.3f});')
        X.tw(f'tl.to("{s} .dl-sky .sun", {{y:{sky_h * 0.9:.0f}, duration:{run:.2f}, ease:"power1.in"}}, {t_run:.3f});')
        if p.get("line") and not dark_page:
            # the page around the effect (header, caption) flips to light-on-dark as night falls, so it stays readable
            X.tw(f'tl.to("#{cid}c", {{"--fg":"#f3efe6", "--muted":"#b8b2a8", "--bg":"#11141c", duration:{run * 0.5:.2f}, ease:"power1.inOut"}}, {t_run + run * 0.3:.3f});')
        X.tw(f'tl.to("{s} .dl-sky .moon", {{opacity:1, y:-{sky_h * 0.06:.0f}, duration:{run * 0.6:.2f}, ease:"power1.out"}}, {t_run + run * 0.4:.3f});')


FX = {"dial": dial}
