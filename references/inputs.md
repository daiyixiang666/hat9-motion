# 输入范围：每个效果、每个场景能吃什么素材

素材不会总是刚好合适：字有长有短，条目有多有少，图片有横有竖，有时还是一段视频。这里写清楚每个参数能接受什么，以及超出范围时会发生什么。所有规则都在构建时（Python）算好，渲染结果每次都一样。

实现见 `scripts/h9/fit.py`，验证见 `scripts/stress.py`（每个效果、每个场景都用极端输入横竖屏各跑一遍，结果写在 `examples/stress/report.md`）。

## 通用规则

### 文字（所有标题、标签、字幕）

- **能写的形式**：字符串；`"第一行|第二行"`（`|` 是强制换行）；或字符串列表（等同于用 `|` 连起来）。`*强调*` 在换行后依然成对保留。
- **排版顺序**（`fit.fit_text`）：
  1. 先在一行里放到尽量大，但不超过这个元素的最大字号；
  2. 放不下时，按词换行，最多到这个元素的行数上限。用 jieba 分词，词不会被拆开；标点不会出现在行首；多一行必须换来大 25% 以上的字号才值得；
  3. 到了最小字号还放不下，最后一行才加省略号「…」。
- **字宽估算**：汉字 1em；拉丁大写字母和数字 0.64em，小写字母 0.54em，空格 0.28em；等宽字体中英文统一按 0.6em 算。实际排版会再留 4% 的余量。
- 下表里的 **「字」**，指不超过这个长度时版式和默认一样，超出后开始缩小或换行。

### 图片和视频

- 任何比例都可以（横、竖、方、全景）。
- 默认按 `object-fit: cover` 铺满，可以用 `focus` 指定焦点，避免主体被裁掉：写 `"30% 40%"`、`[30, 40]` 或 `{"x": 30, "y": 40}` 都行。
- 只有当图片比例和画框相差 3.4 倍以上时（比如 4:1 全景放进竖屏），才改为「模糊铺底 + 完整原图」。依赖坐标的效果（视差、穿梭、标注）始终用铺满，因为坐标指的是画面位置。
- **视频**：凡是标注了「支持视频」的参数，都可以直接给 `.mp4`、`.mov`、`.webm`、`.m4v`。视频会作为计时的媒体层放在效果下面，和其他媒体一样逐帧对时。`video_start` 设置从原片第几秒开始取。

### 列表

- 字符串、`a|b|c`、列表都可以。
- 超过上限的部分会被截掉。上限写在下表里。

