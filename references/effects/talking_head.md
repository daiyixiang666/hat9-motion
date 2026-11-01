# `talking_head` · 

<img src="../../assets/previews/fx/talking_head.webp" width="480" alt="talking_head 横屏"> <img src="../../assets/previews/fx/talking_head_v.webp" width="160" alt="talking_head 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 音视频 |
| 适合的句子 | 口播段落、Vlog、关键词贴纸 |
| 建议时长 | 每个贴纸 ≥ 0.8 秒，每个插入 2–2.5 秒 |
| 参数 | `broll`, `host_fit`, `name`, `stickers` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | 毕导式口播：跳切 + 贴纸 |

```json
{
 "scene": "fx",
 "fx": "talking_head",
 "theme": "lemon",
 "topic": "做内容",
 "stickers": [
  {
   "text": "写稿",
   "at": 1.3
  },
  {
   "text": "配音",
   "at": 2.4
  },
  {
   "text": "渲染",
   "at": 3.5,
   "kind": "bubble"
  }
 ],
 "broll": [
  {
   "src": "../../assets/previews/poster_16x9.mp4",
   "at": 4.3,
   "dur": 2.4,
   "caption": "成片 · 瑞士海报",
   "start": 6.0
  }
 ],
 "line": "做一条口播，三步：*写稿*、配音、渲染。",
 "t": "@关键词"
}
```

**已知坑**：贴纸每分钟别超过 2–3 个（bench_cn）；8 个只用于压力测试。
