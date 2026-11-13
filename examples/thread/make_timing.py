#!/usr/bin/env python3
"""Timed captions for the thread example (a silent film): writes assets/audio/words.json from the script below at a
steady reading pace (4.6 glyphs/s) inside a fixed slot per beat, so the subtitles and every "@词" cue in video.json
have real times. The first beat starts after the opening push-in.

  python3 examples/thread/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
# one entry per beat: (slot in seconds, [captions]). Every caption is one complete statement of at most 16 glyphs,
# so each subtitle page reads on its own; beat 8's second line comes with the last stop of the camera.
BEATS = [
    (4.5, ["小米 2024 年收入 3,659 亿元"]),
    (4.4, ["手机一项就收入 1,918 亿元"]),
    (5.2, ["手机全年出货 1.685 亿台", "手机毛利率只有 12.6%"]),
    (4.2, ["造车第一年交付 13.7 万辆"]),
    (4.4, ["汽车毛利率是手机的 1.5 倍"]),
    (5.0, ["卖车的毛利有 60.5 亿元", "算上费用汽车亏 62 亿元"]),
    (4.2, ["集团经调整净利润 272 亿元"]),
    (6.5, ["一条线走完小米的 2024 年", "三个数看懂小米这一年"]),
]
RATE = 4.6
LEAD = 1.2
PAUSE = 0.6           # between two captions of one beat
LAST_AT = 3.1         # beat 8: the second caption starts when the camera reaches the summary card


def say(words, s, t, stretch=1.0):
    toks = [c for c in s if c.strip()]
    k = 0
    while k < len(toks):
        c = toks[k]
        if c.isascii() and (c.isalnum() or c in ".%,"):      # a Latin / number run ("1,138", "18.5%") is one token
            j = k
            while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] in ".%,"):
                j += 1
            w = "".join(toks[k:j])
            dur = (0.12 * len(w) + 0.15) * stretch
            words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
            t += dur
            k = j
            continue
        words.append({"w": c, "s": round(t, 3), "e": round(t + stretch / RATE, 3)})
        t += stretch / RATE
        k += 1
    words.append({"w": "。", "s": round(t, 3), "e": round(t, 3)})
    return t


def main():
    words, t0 = [], LEAD
    for bi, (slot, caps) in enumerate(BEATS):
        t = t0
        for ci, c in enumerate(caps):
            if bi == len(BEATS) - 1:          # the wide shot, then the summary card: each caption fills its own part
                room = (LAST_AT - PAUSE) if ci == 0 else (slot - LAST_AT - 0.9)
                t = max(t, t0 + LAST_AT) if ci == 1 else t
            else:            # the captions of a beat stay up for most of it (the reading pace slows, never speeds up)
                room = (slot - 0.9) / len(caps) - PAUSE
            natural = say([], c, 0.0)
            t = say(words, c, t, max(1.0, room / natural)) + PAUSE
        t0 += slot
    out = HERE / "assets" / "audio" / "words.json"
    out.write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, film ends {t0:.2f} s -> {out}")


if __name__ == "__main__":
    main()
