# `portal` · 瞳孔穿梭 / 穿洞推进 (#10, B站364.5万 2025)

<img src="../../assets/previews/fx/portal.webp" width="480" alt="portal 横屏"> <img src="../../assets/previews/fx/portal_v.webp" width="160" alt="portal 竖屏">

**怎么动**：a hole opens on a point of frame A showing frame B, then the camera dives through the hole until B fills the screen.

| 项 | 内容 |
|---|---|
| 类别 | 照片 |
| 适合的句子 | 从一个画面进入另一个话题 |
| 建议时长 | 2.5–3 秒 |
| 参数 | `image`, `image2`, `x`, `y` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | B站 364.5万播放（2025） |

```json
{
 "scene": "fx",
 "fx": "portal",
 "theme": "ink",
 "topic": "商业拆解",
 "image": "assets/broll/meeting.jpg",
 "image2": "assets/broll/charts.jpg",
 "x": 41,
 "y": 53,
 "line": "钻进这张报表，看看*钱从哪来*。",
 "t": "@关键词"
}
```

**已知坑**：x / y 要对准画面里的「洞」（瞳孔、杯口、窗）；竖屏裁切后坐标会变。
