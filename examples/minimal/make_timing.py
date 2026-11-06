#!/usr/bin/env python3
"""Timed beats for the minimal example while it has no narration: writes assets/audio/words.json from the script below
at a calm reading pace (4.6 glyphs/s; 0.22 s after ，；、 and 0.45 s after 。？：), so captions and every "@词" cue in
video.json have real times. When a recorded or Windows-TTS voice exists, replace words.json with the aligned one
(scripts/align.py voice.mp3 script.txt) and add meta.voice — the cues stay the same words.

  python3 examples/minimal/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "一颗棉花糖，真能看出一个孩子的未来吗？",
    "一九七二年，斯坦福大学的心理学家米歇尔，做了一个实验。",
    "现在吃，只有一颗；等上十五分钟，就能吃两颗。",
    "多年后回访：当年等得越久的孩子，SAT 分数往往越高。",
    "于是，它成了自控力决定人生最有名的证据。",
    "可二零一三年，罗切斯特大学的研究者换了个问法。",
    "实验前，大人先答应给孩子一套更好的画具。",
    "一组兑现了，一组食言了。",
    "兑现组平均等了约十二分钟，食言组只等了约三分钟。",
    "二零一八年，一项样本更大的重做研究发现，",
    "把家庭背景等因素算进去，这个关联缩小了约三分之二。",
    "孩子没吃那颗糖，未必是自控力更强。",
    "也可能只是，他相信等待真的会有回报。",
]
PUN = "，。：、？！；《》"
RATE = 4.6
LEAD = 0.35


def main():
    words, t = [], LEAD
    for s in SENTS:
        toks = [c for c in s if c.strip()]
        k = 0
        while k < len(toks):
            c = toks[k]
            if c in PUN:
                words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                t += 0.45 if c in "。？：！" else 0.22
                k += 1; continue
            if c.isascii() and c.isalnum():        # a Latin word ("SAT") is one token, read a little faster per letter
                j = k
                while j < len(toks) and toks[j].isascii() and toks[j].isalnum(): j += 1
                w = "".join(toks[k:j]); dur = 0.16 * len(w) + 0.1
                words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)}); t += dur; k = j; continue
            words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)}); t += 1 / RATE
            k += 1
        if s[-1] not in PUN: t += 0.45
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
