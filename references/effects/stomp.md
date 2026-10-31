# `stomp` · 重拍排版 Stomp (#4, TypoKing 1.34万份; B站动态歌词排版 898万)

<img src="../../assets/previews/fx/stomp.webp" width="480" alt="stomp 横屏"> <img src="../../assets/previews/fx/stomp_v.webp" width="160" alt="stomp 竖屏">

**怎么动**：one word per beat slams full-frame, sizes alternate, every third beat inverts the frame; a 2-frame jolt on each hit. words: 1–12 (a list, "a|b|c", or just text → split into words). Long words wrap to two lines. With narration timestamps each word lands the moment it is spoken (like lyric typography).

| 项 | 内容 |
|---|---|
| 类别 | 字效 |
| 适合的句子 | 节奏快的一句话、金句拆字 |
| 建议时长 | 按口播，每词 0.3–0.5 秒 |
| 参数 | `beat`, `text`, `words` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | TypoKing 1.34万份 · B站动态歌词排版 898万播放 |

```json
{
 "scene": "fx",
 "fx": "stomp",
 "theme": "paper",
 "topic": "商业拆解",
 "words": [
  "一杯",
  "4 块钱",
  "柠檬水",
  "一年净赚",
  "44 亿"
 ],
 "line": "一杯 4 块钱的柠檬水，一年净赚 *44 亿*。",
 "src": "蜜雪集团 2024 年度业绩公告",
 "t": "@关键词"
}
```

**已知坑**：词太长会自动缩字号；一页最好 2–4 个字。
