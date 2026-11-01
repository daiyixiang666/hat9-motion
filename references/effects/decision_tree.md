# `decision_tree` · 

<img src="../../assets/previews/fx/decision_tree.webp" width="480" alt="decision_tree 横屏"> <img src="../../assets/previews/fx/decision_tree_v.webp" width="160" alt="decision_tree 竖屏">

**怎么动**：

| 项 | 内容 |
|---|---|
| 类别 | 结构 |
| 适合的句子 | 如果……就……、判断流程 |
| 建议时长 | 5–6 秒 |
| 参数 | `path`, `tree` |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | Envato「Infographics 6 Roadmaps」· VideoHive「Infographic Maker」2.6K |

```json
{
 "scene": "fx",
 "fx": "decision_tree",
 "theme": "paper",
 "topic": "商业拆解",
 "title": "要不要开一家奶茶加盟店？",
 "note": "示意 · 一个思路，不是建议",
 "tree": {
  "q": "选好了人流稳定的位置？",
  "yes": {
   "q": "能接受两年以上回本？",
   "yes": {
    "q": "总部主要靠卖原料赚钱？",
    "yes": {
     "a": "算清原料成本再签",
     "good": true
    },
    "no": {
     "a": "问清加盟费用途",
     "good": true
    }
   },
   "no": {
    "a": "先别开",
    "good": false
   }
  },
  "no": {
   "a": "先别开",
   "good": false
  }
 },
 "path": [
  "是",
  "是",
  "是"
 ],
 "mock": "示意",
 "line": "先看位置，再看回本，最后看*总部怎么赚钱*。",
 "src": "第九顶帽子 · 观点（示意）",
 "t": "@关键词"
}
```

**已知坑**：无
