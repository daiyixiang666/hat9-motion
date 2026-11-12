"""重点信息卡 (key card · the KEY INFO card layout seen in an open-source portrait-template promo): the subject holds the frame, then a KEY INFO
card zooms out from behind it inside four corner brackets while the subject blurs and dims; the card's value swaps
through a sequence — 174 → 18 → 15 — one per cue, each with its own caption, a page counter ticking in the
corner and the brackets snapping in on every swap.

p: values [{v: "174", cap: "个动效 · 开源竖屏模板", at: "@词"}] (1–6; strings work) · kicker (default
   "KEY INFO · 重要信息") · at (when the card comes out; default 0.7 s) · subject | video | image (+ subject_focus,
   subject_start, subject_fit, subject_tag) · layout full | card (default: full for wide footage, card otherwise)
Adapts: 1–6 values, numbers or words, long captions (fitted, 2 lines); the value size is set once for the widest
value so the card never resizes; with no subject the card comes out of a fanned deck of blank cards on a dot grid.
16:9 (card centred over the subject) and 9:16 (card in the upper half, the subject card filling the lower half).
Re-skins with the style: card colour, radius, border and shadow, bracket colour, number font, the style's ease.
"""
from h9 import fit as FT
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


K = _load("_kinfo")
SS = _load("side_stat")

CSS = r"""
.ki .kc-card { overflow:hidden; }
.ki .kc-kick { position:absolute; font:700 22px var(--k-kf); letter-spacing:.18em; text-transform:uppercase; color:color-mix(in srgb, var(--card-fg) 55%, transparent); white-space:nowrap; }
.ki .kc-pg { position:absolute; font:800 22px var(--f-num, var(--k-kf)); color:var(--k-on); background:var(--accent); padding:4px 12px; border-radius:var(--k-rs); white-space:nowrap; }
.ki .kc-pg .kc-d { display:inline-block; height:1.2em; overflow:hidden; vertical-align:bottom; }
.ki .kc-pg .kc-d i { display:block; font-style:normal; height:1.2em; line-height:1.2em; }
.ki .kc-v { position:absolute; left:0; top:0; width:100%; }
.ki .kc-num { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; letter-spacing:-.035em; white-space:nowrap; color:var(--card-fg); }
.ki .kc-v:first-child .kc-num { color:var(--accent); }
.ki .kc-num .kc-u { font-family:var(--f-display); letter-spacing:0; font-size:.42em; margin-left:.12em; }
.ki .kc-cap { font-family:var(--f-display); font-weight:800; color:var(--card-fg); line-height:1.25; margin-top:.5em; }
.ki .kc-cap .sl { display:block; white-space:nowrap; }
.ki .kc-rule { position:absolute; height:2px; background:color-mix(in srgb, var(--card-fg) 14%, transparent); }
.ki .kc-deck { position:absolute; background:color-mix(in srgb, var(--card) 70%, var(--bg)); border-radius:var(--k-r); box-shadow:var(--k-sh); opacity:.7; }
.ki .kc-dots { position:absolute; inset:0; background-image:radial-gradient(color-mix(in srgb, var(--fg) 22%, transparent) 2px, transparent 2.5px); background-size:44px 44px; opacity:.6; }
"""


