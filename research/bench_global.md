# 海外讲解 / 口播 / 视频随笔：包装与动效基准（bench_global）

调研日期：2026-10-31 ｜ 用途：给「九帽动效」（hat9-motion，HTML+GSAP → MP4）定 8–10 个风格族 ｜ 频道：第九顶帽子（AI 时代的判断力与审美；无脸；高帽柴犬主持；16:9 为主，9:16 为辅）

> **方法与边界**
> - 只用 WebSearch / WebFetch 读文字资料（采访、幕后、设计系统、教程摘要、招聘描述），**没有下载任何视频或媒体文件**，没有调用付费 API。
> - 证据分三级，正文逐条标注：
>   - **【源】**：创作者本人 / 官方 / 一手采访或官方仓库可查到的说法（编号见文末来源表）。
>   - **【二手】**：第三方教程、工具厂商博客、AI 摘要页。方向可信，细节可能错。
>   - **〔未核实〕**：基于长期观看的经验观察或估计值，没有找到文字来源；做风格包之前必须自己拉片核对（数镜头时长、取色、认字体）。
> - 公开资料普遍**不写**具体色值、字号、镜头时长。所以本文多数"可测量特征"都是〔未核实〕的估计区间；凡是有出处的数字都单独标了【源】。
> - 用户点名的「Kurzgesagt *In a Nutshell* 风格指南演讲」：**没有找到**公开的官方风格指南或演讲，只找到官方流程页和一篇流程报道（[1][2]）。

---

## 0. 速览：保留谁、删掉谁、各自锚定哪个风格族

| # | 创作者 | 判定 | 锚定风格族 | 一句话：包装为什么好 |
|---|---|---|---|---|
| 1 | Kurzgesagt | **保留（核心）** | I 吉祥物卡通 | 抽象概念全部变成发光扁平世界里的小生物、小机器在"做事" |
| 2 | Vox（Joss Fong / Earworm / Atlas） | **保留（核心）** | A 杂志编辑；B 证据桌 | 记者式"指着证据说话"：旁白说"这个"，画面就高亮这个 |
| 3 | Johnny Harris | **保留（核心）** | B 证据桌拼贴 | 把调查过程拍成能摸到的桌面：打印纸、红笔、地图、胶片 |
| 4 | Cleo Abram（Huge If True） | 保留 | I（主持人代理） | 替观众问最笨的问题，再用定制 3D 和道具把答案演出来 |
| 5 | PolyMatter | 保留 | G 数据地图 | 安静、扁平、几何化的地缘经济图解，一句话对应一张干净的图 |
| 6 | Wendover / Half as Interesting | 保留 | G；J（HAI） | 系统类话题用地图加流程图讲清；HAI 用冷幽默快剪 |
| 7 | LEMMiNO | **保留（核心）** | D 暗场极简纪录 | 黑底、大量留白、电影感 3D 加自作配乐，用克制制造悬疑 |
| 8 | Veritasium | 保留（只借结构） | 横切：钩子 | 先让观众答错，再推翻误解 |
| 9 | 3Blue1Brown | **保留（核心）** | H 图解推导 | 每个动作都有目的；同一个概念全片用同一种颜色 |
| 10 | **Welch Labs**（新增） | 保留 | H；B | 把 AI 内部计算画在纸上、做成 3D，像侦探一样推进 |
| 11 | Fireship | **保留（核心）** | J 终端梗剪 | 不说废话；1–5 秒换一个视觉；冷笑话推着信息走 |
| 12 | AI Explained / Two Minute Papers | 保留（降级） | J（文档截图） | 用论文、推文截图做证据，克制不炒作 |
| 13 | Ali Abdaal | 保留 | F（克制字幕款）；A | 干净的逐词变色字幕、灰底上的局部彩色、纸张音效 |
| 14 | Alex Hormozi + Submagic / Captions | **保留（字幕核心）** | F 动态大字 | 1–3 个词一页，关键词变色、放大、弹出 |
| 15 | MrBeast | 保留（只借字幕和钩子） | 横切 | 第一分钟兑现缩略图的承诺；高能字幕 |
| 16 | Dan Koe | 保留 | F（单色线条） | 纯黑白，只用简单形状和字，靠弹性节奏和匹配剪辑撑起来 |
| 17 | Apple 发布会 / 产品片 | **保留（核心）** | E 发布会展陈；F | 黑底，画面里只有一个东西有颜色，剪辑看不出来 |
| 18 | Vercel Ship / Linear / Stripe | 保留 | E | 暗色、UI 卡片悬浮、一套品牌动效语法 |
| 19 | The Economist / FT / Bloomberg / NYT Visual Investigations | **保留（核心）** | G 数据；B 证据 | 图表标题直接写结论；红色限量用；证据可以逐帧复核 |
| 20 | Pursuit of Wonder | 保留 | C 胶片随笔 | 抽象定格拼贴、颗粒感、慢速哲思 |
| 21 | Nathaniel Drew | 保留 | C 胶片随笔 | 胶片颗粒、暖调、日记体文字、第一人称反思 |
| — | MKBHD | **降级为参考** | （E） | 精品实拍棚拍（机械臂运镜、红色点缀）；对无脸 2D 动效可迁移的东西少 |
| — | Ryan Trahan | **删除（只借钩子）** | — | 实拍 vlog 叙事；只借"目标、赌注、倒计时"这个钩子 |
| — | The Pudding（视频） | **删除** | — | 视频产出很少；只借"一步一个状态"的滚动叙事原则 |

---

## 1. 逐个创作者拆解

字段固定为：链接｜一句话｜调色｜字体｜文字密度｜镜头时长/剪辑率｜每句话怎么可视化｜转场｜2D 镜头运动｜音效/音乐密度｜字幕｜前 5 秒钩子｜招牌手法｜风格族｜证据。

### 1.1 Kurzgesagt – In a Nutshell
- 链接：https://www.youtube.com/@kurzgesagt ｜流程页 https://kurzgesagt.org/youtube/
- 一句话：每个抽象概念都被翻译成一个会动的角色或物件隐喻，画面永远在"做事"，不在"摆字"。
- 调色：深色宇宙底（深靛、深紫蓝，约 #0E1638–#1E1B4B）＋ 2–3 个高饱和点缀（橙黄、洋红、青绿）；大量渐变高光和发光边〔未核实〕。有人在 Adobe 论坛拆过：发光边可能是渐变叠加 Color Dodge 混合模式，或 Illustrator 的 Inner Glow 做的【二手】[4]。
- 字体：画面上的字极少；标题卡用圆润的粗体无衬线〔未核实〕。
- 文字密度：极低。屏幕上的字基本只有数字、标签，或单个词〔未核实〕。
- 镜头时长：场景约 3–6 s，但每句话都在一个持续的镜头运动里，所以"静止感"接近零〔未核实〕。第三方模板把它总结为"每句话一个镜头运动"【二手】[3]。
- 每句可视化：隐喻优先（免疫细胞＝士兵、线粒体＝小人）；尺度对比用穿越尺度的缩放；数字用计数器【源】：官方说风格来自"矢量插画、像素插画和信息图"，"先敲定视觉隐喻和场景，再画"[1]。
- 转场：镜头穿进物体（zoom-through）、形状变形、同色背景擦除〔未核实〕。
- 2D 镜头：多层视差的慢推慢移，配合"2D 扁平动画＋3D 元素"【源】[1]。
- 音效/音乐：每集由 Epic Mountain 专门作曲【源】[1]；音效细，几乎每个物体动作都有拟音〔未核实〕。
- 字幕：不烧字幕，只有 CC〔未核实〕。
- 前 5 秒：直接抛一个宏大问题或反直觉判断（"如果……会怎样"），画面一开始就在动〔未核实〕。
- 招牌：小鸟吉祥物、豆豆眼小人、穿越尺度的推拉、发光扁平。
- 产量数据【源】[2]：一集约 1200 小时；约 200 张草图；2–3 名插画师画 8–12 周（Illustrator）；2–3 名动画师做 8–12 周（After Effects＋Cinema 4D）；旁白一段一段录；音乐和音效最后加；剧本要改十几稿[1]。
- 风格族：**I 吉祥物卡通**。

