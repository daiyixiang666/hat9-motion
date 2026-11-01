"""瀑布图 Waterfall Bridge (D2, VideoHive Infographic Maker 2.6K / Infographics (Holypix) 2.2K; Envato Popular「Bar Chart
Builder」; the standard 「从收入一路扣到净利」 chart of every 财报拆解): the first total grows from the baseline, then each
step falls (or climbs) from where the last one ended — a dashed connector carries the level across, the step's value
counts in, a running readout ticks to the new level — and the final total lands in the accent with a pop.

Adapts: 3–12+ steps (vertical bars; turns into a horizontal cascade when there are many steps or long labels, or with
"orient": "h"), positive and negative steps, subtotals ("sub") anywhere, totals that cross below zero, huge values
(auto 万 / 亿 unless "unit" is given), labels from 1 glyph to a phrase (fitted, 2 lines). Data from "steps" or a
spreadsheet ("csv" + "x" label column + "y" value column; the first row is the start, the last the total).
p: steps [[label, value, kind?], ...] (kind: start | delta | sub | end — default start…delta…end; an end/sub value
may be null and is computed) · unit · dec · title · note · readout (label of the running number) · orient · compact
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

CSS = """
.fx .dtw { position:absolute; }
.fx .dtw .dtw-cam { position:absolute; inset:0; }
.fx .dtw .dtw-tt { position:absolute; left:0; top:0; font:900 4.2vmin/1.15 var(--f-display); color:var(--fg); white-space:nowrap; }
.fx .dtw .dtw-tt small { display:block; font:500 1.9vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; margin-top:.8vmin; }
.fx .dtw .dtw-ro { position:absolute; right:0; top:0; text-align:right; }
.fx .dtw .dtw-ro span { display:block; font:700 1.9vmin var(--f-body); color:var(--muted); letter-spacing:.04em; }
.fx .dtw .dtw-ro b { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; color:var(--fg); font-variant-numeric:tabular-nums; }
.fx .dtw .dtw-ro b small { font-size:.45em; color:var(--muted); margin-left:.15em; }
.fx .dtw .dtw-plot { position:absolute; }
.fx .dtw .dtw-z { position:absolute; background:var(--fg); }
.fx .dtw .dtw-g { position:absolute; background:color-mix(in srgb, var(--fg) 10%, transparent); }
.fx .dtw .dtw-b { position:absolute; border-radius:.35vmin; }
.fx .dtw .dtw-b.tot { background:var(--fg); }
.fx .dtw .dtw-b.up { background:color-mix(in srgb, var(--fg) 38%, var(--bg)); }
.fx .dtw .dtw-b.dn { background:var(--accent); }
.fx .dtw .dtw-b.end { background:var(--fg); box-shadow:0 0 0 .5vmin var(--bg), 0 0 0 1vmin var(--accent); }
.fx .dtw .dtw-k { position:absolute; border-top:.3vmin dashed color-mix(in srgb, var(--fg) 55%, transparent); transform-origin:0 50%; }
.fx .dtw .dtw-k.h { border-top:0; border-left:.3vmin dashed color-mix(in srgb, var(--fg) 55%, transparent); transform-origin:50% 0; }
.fx .dtw .dtw-v { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:800; line-height:1; white-space:nowrap; color:var(--fg); font-variant-numeric:tabular-nums; }
.fx .dtw .dtw-v.dn { color:var(--accent); }
.fx .dtw .dtw-v small { font-size:.55em; color:var(--muted); margin-left:.1em; }
.fx .dtw .dtw-l { position:absolute; font-family:var(--f-body); font-weight:700; line-height:1.15; color:var(--muted); }
.fx .dtw .dtw-l .fl { display:block; white-space:nowrap; }
.fx .dtw .dtw-l.tot { color:var(--fg); font-weight:900; }
"""


def _steps(p, X):
    if p.get("csv"):           # keep blank cells: a blank last row is the computed total
        header, rows = U.D.read(p["csv"], X.src)
        xi, yi = U.D.column(header, p.get("x", 0)), U.D.column(header, p.get("y", 1))
        ki = next((i for i, h in enumerate(header) if h.lower() in ("kind", "类型")), None)
        raw = [[r[xi], U.D.num(r[yi]), (r[ki] or None) if ki is not None else None] for r in rows]
    else:
        raw = []
        for s in p.get("steps", []):
            if isinstance(s, dict): raw.append([s.get("label", ""), s.get("value"), s.get("kind")])
            else: raw.append(list(s) + [None] * (3 - len(s)))
    n = len(raw)
    out, level = [], 0.0
    for i, (lb, v, k) in enumerate(raw):
        k = k or ("start" if i == 0 else "end" if i == n - 1 and n > 2 else "delta")
        v = None if v in (None, "") else float(v)
        if k == "start":
            v = v or 0.0; lo, hi = 0.0, v; level = v
        elif k in ("sub", "end"):
            shown = level if v is None else v
            lo, hi = 0.0, level; v = shown
        else:
            v = v or 0.0; lo, hi = level, level + v; level += v
        out.append({"label": str(lb), "v": v, "kind": k, "lo": lo, "hi": hi, "level": level})
    return out


def waterfall(X, cid, t, d, p):
    st = _steps(p, X)
    if not st: st = [{"label": "—", "v": 0.0, "kind": "start", "lo": 0, "hi": 0, "level": 0}]
    n = len(st)
    allv = [s["lo"] for s in st] + [s["hi"] for s in st]
    if p.get("unit") is None:
        div, suf = U.compact([abs(s["v"]) for s in st] + [abs(x) for x in allv], p.get("compact", "cn"))
        unit = suf
    else:
        div, unit = 1, p.get("unit", "")
    dec = int(p.get("dec", U.decimals([s["v"] for s in st], div)))
    lo, hi = min(0.0, min(allv)), max(0.0, max(allv))
    span = (hi - lo) or 1
    hi += span * (0.14 if hi > 0 else 0); lo -= span * (0.14 if lo < 0 else 0)     # headroom for the value labels
    span = hi - lo
    bx, by, bw, bh = U.box(X)
    title, note = p.get("title", ""), p.get("note", "")
    head_h = (9.5 if note else 7.0) if (title or p.get("readout")) else 0
    max_lab = max(U.em(s["label"]) for s in st)
    horiz = p.get("orient") == "h" or (p.get("orient") != "v" and (n > (6 if X.portrait else 9) or (max_lab > 5 and n > 5)))
    X.css("fx-dtw", CSS)
    html = []
    if title: html.append(f'<div class="dtw-tt">{X.rich(title)}{"<small>" + X.rich(note) + "</small>" if note else ""}</div>')
    ro_lab = p.get("readout", "")
    ro_size = 6.4 if not X.portrait else 5.6
    html.append(f'<div class="dtw-ro"><span>{X.rich(ro_lab)}</span><b style="font-size:{ro_size:.2f}vmin"><i class="ro" style="font-style:normal">0</i><small>{X.rich(unit)}</small></b></div>')
    fmtv = lambda v, sign=False: U.fmt(v, dec, div, False, sign)
    longest = max((fmtv(s["v"], s["kind"] == "delta") for s in st), key=U.em) + unit
    px, py, pw, ph = 0.0, head_h + 4.0, bw, bh - head_h - 4.0
    geo = []
    if not horiz:
        lab_h = 7.0
        ph -= lab_h
        gap = 0.38 if n <= 6 else 0.26
        w = pw / (n + (n + 1) * gap)
        vs = min(3.6, w * 1.0 / max(U.em(longest) * 0.9, 1))
        lab_size, _ = U.fit(max((s["label"] for s in st), key=U.em), w * 1.3, lab_h - 1, 2.6, 1.3, 2)
        Y = lambda v: (hi - v) / span * ph          # vmin from the plot top
        html.append(f'<i class="dtw-z" style="left:0; width:{pw:.2f}vmin; top:{Y(0):.2f}vmin; height:.35vmin"></i>')
        for i, s in enumerate(st):
            x = gap * w * (i + 1) + w * i
            top, bot = Y(max(s["lo"], s["hi"])), Y(min(s["lo"], s["hi"]))
            neg = s["kind"] == "delta" and s["v"] < 0
            cls = "end" if s["kind"] == "end" else "tot" if s["kind"] in ("start", "sub") else ("dn" if neg else "up")
            org = "50% 0%" if neg else "50% 100%"
            html.append(f'<i class="dtw-b {cls}" data-i="{i}" style="left:{x:.2f}vmin; width:{w:.2f}vmin; top:{top:.2f}vmin; height:{max(0.25, bot - top):.2f}vmin; transform-origin:{org}"></i>')
            vy = (bot + 1.0) if neg else (top - vs - 1.0)
            html.append(f'<div class="dtw-v {"dn" if neg else ""}" data-i="{i}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); top:{vy:.2f}vmin; font-size:{vs:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            _, ll = U.fit(s["label"], w * 1.3, lab_h - 1, lab_size, lab_size, 2)
            html.append(f'<div class="dtw-l {"tot" if cls in ("tot", "end") else ""}" data-i="{i}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); top:{ph + 1.4:.2f}vmin; font-size:{lab_size:.2f}vmin; text-align:center">{U.lines_html(X, ll)}</div>')
            if i < n - 1:
                lvl = Y(s["level"]) if s["kind"] != "end" else Y(s["hi"])
                html.append(f'<i class="dtw-k" data-i="{i}" style="left:{x + w:.2f}vmin; width:{gap * w:.2f}vmin; top:{lvl:.2f}vmin"></i>')
            geo.append(s)
        axis = "scaleY"
    else:
        rh = ph / n
        lab_w = min(pw * 0.32, max_lab * min(3.0, rh * 0.48) + 1.5)
        lab_size = min(3.0, rh * 0.48, (lab_w - 1.5) / max(max_lab, 1))
        vs = min(3.0, rh * 0.5)
        val_w = U.em(longest) * vs + 2
        track = pw - lab_w - val_w - 2
        X0 = lambda v: lab_w + 1 + (v - lo) / span * track
        html.append(f'<i class="dtw-z" style="left:{X0(0):.2f}vmin; top:0; height:{ph:.2f}vmin; width:.35vmin"></i>')
        for i, s in enumerate(st):
            y = rh * i + rh * 0.16
            bhh = rh * 0.68
            l, r = X0(min(s["lo"], s["hi"])), X0(max(s["lo"], s["hi"]))
            neg = s["kind"] == "delta" and s["v"] < 0
            cls = "end" if s["kind"] == "end" else "tot" if s["kind"] in ("start", "sub") else ("dn" if neg else "up")
            org = "100% 50%" if neg else "0% 50%"
            html.append(f'<i class="dtw-b {cls}" data-i="{i}" style="left:{l:.2f}vmin; width:{max(0.25, r - l):.2f}vmin; top:{y:.2f}vmin; height:{bhh:.2f}vmin; transform-origin:{org}"></i>')
            html.append(f'<div class="dtw-v {"dn" if neg else ""}" data-i="{i}" style="left:{r + 1:.2f}vmin; top:{y + bhh / 2 - vs / 2:.2f}vmin; font-size:{vs:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            html.append(f'<div class="dtw-l {"tot" if cls in ("tot", "end") else ""}" data-i="{i}" style="left:0; width:{lab_w:.2f}vmin; top:{y + bhh / 2 - lab_size * 0.6:.2f}vmin; font-size:{lab_size:.2f}vmin; text-align:right"><span class="fl">{X.rich(s["label"])}</span></div>')
            if i < n - 1:
                lvl = X0(s["level"]) if s["kind"] != "end" else X0(s["hi"])
                html.append(f'<i class="dtw-k h" data-i="{i}" style="left:{lvl:.2f}vmin; top:{y + bhh:.2f}vmin; height:{rh * 0.32:.2f}vmin"></i>')
        axis = "scaleX"
    X.used_text.update("0123456789.,−+" + unit)
    inner = (f'<div class="dtw" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin"><div class="dtw-cam">'
             f'{"".join(h for h in html if "dtw-tt" in h or "dtw-ro" in h)}'
             f'<div class="dtw-plot" style="left:{px:.2f}vmin; top:{py:.2f}vmin; width:{pw:.2f}vmin; height:{ph:.2f}vmin">'
             f'{"".join(h for h in html if "dtw-tt" not in h and "dtw-ro" not in h)}</div></div></div>')
    _clip(X, cid, t, d, inner, p)
    s_ = f"#{cid}"
    X.tw(f'tl.from("{s_} .dtw-tt, {s_} .dtw-ro", {{y:24, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t:.3f});')
    X.tw(f'tl.from("{s_} .dtw-z", {{{"scaleX" if not horiz else "scaleY"}:0, duration:0.45, ease:"expo.inOut"}}, {t + 0.1:.3f});')
    budget = max(1.2, min(d - 1.4, 0.75 * n))
    stp = budget / n
    gd = min(0.55, stp * 0.8)
    fj = U.js_fmt(dec, False, True)
    prev = 0.0
    for i, s in enumerate(st):
        ti = t + 0.35 + i * stp
        if i > 0:
            X.tw(f'tl.from("{s_} .dtw-k[data-i=\'{i - 1}\']", {{{"scaleX" if not horiz else "scaleY"}:0, duration:{min(0.25, stp * 0.4):.2f}, ease:"power2.out"}}, {ti - 0.12:.3f});')
        ease = "power3.out" if s["kind"] != "delta" else ("bounce.out" if s["v"] < 0 and n <= 6 else "power3.out")
        X.tw(f'tl.from("{s_} .dtw-b[data-i=\'{i}\']", {{{axis}:0, duration:{gd + (0.15 if ease == "bounce.out" else 0):.2f}, ease:"{ease}"}}, {ti:.3f});')
        X.tw(f'tl.from("{s_} .dtw-v[data-i=\'{i}\'], {s_} .dtw-l[data-i=\'{i}\']", {{opacity:0, y:10, duration:0.3, ease:"power2.out"}}, {ti:.3f});')
        sign = s["kind"] == "delta"
        U.count(X, f"{s_} .dtw-v[data-i=\'{i}\'] .n", ti, 0, s["v"] / div, gd, dec, False, sign)
        X.tw(f'(()=>{{const o={{v:{prev / div}}}, el=document.querySelector("{s_} .dtw-ro .ro"), f={U.js_fmt(dec)}; tl.to(o, {{v:{s["level"] / div}, duration:{gd:.2f}, ease:"power2.out", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {ti:.3f});}})();')
        prev = s["level"]
        X.sfx(ti, "tick" if s["kind"] == "delta" else "click")
    tend = t + 0.35 + (n - 1) * stp + gd
    if st[-1]["kind"] == "end":
        X.tw(f'tl.fromTo("{s_} .dtw-b[data-i=\'{n - 1}\']", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tend:.3f});')
        X.tw(f'tl.fromTo("{s_} .dtw-v[data-i=\'{n - 1}\']", {{scale:1}}, {{keyframes:[{{scale:1.25, duration:0.14}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], immediateRender:false}}, {tend:.3f});')
        X.tw(f'tl.set("{s_} .dtw-v[data-i=\'{n - 1}\']", {{color:"var(--accent)"}}, {tend:.3f});')
        X.tw(f'tl.set("{s_} .dtw-ro b", {{color:"var(--accent)"}}, {tend:.3f});')
        X.sfx(tend, "hit")
    X.tw(f'tl.fromTo("{s_} .dtw-cam", {{scale:0.985}}, {{scale:1.025, transformOrigin:"60% 60%", duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


FX = {"waterfall": waterfall}
