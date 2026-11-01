"""倒计时 Countdown (talkcraft countdown-arc-scatter; VideoHive Elements 大类 countdown / openers; 「给你 5 秒猜一猜」):
a ring sweeps once per tick while the digit flips over to the next one, the frame jolts on each hit, and on zero
the ring bursts and the reveal slams in (optional — without it the last number holds as the answer).

Adapts: counts from 2 to 10 (or any start/end), ticks spread over the beat (a long beat slows the ticks, a short
one tightens them), label and reveal a word to a sentence (fitted, ≤ 2 lines).
p: from (5) · to (1) · question · reveal · unit
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .cd { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .cd svg.cd-r { position:absolute; overflow:visible; }
.fx .cd svg.cd-r circle { fill:none; }
.fx .cd .cd-dg { position:absolute; display:grid; place-items:center; overflow:hidden; }
.fx .cd .cd-dg span { position:absolute; inset:0; display:grid; place-items:center; font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--fg);
  font-variant-numeric:tabular-nums; line-height:1; }
.fx .cd .cd-l { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:800; color:var(--fg); }
.fx .cd .cd-l .sl, .fx .cd .cd-rv .sl { display:block; white-space:nowrap; }
.fx .cd .cd-rv { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); font-weight:900; color:var(--accent); }
.fx .cd .cd-bs i { position:absolute; width:.6vmin; background:var(--accent); border-radius:.3vmin; transform-origin:50% 0; }
"""


def countdown(X, cid, t, d, p):
    a, b = int(p.get("from", 5)), int(p.get("to", 1))
    seq = list(range(a, b - 1, -1)) if a >= b else list(range(a, b + 1))
    seq = seq[:12] or [3]
    label, reveal = fit.as_text(p.get("question") or p.get("ask")), fit.as_text(p.get("reveal"))
    x, y, w, h = S.box(X, p)
    lf = fit.fit_text(label, w * 0.9, h * 0.16, S.vm(X, 5.4), S.vm(X, 2.8), max_lines=2) if label else None
    lh_ = lf.n * lf.px * 1.25 + S.vm(X, 3) if lf else 0
    R = min(w * 0.42, (h - lh_) * 0.42, S.vm(X, 30))
    cx, cy = x + w / 2, y + lh_ + (h - lh_) / 2
    X.css("fx-cd", CSS)
    FG, AC = S.col(X, p, "fg"), S.col(X, p, "accent")
    sw = max(6, R * 0.07)
    C = 2 * 3.14159265 * R
    ring = (f'<svg class="cd-r" width="{2 * R:.0f}" height="{2 * R:.0f}" style="left:{cx - R:.0f}px; top:{cy - R:.0f}px" viewBox="{-R:.1f} {-R:.1f} {2 * R:.1f} {2 * R:.1f}">'
            f'<circle r="{R - sw / 2:.1f}" stroke="{FG}" stroke-opacity=".14" stroke-width="{sw:.1f}"/>'
            f'<circle class="arc" r="{R - sw / 2:.1f}" stroke="{AC}" stroke-width="{sw:.1f}" stroke-linecap="round" transform="rotate(-90)" stroke-dasharray="{C:.1f}" stroke-dashoffset="{C:.1f}"/></svg>')
    dpx = R * (1.05 if max(len(str(v)) for v in seq) == 1 else 0.8)
    digits = "".join(f'<span data-k="{k}" style="font-size:{dpx:.0f}px">{v}</span>' for k, v in enumerate(seq))
    html = [ring, f'<div class="cd-dg" style="left:{cx - R:.0f}px; top:{cy - R:.0f}px; width:{2 * R:.0f}px; height:{2 * R:.0f}px">{digits}</div>']
    if lf: html.append(f'<div class="cd-l" style="top:{y:.0f}px; font-size:{lf.px}px">{S.lines(X, lf)}</div>')
    if reveal:
        rf = fit.fit_text(reveal, w * 0.9, R * 1.2, S.vm(X, 13), S.vm(X, 4), max_lines=2)
        html.append(f'<div class="cd-rv" style="top:{cy - rf.n * rf.px * 0.6:.0f}px; font-size:{rf.px}px">{S.lines(X, rf)}</div>')
    rays = "".join(f'<i style="left:{cx:.0f}px; top:{cy:.0f}px; height:{R * 0.3:.0f}px; transform:rotate({k * 24}deg) translateY({R * 1.08:.0f}px)"></i>' for k in range(15))
    html.append(f'<div class="cd-bs">{rays}</div>')
    _clip(X, cid, t, d, f'<div class="cd">{"".join(html)}</div>', p)
    s = f"#{cid} .cd"
    n = len(seq)
    end = t + d * (0.66 if reveal else 0.85)
    tick = (end - (t + 0.35)) / n
    X.tw(f'tl.set("{s} .cd-dg span", {{yPercent:100}}, {t:.3f});')
    X.tw(f'tl.set("{s} .cd-bs i", {{scaleY:0, opacity:0}}, {t:.3f});')
    if lf: X.tw(f'tl.from("{s} .cd-l .sl", {{yPercent:80, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .cd-r", {{scale:0.6, opacity:0, duration:0.5, ease:"back.out(1.8)"}}, {t + 0.05:.3f});')
    for k in range(n):
        tk = t + 0.35 + k * tick
        sp = f"{s} .cd-dg span[data-k='{k}']"
        X.tw(f'tl.to("{sp}", {{yPercent:0, duration:0.32, ease:"back.out(1.6)"}}, {tk:.3f});')
        if k > 0: X.tw(f'tl.to("{s} .cd-dg span[data-k=\'{k - 1}\']", {{yPercent:-100, duration:0.28, ease:"power3.in"}}, {tk - 0.02:.3f});')
        X.tw(f'tl.fromTo("{s} .arc", {{strokeDashoffset:{C:.1f}}}, {{strokeDashoffset:0, duration:{max(0.2, tick * 0.92):.2f}, ease:"none", immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s}", {{x:0}}, {{keyframes:[{{x:-8, duration:0.04}}, {{x:6, duration:0.04}}, {{x:0, duration:0.05}}], immediateRender:false}}, {tk:.3f});')
        X.sfx(tk, "tick")
    if reveal:
        X.tw(f'tl.to("{s} .cd-dg, {s} .cd-r", {{scale:0.5, opacity:0, duration:0.3, ease:"power3.in"}}, {end:.3f});')
        X.tw(f'tl.from("{s} .cd-rv", {{scale:1.8, opacity:0, filter:"blur(12px)", duration:0.45, ease:"expo.out"}}, {end + 0.2:.3f});')
    X.tw(f'tl.to("{s} .cd-bs i", {{keyframes:[{{scaleY:1, opacity:1, duration:0.18}}, {{scaleY:0.2, opacity:0, duration:0.45, ease:"power2.in"}}]}}, {end + (0.2 if reveal else 0):.3f});')
    X.sfx(end + (0.2 if reveal else 0), "hit")


FX = {"countdown": countdown}
