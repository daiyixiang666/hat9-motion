"""扫描清除 Scan field ("removed / cleaned / filtered out"): a band of noise — thousands of dots — and a scan line with a
soft trailing glow sweeps across it; every marked dot it passes flashes and vanishes, the field behind the line is
visibly thinner, and the counter beside climbs in step with the sweep. An optional tag rides on the scan head.

Adapts: any share removed (`ratio` 0.05–0.9), the field density from the panel size, counter with prefix / suffix
("1.2万", "3000+"), kicker / unit / tag fitted; panel, dot shape (square in pixel), line weight and accent follow the style.
p: value · ratio · unit · kicker · tag · direction (ltr | rtl) · subject · subject_label · mock
"""
import importlib.util
import pathlib
import random
import sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _load("_metaphor")

CSS = """
.fx .sf .sf-pan { position:absolute; overflow:hidden; }
.fx .sf .sf-pan.rule { background:transparent; box-shadow:none; border-top:var(--mt-sw) solid var(--fg); border-radius:0; }
.fx .sf svg.sf-f { position:absolute; overflow:visible; }
.fx .sf svg.sf-f .kp, .fx .sf svg.sf-f .rm { fill:var(--card-fg); }
.fx .sf .sf-pan.rule svg.sf-f .kp, .fx .sf .sf-pan.rule svg.sf-f .rm { fill:var(--fg); }
.fx .sf svg.sf-f .a1 { opacity:.9; } .fx .sf svg.sf-f .a2 { opacity:.55; } .fx .sf svg.sf-f .a3 { opacity:.25; }
.fx .sf .sf-scan { position:absolute; top:0; bottom:0; width:0; }
.fx .sf .sf-scan .ln { position:absolute; top:0; bottom:0; left:calc(var(--mt-sw) * -.5); width:max(3px, var(--mt-sw)); background:var(--accent); }
.fx .sf .sf-scan .gl { position:absolute; top:0; bottom:0; right:0; width:90px; background:linear-gradient(90deg, transparent, color-mix(in srgb, var(--accent) 32%, transparent)); }
.fx .sf .sf-scan.rtl .gl { right:auto; left:0; background:linear-gradient(270deg, transparent, color-mix(in srgb, var(--accent) 32%, transparent)); }
.fx .sf .sf-tag { position:absolute; bottom:18px; left:14px; font-size:26px; }
.fx .sf .sf-scan.rtl .sf-tag { left:auto; right:14px; }
.fx .sf .sf-info { position:absolute; display:flex; flex-direction:column; justify-content:center; }
.fx .sf .sf-kick { font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.15; margin-bottom:.3em; }
.fx .sf .sf-kick .fl, .fx .sf .sf-unit .fl { display:block; white-space:nowrap; }
.fx .sf .sf-num { color:var(--accent); display:inline-block; transform-origin:0 70%; }
.fx .sf .sf-unit { font-family:var(--f-body); font-weight:800; color:var(--fg); margin-top:.3em; line-height:1.2; }
"""


