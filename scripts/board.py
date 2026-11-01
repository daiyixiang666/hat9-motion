#!/usr/bin/env python3
"""Aesthetic direction board: the same two moments typeset in several refined directions, as 1920×1080 stills.

  python3 scripts/board.py -> dist/board/<dir>_<n>.png  (+ jpg previews)
Stills are plain HTML screenshotted with the Chrome HyperFrames installed (toolkit/webshot.mjs).
"""
import os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
from h9 import fonts  # noqa: E402

OUT = SKILL / "dist" / "board"
IMG = SKILL / "examples" / "demo" / "assets" / "img"
WEBSHOT = Path(os.environ.get("H9_WEBSHOT", "webshot.mjs"))   # any "url → png" screenshot script


def ff(fid):
    meta = fonts.REG[fid]; p = fonts.find(meta["file"])
    return f"@font-face {{ font-family:'{fid}'; src:url('file://{p}'); font-weight:{meta.get('weight', '400')}; font-style:{meta.get('style', 'normal')}; }}"


def img(name): return f"file://{IMG / name}"


BASE = "* { margin:0; padding:0; box-sizing:border-box; } html, body { width:1920px; height:1080px; overflow:hidden; } body { position:relative; -webkit-font-smoothing:antialiased; font-kerning:normal; }"

D = {}

# ------------------------------------------------------------------ A · 纸上留白 (editorial, light)
D["paper"] = {
    "name": "纸上留白", "refs": "Kinfolk · Monocle · 三联生活周刊 · Pentagram 编辑设计",
    "palette": [("纸", "#EFEBE3"), ("墨", "#171614"), ("灰", "#8B857B"), ("线", "#CFC8BB"), ("朱", "#C8401F")],
    "type": "标题 思源宋体 600 · 西文 EB Garamond Italic · 标签 Inter 500 大写宽字距",
    "fonts": ["noto-serif-sc", "eb-garamond-italic", "inter", "eb-garamond"],
    "css": """
body { background:#EFEBE3; color:#171614; }
.fol { position:absolute; left:160px; right:160px; top:72px; display:flex; justify-content:space-between; font:500 18px/1 'inter'; letter-spacing:.2em; color:#8B857B; text-transform:uppercase; }
.rule { position:absolute; left:160px; right:160px; height:1px; background:#CFC8BB; } .r1 { top:112px; } .r2 { bottom:112px; }
.foot { position:absolute; left:160px; bottom:72px; font:500 17px/1 'inter'; letter-spacing:.16em; color:#8B857B; }
.no { position:absolute; right:160px; top:170px; font:400 220px/1 'eb-garamond'; color:#DAD3C6; }
.h { position:absolute; left:160px; top:330px; font:600 128px/1.2 'noto-serif-sc'; letter-spacing:.02em; }
.h b { font-weight:600; color:#C8401F; }
.en { position:absolute; left:164px; top:668px; font:italic 400 44px/1.3 'eb-garamond-italic'; color:#5E5950; }
.k { position:absolute; left:164px; top:270px; font:500 18px/1 'inter'; letter-spacing:.24em; color:#C8401F; }
.t2 { position:absolute; left:160px; top:170px; font:600 58px/1.3 'noto-serif-sc'; letter-spacing:.02em; }
.fig { position:absolute; top:300px; width:740px; } .fa { left:160px; } .fb { right:160px; }
.fig img { width:740px; height:493px; object-fit:cover; display:block; }
.cap { margin-top:22px; display:flex; justify-content:space-between; align-items:baseline; border-top:1px solid #171614; padding-top:14px; }
.cap .l { font:600 30px/1 'noto-serif-sc'; } .cap .l i { font:italic 400 30px 'eb-garamond-italic'; color:#8B857B; margin-right:14px; }
.cap .v { font:500 17px/1 'inter'; letter-spacing:.2em; text-transform:uppercase; }
.fa .v { color:#C8401F; } .fb .v { color:#8B857B; } .fb img { filter:grayscale(1) contrast(.9) brightness(1.05); opacity:.55; }
""",
    "s1": """<div class="fol"><span>第九顶帽子 — 判断力</span><span>No. 01</span></div><i class="rule r1"></i><i class="rule r2"></i>
<div class="no">02</div><div class="k">THE SECOND THING</div><div class="h">差别不在工具，<br>在<b>判断</b>。</div>
<div class="en">It was never the tool. It is the judgement.</div><div class="foot">第九顶帽子 · 大家都在用 AI，结果凭什么是你的</div>""",
    "s2": """<div class="fol"><span>第九顶帽子 — 判断力</span><span>No. 01</span></div><i class="rule r1"></i><i class="rule r2"></i>
<div class="t2">同一个模型，同样的提示词。</div>
<div class="fig fa"><img src="{a}"><div class="cap"><span class="l"><i>A</i>像杂志</span><span class="v">Keep</span></div></div>
<div class="fig fb"><img src="{b}"><div class="cap"><span class="l"><i>B</i>像地摊海报</span><span class="v">Discard</span></div></div>
<div class="foot">图像均为同一模型、同一提示词生成</div>""",
}

