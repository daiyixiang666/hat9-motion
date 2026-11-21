#!/usr/bin/env python3
"""Synthesise the house SFX kit (pure Python, no samples, MIT — safe to redistribute).

  python3 scripts/sfx.py            -> assets/sfx/<name>.wav  (44.1 kHz mono 16-bit) + assets/sfx/manifest.json

Every sound is a seeded function of time, so re-running gives identical files. The kit has families (impact, whoosh,
pop, tick, click, key, tap, paper …) with several variants each; scripts/h9/sound.py rotates them. manifest.json holds
what the scheduler needs per file, measured from the file itself: where its perceptual peak is (so the peak, not the
file start, lands on the motion) and how loud it is through a phone speaker (so levels are set by ear, not by file).
"""
import json, math, random, struct, subprocess, wave
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


# ---------------------------------------------------------------- v2 kit: more variants, phone-audible layers
def biquad(xs, kind, f, q=0.707, gain_db=0.0):
    """RBJ biquad: kind = lp | hp | bp | peak."""
    w = 2 * math.pi * f / SR; c, s_ = math.cos(w), math.sin(w); al = s_ / (2 * q)
    if kind == "lp":   b = [(1 - c) / 2, 1 - c, (1 - c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "hp": b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    elif kind == "bp": b = [al, 0.0, -al]; a = [1 + al, -2 * c, 1 - al]
    else:
        A = 10 ** (gain_db / 40)
        b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    b = [x / a[0] for x in b]; a1, a2 = a[1] / a[0], a[2] / a[0]
    x1 = x2 = y1 = y2 = 0.0; out = []
    for x in xs:
        y = b[0] * x + b[1] * x1 + b[2] * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y
        out.append(y)
    return out


def dec(sec, tau, a=0.0005):
    """an envelope: linear attack a, then exp decay with time constant tau."""
    return [(i / SR / a if i / SR < a else math.exp(-(i / SR - a) / tau)) for i in range(n(sec))]


def mul(xs, ys): return [x * y for x, y in zip(xs, ys)]


def pad(xs, sec): return [0.0] * n(sec) + xs


def sweep(sec, f_fn, harm=(1.0,)):
    out, ph = [], 0.0
    for i in range(n(sec)):
        ph += 2 * math.pi * f_fn(i / SR) / SR
        out.append(sum(h * math.sin(ph * (k + 1)) for k, h in enumerate(harm)))
    return out


def drive(xs, k): return [math.tanh(k * x) / math.tanh(k) for x in xs]


def click_tr(seed, f=3000, sec=0.006, tau=0.0015):
    """a short bright transient: the layer a phone speaker actually plays."""
    return mul(biquad(noise(sec, seed), "hp", f), dec(sec, tau, 0.0002))


def body(sec, f0, f1, k, tau):
    """a pitched drop f0 -> f1 (exp rate k) under an exp decay: the weight of an impact."""
    return mul(sweep(sec, lambda t: f1 + (f0 - f1) * math.exp(-t * k)), dec(sec, tau, 0.001))


def knock(sec, f, q, tau, seed):
    """resonant noise: wood / desk / card."""
    return mul(biquad(noise(sec, seed), "bp", f, q), dec(sec, tau, 0.0005))


def ring(sec, partials, tau):
    return mul(mix(*[scale(sweep(sec, lambda t, f=f: f), g) for f, g in partials]), dec(sec, tau, 0.0005))


def swish(sec, f0, f1, seed, peak=0.5, q=1.4, tail=0.08):
    """band-passed noise whose centre sweeps f0 -> f1 and whose level rises to `peak` (fraction of sec), then falls
    over `tail` s: asymmetric whooshes that arrive and stop, so the loudest instant is a clear point in time."""
    xs = noise(sec, seed); N = len(xs); P = int(peak * N); T = max(1, int(tail * SR))
    # time-varying bandpass done in blocks (stable, cheap): 64-sample blocks, each with its own coefficients
    res, x1, x2, y1, y2 = [], 0.0, 0.0, 0.0, 0.0
    for b0_ in range(0, N, 64):
        p = b0_ / N
        f = f0 * (f1 / f0) ** min(1.0, p / max(peak, 1e-3)) if p <= peak else f1 * (f0 / f1) ** (0.35 * (p - peak) / max(1 - peak, 1e-3))
        w = 2 * math.pi * min(f, SR * 0.45) / SR; al = math.sin(w) / (2 * q); c = math.cos(w)
        bb = [al / (1 + al), 0.0, -al / (1 + al)]; a1, a2 = -2 * c / (1 + al), (1 - al) / (1 + al)
        for x in xs[b0_:b0_ + 64]:
            y = bb[0] * x + bb[2] * x2 - a1 * y1 - a2 * y2
            x2, x1, y2, y1 = x1, x, y1, y
            res.append(y)
    env = []
    for i in range(N):
        if i <= P: env.append((i / max(P, 1)) ** 2.2)
        else: env.append(math.exp(-(i - P) / T * 3.0))
    return mul(res, env)


def v2():
    """the variants. Names stay stable: scripts/h9/sound.py groups them by prefix (hit, hit_2 …)."""
    def write(name, xs, gain=0.9):           # every v2 sound ends on a short fade, never on a cut-off sample
        k = min(len(xs), n(0.012))
        xs = xs[:len(xs) - k] + [x * (1 - (i + 1) / k) for i, x in enumerate(xs[len(xs) - k:])]
        globals()["write"](name, xs, gain)
    # impacts: body + mid knock + bright transient, so the hit survives a phone speaker
    write("hit_2", drive(mix(body(0.32, 190, 58, 22, 0.09), scale(knock(0.06, 900, 2.2, 0.018, 31), 0.9),
                             scale(click_tr(32, 2500), 0.8)), 1.6), 0.89)
    write("hit_3", mix(scale(knock(0.16, 430, 9, 0.045, 33), 1.6), scale(knock(0.1, 1150, 7, 0.025, 34), 0.8),
                       scale(body(0.16, 240, 120, 18, 0.04), 0.5), scale(click_tr(35, 3500), 0.6)), 0.89)
    write("hit_4", drive(mix(body(0.3, 150, 52, 16, 0.08), scale(mul(biquad(noise(0.22, 36), "bp", 2100, 0.9), dec(0.22, 0.05, 0.0008)), 1.1),
                             scale(click_tr(37, 3000), 0.7)), 1.4), 0.89)
    write("slam_2", drive(mix(body(0.6, 120, 40, 10, 0.16), scale(mul(biquad(noise(0.12, 38), "hp", 1500), dec(0.12, 0.03, 0.0005)), 1.0),
                              scale(ring(0.4, [(523, 0.5), (829, 0.35), (1310, 0.25), (1977, 0.15)], 0.09), 0.5),
                              scale(click_tr(39, 2800), 0.8)), 2.0), 0.89)
    write("slam_3", drive(mix(body(0.45, 230, 46, 26, 0.11), scale(mul(biquad(noise(0.3, 40), "lp", 2200), dec(0.3, 0.07, 0.003)), 0.5),
                              scale(knock(0.08, 700, 2.5, 0.02, 41), 0.9), scale(click_tr(42, 3200), 0.7)), 2.4), 0.89)
    write("boom_2", drive(mix(body(1.6, 75, 28, 3.5, 0.45), scale(mul(biquad(noise(1.0, 43), "lp", 900), dec(1.0, 0.25, 0.004)), 0.8),
                              scale(knock(0.1, 520, 2, 0.035, 44), 1.3), scale(click_tr(45, 2500), 0.6)), 1.8), 0.89)
    # whooshes for transitions: symmetric-ish, a clear peak in the middle (the cut)
    write("whoosh_2", swish(0.5, 450, 3600, 46, peak=0.6, q=1.3, tail=0.12), 0.89)
    write("whoosh_3", mix(swish(0.8, 260, 2600, 47, peak=0.55, q=0.9, tail=0.2),
                          scale(mul(sweep(0.8, lambda t: 140 + 220 * math.sin(math.pi * min(1, t / 0.8))), [math.sin(math.pi * i / n(0.8)) ** 3 for i in range(n(0.8))]), 0.25)), 0.89)
    # entrance whooshes: rise and stop, peak near the end (it lands on the arrival)
    write("whoosh_soft_2", swish(0.55, 300, 2400, 48, peak=0.78, q=0.9, tail=0.07), 0.8)
    write("whoosh_soft_3", swish(0.4, 600, 3200, 49, peak=0.82, q=1.1, tail=0.05), 0.8)
    write("whoosh_deep_2", mix(swish(0.75, 120, 1300, 50, peak=0.7, q=0.8, tail=0.14),
                               scale(mul(sweep(0.75, lambda t: 55 + 35 * t), [min(1, (i / n(0.75)) / 0.7) ** 2 * (1 if i < n(0.53) else math.exp(-(i - n(0.53)) / n(0.1))) for i in range(n(0.75))]), 0.8)), 0.89)
    # pops
    write("pop_2", mix(mul(sweep(0.09, lambda t: 260 + 520 * t / 0.09), dec(0.09, 0.03, 0.0008)), scale(click_tr(51, 2500, 0.004), 0.4)), 0.8)
    write("pop_3", mul(sweep(0.11, lambda t: 820 * math.exp(-t * 30) + 340 + 600 * max(0, t - 0.03)), dec(0.11, 0.035, 0.001)), 0.8)
    write("pop_4", mix(scale(knock(0.03, 1300, 3, 0.006, 52), 1.2), mul(sweep(0.07, lambda t: 700 - 900 * t), dec(0.07, 0.018, 0.0005))), 0.8)
    # ticks (counters, small reveals)
    write("tick_2", mix(mul(sweep(0.03, lambda t: 2600), dec(0.03, 0.006, 0.0003)), scale(click_tr(53, 4000, 0.003), 0.5)), 0.7)
    write("tick_3", ring(0.06, [(1050, 1.0), (2830, 0.45)], 0.012), 0.7)
    write("tick_4", mix(scale(knock(0.04, 3400, 10, 0.008, 54), 1.4), scale(click_tr(55, 5000, 0.002), 0.6)), 0.7)
    # clicks
    write("click_2", mix(click_tr(56, 1800, 0.012, 0.002), pad(scale(click_tr(57, 2200, 0.01, 0.0015), 0.45), 0.07)), 0.7)
    write("click_3", mix(scale(knock(0.025, 1400, 3, 0.005, 58), 1.2), mul(sweep(0.02, lambda t: 2000), dec(0.02, 0.004, 0.0003))), 0.7)
    write("click_4", mix(scale(knock(0.02, 900, 2, 0.004, 59), 1.0), pad(scale(knock(0.02, 1700, 3, 0.003, 60), 0.8), 0.012)), 0.7)
    # single keystrokes: typing is played key by key on the glyphs that appear
    for k, (fr, th) in enumerate(((2800, 380), (3300, 460), (2500, 330), (3900, 520)), 1):
        write(f"key_{k}", drive(mix(scale(click_tr(61 + k, fr, 0.004, 0.0012), 0.45), scale(knock(0.06, th, 3, 0.02, 70 + k), 1.6),
                                    scale(knock(0.05, th * 3.1, 4, 0.012, 75 + k), 0.7),
                                    pad(scale(knock(0.03, th * 2.4, 5, 0.008, 80 + k), 0.5), 0.018)), 2.0), 0.75)
    # taps: a card / chip / note settling onto the page (soft, not an impact)
    write("tap_1", mix(scale(mul(biquad(noise(0.05, 90), "lp", 1500), dec(0.05, 0.01, 0.0006)), 1.0), scale(body(0.08, 210, 150, 20, 0.02), 0.7)), 0.75)
    write("tap_2", mix(scale(knock(0.03, 2200, 1.5, 0.006, 91), 1.0), scale(body(0.07, 240, 170, 25, 0.018), 0.6)), 0.75)
    write("tap_3", mix(mul(sweep(0.04, lambda t: 1100), dec(0.04, 0.009, 0.0005)), scale(knock(0.03, 600, 2, 0.007, 92), 0.8)), 0.75)
    # material
    write("paper_2", swish(0.35, 1800, 4200, 93, peak=0.85, q=0.7, tail=0.04), 0.7)
    write("paper_3", mix(scale(knock(0.05, 2600, 0.8, 0.012, 94), 1.0), pad(scale(knock(0.06, 1900, 0.8, 0.015, 95), 0.7), 0.035),
                         scale(body(0.08, 160, 110, 20, 0.02), 0.4)), 0.7)
    write("shutter_2", mix(scale(click_tr(96, 2000, 0.008, 0.002), 1.0), scale(ring(0.09, [(2200, 0.4), (3500, 0.25)], 0.02), 0.6),
                           pad(scale(click_tr(97, 1500, 0.01, 0.003), 0.6), 0.06)), 0.7)
    write("riser_2", mix(swish(0.75, 200, 6000, 98, peak=0.97, q=0.7, tail=0.02),
                         scale(mul(sweep(0.75, lambda t: 180 * 2 ** (t / 0.75 * 1.6)), [(i / n(0.75)) ** 2.5 for i in range(n(0.75))]), 0.35)), 0.7)
    write("glitch_2", mix(*[pad([((1 if (i // (30 + 9 * k)) % 2 else -1) * 0.5 + x * 0.4) * math.exp(-i / n(0.03))
                                 for i, x in enumerate(noise(0.045, 100 + k))], 0.06 * k) for k in range(4)]), 0.6)
    write("brush_2", swish(0.45, 400, 1600, 104, peak=0.75, q=0.6, tail=0.09), 0.6)
    # second takes of the single sounds, so nothing has to repeat
    write("beep_2", mix(mul(sweep(0.09, lambda t: 1760), dec(0.09, 0.03, 0.003)), scale(mul(sweep(0.09, lambda t: 3520), dec(0.09, 0.015, 0.003)), 0.2)), 0.45)
    write("bell_2", ring(1.6, [(880, 1.0), (2212, 0.3), (3960, 0.1)], 0.45), 0.5)
    write("boing_2", mul(sweep(0.45, lambda t: 160 + 120 * math.sin(t * 44) * math.exp(-t * 6)), dec(0.45, 0.15, 0.003)), 0.7)
    write("tape_2", [x * env(i, 0, 0.008, 0.28, 1.4) * (0.6 + 0.4 * math.sin(i / SR * 190)) for i, x in enumerate(highpass(noise(0.3, 105), 1500))], 0.6)


# ---------------------------------------------------------------- manifest: measured peak + phone loudness per file
def _read(p):
    with wave.open(str(p)) as w:
        raw = w.readframes(w.getnframes()); sr = w.getframerate()
    xs = struct.unpack(f"<{len(raw) // 2}h", raw)
    return [x / 32768 for x in xs], sr


def peak_of(xs, sr):
    """(onset s, perceptual peak s): peak = max of a 10 ms RMS envelope; onset = first time it reaches 10 % of that."""
    win = max(1, int(0.010 * sr)); acc = 0.0; env = []
    sq = [x * x for x in xs]
    for i, v in enumerate(sq):
        acc += v
        if i >= win: acc -= sq[i - win]
        env.append(math.sqrt(max(acc, 0) / win))
    k = max(range(len(env)), key=env.__getitem__)
    pk_c = max(0, k - win // 2)                      # the window ends at k: its centre is the peak time
    thr = env[k] * 0.1
    on = next(i for i, e in enumerate(env) if e >= thr)
    return max(0, on - win) / sr, pk_c / sr


def phone_loudness(p, phone=True):
    """max momentary loudness (LUFS, 400 ms) through a phone-speaker high-pass (150 Hz): what is heard on a phone.
    phone=False: the plain BS.1770 figure (headphones / full-range speakers)."""
    hp = "highpass=f=150:p=2," if phone else ""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af",
                        hp + "apad=pad_dur=0.5,ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-",
                        "-f", "null", "-"], capture_output=True, text=True)
    ms = [float(x) for x in __import__("re").findall(r"lavfi\.r128\.M=(-?[\d.]+)", r.stdout)]
    return round(max(ms), 2) if ms else None


def manifest():
    out = {}
    for p in sorted(OUT.glob("*.wav")):
        xs, sr = _read(p)
        on, pk = peak_of(xs, sr)
        out[p.stem] = {"dur": round(len(xs) / sr, 3), "onset": round(on, 3), "peak": round(pk, 3),
                       "loud": phone_loudness(p), "loud_full": phone_loudness(p, False), "sample_peak_db": round(20 * math.log10(max(abs(x) for x in xs) + 1e-9), 2)}
    (OUT / "manifest.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print("manifest ->", OUT / "manifest.json", f"({len(out)} files)")


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
    v2()
    print("sfx ->", OUT)
    manifest()


if __name__ == "__main__":
    main()
