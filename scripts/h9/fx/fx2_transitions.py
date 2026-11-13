"""fx2 · four transitions: whip_carry · shape_match · paper_tear · paint_wipe. Written on the next beat like the
built-in ones: "tr": "paint_wipe". Each is an overlay clip around the cut at t (covers by t, uncovers after), a pure
function of timeline time; whip_carry also moves the two scenes it joins.

This module exports no effects (FX = {}); scripts/h9/fx.py's transition() dispatches the four ids to TRS below.
"""
import importlib.util
import math
import pathlib
import re
import sys

from h9 import fx as TRM

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]

Z = TRM.Z_TR
CSS = r"""
.tr2 { pointer-events:none; overflow:hidden; }
.tr2-chip { position:absolute; display:flex; align-items:center; justify-content:center; white-space:nowrap; font-family:var(--f-display); font-weight:900;
  background:var(--accent); color:var(--tr2-on, #111); border-radius:var(--tr2-r, 18px); box-shadow:0 30px 80px rgba(0,0,0,.35); }
.tr2-shape { position:absolute; inset:0; background:var(--accent); }
.tr2-half { position:absolute; inset:0; }
.tr2-half i { position:absolute; inset:0; display:block; }
.tr2-half .lip { background:#fffdf8; filter:drop-shadow(0 0 10px rgba(0,0,0,.35)); }
.tr2-half .face { background-color:var(--card, #fbfaf6); }
.tr2-svg { position:absolute; left:0; top:0; overflow:visible; }
"""


def _scenes(X, t):
    """(previous scene id, next scene id) around the cut at t, read from the clips built so far."""
    prev = nxt = None
    for el in X.els:
        m = re.match(r'<\w+ id="([^"]+)" class="clip ([^"]*)" data-start="([\d.]+)" data-duration="([\d.]+)"', el)
        if not m or "scene" not in m.group(2).split():
            continue
        st, du = float(m.group(3)), float(m.group(4))
        if abs(st + du - t) < 0.03:
            prev = m.group(1)
        if abs(st - t) < 0.03:
            nxt = m.group(1)
    return prev, nxt


def _movers(X, cid):
    """what to move for a scene: its .stage, plus the untimed stage the key-info / fx2 effects draw on (cid_scr)."""
    if not cid:
        return ""
    out = [f"#{cid} > .stage"]
    tag = f'id="{cid}_scr"'
    for el in X.els:
        if tag in el:
            out.append(f"#{cid}_scr")
            break
    return ", ".join(out)


def _beat(X, k=0):
    """the video.json beat being built (k=0) or the one before it (k=-1)."""
    beats = X.v.get("beats") or []
    i = int((getattr(X, "beat", None) or {}).get("i", 0)) - int((X.v.get("meta") or {}).get("beat_offset", 0)) + k
    if 0 <= i < len(beats):
        return beats[i]
    return {}


def _base(X):
    X.css("tr2", CSS)
    from h9.aefx import _contrast
    acc = X.S.get("tokens", {}).get("accent", "#e2321f")
    on = "#111111" if _contrast("#111111", acc) >= _contrast("#ffffff", acc) else "#ffffff"
    return f"--tr2-on:{on};"


