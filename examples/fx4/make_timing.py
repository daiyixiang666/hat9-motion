#!/usr/bin/env python3
"""Timed captions for the fx4 example (a silent film with captions): writes assets/audio/words.json from the
script below. Each beat starts where the one before it ends (lengths in BEATS); its sentences are laid out from
0.35 s after the beat starts at 5.6 glyphs/s (0.4 s after 。？), so captions and every "@词" cue in video.json have
real times.

  python3 examples/fx4/make_timing.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BEATS = [   # (beat length in s, sentences)
    (5.0, ["这个仓库有188个效果。", "外加17种转场。"]),
    (6.0, ["第一关需求单：写video.json。", "一句一个beat。"]),
    (5.5, ["分镜检查先算一遍：", "reel示例纯文字占25%。"]),
    (4.5, ["第二关静帧板，哪页只有字一眼看出。"]),
    (5.5, ["第三关小样，只做最难的4秒。", "字幕按时间一段段对上。"]),
    (6.0, ["第四关整片，横竖屏各渲一遍。", "mixue示例全程2分45秒。"]),
    (3.0, ["第五关快切，有实拍才用。"]),
    (6.0, ["第六关自检，逐帧过一遍。", "字号不够，这一项打了叉。"]),
    (5.8, ["26种风格，各一条示例片。", "都从一份video.json开始。"]),
]
PUN = "，。：、？！；"
RATE = 5.6


def main():
    words = []
    start = 0.0
    for i, (d, sents) in enumerate(BEATS):
        t = start + 0.35
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
        end = start + d
        if t > end - 0.1:
            print(f"beat {i + 1}: script runs to {t:.2f} s, past the beat end {end:.2f} s")
        start = end
    out = HERE / "assets" / "audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"{len(words)} tokens, film {start:.1f} s")


if __name__ == "__main__":
    main()
