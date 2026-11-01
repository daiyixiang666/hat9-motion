"""投票卡 Poll Card (结尾引导互动：「你选哪个？评论区打 A / B」；B 站投票卡、Envato「YouTube Subscribe」一类):
the question types on, the options slide in as lettered pills. Ask mode: a highlight walks across the options and
the 「评论区告诉我」 prompt bounces. Result mode (options carry percentages): the bars fill with rolling numbers,
the winner lights up with a check and the others dim. Results must be real and sourced, or tagged 「示意」.

Adapts: question 1 glyph to ~50 (≤ 3 lines), 2–6 options (row height and type follow the count), option text
1 glyph to a sentence, percentages optional (any mix that sums near 100), note / total optional.
p: question · options ["…", …] | [["…", 62], …] · mode (ask | result) · hl · letters (A–F; false → 1–6) · cta (评论区打 A / B) · total · kicker · note
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .pl { position:absolute; inset:0; }
.fx .pl .pl-c { position:absolute; background:var(--card); border-radius:1.6vmin; box-shadow:0 2.6vmin 7vmin rgba(0,0,0,.22); }
.fx .pl .pl-k { position:absolute; display:flex; align-items:center; gap:.5em; font-family:var(--f-mono, monospace); font-weight:700; letter-spacing:.18em; color:var(--accent); white-space:nowrap; }
.fx .pl .pl-q { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--card-fg); line-height:1.16; }
.fx .pl .pl-q .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .pl .gl > span { display:inline-block; }
.fx .pl .pl-o { position:absolute; display:flex; align-items:center; gap:.7em; border-radius:999px; overflow:hidden; border:.16em solid color-mix(in srgb, var(--card-fg) 18%, transparent); }
.fx .pl .pl-o .fill { position:absolute; left:0; top:0; bottom:0; background:color-mix(in srgb, var(--card-fg) 12%, transparent); transform-origin:0 50%; }
.fx .pl .pl-o.win .fill { background:color-mix(in srgb, var(--accent) 55%, transparent); }
.fx .pl .pl-o .lt { position:relative; flex:none; display:inline-grid; place-items:center; width:1.6em; height:1.6em; border-radius:50%; background:var(--card-fg); color:var(--card); font-family:var(--f-display); font-weight:900; font-size:.86em; }
.fx .pl .pl-o.win .lt { background:var(--accent); color:var(--bg); }
.fx .pl .pl-o .tx { position:relative; flex:1; font-family:var(--f-body); font-weight:700; color:var(--card-fg); white-space:nowrap; }
.fx .pl .pl-o .pc { position:relative; flex:none; font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--card-fg); font-variant-numeric:tabular-nums; }
.fx .pl .pl-o .ok { position:relative; flex:none; display:inline-grid; place-items:center; width:1.3em; height:1.3em; border-radius:50%; background:var(--accent); color:var(--bg); font-style:normal; font-size:.8em; }
.fx .pl .pl-o .hi { position:absolute; inset:0; border-radius:999px; box-shadow:inset 0 0 0 .22em var(--accent); opacity:0; }
.fx .pl .pl-cta { position:absolute; display:flex; align-items:center; gap:.55em; font-family:var(--f-display); font-weight:900; color:var(--bg); background:var(--fg); border-radius:999px; padding:.3em 1em; white-space:nowrap; }
.fx .pl .pl-cta svg { width:1.1em; height:1.1em; }
.fx .pl .pl-tot { position:absolute; font-family:var(--f-body); font-weight:500; color:color-mix(in srgb, var(--card-fg) 60%, transparent); white-space:nowrap; }
"""
BUBBLE = '<svg viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4z" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linejoin="round"/></svg>'


def _opts(v):
    out = []
    for it in fit.as_list(v):
        if isinstance(it, dict): out.append((str(it.get("text") or it.get("name") or ""), G.num(it.get("pct", it.get("value")))))
        elif isinstance(it, (list, tuple)): out.append((str(it[0]), G.num(it[1]) if len(it) > 1 else None))
        else: out.append((str(it), None))
    return out[:6]


