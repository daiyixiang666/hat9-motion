"""柱状图赛跑 Bar Chart Race (D2 family — Envato Popular「Bar Chart Builder」; Flourish-style races are the most-viewed data
format on YouTube's data channels): horizontal bars ranked by value; time steps forward, bars stretch, the axis rescales
to the leader, bars overtake each other (they swap rows), values count between periods and a giant period stamp
turns over. The highlighted entity runs in the accent.

Adapts: 2–12 entities shown ("top" caps it; the rest wait below and slide in when they climb), 2–20 periods (the
time budget is shared out; each step = a move + a hold), negative values clamp to 0, huge values (auto 万 / 亿),
names from 1 glyph to a phrase (fitted). Data from "labels" + "series" or a wide spreadsheet ("csv": first column
the period, one column per entity — or "transpose": true when entities are rows).
p: labels [period…] · series {name: [values…]} | csv/x/series_cols · top · hl (name) · unit · dec · title · note · compact
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

SHADE = ["color-mix(in srgb, var(--fg) 82%, var(--bg))", "color-mix(in srgb, var(--fg) 62%, var(--bg))", "color-mix(in srgb, var(--fg) 46%, var(--bg))",
         "color-mix(in srgb, var(--fg) 34%, var(--bg))"]

CSS = """
.fx .dtr { position:absolute; }
.fx .dtr .dtr-tt { position:absolute; left:0; top:0; font:900 4.2vmin/1.15 var(--f-display); color:var(--fg); white-space:nowrap; }
.fx .dtr .dtr-tt small { display:block; font:500 1.9vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; margin-top:.8vmin; }
.fx .dtr .dtr-pd { position:absolute; right:0; bottom:0; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.85; text-align:right;
  color:color-mix(in srgb, var(--fg) 16%, transparent); white-space:nowrap; overflow:hidden; }
.fx .dtr .dtr-pd span { display:block; }
.fx .dtr .dtr-row { position:absolute; left:0; top:0; }
.fx .dtr .dtr-n { position:absolute; right:100%; top:0; display:flex; align-items:center; justify-content:flex-end; padding-right:1.4vmin; white-space:nowrap;
  font-family:var(--f-body); font-weight:800; color:var(--fg); }
.fx .dtr .dtr-b { position:absolute; left:0; top:0; transform-origin:0 50%; border-radius:0 .5vmin .5vmin 0; }
.fx .dtr .dtr-v { position:absolute; left:0; top:0; display:flex; align-items:center; padding-left:1.2vmin; white-space:nowrap;
  font-family:var(--f-num, var(--f-display)); font-weight:800; color:var(--fg); font-variant-numeric:tabular-nums; }
