"""chrome3d · Y2K 镀铬 3D —— 液态镀铬立体字、镭射全息材质、酸性图形 HUD：Behance / Instagram 上的 chrome typography 潮流，
加上当代 MV 包装的镜头语言。真正从字体轮廓挤出的三维字（拉丁用 Archivo 超宽特粗，中文用阿里巴巴普惠体 Heavy），
程序生成的影棚 HDRI 给出锐利的高光条；纯黑底 + 镜面铬 + 一种霓虹粉。镜头在一组组"展台"之间甩镜飞行。
适合：科技 / 潮流 / 增长数字 / 产品发布 / 年轻向的开场。与 studio（金色 PBR 影棚）和 clay（黏土）完全不同：
没有地面布景，没有暖光，物体漂浮在黑色虚空里，靠反射和辉光说话。

这个风格不走逐句场景：WORLD() 一次性搭好整条片子（runtime/chrome3d.js），每个 beat 是一个展台：
  hero    一个大数字 / 短词（deco: ring | blob；可选 chip、sticker、date、at_enter 推迟数字入场）
  bars    3–6 根镀铬柱，最后一根计数 + 霓虹描边          items: [[标签, 数值], …]
  multiple 倍数冲屏 + 冲击环 + 速度线                    value: "12.9×"
  coins   N 枚镀铬圆片翻面，hit 枚翻成粉色               n, hit, value: "75%"
  moat    芯片落位 → 护城河环 → 打叉下沉 → 新词升起       chip, word
  swarm   数字 + 成百上千颗环绕的小球 + 代码面板          value, count
  shovel  镀铬铲子 + 金块雨 + 两行立体字                  lines: [第一行, 第二行]
  outro   镀铬礼帽 + 名字
换站是无闪光的甩镜（运动线 + 局部高光）；全屏闪白只给最多 3 个揭晓点（beat 上写 "flash": true，默认：blob 数字、moat 新词、outro）。
"""
import json, math
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PINK = "#ff3ec8"

STYLE = {
    "name": "Y2K 镀铬 3D", "en": "Y2K Chrome 3D", "benchmarks": ["Behance chrome type", "MV 包装 (Y2K revival)", "Nike / Apple Music 潮流海报", "Acid graphics"],
    "tokens": {
        "bg": "#000000", "fg": "#f4f4f6", "muted": "#8d8e98", "accent": PINK, "accent2": "#cfd3dc", "alert": PINK,
        "line": "#2a2a31", "paper": "#000000", "ink": "#000000", "card": "#0b0b0f", "card-fg": "#f4f4f6",
        "cap-fg": "#ffffff", "cap-size": "42px", "cap-weight": "800", "cap-em": PINK,
        "cap-shadow": "0 0 3px #000, 0 2px 0 #000, 0 0 22px rgba(0,0,0,.95)",
    },
    "fonts": {"display": ["archivo", "smiley-sans"], "zh": ["smiley-sans", "noto-sans-sc"], "body": ["alibaba-puhuiti", "noto-sans-sc"],
              "mono": ["space-mono", "noto-sans-sc"]},
    "font3d": {"latin": "archivo", "latin_axes": {"wght": 900, "wdth": 125}, "cjk": "alibaba-puhuiti-heavy"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.03, "heading": "blurin", "text": "blurin", "camera": "none", "cut": "hard", "transition": "dip", "em": "color"},
    "caption_mode": "reading",
    "layers": [("grain", {"opacity": 0.05})],
    "motion_blur": False,
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"left": 56, "bottom": 30, "h": 250}, "portrait": {"left": 40, "bottom": 600, "h": 280}},
    "sfx": {"fly": ("whoosh", 0.28), "transition": ("whoosh", 0.28), "slam": ("slam", 0.42), "boom": ("boom", 0.42), "pop": ("pop", 0.32),
            "glitch": ("glitch", 0.3), "hit": ("hit", 0.38), "tick": ("tick", 0.22), "riser": ("riser", 0.22), "type": ("type", 0.16),
            "shutter": ("shutter", 0.28), "mascot": ("whoosh_soft", 0.22), "enter": ("whoosh_soft", 0.22), "title": ("slam", 0.42)},
}

