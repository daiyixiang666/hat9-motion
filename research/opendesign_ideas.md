# 从 OpenDesign 借来的点子（只列不做）

来源：[nexu-io/open-design](https://github.com/nexu-io/open-design)（Apache-2.0，2026-10-31 读取）。这次已经借进来的有：
- 插件市场清单 `.claude-plugin/`；
- 手艺规矩 `references/craft.md` 和 `scripts/craft_lint.py`；
- DESIGN.md 转风格 `scripts/design_md.py`。

下面是还没做、值得做的。编号对应 [`cases.json`](cases.json)；「谁来做」只是建议。移植任何 skill 的代码前，先看那个 skill 自己的许可（仓库整体是 Apache-2.0，个别 skill 另有 MIT 等声明，如 `huashu-art-motion`）。

## 流程与工具

| 点子 | OpenDesign 里的出处 | 我们可以做成 | 对应情况 | 建议 |
|---|---|---|---|---|
| 参考片测量包：一条参考视频 → 时长、帧率、尺寸、有无音轨、镜头切点（场景阈值 0.3）、每个镜头一帧、整片联系表、原声 WAV | `apps/daemon/src/media/motion-reference.ts` | `scripts/reference.py`：README「按这个参考视频的节奏做」那一行目前没有工具支撑，这是最直接的补位 | V12 ❌ | 高，单人小活 |
| 成片对照：把我们的成片和参考片在同一批时间点并排，逐对算结构相似度（SSIM），列出最不像的时间点 | `apps/daemon/src/media/motion-compare.ts` | `scripts/compare.py`：分数只告诉你先看哪一秒，判断还是靠人和模型 | V12、QC | 中，和上一条一起做 |
| 透明通道导出：聊天、字幕、标注做成带 alpha 的视频，直接叠进剪映或 Premiere | `skills/chat-motion-overlay`（Remotion 版） | 渲染参数加 `--alpha`，输出带透明的 WebM 或 MOV；先查 HyperFrames 是否支持透明底渲染 | F07、M07 | 中 |
| 「每屏强调色最多 2 处」「`:root` 之外的裸色值超过 12 个」两条 lint | `craft/anti-ai-slop.md` 的 P1 软规则 | 加进 `craft_lint.py`：按片段数强调色用量、数裸色值 | — | 低，顺手 |

## 效果与模板

| 点子 | OpenDesign 里的出处 | 我们可以做成 | 对应情况 | 建议 |
|---|---|---|---|---|
| 小红书式知识卡轮播：3:4 多张卡左右滑，一张一个要点 | `skills/card-xiaohongshu` | 新效果 `card_carousel`；同时是 3:4 / 4:5 比例的第一个专门排版 | U12 ❌、M05 🟡、C13 🟡 | 高 |
| 新闻编辑部图表：NYT 式排版，逐层揭示，区间带折线 | `skills/frame-data-chart-nyt` | 给 `line_draw` 加区间带和编辑式注释（WP2 的范围） | U13 ✅ 可加强、B 类 | 中 |
| 白板流程图：便利贴节点 + 手绘曲线连线 + 光标拖拽 | `skills/frame-flowchart-sticky` | `steps` 的「白板」皮肤（WP1），或单独的 `sticky_flow` | K01 🟡、G07 🟡、E12 🟡 | 中 |
| 胶片漏光章节卡：漏光 + 颗粒 + 遮幅 + 大号衬线字 | `skills/frame-light-leak-cinema` | `chapter_cinema`，也可做 WP5 章节喘息页的一种 | L03 ✅ 可加强、S07 🟡 | 中 |
| Logo 分段组装落版：标志按笔画或部件拼合 + 辉光 + 标语 | `skills/frame-logo-outro` | `logo_reveal`（SVG 路径分段，只用用户自己的标志）；顺带做 Logo 墙 | I07 🟡、C11 ❌ | 中 |
| 流体背景金句：流体位移背景上压一句话 | `skills/frame-liquid-bg-hero` | `liquid_bg`：用种子噪声的着色器或 Canvas，保证逐帧确定；可做留白页背景 | A14 ✅ 可加强、S03 🟡 | 低 |
| 光标光轨逐字引语：光标拖出光轨和色散，字一个个点亮 | `skills/vfx-text-cursor` | `cursor_reveal`：金句和引语的另一种出场 | A01、A14 ✅ 可加强 | 低 |
| 桌面通知横幅 | `skills/frame-macos-notification` | `notify` 加桌面皮肤（平台中立，不用任何系统标志） | G03 ✅ 可加强 | 低 |
| 竖屏年度回顾报告：纸纹、书页隐喻、个人数据高亮 | `skills/weread-year-in-review-video-template` | 一个「年度回顾 / 个人数据报告」风格或模板，吃一份 CSV 或 JSON | 新情况：个人数据回顾 | 中 |
| 艺术风格解说语法：35 种艺术材料配方 + 9 种解说镜头语法 + 确定性 Canvas 笔刷工具 | `skills/huashu-art-motion`（MIT） | 「艺术段落」效果族：水彩、水墨、剪纸、版画的过场与情绪段；把「让具体的物体解释内容，少用连续标题卡」写进镜头表模板 | C18 🟡、T05、S05 | 中，先读许可和配方 |
| 160 个动效案例库，带参数和中英文索引 | `skills/motion-lab` | 作为挑效果时的参照索引，不搬代码 | — | 低，先确认许可 |

## 不借的

- `design-systems/` 里 150 套品牌设计系统（Apple、Stripe、Airbnb……）：都是真实品牌，借来做视频有冒用风险。只借了它的 DESIGN.md 格式。
- 云端素材检索、付费生图生视频（`fal-*`、`venice-*`、`od-next-media-inputs` 的库存图搜索）：要账号和付费，和「零 key」定位冲突。