## 效果（`scene: "fx"`）

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `pop` `apple_blur` `flip3d` | `text`、`sub` | 1 字到一整句；最多 3 行；默认字号 15vmin | 缩小字号并换行；逐字错开的总时长不超过本拍时长的 45% |
| `mask_up` | `text`、`sub` | 最多 4 行，`|` 强制换行 | 同上 |
| `tracking` | `text`、`sub`、`spread` | 最多 2 行；每行围绕自己的中心收拢 | 字越多，散开的距离越小 |
| `blur_focus` | `text` | 有空格时按空格分词，没有空格时用 jieba 分词；最多 3 行 | 出现顺序用固定种子打乱，每次渲染都一样 |
| `typewriter` | `text` | 等宽字体，最多 4 行 | 打字速度自动加快，在本拍 70% 的时间内打完 |
| `scramble` | `text`、`pool` | 等宽字体，最多 3 行 | 每格解码时间按字数压缩 |
| `write_on` | `text` | 最多 3 行；手写体描边后填色 | 画布随最长一行变宽，最宽 86%，高度不超过 64% |
| `slice_text` `shine` `glitch` `impact` `neon` | `text`（`impact` 另有 `sub`） | 最多 3 行 | 缩小字号 |
| `burst` | `text` | 最多 2 行，放在放射线中间 | 缩小字号 |
| `diffuse` | `text`、`sub`、`colors` | `colors` 1–5 个 | 只取前 5 个 |
| `ghost_type` | `ghost`、`text`、`sub` | 背景字 1–10 字（字越多字号越小，可以出血）；前景字最大 7vmin，最多 3 行 | 背景字按设计允许溢出画面 |
| `lockup` | `text`、`sub`、`notes` | `notes` 0–4 条：横屏放在四个角，竖屏排在标题下面 | 只取前 4 条 |
| `odometer` | `value`、`unit`、`sub`、`zh` | 整数、小数、负数，字符串原样显示；数字自动加千分位；`zh:true` 时换算成万、亿 | 位数越多，字号越小 |
| `stomp` | `words` 或 `text` | 1–12 个词；长词自动拆成 2 行；只给 `text` 时自动分词 | 只取前 12 个；每个词的节拍自动压缩 |
| `notify` | `items` | 1–6 条，写法任选：`"应用：消息"`、`[应用, 消息]`、`{app, text}`；消息最多 2 行 | 整组按高度等比缩小；超出 2 行显示省略号 |
| `triple` | `labels`、`icons` | 1–5 个，图标依次是点赞、投币、收藏、转发、评论 | 图标和间距按个数缩放 |
| `lower3` | `text`、`sub` | 名字 1 行，最大 7vmin；身份说明最多 2 行 | 缩小字号 |
| `cartoon` | `text` | 最多 2 行 | 缩小字号 |
| `gooey` | `labels` | 0–2 个词，跟着两个球一起移动 | 缩小字号 |
| `callout` | `image` 或 `video`（支持视频）、`focus`、`x`/`y`/`text`/`sub`，或 `points: [{x,y,text,sub}]` | 1–4 个标注点；点在画面右侧三分之一时标签朝左，在顶部时朝下；标签字号按长度缩小 | 只取前 4 个点 |
| `plate` | `image` 或 `video`（支持视频）、`focus`、`text` | 任何比例；文字最多 3 行 | 极端比例改为模糊铺底 |
| `parallax` | `plate`/`image`/`video`（支持视频）、`fg`（可选的透明抠图）、`text`、`focus` | 标题最多 2 行，夹在两层之间 | 有 `fg` 时始终铺满，保证抠图对位 |
| `portal` | `image`/`video` → `image2`/`video2`（都支持视频）、`x`、`y`、`focus`、`focus2` | A、B 可以是任何比例 | 始终铺满（洞的位置是画面坐标） |
| `mosaic` | `images` | 1–24 张，任何比例。不到 12 张时，铺 12 格并换着裁不同局部；12 张以上每格一张，网格按张数重排；最后推进到中间偏右的一格 | 只取前 24 张 |
| `collage` | `images`、`text` | 1–9 张，每张保持自己的比例（普通横图统一印成 3:2）。1–3 张用设计好的错落版式，4 张以上用带抖动的网格 | 只取前 9 张 |
| `match_cut` | `images`、`text` | 0 到任意多张，轮流使用；文字最多 2 行，最大 20vmin | 没有图时只切色块和字体 |
| `dual` | `img_h`、`img_v`（缺一个就两边用同一张）、`focus`、`text` | 任何比例 | 铺满裁切 |

**每一页的语境层**（`line`、`topic`、`src`、`host`）：
- 字幕 `line` 最多 2 行，横屏从 40px、竖屏从 44px 开始缩小，最小到 28px；
- 页脚的出处过长时显示省略号。

**插件效果**（`scripts/h9/fx/*.py`，由效果作者维护）：输入范围写在各自的文件和交接说明里。`python3 scripts/stress.py --plugins` 会用 `examples/aefx/variants.json` 里的变体测试它们。

## `press` 财经刊的场景

