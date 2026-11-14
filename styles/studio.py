"""studio · 三维影棚 —— 一间暗色展厅里的实时三维：抛光黑漆地板（带倒影）、竖向渐变的影棚背景墙、三盏面光（左上暖主光
3400K、右后冷轮廓光、低位补光）。标题是从字体轮廓挤出、带倒角的香槟色拉丝金属字，数字是缎面白瓷，每一段只有一个朱红漆面
的「活物」，面板是烟色玻璃。镜头在一个连续布景里从一站飞到下一站：每站的机位由这一段主体的包围盒和画幅算出来（竖屏主体宽
占画幅 78%、中心在 y 760），主体下方的地板上摆着这一段的图表物件，所以下半屏是画面和倒影，不是空地板。
对标：Apple 产品发布片的展台光、ManvsMachine / Buck 的材质片、UE 实时影棚。精确、建筑感、冷静；不是镀铬（chrome3d），
不是等距微缩（iso3d），也不是陶土（clay）。适合：年报、产品、需要"贵"的一期。

这个风格不走逐句场景：WORLD() 一次性搭好整条片子的三维世界（runtime/world3d.js），每个 beat 是一个展台：
  title      两三行叠起来的立体字从漆面地板里长出来，主光扫过            lines: ["第一行", "*4162*亿美元"]（*…* 用白瓷）
  number     白瓷大数字站在转盘上，单位是金属字；地板上一排小瓷块按真实个数亮成朱红   value, unit, lit, of (10 | 100)
  compare    两根圆柱，高度按真实比例，以同样速度升起（矮的先停），顶上是数值，高的那根朱红   left / right: {label, value, show}
  rank       4–5 根躺在地板上的圆角长条，长度按真实比例，近端面上是小立体字，镜头俯视 35°   items: [{label, value, show}]
  share      斜立在支架上的粗圆环，真实占比的一段是朱红并滑出               value (0–1 或百分数), show, label
  timeline   沿对角线排开的踏步柱，高度按真实比例，一颗金属球按年份一跳一跳滚过柱顶   items: [{label, value, show}]
  statement  立在地板上的烟色玻璃板，句子是玻璃里的亮字（透视正确），一个词朱红；可选 bars 两根躺条   lines / text
  outro      三座小台座上的白瓷数字，镜头拉远升高看见整个布景，灯只剩轮廓光     items: ["4162亿", …]
旧场景名照常可用：quote → statement；旧的 title / compare / number / statement / outro 字段会被换算成上面的展台。
平面层只有三样：字幕（烟色玻璃条，竖屏 y 1384–1460）、出处行、顶上一行等宽小标（kicker）。不出主持人。
"""
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

VERMILION = "#e2432a"
CHAMPAGNE = "#d9c7a3"
CERAMIC = "#ece8df"

