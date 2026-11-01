"""shared helpers for the W2 text & emphasis effects (text_pages, question_card, vertical_title, flying_words,
number_pages, combo, black_slam, scribble, scanline). Not an effect.

sentences(): a paragraph → sentences (CJK and Latin punctuation, keeps the mark). is_rtl() / measure(): Arabic and
Hebrew run right-to-left and are about half a CJK glyph wide, so they are measured on a proxy string. numbers():
every number in a sentence with its unit and the words before it. rough(): seeded hand-drawn SVG strokes (circle,
cross, strike, underline, arrow, scrawl, check, box) with their length for a draw-on. counter(): a deterministic
count-up that keeps the original decimals and thousands separators.
"""
import math, re
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

END = "。！？!?；;…"
RTL = re.compile(r"[֐-ࣿיִ-﷿ﹰ-﻿]")


def sentences(text):
    """paragraph → sentences, each keeping its closing mark (。！？; Latin '. ' too)."""
    s = re.sub(r"\s*\n+\s*", "\n", str(text or "").strip())
    out, cur = [], ""
    for i, ch in enumerate(s):
        cur += ch
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if ch == "\n" or ch in END and nxt not in "”」』）)" or ch in ".!?" and nxt in (" ", "") and not re.search(r"\d\.$", cur[-3:]):
            if cur.strip(): out.append(cur.strip())
            cur = ""
        elif ch in "”」』）)" and cur[-2:-1] in END:
            out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    return out


def is_rtl(text): return bool(RTL.search(str(text or "")))


def proxy(text):
    """measuring stand-in: RTL glyphs are about half a CJK glyph wide (fit.gw counts them as 1)."""
    return RTL.sub("a", str(text or ""))


def fit_any(text, w, h, max_px, min_px, max_lines=3, lh=1.12):
    """fit.fit_text, but measured on the proxy for right-to-left scripts; returns (px, n_lines)."""
    f = fit.fit_text(proxy(text), w, h, max_px, min_px, lh=lh, max_lines=max_lines)
    return f.px, f.n


NUM = re.compile(r"([+\-−]?)(\d[\d,]*(?:\.\d+)?)\s*(%|％|亿元|億元|亿杯|億杯|亿人|億人|亿|億|万家|萬家|万辆|萬輛|万人|萬人|万|萬|千|家|元|美元|杯|倍|个|個|人|天|年|辆|輛|次|小时|小時|分钟|分鐘|秒|km|公里|TEU)?")


def _year(m):
    """'2024 年' is a date, not a figure: kept as words (the label of the next number)."""
    return m.group(3) == "年" and not m.group(1) and re.fullmatch(r"(19|20)\d\d", m.group(2)) is not None


def numbers(text):
    """[(label, sign, digits, unit)] for every number in the sentence; label = the words just before it."""
    s = str(text or "")
    out, last = [], 0
    for m in NUM.finditer(s):
        if _year(m):
            if not out and m.start() < 3: last = m.end()     # a leading year is context for the whole sentence
            continue
        pre = s[last:m.start()]
        pre = re.split(r"[，,。；;：:、！？]", pre)[-1].strip()
        pre = re.sub(r"^(其中|以及|和|与|及|而|还有|共|另外)", "", pre).strip() or (out[-1][0] if out else "")
        out.append((pre[-12:], m.group(1).replace("−", "-"), m.group(2), m.group(3) or ""))
        last = m.end()
    return out


def mark_numbers(text):
    """HTML of the sentence with each number that numbers() returns wrapped in <span class="n" data-k=i>."""
    from h9.core import esc
    s = str(text or ""); out, last, k = [], 0, 0
    for m in NUM.finditer(s):
        out.append(esc(s[last:m.start()]))
        if _year(m):
            out.append(esc(m.group(0)))
        else:
            out.append(f'<span class="n" data-k="{k}">{esc(m.group(0))}</span>'); k += 1
        last = m.end()
    out.append(esc(s[last:]))
    return "".join(out)


def counter(X, sel, t, digits, dur=0.7, sign=""):
    """count up to `digits` (a string like '46,479' or '44.5') keeping its decimals and separators."""
    raw = digits.replace(",", "")
    dec = len(raw.split(".")[1]) if "." in raw else 0
    sep = "," in digits
    v = float(raw)
    js = f"o.v.toLocaleString('en-US', {{minimumFractionDigits:{dec}, maximumFractionDigits:{dec}}})" if sep else f"o.v.toFixed({dec})"
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{v}, duration:{dur:.2f}, ease:"power3.out", '
         f'onUpdate:()=>{{el.textContent="{sign}"+{js};}}}}, {t:.3f});}})();')


# ---------------------------------------------------------------- hand-drawn strokes
def _wob(rand, a): return rand.uniform(-a, a)


def _poly(pts):
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1, 2):
        (cx, cy), (x, y) = pts[i], pts[i + 1]
        d += f" Q{cx:.1f} {cy:.1f} {x:.1f} {y:.1f}"
    if len(pts) % 2 == 0: d += f" L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"
    return d


def _len(pts): return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) * 1.04


