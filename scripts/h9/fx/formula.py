"""公式卡 Formula Card (「净利率 = 净利润 ÷ 收入」; T1 kinetic-type family — the term-flip move of Vox / 回形针 explainers,
Envato Popular「Infographic」packs): the formula sets in words, each term flips over to show its number, the operators
pulse as the arithmetic runs, and the result slams in on its own line, counting, with an accent underline.

Adapts: 1–5 terms with any operators (+ − × ÷ =), term names from 1 glyph to a phrase and numbers of any length (the
whole line is fitted; in 9:16 or when too long it wraps the right-hand side under the left), result as a number
(counts) or text. p: lhs · terms [[name, value], ...] · ops ["÷", ...] · result · unit · dec · note · t_flip · t_result
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]

CSS = """
.fx .dtf { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:3.4vmin; }
.fx .dtf .dtf-row { display:flex; align-items:center; justify-content:center; flex-wrap:wrap; gap:1.6vmin 2.2vmin; }
.fx .dtf .dtf-lhs { font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; }
.fx .dtf .dtf-op { font-family:var(--f-num, var(--f-display)); font-weight:700; color:var(--muted); }
.fx .dtf .dtf-term { position:relative; display:inline-grid; place-items:center; perspective:60vmin; }
.fx .dtf .dtf-term > span { grid-area:1/1; display:block; white-space:nowrap; padding:.4em .55em; border-radius:.35em; line-height:1; backface-visibility:hidden; }
.fx .dtf .dtf-term .fw { font-family:var(--f-display); font-weight:800; color:var(--fg); background:color-mix(in srgb, var(--fg) 7%, transparent); box-shadow:inset 0 0 0 .12em color-mix(in srgb, var(--fg) 18%, transparent); }
.fx .dtf .dtf-term .fv { font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--bg); background:var(--fg); font-variant-numeric:tabular-nums; }
.fx .dtf .dtf-res { display:flex; align-items:baseline; gap:2vmin; position:relative; }
.fx .dtf .dtf-res .eq { font-family:var(--f-num, var(--f-display)); font-weight:700; color:var(--muted); }
.fx .dtf .dtf-res b { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.9; color:var(--accent); font-variant-numeric:tabular-nums; }
.fx .dtf .dtf-res b small { font-size:.45em; margin-left:.08em; }
.fx .dtf .dtf-res i { position:absolute; left:0; right:0; bottom:-1.6vmin; height:1vmin; background:var(--accent); transform-origin:0 50%; border-radius:.5vmin; }
.fx .dtf .dtf-note { font:500 1.8vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.03em; text-align:center; }
"""


def formula(X, cid, t, d, p):
    terms = [(str(a), str(b)) for a, b in p.get("terms", [])][:5] or [("—", "—")]
    ops = (list(p.get("ops", [])) + ["÷"] * len(terms))[: len(terms) - 1]
    lhs = str(p.get("lhs", ""))
    res = str(p.get("result", ""))
    unit = str(p.get("unit", ""))
    bx, by, bw, bh = U.box(X)
    # one line if it fits at a decent size, otherwise lhs on its own line
    pad_em = 1.1 * len(terms) + 0.9 * len(ops) + 1.0
    words_em = sum(max(U.em(a), U.em(b)) for a, b in terms) + sum(U.em(o) for o in ops) + pad_em
    one_em = U.em(lhs) + U.em("=") + words_em
    size = min(6.2 if not X.portrait else 5.4, bw * 0.94 / max(one_em, 1))
    two = X.portrait or size < 3.6
    if two:
        size = min(6.0 if not X.portrait else 5.2, bw * 0.94 / max(words_em, U.em(lhs) * 1.2, 1))
    size = max(2.0, size)
    num = U.D.num(res)
    dec = int(p.get("dec", len(res.split(".")[1].rstrip("%")) if "." in res and num is not None else 0))
    pct = res.strip().endswith("%")
    rs = min(18.0 if not X.portrait else 15.0, bw * 0.7 / max(U.em(res + unit) + 1, 1), bh * 0.3)
    X.css("fx-dtf", CSS)
    tp = "".join(
        (f'<span class="dtf-op" data-o="{i - 1}" style="font-size:{size:.2f}vmin">{X.rich(ops[i - 1])}</span>' if i else "")
        + f'<span class="dtf-term" data-i="{i}" style="font-size:{size:.2f}vmin"><span class="fw">{X.rich(a)}</span><span class="fv">{X.rich(b)}</span></span>'
        for i, (a, b) in enumerate(terms))
    lhs_html = f'<span class="dtf-lhs" style="font-size:{size * 1.05:.2f}vmin">{X.rich(lhs)}</span><span class="dtf-op eq0" style="font-size:{size:.2f}vmin">=</span>'
    rows = (f'<div class="dtf-row">{lhs_html}</div><div class="dtf-row">{tp}</div>' if two else f'<div class="dtf-row">{lhs_html}{tp}</div>')
    shown = U.fmt(0, dec) if num is not None else X.rich(res)
    resh = (f'<div class="dtf-res"><span class="eq" style="font-size:{rs * 0.45:.2f}vmin">=</span><b style="font-size:{rs:.2f}vmin"><span class="n">{shown}</span>'
            f'<small>{"%" if pct else ""}{X.rich(unit)}</small></b><i></i></div>')
    note = f'<div class="dtf-note">{X.rich(p["note"])}</div>' if p.get("note") else ""
    X.used_text.update("=0123456789.,%+−×÷")
    inner = f'<div class="dtf" style="left:{bx:.2f}vmin; top:{by:.2f}vmin; width:{bw:.2f}vmin; height:{bh:.2f}vmin">{rows}{resh}{note}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .dtf-lhs, {s} .eq0", {{x:-40, opacity:0, duration:0.55, ease:"expo.out", stagger:0.08}}, {t:.3f});')
    X.tw(f'tl.from("{s} .dtf-term, {s} .dtf-op:not(.eq0)", {{y:30, opacity:0, duration:0.5, ease:"expo.out", stagger:0.07}}, {t + 0.2:.3f});')
    X.tw(f'tl.set("{s} .dtf-term .fv", {{rotationX:-90, opacity:0}}, {t:.3f});')
    tf = U.cue(X, p, "t_flip", t, t + max(0.9, min(1.6, d * 0.3)))
    step = min(0.32, max(0.18, (d * 0.3) / len(terms)))
    for i in range(len(terms)):
        ti = tf + i * step
        X.tw(f'tl.to("{s} .dtf-term[data-i=\'{i}\'] .fw", {{rotationX:90, opacity:0, duration:0.3, ease:"power2.in"}}, {ti:.3f});')
        X.tw(f'tl.to("{s} .dtf-term[data-i=\'{i}\'] .fv", {{rotationX:0, opacity:1, duration:0.4, ease:"back.out(2)"}}, {ti + 0.22:.3f});')
        X.sfx(ti + 0.22, "click")
        if i:
            X.tw(f'tl.fromTo("{s} .dtf-op[data-o=\'{i - 1}\']", {{scale:1}}, {{keyframes:[{{scale:1.4, duration:0.12}}, {{scale:1, duration:0.3}}], immediateRender:false}}, {ti + 0.1:.3f});')
    tr = max(tf + len(terms) * step + 0.45, U.cue(X, p, "t_result", t, 0))
    X.tw(f'tl.from("{s} .dtf-res", {{scale:1.6, opacity:0, filter:"blur(10px)", duration:0.45, ease:"expo.out"}}, {tr:.3f});')
    if num is not None:
        U.count(X, f"{s} .dtf-res .n", tr, 0, num, 0.7, dec)
    X.tw(f'tl.from("{s} .dtf-res i", {{scaleX:0, duration:0.5, ease:"expo.inOut"}}, {tr + 0.35:.3f});')
    if note: X.tw(f'tl.from("{s} .dtf-note", {{opacity:0, y:10, duration:0.4}}, {tr + 0.5:.3f});')
    X.sfx(tr, "slam")
    X.tw(f'tl.fromTo("{s} .dtf", {{scale:1}}, {{scale:1.04, transformOrigin:"50% 55%", duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


FX = {"formula": formula}
