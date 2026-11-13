"""Captions from word timestamps.

Speakers: a word may carry "spk"; pages never mix speakers. meta.speakers = {"A": {"name": "主持人", "color": "#f6ce3a",
  "side": "left"}, "B": {...}} gives each one a colour, a name tag and a side (16:9: left / right / center).
karaoke — caption_mode "karaoke": the whole page shows dim and each glyph lights up on the moment it is spoken.
bilingual — meta.caption_tr = ["first sentence in English", ...] (one per sentence, split at 。！？): a second line
  under the caption for whichever sentence is being spoken.

Two modes (meta.caption_mode, meta.caption_preset or the style):
  reading — the default in BOTH aspects. One whole phrase per page: ≤16 glyphs in 16:9, ≤14 in 9:16 (1–2 lines),
            in = first glyph − 2 frames, out = last glyph + 5 frames (bridged to the next page if the gap < 0.3 s),
            at most ONE highlighted word per page (from meta.caption_hl keywords).
  punch   — only when asked for (caption_mode "punch", or the douyin / shipinhao preset in 9:16). 2–6 glyphs per
            page, page pops 0.85→1.0 (back.out), keyword enlarged in the accent colour.

Page breaks (pages()), with or without jieba:
  1. phrases end at punctuation (。！？ always), at a speech pause (> 0.3 s between tokens) and at a speaker change;
  2. a phrase longer than the page limit is split into the fewest balanced pages, between tokens only, at the best
     boundary near each balanced cut: the biggest speech gap, then word hints (after 的/了/吗…, before 就/也/但是/所以…),
     else the middle. Latin / number runs (A-Level, AP, 3.8, 2025, 5%), spoken numbers (六十亿), caption_fix keys
     and caption_hl keywords are one token and never split; a number keeps its unit and range (3到4门); no page is
     a 1–2 glyph orphan (it joins its neighbour after a full-width space). jieba, when installed, regroups per-character
     timestamps into real words first (better boundaries); without it the rules above still never cut a run of
     Latin letters / digits and rarely cut a Chinese word. Latin letters count as about half a glyph.

Readability: in 9:16 reading mode over real footage (meta.presenter is a video, or any beat uses a video file) and
with no meta.caption_style / meta.caption_preset, captions get a dark see-through plate (rgba(0,0,0,.55), white
text), a plain heavy sans (PingFang SC / Noto Sans SC 700) and sit in the lower band above the platform UI.
meta.caption_style and meta.caption_preset always win. A style that designs its own subtitle over footage opts out
of the plate with STYLE["caption_plate"] = False.

Position per beat: a beat's "caption_pos": {"bottom": px, "align": "left" | "center" | "right"} puts that beat's
subtitle pages there (over any position the style pins); a style's scene moves the subtitle from a time on with
captions.place(X, t, bottom=…, align=…).
"""
PUN = "，,。.!！?？、；;：:"
SOFT = "，,、；;：:"          # 。！？ always end a page, even after a single glyph


def _decimal(words, i):
    """True when token i is the point in a number like 4.8 (a digit on both sides), not a full stop."""
    if str(words[i]["w"]).strip() not in ".．" or i == 0 or i + 1 >= len(words): return False
    return str(words[i - 1]["w"]).strip()[-1:].isdigit() and str(words[i + 1]["w"]).strip()[:1].isdigit()


def _join_decimals(words):
    """merge "4" "." "8亿" into one token so a page never breaks inside a number."""
    out, i = [], 0
    while i < len(words):
        if out and _decimal(words, i):
            a, b = out[-1], words[i + 1]
            out[-1] = {**a, "w": str(a["w"]).strip() + str(words[i]["w"]).strip() + str(b["w"]).strip(), "e": b["e"]}
            i += 2
        else:
            out.append(words[i]); i += 1
    return out


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
    for i, w in enumerate(words):
        if w["w"] in PUN and not _decimal(words, i): flush(); out.append(w)
        else: run.append(w)
    flush()
    return out


