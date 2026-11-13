"""chrome3d · Y2K 镀铬 3D —— 液态镀铬立体字站在明亮影棚里：浅灰蓝天空一路暖到地平线上一道热橙色光带，下面是一整片深紫镜面地板，
每个物体都在地板上有倒影。真正从字体轮廓挤出的三维字（拉丁用 Archivo 超宽特粗，中文用阿里巴巴普惠体 Heavy），程序生成的影棚
HDRI（天空 + 橙色地平线 + 紫色地面 + 三根灯条）让镀铬反射出颜色，镜头一动灯条高光就在字面上滑过。只有一个热粉色，只给闪光。
适合：科技 / 潮流 / 增长数字 / 产品发布 / 年轻向的开场。与 studio（金色 PBR 影棚）和 clay（黏土）完全不同：没有布景，只有天空、
地平线和镜面地板，主体是铺满画幅的镀铬大字。

这个风格不走逐句场景：WORLD() 一次性搭好整条片子（runtime/chrome3d.js），每个 beat 是一个展台：
  hero    一个大数字 / 短词（deco: ring | blob；可选 chip、sticker、date、at_enter 推迟数字入场）
  bars    3–6 根立在地板上的镀铬柱，最后一根生长时顶上的大数字计数     items: [[标签, 数值], …]
  multiple 倍数冲屏 + 冲击环 + 速度线                                  value: "12.9×"
  coins   N 枚镀铬圆片翻面，hit 枚翻成全息面                            n, hit, value: "75%"
  moat    芯片落在地板上 → 护城河环 → 打叉沉入地板 → 新词从环里升起    chip, word
  swarm   数字 + 成百上千颗环绕的小球 + 代码面板                        value, count
  shovel  插在镀铬金块堆里的铲子 + 两行立体字                           lines: [第一行, 第二行]
  outro   落在地板上的镀铬礼帽 + 名字
镜头低机位、略仰、FOV 40（横屏 36），主体在画面 45% 高处，地平线在 70%，每个 beat 绕主体转 25–32°；物体落地有一次小回弹。
换站是穿过环形门的甩镜；全屏闪白只给最多 3 个揭晓点（beat 上写 "flash": true，默认：blob 数字、moat 新词、outro）。
字幕是磨砂镀铬胶囊里的藏青字，放在地板上；标签和来源是天空上的藏青字。不出主持人贴纸。
"""
import json, math
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PINK = "#ff3d7f"      # glints only
NAVY = "#151538"

STYLE = {
    "name": "Y2K 镀铬 3D", "en": "Y2K Chrome 3D", "benchmarks": ["Behance chrome type", "MV 包装 (Y2K revival)", "Nike / Apple Music 潮流海报", "Acid graphics"],
    "tokens": {      # accent here is the deep shade for any UI text; the runtime's glints use PINK
        "bg": "#dfe6f2", "fg": NAVY, "muted": "#4a4a72", "accent": "#d81b60", "accent2": "#ff8a3c", "alert": "#d81b60",
        "line": "#b8bdd2", "paper": "#dfe6f2", "ink": NAVY, "card": "#ffffff", "card-fg": NAVY,
        "cap-fg": NAVY, "cap-size": "40px", "cap-weight": "800", "cap-em": "#b0124f",
        "cap-bg": "linear-gradient(180deg,rgba(255,255,255,.86) 0%,rgba(232,235,245,.72) 46%,rgba(206,211,228,.7) 54%,rgba(255,255,255,.8) 100%)",
        "cap-pad": ".3em .9em .32em", "cap-radius": "999px", "cap-shadow": "none",
    },
    "fonts": {"display": ["archivo", "smiley-sans"], "zh": ["smiley-sans", "noto-sans-sc"], "body": ["alibaba-puhuiti", "noto-sans-sc"],
              "mono": ["space-mono", "noto-sans-sc"]},
    "font3d": {"latin": "archivo", "latin_axes": {"wght": 900, "wdth": 125}, "cjk": "alibaba-puhuiti-heavy"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.03, "heading": "blurin", "text": "blurin", "camera": "none", "cut": "hard", "transition": "dip", "em": "color"},
    "caption_mode": "reading",
    "layers": [("grain", {"opacity": 0.06})],
    "motion_blur": False,
    # the flat cartoon host does not belong in this world: chrome3d hides it (see css)
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"left": 56, "bottom": 30, "h": 250}, "portrait": {"left": 40, "bottom": 600, "h": 280}},
    "sfx": {"fly": ("whoosh", 0.28), "transition": ("whoosh", 0.28), "slam": ("slam", 0.42), "boom": ("boom", 0.42), "pop": ("pop", 0.32),
            "glitch": ("glitch", 0.3), "hit": ("hit", 0.38), "tick": ("tick", 0.22), "riser": ("riser", 0.22), "type": ("type", 0.16),
            "shutter": ("shutter", 0.28), "mascot": ("whoosh_soft", 0.22), "enter": ("whoosh_soft", 0.22), "title": ("slam", 0.42)},
}

