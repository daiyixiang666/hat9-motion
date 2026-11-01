# `word_swap` · 

<img src="../../assets/previews/fx/word_swap.webp" width="480" alt="word_swap 横屏"> <img src="../../assets/previews/fx/word_swap_v.webp" width="160" alt="word_swap 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 字效 |
| 适合的句子 | 「不是 A，是 B」「它能做 X / Y / Z」 |
| 建议时长 | 每个词 0.5–0.8 秒 |
| 参数 | `host`, `mode`, `post`, `pre`, `words` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | talkcraft word-slot-cycle · Rotating Words 标题模板 |

```json
{
 "scene": "fx",
 "fx": "word_swap",
 "theme": "red",
 "topic": "AI 与判断",
 "host": true,
 "pre": "AI 能帮你",
 "words": [
  "写稿",
  "配音",
  "做图",
  "剪辑"
 ],
 "line": "AI 能帮你写稿、配音、做图、*剪辑*。",
 "t": "@关键词"
}
```

**已知坑**：replace 模式只用前两个词。
