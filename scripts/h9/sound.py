"""sound — the effect sounds of a film: which file, exactly when, how loud.

Every `X.sfx(t, role)` call in a scene, effect, transition or style becomes an event. The scheduler then decides,
from the final timeline the build already has (beat starts, "@词" landings, transition cuts):

  when    the sound's perceptual peak (measured once per file, assets/sfx/manifest.json) lands on the frame where the
          motion lands — not the file start on the motion start. An effect's call names the moment its motion starts;
          the tween it emitted at that moment says when it arrives (ease + duration), and that arrival is the impact.
          `X.sfx(t, role, at="hit")` (transitions, beat "sfx" moments) means t is the impact itself.
          A whoosh peaks on the arrival (fast-in, settle) or at the fastest point of an ease-in-out move; a riser ends
          on the next impact; a count-up ticks with the digits (fast, then slower, a last tick on the settle); typing
          plays one key per glyph; a staggered row of chips pops chip by chip.
  which   each family (impact, whoosh, pop, tick, click, key, tap, paper …) has several variants. The style picks the
          family (its "sfx" map), the scheduler rotates variants, seeded by beat index (same build → same sounds),
          never the same file twice in a row.
  loud    levels are set relative to the narration, through a phone-speaker weighting: during speech an impact sits
          ~6–8 LU under the voice, a whoosh ~10, a tick ~11–14; in pauses ~4 LU closer. meta.sfx_level =
          off | subtle | normal (default) | punchy moves them all. Bigger motions get bigger sounds.

timeline.json["sfx_plan"] records every placed sound (file, impact, start, peak, level, what motion it follows) and
review.py checks it against the rendered audio.
"""
import json, math, re, subprocess, zlib
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
SFX = SKILL / "assets" / "sfx"

QUIET_FX = {"breather", "chapter_breather", "interlude", "suspense", "freeze_frame"}   # beats that should stay quiet
PRESETS = {"off": None, "subtle": -4.0, "normal": 0.0, "punchy": 3.0}

# family -> kind; variants are <family>, <family>_2, <family>_3 … present in the manifest (key / tap use _1.._4)
KIND = {"hit": "impact", "slam": "impact", "boom": "impact",
        "whoosh": "whoosh", "whoosh_soft": "whoosh", "whoosh_deep": "whoosh",
        "riser": "riser",
        "pop": "small", "tick": "small", "click": "small", "key": "small", "tap": "small", "beep": "small",
        "bell": "small", "boing": "small",
        "paper": "material", "brush": "material", "tape": "material", "shutter": "material", "glitch": "material",
        "type": "material"}
LARGE_ROLES = {"slam", "boom", "title", "stamp", "thud", "land"}
# what plays the ticks of a sequence, from the family the style chose for that role
SEQ_FAMILY = {"type": "key", "key": "key", "tick": "tick", "click": "click", "pop": "pop", "tap": "tap", "beep": "tick"}
# target loudness relative to the voice (LU, phone-weighted momentary), (during speech, in a pause)
TARGET = {"L": (-6.0, -2.0), "M_impact": (-8.0, -4.0), "M": (-10.0, -6.0), "S": (-11.0, -7.0), "T": (-14.0, -10.0)}
RANK = {"L": 4, "M_impact": 3, "M": 2, "S": 1, "T": 0}
PEAK_CAP_DB = -5.0          # no single effect sound peaks above this before the final loudness pass (~+4 dB later)
F_LAND = 0.9                # an entrance "lands" when it has covered 90 % of its move (same rule as core.P90)

_MAN = None


def manifest():
    """{file stem: {peak, loud, loud_full, sample_peak_db, …}}: assets/sfx/manifest.json (scripts/sfx.py writes it),
    plus any wav in assets/sfx it does not list yet, measured here the same way."""
    global _MAN
    if _MAN is None:
        p = SFX / "manifest.json"
        _MAN = json.loads(p.read_text()) if p.exists() else {}
        for w in sorted(SFX.glob("*.wav")):
            if w.stem not in _MAN:
                m = _measure(w)
                if m: _MAN[w.stem] = m
    return _MAN


