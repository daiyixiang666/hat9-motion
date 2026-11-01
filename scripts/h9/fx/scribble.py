"""潦草涂鸦标注 Scribble (Johnny Harris / 回形针 / 小Lin说 的手绘红笔标注；AE 的 Trim Paths 手绘圈注；Hand-drawn Annotation Pack):
a fast red marker scribbles over a statement or a picture: words get circled, struck through twice, crossed out,
scrawled over or underlined with a wavy line, an arrow swings in from a handwritten note. Every stroke is seeded
and slightly uneven — drawn on with a hand's speed, never a clean vector.

Adapts: a statement (1–3 lines, fitted; marks aim at words of it) or an image (any aspect; marks aim at boxes in %);
1–8 marks of 8 kinds; notes a word to a short sentence in a hand font; colour from the accent or `ink`.
p: text | image · scribbles: [{type: circle|box|strike|underline|cross|scrawl|check|arrow, target (word) | box [x,y,w,h] %, note}] · ink
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit

CSS = """
.fx .sc { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .sc .sc-t { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.3; }
.fx .sc .sc-t .sl { display:block; white-space:nowrap; }
.fx .sc .sc-img { position:absolute; border-radius:1vmin; box-shadow:0 2vmin 5vmin rgba(0,0,0,.25); object-fit:cover; }
.fx .sc svg.sc-ink { position:absolute; left:0; top:0; overflow:visible; }
.fx .sc svg.sc-ink path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
.fx .sc .sc-note { position:absolute; font-family:var(--f-hand, var(--f-display)); white-space:nowrap; line-height:1.1; }
"""


def scribble(X, cid, t, d, p):
    P = X.portrait
    text = fit.as_text(p.get("text") or "")
    img = p.get("image")
    marks = [m for m in fit.as_list(p.get("scribbles")) if isinstance(m, dict)][:8]   # "marks" is a reserved beat key (scripts/h9/marks.py)
    x, y, w, h = S.box(X, p)
    ink = p.get("ink") or {"paper": "#e2321f", "lemon": "#c8102e", "red": "#111111", "ink": "#ff5a3c"}.get(p.get("theme"), "#e2321f")
    X.css("fx-sc", CSS)
    html = []
    boxes = []                        # px boxes for marks
    if img:
        ar = fit.aspect(X, img, 1.5)
        bw = min(w * (0.92 if P else 0.6), h * (0.66 if P else 0.88) * ar); bh = bw / ar
        ix = x + (w - bw) / 2 if P else x + w * 0.04
        iy = y + (h - bh) / 2 - (S.vm(X, 5) if P else 0)
        html.append(f'<img class="sc-img" src="{X.asset(img)}" alt="" style="left:{ix:.0f}px; top:{iy:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">')
        for m in marks:
            b = m.get("box") or [40, 40, 20, 20]
            boxes.append((ix + bw * b[0] / 100, iy + bh * b[1] / 100, bw * b[2] / 100, bh * b[3] / 100))
        lh = 1.3; tf = None
        block = (iy, iy + bh)
    else:
        lh = 1.3
        tf = fit.fit_text(text or "标注", w * (0.84 if P else 0.8), h * 0.5, S.vm(X, 11 if P else 9.6), S.vm(X, 4), max_lines=3, lh=lh)
        th = tf.n * tf.px * lh
        ty = y + (h - th) / 2 - S.vm(X, 2)
        block = (ty, ty + th)
        html.append(f'<div class="sc-t" style="top:{ty:.0f}px; font-size:{tf.px}px">' + "".join(f'<span class="sl">{X.rich(l)}</span>' for l in tf.lines) + "</div>")
        for m in marks:
            bx = T2.text_box(X, tf, X.W / 2, ty, fit.plain(fit.as_text(m.get("target") or "")), lh) if m.get("target") else None
            if bx is None:
                b = m.get("box") or [40, 40, 20, 20]
                bx = (x + w * b[0] / 100, y + h * b[1] / 100, w * b[2] / 100, h * b[3] / 100)
            boxes.append(bx)
    r = X.rand
    sw = max(4.0, S.vm(X, 0.75))
    paths, notes = [], []
    npx = S.vm(X, 5.4 if P else 4.6)
    for i, (m, (bx, by, bw_, bh_)) in enumerate(zip(marks, boxes)):
        kind = m.get("type") or "circle"
        strokes = T2.rough(kind, bx, by, bw_, bh_, r)
        note = fit.as_text(m.get("note"))
        nx = ny = None
        if note:
            nf = fit.fit_text(note, w * 0.42, npx * 2.4, npx, S.vm(X, 2.6), max_lines=1)
            nw = fit.width(nf.lines[0]) * nf.px
            # notes sit outside the text / picture block, never on top of it:
            # a picture in 16:9 gets a notes column on its right; otherwise below first, then above
            if img and not P:
                nx = ix + bw + S.vm(X, 5)
                ny = min(max(y, by + bh_ / 2 - nf.px / 2 + sum(1 for q in notes if abs(q[2] - (by + bh_ / 2)) < nf.px * 1.2) * nf.px * 1.3), y + h - nf.px)
                below = True
            else:
                kb = sum(1 for q in notes if q[2] > block[1])
                fit_b = block[1] + S.vm(X, 4) + (kb + 1) * nf.px * 1.3 <= y + h
                fit_a = block[0] - S.vm(X, 4) - nf.px - (len(notes) - kb) * nf.px * 1.3 >= y
                # on a picture the side nearer the mark (short arrows); on text alternate; never past the free area
                want = (by + bh_ / 2 > (block[0] + block[1]) / 2) if img else i % 2 == 0
                below = (want and fit_b) or (not fit_a and fit_b) or (not fit_a and not fit_b and want)
                k_row = kb if below else len(notes) - kb
                nx = min(max(x, bx + bw_ * 0.5 - nw * 0.3), x + w - nw)
                ny = block[1] + S.vm(X, 4) + k_row * nf.px * 1.3 if below else block[0] - S.vm(X, 4) - nf.px - k_row * nf.px * 1.3
            notes.append((i, nx, ny, nf.px, nf.lines[0], r.uniform(-6, 4)))
            if kind != "arrow":     # a small arrow from the note to the mark
                if img and not P:
                    ax, ay = nx - S.vm(X, 1), ny + nf.px * 0.5
                    tx, ty_ = bx + bw_ + S.vm(X, 1.2), by + bh_ / 2
                else:
                    ax, ay = nx + nw * 0.15, (ny if below else ny + nf.px)
                    tx, ty_ = bx + bw_ * 0.5, (by + bh_ + S.vm(X, 1.2) if below else by - S.vm(X, 1.2))
                strokes += T2.rough("arrow", ax, ay, tx - ax, ty_ - ay, r, wob=2.5)
        if kind == "arrow" and not note:
            pass
        paths.append((i, strokes))
    svg = [f'<svg class="sc-ink" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">']
    for i, strokes in paths:
        for j, (dd, L) in enumerate(strokes):
            svg.append(f'<path data-m="{i}" data-s="{j}" d="{dd}" stroke="{ink}" stroke-width="{sw * (0.8 if j else 1):.1f}" stroke-dasharray="{L:.0f}" stroke-dashoffset="{L:.0f}"/>')
    svg.append("</svg>")
    html.append("".join(svg))
    for i, nx, ny, px, line, rot in notes:
        html.append(f'<div class="sc-note" data-m="{i}" style="left:{nx:.0f}px; top:{ny:.0f}px; font-size:{px:.0f}px; color:{ink}; transform:rotate({rot:.1f}deg)">{X.rich(line)}</div>')
    _clip(X, cid, t, d, f'<div class="sc">{"".join(html)}</div>', p)
    s = f"#{cid} .sc"
    if img: X.tw(f'tl.from("{s} .sc-img", {{opacity:0, scale:0.94, y:30, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    else: X.tw(f'tl.from("{s} .sc-t .sl", {{opacity:0, y:24, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "enter")
    at = fit.as_list(p.get("at"))
    n = max(1, len(paths))
    for k, (i, strokes) in enumerate(paths):
        tk = None
        if k < len(at) and X.chars:
            try: tk = float(X.T(at[k], t))
            except SystemExit: tk = None
        tk = tk or t + 0.6 + k * min(0.75, (d - 1.0) / n)
        tt = tk
        for j, (dd, L) in enumerate(strokes):
            dur = max(0.12, min(0.5, L / 2600))
            X.tw(f'tl.to("{s} path[data-m=\'{i}\'][data-s=\'{j}\']", {{strokeDashoffset:0, duration:{dur:.2f}, ease:"power1.inOut"}}, {tt:.3f});')
            tt += dur * 0.85
        X.sfx(tk, "brush")
        X.tw(f'tl.from("{s} .sc-note[data-m=\'{i}\']", {{opacity:0, y:12, scale:0.9, duration:0.35, ease:"back.out(2)"}}, {tt - 0.1:.3f});')


FX = {"scribble": scribble}
