"""Transitions (overlay clips at a beat boundary) and persistent texture layers.

A transition is drawn ON TOP of the cut at time t: it covers the frame by t and uncovers after t,
so the two scenes never need to overlap. Each one is a pure function of timeline time.
"""
import math

Z_TR, Z_OV = 40, 30


def noise_svg(freq=0.8, octaves=3, alpha=0.5, seed=3, tint="0 0 0"):
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'><filter id='n'>"
           f"<feTurbulence type='fractalNoise' baseFrequency='{freq}' numOctaves='{octaves}' seed='{seed}' stitchTiles='stitch'/>"
           f"<feColorMatrix values='0 0 0 0 {tint.split()[0]} 0 0 0 0 {tint.split()[1]} 0 0 0 0 {tint.split()[2]} 0 0 0 {alpha} 0'/></filter>"
           f"<rect width='100%' height='100%' filter='url(%23n)'/></svg>")
    return "url(\"data:image/svg+xml;utf8," + svg.replace('"', "'").replace("<", "%3C").replace(">", "%3E") + "\")"


def cut(X, prev, nxt, t, kind=None):
    """velocity-matched cut (HyperFrames cut-the-curve idea): the old stage accelerates out (power4.in),
    the new one decelerates in (power4.out) from the same direction, both blurred at the seam."""
    kind = kind or X.M.get("cut", "hard")
    if kind == "hard" or not prev: return
    if kind in ("dip", "flash", "wipe", "bars", "leak", "paper", "ink", "glitch", "iris", "shutter", "burn") or kind in TR2:
        return transition(X, t, kind)
    a = 0.16
    if kind == "slide":
        X.tw(f'tl.to("#{prev} > .stage", {{xPercent:-6, filter:"blur(12px)", duration:{a}, ease:"power4.in"}}, {t - a:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{xPercent:6, filter:"blur(12px)", duration:0.34, ease:"power4.out"}}, {t:.3f});')
    elif kind == "zoom":
        X.tw(f'tl.to("#{prev} > .stage", {{scale:1.12, filter:"blur(10px)", duration:{a}, ease:"power4.in"}}, {t - a:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{scale:0.9, filter:"blur(10px)", duration:0.34, ease:"power4.out"}}, {t:.3f});')
    elif kind == "rise":
        X.tw(f'tl.to("#{prev} > .stage", {{yPercent:-5, filter:"blur(10px)", duration:{a}, ease:"power4.in"}}, {t - a:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{yPercent:5, filter:"blur(10px)", duration:0.34, ease:"power4.out"}}, {t:.3f});')
    elif kind == "zoomin":   # Smooth Transitions pack: zoom through (out 1→1.7, in 0.55→1), heavy blur at the seam
        X.tw(f'tl.to("#{prev} > .stage", {{scale:1.7, filter:"blur(22px)", opacity:0.6, duration:0.24, ease:"power4.in"}}, {t - 0.24:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{scale:1.6, filter:"blur(22px)", duration:0.45, ease:"power4.out"}}, {t:.3f});')
    elif kind == "whip":     # whip pan: both frames on one strip, directional blur, matched speed at the cut
        X.tw(f'tl.to("#{prev} > .stage", {{xPercent:-11, scale:1.25, filter:"blur(34px)", duration:0.2, ease:"power3.in"}}, {t - 0.2:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{xPercent:11, scale:1.25, filter:"blur(34px)", duration:0.34, ease:"power3.out"}}, {t:.3f});')
    elif kind == "spin":     # spin transition: rotate + scale + blur through the cut
        X.tw(f'tl.to("#{prev} > .stage", {{rotation:28, scale:1.9, filter:"blur(18px)", duration:0.24, ease:"power4.in"}}, {t - 0.24:.3f});')
        X.tw(f'tl.from("#{nxt} > .stage", {{rotation:-28, scale:1.9, filter:"blur(18px)", duration:0.4, ease:"power4.out"}}, {t:.3f});')
    elif kind == "step":   # stop-motion: 2 frames off-register then snap
        X.tw(f'tl.from("#{nxt} > .stage", {{x:24, rotation:-1.2, duration:0.1, ease:"steps(2)"}}, {t:.3f});')
    X.sfx(t - 0.05, "cut")


