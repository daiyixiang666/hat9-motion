#!/usr/bin/env python3
"""The minimal film's music bed: a slow felt-piano piece synthesised here (numpy; no samples, MIT).

  python3 examples/minimal/make_music.py examples/minimal/assets/audio/music.wav --dur 63.8 --hits 4.7,10.8,...

72 bpm, Fmaj7 – Am7 – Dm9 – Bbmaj7. Soft piano notes (a few decaying partials, hammer softened by a low-pass) play a
sparse broken chord per bar over a quiet sustained pad; each scene change gets one high, very soft note so the cut
breathes with the thread. Same loudness target as scripts/music.py (about −16 LUFS).
"""
import argparse, sys, wave
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from music import SR, hz, lp   # noqa: E402

CHORDS = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 57, 60, 64], [46, 53, 57, 62]]   # Fmaj7 Am7 Dm9 Bbmaj7


def piano(f, dur, vel=0.5):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, (amp, dec) in enumerate(((1.0, 2.6), (0.42, 1.5), (0.2, 0.9), (0.08, 0.5))):
        out += amp * np.sin(2 * np.pi * f * (k + 1) * t * (1 + 0.0004 * k)) * np.exp(-t / dec)
    out *= np.minimum(1, t / 0.006)
    return lp(out * vel, 0.25)


def pad(freqs, dur):
    n = int(SR * dur)
    t = np.arange(n) / SR
    out = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for f in freqs)
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.5)
    return out * env * 0.035


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--dur", type=float, default=60); ap.add_argument("--hits", default="")
    a = ap.parse_args()
    n = int(SR * (a.dur + 4))
    L, R = np.zeros(n), np.zeros(n)
    rng = np.random.default_rng(7)

    def add(sig, t, pan=0.0):
        i = int(t * SR); j = min(n, i + len(sig))
        L[i:j] += sig[:j - i] * (1 - pan) * 0.5 * 2; R[i:j] += sig[:j - i] * (1 + pan) * 0.5 * 2

    bar = 60 / 72 * 4
    k = 0
    while k * bar < a.dur:
        ch = CHORDS[k % 4]
        t0 = k * bar
        add(pad([hz(m) for m in ch], bar + 1.5), t0)
        add(piano(hz(ch[0] - 12), 4.0, 0.42), t0, -0.2)
        order = [1, 2, 3, 2] if k % 2 == 0 else [3, 1, 2, 0]
        for j, idx in enumerate(order):
            add(piano(hz(ch[idx] + 12), 3.0, 0.22 + 0.05 * rng.random()), t0 + bar * (0.25 + j * 0.19), 0.25 * (j % 2 * 2 - 1))
        k += 1
    for h in [float(x) for x in a.hits.split(",") if x]:
        add(piano(hz(84), 3.0, 0.16), h - 0.02, 0.3)
    mix = np.stack([L, R], 1)[: int(SR * a.dur)]
    fade = int(SR * 3)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    rms = np.sqrt(np.mean(mix ** 2)) + 1e-9
    mix *= 10 ** (-16 / 20) / rms * 0.71
    mix = np.clip(mix, -0.98, 0.98)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    print(a.out, f"{a.dur:.1f}s")


if __name__ == "__main__":
    main()
