"""口播广告位 Sponsor Slot (B 站 / YouTube 口播里的「本期内容由…支持」): a card slides in with an explicit
「广告」 chip (always shown — ads must be labelled), the sponsor's mark and name land, selling points tick in one
by one, the promo code types into a dashed box, the call-to-action pill pulses and a ring counts the ad's seconds
down for the whole beat. Never use a real brand's logo without permission; the demo uses a made-up brand.

Adapts: sponsor name 1 glyph to ~24, 0–4 points (1 glyph to a sentence each), code / cta / logo / product image
optional (image beside the card in 16:9 when there's room, above it in 9:16).
p: sponsor · lead (本期内容由 … 支持) · ad_tag (广告) · points · code · cta · logo · image · note
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .sp { position:absolute; inset:0; }
.fx .sp .sp-c { position:absolute; background:var(--card); color:var(--card-fg); border-radius:1.6vmin; box-shadow:0 2.6vmin 7vmin rgba(0,0,0,.25); }
.fx .sp .sp-ad { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--card); background:var(--card-fg); border-radius:.35em; padding:.08em .5em; white-space:nowrap; }
.fx .sp .sp-lb { position:absolute; font-family:var(--f-body); font-weight:500; color:color-mix(in srgb, var(--card-fg) 60%, transparent); white-space:nowrap; }
.fx .sp .sp-mk { position:absolute; display:grid; place-items:center; border-radius:28%; background:var(--accent); color:var(--bg); font-family:var(--f-display); font-weight:900; overflow:hidden; }
.fx .sp .sp-mk img { width:100%; height:100%; object-fit:cover; }
.fx .sp .sp-n { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--card-fg); line-height:1.08; }
.fx .sp .sp-n .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .sp .gl > span { display:inline-block; }
.fx .sp .sp-pt { position:absolute; display:flex; align-items:center; gap:.55em; font-family:var(--f-body); font-weight:700; color:var(--card-fg); white-space:nowrap; }
.fx .sp .sp-pt i { flex:none; display:inline-grid; place-items:center; width:1.3em; height:1.3em; border-radius:50%; background:var(--accent); color:var(--bg); font-style:normal; font-size:.78em; }
.fx .sp .sp-code { position:absolute; display:flex; align-items:center; gap:.6em; border:.16em dashed var(--card-fg); border-radius:.5em; padding:.2em .7em; white-space:nowrap; }
.fx .sp .sp-code span { font-family:var(--f-body); font-weight:500; font-size:.62em; color:color-mix(in srgb, var(--card-fg) 60%, transparent); }
.fx .sp .sp-code b { font-family:var(--f-mono, monospace); font-weight:700; color:var(--card-fg); letter-spacing:.12em; }
.fx .sp .sp-cta { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--bg); background:var(--fg); border-radius:999px; padding:.3em 1em; white-space:nowrap; }
.fx .sp .sp-ring { position:absolute; }
.fx .sp .sp-ring b { position:absolute; inset:0; display:grid; place-items:center; font-family:var(--f-mono, monospace); font-weight:700; color:var(--card-fg); }
.fx .sp .sp-img { position:absolute; overflow:hidden; border-radius:1.4vmin; box-shadow:0 2vmin 5vmin rgba(0,0,0,.25); }
.fx .sp .sp-img img { width:100%; height:100%; object-fit:cover; display:block; }
"""


