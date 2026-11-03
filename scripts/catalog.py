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
STYLE_NAMES = {"reel": "动效库", "press": "财经刊", "poster": "瑞士海报", "zine": "拼贴杂志", "screen": "AI 工具台", "hud": "暗场",
               "doc": "实拍纪录", "papercut": "剪纸", "sketch": "手绘白板", "ink": "水墨国风", "flat": "扁平插画", "pixel": "像素复古"}


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


REELS = [EX] + [SKILL / "examples" / d for d in ("media", "cite", "structure", "data", "screens", "social", "pacing",
                                                   "avmedia", "text2", "charts2", "docs2", "ui2", "genre", "pipeline2")]   # every demo reel that feeds the gallery


def beats():
    """(beat, reel_16x9, reel_9x16, style) across every rendered demo reel. The per-style reels (scripts/style_reels.py,
    examples/styled-<style>/) come first, so a card is cut from the style it is meant to be shown in; effects without
    a styled render fall back to the original reels (the default `reel` look)."""
    for ex in sorted((SKILL / "examples").glob("styled-*")):
        sid = ex.name[len("styled-"):]
        vj, r = ex / "video.json", ex / "renders" / f"{sid}_16x9.mp4"
        if not (vj.exists() and r.exists()): continue
        for b in json.loads(vj.read_text())["beats"]:
            yield b, r, ex / "renders" / f"{sid}_9x16.mp4", sid
    for ex in REELS:
        vj, r = ex / "video.json", ex / "renders" / "reel_16x9.mp4"
        if not (vj.exists() and r.exists()): continue
        for b in json.loads(vj.read_text())["beats"]:
            yield b, r, ex / "renders" / "reel_9x16.mp4", "reel"

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

