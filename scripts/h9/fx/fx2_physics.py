"""fx2 · physics: drop_stack · pour_fill · topple · magnet_sort — things with weight. Every motion here has a cause
(gravity, a push, a pour, a magnet) and an effect you can count. Layout: text above the caption band, the scene runs
on to the bottom edge. Colours / fonts only from the style tokens (re-skins in every style).
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
.f2 .ds-u { position:absolute; border-radius:var(--k-rs); display:flex; align-items:center; justify-content:center; overflow:hidden; white-space:nowrap;
  font-family:var(--f-body); font-weight:800; color:var(--bg); will-change:transform; }
.f2 .ds-u.a { background:color-mix(in srgb, var(--fg) 88%, var(--bg)); } .f2 .ds-u.b { background:color-mix(in srgb, var(--fg) 70%, var(--bg)); }
.f2 .ds-u.top { background:var(--accent); color:var(--k-on); }
.f2 .ds-ghost { position:absolute; border:3px dashed color-mix(in srgb, var(--fg) 34%, transparent); border-radius:var(--k-rs); }
.f2 .ds-tick { position:absolute; height:3px; background:color-mix(in srgb, var(--fg) 45%, transparent); }
.f2 .ds-tl { position:absolute; font:700 26px var(--f-mono, monospace); color:var(--muted); white-space:nowrap; transform:translateY(-50%); }
.f2 .ds-cnt { position:absolute; text-align:left; }
.f2 .ds-cnt .f2-num { display:block; color:var(--fg); transform-origin:0 80%; }
.f2 .ds-cnt .u { display:block; font:800 44px var(--f-body); color:var(--muted); margin-top:4px; white-space:nowrap; }
.f2 .ds-tk { position:absolute; font:800 44px var(--f-body); color:var(--fg); white-space:nowrap; opacity:0; visibility:hidden; }
.f2 .pf-svg { position:absolute; left:0; top:0; overflow:visible; }
.f2 .pf-num { position:absolute; text-align:center; }
.f2 .pf-num .f2-num { display:block; }
.f2 .pf-cap { position:absolute; font:700 32px var(--f-body); color:var(--muted); white-space:nowrap; text-align:center; }
.f2 .tp-sl { position:absolute; border-radius:var(--k-rs); display:flex; align-items:center; justify-content:center; overflow:hidden; will-change:transform; }
.f2 .tp-sl.a { background:var(--fg); color:var(--bg); } .f2 .tp-sl.b { background:var(--accent); color:var(--k-on); }
.f2 .tp-sl span { display:block; white-space:nowrap; font-family:var(--f-display); font-weight:900; line-height:1; transform:rotate(-90deg); }
.f2 .tp-mir { position:absolute; left:0; top:0; width:100%; height:100%; opacity:.26; }
.f2 .tp-plinth { position:absolute; left:0; right:0; bottom:0; border-top:6px solid var(--fg); overflow:hidden;
  background:repeating-linear-gradient(0deg, transparent 0 70px, color-mix(in srgb, var(--fg) 14%, transparent) 70px 73px), color-mix(in srgb, var(--fg) 9%, var(--bg)); }
.f2 .tp-ball { position:absolute; border-radius:50%; background:var(--accent); box-shadow:inset -10px -12px 0 color-mix(in srgb, #000 22%, transparent); }
.f2 .tp-hd { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.1; color:var(--fg); }
.f2 .tp-hd .sl { display:block; white-space:nowrap; }
.f2 .tp-dust { position:absolute; width:18px; height:18px; border-radius:50%; background:color-mix(in srgb, var(--fg) 40%, transparent); opacity:0; }
.f2 .ms-chip { position:absolute; left:0; top:0; border-radius:50%; display:flex; align-items:center; justify-content:center; font-family:var(--f-body);
  font-weight:900; background:color-mix(in srgb, var(--fg) 34%, var(--bg)); color:var(--fg); will-change:transform; box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--fg) 50%, transparent); }
.f2 .ms-lab { position:absolute; white-space:nowrap; font:900 52px var(--f-display); color:var(--fg); }
.f2 .ms-tal { position:absolute; white-space:nowrap; }
.f2 .ms-mag { position:absolute; overflow:visible; }
.f2 .ms-ring { position:absolute; border-radius:50%; border:4px solid var(--accent); opacity:0; }
"""


def _css(X):
    X.css("fx-f2-phys", CSS)


def _nice_per(v, cap):
    """the value one unit stands for, from 1 / 2 / 5 × 10ⁿ, so that v needs at most `cap` units."""
    if v <= cap:
        return 1.0
    k = 0
    while True:
        for m in (1, 2, 5):
            per = m * (10 ** k)
            if v / per <= cap:
                return float(per)
        k += 1


