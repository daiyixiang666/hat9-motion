#!/usr/bin/env python3
"""Narration on the Windows VoxCPM2 server (no local TTS, no local ASR).

  python3 tts_win.py            -> assets/audio/voice.mp3 + assets/audio/words.json

Clones the channel narrator from examples/mixue (first sentence), one request per sentence, trims the silence at both
ends, joins with pauses (0.22 s after ，/ 0.4 s after 。？！), loudnorm −16 LUFS. Word times are NOT from ASR: each
sentence's voiced span is split across its characters by weight (CJK 1, Latin letter 0.45, digit 0.6).
"""
import base64, json, subprocess, tempfile, urllib.request, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER = "http://laptop-johgo8ej.tail3e6c16.ts.net:8000"
REF = HERE.parent / "mixue" / "assets" / "audio" / "voice.mp3"
REF_TEXT = "一杯四块钱的柠檬水，一年净赚四十四亿多。"
SENTS = json.loads((HERE / "script.json").read_text())["sentences"]
SR = 24000
PUN = "，。？！、：；"


def sh(*a): subprocess.run(a, check=True)


def dur(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def main():
    td = Path(tempfile.mkdtemp())
    ref = td / "ref.wav"
    sh("ffmpeg", "-v", "error", "-y", "-i", str(REF), "-t", "2.44", "-ac", "1", "-ar", "24000", str(ref))
    ref_b64 = "data:audio/wav;base64," + base64.b64encode(ref.read_bytes()).decode()
    parts, words, t = [], [], 0.0
    for i, s in enumerate(SENTS):
        raw, clean = td / f"s{i}_raw.wav", td / f"s{i}.wav"
        body = {"model": "openbmb/VoxCPM2", "input": s, "response_format": "wav", "seed": 1234 + i,
                "ref_audio": ref_b64, "ref_text": REF_TEXT}
        req = urllib.request.Request(SERVER + "/v1/audio/speech", json.dumps(body).encode(), {"Content-Type": "application/json"})
        for k in range(3):
            try:
                with urllib.request.urlopen(req, timeout=300) as r: raw.write_bytes(r.read()); break
            except Exception as e:
                if k == 2: raise
        sh("ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse,atempo=1.05",
           "-ac", "1", "-ar", str(SR), str(clean))
        d = dur(clean)
        # character weights inside the voiced span
        toks, buf = [], ""
        for ch in s:
            if ch.isascii() and (ch.isalnum() or ch in ".%"): buf += ch; continue
            if buf: toks.append(buf); buf = ""
            if ch.strip(): toks.append(ch)
        if buf: toks.append(buf)
        wt = [0 if x in PUN else (sum(0.6 if c.isdigit() else 0.45 for c in x) if x.isascii() else 1.0) for x in toks]
        W = sum(wt) or 1; acc = t
        for x, w_ in zip(toks, wt):
            e = acc + d * w_ / W
            k = max(len(x), 1)   # one token per glyph (Latin words split) so captions can regroup with jieba
            for j, c in enumerate(x):
                words.append({"w": c, "s": round(acc + (e - acc) * j / k, 3), "e": round(acc + (e - acc) * (j + 1) / k, 3)})
            acc = e
        parts.append((clean, d))
        t += d
        gap = 0.4 if s[-1] in "。？！" else 0.22
        if i < len(SENTS) - 1:
            sil = td / f"g{i}.wav"
            sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", f"{gap}", str(sil))
            parts.append((sil, gap)); t += gap
        print(f"s{i} {d:.2f}s  {s}")
    lst = td / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p, _ in parts))
    out = HERE / "assets" / "audio"
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000",
       "-c:a", "libmp3lame", "-b:a", "192k", str(out / "voice.mp3"))
    # sentence ends as "！": captions.pages() only hard-breaks on non-soft punctuation when the page is short,
    # so a 1-glyph tail ("万。") would otherwise run into the next sentence (shared captions.py issue, see hand-over)
    for x in words:
        if x["w"] == "。": x["w"] = "！"
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    (out / "timing.json").write_text(json.dumps({"total": round(t, 3), "asr_checked": False}, ensure_ascii=False))
    print("total", round(t, 2), "s ->", out)


if __name__ == "__main__":
    main()
