# `chapter_bar` · 

<img src="../../assets/previews/fx/chapter_bar.webp" width="480" alt="chapter_bar 横屏"> <img src="../../assets/previews/fx/chapter_bar_v.webp" width="160" alt="chapter_bar 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 结构 |
| 适合的句子 | 目录、第几部分、章节过渡 |
| 建议时长 | 2–3 秒 |
| 参数 | `chapters`, `hl`, `now`, `title` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | talkcraft chapter-progress-list · B 站分 P 目录 |

```json
{
 "scene": "fx",
 "fx": "chapter_bar",
 "theme": "paper",
 "topic": "商业拆解",
 "title": "这期分三部分",
 "chapters": [
  "门店有多少",
  "钱从哪来",
  "为什么不怕便宜"
 ],
 "hl": 1,
 "line": "接下来第二部分：*钱从哪来*。",
 "t": "@关键词"
}
```

**已知坑**：无