def rough(kind, x, y, w, h, rand, wob=None):
    """→ [(path_d, length)] strokes for a hand-drawn mark around/over the box (x, y, w, h)."""
    wob = wob if wob is not None else max(3.0, min(w, h) * 0.06)
    cx, cy = x + w / 2, y + h / 2
    out = []
    if kind == "circle":
        rx, ry = w / 2 + wob * 2.2, h / 2 + wob * 1.8
        a0 = rand.uniform(-2.6, -2.0); turns = rand.uniform(1.12, 1.28); n = 44
        pts = []
        for k in range(n + 1):
            a = a0 + 2 * math.pi * turns * k / n
            g = 1 + 0.06 * math.sin(a * 2.3 + a0) + (0.05 * k / n)
            pts.append((cx + rx * g * math.cos(a) + _wob(rand, wob * 0.3), cy + ry * g * math.sin(a) + _wob(rand, wob * 0.3)))
        out.append(pts)
    elif kind == "box":
        p = [(x - wob, y - wob), (x + w + wob, y - wob * 0.5), (x + w + wob * 0.6, y + h + wob), (x - wob * 0.7, y + h + wob * 0.8), (x - wob * 1.2, y - wob * 1.6)]
        pts = []
        for i in range(len(p) - 1):
            for k in range(6):
                f = k / 6
                pts.append((p[i][0] + (p[i + 1][0] - p[i][0]) * f + _wob(rand, wob * 0.25), p[i][1] + (p[i + 1][1] - p[i][1]) * f + _wob(rand, wob * 0.25)))
        pts.append(p[-1]); out.append(pts)
    elif kind in ("strike", "underline"):
        yy = cy if kind == "strike" else y + h + wob * 0.8
        for pas in range(2 if kind == "strike" else 1):
            n = 14; pts = []
            for k in range(n + 1):
                f = k / n
                wave = math.sin(f * math.pi * (5 if kind == "underline" else 2)) * wob * (0.7 if kind == "underline" else 0.25)
                pts.append((x - wob + (w + 2 * wob) * f, yy + wave + pas * wob * 0.9 + _wob(rand, wob * 0.2) - f * wob * 0.4 * (1 - 2 * pas)))
            out.append(pts if pas == 0 else pts[::-1])
    elif kind == "cross":
        for (ax, ay, bx, by) in ((x, y, x + w, y + h), (x + w, y, x, y + h)):
            n = 10; pts = []
            for k in range(n + 1):
                f = k / n
                pts.append((ax + (bx - ax) * f + _wob(rand, wob * 0.3), ay + (by - ay) * f + _wob(rand, wob * 0.3)))
            out.append(pts)
    elif kind == "scrawl":
        rows = max(3, int(h / max(8.0, wob * 2.2))); pts = []
        for r in range(rows + 1):
            yy = y + h * r / rows
            pts.append((x + (0 if r % 2 == 0 else w) + _wob(rand, wob), yy + _wob(rand, wob * 0.5)))
            pts.append((x + (w if r % 2 == 0 else 0) + _wob(rand, wob), yy + h / rows * 0.5 + _wob(rand, wob * 0.5)))
        out.append(pts)
    elif kind == "check":
        pts = [(x, y + h * 0.55), (x + w * 0.18, y + h * 0.72), (x + w * 0.36, y + h * 1.0), (x + w * 0.6, y + h * 0.5), (x + w * 0.82, y + h * 0.15), (x + w, y)]
        out.append([(px + _wob(rand, wob * 0.3), py + _wob(rand, wob * 0.3)) for px, py in pts])
    elif kind == "arrow":      # (x, y) → (x+w, y+h): a bowed stroke and a two-flick head
        ax, ay, bx, by = x, y, x + w, y + h
        nx, ny = -(by - ay), (bx - ax)
        L = math.hypot(nx, ny) or 1
        bow = 0.22 * math.hypot(bx - ax, by - ay)
        n = 16; pts = []
        for k in range(n + 1):
            f = k / n
            bend = math.sin(f * math.pi) * bow
            pts.append((ax + (bx - ax) * f + nx / L * bend + _wob(rand, wob * 0.2), ay + (by - ay) * f + ny / L * bend + _wob(rand, wob * 0.2)))
        out.append(pts)
        dx, dy = pts[-1][0] - pts[-3][0], pts[-1][1] - pts[-3][1]
        a = math.atan2(dy, dx); hl = max(14.0, min(46.0, math.hypot(bx - ax, by - ay) * 0.14))
        for s_ in (-1, 1):
            out.append([(bx, by), (bx - hl * math.cos(a + s_ * 0.5) + _wob(rand, 2), by - hl * math.sin(a + s_ * 0.5) + _wob(rand, 2))])
    return [(_poly(p), _len(p)) for p in out]


def text_box(X, f, cx, top, target, lh):
    """approximate px box of `target` inside centred fitted lines f (for marking words of a headline)."""
    for li, l in enumerate(f.lines):
        pl = fit.plain(l); i = pl.find(target)
        if i < 0: continue
        lw = fit.width(pl) * f.px
        x0 = cx - lw / 2 + fit.width(pl[:i]) * f.px
        return (x0, top + li * f.px * lh + f.px * (lh - 1) / 2, fit.width(target) * f.px, f.px)
    return None
