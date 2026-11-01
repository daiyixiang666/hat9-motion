# `radar` · 

<img src="../../assets/previews/fx/radar.webp" width="480" alt="radar 横屏"> <img src="../../assets/previews/fx/radar_v.webp" width="160" alt="radar 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 多维能力对比（两三家） |
| 建议时长 | 4–5 秒 |
| 参数 | `axes`, `fmt`, `hl`, `max`, `series` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive「Infographics」2.2K · 「Quantum HUD」5.9K |

```json
{
 "scene": "fx",
 "fx": "radar",
 "theme": "ink",
 "topic": "商业拆解",
 "title": "蜜雪和瑞幸，强在不同地方",
 "note": "2024 年 · 每根轴按两家中较大值归一",
 "axes": [
  "门店数",
  "全年收入",
  "单店收入",
  "门店增速"
 ],
 "series": [
  {
   "name": "蜜雪冰城",
   "values": [
    46479,
    248.3,
    53.4,
    23.7
   ]
  },
  {
   "name": "瑞幸咖啡",
   "values": [
    22340,
    344.75,
    154.3,
    37.5
   ]
  }
 ],
 "fmt": [
  "家",
  "亿",
  "万",
  "%"
 ],
 "hl": 2,
 "line": "蜜雪赢在*店多*，瑞幸赢在每家店卖得多。",
 "src": "蜜雪集团、瑞幸咖啡 2024 年年报",
 "t": "@关键词"
}
```

**已知坑**：每根轴各自归一，图形只看相对强弱；具体数值看标注。
