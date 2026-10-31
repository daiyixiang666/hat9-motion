"""studio · 三维影棚 —— 用实时三维渲染做 C4D / UE 式的成片：一整个连续的三维布景，镜头随口播在各段之间飞行。
真正的立体中文字（从字体轮廓挤出、带倒角）、金属 / 缎面 / 漆面材质、环境光反射、接触阴影、景深和辉光；
文字长句用清晰的平面层叠在三维画面上。对标：Apple 产品片、Buck / ManvsMachine 的材质感、UE 实时影棚。
适合：开场、观点、产品 / 工具、需要"高级感"的任何一期。

这个风格不走逐句场景：WORLD() 一次性搭好整条片子的三维世界（runtime/world3d.js）。
"""
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

STYLE = {
    "name": "三维影棚", "en": "3D Studio", "benchmarks": ["Apple 产品片", "ManvsMachine", "Buck", "何同学"],
    "tokens": {
        "bg": "#07080b", "fg": "#f3ede0", "muted": "#8c8a86", "accent": "#e9c47c", "accent2": "#e9c47c", "alert": "#e0392f",
        "line": "#1a1c20", "paper": "#07080b", "ink": "#000", "card": "#111", "card-fg": "#f3ede0",
        "cap-fg": "#f3ede0", "cap-size": "40px", "cap-weight": "600", "cap-shadow": "0 2px 0 rgba(0,0,0,.85), 0 0 18px rgba(0,0,0,.8)", "cap-em": "#e9c47c",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono"},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.03, "heading": "blurin", "text": "blurin", "camera": "none", "cut": "hard", "transition": "dip", "em": "static"},
    "layers": [("grain", {"opacity": 0.07})],
    "motion_blur": False,
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 70, "bottom": 30, "h": 300}, "portrait": {"left": 60, "bottom": 300, "h": 340}},
    "sfx": {"transition": ("whoosh_deep", 0.35), "title": ("boom", 0.4), "line": ("whoosh_soft", 0.25), "enter": ("whoosh_deep", 0.3), "pop": ("pop", 0.4),
            "hit": ("hit", 0.4), "count": ("tick", 0.25), "mascot": ("whoosh_soft", 0.25), "fly": ("whoosh_soft", 0.3)},
    # camera stations, one per beat (title, compare, statement, number, quote, outro)
    "stations": [
        {"cam": [0, 0.35, 9.8], "look": [0, 0.0, 0], "focus": 9.8, "drift": 0.4},
        {"cam": [0, 0.6, -11.4], "look": [0, 0.1, -20], "focus": 8.6, "drift": 0.5},
        {"cam": [0, 0.8, -31.8], "look": [0.2, 0.3, -40], "focus": 8.2, "drift": 0.45},
        {"cam": [0, 5.4, -51.0], "look": [0, -0.2, -61.5], "focus": 11.0, "drift": 0.4},
        {"cam": [-2.6, 0.6, -71.6], "look": [-0.4, 0.2, -80], "focus": 8.6, "drift": 0.5},
        {"cam": [0, 0.6, -92.6], "look": [0, 0.45, -100], "focus": 7.4, "drift": 0.3},
    ],
}

STYLE["css"] = """
#w3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-studio .w-ov { position:absolute; inset:0; pointer-events:none; }
.st-studio .w-q { position:absolute; left:130px; top:50%; transform:translateY(-55%); width:720px; }
.st-studio .w-q .k { font-family:var(--f-mono); font-size:18px; letter-spacing:.32em; color:var(--accent); margin-bottom:26px; }
.st-studio .w-q .q { font-family:var(--f-display); font-weight:800; font-size:76px; line-height:1.22; color:var(--fg); text-shadow:0 4px 40px rgba(0,0,0,.9); }
.st-studio .w-q .q .em .emt { color:var(--accent); }
.st-studio .w-q .em .emb { display:none; }
.st-studio .w-out { position:absolute; left:0; right:0; bottom:140px; text-align:center; }
.st-studio .w-out .s { font-size:34px; color:var(--muted); font-weight:500; letter-spacing:.06em; }
.st-studio .w-out .c { display:inline-block; margin-top:18px; font-family:var(--f-body); font-weight:700; font-size:26px; color:#0b0b0d;
  background:linear-gradient(180deg, #f3d98b, #c99d3d); padding:10px 28px; border-radius:999px; }
.st-studio .w-tag { position:absolute; top:58px; left:0; right:0; text-align:center; font-family:var(--f-mono); font-size:17px; letter-spacing:.36em; color:var(--muted); }
"""


