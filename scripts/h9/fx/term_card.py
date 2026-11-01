"""名词解释卡 Term Card (talkcraft info-term-card; 回形针 / 所长林超讲概念时的「词典条目」; Kurzgesagt 的术语定格):
a dictionary entry — the term lands glyph by glyph out of a blur, its reading types on in mono, a part-of-speech
tag pops, a rule draws, the definition lifts line by line and a marker sweeps the key phrase (*…* in the text);
an optional example and source follow. A huge outlined first glyph drifts behind as the page's texture.

Adapts: term 1–14 glyphs (1–2 lines, fitted), reading/English any length (1 line, fitted), definition a phrase to
~90 glyphs (≤ 4 lines), example ≤ 2 lines, all optional except the term.
p: term · reading · pos · definition (*key phrase*) · example · source
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit
from h9.core import esc

CSS = """
.fx .tc { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .tc .tc-g { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1; color:color-mix(in srgb, var(--fg) 5%, transparent);
  -webkit-text-stroke:.35vmin color-mix(in srgb, var(--fg) 16%, transparent); white-space:nowrap; }
.fx .tc .tc-t { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.08; letter-spacing:-.01em; }
.fx .tc .tc-t .sl, .fx .tc .tc-d .sl, .fx .tc .tc-e .sl { display:block; white-space:nowrap; }
.fx .tc .tc-t .tg { display:inline-block; }
.fx .tc .tc-r { position:absolute; font-family:var(--f-mono, monospace); font-weight:500; color:var(--muted); letter-spacing:.06em; white-space:nowrap; }
.fx .tc .tc-p { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--bg); background:var(--fg); border-radius:999px; white-space:nowrap; }
.fx .tc .tc-rule { position:absolute; height:.45vmin; background:var(--fg); transform-origin:0 50%; }
.fx .tc .tc-d { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--fg); line-height:1.42; }
.fx .tc .tc-d .sl { overflow:hidden; padding-bottom:.08em; } .fx .tc .tc-d .sl > span { display:inline-block; }
.fx .tc .tc-d .em .emb { left:-.08em; right:-.08em; bottom:.06em; top:auto; height:.46em; background:var(--accent); opacity:.9; transform-origin:0 50%; }
.fx .tc .tc-d .em .emt { position:relative; z-index:1; }
.fx .tc .tc-e { position:absolute; font-family:var(--f-quote, var(--f-body)); font-style:italic; font-weight:500; color:var(--muted); line-height:1.4;
  border-left:.45vmin solid var(--accent); }
