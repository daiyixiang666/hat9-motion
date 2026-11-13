"""iso3d · 等距微缩 —— 一整条片子是一个连续的等距 3D 微缩世界（正交镜头）：每句话一座漂浮的玩具小岛，
马卡龙配色、圆角积木造型、低角度太阳拉出的柔和长影子、接触阴影（AO 感）、轻微辉光；镜头在岛与岛之间飞行、环绕、推拉。
数据也做成实物：包裹堆成山、柱子一块块长高、硬币一枚枚掉落、一个包裹真的走完全程（镜头跟着它）。
真正的立体中文字（字体轮廓挤出），长句和数字用清晰的平面卡片叠在画面上。
对标：Monument Valley 的等距构图、Blender 微缩模型 / tilt-shift 城市、Apple 地图 3D 城市、Kurzgesagt 的城市段落。
适合：物流、城市、零售、供应链、平台经济这类"有东西在流动"的选题。

这个风格不走逐句场景：WORLD() 一次性搭好整个世界（runtime/iso3d.js）。每个 beat 的 "scene" 选一座岛：
  pile 包裹山 + 价签 · city 城市街区 + 环形传送带 + 一个人的年包裹量 · bars 立体柱状图 · route 一个包裹走完的几站
  （紧跟一个 "cont" beat = 镜头跟拍那一段）· coins 硬币减少 / 包裹塔长高 · scale 拉远看全景 + 立体大字 · outro 落版
每个 beat 可带 "card"（左侧 / 顶部的数字卡片）。横竖屏各自取景：镜头把岛放进卡片留出的那块画面里。
"""
import json
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

PAL = {
    # pastel but with contrast: buildings and props are muted; the one saturated colour (coral) marks the object the sentence is about
    "sky0": "#fde9dc", "sky1": "#efe0f7", "sky2": "#d9e4fb",
    "slab": "#fbf3e7", "slab2": "#ecf4ee", "slab3": "#f8ebf1", "slabSide": "#b9a9d6",
    "b0": "#ecc9bd", "b1": "#bfcbea", "b2": "#bfded2", "b3": "#efdcb2", "b4": "#cfc3ea", "b5": "#ecc9d6",
    "roof": "#f6f0ea", "window": "#4f5c94", "glass": "#7fa2e0", "door": "#5b5690", "path": "#e3d8ca",
    "kraft": ["#dcae7a", "#d4a06a", "#e4bb8c", "#cb955e"],
    "coral": "#f0284f", "mint": "#7cc9b2", "sky": "#93acec", "lilac": "#b7a8e6",
    "ink": "#26305e", "muted": "#8e86ac", "card": "#ffffff",
    "road": "#7b7699", "lane": "#fffaf0", "belt": "#504a6e", "floor": "#efe7df", "cargo": "#ffffff",
    "trunk": "#9c7a63", "leaf0": "#9ccfb1", "leaf1": "#b6dcc0", "tyre": "#26305e", "skin": "#ffd9c2", "cloud": "#ffffff",
    "gold": "#ffcf5a", "gold2": "#f2b63b", "shadow": "#3b2f63",
    "hemiSky": "#fff6ee", "hemiGround": "#b8acdc", "sun": "#fff1de",
}

