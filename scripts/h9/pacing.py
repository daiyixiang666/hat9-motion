"""pacing — time edits around the narration, and beat-level life.

  meta.gaps    = [{"after": "@词$" | seconds, "dur": 1.5}, ...]
                 silence is inserted into the voice in the pause after that point; every later word (so every "@cue")
                 moves later by dur. For breathers, interludes, a suspense hold before a reveal.
  meta.lead    = 1.8      the narration starts 1.8 s in, so a silent cold open plays first; all cues move with it.
  meta.duck    = true | 10 (dB)   the music bed dips while someone speaks: a sidechain-style envelope built from the
                 word timestamps (0.15 s attack, 0.4 s release), rendered into a ducked copy of the music file.
  per beat "music": "up" | dB      the bed comes up for that beat (voiceless runs; quick-cut montage beats by default),
                 up over 0.25 s into its start, back down over its last 0.3 s, on top of the duck envelope (h9/beatsync.py builds the windows).
  breath       = true      in the narrator's breaths and short pauses (0.25–1.4 s gaps between words) the page takes a
                 small breath: the scene's stage eases in ~1% and back, so a pause never reads as a frozen frame.
  rate_adapt   = true      per beat, the speaking rate sets the tempo: fast talk (> 6 syllables/s, a CJK glyph = 1, a Latin
                 letter ≈ 1/3) plays the entrance up to 1.6× faster; slow talk (< 3.5 syllables/s) gets a wider camera creep and a slow ambient light.
  per beat "sfx": [{"at": "@词" | seconds into the beat, "name": "hit" | style role, "vol": 0.6, "hit": "flash" | "dark" |
                 "shake" | "punch"}]   sound-led moments: the sound and a visual hit land on the same frame.
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
    """a ducked copy of the music bed; returns its url (unchanged when meta.duck is off or there are no words, and no
    beat lifts the music). Beats with "music": "up" (X.music_up = [(t0, t1, dB)]) lift the bed there: the file keeps
    the lifted level at full scale and the rest lower, and X.music_gain tells build.py to play the clip that much louder."""
    db = meta.get("duck")
    ups = getattr(X, "music_up", None) or []
    if not music_url or ((not db or not X._words) and not ups): return music_url
    sp = speech_spans(X._words) if db and X._words else []
    if not sp and not ups: return music_url
    db = 10.0 if db is True else float(db or 0)
    low = 10 ** (-db / 20)
    terms = "+".join(f"min(1,max(0,(t-{a - 0.15:.3f})/0.15))*min(1,max(0,({b + 0.4:.3f}-t)/0.4))" for a, b in sp)
    expr = f"1-{1 - low:.4f}*min(1,{terms})" if sp else "1"
    if ups:
        top = max(u for _, _, u in ups)
        base = 10 ** (-top / 20)            # the normal bed, relative to the loudest lift
        lift = "+".join(f"{10 ** ((u - top) / 20) - base:.4f}*min(1,max(0,(t-{a - 0.25:.3f})/0.25))*min(1,max(0,({b:.3f}-t)/0.3))" for a, b, u in ups)
        expr = f"({expr})*min(1,{base:.4f}+{lift})"
        X.music_gain = round(10 ** (top / 20), 4)
    src = X.out / music_url
    dst = src.with_name(src.stem + "_duck.wav")
    script = X.out / "assets" / "audio" / ".duck_filter.txt"
    script.write_text(f"[0:a]volume='{expr}':eval=frame[o]")
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


def _speech_in(X, t0, t1):
    """(syllables spoken, seconds of speech) inside [t0, t1); a CJK glyph = 1, a Latin letter or digit ≈ 1/3."""
    n, secs = 0, 0.0
    for c, s, e in X.chars:
        if t0 <= s < t1 and c.strip() and c not in "，。、！？；：,.!?;:":
            n += 1 if ord(c[0]) >= 0x2E80 else 1 / 3; secs += max(0.0, min(e, t1) - s)
    return n, secs


def _wrap(X, n_tw, n_audio, t, s):
    """play the beat's tween lines s× faster (nested timeline); SFX move with them."""
    lines = X.tws[n_tw:]
    P = t * (1 - 1 / s)
    X.tws[n_tw:] = ["{ const __m = tl; { const tl = gsap[\"timeline\"]();\n" + "\n".join(lines)
                    + f"\ntl.timeScale({s:.4f}); __m.add(tl, {P:.4f}); }} }}"]
    X.audio[n_audio:] = [(t + (ta - t) / s, u, v) for ta, u, v in X.audio[n_audio:]]


