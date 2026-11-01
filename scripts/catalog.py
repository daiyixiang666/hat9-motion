#!/usr/bin/env python3
"""Effect catalog: cut every effect out of the showcase reel as a looping preview, and write docs/effects.md.

  python3 scripts/catalog.py      (needs examples/aefx/renders/reel_16x9.mp4 [+ reel_9x16.mp4])
  -> assets/previews/fx/<name>.webp + .gif   and   docs/effects.md
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
from h9 import aefx  # noqa: E402

EX = SKILL / "examples" / "aefx"
OUT = SKILL / "assets" / "previews" / "fx"
DOC = SKILL / "docs" / "effects.md"
CARDS = SKILL / "references" / "effects"
GIF = "--gif" in sys.argv          # webp only by default (GitHub renders animated webp); --gif adds fallbacks
GALLERY = SKILL / "gallery"
CAT = {   # gallery filter categories
    "字效": ["pop", "mask_up", "tracking", "blur_focus", "apple_blur", "typewriter", "scramble", "write_on", "flip3d", "slice_text", "shine",
             "glitch", "neon", "stomp", "match_cut", "impact", "ghost_type", "lockup"],
    "图形": ["burst", "cartoon", "gooey", "diffuse"],
    "照片": ["parallax", "mosaic", "collage", "portal", "callout", "text_mask"],
    "数据": ["odometer", "bars", "line_draw", "donut", "timeline"],
    "地图": ["earth_zoom", "map_route"],
    "界面": ["notify", "lower3", "triple", "chat", "hud_lock", "glass", "comment_thread", "im_chat", "danmaku", "receipt"],
    "结构": ["list_stack", "steps", "ranking", "pros_cons", "quadrant", "countdown", "chapter_bar"],
    "素材": ["media"],
    "引用": ["cite_pdf", "cite_paper", "cite_article", "cite_quote", "cite_post", "cite_video", "cite_stack"],
    "屏幕": ["scroll_shot", "screencast", "spotlight", "code"],
    "人物": ["profile_card", "equity_tree"],
    "节奏": ["breather", "interlude", "suspense", "cold_open", "beat_cut", "reaction", "loading", "think_loop", "chapter_breather"],
}
CAT["字效"] += ["term_card", "word_swap"]
CAT["数据"] += ["table", "statement_table", "waterfall", "scale_compare", "bar_race", "stacked_bars", "formula", "bars_csv", "line_csv"]
CAT["地图"] += ["china_map"]
def cat_of(fx): return next((k for k, v in CAT.items() if fx in v), "其他")


def cut(src, t, d, dst, w=480, fps=15):
    """one effect -> animated webp (small, via Pillow) + gif (universal); a little trimmed off each end of the beat."""
    import tempfile
    from PIL import Image
    a, dur = t + 0.12, max(0.6, d - 0.3)
    vf = f"fps={fps},scale={w}:-2:flags=lanczos"
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(src), "-vf", vf, f"{td}/f%04d.png"], check=True)
        frames = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("f*.png"))]
        frames[0].save(dst.with_suffix(".webp"), save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, quality=72, method=5)
    if not GIF: return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(src), "-vf", f"{vf},split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4", "-loop", "0", str(dst.with_suffix(".gif"))], check=True)


SUIT = {
    "pop": "开场、短标题", "mask_up": "任何标题、两行观点", "tracking": "电影感标题、一个词", "blur_focus": "金句、英文口号", "apple_blur": "结论、产品口吻的判断句",
    "typewriter": "提示词、命令、搜索", "scramble": "技术名词、英文代号", "write_on": "关键词、签名、毛笔字", "flip3d": "账号名、章节名", "slice_text": "对比、反转",
    "shine": "收尾、品牌", "glitch": "出错、警告、反转", "neon": "夜景、潮流、店招", "stomp": "节奏快的一句话、金句拆字", "match_cut": "一个词贯穿多个场景",
    "impact": "重点结论、冲击句", "ghost_type": "章节标题 + 小字说明", "lockup": "中英双语标题、字体展示", "burst": "爆款、数字揭晓、强调",
    "cartoon": "搞笑、吐槽、意外", "gooey": "合并、碰撞、两者关系", "diffuse": "安静的过渡、情绪句", "parallax": "开场大图、人物故事",
    "mosaic": "大量案例、作品合集", "collage": "资料拼贴、证据", "portal": "从一个画面进入另一个话题", "callout": "指出图里的细节",
    "odometer": "任何数字、比例", "notify": "平台反馈、增长、消息", "lower3": "人物 / 账号介绍、结尾", "triple": "片尾求三连 / 关注",
    "earth_zoom": "地点揭晓、「在哪里」、开场定位", "map_route": "路线、物流、扩张、从 A 到 B", "bars": "逐年对比、排行、增长 / 下滑",
    "line_draw": "趋势、增长曲线、穿过零线的变化", "donut": "占比、构成、「一半以上」", "timeline": "发展历程、关键年份、复盘",
    "chat": "问 AI、对话、提示词演示", "hud_lock": "锁定目标、指出关键人 / 物、选址", "glass": "一个核心数字浮在实拍上",
    "text_mask": "一个关键词 + 实拍，转场进入画面",
}
DUR = {"stomp": "按口播，每词 0.3–0.5 秒", "portal": "2.5–3 秒", "mosaic": "2.5–3 秒", "match_cut": "2–3 秒（每 0.22 秒一切）", "parallax": "2–4 秒",
       "earth_zoom": "3–4 秒", "map_route": "3–4 秒", "bars": "3 秒起，每多 5 根 +0.5 秒", "line_draw": "3–4 秒", "timeline": "每个节点 ≥ 0.5 秒",
       "chat": "一问一答 3.5 秒；每多一条 +1 秒", "hud_lock": "3 秒", "text_mask": "3 秒（多图每张 ≥ 0.15 秒）"}
PIT = {
    "parallax": "需要先抠图 + 修补背景板（scripts/cutout 流程）；主体太小时视差不明显。",
    "stomp": "词太长会自动缩字号；一页最好 2–4 个字。",
    "portal": "x / y 要对准画面里的「洞」（瞳孔、杯口、窗）；竖屏裁切后坐标会变。",
    "callout": "竖屏时图片裁切不同，x / y 要按竖屏重新给。",
    "match_cut": "每个画面的底色和字色是成对设计的，换图时保持一深一浅交替。",
    "write_on": "笔画描边依赖字体轮廓；毛笔字体（马善政）效果最好。",
    "ghost_type": "虚影字是故意半透明的，check 时已标记为允许重叠。",
    "earth_zoom": "只画陆地不画国界；需要国界时必须换中国视角数据并核对标准地图。d3 / topojson 走 jsdelivr，渲染机要能联网。",
    "map_route": "途经点决定线走哪条走廊，只给起终点会画成大圆航线；跨日期变更线的路线会自动以路线为中心。",
    "bars": "超过 10 根（竖屏 7 根）或标签很长时自动改横向；负数挂在零线下方并换浅色；大于 10 万自动换算万 / 亿。",
    "line_draw": "点很多时横轴标签自动隔几个显示；有负数时画零线，面积填到零线。",
    "donut": "segments 会按总和归一化，最多 6 段。",
    "chat": "文字太多时字号会缩到 2vmin，再多就让旧消息上滚出窗口。",
    "hud_lock": "竖屏会裁图，用 v: {x, y, w, h, ox} 单独给竖屏的框和裁切位置。",
    "glass": "用视频做背景时卡片的模糊依赖 backdrop-filter，渲染里已验证有效。",
    "text_mask": "多图时每张图在字里切换；没有图时用强调色渐变填字、不做穿透。",
}


REELS = [EX] + [SKILL / "examples" / d for d in ("media", "cite", "structure", "data", "screens", "social", "pacing")]   # every demo reel that feeds the gallery


def beats():
    """(beat, reel_16x9, reel_9x16) across all demo reels that have been rendered."""
    for ex in REELS:
        vj, r = ex / "video.json", ex / "renders" / "reel_16x9.mp4"
        if not (vj.exists() and r.exists()): continue
        for b in json.loads(vj.read_text())["beats"]:
            yield b, r, ex / "renders" / "reel_9x16.mp4"

SUIT.update({
    "media": "任意张数的图片 / 视频：1 张、3 张、200 张各是一种编排",
    "cite_pdf": "引用判决书、报告、财报原文", "cite_paper": "引用论文", "cite_article": "引用新闻报道", "cite_quote": "引用某人说过的话",
    "cite_post": "引用一条社交帖子", "cite_video": "引用别人的视频片段", "cite_stack": "多个信源交叉验证",
    "list_stack": "「三个原因」「四个要点」、清单、结尾总结", "steps": "教程、流程、「三步做出……」", "ranking": "盘点、年度十大、门店 / 销量排行",
    "term_card": "名词解释、概念、术语", "word_swap": "「不是 A，是 B」「它能做 X / Y / Z」", "pros_cons": "测评、优缺点、该不该",
    "quadrant": "定位、谁在哪个位置、2×2 矩阵", "countdown": "「给你 5 秒」、悬念、倒数", "chapter_bar": "目录、第几部分、章节过渡",
    "table": "多年财务、对比清单、参数表", "statement_table": "利润表 / 资产负债表里的一行", "waterfall": "从收入一路扣到净利",
    "scale_compare": "「相当于 N 个…」「绕赤道 N 圈」", "bar_race": "排名随时间变化、超车", "stacked_bars": "构成变化、占比",
    "formula": "一个比率怎么算出来", "bars_csv": "手上只有一张表格", "line_csv": "手上只有一张表格（趋势）",
    "scroll_shot": "长截图、网页、长聊天记录", "screencast": "真实录屏、教程、产品演示", "spotlight": "「看这里」「只看这一行」", "code": "代码、命令行、改动前后",
    "comment_thread": "评论区截图、热评", "im_chat": "聊天记录、对话证据", "danmaku": "弹幕刷屏、高能时刻", "receipt": "小票、账单、客单价",
    "profile_card": "人物介绍、创始人、管理层", "equity_tree": "股权穿透、组织架构", "china_map": "省份对比、分级设色、门店撒点",
    "breather": "金句后的停顿、留白", "interlude": "章节之间的空镜、纯音乐段", "suspense": "「答案是……」揭晓数字", "cold_open": "片头先画面后说话",
    "beat_cut": "音乐卡点、快节奏蒙太奇", "reaction": "好笑 / 沉重的反应时刻", "loading": "等待、加载、「正在生成」", "think_loop": "思考停顿", "chapter_breather": "章节之间喘口气",
})
DUR.update({
    "media": "1–3 张 3–4 秒，几十张以上 4–6 秒", "list_stack": "每条 0.6–1 秒 + 1 秒", "steps": "每步 0.6–1 秒 + 1 秒", "ranking": "每条 0.4–0.6 秒 + 第 1 名 1.5 秒",
    "word_swap": "每个词 0.5–0.8 秒", "countdown": "每下 0.5–1 秒", "term_card": "3.5–5 秒", "table": "3.5–5 秒", "statement_table": "4–5 秒", "waterfall": "4–6 秒",
    "scale_compare": "4–5 秒", "bar_race": "每个时间点 1.5–3 秒", "stacked_bars": "4–5 秒", "formula": "3.5–4.5 秒", "scroll_shot": "每个停点 1–1.5 秒",
    "screencast": "跟录屏一样长（3–10 秒）", "code": "3–6 秒（行多就更长）", "comment_thread": "3.5–5 秒", "im_chat": "4–6 秒", "equity_tree": "4–5 秒", "china_map": "4–5 秒",
    "cite_pdf": "4–5 秒", "cite_video": "跟引用片段一样长", "cite_stack": "每个信源 1–1.5 秒",
    **{k: "1–8 秒（按时长伸缩）" for k in ("breather", "interlude", "cold_open", "reaction", "loading", "think_loop", "chapter_breather")},
    "suspense": "悬停 1–3 秒最佳", "beat_cut": "按小节，100 bpm 每拍 0.6 秒",
})
PIT.update({
    "media": "items 可以混放图片和视频；几十张以上用缩略图拼图，视频只显示静帧。",
    "cite_pdf": "quote 要和 PDF 里的原文一字不差才能定位；扫描件用 box 手动框。", "cite_video": "视频要能逐帧定位（mp4 / webm）；字幕写原话或描述，别编台词。",
    "list_stack": "条目里的「：」会把后半句拆成小字说明；不想拆就用 [\"整句\", \"\"]。", "ranking": "第 1 名放在 items 第一个；默认先显示问号卡再翻开，hide_top: false 关掉。",
    "countdown": "问题用 question（label 是画廊页脚）。", "quadrant": "x、y 是 0–100 的相对位置，不是原始数值。", "word_swap": "replace 模式只用前两个词。",
    "table": "行数超过上限会折叠；高亮用首列文字比用序号稳。", "statement_table": "负数写成负值即可，显示时自动加括号；值单位用 unit 写明。",
    "waterfall": "最后一行留空就自动算合计；kind 用 sub 插小计。", "scale_compare": "ratio 自己算好写进去，method 写明换算口径。", "bar_race": "不同公司的财年口径要在 note 里写明。",
    "scroll_shot": "停点用 heading / find 时，截图旁要有 webpage.mjs 生成的同名 .json。", "screencast": "clicks 里的 t 是录屏里的秒数，at 是这一拍里的秒数或 \"@关键词\"。",
    "code": "文件参数叫 file（src 是页脚来源）。", "china_map": "需要中国视角数据和南海诸岛附图（已内置）；各省数据要能引用来源。",
    "profile_card": "单人的一句话简介用 bio，line 是口播字幕。", "cold_open": "配音要整体后移（meta.lead），否则会压在开场上。",
    "beat_cut": "要有 meta.bpm 或 beats，否则按 0.5 秒切。", "suspense": "揭晓用 at: \"@词\"，否则在 62% 处。", "think_loop": "圈数参数叫 orbits（marks 是保留字）。",
})


def main():
    OUT.mkdir(parents=True, exist_ok=True); DOC.parent.mkdir(parents=True, exist_ok=True)
    CARDS.mkdir(parents=True, exist_ok=True); GALLERY.mkdir(parents=True, exist_ok=True)
    rows, trans = [], []
    seen, carded = set(), set()
    for b, reel, reel_v in beats():
        fx = b["fx"]
        if fx == "plate":
            if b.get("tr") and b["tr"] != "hard":
                name = f"tr_{b['tr']}"
                cut(reel, b["t"] - 0.45, 1.2, OUT / name, w=360)
                if reel_v.exists(): cut(reel_v, b["t"] - 0.45, 1.2, OUT / f"{name}_v", w=200)
                trans.append((b["tr"], b.get("label", ""), name))
            continue
        band = b.get("preview")                 # a variant worth its own card (e.g. media with 3 vs 200 items)
        key = f"{fx}-{band}" if band else fx
        if key in seen: continue
        seen.add(key)
        cut(reel, b["t"], b["d"], OUT / key)
        if reel_v.exists(): cut(reel_v, b["t"], b["d"], OUT / f"{key}_v", w=240)
        doc = (aefx.FX[fx].__doc__ or "").strip().replace("\n", " ")
        title, _, how = doc.partition(":")
        import inspect
        params = sorted(set(re.findall(r'p\[["\'](\w+)["\']\]|p\.get\(["\'](\w+)["\']', inspect.getsource(aefx.FX[fx]))))
        keys = sorted({a or b_ for a, b_ in params} - {"label", "ref"})
        rows.append((fx, title.strip(), how.strip(), keys, b.get("label", ""), b.get("ref", ""), key, b.get("band_label", "")))
        if fx in carded: continue
        carded.add(fx)
        ex = {k: v for k, v in b.items() if k not in ("t", "d", "tr", "label", "ref")}
        ex = {"scene": "fx", **{k: v for k, v in ex.items() if k != "scene"}, "t": "@关键词"}
        (CARDS / f"{fx}.md").write_text(f"""# `{fx}` · {title.strip()}

