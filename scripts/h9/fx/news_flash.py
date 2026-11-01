"""新闻快讯 News Flash (新闻速报类口播的开场：快讯横幅 + 时间戳 + 滚动字幕；talkcraft news-card-desk 一类):
a neutral broadcast package — the kicker block flashes on, a live dot pulses, the timestamp types, the headline
lifts line by line and gets a red underline, updates drop in one by one with their time tags, and a ticker crawls
along the bottom for the whole beat. No real network's look is imitated.

Adapts: headline 1 glyph to ~60 (1–3 lines), 0–5 updates (each "时间：内容", [时间, 内容] or plain text),
0–10 ticker items (crawl speed follows their length), optional image (any aspect; right column in 16:9, under the
headline in 9:16), kicker / time / source all optional.
p: headline · kicker (快讯) · live (true) · time · source · items · ticker · image · image_label (资料图)
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
.fx .nf { position:absolute; inset:0; }
.fx .nf .nf-band { position:absolute; display:flex; align-items:stretch; background:var(--fg); color:var(--bg); overflow:hidden; border-radius:.6vmin; }
.fx .nf .nf-k { display:flex; align-items:center; gap:.45em; background:var(--nf-r, #d7261e); color:#fff; font-family:var(--f-display); font-weight:900; letter-spacing:.12em; padding:0 .8em; white-space:nowrap; }
.fx .nf .nf-dot { width:.5em; height:.5em; border-radius:50%; background:#fff; flex:none; }
.fx .nf .nf-live { font-family:var(--f-mono, monospace); font-weight:700; letter-spacing:.14em; font-size:.62em; }
.fx .nf .nf-meta { flex:1; display:flex; align-items:center; justify-content:space-between; gap:1em; padding:0 1em; font-family:var(--f-mono, monospace); white-space:nowrap; overflow:hidden; }
.fx .nf .nf-meta .tm { font-weight:700; letter-spacing:.06em; }
.fx .nf .nf-meta .so { opacity:.72; white-space:nowrap; }
.fx .nf .nf-h { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.16; letter-spacing:-.01em; }
.fx .nf .nf-h .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.08em; } .fx .nf .gl > span { display:inline-block; }
.fx .nf .nf-ul { position:absolute; height:.7vmin; background:var(--nf-r, #d7261e); transform-origin:0 50%; }
.fx .nf .nf-img { position:absolute; overflow:hidden; border-radius:.8vmin; box-shadow:0 1.6vmin 4vmin rgba(0,0,0,.25); }
.fx .nf .nf-img img { width:100%; height:100%; object-fit:cover; display:block; }
.fx .nf .nf-img span { position:absolute; left:.6em; top:.5em; font-family:var(--f-mono, monospace); font-size:1.6vmin; color:#fff; background:rgba(0,0,0,.55); padding:.15em .5em; border-radius:.3em; }
.fx .nf .nf-it { position:absolute; display:flex; align-items:baseline; gap:.7em; color:var(--fg); }
.fx .nf .nf-it b { flex:none; font-family:var(--f-mono, monospace); font-weight:700; color:#fff; background:var(--nf-r, #d7261e); padding:.05em .45em; border-radius:.25em; font-size:.82em; }
.fx .nf .nf-it span { font-family:var(--f-body); font-weight:700; white-space:nowrap; }
.fx .nf .nf-tk { position:absolute; display:flex; align-items:stretch; background:var(--fg); color:var(--bg); overflow:hidden; border-radius:.6vmin; }
.fx .nf .nf-tk .lb { flex:none; display:flex; align-items:center; background:var(--nf-r, #d7261e); color:#fff; font-family:var(--f-display); font-weight:900; padding:0 .7em; letter-spacing:.1em; position:relative; z-index:1; }
.fx .nf .nf-tk .rail { position:relative; flex:1; overflow:hidden; }
.fx .nf .nf-tk .run { position:absolute; left:0; top:0; height:100%; display:flex; align-items:center; white-space:nowrap; font-family:var(--f-body); font-weight:700; }
.fx .nf .nf-tk .run i { font-style:normal; margin:0 1.1em; color:var(--nf-r, #d7261e); }
"""


def _items(v):
    out = []
    for it in fit.as_list(v):
        if isinstance(it, dict): out.append((str(it.get("time") or it.get("tag") or ""), str(it.get("text") or "")))
        elif isinstance(it, (list, tuple)): out.append((str(it[0]), str(it[1]) if len(it) > 1 else ""))
        else:
            s = str(it)
            a, sep, b = s.partition("：")
            out.append((a, b) if sep and len(a) <= 8 else ("", s))
    return out[:5]


