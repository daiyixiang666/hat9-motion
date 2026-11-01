"""几个选项里选中一个 Pick one (Envato Elements「Elements」Popular: Checklist Pack, Search Bars; the quiz / poll card
of every knowledge channel): the question lands, option cards deal in, a selection frame hops across them —
fast, then slowing like a wheel — and settles on the answer; the others dim, the pick lifts with a tick, and each
card's number (if given) counts up so the viewer sees why.

Adapts: 2–8 options (grid from the count and the frame; 9:16 stacks), labels from a glyph to a phrase (fitted),
optional sub line and value per option (any magnitude, 万 / 亿), pick by index or label; the hop path is seeded,
so every render is identical.
p: q · options [label | [label, value] | {label, sub, value}] · pick · unit · title · note · mock · hops
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


def choose_one(X, cid, t, d, p):
    W.base(X)
    opts = []
    for o in p["options"][:8]:
        if isinstance(o, dict): opts.append((str(o.get("label", "")), o.get("sub", ""), W.num(o.get("value"))))
        elif isinstance(o, (list, tuple)): opts.append((str(o[0]), o[2] if len(o) > 2 else "", W.num(o[1]) if len(o) > 1 else None))
        else: opts.append((str(o), "", None))
    n = len(opts)
    pk = p.get("pick", 0)
    pick = next((i for i, o in enumerate(opts) if o[0] == str(pk)), None) if isinstance(pk, str) else int(pk)
    pick = pick if pick is not None and 0 <= pick < n else 0
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    qs, ql = W.fit_px(X, p.get("q", ""), x1 - x0, 150, 60 if not P else 54, 28, 2)
    top = y0 + (qs * 1.15 * len(ql) + 30 if ql else 0)
    if P: cols = 1 if n <= 4 else 2
    else: cols = n if n <= 4 else math.ceil(n / 2)
    rows = math.ceil(n / cols)
    gap = 24
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    ch = min(260 if not P else 200, (y1 - top - gap * (rows - 1)) / rows)
    oy = top + max(0, (y1 - top - (ch * rows + gap * (rows - 1))) / 2)
    vals = [o[2] for o in opts if o[2] is not None]
    div, suf = W.F.compact(max(abs(v) for v in vals)) if vals else (1, "")
    unit = suf + p.get("unit", "")
    dec = int(p.get("dec", W.dec_of([v / div for v in vals]) if vals else 0))
    cards = []
    for i, (lab, sub, v) in enumerate(opts):
        r, c = divmod(i, cols)
        x, y = x0 + c * (cw + gap), oy + r * (ch + gap)
        ls, ll = W.fit_px(X, lab, cw - 60, ch * 0.42, 52 if not P else 44, 22, 2)
        val = f'<div class="cov w3k"><span class="n">0</span><small>{X.rich(unit)}</small></div>' if v is not None else ""
        cards.append(f'<div class="coc{" pk" if i == pick else ""}" data-i="{i}" style="left:{x:.0f}px; top:{y:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">'
                     f'<i class="cok">{chr(65 + i)}</i><div class="col" style="font-size:{ls:.0f}px">{W.lines_html(X, ll)}</div>'
                     + (f'<div class="cos">{X.rich(sub)}</div>' if sub else "") + val
                     + f'<i class="coy">{W.icon_svg("check")}</i></div>')
    X.css("fx-choose", """
.fx .co .coq { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.15; } .fx .co .coq .fl { display:block; white-space:nowrap; }
.fx .co .coc { position:absolute; text-align:left; align-items:flex-start; border-radius:14px; background:var(--card); border:3px solid color-mix(in srgb, var(--fg) 14%, transparent); padding:22px 26px;
  display:flex; flex-direction:column; justify-content:center; gap:8px; color:var(--card-fg); }
