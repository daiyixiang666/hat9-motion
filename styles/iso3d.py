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
    "sky0": "#fff3e8", "sky1": "#f6eafc", "sky2": "#e3eeff",
    "slab": "#fdf6ec", "slab2": "#eef7f1", "slab3": "#fbeef4", "slabSide": "#d9cbe6",
    "b0": "#ffb7a1", "b1": "#a9c6ff", "b2": "#9fe3cf", "b3": "#ffe199", "b4": "#cdb8ff", "b5": "#ffc2d6",
    "roof": "#f6f0ea", "window": "#6378b4", "glass": "#7fa2e0", "door": "#6f6a9e", "path": "#e8dfd3",
    "kraft": ["#e9b77e", "#e2a96c", "#efc592", "#d99e60"],
    "coral": "#ff5c7a", "mint": "#2fbf9b", "sky": "#6f9bff", "lilac": "#b49cff",
    "ink": "#2f2a4a", "muted": "#9a90b8", "card": "#ffffff",
    "road": "#8e8aa8", "lane": "#fffaf0", "belt": "#5d5878", "floor": "#f2ece6", "cargo": "#ffffff",
    "trunk": "#a7836b", "leaf0": "#7ed3a5", "leaf1": "#a6e3b4", "tyre": "#2f2a4a", "skin": "#ffd9c2", "cloud": "#ffffff",
    "gold": "#ffcf5a", "gold2": "#f2b63b", "shadow": "#5a4a8a",
    "hemiSky": "#fff6ee", "hemiGround": "#c8bfe8", "sun": "#fff1de",
}

STYLE = {
    "name": "等距微缩", "en": "Iso Miniature", "benchmarks": ["Monument Valley", "Blender 微缩模型 / tilt-shift", "Apple 地图 3D 城市", "Kurzgesagt 城市段落"],
    "tokens": {
        "bg": "#f6eafc", "fg": "#2f2a4a", "muted": "#9a90b8", "accent": "#ff5c7a", "accent2": "#2fbf9b", "alert": "#ff5c7a",
        "line": "#e6dcf0", "paper": "#ffffff", "accent-tx": "#dc2f57", "muted-tx": "#675e86", "ink": "#2f2a4a", "card": "#ffffff", "card-fg": "#2f2a4a", "side": "#d9cbe6", "butter": "#ffd76a",
        "cap-bg": "#2f2a4a", "cap-fg": "#fffaf3", "cap-size": "40px", "cap-weight": "700", "cap-pad": "10px 28px 13px", "cap-radius": "18px",
        "cap-shadow": "none", "cap-em": "#ffd76a", "cap-bottom": "50px", "mascot-bg": "#ffe199",
    },
    "fonts": {"display": ["harmonyos-sans-black", "noto-sans-sc"], "body": ["harmonyos-sans", "noto-sans-sc"], "num": ["archivo", "harmonyos-sans-black"]},
    "motion": {"ease": "back.out(1.6)", "dur": 0.55, "stagger": 0.04, "heading": "pop", "text": "rise", "camera": "none", "cut": "hard", "em": "static"},
    "layers": [("grain", {"opacity": 0.035})],
    "motion_blur": False,
    "caption_mode": "reading",          # 9:16 too: a punch page mid-frame would sit on the islands
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"right": 90, "bottom": 110, "h": 300}, "portrait": {"right": 60, "bottom": 430, "h": 300}},
    "sfx": {"fly": ("whoosh_soft", 0.3), "pop": ("pop", 0.32), "count": ("tick", 0.22), "land": ("boing", 0.3), "ding": ("bell", 0.3),
            "click": ("click", 0.16), "riser": ("riser", 0.22), "slam": ("slam", 0.32), "hit": ("hit", 0.3), "mascot": ("whoosh_soft", 0.25),
            "enter": ("whoosh_soft", 0.25), "transition": ("whoosh_soft", 0.3)},
    "font3d": "harmonyos-sans-black",
}

