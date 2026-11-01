"""弹幕 (bullet comments — B站 / 抖音 的「弹幕刷屏」, the 高能 moment every 二创 and 口播 uses): comments fly
right-to-left in lanes at one constant speed (long ones take longer, like the real thing), never overlapping in a
lane; highlighted ones are larger and coloured; on a cue the screen floods and a 「前方高能」 banner slams in.
Over a still / video background, or a neutral player frame when none is given.

Adapts: 3–300 comments (fewer are recycled to reach `count`); each a word to a sentence; lanes and type size
follow the frame; any background aspect.
p: items [text | {text, hl}] · count · bg (image or video) · t_hl · hl_text · speed (seconds to cross) · mock
"""
from h9.aefx import _clip
from h9 import fit as FT
import importlib.util, pathlib, random, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")


def danmaku(X, cid, t, d, p):
    SO.base_css(X)
    raw = [it if isinstance(it, dict) else {"text": str(it)} for it in FT.as_list(p.get("items"))] or [{"text": "前排"}, {"text": "哈哈哈哈"}]
    W, H, P = X.W, X.H, X.portrait
    fs = SO.px(X, 3.6 if P else 3.2)
    lane_h = fs * 1.6
    y0, y1 = (270, 1240) if P else (120, 880)
    lanes = max(3, int((y1 - y0) // lane_h))
    v = W / float(p.get("speed", 5.0)) * (1.0 if not P else 0.8)
    rnd = random.Random(int(p.get("seed", 11)))
    th = SO.cue(X, p, "t_hl", t, None) if p.get("t_hl") is not None else None
    n = int(p.get("count", max(len(raw), 24)))
    t_end = t + d - 0.3
    starts = sorted(t + (d - 1.0) * (k + rnd.random() * 0.8) / n for k in range(n))
    if th is not None:                                  # the flood: an extra burst right at the cue
        starts += [th + rnd.random() * 0.9 for _ in range(max(8, n // 3))]
        starts.sort()
    free = [t - 10.0] * lanes
    items, tw = [], []
    for k, st in enumerate(starts):
        if st > t_end - 0.4: continue
        it = raw[k % len(raw)]
        hl = bool(it.get("hl"))
        size = fs * (1.25 if hl else 1.0)
        w = FT.width(it.get("text", "")) * size + SO.px(X, 2)
        lane = min(range(lanes), key=lambda L: (max(0.0, free[L] - st), rnd.random()))
        st = max(st, free[lane])
        if st > t_end - 0.4: continue
        dur = (W + w) / v
        free[lane] = st + (w + SO.px(X, 6)) / v          # the next one in this lane may enter once this tail is in
        y = y0 + lane * lane_h
        items.append(f'<div class="wpd-i{" hl" if hl else ""}" data-layout-allow-overlap data-k="{k}" style="top:{y:.0f}px; font-size:{size:.0f}px">{X.rich(it.get("text", ""))}</div>')
        tw.append(f'tl.fromTo("#{cid} .wpd-i[data-k=\'{k}\']", {{x:{W}}}, {{x:{-w:.0f}, duration:{dur:.2f}, ease:"none", immediateRender:true}}, {st:.3f});')
    bg = ""
    if p.get("bg"):
        mh, _ = FT.media(X, cid, "bg", p["bg"], t, d, "wpd-bg", box_ar=W / H, fill="cover")
        bg = mh + '<i class="wpd-sh"></i>'
    X.css("fx-wpd", """
.fx .wpd { position:absolute; inset:0; overflow:hidden; font-family:var(--f-body); }
.fx .wpd .wpd-bg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .wpd-sh { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.35), rgba(0,0,0,.15) 40%, rgba(0,0,0,.45)); }
.fx .wpd-i { position:absolute; left:0; white-space:nowrap; font-weight:800; color:#fff; line-height:1.2;
  text-shadow:0 0 .12em #000, 0 0 .12em #000, 0 .06em .1em rgba(0,0,0,.6); will-change:transform; }
.fx .wpd-i.hl { color:#ffd84a; font-weight:900; }
.fx .wpd-hn { position:absolute; left:50%; top:46%; transform:translate(-50%,-50%); font:900 9vmin var(--f-body); color:#fff; background:var(--accent);
  padding:1vmin 4vmin; border-radius:1.2vmin; letter-spacing:.06em; box-shadow:0 2vmin 6vmin rgba(0,0,0,.4); opacity:0; white-space:nowrap; z-index:3; }
.fx .wpd-pl { position:absolute; left:50%; top:47%; transform:translate(-50%,-50%); border-radius:2vmin; overflow:hidden;
  background:linear-gradient(135deg, color-mix(in srgb, var(--fg) 14%, var(--bg)), color-mix(in srgb, var(--fg) 4%, var(--bg))); box-shadow:0 0 0 .3vmin color-mix(in srgb, var(--fg) 12%, transparent); }
.fx .wpd-pl i { position:absolute; left:3vmin; right:3vmin; bottom:3vmin; height:.8vmin; border-radius:.4vmin; background:color-mix(in srgb, var(--fg) 20%, transparent); }
.fx .wpd-pl b { position:absolute; left:3vmin; bottom:3vmin; height:.8vmin; border-radius:.4vmin; background:var(--accent); width:0; }
""")
    player = "" if bg else (f'<div class="wpd-pl" style="width:{(92 if P else 150)}vmin; height:{(150 if P else 84)}vmin"><i></i><b></b></div>')
    hn = f'<div class="wpd-hn" data-layout-allow-overlap>{X.rich(p.get("hl_text", "前方高能"))}</div>' if th is not None else ""
    mock = f'<i class="wp-mock" style="right:3vmin; top:{(y0 - SO.px(X, 4)):.0f}px">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    X.used_text.update(p.get("hl_text", "前方高能"))
    _clip(X, cid, t, d, f'<div class="wpd">{bg}{player}{"".join(items)}{hn}{mock}</div>', p, transparent=FT.is_video(p.get("bg")))
    for line in tw: X.tw(line)
    if player: X.tw(f'tl.fromTo("#{cid} .wpd-pl b", {{width:"0%"}}, {{width:"100%", duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if th is not None:
        X.tw(f'tl.to("#{cid} .wpd-hn", {{opacity:1, duration:0.01}}, {th:.3f});')
        X.tw(f'tl.fromTo("#{cid} .wpd-hn", {{scale:2.2}}, {{scale:1, duration:0.32, ease:"power4.out"}}, {th:.3f});')
        X.tw(f'tl.to("#{cid} .wpd-hn", {{opacity:0, scale:0.9, duration:0.3}}, {min(th + 1.3, t + d - 0.3):.3f});')
        X.tw(f'tl.fromTo("#{cid} .wpd", {{x:0}}, {{keyframes:[{{x:-12, duration:0.04}}, {{x:9, duration:0.04}}, {{x:-4, duration:0.04}}, {{x:0, duration:0.05}}]}}, {th:.3f});')
        X.sfx(th, "slam")


FX = {"danmaku": danmaku}
