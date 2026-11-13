---
name: hat9-motion
description: 九帽动效 hat9-motion — 把口播视频（真人出镜）、录音或文案做成 AE 级动效视频；先定谁来口播，人一直在画面里，动效围着人换位置（横屏 16:9 / 竖屏 9:16）。内置 26 种风格（财经刊、极简讲述、瑞士海报、剪纸、手绘白板、水墨、像素、拼贴杂志、等距微缩、镀铬三维……）和 197 个按 VideoHive 销量、YouTube 与 B 站播放量复刻的 AE 动效与转场（2.5D 照片视差、重拍排版 Stomp、瞳孔穿梭、文字匹配剪辑、照片墙、数字滚动、掉落堆叠、倒入液面、推轨穿层、焦点转移、引用、图表、地图……），自动分镜、对准口播逐字时间、字幕、主持人形象，HyperFrames 逐帧确定渲染，零 API key 可出片。Use when the user wants an explainer / talking-head / 口播 / 解说 / 知识类短视频、动效、motion graphics、kinetic typography、AE 特效、片头、字幕包装、竖屏抖音视频, or asks to "turn this script into a video".
license: MIT
compatibility: Python 3.9+, Node.js 22+, FFmpeg; Chrome is fetched by HyperFrames on first render. Works in Claude Code, Codex, Cursor, WorkBuddy and any agent that can run shell commands; chat-only assistants use dist/hat9-motion.skill.md.
metadata:
  version: "0.18.0"
  author: daiyixiang666
---

# 九帽动效 hat9-motion

`SKILL_DIR` = 本文件所在目录。命令都用 `python3 $SKILL_DIR/scripts/hat9.py …`（Windows：`python`）。

## 先分流：用户要什么？

| 用户说 | 走哪条路 |
|---|---|
| 「帮我剪这条口播 / 我拍了一段口播」（真人出镜视频） | **A. 整片**，走口播视频路线（第 1 步第 1 种） |
| 「把这段文案 / 录音做成视频」 | **A. 整片**（先问谁来口播） |
| 「用 xx 效果做一个片头 / 这一句加个 xx」 | **B. 单个效果**：读 `gallery/llms.txt` 选 id，再读 `references/effects/<id>.md` |
| 「改一下第 3 句 / 换个转场 / 字太小」 | **C. 改已有片**：只改 `video.json` 对应 beat，重新 render |
| 「只要封面 / 静帧」 | `scripts/cover.py` 出 16:9 / 4:3 / 3:4 封面，或 `snapshot --at` 抽帧 |
| 「我有 PDF / 论文 / 新闻 / 截图 / 录屏 / 表格 / 一堆图 / 一个网址」 | 先查 `references/inputs.md` 找对应效果（`cite_*`、`media`、`scroll_shot`、`screencast`、`table` …）；网址用 `scripts/url_brief.py`；**讲产品 / 工具时用 `scripts/ui_capture.py 网址 --auto --aspect 9:16`** 抓真实界面组件（配 `ui_lift` 出框效果），不编界面；表格用 `csv` 参数 |
| 「只有录音没有逐字时间」 | `scripts/align.py 录音 稿子 --out words.json` |
| 「看着像 AI 模板 / 不高级」 | 先读 `references/craft.md`，再跑 `python3 scripts/craft_lint.py <构建目录>` 查默认手法 |
| 「片子不够厉害 / 太平 / 像 PPT」 | 读 `references/director.md`，从关卡 1 重走：`brief check` 查分镜 → `stills` 看静帧板 → `review` + `--gate` 打分 |
| 「学这几条参考片的感觉」 | `hat9.py refs 参考*.mp4 --out work/refs` → 写 `principles.md` → `style new` 派生 → 先做一个场景对比参考板 |
| 环境报错 | `hat9.py doctor`，按提示补齐 |

## A. 整片（默认流程）

按关卡走，**不许跳关**；哪一关不过就回到那一关改，不在成片上修修补补（`references/director.md`）。

