# 中国省级地图数据（china_map 用）

`china-provinces-ne.topo.json`：34 个省级单位（含台湾省、香港、澳门），由 Natural Earth 数据制作，公有领域，可商用、可再分发。
- 来源：Natural Earth admin-1 省份 + 中国视角国界 + maritime indicator（https://www.naturalearthdata.com/about/terms-of-use/ ，https://github.com/nvkelso/natural-earth-vector）。
- 处理：台湾各县市合并为「台湾省」；香港、澳门各区合并；中国视角轮廓中 admin-1 未覆盖的部分并入相邻省份（藏南、阿克赛钦边缘并入西藏，钓鱼岛并入台湾省，西沙、南沙、黄岩岛并入海南）；简化 25%，南海岛礁外扩 0.01°。
- 对象 `provinces`（adcode, name, name_en, iso_3166_2）和 `ninedash`（Natural Earth 的 9 段断续线）。

合规处理（china_map 内置）：
- 台湾、香港、澳门与大陆同一种画法，不画国界线。
- 右下角「南海诸岛」附图：海南岛与南海岛礁 + 断续线。
- 断续线按 2013 年标准地图画 10 段：Natural Earth 只有 9 段，台湾以东一段按标准地图位置补画（近似坐标 122.55°E 23.5°N → 122.75°E 24.55°N），主图和附图都画出。正式用于需要审图的场合时，请以自然资源部标准地图为准核对。
