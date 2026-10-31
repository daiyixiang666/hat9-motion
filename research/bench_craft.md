# 调研：顶级动效工作室的手艺 + 可合法借用的开源动效代码（2026-10-31）

服务对象：九帽动效（hat9-motion），HTML + CSS + GSAP，由 HyperFrames 0.8.191 逐帧渲染成 MP4。频道是无脸中文口播讲解：戴高帽的柴犬会说话，画面用 AI 图和 B-roll，主画幅 16:9。
目标：做出来的动效像顶级工作室出品，而不是模板。

写法约定：
- **已核实**：读过一手来源（官方文档、源码常量、LICENSE 原文、`gh api` 查到的许可）。
- **推导**：用已核实的数字算出来的，算法写在旁边。
- **未核实**：凭行业常识或二手资料，没找到一手出处。
- 许可只认 MIT / Apache-2.0 / BSD / ISC 可以搬代码；其余许可只借思路、自己重写。与 `SOURCES.md` 不重复的部分才展开。

---

## A. 手艺原则

### A1. 一手数字：设计系统的动效 token（已核实）

**Material Design 3**（数字取自 androidx `MotionTokens.kt` / `StandardMotionTokens.kt` / `ExpressiveMotionTokens.kt` 源码常量；m3.material.io 是 JS 渲染页，抓不到正文）

| 缓动 token | cubic-bezier |
|---|---|
| Emphasized（M3 官方是路径曲线，CSS 用这个近似） | (0.2, 0, 0, 1) |
| Emphasized Decelerate（入场） | (0.05, 0.7, 0.1, 1) |
| Emphasized Accelerate（退场） | (0.3, 0, 0.8, 0.15) |
| Standard | (0.2, 0, 0, 1) |
| Standard Decelerate | (0, 0, 0, 1) |
| Standard Accelerate | (0.3, 0, 1, 1) |
| Legacy（= M1/M2 standard） | (0.4, 0, 0.2, 1) |

时长 token：short1–4 = 50/100/150/200 ms；medium1–4 = 250/300/350/400 ms；long1–4 = 450/500/550/600 ms；extra-long1–4 = 700/800/900/1000 ms。

M3 弹簧 token（质量取 1）。overshoot 与时长是我用 ζ 和 k 算的推导值：

| 方案 | spatial（位置/尺寸）ζ / k | effects（透明度/颜色）ζ / k | 推导：overshoot，周期 2π/√k |
|---|---|---|---|
| Standard default | 0.9 / 700 | 1.0 / 1600 | 0.2%，0.24 s |
| Standard fast / slow | 0.9 / 1400；0.9 / 300 | 1.0 / 3800；1.0 / 800 | 0.2%，0.17 s / 0.36 s |
| **Expressive default** | **0.8 / 380** | 1.0 / 1600 | **1.5%，0.32 s** |
| Expressive fast | 0.6 / 800 | 1.0 / 3800 | 9.5%，0.22 s |
| Expressive slow | 0.8 / 200 | 1.0 / 800 | 1.5%，0.44 s |

两条可以直接拿来用的规律：**effects 弹簧一律 ζ=1**，也就是透明度和颜色永远不回弹，这与 HyperFrames motion.md「opacity and colour never do」一致；**想要显得高级就用 ζ≈0.8**。

**Material 1（m1.material.io 正文可读，已核实）**
- 手机基线约 300 ms；全屏大转场 375 ms；入场 225 ms，退场 195 ms；超过 400 ms 就开始显得慢。平板时长 +30%，穿戴设备 −30%，桌面 150–200 ms。
- 原文要点：时长随**位移距离、速度、表面积变化**一起变长；退场可以更短，因为观众不需要盯着它看。
- 曲线：standard (0.4,0,0.2,1)、decelerate (0,0,0.2,1)、accelerate (0.4,0,1,1)、sharp (0.4,0,0.6,1)。

**IBM Carbon（已核实）**

| 曲线 | productive（干活型） | expressive（表达型，更适合视频） |
|---|---|---|
| standard | (0.2, 0, 0.38, 0.9) | (0.4, 0.14, 0.3, 1) |
| entrance | (0, 0, 0.38, 0.9) | (0, 0, 0.3, 1) |
| exit | (0.2, 0, 1, 0.9) | (0.4, 0.14, 1, 1) |

时长 token：fast-01 70 ms（按钮）、fast-02 110 ms（淡入淡出）、moderate-01 150 ms（短位移）、moderate-02 240 ms（展开、toast）、slow-01 400 ms（大展开）、slow-02 700 ms（背景压暗）。
Carbon 明说用的是**非线性**时长刻度：距离翻倍，时长远不到翻倍。对象离开后可能回来（比如侧栏）用 standard 曲线，永久离开才用 exit 曲线。

**Apple**
- HIG Motion 只有定性要求（已核实，读的是 developer.apple.com 的 JSON 正文）：有目的地加动效，不为动而动；过量动画让人分心甚至身体不适；反馈动画要短而准；不要让人等动画播完；游戏保持 30–60 fps。
- SwiftUI 弹簧只有两个参数：duration 和 bounce（−1…1）。WWDC23《Animate with springs》演示用 duration 0.5、bounce 0.15（几乎感觉不到弹）和 0.3（能明显感到弹）；bounce 超过约 0.4 对 UI 来说太夸张；不确定时用 bounce 0（已核实，来源 WWDC notes）。
- 「bounce = 1 − ζ」这个换算未核实。如果成立：bounce 0.15 ≈ ζ 0.85，overshoot 0.6%；bounce 0.3 ≈ ζ 0.7，overshoot 4.6%。

**GSAP**
- 默认 ease 是 `power1.out`。power1–4 分别等于 quad / cubic / quart / quint，power4 又叫 strong（已核实，gsap.com/docs/v3/Eases）。
- GSAP 名字对应的 CSS cubic-bezier 近似值取自 easings.net 源码 `src/easings.yml`（已核实；该仓库 GPL-3.0，但数值是事实，不受版权保护，我们只抄数值）：
  - out：sine (0.61,1,0.88,1)、quad (0.5,1,0.89,1)、cubic (0.33,1,0.68,1)、quart (0.25,1,0.5,1)、quint (0.22,1,0.36,1)、expo (0.16,1,0.3,1)、circ (0,0.55,0.45,1)、back (0.34,1.56,0.64,1)
  - in：cubic (0.32,0,0.67,0)、quart (0.5,0,0.75,0)、quint (0.64,0,0.78,0)、expo (0.7,0,0.84,0)
  - inOut：sine (0.37,0,0.63,1)、cubic (0.65,0,0.35,1)、quart (0.76,0,0.24,1)、quint (0.83,0,0.17,1)、expo (0.87,0,0.13,1)、circ (0.85,0,0.15,1)
