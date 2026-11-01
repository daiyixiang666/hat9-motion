# 节奏与交付流水线 · 演示

同一段旁白（来自 `examples/mixue`），演示这一版新增的几个开关。

| 文件 | 演示什么 |
|---|---|
| `dialogue.json` | 双人对话字幕：词带 `spk`，`meta.speakers` 给名字、颜色、左右位置；`meta.caption_tr` 给第二行英文（演示用：同一段旁白按句标成两个人） |
| `karaoke.json` | 卡拉 OK 字幕：`caption_mode: "karaoke"`，整句先暗着，说到哪个字亮哪个字 |
| `cold_open.json` | `meta.lead: 3` 先放 3 秒无声开场再开口；`meta.gaps` 在「四十四亿多」后插入 1.6 秒停顿（留白页撑住）；`meta.duck: 10` 说话时音乐自动压低 10 dB |
| `elastic.json` | 弹性时长：同一批效果放在 0.8 秒和 6 秒的拍里。短拍整段入场按比例加快，长拍落定后镜头继续缓慢推进 |
| `covers/` | `scripts/cover.py` 生成的 16:9、4:3、3:4 封面（标题自动定字号，不出界） |
| `fixtures/` | `scripts/align.py` 的测试夹具：模拟的 Whisper 式逐字时间（故意带两处同音错字）和原稿 |

## 新开关一览（写在 video.json 的 meta 里）

- `lead`: 秒数。配音和所有 `"@关键词"` 整体后移，前面空出来给无声开场。
- `gaps`: `[{"after": "@词$", "dur": 1.5}]`。在那个词之后的停顿里插入静音，后面所有词和关键词一起后移。
- `duck`: `true` 或分贝数（默认 10）。按逐字时间生成「说话时压低」的音乐副本。
- `elastic`: 默认开启；`false` 关掉整片的弹性时长。单个 beat 写 `"hold": "static"` 关掉。
- `speakers`: `{"A": {"name": "主持人", "color": "#f6ce3a", "side": "left"}}`，配合 words.json 里每个词的 `spk`。
- `caption_mode`: 新增 `"karaoke"`。
- `caption_tr`: 每句一行的第二语言字幕（按 。！？ 切句）。

## 工具

```bash
python3 scripts/align.py 录音.wav 稿子.txt --out assets/audio/words.json            # 自动选：转写文件 → faster-whisper → whisperx → 静音切分
python3 scripts/align.py 录音.wav 稿子.txt --backend silence --out words.json        # 不装模型也能用
python3 scripts/cover.py examples/mixue --at 2.5 --title "一杯 4 块钱的柠檬水|一年净赚 *44 亿*" --check
python3 scripts/stress.py --plugins          # 全量压力测试：含 9:16 安全区、0.8 秒 / 6 秒时长维度
```
