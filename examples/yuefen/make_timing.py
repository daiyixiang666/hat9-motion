#!/usr/bin/env python3
"""Timed beats for the yuefen example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.4 glyphs/s; 0.22 s after ，、 and 0.45 s after 。？), and holds every sentence on screen
for at least HOLD seconds so each card has time to finish. Captions and every "@词" cue in video.json use these times.

  python3 examples/yuefen/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "2024年，茅台一年卖了多少钱？",
    "营业收入一年一个台阶，三年涨了近四成。",
    "茅台酒卖的钱，是系列酒的5.9倍。",
    "直销渠道的份额，比上一年反而降了。",
    "每卖100元酒，成本还不到8元。",
    "最大一笔开支是营业成本，研发最少。",
    "收入里将近一半，变成了归母净利润。",
    "这就是一瓶白酒的年度账本。",
]
HOLD = [4.4, 4.6, 4.3, 4.6, 4.4, 4.4, 4.4, 4.2]
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