- `back.out(s)` 的峰值 overshoot（推导，数值积分）：s=1.0 → 3.7%，1.2 → 5.3%，1.4 → 7.1%，1.70158（默认）→ 10%，2.2 → 15.4%。
- 弹簧阻尼比 ζ 对应的 overshoot = exp(−ζπ/√(1−ζ²))（推导）：0.9 → 0.2%，0.8 → 1.5%，0.7 → 4.6%，0.6 → 9.5%，0.5 → 16%，0.3 → 37%。HyperFrames 的分档是：0.7–0.85 显得高级，0.4–0.6 显得活泼，0.3 以下像卡通。

**After Effects ↔ CSS 换算（推导；AE 默认值已核实）**
- AE 的 Easy Ease 是两侧速度 0、影响 33.33%（Adobe 社区确认）。对一维属性，速度为 0 的关键帧把影响 i 映射成 cubic-bezier 控制点 (i, 0) 和 (1−i₂, 1)。所以：
  - Easy Ease ≈ cubic-bezier(0.333, 0, 0.667, 1)，接近 sine.inOut。
  - 两侧影响 85%（HyperFrames `text-match-cut` 逐帧量过的教程值）≈ (0.85, 0, 0.15, 1)，几乎等于 circ.inOut 或 power4.inOut。
  - 只给落点一侧 85%、出发一侧 0% ≈ (0, 0, 0.15, 1)，相当于 M3 standard decelerate 的味道。
- School of Motion、Ben Marriott、Jake Bartlett 都教「拉速度图的手柄」：影响拉到 70–90% 就是又快又稳的落地。我没找到他们写成文字的具体百分比（未核实），上面的换算可以代替。

### A2. HyperFrames 自带的实测规则（已核实，来自 `~/.claude/skills/hyperframes/references/{motion,film,captions,look}.md`，是官方发布片逐帧量出来的）

- **快速位移** 0.3–0.6 s，峰值帧带动态模糊：文字级元素 6–12 px，全屏 15–20 px，水平运动只做水平模糊。一个动作就是一个 tween。
- **慢进快出**：落地用长尾 ease-out，落地时间比离场长。退场 = 入场的 50–60%（短 40–50%）。离场是一个连贯动作，不能滑一下、停住、再走。
- **按角色选 ease**：落地用 `expo.out` / `power4.out`；镜头和颜色泛洪用 `power2.inOut`；穿越和退场用 `power3.in`。「所有东西都 power2.out 0.5 s」是 AI 味的来源。线性只用于旋转、进度条，以及「恒速本身就是重点」的情况。
- **重叠**：下一个元素在上一个完成 30–50% 时出发。**错峰**：字母 1 帧，单词 60–120 ms，列表项 40–80 ms。
- **标题落地后完全静止**，动作交给下一个元素、镜头或背景。一部片里标题入场方式要换着用：
  - 逐词 blur 6 px→0 + 透明度，每个 0.13 s，间隔 0.067 s；
  - 逐词从浅灰变成墨色；
  - 整行 blur 8 px→0，0.13–0.2 s；
  - 人名逐字母，间隔 0.1 s；
  - 文字插在主体背后；
  - 老虎机滚词，每滚 0.1 s。
- **停留**：英文 0.5 s + 每词 0.3 s；片尾最后一句 ≥ 2 s；1–2 词的章节标题可以只停 0.4 s；退场 blur + 淡出 0.13–0.25 s。
- **标题字号** 4–9% 帧高；安静的行 2.5–4%，主角词占画宽 60–90%；只有一个强调色词，而且它承载意义。
- **节奏**：蒙太奇每 0.13–0.8 s 一切；演示镜头 7–10 s 不换构图；平均镜头 1.8–3 s，镜头内部要有运动；高潮前停 0.3–0.75 s。
- **转场要有原因**：一部片 3–5 种，每种都由画面上的东西引发。HyperFrames 的规定是节拍之间的接缝最多 1/3 用硬切，硬切留给场景内推镜；两个世界之间永远不交叉溶解。
  - 与用户偏好冲突：用户 v4 定稿是约 90% 硬切加 8 个有动机的转场（见 memory `video-motion-feedback`）。**以用户为准**：场景内、句子之间用硬切，章节之间用有动机的转场。
- **配乐与命中**：要落在重音上的动作提前 40–190 ms 开始；反应动作滞后 0–45 ms；命中本身是 0 ms 的 `tl.set`，给命中加缓动就把命中做没了。
- **脚本密度**：TTS 每秒约 2.2 个英文词，一场戏约 19 词（9 s）。场景前 1/4 就把东西全摆出来然后冻住 = 幻灯片；应该在后半段跟着口播逐个揭示。
- **AI 味清单**：标题和 UI 上的呼吸、漂浮、脉冲循环；标题落地后还在滑或缩放；场景末尾慢推；UI 回弹；点击光圈；每场同一种入场；所有东西都淡入上滑。
- **视频压缩**：暗底上的全屏线性渐变在 H.264 下会出色带，改用径向渐变或纯色加局部光；5% 透明度的强调色压缩后会消失，氛围层用 15–25%，焦点元素用满饱和。

### A3. 工作室与教学者：可以迁移的手艺（基于公开作品的观察；具体参数多为未核实）

这些工作室几乎不公开数字参数，以下是能落到代码里的共性，不是引用原话。

| 来源 | 招牌 | 落到九帽动效 |
|---|---|---|
| **Buck** | 每个项目先做 style frame，再定一整套设计语言；2D 和 3D 混用；一镜只讲一个想法 | 每期先出 3–5 张风格帧（配色、字体、质感、柴犬造型），再写场景；一个风格包就是一套完整语言 |
| **ManvsMachine** | 材质和光就是高级感：触感 CG、精准的慢镜头运动、微距细节 | 卡片和数字用 light-sweep、gloss 让光扫一次；镜头用 power2.inOut 慢推，一镜一次 |
| **Ordinary Folk / Giant Ant** | 绑定骨骼动画 + 少量逐帧特效（拖影、闪光、烟），有手作质感和抖动（boil） | 柴犬身体用 GSAP 绑定，嘴、拖影、闪光用逐帧（stepped，一拍二）；手绘批注用 boil |
| **Oddfellows / Gunner / Animade** | 转场穿过物体：一个形状变成下一个场景；大胆的平面形状和字体 | 「物体变成世界」「形状 morph」型转场；章节卡用大字和色块 |
| **Kurzgesagt** | 旁白定节奏（官网原文，已核实）；2D 扁平动画结合 3D 元素（已核实）；背景里持续有星点、粒子这类环境次级运动；视差镜头；一期内配色统一（后几项是观察） | 以逐字时间戳为时间轴主干；背景层允许环境运动，**标题层禁止**；所有 AI 图过同一个 LUT |
| **Vox 解说** | 关键词手绘标注 + 细连线连到注释标签，作为一个节拍 | HyperFrames `vox-annotate` 直接可用 |
| **School of Motion / Ben Marriott / Jake Bartlett** | 迪士尼 12 原则搬到 MoGraph；核心是 Graph Editor（值图 vs 速度图），手柄拉长出长尾 | 见下方 12 原则对照表和 A1 的 AE 换算 |
| **Apple HIG** | 有目的、简短、可取消、不为动而动 | 每个非硬切转场都必须写 `why`（与用户 v4 规则一致） |

