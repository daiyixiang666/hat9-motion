# `dialogue` · 

<img src="../../assets/previews/fx/dialogue.webp" width="480" alt="dialogue 横屏"> <img src="../../assets/previews/fx/dialogue_v.webp" width="160" alt="dialogue 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 人物 |
| 适合的句子 | 采访、对谈、两个人的观点交锋 |
| 建议时长 | 每句 1–1.5 秒 |
| 参数 | — |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | VideoHive Text Messages 3.8K · Lower Thirds 第 1 名 6.3K |

```json
{
 "scene": "fx",
 "fx": "dialogue",
 "theme": "paper",
 "topic": "做内容",
 "line": "采访类片子，谁在说话要*一眼看出来*。",
 "mock": "示意对话",
 "host": false,
 "speakers": [
  {
   "name": "主持人",
   "role": "第九顶帽子"
  },
  {
   "name": "加盟店老板",
   "role": "示意人物"
  }
 ],
 "lines": [
  [
   "主持人",
   "4 块钱一杯，你还能赚到钱吗？"
  ],
  [
   "加盟店老板",
   "靠的是量，一天要卖几百杯才行。"
  ],
  [
   "主持人",
   "那原料从哪进？"
  ],
  [
   "加盟店老板",
   "全部从总部进，自己不能乱买。"
  ]
 ],
 "t": "@关键词"
}
```

**已知坑**：台词要么是真实原话（写 src），要么标 mock「示意对话」；超过 6 句请把时长放到 6 秒以上。
