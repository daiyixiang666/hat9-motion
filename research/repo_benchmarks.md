# 视频 Agent / 视频 Skill 开源仓库对标（打包 hat9-motion 前的调研）

调研日期：2026-10-31。方法：`gh api` 读取仓库元数据、README 原文、文件树和清单文件（SKILL.md、plugin.json、openai.yaml、issue 模板、llms.txt）。只读了文本，没有克隆运行，也没有下载任何视频或图片（媒体文件大小来自 git tree 的 size 字段）。

标注约定：
- **【未验证】**：只看了 README 的说法，没有打开网站或实际跑过；
- **【推断】**：我对"为什么能起量"的判断，不是仓库自己说的。

星数是 2026-10-31 的 GitHub API 数字。"日均"等于总星数除以建仓天数，只能粗看增长速度（早期爆发和长尾分不开）。

---

## 0. 结论先说（5 条）

1. **最近半年涨得最快的视频仓库全是"给编程 agent 用的 skill"**，不是 WebUI 工具：OpenMontage 每天约 342 星，HyperFrames 约 325，lemo-opuscar 约 287（35 天到 1 万），brag 约 144，video-shotcraft 约 148。老一代的 MoneyPrinterTurbo 和 NarratoAI 靠的是 WebUI 加 Windows 一键包。
2. **首屏只放一样东西：真实成片在动。** 赢家的首屏都是"一句话 + 会动的成片或效果拼贴 + 一个通往在线画廊的大按钮"。赞助墙压在样片前面的 README（MPT、NarratoAI）是反例。
3. **效果库类仓库的标配是三件套**：在线画廊（GitHub Pages，每个效果自动循环播放，可搜索，可一键复制名字），每个效果一张"配方卡"（意图、参数、已知坑、可复制源码），以及给 agent 看的索引（shotcraft 的 `gallery/llms.txt`）。这正对应我们大约 40 个 AE 式效果。
4. **安装方式已经收敛**：①"把仓库链接丢给 agent"一句话；②`npx skills add owner/repo`；③Claude Code / Codex 的 plugin marketplace；④手动 clone，加国内镜像。中文仓库还会给"只能聊天的助手"（豆包、DeepSeek）一个单文件版。
5. **最有说服力的证据是对比**：同一个模型、同一份 brief，不用 skill 和用 skill 各做一条（motionmaxxing）；或者同一套流程做出完全不同的三支片（guizang、lemo）。我们之前收到的反馈是"风格太像"，这正好是要用对比去证明的地方。

---

## 1. 对标仓库总表

### 1a. 基本事实

