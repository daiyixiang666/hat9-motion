#!/usr/bin/env python3
"""Timed captions for the bauhaus example (a silent film): writes assets/audio/words.json from the script below at a
steady reading pace (4.6 glyphs/s; 0.22 s after ，：、, 0.7 s after 。), so the subtitles and every "@词" cue in
video.json have real times. Each sentence is one beat.

  python3 examples/bauhaus/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "FY24，宜家全球零售额 451 亿欧元。",
    "比上一年少 5.3%，涨上去又退了回来。",
    "因为降价：给门店的批发价，平均降 10%。",
    "集团 CEO 亲口说的，一个市场都没落下。",
    "这些市场分给 12 家加盟商，英格卡管 31 个。",
    "门店来了 8.99 亿人次，网站来了 46 亿次。",
    "钱从哪来：71% 门店，26% 线上，3% 服务。",
    "价格降了，人来得更多，零售额少了 5.3%。",
]
PUN = "，。：、？！；"
RATE = 4.6
LEAD = 0.4


def main():
    words, t = [], LEAD
    for s in SENTS:
        k = 0
        toks = [c for c in s if c.strip()]
        while k < len(toks):
            c = toks[k]
            if c in PUN:
                words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                t += 0.7 if c == "。" else 0.22
                k += 1
                continue
            if c.isascii() and (c.isalnum() or c in ".%"):      # a Latin / number run ("FY24", "5.3%") is one token
                j = k
                while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] in ".%"):
                    j += 1
                w = "".join(toks[k:j])
                dur = 0.12 * len(w) + 0.15
                words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                t += dur
                k = j
                continue
            words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
            t += 1 / RATE
            k += 1
    out = HERE / "assets" / "audio" / "words.json"
    out.write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s -> {out}")


if __name__ == "__main__":
    main()
