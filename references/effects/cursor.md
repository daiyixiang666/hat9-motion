# `cursor` · 

<img src="../../assets/previews/fx/cursor.webp" width="480" alt="cursor 横屏"> <img src="../../assets/previews/fx/cursor_v.webp" width="160" alt="cursor 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 屏幕 |
| 适合的句子 | 在截图 / 录屏上指给观众看：点哪里、拖什么、输入什么 |
| 建议时长 | 每个动作 0.8–1.2 秒 + 1 秒 |
| 参数 | `dark_chrome`, `frame`, `image`, `path`, `start`, `steps`, `tab`, `theme`, `trail`, `url`, `video`, `zoom` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive Phone 7 App & Gestures 2.6K |

```json
{
 "scene": "fx",
 "fx": "cursor",
 "theme": "ink",
 "topic": "做内容",
 "line": "在画廊里点一下，就能*切到另一条成片*。",
 "image": "../screens/assets/gallery_top.jpg",
 "frame": "browser",
 "url": "daiyixiang666.github.io/hat9-motion/gallery/",
 "zoom": 1.5,
 "path": [
  {
   "act": "hover",
   "x": 113,
   "y": 252,
   "label": "5 条成片"
  },
  {
   "act": "click",
   "x": 569,
   "y": 252,
   "label": "切到地图纪录"
  },
  {
   "act": "click",
   "x": 40,
   "y": 752,
   "label": "播放"
  }
 ],
 "t": "@关键词"
}
```

**已知坑**：path 的坐标是相对原图的（0–1 或原图像素）；静态截图点了不会变，要变化请换成录屏或几张截图。
