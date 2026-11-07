"""日志滚动 Log scroll (proof by volume: "every day several releases", "89 issues fixed"): a terminal / table window of
real log lines scrolls past; each line flashes as it crosses the read line, a corner counter steps (DAY 02 → 13, or
0 → 89 条) and at the end a rising tag pops ("加速提升中 ↑").

Adapts: lines as a list (strings, or [col, col, ...] rows) or a text file (one line per row; columns split on tabs or
" | "), any count (few lines type in, many scroll), a header row for table mode (`columns`), status words shown as chips
(`chips`), long cells cut with an ellipsis; window, chips, marker and type follow the style (mono face, corners, accent).
p: lines | file · columns · chips (words drawn as status chips, default 已发布/已解决/已修复/done/fixed) · title · counter
   ({label, from, to, pad} or "89 条") · tag · visible (rows on screen) · subject · subject_label · mock
"""
import importlib.util
import pathlib
import sys
from h9 import fit
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
.fx .ls .ls-win { position:absolute; display:flex; flex-direction:column; }
.fx .ls .ls-bar { flex:none; display:flex; align-items:center; gap:14px; padding:0 22px; border-bottom:1px solid color-mix(in srgb, var(--card-fg) 14%, transparent);
  font:600 20px var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 60%, transparent); white-space:nowrap; }
.fx .ls .ls-bar i { width:13px; height:13px; border-radius:var(--mt-dot); background:color-mix(in srgb, var(--card-fg) 22%, transparent); flex:none; }
.fx .ls .ls-bar i:first-child { background:var(--accent); }
.fx .ls .ls-bar .ttl { overflow:hidden; text-overflow:ellipsis; }
.fx .ls .ls-ctr { margin-left:auto; display:flex; align-items:baseline; gap:.3em; color:var(--accent); font-family:var(--f-num, var(--f-mono)); font-weight:900; }
.fx .ls .ls-ctr small { font:700 .5em var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 60%, transparent); letter-spacing:.1em; }
.fx .ls .ls-view { position:relative; flex:1; overflow:hidden; }
.fx .ls .ls-band { position:absolute; left:0; right:0; background:color-mix(in srgb, var(--accent) 12%, transparent); border-left:var(--mt-sw) solid var(--accent); }
.fx .ls .ls-rows { position:absolute; left:0; right:0; top:0; }
.fx .ls .ls-row, .fx .ls .ls-head { display:flex; align-items:center; gap:18px; padding:0 22px; font-family:var(--f-mono, monospace); color:var(--card-fg); white-space:nowrap; }
.fx .ls .ls-head { flex:none; color:color-mix(in srgb, var(--card-fg) 55%, transparent); font-weight:700; border-bottom:1px solid color-mix(in srgb, var(--card-fg) 14%, transparent); }
.fx .ls .ls-row .mk { flex:none; width:.55em; height:.55em; border-radius:var(--mt-dot); background:var(--accent); }
.fx .ls .ls-row .c, .fx .ls .ls-head .c { overflow:hidden; text-overflow:ellipsis; flex:none; }
.fx .ls .ls-row.g1 { background:color-mix(in srgb, var(--card-fg) 4%, transparent); }
.fx .ls .ls-row .c.rep { color:color-mix(in srgb, var(--card-fg) 28%, transparent); }
.fx .ls .ls-row .c.dim { color:color-mix(in srgb, var(--card-fg) 55%, transparent); }
.fx .ls .ls-row .c.last, .fx .ls .ls-head .c.last { flex:1; min-width:0; }
.fx .ls .ls-row .chip { display:inline-block; font-family:var(--f-body); font-weight:800; font-size:.82em; color:var(--accent);
  background:color-mix(in srgb, var(--accent) 16%, transparent); padding:.1em .55em; border-radius:calc(var(--mt-r) * .5); }