**迪士尼 12 原则 → MoGraph 代码对照**（数字是推导或惯例，未核实标出）

| 原则 | 九帽动效里的做法 |
|---|---|
| 挤压拉伸 | `scaleX × scaleY ≈ 1` 保持面积。道具 5–15%，柴犬落地可到 20–30%，持续 2–3 帧（HyperFrames `char-slam-explode` 用三帧落地） |
| 预备动作 | 大动作前反向退 5–10% 位移，3–6 帧（0.1–0.2 s）（未核实，动画惯例）。**文字和 UI 不用** |
| 舞台调度 | 一个节拍只有一个焦点；其余压暗到 40–60%，或 blur 4–8 px（参考 `focus-swap`） |
| 跟随与重叠 | 帽子、耳朵、尾巴比身体晚 2–4 帧，overshoot ≤ 5%，4–8 帧内回稳（二手教程值，未核实） |
| 慢入慢出 | 见 token 表 |
| 弧线 | 有机物体走 MotionPath 弧线（`arc-motion-path`），不走直线斜移 |
| 次级动作 | 柴犬说话时眨眼、耳朵抖、帽子歪；背景环境漂移。**标题不做** |
| 时间 | 角色和手绘层一拍二（12–15 fps 步进），镜头一拍一（未核实来源：传统动画惯例，Whitaker & Halas《Timing for Animation》讨论过「Ones or Twos」） |
| 夸张 | 主数字落地 scale 1.15→1；两帧色闪 |
| 立体造型 | 所有层光源方向一致，投影方向一致 |
| 吸引力 | 形状语言和配色统一；柴犬造型锁定 |

### A4. 和口播对时（核心规则）

1. **感知落点是 90% 进度，不是 tween 结束**（推导，按 ease 公式精确计算）：
   - 到达 90% 的时刻占总时长的比例 p90：`expo.out` 0.33、`power4.out` 0.37、`power3.out` 0.44、`power2.out` 0.54、`power1.out` 0.68、`sine.out` 0.71。
   - 所以 tween 开始时间 = 词起点 − p90 × 时长 − 提前量。
2. **提前量取 2 帧（30 fps 下约 67 ms）**。依据是 ITU-R BT.1359 的不对称容忍：声音比画面早 45 ms 以上就能被察觉，声音比画面晚 125 ms 以内察觉不到（容忍阈 +90 / −185 ms）（已核实：ITU 原文与多处二手来源一致，二手来源正负号约定不一）。结论是**画面宁早勿晚**，早 2–3 帧最安全。这与 HyperFrames「提前 40–190 ms」一致。
3. **硬切和命中**：落在词起点或提前 0–2 帧，用 `tl.set`，不加缓动。
4. **反应动作**（柴犬点头、惊讶）：词后 0–1 帧（0–45 ms）。
5. **蒙太奇切在名词起点**（用户 v4 规则：montages cut on spoken nouns）。中文 ASR 返回整句时，按字数平分时长再人工校对（HyperFrames captions.md）。
6. **时间轴结构**：用 Motion Canvas `waitUntil('事件')` 的思路，场景里写 `at:"关键词"`，由逐字时间戳解析出时间。HyperFrames `beat-timeline` 是同样的思路：把节拍行钉在命名标签上。

### A5. 屏幕文字的停留时间（中文）

| 数据 | 值 | 状态 |
|---|---|---|
| Netflix 简体中文字幕 | 成人 ≤ 9 字/秒，儿童 ≤ 7 字/秒；SDH 成人 11 字/秒；每行 ≤ 16 字（SDH 可到 18） | 已核实 |
| Netflix 字幕时序 | 最短 20 帧（约 0.8 s）；两条之间至少 2 帧；间隔要么正好 2 帧，要么 ≥ 0.5 s；入点在音频起点或 1–2 帧内；后面没有字幕时出点 ≥ 音频结束后 0.5 s；屏幕文字淡入淡出时，入出点取在淡变的一半 | 已核实 |
| 中文连续文本默读 | IReST 等研究：约 255–295 字/分（4.3–4.9 字/秒）；RSVP 最大速度 259.5 ± 38.2 字/分；年轻正常读者最大速度 273 ± 34 字/分 | 区间已核实；255 这个具体数出自二手博客，未核实 |
| HyperFrames 英文规则 | 0.5 s + 每词 0.3 s | 已核实 |

**九帽动效的读时公式**（推导：介于默读 ~4.5 字/秒和字幕上限 9 字/秒之间；画面上还有别的东西在抢注意力，取约 6 字/秒）：
- **口播里没念的字**（标签、来源、补充说明）：`T = max(1.0, 0.5 + n/6)` 秒，n 是汉字数（数字和英文单词各算 1 个）。例：12 字 → 2.5 s。
- **口播里念到的关键词或标题**：入点 = 词起点 − 2 帧；出点 ≥ 这个短语结束 + 0.3 s；至少 0.8 s。
- **字幕条**：≤ 9 字/秒，≤ 16 字/行，最短 0.8 s，间隔 ≥ 2 帧。
- **章节短标题**（≤ 4 字）≥ 0.6 s；片尾一句 ≥ 2 s；数字滚动 1.2–1.6 s 后再停 ≥ 1 s。
- **一屏字数**：动效标题每屏 4–12 个汉字（HyperFrames film.md）；超出就分屏或换场景，不要缩小字号（MotionGit 规范同理）。

### A6. 让 2D 显得高级

- **景深分层**：3–5 层。视差速度按 1/z 关系分配：远景 0.2–0.4×，中景 1×，前景 1.3–2× 镜头位移（推导）。远近两层加 2–8 px 模糊（未核实，经验值）。前景物体可以部分出画。AI 图先抠出主体和前景，变成 2.5D（media-use `remove-background`）。
- **动态模糊**：电影标准快门 180°（惯例）；HyperFrames `extended-keyframe` 默认 240°、每帧 32 个采样（已核实，源码）。只给快速移动的元素加。根节点开 `data-motion-blur="on"` 就是渲染时的真模糊。
- **次级运动**：放在角色和背景上，标题和 UI 落地后静止。
- **质感**：
  - 颗粒每帧换 seed（要一拍二的感觉就每 2 帧换一次）。
  - 纸纹用 `multiply` 叠。
  - 颗粒的尺寸和透明度要能扛住 H.264：粒径 1–2 px、透明度 6–12%（推导：HyperFrames 实测 5% 会被压掉，未核实具体阈值）。
