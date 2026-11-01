"""主讲人画中画 (talking-head picture-in-picture): the host opens the beat full-frame, then springs into a round
(or rounded-square) window in a corner while the content — a clip, a still or a page — takes the screen; it can
spring back to full-frame at `back_at`. A ring and a name chip ride the window.

p: main (image or video) · host (video; default meta.host_video / meta.mascot; false = no host) · name · role ·
   at (when the host shrinks: "@词", seconds, default 30 %) · back_at (optional) · corner (br | bl | tr | tl; 9:16
   default tr, clear of the platform buttons) · shape (circle | round) · host_fit (contain | cover; .webm → contain)
   · host_focus [x%, y%] (the face in the host frame) · kicker / title (a tag over the content) · main_start
Adapts: any main aspect (cover, extreme ratios get a blurred fill), still or video main, no host (a monogram window),
16:9 and 9:16 corners, short beats (the shrink lands by 45 % of the beat at the latest).
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip, _theme_style


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A, C = _load("_av"), _load("_cite")

CSS = """
.pp-main { position:absolute; inset:0; overflow:hidden; }
.pp-main > img, .pp-main .pp-img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.pp-tag { position:absolute; display:flex; align-items:center; gap:12px; font:800 28px var(--f-body); color:#fbfaf6; background:rgba(17,17,17,.82); padding:8px 16px 8px 8px; border-radius:10px; }
.pp-tag i { font-style:normal; font:700 20px var(--f-mono, monospace); letter-spacing:.12em; color:#111; background:#f6ce3a; padding:4px 10px; border-radius:6px; }
.pp-scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.42), rgba(0,0,0,0) 22%, rgba(0,0,0,0) 70%, rgba(0,0,0,.42)); }
.pp-ring { position:absolute; border-radius:50%; border:6px solid var(--accent); box-shadow:0 18px 40px rgba(0,0,0,.35), 0 0 0 10px rgba(255,255,255,.12); }
.pp-ring.sq { border-radius:22%; }
.pp-chip { position:absolute; transform:translateX(-50%); white-space:nowrap; font:800 28px var(--f-body); color:var(--bg); background:var(--fg); padding:5px 14px; border-radius:6px; }
.pp-chip small { font:600 20px var(--f-mono, monospace); margin-left:8px; opacity:.75; }
.pp-full-name { position:absolute; display:flex; flex-direction:column; gap:4px; }
.pp-full-name b { font:900 54px var(--f-display); color:var(--fg); line-height:1.05; }
.pp-full-name span { font:600 28px var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; }
.pp-full-name i { display:block; width:72px; height:8px; background:var(--accent); margin-bottom:10px; }
.pp-mono { position:absolute; inset:0; display:grid; place-items:center; }
"""


def pip(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    host = A.host_src(X, p)
    ts = A.when(X, p, "at", t, d, 0.3)
    ts = min(ts, t + d * 0.45)
    tb = A.when(X, p, "back_at", t, d, 0.95) if p.get("back_at") is not None else None
    corner = p.get("corner") or ("tr" if P else "br")
    shape = p.get("shape", "circle")
    r = (128 if P else 150) * float(p.get("size", 1))
    m = 56 if P else 96
    top_y = 252 if P else 130
    bot_y = (H - 690) if P else (H - 210)       # 9:16: a bottom window sits above the caption, not beside it
    cx = (W - m - r) if "r" in corner else (m + r)
    cy = (top_y + r + 10) if corner.startswith("t") else (bot_y - r)
    # the content
    main = p.get("main")
    X.css("fx-pip", CSS)
    X.css("fx-cite-base", C.CSS)     # .ct-mono discs, .ct-l lines
    inner_main = ""
    card = ""
    if main:
        ar = fit.aspect(X, main, 16 / 9)
        frame_ar = W / H
        if max(ar / frame_ar, frame_ar / ar) > 1.9:      # e.g. a 16:9 clip in a 9:16 frame: show it whole, as a card on the stage
            cw = (W - 2 * m) if ar > frame_ar else min(W * 0.5, (H - 520) * ar)
            ch = cw / ar
            ccx, ccy = (W - cw) / 2, (top_y + (H * 0.42 if P else H * 0.5) - ch / 2) if P else (H - ch) / 2
            if P: ccy = max(top_y + 2 * r + 60, min(ccy, 1250 - ch))
            rect = f"inset:auto; left:{ccx:.0f}px; top:{ccy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; border-radius:18px; box-shadow:0 30px 70px rgba(0,0,0,.35);"
            card = "card"
        else:
            rect = ""
        if fit.is_video(main):
            _, msel = fit.media(X, cid, "main", main, t, d, "pp-mv", focus=p.get("focus"), fill="cover", z=2, start=float(p.get("main_start", 0)), extra_style=rect)
        else:
            mh, msel = fit.media(X, cid, "mi", main, t, d, "pp-img", focus=p.get("focus"), fill="cover" if rect else "auto", extra_style=rect)
            inner_main = mh
    else:
        msel = None
    kick, title = p.get("kicker", ""), p.get("title", "")
    X.used_text.update(str(kick) + str(title))
    tag = ""
    if kick or title:
        tx, ty = (m, top_y + 6) if not (corner.startswith("t") and "l" in corner) else (W - m - 600, top_y + 6)
        tag = f'<div class="pp-tag" style="left:{tx}px; top:{ty}px">{f"<i>{X.rich(kick)}</i>" if kick else ""}<span>{X.rich(title)}</span></div>'
    name, role = p.get("name", ""), p.get("role", "")
    X.used_text.update(str(name) + str(role))
    full_name = (f'<div class="pp-full-name" style="left:{m}px; top:{(H * 0.62) if P else (H * 0.40):.0f}px"><i></i><b>{X.rich(name)}</b><span>{X.rich(role)}</span></div>'
                 if (name and not P) else "")
    inner = f'<div class="pp-main">{inner_main}{"" if card else "<div class=pp-scrim></div>"}</div>{tag}'
    _clip(X, cid, t, d, inner, p, transparent=bool(main and fit.is_video(main)))
    if card and fit.is_video(main): A.stage_bg(X, cid, t, d, p); A.scope(X, msel, t, d)
    S = f"#{cid}"
    # the host layer: full frame on a lit stage, then clipped to the window and flown into the corner
    fx_, fy_ = (p.get("host_focus") or [50, 40])[:2]
    hfit = p.get("host_fit") or ("contain" if host and str(host).lower().endswith(".webm") else "cover")
    # the host layer is a root sibling, outside the themed clip: carry the theme's variables onto it
    stage = _theme_style(p, paint=False) + ";background:radial-gradient(ellipse 60% 70% at 50% 45%, color-mix(in srgb, var(--card) 92%, #fff 8%), var(--bg));"
    if host:
        _, hsel = fit.media(X, cid, "host", host, t, d, "pp-host", z=4, extra_style=stage)
        X.css(f"pp-hfit-{cid}", f"{hsel} video {{ object-fit:{hfit} !important; object-position:{fx_}% {fy_ if hfit == 'cover' else 50}% !important; }}")
    else:
        hsel = f"#{cid}_hm"
        mono = C.mono_html(X, name or "主讲", int(min(W, H) * 0.42))
        X.els.append(f'<div id="{cid}_hm" class="fxv" style="position:absolute; inset:0; z-index:4; pointer-events:none; {stage}"><div class="pp-mono">{mono}</div></div>')
    face = H * (0.30 if hfit == "contain" else 0.34)          # the face disc in the full frame, px
    s = r / face
    fpx, fpy = W * fx_ / 100, H * fy_ / 100
    x1, y1 = cx - s * fpx, cy - s * fpy
    R = r / s
    clip0 = f"circle({max(W, H):.0f}px at {fpx:.0f}px {fpy:.0f}px)" if shape == "circle" else f"inset(0px 0px 0px 0px round 0px)"
    if shape == "circle":
        clip1 = f"circle({R:.0f}px at {fpx:.0f}px {fpy:.0f}px)"
    else:
        clip1 = f"inset({fpy - R:.0f}px {W - fpx - R:.0f}px {H - fpy - R:.0f}px {fpx - R:.0f}px round {R * 0.44:.0f}px)"
    # the layer is an untimed root sibling with a painted stage: visible only inside the beat
    X.css(f"pp-vis-{cid}", f"{hsel} {{ visibility:hidden; }}")
    X.tw(f'tl.set("{hsel}", {{visibility:"visible", transformOrigin:"0 0", clipPath:"{clip0}"}}, {t:.3f});')
    X.tw(f'tl.set("{hsel}", {{visibility:"hidden"}}, {t + d:.3f});')
    X.tw(f'tl.from("{hsel}", {{opacity:0, duration:0.3}}, {t:.3f});')
    X.tw(f'tl.fromTo("{hsel}", {{scale:1.04}}, {{scale:1, duration:{max(0.2, ts - t):.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.to("{hsel}", {{scale:{s:.4f}, x:{x1:.1f}, y:{y1:.1f}, clipPath:"{clip1}", duration:0.75, ease:"expo.inOut"}}, {ts:.3f});')
    X.sfx(ts, "whoosh_soft")
    # ring + chip over the window
    sq = " sq" if shape != "circle" else ""
    chip_y = cy + r + 16
    if corner.startswith("b"): chip_y = cy - r - 52
    chip = f'<div class="pp-chip" style="left:{cx:.0f}px; top:{chip_y:.0f}px">{X.rich(name)}{f"<small>{X.rich(role)}</small>" if role else ""}</div>' if name else ""
    X.clip(f"{cid}r", t, d, f'<div class="pp-ring{sq}" style="left:{cx - r - 3:.0f}px; top:{cy - r - 3:.0f}px; width:{2 * r + 6:.0f}px; height:{2 * r + 6:.0f}px"></div>{chip}{full_name}', "pp-over", 5, track=24)
    X.tw(f'tl.set("#{cid}r .pp-ring, #{cid}r .pp-chip", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.fromTo("#{cid}r .pp-ring", {{opacity:0, scale:1.25}}, {{opacity:1, scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {ts + 0.6:.3f});')
    if chip: X.tw(f'tl.fromTo("#{cid}r .pp-chip", {{opacity:0, y:-8}}, {{opacity:1, y:0, duration:0.35, ease:"expo.out", immediateRender:false}}, {ts + 0.75:.3f});')
    if full_name:
        X.tw(f'tl.from("#{cid}r .pp-full-name > *", {{x:-40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t + 0.2:.3f});')
        X.tw(f'tl.to("#{cid}r .pp-full-name", {{opacity:0, x:-30, duration:0.3, ease:"power2.in"}}, {ts - 0.05:.3f});')
    # the content: lands behind the shrinking host, then keeps creeping
    if msel:
        X.tw(f'tl.fromTo("{msel}", {{scale:1.14}}, {{scale:1, duration:0.9, ease:"expo.out"}}, {ts:.3f});')
        X.tw(f'tl.to("{msel}", {{scale:1.05, duration:{max(0.2, t + d - ts - 0.9):.2f}, ease:"none"}}, {ts + 0.9:.3f});')
    if tag: X.tw(f'tl.from("{S} .pp-tag", {{y:-16, opacity:0, duration:0.45, ease:"expo.out"}}, {ts + 0.5:.3f});')
    # gentle life in the window
    hold0 = ts + 0.8
    end = tb if tb else t + d
    if end - hold0 > 0.3:
        X.tw(f'tl.to("{hsel}", {{y:{y1 - 6:.1f}, duration:{(end - hold0) / 2:.2f}, ease:"sine.inOut", yoyo:true, repeat:1}}, {hold0:.3f});')
    if tb:
        X.tw(f'tl.to("{hsel}", {{scale:1, x:0, y:0, clipPath:"{clip0}", duration:0.7, ease:"expo.inOut"}}, {tb:.3f});')
        X.tw(f'tl.to("#{cid}r .pp-ring, #{cid}r .pp-chip", {{opacity:0, duration:0.2}}, {tb:.3f});')
        X.sfx(tb, "whoosh_soft")


FX = {"pip": pip}
