"""clay · 陶土影棚 —— 一镜到底的陶土小剧场：一张无缝纸背景（地面和墙同一色、柔和的弧形转角），
一个陶土小人把每一句话演出来——拖、跳、压、拉、搬、跳石头、推卷轴、挥手——它的动作让图表发生变化。
哑光陶土、石膏白、赤陶是唯一的饱和色（每段只有一个"活"的物件），柔和真实的投影，没有金属，没有辉光。
小人和物件按"一拍二"（每 2 帧换一个姿势）动，镜头平滑地沿纸背景横移到下一个布景。对标：定格黏土短片、柔和三维编辑插画。

这个风格不走逐句场景：WORLD() 一次性搭好整条片子（runtime/clay3d.js）。每个 beat 是一幕：
  title 拖着立体数字进场 · number 跳压柄、数字一个个从地面弹起 · compare 压泵、两根柱子按真实比例升起
  share 从奶酪轮里拉出真实占比的一块 · rank 按真实宽度搭台阶、举着最后一块放上去
  timeline 按真实高度的踏脚石一块块跳过去 · statement 推着卷轴在斜台上印出一句话、坐在台端
  outro 三个小数字回顾、拍一拍、挥手，灯光转暮色
旧场景名照常可用：quote → statement；其它未知场景按 statement 演；"fx" 段落由效果页盖在布景上。
字段：每个 beat 可写 "head"（墙上印的标题，*词* 为赤陶色）、"sub"（标题下一行小字）、"src"（来源行）。
"""
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

SWEEP, PLASTER, CLAYC, TERRA, DARK, SAGE = "#e9e2d6", "#f6f1e7", "#d8c9b4", "#c8572f", "#3a332d", "#9aa58d"
TERRA_INK = "#a8461f"      # terracotta for type: the same hue, deep enough for 4.5:1 on plaster and on the sweep
SRC_INK = "#5f574e"

STYLE = {
    "name": "陶土影棚", "en": "Clay Studio", "benchmarks": ["定格黏土短片", "柔和三维编辑插画"],
    "look": "clay", "bg3d": SWEEP, "floor3d": SWEEP, "font3d": "noto-serif-sc", "aperture": 0.0,
    "tokens": {
        "bg": SWEEP, "fg": DARK, "muted": "#6f665c", "accent": TERRA_INK, "accent2": TERRA_INK, "alert": TERRA,
        "line": "#d6ccbd", "paper": PLASTER, "ink": DARK, "card": PLASTER, "card-fg": DARK,
        # caption: a plaster pill with a soft shadow, dark clay 44 px, key word terracotta
        "cap-bg": PLASTER, "cap-fg": DARK, "cap-size": "44px", "cap-weight": "700", "cap-pad": "12px 40px 14px", "cap-radius": "38px",
        "cap-shadow": "none", "cap-em": TERRA_INK, "cap-bottom": "460px",
    },
    "fonts": {"display": ["noto-serif-sc", "fraunces"], "body": "noto-sans-sc", "num": ["fraunces", "noto-serif-sc"],
              "mono": "jetbrains-mono", "cap": "noto-sans-sc"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.04, "heading": "rise", "text": "rise", "camera": "none", "cut": "hard",
               "transition": "dip", "em": "static"},
    "layers": [("grain", {"opacity": 0.06, "blend": "multiply"})],
    "motion_blur": False,
    "caption_plate": False,
    "safe_exempt": [],
    "mascot": {"mode": "none"},      # the clay figure is the performer; no host sticker
    "sfx": {"transition": ("whoosh_soft", 0.3), "title": ("pop", 0.35), "pop": ("pop", 0.4), "hit": ("hit", 0.3),
            "count": ("tick", 0.25), "fly": ("whoosh_soft", 0.25), "mascot": None},
    # kept for films written for the old studio-derived clay; the clay world fits its camera per beat instead
    "stations": [],
}

KIND = {"title": "title", "number": "number", "compare": "compare", "share": "share", "rank": "rank", "timeline": "timeline",
        "statement": "statement", "quote": "statement", "outro": "outro", "fx": "fx"}
NOMINAL = {"title": 3.0, "number": 2.7, "compare": 3.3, "share": 2.7, "rank": 3.4, "timeline": 2.9, "statement": 2.6, "outro": 3.0, "fx": 1.0}

