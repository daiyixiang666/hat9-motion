#!/usr/bin/env python3
"""Gate 2 — one still per beat on a board, before the film is rendered.

  python3 scripts/stills.py work/video.json [--style press] [--aspect 9:16] [--out work/stills] [--settled]

Builds the project, grabs every beat once its entrance has settled (start + 60 % of the beat, at most 1.2 s in) and
lays the stills out in order with the beat number, time, effect and the line spoken over it. Look at the board as a
viewer on a phone: is every picture readable, different from its neighbours, and about what is being said? Fix the
storyboard and run it again; only then render (or make a sample of the hardest part with sample.py).
--settled adds a second board grabbed 0.35 s before each beat ends (the finished picture: every item revealed).
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brief, review  # noqa: E402

HF = ["npx", "--yes", "hyperframes@0.8.191"]


def snapshot(build_dir, times, out):
    at = ",".join(f"{t:.2f}" for t in times)
    r = subprocess.run(HF + ["snapshot", "--at", at, "--no-end", "-o", str(out), "--json"], cwd=build_dir, capture_output=True, text=True)
    text = r.stdout
    start = text.find("{")
    if r.returncode or start < 0:
        print(r.stdout[-1500:], r.stderr[-1500:])
        raise SystemExit("snapshot failed")
    data = json.loads(text[start:])
    return [f["path"] for f in data["frames"]]


def wrap(text, n):
    lines = []
    while text and len(lines) < 2:
        lines.append(text[:n])
        text = text[n:]
    if text:
        lines[-1] = lines[-1][:-1] + "…"
    return lines


def board(items, out, cols, prefix="board"):
    from PIL import Image, ImageDraw
    first = Image.open(items[0]["png"])
    tw = 300 if first.height > first.width else 480
    th = round(first.height * tw / first.width)
    cap = 70
    head = review.label_font(20)
    body = review.label_font(18)
    per = cols * 3
    made = []
    for s in range(0, len(items), per):
        chunk = items[s:s + per]
        rows = (len(chunk) + cols - 1) // cols
        im = Image.new("RGB", (cols * (tw + 8), rows * (th + cap + 8)), (20, 20, 20))
        d = ImageDraw.Draw(im)
        for k, it in enumerate(chunk):
            x = (k % cols) * (tw + 8)
            y = (k // cols) * (th + cap + 8)
            im.paste(Image.open(it["png"]).convert("RGB").resize((tw, th)), (x, y))
            d.text((x + 6, y + th + 4), f"#{it['i']}  {it['t']:.1f}s  {it['what']}", fill=(255, 210, 0), font=head)
            for j, line in enumerate(wrap(it["said"], tw // 19)):
                d.text((x + 6, y + th + 28 + j * 20), line, fill=(220, 220, 220), font=body)
        p = out / f"{prefix}_{len(made) + 1:02d}.jpg"
        im.save(p, quality=88)
        made.append(p)
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--style")
    ap.add_argument("--aspect")
    ap.add_argument("--out")
    ap.add_argument("--settled", action="store_true", help="also a board of each beat 0.35 s before it ends")
    a = ap.parse_args()
    vpath = Path(a.video).resolve()
    build_dir, tl = brief.build(vpath, a.style, a.aspect)
    out = Path(a.out).resolve() if a.out else vpath.parent / "stills"
    out.mkdir(parents=True, exist_ok=True)
    video = json.loads(vpath.read_text())
    words = review.load_words(vpath)
    lead = tl.get("lead") or 0
    times = []
    for x in tl["beats"]:
        times.append(x["t"] + min(1.2, x["d"] * 0.6))
    pngs = snapshot(build_dir, times, out / "frames")
    items = []
    for x, b, png, t in zip(tl["beats"], video["beats"], pngs, times):
        said = review.spoken(words, x["t"] - lead, x["t"] - lead + x["d"]) if words else ""
        items.append({"i": x["i"], "t": t, "png": png, "what": b.get("fx") or b.get("scene") or "", "said": said})
    landscape = len(pngs) and "16x9" in build_dir.name
    made = board(items, out, 4 if landscape else 6)
    if a.settled:
        late = []
        for x in tl["beats"]:
            late.append(max(x["t"], x["t"] + x["d"] - 0.35))
        pngs2 = snapshot(build_dir, late, out / "frames_settled")
        items2 = []
        for it, png, t in zip(items, pngs2, late):
            items2.append(dict(it, png=png, t=t))
        made += board(items2, out, 4 if landscape else 6, prefix="board_settled")
    print(f"静帧板：{', '.join(p.name for p in made)}  →  {out}")
    print("逐张看：读得清吗？和前后不一样吗？和这句话有关吗？改分镜再跑一遍，过了再渲染。")


if __name__ == "__main__":
    main()
