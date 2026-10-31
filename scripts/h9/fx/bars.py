"""柱状图生长 Bar Chart Grow (D2, Infographic Maker 2.6K / Clean Growth Chart 878; Mapal「Animate Infographics Like VOX」
34.6 万播放): baseline + gridlines draw first, bars grow out of the zero line staggered with their values counting,
the highlighted bar flips to the accent and pops, a growth chip lands on it.

Adapts to its input: 1–15+ bars (vertical; switches to horizontal ranking bars when there are many items or long
labels, or with "orient": "h"), negative values (bars hang below a zero line, in a muted colour), huge values (auto
万 / 亿 or K / M / B, "compact": "cn" | "en" | "none"), labels from 1 glyph to a phrase (font fitted, 2 lines max).
p: items [[label, value], ...] · unit · dec · hl (index, -1 = none) · title · note · growth · orient · compact
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


def bars(X, cid, t, d, p):
    items = [(str(lb), float(v)) for lb, v in p["items"]]
    n = len(items)
    vals = [v for _, v in items]
    div, suf = F.compact(max(abs(v) for v in vals), p.get("compact", "cn"))
    unit = (suf + p.get("unit", "")) if div != 1 else p.get("unit", "")
    dec = int(p.get("dec", 1 if div != 1 or any(v != int(v) for v in vals) else 0))
    hl = int(p.get("hl", n - 1 if all(v >= 0 for v in vals) else -1))
    lo, hi = None, None
    Wv, Hv = F.frame_vmin(X)
    max_lab = max(F.em(lb) for lb, _ in items)
    horiz = p.get("orient") == "h" or (p.get("orient") != "v" and (n > (7 if X.portrait else 10) or (max_lab > 4.5 and n > 4)))
    lo, hi = F.series_range(vals, 1.08 if horiz else 1.28)
    cw = min(120.0, Wv * 0.86); ch = min(62.0, Hv * 0.52) if not X.portrait else min(84.0, Hv * 0.42)
    if horiz: ch = min(Hv * (0.40 if X.portrait else 0.56), max(30.0, n * 7.5))
    X.css("fx-bars", """
