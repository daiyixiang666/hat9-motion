# `bar_race` · 

<img src="../../assets/previews/fx/bar_race.webp" width="480" alt="bar_race 横屏"> <img src="../../assets/previews/fx/bar_race_v.webp" width="160" alt="bar_race 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 数据 |
| 适合的句子 | 排名随时间变化、超车 |
| 建议时长 | 每个时间点 1.5–3 秒 |
| 参数 | `compact`, `csv`, `dec`, `hl`, `note`, `title`, `top`, `transpose`, `unit` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Data Is Beautiful 编程语言排行赛跑 上线一个半月 265万播放 |

```json
{
 "scene": "fx",
 "fx": "bar_race",
 "theme": "ink",
 "topic": "商业拆解",
 "csv": "assets/stores.csv",
 "x": "时间",
 "hl": "蜜雪冰城",
 "title": "全球门店数",
 "note": "星巴克为财年末（9 月底）",
 "line": "一年时间，蜜雪冰城从第三冲到了*第一*。",
 "src": "McDonald's、Starbucks 10-K；蜜雪集团 2024 年度业绩公告",
 "t": "@关键词"
}
```

**已知坑**：不同公司的财年口径要在 note 里写明。
