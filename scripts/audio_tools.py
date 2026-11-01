#!/usr/bin/env python3
"""Voice clean-up before a build: denoise a recording, splice takes, cut flubs, keep words.json in step.

  python3 scripts/audio_tools.py denoise raw.wav voice.wav            # DeepFilterNet if installed, else ffmpeg
  python3 scripts/audio_tools.py splice t1.wav t2.wav t3.wav --out voice.wav [--gap 0.25] [--words w1.json w2.json w3.json]
  python3 scripts/audio_tools.py cut voice.wav clean.wav --remove 3.2-4.1,9.8-10.4 [--words words.json]
  python3 scripts/audio_tools.py flubs words.json                     # suggests --remove ranges (restarts, long pauses)

Every command ends with loudness at -16 LUFS (the house level, same as voice.py), 48 kHz.
--words writes <out>.words.json next to the audio with times shifted to match, so captions and "@词" cues stay right.
Nothing here listens to speech: flubs works from an existing words.json (made on the speech machine), never runs ASR.

DeepFilterNet (MIT/Apache, https://github.com/Rikorose/DeepFilterNet) is optional:  pip install deepfilternet
Without it denoise falls back to ffmpeg highpass + afftdn, which removes steady hiss/hum but not music or voices.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
LOUD = "loudnorm=I=-16:TP=-1.5:LRA=9"
DF_HINT = ("DeepFilterNet not found, using ffmpeg afftdn (steady noise only).\n"
           "  For real denoising:  pip install deepfilternet   (then `deepFilter` is on PATH)")


def ff(*args):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", *map(str, args)])


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode().strip())


def finish(src, out):
    """loudness + 48 kHz mono into out (wav / mp3 / m4a by extension)."""
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    ff("-i", src, "-af", LOUD, "-ar", 48000, "-ac", 1, out)


def load_words(p):
    data = json.loads(Path(p).read_text())
    words = []
    for x in data:
        if "words" in x: words += x["words"]
        else: words.append(x)
    return words


def write_words(out, words):
    p = Path(str(out).rsplit(".", 1)[0] + ".words.json")
    p.write_text(json.dumps(words, ensure_ascii=False))
    print(f"words -> {p}")


def ranges(s):
    """"3.2-4.1,9.8-10.4" -> [(3.2, 4.1), (9.8, 10.4)]"""
    out = []
    for part in str(s).split(","):
        part = part.strip()
        if not part: continue
        a, b = part.split("-")
        a = float(a)
        b = float(b)
        if b <= a: sys.exit(f"bad range {part}: end must be after start")
        out.append((a, b))
    out.sort()
    return out


# ---------------------------------------------------------------- denoise (O04)
def deepfilter(src, out):
    """True if DeepFilterNet did the job (CLI first, then the python package)."""
    exe = shutil.which("deepFilter")
    if exe:
        with tempfile.TemporaryDirectory() as tmp:
            wav = Path(tmp) / "in.wav"
            ff("-i", src, "-ar", 48000, "-ac", 1, wav)          # DeepFilterNet works at 48 kHz
            subprocess.check_call([exe, str(wav), "-o", tmp])
            got = sorted(p for p in Path(tmp).glob("*.wav") if p.name != "in.wav")
            if not got: return False
            finish(got[0], out)
        return True
    try:
        from df.enhance import enhance, init_df, load_audio, save_audio
    except ImportError:
        return False
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "in.wav"
        clean = Path(tmp) / "clean.wav"
        ff("-i", src, "-ar", 48000, "-ac", 1, wav)
        model, state, _ = init_df()
        audio, _ = load_audio(str(wav), sr=state.sr())
        save_audio(str(clean), enhance(model, state, audio), state.sr())
        finish(clean, out)
    return True


def denoise(a):
    if not a.ffmpeg_only and deepfilter(a.src, a.out):
        print(f"denoised (DeepFilterNet) -> {a.out}")
        return
    if a.require_df: sys.exit(DF_HINT.split("\n")[0].replace(", using ffmpeg afftdn (steady noise only)", ""))
    if not a.ffmpeg_only: print(DF_HINT, file=sys.stderr)
    nr = {"light": 8, "medium": 14, "strong": 22}[a.strength]
    chain = f"highpass=f=80,afftdn=nr={nr}:nf=-40:tn=1,{LOUD}"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    ff("-i", a.src, "-af", chain, "-ar", 48000, "-ac", 1, a.out)
    print(f"denoised (ffmpeg afftdn nr={nr}) -> {a.out}")


# ---------------------------------------------------------------- splice takes (O08)
def splice(a):
    takes = a.takes
    if a.words and len(a.words) != len(takes): sys.exit("--words needs one words.json per take, in the same order")
    lens = [dur(t) for t in takes]
    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, t in enumerate(takes):                         # same format, a 15 ms fade at both ends so joins don't click
            p = Path(tmp) / f"t{i}.wav"
            fo = max(0.0, lens[i] - 0.015)
            ff("-i", t, "-af", f"afade=t=in:d=0.015,afade=t=out:st={fo:.3f}:d=0.015", "-ar", 48000, "-ac", 1, p)
            parts.append(p)
        gap = Path(tmp) / "gap.wav"
        ff("-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{a.gap:.3f}", gap)
        lst = Path(tmp) / "list.txt"
        seq = []
        for i, p in enumerate(parts):
            if i and a.gap > 0: seq.append(gap)
            seq.append(p)
        lst.write_text("".join(f"file '{p}'\n" for p in seq))
        joined = Path(tmp) / "joined.wav"
        ff("-f", "concat", "-safe", 0, "-i", lst, "-c", "copy", joined)
        finish(joined, a.out)
    print(f"spliced {len(takes)} takes ({sum(lens) + a.gap * (len(takes) - 1):.2f}s) -> {a.out}")
    if a.words:
        words = []
        off = 0.0
        for i, p in enumerate(a.words):
            for w in load_words(p):
                words.append({**w, "s": round(float(w["s"]) + off, 3), "e": round(float(w["e"]) + off, 3)})
            off += lens[i] + a.gap
        write_words(a.out, words)


# ---------------------------------------------------------------- cut flubs (O08)
def cut(a):
    cuts = ranges(a.remove)
    total = dur(a.src)
    keep = []
    pos = 0.0
    for c0, c1 in cuts:
        if c0 > pos: keep.append((pos, c0))
        pos = max(pos, c1)
    if pos < total: keep.append((pos, total))
    if not keep: sys.exit("nothing left after the cuts")
    f = a.fade
    chains = []
    for i, (k0, k1) in enumerate(keep):                       # each kept piece gets short fades so the joins don't click
        fo = max(0.0, k1 - k0 - f)
        chains.append(f"[0:a]atrim={k0:.3f}:{k1:.3f},asetpts=PTS-STARTPTS,"
                      f"afade=t=in:d={f:.3f},afade=t=out:st={fo:.3f}:d={f:.3f}[k{i}]")
    graph = ";".join(chains) + ";" + "".join(f"[k{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1,{LOUD}[o]"
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    ff("-i", a.src, "-filter_complex", graph, "-map", "[o]", "-ar", 48000, "-ac", 1, a.out)
    gone = sum(c1 - c0 for c0, c1 in cuts)
    print(f"cut {len(cuts)} range(s), {gone:.2f}s removed ({total:.2f}s -> {total - gone:.2f}s) -> {a.out}")
    if a.words:
        import importlib.util                                   # fx helpers load by path (h9/fx is not a package)
        spec = importlib.util.spec_from_file_location("_av", Path(__file__).resolve().parent / "h9" / "fx" / "_av.py")
        av = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(av)
        write_words(a.out, av.retime_words(load_words(a.words), cuts))


# ---------------------------------------------------------------- find flubs in a words.json (O08)
PUNCT = set("，。！？、；：,.!?;:…—\"'“”‘’（）() ")


def flubs(a):
    """restarts (the same 2–8 characters said twice inside one clause → keep the second take) and long pauses.
    A repeat across a comma is rhetoric (看懂谁在赚钱，比看懂谁在卖货…), and 一件一件 with no pause is reduplication."""
    chars = []
    clause = []                                                  # punctuation in words.json marks where clauses end
    k_clause = 0
    for w in load_words(a.words):
        tok = str(w["w"]).strip()
        k = max(len(tok), 1)
        s, e = float(w["s"]), float(w["e"])
        for j, ch in enumerate(tok):
            if ch in PUNCT:
                k_clause += 1
                continue
            chars.append((ch, s + (e - s) * j / k, s + (e - s) * (j + 1) / k))
            clause.append(k_clause)
    text = "".join(c[0] for c in chars)
    out = []
    i = 0
    while i < len(chars):
        hit = None
        for n in range(min(8, (len(chars) - i) // 2), 1, -1):     # longest repeat first
            for gap in range(0, 4):                               # a few stray characters between the two tries
                j = i + n + gap
                if j + n > len(chars): break
                if text[i:i + n] != text[j:j + n] or chars[j][1] - chars[i][1] > a.window: continue
                if clause[i] != clause[j]: continue
                pause = chars[j][1] - chars[j - 1][2]
                if n < 3 and pause < 0.2: continue
                hit = (n, j)
                break
            if hit: break
        if hit:
            n, j = hit
            out.append({"kind": "restart", "a": round(chars[i][1], 3), "b": round(chars[j][1], 3),
                        "said": text[i:j + n], "keep": text[j:j + n]})
            i = j
            continue
        i += 1
    for (c, s, e), (c2, s2, e2) in zip(chars, chars[1:]):
        if s2 - e > a.pause:
            out.append({"kind": "pause", "a": round(e + 0.25, 3), "b": round(s2 - 0.25, 3), "said": f"{c}…{c2}",
                        "keep": f"{s2 - e:.2f}s pause → 0.5s"})
    out.sort(key=lambda x: x["a"])
    for x in out: print(f'{x["kind"]:7s} {x["a"]:7.2f}-{x["b"]:<7.2f} {x["said"]}  →  {x["keep"]}')
    if out:
        print("\n--remove " + ",".join(f'{x["a"]:.2f}-{x["b"]:.2f}' for x in out))
        print("(listen before cutting: a repeat can be on purpose)")
    else:
        print("no restarts or long pauses found")
    if a.json: Path(a.json).write_text(json.dumps(out, ensure_ascii=False, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("denoise", help="remove background noise (DeepFilterNet, else ffmpeg)")
    p.add_argument("src"); p.add_argument("out")
    p.add_argument("--strength", choices=["light", "medium", "strong"], default="medium", help="ffmpeg fallback only")
    p.add_argument("--ffmpeg-only", action="store_true", help="skip DeepFilterNet even if installed")
    p.add_argument("--require-df", action="store_true", help="fail instead of falling back")
    p.set_defaults(fn=denoise)
    p = sub.add_parser("splice", help="join takes in order with a short gap")
    p.add_argument("takes", nargs="+"); p.add_argument("--out", required=True)
    p.add_argument("--gap", type=float, default=0.25, help="silence between takes, seconds")
    p.add_argument("--words", nargs="+", help="one words.json per take -> <out>.words.json")
    p.set_defaults(fn=splice)
    p = sub.add_parser("cut", help="remove time ranges (flubs, restarts, long pauses)")
    p.add_argument("src"); p.add_argument("out")
    p.add_argument("--remove", required=True, help='"a-b,c-d" in seconds')
    p.add_argument("--fade", type=float, default=0.02, help="fade at each join, seconds")
    p.add_argument("--words", help="words.json of src -> <out>.words.json retimed")
    p.set_defaults(fn=cut)
    p = sub.add_parser("flubs", help="suggest cut ranges from a words.json")
    p.add_argument("words")
    p.add_argument("--window", type=float, default=4.0, help="max seconds between a phrase and its retry")
    p.add_argument("--pause", type=float, default=1.2, help="report silences longer than this")
    p.add_argument("--json", help="also write the suggestions here")
    p.set_defaults(fn=flubs)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
