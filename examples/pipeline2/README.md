# 流水线与交付 · 第二版演示

旁白还是 `examples/mixue` 那段。这里演示这一版新加的开关和几个独立脚本。

| 文件 | 演示什么 |
|---|---|
| `delivery.json` | 交付相关。系列片头（`series`，「商业拆解 · 第 12 期」）、AI 生成角标（`ai_label`）、品牌包（`brand: "brand.json"`，换色、换字体、加 logo）、小红书字幕预设 |
| `rhythm.json` | 节奏相关。停顿里的「呼吸」微动（`breath`）、按语速自适应（`rate_adapt`）、抖音字幕预设，以及声画同拍：beat 里的 `sfx` 带 `hit`。还有轻重情绪：beat 写 `mood`，重段换深色调，并换 `music_moods` 里的配乐 |
| `text_lang.json` | 无旁白短片。上标、下标（`CO_{2}`、`E = mc^{2}`），繁体字和 emoji，标题和每页文字同时写中、英、日三种，用 `--lang` 选一种出片 |
| `brand.json` | `design_md.py --brand-json` 从 `examples/brand/DESIGN.md` 导出的品牌包，任何风格都能用 |
| `make_talk.py` | 把 5 个示例的旁白拼成一段 2 分半的长口播，给下面的剪辑脚本当输入 |
| `cut/` | `cut_list.py` 从长口播里挑出约 40 秒，生成剪辑单、剪好的 voice.wav、重排时间的 words.json 和一份可直接出片的 video.json |
| `ref_doc.pacing.json` / `ref_reel.pacing.json` | `ref_pacing.py` 量出来的参考片节奏：每分钟切几次，镜头时长的中位数和四分位，每 10 秒切几次 |

## 新开关（写在 video.json 的 meta 里，不写就和以前完全一样）

**节奏**
- `breath: true`：旁白里 0.25–1.4 秒的停顿，画面跟着轻轻吸一口气（放大约 1%，上浮 3 px），说话一开始就回位。
- `rate_adapt: true`：语速快（每秒超过 6 个字）时，这一拍的入场整体加速，最多 1.6 倍；语速慢（每秒不到 3.5 个字）时，镜头推得更开，还会加一层缓慢移动的柔光氛围。
- beat 里写 `"sfx": [{"at": "@关键词", "name": "hit", "vol": 0.5, "hit": "flash"}]`，音效和画面在同一帧落下。`name` 可以是风格里的音效角色，也可以是 `assets/sfx` 里的文件名。`hit` 有四种：`flash` 白闪，`dark` 压黑，`shake` 震动，`punch` 推一下。
- beat 里写 `"mood": "heavy"` 或 `"light"`，之后的 beat 沿用同一情绪，直到再次改写。重段换成深色调。`meta.music_moods: {"heavy": "重.mp3"}` 给重段换配乐，两段之间交叉淡化 0.4 秒；开了 `duck` 时每段都会压低。

**交付**
- `aspect` 新增 `1:1`、`4:5`、`3:4`。画面仍按 9:16 排版，再整体缩放、裁切到目标尺寸，所有效果都能直接用（1:1 缩到 0.8 倍，左右各留 108 px 底色边）。想按目标尺寸单独排版就写 `meta.canvas: false`。
- `ai_label: true`，或写成 `{"text": "AI 生成", "pos": "br"}`：画面角落常驻一个「AI 生成」小标。竖屏默认右下，横屏默认右上，不压字幕和平台按钮。
- `caption_preset`：`douyin`、`shipinhao`、`xiaohongshu`、`bilibili`、`youtube`，分别对应各平台常见的字幕字号、描边、位置和强调色。抖音和视频号的大字居中字幕只用在竖屏，横屏自动改成底部字幕。
- `brand`：brand.json 的路径，也可以直接写成对象：`{colors, fonts, tokens, logo, logo_pos}`。它会把颜色、字体和圆角套到任何风格上，`logo` 会放在角落：横屏默认右上，竖屏默认左下（字幕和来源行之间的空档）。`logo_pos` 可以写 `"tr"`，也可以按画幅分别写，例如 `{"9:16": "bl", "16:9": "tr"}`。logo 下面默认垫一块浅色底板，深色页面上也看得清；不要底板就写 `logo_plate: false`。
- `series: {"name": "商业拆解", "ep": 12, "opener": true}`：开头加 1.8 秒的系列卡（系列名、第几期、标题），旁白自动后移。`scripts/cover.py` 的封面眉题也会自动写成「商业拆解 · 第 12 期」。
- `offline: true`：地图类效果只用仓库里自带的 d3-geo 和 topojson-client（ISC 许可）。缺文件就报错，不会去连 CDN。GSAP 始终从 jsdelivr 加载，不随仓库分发。

