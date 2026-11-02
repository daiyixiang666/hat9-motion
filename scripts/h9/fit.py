"""fit — make effects and scenes take any realistic input and still look designed.

Everything here is computed at build time (no browser): glyph widths are estimated per character class,
so a text's width in em is known before layout and the font size can be chosen to fill a box.

  fit_text(text, box_w, box_h, max_px, min_px)  -> Fit(px, lines)   shrink → wrap (balanced, by words) → ellipsis
  grid(n, box_w, box_h, item_ar)                -> (cols, rows)      the grid that gives every item the most area
  scatter(n, portrait, rand)                    -> [(x%, y%, w%, rot)] loose collage positions for 1–8 pieces
  media(X, cid, key, src, t, d, cls)            -> (html, selector)  <img> inline, or a properly timed <video>
  fmt_num(v)                                    -> "4.6万" / "12,000" / "-3.5"
  as_list / as_pairs / as_text                  -> parameters given as a string, a list or nothing

Text markup is the house one: *强调* and | (forced line break); both survive line breaking.
"""
import math, re, subprocess
from dataclasses import dataclass
from pathlib import Path

CLOSE = set("，。、；：！？）》」』”’,.;:!?)]}%…—·・")      # never starts a line
OPEN = set("（《「『“‘([{")                               # never ends a line
VIDEO = {".mp4", ".mov", ".webm", ".m4v"}


# ---------------------------------------------------------------- parameters
def as_list(v, sep="|"):
    """None → [];  "a|b" → ["a","b"];  ["a","b"] → same;  3 → ["3"]."""
    if v is None or v == "": return []
    if isinstance(v, (list, tuple)): return [x for x in v if x is not None and x != ""]
    if isinstance(v, str): return [s for s in v.split(sep)] if sep and sep in v else [v]
    return [v]


def as_text(v, joiner="|"):
    if v is None: return ""
    if isinstance(v, (list, tuple)): return joiner.join(str(x) for x in v)
    return str(v)


def as_pairs(items, keys=(("app", "title", "name", "a"), ("text", "msg", "sub", "b"))):
    """notification-like items: "抖音：播放破 10 万" | ["抖音", "…"] | {"app": "抖音", "text": "…"} → [(a, b)]."""
    out = []
    for it in as_list(items):
        if isinstance(it, dict):
            a = next((it[k] for k in keys[0] if k in it), ""); b = next((it[k] for k in keys[1] if k in it), "")
        elif isinstance(it, (list, tuple)):
            a, b = (list(it) + ["", ""])[:2]
        else:
            m = re.split(r"[：:]", str(it), maxsplit=1)
            a, b = (m[0], m[1]) if len(m) == 2 else ("", m[0])
        out.append((str(a).strip(), str(b).strip()))
    return out


# ---------------------------------------------------------------- measuring
def gw(ch, mono=False):
    """estimated advance of one glyph in em (CJK = 1)."""
    o = ord(ch)
    if mono: return 1.0 if o > 0x2e7f else 0.6
    if ch in "  ": return 0.28
    if o < 128:
        if ch in "il.,:;'|!`": return 0.3
        if ch in "mwMW@%": return 0.86
        if ch.isupper() or ch.isdigit(): return 0.64
        return 0.54
    if 0x2000 <= o < 0x2070: return 0.6 if ch not in "—…" else 1.0
    if 0xff61 <= o <= 0xffdc: return 0.5            # halfwidth forms
    if 0x0590 <= o < 0x0900 or 0xfb1d <= o < 0xfe00 or 0xfe70 <= o < 0xff00: return 0.55   # Hebrew / Arabic (joined letters)
    return 1.0


def plain(s):
    return re.sub(r"[*|]", "", str(s))


def width(s, mono=False):
    return sum(gw(c, mono) for c in plain(s))


def _parse(text):
    """markup → (segments, emmask): segments split at |, emmask[i] for every char of the joined plain text."""
    segs, cur, mask, em = [], [], [], False
    for ch in str(text):
        if ch == "*": em = not em; continue
        if ch == "|": segs.append("".join(cur)); cur = []; continue
        cur.append(ch); mask.append(em)
    segs.append("".join(cur))
    return segs, mask