FX_CSS = r"""
/* an effect page in clay: the sweep ground with a soft horizon, a printed serif headline, a plaster caption pill */
.fx { background:radial-gradient(120% 70% at 50% 62%, #f1ebe1 0%, #e9e2d6 46%, #ddd4c5 100%) !important; }
.fx::after { content:""; position:absolute; left:-10%; right:-10%; top:64%; height:22%; pointer-events:none;
  background:radial-gradient(60% 50% at 50% 0%, rgba(58,40,25,.10), rgba(58,40,25,0) 70%); }
.fx .big { color:#3a332d; text-shadow:0 .03em 0 rgba(255,255,255,.55), 0 .1em .18em rgba(58,40,25,.16); }
.ctx.clx .hd { left:110px; right:110px; top:52px; height:auto; border:none; display:block; }
.ctx.clx .hd b { font-family:var(--f-display); font-weight:800; font-size:40px; color:#3a332d; letter-spacing:.01em; }
.ctx.clx .hd span { font-family:var(--f-body); font-size:28px; color:#5f574e; opacity:1; margin-left:16px; }
.ctx.clx .hd .fxid { display:none; }
.ctx.clx .cap > span { background:#f6f1e7; color:#3a332d; border-radius:38px; padding:12px 40px 14px; font-weight:700;
  box-shadow:0 10px 24px rgba(58,40,25,.16), 0 2px 0 rgba(58,40,25,.06); }
.ctx.clx .cap .em .emt { background:none; color:#a8461f; padding:0; }
.ctx.clx .ft { opacity:1; color:#5f574e; font-family:var(--f-body); font-size:22px; }
#root.v .ctx.clx .hd { left:110px; right:120px; top:230px; } #root.v .ctx.clx .hd b { font-size:56px; display:block; } #root.v .ctx.clx .hd span { display:block; margin:10px 0 0; font-size:30px; }
#root.v .ctx.clx .cap { top:1384px; bottom:auto; padding:0 120px 0 110px; }
#root.v .ctx.clx .ft { left:110px; right:120px; top:1474px; font-size:22px; }
"""

STYLE["css"] = FX_CSS + r"""
#w3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-clay .cap .cp { box-shadow:0 10px 26px rgba(58,40,25,.17), 0 2px 0 rgba(58,40,25,.05); line-height:1.25; letter-spacing:.01em; }
#root.v.st-clay .clip.cap { padding-left:110px; padding-right:120px; }
#root.v.st-clay .cap .cp { display:block; width:850px; box-sizing:border-box; }
#root.h.st-clay { --cap-bottom:34px; }
#root.h.st-clay .cap .cp { min-width:760px; }
.cl-src { position:absolute; left:110px; top:1474px; height:32px; line-height:32px; font-family:var(--f-body); font-size:22px; font-weight:500;
  color:#5f574e; white-space:nowrap; max-width:850px; overflow:hidden; text-overflow:ellipsis; }
#root.h .cl-src { top:36px; left:auto; right:64px; text-align:right; max-width:760px; }
"""


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect card in clay: headline printed like the wall type, the spoken line on a plaster pill,
    source in warm grey."""
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (f'<div class="hd"><b>{X.rich(X.channel)}</b><span>{parts["topic"]}</span><div class="fxid">{parts["fxid"]}</div></div>'
             + f'<div class="cap"><span style="font-size:{max(42, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.clip(f"{cid}c", t, d, inner, "ctx clx", 30, track=20, sty=parts["sty"])
    X.tw(f'tl.from("#{cid}c .cap > span", {{scaleY:0.2, scaleX:1.08, transformOrigin:"50% 100%", duration:0.32, ease:"back.out(2)"}}, {t + 0.05:.3f});')


def _num(v):
    try:
        return float(str(v).replace(",", ""))
    except (TypeError, ValueError):
        return None


def _em_word(s):
    m = re.search(r"\*([^*]+)\*", str(s or ""))
    return m.group(1) if m else None


def _plain(s):
    return re.sub(r"[*|]", "", str(s or ""))


def _params(b, X, t):
    """what each act needs, from the beat — the clay film's own fields first, then the fields old films use."""
    k = KIND.get(b.get("scene"), "statement")
    p = {}
    if k == "title":
        p["obj"] = str(b.get("obj") or b.get("value") or _em_word(b.get("title")) or _plain(b.get("title"))[:4])
        p["unit"] = b.get("unit") or ""
        p["size"] = b.get("size")
    elif k == "number":
        p["value"] = str(b.get("value", ""))
        p["unit"] = b.get("unit", "")
        if b.get("head") and b.get("label"):
            p["label"] = b["label"]          # printed on the plinth (old films use "label" as the headline instead)
    elif k == "compare":
        items = b.get("items")
        if not items and (b.get("left") or b.get("right")):
            win = 0 if b.get("verdict", "left") == "left" else 1
            items = []
            for j, side in enumerate(("left", "right")):
                s = b.get(side) or {}
                v = _num(s.get("value"))
                items.append({"label": s.get("label", ""), "value": v if v is not None else (1.0 if j == win else 0.62), "display": s.get("display", "")})
        p["items"] = [{"label": it.get("label", ""), "value": _num(it.get("value")) or 0.0,
                       "display": it.get("display") if it.get("display") is not None else str(it.get("value", ""))} for it in (items or [])]
    elif k == "share":
        p["value"] = _num(b.get("value", 50))
        p["display"] = b.get("display")
        p["label"] = b.get("label") if b.get("head") else None
        p["rest"] = b.get("rest")
    elif k in ("rank", "timeline", "outro"):
        p["items"] = []
        for it in b.get("items") or []:
            q = dict(it)
            q["value"] = _num(it.get("value")) or 0.0
            p["items"].append(q)
    elif k == "statement":
        lines = b.get("lines") or str(b.get("text") or b.get("line") or _plain(b.get("title", ""))).split("|")
        p["lines"] = [str(x) for x in lines if str(x).strip()]
    for key in ("hmax", "wmax", "vsize", "angle", "len"):
        if b.get(key) is not None:
            p[key] = b[key]
    head = b.get("head")
    if head is None:
        head = b.get("title") if k in ("title", "outro") else (b.get("label") if k == "number" else None)
    return k, p, head


