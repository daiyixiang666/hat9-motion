#!/usr/bin/env python3
"""Narration for this example on the Windows VoxCPM2 server (no local TTS, no ASR).

  python3 examples/poster/tts_win.py

Clones the channel narrator from examples/mixue (0–2.44 s), synthesises each sentence (2 takes, keeps the one whose
pace is closest to 4.4 glyphs/s), trims the silence, joins with pauses (0.22 s after ，/ 0.40 s after 。：),
loudnorms to −16 LUFS -> assets/audio/voice.mp3, and writes assets/audio/words.json by interpolating each sentence's
glyphs across its voiced span (punctuation weighted as a short pause). Not ASR-checked.
"""
import base64, json, subprocess, urllib.request, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
SERVER = json.loads((Path.home() / "Desktop/test/video/toolkit/local.json").read_text())["ttsServer"]
OUT = HERE / "assets" / "audio"; TMP = OUT / "tts" / "takes"   # intermediates (gitignored)
SENTS = [
    "AI 让每个人都能一口气生成一百个答案。",
    "可问题，从来不是答案不够多。",
    "一九九七年，乔布斯在苹果开发者大会上说：",
    "专注，就是学会说不。",
    "生成变便宜了，判断就变贵了。",
    "你能做出多少张图，不重要。",
    "你敢扔掉多少张，才重要。",
    "选择，才是新的创作。",
    "这里是第九顶帽子。",
]
PUN = "，。：、？！"
SR = 24000


def sh(*a): return subprocess.check_output(a)


def dur(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def synth(text, seed, out):
    ref = TMP / "ref.wav"
    body = {"model": "openbmb/VoxCPM2", "input": text, "response_format": "wav", "seed": seed,
            "ref_audio": "data:audio/wav;base64," + base64.b64encode(ref.read_bytes()).decode(),
            "ref_text": "一杯四块钱的柠檬水，一年净赚四十四亿多。"}
    req = urllib.request.Request(SERVER.rstrip("/") + "/v1/audio/speech", json.dumps(body).encode(), {"Content-Type": "application/json"})
    raw = out.with_suffix(".raw.wav")
    for k in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as r: raw.write_bytes(r.read()); break
        except Exception:
            if k == 2: raise
    sh("ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
       "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse",
       "-ac", "1", "-ar", str(SR), str(out))
    raw.unlink()


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    sh("ffmpeg", "-v", "error", "-y", "-ss", "0", "-t", "2.44", "-i", str(SKILL / "examples/mixue/assets/audio/voice.mp3"), "-ac", "1", "-ar", "24000", str(TMP / "ref.wav"))
    chosen = []
    for i, s in enumerate(SENTS):
        n = sum(1 for c in s if c not in PUN and c.strip())
        best = None
        for seed in (11 + i, 101 + i):
            p = TMP / f"s{i}_{seed}.wav"
            if not p.exists(): synth(s, seed, p)
            d = dur(p); score = abs(d / max(n, 1) - 1 / 4.4)
            print(f"  s{i} seed {seed}: {d:.2f}s  {d / n:.3f}s/glyph")
            if best is None or score < best[0]: best = (score, p, d)
        chosen.append(best)
    # join with pauses; record each sentence's voiced span
    parts, spans, t = [], [], 0.0
    lst = TMP / "concat.txt"; lines = []
    for i, (_, p, d) in enumerate(chosen):
        spans.append((t, t + d)); lines.append(f"file '{p.name}'"); t += d
        if i + 1 < len(chosen):
            g = 0.40 if SENTS[i][-1] in "。：" else 0.22
            gp = TMP / f"gap{int(g * 100)}.wav"
            if not gp.exists(): sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(g), str(gp))
            lines.append(f"file '{gp.name}'"); t += g
    lst.write_text("\n".join(lines))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", str(OUT / "voice.mp3"))
    # words: glyphs evenly over the span, punctuation counts as a 1.4-glyph pause (no ASR)
    words = []
    for s, (a, b) in zip(SENTS, spans):
        toks = [c for c in s if c.strip()]
        w = [1.4 if c in PUN else 1.0 for c in toks]
        if toks[-1] in PUN: w[-1] = 0.0
        unit = (b - a) / sum(w); x = a
        for c, k in zip(toks, w):
            if c in PUN: words.append({"w": c, "s": round(x, 3), "e": round(x, 3)}); x += k * unit
            else: words.append({"w": c, "s": round(x, 3), "e": round(x + unit, 3)}); x += unit
    (OUT / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print("voice", round(t, 2), "s;", len(words), "tokens")


if __name__ == "__main__":
    main()
