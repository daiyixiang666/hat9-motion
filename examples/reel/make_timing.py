#!/usr/bin/env python3
"""Timed captions for the reel example (a silent film with captions): writes assets/audio/words.json from the
script below. Each beat starts at a fixed time; its sentences are laid out from 0.35 s after the beat starts at
5.6 glyphs/s (0.4 s after 。？), so captions and every "@词" cue in video.json have real times.

  python3 examples/reel/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEAT = 4.8
BEATS = [
    ["拼多多2024年成绩单。", "全年营收3938亿元。"],
    ["营收同比增长59%。", "上一年还是2476亿。"],
    ["净利润1124亿元。", "每100元营收净赚28.5元。"],
    ["收入分成两大块。", "两类收入几乎各占一半。"],
    ["营销费用1113亿元。", "是研发费用的8.8倍。"],
    ["再看四年的营收。", "2024年是2021年4.2倍。"],
    ["3938亿营收去了哪？", "成本拿走最大的一块。"],
    ["这一年记住三个数。", "关注示例频道。"],
]
PUN = "，。：、？！；"
RATE = 5.6


def main():
    words = []
    for i, sents in enumerate(BEATS):
        t = i * BEAT + 0.35
        for s in sents:
            toks = [c for c in s if c.strip()]
            k = 0
            while k < len(toks):
                c = toks[k]
                if c in PUN:
                    words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                    t += 0.4 if c in "。？！" else 0.2
                    k += 1
                    continue
                if c.isascii() and c.isalnum():
                    j = k
                    while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] in ".%"):
                        j += 1
                    w = "".join(toks[k:j])
                    dur = 0.1 * len(w) + 0.1
                    words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                    t += dur
                    k = j
                    continue
                words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
                t += 1 / RATE
                k += 1
        end = (i + 1) * BEAT
        if t > end - 0.1:
            print(f"beat {i + 1}: script runs to {t:.2f} s, past the beat end {end:.2f} s")
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    for w in words:
        w["est"] = True          # estimated from the text: a recording added later re-times the film
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, film {len(BEATS) * BEAT:.1f} s")


if __name__ == "__main__":
    main()