STYLE = {
    "name": "三维影棚", "en": "3D Studio", "benchmarks": ["Apple 产品发布片展台光", "ManvsMachine", "Buck", "UE 实时影棚"],
    "tokens": {
        "bg": "#0b0c10", "fg": "#ece8df", "muted": "#9aa0aa", "accent": VERMILION, "accent2": CHAMPAGNE, "alert": "#e0392f",
        "line": "#1a1c20", "paper": "#07080b", "ink": "#000", "card": "#111", "card-fg": "#f3ede0",
        "cap-fg": "#f3efe6", "cap-size": "40px", "cap-weight": "600", "cap-shadow": "none", "cap-em": "#ff8a6e",
        "cap-bg": "linear-gradient(180deg, rgba(44,48,58,.78), rgba(18,20,26,.84))", "cap-pad": "0 32px", "cap-radius": "14px",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono"},
    "font3d": "noto-sans-sc",
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.03, "heading": "blurin", "text": "blurin", "camera": "none", "cut": "hard", "transition": "dip", "em": "static"},
    "layers": [("grain", {"opacity": 0.07})],
    "motion_blur": False,
    "safe_exempt": [".w-tag"],     # the channel tag at the top is page furniture
    # the host is never placed in a studio film (WORLD turns it off); this entry stays for styles built on studio
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 70, "bottom": 30, "h": 300}, "portrait": {"left": 60, "bottom": 300, "h": 340}},
    "sfx": {"transition": ("whoosh_deep", 0.35), "title": ("boom", 0.4), "line": ("whoosh_soft", 0.25), "enter": ("whoosh_deep", 0.3), "pop": ("pop", 0.4),
            "hit": ("hit", 0.4), "count": ("tick", 0.25), "mascot": ("whoosh_soft", 0.25), "fly": ("whoosh_soft", 0.3)},
    # camera stations of the 0.x six-beat set (used only by styles built on studio that keep that set, e.g. clay)
    "stations": [
        {"cam": [0, 0.35, 9.8], "look": [0, 0.0, 0], "focus": 9.8, "drift": 0.4},
        {"cam": [0, 0.6, -11.4], "look": [0, 0.1, -20], "focus": 8.6, "drift": 0.5},
        {"cam": [0, 0.8, -31.8], "look": [0.2, 0.3, -40], "focus": 8.2, "drift": 0.45},
        {"cam": [0, 5.4, -51.0], "look": [0, -0.2, -61.5], "focus": 11.0, "drift": 0.4},
        {"cam": [-2.6, 0.6, -71.6], "look": [-0.4, 0.2, -80], "focus": 8.6, "drift": 0.5},
        {"cam": [0, 0.6, -92.6], "look": [0, 0.45, -100], "focus": 7.4, "drift": 0.3},
    ],
}

