# `beat_cut` · 

<img src="../../assets/previews/fx/beat_cut.webp" width="480" alt="beat_cut 横屏"> <img src="../../assets/previews/fx/beat_cut_v.webp" width="160" alt="beat_cut 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 节奏 |
| 适合的句子 | 音乐卡点、快节奏蒙太奇 |
| 建议时长 | 按小节，100 bpm 每拍 0.6 秒 |
| 参数 | `every`, `items`, `theme`, `ticks` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 纯音乐 3.6 秒，100 bpm，每拍一切 |

```json
{
 "scene": "fx",
 "fx": "beat_cut",
 "theme": "lemon",
 "items": [
  "卖*原料*",
  "assets/clips/tanks.mp4",
  "卖*包材*",
  "assets/clips/factory.mp4",
  "卖*设备*",
  "assets/clips/harbor.mp4",
  "卖给 *4.6 万*家店"
 ],
 "t": "@关键词"
}
```

**已知坑**：要有 meta.bpm 或 beats，否则按 0.5 秒切。
