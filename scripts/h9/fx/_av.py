"""shared helpers for the video & audio effects (pip, freeze_frame, speed_ramp, footage, audio_quote, podcast,
talking_head, host_point). Files starting with _ are not effects; load by path like _cite.py.

when(): a moment inside the beat ("@词", seconds from the beat start, or a fraction) ·
still(): one frame of a clip as a jpg in the build · retime(): a speed-ramped copy of a clip (ffmpeg, cached) ·
peaks(): waveform bars of an audio file · karaoke(): the narration characters inside a window, as lines ·
audio(): a timed <audio> at root level (HyperFrames only seeks timed media) ·
subs_band(): where a clip has burned-in subtitles ("bottom" / "top" / None, sampled from frames) ·
avoid_caps(): move our captions out of that band for the beat · host_src(): the talking host's video ·
cover_map(): a point/box given in % of a video's own frame → px on screen (object-fit: cover) ·
retime_words(): shift a words.json after cutting ranges out of the recording (used by scripts/audio_tools.py).
"""
import hashlib, json, re, subprocess
from pathlib import Path
from h9 import fit
from h9.core import esc

PUN = "，,。.!！?？、；;：:"


def _h(*xs): return hashlib.sha1("|".join(map(str, xs)).encode()).hexdigest()[:10]


def snap(X, x): return round(float(x) * X.fps) / X.fps


def when(X, p, key, t, d, frac):
    """p[key] as "@词" / seconds into the beat (p[key+'_rel'] or a bare number below d) / else t + d·frac; inside the beat."""
    v = p.get(key)
    if p.get(key + "_rel") is not None: x = t + float(p[key + "_rel"])
    elif isinstance(v, str) and v.startswith("@"): x = float(X.T(v, t))
    elif isinstance(v, (int, float)): x = t + float(v)
    else: x = t + d * frac
    return snap(X, min(max(x, t + 0.05), t + d - 0.05))


def src_abs(X, src): return fit._abs(X, src)


def scope(X, sel, t, d):
    """an untimed fit.media wrapper stays in the DOM all film long; one with a painted style (a card's shadow) must
    be hidden outside its beat or it shows through every transparent beat."""
    X.css(f"av-scope-{sel}", f"{sel} {{ visibility:hidden; }}")
    X.tw(f'tl.set("{sel}", {{visibility:"visible"}}, {t:.3f}); tl.set("{sel}", {{visibility:"hidden"}}, {t + d:.3f});')


def stage_bg(X, cid, t, d, p):
    """the theme's painted stage under the video layers (z 1), for a transparent effect clip whose picture does not
    fill the frame (card mode) — otherwise the root background shows and dark header text can vanish on it."""
    from h9.aefx import _theme_style
    sty = _theme_style(p, paint=True) or "background:var(--bg)"
    X.clip(f"{cid}bg", t, d, "", "fx-stage-bg", 1, track=23, sty=sty + ";position:absolute;inset:0")


def still(X, src, at):
    """the frame of `src` at `at` seconds, written into the build; returns its project url."""
    a = src_abs(X, src)
    out = X.out / "assets" / "img"; out.mkdir(parents=True, exist_ok=True)
    name = f"still_{_h(a, round(float(at), 3), a.stat().st_mtime if a.exists() else 0)}.jpg"
    if not (out / name).exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, float(at)):.3f}", "-i", str(a), "-frames:v", "1", "-q:v", "2", str(out / name)], check=True)
    return f"assets/img/{name}"


def retime(X, src, segs, smooth=False):
    """segs = [(a, b, speed), …] in source seconds → (abs path of a cached clip, its duration, [(out_t0, out_t1, speed)])."""
    a = src_abs(X, src)
    dur = fit.duration(a) or 0
    clean = []
    for s in segs:
        x0, x1, k = float(s[0]), float(s[1]), float(s[2] if len(s) > 2 else 1)
        x0, x1 = max(0.0, x0), min(dur, x1) if dur else x1
        if x1 - x0 > 0.04 and k > 0: clean.append((x0, x1, min(max(k, 0.05), 16)))
    if not clean: clean = [(0.0, dur or 1.0, 1.0)]
    out = Path(X.out).resolve() / "assets" / "video"; out.mkdir(parents=True, exist_ok=True)     # absolute: --out may be relative
    name = f"ramp_{_h(a, clean, smooth, a.stat().st_mtime if a.exists() else 0)}.mp4"
    parts, fc, o = [], [], 0.0
    for i, (x0, x1, k) in enumerate(clean):
        f = f"[0:v]trim=start={x0:.3f}:end={x1:.3f},setpts=(PTS-STARTPTS)/{k:.4f}"
        if smooth and k < 1: f += ",minterpolate=fps=30:mi_mode=blend"
        fc.append(f + ",fps=30[v%d]" % i)
        parts.append((o, o + (x1 - x0) / k, k)); o += (x1 - x0) / k
    fc.append("".join(f"[v{i}]" for i in range(len(clean))) + f"concat=n={len(clean)}:v=1:a=0[o]")
    if not (out / name).exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-filter_complex", ";".join(fc), "-map", "[o]", "-an",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(out / name)], check=True)
    return out / name, fit.duration(out / name) or o, parts


