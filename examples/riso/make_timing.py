#!/usr/bin/env python3
"""Timed captions for the riso example (a silent film): writes assets/audio/words.json from the lines below at a calm
reading pace (4.6 glyphs/s; a figure such as "169.9" is one token read at 0.2 s per character; 0.22 s after ，、 and
0.45 s after 。), so the captions and every "@词" cue in video.json have real times.

  python3 examples/riso/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "2024 年，名创优品营收 169.9 亿元。",
    "主品牌里，国内 93.3 亿，海外 66.7 亿。",
    "海外一年从 47.1 亿涨到 66.7 亿，增长 41.9%。",
    "海外已占主品牌营收的 41.7%。",
    "海外门店 3118 家，亚洲最多，拉美第二。",
    "毛利率从 41.2% 升到 44.9%，创历史新高。",
    "全年新增的 31.6 亿营收里，62% 来自海外。",
]
PUN = "，。：、？！；《》"
RATE = 4.6
LEAD = 0.3
GAP = 0.25          # extra breath between lines
MIN = 4.45          # every line holds its page at least this long (charts need ≥ 4 s on screen)


def is_fig(c):
    return c.isascii() and (c.isalnum() or c in ".,%")


def main():
    words, t = [], LEAD
    for s in SENTS:
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
            if is_fig(c):
                j = k
                while j < len(toks) and is_fig(toks[j]):
                    j += 1
                w = "".join(toks[k:j])
                dur = 0.2 * len(w) + 0.1
                words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                t += dur
                k = j
                continue
            words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
            t += 1 / RATE
            k += 1
        t = max(t + GAP, t0 + MIN)
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
