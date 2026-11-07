"""作品扇面 Card fan ("look at what's new"): a stack of real cards — thumbnails, covers, screenshots — rises into the
frame and fans out into an arc behind the title with a slight 3D lean, each card floating on its own; then a play badge
pops on the centre card with a ripple. Title and a kicker chip sit above the fan.

Adapts: 2–15 cards (fewer than 5 are recycled), any card aspect (default from the pictures), the arc opens as wide as
the frame allows, titles from a word to a line (fitted); corners, shadow, tilt, chip and badge follow the style.
p: items | images | folder · title · kicker · card_ar · max (cards) · play (true) · subject · subject_label · mock
"""
import importlib.util
import math
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
MD = M.MD

CSS = """
.fx .cf .cf-stage { position:absolute; inset:0; perspective:1600px; }
.fx .cf .cf-c { position:absolute; border-radius:var(--mt-r); overflow:hidden; background:var(--card); box-shadow:var(--mt-shadow), 0 0 0 3px var(--card); }
.fx .cf .cf-c img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .cf .cf-ttl { position:absolute; text-align:center; }
.fx .cf .cf-kick { position:absolute; transform:translateX(-50%); }
.fx .cf .cf-play { position:absolute; display:grid; place-items:center; border-radius:var(--mt-dot); background:color-mix(in srgb, var(--fg) 72%, transparent);
  box-shadow:0 0 0 calc(var(--mt-sw) * .8) var(--card); }
.fx .cf .cf-play svg { width:42%; height:42%; fill:var(--card); margin-left:8%; }
.fx .cf .cf-rip { position:absolute; border-radius:var(--mt-dot); border:var(--mt-sw) solid var(--accent); opacity:0; }
"""


