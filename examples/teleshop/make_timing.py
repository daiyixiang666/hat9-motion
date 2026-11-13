#!/usr/bin/env python3
"""Timed beats for the teleshop example (a silent film with captions): writes assets/audio/words.json from the script
below at a calm reading pace (4.4 glyphs/s; 0.22 s after ，、 and 0.45 s after 。？), and holds every sentence on screen
for at least HOLD seconds so each card has time to finish. Captions and every "@词" cue in video.json use these times.

  python3 examples/teleshop/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SENTS = [
    "海底捞全年收入427.55亿元。",
    "年度利润同比增长4.6%。",
    "最大的开支是原材料和员工。",
    "人均消费反而降到97.5元。",
    "翻台率涨到每天4.1次。",
    "年底共有1368家海底捞门店。",
    "收入的94.5%来自海底捞餐厅。",
    "这就是海底捞的2024年。",
]
HOLD = [4.6, 4.4, 4.6, 4.3, 4.3, 4.6, 4.5, 4.2]
PUN = "，。：、？！；"
RATE = 4.4
LEAD = 0.7


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