PAUSE = 0.3            # a silence longer than this between two tokens ends a phrase
HARD = "。.!！?？"      # sentence ends
ASCII_JOIN = "-%+/'&_#@"   # glue inside a Latin / number run: A-Level, 5%, C++, 24/7
# no-jieba word-boundary hints: a phrase may end after these particles, or start at these words
END_AFTER = "的了吗呢吧啊呀嘛"
NOT_AFTER = {"了": "解", "的": "确"}          # 了解 / 的确 are words, not particle + next word
START_AT = "就也都还但而才又把被让和跟与或再很最更只"
START_AT2 = ("所以", "因为", "如果", "可以", "但是", "而且", "然后", "其实", "就是", "还是", "不过")
RANGE_LINK = "到至~～-和或第约近超"        # 3到4门 / 第3名: a number stays with what joins it


def _ascii_word(c):
    """True for a character that belongs to a Latin / number run (letters, digits and the joiners above)."""
    if c.isascii() and c.isalnum():
        return True
    return c in ASCII_JOIN


def glen(text):
    """caption length in CJK glyph widths: a Latin letter or digit counts about half a glyph."""
    n = 0.0
    for c in text:
        if c.isascii():
            n += 0.55
        else:
            n += 1.0
    return n


def _merge_ascii(words):
    """glue neighbouring tokens that form one Latin / number run ("A" "-" "L" "e"... -> "A-Level"; "A" "P" -> "AP")
    so a page can never break inside it."""
    out = []
    for w in words:
        tok = str(w["w"]).strip()
        if out and tok:
            prev = str(out[-1]["w"]).strip()
            same_spk = out[-1].get("spk") == w.get("spk")
            if prev and same_spk and _ascii_word(prev[-1]) and _ascii_word(tok[0]):
                merged = dict(out[-1])
                merged["w"] = prev + tok
                merged["e"] = w["e"]
                out[-1] = merged
                continue
        out.append(w)
    return out


CN_NUM = "零〇一二两三四五六七八九十百千万亿"
CN_BIG = "十百千万亿"


def _merge_numbers(words):
    """glue a spoken number that the aligner gave glyph by glyph ("六" "十" "亿" -> "六十亿", "3" "千" -> "3千"),
    so a page never breaks inside it and caption_fix ("六十亿" -> "60 亿") still finds it."""
    out = []
    for w in words:
        tok = str(w["w"]).strip()
        if out and tok:
            prev = str(out[-1]["w"]).strip()
            same_spk = out[-1].get("spk") == w.get("spk")
            glue = False
            if prev and prev[-1] in CN_NUM and tok[0] in CN_NUM:
                glue = True
            if prev and prev[-1].isdigit() and tok[0] in CN_BIG:
                glue = True
            if glue and same_spk:
                merged = dict(out[-1])
                merged["w"] = prev + tok
                merged["e"] = w["e"]
                out[-1] = merged
                continue
        out.append(w)
    return out


def _merge_keep(words, keep):
    """glue the tokens under each occurrence of a protected string (caption_fix keys, caption_hl keywords) into one
    token, so a page never breaks inside a fixed term or a highlighted word."""
    if not keep:
        return words
    starts = []
    text = ""
    for w in words:
        starts.append(len(text))
        text += str(w["w"]).strip()
    # owner[i] = index of the token that holds character i
    owner = []
    for i in range(len(words)):
        size = len(str(words[i]["w"]).strip())
        for j in range(size):
            owner.append(i)
    group = list(range(len(words)))        # group[i] = first token of the run token i is glued into
    for key in keep:
        key = str(key).strip()
        if len(key) < 2:
            continue
        pos = text.find(key)
        while pos >= 0:
            first = owner[pos]
            last = owner[pos + len(key) - 1]
            ok = True
            for i in range(first, last + 1):
                if words[i].get("spk") != words[first].get("spk"):
                    ok = False
            if ok:
                for i in range(first, last + 1):
                    group[i] = group[first]
            pos = text.find(key, pos + 1)
    out = []
    for i in range(len(words)):
        tok = str(words[i]["w"]).strip()
        if out and i > 0 and group[i] == group[i - 1]:
            merged = dict(out[-1])
            merged["w"] = str(merged["w"]).strip() + tok
            merged["e"] = words[i]["e"]
            out[-1] = merged
        else:
            out.append(words[i])
    return out


