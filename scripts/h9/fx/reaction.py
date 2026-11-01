"""反应镜头 Reaction Beat (S11 好笑「？？？」 · S12 沉重 · 抖音 / B 站 的梗后定格、综艺花字):
a beat with no words that tells the viewer how to feel.
  funny — the frame freezes with a jolt and zoom, three "?" pop in on twos with a wobble, a sweat drop slides, a
          speed-line burst flickers; a boing.
  heavy — colour drains to grey, the camera creeps in slowly, black bars close a little, a short line fades up in
          Song, a low boom.
Adapts: 1–8 s (funny re-pops the marks on longer holds; heavy just goes further); background = theme, a still
("image", any aspect) or footage ("video"); text optional, a word to a sentence (fitted).
p: mood funny | heavy · text · image | video · focus
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def reaction(X, cid, t, d, p):
    from h9 import fit as FIT
    Wv, Hv = F.frame_vmin(X)
    mood = p.get("mood", "funny")
    ts, tl_ = F.fit(p.get("text", ""), Wv * 0.8, Hv * 0.2, 7 if mood == "funny" else 5.5, 2.6, 2) if p.get("text") else (0, [])
    X.css("fx-p5re", """
.fx .p5re { position:absolute; inset:0; overflow:hidden; }
.fx .p5re .bgm { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .p5re .pg { position:absolute; inset:0; background:radial-gradient(60% 50% at 50% 45%, color-mix(in srgb, var(--accent) 22%, var(--bg)), var(--bg)); }
.fx .p5re .tx { position:absolute; left:0; right:0; bottom:22%; text-align:center; font-family:var(--f-display); font-weight:900; line-height:1.15; color:var(--fg); }
.fx .p5re .tx .fl { display:block; white-space:nowrap; }
.fx .p5re.funny .tx { color:#111; } .fx .p5re.funny .tx .fl { display:inline-block; background:#f6ce3a; padding:.1em .4em; margin:.06em 0; transform:rotate(-2deg); box-shadow:.5vmin .5vmin 0 #111; }
.fx .p5re .qm { position:absolute; font:900 14vmin var(--f-display); color:#f6ce3a; -webkit-text-stroke:.5vmin #111; paint-order:stroke fill; }
.fx .p5re .sw { position:absolute; width:4vmin; height:6vmin; border-radius:50% 50% 50% 50% / 60% 60% 40% 40%; background:linear-gradient(160deg, #bfe6ff, #5bb2f0); border:.4vmin solid #111; }
.fx .p5re .sl { position:absolute; inset:-20%; background:repeating-conic-gradient(from 0deg, rgba(0,0,0,.0) 0 4deg, rgba(0,0,0,.14) 4deg 5deg); opacity:0; }
.fx .p5re .bar { position:absolute; left:0; right:0; height:0; background:#000; } .fx .p5re .bar.t { top:0; } .fx .p5re .bar.b { bottom:0; }
.fx .p5re.heavy .tx { font-family:var(--f-serif, var(--f-quote, var(--f-display))); font-weight:700; color:#eee; }
#root.v .fx .p5re .tx { bottom:30%; }
""")
    vsel = None; bg = '<div class="pg"></div>'
    if p.get("image") or p.get("video"):
        mk, vsel = FIT.media(X, cid, "bg", p.get("image") or p.get("video"), t, d, "bgm", focus=p.get("focus"), z=2)
        bg = mk or ""
    marks = ""
    if mood == "funny":
        spots = [(64, 20, -12), (76, 33, 10), (58, 40, -4)] if not X.portrait else [(60, 24, -12), (74, 31, 10), (56, 38, -4)]
        marks = '<div class="sl"></div>' + "".join(f'<b class="qm q{k}" style="left:{x}%; top:{y}%; transform:rotate({r}deg)">?</b>' for k, (x, y, r) in enumerate(spots))
        marks += '<i class="sw" style="left:38%; top:24%"></i>'
    else:
        marks = '<i class="bar t"></i><i class="bar b"></i>'
    inner = f'<div class="p5re {mood}">{bg}{marks}' + (f'<div class="tx" style="font-size:{ts:.2f}vmin">{P.lines_html(X, tl_)}</div>' if tl_ else "") + "</div>"
    _clip(X, cid, t, d, inner, p, transparent=bool(vsel))
    s = f"#{cid}"
    tgt = vsel or f"{s} .p5re .bgm, {s} .p5re .pg"
    if mood == "funny":
        X.tw(f'tl.fromTo("{tgt}", {{scale:1}}, {{keyframes:[{{scale:1.18, duration:0.08, ease:"power4.out"}}, {{scale:1.14, duration:{max(0.2, d - 0.08):.2f}, ease:"none"}}]}}, {t:.3f});')
        X.tw(f'tl.fromTo("{s} .p5re .sl", {{opacity:0.9}}, {{opacity:0, duration:0.35, ease:"steps(4)", immediateRender:false}}, {t:.3f});')
        reps = max(1, int(d // 2.5))
        for r in range(reps):
            t0 = t + 0.12 + r * 2.5
            X.tw(f'tl.fromTo("{s} .p5re .qm", {{scale:0, opacity:1}}, {{scale:1, duration:0.24, ease:"back.out(3)", stagger:{{each:0.14}}, immediateRender:{"true" if r == 0 else "false"}}}, {t0:.3f});')
            X.sfx(t0, "boing", 0.4)
        X.tw(f'tl.to("{s} .p5re .qm", {{rotation:"+=8", duration:0.25, ease:"sine.inOut", yoyo:true, repeat:{max(1, int(d / 0.25)) - 1}}}, {t + 0.6:.3f});')
        X.tw(f'tl.fromTo("{s} .p5re .sw", {{y:0, opacity:0}}, {{keyframes:[{{opacity:1, duration:0.1}}, {{y:"{4 + 2 * d:.1f}vmin", duration:{max(0.4, d - 0.4):.2f}, ease:"power1.in"}}]}}, {t + 0.3:.3f});')
        if tl_: X.tw(f'tl.from("{s} .p5re .tx .fl", {{scale:0, rotation:-12, duration:0.3, ease:"back.out(2.5)", stagger:0.08}}, {t + 0.45:.3f});')
    else:
        X.tw(f'tl.fromTo("{tgt}", {{filter:"saturate(1) brightness(1)"}}, {{filter:"saturate(0) brightness(.62)", duration:{min(1.6, d * 0.5):.2f}, ease:"power2.out"}}, {t:.3f});')
        P.push(X, tgt.split(",")[0], t, d, base=0.014, cap=0.1)
        X.tw(f'tl.to("{s} .p5re .bar", {{height:"{9 if not X.portrait else 6}%", duration:{min(1.2, d * 0.4):.2f}, ease:"power2.inOut"}}, {t + 0.1:.3f});')
        if tl_: X.tw(f'tl.from("{s} .p5re .tx .fl", {{opacity:0, y:10, filter:"blur(6px)", duration:{min(1.4, d * 0.45):.2f}, ease:"sine.out", stagger:0.25}}, {t + min(0.8, d * 0.3):.3f});')
        X.sfx(t, "boom", 0.25)


FX = {"reaction": reaction}
