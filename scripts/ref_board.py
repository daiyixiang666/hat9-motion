#!/usr/bin/env python3
"""Learn a look from reference films: one board per reference + a principles sheet to fill in.

  python3 scripts/ref_board.py ref1.mp4 ref2.mp4 ... [--out work/refs] [--frames 12] [--transcribe]

For every reference: its cutting pace (scripts/ref_pacing.py), one frame from the middle of each shot (evenly
thinned to --frames) on a numbered strip (R2-07 = reference 2, frame 7), and with --transcribe a transcript
(faster-whisper, if installed). Then principles.md: the pace table and empty slots for 5–10 principles, each to be
backed by 2–3 frame ids. Write the principles from the boards — "two fonts: sans body + italic serif for the
stressed word", "one line runs through the whole film" — then derive a style with `hat9.py style new` and prove
one scene against the board before building the rest (references/director.md, part 5).
"""
import argparse, statistics, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_pacing, review  # noqa: E402


def grab(src, t, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1", "-vf", "scale=-2:360", str(path)], check=True)
    return path


def strip(rid, name, pngs, st, out):
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert("RGB") for p in pngs]
    h = 360
    pad = 6
    width = sum(im.width + pad for im in ims) + pad
    board = Image.new("RGB", (max(width, 900), h + 96), (18, 18, 18))
    d = ImageDraw.Draw(board)
    d.text((pad, 8), f"R{rid}  {name}", fill=(255, 210, 0), font=review.label_font(26))
    d.text((pad, 42), f"{st['shots']} 个镜头 · {st['per_min']} 刀/分钟 · 中位 {st['median']}s · 1 秒以下 {int(st['short_share'] * 100)}%",
           fill=(210, 210, 210), font=review.label_font(20))
    x = pad
    tag = review.label_font(20)
    for k, im in enumerate(ims):
        board.paste(im, (x, 84))
        d.rectangle([x, 84, x + 74, 110], fill=(0, 0, 0))
        d.text((x + 4, 86), f"R{rid}-{k + 1:02d}", fill=(255, 210, 0), font=tag)
        x += im.width + pad
    board.save(out, quality=88)
    return out


def transcribe(src):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    model = WhisperModel("small", compute_type="int8")
    segs, _ = model.transcribe(str(src), vad_filter=True, condition_on_previous_text=False)
    return "\n".join(f"[{s.start:6.1f}] {s.text.strip()}" for s in segs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("refs", nargs="+")
    ap.add_argument("--out", default="refs")
    ap.add_argument("--frames", type=int, default=12)
    ap.add_argument("--transcribe", action="store_true")
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for rid, ref in enumerate(a.refs, 1):
        src = Path(ref).resolve()
        bounds, dur = ref_pacing.cuts(src, 0.3)
        st = ref_pacing.stats(bounds, dur)
        mids = []
        ends = bounds[1:] + [dur]
        for s, e in zip(bounds, ends):
            mids.append((s + e) / 2)
        if len(mids) > a.frames:
            step = len(mids) / a.frames
            thinned = []
            for k in range(a.frames):
                thinned.append(mids[int(k * step)])
            mids = thinned
        with tempfile.TemporaryDirectory() as tmp:
            pngs = []
            for k, t in enumerate(mids):
                pngs.append(grab(src, t, Path(tmp) / f"{k:03d}.jpg"))
            board = strip(rid, src.name, pngs, st, out / f"R{rid}_{src.stem}.jpg")
        line = f"| R{rid} | {src.name} | {dur:.0f}s | {st['shots']} | {st['per_min']} | {st['median']}s | {int(st['short_share'] * 100)}% |"
        rows.append((st, line))
        print(f"  R{rid} {src.name}: {st['per_min']} 刀/分钟，中位 {st['median']}s → {board.name}")
        if a.transcribe:
            text = transcribe(src)
            if text is None:
                print("    （没装 faster-whisper，跳过逐字稿）")
            else:
                (out / f"R{rid}_{src.stem}.txt").write_text(text + "\n", encoding="utf-8")
    medians = [st["median"] for st, _ in rows]
    lines = ["# 参考片原则", "", "## 节奏", "", "| # | 片子 | 时长 | 镜头 | 刀/分钟 | 中位镜头 | 1 秒以下 |", "|---|---|---|---|---|---|---|"]
    lines += [line for _, line in rows]
    lines += ["", f"参考片中位镜头的中位数：**{statistics.median(medians):.2f}s**（自己的片子用 `review.py --ref` 对比）", "",
              "## 原则（5–10 条，每条配 2–3 个帧编号；写成能照做的话）", ""]
    for k in range(1, 8):
        lines += [f"{k}. 原则：", "   参考帧：", "   落到风格里：（颜色 / 字体 / 版式 / 镜头 / 转场 / CSS）", ""]
    lines += ["## 覆盖检查", "", "把每张参考帧归到一条原则下；归不进去的帧说明还漏了原则。", "",
              "## 下一步", "", "`python3 scripts/hat9.py style new <id> --from <最接近的风格>`，先做一个场景对着参考板比，过关再铺开。"]
    (out / "principles.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"参考板和原则表 → {out}")


if __name__ == "__main__":
    main()
