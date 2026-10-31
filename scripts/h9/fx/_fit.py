"""input-adaptive helpers for the plugin effects (files starting with _ are not effects; load by path).

fit(): pick a font size (vmin) and balanced line breaks so any text — 1 glyph to a sentence — fills a box
without overflowing; breaks fall between words (jieba for Chinese, Latin runs kept whole), never inside one.
compact(): scale huge numbers to 万 / 亿 (or K / M / B) so counters stay ≤ ~5 digits.
"""
import re

PUNCT_TAIL = re.compile(r"^[，。、！？；：,.!?;:）)」』”’%‰·]+$")


def em(s):
    """approximate advance width in em (CJK 1.0; Latin ~0.55; digits 0.6)."""
    w = 0.0
    for ch in str(s):
        o = ord(ch)
        if ch == " ": w += 0.3
        elif o >= 0x2E80: w += 1.0
        elif ch.isdigit(): w += 0.6
        elif ch.isupper(): w += 0.68
        elif ch.isalpha(): w += 0.55
        else: w += 0.42
    return w


def tokens(s):
    from h9.core import words
    out = []
    for w in words(str(s)):
        if out and (not w.strip() or PUNCT_TAIL.match(w)): out[-1] += w; continue
        out.append(w)
    return out or [str(s)]


def balance(s, n):
    """split into n lines with the smallest possible widest line (contiguous words)."""
    tk = tokens(s); n = max(1, min(n, len(tk)))
    ws = [em(x) for x in tk]
    pre = [0.0]
    for w in ws: pre.append(pre[-1] + w)
    T = len(tk); INF = float("inf")
    best = [[INF] * (T + 1) for _ in range(n + 1)]; cut = [[0] * (T + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for k in range(1, n + 1):
        for j in range(1, T + 1):
            for i in range(k - 1, j):
                v = max(best[k - 1][i], pre[j] - pre[i])
                if v < best[k][j]: best[k][j] = v; cut[k][j] = i
    lines, j = [], T
    for k in range(n, 0, -1):
        i = cut[k][j]; lines.append("".join(tk[i:j]).strip()); j = i
    return lines[::-1]


def fit(s, box_w, box_h, max_size, min_size=1.6, max_lines=3, lh=1.12):
    """-> (size_vmin, [lines]).  '|' in s forces the breaks."""
    s = str(s)
    if "|" in s:
        lines = [x.strip() for x in s.split("|")]
        size = min(max_size, box_w / max(em(x) for x in lines), box_h / (len(lines) * lh))
        return max(min_size, size), lines
    best = None
    for n in range(1, max_lines + 1):
        lines = balance(s, n)
        size = min(max_size, box_w / max(max(em(x) for x in lines), 0.5), box_h / (len(lines) * lh))
        score = size * (1 - 0.07 * (len(lines) - 1))
        if best is None or score > best[0] + 1e-9: best = (score, size, lines)
    return max(min_size, best[1]), best[2]


def frame_vmin(X):
    m = min(X.W, X.H); return X.W / m * 100, X.H / m * 100


def lines_html(X, lines, cls="fl"):
    return "".join(f'<span class="{cls}">{X.rich(x)}</span>' for x in lines)


def compact(vabs, mode="cn"):
    """-> (divisor, suffix) for the largest magnitude in a series."""
    if mode == "en":
        for d, s in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
            if vabs >= d * 10: return d, s
        return 1, ""
    if mode in ("cn", "auto"):
        if vabs >= 1e8: return 1e8, "亿"
        if vabs >= 1e5: return 1e4, "万"
    return 1, ""


def series_range(vals, head=1.22):
    lo, hi = min(0.0, min(vals)), max(0.0, max(vals))
    if hi == lo: hi = lo + 1
    span = hi - lo
    return lo - (span * (head - 1) if lo < 0 else 0), hi + (span * (head - 1) if hi > 0 else 0)


def js_fmt(dec):
    return f'(x)=>x.toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})'


def video_bg(X, cid, t, d, src, start=0.0):
    """footage behind an effect: a timed top-level <video> clip just under the effect clip (videos must be clips
    to stay frame-accurate). The effect must then be built without a theme background (see no_bg)."""
    url = X.asset(src, "video")
    X.clip(f"{cid}vb", t, d, "", "fxvb", 2, track=19, tag="video",
           attrs=f'src="{url}" muted playsinline data-media-start="{float(start):.3f}"', sty="width:100%; height:100%; object-fit:cover")
    return f"#{cid}vb"


def no_bg(p):
    """copy of the beat without its page theme, so the effect clip is transparent over footage."""
    return {k: v for k, v in p.items() if k != "theme"}