STYLE["css"] = """
#w3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-chrome3d .c-ov { position:absolute; inset:0; pointer-events:none; }
.st-chrome3d .mono { font-family:var(--f-mono); }
/* frame furniture */
.st-chrome3d .cn { position:absolute; width:38px; height:38px; border:0 solid rgba(226,228,236,.75); }
.st-chrome3d .cn.tl { left:28px; top:28px; border-left-width:2px; border-top-width:2px; }
.st-chrome3d .cn.tr { right:28px; top:28px; border-right-width:2px; border-top-width:2px; }
.st-chrome3d .cn.bl { left:28px; bottom:28px; border-left-width:2px; border-bottom-width:2px; }
.st-chrome3d .cn.br { right:28px; bottom:28px; border-right-width:2px; border-bottom-width:2px; }
.st-chrome3d .tag { position:absolute; display:flex; align-items:baseline; gap:14px; }
.st-chrome3d .tag b { font-family:var(--f-zh); font-weight:400; font-size:28px; color:#fff; letter-spacing:.04em; }
.st-chrome3d .tag span { font-family:var(--f-mono); font-size:15px; letter-spacing:.24em; color:var(--muted); }
.st-chrome3d .tc { position:absolute; font-family:var(--f-mono); font-size:17px; letter-spacing:.16em; color:#e8e9ee; display:flex; align-items:center; gap:12px; }
.st-chrome3d .tc i { width:12px; height:12px; border-radius:50%; background:var(--accent); box-shadow:0 0 14px var(--accent); display:block; }
.st-chrome3d .tick { position:absolute; left:28px; right:28px; height:34px; overflow:hidden; border-top:1px solid rgba(255,255,255,.16); border-bottom:1px solid rgba(255,255,255,.16); }
.st-chrome3d .tick .tk { position:absolute; left:0; top:0; height:34px; line-height:34px; white-space:nowrap; font-family:var(--f-mono); font-size:15px; letter-spacing:.18em; color:#a9aab3; }
.st-chrome3d .tick .tk b { color:#ff6fd6; font-weight:400; padding:0 .9em; }
/* per-beat kicker + source */
.st-chrome3d .kk { position:absolute; }
.st-chrome3d .kk .ke { font-family:var(--f-mono); font-size:16px; letter-spacing:.22em; color:#b7b8c2; white-space:nowrap; }
.st-chrome3d .kk .ke b { color:var(--accent); font-weight:400; margin-right:1.1em; }
.st-chrome3d .kk .kz { font-family:var(--f-zh); color:#fff; line-height:1.1; margin-top:8px; white-space:nowrap;
  background:linear-gradient(180deg,#ffffff 0%,#e9eaf0 38%,#8a8c96 52%,#f6f6fa 70%,#c9cbd4 100%); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }
.st-chrome3d .kk .kb { height:3px; width:120px; background:var(--accent); margin-top:12px; transform-origin:0 50%; box-shadow:0 0 12px var(--accent); }
.st-chrome3d .src { position:absolute; font-family:var(--f-mono); color:#9c9da7; letter-spacing:.04em; line-height:1.35; }
.st-chrome3d .src b { color:var(--accent); font-weight:400; margin-right:.6em; letter-spacing:.2em; }
/* stickers and chips */
.st-chrome3d .chip { position:absolute; display:flex; justify-content:center; }
.st-chrome3d .chip span { font-family:var(--f-body); font-weight:700; color:#fff; border:2px solid var(--accent); border-radius:999px; padding:.18em .9em;
  box-shadow:0 0 18px rgba(255,62,200,.45), inset 0 0 12px rgba(255,62,200,.25); background:rgba(0,0,0,.55); white-space:nowrap; }
.st-chrome3d .pill { position:absolute; font-family:var(--f-display); font-variation-settings:"wdth" 125, "wght" 900; color:#000; background:var(--accent);
  padding:.12em .55em; border-radius:999px; white-space:nowrap; box-shadow:0 0 26px rgba(255,62,200,.6); }
.st-chrome3d .burst { position:absolute; display:grid; place-items:center; }
.st-chrome3d .burst svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.st-chrome3d .burst .bt { position:relative; text-align:center; color:#000; line-height:1.05; }
.st-chrome3d .burst .bt b { display:block; font-family:var(--f-zh); font-weight:400; }
.st-chrome3d .burst .bt i { display:block; font-style:normal; font-family:var(--f-mono); letter-spacing:.14em; margin-top:.25em; }
.st-chrome3d .date { position:absolute; font-family:var(--f-mono); color:#fff; letter-spacing:.2em; border:1px solid rgba(255,255,255,.5); padding:.35em .8em; background:rgba(0,0,0,.5); white-space:nowrap; }
.st-chrome3d .date b { color:var(--accent); font-weight:400; margin-right:.7em; }
.st-chrome3d .eq { position:absolute; text-align:center; font-family:var(--f-mono); color:#d8d9e0; letter-spacing:.12em; white-space:nowrap; }
.st-chrome3d .eq b { color:var(--accent); font-weight:400; }
.st-chrome3d .lg { position:absolute; display:flex; gap:28px; font-family:var(--f-body); font-weight:700; color:#e9eaf0; white-space:nowrap; }
.st-chrome3d .lg span { display:flex; align-items:center; gap:10px; }
.st-chrome3d .lg i { width:.8em; height:.8em; border-radius:50%; display:block; }
.st-chrome3d .lg .a i { background:var(--accent); box-shadow:0 0 12px var(--accent); }
.st-chrome3d .lg .b i { background:linear-gradient(135deg,#fff,#7d808a); }
/* code panel */
.st-chrome3d .code { position:absolute; border:1px solid rgba(255,255,255,.22); background:rgba(6,6,9,.72); overflow:hidden; }
.st-chrome3d .code .hd { display:flex; justify-content:space-between; align-items:center; padding:12px 18px; border-bottom:1px solid rgba(255,255,255,.14); font-family:var(--f-mono); color:#a7a8b2; letter-spacing:.16em; }
.st-chrome3d .code .hd .n { color:#fff; font-family:var(--f-display); font-variation-settings:"wdth" 125, "wght" 800; letter-spacing:.02em; }
.st-chrome3d .code .bd { padding:14px 18px; font-family:var(--f-mono); color:#d6d7de; white-space:pre; line-height:1.55; }
.st-chrome3d .code .bd .l { display:block; } .st-chrome3d .code .bd .k { color:var(--accent); } .st-chrome3d .code .bd .c { color:#6f707a; }
.st-chrome3d .code .bd .cur { display:inline-block; width:.6em; height:1.1em; background:var(--accent); vertical-align:-.2em; }
/* whip streaks over each camera flight: thin motion lines, no full-frame light */
.st-chrome3d .whip i { position:absolute; left:0; display:block; border-radius:2px;
  background:linear-gradient(90deg, rgba(225,228,238,0), rgba(225,228,238,.7) 55%, rgba(255,255,255,.85) 70%, rgba(225,228,238,0)); }
.st-chrome3d .whip i.p { background:linear-gradient(90deg, rgba(255,62,200,0), rgba(255,62,200,.75) 60%, rgba(255,62,200,0)); }
.st-chrome3d .spk { position:absolute; width:40px; height:40px; }
.st-chrome3d .spk svg { width:100%; height:100%; display:block; overflow:visible; }
#root.v .cap .cp { max-width:900px; }
"""

