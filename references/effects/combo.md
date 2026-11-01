# `combo` · 

<img src="../../assets/previews/fx/combo.webp" width="480" alt="combo 横屏"> <img src="../../assets/previews/fx/combo_v.webp" width="160" alt="combo 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 连续累加的次数 / 门店数 / 点赞数 |
| 建议时长 | 4–5 秒 |
| 参数 | `at`, `count`, `final`, `hits`, `tag`, `unit` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Number Counter 162.6 万 · Shape Elements burst（Graphics Pack 26.2K） |

```json
{
 "scene": "fx",
 "fx": "combo",
 "theme": "red",
 "topic": "商业拆解",
 "count": 24,
 "unit": "家",
 "hits": [
  "新店开业"
 ],
 "final": "2024 年净增 8,914 家|平均每天约 24 家",
 "line": "平均每天新开*约 24 家*店。",
 "src": "蜜雪集团 2024 年度业绩公告（全年净增 8,914 家）",
 "tag": "COMBO",
 "t": "@关键词"
}
```

**已知坑**：count 写真实总数；超过逐次显示的上限时计数器按步跳。
