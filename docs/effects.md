# 效果目录 · Effects

每个效果都是 `scripts/h9/aefx.py` 里的一个函数，在 `video.json` 里写成一个 beat：

```json
{"scene": "fx", "fx": "stomp", "words": ["大家", "都在用", "AI"], "t": "@大家"}
```

排名和人气依据见 [`research/ae_popular.md`](../research/ae_popular.md)。横屏、竖屏同一套参数。

## 效果

### `parallax` — 2.5D 照片视差 (#2, VoluMax/Photomotion; MDMZ 1171万播放)

<img src="../assets/previews/fx/parallax.webp" width="480" alt="parallax">

clean plate + cut-out subject on separate depths, the camera dollies in so the subject separates from the background; optional title sits BETWEEN the layers.

- 参数：`fg`, `plate`, `text`
- 人气：VoluMax 2.64万份 · MDMZ 教程 1171万播放

### `burst` — 形状元素爆发 (Shape Elements burst)

<img src="../assets/previews/fx/burst.webp" width="480" alt="burst">

radial lines + ring + dots fire as the word slams in.

- 参数：`text`
- 人气：Graphics Pack 2.62万份 · SonduckFilm 321万播放

### `stomp` — 重拍排版 Stomp (#4, TypoKing 1.34万份; B站动态歌词排版 898万)

<img src="../assets/previews/fx/stomp.webp" width="480" alt="stomp">

one word per beat slams full-frame, sizes alternate, every third beat inverts the frame; a 2-frame jolt on each hit. With narration timestamps each word lands the moment it is spoken (like lyric typography).

- 参数：`beat`, `words`
- 人气：TypoKing 1.34万份 · B站动态歌词排版 898万播放

### `mask_up` — 行遮罩上移 (the most-used title reveal)

<img src="../assets/previews/fx/mask_up.webp" width="480" alt="mask_up">

each line rises out of its own mask, expo.out.

- 参数：`sub`, `text`
- 人气：YouTube 153万 / 145万播放

### `mosaic` — 照片墙拼合 (#6, Mosaic Photo Reveal 1.6万份)

<img src="../assets/previews/fx/mosaic.webp" width="480" alt="mosaic">

12 tiles fly in from depth and assemble a wall, then the camera pushes into one tile until it fills the frame.

- 参数：`images`
- 人气：Mosaic Photo Reveal 1.6万份

### `cartoon` — 卡通冲击特效 (#7, 140 Flash FX 1.47万份)

<img src="../assets/previews/fx/cartoon.webp" width="480" alt="cartoon">

speed lines, a jagged impact star, smoke puffs — on twos (12 fps steps).

- 参数：`text`
- 人气：140 Flash FX 1.47万份

### `apple_blur` — 苹果式逐字模糊渐显 (#9, 206.8万 2025)

<img src="../assets/previews/fx/apple_blur.webp" width="480" alt="apple_blur">

each glyph fades up out of a soft blur and a small rise, grey→white.

- 参数：`sub`, `text`
- 人气：206.8万播放（2025）

### `portal` — 瞳孔穿梭 / 穿洞推进 (#10, B站364.5万 2025)

<img src="../assets/previews/fx/portal.webp" width="480" alt="portal">

a hole opens on a point of frame A showing frame B, then the camera dives through the hole until B fills the screen.

- 参数：`image`, `image2`, `x`, `y`
- 人气：B站 364.5万播放（2025）

### `shine` — 光泽扫过 (Shine / CC Light Sweep) on a title

<img src="../assets/previews/fx/shine.webp" width="480" alt="shine">

a bright band travels across the glyphs once.

- 参数：`text`
- 人气：Gold Simple Titles 1.1万份

### `neon` — 霓虹点亮 (#12, Neon Sign Kit 1万份)

<img src="../assets/previews/fx/neon.webp" width="480" alt="neon">

tube text stutters on (stepped flicker pattern), then holds with a steady glow.

- 参数：`color`, `text`
- 人气：Neon Sign Kit 1万份

### `notify` — 手机通知界面 (#13, Envato Elements「Elements」热门第1)

<img src="../assets/previews/fx/notify.webp" width="480" alt="notify">

