# `gif_clip` · 

<img src="../../assets/previews/fx/gif_clip.webp" width="480" alt="gif_clip 横屏"> <img src="../../assets/previews/fx/gif_clip_v.webp" width="160" alt="gif_clip 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 照片 |
| 适合的句子 | 动图、表情包、短循环 |
| 建议时长 | 3–5 秒 |
| 参数 | `caption`, `fit`, `focus`, `frame`, `gif`, `speed`, `src`, `title` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive Photo Frames Slideshow 3.6K（Openers 第 3）· Mixkit Polaroid Slideshow |

```json
{
 "scene": "fx",
 "fx": "gif_clip",
 "theme": "paper",
 "topic": "做内容",
 "gif": "assets/stomp.gif",
 "frame": "sticker",
 "caption": "stomp.gif · 360 像素",
 "title": "GIF 直接拖进来",
 "line": "GIF 动图拖进来，构建时自动*转成视频*。",
 "src": "GIF 由本仓库的动效预览生成",
 "t": "@关键词"
}
```

**已知坑**：转码在构建时做（ffmpeg），GIF 很大时第一次构建慢。
