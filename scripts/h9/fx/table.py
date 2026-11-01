"""数据表格聚焦 Table Focus (D2, VideoHive Infographic Maker 2.6K / Infographics (Holypix) 2.2K; Envato Popular
「Bar Chart Builder」; Mapal「Animate Infographics Like VOX」34.6 万播放): the header rule draws, rows cascade in cell by cell
with their numbers counting, then one row / column / cell is pulled forward — an accent band sweeps behind it, the
rest of the table dims and the camera leans in.

Adapts: 2×2 … 8×12+ (font and row height are solved from the box; past the row limit the tail folds into
「…还有 N 行」; in 9:16 a wide, short table transposes itself), numeric columns auto-detected and right-aligned,
huge numbers scaled to 万 / 亿 per column (unit added to the header), negatives as −x (or (x) with "paren": true),
% kept, text cells from 1 glyph to a phrase (fitted). Data from "rows" or straight from a spreadsheet
("csv": "x.csv", "cols": [...], "limit": N).
p: rows [[header…], [cells…]…] | csv/cols/limit · title · note · hl_row (index or first-cell text) · hl_col (index or
header) · hl_cell [r, c] · t_hl · compact (cn|en|none) · paren · transpose (auto|true|false) · max_rows
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

CSS = """
.fx .dtt { position:absolute; }
.fx .dtt .dtt-cam { position:absolute; inset:0; }
.fx .dtt .dtt-tt { position:absolute; left:0; font:900 4.2vmin/1.15 var(--f-display); color:var(--fg); white-space:nowrap; }
.fx .dtt .dtt-tt small { display:block; font:500 1.9vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; margin-top:.8vmin; }
.fx .dtt .dtt-z { position:absolute; left:0; right:0; background:color-mix(in srgb, var(--fg) 5%, transparent); }
.fx .dtt .dtt-r { position:absolute; left:0; right:0; height:.14vmin; background:color-mix(in srgb, var(--fg) 16%, transparent); transform-origin:0 50%; }
.fx .dtt .dtt-hr { position:absolute; left:0; right:0; height:.45vmin; background:var(--fg); transform-origin:0 50%; }
.fx .dtt .dtt-band { position:absolute; background:var(--accent); transform-origin:0 50%; border-radius:.5vmin; }
.fx .dtt .dtt-band.v { transform-origin:50% 0; }
.fx .dtt .dtt-ring { position:absolute; border:.5vmin solid var(--accent); border-radius:.7vmin; }
.fx .dtt .dtt-c { position:absolute; display:flex; align-items:center; white-space:nowrap; color:var(--fg); font-family:var(--f-body); font-weight:500; }
.fx .dtt .dtt-c.n { justify-content:flex-end; font-family:var(--f-num, var(--f-display)); font-weight:700; font-variant-numeric:tabular-nums; }
.fx .dtt .dtt-c.h { color:var(--muted); font-weight:800; }
.fx .dtt .dtt-c.l { font-weight:800; }
.fx .dtt .dtt-c.neg { color:color-mix(in srgb, var(--fg) 55%, var(--bg)); }
.fx .dtt .dtt-c.more { color:var(--muted); font-style:italic; font-weight:500; }
.fx .dtt .dtt-c .u { font-size:.62em; color:var(--muted); margin-left:.12em; font-weight:600; }
.fx .dtt .dtt-c.on { color:var(--bg); } .fx .dtt .dtt-c.on .u { color:var(--bg); opacity:.8; }
"""


def _idx(v, names, n):
    if v is None: return None
    if isinstance(v, int): return v if 0 <= v < n else None
    s = str(v).strip()
    if s in names: return names.index(s)            # a label wins over an index ("2024" is a row, not row 2024)
    if s.lstrip("-").isdigit(): k = int(s); return k if 0 <= k < n else None
    return None


def table(X, cid, t, d, p):
    rows = U.rows_of(p, X)
    if not rows: rows = [["—"]]
    if p.get("header", True) is False: rows = [[""] * len(rows[0])] + rows
    w = max(len(r) for r in rows)
    rows = [[str(c) for c in r] + [""] * (w - len(r)) for r in rows]
    bx, by, bw, bh = U.box(X)
    tr = p.get("transpose", "auto")
    if tr is True or (tr == "auto" and X.portrait and w > 4 and len(rows) < w):
        rows = [list(c) for c in zip(*rows)]
        w = len(rows[0])
    head, body = rows[0], rows[1:]
    hl_row = _idx(p.get("hl_row"), [r[0] for r in body], len(body))
    hl_col = _idx(p.get("hl_col"), head, w)
    cell = p.get("hl_cell")
    lim = int(p.get("max_rows", 12 if X.portrait else 10))
    more = 0
    if len(body) > lim:
        more = len(body) - (lim - 1)
        keep = list(range(lim - 1))
        if hl_row is not None and hl_row >= lim - 1: keep[-1] = hl_row
        body = [body[i] for i in keep]
        hl_row = keep.index(hl_row) if hl_row in keep else None
    nr = len(body)
    # column kinds and per-column scaling
    kinds, divs, decs, units = [], [], [], []
    for c in range(w):
        col = [r[c] for r in body]
        nums = [U.D.num(x) for x in col]
        numeric = c > 0 and sum(v is not None for v in nums) >= max(1, 0.6 * len([x for x in col if x.strip()]))
        kinds.append("n" if numeric else ("l" if c == 0 else "t"))
        vals = [v for v, x in zip(nums, col) if v is not None and "%" not in x]
        div, suf = U.compact(vals, p.get("compact", "cn")) if numeric and vals else (1, "")
        divs.append(div); units.append(suf)
        decs.append(max([len(x.split(".")[1].rstrip("%")) if "." in x and div == 1 else (1 if div != 1 else 0) for x in col if U.D.num(x) is not None] or [0]))
    head = [h + (f"（{units[c]}）" if units[c] and units[c] not in h else "") for c, h in enumerate(head)]

    def shown(c, x):
        v = U.D.num(x)
        if kinds[c] != "n" or v is None: return x, None, ""
        pct = "%" if x.strip().endswith("%") else ""
        val = v if pct else v / divs[c]
        return U.fmt(val, decs[c], 1, p.get("paren", False)) + pct, val, pct
    # solve the type size: widths in em per column, row height 2.1 em
    cols_em = []
    for c in range(w):
        texts = [head[c]] + [shown(c, r[c])[0] for r in body] + (["…还有 99 行"] if c == 0 and more else [])
        cols_em.append(max(U.em(s) for s in texts) + 1.4)
    title = p.get("title", ""); note = p.get("note", "")
    th_v = (9.0 if note else 6.6) if title else 0
    avail_h = bh - th_v - 1
    size = min(5.6 if not X.portrait else 4.6, bw / sum(cols_em), avail_h / ((nr + 1 + (1 if more else 0)) * 2.1))
    size = max(1.5, size)
    rh = size * 2.1
    tot_w = sum(cols_em) * size
    scale = min(1.0, bw / tot_w)
    cw = [e * size * scale for e in cols_em]
    tw_ = sum(cw)
    tbl_h = rh * (nr + 1 + (1 if more else 0))
    left = (bw - tw_) / 2
    top = th_v + max(0, (avail_h - tbl_h) / 2)
    X.css("fx-dtt", CSS)
    html = []
    if title:
        html.append(f'<div class="dtt-tt" style="left:{left:.2f}vmin; top:{max(0, top - th_v):.2f}vmin">{X.rich(title)}{"<small>" + X.rich(note) + "</small>" if note else ""}</div>')
    xs = [left + sum(cw[:c]) for c in range(w)]
    y0 = top
    # header
    for c in range(w):
        html.append(f'<div class="dtt-c h {"n" if kinds[c] == "n" else ""}" data-r="h" style="left:{xs[c] + size * 0.6:.2f}vmin; width:{cw[c] - size * 1.2:.2f}vmin; top:{y0:.2f}vmin; height:{rh:.2f}vmin; font-size:{size * 0.82:.2f}vmin">{X.rich(head[c])}</div>')
    html.append(f'<i class="dtt-hr" style="left:{left:.2f}vmin; width:{tw_:.2f}vmin; right:auto; top:{y0 + rh - 0.2:.2f}vmin"></i>')
    counters = []
    for i, r in enumerate(body):
        y = y0 + rh * (i + 1)
        if i % 2 == 1: html.append(f'<i class="dtt-z" data-r="{i}" style="left:{left:.2f}vmin; width:{tw_:.2f}vmin; right:auto; top:{y:.2f}vmin; height:{rh:.2f}vmin"></i>')
        html.append(f'<i class="dtt-r" data-r="{i}" style="left:{left:.2f}vmin; width:{tw_:.2f}vmin; right:auto; top:{y + rh - 0.07:.2f}vmin"></i>')
        for c in range(w):
            txt, val, pct = shown(c, r[c])
            neg = val is not None and val < 0
            on = (hl_row == i) or (cell and list(cell) == [i, c])
            cls = f'dtt-c {kinds[c]} {"neg" if neg else ""}'
            inner = f'<span class="nv">{X.rich(txt) if val is None else U.fmt(0, decs[c]) + pct}</span>'
            if val is not None and pct: inner = f'<span class="nv">{U.fmt(0, decs[c])}</span><span class="u">%</span>'
            html.append(f'<div class="{cls}" data-r="{i}" data-c="{c}" style="left:{xs[c] + size * 0.6:.2f}vmin; width:{cw[c] - size * 1.2:.2f}vmin; top:{y:.2f}vmin; height:{rh:.2f}vmin; font-size:{size:.2f}vmin">{inner}</div>')
            if val is not None: counters.append((i, c, val, decs[c]))
    if more:
        y = y0 + rh * (nr + 1)
        html.append(f'<div class="dtt-c more" data-r="m" style="left:{xs[0] + size * 0.6:.2f}vmin; top:{y:.2f}vmin; height:{rh:.2f}vmin; font-size:{size * 0.82:.2f}vmin">…还有 {more} 行</div>')
        X.used_text.update(f"…还有 {more} 行")
    # highlight geometry
    band = ""
    if hl_row is not None:
        y = y0 + rh * (hl_row + 1)
        band = f'<i class="dtt-band" style="left:{left - size * 0.3:.2f}vmin; width:{tw_ + size * 0.6:.2f}vmin; top:{y + rh * 0.08:.2f}vmin; height:{rh * 0.84:.2f}vmin"></i>'
        org = (left + tw_ / 2, y + rh / 2)
    elif hl_col is not None:
        band = f'<i class="dtt-band v" style="left:{xs[hl_col]:.2f}vmin; width:{cw[hl_col]:.2f}vmin; top:{y0 - size * 0.2:.2f}vmin; height:{rh * (nr + 1) + size * 0.4:.2f}vmin; background:color-mix(in srgb, var(--accent) 16%, transparent); border:.4vmin solid var(--accent)"></i>'
        org = (xs[hl_col] + cw[hl_col] / 2, y0 + rh * (nr + 1) / 2)
    elif cell:
        ri, ci = int(cell[0]), int(cell[1])
        y = y0 + rh * (ri + 1)
        band = f'<i class="dtt-ring" style="left:{xs[ci] + size * 0.15:.2f}vmin; width:{cw[ci] - size * 0.3:.2f}vmin; top:{y + rh * 0.04:.2f}vmin; height:{rh * 0.92:.2f}vmin"></i>'
        org = (xs[ci] + cw[ci] / 2, y + rh / 2)
    else:
        org = (left + tw_ / 2, y0 + tbl_h / 2)
    inner = f'<div class="dtt" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin"><div class="dtt-cam">{band}{"".join(html)}</div></div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dtt-tt", {{y:30, opacity:0, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .dtt-hr", {{scaleX:0, duration:0.55, ease:"expo.inOut"}}, {t + 0.12:.3f});')
    X.tw(f'tl.from("{s} .dtt-c[data-r=\'h\']", {{yPercent:60, opacity:0, duration:0.45, ease:"expo.out", stagger:0.04}}, {t + 0.2:.3f});')
    budget = max(0.8, min(d * 0.45, 2.2))
    st = min(0.16, budget / max(nr, 1))
    for i in range(nr):
        ti = t + 0.4 + i * st
        X.tw(f'tl.from("{s} .dtt-r[data-r=\'{i}\'], {s} .dtt-z[data-r=\'{i}\']", {{scaleX:0, transformOrigin:"0 50%", duration:0.5, ease:"expo.out"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .dtt-c[data-r=\'{i}\']", {{yPercent:70, opacity:0, duration:0.45, ease:"expo.out", stagger:0.035}}, {ti:.3f});')
        if nr <= 8 or i % 2 == 0: X.sfx(ti, "tick")
    for i, c, val, dec in counters:
        U.count(X, f'{s} .dtt-c[data-r=\'{i}\'][data-c=\'{c}\'] .nv', t + 0.42 + i * st + c * 0.035, 0, val, 0.75, dec, p.get("paren", False))
    if more: X.tw(f'tl.from("{s} .dtt-c.more", {{opacity:0, duration:0.4}}, {t + 0.4 + nr * st:.3f});')
    rows_done = t + 0.4 + nr * st + 0.6
    th = U.cue(X, p, "t_hl", t, min(rows_done + 0.2, t + d - 1.0))
    th = max(th, t + 0.6)
    if band:
        if hl_row is not None:
            X.tw(f'tl.from("{s} .dtt-band", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {th:.3f});')
            X.tw(f'tl.set("{s} .dtt-c[data-r=\'{hl_row}\'], {s} .dtt-c[data-r=\'{hl_row}\'] .u", {{color:"var(--bg)"}}, {th + 0.12:.3f});')
            dim = f'{s} .dtt-c:not([data-r=\'{hl_row}\']):not([data-r=\'h\'])'
        elif hl_col is not None:
            X.tw(f'tl.from("{s} .dtt-band", {{scaleY:0, duration:0.5, ease:"expo.out"}}, {th:.3f});')
            dim = f'{s} .dtt-c:not([data-c=\'{hl_col}\']):not([data-r=\'h\'])'
            X.tw(f'tl.set("{s} .dtt-c[data-c=\'{hl_col}\']:not([data-r=\'h\'])", {{color:"var(--accent)"}}, {th + 0.12:.3f});')
        else:
            X.tw(f'tl.from("{s} .dtt-ring", {{scale:1.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {th:.3f});')
            dim = f'{s} .dtt-c:not([data-r=\'{int(cell[0])}\'][data-c=\'{int(cell[1])}\']):not([data-r=\'h\'])'
        X.tw(f'tl.to("{dim}", {{opacity:0.3, duration:0.4, ease:"power2.out"}}, {th + 0.05:.3f});')
        X.sfx(th, "hit")
    # camera: settle-in drift, then lean toward the highlight
    ox, oy = org[0] / bw * 100, org[1] / bh * 100
    X.tw(f'tl.set("{s} .dtt-cam", {{transformOrigin:"{ox:.1f}% {oy:.1f}%"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .dtt-cam", {{scale:0.98}}, {{scale:1.0, duration:{max(0.4, th - t):.2f}, ease:"sine.out"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .dtt-cam", {{scale:{1.06 if band else 1.025}, duration:{max(0.4, t + d - th):.2f}, ease:"power2.out"}}, {th:.3f});')


FX = {"table": table}
