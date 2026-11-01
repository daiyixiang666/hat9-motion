# 调研总览（2026-10-31）

**方向**：不以本账号旧片为参考；向真正做得好的创作者和工作室学习，融合成多种风格。

| 文件 | 内容 |
|---|---|
| `visual_sampling.md` | 13 个标杆视频的画面抽样（YouTube 拖动条预览图，静音） |
| `bench_cn.md` | 国内知识区 / 口播包装：24 个账号逐帧实测，10 条共性、14 条禁用、10 个风格族 |
| `bench_global.md` | 海外解说 / 口播 / 视频随笔：21 个创作者，字幕配方，10 个风格族，钩子库 |
| `bench_craft.md` | 动效工作室手艺 + 设计系统动效 token + 可合法借用的开源代码（含许可核对） |
| 本文件（下文） | 开源视频 / 动效技能与模板的许可与可借鉴点 |

---

# 调研：开源视频 / 动效技能与模板

目的：给「九帽动效」（第九顶帽子自己的 AI 视频技能）定架构。每一项写清楚**许可**、**值得拿什么**、**不拿什么**。
许可用 `gh api repos/OWNER/REPO --jq .license.spdx_id` 和 LICENSE 原文核对；核不到的标「未核实」。
原则：只借**思路**；真要搬代码只搬 MIT / Apache / BSD / ISC，并记进 `../THIRD_PARTY.md`。别人的 AI 图、视频、Lottie 素材一律不搬。

---

## 1. 阿杜Next · adu-motion-video（MIT，5.2 万粉的核心资产）

- 仓库：https://github.com/adunext/adu-motion-video ，版本 3.14.1-rc.1，**MIT**（Copyright 2026 阿杜Next）。只读克隆，未运行其脚本。
- 结构：`SKILL.md`（路由）+ `references/` 40 多篇 + `packs/<风格>/<版本>/`（manifest、role、cues、motionWindows、slots）+ `adapters/` + `adaptation-profiles/` + `scripts/pipeline.py`（Win/mac/Linux 同一入口）+ 大量测试。
- 风格目录：「一级模板 → 二级风格」编号（01-A 原片节奏、01-D 杂志分屏、02-B 纸面聚合、03-A 深色 3D 多屏展陈、04-A 仪器台、05-A 鲜色角色……）。MotionGit 主页另有：Color Geometry、Dot-Grid Notes、Two-Color Risograph、Metro Network、Layered Papercut、Isometric Systems、Glowing Lightboard、Museum Timeline、**Growing Mind Map**、Chalkboard、Clay Lab、Swiss Grid 等 28 个模板，2.6 万次下载。

**值得拿的**
1. **可移植性是第一卖点**：一份 Skill 写明「Codex / Claude Code / 豆包 / DeepSeek / WorkBuddy 都能用」，先检查助手能不能读写文件、跑命令；Python 跨平台入口；字体缺失自动回退到随包 OFL 字体，**不因推荐字体缺失而拒绝制作**。
2. **用户引导话术**：「加载这个 skill，引导我开始创作」→ 只问口播/文案/横竖屏，其余可选，助手推荐模板。门槛极低，这是它能做成引流钩子的原因。
3. **编号化风格目录**：用户说「用 01-D」就能复现。编号永不改名。
4. **动作谱思维**（motion-quality.md）：每段写清「开始是什么—发生什么—结果是什么」；文字与容器错时（旧字先退→容器变形→新字进）；先铺路径再送文件；不用无意义的浮动/粒子冒充丰富度。
5. **动作保护窗**：关键动作原速锁死，长段只延长「可停留区」，时间不够就报错改分镜，不全片线性拉伸。
6. **检查方法**：看转场前中后的连续帧（60fps 不能用 1/30 当一帧）、正放倒放到同一时间画面一致、导出后核对帧数/响度。
7. 9 个轻量 TPL（hero / point / number / compare / steps / quote / demo / checklist / outro）——一个「句型 → 模板」的最小集合，好记。

**不拿的**
- 真人口播为中心（人脸跟踪、口播框让位）——我们是无脸账号，主角是柴犬 + AI 图。
- 版本/验收体系过重（candidate、SHA 绑定、review.json），对个人账号是负担；我们只保留「渲染后必看」的最小检查。
- 代码：没有直接复制任何文件。

## 2. MotionGit `.motion` 开放格式（spec 0.1.0-draft.1）

- https://motiongit.com/spec ，https://motiongit.com/@adunext 。格式文档公开，平台条款另议。
- 包结构：ZIP 根目录 `motion.json`（format=`motiongit-template`、runtime.profile=`html-canvas/1`、output 宽高/fps 用 num/den、durationPolicy fixed|range|fit-voiceover|fit-content）+ `params.schema.json`（JSON Schema 管可替换内容）+ `guide.json`（素材角色 video.presenter / image.photo / audio.voiceover / text.script…）+ `presets/` + `previews/` + `licenses/` + `integrity.json`（SHA-256）。
- 运行时契约：`window.renderFrame = (frame, inputs) => {}`，任意帧可独立 seek，随机数要显式 seed，不依赖墙钟。

