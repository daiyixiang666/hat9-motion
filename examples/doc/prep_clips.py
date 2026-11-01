#!/usr/bin/env python3
"""Pre-grade every shot of video.json into assets/clips/<id>.mp4 (starts at 0, covers the shot).

  python3 prep_clips.py --broll <Mixkit 原片目录> [--luts <LUT 目录>]（也可设 H9_MEDIA，读取其下的 broll/ 和 luts/）

Per shot: trim from `in`, optional speed ramp `ramp: [[source_seconds, speed], ...]` (the rest plays at 1×),
scale/crop to 1920×1080 at 30 fps, LUT `lut`, H.264 with a keyframe every 6 frames (frame-accurate seeking).
Shot length comes from the narration cues, resolved with the engine itself.
"""
import os, argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
sys.path.insert(0, str(SKILL / "scripts"))
from h9 import core  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--broll", default=str(Path(os.environ.get("H9_MEDIA", ".")) / "broll"))
    ap.add_argument("--luts", default=str(Path(os.environ.get("H9_MEDIA", ".")) / "luts"))
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    v = json.loads((HERE / "video.json").read_text())
    X = core.Ctx(v, {"motion": {}}, HERE / "build" / "_prep", HERE)
    X.load_words(HERE / v["meta"]["words"])
    beats = v["beats"]
    ts = [X.T(b.get("t", 0)) for b in beats]
    voice = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(HERE / v["meta"]["voice"])]))
    D = voice + float(v["meta"].get("tail", 0.6))
    out = HERE / "assets" / "clips"; out.mkdir(parents=True, exist_ok=True)
    for i, b in enumerate(beats):
        if b["scene"] != "shot" or (a.only and b["id"] not in a.only.split(",")): continue
        d = (ts[i + 1] if i + 1 < len(ts) else D) - ts[i] + 0.6
        src = Path(a.broll) / b["src"]
        inp = float(b.get("in", 0))
        fit = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080"
        lut = f",lut3d=file='{Path(a.luts) / (b['lut'] + '.cube')}'" if b.get("lut") else ""
        segs, pos = [], inp
        for k, (sl, sp) in enumerate(b.get("ramp", [])):
            segs.append(f"[0:v]trim=start={pos}:duration={sl},setpts=(PTS-STARTPTS)/{sp},fps=30,{fit}{lut},setsar=1[r{k}]")
            pos += sl
        n = len(segs)
        segs.append(f"[0:v]trim=start={pos},setpts=PTS-STARTPTS,fps=30,{fit}{lut},setsar=1[r{n}]")
        fc = ";".join(segs) + ";" + "".join(f"[r{k}]" for k in range(n + 1)) + f"concat=n={n + 1}:v=1:a=0,trim=duration={d:.3f}[o]"
        dst = out / f"{b['id']}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", fc, "-map", "[o]", "-an",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-g", "6", "-keyint_min", "6",
                        "-movflags", "+faststart", str(dst)], check=True)
        got = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(dst)]))
        flag = "" if got >= d - 0.65 else "  ! source too short"
        print(f"{b['id']}: {ts[i]:6.2f}s  need {d:.2f}s  got {got:.2f}s  {b['src'].split('/')[-1]}{flag}")


if __name__ == "__main__":
    main()
