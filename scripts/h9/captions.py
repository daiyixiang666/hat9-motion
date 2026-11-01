"""Captions from word timestamps.

Speakers: a word may carry "spk"; pages never mix speakers. meta.speakers = {"A": {"name": "主持人", "color": "#f6ce3a",
  "side": "left"}, "B": {...}} gives each one a colour, a name tag and a side (16:9: left / right / center).
karaoke — caption_mode "karaoke": the whole page shows dim and each glyph lights up on the moment it is spoken.
bilingual — meta.caption_tr = ["first sentence in English", ...] (one per sentence, split at 。！？): a second line
  under the caption for whichever sentence is being spoken.

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
            w = {"w": tok, "s": seg[0]["s"], "e": seg[-1]["e"]}
            if seg[0].get("spk"): w["spk"] = seg[0]["spk"]
            out.append(w)
        run.clear()
    for w in words:
        if w["w"] in PUN: flush(); out.append(w)
        else: run.append(w)
    flush()
    return out


def pages(words, maxlen, minlen=1, spk_out=None):
    """[[start, end, text], ...]; with spk_out=[] it also collects each page's speaker (pages never mix speakers)."""
    lines, cur, cs, ce, sp = [], "", None, None, None
    spks = []
    def push():
        lines.append([cs, ce, cur]); spks.append(sp)
    for w in words:
        tok = str(w["w"]).strip()
        if not tok: continue
        if cur and w.get("spk") is not None and w.get("spk") != sp:
            push(); cur, cs = "", None
        if not cur: sp = w.get("spk", sp)
        if all(c in PUN for c in tok):
            if cur and (tok not in SOFT or len(cur) >= minlen):
                push(); cur, cs = "", None
            continue
        if cs is not None and w["s"] - ce > 0.45:
            push(); cur, cs = "", None
        if cur and len(cur) + len(tok) > maxlen:
            push(); cur, cs = "", None
        if cs is None: cs = w["s"]
        cur += tok; ce = w["e"]
    if cur: push()
    out, osp = [], []
    for ln, k in zip(lines, spks):   # fold a ≤2-glyph orphan into the previous page when it fits (same speaker only)
        if out and len(ln[2]) <= 2 and len(out[-1][2]) + len(ln[2]) <= maxlen + 2 and ln[0] - out[-1][1] < 0.3 and osp[-1] == k:
            out[-1][1] = ln[1]; out[-1][2] += ln[2]
        else: out.append(ln); osp.append(k)
    if spk_out is not None: spk_out[:] = osp
    return out


def build(X, D, fix=None, maxlen=None):
    if not X.chars or X.S.get("captions") is False: return
    meta = X.v.get("meta", {})
    mode = meta.get("caption_mode") or X.S.get("caption_mode") or ("punch" if X.portrait else "reading")
    fix = fix or {}
    hl = meta.get("caption_hl", [])
    f = 1 / X.fps
    spk = []
    if mode == "punch":
        pg = pages(regroup(X._words), maxlen or 6, minlen=2, spk_out=spk)
    else:
        pg = pages(regroup(X._words), maxlen or (14 if X.portrait else 16), spk_out=spk)
    raw = [(p[0], p[1], p[2]) for p in pg]          # before fixes / timing pads (karaoke maps glyphs to words with it)
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
    speakers = meta.get("speakers") or {}
    tr = meta.get("caption_tr") or []
    has2 = " has2" if tr else ""
    used = 0
    for i, (a, b, txt) in enumerate(pg):
        X.used_text.update(txt)
        mark = next((k for k in hl if k in txt), None)
        if mode != "karaoke" and (mark and used / max(i, 1) <= 0.15 + 1e-9 or (mark and mode == "punch")):
            txt = txt.replace(mark, f"*{mark}*", 1); used += 1
        sp = speakers.get(spk[i]) if i < len(spk) and spk[i] is not None else None
        tag, cls, sty = "", "", ""
        if sp:
            side = sp.get("side", "center")
            cls = f" spk spk-{side}"
            sty = f"--spk:{sp.get('color', 'var(--accent)')};"
            if sp.get("name"): tag = f'<b class="spkn">{X.rich(sp["name"])}</b>'
        if mode == "karaoke":
            body, times = _karaoke(X, raw[i], txt)
        else:
            body = X.rich(txt)
        X.clip(f"cap{i}", a, min(b, D) - a, f'<span class="cp">{tag}{body}</span>', f"cap cap-{mode}{cls}{has2}", 50, track=12, sty=sty)
        if mode == "punch":
            X.tw(f'tl.from("#cap{i} .cp", {{scale:0.85, opacity:0, duration:0.18, ease:"back.out(1.7)"}}, {a:.3f});')
        if mode == "karaoke" and times:
            t0 = times[0]
            arr = ",".join(f"{max(0.0, x - t0):.3f}" for x in times)
            X.tw(f'tl.to("#cap{i} .k", {{opacity:1, duration:0.12, ease:"power1.out", stagger:(k)=>[{arr}][k]}}, {t0:.3f});')
    if tr: _bilingual(X, D, tr, mode)
    if speakers:
        X.css("cap-spk", """.cap.spk .cp { box-shadow:inset 0 -0.18em 0 var(--spk); }
.cap .spkn { display:inline-block; font-size:.62em; font-weight:900; color:var(--cap-bg-fg, #111); background:var(--spk); padding:.05em .45em; margin-right:.5em; border-radius:.2em; vertical-align:.15em; }
#root.h .cap.spk-left { text-align:left; padding-left:7%; } #root.h .cap.spk-right { text-align:right; padding-right:7%; }""")
    if mode == "karaoke":
        X.css("cap-karaoke", """.cap-karaoke .k { font-style:normal; opacity:.38; } .cap-karaoke .k.p { opacity:1; }
#root.v .cap-karaoke { bottom:auto; top:var(--punch-top, 71%); } #root.v .cap-karaoke .cp { font-size:calc(var(--cap-size, 46px) * 1.3); line-height:1.25; }""")
    X.css("cap-punch", """.cap-punch { bottom:auto; top:var(--punch-top, 71%); }
.cap-punch .cp { font-family:var(--f-punch, var(--f-display)); font-size:var(--punch-size, 88px); font-weight:900; line-height:1.1;
  -webkit-text-stroke:var(--punch-stroke, 0); paint-order:stroke fill; }
.cap-punch .em .emt { display:inline-block; transform:scale(1.2); color:var(--cap-em, var(--accent)); }""")


