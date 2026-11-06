"""beatsync — the film's cuts, sound hits and quick-cut runs sit on the music's measured beats.

  meta.music_beats = "music/tech/Song.beats.json"   {"tempo": 117.45, "beats": [seconds, ...]} (also [{"time": s}, ...]);
                     omitted → <music name>.beats.json next to meta.music, if it exists. The song starts at film 0 s
                     (that is how build.py lays the bed), so a beat at song second s is a beat at film second s.
  meta.beat_snap   = true (default when beats are found) | false | 0.12   tolerance in seconds.
                     Beat start times that are free (a number, or chained from the previous beat) move to the nearest
                     beat within the tolerance. Word-anchored times ("@词") stay authoritative: they may move later by
                     up to the tolerance, earlier by at most 2 frames (picture a hair early is invisible, a cut well
                     before its word is not). The same rule moves per-beat "sfx" times and their "hit" flashes.
                     A beat with "snap": false keeps its time. Every move is listed in timeline.json ("snap").
  per beat "music" = "up" | dB      lift the music bed for this beat (voiceless runs, montage). "up" = meta.music_up dB
                     (default 8). The quick-cut "montage" effect lifts by default ("music": false to keep the bed).

Also shared with scripts/montage.py and scripts/review.py: the film-time beat grid, best_moment() (the best readable
window of a clip) and flat() (a frame that is mostly one colour).
"""
import json, os, subprocess
from pathlib import Path

TOL = 0.12


def _path(p, base):
    p = Path(os.path.expandvars(os.path.expanduser(str(p))))
    return p if p.is_absolute() else Path(base) / p


def beats_file(meta, base):
    """the beats.json for this film's music, or None."""
    if meta.get("music_beats"):
        p = _path(meta["music_beats"], base)
        if not p.exists(): raise SystemExit(f"meta.music_beats: {p} not found")
        return p
    if not meta.get("music"): return None
    m = _path(meta["music"], base)
    p = m.with_name(m.stem + ".beats.json")
    return p if p.exists() else None


def read_beats(path):
    """(tempo or None, [seconds]) from a beats.json ({"tempo", "beats"} or a bare list, entries may be {"time": s})."""
    j = json.loads(Path(path).read_text())
    raw = j.get("beats", []) if isinstance(j, dict) else j
    bs = []
    for b in raw:
        bs.append(float(b.get("time", 0) if isinstance(b, dict) else b))
    bs.sort()
    return (j.get("tempo") if isinstance(j, dict) else None), bs


def load(meta, base):
    """{"src", "tempo", "beats", "tol", "snap"} for this film, or None when it has no measured beats."""
    p = beats_file(meta, base)
    if not p: return None
    tempo, bs = read_beats(p)
    if not bs: return None
    s = meta.get("beat_snap", True)
    tol = TOL if s is True or s is None else (float(s) if s else 0.0)
    return {"src": str(p), "tempo": tempo, "beats": bs, "tol": tol, "snap": bool(s) and tol > 0}


def frame(x, fps):
    return round(float(x) * fps) / fps