def _clauses(words, minlen):
    """split the token stream into phrases: at punctuation, at a speech pause (> PAUSE s) and at a speaker change.
    Each phrase = {"toks": [...], "hard": ends a sentence, "spk": speaker}."""
    out = []
    cur = []
    cur_spk = None
    for w in words:
        tok = str(w["w"]).strip()
        if not tok:
            continue
        if cur and w.get("spk") is not None and w.get("spk") != cur_spk:
            _close(out, cur, cur_spk, True)
        if not cur:
            cur_spk = w.get("spk", cur_spk)
        is_pun = True
        for c in tok:
            if c not in PUN:
                is_pun = False
        if is_pun:
            text = ""
            for t in cur:
                text += str(t["w"]).strip()
            if cur and (tok not in SOFT or glen(text) >= minlen):
                hard = False
                for c in tok:
                    if c in HARD:
                        hard = True
                _close(out, cur, cur_spk, hard)
            continue
        if cur and w["s"] - cur[-1]["e"] > PAUSE:
            _close(out, cur, cur_spk, False)
            cur_spk = w.get("spk", cur_spk)
        cur.append(dict(w, w=tok))
    _close(out, cur, cur_spk, True)
    return out


def _close(out, cur, spk, hard):
    """end the phrase being collected in cur (if any) and add it to out."""
    if not cur:
        return
    out.append({"toks": list(cur), "hard": hard, "spk": spk})
    cur.clear()


def _boundary_score(toks, k):
    """how good a page break is between toks[k-1] and toks[k]: a speech gap, a particle before it or a
    phrase-starting word after it make it better; cutting a number off its unit or range makes it worse."""
    left = toks[k - 1]["w"]
    right = toks[k]["w"]
    after = ""
    if k + 1 < len(toks):
        after = toks[k + 1]["w"]
    last = left[-1]
    first = right[0]
    score = 0.0
    gap = toks[k]["s"] - toks[k - 1]["e"]
    if gap > 0:
        score += min(gap, 0.3) * 8
    if last in END_AFTER and NOT_AFTER.get(last) != first:
        score += 1.0
    two = (right + after)[:2]
    if two in START_AT2:
        score += 1.0
    elif first in START_AT:
        score += 0.8
    if last.isdigit():
        score -= 3.0                   # 3|门, 2025|年
    if first.isdigit() and last in RANGE_LINK:
        score -= 3.0                   # 3到|4
    return score


def _best_cut(toks, n, maxlen, parts, floor):
    """(score, k) of the best first cut when the phrase (n glyphs) is shown on `parts` pages, or None."""
    limit = maxlen + 0.5                # Latin widths are estimates: half a glyph of slack
    target = n / parts
    best = None
    acc = 0.0
    for k in range(1, len(toks)):
        acc += glen(toks[k - 1]["w"])
        left = acc
        right = n - acc
        if left > limit:
            break
        if right > (parts - 1) * limit:
            continue
        if left < floor or right < floor:
            continue
        score = _boundary_score(toks, k) - abs(left - target) / maxlen * 3
        if best is None or score > best[0]:
            best = (score, k)
    return best


