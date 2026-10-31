"""Captions from word timestamps.

Two modes (style or meta.caption_mode):
  reading — 16:9 default. Whole phrase per page, ≤16 glyphs, ，。 become a full-width space (Netflix 简中),
            in = first glyph − 2 frames, out = last glyph + 5 frames (bridged to the next page if the gap < 0.3 s),
            at most ONE highlighted word per page (from meta.caption_hl keywords).
  punch   — 9:16 / hooks. 2–6 glyphs per page, page pops 0.85→1.0 (back.out), keyword enlarged in the accent colour.
"""
PUN = "，,。.!！?？、；;：:"
SOFT = "，,、；;：:"          # 。！？ always end a page, even after a single glyph


def regroup(words):
    """per-character timestamps (common from aligners/TTS) -> word tokens via jieba, so lines never break mid-word."""
    if not words or max(len(str(w["w"]).strip()) for w in words) > 1: return words
    try:
        import jieba
    except ImportError:
        return words
    out, run = [], []
    def flush():
        if not run: return
        text = "".join(w["w"] for w in run); i = 0
        for tok in jieba.cut(text):
            seg = run[i:i + len(tok)]; i += len(tok)
            out.append({"w": tok, "s": seg[0]["s"], "e": seg[-1]["e"]})
        run.clear()
    for w in words:
        if w["w"] in PUN: flush(); out.append(w)
        else: run.append(w)
    flush()
    return out


def pages(words, maxlen, minlen=1):
    lines, cur, cs, ce = [], "", None, None
    for w in words:
        tok = str(w["w"]).strip()
        if not tok: continue
        if all(c in PUN for c in tok):
            if cur and (tok not in SOFT or len(cur) >= minlen):
                lines.append([cs, ce, cur]); cur, cs = "", None
            continue
        if cs is not None and w["s"] - ce > 0.45:
            lines.append([cs, ce, cur]); cur, cs = "", None
        if cur and len(cur) + len(tok) > maxlen:
            lines.append([cs, ce, cur]); cur, cs = "", None
        if cs is None: cs = w["s"]
        cur += tok; ce = w["e"]
    if cur: lines.append([cs, ce, cur])
    out = []
    for ln in lines:   # fold a ≤2-glyph orphan into the previous page when it fits
        if out and len(ln[2]) <= 2 and len(out[-1][2]) + len(ln[2]) <= maxlen + 2 and ln[0] - out[-1][1] < 0.3:
            out[-1][1] = ln[1]; out[-1][2] += ln[2]
        else: out.append(ln)
    return out


def build(X, D, fix=None, maxlen=None):
    if not X.chars or X.S.get("captions") is False: return
    meta = X.v.get("meta", {})
    mode = meta.get("caption_mode") or X.S.get("caption_mode") or ("punch" if X.portrait else "reading")
    fix = fix or {}
    hl = meta.get("caption_hl", [])
    f = 1 / X.fps
    if mode == "punch":
        pg = pages(regroup(X._words), maxlen or 6, minlen=2)
    else:
        pg = pages(regroup(X._words), maxlen or (14 if X.portrait else 16))
    for p in pg:
        for k, v in fix.items(): p[2] = p[2].replace(k, v)
    # timing: in 2 frames early, out 5 frames late, bridge small gaps (no flicker)
    for i, p in enumerate(pg):
        p[0] = max(0, p[0] - 2 * f); p[1] = p[1] + 5 * f
        if i + 1 < len(pg):
            nxt = pg[i + 1][0] - 2 * f
            p[1] = nxt if nxt - p[1] < 0.3 else min(p[1], nxt)
        p[1] = max(p[1], p[0] + 0.8)
        if i + 1 < len(pg): p[1] = min(p[1], pg[i + 1][0] - 2 * f)
    used = 0
    for i, (a, b, txt) in enumerate(pg):
        X.used_text.update(txt)
        mark = next((k for k in hl if k in txt), None)
        if mark and used / max(i, 1) <= 0.15 + 1e-9 or (mark and mode == "punch"):
            txt = txt.replace(mark, f"*{mark}*", 1); used += 1
        X.clip(f"cap{i}", a, min(b, D) - a, f'<span class="cp">{X.rich(txt)}</span>', f"cap cap-{mode}", 50, track=12)
        if mode == "punch":
            X.tw(f'tl.from("#cap{i} .cp", {{scale:0.85, opacity:0, duration:0.18, ease:"back.out(1.7)"}}, {a:.3f});')
    X.css("cap-punch", """.cap-punch { bottom:auto; top:var(--punch-top, 71%); }
.cap-punch .cp { font-family:var(--f-punch, var(--f-display)); font-size:var(--punch-size, 88px); font-weight:900; line-height:1.1;
  -webkit-text-stroke:var(--punch-stroke, 0); paint-order:stroke fill; }
.cap-punch .em .emt { display:inline-block; transform:scale(1.2); color:var(--cap-em, var(--accent)); }""")


def srt(X, D, path, fix=None):
    """write the narration as an .srt next to the build (for 剪映 / Premiere), whatever the on-screen caption style."""
    if not X.chars: return None
    fix = fix or {}
    pg = pages(regroup(X._words), 14 if X.portrait else 16)
    def ts(x):
        h, r = divmod(max(0.0, x), 3600); m, s_ = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s_):02d},{int(round((s_ - int(s_)) * 1000)):03d}"
    out = []
    for i, (a, b, txt) in enumerate(pg, 1):
        for k, v in fix.items(): txt = txt.replace(k, v)
        out.append(f"{i}\n{ts(a)} --> {ts(min(max(b, a + 0.8), D))}\n{txt}\n")
    path.write_text("\n".join(out), encoding="utf-8")
    return path
