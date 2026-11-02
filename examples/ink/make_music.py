#!/usr/bin/env python3
"""The ink film's music bed: a pentatonic guzheng-style piece synthesised here (numpy; no samples, MIT).

  python3 examples/ink/make_music.py examples/ink/assets/audio/music.wav --dur 31.5 --hits 3.15,7.3,10.63,15.76,18.93,21.71,24.75,27.92

D gong pentatonic. Karplus–Strong plucks with a long, bright decay stand in for the zither; a fifth drone
breathes underneath; an airy sine 'flute' holds long notes in the middle; each scene change gets a rising
glissando (刮奏) into a soft frame-drum hit. Same loudness target as scripts/music.py (≈ −16 LUFS).
"""
import argparse, sys, wave
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from music import SR, hz, lp, env, ks   # noqa: E402

SCALE = [0, 2, 4, 7, 9]                 # gong mode: do re mi sol la
ROOT = 62                               # D4


def deg(k):
    """k-th pentatonic step above ROOT (negative = below)."""
    o, i = divmod(k, 5)
    return ROOT + 12 * o + SCALE[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--bpm", type=float, default=84); ap.add_argument("--hits", default=""); ap.add_argument("--seed", type=int, default=5)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    beat = 60 / a.bpm
    N = int((a.dur + 2.0) * SR)
    L, R = np.zeros(N), np.zeros(N)

    def add(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N or i < 0: return
        s = sig[: N - i] * g
        L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))

    def zither(m, t, g, pan=0.0, dur=1.8, bright=0.75):
        sig = ks(hz(m), dur, rng, bright) * env(int(dur * SR), 0.001, dur * 0.45)
        sig = sig - lp(sig, 0.02)                                         # thin the body, keep the twang
        add(sig, t, g, pan)

    # drone: D2 + A2, slow breathing swell, very dark
    n = N; tt = np.arange(n) / SR
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * tt / 9.0 - 1.4)
    drone = (np.sin(2 * np.pi * hz(38) * tt) + 0.6 * np.sin(2 * np.pi * hz(45) * tt)
             + 0.25 * (2 * ((tt * hz(50)) % 1) - 1)) * swell * np.minimum(1, tt / 2.5)
    drone = lp(drone, 0.03) * 0.16
    L += drone; R += drone

    # zither phrase: a sparse 2-bar figure that wanders the scale, one note per beat with occasional ornaments
    bars = int(np.ceil(a.dur / (4 * beat)))
    figure = [0, 2, 4, 3, 2, 1, 2, -1, 0, 4, 5, 4, 3, 2, 3, 1]
    for b in range(bars):
        shift = [0, 0, -1, 1][b % 4]
        for q in range(8):
            t = b * 4 * beat + q * beat / 2
            if t > a.dur - 2.2: break
            if q % 2 and rng.random() < 0.55: continue                      # leave air between notes (留白)
            k = figure[(b * 8 + q) % len(figure)] + shift
            zither(deg(k), t, 0.30 if q % 4 == 0 else 0.2, pan=-0.25 + 0.5 * rng.random())
            if q == 0: zither(deg(k - 5), t, 0.18, pan=-0.4, dur=2.4, bright=0.5)   # octave below on the downbeat
            if rng.random() < 0.18: zither(deg(k + 1), t + 0.07, 0.12, pan=0.3, dur=0.9)   # grace note

    # flute: long breathy notes in the middle third
    fl = np.zeros(N)
    for t0, k, d in [(7.6, 4, 2.6), (10.6, 5, 2.4), (13.4, 3, 2.2), (18.9, 2, 2.6), (21.8, 4, 2.6), (24.8, 5, 2.8)]:
        if t0 > a.dur - 2: continue
        m = int(d * SR); t = np.arange(m) / SR
        f = hz(deg(k) + 12) * (1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.6))
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
        breath = lp(rng.uniform(-1, 1, m), 0.15) * 0.25
        e = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.8)
        i = int(t0 * SR); fl[i:i + m] += ((tone + breath) * e)[: N - i] * 0.07
    L += fl * 0.8; R += fl

    # scene changes: rising glissando into a frame-drum hit
    for h in [float(x) for x in a.hits.split(",") if x.strip()]:
        steps = 9
        for j in range(steps):
            zither(deg(-2 + j), h - 0.32 + j * 0.032, 0.09 + 0.012 * j, pan=-0.5 + j / steps, dur=1.0, bright=0.9)
        bn = int(0.8 * SR); tb = np.arange(bn) / SR
        drum = np.sin(2 * np.pi * np.cumsum(62 + 55 * np.exp(-tb / 0.04)) / SR) * np.exp(-tb / 0.28)
        skin = lp(rng.uniform(-1, 1, bn), 0.25) * np.exp(-tb / 0.03) * 0.4
        add(drum + skin, h, 0.42)

    # ending: a final low D with its fifth, then fade
    end = a.dur - 2.4
    if end > 0:
        zither(deg(-5), end, 0.35, -0.2, dur=3.0, bright=0.6); zither(deg(-2), end + 0.12, 0.22, 0.2, dur=3.0); zither(deg(0), end + 0.24, 0.2, 0.0, dur=3.0)
    fade = np.ones(N); f0 = int(max(0, a.dur - 1.6) * SR); f1 = int(a.dur * SR)
    fade[f0:f1] = np.linspace(1, 0, f1 - f0) ** 1.5; fade[f1:] = 0
    L, R = L * fade, R * fade
    # small room: two short early reflections
    for dly, g in ((0.043, 0.22), (0.071, 0.14)):
        d = int(dly * SR); L[d:] += R[:-d] * g; R[d:] += L[:-d] * g
    L, R = L[: int(a.dur * SR)], R[: int(a.dur * SR)]
    st = np.stack([L, R], 1)
    rms = np.sqrt(np.mean(st[: int(min(a.dur, 20) * SR)] ** 2)) + 1e-9
    st *= 10 ** (-19 / 20) / rms
    st = np.tanh(st * 1.1) / 1.1
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(a.out, f"{a.dur:.1f}s pentatonic, {a.bpm:.0f} bpm")


if __name__ == "__main__":
    main()