def tokens(s):
    """words that must not be split (jieba when installed, Latin/number runs whole), punctuation glued on."""
    try:
        import jieba, logging
        jieba.setLogLevel(logging.WARNING)
        raw = list(jieba.cut(s))
    except ImportError:
        raw = re.findall(r"[A-Za-z0-9%.,+\-]+|\s+|[^A-Za-z0-9%.,+\-\s]{1,2}", s)
    out = []
    for tk in raw:
        if not tk: continue
        if tk[0] in CLOSE and len(out) > 1 and out[-1].isspace():
            sp = out.pop(); out[-1] += sp + tk            # "第二章 · 供应链": the dot stays with the word before it
        elif out and (tk[0] in CLOSE or out[-1][-1:] in OPEN):
            out[-1] += tk
        else:
            out.append(tk)
    return out


def _break(seg, n, mono=False):
    """balanced greedy split of one segment into ≤ n lines, never inside a token."""
    toks = tokens(seg)
    if n <= 1 or len(toks) <= 1: return [seg]
    total = sum(width(t, mono) for t in toks)
    target = total / n
    lines, cur, cw = [], "", 0.0
    for i, tk in enumerate(toks):
        w = width(tk, mono)
        left = n - len(lines) - 1
        soft = cur[-1:] in "，。；！？、,;!?" and cw >= target * 0.7          # prefer breaking after a clause
        if cur and left > 0 and (soft or (cw + w > target and abs(cw - target) <= abs(cw + w - target))):
            lines.append(cur); cur, cw = "", 0.0
        cur += tk; cw += w
    lines.append(cur)
    return [l.strip() if not mono else l for l in lines if l.strip()] or [seg]


def _remark(lines, flat, mask):
    """put the *em* markers back into broken lines (closed at each line end, reopened on the next).
    Lines may have lost boundary spaces or gained an ellipsis, so characters are re-aligned to the source."""
    out, j = [], 0
    for ln in lines:
        s, em = "", False
        for ch in ln:
            k = j
            while k < len(flat) and flat[k] != ch: k += 1
            m = False
            if k < len(flat): m = mask[k]; j = k + 1
            if m != em: s += "*"; em = m
            s += ch
        if em: s += "*"
        out.append(s)
    return out


@dataclass
class Fit:
    px: int
    lines: list           # markup strings (may hold *em*)
    em: float             # widest line in em

    @property
    def n(self): return len(self.lines)


def fit_text(text, box_w, box_h, max_px, min_px=None, lh=1.12, max_lines=3, mono=False, ls=0.0):
    """the biggest size ≤ max_px at which `text` fits box_w × box_h, choosing 1…max_lines balanced lines.
    Past min_px it wraps to max_lines at min_px, then ellipsizes the last line (only then)."""
    segs, mask = _parse(text)
    min_px = min_px or max(12, max_px * 0.25)
    flat = [c for s in segs for c in s]
    best = None
    for n in range(len(segs), max(len(segs), max_lines) + 1):
        k = [1] * len(segs)                      # lines per forced segment; give extra lines to the widest
        while sum(k) < n:
            j = max(range(len(segs)), key=lambda q: width(segs[q], mono) / k[q]); k[j] += 1
        lines = [l for s, kk in zip(segs, k) for l in _break(s, kk, mono)]
        wem = max(width(l, mono) + ls * len(plain(l)) for l in lines) or 1
        px = min(max_px, box_w * 0.96 / wem, box_h / (len(lines) * lh))
        if best is None or px > best[0] * 1.25:   # one more line has to buy a clearly bigger size
            best = (px, lines, wem)
    px, lines, wem = best
    if px < min_px:
        px = min_px
        room = box_w * 0.96 / px
        if wem > room and lines:                  # last resort: ellipsize the overflowing lines
            fixed = []
            for l in lines:
                if width(l, mono) <= room: fixed.append(l); continue
                cut = ""
                for ch in l:
                    if width(cut + ch + "…", mono) > room: break
                    cut += ch
                fixed.append(cut.rstrip() + "…")
            lines = fixed
            wem = max(width(l, mono) for l in lines)
    marked = _remark([plain(l) for l in lines], flat, mask) if any(mask) else [plain(l) for l in lines]
    return Fit(int(px), marked, wem)


def vmin(X, v): return min(X.W, X.H) * v / 100


# ---------------------------------------------------------------- layouts
def grid(n, box_w, box_h, item_ar=1.0, gap=0.0):
    """(cols, rows) for n items of aspect item_ar (w/h) in a box, maximising each item's area."""
    n = max(1, int(n)); best = (0, 1, n)
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        cw = (box_w - gap * (cols - 1)) / cols; ch = (box_h - gap * (rows - 1)) / rows
        if cw <= 0 or ch <= 0: continue
        w = min(cw, ch * item_ar); area = w * (w / item_ar)
        empty = cols * rows - n
        score = area * (1 - 0.04 * empty)
        if score > best[0]: best = (score, cols, rows)
    return best[1], best[2]