.fx .tc .tc-s { position:absolute; font-family:var(--f-mono, monospace); color:var(--muted); letter-spacing:.04em; white-space:nowrap; }
"""


def term_card(X, cid, t, d, p):
    term = fit.as_text(p.get("term") or p.get("text") or "术语")
    reading, pos_ = fit.as_text(p.get("reading")), fit.as_text(p.get("pos"))
    defin, ex, src = fit.as_text(p.get("definition") or p.get("sub")), fit.as_text(p.get("example")), fit.as_text(p.get("source"))
    x, y, w, h = S.box(X, p)
    P = X.portrait
    cw = w if P else w * (0.62 if p.get("host") else 0.7)
    tf = fit.fit_text(term, cw, h * (0.26 if P else 0.3), S.vm(X, 15 if P else 13), S.vm(X, 6), max_lines=2, lh=1.08)
    rpx = min(S.vm(X, 3.6), tf.px * 0.34)
    rf = fit.fit_text(reading, cw * 0.7, rpx * 1.4, rpx, S.vm(X, 2.4), max_lines=1, mono=True) if reading else None
    ppx = min(S.vm(X, 2.8), tf.px * 0.28)
    df = fit.fit_text(defin, cw, h * (0.3 if P else 0.28), S.vm(X, 5.2 if P else 4.4), S.vm(X, 2.9), max_lines=4, lh=1.42) if defin else None
    ef = fit.fit_text(ex, cw * 0.94, h * 0.14, S.vm(X, 3.4), S.vm(X, 2.5), max_lines=2, lh=1.4) if ex else None
    spx = S.vm(X, 2.2)
    g = S.vm(X, 2.4)
    # stack heights → centre the block in the box
    hs = [tf.n * tf.px * 1.08, (rpx * 1.5 if rf or pos_ else 0), S.vm(X, 2.8), (df.n * df.px * 1.42 if df else 0),
          (ef.n * ef.px * 1.4 + g if ef else 0), (spx * 1.6 if src else 0)]
    tot = sum(hs) + g * 3
    yy = y + max(0, (h - tot) / 2) * (0.8 if P else 1)
    X.css("fx-tc", CSS)
    html = []
    gpx = min(h * 0.9, S.vm(X, 78))
    glyph = fit.plain(term)[:1]
    gx = x + w - gpx * 0.92 if not P else x + w - gpx * 0.8
    html.append(f'<div class="tc-g" data-layout-allow-overlap style="left:{gx:.0f}px; top:{y + (h - gpx) / 2:.0f}px; font-size:{gpx:.0f}px">{X.rich(glyph)}</div>')
    tl_ = "".join(f'<span class="sl">{"".join(f"<i class=tg>{esc(ch)}</i>" if ch.strip() else " " for ch in fit.plain(l))}</span>' for l in tf.lines)
    html.append(f'<div class="tc-t" style="left:{x:.0f}px; top:{yy:.0f}px; font-size:{tf.px}px">{tl_}</div>')
    yy += hs[0] + g * 0.6
    rx = x
    if rf:
        html.append(f'<div class="tc-r" style="left:{rx:.0f}px; top:{yy:.0f}px; font-size:{rf.px}px">{X.rich(rf.lines[0])}</div>')
        rx += (fit.width(rf.lines[0], mono=True) + 0.06 * len(fit.plain(rf.lines[0]))) * rf.px + S.vm(X, 2.4)
    if pos_:
        html.append(f'<div class="tc-p" style="left:{rx:.0f}px; top:{yy + (rpx * 1.25 - ppx * 1.5) / 2:.0f}px; font-size:{ppx:.0f}px; padding:{ppx * 0.18:.0f}px {ppx * 0.7:.0f}px">{X.rich(pos_)}</div>')
    yy += hs[1] + g * 0.5
    html.append(f'<i class="tc-rule" style="left:{x:.0f}px; top:{yy:.0f}px; width:{min(cw, S.vm(X, 30)):.0f}px"></i>')
    yy += hs[2]
    if df:
        dl = "".join(f'<span class="sl"><span>{X.rich(l)}</span></span>' for l in df.lines)
        html.append(f'<div class="tc-d" style="left:{x:.0f}px; top:{yy:.0f}px; width:{cw:.0f}px; font-size:{df.px}px">{dl}</div>')
        yy += hs[3] + g
    if ef:
        html.append(f'<div class="tc-e" style="left:{x:.0f}px; top:{yy:.0f}px; width:{cw:.0f}px; font-size:{ef.px}px; padding-left:{S.vm(X, 2):.0f}px">{S.lines(X, ef)}</div>')
        yy += hs[4]
    if src:
        html.append(f'<div class="tc-s" style="left:{x:.0f}px; top:{yy:.0f}px; font-size:{spx:.0f}px">{X.rich(src)}</div>')
    _clip(X, cid, t, d, f'<div class="tc">{"".join(html)}</div>', p)
    s = f"#{cid} .tc"
    ng = sum(1 for l in tf.lines for ch in fit.plain(l) if ch.strip())
    X.tw(f'tl.fromTo("{s} .tc-g", {{opacity:0, scale:1.15, x:40}}, {{opacity:1, scale:1, x:0, duration:1.2, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .tc-g", {{x:-30, duration:{max(0.5, d - 1.2):.2f}, ease:"none"}}, {t + 1.2:.3f});')
    X.tw(f'tl.from("{s} .tc-t .tg", {{opacity:0, y:"0.25em", filter:"blur(14px)", duration:0.5, ease:"expo.out", stagger:{min(0.06, 0.5 / max(ng, 1)):.3f}}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "enter")
    t1 = t + 0.35 + min(0.5, ng * 0.04)
    if rf: X.tw(f'tl.fromTo("{s} .tc-r", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"steps({max(4, len(rf.lines[0]))})"}}, {t1:.3f});')
    if pos_: X.tw(f'tl.from("{s} .tc-p", {{scale:0, duration:0.35, ease:"back.out(2.4)"}}, {t1 + 0.3:.3f});')
    X.tw(f'tl.from("{s} .tc-rule", {{scaleX:0, duration:0.55, ease:"expo.inOut"}}, {t1 + 0.2:.3f});')
    if df:
        t2 = t1 + 0.45
        X.tw(f'tl.from("{s} .tc-d .sl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.1}}, {t2:.3f});')
        X.tw(f'tl.fromTo("{s} .tc-d .em .emb", {{scaleX:0}}, {{scaleX:1, duration:0.45, ease:"power3.out", stagger:0.12, immediateRender:false}}, {t2 + 0.5 + df.n * 0.1:.3f});')
        X.tw(f'tl.set("{s} .tc-d .em .emb", {{scaleX:0}}, {t:.3f});')
        X.sfx(t2 + 0.5 + df.n * 0.1, "line")
    if ef: X.tw(f'tl.from("{s} .tc-e", {{opacity:0, x:-20, duration:0.5, ease:"expo.out"}}, {t1 + 1.1:.3f});')
    if src: X.tw(f'tl.from("{s} .tc-s", {{opacity:0, duration:0.4}}, {t1 + 1.3:.3f});')


FX = {"term_card": term_card}
