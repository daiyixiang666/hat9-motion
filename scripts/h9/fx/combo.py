"""计数连击 Combo Counter (格斗 / 音游的 COMBO 计数；B 站「连击」梗；直播间点赞连击特效):
hits land faster and faster: each one slams the big ×N counter, a ring bursts, a +1 chip slides into the stack
on the side and the frame jolts; the counter's colour climbs from grey to ink to the accent; on the last hit the
meter fills, the ring bursts wide and the punchline lands.

Adapts: 2–999 hits (up to 60 shown one by one; beyond that the counter steps), hit chips any text (a label per
hit or one repeated label), timing from "at" cues or accelerating across the beat; final line ≤ 2 lines.
p: count · hits (labels) · tag ("COMBO"; "label" is the gallery footer) · unit · final · at
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit
from h9.core import esc

CSS = """
.fx .cb { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .cb .cb-tag { position:absolute; font-family:var(--f-mono, monospace); font-weight:800; letter-spacing:.3em; color:var(--bg); background:var(--fg); white-space:nowrap; }
.fx .cb .cb-n { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.85; white-space:nowrap; font-variant-numeric:tabular-nums; opacity:0; transform-origin:0% 80%; }
.fx .cb .cb-n small { font-family:var(--f-display); font-size:.42em; margin-right:.06em; vertical-align:.5em; }
.fx .cb .cb-u { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; }
.fx .cb .cb-ring { position:absolute; border-radius:50%; border:.7vmin solid var(--accent); opacity:0; }
.fx .cb .cb-chips { position:absolute; overflow:hidden; }
.fx .cb .cb-chip { position:absolute; left:0; font-family:var(--f-body); font-weight:800; color:var(--fg); white-space:nowrap; opacity:0; }
.fx .cb .cb-chip b { color:var(--accent); margin-right:.4em; font-family:var(--f-mono, monospace); }
.fx .cb .cb-meter { position:absolute; height:1.2vmin; background:color-mix(in srgb, var(--fg) 14%, transparent); border-radius:.6vmin; overflow:hidden; }
.fx .cb .cb-meter i { position:absolute; inset:0; background:var(--accent); transform-origin:0 50%; transform:scaleX(0); }
.fx .cb .cb-fin { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .cb .cb-fin .sl { display:block; white-space:nowrap; }
"""


def combo(X, cid, t, d, p):
    P = X.portrait
    hits = [fit.as_text(h_) for h_ in fit.as_list(p.get("hits"))]
    N = int(p.get("count") or len(hits) or 10)
    N = max(2, min(N, 999))
    label = fit.as_text(p.get("tag") or "COMBO")
    unit = fit.as_text(p.get("unit"))
    final = fit.as_text(p.get("final"))
    x, y, w, h = S.box(X, p)
    steps = N if N <= 60 else 60
    # times: accelerating, or from cues
    at = fit.as_list(p.get("at"))
    times = None
    if at and X.chars and len(at) >= steps:
        try: times = [float(X.T(c, t)) for c in at[:steps]]
        except SystemExit: times = None
    span = max(0.6, d * (0.6 if final else 0.75))
    if not times:
        acc = lambda n: [t + 0.35 + span * ((k / max(n - 1, 1)) ** 0.62) for k in range(n)]
        times = acc(steps)
        while steps > 2 and times[-1] - times[-2] < 0.06:      # at least two frames per hit; beyond that the counter steps
            steps -= 1
            times = acc(steps)
    vals = [round((k + 1) * N / steps) for k in range(steps)]
    t_end = times[-1]
    # layout: counter on the right (16:9) / centre (9:16); chips on the left / below
    npx = min(S.vm(X, 30 if P else 34), h * (0.36 if P else 0.6))
    digits = len(str(N)) + 1
    npx = min(npx, (w * (0.9 if P else 0.55)) / (digits * 0.62))
    ncx = x + (w * 0.08 if P else w * 0.42)
    ncy = y + (h * 0.12 if P else (h - npx) / 2 - S.vm(X, 3))
    cpx = S.vm(X, 3.4 if P else 3.0)
    chips_x, chips_y = (x, ncy + npx * 1.25) if P else (x, y + h * 0.2)
    chips_w, chips_h = (w, cpx * 1.6 * 4) if P else (w * 0.36, h * 0.6)
    X.css("fx-cb", CSS)
    tiers = ["var(--muted)", "var(--fg)", "var(--accent)"]
    html = [f'<div class="cb-tag" style="left:{ncx:.0f}px; top:{ncy - S.vm(X, 6):.0f}px; font-size:{S.vm(X, 2.6):.0f}px; padding:{S.vm(X, .5):.0f}px {S.vm(X, 1.4):.0f}px">{X.rich(label)}</div>']
    rs = npx * 1.6
    for q in range(4):     # rings take turns so fast hits never fight over one element
        html.append(f'<i class="cb-ring" data-q="{q}" style="left:{ncx + npx * 0.6 - rs / 2:.0f}px; top:{ncy + npx * 0.45 - rs / 2:.0f}px; width:{rs:.0f}px; height:{rs:.0f}px"></i>')
    for k, v in enumerate(vals):
        col = tiers[min(2, int(3 * k / max(steps, 1)))]
        html.append(f'<div class="cb-n" data-k="{k}" style="left:{ncx:.0f}px; top:{ncy:.0f}px; font-size:{npx:.0f}px; color:{col}"><small>×</small>{v}</div>')
    if unit:
        html.append(f'<div class="cb-u" style="opacity:0; left:{ncx + npx * (0.62 * (len(str(N)) + 0.6)):.0f}px; top:{ncy + npx * 0.52:.0f}px; font-size:{npx * 0.24:.0f}px">{X.rich(unit)}</div>')
    html.append(f'<div class="cb-meter" style="left:{ncx:.0f}px; top:{ncy + npx * 0.98:.0f}px; width:{min(w * 0.5, npx * 0.62 * digits):.0f}px"><i></i></div>')
    chip_rows = int(chips_h / (cpx * 1.6))
    chips = []
    for k in range(steps):
        lab = hits[min(vals[k] - 1, len(hits) - 1)] if hits else (unit or "hit")
        chips.append(f'<div class="cb-chip" data-k="{k}" style="top:{chips_h - cpx * 1.6:.0f}px; font-size:{cpx:.0f}px"><b>+{vals[k] - (vals[k - 1] if k else 0)}</b>{X.rich(lab)}</div>')
    html.append(f'<div class="cb-chips" data-layout-allow-overflow style="left:{chips_x:.0f}px; top:{chips_y:.0f}px; width:{chips_w:.0f}px; height:{chips_h:.0f}px">{"".join(chips)}</div>')
    if final:
        ff = fit.fit_text(final, w * (0.9 if P else 0.5), h * 0.22, S.vm(X, 7.4), S.vm(X, 3.2), max_lines=2, lh=1.12)
        fy = (ncy + npx * 1.25 + chips_h + S.vm(X, 3)) if P else (ncy + npx * 1.15)
        html.append(f'<div class="cb-fin" style="left:{ncx if not P else x:.0f}px; top:{fy:.0f}px; font-size:{ff.px}px">' + "".join(f'<span class="sl">{X.rich(l)}</span>' for l in ff.lines) + "</div>")
    _clip(X, cid, t, d, f'<div class="cb">{"".join(html)}</div>', p)
    s = f"#{cid} .cb"
    X.tw(f'tl.from("{s} .cb-tag", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .cb-meter", {{opacity:0, duration:0.3}}, {t + 0.1:.3f});')
    if unit: X.tw(f'tl.to("{s} .cb-u", {{opacity:1, duration:0.2}}, {times[0]:.3f});')
    for k, tk in enumerate(times):
        gap = (times[k + 1] - tk) if k + 1 < steps else 0.4
        g = min(0.2, gap * 0.85)
        sel = f'{s} .cb-n[data-k=\'{k}\']'
        if k: X.tw(f'tl.set("{s} .cb-n[data-k=\'{k - 1}\']", {{opacity:0}}, {tk:.3f});')
        big = (k + 1) % 5 == 0 or k == steps - 1
        X.tw(f'tl.fromTo("{sel}", {{opacity:1, scale:{1.55 if big else 1.3}}}, {{scale:1, duration:{min(0.18, max(0.05, gap * 0.9)):.3f}, ease:"power4.out", immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .cb-ring[data-q=\'{k % 4}\']", {{opacity:0.9, scale:0.5}}, {{opacity:0, scale:{1.5 if big else 1.15}, duration:{min(0.35, 0.9 * ((times[k + 4] - tk) if k + 4 < steps else 0.4)):.3f}, ease:"power2.out", immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .cb-meter i", {{scaleX:{(k + 1) / steps:.3f}, duration:{g:.3f}}}, {tk:.3f});')
        # chips: the new one slides in at the bottom, older ones move up one row (finished before the next hit)
        X.tw(f'tl.fromTo("{s} .cb-chip[data-k=\'{k}\']", {{opacity:0, x:-40}}, {{opacity:1, x:0, duration:{g:.3f}, ease:"expo.out", immediateRender:false}}, {tk:.3f});')
        for back in range(1, chip_rows + 1):
            j = k - back
            if j < 0: break
            X.tw(f'tl.to("{s} .cb-chip[data-k=\'{j}\']", {{y:{-back * cpx * 1.6:.0f}, opacity:{max(0.0, 1 - back / chip_rows):.2f}, duration:{g:.3f}, ease:"power2.out"}}, {tk + 0.001:.3f});')
        X.tw(f'tl.fromTo("{s}", {{x:0}}, {{keyframes:[{{x:{-10 if big else -4}, duration:{min(0.03, gap / 3):.3f}}}, {{x:{8 if big else 3}, duration:{min(0.03, gap / 3):.3f}}}, {{x:0, duration:{min(0.04, gap / 3):.3f}}}], immediateRender:false}}, {tk:.3f});')
        if k < 40 or big: X.sfx(tk, "hit" if big else "click")
    if final:
        X.tw(f'tl.from("{s} .cb-fin .sl", {{yPercent:80, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t_end + 0.25:.3f});')


FX = {"combo": combo}