### 1.2 Vox（Joss Fong、Estelle Caswell / Earworm、Vox Atlas）
- 链接：https://www.youtube.com/@Vox
- 一句话：记者式"指着证据说话"。每句旁白在屏幕上都有一个具体的指向对象（档案、被高亮的句子、地图、图表）。
- 调色：纸白或米色底、黑字、品牌黄 #FFF200（第三方从 vox.com 网站提取：黄色只作底块，不作文字色）【二手】[9]；视频里常见黄色马克笔高亮〔未核实〕。
- 字体：Balto（Type Supply / Tal Leming 设计，美式 gothic 无衬线），用来传达"懂行的朋友"的语气【二手】[9]；网站正文用 Harriet 衬线，标签用 Roboto Mono 大写【二手】[9]。
- 文字密度：中。关键词、档案引文高亮、地图标签〔未核实〕。
- 剪辑与动效【二手·第三方教程】[6]：
  - 图形合成按 **12fps** 做和渲染，放进 24fps 时间线，形成"顿挫感"；
  - 文字层比底块**晚几帧**进入；
  - 纸张纹理背景：5–6 张纹理轮换，**每秒出现 2–3 张**（纹理"抖动"）；
  - 转场：两段画面作为 3D 图层，相机后拉或前推，配合**短于镜头运动的高斯模糊**峰值，对准剪辑点；
  - 照片和剪报边缘加轻微色差和羽化模糊（模拟镜头）。
- 每句可视化：档案＋高亮、地图、图表、Google Earth Studio 飞行镜头（Fong："不要太疯，但要给作品带来能量"）【源】[5]。
- 音乐【源】[5]：用 APM 曲库按关键词找曲子；**大约每 20 秒换曲或改编一次**；曲子的起止当作"情绪提示"和"注意力提示"，标记段落和重点；避免和人声音高打架的乐器；开头需要"节奏很快的东西"。
- 写稿【源】[5]：旁白比印刷稿更直白（"不能太聪明、太漂亮"）；常用指示语 "This is…" / "Look at this"；用 "That's right" 这类停顿让观众消化；段落结尾＝一句小结＋音乐收尾。
- 前 5 秒 / 结构【源】[5]：黑洞那集**先不给照片**，先讲"地球那么大的望远镜"有多难，最后才揭晓。Fong："我不想让照片成为观众看到的第一样东西"。
- Earworm【源】[7][8]：音乐可视化，"只要有一个词不在拍上，整个东西就塌了"——画面严格对拍。故事编辑会检查剧本"是否可视"："视频的意义就是你在谈论屏幕上的东西"。
- 招牌：黄色高亮、纸张纹理、12fps 图形、档案上的手写标注、Google Earth 推进。
- 风格族：**A 杂志编辑**（主）＋ **B 证据桌**（次）。

### 1.3 Johnny Harris
- 链接：https://www.youtube.com/@johnnyharris
- 一句话：把"我在查"这件事本身拍成可触摸的桌面，观众像跟着他一起翻档案。
- 调色：暖黄纸张（约 #E9DFC9）＋ 去饱和的黑白档案 ＋ 唯一的红笔标注色（约 #D1281F）＋ 地图上的少量饱和色〔未核实〕。
- 字体：打字机或等宽字体做标签，粗体无衬线做标题〔未核实〕。
- 文字密度：中。档案原文里高亮一句，地图上的地名标签〔未核实〕。
- 镜头时长：快，约 2–4 s；读证据时会停 5 s 以上〔未核实〕。
- 每句可视化：**实物纸张道具放在桌上，用有创意的机位拍**，叠在口播画面上；致敬黑白片和胶片盘【二手】[10]；地图用 GEOlayers 插件【二手·页面标题】[11]。
- 转场：胶片烧、漏光、电视信号扭曲（TV warble）、地图 3D 倾斜后俯冲【二手·仿制教程标题】；论坛建议的同类做法：漏光叠加＋饱和度＋颗粒、灰尘划痕、纸纹、混合模式叠两层【二手】。
- 2D 镜头：在纸面上推拉；地图先倾斜再俯冲；路线描线〔未核实〕。
- 音效：密。纸张、打字机、放映机、whoosh 几乎每个动作都有〔未核实〕。
- 字幕：不烧字幕；屏幕上的字是"道具上的字"〔未核实〕。
- 前 5 秒：本人对镜头抛出个人经历或一份"我找到的文件"＋悬念〔未核实〕。
- 招牌：桌面俯拍证据、红笔圈画、地图俯冲、胶片质感、画幅变化〔未核实〕。
- 风格族：**B 证据桌拼贴**。

### 1.4 Cleo Abram — Huge If True
- 链接：https://www.youtube.com/@CleoAbram
- 一句话：乐观的"好奇代理人"。她替观众问最简单的问题，再用定制 3D 和实物道具把答案演出来。
- 流程与团队【二手·Colin and Samir 访谈摘要】[12]：
  - 4 人团队（主持、动画师兼主制片、科学制片、剪辑）；
  - **三栏脚本**：每句话一行，三列分别写音频、画面、来源；
  - 选题清单第一条是"有没有视觉潜力"；
  - **刻意放弃了 Tron 式配色**（黑、银、霓虹紫绿），自己定义节目的样子；
  - 主持人当"观众代理"，会拍自己的笨拙时刻；
  - 开场先露脸，前 30–50 秒用好奇缺口；
  - 剪辑负责"情绪起伏"，把 vlog 感和讲解感揉在一起。
- 调色 / 字体：明亮乐观、白底或实景＋粗体白字〔未核实〕。
- 镜头时长：口播 3–6 s，3D 段落更长〔未核实〕。
- 对我们的意义：柴犬＝观众代理。"三栏脚本"直接变成九帽的 beat 表（台词｜画面｜来源）。
- 风格族：**I 吉祥物卡通 / 主持人代理**。

### 1.5 PolyMatter
- 链接：https://www.youtube.com/@PolyMatter
- 一句话：安静、扁平、几何化。每句话对应一张干净的图标化图解。
- 调色：中性或深色底、低饱和国家剪影、1 个强调色（常见橙或红）〔未核实〕。
- 字体：干净的几何无衬线；标签小，极少整句〔未核实〕。
- 镜头时长：稳定的 4–6 s；图解按句子逐步累积〔未核实〕。
- 每句可视化：图标、箭头、国家剪影、简单柱图；很少用实拍〔未核实〕。
- 转场：同底色上元素进出，平推〔未核实〕。
- 音效：低。音乐平稳〔未核实〕。
- 前 5 秒：一个反常的数字或对比〔未核实〕。
- 风格族：**G 数据地图**。
- 说明：没有找到幕后资料，以上都是观察。

### 1.6 Wendover Productions / Half as Interesting（Sam Denby）
- 链接：https://www.youtube.com/@Wendoverproductions ｜ https://www.youtube.com/@halfasinteresting
- 一句话：Wendover 用地图、流程图和库存镜头把"系统"（物流、航空）讲清；HAI 用冷幽默快剪讲冷知识。
- 【源·二手摘要】[39]：Sam Denby 近 11 年保持双周一更；后来招了后期团队；HAI 是为了团队化而拆出来的。
- Wendover〔未核实〕：低饱和卫星或扁平地图底＋路线、节点；统计数字直接上屏；镜头 3–5 s；音乐轻。
- HAI〔未核实〕：1.5–3 s 一个画面；库存素材加反差字幕；一句一梗。
- 风格族：Wendover → **G**；HAI → **J**。

### 1.7 LEMMiNO
- 链接：https://www.youtube.com/@LEMMiNO ｜ https://lemmi.no/faq
- 一句话：黑底、留白、电影感 3D 与排版，加上自己做的配乐，用"克制"制造悬疑。
- 工具链【源】[13]：剧本用 Sublime Text、Obsidian、Google Docs；静态图 Photoshop；动态图 After Effects；3D 用 Cinema 4D（有时 Blender），实时 3D 用 Unreal Engine；音乐和音效用 FL Studio / Ableton（部分音乐自己作曲并单独发布）；剪辑用 Premiere（有时 DaVinci）。
- 调色：近黑底（约 #0A0A0B–#121212）＋ 单一冷色或琥珀色强调，面积不到 10%〔未核实〕。
- 字体：大写、宽字距的细到中等字重无衬线；章节标题卡〔未核实〕。
- 镜头时长：长，约 6–12 s；慢速 3D 推拉或环绕〔未核实〕。
- 每句可视化：极简 3D 场景、点阵或线框地图、档案照片放在黑场里〔未核实〕。
- 转场：黑场、慢溶解；几乎没有花哨转场〔未核实〕。
- 音效/音乐：合成器铺底＋低频；音效极少，只在揭示处用〔未核实〕。
- 前 5 秒：冷开场，一句悬念旁白配黑场里的一个物件〔未核实〕。
- 风格族：**D 暗场极简纪录**。