# ---- second wave (0.7)
CAT["音视频"] = ["pip", "freeze_frame", "speed_ramp", "footage", "audio_quote", "podcast", "talking_head", "host_point"]
SUIT.update({
    "pip": "图形 / 素材占满屏时主持人缩进角落", "freeze_frame": "「停一下，看这里」、关键瞬间标注", "speed_ramp": "慢放看细节、快进跳过",
    "footage": "采访切片、自带字幕的素材", "audio_quote": "引用一段原声、某人在节目里说的话", "podcast": "播客切片、对谈节目",
    "talking_head": "口播段落、Vlog、关键词贴纸", "host_point": "主持人指着数字 / 结论 / 图里的细节",
})
DUR.update({
    "pip": "4–8 秒（缩窗在前 30%）", "freeze_frame": "5–7 秒（定格 2.4–3.4 秒）", "speed_ramp": "按变速后的长度，常见 4–6 秒",
    "footage": "跟素材一样长", "audio_quote": "跟引用的原声一样长 + 0.8 秒", "podcast": "跟切片一样长 + 0.8 秒",
    "talking_head": "每个贴纸 ≥ 0.8 秒，每个插入 2–2.5 秒", "host_point": "5–6 秒",
})
PIT.update({
    "pip": "主画面是自带页眉的成片时，kicker 标签会叠在原片标题上，别加 kicker。",
    "freeze_frame": "box 是原片画面的百分比；先截一帧看准再写，别猜。",
    "speed_ramp": "ramp 用原片秒数；慢放要素材本身有动作，静止镜头慢放看不出来。",
    "footage": "subs:auto 是启发式；原片自带页眉 / 大标题时直接写 subs，并用 zoom 推掉页眉。",
    "audio_quote": "words.json 必须是这段音频自己的时间戳；没有就写 quote（原话，一字不改）。",
    "podcast": "多人 turns 需要真实多人音频；拿单人旁白做多人只能标「示意」。",
    "talking_head": "贴纸每分钟别超过 2–3 个（bench_cn）；8 个只用于压力测试。",
    "host_point": "图片卡的 box 写原图百分比，裁切会自动朝框的方向。",
})
CAT["字效"] += ["text_pages", "vertical_title", "flying_words", "black_slam", "scribble"]
CAT["数据"] += ["number_pages", "combo"]
CAT["结构"] += ["question_card"]
CAT["引用"] += ["scanline"]
SUIT.update({
    "text_pages": "一段话要完整读完（背景介绍、原文、长引用、外文原句）", "question_card": "先抛问题再揭晓（选择题 / 翻面答案）",
    "vertical_title": "国风片名、古文原句、竖排标题", "flying_words": "一串关键词汇成一个结论、开场关键词",
    "number_pages": "一句话里很多数字（财报、快讯）", "combo": "连续累加的次数 / 门店数 / 点赞数",
    "black_slam": "最重的一句结论、反转、冲击金句", "scribble": "推翻一个常见误解、在原文 / 截图上圈重点",
    "scanline": "在文件 / 截图里逐条找出关键句",
})
DUR.update({
    "text_pages": "每句 1.2–2 秒（80–200 字约 6–12 秒，按口播）", "question_card": "4.5–6 秒（揭晓前留 ≥ 1.5 秒）",
    "vertical_title": "title 3–4 秒；classical 5–6 秒", "flying_words": "4–5 秒（每词 0.4–0.6 秒）",
    "number_pages": "每个数字 0.5–0.8 秒（十个数字约 7–8 秒）", "combo": "4–5 秒",
    "black_slam": "3–4 秒（有 hits 时每词 0.3–0.4 秒）", "scribble": "4–5 秒", "scanline": "5–6 秒（每块约 0.6 秒）",
})
PIT.update({
    "text_pages": "长段落用 at 和口播逐句对齐；阿拉伯文 / 希伯来文目前用系统字体。",
    "question_card": "答案要可查；选项 ≤ 5 字才横排。",
    "vertical_title": "古文用通行版本，繁体原文里不要混简体字。",
    "number_pages": "数字口径一致、可查；约数在 src 里注明。",
    "combo": "count 写真实总数；超过逐次显示的上限时计数器按步跳。",
    "black_slam": "一条片子用一两次，多了就不重了。",
    "scribble": "target 要是原文里真实存在的词；图片模式的 box 用百分比。",
    "scanline": "box 要对准原图里的真实位置；标签只是摘要，原文才是证据。",
})
CAT["数据"] += ["icon_unit", "scatter", "funnel", "radar", "then_now", "gantt"]
CAT["地图"] += ["area_overlay", "map_timeline", "street_map"]
CAT["结构"] += ["decision_tree", "converge", "choose_one"]
SUIT.update({
    "icon_unit": "普及率、占比（每 100 人里有几个）", "scatter": "两个指标的关系（店数对收入、价格对销量）",
    "funnel": "转化漏斗、层层筛选", "radar": "多维能力对比（两三家）", "then_now": "今昔对比、前后变化",
    "choose_one": "选择题、先猜再揭晓", "converge": "多个来源汇成一个总数", "gantt": "排期、阶段、并行任务",
    "decision_tree": "如果……就……、判断流程", "area_overlay": "面积有多大（把 A 叠到 B 上）",
    "map_timeline": "逐年扩张、城市名单按年份", "street_map": "街区、门店位置、步行路线（示意或自带数据）",
})
DUR.update({
    "icon_unit": "4–5 秒", "scatter": "4.5–6 秒（点多就更长）", "funnel": "4–5 秒", "radar": "4–5 秒", "then_now": "4–5 秒",
    "choose_one": "4.5–6 秒", "converge": "4.5–6 秒", "gantt": "4.5–6 秒", "decision_tree": "5–6 秒",
    "area_overlay": "5–6 秒", "map_timeline": "6–8 秒（年份多就更长）", "street_map": "5–6 秒",
})
PIT.update({
    "funnel": "mode=share 用于互相包含的人群（不是严格的转化）；conv 才是逐层转化。",
    "radar": "每根轴各自归一，图形只看相对强弱；具体数值看标注。",
    "area_overlay": "面积写官方数字（area）；轮廓只是图。小国家用自带 10m GeoJSON 更准。",
    "map_timeline": "年份和坐标要真实可查；始终带南海诸岛附图。",
    "street_map": "不抓取街道数据：只用你给的 GeoJSON；示意图要加 mock。",
    "then_now": "两个数字口径要一致（同一指标、同一单位）。",
})
CAT["界面"] += ["app_flow", "form_fill", "search_box"]
CAT["屏幕"] += ["cursor"]
CAT["照片"] += ["turntable"]
CAT["人物"] += ["relation_graph", "dialogue", "interview"]
SUIT.update({
    "app_flow": "App 教程、「三步做出……」、新手引导", "cursor": "在截图 / 录屏上指给观众看：点哪里、拖什么、输入什么",
    "form_fill": "「发布前要勾选什么」「这个设置一定要打开」", "turntable": "产品亮相、单品拆解、参数卖点",
    "search_box": "「我搜了一下」、查一手来源", "relation_graph": "谁投资谁、背后都是谁、阵营关系",
    "dialogue": "采访、对谈、两个人的观点交锋", "interview": "访谈 / 播客切片、嘉宾金句",
})
DUR.update({
    "app_flow": "每屏 1.2–1.8 秒（3 屏约 5 秒）", "cursor": "每个动作 0.8–1.2 秒 + 1 秒", "form_fill": "每个字段 0.6–1 秒 + 按钮 1.4 秒",
    "turntable": "4–6 秒", "search_box": "4.5–6 秒（有结果时）", "relation_graph": "每条边 0.5–0.7 秒 + 高亮 1.5 秒",
    "dialogue": "每句 1–1.5 秒", "interview": "4–8 秒（跟片段一样长）",
})
PIT.update({
    "app_flow": "截图和生成页可以混用；tap 是 0–1 的相对坐标；生成页别写真实 App 名字和 logo。",
    "cursor": "path 的坐标是相对原图的（0–1 或原图像素）；静态截图点了不会变，要变化请换成录屏或几张截图。",
    "form_fill": "字段超过 6 个请给 6 秒以上；AI 声明这类开关用 toggle + note 写明平台要求。",
    "turntable": "单张图是伪 3D 摇摆，不是真转；要真转请给多视角 views。抠图（透明底）效果最好。",
    "search_box": "结果写真实标题和网址；示意页面请加 mock；hl 默认取查询里的词。",
    "relation_graph": "金额写清口径和截止时间（src）；不确定的关系用「示意」，别编。",
    "dialogue": "台词要么是真实原话（写 src），要么标 mock「示意对话」；超过 6 句请把时长放到 6 秒以上。",
    "interview": "q / a 要是嘉宾真实说过的话，或标 mock；竖版素材用 focus 选人脸位置。",
})
CAT["类型"] = ["review_card", "news_flash", "deal_card", "next_teaser", "opener", "sponsor_card", "share_card", "poll_card", "clip_style"]
SUIT.update({
    "review_card": "测评、打分、该不该买", "news_flash": "刚刚 / 快讯 / 某公司宣布", "deal_card": "带货、价格对比、限时优惠",
    "next_teaser": "片尾预告下一期", "opener": "系列栏目每期开头 3 秒", "sponsor_card": "口播广告位、恰饭段落",
    "share_card": "结尾金句、可截图转发的结论", "poll_card": "引导评论、你会选哪个", "clip_style": "直播 / 访谈切片包装",
})
DUR.update({
    "review_card": "4.5–6 秒", "news_flash": "4.5–6 秒（滚动条越长越好看）", "deal_card": "4.5–6 秒", "next_teaser": "3.5–5 秒",
    "opener": "3–4.5 秒", "sponsor_card": "4–6 秒（圆环按拍长倒数）", "share_card": "4–5 秒（快门在拍末前 1.1 秒）",
    "poll_card": "4–5 秒", "clip_style": "跟素材一样长（3–8 秒）",
})
PIT.update({
    "review_card": "分数要有出处，没有就写 note: 示意数据；stars: false 关掉星级。",
    "news_flash": "items / ticker 必须是可查的事实并写 src；time 写发布日期，不写就只显示来源。",
    "deal_card": "原价、券、库存如果不是真的就写 note: 示意；countdown 是演示倒计时，不代表真实活动。",
    "next_teaser": "video 封面时页面底色由独立的底色层画出（paint_bg）。",
    "opener": "ep 里第一个数字串会滚动，前后文字照常显示；竖屏不显示 ep 前缀（如「第」）。",
    "sponsor_card": "引导语参数叫 lead（label 是画廊页脚）；广告角标始终显示，不能关。",
    "share_card": "导出单张图用 scripts/share_card.py（3:4 / 4:5 / 1:1 / 9:16）。",
    "poll_card": "result 模式的百分比要真实（写 total 和来源），否则用 ask 模式。",
    "clip_style": "有 line 时本拍的页面字幕被隐藏；不要模仿任何平台的直播界面。",
})
CAT["照片"] += ["logo_wall", "halftone", "meme_stage", "gif_clip", "svg_art"]
CAT["文档"] = ["doc_photo", "slides", "doc_flip", "doc_pick", "handwrite", "email_card", "notice_card"]
SUIT.update({"logo_wall":"这些公司都在用、合作方、投资组合",
"halftone":"老照片、低清截图、档案图",
"meme_stage":"吐槽、一句一张反应图",
"gif_clip":"动图、表情包、短循环",
"svg_art":"图标、插画、品牌色切换",
"doc_photo":"手机拍的文件 / 白板 / 截图证据",
"slides":"PPT、财报会、发布会页",
"doc_flip":"判决书、财报、长文档翻到某页",
"doc_pick":"一叠材料里的关键一页",
"handwrite":"学习笔记、拆解笔记",
"email_card":"邮件证据、offer、通知邮件",
"notice_card":"公告、通知、说明（版式示意）"})
DUR.update({"logo_wall":"4–5 秒","halftone":"3.5–5 秒","meme_stage":"每张 ≥0.6 秒","gif_clip":"3–5 秒",
"svg_art":"4–5 秒（带 swap）","doc_photo":"4.5–5.5 秒","slides":"≤8 页每页 ≥0.6 秒；快翻 4–5 秒",
"doc_flip":"5–6 秒","doc_pick":"4.5–5.5 秒","handwrite":"每行 ≥0.4 秒","email_card":"4.5–5.5 秒","notice_card":"5–6 秒"})
PIT.update({"logo_wall":"只用自己的或虚构的 logo，绝不用真实品牌的标。",
"gif_clip":"转码在构建时做（ffmpeg），GIF 很大时第一次构建慢。",
"svg_art":"自动换色按最深色 → 字色、最饱和色 → 强调色；颜色写在 CSS class 里的 SVG 不会被换色。",
"doc_photo":"自动找角点是启发式（Otsu / Canny 找最大四边形）；背景杂乱时请手动给 corners。",
"doc_flip":"PDF 是节选时用 `of` 写全文页数，否则计数器显示节选的页数。",
"handwrite":"手写字体来自 assets/fonts.json，构建机要能找到字体（设置 H9_MEDIA）。",
"email_card":"示例或虚构邮件必须带「示意」章；界面是中性的，不模仿任何真实邮箱产品。",
"notice_card":"刻意做成普通版式：不要红头、不要公章，保留「版式示意」水印，除非是你自己的文件。"})


