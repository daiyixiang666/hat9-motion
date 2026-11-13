"""fx2 · camera: dolly_layers · rack_focus · orbit_number — the lens moves, not the cards. Depth is real CSS 3D (one
perspective, planes at real z), focus is computed from distance to the focal plane every frame (seekable: one
proxy tween, drawn in onUpdate). Colours / fonts only from the style tokens.
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
.f2 .dl-view { position:absolute; inset:0; perspective:900px; overflow:hidden; }
.f2 .dl-world { position:absolute; inset:0; transform-style:preserve-3d; }
.f2 .dl-p { position:absolute; left:0; top:0; transform-style:flat; will-change:transform, filter, opacity; }
.f2 .dl-fr { position:absolute; border:3px solid color-mix(in srgb, var(--fg) 26%, transparent); border-radius:var(--k-r); }
.f2 .dl-tx { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.12; color:var(--fg); }
.f2 .dl-tx .sl { display:block; white-space:nowrap; }
.f2 .dl-ix { position:absolute; font:800 40px var(--f-mono, monospace); color:var(--accent); letter-spacing:.08em; }
.f2 .dl-floor { position:absolute; transform-origin:50% 0; transform:rotateX(-90deg);
  background-image:repeating-linear-gradient(90deg, color-mix(in srgb, var(--fg) 26%, transparent) 0 3px, transparent 3px 180px),
                   repeating-linear-gradient(0deg, color-mix(in srgb, var(--fg) 20%, transparent) 0 3px, transparent 3px 240px); }
.f2 .dl-fade { position:absolute; left:0; right:0; pointer-events:none; }
.f2 .rf-b, .f2 .rf-a { position:absolute; will-change:transform, filter; }
.f2 .rf-tx { font-family:var(--f-display); font-weight:900; line-height:1.14; }
.f2 .rf-tx .sl { display:block; white-space:nowrap; }
.f2 .rf-lab { display:inline-block; font:800 34px var(--f-body); letter-spacing:.12em; padding:6px 16px; border-radius:var(--k-rs); margin-bottom:22px; }
.f2 .rf-card { position:absolute; background:var(--card); color:var(--card-fg); border-radius:var(--k-r) var(--k-r) 0 0; box-shadow:var(--k-sh); }
.f2 .rf-bk { position:absolute; border-radius:50%; background:color-mix(in srgb, var(--accent) 34%, transparent); filter:blur(14px); }
.f2 .on-view { position:absolute; inset:0; perspective:1400px; overflow:hidden; }
.f2 .on-sc { position:absolute; left:0; top:0; width:0; height:0; transform-style:preserve-3d; }
.f2 .on-l { position:absolute; left:0; top:0; white-space:nowrap; font-family:var(--f-num, var(--f-display)); font-weight:900; letter-spacing:-.03em; line-height:1;
  transform-style:preserve-3d; }
.f2 .on-unit { position:absolute; left:0; top:0; white-space:nowrap; font-family:var(--f-display); font-weight:900; color:var(--fg); }
.f2 .on-lab { position:absolute; left:0; top:0; white-space:nowrap; font:800 40px var(--f-body); background:color-mix(in srgb, var(--bg) 80%, transparent); padding:6px 14px; border-radius:var(--k-rs); color:var(--fg); display:flex; align-items:center; gap:14px; }
.f2 .on-lab i { width:18px; height:18px; border-radius:50%; background:var(--accent); flex:none; box-shadow:0 0 0 6px color-mix(in srgb, var(--accent) 25%, transparent); }
.f2 .on-disc { position:absolute; border-radius:50%; transform-origin:50% 50%;
  background:repeating-radial-gradient(circle, color-mix(in srgb, var(--fg) 22%, transparent) 0 3px, transparent 3px 60px); }
.f2 .on-floor { position:absolute; left:0; right:0; bottom:0;
  background:repeating-linear-gradient(0deg, transparent 0 58px, color-mix(in srgb, var(--fg) 13%, transparent) 58px 61px), linear-gradient(180deg, transparent, color-mix(in srgb, var(--accent) 18%, var(--bg)) 70%); }
"""


