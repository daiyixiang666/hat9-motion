#!/usr/bin/env python3
"""Narration for this example on the Windows VoxCPM2 server (no local TTS, no local ASR).

  python3 tts_win.py            -> assets/audio/voice.mp3 (−16 LUFS) + assets/audio/words.json [{w,s,e}]

Per sentence: one remote take cloned from the channel narrator, silence trimmed at both ends, joined with
0.22 s after a comma-ended sentence and 0.40 s after a full stop. Word times have no ASR: each sentence's span
is known exactly, characters are spread evenly over it (punctuation gets no time).
"""
import base64, json, subprocess, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = "http://laptop-johgo8ej.tail3e6c16.ts.net:8000"
REF = HERE.parent / "mixue" / "assets" / "audio" / "voice.mp3"
REF_TEXT = "一杯四块钱的柠檬水，一年净赚四十四亿多。"
SENTENCES = [
    "一九五六年，一个开卡车起家的商人，把装船成本砍掉了百分之九十七。",
    "在那之前，货要靠码头工人一件一件扛上船。",
    "每装一吨，要花五点八三美元。",
    "他把货装进统一尺寸的铁箱子，",
    "第一艘船装了五十八个箱子，每吨只要十六美分。",
    "将近七十年后，上海港一年吞吐五千一百五十万个标准箱。",
    "全球大约八成的货物贸易，走的是海运。",
    "改变世界的，往往不是新发明，而是把成本打下来的人。",
    "这里是第九顶帽子。",
]
PUN = "，。、？！：；"
SR = 24000
OUT = HERE / "assets" / "audio"; TMP = OUT / "takes"


def sh(*a): subprocess.run(a, check=True)


def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def main():
    TMP.mkdir(parents=True, exist_ok=True)
    ref = TMP / "ref.wav"
    sh("ffmpeg", "-v", "error", "-y", "-ss", "0", "-t", "2.44", "-i", str(REF), "-ac", "1", "-ar", str(SR), str(ref))
    ref_b64 = "data:audio/wav;base64," + base64.b64encode(ref.read_bytes()).decode()
    parts, words, t = [], [], 0.0
    for i, s in enumerate(SENTENCES):
        raw, cut = TMP / f"s{i}_raw.wav", TMP / f"s{i}.wav"
        if not cut.exists():
            body = {"model": "openbmb/VoxCPM2", "input": s, "response_format": "wav", "seed": 1000 + i, "ref_audio": ref_b64, "ref_text": REF_TEXT}
            req = urllib.request.Request(SERVER + "/v1/audio/speech", json.dumps(body).encode(), {"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=300) as r: raw.write_bytes(r.read())
            sh("ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
               "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
               "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,atempo=1.04",
               "-ac", "1", "-ar", str(SR), str(cut))
        d = dur(cut)
        glyphs = [c for c in s if c not in PUN]
        k, step = 0, d / max(len(glyphs), 1)
        for c in s:
            if c in PUN:
                e = words[-1]["e"] if words else t
                words.append({"w": c, "s": round(e, 3), "e": round(e, 3)})
            else:
                words.append({"w": c, "s": round(t + k * step, 3), "e": round(t + (k + 1) * step, 3)}); k += 1
        parts.append(cut)
        gap = 0.40 if s.endswith("。") else 0.22
        if i < len(SENTENCES) - 1:
            g = TMP / f"g{i}.wav"
            sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{gap}", str(g))
            parts.append(g)
        t += d + (gap if i < len(SENTENCES) - 1 else 0)
        print(f"  s{i}: {d:.2f}s  {s}")
    lst = TMP / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k", str(OUT / "voice.mp3"))
    (OUT / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"voice.mp3 {dur(OUT / 'voice.mp3'):.2f}s, {len(words)} tokens")


if __name__ == "__main__":
    main()
