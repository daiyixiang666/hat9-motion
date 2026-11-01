#!/usr/bin/env python3
"""Test media for the `media` reel: frames pulled from our own showcase films (vector, no third-party footage).

  python3 examples/media/make_frames.py            -> examples/media/assets/frames/<film>_<h|v>_<k>.jpg

Needs the renders in examples/{mixue,screen,atlas,poster}/renders/ (python3 scripts/render.py …). The frames are
build artefacts (gitignored): re-run this after a fresh clone. Also prints the films' real frame counts, which the
reel's lines quote.
"""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
EX = HERE.parent
OUT = HERE / "assets" / "frames"
FILMS = [("mixue", "press"), ("screen", "screen"), ("atlas", "atlas"), ("poster", "poster")]
N_H, N_V = 60, 15            # per film: landscape frames, portrait frames


def frames(src):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
                                 "-show_entries", "stream=nb_read_packets:format=duration", "-of", "json", str(src)])
    j = json.loads(o)
    return int(j["streams"][0]["nb_read_packets"]), float(j["format"]["duration"])


def grab(src, n, dur, tag, w):
    for k in range(n):
        at = dur * (k + 0.5) / n
        dst = OUT / f"{tag}_{k:02d}.jpg"
        if dst.exists(): continue
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.3f}", "-i", str(src), "-frames:v", "1",
                        "-vf", f"scale={w}:-2", "-q:v", "3", str(dst)], check=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for ex, style in FILMS:
        h = EX / ex / "renders" / f"{style}_16x9.mp4"
        v = EX / ex / "renders" / f"{style}_9x16.mp4"
        if not h.exists(): print("missing", h); continue
        nf, dur = frames(h); total += nf
        grab(h, N_H, dur, f"{ex}_h", 960)
        if v.exists(): grab(v, N_V, frames(v)[1], f"{ex}_v", 540)
        print(f"{ex:7s} {nf} frames · {dur:.2f}s")
    print(f"total 16:9 frames: {total:,}  ->  {OUT}  ({len(list(OUT.glob('*.jpg')))} jpg)")


if __name__ == "__main__":
    main()
