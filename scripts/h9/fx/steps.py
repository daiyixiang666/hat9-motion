"""步骤流程 Process Steps (talkcraft numbered-step-stack / step-timeline-vertical; VideoHive Infographics「Process / Steps」
是信息图包的标配; 教程类「三步做出……」): numbered nodes on one connector; the line draws to each step as it is
spoken, a light rides along it, the current node fills with the accent and swells, finished nodes turn solid,
labels lift in under (16:9) or beside (9:16) their node.

Adapts: 2–12 steps — one row up to 6 (16:9) / one column up to 6 (9:16), then a snake of two rows / columns;
labels a word to a sentence with an optional sub-line, one shared size (≤ 3 lines).
p: items ["…" | ["step", "sub"] | {"text", "sub"}] · title · hl (node left lit; default last) · at [cues]
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .sp { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .sp .sp-k { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .sp .sp-k .sl { display:block; white-space:nowrap; }
.fx .sp svg.sp-path { position:absolute; left:0; top:0; overflow:visible; }
.fx .sp svg.sp-path path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.fx .sp .sp-n { position:absolute; display:grid; place-items:center; border-radius:50%; font-family:var(--f-num, var(--f-display)); font-weight:900; font-variant-numeric:tabular-nums; }
.fx .sp .sp-n .ring { position:absolute; inset:0; border-radius:50%; border:.5vmin solid var(--fg); opacity:.35; }
.fx .sp .sp-n .fill { position:absolute; inset:0; border-radius:50%; background:var(--accent); }
.fx .sp .sp-n .done { position:absolute; inset:0; border-radius:50%; background:var(--fg); opacity:0; }
.fx .sp .sp-n b { position:relative; color:var(--fg); }
.fx .sp .sp-tok { position:absolute; left:0; top:0; border-radius:50%; background:var(--accent); box-shadow:0 0 0 .6vmin color-mix(in srgb, var(--accent) 30%, transparent); }
.fx .sp .sp-l { position:absolute; font-family:var(--f-display); font-weight:800; color:var(--fg); line-height:1.2; }
.fx .sp .sp-l .sl, .fx .sp .sp-s .sl { display:block; white-space:nowrap; }
.fx .sp .sp-s { font-family:var(--f-body); font-weight:500; color:var(--muted); line-height:1.3; margin-top:.6vmin; }
"""


