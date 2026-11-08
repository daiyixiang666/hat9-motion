# `cold_open` · 

<img src="../../assets/previews/fx/cold_open.webp" width="480" alt="cold_open 横屏"> <img src="../../assets/previews/fx/cold_open_v.webp" width="160" alt="cold_open 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 节奏 |
| 适合的句子 | 片头先画面后说话 |
| 建议时长 | 1–8 秒（按时长伸缩） |
| 参数 | `clips`, `grade`, `kicker`, `sub`, `title` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 电影预告 / 纪录片冷开场 |

```json
{
 "scene": "fx",
 "fx": "cold_open",
 "at_rel": 1.8,
 "clips": [
  "assets/clips/shoppers.mp4",
  "assets/clips/kitchen.mp4",
  "assets/clips/toaster.mp4",
  "assets/clips/gas.mp4"
 ],
 "kicker": "商业拆解",
 "title": "一杯 *¥4* 的生意",
 "sub": "蜜雪冰城 · 2024 年报",
 "t": "@关键词"
}
```

**已知坑**：配音要整体后移（meta.lead），否则会压在开场上。
