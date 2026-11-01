"""财报表 Financial Statement Focus (D2 infographic family — VideoHive Infographic Maker 2.6K; the 利润表 / 资产负债表 shot of
every 财报拆解 video): a printed statement card tilts up into view, line items type in top-down in accounting form
(negatives in brackets, subtotal rules, a double rule under the bottom line), amounts count, and the key line is
marked with a highlighter sweep, its figure turns accent and a margin note slides in on a leader.

Adapts: 2–16 line items with indents, subtotals ("sub") and totals ("total"); 1–3 period columns ("cols" +
per-item "values"), an optional 同比 column ("yoy"); labels from 2 glyphs to a long 科目名 (fitted); any magnitude
(pass "unit", e.g. "亿元"); 9:16 stacks the card full width. Data from "items" or a spreadsheet ("csv": first column
科目, then one column per period; a "kind" column is optional).
p: items [[label, value | [values], kind?, yoy?] | {label, value | values, kind, yoy, indent}] · cols · title ·
unit · period · hl (index or label) · hl_note · t_hl · dec
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

CSS = """
.fx .dts { position:absolute; perspective:160vmin; }
.fx .dts .dts-cam { position:absolute; inset:0; }
.fx .dts .dts-card { position:absolute; background:var(--card); color:var(--card-fg); border-radius:1vmin;
  box-shadow:0 2vmin 6vmin rgba(0,0,0,.22), 0 .3vmin .8vmin rgba(0,0,0,.12); transform-origin:50% 100%; }
