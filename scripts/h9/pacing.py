"""pacing — time edits around the narration, and beat-level life.

  meta.gaps    = [{"after": "@词$" | seconds, "dur": 1.5}, ...]
                 silence is inserted into the voice in the pause after that point; every later word (so every "@cue")
                 moves later by dur. For breathers, interludes, a suspense hold before a reveal.
  meta.lead    = 1.8      the narration starts 1.8 s in, so a silent cold open plays first; all cues move with it.
  meta.duck    = true | 10 (dB)   the music bed dips while someone speaks: a sidechain-style envelope built from the
                 word timestamps (0.15 s attack, 0.4 s release), rendered into a ducked copy of the music file.
  elastic      every fx beat stays alive for its whole length. Long beats get a slow camera creep plus a little drift
                 once the entrance has landed; short beats whose entrance would not finish play the whole entrance
                 faster (nested timeline with timeScale). "hold": "static" on a beat opts out; meta.elastic = false
                 turns it off for the film; a style can opt its own scenes in with STYLE["elastic"] = True.
"""
import re, subprocess
from pathlib import Path


def _shift(X, at, by):
    X.chars = [(c, s + by, e + by) if s >= at - 1e-6 else (c, s, e) for c, s, e in X.chars]
    X._words = [dict(w, s=w["s"] + by, e=w["e"] + by) if w["s"] >= at - 1e-6 else w for w in X._words]


def time_edits(X, meta, voice_url):
    """apply meta.gaps then meta.lead. Returns (voice_url, lead, total_gap_seconds)."""
    gaps, lead = meta.get("gaps") or [], float(meta.get("lead") or 0)
    added = 0.0
    if gaps and voice_url and X.chars:
        pts = []
        for g in gaps:
            a, dur = g.get("after"), float(g.get("dur", 1.0))
            tt = float(X.T(a)) if isinstance(a, str) else float(a)
            nxt = next((s for _, s, e in X.chars if s > tt + 1e-3), None)
            pts.append(((tt + nxt) / 2 if nxt is not None and nxt - tt < 1.5 else tt, dur))
        pts.sort()
        src = X.out / voice_url
        dst = src.with_name(src.stem + "_gaps.wav")
        n = len(pts)
        f = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=%d%s" % (n + 1, "".join(f"[a{k}]" for k in range(n + 1)))]
        cuts = [0.0] + [p for p, _ in pts]
        order = []
        for k in range(n + 1):
            end = f":end={cuts[k + 1]:.3f}" if k < n else ""
            f.append(f"[a{k}]atrim=start={cuts[k]:.3f}{end},asetpts=PTS-STARTPTS[s{k}]")
            order.append(f"[s{k}]")
            if k < n:
                f.append(f"anullsrc=r=48000:cl=stereo,atrim=duration={pts[k][1]:.3f}[z{k}]")
                order.append(f"[z{k}]")
        f.append("".join(order) + f"concat=n={len(order)}:v=0:a=1[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex", ";".join(f), "-map", "[o]", str(dst)], check=True)
        voice_url = str(Path(voice_url).with_name(dst.name))
        for p, dur in reversed(pts):        # later points first, so earlier points keep their original times
            _shift(X, p, dur)
        added = sum(d for _, d in pts)
    if lead and X.chars:
        _shift(X, -1e9, lead)
    return voice_url, lead, added


def speech_spans(words, join=0.35):
    sp = []
    for w in words:
        if w["e"] - w["s"] <= 1e-6: continue          # punctuation tokens
        if sp and w["s"] - sp[-1][1] < join: sp[-1][1] = max(sp[-1][1], w["e"])
        else: sp.append([w["s"], w["e"]])
    return sp


def duck(X, meta, music_url):
    """a ducked copy of the music bed; returns its url (unchanged when meta.duck is off or there are no words)."""
    db = meta.get("duck")
    if not db or not music_url or not X._words: return music_url
    db = 10.0 if db is True else float(db)
    low = 10 ** (-db / 20)
    sp = speech_spans(X._words)
    if not sp: return music_url
    terms = "+".join(f"min(1,max(0,(t-{a - 0.15:.3f})/0.15))*min(1,max(0,({b + 0.4:.3f}-t)/0.4))" for a, b in sp)
    src = X.out / music_url
    dst = src.with_name(src.stem + "_duck.wav")
    script = X.out / "assets" / "audio" / ".duck_filter.txt"
    script.write_text(f"[0:a]volume='1-{1 - low:.4f}*min(1,{terms})':eval=frame[o]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex_script", str(script), "-map", "[o]", str(dst)], check=True)
    script.unlink()
    return str(Path(music_url).with_name(dst.name))


# ---------------------------------------------------------------- elastic beats
_T = re.compile(r",\s*(-?\d+(?:\.\d+)?)\);")
_DUR = re.compile(r"duration:\s*(\d+(?:\.\d+)?)")
_ST = re.compile(r"stagger:\s*(?:\{[^}]*?(?:each|amount):\s*)?(\d+(?:\.\d+)?)")


def entrance_end(lines, t, d):
    """when the beat's own animation has landed (estimated from the tween lines it emitted)."""
    E = t
    for ln in lines:
        ts = _T.findall(ln)
        if not ts: continue
        T = float(ts[-1])
        if T > t + 0.6 * d: continue                   # a late action (exit, second hit) is not the entrance
        dur = max([float(x) for x in _DUR.findall(ln)] or [0.0])
        st = _ST.search(ln)
        E = max(E, T + dur + (min(0.6, float(st.group(1)) * 8) if st else 0.0))
    return E


def elastic(X, b, t, d, cid, n_tw, n_audio, n_els, i):
    meta = X.v.get("meta", {})
    if meta.get("elastic") is False or b.get("hold") == "static": return
    if b.get("scene") != "fx" and not X.S.get("elastic"): return
    lines = X.tws[n_tw:]
    if not lines: return
    E = entrance_end(lines, t, d)
    ent = E - t
    if ent > 0.85 * d and d < 2.0:                    # short beat: the whole entrance plays faster
        s = min(3.0, ent / (0.8 * d))
        if s < 1.05: return
        P = t * (1 - 1 / s)
        X.tws[n_tw:] = ["{ const __m = tl; { const tl = gsap[\"timeline\"]();\n" + "\n".join(lines)
                        + f"\ntl.timeScale({s:.4f}); __m.add(tl, {P:.4f}); }} }}"]
        X.audio[n_audio:] = [(t + (ta - t) / s, u, v) for ta, u, v in X.audio[n_audio:]]
        return
    if d < 1.8: return
    if re.search(rf'["\']#{re.escape(cid)}["\']\s*,', "\n".join(lines)): return     # the effect moves its own root
    if any(f'id="{cid}_' in el for el in X.els[n_els:]): return                       # root-level media layers: video is alive already
    h0 = min(max(E, t + 0.5), t + d - 0.8)
    dur = t + d - h0
    if dur < 0.6: return
    px = (1 if i % 2 == 0 else -1) * 0.6 * min(X.W, X.H) / 100
    X.tw(f'tl.fromTo("#{cid}", {{scale:1, x:0}}, {{scale:1.022, x:{px:.1f}, duration:{dur:.2f}, ease:"sine.inOut", immediateRender:false}}, {h0:.3f});')
