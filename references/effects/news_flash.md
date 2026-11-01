# `news_flash` · 

<img src="../../assets/previews/fx/news_flash.webp" width="480" alt="news_flash 横屏"> <img src="../../assets/previews/fx/news_flash_v.webp" width="160" alt="news_flash 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 类型 |
| 适合的句子 | 刚刚 / 快讯 / 某公司宣布 |
| 建议时长 | 4.5–6 秒（滚动条越长越好看） |
| 参数 | `at`, `headline`, `image`, `image_label`, `items`, `kicker`, `live`, `source`, `text`, `theme`, `ticker`, `ticker_label`, `time` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | talkcraft news-card-desk · 速报类口播 |

```json
{
 "scene": "fx",
 "fx": "news_flash",
 "theme": "paper",
 "topic": "商业拆解",
 "kicker": "快讯",
 "time": "2025-03-03",
 "source": "新华网 · 澎湃新闻",
 "headline": "蜜雪集团今日在港交所挂牌上市",
 "items": [
  [
   "开盘",
   "262 港元，较发行价涨 29.4%"
  ],
  [
   "收盘",
   "290 港元，首日涨 43.2%"
  ],
  [
   "市值",
   "收盘约 1093 亿港元"
  ]
 ],
 "ticker": [
  "发行价 202.5 港元",
  "股票代码 02097",
  "2025 年开年港股最大 IPO",
  "全球门店 46,479 家（截至 2024 年底）"
 ],
 "line": "2025 年 3 月 3 日，蜜雪上市*首日涨了四成多*。",
 "src": "新华网 2025-03-03 · 澎湃新闻",
 "t": "@关键词"
}
```

**已知坑**：items / ticker 必须是可查的事实并写 src；time 写发布日期，不写就只显示来源。
