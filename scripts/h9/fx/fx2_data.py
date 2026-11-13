"""fx2 · data that tells: zoom_scale · small_multiples (bar_race lives in bar_race.py). The chart is the hero and
runs to the bottom edge; labels stay in the text-safe box. Colours / fonts only from the style tokens.
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
.f2 .zs-bar { position:absolute; transform-origin:50% 100%; border-radius:var(--k-rs) var(--k-rs) 0 0; }
.f2 .zs-a { background:var(--fg); } .f2 .zs-b { background:var(--accent); }
.f2 .zs-dot { position:absolute; width:34px; height:34px; margin:-17px 0 0 -17px; border-radius:50%; background:var(--fg); opacity:0; }
.f2 .zs-ring { position:absolute; width:120px; height:120px; margin:-60px 0 0 -60px; border-radius:50%; border:4px solid var(--fg); opacity:0; }
.f2 .zs-gl { position:absolute; height:3px; background:color-mix(in srgb, var(--fg) 24%, transparent); }
.f2 .zs-gt { position:absolute; font:700 28px var(--f-mono, monospace); color:var(--muted); white-space:nowrap; transform:translateY(-120%); }
.f2 .zs-lab { position:absolute; white-space:nowrap; }
.f2 .zs-lab .n { display:block; font:800 38px var(--f-body); color:var(--muted); }
.f2 .zs-lab .v { display:block; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1.05; }
.f2 .zs-ro { position:absolute; white-space:nowrap; font:900 46px var(--f-display); color:var(--accent); text-align:center; }
.f2 .zs-top { position:absolute; height:120px; background:linear-gradient(180deg, var(--bg), transparent); pointer-events:none; }
.f2 .zs-base { position:absolute; height:6px; background:var(--fg); }
.f2 .zs-over { position:absolute; text-align:center; opacity:0; }
.f2 .zs-over b { display:inline-block; font:900 36px var(--f-body); color:var(--k-on); white-space:nowrap; }
.f2 .sm-c { position:absolute; border-radius:var(--k-r); background:color-mix(in srgb, var(--fg) 5%, var(--bg)); outline:2px solid color-mix(in srgb, var(--fg) 14%, transparent); outline-offset:-2px; }
.f2 .sm-c.hl { outline:5px solid var(--accent); outline-offset:-5px; }
.f2 .sm-n { position:absolute; left:16px; top:12px; font:800 34px var(--f-body); color:var(--fg); white-space:nowrap; }
.f2 .sm-s { position:absolute; right:16px; top:18px; font:700 26px var(--f-mono, monospace); color:var(--muted); white-space:nowrap; }
.f2 .sm-c.hl .sm-n { color:var(--accent); }
.f2 .sm-b { position:absolute; bottom:0; transform-origin:50% 100%; background:color-mix(in srgb, var(--fg) 70%, var(--bg)); border-radius:3px 3px 0 0; }
.f2 .sm-c.hl .sm-b, .f2 .sm-big .sm-b { background:var(--accent); }
.f2 .sm-tr { position:absolute; height:3px; background:color-mix(in srgb, var(--fg) 22%, transparent); }
.f2 .sm-big { position:absolute; }
.f2 .sm-bx { position:absolute; font:700 26px var(--f-mono, monospace); color:var(--muted); white-space:nowrap; }
"""


def _css(X):
    X.css("fx-f2-data", CSS)


def _cn(v):
    """4 → "4"; 45000 → "4.5 万"; 4.45e9 → "44.5 亿"."""
    if v >= 1e8:
        x = v / 1e8
        return (f"{x:,.1f}".rstrip("0").rstrip(".")) + " 亿"
    if v >= 1e4:
        x = v / 1e4
        return (f"{x:,.1f}".rstrip("0").rstrip(".")) + " 万"
    return f"{v:,.2f}".rstrip("0").rstrip(".")


