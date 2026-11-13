# 更新记录

## 0.18.0 · 2026-11-13
- 新风格 `riso` 孔版印刷：荧光粉 / 蓝 / 黄三块版在暖白纸上套印，网点和套印偏移，叠印圆、网点格、刮板色带、色纸条做图表；示例《名创优品 2024：增长的那一半在海外》。
- 新风格 `yuefen` 月份牌国货：石印卡纸、金线 Art Deco 外框和拱窗，撕页日历、柜台瓶子、铁盒盖、药房天平、火柴盒贴做图表；示例《一瓶白酒的年度账本》。
- 新风格 `editorial` 影像杂志：真实照片 + 巨大衬线标题和数字，四种杂志页面轮流，朱红细线信息图；示例《迅销 2024 财年：优衣库的一年》（照片来自 Unsplash，署名见 `examples/editorial/SOURCES.md`）。
- 新风格 `title` 片头字幕：会呼吸的黑色胶片、颗粒划痕，手刻数字、红线划掉旧值、计数线和胶片格；示例《Netflix 2024：3 亿会员这一年》。
- 新风格 `bauhaus` 包豪斯构成：红蓝黄黑整页轮换，模块搭出的大数字，圆切块、同心环、面积成比例的正方形，形状按 45° 一步步转；示例《宜家降价的一年》。
- 新风格 `thread` 一线长卷：整片一张长纸，一根橙线串起一组组卡片，镜头不切、沿线滑过去，结尾拉远看整条路；示例《小米的 2024：一条线走完年报》。
- 新风格 `teleshop` 电视购物：显像管里的 90 年代购物广告，金箔、红绸、立体金字、爆炸价签和印章，把真实数字当奇迹商品来卖；示例《一锅火锅的年度账本》。
- 新风格 `vapor` 蒸汽波桌面：霓虹日落网格前的 90 年代桌面，每个数装在系统对话框里，报错框、安装向导、进度条、文件列表、画图程序做图表；示例《任天堂 FY2025 账本》。
- 新参数 `meta.silent`（默认 `false`）：无声展示片写 `true`，成片检查不再报静音（dead-air）和响度；五条新示例都开了。
- 新效果 `glyph_sphere` 代码球成字：一团占满画面的旋转代码字符球，在关键时刻飞进数字的真实字形里拼成大字，再换成实心字，剩下的字符绕成一圈光环。
- 新效果 `cube_number` 方块落数：从前上方看的大棋盘上，数字由一列列落下的立体方块搭成（每笔 2 格粗、接触阴影），单位用平面大字；写 `from` 时旧数的方块先沉下去，不编中间数。
- 新效果 `wire_resolve` 线框成形：2–5 张卡片先是发光线框，一道亮线从上往下扫过，扫过的地方变成成品卡片，条形按真实比例。
- 新转场 `anchor_match` 锚点匹配：只留下两拍共有的那个数字 / 元素，飞到下一拍的位置并换上新样子；用 `data-anchor` 或 `tr_anchor` 指定，示例 `examples/fx3/`。
- 八种新风格的自写场景登记进 `form_families.json`，`brief check` 不再报 form-unknown；README、画廊、`references/styles.md` 同步到 26 种风格。

