"""papercut · 剪纸风 —— 层叠纸艺：中国窗花、祥云、灯笼的镂空剪纸，加上 Apple / Google 纸艺广告那种层层叠叠的立体纸景。
每一层纸都有按深度投下的真实阴影，镜头推进时各层按远近视差移动；纸张带纤维和毛边。
配色只用节庆红、纸白，加一点金和深红做阴影；大字是"剪出来的纸字"。
转场是纸的动作：新的一页带毛边滑上来、从上往下翻折、从侧面推入，盖住上一页。

场景全部自己实现（SCENES）：hook 大数字开场 · tickets 两张票根 + 纪录印章 · calendar 撕日历 + 鞭炮 ·
share 圆形窗花切出一块 · banner 卷轴横幅 + 纸火焰 · stacks 纸张叠成的排行 · thesis 判断句 · outro 印章落版。
横屏竖屏各自排版；文字、条数按 scripts/h9/fit.py 自适应。
"""
import math

STYLE = {
    "name": "剪纸风", "en": "Papercut", "benchmarks": ["中国窗花剪纸", "Apple / Google 纸艺广告", "层叠纸雕 diorama"],
    "tokens": {
        "bg": "#c62a1f", "fg": "#1e1b18", "muted": "#6c635a", "accent": "#c62a1f", "accent2": "#d6a23c", "alert": "#c62a1f",
        "line": "#e6dccb", "paper": "#f3ede1", "ink": "#1e1b18", "card": "#fbf7ee", "card-fg": "#1e1b18",
        "red": "#c62a1f", "red2": "#e0452f", "deep": "#8d1711", "gold": "#d6a23c", "cream": "#fbf7ee",
        "cap-bg": "#fbf7ee", "cap-fg": "#1e1b18", "cap-size": "40px", "cap-weight": "700", "cap-pad": "8px 22px 10px", "cap-radius": "3px",
        "cap-shadow": "0 3px 0 rgba(90,20,10,.35)", "cap-bottom": "60px", "cap-em": "#c62a1f",
        "punch-top": "70%", "punch-size": "72px",
    },
    "fonts": {"display": ["zcool-kuhei", "noto-sans-sc"], "body": "noto-sans-sc", "num": "archivo-black", "hand": "lxgw-wenkai",
              "mono": "jetbrains-mono", "serif": "noto-serif-sc"},
    "motion": {"ease": "expo.out", "dur": 0.55, "stagger": 0.04, "cut": "hard", "transition": "paper", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.07}), ("vignette", {"alpha": 0.22, "inner": 55})],
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 90, "bottom": 0, "h": 400}, "portrait": {"right": 150, "bottom": 600, "h": 300}},
    "outro": {"move": False},
    "sfx": {"transition": ("paper", 0.5), "enter": ("paper", 0.45), "pop": ("pop", 0.45), "hit": ("hit", 0.4), "slam": ("slam", 0.5),
            "count": ("type", 0.3), "click": ("click", 0.3), "mascot": ("whoosh_soft", 0.3), "tear": ("paper", 0.6), "line": ("click", 0.3)},
}

# ---------------------------------------------------------------- paper vocabulary
CSS = r"""
.st-papercut .em .emb { display:none; } .st-papercut .stage { perspective:2200px; }
.pcw { position:absolute; inset:-8px; filter:drop-shadow(0 -6px 14px rgba(40,8,4,.35)); }
.pc { position:absolute; inset:0; overflow:hidden; }
.pc .cam { position:absolute; inset:0; }
.pc .sheet { position:absolute; inset:-40px; }
.pc.red .sheet { background-color:var(--red); }
.pc.cream .sheet { background-color:var(--paper); }
.pc .lay { position:absolute; }
.pc .sh1 { filter:drop-shadow(0 3px 0 rgba(70,15,8,.26)) drop-shadow(0 9px 12px rgba(70,15,8,.22)); }
.pc .sh2 { filter:drop-shadow(0 5px 0 rgba(70,15,8,.28)) drop-shadow(0 16px 20px rgba(70,15,8,.28)); }
.pc .sh3 { filter:drop-shadow(0 8px 0 rgba(70,15,8,.30)) drop-shadow(0 26px 30px rgba(70,15,8,.32)); }
.pc svg { display:block; overflow:visible; }
.pc .cut { font-family:var(--f-display); font-weight:400; color:var(--cream); line-height:1; letter-spacing:.01em;
  text-shadow:0 5px 0 var(--deep), 0 14px 22px rgba(60,10,5,.38); white-space:nowrap; }
.pc.cream .cut { color:var(--red); text-shadow:0 5px 0 #7a140f, 0 14px 22px rgba(60,10,5,.22); }
.pc .cut .c, .pc .cut .n { display:inline-block; }
.pc .cut .n { font-family:var(--f-num); }
.pc .chip { position:absolute; display:inline-flex; align-items:center; gap:12px; padding:10px 22px 12px; background:var(--cream); color:var(--ink);
  font-family:var(--f-display); font-size:30px; white-space:nowrap; }
.pc.cream .chip { background:var(--red); color:var(--cream); }
.pc .note { position:absolute; font-family:var(--f-hand); color:var(--red); white-space:nowrap; }
.pc.red .note { color:var(--cream); }
/* furniture */
.pc-hd { position:absolute; left:84px; right:84px; top:34px; height:52px; display:flex; justify-content:space-between; align-items:center; z-index:6; }
.pc-hd .tag { background:var(--cream); color:var(--ink); font-family:var(--f-display); font-size:22px; padding:7px 16px 9px; }
.pc-hd .tag b { color:var(--deep); font-weight:400; margin-right:10px; }
.pc.cream .pc-hd .tag { background:var(--deep); color:var(--cream); } .pc.cream .pc-hd .tag b { color:#ffd77a; }
.pc-hd .pg { font-family:var(--f-num); font-size:22px; color:var(--cream); background:var(--deep); padding:6px 12px; }
.pc.cream .pc-hd .pg { background:var(--ink); }
.pc-ft { position:absolute; left:84px; bottom:18px; z-index:6; font-family:var(--f-mono); font-size:16px; color:var(--cream); background:rgba(141,23,17,.9); padding:3px 9px;
  letter-spacing:.03em; white-space:nowrap; }
.pc.cream .pc-ft { color:#3f3933; background:rgba(251,247,238,.85); }
#root.v .pc-hd { left:56px; right:56px; top:206px; } #root.v .pc-ft { left:56px; bottom:auto; top:1478px; font-size:17px; }
"""


def deckle(rnd, n=36, amp=0.5, sides="tblr"):
    """clip-path polygon (percent) with torn / deckled paper edges."""
    pts = []
    j = lambda s: rnd.uniform(0, amp) if s in sides else 0.0
    for i in range(n + 1): pts.append((100 * i / n, j("t")))
    for i in range(1, n): pts.append((100 - j("r"), 100 * i / n))
    for i in range(n, -1, -1): pts.append((100 * i / n, 100 - j("b")))
    for i in range(n - 1, 0, -1): pts.append((j("l"), 100 * i / n))
    return "polygon(" + ",".join(f"{x:.2f}% {y:.2f}%" for x, y in pts) + ")"


def noise_bg(alpha=0.16, seed=3):
    from h9 import fx as FXM
    return FXM.noise_svg(0.7, 3, alpha, seed=seed, tint="0.35 0.25 0.18")


def flower(uid, color, petals=8, holes=True):
    """窗花: a scalloped paper disc with symmetric hollow cuts (mask), 200×200 viewBox."""
    r = []
    for k in range(petals * 3):
        a = 2 * math.pi * k / (petals * 3)
        r.append(f'<circle cx="{100 + 88 * math.cos(a):.2f}" cy="{100 + 88 * math.sin(a):.2f}" r="9.5"/>')
    cuts = []
    if holes:
        for k in range(petals):
            a = 360 * k / petals
            cuts.append(f'<ellipse cx="100" cy="52" rx="11" ry="26" transform="rotate({a:.1f} 100 100)"/>')
            cuts.append(f'<path d="M100 18 l6 9 l-6 9 l-6 -9 z" transform="rotate({a + 180 / petals:.1f} 100 100)"/>')
            cuts.append(f'<circle cx="100" cy="80" r="3.6" transform="rotate({a + 180 / petals:.1f} 100 100)"/>')
        for k in range(6):
            cuts.append(f'<ellipse cx="100" cy="88" rx="5" ry="11" transform="rotate({60 * k} 100 100)"/>')
        cuts.append('<circle cx="100" cy="100" r="4.5"/>')
    return (f'<svg viewBox="0 0 200 200"><defs><mask id="m{uid}"><rect width="200" height="200" fill="#fff"/>'
            f'<g fill="#000">{"".join(cuts)}</g></mask></defs>'
            f'<g fill="{color}" mask="url(#m{uid})"><circle cx="100" cy="100" r="88"/>{"".join(r)}</g></svg>')


CLOUD = ("M14 64 C10 46 28 36 42 42 C46 22 76 16 88 34 C100 24 124 28 126 46 C142 44 152 56 146 68 Z")