.fx .co .cok { position:absolute; left:18px; top:14px; font:800 20px var(--f-mono, monospace); color:var(--muted); font-style:normal; }
.fx .co .col { font-family:var(--f-display); font-weight:900; line-height:1.15; } .fx .co .col .fl { display:block; white-space:nowrap; }
.fx .co .cos { font:500 20px var(--f-body); color:var(--muted); }
.fx .co .cov { font-size:42px; color:var(--muted); } .fx .co .cov small { font-size:.5em; margin-left:.1em; }
.fx .co .coc.pk .cov { color:var(--accent); }
.fx .co .coy { position:absolute; right:16px; top:14px; width:40px; height:40px; border-radius:50%; background:var(--accent); display:grid; place-items:center; opacity:0; }
.fx .co .coy svg { width:26px; height:26px; fill:none; stroke:var(--bg); stroke-width:3.4; stroke-linecap:round; stroke-linejoin:round; }
.fx .co .cosel { position:absolute; border:5px solid var(--accent); border-radius:18px; pointer-events:none; box-shadow:0 0 0 4px color-mix(in srgb, var(--accent) 25%, transparent); }
""")
    # selection frame: one element moved (transform) over a seeded hop path that slows down
    rnd = W.rand(p, 31)
    hops = int(p.get("hops", 7 if n > 2 else 5))
    path, last = [], -1
    for h in range(hops - 1):
        c = rnd.randrange(n)
        while c == last and n > 1: c = rnd.randrange(n)
        path.append(c); last = c
    if path and path[-1] == pick and n > 1: path[-1] = (pick + 1) % n
    path.append(pick)
    pos = []
    for i in range(n):
        r, c = divmod(i, cols)
        pos.append((x0 + c * (cw + gap) - 8, oy + r * (ch + gap) - 8))
    sel = f'<i class="cosel" style="left:0; top:0; width:{cw + 16:.0f}px; height:{ch + 16:.0f}px"></i>'
    inner = (f'<div class="w3 co"><div class="coq" style="left:{x0}px; top:{y0}px; font-size:{qs:.0f}px">{W.lines_html(X, ql)}</div>'
             f'{"".join(cards)}{sel}{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    X.used_text.update("ABCDEFGH0123456789.,")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .coq .fl", {{yPercent:60, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t:.3f});')
    X.tw(f'tl.from("{s} .coc", {{y:50, opacity:0, rotation:-3, duration:0.5, ease:"back.out(1.8)", stagger:0.08}}, {t + 0.2:.3f});')
    th = t + 0.3 + n * 0.08 + 0.3
    X.tw(f'tl.set("{s} .cosel", {{x:{pos[path[0]][0]:.0f}, y:{pos[path[0]][1]:.0f}}}, {t:.3f});')
    X.tw(f'tl.from("{s} .cosel", {{opacity:0, duration:0.2}}, {th:.3f});')
    span = min(2.0, max(1.0, d * 0.4))
    # durations grow geometrically (wheel slowing down)
    k = len(path) - 1
    ws = [1.35 ** j for j in range(k)]
    tot = sum(ws) or 1
    tt = th + 0.15
    for j in range(1, len(path)):
        dur = span * ws[j - 1] / tot
        x, y = pos[path[j]]
        X.tw(f'tl.to("{s} .cosel", {{x:{x:.0f}, y:{y:.0f}, duration:{dur * 0.7:.3f}, ease:"power2.out"}}, {tt:.3f});')
        X.sfx(tt, "tick")
        tt += dur
    X.tw(f'tl.to("{s} .coc:not(.pk)", {{opacity:0.38, scale:0.97, duration:0.4}}, {tt:.3f});')
    X.tw(f'tl.fromTo("{s} .coc.pk", {{scale:1}}, {{keyframes:[{{scale:1.08, duration:0.14}}, {{scale:1.04, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tt:.3f});')
    X.tw(f'tl.to("{s} .cosel", {{scale:1.04, transformOrigin:"50% 50%", duration:0.35, ease:"back.out(3)"}}, {tt:.3f});')
    X.tw(f'tl.to("{s} .coc.pk .coy", {{opacity:1, duration:0.2}}, {tt + 0.05:.3f});')
    X.tw(f'tl.from("{s} .coc.pk .coy", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {tt + 0.05:.3f});')
    X.sfx(tt, "hit")
    for i, (_, _, v) in enumerate(opts):
        if v is not None: W.count(X, f"{s} .coc[data-i=\'{i}\'] .n", tt + 0.1, v / div, dur=0.8, dec=dec)


FX = {"choose_one": choose_one}