## 0.17.0 · 2026-11-12
- 14 种风格重做画面：`atlas` `chrome3d` `doc` `flat` `ink` `iso3d` `minimal` `press` `papercut` `pixel` `poster` `screen` `sketch` `zine`，各自的示例片和预览重新渲染，说明见 `references/styles.md`。
- 新效果 15 个：物理 `drop_stack` `pour_fill` `topple` `magnet_sort` · 镜头 `dolly_layers` `rack_focus` `orbit_number` · 字效 `word_mosaic` `type_mask` `weight_breath` `unroll` · 数据 `zoom_scale` `small_multiples` · 质感 `ink_reveal` `stamp_press`；示例 `examples/fx2/`，每个都有配方卡。
- 新转场 4 种：`whip_carry` 甩镜带物、`shape_match` 形状匹配、`paper_tear` 撕纸、`paint_wipe` 三笔刷屏，写法同其他转场 `"tr": "paint_wipe"`。
- `bar_race` 改进：竖屏条形用满版面，期数章铺到底边；口播说到某一期时那一期就开始。
- 不出主持人的风格（如 `poster` `flat` `ink` `minimal` `pixel`）真的不放主持人，`host: true` 和落版也不放；要放写 `"host": "force"`，或用 `meta.mascot_mode` 整片指定。
- 字幕：beat 写 `caption_pos: {"bottom", "align"}` 指定这一句字幕的位置；风格可用 `"caption_plate": False` 关掉真人画面上的默认深色底板。
- `key_card` `side_stat` `stack_build` `chip_cycle` 等贴人版式没写 `theme` 时画在风格自己的底色上（之前在深色风格里大字会看不见）。
- 找不到登记的字体时，`doctor`、`style check`、`render` 会写明缺哪款字体、怎么补（`H9_MEDIA` / `H9_FONT_DIRS`）；三维字缺字体时报错说明缺哪个文件。
- 检查更准：字幕对比度按字幕实际所在的位置取样；场景自带的 `at_big` / `at_title` 对时不再误报「大字和口播对不上」；整片一个布景的风格（`atlas` `chrome3d` `iso3d` 等）镜头飞到下一站算一次切换，它们和实拍为主的 `doc` 不再报「相邻版式重复」；字号检查只看当前画幅的规则；`brief check` 认识新效果和各风格自己的场景。
- `stills --settled` 多出一张每个 beat 结束前 0.35 秒的静帧板；`style publish` 渲染时带检查关。
- 竖屏字幕不再压在平台的标题 / 音乐 / 评论栏下：各风格 9:16 的字幕都挪到底部 400 px 以上（`atlas` `doc` `flat` `ink` `iso3d` `minimal` `papercut` `poster` `screen` `sketch` `zine` `studio` `clay`），压在底部的来源行也挪到安全线上方，需要时把画面内容往上让；横屏不变。
- 新检查 `caption-safe`（P0）：按字幕在成片里的真实位置，查 9:16 每页字幕（含动效页上的字幕）是否进了底部 400 px、顶部 200 px 或右下按钮区；`style check`、`brief check`、`render` 前的检查和 `stress.py` 都会跑。
- 不出主持人的风格、以及自己给主持人画框的风格（`screen` 的视频通话小窗），动效页也不再贴主持人小贴纸。
- `doc` `minimal` `screen` `pixel` `press` 竖屏重新排版，所有要读的字都在安全区内；`press` 长输入不再溢出、来源跟着版式走，并新增 1:1 和 3:4 版式；从 `press` 派生的风格默认字幕也在安全区内。
- `style check` 新增安全区扫描：示例片每个 beat 取两帧，页面上要读的字进了平台界面区就算错误（页眉、页码等家具写进 `STYLE["safe_exempt"]` 即可）。动效页的页脚和来源也收进安全区。
- 对比场景 `compare` 竖屏不再让标签压在顶部小标签下面，贴纸避开右下按钮区。
- 竖屏示例片里要读的字全部回到安全区内：`chrome3d` 页眉下移、`sketch` `papercut` `zine` 的大数字和图表让出右下按钮区、`pixel` 日期下移、`atlas` 航线标注只在本段出现、动效页的页脚换成两行。
- `render`：构建检查有错误的风格不再悄悄跳过，会写明原因并以非 0 退出（`--force` 照样渲染）。
- 修正：数字格式化把 1200000 写成「1,200,」、把整数末尾的 0 去掉的问题。
- `clay` 强调色从 `#c2643f` 调深到 `#ad5632`，在陶土底上的对比度达到 3:1。

## 0.16.1 · 2026-11-11
- 修正：`lower3`、`side_stat`、`stack_build`、`strike_fix` 叠在全屏真人画面上时，字原来跟着风格用深色，画面一压暗就看不清；现在这一镜的字自动换成浅色加阴影。排版位置不变，带白卡片的效果（如 `key_card`）不受影响。

## 0.16.0 · 2026-11-11
目标：换一个弱一点的模型来驱动，也能出合格的片子。这些都改成了代码里的默认行为，不靠模型自己记得做。
- 字幕：两种画幅默认都是一句一页（竖屏最多约 14 字），按标点、停顿和词边界断开；没装 jieba 也不会把「国际课程」「A-Level」「3到4」切开，不留 1–2 字的碎页。画面里有真人素材时，竖屏字幕默认加深色底板、用普通粗黑体。「快闪」字幕改成只有明确要求时才用。
- 对口播：清单、步骤、排行、数字卡等效果的每一条，没写 `at` 时自动在说到它的那一刻出现；大字标题比这一镜开头晚说出来时，这一镜自动推迟到说出的那一刻。
- 真人口播版面：竖屏小卡改成人占下方约 55%、图文占上方整宽；需要地方的图文不再压在全屏真人上，人自动挪到小卡或侧边，确实要留在全屏可写 `"presenter_force": true`，这时会压暗画面。竖屏不再用窄侧栏。
- 出镜形式 `meta.presenter.form`：`full` 全屏口播 · `bubble` 圆形头像 · `split` 上下分屏 · `pip` 小窗 · `cutout` 抠像站位。整片选一次，`scripts/h9/presenter.py preview` 用自己的素材出一张对比图。
- 缺内容直接报错：`chip_cycle`、`action_card`、`stamp_compare`、`chat` 没给内容时不再画灰色占位条或默认文案；要占位动画须写 `skeleton: true`。
- `hat9.py render` 先跑分镜检查，有 P0 就不渲染（`--force` 可跳过）；渲染完自动出每秒 2 帧的检查图，检查字幕碎片、音画偏差、字压脸、字太小、对比度，有 P0 时退出码非 0。没写 `meta.style` 时用 press 出一条，不再把所有风格都渲一遍。
- `hat9.py doctor` 会提示安装 jieba 和 faster-whisper。