def cloud(uid, color):
    return (f'<svg viewBox="0 0 160 80"><defs><mask id="c{uid}"><rect width="160" height="80" fill="#fff"/>'
            f'<g fill="none" stroke="#000" stroke-width="3"><path d="M44 54 a8 8 0 1 1 10 -8"/><path d="M86 50 a9 9 0 1 1 12 -9"/><path d="M118 58 a6 6 0 1 1 8 -6"/></g></mask></defs>'
            f'<path d="{CLOUD}" fill="{color}" mask="url(#c{uid})"/></svg>')


def lantern():
    return ('<svg viewBox="0 0 120 190"><line x1="60" y1="0" x2="60" y2="26" stroke="#3b2a18" stroke-width="3"/>'
            '<rect x="40" y="24" width="40" height="12" rx="3" fill="#d6a23c"/>'
            '<ellipse cx="60" cy="86" rx="52" ry="52" fill="#e0452f"/>'
            '<g fill="none" stroke="#8d1711" stroke-width="2.4" opacity=".7"><ellipse cx="60" cy="86" rx="34" ry="52"/><ellipse cx="60" cy="86" rx="14" ry="52"/></g>'
            '<rect x="40" y="134" width="40" height="12" rx="3" fill="#d6a23c"/>'
            '<g stroke="#d6a23c" stroke-width="3"><line x1="50" y1="146" x2="48" y2="186"/><line x1="60" y1="146" x2="60" y2="190"/><line x1="70" y1="146" x2="72" y2="186"/></g></svg>')


def hills(rnd, w, h, color, waves=3, amp=0.18):
    """a layer of paper hills: smooth wave top edge, seeded."""
    ph = rnd.uniform(0, math.pi * 2)
    pts = []
    for i in range(41):
        x = w * i / 40
        y = h * (amp + amp * 0.9 * math.sin(ph + waves * math.pi * 2 * i / 40) + rnd.uniform(-0.012, 0.012))
        pts.append(f"{x:.1f},{y:.1f}")
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="width:100%;height:100%"><polygon points="0,{h} {" ".join(pts)} {w},{h}" fill="{color}"/></svg>'


def scallop_strip(color, n=40, w=1000, h=40, down=True):
    """a paper band with a row of scallops hanging off it (bunting / lace edge); down=False points them up."""
    r, band = w / n / 2, h * 0.4
    arcs = "".join(f"A{r:.2f},{h - band:.2f} 0 0 1 {w - (k + 1) * 2 * r:.2f},{band:.2f} " for k in range(n))
    flip = "" if down else "transform:scaleY(-1);"
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="width:100%;height:100%;{flip}"><path d="M0,0 H{w} V{band:.2f} {arcs} Z" fill="{color}"/></svg>'


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def counter(X, sel, t, a, b, dur=1.0, dec=0):
    js = f"o.v.toFixed({dec})" if dec else "Math.round(o.v).toLocaleString('en-US')"
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power3.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def cutword(X, text, cls="cut", num_cls="n"):
    """paper-cut letters: every glyph its own piece of paper with a slight seeded tilt; digits use the number face."""
    out = []
    for ch in str(text):
        if not ch.strip(): out.append(" "); continue
        rot = X.rand.uniform(-2.5, 2.5)
        k = num_cls if (ch.isdigit() or ch in ".,%") else "c"
        out.append(f'<i class="{k}" style="transform:rotate({rot:.2f}deg)">{X.rich(ch)}</i>')
    return "".join(out)


