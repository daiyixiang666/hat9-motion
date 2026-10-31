# 调研：After Effects 最受欢迎的动效，按真实数据排名（2026-10-31）

服务对象：九帽动效（hat9-motion），HTML + CSS + GSAP（+ SVG / WebGL），由 HyperFrames 逐帧渲染成 MP4，横屏 16:9 和竖屏 9:16 都要。
目标：不自己发明动效，**照着已经被市场验证过的 AE 动效来做**。每一条都要有人气数据，不靠个人口味。

---

## 0. 口径与写法约定

| 来源 | 人气指标 | 怎么取的 | 局限 |
|---|---|---|---|
| VideoHive（Envato Market） | 累计**销量**（Sales） | 各 AE 分类按 `?sort=sales` 抓第 1 页（30 条） | 销量是上架以来的累计数，老模板占便宜；页面上没有动效说明 |
| Envato Elements | 「Popular」排序的**名次**（不公开下载量） | AE 总表 + Titles / Elements / Infographics 分类第 1 页 | 只能看名次，看不到数量；但代表的是**当下（2026）**的需求 |
| Mister Horse（Animation Composer） | 官方用户数、评分、预设数量 | misterhorse.com 产品页 | 官方自己报的数 |
| Motion Bro（Videolancer） | 官方称的下载量 | 搜索摘要（页面本身返回 403，没能直接读） | 官方自己报的数 |
| Motion Array | — | 页面返回 **403**（Cloudflare），没拿到 | **缺这一项** |
| Mixkit | 无人气排序 | 免费 AE 模板页 | 只能看它主推哪些类型 |
| YouTube | **播放量**、点赞数 | `yt-dlp --flat-playlist`（只取元数据，不下载视频）：5 个指定频道的全部视频，加 40+ 组关键词搜索（每组 40 条，再按播放量重排） | 搜索按相关度召回，不能保证是全站最高；播放量是累计数 |
| B 站 | **播放量** | 搜索接口 `order=click`（最多播放），每个关键词取前 10；重点视频再查 view 接口 | 「文字动画」这类词会混进《头文字D》等无关结果，已手动剔除 |
| 趋势文章 | 定性 | Envato Elements Learn、Envato Author Hub、Videobolt、Motionographer | 多数是软文，只作佐证 |

- 所有数字都是 **2026-10-31 抓取的当天值**（已核实）。「1.2万」「4.5K」一类都是原页面的写法。
- **怎么动**一栏的帧数、缓动、时长：如果没有特别注明，都是**行业惯例和教程常见值（未逐帧测量）**，按 30 fps 写（`f` = 帧）。缓动用 GSAP 名称，必要时附 cubic-bezier。
- **人气等级**：
  - **S**：至少 3 个来源达到 A，或者一个来源到了头部量级（VideoHive ≥1 万销量、YouTube ≥200 万播放、B 站 ≥300 万播放）且另有 A 级佐证。
  - **A**：VideoHive ≥3K 销量，或 YouTube ≥100 万，或 B 站 ≥100 万。
  - **B**：VideoHive ≥1K，或 YouTube ≥30 万，或 B 站 ≥10 万，或进了 Envato Elements「Popular」第 1 页。
  - **C**：只有趋势文章或零星证据。
- **可行性**：**是** = HTML/CSS/GSAP/SVG 就能做到同等效果；**部分** = 需要 WebGL、预计算或者效果打折；**否** = 依赖实拍、跟踪、抠像等，这条管线做不了。

---

## 1. 总排名 Top 25（跨来源人气）

| # | 编号 | 动效 | 等级 | 头条证据 |
|---|---|---|---|---|
| 1 | X1 | Seamless Zoom / Spin 无缝缩放旋转转场 | S | VideoHive AE 全站销量第 1：Videolancer's Transitions **41,553**；同作者的 Motion Bro 免费包官方称 **>100 万**下载；B 站「拆解博主 100 种剪辑手法」**330.8 万** |
| 2 | K1 | 2.5D Photo Parallax 照片视差 | S | VoluMax **26.4K**（全站第 2）+ Photomotion **26.1K**（第 4）；MDMZ 单图做 3D 场景 **1171.5 万**播放（本次查到的单条最高） |
| 3 | S1 | Shape Burst / Shape Elements 放射爆发和图形元素 | S | Graphics Pack **26.2K**（第 3）、Big Pack of Elements 7.3K；SonduckFilm「4 Great Motion Graphics Techniques」**321.6 万** |
| 4 | T3 | Kinetic Typography / Stomp 重拍排版 | S | TypoKing **13.4K**；Stomp 1/2/3 合计约 7K；B 站「动态歌词排版」**898 万 / 563 万 / 460 万** |
| 5 | T1 | Mask Slide-Up Reveal 遮罩上滑逐字揭示 | S | YouTube 153.6 万、145.7 万、117.3 万、92.9 万；210 Text Presets 4.3K、870 Title Animations 4K |
| 6 | K4 | Mosaic Photo Reveal / 照片墙 / Carousel | S | Mosaic Photo Reveal **16K**（第 5）、Photo Gallery on a Sunny Afternoon **8K**；Envato Popular 有 3 个 Carousel |
| 7 | S6 | Cartoon Flash FX 卡通特效元素 | S | 140 Flash FX Elements **14.7K**（第 6）、RTFX Generator **13.2K**（第 8） |
| 8 | K2 | Earth Zoom 地球推近 | S | Ultimate Earth Zoom Toolkit **9.5K**；Google Earth Studio 缩放教程 **207 万**、Video Copilot 3D 地球 **189.8 万** |
| 9 | T2 | Blur-Fade Reveal 苹果式逐字模糊渐显 | A+ | Marketing Demons **206.8 万**（2025-04，标明 Apple-style）；Bricks 76 万（2025-06）；NaughtyyJuan 40.1 万（2025-12） |
| 10 | X4 | Zoom-Through Portal 穿洞推进（瞳孔穿梭） | A+ | B 站「3 分钟学会瞳孔穿梭效果」**364.5 万**播放、20.3 万赞（2025-06）；Cinecom Infinite Zoom 117.3 万 |
| 11 | T11 | Shine Sweep / Gold Titles 金属光泽扫光 | A | Gold Simple Titles **11K**（第 10）；Logo Intro Elegance Flare 6.2K（Logo Stings 第 1） |
| 12 | T10 | Neon Flicker 霓虹闪亮 | A | Neon Sign Kit **10K**（第 11） |
| 13 | C3 | UI / Social Mockups 通知、聊天气泡、搜索框 | A | Instagram Stories **6.9K**、Text Messages 3.8K；Envato Elements「Elements」分类 Popular **第 1 名 Mobile Notification** |
| 14 | C1 | Lower Thirds 下三分之一字条 | A | 子类 2,772 个，前 30 名里 19 个销量 ≥1.1K，第 1 名 **6.3K** |
| 15 | T9 / X5 | Glitch 故障（文字和转场） | A | Video Copilot 198.5 万、Learnin5 164.2 万；Glitch Transitions 4.5K；B 站故障干扰 38.9 万 |
| 16 | C5 | Animated Icons 动态图标 | A | 555 Animated Icons **6.4K**、Flat Animated Icons 3.2K |
| 17 | D5 | HUD 科技界面 | A | Quantum HUD Infographic **5.9K**（Infographics 第 1） |
| 18 | C2 | Line Callouts 引线标注 | A | Call-Out Titles **4.5K**、8 Line Call-Outs 1.8K；Envato Popular 有 3 个 Call-Outs |
| 19 | K3 | Map Route 地图路线 | A | Map Route Generator 3.5K、3D Earth Connections 3.4K、3D Map Kit 3.2K；YouTube 169.5 万 |
| 20 | D1 | Number Counter 数字滚动 | A | YouTube 162.6 万；Envato Popular 有 Number Counter、Counter/Timer |
| 21 | P2 | Collage / Paper Cutout 拼贴剪纸 | A | Fakeplastictree「Collage」**203.5 万**；Mapal 50 万；被 2026 趋势文章反复提到 |
| 22 | T6 | Write-on 手写 / 描边→填充 | A | 描边 logo 128.5 万、手写 123.7 万；B 站 PR 文字手写 46.6 万 |
| 23 | T7 | Text Match Cut 文字匹配剪辑 | A（上升中） | Envato Elements Titles Popular **第 1、2、5、7 名**全是它；Karl Shakur 111.5 万（2024） |
| 24 | X8 | Camera Move + Impact Shake 镜头运动和冲击抖动 | A | Bricks 106.8 万（2025）、Marketing Demons 92.3 万（2025）；Envato Elements Popular 至少 6 个相关条目 |
| 25 | X2 | Whip Pan 甩镜滑移 | A | SonduckFilm「3 Popular Transitions」102.8 万（第一个就是 Whip Pan）、Olufemii 126.3 万 |

> 读法：1–8 是「多年畅销 + 教程爆款」的老牌常青款；9、10、23、24 是 **2024–2026 新起来的**，近期增长最快；13（UI 模拟）和 23（Text Match Cut）在 Envato Elements 当前的 Popular 榜上排得最靠前，代表**当下需求**。

---

## 2. 分类明细（46 条）

### A. 文字动画 Text Animation