# ------------------------------------------------------------------------------------------------ whip_carry
def whip_carry(X, t):
    """甩镜带物 Whip Carry: a whip-pan — both scenes smear sideways with a horizontal motion blur — while one element stays
    locked in frame and rides across the cut into the next beat: the stressed word of the outgoing line (or the next
    beat's "carry")."""
    sty = _base(X)
    prev, nxt = _scenes(X, t)
    nb = _beat(X, 0)
    pb = _beat(X, -1)
    carry = str(nb.get("carry") or "")
    if not carry:
        m = re.search(r"\*([^*]+)\*", str(pb.get("line") or ""))
        carry = m.group(1) if m else ""
    cid = X.uid("tr2w")
    P = X.portrait
    chip = ""
    if carry:
        px, ln = A.fit_px(carry, X.W * 0.8, 200, 110 if P else 96, 40, max_lines=1, lh=1.0)
        from h9 import fit as FT
        w = FT.width(ln[0]) * px + px * 1.0
        h = px * 1.55
        chip = f'<div class="tr2-chip" style="left:{(X.W - w) / 2:.0f}px; top:{X.H * 0.42 - h / 2:.0f}px; width:{w:.0f}px; height:{h:.0f}px; font-size:{px:.0f}px">{X.rich(ln[0])}</div>'
    filt = (f'<svg width="0" height="0" style="position:absolute"><filter id="WCb_{cid}" x="-30%" y="-5%" width="160%" height="110%">'
            f'<feGaussianBlur class="wcb" stdDeviation="0 0"/></filter></svg>')
    X.clip(cid, t - 0.32, 1.25, filt + chip, "tr2", Z, sty=sty)
    pm, nm = _movers(X, prev), _movers(X, nxt)
    sel = f"#{cid} .wcb"
    if pm:
        X.tw(f'tl.set("{pm}", {{filter:"url(#WCb_{cid})"}}, {t - 0.22:.3f});')
        X.tw(f'tl.to("{pm}", {{x:{-X.W * 0.55:.0f}, duration:0.22, ease:"power3.in"}}, {t - 0.22:.3f});')
    if nm:
        X.tw(f'tl.set("{nm}", {{filter:"url(#WCb_{cid})"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{nm}", {{x:{X.W * 0.55:.0f}}}, {{x:0, duration:0.34, ease:"power3.out", immediateRender:false}}, {t:.3f});')
        X.tw(f'tl.set("{nm}", {{filter:"none"}}, {t + 0.36:.3f});')
    X.tw(f'tl.fromTo("{sel}", {{attr:{{stdDeviation:"0 0"}}}}, {{attr:{{stdDeviation:"70 0"}}, duration:0.22, ease:"power3.in", immediateRender:false}}, {t - 0.22:.3f});')
    X.tw(f'tl.to("{sel}", {{attr:{{stdDeviation:"0 0"}}, duration:0.34, ease:"power3.out"}}, {t:.3f});')
    if chip:
        X.tw(f'tl.fromTo("#{cid} .tr2-chip", {{scale:0.5, opacity:0}}, {{scale:1, opacity:1, duration:0.2, ease:"back.out(2.4)", immediateRender:true}}, {t - 0.32:.3f});')
        X.tw(f'tl.to("#{cid} .tr2-chip", {{scale:1.06, duration:0.08, yoyo:true, repeat:1}}, {t - 0.04:.3f});')
        X.tw(f'tl.to("#{cid} .tr2-chip", {{y:{-X.H * 0.28:.0f}, scale:0.42, opacity:0, duration:0.45, ease:"power3.in"}}, {t + 0.42:.3f});')
    X.sfx(t - 0.2, "whoosh")


# ------------------------------------------------------------------------------------------------ shape_match
def _geo(v, dflt, W, H):
    """{x, y, w, h, r} as fractions of the frame (r: "50%" or px) → (left, top, width, height, radius css)."""
    if isinstance(v, dict) and ("9:16" in v or "16:9" in v):
        v = v.get("9:16" if H > W else "16:9")      # one geometry per aspect
    if not isinstance(v, dict):
        v = dflt
    x, y, w = float(v.get("x", dflt["x"])), float(v.get("y", dflt["y"])), float(v.get("w", dflt["w"]))
    hv = v.get("h", dflt.get("h"))
    r = v.get("r", dflt["r"])
    w_px = w * W
    h_px = float(hv) * H if hv is not None else w_px
    if v.get("shape") == "circle" or r == "50%":
        side = min(w_px, h_px)
        h_px = w_px = side
        rr = side / 2
    else:
        rr = float(r)
    return x * W, y * H, w_px, h_px, rr


