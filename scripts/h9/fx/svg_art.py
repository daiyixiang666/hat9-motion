"""SVG 矢量插画 (a vector illustration that stays sharp at any size and takes the page's colours): the SVG is inlined,
its colours become theme variables (darkest → ink, most saturated → accent, the rest kept or tinted), strokes draw
on, fills follow; optionally the palette swaps live to another theme mid-beat to show the art follows the theme.

p: svg (file) · recolor ("auto" | false | {"#hex": "fg" | "accent" | "bg" | "card" | "#hex"}) · draw (true) ·
   swap (a theme name: "ink" | "paper" | "red" | "lemon") · t_swap ("@词" / seconds) · title · caption
Adapts: any viewBox / aspect (contained in the box), hundreds of shapes (staggers are capped), gradients (stop colours
are mapped too); scripts, event handlers and external links are stripped. 16:9 and 9:16.
"""
import re
from h9 import fit
from h9.aefx import _clip, THEMES
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)

HEX = re.compile(r'(fill|stroke|stop-color)="(#[0-9a-fA-F]{3}|#[0-9a-fA-F]{6})"')


def _norm(h):
    h = h.lower()
    return "#" + "".join(c * 2 for c in h[1:]) if len(h) == 4 else h


def _sat_lum(h):
    r, g, b = [v / 255 for v in D.hexrgb(h)]
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn), (0.2126 * r + 0.7152 * g + 0.0722 * b)


def _clean(svg):
    svg = re.sub(r"<\?xml[^>]*>|<!DOCTYPE[^>]*>", "", svg)
    svg = re.sub(r"<script[\s\S]*?</script>", "", svg, flags=re.I)
    svg = re.sub(r'\son\w+="[^"]*"', "", svg)
    svg = re.sub(r'(xlink:)?href="(https?:|//)[^"]*"', "", svg)
    return svg


