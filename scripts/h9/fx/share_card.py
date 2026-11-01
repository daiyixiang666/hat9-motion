"""金句分享卡 Share Card (结尾的「可以截图转发」的金句卡；小红书 / 朋友圈金句图): a poster-shaped card rises,
the quote mark lands, the quote lifts line by line with its keyword marked, the attribution and handle settle, then a
shutter flash and a small tilt-and-settle say 「this one is for saving」. `export: true` drops the page around it so
scripts/share_card.py can save the card itself as a still.

Adapts: quote 1 glyph to ~120 (1–8 lines, fitted to a 4:5 card; short lines set big), attribution / handle / kicker / date optional.
p: quote (*关键词*) · by · handle · kicker (今日金句) · date · export · hint (适合截图转发)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .sc { position:absolute; inset:0; }
.fx .sc .sc-c { position:absolute; background:var(--card); color:var(--card-fg); border-radius:1.8vmin; box-shadow:0 3vmin 8vmin rgba(0,0,0,.28); overflow:hidden; }
.fx .sc .sc-c::before { content:""; position:absolute; inset:0; background:repeating-linear-gradient(0deg, transparent 0 3px, color-mix(in srgb, var(--card-fg) 3%, transparent) 3px 4px); }
.fx .sc .sc-k { position:absolute; font-family:var(--f-mono, monospace); font-weight:700; letter-spacing:.24em; color:var(--accent); white-space:nowrap; }
.fx .sc .sc-qm { position:absolute; font-family:var(--f-quote, var(--f-display)); font-weight:900; line-height:1; color:var(--accent); }
.fx .sc .sc-q { position:absolute; font-family:var(--f-quote, var(--f-display)); font-weight:900; color:var(--card-fg); line-height:1.3; }
.fx .sc .sc-q .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.08em; } .fx .sc .gl > span { display:inline-block; }
.fx .sc .sc-q .em .emb { left:-.04em; right:-.04em; bottom:.04em; top:auto; height:.38em; background:var(--accent); opacity:.45; transform-origin:0 50%; }
.fx .sc .sc-q .em .emt { position:relative; z-index:1; }
.fx .sc .sc-rule { position:absolute; height:.4vmin; background:var(--card-fg); transform-origin:0 50%; }
.fx .sc .sc-by { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--card-fg); white-space:nowrap; }
.fx .sc .sc-hd { position:absolute; display:flex; align-items:center; gap:.5em; font-family:var(--f-body); font-weight:700; color:color-mix(in srgb, var(--card-fg) 62%, transparent); white-space:nowrap; }
.fx .sc .sc-hd b { display:inline-grid; place-items:center; width:1.7em; height:1.7em; border-radius:50%; background:var(--card-fg); color:var(--card); font-size:.8em; }
.fx .sc .sc-flash { position:absolute; background:#fff; opacity:0; border-radius:1.8vmin; }
.fx .sc .sc-hint { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--bg); background:var(--fg); border-radius:999px; padding:.25em .9em; white-space:nowrap; }
"""