# ------------------------------------------------------------------ B · 墨绿夜读 (dark literary)
D["night"] = {
    "name": "墨绿夜读", "refs": "Aesop · A24 片头字卡 · 看理想 · 一席",
    "palette": [("墨绿", "#0F1B17"), ("骨白", "#E7E0D1"), ("苔", "#8E9A90"), ("沙", "#D2B48C"), ("线", "#24332D")],
    "type": "标题 霞鹜文楷 · 西文 Fraunces Italic · 标签 思源黑体 400 宽字距",
    "fonts": ["lxgw-wenkai", "fraunces", "noto-sans-sc"],
    "css": """
body { background:#0F1B17; color:#E7E0D1; }
body::after { content:''; position:absolute; inset:0; background:radial-gradient(ellipse 70% 60% at 50% 45%, rgba(210,180,140,.06), rgba(0,0,0,.35) 100%); }
.lab { position:absolute; left:0; right:0; top:300px; text-align:center; font:400 22px/1 'noto-sans-sc'; letter-spacing:.5em; color:#8E9A90; }
.h { position:absolute; left:0; right:0; top:380px; text-align:center; font:500 118px/1.35 'lxgw-wenkai'; letter-spacing:.06em; }
.h b { font-weight:500; color:#D2B48C; }
.ln { position:absolute; left:50%; top:722px; width:64px; height:1px; margin-left:-32px; background:#D2B48C; }
.en { position:absolute; left:0; right:0; top:756px; text-align:center; font:italic 300 38px/1.3 'fraunces'; color:#A9B3AA; font-variation-settings:'SOFT' 100, 'WONK' 1; }
.cn { position:absolute; left:110px; bottom:84px; font:400 18px/1 'noto-sans-sc'; letter-spacing:.3em; color:#5E6E66; }
.t2 { position:absolute; left:0; right:0; top:140px; text-align:center; font:500 56px/1.3 'lxgw-wenkai'; letter-spacing:.08em; }
.fig { position:absolute; top:270px; width:760px; } .fa { left:150px; } .fb { right:150px; }
.fig img { width:760px; height:507px; object-fit:cover; display:block; }
.fb img { filter:grayscale(.8) brightness(.45); }
.cap { margin-top:26px; text-align:center; font:500 34px/1 'lxgw-wenkai'; letter-spacing:.12em; } .fb .cap { color:#6F7D74; }
.cap i { display:block; margin-bottom:10px; font:italic 300 22px 'fraunces'; letter-spacing:.1em; color:#D2B48C; } .fb .cap i { color:#5E6E66; }
""",
    "s1": """<div class="lab">第 二 件 事</div><div class="h">差别不在工具，<br>在<b>判断</b>。</div><i class="ln"></i>
<div class="en">It was never the tool. It is the judgement.</div><div class="cn">第九顶帽子</div>""",
    "s2": """<div class="t2">同一个模型，同样的提示词</div>
<div class="fig fa"><img src="{a}"><div class="cap"><i>the one you keep</i>像杂志</div></div>
<div class="fig fb"><img src="{b}"><div class="cap"><i>the one you throw away</i>像地摊海报</div></div><div class="cn">第九顶帽子</div>""",
}

