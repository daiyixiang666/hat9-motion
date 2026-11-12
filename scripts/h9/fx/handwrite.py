"""手写笔记 (notes written by hand on a ruled sheet — a study-notes / 拆解笔记 look): line by line the ink runs out of a
pen tip at writing speed, then the *marked* words get a hand-drawn underline or circle; the sheet sits taped on the page.

p: lines (list) or text ("a|b|c") · paper ("lined" | "grid" | "plain" | "kraft") · ink ("blue" | "black" | "red" | "#hex") ·
   font (a handwriting id from assets/fonts.json: "lxgw-wenkai" default, "ma-shan-zheng", "long-cang", "zcool-kuaile", "caveat") ·
   mark ("underline" | "circle") · at (list: when each line starts) · title (written as the first, bigger line) · tilt (deg)
Adapts: 1–10 lines of 1 to ~30 glyphs (the hand size follows the longest line and the ruling follows the hand);
16:9 sheet to the left of centre, 9:16 sheet full width. For a photo of real notes or a whiteboard use doc_photo.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)

INK = {"blue": "#1f3c8f", "black": "#1b1b1b", "red": "#c1271b", "green": "#1d6b46"}
PAPER = {"lined": "#fbfaf4", "grid": "#fbfaf4", "plain": "#fbfaf4", "kraft": "#d9c7a3"}


def handwrite(X, cid, t, d, p):
    lines = fit.as_list(p.get("lines") or p.get("text"))
    lines = [str(l) for l in lines] or ["……"]
    title = fit.as_text(p.get("title"))
    font = p.get("font", "lxgw-wenkai")
    X.S["fonts"] = {**X.S.get("fonts", {}), "note": font}          # make the hand available to this build
    ink = INK.get(p.get("ink", "blue"), p.get("ink", "#1f3c8f"))
    paper = p.get("paper", "lined")
    x0, y0, x1, y1 = D.box(X, p, text=True)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    sw = bw * (0.94 if P else 0.62); shh = bh * (0.96 if P else 1.0)
    few = len(lines) + (1 if title else 0) <= 2
    if few: shh *= 0.7                                   # a line or two: a shorter note, bigger hand
    sx, sy = x0 + (bw - sw) / 2 if P else x0 + bw * 0.06, y0 + (bh - shh) / 2
    pad_x, pad_top = sw * 0.09, shh * 0.1
    rows = len(lines) + (1.6 if title else 0)
    widest = max(fit.width(fit.plain(l)) for l in lines) if lines else 1
    px = min(130 if few else 78, (sw - 2 * pad_x) / max(widest, 1) * 0.96, (shh - pad_top * 1.8) / (rows * 1.55))
    px = max(24, px)
    lh = px * 1.55
    tpx = min(px * 1.35, (sw - 2 * pad_x) / max(fit.width(title), 1) * 0.96) if title else 0
    tilt = float(p.get("tilt", -1.6))
    mark = p.get("mark", "underline")
    X.used_text.update("".join(lines) + title)
    rows_html = []
    y = pad_top
    if title:
        rows_html.append(f'<div class="hw-l hw-t" data-k="t" style="top:{y:.0f}px; left:{pad_x:.0f}px; font-size:{tpx:.0f}px; line-height:{tpx * 1.3:.0f}px">{X.rich(title)}</div>')
        y += tpx * 1.6
    for i, l in enumerate(lines):
        rows_html.append(f'<div class="hw-l" data-k="{i}" style="top:{y:.0f}px; left:{pad_x:.0f}px; font-size:{px:.0f}px; line-height:{lh:.0f}px">{X.rich(l)}</div>')
        y += lh
    ruling = {"lined": f"repeating-linear-gradient(180deg, transparent 0 {lh - 2:.0f}px, rgba(31,60,143,.18) {lh - 2:.0f}px {lh:.0f}px)",
              "grid": f"linear-gradient(90deg, rgba(31,60,143,.1) 1px, transparent 1px) 0 0/{lh / 2:.0f}px {lh / 2:.0f}px, linear-gradient(180deg, rgba(31,60,143,.1) 1px, transparent 1px) 0 0/{lh / 2:.0f}px {lh / 2:.0f}px",
              "plain": "none", "kraft": "none"}.get(paper, "none")
    sheet = (f'<div class="hw-sh" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{sw:.0f}px; height:{shh:.0f}px; --rot:{tilt}deg; background-color:{PAPER.get(paper, "#fbfaf4")};'
             f' background-image:{ruling}; background-position:0 {pad_top + (tpx * 1.6 if title else 0) - lh * 0.12:.0f}px; color:{ink}">'
             f'<i class="hw-margin" style="left:{pad_x * 0.62:.0f}px"></i>{"".join(rows_html)}<i class="hw-pen"></i></div>'
             f'<i class="hw-tape" style="left:{sx + sw / 2 - 70:.0f}px; top:{sy - 18:.0f}px"></i>')
    X.css("fx-d2", D.CSS)
    X.css("fx-handwrite", """