def _css(X):
    X.css("fx-f2-cam", CSS)


# ------------------------------------------------------------------------------------------------ dolly_layers
def dolly_layers(X, cid, t, d, p):
    """推轨穿层 Dolly Layers: one continuous camera push through 4–6 planes standing at real depth — the title, each item,
    then the number. The plane at the focal distance is sharp; planes ahead are soft and small, planes behind the lens
    sweep past and dissolve. Each plane arrives in focus when the narration says it."""
    F = "dolly_layers"
    title = str(p.get("title") or "")
    items = A.texts(F, p, "items", 2, 4)
    val = p.get("value")
    miss = []
    if not title:
        miss.append("title (the first plane)")
    if len(items) < 2:
        miss.append("items (2–4 planes)")
    if val in (None, ""):
        miss.append("value (the last plane: a number)")
    A.need(F, t, p, miss)
    title = title or "—"
    while len(items) < 2:
        items.append({"text": "—"})
    if val in (None, ""):
        val = "0"
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    D = 1500.0 if P else 1300.0
    cy = (G["y0"] + G["y1"]) / 2 - (30 if P else 0)
    planes = []
    tw_ = G["w"] - (40 if P else 200)
    if title:
        px, ln = A.fit_px(title, tw_, 640, 200 if P else 150, 40, max_lines=3, lh=1.12)
        planes.append(("title", f'<div class="dl-tx" style="left:{(W - tw_) / 2:.0f}px; width:{tw_:.0f}px; top:{cy - px * 1.12 * len(ln) / 2:.0f}px; font-size:{px:.0f}px; text-align:center">{A.lines_html(X, ln)}</div>', title))
    for i, it in enumerate(items):
        px, ln = A.fit_px(A.strip(it["text"]), tw_ - 40, 520, 240 if P else 170, 36, max_lines=2, lh=1.12)
        off = (20 if i % 2 == 0 else -20) if P else (140 if i % 2 == 0 else -140)
        x = (W - tw_) / 2 + off
        h_ = px * 1.12 * len(ln)
        planes.append(("item", f'<div class="dl-ix" style="left:{x:.0f}px; top:{cy - h_ / 2 - 66:.0f}px">{i + 1:02d}</div>'
                               f'<div class="dl-tx" style="left:{x:.0f}px; width:{tw_:.0f}px; top:{cy - h_ / 2:.0f}px; font-size:{px:.0f}px">{A.lines_html(X, ln)}</div>', it["text"]))
    if val not in (None, ""):
        vs = str(val)
        unit = str(p.get("unit") or "")
        X.used_text.update(vs + unit)
        vpx, _ = A.fit_px(vs, tw_ * 0.98, 460, 420 if P else 320, 60, max_lines=1, lh=1.0)
        lab = str(p.get("label") or "")
        lab_h = ""
        if lab:
            lpx, ll = A.fit_px(lab, tw_, 60, 46, 26, max_lines=1)
            lab_h = f'<div class="dl-tx" style="left:{(W - tw_) / 2:.0f}px; width:{tw_:.0f}px; top:{cy + vpx * 0.62:.0f}px; font-size:{lpx:.0f}px; font-weight:700; text-align:center; color:var(--muted)">{X.rich(ll[0])}</div>'
        unit_h = f'<div class="dl-tx" style="left:{(W - tw_) / 2:.0f}px; width:{tw_:.0f}px; top:{cy + vpx * 0.5:.0f}px; text-align:center; font-size:{min(90, vpx * 0.3):.0f}px; color:var(--accent)">{X.rich(unit)}</div>' if unit else ""
        if lab_h:
            lab_h = lab_h.replace(f"top:{cy + vpx * 0.62:.0f}px", f"top:{cy + vpx * 0.5 + (min(90, vpx * 0.3) * 1.2 if unit else 0) + 10:.0f}px")
        planes.append(("num", f'<div class="dl-tx" style="left:{(W - tw_) / 2:.0f}px; width:{tw_:.0f}px; top:{cy - vpx * 0.6:.0f}px; text-align:center; color:var(--accent); line-height:1; white-space:nowrap">'
                              f'<span class="f2-num" style="font-size:{vpx:.0f}px">{X.rich(vs)}</span></div>' + unit_h + lab_h, vs))
    n = len(planes)
    if n > 6:
        raise SystemExit(f"{F}: {n} planes — at most 6 (title + 4 items + number)")
    ins = 70 if P else 90
    html = []
    for k, (kind, body, _) in enumerate(planes):
        fr = f'<div class="dl-fr" style="left:{ins}px; top:{G["y0"] - 30:.0f}px; width:{W - 2 * ins}px; height:{G["y1"] - G["y0"] + 60:.0f}px"></div>'
        html.append(f'<div class="dl-p p{k}" style="width:{W}px; height:{H}px">{fr}{body}</div>')
    depth = n * D + 4000
    floor = (f'<div class="dl-floor" style="left:{-W:.0f}px; width:{3 * W:.0f}px; top:{G["floor"] - 40:.0f}px; height:{depth:.0f}px; transform:translateZ({800:.0f}px) rotateX(-90deg)"></div>')
    fade = f'<div class="dl-fade" style="top:{G["floor"] - 260:.0f}px; height:260px; background:linear-gradient(180deg, transparent, color-mix(in srgb, var(--bg) 0%, transparent))"></div>'
    inner = f'<div class="dl-view"><div class="dl-world">{floor}{"".join(html)}</div></div>{fade}'
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, inner)
    texts = [{"text": A.strip(x[2])} for x in planes]
    stops = A.cues(X, p, texts, t, d, start=0.08, end=0.72, gap=0.55)
    stops[0] = min(stops[0], t + 0.45)
    X.tw(f'(()=>{{const R=document.querySelector("{s}"); if(!R) return; const w=R.querySelector(".dl-world"), ps=[...R.querySelectorAll(".dl-p")], D={D}, N={n};'
         f'const V={{z:{-0.55 * D:.0f}, dr:0}};'
         f'const draw=()=>{{const cz=V.z+V.dr; w.style.transform="translateZ("+cz.toFixed(1)+"px)";'
         f'ps.forEach((e,k)=>{{const rel=cz-k*D; e.style.transform="translateZ("+(-k*D)+"px)"; let b, o;'
         f'const dz=Math.max(0,Math.abs(rel)-0.12*D); if(rel<0){{b=Math.min(16,dz/D*12); o=rel<-2.6*D?0:Math.min(1,(2.6*D+rel)/(0.6*D));}} else {{b=Math.min(22,dz/30); o=Math.max(0,1-rel/620);}}'
         f'e.style.filter=b>0.15?"blur("+b.toFixed(2)+"px)":"none"; e.style.opacity=o.toFixed(3); e.style.visibility=o<0.01?"hidden":"";}});}};'
         f'draw();'
         f'tl.fromTo(V,{{dr:0}},{{dr:{0.08 * D:.0f},duration:{d:.2f},ease:"none",immediateRender:false,onUpdate:draw}},{t:.3f});'
         f'tl.fromTo(V,{{z:{-0.55 * D:.0f}}},{{z:{-0.08 * D:.0f},duration:{max(0.3, stops[0] - t):.2f},ease:"power3.out",immediateRender:false,onUpdate:draw}},{t:.3f});'
         + "".join(f'tl.fromTo(V,{{z:{(k - 1) * D - 0.08 * D:.0f}}},{{z:{k * D - 0.08 * D:.0f},duration:{max(0.35, stops[k] - stops[k - 1] - 0.1):.2f},ease:"expo.inOut",immediateRender:false,onUpdate:draw}},{stops[k - 1] + 0.1:.3f});'
                   for k in range(1, n))
         + '})();')
    for k in range(1, n):
        X.sfx(stops[k] - 0.3, "whoosh_soft", 0.5)
    X.tw(f'tl.fromTo("{s} .p{n - 1} .f2-num", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.12}}, {{scale:1, duration:0.4, ease:"back.out(3)"}}], immediateRender:false}}, {stops[-1]:.3f});')