def peaks(X, src, a=0.0, b=None, n=96):
    """n bar heights in 0..1 for src between a and b seconds (RMS per bar, square-root shaped)."""
    import numpy as np
    s = src_abs(X, src)
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{max(0.0, float(a)):.3f}"] + (["-t", f"{float(b) - float(a):.3f}"] if b else []) + \
          ["-i", str(s), "-ac", "1", "-ar", "8000", "-f", "f32le", "-"]
    try: raw = subprocess.check_output(cmd)
    except subprocess.CalledProcessError: return [0.2] * n
    y = np.frombuffer(raw, dtype=np.float32)
    if not len(y): return [0.2] * n
    k = max(1, len(y) // n)
    v = np.array([float(np.sqrt(np.mean(y[i * k:(i + 1) * k] ** 2))) if i * k < len(y) else 0.0 for i in range(n)])
    m = float(v.max()) or 1.0
    return [round(float(x), 3) for x in np.sqrt(v / m)]


def load_chars(X, words):
    """words.json (relative to the example, or absolute) → [(char, s, e)] like core.load_words, punctuation kept with s=e."""
    pth = src_abs(X, words)
    data = json.loads(Path(pth).read_text())
    ws = []
    for x in data: ws += x["words"] if isinstance(x, dict) and "words" in x else [x]
    out = []
    for w in ws:
        tok = str(w.get("w", w.get("t", ""))).strip(); k = max(len(tok), 1)
        for j, ch in enumerate(tok):
            out.append((ch, w["s"] + (w["e"] - w["s"]) * j / k, w["s"] + (w["e"] - w["s"]) * (j + 1) / k))
    return out


def karaoke(X, words, a, b, maxlen=14):
    """characters spoken in [a, b) as display lines: [(line_text, [(char, s_rel, e_rel)…])], broken at punctuation,
    and at maxlen only between words (jieba when installed) — 苏伊士 never splits as 苏 | 伊士."""
    chars = [c for c in load_chars(X, words) if a - 0.02 <= c[1] < b]
    starts, pos = set(), 0
    for tk in fit.tokens("".join(c[0] for c in chars if c[0] not in PUN)):
        starts.add(pos); pos += len(tk)
    lines, cur, k = [], [], 0          # cur items: (char, s, e, starts_a_word, is_punct)
    forced = set()                     # lines that ended because they were full (an orphan after them may rejoin)

    def close():
        if not cur: return
        if len(cur) <= 2 and lines and len(lines) - 1 in forced and len(lines[-1]) + len(cur) <= maxlen + 3:
            lines[-1].extend(cur)      # no 「了」 alone on a line
        else: lines.append(list(cur))
        cur.clear()
    for ch, s, e in chars:
        if ch in PUN:
            if ch in "。！？!?" or len(cur) >= 6: close()
            elif cur: cur.append((ch, s - a, e - a, False, True))
            continue
        if len(cur) >= maxlen:         # full: break after the last comma, else before the last word start
            cut = len(cur)
            for c in range(len(cur), max(3, maxlen // 2) - 1, -1):
                if (k in starts if c == len(cur) else cur[c][3]) or cur[c - 1][4]: cut = c; break
            forced.add(len(lines)); lines.append(cur[:cut]); del cur[:cut]
        cur.append((ch, s - a, e - a, k in starts, False)); k += 1
    close()
    return [("".join(c[0] for c in ln), [c[:3] for ln_c in [ln] for c in ln_c]) for ln in lines]


def audio(X, cid, src, t, d, start=0.0, vol=1.0):
    """a timed <audio> as a root sibling of the effect clip."""
    url = X.asset(src, "audio")
    fit._TRACK[0] += 1
    X.els.append(f'<audio id="{cid}_au" class="clip" src="{url}" data-start="{t:.3f}" data-duration="{d:.3f}" '
                 f'data-track-index="{fit._TRACK[0]}" data-media-start="{max(0.0, float(start)):.3f}" data-volume="{vol}"></audio>')


def subs_band(X, src, start=0.0, d=None, n=6):
    """sample n frames; where most frames carry dense high-contrast glyph edges in the bottom (or top) strip, at least as
    dense as in the middle of the picture, take it as burned-in subtitles. Returns "bottom" | "top" | None.
    (Analysed at 640×360 — 360×640 for a portrait source, whose subtitles sit higher, above the platform buttons — so
    small caption pills survive; any persistent text strip counts, which is what we want.)"""
    import numpy as np
    a = src_abs(X, src)
    dur = fit.duration(a) or 0
    if not dur: return None
    sz = fit.size(a) or (16, 9)
    pw, ph = (360, 640) if sz[1] > sz[0] else (640, 360)
    rows = lambda y0, y1: slice(int(ph * y0), int(ph * y1))
    sb, sm, st = (rows(.58, .88), rows(.22, .52), rows(.03, .18)) if ph > pw else (rows(.75, .98), rows(.30, .70), rows(.02, .22))
    span = max(0.1, min(dur - start, d or dur))
    hits = {"bottom": 0, "top": 0}; got = 0
    for i in range(n):
        tt = start + span * (i + 0.5) / n
        try:
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{tt:.2f}", "-i", str(a), "-frames:v", "1",
                                           "-vf", f"scale={pw}:{ph},format=gray", "-f", "rawvideo", "-"])
        except subprocess.CalledProcessError:
            continue
        if len(raw) < pw * ph: continue
        got += 1
        g = np.frombuffer(raw[:pw * ph], dtype=np.uint8).reshape(ph, pw).astype(np.float32)
        gx = np.abs(np.diff(g, axis=1))
        ed = (gx > 70) & ((g[:, 1:] > 170) | (g[:, :-1] > 170))
        row = ed.mean(axis=1)
        top6 = lambda r: float(np.sort(r)[-6:].mean())
        b, m, t_ = top6(row[sb]), top6(row[sm]), top6(row[st])
        if b > 0.02 and b >= 0.7 * m: hits["bottom"] += 1
        if t_ > 0.02 and t_ >= 0.8 * m and t_ > 1.3 * b: hits["top"] += 1
    if not got: return None
    if hits["bottom"] >= max(2, 0.5 * got): return "bottom"          # subtitles live at the bottom far more often
    if hits["top"] >= 0.8 * got and hits["bottom"] == 0: return "top"   # titles and page headers also sit up there
    return None


def band_box(src_portrait, band):
    """(top, height) of the subtitle strip as fractions of the source frame."""
    if band == "top": return 0.03, 0.18
    return (0.62, 0.20) if src_portrait else (0.78, 0.18)


def avoid_caps(X, cid, t, d, band):
    """for this beat only: the effect's own caption pill and the narration captions leave `band`."""
    if band not in ("bottom", "top"): return
    if band == "bottom":
        top = 272 if X.portrait else 122          # under the page header (9:16 header ends at 250 px)
        X.css(f"av-cap-{cid}", f"#root #{cid}c.ctx .cap {{ bottom:auto; top:{top}px; }}")     # beats #root.v .ctx .cap
        cb, pt = (f"{X.H - 330}px", "14%") if X.portrait else (f"{X.H - 190}px", "12%")
    else:
        X.css(f"av-cap-{cid}", f"#root #{cid}c.ctx .cap {{ bottom:{430 if X.portrait else 66}px; top:auto; }}")
        cb, pt = ("430px", "66%") if X.portrait else ("66px", "71%")
    X.tw(f'(()=>{{const r=document.getElementById("root"); const cs=getComputedStyle(r); const cb=cs.getPropertyValue("--cap-bottom").trim()||"56px", pt=cs.getPropertyValue("--punch-top").trim()||"71%";'
         f' tl.set(r, {{"--cap-bottom":"{cb}", "--punch-top":"{pt}"}}, {t:.3f}); tl.set(r, {{"--cap-bottom":cb, "--punch-top":pt}}, {t + d:.3f});}})();')


def host_src(X, p):
    """the talking host clip: p.host, else meta.host_video / meta.mascot; None when there is none."""
    h = p.get("host")
    if h is False: return None
    meta = X.v.get("meta", {})
    return h or meta.get("host_video") or meta.get("mascot")


def cover_map(X, src, box, frame=None, focus=(50, 50)):
    """box (x%, y%, w%, h%) of the source frame → px (x, y, w, h) on screen, where the video fills `frame`
    (x, y, w, h px; default the whole canvas) with object-fit: cover and object-position `focus` (%)."""
    fx, fy, fw, fh = frame or (0, 0, X.W, X.H)
    sz = fit.size(src_abs(X, src)) or (16, 9)
    s = max(fw / sz[0], fh / sz[1])
    ox, oy = fx + (fw - sz[0] * s) * focus[0] / 100, fy + (fh - sz[1] * s) * focus[1] / 100
    x, y, w, h = [float(v) for v in box]
    return ox + sz[0] * s * x / 100, oy + sz[1] * s * y / 100, sz[0] * s * w / 100, sz[1] * s * h / 100


def retime_words(words, cuts):
    """words [{w,s,e}] minus the cut ranges [(a, b)…]: words inside a cut are dropped, later words shift left."""
    cuts = sorted((float(a), float(b)) for a, b in cuts)
    out = []
    for w in words:
        s, e = float(w["s"]), float(w["e"])
        if any(a <= s and e <= b for a, b in cuts): continue
        shift = sum(b - a for a, b in cuts if b <= s)
        out.append({**w, "s": round(s - shift, 3), "e": round(e - shift, 3)})
    return out


def tc(s):
    s = max(0, int(round(s))); return f"{s // 60:02d}:{s % 60:02d}"


def plain(s): return re.sub(r"[*|]", "", str(s or ""))


# ---------------------------------------------------------------- waveform + karaoke (audio_quote, podcast)
WAVE_CSS = """
.aw { position:absolute; }
.aw .row { position:absolute; inset:0; display:flex; align-items:center; gap:var(--gap, 4px); }
.aw .row i { flex:1; border-radius:3px; background:var(--wave-dim, rgba(127,127,127,.35)); min-height:4px; }
.aw .row.on i { background:var(--wave-on, var(--accent)); }
.aw .row.on { clip-path:inset(0 100% 0 0); }
.aw .ph { position:absolute; top:-8px; bottom:-8px; left:0; width:3px; background:var(--fg); border-radius:2px; }
.kr { position:absolute; }
.kr .kl { position:absolute; left:0; right:0; opacity:0; font-family:var(--f-body); font-weight:900; line-height:1.25; white-space:nowrap; }
.kr .kl i { font-style:normal; color:rgba(127,127,127,.55); color:var(--kr-dim, color-mix(in srgb, var(--fg) 45%, transparent)); }
"""


def wave_html(X, pk, x, y, w, h, cls="aw"):
    rows = "".join(f'<i style="height:{max(6, v * 100):.0f}%"></i>' for v in pk)
    gap = max(2, min(6, w / max(len(pk), 1) * 0.35))
    return (f'<div class="{cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px; --gap:{gap:.1f}px">'
            f'<div class="row">{rows}</div><div class="row on">{rows}</div><i class="ph"></i></div>')


def wave_tweens(X, sel, t0, run, w):
    X.css("av-wave", WAVE_CSS)
    X.tw(f'tl.fromTo("{sel} .row.on", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{run:.2f}, ease:"none"}}, {t0:.3f});')
    X.tw(f'tl.fromTo("{sel} .ph", {{x:0}}, {{x:{w - 3:.0f}, duration:{run:.2f}, ease:"none"}}, {t0:.3f});')


def kara_html(X, lines, x, y, w, h, max_px, min_px=26, cls="kr"):
    """one absolutely placed line per karaoke line, all sharing the largest size at which the longest line fits."""
    longest = max((ln for ln, _ in lines), key=lambda s: fit.width(s), default="")
    f = fit.fit_text(longest, w, h, max_px, min_px, lh=1.25, max_lines=1)
    px = f.px
    X.used_text.update("".join(ln for ln, _ in lines))
    body = "".join(f'<div class="kl" data-i="{i}" style="top:{(h - px * 1.25) / 2:.0f}px; font-size:{px}px">' + "".join(f"<i>{esc(c)}</i>" for c, _, _ in chars) + "</div>"
                   for i, (_, chars) in enumerate(lines))
    return f'<div class="{cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">{body}</div>', px


def kara_tweens(X, sel, lines, t0, end, ink="var(--fg)"):
    """line i shows from its first character to the next line's; each character lights on its own time."""
    X.css("av-wave", WAVE_CSS)
    for i, (_, chars) in enumerate(lines):
        if not chars: continue
        a = t0 + chars[0][1] - 0.12
        b = (t0 + lines[i + 1][1][0][1] - 0.12) if i + 1 < len(lines) and lines[i + 1][1] else end
        L = f'{sel} .kl[data-i="{i}"]'
        X.tw(f"tl.fromTo('{L}', {{opacity:0, y:18}}, {{opacity:1, y:0, duration:0.22, ease:'power3.out', immediateRender:false}}, {a:.3f});")
        X.tw(f"tl.to('{L}', {{opacity:0, y:-14, duration:0.16, ease:'power2.in', immediateRender:false}}, {max(a + 0.25, b - 0.02):.3f});")
        for j, (_, s, _) in enumerate(chars):
            X.tw(f"tl.set('{L} i:nth-child({j + 1})', {{color:'{ink}'}}, {t0 + s:.3f});")
