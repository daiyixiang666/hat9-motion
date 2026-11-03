#!/usr/bin/env python3
"""Pre-delivery review of a rendered film: contact sheets to look at, plus the checks a viewer would complain about.

  python3 scripts/review.py work/renders/press_9x16.mp4 [--video work/video.json] [--out work/review] [--strict]

Writes <out>/sheet_NN.jpg (2 frames per second, time-stamped) and <out>/review.md, and prints the findings:
  freeze        the picture does not change for more than 2.5 s                       (P0)
  hook          nothing changes in the first 2 s                                      (P0)
  slides        share of frames that are a flat ground with a little text (PPT look)  (P0 above 30 %)
  caption-dup   on-screen big text that only repeats the spoken line                  (P1, P0 above 30 % of text beats)
  cut-gap       more than 6 s without a cut or a big change                           (P1)
  fx-repeat     the same effect used more than 3 times                                (P1)
Then look at every sheet and score the rubric in review.md (references/director.md); deliver only when every score ≥ 8.
Needs ffmpeg and Pillow.
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

TEXT_FX = {"stomp", "black_slam", "tracking", "word_swap", "lockup", "mask_up", "flying_words", "text_mask", "typewriter",
           "scramble", "ghost_type", "write_on", "handwrite", "vertical_title", "glitch", "neon", "shine", "apple_blur", "diffuse"}
PUN = re.compile(r"[\s，。、；：！？,.;:!?…—“”‘’（）()《》「」*·\-]")


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip())


def freezes(path, dur):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "scale=270:-2,freezedetect=n=-48dB:d=2.5", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = []
    start = None
    for line in r.stderr.splitlines():
        if "freeze_start:" in line:
            start = float(line.split("freeze_start:")[1].split()[0])
        if "freeze_end:" in line and start is not None:
            out.append((start, float(line.split("freeze_end:")[1].split()[0])))
            start = None
    if start is not None:
        out.append((start, dur))
    return out


def scene_changes(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "scale=270:-2,select='gt(scene,0.14)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m.group(1)) for m in re.finditer(r"pts_time:([0-9.]+)", r.stderr)]


def frames(path, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", "fps=2,scale=216:-2", str(Path(tmp) / "f_%05d.jpg")], check=True)
    return sorted(Path(tmp).glob("f_*.jpg"))


def flat(im):
    """a frame that is mostly one colour: share of pixels close to the most common colour."""
    small = im.convert("RGB").resize((27, 48))
    raw = small.tobytes()
    counts = {}
    for i in range(0, len(raw), 3):
        key = (raw[i] // 24, raw[i + 1] // 24, raw[i + 2] // 24)
        counts[key] = counts.get(key, 0) + 1
    top = max(counts.values())
    return top / (len(raw) // 3)


def sheets(files, out):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(18)
    cols, rows = 10, 4
    per = cols * rows
    w, h = Image.open(files[0]).size
    made = []
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        board = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), (24, 24, 24))
        d = ImageDraw.Draw(board)
        for i, f in enumerate(chunk):
            x = (i % cols) * (w + 4)
            y = (i // cols) * (h + 4)
            board.paste(Image.open(f), (x, y))
            t = (s + i) / 2
            d.rectangle([x, y, x + 54, y + 22], fill=(0, 0, 0))
            d.text((x + 4, y + 2), f"{t:.1f}s", fill=(255, 220, 0), font=font)
        p = out / f"sheet_{len(made) + 1:02d}.jpg"
        board.save(p, quality=85)
        made.append(p)
    return made


def spoken(words, a, b):
    return "".join(w["w"] for w in words if a - 0.1 <= w["s"] < b)


def screen_text(beat):
    parts = []
    for k in ("words", "hits", "text", "pre", "post", "sub"):
        v = beat.get(k)
        if isinstance(v, list):
            parts += [str(x) for x in v]
        elif isinstance(v, str):
            parts.append(v)
    return PUN.sub("", "".join(parts))


def caption_dups(vpath):
    v = json.loads(vpath.read_text())
    meta = v.get("meta", {})
    if not meta.get("words"):
        return [], 0
    words = json.loads((vpath.parent / meta["words"]).read_text())
    words = [w for x in words for w in (x["words"] if "words" in x else [x])]
    beats = [b for b in v["beats"] if isinstance(b.get("t"), (int, float))]
    dups, texty = [], 0
    for i, b in enumerate(beats):
        if b.get("fx") not in TEXT_FX:
            continue
        txt = screen_text(b)
        if not txt:
            continue
        texty += 1
        end = beats[i + 1]["t"] if i + 1 < len(beats) else b["t"] + 6
        line = PUN.sub("", spoken(words, b["t"], end + 1.0))
        if all(ch in line for ch in txt):
            dups.append((b["t"], b["fx"], txt))
    return dups, texty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("film")
    ap.add_argument("--video", help="the video.json it was built from (enables caption-dup and fx-repeat)")
    ap.add_argument("--out")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a P0 is found")
    a = ap.parse_args()
    film = Path(a.film).resolve()
    out = Path(a.out).resolve() if a.out else film.parent / f"review_{film.stem}"
    out.mkdir(parents=True, exist_ok=True)
    dur = probe(film)
    found = []

    body_end = dur - 1.5
    for s, e in freezes(film, dur):
        if s < body_end and min(e, body_end) - s > 2.5:
            found.append(("P0", "freeze", f"{s:.1f}–{e:.1f}s 画面 {e - s:.1f} 秒没有变化"))
    cuts = scene_changes(film)
    early = [c for c in cuts if c <= 2.0]
    fr = freezes(film, dur)
    if not early and any(s <= 0.2 and e >= 2.0 for s, e in fr):
        found.append(("P0", "hook", "前 2 秒画面没有任何变化"))
    edges = [0.0] + cuts + [dur]
    for x, y in zip(edges, edges[1:]):
        if y - x > 6.0:
            found.append(("P1", "cut-gap", f"{x:.1f}–{y:.1f}s {y - x:.1f} 秒没有切换"))

    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        files = frames(film, tmp)
        flats = [flat(Image.open(f)) > 0.82 for f in files]
        made = sheets(files, out)
    ratio = sum(flats) / max(1, len(flats))
    run, best, best_at = 0, 0, 0
    for i, x in enumerate(flats):
        run = run + 1 if x else 0
        if run > best:
            best, best_at = run, i - run + 1
    if ratio > 0.30:
        found.append(("P0", "slides", f"{ratio:.0%} 的画面是纯色底 + 少量文字（最长一段 {best_at / 2:.1f}s 起 {best / 2:.1f} 秒）"))
    elif ratio > 0.15:
        found.append(("P1", "slides", f"{ratio:.0%} 的画面是纯色底 + 少量文字"))

    if a.video:
        vpath = Path(a.video).resolve()
        dups, texty = caption_dups(vpath)
        if dups:
            level = "P0" if texty and len(dups) / texty > 0.30 else "P1"
            found.append((level, "caption-dup", f"{len(dups)}/{texty} 个大字镜头只是在重复字幕：" +
                          "；".join(f"{t:.1f}s {fx}「{txt}」" for t, fx, txt in dups[:8])))
        counts = {}
        for b in json.loads(vpath.read_text())["beats"]:
            if b.get("scene") == "fx":
                counts[b["fx"]] = counts.get(b["fx"], 0) + 1
        for fx, n in sorted(counts.items(), key=lambda x: -x[1]):
            if n > 3:
                found.append(("P1", "fx-repeat", f"{fx} 用了 {n} 次"))

    lines = [f"# 自检：{film.name}", "", f"时长 {dur:.1f}s · 静帧板 {len(made)} 张（每秒 2 帧）", "", "## 自动检查", ""]
    lines += [f"- **{lv}** `{rule}` {msg}" for lv, rule, msg in found] or ["- 没有发现自动可查的问题"]
    lines += ["", "## 逐张看静帧板后打分（1–10，每项 ≥ 8 才交付）", "",
              "| 项 | 分 | 最差的地方 |", "|---|---|---|",
              "| 钩子：只看前 2 秒会不会继续看 | | |", "| 手机可读：每屏要读的字读得清 | | |",
              "| 节奏：没有 2.5 秒不变的地方 | | |", "| 信息：画面给出字幕之外的东西 | | |",
              "| 多样：版式 / 颜色 / 效果没有一种用到底 | | |", "| 相关：每个画面和那句话有关 | | |",
              "", "## 最差的 3 个问题 → 怎么改", "", "1. ", "2. ", "3. "]
    (out / "review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for lv, rule, msg in found:
        print(f"  {lv} {rule:<12} {msg}")
    print(f"静帧板：{', '.join(p.name for p in made)}  →  {out}")
    print("逐张看完再按 review.md 打分；每项 ≥ 8 才交付。")
    if a.strict and any(lv == "P0" for lv, _, _ in found):
        sys.exit(1)


if __name__ == "__main__":
    main()