- **光**：每个主角元素让光扫过一次（`light-sweep-pass`、`gloss-sweep`）；暗角 15–25%。
- **调色一致**：整期一个 LUT（film-look 技能导出 `.cube`，或者 HyperFrames WebGL grade）。所有 AI 图、B-roll、动效层吃同一个 LUT、同一层颗粒、同一个暗角。配色控制在底色、墨色、强调色加两个辅助色。
- **时间质感**：手绘层和柴犬嘴型一拍二（`stop-motion-cadence`：`floor(t·fps)/fps`）；手绘线条用 boil，每 2–3 帧换一次姿态（`hw-boil`）。

### A7. 动态字体（kinetic type）规则

- **行遮罩揭示**：每行外包一层 `overflow: clip`。行从 yPercent 110 → 0，用 `expo.out`，0.6–0.8 s，行间错峰 0.1 s。GSAP SplitText 的 `mask:"lines"`（v3.13+）、`autoSplit` + `onSplit` 是官方做法（已核实，gsap.com 文档；社区范例 yPercent 110、stagger 0.1、expo.out）。
  - 中文注意：遮罩层底部留 0.1 em，否则数字和拉丁字母的下伸部会被裁掉。
- **字距动画**：letter-spacing 从 0.5 em 收到 0.02–0.08 em，0.8–1.0 s，`power3.out`；透明度在前 40% 完成（HyperFrames `tracking-in`）。
- **字号反差**：主角词是正文的 3–5 倍；或者按 HyperFrames 的比例，安静行 2.5–4% 帧高，主角词占 60–90% 画宽。双字体做强调（`caption-editorial-emphasis`）。
- **只有一个强调色词**；字重变化可以用可变字体的 wght 轴（`weight-wave`、`variable-axis-type`；思源黑体有 VF 版本，OFL 许可）。
- **中文切分**：
  - 用浏览器内置的 `Intl.Segmenter('zh', {granularity:'word'})` 按词切，Chromium 自带，结果确定，渲染器里可以直接用。
  - ≤ 12 字可以逐字，间隔 1 帧；更长就逐词，间隔 0.07–0.1 s。
  - 断行用 `text-wrap: balance`（或 Active Theory 的 `balance-text`，MIT）加 `line-break: strict`，避免标点出现在行首、一个字孤零零占一行。
- **换句**：用 `line-swap`（旧行从遮罩里向上出、新行从下进，同一拍），或 `kinetic-type-swap`（句子不动，只滚一个词槽，词槽宽度预设成最宽的候选，句子不会重排）。
- **退场**：逐词 blur + 淡出 0.13–0.25 s，或者跟着场景的动作一起走。不要每个标题都淡出上滑。

---

## B. 可借用的开源动效代码

### B1. HyperFrames 注册表（本机 0.8.191）

- 用 `catalog --json` 拿到 448 项：block 210 个，component 238 个。catalog JSON **没有逐项的 license 字段**。
- 仓库 `heygen-com/hyperframes` 许可是 **Apache-2.0**（`gh api` 已核实；npm 包 `hyperframes@0.8.191` 的 license 字段也是 Apache-2.0）。注册表源码在仓库的 `registry/` 目录，`hyperframes add` 从 raw.githubusercontent 拉取。
- **注册表里混有第三方授权**（扫描仓库树、读了 NOTICE 文件，已核实）：
  - 36 个 WebGPU shader block 自带 `shaders.THIRD-PARTY-LICENSES.txt`：shaders 4.0.0，MIT，© Shader Effects Inc.
  - 4 个 block 打包了 GSAP 3.14.2，附 `GSAP-NOTICE.txt`（GSAP Standard License，非 OSI 许可）。
  - 4 个 block 用 Three.js（MIT）；另有 Clipper、opentype.js、three-mesh-bvh 的许可文件。
  - 字体是 Inter、EB Garamond、Archivo（OFL）。
  - 标签 `transitions-dev-port` 的 16 项写着「transitions.dev-inspired」。上游 transitions.dev 是**自定义许可**：可以商用、可以改，但**不能把这套转场库本身当竞品再分发**（已核实上游 LICENSE）。所以这 16 项的成片随便用，**不要原样打包进九帽技能**（谨慎做法，未核实 HyperFrames 是否已经重写干净）。
  - 标签 `remocn-port` 的项来自 Remocn（MIT）。
- **质量提醒**：注册表自己的 `component-quality-bar.md` 写着「213 个新组件里有 97 个没有自己的 timeline」。所以 `add` 之后要先单独 `snapshot` 一遍，别以为 catalog 页面能动就代表装下来能动。

**最适合口播讲解的约 25 个条目**（名字已与 catalog 逐一核对存在）