STAR = '<svg viewBox="-50 -50 100 100"><path d="M0-50 Q0 0 50 0 Q0 0 0 50 Q0 0 -50 0 Q0 0 0-50Z" fill="{c}"/></svg>'


def _burst_svg(n=16, r0=0.78, r1=1.0):
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n - math.pi / 2
        r = r1 if k % 2 == 0 else r0
        pts.append(f"{50 + 50 * r * math.cos(a):.1f},{50 + 50 * r * math.sin(a):.1f}")
    return f'<svg viewBox="0 0 100 100"><polygon points="{" ".join(pts)}" fill="{PINK}"/><polygon points="{" ".join(pts)}" fill="none" stroke="#fff" stroke-width="1.2" transform="translate(50 50) scale(.9) translate(-50 -50)"/></svg>'


def _num(v):
    return float(str(v).replace(",", ""))


def _dec(v):
    s = str(v)
    return len(s.split(".")[1]) if "." in s else 0


def WORLD(beats, times, X, D):
    from h9 import glyphs, fonts, fit
    P = X.portrait
    W, H = X.W, X.H
    meta = X.v.get("meta", {})
    n = len(beats)
    cfg = {"w": W, "h": H, "portrait": P, "accent": PINK, "D": D, "beats": []}
    text3d = set("0123456789.,%$×+-")
    for i, (b, (t, d)) in enumerate(zip(beats, times)):
        k = b.get("scene", "hero")
        T = lambda key, dflt=None: (X.T(b.get(key), t) if b.get(key) is not None else dflt)
        c = {"kind": k, "t": t, "d": d}
        if k == "hero":
            c.update(value=str(b.get("value", "")), at=T("at", t + 0.6), enter=T("at_enter", t), deco=b.get("deco", "ring" if i % 2 == 0 else "blob"))
            text3d.update(c["value"])
        elif k == "bars":
            items = [[str(a), _num(v)] for a, v in b["items"]]
            dec = max(_dec(v) for _, v in b["items"])
            c.update(items=items, dec=dec, pre=b.get("pre", ""), suf=b.get("suf", ""), at=T("at", t + 0.2), at_v=T("at_v", t + 1.2))
            text3d.update("".join(a for a, _ in items)); text3d.update(c["pre"] + c["suf"])
        elif k == "multiple":
            c.update(value=str(b["value"]), at=T("at", t + 0.8)); text3d.update(c["value"])
        elif k == "coins":
            nn = int(b.get("n", 100)); hit = max(0, min(nn, int(round(_num(b.get("hit", 75))))))
            val = str(b.get("value", f"{hit}%"))
            num = "".join(ch for ch in val if ch.isdigit() or ch == ".")
            c.update(n=nn, hit=hit, value=val, to=_num(num or hit), dec=_dec(num or hit), pre=val[:val.find(num)] if num else "",
                     suf=val[val.find(num) + len(num):] if num else "", at_show=T("at_show", t + 0.6), at_hit=T("at_hit", t + 1.8))
            text3d.update(val)
        elif k == "moat":
            c.update(chip=str(b.get("chip", "GPU")), word=str(b.get("word", "CUDA")), at_moat=T("at_moat", t + 0.8),
                     at_chip=T("at_chip", t + 1.8), at_word=T("at_word", t + 2.8))
            text3d.update(c["chip"] + c["word"])
        elif k == "swarm":
            c.update(value=str(b["value"]), at=T("at", t + 0.6)); text3d.update(c["value"])
        elif k == "shovel":
            lines = [str(x) for x in (b.get("lines") or ["卖铲子的人", "先发财"])][:2]
            c.update(lines=lines, at_rain=T("at_rain", t + 0.1), at_title=T("at_title", t + 0.9), at_line2=T("at_line2", None))
            text3d.update("".join(lines))
        elif k == "outro":
            c.update(title=str(b.get("title", X.channel))); text3d.update(c["title"])
        cfg["beats"].append(c)
    marked = [i for i, b in enumerate(beats) if b.get("flash")]
    if not marked:
        marked = [i for i, c in enumerate(cfg["beats"]) if (c["kind"] == "hero" and c.get("deco") == "blob") or c["kind"] in ("moat", "outro")]
    for i in marked[:3]:
        c = cfg["beats"][i]
        c["flash"] = {"hero": c.get("at"), "multiple": c.get("at"), "moat": (c.get("at_word") or c["t"]) + 0.1, "outro": c["t"] + 0.75}.get(c["kind"], c["t"] + 0.1)

    # 3D glyphs: CJK from the heavy CJK face, Latin / digits from Archivo at 125 width / 900 weight
    f3 = {**STYLE["font3d"], **X.S.get("font3d", {})}
    txt = "".join(sorted(text3d))
    gl = glyphs.outlines(fonts.find(fonts.REG[f3["cjk"]]["file"]), txt)
    gl.update(glyphs.outlines(fonts.find(fonts.REG[f3["latin"]]["file"]), txt, f3["latin_axes"]))
    js = (SKILL / "runtime" / "chrome3d.js").read_text()
    X.extra_head = ('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",'
                    '"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>')
    X.extra_body = ('<script>window.__hf=window.__hf||{};window.__hf.buildReady=window.__hf.buildReady||{};'
                    'window.__hf.buildReady.world=new Promise(r=>{window.__h9WorldReady=r;});'
                    f'window.__H9_CHROME={json.dumps(cfg, ensure_ascii=False)};window.__H9_GLYPHS={json.dumps(gl, separators=(",", ":"))};</script>'
                    f'<script type="module">{js}</script>')
    X.clip("world", 0, D, '<canvas id="w3d" width="%d" height="%d"></canvas>' % (W, H), "w3d-host", 1, track=2, attrs="data-motion-blur=\"off\"")
    if P: X.css("chr-cap", "#root.v { --cap-bottom:520px; --cap-size:46px; }")

    # ---------------- layout (px) per aspect: frame furniture, kicker, source, the subject band the runtime frames into
    L = ({"tag": (60, 212), "tc": (60, 216), "tick": 262, "kk": (60, 318), "kkw": 960, "kzh": 68, "src": (60, 436), "srcw": 900, "cy": 860}
         if P else {"tag": (70, 44), "tc": (70, 48), "tick": 94, "kk": (70, 150), "kkw": 900, "kzh": 60, "src": (70, 132), "srcw": 1180, "cy": 510})

    # ---------------- persistent HUD
    tag = meta.get("tag", "")
    ticker = meta.get("ticker") or []
    hud = (f'<i class="cn tl"></i><i class="cn tr"></i><i class="cn bl"></i><i class="cn br"></i>'
           f'<div class="tag" style="left:{L["tag"][0]}px;top:{L["tag"][1]}px"><b>{X.rich(X.channel)}</b><span>{X.rich(tag)}</span></div>'
           f'<div class="tc" style="right:{L["tc"][0]}px;top:{L["tc"][1]}px"><i></i><span class="tcv">00:00:00</span></div>')
    if ticker:
        unit = "".join(f"{X.rich(s)}<b>✦</b>" for s in ticker)
        est = sum(fit.width(s, mono=True) * 15 * 1.18 + 15 * 3 for s in ticker) or 400
        speed = 70
        rep = int(math.ceil((W + speed * D) / est)) + 1
        hud += f'<div class="tick" style="top:{L["tick"]}px"><div class="tk">{unit * rep}</div></div>'
    X.clip("hud", 0, D, hud, "c-ov", 8, track=5, attrs="data-layout-ignore")
    X.tw(f'(()=>{{const o={{v:0}};const el=document.querySelector("#hud .tcv");tl.to(o,{{v:{D:.3f},duration:{D:.3f},ease:"none",onUpdate:()=>{{const s=Math.floor(o.v),f=Math.floor((o.v-s)*30);el.textContent="00:"+String(s).padStart(2,"0")+":"+String(f).padStart(2,"0");}}}},0);}})();')
    if ticker: X.tw(f'tl.fromTo("#hud .tk",{{x:0}},{{x:{-speed * D:.0f},duration:{D:.3f},ease:"none"}},0);')
    for k2 in range(int(D / 0.5)):           # REC dot blinks
        X.tw(f'tl.set("#hud .tc i",{{opacity:{1 if k2 % 2 == 0 else 0.15}}},{k2 * 0.5:.2f});')
    X.enter("#hud .cn", 0.0, "accent", verb="pop", dur=0.4, stagger=0.05)
    X.enter("#hud .tag", 0.1, "text", verb="fade", dur=0.4)

    # ---------------- per beat overlays
    real = [c for c in cfg["beats"] if c["kind"] != "outro"]
    for i, (b, c) in enumerate(zip(beats, cfg["beats"])):
        t, d, k = c["t"], c["d"], c["kind"]
        if i: X.sfx(t - 0.56, "fly")      # the flight runs t-0.53 → t-0.08, inside the narration pause
        if i:   # whip streaks over the camera flight, travelling against the camera's sideways move
            dx = math.sin(i * 1.7) - math.sin((i - 1) * 1.7)
            sgn = -1 if dx > 0 else 1
            lines = []
            for k2 in range(14):
                y = X.rand.uniform(0.12, 0.86) * H; w = X.rand.uniform(0.18, 0.42) * W; hh = X.rand.choice([1, 2, 2, 3])
                lines.append(f'<i class="{"p" if k2 % 5 == 0 else ""}" style="top:{y:.0f}px;width:{w:.0f}px;height:{hh}px;{"transform:scaleX(-1);" if sgn < 0 else ""}"></i>')
            X.clip(f"sw{i}", t - 0.56, 0.56, f'<div class="whip">{"".join(lines)}</div>', "c-ov", 9, track=6 + i % 2, attrs="data-layout-ignore")
            a0, a1 = (-0.45 * W, 1.1 * W) if sgn > 0 else (1.1 * W, -0.45 * W)
            X.tw(f'tl.fromTo("#sw{i} .whip i",{{x:{a0:.0f},opacity:0}},{{x:{a1:.0f},opacity:1,duration:0.38,ease:"power2.inOut",stagger:{{each:0.01,from:"random"}}}},{t - 0.53:.3f});')
            X.tw(f'tl.to("#sw{i} .whip",{{opacity:0,duration:0.1}},{t - 0.12:.3f});')
        if k != "outro" and (b.get("k") or b.get("kz")):
            idx = f"{real.index(c) + 1:02d}/{len(real):02d}"
            ft = fit.fit_text(b.get("kz", ""), L["kkw"], L["kzh"], L["kzh"] * 0.92, 26, max_lines=1)
            html = (f'<div class="kk" style="left:{L["kk"][0]}px;top:{L["kk"][1]}px"><div class="ke" data-layout-ignore><b>{idx}</b>{X.rich(b.get("k", ""), split="chars")}</div>'
                    f'<div class="kz" style="font-size:{ft.px}px">{X.rich(ft.lines[0] if ft.lines else "")}</div><div class="kb"></div></div>')
            ka = t - 0.08 if i else t       # the kicker lands with the camera
            X.clip(f"kk{i}", ka, d, html, "c-ov", 7, track=3 + i % 2)
            X.enter(f"#kk{i} .ke .c", ka + 0.04, "text", verb="type", stagger=min(0.025, 0.6 / max(1, len(str(b.get("k", ""))))))
            X.tw(f'tl.from("#kk{i} .kz",{{x:-40,opacity:0,filter:"blur(8px)",duration:0.45,ease:"expo.out"}},{ka + 0.08:.3f});')
            X.tw(f'tl.fromTo("#kk{i} .kb",{{scaleX:0}},{{scaleX:1,duration:0.5,ease:"expo.out"}},{ka + 0.14:.3f});')
            X.tw(f'tl.to("#kk{i}",{{opacity:0,x:-24,duration:0.2,ease:"power2.in"}},{t + d - 0.66:.3f});')
        if b.get("src"):
            fs = fit.fit_text(b["src"], L["srcw"], 56, 18 if not P else 19, 13, max_lines=2, mono=True)
            X.clip(f"src{i}", t, d, f'<div class="src" data-layout-ignore style="left:{L["src"][0]}px;bottom:{L["src"][1]}px;font-size:{fs.px}px;max-width:{L["srcw"]}px"><b>SRC</b>{"<br>".join(X.rich(s) for s in fs.lines)}</div>', "c-ov", 7, track=9 + i % 2)
            X.tw(f'tl.from("#src{i} .src",{{opacity:0,y:10,duration:0.4,ease:"expo.out"}},{t + 0.5:.3f});')
        n_els = len(X.els)
        _extras(X, b, c, i, L, P, W, H, fit)
        # this beat's chips, stickers, panels and source leave before the camera whips away
        ids = [e.split('id="', 1)[1].split('"', 1)[0] for e in X.els[n_els:]] + ([f"src{i}"] if b.get("src") else [])
        if ids and i + 1 < len(beats):
            X.tw(f'tl.to([{",".join(f"{chr(34)}#{x}{chr(34)}" for x in ids)}],{{opacity:0,duration:0.22,ease:"power2.in"}},{t + d - 0.68:.3f});')

    # outro: the mascot cameo is placed by build.py; sound for the hat + name
    for c in cfg["beats"]:
        if c["kind"] == "outro": X.sfx(c["t"] + 0.15, "boom"); X.sfx(c["t"] + 0.75, "slam")


