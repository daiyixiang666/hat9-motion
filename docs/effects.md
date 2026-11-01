# 效果目录 · Effects

每个效果都是 `scripts/h9/aefx.py` 里的一个函数，在 `video.json` 里写成一个 beat：

```json
{"scene": "fx", "fx": "stomp", "words": ["大家", "都在用", "AI"], "t": "@大家"}
```

排名和人气依据见 [`research/ae_popular.md`](../research/ae_popular.md)。横屏、竖屏同一套参数。

## 效果

### `parallax` — 2.5D 照片视差 (#2, VoluMax/Photomotion; MDMZ 1171万播放)

<img src="../assets/previews/fx/parallax.webp" width="480" alt="parallax">

clean plate + cut-out subject on separate depths, the camera dollies in so the subject separates from the background; optional title sits BETWEEN the layers. plate | image | video as the ground (+focus); fg optional (a transparent PNG cut-out).

- 参数：`fg`, `focus`, `image`, `plate`, `text`, `video`
- 人气：VoluMax 2.64万份 · MDMZ 教程 1171万播放

### `burst` — 形状元素爆发 (Shape Elements burst)

<img src="../assets/previews/fx/burst.webp" width="480" alt="burst">

radial lines + ring + dots fire as the word slams in.

- 参数：—
- 人气：Graphics Pack 2.62万份 · SonduckFilm 321万播放

### `stomp` — 重拍排版 Stomp (#4, TypoKing 1.34万份; B站动态歌词排版 898万)

<img src="../assets/previews/fx/stomp.webp" width="480" alt="stomp">

one word per beat slams full-frame, sizes alternate, every third beat inverts the frame; a 2-frame jolt on each hit. words: 1–12 (a list, "a|b|c", or just text → split into words). Long words wrap to two lines. With narration timestamps each word lands the moment it is spoken (like lyric typography).

- 参数：`beat`, `text`, `words`
- 人气：TypoKing 1.34万份 · B站动态歌词排版 898万播放

### `mask_up` — 行遮罩上移 (the most-used title reveal)

<img src="../assets/previews/fx/mask_up.webp" width="480" alt="mask_up">

each line rises out of its own mask, expo.out.

- 参数：`sub`
- 人气：YouTube 153万 / 145万播放

### `mosaic` — 照片墙拼合 (#6, Mosaic Photo Reveal 1.6万份)

<img src="../assets/previews/fx/mosaic.webp" width="480" alt="mosaic">

tiles fly in from depth and assemble a wall, then the camera pushes into one tile until it fills the frame. images: 1…24 of any aspect (fewer than 12 → varied crops; 12–24 → one tile each, the grid re-shapes to the count); clips may be mixed in (up to 6 play, the rest show a still).

- 参数：`focus`, `image`, `images`, `video`
- 人气：Mosaic Photo Reveal 1.6万份

### `cartoon` — 卡通冲击特效 (#7, 140 Flash FX 1.47万份)

<img src="../assets/previews/fx/cartoon.webp" width="480" alt="cartoon">

speed lines, a jagged impact star, smoke puffs — on twos (12 fps steps).

- 参数：`text`
- 人气：140 Flash FX 1.47万份

### `apple_blur` — 苹果式逐字模糊渐显 (#9, 206.8万 2025)

<img src="../assets/previews/fx/apple_blur.webp" width="480" alt="apple_blur">

each glyph fades up out of a soft blur and a small rise, grey→white.

- 参数：—
- 人气：206.8万播放（2025）

### `portal` — 瞳孔穿梭 / 穿洞推进 (#10, B站364.5万 2025)

<img src="../assets/previews/fx/portal.webp" width="480" alt="portal">

a hole opens on a point of frame A showing frame B, then the camera dives through the hole until B fills the screen. image|video and image2|video2 (+focus, focus2).

- 参数：`focus`, `focus2`, `image`, `image2`, `video`, `video2`, `x`, `y`
- 人气：B站 364.5万播放（2025）

### `shine` — 光泽扫过 (Shine / CC Light Sweep) on a title

<img src="../assets/previews/fx/shine.webp" width="480" alt="shine">

a bright band travels across the glyphs once.

- 参数：—
- 人气：Gold Simple Titles 1.1万份

### `neon` — 霓虹点亮 (#12, Neon Sign Kit 1万份)

<img src="../assets/previews/fx/neon.webp" width="480" alt="neon">

tube text stutters on (stepped flicker pattern), then holds with a steady glow.

- 参数：`color`
- 人气：Neon Sign Kit 1万份

### `notify` — 手机通知界面 (#13, Envato Elements「Elements」热门第1)

<img src="../assets/previews/fx/notify.webp" width="480" alt="notify">

iOS-style banners drop in one after another and stack. items: 1–6 of "应用：消息" | [应用, 消息] | {app, text}; long messages wrap to two lines; the stack scales to fit.

- 参数：`items`, `line`
- 人气：Envato Elements「Elements」热门第1

### `lower3` — 下三分之一字条 (#14, Lower Thirds 第1名 6.3K)

<img src="../assets/previews/fx/lower3.webp" width="480" alt="lower3">

accent bar grows, name slides out of a mask, role follows.

- 参数：`sub`, `text`
- 人气：Lower Thirds 第1名 6.3K份

### `glitch` — 故障 RGB 分离 (Glitch / RGB split)

<img src="../assets/previews/fx/glitch.webp" width="480" alt="glitch">

red & cyan copies jitter on stepped frames, then lock.

- 参数：`text`
- 人气：Video Copilot 198万播放

### `triple` — 三连 (like · coin · favourite …)

<img src="../assets/previews/fx/triple.webp" width="480" alt="triple">

1–5 icons pop in sequence, each with a ring burst; the B站/抖音 staple ending. labels: list of 1–5 (icons in order: 点赞 投币 收藏 转发 评论); icons: optional indices into that set.