| # | 名称 | 类型 | 做什么 / 为什么值得用 |
|---|---|---|---|
| 1 | `per-word-rise` | c | 逐词或逐字 blur→清晰上升，落地后真正静止。**`cues` 参数填的是每个词的落地时间**，可以直接喂口播时间戳 |
| 2 | `line-swap` | c | 整行换句：A 从遮罩向上出，B 从下进，同一拍完成，可以给一个词画下划线 |
| 3 | `kinetic-type-swap` | c | 句子固定，只有一个词槽滚动换词。词槽预设为最宽候选的宽度，不重排；`cues` 可对口播 |
| 4 | `text-match-cut` / `type-match-cut` | c | 文字到文字的匹配剪辑：两段共用一条 85% easy-ease，在速度峰值硬切；标题被劈开，新面板从字缝里长出来 |
| 5 | `vox-annotate`（吸收了 `marker-highlight`） | c | Vox 式标注：关键词手绘高亮、圈、下划线或涂抹，同时一根细线连到等宽字体标签，作为一个节拍 |
| 6 | `hw-underline` / `hw-callout-circle` / `hw-arrow` / `hw-boil` | c | 手绘批注家族：抖动线条、带动量的标签、种子化 boil，可 seek |
| 7 | `caption-editorial-emphasis` / `caption-camera-follow` | c | 双字体加巨大字号反差的强调字幕；一句话写在比画面大得多的世界里，镜头匀速后拉 |
| 8 | `cut-the-curve` | c | 速度匹配的方向硬切：出场 `power4.in`，峰值换身份，入场 `power4.out`；接缝共用 12 px 模糊 |
| 9 | `whip-pan-cut` | c | 整屏甩镜，0.55 s `power3.inOut`；两场景在一条连续条带上，接缝速度天然相等；有封顶的方向模糊 |
| 10 | `iris-reveal` | c | 从有动机的点开圆形 clip-path；前态压暗去饱和，后态全彩 |
| 11 | `halftone-dissolve` | c | 半调网点从小到大打开窗口，A 溶到 B。适合报纸、印刷风 |
| 12 | `ink-bleed-reveal` | c | 墨水在纸上洇开（gooey：feGaussianBlur + feColorMatrix 阈值）再收缩，露出 logo 或图 |
| 13 | `torn-paper-rip` / `paper-collage-reveal` | c | 撕纸露出白芯后揭走；拼贴纸片错峰飞散 |
| 14 | `camera-rig-depth-stack` / `focus-rack` / `pull-back-reveal` | c | 景深卡片堆、两层之间拉焦、从细节后拉揭示全貌。AI 图做 2.5D 的现成镜头 |
| 15 | `scroll-camera-story` | c | 长画卷强制滚动，各层视差，最后减速停在终点段。适合时间线、流程 |
| 16 | `camera-shake` | c | 9 种实测手持、长焦、绑定机位的抖动配置，闭式公式，可 seek。配合 slam |
| 17 | `motion-blur` / `extended-keyframe` / `echo-smear` | c | AE 式快门积分模糊；「永不完全落地」的长尾 ease（87% 位移在前 20% 时长完成）；按速度拖影 |
| 18 | `light-sweep-pass` / `gloss-sweep` / `text-shimmer` | c | 一道主光扫过，场景里每个元素的高光和阴影同步移动；卡片落地吃一次镜面光 |
| 19 | `chart-story` / `mk-line-graph` / `bar-chart-race` | c/b | 按阅读顺序生长的图表，数值标签跟着绘制前沿走，强调值单独标出 |
| 20 | `count-up` / `number-wheel` / `slot-machine-roll` | c | 数字滚动、滚轮、老虎机 |
| 21 | `world-map` / `nyc-paris-flight` / `north-korea-locked-down` | b | 地图类：地区等值图、飞行路线、真实地图推近 + 红圈 + 编辑风染色 |
| 22 | `constellation-hub` / `radial-surround` / `exploded-stack` | c/b | 概念图：中心节点按口播顺序点亮、标签围成一圈再收拢、分层爆炸图 |
| 23 | `before-after-wipe` / `comparison-split` / `split-tilt-cards` | c | 对比三件套 |
| 24 | `grain-overlay` / `vignette` / `organic-light-leak-overlay` / `editorial-flash-overlay` | c/b | 质感和光的常驻层，以及有动机的闪光、漏光转场 |
| 25 | `stop-motion-cadence` | c | 步进时间法则加种子 boil，给柴犬和手绘层用 |
| 26 | `lottie-character-walk` | b | 关节式扁平角色：Lottie 负责表演，GSAP 负责舞台。柴犬表演的参考结构 |
| 27 | `domain-warp-dissolve` / `light-leak` / `whip-pan` / `cross-warp-morph` | b | shader 转场（WebGL），作为偶尔使用的大转场 |
| 28 | `cinemagraph` / `grade-split-reveal` / `yt-feather-highlight` | b/c | 静图里只有一块区域在动；平调和成品调色的对比揭示；羽化聚光灯在目标之间滑动 |
| 29 | `beat-timeline` | c | 暂停态的主时间轴骨架，节拍钉在命名标签上。对时架构可以参考 |

（c = component，b = block。搜过的 query：kinetic type、transition、grain、paper、editorial、3d card、caption、chart、map、mask reveal、parallax、motion blur、camera、ink、halftone。）

### B2. 外部来源：许可与值得移植的技法