def svg_art(X, cid, t, d, p):
    src = p.get("svg") or p.get("src")
    if not src: raise SystemExit("svg_art needs `svg`")
    svg = _clean(fit._abs(X, src).read_text(encoding="utf-8"))
    uid = f"sv{cid}"
    svg = re.sub(r'id="([^"]+)"', lambda m: f'id="{uid}-{m.group(1)}"', svg)                  # ids unique per beat
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{uid}-{m.group(1)})', svg)
    cols = sorted({_norm(h) for _, h in HEX.findall(svg)})
    rc = p.get("recolor", "auto")
    mapping = {}
    if rc == "auto" and cols:
        dark = min(cols, key=lambda h: _sat_lum(h)[1])
        mapping[dark] = "var(--fg)"
        sat = [h for h in cols if _sat_lum(h)[0] > 0.45 and h != dark]
        if sat: mapping[max(sat, key=lambda h: _sat_lum(h)[0])] = "var(--accent)"
    elif isinstance(rc, dict):
        for k, v in rc.items():
            mapping[_norm(k)] = f"var(--{v})" if v in ("fg", "accent", "bg", "card", "muted") else v
    var_of = {h: f"--{uid}c{i}" for i, h in enumerate(cols)}

    def tag(m):
        s = m.group(0)
        if s.startswith("</") or s.startswith("<svg") or s.startswith("<!--"): return s
        styles = []
        def rep(mm):
            styles.append(f"{mm.group(1)}:var({var_of[_norm(mm.group(2))]})"); return ""
        s2 = HEX.sub(rep, s)
        name = re.match(r"<(\w+)", s2)
        el = name.group(1) if name else ""
        cls = []
        if el in ("path", "line", "polyline", "polygon", "circle", "ellipse", "rect"):
            stroked = re.search(r'stroke(?:-width)?="', s) or "stroke:" in "".join(styles)
            if stroked and 'stroke="none"' not in s: cls.append("sv-s")
            cls.append("sv-f")
            if stroked and "pathLength" not in s2: s2 = s2.replace(f"<{el}", f'<{el} pathLength="1"', 1)
        if styles:
            if 'style="' in s2: s2 = s2.replace('style="', f'style="{";".join(styles)};', 1)
            else: s2 = s2.replace(f"<{el}", f'<{el} style="{";".join(styles)}"', 1)
        if cls:
            if 'class="' in s2: s2 = s2.replace('class="', f'class="{" ".join(cls)} ', 1)
            else: s2 = s2.replace(f"<{el}", f'<{el} class="{" ".join(cls)}"', 1)
        return s2
    svg = re.sub(r"<[^>]+>", tag, svg)
    svg = re.sub(r"<svg\b", '<svg preserveAspectRatio="xMidYMid meet" style="width:100%; height:100%; overflow:visible"', svg, count=1)
    vb = re.search(r'viewBox="([\d.\-\s]+)"', svg)
    ar = 1.0
    if vb:
        v = [float(x) for x in vb.group(1).split()]
        if len(v) == 4 and v[3]: ar = v[2] / v[3]
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title, caption = fit.as_text(p.get("title")), fit.as_text(p.get("caption"))
    tf = D.C.fitted(X, title, bw * (0.95 if P else 0.42), 200 if not P else 110, 60 if not P else 54, 26, max_lines=3) if title else None
    cf = D.C.fitted(X, caption, bw * (0.95 if P else 0.42), 120, 34, 20, max_lines=3) if caption else None
    pad_sw = 0.16 if p.get("swap") else 0.0                         # room for the swap panel around the art
    if P:
        top = (tf.n * tf.px * 1.12 + 24) if tf else 0
        bot = (cf.n * cf.px * 1.3 + 24) if cf else 0
        aw, ah = bw, bh - top - bot
        sw = min(aw * (0.92 - pad_sw), ah * (1 - pad_sw) * ar); sh = sw / ar
        sx, sy = x0 + (bw - sw) / 2, y0 + top + (ah - sh) / 2
        tx, ty, cx_, cy_ = x0, y0, x0, y0 + top + ah + 16
    else:
        text_w = bw * 0.42 if (tf or cf) else 0
        aw, ah = bw - text_w - (40 if text_w else 0), bh
        sw = min(aw * (0.92 - pad_sw), ah * (0.92 - pad_sw) * ar); sh = sw / ar
        sx, sy = x0 + (aw - sw) / 2, y0 + (ah - sh) / 2
        tblock = ((tf.n * tf.px * 1.12) if tf else 0) + ((cf.n * cf.px * 1.3 + 22) if cf else 0)
        tx = x0 + aw + 40; ty = y0 + (bh - tblock) / 2; cx_, cy_ = tx, ty + ((tf.n * tf.px * 1.12 + 22) if tf else 0)
    base = {h: mapping.get(h, h) for h in cols}
    varcss = ";".join(f"{var_of[h]}:{base[h]}" for h in cols)
    swap = THEMES.get(p.get("swap")) if p.get("swap") else None
    X.used_text.update(title + caption)
    head = (f'<div class="d2-ttl sv-ttl" style="left:{tx:.0f}px; top:{ty:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else "")
    cap = (f'<div class="sv-cap" style="left:{cx_:.0f}px; top:{cy_:.0f}px; width:{(bw if P else bw * 0.42):.0f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>' if cf else "")
    art = f'<div class="sv-art" style="left:{sx:.1f}px; top:{sy:.1f}px; width:{sw:.1f}px; height:{sh:.1f}px; {varcss}">{svg}</div>'
    X.css("fx-d2", D.CSS)
    X.css("fx-svg", """
.sv-art { position:absolute; }
.sv-art .sv-s { stroke-dasharray:1 1; }
.sv-cap { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.3; }
.sv-swap { position:absolute; opacity:0; border-radius:22px; z-index:1; }
.sv-panel { position:absolute; border-radius:22px; background:var(--card); box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fg) 10%, transparent); }
.sv-art { z-index:2; }
""")
    pdx, pdy = sw * 0.07 + 20, sh * 0.06 + 20                    # the swap panel: a card behind the art, not the whole page
    swap_bg = (f'<i class="sv-swap" style="left:{sx - pdx:.0f}px; top:{sy - pdy:.0f}px; width:{sw + 2 * pdx:.0f}px; height:{sh + 2 * pdy:.0f}px; background:{swap["bg"]}"></i>'
               f'<i class="sv-panel" style="left:{sx - pdx:.0f}px; top:{sy - pdy:.0f}px; width:{sw + 2 * pdx:.0f}px; height:{sh + 2 * pdy:.0f}px"></i>') if swap else ""
    _clip(X, cid, t, d, f'<div class="d2 sv">{swap_bg}{art}{head}{cap}</div>', p)
    S = f"#{cid}"
    n_s = svg.count("sv-s"); n_f = svg.count("sv-f")
    if p.get("draw", True) and n_s:
        X.tw(f'tl.fromTo("{S} .sv-s", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.9, ease:"power2.inOut", stagger:{{amount:{min(1.0, 0.04 * n_s):.2f}}}}}, {t + 0.1:.3f});')
        X.tw(f'tl.from("{S} .sv-f", {{fillOpacity:0, duration:0.5, ease:"power2.out", stagger:{{amount:{min(0.8, 0.03 * n_f):.2f}}}}}, {t + 0.55:.3f});')
    else:
        X.tw(f'tl.from("{S} .sv-f", {{opacity:0, scale:0.92, transformOrigin:"50% 50%", duration:0.5, ease:"back.out(1.6)", stagger:{{amount:{min(0.9, 0.03 * n_f):.2f}}}}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{S} .sv-art", {{y:40, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    if tf: X.tw(f'tl.from("{S} .sv-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t + 0.2:.3f});')
    if cf: X.tw(f'tl.from("{S} .sv-cap", {{opacity:0, y:14, duration:0.5}}, {t + 0.45:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")
    if swap:
        ts = D.times(X, p, t, d, 1, key="t_swap", lead=d * 0.55)[0]
        tgt = {}
        for h in cols:
            m = mapping.get(h)
            if m == "var(--fg)": tgt[var_of[h]] = swap["fg"]
            elif m == "var(--accent)": tgt[var_of[h]] = swap["accent"]
        if tgt:
            props = ", ".join(f'"{k}":"{v}"' for k, v in tgt.items())
            X.tw(f'tl.to("{S} .sv-art", {{{props}, duration:0.6, ease:"power2.inOut"}}, {ts:.3f});')
        X.tw(f'tl.to("{S} .sv-swap", {{opacity:1, duration:0.6, ease:"power2.inOut"}}, {ts:.3f});')
        X.sfx(ts, "whoosh_soft")
    hold = t + 1.6
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .sv-art", {{y:-12, duration:{t + d - hold:.2f}, ease:"sine.inOut"}}, {hold:.3f});')


FX = {"svg_art": svg_art}
