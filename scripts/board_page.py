#!/usr/bin/env python3
"""The aesthetic direction board page (published to the same gallery Artifact).

  python3 scripts/board_page.py -> dist/gallery/index.html + prints the files map
"""
import html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import board  # noqa: E402

OUT = SKILL / "dist" / "gallery"
B = SKILL / "dist" / "board"
PV = SKILL / "examples" / "demo" / "previews"
ORDER = ["paper", "night", "klein", "darkroom", "daylight", "clay"]
CLAY = {"name": "陶土影棚 · 三维", "refs": "Buck · Ordinary Folk · Apple「iPhone 拍摄」陶土片 · C4D 陶土渲染",
        "palette": [("暖灰", "#CFC8BE"), ("赤陶", "#C2643F"), ("石膏", "#F4F0E8"), ("炭", "#3D3833")],
        "type": "三维立体字 思源宋体 900 挤出 · 平面层 EB Garamond + 思源宋体"}


def main():
    tpl = (HERE / "gallery_template.html").read_text()
    style = tpl[tpl.index("<style>") + 7: tpl.index("</style>")]
    files, rows = {}, []
    for i, k in enumerate(ORDER, 1):
        d = CLAY if k == "clay" else board.D[k]
        for n in ("s1", "s2"):
            files[f"b/{k}_{n}.jpg"] = str(B / f"{k}_{n}.jpg")
        sw = "".join(f'<li><i style="background:{c}"></i><span>{html.escape(nm)}</span><code>{c}</code></li>' for nm, c in d["palette"])
        extra = ""
        if k == "clay":
            files["v/clay.mp4"] = str(PV / "clay_16x9.mp4"); files["v/clay.jpg"] = str(PV / "clay_16x9.jpg")
            extra = '<div class="mv"><video src="v/clay.mp4" poster="v/clay.jpg" controls playsinline preload="metadata"></video><p>动起来的样子（18 秒，镜头在同一个三维布景里飞行）</p></div>'
        rows.append(f"""
<section class="dir" id="{k}">
  <header><span class="idx">{i:02d}</span><h2>{html.escape(d['name'])}</h2><p class="refs">参照 {html.escape(d['refs'])}</p></header>
  <div class="pair"><img src="b/{k}_s1.jpg" alt="{html.escape(d['name'])} 观点帧" loading="lazy"><img src="b/{k}_s2.jpg" alt="{html.escape(d['name'])} 对比帧" loading="lazy"></div>
  <div class="spec"><ul class="pal">{sw}</ul><p class="type">{html.escape(d['type'])}</p></div>{extra}
</section>""")
    files["v/hud.mp4"] = str(PV / "hud_16x9.mp4"); files["v/hud.jpg"] = str(PV / "hud_16x9.jpg")
    # AE effect library reel (both orientations) + ranked list from its video.json
    AP = SKILL / "examples" / "aefx" / "previews"
    for k in ("16x9", "9x16"):
        files[f"v/fx_{k}.mp4"] = str(AP / f"reel_{k}.mp4"); files[f"v/fx_{k}.jpg"] = str(AP / f"reel_{k}.jpg")
    fxj = json.loads((SKILL / "examples" / "aefx" / "video.json").read_text())
    items = []
    t = 0.0
    for b in fxj["beats"]:
        if b.get("fx") == "plate" and b.get("text") == "转场": t = b["t"]; continue
        lab, ref = b.get("label", ""), b.get("ref", "")
        mm = int(b["t"] // 60); ss = int(b["t"] % 60)
        items.append(f'<li><code>{mm}:{ss:02d}</code><b>{html.escape(lab)}</b><span>{html.escape(ref)}</span></li>')
    fx_html = f"""
<section class="fxs">
  <h2>AE 动效库 · 按人气复刻</h2>
  <p class="refs">40 个效果和转场，按 VideoHive 销量、YouTube / B 站播放量排序（数据见调研 ae_popular.md）。横屏、竖屏同一套代码自适应。</p>
  <div class="fxv"><div class="h"><video src="v/fx_16x9.mp4" poster="v/fx_16x9.jpg" controls playsinline preload="metadata"></video><p>横屏 16:9 · 86 秒</p></div>
  <div class="v"><video src="v/fx_9x16.mp4" poster="v/fx_9x16.jpg" controls playsinline preload="metadata"></video><p>竖屏 9:16</p></div></div>
  <ol class="fxl">{''.join(items)}</ol>
</section>"""
    log = (SKILL / "CHANGELOG.md").read_text()
    log_html = "".join(f"<li>{html.escape(l[2:])}</li>" for l in log.splitlines() if l.startswith("- "))[:6000]
    page = f"""<title>九帽动效样片墙</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@500;700&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>{style}
.dir {{ margin-top:64px; padding-top:28px; border-top:1px solid var(--rule); display:grid; gap:18px; }}
.dir header {{ display:flex; align-items:baseline; gap:16px; flex-wrap:wrap; }}
.dir .idx {{ font-family:var(--f-mono); color:var(--shiba); font-size:14px; }}
.dir h2 {{ margin:0; }}
.dir .refs {{ margin:0; color:var(--dim); font-size:14px; }}
.pair {{ display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:14px; }}
.pair img {{ width:100%; aspect-ratio:16/9; object-fit:cover; display:block; border-radius:3px; box-shadow:0 0 0 1px var(--rule); }}
.spec {{ display:flex; gap:28px; align-items:center; flex-wrap:wrap; }}
.pal {{ list-style:none; margin:0; padding:0; display:flex; gap:16px; flex-wrap:wrap; }}
.pal li {{ display:flex; align-items:center; gap:7px; font-size:13px; color:var(--dim); }}
.pal i {{ width:18px; height:18px; border-radius:50%; display:block; box-shadow:0 0 0 1px rgba(255,255,255,.2); }}
.pal code {{ font-family:var(--f-mono); font-size:12px; color:var(--ink); opacity:.7; }}
.type {{ margin:0; font-size:14px; color:var(--ink); }}
.mv {{ max-width:900px; }} .mv video {{ width:100%; aspect-ratio:16/9; display:block; background:#000; border-radius:3px; }} .mv p {{ margin:8px 0 0; font-size:13px; color:var(--dim); }}
.fxs {{ margin-top:48px; display:grid; gap:16px; }}
.fxv {{ display:grid; grid-template-columns:minmax(0, 3fr) minmax(0, 1fr); gap:16px; align-items:start; }}
.fxv video {{ width:100%; display:block; background:#000; border-radius:3px; }} .fxv .h video {{ aspect-ratio:16/9; }} .fxv .v video {{ aspect-ratio:9/16; }}
.fxv p {{ margin:6px 0 0; font-size:13px; color:var(--dim); }}
.fxl {{ list-style:none; margin:0; padding:0; columns:2; column-gap:32px; font-size:13px; }}
.fxl li {{ break-inside:avoid; display:grid; grid-template-columns:44px minmax(0, 1fr); column-gap:10px; padding:6px 0; border-bottom:1px solid var(--rule); }}
.fxl code {{ font-family:var(--f-mono); color:var(--shiba); grid-row:span 2; }} .fxl b {{ font-weight:500; color:var(--ink); }} .fxl span {{ color:var(--dim); }}
.bh {{ margin-top:72px; }}
@media (max-width: 860px) {{ .fxv {{ grid-template-columns:minmax(0, 1fr); }} .fxl {{ columns:1; }} }}
.ask {{ margin-top:22px; background:var(--slip); border:1px solid var(--rule); border-radius:6px; padding:16px 20px; color:var(--dim); max-width:60em; }}
.ask b {{ color:var(--ink); font-weight:500; }}
@media (max-width: 860px) {{ .pair {{ grid-template-columns:minmax(0, 1fr); }} }}
</style>
<div class="wrap">
  <header>
    <div><div class="kick">第九顶帽子 · 九帽动效 v0.3</div><h1>按最高赞复刻的 AE 动效</h1></div>
    <p class="lede">不再自己编动效：先统计 VideoHive 销量、YouTube 和 B 站播放量最高的 AE 动效，再逐个用代码复刻，横屏竖屏都能用。下面还有上一轮的美学方向板（配色和字体）。</p>
  </header>
  <div class="ask">先看最上面的<b>动效库</b>：哪些效果复刻得不像、哪些想多用，直接说时间点（比如「0:42 霓虹不够亮」）。下面的方向板管配色和字体。</div>
  {fx_html}
  <h2 class="bh">美学方向板</h2>
  {''.join(rows)}
  <section class="notes">
    <div>
      <h3>上一轮的动画试做（供对比）</h3>
      <div class="mv"><video src="v/hud.mp4" poster="v/hud.jpg" controls playsinline preload="metadata"></video><p>暗场 HUD（对标所长林超 / 小Lin说）：你评价「中规中矩」，颜色用了金色渐变，已放弃这条配色。</p></div>
    </div>
    <div><h3>更新记录</h3><ul>{log_html}</ul></div>
  </section>
  <footer>示例图片用 GPT Image 2 自行生成 · 配音为本地 TTS 占位 · 字体均为 OFL / Apache</footer>
</div>
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "index.html").write_text(page)
    (OUT / "files.json").write_text(json.dumps(files, indent=1))
    print(OUT / "index.html", len(files), "files")


if __name__ == "__main__":
    main()