.fx .dtr .dtr-v small { font-size:.55em; color:var(--muted); margin-left:.15em; }
.fx .dtr .dtr-row.hl .dtr-n, .fx .dtr .dtr-row.hl .dtr-v { color:var(--accent); }
.fx .dtr .dtr-ax { position:absolute; top:0; width:.3vmin; background:var(--fg); }
"""


def bar_race(X, cid, t, d, p):
    labels, ser = U.wide_of(p, X)
    if p.get("transpose") and p.get("csv"):
        header, rows = U.D.read(p["csv"], X.src)
        labels = header[1:]
        ser = [(r[0], [U.D.num(c) or 0.0 for c in r[1:]]) for r in rows]
    if not ser: ser = [("—", [0.0])]
    F_ = max(len(v) for _, v in ser)
    labels = (list(labels) + [""] * F_)[:F_]
    ser = [(n, [max(0.0, (vs[k] if k < len(vs) else vs[-1]) or 0.0) for k in range(F_)]) for n, vs in ser]
    E = len(ser)
    top = int(p.get("top", min(E, 10 if not X.portrait else 8)))
    div, suf = U.compact([v for _, vs in ser for v in vs], p.get("compact", "cn"))
    unit = (suf + p.get("unit", "")) if div != 1 else p.get("unit", "")
    dec = int(p.get("dec", U.decimals([v for _, vs in ser for v in vs], div)))
    hl = p.get("hl")
    bx, by, bw, bh = U.box(X)
    vpx = min(X.W, X.H) / 100
    title, note = p.get("title", ""), p.get("note", "")
    head_h = max((9.5 if note else 7.0) if title else 0, 0 if X.portrait else 9.0)
    name_em = max(U.em(n) for n, _ in ser)
    plot_top = head_h + 2.0
    plot_h = bh - plot_top - (2 if not X.portrait else 18)
    rowh = plot_h / top
    name_size = min(3.4, rowh * 0.46, bw * 0.24 / max(name_em, 1))
    name_w = name_em * name_size + 2.2
    vstr = U.fmt(max(v for _, vs in ser for v in vs), dec, div) + unit
    val_size = min(3.2, rowh * 0.44)
    track = bw - name_w - U.em(vstr) * val_size - 3.5
    x0 = name_w
    ranks = []
    for k in range(F_):
        order = sorted(range(E), key=lambda e: -ser[e][1][k])
        ranks.append({e: r for r, e in enumerate(order)})
    maxes = [max(ser[e][1][k] for e in range(E)) or 1 for k in range(F_)]
    X.css("fx-dtr", CSS)
    pd_size = min(10.0 if not X.portrait else 18.0, bw * (0.34 if not X.portrait else 0.5) / max(max(U.em(l) for l in labels) or 1, 1))
    pd_pos = "top:0; bottom:auto" if not X.portrait else ""      # 16:9: top-right beside the title; 9:16: under the bars
    html = [f'<div class="dtr-tt">{X.rich(title)}{"<small>" + X.rich(note) + "</small>" if note else ""}</div>' if title else "",
            f'<div class="dtr-pd" style="font-size:{pd_size:.2f}vmin; height:{pd_size * 0.9:.2f}vmin; width:{bw * 0.62:.2f}vmin; {pd_pos}">' + "".join(f'<span data-k="{k}">{X.rich(l)}</span>' for k, l in enumerate(labels)) + "</div>",
            f'<i class="dtr-ax" style="left:{x0:.2f}vmin; top:{plot_top:.2f}vmin; height:{plot_h:.2f}vmin"></i>']
    init = []
    for e, (name, vs) in enumerate(ser):
        r0 = ranks[0][e]
        col = "var(--accent)" if name == hl else SHADE[e % len(SHADE)]
        y = plot_top + rowh * r0
        hidden = r0 >= top
        sc = vs[0] / maxes[0]
        init.append((e, y * vpx, 0 if hidden else 1, sc, sc * track * vpx))
        html.append(f'<div class="dtr-row {"hl" if name == hl else ""}" data-e="{e}" style="left:{x0:.2f}vmin; width:{track:.2f}vmin; height:{rowh:.2f}vmin">'
                    f'<div class="dtr-n" style="height:{rowh:.2f}vmin; font-size:{name_size:.2f}vmin">{X.rich(name)}</div>'
                    f'<i class="dtr-b" style="top:{rowh * 0.14:.2f}vmin; width:{track:.2f}vmin; height:{rowh * 0.72:.2f}vmin; background:{col}"></i>'
                    f'<div class="dtr-v" style="height:{rowh:.2f}vmin; font-size:{val_size:.2f}vmin"><span class="n">{U.fmt(vs[0], dec, div)}</span><small>{X.rich(unit)}</small></div></div>')
    X.used_text.update("0123456789.,")
    inner = f'<div class="dtr" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin">{"".join(html)}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dtr-tt", {{y:24, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .dtr-ax", {{scaleY:0, transformOrigin:"50% 0", duration:0.45, ease:"expo.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.set("{s} .dtr-pd span", {{yPercent:110, autoAlpha:0}}, {t:.3f}); tl.to("{s} .dtr-pd span[data-k=\'0\']", {{yPercent:0, autoAlpha:1, duration:0.6, ease:"expo.out"}}, {t + 0.2:.3f});')
    X.tw(f'tl.set("{s} .dtr-pd span", {{position:"absolute", right:0, top:0}}, {t:.3f});')
    for e, y, op, sc, vx in init:      # starting state on the timeline (no inline transforms: GSAP owns them)
        X.tw(f'tl.set("{s} .dtr-row[data-e=\'{e}\']", {{y:{y:.1f}, autoAlpha:{op}}}, {t:.3f}); tl.set("{s} .dtr-row[data-e=\'{e}\'] .dtr-b", {{scaleX:{sc:.4f}}}, {t:.3f}); tl.set("{s} .dtr-row[data-e=\'{e}\'] .dtr-v", {{x:{vx:.1f}}}, {t:.3f});')
    # intro: frame 0 bars grow
    for e, (name, vs) in enumerate(ser):
        r0 = ranks[0][e]
        if r0 >= top: continue
        ti = t + 0.25 + r0 * 0.06
        sc0 = vs[0] / maxes[0]
        X.tw(f'tl.fromTo("{s} .dtr-row[data-e=\'{e}\'] .dtr-b", {{scaleX:0}}, {{scaleX:{sc0:.4f}, duration:0.6, ease:"power3.out", immediateRender:false}}, {ti:.3f});')
        X.tw(f'tl.fromTo("{s} .dtr-row[data-e=\'{e}\'] .dtr-v", {{x:0}}, {{x:{sc0 * track * vpx:.1f}, duration:0.6, ease:"power3.out", immediateRender:false}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .dtr-row[data-e=\'{e}\'] .dtr-n", {{x:-20, opacity:0, duration:0.45, ease:"expo.out"}}, {ti:.3f});')
        U.count(X, f"{s} .dtr-row[data-e=\'{e}\'] .n", ti, 0, vs[0] / div, 0.6, dec)
    X.sfx(t + 0.25, "whoosh_soft")
    if F_ > 1:
        start = t + 1.2
        budget = max(0.8 * (F_ - 1), t + d - 0.9 - start)
        seg = budget / (F_ - 1)
        mv = seg * 0.62
        for k in range(1, F_):
            tk = start + seg * (k - 1)
            for e, (name, vs) in enumerate(ser):
                ra, rb = ranks[k - 1][e], ranks[k][e]
                sa, sb = vs[k - 1] / maxes[k - 1], vs[k] / maxes[k]
                ya, yb = plot_top + rowh * min(ra, top), plot_top + rowh * min(rb, top)
                X.tw(f'tl.to("{s} .dtr-row[data-e=\'{e}\'] .dtr-b", {{scaleX:{sb:.4f}, duration:{mv:.2f}, ease:"power2.inOut"}}, {tk:.3f});')
                X.tw(f'tl.to("{s} .dtr-row[data-e=\'{e}\'] .dtr-v", {{x:{sb * track * vpx:.1f}, duration:{mv:.2f}, ease:"power2.inOut"}}, {tk:.3f});')
                if ra != rb or (ra >= top) != (rb >= top):
                    X.tw(f'tl.to("{s} .dtr-row[data-e=\'{e}\']", {{y:{yb * vpx:.1f}, autoAlpha:{0 if rb >= top else 1}, duration:{mv:.2f}, ease:"power3.inOut"}}, {tk:.3f});')
                U.count(X, f"{s} .dtr-row[data-e=\'{e}\'] .n", tk, vs[k - 1] / div, vs[k] / div, mv, dec, ease="power2.inOut")
            od = min(0.35, mv * 0.45)       # the old stamp leaves before the new one arrives (never two at once)
            X.tw(f'tl.to("{s} .dtr-pd span[data-k=\'{k - 1}\']", {{yPercent:-110, autoAlpha:0, duration:{od:.2f}, ease:"power3.in"}}, {tk + mv * 0.3:.3f});')
            X.tw(f'tl.to("{s} .dtr-pd span[data-k=\'{k}\']", {{yPercent:0, autoAlpha:1, duration:{min(0.6, mv):.2f}, ease:"expo.out"}}, {tk + mv * 0.3 + od + 0.02:.3f});')
            X.sfx(tk, "whoosh_soft")
            swapped = any(ranks[k - 1][e] != ranks[k][e] for e in range(E))
            if swapped: X.sfx(tk + mv * 0.6, "tick")
        if hl is not None:
            he = next((e for e, (n, _) in enumerate(ser) if n == hl), None)
            if he is not None and ranks[-1][he] == 0:
                tend = start + budget - seg + mv
                X.tw(f'tl.fromTo("{s} .dtr-row[data-e=\'{he}\'] .dtr-v", {{scale:1}}, {{keyframes:[{{scale:1.25, duration:0.14}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], transformOrigin:"0% 50%", immediateRender:false}}, {tend:.3f});')
                X.sfx(tend, "hit")


FX = {"bar_race": bar_race}
