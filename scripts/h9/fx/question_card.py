"""设问卡 Question Card (小Lin说 的问号卡；回形针「问题来了」；quiz show reveal):
a card drops onto the page with a giant question mark that keeps wobbling, the question lifts in line by line;
with options, the choices deal in as lettered chips, a beat of suspense, then the wrong ones grey out and the
right one fills with the accent and a tick; without options the card flips over to show the answer on its back.

Adapts: question a word to ~60 glyphs (≤ 4 lines, fitted; options shrink first so it is never cut), 0–5 options
(16:9: a row for up to 3 short ones, two columns for 4–5, else a column; 9:16: a column), answer by index or text,
emoji and right-to-left text measured like any text.
p: q · options · answer (index or text) · reveal (line shown after the answer) · kicker · at_reveal
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
.fx .qc { position:absolute; left:0; top:0; width:100%; height:100%; perspective:1600px; }
.fx .qc .qc-card { position:absolute; transform-style:preserve-3d; }
.fx .qc .qc-face { position:absolute; inset:0; border-radius:2.2vmin; background:var(--card); box-shadow:0 2.6vmin 6vmin rgba(0,0,0,.28), inset 0 0 0 .35vmin color-mix(in srgb, var(--fg) 12%, transparent);
  backface-visibility:hidden; overflow:hidden; }
.fx .qc .qc-back { transform:rotateY(180deg); background:var(--accent); }
.fx .qc .qc-qm { position:absolute; font-family:var(--f-display); font-weight:900; line-height:.8; color:var(--accent); transform-origin:50% 80%; }
.fx .qc .qc-k { position:absolute; font-family:var(--f-mono, monospace); font-weight:600; letter-spacing:.14em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.fx .qc .qc-q { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--card-fg, var(--fg)); line-height:1.16; }
.fx .qc .qc-q .sl, .fx .qc .qc-a .sl, .fx .qc .qc-rv .sl { display:block; white-space:nowrap; overflow:hidden; padding-bottom:.06em; }
.fx .qc .qc-q .sl > span, .fx .qc .qc-rv .sl > span { display:inline-block; }
.fx .qc .qc-o { position:absolute; display:flex; align-items:center; gap:.7em; border-radius:1.2vmin; background:var(--bg); color:var(--fg);
  box-shadow:inset 0 0 0 .3vmin color-mix(in srgb, var(--fg) 18%, transparent); font-family:var(--f-body); font-weight:800; white-space:nowrap; overflow:hidden; }
.fx .qc .qc-o b { position:relative; display:grid; place-items:center; flex:none; border-radius:50%; background:var(--fg); color:var(--bg); font-family:var(--f-mono, monospace); font-weight:700; }
.fx .qc .qc-o .ok { position:absolute; inset:0; background:var(--accent); opacity:0; }
.fx .qc .qc-o span { position:relative; }
.fx .qc .qc-o .tick { position:relative; margin-left:auto; font-weight:900; opacity:0; }
.fx .qc .qc-a { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--bg); line-height:1.16; text-align:center; }
.fx .qc .qc-rv { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--fg); line-height:1.3; }
"""


