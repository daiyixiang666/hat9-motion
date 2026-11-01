# `cite_article` · 

<img src="../../assets/previews/fx/cite_article.webp" width="480" alt="cite_article 横屏"> <img src="../../assets/previews/fx/cite_article_v.webp" width="160" alt="cite_article 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 引用 |
| 适合的句子 | 引用新闻报道 |
| 建议时长 | 2–3 秒 |
| 参数 | `box`, `byline`, `date`, `dek`, `excerpt`, `focus`, `headline`, `hl`, `image`, `kicker`, `outlet`, `points`, `section`, `url` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 「据某某报道」：标题 + 原文摘录 + 要点 |

```json
{
 "scene": "fx",
 "fx": "cite_article",
 "theme": "paper",
 "topic": "AI 与判断",
 "outlet": "Reuters",
 "section": "Technology",
 "headline": "ChatGPT sets record for fastest-growing user base - analyst note",
 "byline": "Krystal Hu",
 "date": "2023-02-01",
 "excerpt": "just two months after launch, making it the fastest-growing consumer application in history",
 "hl": "the fastest-growing consumer application in history",
 "url": "reuters.com/technology/chatgpt-sets-record-fastest-growing-user-base-analyst-note-2023-02-01/",
 "points": [
  "上线约 2 个月，月活约 1 亿（UBS 估算）",
  "TikTok 用了约 9 个月",
  "Instagram 用了约 2 年半"
 ],
 "line": "路透社报道：ChatGPT 两个月月活破亿，是*史上增长最快*的消费级应用。",
 "src": "Reuters 2023-02-01（援引 UBS）",
 "t": "@关键词"
}
```

**已知坑**：无