# ------------------------------------------------------------------------------------------------ rack_focus
def rack_focus(X, cid, t, d, p):
    """焦点转移 Rack Focus: two planes at different depths — the claim on a card close to the lens, the fact further back.
    The focus pulls from one to the other: the near plane melts into blur and drifts toward camera, the far one
    sharpens (with a small focus-hunt overshoot) and settles. The pull lands when the narration says the fact."""
    F = "rack_focus"
    a, b = str(p.get("a") or ""), str(p.get("b") or "")
    A.need(F, t, p, [x for x, ok in (("a (the near plane: claim / before)", a), ("b (the far plane: fact / after)", b)) if not ok])
    a = a or "—"
    b = b or "—"
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    la, lb = str(p.get("a_label") or ""), str(p.get("b_label") or "")
    if P:
        bx, bw_, by = G["x0"], G["w"], G["y0"] + 30
        bpx, bl = A.fit_px(b, bw_, 470, 140, 44, max_lines=3, lh=1.14)
        ax, aw = G["x0"] - 10, G["w"] + 20
        ay = max(by + (bpx * 1.14 * len(bl)) + (70 if lb else 10) + 60, G["y1"] - 520)
        apx, al = A.fit_px(a, aw - 100, G["y1"] - ay - 110 - (60 if la else 0), 130, 40, max_lines=3, lh=1.14)
        card = (ax, ay, aw, H - ay + 60)
    else:
        bw_ = G["w"] * 0.56
        bx, by = G["x1"] - bw_, G["y0"] + 20
        bpx, bl = A.fit_px(b, bw_, 420, 120, 40, max_lines=3, lh=1.14)
        aw = G["w"] * 0.52
        ax = G["x0"] - 20
        ay = G["y0"] + (G["y1"] - G["y0"]) * 0.42
        apx, al = A.fit_px(a, aw - 100, G["y1"] - ay - 80, 110, 36, max_lines=3, lh=1.14)
        card = (ax, ay, aw, H - ay + 60)
    R = X.rand
    bok = ""
    for i in range(6):
        r = R.uniform(70, 170)
        bok += f'<i class="rf-bk" style="left:{R.uniform(-40, W - 80):.0f}px; top:{R.uniform(card[1] - 120, H - 60):.0f}px; width:{r:.0f}px; height:{r:.0f}px"></i>'
    lab_b = f'<span class="rf-lab" style="background:var(--accent); color:var(--k-on)">{X.rich(lb)}</span>' if lb else ""
    lab_a = f'<span class="rf-lab" style="background:var(--card-fg); color:var(--card)">{X.rich(la)}</span>' if la else ""
    html = (f'<div class="rf-b" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw_:.0f}px">{lab_b}<div class="rf-tx" style="font-size:{bpx:.0f}px; color:var(--fg)">{A.lines_html(X, bl)}</div></div>'
            f'<div class="rf-a"><div class="rf-card" style="left:{card[0]:.0f}px; top:{card[1]:.0f}px; width:{card[2]:.0f}px; height:{card[3]:.0f}px"></div>'
            f'<div style="position:absolute; left:{card[0] + 50:.0f}px; top:{card[1] + 50:.0f}px; width:{card[2] - 100:.0f}px">{lab_a}<div class="rf-tx" style="font-size:{apx:.0f}px">{A.lines_html(X, al)}</div></div>{bok}</div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, html)
    tp = K.U.when(X, p.get("at"), t, None)
    if tp is None:
        hit = X.spoken_at(A.strip(b), t, t + d) if getattr(X, "chars", None) else None
        tp = hit if hit is not None else t + d * 0.45
    tp = max(t + 0.9, min(tp, t + d - 1.0))
    X.tw(f'tl.set("{s} .rf-b", {{filter:"blur(16px)", scale:0.93, opacity:0.62, transformOrigin:"50% 50%"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .rf-a", {{filter:"blur(0px)", scale:1, transformOrigin:"50% 30%"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .rf-a", {{y:120}}, {{y:0, duration:0.7, ease:"power3.out", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .rf-a", {{scale:1}}, {{scale:1.025, duration:{tp - t:.2f}, ease:"none", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.to("{s} .rf-a", {{filter:"blur(20px)", scale:1.09, y:50, opacity:0.5, duration:0.75, ease:"power2.inOut"}}, {tp - 0.15:.3f});')
    X.tw(f'tl.to("{s} .rf-b", {{keyframes:[{{filter:"blur(0px)", scale:1.0, opacity:1, duration:0.6, ease:"power2.inOut"}}, {{filter:"blur(3px)", duration:0.1, ease:"none"}}, {{filter:"blur(0px)", duration:0.16, ease:"power1.out"}}]}}, {tp - 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .rf-bk", {{filter:"blur(14px)"}}, {{filter:"blur(30px)", duration:0.75, ease:"power2.inOut", immediateRender:false}}, {tp - 0.15:.3f});')
    X.sfx(tp - 0.1, "whoosh_soft", 0.5)


# ------------------------------------------------------------------------------------------------ orbit_number
def orbit_number(X, cid, t, d, p):
    """环绕大数 Orbit Number: a huge number extruded in real CSS 3D (sixteen stacked slices), the camera orbiting 60° around
    it while it counts up; labels are pinned in space around it and keep facing the lens as the view turns."""
    F = "orbit_number"
    val = p.get("value")
    labels = A.texts(F, p, "labels", 0, 4)
    A.need(F, t, p, [] if val not in (None, "") else ["value (the number)"])
    vs = str(val if val not in (None, "") else "0")
    unit = str(p.get("unit") or "")
    G = A.frame(X, p)
    P = G["P"]
    W, H = X.W, X.H
    hh = 0
    head = ""
    if p.get("title") or p.get("note"):
        head, hh = A.head(X, p, G["x0"], G["y0"], G["w"], align="center")
    X.used_text.update(vs + unit + "0123456789.,")
    vpx, _ = A.fit_px(vs, W * (0.96 if P else 0.8), 560, 560 if P else 420, 60, max_lines=1, lh=1.0)
    cy = (G["y0"] + hh + G["y1"]) / 2 - (30 if P else 10)
    cx = W / 2
    N = 14
    layers = ""
    for i in range(N - 1, -1, -1):        # back to front: a solid dark side wall, then the lit face
        if i == 0:
            col = "var(--accent)"
        elif i == N - 1:
            col = "color-mix(in srgb, var(--accent) 30%, #000)"
        else:
            col = "color-mix(in srgb, var(--accent) 52%, #000)"
        layers += f'<div class="on-l L{i}" style="font-size:{vpx:.0f}px; color:{col}; transform:translate(-50%,-50%) translateZ({-i * 5:.1f}px)"><b class="v" style="font-weight:inherit">{X.rich(vs)}</b></div>'
    refl = ""
    if unit:
        upx, ul = A.fit_px(unit, G["w"], 90, 64 if P else 54, 34, max_lines=1)
        refl = f'<div class="on-unit" style="font-size:{upx:.0f}px; transform:translate(-50%, {vpx * 0.58:.0f}px) translateZ(4px)">{X.rich(ul[0])}</div>'
    disc_r = G["w"] * 0.55
    disc = f'<div class="on-disc" style="left:{-disc_r:.0f}px; top:{-disc_r:.0f}px; width:{2 * disc_r:.0f}px; height:{2 * disc_r:.0f}px; transform:translateY({vpx * 0.52:.0f}px) rotateX(90deg)"></div>'
    pos = []
    if P:
        spots = [(-0.22, -1, 70), (0.22, 1, -70), (0.22, -2, -70), (-0.22, 2, 70)]
    else:
        spots = [(-0.3, -1, 140), (0.3, 1, -140), (0.3, -1, -160), (-0.3, 1, 160)]
    lab_html = ""
    for i, it in enumerate(labels):
        fx_, fy_, z = spots[i]
        lpx, ll = A.fit_px(A.strip(it["text"]), G["w"] * 0.5, 60, 40 if P else 36, 34, max_lines=1)
        x = fx_ * G["w"]
        ring = 1 if abs(fy_) == 1 else 2
        y = (1 if fy_ > 0 else -1) * (vpx * 0.5 + (40 if fy_ < 0 else 70 + (230 if unit else 0)) + (ring - 1) * 66)
        pos.append([round(x), round(y), z])
        lab_html += f'<div class="on-lab b{i}" style="font-size:{lpx:.0f}px"><i></i>{K.hl_html(X, ll[0])}</div>'
    inner = (head + f'<div class="on-floor" style="top:{cy + vpx * 0.4:.0f}px"></div>'
             f'<div class="on-view"><div class="on-sc" style="left:{cx:.0f}px; top:{cy:.0f}px">{disc}{refl}{layers}{lab_html}</div></div>')
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, inner)
    A.head_in(X, s, t, k_)
    num = None
    try:
        num = float(vs.replace(",", ""))
    except ValueError:
        num = None
    dec = A.decimals(vs)
    comma = "," in vs
    X.tw(f'(()=>{{const R=document.querySelector("{s}"); if(!R) return; const sc=R.querySelector(".on-sc"), labs=[...R.querySelectorAll(".on-lab")], vv=[...R.querySelectorAll(".on-l .v")], P={A.js(pos)};'
         f'const V={{a:-32, n:{0 if num is not None else "null"}}};'
         f'const draw=()=>{{sc.style.transform="rotateX(-12deg) rotateY("+V.a.toFixed(2)+"deg)";'
         f'labs.forEach((e,i)=>{{const q=P[i]; e.style.transform="translate3d("+q[0]+"px,"+q[1]+"px,"+q[2]+"px) rotateY("+(-V.a).toFixed(2)+"deg) rotateX(12deg) translate(-50%,-50%)";}});'
         + (f'const s=V.n.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec},useGrouping:{"true" if comma else "false"}}}); vv.forEach(e=>{{e.textContent=s;}});' if num is not None else "")
         + f'}}; draw();'
         f'tl.fromTo(V,{{a:-32}},{{a:32,duration:{d:.2f},ease:"sine.inOut",immediateRender:false,onUpdate:draw}},{t:.3f});'
         + (f'tl.fromTo(V,{{n:0}},{{n:{num},duration:{min(1.4, d * 0.35):.2f},ease:"power3.out",immediateRender:false,onUpdate:draw}},{t + 0.15:.3f});' if num is not None else "")
         + '})();')
    X.tw(f'tl.fromTo("{s} .on-sc", {{opacity:0}}, {{opacity:1, duration:0.3, immediateRender:true}}, {t + 0.05:.3f});')
    for i in range(len(labels)):
        at = t + min(1.0, d * 0.25) + i * 0.3
        X.tw(f'tl.fromTo("{s} .b{i}", {{opacity:0}}, {{opacity:1, duration:0.3, immediateRender:true}}, {at:.3f});')
    X.sfx(t + 0.15, "whoosh_soft")


FX = {"dolly_layers": dolly_layers, "rack_focus": rack_focus, "orbit_number": orbit_number}
