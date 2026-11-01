# `cite_video` · 

<img src="../../assets/previews/fx/cite_video.webp" width="480" alt="cite_video 横屏"> <img src="../../assets/previews/fx/cite_video_v.webp" width="160" alt="cite_video 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 引用 |
| 适合的句子 | 引用别人的视频片段 |
| 建议时长 | 跟引用片段一样长 |
| 参数 | `caption`, `focus`, `hl`, `image`, `kicker`, `license`, `quote`, `source`, `start`, `title`, `video`, `year` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 片段真实播放 · 进度条 · 时间码 |

```json
{
 "scene": "fx",
 "fx": "cite_video",
 "theme": "ink",
 "topic": "商业拆解",
 "video": "assets/working_dollars_1957.mp4",
 "start": 0,
 "title": "Working Dollars (1957)",
 "source": "Prelinger Archives · archive.org",
 "year": "1957",
 "license": "公有领域",
 "caption": "书架上的四本书：*SALES · EARNINGS · DIVIDENDS · GROWTH*",
 "kicker": "档案影像",
 "line": "1957 年的一部动画片，就在教普通人看*销售、盈利和增长*。",
 "src": "Prelinger Archives（公有领域）",
 "t": "@关键词"
}
```

**已知坑**：视频要能逐帧定位（mp4 / webm）；字幕写原话或描述，别编台词。