# ------------------------------------------------------------------------------------------------ zoom_scale
def zoom_scale(X, cid, t, d, p):
    """十倍缩放 Zoom Scale: two bars on one axis. The axis starts where the small one is easy to see, then zooms out by powers
    of ten — 10 → 100 → 1,000 … — gridlines sliding down and relabelling each step — until the small bar is a dot on the
    floor and the big one finally fits beside it. The number of steps IS the gap."""
    F = "zoom_scale"
    a = p.get("a") or {}
    b = p.get("b") or {}
    if not isinstance(a, dict) or not isinstance(b, dict):
        raise SystemExit(f"{F}: a and b are {{label, value}} objects")
    va = A.number(F, a, "value")
    vb = A.number(F, b, "value")
    miss = []
    if va is None or not a.get("label"):
        miss.append("a {label, value} (the small one)")
    if vb is None or not b.get("label"):
        miss.append("b {label, value} (the big one)")
    A.need(F, t, p, miss)
    va = va if va is not None else 1.0
    vb = vb if vb is not None else 1000.0
    if va <= 0 or vb <= va:
        raise SystemExit(f"{F}: need 0 < a.value < b.value (got {va}, {vb})")
    if vb / va < 50:
        raise SystemExit(f"{F}: {vb / va:.0f}× is under two powers of ten — use bars or scale_compare instead")
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    unit = str(p.get("unit") or "")
    lab_top = G["y0"] + hh + 6
    lab_h = 150 if P else 120
    py = lab_top + lab_h + (110 if P else 70)
    yb = G["floor"] - 6
    Hp = yb - py
    ka = math.ceil(math.log10(va) + 1e-9)
    if va / 10 ** ka > 0.62:
        ka += 1
    kb = math.ceil(math.log10(vb) - 1e-9)
    if vb / 10 ** kb > 0.92:
        kb += 1
    nsteps = kb - ka
    bwid = 300 if P else 260
    xa = G["x0"] + G["w"] * (0.27 if P else 0.3)
    xb = G["x0"] + G["w"] * (0.73 if P else 0.62)
    html = [head]
    for k in range(ka - 1, kb + 1):
        html.append(f'<i class="zs-gl gl{k - ka + 1}" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:0px"></i>')
        html.append(f'<div class="zs-gt gt{k - ka + 1}" style="left:{G["x0"]:.0f}px; top:0px">{X.rich(_cn(10 ** k) + (" " + unit if unit else ""))}</div>')
    for key, x, v, cls, lab in (("a", xa, va, "zs-a", a), ("b", xb, vb, "zs-b", b)):
        html.append(f'<i class="zs-bar {cls} b{key}" style="left:{x - bwid / 2:.0f}px; top:{py:.0f}px; width:{bwid}px; height:{Hp:.0f}px"></i>')
        vs = str(lab.get("show") or (_cn(v) + (" " + unit if unit else "")))
        lw = G["w"] * 0.48
        vpx, _ = A.fit_px(vs, lw, 120, 96 if P else 80, 40, max_lines=1, lh=1.0)
        col = "var(--accent)" if key == "b" else "var(--fg)"
        al = "left" if key == "a" else "right"
        lx = G["x0"] if key == "a" else G["x1"] - lw
        html.append(f'<div class="zs-lab" style="left:{lx:.0f}px; width:{lw:.0f}px; top:{lab_top:.0f}px; text-align:{al}"><span class="n">{K.hl_html(X, lab.get("label") or "—")}</span>'
                    f'<span class="v" style="font-size:{vpx:.0f}px; color:{col}">{X.rich(vs)}</span></div>')
    html.append(f'<i class="zs-dot" style="left:{xa:.0f}px; top:{yb - 17:.0f}px"></i><i class="zs-ring" style="left:{xa:.0f}px; top:{yb - 17:.0f}px"></i>')
    html.append(f'<i class="zs-top" style="left:0; right:0; top:{py - 10:.0f}px"></i>')
    html.append(f'<div class="zs-over" style="left:{xb - bwid / 2:.0f}px; width:{bwid}px; top:{py + 14:.0f}px"><b>↑</b></div>')
    html.append(f'<i class="zs-base" style="left:{G["x0"]:.0f}px; width:{G["w"]:.0f}px; top:{yb:.0f}px"></i>')
    if P:
        html.append(f'<div class="zs-ro" style="left:{G["x0"]:.0f}px; width:{xb - bwid / 2 - G["x0"] - 20:.0f}px; top:{py - 64:.0f}px; text-align:left">×1</div>')
    else:
        html.append(f'<div class="zs-ro" style="left:{G["x0"] + G["w"] * 0.28:.0f}px; width:{G["w"] * 0.44:.0f}px; top:{lab_top + 46:.0f}px; font-size:60px">×1</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    t0 = K.U.when(X, p.get("at"), t, t + min(1.1, d * 0.25))
    span = max(0.35 * nsteps, t + d - 1.1 - t0)
    stp = span / nsteps
    X.used_text.update("×0123456789,")
    X.tw(f'(()=>{{const R=document.querySelector("{s}"); if(!R) return; const q=c=>R.querySelector(c);'
         f'const ba=q(".ba"), bb=q(".bb"), dot=q(".zs-dot"), ro=q(".zs-ro"), K0={ka - 1}, KN={kb}, ka={ka}, va={va}, vb={vb}, py={py:.1f}, yb={yb:.1f}, Hp={Hp:.1f};'
         f'const gl=[], gt=[]; for(let k=K0;k<=KN;k++){{gl.push(q(".gl"+(k-ka+1))); gt.push(q(".gt"+(k-ka+1)));}}'
         f'const V={{lg:ka, g:0}};'
         f'const draw=()=>{{const M=Math.pow(10,V.lg); const ha=va/M*Hp, hb=Math.min(vb/M*Hp, Hp);'
         f'ba.style.transform="scaleY("+(Math.max(ha,0)/Hp*V.g).toFixed(5)+")"; bb.style.transform="scaleY("+(hb/Hp*V.g).toFixed(5)+")";'
         f'const dv=ha<16?Math.min(1,(16-ha)/8):0; dot.style.opacity=(dv*V.g).toFixed(3);'
         f'for(let i=0;i<gl.length;i++){{const k=K0+i, f=Math.pow(10,k-V.lg), y=yb-f*Hp; const vis=(y>=py-4&&y<=yb-6)?1:0;'
         f'const o=vis*Math.min(1,(yb-y)/90)*V.g; gl[i].style.top=y.toFixed(1)+"px"; gl[i].style.opacity=o.toFixed(3);'
         f'gt[i].style.top=y.toFixed(1)+"px"; gt[i].style.opacity=((y<{G["y1"] if P else 1e9:.0f})?o:0).toFixed(3);}}'
         f'const n=Math.floor(V.lg-ka+1e-6); ro.textContent="×"+Math.pow(10,n).toLocaleString("en-US");'
         f'const over=vb/M; const oe=R.querySelector(".zs-over"); if(oe){{if(over>1.02){{oe.style.opacity=V.g; const cn=v=>v>=1e8?(v/1e8).toFixed(v>=1e9?0:1)+" 亿":(v>=1e4?(v/1e4).toFixed(v>=1e5?0:1)+" 万":(v>=10?Math.round(v)+"":v.toFixed(1))); oe.querySelector("b").textContent="↑ 还高 "+cn(over)+" 倍";}} else oe.style.opacity=0;}}}};'
         f'draw();'
         f'tl.fromTo(V,{{g:0}},{{g:1,duration:.7,ease:"power3.out",immediateRender:false,onUpdate:draw}},{t + 0.2:.3f});'
         f'tl.fromTo(V,{{lg:{ka}}},{{lg:{kb},duration:{span:.3f},ease:"sine.inOut",immediateRender:false,onUpdate:draw}},{t0:.3f});'
         + '})();')
    for i in range(nsteps):
        X.sfx(t0 + i * stp + stp * 0.3, "tick", 0.4)
    tend = t0 + span
    X.tw(f'tl.fromTo("{s} .zs-ring", {{opacity:0.9, scale:0.3}}, {{opacity:0, scale:1.6, duration:0.8, ease:"power2.out", immediateRender:false}}, {tend:.3f});')
    X.tw(f'tl.fromTo("{s} .zs-ro", {{scale:1}}, {{keyframes:[{{scale:1.15, duration:0.12}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tend:.3f});')
    X.sfx(tend, "hit")


# ------------------------------------------------------------------------------------------------ small_multiples
def small_multiples(X, cid, t, d, p):
    """小倍数图 Small Multiples: up to twelve mini-charts on one shared scale in a 3 × 4 grid, drawing one after another in
    reading order; then one is singled out — outlined in the accent and, in 9:16, lifted into a full-width version
    under the caption that runs to the bottom edge."""
    F = "small_multiples"
    charts = p.get("charts") or []
    if not isinstance(charts, list):
        raise SystemExit(f"{F}: charts must be a list of {{name, values}}")
    if len(charts) > 12:
        raise SystemExit(f"{F}: at most 12 charts (3 × 4), got {len(charts)} — split the beat")
    rows_ = []
    for c in charts:
        if not isinstance(c, dict) or not c.get("name") or not isinstance(c.get("values"), list) or not c["values"]:
            raise SystemExit(f"{F}: every chart needs a name and a non-empty values list")
        vals = []
        for v in c["values"]:
            vals.append(max(0.0, float(v or 0)))
        rows_.append({"name": str(c["name"]), "values": vals, "note": str(c.get("note") or "")})
    A.need(F, t, p, [] if len(rows_) >= 4 else ["charts (4–12 mini-charts, each {name, values})"])
    if not rows_:
        rows_ = [{"name": "—", "values": [1, 2, 3], "note": ""}] * 4
    n = len(rows_)
    kind = A.choice(F, p, "kind", ("bars", "line"), "bars")
    hl = p.get("hl")
    hi = None
    for i, r in enumerate(rows_):
        if hl is not None and (hl == r["name"] or hl == i):
            hi = i
    G = A.frame(X, p)
    P = G["P"]
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"])
    cols = 3 if P else 4
    nrow = math.ceil(n / cols)
    gap = 18 if P else 20
    top = G["y0"] + hh + 6
    cw = (G["w"] - (cols - 1) * gap) / cols
    ch = (G["y1"] - top - (nrow - 1) * gap) / nrow
    vmax = max(max(r["values"]) for r in rows_) or 1.0
    html = [head]
    xl = p.get("x") or []
    for i, r in enumerate(rows_):
        c_, r_ = i % cols, i // cols
        x = G["x0"] + c_ * (cw + gap)
        y = top + r_ * (ch + gap)
        npx, nl = A.fit_px(r["name"], cw * 0.6, 44, 34, 22, max_lines=1)
        inner = f'<span class="sm-n" style="font-size:{npx:.0f}px">{X.rich(nl[0])}</span>'
        if r["note"]:
            inner += f'<span class="sm-s">{X.rich(r["note"])}</span>'
        px0, px1 = 16, cw - 16
        cy0, cy1 = 64, ch - 16
        m = len(r["values"])
        inner += f'<i class="sm-tr" style="left:{px0}px; width:{px1 - px0:.0f}px; top:{cy1:.0f}px"></i>'
        if kind == "bars":
            bwid = (px1 - px0) / m
            for j, v in enumerate(r["values"]):
                hgt = (cy1 - cy0) * v / vmax
                inner += f'<i class="sm-b" style="left:{px0 + j * bwid + 1:.1f}px; width:{max(2, bwid - 3):.1f}px; height:{hgt:.1f}px; bottom:{ch - cy1:.0f}px"></i>'
        else:
            pts = []
            for j, v in enumerate(r["values"]):
                pts.append(f"{px0 + (px1 - px0) * j / max(1, m - 1):.1f},{cy1 - (cy1 - cy0) * v / vmax:.1f}")
            col = "var(--accent)" if i == hi else "var(--fg)"
            inner += f'<svg style="position:absolute; left:0; top:0; overflow:visible" width="{cw:.0f}" height="{ch:.0f}"><polyline class="sm-ln" points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>'
        html.append(f'<div class="sm-c c{i}{" hl" if i == hi else ""}" style="left:{x:.0f}px; top:{y:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">{inner}</div>')
    big = ""
    if P and hi is not None:
        bx0, by0, by1 = G["x0"], G["y1"] + 70, G["floor"] - 10
        r = rows_[hi]
        m = len(r["values"])
        bwid = G["w"] / m
        body = f'<i class="sm-tr" style="left:0; width:{G["w"]:.0f}px; top:{by1 - by0:.0f}px; height:5px"></i>'
        mm = max(len(q["values"]) for q in rows_)
        sums = [sum(q["values"][j] for q in rows_ if j < len(q["values"])) for j in range(mm)]
        smax = max(sums) or 1.0
        sw_ = G["w"] / mm
        for j, v in enumerate(sums):     # behind it: all charts added up, drawn while the grid draws
            hgt = (by1 - by0 - 30) * v / smax
            body += f'<i class="sm-b sm-sum" style="left:{j * sw_ + 2:.1f}px; width:{max(3, sw_ - 6):.1f}px; height:{hgt:.1f}px; bottom:0; background:color-mix(in srgb, var(--fg) 22%, transparent)"></i>'
        for j, v in enumerate(r["values"]):
            hgt = (by1 - by0 - 30) * v / vmax
            body += f'<i class="sm-b sm-one" style="left:{j * bwid + 2:.1f}px; width:{max(3, bwid - 6):.1f}px; height:{hgt:.1f}px; bottom:{0:.0f}px"></i>'
        big = f'<div class="sm-big" style="left:{bx0:.0f}px; top:{by0:.0f}px; width:{G["w"]:.0f}px; height:{by1 - by0:.0f}px">{body}</div>'
        html.append(big)
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body">{"".join(html)}</div>')
    A.head_in(X, s, t, k_)
    t0 = t + min(0.45, d * 0.1)
    each = min(0.22, (d * 0.55) / n)
    order = list(range(n))
    for i in order:
        at = t0 + i * each
        X.tw(f'tl.fromTo("{s} .c{i}", {{opacity:0, y:24}}, {{opacity:1, y:0, duration:0.3, ease:"power3.out", immediateRender:true}}, {at:.3f});')
        if kind == "bars":
            X.tw(f'tl.fromTo("{s} .c{i} .sm-b", {{scaleY:0}}, {{scaleY:1, duration:0.4, ease:"power3.out", stagger:0.012, immediateRender:true}}, {at + 0.1:.3f});')
        else:
            X.tw(f'tl.to("{s} .c{i} .sm-ln", {{attr:{{"stroke-dashoffset":0}}, duration:0.5, ease:"power2.inOut"}}, {at + 0.1:.3f});')
    tl_ = t0 + n * each + 0.4
    if big:
        X.tw(f'tl.fromTo("{s} .sm-big .sm-sum", {{scaleY:0}}, {{scaleY:1, duration:{max(0.5, n * each):.2f}, ease:"power1.inOut", stagger:0.01, immediateRender:true}}, {t0:.3f});')
    if hi is not None:
        th = K.U.when(X, p.get("at"), t, None)
        if th is None:
            hit = X.spoken_at(rows_[hi]["name"], t, t + d) if getattr(X, "chars", None) else None
            th = hit if hit is not None and hit > tl_ else tl_
        th = min(th, t + d - 1.0)
        others = ", ".join(f"{s} .c{i}" for i in range(n) if i != hi)
        X.tw(f'tl.to("{others}", {{opacity:0.38, duration:0.35}}, {th:.3f});')
        X.tw(f'tl.fromTo("{s} .c{hi}", {{scale:1}}, {{keyframes:[{{scale:1.08, duration:0.18, ease:"power2.out"}}, {{scale:1, duration:0.4, ease:"back.out(2)"}}], immediateRender:false}}, {th:.3f});')
        if big:
            X.tw(f'tl.fromTo("{s} .sm-big .sm-one", {{scaleY:0}}, {{scaleY:1, duration:0.5, ease:"power3.out", stagger:0.02, immediateRender:true}}, {th + 0.15:.3f});')
        X.sfx(th, "pop")
    X.sfx(t0, "whoosh_soft", 0.4)


FX = {"zoom_scale": zoom_scale, "small_multiples": small_multiples}