def list_cols(n, portrait):
    """columns for a list of n short items (chips, icons, stats)."""
    if portrait: return 1 if n <= 4 else 2
    return n if n <= 4 else math.ceil(n / 2)


def scatter(n, portrait, rand, ars=None, frame_ar=None):
    """loose collage: n pieces as (x%, y%, w%, rot°) of the frame — a designed stagger for 1–3, a jittered grid
    beyond; each piece keeps its own aspect (ars, w/h) and sits centred in its cell. Up to 9 pieces."""
    n = max(1, min(int(n), 9))
    ars = (list(ars) + [1.5] * n)[:n] if ars else [1.5] * n
    far = frame_ar or (9 / 16 if portrait else 16 / 9)
    hpct = lambda w, ar: w * far / ar                       # piece height in % of frame height
    if n <= 3 and not portrait:
        base = {1: [(50, 50, 46)], 2: [(34, 46, 40), (66, 54, 38)], 3: [(31, 36, 34), (61, 30, 30), (47, 68, 36)]}[n]
    elif n <= 3:
        base = {1: [(50, 48, 80)], 2: [(42, 36, 70), (58, 64, 66)], 3: [(38, 30, 62), (62, 50, 58), (44, 72, 64)]}[n]
    else:
        cols, rows = grid(n, 84, 64 * (1 / far), sum(ars) / n, gap=3)
        cw, ch = 84 / cols, 64 / rows
        base = []
        for k in range(n):
            r, c = divmod(k, cols)
            inrow = min(cols, n - r * cols)
            cx = (100 - inrow * cw) / 2 + (c + 0.5) * cw
            cy = 18 + (r + 0.5) * ch
            base.append((cx, cy, cw * 0.98))
    out = []
    for k, (cx, cy, w) in enumerate(base):
        ar = ars[k]
        h = hpct(w, ar)
        lim = {1: 72, 2: 60, 3: 50}.get(n) or 62 / max(1, math.ceil(n / max(1, round(math.sqrt(n * far)))))
        if h > lim: w = w * lim / h; h = lim                 # tall pieces get narrower, not taller than their cell
        x = cx - w / 2 + rand.uniform(-1.8, 1.8); y = cy - h / 2 + rand.uniform(-1.5, 1.5)
        x = min(max(x, 3), 97 - w); y = min(max(y, 13), 92 - h)
        out.append((round(x, 1), round(y, 1), round(w, 1), round(rand.choice([-1, 1]) * rand.uniform(2, 6.5), 1)))
    return out


# ---------------------------------------------------------------- numbers
def fmt_num(v, zh=True, dec=None):
    """12000 → "1.2万" (zh) or "12,000";  -3.5 → "-3.5";  4.45e9 → "44.5亿";  strings pass through."""
    if isinstance(v, str):
        try: v = float(v.replace(",", ""))
        except ValueError: return v
    neg = v < 0; a = abs(float(v))
    if zh and a >= 1e8: s = f"{a / 1e8:.{1 if dec is None else dec}f}".rstrip("0").rstrip(".") + "亿"
    elif zh and a >= 1e4: s = f"{a / 1e4:.{1 if dec is None else dec}f}".rstrip("0").rstrip(".") + "万"
    elif a == int(a) and dec is None: s = f"{int(a):,}"
    else: s = f"{a:,.{2 if dec is None else dec}f}".rstrip("0").rstrip(".")
    return ("-" if neg else "") + s


def nice_unit(a, b=0, lo=40, hi=640):
    """a dot/tick unit (1, 2, 5 × 10^k) so max(a, b)/unit lands between lo and hi."""
    m = max(abs(a), abs(b), 1)
    for e in range(0, 13):
        for f in (1, 2, 5):
            u = f * 10 ** e
            if m / u <= hi: return u
    return 10 ** 12


# ---------------------------------------------------------------- media
_SIZE, _DUR = {}, {}


def is_video(src): return bool(src) and Path(str(src)).suffix.lower() in VIDEO


def size(path):
    """(w, h) of an image or video, or None."""
    p = str(path)
    if p in _SIZE: return _SIZE[p]
    r = None
    try:
        if is_video(p):
            o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", p], text=True).strip()
            w, h = o.split(",")[:2]; r = (int(w), int(h))
        else:
            from PIL import Image
            with Image.open(p) as im: r = im.size
    except Exception:
        r = None
    _SIZE[p] = r
    return r