.hw-sh { position:absolute; transform:rotate(var(--rot)); box-shadow:0 2px 0 rgba(0,0,0,.06), 0 22px 54px rgba(0,0,0,.26); border-radius:3px; }
.hw-margin { position:absolute; top:0; bottom:0; width:2px; background:rgba(193,39,27,.35); }
.hw-l { position:absolute; white-space:nowrap; font-family:var(--f-note); font-weight:500; clip-path:inset(-20% 100% -40% 0); }
.hw-t { font-weight:700; }
.hw-l .em .emt { position:relative; z-index:1; }
.hw-l .em .emb { display:none; }
.hw-u { position:absolute; left:-4%; bottom:-.12em; width:108%; height:.42em; overflow:visible; pointer-events:none; }
.hw-u path { fill:none; stroke:currentColor; stroke-width:3.2; stroke-linecap:round; stroke-dasharray:1 1; stroke-dashoffset:1; }
.hw-c { position:absolute; left:-14%; top:-24%; width:128%; height:148%; overflow:visible; pointer-events:none; }
.hw-c path { fill:none; stroke:#c1271b; stroke-width:3; stroke-linecap:round; stroke-dasharray:1 1; stroke-dashoffset:1; }
.hw-pen { position:absolute; left:0; top:0; width:14px; height:14px; margin:-7px 0 0 -7px; border-radius:50%; background:currentColor; box-shadow:0 0 0 4px rgba(31,60,143,.15); opacity:0; }
.hw-tape { position:absolute; width:140px; height:36px; background:rgba(246,206,58,.55); transform:rotate(-3deg); box-shadow:0 2px 6px rgba(0,0,0,.12); }
""")
    # hand-drawn marks inside each *marked* run
    u = '<svg class="hw-u" viewBox="0 0 100 10" preserveAspectRatio="none"><path pathLength="1" d="M2 6 C 25 3, 50 8, 98 4"/></svg>'
    c = '<svg class="hw-c" viewBox="0 0 100 40" preserveAspectRatio="none"><path pathLength="1" d="M50 3 C 90 2, 99 18, 92 30 C 82 40, 18 40, 7 30 C -2 18, 12 4, 56 5"/></svg>'
    body = "".join(rows_html).replace('<i class="emb"></i>', u if mark == "underline" else c)
    sheet = sheet.replace("".join(rows_html), body)
    _clip(X, cid, t, d, f'<div class="d2 hw">{sheet}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .hw-sh, {S} .hw-tape", {{y:70, rotation:"-=3", opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.sfx(t, "paper")
    keys = (["t"] if title else []) + [str(i) for i in range(len(lines))]
    say = ([str(title)] if title else [])
    for ln in lines:
        say.append(str(ln))
    starts = D.times(X, p, t, d, len(keys), key="at", lead=0.5, tail=min(0.8, d * 0.18), texts=say)
    yrow = pad_top
    for j, k in enumerate(keys):
        txt = title if k == "t" else lines[int(k)]
        size = tpx if k == "t" else px
        wpx = fit.width(fit.plain(txt)) * size
        nxt = starts[j + 1] if j + 1 < len(keys) else t + d - 0.3
        dur = min(max(0.35, min(0.11 * len(fit.plain(txt)), nxt - starts[j] - 0.15)), nxt - starts[j] - 0.02)
        sel = f"{S} .hw-l[data-k='{k}']"
        X.tw(f'tl.to("{sel}", {{clipPath:"inset(-20% 0% -40% 0)", duration:{dur:.2f}, ease:"none"}}, {starts[j]:.3f});')
        X.tw(f'tl.set("{S} .hw-pen", {{x:{pad_x:.0f}, y:{yrow + size * 1.05:.0f}, opacity:1}}, {starts[j]:.3f});')
        X.tw(f'tl.to("{S} .hw-pen", {{x:{pad_x + wpx:.0f}, duration:{dur:.2f}, ease:"none"}}, {starts[j]:.3f});')
        if any(fit._parse(fit.as_text(txt))[1]): X.tw(f'tl.to("{sel} .hw-u path, {sel} .hw-c path", {{strokeDashoffset:0, duration:0.4, ease:"power2.inOut", stagger:0.15}}, {starts[j] + dur + 0.05:.3f});')
        X.sfx(starts[j], "brush" if j == 0 else "click")
        yrow += size * 1.6 if k == "t" else lh
    X.tw(f'tl.to("{S} .hw-pen", {{opacity:0, duration:0.2}}, {starts[-1] + max(0.35, min(0.11 * len(fit.plain(title if keys[-1] == "t" else lines[-1])), t + d - 0.45 - starts[-1])) + 0.05:.3f});')
    hold = starts[-1] + 1.0
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .hw-sh", {{scale:1.025, duration:{t + d - hold:.2f}, ease:"none"}}, {hold:.3f});')


FX = {"handwrite": handwrite}