| 场景 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `hook` | `price`、`value`、`unit`、`unit2`、`item`、`item_en`、`kicker`、`sub` | `price` 任意短串（¥4、$19.9）；`value` 整数、小数或字符串，计数器的小数位与原值一致；`item` 最多 2 行；`sub` 最多 2 行 | 数字按位数缩小，单位按长度缩小 |
| `stores` | `a{name,n}`、`b{name,n}`、`per`、`rows`、`unit`、`diff`、`legend`、`per_label`、`title` | 任意两个数（12 对 3000、850 对 920、百万级都可以）。点的单位自动取 1/2/5×10ⁿ，使点数落在 40–640 之间；行数自动定；多出来的列在较大的一方点亮；差值自动算出 | 标题限 1 行（缩小到 40px，再长才加省略号）；名字和数字按块宽缩小 |
| `turn` | `q`、`pre`、`struck` | 任意长度。放不进一行时，`pre` 和被划掉的部分各占一行；`q` 最多 2 行 | 缩小字号 |
| `split` | `pct`（0.1–99.9）、`items`（1–5 个，`[图标, 字]` 或只写字）、`pl_pre`、`pl`、`pl_sub`、`total`、`small{q,label,tag}`、`title` | 小数位与原值一致；小的那段可以是任何宽度，推进镜头始终对准它的中心；`pl` 和 `label` 最多 2 行；红条太窄放不下 `total` 时省略不画 | 标签字号按总宽度缩小；竖屏标签可以折成两行 |
| `chain` | `nodes`（3–7 个，每个 `{name, sub, icon}`）、`hot`、`title`（`a||b` 表示两句交替出现）、`bracket` | 节点大小和间距按个数计算；名字按间距缩小 | 只取前 7 个 |
| `wheel` | `stations`（3–6 个）、`big`、`q`、`sum`、`center` | 站点等分圆周；彗星依次经过 `at_more`、`at_mat`，之后每站隔 0.75 秒；`big` 最多 2 行；`sum` 最多 4 行，位置跟着 `big` 下移 | 只取前 6 个 |
| `thesis` | `l1`、`em`、`l2`、`struck` | `l1` 横屏最多 2 行、竖屏最多 3 行，`em` 的红色底条跟着换行；`l2` 最多 2 行，位置跟着 `l1` 下移 | 缩小字号 |
| `outro` | `title`、`sub`、`cta` | `title` 最多 2 行，`sub` 和 `cta` 位置跟着下移 | 缩小字号 |

**镜头**：每一页都有推拉调度。推镜幅度上限 1.08，同时以不吃掉左右边距为限（竖屏约 1.03，横屏约 1.065）；页面最上面的小标题不会滑到页眉线下面；左右边距始终留在画面里。

## `poster` 瑞士海报的场景

| 场景 | 参数 | 接受的范围 |
|---|---|---|
| `hundred` | `pre`、`big`、`count`、`en` | `count` 任意整数，补零位数跟着位数走；`big` 最多 3 行，高度不会压到矩阵；`en` 在本栏内换行 |
| `problem` | `big`、`q`、`claim`、`strike` | `big` 最多 2 行；`claim` 最多 3 行，被划掉的部分在哪一行都能找到 |
| `quote` | `year`、`who`、`who_sub`、`q1`、`q2`、`q3`、`en` | 年份可以是任何短串；引语逐行按栏宽缩小；英文原文最多 5 行，缩到页脚时自动算出缩放比例 |
| `price` | `left`、`right`（各为 `[词, 说明]`） | 两栏用同一个字号，按较长的一侧缩小 |
| `keep` | `frames`（2–36）、`keep_i`、`a`、`b` | 帧网格按数量取 3、4 或 6 列；计数器跟着帧数走 |
| `thesis` | `big`、`rest`、`mo` | `big` 最多 2 行，不会压到 `rest`；`rest` 最多 3 行 |
| `outro` | `title`、`sub`、`mo` | 按整栏宽度缩小 |

## 0.6 新增效果

每个效果一个文件，在 `scripts/h9/fx/`。各示例文件夹里的 `variants.json` 是故意换了输入的样例；`python3 scripts/stress.py --plugins` 会把它们和 `examples/stress/targets/*.json` 一起跑一遍。