def WORLD(beats, times, X, D):
    from h9 import glyphs, fonts
    st = X.S.get("stations", STYLE["stations"])
    by = {b["scene"]: (b, t, d) for b, (t, d) in zip(beats, times)}
    tb, t1, d1 = by["title"]; cb, t2, d2 = by["compare"]; sb, t3, d3 = by["statement"]
    nb, t4, d4 = by["number"]; qb, t5, d5 = by["quote"]; ob, t6, d6 = by["outro"]
    stack = sb.get("words") or ["工具", "判断"]
    look = X.S.get("look", "gold")
    cfg = {
        "w": X.W, "h": X.H, "bg": X.S.get("bg3d", "#07080b"), "floor": X.S.get("floor3d", "#0c0d11"), "floorY": -1.35, "ccw": False,
        "aperture": X.S.get("aperture", 0.0016), "look": look,
        "stations": st, "beats": [{"t": t, "d": d} for t, d in times],
        "images": {"a": X.asset(cb["left"]["img"]), "b": X.asset(cb["right"]["img"]), "quote": X.asset(qb["image"]),
                   "desk": X.asset(tb["image"]), **{f"w{i}": X.asset(p) for i, p in enumerate(tb.get("wall", []))}},
        "s1": {"t": t1, "title": tb["title"].replace("*", ""), "sub": tb.get("sub", "")},
        "s2": {"t": t2, "la": cb["left"]["label"], "lb": cb["right"]["label"], "stickers": cb["right"].get("stickers", []),
               "ta": X.T(cb.get("at_left"), t2) or t2 + 1, "tb": X.T(cb.get("at_right"), t2) or t2 + 2,
               "ts": X.T(cb.get("at_stickers"), t2) or t2 + 2.5, "tv": X.T(cb.get("at_verdict"), t2)},
        "s3": {"t": t3, "a": stack[0], "b": stack[1], "ta": X.T((sb.get("at") or [None])[0], t3) or t3 + 0.1,
               "tb": X.T((sb.get("at") or [None, None])[1], t3) or t3 + 0.9},
        "s4": {"t": t4, "v": int(nb["value"]), "hl": int(nb.get("hl", 10)), "ta": X.T(nb.get("at"), t4) or t4 + 0.2, "th": X.T(nb.get("at_hl"), t4) or t4 + 1.4},
        "s5": {"t": t5}, "s6": {"t": t6, "d": d6, "title": ob.get("title", "第九顶帽子")},
    }
    text = "".join([cfg["s1"]["title"], cfg["s1"]["sub"], cfg["s2"]["la"], cfg["s2"]["lb"], "".join(cfg["s2"]["stickers"]),
                    stack[0], stack[1], "0123456789%", cfg["s6"]["title"]])
    font = fonts.find(fonts.REG[X.S.get("font3d", "noto-sans-sc")]["file"])
    gl = glyphs.outlines(font, text, {"wght": 900})
    js = (SKILL / "runtime" / "world3d.js").read_text()
    X.css("w3d-import", "")
    X.extra_head = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
                    '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>')
    X.extra_body = ('<script>window.__hf=window.__hf||{};window.__hf.buildReady=window.__hf.buildReady||{};'
                    'window.__hf.buildReady.world=new Promise(r=>{window.__h9WorldReady=r;});'
                    f'window.__H9_WORLD={json.dumps(cfg, ensure_ascii=False)};window.__H9_GLYPHS={json.dumps(gl, separators=(",", ":"))};</script>'
                    f'<script type="module">{js}</script>')
    X.clip("world", 0, D, '<canvas id="w3d" width="%d" height="%d"></canvas>' % (X.W, X.H), "w3d-host", 1, track=2, attrs="data-motion-blur=\"off\"")
    # whoosh on every camera flight, impacts on the payoffs
    for i, (t, d) in enumerate(times):
        if i: X.sfx(t - 0.5, "fly")
    X.sfx(t1 + 0.1, "title"); X.sfx(cfg["s2"]["ts"], "pop"); X.sfx(cfg["s3"]["tb"], "hit"); X.sfx(cfg["s4"]["ta"], "count"); X.sfx(cfg["s4"]["th"], "pop"); X.sfx(t6 + 0.4, "hit")
    if cfg["s2"]["tv"]: X.sfx(cfg["s2"]["tv"], "hit")
    # crisp DOM layers where long text must read: the quote line and the outro sub/CTA
    X.clip("wq", t5, d5, f'<div class="w-q"><div class="k">{X.rich(qb.get("kicker", "THE JUDGMENT"))}</div><div class="q">{X.rich(qb["text"], split="chars")}</div></div>', "w-ov", 5, track=3)
    n = len(str(qb["text"]).replace("*", "").replace("|", ""))
    X.enter("#wq .k", t5 + 0.2, "text", verb="fade")
    X.enter("#wq .q .c", t5 + 0.3, "heading", verb="blurin", stagger=min(0.045, 1.4 / n), dur=0.45)
    X.clip("wo", t6, d6, f'<div class="w-out"><div class="s">{X.rich(ob.get("sub", ""))}</div><div class="c">{X.rich(ob.get("cta", "关注"))}</div></div>', "w-ov", 5, track=4)
    X.enter("#wo .s", t6 + 0.9, "text", verb="blurin")
    X.enter("#wo .c", t6 + 1.2, "accent", verb="pop", dur=0.45)
    X.clip("wtag", 0, D, f'<div class="w-tag">{X.rich("第九顶帽子 · THE NINTH HAT")}</div>', "w-ov", 6, track=5)
