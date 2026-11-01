# 用自己的品牌规范出片

`DESIGN.md` 是一个虚构品牌「青舟研究所」的设计规范（格式同 OpenDesign 的设计系统）。一条命令把它变成九帽动效的风格，再用任意示例出片：

```bash
python3 scripts/design_md.py examples/brand/DESIGN.md --name qingzhou --base press   # -> styles/brand_qingzhou.py
python3 scripts/render.py examples/brand/video.json --styles brand_qingzhou --aspect 16:9 --lint
```

`video.json` 就是柠檬水那条示例，只换了风格：颜色、字体、圆角来自 DESIGN.md，场景和动效沿用 `press`。换成你自己的 DESIGN.md（或旁边放一份 tokens.css）即可；字体只能用 `assets/fonts.json` 里的 OFL 字体，找不到的会提示并沿用原风格。
