#!/usr/bin/env python3
"""Measure a reference video's cutting rhythm and map it onto a storyboard — picture only, no speech recognition.

  python3 scripts/ref_pacing.py ref.mp4 [--video work/video.json] [--apply] [--threshold 0.3] [--out pacing.json]

1. ffmpeg scene detection (select='gt(scene,T)' + showinfo) finds the cuts; shots shorter than 0.25 s are merged.
2. Reports shots / minute, median / p25 / p75 shot length, the share of very short shots (< 1 s) and the rhythm over
   time (shots per 10 s window), so "the reference cuts every 1.6 s and speeds up in the last third" is a number.
3. With --video: every beat longer than the reference's p75 is flagged, with how many cuts the reference would put in
   that span. --apply writes those as `"cuts"` hints on the beats (and `"tr": "hard"` between beats when the reference
   uses hard cuts), into <video>.paced.json — the storyboard is never overwritten.
"""
import argparse, json, re, statistics, subprocess
from pathlib import Path


def cuts(path, thr):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-vf", f"select='gt(scene,{thr})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    ts = [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]))
    out = [0.0]
    for t in ts:
        if t - out[-1] >= 0.25: out.append(t)
    return out, d


def stats(bounds, d):
    shots = [b - a for a, b in zip(bounds, bounds[1:] + [d]) if b - a > 0]
    q = statistics.quantiles(shots, n=4) if len(shots) >= 4 else [min(shots), statistics.median(shots), max(shots)]
    win = [sum(1 for b in bounds if k <= b < k + 10) for k in range(0, int(d) + 1, 10)]
    return {"duration": round(d, 2), "shots": len(shots), "per_min": round(len(shots) / d * 60, 1), "median": round(statistics.median(shots), 2),
            "p25": round(q[0], 2), "p75": round(q[-1], 2), "short_share": round(sum(s < 1 for s in shots) / len(shots), 2),
            "per_10s": win, "cuts": [round(b, 2) for b in bounds[1:]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ref"); ap.add_argument("--video"); ap.add_argument("--apply", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.3); ap.add_argument("--out")
    a = ap.parse_args()
    b, d = cuts(a.ref, a.threshold)
    st = stats(b, d)
    print(f"{Path(a.ref).name}: {st['shots']} shots in {d:.1f} s · {st['per_min']}/min · median {st['median']} s "
          f"(p25 {st['p25']}, p75 {st['p75']}) · {int(st['short_share'] * 100)}% under 1 s")
    print("  shots per 10 s:", " ".join(map(str, st["per_10s"])))
    res = {"reference": str(a.ref), **st}
    if a.video:
        vp = Path(a.video); v = json.loads(vp.read_text())
        beats = v["beats"]
        flags = []
        for i, bt in enumerate(beats):
            dd = bt.get("d")
            if isinstance(dd, (int, float)) and dd > st["p75"]:
                n = max(0, round(dd / st["median"]) - 1)
                flags.append({"beat": i, "d": dd, "ref_cuts": n})
                if a.apply and n: bt["cuts"] = n
        if a.apply:
            for bt in beats[1:]: bt.setdefault("tr", "hard")
            outp = vp.with_suffix(".paced.json"); outp.write_text(json.dumps(v, ensure_ascii=False, indent=1))
            print("  →", outp)
        res["beats_over_p75"] = flags
        if flags: print(f"  {len(flags)} beat(s) longer than the reference's p75 — the reference would cut inside them:", flags[:6])
        else: print("  (beats without explicit d are timed from the narration; pass a built storyboard to compare, or read the numbers above)")
    out = Path(a.out) if a.out else Path(a.ref).with_suffix(".pacing.json")
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print("  →", out)


if __name__ == "__main__":
    main()
