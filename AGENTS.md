# AGENTS.md — 给 Codex / Cursor / WorkBuddy / 任何编码智能体

你在一个 **视频生成技能仓库** 里。用户给你文案或录音，你产出 mp4。

1. 先读 `SKILL.md`（入口），需要细节时再读 `references/` 和 `docs/effects.md`。
2. 最快路径：`python3 scripts/hat9.py quick "文案" --aspect 9:16` —— 自动分镜、配音、渲染。
3. 精修路径：`python3 scripts/hat9.py plan "文案" --out work/` 生成 `work/video.json`，逐句改 beat（换效果、写 `"@关键词"` 对时、加 `marks` 指哪说哪），再 `python3 scripts/hat9.py render work/video.json --aspect 16:9`。
4. 渲染前必须 `npx --yes hyperframes@0.8.191 check` 无 error；渲染后抽帧看一眼再交付。
5. 不要：调用付费生图 / 视频接口（先问用户）、用别人的 AI 图和视频、打包非 OFL/Apache 字体、把 GSAP 源码放进仓库。
6. 环境有问题先跑 `python3 scripts/hat9.py doctor`。