| 来源 | 许可（核实方式） | 值得移植的 1–2 个技法 |
|---|---|---|
| **Codrops / Tympanus**（github.com/codrops，351 个仓库） | **分两种**（`gh api` 逐仓查过）：131 个带 MIT LICENSE；220 个没有 LICENSE 文件，README 写的是旧版 Codrops 许可：「可以集成或改造后用于个人或商业项目……**不能原样出售、再分发、再发布，也不能卖插件化版本**」。Codrops 现在的许可页（403 抓不到，以搜索摘要为准）说可下载的 demo 默认 MIT，但**以各仓库为准** | **MIT 的可以搬**：`LayersAnimation`（多层 polygon clip-path 层叠擦除，`power3.inOut` 1.4 s，层间 stagger，然后 `expo`/`power4` 揭示）；`KineticTypePageTransition`（多行重复大字整体 scale 2.7 + rotate −90°，`power2.inOut` 1.4 s，行与行 x 方向错位 stagger 0.04，`back` 回位）；`TextBlockTransitions`（逐词 yPercent 30 + 透明度，0.8 s，stagger）；`SlicedTextEffect`；`OnScrollSVGFilterText`（HTML 文字上叠 feTurbulence/feDisplacementMap）；`PixelTransition`；`ShapesSlideshow`；`TypeShuffleAnimation`（LCD 洗牌字）。**旧许可的只学思路、自己重写**：`LiquidDistortion`（PixiJS 位移贴图幻灯）、`CSSGlitchEffect`（clip-path 切片故障）、`CreativeGooeyEffects`、`SliceRevealer`/`BlockRevealers`/`RotatedRevealers`（色块揭示）、`MorphingPageTransition`。原因：九帽技能以后要分发，原样带进去会碰「再分发」条款 |
| **GSAP 官方 CodePen** | CodePen 规定公开 Pen 一律 MIT（已核实，blog.codepen.io/docs/licensing）；但 GSAP 库本身是 GSAP Standard License（免费、可商用、全部插件免费，非 OSI；禁止拿来做和 Webflow 竞争的无代码动画搭建器） | SplitText `mask:"lines"` 行遮罩；`Flip`（建时间轴时测量一次两个布局，生成可 seek 的 tween，做「卡片变全屏」）；MorphSVG 做图标变形；CustomEase 写 AE 曲线，例如 `"M0,0 C0.05,0.7 0.1,1 1,1"`；CustomWiggle 做确定性抖动。**GSAP 走 CDN，不随包分发**（与 SOURCES.md 一致） |
| **Motion Canvas**（motion-canvas/motion-canvas，examples 仓库同样 MIT） | MIT（已核实） | `waitUntil('事件')` 命名时间点，在编辑器里拖动对齐口播 → 我们的 `at:"关键词"`；`all / chain / sequence` 组合子；代码块 diff 变形；Layout 自动布局过渡 |
| **gl-transitions**（125 个 GLSL 转场） | 仓库 MIT。LICENSE 写明单个文件可以在头注释里另定许可：**123 个头注 MIT，`InvertedPageCurl` 是 BSD-3，`StereoViewer` 是 BSD-2**（逐个文件 grep 过，已核实） | `LumaWipe`（按灰度图擦除 → 用我们自己画的墨迹、纸边、笔刷灰度图做转场）；`DisplacementMap`（位移贴图交叉溶解，源自 Codrops Robin Delaporte 的文章）；`TangentMotionBlur`、`DirectionalWarp`、`CrossZoom`、`PerlinDissolve`、`FilmBurn`、`InvertedPageCurl`（翻页） |
| **anime.js**（juliangarnier/anime） | MIT（已核实） | `stagger(v, {grid:[c,r], from:'center'})` 按距离错峰（HyperFrames `stagger-lattice` 已经用 GSAP 实现）；`createSpring({mass, stiffness, damping})` 闭式弹簧；SVG 描线 / morph。v4 是否内置 splitText 未核实 |
| **Lusion** | `lusionltd/WebGL-Scroll-Sync` MIT；另一个公开仓库 ORYZO-1 与动效无关。官网那些效果**没有开源**（只有第三方逆向克隆，不碰） | DOM 和 WebGL 同步的思路（我们是逐帧渲染，用处有限） |
| **Active Theory** | 自家框架 Hydra 没有开源（与 AGPL 的 hydra-synth 是两回事，后者别碰）。公开 MIT 仓库：`split-text`、`balance-text`、`fit-text`、`activeframe` | `balance-text`：让多行均匀分布，治中文标题末行孤字；`split-text`：行、词、字切分；`activeframe`：基于 WebCodecs 的逐帧精确视频格式（HyperFrames 视频 seek 出问题时可以参考） |
| **awesome 列表** | `sergey-pimenov/awesome-web-animation` CC0；`lucasmaiaesilva/awesome-motion-design-web` 无许可，2015 年后停更。**没找到 "awesome-gsap"** | 只是索引，用来找库，没有可以直接搬的代码 |
| **paper-design/shaders** | Apache-2.0（读过 LICENSE 原文，已核实） | 现成的 `halftone-dots`、`halftone-cmyk`、`paper-texture`、`grain-gradient`、`fluted-glass`、`image-dithering`、`god-rays`、`liquid-metal`。**半调和纸张材质层的首选来源** |
| **pixijs/filters** | MIT（已核实） | 可以照着改写成 WebGL/CSS 的滤镜：`old-film`、`crt`、`dot`（半调）、`motion-blur`、`zoom-blur`、`rgb-split`、`glitch`、`shockwave`、`godray`、`tilt-shift`、`ascii`、`cross-hatch` |
| **mattdesl/glsl-film-grain**、**stegu/webgl-noise**、**ashima/webgl-noise** | 均 MIT（已核实） | 自然的胶片颗粒；simplex 和 cellular 噪声（墨迹、纸纤维、domain warp） |
| **robin-dela/hover-effect** | MIT（已核实） | 位移贴图两图过渡，Codrops DistortionHoverEffect 的库化版本 |
| **Splitting.js** | MIT（已核实） | 切分后注入 `--char-index` / `--word-index` / `--line-index` CSS 变量，可以做纯 CSS 错峰 |
| **motion.dev**、**Remocn**、**Theatre.js core**、**d3** | MIT、MIT、Apache-2.0、ISC（已核实） | 弹簧只用 `visualDuration + bounce` 两个参数；Remocn 的转场和场景思路（不要连带 Remotion 运行时，Remotion 不是开源许可）；Theatre 把关键帧存成 JSON；d3 的插值和对象恒定 |
| **⚠️ 不要搬代码的** | LYGIA = Prosperity 3.0（非商用，商用只能试 30 天）；react-bits = MIT + Commons Clause（禁止再分发组件本身）；hydra-synth = AGPL-3.0；pmndrs/postprocessing = Zlib（宽松，但不在 MIT/Apache/BSD/ISC 名单里，要用先问用户）；Remotion = 自定义许可；transitions.dev = 自定义许可（禁止作为竞品库再分发） | 只看思路 |

---

## C. 九帽动效默认动效 token

时长按 30 fps 换算帧数；60 fps 时帧数翻倍。

### C1. 缓动

| token | 用途 | cubic-bezier | GSAP 写法 | 来源 |
|---|---|---|---|---|
| `arrive` | 主体入场、标题落地（默认） | (0.16, 1, 0.3, 1) | `expo.out` | HyperFrames motion.md；easings.net |
| `arrive-soft` | 卡片、图片入场 | (0.22, 1, 0.36, 1) | `power4.out` | 同上 |
| `arrive-calm` | 安静章节、长距离入场 | (0.25, 1, 0.5, 1) | `power3.out` | 同上 |
| `emph-decel` | 想要 M3 那种「冲进来急刹」的入场 | (0.05, 0.7, 0.1, 1) | `CustomEase "M0,0 C0.05,0.7 0.1,1 1,1"` | M3 |
| `exit` | 普通退场 | (0.32, 0, 0.67, 0) | `power2.in` | HyperFrames |
| `exit-fast` | 穿越、zoom-through、甩出 | (0.5, 0, 0.75, 0) | `power3.in` | HyperFrames |
| `cut-out` / `cut-in` | 速度匹配剪辑的前半 / 后半 | (0.64, 0, 0.78, 0) / (0.22, 1, 0.36, 1) | `power4.in` / `power4.out` | HyperFrames `cut-the-curve` |
| `move` | 镜头推拉、重排、颜色泛洪 | (0.65, 0, 0.35, 1) | `power2.inOut` | HyperFrames |
| `whip` | 甩镜 | (0.76, 0, 0.24, 1) | `power3.inOut` | HyperFrames `whip-pan-cut` |
| `match` | 文字匹配剪辑（AE 85% 影响） | (0.85, 0, 0.15, 1) | `CustomEase "M0,0 C0.85,0 0.15,1 1,1"`（≈ `circ.inOut`） | HyperFrames `text-match-cut` + 推导 |
| `draw` | 描线、柱子生长、进度 | (0.37, 0, 0.63, 1) | `sine.inOut` | easings.net |
| `pop` | 小徽章、图标弹出（overshoot 7%） | 约 (0.34, 1.4, 0.64, 1)（未核实的近似） | `back.out(1.4)` | HyperFrames + 推导 |
| `spring` | 高级感位置回弹（ζ 0.8，overshoot 1.5%） | — | 闭式弹簧 ζ=0.8、k=380，或 `elastic.out(1,0.75)` 近似（未核实） | M3 Expressive default |
| `spring-play` | 柴犬、道具的活泼回弹（ζ 0.6，overshoot 9.5%） | — | 闭式弹簧 ζ=0.6、k=800，或 `elastic.out(1,0.5)` | M3 Expressive fast；HyperFrames |
| `trail` | 「永不完全落地」的长尾 | 自定义：前 20% 时长走完 87% 位移 | `EK.ease()` | HyperFrames `extended-keyframe` |
| `linear` | 旋转、进度条、恒速漂移 | (0, 0, 1, 1) | `none` | — |
| `hit` | 音乐或口播命中 | — | `tl.set`（0 ms） | HyperFrames film.md |

