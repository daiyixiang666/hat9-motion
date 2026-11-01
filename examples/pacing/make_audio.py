#!/usr/bin/env python3
"""Re-time the 《一杯 4 块钱的柠檬水》 narration with silences in it, for the pacing demo (no TTS).

  python3 examples/pacing/make_audio.py      -> assets/audio/voice.mp3 + words.json + timeline.json

Takes examples/mixue/assets/audio/{voice.mp3, words.json}, cuts it at sentence (or word) boundaries and puts the
silent moments in between: a cold open before the first word, a mid-sentence suspense hold, a B-roll interlude, a
music-only beat-cut section and a breather after the 金句. Until the pipeline has meta.lead / gaps, this is how a
silent moment is made: in the audio, not in the picture.
"""
import json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "mixue" / "assets" / "audio"
SR = 48000
PUN = "，。、？！：；"

words = json.loads((SRC / "words.json").read_text())
raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(SRC / "voice.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
audio = np.frombuffer(raw, dtype=np.float32)

# sentence index -> list of word indices (punctuation included)
sents, cur = [], []
for i, w in enumerate(words):
    cur.append(i)
    if w["w"] in "。？！": sents.append(cur); cur = []
if cur: sents.append(cur)


def span(ids):
    chars = [i for i in ids if words[i]["w"] not in PUN]
    return words[chars[0]]["s"], words[chars[-1]]["e"]


def split(ids, after):
    """split a sentence's word ids right after the text `after`."""
    txt = "".join(words[i]["w"] for i in ids)
    k = txt.index(after) + len(after)
    # skip punctuation that follows the split point into the first half
    while k < len(ids) and words[ids[k]]["w"] in PUN: k += 1
    return ids[:k], ids[k:]


s0a, s0b = split(sents[0], "净赚")
PLAN = [("sil", 3.0, "cold_open"), ("say", s0a, "s0a"), ("sil", 1.15, "suspense_hold"), ("say", s0b, "s0b"), ("sil", 0.35, None),
        ("say", sents[1], "s1"), ("sil", 2.8, "interlude"), ("say", sents[2], "s2"), ("sil", 3.6, "beat_cut"),
        ("say", sents[9], "s9"), ("sil", 2.6, "breather"), ("say", sents[10], "s10")]

out, ow, marks, pos = [], [], {}, 0.0
for kind, val, tag in PLAN:
    if kind == "sil":
        out.append(np.zeros(int(val * SR), dtype=np.float32))
        if tag: marks[tag] = [round(pos, 3), round(pos + val, 3)]
        pos += val
        continue
    a, b = span(val)
    a0, b0 = max(0.0, a - 0.04), b + 0.14
    seg = audio[int(a0 * SR):int(b0 * SR)].copy()
    fade = int(0.012 * SR); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
    out.append(seg)
    for i in val:
        w = words[i]
        ow.append({"w": w["w"], "s": round(w["s"] - a0 + pos, 3), "e": round(w["e"] - a0 + pos, 3)})
    marks[tag] = [round(pos, 3), round(pos + (b0 - a0), 3)]
    pos += b0 - a0

pcm = np.concatenate(out)
(HERE / "assets" / "audio").mkdir(parents=True, exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "libmp3lame", "-b:a", "160k",
                str(HERE / "assets" / "audio" / "voice.mp3")], input=pcm.tobytes(), check=True)
(HERE / "assets" / "audio" / "words.json").write_text(json.dumps(ow, ensure_ascii=False))
(HERE / "assets" / "audio" / "timeline.json").write_text(json.dumps({"duration": round(pos, 3), "marks": marks}, ensure_ascii=False, indent=1))
print(round(pos, 3), json.dumps(marks, ensure_ascii=False))