def news_flash(X, cid, t, d, p):
    P = X.portrait
    head = fit.as_text(p.get("headline") or p.get("text") or "快讯")
    kick = fit.as_text(p.get("kicker") or "快讯")
    tm, so = fit.as_text(p.get("time")), fit.as_text(p.get("source"))
    items = _items(p.get("items"))
    tick = [str(x) for x in fit.as_list(p.get("ticker"))][:10]
    img = p.get("image")
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-nf", CSS)
    html = []
    bh = G.vm(X, 6.6 if not P else 6.2)
    bpx = bh * 0.46
    mpx = bpx * 0.78
    kw = (fit.width(kick) * 1.12 + (3.2 if p.get("live", True) else 0) + 1.6) * bpx
    tmw = (fit.width(tm, mono=True) + 2) * mpx if tm else 0
    if so:   # fit the source into what is left of the band (ellipsis only when it cannot fit at all)
        sof = fit.fit_text(so, max(w - kw - tmw - mpx * 3, mpx * 4), mpx * 1.2, mpx, mpx * 0.75, max_lines=1)
        so, mpx_so = fit.plain(sof.lines[0]), sof.px
    else:
        mpx_so = mpx
    bw_ = w if (tm or so) else min(w, kw)   # nothing to show beside the kicker → the band is just the kicker
    html.append(f'<div class="nf-band" style="left:{x:.0f}px; top:{y:.0f}px; width:{bw_:.0f}px; height:{bh:.0f}px; font-size:{bpx:.0f}px">'
                f'<div class="nf-k">{"<i class=nf-dot></i>" if p.get("live", True) else ""}{X.rich(kick)}{"<span class=nf-live>LIVE</span>" if p.get("live", True) else ""}</div>'
                f'<div class="nf-meta" style="font-size:{mpx:.0f}px"><span class="tm">{X.rich(tm)}</span><span class="so" style="font-size:{mpx_so:.0f}px">{X.rich(so)}</span></div></div>')
    th = G.vm(X, 6.0) if tick else 0
    top = y + bh + g * 1.4
    bottom = y + h - (th + g if tick else 0)
    avail = bottom - top
    if img and not P:
        iw, ih = w * 0.36, avail * 0.62
        hw = w - iw - g * 1.6
        html.append(f'<div class="nf-img" style="left:{x + w - iw:.0f}px; top:{top:.0f}px; width:{iw:.0f}px; height:{ih:.0f}px"><img src="{X.asset(img)}" alt=""><span>{X.rich(p.get("image_label", "资料图"))}</span></div>')
    else:
        hw = w
    share = 0.36 if (img and P and items) else 0.5 if (items or (img and P)) else 0.8
    hf = fit.fit_text(head, hw, avail * share, G.vm(X, 10 if not P else 11), G.vm(X, 4.2), max_lines=3, lh=1.16)
    # stack height → centre headline + image + updates in the free band (biased a little upward)
    ih_p = min(avail * 0.34, w * 0.62) if (img and P) else 0
    rowh = min(G.vm(X, 8.2 if not P else 7.6), avail * 0.42 / max(len(items), 1)) if items else 0
    stack = hf.n * hf.px * 1.16 + g * 1.4 + (ih_p + g if ih_p else 0) + rowh * len(items)
    if stack > avail and ih_p:   # too tall: the picture gives way first, then the update rows
        cut = min(stack - avail, ih_p - avail * 0.14); ih_p -= cut; stack -= cut
    if stack > avail and items:
        rowh = max(G.vm(X, 4), rowh - (stack - avail) / len(items)); stack = hf.n * hf.px * 1.16 + g * 1.4 + (ih_p + g if ih_p else 0) + rowh * len(items)
    top = top + max(0.0, (avail - stack) * 0.42)
    html.append(f'<div class="nf-h" style="left:{x:.0f}px; top:{top:.0f}px; font-size:{hf.px}px">{G.line_html(X, hf)}</div>')
    hy = top + hf.n * hf.px * 1.16
    ulw = min(hw, max(fit.width(l) for l in hf.lines) * hf.px * 0.98)
    html.append(f'<i class="nf-ul" style="left:{x:.0f}px; top:{hy + g * 0.2:.0f}px; width:{ulw * 0.4:.0f}px"></i>')
    yy = hy + g * 1.4
    if img and P:
        ih = ih_p
        html.append(f'<div class="nf-img" style="left:{x:.0f}px; top:{yy:.0f}px; width:{w:.0f}px; height:{ih:.0f}px"><img src="{X.asset(img)}" alt=""><span>{X.rich(p.get("image_label", "资料图"))}</span></div>')
        yy += ih + g
    if items:
        ipx, fits = S.fitpx([b for _, b in items], hw - G.vm(X, 14), rowh * 0.62, G.vm(X, 4.2), G.vm(X, 2.3), max_lines=1)
        for k, (a, b) in enumerate(items):
            tag = f"<b>{X.rich(a)}</b>" if a else "<b>·</b>"
            html.append(f'<div class="nf-it" data-k="{k}" style="left:{x:.0f}px; top:{yy + k * rowh:.0f}px; width:{hw:.0f}px; font-size:{ipx}px">{tag}<span>{X.rich(fits[k].lines[0])}</span></div>')
    if tick:
        tpx = th * 0.44
        body = "".join(f"<span data-layout-allow-occlusion>{X.rich(s_)}</span><i data-layout-allow-occlusion>◆</i>" for s_ in tick)
        tw = sum(fit.width(s_) * tpx + tpx * 2.8 for s_ in tick)
        reps = max(2, int(-(-w * 2 // max(tw, 1))) + 1)
        html.append(f'<div class="nf-tk" data-layout-allow-overflow data-layout-allow-overlap style="left:{x:.0f}px; top:{y + h - th:.0f}px; width:{w:.0f}px; height:{th:.0f}px; font-size:{tpx:.0f}px">'
                    f'<div class="lb">{X.rich(p.get("ticker_label", "滚动"))}</div><div class="rail" data-layout-allow-overflow><div class="run" data-layout-allow-overflow data-layout-allow-overlap data-layout-allow-occlusion>{body * reps}</div></div></div>')
    _clip(X, cid, t, d, f'<div class="nf" style="--nf-r:{"#111" if p.get("theme") == "red" else RED}">{"".join(html)}</div>', p)
    s = f"#{cid} .nf"
    X.tw(f'tl.fromTo("{s} .nf-band", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .nf-k", {{opacity:1}}, {{keyframes:[{{opacity:0.25, duration:0.08}}, {{opacity:1, duration:0.08}}, {{opacity:0.25, duration:0.08}}, {{opacity:1, duration:0.08}}], immediateRender:false}}, {t + 0.35:.3f});')
    if p.get("live", True):
        n = max(1, int((d - 0.6) / 0.9))
        X.tw(f'tl.fromTo("{s} .nf-dot", {{opacity:1}}, {{opacity:0.15, duration:0.45, ease:"sine.inOut", yoyo:true, repeat:{n * 2 - 1}, immediateRender:false}}, {t + 0.6:.3f});')
    if tm: X.tw(f'tl.fromTo("{s} .nf-meta .tm", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.45, ease:"steps({max(4, len(tm))})"}}, {t + 0.3:.3f});')
    if so: X.tw(f'tl.from("{s} .nf-meta .so", {{opacity:0, duration:0.4}}, {t + 0.55:.3f});')
    X.sfx(t, "hit")
    X.tw(f'tl.from("{s} .nf-h .gl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.09}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .nf-ul", {{scaleX:0, duration:0.5, ease:"expo.inOut"}}, {t + 0.6 + hf.n * 0.09:.3f});')
    if img: X.tw(f'tl.fromTo("{s} .nf-img", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:0.7, ease:"expo.inOut"}}, {t + 0.4:.3f});')
    if img: X.tw(f'tl.fromTo("{s} .nf-img img", {{scale:1.12}}, {{scale:1.0, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if items:
        t0 = t + 0.9 + hf.n * 0.09
        step = max(0.25, min(0.7, (d - (t0 - t) - 1.0) / len(items)))
        at = fit.as_list(p.get("at"))
        for k in range(len(items)):
            tk = t0 + k * step
            if k < len(at) and X.chars:
                try: tk = float(X.T(at[k], t)) - 0.1
                except SystemExit: pass
            X.tw(f'tl.from("{s} .nf-it[data-k=\'{k}\']", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {tk:.3f});')
            X.tw(f'tl.fromTo("{s} .nf-it[data-k=\'{k}\'] b", {{scale:1.4}}, {{scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {tk:.3f});')
            X.sfx(tk, "click")
    if tick:
        X.tw(f'tl.from("{s} .nf-tk", {{yPercent:120, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.45:.3f});')
        speed = G.vm(X, 9)      # px / s
        X.tw(f'tl.fromTo("{s} .nf-tk .run", {{x:0}}, {{x:{-speed * d:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


FX = {"news_flash": news_flash}
