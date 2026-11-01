"""测评卡 Review Card (测评类口播的结论页：数码 / 工具 / 课程测评里的「评分条 + 优缺点 + 结论章」):
the product name lifts, the overall score rolls up while the stars fill, every dimension's bar grows with its value
counting, pros and cons tick in, then the verdict stamp slams onto the card with a two-frame jolt.

Adapts: 1–8 scored dimensions (row height and type follow the count), scores on any scale (`max`, default 10),
0–6 pros and 0–6 cons each (more fold into 「+N」), optional product image, names 1 glyph to a long line.
p: product · sub · image · scores [[维度, 分], …] or {维度: 分} · max · overall · stars (0–5) · pros · cons ·
   verdict · verdict_kind (good | bad | mixed) · note (e.g. 「示意数据」) · at (cue for the stamp)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .rv { position:absolute; inset:0; }
.fx .rv .rv-l { position:absolute; background:var(--card); color:var(--card-fg); border-radius:1.4vmin; box-shadow:0 2.4vmin 6vmin rgba(0,0,0,.22); overflow:hidden; }
.fx .rv .rv-img { position:absolute; object-fit:cover; border-radius:1vmin; }
.fx .rv .rv-n { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.1; color:var(--card-fg); }
.fx .rv .rv-n .gl, .fx .rv .rv-s .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .rv .gl > span { display:inline-block; }
.fx .rv .rv-s { position:absolute; font-family:var(--f-body); font-weight:500; line-height:1.3; color:color-mix(in srgb, var(--card-fg) 62%, transparent); }
.fx .rv .rv-o { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.9; color:var(--card-fg); white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .rv .rv-o small { font-size:.34em; font-weight:700; color:color-mix(in srgb, var(--card-fg) 55%, transparent); margin-left:.12em; }
.fx .rv .rv-row { position:absolute; display:flex; align-items:center; }
.fx .rv .rv-lab { flex:none; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.fx .rv .rv-tr { position:relative; flex:none; background:color-mix(in srgb, var(--fg) 12%, transparent); border-radius:999px; overflow:hidden; }
.fx .rv .rv-bar { position:absolute; left:0; top:0; bottom:0; background:var(--fg); border-radius:999px; transform-origin:0 50%; }
.fx .rv .rv-bar.top { background:var(--accent); }
.fx .rv .rv-v { flex:none; text-align:right; font-family:var(--f-num, var(--f-display)); font-weight:800; color:var(--fg); font-variant-numeric:tabular-nums; white-space:nowrap; }
.fx .rv .rv-pc { position:absolute; }
.fx .rv .rv-pc h4 { margin:0; font-family:var(--f-display); font-weight:900; color:var(--fg); display:flex; align-items:center; gap:.4em; white-space:nowrap; }
.fx .rv .rv-pc h4 i { display:inline-grid; place-items:center; width:1.25em; height:1.25em; border-radius:50%; font-style:normal; font-size:.8em; color:var(--bg); }
.fx .rv .rv-pc.pro h4 i { background:#1e7a44; } .fx .rv .rv-pc.con h4 i { background:#c0362c; }
.fx .rv .rv-pc .it { display:block; font-family:var(--f-body); font-weight:500; color:var(--fg); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.fx .rv .rv-pc .it b { font-weight:900; margin-right:.35em; }
.fx .rv .rv-pc.pro .it b { color:#1e7a44; } .fx .rv .rv-pc.con .it b { color:#c0362c; }
.fx .rv .rv-stamp { position:absolute; font-family:var(--f-display); font-weight:900; letter-spacing:.08em; white-space:nowrap; border:.55vmin solid currentColor;
  border-radius:1vmin; text-align:center; line-height:1; background:color-mix(in srgb, var(--card) 70%, transparent); }
.fx .rv .rv-stamp small { display:block; font-family:var(--f-mono, monospace); font-weight:600; letter-spacing:.2em; font-size:.32em; margin-top:.35em; opacity:.8; }
.fx .rv .rv-stamp.good { color:#1e7a44; } .fx .rv .rv-stamp.bad { color:#c0362c; } .fx .rv .rv-stamp.mixed { color:#a35f00; }
"""


def _scores(v):
    out = []
    if isinstance(v, dict): v = list(v.items())
    for it in fit.as_list(v):
        if isinstance(it, dict): it = (it.get("name") or it.get("text") or "", it.get("score", it.get("value")))
        if isinstance(it, (list, tuple)) and len(it) >= 2 and G.num(it[1]) is not None: out.append((str(it[0]), it[1]))
        elif isinstance(it, str) and ("：" in it or ":" in it):
            a, b = it.replace(":", "：").split("：", 1)
            if G.num(b) is not None: out.append((a, b))
    return out[:8]