def rate_adapt(X, b, t, d, cid, n_tw, n_audio, n_els):
    """meta.rate_adapt: the speaking rate inside this beat sets its tempo (see module doc)."""
    if not X.v.get("meta", {}).get("rate_adapt") or b.get("hold") == "static" or not X.chars: return
    n, secs = _speech_in(X, t, t + d)
    if n < 4 or secs < 0.6: return
    cps = n / secs
    if cps > 6.0 and X.tws[n_tw:]:
        _wrap(X, n_tw, n_audio, t, min(1.6, cps / 5.0))
        b["_rate"] = "fast"
    elif cps < 3.5 and d >= 2.0:
        b["_rate"] = "slow"
        X.css("rate-amb", ".rt-amb { pointer-events:none; background:radial-gradient(ellipse 60% 50% at 30% 40%, rgba(255,240,210,.16), rgba(255,240,210,0) 70%); mix-blend-mode:soft-light; }")
        X.clip(f"{cid}amb", t, d, "", "rt-amb", 3, track=24)
        X.tw(f'tl.fromTo("#{cid}amb", {{opacity:0, xPercent:-6}}, {{opacity:1, xPercent:6, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


HITS = {
    "flash": ("#fff", 0.0, 0.85, 0.12), "dark": ("#000", 0.0, 0.9, 0.14),
}


def sound_moments(X, b, t, d, cid):
    """per-beat "sfx": sounds bound to visual hits on the same frame."""
    for k, m in enumerate(b.get("sfx") or []):
        at = m.get("at", 0)
        ta = float(X.T(at, t)) if isinstance(at, str) else t + float(at)
        if not (t - 0.01 <= ta <= t + d): continue
        sn = getattr(X, "snapper", None)
        if sn and m.get("snap") is not False:           # onto the music's beat, within tolerance; "@词" never well before its word
            ta = sn.snap(ta, at, f"sfx {X.beat.get('i', 0)}.{k} ({m.get('name', 'hit')})", t - 0.01, t + d)
        X.sfx(ta, m.get("name", "hit"), m.get("vol"))
        hit = m.get("hit")
        if sn: X.__dict__.setdefault("sfx_hits", []).append({"t": round(ta, 3), "name": m.get("name", "hit"), "hit": hit})
        if hit in HITS:
            col, a0, a1, dur = HITS[hit]
            hid = f"{cid}hit{k}"
            X.clip(hid, ta, dur + 0.02, "", "ov-hit", 44, track=25, sty=f"background:{col};opacity:0;pointer-events:none")
            X.tw(f'tl.fromTo("#{hid}", {{opacity:{a1}}}, {{opacity:0, duration:{dur:.2f}, ease:"power2.out", immediateRender:false}}, {ta:.3f});')
        elif hit == "shake":
            X.tw(f'tl.to("#{cid}", {{keyframes:[{{y:-14, duration:0.04}}, {{y:11, duration:0.04}}, {{y:-6, duration:0.04}}, {{y:0, duration:0.06}}]}}, {ta:.3f});')
        elif hit == "punch":
            X.tw(f'tl.to("#{cid} > .stage", {{keyframes:[{{scale:1.045, duration:0.06, ease:"power2.out"}}, {{scale:1, duration:0.22, ease:"power3.out"}}]}}, {ta:.3f});')


def breaths(X, spans, D):
    """meta.breath: a small inhale on the active scene in each short pause of the narration."""
    if not X.v.get("meta", {}).get("breath") or not X._words: return
    sp = speech_spans(X._words, join=0.12)
    for (a0, a1), (b0, b1) in zip(sp, sp[1:]):
        g0, g1 = a1, b0
        gap = g1 - g0
        if not (0.25 <= gap <= 1.4): continue
        hit = next(((cid, t, d) for cid, t, d, hold in spans if t + 0.4 <= g0 and g1 <= t + d - 0.05 and not hold), None)
        if not hit: continue
        cid = hit[0]
        half = max(0.12, gap / 2)
        X.tw(f'tl.to("#{cid} > .stage", {{scale:1.011, y:-3, duration:{half:.3f}, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, {g0:.3f});')


def elastic(X, b, t, d, cid, n_tw, n_audio, n_els, i):
    meta = X.v.get("meta", {})
    if meta.get("elastic") is False or b.get("hold") == "static": return
    if b.get("scene") != "fx" and not X.S.get("elastic"): return
    lines = X.tws[n_tw:]
    if not lines: return
    wrapped = b.get("_rate") == "fast"
    E = entrance_end(lines, t, d)
    ent = E - t
    if wrapped and d < 2.0: return
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
    slow = b.get("_rate") == "slow"
    px = (1 if i % 2 == 0 else -1) * (1.1 if slow else 0.6) * min(X.W, X.H) / 100
    X.tw(f'tl.fromTo("#{cid}", {{scale:1, x:0}}, {{scale:{1.045 if slow else 1.022}, x:{px:.1f}, duration:{dur:.2f}, ease:"sine.inOut", immediateRender:false}}, {h0:.3f});')