def scan_field(X, cid, t, d, p):
    M.base(X)
    X.css("fx-sf", CSS)
    sk = M.skin(X)
    P = X.portrait
    rnd = random.Random(int(p.get("seed", 9)) * 7919 + 13)
    has_sub = bool(p.get("subject"))
    R = M.regions(X, p, has_sub, graphic_share=0.58, hero_ar=1.25, row="info")
    gx0, gy0, gx1, gy1 = R["g"]
    if R["side"]:
        pan = (gx0, gy0, gx1, gy1)
        info = R["side"]
    elif P:
        split = gy0 + (gy1 - gy0) * 0.58
        pan = (gx0, gy0, gx1, split)
        info = (gx0, split + 40, gx1, gy1)
    else:
        split = gx0 + (gx1 - gx0) * 0.62
        pan = (gx0, gy0, split, gy1)
        info = (split + 70, gy0, gx1, gy1)
    px0, py0, px1, py1 = pan
    pw = px1 - px0
    ph = py1 - py0
    inset = 34
    fw = pw - 2 * inset
    fh = ph - 2 * inset
    pitch = 13.0 if not P else 12.0
    cols = int(fw / pitch)
    rows = int(fh / pitch)
    while cols * rows > 4200:
        pitch += 1
        cols = int(fw / pitch)
        rows = int(fh / pitch)
    fx0 = (fw - cols * pitch) / 2
    fy0 = (fh - rows * pitch) / 2
    ratio = max(0.05, min(0.9, float(p.get("ratio", 0.38))))
    K = 28
    rm = []
    kp = []
    for k in range(K):
        rm.append([])
    square = sk["dot"] == "0"
    rr = pitch * 0.34
    for r in range(rows):
        for c in range(cols):
            if rnd.random() < 0.08:
                continue
            x = fx0 + c * pitch + pitch / 2
            y = fy0 + r * pitch + pitch / 2
            a = rnd.choice(("a1", "a1", "a2", "a3"))
            if square:
                el = f'<rect class="{a}" x="{x - rr:.1f}" y="{y - rr:.1f}" width="{2 * rr:.1f}" height="{2 * rr:.1f}"/>'
            else:
                el = f'<circle class="{a}" cx="{x:.1f}" cy="{y:.1f}" r="{rr:.1f}"/>'
            if rnd.random() < ratio:
                slice_k = min(K - 1, int(c / cols * K))
                rm[slice_k].append(el)
            else:
                kp.append(el)
    groups = f'<g class="kp">{"".join(kp)}</g>'
    for k in range(K):
        groups += f'<g class="rm s{k}">{"".join(rm[k])}</g>'
    svg = f'<svg class="sf-f" style="left:{inset}px; top:{inset}px" width="{fw:.0f}" height="{fh:.0f}">{groups}</svg>'
    rtl = p.get("direction") == "rtl"
    tag = p.get("tag", "")
    tag_html = ""
    if tag:
        X.used_text.update(tag)
        tag_html = f'<div class="mt-pill sf-tag">{X.rich(tag)}</div>'
    scan = f'<div class="sf-scan{" rtl" if rtl else ""}"><i class="gl"></i><i class="ln"></i>{tag_html}</div>'
    pan_cls = "mt-card sf-pan" + (" rule" if sk["panel"] == "rule" else "")
    panel = f'<div class="{pan_cls}" style="left:{px0:.0f}px; top:{py0:.0f}px; width:{pw:.0f}px; height:{ph:.0f}px">{svg}{scan}</div>'
    # info: kicker · counter · unit
    ix0, iy0, ix1, iy1 = info
    iw = ix1 - ix0
    ih = iy1 - iy0
    val_s = str(p.get("value", 0))
    steps = [(t, val_s)]
    num_html, sufs = M.stepper_html(X, steps)
    n_px = min(ih * 0.5, iw / max(1.0, len(val_s) * 0.62), 220)
    kick = p.get("kicker", "")
    unit = p.get("unit", "")
    k_html = ""
    if kick:
        k_px, k_lines, _ = M.fit_text(X, kick, iw, ih * 0.3, min(60, n_px * 0.42), 24, 2)
        k_html = f'<div class="sf-kick" style="font-size:{k_px:.0f}px">{k_lines}</div>'
    u_html = ""
    if unit:
        u_px, u_lines, _ = M.fit_text(X, unit, iw, ih * 0.25, min(46, n_px * 0.3), 22, 2)
        u_html = f'<div class="sf-unit" style="font-size:{u_px:.0f}px">{u_lines}</div>'
    info_html = (f'<div class="sf-info" style="left:{ix0:.0f}px; top:{iy0:.0f}px; width:{iw:.0f}px; height:{ih:.0f}px">'
                 f'{k_html}<div><span class="sf-num" style="font-size:{n_px:.0f}px">{num_html}</span></div>{u_html}</div>')
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=t + 0.3)
    mock = M.mock_tag(X, p, px1 - 80, py0 + 12)
    _clip(X, cid, t, d, M.wrap(X, sk, panel + info_html + subj + mock, "sf"), p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    col = M.colors(X, p)
    X.tw(f'tl.from("{s} .sf-pan", {{y:50, opacity:0, duration:0.55, ease:"{e}"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} svg.sf-f", {{opacity:0, scale:1.04, transformOrigin:"50% 50%", duration:0.5, ease:"power2.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .sf-info > *", {{x:-30, opacity:0, duration:0.5, ease:"{e}", stagger:0.1}}, {t + 0.3:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # the sweep
    t_s = t + 0.7
    t_e = t + d - min(1.0, d * 0.2)
    x_a = inset + fx0
    x_b = inset + fx0 + cols * pitch
    if rtl:
        x_a, x_b = x_b, x_a
    X.tw(f'tl.set("{s} .sf-scan", {{x:{x_a - (0 if not rtl else 0):.1f}, opacity:0}}, {t:.3f});')
    X.tw(f'tl.to("{s} .sf-scan", {{opacity:1, duration:0.15}}, {t_s - 0.15:.3f});')
    X.tw(f'tl.to("{s} .sf-scan", {{x:{x_b:.1f}, duration:{t_e - t_s:.2f}, ease:"none"}}, {t_s:.3f});')
    X.tw(f'tl.to("{s} .sf-scan", {{opacity:0, duration:0.25}}, {t_e:.3f});')
    if tag:
        X.tw(f'tl.from("{s} .sf-tag", {{y:20, opacity:0, duration:0.35, ease:"back.out(2)"}}, {t_s:.3f});')
    for k in range(K):
        kk = (K - 1 - k) if rtl else k
        frac = (kk + 0.5) / K
        when = t_s + (t_e - t_s) * frac
        X.tw(f'tl.to("{s} .rm.s{k}", {{keyframes:[{{fill:"{col["accent"]}", duration:0.06}}, {{opacity:0, duration:0.22, ease:"power2.in"}}]}}, {when - 0.04:.3f});')
    X.sfx(t_s, "whoosh")
    val, pre, suf, dec = M.split_num(val_s)
    js_f = f'(x)=>x.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})'
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .sf-num .n"); const f={js_f}; if(!el) return; '
         f'tl.to(o, {{v:{val}, duration:{t_e - t_s:.2f}, ease:"none", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {t_s:.3f});}})();')
    for k, sfx_ in enumerate(sufs):
        X.tw(f'tl.set("{s} .sf-num .sf[data-k=\'{k}\']", {{opacity:1}}, {t_e:.3f});')
    X.tw(f'tl.fromTo("{s} .sf-num", {{scale:1}}, {{keyframes:[{{scale:1.15, duration:0.1}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {t_e:.3f});')
    X.sfx(t_e, "hit")
    # after the sweep: the cleaned field settles
    X.tw(f'tl.to("{s} .kp", {{opacity:0.75, duration:0.5}}, {t_e + 0.1:.3f});')


FX = {"scan_field": scan_field}
