# 插件效果

每个文件一个（或一组）效果，导出 `FX = {"名字": 函数}`，签名同 `aefx.py`：`fn(X, cid, t, d, p)`。
可以 `from h9.aefx import _clip, _chars, THEMES` 复用外壳（主题、真实口播语境、页眉字幕）。名字不能和已有效果重复。