.fx .bc { position:absolute; left:50%; top:52%; transform:translate(-50%,-50%); }
#root.v .fx .bc { top:43%; }
.fx .bc .bct { position:absolute; left:0; bottom:calc(100% + 4vmin); font:900 4.4vmin var(--f-display); color:var(--fg); white-space:nowrap; }
.fx .bc .bct small { font:500 2vmin var(--f-mono, monospace); color:var(--muted); margin-left:1.6vmin; letter-spacing:.06em; }
.fx .bc .bcg { position:absolute; background:color-mix(in srgb, var(--fg) 13%, transparent); }
.fx .bc .bcz { position:absolute; background:var(--fg); }
.fx .bc .bcb { position:absolute; background:color-mix(in srgb, var(--fg) 78%, var(--bg)); }
.fx .bc .bcb.neg { background:color-mix(in srgb, var(--fg) 40%, var(--bg)); }
.fx .bc .bcb.hl { background:var(--accent); }
.fx .bc .bcv { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:800; line-height:1; color:var(--fg); font-variant-numeric:tabular-nums; white-space:nowrap; }
.fx .bc .bcv small { font-size:.5em; margin-left:.15em; color:var(--muted); }
.fx .bc .bcv.hl { color:var(--accent); }
.fx .bc .bcl { position:absolute; font-family:var(--f-body); font-weight:700; line-height:1.15; color:var(--muted); }
.fx .bc .bcl .fl { display:block; white-space:nowrap; }
.fx .bc .bcgr { position:absolute; display:flex; align-items:center; gap:.8vmin; white-space:nowrap; }
.fx .bc .bcgr b { font:900 3.4vmin var(--f-display); color:var(--bg); background:var(--accent); padding:.3vmin 1.3vmin; border-radius:.6vmin; }
.fx .bc .bcgr svg { width:4.4vmin; height:4.4vmin; overflow:visible; } .fx .bc .bcgr path { fill:none; stroke:var(--accent); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
""")
    span = hi - lo
    zr = hi / span                                   # zero line: fraction from the top (vertical) / from the left is lo
    fmt = lambda v: f"{v / div:,.{dec}f}"
    vstr = max((fmt(v) for v in vals), key=F.em) + unit
    html, tw = [], []
    if not horiz:
        gap = 0.42 if n <= 6 else 0.28 if n <= 10 else 0.18
        w = cw / (n + (n + 1) * gap)                 # bar width in vmin
        vs = min(4.6, w * 1.05 / max(F.em(vstr) * 0.95, 1))
        lab_size, _ = F.fit(max((lb for lb, _ in items), key=F.em), w * 1.25, 6, 2.6, 1.3, 2)
        html.append(f'<i class="bcz" style="left:0; right:0; top:{zr * 100:.2f}%; height:.4vmin; margin-top:-.2vmin"></i>')
        for k in (0.25, 0.5, 0.75):
            html.append(f'<i class="bcg" style="left:0; right:0; top:{k * 100:.0f}%; height:.15vmin"></i>')
        for i, (lb, v) in enumerate(items):
            x = gap * w * (i + 1) + w * i
            h = abs(v) / span * 100
            cls = "hl" if i == hl else ("neg" if v < 0 else "")
            pos = f"bottom:{(1 - zr) * 100:.2f}%" if v >= 0 else f"top:{zr * 100:.2f}%"
            org = "50% 100%" if v >= 0 else "50% 0%"
            html.append(f'<i class="bcb {cls}" data-i="{i}" style="left:{x:.2f}vmin; width:{w:.2f}vmin; {pos}; height:{h:.2f}%; transform-origin:{org}; border-radius:{".6vmin .6vmin 0 0" if v >= 0 else "0 0 .6vmin .6vmin"}"></i>')
            vpos = (f"bottom:calc({(1 - zr) * 100 + h:.2f}% + 1vmin)" if v >= 0 else f"top:calc({zr * 100 + h:.2f}% + 1vmin)")
            html.append(f'<div class="bcv {"hl" if i == hl else ""}" data-i="{i}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); {vpos}; font-size:{vs:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            _, ll = F.fit(lb, w * 1.25, 6, lab_size, lab_size, 2)
            html.append(f'<div class="bcl" data-i="{i}" style="left:{x + w / 2:.2f}vmin; transform:translateX(-50%); top:calc(100% + 1.6vmin); font-size:{lab_size:.2f}vmin; text-align:center">{F.lines_html(X, ll)}</div>')
        if 0 <= hl < n and items[hl][1] > 0 and items[0][1] > 0 and hl != 0 and n <= 10:
            grow = p.get("growth") or f"+{(items[hl][1] / items[0][1] - 1) * 100:.0f}%"
            xh = gap * w * (hl + 1) + w * hl + w / 2
            hh = items[hl][1] / span * 100
            html.append(f'<div class="bcgr" style="left:{xh:.2f}vmin; transform:translateX(-50%); bottom:calc({(1 - zr) * 100 + hh:.2f}% + {vs + 2.2:.2f}vmin)"><b>{X.rich(grow)}</b>'
                        '<svg viewBox="0 0 40 40"><path d="M4 34 C 14 30, 26 20, 34 6 M34 6 l-9 2 M34 6 l-1 9"/></svg></div>')
        grow_axis = "scaleY"
    else:
        rh = ch / n
        lab_w = min(cw * 0.3, max(F.em(lb) for lb, _ in items) * min(3.2, rh * 0.5) + 1)
        lab_size = min(3.2, rh * 0.5, (lab_w - 1) / max(max_lab, 1))
        track = cw - lab_w - 2
        vs = min(3.2, rh * 0.55)
        val_w = F.em(vstr) * vs + 1.5
        track -= val_w
        zx = -lo / span                               # zero line from the left of the track
        x0 = lab_w + 2
        html.append(f'<i class="bcz" style="left:{x0 + zx * track:.2f}vmin; top:0; bottom:0; width:.35vmin"></i>')
        for i, (lb, v) in enumerate(items):
            y = rh * i + rh * 0.15
            bh = rh * 0.7
            w = abs(v) / span * track
            cls = "hl" if i == hl else ("neg" if v < 0 else "")
            left = x0 + zx * track - (w if v < 0 else 0)
            html.append(f'<i class="bcb {cls}" data-i="{i}" style="left:{left:.2f}vmin; width:{w:.2f}vmin; top:{y:.2f}vmin; height:{bh:.2f}vmin; transform-origin:{"100% 50%" if v < 0 else "0 50%"}; border-radius:{"0 .5vmin .5vmin 0" if v >= 0 else ".5vmin 0 0 .5vmin"}"></i>')
            vx = (left + w + 1) if v >= 0 else (x0 + zx * track + 1)      # negatives: value sits on the empty positive side
            tr = ""
            html.append(f'<div class="bcv {"hl" if i == hl else ""}" data-i="{i}" style="left:{vx:.2f}vmin; {tr} top:{y + bh / 2 - vs / 2:.2f}vmin; font-size:{vs:.2f}vmin"><span class="n">0</span><small>{X.rich(unit)}</small></div>')
            html.append(f'<div class="bcl" data-i="{i}" style="right:calc(100% - {lab_w:.2f}vmin); top:{y + bh / 2 - lab_size * 0.58:.2f}vmin; font-size:{lab_size:.2f}vmin; text-align:right"><span class="fl">{X.rich(lb)}</span></div>')
        grow_axis = "scaleX"
    X.used_text.update("0123456789.,+-%" + unit)
    inner = (f'<div class="bc" style="width:{cw:.2f}vmin; height:{ch:.2f}vmin"><div class="bct">{X.rich(p.get("title", ""))}<small>{X.rich(p.get("note", ""))}</small></div>'
             + "".join(html) + '</div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .bct", {{x:-30, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .bcz", {{{"scaleX" if not horiz else "scaleY"}:0, duration:0.45, ease:"expo.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .bcg", {{scaleX:0, transformOrigin:"0 50%", duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.2:.3f});')
    st = min(0.22, max(0.05, (d - 1.6) / max(n, 1)))
    gd = 0.75 if n <= 8 else 0.55
    fj = F.js_fmt(dec)
    for i, (lb, v) in enumerate(items):
        ti = t + 0.4 + i * st
        X.tw(f'tl.from("{s} .bcb[data-i=\'{i}\']", {{{grow_axis}:0, duration:{gd}, ease:"power3.out"}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .bcv[data-i=\'{i}\'], {s} .bcl[data-i=\'{i}\']", {{opacity:0, duration:0.35, ease:"power2.out"}}, {ti:.3f});')
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .bcv[data-i=\'{i}\'] .n"), f={fj}; tl.to(o, {{v:{v / div}, duration:{gd}, ease:"power3.out", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {ti:.3f});}})();')
        if n <= 8 or i % 2 == 0: X.sfx(ti, "tick")
    th = t + 0.4 + (n - 1) * st + gd + 0.05
    if 0 <= hl < n:
        ax2 = "scaleX" if not horiz else "scaleY"
        X.tw(f'tl.to("{s} .bcb.hl", {{keyframes:[{{{ax2}:1.08, duration:0.12}}, {{{ax2}:1, duration:0.3, ease:"back.out(3)"}}]}}, {th:.3f});')
        X.sfx(th + 0.1, "hit")
    X.tw(f'tl.from("{s} .bcgr", {{scale:0, transformOrigin:"50% 100%", duration:0.4, ease:"back.out(2.5)"}}, {th + 0.1:.3f});')


FX = {"bars": bars}