def poll_card(X, cid, t, d, p):
    P = X.portrait
    q = fit.as_text(p.get("question") or p.get("text") or "你选哪个？")
    opts = _opts(p.get("options")) or [("A", None), ("B", None)]
    result = (p.get("mode") == "result") or (p.get("mode") != "ask" and all(v is not None for _, v in opts))
    hl = p.get("hl")
    if hl is None and result: hl = max(range(len(opts)), key=lambda k: opts[k][1] or 0)
    lv = p.get("letters")   # false → numbers; a list / "甲乙丙" → those; default A–F
    letters = [str(k + 1) for k in range(6)] if lv is False else ([str(c) for c in lv] if isinstance(lv, (list, tuple)) else list(str(lv)) if isinstance(lv, str) and lv else list("ABCDEF"))
    cta = fit.as_text(p.get("cta") or ("评论区打 " + " / ".join(letters[:len(opts)]) if not result else ""))
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-gn", G.CSS); X.css("fx-pl", CSS)
    cw = w if P else min(w * (0.6 if p.get("host") else 0.72), G.vm(X, 120))
    cx = x if P else x + (w - cw) / 2 - (w * 0.08 if p.get("host") else 0)
    pad = G.vm(X, 3.6)
    iw = cw - 2 * pad
    kpx = G.vm(X, 2.2)
    qf = fit.fit_text(q, iw, h * 0.26, G.vm(X, 6.4 if not P else 7), G.vm(X, 3.4), max_lines=3, lh=1.16)
    n = len(opts)
    rowh = min(G.vm(X, 9.5 if n <= 3 else 8), (h * 0.5) / n)
    oh = rowh * 0.82
    opx, ofits = S.fitpx([a for a, _ in opts], iw - oh * 3.4, oh * 0.5, G.vm(X, 3.8), G.vm(X, 2.2), max_lines=1)
    ctpx = G.vm(X, 3.4) if cta else 0
    tot = fit.as_text(p.get("total"))
    tpx = G.vm(X, 2.3) if tot else 0
    body = kpx * 2 + qf.n * qf.px * 1.16 + g + rowh * n + (ctpx * 1.9 + g if cta else 0) + (tpx * 1.6 if tot else 0)
    ch = min(h, body + 2 * pad)
    cy = y + (h - ch) / 2
    html = [f'<div class="pl-c" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px"></div>']
    yy = cy + pad
    html.append(f'<div class="pl-k" style="left:{cx + pad:.0f}px; top:{yy:.0f}px; font-size:{kpx:.0f}px">{X.rich(p.get("kicker", "投票 · POLL"))}</div>')
    note = fit.as_text(p.get("note"))
    if note:
        npx = G.vm(X, 1.8)
        html.append(G.note_tag(X, note, cx + cw - pad - (fit.width(note) + 1.2) * npx, yy - npx * 0.1, npx))
    yy += kpx * 2
    html.append(f'<div class="pl-q" style="left:{cx + pad:.0f}px; top:{yy:.0f}px; font-size:{qf.px}px">{G.line_html(X, qf)}</div>')
    yy += qf.n * qf.px * 1.16 + g
    for k, ((a, v), f) in enumerate(zip(opts, ofits)):
        win = result and k == hl
        right = (f'<span class="pc pl-pc{k}">0%</span>' if result and v is not None else "") + ('<i class="ok">✓</i>' if win else "")
        html.append(f'<div class="pl-o{" win" if win else ""}" data-k="{k}" style="left:{cx + pad:.0f}px; top:{yy + k * rowh:.0f}px; width:{iw:.0f}px; height:{oh:.0f}px; '
                    f'padding:0 {oh * 0.3:.0f}px; font-size:{opx}px">'
                    f'<i class="fill" style="width:{(v or 0) if result else 0:.1f}%"></i><span class="lt">{X.rich(letters[k] if k < len(letters) else str(k + 1))}</span>'
                    f'<span class="tx">{X.rich(f.lines[0])}</span>{right}<i class="hi"></i></div>')
    yy += rowh * n
    if cta:
        yy += g * 0.4
        cf = fit.fit_text(cta, iw - ctpx * 3, ctpx * 1.3, ctpx, G.vm(X, 2.3), max_lines=1)
        html.append(f'<div class="pl-cta" style="left:{cx + pad:.0f}px; top:{yy:.0f}px; font-size:{cf.px}px">{BUBBLE}{X.rich(cf.lines[0])}</div>')
        yy += ctpx * 1.9 + g
    if tot:
        html.append(f'<div class="pl-tot" style="left:{cx + pad:.0f}px; top:{yy:.0f}px; font-size:{tpx:.0f}px">{X.rich(tot)}</div>')
    _clip(X, cid, t, d, f'<div class="pl">{"".join(html)}</div>', p)
    s = f"#{cid} .pl"
    X.tw(f'tl.from("{s} .pl-c", {{y:50, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .pl-k", {{opacity:0, duration:0.35}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .pl-q .gl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {t + 0.2:.3f});')
    X.sfx(t + 0.1, "enter")
    to = t + 0.5 + qf.n * 0.08
    X.tw(f'tl.from("{s} .pl-o", {{x:-40, opacity:0, duration:0.45, ease:"expo.out", stagger:0.1}}, {to:.3f});')
    X.tw(f'tl.from("{s} .pl-o .lt", {{scale:0, duration:0.35, ease:"back.out(2.6)", stagger:0.1}}, {to + 0.1:.3f});')
    for k in range(n): X.sfx(to + k * 0.1, "click")
    tf = to + 0.3 + n * 0.1
    if result:
        X.tw(f'tl.from("{s} .pl-o .fill", {{scaleX:0, duration:0.9, ease:"power3.out", stagger:0.08}}, {tf:.3f});')
        for k, (a, v) in enumerate(opts):
            if v is None: continue
            dec = 0 if float(v).is_integer() else min(2, G.dec_of(round(float(v), 2)))
            X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .pl-pc{k}"); if(!el) return; tl.to(o, {{v:{v}, duration:0.9, ease:"power3.out", onUpdate:()=>{{el.textContent=o.v.toFixed({dec})+"%";}}}}, {tf + k * 0.08:.3f});}})();')
        tw_ = tf + 1.1
        if hl is not None:
            X.tw(f'tl.to("{s} .pl-o:not(.win)", {{opacity:0.45, duration:0.35}}, {tw_:.3f});')
            X.tw(f'tl.fromTo("{s} .pl-o.win", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.18}}, {{scale:1, duration:0.4, ease:"back.out(2.4)"}}], immediateRender:false}}, {tw_:.3f});')
            X.tw(f'tl.from("{s} .pl-o.win .ok", {{scale:0, rotation:-45, duration:0.4, ease:"back.out(2.6)"}}, {tw_ + 0.05:.3f});')
            X.sfx(tw_, "hit")
    else:     # the highlight walks across the options, round after round, until the beat ends
        step = 0.42
        k, tt = 0, tf
        while tt < t + d - 0.5:
            X.tw(f'tl.fromTo("{s} .pl-o[data-k=\'{k % n}\'] .hi", {{opacity:0}}, {{keyframes:[{{opacity:1, duration:0.12}}, {{opacity:0, duration:0.3}}], immediateRender:false}}, {tt:.3f});')
            k += 1; tt += step
    if cta:
        tc = tf + (1.4 if result else 0.3)
        X.tw(f'tl.from("{s} .pl-cta", {{scale:0.4, opacity:0, duration:0.4, ease:"back.out(2.2)"}}, {tc:.3f});')
        rp = max(1, int((d - (tc - t) - 0.6) / 0.5)); rp -= (rp % 2 == 0)
        X.tw(f'tl.to("{s} .pl-cta svg", {{y:-5, duration:0.25, ease:"sine.inOut", yoyo:true, repeat:{max(1, rp * 2 - 1)}}}, {tc + 0.5:.3f});')
    if tot: X.tw(f'tl.from("{s} .pl-tot", {{opacity:0, duration:0.4}}, {tf + 0.4:.3f});')


FX = {"poll_card": poll_card}