STYLE["css"] = """
#w3d { position:absolute; inset:0; width:100%; height:100%; display:block; }
.st-chrome3d { background:#dfe6f2; }
.st-chrome3d .mascot { display:none !important; }
.st-chrome3d .c-ov { position:absolute; inset:0; pointer-events:none; }
.st-chrome3d .mono { font-family:var(--f-mono); }
/* caption: navy type on a frosted chrome pill, standing on the mirror floor */
.st-chrome3d .cap .cp { -webkit-backdrop-filter:blur(14px) saturate(1.3); backdrop-filter:blur(14px) saturate(1.3); line-height:1.25;
  border:1.5px solid rgba(255,255,255,.95); box-shadow:inset 0 2px 0 rgba(255,255,255,.9), inset 0 -2px 0 rgba(150,156,190,.55), 0 10px 28px rgba(21,21,56,.32); }
/* per-beat kicker: index chip + English line + Chinese headline, navy on the sky */
.st-chrome3d .kk { position:absolute; }
.st-chrome3d .kk .ke { font-family:var(--f-mono); font-size:30px; letter-spacing:.1em; color:#151538; white-space:nowrap; display:flex; align-items:center; gap:.6em; }
.st-chrome3d .kk .ke b { font-weight:700; color:#fff; background:#151538; border-radius:999px; padding:.04em .6em; letter-spacing:.06em; }
.st-chrome3d .kk .kz { font-family:var(--f-zh); color:#151538; line-height:1.1; margin-top:10px; white-space:nowrap; }
.st-chrome3d .kk.c { left:0; right:0; text-align:center; } .st-chrome3d .kk.c .ke { justify-content:center; }
.st-chrome3d .src { position:absolute; font-family:var(--f-mono); color:#151538; letter-spacing:.02em; line-height:1.3; }
.st-chrome3d .src b { font-weight:700; margin-right:.6em; letter-spacing:.14em; }
/* chips, stickers, panels: navy / white / frosted, never neon */
.st-chrome3d .chip { position:absolute; display:flex; justify-content:center; }
.st-chrome3d .chip span { font-family:var(--f-body); font-weight:800; color:#fff; background:#151538; border-radius:999px; padding:.14em .85em .18em;
  box-shadow:inset 0 2px 0 rgba(255,255,255,.25), 0 8px 22px rgba(21,21,56,.3); white-space:nowrap; }
.st-chrome3d .pill { position:absolute; font-family:var(--f-display); font-variation-settings:"wdth" 125, "wght" 900; color:#fff; background:#151538;
  padding:.12em .6em; border-radius:999px; white-space:nowrap; box-shadow:0 8px 22px rgba(21,21,56,.3); }
.st-chrome3d .burst { position:absolute; display:grid; place-items:center; }
.st-chrome3d .burst svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; filter:drop-shadow(0 10px 18px rgba(21,21,56,.35)); }
.st-chrome3d .burst .bt { position:relative; text-align:center; color:#fff; line-height:1.05; }
.st-chrome3d .burst .bt b { display:block; font-family:var(--f-zh); font-weight:400; }
.st-chrome3d .burst .bt i { display:block; font-style:normal; font-family:var(--f-mono); letter-spacing:.12em; margin-top:.25em; }
.st-chrome3d .date { position:absolute; font-family:var(--f-mono); color:#151538; letter-spacing:.14em; border:2px solid #151538; padding:.25em .7em; background:rgba(255,255,255,.55); white-space:nowrap; border-radius:6px; }
.st-chrome3d .eq { position:absolute; text-align:center; font-family:var(--f-mono); color:#151538; letter-spacing:.08em; white-space:nowrap; font-weight:700; }
.st-chrome3d .lg { position:absolute; display:flex; gap:34px; font-family:var(--f-body); font-weight:800; color:#151538; white-space:nowrap; }
.st-chrome3d .lg span { display:flex; align-items:center; gap:12px; }
.st-chrome3d .lg i { width:.8em; height:.8em; border-radius:50%; display:block; }
.st-chrome3d .lg .a i { background:linear-gradient(135deg,#ffb0cb,#ff3d7f 50%,#ff8a3c); }
.st-chrome3d .lg .b i { background:linear-gradient(135deg,#fff,#8d90a6); border:1.5px solid #151538; }
/* code panel: a frosted chrome window on the sky */
.st-chrome3d .code { position:absolute; border:1.5px solid rgba(255,255,255,.95); border-radius:22px; overflow:hidden;
  background:linear-gradient(180deg,rgba(255,255,255,.8),rgba(228,232,244,.7)); -webkit-backdrop-filter:blur(12px); backdrop-filter:blur(12px);
  box-shadow:inset 0 2px 0 #fff, 0 14px 34px rgba(21,21,56,.28); }
.st-chrome3d .code .hd { display:flex; justify-content:space-between; align-items:center; padding:12px 22px; border-bottom:1.5px solid rgba(21,21,56,.18); font-family:var(--f-mono); color:#151538; letter-spacing:.1em; }
.st-chrome3d .code .hd .n { color:#151538; font-family:var(--f-display); font-variation-settings:"wdth" 125, "wght" 900; letter-spacing:.02em; }
.st-chrome3d .code .bd { padding:12px 22px; font-family:var(--f-mono); color:#151538; white-space:pre; line-height:1.36; }
.st-chrome3d .code .bd .l { display:block; } .st-chrome3d .code .bd .k { font-weight:700; } .st-chrome3d .code .bd .c { color:#55557a; }
.st-chrome3d .code .bd .cur { display:inline-block; width:.6em; height:1.1em; background:#151538; vertical-align:-.2em; }
/* whip streaks over each camera flight: thin navy motion lines on the bright sky */
.st-chrome3d .whip i { position:absolute; left:0; display:block; border-radius:2px;
  background:linear-gradient(90deg, rgba(21,21,56,0), rgba(21,21,56,.45) 60%, rgba(21,21,56,0)); }
.st-chrome3d .whip i.p { background:linear-gradient(90deg, rgba(255,61,127,0), rgba(255,61,127,.8) 60%, rgba(255,61,127,0)); }
#root.v .cap .cp { max-width:860px; }
"""

