# `whip_carry` · 甩镜带物（转场）

<img src="../../assets/previews/fx/tr_whip_carry.webp" width="360" alt="whip_carry"> <img src="../../assets/previews/fx/tr_whip_carry_v.webp" width="140" alt="whip_carry 竖屏">

**怎么动**：甩镜转场：两个场景都横向甩开、带水平动态模糊，同时一个元素锁在画面里不动，跨过剪辑点带进下一拍——上一句里被强调（*…*）的词，或下一拍写的 `carry`。

| 项 | 内容 |
|---|---|
| 类别 | 转场 |
| 写法 | 写在下一个 beat 上：`"tr": "whip_carry"` |
| 适合 | 前一拍的结论要带进下一拍（「加盟费只占 2.5%」→ 下一拍拆收入） |
| 时长 | 剪辑点前后约 0.3 + 0.6 秒 |
| 参数 | `carry`（写在下一拍上，可选） |
| 横屏 / 竖屏 | ✓ / ✓ |
| 跟风格换皮 | 颜色只用风格的 token |
| 什么时候用 | 两拍讲的是同一件事的两面 |
| 什么时候不用 | 两拍毫无关系（带过去的词会显得莫名其妙） |

```json
{"scene": "fx", "fx": "magnet_sort", "tr": "whip_carry", "carry": "加盟费只占 2.5%", "…": "…"}
```

**实现**：`scripts/h9/fx/fx2_transitions.py`，由 `scripts/h9/fx.py` 的 `transition()` 调用。