.fx .dts .dts-hd { position:absolute; left:0; right:0; top:0; }
.fx .dts .dts-hd b { display:block; font:900 3.6vmin/1.2 var(--f-display); color:var(--card-fg); }
.fx .dts .dts-hd span { display:block; font:500 1.7vmin/1.4 var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 55%, transparent); letter-spacing:.04em; margin-top:.6vmin; }
.fx .dts .dts-ch { position:absolute; font:700 1.8vmin var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 55%, transparent); text-align:right; letter-spacing:.04em; white-space:nowrap; }
.fx .dts .dts-rule { position:absolute; height:.15vmin; background:color-mix(in srgb, var(--card-fg) 14%, transparent); transform-origin:0 50%; }
.fx .dts .dts-rule.k-sub { height:.25vmin; background:var(--card-fg); }
.fx .dts .dts-rule.dbl { height:.85vmin; background:transparent; border-top:.25vmin solid var(--card-fg); border-bottom:.25vmin solid var(--card-fg); }
.fx .dts .dts-l { position:absolute; display:flex; align-items:center; white-space:nowrap; font-family:var(--f-body); font-weight:500; color:var(--card-fg); }
.fx .dts .dts-l.k-sub, .fx .dts .dts-l.k-total { font-weight:900; }
.fx .dts .dts-a { position:absolute; display:flex; align-items:center; justify-content:flex-end; white-space:nowrap; font-family:var(--f-num, var(--f-display)); font-weight:700; color:var(--card-fg); font-variant-numeric:tabular-nums; }
.fx .dts .dts-a.k-sub, .fx .dts .dts-a.k-total { font-weight:900; }
.fx .dts .dts-a.y { font-weight:700; color:color-mix(in srgb, var(--card-fg) 60%, transparent); }
.fx .dts .dts-a.y.up { color:color-mix(in srgb, var(--card-fg) 80%, transparent); }
.fx .dts .dts-mk { position:absolute; background:color-mix(in srgb, var(--accent) 24%, transparent); border-left:.6vmin solid var(--accent); transform-origin:0 50%; }
.fx .dts .dts-note { position:absolute; display:flex; align-items:center; gap:1.2vmin; white-space:nowrap; }
.fx .dts .dts-note i { display:block; height:.3vmin; width:5vmin; background:var(--accent); transform-origin:0 50%; }
.fx .dts .dts-note b { font:900 3vmin var(--f-display); color:var(--bg); background:var(--accent); padding:.6vmin 1.6vmin; border-radius:.6vmin; }
"""


def _items(p, X):
    out = []
    if p.get("csv"):
        header, rows = U.D.read(p["csv"], X.src)
        kind_i = next((i for i, h in enumerate(header) if h.lower() in ("kind", "类型")), None)
        cols = [h for i, h in enumerate(header[1:], 1) if i != kind_i]
        for r in rows:
            vals = [U.D.num(c) for i, c in enumerate(r[1:], 1) if i != kind_i]
            out.append({"label": r[0], "values": vals, "kind": (r[kind_i] if kind_i is not None else "line") or "line"})
        return cols, out
    for it in p.get("items", []):
        if isinstance(it, dict):
            v = it.get("values", it.get("value"))
            out.append({"label": it.get("label", ""), "values": v if isinstance(v, list) else [v], "kind": it.get("kind", "line"),
                        "yoy": it.get("yoy"), "indent": it.get("indent", 0)})
        else:
            it = list(it) + [None] * (4 - len(it))
            v = it[1]
            out.append({"label": it[0], "values": v if isinstance(v, list) else [v], "kind": it[2] or "line", "yoy": it[3]})
    return p.get("cols") or [], out


def statement_table(X, cid, t, d, p):
    cols, items = _items(p, X)
    items = items[:16] or [{"label": "—", "values": [None], "kind": "line"}]
    nv = max(len(it["values"]) for it in items)
    cols = (list(cols) + [""] * nv)[:nv]
    has_yoy = any(it.get("yoy") for it in items)
    allv = [v for it in items for v in it["values"] if v is not None]
    dec = int(p.get("dec", U.decimals(allv)))
    n = len(items)
    hl = p.get("hl")
    labels = [str(it["label"]) for it in items]
    hl_i = labels.index(hl) if isinstance(hl, str) and hl in labels else (hl if isinstance(hl, int) and 0 <= hl < n else None)
    bx, by, bw, bh = U.box(X)
    cw_ = min(bw, 118.0) if not X.portrait else bw
    note = p.get("hl_note", "")
    pad = 4.0
    head_h = 9.0
    amt_em = max(U.em(U.fmt(v, dec, 1, True)) for v in allv) if allv else 3
    amt_em = max(amt_em, max([U.em(c) for c in cols] or [0]) * 0.75)
    yoy_em = max([U.em(str(it.get("yoy") or "")) for it in items] or [0]) if has_yoy else 0
    lab_em = max(U.em(l) + (1.2 if it.get("indent") else 0) for l, it in zip(labels, items))
    rows_h = bh - head_h - pad * 2 - 3.5
    size = min(3.4 if not X.portrait else 3.2, rows_h / (n * 2.0), (cw_ - pad * 2) / (lab_em + nv * (amt_em + 2.2) + (yoy_em + 2.2 if has_yoy else 0)))
    size = max(1.4, size)
    rh = size * 2.0
    card_h = head_h + 3.5 + rh * n + pad * 2
    cx = (bw - cw_) / 2 if not note or X.portrait else max(0, (bw - cw_) / 2 - 10)
    cy = max(0, (bh - card_h) / 2)
    inner_w = cw_ - pad * 2
    amt_w = (amt_em + 2.2) * size
    yoy_w = (yoy_em + 2.2) * size if has_yoy else 0
    xa = [inner_w - yoy_w - amt_w * (nv - k) for k in range(nv)]   # left edge of each amount column
    X.css("fx-dts", CSS)
    h = [f'<div class="dts-hd" style="left:{pad:.2f}vmin; top:{pad:.2f}vmin"><b>{X.rich(p.get("title", "利润表（摘要）"))}</b><span>{X.rich(p.get("period", ""))}{(" · 单位：" + X.rich(p["unit"])) if p.get("unit") else ""}</span></div>']
    yh = pad + head_h
    for k, c in enumerate(cols):
        h.append(f'<div class="dts-ch" style="left:{pad + xa[k]:.2f}vmin; width:{amt_w - size * 0.6:.2f}vmin; top:{yh:.2f}vmin">{X.rich(c)}</div>')
    if has_yoy: h.append(f'<div class="dts-ch" style="left:{pad + inner_w - yoy_w:.2f}vmin; width:{yoy_w - size * 0.3:.2f}vmin; top:{yh:.2f}vmin">同比</div>')
    h.append(f'<i class="dts-rule k-sub" data-r="h" style="left:{pad:.2f}vmin; width:{inner_w:.2f}vmin; top:{yh + 3.0:.2f}vmin"></i>')
    y0 = yh + 3.5
    counters, ruled = [], set()
    for i, it in enumerate(items):
        y = y0 + rh * i
        k = it["kind"]
        ind = size * 1.2 if it.get("indent") else 0
        if k in ("sub", "total"):
            ruled.add(i)
            h.append(f'<i class="dts-rule k-sub" data-r="{i}" style="left:{pad + xa[0]:.2f}vmin; width:{inner_w - xa[0]:.2f}vmin; top:{y:.2f}vmin"></i>')
        h.append(f'<div class="dts-l k-{k}" data-r="{i}" style="left:{pad + ind:.2f}vmin; top:{y:.2f}vmin; height:{rh:.2f}vmin; font-size:{size:.2f}vmin">{X.rich(it["label"])}</div>')
        for kk, v in enumerate(it["values"]):
            txt = U.fmt(0, dec) if v is not None else "—"
            h.append(f'<div class="dts-a k-{k}" data-r="{i}" data-c="{kk}" style="left:{pad + xa[kk]:.2f}vmin; width:{amt_w - size * 0.6:.2f}vmin; top:{y:.2f}vmin; height:{rh:.2f}vmin; font-size:{size:.2f}vmin"><span class="n">{txt}</span></div>')
            if v is not None: counters.append((i, kk, v))
        if has_yoy and it.get("yoy"):
            yy = str(it["yoy"])
            h.append(f'<div class="dts-a y {"up" if yy.startswith("+") else ""}" data-r="{i}" style="left:{pad + inner_w - yoy_w:.2f}vmin; width:{yoy_w - size * 0.3:.2f}vmin; top:{y:.2f}vmin; height:{rh:.2f}vmin; font-size:{size * 0.88:.2f}vmin">{X.rich(yy)}</div>')
        if k == "total":
            ruled.add(i)
            h.append(f'<i class="dts-rule dbl" data-r="{i}" style="left:{pad + xa[0]:.2f}vmin; width:{inner_w - xa[0]:.2f}vmin; top:{y + rh - 0.2:.2f}vmin"></i>')
        elif i < n - 1 and items[i + 1]["kind"] not in ("sub", "total"):
            ruled.add(i)
            h.append(f'<i class="dts-rule" data-r="{i}" style="left:{pad:.2f}vmin; width:{inner_w:.2f}vmin; top:{y + rh - 0.07:.2f}vmin"></i>')
    mk = ""
    if hl_i is not None:
        y = y0 + rh * hl_i
        mk = f'<i class="dts-mk" style="left:{pad - 1:.2f}vmin; width:{inner_w + 2:.2f}vmin; top:{y + rh * 0.06:.2f}vmin; height:{rh * 0.88:.2f}vmin"></i>'
    card = f'<div class="dts-card" style="left:{cx:.2f}vmin; top:{cy:.2f}vmin; width:{cw_:.2f}vmin; height:{card_h:.2f}vmin">{mk}{"".join(h)}</div>'
    nt = ""
    if note and hl_i is not None:
        y = cy + y0 + rh * hl_i + rh / 2
        if X.portrait:
            ny = cy + card_h + 3 if cy + card_h + 9 < bh else bh - 4.5      # a tall card: hang it on the card's bottom edge
            nt = f'<div class="dts-note" style="right:{bw - cx - cw_:.2f}vmin; top:{ny:.2f}vmin"><b>{X.rich(note)}</b></div>'
        else:
            nt = f'<div class="dts-note" style="left:{cx + cw_ + 1.5:.2f}vmin; top:{y - 2.6:.2f}vmin"><i></i><b>{X.rich(note)}</b></div>'
    inner = f'<div class="dts" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin"><div class="dts-cam">{card}{nt}</div></div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dts-card", {{rotationX:24, y:60, scale:0.94, opacity:0, duration:0.8, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .dts-hd > *, {s} .dts-ch", {{y:14, opacity:0, duration:0.45, ease:"expo.out", stagger:0.06}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .dts-rule[data-r=\'h\']", {{scaleX:0, duration:0.5, ease:"expo.inOut"}}, {t + 0.35:.3f});')
    budget = max(0.9, min(d * 0.45, 2.6))
    stp = min(0.22, budget / n)
    for i, it in enumerate(items):
        ti = t + 0.55 + i * stp
        if i in ruled: X.tw(f'tl.from("{s} .dts-rule[data-r=\'{i}\']", {{scaleX:0, duration:0.4, ease:"expo.out"}}, {ti:.3f});')
        X.tw(f'tl.fromTo("{s} .dts-l[data-r=\'{i}\']", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.4, ease:"power2.out"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .dts-a[data-r=\'{i}\']", {{opacity:0, duration:0.25}}, {ti + 0.05:.3f});')
        X.sfx(ti, "tick" if it["kind"] == "line" else "click")
    for i, kk, v in counters:
        quick = items[i]["kind"] in ("sub", "total")
        U.count(X, f"{s} .dts-a[data-r=\'{i}\'][data-c=\'{kk}\'] .n", t + 0.6 + i * stp + kk * 0.05, 0, v, 0.45 if quick else 0.7, dec, True)
    done = t + 0.55 + n * stp + 0.6
    th = max(t + 0.8, U.cue(X, p, "t_hl", t, min(done, t + d - 1.2)))
    if hl_i is not None:
        X.tw(f'tl.from("{s} .dts-mk", {{scaleX:0, duration:0.55, ease:"expo.out"}}, {th:.3f});')
        X.tw(f'tl.set("{s} .dts-a[data-r=\'{hl_i}\']:not(.y)", {{color:"var(--accent)"}}, {th + 0.15:.3f});')
        X.tw(f'tl.fromTo("{s} .dts-a[data-r=\'{hl_i}\']:not(.y)", {{scale:1}}, {{keyframes:[{{scale:1.18, duration:0.14}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], transformOrigin:"100% 50%", immediateRender:false}}, {th + 0.15:.3f});')
        X.sfx(th + 0.1, "hit")
        if nt:
            if not X.portrait: X.tw(f'tl.from("{s} .dts-note i", {{scaleX:0, duration:0.35, ease:"expo.out"}}, {th + 0.35:.3f});')
            X.tw(f'tl.from("{s} .dts-note b", {{x:-24, opacity:0, duration:0.45, ease:"back.out(2)"}}, {th + 0.45:.3f});')
        oy = (cy + y0 + rh * hl_i + rh / 2) / bh * 100
        X.tw(f'tl.to("{s} .dts-cam", {{scale:1.07, transformOrigin:"50% {oy:.1f}%", duration:{max(0.5, t + d - th):.2f}, ease:"power2.inOut"}}, {th:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .dts-cam", {{scale:1}}, {{scale:1.03, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


FX = {"statement_table": statement_table}
