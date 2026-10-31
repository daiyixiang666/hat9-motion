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

见 `research/SOURCES.md`。目前**没有**从任何第三方仓库复制代码；若以后移植 MIT/Apache 代码，在此逐条登记：文件、来源、许可、原作者。

## 示例素材

`examples/demo/assets/img/*` 为本账号用 GPT Image 2 自行生成；配音为本地 VoxCPM2 合成；柴犬主持人为本账号 IP。

`examples/aefx/assets/broll/*`：截自 Mixkit 免费视频（Mixkit Stock Video Free License），只用于渲染示例，素材文件不随仓库再分发（已写入 .gitignore），清单见该目录的 CREDITS.md。
`examples/mixue/`：画面为代码矢量绘制；背景音乐由 `scripts/music.py` 合成（MIT）；数据来自蜜雪集团 2024 年度业绩公告、McDonald's 2024 Form 10-K。