# ------------------------------------------------------------------ C · 克莱因色块 (Swiss poster)
D["klein"] = {
    "name": "克莱因色块", "refs": "Experimental Jetset · Nothing · Spotify 年度报告 · 瑞士国际主义海报",
    "palette": [("米白", "#F3F0E8"), ("黑", "#111111"), ("克莱因蓝", "#1A3BD8"), ("浅灰", "#D9D5CC")],
    "type": "标题 得意黑 · 西文 Archivo 窄体 800 · 标签 Archivo 600",
    "fonts": ["smiley-sans", "archivo"],
    "css": """
body { background:#F3F0E8; color:#111; }
.blk { position:absolute; right:0; top:0; bottom:0; width:820px; background:#1A3BD8; }
.h1 { position:absolute; left:120px; top:250px; font:400 196px/1.02 'smiley-sans'; letter-spacing:-.01em; }
.h2 { position:absolute; left:1180px; top:420px; font:400 260px/1 'smiley-sans'; color:#F3F0E8; }
.lbl { position:absolute; font:600 20px/1.2 'archivo'; letter-spacing:.14em; text-transform:uppercase; }
.l1 { left:124px; top:170px; } .l2 { left:1180px; top:340px; color:#C9D2FF; } .l3 { left:124px; bottom:90px; color:#7D786E; }
.big { position:absolute; left:1176px; bottom:70px; font:800 120px/1 'archivo'; font-stretch:75%; color:#3F5BEA; }
.half { position:absolute; top:0; bottom:0; width:50%; overflow:hidden; } .ha { left:0; } .hb { right:0; background:#111; }
.half img { width:100%; height:100%; object-fit:cover; display:block; } .hb img { filter:grayscale(1) brightness(.5); }
.ab { position:absolute; bottom:70px; font:800 220px/1 'archivo'; font-stretch:75%; } .ha .ab { left:70px; color:#F3F0E8; } .hb .ab { left:70px; color:#1A3BD8; }
.tg { position:absolute; top:70px; left:70px; font:400 64px/1 'smiley-sans'; padding:10px 22px; } .ha .tg { background:#1A3BD8; color:#F3F0E8; } .hb .tg { background:#F3F0E8; color:#111; }
""",
    "s1": """<div class="blk"></div><div class="lbl l1">Not the tool —</div><div class="h1">差别<br>不在<br>工具</div>
<div class="lbl l2">— the judgement</div><div class="h2">在判断</div><div class="big">02</div><div class="lbl l3">第九顶帽子 · The Ninth Hat</div>""",
    "s2": """<div class="half ha"><img src="{a}"><div class="tg">像杂志</div><div class="ab">A</div></div>
<div class="half hb"><img src="{b}"><div class="tg">像地摊海报</div><div class="ab">B</div></div>""",
}

# ------------------------------------------------------------------ E · 暗房胶片 (cinematic)
D["darkroom"] = {
    "name": "暗房胶片", "refs": "Pursuit of Wonder · 王家卫片头 · Criterion 字卡",
    "palette": [("暗房黑", "#120F0D"), ("乳白", "#EFE5D3"), ("褪色", "#9C9182"), ("安全灯红", "#B4432F")],
    "type": "标题 思源宋体 300 宽字距 · 西文 EB Garamond Italic",
    "fonts": ["noto-serif-sc", "eb-garamond-italic"],
    "css": """
body { background:#120F0D; color:#EFE5D3; }
.lb { position:absolute; left:0; right:0; height:132px; background:#000; z-index:3; } .lt { top:0; } .lbb { bottom:0; }
.ph { position:absolute; inset:0; } .ph img { width:100%; height:100%; object-fit:cover; filter:sepia(.25) saturate(.8) contrast(1.05) brightness(.55); }
.gr { position:absolute; inset:0; background:linear-gradient(180deg, rgba(18,15,13,.1), rgba(18,15,13,.75)); }
.h { position:absolute; left:0; right:0; top:560px; text-align:center; font:300 76px/1.5 'noto-serif-sc'; letter-spacing:.24em; z-index:2; }
.h b { font-weight:300; color:#E4A08F; }
.en { position:absolute; left:0; right:0; top:760px; text-align:center; font:italic 400 30px 'eb-garamond-italic'; letter-spacing:.06em; color:#B5AA99; z-index:2; }
.tc { position:absolute; right:60px; bottom:52px; font:italic 400 22px 'eb-garamond-italic'; color:#6A6158; z-index:4; letter-spacing:.2em; }
.dip { position:absolute; top:250px; width:780px; } .da { left:150px; } .db { right:150px; }
.dip img { width:780px; height:520px; object-fit:cover; display:block; border:10px solid #EFE5D3; } .db img { filter:grayscale(1) brightness(.6); border-color:#5a534b; }
.dc { margin-top:24px; text-align:center; font:300 30px/1 'noto-serif-sc'; letter-spacing:.3em; } .db .dc { color:#7D7468; }
""",
    "s1": """<div class="ph"><img src="{q}"></div><div class="gr"></div><i class="lb lt"></i><i class="lb lbb"></i>
<div class="h">差别不在工具，在<b>判断</b>。</div><div class="en">It was never the tool. It is the judgement.</div><div class="tc">第九顶帽子 — 02</div>""",
    "s2": """<i class="lb lt"></i><i class="lb lbb"></i>
<div class="dip da"><img src="{a}"><div class="dc">像杂志</div></div><div class="dip db"><img src="{b}"><div class="dc">像地摊海报</div></div><div class="tc">第九顶帽子 — 02</div>""",
}