STYLE["css"] = """
#iso3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-iso3d .iso-ov { position:absolute; inset:0; pointer-events:none; }
.st-iso3d .cap .cp { box-shadow:6px 6px 0 var(--accent); }
.st-iso3d.v .cap { bottom:300px; } .st-iso3d.v .cap .cp { font-size:46px; }
.st-iso3d .ic-wrap { position:absolute; display:flex; align-items:center; }
.st-iso3d.h .ic-wrap { left:96px; top:110px; bottom:150px; width:600px; }
.st-iso3d.v .ic-wrap { left:60px; right:60px; top:300px; align-items:flex-start; }
.st-iso3d .ic-card { width:100%; background:var(--card); color:var(--card-fg); border-radius:30px; padding:34px 44px 36px;
  box-shadow:12px 12px 0 var(--side), 0 30px 60px rgba(80,60,130,.12); }
.st-iso3d.v .ic-card { padding:34px 50px 38px; }
.st-iso3d .ic-k { display:inline-block; font-family:var(--f-body); font-weight:700; color:#fff; background:var(--ink); border-radius:12px; padding:6px 16px 8px;
  letter-spacing:.04em; white-space:nowrap; }
.st-iso3d .ic-n { display:flex; align-items:baseline; gap:.12em; margin-top:16px; white-space:nowrap; line-height:.95; }
.st-iso3d .ic-n .v { font-family:var(--f-num); font-weight:800; letter-spacing:-.035em; font-variant-numeric:tabular-nums; color:var(--ink); }
.st-iso3d .ic-n .u { font-family:var(--f-display); font-weight:900; color:var(--accent-tx); }
.st-iso3d .ic-n .pre { font-family:var(--f-num); font-weight:800; color:var(--muted-tx); letter-spacing:-.03em; }
.st-iso3d .ic-t { font-family:var(--f-display); font-weight:900; line-height:1.12; margin-top:16px; color:var(--ink); }
.st-iso3d .ic-t .em .emt { color:var(--accent-tx); } .st-iso3d .em .emb { display:none; }
.st-iso3d .ic-rows { margin-top:18px; display:flex; flex-direction:column; gap:12px; }
.st-iso3d .ic-r { font-family:var(--f-body); font-weight:700; color:var(--ink); line-height:1.25; }
.st-iso3d .ic-r .em .emt { color:var(--accent-tx); font-family:var(--f-num); font-weight:800; }
.st-iso3d .ic-r.chip { align-self:flex-start; font-weight:600; color:var(--muted-tx); background:#f4eefa; border-radius:10px; padding:5px 14px 7px; }
.st-iso3d .ic-st { position:relative; margin-top:26px; display:flex; justify-content:space-between; }
.st-iso3d .ic-st .rail { position:absolute; left:0; right:0; top:15px; height:6px; border-radius:3px; background:#efe8f6; }
.st-iso3d .ic-st .fill { position:absolute; left:0; right:0; top:15px; height:6px; border-radius:3px; background:var(--accent); transform-origin:0 50%; transform:scaleX(0); }
.st-iso3d .ic-st .s { position:relative; display:flex; flex-direction:column; align-items:center; gap:8px; }
.st-iso3d .ic-st .s i { display:block; width:36px; height:36px; border-radius:50%; background:#fff; border:6px solid #e3d9ef; }
.st-iso3d .ic-st .s b { font-family:var(--f-body); font-weight:700; color:var(--muted-tx); white-space:nowrap; }
.st-iso3d .pin { position:absolute; left:0; top:0; display:flex; align-items:center; gap:10px; background:#fff; color:var(--ink); border-radius:16px;
  padding:8px 18px 9px 9px; font-family:var(--f-body); font-weight:700; white-space:nowrap; box-shadow:5px 5px 0 var(--side); opacity:0; transform-origin:50% 100%; }
.st-iso3d .pin::after { content:""; position:absolute; left:50%; bottom:-11px; margin-left:-9px; border:9px solid transparent; border-top:11px solid #fff; border-bottom:0; }
.st-iso3d .pin b { display:inline-flex; align-items:center; justify-content:center; width:1.55em; height:1.55em; border-radius:50%; background:#efe8f6; color:var(--ink);
  font-family:var(--f-num); font-weight:800; font-size:.85em; }
.st-iso3d .pin.on { background:var(--accent-tx); color:#fff; } .st-iso3d .pin.on::after { border-top-color:var(--accent-tx); } .st-iso3d .pin.on b { background:#fff; color:var(--accent-tx); }
.st-iso3d .hd { position:absolute; display:flex; align-items:center; gap:14px; font-family:var(--f-body); font-weight:700; color:var(--ink);
  background:rgba(255,255,255,.92); border-radius:16px; padding:9px 20px 9px 10px; box-shadow:5px 5px 0 var(--side); }
.st-iso3d .hd .tt { color:var(--muted-tx); font-weight:600; }
.st-iso3d.h .hd { left:96px; top:38px; font-size:24px; } .st-iso3d.v .hd { left:60px; top:126px; font-size:30px; }
.st-iso3d .hd .logo { width:34px; height:34px; border-radius:10px; background:var(--accent); box-shadow:4px 4px 0 var(--side); }
.st-iso3d .hd .dots { display:flex; gap:7px; margin-left:8px; } .st-iso3d .hd .dots i { display:block; width:10px; height:10px; border-radius:5px; background:#ddd2ea; }
.st-iso3d .src { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted-tx); line-height:1.35; background:rgba(255,255,255,.88); border-radius:12px; padding:8px 14px; }
.st-iso3d.h .src { right:80px; top:38px; text-align:right; } .st-iso3d.v .src { left:60px; top:200px; }
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

    # ---- 3D glyph outlines for every string the world extrudes
    text = "0123456789.,%¥×+-"
    for m in mods:
        for key in ("tag", "word", "title", "ya", "yb"): text += str(m.get(key) or "")
        text += "".join(str(x) for x in (m.get("labels") or m.get("values") or [])) + "".join(str(x) for x in (m.get("years") or []))
    fid = S.get("font3d", "harmonyos-sans-black")
    path = fonts.find(fonts.REG[fid]["file"])
    if not path: raise SystemExit(f"iso3d: 3D font {fid} not found ({fonts.REG[fid]['file']})")
    gl = glyphs.outlines(path, text, {"wght": 900})
    miss = "".join(sorted({c for c in text if not c.isspace() and c not in gl}))
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
    sw = (X.W - 150) if P else 760
    sf = F.fit_text(src, sw, 72 if P else 62, 24 if P else 21, min_px=16, lh=1.35, max_lines=2)
    X.clip("hd", 0, D, f'<div class="hd"><span class="logo"></span>{X.rich(X.channel)}<span class="tt">'
           f'{X.rich(meta.get("title", ""))}</span><span class="dots">{dots}</span></div>'
           + (f'<div class="src" style="font-size:{sf.px}px">{"<br>".join(X.rich(l) for l in sf.lines)}</div>' if src else ""), "iso-ov", 6, track=6)
    X.tw('tl.from("#hd .hd", {y:-30, opacity:0, duration:0.5, ease:"back.out(1.6)"}, 0.15);')
    X.tw('tl.from("#hd .src", {opacity:0, duration:0.5}, 0.35);')
    for j, i in enumerate(chap):
        t = mods[i]["t"]
        X.tw(f'tl.to("#hdot{j}", {{width:30, backgroundColor:"{pal["coral"]}", duration:0.35, ease:"back.out(1.6)"}}, {max(0, t - 0.1):.3f});')
        if j: X.tw(f'tl.to("#hdot{j - 1}", {{width:10, backgroundColor:"#b9aed0", duration:0.3}}, {max(0, t - 0.1):.3f});')

    # ---- per-beat cards
    route = next((m for m in mods if m["kind"] == "route"), None)
    bw = (X.W - 120 - 100) if P else (600 - 88)
    for i, (b, (t, d)) in enumerate(zip(beats, times)):
        c = b.get("card")
        if not c or b["scene"] == "cont": continue
        d_all = d + (times[i + 1][1] if b["scene"] == "route" and i + 1 < len(beats) and beats[i + 1]["scene"] == "cont" else 0)
        cid = f"card{i}"
        parts = []
        kf = F.fit_text(c.get("kicker", ""), bw, 44, 34 if P else 28, min_px=18, max_lines=1)
        if c.get("kicker"): parts.append(f'<div class="ic-k" style="font-size:{kf.px}px">{X.rich(kf.lines[0] if kf.lines else c["kicker"])}</div>')
        num = c.get("num")
        if num:
            dec = int(num.get("dec", 0)); v = float(num["v"]); s_end = f"{v:.{dec}f}"
            pre = num.get("pre", "")
            wem = F.width(s_end) * 1.08 + F.width(num.get("unit", "")) * 0.42 + F.width(pre) * 0.5 + 0.3
            px = int(min(170 if P else 150, bw * 0.96 / max(wem, 0.1)))
            parts.append(f'<div class="ic-n">' + (f'<span class="pre" style="font-size:{int(px * 0.5)}px">{X.rich(pre)}</span>' if pre else "")
                         + f'<span class="v" style="font-size:{px}px">{X.rich(f"{float(num.get("from", 0)):.{dec}f}")}</span>'
                         f'<span class="u" style="font-size:{int(px * 0.42)}px">{X.rich(num.get("unit", ""))}</span></div>')
            X.used_text.update("0123456789.")
        title_html = ""
        if c.get("title"):
            tf = F.fit_text(c["title"], bw, 260 if P else 230, 132 if P else 112, max_lines=2)
            title_html = f'<div class="ic-t" style="font-size:{tf.px}px">{"<br>".join(X.rich(l) for l in tf.lines)}</div>'
            if not c.get("at_title"): parts.append(title_html); title_html = ""
        rows = c.get("rows", [])
        if rows:
            rh = []
            for j, r in enumerate(rows):
                txt = r if isinstance(r, str) else (r.get("text") or r.get("chip") or "")
                chip = isinstance(r, dict) and "chip" in r
                rf = F.fit_text(txt, bw - (28 if chip else 0), 100, (26 if P else 22) if chip else (40 if P else 34), min_px=16, lh=1.25, max_lines=2)
                rh.append(f'<div class="ic-r{" chip" if chip else ""}" id="{cid}r{j}" style="font-size:{rf.px}px">{"<br>".join(X.rich(l) for l in rf.lines)}</div>')
            parts.append(f'<div class="ic-rows">{"".join(rh)}</div>')
        if title_html: parts.append(title_html)
        steps = c.get("steps")
        if steps:
            names = steps if isinstance(steps, list) else (route or {}).get("names") or []
            n = len(names)
            spx = F.fit_text("".join(names), bw * 0.9, 50, 30 if P else 25, min_px=16, max_lines=1).px if n else 20
            spx = min(spx, int(bw / max(1, n) / max(1.0, max(F.width(x) for x in names)) * 0.9)) if n else spx
            parts.append('<div class="ic-st"><div class="rail"></div><div class="fill" id="%sfill"></div>%s</div>' % (
                cid, "".join(f'<div class="s" id="{cid}s{j}"><i></i><b style="font-size:{spx}px">{X.rich(x)}</b></div>' for j, x in enumerate(names))))
        X.clip(cid, t, d_all, f'<div class="ic-wrap"><div class="ic-card">{"".join(parts)}</div></div>', "iso-ov", 5, track=3 + i % 2)
        # motion: the card drops in like a block, its pieces pop in order, then it lifts away before the next island
        X.tw(f'tl.from("#{cid} .ic-card", {{y:60, scale:0.9, rotation:-2.5, opacity:0, duration:0.55, ease:"back.out(1.5)"}}, {t:.3f});')
        X.sfx(t + 0.05, "pop")
        if c.get("kicker"): X.tw(f'tl.from("#{cid} .ic-k", {{x:-36, opacity:0, duration:0.4, ease:"back.out(2)"}}, {t + 0.12:.3f});')
        if num:
            cue = T(num.get("at"), t) or t + 0.6
            dur = float(num.get("dur", 1.0))
            ta = max(t + 0.25, cue - dur * 0.7)          # the count lands on its word
            js_fmt = f"o.v.toFixed({dec})"
            X.tw(f'(()=>{{const o={{v:{float(num.get("from", 0))}}}, el=document.querySelector("#{cid} .ic-n .v"); tl.to(o, {{v:{v}, duration:{dur}, ease:"power3.out", onUpdate:()=>{{el.textContent={js_fmt};}}}}, {ta:.3f});}})();')
            show = max(t + 0.1, ta - 0.1) if num.get("reveal") == "cue" else t + 0.15
            X.tw(f'tl.from("#{cid} .ic-n", {{scale:0.6, opacity:0, transformOrigin:"0% 80%", duration:0.45, ease:"back.out(2)"}}, {show:.3f});')
            X.tw(f'tl.fromTo("#{cid} .ic-n .v", {{scale:1}}, {{scale:1.08, duration:0.12, yoyo:true, repeat:1, ease:"power2.out", transformOrigin:"0% 80%"}}, {ta + dur * 0.75:.3f});')
            X.tw(f'tl.fromTo("#{cid} .ic-n .u", {{y:24, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"back.out(2)"}}, {max(show + 0.1, min(ta + dur * 0.6, t + 0.6)):.3f});')
            X.sfx(ta, "count")
        if c.get("title"):
            ta = T(c.get("at_title"), t) or t + 0.25
            X.tw(f'tl.from("#{cid} .ic-t", {{y:40, scale:0.85, opacity:0, transformOrigin:"0% 100%", duration:0.5, ease:"back.out(1.8)"}}, {max(t + 0.1, ta - 0.25):.3f});')
            X.sfx(max(t + 0.1, ta - 0.1), "slam")
        for j, r in enumerate(rows):
            ta = T(r.get("at"), t) if isinstance(r, dict) else None
            ta = max(t + 0.25 + j * 0.08, (ta - 0.2) if ta else t + 0.45 + j * 0.12)
            X.tw(f'tl.from("#{cid}r{j}", {{y:22, opacity:0, duration:0.4, ease:"back.out(1.8)"}}, {ta:.3f});')
            if isinstance(r, dict) and r.get("at"):
                X.tw(f'tl.from("#{cid}r{j} .em", {{scale:1.6, color:"{pal["coral"]}", duration:0.45, ease:"back.out(2.4)"}}, {ta + 0.12:.3f});')
                X.sfx(ta + 0.1, "pop")
        if steps and route:
            names = steps if isinstance(steps, list) else route.get("names") or []
            ats = route.get("at") or []
            for j in range(len(names)):
                tj = ats[j] if j < len(ats) else t + 0.5 + j * 0.4
                X.tw(f'tl.to("#{cid}s{j} i", {{backgroundColor:"{pal["coral"]}", borderColor:"#ffd1db", scale:1.2, duration:0.3, ease:"back.out(2.5)"}}, {tj - 0.05:.3f});')
                X.tw(f'tl.to("#{cid}s{j} b", {{color:"{pal["ink"]}", duration:0.2}}, {tj - 0.05:.3f});')
                if j: X.tw(f'tl.to("#{cid}fill", {{scaleX:{j / max(1, len(names) - 1):.3f}, duration:0.35, ease:"power2.out"}}, {tj - 0.3:.3f});')
        X.tw(f'tl.to("#{cid} .ic-card", {{y:-34, opacity:0, scale:0.96, duration:0.24, ease:"power2.in"}}, {t + d_all - 0.26:.3f});')

    # ---- DOM pins over the route's stations (the runtime moves them every frame)
    if route:
        names = route.get("names") or ["揽收", "分拨", "干线", "再分拨", "派送"]
        ppx = 30 if P else 25
        pins = "".join(f'<div class="pin" id="pin{j}" style="font-size:{ppx}px"><b>{j + 1}</b>{X.rich(x)}</div>' for j, x in enumerate(names))
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
