"""the showcase's chiptune bed: Am–F–C–G at 128 bpm (pulse arpeggio + triangle bass + noise drums), resolving to a C fanfare
on the end card. Deterministic; writes assets/audio/music.mp3. The length and the fanfare time come from video.json (the
last beat's cue, found in words.json) unless given:   python3 examples/pixel/chiptune.py [seconds] [outro_at]"""
import json, subprocess, sys
from pathlib import Path

import numpy as np

SR = 44100
BPM = 128
B = 60 / BPM                  # one beat
HERE = Path(__file__).resolve().parent


def hz(n): return 440.0 * 2 ** ((n - 69) / 12)


def tone(kind, f, dur, v, duty=0.5, decay=4.0, vib=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = np.cumsum(np.full(n, f) * (1 + vib * np.sin(2 * np.pi * 5.5 * t)) / SR) % 1.0
    if kind == "sq": w = np.where(ph < duty, 1.0, -1.0)
    elif kind == "tri": w = 4 * np.abs(ph - 0.5) - 1
    else: w = noise(n, f)
    env = np.exp(-decay * t) * v
    env = np.round(env * 15 / max(v, 1e-6)) / 15 * max(v, 1e-6)      # 4-bit volume steps
    return w * env


def noise(n, clock):
    rng = np.random.default_rng(int(clock))
    hold = max(1, int(SR / clock))
    return np.repeat(rng.choice([-1.0, 1.0], n // hold + 1), hold)[:n]


def add(buf, at, x):
    i = int(at * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += x


def timing():
    """film length (voice + tail + 1 s) and when the end card starts, from video.json + words.json."""
    video = json.loads((HERE / "video.json").read_text())
    words = json.loads((HERE / video["meta"]["words"]).read_text())
    text = ""
    starts = []
    for w in words:
        tok = str(w["w"]).strip()
        for j in range(len(tok)):
            text += tok[j]
            starts.append(w["s"] + (w["e"] - w["s"]) * j / len(tok))
    cue = str(video["beats"][-1].get("t", 0))
    outro = float(cue) if not cue.startswith("@") else starts[text.find(cue[1:])]
    length = words[-1]["e"] + float(video["meta"].get("tail", 0.6)) + 1.0
    return length, outro


def main():
    dur, outro = timing()
    if len(sys.argv) > 1: dur = float(sys.argv[1])
    if len(sys.argv) > 2: outro = float(sys.argv[2])
    buf = np.zeros(int(dur * SR))
    chords = [(57, (69, 72, 76)), (53, (69, 72, 77)), (48, (67, 72, 76)), (55, (67, 71, 74))]    # Am F C G (bass, triad)
    bar = 4 * B; k = 0
    t = 0.0
    while t < outro - 0.01:
        root, tri = chords[k % 4]
        arp = [tri[0], tri[1], tri[2], tri[0] + 12, tri[2], tri[1]] * 3
        for j in range(16):                                      # 16th-note pulse arpeggio
            at = t + j * B / 4
            if at >= outro: break
            add(buf, at, tone("sq", hz(arp[j % len(arp)] + (12 if k % 8 >= 4 and j % 4 == 3 else 0)), B / 4, 0.10, 0.125, 9))
        for j in range(8):                                       # triangle bass in eighths, octave bounce
            at = t + j * B / 2
            if at >= outro: break
            add(buf, at, tone("tri", hz(root - 12 + (12 if j % 2 else 0)), B / 2 * 0.9, 0.34, decay=3))
        for j in range(4):                                       # kick on 1 + 3, snare on 2 + 4, hats on eighths
            at = t + j * B
            if at >= outro: break
            if j % 2 == 0: add(buf, at, tone("tri", 110, 0.09, 0.5, decay=30) + tone("noise", 1800, 0.09, 0.12, decay=40))
            else: add(buf, at, tone("noise", 7000, 0.12, 0.2, decay=22))
            for q in range(2): add(buf, at + q * B / 2 + B / 4, tone("noise", 16000, 0.03, 0.06, decay=90))
        if k % 2 == 1:                                           # a tiny lead answer every other bar
            for q, n in enumerate((tri[2] + 12, tri[1] + 12, tri[0] + 12)):
                add(buf, t + 3 * B + q * B / 3, tone("sq", hz(n), B / 3, 0.07, 0.25, 6))
        t += bar; k += 1
    # end card: C major fanfare + held chord
    for q, n in enumerate((60, 64, 67, 72, 76, 79, 84)):
        add(buf, outro + q * 0.07, tone("sq", hz(n), 0.12, 0.12, 0.25, 8))
    for n in (60, 64, 67, 72):
        add(buf, outro + 0.55, tone("sq", hz(n), dur - outro - 0.55, 0.06, 0.25, 0.7, vib=0.004))
    add(buf, outro + 0.55, tone("tri", hz(36), dur - outro - 0.55, 0.32, decay=0.6))
    buf = buf / max(1e-6, np.abs(buf).max()) * 0.85
    wav = HERE / "assets" / "audio" / "music.wav"; mp3 = wav.with_suffix(".mp3")
    import wave
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((buf * 32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ac", "2", "-b:a", "192k", str(mp3)], check=True)
    wav.unlink()
    print(mp3)


if __name__ == "__main__":
    main()