def _burst_svg(n=16, r0=0.78, r1=1.0):
    pts = []
    for k in range(n * 2):
        a = math.pi * k / n - math.pi / 2
        r = r1 if k % 2 == 0 else r0
        pts.append(f"{50 + 50 * r * math.cos(a):.1f},{50 + 50 * r * math.sin(a):.1f}")
    return f'<svg viewBox="0 0 100 100"><polygon points="{" ".join(pts)}" fill="{NAVY}"/><polygon points="{" ".join(pts)}" fill="none" stroke="#fff" stroke-width="1.2" transform="translate(50 50) scale(.9) translate(-50 -50)"/></svg>'


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
    # the caption stands on the mirror floor (horizon at 70 % of the frame)
    X.css("chr-cap", "#root.v { --cap-bottom:430px; } #root.h { --cap-bottom:104px; }")

    # ---------------- layout (px) per aspect. 9:16: kicker centred on the sky, source printed just above the horizon line
    # (hero beats) or under the kicker; 16:9: kicker top-left, source top-right. cy = the subject centre the runtime frames.
    hor = round(H * 0.70)
    L = ({"kk": (0, 204), "kzh": 68, "kkw": 980, "src_top": 350, "src_bot": H - hor + 18, "srcw": 960, "cy": round(H * 0.45)}   # 9:16: kicker under the top tabs
         if P else {"kk": (70, 40), "kzh": 56, "kkw": 900, "src_top": 44, "srcw": 700, "cy": round(H * 0.45)})

    # ---------------- per beat overlays
    real = [c for c in cfg["beats"] if c["kind"] != "outro"]
    for i, (b, c) in enumerate(zip(beats, cfg["beats"])):
        t, d, k = c["t"], c["d"], c["kind"]
        late = 0.55 if k == "outro" else 0.0     # runtime LATE: the outro station arrives after its line starts
        if i: X.sfx(t - 0.56 + late, "fly")      # the flight runs t-0.53 → t-0.08, inside the narration pause
        if i:   # whip streaks over the camera flight, travelling against the camera's sideways move
            dx = math.sin(i * 1.7) - math.sin((i - 1) * 1.7)
            sgn = -1 if dx > 0 else 1
            lines = []
            for k2 in range(14):
                y = X.rand.uniform(0.12, 0.66) * H; w = X.rand.uniform(0.18, 0.42) * W; hh = X.rand.choice([2, 2, 3, 4])
                lines.append(f'<i class="{"p" if k2 % 6 == 0 else ""}" style="top:{y:.0f}px;width:{w:.0f}px;height:{hh}px;{"transform:scaleX(-1);" if sgn < 0 else ""}"></i>')
            X.clip(f"sw{i}", t - 0.56 + late, 0.56, f'<div class="whip">{"".join(lines)}</div>', "c-ov", 9, track=6 + i % 2, attrs="data-layout-ignore")
            a0, a1 = (-0.45 * W, 1.1 * W) if sgn > 0 else (1.1 * W, -0.45 * W)
            X.tw(f'tl.fromTo("#sw{i} .whip i",{{x:{a0:.0f},opacity:0}},{{x:{a1:.0f},opacity:1,duration:0.38,ease:"power2.inOut",stagger:{{each:0.01,from:"random"}}}},{t - 0.53 + late:.3f});')
            X.tw(f'tl.to("#sw{i} .whip",{{opacity:0,duration:0.1}},{t - 0.12 + late:.3f});')
        if k != "outro" and (b.get("k") or b.get("kz")):
            idx = f"{real.index(c) + 1:02d}/{len(real):02d}"
            ft = fit.fit_text(b.get("kz", ""), L["kkw"], L["kzh"], L["kzh"] * 0.92, 40, max_lines=1)
            cls = "kk c" if P else "kk"
            pos = f"top:{L['kk'][1]}px" if P else f"left:{L['kk'][0]}px;top:{L['kk'][1]}px"
            html = (f'<div class="{cls}" style="{pos}"><div class="ke"><b>{idx}</b><span>{X.rich(b.get("k", ""), split="chars")}</span></div>'
                    f'<div class="kz" style="font-size:{ft.px}px">{X.rich(ft.lines[0] if ft.lines else "")}</div></div>')
            ka = t - 0.08 if i else t       # the kicker lands with the camera
            X.clip(f"kk{i}", ka, d, html, "c-ov", 7, track=3 + i % 2)
            X.enter(f"#kk{i} .ke .c", ka + 0.06, "text", verb="type", stagger=min(0.025, 0.6 / max(1, len(str(b.get("k", ""))))))
            X.tw(f'tl.from("#kk{i} .ke b",{{scale:0,duration:0.35,ease:"back.out(1.6)"}},{ka:.3f});')
            X.tw(f'tl.from("#kk{i} .kz",{{y:-36,opacity:0,duration:0.42,ease:"back.out(1.4)"}},{ka + 0.08:.3f});')
            X.tw(f'tl.to("#kk{i}",{{opacity:0,y:-20,duration:0.2,ease:"power2.in"}},{t + d - 0.66:.3f});')
        if b.get("src"):
            fs = fit.fit_text(b["src"], L["srcw"] - 110, 110 if P else 100, 30 if P else 26, 28 if P else 24, max_lines=3 if not P else 2, mono=True)
            body = f'<b>SRC</b>{"<br>".join(X.rich(s) for s in fs.lines)}'
            if P and k == "hero":
                pos = f"left:0;right:0;text-align:center;bottom:{L['src_bot']}px"
            elif P:
                pos = f"left:0;right:0;text-align:center;top:{L['src_top']}px"
            else:
                pos = f"right:70px;top:{L['src_top']}px;text-align:right;max-width:{L['srcw']}px"
            X.clip(f"src{i}", t, d, f'<div class="src" data-layout-ignore style="{pos};font-size:{fs.px}px">{body}</div>', "c-ov", 7, track=9 + i % 2)
            X.tw(f'tl.from("#src{i} .src",{{opacity:0,y:10,duration:0.4,ease:"expo.out"}},{t + 0.5:.3f});')
        n_els = len(X.els)
        _extras(X, b, c, i, L, P, W, H, fit)
        # this beat's chips, stickers, panels and source leave before the camera whips away
        ids = [e.split('id="', 1)[1].split('"', 1)[0] for e in X.els[n_els:]] + ([f"src{i}"] if b.get("src") else [])
        if ids and i + 1 < len(beats):
            nl = 0.55 if cfg["beats"][i + 1]["kind"] == "outro" else 0.0
            X.tw(f'tl.to([{",".join(f"{chr(34)}#{x}{chr(34)}" for x in ids)}],{{opacity:0,duration:0.22,ease:"power2.in"}},{t + d - 0.68 + nl:.3f});')

    for c in cfg["beats"]:
        if c["kind"] == "outro": X.sfx(c["t"] + 0.15, "boom"); X.sfx(c["t"] + 0.75, "slam")


