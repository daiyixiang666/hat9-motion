#!/usr/bin/env python3
"""Your recording + its script → words.json (one entry per character, punctuation as zero-length tokens).

  python3 scripts/align.py voice.wav script.txt --out assets/audio/words.json
  python3 scripts/align.py voice.wav "一杯四块钱的柠檬水，……" --out words.json --backend silence
  python3 scripts/align.py voice.wav script.txt --transcript asr.json --out words.json   # bring your own word timestamps

Backends (--backend auto tries them in this order):
  transcript      a word-timestamp file you already have (any of [{w|word|text, s|start, e|end}], or
                  {"segments": [{"words": [...]}]} from Whisper-style tools): the script is matched to it glyph by glyph
  faster-whisper  pip install faster-whisper — transcribes with word timestamps, then the same matching
  whisperx        pip install whisperx — forced alignment, then the same matching
  silence         no model: ffmpeg finds the pauses; the script's clauses are spread over the voiced stretches by
                  length. Good enough for captions and most "@cues"; a real aligner is better for single words.
The script is the source of truth for the text (ASR spelling mistakes never reach the captions); the recording only
supplies the timing. Unmatched glyphs are interpolated between their matched neighbours.
"""
import argparse, difflib, json, re, subprocess, sys
from pathlib import Path

PUN = set("，。、；：！？,.;:!?…—“”‘’（）《》「」 ")
STOP = set("。！？!?")


def script_text(arg):
    p = Path(arg)
    return p.read_text(encoding="utf-8").strip() if p.exists() and p.is_file() else arg.strip()


def load_transcript(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, dict): d = [w for seg in d.get("segments", []) for w in seg.get("words", [])] or d.get("words", [])
    out = []
    for w in d:
        tok = str(w.get("w", w.get("word", w.get("text", "")))).strip()
        s, e = w.get("s", w.get("start")), w.get("e", w.get("end"))
        if tok and s is not None and e is not None: out.append({"w": tok, "s": float(s), "e": float(e)})
    return out


def asr_faster_whisper(audio):
    from faster_whisper import WhisperModel          # noqa: optional dependency
    m = WhisperModel("small", device="auto", compute_type="auto")
    segs, _ = m.transcribe(str(audio), language="zh", vad_filter=True, condition_on_previous_text=False, word_timestamps=True)
    return [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in (s.words or []) if w.word.strip()]


def asr_whisperx(audio):
    import whisperx                                   # noqa: optional dependency
    dev = "cpu"
    model = whisperx.load_model("small", dev, compute_type="int8")
    au = whisperx.load_audio(str(audio))
    r = model.transcribe(au, language="zh")
    am, meta = whisperx.load_align_model(language_code="zh", device=dev)
    r = whisperx.align(r["segments"], am, meta, au, dev)
    return [{"w": w["word"].strip(), "s": w["start"], "e": w["end"]} for s in r["segments"] for w in s.get("words", []) if "start" in w]


def match(script, words):
    """script glyphs ← transcript glyph times (difflib on punctuation-free strings), the rest interpolated."""
    tc = []
    for w in words:
        g = [c for c in w["w"] if c not in PUN]
        for k, c in enumerate(g):
            a = w["s"] + (w["e"] - w["s"]) * k / len(g); b = w["s"] + (w["e"] - w["s"]) * (k + 1) / len(g)
            tc.append((c, a, b))
    sc = [c for c in script if c not in PUN]
    times = [None] * len(sc)
    sm = difflib.SequenceMatcher(a=sc, b=[c for c, _, _ in tc], autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): times[blk.a + k] = tc[blk.b + k][1:]
    return fill(times, tc[0][1] if tc else 0.0, tc[-1][2] if tc else 1.0), sc


def fill(times, t0, t1):
    n = len(times)
    known = [i for i, x in enumerate(times) if x is not None]
    if not known: return [(t0 + (t1 - t0) * i / n, t0 + (t1 - t0) * (i + 1) / n) for i in range(n)]
    out = list(times)
    for i in range(n):
        if out[i] is not None: continue
        L = max([k for k in known if k < i], default=None); R = min([k for k in known if k > i], default=None)
        a = times[L][1] if L is not None else t0
        b = times[R][0] if R is not None else t1
        lo = L if L is not None else -1; hi = R if R is not None else n
        span = (b - a) / max(1, hi - lo - 1)
        out[i] = (a + span * (i - lo - 1), a + span * (i - lo))
    return out


