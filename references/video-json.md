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
| `music_beats` | beats.json 路径 | 配乐的实测节拍 `{"tempo", "beats": [秒…]}`；不写时自动找配乐旁边的 `<歌名>.beats.json`（素材库 `music/<情绪>/` 里都有） |
| `beat_snap` | 默认开；`false` 关掉；或容差秒数（默认 0.12） | 有节拍时，换画面、转场、`sfx` 音效和它的画面冲击自动挪到最近的拍上。写 `"@词"` 的时间以口播为准：最多晚 0.12 秒、最多早 2 帧，挪不动就不挪。单个 beat 或音效写 `"snap": false` 不动。挪了什么记在构建目录的 `timeline.json` |
| beat `music` | `"up"` 或分贝数 | 这一段配乐推上来（默认 +8 dB，`meta.music_up` 可改），用在无人声段；快切 beat 默认就推，写 `false` 不推 |
| `elastic` | 默认开启；`false` 关掉 | 拍短时入场按比例加快，拍长时落定后镜头继续推进；单个 beat 写 `"hold": "static"` 关掉 |
| `speakers` | `{"A": {"name": "主持人", "color": "#f6ce3a", "side": "left"}}` | 多人对话：words.json 里每个词带 `spk`，字幕按说话人分色、分左右、带名牌 |
| `caption_mode` | `"reading"` / `"punch"` / `"karaoke"` | 卡拉 OK：整句先暗着，说到哪个字亮哪个字 |
| `caption_tr` | 每句一行 | 第二语言字幕（按 。！？ 切句对齐） |

### 片中快切（无人声段，卡拍）

```json
"meta": {"music": "$H9_MEDIA/music/tech/Digital_Lemonade.mp3", "duck": true,
         "gaps": [{"after": "@走得越多$", "dur": 2.6}]},
"beats": [ …,
  {"scene": "fx", "fx": "montage", "t": "@走得越多$", "per": 1, "clips": [
    {"src": "clips/factory.mp4", "in": "auto", "label": "工厂", "line": "原料走得越多"},
    {"src": "clips/harbor.mp4",  "in": "auto", "label": "海运", "line": "原料走得越多"}]},
  {"scene": "thesis", "t": "@看懂谁", …} ]
```

- 快切从下一拍开始（最多等一拍），每 `per` 拍一刀（`0.5` = 半拍），每段自动挑最好看的一截（`"in"` 写秒数则照用），每刀开头轻推一下；`label` 是顶部黄底标签（≤ 8 字，可省）。
- 每段必须写 `line`：它对应哪句话。和口播无关的画面不进快切。
- 配合 `gaps` 在那句话后面空出几拍；不写 `d` 且下一个 beat 没写 `t` 时，这段刚好按段数的拍子长。
- 例子：`examples/beatsync/`。

工具：`scripts/align.py`（录音 + 稿子 → words.json）、`scripts/cover.py`（16:9 / 4:3 / 3:4 封面）、`scripts/url_brief.py`（网址 → 长截图 + 引用 beat）、`scripts/h9/data.py`（数据效果直接读 CSV / Excel）。

## 交付开关（写在 `meta` 里，0.7）

| 开关 | 写法 | 作用 |
|---|---|---|
| `breath` | `true` | 旁白 0.25–1.4 秒的停顿里，画面轻轻「吸一口气」 |
| `rate_adapt` | `true` | 语速快（每秒 6 字以上）时入场整体加速，最多 1.6 倍；语速慢（每秒 3.5 字以下）时镜头推得更开，并加柔光层 |
| beat `sfx` | `[{"at": "@词", "name": "hit", "vol": 0.5, "hit": "flash"}]` | 音效和画面冲击在同一帧；`hit` 可选 flash / dark / shake / punch |
| beat `mood` + `music_moods` | `"mood": "heavy"`；`{"heavy": "重.mp3"}` | 沉重段落换深色调和配乐，后面的 beat 沿用 |
| `aspect` | `1:1` / `4:5` / `3:4` | 按 9:16 排版后缩放裁切；`canvas: false` 关掉 |
| `ai_label` | `true` / `"AI 生成"` / `{"text", "pos"}` | 画面角落常驻「AI 生成」标识 |
| `caption_preset` | `douyin` / `shipinhao` / `xiaohongshu` / `bilibili` / `youtube` | 套用对应平台的字幕样式 |
| `brand` | brand.json 路径或对象 | 颜色、字体、圆角、logo 套到任何风格（用 `design_md.py --brand-json` 生成） |
| `series` | `{"name", "ep", "opener": true}` | 加 1.8 秒系列片头，封面眉题自动带期数 |
| `lang` / `--lang` | `"ja"` | 多语言字段 `{"zh", "en", "ja", …}` 里选一种；日文、韩文、繁体、阿拉伯文、希伯来文自动换字体 |
| `offline` | `true` | 地图只用仓库自带的 d3-geo 和 topojson，缺文件就报错 |
| 文字标记 | `CO_{2}`、`mc^{2}` | 下标、上标 |

工具：`scripts/cut_list.py`（长口播挑段精剪）、`scripts/ref_pacing.py`（量参考片的剪辑节奏）、`scripts/export_edit.py`（FCPXML + 分轨音频 + SRT，可导入剪辑软件）、`scripts/longform.py`（长片按章节分段渲染再拼接）、`scripts/share_card.py`（导出单张金句图）、`scripts/audio_tools.py`（降噪、拼接录音、剪口误）。
