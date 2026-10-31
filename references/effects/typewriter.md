# `typewriter` · 打字机 + 光标

<img src="../../assets/previews/fx/typewriter.webp" width="480" alt="typewriter 横屏"> <img src="../../assets/previews/fx/typewriter_v.webp" width="160" alt="typewriter 竖屏">

**怎么动**：one glyph per 2 frames, blinking caret (deterministic blink on the timeline).

| 项 | 内容 |
|---|---|
| 类别 | 字效 |
| 适合的句子 | 提示词、命令、搜索 |
| 建议时长 | 2–3 秒 |
| 参数 | `text` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | T5 · 科技 / 教程类必备 |

```json
{
 "scene": "fx",
 "fx": "typewriter",
 "theme": "ink",
 "topic": "AI 与判断",
 "text": "prompt: 杂志感，柔光",
 "line": "提示词里加上*杂志感*三个字，画面就变了。",
 "host": true,
 "t": "@关键词"
}
```

**已知坑**：无