def steps(X, cid, t, d, p):
    its = (S.items(p.get("items")) or [("第一步", ""), ("第二步", "")])[:12]
    n = len(its)
    x, y, w, h = S.box(X, p)
    title = fit.as_text(p.get("title"))
    kh = 0
    if title:
        kf = fit.fit_text(title, w * 0.9, S.vm(X, 12), S.vm(X, 6 if X.portrait else 5.2), S.vm(X, 3.2), max_lines=2)
        kh = kf.n * kf.px * 1.12 + S.vm(X, 4)
    y1, h1 = y + kh, h - kh
    has_sub = any(b for _, b in its)
    P = X.portrait
    lanes = 1 if n <= 6 else 2
    per = -(-n // lanes)
    pos, lab = [], []                           # node centres; label boxes (x, y, w, h)
    if not P:
        colw = w / per
        lane_room = (h1 - (S.vm(X, 5) if lanes > 1 else 0)) / lanes
        D = min(S.vm(X, 18 if n <= 4 else 14 if n <= 6 else 11), colw * 0.42, lane_room * 0.36)
        lw, lh_ = colw * 0.92, lane_room - D - S.vm(X, 4.5)
        tmax = S.vm(X, 7 if n <= 3 else 6.2 if n <= 4 else 5 if n <= 6 else 4.2)
        tpx, tfs = S.fitpx([a for a, _ in its], lw, lh_ * (0.6 if has_sub else 0.95), tmax, S.vm(X, 2.7), max_lines=3)
        spx, sfs = S.fitpx([b or " " for _, b in its], lw, lh_ * 0.36, max(S.vm(X, 2.6), tpx * 0.58), S.vm(X, 2.4), max_lines=2)
        content = max(f.n * tpx * 1.2 + ((g.n * spx * 1.3 + S.vm(X, 0.6)) if b else 0) for f, g, (_, b) in zip(tfs, sfs, its))
        lane_p = D + S.vm(X, 2.2) + content + S.vm(X, 5)
        top = y1 + max(0, (h1 - lanes * lane_p + S.vm(X, 5)) / 2) * 0.92       # the whole diagram sits optically centred
        for k in range(n):
            r, c = divmod(k, per)
            if r % 2: c = per - 1 - c
            cx, cy = x + (c + 0.5) * colw, top + r * lane_p + D / 2
            pos.append((cx, cy))
            lab.append((cx - colw * 0.46, cy + D / 2 + S.vm(X, 2.2), lw, content))
    else:
        lane_w = w / lanes
        D = min(S.vm(X, 13), (h1 / per) * 0.5, lane_w * 0.28)
        rowh = h1 / per
        for k in range(n):
            c, r = divmod(k, per)
            if c % 2: r = per - 1 - r
            cx, cy = x + c * lane_w + D / 2 + S.vm(X, 1), y1 + (r + 0.5) * rowh
            pos.append((cx, cy))
            lab.append((cx + D / 2 + S.vm(X, 3), cy - rowh * 0.46, lane_w - D - S.vm(X, 6), rowh * 0.92))
        lw, lh_ = lab[0][2], lab[0][3]
        tpx, tfs = S.fitpx([a for a, _ in its], lw, lh_ * (0.6 if has_sub else 0.95), S.vm(X, 5.8), S.vm(X, 2.7), max_lines=3)
        spx, sfs = S.fitpx([b or " " for _, b in its], lw, lh_ * 0.36, max(S.vm(X, 2.6), tpx * 0.58), S.vm(X, 2.4), max_lines=2)
    X.css("fx-sp", CSS)
    BG, FG, AC = S.col(X, p, "bg"), S.col(X, p, "fg"), S.col(X, p, "accent")
    # the connector: straight between neighbours; a lane change detours outside the label column
    pts, at = [pos[0]], [0]
    lane_of = lambda k: k // per
    for k in range(1, n):
        if lane_of(k) != lane_of(k - 1):
            (ax, ay), (bx, by) = pos[k - 1], pos[k]
            if not P:
                ex = ax + (w / per) * 0.5 * (1 if (lane_of(k - 1) % 2 == 0) else -1)
                pts += [(ex, ay), (ex, by)]
            else:
                ey = ay + (h1 / per) * 0.5 * (1 if (lane_of(k - 1) % 2 == 0) else -1)
                pts += [(ax, ey), (bx, ey)]
        pts.append(pos[k]); at.append(len(pts) - 1)
    lens = [0.0]
    for i in range(1, len(pts)): lens.append(lens[-1] + math.dist(pts[i - 1], pts[i]))
    cum = [lens[i] for i in at]
    total = max(lens[-1], 1)
    dpath = "M" + " L".join(f"{a:.1f} {b:.1f}" for a, b in pts)
    sw = max(3.0, S.vm(X, 0.55))
    svg = (f'<svg class="sp-path" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">'
           f'<path class="bgp" d="{dpath}" stroke="{FG}" stroke-opacity=".18" stroke-width="{sw:.1f}" stroke-dasharray="{sw * 0.2:.1f} {sw * 2.6:.1f}"/>'
           f'<path class="fgp" d="{dpath}" stroke="{FG}" stroke-width="{sw:.1f}" stroke-dasharray="{total:.1f}" stroke-dashoffset="{total:.1f}"/></svg>')
    nodes, labels = [], []
    for k, ((cx, cy), (a, b)) in enumerate(zip(pos, its)):
        nodes.append(f'<div class="sp-n" data-k="{k}" style="left:{cx - D / 2:.0f}px; top:{cy - D / 2:.0f}px; width:{D:.0f}px; height:{D:.0f}px; font-size:{D * 0.44:.0f}px">'
                     f'<i class="ring"></i><i class="done"></i><i class="fill"></i><b>{k + 1}</b></div>')
        lx, ly, lw_, lh2 = lab[k]
        align = "center" if not P else "left"
        sub = f'<div class="sp-s" style="font-size:{spx}px">{S.lines(X, sfs[k])}</div>' if b else ""
        top = ly if not P else cy - (tfs[k].n * tpx * 1.2 + (sfs[k].n * spx * 1.3 + S.vm(X, 0.6) if b else 0)) / 2
        labels.append(f'<div class="sp-l" data-k="{k}" style="left:{lx:.0f}px; top:{top:.0f}px; width:{lw_:.0f}px; text-align:{align}; font-size:{tpx}px">'
                      f'{S.lines(X, tfs[k])}{sub}</div>')
    tk_ = D * 0.26
    tok = f'<i class="sp-tok" style="width:{tk_:.0f}px; height:{tk_:.0f}px; margin:{-tk_ / 2:.0f}px 0 0 {-tk_ / 2:.0f}px"></i>'
    head = f'<div class="sp-k" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{kf.px}px">{S.lines(X, kf)}</div>' if title else ""
    _clip(X, cid, t, d, f'<div class="sp">{head}{svg}{tok}{"".join(nodes)}{"".join(labels)}</div>', p)
    s = f"#{cid} .sp"
    item_texts = [a for a, _ in its]
    T = S.beats(X, p, t, d, n, start=0.55 if title else 0.35, share=0.62, texts=item_texts)
    if title: X.tw(f'tl.from("{s} .sp-k .sl", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .bgp", {{opacity:0, duration:0.5}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .sp-n", {{scale:0.4, opacity:0, duration:0.45, ease:"back.out(2)", stagger:{min(0.05, 0.5 / n):.3f}}}, {t + 0.08:.3f});')
    X.tw(f'tl.set("{s} .sp-tok", {{x:{pos[0][0]:.0f}, y:{pos[0][1]:.0f}, opacity:0}}, {t:.3f});')
    X.tw(f'tl.set("{s} .sp-n .fill", {{scale:0}}, {t:.3f});')
    hl = int(p.get("hl", n - 1))
    for k, tk in enumerate(T):
        n_ = f"{s} .sp-n[data-k='{k}']"
        if k > 0:
            mv = min(0.5, max(0.2, tk - T[k - 1] - 0.1))
            X.tw(f'tl.to("{s} .fgp", {{strokeDashoffset:{total - cum[k]:.1f}, duration:{mv:.2f}, ease:"power2.inOut"}}, {tk - mv:.3f});')
            via = pts[at[k - 1] + 1:at[k] + 1]          # corner points then the node
            dd = [math.dist(a_, b_) for a_, b_ in zip([pts[at[k - 1]]] + via[:-1], via)]
            t0_ = tk - mv
            for (vx, vy), dl in zip(via, dd):
                part = mv * dl / max(sum(dd), 1)
                X.tw(f'tl.to("{s} .sp-tok", {{x:{vx:.0f}, y:{vy:.0f}, duration:{max(0.05, part):.2f}, ease:"none"}}, {t0_:.3f});')
                t0_ += part
            prev = f"{s} .sp-n[data-k='{k - 1}']"
            X.tw(f'tl.to("{prev} .fill", {{scale:0, duration:0.25}}, {tk - 0.05:.3f});')
            X.tw(f'tl.to("{prev} .done", {{opacity:1, duration:0.25}}, {tk - 0.05:.3f});')
            X.tw(f'tl.to("{prev} b", {{color:"{BG}", duration:0.2}}, {tk - 0.05:.3f});')
            X.tw(f'tl.to("{prev}", {{scale:1, duration:0.3}}, {tk - 0.05:.3f});')
            X.tw(f'tl.to("{s} .sp-l[data-k=\'{k - 1}\']", {{opacity:0.55, duration:0.3}}, {tk:.3f});')
        else:
            X.tw(f'tl.to("{s} .sp-tok", {{opacity:1, duration:0.2}}, {tk - 0.1:.3f});')
        X.tw(f'tl.to("{n_} .fill", {{scale:1, duration:0.4, ease:"back.out(2.2)"}}, {tk - 0.05:.3f});')
        X.tw(f'tl.to("{n_} b", {{color:"{BG}", duration:0.2}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{n_}", {{scale:1}}, {{keyframes:[{{scale:1.22, duration:0.16}}, {{scale:1.1, duration:0.3, ease:"power2.out"}}], immediateRender:false}}, {tk - 0.05:.3f});')
        X.tw(f'tl.from("{s} .sp-l[data-k=\'{k}\'] .sl", {{yPercent:80, opacity:0, duration:0.45, ease:"expo.out", stagger:0.04}}, {tk - 0.02:.3f});')
        X.sfx(tk - 0.05, "click")
    if hl != n - 1 and 0 <= hl < n:
        e = T[-1] + 0.55; n_ = f"{s} .sp-n[data-k='{hl}']"
        X.tw(f'tl.to("{s} .sp-n[data-k=\'{n - 1}\'] .fill", {{scale:0, duration:0.25}}, {e:.3f});')
        X.tw(f'tl.to("{s} .sp-n[data-k=\'{n - 1}\'] .done", {{opacity:1, duration:0.25}}, {e:.3f});')
        X.tw(f'tl.to("{n_} .fill", {{scale:1, duration:0.35, ease:"back.out(2)"}}, {e:.3f});')
        X.tw(f'tl.to("{s} .sp-l[data-k=\'{hl}\']", {{opacity:1, duration:0.3}}, {e:.3f});')
        X.tw(f'tl.to("{s} .sp-tok", {{x:{pos[hl][0]:.0f}, y:{pos[hl][1]:.0f}, duration:0.5, ease:"power2.inOut"}}, {e:.3f});')
    X.tw(f'tl.fromTo("{s}", {{scale:1}}, {{scale:1.02, duration:{d:.2f}, ease:"none", transformOrigin:"50% 50%"}}, {t:.3f});')


FX = {"steps": steps}