### 按数量换动效 `media`

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `media` | `items`（图片路径、视频路径或 `{src|video, caption, focus, fit}`，可混放）· `hl` · `t_hl` · `count_label` | 0 到 2000 张，任意比例。0 张：骨架占位；1 张：整屏推进（比例不合时变成卡片压在自身模糊底上）；2 张：斜切对决 + 滑杆；3 张：发牌、扇开、拎出一张；4–6 张：杂志式拼版；7–24 张：照片墙拼合、平移、飞向高亮那张；25–99 张：马赛克翻转 + 推镜 + 焦点转移；100 张以上：从一张图拉远成一片画海 + 计数器 | 1–24 张时视频真实播放（7–24 张默认同时播 6 段）；25 张以上视频显示静帧；100 张以上用构建时拼好的缩略图集 |

### 引用 `cite_*`

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `cite_pdf` | `pdf`、`page`（或按 `quote` 自动找页）、`quote`、`box`、`cite` | 真实 PDF（需要 PyMuPDF）；引文按原文定位，可跨行；扫描件用 `box` 手动框 | 找不到原文时报错并列出候选页 |
| `cite_paper` | `title`、`authors`、`venue`、`year`、`id`、`abstract`、`hl`、`figure`、`cites` | 作者 1–50+ 人，太多时显示前几位 + 「等 N 人」；摘要高亮一处 | 标题最多 3 行 |
| `cite_article` | `outlet`、`headline`、`dek`、`byline`、`date`、`excerpt`、`hl`，或 `image`（截图）+ `box` | 字段排版或截图滚动高亮；媒体名只显示文字 | 摘录过长时滚动到高亮处 |
| `cite_quote` | `quote`、`translation`、`name`、`role`、`source`、`date`、`portrait` | 一句话到一段；中英双语；没有头像时用首字母章 | 引语按长度缩小字号 |
| `cite_post` | `name`、`handle`、`text`、`time`、`counts`、`avatar` | 平台中立的帖子卡；互动数自动换算万 / 亿 | 正文最多 8 行 |
| `cite_video` | `video`、`title`、`source`、`tc`、`caption` | 横屏或竖屏视频，真实播放；进度条和时间码 | 片段比拍短就停在最后一帧 |
| `cite_stack` | `sources`（1–5 个）、`verdict` | 每个信源可标一致 / 不符 / 存疑 | 超过 5 个折叠 |

### 结构

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `list_stack` | `items` · `title` · `style` | 1–14 条（16:9 超过 5 条、9:16 超过 7 条分两栏），每条 1 字到一句，同一字号最多 2 行；"要点：说明" 自动拆成主行 + 小字 | 超过 14 条截断；标题从中间大字缩成角标 |
| `steps` | `items` · `title` · `hl` | 2–12 步，6 步以内一行（竖屏一列），之后蛇形两行（两列），连线绕开标签 | 标签最多 3 行、说明 2 行，同一字号 |
| `ranking` | `items`（第 1 名在前）· `unit` · `hide_top` | 2–15 条（16:9 超过 8 条、9:16 超过 10 条分两栏）；数值可有可无，全都有才画条；百万以下显示精确值并滚动计数，百万以上用万/亿 | 第 1 名先翻成问号卡，再翻开 |
| `term_card` | `term` · `reading` · `pos` · `definition` · `example` · `source` | 术语 1–14 字（1–2 行），释义最多 4 行（*关键词* 被马克笔划出），例句最多 2 行 | 只有术语也能成页 |
| `word_swap` | `pre` · `words` · `post` · `mode` | 2–8 个词，长短不一（槽位随词变宽）；整句放不下时前半句单独一行；`replace` 为「不是 A，是 B」 | — |
| `pros_cons` | `pros` · `cons` · `labels` · `verdict` | 每边 1–8 条，两边可以不一样多；横屏左右、竖屏上下 | 结论最多 2 行 |
| `quadrant` | `items`（x、y 为 0–100）· `x_axis` · `y_axis` · `quads` · `hl` | 1–12 个点，标签自动避让点、轴线和轴标签 | 象限名放在图外四角 |
| `countdown` | `from` · `to` · `question` · `reveal` | 2–12 下，问题和答案最多 2 行 | 不给 `reveal` 就停在最后一个数字 |
| `chapter_bar` | `chapters` · `hl` · `now` | 2–8 章，标题最多 2 行；横屏一条进度条，竖屏竖轨 | — |