def shape_match(X, t):
    """形状匹配 Shape Match: a shape that belongs to beat A (by default a disc) swells to fill the frame across the cut and
    then settles into the matching shape of beat B (by default a wide card), handing over to the real one underneath.
    Beat B may name both: "tr_from" / "tr_to" = {x, y, w, h, r} in frame fractions (r in px or "50%")."""
    sty = _base(X)
    nb = _beat(X, 0)
    W, H = X.W, X.H
    P = X.portrait
    d_from = {"x": 0.25 if P else 0.36, "y": 0.3 if P else 0.27, "w": 0.5 if P else 0.28, "h": None, "r": "50%", "shape": "circle"}
    d_to = {"x": 0.06 if P else 0.08, "y": 0.2 if P else 0.18, "w": 0.88 if P else 0.84, "h": 0.42 if P else 0.6, "r": 28}
    f = _geo(nb.get("tr_from"), d_from, W, H)
    g = _geo(nb.get("tr_to"), d_to, W, H)
    cid = X.uid("tr2s")
    X.clip(cid, t - 0.48, 1.25, '<i class="tr2-shape"></i>', "tr2", Z, sty=sty)
    e = f"#{cid} .tr2-shape"

    def ins(q):
        x, y, w, h, r = q
        return f"inset({y:.0f}px {W - x - w:.0f}px {H - y - h:.0f}px {x:.0f}px round {r:.0f}px)"
    X.tw(f'tl.set("{e}", {{clipPath:"{ins(f)}"}}, {t - 0.48:.3f});')
    X.tw(f'tl.fromTo("{e}", {{scale:0, transformOrigin:"{f[0] + f[2] / 2:.0f}px {f[1] + f[3] / 2:.0f}px"}}, {{scale:1, duration:0.22, ease:"back.out(1.8)", immediateRender:true}}, {t - 0.48:.3f});')
    X.tw(f'tl.to("{e}", {{clipPath:"inset(-2px -2px -2px -2px round 0px)", duration:0.24, ease:"power3.in"}}, {t - 0.24:.3f});')
    X.tw(f'tl.to("{e}", {{clipPath:"{ins(g)}", duration:0.42, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.tw(f'tl.to("{e}", {{opacity:0, duration:0.3, ease:"power1.in"}}, {t + 0.45:.3f});')
    X.sfx(t - 0.24, "whoosh_soft")
    X.sfx(t + 0.02, "pop", 0.4)


# ------------------------------------------------------------------------------------------------ paper_tear
def paper_tear(X, t):
    """撕纸 Paper Tear: two sheets of paper close over the cut from opposite corners, meeting along a rough diagonal; then
    the paper rips along that seam — torn white fibre lips showing — and the halves fly apart, revealing the next beat."""
    sty = _base(X)
    W, H = X.W, X.H
    R = X.rand
    y_l, y_r = (0.62, 0.40) if X.portrait else (0.70, 0.30)
    n = 70
    pts = []
    ph = R.uniform(0, 6.3)
    for i in range(n + 1):
        f = i / n
        x = -0.05 + 1.1 * f
        wave = 0.02 * math.sin(f * 7.0 + ph) + 0.01 * math.sin(f * 17.0 + ph * 2)
        y = y_l + (y_r - y_l) * f + wave + R.uniform(-0.004, 0.004)
        pts.append((x * 100, y * 100))
    from h9.aefx import _lum
    tok = X.S.get("tokens", {})
    paper = None
    best = -1.0
    for key in ("card", "bg", "fg", "paper"):
        c = tok.get(key)
        lv = _lum(c) if c else None
        if lv is not None and lv > best:
            best, paper = lv, c                    # paper is the lightest colour the style owns
    paper = paper or "#fbfaf6"

    def poly(shift, top):
        ps = [f"{x:.2f}% calc({y:.2f}% + {shift}px)" for x, y in pts]
        if top:
            ps += ["110% -10%", "-10% -10%"]
        else:
            ps += ["110% 110%", "-10% 110%"]
        return "polygon(" + ", ".join(ps) + ")"
    noise = TRM.noise_svg(0.7, 3, 0.22, seed=11, tint="0.35 0.3 0.25")
    halves = ""
    for key, top, lip in (("a", True, 9), ("b", False, -9)):
        halves += (f'<div class="tr2-half h{key}"><i class="lip" style="clip-path:{poly(lip, top)}"></i>'
                   f'<i class="face" style="clip-path:{poly(0, top)}; background-color:{paper}; background-image:{noise}; background-size:320px"></i></div>')
    cid = X.uid("tr2p")
    X.clip(cid, t - 0.32, 1.0, halves, "tr2", Z, sty=sty)
    ha, hb = f"#{cid} .ha", f"#{cid} .hb"
    X.tw(f'tl.fromTo("{ha}", {{xPercent:-60, yPercent:-70, rotation:-4}}, {{xPercent:0, yPercent:0, rotation:0, duration:0.3, ease:"power3.in", immediateRender:true}}, {t - 0.32:.3f});')
    X.tw(f'tl.fromTo("{hb}", {{xPercent:60, yPercent:70, rotation:4}}, {{xPercent:0, yPercent:0, rotation:0, duration:0.3, ease:"power3.in", immediateRender:true}}, {t - 0.32:.3f});')
    X.tw(f'tl.to("{ha}", {{keyframes:[{{x:-6, y:-4, rotation:-0.6, duration:0.06, ease:"none"}}, {{xPercent:-35, yPercent:-80, rotation:-9, duration:0.5, ease:"power2.in"}}]}}, {t + 0.04:.3f});')
    X.tw(f'tl.to("{hb}", {{keyframes:[{{x:6, y:4, rotation:0.6, duration:0.06, ease:"none"}}, {{xPercent:35, yPercent:80, rotation:8, duration:0.5, ease:"power2.in"}}]}}, {t + 0.04:.3f});')
    X.sfx(t - 0.3, "paper")
    X.sfx(t + 0.04, "paper", 0.8)


# ------------------------------------------------------------------------------------------------ paint_wipe
def paint_wipe(X, t):
    """三笔刷屏 Paint Wipe: three broad paint strokes with ragged bristle edges sweep across and cover the frame by the cut;
    then each stroke's tail runs out after its head, uncovering the next beat. Colours: the style's accent and text colour."""
    sty = _base(X)
    W, H = X.W, X.H
    R = X.rand
    P = X.portrait
    band = H / 3
    sw_ = band * 1.32
    cols = ["var(--accent)", "var(--fg)", "color-mix(in srgb, var(--accent) 70%, var(--fg))"]
    paths = ""
    for i in range(3):
        yc = band * (i + 0.5)
        tilt = (band * 0.16) * (1 if i % 2 == 0 else -1)
        x0, x1 = -sw_ * 0.6, W + sw_ * 0.6
        if i % 2 == 1:
            x0, x1 = x1, x0
        mid = (x0 + x1) / 2
        dpath = f"M {x0:.0f} {yc - tilt:.0f} Q {mid:.0f} {yc + R.uniform(-band * 0.12, band * 0.12):.0f} {x1:.0f} {yc + tilt:.0f}"
        paths += (f'<path class="pw pw{i}" d="{dpath}" fill="none" stroke="{cols[i]}" stroke-width="{sw_:.0f}" stroke-linecap="butt" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1"/>'
                  f'<path class="pw pw{i}" d="{dpath}" fill="none" stroke="color-mix(in srgb, {cols[i]} 70%, #000)" stroke-opacity=".35" stroke-width="{sw_ * 0.86:.0f}" '
                  f'stroke-linecap="butt" pathLength="1" stroke-dasharray="1 1.2" stroke-dashoffset="1" filter="url(#PWs_CID)"/>')
    cid = X.uid("tr2b")
    paths = paths.replace("CID", cid)
    svg = (f'<svg class="tr2-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>'
           f'<filter id="PWr_{cid}" x="-10%" y="-20%" width="120%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.9 0.012" numOctaves="2" seed="{R.randint(1, 90)}" result="n"/>'
           f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{band * 0.22:.0f}" xChannelSelector="R" yChannelSelector="G"/></filter>'
           f'<filter id="PWs_{cid}"><feTurbulence type="fractalNoise" baseFrequency="0.004 0.18" numOctaves="2" seed="{R.randint(1, 90)}" result="n"/>'
           f'<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3 1.6" result="m"/><feComposite in="SourceGraphic" in2="m" operator="in"/></filter></defs>'
           f'<g filter="url(#PWr_{cid})">{paths}</g></svg>')
    X.clip(cid, t - 0.5, 1.2, svg, "tr2", Z, sty=sty)
    for i in range(3):
        a = t - 0.46 + i * 0.09
        X.tw(f'tl.fromTo("#{cid} .pw{i}", {{attr:{{"stroke-dashoffset":1}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:{0.42 - i * 0.07:.2f}, ease:"power2.inOut", immediateRender:true}}, {a:.3f});')
        X.tw(f'tl.to("#{cid} .pw{i}", {{attr:{{"stroke-dashoffset":-1.05}}, duration:0.44, ease:"power2.in"}}, {t + 0.06 + i * 0.08:.3f});')
        X.sfx(a, "brush", 0.6)


TRS = {"whip_carry": whip_carry, "shape_match": shape_match, "paper_tear": paper_tear, "paint_wipe": paint_wipe}   # dispatched by fx.transition()
FX = {}