# ------------------------------------------------------------------ F · 白昼发布会 (light keynote)
D["daylight"] = {
    "name": "白昼发布会", "refs": "Apple 发布会白场 · Linear 官网 · 何同学",
    "palette": [("白", "#F5F5F7"), ("石墨", "#1D1D1F"), ("灰", "#6E6E73"), ("蓝", "#0A63E0")],
    "type": "标题 思源黑体 700 紧排 · 西文 Inter 600",
    "fonts": ["noto-sans-sc", "inter"],
    "css": """
body { background:#F5F5F7; color:#1D1D1F; }
.k { position:absolute; left:0; right:0; top:330px; text-align:center; font:600 30px/1 'inter'; color:#6E6E73; letter-spacing:-.01em; }
.h { position:absolute; left:0; right:0; top:400px; text-align:center; font:700 150px/1.12 'noto-sans-sc'; letter-spacing:-.04em; }
.h b { font-weight:700; color:#0A63E0; }
.en { position:absolute; left:0; right:0; top:800px; text-align:center; font:600 34px/1 'inter'; color:#86868B; letter-spacing:-.02em; }
.t2 { position:absolute; left:0; right:0; top:150px; text-align:center; font:700 64px/1.2 'noto-sans-sc'; letter-spacing:-.03em; }
.card { position:absolute; top:300px; width:760px; border-radius:30px; overflow:hidden; background:#fff; box-shadow:0 30px 70px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.05); }
.ca { left:150px; } .cb { right:150px; }
.card img { width:760px; height:470px; object-fit:cover; display:block; } .cb img { filter:grayscale(1) contrast(.9); opacity:.45; }
.card .c { padding:26px 34px; display:flex; justify-content:space-between; align-items:center; font:700 34px 'noto-sans-sc'; letter-spacing:-.02em; }
.card .c span { font:600 22px 'inter'; color:#0A63E0; } .cb .c { color:#86868B; } .cb .c span { color:#86868B; }
""",
    "s1": """<div class="k">The second thing.</div><div class="h">差别不在工具，<br>在<b>判断</b>。</div><div class="en">It was never the tool.</div>""",
    "s2": """<div class="t2">同一个模型，同样的提示词。</div>
<div class="card ca"><img src="{a}"><div class="c">像杂志<span>Keep</span></div></div>
<div class="card cb"><img src="{b}"><div class="c">像地摊海报<span>Discard</span></div></div>""",
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[1].split(",") if len(sys.argv) > 1 else list(D)
    for k in only:
        d = D[k]
        faces = "\n".join(ff(f) for f in d["fonts"])
        for n in ("s1", "s2"):
            body = d[n].format(a=img("cup_mag.jpg"), b=img("cup_cheap.jpg"), q=img("hands.jpg"))
            page = f"<!doctype html><html><head><meta charset='utf-8'><style>{faces}\n{BASE}\n{d['css']}</style></head><body>{body}</body></html>"
            hp = OUT / f"{k}_{n}.html"; hp.write_text(page)
            png = OUT / f"{k}_{n}.png"
            subprocess.run(["node", str(WEBSHOT), hp.as_uri(), str(png), "--width", "1920", "--height", "1080", "--scale", "1"], check=True, capture_output=True)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(png), "-q:v", "3", str(OUT / f"{k}_{n}.jpg")], check=True)
            print("ok", k, n)


if __name__ == "__main__":
    main()