两条铁律：透明度和颜色**永远不回弹**（M3 effects 弹簧 ζ=1）；只有位置和尺寸可以弹。

### C2. 时长

| token | 秒 | 帧 @30 | 用途 |
|---|---|---|---|
| `flash` | 0.067–0.1 | 2–3 | 闪白；dip cut 前压暗 40% 3 帧 |
| `micro` | 0.2 | 6 | 图标、徽章、勾 |
| `word` | 0.13–0.35 | 4–10 | 单个词或字入场（blur-in 风格取 0.13–0.2） |
| `card` | 0.55 | 16–17 | 卡片、面板、图片入场 |
| `line` | 0.7 | 21 | 行遮罩揭示 |
| `move` | 0.9 | 27 | 镜头推拉、版式重排 |
| `transition` | 0.4–0.65 | 12–20 | 有动机的转场：iris 0.15–0.4，zoom-through 0.35，物体变世界 0.65，颜色泛洪 0.4 |
| `whip` | 0.55（拖影段 0.13–0.3） | 16–17 | 甩镜 |
| `count` | 1.2–1.6 | 36–48 | 数字滚动 |
| `exit` | 入场 × 0.5–0.6（0.15–0.35） | 5–10 | 退场 |
| `ambient` | 整个镜头 | — | AI 图慢推 scale 1.0→1.08；背景轨道每秒 3–5° |

**距离修正**（推导，符合 M1「距离越大越长」和 Carbon「非线性刻度」，并落在 HyperFrames 实测的 0.3–0.6 s 快动作区间里）：
`dur = 0.3 + 0.35 × √(d / 1920)` 秒，d 是 1080p 下的位移像素；缩放类取 d = |Δscale| × 元素对角线。
算例：100 px → 0.38 s，480 px → 0.48 s，960 px → 0.55 s，1920 px → 0.65 s。

### C3. 错峰与重叠

| 单位 | stagger |
|---|---|
| 汉字逐字（≤ 12 字） | 1 帧（0.033 s） |
| 词（`Intl.Segmenter` 切出来的） | 0.07–0.1 s |
| 行 | 0.1 s |
| 列表项 | 0.06 s（40–80 ms） |
| 网格卡片 | 0.05 s，`from:'center'` 或 `'start'` |

- **总展开上限 0.6 s**：`stagger = min(base, 0.6 / (n − 1))`。
- **重叠**：下一个元素在上一个完成 30–50% 时开始。

### C4. 读时与对时公式

```
口播没念的字:  T_hold = max(1.0, 0.5 + n_chars / 6)            # 秒，约 6 字/秒
口播念到的字:  t_in = t_word − 2f ;  t_out ≥ t_phrase_end + 0.3 ;  T ≥ 0.8
字幕条:        ≤ 9 字/秒，≤ 16 字/行，T ≥ 0.8 s，间隔 ≥ 2 帧    # Netflix 简中
章节短标题:    ≥ 0.6 s ；片尾一句 ≥ 2 s ；数字滚完再停 ≥ 1 s
动作对口播:    t_start = t_word − p90(ease) × dur − 2f
               p90: expo.out .33 | power4.out .37 | power3.out .44 | power2.out .54
硬切 / 命中:   t_word − (0…2f)，tl.set
反应动作:      t_word + (0…1f)
容忍度:        画面早于声音 ≤ 125 ms 察觉不到；晚于声音 > 45 ms 会被察觉 (ITU-R BT.1359)
```

---

## D. 最值得先做的 15 个技法（按收益排序）