| # | 仓库 | ⭐（日均） | 建仓 | 许可 | 类型 | 安装路径 | 文档 / agent 说明文件 |
|---|---|---|---|---|---|---|---|
| 1 | [harry0703/MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | 136.8k（142） | 2024-03 | MIT | WebUI + API + CLI，主题→短视频 | pip 包 `mpt`、Windows 一键包、Docker（ghcr 预构建）、Colab、**远程 SKILL.md 链接让 agent 自装** | `docs/skill/SKILL.md`（带 `compatibility`、`metadata.version: 1.3.2`）；README 三语 |
| 2 | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) | 76.5k（325） | 2026-03 | Apache-2.0 | HTML→视频的渲染框架，"Built for agents" | `claude plugin marketplace add` + `install`、`npx skills add heygen-com/hyperframes`、`npx hyperframes skills update`、`npx hyperframes init` | 7 个 skill（4 个核心常装、3 个按需装）；`.claude-plugin/`、`.agents/skills/`；文档站；`npx hyperframes doctor` |
| 3 | [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) | 73.9k（342） | 2026-03 | AGPL-3.0 | 全流程视频制作 agent 系统（Remotion 和 HyperFrames 二选一） | `git clone && make setup`，然后在 agent 里说需求 | `AGENT_GUIDE.md`、`PROJECT_CONTEXT.md`、`PROMPT_GALLERY.md`；`.agents/skills/*` 上百个，带 openai.yaml |
| 4 | [remotion-dev/remotion](https://github.com/remotion-dev/remotion) + [remotion-dev/skills](https://github.com/remotion-dev/skills) | 69.4k（30）+ 6.0k（21） | 2020 / 2026-01 | 自有许可（NOASSERTION）/ 未声明 | React 视频框架 + 官方 agent skills | `npx create-video@latest`；`npx skills add remotion-dev/skills`；`gh skill install remotion-dev/skills`；`bun create video` 时可勾选 | skills README 由脚本自动生成；**路由型 SKILL.md**（`version: 4.0.539` 与包版本同步）；每个子 skill 带 `agents/openai.yaml` |
| 5 | [ATH-MaaS/Pixelle-Video](https://github.com/ATH-MaaS/Pixelle-Video)（README 内链写的是 AIDC-AI 组织） | 29.6k（83） | 2025-11 | Apache-2.0 | WebUI，主题→全自动短视频（ComfyUI） | **Windows 一键整合包**（双击 start.bat）；`uv run streamlit run web/app.py` | 文档站（中文）、B 站视频教程徽章 |
| 6 | [latent-spaces/brag](https://github.com/latent-spaces/brag) | 19.7k（144） | 2026-06 | MIT | skill：把当前项目做成发布短片（基于 HyperFrames） | Codex 和 Claude 的 plugin marketplace、`npx skills add … --skill brag`、rsync 手动复制 | `skills/brag/SKILL.md` + 按步骤拆的 `references/step-1..4`；`.claude-plugin/`、`.codex-plugin/`、根目录 `plugin.json`（agent-plugins.org schema）；**软链到 `.claude/.agents/.opencode` 三个发现路径** |
| 7 | [Vincentwei1021/video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft) | 15.4k（148） | 2026-07 | Apache-2.0 | skill：产品宣传片，**124 张镜头卡、150 个镜头** | "Install this skill for me: <链接>"、`npx skills add`、clone + `ln -s` 到 `~/.claude/skills` 和 `~/.codex/skills`；**AtomGit 国内镜像** | 根目录 `SKILL.md`（**中英双语 description**，三种模式先分流）；`agents/openai.yaml`（中文 default_prompt）；**`gallery/llms.txt`**；`references/shots/<类>/<卡>.md` + `demos/<类>/<卡>/` |
| 8 | [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar) | 10.1k（287） | 2026-09 | MIT（代码）+ CC BY 4.0（样片） | skill：66 种影片风格，每种配一支代码做的短片 | `claude plugin marketplace add` + `install`；或 clone 后直接运行 `claude` | `DIRECTOR.md`（怎么导）、`TECHNIQUE.md`（怎么做）、`styles/<风格>/STYLE.md`；`AGENTS.md` 和 `CLAUDE.md`；`MY-STYLES.md`（自建风格流程） |
| 9 | [HKUDS/ViMax](https://github.com/HKUDS/ViMax) | 12.8k（22） | 2025-03 | MIT | 学术：多 agent 视频生成（导演、编剧、制片） | `git clone && uv sync`，配 yaml；带 WebUI 和 TUI | 中英 README、arXiv 论文、Roadmap |
| 10 | [linyqh/NarratoAI](https://github.com/linyqh/NarratoAI) | 11.7k（14） | 2024-08 | MIT | WebUI：影视解说加自动剪辑 | Windows 和 macOS 整合包、Docker、uv | 飞书官方文档；另有云端版 narratoai.cn |
| 11 | [Vincentwei1021/video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft) | 2.0k（28） | 2026-08 | PolyForm 非商业 | skill：**口播视频**，字级对时，108 张动效卡（**和我们最直接竞争**） | "帮我安装这个 skill：<链接>"、`npx skills add`、clone + ln | 中文 README 为默认；`SKILL.md` 八步管线；`references/cards/` 108 张；FAQ |
| 12 | [op7418/guizang-product-video-skill](https://github.com/op7418/guizang-product-video-skill) | 0.9k（21） | 2026-09 | AGPL-3.0 + 商业授权 | skill：代码库→产品宣传片（归藏） | `npx skills add … --skill …`，或"帮我安装这个 skill：<链接>"，或 clone 到 `~/.agents/skills` 和 `~/.claude/skills` | `SKILL.md` + `agents/openai.yaml`；`references/`、`scripts/`、`assets/fx-lab/`、`tests/` |
| 13 | [adunext/adu-motion-video](https://github.com/adunext/adu-motion-video) | 0.65k（20） | 2026-09 | MIT | 口播、知识讲解动效模板（现改为 MotionGit 的 `.motion` 单文件） | 下载 `.motion` 文件，直接发给助手；旧版提供 Release zip | `AGENTS.md`、`SKILL.md`、`agents/openai.yaml`；支持豆包、DeepSeek、WorkBuddy |
| 14 | [Tejashmakwana/motionmaxxing](https://github.com/Tejashmakwana/motionmaxxing) | 1.2k（47） | 2026-10 | Apache-2.0 | skill：把"AI 味"动效改成设计师水准（HyperFrames + GSAP） | 按 README 的 Install 一节【未细看】 | `SKILL.md`；把质量门 G0–G5 和"12 条实测缓动曲线"写成卖点 |

补充参考（不进主表，但各有一招可抄）：

| 仓库 | ⭐ | 可抄的一招 |
|---|---|---|
| [openfilm/openfilm](https://github.com/openfilm/openfilm) | 3.9k（27 天，日均 144） | `npx skills add openfilm/openfilm`；没有 skill 系统的 agent 就让它运行 `npx -y openfilm@latest`，按打印出来的手册走；发布视频是用自己做的 |
| [feitangyuan/onetake](https://github.com/feitangyuan/onetake) | 3.6k（日均 102） | 一句话卖点"一镜到底"；把"连贯性是量出来的"做成徽章；中英双语写在同一个 README |
| [nexu-io/html-video](https://github.com/nexu-io/html-video) | 4.8k | 功能型徽章：`agents-14 backends`、`templates-21`、`quickstart-3 commands` |
| [Vincentwei1021/anything2explainer](https://github.com/Vincentwei1021/anything2explainer) | 2.9k | 首屏放中英两条成片（user-attachments 内嵌视频），写明时长和配音；如实写"1–3 小时，4 个确认点" |
| [Remocn/remocn](https://github.com/Remocn/remocn) | 1.7k | 用 shadcn 注册表的方式分发效果（`npx shadcn add @remocn/blur-reveal`，代码归用户）；"Setup with AI"：把一段话粘进空文件夹里的 agent 就行 |
| [liangdabiao/whiteboard-teacher-video](https://github.com/liangdabiao/whiteboard-teacher-video) | 435（15 天） | 开头直接贴 5 条 **B 站成片链接**；"和普通 AI 生视频工具的区别"对比表；"零生图 API 成本"；依赖体积和安装耗时写成实测表 |
| [xiazhuo123456789/vibe-knowledge-video](https://github.com/xiazhuo123456789/vibe-knowledge-video) | 144 | "逆向自 8 条抖音爆款（1091 帧逐秒分析）"；方法论地图把每一步对应到文档；新手和熟手两条路径 |
| [zhuyansen/awesome-claude-video-skills](https://github.com/zhuyansen/awesome-claude-video-skills) | 1.3k | 收录规则：≥50 星只看主题；不足 50 星要过 README 质量线（**展示结果、一条命令启动、具体产出、文档完整**），并且至少 5 星 |
| [anthropics/skills](https://github.com/anthropics/skills) | 185.8k | 格式标准：`skills/<name>/SKILL.md` + `.claude-plugin/marketplace.json`；frontmatter 只强制要求 name 和 description |
| [Anil-matcha/AI-Youtube-Shorts-Generator](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator)（原 SamurAIGPT，已重定向） | 5.7k | "为什么用我而不用 Opus Clip"的对比表（价格、水印、额度、可自托管） |
| [RayVentura/ShortGPT](https://github.com/RayVentura/ShortGPT) / [gyoridavid/short-video-maker](https://github.com/gyoridavid/short-video-maker) / [showlab/Paper2Video](https://github.com/showlab/Paper2Video) | 8.1k / 1.5k / 2.4k | 上一代：Colab、Docker、MCP + REST、论文项目页。ShortGPT 自 2025-02 后没有再推送 |

### 1b. 首屏、首次成功、样片、社区、起量原因

| 仓库 | README 首屏（从上到下） | "60 秒首次成功"路径 | 样片怎么展示 | 社区钩子 | 起量关键【推断】 |
|---|---|---|---|---|---|
| MoneyPrinterTurbo | 标题 + 中文副标题 + 一句话 → 版本、平台、Python、下载量徽章 → Trendshift 和 Star History Rank 徽章 → `简体中文 \| English \| 日本語` → WebUI 截图 → **大段赞助墙**（Kimi、火山……） | 推荐用 AI Agent：粘贴"使用这个 Skill：<raw SKILL.md 链接>，帮我生成一个主题为…的视频"，agent 自装，只在缺 API Key 时才问 | "作品展示"分**竖屏 9:16 和横屏 16:9 两组，每组 8 条**，4 列缩略图（width=180），链到 GitHub Pages 播放器；视频放在另一个仓库 `mpt-assets` 的 Release 里 | Issues；赞助商返利链接 | 中文优先、免费素材（Pexels）加免费 TTS、WebUI 和 Windows 一键包、"Money Printer"这个名字本身就传播 |
| HyperFrames | 明暗双版 logo → npm、下载量、许可、Node、Discord 徽章 → 一句话 "Write HTML. Render video. Built for agents." → 导航（Studio、Quickstart、Showcase、Playground、Catalog、Docs、Discord）→ 桌面 App 动图 | `npx skills add heygen-com/hyperframes` 后试一句 prompt："Using /hyperframes, create a 10-second product intro…"；或 `npx hyperframes init → preview → render` | 官网 Showcase 和 Catalog（约 450 个 block）；README 里放 10 张设计模板 2 列网格（静图链到网站） | Discord、ADOPTERS.md（tldraw、TanStack）、预约 30 分钟用户访谈 | HeyGen 背书；对 agent 友好（纯 HTML、CLI 不需要交互）；Apache 许可对比 Remotion 的自有许可；`npx hyperframes add <block>` 注册表 |
| OpenMontage | 吉祥物 → 一句话 → 官网大徽章 → 锚点导航 → "#1 Repository of the Day"徽章 → YouTube、X、Discussions → **6 条内嵌成片**（每条下面写清用了哪些模型和工具） | `make setup` 后说"Make a 60-second animated explainer…"；**"零 API Key 能得到什么"表**；`make demo` 直接渲染零 key 示例 | GitHub user-attachments 内嵌视频，每条配一段制作说明；`PROMPT_GALLERY.md` 列出测过的 prompt、预期成本和样片 | Discussions、YouTube 频道、Star History | 只写"agent 打开项目就能用"；"Try These Prompts"按花费分档（零 key、约 $0.15–1.5、约 $1–3）；"从你喜欢的视频开始"；Backlot 实时看板 |
| Remotion / skills | 明暗双版 hero 图（avif/webp）→ Discord、npm、下载量、Twitter → 三条"Make videos agentically / interactively / programmatically" | `npx create-video@latest`；skill：`/remotion-create Make a promo video for a record store`；**默认不渲染，先开 Studio 预览** | 官网 showcase【未验证】 | Discord | 老牌框架；官方 skills 直接集成进脚手架 |
| Pixelle-Video | 标题 + 中英切换 → 徽章：B 站视频教程、Windows 包、使用文档、星、Issues、Forks、许可 → **内嵌演示视频** → 五条 emoji 列表"输入主题就能…" → WebUI 截图 → 最近更新 | Windows 整合包：双击 `start.bat`，浏览器打开 8501，填 API 就能出片 | 3 列视频表格：扩展模块、竖屏、横屏分组，每格写题材和模板名 | 微信群和 Discord 二维码并排（250px） | 阿里系背书【推断】；Windows 整合包；中文文档；接入 RunningHub 和 ComfyUI 生态 |
| brag | `# /brag` → "**You built it. Now brag.**" → 托管版入口 letsbrag.app → **hero 图链到发布网站，网站上循环播放的视频就是 /brag 给自己这个仓库做的** | `/plugin install brag@brag` 后在任意项目里说 "let's /brag" | 发布网站（GitHub Pages）；`examples/` 放 5 个假产品站，兼作基准测试集 | Star History、Contributing | 名字和口号好记；**自己用自己做宣传片**；一条命令出成果；有托管版降低门槛 |
| video-shotcraft | 明暗双版 logo → `English \| 中文 \| 日本語 \| Русский` → 徽章：**Gallery live previews**、**Showcase**、星、许可、Claude Code skill、Codex skill、AtomGit Star、Trendshift → **6 镜头拼贴的动态 webp（1.2 MB）** → "▶ Browse all 150 shots in the Gallery · 🎬 Watch the Showcase" | "Install this skill for me: <链接>"，然后"Use video-shotcraft to make a promo for my product."（"你说 → 会发生什么"表） | 在线画廊 150 个镜头（可搜索、筛选、复制卡名）【网站功能未验证】；README 按 10 个类别各放 1 张动态 webp（2 列，51–264 KB）；8 秒工作流 GIF | **Showcase 投稿 issue 表单 → 脚本自动发布**；赞助位；X、抖音、小红书关注徽章；Star History | 效果可视化做到极致；中文作者面向全球；**剪映草稿导出**；国内镜像；What's new 持续更新 |
| lemo-opuscar | 标题 + 一句话（数字用 `<!--n-->66<!--/n-->` 标记，可自动更新）→ 中文入口 → "▶ Watch the gallery" 大按钮 → Trendshift → "Built for Claude" 提醒 → **4 条带日期的 🆕 更新** → 招牌片 OPUSCAR 98（6:31，98 种风格） | `claude plugin install …`，然后"Make a 45-second film in the **watercolor** style about…"；只输入 `/lemo-opuscar:lemo-opuscar` 会先问语言和要做什么 | **每种风格一支完整短片**；README 里 3 列静帧 JPG（17–70 KB）链到 STYLE.md；视频放在 Release（`releases/download/films/*.mp4`）；GitHub Pages 画廊 | **每到一个星数里程碑做一支感谢短片**；X；"Watch → Custom → Releases"提示 | 一支招牌片引爆；风格数量多，每种都有真片；如实写"一条片 30–60 分钟、耗不少 token" |
| ViMax | logo → Trendshift → 一排徽章（Python、uv、许可、版本、YouTube、arXiv、**飞书群、微信群**、中英文、Quick Start）→ 先讲痛点，再讲方案 | `uv sync` 后配 yaml，跑 WebUI 或 TUI | "Video Demos Generated from Scratch"3 列内嵌视频 | 飞书和微信群（Communication.md） | 港大 HKUDS 品牌加论文；中文社群 |
| NarratoAI | 标题 + 副标题 + 中英切换 + 云端版入口 → 星、Issues 徽章 → 社群和飞书文档 → WebUI 截图 → 赞助福利 → **"⚠️谨防被骗"（有人改名后售卖）** | 整合包（Win、Apple Silicon）或 Docker，浏览器打开 8501 | 界面截图为主 | 开源社群（wiki 里的群）、Discord | 解说赛道刚需；整合包；同时有云端版 |
| video-talkcraft | logo → 徽章：Gallery、许可、**WeChat 讨论群** → 粗体一句话"口播视频的 agent skill：字级配音同步 · 108 张动效配方卡 · 七层反 PPT 镜头系统 · 三重验收" → 中英切换 → 画廊截图（链到网站） | "帮我安装这个 skill：<链接>"，然后"用 video-talkcraft 把这份口播稿 + voiceover.wav 做成视频" | 在线画廊，一页 108 个动效自动播放加搜索【未验证】；本地 `open gallery/index.html` | 微信群；README 里点名感谢社区贡献的卡 | 中文口播刚需；**实测数据表**（对时误差 20–40 ms，改一个镜头 53 秒出片）；FAQ |
| guizang | 标题 → 粗体一句话"软件更新了，顺手把宣传片也做了。" → 星、许可、Agent Skill、Claude Code、Codex 徽章 → 两句话讲清价值 → hero 静图 → **"30 秒开始"** | `npx skills add …` 后对 agent 说一整段需求，或"帮我安装这个 skill：<链接>，然后…" | 3 张说明图（约 100 KB 的 JPG）；**"同一套流程，三支不一样的片子"表**（CodePilot、Zed、T3 Code） | Issues 征集作品 | 归藏本人的影响力【推断】；"怎么提需求比较容易一次做好"给了 4 类 prompt 范例；FAQ 很诚实（"不是一键转换器"） |
| adu-motion-video | 标题 → 引用框公告（升级为 `.motion`）→ 封面图 640px → 一段说明 → 4 个链接（下载、如何开始、查看风格、指南） | 下载 `.motion` 发给助手，粘贴给出的那段 prompt | **每个模板一张 GIF（240×135，234–909 KB）+ 同名 mp4，每行 3 个**，链到 Pages 画廊 `?template=01-A`；每类标"横屏 ✓ · 竖屏 ✓" | MotionGit 主页 | 中文口播模板；连豆包、DeepSeek、WorkBuddy 都支持 |
| motionmaxxing | **hero GIF（3.5 MB）** → 一句话"Looksmaxxing for motion graphics." → 功能型徽章（eases-12 measured、mog check G0–G5、early release）→ 锚点导航 → 评分表 Slop / Mid / Maxxed | 【未细看】 | **前后对比 GIF：同一模型、同一 brief，不用 skill 和用 skill 各一条**（1.3–4 MB，并附 mp4） | X | 梗名加对比证据；"Glow-up, not a miracle"这种诚实口吻 |

---

## 2. "README 首屏"模式：最好的 README 按什么顺序排

GitHub 首屏大约 700–900 px 高，只装得下前 5 项。**第 1–6 项必须在第一次滚动之前出现**，赞助、安装细节、目录结构都放后面。

| 顺序 | 区块 | 写法要点 | 原文示例 |
|---|---|---|---|
| 1 | Logo 或字标（可选） | 明暗两版 `<picture>`，宽 96–200 px，别太大 | shotcraft 96px；OpenMontage 吉祥物 200px |
| 2 | 名字 + **一句话**（不超过 12 个英文词，或 20 个汉字） | 讲用户得到什么，不讲技术 | "Write HTML. Render video. Built for agents." / "You built it. Now brag." / "软件更新了，顺手把宣传片也做了。" |
| 3 | 语言切换 | 紧跟标题；面向中文用户就让中文 README 当默认 | `简体中文 \| English`（MPT、talkcraft）；lemo 用一行小字"🇨🇳 中文用户请看简体中文说明" |
| 4 | 徽章行（5–8 个） | **优先放能点的功能型徽章**：▶ Gallery、Showcase、Claude Code skill、Codex skill、微信群；星数、许可放最后 | shotcraft 第一行是 Gallery 和 Showcase 两个彩色徽章；html-video 用 `templates-21`、`quickstart-3 commands` |
| 5 | **Hero 动态媒体** | 自动播放的拼贴（webp 或 GIF，控制在 1.5 MB 以内）或内嵌 mp4；整张图可点击，通往画廊 | shotcraft `cover.webp`（6 镜头，1.2 MB）；OpenMontage 和 Pixelle 用 user-attachments `<video>` |
| 6 | 两个大 CTA | "▶ 在线看全部 N 个效果 · 🎬 看成片" | shotcraft："**▶ Browse all 150 shots in the Gallery** · **🎬 Watch the Showcase**" |
| 7 | 它做什么 / 不是什么（2–3 句） | 明说"不是视频生成模型，每一帧都是代码画的，可以继续改" | shotcraft "It is not a video generator."；guizang FAQ "是让模型生成一段视频吗？" |
| 8 | 工作流动图或流程图 | 8 秒循环：输入 → 分镜 → 选效果 → 渲染 → MP4 | shotcraft `workflow.gif`；Pixelle `flow.png` |
| 9 | 🆕 What's new（3–4 条，带日期） | 每条一句话，链到详情；**证明项目还活着** | lemo 4 条 🆕；shotcraft `[!IMPORTANT]` 提示框；talkcraft 注释里约定"每条一句话、≤200 字" |
| 10 | 30 秒开始 / 安装 | 从轻到重排：丢链接 → `npx skills add` → plugin → 手动；**每种方式一个代码块** | guizang "## 30 秒开始"；shotcraft "The simplest way is to hand your agent the link" |
| 11 | "你说 → 会发生什么"表 | 4–6 条可以直接复制的中文 prompt | shotcraft 的 Say / What happens 表；guizang 的"怎么提需求，比较容易一次做好" |
| 12 | 效果库网格（按类别） | 2–3 列，每格一张动态缩略图 + 效果名 + 一句说明；链到画廊锚点 | shotcraft 10 类 × 1 张 webp；adu 每类最多 3 个 GIF；lemo 3 列静帧 |
| 13 | 你提供什么 / 你得到什么 | 输入和交付物表（MP4 规格、可编辑工程、封面、字幕） | talkcraft "你提供什么 vs. 它做什么"；shotcraft "What you get" |
| 14 | 对比证据 | 不用和用的对比；同一份稿子出 N 种风格 | motionmaxxing glow-up；guizang 三支片对比表 |
| 15 | 环境要求 + 国内说明 | 用表格；镜像、CDN 被墙的处理 | shotcraft "Headless Linux / CI notes" 和 AtomGit 镜像 |
| 16 | 仓库结构（放进 `<details>`） | 树状图加一行说明 | shotcraft、talkcraft、guizang |
| 17 | FAQ | 免费吗、要会代码吗、能商用吗、能用豆包吗、是不是 AI 生视频 | talkcraft、guizang、vibe-knowledge |
| 18 | Showcase 投稿 + 社区 | issue 表单、微信群二维码、Discord | shotcraft showcase.yml；Pixelle 微信加 Discord 二维码 |
| 19 | 许可（按资产类型分开写）+ 致谢 | 代码、样片、字体、音效分别说明；对标的创作者"只学手法，不含素材" | lemo 分四类写许可；shotcraft Acknowledgements 的措辞 |
| 20 | Star History + 关注 + 里程碑 | 明暗两版图表；抖音、小红书、X 徽章 | lemo "Thank you for every star"感谢短片 |

**反面教材**：MPT 和 NarratoAI 把赞助墙放在样片前面（MPT 的样片在第 226 行才出现）；ShortGPT 首屏重复放了两个 Discord 徽章；gyoridavid 第一行是付费社群广告。

---

## 3. 安装与首次运行：按效果排序

### 3a. 安装入口（从好到次）

| 排名 | 方式 | 一行示例 | 谁在用 | 适合我们吗 |
|---|---|---|---|---|
| 1 | **把链接丢给 agent** | `帮我安装这个 skill：https://github.com/<you>/hat9-motion` | shotcraft、talkcraft、guizang、whiteboard | 最适合：零命令；豆包、WorkBuddy 这类中文助手也能理解 |
| 2 | **skills CLI** | `npx skills add <you>/hat9-motion`（多 skill 仓库加 `--skill hat9-motion`，`-g` 表示全局） | hyperframes、remotion、brag、shotcraft、openfilm、guizang | 必做：skills.sh 收录，支持 75+ 种 agent。要求根目录有 `SKILL.md`，或放在 `skills/<name>/SKILL.md` |
| 3 | **Plugin marketplace** | Claude：`/plugin marketplace add <you>/hat9-motion` → `/plugin install hat9-motion@hat9-motion`；Codex：`codex plugin marketplace add …` → `codex plugin add …` | hyperframes、brag、lemo、remocn、anthropics/skills | 建议做：有版本号，可以自动更新 |
| 4 | **远程 SKILL.md 链接** | `使用这个 Skill：https://raw.githubusercontent.com/…/SKILL.md，帮我做…` | MPT（SKILL.md 里写了"只加载了远程文件时，去官方仓库下载 helper"） | 可选，适合想"不装就试"的用户 |
| 5 | **单文件包给只能聊天的助手** | 把 `dist/hat9-motion.skill.md` 发给豆包或 DeepSeek | adu（`.motion`）、vibe-knowledge（"知识文档任何 AI 都能读"） | 我们已经有了，要放进 Release 并在 README 写清楚 |
| 6 | 一键整合包、Docker、Colab | 双击 `start.bat`、`docker compose up` | MPT、Pixelle、NarratoAI | 不适合（我们不是 WebUI） |
| 7 | 手动 clone + 软链 + 国内镜像 | `git clone … && ln -s "$(pwd)" ~/.claude/skills/hat9-motion` | 所有 skill 仓库都有；shotcraft 有 AtomGit 镜像 | 作为兜底，放在最后 |

注意事项：
- hyperframes README 提醒，`npx skills add` 读的是 skills.sh 注册表的快照，**可能比 main 晚几个小时**，所以它另外提供了 `npx hyperframes skills update`。我们可以在 README 里写"要最新版就用 git pull 或 plugin update"。
- brag 在 `.claude/skills/`、`.agents/skills/`、`.opencode/skills/` 下放软链指向 `skills/brag/`，clone 下来各家 agent 都能自动发现。Windows 需要开 `core.symlinks`，README 里专门写了一段提示。

### 3b. 让用户"第一次就成功"的做法

| 做法 | 例子 | 对我们的意义 |
|---|---|---|
| **零 key 也能出片**，并且写明 | OpenMontage 的"What You Get With Zero API Keys"表和 `make demo`；whiteboard 的"零生图 API 成本" | 我们本地合成音效、本地 TTS、HyperFrames 渲染，本来就是零 key。要写成一张表 |
| **doctor 自检** | `npx hyperframes doctor`；talkcraft `runtime/check-runtime.sh`；guizang 首次使用先检查 Node、Python、FFmpeg | 加一个 `scripts/doctor.py`：检查 Node 22、FFmpeg、Chrome、字体、hyperframes 版本 |
| **先预览，后渲染** | Remotion skill"默认不渲染，先开 Studio"；guizang"先给我看几张关键画面"；talkcraft"首镜先做先确认" | SKILL.md 里规定：先出 3 张关键帧或一个单镜预览，用户确认后再整片渲染 |
| **如实写时间和成本** | lemo"30–60 分钟、耗不少 token"；anything2explainer"1–3 小时、4 个确认点"；OpenMontage 按花费分档 | 写"60 秒竖屏约 X 分钟渲染（机型）"，**实测后再写** |
| **按场景给 prompt 范例** | OpenMontage "Try These Prompts"；guizang 4 类需求范例；lemo"Then just say what you want" | 4–6 条中文范例：有录音、只有文案、指定效果、改已有片 |
| **只问缺的** | MPT SKILL.md 的 Required Behavior：只在缺凭据时问一次，安装、生成都不需要确认 | 我们规定"只问三件事"，这一条要写进 README |
| **从参考视频开始** | OpenMontage"Paste a reference video"，先给 2–3 个方案和成本 | 进阶玩法：贴一条抖音参考，拆出节奏后套我们的效果 |

---

## 4. 样片和演示的展示方式

### 4a. 具体规格（来自各仓库 git tree 的文件大小）

| 用途 | 格式与大小 | 例子 |
|---|---|---|
| Hero 拼贴 | 动态 webp，**约 1.2 MB**，6 个镜头 | shotcraft `assets/readme/cover.webp` 1241 KB |
| Hero 单片 GIF | 3.5–5.4 MB（偏重，首屏加载慢） | motionmaxxing `hero.gif` 3537 KB；onetake `hero.gif` 5400 KB |
| 类别格子 | 动态 webp **51–264 KB**/张，2 列 | shotcraft `examples/*.webp` 10 张 |
| 模板格子 | GIF **240×135**（竖屏 135×240），234–909 KB，**同目录配同名 mp4** | adu `assets/demos/01-A.gif` + `01-A.mp4` |
| 风格静帧 | JPG **17–70 KB**，3 列 | lemo `docs/frames/*.jpg` |
| 前后对比 | GIF 1.3–4 MB + mp4 2.3–2.6 MB + poster JPG | motionmaxxing `*-comparison.gif/mp4` |
| 说明图 | JPG 约 100 KB | guizang `assets/readme/*.jpg` |
| 成片 | Release 附件（`releases/download/<tag>/x.mp4`）或 user-attachments 内嵌 | lemo、MPT 的 mpt-assets；OpenMontage、Pixelle、anything2explainer |

### 4b. 七种展示模式

1. **在线画廊（GitHub Pages）**：一页放全部效果，自动循环播放，可搜索、筛选，可点一下复制效果名（shotcraft 150 个，talkcraft 108 个，adu、lemo 也有）【交互功能按 README 描述，未打开验证】。README 里放一张画廊截图或拼贴，链过去（talkcraft 用的是 `gallery-zh.png` 截图）。
2. **README 里的分类网格**：每类 1 张代表图（shotcraft），或每类最多 3 个（adu）。**数量控制在 6–12 格**，完整列表交给画廊。
3. **内嵌成片**：GitHub 网页编辑器拖进 mp4，会生成 `user-attachments` 链接，`<video>` 能直接播放。OpenMontage 首屏就连放 6 条，每条下面一段制作说明（用了什么模型和工具）。shotcraft 的投稿表单写着拖拽上传上限 10 MB【GitHub 通用上限未核实】。
4. **竖屏和横屏分开放**：MPT 两组各 8 条；adu 每类标"横屏 ✓ · 竖屏 ✓"。**我们主打双画幅，这一点必须做出来。**
5. **对比**：不用 skill 和用 skill（motionmaxxing）；同一流程做出三支不同的片（guizang 表）；库里的风格和我改过的风格并排（lemo）。
6. **招牌片和自我宣传**：lemo 的 OPUSCAR 98 用 6 分 31 秒串起 98 种风格；brag 发布网站上的视频是 `/brag` 给自己做的；openfilm 的发布视频用 OpenFilm 自己做。**用自己的工具给自己做 README 视频，是最强的证明。**
7. **社区 Showcase 和里程碑**：shotcraft 用 issue 表单收集作品，审核后脚本自动发布到 Showcase 页；lemo 每到一个星数里程碑做一支感谢短片。

中文受众补充：whiteboard 开头直接贴 B 站成片链接；Pixelle 第一个徽章是"🎥 视频教程"（B 站）。抖音、小红书没有可以嵌进 README 的播放器，只能放链接加封面图。

**托管建议**：README 用的小图（webp、jpg，单张 300 KB 以内）放仓库 `assets/readme/`；mp4 放 GitHub Release（不会让仓库变大）；画廊用 GitHub Pages。国内访问 Pages 和 Release 可能慢，可以加 AtomGit 或 Gitee 镜像【国内访问速度未实测】。

---

## 5. Agent skill 的具体写法

### 5a. 规范硬约束（agentskills.io 规范，`agentskills/agentskills` 仓库的 `docs/specification.mdx`）

- `name`：1–64 个字符，只能用小写字母、数字和连字符，**必须和所在目录同名**。
- `description`：1–1024 个字符，要写清"做什么 + 什么时候用"，带上触发关键词。
- 可选字段：`license`（**顶层字段**）、`compatibility`（≤500 字符，写环境要求）、`metadata`（字符串到字符串的映射，例如 `version: "1.0"`）、`allowed-tools`（实验性）。
- 渐进加载：元数据约 100 token，SKILL.md 正文建议 <5000 token，**正文控制在 500 行以内**；引用文件**只往下一层**，不要连环嵌套。
- `npx skills add` 的发现路径：仓库根目录（有 `SKILL.md` 时）、`skills/`、`skills/<分类>/<name>/`、`.agents/skills/`、`.claude/skills/`、`.codebuddy/skills/`、`.trae/skills/`、`.qwen/skills/` 等 50 多个目录。

**我们现在的问题**：`SKILL.md` 把 `license` 写在了 `metadata` 里面（规范里它是顶层字段）；`metadata.version: "0.1.0"`，而 CHANGELOG 已经到 0.3.0；README 还写着"10 种风格"，但 CHANGELOG 0.2.0 说 0.1 的 10 种风格已经作废重做。打包前要把这几处统一。

### 5b. 最好的仓库怎么组织

| 部件 | 最佳做法 | 例子 |
|---|---|---|
| SKILL.md 开头 | **先分流**：判断用户要的是哪种任务、用的是什么模型，再进入流程 | brag：先判断模型和参数；shotcraft："只处理音效"直接去音效流程，整片制作分三种模式，并且"先做一次最小的只读检查，再推荐一种模式" |
| 硬规则清单 | 用"Required Behavior"列出要求：只问缺的；不轮询；前台运行，超时至少 20 分钟；不打印 key | MPT `docs/skill/SKILL.md` |
| 路由式 SKILL.md | 主文件只做导航："做 X 就读 `./x/REFERENCE.md`" | remotion-best-practices（description 就是"Router for all Remotion skills"） |
| description 双语 | 一段 description 里同时写英文和中文触发词 | shotcraft："…Use for full product promos… 用真实页面与镜头卡制作产品宣传片；用户要求…时使用。" |
| references 按步骤拆 | `step-1-inspect / step-2-plan / step-3-compose / step-4-deliver` | brag |
| references 按角色拆 | `DIRECTOR.md`（导）、`TECHNIQUE.md`（做）、`styles/<x>/STYLE.md`（风格） | lemo |
| 效果和镜头卡 | `references/shots/<类>/<卡>.md` + `demos/<类>/<卡>/` 实现；卡片字段：**意图、能量档、建议时长、参数、实现要点、已知坑、可复制的自包含源码、HTML 预览** | shotcraft 124 张；talkcraft 108 张（`template/cards/` 单文件复制就能用） |
| 给 agent 的效果索引 | `llms.txt`：每个效果一行，写名字、一句话描述、画廊锚点链接 | shotcraft `gallery/llms.txt`："- [fracture](…#fracture): Twenty-five 3D tiles fly in…" |
| scripts | 自检（doctor）、渲染、QA（3×4 联系表、静止帧检测、音效是否到位）、测试 | talkcraft `contact_sheet.py`；guizang `tests/`；vibe `render_frames.py --sheet` |
| examples | 可以直接跑的示例，**兼作回归测试集** | brag 的 5 个假产品站；我们的 `examples/demo` |
| Codex 展示信息 | `agents/openai.yaml`：`display_name`、`short_description`、`icon_small/large`、`brand_color`、`default_prompt` | shotcraft（中文 default_prompt）、remotion、guizang、adu |
| Plugin 清单 | `.claude-plugin/marketplace.json` + `plugin.json`（带 version）；`.codex-plugin/plugin.json`（`interface.defaultPrompt[]`、`category`、`capabilities`）；根目录 `plugin.json`（agent-plugins.org schema） | brag 三份都有；hyperframes、lemo |
| 仓库根目录说明 | `AGENTS.md` 或 `CLAUDE.md`：clone 下来后 Codex、Claude 自动读到 | lemo、vibe、adu；OpenMontage 用 `AGENT_GUIDE.md`，README 里还有一节"If You're An OpenClaw Agent Reading This" |
| 版本 | SemVer：SKILL `metadata.version`、plugin.json 的 version、CHANGELOG、Git tag 和 Release zip 都对上；README 写 What's new | remotion 的 skill 版本跟着包版本走；MPT 1.3.2；adu 每个版本出 Release zip；brag 0.5.0 |
| 自定义扩展 | 用户自建的风格和效果放在独立目录，**升级不覆盖** | lemo `~/lemo-my-styles/`（流程写在 MY-STYLES.md） |
| 注册表分发 | 单个效果可以单独装进用户工程 | `npx hyperframes add flash-through-white`；`npx shadcn add @remocn/blur-reveal` |

关于 llms.txt：除 shotcraft 外，没有找到其他视频 skill 仓库放 llms.txt。hyperframes 和 remotion 的文档站有没有提供 llms.txt，**我没有核实**。

---

## 6. 我们要超过它们的清单（按影响排序，约 25 条）

> 括号里是对标对象。"必做"是打包上线前就该完成的。

**A. 首屏和证据（影响最大）**
1. **必做｜用 hat9-motion 给自己做一支 README 视频**：竖屏和横屏各一条，15–25 秒，内容就是"这个仓库能做什么"的口播，同时把十几个招牌效果串起来。放在首屏，用 user-attachments 内嵌，另存一份 Release mp4。（brag、openfilm、lemo）
2. **必做｜Hero 拼贴**：6 个效果的动态 webp，**1.5 MB 以内**，宽 1200 px，横竖屏各占一半，可点击通往画廊。（shotcraft cover.webp）
3. **必做｜在线画廊（GitHub Pages）**：约 40 个效果和转场全部自动循环播放；有**横屏和竖屏切换**、搜索、按类别筛选、**点一下复制效果 id**；每个效果有锚点。README 第一行徽章就是"▶ 在线看全部 40 个动效"。（shotcraft、talkcraft、adu）
4. **必做｜一句话卖点**：中文不超过 20 字，再配一行英文。不要写"技能"这类词，要写用户得到什么，例如"一条口播，变成 AE 级动效成片（横竖屏）"。（brag、guizang）
5. **对比证据**：同一段口播，用"裸 Claude + HyperFrames"做一条，用 hat9-motion 做一条，左右并排放 GIF 和 mp4。旁边写明"同一模型、同一稿子"。（motionmaxxing）
6. **"同一段口播 × N 种风格"网格**：用来证明风格之间真的不一样（正好回应我们自己之前被批评的"风格太像"）。（guizang 三支片对比表、lemo）
7. **双画幅显式展示**：每个效果格子都标"横屏 ✓ · 竖屏 ✓"；样片分 9:16 和 16:9 两行放。（adu、MPT）

**B. 安装和首次成功**
8. **必做｜安装区按顺序写**：①"帮我安装这个 skill：<链接>"；②`npx skills add <you>/hat9-motion`；③Claude 和 Codex 的 plugin marketplace；④手动 clone 加 **Gitee 或 AtomGit 镜像**；⑤只能聊天的助手用单文件 `hat9-motion.skill.md`（放进 Release）。（shotcraft、guizang、adu）
9. **必做｜符合规范**：`name: hat9-motion` 和目录同名；`license` 改成顶层字段；`metadata.version` 和 CHANGELOG 同步；description 控制在 1024 字符以内，**中英双语触发词都要有**（口播、动效、字幕、竖屏、解说、AE 特效、explainer、motion graphics、kinetic typography）。（agentskills 规范、shotcraft）
10. **必做｜零 key 首次成功**：`examples/demo` 不需要任何 API key 就能渲染（本地 TTS、合成音效、自带字体）。README 写"零 key 能得到什么"表，加上**实测**的出片时间（机型 + 时长）。（OpenMontage、whiteboard）
11. **doctor 自检**：`python3 scripts/doctor.py` 检查 Node 22+、FFmpeg、Chrome、字体、hyperframes 版本，缺什么就给出对应的安装命令（macOS、Windows、Linux）。（hyperframes doctor、guizang）
12. **"你说 → 会发生什么"表**：5 条中文 prompt，覆盖有录音、只有文案、指定效果名、改某一段、贴参考视频。（shotcraft、guizang、OpenMontage）

**C. 效果库（我们的差异点）**
13. **每个效果一张配方卡**：`references/effects/<id>.md`，写意图、适合什么句型、时长、参数、已知坑、竖屏注意事项、对标的 AE 原型（出处和热度），并配一个 demo HTML。（shotcraft、talkcraft）
14. **给 agent 的效果索引 `effects/llms.txt`**（同时放在画廊根目录）：每行写 id、一句话描述、画廊锚点，让 agent 按名字选效果，不用读完整个库。（shotcraft gallery/llms.txt）
15. **README 效果网格**：6–10 个类别（入场、强调、数据、照片和拼贴、转场、质感），每类 1 张动态 webp（250 KB 以内，宽 480 px）+ 效果名 + 一句话说明。（shotcraft）
16. **单个效果可以单独用**：例如 `python3 scripts/h9 add <effect-id> <工程目录>`，让已有 HyperFrames 工程也能用我们的效果。之后可以考虑做成 HyperFrames registry 的 block。（hyperframes add、remocn）

**D. Agent 侧质量**
17. **SKILL.md 改成路由式，控制在 500 行以内**：开头先分流（整片 / 单个效果 / 改已有片 / 只要封面）；写一份硬规则清单（只问三件事；先出关键帧，确认后再整片渲染；付费接口必须先问；不轮询）；references 只往下一层。（remotion、MPT、shotcraft）
18. **多 agent 适配文件**：`.claude-plugin/{marketplace,plugin}.json`、`.codex-plugin/plugin.json`、`agents/openai.yaml`（中文 default_prompt"用 $hat9-motion 把这段口播做成竖屏动效视频"）、根目录 `AGENTS.md`，以及指向 skill 的 `.agents/skills`、`.claude/skills` 软链（README 附 Windows 说明）。（brag、shotcraft）
19. **版本和发布**：SemVer tag + GitHub Release（附 zip、单文件 skill.md 和样片 mp4）+ CHANGELOG；README 放 3 条带日期的 🆕 更新；`pack.py` 自动同步各处版本号。（lemo、adu、remotion）

**E. 信任、社区、增长**
20. **把账算清楚**：写清楚出片时间、token 消耗、在什么机器上实测、哪些已验证哪些还没验证；FAQ 里诚实回答"它不是一键成片"。（lemo、anything2explainer、guizang）
21. **交付物表**：MP4（1080×1920 和 1920×1080，30fps）、可编辑的 HyperFrames 工程、3 种比例的封面、SRT 字幕；之后可以做**剪映草稿导出**，这对中文创作者价值很高。（shotcraft JianYing export、guizang 封面）
22. **许可按资产类型分开写**：代码 MIT；样片 CC BY 4.0；字体 OFL 或 Apache；音效是我们自己合成的；`THIRD_PARTY.md`；对标创作者只学手法，不含他们的素材（参考 shotcraft Acknowledgements 的措辞）。加一句"本项目免费，谨防有人倒卖"。（lemo、NarratoAI）
23. **FAQ**：是 AI 生视频吗？要会代码吗？能用豆包或 DeepSeek 吗？能商用吗？竖屏效果会不会被裁？字体会不会显示成方块？同时有 SEO 作用。（talkcraft、guizang、vibe）
24. **Showcase 和社区**：`.github/ISSUE_TEMPLATE/showcase.yml` 投稿表单，审核后在画廊 Showcase 页展示，附作者的抖音或小红书；README 放微信群二维码徽章和抖音、小红书关注徽章；贴真实发布的抖音、B 站成片链接。（shotcraft、talkcraft、whiteboard）
25. **进入收录渠道**：skills.sh（装过就会出现）、awesome-claude-video-skills（≥50 星或过 README 质量线：展示结果、一条命令启动、具体产出、文档完整）、VoltAgent/awesome-agent-skills、HyperFrames 的 Showcase 和 ADOPTERS.md（提 PR）。（awesome-claude-video-skills 收录规则）
26. **Star History + 里程碑感谢片**：用自己的工具做，几乎没有额外成本，每次又是一条可以发抖音的内容。（lemo）
27. **CI 守住画廊**：`python -m unittest` 加一个工作流，每次提交给每个效果渲染 1 帧快照，避免画廊和代码对不上。（guizang tests、talkcraft 回归）

---

### 附：本次没有核实的内容
- 各在线画廊的搜索、筛选、复制功能，以及 HyperFrames 和 Remotion 文档站是否有 llms.txt。
- 微信群和 Discord 的活跃度、安装后实际出片要多久（都没有实测）。
- GitHub user-attachments 视频的通用大小上限（只看到 shotcraft 表单里写的 10 MB）。
- Pixelle-Video 的组织归属：仓库在 ATH-MaaS 下，README 内链写的是 AIDC-AI。
- 所有"起量关键"都是推断。

原始 README 文本存放在会话临时目录，没有放进本仓库。