def _glyph_text(acts):
    s = "0123456789%.,+-"
    for a in acts:
        p = a["p"]
        s += str(p.get("obj", "")) + str(p.get("value", "")) + str(p.get("unit", "")) + str(p.get("display") or "")
        for it in p.get("items", []):
            s += str(it.get("display") or "") + str(it.get("v") or "")
    return s


def WORLD(beats, times, X, D):
    from h9 import glyphs, fonts
    acts = []
    for b, (t, d) in zip(beats, times):
        k, p, head = _params(b, X, t)
        acts.append({"kind": k, "t": round(t, 3), "d": round(d, 3), "p": p, "head": head, "sub": b.get("sub") if k != "outro" or b.get("head") else None,
                     "nominal": NOMINAL.get(k, 3.0), "src": b.get("src", ""), "b": b})
    # extruded type: Fraunces (soft serif, SOFT 100) for figures and Latin, 思源宋体 900 for Chinese
    text = _glyph_text(acts)
    latin = "".join(sorted(set(c for c in text if ord(c) < 0x2000)))
    cjk = "".join(sorted(set(c for c in text if ord(c) >= 0x2000)))
    gl = glyphs.outlines(fonts.find(fonts.REG["fraunces"]["file"]), latin, {"wght": 760, "SOFT": 100, "WONK": 0, "opsz": 144})
    if cjk:
        gl.update({ch: v for ch, v in glyphs.outlines(fonts.find(fonts.REG["noto-serif-sc"]["file"]), cjk, {"wght": 900}).items() if ch not in gl})
    gl["__cap"] = 0.7
    # every string the runtime prints on a canvas joins the font subset
    used = []
    for a in acts:
        used += [str(a["head"] or ""), str(a["sub"] or "")]
        p = a["p"]
        used += [str(p.get("unit", "")), str(p.get("label") or ""), str(p.get("rest") or "")] + [str(x) for x in p.get("lines", [])]
        for it in p.get("items", []):
            used += [str(it.get(k2, "")) for k2 in ("label", "year", "display", "v")]
    X.used_text.update("".join(used).replace("*", ""))
    cfg = {"w": X.W, "h": X.H, "duration": D,
           "beats": [{k2: a[k2] for k2 in ("kind", "t", "d", "p", "head", "sub", "nominal")} for a in acts]}
    js = (SKILL / "runtime" / "clay3d.js").read_text()
    X.extra_head = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
                    '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>')
    X.extra_body = ('<script>window.__hf=window.__hf||{};window.__hf.buildReady=window.__hf.buildReady||{};'
                    'window.__hf.buildReady.world=new Promise(r=>{window.__h9WorldReady=r;});'
                    f'window.__H9_CLAY={json.dumps(cfg, ensure_ascii=False)};window.__H9_GLYPHS={json.dumps(gl, separators=(",", ":"))};</script>'
                    f'<script type="module">{js}</script>')
    X.clip("world", 0, D, '<canvas id="w3d" width="%d" height="%d"></canvas>' % (X.W, X.H), "w3d-host", 1, track=2, attrs='data-motion-blur="off"')
    # source line per beat (flat DOM type, crisp), sounds on the acts, and effect pages for "fx" beats
    for i, a in enumerate(acts):
        t, d = a["t"], a["d"]
        if a["src"] and a["kind"] != "fx":
            X.clip(f"clsrc{i}", t + 0.06, max(0.3, d - 0.06), f'<div class="cl-src">{X.rich(a["src"])}</div>', "cl-srcw", 6, track=3 + i % 2)
            X.tw(f'tl.from("#clsrc{i} .cl-src", {{clipPath:"inset(0 100% 0 0)", duration:0.25, ease:"power2.out"}}, {t + 0.08:.3f});')
        if i:
            X.sfx(t - 0.4, "fly")
        X.sfx(t + 0.9, "pop")
        if a["kind"] == "fx":
            from h9 import aefx
            X.beat = {"t": t, "d": d, "i": i, "n": len(acts)}
            cid = a["b"].get("id") or X.uid("s")
            fn = aefx.FX.get(a["b"].get("fx"))
            if fn:
                fn(X, cid, t, d, a["b"])
