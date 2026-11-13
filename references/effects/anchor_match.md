# `anchor_match` · 锚点匹配（转场）

<img src="../../assets/previews/fx/tr_anchor_match.webp" width="360" alt="anchor_match"> <img src="../../assets/previews/fx/tr_anchor_match_v.webp" width="140" alt="anchor_match 竖屏">

**怎么动**：围绕一个贯穿两拍的元素做匹配剪辑，共 16 帧（剪辑点在第 6 帧）：第 0–6 帧，下一拍的底色从下往上盖住上一拍的一切，只留下锚点不动；第 4–14 帧，锚点从旧位置飞到新位置、缩放到新大小（cubic-bezier(0.65, 0, 0.35, 1)），颜色、底色和圆角渐变成新样子；第 10–16 帧，底色揭开，下一拍在它周围出现。

| 项 | 内容 |
|---|---|
| 类别 | 转场 |
| 写法 | 写在下一个 beat 上：`"tr": "anchor_match"`，可选 `"tr_anchor": "value"`（一个 `data-anchor` 名字，或一个 CSS 选择器如 `".wr-v"`） |
| 适合 | 同一个数字 / 词换一种讲法：大数字揭晓 → 拆解卡片 |
| 时长 | 16 帧（30 fps 约 0.53 秒） |
| 横屏 / 竖屏 | ✓ / ✓ |
| 跟风格换皮 | 锚点的颜色、底色、圆角都从两拍真实的样子取；底色取下一拍的页面底色 |
| 什么时候用 | 两拍里有同一个数或同一个词 |
| 什么时候不用 | 两拍没有共同元素（会退回成一次普通的底色上推） |

**锚点怎么找**：

1. 写了 `tr_anchor`：在上一拍找这个 `data-anchor` 名字（或选择器），再在下一拍找同名的元素。
2. 没写：上一拍里带 `data-anchor` 属性的元素，下一拍里同名的元素。`glyph_sphere` 的实心数字、`wire_resolve` 重点卡片的数值都带 `data-anchor="value"`。
3. 都没有：各取场景里字号最大的那段文字。

锚点按布局位置测量（不受入场动画的位移影响），以复制品的形式飞过去；下一拍真正的锚点等它完全显示出来再接手（最多再等 0.8 秒）。

```json
{"scene": "fx", "fx": "wire_resolve", "tr": "anchor_match", "items": ["…"], "…": "…"}
```

**实现**：`scripts/h9/fx/fx3_transitions.py`，由 `scripts/h9/fx.py` 的 `transition()` 调用。