def question_card(X, cid, t, d, p):
    P = X.portrait
    q = fit.as_text(p.get("q") or p.get("question") or p.get("text") or "为什么？")
    opts = [fit.as_text(o) for o in fit.as_list(p.get("options"))][:5]
    ans = p.get("answer")
    if isinstance(ans, str) and ans in opts: ans = opts.index(ans)
    ans_i = ans if isinstance(ans, int) and 0 <= ans < len(opts) else (None if not opts else len(opts) - 1)
    ans_text = fit.as_text(ans) if isinstance(ans, str) and ans not in opts else ""
    reveal = fit.as_text(p.get("reveal"))
    kicker = fit.as_text(p.get("kicker") or "问题来了")
    x, y, w, h = S.box(X, p)
    # card geometry
    cw = w * (0.94 if P else (0.66 if p.get("host") else 0.74))
    no = len(opts)
    longest = max((len(fit.plain(o)) for o in opts), default=0)
    # one row (16:9, ≤ 3 short options) · two columns (16:9, 4–5 options) · one column (9:16 or long options)
    cols = 0 if not no else (1 if P else (no if (no <= 3 and longest <= 5) else (2 if (no > 3 and longest <= 14) else 1)))
    rows_opt = 0 if not no else -(-no // cols)
    opx = S.vm(X, 4.6 if P else 3.4)
    oh = opx * 2.3
    opt_h = 0 if not no else (rows_opt * oh + (rows_opt - 1) * S.vm(X, 1.4))
    rvpx = S.vm(X, 3.6 if P else 3.0)
    rv_h = rvpx * 1.3 * 2 + S.vm(X, 3) if reveal else 0
    pad = S.vm(X, 4.2)
    qm_px = S.vm(X, 26 if P else 34)
    qtext_w = cw - pad * 2 - qm_px * (0.7 if P else 0.62)       # keep clear of the big "?"
    qm_ = T2.proxy(q) if T2.is_rtl(q) else q
    q0 = fit.fit_text(qm_, qtext_w, 1e5, S.vm(X, 5.2 if P else 4.6), S.vm(X, 3.6), max_lines=4, lh=1.16)
    # never taller than the free area: options shrink first (down to 60 %), then the question
    room = h - S.vm(X, 3) - rv_h - (S.vm(X, 3) if no else 0)
    kpx = S.vm(X, 2.6)
    min_card = max(qm_px * 0.9, pad * 2 + kpx * 2 + q0.n * q0.px * 1.16)     # the whole question must still fit
    if no and opt_h > room - min_card:
        k = max(0.6, (room - min_card) / opt_h)
        oh *= k; opx *= k; opt_h *= k
    ch_max = h - opt_h - rv_h - S.vm(X, 3) - (S.vm(X, 3) if no else 0)
    qf = fit.fit_text(qm_, qtext_w, max(S.vm(X, 8), ch_max - pad * 2 - kpx * 2), S.vm(X, 8.6 if P else 7.4), S.vm(X, 3.6), max_lines=4, lh=1.16)
    if T2.is_rtl(q): qf = fit.Fit(qf.px, [q], qf.em)
    card_h = pad * 2 + kpx * 2 + qf.n * qf.px * 1.16
    card_h = max(card_h, qm_px * 0.9)
    total = card_h + (S.vm(X, 3) + opt_h if no else 0) + rv_h
    cx = x + (w - cw) / 2 if P else x
    cy = y + max(0, (h - total) / 2)
    X.css("fx-qc", CSS)
    html = []
    qm_left = cw - qm_px * 0.7
    face = (f'<div class="qc-face"><div class="qc-qm" data-layout-allow-overlap data-layout-allow-overflow style="left:{qm_left:.0f}px; top:{qm_px * 0.04:.0f}px; font-size:{qm_px:.0f}px">?</div>'
            f'<div class="qc-k" style="left:{pad:.0f}px; top:{pad:.0f}px; font-size:{kpx:.0f}px">{X.rich(kicker)}</div>'
            f'<div class="qc-q" style="left:{pad:.0f}px; top:{pad + kpx * 2:.0f}px; width:{qtext_w:.0f}px; font-size:{qf.px}px;{"direction:rtl;text-align:right" if T2.is_rtl(q) else ""}">'
            + "".join(f'<span class="sl"><span>{X.rich(l)}</span></span>' for l in qf.lines) + "</div></div>")
    back = ""
    if not no and ans_text:
        af = fit.fit_text(ans_text, cw - pad * 2, card_h - pad * 2, S.vm(X, 9), S.vm(X, 3.6), max_lines=3, lh=1.16)
        back = (f'<div class="qc-face qc-back"><div class="qc-a" style="left:{pad:.0f}px; top:{(card_h - af.n * af.px * 1.16) / 2:.0f}px; width:{cw - pad * 2:.0f}px; font-size:{af.px}px">'
                + "".join(f'<span class="sl">{X.rich(l)}</span>' for l in af.lines) + "</div></div>")
    html.append(f'<div class="qc-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{card_h:.0f}px">{face}{back}</div>')
    oy = cy + card_h + S.vm(X, 3)
    if no:
        gap = S.vm(X, 1.6)
        ow = (cw - gap * (cols - 1)) / cols
        pos = [(cx + (i % cols) * (ow + gap), oy + (i // cols) * (oh + S.vm(X, 1.4)), ow) for i in range(no)]
        for i, (ox, oyy, ow) in enumerate(pos):
            txt = opts[i]
            room = ow - opx * 3.2
            f = fit.fit_text(T2.proxy(txt) if T2.is_rtl(txt) else txt, room, oh, opx, S.vm(X, 2.6), max_lines=1)
            html.append(f'<div class="qc-o" data-i="{i}" style="left:{ox:.0f}px; top:{oyy:.0f}px; width:{ow:.0f}px; height:{oh:.0f}px; padding:0 {opx * 0.8:.0f}px; font-size:{f.px}px">'
                        f'<i class="ok"></i><b style="width:{f.px * 1.5:.0f}px; height:{f.px * 1.5:.0f}px; font-size:{max(f.px * 0.72, S.vm(X, 2.6)):.0f}px">{"ABCDE"[i]}</b>'
                        f'<span>{X.rich(txt if T2.is_rtl(txt) else f.lines[0])}</span><span class="tick">✓</span></div>')
        oy += opt_h
    if reveal:
        rf = fit.fit_text(reveal, cw, rvpx * 1.3 * 2, rvpx, S.vm(X, 2.6), max_lines=2, lh=1.3)
        html.append(f'<div class="qc-rv" style="left:{cx:.0f}px; top:{oy + S.vm(X, 3):.0f}px; width:{cw:.0f}px; font-size:{rf.px}px">'
                    + "".join(f'<span class="sl"><span>{X.rich(l)}</span></span>' for l in rf.lines) + "</div>")
    _clip(X, cid, t, d, f'<div class="qc">{"".join(html)}</div>', p)
    s = f"#{cid} .qc"
    X.tw(f'tl.from("{s} .qc-card", {{y:-{S.vm(X, 12):.0f}, rotation:-5, opacity:0, duration:0.7, ease:"back.out(1.6)"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .qc-qm", {{scale:0, rotation:-30, duration:0.6, ease:"back.out(2.6)"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("{s} .qc-qm", {{keyframes:[{{rotation:8, duration:0.5}}, {{rotation:-6, duration:0.5}}, {{rotation:4, duration:0.45}}, {{rotation:0, duration:0.4}}], ease:"sine.inOut", repeat:{max(0, int(d / 1.85))}}}, {t + 0.8:.3f});')
    X.tw(f'tl.from("{s} .qc-k", {{opacity:0, x:-20, duration:0.4}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .qc-q .sl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.09}}, {t + 0.3:.3f});')
    X.sfx(t + 0.05, "pop")
    tr_ = p.get("at_reveal")
    t_rev = float(X.T(tr_, t)) if (tr_ is not None and (X.chars or isinstance(tr_, (int, float)))) else t + max(1.6, d * 0.58)
    if no:
        X.tw(f'tl.from("{s} .qc-o", {{y:{S.vm(X, 4):.0f}, opacity:0, duration:0.45, ease:"back.out(1.8)", stagger:0.12}}, {t + 0.75:.3f});')
        for i in range(no): X.sfx(t + 0.75 + i * 0.12, "click")
        for i in range(no):
            sel = f'{s} .qc-o[data-i=\'{i}\']'
            if i == ans_i:
                X.tw(f'tl.to("{sel} .ok", {{opacity:1, duration:0.25}}, {t_rev:.3f});')
                X.tw(f'tl.to("{sel}", {{color:"#111111", scale:1.05, duration:0.4, ease:"back.out(2.4)"}}, {t_rev:.3f});')
                X.tw(f'tl.to("{sel} .tick", {{opacity:1, duration:0.2}}, {t_rev + 0.15:.3f});')
                X.tw(f'tl.from("{sel} .tick", {{scale:2.2, duration:0.35, ease:"back.out(3)"}}, {t_rev + 0.15:.3f});')
            else:
                X.tw(f'tl.to("{sel}", {{opacity:0.35, scale:0.97, duration:0.35}}, {t_rev:.3f});')
        X.sfx(t_rev, "hit")
    elif ans_text:
        X.tw(f'tl.to("{s} .qc-card", {{rotationY:180, duration:0.8, ease:"power3.inOut"}}, {t_rev:.3f});')
        X.tw(f'tl.from("{s} .qc-a .sl", {{opacity:0, y:20, duration:0.4, stagger:0.08}}, {t_rev + 0.5:.3f});')
        X.sfx(t_rev, "whoosh_soft")
    if reveal:
        X.tw(f'tl.from("{s} .qc-rv .sl > span", {{yPercent:110, duration:0.5, ease:"expo.out", stagger:0.08}}, {t_rev + 0.35:.3f});')


FX = {"question_card": question_card}
