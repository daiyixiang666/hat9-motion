"""带货价签 Deal Card (带货 / 种草口播的价格页；Envato「Modern Price Tags & Counters」一类): the original price
appears and a red stroke strikes it out, the new price slams in with a ring burst, the saving badge pops, a coupon
tears in along its perforation, the countdown ticks down second by second for the whole beat and the stock bar
drains. Prices must be real and sourced, or the card carries a visible 「示意」 tag.

Adapts: product name 1 glyph to ~30 (≤ 2 lines), prices of any size (¥ / $ / no symbol, decimals kept), 0–4 tags,
coupon / countdown / stock all optional, image any aspect (left in 16:9, top in 9:16) or a typographic tile.
p: product · sub · image · price · was · cur (¥) · unit (/杯) · coupon · tags · countdown (seconds | "HH:MM:SS") ·
   stock ([剩, 共] | "仅剩 23 件") · note · at (cue for the slam)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

RED = "#d7261e"
CSS = """
.fx .dl { position:absolute; inset:0; }
.fx .dl .dl-pic { position:absolute; overflow:hidden; border-radius:1.4vmin; box-shadow:0 2.4vmin 6vmin rgba(0,0,0,.22); background:var(--card); }
.fx .dl .dl-pic img { width:100%; height:100%; object-fit:cover; display:block; }
.fx .dl .dl-tile { position:absolute; inset:0; display:grid; place-items:center; background:var(--accent); color:var(--bg); }
.fx .dl .dl-tile b { font-family:var(--f-display); font-weight:900; line-height:1; }
.fx .dl .dl-tags { position:absolute; display:flex; flex-wrap:wrap; gap:.5em; }
.fx .dl .dl-tags span { font-family:var(--f-body); font-weight:700; color:""" + RED + """; border:.18em solid """ + RED + """; border-radius:.35em; padding:.05em .5em; white-space:nowrap; }
.fx .dl .dl-n { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .dl .dl-n .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .dl .gl > span { display:inline-block; }
.fx .dl .dl-s { position:absolute; font-family:var(--f-body); color:var(--muted); white-space:nowrap; }
.fx .dl .dl-was { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:700; color:var(--muted); white-space:nowrap; }
.fx .dl .dl-was i { position:absolute; left:-6%; right:-6%; top:52%; height:.12em; background:""" + RED + """; transform-origin:0 50%; transform:rotate(-8deg); }
.fx .dl .dl-now { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; color:""" + RED + """; line-height:.86; white-space:nowrap; }
.fx .dl .dl-now small { font-size:.4em; font-weight:800; margin-right:.04em; vertical-align:.95em; }
.fx .dl .dl-now em { font-style:normal; font-size:.26em; font-family:var(--f-body); font-weight:700; color:var(--fg); margin-left:.25em; }
.fx .dl .dl-ring { position:absolute; border-radius:50%; border:.6vmin solid """ + RED + """; opacity:0; }
.fx .dl .dl-save { position:absolute; display:grid; place-items:center; text-align:center; border-radius:50%; background:""" + RED + """; color:#fff;
  font-family:var(--f-display); font-weight:900; line-height:1.05; transform:rotate(12deg); }
.fx .dl .dl-cp { position:absolute; display:flex; align-items:stretch; background:#fff3e8; color:""" + RED + """; border-radius:.8vmin; overflow:hidden; }
.fx .dl .dl-cp .l { display:flex; align-items:center; padding:0 .9em; font-family:var(--f-display); font-weight:900; white-space:nowrap; }
.fx .dl .dl-cp .r { display:flex; align-items:center; padding:0 .8em; font-family:var(--f-body); font-weight:700; font-size:.7em; background:""" + RED + """; color:#fff;
  border-left:.18em dashed #fff3e8; white-space:nowrap; }
.fx .dl .dl-cd { position:absolute; display:flex; align-items:center; gap:.6em; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; }
.fx .dl .dl-cd b { font-family:var(--f-mono, monospace); font-weight:700; color:var(--bg); background:var(--fg); padding:.05em .4em; border-radius:.25em; letter-spacing:.04em; }
.fx .dl .dl-st { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; }
.fx .dl .dl-st .tr { margin-top:.35em; height:.5em; border-radius:999px; background:color-mix(in srgb, var(--fg) 12%, transparent); overflow:hidden; }
.fx .dl .dl-st .tr i { display:block; height:100%; background:linear-gradient(90deg, """ + RED + """, #ff8a3d); border-radius:999px; transform-origin:0 50%; }
"""


def _secs(v):
    if v is None or v == "": return None
    if isinstance(v, (int, float)): return int(v)
    parts = [int(x) for x in str(v).split(":") if x.strip().isdigit()]
    s = 0
    for x in parts: s = s * 60 + x
    return s if parts else None


def _price(v):
    s = str(v).strip()
    n = G.num(s)
    return (n, G.dec_of(s.replace("¥", "").replace("$", ""))) if n is not None else (None, 0)


def deal_card(X, cid, t, d, p):
    P = X.portrait
    name = fit.as_text(p.get("product") or p.get("title") or "商品")
    sub = fit.as_text(p.get("sub"))
    cur = p.get("cur", "¥")
    now, nd = _price(p.get("price", ""))
    was, wd = _price(p.get("was", "")) if p.get("was") not in (None, "") else (None, 0)
    unit = fit.as_text(p.get("unit"))
    tags = [str(x) for x in fit.as_list(p.get("tags"))][:4]
    coupon = fit.as_list(p.get("coupon"))
    cd = _secs(p.get("countdown"))
    stock = p.get("stock")
    img = p.get("image")
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-gn", G.CSS); X.css("fx-dl", CSS)
    html = []
    if P:
        busy = sum(1 for v in (p.get("coupon"), p.get("countdown"), p.get("stock"), p.get("tags")) if v not in (None, "", []))
        pw, ph = w, h * (0.34 if busy <= 1 else 0.26 if busy == 2 else 0.2)
        px_, py_ = x, y
        rx, ry, rw, rh = x, y + ph + g * 1.4, w, h - ph - g * 1.4
    else:
        pw, ph = w * 0.4, h
        px_, py_ = x, y
        rx, ry, rw, rh = x + pw + g * 2.2, y, w - pw - g * 2.2, h
    if img:
        pic = f'<img src="{X.asset(img)}" alt="">'
    else:
        tpx = min(ph * 0.42, pw * 0.38)
        pic = f'<div class="dl-tile"><b style="font-size:{tpx:.0f}px">{X.rich(fit.plain(name)[:1])}</b></div>'
    html.append(f'<div class="dl-pic" style="left:{px_:.0f}px; top:{py_:.0f}px; width:{pw:.0f}px; height:{ph:.0f}px">{pic}</div>')
    note = fit.as_text(p.get("note"))
    if note: html.append(G.note_tag(X, note, px_ + G.vm(X, 1.6), py_ + G.vm(X, 1.6), G.vm(X, 2)))
    # right column: measure everything, then centre the stack
    tpx = G.vm(X, 2.6)
    nf = fit.fit_text(name, rw, rh * 0.18, G.vm(X, 6.4), G.vm(X, 3.2), max_lines=2, lh=1.12)
    sf = fit.fit_text(sub, rw, G.vm(X, 3.6), G.vm(X, 2.8), G.vm(X, 2), max_lines=1) if sub else None
    nowtxt = f"{now:,.{nd}f}" if now is not None else fit.as_text(p.get("price"))
    cph = G.vm(X, 6.2 if not P else 5.6) if coupon else 0
    cdh = G.vm(X, 4.6 if not P else 4.2) if cd is not None else 0
    sth = G.vm(X, 5.4 if not P else 5.0) if stock not in (None, "") else 0
    fixed = (tpx * 1.6 if tags else 0) + nf.n * nf.px * 1.12 + (sf.px * 1.4 if sf else 0) + cph + cdh + sth
    nparts = sum(1 for v in (tags, True, sf, was is not None, True, coupon, cd is not None, stock not in (None, "")) if v)
    room = rh - fixed - g * (nparts - 1)            # what is left for the was + now prices
    npx = max(G.vm(X, 7), min(G.vm(X, 22 if not P else 24), room / (0.9 + (0.41 if was is not None else 0)), rw * 0.62 / max(0.62 * len(nowtxt) + 0.5, 1)))
    wpx = npx * 0.34
    parts = [tpx * 1.6 if tags else 0, nf.n * nf.px * 1.12, sf.px * 1.4 if sf else 0, wpx * 1.2 if was is not None else 0, npx * 0.9, cph, cdh, sth]
    gaps = g * (sum(1 for v in parts if v) - 1)
    yy = ry + max(0.0, (rh - sum(parts) - gaps) / 2)
    if tags:
        html.append(f'<div class="dl-tags" style="left:{rx:.0f}px; top:{yy:.0f}px; width:{rw:.0f}px; font-size:{tpx:.0f}px">' + "".join(f"<span>{X.rich(s_)}</span>" for s_ in tags) + "</div>")
        yy += parts[0] + g
    html.append(f'<div class="dl-n" style="left:{rx:.0f}px; top:{yy:.0f}px; font-size:{nf.px}px">{G.line_html(X, nf)}</div>')
    yy += parts[1] + g
    if sf:
        html.append(f'<div class="dl-s" style="left:{rx:.0f}px; top:{yy:.0f}px; font-size:{sf.px}px">{X.rich(sf.lines[0])}</div>')
        yy += parts[2] + g
    if was is not None:
        html.append(f'<div class="dl-was" style="left:{rx:.0f}px; top:{yy:.0f}px; font-size:{wpx:.0f}px">原价 {X.rich(cur)}{was:,.{wd}f}<i></i></div>')
        yy += parts[3] + g
    ny = yy
    html.append(f'<div class="dl-now" style="left:{rx:.0f}px; top:{ny:.0f}px; font-size:{npx:.0f}px"><small>{X.rich(cur)}</small>{X.rich(nowtxt)}'
                f'{f"<em>{X.rich(unit)}</em>" if unit else ""}</div>')
    nw = (0.4 * fit.width(cur) + fit.width(nowtxt) * 0.95) * npx
    rs = npx * 1.3
    html.append(f'<i class="dl-ring" style="left:{rx + nw / 2 - rs / 2:.0f}px; top:{ny + npx * 0.43 - rs / 2:.0f}px; width:{rs:.0f}px; height:{rs:.0f}px"></i>')
    if was is not None and now is not None and was > now:
        save = was - now
        sd = 0 if save >= 100 else max(nd, wd)
        sz = max(G.vm(X, 10), min(npx * 0.85, G.vm(X, 15)))
        stxt = f"省{cur}{save:,.{sd}f}"
        pct = round(save / was * 100)
        if len(stxt) > 6:   # a long amount will not read at badge size: the percentage alone, big
            inner_ = f'<span style="font-size:{sz * 0.17:.0f}px">立省</span><br><span style="font-size:{sz * 0.3:.0f}px">-{pct}%</span>'
        else:
            inner_ = f'{X.rich(stxt)}<br><span style="font-size:{sz * 0.24:.0f}px">-{pct}%</span>'
        sfs = sz * 0.2 * min(1.0, 5.5 / max(len(stxt), 1))
        sx = min(rx + nw + (fit.width(unit) * 0.26 * npx if unit else 0) + g, rx + rw - sz)
        html.append(f'<div class="dl-save" style="left:{sx:.0f}px; top:{ny - sz * 0.25:.0f}px; width:{sz:.0f}px; height:{sz:.0f}px; font-size:{sfs:.0f}px">{inner_}</div>')
    yy = ny + npx * 0.9 + g
    if coupon:
        a, b = (str(coupon[0]), str(coupon[1]) if len(coupon) > 1 else "领券")
        cpx = cph * 0.44
        html.append(f'<div class="dl-cp" style="left:{rx:.0f}px; top:{yy:.0f}px; height:{cph:.0f}px; font-size:{cpx:.0f}px"><span class="l">{X.rich(a)}</span><span class="r">{X.rich(b)}</span></div>')
        yy += cph + g
    if cd is not None:
        hh, mm, ss = cd // 3600, cd % 3600 // 60, cd % 60
        html.append(f'<div class="dl-cd" style="left:{rx:.0f}px; top:{yy:.0f}px; font-size:{cdh * 0.56:.0f}px">{X.rich(p.get("countdown_label", "限时"))}'
                    f'<b class="dl-cdv">{hh:02d}:{mm:02d}:{ss:02d}</b></div>')
        yy += cdh + g
    if stock not in (None, ""):
        if isinstance(stock, (list, tuple)) and len(stock) >= 2 and G.num(stock[0]) is not None:
            left, tot = G.num(stock[0]), G.num(stock[1]) or 1
            lab, frac = f"仅剩 {int(left)} 件", max(0.02, min(1.0, left / tot))
        else:
            lab, frac = fit.as_text(stock), 0.22
        sw = min(rw, G.vm(X, 44))
        html.append(f'<div class="dl-st" style="left:{rx:.0f}px; top:{yy:.0f}px; width:{sw:.0f}px; font-size:{sth * 0.46:.0f}px">{X.rich(lab)}'
                    f'<div class="tr"><i style="width:{frac * 100:.0f}%"></i></div></div>')
    _clip(X, cid, t, d, f'<div class="dl">{"".join(html)}</div>', p)
    s = f"#{cid} .dl"
    X.tw(f'tl.from("{s} .dl-pic", {{y:50, opacity:0, scale:0.94, duration:0.7, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .dl-pic img, {s} .dl-tile b", {{scale:1.12}}, {{scale:1.0, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if tags: X.tw(f'tl.from("{s} .dl-tags span", {{scale:0.4, opacity:0, duration:0.35, ease:"back.out(2.2)", stagger:0.07}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .dl-n .gl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {t + 0.15:.3f});')
    if sf: X.tw(f'tl.from("{s} .dl-s", {{opacity:0, duration:0.4}}, {t + 0.4:.3f});')
    X.sfx(t + 0.1, "enter")
    ts = S.beats(X, {"at": p.get("at")}, t, d, 1)[0] if p.get("at") else t + min(1.3, d * 0.32)
    if was is not None:
        X.tw(f'tl.from("{s} .dl-was", {{opacity:0, x:-20, duration:0.4, ease:"expo.out"}}, {t + 0.45:.3f});')
        X.tw(f'tl.fromTo("{s} .dl-was i", {{scaleX:0}}, {{scaleX:1, duration:0.28, ease:"power4.out"}}, {ts - 0.35:.3f});')
        X.sfx(ts - 0.35, "click")
    X.tw(f'tl.fromTo("{s} .dl-now", {{scale:2.1, opacity:0, transformOrigin:"0% 60%"}}, {{scale:1, opacity:1, duration:0.36, ease:"back.out(1.6)", immediateRender:true}}, {ts:.3f});')
    X.tw(f'tl.fromTo("{s} .dl-ring", {{scale:0.4, opacity:0.9}}, {{scale:1.6, opacity:0, duration:0.6, ease:"expo.out", immediateRender:false}}, {ts + 0.1:.3f});')
    X.sfx(ts, "slam")
    X.tw(f'tl.from("{s} .dl-save", {{scale:0, rotation:-40, duration:0.45, ease:"back.out(2.4)"}}, {ts + 0.35:.3f});')
    rp = max(1, int((d - (ts - t) - 0.8) / 0.5)); rp -= (rp % 2 == 0)      # odd → ends back at scale 1
    X.tw(f'tl.to("{s} .dl-save", {{scale:1.06, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:{max(1, rp)}}}, {ts + 0.8:.3f});')
    if coupon:
        X.tw(f'tl.fromTo("{s} .dl-cp", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"expo.inOut"}}, {ts + 0.5:.3f});')
        X.tw(f'tl.from("{s} .dl-cp .r", {{x:20, duration:0.35, ease:"back.out(2)"}}, {ts + 0.85:.3f});')
        X.sfx(ts + 0.5, "click")
    if cd is not None:
        X.tw(f'tl.from("{s} .dl-cd", {{opacity:0, y:12, duration:0.4}}, {ts + 0.6:.3f});')
        X.tw(f'(()=>{{const o={{v:{cd}}}, el=document.querySelector("{s} .dl-cdv"); if(!el) return; const f=(n)=>String(n).padStart(2,"0"); '
             f'tl.to(o, {{v:{max(0, cd - d)}, duration:{d:.2f}, ease:"none", onUpdate:()=>{{const k=Math.max(0,Math.ceil(o.v)); el.textContent=f(Math.floor(k/3600))+":"+f(Math.floor(k%3600/60))+":"+f(k%60);}}}}, {t:.3f});}})();')
    if stock not in (None, ""):
        X.tw(f'tl.from("{s} .dl-st", {{opacity:0, y:12, duration:0.4}}, {ts + 0.7:.3f});')
        X.tw(f'tl.fromTo("{s} .dl-st .tr i", {{scaleX:1}}, {{scaleX:0.82, duration:{max(0.5, d - (ts - t) - 0.7):.2f}, ease:"power1.in", immediateRender:false}}, {ts + 0.7:.3f});')


FX = {"deal_card": deal_card}
