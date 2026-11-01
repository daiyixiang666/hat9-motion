---
name: hat9-motion
description: 九帽动效 hat9-motion — 把口播、文案或录音做成 AE 级动效视频（横屏 16:9 / 竖屏 9:16）。内置按 VideoHive 销量、YouTube 与 B 站播放量复刻的 40 个 AE 动效与转场（2.5D 照片视差、重拍排版 Stomp、瞳孔穿梭、文字匹配剪辑、照片墙、手机通知、数字滚动、无缝缩放转场……），自动分镜、对准口播逐字时间、字幕、柴犬主持人，HyperFrames 逐帧确定渲染，零 API key 可出片。Use when the user wants an explainer / talking-head / 口播 / 解说 / 知识类短视频、动效、motion graphics、kinetic typography、AE 特效、片头、字幕包装、竖屏抖音视频, or asks to "turn this script into a video".
license: MIT
compatibility: Python 3.9+, Node.js 22+, FFmpeg; Chrome is fetched by HyperFrames on first render. Works in Claude Code, Codex, Cursor, WorkBuddy and any agent that can run shell commands; chat-only assistants use dist/hat9-motion.skill.md.
metadata:
  version: "0.7.0"
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
| 「我有 PDF / 论文 / 新闻 / 截图 / 录屏 / 表格 / 一堆图 / 一个网址」 | 先查 `references/inputs.md` 找对应效果（`cite_*`、`media`、`scroll_shot`、`screencast`、`table` …）；网址用 `scripts/url_brief.py`，表格用 `csv` 参数 |
| 「只有录音没有逐字时间」 | `scripts/align.py 录音 稿子 --out words.json` |
| 「看着像 AI 模板 / 不高级」 | 先读 `references/craft.md`，再跑 `python3 scripts/craft_lint.py <构建目录>` 查默认手法 |
| 环境报错 | `hat9.py doctor`，按提示补齐 |

## A. 整片（默认流程）

1. **只问三件事**（已给的不再问）：口播是录音还是只有文案？横屏还是竖屏（可两个都要）？有没有要用的图片 / 截图？
2. **出分镜**：`hat9.py plan "文案" --out work/` → `work/video.json`。一句一个 beat，按句型自动挑效果（`references/sentence-to-visual.md`）。**检查并改它**：
   - 每个 beat 必须回答「这句话观众看见什么」；不合适就换 `fx`（id 见 `gallery/llms.txt`）。
   - 关键词写 `"@词"` 对时；说到「这个 / 这里」时加 `marks` 指哪说哪。
   - 相邻 beat 不要连用同一个效果；章节之间才用招牌转场（`"tr": "zoomin"` 等），句间默认硬切。
3. **配音**：有录音就放进 `work/assets/audio/` 并在 `meta.voice` 指定（逐字时间戳 `meta.words` 用任何对齐工具生成）；只有文案时 `hat9.py quick` 会自动选本地 TTS / 系统语音 / 静音。
4. **先看关键帧再整片渲染**：`hat9.py build work/video.json --aspect 9:16`，在 `work/build/...` 里 `npx --yes hyperframes@0.8.191 snapshot --at 1,4,8` 看几帧，有问题先改。
5. **渲染**：`hat9.py render work/video.json --aspect 9:16 --preview`（横竖都要就各跑一次）。`check` 有 error 不会渲染，按报错修。
6. **交付前**完整看一遍、听一遍；告诉用户实际检查了什么。

最快体验（不改分镜）：`hat9.py quick "文案" --aspect 9:16`。

## 硬规则

- 付费生成接口（Midjourney、Seedance、可灵、即梦、极九……）**每次调用前都要用户当场同意**；本技能本身不需要任何 key。
- 不用别人的 AI 图片和视频；字体只用 `assets/fonts.json` 里的 OFL / Apache 字体；音效用 `scripts/sfx.py` 合成的。
- 画面是时间的函数：不写 `Math.random()`、`Date.now()`、无限循环；随机数用 `X.rand`（有种子）。
- 不轮询、不反复渲染整片试错：改 → 抽帧 → 再渲染。
- 不在没有用户同意时发布到任何平台或公开仓库。

## 目录

- `scripts/hat9.py` 命令行 · `scripts/build.py` video.json → HyperFrames 工程 · `scripts/h9/aefx.py` **AE 动效库**
- `gallery/` 在线画廊（`llms.txt` 效果索引、`effects.json`）· `references/effects/<id>.md` 每个效果的配方卡
- `references/video-json.md` 格式 · `references/motion-rules.md` 缓动 / 时长 / 对口播 · `references/sentence-to-visual.md` 句型 → 画面 · `references/aesthetics.md` 出图规则
- `styles/` 风格：`press` 财经刊（商业拆解 / 数据）· `screen` AI 工具台（产品界面 / AI 工具）· `atlas` 地图纪录（贸易 / 地缘）· `doc` 实拍纪录（实拍视频）· `poster` 瑞士海报（观点 / 金句）· `reel` 动效库 · `hud` · `studio` / `clay` 三维。选法见 `references/styles.md`，输入范围见 `references/inputs.md`· `examples/` 可直接渲染的示例