1. **先定口播：谁来说、用什么素材。**这是剪口播，没有口播主体就不往下做分镜。已给的不再问，按下面顺序要：
   1. **口播视频（首选）**：用户自己出镜说话的视频。它既是声音也是画面主体，人整片都在，图表和字围着人换位置。
      先降噪、剪口误（`scripts/audio_tools.py cut 口播.mp4 剪好.mp4 --remove … --voice voice.wav --words …`，画面和声音在同一处剪，口型不会错位），
      再把剪好的视频设成 `meta.presenter`（`"fit": "cover", "loop": false`），`voice.wav` 设成 `meta.voice`。完整步骤见 `references/presenter.md`「真人口播视频」。
   2. **只有录音**：问用户要一个口播形象——本人照片或抠像、自己的卡通形象（透明 webm）、或一段录屏；都没有再用 `assets/host.webm`，或明确不要主体。
   3. **只有文案**：先问能不能自己录一遍（真人声音最好）；不能再用本地 TTS，主体同第 2 种。
   有了口播主体，**让用户选出镜形式**（整片一次，写 `meta.presenter.form`）：`full` 全屏口播 · `bubble` 圆形头像 · `split` 上下分屏 · `pip` 小窗 · `cutout` 抠像站位（素材要带透明）。
   先用用户自己的素材出一张对比图给他看着选：`python3 scripts/h9/presenter.py preview 口播.mp4 --focus 50,30 --out work/forms`（图在 `work/forms/stills/board_01.jpg`）。选定后各 beat 不写 `presenter` 也会跟着形式走；图文需要地方时，人会自动让开，不会被字压住脸。
   然后再问：横屏还是竖屏（可两个都要）？有没有要用的图片 / 截图 / 录屏？
2. **需求单**：`hat9.py brief new work/` → 填 `work/brief.md`：一句话片子、参考、节拍表（前 2 秒是**画面**钩子，之后每 3–5 秒一个视觉爆点）、全片 ≤ 3 句大字。用户想要某种说不清的感觉时，先 `hat9.py refs 参考1.mp4 参考2.mp4 … --out work/refs` 出参考板，把原则写进 `principles.md`。
3. **分镜**：`hat9.py plan "文案" --out work/` → `work/video.json`，按节拍表改：
   - 每个 beat 必须回答「这句话观众看见什么」；不合适就换 `fx`（id 见 `gallery/llms.txt`）。讲工具给真实录屏 / 截图，讲风格给同一内容不同风格并排。
   - 关键词写 `"@词"` 对时；说到「这个 / 这里」时加 `marks` 指哪说哪。
   - **同一个重点换着载体说**：数字和关键词优先用贴着主体的版式（`side_stat` `key_card` `stack_build` `stamp_compare` `strike_fix` `chip_cycle`）或数字画面（`mosaic_number` `seat_swarm` `dial` `log_scroll` `one_to_many` `scan_field` `card_fan`），全屏大字全片 ≤ 25% 且不连着用；有录屏 / 卡通形象 / 真人时开 `meta.presenter` 让它常驻并换位置（`references/presenter.md`），想要贯穿外框用 `meta.device`（`references/device.md`）；结尾用 `action_card`。
   - 相邻 beat 不连用同一个效果；章节之间才用招牌转场（`"tr": "zoomin"` 等），句间默认硬切。
   - **分镜检查**：`hat9.py brief check work/video.json --aspect 9:16`，P0 必须改（纯文字画面太多、一个画面撑太久、大字重复字幕）。
4. **配音**：口播视频的声音在第 1 步已经拆成 `voice.wav`，直接用；有录音就放进 `work/assets/audio/` 并在 `meta.voice` 指定（逐字时间戳 `meta.words` 用 `scripts/align.py`）；只有文案时 `hat9.py quick` 会自动选本地 TTS / 系统语音 / 静音。
5. **静帧板**：`hat9.py stills work/video.json --aspect 9:16` → 每个 beat 一张，带口播（加 `--settled` 再出一张每个 beat 结束前、全部内容出齐时的板）。按手机大小逐张看：读得清？和前后不一样？和这句话有关？改到满意。
6. **小样**：`hat9.py sample work/video.json --range 0,4 --aspect 9:16` 只做最难的几秒（开场钩子、快切），带声音看手感。
7. **整片 + 声音**：`hat9.py render work/video.json --aspect 9:16 --preview`。它会先自动跑分镜检查，有 P0 就**拒绝渲染**（改掉再来，确实要出才加 `--force`）；渲染完自动出每秒 2 帧的检查图并检查字幕碎片、音画偏差、字压脸、字太小、对比度，**有 P0 退出码非 0，不算完成**。配乐写 `meta.music`（旁边有 `.beats.json` 就自动卡拍：换画面、转场、音效吸到节拍上，不挪到口播词之前）、`"duck": true`（说话时压低）；无人声的快切段写成一个 `{"scene": "fx", "fx": "montage", "clips": [...]}` beat（每刀卡拍、自动挑每段最好看的一秒、每刀写明对应哪句话，配乐自动推上来）。渲染自动把响度标准化到 -14 LUFS。
8. **交付前自检**：`hat9.py review 成片.mp4 --video work/video.json [--ref 参考.mp4]`，P0 必须改；把静帧板逐张看完，在 `review.md` 里六项打分、写下最差的 3 处，改掉重渲。最后 `hat9.py review --gate review.md`，**过了才交付**，并告诉用户实际检查了什么。

