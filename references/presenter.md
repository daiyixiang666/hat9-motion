# 主体层 Presenter：主体一直在，只是换位置

一整片都留着同一个主体——口播真人、录屏、卡通形象（透明 webm）或一张图——每个 beat 只决定它**站在哪**：全屏、图表下面的小卡、侧边、角落、或者先藏起来。换位置是一段 0.65 秒的平滑移动（不是切），视频一直往下播。这个 beat 的图形自动排在主体让出来的那块地方。

参考：抖音 7701488753897917723——人一直在，只是全屏 → 下方小卡 → 侧边 → 角落 → 回全屏，信息卡从他身边长出来，所以画面信息每 1–2 秒就换一次。

## 什么时候用

- 有一个能一直出现的主体：真人口播、卡通形象口播、一段长录屏、一张产品图。
- 想要「信息围着人动」而不是一屏一屏硬切。
- 不用：纯图表片、快切蒙太奇、没有主体的片子。

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