def review_card(X, cid, t, d, p):
    P = X.portrait
    name = fit.as_text(p.get("product") or p.get("title") or p.get("text") or "测评对象")
    sub = fit.as_text(p.get("sub"))
    sc = _scores(p.get("scores"))
    mx = G.num(p.get("max")) or 10.0
    vals = [G.num(v) for _, v in sc]
    ov = G.num(p.get("overall"))
    if ov is None: ov = round(sum(vals) / len(vals), 1) if vals else None
    st = None if p.get("stars") is False else G.num(p.get("stars"))   # stars: false hides the row
    if st is None and ov is not None and p.get("stars") is not False: st = round(ov / mx * 5 * 2) / 2
    pros, cons = [S.flat(p.get("pros")), S.flat(p.get("cons"))]
    verdict = fit.as_text(p.get("verdict"))
    kind = p.get("verdict_kind") or ("good" if (ov or 0) / mx >= 0.8 else "bad" if (ov or 0) / mx < 0.55 else "mixed")
    img = p.get("image")
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.6)
    X.css("fx-gn", G.CSS); X.css("fx-rv", CSS)
    html = []
    # ---- the product panel (left in 16:9, top band in 9:16)
    verdict_px = G.vm(X, 4.6 if not P else 5.0) if verdict else 0
    if P:
        L = (x, y, w, h * (0.3 if img else 0.24) + (verdict_px * 1.7 if verdict else 0))
    else:
        L = (x, y, w * 0.36, h)
    lx, ly, lw, lh = L
    pad = G.vm(X, 3)
    html.append(f'<div class="rv-l" style="left:{lx:.0f}px; top:{ly:.0f}px; width:{lw:.0f}px; height:{lh:.0f}px"></div>')
    ix = lx + pad; iy = ly + pad; iw = lw - 2 * pad
    if img:
        if P:
            isz = lh - 2 * pad
            html.append(f'<img class="rv-img" src="{X.asset(img)}" alt="" style="left:{ix:.0f}px; top:{iy:.0f}px; width:{isz:.0f}px; height:{isz:.0f}px">')
            ix += isz + pad; iw -= isz + pad
        else:
            ih = lh * 0.4
            html.append(f'<img class="rv-img" src="{X.asset(img)}" alt="" style="left:{ix:.0f}px; top:{iy:.0f}px; width:{iw:.0f}px; height:{ih:.0f}px">')
            iy += ih + pad
    if P:   # name + sub on the left of the band, the score on its right
        ow = min(iw * 0.42, G.vm(X, 26))
        nw = iw - ow - pad
        nf = fit.fit_text(name, nw, lh * 0.5, G.vm(X, 7), G.vm(X, 2.8), max_lines=3, lh=1.1)
        sf = fit.fit_text(sub, nw, lh * 0.26, G.vm(X, 3), G.vm(X, 2.2), max_lines=2, lh=1.3) if sub else None
        blockh = nf.n * nf.px * 1.1 + (sf.n * sf.px * 1.3 + g * 0.4 if sf else 0)
        ny = ly + (lh - verdict_px * 1.7 - blockh) / 2 + (G.vm(X, 1.6) if p.get("note") else 0)
        html.append(f'<div class="rv-n" style="left:{ix:.0f}px; top:{ny:.0f}px; font-size:{nf.px}px">{G.line_html(X, nf)}</div>')
        if sf: html.append(f'<div class="rv-s" style="left:{ix:.0f}px; top:{ny + nf.n * nf.px * 1.1 + g * 0.4:.0f}px; font-size:{sf.px}px">{G.line_html(X, sf)}</div>')
        opx = min(G.vm(X, 14), lh * 0.42)
        spx = min(G.vm(X, 4.6), (ow - G.vm(X, 1)) / 5.6)
        ox = lx + lw - pad - ow
        oy = ly + (lh - verdict_px * 1.7 - opx * 0.9 - spx - g * 0.5) / 2 + (G.vm(X, 1.6) if p.get("note") else 0)
    else:
        nf = fit.fit_text(name, iw, lh * 0.2, G.vm(X, 7), G.vm(X, 3.4), max_lines=2, lh=1.1)
        sf = fit.fit_text(sub, iw, lh * 0.12, G.vm(X, 2.8), G.vm(X, 2.1), max_lines=2, lh=1.3) if sub else None
        html.append(f'<div class="rv-n" style="left:{ix:.0f}px; top:{iy:.0f}px; font-size:{nf.px}px">{G.line_html(X, nf)}</div>')
        iy += nf.n * nf.px * 1.1 + g * 0.3
        if sf:
            html.append(f'<div class="rv-s" style="left:{ix:.0f}px; top:{iy:.0f}px; font-size:{sf.px}px">{G.line_html(X, sf)}</div>')
            iy += sf.n * sf.px * 1.3
        nh = G.vm(X, 1.9) * 2.2 if p.get("note") else 0
        room = ly + lh - pad - nh - (iy + g)          # score + stars must fit between the sub and the note
        spx = min(G.vm(X, 4.4), iw / 6, room * 0.22)
        opx = max(G.vm(X, 4), min(G.vm(X, 16 if not img else 11), (room - g * 0.8 - spx) / 0.95))
        ox = ix
        oy = max(iy + g, ly + lh - pad - nh - g * 0.8 - spx - opx * 0.95)
    if ov is not None:
        dec = 1 if (ov != int(ov) or any(v != int(v) for v in vals if v is not None)) else 0
        html.append(f'<div class="rv-o" style="left:{ox:.0f}px; top:{oy:.0f}px; font-size:{opx:.0f}px"><span class="rv-ov">{0:.{dec}f}</span><small>/{mx:g}</small></div>')
        if st is not None: html.append(G.stars(X, spx, "gn-stars rv-st", f"left:{ox:.0f}px; top:{oy + opx * 0.95 + g * 0.4:.0f}px"))
    note = fit.as_text(p.get("note"))
    if note:
        npx = G.vm(X, 1.9)
        html.append(G.note_tag(X, note, lx + pad, ly + lh - pad - npx * 1.6 if not P else ly + pad * 0.5, npx))
    # ---- the verdict stamp
    if verdict:
        vf = fit.fit_text(verdict, (lw if not P else w) * 0.5, verdict_px * 1.3, verdict_px, G.vm(X, 3), max_lines=1)
        vw = fit.width(vf.lines[0]) * vf.px * 1.08 + vf.px * 1.6
        if P:   # under the name, inside the band
            vx, vy = lx + pad, ly + lh - pad * 0.5 - vf.px * 1.75
        else:   # beside the big score, straddling the panel's right edge
            vx = lx + lw - vw * 0.9
            vy = oy + opx * 0.05
        html.append(f'<div class="rv-stamp {kind}" style="left:{vx:.0f}px; top:{vy:.0f}px; font-size:{vf.px}px; padding:{vf.px * 0.35:.0f}px {vf.px * 0.6:.0f}px; transform:rotate(-8deg)">'
                    f'{X.rich(vf.lines[0])}<small>VERDICT</small></div>')
    # ---- score bars + pros / cons (right in 16:9, below in 9:16)
    if P:
        rx, ry, rw = x, ly + lh + g * 1.6, w
        rh = y + h - ry
    else:
        rx, ry, rw = lx + lw + g * 1.8, y, w - lw - g * 1.8
        rh = h
    has_pc = bool(pros or cons)
    bh = rh * (0.56 if has_pc else 1.0) if sc else 0
    n = len(sc)
    if n:
        rowh = min(G.vm(X, 9 if not P else 10), bh / n)
        labw = rw * (0.3 if not P else 0.32)
        valw = rw * 0.14
        trw = rw - labw - valw - g
        lpx, _ = S.fitpx([a for a, _ in sc], labw - g * 0.5, rowh * 0.6, G.vm(X, 3.6), G.vm(X, 2.2), max_lines=1)
        vpx2 = min(lpx * 1.25, rowh * 0.62)
        trh = max(G.vm(X, 1.2), min(rowh * 0.32, G.vm(X, 2.6)))
        y0 = ry + (bh - rowh * n) / 2 if not P else ry + (0 if has_pc else (bh - rowh * n) * 0.3)
        best = max(vals) if vals else 0
        for k, (a, v) in enumerate(sc):
            yy = y0 + k * rowh
            frac = max(0.0, min(1.0, G.num(v) / mx))
            html.append(f'<div class="rv-row" data-k="{k}" style="left:{rx:.0f}px; top:{yy:.0f}px; height:{rowh:.0f}px">'
                        f'<span class="rv-lab" style="width:{labw:.0f}px; font-size:{lpx}px">{X.rich(a)}</span>'
                        f'<span class="rv-tr" style="width:{trw:.0f}px; height:{trh:.0f}px"><i class="rv-bar{" top" if G.num(v) == best else ""}" style="width:{frac * 100:.1f}%"></i></span>'
                        f'<span class="rv-v" style="width:{valw:.0f}px; font-size:{vpx2:.0f}px">{0:.{min(2, G.dec_of(v))}f}</span></div>')
    if has_pc:
        py = ry + bh + (g if n else 0)
        ph = ry + rh - py
        cw = (rw - g * 1.5) / 2
        def col(items, cls, head, mark, cx):
            shown = items[:4] + ([f"+{len(items) - 4}"] if len(items) > 4 else [])
            if not shown: return ""
            hpx = min(G.vm(X, 3.6), ph * 0.2)
            rowh2 = min(G.vm(X, 6.2), (ph - hpx * 1.6) / max(len(shown), 1))
            ipx, _ = S.fitpx(shown, cw - G.vm(X, 3), rowh2 * 0.7, G.vm(X, 3.2), G.vm(X, 2.1), max_lines=1)
            its = "".join(f'<span class="it" style="font-size:{ipx}px; line-height:{rowh2:.0f}px"><b>{mark}</b>{X.rich(s_)}</span>' for s_ in shown)
            return (f'<div class="rv-pc {cls}" style="left:{cx:.0f}px; top:{py:.0f}px; width:{cw:.0f}px">'
                    f'<h4 style="font-size:{hpx:.0f}px; margin-bottom:{hpx * 0.4:.0f}px"><i>{"✓" if cls == "pro" else "✕"}</i>{X.rich(head)}</h4>{its}</div>')
        labs = fit.as_list(p.get("labels")) or ["优点", "缺点"]
        html.append(col(pros, "pro", labs[0], "+", rx))
        html.append(col(cons, "con", labs[1] if len(labs) > 1 else "缺点", "−", rx + cw + g * 1.5))
    _clip(X, cid, t, d, f'<div class="rv">{"".join(html)}</div>', p)
    s = f"#{cid} .rv"
    X.tw(f'tl.from("{s} .rv-l", {{x:{-60 if not P else 0}, y:{0 if not P else -40}, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    if img: X.tw(f'tl.from("{s} .rv-img", {{scale:1.15, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .rv-n .gl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {t + 0.15:.3f});')
    if sub: X.tw(f'tl.from("{s} .rv-s", {{opacity:0, y:12, duration:0.5}}, {t + 0.35:.3f});')
    X.sfx(t + 0.1, "enter")
    if ov is not None:
        dec = 1 if (ov != int(ov) or any(v != int(v) for v in vals if v is not None)) else 0
        G.counter(X, f"{s} .rv-ov", t + 0.35, 0, ov, dur=1.0, dec=dec, sep=False)
        if st is not None: X.tw(f'tl.to("{s} .rv-st .on", {{width:"{(st or 0) / 5 * 100:.1f}%", duration:0.9, ease:"steps({max(2, int((st or 0) * 2))})"}}, {t + 0.45:.3f});')
        X.sfx(t + 0.35, "count")
    for k, (a, v) in enumerate(sc):
        tk = t + 0.45 + k * min(0.14, 1.0 / max(n, 1))
        X.tw(f'tl.from("{s} .rv-row[data-k=\'{k}\'] .rv-lab", {{opacity:0, x:-16, duration:0.4, ease:"expo.out"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .rv-row[data-k=\'{k}\'] .rv-bar", {{scaleX:0, duration:0.8, ease:"power3.out"}}, {tk + 0.05:.3f});')
        G.counter(X, f"{s} .rv-row[data-k=\'{k}\'] .rv-v", tk + 0.05, 0, G.num(v), dur=0.8, dec=min(2, G.dec_of(v)), sep=False)
    tpc = t + 0.6 + n * min(0.14, 1.0 / max(n, 1)) + 0.2
    if has_pc:
        X.tw(f'tl.from("{s} .rv-pc h4", {{opacity:0, y:14, duration:0.4, ease:"expo.out", stagger:0.1}}, {tpc:.3f});')
        X.tw(f'tl.from("{s} .rv-pc .it", {{opacity:0, x:-14, duration:0.35, ease:"expo.out", stagger:0.07}}, {tpc + 0.15:.3f});')
    if verdict:
        tv = S.beats(X, {"at": p.get("at")}, t, d, 1)[0] if p.get("at") else min(t + d - 0.9, tpc + 0.6 + (len(pros) + len(cons)) * 0.07)
        tv = max(tv, t + 0.8)
        X.tw(f'tl.fromTo("{s} .rv-stamp", {{scale:2.4, opacity:0, rotation:-22}}, {{scale:1, opacity:1, rotation:-8, duration:0.32, ease:"power4.in", immediateRender:true}}, {tv:.3f});')
        X.tw(f'tl.fromTo("{s}", {{x:0, y:0}}, {{keyframes:[{{x:-10, y:6, duration:0.04}}, {{x:7, y:-4, duration:0.04}}, {{x:0, y:0, duration:0.06}}], immediateRender:false}}, {tv + 0.32:.3f});')
        X.sfx(tv + 0.3, "slam")


FX = {"review_card": review_card}