.fx .ls .ls-tag { font-size:34px; }
.fx .ls .ls-tag b { display:inline-block; font-weight:900; }
"""

CHIPS = ["已发布", "已解决", "已修复", "已完成", "done", "fixed", "released", "merged", "已合并", "已上线"]


def _rows(X, p):
    raw = p.get("lines")
    if not raw and p.get("file"):
        path = M.W3.resolve(X, p["file"])
        raw = []
        for ln in path.read_text().splitlines():
            if ln.strip():
                raw.append(ln.rstrip())
    rows = []
    for r in raw or []:
        if isinstance(r, (list, tuple)):
            cells = []
            for c in r:
                cells.append(str(c))
            rows.append(cells)
            continue
        s = str(r)
        if "\t" in s:
            rows.append(s.split("\t"))
        elif " | " in s:
            rows.append(s.split(" | "))
        else:
            rows.append([s])
    return rows


def _counter(p):
    """-> (label, start, end, pad, unit) from p.counter."""
    c = p.get("counter")
    if not c:
        return None
    if isinstance(c, dict):
        return (str(c.get("label", "")), float(c.get("from", 0)), float(c.get("to", 0)), int(c.get("pad", 0)), str(c.get("unit", "")))
    val, pre, suf, _ = M.split_num(c)
    return (pre.strip(), 0.0, val, 0, suf.strip())


def log_scroll(X, cid, t, d, p):
    M.base(X)
    X.css("fx-ls", CSS)
    sk = M.skin(X)
    P = X.portrait
    rows = _rows(X, p)
    if not rows:
        raise SystemExit(f"log_scroll at {t:.2f}s: give `lines` (a list) or `file` (a text file, one line per row)")
    has_sub = bool(p.get("subject"))
    R = M.regions(X, p, has_sub, graphic_share=0.6, hero_ar=0.92, row="center")
    gx0, gy0, gx1, gy1 = R["g"]
    wx0, wy0, wx1, wy1 = gx0, gy0, gx1, gy1
    ww = wx1 - wx0
    wh = wy1 - wy0
    bar_h = 58
    cols_hdr = p.get("columns")
    head_h = 0
    vis = int(p.get("visible", 11 if P else 9))
    rh = (wh - bar_h) / (vis + (0.8 if cols_hdr else 0))
    rh = max(34.0, min(rh, 74.0))
    if cols_hdr:
        head_h = rh * 0.8
    font_px = rh * 0.42
    vis = int((wh - bar_h - head_h) / rh)
    if len(rows) < vis:                                    # a short log: the window hugs its rows
        wh = bar_h + head_h + len(rows) * rh + rh * 0.6
        wy1 = wy0 + wh
    # column widths from content (capped), the last column takes the rest
    ncol = 0
    for r in rows:
        ncol = max(ncol, len(r))
    if cols_hdr:
        ncol = max(ncol, len(cols_hdr))
    widths = []
    for k in range(ncol - 1):
        wmax = 0.0
        for r in rows:
            if k < len(r):
                wmax = max(wmax, fit.width(fit.plain(r[k]), mono=True))
        if cols_hdr and k < len(cols_hdr):
            wmax = max(wmax, fit.width(fit.plain(cols_hdr[k]), mono=True))
        widths.append(min(wmax * font_px * 1.05 + 4, ww * 0.26))
    chips = p.get("chips", CHIPS)
    row_html = []
    group = 0
    prev_key = None
    for i, r in enumerate(rows):
        key = r[0] if len(r) > 1 else None
        first_of_group = key != prev_key
        if first_of_group and i > 0 and key is not None:
            group = 1 - group
        prev_key = key
        cells = ['<i class="mk"></i>']
        for k in range(ncol):
            txt = r[k] if k < len(r) else ""
            is_chip = txt.strip() in chips
            inner = f'<span class="chip">{X.rich(txt)}</span>' if is_chip else X.rich(txt)
            if k == ncol - 1:
                cells.append(f'<span class="c last">{inner}</span>')
            else:
                dim = " dim" if (k > 0 and not is_chip) else ""
                if k == 0 and key is not None and not first_of_group:
                    dim = " rep"
                cells.append(f'<span class="c{dim}" style="width:{widths[k]:.0f}px">{inner}</span>')
        row_html.append(f'<div class="ls-row g{group}" data-i="{i}" style="height:{rh:.1f}px; font-size:{font_px:.1f}px">{"".join(cells)}</div>')
    head_html = ""
    if cols_hdr:
        hc = ['<i style="width:.55em; flex:none"></i>']
        for k in range(ncol):
            txt = cols_hdr[k] if k < len(cols_hdr) else ""
            if k == ncol - 1:
                hc.append(f'<span class="c last">{X.rich(txt)}</span>')
            else:
                hc.append(f'<span class="c" style="width:{widths[k]:.0f}px">{X.rich(txt)}</span>')
        head_html = f'<div class="ls-head" style="height:{head_h:.1f}px; font-size:{font_px * 0.9:.1f}px">{"".join(hc)}</div>'
    cnt = _counter(p)
    ctr_html = ""
    if cnt:
        label, c0, c1, pad, unit = cnt
        X.used_text.update(label + unit + "0123456789")
        first = str(int(c0)).zfill(pad)
        lab_html = f"<small>{X.rich(label)}</small>" if label else ""
        unit_html = f"<small>{X.rich(unit)}</small>" if unit else ""
        ctr_html = f'<span class="ls-ctr" style="font-size:{min(40, bar_h * 0.62):.0f}px">{lab_html}<b class="n">{first}</b>{unit_html}</span>'
    title = p.get("title", "")
    X.used_text.update(title)
    bar = f'<div class="ls-bar" style="height:{bar_h}px"><i></i><i></i><i></i><span class="ttl">{X.rich(title)}</span>{ctr_html}</div>'
    band_row = max(1, vis - 2)
    band = f'<div class="ls-band" style="top:{band_row * rh:.1f}px; height:{rh:.1f}px"></div>'
    view = f'<div class="ls-view">{band}<div class="ls-rows" data-layout-allow-overlap>{"".join(row_html)}</div></div>'
    win = (f'<div class="mt-card ls-win" style="left:{wx0:.0f}px; top:{wy0:.0f}px; width:{ww:.0f}px; height:{wh:.0f}px">'
           f'{bar}{head_html}{view}</div>')
    tag = p.get("tag", "")
    tag_html = ""
    if tag:
        X.used_text.update(tag)
        arrow = ""
        txt = tag
        if tag.endswith("↑"):
            txt = tag[:-1].rstrip()
            arrow = "<b>↑</b>"
        tag_px = 40 if P else 36
        ty = wy1 - tag_px * 1.9
        tag_html = f'<div class="mt-pill acc ls-tag" style="right:{X.W - wx1 + 24:.0f}px; top:{ty:.0f}px; font-size:{tag_px}px">{X.rich(txt)}{arrow}</div>'
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=t + 0.3)
    mock = M.mock_tag(X, p, wx1 - 80, wy0 - 40)
    _clip(X, cid, t, d, M.wrap(X, sk, win + tag_html + subj + mock, "ls"), p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    col = M.colors(X, p)
    X.tw(f'tl.from("{s} .ls-win", {{y:60, opacity:0, scale:0.97, duration:0.55, ease:"{e}"}}, {t + 0.02:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    n = len(rows)
    t_s = t + 0.55
    t_e = t + d - (1.1 if tag else 0.5)
    flashes = []
    if n > vis:
        X.tw(f'tl.from("{s} .ls-row:nth-child(-n+{vis})", {{opacity:0, x:-24, duration:0.3, ease:"{e}", stagger:0.04}}, {t + 0.15:.3f});')
        shift = (n - vis) * rh
        X.tw(f'tl.to("{s} .ls-rows", {{y:{-shift:.1f}, duration:{t_e - t_s:.2f}, ease:"none"}}, {t_s:.3f});')
        speed = shift / max(0.1, t_e - t_s)
        band_y = band_row * rh
        for i in range(n):
            y0 = i * rh
            if y0 <= band_y:
                if i == band_row:
                    flashes.append((i, t + 0.35))
                continue
            when = t_s + (y0 - band_y) / speed
            if when < t_e + 0.01:
                flashes.append((i, when))
    else:
        each = min(0.45, (t_e - t - 0.3) / max(1, n))
        X.tw(f'tl.from("{s} .ls-row", {{opacity:0, x:-24, duration:0.3, ease:"{e}", stagger:{each:.3f}}}, {t + 0.3:.3f});')
        X.tw(f'tl.set("{s} .ls-band", {{opacity:0}}, {t:.3f});')
    for i, when in flashes:
        X.tw(f'tl.fromTo("{s} .ls-row[data-i=\'{i}\']", {{color:"{col["accent"]}"}}, {{color:"{col["card-fg"]}", duration:0.6, ease:"power2.out", immediateRender:false}}, {when:.3f});')
        X.tw(f'tl.fromTo("{s} .ls-row[data-i=\'{i}\'] .mk", {{scale:1}}, {{keyframes:[{{scale:1.8, duration:0.08}}, {{scale:1, duration:0.3}}], immediateRender:false}}, {when:.3f});')
    if flashes:
        X.sfx(flashes[0][1], "type")
    if cnt:
        label, c0, c1, pad, unit = cnt
        X.tw(f'(()=>{{const o={{v:{c0}}}, el=document.querySelector("{s} .ls-ctr .n"); if(!el) return; '
             f'tl.to(o, {{v:{c1}, duration:{t_e - t_s:.2f}, ease:"none", onUpdate:()=>{{el.textContent=String(Math.round(o.v)).padStart({pad},"0");}}}}, {t_s:.3f});}})();')
        X.tw(f'tl.fromTo("{s} .ls-ctr", {{scale:1}}, {{keyframes:[{{scale:1.25, duration:0.1}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], immediateRender:false}}, {t_e:.3f});')
    if tag:
        X.tw(f'tl.from("{s} .ls-tag", {{y:30, scale:0.6, opacity:0, duration:0.45, ease:"back.out(2.4)"}}, {t_e + 0.05:.3f});')
        X.tw(f'tl.fromTo("{s} .ls-tag b", {{y:6}}, {{y:-6, duration:0.35, ease:"sine.inOut", yoyo:true, repeat:{max(1, int((t + d - t_e - 0.4) / 0.35))}, immediateRender:false}}, {t_e + 0.4:.3f});')
        X.sfx(t_e + 0.05, "pop")


FX = {"log_scroll": log_scroll}
