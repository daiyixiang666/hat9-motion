#!/usr/bin/env python3
"""Gate 3 — a moving sample of the hardest few seconds (the hook, a quick-cut run), without rendering the film.

  python3 scripts/sample.py work/video.json --range 0,4 [--fps 15] [--style press] [--aspect 9:16] [--out sample.mp4]

Snapshots the range at --fps (exact instants, not frame-snapped), stitches the stills into an mp4 and lays the
narration of that range under it, so timing against the voice can be judged. 4 s at 15 fps is 60 stills — seconds,
not the minutes a full render takes. Watch it; when the feel is right, render the film.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import brief, stills  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--range", required=True, help="start,end in film seconds")
    ap.add_argument("--fps", type=int, default=15)
    ap.add_argument("--style")
    ap.add_argument("--aspect")
    ap.add_argument("--out")
    a = ap.parse_args()
    vpath = Path(a.video).resolve()
    t0, t1 = [float(x) for x in a.range.split(",")]
    build_dir, tl = brief.build(vpath, a.style, a.aspect)
    times = []
    n = int(round((t1 - t0) * a.fps))
    for k in range(n):
        times.append(t0 + k / a.fps)
    out = Path(a.out).resolve() if a.out else vpath.parent / "samples" / f"sample_{t0:g}-{t1:g}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    meta = json.loads(vpath.read_text()).get("meta", {})
    with tempfile.TemporaryDirectory() as tmp:
        pngs = stills.snapshot(build_dir, times, Path(tmp) / "f")
        listing = Path(tmp) / "list.txt"
        lines = []
        for p in pngs:
            lines.append(f"file '{p}'")
            lines.append(f"duration {1 / a.fps:.6f}")
        lines.append(f"file '{pngs[-1]}'")
        listing.write_text("\n".join(lines) + "\n")
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing)]
        voice = meta.get("voice")
        if voice:
            lead = tl.get("lead") or 0
            start = max(0.0, t0 - lead)
            cmd += ["-ss", f"{start:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(vpath.parent / voice)]
            if t0 < lead:
                cmd += ["-af", f"adelay={int((lead - t0) * 1000)}:all=1"]
        cmd += ["-vf", f"fps={a.fps},format=yuv420p", "-c:v", "libx264", "-crf", "20", "-shortest" if voice else "-an", str(out)]
        subprocess.run([c for c in cmd if c], check=True)
    print(f"小样：{out}  （{n} 帧 @ {a.fps}fps，{t1 - t0:.1f} 秒）")


if __name__ == "__main__":
    main()
