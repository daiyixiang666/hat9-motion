"""堆叠柱状图 Stacked Bars (D2, VideoHive Infographic Maker 2.6K / Infographics (Holypix) 2.2K; SonduckFilm「Bar Infographics
with Controls」23.2 万播放): each category's column builds segment by segment from the baseline — every series in its
own shade, values printed inside segments that are tall enough — the totals count on top, then one series is pulled
forward (the others fade) and its share labels light up.

Adapts: 2–12 categories (vertical; horizontal rows when there are many or the labels are long, or "orient": "h"),
2–6 series, "percent": true for 100 % stacks, huge values (auto 万 / 亿 or "unit"), labels fitted. Data from
"labels" + "series" or a wide spreadsheet ("csv": first column the category, one column per series; "series_cols"
picks / orders them).
p: labels · series {name: [values]} | csv/x/series_cols · hl (series name) · percent · unit · dec · title · note · orient ·
total_col (csv column printed as the total) | totals [..]
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

SHADE = ["var(--fg)", "var(--accent)", "color-mix(in srgb, var(--fg) 42%, var(--card))", "color-mix(in srgb, var(--accent) 42%, var(--card))",
         "color-mix(in srgb, var(--fg) 18%, var(--card))", "color-mix(in srgb, var(--accent) 70%, var(--fg))"]
INK = ["var(--bg)", "var(--bg)", "var(--card)", "var(--card-fg)", "var(--card-fg)", "var(--bg)"]

CSS = """
.fx .dtk { position:absolute; }
.fx .dtk .dtk-tt { position:absolute; left:0; top:0; font:900 4.2vmin/1.15 var(--f-display); color:var(--fg); white-space:nowrap; }
.fx .dtk .dtk-tt small { display:block; font:500 1.9vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; margin-top:.8vmin; }
.fx .dtk .dtk-lg { position:absolute; display:flex; flex-wrap:wrap; gap:1vmin 2.6vmin; }
.fx .dtk .dtk-lg span { display:flex; align-items:center; gap:.9vmin; font:700 2.6vmin var(--f-body); color:var(--fg); white-space:nowrap; }
.fx .dtk .dtk-lg i { width:2vmin; height:2vmin; border-radius:.3vmin; display:block; }
.fx .dtk .dtk-z { position:absolute; background:var(--fg); }
.fx .dtk .dtk-s { position:absolute; display:flex; align-items:center; justify-content:center; overflow:hidden; }
.fx .dtk .dtk-s b { font-family:var(--f-num, var(--f-display)); font-weight:800; white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .dtk .dtk-t { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; color:var(--fg); white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .dtk .dtk-t small { font-size:.5em; color:var(--muted); margin-left:.12em; }
.fx .dtk .dtk-l { position:absolute; font-family:var(--f-body); font-weight:700; line-height:1.15; color:var(--muted); }
.fx .dtk .dtk-l .fl { display:block; white-space:nowrap; }
"""


def stacked_bars(X, cid, t, d, p):
    labels, ser = U.wide_of(p, X)
    ser = ser[:6] or [("—", [0.0])]
    n = max(len(labels), max(len(v) for _, v in ser))
    labels = (list(labels) + [""] * n)[:n]
    ser = [(nm, [max(0.0, (vs[k] if k < len(vs) else 0.0) or 0.0) for k in range(n)]) for nm, vs in ser]
    S = len(ser)
    pct = bool(p.get("percent"))
    totals = [sum(vs[k] for _, vs in ser) for k in range(n)]
    shown_tot = list(totals)
    if p.get("total_col") and p.get("csv"):        # print the official total (may include series not drawn)
        _, allc = U.D.wide(p["csv"], p.get("x", 0), [p["total_col"]], base=X.src)
        shown_tot = (list(allc.values())[0] + totals)[:n]
    elif p.get("totals"): shown_tot = ([float(x) for x in p["totals"]] + totals)[:n]
    if p.get("unit") is None:
        div, unit = U.compact(totals, p.get("compact", "cn"))
    else:
        div, unit = 1, p.get("unit", "")
    dec = int(p.get("dec", U.decimals([v for _, vs in ser for v in vs] + totals, div)))
    hl = p.get("hl")
    hi_ = max(1.0 if pct else max(totals) or 1, 1e-9)
    bx, by, bw, bh = U.box(X)
    title, note = p.get("title", ""), p.get("note", "")
    head_h = (9.5 if note else 7.0) if title else 0
    lg_h = 4.0
    max_lab = max(U.em(l) for l in labels)
    horiz = p.get("orient") == "h" or (p.get("orient") != "v" and (n > (6 if X.portrait else 10) or (max_lab > 5 and n > 4)))
    X.css("fx-dtk", CSS)
    html = []
    if title: html.append(f'<div class="dtk-tt">{X.rich(title)}{"<small>" + X.rich(note) + "</small>" if note else ""}</div>')
    html.append(f'<div class="dtk-lg" style="left:0; right:0; top:{head_h:.2f}vmin">' + "".join(
        f'<span data-s="{j}"><i style="background:{SHADE[j]}"></i>{X.rich(nm)}</span>' for j, (nm, _) in enumerate(ser)) + "</div>")
    py = head_h + lg_h + 4.5
    ph = bh - py
    segs = []
    tstr = max((U.fmt(x, dec, div) for x in totals), key=U.em) + unit
    if not horiz:
        lab_h = 6.0
        ph -= lab_h
        gap = 0.5 if n <= 5 else 0.32
        w = bw / (n + (n + 1) * gap)
        ts = min(3.8, w * 0.95 / max(U.em(tstr) * 0.9, 1))
        lab_size, _ = U.fit(max(labels, key=U.em), w * 1.3, lab_h - 1, 2.8, 1.3, 2)
        html.append(f'<i class="dtk-z" style="left:0; width:{bw:.2f}vmin; top:{py + ph:.2f}vmin; height:.35vmin"></i>')
        for k in range(n):
            x = gap * w * (k + 1) + w * k
            base = py + ph
            tot = 1.0 if pct else totals[k]
            for j, (nm, vs) in enumerate(ser):
                v = vs[k] / (totals[k] or 1) if pct else vs[k]
                hgt = v / hi_ * ph
                base -= hgt
                show = f"{v * 100:.0f}%" if pct else U.fmt(vs[k], dec, div)
                fs = min(2.4, w * 0.8 / max(U.em(show), 1), hgt * 0.62)
                lab = f'<b style="font-size:{fs:.2f}vmin; color:{INK[j]}">{show}</b>' if fs >= 2.0 else ""
                html.append(f'<div class="dtk-s" data-k="{k}" data-s="{j}" style="left:{x:.2f}vmin; width:{w:.2f}vmin; top:{base:.2f}vmin; height:{max(0.1, hgt):.2f}vmin; background:{SHADE[j]}; transform-origin:50% 100%">{lab}</div>')
                segs.append((k, j))
            if not pct:
                html.append(f'<div class="dtk-t" data-k="{k}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); top:{base - ts - 1:.2f}vmin; font-size:{ts:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            _, ll = U.fit(labels[k], w * 1.3, lab_h - 1, lab_size, lab_size, 2)
            html.append(f'<div class="dtk-l" data-k="{k}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); top:{py + ph + 1.4:.2f}vmin; font-size:{lab_size:.2f}vmin; text-align:center">{U.lines_html(X, ll)}</div>')
        axis, org = "scaleY", None
    else:
        rh = ph / n
        lab_w = min(bw * 0.28, max_lab * min(3.0, rh * 0.46) + 1.5)
        lab_size = min(3.0, rh * 0.46, (lab_w - 1.5) / max(max_lab, 1))
        ts = min(3.0, rh * 0.5)
        track = bw - lab_w - U.em(tstr) * ts - 3
        html.append(f'<i class="dtk-z" style="left:{lab_w + 1:.2f}vmin; top:{py:.2f}vmin; height:{ph:.2f}vmin; width:.35vmin"></i>')
        for k in range(n):
            y = py + rh * k + rh * 0.15
            hh = rh * 0.7
            x = lab_w + 1
            for j, (nm, vs) in enumerate(ser):
                v = vs[k] / (totals[k] or 1) if pct else vs[k]
                ww = v / hi_ * track
                show = f"{v * 100:.0f}%" if pct else U.fmt(vs[k], dec, div)
                fs = min(2.2, hh * 0.55, ww * 0.85 / max(U.em(show), 1))
                lab = f'<b style="font-size:{fs:.2f}vmin; color:{INK[j]}">{show}</b>' if fs >= 2.0 else ""
                html.append(f'<div class="dtk-s" data-k="{k}" data-s="{j}" style="left:{x:.2f}vmin; width:{max(0.1, ww):.2f}vmin; top:{y:.2f}vmin; height:{hh:.2f}vmin; background:{SHADE[j]}; transform-origin:0 50%">{lab}</div>')
                x += ww
                segs.append((k, j))
            if not pct:
                html.append(f'<div class="dtk-t" data-k="{k}" style="left:{x + 1:.2f}vmin; top:{y + hh / 2 - ts / 2:.2f}vmin; font-size:{ts:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            html.append(f'<div class="dtk-l" data-k="{k}" style="left:0; width:{lab_w:.2f}vmin; top:{y + hh / 2 - lab_size * 0.6:.2f}vmin; font-size:{lab_size:.2f}vmin; text-align:right"><span class="fl">{X.rich(labels[k])}</span></div>')
        axis = "scaleX"
    X.used_text.update("0123456789.,%" + unit)
    inner = f'<div class="dtk" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin">{"".join(html)}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dtk-tt", {{y:24, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .dtk-lg span", {{y:12, opacity:0, duration:0.4, ease:"expo.out", stagger:0.08}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .dtk-z", {{{"scaleX" if not horiz else "scaleY"}:0, duration:0.45, ease:"expo.inOut"}}, {t + 0.1:.3f});')
    budget = max(1.0, min(d - 1.8, 0.45 * n + 0.6))
    stk = budget / n
    sd = min(0.4, stk * 0.9 / max(S, 1) + 0.12)
    for k in range(n):
        tk = t + 0.4 + k * stk
        X.tw(f'tl.from("{s} .dtk-l[data-k=\'{k}\']", {{opacity:0, y:8, duration:0.3}}, {tk:.3f});')
        for j in range(S):
            X.tw(f'tl.from("{s} .dtk-s[data-k=\'{k}\'][data-s=\'{j}\']", {{{axis}:0, duration:{sd:.2f}, ease:"power3.out"}}, {tk + j * sd * 0.7:.3f});')
        if not pct:
            X.tw(f'tl.from("{s} .dtk-t[data-k=\'{k}\']", {{opacity:0, duration:0.3}}, {tk:.3f});')
            U.count(X, f"{s} .dtk-t[data-k=\'{k}\'] .n", tk, 0, shown_tot[k] / div, sd * (S * 0.7 + 0.3), dec)
        X.sfx(tk, "tick")
    tb = t + 0.4 + n * stk + 0.3
    if hl is not None:
        hj = next((j for j, (nm, _) in enumerate(ser) if nm == hl), None)
        if hj is not None:
            th = max(tb, U.cue(X, p, "t_hl", t, tb))
            X.tw(f'tl.to("{s} .dtk-s:not([data-s=\'{hj}\']), {s} .dtk-lg span:not([data-s=\'{hj}\'])", {{opacity:0.25, duration:0.4}}, {th:.3f});')
            X.tw(f'tl.fromTo("{s} .dtk-s[data-s=\'{hj}\']", {{scale:1}}, {{keyframes:[{{scale:1.05, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {th:.3f});')
            X.tw(f'tl.fromTo("{s} .dtk-lg span[data-s=\'{hj}\']", {{scale:1}}, {{keyframes:[{{scale:1.2, duration:0.14}}, {{scale:1, duration:0.35}}], transformOrigin:"0 50%", immediateRender:false}}, {th:.3f});')
            X.sfx(th, "hit")
    X.tw(f'tl.fromTo("{s} .dtk", {{scale:0.985}}, {{scale:1.02, transformOrigin:"50% 70%", duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


FX = {"stacked_bars": stacked_bars}