def key_card(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    raw = list(p.get("values") or [{"v": p.get("value", "174"), "cap": p.get("cap", "")}])[:6]
    vals = []
    for it in raw:
        if not isinstance(it, dict):
            it = {"v": it}
        vals.append(it)
    n = len(vals)
    ar = K.subject_ar(X, src) if src else 1.0
    layout = p.get("layout") or ("full" if (src and ar > 1.2) else "card")
    inner = []
    # ---- the card's size: the widest value at one size
    if P:
        cw = aw
    else:
        cw = min(aw * 0.56, 1000)
    pad = 54 if not P else 50
    vmax = 230 if not P else 300
    vpx = vmax
    for it in vals:
        em = FT.width(str(it.get("v", ""))) + (FT.width(str(it.get("unit", ""))) * 0.42 + 0.12 if it.get("unit") else 0)
        px = (cw - 2 * pad) * 0.96 / max(1.0, em)
        if px < vpx:
            vpx = px
    cap_px = 40 if not P else 52
    cap_lines = 1
    for it in vals:
        if it.get("cap"):
            f = FT.fit_text(str(it["cap"]), cw - 2 * pad, cap_px * 2.6, cap_px, 26, lh=1.25, max_lines=2)
            if f.n > cap_lines:
                cap_lines = f.n
            if f.px < cap_px:
                cap_px = f.px
    kick_h = 60
    val_h = vpx * 1.02 + cap_px * 1.25 * cap_lines + cap_px * 0.5
    ch = pad + kick_h + val_h + pad * 0.8
    cx = x0 + (aw - cw) / 2
    if P and src and layout != "full":
        cy = y0 + ah * 0.04
    elif P:
        cy = y0 + (ah - ch) / 2
    else:
        cy = y0 + (ah - ch) / 2 - ah * 0.03
    # ---- the subject
    if src:
        if layout == "full":
            inner.append(K.subject(X, p, 0, 0, X.W, X.H, t, d, k, cls="kc-subj", full=True))
            inner.append('<div class="k-scrim kc-dim" style="background:rgba(0,0,0,.18)"></div>')
        else:
            if P:
                sw = aw * 0.72
                sy = cy + ch * 0.55
                sh = K.low(X, p) - sy
            else:
                sh = ah * 0.86
                sw = min(aw * 0.36, sh * max(0.6, min(1.1, ar)))
                sy = y0 + (ah - sh) / 2
            sx = x0 + (aw - sw) / 2
            inner.append(K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="kc-subj"))
    else:
        inner.append('<div class="kc-dots"></div>')
        for j in range(2):
            rot = -5 + j * 9
            off = 26 + j * 22
            inner.append(f'<div class="kc-deck" data-j="{j}" style="left:{cx + off:.0f}px; top:{cy + off * 0.6:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; transform:rotate({rot}deg)"></div>')
    # ---- the card
    kick = p.get("kicker", "KEY INFO · 重要信息")
    X.used_text.update(str(kick) + "0123456789/ ")
    vh = []
    for i in range(n):
        it = vals[i]
        v = str(it.get("v", ""))
        X.used_text.update(v)
        unit = ""
        if it.get("unit"):
            X.used_text.update(str(it["unit"]))
            unit = f'<span class="kc-u">{X.rich(it["unit"])}</span>'
        pre, digits, suf, num = SS._parse(v)
        if digits is not None:
            num_html = f'{X.rich(pre)}<span class="kc-n" data-n="{i}">{digits}</span>{X.rich(suf)}'
        else:
            num_html = X.rich(v)
        cap = ""
        if it.get("cap"):
            f = FT.fit_text(str(it["cap"]), cw - 2 * pad, cap_px * 2.6, cap_px, cap_px, lh=1.25, max_lines=2)
            X.used_text.update(str(it["cap"]))
            ls = ""
            for ln in f.lines:
                ls += f'<span class="sl">{K.hl_html(X, ln)}</span>'
            cap = f'<div class="kc-cap" style="font-size:{cap_px}px">{ls}</div>'
        vh.append(f'<div class="kc-v" data-i="{i}"><div class="kc-num" style="font-size:{vpx:.0f}px">{num_html}{unit}</div>{cap}</div>')
    room = cw - 2 * pad - (130 if n > 1 else 0)
    kf = FT.fit_text(str(kick), room, 34, 26 if P else 22, 14, max_lines=1, mono=True, ls=0.18)
    kick_px = kf.px
    kick_txt = kf.lines[0] if kf.lines else kick
    pg = ""
    if n > 1:
        digs = ""
        for i in range(n):
            digs += f"<i>{i + 1}</i>"
        pg = f'<div class="kc-pg" style="right:{pad:.0f}px; top:{pad - 6:.0f}px"><span class="kc-d">{digs}</span> / {n}</div>'
    card = (f'<div class="k-card kc-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">'
            f'<div class="kc-kick" style="left:{pad:.0f}px; top:{pad:.0f}px; font-size:{kick_px}px">{X.rich(kick_txt)}</div>{pg}'
            f'<i class="kc-rule" style="left:{pad:.0f}px; right:{pad:.0f}px; top:{pad + 42:.0f}px"></i>'
            f'<div class="kc-vals" style="position:absolute; left:{pad:.0f}px; right:{pad:.0f}px; top:{pad + kick_h:.0f}px; height:{val_h:.0f}px; overflow:hidden">{"".join(vh)}</div></div>')
    inner.append(card)
    m = 30
    inner.append(K.brackets(cx - m, cy - m, cw + 2 * m, ch + 2 * m, cls="kc-brk"))
    X.css("fx-key-card", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    t_out = K.U.when(X, p.get("at"), t, t + min(0.8, d * 0.18))
    if src:
        K.subject_in(X, f"{s_} .kc-subj", t, e, full=(layout == "full"))
        msel = f"{s_} .kc-subj > img, {s_} .kc-subj > video, {s_} .kc-subj .k-pin > *"
        X.tw(f'tl.to("{msel}", {{filter:"blur(14px) brightness(.62)", scale:1.08, duration:0.6, ease:"power2.inOut"}}, {t_out:.3f});')
        X.tw(f'tl.to("{s_} .kc-subj", {{scale:0.94, duration:0.6, ease:"power2.inOut"}}, {t_out:.3f});')
    else:
        X.tw(f'tl.fromTo("{s_} .kc-deck", {{scale:0.6, opacity:0, rotation:0}}, {{scale:1, opacity:0.7, duration:0.55, ease:"{e}", stagger:0.08, immediateRender:true}}, {t_out - 0.2:.3f});')
        X.tw(f'tl.fromTo("{s_} .kc-dots", {{opacity:0}}, {{opacity:0.6, duration:0.6}}, {t:.3f});')
    # the card zooms out from behind the subject (from the frame centre, small), then breathes
    X.tw(f'tl.fromTo("{s_} .kc-card", {{scale:0.35, y:{ch * 0.5:.0f}, opacity:0}}, {{scale:1, y:0, opacity:1, duration:0.62, ease:"{e}", immediateRender:true}}, {t_out:.3f});')
    X.tw(f'tl.fromTo("{s_} .kc-card", {{scale:1}}, {{scale:1.025, duration:{max(0.5, t + d - t_out - 0.62):.2f}, ease:"none", immediateRender:false}}, {t_out + 0.62:.3f});')
    X.sfx(t_out, "whoosh")
    corners = ((-1, -1), (1, -1), (-1, 1), (1, 1))
    for j in range(4):
        dx = corners[j][0] * 90
        dy = corners[j][1] * 70
        X.tw(f'tl.fromTo("{s_} .kc-brk i:nth-child({j + 1})", {{x:{dx}, y:{dy}, opacity:0}}, {{x:0, y:0, opacity:1, duration:0.5, ease:"expo.out", immediateRender:true}}, {t_out + 0.18:.3f});')
    X.sfx(t_out + 0.2, "click")
    times = []
    first = t_out + 0.3
    auto = K.U.spread(n, first, t + d * 0.8) if n > 1 else [first]
    fixed = []
    say = []
    for i in range(n):
        v_at = vals[i].get("at")
        fixed.append(v_at is not None)
        say.append([str(vals[i].get("v", "")), str(vals[i].get("cap", ""))])
        if i == 0 and v_at is None:
            times.append(first)
            continue
        times.append(K.U.when(X, v_at, t, auto[i]))
    times = K.U.follow(X, say, first, t + d - first, times, fixed, gap=0.7)    # never before the card is out
    for i in range(1, n):
        if times[i] < times[i - 1] + 0.7:
            times[i] = times[i - 1] + 0.7
    for i in range(n):
        ti = times[i]
        sel = f'{s_} .kc-v[data-i=\\"{i}\\"]'
        if i == 0:
            X.tw(f'tl.fromTo("{sel}", {{y:60, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"{e}", immediateRender:true}}, {ti:.3f});')
        else:
            psel = f'{s_} .kc-v[data-i=\\"{i - 1}\\"]'
            X.tw(f'tl.to("{psel}", {{y:-90, opacity:0, duration:0.3, ease:"power3.in"}}, {ti - 0.15:.3f});')
            X.tw(f'tl.fromTo("{sel}", {{y:110, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"{e}", immediateRender:true}}, {ti + 0.08:.3f});')
            X.tw(f'tl.to("{s_} .kc-pg .kc-d i", {{yPercent:{-100 * i}, duration:0.35, ease:"power3.inOut"}}, {ti:.3f});')
            for j in range(4):
                dx = corners[j][0] * 22
                dy = corners[j][1] * 22
                X.tw(f'tl.fromTo("{s_} .kc-brk i:nth-child({j + 1})", {{x:{dx}, y:{dy}}}, {{x:0, y:0, duration:0.4, ease:"back.out(3)", immediateRender:false}}, {ti:.3f});')
            X.sfx(ti, "whoosh_soft")
        pre, digits, suf, num = SS._parse(str(vals[i].get("v", "")))
        if digits is not None and num >= 10:
            SS._count_js(X, f'{s_} .kc-n[data-n=\\"{i}\\"]', round(num * 0.55), num, digits, ti + 0.05, 0.6)
        if vals[i].get("cap"):
            X.tw(f'tl.fromTo("{sel} .kc-cap", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.45, ease:"power2.out", immediateRender:true}}, {ti + 0.3:.3f});')
        if "*" in str(vals[i].get("cap", "")):
            K.hl_tween(X, sel, ti + 0.7, k)


FX = {"key_card": key_card}