### 1.8 Veritasium（Derek Muller）
- 链接：https://www.youtube.com/@veritasium
- 一句话：用"误解"开局：先让观众心里给出一个错误答案，再用实验和动画推翻它。
- 【源·二手摘要】[38]：标题和缩略图要反复测试迭代（"Clickbait is Unreasonably Effective"）；要火，点击率和观众留存缺一不可；误解贯穿开头几秒、标题、缩略图和措辞；叙事吸引注意，但数字和证据必须站得住。
- 包装〔未核实〕：实拍演示加外包 2D/3D 动画；字幕不烧录；动画段多是干净的图解。
- 前 5 秒：一个问题或演示："你觉得会发生什么？"〔未核实〕。
- 风格族：横切，作为**钩子结构**的基准，不当视觉锚。

### 1.9 3Blue1Brown（Grant Sanderson）
- 链接：https://www.youtube.com/@3blue1brown ｜ https://www.3blue1brown.com/faq/
- 一句话：每一个动作都有目的；视觉强化旁白而不是和旁白抢；同一个概念全片同色。
- 设计原则【源】[14]：几乎所有动画都用自研的 Manim；屏幕上的每个运动都要刻意、有可识别的目的；视觉强化旁白、不竞争；避免"公式或文字无目的地乱动"；Manim 只做片段，最后在剪辑软件里拼；不建议在 Manim 里对旁白。
- 参数【源】[15][16]：3b1b 视频仓库配置为**背景 #000000、字体 CMU Serif、30fps、3840×2160**；manimlib 默认背景 #333333、默认字体 Consolas。官方色板（_C 档）：BLUE #58C4DD、TEAL #5CD0B3、GREEN #83C167、YELLOW #FFFF00、GOLD #F0AC5F、RED #FC6255、MAROON #C55F73、PURPLE #9A72AC、GREY #888888（每色有 _A 到 _E 五档深浅）。
- 音乐【源】[14]：Vincent Rubinetti 作曲。
- 镜头时长：长，5–15 s，画面元素逐步累积，不跳切〔未核实〕。
- 每句可视化：公式和图形的变形（Transform）、高亮（Indicate）、画圈（Circumscribe）、逐个错峰进入（LaggedStart）；圆周率小生物做反应〔未核实〕。
- 音效：几乎没有；音乐低〔未核实〕。
- 字幕：不烧录〔未核实〕。
- 前 5 秒：一个漂亮的问题或谜题画面〔未核实〕。
- 风格族：**H 图解推导**。

### 1.10 Welch Labs（新增，2025–2026 AI 讲解标杆之一）
- 链接：https://www.youtube.com/@WelchLabsVideo
- 一句话：把神经网络内部的计算"摊开来给你看"：实体纸张打印、手绘标注、3D 渲染，加上侦探式推进。
- 【源·标题级】[42]：Grant Sanderson 曾录过帮 Stephen Welch 上手 Manim 的会话（会员帖，内容未读到）。
- 包装〔未核实〕：纸张打印的矩阵和激活图放在桌面上，加深色 3D；节奏慢、悬疑叙事；数字精确。
- 风格族：**H 图解推导**＋**B 证据桌**混合。对"AI 判断力"题材很对路。

### 1.11 Fireship（Jeff Delaney）
- 链接：https://www.youtube.com/@Fireship
- 一句话：零废话。1–5 秒换一个视觉，冷笑话推着信息走，一屏只讲一行代码。
- 工作流【二手·其本人讲解视频的摘要】[17]：
  - 不写完整剧本，**一句一句**分段录音，剪好整条旁白后再上画面；
  - 屏上图形通常停 **1–5 秒**，用来强化刚说的话；
  - 代码不拍实时打字：先倒序删掉，再按 Ctrl+Z 录屏；讲某一行时用冻帧；看不明白的行加 emoji 或图注，让暂停的观众也能看懂；
  - **最用心打磨前 60 秒**；面向中高级观众，跳过基础；
  - 静态图用 Figma，图标和 emoji 来自 FlatIcon，GIF 来自 Giphy（注意版权），复杂动画在 After Effects 里做成短片段再导入 Premiere。
- 调色：深色代码面板＋橙黄火焰品牌色＋青色强调〔未核实〕。
- 字体：等宽代码字体＋粗体无衬线标题〔未核实〕。
- 镜头时长：约 1–3 s，"100 秒讲清 X"格式【二手】。
- 转场：硬切为主；梗图插入 ≤1 s；偶尔 whoosh 推移〔未核实〕。
- 音效：中高。每个梗一个音效〔未核实〕。
- 前 5 秒：一句冷嘲＋直接定义"X 是一个……"，没有片头〔未核实〕。
- 风格族：**J 终端梗剪**。

### 1.12 AI Explained / Two Minute Papers
- AI Explained：https://www.youtube.com/@aiexplained-official ，自称 "AI, without the hype"，以拆解论文和基准测试见长，被评价为"更清醒、分析型"【二手】[41]。包装：论文、推文截图加高亮框，平静旁白，剪辑极简〔未核实〕。
- Two Minute Papers：https://www.youtube.com/@TwoMinutePapers ，固定开场 "Dear Fellow Scholars, this is Two Minute Papers with Károly Zsolnai-Fehér"【源】[40]；作者讨论过术语解释用"简介栏词典"还是"画面叠字"【源】[40]。包装弱：论文结果素材循环播放加旁白〔未核实〕。
- 只借两点：①截图证据要带来源标签和高亮框；②固定开场的仪式感。
- 风格族：**J**（文档截图支线）。

### 1.13 Ali Abdaal
- 链接：https://www.youtube.com/@aliabdaal
- 一句话：干净、克制的生产力美学：灰底上的局部彩色、圆角卡片、逐词变色字幕、纸张音效。
- 【二手】[22]：字体 Inter 或 TT Fors；字幕"逐词出现，同时伴随颜色动画"，说完的词渐变成另一色（原文 "fades into black"，推测是浅底字卡）；没有漂浮和旋转动画。另一工具站描述为灰度背景上的选择性彩色、手写风字幕。仿制教程提到纸张撕裂转场、纸张揉搓和 whoosh 音效、半调背景。
- 镜头时长：口播 2–4 s 跳切，B-roll 和文字卡穿插〔未核实〕。
- 风格族：**F 动态大字**（克制字幕款）＋ **A**。

### 1.14 Alex Hormozi ＋ Submagic / Captions 类工具
- 链接：https://www.youtube.com/@AlexHormozi ｜ https://www.submagic.co
- 一句话：短视频字幕的"工业标准"。一页 1–3 个词，关键词变色、放大、弹出，字本身就是画面的节奏。
- 规格见 §3 字幕配方。
- 风格族：**F 动态大字**。

### 1.15 MrBeast
- 链接：https://www.youtube.com/@MrBeast
- 【源·泄露内部文档，真实性有争议】[18]："第一分钟要抓住注意力，并**证明缩略图的期待会被满足**"；6000 万点击在第一分钟流失 2100 万"算不错"；1–3 分钟、3–6 分钟、6 分钟到结尾各有明确职责；标题和缩略图设定期待，后面一切都要围绕它。
- 字幕规格见 §3。
- 风格族：横切（钩子＋高能字幕）。