STYLE = {
    "name": "等距微缩", "en": "Iso Miniature", "benchmarks": ["Monument Valley", "Blender 微缩模型 / tilt-shift", "Apple 地图 3D 城市", "Kurzgesagt 城市段落"],
    "tokens": {
        "bg": "#efe0f7", "fg": "#26305e", "muted": "#8e86ac", "accent": "#f0284f", "accent2": "#7cc9b2", "alert": "#f0284f",
        "line": "#e6dcf0", "paper": "#ffffff", "accent-tx": "#d81f48", "muted-tx": "#5d5784", "ink": "#26305e", "navy": "#26305e", "card": "#ffffff", "card-fg": "#26305e", "side": "#cfc3ea", "butter": "#ffd76a",
        "cap-bg": "#ffffff", "cap-fg": "#26305e", "cap-size": "38px", "cap-weight": "900", "cap-pad": "12px 30px 14px", "cap-radius": "22px",
        "cap-shadow": "none", "cap-em": "#d81f48", "cap-bottom": "70px", "mascot-bg": "#ffe199",
    },
    "fonts": {"display": ["harmonyos-sans-black", "noto-sans-sc"], "body": ["harmonyos-sans", "noto-sans-sc"], "num": ["archivo", "harmonyos-sans-black"]},
    "motion": {"ease": "back.out(1.6)", "dur": 0.55, "stagger": 0.04, "heading": "pop", "text": "rise", "camera": "none", "cut": "hard", "em": "static"},
    "layers": [("grain", {"opacity": 0.035})],
    "motion_blur": False,
    "caption_mode": "reading",          # 9:16 too: a punch page mid-frame would sit on the islands
    "safe_exempt": ["#hd .hd"],     # 9:16 page furniture (header / HUD / legend / scale bar) may sit under the platform chrome
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 90, "bottom": 110, "h": 300}, "portrait": {"right": 60, "bottom": 430, "h": 300}},
    "sfx": {"fly": ("whoosh_soft", 0.3), "pop": ("pop", 0.32), "count": ("tick", 0.22), "land": ("boing", 0.3), "ding": ("bell", 0.3),
            "click": ("click", 0.16), "riser": ("riser", 0.22), "slam": ("slam", 0.32), "hit": ("hit", 0.3), "mascot": ("whoosh_soft", 0.25),
            "enter": ("whoosh_soft", 0.25), "transition": ("whoosh_soft", 0.3)},
    "font3d": "harmonyos-sans-black",
}

STYLE["css"] = """
#iso3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-iso3d .iso-ov { position:absolute; inset:0; pointer-events:none; }
/* caption = a road sign planted in the world: white board, coloured border, navy type, a grey pole running down off the frame */
.st-iso3d .clip.cap { bottom:var(--cap-bottom); }
.st-iso3d .cap .cp { position:relative; background:#ffffff; color:var(--navy); border:6px solid var(--accent); border-radius:22px; font-size:38px; font-weight:900;
  padding:12px 30px 14px; box-shadow:0 10px 0 rgba(59,47,99,.35); }
.st-iso3d .cap .cp::before { content:""; position:absolute; left:50%; top:100%; width:14px; margin:6px 0 0 -7px; height:900px; z-index:-1;
  background:linear-gradient(90deg, #9d97b8 0 50%, #7a7398 50% 100%); border-radius:4px; }
.st-iso3d .cap .em .emt { color:var(--accent-tx); } .st-iso3d .em .emb { display:none; }
.st-iso3d.v .clip.cap { bottom:var(--iso-cap-b, 424px); }
/* no host sticker in this world */
.st-iso3d .mascot { display:none !important; }
/* stage names = signposts planted at each station (the runtime moves them with the camera) */
.st-iso3d .pin { position:absolute; left:0; top:0; display:flex; flex-direction:column; align-items:center; opacity:0; transform-origin:50% 100%; }
.st-iso3d .pin .bd { display:flex; align-items:center; gap:10px; background:#fff; color:var(--navy); border:5px solid var(--side); border-radius:14px;
  padding:6px 18px 8px 8px; font-family:var(--f-display); font-weight:900; white-space:nowrap; box-shadow:0 6px 0 rgba(59,47,99,.3); }
.st-iso3d .pin .bd b { display:inline-flex; align-items:center; justify-content:center; width:1.5em; height:1.5em; border-radius:50%; background:var(--side); color:var(--navy);
  font-family:var(--f-num); font-weight:800; font-size:.85em; }
.st-iso3d .pin .pl { width:10px; height:96px; background:linear-gradient(90deg, #9d97b8 0 50%, #7a7398 50% 100%); border-radius:0 0 3px 3px; }
.st-iso3d .pin.on .bd { border-color:var(--accent); } .st-iso3d .pin.on .bd b { background:var(--accent-tx); color:#fff; }
/* the sky band: one small title sign + the data note */
.st-iso3d .hd { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-display); font-weight:900; color:var(--navy);
  background:#fff; border:4px solid var(--navy); border-radius:14px; padding:6px 18px 7px 8px; box-shadow:0 6px 0 rgba(59,47,99,.3); }
.st-iso3d.h .hd { left:96px; top:38px; font-size:26px; } .st-iso3d.v .hd { left:60px; top:110px; font-size:32px; }
.st-iso3d .hd .logo { width:32px; height:32px; border-radius:9px; background:var(--accent); }
.st-iso3d .hd .dots { display:flex; gap:7px; margin-left:6px; } .st-iso3d .hd .dots i { display:block; width:10px; height:10px; border-radius:5px; background:#d6cde6; }
.st-iso3d .src { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--navy); line-height:1.35; opacity:.82; }
.st-iso3d.h .src { right:80px; top:40px; text-align:right; } .st-iso3d.v .src { left:62px; top:180px; right:60px; }
.st-iso3d .note { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--navy); background:rgba(255,255,255,.9); border-radius:10px; padding:4px 12px 6px; opacity:.9; }
.st-iso3d.h .note { right:80px; top:120px; } .st-iso3d.v .note { left:60px; top:300px; }
.st-iso3d .hd .tt { color:var(--muted-tx); font-weight:700; }
"""