def _extras(X, b, c, i, L, P, W, H, fit):
    t, d, k = c["t"], c["d"], c["kind"]
    cy = L["cy"]
    if k == "hero":
        X.sfx(c["at"], "slam"); X.sfx(t + 0.05, "riser" if i == 0 else "enter")
        if b.get("chip"):
            ft = fit.fit_text(b["chip"], W * 0.7, 60, 36 if not P else 40, 22, max_lines=1)
            top = cy + (190 if not P else 250)
            X.clip(f"chip{i}", t, d, f'<div class="chip" style="left:0;right:0;top:{top}px"><span style="font-size:{ft.px}px">{X.rich(ft.lines[0])}</span></div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#chip{i} span",{{scale:0.6,opacity:0,duration:0.45,ease:"back.out(2.4)"}},{c["at"] + 0.15:.3f});')
        if b.get("sticker"):
            st = b["sticker"] if isinstance(b["sticker"], list) else [b["sticker"]]
            sz = 250 if not P else 270
            x, y = (W * 0.74, cy - 330) if not P else (W - sz - 70, cy - 470)
            at = X.T(b.get("at_sticker"), t) if b.get("at_sticker") else c["at"] - 0.6
            f1 = fit.fit_text(st[0], sz * 0.62, sz * 0.26, sz * 0.2, 18, max_lines=1)
            sub = f'<i data-layout-ignore style="font-size:{max(16, int(sz * 0.075))}px">{X.rich(st[1])}</i>' if len(st) > 1 else ""
            X.clip(f"bst{i}", t, d, f'<div class="burst" style="left:{x:.0f}px;top:{y:.0f}px;width:{sz}px;height:{sz}px">{_burst_svg()}<div class="bt"><b style="font-size:{f1.px}px">{X.rich(f1.lines[0])}</b>{sub}</div></div>', "c-ov", 7, track=12)
            X.tw(f'tl.from("#bst{i} .burst",{{scale:0,rotation:-140,duration:0.6,ease:"back.out(2)"}},{at:.3f});')
            X.tw(f'tl.to("#bst{i} .burst svg",{{rotation:60,duration:{max(1.0, t + d - at):.2f},ease:"none"}},{at:.3f});')
            X.sfx(at, "pop")
        if b.get("date"):
            x, y = (L["kk"][0], cy + 250) if not P else (L["kk"][0], cy + 300)
            X.clip(f"dt{i}", t, d, f'<div class="date" style="left:{x}px;top:{y}px;font-size:{18 if not P else 20}px"><b>●</b>{X.rich(b["date"], split="chars")}</div>', "c-ov", 7, track=13)
            X.enter(f"#dt{i} .c", t + 0.35, "text", verb="type", stagger=0.04)
            X.tw(f'tl.from("#dt{i} .date",{{opacity:0,duration:0.2}},{t + 0.3:.3f});')
    elif k == "bars":
        X.sfx(c["at"], "enter")
        for j in range(len(c["items"]) - 1): X.sfx(min(c["at"], t - 0.48) + 0.1 + j * 0.16, "tick")
        X.sfx(c["at_v"], "slam")
        if b.get("pill"):
            ft = fit.fit_text(b["pill"], 420, 50, 34, 20, max_lines=1)
            x, y = (L["kk"][0], L["kk"][1] + 128) if not P else (L["kk"][0], L["kk"][1] + 130)
            X.clip(f"pl{i}", t, d, f'<div class="pill" style="left:{x}px;top:{y}px;font-size:{ft.px}px">{X.rich(ft.lines[0])}</div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#pl{i} .pill",{{scale:0,rotation:-12,duration:0.45,ease:"back.out(2.6)"}},{c["at_v"] + 0.9:.3f});')
            X.sfx(c["at_v"] + 0.9, "pop")
    elif k == "multiple":
        X.sfx(t + 0.05, "enter"); X.sfx(c["at"], "boom")
        if b.get("eq"):
            ft = fit.fit_text(b["eq"], W * 0.8, 50, 30 if not P else 32, 16, max_lines=1, mono=True)
            top = cy + (200 if not P else 260)
            X.clip(f"eq{i}", t, d, f'<div class="eq" style="left:0;right:0;top:{top}px;font-size:{ft.px}px">{X.rich(ft.lines[0], split="chars")}</div>', "c-ov", 7, track=11)
            X.enter(f"#eq{i} .c", t + 0.25, "text", verb="type", stagger=0.02)
    elif k == "coins":
        X.sfx(c["at_show"], "shutter"); X.sfx(c["at_hit"], "pop"); X.sfx(c["at_hit"] + 0.5, "tick")
        lg = b.get("legend")
        if lg:
            fs = 26 if not P else 30
            x0, top = ((W * 0.5 + 0.27 * W * 0.84) - 230, cy + 170) if not P else (None, cy + 350)
            pos = f"left:{x0:.0f}px;top:{top}px" if not P else f"left:0;right:0;justify-content:center;top:{top}px"
            X.clip(f"lg{i}", t, d, f'<div class="lg" style="{pos};font-size:{fs}px"><span class="a"><i></i>{X.rich(lg[0])}</span><span class="b"><i></i>{X.rich(lg[1])}</span></div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#lg{i} span",{{opacity:0,y:14,duration:0.4,stagger:0.12,ease:"expo.out"}},{c["at_hit"] + 0.6:.3f});')
    elif k == "moat":
        X.sfx(t + 0.2, "enter"); X.sfx(c["at_moat"], "riser"); X.sfx(c["at_chip"] + 0.05, "glitch"); X.sfx(c["at_word"] + 0.1, "slam")
    elif k == "swarm":
        X.sfx(t + 0.05, "riser"); X.sfx(c["at"], "hit")
        code = b.get("code") or [
            ("c", "// kernel.cu"), ("k", "__global__ void scale(float *x, float a, int n) {"),
            ("", "  int i = blockIdx.x * blockDim.x + threadIdx.x;"), ("", "  if (i < n) x[i] *= a;"), ("", "}"),
            ("k", "scale<<<blocks, 256>>>(d_x, 2.0f, n);"), ("", "cudaDeviceSynchronize();")]
        if P: box = (60, cy + 190, 960, 252, 18)
        else: box = (70, cy - 140, 640, 360, 18)
        x, y, w, h, fs = box
        total = int(b.get("count", 0))
        lines = "".join(f'<span class="l {cls}">{X.rich(s)}</span>' for cls, s in code)
        X.clip(f"cd{i}", t, d, f'<div class="code" style="left:{x}px;top:{y:.0f}px;width:{w}px;height:{h}px"><div class="hd" data-layout-ignore style="font-size:{fs - 3}px">'
                               f'<span>{X.rich(b.get("label", "DEVELOPERS"))}</span><span class="n" style="font-size:{fs + 8}px">0</span></div>'
                               f'<div class="bd" data-layout-ignore style="font-size:{fs}px">{lines}<span class="cur"></span></div></div>', "c-ov", 7, track=11)
        X.tw(f'tl.from("#cd{i} .code",{{clipPath:"inset(0 100% 0 0)",duration:0.5,ease:"expo.inOut"}},{t + 0.15:.3f});')
        atc = X.T(b.get("at_code"), t) if b.get("at_code") else t + 1.2
        X.tw(f'tl.from("#cd{i} .bd .l",{{opacity:0,x:-12,duration:0.25,stagger:0.12,ease:"power2.out"}},{min(atc, t + 0.5):.3f});')
        if total:
            X.tw(f'(()=>{{const o={{v:0}};const el=document.querySelector("#cd{i} .hd .n");tl.to(o,{{v:{total},duration:1.3,ease:"power3.out",onUpdate:()=>{{el.textContent=Math.round(o.v).toLocaleString("en-US");}}}},{c["at"] - 0.6:.3f});}})();')
        for k2 in range(int(d / 0.4)):
            X.tw(f'tl.set("#cd{i} .cur",{{opacity:{1 if k2 % 2 == 0 else 0}}},{t + k2 * 0.4:.2f});')
        X.sfx(atc, "type")
    elif k == "shovel":
        X.sfx(c["at_rain"] + 0.4, "tick"); X.sfx(c["at_title"], "slam")
        if c.get("at_line2"): X.sfx(c["at_line2"], "hit")