### 1.16 Dan Koe（及"Dan Koe 风"极简动画）
- 链接：https://www.youtube.com/@DanKoeTalks
- 一句话：纯黑白，只用简单形状和字。靠弹性节奏、匹配剪辑和形变撑起高级感。
- 规格【二手·仿制教程】[25]：
  - 严格黑底白元素；
  - 实心物体白填充无描边，线框和效果用约 3px 白描边（书本轮廓约 10px）；
  - 24fps、竖屏 1080×1920；主动作约 **12 帧一拍**；后续道具错开几帧依次到达；
  - 弹性"啪"地停，不要滑行：缓动手柄要短，加惯性回弹和 overshoot；
  - 元素从 0 缩放弹入弹出；线框用阶梯式闪烁（0→30→70→100% 不透明度）；
  - 转场：两层在形状重合的那一帧切换（匹配剪辑）；圆变方的形变；随机速度线飞过；
  - 可选：posterize time 约 12fps 做顿挫感；辉光只给关键元素（如灯泡）；粒子极少、高对比。
- 风格族：**F 动态大字 / 单色线条**。

### 1.17 Apple 发布会与产品片
- 链接：https://www.youtube.com/@Apple
- 一句话：黑底，画面里只有一个东西有颜色；一个镜头一个想法；剪辑看不出来。
- 【二手】[26]：背景纯黑或纯白；颜色只在中心的产品或 UI 上，四周留空；不在同一帧叠多种特效；剪辑接近隐形；音乐高级且锁拍；音效稀少，只打关键点、音量低、不和画面抢；全片最多用一两款品牌字体，规则统一。
- 【二手】[27]：SF Pro 的授权只允许在 Apple 平台上开发软件，**不能用于营销或品牌视频** → 我们必须用替代字体。
- 【二手】[28]：keynote 里大量"不可察觉"的过渡（从剧院地板落入地下实验室；从相机模组特写推到 Apple Park）。
- 大字卡〔未核实〕：一卡 1–3 个词，字号占画面宽度 40–70%，字重 600–700，字距收紧；偶尔用渐变或金属质感填字；进场多为上移＋淡入，约 0.6–0.9 s，expo 缓出。
- 风格族：**E 发布会展陈**＋**F**。

### 1.18 Vercel Ship / Linear / Stripe
- Vercel Ship 2025【源】[29]（外包给 Basement Studio）：视觉身份围绕"liquid（液态）"概念；角色动画**一拍二（每个姿势停 2 帧，约 12fps 节奏），相机和环境保持 24fps**；人物和物体统一成黑色剪影材质；暖调分级；先出预渲染检查节奏、增删镜头，再出 EXR 分层合成。
- Vercel 官方开源的 create-remotion-geist 技能：暗色主题、Geist 字体、官方色板、弹簧动画【二手】[30]。
- Linear【源·招聘】[31]：内部招 Motion Storyteller，要求"让我们的 UI 活起来的动态图形"。观察：近黑底（约 #08090A）、细微渐变光晕、UI 卡片带 3D 透视悬浮、慢而精确〔未核实〕。
- Stripe【源·招聘】[32]："动效是我们让品牌活起来的核心，从活动舞台到数字营销"。观察：标志性的流动渐变网格（blurple 约 #635BFF）〔未核实〕。
- 风格族：**E 发布会展陈**。

### 1.19 新闻编辑部图形：The Economist / FT / Bloomberg / NYT Visual Investigations
- The Economist【源】[33]：2017 年图表风格指南（v1.2）规定图表标题、标签、坐标轴用 **Econ Sans Condensed** 的各个字重；品牌主字体 Econ Sans，小字号正文用 Milo。红色多被第三方记为 #E3120B，并说红色"按配给使用，作规则线而非大面积填充"【二手】。
- FT【源】[34]：视觉故事团队由编辑、设计师、2 名图形记者、2 名记者组成，另有视觉调查小组。招聘描述：做动态图形、3D 动画和"视觉主导的讲解"。FT 纸色约 #FFF1E5、claret 约 #990F3D〔未核实，记忆中的 Origami 色板，仓库路径未取到〕。
- Bloomberg Quicktake【源】[35]：由 Territory Studio 做的动态包装系统（片头卡、过场、插页）；有说法是黑或深蓝底配白、黄字〔未核实〕。
- NYT Visual Investigations【源】[36]：几乎每个故事都用卫星图；逐帧核对；3D 重建现场；拼出详细时间线；"切面图形＋地图＋动态影像"。
- 可迁移：①**图表标题＝结论句**；②红色和强调色限量使用；③证据要能复核（时间码、来源、坐标标签）；④时间线和地图是"证据的坐标系"。
- 风格族：**G 数据地图**＋**B 证据桌**。

### 1.20 Pursuit of Wonder
- 链接：https://www.youtube.com/@PursuitofWonder
- 一句话：用抽象、颗粒感的定格拼贴讲哲思，慢、深、旁白低沉。
- 【二手】[10]：抽象定格动画、大胆用色（作者说自己做会降饱和）、图层多、独特素材多、很耗时。论坛建议颗粒或粒子层做一次带 alpha 的素材反复叠用【二手】[43]。
- 镜头 5–10 s；字极少；钢琴或环境乐〔未核实〕。
- 风格族：**C 胶片随笔**。

### 1.21 Nathaniel Drew
- 链接：https://www.youtube.com/@NathanielDrew
- 一句话：胶片颗粒、暖调、日记体文字、第一人称反思的"慢视频"。
- 〔未核实〕：16mm 或超 8 颗粒；高光偏暖；手写或打字机字体做小号叠字；钢琴或原声吉他；镜头 3–6 s；交叉溶解。
- 风格族：**C 胶片随笔**。

---

## 2. 横切数据：剪辑节奏有没有可靠的数字？

- 唯一找到的量化数据来自一个剪辑工具的样本（33 条 3–20 分钟的旁白类长视频，共 4412 个镜头）【二手】[37]：
  - **镜头时长中位数 3.62 s**（P10 1.54 / P25 2.30 / P75 5.25 / P90 7.46 s）；
  - 62.7% 的镜头在 2–6 s；只有 1.3% 超过 12 s；
  - **前 30 秒中位数 3.1 s，之后 3.7 s**：开头略密，不是暴快；
  - 建议区间：钩子 2–4 s｜普通无脸旁白 3–5 s｜密集讲解 3–6 s｜纪录叙事 4–7 s｜**关键照片或证据 6–10+ s｜要读的图表 5–12+ s**；
  - 作者的警告：剪辑次数≠视觉变化。应该数"**每分钟有意义的视觉变化**"；频繁切换相似图片会显得又静又乱。
- 和标杆交叉核对：Fireship 图形停 1–5 s【二手】[17]；Vox 约每 20 s 换一次音乐【源】[5]；Kurzgesagt 每句一个镜头运动【二手】[3]。
- 结论：九帽的默认值定为"**每 3–5 s 一次有意义的视觉变化，前 30 s 快 15%，证据和图表按阅读量放宽到 5–12 s**"，按风格族上下浮动（见 §5）。

---

## 3. 综合（1）：优秀者共有的 10 条规则

1. **先有画面再定稿，每句话都有画面计划。** Cleo 用三栏脚本（台词｜画面｜来源）[12]；Vox 的故事编辑专门查"可视性"[7]；Kurzgesagt 先定视觉隐喻再画[1]。→ 九帽的 beat 表必须每行都有 `visual` 字段，空着就不许渲染。
2. **一个画面一个想法，每 3–5 s 一次有意义的变化。** 镜头中位数约 3.6 s[37]；Apple"一个镜头一个想法"[26]；Fireship 1–5 s[17]。"变化"可以是推进、高亮、新元素，不一定是硬切。
3. **指哪说哪。** 旁白说"这个"的那一刻，画面要用高亮、圈、箭头、放大指向它。Vox 的 "This is… / Look at this"[5]，3b1b 的 Indicate 和 Circumscribe，Johnny Harris 的红笔。
4. **系统一致，克制配给。** 字体 ≤2 族（Apple 一两款[26]）、强调色 1 个（Economist 红色配给、Vox 黄只作底块[9]）；同一概念全片同色（3b1b）。
5. **每个动作都有目的。** 3b1b："屏幕上每个运动都要刻意、有可识别的目的"[14]。不用漂浮、随机粒子或无意义的 wiggle 冒充丰富。
6. **延迟揭示，先建立难度或误解。** Fong 不先给照片[5]；Veritasium 从误解开始[38]；MrBeast 第一分钟兑现承诺[18]。前 5 s 给问题，前 30 s 给"为什么值得看"，结论放到中后段。
7. **声音就是结构。** 音乐的起止标记段落和重点，约 20 s 变化一次，避开人声频段[5]；Apple 锁拍、音效稀少[26]；Kurzgesagt 每集原创配乐[1]。音效永远绑在一个看得见的动作上。
8. **一个风格一个质感层，全片不换。** Vox 的纸纹每秒抖 2–3 次[6]；Johnny 的纸张和胶片；Pursuit 的颗粒；Kurzgesagt 的发光。质感层是"统一画面的胶水"。
9. **帧率和缓动有性格，选定就不变。** 手作感用一拍二或 12fps（Vox 图形[6]、Vercel Ship 角色[29]、Dan Koe posterize[25]）；产品感用顺滑高帧率加 expo 缓动（Apple）。同一集不混用。
10. **开头最密，段落尾留白。** 前 30 s 镜头比后面短约 0.5 s[37]；Fireship 最用心打磨前 60 s[17]；段落结尾＝小结句、停顿、音乐收尾[5]。

