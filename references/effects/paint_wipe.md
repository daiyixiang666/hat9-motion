# `paint_wipe` · 三笔刷屏（转场）

<img src="../../assets/previews/fx/tr_paint_wipe.webp" width="360" alt="paint_wipe"> <img src="../../assets/previews/fx/tr_paint_wipe_v.webp" width="140" alt="paint_wipe 竖屏">

**怎么动**：三道宽笔刷带着毛糙的鬃毛边扫过、在剪辑点前盖满画面；然后每笔的尾巴追着头跑出去，露出下一拍。颜色用风格的强调色和文字色。

| 项 | 内容 |
|---|---|
| 类别 | 转场 |
| 写法 | 写在下一个 beat 上：`"tr": "paint_wipe"` |
| 适合 | 节奏快的转段、手作感 |
| 时长 | 剪辑点前后约 0.3 + 0.6 秒 |
| 参数 | — |
| 横屏 / 竖屏 | ✓ / ✓ |
| 跟风格换皮 | 颜色只用风格的 token |
| 什么时候用 | 情绪上扬、需要一个有能量的转段 |
| 什么时候不用 | 严肃 / 沉重的段落 |

```json
{"scene": "fx", "fx": "pour_fill", "tr": "paint_wipe", "…": "…"}
```

**实现**：`scripts/h9/fx/fx2_transitions.py`，由 `scripts/h9/fx.py` 的 `transition()` 调用。
