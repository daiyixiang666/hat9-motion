"""voicesync — the picture is timed by the real voice, never by a guess.

When a film has a voice file (meta.voice), every "@词" cue, every auto-timed list item, the captions and the beat
cuts come from word times measured on THAT recording:

  resolve(vpath)   -> the words file every tool must read (build, review, longform). With a voice it is
                      assets/audio/<voice>.sync-words.json, made and cached here:
                        1. meta.words was measured on THIS recording by scripts/align.py (its <words>.align.json
                           names the recording's hash and a real aligner) -> used as is
                        2. otherwise (TTS-supplied or text-estimated times, another take, no words) -> measured now on
                           the recording with faster-whisper (medium, small as fallback) / whisperx, the words' own
                           text being the script
                        3. no recognizer installed: the given words are used only if they fit the recording (speech
                           starts / ends together, < 10 % of the words in its pauses), else the script is spread over
                           the recording's voiced stretches; no words and no meta.script -> stop, naming the command
                      In every case no word starts inside a pause of the recording (moved to where speech resumes).
                      The cache is keyed by the voice file's and the words file's contents: a new recording or an
                      edited words.json re-times the film on the next build.
  estimate(text)   -> honest text-only timing for a film without a voice yet: digits are read out ("3938" = 7
                      syllables), Latin words by syllable (an acronym letter by letter), pauses after punctuation.
                      Every entry carries "est": true, so a voice added later always re-times the film.
  check(vpath, bdir, tl) -> the voice-sync findings for the build-time gate (review.static_checks):
                      P0 voice-cut   the voice runs past the end of the picture (meta.duration too short)
                      P0 voice-sync  the words' speech ends more than max(0.3 s, 2 %) away from the recording's
                      P0 voice-sync  more than 10 % of the words start inside the recording's pauses
                      P0 cue-early   a "@词" visual lands more than 120 ms before its word is spoken (P1 above 80 ms)
                      P0 cue-scaled  a word-anchored animation sits inside a sped-up (time-scaled) block

Python standard library + ffmpeg only; the aligners are optional.
"""
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from array import array
from pathlib import Path

VERSION = "1"
PUN = set("，。、；：！？,.;:!?…—“”‘’（）《》「」\"'()[]【】·～~ ")
STOP = set("。！？!?…")
SOFT = set("，、；：,;:—")
EARLY_P0 = 0.120          # a word-anchored visual may land at most this much before its word (P0 beyond)
EARLY_P1 = 0.080          # up to this much early is normal (the 2-frame lead the entrances use)
LATE_OK = 0.150           # landing up to this much after the word starts reads as "on the word"
MIN_PAUSE = 0.12          # a gap in the speech shorter than this is a stop consonant, not a pause


# ------------------------------------------------------------------ reading: what is actually said
DIG = "零一二三四五六七八九"


def _under_10k(n):
    """1..9999 -> Chinese reading; zeros inside read once (1005 = 一千零五)."""
    out = ""
    units = [(1000, "千"), (100, "百"), (10, "十"), (1, "")]
    zero = False
    started = False
    for size, name in units:
        d = n // size
        n = n % size
        if d == 0:
            if started:
                zero = True
            continue
        if zero:
            out += "零"
            zero = False
        out += DIG[d] + name
        started = True
    return out


def int_reading(n):
    """non-negative int -> Chinese reading: 10 = 十, 248 = 二百四十八, 46479 = 四万六千四百七十九."""
    if n == 0:
        return "零"
    parts = []
    groups = [(100000000, "亿"), (10000, "万"), (1, "")]
    rest = n
    need_zero = False
    for size, name in groups:
        g = rest // size
        rest = rest % size
        if g == 0:
            if parts:
                need_zero = True
            continue
        text = int_reading(g) if g >= 10000 else _under_10k(g)
        if parts and (need_zero or g < 1000):
            text = "零" + text
        need_zero = False
        parts.append(text + name)
    s = "".join(parts)
    if s.startswith("一十"):
        s = s[1:]
    return s


