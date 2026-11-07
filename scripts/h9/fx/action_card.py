"""截图页 (action card · the reference promo's end page at 127–134 s): the page viewers screenshot — a title
("截图这一页，交给你的 AI 助手"), a URL typing itself into an input box, 2–6 numbered steps lighting in one by one, a
row of thumbnails, then a「截图此页」stamp lands with a brief frame flash and shutter brackets closing on the card.

p: title ("截图这一页，|交给你的 *AI* 助手") · kicker · url · label ("给 AI 的开始说明") · steps [..] (2–6) · thumbs
   [images] (0–8; none → skeleton tiles) · note (a footer line) · stamp ("截图此页"; false = none) · stamp_at
   · subject | video | image (+ subject_focus, subject_start, subject_fit, subject_tag)
Adapts: 2–6 steps, long steps (fitted to one line, then two), long URLs (scrolled in the box as they type), 0–8
thumbs; 16:9: the card in two columns (title + URL | steps + thumbs), sized to its content and centred;
one; 9:16: one tall column filling the frame. The subject rides as a round avatar in the card's corner.
Re-skins with the style: card colour, radius, border, shadow, input box, step numerals (f-num), stamp shape, the
style's ease.
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
U = K.U

CSS = r"""
.ki .ac-card { overflow:hidden; }
.ki .ac-kick { position:absolute; font:700 20px var(--k-kf); letter-spacing:.16em; text-transform:uppercase; color:color-mix(in srgb, var(--card-fg) 52%, transparent); white-space:nowrap; }
.ki .ac-title { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.22; color:var(--card-fg); }
.ki .ac-title .sl { display:block; white-space:nowrap; }
.ki .ac-in { position:absolute; display:flex; align-items:center; gap:14px; padding:0 22px; border-radius:calc(var(--k-rs) * .5 + 6px); overflow:hidden; white-space:nowrap;
  box-shadow:inset 0 0 0 3px var(--accent); background:color-mix(in srgb, var(--accent) 6%, var(--card)); color:var(--accent); }
