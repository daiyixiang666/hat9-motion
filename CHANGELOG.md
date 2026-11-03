# 更新记录

## 0.10.0 · 2026-11-03
- 自定义风格：`hat9.py style new <id> --from <风格>` 从任一风格派生。默认只改颜色、字体、动效页底色、质感层和 CSS，其余全部继承底稿（`BASE = "ink"`）；`--copy` 整份复制，连场景代码一起改。
- `style preview`（示例片 + 动效片的静帧拼图，或 `--render` 出片）、`style check`（字体、对比度、横竖屏构建）、`style publish`（示例片放进画廊，风格墙自动多一格）。

## 0.9.0 · 2026-11-02
- 动效跟着风格换皮：动效页面的四种底色从风格配色推出来（`STYLE["fx_themes"]` 可以自己定），风格可以用 `FX_FRAME` 画自己的动效页面。`press` `poster` `zine` `screen` `hud` `doc` `papercut` `sketch` `ink` `flat` `pixel` 都有了各自的版本。
- 画廊：风格墙（点一种风格，播它的示例成片、只看这个风格的动效）、按风格筛选、每张卡标出风格；138 个动效卡改用最合适的风格演示（`scripts/style_reels.py`）。
- 修正：竖屏拼贴不再压到字幕下面；竖屏转台标注不再撞字幕；「·」不放在行首；图表标注离画面边缘留出边距。

## 0.8.1 · 2026-11-02
- 新字体 `fusion-pixel` 缝合像素（中文像素字，`pixel` 风格改用它）和 `lxgw-marker` 霞鹜漫黑（马克笔手写，`sketch`、`zine` 改用它），共 60 款。

## 0.8.0 · 2026-11-02
- 新风格 8 种，各带一条横竖屏示例成片：`papercut` 剪纸、`sketch` 手绘白板、`ink` 水墨国风、`zine` 拼贴杂志、`flat` 扁平插画、`pixel` 像素复古、`iso3d` 等距微缩（Three.js）、`chrome3d` Y2K 镀铬（Three.js）。
- 字体扩到 58 款，按类别、用途、气质打标签；`references/fonts.md` 和在线字体样张。
- 字幕：数字里的小数点不再断页（4.8、14.6）；书法字体的字形轮廓可以直接读取。

## 0.7.0 · 2026-11-01
- 新效果 58 个：音视频（`pip` `freeze_frame` `speed_ramp` `footage` `audio_quote` `podcast` `talking_head` `host_point`）、文字（`text_pages` `question_card` `vertical_title` `flying_words` `number_pages` `combo` `black_slam` `scribble` `scanline`）、图表与地图（`icon_unit` `scatter` `funnel` `radar` `then_now` `choose_one` `converge` `gantt` `decision_tree` `area_overlay` `map_timeline` `street_map`）、图片与文档（`logo_wall` `halftone` `meme_stage` `gif_clip` `svg_art` `doc_photo` `slides` `doc_flip` `doc_pick` `handwrite` `email_card` `notice_card`）、界面与人物（`app_flow` `cursor` `form_fill` `turntable` `search_box` `relation_graph` `dialogue` `interview`）、片子类型（`review_card` `news_flash` `deal_card` `next_teaser` `opener` `sponsor_card` `share_card` `poll_card` `clip_style`）。
- 交付：1:1 / 4:5 / 3:4、`meta.ai_label`、`caption_preset`、`brand`、`series`、多语言、`breath`、`rate_adapt`、音效冲击、情绪切换；`cut_list.py`、`ref_pacing.py`、`export_edit.py`（FCPXML）、`longform.py`、`share_card.py`、`audio_tools.py`。
- 日文、韩文、阿拉伯文、希伯来文字体（可选）；上下标。

## 0.6.0 · 2026-10-31
- 新效果 50 个（`scripts/h9/fx/`）：`media`（按张数换编排，1–2000 张，可混视频）；引用 `cite_pdf` `cite_paper` `cite_article` `cite_quote` `cite_post` `cite_video` `cite_stack`；结构 `list_stack` `steps` `ranking` `term_card` `word_swap` `pros_cons` `quadrant` `countdown` `chapter_bar`；数据 `table` `statement_table` `waterfall` `scale_compare` `bar_race` `stacked_bars` `formula` `bars_csv` `line_csv`；屏幕 `scroll_shot` `screencast` `spotlight` `code`；社交人物 `comment_thread` `im_chat` `profile_card` `equity_tree` `china_map` `danmaku` `receipt`；节奏 `breather` `interlude` `suspense` `cold_open` `beat_cut` `reaction` `loading` `think_loop` `chapter_breather`。
- 流水线：弹性时长；`meta.lead` / `gaps` / `duck` / `speakers` / `caption_tr`；卡拉 OK 字幕；`scripts/align.py`（录音对齐）、`scripts/cover.py`（三比例封面）、`scripts/url_brief.py`（网址出片）、`scripts/h9/data.py`（CSV / Excel）。
- 压力测试加入竖屏安全区和时长维度；`scripts/craft_lint.py` 检查常见的 AI 默认手法；`scripts/design_md.py` 导入 DESIGN.md 品牌规范。
- Claude Code 插件安装（`.claude-plugin/`）。

## 0.5.0 · 2026-10-31
- 新风格：`screen` AI 工具台、`atlas` 地图纪录、`doc` 实拍纪录、`poster` 瑞士海报，各带一条示例成片。
- 新动效：`earth_zoom` `map_route` `bars` `line_draw` `donut` `timeline` `chat` `hud_lock` `glass` `text_mask`（`scripts/h9/fx/`，一个效果一个文件）。
- 素材自适应：文字长短、列表条数、图片张数和比例、部分效果支持视频（`scripts/h9/fit.py`）；压力测试 `scripts/stress.py`；参数范围见 `references/inputs.md`。
- 字幕：句末标点总是断页。

## 0.4.0 · 2026-10-31
- 示例重做：《一杯 4 块钱的柠檬水》（`press` 财经刊风格）；动效库每个效果都放在真实口播页面里演示。
- `scripts/music.py` 合成背景音乐；`scripts/hero.py` 生成首页动图和网页版成片。

## 0.3.0 · 2026-10-31
- AE 动效库：28 个效果 + 12 种转场，横竖屏同一套代码。
- `hat9` 命令行（doctor / quick / plan / build / render / fx / styles / pack）；在线画廊、配方卡、SRT 字幕导出。

## 0.2.0 · 2026-10-31
- 三维引擎：立体中文字、PBR 材质、景深；`studio`、`clay`、`hud` 风格。

## 0.1.0 · 2026-10-31
- 引擎：video.json → HyperFrames；`"@关键词"` 对准口播；标注、字幕、柴犬主持人。