def number_reading(run, nxt=""):
    """a digit run as it is read aloud: '248' -> 二百四十八, '97.5' -> 九十七点五, '2024' before 年 -> 二零二四,
    '007' -> 零零七. `nxt` is the glyph after the run."""
    run = run.replace(",", "")
    if "." in run:
        a, _, b = run.partition(".")
        head = int_reading(int(a)) if a else "零"
        return head + "点" + "".join(DIG[int(c)] for c in b if c.isdigit())
    if (len(run) == 4 and nxt == "年") or run.startswith("0") and len(run) > 1 or len(run) > 12:
        return "".join(DIG[int(c)] for c in run)
    return int_reading(int(run))


def latin_syllables(word):
    """rough spoken syllables of a Latin word: an acronym (all caps, <= 5 letters) letter by letter, else ~3 letters
    per syllable."""
    if word.isupper() and len(word) <= 5:
        return len(word)
    return max(1, round(len(word) / 3))


def reading_units(text):
    """text -> [(unit, glyph index)]: one unit per spoken syllable-ish piece, each pointing back at the glyph of
    `text` it came from. Digits become their reading (with % read as 百分之…), a Latin word is one unit
    (lower-cased), punctuation and spaces give no unit."""
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isdigit() and ch.isascii():
            j = i
            while j < n and ((text[j].isdigit() and text[j].isascii()) or (text[j] in ".," and j + 1 < n and text[j + 1].isdigit())):
                j += 1
            pct = j < n and text[j] in "%％"
            nxt = text[j] if j < n else ""
            spoken = number_reading(text[i:j], nxt)
            if pct:
                spoken = "百分之" + spoken
            span = j - i + (1 if pct else 0)
            for k in range(len(spoken)):
                out.append((spoken[k], i + min(span - 1, k * span // max(1, len(spoken)))))
            i = j + (1 if pct else 0)
            continue
        if ch.isascii() and ch.isalpha():
            j = i
            while j < n and text[j].isascii() and (text[j].isalpha() or text[j] == "-"):
                j += 1
            out.append((text[i:j].replace("-", "").lower(), i))
            i = j
            continue
        if ch in PUN or not ch.strip():
            i += 1
            continue
        out.append((ch, i))
        i += 1
    return out


# ------------------------------------------------------------------ honest estimate (no voice yet)
def estimate(text, rate=4.6, lead=0.35):
    """per-token word times for a script that has no recording yet. Chinese glyphs at `rate` per second, digits
    as their reading, Latin words by syllable, 0.22 s after ，、；： and 0.45 s after 。！？. Every entry has
    "est": true (a voice added later re-times the film instead of being laid over this guess)."""
    per = 1.0 / rate
    words = []
    t = lead
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if not ch.strip():
            i += 1
            continue
        if ch in PUN:
            words.append({"w": ch, "s": round(t, 3), "e": round(t, 3), "est": True})
            if ch in STOP:
                t += 0.45
            elif ch in SOFT:
                t += 0.22
            i += 1
            continue
        if ch.isdigit() and ch.isascii():
            j = i
            while j < n and ((text[j].isdigit() and text[j].isascii()) or (text[j] in ".," and j + 1 < n and text[j + 1].isdigit())):
                j += 1
            nxt = text[j] if j < n else ""
            spoken = number_reading(text[i:j], nxt)
            if j < n and text[j] in "%％":
                spoken = "百分之" + spoken
                j += 1
            run = text[i:j]
            dur = max(1, len(spoken)) * per
            words.append({"w": run, "s": round(t, 3), "e": round(t + dur, 3), "est": True})
            t += dur
            i = j
            continue
        if ch.isascii() and ch.isalpha():
            j = i
            while j < n and text[j].isascii() and (text[j].isalpha() or text[j] == "-"):
                j += 1
            run = text[i:j]
            dur = latin_syllables(run.replace("-", "")) * per * 0.9
            words.append({"w": run, "s": round(t, 3), "e": round(t + dur, 3), "est": True})
            t += dur
            i = j
            continue
        words.append({"w": ch, "s": round(t, 3), "e": round(t + per, 3), "est": True})
        t += per
        i += 1
    return words


def is_estimate(words):
    for w in words:
        if isinstance(w, dict) and w.get("est"):
            return True
    return False


def estimated_meta(vpath, meta):
    """True when meta.words is a text-only estimate (then a meta.duration next to it was estimated too)."""
    wrel = meta.get("words")
    if not wrel:
        return False
    p = Path(vpath).parent / wrel
    if not p.exists():
        return False
    return is_estimate(flat(json.loads(p.read_text(encoding="utf-8"))))


# ------------------------------------------------------------------ the recording: where is speech
_SPAN_CACHE = {}


def _probe(path):
    try:
        out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
        return float(out.strip())
    except Exception:
        return 0.0


def envelope(path, sr=8000, hop=0.01):
    """the recording's level in dBFS every `hop` seconds (mono, decoded by ffmpeg)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    pcm = array("h")
    pcm.frombytes(raw[: len(raw) // 2 * 2])
    if sys.byteorder == "big":
        pcm.byteswap()
    step = max(1, int(sr * hop))
    levels = []
    for k in range(0, len(pcm), step):
        chunk = pcm[k:k + step]
        if not chunk:
            break
        acc = 0
        for v in chunk:
            acc += v * v
        rms = math.sqrt(acc / len(chunk))
        if rms < 1.0:
            levels.append(-96.0)
        else:
            levels.append(20.0 * math.log10(rms / 32768.0))
    return levels, step / sr


def speech_spans(path):
    """([(start, end)] voiced stretches, duration) of a recording. The threshold adapts to the file: 12 dB over its
    noise floor and at most 35 dB under its loud speech; gaps under 0.12 s (stop consonants) are joined, blips
    under 0.05 s dropped."""
    p = Path(path)
    key = (str(p.resolve()), p.stat().st_mtime, p.stat().st_size)
    if key in _SPAN_CACHE:
        return _SPAN_CACHE[key]
    levels, hop = envelope(p)
    if not levels:
        return [], 0.0
    srt = sorted(levels)
    floor = max(srt[int(len(srt) * 0.10)], -90.0)
    loud = srt[min(len(srt) - 1, int(len(srt) * 0.95))]
    thr = max(floor + 12.0, loud - 35.0)
    spans = []
    start = None
    for k in range(len(levels)):
        on = levels[k] > thr
        if on and start is None:
            start = k
        if not on and start is not None:
            spans.append([start * hop, k * hop])
            start = None
    if start is not None:
        spans.append([start * hop, len(levels) * hop])
    joined = []
    for a, b in spans:
        if joined and a - joined[-1][1] < MIN_PAUSE:
            joined[-1][1] = b
        else:
            joined.append([a, b])
    kept = []
    for a, b in joined:
        if b - a >= 0.05:
            kept.append((round(a, 3), round(b, 3)))
    dur = _probe(p) or len(levels) * hop
    _SPAN_CACHE[key] = (kept, dur)
    return kept, dur


def pauses(spans, dur, min_len=MIN_PAUSE):
    """the silent stretches between (and around) the voiced spans, at least min_len long."""
    out = []
    t = 0.0
    for a, b in spans:
        if a - t >= min_len:
            out.append((t, a))
        t = b
    if dur - t >= min_len:
        out.append((t, dur))
    return out


def _pause_at(ps, t, margin=0.03):
    """the pause containing t (with `margin` inside its edges), else None."""
    for a, b in ps:
        if a + margin <= t < b - margin:
            return a, b
    return None


# ------------------------------------------------------------------ fitting words to the recording
def flat(data):
    out = []
    for x in data:
        if isinstance(x, dict) and "words" in x:
            out += x["words"]
        else:
            out.append(x)
    return out


def voiced(words):
    """the words that are spoken (not punctuation, not zero-length)."""
    out = []
    for w in words:
        tok = str(w.get("w", "")).strip()
        if not tok or all(c in PUN for c in tok):
            continue
        if float(w["e"]) - float(w["s"]) <= 1e-6:
            continue
        out.append(w)
    return out


def verify(words, spans, dur):
    """do these word times describe this recording? -> (ok, reason, facts)."""
    vw = voiced(words)
    if not vw or not spans:
        return False, "没有可比的词或录音里没有人声", {}
    ps = pauses(spans, dur, 0.25)
    first_w = float(vw[0]["s"])
    last_w = float(vw[-1]["e"])
    first_a = spans[0][0]
    last_a = spans[-1][1]
    in_pause = 0
    for w in vw:
        mid = (float(w["s"]) + float(w["e"])) / 2
        if _pause_at(ps, mid, 0.05):
            in_pause += 1
    share = in_pause / len(vw)
    tol = max(0.3, 0.02 * last_a)
    facts = {"words_end": round(last_w, 3), "speech_end": round(last_a, 3), "words_start": round(first_w, 3),
             "speech_start": round(first_a, 3), "in_pause": round(share, 3), "tolerance": round(tol, 3)}
    if abs(last_w - last_a) > tol:
        return False, f"逐字时间里的话在 {last_w:.2f}s 说完，录音在 {last_a:.2f}s 说完（差 {last_w - last_a:+.2f}s）", facts
    if abs(first_w - first_a) > max(0.4, tol):
        return False, f"逐字时间里的话从 {first_w:.2f}s 开始，录音从 {first_a:.2f}s 开始", facts
    if share > 0.10:
        return False, f"{share:.0%} 的字落在录音的停顿里", facts
    return True, "", facts


def refine(words, spans, dur):
    """no word starts inside a pause of the recording (moved to where the speech resumes) and no word ends inside
    one (moved back to where it stopped); a run of words piled onto one onset is spread to the next word."""
    ps = pauses(spans, dur)
    out = []
    for w in words:
        out.append(dict(w))
    idx = []
    for k in range(len(out)):
        tok = str(out[k].get("w", "")).strip()
        if tok and not all(c in PUN for c in tok):
            idx.append(k)
    for k in idx:
        w = out[k]
        s = float(w["s"])
        e = float(w["e"])
        hit = _pause_at(ps, s)
        if hit:
            s = hit[1]
        hit = _pause_at(ps, e)
        if hit and hit[0] > s + 0.04:
            e = hit[0]
        if e < s + 0.04:
            e = s + 0.04
        w["s"] = s
        w["e"] = e
    # piled-up runs (several words moved to one onset): spread them up to the next word that kept its time
    j = 0
    while j < len(idx):
        k = idx[j]
        run = [k]
        m = j + 1
        while m < len(idx) and float(out[idx[m]]["s"]) <= float(out[run[-1]]["s"]) + 0.02:
            run.append(idx[m])
            m += 1
        if len(run) > 1:
            a = float(out[run[0]]["s"])
            if m < len(idx):
                b = float(out[idx[m]]["s"])
            else:
                b = a + 0.18 * len(run)
            step = max(0.04, (b - a) / len(run))
            for r in range(len(run)):
                out[run[r]]["s"] = a + step * r
                out[run[r]]["e"] = max(float(out[run[r]]["e"]), a + step * (r + 1))
        j = m
    # punctuation sits at the end of the word before it; round
    last = 0.0
    for w in out:
        tok = str(w.get("w", "")).strip()
        if tok and all(c in PUN for c in tok):
            w["s"] = last
            w["e"] = last
        else:
            last = float(w["e"])
        w["s"] = round(float(w["s"]), 3)
        w["e"] = round(float(w["e"]), 3)
        w.pop("est", None)
    return out


def moved_count(before, after):
    """how many spoken tokens refine() moved by more than 40 ms (token lists of the same length and order)."""
    n = 0
    for a, b in zip(before, after):
        tok = str(a.get("w", "")).strip()
        if not tok or all(c in PUN for c in tok):
            continue
        if abs(float(a["s"]) - float(b["s"])) > 0.04:
            n += 1
    return n


# ------------------------------------------------------------------ alignment on the recording
def _align_mod():
    here = Path(__file__).resolve().parents[1]
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    import align
    return align


def asr_align(voice, script):
    """word times for `script` measured on `voice` with a speech recognizer -> (words, backend), or (None, why) when
    no recognizer is installed or usable. Without a script the recognizer's own text is used."""
    align = _align_mod()
    tried = []
    for be in ("faster-whisper", "whisperx"):
        try:
            if be == "faster-whisper":
                asr = align.asr_faster_whisper(voice)
                be = be + ":" + str(align.ASR_USED.get("model", ""))
            else:
                asr = align.asr_whisperx(voice)
        except ImportError:
            tried.append(f"{be} 没装")
            continue
        except Exception as e:                     # a model download that failed, a broken install …
            tried.append(f"{be}：{type(e).__name__} {str(e)[:80]}")
            continue
        if not asr:
            tried.append(f"{be} 没听出字")
            continue
        text = script
        if not text:
            text = "".join(w["w"] for w in asr)
        times, sc = align.match(text, asr)
        return align.to_words(text, times), be
    return None, "；".join(tried)


def pause_align(voice, script):
    """no recognizer: the script's clauses spread over the recording's voiced stretches (align.py --backend silence)."""
    align = _align_mod()
    times, sc = align.silence_align(voice, script)
    return align.to_words(script, times)


def _sha(path):
    h = hashlib.sha1()
    with open(path, "rb") as f:
        while True:
            b = f.read(1 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:16]


def sidecar_path(words_path):
    p = Path(words_path)
    return p.with_name(p.stem + ".align.json")


def write_sidecar(words_path, voice, backend):
    """align.py writes next to its words.json which recording the times were measured on (and how)."""
    info = {"voice": Path(voice).name, "voice_sha": _sha(voice), "backend": backend}
    sidecar_path(words_path).write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")


def read_sidecar(words_path):
    p = sidecar_path(words_path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def voice_path(vpath, meta):
    voice = meta.get("voice")
    if not voice:
        return None
    p = Path(os.path.expandvars(os.path.expanduser(str(voice))))
    if not p.is_absolute():
        p = Path(vpath).parent / p
    return p


def resolve(vpath, meta=None, log=print):
    """the words file the film must be timed by (see module doc). None when the film has neither voice nor words."""
    vpath = Path(vpath)
    src = vpath.parent
    if meta is None:
        meta = json.loads(vpath.read_text(encoding="utf-8")).get("meta", {})
    wrel = meta.get("words")
    wpath = src / wrel if wrel else None
    if wpath is not None and not wpath.exists():
        raise SystemExit(f"meta.words 指向的文件不存在：{wpath}")
    vp = voice_path(vpath, meta)
    if vp is None:
        return wpath
    if not vp.exists():
        raise SystemExit(f"meta.voice 指向的录音不存在：{vp}")
    cache_dir = src / "assets" / "audio"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f"{vp.stem}.sync-words.json"
    stamp = cache_dir / f"{vp.stem}.sync.json"
    vsha = _sha(vp)
    key = VERSION + ":" + vsha + ":" + (_sha(wpath) if wpath else "-")
    if stamp.exists() and cache.exists():
        try:
            st = json.loads(stamp.read_text(encoding="utf-8"))
        except Exception:
            st = {}
        if st.get("key") == key:
            return cache
    spans, dur = speech_spans(vp)
    words = flat(json.loads(wpath.read_text(encoding="utf-8"))) if wpath else []
    side = read_sidecar(wpath) if wpath else {}
    facts = {}
    reason = ""
    if words and not is_estimate(words):
        ok, reason, facts = verify(words, spans, dur)
    else:
        ok = False
        reason = "逐字时间是按字数估的（还没有录音时的占位）" if words else "没有逐字时间（meta.words）"
    trusted = bool(words) and not is_estimate(words) and side.get("voice_sha") == vsha \
        and not str(side.get("backend", "")).startswith("silence")
    backend = side.get("backend") if trusted else None
    status = "measured" if trusted else ""
    if not trusted:
        # word times not measured on THIS recording (TTS estimates, another take, a guess from the text):
        # measure them now, the script being the words' own text
        script = "".join(str(w.get("w", "")) for w in words) if words else (meta.get("script") or "")
        got, why = asr_align(vp, script)
        if got:
            words = got
            backend = why
            status = "aligned"
            log(f"voice-sync: 按录音对齐逐字时间（{backend}）" + (f"；原来的逐字时间不能直接用：{reason}" if reason else ""))
        elif ok:
            status = "verified"
            log(f"voice-sync: 没装语音对齐（{why}），逐字时间和录音的起止、停顿对得上，先用它；更准：pip install faster-whisper")
        elif script:
            words = pause_align(vp, script)
            backend = "silence"
            status = "aligned"
            log(f"voice-sync: {reason} → 按录音的停顿重新对时（没装语音对齐：{why}）；单个词更准：pip install faster-whisper")
        else:
            rel = os.path.relpath(vp, src)
            out_rel = wrel or "assets/audio/words.json"
            raise SystemExit(
                f"✗ 有录音 {rel}，但{reason}，也没有稿子可以对齐（{why}）。画面必须按真实录音对时：\n"
                f"  装上对齐模型再构建一次（会自动对齐）：pip install faster-whisper\n"
                f"  或者手动对齐：python3 scripts/align.py {rel} 稿子.txt --out {out_rel}"
                + ("" if wrel else f"，并在 meta 里写 \"words\": \"{out_rel}\""))
    fixed = refine(words, spans, dur)
    moved = moved_count(words, fixed)
    cache.write_text(json.dumps(fixed, ensure_ascii=False), encoding="utf-8")
    info = {"key": key, "status": status, "backend": backend, "reason": reason, "voice": vp.name,
            "words": wrel, "moved_out_of_pauses": moved, "facts": facts}
    stamp.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    if moved and status != "measured":
        log(f"voice-sync: {moved} 个字原本落在录音的停顿里，已挪到说出来的那一刻")
    return cache


# ------------------------------------------------------------------ the gate
def _built_voice(bdir):
    """(audio file, start in film time) of the voice clip in a built index.html, else (None, 0)."""
    p = Path(bdir) / "index.html"
    if not p.exists():
        return None, 0.0
    doc = p.read_text(encoding="utf-8")
    m = re.search(r'<audio id="voice"[^>]*?src="([^"]+)"[^>]*?data-start="([\d.]+)"', doc)
    if not m:
        return None, 0.0
    return Path(bdir) / m.group(1), float(m.group(2))


def check(vpath, bdir, tl):
    """voice <-> picture findings for a build (see module doc). [] when the film has no voice."""
    found = []
    if not tl or not bdir:
        return found
    sync = tl.get("voice_sync") or {}
    audio, start = _built_voice(bdir)
    if audio is None or not audio.exists():
        return found
    spans, adur = speech_spans(audio)
    film_spans = []
    for a, b in spans:
        film_spans.append((a + start, b + start))
    D = float(tl.get("duration") or 0)
    voice_end = start + adur
    speech_end = film_spans[-1][1] if film_spans else start
    if D and speech_end > D + 0.05:
        found.append(("P0", "voice-cut", f"口播在 {speech_end:.2f}s 才说完，画面在 {D:.2f}s 就结束了：删掉 meta.duration（有录音时按录音长度定）或改长"))
    elif D and voice_end > D + 0.5:
        found.append(("P1", "voice-cut", f"录音文件比画面长 {voice_end - D:.2f}s（末尾是静音则无妨）"))
    wend = sync.get("words_end")
    if wend is not None and film_spans:
        tol = max(0.3, 0.02 * speech_end)
        if abs(wend - speech_end) > tol:
            found.append(("P0", "voice-sync", f"画面按逐字时间在 {wend:.2f}s 说完，录音在 {speech_end:.2f}s 说完（差 {wend - speech_end:+.2f}s，"
                          f"画面{'晚' if wend > speech_end else '早'}）：逐字时间不是这条录音的，删掉 assets/audio/*.sync.json 重新构建"))
    starts = sync.get("word_starts") or []
    if starts and film_spans:
        ps = pauses(film_spans, D or voice_end, 0.25)
        bad = 0
        for s in starts:
            if _pause_at(ps, s, 0.05):
                bad += 1
        if bad / len(starts) > 0.10:
            found.append(("P0", "voice-sync", f"{bad}/{len(starts)} 个字在录音的停顿里开始：逐字时间和录音对不上，按录音重新对齐（scripts/align.py）"))
    ps = pauses(film_spans, D or voice_end, MIN_PAUSE)
    early = []
    soft = []
    for c in tl.get("cues") or []:
        cue = str(c.get("cue", ""))
        if cue.split("+")[0].split("-")[0].endswith("$"):
            continue                                   # "@词$" lands when the word ends
        land = float(c["t"]) - (2.0 / 30 if c.get("kind") != "cut" else 0.0)
        hit = _pause_at(ps, land, 0.0)
        if not hit:
            continue
        gap = hit[1] - land
        if gap > EARLY_P0:
            early.append((c, gap))
        elif gap > EARLY_P1:
            soft.append((c, gap))
    for c, gap in early[:12]:
        found.append(("P0", "cue-early", f"#{c.get('beat')} {c['t']:.2f}s {c['cue']} 的画面比口播早 {gap * 1000:.0f} ms 落下（话还没说出来）"))
    if len(early) > 12:
        found.append(("P0", "cue-early", f"还有 {len(early) - 12} 处画面早于口播"))
    for c, gap in soft[:6]:
        found.append(("P1", "cue-early", f"#{c.get('beat')} {c['t']:.2f}s {c['cue']} 的画面比口播早 {gap * 1000:.0f} ms"))
    found += scaled_cues(bdir, tl)
    return found


_BLOCK = re.compile(r'\{ const __m = tl; \{ const tl = gsap\["timeline"\]\(\);\n(.*?)\ntl\.timeScale\(([\d.]+)\); __m\.add\(tl, (-?[\d.]+)\); \} \}', re.S)
_AT = re.compile(r",\s*(-?\d+(?:\.\d+)?)\);")


def scaled_cues(bdir, tl):
    """P0 cue-scaled: a word-anchored tween inside a sped-up block (timeScale s, compressed towards the beat start t)
    lands (T - t)(1 - 1/s) before its word."""
    p = Path(bdir) / "index.html"
    if not p.exists():
        return []
    doc = p.read_text(encoding="utf-8")
    found = []
    for m in _BLOCK.finditer(doc):
        s = float(m.group(2))
        if s <= 1.0:
            continue
        t0 = float(m.group(3)) / (1 - 1 / s)
        times = []
        for x in _AT.findall(m.group(1)):
            times.append(float(x))
        worst = None
        for i, marks in tl.get("cue_marks") or []:
            for mk in marks:
                if mk <= t0 + 0.005:
                    continue
                for T in times:
                    if mk - 0.30 <= T <= mk + 0.002:    # on the word or in the 0.3 s lead-in that lands on it
                        pull = (mk - t0) * (1 - 1 / s)
                        if worst is None or pull > worst[1]:
                            worst = (i, pull)
        if worst and worst[1] > EARLY_P1:
            found.append(("P0", "cue-scaled", f"#{worst[0]} 对口播的动画被整段加速 ×{s:.2f}，会比词早 {worst[1] * 1000:.0f} ms 落下"))
    return found