最快体验（不改分镜）：`hat9.py quick "文案" --aspect 9:16`。

## 这些事代码会自动做（不用、也不要手动绕开）

- 字幕：一句一页，不在词中间断；真人画面上自动加深色底板。装上 `jieba` 断句更准（`hat9.py doctor` 会提示）。
- 竖屏字幕不压平台界面：9:16 每页字幕必须在底部 400 px（标题 / 音乐 / 评论栏）以上、顶部 200 px 以下，检查量的是字幕的真实位置，压进去算 P0。
- 对口播：清单的每一条、大字标题，没写 `at` / `"@词"` 时自动在说到它的那一刻出现。
- 版面：真人口播时，需要地方的图文不会压在脸上，人自动挪到小卡 / 侧边 / 选定的形式位。
- 缺内容直接报错（不画灰色占位条）：报错就补内容，别加 `skeleton: true` 糊过去。
- 检查：`render` 前后的检查会自己跑。看到 P1 也要打开检查图看一眼再交付。

## 硬规则

- 付费生成接口（Midjourney、Seedance、可灵、即梦、极九……）**每次调用前都要用户当场同意**；本技能本身不需要任何 key。
- 不用别人的 AI 图片和视频；字体只用 `assets/fonts.json` 里登记的字体（OFL / Apache / IPA，或标明免费商用的；后者不随仓库分发）；音效用 `scripts/sfx.py` 合成的。
- 画面是时间的函数：不写 `Math.random()`、`Date.now()`、无限循环；随机数用 `X.rand`（有种子）。
- 不轮询、不反复渲染整片试错：改 → 抽帧 → 再渲染。
- 不在没有用户同意时发布到任何平台或公开仓库。

## 目录

- `scripts/hat9.py` 命令行 · `scripts/build.py` video.json → HyperFrames 工程 · `scripts/h9/aefx.py` **AE 动效库**
- `gallery/` 在线画廊（`llms.txt` 效果索引、`effects.json`）· `references/effects/<id>.md` 每个效果的配方卡
- `references/video-json.md` 格式 · `references/motion-rules.md` 缓动 / 时长 / 对口播 · `references/sentence-to-visual.md` 句型 → 画面 · `references/aesthetics.md` 出图规则
- `styles/` 风格：`press` 财经刊（商业拆解 / 数据）· `screen` AI 工具台，暖白桌面窗口（产品界面 / AI 工具）· `atlas` 地图纪录（贸易 / 地缘）· `doc` 实拍纪录（实拍视频）· `minimal` 极简讲述，冷调浅底一条蓝线（观点 / 心理 / 认知）· `poster` 瑞士海报（观点 / 金句）· `zine` 拼贴杂志（潮玩 / 年轻消费）· `papercut` 层叠剪纸（节日 / 民俗）· `sketch` 手绘白板，牛皮纸（讲原理）· `ink` 水墨国风（国风 / 文化）· `flat` 五色扁平招贴（本地生活 / 城市）· `pixel` 像素复古（游戏 / 互联网）· `iso3d` 等距微缩（物流 / 产业链）· `chrome3d` Y2K 镀铬影棚（科技 / 芯片）· `riso` 孔版印刷，三色套印（消费 / 商业拆解）· `yuefen` 月份牌国货（老字号 / 国货）· `editorial` 影像杂志，真实照片（品牌 / 商业特写）· `title` 片头字幕，黑色胶片（财报 / 悬疑复盘）· `bauhaus` 包豪斯构成（观点 / 比例结构）· `thread` 一线长卷，一镜到底沿线走（年报 / 层层拆解）· `teleshop` 电视购物（消费 / 年度账本）· `vapor` 蒸汽波桌面，系统对话框（游戏 / 互联网）· `reel` 动效库 · `hud` · `studio` / `clay` 三维。选法见 `references/styles.md`；用户想要自己的风格时 `python3 scripts/hat9.py style new <id> --from <最接近的风格>`，改完 `style check`，输入范围见 `references/inputs.md`· `examples/` 可直接渲染的示例
