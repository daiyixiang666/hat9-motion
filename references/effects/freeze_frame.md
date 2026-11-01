# `freeze_frame` · 

<img src="../../assets/previews/fx/freeze_frame.webp" width="480" alt="freeze_frame 横屏"> <img src="../../assets/previews/fx/freeze_frame_v.webp" width="160" alt="freeze_frame 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 音视频 |
| 适合的句子 | 「停一下，看这里」、关键瞬间标注 |
| 建议时长 | 5–7 秒（定格 2.4–3.4 秒） |
| 参数 | `hold`, `image`, `mode`, `pin`, `pins`, `resume`, `stamp`, `start`, `video` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | B站科普常用：关键瞬间定格 |

```json
{
 "scene": "fx",
 "fx": "freeze_frame",
 "theme": "ink",
 "topic": "商业拆解",
 "video": "../cite/assets/working_dollars_1957.mp4",
 "start": 0.4,
 "at": 1.6,
 "hold": 2.8,
 "pins": [
  {
   "box": [
    11,
    3,
    16,
    50
   ],
   "label": "SALES",
   "sub": "销售额"
  }
 ],
 "line": "定格这一帧：1957 年的理财动画里，账本上写着 *SALES*。",
 "src": "Working Dollars (1957) · Prelinger Archives（公有领域）",
 "t": "@关键词"
}
```

**已知坑**：box 是原片画面的百分比；先截一帧看准再写，别猜。