- 参数：`icons`, `labels`
- 人气：555 Animated Icons 6.4K份 · B站三连 157万

### `callout` — 标注引线 (Callout title)

<img src="../assets/previews/fx/callout.webp" width="480" alt="callout">

a dot pops on the subject, the leader line draws out, the label slides along it. image | video (+focus) as the ground; one point (x, y, text, sub) or points: [{x, y, text, sub}, …] up to 4. Labels turn left when the point is on the right third, and drop below when it is near the top.

- 参数：`focus`, `image`, `points`, `sub`, `text`, `video`, `x`, `y`
- 人气：Call-Out Titles 4.5K份

### `odometer` — 数字滚轮 (Odometer / number wheel)

<img src="../assets/previews/fx/odometer.webp" width="480" alt="odometer">

each digit column spins down to its value, staggered. value: 46479 | "46,479" | -3.5 | "97.5" | 1.2e9 (numbers get thousands separators; zh:true → 万/亿).

- 参数：`unit`, `value`, `zh`
- 人气：YouTube 162.6万播放

### `collage` — 拼贴剪纸 (#21, Fakeplastictree Collage 203.5万)

<img src="../assets/previews/fx/collage.webp" width="480" alt="collage">

torn-edge photo pieces land on paper on twos, tape, a hand-drawn arrow. images: 1–9 of any aspect (each piece keeps its picture's shape; clips play inside their frames); text: the handwritten note.

- 参数：`focus`, `image`, `images`, `text`, `video`
- 人气：Fakeplastictree 203.5万播放

### `write_on` — 描边书写 → 填色 (Trim Paths on text / 手写签名)

<img src="../assets/previews/fx/write_on.webp" width="480" alt="write_on">

glyph outlines draw on, then the fill floods in.

- 参数：`text`
- 人气：YouTube 128.5万 / 123.7万播放

### `match_cut` — 文字匹配剪辑 Text Match Cut (#23, Envato Elements 标题热门第1/2)

<img src="../assets/previews/fx/match_cut.webp" width="480" alt="match_cut">

the word holds its exact place while everything around it hard-cuts — background, colour field and typeface change every few frames. Each cut is a designed pair (ground + type treatment), so the word always reads. images: 0…N (all are cycled; clips play as grounds).

- 参数：`focus`, `images`, `text`
- 人气：Envato Elements 标题热门第1、2名

### `impact` — 冲击抖动 (#24, Bricks 106.8万 2025)

<img src="../assets/previews/fx/impact.webp" width="480" alt="impact">

the title slams in and the whole frame takes a decaying camera shake.

- 参数：—
- 人气：Bricks 106.8万播放（2025）

### `typewriter` — 打字机 + 光标

<img src="../assets/previews/fx/typewriter.webp" width="480" alt="typewriter">

one glyph per 2 frames, blinking caret (deterministic blink on the timeline).

- 参数：`text`
- 人气：T5 · 科技 / 教程类必备

### `scramble` — 乱码解码 (Decoder / Scramble)

<img src="../assets/previews/fx/scramble.webp" width="480" alt="scramble">

every slot is a reel of random glyphs that steps (not slides) onto its real character, slots settling left→right. Pure transforms with a steps() ease, so it seeks in any order.

- 参数：`pool`, `text`
- 人气：科技类标题高频

### `tracking` — 字距收拢 (Tracking In)

<img src="../assets/previews/fx/tracking.webp" width="480" alt="tracking">

glyphs start spread wide and drift together while sharpening — done with transforms (x offset ∝ distance from the centre of its own line), so it never snaps to whole pixels like letter-spacing would.

- 参数：`spread`
- 人气：电影片头经典

### `flip3d` — 逐字三维翻转 (3D Flip per character)

<img src="../assets/previews/fx/flip3d.webp" width="480" alt="flip3d">

rotateX from -100°, transform-origin bottom, perspective on the line.

- 参数：—
- 人气：文字动效合集高频

### `ghost_type` — 巨型虚影背景字 (Ghost / outline background type)

<img src="../assets/previews/fx/ghost_type.webp" width="480" alt="ghost_type">

a huge outlined word drifts behind small foreground copy.

- 参数：`ghost`, `text`
- 人气：B站「碰撞吧！」107万播放

### `lockup` — 中英双语锁定 + 注释引线 (type specimen lockup)

<img src="../assets/previews/fx/lockup.webp" width="480" alt="lockup">

headline, latin line, 0–4 leader-line annotations.

- 参数：`notes`
- 人气：B站「碰撞吧！」107万播放

### `diffuse` — 弥散光 (diffuse gradient blobs)

<img src="../assets/previews/fx/diffuse.webp" width="480" alt="diffuse">

1–5 soft colour blobs orbit slowly behind a calm title.

- 参数：`colors`
- 人气：B站「碰撞吧！」107万播放

### `gooey` — 粘性碰撞 (gooey metaballs)

<img src="../assets/previews/fx/gooey.webp" width="480" alt="gooey">

two balls approach, merge with a liquid neck, bounce apart; squash & stretch. labels: optional [左, 右] — two words that ride under the balls (e.g. 流量 / 供应链).

- 参数：`labels`
- 人气：S5 · B站「碰撞吧！」107万播放

### `earth_zoom` — 

<img src="../assets/previews/fx/earth_zoom.webp" width="480" alt="earth_zoom">



- 参数：`from_lat`, `from_lon`, `km`, `lat`, `lon`, `sub`, `text`, `zoom`
- 人气：Ultimate Earth Zoom Toolkit 9.5K · Google Earth Studio 缩放教程 207万播放

### `map_route` — 

<img src="../assets/previews/fx/map_route.webp" width="480" alt="map_route">



- 参数：`chips`, `from`, `from_sub`, `points`, `stops`, `to`, `to_sub`
- 人气：Map Route Generator 3.5K · Ignace Aleya 动画旅行地图 169.5万播放

### `bars` — 

<img src="../assets/previews/fx/bars.webp" width="480" alt="bars">



- 参数：`compact`, `dec`, `growth`, `hl`, `items`, `note`, `orient`, `title`, `unit`
- 人气：Infographic Maker 2.6K · Mapal VOX 式信息图 34.6万播放

### `line_draw` — 

<img src="../assets/previews/fx/line_draw.webp" width="480" alt="line_draw">



- 参数：`compact`, `dec`, `note`, `points`, `title`, `unit`
- 人气：Envato Popular「Line Chart Infographic」· SonduckFilm 23.2万播放

### `donut` — 

<img src="../assets/previews/fx/donut.webp" width="480" alt="donut">



- 参数：`center`, `dec`, `segments`, `sub`, `text`, `value`
- 人气：Envato Popular「Infographic Pie Chart 250+」· Move Shapes 17.6万播放

### `timeline` — 

<img src="../assets/previews/fx/timeline.webp" width="480" alt="timeline">



- 参数：`hl`, `items`
- 人气：Company Timeline 3.2K（Titles 第 9）· Smertimba 23.9万播放

### `chat` — 

<img src="../assets/previews/fx/chat.webp" width="480" alt="chat">



- 参数：`a`, `hl`, `placeholder`, `q`, `title`, `turns`
- 人气：Envato Elements「Elements」Popular 第 1 · Text Messages 3.8K

### `hud_lock` — 

<img src="../assets/previews/fx/hud_lock.webp" width="480" alt="hud_lock">



- 参数：`image`, `readouts`, `text`, `v`, `video`, `video_start`
- 人气：Quantum HUD Infographic 5.9K（Infographics 第 1）

### `glass` — 

<img src="../assets/previews/fx/glass.webp" width="480" alt="glass">



- 参数：`compact`, `dec`, `image`, `kicker`, `rows`, `tag`, `text`, `unit`, `value`, `value_text`, `video`, `video_start`
- 人气：Bricks「Animate Like Apple」76万播放（2025）· Envato「Real Glass FX」Popular 第 4

### `text_mask` — 

<img src="../assets/previews/fx/text_mask.webp" width="480" alt="text_mask">



- 参数：`image`, `images`, `sub`, `text`
- 人气：SonduckFilm「5 Quick Text Effects」76.7万播放 · Mixkit Video Mask Title

<img src="../assets/previews/fx/media-1.webp" width="320" alt="media 1 张"> 1 张

<img src="../assets/previews/fx/media-2.webp" width="320" alt="media 2 张"> 2 张

<img src="../assets/previews/fx/media-3.webp" width="320" alt="media 3 张"> 3 张

<img src="../assets/previews/fx/media-5.webp" width="320" alt="media 5 张"> 5 张

<img src="../assets/previews/fx/media-12.webp" width="320" alt="media 12 张"> 12 张

<img src="../assets/previews/fx/media-40.webp" width="320" alt="media 40 张"> 40 张

<img src="../assets/previews/fx/media-200.webp" width="320" alt="media 200 张"> 200 张

<img src="../assets/previews/fx/media-video.webp" width="320" alt="media 视频混排"> 视频混排

### `cite_pdf` — 

<img src="../assets/previews/fx/cite_pdf.webp" width="480" alt="cite_pdf">



- 参数：`cite`, `file`, `kicker`, `page_label`, `pdf`, `quote`, `zh`
- 人气：判决书 / 财报 / 研报原文高亮

### `cite_paper` — 

<img src="../assets/previews/fx/cite_paper.webp" width="480" alt="cite_paper">



- 参数：`abstract`, `arxiv`, `authors`, `cites`, `doi`, `figure`, `hl`, `max_authors`, `takeaway`, `title`, `venue`, `year`
- 人气：论文标题页 + 摘要高亮

### `cite_article` — 

<img src="../assets/previews/fx/cite_article.webp" width="480" alt="cite_article">



- 参数：`box`, `byline`, `date`, `dek`, `excerpt`, `focus`, `headline`, `hl`, `image`, `kicker`, `outlet`, `points`, `section`, `url`
- 人气：「据某某报道」：标题 + 原文摘录 + 要点

### `cite_quote` — 

<img src="../assets/previews/fx/cite_quote.webp" width="480" alt="cite_quote">



- 参数：`date`, `hl`, `image`, `name`, `role`, `source`, `text`, `year`, `zh`
- 人气：名人原话 + 出处 + 译文

### `cite_post` — 

<img src="../assets/previews/fx/cite_post.webp" width="480" alt="cite_post">



- 参数：`avatar`, `counts`, `date`, `handle`, `hl`, `image`, `name`, `stat`, `text`, `time`, `verified`, `zh`
- 人气：平台中立的帖子卡：不用任何平台界面和标志

### `cite_video` — 

<img src="../assets/previews/fx/cite_video.webp" width="480" alt="cite_video">



- 参数：`caption`, `focus`, `hl`, `image`, `kicker`, `license`, `quote`, `source`, `start`, `title`, `video`, `year`
- 人气：片段真实播放 · 进度条 · 时间码

### `cite_stack` — 

<img src="../assets/previews/fx/cite_stack.webp" width="480" alt="cite_stack">



- 参数：`claim`, `kicker`, `sources`, `tally`
- 人气：交叉验证：每条来源打勾，连线汇到结论

### `list_stack` — 

<img src="../assets/previews/fx/list_stack.webp" width="480" alt="list_stack">



- 参数：`hl`, `items`, `strike`, `style`, `title`
- 人气：Envato Elements「Checklist Pack」热门 · talkcraft numbered-step-stack

### `steps` — 

<img src="../assets/previews/fx/steps.webp" width="480" alt="steps">



- 参数：`hl`, `items`, `title`
- 人气：talkcraft step-timeline-vertical · 教程类「三步做出……」

### `ranking` — 

<img src="../assets/previews/fx/ranking.webp" width="480" alt="ranking">



- 参数：`hide_top`, `items`, `title`, `unit`
- 人气：盘点类「年度十大」格式 · talkcraft number-slab-pop

### `term_card` — 

<img src="../assets/previews/fx/term_card.webp" width="480" alt="term_card">



- 参数：`definition`, `example`, `host`, `pos`, `reading`, `source`, `sub`, `term`, `text`
- 人气：talkcraft info-term-card · 回形针 / 所长林超的概念卡

### `word_swap` — 

<img src="../assets/previews/fx/word_swap.webp" width="480" alt="word_swap">



- 参数：`host`, `mode`, `post`, `pre`, `words`
- 人气：talkcraft word-slot-cycle · Rotating Words 标题模板

### `pros_cons` — 

<img src="../assets/previews/fx/pros_cons.webp" width="480" alt="pros_cons">



- 参数：`cons`, `labels`, `pros`, `verdict`
- 人气：测评类口播标配 · Envato Elements Checklist Pack

### `quadrant` — 

<img src="../assets/previews/fx/quadrant.webp" width="480" alt="quadrant">



- 参数：`hl`, `items`, `note`, `quads`, `x_axis`, `y_axis`
- 人气：咨询式 2×2 定位图（BCG 矩阵式）

### `countdown` — 

<img src="../assets/previews/fx/countdown.webp" width="480" alt="countdown">



- 参数：`ask`, `from`, `question`, `reveal`, `to`
- 人气：VideoHive Elements countdown 大类 · talkcraft countdown-arc-scatter

### `chapter_bar` — 

<img src="../assets/previews/fx/chapter_bar.webp" width="480" alt="chapter_bar">



- 参数：`chapters`, `hl`, `now`, `title`
- 人气：talkcraft chapter-progress-list · B 站分 P 目录

### `table` — 

<img src="../assets/previews/fx/table.webp" width="480" alt="table">



- 参数：`compact`, `header`, `hl_cell`, `hl_col`, `hl_row`, `max_rows`, `note`, `paren`, `title`, `transpose`
- 人气：VideoHive Infographic Maker 2.6K · Mapal VOX 式信息图 34.6万播放

### `statement_table` — 

<img src="../assets/previews/fx/statement_table.webp" width="480" alt="statement_table">



- 参数：`dec`, `hl`, `hl_note`, `period`, `title`, `unit`
- 人气：VideoHive Infographic Maker 2.6K · Mapal VOX 式信息图 34.6万播放

### `waterfall` — 

<img src="../assets/previews/fx/waterfall.webp" width="480" alt="waterfall">



- 参数：`compact`, `dec`, `note`, `orient`, `readout`, `title`, `unit`
- 人气：VideoHive Infographic Maker 2.6K · Mapal VOX 式信息图 34.6万播放

### `scale_compare` — 

<img src="../assets/previews/fx/scale_compare.webp" width="480" alt="scale_compare">



- 参数：`a_label`, `b_label`, `basis`, `dec`, `head`, `icon`, `method`, `mode`, `ratio`, `ratio_label`, `ref_value`, `unit_name`, `value`
- 人气：Envato Popular Infographic · Mapal VOX 式信息图 34.6万播放

### `bar_race` — 

<img src="../assets/previews/fx/bar_race.webp" width="480" alt="bar_race">



- 参数：`compact`, `csv`, `dec`, `hl`, `note`, `title`, `top`, `transpose`, `unit`
- 人气：Data Is Beautiful 编程语言排行赛跑 上线一个半月 265万播放

### `stacked_bars` — 

<img src="../assets/previews/fx/stacked_bars.webp" width="480" alt="stacked_bars">



- 参数：`compact`, `csv`, `dec`, `hl`, `note`, `orient`, `percent`, `title`, `total_col`, `totals`, `unit`, `x`
- 人气：SonduckFilm Bar Infographics 23.2万播放 · Infographic Maker 2.6K

### `formula` — 

<img src="../assets/previews/fx/formula.webp" width="480" alt="formula">



- 参数：`dec`, `lhs`, `note`, `ops`, `result`, `terms`, `unit`
- 人气：YouTube 数字滚动教程 162.6万播放 · Envato Popular Number Counter

### `bars_csv` — 

<img src="../assets/previews/fx/bars_csv.webp" width="480" alt="bars_csv">



- 参数：`fxid`, `limit`, `scale`, `sort`
- 人气：VideoHive Infographic Maker 2.6K · Mapal VOX 式信息图 34.6万播放

### `scroll_shot` — 

<img src="../assets/previews/fx/scroll_shot.webp" width="480" alt="scroll_shot">



- 参数：`dark_chrome`, `frame`, `image`, `shot`, `tab`, `toc`, `url`
- 人气：VideoHive Minimal Website Presentation 1.9K

### `screencast` — 

<img src="../assets/previews/fx/screencast.webp" width="480" alt="screencast">



- 参数：`clicks`, `clicks_json`, `cursor`, `dark_chrome`, `frame`, `hl`, `image`, `start`, `steps`, `tab`, `url`, `video`
- 人气：VideoHive iTouch 2 App Promo 2.1K

### `spotlight` — 

<img src="../assets/previews/fx/spotlight.webp" width="480" alt="spotlight">



- 参数：`boxes`, `dark_chrome`, `dim`, `frame`, `image`, `start`, `url`, `video`, `zoom`
- 人气：VideoHive Explainer Video Toolkit 4 2.5K

### `code` — 

<img src="../assets/previews/fx/code.webp" width="480" alt="code">



- 参数：`at_hl`, `cmd`, `hl`, `mode`, `output`, `prompt`, `title`
- 人气：Askiko Typewriter Text Effect 113.3 万播放

### `comment_thread` — 

<img src="../assets/previews/fx/comment_thread.webp" width="480" alt="comment_thread">



- 参数：`comments`, `hl`, `items`, `mock`, `mock_label`, `placeholder`, `sort`, `text`, `title`, `total`
- 人气：Envato「Social Media Comments」评论截图包常年在社交类前列

### `im_chat` — 

<img src="../assets/previews/fx/im_chat.webp" width="480" alt="im_chat">



- 参数：`items`, `messages`, `mock`, `mock_label`, `read`, `title`
- 人气：Envato「Text Messages」3.8K 份

### `profile_card` — 

<img src="../assets/previews/fx/profile_card.webp" width="480" alt="profile_card">



- 参数：`follow`, `hl`, `mock`, `mock_label`
- 人气：Envato「Lower Thirds」6.3K 份 · 社交名片模板

<img src="../assets/previews/fx/profile_card-group.webp" width="320" alt="profile_card 多人并列"> 多人并列

### `equity_tree` — 

<img src="../assets/previews/fx/equity_tree.webp" width="480" alt="equity_tree">



- 参数：`hl`, `holders`, `mock`, `mock_label`, `mode`, `root`, `subs`, `summary`
- 人气：企查查 / 天眼查式股权图 · Envato「Organizational Chart」

### `china_map` — 

<img src="../assets/previews/fx/china_map.webp" width="480" alt="china_map">



- 参数：`dec`, `dot_unit`, `dots`, `focus`, `highlight`, `hl`, `legend`, `list`, `mock`, `mock_label`, `points`, `seed`, `title`, `top`, `unit`, `values`
- 人气：Envato「China Map」地图信息图包

<img src="../assets/previews/fx/china_map-dots.webp" width="320" alt="china_map 门店撒点"> 门店撒点

### `danmaku` — 

<img src="../assets/previews/fx/danmaku.webp" width="480" alt="danmaku">



- 参数：`bg`, `count`, `hl_text`, `items`, `mock`, `mock_label`, `seed`, `speed`, `t_hl`
- 人气：B站弹幕刷屏 · 二创与口播常用

### `receipt` — 

<img src="../assets/previews/fx/receipt.webp" width="480" alt="receipt">



- 参数：`currency`, `discount`, `items`, `mock`, `mock_label`, `no`, `note`, `paid`, `seed`, `store`, `time`, `total`
- 人气：Envato「Receipt」mockup

### `cold_open` — 

<img src="../assets/previews/fx/cold_open.webp" width="480" alt="cold_open">



- 参数：`clips`, `grade`, `kicker`, `sub`, `title`
- 人气：电影预告 / 纪录片冷开场

### `suspense` — 

<img src="../assets/previews/fx/suspense.webp" width="480" alt="suspense">



- 参数：`countdown`, `dec`, `q`, `reveal`, `sub`, `unit`, `value`
- 人气：句中停 1.15 秒，再落数字

### `interlude` — 

<img src="../assets/previews/fx/interlude.webp" width="480" alt="interlude">



- 参数：`beats`, `bpm`, `clips`, `grade`, `kicker`, `letterbox`, `source`, `title`
- 人气：不说话的 2.8 秒

### `beat_cut` — 

<img src="../assets/previews/fx/beat_cut.webp" width="480" alt="beat_cut">



- 参数：`every`, `items`, `theme`, `ticks`
- 人气：纯音乐 3.6 秒，100 bpm，每拍一切

### `breather` — 

<img src="../assets/previews/fx/breather.webp" width="480" alt="breather">



- 参数：`focus`, `held`, `image`, `kicker`, `lift`, `meter`, `mood`, `sub`, `text`, `video`
- 人气：金句后停 2.6 秒

### `pip` — 

<img src="../assets/previews/fx/pip.webp" width="480" alt="pip">



- 参数：`back_at`, `corner`, `focus`, `host_fit`, `host_focus`, `kicker`, `main`, `main_start`, `name`, `role`, `shape`, `size`, `title`
- 人气：小Lin说、林亦、毕导常用

### `freeze_frame` — 

<img src="../assets/previews/fx/freeze_frame.webp" width="480" alt="freeze_frame">



- 参数：`hold`, `image`, `mode`, `pin`, `pins`, `resume`, `stamp`, `start`, `video`
- 人气：B站科普常用：关键瞬间定格

### `speed_ramp` — 

<img src="../assets/previews/fx/speed_ramp.webp" width="480" alt="speed_ramp">



- 参数：`badge`, `drama`, `focus`, `graph`, `ramp`, `smooth`, `start`, `video`
- 人气：B站「AE 变速卡点」173.4 万播放

### `footage` — 

<img src="../assets/previews/fx/footage.webp" width="480" alt="footage">



- 参数：`band_label`, `focus`, `image`, `name`, `role`, `show_band`, `start`, `subs`, `video`, `zoom`
- 人气：采访切片、素材自带字幕

### `audio_quote` — 

<img src="../assets/previews/fx/audio_quote.webp" width="480" alt="audio_quote">



- 参数：`a`, `audio`, `avatar`, `b`, `bars`, `date`, `kicker`, `quote`, `role`, `source`, `vol`, `who`, `words`
- 人气：Envato「Audio Visualizer」热门

### `podcast` — 

<img src="../assets/previews/fx/podcast.webp" width="480" alt="podcast">



- 参数：`a`, `art`, `audio`, `b`, `ep`, `episode`, `hosts`, `show`, `speaker`, `turns`, `vol`, `words`
- 人气：Envato「Audio Visualizer」热门

### `talking_head` — 

<img src="../assets/previews/fx/talking_head.webp" width="480" alt="talking_head">



- 参数：`broll`, `host_fit`, `name`, `stickers`
- 人气：毕导式口播：跳切 + 贴纸

### `host_point` — 

<img src="../assets/previews/fx/host_point.webp" width="480" alt="host_point">



- 参数：`card`, `host_fit`, `say`, `side`
- 人气：Vox「Look at this」指哪说哪

### `text_pages` — 

<img src="../assets/previews/fx/text_pages.webp" width="480" alt="text_pages">



- 参数：`at`, `dir`, `pages`, `paragraph`, `text`, `title`, `trans`, `translation`
- 人气：Envato Elements「Hook & Captions」Titles Popular 第 12 · B 站动态歌词排版 898 万

### `question_card` — 

<img src="../assets/previews/fx/question_card.webp" width="480" alt="question_card">



- 参数：`answer`, `at_reveal`, `host`, `kicker`, `options`, `q`, `question`, `reveal`, `text`
- 人气：知识区设问手法（小Lin说 / 回形针的问号卡）· Kinetic Typography Pack 4.2K

### `vertical_title` — 

<img src="../assets/previews/fx/vertical_title.webp" width="480" alt="vertical_title">



- 参数：`font`, `mode`, `seal`, `sub`, `text`
- 人气：国风纪录片 / 片头常用的竖排版式

### `flying_words` — 

<img src="../assets/previews/fx/flying_words.webp" width="480" alt="flying_words">



- 参数：`at`, `final`, `items`, `sub`, `words`
- 人气：B 站「PV 中的文字穿梭效果」23 万 · VideoHive Flying Through Words 2.2K

### `number_pages` — 

<img src="../assets/previews/fx/number_pages.webp" width="480" alt="number_pages">



- 参数：`at`, `items`, `per_page`, `text`
- 人气：Number Counter：YouTube 162.6 万 · Envato Popular「Number Counter」

### `combo` — 

<img src="../assets/previews/fx/combo.webp" width="480" alt="combo">



- 参数：`at`, `count`, `final`, `hits`, `tag`, `unit`
- 人气：Number Counter 162.6 万 · Shape Elements burst（Graphics Pack 26.2K）

### `black_slam` — 

<img src="../assets/previews/fx/black_slam.webp" width="480" alt="black_slam">



- 参数：`at`, `hits`, `sub`, `text`, `theme`
- 人气：Camera Move + Impact Shake：Bricks 106.8 万（2025）

### `scribble` — 

<img src="../assets/previews/fx/scribble.webp" width="480" alt="scribble">



- 参数：`at`, `image`, `ink`, `scribbles`, `text`, `theme`
- 人气：B 站「白菜和杜比 手绘科普」69.9 万（2026）· Ben Marriott Hand Drawn 45.4 万

### `scanline` — 

<img src="../assets/previews/fx/scanline.webp" width="480" alt="scanline">



- 参数：`at`, `blocks`, `dir`, `image`, `text`
- 人气：HUD 扫描界面（Quantum HUD Infographic 5.9K）

### `icon_unit` — 

<img src="../assets/previews/fx/icon_unit.webp" width="480" alt="icon_unit">



- 参数：`big`, `big_unit`, `groups`, `icon`, `legend`, `per`, `share`, `sub`, `text`, `total`, `unit`, `value`
- 人气：VideoHive「555 Animated Icons」6.4K · Pictogram Infographic Kit 759

### `scatter` — 

<img src="../assets/previews/fx/scatter.webp" width="480" alt="scatter">



- 参数：`hl`, `hl_note`, `labels`, `log`, `points`, `quad`, `size_lab`, `xlab`, `xunit`, `ylab`, `yunit`
- 人气：VideoHive「Infographic Maker」2.6K · 「Infographics」2.2K

### `funnel` — 

<img src="../assets/previews/fx/funnel.webp" width="480" alt="funnel">



- 参数：`dec`, `floor`, `hl`, `mode`, `pct_label`, `stages`, `unit`
- 人气：VideoHive「Simple Infographics」1.9K · 「Infographic Maker」2.6K

### `radar` — 

<img src="../assets/previews/fx/radar.webp" width="480" alt="radar">



- 参数：`axes`, `fmt`, `hl`, `max`, `series`
- 人气：VideoHive「Infographics」2.2K · 「Quantum HUD」5.9K

### `then_now` — 

<img src="../assets/previews/fx/then_now.webp" width="480" alt="then_now">



- 参数：`change`, `dec`, `now`, `then`
- 人气：Envato Popular「Vertical Split Screen」· SonduckFilm 分屏教程 23.2 万

### `choose_one` — 

<img src="../assets/previews/fx/choose_one.webp" width="480" alt="choose_one">



- 参数：`dec`, `hops`, `options`, `pick`, `q`, `unit`
- 人气：知识区「先猜再揭晓」开场 · 选项卡逐个跳动后落定

### `converge` — 

<img src="../assets/previews/fx/converge.webp" width="480" alt="converge">



- 参数：`dec`, `sources`, `target`, `total`, `unit`
- 人气：VideoHive「3D Earth Connections」3.4K · 「Infographic Maker」2.6K

### `gantt` — 

<img src="../assets/previews/fx/gantt.webp" width="480" alt="gantt">



- 参数：`hi`, `hl`, `lo`, `milestones`, `now`, `tasks`, `unit`
- 人气：VideoHive「Company Timeline」3.2K · Envato「Infographics 6 Roadmaps」

### `decision_tree` — 

<img src="../assets/previews/fx/decision_tree.webp" width="480" alt="decision_tree">



- 参数：`path`, `tree`
- 人气：Envato「Infographics 6 Roadmaps」· VideoHive「Infographic Maker」2.6K

### `area_overlay` — 

<img src="../assets/previews/fx/area_overlay.webp" width="480" alt="area_overlay">



- 参数：`a`, `b`, `ratio_text`, `unit`
- 人气：VideoHive「Infographics 3D Map Kit」3.2K · 「Map Kit」1.4K · Vox 式地图

### `map_timeline` — 

<img src="../assets/previews/fx/map_timeline.webp" width="480" alt="map_timeline">



- 参数：`from`, `labels`, `points`, `to`, `unit`
- 人气：VideoHive「Map Route Generator」3.5K · 「World Map Animation」2.8K

### `street_map` — 

<img src="../assets/previews/fx/street_map.webp" width="480" alt="street_map">



- 参数：`geojson`, `hl`, `route`, `route_label`
- 人气：VideoHive「Map Kit」1.4K · 「3D Map Generator」1.2K

### `logo_wall` — 

<img src="../assets/previews/fx/logo_wall.webp" width="480" alt="logo_wall">



- 参数：`hl`, `kicker`, `logos`, `names`, `sub`, `t_hl`, `title`
- 人气：VideoHive Multi Video & Multi Text Logo Formation 3.8K · Mosaic Photo Reveal 16K

### `halftone` — 

<img src="../assets/previews/fx/halftone.webp" width="480" alt="halftone">



- 参数：`cell`, `focus`, `image`, `ink`, `ink2`, `kicker`, `mode`, `paper`, `src`, `title`
- 人气：Ben Marriott「Make ANYTHING Retro」99.6 万 ·「Instant Dither」30.6 万

### `meme_stage` — 

<img src="../assets/previews/fx/meme_stage.webp" width="480" alt="meme_stage">



- 参数：`at`, `captions`, `images`, `items`, `mode`, `title`
- 人气：Fakeplastictree「Collage」203.5 万 · Ben Marriott Paper Cutout 30.7 万

### `gif_clip` — 

<img src="../assets/previews/fx/gif_clip.webp" width="480" alt="gif_clip">



- 参数：`caption`, `fit`, `focus`, `frame`, `gif`, `speed`, `src`, `title`
- 人气：VideoHive Photo Frames Slideshow 3.6K（Openers 第 3）· Mixkit Polaroid Slideshow

### `svg_art` — 

<img src="../assets/previews/fx/svg_art.webp" width="480" alt="svg_art">



- 参数：`accent`, `bg`, `caption`, `draw`, `fg`, `recolor`, `src`, `svg`, `swap`, `title`
- 人气：「Stroke Logo Animation」128.5 万 · SonduckFilm Stroke Logo Reveal 66.7 万

### `doc_photo` — 

<img src="../assets/previews/fx/doc_photo.webp" width="480" alt="doc_photo">



- 参数：`caption`, `corners`, `hl`, `image`, `kicker`, `ratio`, `src`, `title`
- 人气：Flat Pack FX「Vox Highlighter Effect」31.3 万 · Motion Street「Motion Graphics Like Vox」83.8 万

### `slides` — 

<img src="../assets/previews/fx/slides.webp" width="480" alt="slides">



- 参数：`counter`, `focus`, `pdf`, `slides`, `title`, `zoom`
- 人气：VideoHive Cinematic Parallax Slideshow 5.4K（Openers 第 1）· Photo Slideshow 3D II 2.2K

### `doc_flip` — 

<img src="../assets/previews/fx/doc_flip.webp" width="480" alt="doc_flip">



- 参数：`caption`, `dpi`, `flips`, `hl`, `of`, `pdf`, `quote`, `range`, `target`, `title`
- 人气：Motion Array「Edit A Documentary Like Johnny Harris」53.9 万

### `doc_pick` — 

<img src="../assets/previews/fx/doc_pick.webp" width="480" alt="doc_pick">



- 参数：`caption`, `hl`, `pdf`, `pick`, `quote`, `tag`, `title`
- 人气：Premiere Gal「3D Paper Highlighter」19.8 万 · Documentary Style Pack（Envato Elements 热门）

### `handwrite` — 

<img src="../assets/previews/fx/handwrite.webp" width="480" alt="handwrite">



- 参数：`font`, `ink`, `lines`, `mark`, `paper`, `text`, `tilt`, `title`
- 人气：SonduckFilm「Handwriting Effect」123.7 万 · VideoHive Whiteboard Write 2.1K

### `email_card` — 

<img src="../assets/previews/fx/email_card.webp" width="480" alt="email_card">



- 参数：`attachments`, `body`, `date`, `from`, `inbox`, `sender`, `stamp`, `subject`, `to`
- 人气：Envato Elements「Elements」分类热门：手机通知、搜索框打字等界面元素

### `notice_card` — 

<img src="../assets/previews/fx/notice_card.webp" width="480" alt="notice_card">



- 参数：`body`, `date`, `kind`, `no`, `numbered`, `org`, `signer`, `title`, `watermark`
- 人气：Johnny Harris / Vox 式报纸文件动画 19.6 万（2024）

### `app_flow` — 

<img src="../assets/previews/fx/app_flow.webp" width="480" alt="app_flow">



- 参数：`dark_chrome`, `flow`, `steps`
- 人气：VideoHive Phone 7 App & Gestures 2.6K

### `cursor` — 

<img src="../assets/previews/fx/cursor.webp" width="480" alt="cursor">



- 参数：`dark_chrome`, `frame`, `image`, `path`, `start`, `steps`, `tab`, `theme`, `trail`, `url`, `video`, `zoom`
- 人气：VideoHive Phone 7 App & Gestures 2.6K

### `form_fill` — 

<img src="../assets/previews/fx/form_fill.webp" width="480" alt="form_fill">



- 参数：`cursor`, `done`, `fields`, `sub`, `submit`, `title`
- 人气：Envato Elements「Elements」Popular「Checklist Pack」

### `turntable` — 

<img src="../assets/previews/fx/turntable.webp" width="480" alt="turntable">



- 参数：`at`, `image`, `kicker`, `name`, `price`, `specs`, `sway`, `text`, `turns`, `views`
- 人气：VideoHive Product Promo 分类销量榜

### `search_box` — 

<img src="../assets/previews/fx/search_box.webp" width="480" alt="search_box">



- 参数：`button`, `count`, `engine`, `hl`, `mock`, `pick`, `query`, `results`, `suggest`
- 人气：Envato「Search Screen Pro」Popular 第 7

### `relation_graph` — 

<img src="../assets/previews/fx/relation_graph.webp" width="480" alt="relation_graph">



- 参数：`hl`, `layout`, `t_hl`
- 人气：VideoHive Infographic Maker 2.6K · Envato Infographics「AI Workflow」

### `dialogue` — 

<img src="../assets/previews/fx/dialogue.webp" width="480" alt="dialogue">



- 参数：—
- 人气：VideoHive Text Messages 3.8K · Lower Thirds 第 1 名 6.3K

### `interview` — 

<img src="../assets/previews/fx/interview.webp" width="480" alt="interview">



- 参数：`a`, `at_a`, `at_q`, `ep`, `focus`, `host`, `image`, `name`, `org`, `q`, `role`, `start`, `tc`, `topic`, `video`
- 人气：VideoHive Lower Thirds 第 1 名 6.3K

### `opener` — 

<img src="../assets/previews/fx/opener.webp" width="480" alt="opener">



- 参数：`channel`, `en`, `ep`, `show`, `sub`, `text`, `title`
- 人气：VideoHive Openers 31,965 个 · Corporate Typography Pack 2.8K · Fast Intro 2.6K

### `news_flash` — 

<img src="../assets/previews/fx/news_flash.webp" width="480" alt="news_flash">



- 参数：`at`, `headline`, `image`, `image_label`, `items`, `kicker`, `live`, `source`, `text`, `theme`, `ticker`, `ticker_label`, `time`
- 人气：talkcraft news-card-desk · 速报类口播

### `deal_card` — 

<img src="../assets/previews/fx/deal_card.webp" width="480" alt="deal_card">



- 参数：`at`, `countdown`, `countdown_label`, `coupon`, `cur`, `image`, `note`, `price`, `product`, `stock`, `sub`, `tags`, `title`, `unit`, `was`
- 人气：Envato Infographics「Modern Price Tags & Counters」

### `clip_style` — 

<img src="../assets/previews/fx/clip_style.webp" width="480" alt="clip_style">



- 参数：`comments`, `hearts`, `image`, `line`, `live_text`, `name`, `note`, `quote`, `role`, `time`, `title`, `video`, `viewers`
- 人气：直播 / 访谈切片号通用包装 · talkcraft danmu-bubble-praise

### `review_card` — 

<img src="../assets/previews/fx/review_card.webp" width="480" alt="review_card">



- 参数：`at`, `cons`, `image`, `labels`, `max`, `note`, `overall`, `product`, `pros`, `scores`, `stars`, `sub`, `text`, `title`, `verdict`, `verdict_kind`
- 人气：数码 / 工具测评号常用版式：评分条 + 星级 + 结论徽章

### `sponsor_card` — 

<img src="../assets/previews/fx/sponsor_card.webp" width="480" alt="sponsor_card">



- 参数：`ad_tag`, `code`, `code_label`, `cta`, `host`, `image`, `lead`, `logo`, `note`, `points`, `sponsor`, `title`
- 人气：口播恰饭段落「本期视频由……支持」

### `poll_card` — 

<img src="../assets/previews/fx/poll_card.webp" width="480" alt="poll_card">



- 参数：`cta`, `hl`, `host`, `kicker`, `letters`, `mode`, `note`, `options`, `question`, `text`, `total`
- 人气：Envato Elements Popular「YouTube Subscribe」「Checklist Pack」

### `share_card` — 

<img src="../assets/previews/fx/share_card.webp" width="480" alt="share_card">



- 参数：`by`, `date`, `export`, `handle`, `hint`, `host`, `kicker`, `quote`, `text`
- 人气：小红书 / 朋友圈金句图 · scripts/share_card.py 导出单张

### `next_teaser` — 

<img src="../assets/previews/fx/next_teaser.webp" width="480" alt="next_teaser">



- 参数：`ep`, `hints`, `image`, `kicker`, `note`, `text`, `title`, `video`, `when`
- 人气：系列号片尾常用「下期拆 XX」

## 转场

写在下一个 beat 上：`"tr": "zoomin"`。

| 转场 | 预览 | 说明 |
|---|---|---|
| `zoomin` | <img src="../assets/previews/fx/tr_zoomin.webp" width="240"> | #1 无缝缩放 · Seamless Zoom（VideoHive 销量第1 · 4.16万份） |
| `spin` | <img src="../assets/previews/fx/tr_spin.webp" width="240"> | #1 无缝旋转 · Seamless Spin（Motion Bro 免费包 >100万下载） |
| `whip` | <img src="../assets/previews/fx/tr_whip.webp" width="240"> | #25 甩镜 · Whip Pan（SonduckFilm 102.8万播放） |
| `wipe` | <img src="../assets/previews/fx/tr_wipe.webp" width="240"> | 色块擦除 · Shape Wipe |
| `bars` | <img src="../assets/previews/fx/tr_bars.webp" width="240"> | 色条 · Bars |
| `iris` | <img src="../assets/previews/fx/tr_iris.webp" width="240"> | 圆形开合 · Iris |
| `glitch` | <img src="../assets/previews/fx/tr_glitch.webp" width="240"> | 故障转场 · Glitch（4.5K份） |
| `flash` | <img src="../assets/previews/fx/tr_flash.webp" width="240"> | 闪白 · Flash |
| `leak` | <img src="../assets/previews/fx/tr_leak.webp" width="240"> | 漏光 · Light Leak |
| `burn` | <img src="../assets/previews/fx/tr_burn.webp" width="240"> | 胶片烧 · Film Burn |
| `ink` | <img src="../assets/previews/fx/tr_ink.webp" width="240"> | 墨晕 · Ink |
| `shutter` | <img src="../assets/previews/fx/tr_shutter.webp" width="240"> | 快门 · Shutter |
