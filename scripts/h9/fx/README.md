# 插件效果

每个文件一个（或一组）效果，导出 `FX = {"名字": 函数}`，签名同 `aefx.py`：`fn(X, cid, t, d, p)`。
可以 `from h9.aefx import _clip, _chars, THEMES` 复用外壳（主题、真实口播语境、页眉字幕）。名字不能和已有效果重复。

注意：`scripts/h9/fx.py`（转场模块）和本目录同名，所以这里不能用 `from h9.fx.xxx import`；共用的辅助文件以 `_` 开头（加载器会跳过），按路径加载，见 `earth_zoom.py`。
