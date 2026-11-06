---
name: hat9-motion
description: 九帽动效 hat9-motion — 把口播、文案或录音做成 AE 级动效视频（横屏 16:9 / 竖屏 9:16）。内置 18 种风格（财经刊、极简讲述、瑞士海报、剪纸、手绘白板、水墨、像素、拼贴杂志、等距微缩、镀铬三维……）和 160 个按 VideoHive 销量、YouTube 与 B 站播放量复刻的 AE 动效与转场（2.5D 照片视差、重拍排版 Stomp、瞳孔穿梭、文字匹配剪辑、照片墙、数字滚动、引用、图表、地图……），自动分镜、对准口播逐字时间、字幕、柴犬主持人，HyperFrames 逐帧确定渲染，零 API key 可出片。Use when the user wants an explainer / talking-head / 口播 / 解说 / 知识类短视频、动效、motion graphics、kinetic typography、AE 特效、片头、字幕包装、竖屏抖音视频, or asks to "turn this script into a video".
license: MIT
compatibility: Python 3.9+, Node.js 22+, FFmpeg; Chrome is fetched by HyperFrames on first render. Works in Claude Code, Codex, Cursor, WorkBuddy and any agent that can run shell commands; chat-only assistants use dist/hat9-motion.skill.md.
metadata:
  version: "0.13.0"
  author: 第九顶帽子
---

# 九帽动效 hat9-motion

`SKILL_DIR` = 本文件所在目录。命令都用 `python3 $SKILL_DIR/scripts/hat9.py …`（Windows：`python`）。

## 先分流：用户要什么？

| 用户说 | 走哪条路 |
|---|---|
| 「把这段文案 / 录音做成视频」 | **A. 整片** |
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

1. **只问三件事**（已给的不再问）：口播是录音还是只有文案？横屏还是竖屏（可两个都要）？有没有要用的图片 / 截图 / 录屏？
2. **需求单**：`hat9.py brief new work/` → 填 `work/brief.md`：一句话片子、参考、节拍表（前 2 秒是**画面**钩子，之后每 3–5 秒一个视觉爆点）、全片 ≤ 3 句大字。用户想要某种说不清的感觉时，先 `hat9.py refs 参考1.mp4 参考2.mp4 … --out work/refs` 出参考板，把原则写进 `principles.md`。
3. **分镜**：`hat9.py plan "文案" --out work/` → `work/video.json`，按节拍表改：
   - 每个 beat 必须回答「这句话观众看见什么」；不合适就换 `fx`（id 见 `gallery/llms.txt`）。讲工具给真实录屏 / 截图，讲风格给同一内容不同风格并排。
   - 关键词写 `"@词"` 对时；说到「这个 / 这里」时加 `marks` 指哪说哪。
   - 相邻 beat 不连用同一个效果；章节之间才用招牌转场（`"tr": "zoomin"` 等），句间默认硬切。
   - **分镜检查**：`hat9.py brief check work/video.json --aspect 9:16`，P0 必须改（纯文字画面太多、一个画面撑太久、大字重复字幕）。
4. **配音**：有录音就放进 `work/assets/audio/` 并在 `meta.voice` 指定（逐字时间戳 `meta.words` 用 `scripts/align.py`）；只有文案时 `hat9.py quick` 会自动选本地 TTS / 系统语音 / 静音。
5. **静帧板**：`hat9.py stills work/video.json --aspect 9:16` → 每个 beat 一张，带口播。按手机大小逐张看：读得清？和前后不一样？和这句话有关？改到满意。
6. **小样**：`hat9.py sample work/video.json --range 0,4 --aspect 9:16` 只做最难的几秒（开场钩子、快切），带声音看手感。
7. **整片 + 声音**：`hat9.py render work/video.json --aspect 9:16 --preview`。配乐写 `meta.music`（旁边有 `.beats.json` 就自动卡拍：换画面、转场、音效吸到节拍上，不挪到口播词之前）、`"duck": true`（说话时压低）；无人声的快切段写成一个 `{"scene": "fx", "fx": "montage", "clips": [...]}` beat（每刀卡拍、自动挑每段最好看的一秒、每刀写明对应哪句话，配乐自动推上来）。渲染自动把响度标准化到 -14 LUFS。
8. **交付前自检**：`hat9.py review 成片.mp4 --video work/video.json [--ref 参考.mp4]`，P0 必须改；把静帧板逐张看完，在 `review.md` 里六项打分、写下最差的 3 处，改掉重渲。最后 `hat9.py review --gate review.md`，**过了才交付**，并告诉用户实际检查了什么。

最快体验（不改分镜）：`hat9.py quick "文案" --aspect 9:16`。

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
- `styles/` 风格：`press` 财经刊（商业拆解 / 数据）· `screen` AI 工具台（产品界面 / AI 工具）· `atlas` 地图纪录（贸易 / 地缘）· `doc` 实拍纪录（实拍视频）· `minimal` 极简讲述（观点 / 心理 / 认知）· `poster` 瑞士海报（观点 / 金句）· `zine` 拼贴杂志（潮玩 / 年轻消费）· `papercut` 剪纸（节日 / 民俗）· `sketch` 手绘白板（讲原理）· `ink` 水墨国风（国风 / 文化）· `flat` 扁平插画（本地生活 / 城市）· `pixel` 像素复古（游戏 / 互联网）· `iso3d` 等距微缩（物流 / 产业链）· `chrome3d` Y2K 镀铬（科技 / 芯片）· `reel` 动效库 · `hud` · `studio` / `clay` 三维。选法见 `references/styles.md`；用户想要自己的风格时 `python3 scripts/hat9.py style new <id> --from <最接近的风格>`，改完 `style check`，输入范围见 `references/inputs.md`· `examples/` 可直接渲染的示例
