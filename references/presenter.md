# 主体层 Presenter：主体一直在，只是换位置

一整片都留着同一个主体——口播真人、录屏、卡通形象（透明 webm）或一张图——每个 beat 只决定它**站在哪**：全屏、图表下面的小卡、侧边、角落、或者先藏起来。换位置是一段 0.65 秒的平滑移动（不是切），视频一直往下播。这个 beat 的图形自动排在主体让出来的那块地方。

参考：抖音 7701488753897917723——人一直在，只是全屏 → 下方小卡 → 侧边 → 角落 → 回全屏，信息卡从他身边长出来，所以画面信息每 1–2 秒就换一次。

## 什么时候用

- 有一个能一直出现的主体：真人口播、卡通形象口播、一段长录屏、一张产品图。
- 想要「信息围着人动」而不是一屏一屏硬切。
- 不用：纯图表片、快切蒙太奇、没有主体的片子。

## 真人口播视频（最常见）

用户自己出镜说了一段话，要剪成带动效的成片。人就是主体，声音也从这条视频来，两者必须在同一处剪，口型才不会错位。

```bash
# 1. 拆出声音、降噪，再把干净的声音装回视频
ffmpeg -i 口播.mp4 -vn -ac 1 -ar 48000 raw.wav
python3 scripts/audio_tools.py denoise raw.wav clean.wav
ffmpeg -i 口播.mp4 -i clean.wav -map 0:v -map 1:a -c:v copy -c:a aac 口播_clean.mp4

# 2. 逐字时间：有稿子直接对齐；没有稿子先用 faster-whisper 转写，校对成稿子再对齐
python3 scripts/align.py clean.wav 稿子.txt --out talk_words.json

# 3. 找口误（重说、长停顿），确认后连画面一起剪掉
python3 scripts/audio_tools.py flubs talk_words.json
python3 scripts/audio_tools.py cut 口播_clean.mp4 work/assets/video/talk.mp4 \
    --remove 3.2-4.1,9.8-10.4 --voice work/assets/audio/voice.wav --words talk_words.json
```

`cut` 的输入输出都是视频时，画面和声音在同样的时间点剪，另外把剪好的声音写成 `--voice` 指定的 wav；`--words` 写出对应的新逐字时间（`talk.words.json`，放到 `assets/audio/words.json`）。

```json
"meta": {
  "voice": "assets/audio/voice.wav",
  "words": "assets/audio/words.json",
  "presenter": {"src": "assets/video/talk.mp4", "fit": "cover", "loop": false, "audio": false, "focus": [50, 35]}
}
```

- `loop: false`、`start: 0`：视频和口播从同一秒开始一起往下走，人说的就是字幕上的词。
- 先选一个出镜形式（`form`，见下一节），大部分 beat 不用写 `presenter`，跟着形式走就行。
- 人是这条片子的看点：开头和结尾用 `full`，中间多用 `card` / `side` 让图表从人身边长出来，`hidden` 只给真正需要整屏的画面，别连着藏好几句。
- `focus` 写脸在原视频里的位置（百分比），竖屏裁切时脸不会被切掉；所有裁切和放大都以它为中心，先抽一帧量准。
- 字不会压在真人脸上：真人素材（fit cover）的 beat 落在 `full`，而效果需要自己的版面（ON_PERSON 名单以外的所有效果：mask_up、list_stack、steps、图表……），会自动换到 `card`（9:16）/ `side`（16:9），选了 bubble / split / pip 形式就换回形式自己的位置；每换一个 beat 打印一行。真要压在人上写 `"presenter_force": true`，这时人身上自动加深色渐变，字变成浅色。
- ON_PERSON（可以直接放在全屏真人上）：lower3、callout、key_card、side_stat、stack_build、strike_fix、chip_cycle、talking_head、host_point，以及没有 fx 的纯字幕 beat。

## 出镜形式（主播出镜形式，整片选一次）

`meta.presenter.form` 决定整片的出镜方式；没写 `presenter` 的 beat 都按形式放，单个 beat 写了就以 beat 为准（bubble / pip 片子里开头结尾照样可以写 `"presenter": "full"`）。

| form | 样子 | 选项 |
|---|---|---|
| `full` 全屏口播 | 人铺满全屏；需要版面的效果自动让到 card / side | — |
| `bubble` 圆形头像 | 人在一个圆里（细描边 + 软阴影，按 focus 裁脸），图形和字占画面其余部分，圆一直不动 | `pos` top-right（默认）/ top-left / bottom-right / bottom-left；`size` 直径占宽度比例（9:16 默认 0.45，16:9 按高度 0.5）；`zoom` 圆里放大多少（默认 1.4，脸自动放在圆心） |
| `split` 上下分屏 | 9:16 人占一半（默认下半）、图形占另一半；16:9 左右分 | `pos` bottom / top（16:9：right / left）；`size` 人占的比例（默认 0.5） |
| `pip` 小窗 | 角落里一个圆角小窗，图形占其余 | `pos` 同 bubble；`size` 占宽度比例（9:16 默认 0.34，16:9 0.22） |
| `cutout` 抠像站位 | 抠像主体站在底部，字在头顶 | 只能用带透明通道的素材（.webm / .png / .gif / .webp） |

```json
"presenter": {"src": "assets/video/talk.mp4", "form": "bubble", "pos": "top-right", "size": 0.45, "focus": [56, 28]}
```

先用自己的口播素材看一眼每种形式（每种一张静帧，拼成一张板）：

```bash
python3 scripts/h9/presenter.py preview assets/video/talk.mp4 --focus 56,28 --out work/forms   # 板在 work/forms/stills/board_01.jpg
```

## JSON

