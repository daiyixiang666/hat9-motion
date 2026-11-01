# `scatter` · 

<img src="../../assets/previews/fx/scatter.webp" width="480" alt="scatter 横屏"> <img src="../../assets/previews/fx/scatter_v.webp" width="160" alt="scatter 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 两个指标的关系（店数对收入、价格对销量） |
| 建议时长 | 4.5–6 秒（点多就更长） |
| 参数 | `hl`, `hl_note`, `labels`, `log`, `points`, `quad`, `size_lab`, `xlab`, `xunit`, `ylab`, `yunit` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive「Infographic Maker」2.6K · 「Infographics」2.2K |

```json
{
 "scene": "fx",
 "fx": "scatter",
 "theme": "ink",
 "topic": "商业拆解",
 "title": "店多，不等于每家店赚得多",
 "note": "2024 年 · 气泡 = 单店年收入",
 "points": [
  [
   "蜜雪冰城",
   46479,
   248.3,
   53.4
  ],
  [
   "瑞幸咖啡",
   22340,
   344.75,
   154.3
  ],
  [
   "古茗",
   9914,
   87.91,
   88.7
  ],
  [
   "霸王茶姬",
   6440,
   124.05,
   192.6
  ]
 ],
 "xlab": "门店数",
 "xunit": "家",
 "ylab": "全年收入",
 "yunit": "亿元",
 "size_lab": "单店收入（万元）",
 "hl": "蜜雪冰城",
 "hl_note": "4.6 万家店，单店收入约 53 万",
 "line": "店最多的蜜雪，*单店收入*却是四家里最低的。",
 "src": "各公司 2024 年年报 / 招股书（单店收入 = 收入 ÷ 年末门店数）",
 "t": "@关键词"
}
```

**已知坑**：无
