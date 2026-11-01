"""Vlog 式口播 (talking head with stickers and cut-ins): the host owns the frame on a lit set; keyword stickers slap
on beside the head on their words (tags, speech bubbles, doodle arrows), and B-roll cut-ins land as tilted polaroids
— stills or playing clips — then fly off. The host keeps breathing and nodding so a long take never freezes.

p: host (video; default meta.host_video / meta.mascot) · stickers [{text, at, kind: tag|bubble|note}] (0–8;
   strings allowed) · broll [{src (image or video), at, dur, caption}] (0–4) · host_fit · kicker
Adapts: 0–8 stickers (16:9: beside the head, a 2 × 4 grid past four; 9:16: four slots above the head, later ones
replace earlier ones), 0–4 cut-ins (stills or clips, any aspect inside the polaroid; stickers step aside while one
plays), long sticker text (2 lines), no host (a monogram of `name` stands in).
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A, C = _load("_av"), _load("_cite")

CSS = """
.th-set { position:absolute; inset:0; overflow:hidden; background:radial-gradient(ellipse 55% 65% at var(--hx, 32%) 55%, color-mix(in srgb, var(--accent) 22%, var(--bg)), var(--bg) 70%); }
.th-set::before { content:''; position:absolute; inset:0; background-image:linear-gradient(color-mix(in srgb, var(--fg) 6%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in srgb, var(--fg) 6%, transparent) 1px, transparent 1px); background-size:64px 64px; }
.th-st { position:absolute; opacity:0; }
.th-st.tag b { display:inline-block; font-family:var(--f-display); font-weight:900; color:#111; background:#f6ce3a; padding:.18em .5em; border-radius:.18em; box-shadow:.12em .12em 0 #111; }
.th-st.note b { display:inline-block; font-family:var(--f-hand, var(--f-body)); font-weight:700; color:var(--fg); border-bottom:.1em solid var(--accent); padding:0 .1em; }
.th-st.bubble b { display:inline-block; position:relative; font-family:var(--f-body); font-weight:900; color:#111; background:#fbfaf6; padding:.4em .7em; border-radius:.8em; box-shadow:0 .2em .6em rgba(0,0,0,.25); }
.th-st.bubble b::after { content:''; position:absolute; bottom:-.42em; width:.8em; height:.8em; background:#fbfaf6; transform:rotate(45deg); }
.th-st.bubble.l b::after { right:.9em; } .th-st.bubble.r b::after { left:.9em; }
.th-pol { position:absolute; background:#fbfaf6; padding:14px 14px 62px; box-shadow:0 24px 60px rgba(0,0,0,.35); opacity:0; }
.th-pol .ph { position:absolute; left:14px; top:14px; right:14px; bottom:62px; overflow:hidden; background:#ddd; }
.th-pol .ph img { width:100%; height:100%; object-fit:cover; display:block; }
.th-pol span { position:absolute; left:16px; right:16px; bottom:14px; font:700 26px var(--f-hand, var(--f-body)); color:#222; text-align:center; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.th-pol .tape { position:absolute; left:50%; top:-16px; width:120px; height:30px; margin-left:-60px; background:rgba(246,206,58,.75); transform:rotate(-3deg); }
"""


def talking_head(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    host = A.host_src(X, p)
    if P:
        hs = 820; hx, hy = (W - hs) / 2, 1300 - hs
    else:
        hs = H * 0.9; hx, hy = W * 0.08, H - hs
    X.css("fx-th", CSS)
    X.css("fx-cite-base", C.CSS)
    S = f"#{cid}"
    set_html = f'<div class="th-set" style="--hx:{(hx + hs / 2) / W * 100:.0f}%"></div>'
    hsel = None
    if not host:     # no host clip: a monogram disc stands where the head would be
        ms = int(hs * 0.52)
        set_html += f'<div class="th-mono" style="position:absolute; left:{hx + (hs - ms) / 2:.0f}px; top:{hy + hs * 0.18:.0f}px">{C.mono_html(X, p.get("name") or "主讲", ms)}</div>'
    _clip(X, cid, t, d, set_html, p)
    if host:
        rect = f"inset:auto; left:{hx:.0f}px; top:{hy:.0f}px; width:{hs:.0f}px; height:{hs:.0f}px;"
        _, hsel = fit.media(X, cid, "th", host, t, d, "th-h", z=4, extra_style=rect)
        hfit = p.get("host_fit") or ("contain" if str(host).lower().endswith(".webm") else "cover")
        X.css(f"th-hfit-{cid}", f"{hsel} video {{ object-fit:{hfit} !important; }}")
    # cut-ins first: their windows decide when stickers may pop
    brs = [b if isinstance(b, dict) else {"src": str(b)} for b in (p.get("broll") or [])][:4]
    pol_meta, pol_html = [], []
    for k, br in enumerate(brs):
        ar = fit.aspect(X, br["src"], 4 / 3)
        pw = (W * 0.46) if not P else (W * 0.72)
        phw = pw - 28; phh = min(phw / ar, (H * 0.55) if not P else 560)
        phw = min(phw, phh * ar) if ar < 1 else phw
        pw = phw + 28; ph_ = phh + 76
        px0 = (W - 96 - pw) if not P else (W - pw) / 2
        py0 = ((H - ph_) / 2 - 20) if not P else 280
        rot = [4, -5, 3, -4][k % 4]
        ta = A.when(X, br, "at", t, d, 0.3 + 0.4 * k / max(len(brs), 1)) if br.get("at") is not None else A.snap(X, t + d * (0.3 + 0.4 * k / max(len(brs), 1)))
        tb = min(t + d - 0.1, ta + float(br.get("dur", min(2.4, d * 0.4))))
        cap = str(br.get("caption", ""))
        X.used_text.update(cap)
        photo = ""
        if fit.is_video(br["src"]):
            origin = f"{phw / 2 + 14:.0f}px {phh / 2 + 14:.0f}px"
            rect = f"inset:auto; left:{px0 + 14:.0f}px; top:{py0 + 14:.0f}px; width:{phw:.0f}px; height:{phh:.0f}px; transform-origin:{phw / 2:.0f}px {phh / 2:.0f}px;"
            _, vs = fit.media(X, cid, f"pv{k}", br["src"], ta, tb - ta, "th-pv", fill="cover", z=6, start=float(br.get("start", 0)), extra_style=rect)
        else:
            vs = None; origin = "50% 50%"
            photo = f'<img src="{X.asset(br["src"])}" alt="">'
        pol_html.append(f'<div class="th-pol" data-k="{k}" style="left:{px0:.0f}px; top:{py0:.0f}px; width:{pw:.0f}px; height:{ph_:.0f}px; transform-origin:{origin}">'
                        f'<i class="tape"></i><div class="ph">{photo}</div><span>{X.rich(cap)}</span></div>')
        pol_meta.append((k, ta, tb, rot, vs))
    wins = [(ta, tb) for _, ta, tb, _, _ in pol_meta]
    # stickers (overlay clip above the host)
    sts = [s if isinstance(s, dict) else {"text": str(s)} for s in (p.get("stickers") or [])][:8]
    n = len(sts)
    over = []
    times = []
    for i, st in enumerate(sts):
        ti = A.when(X, st, "at", t, d, 0.15 + 0.7 * (i + 0.5) / max(n, 1)) if st.get("at") is not None else A.snap(X, t + d * (0.15 + 0.7 * (i + 0.5) / max(n, 1)))
        for ta, tb in wins:      # a sticker never pops while a cut-in holds the stage
            if ta - 0.45 <= ti <= tb + 0.05: ti = (tb + 0.1) if tb + 0.1 < t + d - 0.4 else max(t + 0.15, ta - 0.6)
        times.append(A.snap(X, ti))
        kind = st.get("kind", "tag" if i % 3 != 2 else "bubble")
        txt = str(st.get("text", ""))
        X.used_text.update(txt)
        if P:                    # 2 × 2 slots above the head; a fifth sticker takes the first one's slot
            slot = i % 4
            side = "l" if slot % 2 == 0 else "r"
            px_ = 64
            f = fit.fit_text(txt, W * 0.42, px_ * 2.6, px_, 32, lh=1.15, max_lines=2)
            x = 70 if side == "l" else W * 0.5
            y = 270 + (slot // 2) * 150
        elif n <= 4:
            side = "r" if i % 2 == 0 else "l"
            px_ = 70
            f = fit.fit_text(txt, W * 0.38, px_ * 2.6, px_, 34, lh=1.15, max_lines=2)
            x = (hx + hs * 0.86 + (i // 2) * 30) if side == "r" else (hx + hs * 0.86 + 360 + (i // 2) * 20)
            y = 150 + (i % 4) * 190
            x = min(x, W - 96 - min(W * 0.38, f.px * max(len(l) for l in f.lines) * 1.1))
        else:                    # 5–8: a 2 × 4 grid beside the head, every sticker its own cell
            col, row = (i + i // 4) % 2, i % 4
            side = "r" if col == 0 else "l"
            x0 = hx + hs * 0.86
            colw = (W - 96 - x0 - 30) / 2
            px_ = 60
            f = fit.fit_text(txt, colw, px_ * 2.4, px_, 30, lh=1.15, max_lines=2)
            x = x0 + col * (colw + 30)
            y = 150 + row * 190
        rot = [-6, 5, -3, 7, -5, 4, -7, 3][i % 8]
        body = "<br>".join(X.rich(l) for l in f.lines)
        over.append(f'<div class="th-st {kind} {side}" data-i="{i}" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{f.px}px; transform:rotate({rot}deg)"><b>{body}</b></div>')
    ends = [t + d] * n
    if P:
        for i in range(4, n):
            if times[i] > times[i - 4] + 0.6: ends[i - 4] = times[i] - 0.12
    X.clip(f"{cid}s", t, d, "".join(over + pol_html), "th-over", 5, track=25)
    # motion
    if hsel:
        X.tw(f'tl.from("{hsel}", {{y:80, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
        X.tw(f'tl.to("{hsel}", {{keyframes:[{{y:-8, rotation:-1.2, duration:{d / 4:.2f}}}, {{y:0, rotation:0.8, duration:{d / 4:.2f}}}, {{y:-6, rotation:-0.6, duration:{d / 4:.2f}}}, {{y:0, rotation:0, duration:{d / 4:.2f}}}], ease:"sine.inOut", transformOrigin:"50% 100%"}}, {t + 0.6:.3f});')
    else:
        X.tw(f'tl.from("{S} .th-mono", {{y:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{S} .th-set", {{scale:1.0}}, {{scale:1.05, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    sel_i = lambda i: f'#{cid}s .th-st[data-i="{i}"]'
    hidden = set()               # (sticker, window) pairs: stickers faded out for a cut-in
    for ta, tb in wins:
        ids = [i for i in range(n) if times[i] < ta - 0.4 and ends[i] > ta]
        if not ids: continue
        X.tw(f'tl.to(\'{", ".join(sel_i(i) for i in ids)}\', {{opacity:0, scale:0.8, duration:0.25, ease:"power2.in", immediateRender:false}}, {ta - 0.05:.3f});')
        back = [i for i in ids if ends[i] > tb + 0.4 and tb < t + d - 0.4]
        if back: X.tw(f'tl.to(\'{", ".join(sel_i(i) for i in back)}\', {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {tb:.3f});')
        hidden.update(i for i in ids if i not in back)
    for i, ti in enumerate(times):
        rot = [-6, 5, -3, 7, -5, 4, -7, 3][i % 8]
        X.tw(f"tl.fromTo('{sel_i(i)}', {{opacity:0, scale:1.8, rotation:{rot * 3}}}, {{opacity:1, scale:1, rotation:{rot}, duration:0.32, ease:'back.out(2.4)', immediateRender:false}}, {ti - 0.06:.3f});")
        X.tw(f"tl.to('{sel_i(i)}', {{y:-6, duration:0.9, ease:'sine.inOut', yoyo:true, repeat:{max(0, int((min(ends[i], t + d) - ti) / 0.9) - 1)}}}, {ti + 0.3:.3f});")
        if ends[i] < t + d and i not in hidden:
            X.tw(f"tl.to('{sel_i(i)}', {{opacity:0, scale:0.7, duration:0.2, ease:'power2.in', immediateRender:false}}, {ends[i] - 0.1:.3f});")
        X.sfx(ti, "pop")
    if pol_meta and hsel and P:     # 9:16: the cut-in lands above the head, so the host ducks down and back up after the last one
        ta0, tb1 = pol_meta[0][1], pol_meta[-1][2]
        X.tw(f'tl.to("{hsel}", {{yPercent:22, scale:0.86, duration:0.4, ease:"power3.inOut", immediateRender:false}}, {ta0 - 0.05:.3f});')
        if t + d - tb1 > 0.5: X.tw(f'tl.to("{hsel}", {{yPercent:0, scale:1, duration:0.45, ease:"power3.inOut", immediateRender:false}}, {tb1 - 0.2:.3f});')
    if pol_meta and not hsel and P:     # 9:16 without a host: the monogram gives the stage to the cut-in
        ta0, tb1 = pol_meta[0][1], pol_meta[-1][2]
        X.tw(f'tl.to("{S} .th-mono", {{opacity:0, scale:0.9, duration:0.3, ease:"power2.in", immediateRender:false}}, {ta0 - 0.05:.3f});')
        if t + d - tb1 > 0.5: X.tw(f'tl.to("{S} .th-mono", {{opacity:1, scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {tb1 - 0.1:.3f});')
    for k, ta, tb, rot, vs in pol_meta:
        sel = f'#{cid}s .th-pol[data-k="{k}"]'
        both = sel + (f", {vs}" if vs else "")
        X.tw(f"tl.fromTo('{both}', {{opacity:0, x:{220 if not P else 0}, y:{0 if not P else 260}, rotation:{rot * 3}}}, {{opacity:1, x:0, y:0, rotation:{rot}, duration:0.5, ease:'expo.out', immediateRender:false}}, {ta:.3f});")
        X.tw(f"tl.to('{both}', {{opacity:0, x:{260 if not P else 0}, y:{0 if not P else -200}, rotation:{rot * 2}, duration:0.35, ease:'power2.in', immediateRender:false}}, {max(ta + 0.6, tb - 0.35):.3f});")
        X.sfx(ta, "whoosh_soft")


FX = {"talking_head": talking_head}