**值得拿的**：参数与动画实现分离（JSON Schema）；素材角色表；`variants` 风格预设（≤24）；「文字太长就分页/换场景，不要缩到看不清」；声明 `permissions.network=false`。
**我们的做法**：九帽动效的场景参数同样用 JSON 描述，并预留 `motion.json` 导出（`scripts/pack.py --motion`，第二轮做），这样以后能上 MotionGit。

## 3. HyperFrames（heygen-com/hyperframes，Apache-2.0，本机已装 0.8.191）

- 本机技能：`~/.claude/skills/hyperframes*`；块库约 450 个（转场、叠加、标题、字效、字幕、图表、3D、镜头）。
- 渲染契约：`.clip` + `data-start` / `data-duration`；每个合成一个 paused GSAP timeline 注册到 `window.__timelines`；禁止 `Date.now()`、无种子随机、`repeat:-1`；`check` 静态检查 + `snapshot` 抽帧。ep02 实测：2 分钟成片 1 分 50 秒渲完。

**值得拿的**：直接**以它为渲染器**（Apache-2.0，确定性逐帧、快）。我们的产物就是合法的 HyperFrames 工程，所以用户也能在 HyperFrames 桌面版里继续改。块库里的颗粒、CRT、转场可按需 `hyperframes add` 后改皮肤。
**不拿的**：它的风格是通用英文产品片；中文排版、字幕、柴犬、审美判断都要我们自己做。

## 4. 作者本地的 Explainer Toolkit v2（未开源）

- 自家代码。21 个风格包（magazine / riso / darkroom / collage / shanshui / swiss / vhs …）、192 个组件、`verify.mjs`（实测字形重叠、遮挡、对比度、响度）。
- **值得拿的**：风格包字段设计（13 色主题 + 字体角色 + LUT + 招牌转场 + 常驻层 + 组件皮肤）；`verify.mjs` 作为可选的最后一关。
- **不拿的**：它绑定 Node 构建、素材库、edge-tts，面向纪录片式商业分析；太重，不便单文件分发。九帽动效保持「Python 标准库 + HyperFrames」即可跑。

## 5. Remotion（remotion-dev/remotion，~69k★）

- **许可：自定义 Remotion License，非 OSI**。个人/≤3 人公司/非营利免费，更大公司要买；禁止卖衍生品。→ **不用其代码**。
- remotion-dev/skills（~6k★，无 LICENSE，未核实）：一个路由 SKILL.md 按意图加载子文档；「先预览、用户没要就不渲」。
- 值得拿的思路：一切都是 `frame` 的纯函数；`interpolate` + clamp；`spring` 参数；`<Series>` / `<TransitionSeries>` 让转场跨两场重叠；用 schema（zod）校验模板 props；TikTok 模板的逐词字幕分页。

## 6. Motion Canvas（MIT，~19.6k★）/ Revideo（midrender/revideo，MIT，~4.2k★）

- 生成器式时间线：`yield* all(...)`、`chain`、`sequence`、`waitUntil('事件')`——把动画钉到口播事件上。
- Revideo：无头 `renderVideo()`、并行分块渲染 + FFmpeg 拼接。
- 拿：**按口播事件命名时间点**（我们的 beat 用 `at:"关键词"` 自动从逐字时间戳找时间）；动作语法 `all / chain / sequence` 映射成场景里的 stagger 规则。

## 7. Theatre.js（~12.8k★，2024 年后基本停更）

- **@theatre/core Apache-2.0，@theatre/studio AGPL-3.0** → 不打包 studio。
- 拿：关键帧状态存成 JSON，可视化手调后序列化。我们第二轮可考虑「手调覆盖层」`overrides.json`。

## 8. GSAP（greensock/GSAP，~30k★，v3.15）

- **许可：Webflow 的 Standard no-charge license，非 OSI**；商用免费，原付费插件（SplitText、DrawSVG、MorphSVG、CustomEase、Flip）全部免费；禁止用于与 Webflow 竞争的无代码可视化动画搭建器。
- 做法：**不随包分发 gsap.js，用 CDN（jsdelivr gsap@3.14.2，与 ep02 一致）**；文档写明许可。
- 拿：小而固定的缓动表（入 `expo.out` / `power3.out`，出 `power2.in`，强调 `back.out(1.7)`）；SplitText 的 `mask:'lines'` 字效思路；一个场景一条 paused timeline。

## 9. Lottie