## 0.15.1 · 2026-11-11
- 整片流程第一步改成「先定口播」：首选用户自己出镜的口播视频，它同时是声音和画面主体；只有录音或文案时，先问要什么口播形象。
- `audio_tools.py cut` 支持视频进、视频出：画面和声音在同样的时间点剪，口型不错位；`--voice` 同时写出剪好的声音给 `meta.voice` 用。
- `references/presenter.md` 新增「真人口播视频」完整步骤：降噪 → 逐字时间 → 剪口误 → 设成常驻主体。

## 0.15.0 · 2026-11-07
- 新参数 `meta.channel`：页眉、落版、名牌上印的频道名。不写就用 `meta.title`。之前各风格的页眉里写死了一个固定名字。
- 示例里的频道名、口号和主持人都换成中性的：频道名统一叫「示例频道」，主持人换成代码绘制的卡通形象 `assets/host.webm`。像素风的主持人改成一个小机器人。
- 示例配音结尾那句固定的收尾词剪掉了，落版接在口播之后。
- 所有展示片、效果预览、字体样张按新示例重新渲染。
- 去掉 `research/` 文件夹；动效人气数据移到 `references/ae_popular.md`。

## 0.14.4 · 2026-11-07
- 修正：设了 `meta.caption_style` 的 `cap-bottom` 以后，字幕位置以它为准。之前瑞士海报等风格会把字幕钉在自己的位置（左对齐、离底 540 px）。
- `montage` 新参数 `zoom`（如 1.45）：每段素材从顶部放大，素材里自带的字幕会被推出画面，不和片子的字幕打架。

## 0.14.3 · 2026-11-07
- 新参数 `meta.caption_style`：直接指定字幕的 token（位置、字号、字体、底板颜色……），优先于风格和字幕预设。一条片子里换了好几种风格，字幕也能保持同一个样子。
- 单个 beat 写 `"caption": false`，这段就不出字幕：适合画面上已经写着同一句话的时候，避免字幕和画面重复。

## 0.14.2 · 2026-11-07
- 长片按章换风格：`scripts/longform.py` 里，章节开头的 beat 写 `"style": "ink"`（或 `chapter: {"style": ...}`），这一章就用这个风格出，其余章用默认风格，章与章之间硬切。
- 修正：主体（如卡通主持人）`hidden` 时，竖屏画面不再被压在上半屏的小框里，效果重新铺满整个画面。
- 修正：`longform.py` 不再把 beat 的时长 `d` 当成时间点平移（之前写了 `d` 的 beat 会变成负时长）；`"at": [t1, t2]` 这类时间列表也会随章节平移；配乐路径支持 `$H9_MEDIA`。
- 新参数 `frame_fit: {scale, x, y}`：单个 beat 的画面整体放大、平移，填满竖屏空白；不影响效果自己的抖动和推镜。
- `stomp` 第三个词改成强调色底上的实心字，并停到这一拍结束（之前是空心描边，底色还会提前退回）。

## 0.14.1 · 2026-11-07
- 版式示例和文档里的数字、文案全部换成九帽动效自己的事实（174 个动效、18 种风格、7 天 15 个版本、把仓库地址发给 Claude Code / Codex / Cursor），`key_card`、`side_stat`、`chip_cycle`、`strike_fix` 的默认值也改成中性的；对应的预览动图重新生成。
- 新检查 `number-repeat`（P1，review / brief check）：相邻两个 beat 都是「一个大数字 + 小字」（`key_card`、`side_stat`、`odometer`、`number` 场景、`scan_field`、`mosaic_number`、`seat_swarm`、`glass`、带数字的仪表盘等）就提醒换一种载体。名单在 `form_families.json` 的 `number_hero`。

