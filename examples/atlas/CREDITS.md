# examples/atlas 素材与数据来源

| 内容 | 来源 | 授权 |
|---|---|---|
| `assets/map/world-chn-50m.topo.json` | Natural Earth 10m admin-0（中国视角），本机素材库简化版（台湾、藏南、阿克赛钦在中国境内，黄岩岛并入中国） | 公有领域 |
| `assets/map/ne_10m_admin_0_boundary_lines_maritime_indicator_chn.geojson` | Natural Earth 南海断续线（9 段）；台湾以东第 10 段按 2013 年标准地图手工补画（位置参考 DataV 数据核对，未使用其几何） | 公有领域 |
| `assets/map/marnet_searoute-py.geojson` | searoute-py 的海运航线网络（Eurostat searoute / ORNL Global Shipping Lane Network） | Apache-2.0（见 `searoute-py.LICENSE.txt`） |
| `assets/map/paper-ambientcg-paper006.jpg` | ambientCG Paper 006（缩小到 1024） | CC0 |
| 近景 10 m 海岸线 | Natural Earth `ne_10m_admin_0_countries_chn.geojson`（13 MB，不随仓库；找不到时近景退回 50 m） | 公有领域 |
| 配音 | 本账号旁白音色，Windows 上的 VoxCPM2 服务合成（`tts_win.py`），未做语音识别核对 | 自有 |
| 背景音乐 | `scripts/music.py` 合成（tense，92 bpm） | MIT |
| 柴犬主持人 | 本账号 IP（引用 `../mixue/assets/video/shiba.webm`） | 自有 |

数据：苏伊士运河管理局 2024 / 2023 年收入（Egypt Today，2025-04）；Drewry World Container Index（2024-01-04、2024-07-18）；
World Bank 亚欧绕行 3,000–3,500 海里、7–10 天；运河长 193.3 公里与约 12% 贸易占比（世界经济论坛）；航线距离由 searoute 网络计算（苏伊士 10,508 海里，好望角 13,828 海里）。