def _measure(path):
    import array, wave
    try:
        with wave.open(str(path)) as w:
            sr, ch, raw = w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())
            if w.getsampwidth() != 2: return None
    except (OSError, EOFError, wave.Error):
        return None
    a = array.array("h"); a.frombytes(raw[:len(raw) // 2 * 2])
    xs = [a[i] / 32768 for i in range(0, len(a), ch)]
    if not xs: return None
    win = max(1, int(0.010 * sr)); acc = 0.0; best, k = -1.0, 0
    for i, x in enumerate(xs):
        acc += x * x
        if i >= win: acc -= xs[i - win] * xs[i - win]
        if acc > best: best, k = acc, i
    def loud(hp):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                            hp + "apad=pad_dur=0.5,ebur128=metadata=1,ametadata=print:key=lavfi.r128.M:file=-", "-f", "null", "-"],
                           capture_output=True, text=True)
        ms = [float(x) for x in re.findall(r"lavfi\.r128\.M=(-?[\d.]+)", r.stdout)]
        return max(ms) if ms else None
    lp = loud("highpass=f=150:p=2,")
    if lp is None: return None
    return {"dur": round(len(xs) / sr, 3), "peak": round(max(0, k - win // 2) / sr, 3), "loud": lp, "loud_full": loud(""),
            "sample_peak_db": round(20 * math.log10(max(abs(x) for x in xs) + 1e-9), 2)}


def family_of(name):
    """'whoosh_soft_2' -> 'whoosh_soft'; 'key_3' -> 'key'; 'hit' -> 'hit'."""
    m = re.match(r"^(.*?)(?:_(\d+))?$", name)
    base = m.group(1)
    return base if base in KIND else (name if name in KIND else base)


def variants(fam):
    man = manifest()
    out = [k for k in man if family_of(k) == fam]
    return sorted(out, key=lambda k: (k != fam, k))


class Snd(str):
    """a sound event's url that carries its facts through the (t, url, vol) tuples other passes rescale."""
    def __new__(cls, url, **kw):
        s = str.__new__(cls, url)
        s.__dict__.update(kw)
        return s


def event(X, t, name, role, vol, style_vol, at=None):
    """what core.Ctx.sfx records (a Snd in X.audio)."""
    fam = family_of(name)
    lib = name in manifest() or fam in KIND and variants(fam)
    hint = 0.0
    if vol is not None and style_vol:
        hint = max(-6.0, min(6.0, 20 * math.log10(max(float(vol), 1e-3) / float(style_vol))))
    sv = float(style_vol or 0.4)
    style_db = max(-5.0, min(2.0, 0.5 * 20 * math.log10(max(sv, 1e-3) / 0.4)))
    beat = getattr(X, "beat", {}) or {}
    return Snd(f"assets/sfx/{name}.wav", name=name, asked=name, fam=fam, role=role, lib=bool(lib), exact=at is not None,
               hint=max(-6.0, min(3.0, hint + style_db)), beat=int(beat.get("i", -1)), ci=len(X.tws), t0=float(t), done=at is not None,
               motion=("cue" if at is not None else None), seq=None, accent=False, vol_in=vol)


# ---------------------------------------------------------------- eases (GSAP 3 names)
def _ease_fn(name):
    name = (name or "power1.out").strip()
    m = re.match(r"^([a-zA-Z0-9]+)(?:\.(inOut|in|out))?(?:\(([^)]*)\))?$", name)
    if not m: return (lambda x: 1 - (1 - x) ** 2), "out"
    base, typ, arg = m.group(1).lower(), m.group(2) or "out", m.group(3)
    if base in ("none", "linear", "power0"): return (lambda x: x), "none"
    if base == "steps": return (lambda x: 1.0 if x >= 1 else math.floor(x * max(1, int(float(arg or 1)))) / max(1, int(float(arg or 1)))), "steps"
    pw = {"power1": 2, "quad": 2, "power2": 3, "cubic": 3, "power3": 4, "quart": 4, "power4": 5, "quint": 5, "strong": 5}
    if base in pw:
        k = pw[base]; fin = lambda x, k=k: x ** k
    elif base == "sine": fin = lambda x: 1 - math.cos(x * math.pi / 2)
    elif base == "expo": fin = lambda x: 0.0 if x <= 0 else 2 ** (10 * (x - 1))
    elif base == "circ": fin = lambda x: 1 - math.sqrt(max(0.0, 1 - x * x))
    elif base == "back":
        s = float((arg or "1.70158").split(",")[0]); fin = lambda x, s=s: x * x * ((s + 1) * x - s)
    elif base == "elastic":
        fin = lambda x: 0.0 if x <= 0 else (1.0 if x >= 1 else -(2 ** (10 * x - 10)) * math.sin((x * 10 - 10.75) * (2 * math.pi) / 3))
    elif base == "bounce":
        def bo(x):
            n1, d1 = 7.5625, 2.75
            if x < 1 / d1: return n1 * x * x
            if x < 2 / d1: x -= 1.5 / d1; return n1 * x * x + 0.75
            if x < 2.5 / d1: x -= 2.25 / d1; return n1 * x * x + 0.9375
            x -= 2.625 / d1; return n1 * x * x + 0.984375
        fin = lambda x: 1 - bo(1 - x)
    else:
        fin = lambda x: x * x
    if typ == "in": return fin, "in"
    if typ == "out": return (lambda x: 1 - fin(1 - x)), "out"
    return (lambda x: fin(2 * x) / 2 if x < 0.5 else 1 - fin(2 - 2 * x) / 2), "inOut"


def land_frac(ease, kind="impact"):
    """fraction of the duration at which the motion visibly arrives (first time it covers 90 %); for a whoosh on an
    ease-in-out move, the fastest point (the middle)."""
    f, typ = _ease_fn(ease)
    if kind == "whoosh" and typ == "inOut": return 0.5
    if typ in ("steps",): return 1.0
    for i in range(1, 201):
        x = i / 200
        if f(x) >= F_LAND: return x
    return 1.0


def inv_progress(ease, q):
    """earliest x with ease(x) >= q (for count-up ticks)."""
    f, _ = _ease_fn(ease)
    lo = 0.0
    for i in range(1, 401):
        x = i / 400
        if f(x) >= q - 1e-9: return x
    return 1.0


# ---------------------------------------------------------------- tween lines -> records
CALL = re.compile(r"\btl\.(fromTo|from|to|set)\(")
NUM = re.compile(r"^-?\d+(?:\.\d+)?$")


def _close(s, j):
    """index just past the bracket that closes at depth 0, starting inside it at j."""
    depth, q = 1, None
    k = j
    while k < len(s) and depth:
        c = s[k]
        if q:
            if c == q and s[k - 1] != "\\": q = None
        elif c in "\"'`": q = c
        elif c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        k += 1
    return k


def _split(body):
    out, depth, q, cur = [], 0, None, []
    for k, c in enumerate(body):
        if q:
            cur.append(c)
            if c == q and body[k - 1] != "\\": q = None
            continue
        if c in "\"'`": q = c
        elif c in "([{": depth += 1
        elif c in ")]}": depth -= 1
        if c == "," and depth == 0: out.append("".join(cur)); cur = []; continue
        cur.append(c)
    out.append("".join(cur))
    return out


def _top(vars_):
    """{key: raw value} of the top level of a JS object literal."""
    v = vars_.strip()
    if not (v.startswith("{") and v.endswith("}")): return {}
    out = {}
    for part in _split(v[1:-1]):
        if ":" not in part: continue
        k, val = part.split(":", 1)
        out[k.strip().strip("\"'")] = val.strip()
    return out


MOTION = {"x", "y", "xPercent", "yPercent", "scale", "scaleX", "scaleY", "rotation", "rotationX", "rotationY", "rotate",
          "clipPath", "strokeDashoffset", "width", "height", "left", "top", "z", "skewX", "--p", "keyframes", "display", "textContent"}


def tweens(lines, base=0):
    out = []
    for li, ln in enumerate(lines):
        if ln.lstrip().startswith("{ const __m = tl;"): continue        # a nested, rescaled block: local times
        for m in CALL.finditer(ln):
            k = _close(ln, m.end())
            args = _split(ln[m.end():k - 1])
            if len(args) < 2 or not NUM.match(args[-1].strip()): continue
            start = float(args[-1])
            meth = m.group(1)
            v = _top(args[-2]) if len(args) >= 3 or meth == "set" else {}
            if meth == "set": v = _top(args[1]) if len(args) >= 3 else {}
            fv = _top(args[1]) if meth == "fromTo" and len(args) >= 4 else {}
            dur = 0.0
            kf1 = None
            if "keyframes" in v:                                  # a punch / shake: it hits on its first extreme
                m1 = re.search(r"duration:\s*(\d+(?:\.\d+)?)", v["keyframes"])
                kf1 = float(m1.group(1)) if m1 else None
            if meth != "set":
                d = v.get("duration")
                if d and NUM.match(d): dur = float(d)
                elif "keyframes" in v:
                    dur = sum(float(x) for x in re.findall(r"duration:\s*(\d+(?:\.\d+)?)", v["keyframes"]))
                else: dur = 0.5                                   # GSAP default
            ease = (v.get("ease") or "").strip("\"'") or ("none" if meth == "set" else "power1.out")
            st = v.get("stagger")
            each = amount = None; stfn = False
            if st:
                if NUM.match(st): each = float(st)
                elif st.startswith("{"):
                    sv = _top(st)
                    if sv.get("each") and NUM.match(sv["each"]): each = float(sv["each"])
                    if sv.get("amount") and NUM.match(sv["amount"]): amount = float(sv["amount"])
                else: stfn = True
            keys = set(v) | set(fv)
            target = args[0].strip()
            cval = None
            if not target[:1] in "\"'`" and ("onUpdate" in v or "v" in v):
                a0 = re.search(r"\{\s*v\s*:\s*(-?[\d.]+)", ln)
                b1 = v.get("v")
                dp = re.search(r"toFixed\((\d)\)|FractionDigits:\s*(\d)", ln)
                try: cval = (float(a0.group(1)) if a0 else 0.0, float(b1), int((dp.group(1) or dp.group(2)) if dp else 0))
                except (TypeError, ValueError): cval = None
            out.append({"li": base + li, "cval": cval, "kf1": kf1, "keys": keys, "meth": meth, "sel": target.strip("\"'`"), "start": start, "dur": dur, "ease": ease,
                        "each": each, "amount": amount, "stfn": stfn, "repeat": v.get("repeat"), "yoyo": "yoyo" in v,
                        "counter": not target[:1] in "\"'`" and ("onUpdate" in v or "v" in v),
                        "motion": bool(keys & MOTION), "fade": bool(keys & {"opacity", "autoAlpha", "filter"}) and not (keys & MOTION)})
    return out


def _ambient(tw):
    if tw["counter"]: return True
    if tw["repeat"] and tw["repeat"].strip() not in ("0", "1"): return True
    if tw["dur"] >= 1.6: return True
    if tw["ease"] in ("none", "linear", "sine.inOut", "power0") and tw["dur"] > 0.8: return True
    return False


def _affinity(kind, role, keys):
    """how much a tween looks like the motion this sound is for (a pop scales, a whoosh travels, a hit lands)."""
    if kind == "small" and role in ("pop", "drop", "dot", "chip", "title", "tick") and keys & {"scale", "scaleX", "scaleY", "keyframes"}: return 0.1
    if kind == "impact" and keys & {"scale", "y", "yPercent", "keyframes"}: return 0.05
    if kind == "whoosh" and keys & {"x", "xPercent", "y", "yPercent", "clipPath"}: return 0.05
    return 0.0


def count_sel(html, sel):
    """how many elements the selector's last simple part names in this html (0 = unknown)."""
    last = sel.split(",")[-1].strip().split()[-1] if sel.strip() else ""
    last = re.sub(r"\[.*?\]|:[\w-]+(\(.*?\))?", "", last)
    if not last: return 0
    if "." in last:
        cls = last.split(".")[-1]
        n = 0
        for m in re.finditer(r'class="([^"]*)"|class=([\w-]+)', html):
            names = (m.group(1) or m.group(2) or "").split()
            if cls in names: n += 1
        return n
    if re.match(r"^[a-z]+\d?$", last):
        return len(re.findall(rf"<{last}[\s>]", html))
    return 0


# ---------------------------------------------------------------- snapping events onto their motion
def snap(X, lo, hi, n_els=0, events=None):
    """pair every pending event (recorded while X.tws grew from lo to hi) with the tween it accompanies and move it
    to that tween's arrival; count-ups, typing and staggered pops become sequences."""
    lines = X.tws[lo:hi]
    tws = tweens(lines, lo)
    html = None
    if events is None:
        idx = [k for k, (t, u, v) in enumerate(X.audio) if isinstance(u, Snd) and not u.done and lo <= u.ci <= hi]
    else:
        idx = events
    if not idx: return
    new = {}
    for k in idx:
        t, u, vol = X.audio[k]
        u.done = True
        if not u.lib: continue
        kind = KIND.get(u.fam, "small")
        role = u.role
        if kind == "riser": continue          # a riser builds towards the next impact (schedule), not the tween it starts with
        # count-ups: ticks that follow the digits
        if role == "count" or (u.fam in ("type",) and role in ("count",)):
            cs = [tw for tw in tws if tw["counter"] and abs(tw["start"] - t) <= 0.6 and 0.3 <= tw["dur"] <= 6]
            if cs:
                c = min(cs, key=lambda tw: abs(tw["start"] - t))
                u.follows = X.tws[c["li"]]
                new[k] = _count_ticks(X, u, c, vol)
                continue
        if role == "type" or (u.fam == "type" and role not in ("count",)):
            if html is None: html = "".join(X.els[n_els:])
            seq = _type_keys(X, u, t, tws, html, vol)
            if seq:
                new[k] = seq
                continue
        best, bs = None, 9.0
        for tw in tws:
            if _ambient(tw): continue
            ds = tw["start"] - t
            if not (-0.30 <= ds <= 0.30): continue
            rel = tw["li"] - u.ci
            dist = (-rel - 1) if rel < 0 else rel
            sc = abs(ds) + 0.03 * min(dist, 10) + (0.06 if rel >= 0 else 0) + (0.15 if tw["fade"] else 0)
            if _ease_fn(tw["ease"])[1] == "inOut" and kind != "whoosh" and not tw["kf1"]: continue   # a glide, not a landing
            sc += 0.1 if tw["dur"] > 1.2 else 0
            sc -= _affinity(kind, role, tw["keys"])
            if sc < bs: best, bs = tw, sc
        if not best: continue
        imp = best["start"] + land_frac(best["ease"], kind) * best["dur"]
        if best["yoyo"]: imp = best["start"] + best["dur"]
        if best["kf1"]: imp = best["start"] + best["kf1"]
        cap = min(1.5, best["dur"] + 0.05) if abs(best["start"] - t) <= 0.03 else 0.7    # same start: surely its motion
        if not (-0.2 <= imp - t <= max(0.7, cap)): continue
        if kind == "small" and role in ("pop", "tick", "drop", "dot", "chip") and (best["each"] or best["amount"]) and not best["stfn"]:
            if html is None: html = "".join(X.els[n_els:])
            seq = _stagger_pops(X, u, best, html, vol, kind)
            if seq:
                new[k] = seq
                continue
        u.motion = f'{best["sel"][:40]} {best["ease"]} {best["dur"]:.2f}s@{best["start"]:.3f}'
        u.follows = X.tws[best["li"]]           # pacing._wrap moves the sound with this line, whatever it does to it
        new[k] = [(frame(imp, X.fps), u, vol)]
    for k in sorted(new, reverse=True):
        X.audio[k:k + 1] = new[k]


def frame(t, fps):
    return round(round(t * fps) / fps, 4)


def _clone(u, name=None, **kw):
    d = dict(u.__dict__)
    d.update(kw)
    d.setdefault("follows", u.__dict__.get("follows"))
    nm = name or u.name
    d["name"] = nm
    d["fam"] = family_of(nm) if name else u.fam
    return Snd(f"assets/sfx/{nm}.wav", **d)


def _seq_family(u):
    return SEQ_FAMILY.get(u.fam, "tick")


def _count_ticks(X, u, c, vol):
    """a count-up: ticks at equal steps of the shown value (so they follow the ease: dense, then slower), the last
    one on the settle, a touch louder."""
    fam = _seq_family(u)
    n = max(4, min(9, int(round(c["dur"] * 6))))
    times = []
    for j in range(1, n + 1):
        x = inv_progress(c["ease"], j / n)
        tt = c["start"] + x * c["dur"]
        if times and tt - times[-1] < 0.06: continue
        times.append(tt)
    settle = 0.995                    # the digits stop changing when the last shown step is reached, before the tween ends
    if c.get("cval"):
        a, b, dp = c["cval"]
        if abs(b - a) > 0: settle = max(0.9, 1 - 0.5 * 10 ** (-dp) / abs(b - a))
    end = c["start"] + inv_progress(c["ease"], settle) * c["dur"]
    times = [x for x in times if x < end - 0.04] + [end]
    out = []
    sid = f"c{u.ci}"
    for j, tt in enumerate(times):
        last = j == len(times) - 1
        out.append((frame(tt, X.fps), _clone(u, name=fam, seq=sid, accent=last, role="count", motion=f'count {c["ease"]} {c["dur"]:.2f}s@{c["start"]:.3f}', fam=fam), vol))
    return out


def _type_keys(X, u, t, tws, html, vol):
    """typing: one key per glyph that appears (a staggered display/opacity set, or one stepped reel per slot)."""
    fam = "key"
    near = [tw for tw in tws if abs(tw["start"] - t) <= 0.3]
    times = []
    st = [tw for tw in near if (tw["each"] or tw["amount"]) and tw["dur"] <= 0.08 and not tw["stfn"]]
    if st:
        tw = min(st, key=lambda w: abs(w["start"] - t))
        N = count_sel(html, tw["sel"])
        if N >= 2:
            each = tw["each"] if tw["each"] else tw["amount"] / max(N - 1, 1)
            times = [tw["start"] + j * each for j in range(min(N, 60))]
            u.follows = X.tws[tw["li"]]
    if not times:
        same = [tw for tw in near if abs(tw["start"] - t) <= 0.02 and tw["ease"].startswith("steps")]
        if len(same) >= 3: times = sorted(tw["start"] + tw["dur"] for tw in same)
    if not times: return None
    keep = []
    for tt in times:
        if keep and tt - keep[-1] < 0.045: continue
        keep.append(tt)
    sid = f"k{u.ci}"
    return [(frame(tt, X.fps), _clone(u, name=fam, seq=sid, role="type", motion=f"type {len(keep)} keys", fam=fam), vol) for tt in keep]


def _stagger_pops(X, u, tw, html, vol, kind):
    N = count_sel(html, tw["sel"])
    if N < 2 or N > 40: return None
    each = tw["each"] if tw["each"] else tw["amount"] / max(N - 1, 1)
    lf = land_frac(tw["ease"], kind) * tw["dur"]
    times = [tw["start"] + j * each + lf for j in range(N)]
    keep = []
    for tt in times:
        if keep and tt - keep[-1] < 0.09: continue
        keep.append(tt)
    if len(keep) > 6:                       # a row of chips pops chip by chip; a long title gets six, not one per glyph
        step = len(keep) / 6
        keep = [keep[int(j * step)] for j in range(6)]
    fam = _seq_family(u)
    sid = f"p{u.ci}"
    u.follows = X.tws[tw["li"]]
    return [(frame(tt, X.fps), _clone(u, name=fam, seq=sid, motion=f'{tw["sel"][:30]} x{N} {tw["ease"]}', fam=fam), vol) for tt in keep]


# ---------------------------------------------------------------- the mix
def level(meta):
    v = meta.get("sfx_level", "normal")
    if v is False: v = "off"
    if v is True or v is None: v = "normal"
    if str(v) not in PRESETS: raise SystemExit(f'meta.sfx_level 只能是 off / subtle / normal / punchy（现在是 {v!r}）')
    return PRESETS[str(v)]


def voice_ref(path):
    """(phone-weighted, plain) integrated loudness of the narration (LUFS); None when it cannot be measured."""
    if not path or not Path(path).exists(): return None
    vals = []
    for hp in ("highpass=f=150:p=2,", ""):
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", hp + "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True)
        m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
        if not m: return None
        vals.append(float(m[-1]))
    return tuple(vals)


def _size(u):
    if u.seq: return "T"
    kind = KIND.get(u.fam, "small")
    if kind == "impact":
        return "L" if (u.role in LARGE_ROLES or u.fam in ("slam", "boom")) else "M_impact"
    if kind in ("whoosh", "material", "riser"): return "M"
    return "S"


def _in(t, spans, pad=0.05):
    for a, b in spans:
        if a - pad <= t <= b + pad: return True
    return False


def _pick(u, beat_count, last):
    """the variant: seeded by beat index and the event's place in its beat, never the file just played."""
    vs = variants(u.fam) if u.fam in KIND else []
    if not vs: return u.name
    if u.seq:
        key = f"{u.fam}|{u.seq}|{beat_count}"
    else:
        key = f"{u.fam}|{u.beat}|{beat_count}"
    i = zlib.crc32(key.encode()) % len(vs)
    for _ in range(len(vs)):
        if vs[i] not in last: break
        i = (i + 1) % len(vs)
    return vs[i]


def _avoid(u, fam_last):
    """the files to avoid for this event: the one just played, and this family's last pick (unless it is a sequence)."""
    out = list(fam_last.get("_", []))
    if not u.seq and fam_last.get(u.fam): out.append(fam_last[u.fam])
    return out


def _gain(ref, ref_full, tgt, info):
    """dB for this file: its phone-speaker loudness on target; on full-range playback no more than 2 LU over the
    target (a bass-heavy hit must not cover words on headphones); never past the peak cap."""
    g = ref + tgt - info["loud"]
    if info.get("loud_full") is not None: g = min(g, ref_full + tgt + 2.0 - info["loud_full"])
    return min(g, PEAK_CAP_DB - info["sample_peak_db"], 12.0)


def schedule(X, D, voice_path, speech):
    """[(start, url, vol, media_start)] for every effect sound + the plan rows for timeline.json + the voice loudness."""
    meta = X.v.get("meta", {})
    off = level(meta)
    if off is None: return [], [], None
    # anything not yet paired with its motion (layers, nav, device chrome …): pair it in its own neighbourhood
    pend = [k for k, (t, u, v) in enumerate(X.audio) if isinstance(u, Snd) and not u.done]
    for k in sorted(pend, reverse=True):
        u = X.audio[k][1]
        snap(X, max(0, u.ci - 80), min(len(X.tws), u.ci + 20), 0, [k])
    man = manifest()
    muted = getattr(X, "sfx_muted", set())
    quiet = getattr(X, "sfx_quiet", set())
    refs = voice_ref(voice_path)
    has_voice = refs is not None
    ref, ref_full = refs if has_voice else (-18.0, -16.0)
    evs = sorted(X.audio, key=lambda e: e[0])
    # risers end on the next impact
    imps = [t for t, u, v in evs if isinstance(u, Snd) and KIND.get(u.fam) == "impact"]
    rows, out = [], []
    fam_last = {}
    per_beat = {}
    placed = []
    for t, u, vol in evs:
        if not isinstance(u, Snd):           # a style's own synthesised sound (e.g. pixel chips): as the style placed it
            if t < D - 0.05: out.append((max(0.0, t), str(u), vol, 0.0)); rows.append({"file": Path(str(u)).name, "impact": round(t, 3), "start": round(max(0.0, t), 3), "own": True})
            continue
        if u.beat in muted: continue
        if u.beat in quiet and u.seq: continue          # a quiet beat keeps its single sounds, softer, and no tick runs
        if not u.lib:
            continue
        kind = KIND.get(u.fam, "small")
        bc = per_beat.get((u.beat, u.fam), 0); per_beat[(u.beat, u.fam)] = bc + 1
        if kind == "riser" and not u.exact:
            nxt = [x for x in imps if t + 0.3 < x <= t + 2.4]
            name = None
            if nxt:
                gap = nxt[0] - t
                fit = [k for k in variants("riser") if man[k]["peak"] <= gap + 0.15]
                name = max(fit, key=lambda k: man[k]["peak"]) if fit else min(variants("riser"), key=lambda k: man[k]["peak"])
                imp = nxt[0]
                u.motion = f"riser into {imp:.3f}"
            else:
                name = _pick(u, bc, _avoid(u, fam_last))
                imp = t + man[name]["peak"]          # nothing to land on: it starts where it was asked to
        else:
            name = _pick(u, bc, _avoid(u, fam_last))
            imp = t
            if kind == "whoosh" and not u.exact and u.motion is None:
                imp = t + min(man[name]["peak"], 0.25)       # unpaired: loudest while the thing moves, not 0.5 s later
        info = man.get(name)
        if not info: continue
        size = _size(u)
        sp = _in(imp, speech) if has_voice else False
        tgt = TARGET[size][0 if sp else 1] + off + u.hint + (3.0 if u.accent else 0.0) - (4.0 if u.beat in quiet else 0.0)
        g_db = _gain(ref, ref_full, tgt, info)
        start = imp - info["peak"]
        placed.append({"imp": imp, "start": start, "name": name, "vol": round(10 ** (g_db / 20), 4), "size": size, "u": u,
                       "speech": sp, "tgt": tgt})
        fam_last["_"] = [name]
        if not u.seq: fam_last[u.fam] = name
    # two sounds on the same instant: keep the bigger one (a whoosh may still lead into an impact)
    placed.sort(key=lambda p: p["imp"])
    keep = []
    for p in placed:
        if KIND.get(p["u"].fam) == "whoosh" and any(KIND.get(q["u"].fam) == "whoosh" and abs(q["imp"] - p["imp"]) < 0.2 for q in keep[-4:]):
            continue                                       # one whoosh per cut (a scene's exit and the next entrance)
        clash = None
        for q in keep[-4:]:
            if abs(q["imp"] - p["imp"]) < 0.045:
                ka, kb = KIND.get(q["u"].fam), KIND.get(p["u"].fam)
                if {ka, kb} & {"whoosh", "riser"} and ka != kb: continue
                clash = q
        if clash:
            if RANK[p["size"]] > RANK[clash["size"]]: keep[keep.index(clash)] = p
            continue
        keep.append(p)
    # no file three times running after the clash pass either
    for i in range(2, len(keep)):
        if keep[i]["name"] == keep[i - 1]["name"] == keep[i - 2]["name"]:
            vs = variants(keep[i]["u"].fam)
            if len(vs) > 1:
                nm = vs[(vs.index(keep[i]["name"]) + 1) % len(vs)]
                info = man[nm]
                keep[i]["start"] = keep[i]["imp"] - info["peak"]
                g_db = _gain(ref, ref_full, keep[i]["tgt"], info)
                keep[i]["vol"] = round(10 ** (g_db / 20), 4); keep[i]["name"] = nm
    for p in keep:
        if p["imp"] >= D - 0.05: continue
        st = max(0.0, p["start"])
        ms = st - p["start"]                     # at the very start of the film: play the file from inside, peak still on time
        url = X.asset(SFX / f'{p["name"]}.wav', "sfx")
        out.append((st, url, p["vol"], round(ms, 3)))
        u = p["u"]
        rows.append({"file": p["name"], "role": u.role, "size": p["size"], "impact": round(p["imp"], 3), "start": round(st, 3),
                     "peak": man[p["name"]]["peak"], "skip": round(ms, 3), "vol": p["vol"], "speech": p["speech"], "target_lu": round(p["tgt"], 1),
                     "beat": u.beat, "motion": u.motion, "moved": round(p["imp"] - u.t0, 3), "seq": u.seq,
                     "asked": u.asked, "t0": round(u.t0, 3), "exact": u.exact})
    rows.sort(key=lambda r: r["start"])
    out.sort(key=lambda e: e[0])
    return out, rows, (round(ref, 2) if has_voice else None)