def page(X, b, cid, t, d, inner, kind="red", enter="slide", cls=""):
    """one paper page: deckled sheet, furniture, layered content; it slides / folds over the previous page."""
    from h9 import fit  # noqa: F401  (styles import the fit layer for adaptive sizing)
    X.css("papercut", CSS)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    sec = meta.get("section", "节庆经济"); src = b.get("src", meta.get("src", ""))
    X.used_text.update(sec + src + "0123456789/·" + X.channel + "来源：")
    clip = deckle(X.rand, 48, 0.35)
    furn = (f'<div class="pc-hd"><div class="tag"><b>{X.rich(X.channel)}</b>{X.rich(sec)}</div><div class="pg">{i + 1:02d}/{n:02d}</div></div>'
            + (f'<div class="pc-ft">来源：{X.rich(src)}</div>' if src else ""))
    html = (f'<div class="pcw"><div class="pc {kind} {cls}" style="clip-path:{clip}"><div class="sheet" style="background-image:{noise_bg(0.16 if kind == "cream" else 0.12, i + 3)}"></div>'
            f'<div class="cam">{inner}</div>{furn}</div></div>')
    D = X.duration or (t + d)
    ext = min(d + 0.7, max(d, D - t))           # stay under the next page while it slides in
    X.clip(cid, t, ext, html, "scene", 2 + i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    if i > 0:
        if enter == "fold":
            X.tw(f'tl.from("{s} .pcw", {{rotationX:-82, transformOrigin:"50% 0%", duration:0.7, ease:"expo.out"}}, {t:.3f});')
        elif enter == "side":
            X.tw(f'tl.from("{s} .pcw", {{xPercent:104, rotation:2.5, duration:0.6, ease:"expo.out"}}, {t:.3f});')
        else:
            X.tw(f'tl.from("{s} .pcw", {{yPercent:104, rotation:-2, duration:0.6, ease:"expo.out"}}, {t:.3f});')
        X.sfx(t, "transition")
    return s


def dolly(X, s, t, d, layers, push=(1.06, 1.0)):
    """camera through paper: the page scales, and each layer drifts by its depth (deep = slow)."""
    a, b_ = push
    X.tw(f'tl.fromTo("{s} .cam", {{scale:{a}}}, {{scale:{b_}, duration:{d:.2f}, ease:"power2.out"}}, {t:.3f});')
    for sel, depth in layers:
        X.tw(f'tl.fromTo("{s} {sel}", {{y:{18 * depth:.1f}, x:{-10 * depth:.1f}}}, {{y:{-12 * depth:.1f}, x:{10 * depth:.1f}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


def sway(X, sel, t, d, deg=4, period=1.6):
    rep = max(1, int(d / period))
    X.tw(f'tl.fromTo("{sel}", {{rotation:{-deg}}}, {{rotation:{deg}, duration:{period:.2f}, ease:"sine.inOut", yoyo:true, repeat:{rep}, transformOrigin:"50% 0%"}}, {t:.3f});')


# ---------------------------------------------------------------- scenes
def hook(b, X, t, d, cid):
    """开场：红纸夜色，窗花在背后转，灯笼摇；先落一个小标签，再从地面折起巨大的剪纸数字。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    X.css("pc-hook", """
.pc-hook .fl1 { width:780px; height:780px; left:-200px; top:-260px; }
.pc-hook .fl2 { width:420px; height:420px; right:-110px; top:520px; }
.pc-hook .lan { width:120px; height:190px; top:-20px; }
.pc-hook .hl { left:0; right:0; bottom:0; }
.pc-hook .cl { width:260px; height:130px; }
.pc-hook .big { position:absolute; left:0; right:0; text-align:center; perspective:1400px; }
.pc-hook .big .c, .pc-hook .big .n { transform-origin:50% 100%; }
#root.v .pc-hook .fl1 { width:820px; height:820px; left:-300px; top:-180px; }
#root.v .pc-hook .fl2 { width:420px; height:420px; right:-160px; top:760px; }
""")
    sm, big = b.get("small", ""), b.get("big", "")
    bw = (W - 192) if not P else (W - 112)
    f = fit.fit_text(big, bw, (360 if not P else 360), 380 if not P else 360, max_lines=2)
    hs = [(0.42, "#9e1a13", 1), (0.30, "#b8261c", 2), (0.17, "#f3ede1", 3)] if not P else [(0.40, "#9e1a13", 1), (0.30, "#b8261c", 2), (0.20, "#f3ede1", 3)]
    hl = "".join(f'<div class="lay hl h{k} sh{k}" style="height:{int(H * hh)}px">{hills(X.rand, 1000, 300, col, waves=2 + k)}</div>' for hh, col, k in hs)
    lx = [0.66, 0.78, 0.9] if not P else [0.56, 0.72, 0.88]
    lans = "".join(f'<div class="lay lan sh2" data-k="{k}" style="left:{int(W * x) - 60}px;top:{-20 + 60 * (k % 2)}px">{lantern()}</div>' for k, x in enumerate(lx))
    clouds = (f'<div class="lay cl cl1 sh1" style="left:{int(W * 0.08)}px;top:{int(H * (0.44 if not P else 0.34))}px">{cloud(cid + "a", "#f3ede1")}</div>'
              f'<div class="lay cl cl2 sh1" style="left:{int(W * 0.62)}px;top:{int(H * (0.52 if not P else 0.47))}px">{cloud(cid + "b", "#e0452f")}</div>')
    ytxt = int(H * (0.30 if not P else 0.33))
    inner = (f'<div class="lay fl1 sh2">{flower(cid + "f1", "#d8463a")}</div><div class="lay fl2 sh1">{flower(cid + "f2", "#a51d15", 6)}</div>'
             f'{clouds}{lans}{hl}'
             + (f'<div class="chip sh1 small" style="left:50%;top:{ytxt}px;transform:translateX(-50%)">{X.rich(sm)}</div>' if sm else "") +
             f'<div class="big cut" style="top:{ytxt + 90}px;font-size:{f.px}px;line-height:1.05">{"<br>".join(cutword(X, x) for x in f.lines)}</div>')
    s = page(X, b, cid, t, d, inner, "red", cls="pc-hook")
    ts, tb = T(X, b, "at_small", t, t + 0.1), T(X, b, "at_big", t, t + 0.6)
    X.tw(f'tl.from("{s} .small", {{y:-40, rotation:-6, opacity:0, duration:0.5, ease:"back.out(1.8)"}}, {max(t, ts - 0.2):.3f});')
    X.sfx(max(t, ts - 0.2), "pop")
    X.tw(f'tl.from("{s} .big .c, {s} .big .n", {{rotationX:-95, opacity:0, duration:0.6, ease:"back.out(1.4)", stagger:0.07}}, {max(t + 0.15, tb - 0.35):.3f});')
    X.sfx(max(t + 0.15, tb - 0.3), "slam")
    X.tw(f'tl.fromTo("{s} .fl1", {{rotation:0}}, {{rotation:24, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .fl2", {{rotation:0}}, {{rotation:-30, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    for k in range(3): sway(X, f"{s} .lan[data-k='{k}']", t, d + 0.7, 3 + k, 1.4 + 0.3 * k)
    X.tw(f'tl.fromTo("{s} .cl1", {{x:-40}}, {{x:60, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .cl2", {{x:40}}, {{x:-50, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hl", {{yPercent:60, duration:0.9, ease:"expo.out", stagger:0.08}}, {t:.3f});')
    dolly(X, s, t, d + 0.7, [(".h1", 0.4), (".h2", 0.8), (".h3", 1.4)], push=(1.08, 1.0))


def tickets(b, X, t, d, cid):
    """两张剪纸票根：数字随口播滚动，最后一枚"纪录"印章砸下来；手写批注画出同比。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    items = b.get("items", [])[:3] or [{"label": "票房", "value": 0, "unit": ""}]
    n = len(items)
    X.css("pc-tix", """
.pc-tix .bunt { left:-20px; right:-20px; top:96px; height:46px; }
.pc-tix .edge { left:-20px; right:-20px; bottom:-2px; height:34px; }
.pc-tix .kick { position:absolute; font-family:var(--f-display); color:var(--ink); white-space:nowrap; }
.pc-tix .kick small { display:block; font-family:var(--f-body); font-weight:700; font-size:30px; color:var(--deep); margin-top:12px; }
.pc-tix .tk { position:absolute; }
.pc-tix .tk .body { position:absolute; inset:0; background:var(--red);
  -webkit-mask:radial-gradient(circle at 0 50%, transparent 26px, #000 27px) left/51% 100% no-repeat, radial-gradient(circle at 100% 50%, transparent 26px, #000 27px) right/51% 100% no-repeat; }
.pc-tix .tk .in { position:absolute; inset:18px 44px; border:3px dashed rgba(251,247,238,.55); display:flex; flex-direction:column; justify-content:center; padding:0 26px; }
.pc-tix .tk .lb { font-family:var(--f-display); color:var(--cream); white-space:nowrap; }
.pc-tix .tk .vl { font-family:var(--f-num); color:var(--cream); line-height:1; white-space:nowrap; text-shadow:0 4px 0 var(--deep); }
.pc-tix .tk .vl small { font-family:var(--f-display); margin-left:10px; }
.pc-tix .seal { position:absolute; width:210px; height:210px; border:9px double var(--red); color:var(--red); display:grid; place-items:center;
  font-family:var(--f-serif); font-weight:900; font-size:76px; line-height:.95; text-align:center; background:rgba(251,247,238,.6); }
""")
    kx, ky = (96, 170) if not P else (56, 290)
    title = fit.fit_text(b.get("title", ""), W - 2 * kx - (0 if P else 600), 90, 66, max_lines=1)
    sub = b.get("sub", "")
    if not P:
        tw, th, gap = (min(800, (W - 192 - (n - 1) * 50) // n), 340 if n < 3 else 300, 50)
        x0 = (W - (n * tw + (n - 1) * gap)) // 2; ys = [400 if n < 3 else 420] * n; xs = [x0 + k * (tw + gap) for k in range(n)]
    else:
        th, gap, y0 = (300, 70, 520) if n < 3 else (220, 84, 470)
        tw = W - 112; xs = [56] * n; ys = [y0 + k * (th + gap) for k in range(n)]
    tix = ""
    for k, it in enumerate(items):
        lb = fit.fit_text(it.get("label", ""), tw - 160, 60, 40, max_lines=1)
        vt = f'{it.get("value", "")}'
        vf = fit.fit_text(vt + "  " + it.get("unit", ""), tw - 170, th * 0.5, 170, max_lines=1, mono=True)
        rot = (-3 + 6 * k / max(1, n - 1)) if n > 1 else -2
        tix += (f'<div class="tk sh2" data-k="{k}" style="left:{xs[k]}px;top:{ys[k]}px;width:{tw}px;height:{th}px;transform:rotate({rot:.1f}deg)">'
                f'<div class="body"></div><div class="in"><div class="lb" style="font-size:{lb.px}px">{X.rich(it.get("label", ""))}</div>'
                f'<div class="vl" style="font-size:{vf.px}px"><span class="v">0</span><small style="font-size:{int(vf.px * 0.36)}px">{X.rich(it.get("unit", ""))}</small></div></div></div>')
        if it.get("note"):
            nx = xs[k] + tw - 270; ny = ys[k] + th + (18 if not P else 30)
            tix += f'<div class="note nt" data-k="{k}" style="left:{nx}px;top:{ny}px;font-size:34px">{X.rich(it["note"])}</div>'
    sx, sy = (xs[-1] + tw - 140, ys[-1] - 90) if not P else (W - 330, ys[0] - 150)
    inner = (f'<div class="lay bunt sh1">{scallop_strip("#c62a1f", 24, 1000, 46)}</div>'
             f'<div class="kick" style="left:{kx}px;top:{ky}px;font-size:{title.px}px">{X.rich(title.lines[0] if title.lines else "")}<small>{X.rich(sub)}</small></div>'
             f'{tix}<div class="seal sh2" style="left:{sx}px;top:{sy}px">{X.rich(b.get("seal", "纪录"))}</div>')
    s = page(X, b, cid, t, d, inner, "cream", "slide", cls="pc-tix")
    X.tw(f'tl.from("{s} .kick", {{x:-40, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .bunt", {{yPercent:-120, duration:0.6, ease:"back.out(1.6)"}}, {t + 0.2:.3f});')
    sway(X, f"{s} .bunt", t, d + 0.7, 0.6, 1.8)
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.6 + k * 0.9)
        X.tw(f'tl.from("{s} .tk[data-k=\'{k}\']", {{x:{(-1 if k % 2 == 0 else 1) * 380}, y:40, rotation:{(-12 if k % 2 == 0 else 12)}, opacity:0, duration:0.6, ease:"expo.out"}}, {max(t + 0.3, tk - 0.45):.3f});')
        X.sfx(max(t + 0.3, tk - 0.45), "enter")
        v = it.get("value", 0)
        try: fv = float(str(v).replace(",", "")); dec = len(str(v).split(".")[1]) if "." in str(v) else 0
        except ValueError: fv, dec = None, 0
        if fv is not None: counter(X, f"{s} .tk[data-k='{k}'] .v", max(t + 0.35, tk - 0.3), 0, fv, dur=1.0, dec=dec)
        else: X.tw(f'tl.set("{s} .tk[data-k=\'{k}\'] .v", {{textContent:"{v}"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .nt[data-k=\'{k}\']", {{y:16, opacity:0, rotation:-4, duration:0.5, ease:"back.out(2)"}}, {max(t + 0.5, tk + 0.6):.3f});')
    tsl = T(X, b, "at_seal", t, t + d * 0.75)
    X.tw(f'tl.fromTo("{s} .seal", {{scale:2.6, rotation:-30, opacity:0}}, {{scale:1, rotation:-9, opacity:1, duration:0.32, ease:"expo.out"}}, {tsl - 0.12:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{x:0}}, {{keyframes:[{{x:-10, duration:0.04}}, {{x:8, duration:0.04}}, {{x:-3, duration:0.04}}, {{x:0, duration:0.05}}]}}, {tsl + 0.18:.3f});')
    X.sfx(tsl + 0.15, "slam")
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1.0}}, {{scale:1.045, duration:{d + 0.7:.2f}, ease:"none", transformOrigin:"50% 55%"}}, {t:.3f});')


def calendar(b, X, t, d, cid):
    """撕日历：前一页"除夕"被撕掉飞走，露出"大年初一"；右边剪纸大数字砸下，纸屑飞，鞭炮串摇。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    X.css("pc-cal", """
