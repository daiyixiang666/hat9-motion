# `street_map` · 

<img src="../../assets/previews/fx/street_map.webp" width="480" alt="street_map 横屏"> <img src="../../assets/previews/fx/street_map_v.webp" width="160" alt="street_map 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 地图 |
| 适合的句子 | 街区、门店位置、步行路线（示意或自带数据） |
| 建议时长 | 5–6 秒 |
| 参数 | `geojson`, `hl`, `route`, `route_label` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive「Map Kit」1.4K · 「3D Map Generator」1.2K |

```json
{
 "scene": "fx",
 "fx": "street_map",
 "theme": "paper",
 "topic": "商业拆解",
 "title": "一个路口，三家奶茶店",
 "note": "示意地图 · 自绘 GeoJSON",
 "geojson": "assets/street_demo.geojson",
 "route": [
  [
   120.0031,
   30.00125
  ],
  [
   120.0031,
   30.0018
  ],
  [
   120.005,
   30.0018
  ],
  [
   120.005,
   30.0027
  ],
  [
   120.00485,
   30.0027
  ]
 ],
 "hl": "奶茶店 C",
 "mock": "示意",
 "line": "出了地铁口，*不到 400 米*就路过三家奶茶店。",
 "src": "示意地图（自绘）",
 "t": "@关键词"
}
```

**已知坑**：不抓取街道数据：只用你给的 GeoJSON；示意图要加 mock。
