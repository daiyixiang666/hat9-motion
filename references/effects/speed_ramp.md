# `speed_ramp` · 

<img src="../../assets/previews/fx/speed_ramp.webp" width="480" alt="speed_ramp 横屏"> <img src="../../assets/previews/fx/speed_ramp_v.webp" width="160" alt="speed_ramp 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 音视频 |
| 适合的句子 | 慢放看细节、快进跳过 |
| 建议时长 | 按变速后的长度，常见 4–6 秒 |
| 参数 | `badge`, `drama`, `focus`, `graph`, `ramp`, `smooth`, `start`, `video` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | B站「AE 变速卡点」173.4 万播放 |

```json
{
 "scene": "fx",
 "fx": "speed_ramp",
 "theme": "ink",
 "topic": "商业拆解",
 "video": "../pacing/assets/clips/factory.mp4",
 "ramp": [
  [
   0,
   1.2,
   1
  ],
  [
   1.2,
   2.2,
   0.25
  ],
  [
   2.2,
   4.0,
   2
  ]
 ],
 "drama": true,
 "line": "放慢四倍：福特早年的流水线上，工人正在装*木制车轮*。",
 "src": "Henry Ford's Mirror of America (1962) · Prelinger Archives（公有领域）",
 "t": "@关键词"
}
```

**已知坑**：ramp 用原片秒数；慢放要素材本身有动作，静止镜头慢放看不出来。