def sponsor_card(X, cid, t, d, p):
    P = X.portrait
    name = fit.as_text(p.get("sponsor") or p.get("title") or "赞助商")
    label = fit.as_text(p.get("lead") or f"本期内容由 {fit.plain(name)} 支持")   # not `label`: that is the page footnote
    adt = fit.as_text(p.get("ad_tag") or "广告")
    pts = S.flat(p.get("points"))[:4]
    code, cta = fit.as_text(p.get("code")), fit.as_text(p.get("cta"))
    logo, img = p.get("logo"), p.get("image")
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-gn", G.CSS); X.css("fx-sp", CSS)
    html = []
    side_img = img and not P and not p.get("host")
    if P:
        ih = min(h * 0.28, w * 0.56) if img else 0
        cx, cy, cw, ch = x, y + (ih + g if img else 0), w, h - (ih + g if img else 0)
    else:
        cw = w * (0.56 if (side_img or p.get("host")) else 0.7)
        cx, cy, ch = x + (0 if (side_img or p.get("host")) else (w - cw) / 2), y, h
        if side_img:
            iw = w - cw - g * 2
            html.append(f'<div class="sp-img" style="left:{x + cw + g * 2:.0f}px; top:{y + h * 0.12:.0f}px; width:{iw:.0f}px; height:{h * 0.76:.0f}px"><img src="{X.asset(img)}" alt=""></div>')
    pad = G.vm(X, 3.4)
    ix, iw_ = cx + pad, cw - 2 * pad
    adpx = G.vm(X, 2.4)
    mk = G.vm(X, 9.5 if not P else 10)
    nf = fit.fit_text(name, iw_ - mk - g, mk * 1.1, G.vm(X, 6.6), G.vm(X, 3.2), max_lines=2, lh=1.08)
    ptpx_max = G.vm(X, 3.6)
    rowh = min(G.vm(X, 6.4), (ch * 0.42) / max(len(pts), 1)) if pts else 0
    ptpx, pfits = S.fitpx(pts, iw_ - ptpx_max * 1.8, rowh * 0.7, ptpx_max, G.vm(X, 2.2), max_lines=1) if pts else (0, [])
    cdpx = G.vm(X, 3.6) if code else 0
    ctpx = G.vm(X, 3.6) if cta else 0
    parts = [adpx * 1.6, mk, rowh * len(pts), cdpx * 1.9, ctpx * 1.9]
    tot = sum(parts) + g * (sum(1 for v in parts if v) - 1)
    if P:   # the card hugs its content; picture + card sit together a little above the middle
        room = ch
        ch = min(ch, tot + 2 * pad)
        sh = (room - ch) * 0.42
        cy += sh
        if img: html.append(f'<div class="sp-img" style="left:{x:.0f}px; top:{y + sh:.0f}px; width:{w:.0f}px; height:{ih:.0f}px"><img src="{X.asset(img)}" alt=""></div>')
    else:
        ch = min(ch, tot + 2 * pad)
        cy = cy + (h - ch) / 2
    html.append(f'<div class="sp-c" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px"></div>')
    yy = cy + pad + max(0.0, (ch - 2 * pad - tot) / 2)
    adw = (fit.width(adt) + 1.0) * adpx
    html.append(f'<div class="sp-ad" style="left:{ix:.0f}px; top:{yy:.0f}px; font-size:{adpx:.0f}px">{X.rich(adt)}</div>')
    lbf = fit.fit_text(label, iw_ - adw - g - adpx * 4, adpx * 1.3, adpx, adpx * 0.75, max_lines=1)
    html.append(f'<div class="sp-lb" style="left:{ix + adw + g * 0.6:.0f}px; top:{yy:.0f}px; font-size:{lbf.px}px">{X.rich(lbf.lines[0])}</div>')
    rs = adpx * 2.6
    html.append(f'<div class="sp-ring" data-layout-allow-overlap style="left:{cx + cw - pad - rs:.0f}px; top:{yy - rs * 0.25:.0f}px; width:{rs:.0f}px; height:{rs:.0f}px">'
                f'<svg viewBox="0 0 40 40" width="{rs:.0f}" height="{rs:.0f}"><circle cx="20" cy="20" r="17" fill="none" stroke="var(--line)" stroke-width="3.5"/>'
                f'<circle class="arc" cx="20" cy="20" r="17" fill="none" stroke="var(--accent)" stroke-width="3.5" stroke-linecap="round" stroke-dasharray="106.8" stroke-dashoffset="0" transform="rotate(-90 20 20)"/></svg>'
                f'<b style="font-size:{rs * 0.32:.0f}px" class="sp-sec">{int(round(d))}</b></div>')
    yy += parts[0] + g
    mkin = f'<img src="{X.asset(logo)}" alt="">' if logo else X.rich(fit.plain(name)[:1])
    html.append(f'<div class="sp-mk" style="left:{ix:.0f}px; top:{yy:.0f}px; width:{mk:.0f}px; height:{mk:.0f}px; font-size:{mk * 0.5:.0f}px">{mkin}</div>')
    html.append(f'<div class="sp-n" style="left:{ix + mk + g:.0f}px; top:{yy + (mk - nf.n * nf.px * 1.08) / 2:.0f}px; font-size:{nf.px}px">{G.line_html(X, nf)}</div>')
    yy += mk + g
    for k, f in enumerate(pfits):
        html.append(f'<div class="sp-pt" data-k="{k}" style="left:{ix:.0f}px; top:{yy + k * rowh:.0f}px; height:{rowh:.0f}px; font-size:{ptpx}px"><i>✓</i>{X.rich(f.lines[0])}</div>')
    yy += rowh * len(pts) + (g if pts else 0)
    if code:
        html.append(f'<div class="sp-code" style="left:{ix:.0f}px; top:{yy:.0f}px; font-size:{cdpx:.0f}px"><span>{X.rich(p.get("code_label", "专属码"))}</span><b class="sp-cv">{X.rich(code)}</b></div>')
        yy += cdpx * 1.9 + g
    if cta:
        cf = fit.fit_text(cta, iw_ - ctpx * 2, ctpx * 1.3, ctpx, G.vm(X, 2.4), max_lines=1)
        html.append(f'<div class="sp-cta" style="left:{ix:.0f}px; top:{yy:.0f}px; font-size:{cf.px}px">{X.rich(cf.lines[0])}</div>')
    note = fit.as_text(p.get("note"))
    if note:
        npx = G.vm(X, 1.8)
        html.append(G.note_tag(X, note, cx + cw - pad - (fit.width(note) + 1.2) * npx, cy + ch - pad * 0.5 - npx * 1.4, npx))
    _clip(X, cid, t, d, f'<div class="sp">{"".join(html)}</div>', p)
    s = f"#{cid} .sp"
    X.tw(f'tl.from("{s} .sp-c", {{x:{0 if P else -80}, y:{40 if P else 0}, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    if img: X.tw(f'tl.from("{s} .sp-img", {{opacity:0, scale:1.08, duration:0.8, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .sp-ad", {{scale:0, duration:0.35, ease:"back.out(2.4)"}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .sp-lb", {{opacity:0, x:-12, duration:0.4}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .sp-mk", {{scale:0, rotation:-25, duration:0.5, ease:"back.out(2)"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .sp-n .gl > span", {{yPercent:110, duration:0.55, ease:"expo.out", stagger:0.08}}, {t + 0.38:.3f});')
    X.sfx(t + 0.2, "pop")
    X.tw(f'tl.from("{s} .sp-ring", {{opacity:0, scale:0.6, duration:0.4, ease:"back.out(2)"}}, {t + 0.35:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-ring .arc", {{strokeDashoffset:0}}, {{strokeDashoffset:106.8, duration:{d - 0.35:.2f}, ease:"none"}}, {t + 0.35:.3f});')
    X.tw(f'(()=>{{const o={{v:{d:.2f}}}, el=document.querySelector("{s} .sp-sec"); if(!el) return; tl.to(o, {{v:0, duration:{d:.2f}, ease:"none", onUpdate:()=>{{el.textContent=Math.max(0,Math.ceil(o.v));}}}}, {t:.3f});}})();')
    t0 = t + 0.75
    step = max(0.25, min(0.6, (d - 2.0) / max(len(pts), 1)))
    for k in range(len(pts)):
        X.tw(f'tl.from("{s} .sp-pt[data-k=\'{k}\']", {{opacity:0, x:-18, duration:0.4, ease:"expo.out"}}, {t0 + k * step:.3f});')
        X.tw(f'tl.from("{s} .sp-pt[data-k=\'{k}\'] i", {{scale:0, duration:0.35, ease:"back.out(2.6)"}}, {t0 + k * step + 0.08:.3f});')
        X.sfx(t0 + k * step, "click")
    tc = t0 + len(pts) * step
    if code:
        X.tw(f'tl.from("{s} .sp-code", {{opacity:0, y:10, duration:0.35}}, {tc:.3f});')
        X.tw(f'tl.fromTo("{s} .sp-cv", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"steps({max(3, len(code))})"}}, {tc + 0.15:.3f});')
    if cta:
        tcta = tc + (0.6 if code else 0.1)
        X.tw(f'tl.from("{s} .sp-cta", {{scale:0.4, opacity:0, duration:0.4, ease:"back.out(2.2)"}}, {tcta:.3f});')
        rp = max(1, int((d - (tcta - t) - 0.6) / 0.45)); rp -= (rp % 2 == 0)
        X.tw(f'tl.to("{s} .sp-cta", {{scale:1.07, duration:0.45, ease:"sine.inOut", yoyo:true, repeat:{max(1, rp)}}}, {tcta + 0.5:.3f});')


FX = {"sponsor_card": sponsor_card}
