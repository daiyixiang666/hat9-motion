# `search_box` · 

<img src="../../assets/previews/fx/search_box.webp" width="480" alt="search_box 横屏"> <img src="../../assets/previews/fx/search_box_v.webp" width="160" alt="search_box 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 界面 |
| 适合的句子 | 「我搜了一下」、查一手来源 |
| 建议时长 | 4.5–6 秒（有结果时） |
| 参数 | `button`, `count`, `engine`, `hl`, `mock`, `pick`, `query`, `results`, `suggest` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Envato「Search Screen Pro」Popular 第 7 |

```json
{
 "scene": "fx",
 "fx": "search_box",
 "theme": "paper",
 "topic": "商业拆解",
 "line": "查一个数字，先找*一手来源*，别只看转述。",
 "engine": "搜索",
 "query": "蜜雪冰城 门店数",
 "suggest": [
  "蜜雪冰城 门店数 2024",
  "蜜雪冰城 门店数 麦当劳",
  "蜜雪冰城 门店数 海外"
 ],
 "results": [
  {
   "title": "蜜雪集团 2024 年度业绩公告",
   "url": "hkexnews.hk · 02097",
   "snippet": "截至 2024 年 12 月 31 日，门店网络共 46,479 家"
  },
  {
   "title": "McDonald's Corporation 2024 Form 10-K",
   "url": "sec.gov",
   "snippet": "Systemwide restaurants at year end: 43,477"
  },
  {
   "title": "某自媒体：蜜雪门店已超 5 万家？",
   "url": "转述 · 未注明来源",
   "snippet": "转了三手的数字，和公告对不上"
  }
 ],
 "hl": [
  "门店",
  "46,479",
  "43,477"
 ],
 "pick": 0,
 "mock": "示意页面",
 "src": "蜜雪集团 2024 年报；麦当劳 2024 年 10-K",
 "t": "@关键词"
}
```

**已知坑**：结果写真实标题和网址；示意页面请加 mock；hl 默认取查询里的词。
