# `funnel` · 

<img src="../../assets/previews/fx/funnel.webp" width="480" alt="funnel 横屏"> <img src="../../assets/previews/fx/funnel_v.webp" width="160" alt="funnel 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 转化漏斗、层层筛选 |
| 建议时长 | 4–5 秒 |
| 参数 | `dec`, `floor`, `hl`, `mode`, `pct_label`, `stages`, `unit` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive「Simple Infographics」1.9K · 「Infographic Maker」2.6K |

```json
{
 "scene": "fx",
 "fx": "funnel",
 "theme": "paper",
 "topic": "商业拆解",
 "title": "11 亿网民，有多少人在看微短剧",
 "note": "截至 2024 年 6 月 · 占网民比例",
 "stages": [
  [
   "网民",
   1099670000
  ],
  [
   "网络支付用户",
   969000000
  ],
  [
   "微短剧用户",
   576000000
  ]
 ],
 "unit": "人",
 "mode": "share",
 "pct_label": "占网民",
 "hl": 2,
 "line": "一半以上的网民，*已经在看微短剧*。",
 "src": "CNNIC 第 54 次《中国互联网络发展状况统计报告》",
 "t": "@关键词"
}
```

**已知坑**：mode=share 用于互相包含的人群（不是严格的转化）；conv 才是逐层转化。
