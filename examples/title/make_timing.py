#!/usr/bin/env python3
"""Timed beats for the title example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.5 glyphs/s; 0.22 s after ，、 and 0.5 s after 。：), so captions and every "@词" cue in
video.json have real times.

  python3 examples/title/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "2024年底，Netflix付费会员到了3.02亿。",
    "第四季度一口气净增1891万，单季最多。",
    "全年加起来，净增会员4136万。",
    "股东信原话：史上净增最多的一个季度。",
    "全年营收，从337亿美元涨到390亿美元。",
    "营业利润率，从20.6%提到26.7%。",
    "第四季度，广告国家里超过55%的新注册，选了广告套餐。",
    "就在同一天，美国等四国多数套餐宣布涨价。",
]
PUN = "，。：、？！；《》"
RATE = 4.5
LEAD = 0.5


def main():
    words = []
    t = LEAD
    for s in SENTS:
        toks = [c for c in s if c.strip()]
        k = 0
        while k < len(toks):
            c = toks[k]
            if c in PUN:
                words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                if c in "。？：！":
                    t += 0.5
                else:
                    t += 0.22
                k += 1
                continue
            if c.isascii() and c.isalnum():
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
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