**文字**
- `^{...}` 是上标，`_{...}` 是下标，`*`、`|` 等原有标记照常可用。
- 任何文字字段都可以写成 `{"zh": "…", "en": "…", "ja": "…"}`。用 `build.py --lang ja` 或 `meta.lang` 选语言，缺的语言先退回 zh，再退回第一个值。日文、韩文、繁体、阿拉伯文、希伯来文会自动换上对应的 Noto 字体（`noto-sans-jp`、`-kr`、`-tc`、`-arabic`、`-hebrew`，都是可选字体，没装就用系统字体）。阿拉伯文和希伯来文按从右往左排，标点落在正确的一侧，但版式不镜像。逐字入场的效果遇到这两种文字时改成整段入场，字母连写和顺序不会被拆乱。

## 脚本

```bash
python3 scripts/build.py examples/pipeline2/text_lang.json --lang ja --aspect 16:9            # 选一种语言出片
python3 scripts/build.py examples/pipeline2/delivery.json --aspect 3:4                        # 1:1 / 4:5 / 3:4
python3 scripts/cut_list.py 长口播_words.json --audio 长口播.wav --target 40 --keep "净利润,加盟" --out cut/
python3 scripts/ref_pacing.py 参考片.mp4 --video my/video.json --apply                       # 量参考片节奏，标出偏长的 beat，写 video.paced.json
python3 scripts/export_edit.py build/xxx --render renders/xxx.mp4 --out handoff/             # 交给剪辑软件
python3 scripts/longform.py long/video.json --chapter-len 120 --jobs 2 --out long/           # 长片：分章并行渲染再无损拼接
python3 scripts/design_md.py examples/brand/DESIGN.md --name qingzhou --brand-json brand.json
```

- **cut_list.py**：给每句话打分。带数字、转折词、问句的句子加分，长度适中的也加分；太长的、以口头禅开头的减分，`--keep` 里的词大幅加分。在目标时长内挑分数最高的句子，开头和结尾各保留一句最强的，句子之间留 `--gap` 秒的气口。
- **ref_pacing.py**：用场景检测量出参考片的切点。加上 `--video` 时，会标出比参考片 75 分位还长的 beat；再加 `--apply`，把建议的切点写进 `video.paced.json`。
- **export_edit.py** 导出这些文件：
  - `film_silent.mp4`：无声画面，直接从成片复制视频流。
  - `voice.wav`、`music.wav`、`sfx.wav`：人声、音乐、音效三条整长分轨，可以在剪辑软件里重新混音。
  - `captions.srt`：字幕。
  - `timeline.fcpxml`：FCPXML 1.9，Final Cut Pro 和 DaVinci Resolve 的导入格式。画面在主轨，三条分轨分别带 dialogue / music / effects 角色，字幕是 Basic Title。
  - 剪映草稿是私有的加密格式，不支持导出。剪映和 Premiere 用户请导入无声画面、三条分轨和 SRT。
- **longform.py**：按 beat 上的 `"chapter": true` 或 `--chapter-len` 分章，切好每章的人声、音乐和逐字时间。各章并行构建、渲染，最后用 concat 无损拼接。暂不支持 `meta.gaps`；`lead` 只作用于第一章。
