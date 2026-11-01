"""揭晓前悬停 Suspense → Reveal (S10 · 「答案是……」停 1 秒再出数字; S20 句中长停顿; 综艺「揭晓」/ 小Lin说 数字卡前的停顿):
the setup line sits up top while the answer is hidden under a striped card with a pulsing "?"; a heartbeat ticks
faster and faster, a ring of ticks closes, the camera creeps in and the vignette tightens; on the cue the card
splits apart with a flash, the answer slams in (a number counts the last stretch), the frame shakes once and the
note under it settles.

Adapts: any build length (pulses are spaced from the time left, so 0.8 s and 6 s both escalate); the reveal can be
a number (value + unit, auto 万/亿, counted) or text from a word to a phrase (fitted); setup line and note from a
word to a sentence (fitted); optional 3-2-1 countdown on builds ≥ 3 s.
p: q · reveal | value (+ unit, dec) · sub · at ("@关键词" | seconds) | at_rel · countdown · occluder card | blur
"""
from h9.aefx import _clip
import importlib.util, math, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def suspense(X, cid, t, d, p):
    Wv, Hv = F.frame_vmin(X)
    tr = P.at(X, p, "at", t, d, 0.62)
    tr = max(tr, P.snap(X, t + min(0.6, d * 0.4)))
    build = tr - t
    num = p.get("value")
    if num is not None:
        num = float(num); div, suf = F.compact(abs(num), "cn")
        unit = (suf + p.get("unit", "")) if div != 1 else p.get("unit", "")
        dec = int(p.get("dec", 1 if div != 1 or num != int(num) else 0))
        rtxt = f"{num / div:,.{dec}f}"
    else:
        rtxt, unit, dec, div = str(p.get("reveal", "？")), "", 0, 1
    cw = Wv * (0.74 if X.portrait else 0.62)
    rs = min(26.0, cw / max(F.em(rtxt) + F.em(unit) * 0.42, 1.0)) if num is not None else F.fit(rtxt, cw, Hv * 0.3, 22, 4, 2)[0]
    rl = [rtxt] if num is not None else F.fit(rtxt, cw, Hv * 0.3, 22, 4, 2)[1]
    qs, ql = F.fit(p.get("q", ""), Wv * 0.84, Hv * 0.16, 6.4 if X.portrait else 5.6, 2.6, 2) if p.get("q") else (0, [])
    ss, sl = F.fit(p.get("sub", ""), Wv * 0.8, Hv * 0.12, 3.0, 2.0, 2) if p.get("sub") else (0, [])
    ch = rs * 1.25 * len(rl) + 6
    X.css("fx-p5su", """
.fx .p5su { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:4vmin; }
.fx .p5su .vg { position:absolute; inset:0; background:radial-gradient(closest-side, transparent 55%, rgba(0,0,0,.55)); opacity:.4; pointer-events:none; }
.fx .p5su .q { text-align:center; font-family:var(--f-display); font-weight:800; line-height:1.2; color:var(--fg); } .fx .p5su .q .fl { display:block; white-space:nowrap; }
.fx .p5su .q .dots i { display:inline-block; }
.fx .p5su .slot { position:relative; display:grid; place-items:center; }
.fx .p5su .ans { text-align:center; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1.05; color:var(--accent); letter-spacing:-.02em; white-space:nowrap; font-variant-numeric:tabular-nums; }
.fx .p5su .ans .fl { display:block; } .fx .p5su .ans small { font-size:.42em; margin-left:.1em; color:var(--fg); }
.fx .p5su .occ { position:absolute; inset:-1.5vmin -2vmin; display:flex; }
.fx .p5su .occ .h { flex:1; background:repeating-linear-gradient(-45deg, var(--card) 0 2.2vmin, color-mix(in srgb, var(--card) 70%, var(--fg)) 2.2vmin 4.4vmin);
  box-shadow:inset 0 0 0 .4vmin var(--fg); background-size:200% 100%; }
.fx .p5su .occ .h1 { border-radius:1.6vmin 0 0 1.6vmin; } .fx .p5su .occ .h2 { border-radius:0 1.6vmin 1.6vmin 0; }
.fx .p5su .occ .qm { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); font:900 var(--qs) var(--f-display); color:var(--fg); text-shadow:0 0 3vmin color-mix(in srgb, var(--accent) 60%, transparent); }
.fx .p5su .ring { position:absolute; left:50%; top:50%; width:var(--rd); height:var(--rd); margin:calc(var(--rd) / -2) 0 0 calc(var(--rd) / -2); }
.fx .p5su .ring circle { fill:none; stroke:var(--accent); stroke-width:1.1; stroke-dasharray:1.2 2.2; }
.fx .p5su .cd { position:absolute; right:-9vmin; top:-4vmin; font:900 8vmin var(--f-num, var(--f-display)); color:var(--accent); }
.fx .p5su .sub { text-align:center; font-family:var(--f-body); font-weight:600; line-height:1.4; color:var(--muted); } .fx .p5su .sub .fl { display:block; white-space:nowrap; }
.fx .p5su .flash { position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none; }
""")
    X.used_text.update("0123456789.,？?" + unit)
    ans = (f'<div class="ans" style="font-size:{rs:.2f}vmin"><span class="n">{"0" if num is not None else ""}</span><small>{X.rich(unit)}</small></div>' if num is not None
           else f'<div class="ans" style="font-size:{rs:.2f}vmin">{P.lines_html(X, rl)}</div>')
    cdn = 3 if p.get("countdown") and build >= 3 else 0
    cd = "".join(f'<div class="cd" data-k="{k}" style="opacity:0">{k}</div>' for k in range(cdn, 0, -1))
    rd = max(ch, cw * 0.5) * 1.35
    inner = (f'<div class="p5su"><div class="vg"></div>' + (f'<div class="q" style="font-size:{qs:.2f}vmin">{P.lines_html(X, ql)}</div>' if ql else "")
             + f'<div class="slot" style="min-width:{min(cw, max(30, (F.em(rtxt) + 1) * rs)):.1f}vmin; min-height:{ch:.1f}vmin">{ans}'
             f'<svg class="ring" viewBox="0 0 100 100" style="--rd:{rd:.1f}vmin"><circle cx="50" cy="50" r="48"/></svg>'
             f'<div class="occ" style="--qs:{min(ch * 0.7, 18):.1f}vmin"><i class="h h1"></i><i class="h h2"></i><b class="qm">?</b></div>{cd}</div>'
             + (f'<div class="sub" style="font-size:{ss:.2f}vmin">{P.lines_html(X, sl)}</div>' if sl else "") + '<i class="flash"></i></div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    # build: creep + vignette + ring closes + stripes crawl + accelerating heartbeat
    X.tw(f'tl.fromTo("{s} .p5su", {{scale:1}}, {{scale:{1 + min(0.08, 0.02 + 0.012 * build):.3f}, duration:{build:.2f}, ease:"power1.in"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .p5su", {{scale:1, duration:0.35, ease:"expo.out"}}, {tr:.3f});')
    X.tw(f'tl.fromTo("{s} .p5su .vg", {{opacity:0.25}}, {{opacity:0.9, duration:{build:.2f}, ease:"power2.in"}}, {t:.3f}); tl.to("{s} .p5su .vg", {{opacity:0.2, duration:0.4}}, {tr:.3f});')
    X.tw(f'tl.fromTo("{s} .p5su .ring", {{scale:1.35, rotation:0, opacity:0.2}}, {{scale:1.0, rotation:{90 + 25 * build:.0f}, opacity:1, duration:{build:.2f}, ease:"power2.in"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .p5su .ring", {{scale:1.6, opacity:0, duration:0.4, ease:"expo.out"}}, {tr:.3f});')
    X.tw(f'tl.fromTo("{s} .p5su .occ .h", {{backgroundPosition:"0% 0%"}}, {{backgroundPosition:"{60 + 40 * build:.0f}% 0%", duration:{build:.2f}, ease:"none"}}, {t:.3f});')
    if ql: X.tw(f'tl.from("{s} .p5su .q .fl", {{yPercent:50, opacity:0, duration:0.55, ease:"expo.out", stagger:0.08}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .p5su .occ", {{scaleX:0.4, opacity:0, duration:0.45, ease:"back.out(1.8)"}}, {t + 0.12:.3f});')
    # heartbeat: intervals shrink from ~0.6 s to ~0.14 s, ending on the reveal
    beats, k, x = [], 0, tr - 0.2
    while x > t + 0.25:
        beats.append(x); k += 1; x -= min(0.6, 0.14 * (1.32 ** k))
    for i, b in enumerate(sorted(beats)):
        amp = 1.06 + 0.1 * (i + 1) / max(len(beats), 1)
        X.tw(f'tl.fromTo("{s} .p5su .occ .qm", {{scale:{amp:.3f}}}, {{scale:1, duration:0.12, ease:"power2.out", immediateRender:false}}, {P.snap(X, b):.3f});')
        X.sfx(P.snap(X, b), "tick", 0.2 + 0.25 * i / max(len(beats), 1))
    for j, k_ in enumerate(range(cdn, 0, -1)):
        tk = P.snap(X, tr - (cdn - j) * min(0.8, build / (cdn + 1)))
        X.tw(f'tl.fromTo("{s} .p5su .cd[data-k=\'{k_}\']", {{opacity:1, scale:1.6}}, {{scale:1, duration:0.25, ease:"expo.out", immediateRender:false}}, {tk:.3f}); tl.set("{s} .p5su .cd[data-k=\'{k_}\']", {{opacity:0}}, {tk + min(0.78, build / (cdn + 1)) - 0.02:.3f});')
    if build > 1.0: X.sfx(tr - min(1.6, build), "riser", 0.22)
    # reveal
    X.tw(f'tl.to("{s} .p5su .occ .h1", {{xPercent:-130, rotation:-8, opacity:0, duration:0.34, ease:"power3.out"}}, {tr - 0.03:.3f});')
    X.tw(f'tl.to("{s} .p5su .occ .h2", {{xPercent:130, rotation:8, opacity:0, duration:0.34, ease:"power3.out"}}, {tr - 0.03:.3f});')
    X.tw(f'tl.to("{s} .p5su .occ .qm", {{scale:0, opacity:0, duration:0.15}}, {tr - 0.02:.3f});')
    X.tw(f'tl.fromTo("{s} .p5su .flash", {{opacity:0.7}}, {{opacity:0, duration:0.18, ease:"none", immediateRender:false}}, {tr:.3f});')
    X.tw(f'tl.from("{s} .p5su .ans", {{scale:1.7, opacity:0, filter:"blur(8px)", duration:0.32, ease:"expo.out"}}, {tr:.3f});')
    X.tw(f'tl.fromTo("{s} .p5su .slot", {{x:0}}, {{keyframes:[{{x:-16, duration:0.04}}, {{x:12, duration:0.04}}, {{x:-6, duration:0.04}}, {{x:0, duration:0.05}}]}}, {tr + 0.06:.3f});')
    if num is not None:
        fj = F.js_fmt(dec)
        X.tw(f'(()=>{{const o={{v:{num / div * 0.82:.4f}}}, el=document.querySelector("{s} .p5su .n"), f={fj}; el.textContent=f(o.v); tl.to(o, {{v:{num / div:.4f}, duration:0.45, ease:"power3.out", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {tr:.3f});}})();')
    if sl: X.tw(f'tl.from("{s} .p5su .sub .fl", {{y:14, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {tr + 0.35:.3f});')
    post = t + d - tr
    if post > 0.6: X.tw(f'tl.fromTo("{s} .p5su .slot", {{scale:1}}, {{scale:{1 + min(0.06, 0.015 * post):.3f}, duration:{post:.2f}, ease:"sine.out", immediateRender:false}}, {tr + 0.25:.3f});')
    X.sfx(tr, "slam", 0.5); X.sfx(tr, "boom", 0.35)


FX = {"suspense": suspense}
