"""产品转台 (product turntable · the hero shot of every product promo; the VideoHive "Product Promo"
category): the product stands on a lit disc that turns; with one cut-out picture it sways
in perspective (rotateY with a specular sweep masked to its silhouette, a floor shadow that breathes, a soft
reflection); with several views it steps through them like a real turntable. Spec callouts pop out on leader lines.

p: image (a cut-out PNG / SVG / any picture) | views [images around the product, in order] · name · kicker · price ·
   specs [str | {text, at}] (0–6) · turns (views mode, default 1) · sway (single image, degrees, default 26) · mock
Adapts: any aspect of product art (fitted into the stage), 0–6 specs of any length (≤2 lines, fitted; 16:9 left/right,
9:16 a two-column list), 1–36 views.
"""
import importlib.util, pathlib, sys
from h9 import fit as FT
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


U = _load("_ui")


def turntable(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    views = [v for v in FT.as_list(p.get("views")) if v]
    src = p.get("image") or (views[0] if views else None)
    if not src: raise SystemExit("turntable needs `image` (a product cut-out) or `views`")
    ar = FT.aspect(X, src, 0.6)
    specs = []
    for sp in FT.as_list(p.get("specs"))[:6]:
        specs.append(sp if isinstance(sp, dict) else {"text": str(sp)})
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 24
    aw, ah = x1 - x0, y1 - y0
    title_h = (150 if not P else 170) if (p.get("name") or p.get("kicker")) else 0
    # product box
    if P:
        spec_h = (min(len(specs), 6) + 1) // 2 * 92 + (20 if specs else 0)
        bh = ah - title_h - spec_h - 120
        bw = aw * 0.8
        bcx, btop = x0 + aw / 2, y0 + title_h + 20
    else:
        bh = ah - 160
        bw = aw * (0.36 if specs else 0.5)
        bcx, btop = x0 + aw / 2, y0 + 30
    ph = min(bh, bw / ar); pw = ph * ar
    px_, py_ = bcx - pw / 2, btop + (bh - ph) * 0.4
    disc_w = max(pw * 1.7, min(aw * 0.5, 620) if not P else aw * 0.78)
    if P and specs:      # 9:16: the spec rows sit under the disc; shrink the product until the last row ends inside the area
        over = py_ + ph + disc_w * 0.18 + 40 + spec_h - y1
        if over > 0:
            ph = max(ph - over, ph * 0.55); pw = ph * ar
            px_, py_ = bcx - pw / 2, btop + max(0.0, (bh - over - ph) * 0.4)
            disc_w = max(pw * 1.7, aw * 0.78)
    disc_y = py_ + ph - disc_w * 0.06
    if views:
        imgs = "".join(f'<img class="tt-v" data-k="{k}" src="{X.asset(v)}" alt="">' for k, v in enumerate(views))
        mask = ""
    else:
        url = X.asset(src)
        imgs = f'<img class="tt-v" data-k="0" src="{url}" alt=""><i class="tt-shine" style="-webkit-mask-image:url({url}); mask-image:url({url})"></i>'
        mask = url
    refl = f'<img class="tt-refl" src="{X.asset(src)}" alt="">'
    ticks = "".join(f'<i style="transform:rotate({a}deg) translateX({disc_w / 2 - 14:.0f}px)"></i>' for a in range(0, 360, 15))
    disc = (f'<div class="tt-disc" style="left:{bcx - disc_w / 2:.0f}px; top:{disc_y - disc_w / 2:.0f}px; width:{disc_w:.0f}px; height:{disc_w:.0f}px">'
            f'<div class="tt-ring">{ticks}</div></div>')
    shadow = f'<i class="tt-shadow" style="left:{bcx - pw * 0.55:.0f}px; top:{py_ + ph - pw * 0.08:.0f}px; width:{pw * 1.1:.0f}px; height:{pw * 0.16:.0f}px"></i>'
    glow = f'<i class="tt-glow" style="left:{bcx - disc_w * 0.7:.0f}px; top:{py_ - ph * 0.2:.0f}px; width:{disc_w * 1.4:.0f}px; height:{ph * 1.3:.0f}px"></i>'
    prod = (f'<div class="tt-prod" style="left:{px_:.0f}px; top:{py_:.0f}px; width:{pw:.0f}px; height:{ph:.0f}px">'
            f'<div class="tt-spin">{imgs}</div>{refl}</div>')
    # title
    head = ""
    if title_h:
        nf = FT.fit_text(str(p.get("name", "")), aw * (0.5 if not P else 0.92), 80, 64 if not P else 60, 26, max_lines=1)
        kick = f'<div class="tt-kick">{X.rich(p["kicker"])}</div>' if p.get("kicker") else ""
        price = f'<div class="tt-price">{X.rich(p["price"])}</div>' if p.get("price") else ""
        hx = x0 if not P else x0
        head = f'<div class="tt-head" style="left:{hx:.0f}px; top:{y0:.0f}px; width:{aw * (0.5 if not P else 1):.0f}px">{kick}<b style="font-size:{nf.px}px">{X.rich(nf.lines[0] if nf.lines else "")}</b>{price}</div>'
    # specs with leader lines
    callouts, lines_svg = [], []
    anchors = [(0.78, 0.22), (0.86, 0.5), (0.74, 0.8), (0.22, 0.22), (0.14, 0.5), (0.26, 0.8)]
    order = [0, 3, 1, 4, 2, 5]
    for j, sp in enumerate(specs):
        if P:
            col, row = j % 2, j // 2
            cw = (aw - 24) / 2
            sx, sy = x0 + col * (cw + 24), py_ + ph + disc_w * 0.18 + 40 + row * 92
            f = FT.fit_text(str(sp.get("text", "")), cw - 60, 70, 32, 16, max_lines=2, lh=1.15)
            callouts.append(f'<div class="tt-spec" data-j="{j}" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{cw:.0f}px; font-size:{f.px}px"><i></i><span>{"<br>".join(X.rich(l) for l in f.lines)}</span></div>')
        else:
            a = anchors[order[j]]
            ax, ay = px_ + pw * a[0], py_ + ph * a[1]
            right = a[0] > 0.5
            cw = min(400, (x1 - (px_ + pw) - 90) if right else (px_ - x0 - 90))
            f = FT.fit_text(str(sp.get("text", "")), cw - 40, 90, 34, 16, max_lines=2, lh=1.15)
            sx = (px_ + pw + 80) if right else (px_ - 80 - cw)
            sy = ay - 34
            callouts.append(f'<div class="tt-spec{" r" if right else " l"}" data-j="{j}" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{cw:.0f}px; font-size:{f.px}px"><i></i><span>{"<br>".join(X.rich(l) for l in f.lines)}</span></div>')
            ex = sx if right else sx + cw
            lines_svg.append(f'<path data-j="{j}" d="M{ax:.0f} {ay:.0f} L{(ax + ex) / 2:.0f} {ay:.0f} L{ex:.0f} {sy + 34:.0f}" pathLength="1"/><circle data-j="{j}" cx="{ax:.0f}" cy="{ay:.0f}" r="7"/>')
    svg = f'<svg class="tt-lines" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(lines_svg)}</svg>' if lines_svg else ""
    X.css("fx-turntable", """
.tt-glow { position:absolute; border-radius:50%; background:radial-gradient(closest-side, color-mix(in srgb, var(--accent) 22%, transparent), transparent); }
.tt-disc { position:absolute; border-radius:50%; transform:rotateX(76deg); background:radial-gradient(closest-side, color-mix(in srgb, var(--fg) 10%, var(--bg)), color-mix(in srgb, var(--fg) 4%, var(--bg)) 70%, transparent 71%);
  box-shadow:0 0 0 2px color-mix(in srgb, var(--fg) 12%, transparent); }
.tt-ring { position:absolute; inset:0; }
.tt-ring i { position:absolute; left:50%; top:50%; width:14px; height:4px; margin:-2px 0 0 -7px; background:color-mix(in srgb, var(--fg) 35%, transparent); border-radius:2px; }
.tt-shadow { position:absolute; border-radius:50%; background:radial-gradient(closest-side, rgba(0,0,0,.38), transparent); }
.tt-prod { position:absolute; perspective:1400px; }
.tt-spin { position:absolute; inset:0; transform-style:preserve-3d; }
.tt-v { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; }
.tt-v:not([data-k="0"]) { opacity:0; }
.tt-shine { position:absolute; inset:0; -webkit-mask-size:contain; mask-size:contain; -webkit-mask-repeat:no-repeat; mask-repeat:no-repeat; -webkit-mask-position:center; mask-position:center;
  background:linear-gradient(105deg, transparent 35%, rgba(255,255,255,.75) 48%, transparent 60%); background-size:300% 100%; background-position:100% 0; mix-blend-mode:screen; }
.tt-refl { position:absolute; left:0; top:100%; width:100%; height:100%; object-fit:contain; transform:scaleY(-1); opacity:.16; -webkit-mask-image:linear-gradient(to top, rgba(0,0,0,.9), transparent 45%); mask-image:linear-gradient(to top, rgba(0,0,0,.9), transparent 45%); }
.tt-head { position:absolute; display:flex; flex-direction:column; gap:8px; }
.tt-kick { display:flex; align-items:center; gap:10px; font:700 24px var(--f-mono, monospace); letter-spacing:.12em; color:var(--fg); text-transform:uppercase; }
.tt-kick::before { content:""; width:14px; height:14px; background:var(--accent); }
.tt-head b { font-family:var(--f-display, var(--f-body)); font-weight:900; color:var(--fg); white-space:nowrap; line-height:1.1; }
.tt-price { align-self:flex-start; font:900 40px var(--f-num, var(--f-display)); color:var(--bg); background:var(--fg); padding:4px 16px; border-radius:8px; }
.tt-lines { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.tt-lines path { fill:none; stroke:var(--fg); stroke-width:2.5; stroke-dasharray:1 1; stroke-dashoffset:1; opacity:.7; }
.tt-lines circle { fill:var(--accent); stroke:var(--bg); stroke-width:3; }
.tt-spec { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-body); font-weight:800; color:var(--fg); line-height:1.15; }
.tt-spec.l { flex-direction:row-reverse; text-align:right; }
.tt-spec i { flex:none; width:12px; height:12px; border-radius:50%; background:var(--accent); }
""")
    mk = U.mock(X, p, x1, y0, right=True)
    _clip(X, cid, t, d, f'{glow}{disc}{shadow}{prod}{svg}{"".join(callouts)}{head}{mk}', p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .tt-disc", {{scale:0.6, opacity:0, duration:0.7, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .tt-ring", {{rotation:0}}, {{rotation:{-90 * d:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .tt-prod", {{y:80, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .tt-glow, {s} .tt-shadow", {{opacity:0, duration:0.8}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")
    if views and len(views) > 1:
        n = len(views); turns = max(1, int(p.get("turns", 1)))
        steps = n * turns
        per = (d - 0.6) / steps
        for k in range(1, steps):
            a, b = (k - 1) % n, k % n
            tk = t + 0.4 + k * per
            X.tw(f'tl.set("{s} .tt-v[data-k=\'{a}\']", {{opacity:0}}, {tk:.3f});')
            X.tw(f'tl.set("{s} .tt-v[data-k=\'{b}\']", {{opacity:1}}, {tk:.3f});')
    else:
        sw = float(p.get("sway", 26))
        half = max(1.2, min(2.4, (d - 0.4) / 2))
        reps = max(0, int((d - 0.4) / half) - 1)
        X.tw(f'tl.fromTo("{s} .tt-spin", {{rotationY:{-sw:.1f}}}, {{rotationY:{sw:.1f}, duration:{half:.2f}, ease:"sine.inOut", repeat:{reps}, yoyo:true, immediateRender:false}}, {t + 0.2:.3f});')
        X.tw(f'tl.set("{s} .tt-spin", {{rotationY:{-sw:.1f}}}, {t:.3f});')
        X.tw(f'tl.fromTo("{s} .tt-shine", {{backgroundPosition:"100% 0"}}, {{backgroundPosition:"0% 0", duration:{half:.2f}, ease:"sine.inOut", repeat:{reps}, yoyo:true, immediateRender:false}}, {t + 0.2:.3f});')
        X.tw(f'tl.fromTo("{s} .tt-shadow", {{scaleX:0.82}}, {{scaleX:1.05, duration:{half / 2:.2f}, ease:"sine.inOut", repeat:{2 * reps + 1}, yoyo:true, immediateRender:false}}, {t + 0.2:.3f});')
    X.tw(f'tl.fromTo("{s} .tt-prod", {{y:0}}, {{y:-10, duration:{max(0.5, d - 1.0):.2f}, ease:"sine.inOut", immediateRender:false}}, {t + 0.9:.3f});')
    if head:
        X.tw(f'tl.from("{s} .tt-head > *", {{y:30, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.2:.3f});')
    T = U.spread(len(specs), t + 0.9, t + d - 1.0)
    for j, sp in enumerate(specs):
        tj = U.when(X, sp.get("at"), t, T[j])
        if lines_svg:
            X.tw(f'tl.from("{s} .tt-lines circle[data-j=\'{j}\']", {{scale:0, transformOrigin:"50% 50%", duration:0.3, ease:"back.out(3)"}}, {tj:.3f});')
            X.tw(f'tl.to("{s} .tt-lines path[data-j=\'{j}\']", {{strokeDashoffset:0, duration:0.4, ease:"power2.out"}}, {tj + 0.05:.3f});')
        X.tw(f'tl.from("{s} .tt-spec[data-j=\'{j}\']", {{x:{0 if P else 20}, y:{16 if P else 0}, opacity:0, duration:0.45, ease:"expo.out"}}, {tj + 0.25:.3f});')
        X.sfx(tj, "pop")


FX = {"turntable": turntable}