def voiced(audio, noise="-34dB", gap=0.22):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(audio), "-af", f"silencedetect=noise={noise}:d={gap}", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    sil = []
    for line in r.stderr.splitlines():
        a = re.search(r"silence_start: ([\d.]+)", line); b = re.search(r"silence_end: ([\d.]+)", line)
        if a: sil.append([float(a.group(1)), None])
        if b and sil: sil[-1][1] = float(b.group(1))
    segs, t = [], 0.0
    for a, b in sil:
        if a - t > 0.08: segs.append([t, a])
        t = b if b is not None else dur
    if dur - t > 0.08: segs.append([t, dur])
    return segs


def silence_align(audio, script):
    """no model: clause boundaries snap to the detected pauses nearest to where an even speaking rate puts them;
    glyphs spread over the voiced time inside each clause."""
    segs = voiced(audio, noise="-32dB", gap=0.15)
    if not segs: segs = [[0.0, 1.0]]
    clauses = [c for c in re.split(r"(?<=[，。、；：！？,.;:!?])", script) if any(ch not in PUN for ch in c)]
    lens = [sum(1 for ch in c if ch not in PUN) for c in clauses]
    N = max(1, sum(lens))
    tv = sum(b - a for a, b in segs)
    def real(v):                       # voiced-time position -> clock time
        for a0, b0 in segs:
            if v <= b0 - a0: return a0 + v
            v -= b0 - a0
        return segs[-1][1]
    gaps = [(segs[k][1] + segs[k + 1][0]) / 2 for k in range(len(segs) - 1)]
    bounds, cum, used = [segs[0][0]], 0, -1
    for L in lens[:-1]:
        cum += L
        r0 = real(tv * cum / N)
        cand = [(abs(g - r0), k) for k, g in enumerate(gaps) if k > used and abs(g - r0) < 0.9]
        if cand:
            _, k = min(cand); used = k; bounds.append(gaps[k])
        else:
            bounds.append(max(r0, bounds[-1] + 0.05))
    bounds.append(segs[-1][1])
    times = []
    for (c0, c1), L in zip(zip(bounds, bounds[1:]), lens):
        vs = [(max(a0, c0), min(b0, c1)) for a0, b0 in segs if min(b0, c1) - max(a0, c0) > 0.02] or [(c0, c1)]
        tot = sum(y - x for x, y in vs); step = tot / max(1, L)
        k, acc = 0, 0.0
        for j in range(L):
            v = j * step
            while k < len(vs) - 1 and v >= acc + (vs[k][1] - vs[k][0]): acc += vs[k][1] - vs[k][0]; k += 1
            s0 = vs[k][0] + (v - acc)
            times.append((s0, s0 + step))
    sc = [c for c in script if c not in PUN]
    return times[:len(sc)], sc


def to_words(script, sc_times):
    """per-glyph entries in script order, punctuation as zero-length tokens."""
    out, k, last = [], 0, 0.0
    for ch in script:
        if ch in PUN:
            if ch.strip(): out.append({"w": ch, "s": last, "e": last})
            continue
        s, e = sc_times[k]; k += 1
        out.append({"w": ch, "s": round(s, 3), "e": round(e, 3)}); last = round(e, 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio"); ap.add_argument("script"); ap.add_argument("--out", required=True)
    ap.add_argument("--backend", default="auto", choices=["auto", "transcript", "faster-whisper", "whisperx", "silence"])
    ap.add_argument("--transcript")
    a = ap.parse_args()
    script = script_text(a.script)
    order = [a.backend] if a.backend != "auto" else (["transcript"] if a.transcript else []) + ["faster-whisper", "whisperx", "silence"]
    used, times = None, None
    for be in order:
        try:
            if be == "transcript":
                if not a.transcript: raise SystemExit("--transcript is required for this backend")
                times, sc = match(script, load_transcript(a.transcript))
            elif be == "faster-whisper":
                times, sc = match(script, asr_faster_whisper(a.audio))
            elif be == "whisperx":
                times, sc = match(script, asr_whisperx(a.audio))
            else:
                times, sc = silence_align(a.audio, script)
            used = be; break
        except ImportError:
            print(f"  · {be} not installed — pip install {be}", file=sys.stderr)
    words = to_words(script, times)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    print(f"{a.out}  {len(words)} tokens  backend={used}  {words[-1]['e'] if words else 0:.2f}s")


if __name__ == "__main__":
    main()
