#!/usr/bin/env python3
"""Timed beats for the clay example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.8 glyphs/s; 0.5 s after a sentence, 1.0 s after a beat's last sentence; the last glyph
holds through the pause so the caption stays up), so the captions and every "@词" cue in video.json have real times.

  python3 examples/clay/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEATS = [
    ["乐高公布了2024年报。", "全年收入743亿丹麦克朗。"],
    ["比上一年增长了13%。", "玩具市场却下滑了1%。"],
    ["营业利润从171亿涨到187亿。"],
    ["840款产品里46%是新品。"],
    ["年底门店一共1069家。", "七成多是认证零售店。"],
    ["五年收入从437亿涨到743亿。"],
    ["认证质量平衡采购从18%升到47%。"],
    ["这就是乐高的2024年。"],
]
PUN = "，。：、？！；"
RATE = 4.8
LEAD = 0.6


def main():
    words = []
    t = LEAD
    for sents in BEATS:
        for si, s in enumerate(sents):
            toks = [c for c in s if c.strip()]
            k = 0
            while k < len(toks):
                c = toks[k]
                if c in PUN:
                    pause = 1.0 if si == len(sents) - 1 else 0.5
                    if words:          # the sentence's last glyph holds through the pause: its caption page stays up
                        words[-1]["e"] = round(t + pause - 0.12, 3)
                    words.append({"w": c, "s": round(t, 3), "e": round(t, 3)})
                    t += pause
                    k += 1
                    continue
                if c.isascii() and c.isalnum():
                    j = k
                    while j < len(toks) and toks[j].isascii() and (toks[j].isalnum() or toks[j] in ".%"):
                        j += 1
                    w = "".join(toks[k:j])
                    dur = 0.13 * len(w) + 0.12
                    words.append({"w": w, "s": round(t, 3), "e": round(t + dur, 3)})
                    t += dur
                    k = j
                    continue
                words.append({"w": c, "s": round(t, 3), "e": round(t + 1 / RATE, 3)})
                t += 1 / RATE
                k += 1
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    for w in words:
        w["est"] = True          # estimated from the text: a recording added later re-times the film
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, {t:.2f} s")


if __name__ == "__main__":
    main()
