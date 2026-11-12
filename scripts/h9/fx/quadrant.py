"""象限图 2×2 Quadrant (咨询式定位图，商业拆解里讲「谁在哪个位置」; talkcraft chip-grid-single-select; VideoHive
Infographics 的 Matrix / Positioning Map): the axes draw out from the centre, axis words land at the ends, the
four quadrant names fade in as a watermark, then each brand drops onto its spot; the highlighted one gets a pulse
ring and its quadrant warms.

Adapts: 1–12 items placed by x / y (0–100), labels a word to a phrase (fitted, flipped to the left near the right
edge), optional quadrant names, axis words any length; square plot sized to the free area in both aspects.
p: items [{"text", "x", "y"}] · x_axis ["低", "高"] · y_axis ["低", "高"] · quads [TL, TR, BL, BR] · hl · note
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .qd { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .qd .qd-ax { position:absolute; background:var(--fg); }
.fx .qd .qd-al { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--muted); white-space:nowrap; }
.fx .qd .qd-q { position:absolute; overflow:visible; font-family:var(--f-display); font-weight:800; color:color-mix(in srgb, var(--fg) 42%, transparent); }
.fx .qd .qd-q span { position:absolute; white-space:nowrap; }
.fx .qd .qd-q.hot { background:color-mix(in srgb, var(--accent) 16%, transparent); } .fx .qd .qd-q.hot span { color:var(--accent); }
.fx .qd .qd-d { position:absolute; width:0; height:0; }
.fx .qd .qd-d i { position:absolute; border-radius:50%; background:var(--fg); }
.fx .qd .qd-d .rg { position:absolute; border-radius:50%; border:.45vmin solid var(--accent); opacity:0; }
.fx .qd .qd-d b { position:absolute; top:0; font-family:var(--f-display); font-weight:800; color:var(--fg); white-space:nowrap; transform:translateY(-50%); }
.fx .qd .qd-d.hl i { background:var(--accent); }
.fx .qd .qd-n { position:absolute; font-family:var(--f-mono, monospace); color:var(--muted); white-space:nowrap; }
"""