# ------------------------------------------------------------------------------------------------ drop_stack
def drop_stack(X, cid, t, d, p):
    """掉落堆叠 Drop Stack: units fall with gravity, bounce once and stack into a column whose height IS the number; a counter
    ticks on every landing and names the unit that just landed (items, synced to the narration). A dashed outline shows
    the final height from the first frame, so the eye knows where the count is going."""
    F = "drop_stack"
    val = A.number(F, p, "value")
    items = A.texts(F, p, "items", 0, 60)
    A.need(F, t, p, [] if val is not None else ["value (the number the column counts to)"])
    if val is None:
        val = 12.0
    if val <= 0:
        raise SystemExit(f"{F}: value must be > 0")
    per = A.number(F, p, "per", None, 1e-9)
    if per is None:
        per = _nice_per(val, 40)
    n = int(math.ceil(val / per - 1e-9))
    if n > 60:
        raise SystemExit(f"{F}: {n} units is too many to read — set `per` (one unit = per) so there are at most 60")
    if items and len(items) > n:
        raise SystemExit(f"{F}: {len(items)} items for {n} units — give at most one item per unit")
    dec = A.decimals(p.get("value"))
    unit = str(p.get("unit") or "")
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    col_w = 424 if P else 520
    colx = G["x0"] if P else G["x0"] + 30
    floor = X.H - 6                          # the stack grows from the bottom edge
    col_top = G["y0"] + hh + (10 if P else 4)
    slot = min(132.0 if P else 96.0, (floor - col_top) / n)
    gap = max(3.0, min(8.0, slot * 0.12))
    bh = slot - gap
    top_final = floor - n * slot
    # counter (right of the column)
    cx0 = colx + col_w + (44 if P else 120)
    cw = (X.W - 24 - cx0) if P else (G["x1"] - cx0)
    ctop = col_top if P else max(G["y0"] + hh, (G["y0"] + G["y1"]) / 2 - 300)
    vs = A.fmt(val, dec)
    npx, _ = A.fit_px(vs, cw, 520, 470 if P else 440, 60, max_lines=1, lh=1.0)
    X.used_text.update("0123456789.," + vs)
    html = [head, f'<div class="f2-ground" style="top:{floor:.0f}px"></div>']
    html.append(f'<div class="ds-ghost" style="left:{colx - 6:.0f}px; top:{top_final - 6:.0f}px; width:{col_w + 12:.0f}px; height:{floor - top_final + 6:.0f}px"></div>')
    step = 5 if n > 12 else 1
    if n > 40:
        step = 10
    for k in range(step, n + 1, step):
        y = floor - k * slot
        html.append(f'<i class="ds-tick" style="left:{colx + col_w + 8:.0f}px; top:{y:.0f}px; width:{18 if P else 22}px"></i>')
        if not P:
            html.append(f'<div class="ds-tl" style="left:{colx + col_w + 38:.0f}px; top:{y:.0f}px">{X.rich(A.fmt(min(k * per, val), dec))}</div>')
    for k in range(n):
        y = floor - (k + 1) * slot + gap / 2
        cls = "a" if k % 2 == 0 else "b"
        if k == n - 1:
            cls = "top"
        lab = ""
        if k < len(items) and bh >= 30 and ((not P) or y + bh < G["y1"] - 4):
            lpx, ll = A.fit_px(A.strip(items[k]["text"]), col_w - 40, bh * 0.9, min(44, bh * 0.58), 18, max_lines=1)
            lab = f'<span style="font-size:{lpx:.0f}px">{X.rich(ll[0])}</span>'
        html.append(f'<div class="ds-u {cls} u{k}" style="left:{colx:.0f}px; top:{y:.0f}px; width:{col_w}px; height:{bh:.1f}px">{lab}</div>')
    html.append(f'<div class="ds-cnt" style="left:{cx0:.0f}px; top:{ctop:.0f}px; width:{cw:.0f}px"><span class="f2-num" style="font-size:{npx:.0f}px">0</span>'
                f'<span class="u">{X.rich(unit)}</span></div>')
    tky = ctop + npx * 1.0 + 76
    for k in range(len(items)):
        tpx, tl_ = A.fit_px(A.strip(items[k]["text"]), cw, 80, 60, 30, max_lines=1)
        html.append(f'<div class="ds-tk tk{k}" style="left:{cx0:.0f}px; top:{tky:.0f}px; font-size:{tpx:.0f}px">{X.rich(tl_[0])}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    # landing times: spoken items first, else a rain that starts slow and speeds up
    a = t + min(0.55, d * 0.15)
    b = t + max(d * 0.78, min(d - 0.8, a + 0.6))
    auto = []
    for k in range(n):
        x = k / (n - 1) if n > 1 else 0.0
        auto.append(a + (b - a) * (0.45 * x + 0.55 * (1 - (1 - x) ** 2)))
    lands = list(auto)
    if items:
        cs = A.cues(X, p, items, t, d, start=0.15, end=0.78, gap=0.08)
        for k in range(len(items)):
            lands[k] = cs[k]
        for k in range(1, n):
            if lands[k] < lands[k - 1] + 0.06:
                lands[k] = lands[k - 1] + 0.06
    data = []
    for k in range(n):
        y = floor - (k + 1) * slot + gap / 2
        hgt = y + bh + 80
        fd = A.fall_time(hgt)
        hop = min(46.0, slot * 0.55)
        data.append([round(hgt), round(lands[k], 3), round(fd, 3), round(hop, 1)])
    X.tw(f'(()=>{{const S="{s}", D={A.js(data)}; D.forEach((b,i)=>{{const e=S+" .u"+i;'
         f'tl.set(e,{{y:-b[0]}},{t:.3f});'
         f'tl.to(e,{{y:0,duration:b[2],ease:"power2.in"}},b[1]-b[2]);'
         f'tl.to(e,{{scaleY:.8,scaleX:1.05,transformOrigin:"50% 100%",duration:.05,ease:"power2.out"}},b[1]);'
         f'tl.to(e,{{y:-b[3],scaleY:1,scaleX:1,duration:.11,ease:"power2.out"}},b[1]+.05);'
         f'tl.to(e,{{y:0,duration:.11,ease:"power2.in"}},b[1]+.16);'
         f'tl.to(e,{{scaleY:.94,duration:.04,ease:"none"}},b[1]+.27);'
         f'tl.to(e,{{scaleY:1,duration:.14,ease:"power2.out"}},b[1]+.31);}});}})();')
    # the counter ticks on each landing (pure function of time: one short tween per landing)
    vals = []
    for k in range(n):
        vals.append(round(min((k + 1) * per, val), 6))
    X.tw(f'(()=>{{const el=document.querySelector("{s} .ds-cnt .f2-num"); if(!el) return; const o={{v:0}}, L={A.js([round(x, 3) for x in lands])}, V={A.js(vals)};'
         f'const w=()=>{{el.textContent=o.v.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}});}};'
         f'L.forEach((at,i)=>{{tl.fromTo(o,{{v:i?V[i-1]:0}},{{v:V[i],duration:.05,ease:"none",immediateRender:false,onUpdate:w}},at);'
         f'tl.fromTo(el,{{scale:1.1}},{{scale:1,duration:.18,ease:"power2.out",immediateRender:false}},at);}});}})();')
    for k in range(len(items)):
        X.tw(f'tl.fromTo("{s} .tk{k}", {{autoAlpha:0, y:16}}, {{autoAlpha:1, y:0, duration:0.12, immediateRender:false}}, {lands[k]:.3f});')
        if k + 1 < len(items):
            X.tw(f'tl.to("{s} .tk{k}", {{autoAlpha:0, duration:0.05}}, {lands[k + 1] - 0.02:.3f});')
    last = lands[-1]
    C = A.pal(X, p)
    X.tw(f'tl.to("{s} .ds-cnt .f2-num", {{color:"{C['accent']}", duration:0.15}}, {last:.3f});')
    X.tw(f'tl.to("{s} .ds-ghost", {{opacity:0, duration:0.3}}, {last:.3f});')
    A.shake(X, f"{s} .f2-body", last + 0.02, amp=12, n=6)
    every = max(1, n // 10)
    for k in range(0, n, every):
        X.sfx(lands[k], "tick", 0.35)
    X.sfx(last, "hit")


# ------------------------------------------------------------------------------------------------ pour_fill
def pour_fill(X, cid, t, d, p):
    """倒入液面 Pour Fill: a stream pours into a container outline and the level rises to the percentage; the surface sloshes
    and settles (or grains heap up and slump flat). From `from` to `value`, with a dashed mark where it started. Over
    100 % it overflows: the liquid runs down the outside and pools on the floor."""
    F = "pour_fill"
    val = A.number(F, p, "value")
    A.need(F, t, p, [] if val is not None else ["value (the percentage to fill to)"])
    if val is None:
        val = 50.0
    if val < 0:
        raise SystemExit(f"{F}: value must be ≥ 0")
    if val > 400:
        raise SystemExit(f"{F}: value {val} is too large to pour; use a different effect for ratios above 400 %")
    frm = A.number(F, p, "from", 0.0, 0.0, min(val, 100.0))
    mat = A.choice(F, p, "material", ("liquid", "grains"), "liquid")
    dec = max(A.decimals(p.get("value")), A.decimals(p.get("from")) if p.get("from") is not None else 0)
    unit = str(p.get("unit") if p.get("unit") is not None else "%")
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"], align="center" if P else "left")
    if P:
        vw = 760.0
        xl = G["cx"] - vw / 2
        vt = G["y0"] + hh + 70
    else:
        vw = 560.0
        xl = G["x0"] + 80
        vt = G["y0"] + hh + 50
    xr = xl + vw
    vb = G["floor"] - 8
    rad = 90.0 if P else 70.0
    pad = 34.0
    num_w = (vw - 80) if P else (G["x1"] - xr - 100)
    vs = A.fmt(val, dec) + unit
    npx, _ = A.fit_px(vs, num_w, 400, 230 if P else 260, 60, max_lines=1, lh=1.0)
    X.used_text.update("0123456789.,%" + vs)
    cap = str(p.get("caption") or "")
    inner_path = (f"M {xl:.0f} {vt:.0f} L {xl:.0f} {vb - rad:.0f} Q {xl:.0f} {vb:.0f} {xl + rad:.0f} {vb:.0f} L {xr - rad:.0f} {vb:.0f} "
                  f"Q {xr:.0f} {vb:.0f} {xr:.0f} {vb - rad:.0f} L {xr:.0f} {vt:.0f} Z")
    outline = (f"M {xl - 26:.0f} {vt - 4:.0f} L {xl:.0f} {vt:.0f} L {xl:.0f} {vb - rad:.0f} Q {xl:.0f} {vb:.0f} {xl + rad:.0f} {vb:.0f} L {xr - rad:.0f} {vb:.0f} "
               f"Q {xr:.0f} {vb:.0f} {xr:.0f} {vb - rad:.0f} L {xr:.0f} {vt:.0f} L {xr + 26:.0f} {vt - 4:.0f}")
    fill = "var(--accent)"
    pat = ""
    if mat == "grains":
        pat = ('<pattern id="PFG" width="22" height="20" patternUnits="userSpaceOnUse"><rect width="22" height="20" fill="var(--accent)"/>'
               '<circle cx="5" cy="5" r="4.2" fill="color-mix(in srgb, var(--accent) 70%, var(--fg))"/><circle cx="16" cy="14" r="4.6" fill="color-mix(in srgb, var(--accent) 78%, var(--bg))"/>'
               '<circle cx="15" cy="3" r="2.4" fill="color-mix(in srgb, var(--accent) 60%, var(--bg))"/></pattern>')
        fill = "url(#PFG)"
    lvl_y = lambda v: vb - (vb - vt - pad) * min(v, 100.0) / 100.0
    ticks = ""
    for q in (25, 50, 75, 100):
        y = lvl_y(q)
        ticks += f'<line x1="{xr - 40:.0f}" y1="{y:.0f}" x2="{xr - 6:.0f}" y2="{y:.0f}" stroke="var(--fg)" stroke-opacity=".5" stroke-width="4"/>'
        if (not P) or y < G["y1"] - 30:
            ticks += f'<text x="{xr - 52:.0f}" y="{y + 9:.0f}" text-anchor="end" fill="var(--muted)" style="font:700 26px var(--f-mono, monospace)">{q}%</text>'
    from_line = ""
    if frm > 0:
        yf = lvl_y(frm)
        from_line = f'<line class="pf-from" x1="{xl + 8:.0f}" y1="{yf:.0f}" x2="{xr - 8:.0f}" y2="{yf:.0f}" stroke="var(--fg)" stroke-width="5" stroke-dasharray="18 12"/>'
    svg = (f'<svg class="pf-svg" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}"><defs><clipPath id="PFC_{cid}"><path d="{inner_path}"/></clipPath>{pat}</defs>'
           f'<ellipse cx="{(xl + xr) / 2:.0f}" cy="{vb + 14:.0f}" rx="{vw * 0.56:.0f}" ry="20" fill="color-mix(in srgb, var(--fg) 16%, transparent)"/>'
           f'<path d="{inner_path}" fill="color-mix(in srgb, var(--fg) 6%, var(--bg))"/>'
           f'<g clip-path="url(#PFC_{cid})"><path class="pf-liq" d="" fill="{fill}"/><path class="pf-hi" d="" fill="none" stroke="color-mix(in srgb, var(--bg) 40%, var(--accent))" stroke-width="6"/></g>'
           f'<rect class="pf-str" x="0" y="0" width="0" height="0" fill="{fill}"/>'
           f'<path class="pf-sl" d="" fill="var(--accent)"/><path class="pf-sr" d="" fill="var(--accent)"/><ellipse class="pf-pool" cx="{(xl + xr) / 2:.0f}" cy="{vb + 12:.0f}" rx="0" ry="0" fill="var(--accent)"/>'
           + "".join(f'<circle class="pf-bub" cx="{xl + vw * (0.15 + 0.7 * ((i * 37) % 10) / 10):.0f}" cy="{vb - 30:.0f}" r="{6 + (i % 3) * 4}" fill="color-mix(in srgb, var(--bg) 35%, transparent)" clip-path="url(#PFC_{cid})" opacity="0"/>' for i in range(8) if mat == "liquid") +
           f'{from_line}{ticks}<path d="{outline}" fill="none" stroke="var(--fg)" stroke-width="9" stroke-linejoin="round" stroke-linecap="round"/></svg>')
    if P:
        nx, nw = xl + 40, vw - 80
    else:
        nx, nw = xr + 70, G["x1"] - xr - 70
    html = [f'<div class="f2-ground" style="top:{vb + 8:.0f}px; border-top-width:0; background:color-mix(in srgb, var(--fg) 7%, var(--bg))"></div>', svg, head,
            f'<div class="pf-num" style="left:{nx:.0f}px; width:{nw:.0f}px; top:0px"><span class="f2-num" style="font-size:{npx:.0f}px; color:var(--fg)"><b class="v" style="font-weight:inherit">{A.fmt(frm, dec)}</b>{X.rich(unit)}</span></div>']
    if cap:
        cpx, cl = A.fit_px(cap, nw, 50, 34, 24, max_lines=1)
        html.append(f'<div class="pf-cap" style="left:{nx:.0f}px; width:{nw:.0f}px; top:0px; font-size:{cpx:.0f}px">{X.rich(cl[0])}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    t0 = K.U.when(X, p.get("at"), t, t + min(0.45, d * 0.12))
    dur = max(1.1, min(2.6, 1.0 + 0.016 * (val - frm)))
    if t0 + dur > t + d - 1.0:
        dur = max(0.8, t + d - 1.0 - t0)
    sx = (xl + xr) / 2 - vw * 0.18
    num_top_cap = (G["y1"] - npx * 1.05 - (56 if cap else 0)) if P else 1e9
    X.tw(f'(()=>{{const R=document.querySelector("{s}"); if(!R) return; const q=c=>R.querySelector(c); const liq=q(".pf-liq"), hi=q(".pf-hi"), st=q(".pf-str"), sl=q(".pf-sl"), sr=q(".pf-sr"), pool=q(".pf-pool"), num=q(".pf-num"), nn=q(".pf-num .v"), cap=q(".pf-cap");'
         f'const xl={xl:.1f}, xr={xr:.1f}, vt={vt:.1f}, vb={vb:.1f}, pad={pad}, H={X.H}, top0=0, sx={sx:.1f}, P={1 if P else 0}, grains={1 if mat == "grains" else 0}, val={val}, frm={frm}, npx={npx:.1f}, ncap={num_top_cap:.1f};'
         f'const V={{lvl:{frm}, amp:0, ph:0, sw:0}};'
         f'const draw=()=>{{const lv=Math.min(V.lvl,100), y=vb-(vb-vt-pad)*lv/100, hw=(xr-xl)/2, cx=(xl+xr)/2; let d="M "+(xl-30)+" "+(vb+40); let h="";'
         f'for(let x=xl-30;x<=xr+30;x+=12){{const u=(x-cx)/hw; let yy;'
         f'if(grains){{yy=y-V.amp*Math.max(0,1-Math.pow((x-sx)/(hw*1.25),2))+2.5*Math.sin(x*.37);}}'
         f'else{{yy=y+V.amp*Math.cos(V.ph*7.2)*u+V.amp*.28*Math.sin(x/38+V.ph*9)+ (V.sw>0?4*Math.sin(x/17-V.ph*22):0);}}'
         f'd+=" L "+x.toFixed(1)+" "+yy.toFixed(1); h+=(h?" L ":"M ")+x.toFixed(1)+" "+yy.toFixed(1);}}'
         f'd+=" L "+(xr+30)+" "+(vb+40)+" Z"; liq.setAttribute("d",d); hi.setAttribute("d",grains?"":h);'
         f'st.setAttribute("x",(sx-V.sw/2).toFixed(1)); st.setAttribute("y",top0); st.setAttribute("width",V.sw.toFixed(1)); st.setAttribute("height",Math.max(0,y-top0).toFixed(1));'
         f'const ov=val>100?Math.max(0,Math.min(1,(V.lvl-100)/(val-100))):0;'
         f'const run=(vb-vt)*Math.min(1,ov*2.2), w=18*Math.min(1,ov*4);'
         f'sl.setAttribute("d",ov>0?`M ${{xl-26}} ${{vt-6}} q -16 6 -14 22 L ${{xl-12-w}} ${{vt+run}} L ${{xl-12+w*.3}} ${{vt+run}} L ${{xl+2}} ${{vt}} Z`:"");'
         f'sr.setAttribute("d",ov>0?`M ${{xr+26}} ${{vt-6}} q 16 6 14 22 L ${{xr+12+w}} ${{vt+run}} L ${{xr+12-w*.3}} ${{vt+run}} L ${{xr-2}} ${{vt}} Z`:"");'
         f'pool.setAttribute("rx",(ov>0.45?(xr-xl)*(0.55+0.5*(ov-0.45)):0).toFixed(1)); pool.setAttribute("ry",(ov>0.45?16:0));'
         f'nn.textContent=V.lvl.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}});'
         f'let ny; if(P){{ny=y-npx*1.08-30-(cap?56:0); if(ny<vt+16) ny=vt+16; if(ny>ncap) ny=ncap;}} else {{ny=Math.min(y-npx*0.55, vb-npx*1.1); if(ny<vt-40) ny=vt-40;}}'
         f'num.style.top=ny.toFixed(1)+"px"; if(cap) cap.style.top=(ny+npx*1.06).toFixed(1)+"px";}};'
         f'draw();'
         f'tl.fromTo(V,{{ph:0}},{{ph:{d:.2f},duration:{d:.2f},ease:"none",immediateRender:false,onUpdate:draw}},{t:.3f});'
         f'tl.fromTo(V,{{sw:0}},{{sw:34,duration:.22,ease:"power2.out",immediateRender:false,onUpdate:draw}},{t0 - 0.22:.3f});'
         f'tl.fromTo(V,{{lvl:{frm}}},{{lvl:{val},duration:{dur:.2f},ease:"power1.inOut",immediateRender:false,onUpdate:draw}},{t0:.3f});'
         f'tl.fromTo(V,{{amp:0}},{{amp:grains?60:16,duration:.4,ease:"power2.out",immediateRender:false,onUpdate:draw}},{t0:.3f});'
         f'tl.fromTo(V,{{sw:34}},{{sw:0,duration:.3,ease:"power2.in",immediateRender:false,onUpdate:draw}},{t0 + dur - 0.2:.3f});'
         f'tl.fromTo(V,{{amp:grains?60:16}},{{amp:grains?4:5,duration:{1.5 if mat == "liquid" else 0.7},ease:grains?"power3.out":"power1.out",immediateRender:false,onUpdate:draw}},{t0 + dur - 0.1:.3f});'
         f'}})();')
    C = A.pal(X, p)
    X.tw(f'tl.fromTo("{s} .pf-num .f2-num", {{color:"{C['fg']}"}}, {{color:"{C['accent']}", duration:0.25, immediateRender:false}}, {t0 + dur:.3f});')
    X.tw(f'tl.fromTo("{s} .pf-num", {{scale:1}}, {{keyframes:[{{scale:1.08, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {t0 + dur:.3f});')
    if cap:
        X.tw(f'tl.fromTo("{s} .pf-cap", {{opacity:0}}, {{opacity:1, duration:0.4, immediateRender:true}}, {t0 + dur * 0.5:.3f});')
    A.hold_push(X, f"{s} .f2-body", t0 + dur - 0.2, t + d, 1.05, "50% 60%")
    if mat == "liquid":           # the settled liquid keeps living: bubbles rise from the floor to the surface
        rise = vb - 30 - lvl_y(min(val, 100.0)) - 10
        for i in range(8):
            at = t0 + dur * 0.6 + i * 0.37
            if at + 1.2 > t + d:
                break
            X.tw(f'tl.fromTo("{s} .pf-bub:nth-of-type({i + 1})", {{y:0, opacity:0.9}}, {{y:{-rise:.0f}, opacity:0, duration:1.6, ease:"power1.in", immediateRender:false}}, {at:.3f});')
    X.sfx(t0 - 0.2, "whoosh_soft")
    X.sfx(t0 + dur, "pop")


# ------------------------------------------------------------------------------------------------ topple
def _topple_sim(n, h, w, ang0=0.0):
    """dominoes: slab i pivots on its bottom-right corner; slab i's top corner meets slab i+1's face and tips it;
    a slab leaning on its neighbour can never pass through it. → per slab: (start index, [angle per 1/60 s])."""
    G = 23.0              # angular gravity, tuned so a free slab tips 0→90° in ≈ 0.55 s
    dt = 1 / 60.0
    th = [0.0] * n
    om = [0.0] * n
    on = [False] * n
    landed = [False] * n
    bounced = [False] * n
    hist = [[] for _ in range(n)]
    on[0] = True
    om[0] = 2.2
    rad = math.radians

    def allowed(i, phi):
        # largest angle of slab i (degrees) whose top-right corner stays left of slab i+1's left face (slab i+1 at phi)
        lo, hi_ = 0.0, 90.0
        px = w + 0.0                       # slab i pivot at x = w (local frame, floor y = 0)
        qx = h + w                         # slab i+1 pivot
        f = rad(phi)
        blx, bly = qx - w * math.cos(f), -w * math.sin(f)
        tlx, tly = qx - w * math.cos(f) + h * math.sin(f), -w * math.sin(f) - h * math.cos(f)
        ex, ey = tlx - blx, tly - bly
        L = math.hypot(ex, ey)

        def ok(psi):
            ps = rad(psi)
            cx, cy = px + h * math.sin(ps), -h * math.cos(ps)
            rx, ry = cx - blx, cy - bly
            along = (rx * ex + ry * ey) / L
            if along > L or along < 0:
                return True
            cross = ex * ry - ey * rx      # > 0: the corner is on the far (right) side of the face
            return cross <= 0
        if ok(90.0):
            return 90.0
        for _ in range(30):
            mid = (lo + hi_) / 2
            if ok(mid):
                lo = mid
            else:
                hi_ = mid
        return lo

    steps = 0
    while steps < 600:
        steps += 1
        for i in range(n):
            if not on[i] or landed[i] and bounced[i] and abs(om[i]) < 1e-3:
                hist[i].append(th[i])
                continue
            a = G * (math.sin(rad(th[i])) + 0.12)
            om[i] += a * dt
            th[i] += math.degrees(om[i] * dt)
            if th[i] >= 90.0:
                th[i] = 90.0
                if not bounced[i]:
                    om[i] = -abs(om[i]) * 0.18
                    bounced[i] = True
                else:
                    om[i] = 0.0
                landed[i] = True
            if th[i] < 0:
                th[i] = 0.0
            hist[i].append(th[i])
        for i in range(n - 1):
            if not on[i]:
                continue
            lim = allowed(i, th[i + 1])
            if th[i] > lim:
                th[i] = lim
                hist[i][-1] = lim
                if not on[i + 1]:
                    on[i + 1] = True
                    om[i + 1] = max(om[i] * 0.9, 1.6)
                else:
                    om[i + 1] = max(om[i + 1], om[i] * 0.6)
                om[i] = min(om[i], om[i + 1])
        if all(landed) and all(abs(x - 90.0) < 0.01 for x in th):
            break
    return hist


def topple(X, cid, t, d, p):
    """多米诺推倒 Topple: a row of tall slabs, one item written up each spine; a ball rolls in, the first slab tips and knocks
    the next — a real domino chain (each one leans on its neighbour, never through it) — and as they land flat the
    row reads left to right: the items become the sentence. An optional headline slams down on top."""
    F = "topple"
    items = A.texts(F, p, "items", 2, 5)
    A.need(F, t, p, [] if len(items) >= 2 else ["items (2–5 slabs, each a word or short phrase)"])
    while len(items) < 2:
        items.append({"text": "—"})
    n = len(items)
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    floor = G["y1"] - 6 if P else G["y1"] - 16
    wth = (170 if n <= 3 else 150) if P else (160 if n <= 3 else 130)
    avail = G["w"] - (0 if P else 120)
    room = floor - (G["y0"] + hh) - 60                       # standing height the frame allows
    if P:
        hs = min(560.0, max(500.0, room * 0.55)) if room > 520 else room
    else:
        hs = min((avail - wth) / n, room - 160)
    x_start = G["x0"] + (0 if P else max(0, (avail - (n * hs + wth)) / 2) + 60)
    row_end = x_start + n * hs + wth
    pan_max = max(0.0, row_end - (X.W - 40))                  # 9:16: a row longer than the frame → the camera follows the chain
    hl = p.get("hl")
    html = [head]
    mir = []
    for i, it in enumerate(items):
        x = x_start + i * hs
        cls = "b" if (hl is not None and (hl == i or hl == it["text"])) or (hl is None and i == n - 1) else "a"
        tpx, tl_ = A.fit_px(A.strip(it["text"]), hs * 0.88, wth * 0.74, wth * 0.68, 22, max_lines=1, lh=1.0)
        body = f'<span style="font-size:{tpx:.0f}px">{K.hl_html(X, tl_[0])}</span>'
        geo = f'left:{x:.1f}px; top:{floor - hs:.1f}px; width:{wth}px; height:{hs:.1f}px'
        html.append(f'<div class="tp-sl {cls} sl{i}" style="{geo}">{body}</div>')
        mir.append(f'<div class="tp-sl {cls} sl{i}" style="{geo}">{body}</div>')
    plinth = (f'<div class="tp-plinth" style="top:{floor:.0f}px"><div class="tp-mir" style="top:{-floor:.0f}px; height:{X.H}px; transform:scaleY(-1); transform-origin:50% {floor:.0f}px">'
              + '<div class="tp-pan" style="position:absolute; inset:0">' + "".join(mir) + '</div></div></div>')
    html.insert(1, plinth)
    html.insert(2, '<div class="tp-pan" style="position:absolute; inset:0">')
    bd = wth * 0.62
    html.append(f'<div class="tp-ball" style="left:{x_start - bd - 6:.0f}px; top:{floor - bd:.0f}px; width:{bd:.0f}px; height:{bd:.0f}px"></div>')
    for i in range(n):
        for j in range(3):
            html.append(f'<i class="tp-dust du{i}" style="left:{x_start + i * hs + wth + hs * (0.2 + 0.3 * j):.0f}px; top:{floor - 14:.0f}px"></i>')
    html.append('</div>')
    hd = str(p.get("text") or "")
    if hd:
        hy0 = G["y0"] + hh + 10
        hy1 = floor - wth - 40
        hpx, hl_ = A.fit_px(hd, G["w"], max(120, hy1 - hy0), 190 if P else 140, 40, max_lines=2, lh=1.1)
        hy = hy1 - hpx * 1.1 * len(hl_)
        html.append(f'<div class="tp-hd" style="left:{G["x0"]:.0f}px; top:{hy:.0f}px; width:{G["w"]:.0f}px; font-size:{hpx:.0f}px">{A.lines_html(X, hl_)}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    hist = _topple_sim(n, hs, wth)
    push = K.U.when(X, items[0].get("at"), t, None)
    if push is None:
        hit = X.spoken_at(A.strip(items[0]["text"]), t, t + d) if getattr(X, "chars", None) else None
        push = hit if hit is not None else t + d * 0.3
    push = max(push, t + 0.5)
    sim_len = max(len(hh_) for hh_ in hist) / 60.0
    if push + sim_len > t + d - 0.6:
        push = max(t + 0.3, t + d - 0.6 - sim_len)
    # the ball rolls in and taps the first slab at `push`
    X.tw(f'tl.fromTo("{s} .tp-ball", {{x:{-(x_start + 40):.0f}, rotation:-360}}, {{x:0, rotation:0, duration:0.55, ease:"power1.in", immediateRender:true}}, {push - 0.55:.3f});')
    X.tw(f'tl.to("{s} .tp-ball", {{x:-24, rotation:-40, duration:0.4, ease:"power2.out"}}, {push:.3f});')
    lands = []
    for i in range(n):
        seq = hist[i]
        first = 0
        while first < len(seq) and seq[first] <= 0.0:
            first += 1
        frames = []
        last_a = 0.0
        k = first
        while k < len(seq):
            a = seq[k]
            if abs(a - last_a) > 0.05 or k == len(seq) - 1:
                frames.append([round(a, 2), k])
                last_a = a
            k += 2
        kf = []
        prev_k = first
        for a, kk in frames:
            kf.append(f"{{rotation:{a},duration:{max(1, kk - prev_k) / 60:.4f},ease:\"none\"}}")
            prev_k = kk
        st = push + first / 60.0
        X.tw(f'tl.set("{s} .sl{i}", {{rotation:0, transformOrigin:"100% 100%"}}, {t:.3f});')
        if kf:
            X.tw(f'tl.to("{s} .sl{i}", {{keyframes:[{",".join(kf)}]}}, {st:.3f});')
        land = None
        for k in range(len(seq)):
            if seq[k] >= 89.9:
                land = push + k / 60.0
                break
        lands.append(land or (push + sim_len))
        if pan_max > 0:
            tgt = min(pan_max, max(0.0, x_start + i * hs + wth + hs - (X.W - 60)))
            X.tw(f'tl.to("{s} .tp-pan", {{x:{-tgt:.0f}, duration:{max(0.25, lands[-1] - st + 0.15):.2f}, ease:"power1.inOut"}}, {st:.3f});')
        X.tw(f'tl.fromTo("{s} .du{i}", {{opacity:0.8, y:0, scale:0.4}}, {{opacity:0, y:-46, scale:1.8, duration:0.5, ease:"power2.out", stagger:0.04, immediateRender:false}}, {lands[-1]:.3f});')
        X.sfx(lands[-1], "click", 0.5)
    last = max(lands)
    A.shake(X, f"{s} .f2-body", last, amp=10, n=5)
    if hd:
        A.fall(X, f"{s} .tp-hd", last + 0.35, 900, squash=0.1)
        X.tw(f'tl.set("{s} .tp-hd", {{opacity:0}}, {t:.3f}); tl.set("{s} .tp-hd", {{opacity:1}}, {last + 0.35 - A.fall_time(900):.3f});')
        A.shake(X, f"{s} .f2-body", last + 0.37, amp=16, n=6, seed=1)
        X.sfx(last + 0.35, "slam")
    X.sfx(push, "tick")


# ------------------------------------------------------------------------------------------------ magnet_sort
def _magnet_svg(w, h, col):
    """a horseshoe magnet (U), poles up; tips in a lighter band."""
    t_ = w * 0.27
    r_out = w / 2
    r_in = r_out - t_
    cy = h - r_out
    path = (f"M 0 0 L {t_:.0f} 0 L {t_:.0f} {cy:.0f} A {r_in:.0f} {r_in:.0f} 0 0 0 {w - t_:.0f} {cy:.0f} L {w - t_:.0f} 0 L {w:.0f} 0 "
            f"L {w:.0f} {cy:.0f} A {r_out:.0f} {r_out:.0f} 0 0 1 0 {cy:.0f} Z")
    tip = h * 0.2
    return (f'<svg class="ms-mag-s" width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}" style="overflow:visible"><path d="{path}" fill="{col}"/>'
            f'<rect x="0" y="0" width="{t_:.0f}" height="{tip:.0f}" fill="color-mix(in srgb, var(--bg) 75%, var(--fg))"/>'
            f'<rect x="{w - t_:.0f}" y="0" width="{t_:.0f}" height="{tip:.0f}" fill="color-mix(in srgb, var(--bg) 75%, var(--fg))"/></svg>')


def _isnum(v):
    try:
        float(str(v).replace(",", "").replace("%", ""))
        return True
    except ValueError:
        return False


def magnet_sort(X, cid, t, d, p):
    """磁极分拣 Magnet Sort: dozens of chips lie scattered over the whole frame; two magnets switch on and every chip flies to
    its pole (closest first, overshooting into the pile), each pole tallying as its pile grows. The split you see IS the
    split in the data: 97.5 % vs 2.5 % lands as 39 chips against 1."""
    F = "magnet_sort"
    la, lb = str(p.get("a") or ""), str(p.get("b") or "")
    miss = []
    if not la or not lb:
        miss.append("a and b (the two pole labels)")
    na = A.number(F, p, "a_count", None, 0, 80)
    nb = A.number(F, p, "b_count", None, 0, 80)
    share = A.number(F, p, "share", None, 0, 100)
    total = int(A.number(F, p, "n", 40, 4, 80))
    if na is None or nb is None:
        if share is None:
            miss.append("a_count + b_count, or share (percent that goes to a)")
            share = 50.0
        na = round(total * share / 100.0)
        nb = total - na
    A.need(F, t, p, miss)
    na, nb = int(na), int(nb)
    if na + nb == 0:
        raise SystemExit(f"{F}: no chips to sort")
    va = p.get("a_value", na)
    vb_ = p.get("b_value", nb)
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    W, H = X.W, X.H
    html = [head]
    tal = []
    R = X.rand
    ca = str(p.get("chip_a") or (A.strip(la)[:1] or "A"))
    cb = str(p.get("chip_b") or (A.strip(lb)[:1] or "B"))
    X.used_text.update(ca + cb)
    ty = G["y0"] + hh + 6
    if P:
        cs, gapc, prow = 66, 6, 5
        mw, mh = 380, 290
        mtop = H - mh - 8                                   # magnets stand on the bottom edge
        mxs = {"a": W * 0.25 - mw / 2, "b": W * 0.75 - mw / 2}
        y = ty
        for key, lab, val, mcol in (("a", la, va, "var(--accent)"), ("b", lb, vb_, "var(--fg)")):
            align = "left" if key == "a" else "right"
            lpx, ll = A.fit_px(lab, G["w"], 70, 54, 34, max_lines=1)
            vstr = str(val)
            X.used_text.update(vstr + "0123456789.,%")
            tpx, _ = A.fit_px(vstr, G["w"], 300, 260, 240, max_lines=1, lh=1.0)
            html.append(f'<div class="ms-lab" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:{y:.0f}px; font-size:{lpx:.0f}px; text-align:{align}">{K.hl_html(X, ll[0])}</div>')
            html.append(f'<div class="ms-tal t{key}" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:{y + lpx * 1.25:.0f}px; text-align:{align}"><span class="f2-num" style="font-size:{tpx:.0f}px; color:{mcol}">{"0" if _isnum(vstr) else X.rich(vstr)}</span></div>')
            y += lpx * 1.25 + tpx * 0.98 + 14
            mx = mxs[key]
            html.append(f'<div class="ms-mag m{key}" style="left:{mx:.0f}px; top:{mtop:.0f}px; width:{mw}px; height:{mh}px">{_magnet_svg(mw, mh, mcol)}</div>')
            html.append(f'<i class="ms-ring r{key}" style="left:{mx + mw / 2 - 180:.0f}px; top:{mtop - 60:.0f}px; width:360px; height:360px"></i>')
            tal.append((key, val, mx + mw / 2, mx))
        scatter = (40, W - 40 - cs, G["y0"] + hh + 120, mtop - cs - 20)
    else:
        cs, gapc, prow = 50, 6, 5
        mw, mh = 300, 250                                   # drawn poles-up, turned to face the centre
        mcy = G["y1"] - mw / 2 + 10
        mxs = {"a": G["x0"] - 30, "b": G["x1"] - mh + 30}
        for key, lab, val, mcol in (("a", la, va, "var(--accent)"), ("b", lb, vb_, "var(--fg)")):
            align = "left" if key == "a" else "right"
            lx = G["x0"] if key == "a" else G["x0"] + G["w"] * 0.5
            lpx, ll = A.fit_px(lab, G["w"] * 0.48, 60, 46, 34, max_lines=1)
            vstr = str(val)
            X.used_text.update(vstr + "0123456789.,%")
            tpx, _ = A.fit_px(vstr, G["w"] * 0.46, 220, 200, 160, max_lines=1, lh=1.0)
            html.append(f'<div class="ms-lab" style="left:{lx:.0f}px; width:{G["w"] * 0.5:.0f}px; top:{ty:.0f}px; font-size:{lpx:.0f}px; text-align:{align}">{K.hl_html(X, ll[0])}</div>')
            html.append(f'<div class="ms-tal t{key}" style="left:{lx:.0f}px; width:{G["w"] * 0.5:.0f}px; top:{ty + lpx * 1.2:.0f}px; text-align:{align}"><span class="f2-num" style="font-size:{tpx:.0f}px; color:{mcol}">{"0" if _isnum(vstr) else X.rich(vstr)}</span></div>')
            rot = 90 if key == "a" else -90
            mx = mxs[key]
            # the box is mh wide × mw tall once turned; the svg inside is turned about its centre
            html.append(f'<div class="ms-mag m{key}" style="left:{mx:.0f}px; top:{mcy - mw / 2:.0f}px; width:{mh}px; height:{mw}px">'
                        f'<div style="position:absolute; left:{(mh - mw) / 2:.0f}px; top:{(mw - mh) / 2:.0f}px; width:{mw}px; height:{mh}px; transform:rotate({rot}deg)">{_magnet_svg(mw, mh, mcol)}</div></div>')
            html.append(f'<i class="ms-ring r{key}" style="left:{mx + mh / 2 - 160:.0f}px; top:{mcy - 160:.0f}px; width:320px; height:320px"></i>')
            tal.append((key, val, mx + mh / 2, mx))
        scatter = (G["x0"] + 320, G["x1"] - 320 - cs, G["y0"] + hh + 300, G["y1"] - cs)
    chips = []
    order = ["a"] * na + ["b"] * nb
    R.shuffle(order)
    slots = {"a": 0, "b": 0}
    for i, pole in enumerate(order):
        sx = R.uniform(scatter[0], scatter[1])
        sy = R.uniform(scatter[2], max(scatter[2] + 10, scatter[3]))
        k = slots[pole]
        slots[pole] += 1
        r_, c_ = divmod(k, prow)
        if P:
            cx_ = mxs[pole] + mw / 2
            row_w = prow * (cs + gapc) - gapc
            tx = cx_ - row_w / 2 + c_ * (cs + gapc)
            tyy = mtop - 14 - (r_ + 1) * (cs + gapc)
        else:
            col_h = prow * (cs + gapc) - gapc
            tyy = mcy - col_h / 2 + c_ * (cs + gapc)
            if pole == "a":
                tx = mxs["a"] + mh + 10 + r_ * (cs + gapc)
            else:
                tx = mxs["b"] - 10 - cs - r_ * (cs + gapc)
        chips.append([round(sx), round(sy), round(tx), round(tyy), pole, round(R.uniform(-40, 40))])
    for i, c in enumerate(chips):
        html.append(f'<div class="ms-chip c{i}" style="width:{cs}px; height:{cs}px; font-size:{cs * 0.5:.0f}px">{X.rich(ca if c[4] == "a" else cb)}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    ts = K.U.when(X, p.get("at"), t, None)
    if ts is None:
        hit = X.spoken_at(A.strip(la), t, t + d) if getattr(X, "chars", None) else None
        ts = hit if hit is not None else t + min(0.9, d * 0.22)
    win = max(0.8, min(1.6, t + d - ts - 1.4))
    # flight order: closest to its magnet first
    dist = []
    for i, c in enumerate(chips):
        dist.append((math.hypot(c[0] - c[2], c[1] - c[3]), i))
    dist.sort()
    starts = {}
    for rank, (_, i) in enumerate(dist):
        starts[i] = ts + 0.12 + win * (rank / max(1, len(chips) - 1)) ** 0.8
    # re-slot in arrival order so piles fill bottom-up
    for pole in ("a", "b"):
        idx = [i for _, i in dist if chips[i][4] == pole]
        tgt = sorted([(chips[i][2], chips[i][3]) for i in idx], key=lambda q: (-q[1], q[0]))
        for j, i in enumerate(idx):
            chips[i][2], chips[i][3] = tgt[j]
    C = A.pal(X, p)
    data = []
    for i, c in enumerate(chips):
        data.append([c[0], c[1], c[2], c[3], 1 if c[4] == "a" else 0, c[5], round(starts[i], 3)])
    X.tw(f'(()=>{{const S="{s}", D={A.js(data)}; D.forEach((c,i)=>{{const e=S+" .c"+i;'
         f'tl.set(e,{{x:c[0],y:c[1],rotation:c[5]}},{t:.3f});'
         f'tl.fromTo(e,{{scale:0}},{{scale:1,duration:.3,ease:"back.out(2)",immediateRender:false}},{t + 0.05:.3f}+(i%12)*.012);'
         f'tl.to(e,{{x:c[2],duration:.55,ease:"power2.in"}},c[6]);'
         f'tl.to(e,{{y:c[3],rotation:0,duration:.62,ease:"back.out(1.7)"}},c[6]);'
         f'tl.to(e,{{backgroundColor:c[4]?"{C['accent']}":"{C['fg']}",color:c[4]?"{C['on']}":"{C['bg']}",duration:.12}},c[6]+.45);}});}})();')
    for key, val, cx_, mx in tal:
        arr = sorted(starts[i] + 0.5 for i, c in enumerate(chips) if c[4] == key)
        if not arr:
            continue
        sval = str(val)
        num = None
        try:
            num = float(sval.replace(",", "").replace("%", ""))
        except ValueError:
            num = None
        if num is not None:
            dec = A.decimals(sval)
            suf = "%" if sval.strip().endswith("%") else ""
            X.tw(f'(()=>{{const el=document.querySelector("{s} .t{key} .f2-num"); if(!el) return; const o={{v:0}};'
                 f'tl.fromTo(o,{{v:0}},{{v:{num},duration:{max(0.1, arr[-1] - arr[0]):.2f},ease:"none",immediateRender:false,onUpdate:()=>{{el.textContent=o.v.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})+"{suf}";}}}},{arr[0]:.3f});}})();')
        X.tw(f'tl.fromTo("{s} .m{key}", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.1}}, {{scale:1, duration:0.3, ease:"power2.out"}}], transformOrigin:"50% 100%", immediateRender:false}}, {ts:.3f});')
        X.tw(f'tl.fromTo("{s} .r{key}", {{opacity:0.9, scale:0.3}}, {{opacity:0, scale:1.6, duration:0.7, ease:"power2.out", immediateRender:false}}, {ts:.3f});')
        X.tw(f'tl.fromTo("{s} .r{key}", {{opacity:0.6, scale:0.3}}, {{opacity:0, scale:1.6, duration:0.7, ease:"power2.out", immediateRender:false}}, {ts + 0.3:.3f});')
    X.sfx(ts, "whoosh_soft")
    X.sfx(ts + win + 0.5, "pop")


FX = {"drop_stack": drop_stack, "pour_fill": pour_fill, "topple": topple, "magnet_sort": magnet_sort}