TR2 = ("whip_carry", "shape_match", "paper_tear", "paint_wipe")     # drawn by scripts/h9/fx/fx2_transitions.py


def _tr2(kind):
    """the fx2 transition function for `kind` (the module is loaded with the effect library; loaded here if not yet)."""
    import importlib.util, pathlib, sys
    m = sys.modules.get("h9fx_fx2_transitions")
    if m is None:
        spec = importlib.util.spec_from_file_location("h9fx_fx2_transitions", pathlib.Path(__file__).with_name("fx") / "fx2_transitions.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["h9fx_fx2_transitions"] = m
        spec.loader.exec_module(m)
    return m.TRS[kind]


def transition(X, t, kind=None):
    kind = kind or X.M["transition"]
    if not kind or kind in ("cut", "hard"): return
    if kind in TR2:          # whip_carry also moves the two scenes it joins; the others are overlays like the ones below
        return _tr2(kind)(X, t)
    cid = X.uid("tr")
    a, b = t - 0.32, 0.7          # clip window around the cut
    X.sfx(t - 0.25 if kind not in ("flash", "glitch") else t, "transition")
    if kind == "flash":
        X.clip(cid, t, 0.5, "", "tr-flash", Z_TR)
        X.tw(f'tl.fromTo("#{cid}", {{opacity:0.95}}, {{opacity:0, duration:0.45, ease:"power2.out"}}, {t:.3f});')
    elif kind == "dip":
        X.clip(cid, a, b, "", "tr-dip", Z_TR)
        X.tw(f'tl.fromTo("#{cid}", {{opacity:0}}, {{opacity:1, duration:0.3, ease:"power2.in"}}, {a:.3f});')
        X.tw(f'tl.to("#{cid}", {{opacity:0, duration:0.38, ease:"power2.out"}}, {t:.3f});')
    elif kind == "wipe":
        X.clip(cid, a, b, '<i class="p"></i>', "tr-wipe", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .p", {{xPercent:-101}}, {{xPercent:0, duration:0.32, ease:"power3.in"}}, {a:.3f});')
        X.tw(f'tl.to("#{cid} .p", {{xPercent:101, duration:0.36, ease:"power3.out"}}, {t:.3f});')
    elif kind == "bars":
        X.clip(cid, a, b, "".join(f'<i class="b" style="top:{i * 20}%"></i>' for i in range(5)), "tr-bars", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .b", {{scaleX:0, transformOrigin:"0 50%"}}, {{scaleX:1, duration:0.26, ease:"power3.in", stagger:0.015}}, {a:.3f});')
        X.tw(f'tl.to("#{cid} .b", {{scaleX:0, transformOrigin:"100% 50%", duration:0.3, ease:"power3.out", stagger:0.03}}, {t:.3f});')
    elif kind == "leak":
        X.clip(cid, t - 0.45, 1.2, '<i class="l"></i>', "tr-leak", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .l", {{xPercent:-70, opacity:0}}, {{xPercent:30, opacity:1, duration:0.55, ease:"sine.in"}}, {t - 0.45:.3f});')
        X.tw(f'tl.to("#{cid} .l", {{xPercent:90, opacity:0, duration:0.6, ease:"sine.out"}}, {t + 0.1:.3f});')
    elif kind == "paper":
        X.clip(cid, a, b + 0.1, '<i class="pp"></i>', "tr-paper", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .pp", {{xPercent:-130, rotation:-8}}, {{xPercent:-10, rotation:-4, duration:0.32, ease:"steps(5)"}}, {a:.3f});')
        X.tw(f'tl.to("#{cid} .pp", {{xPercent:130, rotation:3, duration:0.42, ease:"steps(6)"}}, {t:.3f});')
    elif kind == "ink":
        X.clip(cid, t - 0.45, 1.1, '<i class="k"></i>', "tr-ink", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .k", {{scale:0, opacity:1}}, {{scale:1, duration:0.45, ease:"power2.in"}}, {t - 0.45:.3f});')
        X.tw(f'tl.to("#{cid} .k", {{opacity:0, scale:1.25, duration:0.6, ease:"sine.out"}}, {t:.3f});')
    elif kind == "glitch":
        X.clip(cid, t - 0.1, 0.36, "".join(f'<i class="g" style="top:{i * 12.5}%"></i>' for i in range(8)), "tr-glitch", Z_TR)
        for k in range(6):
            tt = t - 0.1 + k * 0.05
            X.tw(f'tl.set("#{cid} .g", {{xPercent:i => [{",".join(str(X.rand.randint(-40, 40)) for _ in range(8))}][i], opacity:i => [{",".join(str(round(X.rand.random(), 2)) for _ in range(8))}][i]}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .g", {{opacity:0}}, {t + 0.22:.3f});')
    elif kind == "iris":
        X.clip(cid, a, b, "", "tr-iris", Z_TR)
        X.tw(f'tl.fromTo("#{cid}", {{clipPath:"circle(0% at 50% 50%)"}}, {{clipPath:"circle(80% at 50% 50%)", duration:0.32, ease:"power3.in"}}, {a:.3f});')
        X.tw(f'tl.to("#{cid}", {{clipPath:"circle(0% at 50% 50%)", duration:0.36, ease:"power3.out"}}, {t:.3f});')
    elif kind == "shutter":
        X.clip(cid, a, b, '<i class="u"></i><i class="d"></i>', "tr-shutter", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .u", {{yPercent:-100}}, {{yPercent:0, duration:0.3, ease:"power3.in"}}, {a:.3f});')
        X.tw(f'tl.fromTo("#{cid} .d", {{yPercent:100}}, {{yPercent:0, duration:0.3, ease:"power3.in"}}, {a:.3f});')
        X.tw(f'tl.to("#{cid} .u", {{yPercent:-100, duration:0.36, ease:"power3.out"}}, {t:.3f});')
        X.tw(f'tl.to("#{cid} .d", {{yPercent:100, duration:0.36, ease:"power3.out"}}, {t:.3f});')
    elif kind == "burn":   # film burn: white-hot bloom + projector flicker
        X.clip(cid, t - 0.3, 0.9, '<i class="l"></i>', "tr-burn", Z_TR)
        X.tw(f'tl.fromTo("#{cid} .l", {{opacity:0, scale:0.6}}, {{opacity:1, scale:1.4, duration:0.3, ease:"power2.in"}}, {t - 0.3:.3f});')
        X.tw(f'tl.to("#{cid} .l", {{opacity:0, scale:1.8, duration:0.5, ease:"power1.out"}}, {t:.3f});')


TR_CSS = """
.tr-flash { background:#fff; opacity:0; }
.tr-dip { background:var(--bg); opacity:0; }
.tr-wipe .p, .tr-bars .b, .tr-shutter i { position:absolute; display:block; background:var(--accent); }
.tr-wipe .p { inset:0 -6%; transform:skewX(-8deg); }
.tr-bars .b { left:0; right:0; height:20.5%; }
.tr-shutter i { left:0; right:0; height:50.5%; background:var(--ink, #000); } .tr-shutter .u { top:0; } .tr-shutter .d { bottom:0; }
.tr-leak .l { position:absolute; inset:-30% -40%; display:block; mix-blend-mode:screen;
  background:radial-gradient(ellipse 35% 55% at 50% 50%, rgba(255,214,150,.95), rgba(255,120,40,.65) 40%, rgba(200,40,20,.25) 65%, rgba(0,0,0,0) 80%); }
.tr-burn .l { position:absolute; inset:-20%; display:block; mix-blend-mode:screen;
  background:radial-gradient(circle at 60% 45%, #fffbe8 0%, #ffd27a 18%, rgba(255,110,30,.7) 38%, rgba(0,0,0,0) 70%); }
.tr-paper .pp { position:absolute; top:-30%; bottom:-30%; left:0; width:140%; display:block; background:var(--paper); box-shadow:0 0 60px rgba(0,0,0,.35);
  clip-path:polygon(4% 0, 100% 0, 96% 8%, 99% 17%, 95% 26%, 98% 37%, 94% 48%, 99% 59%, 95% 70%, 98% 81%, 94% 91%, 97% 100%, 0 100%, 3% 88%, 0 76%, 4% 64%, 1% 52%, 5% 40%, 1% 28%, 4% 15%); }
.tr-ink .k { position:absolute; left:50%; top:50%; width:260vmax; height:260vmax; margin:-130vmax 0 0 -130vmax; border-radius:50%; display:block;
  background:radial-gradient(circle, var(--ink) 0%, var(--ink) 38%, rgba(0,0,0,0) 50%); }
.tr-glitch .g { position:absolute; left:0; right:0; height:12.5%; display:block; background:var(--accent); mix-blend-mode:difference; opacity:0; }
.tr-iris { background:var(--accent); }
"""


def overlays(X, D):
    """persistent texture / frame layers declared by the style: S['layers'] = [name or (name, opts)]."""
    for spec in X.S.get("layers", []):
        name, o = (spec, {}) if isinstance(spec, str) else spec
        cid = f"ov-{name}"
        if name == "grain":
            X.clip(cid, 0, D, "", "ov-grain", o.get("z", Z_OV + 2), track=20, attrs=f'data-layout-allow-overflow')
            X.css("ov-grain", f".ov-grain {{ inset:-200px; background-image:{noise_svg(o.get('freq', 0.9), 2, o.get('alpha', 0.55), tint=o.get('tint', '0.5 0.5 0.5'))}; "
                              f"background-size:320px; opacity:{o.get('opacity', 0.12)}; mix-blend-mode:{o.get('blend', 'overlay')}; pointer-events:none; }}")
            step = 1 / o.get("fps", 12)
            k = int(D / step)
            xs = ",".join(f"{X.rand.randint(0, 320)}" for _ in range(64))
            for i in range(k):  # re-seat the grain 12x a second (deterministic)
                X.tw(f'tl.set("#{cid}", {{x:{X.rand.randint(-160, 160)}, y:{X.rand.randint(-160, 160)}}}, {i * step:.3f});')
        elif name == "vignette":
            X.clip(cid, 0, D, "", "ov-vig", Z_OV, track=21)
            X.css("ov-vig", f".ov-vig {{ background:radial-gradient(ellipse at center, rgba(0,0,0,0) {o.get('inner', 50)}%, rgba(0,0,0,{o.get('alpha', 0.55)}) 100%); pointer-events:none; }}")
        elif name == "letterbox":
            h = round((X.H - X.W / o.get("ratio", 2.39)) / 2) if not X.portrait else 0
            if h > 0:
                X.clip(cid, 0, D, '<i class="u"></i><i class="d"></i>', "ov-lb", Z_OV + 5, track=22)
                X.css("ov-lb", f".ov-lb i {{ position:absolute; left:0; right:0; height:{h}px; background:#000; display:block; }} .ov-lb .u {{ top:0; }} .ov-lb .d {{ bottom:0; }}")
        elif name == "paper":   # paper ground; jitter = re-seat the fibres N times a second (Vox: 2–3/s)
            X.clip(cid, 0, D, "", "ov-paper", o.get("z", 0), track=23, attrs="data-layout-allow-overflow")
            X.css("ov-paper", f".ov-paper {{ inset:-60px; background-color:{o.get('color', 'var(--paper)')}; background-image:{noise_svg(o.get('freq', 0.65), 4, o.get('alpha', 0.22), seed=7, tint=o.get('tint', '0.35 0.28 0.2'))}; {o.get('extra', '')} }}")
            if o.get("jitter"):
                step = 1 / o["jitter"]
                for i in range(int(D / step)):
                    X.tw(f'tl.set("#{cid}", {{x:{X.rand.randint(-40, 40)}, y:{X.rand.randint(-40, 40)}}}, {i * step:.3f});')
        elif name == "stars":    # ambient background only (never on titles): slow drift + a few twinkles
            r = X.rand
            dots = "".join(f'<i style="left:{r.uniform(0, 100):.1f}%;top:{r.uniform(0, 100):.1f}%;width:{(s := r.choice([2, 2, 3, 4]))}px;height:{s}px;opacity:{r.uniform(.25, .9):.2f}"></i>' for _ in range(o.get("n", 90)))
            X.clip(cid, 0, D, dots, "ov-stars", 1, track=31, attrs="data-layout-allow-overflow")
            X.css("ov-stars", ".ov-stars { inset:-5%; pointer-events:none; } .ov-stars i { position:absolute; border-radius:50%; background:#fff; display:block; box-shadow:0 0 6px rgba(255,255,255,.8); }")
            X.tw(f'tl.fromTo("#{cid}", {{xPercent:-1.5}}, {{xPercent:1.5, duration:{D:.2f}, ease:"none"}}, 0);')
            for k in range(1, 13):
                X.tw(f'tl.to("#{cid} i:nth-child({k * 7})", {{opacity:0.1, duration:0.8, ease:"sine.inOut", yoyo:true, repeat:{max(1, int(D / 1.6))}}}, {r.uniform(0, 1.5):.2f});')
        elif name == "bgcolor":
            X.clip(cid, 0, D, "", "ov-bg", 0, track=32)
            X.css("ov-bg", f".ov-bg {{ background:{o.get('css', 'var(--bg)')}; }}")
        elif name == "fibers":
            X.clip(cid, 0, D, "", "ov-fib", Z_OV - 2, track=24)
            X.css("ov-fib", f".ov-fib {{ background-image:{noise_svg(0.02, 2, o.get('alpha', 0.18), seed=5, tint=o.get('tint', '0.3 0.25 0.2'))}; mix-blend-mode:multiply; pointer-events:none; }}")
        elif name == "grid":
            X.clip(cid, 0, D, "", "ov-grid", 0, track=25)
            c, step = o.get("color", "var(--line)"), o.get("step", 120)
            X.css("ov-grid", f".ov-grid {{ background-image:linear-gradient(90deg, {c} 1px, transparent 1px), linear-gradient(0deg, {c} 1px, transparent 1px); background-size:{step}px {step}px; background-position:{(X.W % step) // 2}px {(X.H % step) // 2}px; opacity:{o.get('opacity', 0.5)}; }}")
        elif name == "dots":
            X.clip(cid, 0, D, "", "ov-dots", 0, track=25)
            X.css("ov-dots", f".ov-dots {{ background-image:radial-gradient({o.get('color', 'var(--line)')} 2.2px, transparent 2.6px); background-size:{o.get('step', 44)}px {o.get('step', 44)}px; opacity:{o.get('opacity', 0.7)}; }}")
        elif name == "scanlines":
            X.clip(cid, 0, D, "", "ov-scan", Z_OV + 1, track=26)
            X.css("ov-scan", f".ov-scan {{ background:repeating-linear-gradient(0deg, rgba(0,0,0,{o.get('alpha', 0.18)}) 0 2px, transparent 2px 4px); pointer-events:none; mix-blend-mode:multiply; }}")
        elif name == "glow":   # stage floor glow
            X.clip(cid, 0, D, "", "ov-glow", 0, track=27)
            X.css("ov-glow", ".ov-glow { background:radial-gradient(ellipse 60% 45% at 50% 110%, var(--accent2) 0%, rgba(0,0,0,0) 70%), radial-gradient(ellipse 50% 60% at 50% -10%, rgba(255,255,255,.10), rgba(0,0,0,0) 70%), var(--bg); }")
        elif name == "folio":   # magazine running head
            left, right = o.get("left", X.v.get("meta", {}).get("folio", X.channel)), o.get("right", "")
            X.clip(cid, 0, D, f'<span class="fl">{X.rich(left)}</span><i class="fr-rule"></i><span class="fr">{X.rich(right)}</span>', "ov-folio", Z_OV + 3, track=28)
        elif name == "stamp":   # film date stamp
            X.clip(cid, 0, D, f'<span>{X.rich(o.get("text", "26 10 31"))}</span>', "ov-stamp", Z_OV + 3, track=29)
        elif name == "frame":   # inset border (poster / sticker book)
            X.clip(cid, 0, D, "", "ov-frame", Z_OV + 4, track=30)
        elif name == "weave":   # projector gate weave on the whole picture
            pass  # applied in build (needs the stage wrapper)
