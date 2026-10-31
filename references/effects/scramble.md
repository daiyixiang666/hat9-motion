# `scramble` · 乱码解码 (Decoder / Scramble)

<img src="../../assets/previews/fx/scramble.webp" width="480" alt="scramble 横屏"> <img src="../../assets/previews/fx/scramble_v.webp" width="160" alt="scramble 竖屏">

**怎么动**：every slot is a reel of random glyphs that steps (not slides) onto its real character, slots settling left→right. Pure transforms with a steps() ease, so it seeks in any order.

| 项 | 内容 |
|---|---|
| 类别 | 字效 |
| 适合的句子 | 技术名词、英文代号 |
| 建议时长 | 2–3 秒 |
| 参数 | `pool`, `text` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 科技类标题高频 |

```json
{
 "scene": "fx",
 "fx": "scramble",
 "theme": "ink",
 "topic": "AI 与判断",
 "text": "JUDGMENT",
 "line": "AI 时代最贵的能力，叫*判断力*。",
 "host": true,
 "t": "@关键词"
}
```

**已知坑**：无
