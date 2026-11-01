# `footage` · 

<img src="../../assets/previews/fx/footage.webp" width="480" alt="footage 横屏"> <img src="../../assets/previews/fx/footage_v.webp" width="160" alt="footage 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 音视频 |
| 适合的句子 | 采访切片、自带字幕的素材 |
| 建议时长 | 跟素材一样长 |
| 参数 | `band_label`, `focus`, `image`, `name`, `role`, `show_band`, `start`, `subs`, `video`, `zoom` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 采访切片、素材自带字幕 |

```json
{
 "scene": "fx",
 "fx": "footage",
 "theme": "ink",
 "topic": "做内容",
 "video": "../../assets/previews/doc_16x9.mp4",
 "start": 5.0,
 "subs": "auto",
 "show_band": true,
 "line": "原片自带字幕时，我们的字幕*自动让开*。",
 "src": "成片《一个铁箱子》· 原片字幕在底部",
 "zoom": 1.12,
 "t": "@关键词"
}
```

**已知坑**：subs:auto 是启发式；原片自带页眉 / 大标题时直接写 subs，并用 zoom 推掉页眉。
