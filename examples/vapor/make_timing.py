#!/usr/bin/env python3
"""Timed beats for the vapor example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.4 glyphs/s; 0.22 s after ，、 and 0.45 s after 。？), and holds every sentence on screen
for at least HOLD seconds so each card has time to finish. Captions and every "@词" cue in video.json use these times.

  python3 examples/vapor/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "任天堂上个财年卖了多少钱？",
    "营业收入比前一年少了三成。",
    "硬件出货在年底那季最猛。",
    "软硬件销量都不到上年八成。",
    "卖得最多的是OLED款硬件。",
    "软件收入一半多来自数字版。",
    "每100日元收入有24.3日元营业利润。",
    "这就是任天堂的一年。",
]
HOLD = [4.3, 3.9, 5.0, 4.6, 4.8, 4.6, 4.4, 4.4]
PUN = "，。：、？！；"
RATE = 4.4
LEAD = 0.4


def main():
    words, t = [], LEAD
    for s, hold in zip(SENTS, HOLD):
        t0 = t
        toks = [c for c in s if c.strip()]
        k = 0
        while k < len(toks):
            c = toks[k]
            if c in PUN:
                words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                t += 0.45 if c in "。？：！" else 0.22
                k += 1
                continue
            if c.isascii() and c.isalnum():        # a number ("2024", "5.9") is one token
                j = k
                while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] == "."):
                    j += 1
                w = "".join(toks[k:j])
                dur = 0.12 * len(w) + 0.12
                words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                t += dur
                k = j
                continue
            words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
            t += 1 / RATE
            k += 1
        t = max(t, t0 + hold)
        for w in reversed(words):            # the caption page stays up until the next sentence
            if w["w"] not in PUN:
                w["e"] = round(t - 0.12, 3)
                break
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
