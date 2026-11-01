"""主持人和内容互动 (the host points at the content — "看这里"): the host stands beside a card; on the cue a hand-drawn
arrow sweeps from the host to the target, the host leans in, the target rings and its number counts up, and a
speech bubble says the line. Works with a number, a short statement or a picture with a box to point at.

p: host (video; default meta.host_video / meta.mascot) · card {kind: number|text|image, value, unit, label, sub,
   image, box:[x%,y%,w%,h%]} (text cards take `text` or `value`) · say (bubble text) · at (point moment: "@词" / seconds; default 35 %) · side (host
   left | right) · src (shown in the page footer)
Adapts: number / text / image cards (text fitted to 3 lines, numbers formatted 万/亿), host on either side,
no host (the arrow starts from the corner), 16:9 side by side or 9:16 card above, host below.
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A, C = _load("_av"), _load("_cite")

CSS = """
.hp-card { position:absolute; background:var(--card); color:var(--card-fg, var(--fg)); border-radius:22px; box-shadow:0 30px 80px rgba(0,0,0,.25); overflow:hidden; }
.hp-card .lab { position:absolute; font:800 26px var(--f-body); letter-spacing:.06em; color:var(--muted); }
.hp-card .num { position:absolute; font-family:var(--f-num, var(--f-display)); font-variation-settings:"wdth" 70, "wght" 900; font-weight:900; line-height:.85; color:var(--accent); white-space:nowrap; }
.hp-card .num small { font-family:var(--f-display); font-size:.36em; color:var(--card-fg, var(--fg)); margin-left:.12em; }
.hp-card .txt { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.18; }
.hp-card .sub { position:absolute; font:700 26px var(--f-body); color:var(--muted); letter-spacing:0; }
.hp-card img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.hp-ring { position:absolute; border:6px solid #f6ce3a; border-radius:16px; opacity:0; }
.hp-arrow { position:absolute; inset:0; overflow:visible; pointer-events:none; }
.hp-arrow path { fill:none; stroke:var(--accent); stroke-width:10; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 3px 0 rgba(0,0,0,.18)); }
.hp-bub { position:absolute; opacity:0; }
.hp-bub b { position:relative; display:inline-block; font-family:var(--f-body); font-weight:900; color:#111; background:#fbfaf6; padding:.42em .75em; border-radius:.75em; box-shadow:0 .2em .7em rgba(0,0,0,.28); line-height:1.25; }
.hp-bub b::after { content:''; position:absolute; bottom:-.4em; left:1.2em; width:.8em; height:.8em; background:#fbfaf6; transform:rotate(45deg); }
.hp-bub.r b::after { left:auto; right:1.2em; }
"""


def host_point(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    host = A.host_src(X, p)
    side = p.get("side", "left")
    tp = A.when(X, p, "at", t, d, 0.35)
    card = p.get("card") or {}
    kind = card.get("kind") or ("image" if card.get("image") else "number" if card.get("value") is not None else "text")
    # layout
    if P:
        cx, cy, cw, ch = 56, 262, W - 112, 520
        hs = 500; hx = 30 if side == "left" else W - 30 - hs; hy = 1300 - hs
    else:
        hs = H * 0.78; hx = 30 if side == "left" else W - 30 - hs; hy = H - hs
        cw, ch = W * 0.5, H * 0.56
        cx = (W - 96 - cw) if side == "left" else 96
        cy = (H - ch) / 2 - 30
    pad = 40
    body = ""
    tx, ty, tw_, th_ = cx + cw * 0.15, cy + ch * 0.25, cw * 0.7, ch * 0.5     # the point target (screen px)
    lab = card.get("label", ""); sub = card.get("sub", "")
    X.used_text.update(str(lab) + str(sub))
    if kind == "number":
        v = card.get("value")
        unit = card.get("unit", "")
        txt = fit.fmt_num(v) if isinstance(v, (int, float)) else str(v)
        X.used_text.update(txt + str(unit) + "0123456789.,")
        npx = min(ch * 0.42, (cw - 2 * pad) / max(1, len(txt) * 0.62 + len(str(unit)) * 0.4))
        body = (f'<div class="lab" style="left:{pad}px; top:{pad}px">{X.rich(lab)}</div>'
                f'<div class="num" style="left:{pad}px; top:{ch * 0.3:.0f}px; font-size:{npx:.0f}px"><span class="hp-n">{X.rich(txt)}</span><small>{X.rich(unit)}</small></div>'
                + (f'<div class="sub" style="left:{pad}px; bottom:{pad}px">{X.rich(sub)}</div>' if sub else ""))
        tx, ty, tw_, th_ = cx + pad - 14, cy + ch * 0.3 - 14, min(cw - 2 * pad + 28, npx * (len(txt) * 0.62 + len(str(unit)) * 0.4) + 28), npx * 0.95 + 28
    elif kind == "image":
        foc = (50, 50)
        if card.get("box"):     # crop toward the box so the target is never cut away by the card's shape
            b = [float(v) for v in card["box"]]
            foc = (max(0, min(100, b[0] + b[2] / 2)), max(0, min(100, b[1] + b[3] / 2)))
        body = f'<img src="{X.asset(card["image"])}" alt="" style="object-position:{foc[0]:.0f}% {foc[1]:.0f}%">' + (f'<div class="lab" style="left:{pad}px; top:{pad}px; color:#fff; text-shadow:0 2px 8px rgba(0,0,0,.6)">{X.rich(lab)}</div>' if lab else "")
        if card.get("box"):
            bx, by, bw, bh = A.cover_map(X, card["image"], card["box"], frame=(cx, cy, cw, ch), focus=foc)
            tx, ty, tw_, th_ = bx, by, bw, bh
    else:
        f = C.fitted(X, card.get("text") or card.get("value", ""), cw - 2 * pad, ch - 2 * pad - 110, 72 if not P else 66, 30, max_lines=3, lh=1.18)
        body = (f'<div class="lab" style="left:{pad}px; top:{pad}px">{X.rich(lab)}</div>'
                f'<div class="txt" style="left:{pad}px; top:{pad + 56 + (ch - 2 * pad - 60 - f.n * f.px * 1.18) / 2:.0f}px; font-size:{f.px}px">{C.lines(X, f)}</div>'
                + (f'<div class="sub" style="left:{pad}px; bottom:{pad}px">{X.rich(sub)}</div>' if sub else ""))
        tx, ty, tw_, th_ = cx + pad - 14, cy + pad + 56 + (ch - 2 * pad - 60 - f.n * f.px * 1.18) / 2 - 10, min(cw - 2 * pad + 28, f.px * max(fit.width(l) for l in f.lines) + 28), f.n * f.px * 1.18 + 20
    X.css("fx-hp", CSS)
    S = f"#{cid}"
    card_html = f'<div class="hp-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">{body}</div>'
    _clip(X, cid, t, d, card_html, p)
    if host and not P:     # the host's body runs under the page footnote at the bottom left: give it a backing
        X.css(f"hp-ft-{cid}", f"#{cid}c .ft > div:first-child {{ background:var(--bg); padding:2px 10px; margin-left:-10px; border-radius:6px; }}")
    hsel = None
    if host:
        rect = f"inset:auto; left:{hx:.0f}px; top:{hy:.0f}px; width:{hs:.0f}px; height:{hs:.0f}px; transform-origin:50% 100%;"
        _, hsel = fit.media(X, cid, "hp", host, t, d, "hp-h", z=4, extra_style=rect)
        hfit = p.get("host_fit") or ("contain" if str(host).lower().endswith(".webm") else "cover")
        X.css(f"hp-hfit-{cid}", f"{hsel} video {{ object-fit:{hfit} !important; }}")
    # arrow from the host's shoulder toward the target, bubble above the head (overlay above the host)
    sx = (hx + hs * 0.70) if side == "left" else (hx + hs * 0.30)
    sy = hy + hs * (0.30 if not P else 0.22)
    ex = (tx - 18) if side == "left" else (tx + tw_ + 18)
    ey = ty + th_ / 2
    if P: ex, ey = tx + tw_ / 2, ty + th_ + 18
    mx, my = (sx + ex) / 2, min(sy, ey) - (220 if not P else 90)
    import math
    ang = math.atan2(ey - my, ex - mx)
    hl = 30
    h1 = (ex - hl * math.cos(ang - 0.5), ey - hl * math.sin(ang - 0.5)); h2 = (ex - hl * math.cos(ang + 0.5), ey - hl * math.sin(ang + 0.5))
    arrow = (f'<svg class="hp-arrow" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path class="sh" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" d="M{sx:.0f},{sy:.0f} Q{mx:.0f},{my:.0f} {ex:.0f},{ey:.0f}"/>'
             f'<path class="hd" d="M{h1[0]:.0f},{h1[1]:.0f} L{ex:.0f},{ey:.0f} L{h2[0]:.0f},{h2[1]:.0f}" opacity="0"/></svg>')
    ring = f'<div class="hp-ring" style="left:{tx - 6:.0f}px; top:{ty - 6:.0f}px; width:{tw_ + 12:.0f}px; height:{th_ + 12:.0f}px"></div>'
    say = p.get("say", "")
    bub = ""
    if say:
        bw_ = W * (0.3 if not P else 0.42)
        bf = fit.fit_text(str(say), bw_, 140, 42 if not P else 44, 26, lh=1.25, max_lines=2)
        bh_ = bf.n * bf.px * 1.25 + 40
        if P:     # beside the host, clear of the card above
            bx_ = (hx + hs * 0.86) if side == "left" else (hx + hs * 0.14 - bw_)
            by_ = hy + hs * 0.18
        else:     # above the head
            bx_ = (hx + hs * 0.45) if side == "left" else (hx + hs * 0.55 - bw_)
            by_ = max(130, hy - bh_ - 10)
        bub = f'<div class="hp-bub{" r" if side != "left" else ""}" style="left:{bx_:.0f}px; top:{by_:.0f}px; font-size:{bf.px}px"><b>{"<br>".join(X.rich(l) for l in bf.lines)}</b></div>'
        X.used_text.update(str(say))
    X.clip(f"{cid}o", t, d, arrow + ring + bub, "hp-over", 5, track=26)
    O = f"#{cid}o"
    X.tw(f'tl.from("{S} .hp-card", {{x:{80 if side == "left" else -80}, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{S} .hp-card > *", {{y:20, opacity:0, duration:0.45, ease:"expo.out", stagger:0.08}}, {t + 0.25:.3f});')
    if hsel:
        X.tw(f'tl.from("{hsel}", {{y:90, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
        lean = 3.5 if side == "left" else -3.5
        X.tw(f'tl.to("{hsel}", {{rotation:{lean}, x:{18 if side == "left" else -18}, duration:0.35, ease:"back.out(2)"}}, {tp - 0.1:.3f});')
        X.tw(f'tl.to("{hsel}", {{rotation:0, x:0, duration:0.6, ease:"sine.inOut"}}, {tp + 0.9:.3f});')
        X.tw(f'tl.to("{hsel}", {{y:-6, duration:0.8, ease:"sine.inOut", yoyo:true, repeat:{max(0, int((t + d - tp - 1.5) / 0.8) - 1)}}}, {tp + 1.5:.3f});')
    X.tw(f'tl.to("{O} .hp-arrow .sh", {{strokeDashoffset:0, duration:0.45, ease:"power2.inOut"}}, {tp:.3f});')
    X.tw(f'tl.to("{O} .hp-arrow .hd", {{opacity:1, duration:0.1}}, {tp + 0.42:.3f});')
    X.sfx(tp, "whoosh_soft")
    X.tw(f'tl.fromTo("{O} .hp-ring", {{opacity:0, scale:1.15}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)", immediateRender:false}}, {tp + 0.45:.3f});')
    X.tw(f'tl.to("{O} .hp-ring", {{scale:1.04, duration:0.5, ease:"sine.inOut", yoyo:true, repeat:{max(0, int((t + d - tp - 0.8) / 0.5) - 1)}}}, {tp + 0.8:.3f});')
    X.sfx(tp + 0.45, "hit")
    if kind == "number" and isinstance(card.get("value"), (int, float)):
        v = float(card["value"])
        dec = 1 if v != int(v) and abs(v) < 1e4 else 0
        if abs(v) >= 1e4:
            C.counter(X, f"{S} .hp-n", tp + 0.45, 0, v, dur=0.9, fmt="zh")
        else:
            X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{S} .hp-n"); tl.to(o, {{v:{v}, duration:0.9, ease:"power3.out", onUpdate:()=>{{el.textContent=o.v.toFixed({dec});}}}}, {tp + 0.45:.3f});}})();')
    if bub:
        X.tw(f'tl.fromTo("{O} .hp-bub", {{opacity:0, scale:0.6, y:20}}, {{opacity:1, scale:1, y:0, duration:0.4, ease:"back.out(2)", transformOrigin:"{"0% 100%" if side == "left" else "100% 100%"}", immediateRender:false}}, {max(t + 0.3, tp - 0.5):.3f});')
        X.sfx(max(t + 0.3, tp - 0.5), "pop")
    X.tw(f'tl.fromTo("{S} .hp-card", {{scale:1}}, {{scale:1.03, duration:{max(0.2, t + d - tp):.2f}, ease:"none", immediateRender:false}}, {tp:.3f});')


FX = {"host_point": host_point}
