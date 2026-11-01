# `podcast` · 

<img src="../../assets/previews/fx/podcast.webp" width="480" alt="podcast 横屏"> <img src="../../assets/previews/fx/podcast_v.webp" width="160" alt="podcast 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 音视频 |
| 适合的句子 | 播客切片、对谈节目 |
| 建议时长 | 跟切片一样长 + 0.8 秒 |
| 参数 | `a`, `art`, `audio`, `b`, `ep`, `episode`, `hosts`, `show`, `speaker`, `turns`, `vol`, `words` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Envato「Audio Visualizer」热门 |

```json
{
 "scene": "fx",
 "fx": "podcast",
 "theme": "paper",
 "topic": "做内容",
 "audio": "../mixue/assets/audio/voice.mp3",
 "words": "../mixue/assets/audio/words.json",
 "a": 0,
 "b": 6.6,
 "show": "第九顶帽子 · 商业拆解",
 "episode": "一杯 4 块钱的柠檬水，一年净赚 44 亿多",
 "ep": "01",
 "hosts": [
  {
   "name": "柴犬"
  }
 ],
 "line": "做成播客切片也行：头像跟着*音量*跳。",
 "t": "@关键词"
}
```

**已知坑**：多人 turns 需要真实多人音频；拿单人旁白做多人只能标「示意」。