iOS-style banners drop in one after another and stack.

- 参数：`items`
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

### `triple` — 三连 (like · coin · favourite)

<img src="../assets/previews/fx/triple.webp" width="480" alt="triple">

icons pop in sequence, each with a ring burst; the B站/抖音 staple ending.

- 参数：`labels`
- 人气：555 Animated Icons 6.4K份 · B站三连 157万

### `callout` — 标注引线 (Callout title)

<img src="../assets/previews/fx/callout.webp" width="480" alt="callout">

a dot pops on the subject, the leader line draws out, the label slides along it.

- 参数：`image`, `sub`, `text`, `x`, `y`
- 人气：Call-Out Titles 4.5K份

### `odometer` — 数字滚轮 (Odometer / number wheel)

<img src="../assets/previews/fx/odometer.webp" width="480" alt="odometer">

each digit column spins down to its value, staggered.

- 参数：`sub`, `unit`, `value`
- 人气：YouTube 162.6万播放

### `collage` — 拼贴剪纸 (#21, Fakeplastictree Collage 203.5万)

<img src="../assets/previews/fx/collage.webp" width="480" alt="collage">

torn-edge photo pieces land on paper on twos, tape, a hand-drawn arrow.

- 参数：`images`, `text`
- 人气：Fakeplastictree 203.5万播放

### `write_on` — 描边书写 → 填色 (Trim Paths on text / 手写签名)

<img src="../assets/previews/fx/write_on.webp" width="480" alt="write_on">

glyph outlines draw on, then the fill floods in.

- 参数：`text`
- 人气：YouTube 128.5万 / 123.7万播放

### `match_cut` — 文字匹配剪辑 Text Match Cut (#23, Envato Elements 标题热门第1/2)

<img src="../assets/previews/fx/match_cut.webp" width="480" alt="match_cut">

the word holds its exact place while everything around it hard-cuts — background, colour field and typeface change every few frames. Each cut is a designed pair (ground + type treatment), so the word always reads.

- 参数：`images`, `text`
- 人气：Envato Elements 标题热门第1、2名

### `impact` — 冲击抖动 (#24, Bricks 106.8万 2025)

<img src="../assets/previews/fx/impact.webp" width="480" alt="impact">

the title slams in and the whole frame takes a decaying camera shake.

- 参数：`sub`, `text`
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

glyphs start spread wide and drift together while sharpening — done with transforms (x offset ∝ distance from the centre), so it never snaps to whole pixels like letter-spacing would.

- 参数：`spread`, `sub`, `text`
- 人气：电影片头经典

### `flip3d` — 逐字三维翻转 (3D Flip per character)

<img src="../assets/previews/fx/flip3d.webp" width="480" alt="flip3d">

rotateX from -100°, transform-origin bottom, perspective on the line.

- 参数：`text`
- 人气：文字动效合集高频

### `ghost_type` — 巨型虚影背景字 (Ghost / outline background type)

<img src="../assets/previews/fx/ghost_type.webp" width="480" alt="ghost_type">

a huge outlined word drifts behind small foreground copy.

- 参数：`ghost`, `sub`, `text`
- 人气：B站「碰撞吧！」107万播放

### `lockup` — 中英双语锁定 + 注释引线 (type specimen lockup)

<img src="../assets/previews/fx/lockup.webp" width="480" alt="lockup">

headline, latin line, two leader-line annotations.

- 参数：`notes`, `sub`, `text`
- 人气：B站「碰撞吧！」107万播放

### `diffuse` — 弥散光 (diffuse gradient blobs)

<img src="../assets/previews/fx/diffuse.webp" width="480" alt="diffuse">

3 soft colour blobs orbit slowly behind a calm title.

- 参数：`colors`, `sub`, `text`
- 人气：B站「碰撞吧！」107万播放

### `gooey` — 粘性碰撞 (gooey metaballs)

<img src="../assets/previews/fx/gooey.webp" width="480" alt="gooey">

two balls approach, merge with a liquid neck, bounce apart; squash & stretch.

- 参数：—
- 人气：S5 · B站「碰撞吧！」107万播放

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