def _extras(X, b, c, i, L, P, W, H, fit):
    t, d, k = c["t"], c["d"], c["kind"]
    cy = L["cy"]
    if k == "hero":
        X.sfx(c["at"], "slam"); X.sfx(t + 0.05, "riser" if i == 0 else "enter")
        if b.get("chip"):
            ft = fit.fit_text(b["chip"], W * 0.7, 60, 40 if P else 36, 30, max_lines=1)
            top = cy + (216 if P else 190)
            X.clip(f"chip{i}", t, d, f'<div class="chip" style="left:0;right:0;top:{top}px"><span style="font-size:{ft.px}px">{X.rich(ft.lines[0])}</span></div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#chip{i} span",{{scale:0.6,opacity:0,duration:0.42,ease:"back.out(1.8)"}},{c["at"] + 0.15:.3f});')
        if b.get("sticker"):
            st = b["sticker"] if isinstance(b["sticker"], list) else [b["sticker"]]
            sz = 270 if P else 240
            x, y = (W - sz - 44, cy - 560) if P else (W * 0.75, cy - 330)
            at = X.T(b.get("at_sticker"), t) if b.get("at_sticker") else c["at"] - 0.6
            f1 = fit.fit_text(st[0], sz * 0.62, sz * 0.26, sz * 0.2, 30, max_lines=1)
            sub = f'<i data-layout-ignore style="font-size:{max(28, int(sz * 0.1))}px">{X.rich(st[1])}</i>' if len(st) > 1 else ""
            X.clip(f"bst{i}", t, d, f'<div class="burst" style="left:{x:.0f}px;top:{y:.0f}px;width:{sz}px;height:{sz}px">{_burst_svg()}<div class="bt"><b style="font-size:{f1.px}px">{X.rich(f1.lines[0])}</b>{sub}</div></div>', "c-ov", 7, track=12)
            X.tw(f'tl.from("#bst{i} .burst",{{scale:0,rotation:-140,duration:0.55,ease:"back.out(1.7)"}},{at:.3f});')
            X.tw(f'tl.to("#bst{i} .burst svg",{{rotation:40,duration:{max(1.0, t + d - at):.2f},ease:"none"}},{at:.3f});')
            X.sfx(at, "pop")
        if b.get("date"):
            pos = f"left:50%;translate:-50% 0;top:{L['src_top']}px" if P else f"left:70px;top:{cy + 230}px"
            X.clip(f"dt{i}", t, d, f'<div class="date" style="{pos};font-size:30px">{X.rich(b["date"], split="chars")}</div>', "c-ov", 7, track=13)
            X.enter(f"#dt{i} .c", t + 0.35, "text", verb="type", stagger=0.04)
            X.tw(f'tl.from("#dt{i} .date",{{opacity:0,duration:0.2}},{t + 0.3:.3f});')
    elif k == "bars":
        X.sfx(c["at"], "enter")
        for j in range(len(c["items"]) - 1): X.sfx(min(c["at"], t - 0.48) + 0.1 + j * 0.16, "tick")
        X.sfx(c["at_v"], "slam")
        if b.get("pill"):
            ft = fit.fit_text(b["pill"], 460, 56, 40, 30, max_lines=1)
            pos = f"left:50%;top:{L['src_top'] + 112}px" if P else f"right:70px;top:{L['src_top'] + 130}px"
            X.clip(f"pl{i}", t, d, f'<div class="pill" style="{pos};font-size:{ft.px}px{";translate:-50% 0" if P else ""}">{X.rich(ft.lines[0])}</div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#pl{i} .pill",{{scale:0,rotation:-10,duration:0.42,ease:"back.out(1.8)"}},{c["at_v"] + 0.9:.3f});')
            X.sfx(c["at_v"] + 0.9, "pop")
    elif k == "multiple":
        X.sfx(t + 0.05, "enter"); X.sfx(c["at"], "boom")
        if b.get("eq"):
            ft = fit.fit_text(b["eq"], W * 0.8, 56, 38 if P else 34, 28, max_lines=1, mono=True)
            top = cy + (200 if P else 200)
            X.clip(f"eq{i}", t, d, f'<div class="eq" style="left:0;right:0;top:{top}px;font-size:{ft.px}px">{X.rich(ft.lines[0], split="chars")}</div>', "c-ov", 7, track=11)
            X.enter(f"#eq{i} .c", t + 0.25, "text", verb="type", stagger=0.02)
    elif k == "coins":
        X.sfx(c["at_show"], "shutter"); X.sfx(c["at_hit"], "pop"); X.sfx(c["at_hit"] + 0.5, "tick")
        lg = b.get("legend")
        if lg:
            fs = 34 if P else 30
            pos = f"left:0;right:0;justify-content:center;top:{L['src_top'] + 96}px" if P else f"left:{W * 0.5 + 0.25 * 0.0 + 340:.0f}px;top:{cy + 190}px"
            X.clip(f"lg{i}", t, d, f'<div class="lg" style="{pos};font-size:{fs}px"><span class="a"><i></i>{X.rich(lg[0])}</span><span class="b"><i></i>{X.rich(lg[1])}</span></div>', "c-ov", 7, track=11)
            X.tw(f'tl.from("#lg{i} span",{{opacity:0,y:14,duration:0.4,stagger:0.12,ease:"back.out(1.4)"}},{c["at_hit"] + 0.6:.3f});')
    elif k == "moat":
        X.sfx(t + 0.2, "enter"); X.sfx(c["at_moat"], "riser"); X.sfx(c["at_chip"] + 0.05, "glitch"); X.sfx(c["at_word"] + 0.1, "slam")
    elif k == "swarm":
        X.sfx(t + 0.05, "riser"); X.sfx(c["at"], "hit")
        code = b.get("code") or [
            ("c", "// kernel.cu"), ("k", "__global__ void scale(float *x, float a, int n) {"),
            ("", "  int i = blockIdx.x * blockDim.x + threadIdx.x;"), ("", "  if (i < n) x[i] *= a;"), ("", "}"),
            ("k", "scale<<<blocks, 256>>>(d_x, 2.0f, n);"), ("", "cudaDeviceSynchronize();")]
        if P: box = (40, round(H * 0.70) - 392, 920, 376, 28)      # 9:16: the counter ends clear of the right-hand buttons
        else: box = (60, 330, 780, 392, 22)
        x, y, w, h, fs = box
        total = int(b.get("count", 0))
        lines = "".join(f'<span class="l {cls}">{X.rich(s)}</span>' for cls, s in code)
        X.clip(f"cd{i}", t, d, f'<div class="code" style="left:{x}px;top:{y:.0f}px;width:{w}px;height:{h}px"><div class="hd" data-layout-ignore style="font-size:{fs + 2}px">'
                               f'<span>{X.rich(b.get("label", "DEVELOPERS"))}</span><span class="n" style="font-size:{fs + 12}px">0</span></div>'
                               f'<div class="bd" data-layout-ignore style="font-size:{fs}px">{lines}<span class="cur"></span></div></div>', "c-ov", 7, track=11)
        X.tw(f'tl.from("#cd{i} .code",{{clipPath:"inset(0 100% 0 0 round 22px)",duration:0.5,ease:"expo.inOut"}},{t + 0.15:.3f});')
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
