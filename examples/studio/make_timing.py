#!/usr/bin/env python3
"""Timed captions for the studio example (a silent film): writes assets/audio/words.json from the captions below at a
steady reading pace inside each beat's slot, so the subtitle pages have real times. Each caption is one complete
sentence of at most 16 glyphs, so a page never breaks at a comma. Beat start times in video.json follow SLOTS.

  python3 examples/studio/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLOTS = [4.6, 4.4, 4.8, 4.4, 4.8, 5.0, 4.4, 5.4]
CAPS = [
    ["苹果一年净销售额4162亿美元"],
    ["iPhone一项就占了50.4%"],
    ["iPhone之后是服务和可穿戴"],
    ["服务收入涨到1092亿美元"],
    ["研发一年花了346亿美元", "约占净销售额的8.3%"],
    ["净销售额五年涨了13.8%"],
    ["每卖100美元毛利46.9美元"],
    ["三个数看懂苹果这一年"],
]
LEAD = [1.0, 0.45, 0.45, 0.45, 0.45, 0.45, 0.45, 0.9]     # the caption arrives with the camera
TAIL = 0.55          # gap before the next beat's flight
PAUSE = 0.35


def tokens(s):
    out, k = [], 0
    while k < len(s):
        c = s[k]
        if c.isascii() and (c.isalnum() or c in ".%,"):        # a Latin / number run is one token
            j = k
            while j < len(s) and s[j].isascii() and (s[j].isalnum() or s[j] in ".%,"):
                j += 1
            out.append(s[k:j])
            k = j
            continue
        if c.strip():
            out.append(c)
        k += 1
    return out


def main():
    words, t0 = [], 0.0
    for slot, caps, lead in zip(SLOTS, CAPS, LEAD):
        room = (slot - lead - TAIL - PAUSE * (len(caps) - 1)) / len(caps)
        t = t0 + lead
        for c in caps:
            toks = tokens(c)
            step = room / len(toks)
            for w in toks:
                words.append({"w": w, "s": round(t, 3), "e": round(t + step, 3)})
                t += step
            words.append({"w": "。", "s": round(t, 3), "e": round(t, 3)})
            t += PAUSE
        t0 += slot
    out = HERE / "assets" / "audio" / "words.json"
    out.write_text(json.dumps(words, ensure_ascii=False))
    starts = [round(sum(SLOTS[:i]), 2) for i in range(len(SLOTS))]
    print(f"{len(words)} tokens, beat starts {starts}, film ends {t0:.2f} s -> {out}")


if __name__ == "__main__":
    main()
