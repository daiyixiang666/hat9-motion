#!/usr/bin/env python3
"""Narration on the Windows VoxCPM2 server (no local TTS / ASR on the Mac).

  python3 examples/atlas/tts_win.py examples/atlas/script.json

script.json: {"server", "model", "ref": {"audio", "start", "end", "text"}, "sentences": [...], "takes": 2, "tempo": 1.0}
Per sentence: N seeded takes; without ASR the take whose length is closest to the expected speaking time
(≈0.2 s a glyph) wins — that catches skipped or repeated words, not misreads. Silence trimmed at both ends,
joined with 0.22 s after ，-type pauses inside a sentence (already in the take) and 0.4 s between sentences,
loudnorm −16 LUFS. words.json = per-sentence spans with characters interpolated inside each span,
punctuation tokens inserted (zero length) so captions break where the script breaks.
"""
import base64, json, subprocess, sys, urllib.request, wave
from pathlib import Path

PUN = "，。、？！：；,.?!"


def sh(*a): return subprocess.run(a, check=True, capture_output=True)


def dur(p):
    with wave.open(str(p)) as w: return w.getnframes() / w.getframerate()


def main():
    job = json.loads(Path(sys.argv[1]).read_text())
    here = Path(sys.argv[1]).parent
    out = here / "assets" / "audio"; tk = out / "takes"; tk.mkdir(parents=True, exist_ok=True)
    r = job["ref"]; ref = tk / "ref.wav"
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(r["start"]), "-to", str(r["end"]), "-i", str(here / r["audio"]), "-ac", "1", "-ar", "16000", str(ref))
    ref64 = "data:audio/wav;base64," + base64.b64encode(ref.read_bytes()).decode()
    chosen = []
    for i, s in enumerate(job["sentences"]):
        spoken = s.get("say", s["text"]) if isinstance(s, dict) else s
        text = s["text"] if isinstance(s, dict) else s
        n = sum(1 for c in text if c not in PUN and not c.isspace())
        expect = n * job.get("sec_per_glyph", 0.2)
        best = None
        for k in range(job.get("takes", 2)):
            raw, wav = tk / f"s{i}_{k}.raw.wav", tk / f"s{i}_{k}.wav"
            if not wav.exists():
                body = {"model": job["model"], "input": spoken, "response_format": "wav", "seed": 1000 + i * 17 + k,
                        "ref_audio": ref64, "ref_text": r["text"], **job.get("extra", {})}
                req = urllib.request.Request(job["server"].rstrip("/") + "/v1/audio/speech", json.dumps(body).encode(), {"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=300) as resp: raw.write_bytes(resp.read())
                af = ("silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,"
                      "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse")
                if job.get("tempo", 1) != 1: af += f",atempo={job['tempo']}"
                sh("ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", af, "-ac", "1", "-ar", "24000", str(wav)); raw.unlink()
            d = dur(wav); score = abs(d - expect) / expect
            print(f"  s{i} take{k}: {d:.2f}s (expect {expect:.2f}s, off {score:.0%})")
            if best is None or score < best[0]: best = (score, wav, d)
        chosen.append((text, best[1], best[2]))
    # join
    gap = job.get("gap", 0.4); t = 0.0; words = []; lst = tk / "concat.txt"; parts = []
    sil = tk / "gap.wav"; sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(gap), str(sil))
    for j, (text, wav, d) in enumerate(chosen):
        glyphs = [c for c in text if not c.isspace()]
        body = [c for c in glyphs if c not in PUN]
        # weight: a mid-sentence comma takes ~3 glyphs of time
        wts = [3.0 if c in PUN else 1.0 for c in glyphs]
        if glyphs and glyphs[-1] in PUN: wts[-1] = 0.0
        tot = sum(wts) or 1; acc = 0.0
        for c, w in zip(glyphs, wts):
            s0 = t + d * acc / tot; acc += w; s1 = t + d * acc / tot
            words.append({"w": c, "s": round(s0, 3), "e": round(s0 if c in PUN else s1, 3)})
        parts.append(wav); t += d
        if j + 1 < len(chosen): parts.append(sil); t += gap
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    sh("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-af", "loudnorm=I=-16:TP=-1.5:LRA=9", "-ar", "48000", "-c:a", "libmp3lame", "-b:a", "192k", str(out / "voice.mp3"))
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    print(f"voice.mp3 {t:.2f}s, {len(words)} tokens")


if __name__ == "__main__":
    main()
