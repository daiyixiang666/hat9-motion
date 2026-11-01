"""一句话十个数字，自动拆页 Number Pages (财经快讯的数据条；小Lin说 / 所长林超 一口气报数时的数字卡分页):
a sentence crammed with numbers is pulled apart: the sentence runs along the top as a ticker with the numbers
being read lit up, and below it the numbers become big count-up cards, two or three per page, page by page,
each with its own label. Nothing is dropped: ten numbers make four or five pages.

Adapts: 1–20 numbers parsed from the text (units 亿 / 億 / 万 / 萬 / % / 家 / 元 / 杯 / 倍 / 个 / 個 … kept; a year
such as "2024 年" is a date, not a figure: it stays in the sentence and labels the next number), or given as items;
per page 3 (16:9) / 2 (9:16), fewer when labels are long, pages balanced (10 → 3·3·2·2); numbers keep their
decimals and thousands separators while counting; the last number still gets ~1.5 s on screen.
p: text · items ([[label, value, unit], …], instead of parsing) · per_page · at · title
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit
from h9.core import esc

CSS = """
.fx .np { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .np .np-tk { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.5; }
.fx .np .np-tk .n { color:var(--fg); font-weight:800; background-image:linear-gradient(var(--accent), var(--accent)); background-repeat:no-repeat;
  background-position:0 92%; background-size:0% 0.28em; }
.fx .np .np-card { position:absolute; border-top:.5vmin solid var(--fg); }
.fx .np .np-v { position:absolute; left:0; font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--fg); line-height:1; white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .np .np-v small { font-family:var(--f-display); font-weight:900; color:var(--accent); margin-left:.12em; }
.fx .np .np-l { position:absolute; left:0; font-family:var(--f-body); font-weight:700; color:var(--muted); line-height:1.3; }
.fx .np .np-i { position:absolute; right:0; font-family:var(--f-mono, monospace); color:var(--muted); }
.fx .np .np-pg { position:absolute; font-family:var(--f-mono, monospace); font-weight:600; color:var(--muted); white-space:nowrap; }
.fx .np .np-pg i { display:inline-block; width:2.2vmin; height:.5vmin; margin-right:.6vmin; background:color-mix(in srgb, var(--fg) 18%, transparent); vertical-align:middle; }
.fx .np .np-pg i b { display:block; height:100%; background:var(--accent); opacity:0; }
"""


def number_pages(X, cid, t, d, p):
    P = X.portrait
    text = fit.as_text(p.get("text") or "")
    if p.get("items"):
        nums = []
        for it in fit.as_list(p["items"]):
            it = list(it) if isinstance(it, (list, tuple)) else [it]
            lab = str(it[0]) if len(it) > 1 else ""
            val = str(it[1] if len(it) > 1 else it[0]); unit = str(it[2]) if len(it) > 2 else ""
            sign = "-" if val.startswith("-") else ("+" if val.startswith("+") else "")
            nums.append((lab, sign, val.lstrip("+-"), unit))
    else:
        nums = T2.numbers(text)
    nums = nums[:20] or [("", "", "0", "")]
    N = len(nums)
    x, y, w, h = S.box(X, p)
    per = int(p.get("per_page") or (2 if P else 3))
    if not P and max(len(n[0]) for n in nums) > 9: per = min(per, 2)
    # balanced pages (10 numbers at 3 a page → 3 · 3 · 2 · 2, never a lonely last card)
    npg = -(-N // per)
    sizes = [N // npg + (1 if i < N % npg else 0) for i in range(npg)]
    starts = [sum(sizes[:i]) for i in range(npg + 1)]
    pages = [nums[starts[i]:starts[i + 1]] for i in range(npg)]
    # ticker: the sentence (or the labels joined) at the top
    tick = text or "，".join(f"{a}{s}{v}{u}" for a, s, v, u in nums)
    tkpx = S.vm(X, 3.0 if P else 2.6)
    tkf = fit.fit_text(tick, w, tkpx * 1.5 * (3 if P else 2), tkpx, S.vm(X, 2.6), max_lines=3, lh=1.5)
    tk_h = tkf.n * tkf.px * 1.5
    gap = S.vm(X, 3)
    top = y + tk_h + gap * 1.4
    area_h = h - (top - y) - S.vm(X, 4)
    if P:
        cw, ch = w, min(area_h / per - gap, S.vm(X, 30))
    else:
        cw, ch = (w - gap * (per - 1)) / per, min(area_h, S.vm(X, 34))
    vpx = min(ch * 0.5, S.vm(X, 15 if P else 12))
    X.css("fx-np", CSS)
    html = []
    # ticker with each number wrapped so it can light up when read (the browser wraps it at the fitted size)
    joined = T2.mark_numbers(text) if text else esc(tick)
    html.append(f'<div class="np-tk" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; font-size:{tkf.px}px">{joined}</div>')
    for pi, pg in enumerate(pages):
        for j, (lab, sign, val, unit) in enumerate(pg):
            idx = starts[pi] + j
            if P: cx_, cy_ = x, top + j * (ch + gap)
            else: cx_, cy_ = x + j * (cw + gap), top + (area_h - ch) / 2
            vtxt = f"{sign}{val}"
            vw = fit.width(vtxt) * 0.95 + (fit.width(unit) * 0.45 if unit else 0)
            v_px = min(vpx, cw * 0.92 / max(vw, 1))
            lf = fit.fit_text(lab or " ", cw, ch * 0.3, S.vm(X, 3.4 if P else 2.8), S.vm(X, 2.6), max_lines=2, lh=1.3)
            html.append(f'<div class="np-card" data-p="{pi}" data-i="{idx}" style="left:{cx_:.0f}px; top:{cy_:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; opacity:0">'
                        f'<div class="np-v" style="top:{S.vm(X, 2.4):.0f}px; font-size:{v_px:.0f}px"><span class="v">{esc(sign)}0</span>{f"<small style=font-size:{v_px * 0.42:.0f}px>{esc(unit)}</small>" if unit else ""}</div>'
                        f'<div class="np-l" style="top:{S.vm(X, 2.4) + v_px * 1.12:.0f}px; width:{cw:.0f}px; font-size:{lf.px}px">{"<br>".join(X.rich(l) for l in lf.lines)}</div>'
                        f'<div class="np-i" data-layout-ignore style="top:{S.vm(X, 1):.0f}px; font-size:{S.vm(X, 1.8):.0f}px">{idx + 1:02d}/{N:02d}</div></div>')
    if len(pages) > 1:
        dots = "".join(f'<i data-p="{i}"><b></b></i>' for i in range(len(pages)))
        html.append(f'<div class="np-pg" style="left:{x:.0f}px; top:{y + h - S.vm(X, 2.6):.0f}px; font-size:{S.vm(X, 2):.0f}px">{dots}</div>')
    _clip(X, cid, t, d, f'<div class="np">{"".join(html)}</div>', p)
    s = f"#{cid} .np"
    X.tw(f'tl.from("{s} .np-tk", {{opacity:0, y:-14, duration:0.45, ease:"expo.out"}}, {t + 0.05:.3f});')
    # timing: one moment per number
    at = fit.as_list(p.get("at"))
    times = None
    if at and X.chars:
        try: times = [float(X.T(at[i], t)) for i in range(N)] if len(at) >= N else None
        except SystemExit: times = None
    if not times:
        span = max(0.6, d - 2.0)      # the last number still gets ~1.5 s on screen
        times = [t + 0.45 + span * i / max(N - 1, 1) for i in range(N)]
    for pi, pg in enumerate(pages):
        a = times[starts[pi]] - 0.15
        # the page clears before the next one deals in (but never before its last card is in)
        b = max(times[starts[pi + 1]] - 0.42, times[starts[pi + 1] - 1] - 0.13) if pi + 1 < len(pages) else None
        if len(pages) > 1:
            X.tw(f'tl.to("{s} .np-pg i[data-p=\'{pi}\'] b", {{opacity:1, duration:0.2}}, {a:.3f});')
        for j in range(len(pg)):
            idx = starts[pi] + j
            ti = times[idx]
            sel = f'{s} .np-card[data-i=\'{idx}\']'
            de = 0.45 if b is None else max(0.05, min(0.45, b - (ti - 0.2) - 0.02))     # in before the page turns
            X.tw(f'tl.fromTo("{sel}", {{opacity:0, y:{S.vm(X, 4):.0f}}}, {{opacity:1, y:0, duration:{de:.2f}, ease:"expo.out", immediateRender:false}}, {ti - 0.2:.3f});')
            T2.counter(X, f"{sel} .v", ti - 0.15, pg[j][2], dur=0.7, sign=pg[j][1])
            X.tw(f'tl.to("{s} .np-tk .n[data-k=\'{idx}\']", {{backgroundSize:"100% 0.28em", duration:0.35}}, {ti - 0.1:.3f});')
            X.sfx(ti - 0.15, "count")
            if b is not None:
                X.tw(f'tl.to("{sel}", {{opacity:0, y:-{S.vm(X, 3):.0f}, duration:0.2, ease:"power2.in"}}, {b:.3f});')


FX = {"number_pages": number_pages}
