#!/usr/bin/env python3
"""A ~2.5-minute "long talk" for the cut_list demo: the five example narrations joined end to end (our own audio),
with their word timestamps shifted onto the joined file. No TTS, no speech recognition."""
import json, subprocess
from pathlib import Path

EX = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "talk"
PARTS = ["mixue", "screen", "atlas", "doc", "poster"]


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def main():
    OUT.mkdir(exist_ok=True)
    words, t, inputs = [], 0.0, []
    for name in PARTS:
        meta = json.loads((EX / name / "video.json").read_text())["meta"]
        voice, wj = EX / name / meta["voice"], EX / name / meta["words"]
        data = json.loads(wj.read_text())
        ws = [w for x in data for w in (x["words"] if isinstance(x, dict) and "words" in x else [x])]
        for w in ws: words.append({"w": w.get("w", w.get("t", "")), "s": round(w["s"] + t, 3), "e": round(w["e"] + t, 3)})
        inputs.append(str(voice)); t += dur(voice) + 0.9
    f = "".join(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur=0.9[a{k}];" for k in range(len(inputs)))
    f += "".join(f"[a{k}]" for k in range(len(inputs))) + f"concat=n={len(inputs)}:v=0:a=1[o]"
    cmd = ["ffmpeg", "-v", "error", "-y"] + sum([["-i", i] for i in inputs], []) + ["-filter_complex", f, "-map", "[o]", str(OUT / "talk.wav")]
    subprocess.run(cmd, check=True)
    (OUT / "talk_words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(OUT / "talk.wav", f"{t:.1f}s", len(words), "words")


if __name__ == "__main__":
    main()