附加两条（对无脸＋中文频道尤其重要）：
11. **屏幕上的字只放关键词、数字、引文**，不复读整句旁白（字幕层除外）。Kurzgesagt、Apple、LEMMiNO 都是"少字派"。
12. **主持人＝观众代理。** Cleo 用自己[12]，Kurzgesagt 用小鸟，3b1b 用圆周率小生物。九帽用柴犬：提问、困惑、恍然，**每 20–40 s 出现一次 ≤1.5 s 的反应**〔建议值〕。

---

## 4. 综合（2）：禁用的失败模式

| # | 失败模式 | 为什么禁 / 依据 |
|---|---|---|
| 1 | 屏幕标题和字幕同时显示同一句话 | 双倍阅读负担；优秀者都只放关键词（规则 11） |
| 2 | 一页里高亮好几个词，或用 3 种以上高亮色 | 高亮失去意义；厂商指南也警告"不要每行都高亮"[23]；Submagic 最多 3 色[20] |
| 3 | 无目的的漂浮、循环 wiggle、随机粒子、呼吸缩放 | 违反 3b1b 原则[14]；阿杜《动作谱》同样禁止（SOURCES.md） |
| 4 | 每个剪辑点换一种炫技转场（转场大杂烩） | Apple 要求"剪辑隐形"[26]；一个风格只留 2–3 个招牌转场 |
| 5 | 字体超过 2 族、强调色超过 1 个 | 规则 4 |
| 6 | 说 A 画 B；字幕滞后语音；画面先于旁白很久就揭晓 | 规则 3；Earworm"一个词不在拍上就塌"[8] |
| 7 | 图表或证据一闪而过（<4 s） | 图表要 5–12 s，证据要 6–10 s[37] |
| 8 | 一首背景乐从头放到尾；音乐和人声音高相撞 | Vox 约 20 s 变化一次、避开人声频段[5] |
| 9 | 开场放 Logo 片头、"大家好我是……"、长自我介绍 | 第一分钟定生死[18]；Fireship 没有片头[17] |
| 10 | 缩略图或标题的承诺在前 60 s 没兑现 | MrBeast 内部文档[18] |
| 11 | 字太长就缩小字号 | MotionGit 规范：分页或换场景，不缩字（SOURCES.md §2） |
| 12 | AI 图每个镜头画风漂移 | 规则 8；风格包要锁定统一的出图提示词和参考图 |
| 13 | 用授权不明或受限的字体（SF Pro 不能做营销视频[27]；Komika Axis 授权说法互相矛盾[21]） | 只用 OFL 等可再分发字体（见 §5 字体映射） |
| 14 | 竖屏字幕或关键信息被平台 UI 遮挡（右侧按钮栏、底部文案区） | 安全区见 §3.4；导出后必须在手机上看[23] |
| 15 | "假高级"：满屏玻璃拟态、霓虹 Tron 配色、廉价镜头光晕 | Cleo 刻意放弃 Tron 配色[12]；和"审美判断"的频道定位冲突 |
| 16 | 质感层和帧率中途换（前半段 12fps 纸感，后半段 60fps 玻璃） | 规则 8、规则 9 |
| 17 | 整页字幕"闪现"时没有任何节奏锚，或逐字蹦但切得太碎出现闪烁 | 厂商指南："避免过度分段造成的闪烁"[23] |

---

## 5. 综合（3）：动态字幕配方

### 5.1 标杆配方对照（英文原版）

| 款 | 字体 | 大小写 / 描边 / 阴影 | 每页 | 高亮逻辑 | 动画 | 时间 | 证据 |
|---|---|---|---|---|---|---|---|
| **Hormozi 旧版** | The Bold Font（替代：Montserrat Black 900） | 全大写；有阴影；无描边 | 1–3 词（短视频）；或 4–6 词分 2 行 | 当前词或关键词变色（黄或绿，常见 #FDE047），可加大约 4pt | 逐词点亮 | 在说到关键词时拆页，让关键词单独放大 | 【二手】[19][44] |
| **Hormozi 2025 新版** | Anton | 全大写；浅阴影；**黄色描边** | 同上 | 关键词换填充色；拆页放大 | **弹出（pop-in），自下而上** | Premiere 设定：每行最多 15 字符、每页至少 2 s | 【二手】[19] |
| **MrBeast** | Komika Axis（替代：Bangers / Anton） | 全大写；#FFD700 黄填充；**6–10px 黑描边**；轻投影 | **3–5 词** | 整页同色；强调时改用红色 | **Flash：整页同时出现** | 页面紧贴口语断句 | 【二手·厂商】[21] |
| **Ali Abdaal** | Inter / TT Fors | 句首大写；无漂浮旋转 | 一句半句（约 4–8 词）〔未核实〕 | **逐词颜色动画**：说完的词渐变成另一色（原文 "fades into black"） | 逐词变色，克制 | 跟随逐词时间戳 | 【二手】[22] |
| **Submagic 通用** | 每个主题自定 | — | 手动断行 | 主色＋**最多 3 个高亮色**，**手动**选词 | 主题内置 | — | 【源·帮助中心】[20] |
| **阅读型（Netflix 简中）** | 黑体（SimHei 占位） | 白字 | **每行 16 字，最多 2 行** | 无 | 无 | **成人 ≤9 字/秒**；**不用逗号句号，改空格**；底部偏重的"金字塔"断行；上行不要只留一两个字 | 【源】[24] |

厂商通用建议【二手】[23]：钩子期每页 2–5 词，普通短视频 3–7 词/行，长视频教程 6–10 词/行；在意群边界断行；只高亮数字、反转词（但是、其实）、关键名词、CTA 动词和"那一句要记住的话"；字幕在短语开始时出现、结束时消失，不许滞后。

### 5.2 九帽中文字幕配方（建议值，需实测）

> 公开资料里**没有**任何来源给出"高亮提前或延后多少毫秒"的标准（检索结论：只能自己校准）。下面的帧数是我们的工程起点，全部〔未核实〕，第一支片渲染后要逐帧检查。

**A. 阅读型（16:9 长视频默认）**
- 每行 ≤16 字，最多 2 行；读速 ≤9 字/秒（不达标就拆页，不缩字）【源】[24]。
- 去掉逗号句号，用一个全角空格代替；问号保留【源】[24]。
- 底部居中，距底边约 8% 画高；思源黑体 Medium，白字＋40–60% 黑底条或 2px 暗描边。
- 整句出现（不逐词）。**出现时间＝首字发音前 1–2 帧（约 33–67ms@30fps）；消失时间＝末字结束后 4–6 帧**；如果和下一页间隔不到 0.3 s，就把上一页延长到下一页出现，避免闪烁。
- 遇到镜头切换：字幕不跨切点。切点前后 ≤3 帧时，对齐到切点。
- 高亮：**每页最多 1 个词**，只用当前风格的强调色，**全片高亮比例 ≤15%**。

