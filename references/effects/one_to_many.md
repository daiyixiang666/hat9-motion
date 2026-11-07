# `one_to_many` · 一个变一群 · One to Many

<img src="../../assets/previews/fx/one_to_many.webp" width="480" alt="one_to_many 横屏"> <img src="../../assets/previews/fx/one_to_many_v.webp" width="160" alt="one_to_many 竖屏">

**怎么动**：一张主体卡独自居中，旁边一个大大的「1」；然后它缩进网格正中的 2×2 位置，几十个小格（终端、卡片、头像或真实图片）从它向外一圈圈弹出，「1」飞到它的角上数到总数，标题落在网格上，小格一直在干活（进度条在走、对勾落下）。

**什么时候用**：「一个人 + 一群 Agent」「一份内容分发到 40 个平台」「1 个模板生出 1000 条视频」这类一对多。

| 项 | 内容 |
|---|---|
| 类别 | 数字变形状 |
| 建议时长 | 5–6 秒 |
| 横屏 / 竖屏 | ✓ / ✓ |

**参数**

| 参数 | 说明 |
|---|---|
| `subject` | 主体（图片 / 视频）；没有时用 one 文字卡 |
| `one` | 没有主体时卡上的字，默认「你」 |
| `subject_label` | 主体名字条 |
| `count` | 小格数量，6–200 |
| `kind` | terminal | card | avatar | image |
| `items / folder` | kind image 用的图 |
| `names` | 小格标题 |
| `lines` | terminal / card 小格的文字池 |
| `one_unit` | 「1」后面的单位，如「人」 |
| `unit` | 总数后面的单位 |
| `title` | 落在网格上的标题，支持 *强调* |
| `mock` | 示意标签 |

```json
{
 "scene": "fx",
 "fx": "one_to_many",
 "subject": "../mixue/assets/video/shiba.webm",
 "subject_label": "柴柴",
 "count": 47,
 "one_unit": "人",
 "unit": "个",
 "title": "背后是*一群 Agent*",
 "kind": "terminal",
 "line": "屏幕前是我一个人，背后是 *一群 Agent*。",
 "t": "@关键词"
}
```

所有这一组效果（数字变形状）：颜色、字体、圆角、描边、阴影、入场缓动都取自当前风格（18 种风格自动换皮）；横竖屏同一套参数；可选 `subject`（图片或视频）把主讲人放在旁边的小卡里。

**已知坑**：总数显示为 count + 1（包含主体自己）。终端小格里的字是质感，不要放需要读的信息。