| # | 技法 | 为什么排在这里 | 来源与许可 |
|---|---|---|---|
| 1 | **口播锚定调度器**：`at:"关键词"` → 逐字时间戳 → `t_start = t_word − p90×dur − 2f`；硬切和命中用 `tl.set` | 一切动效对不上口播就显得廉价。这是全局基础设施 | 自研；思路来自 Motion Canvas `waitUntil`（MIT）、HyperFrames film.md 和 `beat-timeline`（Apache-2.0）；ITU-R BT.1359（只用数字） |
| 2 | **中文行遮罩和逐词字效**：`Intl.Segmenter` 切词，加 overflow-clip 行遮罩、yPercent 110→0、`expo.out` 0.7 s、stagger 0.1；`balance-text` 防孤字 | 口播讲解八成画面是字 | GSAP SplitText（GSAP Standard License，走 CDN）或自写切分；Splitting.js、activetheory/split-text、balance-text（MIT）；HyperFrames `per-word-rise`、`line-swap`（Apache-2.0） |
| 3 | **速度匹配剪辑三件套**：方向硬切、甩镜、文字匹配剪辑 | 用户要硬切为主，但不能「像幻灯片」；在速度峰值切，接缝就看不出来 | HyperFrames `cut-the-curve`、`whip-pan-cut`、`text-match-cut`、`type-match-cut`（Apache-2.0） |
| 4 | **关键词手绘标注**：高亮、圈、下划线、涂抹，加连线和标签，作为一个节拍；手绘线条 boil | 讲解类最有效的强调手段，而且自带手作质感 | HyperFrames `vox-annotate`、`hw-*`（Apache-2.0） |
| 5 | **AI 图 2.5D 景深**：抠出 3–5 层，视差 0.3×/1×/1.6×，远近层加模糊，加拉焦、后拉揭示 | AI 静图从「贴图」变成「镜头」，用户最反感静态 | HyperFrames `camera-rig-depth-stack`、`focus-rack`、`pull-back-reveal`、`scroll-camera-story`（Apache-2.0）；media-use 抠图 |
| 6 | **快门动态模糊加长尾落地**（240°，只给快速移动的元素） | 一个参数就把 2D 的 CSS 味变成胶片感 | HyperFrames `data-motion-blur`、`motion-blur`、`extended-keyframe`（Apache-2.0）；gl-transitions `TangentMotionBlur`（MIT） |
| 7 | **整期统一材质层**：同一个 LUT 加颗粒（每帧或每 2 帧换 seed）加纸纹 multiply 加暗角 | 把 AI 图、B-roll、动效粘成一部片，是「调色一致」的落地办法 | paper-design/shaders `grain-gradient`、`paper-texture`（Apache-2.0）；mattdesl/glsl-film-grain（MIT）；HyperFrames `grain-overlay`、`vignette`（Apache-2.0）；film-look 技能 LUT |
| 8 | **灰度图驱动的有机转场**：LumaWipe 和 DisplacementMap，配自制的墨迹、纸边、笔刷灰度图 | 转场带上风格包的气质，每个风格一种招牌转场 | gl-transitions `LumaWipe`、`DisplacementMap`（MIT）；robin-dela/hover-effect（MIT） |
| 9 | **墨水洇开和 gooey 揭示** | 中文、水墨、纸面风格的标志性揭示 | HyperFrames `ink-bleed-reveal`（Apache-2.0）；Codrops `GooeyTextHoverEffect`（MIT）；Lucas Bebber 的 gooey 原理（旧版 Codrops 许可 → 自己重写） |
| 10 | **柴犬一拍二表演**：嘴型跟着口播振幅包络步进到 12 fps，眨眼和耳朵做次级动作（晚 2–4 帧），落地挤压 2–3 帧 | 吉祥物是频道的识别符号；一拍二让它像手作动画而不是 PPT | HyperFrames `stop-motion-cadence`、`hw-boil`、`lottie-character-walk`（Apache-2.0）；迪士尼原则；振幅包络用 ffmpeg 自研 |
| 11 | **半调和网点溶解**（印刷、报纸风） | 商业分析和新闻语境很合适，质感强 | HyperFrames `halftone-dissolve`（Apache-2.0）；paper-design/shaders `halftone-dots`、`halftone-cmyk`（Apache-2.0）；pixi `dot`（MIT） |
| 12 | **多层 clip-path 层叠擦除和色块揭示**（章节转场） | 便宜、确定、可 seek，但看起来很贵 | Codrops `LayersAnimation`（MIT，参数：`power3.inOut` 1.4 s + stagger） |
| 13 | **主光扫过和镜面光**（卡片、数字、logo 落地后扫一次，然后静止） | ManvsMachine 式「材质即高级」，几乎零成本 | HyperFrames `light-sweep-pass`、`gloss-sweep`、`text-shimmer`（Apache-2.0） |
| 14 | **数据叙事组件**：图表按阅读顺序生长，数字滚动，强调值标注，地图推近加红圈 | 商业分析和 AI 赚钱题材离不开数字 | HyperFrames `chart-story`、`count-up`、`number-wheel`、`world-map`、`north-korea-locked-down`（Apache-2.0）；d3（ISC） |
| 15 | **撕纸、拼贴、翻页转场** | 纸面风格包的招牌；翻页适合「下一章」 | HyperFrames `torn-paper-rip`、`paper-collage-reveal`（Apache-2.0）；gl-transitions `InvertedPageCurl`（BSD-3） |

**落地顺序建议**：先做 1、2、3、6、7。这五个是所有风格共用的地基，做完任何一个风格都会立刻上一个档次。4、5、10 是讲解频道的灵魂。8、9、11、12、15 按风格包挑一两个做招牌转场，**不要全塞进一期**（与用户 v3、v4 的反馈一致：转场要有动机，不是越多越好）。

---

## 来源

- HyperFrames：`~/.claude/skills/hyperframes/references/{motion,look,captions,film}.md`；`~/.claude/skills/hyperframes-registry/references/component-quality-bar.md`；本机 `npx hyperframes@0.8.191 catalog --json`（结果在 `/private/tmp/claude-501/-Users-dai-Desktop-test/37d533ff-1774-40ae-8712-7cadfc7a24c2/scratchpad/hfcat/catalog.json`）；https://github.com/heygen-com/hyperframes （Apache-2.0；registry 下的 THIRD-PARTY-LICENSES 和 GSAP-NOTICE）
- Material 3 源码：https://github.com/androidx/androidx/tree/androidx-main/compose/material3/material3/src/commonMain/kotlin/androidx/compose/material3/tokens （MotionTokens.kt、StandardMotionTokens.kt、ExpressiveMotionTokens.kt）
- Material 1：https://m1.material.io/motion/duration-easing.html
- IBM Carbon：https://carbondesignsystem.com/elements/motion/overview/
- Apple HIG Motion：https://developer.apple.com/design/human-interface-guidelines/motion ；WWDC23 Animate with springs：https://developer.apple.com/videos/play/wwdc2023/10158/ 、https://wwdcnotes.com/notes/wwdc23/10158
- GSAP Eases：https://gsap.com/docs/v3/Eases/ ；SplitText：https://gsap.com/docs/v3/Plugins/SplitText/ ；GSAP Standard License：https://gsap.com/standard-license
- easings.net 数值：https://github.com/ai/easings.net/blob/master/src/easings.yml
- Netflix 简中字幕：https://partnerhelp.netflixstudios.com/hc/en-us/articles/215986007-Simplified-Chinese-Timed-Text-Style-Guide ；字幕时序：https://partnerhelp.netflixstudios.com/hc/en-us/articles/360051554394-Timed-Text-Style-Guide-Subtitle-Timing-Guidelines
- 中文阅读速度：https://pmc.ncbi.nlm.nih.gov/articles/PMC6456801/ ；IReST：https://avesis.kocaeli.edu.tr/yayin/23e6bda7-d1eb-4148-9188-ab34aa4fc2be/standardized-assessment-of-reading-performance-the-new-international-reading-speed-texts-irest
- ITU-R BT.1359：https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-1-199811-I!!PDF-E.pdf ；https://en.wikipedia.org/wiki/Audio-to-video_synchronization
- AE Easy Ease 33.33%：https://creativecow.net/?p=156140
- Kurzgesagt 流程：https://kurzgesagt.org/youtube/
- Codrops：https://github.com/codrops （逐仓库 license）；旧版许可原文见 https://github.com/codrops/LiquidDistortion
- CodePen 许可：https://blog.codepen.io/docs/licensing/
- gl-transitions：https://github.com/gl-transitions/gl-transitions （LICENSE 加 transitions/ 头注释）
- Motion Canvas：https://github.com/motion-canvas/motion-canvas ；anime.js：https://github.com/juliangarnier/anime
- paper-design/shaders：https://github.com/paper-design/shaders ；pixi filters：https://github.com/pixijs/filters
- Active Theory：https://github.com/activetheory ；Lusion：https://github.com/lusionltd
- transitions.dev 许可：https://github.com/Jakubantalik/transitions.dev ；Remocn：https://github.com/Remocn/remocn
- LYGIA：https://github.com/patriciogonzalezvivo/lygia ；react-bits：https://github.com/DavidHDev/react-bits
- awesome-web-animation：https://github.com/sergey-pimenov/awesome-web-animation