def quadrant(X, cid, t, d, p):
    its = []
    for it in fit.as_list(p.get("items"))[:12]:
        if isinstance(it, dict): its.append((str(it.get("text") or it.get("name") or ""), float(it.get("x", 50)), float(it.get("y", 50))))
        else: its.append((str(it[0]), float(it[1]), float(it[2])))
    its = its or [("A", 70, 70)]
    xa = (fit.as_list(p.get("x_axis")) + ["低", "高"])[:2] if p.get("x_axis") else ["低", "高"]
    ya = (fit.as_list(p.get("y_axis")) + ["低", "高"])[:2] if p.get("y_axis") else ["低", "高"]
    quads = (fit.as_list(p.get("quads")) + ["", "", "", ""])[:4]
    hl = int(p.get("hl", -1))
    x, y, w, h = S.box(X, p)
    apx = S.vm(X, 3)
    side = min(w * (0.66 if not X.portrait else 0.94), h - apx * 5.6)
    px0, py0 = x + (w - side) / 2, y + apx * 2.2 + (h - apx * 5.6 - side) / 2
    cx, cy = px0 + side / 2, py0 + side / 2
    X.css("fx-qd", CSS)
    lw = max(3, S.vm(X, 0.45))
    html = [f'<i class="qd-ax h" style="left:{px0:.0f}px; top:{cy - lw / 2:.0f}px; width:{side:.0f}px; height:{lw:.0f}px"></i>',
            f'<i class="qd-ax v" style="left:{cx - lw / 2:.0f}px; top:{py0:.0f}px; width:{lw:.0f}px; height:{side:.0f}px"></i>',
            f'<div class="qd-al" style="left:{px0:.0f}px; top:{cy + apx * 0.6:.0f}px; font-size:{apx:.0f}px">{X.rich(xa[0])}</div>',
            f'<div class="qd-al" style="left:{px0 + side:.0f}px; top:{cy + apx * 0.6:.0f}px; font-size:{apx:.0f}px; transform:translateX(-100%)">{X.rich(xa[1])} →</div>',
            f'<div class="qd-al" style="left:{cx + apx * 0.6:.0f}px; top:{py0 + side - apx * 1.4:.0f}px; font-size:{apx:.0f}px">{X.rich(ya[0])}</div>',
            f'<div class="qd-al" style="left:{cx + apx * 0.6:.0f}px; top:{py0:.0f}px; font-size:{apx:.0f}px">↑ {X.rich(ya[1])}</div>']
    qs = side / 2
    qpx = min(S.vm(X, 2.8), qs * 0.8 / max(max(fit.width(q) for q in quads) or 1, 1))
    corner = ["left:0; bottom:calc(100% + {m}px)", "right:0; bottom:calc(100% + {m}px)", "left:0; top:calc(100% + {m}px)", "right:0; top:calc(100% + {m}px)"]   # names sit just outside the plot
    hot_q = -1
    if 0 <= hl < len(its): hot_q = (0 if its[hl][2] >= 50 else 2) + (1 if its[hl][1] >= 50 else 0)
    for k, q in enumerate(quads):
        qx = px0 + (k % 2) * qs; qy = py0 + (k // 2) * qs
        m = round(qpx * 0.6)
        html.append(f'<div class="qd-q{" hot" if k == hot_q else ""}" data-k="{k}" style="left:{qx:.0f}px; top:{qy:.0f}px; width:{qs:.0f}px; height:{qs:.0f}px; font-size:{qpx:.0f}px">'
                    f'<span style="{corner[k].format(m=m)}">{X.rich(q)}</span></div>')
    dpx = S.vm(X, 2.2)
    lpx = min(S.vm(X, 3.6), S.fitpx([a for a, _, _ in its], side * 0.42, apx * 1.6, S.vm(X, 3.6), S.vm(X, 2.4), max_lines=1)[0])
    if len(its) > 6: lpx = min(lpx, S.vm(X, 2.8))
    dots = [(px0 + side * max(0, min(100, vx)) / 100, py0 + side * (1 - max(0, min(100, vy)) / 100)) for _, vx, vy in its]
    # obstacles: axis words, the axes, every dot
    obs = [(px0, cy + apx * 0.5, fit.width(xa[0]) * apx, apx * 1.3), (px0 + side - (fit.width(xa[1]) + 1.2) * apx, cy + apx * 0.5, (fit.width(xa[1]) + 1.2) * apx, apx * 1.3),
           (cx + apx * 0.5, py0, (fit.width(ya[1]) + 1.2) * apx, apx * 1.3), (cx + apx * 0.5, py0 + side - apx * 1.4, fit.width(ya[0]) * apx, apx * 1.3)]
    obs += [(dx - dpx, dy - dpx, dpx * 2, dpx * 2) for dx, dy in dots]
    obs += [(px0, cy - 3, side, 6), (cx - 3, py0, 6, side)]          # the axes themselves
    cands = []
    for (a, _, _), (dx, dy) in zip(its, dots):
        lw_, lh2 = fit.width(a) * lpx + 4, lpx * 1.25
        g_ = dpx * 0.9
        cands.append([(dx + g_, dy - lh2 / 2, lw_, lh2), (dx - g_ - lw_, dy - lh2 / 2, lw_, lh2),
                      (dx - lw_ / 2, dy - g_ - lh2, lw_, lh2), (dx - lw_ / 2, dy + g_, lw_, lh2),
                      (dx + g_, dy - lh2 - g_ * 0.4, lw_, lh2), (dx - g_ - lw_, dy + g_ * 0.4, lw_, lh2)])
    pick = S.place_labels(cands, obs, X.W, X.H)
    for k, (a, vx, vy) in enumerate(its):
        dx, dy = dots[k]
        bx_, by_, _, _ = cands[k][pick[k]]
        lab = f'<b style="left:{bx_ - dx:.0f}px; top:{by_ - dy:.0f}px; transform:none; font-size:{lpx:.0f}px">{X.rich(a)}</b>'
        html.append(f'<div class="qd-d{" hl" if k == hl else ""}" data-k="{k}" style="left:{dx:.0f}px; top:{dy:.0f}px">'
                    f'<i style="left:{-dpx / 2:.0f}px; top:{-dpx / 2:.0f}px; width:{dpx:.0f}px; height:{dpx:.0f}px"></i>'
                    f'<span class="rg" style="left:{-dpx * 1.6:.0f}px; top:{-dpx * 1.6:.0f}px; width:{dpx * 3.2:.0f}px; height:{dpx * 3.2:.0f}px"></span>{lab}</div>')
    if p.get("note"):
        html.append(f'<div class="qd-n" style="left:{px0:.0f}px; top:{py0 + side + apx * 1.9:.0f}px; font-size:{S.vm(X, 2):.0f}px">{X.rich(p["note"])}</div>')
    _clip(X, cid, t, d, f'<div class="qd">{"".join(html)}</div>', p)
    s = f"#{cid} .qd"
    X.tw(f'tl.from("{s} .qd-ax.h", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .qd-ax.v", {{scaleY:0, duration:0.6, ease:"expo.inOut"}}, {t + 0.12:.3f});')
    X.tw(f'tl.from("{s} .qd-al", {{opacity:0, duration:0.4, stagger:0.06}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .qd-q", {{opacity:0, scale:0.92, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.45:.3f});')
    item_texts = [a for a, _, _ in its]
    T = S.beats(X, p, t, d, len(its), start=0.8, share=0.5, texts=item_texts)
    for k, tk in enumerate(T):
        X.tw(f'tl.from("{s} .qd-d[data-k=\'{k}\'] i", {{scale:0, y:-40, duration:0.5, ease:"bounce.out"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .qd-d[data-k=\'{k}\'] b", {{opacity:0, duration:0.4, ease:"power2.out"}}, {tk + 0.15:.3f});')
        X.sfx(tk, "pop")
    if 0 <= hl < len(its):
        th = T[-1] + 0.5
        X.tw(f'tl.fromTo("{s} .qd-d[data-k=\'{hl}\'] .rg", {{scale:0.4, opacity:1}}, {{scale:1.6, opacity:0, duration:0.9, ease:"power2.out", repeat:1, immediateRender:false}}, {th:.3f});')
        X.tw(f'tl.from("{s} .qd-q.hot", {{backgroundColor:"rgba(0,0,0,0)", duration:0.5}}, {th:.3f});')
        X.sfx(th, "hit")
    X.tw(f'tl.fromTo("{s}", {{scale:1}}, {{scale:1.025, duration:{d:.2f}, ease:"none", transformOrigin:"50% 50%"}}, {t:.3f});')


FX = {"quadrant": quadrant}