def _split_clause(toks, maxlen, minpart):
    """break one phrase longer than maxlen into the fewest balanced pages (one more when that avoids a bad cut),
    only between tokens, at the best boundary near each balanced cut (speech gap > word hints > middle), never
    leaving a part shorter than minpart."""
    text = ""
    for t in toks:
        text += t["w"]
    n = glen(text)
    if n <= maxlen + 0.5 or len(toks) < 2:
        return [toks]
    parts = int(n // maxlen)
    if parts * maxlen < n:
        parts += 1
    best = None
    for floor in (minpart, 1):
        for extra in (0, 1):
            tries = parts + extra
            if extra and n / tries < minpart:
                continue
            cut = _best_cut(toks, n, maxlen, tries, floor)
            if cut is None:
                continue
            score = cut[0] - extra * 1.5           # an extra page costs something, a word cut costs more
            if best is None or score > best[0]:
                best = (score, cut[1])
        if best is not None:
            break
    if best is None:
        # nothing fits (e.g. one very long Latin token): cut as close to the middle as the tokens allow
        acc = 0.0
        best_diff = None
        best_k = 1
        for k in range(1, len(toks)):
            acc += glen(toks[k - 1]["w"])
            diff = abs(acc - n / 2)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_k = k
        best = (0.0, best_k)
    head = toks[:best[1]]
    rest = toks[best[1]:]
    return [head] + _split_clause(rest, maxlen, minpart)


def pages(words, maxlen, minlen=1, spk_out=None, keep=None):
    """[[start, end, text], ...]; with spk_out=[] it also collects each page's speaker (pages never mix speakers).
    keep = strings a page may never break inside (caption_fix keys, caption_hl keywords).
    Breaks at punctuation and speech pauses first; a phrase longer than maxlen is split into balanced parts at the
    best gap between tokens (jieba words when installed, else characters scored by speech gaps and word hints), never
    inside a Latin / number run, never leaving a 1-2 glyph orphan page."""
    words = _join_decimals(words)
    words = _merge_ascii(words)
    words = _merge_numbers(words)
    words = _merge_keep(words, keep)
    minpart = 3
    if maxlen < 9:
        minpart = 2
    raw = []
    for cl in _clauses(words, minlen):
        parts = _split_clause(cl["toks"], maxlen, minpart)
        for j in range(len(parts)):
            part = parts[j]
            text = ""
            for t in part:
                text += t["w"]
            hard = False
            if j == len(parts) - 1:
                hard = cl["hard"]
            raw.append({"s": part[0]["s"], "e": part[-1]["e"], "text": text, "hard": hard, "spk": cl["spk"]})
    # a <= 2-glyph orphan joins the page before it (same sentence, same speaker) ...
    folded = []
    for pg in raw:
        if folded:
            prev = folded[-1]
            small = glen(pg["text"]) <= 2
            fits = glen(prev["text"]) + glen(pg["text"]) + 1 <= maxlen + 2
            if small and fits and not prev["hard"] and prev["spk"] == pg["spk"] and pg["s"] - prev["e"] < 1.0:
                prev["e"] = pg["e"]
                prev["text"] += "\u3000" + pg["text"]     # full-width space where the comma / pause was
                prev["hard"] = pg["hard"]
                continue
        folded.append(pg)
    # ... or, when it opens a sentence, the page after it
    final = []
    carry = None
    for pg in folded:
        if carry is not None:
            if carry["spk"] == pg["spk"] and glen(carry["text"]) + glen(pg["text"]) + 1 <= maxlen + 2:
                pg = dict(pg)
                pg["s"] = carry["s"]
                pg["text"] = carry["text"] + "\u3000" + pg["text"]
            else:
                final.append(carry)
            carry = None
        if glen(pg["text"]) <= 2 and not pg["hard"]:
            carry = pg
            continue
        final.append(pg)
    if carry is not None:
        final.append(carry)
    out = []
    osp = []
    for pg in final:
        out.append([pg["s"], pg["e"], pg["text"]])
        osp.append(pg["spk"])
    if spk_out is not None:
        spk_out[:] = osp
    return out


# meta.caption_preset: house caption looks per platform (applied on top of the style's caption tokens).
# douyin / shipinhao: big punchy page above the bottom chrome; xiaohongshu: quieter, smaller, soft plate;
# bilibili / youtube: classic outlined reading line at the bottom of 16:9.
PRESETS = {
    "douyin":      {"mode": "punch",   "v": {"punch-top": "70%", "punch-size": "78px", "punch-stroke": "6px #000", "cap-bg": "none", "cap-fg": "#fff", "cap-em": "#ffd84a"}},
    "shipinhao":   {"mode": "punch",   "v": {"punch-top": "69%", "punch-size": "70px", "punch-stroke": "5px #000", "cap-bg": "none", "cap-fg": "#fff", "cap-em": "#ffd84a"}},
    "xiaohongshu": {"mode": "reading", "v": {"cap-size": "40px", "cap-bg": "rgba(255,255,255,.88)", "cap-fg": "#222", "cap-pad": "8px 18px 10px", "cap-radius": "10px",
                                            "cap-shadow": "none", "cap-em": "#ff2442", "cap-bottom": "120px"}},
    "bilibili":    {"mode": "reading", "v": {"cap-size": "44px", "cap-bg": "none", "cap-fg": "#fff", "cap-shadow": "0 0 3px #000, 0 0 3px #000, 0 2px 6px rgba(0,0,0,.8)",
                                            "cap-em": "#00a1d6", "cap-bottom": "48px"}},
    "youtube":     {"mode": "reading", "v": {"cap-size": "42px", "cap-bg": "rgba(8,8,8,.75)", "cap-fg": "#fff", "cap-pad": "4px 12px 6px", "cap-radius": "4px",
                                            "cap-shadow": "none", "cap-em": "#fff", "cap-bottom": "56px"}},
}


VIDEO_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi")

# 9:16 reading captions over real footage (a filmed presenter, B-roll): a dark see-through plate and a plain heavy
# sans, in the lower band clear of the platform's bottom UI. White text on a light table / wall stays readable.
FOOTAGE_PLATE = (
    "#root#root.v { --cap-bg:rgba(0,0,0,.55); --cap-fg:#fff; --cap-em:#ffd84a; --cap-shadow:none;"
    " --cap-pad:8px 22px 11px; --cap-radius:12px; --cap-size:50px; --cap-weight:700; --cap-bottom:516px;"
    " --f-cap:'PingFang SC', 'Noto Sans SC', 'Source Han Sans SC', 'Microsoft YaHei', 'h9-noto-sans-sc', sans-serif; }"
    " #root#root.v .clip.cap { top:auto !important; bottom:var(--cap-bottom) !important; left:0 !important;"
    " right:0 !important; text-align:center !important; padding-left:120px; padding-right:120px; }"
    " #root#root.v .cap .cp { line-height:1.3; letter-spacing:.01em; }"
)


def _mentions_video(obj):
    """True when a video.json value (string, list or dict, searched all the way down) names a video file."""
    if isinstance(obj, str):
        low = obj.lower()
        for ext in VIDEO_EXT:
            if low.endswith(ext):
                return True
        return False
    if isinstance(obj, dict):
        for key in obj:
            if _mentions_video(obj[key]):
                return True
        return False
    if isinstance(obj, list):
        for item in obj:
            if _mentions_video(item):
                return True
    return False


def has_footage(video):
    """True when real footage can sit under the captions: a video presenter or any video clip in the beats."""
    meta = video.get("meta", {})
    pres = meta.get("presenter")
    if isinstance(pres, dict):
        pres = pres.get("src")
    if pres and _mentions_video(pres):
        return True
    return _mentions_video(video.get("beats", []))


def place(X, t, bottom=None, align=None):
    """move the subtitle from time t on: bottom = px from the frame's bottom edge, align = left / center / right.
    For a style's scenes, e.g. a toast that alternates top / bottom per beat (a beat's own "caption_pos" is _beat_pos)."""
    reqs = getattr(X, "caption_places", None)
    if reqs is None:
        reqs = []
        X.caption_places = reqs
    reqs.append((float(t), bottom, align))


def _places(X):
    """the tweens for every caption move asked for with place() (set on #root just before the beat starts)."""
    for t, bottom, align in getattr(X, "caption_places", None) or []:
        vals = {}
        if bottom is not None:
            vals["--cap-bottom"] = f"{float(bottom):.0f}px"
        if align:
            vals["--cap-align"] = align
        if vals:
            body = ", ".join(f'"{k}":"{v}"' for k, v in vals.items())
            X.tw(f'tl.set("#root", {{{body}}}, {max(0, t - 0.02):.3f});')


def _beat_pos(X, a):
    """inline position for a page starting at a, from the beat's "caption_pos" (inline !important beats a style's pin)."""
    for t0, t1, cp in getattr(X, "caption_pos", None) or []:
        if t0 - 0.05 <= a < t1:
            out = ""
            if cp.get("bottom") is not None:
                out += f"top:auto !important; bottom:{float(cp['bottom']):.0f}px !important;"
            if cp.get("align"):
                out += f"text-align:{cp['align']} !important;"
            return out
    return ""


def build(X, D, fix=None, maxlen=None):
    _places(X)
    if not X.chars or X.S.get("captions") is False: return
    meta = X.v.get("meta", {})
    pre = PRESETS.get(meta.get("caption_preset") or "")
    if pre:
        v = dict(pre["v"])
        pmode = pre["mode"] if X.portrait or pre["mode"] != "punch" else "reading"      # punch pages are a 9:16 look; 16:9 reads
        if pmode == "reading" and X.portrait: v["cap-bottom"] = "516px"   # 9:16: the same band the punch pages use, above the chrome
        if pmode == "reading" and pre["mode"] == "punch":                  # 16:9 version of a punch preset: outlined reading line
            v.update({"cap-shadow": "0 0 4px #000, 0 0 4px #000, 0 3px 8px rgba(0,0,0,.8)", "cap-size": "46px"})
        X.css("cap-preset", "#root { " + " ".join(f"--{k}:{val};" for k, val in v.items()) + " }")
        pre = dict(pre, mode=pmode)
    # reading (one whole phrase per page) is the default in both aspects; punch only when the film or a preset asks
    mode = meta.get("caption_mode") or (pre or {}).get("mode") or X.S.get("caption_mode") or "reading"
    # meta.caption_style: caption tokens that win over the style and the preset — one subtitle look across a
    # mixed-style film, e.g. {"cap-bottom": "300px", "cap-size": "50px", "f-cap": "'PingFang SC', sans-serif"}
    user = meta.get("caption_style") or {}
    if user:
        css = "#root#root { " + " ".join(f"--{k}:{val};" for k, val in user.items()) + " }"
        if "cap-bottom" in user:
            # some styles pin the subtitle box themselves (poster: left-aligned, 540 px up); the film's choice wins
            css += (" #root#root .clip.cap { top:auto !important; bottom:var(--cap-bottom) !important; left:0 !important;"
                    " right:0 !important; text-align:center !important; }"
                    " #root#root.v .clip.cap { padding-left:120px; padding-right:120px; }")
        X.css("cap-user", css)
    if not user and not pre and mode == "reading" and X.portrait and has_footage(X.v) and X.S.get("caption_plate", True) is not False:
        X.css("cap-auto", FOOTAGE_PLATE)
    fix = fix or {}
    hl = meta.get("caption_hl", [])
    f = 1 / X.fps
    spk = []
    keep = list(fix.keys())
    for k in hl:
        keep.append(k)
    if mode == "punch":
        pg = pages(regroup(X._words), maxlen or 6, minlen=2, spk_out=spk, keep=keep)
    else:
        pg = pages(regroup(X._words), maxlen or (14 if X.portrait else 16), spk_out=spk, keep=keep)
    mute = getattr(X, "caption_mute", [])
    if mute:          # a page is dropped when most of it falls inside a muted beat
        kept = []
        kept_spk = []
        for k in range(len(pg)):
            p = pg[k]
            inside = 0.0
            for m0, m1 in mute:
                inside += max(0.0, min(p[1], m1) - max(p[0], m0))
            if inside < 0.5 * max(p[1] - p[0], 0.01):
                kept.append(p)
                kept_spk.append(spk[k] if k < len(spk) else None)
        pg = kept
        spk[:] = kept_spk
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
        sty += _beat_pos(X, a)
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
    if "".join(c for c, _ in cs) == "".join(c for c in glyphs if c.strip() and c not in PUN) and cs:
        it = iter(s0 for _, s0 in cs)
        times = [next(it) if c.strip() and c not in PUN else None for c in glyphs]
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
    pg = pages(regroup(X._words), 14 if X.portrait else 16, spk_out=spk, keep=list(fix.keys()))
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
