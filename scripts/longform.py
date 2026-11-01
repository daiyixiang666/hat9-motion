#!/usr/bin/env python3
"""Long films (10 minutes and up): build and render chapter by chapter, then join them losslessly.

  python3 scripts/longform.py work/video.json [--style press] [--aspect 16:9] [--chapter-len 120] [--jobs 2] [--out work/long]

Chapters: beats with "chapter": true start a new chapter; without any, beats are grouped into chapters of at most
--chapter-len seconds (cut only between beats). For each chapter the script resolves every "@cue" to absolute time,
slices the narration (and music, keeping its position), shifts words and cues to the chapter's own clock, writes
<out>/chNN/video.json, builds and renders it. Chapters render in parallel (--jobs) and are joined with ffmpeg's
concat demuxer (stream copy: same encoder settings, no re-encode) into <out>/<name>.mp4.

Limits: meta.gaps is not applied across chapters (edit the narration first); meta.lead applies to chapter 1 only.
A cut lands between beats, so a sentence that spans two beats is cut there too — put chapter marks on sentence starts.
"""
import argparse, copy, json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h9 import core  # noqa: E402

HF = ["npx", "--yes", "hyperframes@0.8.191"]


def probe(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def resolve(obj, X, after):
    """every "@cue" string -> absolute seconds (first hit after `after`), recursively."""
    if isinstance(obj, dict): return {k: resolve(v, X, after) for k, v in obj.items()}
    if isinstance(obj, list): return [resolve(v, X, after) for v in obj]
    if isinstance(obj, str) and obj.startswith("@"):
        try: return float(X.T(obj, after))
        except SystemExit: return obj
    return obj


def shift(obj, by, keys_time):
    """subtract `by` from absolute times (numbers under cue-like keys)."""
    if isinstance(obj, dict):
        return {k: (round(v - by, 3) if isinstance(v, (int, float)) and not isinstance(v, bool) and (k in keys_time or k.startswith("at")) else shift(v, by, keys_time))
                for k, v in obj.items()}
    if isinstance(obj, list): return [shift(v, by, keys_time) for v in obj]
    return obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--style"); ap.add_argument("--aspect"); ap.add_argument("--chapter-len", type=float, default=120)
    ap.add_argument("--jobs", type=int, default=2); ap.add_argument("--out"); ap.add_argument("--quality", default="standard")
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    vp = Path(a.video).resolve(); src = vp.parent
    v = json.loads(vp.read_text()); meta = v["meta"]
    style = a.style or meta.get("style", "press"); aspect = a.aspect or meta.get("aspect", "16:9")
    out = Path(a.out) if a.out else src / "long"; out.mkdir(parents=True, exist_ok=True)
    X = core.Ctx(v, {"motion": {}}, out, src, aspect)
    if meta.get("words"): X.load_words(src / meta["words"])
    words = json.loads((src / meta["words"]).read_text()) if meta.get("words") else []
    words = [w for x in words for w in (x["words"] if isinstance(x, dict) and "words" in x else [x])]
    voice = src / meta["voice"] if meta.get("voice") else None
    D = probe(voice) + float(meta.get("tail", 0.6)) if voice else float(meta.get("duration", 0))
    # absolute beat starts
    beats, starts, after = [], [], 0.0
    for i, b in enumerate(v["beats"]):
        t = b.get("t", 0 if i == 0 else None)
        t = float(X.T(t, after)) if t is not None else None
        if t is None: t = starts[-1] + float(v["beats"][i - 1].get("d", 3))
        bb = resolve({k: x for k, x in b.items() if k != "t"}, X, t); bb["t"] = t
        beats.append(bb); starts.append(t); after = t
    # chapters
    cuts = [0] + [i for i, b in enumerate(beats) if i and b.get("chapter")]
    if len(cuts) == 1:
        cuts, t0 = [0], 0.0
        for i, t in enumerate(starts):
            if i and t - t0 >= a.chapter_len: cuts.append(i); t0 = t
    ranges = [(cuts[k], cuts[k + 1] if k + 1 < len(cuts) else len(beats)) for k in range(len(cuts))]
    chapters = []
    for k, (i0, i1) in enumerate(ranges):
        t0 = starts[i0]; t1 = starts[i1] if i1 < len(beats) else D
        d = out / f"ch{k + 1:02d}"; (d / "assets").mkdir(parents=True, exist_ok=True)
        cm = copy.deepcopy(meta)
        if k: cm.pop("lead", None)
        cm.pop("gaps", None)
        if voice:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(voice), str(d / "assets" / "voice.wav")], check=True)
            cm["voice"] = "assets/voice.wav"; cm["tail"] = 0.0 if i1 < len(beats) else float(meta.get("tail", 0.6))
        if words:
            cw = [dict(w, s=round(w["s"] - t0, 3), e=round(w["e"] - t0, 3)) for w in words if t0 - 1e-3 <= w["s"] < t1]
            (d / "assets" / "words.json").write_text(json.dumps(cw, ensure_ascii=False)); cm["words"] = "assets/words.json"
        if meta.get("music"):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}", "-i", str(src / meta["music"]), str(d / "assets" / "music.wav")], check=True)
            cm["music"] = "assets/music.wav"
        for key in ("mascot",):
            if cm.get(key): cm[key] = str((src / cm[key]).resolve())
        cm["duration"] = round(t1 - t0, 3)
        cm["beat_offset"], cm["beat_total"] = i0, len(beats)     # page furniture keeps the film's numbering
        cb = []
        for b in beats[i0:i1]:
            nb = shift(b, t0, {"t", "d"})
            for kk, vv in list(nb.items()):        # media paths stay valid from the chapter folder
                if isinstance(vv, str) and (src / vv).exists() and not vv.startswith("@"): nb[kk] = str((src / vv).resolve())
            cb.append(nb)
        (d / "video.json").write_text(json.dumps({"meta": cm, "beats": cb}, ensure_ascii=False, indent=1))
        chapters.append((k + 1, d, t0, t1))
        print(f"chapter {k + 1}: beats {i0}–{i1 - 1}  {t0:.2f}–{t1:.2f} s")

    def job(c):
        n, d, t0, t1 = c
        tag = aspect.replace(":", "x"); b = d / "build" / f"{style}_{tag}"
        subprocess.run([sys.executable, "-W", "ignore", str(HERE / "build.py"), str(d / "video.json"), "--style", style, "--aspect", aspect, "--out", str(b)], check=True,
                       capture_output=True)
        if a.no_render: return None
        mp4 = d / f"ch{n:02d}.mp4"
        subprocess.run(HF + ["render", "--quality", a.quality, "--output", str(mp4.resolve())], cwd=b, check=True, capture_output=True)
        return mp4
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        mp4s = list(ex.map(job, chapters))
    if a.no_render: print("built", len(chapters), "chapters (no render)"); return
    lst = out / "concat.txt"; lst.write_text("".join(f"file '{m.resolve()}'\n" for m in mp4s))
    final = out / f"{vp.stem}_{aspect.replace(':', 'x')}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(final)], check=True)
    print(f"→ {final}  {probe(final):.2f} s (story {D:.2f} s, {len(chapters)} chapters)")


if __name__ == "__main__":
    main()