## 0.14.0 · 2026-11-06
- 同一个重点，换着载体说：新增 7 个贴着主体的版式（`stack_build` 字逐行叠出 / 名片、`side_stat` 侧贴数字、`key_card` 信息卡放大、`stamp_compare` 截图标注对比、`strike_fix` 删除线改口、`chip_cycle` 步骤 + 标签轮换、`action_card` 可截图的结尾行动页）和 7 个把数字变成画面的效果（`mosaic_number` 作品拼数字、`seat_swarm` 空位涌入、`dial` 仪表 / 24 小时钟、`log_scroll` 日志滚动、`one_to_many` 一变一群、`scan_field` 扫描清除、`card_fan` 卡片扇形）。每个都跟着风格换皮，有的连结构一起变（暗场是细线仪表，海报是实心扇形，水墨是一笔弧）。
- 主体层 `meta.presenter`：真人、录屏或卡通形象常驻画面，每个 beat 写 `presenter: full / card / side / corner / hidden`，在镜头之间平滑换位置、视频不断，效果自动排在空出来的区域里；字幕自动垫底色，压在任何画面上都看得清。见 `references/presenter.md`。
- 章节外框 `meta.device`：相机 / 浏览器 / 手机外框贯穿全片，beat 写 `chapter: {label, bg}`，换章时模式名和底色一起换。见 `references/device.md`。
- 版式多样性检查（review / brief check）：每个效果归到一类版式；相邻两个 beat 同一类、全屏大字超过 25%（超过 40% 判 P0）、60 秒以上少于 5 类版式都会报出来。

## 0.13.0 · 2026-11-06
- 新风格 `minimal` 极简讲述：暖白纸 / 深炭灰底 + 剪影插画，一条细蓝线贯穿全片（地平线、钟面、坐标轴、柱子轮廓、划线都是它），斜体衬线只给每屏一个重音词；示例《棉花糖实验，测的真是自控力吗》（Mischel 1972、Shoda 1990、Kidd 2013、Watts 2018）。
- 配乐卡拍：配乐旁有 `.beats.json` 时，换画面、转场、音效和冲击帧自动吸到节拍上（不挪到口播词之前）；片中快切 `"fx": "montage"`（每刀卡拍、每段自动挑最好看的一秒）；说话时配乐压低、无人声段自动推上来；渲染自动标准化到 -14 LUFS；review 新增卡拍 / 音画 / 配乐压低检查。
- 讲产品只用真实界面：`scripts/ui_capture.py`（网址 → 真实组件 2 倍截图 + ui.json + 现成 beat，竖屏抓手机版）和 `ui_lift` 组件出框效果。
- craft_lint 加工作室规矩：字体过多、强调色过多、全片都是淡入、渐变底居中标题、占位标签。
- 修正：两个同名素材文件构建时不再互相覆盖。

## 0.12.0 · 2026-11-03
- 导演关卡都有了命令：`hat9.py brief new / check`（需求单模板；渲染前查分镜：开场是不是纯文字、一个画面撑太久、纯文字画面占比、大字重复字幕、效果重复）、`hat9.py stills`（每个 beat 一张静帧，带口播排成板）、`hat9.py sample --range`（几秒的动画小样，带声音，不用整片渲染）。
- `hat9.py montage`：快切卡在音乐节拍上；每段自动挑画面完整、没有转场、略有动作的一秒；每刀必须写明对应哪句话；可直接放进成片。
- `hat9.py refs`：从参考片量节奏、每个镜头抽一帧排成带编号的参考板、可选逐字稿，生成原则表。
- `hat9.py review` 新增响度 / 峰值、空白、和参考片比节奏（`--ref`），以及交付关 `--gate`（六项都打分且 ≥ 8、没有 P0 才放行）。

## 0.11.0 · 2026-11-03
- 导演手册 `references/director.md`：需求单（一句话片子、节拍表：前 2 秒钩子、每 3–5 秒一个视觉爆点）、关卡流程（规划 → 静帧 → 小样 → 整片 → 打磨 → 声音 → 渲染 → 自检）、画面硬规矩（大字不重复字幕、不做 PPT 大字报、不静止超过 2.5 秒、手机可读、快切卡拍）、打分自检循环、从参考视频学风格的方法。
- `scripts/review.py`（`hat9.py review`）：成片出每秒 2 帧的静帧板，自动查静止过久、前 2 秒无变化、切换间隔、纯色大字报占比、大字只重复字幕、同一效果用太多，并生成打分表。

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
- 引擎：video.json → HyperFrames；`"@关键词"` 对准口播；标注、字幕、主持人形象。
