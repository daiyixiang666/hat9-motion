"""shared helpers for the structure effects (list_stack, steps, ranking, term_card, word_swap, …). Not an effect.

box(): the free area of the page in px — clear of the header band, the caption pill and the footer — so a
layout can fill it instead of guessing. items(): any list-ish parameter → [(text, sub)]. fitpx(): one font size
that fits EVERY string of a group in its slot (rows of a list must share a size). beats(): when each item lands —
from narration cues ("at": ["@一", "@二"]) when given, else spread evenly over the beat.
"""
from h9 import fit
from h9.aefx import _cap_clear, THEMES


def vm(X, v): return min(X.W, X.H) * v / 100


def box(X, p, pad=None):
    """(x, y, w, h) in px of the page area the effect may use."""
    if X.portrait:
        x0, x1 = 56, X.W - 56
        y0 = 268 if p.get("line") else 120
        y1 = 1300 if p.get("line") else X.H - 140
        if p.get("host"): y0 = max(y0, 520)          # the host sits top-right in 9:16
    else:
        x0, x1 = 96, X.W - 96
        y0 = 118 if p.get("line") else 70
        y1 = X.H - (_cap_clear(X, p) + 30 if p.get("line") else 70)
    if pad: x0 += pad; x1 -= pad; y0 += pad; y1 -= pad
    return x0, y0, x1 - x0, y1 - y0


def items(v, keys_a=("text", "title", "name", "label", "a"), keys_b=("sub", "desc", "note", "b")):
    """"a|b" · ["a", "b"] · [["a", "sub"]] · [{"text": "a", "sub": "…"}] → [(text, sub)]."""
    out = []
    for it in fit.as_list(v):
        if isinstance(it, dict):
            a = next((it[k] for k in keys_a if it.get(k) not in (None, "")), "")
            b = next((it[k] for k in keys_b if it.get(k) not in (None, "")), "")
            out.append((str(a), str(b)))
        elif isinstance(it, (list, tuple)):
            out.append((str(it[0]) if it else "", str(it[1]) if len(it) > 1 and it[1] is not None else ""))
        else:
            s = str(it)
            a, sep, b = s.partition("：") if "：" in s else s.partition("::")
            out.append((a, b) if sep and b else (s, ""))
    return out


def fitpx(texts, w, h, max_px, min_px, max_lines=2, lh=1.18):
    """the largest size at which every text fits w × h; returns (px, [Fit per text at that px])."""
    texts = [t for t in texts] or [""]
    px = min(fit.fit_text(t, w, h, max_px, min_px, lh=lh, max_lines=max_lines).px for t in texts)
    return px, [wrap_at(t, w, px, max_lines) for t in texts]


def wrap_at(text, w, px, max_lines=2):
    """lines for `text` at exactly `px`: the fewest balanced lines that fit w; ellipsis only past max_lines."""
    for n in range(1, max_lines + 1):
        f = fit.fit_text(text, w, 1e6, px, px, max_lines=n)
        cut = any(fit.plain(l).endswith("…") for l in f.lines) and not fit.plain(text).endswith("…")
        if not cut and f.px >= int(px) and all(fit.width(l) * px <= w * 0.97 for l in f.lines):
            return fit.Fit(int(px), f.lines, f.em)
    f = fit.fit_text(text, w, 1e6, px, px, max_lines=max_lines)
    return fit.Fit(int(px), f.lines, f.em)


def lines(X, f, cls="sl"):
    return "".join(f'<span class="{cls}">{X.rich(l)}</span>' for l in f.lines)


def beats(X, p, t, d, n, start=0.3, share=0.62):
    """landing time of each of n items."""
    at = fit.as_list(p.get("at"))
    if at and X.chars:
        out = []
        for k in range(n):
            try: out.append(float(X.T(at[k], t)) if k < len(at) else None)
            except SystemExit: out.append(None)
        if all(x is not None for x in out): return out
    step = max(0.12, d * share / max(n, 1))
    return [t + start + k * step for k in range(n)]


def num(v):
    try: return float(str(v).replace(",", ""))
    except (TypeError, ValueError): return None


def col(X, p, key):
    """a theme colour as a literal (GSAP can tween hex, not var(--x))."""
    th = THEMES.get(p.get("theme")) or {}
    tok = X.S.get("tokens", {})
    v = th.get(key) or tok.get(key) or {"bg": "#121212", "fg": "#f3efe6", "accent": "#f6ce3a", "muted": "#958f85"}.get(key, "#888")
    return v


def flat(v):
    """list items as single strings ("要点：说明" kept whole) — for effects that show one text per item."""
    return [f"{a}：{b}" if b else a for a, b in items(v)]


def place_labels(cands, obstacles, W, H):
    """greedy label placement: cands = [[(x, y, w, h), ...options in preference order], ...] → chosen boxes (index per label).
    Avoids the obstacles and already placed labels; falls back to the least-overlapping option."""
    def ov(a, b):
        return max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])) * max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    placed, out = list(obstacles), []
    m = W * 0.04                                  # labels keep a margin from the left / right edge of the frame
    for opts in cands:
        best, bi = None, 0
        for i, r in enumerate(opts):
            inside = r[0] >= m and r[1] >= 0 and r[0] + r[2] <= W - m and r[1] + r[3] <= H
            cost = sum(ov(r, q) for q in placed) + (0 if inside else 1e9)
            if best is None or cost < best: best, bi = cost, i
            if cost == 0: break
        out.append(bi); placed.append(opts[bi])
    return out