### 数据和表格

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `table` | `rows` 或 `csv`+`cols`+`limit`；`title` `note` `hl_row`（序号或首列文字）`hl_col`（序号或表头）`hl_cell` [r,c] `t_hl` `compact` `paren` `transpose` `max_rows` | 2×2 到 8×12+；数字列自动识别、右对齐、逐个计数；单列 ≥10 万自动换 万/亿 并写进表头；负数 −x（`paren`: (x)）；% 保留；文字 1 字到短语 | 字号按框解出（最小 1.5vmin）；超过 `max_rows`（横 10 / 竖 12）折成「…还有 N 行」，高亮行保留；竖屏宽表自动转置 |
| `statement_table` | `items` [[科目, 值或[值…], kind, 同比]] 或 dict（`indent`）或 `csv`（首列科目，每期一列，可选 kind 列）；`cols` `title` `period` `unit` `hl` `hl_note` `t_hl` `dec` | 2–16 行；1–3 期；kind = line / sub（单线小计）/ total（双线合计）；负数记作 (x)；同比列可选 | 超过 16 行截断；字号按行数缩（最小 1.4vmin）；竖屏备注挂到卡片下沿 |
| `waterfall` | `steps` [[名, 值, kind]]（start / delta / sub / end；sub、end 值可空=自动算）或 `csv`+`x`+`y`（空格=自动合计，可选 kind 列）；`unit` `dec` `title` `note` `readout` `orient` `compact` | 3–12+ 步；正负步；小计任意位置；跌破零；大数自动 万/亿 | 步多或标签长（横 >9、竖 >6）自动改横向瀑布 |
| `scale_compare` | `mode` laps / units / area；`ratio`（或 `value`+`ref_value`）`head` `ratio_label` `basis` `method` `icon`（container field earth building car person cup phone box ship plane dam coin）`a_label` `b_label` `unit_name` `dec` | ratio 0.01 到 10 万+ | units：>120 个时每个图标代表 ×10/×100 并加图例；laps：最多画 24 圈并注明；area：小方块最小 1.2vmin 仍可见 |
| `bar_race` | `labels`+`series` {名:[值…]} 或宽表 `csv`（首列时间；`transpose`: 实体在行）；`top` `hl` `unit` `dec` `title` `note` `compact` | 2–12 个实体、2–20 个时间点；负值按 0；大数 万/亿 | 超过 `top`（横 10 / 竖 8）的在下方等待，升进来时滑入；时间预算平分到每一步（移动 62% + 停留） |
| `stacked_bars` | `labels`+`series` 或宽表 `csv`+`series_cols`；`hl` `percent` `unit` `dec` `title` `note` `orient` `total_col` / `totals` | 2–12 个类别、2–6 个系列；100% 堆叠；段内数字放得下才显示 | 类别多或标签长自动横排；超过 6 个系列截断 |
| `formula` | `lhs` `terms` [[名, 值]] `ops` `result` `unit` `dec` `note` `t_flip` `t_result` | 1–5 项，任意运算符；结果为数字（计数）或文字 | 一行放不下（或竖屏）时左边单独一行 |
| `bars_csv` | `csv` `x` `y` + `bars` 的全部参数；`sort`（desc/asc/keep）`limit` `scale` | 任意两列表 | 类别不是时间（品牌、城市）默认从大到小并高亮第一（不出增长角标）|
| `line_csv` | `csv` `x` `y` + `line_draw` 的全部参数；`limit`（最后 N 行）`scale` | 任意两列表 | — |