.ki.sk-pixel .ac-in, .ki.sk-poster .ac-in, .ki.sk-zine .ac-in { border-radius:0; }
.ki .ac-in .ac-url { font-family:var(--f-mono, monospace); font-weight:700; color:var(--card-fg); }
.ki .ac-lab { position:absolute; font-family:var(--f-body); font-weight:700; color:color-mix(in srgb, var(--card-fg) 55%, transparent); white-space:nowrap; }
.ki .ac-st { position:absolute; display:flex; align-items:baseline; gap:.7em; font-family:var(--f-body); font-weight:700; color:var(--card-fg); white-space:nowrap; }
.ki .ac-st i { font-style:normal; font-family:var(--f-num, var(--f-mono, monospace)); font-weight:900; color:var(--accent); min-width:1.6em; }
.ki .ac-th { position:absolute; overflow:hidden; border-radius:calc(var(--k-rs) * .5 + 8px); background:color-mix(in srgb, var(--card-fg) 8%, var(--card));
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 12%, transparent); }
.ki.sk-pixel .ac-th, .ki.sk-poster .ac-th, .ki.sk-zine .ac-th { border-radius:0; }
.ki .ac-th img { width:100%; height:100%; object-fit:cover; display:block; }
.ki .ac-th.first { box-shadow:0 0 0 4px var(--accent); }
.ki .ac-th .ac-sk { position:absolute; left:12%; right:12%; height:6%; border-radius:4px; background:color-mix(in srgb, var(--card-fg) 18%, transparent); }
.ki .ac-note { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--card-fg); white-space:nowrap; }
.ki .ac-note b { color:var(--accent); }
.ki .ac-stamp { color:var(--accent); border-color:var(--accent); background:color-mix(in srgb, var(--card) 88%, transparent); }
.ki .ac-av { position:absolute; overflow:hidden; border-radius:50%; box-shadow:0 0 0 4px var(--accent); }
.ki .ac-av img, .ki .ac-av video { width:100%; height:100%; object-fit:cover; display:block; }
"""


def action_card(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    steps = list(FT.as_list(p.get("steps") or ["打开上面的地址", "选一个喜欢的模板", "按 README 制作"]))[:6]
    thumbs = list(FT.as_list(p.get("thumbs") or []))[:8]
    ns = len(steps)
    inner = []
    # ---- card + optional subject
    if P:
        cx, cy, cw, ch = x0, y0, aw, ah
    else:
        cx, cy, cw, ch = x0 + aw * 0.04, y0, aw * 0.92, ah
    pad = 50 if not P else 52
    iw = cw - 2 * pad
    two = not P
    if two:
        colw = (iw - 56) / 2
        lx, rx = pad, pad + colw + 56
    else:
        colw = iw
        lx, rx = pad, pad
    parts = []
    yl = pad
    kick = p.get("kicker", "SCREENSHOT THIS PAGE · HAND IT TO YOUR AI ASSISTANT")
    kf = FT.fit_text(str(kick), colw if two else iw - 120, 30, 20, 13, max_lines=1, mono=True, ls=0.16)
    X.used_text.update(str(kick))
    parts.append(f'<div class="ac-kick" style="left:{lx:.0f}px; top:{yl:.0f}px; font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else kick)}</div>')
    yl += 52
    title = p.get("title", "截图这一页，|交给你的 *AI* 助手")
    tmax = 88 if not P else 96
    f = FT.fit_text(title, colw, ch * 0.3, tmax, 36, lh=1.22, max_lines=3)
    ls = ""
    for ln in f.lines:
        ls += f'<span class="sl">{K.hl_html(X, ln)}</span>'
    parts.append(f'<div class="ac-title" style="left:{lx:.0f}px; top:{yl:.0f}px; font-size:{f.px}px">{ls}</div>')
    yl += f.n * f.px * 1.22 + 30
    url = str(p.get("url", "github.com/daiyixiang666/hat9-motion"))
    in_h = 84 if not P else 92
    upx = 30 if not P else 34
    room = (colw - 22 * 2 - 50) / upx
    X.used_text.update(url)
    url_w = FT.width(url, mono=True) * upx
    shift = max(0.0, url_w - (colw - 22 * 2 - 50))
    parts.append(f'<div class="ac-in" style="left:{lx:.0f}px; top:{yl:.0f}px; width:{colw:.0f}px; height:{in_h}px; font-size:{upx}px">{K.ICON_LINK}'
                 f'<span class="ac-url">{U.typed(X, url)}<i class="ui-caret ac-car"></i></span></div>')
    yl += in_h + 34
    # right column (or continuing down in 9:16)
    yr = pad + 8 if two else yl
    label = p.get("label", "给 AI 的开始说明")
    if label:
        X.used_text.update(str(label))
        parts.append(f'<div class="ac-lab" style="left:{rx:.0f}px; top:{yr:.0f}px; font-size:{24 if not P else 28}px">{X.rich(label)}</div>')
        yr += 50 if not P else 58
    note = p.get("note")
    thumbs_n = len(thumbs) if thumbs else (6 if not P else 5)
    # how much room the steps get
    if P:
        th_h = min(300.0, (colw - 14 * (thumbs_n - 1)) / thumbs_n / 0.62)
    else:
        th_h = min(250.0, (colw - 12 * (thumbs_n - 1)) / thumbs_n / 0.62)
    note_h = 50 if note else 0
    steps_room = ch - pad - yr - th_h - 40 - note_h
    spx = 34 if not P else 40
    gap_k = 1.9
    for s in steps:
        fs = FT.fit_text(str(s), colw - spx * 2.4, spx * 1.4, spx, 24 if P else 22, max_lines=1)
        if fs.px < spx:
            spx = fs.px
    if ns * spx * gap_k > steps_room:
        spx = max(22, steps_room / (ns * gap_k))
    for i in range(ns):
        fs = FT.fit_text(str(steps[i]), colw - spx * 2.4, spx * 1.4, spx, spx, max_lines=1)
        X.used_text.update(str(steps[i]) + "0123456789")
        txt = fs.lines[0] if fs.lines else steps[i]
        parts.append(f'<div class="ac-st" data-i="{i}" style="left:{rx:.0f}px; top:{yr:.0f}px; font-size:{spx:.0f}px"><i>{i + 1:02d}</i>{K.hl_html(X, txt)}</div>')
        yr += spx * gap_k
    yr += 18
    tw = th_h * 0.62
    gap = (colw - thumbs_n * tw) / max(1, thumbs_n - 1) if thumbs_n > 1 else 0
    for j in range(thumbs_n):
        tx = rx + j * (tw + gap)
        cls = "ac-th first" if j == 0 else "ac-th"
        if thumbs:
            body = f'<img src="{X.asset(thumbs[j])}" alt="">'
        else:
            body = (f'<i class="ac-sk" style="top:14%; width:auto"></i><i class="ac-sk" style="top:26%; right:30%"></i>'
                    f'<i class="ac-sk" style="top:44%; height:30%; border-radius:8px"></i>')
        parts.append(f'<div class="{cls}" data-j="{j}" style="left:{tx:.0f}px; top:{yr:.0f}px; width:{tw:.0f}px; height:{th_h:.0f}px">{body}</div>')
    yr += th_h + 22
    if note:
        npx, nl = K.fit(note, colw, 40, 24 if not P else 28, 16, max_lines=1)
        X.used_text.update(str(note))
        parts.append(f'<div class="ac-note" style="left:{rx:.0f}px; top:{yr:.0f}px; font-size:{npx}px">{K.hl_html(X, nl[0] if nl else note)}</div>')
    if src:
        av = 124 if P else 132
        media = ""
        if FT.is_video(src):
            media = K.S.vtag(X, src, t, d, av, av, float(p.get("subject_start", 0)), p.get("subject_focus"))
        else:
            media = f'<img src="{X.asset(src)}" alt="">'
        if two:
            apos = f"left:{lx + 6:.0f}px; top:{yl + 6:.0f}px"
        else:
            apos = f"right:{pad:.0f}px; top:{pad - 6:.0f}px"
        parts.append(f'<div class="ac-av" style="{apos}; width:{av}px; height:{av}px">{media}</div>')
    stamp = p.get("stamp", "截图此页")
    if stamp:
        X.used_text.update(str(stamp))
        spx_ = 44 if not P else 50
        sw_ = (FT.width(str(stamp)) + 1.2) * spx_ + 40
        if two:
            sx_ = lx + 6 + (160 if src else 0)
            sy_ = yl + 30
        else:
            sx_ = cw - pad - sw_ + 10
            sy_ = yr - th_h * 0.75 - 22
        parts.append(f'<div class="k-stamp ac-stamp" style="left:{sx_:.0f}px; top:{sy_:.0f}px; font-size:{spx_}px; transform:rotate(-8deg)">{K.ICON_OK}{X.rich(stamp)}</div>')
    used = yr + 60
    if two and yl + 140 > used:
        used = yl + 140
    if used < ch:
        cy = cy + (ch - used) / 2
        ch = used
    inner.append(f'<div class="k-card ac-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">{"".join(parts)}</div>')
    inner.append(K.brackets(cx - 24, cy - 18, cw + 48, ch + 36, cls="ac-brk"))
    inner.append('<div class="k-flash ac-flash"></div>')
    X.css("fx-action-card", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    X.tw(f'tl.fromTo("{s_} .ac-card", {{y:90, opacity:0, scale:0.96}}, {{y:0, opacity:1, scale:1, duration:0.6, ease:"{e}", immediateRender:true}}, {t:.3f});')
    X.tw(f'tl.set("{s_} .ac-brk", {{opacity:0}}, {t:.3f});')
    if src:
        X.tw(f'tl.fromTo("{s_} .ac-av", {{scale:0, rotation:-30}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2)", immediateRender:true}}, {t + 0.45:.3f});')
    X.sfx(t, "whoosh_soft")
    X.tw(f'tl.fromTo("{s_} .ac-kick", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -3% 0 0)", duration:0.5, ease:"power2.out", immediateRender:true}}, {t + 0.2:.3f});')
    K.rise(X, f"{s_} .ac-title", t + 0.25, e, dist=40, dur=0.55)
    K.hl_tween(X, f"{s_} .ac-title", t + 0.8, k)
    X.tw(f'tl.fromTo("{s_} .ac-in", {{scaleX:0.2, opacity:0, transformOrigin:"0% 50%"}}, {{scaleX:1, opacity:1, duration:0.45, ease:"power3.out", immediateRender:true}}, {t + 0.5:.3f});')
    cps = max(18.0, len(url) / max(0.8, d * 0.2))
    t_type = t + 0.85
    end_type = U.type_in(X, f"{s_} .ac-url", t_type, len(url), cps=cps, caret=f"{s_} .ac-car", until=t + d)
    if shift > 1:
        X.tw(f'tl.fromTo("{s_} .ac-url", {{x:0}}, {{x:{-shift:.0f}, duration:{max(0.3, end_type - t_type) * 0.5:.2f}, ease:"none", immediateRender:false}}, {t_type + (end_type - t_type) * 0.5:.3f});')
    X.sfx(t_type, "type")
    if label:
        X.tw(f'tl.fromTo("{s_} .ac-lab", {{opacity:0, x:-16}}, {{opacity:1, x:0, duration:0.35, immediateRender:true}}, {end_type + 0.05:.3f});')
    t_stamp = U.when(X, p.get("stamp_at"), t, t + d - 1.0)
    first = end_type + 0.25
    last = max(first + 0.3 * ns, t_stamp - 1.0 - (0.3 if thumbs_n else 0))
    st_t = K.cues(X, p, "at", t, d, ns)
    auto = U.spread(ns, first, last)
    given = p.get("at") or []
    for i in range(ns):
        ti = auto[i]
        if i < len(given):
            ti = st_t[i]
        X.tw(f'tl.fromTo("{s_} .ac-st[data-i=\\"{i}\\"]", {{x:-30, opacity:0}}, {{x:0, opacity:1, duration:0.4, ease:"{e}", immediateRender:true}}, {ti:.3f});')
        X.tw(f'tl.fromTo("{s_} .ac-st[data-i=\\"{i}\\"] i", {{scale:1.8}}, {{scale:1, duration:0.4, ease:"back.out(2)", immediateRender:true}}, {ti:.3f});')
        X.sfx(ti, "tick")
    t_th = last + 0.35
    X.tw(f'tl.fromTo("{s_} .ac-th", {{y:60, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"{e}", stagger:0.06, immediateRender:true}}, {t_th:.3f});')
    if note:
        X.tw(f'tl.fromTo("{s_} .ac-note", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.5, ease:"none", immediateRender:true}}, {t_th + 0.3:.3f});')
    if stamp:
        X.tw(f'tl.fromTo("{s_} .ac-flash", {{opacity:0}}, {{keyframes:[{{opacity:0.85, duration:0.05}}, {{opacity:0, duration:0.25}}], immediateRender:false}}, {t_stamp:.3f});')
        X.tw(f'tl.set("{s_} .ac-brk", {{opacity:1}}, {t_stamp:.3f});')
        corners = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        for j in range(4):
            X.tw(f'tl.fromTo("{s_} .ac-brk i:nth-child({j + 1})", {{x:{corners[j][0] * 60}, y:{corners[j][1] * 60}}}, {{x:0, y:0, duration:0.35, ease:"expo.out", immediateRender:false}}, {t_stamp:.3f});')
        X.tw(f'tl.fromTo("{s_} .ac-card", {{scale:1}}, {{keyframes:[{{scale:0.975, duration:0.06}}, {{scale:1, duration:0.3, ease:"back.out(2)"}}], immediateRender:false}}, {t_stamp:.3f});')
        X.tw(f'tl.fromTo("{s_} .ac-stamp", {{scale:2.4, opacity:0, rotation:-20}}, {{scale:1, opacity:1, rotation:-8, duration:0.3, ease:"power4.in", immediateRender:true}}, {t_stamp + 0.1:.3f});')
        X.sfx(t_stamp, "shutter")
        X.sfx(t_stamp + 0.38, "slam")


FX = {"action_card": action_card}
