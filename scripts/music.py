#!/usr/bin/env python3
"""A quiet, royalty-free music bed for 口播, synthesised here (numpy; no samples, MIT — safe to publish).

  python3 scripts/music.py out.wav --dur 31 [--bpm 100] [--mood brief|warm|tense] [--hits 2.8,6.9,9.3] [--seed 7]

Kick + soft hats + sub bass + Karplus–Strong plucks (with a dotted-8th delay) + a ducked pad, over a
four-chord loop. `--hits` adds a low boom + cymbal swell on those seconds (scene changes); the last
bar resolves and fades. Loudness is normalised to about −16 LUFS (RMS approximation), so a
meta.music_volume of ~0.2 sits the bed 12–14 dB under a −16 LUFS voice.
"""
import argparse, wave
import numpy as np

SR = 44100
MOODS = {   # chord roots (MIDI) + quality; one chord per bar
    "brief": [(57, "m"), (53, "M"), (48, "M"), (55, "M")],      # Am F C G
    "warm":  [(48, "M7"), (57, "m7"), (53, "M7"), (55, "M")],   # Cmaj7 Am7 Fmaj7 G
    "tense": [(52, "m"), (48, "M"), (55, "M"), (50, "m")],      # Em C G Dm
}
SHAPE = {"m": [0, 3, 7, 12], "M": [0, 4, 7, 12], "m7": [0, 3, 7, 10], "M7": [0, 4, 7, 11]}


def hz(m): return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, a):
    """one-pole low-pass, a in (0,1): smaller = darker."""
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def env(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)


def ks(f, dur, rng, bright=0.5):
    """Karplus–Strong plucked string."""
    n = int(dur * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * (0.5 + 0.5 * bright)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = 0.996 * 0.5 * (buf[j] + buf[(j + 1) % p])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out"); ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--bpm", type=float, default=100); ap.add_argument("--mood", default="brief", choices=MOODS)
    ap.add_argument("--hits", default=""); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    beat = 60 / a.bpm; bar = 4 * beat
    N = int((a.dur + 1.5) * SR)
    L, R = np.zeros(N), np.zeros(N)

    def add(sig, t, g=1.0, pan=0.0):
        i = int(t * SR)
        if i >= N: return
        s = sig[: N - i] * g
        L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))

    prog = MOODS[a.mood]
    nbars = int(np.ceil(a.dur / bar))
    duck = np.ones(N)
    # kick + sidechain curve
    kn = int(0.4 * SR); tk = np.arange(kn) / SR
    kick = np.sin(2 * np.pi * np.cumsum(45 + 75 * np.exp(-tk / 0.03)) / SR) * np.exp(-tk / 0.16)
    for b in range(nbars):
        for q in range(4):
            t = b * bar + q * beat
            add(kick, t, 0.42)
            i = int(t * SR); m = min(N - i, int(0.35 * SR))
            if m > 0: duck[i:i + m] = np.minimum(duck[i:i + m], 0.45 + 0.55 * (np.arange(m) / m) ** 0.6)
            hat = lp(rng.uniform(-1, 1, int(0.05 * SR)), 0.9); hat = (hat - lp(hat, 0.2)) * env(len(hat), 0.001, 0.012)
            add(hat, t + beat / 2, 0.16, 0.3)
    # chords: pad (ducked), sub bass, plucked arpeggio with delay
    pad_l, pad_r = np.zeros(N), np.zeros(N)
    pl = np.zeros(N)
    for b in range(nbars):
        root, q = prog[b % len(prog)]
        notes = [root + s for s in SHAPE[q]]
        t0 = b * bar; n = int(bar * SR)
        tt = np.arange(n) / SR
        e = np.minimum(1, tt / 0.6) * np.minimum(1, (bar - tt) / 0.3)
        i = int(t0 * SR); m = min(n, N - i)
        for k, nn in enumerate(notes[:3]):
            f = hz(nn + 12)
            for det, side in ((-0.12, 0), (0.12, 1)):
                w = 2 * ((tt * f * 2 ** (det / 12)) % 1) - 1
                (pad_l if side == 0 else pad_r)[i:i + m] += (w * e)[:m] * 0.05
        bass = np.sin(2 * np.pi * hz(root - 12) * tt) * e
        L[i:i + m] += bass[:m] * 0.11; R[i:i + m] += bass[:m] * 0.11
        arp = [notes[0], notes[2], notes[3], notes[1]]
        for s in range(16):
            if s % 4 == 3 and rng.random() < 0.5: continue
            f = hz(arp[s % 4] + 12)
            j = int((t0 + s * beat / 4) * SR)
            sig = ks(f, 0.5, rng, bright=0.35) * env(int(0.5 * SR), 0.002, 0.18)
            m2 = min(len(sig), N - j)
            if m2 > 0: pl[j:j + m2] += sig[:m2] * (0.22 if s % 4 == 0 else 0.15)
    pad_l, pad_r = lp(pad_l, 0.08) * duck, lp(pad_r, 0.08) * duck
    d = int(0.75 * beat * SR)                       # dotted-8th delay on the plucks
    dl = np.zeros(N); dl[d:] = pl[:-d] * 0.35; dl2 = np.zeros(N); dl2[2 * d:] = pl[:-2 * d] * 0.15
    L += pad_l + pl + dl * 0.6 + dl2; R += pad_r + pl * 0.9 + dl + dl2 * 0.6
    # scene hits: low boom + reversed-noise swell into the hit
    for h in [float(x) for x in a.hits.split(",") if x.strip()]:
        bn = int(0.9 * SR); tb = np.arange(bn) / SR
        boom = np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-tb / 0.05)) / SR) * np.exp(-tb / 0.35)
        add(boom, h, 0.5)
        sw = lp(rng.uniform(-1, 1, int(0.45 * SR)), 0.35) * np.linspace(0, 1, int(0.45 * SR)) ** 2
        add(sw, max(0, h - 0.45), 0.12, 0.0)
    # end: fade over the last bar
    fade = np.ones(N); f0 = int(max(0, a.dur - 2.0) * SR); f1 = int(a.dur * SR)
    fade[f0:f1] = np.linspace(1, 0, f1 - f0) ** 1.5; fade[f1:] = 0
    L, R = L * fade, R * fade
    L, R = L[: int(a.dur * SR)], R[: int(a.dur * SR)]
    st = np.stack([L, R], 1)
    rms = np.sqrt(np.mean(st[: int(min(a.dur, 20) * SR)] ** 2)) + 1e-9
    st *= 10 ** (-19 / 20) / rms                    # ≈ −16 LUFS for this kind of material
    st = np.tanh(st * 1.1) / 1.1                     # soft safety clip
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(a.out, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    print(a.out, f"{a.dur:.1f}s", a.mood, f"{a.bpm:.0f} bpm")


if __name__ == "__main__":
    main()
