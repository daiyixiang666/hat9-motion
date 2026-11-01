# `scale_compare` · 

<img src="../../assets/previews/fx/scale_compare.webp" width="480" alt="scale_compare 横屏"> <img src="../../assets/previews/fx/scale_compare_v.webp" width="160" alt="scale_compare 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 「相当于 N 个…」「绕赤道 N 圈」 |
| 建议时长 | 4–5 秒 |
| 参数 | `a_label`, `b_label`, `basis`, `dec`, `head`, `icon`, `method`, `mode`, `ratio`, `ratio_label`, `ref_value`, `unit_name`, `value` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Envato Popular Infographic · Mapal VOX 式信息图 34.6万播放 |

```json
{
 "scene": "fx",
 "fx": "scale_compare",
 "theme": "lemon",
 "topic": "商业拆解",
 "mode": "laps",
 "ratio": 7.835,
 "dec": 1,
 "head": "上海港一年|5150 万个标准箱，首尾相连",
 "ratio_label": "圈",
 "method": "按 20 英尺箱长 6.096 米、赤道周长 40,075 公里计算",
 "line": "上海港一年的集装箱首尾相连，能绕赤道 *7.8 圈*。",
 "src": "上港集团 2024 年业务快报",
 "basis": "绕地球赤道",
 "t": "@关键词"
}
```

**已知坑**：ratio 自己算好写进去，method 写明换算口径。
