# `stack_build` · 字叠在主体旁

<img src="../../assets/previews/fx/stack_build.webp" width="480" alt="stack_build 横屏"> <img src="../../assets/previews/fx/stack_build_v.webp" width="160" alt="stack_build 竖屏">

**怎么动**：主体（实拍 / 录屏 / 吉祥物）占着画面，旁边先出一行小字 kicker，再一行行往下叠大字，每行从自己的槽里升出来；最后一行（或 `*…*` 标的词）套上色块。`variant: "name"` 是名片版：我是 / 名字 / 身份逐行叠出，最后一个关注按钮被点成「已关注」。

| 项 | 内容 |
|---|---|
| 类别 | 重点信息（贴在主体旁） |
| 适合的句子 | 开场一句定位（「开源的 AI 剪辑竖屏模板」）、人物 / 账号介绍、结尾求关注 |
| 建议时长 | 3–4.5 秒（名片版带按钮 ≥ 4.5 秒） |
| 参数 | `lines`（1–6 行，`*词*` 标重点，默认最后一行）、`kicker`、`sub`、`at`（每行的时间）、`subject` / `video` / `image`（+ `subject_focus` `subject_start` `subject_fit` `subject_tag`）、`layout`（full / side / none）、`side`；名片版 `variant: "name"`、`pre`、`name`、`role`、`desc`、`en`、`follow`、`follow_at` |
| 横屏 / 竖屏 | ✓ / ✓（full：竖屏字在下半屏的暗角上；side：竖屏主体卡变高） |
| 跟风格换皮 | 字体、强调色、圆角、描边、阴影、重点词的标法（色块 / 下划线 / 马克笔 / 墨晕）都从风格来（`scripts/h9/fx/_kinfo.py` 的 `SKINS`） |
| 章节底色 | beat 没写 `theme` 时，颜色跟着这一章的 `chapter.bg` 颜色世界走（`scripts/h9/device.py`），深色、浅色、强调色章节都可读；在主持人区域里（`presenter.py`）按区域大小排版 |
| 参考 | 抖音开源竖屏模板宣传片（douyin 7701488753897917723）的同类版式 |

没有主体时：字放大占左边，重点词做成右侧的超大空心字，角上 01 / 03 计数跟着跳。

```json
{
 "scene": "fx",
 "fx": "stack_build",
 "d": 4.0,
 "theme": "ink",
 "topic": "开源模板",
 "subject": "$H9_MEDIA/broll/tech/typing-on-laptop-closeup_mixkit-1808.mp4",
 "subject_start": 2,
 "kicker": "OPEN-SOURCE · PORTRAIT TEMPLATES",
 "lines": [
  "开源的",
  "AI 剪辑",
  "竖屏模板"
 ],
 "sub": "一条口播，直接出成片",
 "line": "开源的 AI 剪辑*竖屏模板*。"
}
```
