# `parallax` · 2.5D 照片视差 (#2, VoluMax/Photomotion; MDMZ 1171万播放)

<img src="../../assets/previews/fx/parallax.webp" width="480" alt="parallax 横屏"> <img src="../../assets/previews/fx/parallax_v.webp" width="160" alt="parallax 竖屏">

**怎么动**：clean plate + cut-out subject on separate depths, the camera dollies in so the subject separates from the background; optional title sits BETWEEN the layers.

| 项 | 内容 |
|---|---|
| 类别 | 照片 |
| 适合的句子 | 开场大图、人物故事 |
| 建议时长 | 2–4 秒 |
| 参数 | `fg`, `plate`, `text` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VoluMax 2.64万份 · MDMZ 教程 1171万播放 |

```json
{
 "scene": "fx",
 "fx": "parallax",
 "theme": "ink",
 "topic": "商业拆解",
 "text": "成交",
 "plate": "assets/broll/silhou_plate.jpg",
 "fg": "assets/broll/silhou_fg.png",
 "line": "流量再大，最后都要落到*成交*。",
 "t": "@关键词"
}
```

**已知坑**：需要先抠图 + 修补背景板（scripts/cutout 流程）；主体太小时视差不明显。