def _f(x):
    return None if x is None else round(float(x), 3)


def WORLD(beats, times, X, D):
    from h9 import glyphs, fonts, fit as F
    P = X.portrait
    S = X.S
    pal = dict(PAL, **(S.get("pal") or {}))
    T = lambda v, t0: _f(X.T(v, t0)) if v is not None else None

    # ---- the module list the runtime builds (one island per beat; "cont" continues the previous one)
    mods = []
    for i, (b, (t, d)) in enumerate(zip(beats, times)):
        k = b["scene"]
        m = {"kind": k, "t": _f(t), "d": _f(d)}
        if k == "pile":
            m.update(tag=b.get("tag", "¥8"), at_num=T(b.get("at_num") or (b.get("card") or {}).get("num", {}).get("at"), t), at_tag=T(b.get("at_tag"), t), base=b.get("base"))
        elif k == "city":
            m.update(count=b.get("count", 124), at_cap=T(b.get("at_cap"), t))
        elif k == "bars":
            m.update(values=b["values"], labels=b.get("labels"), years=b.get("years"), gap_after=b.get("gap_after"), hl=b.get("hl"), at_bars=T(b.get("at_bars"), t))
        elif k == "route":
            m.update(names=b.get("names"), kinds=b.get("kinds"), at_pins=T(b.get("at_pins"), t))
        elif k == "cont":
            r = next((x for x in reversed(mods) if x["kind"] == "route"), None)
            if r is None: raise SystemExit("iso3d: a 'cont' beat must follow a 'route' beat")
            r["d2"] = _f(d)
            r["at"] = [T(c, t - 0.3) for c in b.get("at", [])]
            n = len(r.get("names") or [1] * 5)
            if len(r["at"]) != n: r["at"] = [round(t + 0.15 + j * (d - 0.6) / max(1, n - 1), 3) for j in range(n)]
            r["t2"] = _f(t)
        elif k == "coins":
            m.update(a=b.get("a", 14.6), b=b.get("b", 8), ya=b.get("ya", ""), yb=b.get("yb", ""), at_drop=T(b.get("at_drop"), t))
        elif k == "scale":
            m.update(word=b.get("word", "规模"), at_word=T(b.get("at_word"), t))
        elif k == "outro":
            m.update(title=b.get("title", X.channel))
        else:
            raise SystemExit(f"iso3d: unknown scene {k!r} (pile · city · bars · route · cont · coins · scale · outro)")
        mods.append(m)

    # ---- the numbers live in the world: a card's figure becomes a billboard on posts (digits dropped in on their word),
    # its rows become 3D lettering standing on the island (or painted on the road / a truck's side), chips become a small data note
    def plain(x):
        return str(x or "")
    notes = {}
    for i, (b, m) in enumerate(zip(beats, mods)):
        c = b.get("card")
        if not c or m["kind"] == "cont":
            continue
        t0 = m["t"]
        num = c.get("num")
        if num:
            dec = int(num.get("dec", 0))
            v = float(num["v"])
            sg = {"k": plain(c.get("kicker")), "v": f"{v:.{dec}f}", "u": plain(num.get("unit")), "pre": plain(num.get("pre")),
                  "at": T(num.get("at"), t0) or round(t0 + 0.6, 3)}
            fr = num.get("from")
            if fr is not None and float(fr) != 0 and float(fr) != v:
                sg["from"] = f"{float(fr):.{dec}f}"
            m["sign"] = sg
        elif c.get("title") and m["kind"] != "scale":
            m["sign"] = {"k": plain(c.get("kicker")), "v": plain(c["title"]).replace("*", ""), "u": "", "pre": "", "at": T(c.get("at_title"), t0) or round(t0 + 0.4, 3)}
        fl = []
        chips = []
        for r in c.get("rows", []):
            if isinstance(r, dict) and "chip" in r:
                chips.append(plain(r["chip"]))
                continue
            txt = r if isinstance(r, str) else plain(r.get("text"))
            at_r = T(r.get("at"), t0) if isinstance(r, dict) else None
            fl.append({"text": txt, "at": at_r, "mode": (r.get("mode") if isinstance(r, dict) else None) or b.get("rows_as")})
        if fl:
            m["floats"] = fl
        if chips:
            notes[i] = " · ".join(chips)

    # ---- 3D glyph outlines for every string the world extrudes
    text = "0123456789.,%¥×+-−"
    for m in mods:
        for key in ("tag", "word", "title", "ya", "yb"): text += str(m.get(key) or "")
        text += "".join(str(x) for x in (m.get("labels") or m.get("values") or [])) + "".join(str(x) for x in (m.get("years") or []))
        sg = m.get("sign") or {}
        text += "".join(str(sg.get(k, "")) for k in ("k", "v", "u", "pre", "from"))
        text += "".join(f["text"] for f in m.get("floats") or [])
    fid = S.get("font3d", "harmonyos-sans-black")
    path = fonts.find(fonts.REG[fid]["file"])
    if not path: raise SystemExit(f"iso3d: 3D font {fid} not found ({fonts.REG[fid]['file']})")
    gl = glyphs.outlines(path, text, {"wght": 900})
    miss = "".join(sorted({c for c in text if not c.isspace() and c != "*" and c not in gl}))
    if miss:                                       # characters the display face lacks come from MiSans Heavy
        alt = fonts.find(fonts.REG["misans"]["file"])
        if alt: gl.update(glyphs.outlines(alt, miss, {"wght": 900}))

    cfg = {"w": X.W, "h": X.H, "dur": round(D, 3), "pal": pal, "mods": mods, "seed": int(X.v.get("meta", {}).get("seed", 11)),
           "exposure": S.get("exposure", 1.25), "bloom": S.get("bloom", 0.12)}
    js = (SKILL / "runtime" / "iso3d.js").read_text()
    X.extra_head = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
                    '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>')
    X.extra_body = ('<script>window.__hf=window.__hf||{};window.__hf.buildReady=window.__hf.buildReady||{};'
                    'window.__hf.buildReady.world=new Promise(r=>{window.__h9IsoReady=r;});'
                    f'window.__H9_ISO={json.dumps(cfg, ensure_ascii=False)};window.__H9_GLYPHS={json.dumps(gl, separators=(",", ":"))};</script>'
                    f'<script type="module">{js}</script>')
    X.clip("world", 0, D, '<canvas id="iso3d" width="%d" height="%d"></canvas>' % (X.W, X.H), "iso-host", 1, track=2, attrs='data-motion-blur="off"')

    # ---- header: brand + chapter dots, sources on the other side
    meta = X.v.get("meta", {})
    chap = [i for i, m in enumerate(mods) if m["kind"] not in ("cont",)]
    dots = "".join(f'<i id="hdot{j}"></i>' for j in range(len(chap)))
    src = meta.get("src", "")
    sw = (X.W - 122) if P else 760
    sf = F.fit_text(src, sw, 72 if P else 62, 24 if P else 22, min_px=22, lh=1.35, max_lines=3)
    ttl = meta.get("title", "")
    tt = f'<span class="tt">{X.rich(ttl)}</span>' if ttl and ttl != X.channel else ""
    X.clip("hd", 0, D, f'<div class="hd"><span class="logo"></span>{X.rich(X.channel)}{tt}<span class="dots">{dots}</span></div>'
           + (f'<div class="src" style="font-size:{sf.px}px">{"<br>".join(X.rich(l) for l in sf.lines)}</div>' if src else ""), "iso-ov", 6, track=6)
    X.tw('tl.from("#hd .hd", {y:-30, opacity:0, duration:0.5, ease:"back.out(1.6)"}, 0.15);')
    X.tw('tl.from("#hd .src", {opacity:0, duration:0.5}, 0.35);')
    for j, i in enumerate(chap):
        t = mods[i]["t"]
        X.tw(f'tl.to("#hdot{j}", {{width:30, backgroundColor:"{pal["coral"]}", duration:0.35, ease:"back.out(1.6)"}}, {max(0, t - 0.1):.3f});')
        if j: X.tw(f'tl.to("#hdot{j - 1}", {{width:10, backgroundColor:"#b9aed0", duration:0.3}}, {max(0, t - 0.1):.3f});')

    # ---- the caption sign stays at one height in 9:16 (bottom edge y 1496): clear of the platform's bottom bar and the figures painted low

    # ---- per-beat data notes (how a figure was computed), small, under the title sign
    for i, txt in notes.items():
        t, d = times[i]
        if i + 1 < len(beats) and beats[i]["scene"] == "route" and beats[i + 1]["scene"] == "cont": d += times[i + 1][1]
        nf = F.fit_text(txt, (X.W - 144) if P else 760, 70 if P else 62, 26 if P else 24, min_px=24 if P else 22, lh=1.3, max_lines=2)
        X.clip(f"note{i}", t, d, f'<div class="note" style="font-size:{nf.px}px">{"<br>".join(X.rich(l) for l in nf.lines)}</div>', "iso-ov", 5, track=3 + i % 2)
        X.tw(f'tl.from("#note{i} .note", {{y:-14, opacity:0, duration:0.4, ease:"back.out(1.8)"}}, {t + 0.3:.3f});')

    # ---- DOM signposts at the route's stations (the runtime moves them every frame)
    route = next((m for m in mods if m["kind"] == "route"), None)
    if route:
        names = route.get("names") or ["揽收", "分拨", "干线", "再分拨", "派送"]
        ppx = 36 if P else 28
        pins = "".join(f'<div class="pin" id="pin{j}" style="font-size:{ppx}px"><div class="bd"><b>{j + 1}</b>{X.rich(x)}</div><i class="pl"></i></div>' for j, x in enumerate(names))
        X.used_text.update("123456789")
        X.clip("pins", route["t"], route["d"] + route.get("d2", 0), pins, "iso-ov", 7, track=7)
        for j in range(len(names)):
            X.sfx((route.get("at_pins") or route["t"] + 0.6) + j * 0.12, "click")

    # ---- sound: whooshes on flights, payoffs on the world's moments
    for i, m in enumerate(mods):
        t = m["t"]
        if i and m["kind"] != "cont": X.sfx(t - 0.5, "fly")
        if m["kind"] == "pile":
            X.sfx(max(m["t"] + 1.2, (m.get("at_num") or m["t"] + 1.2) + 0.7), "land")
            if m.get("at_tag"): X.sfx(m["at_tag"] - 0.25, "ding")
        elif m["kind"] == "bars":
            for j in range(len(m["values"])): X.sfx((m.get("at_bars") or t + 0.1) + j * min(0.14, 1.1 / len(m["values"])), "click")
        elif m["kind"] == "route":
            for tj in m.get("at") or []: X.sfx(tj, "land")
        elif m["kind"] == "coins":
            if m.get("at_drop"):
                for j in range(min(6, int(round(m["a"])) - int(round(m["b"])))): X.sfx(m["at_drop"] + j * 0.06 + 0.5, "click")
        elif m["kind"] == "scale":
            X.sfx(t - 0.2, "riser")
            if m.get("at_word"): X.sfx(m["at_word"] - 0.15, "slam")
        elif m["kind"] == "outro":
            X.sfx(t + 0.3, "land")
