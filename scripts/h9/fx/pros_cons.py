"""优缺点两栏 Pros & Cons (测评 / 对比类口播的标配; Envato Elements「Checklist Pack」; talkcraft chip-grid-single-select):
two columns under ✓ and ✗ headers; points drop in alternately so the viewer weighs them one against the other,
then an optional verdict bar slides up across both columns.

Adapts: 1–8 points per side (sides may differ in count), each a word to a sentence (one shared size, ≤ 2 lines),
side-by-side in 16:9, stacked in 9:16; custom headers.
p: pros [..] · cons [..] · labels ["优点", "缺点"] · verdict
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .pc { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .pc .pc-h { position:absolute; display:flex; align-items:center; gap:1.6vmin; font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; }
.fx .pc .pc-h i { display:grid; place-items:center; border-radius:50%; font-style:normal; color:var(--bg); }
.fx .pc .pc-h.pro i { background:var(--accent); } .fx .pc .pc-h.con i { background:var(--fg); }
.fx .pc .pc-rule { position:absolute; height:.45vmin; background:var(--fg); transform-origin:0 50%; }
.fx .pc .pc-i { position:absolute; display:flex; gap:1.6vmin; align-items:flex-start; font-family:var(--f-display); font-weight:700; color:var(--fg); line-height:1.25; }
.fx .pc .pc-i b { flex:none; font-weight:900; }
.fx .pc .pc-i.pro b { color:var(--accent); } .fx .pc .pc-i.con b { color:var(--muted); }
.fx .pc .pc-i .sl { display:block; white-space:nowrap; }
.fx .pc .pc-v { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; line-height:1.2; border-radius:1vmin; background:var(--fg); color:var(--bg);
  font-family:var(--f-display); font-weight:900; }
.fx .pc .pc-v .sl { display:block; white-space:nowrap; }
"""


def pros_cons(X, cid, t, d, p):
    pros = S.flat(p.get("pros"))[:8] or ["优点"]
    cons = S.flat(p.get("cons"))[:8] or ["缺点"]
    labels = (fit.as_list(p.get("labels")) + ["优点", "缺点"])[:2] if p.get("labels") else ["优点", "缺点"]
    verdict = fit.as_text(p.get("verdict"))
    x, y, w, h = S.box(X, p)
    P = X.portrait
    vh = (S.vm(X, 12) if verdict else 0)
    hh = S.vm(X, 9)
    if not P:
        gx = S.vm(X, 6); colw = (w - gx) / 2
        cols = [(x, y, colw, h - vh), (x + colw + gx, y, colw, h - vh)]
    else:
        gy = S.vm(X, 5); colh = (h - vh - gy) / 2
        cols = [(x, y, w, colh), (x, y + colh + gy, w, colh)]
    m = max(len(pros), len(cons))
    rh = min((cols[0][3] - hh) / m, S.vm(X, 14) if P else S.vm(X, 18 if m <= 3 else 14 if m <= 5 else 11))
    if not P:            # few points: the block sits in the middle of the page instead of hanging from the top
        used = hh + m * rh + vh
        off = max(0, (h - used) / 2) * 0.9
        cols = [(cx_, cy_ + off, cw_, ch_) for cx_, cy_, cw_, ch_ in cols]
        y = y + off; h = used
    tw = cols[0][2] - S.vm(X, 7)
    tpx, fs_all = S.fitpx(pros + cons, tw, rh * 0.82, S.vm(X, 6) if P else S.vm(X, 6.4 if m <= 3 else 5.2 if m <= 5 else 4.4), S.vm(X, 2.7), max_lines=2)
    fsp, fsc = fs_all[:len(pros)], fs_all[len(pros):]
    X.css("fx-pc", CSS)
    html = []
    hpx = S.vm(X, 6.4 if P else (6.4 if m <= 3 else 5.6))
    for side, (cx, cy, cw, ch), lab, mark, items_, fs in ((0, cols[0], labels[0], "✓", pros, fsp), (1, cols[1], labels[1], "✗", cons, fsc)):
        cls = "pro" if side == 0 else "con"
        html.append(f'<div class="pc-h {cls}" style="left:{cx:.0f}px; top:{cy:.0f}px; font-size:{hpx:.0f}px"><i style="width:{hpx * 1.2:.0f}px; height:{hpx * 1.2:.0f}px; font-size:{hpx * 0.7:.0f}px">{mark}</i>{X.rich(lab)}</div>')
        html.append(f'<i class="pc-rule {cls}" style="left:{cx:.0f}px; top:{cy + hpx * 1.45:.0f}px; width:{cw:.0f}px"></i>')
        for k, f in enumerate(fs):
            html.append(f'<div class="pc-i {cls}" data-s="{side}" data-k="{k}" style="left:{cx:.0f}px; top:{cy + hh + k * rh:.0f}px; width:{cw:.0f}px; font-size:{tpx}px">'
                        f'<b>{"+" if side == 0 else "−"}</b><div>{S.lines(X, f)}</div></div>')
    if verdict:
        vf = fit.fit_text(verdict, w * 0.86, (vh - S.vm(X, 2)) * 0.82, S.vm(X, 4.6), S.vm(X, 2.6), max_lines=2, lh=1.2)
        html.append(f'<div class="pc-v" style="left:{x:.0f}px; top:{y + h - vh + S.vm(X, 2):.0f}px; width:{w:.0f}px; height:{vh - S.vm(X, 2):.0f}px; font-size:{vf.px}px">{S.lines(X, vf)}</div>')
    _clip(X, cid, t, d, f'<div class="pc">{"".join(html)}</div>', p)
    s = f"#{cid} .pc"
    X.tw(f'tl.from("{s} .pc-h", {{y:-30, opacity:0, duration:0.5, ease:"expo.out", stagger:0.12}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .pc-rule", {{scaleX:0, duration:0.6, ease:"expo.inOut", stagger:0.12}}, {t + 0.15:.3f});')
    order = []
    for k in range(m):
        if k < len(pros): order.append((0, k))
        if k < len(cons): order.append((1, k))
    item_texts = []
    for side, k in order:
        item_texts.append(pros[k] if side == 0 else cons[k])
    T = S.beats(X, p, t, d, len(order), start=0.55, share=0.55 if verdict else 0.62, texts=item_texts)
    for (side, k), tk in zip(order, T):
        X.tw(f'tl.from("{s} .pc-i[data-s=\'{side}\'][data-k=\'{k}\']", {{x:{-40 if side == 0 else 40}, opacity:0, duration:0.45, ease:"expo.out"}}, {tk:.3f});')
        X.sfx(tk, "click")
    if verdict:
        tv = T[-1] + 0.5
        X.tw(f'tl.from("{s} .pc-v", {{yPercent:60, opacity:0, duration:0.55, ease:"back.out(1.6)"}}, {tv:.3f});')
        X.sfx(tv, "hit")


FX = {"pros_cons": pros_cons}