# the 0.x overlay css (quote / outro / tag layers of the six-beat set); the showroom adds its own in WORLD()
STYLE["css"] = """
/* 9:16: the caption's bottom edge sits at y 1496, above the platform's bottom bar (bottom 400 px) */
#root.v.st-studio { --cap-bottom:424px; }
#root.v.st-studio .w-out { bottom:440px; }   /* 9:16: the call to action above the platform's bottom bar */
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




# ---------------------------------------------------------------- the showroom (0.19): one station per beat
# the only flat layers: kicker (mono, top), caption (smoked-glass plate), source line. Everything else is 3D.
STUDIO_CSS = """
#w3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-studio { background:#07080b; }
.st-studio .mascot { display:none !important; }
.st-studio .sd-ov { position:absolute; inset:0; pointer-events:none; }
.st-studio .sd-k { position:absolute; font-family:var(--f-mono); font-size:26px; line-height:36px; letter-spacing:.16em; color:#c9ccd3; white-space:nowrap; }
.st-studio .sd-k b { color:#ff8a6e; font-weight:700; margin-right:.9em; letter-spacing:.06em; }
.st-studio .sd-src { position:absolute; font-family:var(--f-body); font-size:24px; line-height:32px; color:#a3a8b2; white-space:nowrap; letter-spacing:.02em; }
#root#root.st-studio .clip.cap { top:var(--sd-cap-top) !important; bottom:auto !important; left:var(--sd-cap-x) !important; right:auto !important;
  width:var(--sd-cap-w); padding:0 !important; text-align:center; }
#root#root.st-studio .cap .cp { display:block; box-sizing:border-box; width:100%; height:76px; line-height:76px; padding:0 28px; white-space:nowrap;
  font-family:var(--f-body); font-size:44px; font-weight:700; color:#f3efe6; letter-spacing:.02em; text-shadow:none;
  background:linear-gradient(180deg, rgba(46,50,60,.80), rgba(16,18,23,.86)); border-radius:14px;
  border-top:1px solid rgba(255,255,255,.42); box-shadow:inset 0 0 0 1px rgba(255,255,255,.06), 0 18px 40px rgba(0,0,0,.45);
  -webkit-backdrop-filter:blur(18px) saturate(1.2); backdrop-filter:blur(18px) saturate(1.2); }
#root#root.st-studio .cap .em .emt { color:#ff8a6e; }
#root.v.st-studio { --sd-cap-top:1384px; --sd-cap-x:100px; --sd-cap-w:860px; }
#root.h.st-studio { --sd-cap-top:932px; --sd-cap-x:460px; --sd-cap-w:1000px; }
"""


def _num(v):
    try:
        return float(str(v).replace(",", "").replace("%", ""))
    except ValueError:
        return 0.0


def _runs(s):
    """'*4162*亿美元' → [["4162", "c"], ["亿美元", "m"]]: *…* is ceramic, the rest champagne metal."""
    out, em = [], False
    for part in re.split(r"(\*)", str(s)):
        if part == "*":
            em = not em
            continue
        if part:
            out.append([part, "c" if em else "m"])
    return out


def _plain(s):
    return re.sub(r"[*|]", "", str(s))


def _split6(s):
    """break a headline into lines of at most 6 Chinese glyphs (Latin / digits count half)."""
    s = _plain(s).strip()
    lines, cur, n = [], "", 0.0
    for ch in s:
        w = 0.5 if ch.isascii() else 1.0
        if n + w > 6 and cur:
            lines.append(cur.strip())
            cur, n = "", 0.0
        cur += ch
        n += w
    if cur.strip():
        lines.append(cur.strip())
    return lines[:3] or ["示例"]


def _items(raw):
    out = []
    for it in raw or []:
        if isinstance(it, dict):
            out.append({"label": str(it.get("label", it.get("k", ""))), "value": _num(it.get("value", it.get("v", 0))),
                        "show": str(it.get("show", it.get("value", "")))})
        else:
            lab, val = it[0], it[1]
            out.append({"label": str(lab), "value": _num(val), "show": str(it[2] if len(it) > 2 else val)})
    return out


def _side(s, fallback):
    s = s or {}
    has = s.get("value") is not None
    return {"label": str(s.get("label", fallback)), "value": _num(s.get("value", 1)) if has else None,
            "show": str(s.get("show", s.get("value", ""))) if has else ""}


def _beat_cfg(b, t, d, X):
    k = b.get("scene", "title")
    k = {"quote": "statement"}.get(k, k)
    c = {"kind": k, "t": t, "d": d}
    if k == "title":
        lines = b.get("lines") or _split6(b.get("title", ""))
        c["lines"] = [_runs(x) for x in lines[:3]]
        c["teaser"] = [float(x) for x in (b.get("teaser") or [])][:3]
    elif k == "number":
        val = str(b.get("value", "0"))
        unit = str(b.get("unit", ""))
        v = _num(val)
        of = int(b.get("of", 100))
        lit = b.get("lit", b.get("hl", round(v) if unit == "%" and v <= 100 else 10))
        c.update(value=val, unit=unit, of=of, lit=max(0, min(of, int(round(float(lit))))),
                 dec=len(val.split(".")[1]) if "." in val else 0)
    elif k == "compare":
        L, R = _side(b.get("left"), "A"), _side(b.get("right"), "B")
        if L["value"] is None or R["value"] is None:       # 0.x compare (two labelled pictures): equal pedestals, the verdict side lit
            L["value"] = R["value"] = 1.0
            hi = 0 if b.get("verdict", "left") == "left" else 1
            c["delta"] = "VS"
        else:
            hi = 0 if L["value"] >= R["value"] else 1
        c.update(left=L, right=R, hi=hi)
        if b.get("delta"):
            c["delta"] = str(b["delta"])
    elif k == "rank":
        c["items"] = _items(b.get("items"))[:5]
    elif k == "share":
        v = _num(b.get("value", 0.5))
        c.update(frac=v / 100 if v > 1 else v, show=str(b.get("show", f"{v:g}")), label=str(b.get("label", "")))
    elif k == "timeline":
        c["items"] = _items(b.get("items"))[:6]
    elif k == "statement":
        if b.get("lines"):
            lines = [str(x) for x in b["lines"]]
        elif b.get("text"):
            lines = [x for x in str(b["text"]).split("|") if x.strip()]
        else:
            lines = [str(x) for x in (b.get("words") or ["示例"])]
        c["lines"] = lines[:3]
        c["bars"] = _items(b.get("bars"))[:2]
    elif k == "outro":
        items = [str(x) for x in (b.get("items") or [])][:3]
        c["items"] = items or [_plain(b.get("title", X.channel))[:6] or "示例"]
        c["labels"] = [str(x) for x in (b.get("labels") or [])][:len(c["items"])]
        c["hi"] = int(b.get("hi", -1))
    else:
        c["kind"] = "title"
        c["lines"] = [_runs(x) for x in _split6(b.get("title") or b.get("text") or b.get("label") or b.get("value") or "—")]
    return c


def _glyph_text(c):
    parts = []
    for key in ("value", "unit", "show", "label", "delta"):
        if c.get(key):
            parts.append(str(c[key]))
    for ln in c.get("lines", []):
        parts.append("".join(r[0] for r in ln) if isinstance(ln, list) else _plain(ln))
    parts.extend(c.get("labels", []))
    for it in c.get("items", []) + c.get("bars", []):
        parts.append(json.dumps(it, ensure_ascii=False) if isinstance(it, dict) else str(it))
    for side in ("left", "right"):
        if c.get(side):
            parts.append(c[side]["label"] + c[side]["show"])
    return "".join(parts)


def WORLD(beats, times, X, D):
    if X.S.get("look") == "clay":
        return _world_legacy(beats, times, X, D)
    from h9 import glyphs, fonts
    P = X.portrait
    W, H = X.W, X.H
    meta = X.v.setdefault("meta", {})
    meta.setdefault("mascot_mode", "off")            # no host sticker in the showroom
    X.S["css"] = ""                                  # the 0.x overlay css (quote / outro / tag layers) has no layer to style here
    silent = bool(meta.get("silent"))
    cfg = {"w": W, "h": H, "portrait": P, "D": D, "beats": [_beat_cfg(b, t, d, X) for b, (t, d) in zip(beats, times)],
           "aperture": X.S.get("aperture", 0.0011)}
    # 3D type: CJK from the heavy Noto Sans SC, Latin and figures from Inter ExtraBold; glass-slab text at a reading weight
    text3d = set("0123456789.,%+-亿美元")
    slab = set()
    for c in cfg["beats"]:
        if c["kind"] == "statement":
            slab.update(_plain("".join(c["lines"])))
            for it in c["bars"]:
                text3d.update(it["label"] + it["show"])
        else:
            text3d.update(_glyph_text(c))
    text3d = "".join(sorted(ch for ch in text3d if not ch.isspace()))
    cjk = fonts.find(fonts.REG[X.S.get("font3d", "noto-sans-sc")]["file"])
    lat = fonts.find(fonts.REG["inter"]["file"])
    gl = glyphs.outlines(cjk, text3d, {"wght": 900})
    gl.update(glyphs.outlines(lat, "".join(ch for ch in text3d if ch.isascii()), {"wght": 800}))
    sl_txt = "".join(sorted(slab))
    gl2 = glyphs.outlines(cjk, sl_txt, {"wght": 700})
    gl2.update(glyphs.outlines(lat, "".join(ch for ch in sl_txt if ch.isascii()), {"wght": 700}))
    js = (SKILL / "runtime" / "world3d.js").read_text()
    X.css("w3d-import", "")
    X.css("studio-room", STUDIO_CSS)
    X.extra_head = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
                    '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>')
    X.extra_body = ('<script>window.__hf=window.__hf||{};window.__hf.buildReady=window.__hf.buildReady||{};'
                    'window.__hf.buildReady.world=new Promise(r=>{window.__h9WorldReady=r;});'
                    f'window.__H9_WORLD={json.dumps(cfg, ensure_ascii=False)};window.__H9_GLYPHS={json.dumps(gl, separators=(",", ":"))};'
                    f'window.__H9_GLYPHS2={json.dumps(gl2, separators=(",", ":"))};</script>'
                    f'<script type="module">{js}</script>')
    X.clip("world", 0, D, '<canvas id="w3d" width="%d" height="%d"></canvas>' % (W, H), "w3d-host", 1, track=2, attrs="data-motion-blur=\"off\"")

    # flat layers: kicker + source, per beat. 9:16: kicker at y 220, source at y 1474 (under the caption plate);
    # 16:9: kicker top-left, source under the caption.
    kpos = "left:100px;top:220px" if P else "left:96px;top:64px"
    spos = "left:100px;top:1474px" if P else f"left:460px;top:{932 + 76 + 12}px"
    real = [c for c in cfg["beats"] if c["kind"] != "outro"]
    for i, (b, c) in enumerate(zip(beats, cfg["beats"])):
        t, d = c["t"], c["d"]
        enter = t + (0.32 if i else 0.25)
        leave = t + d - 0.42
        k = b.get("kicker", "")
        if k:
            idx = f"{real.index(c) + 1:02d}" if c in real else "——"
            html = f'<div class="sd-k" style="{kpos}"><b>{idx}</b>{X.rich(k, split="chars")}</div>'
            X.clip(f"sdk{i}", t, d, html, "sd-ov", 7, track=3 + i % 2)
            X.tw(f'tl.from("#sdk{i} .sd-k b",{{opacity:0,x:-14,duration:0.3,ease:"expo.out"}},{enter:.3f});')
            X.enter(f"#sdk{i} .sd-k .c", enter + 0.06, "text", verb="type", stagger=min(0.025, 0.6 / max(1, len(str(k)))))
            if i + 1 < len(beats):
                X.tw(f'tl.to("#sdk{i} .sd-k",{{opacity:0,duration:0.2,ease:"power2.in"}},{leave:.3f});')
        if b.get("src"):
            X.clip(f"sds{i}", t, d, f'<div class="sd-src" style="{spos}">{X.rich(b["src"])}</div>', "sd-ov", 7, track=5 + i % 2)
            X.tw(f'tl.from("#sds{i} .sd-src",{{opacity:0,y:8,duration:0.35,ease:"expo.out"}},{enter + 0.3:.3f});')
            if i + 1 < len(beats):
                X.tw(f'tl.to("#sds{i} .sd-src",{{opacity:0,duration:0.2,ease:"power2.in"}},{leave:.3f});')
        if not silent:
            if i:
                X.sfx(t - 0.5, "fly")
            X.sfx(t + 0.4, "enter")


def _world_legacy(beats, times, X, D):
    """the 0.x six-beat set (title, compare, statement, number, quote, outro), kept for styles built on it (clay)."""
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
        "legacy": True, "stations": st, "beats": [{"t": t, "d": d} for t, d in times],
        "images": {"a": X.asset(cb["left"]["img"]), "b": X.asset(cb["right"]["img"]), "quote": X.asset(qb["image"]),
                   "desk": X.asset(tb["image"]), **{f"w{i}": X.asset(p) for i, p in enumerate(tb.get("wall", []))}},
        "s1": {"t": t1, "title": tb["title"].replace("*", ""), "sub": tb.get("sub", "")},
        "s2": {"t": t2, "la": cb["left"]["label"], "lb": cb["right"]["label"], "stickers": cb["right"].get("stickers", []),
               "ta": X.T(cb.get("at_left"), t2) or t2 + 1, "tb": X.T(cb.get("at_right"), t2) or t2 + 2,
               "ts": X.T(cb.get("at_stickers"), t2) or t2 + 2.5, "tv": X.T(cb.get("at_verdict"), t2)},
        "s3": {"t": t3, "a": stack[0], "b": stack[1], "ta": X.T((sb.get("at") or [None])[0], t3) or t3 + 0.1,
               "tb": X.T((sb.get("at") or [None, None])[1], t3) or t3 + 0.9},
        "s4": {"t": t4, "v": int(nb["value"]), "hl": int(nb.get("hl", 10)), "ta": X.T(nb.get("at"), t4) or t4 + 0.2, "th": X.T(nb.get("at_hl"), t4) or t4 + 1.4},
        "s5": {"t": t5}, "s6": {"t": t6, "d": d6, "title": ob.get("title", X.channel)},
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
    X.clip("wtag", 0, D, f'<div class="w-tag">{X.rich(X.channel)}</div>', "w-ov", 6, track=5)