### 截图、录屏、代码

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `scroll_shot` | `image`、`stops`、`frame`、`toc` | 长图 1:1–1:20、横图都行；停点 0–8 个，可按标题 / 找字 / 坐标；标签任意长 | 超过 16000 px 自动缩小；滚不动的图改为推近到停点；不给停点就匀速滚完 |
| `screencast` | `video`、`clicks` 或 `clicks_json`、`steps`、`hl` | 横竖录屏；点击 0–12 次；步骤 0–8 条 | 没有点击就慢推；点击间隔超过 2.6 秒先拉远再推近；录屏比拍短就停在最后一帧 |
| `spotlight` | `image` 或 `video`、`boxes`、`frame` | 任意比例；聚光框 1–8 个，矩形或圆形；标签一行 | 没有框就慢推；标签自动上下翻、贴边收回 |
| `code` | `code` 或 `file`、`mode`、`hl`、`cmd`/`output` | 1–60+ 行；每行约 110 列以内（中文算 2 列）；python / js / bash / json / css / html | 行多就跟着光标滚动，最后滚到高亮行；超长行在右侧淡出；字数过多自动从逐字打出改为逐行出现 |

### 社交、人物、中国地图

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `comment_thread` | `items`, `total`, `hl` | 1–20 条，每条 1 字到一段（≤4 行后省略），每条 0–3 条回复 | 超过面板高度自动滚动并保持最新一条在视野里；热评默认取 hot 或点赞最多 |
| `im_chat` | `messages`, `title`, `read` | 2–30 条；文字、语音（秒）、图片、撤回、时间；多人自动显示名字 | 超出窗口自动上滚；两三句时窗口收紧 |
| `profile_card` | `people` 或 `name`/`role`/`bio`/`avatar`/`stats`, `follow`, `hl` | 1–6 人；名字 1 字到长英文名；简介 ≤3 行；0–4 个数字 | 1 人大卡，2–3 人并排，4–6 人网格；数字自动滚动（保留千分位） |
| `equity_tree` | `root`, `holders`, `subs`, `mode`, `hl`, `summary` | 每层 1–8 个，2–4 层；比例可缺省 | 名字自动缩放到节点；`mode:"org"` 变组织架构 |
| `china_map` | `highlight`, `values`, `dots`, `points`, `focus`, `hl` | 1–34 个省；任意子集的数值；撒点几颗到约 600 颗（自动单位） | 省名接受中文全称/简称/英文/ISO；始终带南海诸岛附图 |
| `danmaku` | `items`, `count`, `bg`, `t_hl` | 3–300 条；背景可图可视频 | 条数不足循环补足；同车道不重叠 |
| `receipt` | `items`, `discount`, `total`, `currency` | 1–24 行；名字过长省略 | 合计自动计算；超长小票继续出纸上滚 |

### 不说话的时刻

| 效果 | 参数 | 接受的范围 | 超出范围时 |
|---|---|---|---|
| `breather` | text, sub, kicker, image/video, mood | 0 字到一整句（≤3 行）；1–8 秒，越长镜头推得越多 | 1.5 秒以下只推镜和画线 |
| `interlude` | clips, kicker, title, source, bpm | 0–N 段视频或图片，任意比例；镜头数 ≈ 时长 / 1.4 秒 | 没有素材时用光场；超长比例模糊铺底 |
| `suspense` | q, reveal/value, sub, at | 悬停 0.6–8 秒；揭晓数字自动万/亿，或一个词到一句话 | at 给 "@词" 时揭晓落在字上 |
| `cold_open` | title, kicker, sub, clips, at | 1–8 秒；0–N 段素材；标题 ≤2 行 | 需配音后移（见 meta.lead） |
| `beat_cut` | items, bpm/beats, every | 任意时长、任意条目数（循环）；文字 ≤2 行 | 节拍误差 ≤1 帧 |
| `reaction` | mood, text, image/video | funny / heavy；1–8 秒 | — |
| `loading` | label, steps, done, style | 0–6 步；1–8 秒（进度按时长伸缩） | 超过 4 步时列表滚动 |
| `think_loop` | text, orbits, glyph | 0–8 个环绕标记；整数个循环 | — |
| `chapter_breather` | done, next, n, total, recap | 2–12 章；0–4 条回顾；1–8 秒 | 2 秒以下不显示回顾 |

