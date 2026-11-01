# `share_card` · 

<img src="../../assets/previews/fx/share_card.webp" width="480" alt="share_card 横屏"> <img src="../../assets/previews/fx/share_card_v.webp" width="160" alt="share_card 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 类型 |
| 适合的句子 | 结尾金句、可截图转发的结论 |
| 建议时长 | 4–5 秒（快门在拍末前 1.1 秒） |
| 参数 | `by`, `date`, `export`, `handle`, `hint`, `host`, `kicker`, `quote`, `text` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 小红书 / 朋友圈金句图 · scripts/share_card.py 导出单张 |

```json
{
 "scene": "fx",
 "fx": "share_card",
 "theme": "paper",
 "topic": "商业拆解",
 "quote": "看懂谁在*赚钱*，比看懂谁在卖货更重要。",
 "by": "第九顶帽子 · 商业拆解第 07 期",
 "handle": "@第九顶帽子",
 "date": "2025.03",
 "line": "这句话，*截图*收好。",
 "src": "第九顶帽子",
 "t": "@关键词"
}
```

**已知坑**：导出单张图用 scripts/share_card.py（3:4 / 4:5 / 1:1 / 9:16）。
