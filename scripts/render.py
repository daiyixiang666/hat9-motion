#!/usr/bin/env python3
"""build -> check -> render -> (optional) small web preview, for one or many styles.

  python3 scripts/render.py examples/demo/video.json --styles schematic,archive [--aspect 16:9] [--preview]
  python3 scripts/render.py examples/demo/video.json --styles all --preview

Outputs  <video dir>/renders/<style>_<aspect>.mp4  (+ previews/<style>_<aspect>.mp4 and .jpg poster with --preview).
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
HF = ["npx", "--yes", "hyperframes@0.8.191"]


def run(cmd, cwd=None, ok_fail=False):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode and not ok_fail: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f"failed: {' '.join(map(str, cmd))}")
    return r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--styles", default="all"); ap.add_argument("--aspect", default=None)
    ap.add_argument("--preview", action="store_true"); ap.add_argument("--quality", default="standard")
    a = ap.parse_args()
    v = Path(a.video).resolve()
    styles = sorted(p.stem for p in (SKILL / "styles").glob("[!_]*.py")) if a.styles == "all" else a.styles.split(",")
    aspect = a.aspect or json.loads(v.read_text()).get("meta", {}).get("aspect", "16:9")
    tag = aspect.replace(":", "x")
    (v.parent / "renders").mkdir(exist_ok=True)
    for sid in styles:
        out = v.parent / "build" / f"{sid}_{tag}"
        print(f"== {sid}")
        run([sys.executable, str(HERE / "build.py"), str(v), "--style", sid, "--aspect", aspect, "--out", str(out)])
        chk = run(HF + ["check", "--json"], cwd=out, ok_fail=True)
        j = json.loads(chk[chk.find("{"):])
        errs = [(sec, f) for sec, v in j.items() if isinstance(v, dict) for f in v.get("findings", []) if f["severity"] == "error"]
        for sec, f in errs: print(f"  {sec} error", f["code"], f.get("selector", ""), f.get("time", ""), f["message"][:140])
        if errs: continue
        mp4 = v.parent / "renders" / f"{sid}_{tag}.mp4"
        run(HF + ["render", "--quality", a.quality, "--output", str(mp4)], cwd=out)
        print("  ->", mp4)
        if a.preview:
            pv = v.parent / "previews"; pv.mkdir(exist_ok=True)
            w = 1280 if aspect == "16:9" else 720
            run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"scale={w}:-2", "-c:v", "libx264", "-preset", "slow", "-crf", "26",
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "96k", str(pv / f"{sid}_{tag}.mp4")])
            run(["ffmpeg", "-v", "error", "-y", "-ss", "1.2", "-i", str(mp4), "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "4", str(pv / f"{sid}_{tag}.jpg")])


if __name__ == "__main__":
    main()