def card_fan(X, cid, t, d, p):
    M.base(X)
    X.css("fx-cf", CSS)
    sk = M.skin(X)
    P = X.portrait
    rnd = random.Random(int(p.get("seed", 9)) * 7919 + 21)
    its = M.pool(X, p, cap=int(p.get("max", 11)))
    if not its:
        raise SystemExit(f"card_fan at {t:.2f}s: give `items`, `images` or `folder`")
    src = list(its)
    k = 0
    while len(its) < 5:
        its.append(src[k % len(src)])
        k += 1
    its = its[:int(p.get("max", 11))]
    n = len(its)
    has_sub = bool(p.get("subject"))
    R = M.regions(X, p, has_sub, sub_ar=0.8, graphic_share=0.66, hero_ar=0.95, row="center")
    gx0, gy0, gx1, gy1 = R["g"]
    gw = gx1 - gx0
    gh = gy1 - gy0
    # title block
    title = p.get("title", "")
    kick = p.get("kicker", "")
    t_px = 0
    t_lines = ""
    t_n = 0
    if title:
        t_px, t_lines, t_n = M.fit_text(X, title, gw * 0.96, gh * 0.22, 84 if not P else 76, 32, 2)
    head_h = t_px * 1.15 * t_n
    k_px = 28 if not P else 32
    if kick:
        head_h += k_px * 1.9 + 14
    fan_y0 = gy0 + head_h + 56
    fan_h = gy1 - fan_y0
    # cards
    ars = []
    for it in its:
        ars.append(it["ar"])
    ars.sort()
    car = float(p.get("card_ar", ars[len(ars) // 2]))
    car = max(0.45, min(1.8, car))
    if P:
        car = min(car, 0.68)          # 9:16: landscape pictures are cropped to portrait cards so the fan fills the width
    ch = fan_h * 0.84
    cw = ch * car
    cw_max = gw * (0.38 if car < 1 else 0.5)
    if cw > cw_max:
        cw = cw_max
        ch = cw / car
    rp = ch * 1.9                                   # pivot distance below the card centre
    max_a = math.degrees(math.asin(max(0.05, min(0.95, (gw * 0.98 - cw) / (2 * rp)))))
    step = min(11.0, 2 * max_a / max(1, n - 1))
    cx = (gx0 + gx1) / 2
    ccy = fan_y0 + ch * 0.5 + max(fan_h * 0.04, (fan_h - ch * 1.25) * 0.4)
    left = cx - cw / 2
    top = ccy - ch / 2
    cards = []
    angles = []
    mid = (n - 1) / 2
    for i, it in enumerate(its):
        a = (i - mid) * step
        angles.append(a)
        url = MD.still(X, it)
        z = 100 - int(abs(i - mid) * 2)
        cards.append(f'<div class="cf-c" data-i="{i}" style="left:{left:.1f}px; top:{top:.1f}px; width:{cw:.1f}px; height:{ch:.1f}px; z-index:{z}; '
                     f'transform-origin:50% {ch / 2 + rp:.1f}px"><img src="{url}" alt=""></div>')
    ci = int(round(mid))
    play_d = min(cw, ch) * 0.34
    play = ""
    if p.get("play", True):
        pcx = cx
        pcy = ccy - 0.0
        play = (f'<i class="cf-rip" style="left:{pcx - play_d / 2:.0f}px; top:{pcy - play_d / 2:.0f}px; width:{play_d:.0f}px; height:{play_d:.0f}px; z-index:120"></i>'
                f'<div class="cf-play" style="left:{pcx - play_d / 2:.0f}px; top:{pcy - play_d / 2:.0f}px; width:{play_d:.0f}px; height:{play_d:.0f}px; z-index:121">'
                f'<svg viewBox="0 0 24 24"><path d="M6 3.5v17l14-8.5z"/></svg></div>')
    head = ""
    if title:
        head += f'<div class="cf-ttl mt-t" style="left:{gx0:.0f}px; top:{gy0:.0f}px; width:{gw:.0f}px; font-size:{t_px:.0f}px">{t_lines}</div>'
    if kick:
        X.used_text.update(kick)
        head += f'<div class="mt-pill acc cf-kick" style="left:{cx:.0f}px; top:{gy0 + t_px * 1.15 * t_n + 14:.0f}px; font-size:{k_px}px">{X.rich(kick)}</div>'
    stage = f'<div class="cf-stage">{"".join(cards)}{play}</div>'
    subj = M.subject(X, cid, t, d, p, R["s"], sk, at=t + 1.2)
    mock = M.mock_tag(X, p, gx1 - 80, gy0)
    _clip(X, cid, t, d, M.wrap(X, sk, stage + head + subj + mock, "cf"), p)
    s = f"#{cid}"
    e = M.ease_in(sk)
    tilt = sk.get("tilt", 0)
    # 1 · the stack rises
    for i in range(n):
        jit = rnd.uniform(-3, 3)
        X.tw(f'tl.set("{s} .cf-c[data-i=\'{i}\']", {{rotation:{jit:.2f}, y:{fan_h * 0.12:.0f}}}, {t:.3f});')
    X.tw(f'tl.from("{s} .cf-c", {{y:"+={X.H * 0.5:.0f}", opacity:0, duration:0.6, ease:"expo.out", stagger:0.03}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    if title:
        X.tw(f'tl.from("{s} .cf-ttl .fl", {{yPercent:80, opacity:0, duration:0.55, ease:"{e}", stagger:0.08}}, {t + 0.15:.3f});')
    if kick:
        X.tw(f'tl.from("{s} .cf-kick", {{scale:0.5, opacity:0, duration:0.4, ease:"back.out(2.4)"}}, {t + 0.45:.3f});')
    # 2 · the fan opens from the centre outwards, with a slight 3D lean
    t_f = t + 0.6
    for i in range(n):
        a = angles[i]
        order = abs(i - mid)
        ry = -a * 0.9
        extra = rnd.uniform(-tilt, tilt) if tilt else 0
        X.tw(f'tl.to("{s} .cf-c[data-i=\'{i}\']", {{rotation:{a + extra:.2f}, rotationY:{ry:.1f}, y:0, duration:0.75, ease:"back.out(1.3)"}}, {t_f + order * 0.045:.3f});')
    X.sfx(t_f, "whoosh")
    # 3 · the play badge on the centre card
    t_p = t_f + 0.75 + mid * 0.045 + 0.25
    if play:
        X.tw(f'tl.to("{s} .cf-c[data-i=\'{ci}\']", {{y:-{ch * 0.05:.0f}, scale:1.05, duration:0.4, ease:"{e}"}}, {t_p - 0.1:.3f});')
        X.tw(f'tl.from("{s} .cf-play", {{scale:0, opacity:0, duration:0.4, ease:"back.out(2.6)"}}, {t_p:.3f});')
        X.tw(f'tl.fromTo("{s} .cf-rip", {{scale:1, opacity:0.9}}, {{scale:2.2, opacity:0, duration:0.8, ease:"power2.out", immediateRender:false}}, {t_p + 0.2:.3f});')
        X.sfx(t_p, "pop")
    # hold: every card floats on its own
    t_h = t_p + 0.4
    if t + d - t_h > 0.6:
        for i in range(n):
            if i == ci and play:
                continue
            per = rnd.uniform(0.9, 1.5)
            reps = max(1, int((t + d - t_h) / per))
            amp = rnd.uniform(5, 11)
            X.tw(f'tl.to("{s} .cf-c[data-i=\'{i}\']", {{y:-{amp:.1f}, duration:{per:.2f}, ease:"sine.inOut", yoyo:true, repeat:{reps}}}, {t_h + rnd.uniform(0, 0.4):.3f});')
        X.tw(f'tl.to("{s} .cf-stage", {{y:-{gh * 0.02:.0f}, duration:{t + d - t_h:.2f}, ease:"none"}}, {t_h:.3f});')


FX = {"card_fan": card_fan}