#### T1. Mask Slide-Up Reveal（逐字/逐词遮罩上滑）— S
- **怎么动**：每行套一个 `overflow:hidden` 的遮罩；字（或词）从 `yPercent:100`（下沉在遮罩外）滑到 0。每个字 18–24f（0.6–0.8 s），`power4.out` / `expo.out`（≈ cubic-bezier(0.16,1,0.3,1)）；字与字间隔（stagger）1–2f，词与词 3–4f。可以加 `rotate: 6° → 0`，让字像翻起来。出场：`yPercent: 0 → -100`，12–15f，`power3.in`，方向不变。
- **证据**：Smertimba「[Smooth Text Animation](https://www.youtube.com/watch?v=-VCxTi8sJ-s)」153.6 万（2025-03-31）；Caleb Lancaster「[Revealing Text with Shapes](https://www.youtube.com/watch?v=7X1ogQfpQQM)」145.7 万；Smertimba「[5 Title Animations](https://www.youtube.com/watch?v=50jjngdM1Eo)」117.3 万；Motion Nations「[Mask Text Reveal](https://www.youtube.com/watch?v=93u_vKnwDXg)」92.9 万；VideoHive 标题类 [210 Text Presets](https://videohive.net/item/110-text-animations/9358175) 4.3K、870 Title Animations 4K、[Titles](https://videohive.net/item/titles-and-lower-thirds/20197947) 4.6K（[Titles 销量榜](https://videohive.net/category/after-effects-project-files/titles?sort=sales)）；B 站「[超级常用文字动画效果](https://www.bilibili.com/video/BV1YW411D7Z8)」44 万、「[文字位移遮罩](https://www.bilibili.com/video/BV1bx411p76X)」16.3 万。
- **可行性**：**是**。GSAP SplitText（3.13 起免费；新版有 `mask:"lines"` 选项，在我们锁定的 3.14.2 上需要实测）加 `overflow:hidden`。中文按单字拆没有问题。

#### T2. Blur-Fade Character Reveal（苹果式逐字模糊渐显）— A+
- **怎么动**：每个字 `opacity 0→1` + `filter: blur(10–14px)→0` + `y: 20%→0`（或 `scale 0.9→1`），20–30f，`power2.out`；stagger 1–2f；字距从宽收到正常。整体干净、慢、没有过冲。
- **证据**：Marketing Demons「[How To Master Text Animation In After Effects (Under 1 Minutes)](https://www.youtube.com/watch?v=16kTqBUh8mM)」206.8 万（2025-04-10，简介写明 *Style: Apple-style / clean / minimal*，章节是 Range Selector 配置）；Bricks「[How to Animate Like Apple](https://www.youtube.com/watch?v=n0g4HXxx03s)」76 万（2025-06）；NaughtyyJuan「[The Ultimate Apple Style Animation Guide](https://www.youtube.com/watch?v=5j4HmfgPCDI)」40.1 万（2025-12）；B 站 Heymay「[制作苹果风格视频的窍门](https://www.bilibili.com/video/BV1eJ411m7wL)」17.2 万；Envato Elements Titles Popular 第 1 页有 4 个「SaaS Text Animation」（同一种干净风格）。
- **可行性**：**是**。注意：几百个 span 都开 `filter: blur` 会拖慢渲染。字多时改用「opacity + 小位移」，只给关键词加模糊。

#### T3. Kinetic Typography / Stomp（一拍一词的重拍排版）— S
- **怎么动**：BPM 120–140，每拍 12–15f，每个词停 1–2 拍。入场 `scale 1.4→1.0`，3–4f，`power4.out`（或者直接硬切出现）。重音词配 2–4f 的整屏冲击抖动（位移 8–16 px，指数衰减），偶尔插 1f 黑白反色。字特别大（占画面宽 60–90%），用粗黑体。
- **证据**：[TypoKing](https://videohive.net/item/typoking-title-animation-kinetic-typography-text/11263341) **13,360** 销量（AE 全站第 7，Titles 第 1）；Stomp - Typographic Intro 2.8K、Stomp 2 2.5K、Stomp 3 1.7K、Typography Promo/Stomp 2K；Kinetic Typography Pack 4.2K（[Openers 销量榜](https://videohive.net/category/after-effects-project-files/openers?sort=sales)第 2）。Envato 竖屏指南称 kinetic typography 是 *workhorse of vertical motion design*。YouTube：Motion Nations「[Typography Motion Graphics](https://www.youtube.com/watch?v=UahA-6QYfC0)」78.7 万（2024），SonduckFilm「[3 Kinetic Typography Techniques](https://www.youtube.com/watch?v=UnK5lGmadSs)」69.9 万，Cinthya Studios「[Stomp Kinetic Typography](https://www.youtube.com/watch?v=HM_O0A4Xeb4)」56.8 万。B 站「动态歌词排版」类：[898 万](https://www.bilibili.com/video/BV1A341157Mq)（2022）、[563 万](https://www.bilibili.com/video/BV1NE42157kT)（2024）。
- **可行性**：**是**。关键在对拍：用口播逐字时间戳（hat9-motion 已有 `@关键词`）或 BGM 节拍表驱动。

#### T4. Typographic Camera Layout（排版块 + 镜头旋转推移，「倒鸭子」/ 文字穿梭）— A
- **怎么动**：所有词按版式拼成一张大「海报」。词与词之间，整组容器 `rotate ±90°`、缩放、平移，让新词始终落在画面中心；每次镜头移动 8–12f，`expo.inOut`。已经出现的词留在画外。3D 版本：词沿 z 轴排开，镜头 `translateZ` 依次穿过（「文字穿梭」）。
- **证据**：SonduckFilm「[3 Kinetic Typography Techniques](https://www.youtube.com/watch?v=UnK5lGmadSs)」69.9 万（章节写明 *swing over to the next typography block*）；B 站 2018 年抖音爆款「倒鸭子」（Typemonkey）：[3.6 万](https://www.bilibili.com/video/BV1ds41137gs)、[2.7 万](https://www.bilibili.com/video/BV1mb411c7PP)；「[PV 中的文字穿梭效果](https://www.bilibili.com/video/BV1pb411v7BN)」23 万；「[3D 摄像机文字拉镜](https://www.bilibili.com/video/BV1A34y1K7ye)」15 万；VideoHive Flying Through Words Logo Reveal 2.2K、Words Logo Animation 2.1K（[Logo Stings 销量榜](https://videohive.net/category/after-effects-project-files/logo-stings?sort=sales)）。
- **可行性**：**是**。容器的 `transform-origin` 设在当前词中心，用 GSAP 算逆变换；3D 版本用 CSS `perspective`。

#### T5. Typewriter / Search Typing（打字机和搜索框输入）— A
- **怎么动**：字符逐个出现，**不加缓动**（按帧硬切），英文 12–20 字/秒，中文 8–12 字/秒更好读。光标 0.5 s 亮、0.5 s 灭（`steps(1)`），打字时常亮。搜索框版本：框体 `scaleX 0.6→1`（12f，`back.out(1.2)`）→ 打字 → 「回车」→ 结果卡片自下而上依次进入（stagger 4f）。
- **证据**：Askiko「[Typewriter Text Effect](https://www.youtube.com/watch?v=_28MzZIVuQQ)」113.3 万；Motion Array「[Typing Effect](https://www.youtube.com/watch?v=IMtMYu_jyNU)」18.6 万（2024）；B 站「[PR 打字机](https://www.bilibili.com/video/BV1Vt411R7nk)」54.4 万、「[AE 流畅打字](https://www.bilibili.com/video/BV1Ab411Y7yW)」17.6 万；Envato Elements「Elements」分类 Popular 第 7 名「Search Screen Pro - Typing Animation」、第 23 名「Search Bars」，Titles 分类有「Typewriter Pro」；VideoHive Text Messages 3.8K。
- **可行性**：**是**（GSAP TextPlugin，或按帧截取字符串）。演示「在 AI 工具里输入 prompt」正好用得上。

#### T6. Write-on（手写，或描边→填充）— A
- **怎么动**：手写是沿字形中心线做 `stroke-dashoffset 1→0`，每笔时长和笔画长度成正比，每字 0.3–0.6 s，笔画之间停 2–3f，`sine.inOut` 或 linear。描边→填充是外轮廓先画（0.8–1.2 s，`power2.inOut`），画到 70% 时填充 `opacity 0→1`（0.3 s）。
- **证据**：「[Stroke Logo Animation](https://www.youtube.com/watch?v=r0OTQCvD92Y)」128.5 万；SonduckFilm「[Handwriting Effect](https://www.youtube.com/watch?v=GbMX20YoNTw)」123.7 万；VerticDesigns「[Handwriting Text Reveal](https://www.youtube.com/watch?v=78uhkYo5UOE)」83.2 万；SonduckFilm「[Stroke Logo Reveal Outline](https://www.youtube.com/watch?v=H1xNSFfQALk)」66.7 万；VideoHive「Elegance - Animated Handwriting Typeface」1.5K；B 站「[Pr 文字手写动画](https://www.bilibili.com/video/BV1xW411d7os)」46.6 万、「[PR 描边动画](https://www.bilibili.com/video/BV1Rg411R75d)」18.9 万。
- **可行性**：**是**。英文用单线字体；中文笔顺数据可以用 hanzi-writer（代码 MIT）加 makemeahanzi 数据（数据是 Arphic Public License，打包前要核对）。描边→填充用 opentype.js 把 OFL 字体转成 path，再用 DrawSVG。

#### T7. Text Match Cut（文字匹配剪辑）— A（上升最快）
- **怎么动**：关键词**固定在画面同一位置**（通常正中），背后的载体（报纸、网页、文件截图、不同字体）每 2–4f 硬切一次，连切 6–12 次，最后停在主画面。常配 1f 白闪或扫描线，加快门声。VideoHive「[Match Cut Universal](https://videohive.net/item/match-cut-universal/59112852)」全长 0:03、6 个场景，**平均每场景约 15f**（推导）。
- **证据**：[Envato Elements AE 总表 Popular](https://elements.envato.com/video-templates/compatible-with-after-effects) 第 1、2、12、17 名都叫「Text Match Cut」；[Titles 分类 Popular](https://elements.envato.com/video-templates/titles/compatible-with-after-effects) 第 1、2、5、7 名也是；Infographics 分类第 1 名是「Match Cut」。YouTube：Karl Shakur「[The PERFECT Match Cut Transition](https://www.youtube.com/watch?v=CWb6ldBOhNE)」111.5 万（2024-01），Herman Huang「[6 Match Cut Transitions](https://www.youtube.com/watch?v=CGzyD_54ajU)」98.9 万；Johnny Harris / Vox 式报纸动画 [19.6 万](https://www.youtube.com/watch?v=qjafHzNJLQ0)（2024）；Motion Array「[Edit a Documentary Like Johnny Harris](https://www.youtube.com/watch?v=nZrPVUzYHKE)」53.9 万。
- **可行性**：**是**，这是最简单的一类：截图素材 + 关键词定位对齐 + 硬切。很适合「证据截图」堆叠。截图里的他人头像和个人信息要打码。

#### T8. Highlighter（荧光笔划重点）— B
- **怎么动**：关键词后面的色块 `scaleX 0→1`（`transform-origin: left`），12–18f，`power2.out`。色块高度占字高 40–60%（压在下半部）或者全高，轻微旋转 −1° ~ −2°，边缘用不规则笔刷 mask，混合模式 `multiply`。多个词依次出现，间隔 0.15 s。
- **证据**：Motion Street「[Motion Graphics Like Vox](https://www.youtube.com/watch?v=mVhEb-4nnhQ)」83.8 万（2024）；Flat Pack FX「[Vox Highlighter Effect](https://www.youtube.com/watch?v=a0T3kcizcOY)」31.3 万；Premiere Gal 3D Paper Highlighter 19.8 万；Mapal「How To Make Vox Style Videos」37.9 万。
- **可行性**：**是**。

#### T9. Glitch / RGB Split Text（故障字）— A
- **怎么动**：突发式。每 1–2 s 出现一段 2–6f 的故障：R、G、B 三份副本水平错开 ±4–12 px；画面切成 3–8 条水平带，每条带横向错位 10–40 px；可夹 1f 反色。全部**不加缓动**（按帧切换）。
- **证据**：Video Copilot「[Colorful Glitch FX](https://www.youtube.com/watch?v=3Rc0dNDzbuM)」198.5 万；Learnin5「[Glitch Effect](https://www.youtube.com/watch?v=OfHN2GSkAP8)」164.2 万；VideoHive Epic Digital Distortion 2.6K、Ultimate Glitch Logo Intro 2.5K、9 Modern Glitch Titles 1.6K、Glitch Logo 1.7K；B 站「[故障干扰特效](https://www.bilibili.com/video/BV1NU4y1e742)」38.9 万。
- **可行性**：**是**。用 CSS `clip-path: inset()` 切带，再叠 3 层着色副本（`mix-blend-mode: screen`）；也可以用 SVG `feColorMatrix` + `feOffset`，WebGL shader 最逼真。**随机序列必须用种子**（HyperFrames 不允许用 `Math.random`）。

#### T10. Neon Flicker（霓虹点亮）— A
- **怎么动**：点亮阶段 0.3–0.8 s，按开关表闪烁，例如 [亮 2f, 灭 3f, 亮 1f, 灭 4f, 亮 2f, 灭 1f, 常亮]，辉光半径跟着变。常亮后亮度做 ±2–4% 的不规则低频抖动；可以让某一个字母当「坏灯管」，偶尔闪一下。
- **证据**：VideoHive [Neon Sign Kit](https://videohive.net/item/neon-sign-kit/11928076) **10K**（AE 全站第 11）、Neon Light 2.1K、Light Bulb Kit 1.5K；Smertimba「[Flicker Text Animation](https://www.youtube.com/watch?v=leryJQre62o)」61.3 万；B 站 doyoudo「[Saber 霓虹灯文字](https://www.bilibili.com/video/BV1Wg411c7b1)」11.5 万。
- **可行性**：**是**（多层 `text-shadow` / `drop-shadow` + 写死的闪烁表）。

#### T11. Shine Sweep / Gold Titles（金属光泽扫光）— A
- **怎么动**：字用金属渐变填充（`background-clip:text`）。一道倾斜 15–25° 的高光带从左扫到右，0.6–1.0 s，`power2.inOut`，每 3–4 s 重复一次。同时整体做慢推 `scale 1.00→1.05`（全程 linear），字距略微收紧。
- **证据**：VideoHive [Gold Simple Titles | 4K](https://videohive.net/item/30-simple-titles-/14507047) **11K**（AE 全站第 10，售价 14 美元）；[Logo Intro Elegance Flare](https://videohive.net/item/logo-intro-elegance-flare/237833) 6.2K（Logo Stings 第 1，靠光斑扫过）；Platinum Logo Reveal 3K；Glossy Logo 两款各 1.8K；Envato Elements Titles Popular 有「Luxury Gold Titles」「Golden Titles Cinematic」「Advanced Chrome Typography」。
- **可行性**：**是**。光斑用 `radial-gradient` 加 `screen` 混合，不要用 Optical Flares 之类的现成素材。

#### T12. Word-by-Word Captions（口播逐词字幕 + 当前词高亮）— B（竖屏刚需）
- **怎么动**：按 `words.json` 每 1 个词（或 2–4 个字）出现一次；当前词换色或加底色块，同时 `scale 1.0→1.1→1.0`（4–6f，`back.out`）；最多 2 行。出现方式用 pop（`scale 0.8→1`，3f）或 `y: 10px→0`。9:16 放在中线偏下，避开底部 1/4 和右侧点赞栏（Envato 竖屏安全区建议）。
- **证据**：Envato Elements Titles Popular 第 12 名「Hook & Captions for Social Media」；[Envato 竖屏动效指南](https://elements.envato.com/learn/motion-graphics-for-short-form-video)明确要求 *word by word, synced to the voiceover*；YouTube Hormozi 式字幕：[CapCut 85.9 万](https://www.youtube.com/watch?v=O6-1Bd6SaXg)（2023）、[Premiere 40.2 万](https://www.youtube.com/watch?v=MYdKBuA3XF8)，Matt Loui「Smooth Style Captions」72.8 万。
- **可行性**：**是**（hat9-motion 已经有字幕和 `@关键词` 对时）。

### B. 转场 Transitions

#### X1. Seamless Zoom / Spin（无缝缩放和旋转转场，"Handy Seamless"）— S
- **怎么动**：
  - 出镜：前一画面最后 6–8f `scale 1→1.6–2.5`，`power3.in` / `expo.in`，径向（缩放）模糊同步从 0 拉到最强。
  - 切点：在模糊最强的那一帧。
  - 入镜：新画面从 `scale 0.5`（zoom-out 版）或 `2.0`（zoom-in 版）回到 1，6–8f，`expo.out`，模糊从最强降到 0。
  - 总长 12–16f（0.4–0.53 s）。
  - Spin 版：`rotate 0→±90°`（或 180°）加旋转模糊，画面边缘用镜像填充（AE 里是 Motion Tile 的 mirror edges），避免露出黑边。
- **证据**：VideoHive「[Videolancer's Transitions for After Effects](https://videohive.net/item/handy-seamless-transitions-pack-script/18967340)」**41,553** 销量（[AE 全站销量榜](https://videohive.net/category/after-effects-project-files?sort=sales)第 1）。页面分类依次是 Distortion Zoom、Pan、Spin、3D、Stretch、Split、Stylization、Shape、Glitch、Light Leaks、Simple，更新日志里还有 Smoothed Motion Blur。同作者的 Motion Bro 免费包官方称「超过 100 万用户下载」，含 1,400+ 转场预设（搜索摘要，页面 403 未直读）。另有 Distortion Zoom Transitions 1.3K。YouTube：Olufemii「[10 Easy After Effects Transitions](https://www.youtube.com/watch?v=Fj7woohZ0is)」126.3 万（含 Punch Zoom、Motion Tile）。B 站：「[挑战拆解博主的 100 种剪辑手法](https://www.bilibili.com/video/BV1vxe8z2Exj)」330.8 万（2025-08），「[又一个神级转场](https://www.bilibili.com/video/BV1EY41137Xv)」87.3 万。
- **可行性**：**部分 → 是**。缩放和旋转用 CSS 就行。CSS 没有径向模糊：要么写 WebGL 片元着色器（16–32 次采样），要么叠 8–12 层逐级放大、透明度递减的副本来近似。镜像边缘用 WebGL，或在四周摆 `scaleX(-1)` 的副本。

#### X2. Whip Pan / Slide（甩镜滑移）— A
- **怎么动**：两个画面一起 `translateX -100%`（或沿 y），8–12f，`power4.inOut`（中段速度最快）。中段加水平方向模糊，大小跟速度曲线走（SVG `feGaussianBlur stdDeviation="30–60 0"`）。可以再加 `rotate ±2°` 和 `scale 1.05`，让它更「甩」。
- **证据**：SonduckFilm「[Create 3 Popular Transitions](https://www.youtube.com/watch?v=0refWK_eIgo)」102.8 万（第一个就是 Whip Pan）；Smertimba「[Seamless Whip Pan](https://www.youtube.com/watch?v=DfQutCJ3UBc)」63 万（AE 版）+ 77.9 万（PR 版）；Olufemii 126.3 万；Videolancer 包有「Pan」分类；Split Handy Transitions 923。
- **可行性**：**是**（SVG 的 x/y 分向高斯模糊在 Chromium 里可用）。

#### X3. Shape Wipe（色块扫屏）— A
- **怎么动**：2–4 个色块（矩形条、圆或斜条）依次横扫，彼此间隔 2–3f；每块进 10–14f、出也 10–14f，都用 `power3.inOut`。最后一块盖满画面时切换新画面，或者直接用它当 mask 揭示新画面。总长 18–24f。
- **证据**：Mister Horse「Shape Transitions」200+ 个（Animation Composer 的付费包；插件官方称「超过 1,000,000 名动效设计师使用」，见 [misterhorse.com](https://misterhorse.com/products-for-after-effects)）；[Graphics Pack](https://videohive.net/item/graphics-pack/22601944) 26.2K（更新日志里有 Flat Transitions）；SonduckFilm「3 Popular Transitions」第二段是 Shape Transition；Olufemii 有 Wipe Transition。
- **可行性**：**是**。

#### X4. Zoom-Through Portal（穿洞推进，「瞳孔穿梭」/ Infinite Zoom）— A+
- **怎么动**：先把下一画面放进当前画面里的一个「洞」：瞳孔、窗户、手机屏，或者字母 O 的内腔。镜头对准洞的中心，`scale 1→20–50` 倍，按**对数插值**（每帧放大固定倍率，看起来才匀速），20–40f，`expo.inOut`。洞填满画面后移除外层。
- **证据**：B 站 letmedream「[3 分钟学会瞳孔穿梭效果](https://www.bilibili.com/video/BV1heMvzxEQd)」**364.5 万**播放、20.3 万赞、10.8 万收藏（2025-06-15）；Cinecom「[SUPER EASY Infinite Zoom](https://www.youtube.com/watch?v=1P-SgxQYke4)」117.3 万；SonduckFilm Infinite Zoom 38.5 万；Motion Design School「Infinite Zoom」16.4 万。
- **可行性**：**是**（CSS transform + 对数缩放）。图片分辨率要够，或者用矢量图。

#### X5. Glitch Transition（故障转场）— A
- **怎么动**：切点前后各 3–5f：切带错位 + RGB 分离 + 马赛克块（8–32 px）+ 1f 黑或白，然后硬切。
- **证据**：VideoHive [Glitch Transitions](https://videohive.net/item/glitch-handy-transitions/21059280) 4.5K（AE 全站第 29）、Glitch Twitch RGB TV Noise 777；Ben Marriott「[Cyberpunk Glitch Transitions](https://www.youtube.com/watch?v=YjgfuUxfgqU)」54.1 万；Herman Huang「[Melting Glitch Transition](https://www.youtube.com/watch?v=zTnC63LORrI)」60.6 万；Envato Elements Popular 有「Glitch Transition」「CRT TV Look Cinematic Transition」。
- **可行性**：**是**（CSS / SVG 就够；马赛克用 WebGL 或 canvas 采样）。

#### X6. Light Leak / Flash / Film Burn（光漏、闪白、烧片）— B
- **怎么动**：
  - 过曝闪：白色 overlay `0→1`，4–6f，`power2.in`；切点在峰值；之后 8–15f 衰减，`power2.out`。
  - 光漏：2–3 个橙红或暖黄的径向渐变团，用 `screen` 混合从一侧漂过，20–40f。
- **证据**：VideoHive Light Transitions & Burns 1.7K、15 Massive Light Transitions 1.7K、Lens Flare Transitions 1.4K、Light and Particle Transitions 1.3K（[Transition 销量榜](https://videohive.net/category/after-effects-project-files/elements/transition?sort=sales)）；Olufemii 的 Graphic Flash 和 Film Burn 两段；Envato Elements Popular 有「Flash Cutout Transitions」「Cinematic Film Reel Transitions」「Bokeh Leaks Transitions」。
- **可行性**：**是**（程序化生成的渐变 + `mix-blend-mode: screen`，不用现成的光漏视频）。

#### X7. Paper Rip / Brush Reveal（撕纸和笔刷揭示）— B
- **怎么动**：锯齿状的撕纸边（SVG 路径）从一侧推进或撕开，10–15f。帧率降到 12 fps（一拍二，按帧切换），显得像手工做的。撕口带白色纸芯描边和投影。笔刷版：2–4 道粗笔刷 mask 来回刷开，15–20f。
- **证据**：VideoHive Paint Brush Transitions Reveal Pack 2.1K、Torn Paper Transitions 1.3K；Envato Elements Popular 有「Kinetic Paper Rip Transitions」「Paper Transitions」；Smertimba「[Paper Unfold (Ali Abdaal)](https://www.youtube.com/watch?v=1kdURN_zqE4)」29 万（2024）；Motion Caddy「[Paper Tear](https://www.youtube.com/watch?v=GfRV0w9B-TQ)」25.9 万；Videobolt 2026 趋势里有「Torn paper aesthetics」。
- **可行性**：**是**（纸纹自己做，锯齿用种子生成）。

#### X8. Camera Move + Impact Shake（虚拟镜头转场和冲击抖动）— A
- **怎么动**：
  - 镜头转场：整个场景容器在切换时 `rotateZ ±8–15°`、`scale 1→1.3`，同时平移；12–18f，`expo.inOut`；切点在中段，配方向模糊。
  - 冲击抖动：位移噪声振幅 12–24 px，指数衰减，3–4 次振荡，0.3–0.5 s（GSAP CustomWiggle，或自己写阻尼正弦）。常和 stomp 字或数字落地同步。
- **证据**：Envato Elements「Elements」分类 Popular 里有 Camera Movement Transition（第 6）、Camera Transition（第 14）、Premium Overlays Camera Shake（第 15）、Camera Movement Transitions（第 22）、Shake Transitions Pack（第 38）、Cinematic Perspective Transitions（第 37），见[该分类页](https://elements.envato.com/video-templates/elements/compatible-with-after-effects)。YouTube：Bricks「[Smooth Camera Movement](https://www.youtube.com/watch?v=PdHYC0gqIPA)」106.8 万（2025-03），Marketing Demons「[Master Camera Movement](https://www.youtube.com/watch?v=tX162LxOx-I)」92.3 万（2025-05）。B 站「AE 变速卡点练习」173.4 万。
- **可行性**：**是**。

### C. 图形元素和爆发 Shape Elements / Bursts

#### S1. Circle Burst / Shape Splode（放射线爆发）— S
- **怎么动**：6–12 条放射线。每条线的 trim path 先让 `end` 从 0 到 100%（0–8f，`expo.out`），再让 `start` 从 0 到 100%（3–12f，`power2.in`），效果是线「射出去再消失」。同时外圈圆环 `scale 0.2→1.2`、描边宽度 8→0（10–14f）。可以再加 3–5 个小点或三角向外飞并缩小。总长 12–18f。用来强调重点、配数字落地或 logo 出现。
- **证据**：VideoHive [Graphics Pack](https://videohive.net/item/graphics-pack/22601944) **26.2K**（AE 全站第 3）、[Big Pack of Elements](https://videohive.net/item/big-pack-of-elements/19888878) 7.3K、MoPack 3.6K、Shape Elements（YashkovskiyMD）2.5K；Mister Horse「[Shape Elements](https://misterhorse.com/products/shape-elements/3260)」922 个元素，示例名有 Impact 360、Lines、Dashes、Star。YouTube：SonduckFilm「[4 Great Motion Graphics Techniques](https://www.youtube.com/watch?v=9bnOVV3EBC8)」**321.6 万**（章节：Animated Lines、Shape Splodes、Repeated Circle）；「[4 Great Circle Burst](https://www.youtube.com/watch?v=-dnZ-iJiIAk)」56.7 万；PremiumBeat「[Animated Circle Burst](https://www.youtube.com/watch?v=wPFdak9dYbE)」84.8 万；ECAbrams「[Shape Layer Repeater (radial)](https://www.youtube.com/watch?v=wOZwzLgJw9o)」99.2 万。
- **可行性**：**是**（SVG 线条 + `stroke-dasharray` / DrawSVG；repeater 用循环生成）。

#### S2. Line Draw + Arrows（线条描出和箭头）— A
- **怎么动**：路径描边从 0 画到 100%，0.5–1.0 s，`power2.inOut`；画到 80–100% 时箭头 `scale 0→1`（`back.out`）。可选「虚线流动」：`dashoffset` 线性循环。
- **证据**：Motion Nations「[Minimal Line Motion Graphics Text](https://www.youtube.com/watch?v=7LW5mRTvNcY)」112.1 万（2024-08）；Andrew Pach「[Animate a line along a path](https://www.youtube.com/watch?v=BYWGWATVWVI)」92.8 万；Motion Array「[How To Animate A Line](https://www.youtube.com/watch?v=9Qz4Nldjv6I)」82.6 万；Manuel does Motion「Crazy Trim Paths Tricks」53.9 万；VIDEO MARK「[Animated Arrows](https://www.youtube.com/watch?v=ofwHRvKuwqo)」31.4 万。
- **可行性**：**是**（DrawSVGPlugin 或 `stroke-dashoffset`）。

#### S3. Pop-in with Overshoot / Squash & Stretch（弹出过冲和挤压拉伸）— A
- **怎么动**：标准弹出是 `scale 0 → 1.15`（第 6 帧）→ `0.95`（第 10 帧）→ `1.0`（第 14 帧）；或者直接用 GSAP `back.out(1.7)`（约 10% 过冲）、`elastic.out(1, 0.45)`。落地时挤压：`scaleX 1.15 / scaleY 0.85` 保持 2–3f 再回弹。位移入场时，跟随元素晚 2–3f（overlap）。
- **证据**：Mister Horse「Animation Presets」4.93 星、**1,434 条评分**，官网唯一标「Most Loved」的产品；「[Motion Presets](https://misterhorse.com/products/the-most-handy-motion-presets/43)」1,892 个预设（2D 和 3D Transitions）。B 站爆肝小陈「[5 个动画原理让你的动画更加生动](https://www.bilibili.com/video/BV1g8yfYeE3W)」135.9 万（2024-10），CD 动效研究所「[弹性缩放动画](https://www.bilibili.com/video/BV1rZ4y1P7Hs)」17.5 万。YouTube：Amin Ameri「[Rig and animate ANY Shape](https://www.youtube.com/watch?v=PiSxftDea4w)」78.8 万（2025），Smertimba「[Text Bounce](https://www.youtube.com/watch?v=rDwdXeouQVU)」47.3 万，Jake In Motion「[The LAST graph editor tutorial](https://www.youtube.com/watch?v=7pOCtlrrE3Y)」32.3 万。
- **可行性**：**是**（GSAP `back` / `elastic` / CustomBounce）。

#### S4. Shape Morph（形状变形）— A
- **怎么动**：路径 A 变到 B，12–20f，`power3.inOut`，结尾可加 5% 过冲；颜色和旋转一起变。常用于图标变形（比如问号变灯泡）。
- **证据**：Ben Marriott「[Quick & Easy Shape Morph](https://www.youtube.com/watch?v=3EGuLX6PsQ4)」106.1 万、「[Perfect Shape Morphs](https://www.youtube.com/watch?v=n24aTp1-jK4)」37.8 万（2024）；Smertimba「Shape Morph」40.2 万；NaughtyyJuan「Apple Style UI Shape Morphing」27 万；VideoHive Logo Transforming 2K。
- **可行性**：**是**（MorphSVGPlugin 现在免费）。

#### S5. Liquid / Goo Blobs（液体融球）— A
- **怎么动**：几个圆形 blob 套 goo 滤镜融成一体：`feGaussianBlur` σ≈10，再用 `feColorMatrix` 做 alpha 阈值（`0 0 0 18 -7`）。分裂与合并 20–40f，`elastic.out`。液体转场版：波浪边的 mask 向上涌，15–20f。
- **证据**：VideoHive Liquid Motion Elements 3.2K（售价 199 美元）；Avnish Parker「[Liquid Logo Animation](https://www.youtube.com/watch?v=Dta9tIMbNWo)」113.3 万；SonduckFilm「[3 Liquid Motion Graphics Effects](https://www.youtube.com/watch?v=Pq7BEhiHcKU)」85.4 万；Manuel「Liquid Transitions」57.8 万；Ben Marriott「[Liquid Text](https://www.youtube.com/watch?v=MVeVkawiHd4)」48.8 万。
- **可行性**：**是**（SVG goo 滤镜，注意大面积使用时的性能）。

#### S6. Cartoon Flash FX（卡通特效：烟团、冲击星、速度线、飞溅）— S
- **怎么动**：一拍二（12 fps）逐帧动画。烟团 8–16f，先膨胀再碎散；冲击星和速度线 4–8f；液体飞溅 10–14f；元素消失时「噗」地冒一团烟。
- **证据**：VideoHive [140 Flash FX Elements](https://videohive.net/item/140-flash-fx-elements/11266469) **14.7K**（AE 全站第 6）、[RTFX Generator](https://videohive.net/item/rtfx-generator-440-fx-pack/19563523) **13.2K**（第 8）、Flash FX Pro 2.6K、Pretty Sweet 2D Toolkit 4.8K；Mister Horse 有「2D Special Effects」包。B 站「[白菜和杜比：同款手绘科普动画怎么做](https://www.bilibili.com/video/BV1CguN6VEvz)」69.9 万（2026-08），手绘元素是核心。
- **可行性**：**部分**。矢量逐帧要自己画，可以用 SVG path 关键帧 + 按帧切换；**不能**用 RTFX 等付费素材。

### D. 标注、字条、信息框 Callouts / Lower Thirds / Info Boxes

#### C1. Lower Third（下三分之一字条）— A
- **怎么动**：色条 `scaleX 0→1`（12f，`power3.out`）→ 名字从色条下方遮罩上滑（10f，延迟 4f）→ 副标题再晚 3f；停留 3–5 s；退场倒着播，但更快（8–10f，`power2.in`）。
- **证据**：VideoHive Lower Third 子类共 2,772 个，[销量榜](https://videohive.net/category/after-effects-project-files/elements/lower-third?sort=sales)前 30 名里有 19 个销量 ≥1.1K：[Lower Thirds（NLTB4540）](https://videohive.net/item/lower-thirds/10338608) 6.3K（AE 全站第 20），GerardGerard 3.2K，FALCOM 3.1K，AeMar 2.9K，CleanAndSimple 2.5K 和 2.1K……；SonduckFilm「[Create Any Type of Lower Third](https://www.youtube.com/watch?v=etemwff6LTQ)」67.5 万；Envato Elements Popular 里有 4 个 Lower Third；B 站 doyoudo「[多彩字幕条动画](https://www.bilibili.com/video/BV1vA411e7Wu)」4.1 万。
- **可行性**：**是**。无脸频道用它标「来源 / 人物 / 数据出处」。

#### C2. Line Callout（圆点 + 折线引线 + 标签）— A
- **怎么动**：圆点 `scale 0→1`（6–8f，`back.out`），外加脉冲环 `scale 1→2.5`、`opacity 1→0`（每 1 s 循环）；引线分两段（先斜段再水平段）依次画出，合计 10–14f，`power2.inOut`；文字从引线末端遮罩滑出，8–10f；退场反过来。要跟随画面里的物体，就需要跟踪数据。
- **证据**：VideoHive [Call-Out Titles](https://videohive.net/item/callout-titles/11111538) **4,481**（AE 全站第 28，含 33 个 callout）、8 Line Call-Outs 1.8K（[Infographics 销量榜](https://videohive.net/category/after-effects-project-files/infographics?sort=sales)第 6）、Callout Pack 1.4K、Engineered Call-Outs 873、Line Call-Outs Pack 858；Envato Elements Popular 有「Call-Outs」「Stylish Call Outs」「Modern Call Outs」；SonduckFilm「[Callout Titles](https://www.youtube.com/watch?v=ywnKh121gIo)」36.6 万。
- **可行性**：**是**。标注静态图或截图最简单；视频里跟随物体需要预先算好跟踪点。

#### C3. UI / Social Mockups（手机通知、聊天气泡、搜索框、点赞订阅按钮）— A
- **怎么动**：
  - 通知横幅：从屏幕顶部 `y: -120% → 0`，10–12f，`back.out(1.4)`；停 1.5–2.5 s；向上滑出 8f，`power2.in`。
  - 聊天气泡：`transform-origin` 设在气泡尾巴的角上，`scale 0→1`，8f，`back.out(1.6)`，每条间隔 0.6–1.2 s；前面先放「正在输入」三个点（每个点上下 6 px 正弦运动，周期 0.6 s，相位差 0.15 s）。
  - 按钮：光标移入 → 按下 `scale 0.92→1` → 变色 + 一个小爆发。
- **证据**：Envato Elements「Elements」分类 Popular **第 1 名「Mobile Notification」**，还有「Text Messages」「Search Bars」「YouTube Subscribe」（2 个）「Universal Mobile Notifications」「Checklist Pack」；VideoHive [Instagram Stories](https://videohive.net/item/instagram-stories-designs-and-transitions-pack/21895564) 6.9K（AE 全站第 17）、Instagram Stories（RoyalFX）3K、Text Messages 3.8K、Phone 7 App & Gestures 2.6K、Get Social 2.1K、The YouTuber Pack 3.0 1.7K、Social Media Bundle 1.5K（[Product Promo](https://videohive.net/category/after-effects-project-files/product-promo?sort=sales) / Lower Third 销量榜）。
- **可行性**：**是**（纯 DOM）。做通用 UI，不要仿真微信、抖音或 iOS 的商标界面。

#### C4. Glass Card / Liquid Glass（毛玻璃卡片和液态玻璃）— B（2025 起热）
- **怎么动**：卡片从下方 40–60 px 升起，同时 `opacity 0→1`，16–20f，`expo.out`；`backdrop-filter: blur(0→16–24px) saturate(1.4)`；边缘 1 px 高光描边，高光沿边缘慢慢扫过（2–3 s）。液态玻璃版：边缘有折射（位移贴图），按下时 `scale 0.96` 弹回（spring）。
- **证据**：Envato Elements「Elements」分类 Popular 第 4 名「Real Glass FX」，还有「Glassmorph Calendar」；Titles 分类有「Liquid Glass Titles」；Infographics 分类有「Modern Price Tags & Counters | Solid, Glass & Liquid」。YouTube：Bricks「[Animate Like Apple (Liquid Glass UI)](https://www.youtube.com/watch?v=n0g4HXxx03s)」76 万（2025-06），bentomotion「[Apple Liquid Glass UI](https://www.youtube.com/watch?v=J9MORPelLZk)」30.5 万（2025-07），MDMZ「[Apple's Liquid Glass, No Plugins](https://www.youtube.com/watch?v=Czh7wbRtv2Y)」18.7 万（2025-07）。B 站「[磨砂质感的毛玻璃卡片动效](https://www.bilibili.com/video/BV1qD4y1X7NT)」15.5 万，「[商用级毛玻璃](https://www.bilibili.com/video/BV1mg411T7Bt)」10.3 万。[Videobolt 2026 趋势](https://blog.videobolt.net/post/top-motion-graphics-trends-2026)里有「Dispersions and glass shapes」。
- **可行性**：毛玻璃**是**；真实折射**部分**：可以用 `backdrop-filter: url(#svg位移滤镜)`（只有 Chromium 支持，要在 HyperFrames 渲染器里实测），或者用 WebGL。

#### C5. Animated Icons（动态图标）— A
- **怎么动**：线性图标描线 0.4–0.6 s，`power2.inOut`，画完后 `scale 1→1.1→1`（6f）；填充图标用 pop（`back.out`），内部元素错开 2–3f。
- **证据**：VideoHive [555 Animated Icons](https://videohive.net/item/500-animated-icons/5586340) **6.4K**（AE 全站第 19）、Flat Animated Icons Library 3.2K、Pictogram Infographic Kit 759；Envato Popular 有「50 Animated Real Estate Line Icons」「Marketing & Business Flat Design Icons」「Medical Glass Icons」；Mister Horse 有「Icons」包。
- **可行性**：**是**。图标用 Lucide（ISC）、Tabler（MIT）或 Phosphor（MIT），配 DrawSVG。

### E. 镜头、3D、视差 Camera / 3D / Parallax

#### K1. 2.5D Photo Parallax（照片分层视差）— S
- **怎么动**：把照片抠成前景、中景、背景 3–5 层（背景要补洞），按深度放到 z 轴上。镜头 3–6 s 推进 5–15%（linear 或 `sine.inOut`），或者横移；前景位移约是背景的 2–4 倍。可以再加光线或粒子层增强纵深。
- **证据**：VideoHive [VoluMax](https://videohive.net/item/volumax-3d-photo-animator/13646883) **26.4K**（AE 全站第 2）、[Photomotion](https://videohive.net/item/photo-motion-pro-professional-3d-photo-animator/13922688) **26.1K**（第 4）、[Cinematic Parallax Slideshow](https://videohive.net/item/cinematic-parallax-slideshow/20481472) 5.4K（Openers 第 1）、Photo Animator 3.6K。YouTube：MDMZ「[Create a 3D Scene from a Single Photo](https://www.youtube.com/watch?v=7tVyu-rjHbg)」**1171.5 万**（2021），Josh Keogh「[2.5D parallax](https://www.youtube.com/watch?v=GZimVBFSGm0)」117.1 万，SonduckFilm 3D 照片 68.4 万和 27.6 万。B 站 doyoudo「[三维视差](https://www.bilibili.com/video/BV1Jb411V7HJ)」10.4 万。
- **可行性**：**是**。用 CSS 3D 分层；或者单图 + 深度图，在 WebGL 里做位移。深度图模型用 Depth Anything V2 **Small**（Apache-2.0）；Base / Large 是 CC-BY-NC-4.0。这条对「AI 图 + 口播」用处最大：每张静态 AI 图都能动起来。

#### K2. Earth Zoom（从太空推到地点）— S
- **怎么动**：太空中缓慢自转的地球 → 国家 → 城市 → 地标。缩放按对数插值，3–6 s，整体 `expo.inOut`；相邻层级的图在重叠区间交叉淡化，配一点云层视差；最后用地图标点或文字落地收尾。
- **证据**：VideoHive [Ultimate Earth Zoom Toolkit](https://videohive.net/item/ultimate-earth-zoom-toolkit/10354880) **9.5K**（AE 全站第 12）、Earth Zoom Pro X 2.4K、Earth Zoom Full Custom Kit 1.7K；YouTube：Javier Mercedes「[Google Earth Studio Zoom Transition](https://www.youtube.com/watch?v=nC2B_3PaMuU)」**207 万**，Video Copilot「[Ultra 3D Earth + ORB](https://www.youtube.com/watch?v=iT12Q9O-Q30)」189.8 万，GYAAN「EARTH ZOOM」113.9 万。
- **可行性**：**部分**。技术上可行：WebGL 地球（three.js MIT / globe.gl MIT）+ 多级图片。难点在图源：Google Earth / Earth Studio 的影像有使用限制，应改用 NASA Blue Marble（公有领域）和 Natural Earth（公有领域）矢量，画成风格化地图；用 OpenStreetMap 要按 ODbL 署名。

#### K3. Map Route（地图路线）— A
- **怎么动**：地图先淡入或推近；路线虚线**匀速**描出（linear，时长按路程定，1.5–4 s）；交通工具图标沿路径走（MotionPath，`autoRotate`）；起点终点的图钉从上落下（`back.out`）并带涟漪；镜头跟着路线调整取景（`power2.inOut`）。
- **证据**：VideoHive Map Route Generator 3.5K（Openers 第 4）、3D Earth Connections V2 3.4K、Infographics 3D Map Kit 3.2K（Infographics 第 2）、World Map Animation 2.8K、Map Kit 1.4K；YouTube：Ignace Aleya「[Clean 3D Animated Travel Map](https://www.youtube.com/watch?v=p2O2VYm0uvo)」169.5 万，Octopus Effects「[Animated Travel Map](https://www.youtube.com/watch?v=aztbDYxz92Y)」77.6 万，Vox 式地图 27.3 万 / 14.6 万；B 站「[飞机路线地图动画](https://www.bilibili.com/video/BV14t41167tw)」6.9 万，「[告别 AE：Claude+Remotion 做地图路线](https://www.bilibili.com/video/BV1tsfvBFE1F)」2.4 万（2026）。
- **可行性**：**是**（SVG + Natural Earth / GeoJSON + d3-geo（ISC）投影 + MotionPathPlugin）。

#### K4. Mosaic Reveal / Photo Wall / 3D Carousel（马赛克拼图、照片墙、3D 轮播）— S
- **怎么动**：
  - Mosaic：几十到几百张小图从画外或深处飞入，排成网格；镜头从局部拉远（`scale 4→1`，3–5 s，`expo.out`），最后拼出一张大图或文字。
  - 照片墙：倾斜的 3D 平面（`rotateY 20–30°`）匀速横移。
  - Carousel：卡片沿圆环 `rotateY` 匀速或一步一停地转，前面那张放大。
- **证据**：VideoHive [Mosaic Photo Reveal](https://videohive.net/item/mosaic-photo-reveal/7266788) **16K**（AE 全站第 5）、[Photo Gallery on a Sunny Afternoon](https://videohive.net/item/photo-gallery-on-a-sunny-afternoon/3209013) **8K**（第 14）、Multi Video & Multi Text Logo Formation 3.8K、Simple Mosaic 2.7K、Photo Slideshow 3D II 2.2K；Envato Elements Popular 有「Carousel」（2 个）和「Carousel Showreel」；Mixkit 主推「Grid Photo Slideshow」。B 站「[滚动照片墙](https://www.bilibili.com/video/BV1mh4y1P743)」21.5 万（2023）。
- **可行性**：**是**（CSS 3D）。上百个 DOM 层会渲染很慢，改用 canvas 或 WebGL 实例化。

#### K5. Text Behind Subject（文字在人物/物体后面）— A
- **怎么动**：人物或物体抠图放在文字上层，大标题在它后面 `scale 1.2→1` + 淡入（12–16f，`power3.out`），或者从下方滑出，形成「夹心」纵深。动态视频需要逐帧抠像。
- **证据**：Adobe Made Simple「[Text Behind Objects (Premiere)](https://www.youtube.com/watch?v=FpPG_F72i9E)」121.6 万（2023）；Justin Odisho「[Mask Text Behind Objects (AE Rotobrush)](https://www.youtube.com/watch?v=AzqUbzmBK4w)」60.5 万；Dee Nimmin CapCut 版 40.4 万；Smertimba 26.2 万。
- **可行性**：静态图**是**（用 rembg 或 SAM 抠成 PNG）；视频**部分**（要逐帧 matte）。封面和开头钩子很好用。

### F. 图片与照片效果 Image / Photo

#### P1. Photo Drop + Ken Burns（照片落桌 + 慢推）— B
- **怎么动**：照片（白边或拍立得框）从上方或画外落进来：`rotate -12°→-3°`，`scale 1.15→1`，投影由大变小（模拟落到桌面），12–16f，`back.out(1.2)`。之后整段做 Ken Burns：`scale 1.00→1.06–1.10` 加轻微平移（linear）。多张照片叠放时，每张错开 6–10f。
- **证据**：VideoHive Photo Frames Slideshow 3.6K（Openers 第 3）、Photo Gallery on a Sunny Afternoon 8K、Elegant Opener - Photo Opener 2.9K；Mixkit 主推「Photo Frame Slideshow（Polaroid）」；YouTube：Motion Array「[Edit A Documentary Like Johnny Harris](https://www.youtube.com/watch?v=nZrPVUzYHKE)」53.9 万，Dope Motions「[Historic Photo Slideshow](https://www.youtube.com/watch?v=ZxvWQNoMcAU)」38.9 万。
- **可行性**：**是**。

#### P2. Collage / Paper Cutout Boil（拼贴剪纸 + 抖动）— A
- **怎么动**：元素带白色剪纸描边和硬投影；动画用一拍二或一拍三（8–12 fps，按帧切换）。每 2–3 帧随机微抖 ±1–2 px / ±0.5°（boil）。元素出场在 2–3 帧内直接到位（没有中间帧），带 1 帧过冲。上面再叠纸纹。
- **证据**：YouTube：Fakeplastictree「[Motion Graphic | Collage](https://www.youtube.com/watch?v=CMqw9usH8-8)」**203.5 万**（2023），Mapal「[Collage Animation](https://www.youtube.com/watch?v=RdX3yzQDyG4)」50 万（2023），Toby Garrow「Collage Trail」49.4 万，ilkin 44.4 万，Ben Marriott「[Paper Cutout Stop Motion](https://www.youtube.com/watch?v=nwpYl04Cczo)」30.7 万，Motion Street Vox 83.8 万。趋势文章：Videobolt 2026 的「Torn paper / Modular layouts」，Envato 2026 的「Craft as luxury: mixed-media」。
- **可行性**：**是**（`steps()` + 种子抖动；剪纸素材自己做或用自己的 AI 生成）。

#### P3. Whiteboard / Hand-Drawn Reveal（白板手绘揭示）— B（国内 2026 正热）
- **怎么动**：线稿按笔画顺序匀速描出（`stroke-dashoffset`），手或笔的图标跟着笔尖走（与 MotionPath 同步）；画完 3–6f 内填色淡入；镜头随绘制位置平移。
- **证据**：VideoHive Whiteboard Write 2.1K、Meet Mike&Mary Whiteboard 1.8K、Whiteboard Animation Pack 1.4K；Mister Horse 有「Hand Drawn Stuff」包。B 站「[白菜和杜比：同款手绘科普动画分 9 步教会你](https://www.bilibili.com/video/BV1CguN6VEvz)」69.9 万（2026-08-07）；「[为什么你老能刷到 AI 动画科普视频？vibe 动画是什么](https://www.bilibili.com/video/BV1ALnw6YEM7)」**118.1 万**（2026-10-20 发布，11 天内）。Ben Marriott「Hand Drawn Style」45.4 万；Videobolt 2026 有「Hand-drawn visuals」。
- **可行性**：**是**。需要单线的 SVG 线稿；位图插画可以用「擦除式 mask 揭示」近似。

### G. 数据与信息图 Data / Infographic

#### D1. Number Counter / Odometer（数字滚动）— A
- **怎么动**：数值从 0 到 N，1.0–2.0 s，`expo.out` / `power3.out`（起步快、收尾慢），带千分位、单位和小数位格式；落地时配 S1 爆发和 `1.0→1.1→1.0` 弹跳。里程表版：每一位数字是一竖列，用 `translateY` 滚动，低位转得快，各位错开 2–3f。
- **证据**：YouTube：Learnin5「[Animating Numbers Counting Up](https://www.youtube.com/watch?v=RQPwWZuyzZk)」162.6 万，Justin Odisho「[Animated Number Counter](https://www.youtube.com/watch?v=WBLXmZCB9eQ)」56.5 万，Motion Array「Counting Effect」53.8 万，Validation「commas, decimals & symbols」46.3 万。B 站比邻课堂「[AE 数字滚动动画](https://www.bilibili.com/video/BV1VN4y1V73k)」17.7 万。Envato Elements Popular 有「Number Counter」「Counter, Stopwatch, Timer」「Crypto Numbers Animations」；Mister Horse 有「Timers & Counters」包。
- **可行性**：**是**。GSAP 补间数值 + `Intl.NumberFormat`；数字用等宽（`font-variant-numeric: tabular-nums`），防止宽度跳动。

#### D2. Bar / Line Chart Grow（柱状图和折线图生长）— B
- **怎么动**：先画坐标轴和网格线（8–10f）；柱子从基线 `scaleY 0→1`，每根 18–24f，`power3.out`，彼此错开 3–4f；数值标签同步计数；高亮的那根变色并弹一下。折线：路径从左到右描出 1–1.5 s（`power1.inOut`），线头带光点，最后面积填充淡入到 0.2。
- **证据**：VideoHive Infographic Maker 2.6K、Infographics（Holypix）2.2K、Simple Infographics 1.9K、Clean Growth Chart 878、Graphs 3D Cylinder 629、3D Graphs Pack 585；Envato Popular 有「Bar Chart Builder」「Line Chart Infographic」；YouTube：Mapal「[Animate Infographics Like VOX](https://www.youtube.com/watch?v=nHh0NRo8G2U)」34.6 万，SonduckFilm「[Bar Infographics with Controls](https://www.youtube.com/watch?v=0amv44UwAwg)」23.2 万，Move Shapes 20.7 万。
- **可行性**：**是**（SVG / DOM + d3-scale（ISC））。

#### D3. Pie / Donut Ring（饼图和环形进度）— B
- **怎么动**：圆环从 12 点方向顺时针填到 p（`stroke-dasharray`），0.8–1.2 s，`power2.inOut`；多个扇区依次出现，间隔 0.15 s；中心百分比同步计数；高亮扇区向外移 6–10 px。
- **证据**：Envato Popular 有「Infographic Pie Chart 250+」「Polar Area Charts」「Pie Chart Infographics」；YouTube：Move Shapes「[Circular Pie Chart](https://www.youtube.com/watch?v=E0W0Xfm_JIw)」17.6 万，ECAbrams「Easy as Pie Charts」15.5 万，SonduckFilm「5 Infographic Edits」17.5 万。
- **可行性**：**是**。

#### D4. Timeline（时间轴）— B
- **怎么动**：横线从左往右描出，镜头（容器的 x）跟着匀速移动；到达节点时节点 pop（`back.out`），年份和标签上滑。首尾有缓入缓出，中段线性。竖屏改成竖向时间轴。
- **证据**：VideoHive Company Timeline 3.2K（Titles 第 9）；Envato Popular 有「Horizontal Timeline」「Infographics 6 Roadmaps」；Smertimba「[Scrolling Timeline](https://www.youtube.com/watch?v=mxdpl1u6fWY)」23.9 万（2024）。
- **可行性**：**是**。

#### D5. HUD / Tech Interface（科技界面）— A
- **怎么动**：几个同心环按不同的恒定角速度反向旋转（linear 循环，周期 4–12 s）；刻度和数字闪烁（按帧切换）；角标括号 2–4f 弹入；扫描线循环；数据面板逐行打字。
- **证据**：VideoHive [Quantum HUD Infographic](https://videohive.net/item/quantum-hud-infographic/8678174) **5.9K**（AE 全站第 22，Infographics 第 1）、Sci-fi Interface HUD Pack 2.5K、HUD Pack 800+ 869、UI Future Pack 776；Envato Popular 有「HUD Dashboard Infographics」「Techno_hud」「HUD Elements - Targets」；B 站「[600 多个全息 HUD 元素](https://www.bilibili.com/video/BV1zL411p7KR)」12 万。
- **可行性**：**是**（SVG）。提醒：AI 题材用 HUD 很容易显得像廉价的科技模板，要慎用。

### H. 背景与质感 Backgrounds / Textures

#### B1. Texture Layer：Grain / Halftone / VHS（颗粒、半调、录像带质感）— A
- **怎么动**：颗粒以 12–24 fps 刷新（不是每帧都换，才有胶片感），不透明度 4–10%，`overlay` 或 `soft-light` 混合。半调和抖动：按亮度转成点阵或有序抖动。VHS：色度偏移 2–4 px + 扫描线 + 偶尔一条跟踪错误带（1–3f）。
- **证据**：Ben Marriott「[Make ANYTHING Retro](https://www.youtube.com/watch?v=hXtRc84o-WU)」99.6 万，「[Animated Grain Shading](https://www.youtube.com/watch?v=X8JiaUHmdUA)」75.9 万，「[5 Best Ways to Use Noise](https://www.youtube.com/watch?v=okUI3C-0D9E)」54.6 万，「[Instant Dither](https://www.youtube.com/watch?v=3XlO5J7XorI)」30.6 万（2025-04）；Envato Elements「Elements」分类 Popular 第 9 名「Film Grain Overlay Pack」；[Envato 2026 视频趋势](https://elements.envato.com/learn/motion-design-trends)的「Analog nostalgia」（grain、VHS overlays）；Videobolt 的「Analog textures」。
- **可行性**：**是**。预先生成噪声 tile 循环播放，或者 SVG `feTurbulence` 每帧换 seed；半调用 WebGL，或 SVG pattern + mask。

#### B2. Animated Gradient Blobs（流动渐变背景）— B
- **怎么动**：3–5 个大半径、模糊的色块缓慢漂移（周期 8–20 s，`sine.inOut` 往复或李萨如轨迹），背景色相也轻微漂移；叠一层颗粒，防止出现色带。
- **证据**：Ben Marriott「[Easy Gradients](https://www.youtube.com/watch?v=owvcBgc-iLA)」60.1 万、「[Textures / Looping Backgrounds](https://www.youtube.com/watch?v=CqCbwMbidBw)」65.2 万；Envato Elements Popular 有「Gradient Background」；VideoHive Backgrounds 子类有 6,623 个。
- **可行性**：**是**（CSS `radial-gradient` + `filter: blur`，或 WebGL）。

---

## 3. 观察名单（有人气，但这次不排进主表）

| 动效 | 证据 | 为什么没进主表 | 可行性 |
|---|---|---|---|
| Decode / Scramble（乱码解码成文字） | Mister Horse [Text Presets](https://misterhorse.com/products/text-presets/42) 1,414 个，示例名全是 Decode 系列 | 缺独立的播放量或销量 | 是（ScrambleText 加种子） |
| Particle Dissolve（文字被吹散成粒子） | B 站「[AE 粒子文字飘散](https://www.bilibili.com/video/BV1M4411g7Qz)」38.4 万，「[风吹文字](https://www.bilibili.com/video/BV1HJ411P7Tg)」36.3 万；粒子 Logo 3.7K / 3.6K | 讲解类视频很少用 | 部分（canvas 确定性粒子） |
| Smoke / Ink Transition（烟雾、水墨转场） | B 站「[Ae 烟雾转场](https://www.bilibili.com/video/BV19w4m1Z7TF)」166 万；Mixkit「Splash Logo Reveal（Ink）」 | 需要流体素材或模拟 | 部分（WebGL 噪声流体） |
| 透明手机（实拍跟踪） | B 站「[无边框透明手机](https://www.bilibili.com/video/BV1nZ4y1A7tx)」438.5 万 | 依赖实拍和跟踪 | 否 |
| 变装转场（实拍） | B 站「拆解 100 种剪辑手法」330.8 万 | 实拍剪辑手法 | 否 |
| Split Screen（分屏） | Envato Popular「Vertical Split Screen」；SonduckFilm 23.2 万 | 证据偏弱 | 是 |
| Video Inside Text（文字镂空透出视频） | SonduckFilm「5 Quick Text Effects」76.7 万；Mixkit「Video Mask Title」 | 证据偏弱 | 是 |
| Character Explainer Toolkit（角色解说套件） | Pixity Land 7.3K、AinTrailers 3.7K、Explainer Video Toolkit 4 2.5K | 属于角色绑定，不是动效 | 部分（柴犬主持人的骨骼动画可以参考） |
| Logo Sting（片头 logo） | Elegance Flare 6.2K、Logo 3D Levels 4.5K、Particle Reveal 3.6K | 只用在频道片头 | 是 / 部分 |
| Audio Visualizer（音频频谱） | Envato Popular「Audio Visualizer」「Audio Spectrum Pack」；Mixkit 主推 | 讲解类视频少用 | 是（预先算好 FFT） |
| Stretched Text（拉伸字） | Envato 2025-05 文章「the rise of stretched text」；Jake In Motion「stretch text like a BOSS」16.9 万 | 数据少 | 是 |

---

## 4. 趋势佐证（2025–2026）

1. **Envato Elements 当下的 Popular 榜**（2026-10-31）：
   - Titles：Text Match Cut 霸榜，其次是 SaaS / Apple 式干净文字和 Hook & Captions。
   - Elements：手机通知、玻璃质感（Real Glass FX）、镜头运动和抖动转场（≥6 个）、搜索框打字、胶片颗粒、撕纸转场、纪录片风格包（Documentary Style Pack）。
   - Infographics：Match Cut、世界地图、HUD 仪表盘、AI Workflow、SaaS 信息图、计数器。
2. **[Envato 视频趋势页](https://elements.envato.com/learn/motion-design-trends)**（内容提到 2025 年下半年的新品，推断是 2026 版），共 11 条。和动效相关的：
   - Analog nostalgia：颗粒、VHS、复古字体、节奏更慢。
   - Craft as luxury：手绘、定格、mixed media，能看出逐帧质感。
   - **Coded motion**：程序化、生成式、实时响应，例如 ASCII、2D 物理、粒子流，工具是 Cavalry 和开源 creative coding。
   - The end of aspect ratio rules：一个母版适配多种画幅。
   - Minimalistic editing：长镜头、少剪辑。
3. **[Envato 竖屏动效指南](https://elements.envato.com/learn/motion-graphics-for-short-form-video)**（数字已核实）：
   - 钩子按**前 1.5 秒**设计。
   - 文字 `scale 90%→100%` + 快速 ease-out。
   - **不要用静止帧开场**，开场时画面已经在动。
   - 16:9 里 2 秒的揭示，竖屏要压到 **1 秒以内**。
   - 逐词跟口播。
   - 安全区：中间偏上，避开底部 1/4 和右侧互动栏。
   - 30 fps；最佳时长 31–60 秒。
4. **[Videobolt 2026](https://blog.videobolt.net/post/top-motion-graphics-trends-2026)**（2025-12-11）：手绘线条、模拟质感（颗粒、纸纤维、灰尘）、撕纸美学（降帧）、模块化版式（框格、剪切、叠块、粗字块按序进场）、2D/3D 混合、色散和玻璃形体、AI 辅助。
5. **[Motionographer 2025 预测](https://motionographer.com/2024/12/10/motionographers-crystal-ball-2025-motion-design-predictions-part-1/)**：极简动效（大字、留白、少色）、「活的」数据可视化、超写实但超现实的 3D。
6. **[Envato 2025 预测](https://hub.author.envato.com/motion-design-trend-predictions-2025/)**：kinetic typography 和手作「analog」图形被点名。
7. **「代码动画」本身就是趋势**：
   - B 站「[为什么你老能刷到 AI 动画科普视频？vibe 动画](https://www.bilibili.com/video/BV1ALnw6YEM7)」11 天 118 万播放。
   - YouTube MoSidd「[I Made Vox-Style Motion Graphics Using Only Claude Code & Remotion](https://www.youtube.com/watch?v=7wuYBfE131U)」25.1 万。
   - B 站「Claude+Remotion 做地图路线」2.4 万。

   这说明我们这条 HTML 路线正赶上风口；同时也说明同质化会很快，**拉开差距要靠手艺**（缓动、动态模糊、质感层），而不是靠「能动起来」。

---

## 5. 落地时的共性难点（HTML / GSAP / HyperFrames）

1. **动态模糊是「AE 丝滑感」的一半**。AE 的转场和甩镜几乎都开着 motion blur（Videolancer 的更新日志专门写了 *Smoothed Motion Blur*）。HTML 没有原生的动态模糊，可选三种办法：
   - 方向模糊：SVG `feGaussianBlur stdDeviation="x 0"`，按当前速度动态设值。
   - 子帧合成：每帧渲染 N 个子帧再取平均。要看 HyperFrames 是否支持，否则需要后期处理。
   - 2–4 层残影副本，透明度递减。
2. **径向和缩放模糊、镜像边缘、马赛克、折射**：这几样要用 WebGL 片元着色器（runtime 里已有 `world3d.js`，可以复用它的 WebGL 管线）。
3. **确定性**：故障、颗粒、boil 抖动、撕纸锯齿都要用**带种子的伪随机**（例如 mulberry32，按帧号取值），禁止用 `Math.random` 和 `Date`。
4. **GSAP 插件**：SplitText、DrawSVG、MorphSVG、MotionPath、ScrambleText、CustomEase / CustomBounce / CustomWiggle、Physics2D 自 3.13（2025）起全部免费，我们锁定的 3.14.2 在 Standard No-Charge License 下可用。CDN 上每个插件的路径要逐个实测。
5. **AE 缓动换算**（推导）：
   - AE 的 Easy Ease（速度 0，影响 33.33%）≈ `cubic-bezier(0.333, 0, 0.667, 1)`。
   - 动效师常用的「出点 33%、入点影响 90–100%」的强 ease-out ≈ `cubic-bezier(0.33, 0, 0.1, 1)` 到 `(0.33, 0, 0, 1)`，接近 `expo.out`。
6. **9:16 改编**：揭示时长压到 16:9 的一半左右；横向大幅扫动改成纵向；版式重排，不要直接裁切。

---

## 6. 许可提醒

我们只复刻**通用技法**（遮罩揭示、trim path、缩放转场、视差……技法本身不受版权保护），**不碰任何付费模板的设计和素材**。具体：

1. **VideoHive / Envato Elements / Motion Array 的模板**：许可只允许把模板用在你自己做的成片里，**不允许**把它改成可复用的模板或工具再分发。九帽动效是可复用的库，所以：
   - 不导入、不拆解它们的 `.aep` / `.mogrt` / Lottie。
   - 不照着预览视频逐帧描摹版式。
   - 不用它们自带的音效、音乐、字体和图片。
   - 不用它们的产品名给我们的预设命名，例如「Photomotion®」是注册商标，还有「TypoKing」「Stomp」。
   - 买过的模板也不例外。
2. **Animation Composer、Motion Bro 的预设**：属于专有 EULA，处理方式同上。只参考「哪类预设最多、最受欢迎」，曲线自己调。
3. **Video Copilot、Ben Marriott 等教程**：可以学技法；他们的插件（Saber、ORB、Element 3D）和工程文件不能拿来用。
4. **地图和地球图源**：
   - Google Earth / Earth Studio 的影像有署名要求和使用限制。
   - 改用 NASA Blue Marble 和 Natural Earth（都是公有领域）。
   - 用 OpenStreetMap 要按 ODbL 署名。
5. **Apple 风格 / Liquid Glass**：可以用通用的毛玻璃语言；不要用 SF Pro 字体（许可只限 Apple 平台的样机）、Apple 图标或系统 UI 素材。
6. **UI 模拟**：做通用界面，不要仿真微信、抖音、iOS 的品牌界面。真实截图里的他人头像和人脸一律打码。
7. **字体**：只用 OFL 或 Apache 许可的字体（和 `../THIRD_PARTY.md` 一致）。中文笔顺数据（makemeahanzi / hanzi-writer-data）是 Arphic Public License，打包前要核对。
8. **深度模型**：Depth Anything V2 Small 是 Apache-2.0，可以用；Base / Large 是 CC-BY-NC-4.0，频道开始变现后就不能用。
9. **LottieFiles 等素材站**：每个文件的许可不同，没确认之前一律不用。

---

## 附录 A：VideoHive 销量榜原始数据（2026-10-31，各分类第 1 页前列）

**AE 全站**（[链接](https://videohive.net/category/after-effects-project-files?sort=sales)）

| # | 名称 | 销量 | 主要动效 |
|---|---|---|---|
| 1 | Videolancer's Transitions for After Effects | 41.6K | 无缝缩放、旋转、甩、故障、光漏转场 |
| 2 | VoluMax - 3D Photo Animator | 26.4K | 2.5D 照片视差 |
| 3 | Graphics Pack (motioncan) | 26.2K | 2250+ 元素：标题、字条、形状线条、扁平转场、社媒、信息图 |
| 4 | Photomotion - 3D Photo Animator | 26.1K | 2.5D 照片视差 |
| 5 | Mosaic Photo Reveal | 16K | 马赛克拼图揭示 |
| 6 | 140 Flash FX Elements | 14.7K | 卡通特效元素 |
| 7 | TypoKing | 13.4K | 动态排版（28 种风格） |
| 8 | RTFX Generator | 13.2K | 1850 个卡通 FX |
| 9 | AE Face Tools | 12.2K | 实拍人脸工具（与本库无关） |
| 10 | Gold Simple Titles | 11K | 金色简约标题 |
| 11 | Neon Sign Kit | 10K | 霓虹 |
| 12 | Ultimate Earth Zoom Toolkit | 9.5K | 地球推近 |
| 13 | Transitions (RoyalPixels) | 8.9K | 转场 |
| 14 | Photo Gallery on a Sunny Afternoon | 8K | 照片展示 |
| 15 | Pixity Land | 7.3K | 角色解说套件 |
| 16 | Big Pack of Elements | 7.3K | 形状元素 |
| 17 | Instagram Stories | 6.9K | 社媒版式 |
| 18 | Create Pack | 6.6K | 综合包 |
| 19 | 555 Animated Icons | 6.4K | 动态图标 |
| 20 | Lower Thirds (NLTB4540) | 6.3K | 下三分之一字条 |
| 21 | Logo Intro Elegance Flare | 6.2K | 光斑 logo |
| 22 | Quantum HUD Infographic | 5.9K | HUD |
| 23 | Cinematic Parallax Slideshow | 5.4K | 视差幻灯 |
| 24 | Infinity Graphics Pack | 5K | 综合元素 |
| 25 | Pretty Sweet 2D Toolkit | 4.8K | 2D 卡通 |
| 26 | Titles (flikmotion) | 4.6K | 标题 |
| 27 | Logo 3D Levels | 4.5K | 3D logo |
| 28 | Call-Out Titles | 4.5K | 引线标注 |
| 29 | Glitch Transitions | 4.5K | 故障转场 |
| 30 | 210 Text Presets | 4.3K | 文字预设 |

其他分类各自的第 1 名：

| 分类 | 第 1 名 | 其后几名 |
|---|---|---|
| Titles | TypoKing 13.4K | Gold Simple Titles 11K、Neon Sign Kit 10K、Titles 4.6K、210 Text Presets 4.3K、870 Title Animations 4K、Motion Titles Animated 3.8K、Motion Text Maker 3.3K、Company Timeline 3.2K、Stomp 2.8K |
| Openers | Cinematic Parallax Slideshow 5.4K | Kinetic Typography Pack 4.2K、Photo Frames Slideshow 3.6K、Map Route Generator 3.5K、Elegant Photo Opener 2.9K、Corporate Typography Pack 2.8K、Fast Intro 2.6K、Stomp 2 2.5K、Shape Elements 2.5K、Earth Zoom Pro X 2.4K、Whiteboard Write 2.1K |
| Infographics | Quantum HUD 5.9K | 3D Map Kit 3.2K、Infographic Maker 2.6K、Infographics 2.2K、Simple Infographics 1.9K、8 Line Call-Outs 1.8K、Map Kit 1.4K、3D Map Generator 1.2K、World Map Infographic Pro 1.2K |
| Logo Stings | Logo Intro Elegance Flare 6.2K | Logo 3D Levels 4.5K、Multi Video & Text Logo Formation 3.8K、Colorful Particles Logo Reveal II 3.7K、Particle Reveal 3.6K、Flying Through Images 3.2K、Simple Logo Reveal 3.1K、Platinum 3K |
| Product Promo | Pixity Land 7.3K | AinTrailers 3.7K、Instagram Stories 3K、Phone 7 App & Gestures 2.6K、Explainer Video Toolkit 4 2.5K、Book Animation Toolkit 2.4K、iTouch 2 App Promo 2.1K、Minimal Website Presentation 1.9K |
| Transition | Videolancer 41.6K | Glitch Transitions 4.5K、50 Transitions Pack 2.5K、Transitions 2.1K、Paint Brush Transitions 2.1K、Trendy Transitions 2K、Picture Transition 1.9K、Light Transitions & Burns 1.7K、15 Massive Light Transitions 1.7K |
| Lower Third | Lower Thirds 6.3K | Call-Out Titles 4.5K、Lower Thirds 3.2K / 3.1K / 2.9K、Clean Lower Thirds 2.5K、Lower Thirds 2.1K / 1.8K、The YouTuber Pack 3.0 1.7K |
| Elements 总 | Videolancer 41.6K | Graphics Pack 26.2K、140 Flash FX 14.7K、RTFX 13.2K、Earth Zoom 9.5K、Big Pack 7.3K、Instagram Stories 6.9K、555 Icons 6.4K、Lower Thirds 6.3K、Text Messages 3.8K、MoPack 3.6K、3D Earth Connections 3.4K、Liquid Motion Elements 3.2K、World Map Animation 2.8K、Sci-fi HUD Pack 2.5K |

分类规模（侧栏计数）：AE 项目共 120,026；Openers 31,965；Logo Stings 19,656；Elements 19,027（其中 Backgrounds 6,623、Transition 3,317、Lower Third 2,772、Overlay 2,513）；Titles 15,466。

## 附录 B：指定 YouTube 频道播放最高的视频（2026-10-31，yt-dlp 元数据）

| 频道（视频总数） | 前几名（播放，教的动效） |
|---|---|
| Ben Marriott（194） | Learn AE in 10 Minutes 570 万（入门）· Illustrator to AE ft. Burnt Toast 250 万（插画动画流程）· AE in 60 Minutes 180 万 · Animating a YouTube Intro 140.8 万（形状元素 + 转场）· Shape Morph 106.1 万 · 10 Quick Techniques 108.6 万（笔刷纹理、复古印刷、反光、渐隐、形变、轻微 wiggle、发光高光）· 50 Tips 100 万 · Make ANYTHING Retro 99.6 万 · Smooth Transitions 79 万 · Animated Grain 75.9 万 · Textures 65.2 万 · Gradients 60.1 万 · Text Morph 56.8 万 · Cyberpunk Glitch Transitions 54.1 万 |
| SonduckFilm（987） | Cartoon Animation 340 万 · **4 Great Motion Graphics Techniques 321.6 万**（线条、爆发、重复圆）· Top 10 Effects 250 万 · Top 20 Effects 180 万 · Animate Along Custom Path 169.6 万 · 3 Popular Logo Techniques 150 万 · Top 10 Text Presets 142.5 万 · Handwriting 123.7 万 · 3 Popular Transitions 102.8 万（甩镜、色块、遮罩）· 4 Glitch Effects 94.8 万 · 3 Liquid MG 85.4 万 · 5 Quick Text Effects 76.7 万 · 3 Kinetic Typography 69.9 万 · Lower Third 67.5 万 · Stroke Logo 66.7 万 |
| Video Copilot（92） | SABER 400 万 · Crossfire Particle 300 万 · 3D Light Rays 260 万 · Electric FX 200 万 · **Colorful Glitch 198.5 万** · Shockwave 190 万 · **Ultra 3D Earth 189.8 万** · Rain Drop 160 万 · Animated Polygon 110 万 · Grid Experiment 97.6 万 |
| Jake In Motion（345） | Duik Bassel 87.3 万（角色绑定）· Duik Angela 49.1 万 · Tilt-Shift 38.4 万 · ChatGPT in AE 36.5 万 · **Graph Editor 32.3 万**（缓动）· wiggle/random 表达式 23.1 万 · Halftones 16.9 万 · Stretch Text 16.9 万 |
| Motion Design School（284） | Expressions Trip 690 万（课程宣传）· Character Animation 520 万 · Illustrator→AE 流程 86.5 万 · 3D Cube 28.1 万 · Smear & Trails 22.8 万 · Lettering Animation 21.4 万 · Infinite Zoom 16.4 万 · Wiggle Text 15.6 万 |

关键词搜索里其他频道的头部（按播放量）：MDMZ 单图 3D 视差 1171.5 万；Marketing Demons Apple 式文字 206.8 万；Javier Mercedes Earth Studio 207 万；Fakeplastictree Collage 203.5 万；Ignace Aleya 3D 旅行地图 169.5 万；Learnin5 故障 164.2 万、数字计数 162.6 万；Smertimba 平滑文字 153.6 万；Caleb Lancaster 图形揭示文字 145.7 万；Olufemii 10 个转场 126.3 万；Adobe Made Simple 文字在物体后 121.6 万；Cinecom 无限缩放 117.3 万；Karl Shakur Match Cut 111.5 万；Motion Nations 极简线条文字 112.1 万；Bricks 平滑镜头 106.8 万。

## 附录 C：B 站最多播放（order=click，2026-10-31）

| 关键词 | 最相关的头部视频（播放） |
|---|---|
| AE 教程 | 通用课程居多：GenJi 公开课 905.8 万；「透明手机」438.5 万；**「瞳孔穿梭」364.5 万**；**「100 种剪辑手法·变装转场」330.8 万** |
| 动态排版 | 动态歌词排版 898 万 / 563 万 / 460 万 / 378 万 / 293 万（全是歌词 kinetic typography） |
| AE 转场 | 烟雾转场 166 万；神级转场 87.3 万；AE 转场合集 43.4 万 |
| MG 动画教程 | MG 插件推荐 162.4 万；5 个动画原理 135.9 万；拿捏鸭鸭 MG 129.4 万；MG 基础课 60 万 |
| AE 文字动画 / 文字动画教程 | Pr 文字手写 46.6 万；超级常用文字动画 44 万；文字进场 43 万；100 个文字小动效 40.9 万（4.5 万收藏）；文字动效原来这么简单 63.2 万 |
| AE 故障 | 故障干扰特效 38.9 万；故障 LOGO 20.7 万 |
| AE 卡点 | AE 变速卡点练习 173.4 万 |
| AE 打字机 | PR 打字机 54.4 万；AE 流畅打字 17.6 万 |
| AE 照片墙 | 滚动照片墙 21.5 万；照片墙汇聚 LOGO 16.5 万 |
| AE 数字滚动 | AE 数字滚动动画 17.7 万 |
| AE 毛玻璃 | 毛玻璃卡片动效 15.5 万；商用级毛玻璃 MG 10.3 万 |
| AE 视差 | doyoudo 三维视差 10.4 万 |
| AE 粒子 | 粒子文字飘散 38.4 万；风吹文字 36.3 万 |
| 科普动画 | 「AI 动画科普视频 / vibe 动画」118.1 万（2026-10-20）；「白菜和杜比 手绘科普」69.9 万（2026-08） |
| AE 地图路线 | 飞机路线地图 6.9 万（这个题材在 B 站整体播放偏低） |

**国内和海外的差别**：B 站上播放最高的是**转场类**（瞳孔穿梭、变装、烟雾）和**歌词动态排版**；纯 MG 元素（形状、图表、字条）的教程播放普遍只有几万到二三十万，远低于 YouTube 同类。图表和信息图在两边都不是流量大户，但在 VideoHive 上一直有稳定销量，说明是「刚需工具」，不是「爆款看点」。