**B. 冲击型（9:16、金句、开场钩子）**
- 每页 **2–6 个汉字**（约等于 Hormozi 的 1–3 个英文词）；一页一个意群。
- 字号约为画面宽的 8–11%（1080 宽 → 每字 90–120px）；位置在画面高度 58–68% 处（避开竖屏底部文案区和右侧按钮栏）〔未核实〕。
- 字体：得意黑 Smiley Sans 或思源黑体 Heavy；高能款可用站酷快乐体（替代 Komika Axis）。
- 动画：整页**缩放 0.85→1.06→1.0，共 4–6 帧（130–200ms），back.out(1.7)**；或自下而上移 12–20px 加淡入（Hormozi 新版）。
- 高亮：当前关键词**换强调色并放大到 1.15–1.25 倍**；已说完的词保持白色（Hormozi 式），或降到 60% 灰（Ali 式）。二选一，全片统一。
- 逐词点亮的切换点＝该词发音起点（0 帧）；整页出现＝首字前 1–2 帧。
- emoji → 换成柴犬表情贴纸或线性图标，**每 10 s 最多 1 个**。
- 音效：每页最多一个很轻的 pop 或 tick（比旁白低 18–24 dB），金句页加一个 hit。

**C. 高亮选词逻辑（两种字幕通用，按优先级）**
1. 数字或比例（"3 倍""90%"）；
2. 反转词（"但是""其实""根本不"）后面紧跟的那个核心词；
3. 判断词或价值词（本频道核心："品味""判断""稀缺"）；
4. 动作指令（"去做""停下"）；
5. 专有名词第一次出现时。
- 同一页只取最高优先级的 1 个。连续 3 页都没有候选词时，第 3 页强制给核心名词，保持节奏。

**D. 安全区（9:16）**〔未核实，按抖音 / 小红书常见 UI 估计〕：上 10%、下 20%、右 15% 不放关键文字；16:9 下所有字距边 ≥5%。

---

## 6. 综合（4）：提议的 10 个风格族

每族都写：标杆、**5 条可测量规则**、柴犬怎么出场、适合的选题、9:16 适配。色值和时长是基于标杆推出的**起始参数**（〔未核实〕的部分要拉片校准）。字体全部换成可再分发的开源字体：思源黑体 / 思源宋体（OFL）、得意黑 Smiley Sans（OFL）、霞鹜文楷（OFL）、站酷快乐体（OFL）、JetBrains Mono（OFL）、Inter / Anton / Bebas Neue / Geist（OFL）。

### A. 社论版 Editorial（杂志编辑）
- 标杆：**Vox**、**The Economist**、FT。
- 规则：
  1. 底色纸白 #F7F3EA（或 FT 式 #FFF1E5），墨色 #131313；**唯一强调色**＝社论红 #E3120B 或报纸黄 #FFF200。黄色只作底块和高亮，不作文字色。
  2. 字体三角色：标题用粗无衬线（思源黑体 Heavy，Balto 的角色），引文用衬线（思源宋体 SemiBold），标签用等宽大写（JetBrains Mono 11–14px 档、字距 0.1em）。
  3. 每个画面最多 1 个标题＋1 句 ≤14 字的引文；引文高亮用"马克笔扫过"，320–480ms，从左到右。
  4. 图形元素按 12fps 步进；纸纹每秒抖 2–3 次；文字比底块晚 2–4 帧进入。
  5. 招牌转场只有两种：纸张遮罩擦除（≤10 帧），以及相机后拉＋高斯模糊峰值（模糊时长短于运动）。音乐约每 20 s 变化，段落以音乐收尾。
- 柴犬：右下角"读报"小插画；只在段落小结时抬头说一句。
- 选题：观点、趋势、"大家都在说 X，其实……"。
- 9:16：标题上移到 25% 高度，引文改成一行 ≤10 字。

### B. 证据桌 Evidence Desk（纸面拼贴调查）
- 标杆：**Johnny Harris**、**NYT Visual Investigations**、Vox Atlas。
- 规则：
  1. 俯拍桌面：暖纸 #E9DFC9＋去饱和 100% 的档案图＋**唯一红笔色 #D1281F**；每画面最多 2 处红笔标注。
  2. 新证据每 2–4 s 进场一次；需要阅读的文档停 ≥6 s，相机缓慢推进约 2–4%/s。
  3. 红笔动画：圈、下划线、箭头用描线完成，400–700ms，同时配一个笔划音效；被圈的那句同时加黄底高亮。
  4. 地图：平面先倾斜 30–45° 再俯冲；路线用虚线描画，800–1500ms；地名标签用打字机或等宽字体，每画面最多 4 个。
  5. 质感层：胶片颗粒常驻（强度低）；漏光和胶片烧**只在章节切换时**用。音效密度高：每个纸张或物件动作都有对应声音（纸、打字机、放映机）。每个证据带来源标签（媒体名、日期）。
- 柴犬：戴放大镜，站在桌边推一张纸进画面。
- 选题：案例拆解、AI 公司兴衰、"这个爆款是怎么被做出来的"。
- 9:16：桌面改成竖向堆叠的纸张，一次只放一张证据。

### C. 胶片随笔 Film Essay（颗粒怀旧）
- 标杆：**Nathaniel Drew**、**Pursuit of Wonder**。
- 规则：
  1. 颗粒常驻（16mm 感，噪声按帧换种子）；暖调分级：高光偏橙、阴影偏青绿；黑位抬到约 #141210，不用纯黑。
  2. 镜头 4–8 s；慢推的缩放速度 ≤3%/s；不用弹性缓动，只用 sine.inOut。
  3. 屏幕文字：小号衬线或手写（思源宋体 Light 或霞鹜文楷），居中，每画面 ≤10 字，淡入淡出 600–1000ms。
  4. 音乐：单件乐器（钢琴或吉他）或环境声，没有鼓点；音效每 10 s 最多 1 个。
  5. 转场：交叉溶解或黑场 12–24 帧；局部用 12fps 定格拼贴段落（剪纸、照片碎片）。
- 柴犬：只出现剪影或背影（看窗外、翻书），不说话的镜头占多数。
- 选题：审美、选择、"慢下来想一想"、情绪类判断。
- 9:16：画面更素，字放中间偏上。

### D. 暗场纪录 Dark Minimal Doc（暗场极简纪录）
- 标杆：**LEMMiNO**（辅：Kurzgesagt 的暗场段落）。
- 规则：
  1. 背景 #0A0A0B 到 #121212；**单一强调色**（冷青 #6FD3FF 或琥珀 #FFB000），占画面面积 <10%。
  2. 标题全大写或宽字距中文（字距 0.2–0.4em），细到中等字重（思源黑体 Light/Regular）；章节卡格式统一为"第一章 · 标题"。
  3. 镜头 6–12 s；相机慢推、环绕或横移，只用 sine 或 expo 的 inOut，**禁用 back 和 elastic**。
  4. 信息图用 1–2px 白色细线框、点阵地图、缓慢的数字滚动（≥1.5 s）。
  5. 声音：合成器铺底加低频；只在揭示时放一个 riser→hit；其余时间不用音效。
- 柴犬：黑场里被一束顶光照亮的半身，或只露高帽剪影。
- 选题：悬疑、未解问题、"AI 会不会取代审美"这类大命题。
- 9:16：保留留白，标题放在 1/3 处。

### E. 发布会展陈 Keynote Showcase（暗场产品展示）
- 标杆：**Apple 发布会 / 产品片**、**Vercel Ship**、**Linear**。
- 规则：
  1. 背景纯黑 #000 或 #08090A；**画面中只有主体带色**；最多 2 个径向光晕；不叠多种特效。
  2. 大字卡：每卡 2–8 个汉字（相当于 1–4 个英文词），字号占画宽 40–70%，字重 600–700，字距 -2% 到 -4%（得意黑或思源黑体 Bold，英文用 Geist / Inter）。
  3. 动作顺滑：expo.out 600–900ms；UI 卡片 3D 悬浮（rotateX 10–20°，带透视），缓慢漂移 ≤8px/s。
  4. 剪辑隐形：用匹配剪辑或推进穿越（从细节推到整体）；**禁止花哨转场**；一个镜头一个想法。
  5. 音乐锁拍（大字卡切换落在强拍上）；音效只用在关键 hit 上，音量低。
- 柴犬：像发布会讲者一样站在黑场左侧 1/3 处，聚光灯；产品或 UI 放右侧。
- 选题：AI 工具和产品评测、"新东西来了"、年度盘点。
- 9:16：大字上、UI 下，竖向堆叠。

