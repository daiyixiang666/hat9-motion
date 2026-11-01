# video.json 格式

```json
{
  "meta": {
    "title": "凭什么是你",
    "style": "editorial",            // 风格 id，见 styles.md；命令行 --style 可覆盖
    "aspect": "16:9",                // 16:9（默认）| 9:16 | 1:1 | 4:3 | 3:4
    "voice": "assets/audio/voice.mp3",
    "words": "assets/audio/words.json",   // 逐字/逐词时间戳 [{w,s,e}]；有它才能写 "@关键词"
    "mascot": "assets/video/shiba.webm",  // 透明底的会说话柴犬（avatar/render.py 生成后转 webm）
    "music": "assets/audio/bgm.mp3", "music_volume": 0.12,   // 可选
    "caption_mode": "reading",       // reading（横屏默认）| punch（竖屏默认）
    "caption_hl": ["判断", "不能要"],  // 字幕里允许高亮的词（每页最多 1 个，全片 ≤15%）
    "caption_fix": {"错字": "正字"},   // ASR 纠错
    "tail": 0.8                      // 口播结束后多留几秒
  },
  "beats": [ { "scene": "title", "t": 0, ... }, ... ]
}
```

## 时间

- `t`：这个画面开始的时间。数字 = 秒；`"@差别"` = 口播说出「差别」的那一刻；`"@海报$"` = 说完「海报」；`"@海报+0.3"` = 再晚 0.3 秒。
- `d`：可省，默认到下一个 beat 开始。
- 场景内部的动作点（`at`、`at_left`、`at_hl`……）同样可以写 `"@词"`。写成 `@` 的入场会**提前 2 帧并按缓动的 90% 点对准这个词**，看起来正好落在字上。
- 关键词要在 words.json 里真的存在（ASR 错字先在 `caption_fix` 外另行核对）。

## 每个 beat 都可以带

| 字段 | 作用 |
|---|---|
| `host: true` | cameo 模式的风格里，柴犬在这一句出场（说观点、提问、恍然）。建议每 20–40 秒一次 |
| `chapter: true` | 这里换章节：用风格的招牌转场；否则是句间剪辑（多为硬切） |
| `tr: "flash"` | 强制指定这一刀的转场 / 剪辑 |
| `marks: [...]` | 指哪说哪：在画面元素上画圈、下划线、箭头、方框、删除线、荧光笔，见下 |

```json
"marks": [{"on": ".A", "verb": "circle", "at": "@杂志$", "label": "光 · 留白", "side": "top"}]
```
`on` 是场景里的选择器（compare 的左右图是 `.A` / `.B`；标题 `.ttl`；数字 `.val`）。`verb` = circle | underline | box | strike | arrow | highlight | indicate。

## 场景（scenes/）

| scene | 用在哪句 | 主要参数 |
|---|---|---|
| `title` | 开场钩子、章节名 | `title`（`*强调*`、`\|` 换行）、`kicker`、`sub`、`image` |
| `statement` | 一句观点 | `lines: [...]`、`at: [...]`（每行出现时间）、`image`、`label`；行首 `~` = 弱化 |
| `compare` | A / B 对比 | `left/right: {img, label, note, stickers}`、`chip`、`verdict: left\|right`、`at_left/at_right/at_stickers/at_verdict` |
| `number` | 一个数字 | `value`、`unit`、`label`、`sub`、`viz: dots\|bar\|split\|none`、`hl`、`split_labels`、`at`、`at_hl` |
| `quote` | 金句 / 结论 | `text`、`by`、`image`、`at_em` |
| `outro` | 收尾 | `title`、`sub`、`cta` |

字很长时：**拆成两个 beat 或换场景，不要缩字号。** 动效标题每屏 4–12 个汉字。


## 节奏与字幕开关（写在 `meta` 里）

| 开关 | 写法 | 作用 |
|---|---|---|
| `lead` | 秒数 | 配音和所有 `"@关键词"` 整体后移，前面空出来给无声开场（配合 `cold_open`） |
| `gaps` | `[{"after": "@词$", "dur": 1.5}]` | 在那个词之后插入静音，后面的词和关键词一起后移（配合 `breather` / `interlude`） |
| `duck` | `true` 或分贝数（默认 10） | 说话时背景音乐自动压低，停顿里恢复 |
| `elastic` | 默认开启；`false` 关掉 | 拍短时入场按比例加快，拍长时落定后镜头继续推进；单个 beat 写 `"hold": "static"` 关掉 |
| `speakers` | `{"A": {"name": "主持人", "color": "#f6ce3a", "side": "left"}}` | 多人对话：words.json 里每个词带 `spk`，字幕按说话人分色、分左右、带名牌 |
| `caption_mode` | `"reading"` / `"punch"` / `"karaoke"` | 卡拉 OK：整句先暗着，说到哪个字亮哪个字 |
| `caption_tr` | 每句一行 | 第二语言字幕（按 。！？ 切句对齐） |

工具：`scripts/align.py`（录音 + 稿子 → words.json）、`scripts/cover.py`（16:9 / 4:3 / 3:4 封面）、`scripts/url_brief.py`（网址 → 长截图 + 引用 beat）、`scripts/h9/data.py`（数据效果直接读 CSV / Excel）。
