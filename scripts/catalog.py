#!/usr/bin/env python3
"""Effect catalog: cut every effect out of the showcase reel as a looping preview, and write docs/effects.md.

  python3 scripts/catalog.py      (needs examples/aefx/renders/reel_16x9.mp4 [+ reel_9x16.mp4])
  -> assets/previews/fx/<name>.webp + .gif   and   docs/effects.md
"""
import json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
from h9 import aefx  # noqa: E402

EX = SKILL / "examples" / "aefx"
OUT = SKILL / "assets" / "previews" / "fx"
DOC = SKILL / "docs" / "effects.md"
CARDS = SKILL / "references" / "effects"
GIF = "--gif" in sys.argv          # webp only by default (GitHub renders animated webp); --gif adds fallbacks
GALLERY = SKILL / "gallery"
CAT = {   # gallery filter categories
    "字效": ["pop", "mask_up", "tracking", "blur_focus", "apple_blur", "typewriter", "scramble", "write_on", "flip3d", "slice_text", "shine",
             "glitch", "neon", "stomp", "match_cut", "impact", "ghost_type", "lockup"],
    "图形": ["burst", "cartoon", "gooey", "diffuse"],
    "照片": ["parallax", "mosaic", "collage", "portal", "callout"],
    "数据": ["odometer"],
    "界面": ["notify", "lower3", "triple"],
}
def cat_of(fx): return next((k for k, v in CAT.items() if fx in v), "其他")


def cut(src, t, d, dst, w=480, fps=15):
    """one effect -> animated webp (small, via Pillow) + gif (universal); a little trimmed off each end of the beat."""
    import tempfile
    from PIL import Image
    a, dur = t + 0.12, max(0.6, d - 0.3)
    vf = f"fps={fps},scale={w}:-2:flags=lanczos"
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(src), "-vf", vf, f"{td}/f%04d.png"], check=True)
        frames = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("f*.png"))]
        frames[0].save(dst.with_suffix(".webp"), save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, quality=72, method=5)
    if not GIF: return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{dur:.2f}", "-i", str(src), "-vf", f"{vf},split[s0][s1];[s0]palettegen=max_colors=96[p];[s1][p]paletteuse=dither=bayer:bayer_scale=4", "-loop", "0", str(dst.with_suffix(".gif"))], check=True)


SUIT = {
    "pop": "开场、短标题", "mask_up": "任何标题、两行观点", "tracking": "电影感标题、一个词", "blur_focus": "金句、英文口号", "apple_blur": "结论、产品口吻的判断句",
    "typewriter": "提示词、命令、搜索", "scramble": "技术名词、英文代号", "write_on": "关键词、签名、毛笔字", "flip3d": "账号名、章节名", "slice_text": "对比、反转",
    "shine": "收尾、品牌", "glitch": "出错、警告、反转", "neon": "夜景、潮流、店招", "stomp": "节奏快的一句话、金句拆字", "match_cut": "一个词贯穿多个场景",
    "impact": "重点结论、冲击句", "ghost_type": "章节标题 + 小字说明", "lockup": "中英双语标题、字体展示", "burst": "爆款、数字揭晓、强调",
    "cartoon": "搞笑、吐槽、意外", "gooey": "合并、碰撞、两者关系", "diffuse": "安静的过渡、情绪句", "parallax": "开场大图、人物故事",
    "mosaic": "大量案例、作品合集", "collage": "资料拼贴、证据", "portal": "从一个画面进入另一个话题", "callout": "指出图里的细节",
    "odometer": "任何数字、比例", "notify": "平台反馈、增长、消息", "lower3": "人物 / 账号介绍、结尾", "triple": "片尾求三连 / 关注",
}
DUR = {"stomp": "按口播，每词 0.3–0.5 秒", "portal": "2.5–3 秒", "mosaic": "2.5–3 秒", "match_cut": "2–3 秒（每 0.22 秒一切）", "parallax": "2–4 秒"}
PIT = {
    "parallax": "需要先抠图 + 修补背景板（scripts/cutout 流程）；主体太小时视差不明显。",
    "stomp": "词太长会自动缩字号；一页最好 2–4 个字。",
    "portal": "x / y 要对准画面里的「洞」（瞳孔、杯口、窗）；竖屏裁切后坐标会变。",
    "callout": "竖屏时图片裁切不同，x / y 要按竖屏重新给。",
    "match_cut": "每个画面的底色和字色是成对设计的，换图时保持一深一浅交替。",
    "write_on": "笔画描边依赖字体轮廓；毛笔字体（马善政）效果最好。",
    "ghost_type": "虚影字是故意半透明的，check 时已标记为允许重叠。",
}


