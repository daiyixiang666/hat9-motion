# `area_overlay` · 

<img src="../../assets/previews/fx/area_overlay.webp" width="480" alt="area_overlay 横屏"> <img src="../../assets/previews/fx/area_overlay_v.webp" width="160" alt="area_overlay 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 地图 |
| 适合的句子 | 面积有多大（把 A 叠到 B 上） |
| 建议时长 | 5–6 秒 |
| 参数 | `a`, `b`, `ratio_text`, `unit` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive「Infographics 3D Map Kit」3.2K · 「Map Kit」1.4K · Vox 式地图 |

```json
{
 "scene": "fx",
 "fx": "area_overlay",
 "theme": "paper",
 "topic": "商业拆解",
 "title": "新加坡有多大？放进上海看看",
 "note": "等积投影 · 同一比例尺",
 "a": {
  "name": "新加坡",
  "geojson": "assets/singapore_ne10m.geojson",
  "area": 735.7
 },
 "b": {
  "name": "上海",
  "region": "上海",
  "area": 6340.5
 },
 "unit": "km²",
 "line": "上海的面积，能装下 *8 个多*新加坡。",
 "src": "上海市统计局；新加坡统计局；Natural Earth",
 "t": "@关键词"
}
```

**已知坑**：面积写官方数字（area）；轮廓只是图。小国家用自带 10m GeoJSON 更准。