def custom_styles():
    """styles made with style_kit.py whose showcase film was published to assets/previews: they join the gallery's style wall."""
    import style_kit
    out = []
    for p in sorted((SKILL / "styles").glob("[!_]*.py")):
        sid = p.stem
        if not (SKILL / "assets" / "previews" / f"{sid}_16x9.mp4").exists(): continue
        lin = style_kit.lineage(sid)
        if len(lin) < 2: continue                      # built-in styles are listed by the gallery itself
        st = style_kit.derive.load_base(sid).STYLE
        title = json.loads(style_kit.showcase(sid).read_text()).get("meta", {}).get("title", "")
        out.append({"id": sid, "name": st.get("name", sid), "fits": st.get("fits", ""), "base": lin[1], "title": title})
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True); DOC.parent.mkdir(parents=True, exist_ok=True)
    CARDS.mkdir(parents=True, exist_ok=True); GALLERY.mkdir(parents=True, exist_ok=True)
    rows, trans = [], []
    seen, carded = set(), set()
    ORIG = {}
    for ex_dir in REELS:
        vj = ex_dir / "video.json"
        if not vj.exists(): continue
        for ob in json.loads(vj.read_text())["beats"]:
            if ob.get("scene") == "fx":
                ORIG.setdefault(f"{ob['fx']}-{ob['preview']}" if ob.get("preview") else ob["fx"], ob)
    for b, reel, reel_v, sid in beats():
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
        rows.append((fx, title.strip(), how.strip(), keys, b.get("label", ""), b.get("ref", ""), key, b.get("band_label", ""), sid))
        if fx in carded: continue
        carded.add(fx)
        src_b = ORIG.get(key, b)               # the example shows the beat as written in its demo reel (original asset paths)
        ex = {k: v for k, v in src_b.items() if k not in ("t", "d", "tr", "label", "ref")}
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
    order = {k: i for i, k in enumerate(ORIG)}          # list cards in demo-reel order, so neighbours come in different styles
    rows.sort(key=lambda r: order.get(r[6], len(order)))
    md = ["# 效果目录 · Effects", "", "每个效果都是 `scripts/h9/aefx.py` 里的一个函数，在 `video.json` 里写成一个 beat：", "",
          '```json\n{"scene": "fx", "fx": "stomp", "words": ["大家", "都在用", "AI"], "t": "@大家"}\n```', "",
          "排名和人气依据见 [`research/ae_popular.md`](../research/ae_popular.md)。横屏、竖屏同一套参数。", "", "## 效果", ""]
    for fx, title, how, keys, label, ref, key, band, sid in rows:
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
        {"effects": [{"id": fx, "file": key, "band": band, "title": title, "how": how, "cat": cat_of(fx), "ref": ref, "label": label, "suit": SUIT.get(fx, ""),
                      "style": sid, "style_name": STYLE_NAMES.get(sid, sid)}
                     for fx, title, how, keys, label, ref, key, band, sid in rows],
         "transitions": [{"id": k, "label": label, "file": name} for k, label, name in trans],
         "styles": custom_styles()}, ensure_ascii=False, indent=1))
    print(DOC, len({r[0] for r in rows}), "effects,", len(rows), "cards,", len(trans), "transitions")


if __name__ == "__main__":
    main()
