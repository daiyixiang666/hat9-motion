# 地图数据

`land-50m.topo.json`：Natural Earth 陆地轮廓（中国视角派生版，合并后的陆地，不含国界），公有领域，可商用、可再分发。
来源：Natural Earth（https://www.naturalearthdata.com/about/terms-of-use/），派生处理见素材库 `library/maps/vector/README.md`。
只画陆地、不画国界，所以不涉及国界线的标准地图审核；需要画国界时必须改用中国视角数据（world-chn-50m）并核对标准地图要求。

- `world-chn-50m.topo.json`: Natural Earth 1:50m admin-0 countries, China point of view (public domain). Copied from the project's map library; used by `area_overlay`.
