#!/usr/bin/env python3
"""README hero + showcase files from a finished example: the 16:9 and 9:16 renders side by side, same moments.

  python3 scripts/hero.py examples/mixue --cuts 0.2-2.6,4.2-6.6,7.6-8.8,14.2-15.8,19.6-21.0,22.6-24.0

Writes assets/previews/hero.webp (animated, both aspects in sync), <name>_16x9.mp4 / _9x16.mp4 (web-size) and
their poster .jpg. Needs ffmpeg + Pillow.
"""
import argparse, subprocess, tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
OUT = SKILL / "assets" / "previews"


def run(*a): subprocess.run(a, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("example"); ap.add_argument("--cuts", required=True); ap.add_argument("--style", default="press")
    ap.add_argument("--name", default=None); ap.add_argument("--poster", type=float, default=2.6)
    ap.add_argument("--h", type=int, default=520); ap.add_argument("--fps", type=int, default=12)
    a = ap.parse_args()
    ex = Path(a.example).resolve(); name = a.name or ex.name
    h16, h9 = ex / "renders" / f"{a.style}_16x9.mp4", ex / "renders" / f"{a.style}_9x16.mp4"
    cuts = [tuple(map(float, c.split("-"))) for c in a.cuts.split(",")]
    sel = "+".join(f"between(t,{s},{e})" for s, e in cuts)
    OUT.mkdir(parents=True, exist_ok=True)
    # web-size films + posters
    for src, tag, w in ((h16, "16x9", 1280), (h9, "9x16", 720)):
        run("ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"scale={w}:-2", "-c:v", "libx264", "-preset", "slow", "-crf", "25",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(OUT / f"{name}_{tag}.mp4"))
        run("ffmpeg", "-v", "error", "-y", "-ss", str(a.poster), "-i", str(src), "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "3", str(OUT / f"{name}_{tag}.jpg"))
    # hero: the same moments from both aspects, side by side on a dark card
    H = a.h; W16 = round(H * 16 / 9 / 2) * 2; W9 = round(H * 9 / 16 / 2) * 2; gap, pad = 24, 28
    fc = (f"[0:v]select='{sel}',setpts=N/FRAME_RATE/TB,fps={a.fps},scale={W16}:{H}:flags=lanczos[a];"
          f"[1:v]select='{sel}',setpts=N/FRAME_RATE/TB,fps={a.fps},scale={W9}:{H}:flags=lanczos[b];"
          f"[a]pad={W16 + gap}:{H}:0:0:color=0x111111[a2];[a2][b]hstack=inputs=2,pad=iw+{2 * pad}:ih+{2 * pad}:{pad}:{pad}:color=0x111111[o]")
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        run("ffmpeg", "-v", "error", "-y", "-i", str(h16), "-i", str(h9), "-filter_complex", fc, "-map", "[o]", f"{td}/f%04d.png")
        frames = [Image.open(p).convert("RGB") for p in sorted(Path(td).glob("f*.png"))]
        frames[0].save(OUT / "hero.webp", save_all=True, append_images=frames[1:], duration=round(1000 / a.fps), loop=0, quality=70, method=5)
    for f in ("hero.webp", f"{name}_16x9.mp4", f"{name}_9x16.mp4"):
        print(OUT / f, f"{(OUT / f).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
