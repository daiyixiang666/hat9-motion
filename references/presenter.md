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
- 人是这条片子的看点：开头和结尾用 `full`，中间多用 `card` / `side` / `corner` 让图表从人身边长出来，`hidden` 只给真正需要整屏的画面，别连着藏好几句。
- `focus` 写脸在原视频里的位置（百分比），竖屏裁切时脸不会被切掉。

## JSON

```json
"meta": {
  "presenter": {
    "src": "assets/host.mp4",      // 视频或图片；.webm / .png / .gif 默认按抠像（contain）放
    "at": "full",                  // 第一个 beat 之前的位置（默认 full）
    "fit": "cover",                // cover（默认，真人/录屏）| contain（抠像、卡通形象）
    "focus": [50, 35],             // cover 时脸在画面里的位置（%）；contain 默认 [50, 100] 站在底边
    "loop": true,                  // 素材比片子短时接着循环（默认 true）
    "start": 0,                    // 从素材第几秒开始
    "audio": false,                // 用素材自己的声音（默认静音，口播走 meta.voice）
    "tag": "ON AIR",   // 小卡左上角的名牌（只在 card / side / corner 时出现）
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

`presenter` 可以写在任何 beat 上；不写就保持上一个 beat 的位置（主体不动）。

| 位置 | 9:16 | 16:9 | 图形排在哪 |
|---|---|---|---|
| `full` | 真人/录屏铺满全屏；抠像站在底部操作栏上方，占约 3/4 宽 | 铺满；抠像放在右侧大半 | 真人：全屏叠在人上（选不铺底的效果：lower3、mask_up、callout）；抠像：头顶那块（9:16）/ 左边（16:9） |
| `card` | 下方居中的小卡（约 1/3 宽） | 右下的小卡 | 9:16：上方一块正好 16:9 的版面；16:9：左边 |
| `side` | 右侧高卡（约 0.42 宽） | 右侧 0.36 宽整高 | 左边一块竖版面 |
| `corner` | 右上小卡 | 右上小卡 | 9:16：小卡下面；16:9：左边 |
| `hidden` | 淡出 | 淡出 | 全屏 |

对象写法：`{"at": "side", "flip": true}` 左右镜像（主体在左边）；`{"at": "card", "rect": [x, y, w, h]}` 自定义位置（版面像素，9:16 是 1080×1920，16:9 是 1920×1080），图形占剩下最大的一块；`"move": 0.8` 改这次移动的时长。

所有位置都避开字幕带（9:16 约 y 1300 以下、16:9 底部 176px）和章节装置的边框。

## 图形怎么让位

每个 beat 构建时，它的版面被临时缩小成「主体让出来的那块」（`X.W` / `X.H` 变成那块的尺寸），这个 beat 加的所有元素被包在一个同样大小的盒子里（`container-type:size`）。所以：

- 效果照常排版，只是在小一点的画面里；`vmin / vw / vh` 换成这块的 `cqmin / cqw / cqh`，`#root.v` 竖屏规则只在竖的那块生效。
- 9:16 的 card 留出的正好是 16:9 版面，横屏版式的图表直接能用；side 留的是竖版面。
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
