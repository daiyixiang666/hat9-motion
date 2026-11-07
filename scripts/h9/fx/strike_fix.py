"""删除线改口 (strike fix · the reference promo's 40 s「不是故意 ~~卡大家~~」): a line lands, then one phrase in it is
struck through and the correction is written in above it with an insert caret, like a proof correction; the
struck phrase sinks back. A designed strike per style (a solid bar, an ink brush, a strip of tape, a stepped pixel
bar, a hairline) — not the hand-drawn marker (that is scribble).

p: text ("真的不是故意~~卡大家~~") — ~~…~~ marks the phrase to strike · fix (the correction; optional) · kicker · sub
   (a small line under) · chip (a status chip on the subject, e.g. "群已满员") · at (when the strike lands)
   · subject | video | image (+ subject_focus, subject_start, subject_fit, subject_tag)
Adapts: short to long lines (fitted, up to 3 lines; the struck phrase never breaks), with or without a fix; with a
subject the line takes the free column (16:9) or the top of the frame above the subject card (9:16); with no subject
the line owns the frame and the correction is repeated in a margin note on a ruled right-hand margin.
Re-skins with the style: strike kind, highlight on the fix, chip shape, fonts and the style's ease.
"""
import re
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

CSS = r"""
.ki .sf-line { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.95; color:var(--fg); }
.ki .sf-x { position:relative; display:inline-block; white-space:nowrap; }
.ki .sf-x .sf-w { position:relative; display:inline-block; }
.ki .sf-x .sf-bar { position:absolute; left:-.08em; right:-.08em; top:50%; height:.13em; margin-top:-.03em; background:var(--k-alert); transform-origin:0 50%; }
.ki.sk-minimal .sf-x .sf-bar, .ki.sk-doc .sf-x .sf-bar { height:.05em; background:var(--fg); }
.ki.sk-poster .sf-x .sf-bar { height:.2em; margin-top:-.08em; background:var(--fg); }
.ki.sk-zine .sf-x .sf-bar { height:.42em; margin-top:-.2em; background:var(--k-ink); transform:rotate(-2deg); box-shadow:0 2px 0 rgba(0,0,0,.15); }
.ki.sk-ink .sf-x .sf-bar { height:.2em; margin-top:-.08em; background:var(--k-ink); border-radius:40% 10% 50% 8% / 60% 30% 70% 40%; filter:blur(.5px); opacity:.85; }
.ki.sk-sketch .sf-x .sf-bar { height:.1em; border-radius:999px; transform:rotate(-3deg); }
.ki.sk-pixel .sf-x .sf-bar { height:.16em; box-shadow:.06em .06em 0 var(--k-ink); }
.ki.sk-hud .sf-x .sf-bar, .ki.sk-screen .sf-x .sf-bar { height:.08em; box-shadow:0 0 12px var(--k-alert); }
.ki .sf-fix { position:absolute; left:50%; bottom:90%; transform:translateX(-50%); white-space:nowrap; font-size:.6em; line-height:1.1; color:var(--accent); }
.ki .sf-fix .k-hl { padding:0 .08em; }
.ki .sf-car { position:absolute; left:50%; bottom:76%; width:.44em; height:.24em; margin-left:-.22em; }
.ki .sf-car svg { width:100%; height:100%; overflow:visible; }
.ki .sf-car path { fill:none; stroke:var(--accent); stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
.ki .sf-sub { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); white-space:nowrap; }
.ki .sf-chip { color:var(--fg); background:var(--bg); box-shadow:0 0 0 3px var(--fg); }
.ki.sk-hud .sf-chip, .ki.sk-screen .sf-chip { box-shadow:0 0 0 1.5px var(--accent); color:var(--accent); }
.ki .sf-margin { position:absolute; border-left:3px solid var(--k-alert); padding-left:28px; }
.ki .sf-margin small { display:block; font:700 20px var(--k-kf); letter-spacing:.16em; color:var(--muted); text-transform:uppercase; margin-bottom:10px; }
.ki .sf-margin b { display:block; font-family:var(--f-display); font-weight:900; color:var(--accent); line-height:1.15; }
.ki .sf-margin s { display:block; font-family:var(--f-display); font-weight:700; color:var(--muted); text-decoration-thickness:.08em; text-decoration-color:var(--k-alert); margin-bottom:8px; }
.ki .sf-rules { position:absolute; background-image:linear-gradient(color-mix(in srgb, var(--fg) 9%, transparent) 2px, transparent 2px); }
"""

