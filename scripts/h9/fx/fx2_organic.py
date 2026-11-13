"""fx2 · organic: ink_reveal · stamp_press — matter with texture. Rough edges come from SVG turbulence filters (no
bitmaps), so they re-skin with the style's tokens and stay deterministic and seekable.
"""
import importlib.util
import math
import pathlib
import sys

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]
K = A.K

CSS = r"""
.f2 .ir-svg { position:absolute; left:0; top:0; overflow:visible; }
.f2 .sp-paper { position:absolute; background:var(--card); color:var(--card-fg); box-shadow:0 30px 80px rgba(0,0,0,.3), 0 0 0 1px color-mix(in srgb, var(--card-fg) 10%, transparent); }
.f2 .sp-dt { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.15; white-space:nowrap; }
.f2 .sp-ln { position:absolute; height:16px; border-radius:8px; background:color-mix(in srgb, var(--card-fg) 13%, transparent); }
.f2 .sp-mark { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--accent); white-space:nowrap;
  border:12px solid var(--accent); outline:4px solid var(--accent); outline-offset:-30px; }
.f2 .sp-mark.round { border-radius:50%; }
.f2 .sp-mark .w { font-family:var(--f-display); font-weight:900; line-height:1; letter-spacing:.06em; }
.f2 .sp-mark .s { font-family:var(--f-num, var(--f-mono, monospace)); font-weight:800; letter-spacing:.08em; margin-top:.3em; }
.f2 .sp-st { position:absolute; left:0; top:0; transform-origin:50% 100%; }
.f2 .sp-knob { position:absolute; border-radius:50%; background:radial-gradient(circle at 35% 30%, color-mix(in srgb, var(--fg) 60%, var(--bg)), var(--fg) 60%); }
.f2 .sp-neck { position:absolute; background:linear-gradient(90deg, color-mix(in srgb, var(--fg) 70%, #000), var(--fg) 40%, color-mix(in srgb, var(--fg) 60%, #000)); }
.f2 .sp-blk { position:absolute; border-radius:14px; background:linear-gradient(180deg, color-mix(in srgb, var(--fg) 85%, var(--bg)), color-mix(in srgb, var(--fg) 70%, #000)); }
.f2 .sp-rub { position:absolute; border-radius:0 0 8px 8px; background:var(--accent); }
.f2 .sp-sh { position:absolute; border-radius:50%; background:rgba(0,0,0,.45); filter:blur(30px); }
.f2 .sp-dot { position:absolute; border-radius:50%; background:var(--accent); opacity:0; }
"""


def _css(X):
    X.css("fx-f2-org", CSS)


