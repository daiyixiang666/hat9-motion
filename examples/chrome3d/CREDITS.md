# examples/chrome3d 数据与素材来源

## 数据（每个数字都核对过原始出处）

| 画面里的数字 | 出处 |
|---|---|
| FY2023 数据中心收入 150.1 亿美元（$15.0B） | NVIDIA Q4 FY2023 财报新闻稿：https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2023 |
| FY2024 数据中心收入 $47.5B | NVIDIA Q4 FY2024 财报新闻稿：https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2024 |
| FY2025 数据中心收入 $115.2B | NVIDIA Q4 FY2025 财报新闻稿：https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2025 |
| FY2026 数据中心收入 $193.7B，同比 +68% | NVIDIA Q4 FY2026 财报新闻稿：https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026 |
| 四年将近 13 倍（193.7 ÷ 15.0 = 12.9） | 由上面两项计算 |
| 最近一季 GAAP 毛利率 75.0%（Q2 FY2027，截至 2026-07-26） | NVIDIA 8-K 财报新闻稿（2026-08-26）：https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000073/q2fy27pr.htm |
| 2025-10-29 成为全球第一家市值 5 万亿美元的公司（收盘 $207.04，约 $5.03T） | Fox Business：https://www.foxbusiness.com/markets/nvidia-becomes-first-company-hit-5-trillion-market-valuation-ai-boom-drives-historic-growth ；Reuters 稿（SCMP 转载）：https://www.scmp.com/news/world/united-states-canada/article/3330810/nvidia-becomes-worlds-first-us5-trillion-company-ai-boom-powers-meteoric-rise |
| 约 600 万开发者 | NVIDIA GTC 2025 主题演讲（2025-03-18），TechRadar 现场报道：https://www.techradar.com/pro/live/nvidia-gtc-2025-all-the-news-and-updates-from-jensen-huang-keynote-as-it-happens |

## 素材

| 内容 | 来源 | 授权 |
|---|---|---|
| 三维字 | Archivo（wdth 125 / wght 900）与阿里巴巴普惠体 Heavy 的字形轮廓，构建时挤出 | OFL / 阿里巴巴普惠体免费商用授权 |
| 环境光、材质、所有三维物体 | `runtime/chrome3d.js` 程序生成（无贴图、无下载） | MIT |
| 配音 | TTS 合成旁白 | 自有 |
| 背景音乐 | `scripts/music.py` 合成（tense，112 bpm） | MIT |
| 主持人 | 代码绘制的卡通形象（`assets/host.webm`） | 自有 |
| three.js r160 | 渲染时从 jsdelivr 按固定版本加载 | MIT |

`variants.json` 是输入适配的压力测试（测试数据，不是事实），不进画廊。
