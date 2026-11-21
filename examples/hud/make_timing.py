#!/usr/bin/env python3
"""Timed beats for the hud example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.4 glyphs/s; 0.22 s after ，、 and 0.45 s after 。), and holds every sentence on screen
for at least HOLD seconds so each instrument has time to settle. Captions and every "@词" cue in video.json use these times.

  python3 examples/hud/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "2024年营收少了近一成。",
    "营收降了净利润却涨了15%。",
    "动力电池全球市占率37.9%。",
    "七成收入来自动力电池。",
    "一年研发投入186亿元。",
    "五年间营收涨到七倍多。",
    "约三成收入来自境外。",
    "这就是宁德时代的2024。",
]
HOLD = [4.6, 4.8, 4.6, 4.6, 4.3, 4.8, 4.5, 4.2]
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
            if c.isascii() and (c.isalnum() or c == "%"):        # a number ("2024", "37.9%") is one token
                j = k
                while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] in ".%"):
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
    for w in words:
        w["est"] = True          # estimated from the text: a recording added later re-times the film
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
