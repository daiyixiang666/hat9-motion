#!/usr/bin/env python3
"""Synthesise the house SFX kit (pure Python, no samples, MIT — safe to redistribute).

  python3 scripts/sfx.py            -> assets/sfx/<name>.wav  (44.1 kHz mono 16-bit)

Every sound is a seeded function of time, so re-running gives identical files.
"""
import math, random, struct, wave
from pathlib import Path

SR = 44100
OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"


def write(name, xs, gain=0.9):
    peak = max(1e-9, max(abs(x) for x in xs))
    k = gain / peak
    OUT.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT / f"{name}.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, x * k)) * 32767)) for x in xs))


def n(sec): return int(sec * SR)


def noise(sec, seed):
    r = random.Random(seed)
    return [r.uniform(-1, 1) for _ in range(n(sec))]


def env(i, total, a, d, curve=2.0):
    """attack a seconds, then decay to the end with a power curve."""
    t = i / SR
    if t < a: return t / a
    return max(0.0, 1 - (t - a) / max(d, 1e-6)) ** curve


def lowpass(xs, fc_fn):
    """one-pole lowpass with a time-varying cutoff (Hz)."""
    y, out = 0.0, []
    for i, x in enumerate(xs):
        a = 1 - math.exp(-2 * math.pi * fc_fn(i / SR) / SR)
        y += a * (x - y); out.append(y)
    return out


def highpass(xs, fc):
    lp = lowpass(xs, lambda t: fc)
    return [x - l for x, l in zip(xs, lp)]


def bandsweep(sec, f0, f1, seed, q=2):
    """noise through a lowpass whose cutoff sweeps f0->f1->f0 (classic whoosh)."""
    xs = noise(sec, seed)
    def fc(t):
        p = t / sec
        return f0 + (f1 - f0) * math.sin(math.pi * p) ** q
    ys = highpass(lowpass(xs, fc), 120)
    return [y * math.sin(math.pi * (i / len(ys))) ** 1.5 for i, y in enumerate(ys)]


def tone(sec, f_fn, a=0.002, d=None, curve=3.0, harm=(1.0,)):
    d = d or sec
    out, ph = [], 0.0
    for i in range(n(sec)):
        f = f_fn(i / SR); ph += 2 * math.pi * f / SR
        s = sum(h * math.sin(ph * (k + 1)) for k, h in enumerate(harm))
        out.append(s * env(i, n(sec), a, d, curve))
    return out


def mix(*tracks):
    L = max(len(t) for t in tracks)
    return [sum(t[i] for t in tracks if i < len(t)) for i in range(L)]


def scale(xs, g): return [x * g for x in xs]


def main():
    # transitions
    write("whoosh", bandsweep(0.7, 300, 5200, 1))
    write("whoosh_soft", scale(bandsweep(1.1, 200, 2200, 2, q=1), 0.7), 0.6)
    write("whoosh_deep", mix(bandsweep(0.9, 80, 1400, 3), tone(0.9, lambda t: 70 - 30 * t, a=0.2, d=0.7, curve=2)))
    # impacts
    write("hit", mix(tone(0.45, lambda t: 140 * math.exp(-t * 9) + 45, d=0.45, curve=4),
                     scale([x * env(i, 0, 0.001, 0.08, 3) for i, x in enumerate(noise(0.12, 4))], 0.6)))
    write("boom", tone(1.4, lambda t: 60 * math.exp(-t * 2) + 32, a=0.005, d=1.4, curve=2.5, harm=(1, 0.3)))
    write("slam", mix(tone(0.3, lambda t: 220 * math.exp(-t * 14) + 60, d=0.3, curve=4),
                      scale([x * env(i, 0, 0.0005, 0.05, 2) for i, x in enumerate(highpass(noise(0.08, 5), 2000))], 0.9)))
    # small UI sounds
    write("pop", tone(0.12, lambda t: 380 + 900 * t / 0.12, a=0.001, d=0.12, curve=3), 0.7)
    write("click", [x * env(i, 0, 0.0002, 0.012, 2) for i, x in enumerate(highpass(noise(0.03, 6), 1500))], 0.6)
    write("tick", tone(0.05, lambda t: 1800, a=0.0005, d=0.05, curve=6), 0.5)
    write("type", mix(*[[0.0] * n(0.06 * k) + [x * env(i, 0, 0.0003, 0.02, 3) for i, x in enumerate(highpass(noise(0.03, 10 + k), 2500))] for k in range(6)]), 0.55)
    write("beep", tone(0.16, lambda t: 1320, a=0.004, d=0.16, curve=1.5, harm=(1, 0.2)), 0.45)
    # material sounds
    write("paper", [x * (0.4 + 0.6 * abs(math.sin(i / SR * 37))) * math.sin(math.pi * i / n(0.5)) for i, x in enumerate(highpass(lowpass(noise(0.5, 7), lambda t: 4000), 600))], 0.6)
    write("tape", [x * env(i, 0, 0.01, 0.35, 1.2) * (0.6 + 0.4 * math.sin(i / SR * 260)) for i, x in enumerate(highpass(noise(0.36, 8), 1800))], 0.6)
    write("brush", scale(bandsweep(0.9, 150, 1200, 9, q=1), 0.8), 0.5)
    write("bell", tone(2.2, lambda t: 660, a=0.002, d=2.2, curve=2.2, harm=(1, 0.0, 0.35, 0.0, 0.12)), 0.5)
    write("boing", tone(0.5, lambda t: 220 + 160 * math.sin(t * 38) * math.exp(-t * 5), a=0.003, d=0.5, curve=1.6), 0.7)
    write("shutter", mix(*[[0.0] * n(0.07 * k) + [x * env(i, 0, 0.0002, 0.025, 2) for i, x in enumerate(lowpass(noise(0.04, 20 + k), lambda t: 3000))] for k in range(3)]), 0.6)
    write("glitch", [(1 if (i // 220) % 2 else -1) * 0.4 * env(i, 0, 0.001, 0.25, 1) + x * 0.5 * env(i, 0, 0.001, 0.25, 1) for i, x in enumerate(noise(0.25, 11))], 0.5)
    write("riser", [x * (i / n(1.2)) ** 2 for i, x in enumerate(lowpass(noise(1.2, 12), lambda t: 300 + 5000 * (t / 1.2) ** 2))], 0.6)
    print("sfx ->", OUT)


if __name__ == "__main__":
    main()
