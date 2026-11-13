#!/usr/bin/env python3
"""Timed captions for the editorial example, which is silent: writes assets/audio/words.json from the lines below at a
calm reading pace (4.6 glyphs/s; 0.22 s after ，、 and 0.45 s after 。), each line starting 0.35 s into its page.
The beats in video.json are pinned to the same page times.

  python3 examples/editorial/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGES = [   # (page start, caption)
    (0.0, "优衣库母公司迅销，2024 财年交卷。"),
    (4.4, "赚得更多：营业利润同比涨了三成。"),
    (9.2, "营收首破三万亿日元，公司预计再涨一成。"),
    (14.4, "增长主要来自日本以外。"),
    (18.8, "两边摆在一起，差距一眼可见。"),
    (23.6, "集团营收里，一半以上来自海外优衣库。"),
    (28.4, "光是大中华区，就开着一千多家店。"),
    (33.2, "这是一家服装公司交出的利润率。"),
]
PUN = "，。：、？！；"
RATE = 4.6
LEAD = 0.35


def main():
    words = []
    for t0, s in PAGES:
        t = t0 + LEAD
        toks = [c for c in s if c.strip()]
        k = 0
        while k < len(toks):
            c = toks[k]
            if c in PUN:
                words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                t += 0.45 if c in "。？！" else 0.22
                k += 1
                continue
            if c.isascii() and c.isalnum():        # a Latin word or a number ("2024") is one token
                j = k
                while j < len(toks) and toks[j].isascii() and toks[j].isalnum():
                    j += 1
                w = "".join(toks[k:j])
                dur = 0.16 * len(w) + 0.1
                words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                t += dur
                k = j
                continue
            words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
            t += 1 / RATE
            k += 1
        print(f"{t0:5.1f}  ends {t:5.2f}  {s}")
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens")


if __name__ == "__main__":
    main()
