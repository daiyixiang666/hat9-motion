# `side_stat` · 数字贴在主体旁

<img src="../../assets/previews/fx/side_stat.webp" width="480" alt="side_stat 横屏"> <img src="../../assets/previews/fx/side_stat_v.webp" width="160" alt="side_stat 竖屏">

**怎么动**：一个大数字 + 单位 + 小字说明钉在主体旁边，数字会跳（从上一个数接着数），可以再掉下一个红色小标签（「还在涨」）。一拍里几个数字可以在同一个位置轮换，各自对 `@词`；`side: "both"` 时左右交替。

| 项 | 内容 |
|---|---|
| 类别 | 重点信息（贴在主体旁） |
| 适合的句子 | 「已经收录了一百七十四个动效」「7 天发了 15 个版本」——一个数字配一个人或画面 |
| 建议时长 | 每个数字 ≥ 1 秒，2 个数 4 秒左右 |
| 参数 | `values`（1–6 个：`v` `unit` `cap` `kicker` `tag` `at` `side`；也可以只写字符串）或单个的 `value` `unit` `cap` `kicker` `tag`、`count`、`side`（left / right / both）、`subject` / `video` / `image` |
| 横屏 / 竖屏 | ✓ / ✓（竖屏：数字在上、主体卡占下半屏；both：一个在卡上方、一个在卡下方） |
| 跟风格换皮 | 字体、强调色、圆角、描边、阴影、重点词的标法（色块 / 下划线 / 马克笔 / 墨晕）都从风格来（`scripts/h9/fx/_kinfo.py` 的 `SKINS`） |
| 章节底色 | beat 没写 `theme` 时，颜色跟着这一章的 `chapter.bg` 颜色世界走（`scripts/h9/device.py`），深色、浅色、强调色章节都可读；在主持人区域里（`presenter.py`）按区域大小排版 |
| 参考 | 抖音开源竖屏模板宣传片（douyin 7701488753897917723）的同类版式 |

没有主体时：数字占左边，右边每个数字长出一根柱子，当前的那根用强调色。

```json
{
 "scene": "fx",
 "fx": "side_stat",
 "d": 4.2,
 "theme": "paper",
 "topic": "开源模板",
 "subject": "../../assets/host.webm",
 "subject_tag": "ON AIR · 柴柴",
 "values": [
  {
   "v": "162",
   "unit": "个",
   "cap": "效果 · 已收录"
  },
  {
   "v": "174",
   "unit": "个",
   "cap": "动效 · 含 12 种转场"
  }
 ],
 "line": "已经收录了*一百七十四个*动效。"
}
```
