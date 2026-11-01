# `cite_stack` · 

<img src="../../assets/previews/fx/cite_stack.webp" width="480" alt="cite_stack 横屏"> <img src="../../assets/previews/fx/cite_stack_v.webp" width="160" alt="cite_stack 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 引用 |
| 适合的句子 | 多个信源交叉验证 |
| 建议时长 | 每个信源 1–1.5 秒 |
| 参数 | `claim`, `kicker`, `sources`, `tally` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 交叉验证：每条来源打勾，连线汇到结论 |

```json
{
 "scene": "fx",
 "fx": "cite_stack",
 "theme": "paper",
 "topic": "AI 与判断",
 "claim": "ChatGPT 是增长最快的消费级应用",
 "sources": [
  {
   "kind": "帖子",
   "name": "Sam Altman",
   "date": "2022-12-05",
   "text": "上线 5 天，用户破 100 万",
   "verdict": "ok"
  },
  {
   "kind": "新闻",
   "name": "Reuters · UBS",
   "date": "2023-02-01",
   "text": "上线约 2 个月，月活约 1 亿",
   "verdict": "ok"
  },
  {
   "kind": "发布会",
   "name": "OpenAI DevDay",
   "date": "2025-10-06",
   "text": "每周活跃用户 8 亿",
   "verdict": "ok"
  }
 ],
 "line": "三个来源对得上：*五天一百万，两个月一亿*，现在每周八亿。",
 "src": "@sama · Reuters · TechCrunch（DevDay 2025）",
 "t": "@关键词"
}
```

**已知坑**：无
