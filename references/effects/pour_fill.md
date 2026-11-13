# `pour_fill` · 倒入液面

<img src="../../assets/previews/fx/pour_fill.webp" width="480" alt="pour_fill 横屏"> <img src="../../assets/previews/fx/pour_fill_v.webp" width="160" alt="pour_fill 竖屏">

**怎么动**：一股液体倒进容器轮廓，液面涨到百分比；倒完液面晃动再静止（`material: "grains"` 时是颗粒堆起再塌平）。`from` 画一条虚线标出起点；超过 100% 会从杯口溢出、顺外壁流下、在地上积一滩。数字骑在液面上一起涨。

| 项 | 内容 |
|---|---|
| 类别 | 物理 |
| 适合的句子 | 渗透率、完成率、占比从 A 涨到 B，「已经超了」 |
| 建议时长 | 4–5 秒 |
| 参数 | `value`（必填，0–400）、`from`、`unit`（默认 %）、`material`（liquid / grains）、`caption`（数字下面一行）、`at`（开始倒的时刻）、`title`、`note` |
| 横屏 / 竖屏 | ✓ / ✓（竖屏：容器 760 宽从标题下一直到底边；横屏：容器居左，数字在右） |
| 跟风格换皮 | 颜色只用风格的 token（--bg --fg --muted --accent --card --card-fg），字体用风格的 display / body / num；没写 `theme` 时画在风格自己的底色上 |
| 什么时候用 | 一个比例在变化，或「装满 / 装不下」的感觉 |
| 什么时候不用 | 比较多个对象的占比（用 bars / donut）；比率远超 400%（用 `zoom_scale`） |
| 同步口播 | 有字级时间戳（meta.words）时，条目 / 关键时刻落在说到它的那一刻；`at` 可以写 `"@词"` 或拍内秒数 |
| 缺内容 | 必填参数缺了会直接报错（不会画空骨架）；确实要骨架时写 `"skeleton": true` |

```json
{
 "scene": "fx",
 "fx": "pour_fill",
 "topic": "新能源车",
 "title": "新能源车渗透率",
 "value": 40.9,
 "from": 5.4,
 "caption": "2020 年 5.4% → 2024 年",
 "line": "四年时间，新能源车的渗透率从 5.4% 涨到了 *40.9%*。",
 "src": "中国汽车工业协会；工信部《中国汽车产业发展年报 2021》",
 "t": "@关键词"
}
```

**已知坑**：数字在 9:16 会被夹在字幕带上方，液面太低时数字不会沉到字幕后面。