def main():
    v = json.loads((EX / "video.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True); DOC.parent.mkdir(parents=True, exist_ok=True)
    reel = EX / "renders" / "reel_16x9.mp4"
    reel_v = EX / "renders" / "reel_9x16.mp4"
    CARDS.mkdir(parents=True, exist_ok=True); GALLERY.mkdir(parents=True, exist_ok=True)
    rows, trans = [], []
    seen = set()
    for b in v["beats"]:
        fx = b["fx"]
        if fx == "plate":
            if b.get("tr") and b["tr"] != "hard":
                name = f"tr_{b['tr']}"
                cut(reel, b["t"] - 0.45, 1.2, OUT / name, w=360)
                if reel_v.exists(): cut(reel_v, b["t"] - 0.45, 1.2, OUT / f"{name}_v", w=200)
                trans.append((b["tr"], b.get("label", ""), name))
            continue
        if fx in seen: continue
        seen.add(fx)
        cut(reel, b["t"], b["d"], OUT / fx)
        if reel_v.exists(): cut(reel_v, b["t"], b["d"], OUT / f"{fx}_v", w=240)
        doc = (aefx.FX[fx].__doc__ or "").strip().replace("\n", " ")
        title, _, how = doc.partition(":")
        params = sorted(set(re.findall(r'p\[["\'](\w+)["\']\]|p\.get\(["\'](\w+)["\']', open(aefx.__file__).read().split(f"def {fx}(")[1].split("\ndef ")[0])))
        keys = sorted({a or b_ for a, b_ in params} - {"label", "ref"})
        rows.append((fx, title.strip(), how.strip(), keys, b.get("label", ""), b.get("ref", "")))
        ex = {k: v for k, v in b.items() if k not in ("t", "d", "tr", "label", "ref")}
        ex = {"scene": "fx", **{k: v for k, v in ex.items() if k != "scene"}, "t": "@关键词"}
        (CARDS / f"{fx}.md").write_text(f"""# `{fx}` · {title.strip()}

<img src="../../assets/previews/fx/{fx}.webp" width="480" alt="{fx} 横屏"> <img src="../../assets/previews/fx/{fx}_v.webp" width="160" alt="{fx} 竖屏">

**怎么动**：{how.strip()}

| 项 | 内容 |
|---|---|
| 类别 | {cat_of(fx)} |
| 适合的句子 | {SUIT.get(fx, '—')} |
| 建议时长 | {DUR.get(fx, '2–3 秒')} |
| 参数 | {', '.join(f'`{k}`' for k in keys) or '—'} |
| 横屏 / 竖屏 | ✓ / ✓（尺寸用 vmin，竖屏自动缩放） |
| 人气依据 | {b.get('ref', '—')} |

```json
{json.dumps(ex, ensure_ascii=False, indent=1)}
```

**已知坑**：{PIT.get(fx, '无')}
""")
    md = ["# 效果目录 · Effects", "", "每个效果都是 `scripts/h9/aefx.py` 里的一个函数，在 `video.json` 里写成一个 beat：", "",
          '```json\n{"scene": "fx", "fx": "stomp", "words": ["大家", "都在用", "AI"], "t": "@大家"}\n```', "",
          "排名和人气依据见 [`research/ae_popular.md`](../research/ae_popular.md)。横屏、竖屏同一套参数。", "", "## 效果", ""]
    for fx, title, how, keys, label, ref in rows:
        md += [f"### `{fx}` — {title}", "", f'<img src="../assets/previews/fx/{fx}.webp" width="480" alt="{fx}">', "",
               how, "", f"- 参数：{', '.join(f'`{k}`' for k in keys) or '—'}", f"- 人气：{ref or '—'}", ""]
    md += ["## 转场", "", "写在下一个 beat 上：`\"tr\": \"zoomin\"`。", "", "| 转场 | 预览 | 说明 |", "|---|---|---|"]
    for k, label, name in trans:
        md.append(f'| `{k}` | <img src="../assets/previews/fx/{name}.webp" width="240"> | {label} |')
    DOC.write_text("\n".join(md) + "\n")
    # agent index: one line per effect, pick by name without reading the library
    idx = ["# 九帽动效 · 效果索引（给 AI 读）", "", "在 video.json 里写 {\"scene\": \"fx\", \"fx\": \"<id>\", ...}；转场写在下一个 beat：\"tr\": \"<id>\"。配方卡：references/effects/<id>.md", ""]
    idx += [f"- {fx} [{cat_of(fx)}]: {title} — {SUIT.get(fx, '')}" for fx, title, *_ in rows]
    idx += ["", "## 转场"] + [f"- {k}: {label}" for k, label, _ in trans]
    (GALLERY / "llms.txt").write_text("\n".join(idx) + "\n")
    (GALLERY / "effects.json").write_text(json.dumps(
        {"effects": [{"id": fx, "title": title, "how": how, "cat": cat_of(fx), "ref": ref, "label": label, "suit": SUIT.get(fx, "")} for fx, title, how, keys, label, ref in rows],
         "transitions": [{"id": k, "label": label, "file": name} for k, label, name in trans]}, ensure_ascii=False, indent=1))
    print(DOC, len(rows), "effects,", len(trans), "transitions")


if __name__ == "__main__":
    main()