<img src="../../assets/previews/fx/{fx}.webp" width="480" alt="{fx} 横屏"> <img src="../../assets/previews/fx/{fx}_v.webp" width="160" alt="{fx} 竖屏">

**怎么动**：{how.strip()}

| 项 | 内容 |
|---|---|
| 类别 | {cat_of(fx)} |
| 适合的句子 | {SUIT.get(fx, '—')} |
| 建议时长 | {DUR.get(fx, '2–3 秒')} |
| 参数 | {', '.join(f'`{k}`' for k in keys) or '—'} |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | {b.get('ref', '—')} |

```json
{json.dumps(ex, ensure_ascii=False, indent=1)}
```

**已知坑**：{PIT.get(fx, '无')}
""")
    md = ["# 效果目录 · Effects", "", "每个效果都是 `scripts/h9/aefx.py` 里的一个函数，在 `video.json` 里写成一个 beat：", "",
          '```json\n{"scene": "fx", "fx": "stomp", "words": ["大家", "都在用", "AI"], "t": "@大家"}\n```', "",
          "排名和人气依据见 [`research/ae_popular.md`](../research/ae_popular.md)。横屏、竖屏同一套参数。", "", "## 效果", ""]
    for fx, title, how, keys, label, ref, key, band in rows:
        if key != fx:      # band variants: one extra preview line under the effect
            md += [f'<img src="../assets/previews/fx/{key}.webp" width="320" alt="{fx} {band}"> {band}', ""]
            continue
        md += [f"### `{fx}` — {title}", "", f'<img src="../assets/previews/fx/{fx}.webp" width="480" alt="{fx}">', "",
               how, "", f"- 参数：{', '.join(f'`{k}`' for k in keys) or '—'}", f"- 人气：{ref or '—'}", ""]
    md += ["## 转场", "", "写在下一个 beat 上：`\"tr\": \"zoomin\"`。", "", "| 转场 | 预览 | 说明 |", "|---|---|---|"]
    for k, label, name in trans:
        md.append(f'| `{k}` | <img src="../assets/previews/fx/{name}.webp" width="240"> | {label} |')
    DOC.write_text("\n".join(md) + "\n")
    # agent index: one line per effect, pick by name without reading the library
    idx = ["# 九帽动效 · 效果索引（给 AI 读）", "", "在 video.json 里写 {\"scene\": \"fx\", \"fx\": \"<id>\", ...}；转场写在下一个 beat：\"tr\": \"<id>\"。配方卡：references/effects/<id>.md", ""]
    idx += [f"- {r[0]} [{cat_of(r[0])}]: {r[1]} — {SUIT.get(r[0], '')}" for r in rows if r[6] == r[0]]
    idx += ["", "## 转场"] + [f"- {k}: {label}" for k, label, _ in trans]
    (GALLERY / "llms.txt").write_text("\n".join(idx) + "\n")
    (GALLERY / "effects.json").write_text(json.dumps(
        {"effects": [{"id": fx, "file": key, "band": band, "title": title, "how": how, "cat": cat_of(fx), "ref": ref, "label": label, "suit": SUIT.get(fx, "")}
                     for fx, title, how, keys, label, ref, key, band in rows],
         "transitions": [{"id": k, "label": label, "file": name} for k, label, name in trans]}, ensure_ascii=False, indent=1))
    print(DOC, len({r[0] for r in rows}), "effects,", len(rows), "cards,", len(trans), "transitions")


if __name__ == "__main__":
    main()
