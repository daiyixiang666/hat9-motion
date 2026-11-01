# `media` · 

<img src="../../assets/previews/fx/media.webp" width="480" alt="media 横屏"> <img src="../../assets/previews/fx/media_v.webp" width="160" alt="media 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 素材 |
| 适合的句子 | 任意张数的图片 / 视频：1 张、3 张、200 张各是一种编排 |
| 建议时长 | 1–3 张 3–4 秒，几十张以上 4–6 秒 |
| 参数 | `count`, `count_label`, `fxid`, `hl`, `max_video`, `sub`, `t_hl` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 5.4K 份（Openers 第 1） |

```json
{
 "scene": "fx",
 "fx": "media",
 "theme": "ink",
 "topic": "做内容",
 "items": [
  {
   "src": "assets/frames/atlas_h_25.jpg",
   "caption": "货船为什么不走苏伊士了"
  }
 ],
 "line": "只有一张图，就把*整个画面*给它。",
 "preview": "1",
 "band_label": "1 张",
 "t": "@关键词"
}
```

**已知坑**：items 可以混放图片和视频；几十张以上用缩略图拼图，视频只显示静帧。
