# 第三方说明

九帽动效本身的代码、合成音效（`scripts/sfx.py` 生成）均为 MIT。下面是运行时依赖和借鉴来源。

## 运行时依赖（不随包分发）

| 项目 | 许可 | 用法 |
|---|---|---|
| HyperFrames (heygen-com/hyperframes) 0.8.191 | Apache-2.0 | 渲染器：`npx --yes hyperframes@0.8.191 check / snapshot / render` |
| GSAP 3.14.2 (greensock/GSAP) | GreenSock Standard No-Charge License（非 OSI） | 页面通过 jsdelivr CDN 加载，**不打包进本仓库**；不得用于与 Webflow 竞争的无代码动画搭建器 |
| fontTools（可选） | MIT | 字体子集化 |
| jieba（可选） | MIT | 字幕按词断行 |
| edge-tts（可选） | LGPL-3.0 | 临时配音 `scripts/voice.py`，作为外部命令调用 |

## 字体（按需从官方仓库获取，`assets/fonts.json` 列出来源）

全部为 SIL OFL 1.1 或 Apache-2.0：Noto Sans/Serif SC、LXGW WenKai、Smiley Sans（得意黑）、ZCOOL 快乐体/小薇/庆科黄油体、马善政、Inter、Space Grotesk、Archivo、Barlow Condensed、Oswald、Anton、Bebas Neue、Playfair Display、Fraunces、EB Garamond、DM Serif Display、JetBrains Mono、IBM Plex Mono、Space Mono、Courier Prime、VT323、Special Elite、Permanent Marker、Caveat、Kalam。

## 借鉴的思路（未复制代码）

目前**没有**从任何第三方仓库复制代码；若以后移植 MIT/Apache 代码，在此逐条登记：文件、来源、许可、原作者。

## 示例素材

`examples/demo/assets/img/*` 为作者用 GPT Image 2 生成；示例配音为 TTS 合成。

`examples/aefx/assets/broll/*`：截自 Mixkit 免费视频（Mixkit Stock Video Free License），只用于渲染示例，素材文件不随仓库再分发（已写入 .gitignore），清单见该目录的 CREDITS.md。
`examples/mixue/`：画面为代码矢量绘制；背景音乐由 `scripts/music.py` 合成（MIT）；数据来自蜜雪集团 2024 年度业绩公告、McDonald's 2024 Form 10-K。


## 0.5.0 新增
- `examples/atlas/assets/map/`：Natural Earth 中国视角世界地图（公有领域）；searoute 海运网络（Apache-2.0，许可原文见同目录 `searoute-py.LICENSE.txt`）；ambientCG Paper006 纸纹（CC0）。南海断续线用 Natural Earth 的 9 段，台湾以东第 10 段按 2013 年版标准地图补画。
- `examples/doc/`：Prelinger Archives 档案片（公有领域）和 Mixkit 免费视频（Mixkit Stock Video Free License，素材不随仓库再分发，见 `examples/doc/assets/broll/CREDITS.md`，用 `prep_clips.py` 重建）。
- 地图类动效在渲染时从 jsdelivr 加载 d3-geo 和 topojson-client（ISC），与 GSAP 相同。
- 各示例的背景音乐由 `scripts/music.py` 合成（MIT）。

## OpenDesign（Apache-2.0）
- 来源：[nexu-io/open-design](https://github.com/nexu-io/open-design)，Apache License 2.0。只读取文本后用我们的写法重写，没有复制代码文件。
- `references/craft.md`、`scripts/craft_lint.py`：规则改编自它的 `craft/anti-ai-slop.md`、`craft/animation-discipline.md`、`craft/typography.md`，以及 HyperFrames 模板里的 `house-style.md`、`data-in-motion.md`、`references/motion-principles.md`、`references/typography.md`。其中 anti-ai-slop 和 typography 又改编自 [referodesign/refero_skill](https://github.com/referodesign/refero_skill)（MIT）。
- `scripts/design_md.py`：按它的 DESIGN.md / tokens.css 格式（`design-systems/_schema`）读取颜色、字体和圆角。没有带入任何品牌设计系统。
- `.claude-plugin/`：清单格式参照它和 anthropics/skills 的写法，并通过 `claude plugin validate --strict` 校验。
- `examples/brand/DESIGN.md` 是虚构品牌，只作演示。