.pc-cal .cal { position:absolute; }
.pc-cal .pgx { position:absolute; inset:0; background:var(--cream); }
.pc-cal .pgx .band { position:absolute; left:0; right:0; top:0; height:22%; background:var(--red); display:grid; place-items:center; font-family:var(--f-display); color:var(--cream); }
.pc-cal .pgx .day { position:absolute; left:0; right:0; top:24%; text-align:center; font-family:var(--f-num); color:var(--red); line-height:1; }
.pc-cal .pgx .lbl { position:absolute; left:0; right:0; bottom:9%; text-align:center; font-family:var(--f-display); color:var(--ink); }
.pc-cal .ring { position:absolute; top:-26px; width:34px; height:58px; border-radius:17px; background:#3b2a18; }
.pc-cal .num { position:absolute; text-align:left; }
.pc-cal .sub { position:absolute; font-family:var(--f-display); color:var(--cream); white-space:nowrap; }
.pc-cal .fc { position:absolute; width:70px; }
.pc-cal .fc i { display:block; width:46px; height:76px; margin:0 auto 6px; border-radius:9px; background:linear-gradient(90deg, #b8261c, #e0452f 45%, #9e1a13);
  box-shadow:inset 0 9px 0 #d6a23c, inset 0 -9px 0 #d6a23c; }
.pc-cal .fc .str { position:absolute; left:34px; top:-60px; bottom:0; width:3px; background:#3b2a18; }
.pc-cal .bits i { position:absolute; width:18px; height:18px; display:block; }
""")
    if not P:
        cx, cy, cw, ch = 300, 220, 520, 600
        nx, ny, nw = 930, 330, W - 930 - 230
    else:
        cx, cy, cw, ch = 210, 300, 660, 640
        nx, ny, nw = 56, 1000, W - 112 - 120
    front, back = b.get("front", {}), b.get("back", {})
    def pg(p, cls):
        bf = fit.fit_text(p.get("band", ""), cw - 60, ch * 0.18, 64, max_lines=1)
        lf = fit.fit_text(p.get("label", ""), cw - 60, ch * 0.12, 46, max_lines=1)
        return (f'<div class="pgx {cls}" style="clip-path:{deckle(X.rand, 30, 0.6, "b")}"><div class="band" style="font-size:{bf.px}px">{X.rich(p.get("band", ""))}</div>'
                f'<div class="day" style="font-size:{int(ch * 0.42)}px">{X.rich(p.get("day", ""))}</div><div class="lbl" style="font-size:{lf.px}px">{X.rich(p.get("label", ""))}</div></div>')
    big = b.get("big", "")
    bf = fit.fit_text(big, nw, 330 if not P else 260, 300 if not P else 230, max_lines=1)
    sf = fit.fit_text(b.get("sub", ""), nw, 120, 42, max_lines=2)
    rnd = X.rand
    bits = "".join(f'<i style="left:{rnd.uniform(0, 100):.1f}%;top:{rnd.uniform(0, 60):.1f}%;background:{rnd.choice(["#fbf7ee", "#d6a23c", "#e0452f"])};'
                   f'transform:rotate({rnd.uniform(0, 90):.0f}deg)"></i>' for _ in range(26))
    fcx, fcy = (W - 150, 150) if not P else (W - 120, 300)
    inner = (f'<div class="lay fl sh1" style="width:640px;height:640px;left:{W - 520 if not P else -260}px;top:{H - 560 if not P else 1150}px">{flower(cid + "f", "#a51d15", 10)}</div>'
             f'<div class="cal sh3" style="left:{cx}px;top:{cy}px;width:{cw}px;height:{ch}px">{pg(back, "back")}{pg(front, "front")}'
             f'<i class="ring" style="left:{cw * 0.25 - 17:.0f}px"></i><i class="ring" style="left:{cw * 0.75 - 17:.0f}px"></i></div>'
             f'<div class="num cut" style="left:{nx}px;top:{ny}px;font-size:{bf.px}px">{cutword(X, bf.lines[0] if bf.lines else "")}</div>'
             f'<div class="sub" style="left:{nx + 6}px;top:{ny + bf.px + 40}px;font-size:{sf.px}px;line-height:1.3">{"<br>".join(X.rich(x) for x in sf.lines)}</div>'
             f'<div class="fc sh1" style="left:{fcx}px;top:{fcy}px"><i class="str"></i>{"<i></i>" * (8 if not P else 6)}</div>'
             f'<div class="bits" style="position:absolute;left:{nx}px;top:{ny - 120}px;width:{nw}px;height:{bf.px + 200}px">{bits}</div>')
    s = page(X, b, cid, t, d, inner, "red", "fold", cls="pc-cal")
    tt, tn = T(X, b, "at_tear", t, t + 0.4), T(X, b, "at_big", t, t + d * 0.6)
    X.tw(f'tl.from("{s} .cal", {{y:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.to("{s} .cal .front", {{y:-80, x:-420, rotation:-28, opacity:0, duration:0.75, ease:"power2.in", transformOrigin:"20% 0%"}}, {max(t + 0.5, tt):.3f});')
    X.sfx(max(t + 0.5, tt), "tear")
    X.tw(f'tl.from("{s} .num .c, {s} .num .n", {{y:-160, rotation:-20, opacity:0, duration:0.5, ease:"back.out(1.6)", stagger:0.06}}, {tn - 0.3:.3f});')
    X.sfx(tn - 0.2, "slam")
    X.tw(f'tl.from("{s} .sub", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {tn + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .bits i", {{y:-40, opacity:0, scale:0.4}}, {{y:"+=240", rotation:"+=220", opacity:1, scale:1, duration:1.6, ease:"power1.in", stagger:{{each:0.03, from:"center"}}}}, {tn - 0.2:.3f});')
    sway(X, f"{s} .fc", t, d + 0.7, 5, 1.2)
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0}}, {{rotation:-28, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    dolly(X, s, t, d + 0.7, [(".fl", 0.4), (".cal", 1.0)], push=(1.0, 1.05))


def share(b, X, t, d, cid):
    """圆形窗花被切出一块：那一块抬起来、投下更深的影子，旁边写出占比。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    pct = float(b.get("pct", 50))
    X.css("pc-share", """
.pc-share .disc { position:absolute; }
.pc-share .lab { position:absolute; }
.pc-share .lab .p { font-family:var(--f-num); color:var(--red); line-height:1; white-space:nowrap; text-shadow:0 5px 0 #7a140f, 0 14px 20px rgba(60,10,5,.22); }
.pc-share .lab .p small { font-size:.45em; }
.pc-share .lab .w { font-family:var(--f-display); color:var(--ink); white-space:nowrap; margin-top:14px; }
.pc-share .rest { position:absolute; font-family:var(--f-display); color:var(--muted); white-space:nowrap; }
.pc-share .kick { position:absolute; font-family:var(--f-display); color:var(--ink); white-space:nowrap; }
""")
    if not P: dx, dy, dd = 210, 190, 640
    else: dx, dy, dd = 250, 300, 560
    a1 = -90 + 360 * pct / 100
    def pt(a, r=96): return 100 + r * math.cos(math.radians(a)), 100 + r * math.sin(math.radians(a))
    x1, y1 = pt(-90); x2, y2 = pt(a1)
    big_arc = 1 if pct > 50 else 0
    hot = f"M100,100 L{x1:.2f},{y1:.2f} A96,96 0 {big_arc} 1 {x2:.2f},{y2:.2f} Z"
    rest = f"M100,100 L{x2:.2f},{y2:.2f} A96,96 0 {1 - big_arc} 1 {x1:.2f},{y1:.2f} Z"
    mid = math.radians(-90 + 180 * pct / 100)
    lx, ly = math.cos(mid) * 50, math.sin(mid) * 50
    holes = "".join(f'<circle cx="{100 + 70 * math.cos(2 * math.pi * k / 16):.1f}" cy="{100 + 70 * math.sin(2 * math.pi * k / 16):.1f}" r="5"/>' for k in range(16))
    disc = (f'<svg viewBox="0 0 200 200"><defs><mask id="d{cid}"><rect width="200" height="200" fill="#fff"/><g fill="#000">{holes}<circle cx="100" cy="100" r="9"/></g></mask></defs>'
            f'<g mask="url(#d{cid})"><path class="rest" d="{rest}" fill="#b8261c"/><g class="hotg"><path d="{hot}" fill="#e0452f"/></g></g></svg>')
    lab = b.get("label", ""); restl = b.get("rest", "")
    if not P: lx0, ly0, lw = dx + dd + 90, 300, W - (dx + dd + 90) - 110
    else: lx0, ly0, lw = 56, dy + dd + 90, W - 112 - 120
    wf = fit.fit_text(lab, lw, 120 if not P else 70, 80 if not P else 64, max_lines=2 if not P else 1)
    rf = fit.fit_text(restl, lw, 60, 40, max_lines=1)
    kf = fit.fit_text(b.get("kicker", ""), (W - 192) if not P else (W - 112), 70, 52, max_lines=1)
    pf = 260 if not P else 180
    inner = (f'<div class="kick" style="left:{96 if not P else 56}px;top:{150 if not P else 290}px;font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else "")}</div>'
             f'<div class="disc sh2" style="left:{dx}px;top:{dy + (40 if not P else 60)}px;width:{dd}px;height:{dd}px">{disc}</div>'
             f'<div class="lab" style="left:{lx0}px;top:{ly0}px"><div class="p" style="font-size:{pf}px"><span class="v">0</span><small>%</small></div>'
             f'<div class="w" style="font-size:{wf.px}px;line-height:1.2">{"<br>".join(X.rich(x) for x in wf.lines)}</div></div>'
             f'<div class="rest" style="left:{lx0}px;top:{ly0 + pf + wf.px * wf.n * 1.2 + 50:.0f}px;font-size:{rf.px}px">{X.rich(restl)}</div>')
    s = page(X, b, cid, t, d, inner, "cream", "side", cls="pc-share")
    th = T(X, b, "at_hot", t, t + d * 0.45)
    X.tw(f'tl.from("{s} .kick", {{x:-40, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .disc", {{scale:0.6, rotation:-90, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.2:.3f});')
    X.tw(f'tl.fromTo("{s} .disc", {{rotation:0}}, {{rotation:8, duration:{d + 0.7:.2f}, ease:"none"}}, {t + 1.0:.3f});')
    X.tw(f'tl.to("{s} .hotg", {{x:{lx * 0.5:.1f}, y:{ly * 0.5:.1f}, duration:0.6, ease:"back.out(1.6)", filter:"drop-shadow(0 18px 14px rgba(60,10,5,.45))"}}, {th - 0.2:.3f});')
    X.sfx(th - 0.2, "pop")
    counter(X, f"{s} .lab .v", th - 0.25, 0, pct, dur=0.9, dec=1 if pct != int(pct) else 0)
    X.tw(f'tl.from("{s} .lab .w", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {th + 0.2:.3f});')
    X.tw(f'tl.from("{s} .rest", {{opacity:0, duration:0.5}}, {th + 0.6:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1.0}}, {{scale:1.05, duration:{d + 0.7:.2f}, ease:"none", transformOrigin:"40% 50%"}}, {t:.3f});')


FLAME = "M50 160 C10 130 18 92 40 70 C38 92 50 100 56 96 C48 66 60 30 86 6 C80 40 96 58 102 78 C108 64 106 52 102 40 C128 70 132 116 104 144 C94 156 74 164 50 160 Z"


def banner(b, X, t, d, cid):
    """卷轴横幅从中间展开写出片名；下面剪纸大数字；后面一排纸火焰层层升起、轻轻摇。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    X.css("pc-ban", """
.pc-ban .scroll { position:absolute; }
.pc-ban .scroll .paper { position:absolute; inset:0; background:var(--cream); border-top:8px solid var(--gold); border-bottom:8px solid var(--gold);
  display:grid; place-items:center; font-family:var(--f-display); color:var(--red); white-space:nowrap; }
.pc-ban .scroll .rod { position:absolute; top:-18px; bottom:-18px; width:34px; border-radius:17px; background:linear-gradient(90deg, #8d1711, #c62a1f 50%, #8d1711); }
.pc-ban .num { position:absolute; left:0; right:0; text-align:center; }
.pc-ban .fls { position:absolute; left:0; right:0; bottom:-20px; height:52%; }
.pc-ban .fls svg { position:absolute; bottom:0; transform-origin:50% 100%; }
.pc-ban .fls.back { height:66%; }
.pc-ban .sub { position:absolute; left:0; right:0; text-align:center; font-family:var(--f-display); color:var(--cream); white-space:nowrap; }
.pc-ban .fw { position:absolute; }
#root.v .pc-ban .fls { bottom:300px; height:34%; } #root.v .pc-ban .fls.back { height:46%; }
""")
    tf = fit.fit_text(b.get("title", ""), (1200 if not P else W - 200) - 120, 120, 92, max_lines=1)
    sw = min((1300 if not P else W - 150), int(tf.px * 1.05 * max(1, sum(1 for c in b.get("title", "") if c.strip())) + 180))
    sx, sy, sh = (W - sw) // 2, (210 if not P else 330), 150
    nf = fit.fit_text(b.get("big", ""), W - 192, 300, 300 if not P else 220, max_lines=1)
    cols = ["#d6a23c", "#e0452f", "#f3ede1", "#b8261c", "#d6a23c", "#e0452f", "#f3ede1"]
    k = 7 if not P else 5
    fw_ = 220 if not P else 250
    fls = "".join(f'<svg class="sh1" data-k="{j}" viewBox="0 0 140 170" style="left:{(j + 0.5) * W / k - fw_ / 2:.0f}px;width:{fw_ + 60 * (j % 2)}px"><path d="{FLAME}" fill="{cols[j % len(cols)]}"/></svg>' for j in range(k))
    back = "".join(f'<svg data-k="{j}" viewBox="0 0 140 170" style="left:{j * W / (k - 1) - fw_ * 0.7:.0f}px;width:{fw_ * 1.4:.0f}px"><path d="{FLAME}" fill="{["#9e1a13", "#8d1711"][j % 2]}"/></svg>' for j in range(k))
    ny = sy + sh + (90 if not P else 120)
    sub = b.get("sub", "")
    sf = fit.fit_text(sub, W - 192, 60, 44 if not P else 40, max_lines=1) if sub else None
    fws = ((-180, -200, 560), (W - 300, H - 760, 520)) if not P else ((-220, 120, 520), (W - 260, 860, 480))
    inner = (f'<div class="fw sh1 fwa" style="left:{fws[0][0]}px;top:{fws[0][1]}px;width:{fws[0][2]}px;height:{fws[0][2]}px">{flower(cid + "a", "#a51d15", 10)}</div>'
             f'<div class="fw sh1 fwb" style="left:{fws[1][0]}px;top:{fws[1][1]}px;width:{fws[1][2]}px;height:{fws[1][2]}px">{flower(cid + "b", "#d8463a", 8)}</div>'
             f'<div class="fls back">{back}</div><div class="fls front">{fls}</div>'
             + (f'<div class="sub" style="top:{ny + nf.px + 40}px;font-size:{sf.px}px">{X.rich(sf.lines[0] if sf.lines else "")}</div>' if sf else "") +
             f'<div class="scroll sh2" style="left:{sx}px;top:{sy}px;width:{sw}px;height:{sh}px"><div class="paper" style="font-size:{tf.px}px">{X.rich(tf.lines[0] if tf.lines else "")}</div>'
             f'<i class="rod l" style="left:-17px"></i><i class="rod r" style="right:-17px"></i></div>'
             f'<div class="num cut" style="top:{ny}px;font-size:{nf.px}px">{cutword(X, nf.lines[0] if nf.lines else "")}</div>')
    s = page(X, b, cid, t, d, inner, "red", "slide", cls="pc-ban")
    tn = T(X, b, "at_big", t, t + d * 0.55)
    X.tw(f'tl.fromTo("{s} .scroll .paper", {{clipPath:"inset(0 50% 0 50%)"}}, {{clipPath:"inset(0 0% 0 0%)", duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .scroll .l", {{x:{sw / 2:.0f}}}, {{x:0, duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .scroll .r", {{x:{-sw / 2:.0f}}}, {{x:0, duration:0.8, ease:"power3.inOut"}}, {t + 0.3:.3f});')
    X.sfx(t + 0.3, "enter")
    X.tw(f'tl.from("{s} .fls.back svg", {{scaleY:0, duration:0.8, ease:"back.out(1.5)", stagger:{{each:0.05, from:"edges"}}}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .fls.front svg", {{scaleY:0, duration:0.7, ease:"back.out(1.7)", stagger:{{each:0.06, from:"center"}}}}, {t + 0.2:.3f});')
    rep = max(1, int((d + 0.7) / 0.9))
    for row, ph in (("front", 0.0), ("back", 0.22)):
        for j in range(k):
            X.tw(f'tl.fromTo("{s} .fls.{row} svg[data-k=\'{j}\']", {{scaleY:1, skewX:0}}, {{scaleY:{1.06 + 0.04 * (j % 3):.2f}, skewX:{(-3 if (j + (row == "back")) % 2 else 3)}, duration:0.45, ease:"sine.inOut", yoyo:true, repeat:{rep * 2}}}, {t + 0.9 + ph + 0.07 * j:.3f});')
    X.tw(f'tl.fromTo("{s} .fwa", {{rotation:0}}, {{rotation:30, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .fwb", {{rotation:0}}, {{rotation:-36, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    if sf: X.tw(f'tl.from("{s} .sub", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {tn + 0.35:.3f});')
    X.tw(f'tl.from("{s} .num .c, {s} .num .n", {{rotationX:-95, opacity:0, duration:0.55, ease:"back.out(1.4)", stagger:0.06, transformOrigin:"50% 100%"}}, {tn - 0.35:.3f});')
    X.sfx(tn - 0.3, "slam")
    dolly(X, s, t, d + 0.7, [(".fw", 0.3), (".fls.back", 0.6), (".fls.front", 1.0), (".scroll", 1.3)], push=(1.06, 1.0))


def stacks(b, X, t, d, cid):
    """纸张一层层落下叠成排行：高度按数值，冠军顶上一朵小窗花。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    items = b.get("items", [])[:6] or [{"name": "—", "value": 1}]
    n = len(items)
    X.css("pc-stk", """
.pc-stk .col { position:absolute; bottom:0; }
.pc-stk .col .sht { position:absolute; left:0; right:0; box-shadow:0 -3px 0 rgba(70,15,8,.18) inset, 0 4px 6px rgba(70,15,8,.22); }
.pc-stk .col .lb { position:absolute; left:-30px; right:-30px; text-align:center; }
.pc-stk .col .rk { display:inline-block; font-family:var(--f-num); font-size:24px; color:var(--cream); background:var(--ink); padding:2px 10px; }
.pc-stk .col .nm { font-family:var(--f-display); color:var(--ink); white-space:nowrap; margin-top:6px; }
.pc-stk .col .vl { font-family:var(--f-num); color:var(--red); white-space:nowrap; line-height:1; }
.pc-stk .base { position:absolute; height:14px; background:var(--ink); }
.pc-stk .kick { position:absolute; font-family:var(--f-display); color:var(--ink); white-space:nowrap; }
.pc-stk .crown { position:absolute; width:110px; height:110px; }
""")
    vmax = max(float(it.get("value", 0) or 0) for it in items) or 1
    if not P: base_y, hmax, area_x, area_w = 930, 400, 160, W - 320
    else: base_y, hmax, area_x, area_w = 1260, 520, 56, W - 112 - 100
    cw = min(300, area_w // n - 40); gap = (area_w - n * cw) / max(1, n)
    kf = fit.fit_text(b.get("kicker", ""), (W - 192) if not P else (W - 112), 70, 52, max_lines=1)
    shades = ["#c62a1f", "#e0452f", "#b8261c", "#d6a23c"]
    cols = ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        h = max(32, int(hmax * v / vmax)); m = max(2, min(12, h // 40))
        x = area_x + gap / 2 + k * (cw + gap)
        sheets = "".join(f'<i class="sht" style="bottom:{j * (h / m):.1f}px;height:{h / m + 2:.1f}px;background:{shades[(j + k) % len(shades)]};transform:rotate({X.rand.uniform(-1.2, 1.2):.2f}deg)"></i>' for j in range(m))
        nf = fit.fit_text(it.get("name", ""), cw + 50, 60, 40, max_lines=2)
        vf = fit.fit_text(str(it.get("label", it.get("value", ""))), cw + 50, 80, 64, max_lines=1, mono=True)
        crown = f'<div class="crown sh1" style="left:{cw / 2 - 55:.0f}px;bottom:{h + 8}px">{flower(cid + "cr", "#d6a23c", 8)}</div>' if k == 0 else ""
        cols += (f'<div class="col" data-k="{k}" data-m="{m}" style="left:{x:.0f}px;top:{base_y - h}px;width:{cw}px;height:{h}px">{sheets}{crown}'
                 f'<div class="lb" style="bottom:{h + (128 if k == 0 else 16)}px"><span class="rk">{k + 1}</span>'
                 f'<div class="nm" style="font-size:{nf.px}px;line-height:1.15">{"<br>".join(X.rich(x_) for x_ in nf.lines)}</div>'
                 f'<div class="vl" style="font-size:{vf.px}px">{X.rich(vf.lines[0] if vf.lines else "")}</div></div></div>')
    inner = (f'<div class="kick" style="left:{96 if not P else 56}px;top:{150 if not P else 290}px;font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else "")}</div>'
             f'{cols}<div class="base" style="left:{area_x}px;width:{area_w}px;top:{base_y}px"></div>')
    s = page(X, b, cid, t, d, inner, "cream", "fold", cls="pc-stk")
    X.tw(f'tl.from("{s} .kick", {{x:-40, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{s} .base", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {t + 0.2:.3f});')
    for k, it in enumerate(items):
        tk = T(X, it, "at", t, t + 0.5 + min(0.8, max(0.25, (d - 1.4) / n)) * k)     # uncued items share the beat
        X.tw(f'tl.from("{s} .col[data-k=\'{k}\'] .sht", {{y:-260, opacity:0, rotation:"random(-8,8)", duration:0.32, ease:"power2.out", stagger:0.03}}, {max(t + 0.35, tk - 0.5):.3f});'.replace('"random(-8,8)"', f'{(-6 if k % 2 else 6)}'))
        X.tw(f'tl.from("{s} .col[data-k=\'{k}\'] .lb", {{y:30, opacity:0, duration:0.45, ease:"back.out(1.8)"}}, {max(t + 0.5, tk):.3f});')
        X.sfx(max(t + 0.35, tk - 0.5), "paper" if k else "enter")
    X.tw(f'tl.from("{s} .crown", {{scale:0, rotation:-90, duration:0.6, ease:"back.out(2)"}}, {T(X, items[0], "at", t, t + 0.5) + 0.5:.3f});')
    X.tw(f'tl.fromTo("{s} .crown", {{rotation:0}}, {{rotation:40, duration:{d + 0.7:.2f}, ease:"none"}}, {t + 1:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1.04}}, {{scale:1.0, duration:{d + 0.7:.2f}, ease:"power1.out", transformOrigin:"50% 80%"}}, {t:.3f});')


def thesis(b, X, t, d, cid):
    """判断句：两行剪纸大字；"平均"被一条纸条划掉，"最好的那一部"垫上金纸。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    X.css("pc-th", """
.pc-th .tx { position:absolute; left:0; right:0; text-align:center; }
.pc-th .ln { display:block; white-space:nowrap; }
.pc-th .st { position:relative; display:inline-block; }
.pc-th .st .strip { position:absolute; left:-4%; right:-4%; top:46%; height:.16em; background:var(--cream); transform-origin:0 50%; transform:rotate(-4deg);
  box-shadow:0 4px 0 var(--deep); }
.pc-th .em2 { position:relative; display:inline-block; }
.pc-th .em2 .band { position:absolute; left:-3%; right:-3%; top:8%; bottom:-6%; background:var(--gold); transform-origin:0 50%; z-index:0; box-shadow:0 6px 0 #9a6f1c; }
.pc-th .em2 .w { position:relative; z-index:1; color:var(--ink); text-shadow:none; }
.pc-th .fl { position:absolute; }
""")
    l1, l2, stw, emw = b.get("l1", ""), b.get("l2", ""), b.get("strike", ""), b.get("em", "")
    bw = (W - 192) if not P else (W - 112)
    f1 = fit.fit_text(l1, bw, 300, 150 if not P else 130, max_lines=1 if not P else 2)
    f2 = fit.fit_text(l2, bw, 300, 150 if not P else 130, max_lines=1 if not P else 2)
    def mark(line):
        h = X.rich(line)
        if stw and stw in line: h = h.replace(X.rich(stw), f'<span class="st">{X.rich(stw)}<i class="strip"></i></span>', 1)
        if emw and emw in line: h = h.replace(X.rich(emw), f'<span class="em2"><i class="band"></i><span class="w">{X.rich(emw)}</span></span>', 1)
        return h
    y1 = int(H * (0.27 if not P else 0.30)); y2 = y1 + int(f1.px * 1.2 * f1.n) + (50 if not P else 110)
    inner = (f'<div class="fl sh1" style="width:900px;height:900px;left:{(W - 900) // 2}px;top:{(H - 900) // 2 - 40}px;opacity:.55">{flower(cid + "f", "#a51d15", 12)}</div>'
             f'<div class="tx cut t1" style="top:{y1}px;font-size:{f1.px}px">{"".join(f"<span class=ln>{mark(x)}</span>" for x in f1.lines)}</div>'
             f'<div class="tx cut t2" style="top:{y2}px;font-size:{f2.px}px">{"".join(f"<span class=ln>{mark(x)}</span>" for x in f2.lines)}</div>')
    s = page(X, b, cid, t, d, inner, "red", "slide", cls="pc-th")
    ts, te = T(X, b, "at_strike", t, t + d * 0.35), T(X, b, "at_em", t, t + d * 0.7)
    X.tw(f'tl.from("{s} .t1 .ln", {{yPercent:110, rotationX:-60, opacity:0, duration:0.6, ease:"expo.out", stagger:0.1}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .t2 .ln", {{yPercent:110, rotationX:-60, opacity:0, duration:0.6, ease:"expo.out", stagger:0.1}}, {max(t + 0.6, te - 0.9):.3f});')
    X.tw(f'tl.from("{s} .strip", {{scaleX:0, duration:0.35, ease:"power3.out"}}, {ts:.3f});')
    X.sfx(ts, "tear")
    X.tw(f'tl.from("{s} .band", {{scaleX:0, duration:0.45, ease:"power3.out"}}, {te - 0.1:.3f});')
    X.sfx(te, "pop")
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0, scale:0.9}}, {{rotation:30, scale:1.05, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1.0}}, {{scale:1.04, duration:{d + 0.7:.2f}, ease:"none"}}, {t:.3f});')


def outro(b, X, t, d, cid):
    """落版：一枚红色剪纸印章 + 一句定位 + 关注纸签；主持人出场。"""
    from h9 import fit
    P = X.portrait; W, H = X.W, X.H
    X.css("pc-out", """
.pc-out .seal { position:absolute; background:var(--red); color:var(--cream); display:grid; place-items:center; text-align:center;
  font-family:var(--f-display); line-height:1.02; box-shadow:inset 0 0 0 10px var(--red), inset 0 0 0 14px var(--cream); }
.pc-out .sub { position:absolute; font-family:var(--f-display); color:var(--ink); white-space:nowrap; }
.pc-out .cta { position:absolute; font-size:40px; padding:12px 30px 14px; }
.pc-out .edge { left:-20px; right:-20px; height:40px; }
""")
    sz = 380 if not P else 420
    sx, sy = ((W - sz) // 2 - (260 if not P else 0), 210 if not P else 330)
    tl_ = b.get("title", X.channel)
    half = (len(tl_) + 1) // 2
    sf = fit.fit_text(b.get("sub", ""), (W - sx - 520) if not P else (W - 112), 70, 48, max_lines=1)     # landscape: stay clear of the host
    tx = sx if not P else 56
    fx_, fy_, fs_ = (W - 820, 140, 620) if not P else (-240, 1080, 640)
    inner = (f'<div class="lay fl sh1" style="left:{fx_}px;top:{fy_}px;width:{fs_}px;height:{fs_}px;opacity:.9">{flower(cid + "f", "#e8d9c2", 12)}</div>'
             f'<div class="lay edge sh1" style="top:96px">{scallop_strip("#c62a1f", 30, 1000, 40)}</div>'
             f'<div class="seal sh3" style="left:{sx}px;top:{sy}px;width:{sz}px;height:{sz}px;font-size:{int(sz * 0.27)}px">{X.rich(tl_[:half])}<br>{X.rich(tl_[half:])}</div>'
             f'<div class="sub" style="left:{tx}px;top:{sy + sz + 60}px;font-size:{sf.px}px">{X.rich(sf.lines[0] if sf.lines else "")}</div>'
             f'<div class="chip cta sh1" style="left:{tx}px;top:{sy + sz + 60 + sf.px + 40}px">{X.rich(b.get("cta", ""))}</div>')
    s = page(X, b, cid, t, d, inner, "cream", "fold", cls="pc-out")
    X.tw(f'tl.fromTo("{s} .seal", {{scale:2.2, rotation:-20, opacity:0}}, {{scale:1, rotation:-4, opacity:1, duration:0.4, ease:"expo.out"}}, {t + 0.25:.3f});')
    X.sfx(t + 0.35, "slam")
    X.tw(f'tl.from("{s} .sub", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("{s} .cta", {{scale:0.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.85:.3f});')
    X.tw(f'tl.from("{s} .fl", {{scale:0.7, opacity:0, duration:0.8, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .fl", {{rotation:0}}, {{rotation:24, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1.0}}, {{scale:1.03, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


SCENES = {"hook": hook, "tickets": tickets, "calendar": calendar, "share": share, "banner": banner, "stacks": stacks, "thesis": thesis, "outro": outro}


# ---------------------------------------------------------------- effects in this style (gallery cards / fx beats)
# four paper stocks for the effect themes: rice paper, festive red, indigo-dyed (蓝印) and gold foil (金纸)
STYLE["fx_themes"] = {
    "paper": {"bg": "#f3ede1", "fg": "#1e1b18", "muted": "#6c635a", "accent": "#c62a1f", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "#e2d6c2"},
    "red":   {"bg": "#c62a1f", "fg": "#fbf7ee", "muted": "rgba(251,247,238,.82)", "accent": "#f2c14e", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "rgba(251,247,238,.3)"},
    "ink":   {"bg": "#1d2940", "fg": "#f3ede1", "muted": "#a9b3c6", "accent": "#e8543f", "card": "#26324d", "card-fg": "#f3ede1", "line": "#34405c"},
    "lemon": {"bg": "#e9b949", "fg": "#2a1a0e", "muted": "#5e3f10", "accent": "#b3221a", "card": "#fbf7ee", "card-fg": "#1e1b18", "line": "rgba(42,26,14,.2)"},
}
# the cut-paper frame around a card, per stock: frame band, corner flowers (角花), header tag, caption strip, keyword marker, effect-id stub
FRAME = {
    "paper": {"frame": "#c62a1f", "corner": "#d6a23c", "tag": "#c62a1f", "tag-fg": "#fbf7ee", "tag-b": "#ffd77a", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#c62a1f", "em-fg": "#fbf7ee", "stub": "#1e1b18", "stub-fg": "#fbf7ee"},
    "red":   {"frame": "#fbf7ee", "corner": "#f2c14e", "tag": "#fbf7ee", "tag-fg": "#1e1b18", "tag-b": "#c62a1f", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#c62a1f", "em-fg": "#fbf7ee", "stub": "#1e1b18", "stub-fg": "#fbf7ee"},
    "ink":   {"frame": "#d6a23c", "corner": "#e8543f", "tag": "#d6a23c", "tag-fg": "#1d2940", "tag-b": "#8d1711", "cap": "#f3ede1", "cap-fg": "#1d2940",
              "em": "#e8543f", "em-fg": "#fbf7ee", "stub": "#f3ede1", "stub-fg": "#1d2940"},
    "lemon": {"frame": "#b3221a", "corner": "#fbf7ee", "tag": "#b3221a", "tag-fg": "#fbf7ee", "tag-b": "#ffd77a", "cap": "#fbf7ee", "cap-fg": "#1e1b18",
              "em": "#b3221a", "em-fg": "#fbf7ee", "stub": "#2a1a0e", "stub-fg": "#fbf7ee"},
}


def _b64svg(svg):
    import base64
    return 'url("data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode() + '")'


_WM = _b64svg(flower("wm", "#000", 12).replace("<svg ", "<svg xmlns='http://www.w3.org/2000/svg' ", 1))
_LACE = _b64svg("<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><path fill='#000' fill-rule='evenodd' "
                "d='M0 0H40V40H0Z M10 4.5a5.5 5.5 0 1 0 .01 0Z M30 24.5a5.5 5.5 0 1 0 .01 0Z M30 9l3 3-3 3-3-3Z M10 29l3 3-3 3-3-3Z'/></svg>")
_SHADE = "color-mix(in srgb, var(--bg) 58%, #2a0a06)"      # the paper's own drop: a darker shade of whatever stock it sits on

FX_CSS = r"""
/* the effect's ground is a sheet of paper: fibre texture + a large faint 窗花 cut into the corner */
.fx { background-image:__NOISE__ !important; background-size:340px !important; }
.fx::before { content:""; position:absolute; width:86vmin; height:86vmin; right:-22vmin; bottom:-30vmin; background:var(--fg); opacity:.06;
  -webkit-mask:__WM__ center/contain no-repeat; mask:__WM__ center/contain no-repeat; pointer-events:none; }
#root.v .fx::before { right:-30vmin; bottom:auto; top:13%; }
/* type is cut from paper: every headline casts a solid paper drop plus a soft shadow */
.fx .big, .fx .op .op-ep, .fx .op .op-t, .fx .dn .dnc b, .fx .iu .iub, .fx .nt-t, .fx .dn .dnt strong, .fx .iu .iutx {
  text-shadow:0 .05em 0 __SHADE__, 0 .12em .2em rgba(40,10,5,.24); }
.fx .big { letter-spacing:.01em; }
.fx .col > .sub { background:var(--card); color:var(--card-fg); padding:.7vmin 2vmin .8vmin; letter-spacing:.24em; transform:rotate(-1deg);
  box-shadow:0 .5vmin 0 __SHADE__, 0 1.4vmin 2vmin rgba(40,10,5,.2); font-family:var(--f-body); font-weight:700; }
/* burst: rays become cut paper strips, the ring a punched lace circle, the dots little paper diamonds */
.fx .ray b { border-radius:0; width:1.3vmin; left:-.65vmin; box-shadow:0 .5vmin 0 __SHADE__; }
.fx .ray:nth-child(even) b { background:var(--fg); height:5vmin; }
.fx .bu .ring { border:1.5vmin dotted var(--accent); }
.fx .bu .dot { border-radius:.2vmin; background:var(--accent); width:2.4vmin; height:2.4vmin; transform:rotate(var(--a)) translateY(-22vmin) rotate(45deg); box-shadow:0 .4vmin 0 __SHADE__; }
/* gooey: two paper discs with hollow-cut lace, the merged neck stays paper */
.fx .gw { filter:drop-shadow(0 .7vmin 0 __SHADE__) drop-shadow(0 1.8vmin 1.6vmin rgba(40,10,5,.25)); }
.fx .go { -webkit-mask:__LACE__ 0 0/4.2vmin 4.2vmin repeat; mask:__LACE__ 0 0/4.2vmin 4.2vmin repeat; }
/* donut: the ring is a paper band with a scalloped lace border around it */
.fx .dn .dnr svg { filter:drop-shadow(0 .6vmin 0 __SHADE__) drop-shadow(0 1.6vmin 1.6vmin rgba(40,10,5,.22)); }
.fx .dn .dnr::before { content:""; position:absolute; inset:-5%; border-radius:50%; border:1.2vmin dotted var(--accent); opacity:.55; }
.fx .dn .dntr { stroke:color-mix(in srgb, var(--fg) 14%, var(--bg)); }
.fx .dn .dnlg div i, .fx .dn .dnt i.sw { border-radius:0; transform:rotate(45deg) scale(.86); }
/* maps: the country is a cut-out laid on the page; labels are paper tags; pins are diamonds */
.fx .wpm svg { filter:drop-shadow(0 .45vmin 0 color-mix(in srgb, __SHADE__ 55%, transparent)); }
.fx .wpm-p { fill:color-mix(in srgb, var(--card) 70%, var(--bg)); }
.fx .wpm-lb { border-radius:0; background:var(--card); color:var(--card-fg); box-shadow:0 .35vmin 0 __SHADE__; }
.fx .wpm-pin i { border-radius:.2vmin; transform:rotate(45deg); }
.fx .wpm-r i { border-radius:0; }
.fx .wp-mock { border-radius:0 !important; }
/* icon units: the lit share is stamped on a paper slip */
.fx .iu .iuper { background:var(--card); color:var(--card-fg); padding:.4em .8em; box-shadow:0 .4vmin 0 __SHADE__; }
.fx .iu .iulg i { border-radius:0; transform:rotate(45deg) scale(.8); }
/* opener: no glossy sweep on paper; bars cast paper drops */
.fx .op .op-sweep { display:none; }
.fx .op .op-bar { box-shadow:0 .5vmin 0 __SHADE__; }
/* share card: a paper card with a printed red border line, no screen scanlines */
.fx .sc .sc-c { border-radius:0; box-shadow:0 .7vmin 0 __SHADE__, 0 3vmin 5vmin rgba(40,10,5,.25); outline:.45vmin solid var(--accent); outline-offset:-2.2vmin; }
.fx .sc .sc-c::before { background:__NOISE__; background-size:340px; }
/* next teaser: the cover is a mounted print with a paper border; the RGB glitch and scanline stay off */
.fx .nt .nt-cv { border-radius:0; border:1.1vmin solid #fbf7ee; box-shadow:0 .7vmin 0 __SHADE__, 0 3vmin 5vmin rgba(0,0,0,.3); }
.fx .nt .nt-cv .rgb, .fx .nt .nt-cv .scan { display:none; }
.fx .nt .nt-cv .ph { background:var(--accent); background-image:__NOISE__; }
.fx .nt .nt-cv .ph b { color:rgba(40,10,5,.16); }
.fx .nt .nt-cv .ph i { color:#fbf7ee; -webkit-text-stroke:0; text-shadow:0 .05em 0 rgba(60,10,5,.45), 0 .12em .2em rgba(40,10,5,.3); }
.fx .nt .nt-tape { opacity:.94; }
.fx .nt .nt-k { border-radius:0; box-shadow:0 .4vmin 0 __SHADE__; }
.fx .nt .nt-h span { border-radius:0; border-style:dashed; }
.fx .nt .nt-w { border-radius:0; transform:rotate(-2deg); box-shadow:0 .5vmin 0 __SHADE__; }
.fx .sc .sc-hint { border-radius:0; transform:rotate(2deg); box-shadow:0 .4vmin 0 __SHADE__; }
.fx .sc .sc-flash { border-radius:0; }

/* the card frame (FX_FRAME): scalloped paper border, 角花 corners, paper header tag, caption strip, footer slip */
.ctx.pcx .frm { position:absolute; inset:0; width:100%; height:100%; filter:drop-shadow(0 6px 0 rgba(40,10,5,.22)) drop-shadow(0 10px 12px rgba(40,10,5,.2)); }
.ctx.pcx .cf { position:absolute; filter:drop-shadow(0 4px 0 rgba(40,10,5,.25)); }
.ctx.pcx .hd { left:128px; right:128px; top:40px; height:auto; border:none; display:flex; justify-content:space-between; align-items:center; }
.ctx.pcx .hd .tag { background:var(--pc-tag); color:var(--pc-tag-fg); font-family:var(--f-display); font-weight:400; font-size:24px; padding:7px 16px 9px;
  box-shadow:0 4px 0 rgba(40,10,5,.25); transform:rotate(-1.2deg); white-space:nowrap; }
.ctx.pcx .hd .tag b { color:var(--pc-tag-b); font-weight:400; margin-right:10px; letter-spacing:0; }
.ctx.pcx .hd .tag span { opacity:1; margin-left:0; }
.ctx.pcx .hd .fxid { background:var(--pc-stub); color:var(--pc-stub-fg); font-family:var(--f-mono); font-size:17px; padding:4px 12px; transform:rotate(2deg);
  box-shadow:0 3px 0 rgba(40,10,5,.25); }
.ctx.pcx .cap { bottom:76px; }
.ctx.pcx .cap > span { background:var(--pc-cap); color:var(--pc-cap-fg); border-radius:2px; font-family:var(--f-body); font-weight:800; transform:rotate(-.8deg);
  box-shadow:0 5px 0 var(--pc-frame), 0 14px 20px rgba(40,10,5,.25); }
.ctx.pcx .cap .em .emt { background:var(--pc-em); color:var(--pc-em-fg); padding:0 .16em; box-shadow:0 3px 0 rgba(40,10,5,.25); }
.ctx.pcx .ft { left:128px; right:128px; bottom:38px; opacity:1; color:var(--fg); font-size:15px; }
.ctx.pcx .ft > div { background:color-mix(in srgb, var(--bg) 82%, transparent); box-shadow:0 0 0 5px color-mix(in srgb, var(--bg) 82%, transparent); }
#root.v .ctx.pcx .hd { left:56px; right:56px; top:206px; } #root.v .ctx.pcx .ft { left:56px; right:56px; top:1478px; bottom:auto; font-size:17px; }
#root.v .ctx.pcx .cap { top:1330px; bottom:auto; padding:0 120px; }
"""
STYLE["css"] = (FX_CSS.replace("__NOISE__", noise_bg(0.13, 9)).replace("__WM__", _WM).replace("__LACE__", _LACE)
                .replace("__SHADE__", _SHADE))


def frame_path(W, H, m, r):
    """a full-page band with a scalloped inner edge (evenodd): the paper border a 窗花 card is mounted in."""
    def edge(L):
        n = max(1, round(L / (2 * r)))
        return n, L / (2 * n)
    d = f"M0 0H{W}V{H}H0Z M{m} {m}"
    n, rr = edge(W - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 {2 * rr:.2f} 0" for _ in range(n))
    n, rr = edge(H - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 0 {2 * rr:.2f}" for _ in range(n))
    n, rr = edge(W - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 {-2 * rr:.2f} 0" for _ in range(n))
    n, rr = edge(H - 2 * m); d += "".join(f"a{rr:.2f} {rr:.2f} 0 0 0 0 {-2 * rr:.2f}" for _ in range(n))
    return d + "Z"


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect card in papercut: the effect is mounted in a red (cream / gold) paper border with
    scalloped edges and four 角花 corner flowers; the header is a paper tag, the spoken line a tilted paper strip with
    the keyword cut from red paper, the footnote a small slip."""
    P, W, H = X.portrait, X.W, X.H
    th = p.get("theme") if p.get("theme") in FRAME else "paper"
    fr = FRAME[th]
    m, r, R = (20, 12, 78) if P else (18, 12, 86)
    sty = parts["sty"] + ";" + ";".join(f"--pc-{k}:{v}" for k, v in fr.items())
    corners = "".join(f'<div class="cf" data-k="{k}" style="left:{x - R}px;top:{y - R}px;width:{2 * R}px;height:{2 * R}px">{flower(f"{cid}k{k}", fr["corner"], 8)}</div>'
                      for k, (x, y) in enumerate([(m, m), (W - m, m), (W - m, H - m), (m, H - m)]))
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + f'<svg class="frm" viewBox="0 0 {W} {H}" preserveAspectRatio="none"><path d="{frame_path(W, H, m, r)}" fill="{fr["frame"]}" fill-rule="evenodd"/></svg>{corners}'
             + f'<div class="hd"><div class="tag"><b>{X.rich(X.channel)}</b><span>{parts["topic"]}</span></div><div class="fxid">{parts["fxid"]}</div></div>'
             + f'<div class="cap"><span style="font-size:{parts["cap_px"]}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx pcx{' photo' if parts['photo'] else ''}", 30, track=20, sty=sty)
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .cap > span", {{y:28, rotation:-5, opacity:0, duration:0.42, ease:"back.out(1.8)"}}, {t + 0.08:.3f});')
    X.tw(f'tl.from("{s} .hd .tag", {{y:-90, rotation:-8, duration:0.45, ease:"back.out(1.8)"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .hd .fxid", {{y:-90, rotation:10, duration:0.45, ease:"back.out(1.8)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .cf", {{rotation:0}}, {{rotation:20, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