def _karaoke(X, page, txt):
    """glyph spans for one page + the moment each glyph is spoken (word times when the text maps 1:1, else linear)."""
    a, b, raw = page
    cs = [(c, s0) for c, s0, e0 in X.chars if a - 0.02 <= s0 <= b + 0.02 and c not in PUN and c.strip()]
    glyphs = [c for c in txt if c not in "*|"]
    if "".join(c for c, _ in cs) == "".join(c for c in glyphs if c.strip()) and cs:
        it = iter(s0 for _, s0 in cs)
        times = [next(it) if c.strip() else None for c in glyphs]
        last = a
        times = [last := (x if x is not None else last) for x in times]
    else:
        n = max(1, len(glyphs))
        times = [a + (b - a) * k / n for k in range(n)]
    spans = "".join(f'<i class="k{" p" if c in PUN else ""}">{X.rich(c) if c.strip() else "&nbsp;"}</i>' for c in glyphs)
    return spans, times


def sentences(words):
    """(start, end) of each sentence, split at 。！？!? tokens."""
    out, s0, e0 = [], None, None
    for w in words:
        tok = str(w["w"])
        if w["e"] - w["s"] > 1e-6 and tok.strip() and not all(c in PUN for c in tok):
            if s0 is None: s0 = w["s"]
            e0 = w["e"]
        if any(c in "。！？!?" for c in tok) and s0 is not None:
            out.append((s0, e0)); s0 = None
    if s0 is not None: out.append((s0, e0))
    return out


def _bilingual(X, D, tr, mode):
    f = 1 / X.fps
    sp = sentences(X._words)
    speakers = X.v.get("meta", {}).get("speakers") or {}
    for i, (a, b) in enumerate(sp[:len(tr)]):
        if not tr[i]: continue
        who = next((w.get("spk") for w in X._words if w["s"] >= a - 1e-3 and w.get("spk") is not None), None)
        side = f" spk spk-{speakers[who].get('side', 'center')}" if who in speakers else ""
        nxt = sp[i + 1][0] - 2 * f if i + 1 < len(sp) else min(D, b + 1.0)
        a0 = max(0, a - 2 * f); b0 = max(a0 + 0.8, min(nxt, b + 0.6) if nxt > b else b + 0.3)
        X.clip(f"cap2_{i}", a0, min(b0, D) - a0, f'<span class="cp2">{X.rich(tr[i])}</span>', f"cap cap2{' under-punch' if mode in ('punch', 'karaoke') and X.portrait else ''}{side}", 49, track=11)
    X.css("cap-tr", """.cap.has2 { bottom:calc(var(--cap-bottom, 56px) + var(--cap-size, 46px) * .62 * 1.3 + 14px); }
.cap2 { bottom:var(--cap-bottom, 56px); } .cap2 .cp2 { display:inline-block; font-family:var(--f-latin, var(--f-body)); font-size:calc(var(--cap-size, 46px) * .62); font-weight:600;
  color:var(--cap-fg, #fff); opacity:.88; text-shadow:var(--cap-shadow, 0 2px 0 rgba(0,0,0,.8), 0 0 14px rgba(0,0,0,.6)); background:var(--cap-bg, none); padding:var(--cap-pad, 0); border-radius:var(--cap-radius, 0); max-width:86%; }
.cap2.under-punch { bottom:auto; top:calc(var(--punch-top, 71%) + var(--punch-size, 88px) * 1.3); }""")


def srt(X, D, path, fix=None):
    """write the narration as an .srt next to the build (for 剪映 / Premiere), whatever the on-screen caption style."""
    if not X.chars: return None
    fix = fix or {}
    spk = []
    pg = pages(regroup(X._words), 14 if X.portrait else 16, spk_out=spk)
    names = {k: v.get("name", "") for k, v in (X.v.get("meta", {}).get("speakers") or {}).items()}
    def ts(x):
        h, r = divmod(max(0.0, x), 3600); m, s_ = divmod(r, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s_):02d},{int(round((s_ - int(s_)) * 1000)):03d}"
    out = []
    for i, (a, b, txt) in enumerate(pg, 1):
        for k, v in fix.items(): txt = txt.replace(k, v)
        who = names.get(spk[i - 1]) if i - 1 < len(spk) else None
        out.append(f"{i}\n{ts(a)} --> {ts(min(max(b, a + 0.8), D))}\n{(who + '：') if who else ''}{txt}\n")
    path.write_text("\n".join(out), encoding="utf-8")
    return path