class Snapper:
    """moves times onto the beat grid within the tolerance and an anchor's allowed window; remembers every move."""

    def __init__(self, info, fps):
        self.beats = [frame(b, fps) for b in info["beats"]]
        self.tol = info["tol"]
        self.on = info["snap"]
        self.fps = fps
        self.moves = []

    def nearest(self, t):
        best = None
        for b in self.beats:
            if best is None or abs(b - t) < abs(best - t): best = b
            if b > t + 1: break
        return best

    def window(self, raw):
        """(how far earlier, how far later) a time may move: free times ± tol; "@词" anchors 2 frames earlier, tol later."""
        if isinstance(raw, str) and raw.strip().startswith("@"):
            return min(self.tol, 2 / self.fps), self.tol
        return self.tol, self.tol

    def period(self):
        """the median beat spacing."""
        ds = sorted(y - x for x, y in zip(self.beats, self.beats[1:]))
        return ds[len(ds) // 2] if ds else 0.5

    def snap(self, t, raw, what, lo=None, hi=None, later=None):
        """t moved to the nearest beat when allowed (and inside [lo, hi]); otherwise t unchanged. later = how far a
        voiceless run may wait for its beat (a montage starts on the next beat, up to one beat later)."""
        if not self.on or t is None: return t
        back, fwd = self.window(raw)
        b = self.nearest(float(t))
        if later:
            fwd = max(fwd, later)
            nxt = next((x for x in self.beats if x >= float(t) - 0.5 / self.fps), None)
            if b is not None and b - float(t) < -back - 1e-6 and nxt is not None: b = nxt      # earlier beat not allowed: wait for the next
        if b is None: return t
        dt = b - float(t)
        if dt < -back - 1e-6 or dt > fwd + 1e-6: return t
        if lo is not None and b < lo: return t
        if hi is not None and b > hi: return t
        if abs(dt) < 0.5 / self.fps: return t                          # already on the beat (same frame)
        self.moves.append({"what": what, "from": round(float(t), 3), "to": round(b, 3), "by": round(dt, 3),
                           "anchor": raw if isinstance(raw, str) else None})
        return type(t)(round(b, 3)) if type(t) is not float else round(b, 3)


def snap_beats(beats, times, snapper, lead_floor=0.0, skip=()):
    """snap each beat's start (not the first) in place; keeps order with ≥ 4 frames between beats."""
    gap = 4 / snapper.fps
    for i in range(1, len(times)):
        b = beats[i]
        if b.get("snap") is False or i in skip: continue
        t = times[i][0]
        lo = max(times[i - 1][0] + gap, lead_floor)
        hi = times[i + 1][0] - gap if i + 1 < len(times) else None
        later = snapper.period() * 1.02 if b.get("fx") == "montage" else None
        times[i][0] = snapper.snap(t, b.get("t"), f"beat {i} ({b.get('fx') or b.get('scene')})", lo, hi, later)


def up_windows(beats, times, meta):
    """[(t0, t1, dB)] where the music is lifted: beats with "music": "up" | dB; montage beats by default."""
    out = []
    dflt = float(meta.get("music_up", 8))
    for b, (t, d) in zip(beats, times):
        m = b.get("music")
        if m is None and b.get("fx") == "montage": m = "up"
        if m in (None, False, "keep", "bed"): continue
        db = dflt if m in ("up", True) else float(m)
        if db: out.append((float(t), float(t) + float(d), db))
    return out


def bed_volume(X, vol):
    """the music clip's data-volume: unchanged, unless pacing.duck lifted the bed (it then renders the normal level
    lower in the file and the clip plays louder, so a lift never clips)."""
    g = getattr(X, "music_gain", 1.0)
    return vol if g == 1.0 else round(float(vol) * g, 4)


def run_end(X, b, t):
    """end of a montage beat that owns its length: one cut per clip on the beat grid from t."""
    import math
    per = float(b.get("per", 1))
    n = max(1, len(b.get("clips") or []))
    info = getattr(X, "music_beats", None)
    if info: bs = info["beats"]
    else:
        meta = X.v.get("meta", {})
        bpm = float(meta.get("bpm") or 0)
        step = 60.0 / bpm if bpm else 0.5
        off = float(meta.get("beat_offset", 0.0))
        k0 = max(0, math.floor((t - off) / step))
        bs = [off + k * step for k in range(k0, k0 + int(n * max(per, 1)) + 4)]
    g = [frame(x, X.fps) for x in grid(bs, per)]
    step = (g[1] - g[0]) if len(g) > 1 else 0.5
    cuts = [frame(t, X.fps)]
    for x in g:
        if x > cuts[-1] + 0.45 * step: cuts.append(x)
        if len(cuts) > n: break
    if len(cuts) <= n:                     # the song ran out of beats: keep its last spacing
        while len(cuts) <= n: cuts.append(cuts[-1] + step)
    return cuts[n]


def record(X, tl, beats, D):
    """add the beat-sync facts to timeline.json (only for films with measured beats; other films keep the old format)."""
    from . import pacing
    info = X.music_beats
    moved = {}
    for m in (X.snapper.moves if X.snapper else []):
        if m["what"].startswith("beat "): moved[int(m["what"].split()[1])] = m["from"]
    for row in tl["beats"]:
        if row["i"] in moved: row["t0"] = moved[row["i"]]
        cuts = beats[row["i"]].get("_cuts")
        if cuts: row["cuts"] = cuts
    tl["music_beats"] = {"src": Path(info["src"]).name, "tempo": info["tempo"], "tol": info["tol"], "snap": info["snap"]}
    tl["grid"] = [round(frame(b, X.fps), 3) for b in info["beats"] if b <= D]
    tl["snap"] = X.snapper.moves if X.snapper else []
    tl["speech"] = [[round(a, 3), round(b, 3)] for a, b in pacing.speech_spans(X._words)] if X._words else []
    tl["music_up"] = [[round(a, 3), round(b, 3), db] for a, b, db in getattr(X, "music_up", [])]
    tl["sfx"] = getattr(X, "sfx_hits", [])
    tl["fps"] = X.fps


# ---------------------------------------------------------------- shared with montage.py / review.py
def grid(beats, per=1.0, offset=0.0):
    """film-time cut grid: every `per` beats (0.5 = half beats)."""
    film = [b + offset for b in beats]
    if per == 0.5:
        halves = []
        for x, y in zip(film, film[1:]):
            halves.append(x)
            halves.append((x + y) / 2)
        return halves
    step = max(1, int(per))
    return film[::step]


def flat(im):
    """a frame that is mostly one colour: share of pixels close to the most common colour."""
    small = im.convert("RGB").resize((27, 48))
    raw = small.tobytes()
    counts = {}
    for i in range(0, len(raw), 3):
        key = (raw[i] // 24, raw[i + 1] // 24, raw[i + 2] // 24)
        counts[key] = counts.get(key, 0) + 1
    top = max(counts.values())
    return top / (len(raw) // 3)


def best_moment(src, length, dur, tmp):
    """start of the best `length` s window: the picture is full (not a near-empty ground) for the whole window, there
    is no cut or transition wipe inside, and a little motion breaks ties. A motion-design beat looks best just after
    its entrance settles, not mid-transition, so readability comes first."""
    from PIL import Image
    rate = 10
    d = Path(tmp) / f"scan_{Path(src).stem}"
    d.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-vf", f"fps={rate},scale=54:-2", str(d / "s_%05d.png")], check=True)
    files = sorted(d.glob("s_*.png"))
    full = []
    grey = []
    for f in files:
        im = Image.open(f)
        full.append(1.0 - flat(im))
        grey.append(im.convert("L").tobytes())
    move = [0.0]
    for x, y in zip(grey, grey[1:]):
        diff = 0
        for i in range(len(x)):
            diff += abs(x[i] - y[i])
        move.append(diff / (255.0 * len(x)))
    n = max(1, int(round(length * rate)))
    best, best_at = -1.0, min(0.3, max(0.0, dur - length))
    for i in range(len(files) - n - 2):
        t = i / rate
        if t < 0.3 or t + length > dur - 0.3:
            continue
        window_full = min(full[i:i + n + 1])
        window_move = max(move[i + 1:i + n + 3])      # 0.2 s past the end too: no wipe starting on the last frame
        if window_move > 0.12:      # a cut or a wipe inside the window
            continue
        score = window_full + 0.15 * min(1.0, sum(move[i + 1:i + n + 1]) * 5)
        if score > best:
            best, best_at = score, t
    return best_at


def best_moment_cached(src, length, dur, cache_dir):
    """best_moment with a small json cache next to the build (a rebuild does not rescan every clip)."""
    src = Path(src)
    cf = Path(cache_dir) / ".montage_cache.json"
    try: cache = json.loads(cf.read_text())
    except (OSError, ValueError): cache = {}
    key = f"{src.resolve()}|{src.stat().st_mtime:.0f}|{length:.3f}"
    if key not in cache:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            cache[key] = best_moment(src, length, dur, td)
        cf.parent.mkdir(parents=True, exist_ok=True)
        cf.write_text(json.dumps(cache, indent=0))
    return float(cache[key])