### F. 大字快板 Kinetic Type（动态大字 / 单色线条）
- 标杆：**Dan Koe**、**Hormozi**、Apple 陈述卡。
- 规则：
  1. 单色：黑底白字（或反白），至多 1 个高亮色；线条图标用 3px 白描边，实心物体白填充无描边。
  2. 竖屏每页 2–6 个汉字，横屏 4–10 个汉字；逐词或逐页弹出；关键词放大 1.2–1.5 倍。
  3. 节奏：24/25fps 下主动作 12 帧一拍；落点 overshoot 后回弹；可选 posterize 12fps。
  4. 转场：形状变形（圆→方）、两层形状重合时的匹配剪辑、速度线；字本身就是画面，不配 B-roll。
  5. 每 1.5–3 s 换一页；每页一个很轻的 whoosh 或 pop；金句页加一个 hit 和 4–6 帧画面轻震。
- 柴犬：线条化的柴犬头像图标（白描边），和字一起弹入弹出。
- 选题：金句、观点总结、片尾 CTA、短视频开场。
- 9:16：本族的原生画幅。

### G. 数据地图 Data & Map（数据 / 地图信息图）
- 标杆：**Wendover**、**PolyMatter**、**The Economist / FT / Bloomberg 图表**。
- 规则：
  1. **图表标题＝结论句**（Economist 式，例如"AI 视频的成本两年降了 90%"），副标题写单位和口径；右下角放来源标签。
  2. 一张图只突出 1 个系列，用强调色，其余用灰 #B0B0B0；分类色 ≤4 个；红色线或红色标签限量使用。
  3. 图表停留 5–12 s；柱或线生长 600–1200ms；数字滚动用等宽数字（tabular-nums）。
  4. 地图：低饱和平面底，只高亮 1 个区域；路线描线；标签 ≤4 个；镜头先全景再推近，最多推进两级。
  5. 字体：窄体无衬线（思源黑体 Medium 收窄排，承担 Econ Sans Condensed 的角色），数字用 Inter 或 Geist 的 tabular 字形。
- 柴犬：指挥棒或教鞭，在图表旁边点出那根高亮的柱子。
- 选题：数字、收入、市场规模、对比。
- 9:16：图表改成竖向条形图，标题两行。

### H. 黑板推导 Diagram Explainer（图解推导）
- 标杆：**3Blue1Brown**、**Welch Labs**。
- 规则：
  1. 背景纯黑 #000000；用 3b1b 色板：蓝 #58C4DD、黄 #FFFF00、绿 #83C167、红 #FC6255、灰 #888888；**同一概念全片同色**（在 beat 表里登记颜色）。
  2. 动作词汇只用五个：write（描写）、transform（变形）、indicate（放大到 1.2 倍并变黄再回落）、circumscribe（画圈）、lagged（错峰进入，lag 0.1–0.2）；每个动作 0.6–1.5 s。
  3. 镜头 5–15 s；元素逐步累积，不跳切；一个画面最多 3 个主体。
  4. 公式和标签用衬线（思源宋体，承担 CMU Serif 的角色）；不烧字幕，或只用最简的阅读型字幕。
  5. 音乐低，几乎不用音效；视觉强化旁白不竞争。Welch 变体：叠加纸张打印的矩阵，用 B 族的红笔标注。
- 柴犬：右下角的"圆周率生物"角色，只做表情反应（疑惑、恍然），每 30–60 s 一次。
- 选题：AI 原理、"模型为什么这么判断"、概念拆解。
- 9:16：推导拆成竖向逐行。

### I. 柴犬剧场 Mascot Cartoon（吉祥物卡通 / 主持人代理）
- 标杆：**Kurzgesagt**、**Cleo Abram**（观众代理）。
- 规则：
  1. 扁平矢量＋渐变高光和内发光；深色底＋2–3 个高饱和点缀；**每集定一个主色调**，写进 episode 配置。
  2. **每句话一个镜头运动**（推、拉、横移），场景 3–6 s；3 层视差（前景、中景、背景，速度比 1.4 : 1 : 0.6）。
  3. 每个抽象概念都对应一个角色或物件隐喻（柴犬＋小道具）；屏幕上的字只放数字和标签（≤4 字）。
  4. 柴犬当观众代理：提问、困惑、恍然；每 20–40 s 一个 ≤1.5 s 的反应镜头。
  5. 拟音细：每个角色动作都有 pop、boing 或 click，比旁白低 12–18 dB；配乐按段落变化。
- 柴犬：主角。
- 选题：类比、入门、日常场景里的判断题。
- 9:16：角色居中，镜头运动改成纵向。

### J. 终端快剪 Terminal Meme-Cut（终端 / 梗剪）
- 标杆：**Fireship**、**AI Explained**（截图证据）、Half as Interesting。
- 规则：
  1. 深色代码面板（约 #1E1E2E）＋JetBrains Mono；橙 #FF9F1C 或青 #2EC4B6 作强调；窗口有标题栏的三个圆点。
  2. 1–3 s 一个视觉（Fireship 的区间是 1–5 s）；前 60 s 最密；没有片头。
  3. 代码和截图：冻帧＋逐行高亮框＋旁注图标或图注；论文和推文截图带来源标签（账号、日期）。
  4. 梗图或反应图每 15–30 s 一个，持续 ≤1 s，配一个音效；冷幽默的旁白不解释笑点。
  5. 文字用等宽小标签；转场以硬切为主，偶尔 whoosh 推移（≤6 帧）。
- 柴犬：像素风或终端 ASCII 风的柴犬头像出现在提示符旁边。
- 选题：AI 新闻速递、"100 秒讲清"、工具横评。
- 9:16：代码面板占上 60%，字幕在下。

### 风格族 × 参数速查

| 族 | 背景 | 强调色 | 主字体（中文） | 镜头时长 | 缓动 / 帧感 | 音效密度 | 招牌转场 |
|---|---|---|---|---|---|---|---|
| A 社论版 | #F7F3EA | #E3120B / #FFF200 | 思源黑体 Heavy＋思源宋体 | 3–5 s | 12fps 步进 | 中 | 纸张擦除、后拉加模糊 |
| B 证据桌 | #E9DFC9 | #D1281F | 等宽＋黑体 | 2–4 s（证据 ≥6 s） | 手持感推进 | 高 | 胶片烧、地图俯冲 |
| C 胶片随笔 | #141210 | 暖橙高光 | 思源宋体 Light / 霞鹜文楷 | 4–8 s | sine.inOut | 极低 | 溶解、黑场 |
| D 暗场纪录 | #0A0A0B | #6FD3FF / #FFB000 | 思源黑体 Light 宽字距 | 6–12 s | expo.inOut | 极低 | 黑场 |
| E 发布会 | #000 | 只给主体上色 | 得意黑 / 思源黑体 Bold＋Geist | 3–6 s | expo.out 顺滑 | 低 | 匹配剪辑、推进穿越 |
| F 大字快板 | #000 | 1 个高亮色 | 得意黑 / 思源黑体 Heavy | 1.5–3 s | back.out＋12 帧一拍 | 中 | 形变、速度线 |
| G 数据地图 | 中性浅或深 | 1 系列高亮＋灰 | 思源黑体 Medium＋tabular 数字 | 5–12 s | power2.out | 低 | 推近、分级缩放 |
| H 黑板推导 | #000000 | 3b1b 色板 | 思源宋体 | 5–15 s | smooth（manim 式） | 极低 | transform 原地变形 |
| I 柴犬剧场 | 深色＋每集主色 | 2–3 个高饱和色 | 圆体或黑体 Bold | 3–6 s | 每句一个镜头运动 | 中高（拟音） | 穿越缩放、形变 |
| J 终端快剪 | #1E1E2E | #FF9F1C / #2EC4B6 | JetBrains Mono＋黑体 | 1–3 s | 硬切 | 中高 | 硬切、梗图插入 |

### 横切：钩子库（前 5 秒）

| 钩子 | 标杆 | 九帽写法（柴犬无脸） |
|---|---|---|
| 先给难度，延迟揭示 | Vox / Fong[5] | "这张图看起来很普通，但做出它花了……"——先压住图不给 |
| 抛误解 | Veritasium[38] | "大多数人会选 A。为什么错？" |
| 兑现缩略图 | MrBeast[18] | 第 1 个镜头就出现缩略图里的那个东西或那个数字 |
| 个人证据 | Johnny Harris | 柴犬推进一份"文件"或截图："我找到了这个" |
| 宏大假设 | Kurzgesagt | "如果明天所有人都能一键做出好看的视频……" |
| 冷开场定义 | Fireship[17] | 一句冷嘲＋"X 是一个……"，0 片头 |
| 好奇代理人提问 | Cleo Abram[12] | 柴犬抬头问一个最笨的问题＋"如果是真的，那就大了" |
| 大字陈述 | Apple | 黑场里一句 4–8 字的判断，落在强拍上 |

