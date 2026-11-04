#!/usr/bin/env python3
"""Gate 1 — the brief and the storyboard check, before anything is rendered.

  python3 scripts/brief.py new work/ [--title 标题]              -> work/brief.md (需求单 + 节拍表 to fill in)
  python3 scripts/brief.py check work/video.json [--style press] [--aspect 9:16] [--strict]

`check` builds the project (fast, no render), reads the resolved beat times and flags what the viewer would complain
about later, while it is still cheap to fix:
  hook        the first 2 s are text only (big words on a ground), not a picture            (P1)
  long-beat   one picture held longer than 5 s with nothing new planned (`cuts`, video, screencast)  (P1, P0 above 8 s)
  text-share  share of the runtime that is text-only beats — the PPT look                   (P0 above 30 %, P1 above 15 %)
  caption-dup big words that only repeat the spoken line                                    (P1, P0 above 30 % of text beats)
  same-fx     the same effect on two neighbouring beats, or more than 3 times in the film   (P1)
  no-brief    there is no brief.md next to video.json                                       (P1)
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
import review  # noqa: E402

TEMPLATE = """# 需求单：{title}

> 每一项都写完再出分镜。后面每个决定都拿「一句话片子」来对。规则见 references/director.md。

## 一句话片子
（观众看完要记住的一件事）

## 参考（2–5 条）
| 链接 | 学它哪一点 |
|---|---|
| | |

## 节拍表
前 2 秒必须是**画面**钩子（不是一行大字）；之后每 3–5 秒一个视觉爆点。

| 时间 | 观众看见什么 | 口播 | 素材从哪来 |
|---|---|---|---|
| 0–2s | | | |
| | | | |

## 屏幕大字（全片 ≤ 3 句，且不能只是重复字幕）
1.
2.
3.

## 素材
真实截图 / 录屏 / 数据和出处。不编界面、不编数字。

## 交付
画幅 · 时长 · 封面 · 文案 · 配乐署名 · AI 生成标识
"""

VISUAL_SCENES = {"compare", "number"}       # these always carry a picture or a chart
MOVING_FX_CATS = {"音视频", "屏幕", "素材", "节奏"}   # effects that play footage or cut inside themselves


def catalog():
    data = json.loads((SKILL / "gallery" / "effects.json").read_text())
    return {e["id"]: e.get("cat", "") for e in data["effects"]}


def text_only(b, cats):
    if b.get("scene") in ("statement", "title", "quote"):
        return not (b.get("image") or b.get("video"))
    if b.get("scene") == "fx":
        return cats.get(b.get("fx")) == "字效" or b.get("fx") in review.TEXT_FX
    return False


def moving(b, cats):
    if b.get("cuts") or b.get("video"):
        return True
    return b.get("scene") == "fx" and cats.get(b.get("fx")) in MOVING_FX_CATS


def build(vpath, style, aspect):
    cmd = [sys.executable, str(HERE / "build.py"), str(vpath)]
    if style:
        cmd += ["--style", style]
    if aspect:
        cmd += ["--aspect", aspect]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-1500:], r.stderr[-1500:])
        raise SystemExit("build failed")
    out = Path(r.stdout.strip().splitlines()[-1].split()[0])
    return out, json.loads((out / "timeline.json").read_text())


def check(vpath, style=None, aspect=None):
    video = json.loads(vpath.read_text())
    out, tl = build(vpath, style, aspect)
    cats = catalog()
    beats = video["beats"]
    D = tl["duration"]
    found = []
    if not (vpath.parent / "brief.md").exists():
        found.append(("P1", "no-brief", "没有 brief.md：先跑 brief.py new 写需求单和节拍表"))

    first = [b for b, x in zip(beats, tl["beats"]) if x["t"] < 2.0]
    if first and all(text_only(b, cats) for b in first):
        found.append(("P1", "hook", "前 2 秒只有文字：换成片子里最好看的一段画面（成品、演示、对比）"))

    text_dur = 0.0
    for b, x in zip(beats, tl["beats"]):
        if text_only(b, cats):
            text_dur += x["d"]
        if x["d"] > 5.0 and not moving(b, cats):
            level = "P0" if x["d"] > 8.0 else "P1"
            found.append((level, "long-beat", f"#{x['i']} {x['t']:.1f}s 起 {b.get('fx') or b.get('scene')} 撑了 {x['d']:.1f} 秒：拆成两个 beat，或加 cuts / 镜头运动 / 新元素"))
    share = text_dur / max(D, 0.1)
    if share > 0.30:
        found.append(("P0", "text-share", f"{share:.0%} 的时长是纯文字画面（PPT 感）：全片最多 2–3 屏大字，其余换成画面"))
    elif share > 0.15:
        found.append(("P1", "text-share", f"{share:.0%} 的时长是纯文字画面"))

    dups, texty = review.caption_dups(vpath)
    if dups:
        level = "P0" if texty and len(dups) / texty > 0.30 else "P1"
        found.append((level, "caption-dup", f"{len(dups)}/{texty} 个大字只是重复字幕：" + "；".join(f"{t:.1f}s「{txt}」" for t, fx, txt in dups[:6])))

    counts = {}
    prev = None
    for b, x in zip(beats, tl["beats"]):
        key = b.get("fx") if b.get("scene") == "fx" else None
        if key:
            counts[key] = counts.get(key, 0) + 1
            if key == prev:
                found.append(("P1", "same-fx", f"#{x['i']} {x['t']:.1f}s 和上一个 beat 都是 {key}"))
        prev = key
    for k, n in counts.items():
        if n > 3:
            found.append(("P1", "same-fx", f"{k} 用了 {n} 次（全片最多 3 次）"))
    return found, out


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new")
    n.add_argument("dir")
    n.add_argument("--title", default="")
    c = sp.add_parser("check")
    c.add_argument("video")
    c.add_argument("--style")
    c.add_argument("--aspect")
    c.add_argument("--strict", action="store_true", help="exit 1 when a P0 is found")
    a = ap.parse_args()
    if a.cmd == "new":
        d = Path(a.dir)
        d.mkdir(parents=True, exist_ok=True)
        p = d / "brief.md"
        if p.exists():
            raise SystemExit(f"{p} 已存在，不覆盖")
        p.write_text(TEMPLATE.format(title=a.title or d.resolve().name), encoding="utf-8")
        print(p)
        return
    found, out = check(Path(a.video).resolve(), a.style, a.aspect)
    for lv, rule, msg in found:
        print(f"  {lv} {rule:<12} {msg}")
    if not found:
        print("  分镜检查通过")
    print(f"下一关：python3 scripts/stills.py {a.video}{' --aspect ' + a.aspect if a.aspect else ''}  （每个 beat 一张静帧）")
    if a.strict and any(lv == "P0" for lv, _, _ in found):
        sys.exit(1)


if __name__ == "__main__":
    main()
