#!/usr/bin/env python3
"""Placeholder narration + word timestamps with edge-tts (free Microsoft neural voices).

  python3 scripts/voice.py "文案……" out_dir [--voice zh-CN-YunxiNeural] [--rate +0%]
      -> out_dir/voice.mp3 (−16 LUFS) and out_dir/words.json  [{w,s,e}]

For real episodes use your own recording + any aligner that writes the same words.json.
"""
import argparse, asyncio, json, subprocess
from pathlib import Path


async def synth(text, voice, rate, mp3):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary")
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"], "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--voice", default="zh-CN-YunxiNeural"); ap.add_argument("--rate", default="+0%")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    raw = out / "voice_raw.mp3"
    words = asyncio.run(synth(a.text, a.voice, a.rate, raw))
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", str(out / "voice.mp3")])
    raw.unlink()
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(len(words), "words,", words[-1]["e"] if words else 0, "s ->", out)


if __name__ == "__main__":
    main()