def share_card(X, cid, t, d, p):
    P = X.portrait
    q = fit.as_text(p.get("quote") or p.get("text") or "……")
    by, hd = fit.as_text(p.get("by")), fit.as_text(p.get("handle"))
    kick, date = fit.as_text(p.get("kicker") or "今日金句"), fit.as_text(p.get("date"))
    exp = bool(p.get("export"))
    x, y, w, h = (0, 0, X.W, X.H) if exp else G.area(X, p)
    hint = "" if exp else fit.as_text(p.get("hint", "适合截图转发"))
    X.css("fx-sc", CSS)
    hpx = G.vm(X, 2.6) if hint else 0
    # the card: 4:5, as big as the box allows (export: the whole frame)
    if exp:
        cw, ch = w, h
    else:
        ch = min(h - hpx * 2.4, (w * 0.9) * 5 / 4) if P else min(h - hpx * 0.4, w * 0.5 * 5 / 4)
        cw = ch * 4 / 5
    cx = x + (w - cw) / 2 if (P or exp or p.get("host") is None) else x + (w - cw) / 2
    cy = y + (0 if exp else (h - ch - (hpx * 2.4 if P else 0)) / 2)
    pad = cw * 0.09
    kpx = cw * 0.03
    qmpx = cw * 0.2
    by_px = cw * 0.042
    hd_px = cw * 0.034
    foot = (by_px * 1.6 if by else 0) + (hd_px * 2.4 if (hd or date) else 0)
    qbox = ch - 2 * pad - kpx * 2 - qmpx * 0.55 - foot - pad * 0.6
    nq = len(fit.plain(q).strip())
    qmax = cw * (0.24 if nq <= 3 else 0.16 if nq <= 8 else 0.1)   # a two-word line should fill the card, not sit in a corner
    qf = fit.fit_text(q, cw - 2 * pad, qbox, qmax, cw * 0.036, max_lines=8, lh=1.3)
    html = [f'<div class="sc-c" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px{"; border-radius:0; box-shadow:none" if exp else ""}"></div>']
    yy = cy + pad
    html.append(f'<div class="sc-k" style="left:{cx + pad:.0f}px; top:{yy:.0f}px; font-size:{kpx:.0f}px">{X.rich(kick)}</div>')
    if date: html.append(f'<div class="sc-k" style="left:{cx + cw - pad - (fit.width(date, mono=True) + 0.24 * len(date)) * kpx:.0f}px; top:{yy:.0f}px; font-size:{kpx:.0f}px">{X.rich(date)}</div>')
    yy += kpx * 2
    html.append(f'<div class="sc-qm" data-layout-allow-overlap style="left:{cx + pad - qmpx * 0.06:.0f}px; top:{yy - qmpx * 0.12:.0f}px; font-size:{qmpx:.0f}px">“</div>')
    yy += qmpx * 0.55
    qh = qf.n * qf.px * 1.3
    qy = yy + max(0.0, (qbox - qh) * 0.4)
    html.append(f'<div class="sc-q" style="left:{cx + pad:.0f}px; top:{qy:.0f}px; font-size:{qf.px}px">{G.line_html(X, qf)}</div>')
    fy = cy + ch - pad - foot
    if by or hd: html.append(f'<i class="sc-rule" style="left:{cx + pad:.0f}px; top:{fy - pad * 0.35:.0f}px; width:{cw * 0.16:.0f}px"></i>')
    if by:
        bf = fit.fit_text(by, cw - 2 * pad, by_px * 1.3, by_px, by_px * 0.7, max_lines=1)
        html.append(f'<div class="sc-by" style="left:{cx + pad:.0f}px; top:{fy:.0f}px; font-size:{bf.px}px">{X.rich(bf.lines[0])}</div>')
        fy += by_px * 1.6
    if hd:
        html.append(f'<div class="sc-hd" style="left:{cx + pad:.0f}px; top:{fy + hd_px * 0.4:.0f}px; font-size:{hd_px:.0f}px"><b>{X.rich(fit.plain(hd).lstrip("@")[:1])}</b>{X.rich(hd)}</div>')
    if not exp:
        html.append(f'<i class="sc-flash" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px"></i>')
    card = f'<div class="sc-g" style="position:absolute; inset:0; transform-origin:{cx + cw / 2:.0f}px {cy + ch / 2:.0f}px">{"".join(html)}</div>'
    html = [card]
    if hint:
        hw_ = (fit.width(hint) + 1.8) * hpx
        hx = cx + (cw - hw_) / 2 if P else cx + cw + G.vm(X, 2.4)
        hy = cy + ch + hpx * 0.9 if P else cy + ch - hpx * 2
        html.append(f'<div class="sc-hint" style="left:{hx:.0f}px; top:{hy:.0f}px; font-size:{hpx:.0f}px">{X.rich(hint)}</div>')
    _clip(X, cid, t, d, f'<div class="sc">{"".join(html)}</div>', p)
    s = f"#{cid} .sc"
    if exp:   # a still: everything at rest from the first frame
        X.tw(f'tl.set("{s} .sc-q .em .emb", {{scaleX:1}}, {t:.3f});')
        return
    X.tw(f'tl.from("{s} .sc-g", {{y:80, opacity:0, rotation:-2, duration:0.8, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .sc-k", {{opacity:0, duration:0.4}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .sc-qm", {{scale:0.3, opacity:0, rotation:-20, duration:0.5, ease:"back.out(2.2)"}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .sc-q .gl > span", {{yPercent:110, duration:0.7, ease:"expo.out", stagger:0.12}}, {t + 0.5:.3f});')
    tm = t + 0.9 + qf.n * 0.12
    X.tw(f'tl.fromTo("{s} .sc-q .em .emb", {{scaleX:0}}, {{scaleX:1, duration:0.45, ease:"power3.out", stagger:0.1}}, {tm:.3f});')
    X.tw(f'tl.from("{s} .sc-rule", {{scaleX:0, duration:0.5, ease:"expo.inOut"}}, {tm:.3f});')
    X.tw(f'tl.from("{s} .sc-by, {s} .sc-hd", {{opacity:0, y:12, duration:0.45, ease:"expo.out", stagger:0.1}}, {tm + 0.15:.3f});')
    X.sfx(t + 0.5, "line")
    tsh = max(tm + 0.8, t + d - 1.1)
    # the card keeps floating up a touch until the shutter, so the held seconds are never a still frame
    X.tw(f'tl.fromTo("{s} .sc-g", {{y:0}}, {{y:{-G.vm(X, 1.6):.0f}, duration:{max(0.3, tsh - t - 0.8):.2f}, ease:"sine.inOut", immediateRender:false}}, {t + 0.8:.3f});')
    X.tw(f'tl.fromTo("{s} .sc-flash", {{opacity:0}}, {{keyframes:[{{opacity:0.85, duration:0.05}}, {{opacity:0, duration:0.35, ease:"power2.out"}}], immediateRender:false}}, {tsh:.3f});')
    X.tw(f'tl.to("{s} .sc-g", {{keyframes:[{{scale:0.965, rotation:-1.2, duration:0.18}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2)"}}]}}, {tsh:.3f});')
    X.sfx(tsh, "click")
    if hint: X.tw(f'tl.from("{s} .sc-hint", {{opacity:0, y:14, scale:0.8, duration:0.4, ease:"back.out(2)"}}, {tsh + 0.2:.3f});')


FX = {"share_card": share_card}