# ------------------------------------------------------------------------------------------------ ink_reveal
def ink_reveal(X, cid, t, d, p):
    """墨迹显影 Ink Reveal: ink drops hit the page and bloom — blots with turbulent, wet edges (SVG turbulence displacing the
    shapes) spread until they join, and the headline (and the beat's picture, if any) is revealed inside the ink, knocked
    out in the ground colour. Works on any ground: the ink is the style's text colour or its accent."""
    F = "ink_reveal"
    text = str(p.get("text") or "")
    src = K.src_of(p)
    A.need(F, t, p, [] if (text or src) else ["text (the headline revealed in the ink) or an image"])
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    ink = "var(--accent)" if p.get("ink") == "accent" else "var(--fg)"
    knock = "var(--k-on)" if p.get("ink") == "accent" else "var(--bg)"
    sub = str(p.get("sub") or "")
    top = G["y0"] + 40
    box_h = G["y1"] - top - 30 - (80 if sub else 0)
    px, lines = A.fit_px(A.strip(text) or " ", G["w"] - 40, box_h, 230 if P else 190, 50, max_lines=3, lh=1.08)
    bh = px * 1.08 * len(lines) + (80 if sub else 0)
    ty0 = top + (box_h + (80 if sub else 0) - bh) / 2
    cy_t = ty0 + bh / 2
    txt = ""
    for i, ln in enumerate(lines):
        base = ty0 + px * 0.88 + i * px * 1.08
        txt += f'<text x="{W / 2:.0f}" y="{base:.0f}" text-anchor="middle" fill="{knock}" style="font-family:var(--f-display); font-weight:900; font-size:{px:.0f}px">{X.rich(A.strip(ln))}</text>'
    if sub:
        spx, sl = A.fit_px(sub, G["w"] - 80, 60, 46 if P else 38, 26, max_lines=1)
        txt += f'<text x="{W / 2:.0f}" y="{ty0 + px * 1.08 * len(lines) + 56:.0f}" text-anchor="middle" fill="{knock}" style="font-family:var(--f-body); font-weight:800; font-size:{spx:.0f}px; letter-spacing:.08em">{X.rich(sl[0])}</text>'
    R = X.rand
    from h9 import fit as FT
    tw_ = max([FT.width(A.strip(l)) * px for l in lines] + [400])
    core = math.hypot(min(tw_, G["w"]) / 2, bh / 2) + 90
    if P:
        blots = [(W / 2, cy_t, core), (G["x0"] + 120, G["y0"] + 120, 260), (G["x1"] - 90, cy_t + 330, 300),
                 (W * 0.3, H - 420, 380), (W * 0.78, H - 170, 400), (W * 0.12, cy_t - 40, 220)]
    else:
        blots = [(W / 2, cy_t, core), (G["x0"] + 80, G["y0"] + 60, 230), (G["x1"] - 60, cy_t + 120, 280),
                 (W * 0.22, H - 120, 300), (W * 0.8, H - 60, 260), (W * 0.62, G["y0"] + 30, 200)]
    splat = []
    for j in range(16):
        bx, by, br = blots[j % len(blots)]
        ang = R.uniform(0, math.tau)
        dist = br * R.uniform(1.05, 1.5)
        splat.append((bx + math.cos(ang) * dist, by + math.sin(ang) * dist, R.uniform(8, 34)))
    circles = ""
    inner_c = ""
    halo = ""
    for i, (x, y, r) in enumerate(blots):
        circles += f'<circle class="bl bl{i}" cx="{x:.0f}" cy="{y:.0f}" r="0" fill="white"/>'
        inner_c += f'<circle class="bi bi{i}" cx="{x:.0f}" cy="{y:.0f}" r="0" fill="white"/>'
        halo += f'<circle class="bh bh{i}" cx="{x:.0f}" cy="{y:.0f}" r="0" fill="white"/>'
    for j, (x, y, r) in enumerate(splat):
        circles += f'<circle class="sp sp{j}" cx="{x:.0f}" cy="{y:.0f}" r="0" fill="white"/>'
    seed = R.randint(1, 90)
    img = ""
    if src:
        img = f'<image href="{X.asset(src)}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice"/>'
        if knock == "var(--bg)":
            txt = txt.replace(f'fill="{knock}"', 'fill="#fff" paint-order="stroke" stroke="rgba(0,0,0,.35)" stroke-width="6"')
    svg = (f'<svg class="ir-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>'
           f'<filter id="IRf_{cid}" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="3" seed="{seed}" result="n"/>'
           f'<feDisplacementMap class="ir-dm" in="SourceGraphic" in2="n" scale="150" xChannelSelector="R" yChannelSelector="G"/></filter>'
           f'<filter id="IRh_{cid}" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" seed="{seed + 7}" result="n"/>'
           f'<feDisplacementMap in="SourceGraphic" in2="n" scale="120" xChannelSelector="R" yChannelSelector="G"/><feGaussianBlur stdDeviation="6"/></filter>'
           f'<mask id="IRm_{cid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><g filter="url(#IRf_{cid})">{circles}</g></mask>'
           f'<mask id="IRi_{cid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><g filter="url(#IRf_{cid})">{inner_c}</g></mask>'
           f'<mask id="IRo_{cid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><g filter="url(#IRh_{cid})">{halo}</g></mask></defs>'
           f'<rect width="{W}" height="{H}" fill="{ink}" opacity=".22" mask="url(#IRo_{cid})"/>'
           f'<rect width="{W}" height="{H}" fill="{ink}" mask="url(#IRm_{cid})"/>'
           f'<g mask="url(#IRi_{cid})">{img}{txt}</g></svg>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, svg)
    t0 = K.U.when(X, p.get("at"), t, None)
    if t0 is None:
        hit = X.spoken_at(A.strip(text), t, t + d) if (text and getattr(X, "chars", None)) else None
        t0 = (hit - 0.3) if hit is not None else t + 0.25
    t0 = max(t + 0.1, min(t0, t + d - 1.6))
    order = [0, 5, 1, 2, 3, 4]
    for rank, i in enumerate(order):
        if i >= len(blots):
            continue
        x, y, r = blots[i]
        at = t0 + rank * 0.16
        dur = 1.1 + 0.15 * rank
        X.tw(f'tl.fromTo("{s} .bl{i}", {{attr:{{r:0}}}}, {{attr:{{r:{r:.0f}}}, duration:{dur:.2f}, ease:"power2.out", immediateRender:true}}, {at:.3f});')
        X.tw(f'tl.fromTo("{s} .bi{i}", {{attr:{{r:0}}}}, {{attr:{{r:{r * 0.93:.0f}}}, duration:{dur:.2f}, ease:"power2.out", immediateRender:true}}, {at + 0.12:.3f});')
        X.tw(f'tl.fromTo("{s} .bh{i}", {{attr:{{r:0}}}}, {{attr:{{r:{r * 1.18:.0f}}}, duration:{dur + 0.6:.2f}, ease:"power1.out", immediateRender:true}}, {at + 0.05:.3f});')
    for j, (x, y, r) in enumerate(splat):
        at = t0 + 0.05 + (j % 6) * 0.05
        X.tw(f'tl.fromTo("{s} .sp{j}", {{attr:{{r:0}}}}, {{attr:{{r:{r:.0f}}}, duration:0.25, ease:"back.out(2)", immediateRender:true}}, {at:.3f});')
    X.tw(f'tl.fromTo("{s} .ir-dm", {{attr:{{scale:190}}}}, {{attr:{{scale:70}}, duration:2.2, ease:"power2.out", immediateRender:true}}, {t0:.3f});')
    late = t0 + 0.16 * len(order) + 1.9
    if late < t + d - 0.3:             # the ink keeps bleeding slowly into the paper after it lands
        for i, (x, y, r) in enumerate(blots):
            X.tw(f'tl.to("{s} .bh{i}", {{attr:{{r:{r * 1.32:.0f}}}, duration:{t + d - late:.2f}, ease:"none"}}, {late:.3f});')
            X.tw(f'tl.to("{s} .bl{i}", {{attr:{{r:{r * 1.07:.0f}}}, duration:{t + d - late:.2f}, ease:"none"}}, {late:.3f});')
        X.tw(f'tl.to("{s} .ir-svg", {{scale:1.04, transformOrigin:"50% 45%", duration:{t + d - late:.2f}, ease:"none"}}, {late:.3f});')
    X.sfx(t0, "brush")


# ------------------------------------------------------------------------------------------------ stamp_press
def stamp_press(X, cid, t, d, p):
    """盖章 Stamp Press: a rubber stamp hangs over the document, then slams down — the stamp squashes, the frame jolts — and
    lifts away, leaving an inked mark with a rough, speckled texture (turbulence-eroded ink): the verdict, a date, a
    total. The slam lands when the narration says it."""
    F = "stamp_press"
    text = str(p.get("text") or "")
    A.need(F, t, p, [] if text else ["text (the word on the stamp)"])
    text = text or "示例"
    sub = str(p.get("sub") or "")
    shape = A.choice(F, p, "shape", ("rect", "round"), "rect")
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    pl, pt = (70, G["y0"] + 10) if P else (G["x0"] + 200, G["y0"] - 10)
    pw = (W - 140) if P else (G["w"] - 400)
    title = str(p.get("title") or "")
    paper = []
    y = 70
    if title:
        tpx, tl_ = A.fit_px(title, pw - 120, 140, 64 if P else 52, 30, max_lines=2, lh=1.15)
        paper.append(f'<div class="sp-dt" style="left:60px; top:{y}px; font-size:{tpx:.0f}px">{A.lines_html(X, tl_)}</div>')
        y += int(tpx * 1.15 * len(tl_)) + 50
    R = X.rand
    while y < H - pt + 40:
        wfrac = R.uniform(0.55, 0.95)
        paper.append(f'<i class="sp-ln" style="left:60px; top:{y}px; width:{(pw - 120) * wfrac:.0f}px"></i>')
        y += 46
    tpx, _ = A.fit_px(A.strip(text), (W - 220) if P else 760, 260, 200 if P else 170, 60, max_lines=1, lh=1.0)
    nch = len(A.strip(text))
    mw = max(tpx * 1.08 * nch + 120, 560)
    spx = 0
    if sub:
        spx, _ = A.fit_px(sub, mw - 100, 80, 64 if P else 52, 26, max_lines=1)
    mh = tpx + (spx * 1.4 if sub else 0) + 110
    if shape == "round":
        mw = mh = max(mw, mh) * 1.02
    mcx = W / 2 if P else W / 2
    mcy = G["y0"] + (G["y1"] - G["y0"]) * (0.5 if P else 0.52)
    mark = (f'<div class="sp-mark {shape}" style="left:{mcx - mw / 2:.0f}px; top:{mcy - mh / 2:.0f}px; width:{mw:.0f}px; height:{mh:.0f}px; filter:url(#SPr_{cid})">'
            f'<span class="w" style="font-size:{tpx:.0f}px">{K.hl_html(X, A.strip(text))}</span>' + (f'<span class="s" style="font-size:{spx:.0f}px">{X.rich(sub)}</span>' if sub else "") + '</div>')
    filt = (f'<svg width="0" height="0" style="position:absolute"><filter id="SPr_{cid}" x="-5%" y="-5%" width="110%" height="110%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.7" numOctaves="2" seed="{R.randint(1, 80)}" result="n"/>'
            f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -5 3.6" result="m"/>'
            f'<feComposite in="SourceGraphic" in2="m" operator="in" result="c"/>'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="{R.randint(1, 80)}" result="w"/>'
            f'<feDisplacementMap in="c" in2="w" scale="7" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')
    bw_, bh_ = mw + 40, 96
    stamp = (f'<div class="sp-st" style="left:{mcx - bw_ / 2:.0f}px; top:{mcy - 560:.0f}px; width:{bw_:.0f}px; height:560px">'
             f'<i class="sp-knob" style="left:{bw_ / 2 - 95:.0f}px; top:0; width:190px; height:190px"></i>'
             f'<i class="sp-neck" style="left:{bw_ / 2 - 46:.0f}px; top:150px; width:92px; height:{560 - 150 - bh_ - 20:.0f}px"></i>'
             f'<i class="sp-blk" style="left:0; top:{560 - bh_ - 22:.0f}px; width:{bw_:.0f}px; height:{bh_}px"></i>'
             f'<i class="sp-rub" style="left:14px; top:{560 - 24:.0f}px; width:{bw_ - 28:.0f}px; height:24px"></i></div>')
    shadow = f'<i class="sp-sh" style="left:{mcx - bw_ * 0.5:.0f}px; top:{mcy - 60:.0f}px; width:{bw_:.0f}px; height:120px"></i>'
    dots = ""
    for j in range(10):
        ang = R.uniform(0, math.tau)
        rr = R.uniform(0.55, 0.8)
        dots += f'<i class="sp-dot" style="left:{mcx + math.cos(ang) * mw * rr:.0f}px; top:{mcy + math.sin(ang) * mh * rr * 1.2:.0f}px; width:{R.uniform(6, 18):.0f}px; height:{R.uniform(6, 18):.0f}px"></i>'
    html = (filt + f'<div class="f2-body"><div class="sp-paper" style="left:{pl:.0f}px; top:{pt:.0f}px; width:{pw:.0f}px; height:{H - pt + 80:.0f}px; transform:rotate(-1.4deg)">{"".join(paper)}</div>'
            f'{shadow}{mark}{dots}{stamp}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, html)
    ti = K.U.when(X, p.get("at"), t, None)
    if ti is None:
        hit = X.spoken_at(A.strip(text), t, t + d) if getattr(X, "chars", None) else None
        ti = hit if hit is not None else t + min(0.95, d * 0.3)
    ti = max(t + 0.6, min(ti, t + d - 0.9))
    rot = float(p.get("tilt", -7))
    X.tw(f'tl.set("{s} .sp-mark", {{opacity:0, rotation:{rot}}}, {t:.3f});')
    X.tw(f'tl.set("{s} .sp-st", {{rotation:{rot}}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-st", {{y:-1300, scale:1.18}}, {{y:-300, scale:1.18, duration:0.5, ease:"power3.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-st", {{y:-300}}, {{y:-330, duration:{max(0.1, ti - 0.14 - t - 0.55):.2f}, ease:"sine.inOut", immediateRender:false}}, {t + 0.55:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-sh", {{opacity:0.15, scale:1.5}}, {{opacity:0.3, scale:1.3, duration:0.5, immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.to("{s} .sp-st", {{y:0, scale:1, duration:0.14, ease:"power4.in"}}, {ti - 0.14:.3f});')
    X.tw(f'tl.to("{s} .sp-sh", {{opacity:0.7, scale:1, duration:0.14, ease:"power4.in"}}, {ti - 0.14:.3f});')
    X.tw(f'tl.to("{s} .sp-st", {{scaleY:0.9, scaleX:1.03, duration:0.06, ease:"power2.out"}}, {ti:.3f});')
    X.tw(f'tl.to("{s} .sp-st", {{scaleY:1, scaleX:1, duration:0.12, ease:"power2.out"}}, {ti + 0.06:.3f});')
    X.tw(f'tl.to("{s} .sp-st", {{y:-1500, scale:1.25, duration:0.5, ease:"power3.in"}}, {ti + 0.3:.3f});')
    X.tw(f'tl.to("{s} .sp-sh", {{opacity:0, scale:1.8, duration:0.4}}, {ti + 0.3:.3f});')
    X.tw(f'tl.set("{s} .sp-mark", {{opacity:1}}, {ti:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-mark", {{scale:1.05}}, {{scale:1, duration:0.25, ease:"power2.out", immediateRender:false}}, {ti:.3f});')
    X.tw(f'tl.fromTo("{s} .sp-dot", {{opacity:0, scale:0.2}}, {{opacity:0.9, scale:1, duration:0.12, stagger:0.01, immediateRender:false}}, {ti:.3f});')
    A.shake(X, f"{s} .f2-body", ti + 0.01, amp=20, n=7)
    X.tw(f'tl.fromTo("{s} .f2-body", {{scale:1}}, {{scale:1.05, transformOrigin:"50% 40%", duration:{t + d - ti - 0.3:.2f}, ease:"none", immediateRender:false}}, {ti + 0.3:.3f});')
    X.sfx(ti, "slam")


FX = {"ink_reveal": ink_reveal, "stamp_press": stamp_press}