- airbnb/lottie-web（MIT）、LottieFiles/dotlottie-web（MIT）；`goToAndStop(frame, true)` 可逐帧 seek。
- **LottieFiles 免费动画是 Lottie Simple License**：可商用可改，但再分发须保持同许可，且不能打包成竞品素材库 → **技能里不内置任何 Lottie 素材**，只给接入方法。

## 10. manim（3b1b/manim MIT ~96k★；ManimCommunity/manim MIT ~42k★）

- 拿：命名动作词汇 `Write / Create / FadeIn(shift) / Transform / Indicate / Circumscribe / LaggedStart(lag_ratio)`，以及 `rate_func` 和 `run_time` 默认值；manim-voiceover 的「动画时长 = 这句话的时长」。
- 我们的 `runtime/verbs` 用同样的名字思路：`write`（描字）、`draw`（描线）、`indicate`（强调）、`circumscribe`（画圈）、`lagged`（错峰）。

## 11. 中文 / 视频类 Agent 技能

| 仓库 | 许可 | 拿什么 |
|---|---|---|
| xiazhuo123456789/vibe-knowledge-video（~140★） | README 写 MIT，GitHub 识别为 Other，**未核实** | 最好的中文讲解技能写法：`structure-bible`、**句型 → 画面语法表**（21 种句型）、10 种转场带时长、`quality-gate`、130 秒 ≈ 44 个 beat 的拍子脚手架 |
| liangdabiao/whiteboard-teacher-video（~435★） | Other，未核实 | 手绘白板 MG + 自动音效 |
| Weikezi-AI/create-whiteboard-video（~53★） | MIT | 文案 + SRT + 音频 → `project.js` 清单 → 渲染 |
| jincheng2026/jc-remotion-skills（~15★） | Other，未核实 | 口播精剪：MG 包装、音效、母带 |
| haidrrrry/claude-remotion-skill（~740★） | MIT | 社区 Remotion 技能 |
| anthropics/skills（~186k★） | 顶层无许可，子技能各自 | SKILL.md 渐进披露的写法标准 |
| ComposioHQ / travisvn awesome-claude-skills | 无许可 | 只是目录；没有比 Remotion / HyperFrames 更强的动效条目 |

## 12. 字效、转场、质感

| 仓库 | 许可 | 拿什么 |
|---|---|---|
| gl-transitions/gl-transitions（~2.2k★） | 仓库 MIT（个别文件有作者头注，逐个核） | 约 80 个 GLSL 转场统一 `progress` 接口；第二轮可做 WebGL 转场层 |
| juliangarnier/anime（~74k★） | MIT | `stagger({from:'center', grid})` 错峰语法 |
| motiondivision/motion（~35k★） | MIT | 弹簧只用 `visualDuration + bounce` 两个参数，AI 好写 |
| shshaw/Splitting（~1.8k★） | MIT | 拆字后用 `--char-index` 做 CSS 错峰 |
| jschr/textillate（~3.6k★） | MIT | 字效预设命名（in/out × sequence/reverse/shuffle） |
| 颗粒 / 半调 / 纸张 | — | SVG `feTurbulence` 颗粒按帧换 seed；`mix-blend-mode:multiply` 纸纹；我们自己写，不搬 |

## 13. 编辑 / 数据可视化动效

- d3/d3（ISC）：对象恒定（key）、`d3-interpolate` 数字与路径插值 → 我们的数字滚动、柱图生长。
- the-pudding/svelte-starter（MIT）、russellsamora/scrollama（MIT）：「一步一个状态」的滚动叙事 = 一句口播一个画面状态；克制的编辑配色。
- Flourish SDK：仓库 404，未核实；只借「模板 = 数据 + 设置，故事 = 状态快照之间插值」的思路。

---

## 结论：九帽动效要比任何单一来源好在哪里

1. **无脸优先**：阿杜和大多数中文技能围绕真人口播；我们把「柴犬 + AI 图 + 字」当主角，所有场景不需要人脸。
2. **审美是内容本身**：频道讲「AI 时代凭什么是你」，所以技能里内置 意境 / 光 / 构图 / 色彩 / 质感 五条出图规则和每个风格的「气质说明」，不是只给动画。
3. **一个风格 = 一整套设计语言**：配色、字体、动作词汇、转场、音效、质感层、字幕皮肤、柴犬出场方式一起换（学 toolkit 风格包 + 阿杜「不能只换背景色」）。
4. **轻**：Python 标准库 + HyperFrames，可选 fontTools 子集化；一份 `.skill.md` 单文件能直接丢给 豆包 / DeepSeek（它们不能执行时也能照着写出 HTML）。
5. **自家音效**：所有 SFX 用 ffmpeg 合成，MIT 可分发（Pixabay 素材不允许单独再分发）。
6. **钉口播**：beat 可以写 `at:"关键词"`，从逐字时间戳自动对时（学 Motion Canvas `waitUntil` / manim-voiceover）。