---

## 7. 和九帽动效现有结构的对接建议

1. **beat 表三栏化**（学 Cleo）：`say`（台词）｜`visual`（风格族＋场景模板＋指向对象）｜`source`（来源标签）。`visual` 为空就报错。
2. **每个风格族一份 JSON 风格包**，字段＝本文 §6 的 5 条规则加速查表一行：背景、强调色、字体角色、镜头时长区间、缓动、帧感（12fps 步进或顺滑）、质感层、招牌转场（≤3 个）、音效密度、字幕皮肤、柴犬出场方式。
3. **"指向"作为一等公民**：beat 支持 `point:{target, verb: highlight|circle|arrow|zoom, at:"关键词"}`，自动对齐到逐字时间戳（呼应 SOURCES.md §6 的 `at:"关键词"`）。
4. **自动检查**（渲染前静态检查）：
   - 字体数 ≤2、强调色 ≤1；
   - 高亮比例 ≤15%；
   - 字幕每行 ≤16 字、读速 ≤9 字/秒；
   - 图表或证据停留时长达标；
   - 前 30 s 平均镜头时长比全片短；
   - 没有 `repeat:-1` 的装饰动画；
   - 一集只用一种帧感。

---

## 8. 来源表

（访问于 2026-10-31。标注 404 或 403 的只用到了搜索摘要。）

1. Kurzgesagt — Our video process：https://kurzgesagt.org/youtube/
2. Gigazine — Kurzgesagt 1200 小时制作流程：https://gigazine.net/gsc_news/en/20200217-science-animation-making
3. gofaceless — "Kurzgesagt style" 模板（第三方）：https://www.gofaceless.ai/en/templates/kurzgesagt-style
4. Adobe Community — 发光效果讨论：https://community.adobe.com/t5/illustrator-discussions/how-to-creating-this-design-effect/m-p/11804940
5. The Open Notebook — Joss Fong 黑洞视频访谈：https://www.theopennotebook.com/2020/01/07/videogram-how-a-vox-video-explains-the-science-behind-the-first-photo-of-a-black-hole/
6. PremiumBeat — Replicating Vox motion graphics：https://www.premiumbeat.com/blog/replicating-vox-motion-graphic/
7. Film Independent — Estelle Caswell 访谈：https://www.filmindependent.org/blog/explainer-an-interview-with-vox-pop-video-essayist-estelle-caswell/
8. The Next Web — Earworm：https://thenextweb.com/tnw2019/2019/05/07/earworm-youtube-music-dancing-about-architecture/
9. Vox 字体与配色：https://rosetta.to/u/vox/how-we-got-to-10-million-subs ；https://www.shadcn.io/design/vox/raw （第三方，误把 Balto 记为 Mark Simonson，实为 Type Supply）；https://www.typewolf.com/site-of-the-day/fonts/balto
10. RNDR Newsletter — 5 visuals（Johnny Harris / Pursuit of Wonder）：https://rndr.beehiiv.com/p/5-visuals-next-video-ead0
11. aescripts — How Johnny Harris makes maps（403，只用标题）：https://aescripts.com/learn/how-johnny-harris-makes-maps/
12. Cleo Abram × Colin and Samir 摘要：https://summify.io/discover/how-cleo-abram-dominated-youtube-in-under-1-year-a9sdUTsnFnE
13. LEMMiNO FAQ：https://lemmi.no/faq
14. 3Blue1Brown FAQ：https://www.3blue1brown.com/faq/
15. manimlib default_config.yml：https://github.com/3b1b/manim/blob/master/manimlib/default_config.yml
16. 3b1b/videos custom_config.yml：https://github.com/3b1b/videos/blob/master/custom_config.yml
17. Fireship 制作流程（其讲解视频的摘要）：https://readray.ai/notes/31502
18. MrBeast 内部文档摘录（Simon Willison）：https://simonwillison.net/2024/Sep/15/how-to-succeed-in-mrbeast-production/
19. Submagic — Hormozi captions：https://www.submagic.co/blog/how-to-make-alex-hormozi-captions
20. Submagic 帮助中心 — 高亮颜色：https://care.submagic.co/en/article/how-to-apply-highlighting-colors-to-your-words-16ttppq/
21. VideoCaptions.ai — MrBeast caption style：https://www.videocaptions.ai/glossary/mrbeast-caption-style
22. Ali Abdaal 字幕：https://sendshort.ai/guides/ali-abdaal-captions/ ；https://www.submagic.co/blog/make-captions-like-ali-abdaal （现 404，只用搜索摘要）
23. Subclip — Subtitle styles that convert：https://subclip.app/blogs/subtitle-styles-that-convert
24. Netflix 简体中文字幕规范：https://partnerhelp.netflixstudios.com/hc/en-us/articles/215986007-Chinese-Simplified-Timed-Text-Style-Guide ；每行字数 FAQ：https://backlothelp.netflix.com/hc/en-us/articles/215274938
25. "Dan Koe 风"动画教程摘要：https://readray.ai/notes/924365
26. Apple 产品片设计（非正式拆解）：https://youmind.com/landing/x-viral-articles/apple-product-video-design-secrets
27. Apple 字体授权提醒：https://www.yansmedia.com/blog/what-font-apple-use
28. 9to5Mac — keynote 剪辑拆解：https://9to5mac.com/?p=892397
29. Basement Studio — Behind the Ship（Vercel Ship 2025）：https://basement.studio/post/behind-the-ship
30. Vercel create-remotion-geist（目录页）：https://mcpservers.org/agent-skills/vercel/create-remotion-geist
31. Linear — Motion Storyteller 招聘：https://jobs.accel.com/companies/linear/jobs/48458808-motion-storyteller
32. Stripe — Motion Designer, Experiential 招聘：https://stripe.com/careers/listing/motion-designer-experiential/8047129
33. The Economist 图表风格指南（2017）：https://d30jyndnpz0ndz.cloudfront.net/documents/CHARTstyleguide_20170505.pdf ；Open Future 风格指南：https://d30jyndnpz0ndz.cloudfront.net/documents/OF_styleguide_080818.pdf
34. Press Gazette — FT 视觉故事团队：https://pressgazette.co.uk/publishers/nationals/financial-times-ft-visual-storytelling-team-investigations/
35. Territory Studio — Bloomberg Quicktake：https://territorystudio.com/project/bloomberg
36. NYT Visual Investigations：https://reutersinstitute.politics.ox.ac.uk/news/new-york-times-malachy-browne-future-visual-investigations-age-ai ；https://niemanstoryboard.org/?p=1849
37. Overseeros — How often should visuals change：https://www.overseeros.com/blog/how-often-should-visuals-change-youtube-video
38. Veritasium / Derek Muller：https://rosetta.to/u/veritasium/topic/youtube ；https://rosetta.to/u/wired/veritasium-s-derek-muller-answers-the-web-s-most-searched-questions-wired
39. Sam Denby — Oxford Union 访谈摘要：https://summify.io/discover/wendover-productions-sam-denby-interview-at-the-oxford-union-_q8k3q
40. Two Minute Papers #87：https://rosetta.to/u/twominutepapers/on-the-complexity-of-two-minute-papers-two-minute-papers-87
41. KDnuggets — AI YouTube channels（AI Explained）：https://kdnuggets.com/10-youtube-channels-keeping-you-ahead-in-ai
42. 3Blue1Brown 会员帖 — 与 Welch Labs 的 Manim 会话（付费墙）：https://members.3blue1brown.com/posts/manim-session-116778481
43. VideoHelp 论坛 — Pursuit of Wonder 风格讨论：https://forum.videohelp.com/showthread.php?p=2621086
44. FluxNote — Hormozi caption 指南（搜索摘要）：https://fluxnote.io/guides/how-to-make-alex-hormozi-style-captions
