"""象形单位图 Icon-unit chart (Pictogram Infographic Kit 759; VideoHive Infographic Maker 2.6K): a field of icons pops in
row by row, then the share lights up in the accent colour icon by icon while the big percentage counts; a legend
says what one icon stands for.

Adapts: total 4–1000 icons (grid columns from the count and the box; above ~400 the icons become dots), value as a
count or `share` (0–100); up to 4 groups ([[label, count], ...]) light in turn in different shades; any icon from the
built-in set (person, cup, store, car, phone, house, coin, box, globe, bolt, heart, chip) or an SVG path; labels
from a word to a sentence (fitted). Big totals: pass `per` (one icon = N units) or let it pick a round unit.
p: total · value | share | groups · icon · per · unit · text · sub · title · note · mock
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
SHADES = ["var(--accent)", "color-mix(in srgb, var(--accent) 55%, var(--fg))", "color-mix(in srgb, var(--accent) 45%, var(--bg))", "var(--fg)"]


def icon_unit(X, cid, t, d, p):
    W.base(X)
    total = int(W.num(p.get("total")) or 100)
    per = W.num(p.get("per")) or 1
    if total > 1000:
        per = per * math.ceil(total / 1000); total = math.ceil(total / per)
    groups = []
    if p.get("groups"):
        for g in p["groups"][:4]:
            groups.append((str(g[0]), max(0, int(round((W.num(g[1]) or 0) / per)))))
    elif p.get("share") is not None:
        groups.append((p.get("text", ""), int(round(total * float(p["share"]) / 100))))
    else:
        groups.append((p.get("text", ""), int(round((W.num(p.get("value")) or 0) / per))))
    lit = min(total, sum(c for _, c in groups))
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top0 = y0
    y0 += hhpx
    P = X.portrait
    valmode = p.get("value") is not None and p.get("share") is None and not p.get("groups")
    show = p.get("big") or (f"{W.num(p.get('value')):,.0f}" if valmode else None)
    big_suffix = p.get("big_unit", "%" if not valmode else p.get("unit", ""))
    per_lab = p.get("legend") or (f"1 个 = {W.fmt(per)} {p.get('unit', '')}".strip() if per != 1 or p.get("unit") else "")

    def text_h(tw, bs_max, ts_max):
        """text block size: big number, fitted text, sub, legend rows, per line -> (height, bs, ts, lines)."""
        bs = min(bs_max, tw / max(0.6, W.F.em((show or "100") + big_suffix) * 0.62))
        ts, tl = W.fit_px(X, p.get("text", groups[0][0] if groups else ""), tw, ts_max * 3.2, ts_max, 26, 3)
        h = bs * 1.02 + 18 + ts * 1.18 * len(tl)
        if p.get("sub"): h += 12 + 24 * 1.45 * math.ceil(W.F.em(p["sub"]) * 24 / tw)
        if len(groups) > 1: h += len(groups) * (26 * 1.25 + 12)
        if per_lab: h += 22 + 30
        return h, bs, ts, tl
    # grid box vs text box (9:16: the text block is measured first and the grid takes what is left)
    if P:
        th_, bs, ts, tl = text_h(x1 - x0, 190, 50)
        if th_ > (y1 - y0) * 0.5: th_, bs, ts, tl = text_h(x1 - x0, 130, 40)
        gy1 = max(y0 + (y1 - y0) * 0.38, y1 - th_ - 30)
        gx0, gy0, gx1 = x0, y0, x1; tx0, ty0, tx1, ty1 = x0, gy1 + 30, x1, y1
    else:
        gx0, gy0, gx1, gy1 = x0, y0, x0 + (x1 - x0) * 0.55, y1; tx0, ty0, tx1, ty1 = gx1 + 70, y0, x1, y1
        th_, bs, ts, tl = text_h(tx1 - tx0, 220, 54)
        if th_ > ty1 - ty0: th_, bs, ts, tl = text_h(tx1 - tx0, 150, 40)
    gw, gh = gx1 - gx0, gy1 - gy0
    cols, rows, cell = W.best_grid(total, gw, gh)
    dots = total > 400 or cell < 14
    gx = gx0 + (gw - cell * cols) / 2; gy = gy0 + (gh - cell * rows) / 2
    shade_of = []
    for gi, (_, c) in enumerate(groups): shade_of += [gi] * c
    icon = p.get("icon", "person")
    cells = []
    for i in range(total):
        r, c = divmod(i, cols)
        g = shade_of[i] if i < len(shade_of) else -1
        x, y = gx + c * cell, gy + r * cell
        inner = '<i class="iud"></i>' if dots else W.icon_svg(icon, "iui")
        cells.append(f'<div class="iuc{" on" if g >= 0 else ""}" data-i="{i}" data-g="{g}" style="left:{x:.1f}px; top:{y:.1f}px; width:{cell:.1f}px; height:{cell:.1f}px">{inner}</div>')
    pct = lit / total * 100 if total else 0
    show = show or f"{pct:.0f}"
    tw = tx1 - tx0
    legend = ""
    if len(groups) > 1:
        legend = "".join(f'<div class="iulg" data-g="{gi}"><i style="background:{SHADES[gi % 4]}"></i>{X.rich(lab)}<b>{W.fmt(c * per)}</b></div>' for gi, (lab, c) in enumerate(groups))
    X.css("fx-iu", """