```json
"meta": {
  "presenter": {
    "src": "assets/host.mp4",      // 视频或图片；.webm / .png / .gif 默认按抠像（contain）放
    "form": "full",                // 出镜形式：full | bubble | split | pip | cutout（见上一节）
    "pos": "top-right",            // 形式的位置选项（bubble / pip / split）
    "size": 0.45,                  // 形式的大小选项
    "at": "full",                  // 第一个 beat 之前的位置（默认 full，有 form 时默认形式的位置）
    "fit": "cover",                // cover（默认，真人/录屏）| contain（抠像、卡通形象）
    "focus": [50, 35],             // cover 时脸在画面里的位置（%）；contain 默认 [50, 100] 站在底边
    "loop": true,                  // 素材比片子短时接着循环（默认 true）
    "start": 0,                    // 从素材第几秒开始
    "audio": false,                // 用素材自己的声音（默认静音，口播走 meta.voice）
    "tag": "ON AIR",               // 小卡左上角的名牌（只在带框的 card / corner / pip 时出现）
    "ground": "#…"                 // 抠像主体在小卡里的底色（默认跟着当前章节的卡片色）
  }
},
"beats": [
  { "scene": "fx", "fx": "lower3", "t": 0, "presenter": "full", ... },
  { "scene": "fx", "fx": "donut", "t": "@真正", "presenter": "card", ... },
  { "scene": "fx", "fx": "then_now", "t": "@两年前", "presenter": "side", ... },
  { "scene": "fx", "fx": "odometer", "t": "@现在它", "presenter": "corner", ... },
  { "scene": "fx", "fx": "bars", "t": "@一个月", "presenter": {"at": "side", "flip": true}, ... }
]
```

`presenter` 可以写在任何 beat 上；不写时：有 `form` 就按形式放，没有就保持上一个 beat 的位置（主体不动）。`"presenter_force": true` 让这个 beat 保持 `full`、不被自动让位。

| 位置 | 9:16 | 16:9 | 图形排在哪 |
|---|---|---|---|
| `full` | 真人/录屏铺满全屏；抠像站在底部操作栏上方，占约 3/4 宽 | 铺满；抠像放在右侧大半 | 真人：只放 ON_PERSON 效果（其余自动让位）；抠像：头顶那块（9:16）/ 左边（16:9） |
| `card` | 内容区全宽的大卡，占画面下方 55% | 右侧 40% 宽的整高卡 | 9:16：上方 45% 全宽；16:9：左边 |
| `side` | 右侧 40% 宽、从顶到底的整列 | 右侧 40% 宽整列 | 旁边一块竖版面 |
| `corner` | 右上小卡 | 右上小卡 | 9:16：小卡下面；16:9：左边 |
| `bubble` | 圆形头像（默认右上，0.45 宽） | 圆形（默认右上，0.5 高） | 9:16：圆下面全宽；16:9：圆旁边 |
| `split` | 下半（或上半）全幅 | 右半（或左半）全幅 | 另一半 |
| `pip` | 角落圆角小窗（默认右上，0.34 宽） | 角落小窗 | 9:16：小窗下面全宽；16:9：小窗旁边 |
| `hidden` | 淡出 | 淡出 | 全屏 |

对象写法：`{"at": "side", "flip": true}` 左右镜像（主体在左边）；`{"at": "bubble", "pos": "top-left", "size": 0.4}` 改这个 beat 的位置 / 大小；`{"at": "card", "rect": [x, y, w, h]}` 自定义位置（版面像素，9:16 是 1080×1920，16:9 是 1920×1080），图形占剩下最大的一块；`"move": 0.8` 改这次移动的时长。

图形那块都避开字幕带（9:16 约 y 1300 以下、16:9 底部 176px）和章节装置的边框；人（card / side / split）可以伸进字幕带，字幕带底板压在人身上照样读得清。贴边铺满的位置（side、split）没有边框和圆角；有章节装置（相机 / 浏览器 / 手机外框）时，人停在装置底栏上方，side / split 收进内容区。

## 图形怎么让位

每个 beat 构建时，它的版面被临时缩小成「主体让出来的那块」（`X.W` / `X.H` 变成那块的尺寸），这个 beat 加的所有元素被包在一个同样大小的盒子里（`container-type:size`）。所以：

- 效果照常排版，只是在小一点的画面里；`vmin / vw / vh` 换成这块的 `cqmin / cqw / cqh`，`#root.v` 竖屏规则只在竖的那块生效。
- 9:16 的 card / bubble / pip 留出的是一块全宽的横版面，横屏版式的图表直接能用；side 留的是竖版面。字的大小跟着这块的短边走，所以图形那块越大字越大——别把人缩成小卡去换版面。
- 自带全屏背景的效果（stomp、black_slam……）会把那块铺满，放在 card / side 里就是一块面板。
- 版式检查里，全屏大字类效果放在 card / side 旁边算「贴人」，不算全屏大字。

没有 `meta.presenter`、`meta.device` 和章节对象时，这一层完全不参与，旧片子构建结果不变。

## 风格换皮

小卡的圆角、描边、阴影、名牌形状来自风格（`scripts/h9/presenter.py` 的 `SKIN`；风格文件里也可以写 `"presenter_skin": {...}` 覆盖）：minimal 软阴影大圆角，poster 粗黑框 + 实色错位影，flat 厚白边，screen 细线框 + 光晕，sketch 手绘描边 + 实影，pixel 方角硬影……

## 例子

`examples/presenter/video.json`：30 秒，卡通主持人 full → card → side → corner → full → side → card → corner（浏览器章）→ card → full，相机装置 5 章 + 浏览器 1 章。

```bash
python3 scripts/build.py examples/presenter/video.json --aspect 9:16 --style poster
```