def duration(path):
    p = str(path)
    if p not in _DUR:
        try: _DUR[p] = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], text=True).strip())
        except Exception: _DUR[p] = 0.0
    return _DUR[p]


def _abs(X, src):
    p = Path(str(src))
    return p if p.is_absolute() else X.src / p


def aspect(X, src, default=1.5):
    s = size(_abs(X, src))
    return (s[0] / s[1]) if s and s[1] else default


def focus_css(f):
    """"30% 40%" | [30, 40] | {"x":30,"y":40} | None → an object-position value."""
    if f is None: return "50% 50%"
    if isinstance(f, (list, tuple)): return f"{f[0]}% {f[1]}%"
    if isinstance(f, dict): return f"{f.get('x', 50)}% {f.get('y', 50)}%"
    return str(f)


_TRACK = [60]


def media(X, cid, key, src, t, d, cls, focus=None, box_ar=None, fill="auto", z=2, start=0.0, extra_style=""):
    """one picture for an effect, any aspect, still or moving.
    Still → (inline <img>, '#cid .cls'); an extreme aspect against the box gets a blurred fill behind a contained copy.
    Video → ('', '#cid_key'): an untimed full-frame wrapper (animate THAT) holding a timed <video>, placed as a root
    sibling under the effect clip (HyperFrames only seeks timed media, and a timed video may not sit inside a timed clip)."""
    if not src: return "", None
    pos = focus_css(focus)
    box_ar = box_ar or X.W / X.H
    if is_video(src):
        url = X.asset(src, "video")
        dur = duration(_abs(X, src)) or d
        ms = min(max(0.0, float(start)), max(0.0, dur - d)) if dur > d else 0.0
        _TRACK[0] += 1
        wid = f"{cid}_{key}"
        X.els.append(f'<div id="{wid}" class="fxv {cls}" style="position:absolute; inset:0; overflow:hidden; z-index:{z}; pointer-events:none; {extra_style}">'
                     f'<video id="{wid}v" class="clip" src="{url}" muted playsinline data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="{_TRACK[0]}" '
                     f'data-media-start="{ms:.3f}" style="width:100%; height:100%; object-fit:cover; object-position:{pos}"></video></div>')
        return "", f"#{wid}"
    url = X.asset(src)
    ar = aspect(X, src)
    extreme = fill == "contain" or (fill == "auto" and max(ar / box_ar, box_ar / ar) > 3.4)   # a 16:9 photo in 9:16 still crops
    if extreme:
        X.css("fit-mfill", ".mfill { position:absolute; inset:0; overflow:hidden; } .mfill .mb { position:absolute; inset:-6%; width:112%; height:112%; object-fit:cover; filter:blur(40px) saturate(1.1) brightness(.7); } .mfill .mc { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; }")
        return (f'<div class="{cls} mfill" style="{extra_style}"><img class="mb" src="{url}" alt="" data-layout-allow-overflow><img class="mc" src="{url}" alt="" style="object-position:{pos}"></div>',
                f"#{cid} .{cls.split()[0]}")
    return f'<img class="{cls}" src="{url}" alt="" style="object-position:{pos}; {extra_style}">', f"#{cid} .{cls.split()[0]}"


_WRAP = re.compile(r'<div id="([^"]+)" class="fxv[ "].*?<video id="\1v" [^>]*?data-start="([\d.]+)" data-duration="([\d.]+)"', re.S)


def scope_media(X):
    """the untimed video wrappers made by media() live all film; hide each one outside its video's window, so a painted
    card (shadow, plate, border) does not show through later beats. build.py calls this once after the last beat,
    outside the elastic / rate wraps, so the hide lands exactly when the video ends."""
    for el in X.els:
        m = _WRAP.match(el)
        if not m: continue
        wid, t, d = m.group(1), float(m.group(2)), float(m.group(3))
        X.css(f"fit-scope-{wid}", f"#{wid} {{ visibility:hidden; }}")
        X.tw(f'tl.set("#{wid}", {{visibility:"visible"}}, {t:.3f}); tl.set("#{wid}", {{visibility:"hidden"}}, {t + d:.3f});')


def bg_css(X, src, focus=None):
    """a CSS background value for a still (tiles, match-cut grounds)."""
    return f"url({X.asset(src)}) {focus_css(focus)}/cover"


def seeded_order(n, rand):
    """a deterministic shuffled stagger order (replaces GSAP's from:'random', which is not seed-stable)."""
    order = list(range(n)); rand.shuffle(order)
    rank = [0] * n
    for pos, i in enumerate(order): rank[i] = pos
    return rank