.fx .iu .iuc { position:absolute; display:grid; place-items:center; }
.fx .iu .iuc .iui { width:78%; height:78%; fill:color-mix(in srgb, var(--fg) 16%, transparent); stroke:none; }
.fx .iu .iuc .iud { width:62%; height:62%; border-radius:50%; background:color-mix(in srgb, var(--fg) 16%, transparent); }
.fx .iu .iut { position:absolute; }
.fx .iu .iub { display:flex; align-items:flex-end; gap:6px; color:var(--accent); }
.fx .iu .iub small { font-size:.38em; color:var(--fg); padding-bottom:.12em; }
.fx .iu .iutx { margin-top:18px; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.18; }
.fx .iu .iutx .fl { display:block; white-space:nowrap; }
.fx .iu .iusub { margin-top:12px; font:500 24px/1.45 var(--f-body); color:var(--muted); }
.fx .iu .iuper { margin-top:22px; display:inline-flex; align-items:center; gap:10px; font:700 20px var(--f-mono, monospace); color:var(--muted); }
.fx .iu .iuper svg { width:26px; height:26px; fill:var(--accent); }
.fx .iu .iulg { display:flex; align-items:center; gap:12px; margin-top:12px; font:700 26px var(--f-body); color:var(--fg); white-space:nowrap; }
.fx .iu .iulg i { width:18px; height:18px; border-radius:3px; flex:none; } .fx .iu .iulg b { margin-left:auto; padding-left:18px; font-family:var(--f-num, var(--f-display)); }
""")
    tblock = (f'<div class="iut" style="left:{tx0}px; top:{ty0 + (0 if P else max(0, min((ty1 - ty0) * 0.18, (ty1 - ty0 - th_) / 2))):.0f}px; width:{tw}px">'
              f'<div class="iub w3k" style="font-size:{bs:.0f}px"><span class="n">0</span><small>{X.rich(big_suffix)}</small></div>'
              f'<div class="iutx" style="font-size:{ts:.0f}px">{W.lines_html(X, tl)}</div>'
              + (f'<div class="iusub">{X.rich(p["sub"])}</div>' if p.get("sub") else "")
              + legend
              + (f'<div class="iuper">{"<i style=width:22px;height:22px;border-radius:50%;background:var(--accent);display:inline-block></i>" if dots else W.icon_svg(icon)}{X.rich(per_lab)}</div>' if per_lab else "")
              + '</div>')
    inner = f'<div class="w3 iu">{hh}{"".join(cells)}{tblock}{W.mock_tag(X, p, x1 - 70, top0)}</div>'
    X.used_text.update(show + big_suffix + "0123456789,")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    pop = min(1.2, d * 0.25)
    X.tw(f'tl.from("{s} .iuc", {{scale:0, opacity:0, duration:0.32, ease:"back.out(2.4)", stagger:{{grid:[{rows},{cols}], from:[0,0], amount:{pop:.2f}}}}}, {t + 0.15:.3f});')
    t_lit = t + 0.25 + pop
    lit_dur = min(1.6, max(0.6, d * 0.35))
    X.tw(f'tl.from("{s} .iut", {{x:{0 if P else 40}, y:{30 if P else 0}, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.3:.3f});')
    if lit:
        each = lit_dur / max(lit, 1)
        X.tw(f'tl.fromTo("{s} .iuc.on", {{"--lit":0}}, {{"--lit":1, duration:0.14, ease:"none", stagger:{{each:{each:.4f}}}}}, {t_lit:.3f});')
        X.css(f"fx-iu-lit-{cid}"," ".join(f'#{cid} .iu .iuc[data-g="{gi}"] .iui {{ fill:color-mix(in srgb, {SHADES[gi % 4]} calc(var(--lit, 0) * 100%), color-mix(in srgb, var(--fg) 16%, transparent)); }} '
                                           f'#{cid} .iu .iuc[data-g="{gi}"] .iud {{ background:color-mix(in srgb, {SHADES[gi % 4]} calc(var(--lit, 0) * 100%), color-mix(in srgb, var(--fg) 16%, transparent)); }}' for gi in range(len(groups))))
        X.tw(f'tl.fromTo("{s} .iuc.on", {{scale:1}}, {{keyframes:[{{scale:1.25, duration:0.1}}, {{scale:1, duration:0.25, ease:"back.out(3)"}}], stagger:{{each:{each:.4f}}}, immediateRender:false}}, {t_lit:.3f});')
        X.sfx(t_lit, "count")
    target = W.num(p.get("big")) if p.get("big") else (W.num(p.get("value")) if (p.get("value") is not None and p.get("share") is None and not p.get("groups")) else pct)
    W.count(X, f"{s} .iub .n", t_lit, target or 0, dur=lit_dur, dec=0)
    if p.get("sub"): X.tw(f'tl.from("{s} .iusub", {{opacity:0, y:14, duration:0.4}}, {t + 0.6:.3f});')
    if '"iulg' in inner or '"iuper' in inner:
        X.tw(f'tl.from("{s} .iulg, {s} .iuper", {{opacity:0, y:14, duration:0.4, stagger:0.1}}, {t_lit + lit_dur * 0.5:.3f});')


FX = {"icon_unit": icon_unit}