MARK = re.compile(r"~~(.+?)~~")


def strike_fix(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    text = str(p.get("text") or "这不是~~故意的~~")
    m = MARK.search(text)
    if not m:
        m = MARK.search(text + "~~" + "~~")
    pre = text[:m.start()] if m else text
    wrong = m.group(1) if m else ""
    post = text[m.end():] if m else ""
    fix = p.get("fix", "")
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    inner = []
    sub_rect = None
    if src:
        ar = K.subject_ar(X, src)
        if P:
            sy = y0 + ah * 0.4
            sh = K.low(X, p) - sy
            sw = min(aw * 0.9, max(aw * 0.62, sh * max(0.6, min(1.1, ar))))
            sx = x0 + (aw - sw) / 2
            tx, ty, tw, th = x0, y0 + 20, aw, sy - y0 - 70
        else:
            sr, tr = K.beside(X, p, sub_ar=min(1.1, max(0.62, ar)), side="right", sub_share=0.4)
            sx, sy, sw, sh = sr
            tx, ty, tw, th = tr[0], tr[1] + tr[3] * 0.1, tr[2], tr[3] * 0.8
        sub_rect = (sx, sy, sw, sh)
        inner.append(K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="sf-subj"))
    else:
        if P:
            tx, ty, tw, th = x0, y0 + ah * 0.06, aw, ah * 0.56
        else:
            tx, ty, tw, th = x0 + 20, y0 + ah * 0.1, aw * 0.64, ah * 0.8
    kick = p.get("kicker")
    if kick:
        ty += 50
        th -= 50
    plain = pre + wrong + post
    lh = 1.95
    mx = 150
    if src:
        mx = 140 if P else 130
    f = FT.fit_text(plain, tw * 0.94, th * 0.84, mx, 40, lh=lh, max_lines=3)
    px = f.px
    n_lines = f.n
    block_h = n_lines * px * lh
    top = ty + (th - block_h) / 2
    if kick:
        X.used_text.update(str(kick))
        inner.append(f'<div class="k-kick sf-k" style="left:{tx:.0f}px; top:{top - 30:.0f}px">{X.rich(kick)}</div>')
    X.used_text.update(plain + str(fix))
    fix_html = ""
    if fix:
        fix_html = (f'<span class="sf-fix">{K.hl_html(X, "*" + str(fix) + "*")}</span>'
                    f'<span class="sf-car"><svg viewBox="0 0 20 12"><path d="M2 11 L10 2 L18 11"/></svg></span>')
    line = (f'<div class="sf-line" style="left:{tx:.0f}px; top:{top:.0f}px; width:{tw:.0f}px; font-size:{px}px">'
            f'<span class="sf-pre">{K.hl_html(X, pre)}</span><span class="sf-x"><span class="sf-w">{X.rich(wrong)}</span><i class="sf-bar"></i>{fix_html}</span>'
            f'<span class="sf-post">{K.hl_html(X, post)}</span></div>')
    inner.append(line)
    sub = p.get("sub")
    if sub:
        sp, sl = K.fit(sub, tw, 40, 30 if not P else 34, 18, max_lines=1)
        X.used_text.update(str(sub))
        inner.append(f'<div class="sf-sub" style="left:{tx:.0f}px; top:{top + block_h + 6:.0f}px; font-size:{sp}px">{X.rich(sl[0] if sl else sub)}</div>')
    chip = p.get("chip")
    if chip:
        X.used_text.update(str(chip))
        cpx = 30 if not P else 34
        cw = (FT.width(str(chip)) + 1.6) * cpx + 32
        if sub_rect:
            cxp = sub_rect[0] + (sub_rect[2] - cw) / 2
            cyp = sub_rect[1] - cpx * 1.2 - 26
        else:
            cxp = tx
            cyp = top - cpx * 2.6
        inner.append(f'<div class="k-chip sf-chip" style="left:{cxp:.0f}px; top:{cyp:.0f}px; font-size:{cpx}px">{K.ICON_LOCK}{X.rich(chip)}</div>')
    if not src:
        # the ruled margin with the correction repeated, as in a proof
        if P:
            mxp, myp, mw, mh = x0 + 10, y0 + ah * 0.68, aw - 20, ah * 0.28
        else:
            mxp, myp, mw, mh = x0 + aw * 0.72, y0 + ah * 0.16, aw * 0.26, ah * 0.66
        inner.append(f'<div class="sf-rules" style="left:{mxp:.0f}px; top:{myp:.0f}px; width:{mw:.0f}px; height:{mh:.0f}px; background-size:100% {64 if not P else 72}px"></div>')
        mpx = min(64, (mw - 40) / max(1.0, FT.width(str(fix or wrong))))
        X.used_text.update("CORRECTION · 改")
        right = ""
        if fix:
            right = f'<b style="font-size:{mpx:.0f}px">{X.rich(fix)}</b>'
        inner.append(f'<div class="sf-margin" style="left:{mxp:.0f}px; top:{myp + 20:.0f}px; width:{mw:.0f}px"><small>Correction · 改</small>'
                     f'<s style="font-size:{mpx * 0.6:.0f}px">{X.rich(wrong)}</s>{right}</div>')
    X.css("fx-strike-fix", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    if src:
        K.subject_in(X, f"{s_} .sf-subj", t, e)
        K.subject_drift(X, f"{s_} .sf-subj > img, {s_} .sf-subj > video, {s_} .sf-subj .k-pin > *", t, d)
    if kick:
        X.tw(f'tl.fromTo("{s_} .sf-k", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -5% 0 0)", duration:0.4, ease:"power2.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s_} .sf-line", {{y:50, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(-40% -5% -20% -5%)", duration:0.6, ease:"{e}", immediateRender:true}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")
    t_x = K.U.when(X, p.get("at"), t, t + min(1.3, d * 0.34))
    if X.M.get("ease", "").startswith("steps"):
        bar_ease = X.M["ease"]
    else:
        bar_ease = "power2.inOut"
    X.tw(f'tl.fromTo("{s_} .sf-bar", {{scaleX:0}}, {{scaleX:1, duration:0.36, ease:"{bar_ease}", immediateRender:true}}, {t_x:.3f});')
    X.tw(f'tl.to("{s_} .sf-w", {{opacity:0.42, y:6, duration:0.3}}, {t_x + 0.3:.3f});')
    X.sfx(t_x, "whoosh_soft")
    if fix:
        t_f = t_x + 0.55
        X.tw(f'tl.fromTo("{s_} .sf-car path", {{strokeDasharray:"40 40", strokeDashoffset:40}}, {{strokeDashoffset:0, duration:0.25, ease:"power2.out", immediateRender:true}}, {t_f:.3f});')
        X.tw(f'tl.fromTo("{s_} .sf-fix", {{y:30, opacity:0, scale:0.7}}, {{y:0, opacity:1, scale:1, duration:0.45, ease:"back.out(2)", immediateRender:true}}, {t_f + 0.1:.3f});')
        K.hl_tween(X, f"{s_} .sf-fix", t_f + 0.5, k)
        X.sfx(t_f + 0.1, "pop")
    hl_any = "*" in (pre + post)
    if hl_any:
        K.hl_tween(X, f"{s_} .sf-pre, {s_} .sf-post", t + 0.7, k)
    if sub:
        X.tw(f'tl.fromTo("{s_} .sf-sub", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.6, ease:"none", immediateRender:true}}, {t_x + 1.0:.3f});')
    if chip:
        X.tw(f'tl.fromTo("{s_} .sf-chip", {{y:-30, scale:0.6, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.45, ease:"back.out(2.2)", immediateRender:true}}, {t + 0.5:.3f});')
        X.sfx(t + 0.5, "pop")
    if not src:
        X.tw(f'tl.fromTo("{s_} .sf-rules", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:0.7, ease:"power2.out", immediateRender:true}}, {t + 0.2:.3f});')
        X.tw(f'tl.fromTo("{s_} .sf-margin small", {{opacity:0, x:-20}}, {{opacity:1, x:0, duration:0.4, immediateRender:true}}, {t + 0.4:.3f});')
        X.tw(f'tl.fromTo("{s_} .sf-margin s", {{opacity:0, x:-20}}, {{opacity:1, x:0, duration:0.4, immediateRender:true}}, {t_x + 0.2:.3f});')
        if fix:
            X.tw(f'tl.fromTo("{s_} .sf-margin b", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.5, ease:"{e}", immediateRender:true}}, {t_x + 0.8:.3f});')


FX = {"strike_fix": strike_fix}
