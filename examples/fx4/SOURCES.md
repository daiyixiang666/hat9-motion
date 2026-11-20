# fx4 示例 · 画面上每个事实的出处

《一份 video.json 怎么变成成片》讲的是这个仓库自己。画面上的数字、命令、文件名、检查项和时间都来自仓库本身或在仓库里实际跑出来的结果，下面写明怎么复现。时间是一台普通电脑上的一次实测，换机器会不同。

字幕时间：这条片没有配音，`python3 examples/fx4/make_timing.py` 按每秒 5.6 字排出 `assets/audio/words.json`。

| # | 拍 · 效果 | 画面上的事实 | 怎么复现 |
|---|---|---|---|
| 1 | 开场 · `tilt_board` | 188 个效果、17 种转场 | 效果：`scripts/h9/aefx.py` 的 `FX` 登记表去掉三个辅助项（`plate` `apply_style` `ctx_parts`）：`python3 -c "import sys; sys.path.insert(0, 'scripts'); from h9 import aefx; print(len(set(aefx.FX) - {'plate', 'apply_style', 'ctx_parts'}))"`；转场：`gallery/effects.json` 的 `transitions` 共 17 项。卡片是 `assets/previews/fx/` 里 39 个效果预览的一帧（`assets/fx/`） |
| 2 | 需求单 · `doc_edit` | `examples/fx4/video.json` 第 8 拍（`qc_sheet`）：`checks` 从效果默认的「黑屏、闪帧、文字重叠」改成 `review` 真实的检查名 | 本文件夹 `video.json` 第 8 拍；默认值见 `references/effects/qc_sheet.md` |
| 3 | 需求单 · `time_budget` | `examples/reel` 全片 38.4 秒，纯文字画面 9.6 秒（`title` 和 `statement` 两拍，各 4.8 秒），`text-share 25%` | `python3 scripts/hat9.py brief check examples/reel/video.json --aspect 9:16` 输出 `P1 text-share 25% 的时长是纯文字画面`；落下的 6 张是其余 6 拍的静帧（`assets/stills/reel_b*_9x16.jpg`） |
| 4 | 静帧板 · `pair_check` | 左：`examples/reel` 第 1 拍（`title`，纯文字）；右：第 7 拍（`rank`）。圈出的四处：标题只占左栏、横条按真实长度、每条标数值、底行写算式 | `python3 scripts/hat9.py stills examples/reel/video.json --aspect 16:9 --settled` 的 `frames_settled/frame-00` 和 `frame-06`（`assets/stills/reel_title_16x9.jpg` `reel_rank_16x9.jpg`） |
| 5 | 小样 · `wave_align` | 字幕段是本片前几句字幕；「每秒 5.6 字」是 `make_timing.py` 的 `RATE`；波形是示意，不是录音 | `examples/fx4/make_timing.py` |
| 6 | 整片 · `run_clock` | `examples/mixue` 一次实测：00:06:31 开始 `brief check`，00:06:40 结束；`stills --settled` 到 00:06:51；`sample --range 0,4` 到 00:07:06；`render --aspect 9:16` 到 00:08:09；`render --aspect 16:9` 到 00:08:59；`review` 到 00:09:16。共 2 分 45 秒。时钟只显示「时:分」，节点取每一段结束时钟面上的分钟 | 依次运行 `hat9.py brief check` → `stills` → `sample` → `render`（两种画幅）→ `review`，记下每条命令结束的钟点；缩略图是这次运行的小样一帧、横屏成片一帧和 `review` 的检查图（`assets/run/`） |
| 7 | 快切 · `card_wall`（不给素材：一墙空着的占位卡） | `montage` 是给实拍素材做卡拍快切的；这条片没有实拍，所以不用，墙上的位置都是空的 | `references/director.md` 关卡表「打磨」一行；`scripts/montage.py` |
| 8 | 自检 · `qc_sheet` | 检查项「画面不冻住」「字号够大」「字和底对比够」是 `render` 自动检查的原名；`examples/reel` 竖屏这一次「字号够大」没过（2 处 22 px 的来源行），所以这一项打叉 | `python3 scripts/hat9.py render examples/reel/video.json --aspect 9:16 --preview` 的「自动检查」；24 帧取自这次渲染（`assets/qc/`，每 1.6 秒一帧） |
| 9 | 结尾 · `card_wall` | 26 种风格，各一条示例片 | `references/styles.md` 和 README 列出的 26 种内置风格（`styles/` 里另有一个派生出来的品牌示例风格，不算在内）；墙上是 `assets/previews/` 里 26 条示例片横竖屏各一张封面 |

导航六关的名字和顺序取自 `references/director.md` 的关卡表和 `hat9.py` 的命令说明：需求单 `brief` → 静帧板 `stills` → 小样 `sample` → 整片 `render` → 快切 `montage` → 自检 `review`。左上角钉着的是每一关对应的命令名。
