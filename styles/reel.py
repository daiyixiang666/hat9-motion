"""reel · 动效库默认 —— broadcast-grade default: big type on a strict grid, one orange accent, and always a second layer moving.

Ground is warm black #121110 with two slow diagonal light sweeps (#1d1b19, 900 px wide, drifting 40 px/s) and 5 % grain.
A 12-column grid (margins 80 px, gutter 20 px) is implied; it shows only as four small registration crosses at the
safe-area corners. Type: Noto Sans SC 900 for Chinese headlines (leading 1.08), Inter 900 tabular for numerals,
JetBrains Mono for labels, one italic serif (EB Garamond) only for small English kickers. Orange #ff5a1f marks exactly
one element per beat (a word, a bar, a numeral) plus the caption's key word.

9:16 composition (1080 × 1920): kicker row y 220–262 (orange square + topic on the left, "03/08" on the right);
headline zone y 300–760, left-aligned at x 80, each line revealed by a mask from below (9 frames, 2-frame stagger),
the accent word underlined by an orange bar that wipes left to right after the line lands; evidence zone y 800–1300,
x 80–1000, the beat's figure as large flat shapes; caption y 1380–1456 (46 px / 800, off-white, a 2 px black drop,
the key word orange) over a gradient to 85 % ground; source y 1474–1506 (22 px, muted); below y 1520 a row of
oversized outline numerals of the beat (2 px #2a2826, 420 px tall) scrolls slowly left: texture, not text.
16:9: headline in the left 46 %, evidence in the right 50 %, caption bottom centre.

Scenes (same names as the shared ones, so every old film picks them up; old parameters keep working):
title · number (bar or 10×10 dots) · compare (value panels, or two pictures) · statement · quote · outro,
plus rank (bars racing to true length) · split (one segmented bar breaking into a column) · trend (thick line + area).
Beat transitions: hard cut into even beats, a 5-frame whip (140 px slide + blur) into odd beats; the title ends on a
4-frame orange flash wipe. Hold motion: the evidence zone pushes 1.00 → 1.03, the sweeps drift, the outline row scrolls.
"""
import math
import re

from h9 import fit

BG, FG, MUTED, ACC, LINE, SWEEP, CARD = "#121110", "#f2ede4", "#8a847a", "#ff5a1f", "#2a2826", "#1d1b19", "#1b1a18"
GREY, GREY2 = "#3a3632", "#5a554e"

STYLE = {
    "name": "动效库默认", "en": "FX Reel", "benchmarks": ["broadcast news graphics packages", "Swiss grid typography", "sports data overlays"],
    "tokens": {"bg": BG, "fg": FG, "muted": MUTED, "accent": ACC, "accent2": ACC, "alert": ACC,
               "line": LINE, "paper": "#ece7dd", "ink": BG, "card": CARD, "card-fg": FG, "display-weight": "900",
               # caption: plain type, no plate — 46 px / 800 off-white, a 2 px black drop, the key word orange
               "cap-size": "46px", "cap-weight": "800", "cap-fg": FG, "cap-shadow": "0 2px 0 #000", "cap-em": ACC, "cap-bg": "none"},
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "latin": "eb-garamond-italic", "num": "inter", "hand": "ma-shan-zheng", "quote": "noto-serif-sc"},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static"},
    "layers": [("grain", {"opacity": 0.05})],
    "safe_exempt": [".rl-row", ".rl-rowbox", ".rl-reg", ".rl-gnum"],      # outline numeral rows and registration crosses are texture
    "sfx": {"transition": ("whoosh", 0.35), "pop": ("pop", 0.45), "enter": ("whoosh_soft", 0.35), "slam": ("slam", 0.5), "count": ("type", 0.35),
            "type": ("type", 0.4), "brush": ("brush", 0.5), "boing": ("boing", 0.45), "glitch": ("glitch", 0.45), "whoosh_soft": ("whoosh_soft", 0.35), "whoosh_deep": ("whoosh_deep", 0.4), "paper": ("paper", 0.45), "click": ("click", 0.3), "hit": ("hit", 0.5)},
}

F = 1 / 30
INTER = {"0": .64, "1": .46, "2": .62, "3": .64, "4": .66, "5": .63, "6": .64, "7": .58, "8": .64, "9": .64,
         ".": .27, ",": .27, "%": .9, "+": .62, "-": .42, " ": .25, "×": .6}


def nw(s):
    """Inter 900 advance of a numeral string in em (CJK counted at 1em)."""
    w = 0.0
    for c in str(s):
        w += INTER.get(c, 1.0 if ord(c) > 0x2e80 else 0.66)
    return w


CSS = r"""
.s-reel { background:var(--bg); }
.rl { position:absolute; inset:0; overflow:hidden; color:var(--fg); }
.rl .rl-sw { position:absolute; inset:0; overflow:hidden; }
.rl .rl-sw i { position:absolute; top:-50%; height:200%; width:900px; display:block;
  background:linear-gradient(90deg, rgba(29,27,25,0) 0%, rgba(29,27,25,.9) 35%, #1e1c1a 50%, rgba(29,27,25,.9) 65%, rgba(29,27,25,0) 100%); transform-origin:50% 50%; }
.rl .rl-media { position:absolute; inset:0; overflow:hidden; }
.rl .rl-media img, .rl .rl-media video { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; filter:brightness(.35) saturate(.85); }
.rl .rl-reg { position:absolute; left:0; top:0; overflow:visible; }
.rl .rl-row { position:absolute; left:0; }
.rl .rl-gnum { position:absolute; overflow:visible; }
.rl .rl-fade { position:absolute; left:0; right:0; }
.rl .rl-kick { position:absolute; display:flex; align-items:center; font-family:var(--f-mono); font-size:28px; letter-spacing:.08em; color:var(--fg); white-space:nowrap; }
.rl .rl-kick .sq { width:12px; height:12px; background:var(--accent); margin-right:16px; flex:none; }
.rl .rl-kick .kl { color:var(--fg); }
.rl .rl-kick .kc { position:absolute; right:0; color:var(--muted); }
.rl .rl-kick .kc b { color:var(--fg); font-weight:700; }
.rl .rl-hd { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); letter-spacing:-.01em; }
.rl .rl-hd .rlm { overflow:hidden; padding:.06em .1em .1em; margin:-.06em -.1em -.1em; }
.rl .rl-hd .li { white-space:nowrap; }
.rl .em .emb { left:0; right:0; bottom:-.04em; height:.09em; background:var(--accent); }
.rl .ac-color .em .emt { color:var(--accent); } .rl .ac-color .em .emb { display:none; }
.rl .ac-none .em .emb { display:none; }
.rl .rl-sub { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.3; white-space:nowrap; }
.rl .rl-ev { position:absolute; transform-origin:0 0; }
.rl .rl-src { position:absolute; font-family:var(--f-body); font-size:22px; font-weight:500; color:var(--muted); line-height:1.4; white-space:nowrap; letter-spacing:.02em; }
.rl .mono { font-family:var(--f-mono); letter-spacing:.06em; }
.rl .num { font-family:var(--f-num); font-weight:900; font-variant-numeric:tabular-nums; letter-spacing:-.02em; white-space:nowrap; line-height:1; }
.rl .lab { position:absolute; font-family:var(--f-display); font-weight:800; white-space:nowrap; line-height:1.2; }
.rl .abs { position:absolute; }
.rl .rl-flash { position:absolute; inset:0; background:var(--accent); visibility:hidden; }
.rl svg { display:block; overflow:visible; }
/* number */
.rl .hn { position:absolute; color:var(--fg); }
.rl .hn .u { font-family:var(--f-display); font-weight:900; letter-spacing:0; margin-left:.04em; }
.rl .streaks i { position:absolute; height:6px; background:var(--fg); opacity:0; display:block; border-radius:3px; }
.rl .pbar { position:absolute; background:var(--line); overflow:hidden; }
.rl .pbar b { position:absolute; top:0; bottom:0; display:block; transform-origin:0 50%; }
.rl .dots i { position:absolute; display:block; border-radius:50%; background:var(--line); }
.rl .dots i.on { background:var(--muted); } .rl .dots i.hl { background:var(--accent); }
/* compare */
.rl .pnl { position:absolute; background:var(--card); box-shadow:inset 0 0 0 2px var(--line); overflow:hidden; transform-origin:0 50%; }
.rl .pnl .pw { position:absolute; inset:0; }
.rl .pnl img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.rl .pnl .dim { position:absolute; inset:0; background:#000; opacity:0; }
.rl .pnl .chipl { position:absolute; left:28px; bottom:28px; background:var(--bg); color:var(--fg); font-family:var(--f-display); font-weight:900; font-size:44px; padding:6px 22px 8px; white-space:nowrap; }
.rl .pnl .stk { position:absolute; font-family:var(--f-display); font-weight:900; font-size:34px; color:var(--bg); background:var(--fg); padding:4px 14px 6px; white-space:nowrap; }
.rl .vs { position:absolute; width:124px; height:124px; border-radius:50%; background:var(--fg); color:var(--bg); font-family:var(--f-num); font-weight:900; font-size:46px;
  display:flex; align-items:center; justify-content:center; letter-spacing:-.02em; box-shadow:0 0 0 10px var(--bg); }
.rl .bar { position:absolute; display:block; transform-origin:0 50%; }
/* split / rank */
.rl .blk { position:absolute; display:block; }
.rl .blk .bn { position:absolute; left:22px; top:50%; transform:translateY(-50%); font-family:var(--f-display); font-weight:800; font-size:34px; white-space:nowrap; }
/* quote */
.rl .qmk { position:absolute; font-family:var(--f-latin); font-style:italic; color:var(--accent); line-height:1; }
.rl .qt { position:absolute; font-family:var(--f-quote); font-weight:900; color:var(--fg); line-height:1.25; }
.rl .qt .rlm { overflow:hidden; padding:.04em .1em .08em; margin:-.04em -.1em -.08em; } .rl .qt .li { white-space:nowrap; }
.rl .win { position:absolute; overflow:hidden; box-shadow:inset 0 0 0 2px var(--line); }
.rl .win img, .rl .win video { width:100%; height:100%; object-fit:cover; display:block; }
/* outro */
.rl .chip { position:absolute; height:72px; display:flex; align-items:center; padding:0 34px; background:var(--accent); color:var(--bg); font-family:var(--f-display); font-weight:900; font-size:36px; white-space:nowrap; }
.rl .stat .v { font-family:var(--f-num); font-weight:900; color:var(--fg); white-space:nowrap; line-height:1; letter-spacing:-.02em; }
.rl .stat .k { font-family:var(--f-body); font-weight:600; color:var(--muted); white-space:nowrap; margin-top:12px; }
"""


# ---------------------------------------------------------------- layout
def L(X):
    """the grid per aspect: margins, kicker row, headline zone, evidence zone, caption band, source, outline row."""
    if X.portrait:
        return {"P": True, "x": 80, "w": 920, "rx": 930, "kick": 220, "hy": 300, "hh": 460, "hw": 920,
                "ex": 80, "ey": 800, "ew": 920, "eh": 500, "band": 1160, "src": (80, 1474, 880),
                "row": (1520, 420), "hpx": 140, "scale": 1.0}
    return {"P": False, "x": 96, "w": 1728, "rx": 1824, "kick": 64, "hy": 168, "hh": 640, "hw": 820,
            "ex": 980, "ey": 168, "ew": 844, "eh": 720, "band": 760, "src": (96, 1006, 860),
            "row": (1046, 230), "hpx": 108, "scale": 0.8}


def _meta(X):
    return X.v.get("meta", {}) or {}


def _caps_on(X):
    """reel shows subtitle pages when the film has word timings, unless meta.captions is false (honoured here)."""
    if _meta(X).get("captions") is False:
        X.S["captions"] = False
    return bool(X.chars) and X.S.get("captions") is not False


def _beat_list(X):
    return X.v.get("beats", []) or []


def _next_is_reel(X, i):
    bs = _beat_list(X)
    j = i - int(_meta(X).get("beat_offset", 0)) + 1
    return 0 <= j < len(bs) and bs[j].get("scene") in SCENES


def fit_lines(text, w, h, max_px, min_px, max_lines, lh=1.08):
    return fit.fit_text(text, w, h, max_px, min_px, lh=lh, max_lines=max_lines)


def head_html(X, text, x, y, w, max_px, min_px=None, max_lines=3, accent="bar", lh=1.08, h=None, cls="rl-hd", extra=""):
    """a stack of masked lines (each line rises out of its own mask)."""
    f = fit_lines(text, w, h or max_lines * max_px * lh + 1, max_px, min_px or max_px * 0.5, max_lines, lh)
    rows = ""
    for ln in f.lines:
        rows += f'<div class="rlm"><div class="li">{X.rich(ln)}</div></div>'
    html = (f'<div class="{cls} ac-{accent}" data-layout-allow-overlap style="left:{x}px;top:{y}px;width:{w}px;'
            f'font-size:{f.px}px;line-height:{lh}{extra}">{rows}</div>')
    return html, f.n * f.px * lh, f


def reveal(X, sel, t0, n=1, underline=True):
    """mask reveal from below: 9 frames per line, 2-frame stagger; then the accent bar wipes left → right (8 frames)."""
    X.tw(f'tl.fromTo("{sel} .li", {{yPercent:112}}, {{yPercent:0, duration:{9 * F:.3f}, ease:"power3.out", stagger:{2 * F:.3f}}}, {t0:.3f});')
    if underline:
        X.tw(f'tl.fromTo("{sel} .emb", {{scaleX:0}}, {{scaleX:1, duration:{8 * F:.3f}, ease:"power2.inOut"}}, {t0 + 9 * F + 2 * F * max(0, n - 1) + 0.03:.3f});')


def wipe_in(X, sel, t, dur=0.35, stagger=0.0):
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{dur:.3f}, ease:"power3.out", stagger:{stagger}}}, {t:.3f});')


def rise_in(X, sel, t, dur=0.3, stagger=0.0):
    """clip from below (the line-mask verb for single elements)."""
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(100% 0% 0% 0%)", y:30}}, {{clipPath:"inset(0% 0% 0% 0%)", y:0, duration:{dur:.3f}, ease:"power3.out", stagger:{stagger}}}, {t:.3f});')


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def count(X, sel, t, v0, v1, dec=0, dur=0.9, sep=False):
    """a number that counts (tabular) — text set every frame."""
    fmt = f"o.v.toFixed({dec})"
    if sep:
        fmt = f"Number(o.v.toFixed({dec})).toLocaleString('en-US', {{minimumFractionDigits:{dec}, maximumFractionDigits:{dec}}})"
    X.tw(f'(()=>{{const o={{v:{v0}}}; const els=document.querySelectorAll("{sel}"); tl.to(o, {{v:{v1}, duration:{dur:.3f}, ease:"power3.out", '
         f'onUpdate:()=>{{els.forEach(e=>{{e.textContent={fmt};}});}}}}, {t:.3f});}})();')


def split_num(s):
    """'3938亿' → ('', 3938.0, 0, '亿'); '+59%' → ('+', 59.0, 0, '%'); '28.5' → ('', 28.5, 1, '')."""
    m = re.match(r"^\s*([+\-−]?)([\d,]*\.?\d+)(.*)$", str(s))
    if not m:
        return None
    num = m.group(2).replace(",", "")
    dec = len(num.split(".")[1]) if "." in num else 0
    return m.group(1), float(num), dec, m.group(3)


def outline_row(X, text, y, glyph, W, stroke=LINE, cls="rl-row", H=None):
    """oversized outline numerals / letters (texture, not text): an SVG picture of the numerals tiled along a strip,
    inside a box clipped to the frame below y. Drawn as an image so no checker reads it as overflowing copy."""
    from urllib.parse import quote
    px = glyph / 0.727
    unit = str(text) + "   "
    tw = nw(unit) * px
    svg = (f"<svg xmlns='http://www.w3.org/2000/svg' width='{tw:.0f}' height='{glyph + 40:.0f}'>"
           f"<text x='0' y='{glyph + 2:.0f}' font-family='Inter, Helvetica Neue, Helvetica, Arial, sans-serif' font-weight='900' "
           f"font-size='{px:.0f}' fill='none' stroke='{stroke}' stroke-width='2'>{unit.strip()}</text></svg>")
    uri = "url('data:image/svg+xml," + quote(svg, safe="") + "')"
    H = H or X.H
    bh = max(0, H - y)
    strip = (f'<div class="{cls}" aria-hidden="true" style="position:absolute;left:0;top:0;width:{tw * 6:.0f}px;height:{glyph + 40:.0f}px;'
             f'background-image:{uri};background-repeat:repeat-x;background-size:{tw:.0f}px {glyph + 40:.0f}px"></div>')
    return (f'<div class="rl-rowbox" data-safe="ignore" aria-hidden="true" style="position:absolute;left:0;top:{y:.0f}px;width:{W}px;height:{bh:.0f}px;overflow:hidden">'
            f'{strip}</div>'), tw


def reg_marks(X, l):
    """four tiny registration crosses at the safe-area corners (the only visible trace of the grid)."""
    if l["P"]:
        pts = [(80, 200), (1000, 200), (80, 1520), (1000, 1520)]
    else:
        pts = [(96, 40), (1824, 40), (96, 1040), (1824, 1040)]
    g = ""
    for x, y in pts:
        g += f'<path d="M{x - 12},{y} H{x + 12} M{x},{y - 12} V{y + 12}"/><circle cx="{x}" cy="{y}" r="5"/>'
    return f'<svg class="rl-reg" width="{X.W}" height="{X.H}"><g stroke="#3a3632" stroke-width="2" fill="none">{g}</g></svg>'


def default_outline(b):
    """the beat's oversized outline row: an explicit "outline", else the first figure in the beat, else its index."""
    if b.get("outline"):
        return str(b["outline"])
    for k in ("value", "big", "title", "text", "head"):
        v = b.get(k)
        if v is None:
            continue
        m = re.search(r"\d[\d.,]*", str(v))
        if m:
            return m.group(0)
    return None


# ---------------------------------------------------------------- the page
def page(X, b, cid, t, d, head="", ev="", over="", outline=None, media="", flash=False, push=True, cls=""):
    """one beat on the reel grid: ground + sweeps + registration crosses, optional media (darkened to 35 %), outline
    row, caption gradient, kicker row, evidence (pushes 1.00 → 1.03), headline, source; whip in on odd beats."""
    _caps_on(X)
    X.css("s-reel", CSS)
    l = L(X)
    W, H, P = X.W, X.H, X.portrait
    i, n = X.beat["i"], X.beat["n"]
    # sweeps: x = 40 px/s of film time, so they run on across cuts
    sw = ""
    for k in range(2):
        sw += f'<i class="s{k}" style="left:0;transform:rotate(24deg)"></i>'
    sw = f'<div class="rl-sw">{sw}</div>'
    row = ""
    otext = outline if outline is not None else default_outline(b)
    if otext:
        ry, rg = l["row"]
        row, _ = outline_row(X, otext, ry, rg, W)
    band = l["band"]
    fe = (1560 if P else H) - band
    fade = (f'<div class="rl-fade" style="top:{band}px;height:{fe}px;background:linear-gradient(180deg, rgba(18,17,16,0) 0px, '
            f'rgba(18,17,16,.85) 220px, rgba(18,17,16,.85) {fe - 60 if P else fe}px, rgba(18,17,16,0) 100%)"></div>')
    topic = b.get("kicker") or b.get("topic") or ""
    X.used_text.update(str(topic) + "0123456789/")
    kick = (f'<div class="rl-kick" style="left:{l["x"]}px;top:{l["kick"]}px;width:{(1000 if P else l["rx"]) - l["x"]}px;height:42px">'
            f'<i class="sq"></i><span class="kl">{X.rich(topic)}</span>'
            f'<span class="kc"><b>{i + 1:02d}</b>/{n:02d}</span></div>')
    src = b.get("src") or ""
    sx, sy, swid = l["src"]
    srch = ""
    if src:
        f = fit.fit_text(str(src), swid, 32, 22, 22, max_lines=1)
        srch = f'<div class="rl-src" style="left:{sx}px;top:{sy}px;max-width:{swid}px">{X.rich(f.lines[0] if f.lines else src)}</div>'
    fl = '<i class="rl-flash"></i>' if flash else ""
    html = (f'<div class="rl {cls}">{sw}{media}{reg_marks(X, l)}{fade}{row}'
            f'<div class="rl-ev" data-layout-allow-overlap style="left:0;top:0;width:{W}px;height:{H}px">{ev}</div>'
            f'{head}{over}{kick}{srch}{fl}</div>')
    X.clip(cid, t, d, html, f"scene s-reel {cls}", 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    for k in range(2):
        x0 = ((40 * t + k * 1100) % (W + 1800)) - 1100
        X.tw(f'tl.fromTo("{s} .rl-sw .s{k}", {{x:{x0:.1f}}}, {{x:{x0 + 40 * d:.1f}, duration:{d:.3f}, ease:"none"}}, {t:.3f});')
    if row:
        r0 = -((30 * t) % 900)
        X.tw(f'tl.fromTo("{s} .rl-row", {{x:{r0:.1f}}}, {{x:{r0 - 30 * d:.1f}, duration:{d:.3f}, ease:"none"}}, {t:.3f});')
    if media:
        X.tw(f'tl.fromTo("{s} .rl-media", {{scale:1.0}}, {{scale:1.05, duration:{d:.3f}, ease:"none"}}, {t:.3f});')
    if push:
        X.tw(f'tl.fromTo("{s} .rl-ev", {{scale:1.0}}, {{scale:1.03, transformOrigin:"{l["x"]}px {l["hy"]}px", duration:{d:.3f}, ease:"none"}}, {t:.3f});')
    # kicker: the square snaps, the topic wipes on, the counter's digits roll up
    X.tw(f'tl.from("{s} .rl-kick .sq", {{scale:0, duration:0.2, ease:"back.out(2.4)"}}, {t + 0.02:.3f});')
    wipe_in(X, f"{s} .rl-kick .kl", t + 0.06, 0.3)
    rise_in(X, f"{s} .rl-kick .kc", t + 0.06, 0.25)
    if src:
        wipe_in(X, f"{s} .rl-src", t + 0.5, 0.45)
    # whip: odd beats slide in from the right (5 frames, blurred), the beat before an odd beat slides out left
    if i % 2 == 1 and i > 0:
        X.tw(f'tl.fromTo("{s} > .stage", {{x:140, filter:"blur(16px)"}}, {{x:0, filter:"blur(0px)", duration:{5 * F:.3f}, ease:"power3.out"}}, {t:.3f});')
        X.sfx(t, "transition")
    if (i + 1) % 2 == 1 and i + 1 < n and not flash and _next_is_reel(X, i):
        X.tw(f'tl.to("{s} > .stage", {{x:-140, filter:"blur(16px)", duration:{3 * F:.3f}, ease:"power3.in"}}, {t + d - 3 * F:.3f});')
    if flash:     # 4-frame orange flash wipe across the frame at the end of the beat
        X.tw(f'tl.fromTo("{s} .rl-flash", {{xPercent:-101, visibility:"visible"}}, {{xPercent:0, duration:{2 * F:.3f}, ease:"none"}}, {t + d - 4 * F:.3f});')
        X.tw(f'tl.to("{s} .rl-flash", {{xPercent:101, duration:{2 * F:.3f}, ease:"none"}}, {t + d - 2 * F:.3f});')
        X.sfx(t + d - 4 * F, "transition")
    return s


def media_html(X, src):
    if not src:
        return ""
    if fit.is_video(src):
        return f'<div class="rl-media"><video src="{X.asset(src, "video")}" muted playsinline></video></div>'
    return f'<div class="rl-media"><img src="{X.asset(src)}" alt=""></div>'


# ---------------------------------------------------------------- scenes
def title(b, X, t, d, cid):
    """hook / chapter card: headline up to three lines at 150 px filling x 80–1000; behind it the beat's media
    darkened to 35 %, or (no media) a giant outline numeral of the year / topic; ends on a 4-frame orange flash."""
    l = L(X)
    P = X.portrait
    img = b.get("image")
    ttl = str(b.get("title", ""))
    hx, hy, hw = l["x"], l["hy"], l["hw"]
    hpx = 150 if P else 116
    head, hh, f = head_html(X, ttl, hx, hy, hw, hpx, 84 if P else 64, 3)
    over = ""
    yc = hy + hh + 24
    if b.get("sub"):
        X.used_text.update(str(b["sub"]))
        over += f'<div class="rl-sub" style="left:{hx}px;top:{yc:.0f}px;font-size:{40 if P else 34}px">{X.rich(b["sub"])}</div>'
        yc += 70
    ev = ""
    gtxt = b.get("year") or b.get("outline_big")
    if not img:
        if not gtxt:
            m = re.search(r"\d{2,4}", fit.plain(ttl))
            gtxt = m.group(0) if m else None
        if gtxt:
            label = b.get("label") or ""
            if P:
                gy0 = max(yc + 10, l["ey"])
                if label:
                    X.used_text.update(str(label))
                    ev += f'<div class="abs mono gl" style="left:80px;top:{gy0:.0f}px;font-size:28px;color:var(--muted)">{X.rich(label)}</div>'
                    gy0 += 56
                gh = min(470, 1310 - gy0)
                gpx = min(gh / 0.727, 920 / max(nw(gtxt), 0.5))
                gh = gpx * 0.727
            else:
                gy0 = 200
                if label:
                    X.used_text.update(str(label))
                    ev += f'<div class="abs mono gl" style="left:{l["ex"]}px;top:{gy0}px;font-size:24px;color:var(--muted)">{X.rich(label)}</div>'
                    gy0 += 50
                gpx = min(640 / 0.727, l["ew"] / max(nw(gtxt), 0.5))
                gh = gpx * 0.727
            gx = 80 if P else l["ex"]
            X.used_text.update(str(gtxt))
            ev += (f'<svg class="rl-gnum" data-safe="ignore" aria-hidden="true" data-layout-allow-overlap data-layout-allow-occlusion data-layout-allow-overflow width="{nw(gtxt) * gpx + 20:.0f}" height="{gh + 20:.0f}" '
                   f'style="left:{gx - 4}px;top:{gy0:.0f}px"><text class="gt" x="4" y="{gh + 2:.0f}" font-family="var(--f-num)" font-weight="900" '
                   f'font-size="{gpx:.0f}" fill="none" stroke="#4a4540" stroke-width="3" pathLength="1">{X.rich(gtxt)}</text></svg>')
    s = page(X, b, cid, t, d, head, ev, over, media=media_html(X, img), flash=True, outline=b.get("outline"))
    reveal(X, f"{s} .rl-hd", t + 0.12, f.n)
    X.sfx(t + 0.12, "title")
    if b.get("sub"):
        rise_in(X, f"{s} .rl-sub", T(X, b, "at_sub", t, t + 0.55))
    if gtxt and not img:
        X.tw(f'tl.fromTo("{s} .rl-gnum", {{x:-120, opacity:0}}, {{x:0, opacity:1, duration:0.9, ease:"expo.out"}}, {t + 0.2:.3f});')
        X.tw(f'tl.fromTo("{s} .rl-gnum .gt", {{strokeDasharray:"0 1"}}, {{strokeDasharray:"1 0", duration:1.4, ease:"sine.inOut"}}, {t + 0.2:.3f});')
        if b.get("label"):
            wipe_in(X, f"{s} .gl", t + 0.45)


def number(b, X, t, d, cid):
    """one figure, drawn: the numeral (glyph 420 px) counts up with motion streaks, the unit at 120 px on its baseline;
    under it a full-width proportion bar in true ratio (orange part) — or the 10×10 dot grid (64 px dots)."""
    l = L(X)
    P = X.portrait
    viz = b.get("viz") or ("bar" if b.get("bar") else "dots")
    v, f0, unit = float(b["value"]), float(b.get("from", 0)), str(b.get("unit", ""))
    dec = int(b.get("decimals", 0))
    pre = str(b.get("prefix", ""))
    dots = viz == "dots"
    vtxt = (f"{v:.{dec}f}")
    X.used_text.update("0123456789.%+-" + unit + pre)
    upx = (120 if not dots else 72) if P else (96 if not dots else 64)
    uw = len(unit) * upx * (0.9 if unit.isascii() else 1.0)
    if P:
        avail = 920 - uw - 16
        gmax = 420 if not dots else 175
    else:
        avail = (l["hw"] if not dots else 760) - uw - 16
        gmax = 330 if not dots else 200
    px = min(gmax / 0.727, avail / max(nw(pre + vtxt), 0.5))
    nx = l["x"]
    ny = l["hy"] - px * 0.12
    streaks = "".join(f'<i style="left:{nx + 40 + 90 * k}px;top:{ny + px * (0.25 + 0.11 * k):.0f}px;width:{260 + 50 * (k % 3)}px"></i>' for k in range(5))
    hn = (f'<div class="hn num" data-safe="ignore" style="left:{nx}px;top:{ny:.0f}px;font-size:{px:.0f}px;line-height:1">'
          f'{X.rich(pre)}<span class="n">{X.rich(b.get("from_text", f"{f0:.{dec}f}"))}</span>'
          f'<span class="u" style="font-size:{upx}px">{X.rich(unit)}</span></div>')
    glyph_bottom = ny + px * 0.12 + px * 0.727 + px * 0.06
    over = f'<div class="streaks">{streaks}</div>' + hn
    ev = ""
    lbl = b.get("label") or ""
    sub = b.get("sub") or ""
    if not dots:
        # label under the numeral (headline zone), the bar in the evidence zone
        ly = glyph_bottom + 36 if P else glyph_bottom + 30
        lh_html, lhh, lf = head_html(X, lbl, nx, ly, l["hw"], 60 if P else 50, 36, 2, accent="none") if lbl else ("", 0, None)
        over += lh_html.replace('class="rl-hd', 'class="rl-hd nlab') if lbl else ""
        bx, bw = (80, 920) if P else (l["ex"], l["ew"])
        by = max(990, ly + lhh + 80) if P else 420
        bar = b.get("bar") or {}
        parts = bar.get("parts") if isinstance(bar, dict) else None
        if not parts:     # plain ratio: the value as a share of 100
            parts = [{"v": v, "label": b.get("bar_label", ""), "hot": True}, {"v": max(0.0, 100 - v), "label": ""}]
        tot = sum(float(p.get("v", 0)) for p in parts) or 1
        segs, labs, x = "", "", 0.0
        for k, p in enumerate(parts):
            w = bw * float(p.get("v", 0)) / tot
            col = ACC if p.get("hot") else (GREY2 if p.get("label") else LINE)
            segs += f'<b class="sg{k}" style="left:{x:.1f}px;width:{w:.1f}px;background:{col}"></b>'
            if p.get("label"):
                X.used_text.update(str(p["label"]))
                al = "left" if x < bw * 0.5 else "right"
                pos = f"left:{bx + x:.0f}px" if al == "left" else f"right:{X.W - min(bx + x + w, (930 if P else bx + bw)):.0f}px"
                labs += f'<div class="lab bl{k}" style="{pos};top:{by + 76}px;font-size:{36 if P else 30}px;color:var(--fg)">{X.rich(p["label"])}</div>'
            x += w
        ev += f'<div class="pbar" style="left:{bx}px;top:{by}px;width:{bw}px;height:56px">{segs}</div>' + labs
        tot_lab = bar.get("total") if isinstance(bar, dict) else None
        if tot_lab:
            X.used_text.update(str(tot_lab))
            ty = by + 170
            ev += (f'<svg class="abs brk" style="left:{bx}px;top:{ty}px" width="{bw}" height="30"><path d="M1,0 V22 H{bw - 1} V0" fill="none" stroke="{GREY2}" stroke-width="3"/></svg>'
                   f'<div class="lab tl" style="left:{bx}px;top:{ty + 46}px;font-size:{64 if P else 52}px;color:var(--fg)">{X.rich(tot_lab)}</div>')
    else:
        # dots: 10 × 10, 64 px, across x 80–1000 (9:16) / the evidence column (16:9); label beside the numeral
        n_on, hl = int(round(v)), int(b.get("hl", 0))
        if P:
            gx, gy, cell, gapx, gapy = 80, max(l["hy"] + 280, glyph_bottom + 40), 64, (920 - 640) / 9, 12
            lx, lw = nx + nw(pre + vtxt) * px + uw + 40, 0
            lw = 1000 - lx
        else:
            gx, gy, cell, gapx, gapy = l["ex"] + 90, 190, 56, 14, 14
            lx, lw = nx, l["hw"]
        cells = ""
        for k in range(100):
            c = "on" if k < n_on else ("hl" if k < n_on + hl else "")
            r, q = divmod(k, 10)
            cells += f'<i class="{c}" style="left:{gx + q * (cell + gapx):.1f}px;top:{gy + r * (cell + gapy):.1f}px;width:{cell}px;height:{cell}px"></i>'
        ev += f'<div class="dots">{cells}</div>'
        if lbl:
            if P:
                ly = l["hy"] + 10
                lh_html, lhh, lf = head_html(X, lbl, lx, ly, max(300, lw), 52, 30, 3, accent="none")
            else:
                ly = glyph_bottom + 40
                lh_html, lhh, lf = head_html(X, lbl, lx, ly, lw, 56, 32, 2, accent="none")
            over += lh_html.replace('class="rl-hd', 'class="rl-hd nlab')
    if sub:
        X.used_text.update(str(sub))
        sy = l["kick"] + 50 if not P else None
        if P:
            over = over.replace('<div class="hn', f'<div class="abs mono nsub" style="left:{nx}px;top:{l["kick"] + 46}px;font-size:28px;color:var(--muted)">{X.rich(sub)}</div><div class="hn', 1)
        else:
            over = over.replace('<div class="hn', f'<div class="abs mono nsub" style="left:{nx}px;top:{sy}px;font-size:24px;color:var(--muted)">{X.rich(sub)}</div><div class="hn', 1)
    s = page(X, b, cid, t, d, "", ev, over, outline=b.get("outline", vtxt))
    ta = min(T(X, b, "at", t, t + 0.25), t + 0.3)
    rise_in(X, f"{s} .hn", t + 0.08, 0.3)
    dur = float(b.get("count", 1.0))
    count(X, f"{s} .hn .n", ta, f0, v, dec, dur)
    X.tw(f'tl.fromTo("{s} .hn", {{filter:"blur(10px)", x:-30}}, {{filter:"blur(0px)", x:0, duration:{dur:.3f}, ease:"power3.out"}}, {ta:.3f});')
    X.tw(f'tl.fromTo("{s} .streaks i", {{opacity:0.22, x:120, scaleX:1}}, {{opacity:0, x:-260, scaleX:0.3, duration:{dur * 0.8:.3f}, ease:"power2.out", stagger:0.04}}, {ta:.3f});')
    X.sfx(ta, "count")
    if sub:
        wipe_in(X, f"{s} .nsub", t + 0.1)
    if lbl:
        reveal(X, f"{s} .nlab", ta + 0.35, 2, underline=False)
    if not dots:
        X.tw(f'tl.from("{s} .pbar", {{scaleX:0, transformOrigin:"0% 50%", duration:0.35, ease:"power3.out"}}, {ta + 0.1:.3f});')
        k_hot = None
        bar = b.get("bar") or {}
        parts = bar.get("parts") if isinstance(bar, dict) and bar.get("parts") else [{"hot": True}, {}]
        tk = ta + 0.4
        for k, p in enumerate(parts):
            X.tw(f'tl.from("{s} .pbar .sg{k}", {{scaleX:0, duration:{0.5 if not p.get("hot") else 0.6}, ease:"power3.out"}}, {tk:.3f});')
            if p.get("label"):
                rise_in(X, f"{s} .bl{k}", tk + 0.3)
            if p.get("hot"):
                X.sfx(tk, "pop")
            tk += 0.45
        if isinstance(bar, dict) and bar.get("total"):
            X.tw(f'tl.from("{s} .brk", {{scaleX:0, transformOrigin:"50% 50%", duration:0.4, ease:"power3.out"}}, {tk:.3f});')
            rise_in(X, f"{s} .tl", tk + 0.15)
    else:
        X.tw(f'tl.from("{s} .dots i", {{scale:0, duration:0.22, ease:"back.out(2)", stagger:{{each:0.007, grid:[10,10], from:"start"}}}}, {ta:.3f});')
        if b.get("hl"):
            th = T(X, b, "at_hl", t, ta + 1.2)
            X.tw(f'tl.from("{s} .dots i.hl", {{backgroundColor:"{LINE}", scale:1.5, duration:0.35, ease:"back.out(3)", stagger:0.04}}, {th:.3f});')
            X.sfx(th, "pop")


def statement(b, X, t, d, cid):
    """the sentence set at up to 130–150 px across 3–4 lines, filling the headline and evidence zones; a thick 16 px
    orange rule draws in first; one word in orange; lines land on the beat's stress ("at"). An optional "foot"
    (a computed line or two) sits at the foot of the evidence zone."""
    l = L(X)
    P = X.portrait
    lines = [str(x).lstrip("~") for x in (b.get("lines") or [b.get("text", "")])]
    img = b.get("image")
    x, w = l["x"], l["hw"]
    ry = l["hy"]
    max_px = 150 if P else 112
    sbar = b.get("bar") if isinstance(b.get("bar"), dict) else None
    avail_h = (1300 if P else 900) - (ry + 60) - ((150 if b.get("foot") else 0) + (200 if sbar else 0) if P else 0)
    px = max_px
    for ln in lines:
        px = min(px, w * 0.97 / max(fit.width(ln), 1))
    px = min(px, avail_h / (len(lines) * 1.12))
    px = max(56, px)
    rows = ""
    for ln in lines:
        rows += f'<div class="rlm"><div class="li">{X.rich(ln)}</div></div>'
    lbl = b.get("label") or ""
    over = ""
    if lbl:
        X.used_text.update(str(lbl))
        over += f'<div class="abs mono slab" style="left:{x}px;top:{ry + 30}px;font-size:28px;color:var(--muted)">{X.rich(lbl)}</div>'
    top = ry + (90 if lbl else 50)
    head = (f'<div class="rl-hd ac-color" data-layout-allow-overlap style="left:{x}px;top:{top}px;width:{w}px;font-size:{px:.0f}px;line-height:1.12">{rows}</div>'
            f'<i class="abs srule" style="left:{x}px;top:{ry}px;width:{w if P else 520}px;height:16px;background:var(--accent);transform-origin:0 50%"></i>')
    ev = ""
    foot = b.get("foot")
    if foot:
        fl = foot if isinstance(foot, list) else [foot]
        fy = (1300 - 60 * len(fl) - 20) if P else 600
        fx_ = x if P else l["ex"]
        fw_ = w if P else l["ew"]
        ev += f'<i class="abs frule" style="left:{fx_}px;top:{fy - 24}px;width:{fw_}px;height:2px;background:{GREY2}"></i>'
        for k, ft in enumerate(fl):
            X.used_text.update(str(ft))
            ev += f'<div class="lab ft{k}" style="left:{fx_}px;top:{fy + 60 * k}px;font-size:{38 if P else 30}px;color:var(--fg);font-weight:700">{X.rich(ft)}</div>'
    if sbar:      # a proportion bar under the sentence: the figure as a share of its whole, ends labelled
        bwid = w if P else l["ew"]
        nfoot = len(foot if isinstance(foot, list) else [foot]) if foot else 0
        bend = (1300 - 60 * nfoot - 20 - 24 - 40) if (foot and P) else (1240 if P else 520)
        by = bend - 130
        bx0 = x if P else l["ex"]
        bv = max(0.0, min(100.0, float(sbar.get("v", 0))))
        lpx = 34 if P else 30
        X.used_text.update(str(sbar.get("left", "")) + str(sbar.get("right", "")))
        ev += (f'<div class="pbar sbar" style="left:{bx0}px;top:{by:.0f}px;width:{bwid}px;height:72px">'
               f'<b class="sbf" style="left:0;width:{bwid * bv / 100:.1f}px;background:var(--accent)"></b></div>'
               f'<div class="lab sbl" style="left:{bx0}px;top:{by + 86:.0f}px;font-size:{lpx}px;color:var(--fg)">{X.rich(sbar.get("left", ""))}</div>'
               f'<div class="lab sbr" style="right:{X.W - (min(x + bwid, 930) if P else bx0 + bwid):.0f}px;top:{by + 86:.0f}px;font-size:{lpx}px;color:var(--muted)">{X.rich(sbar.get("right", ""))}</div>')
    s = page(X, b, cid, t, d, head, ev, over, media=media_html(X, img), outline=b.get("outline"))
    X.tw(f'tl.fromTo("{s} .srule", {{scaleX:0}}, {{scaleX:1, duration:0.25, ease:"power3.inOut"}}, {t:.3f});')
    if lbl:
        wipe_in(X, f"{s} .slab", t + 0.15)
    at = b.get("at") or []
    span = min(d * 0.5, 0.42 * len(lines))
    for k in range(len(lines)):
        tk = float(X.T(at[k], t)) if k < len(at) and at[k] is not None else t + 0.3 + k * span / max(len(lines), 1)
        tk = min(tk, t + 0.12 + 0.35 * k + (0.9 if k >= 2 else 0))     # never an empty page waiting for the word
        X.tw(f'tl.fromTo("{s} .rl-hd .rlm:nth-child({k + 1}) .li", {{yPercent:112}}, {{yPercent:0, duration:{9 * F:.3f}, ease:"power3.out"}}, {max(t, tk - 0.1):.3f});')
        X.sfx(tk, "line")
        t_last = max(t, tk - 0.1) + 9 * F
    if sbar:
        tb = t_last + 0.25
        X.tw(f'tl.from("{s} .sbar", {{scaleX:0, transformOrigin:"0% 50%", duration:0.3, ease:"power3.out"}}, {tb:.3f});')
        X.tw(f'tl.from("{s} .sbf", {{scaleX:0, duration:0.6, ease:"power3.out"}}, {tb + 0.25:.3f});')
        rise_in(X, f"{s} .sbl", tb + 0.55)
        rise_in(X, f"{s} .sbr", tb + 0.3)
        X.sfx(tb + 0.25, "pop")
    if foot:
        tf = T(X, b, "at_foot", t, t + 0.4 + span + 0.3)
        if sbar:
            tf = max(tf, t_last + 1.0)
        X.tw(f'tl.from("{s} .frule", {{scaleX:0, transformOrigin:"0% 50%", duration:0.4, ease:"power3.out"}}, {tf:.3f});')
        for k in range(len(foot if isinstance(foot, list) else [foot])):
            wipe_in(X, f"{s} .ft{k}", tf + 0.15 + 0.2 * k, 0.45)


def _panel_value(X, b, side, k, x, y, w, h, vmax, P):
    """a value panel: label, value (160 px), a bar in true ratio to the larger value."""
    lab, val = str(side.get("label", "")), side.get("value", 0)
    disp = str(side.get("text", side.get("display", val)))
    X.used_text.update(lab + disp + str(side.get("note", "")))
    pad = 40 if P else 32
    vpx = 160 if P else 120
    sn = split_num(disp)
    num = disp
    if sn:
        pre, nv, dec, suf = sn
        num = f'{X.rich(pre)}<span class="cn">{nv:.{dec}f}</span><span class="u" style="font-family:var(--f-display);font-size:{vpx * 0.42:.0f}px;margin-left:.06em">{X.rich(suf)}</span>'
    bw = (w - 2 * pad) * float(val) / vmax if vmax else 0
    note = side.get("note", "")
    nh = (f'<div class="lab pn" style="right:{pad}px;top:{pad + 4}px;font-size:{28 if P else 24}px;color:var(--muted);font-weight:600">{X.rich(note)}</div>' if note else "")
    return (f'<div class="pnl p{k}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><div class="pw">'
            f'<div class="lab pl" style="left:{pad}px;top:{pad}px;font-size:{44 if P else 36}px;color:var(--fg)">{X.rich(lab)}</div>{nh}'
            f'<div class="abs num pv" style="left:{pad - 6}px;top:{pad + (70 if P else 56)}px;font-size:{vpx}px;color:var(--fg)">{num}</div>'
            f'<i class="bar pb" style="left:{pad}px;bottom:{pad}px;width:{max(6, bw):.1f}px;height:{40 if P else 32}px;background:{GREY2}"></i>'
            f'</div></div>')


def compare(b, X, t, d, cid):
    """two stacked panels (920 × 430 in 9:16), each with label, value and a bar in true ratio; on the verdict the
    winner pushes 40 px wider and its bar turns orange, the loser dims to 50 %; a VS disc snaps between them.
    Old picture comparisons (left/right with img) use the same panels with the pictures inside."""
    l = L(X)
    P = X.portrait
    A, B = b.get("left", {}) or {}, b.get("right", {}) or {}
    valued = "value" in A and "value" in B
    if P:
        x, w, h = 80, 920, 430
        ya, yb = 300, 300 + h + 70
        vsx, vsy = 80 + 920 - 124 - 60, ya + h + 35 - 62
    else:
        x, w = l["ex"], l["ew"]
        h = 330
        ya, yb = 170, 170 + h + 60
        vsx, vsy = x + w - 124 - 50, ya + h + 30 - 62
    over = ""
    head = ""
    if valued:
        vmax = max(float(A["value"]), float(B["value"])) or 1
        ev = _panel_value(X, b, A, 0, x, ya, w, h, vmax, P) + _panel_value(X, b, B, 1, x, yb, w, h, vmax, P)
    else:
        def pic(side, k, y):
            img = f'<img src="{X.asset(side["img"])}" alt="">' if side.get("img") else ""
            lab = f'<div class="chipl">{X.rich(side["label"])}</div>' if side.get("label") else ""
            spots = ["right:28px;top:28px", "right:28px;top:96px", "right:28px;top:164px"]
            stk = "".join(f'<div class="stk s{j}" style="{spots[j]}">{X.rich(st)}</div>' for j, st in enumerate(side.get("stickers", [])[:3]))
            cl = "A" if k == 0 else "B"
            return (f'<div class="pnl p{k} {cl}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"><div class="pw">{img}<div class="dim"></div>{stk}{lab}</div></div>')
        if not P:      # pictures side by side in 16:9
            hw2 = (1728 - 40) / 2
            ev = ""
            for k, side in enumerate((A, B)):
                xx = 96 + k * (hw2 + 40)
                img = f'<img src="{X.asset(side["img"])}" alt="">' if side.get("img") else ""
                lab = f'<div class="chipl">{X.rich(side["label"])}</div>' if side.get("label") else ""
                spots = ["right:28px;top:28px", "right:28px;top:96px", "right:28px;top:164px"]
                stk = "".join(f'<div class="stk s{j}" style="{spots[j]}">{X.rich(st)}</div>' for j, st in enumerate(side.get("stickers", [])[:3]))
                ev += f'<div class="pnl p{k} {"AB"[k]}" style="left:{xx:.0f}px;top:200px;width:{hw2:.0f}px;height:{hw2 * 0.62:.0f}px"><div class="pw">{img}<div class="dim"></div>{stk}{lab}</div></div>'
            vsx, vsy = 960 - 62, 200 + hw2 * 0.31 - 62
        else:
            ev = pic(A, 0, ya) + pic(B, 1, yb)
    ev += f'<div class="vs">VS</div>'.replace('class="vs"', f'class="vs" style="left:{vsx:.0f}px;top:{vsy:.0f}px"')
    X.used_text.update("VS")
    if b.get("chip") and not b.get("kicker"):
        b = dict(b, kicker=b["chip"])
    note = b.get("note") or b.get("verdict_text")
    if note:
        X.used_text.update(str(note))
        ny = (yb + h + 34) if P else 560
        nx = x if P else l["x"]
        if valued or P:
            over += f'<div class="lab cnote" style="left:{nx}px;top:{ny}px;font-size:{40 if P else 32}px;color:var(--fg)">{X.rich(note)}</div>'
    if not P and valued and b.get("head"):
        hh, _, f = head_html(X, b["head"], l["x"], l["hy"], l["hw"], l["hpx"], 60, 3, accent="none")
        head = hh
    s = page(X, b, cid, t, d, head, ev, over, outline=b.get("outline"))
    if head:
        reveal(X, f"{s} .rl-hd", t + 0.1, 3, underline=False)
    ta = min(T(X, b, "at_left", t, t + 0.05), t + 0.05)
    tb = min(T(X, b, "at_right", t, t + 0.75), t + 0.75)
    for k, tk in ((0, ta), (1, tb)):
        X.tw(f'tl.fromTo("{s} .p{k}", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.35, ease:"power3.out"}}, {tk:.3f});')
        X.sfx(tk, "enter")
        if valued:
            side = A if k == 0 else B
            sn = split_num(str(side.get("text", side.get("display", side.get("value")))))
            if sn:
                count(X, f"{s} .p{k} .cn", tk + 0.1, 0, sn[1], sn[2], 0.8)
            X.tw(f'tl.from("{s} .p{k} .pb", {{scaleX:0, duration:0.55, ease:"power3.out"}}, {tk + 0.2:.3f});')
    X.tw(f'tl.from("{s} .vs", {{scale:0, rotation:-30, duration:0.25, ease:"back.out(2.6)"}}, {tb + 0.4:.3f});')
    X.sfx(tb + 0.4, "pop")
    tv = X.T(b.get("at_verdict"), t) if b.get("at_verdict") else (t + min(d - 1.0, 2.2) if b.get("verdict") else None)
    if tv is not None and b.get("verdict"):
        tv = float(tv)
        win = 0 if b["verdict"] == "left" else 1
        lose = 1 - win
        X.tw(f'tl.to("{s} .p{win}", {{width:"+=40", duration:0.35, ease:"power3.out"}}, {tv:.3f});')
        X.tw(f'tl.to("{s} .p{lose}", {{opacity:0.5, duration:0.35, ease:"power2.out"}}, {tv:.3f});')
        if valued:
            X.tw(f'tl.to("{s} .p{win} .pb", {{backgroundColor:"{ACC}", duration:0.2, ease:"none"}}, {tv:.3f});')
        else:
            X.tw(f'tl.to("{s} .p{lose} img", {{filter:"grayscale(1)", duration:0.35}}, {tv:.3f});')
            X.tw(f'tl.to("{s} .p{win}", {{boxShadow:"inset 0 0 0 6px {ACC}", duration:0.2}}, {tv:.3f});')
        X.sfx(tv, "hit")
    if note:
        rise_in(X, f"{s} .cnote", (tv if tv is not None else tb + 0.6) + 0.3)
    if not valued:
        X.enter(f"{s} .stk", T(X, b, "at_stickers", t, tb + 0.6), "accent", verb="pop", stagger=0.12, dur=0.35)


def quote(b, X, t, d, cid):
    """a 96 px serif quote under a 300 px orange opening quotation mark; attribution row with a rule; media (if any)
    in a 920 × 520 window under it, slowly pushing in."""
    l = L(X)
    P = X.portrait
    text = str(b.get("text", ""))
    img = b.get("image")
    x = l["x"]
    w = 920 if P else (l["hw"] if img else 1500)
    qy = l["hy"] + 110
    maxh = (440 if img else 820) if P else 560
    f = fit_lines(text, w, maxh, 96 if P else 84, 52, 5 if P else 4, 1.25)
    rows = "".join(f'<div class="rlm"><div class="li">{X.rich(ln)}</div></div>' for ln in f.lines)
    qh = f.n * f.px * 1.25
    head = (f'<div class="qmk" data-layout-allow-occlusion style="left:{x - 10}px;top:{l["hy"] - 40}px;font-size:300px;height:200px">“</div>'
            f'<div class="qt ac-none" data-layout-allow-overlap style="left:{x}px;top:{qy}px;width:{w}px;font-size:{f.px}px">{rows}</div>')
    X.used_text.update("“")
    by = b.get("by") or ""
    over = ""
    yb = qy + qh + 40
    if by:
        X.used_text.update(str(by))
        over += (f'<i class="abs qrule" style="left:{x}px;top:{yb + 20}px;width:80px;height:4px;background:var(--fg)"></i>'
                 f'<div class="abs mono qby" style="left:{x + 104}px;top:{yb}px;font-size:28px;color:var(--muted)">{X.rich(by)}</div>')
        yb += 70
    ev = ""
    if img:
        if P:
            wy = max(yb + 20, 820)
            wh = min(520, 1320 - wy)
            ev = f'<div class="win" style="left:80px;top:{wy:.0f}px;width:920px;height:{wh:.0f}px"><img class="wi" src="{X.asset(img)}" alt=""></div>'
        else:
            ev = f'<div class="win" style="left:{l["ex"]}px;top:200px;width:{l["ew"]}px;height:{l["ew"] * 0.62:.0f}px"><img class="wi" src="{X.asset(img)}" alt=""></div>'
    s = page(X, b, cid, t, d, head, ev, over, outline=b.get("outline"))
    X.tw(f'tl.from("{s} .qmk", {{scale:0.4, x:-40, transformOrigin:"0% 30%", duration:0.35, ease:"back.out(1.8)"}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .qt .li", {{yPercent:112}}, {{yPercent:0, duration:{9 * F:.3f}, ease:"power3.out", stagger:{2 * F + 0.06:.3f}}}, {t + 0.2:.3f});')
    X.sfx(t + 0.2, "line")
    ta = T(X, b, "at_em", t, t + 0.6 + 0.12 * f.n)
    X.tw(f'tl.from("{s} .qt .em .emt", {{color:"{FG}", duration:0.25, ease:"none"}}, {ta:.3f});')
    if by:
        X.tw(f'tl.from("{s} .qrule", {{scaleX:0, transformOrigin:"0% 50%", duration:0.3, ease:"power3.out"}}, {ta + 0.2:.3f});')
        wipe_in(X, f"{s} .qby", ta + 0.3)
    if img:
        X.tw(f'tl.fromTo("{s} .win", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power3.out"}}, {t + 0.3:.3f});')
        X.tw(f'tl.fromTo("{s} .win .wi", {{scale:1.0}}, {{scale:1.08, duration:{d:.3f}, ease:"none"}}, {t:.3f});')


def outro(b, X, t, d, cid):
    """channel placeholder at 140 px, a 72 px follow chip, and up to three recap figures as a row of small stats above."""
    l = L(X)
    P = X.portrait
    x = l["x"]
    stats = (b.get("stats") or [])[:3]
    name = str(b.get("title") or X.channel)
    ev = ""
    head = ""
    over = ""
    if P:
        sy, cy, chy = 300, 540, 0
    else:
        sy, cy = 200, 520
    if stats:
        cw = (920 if P else l["hw"]) / len(stats)
        cells = ""
        spx = min([min(84 if P else 72, (cw - 30) / max(nw(st.get("v", "")), 1)) for st in stats])
        for k, st in enumerate(stats):
            X.used_text.update(str(st.get("v", "")) + str(st.get("k", "")))
            cells += (f'<div class="stat abs st{k}" style="left:{x + k * cw:.0f}px;top:{sy + 30}px;width:{cw - 20:.0f}px">'
                      f'<div class="v" style="font-size:{spx:.0f}px">{X.rich(st.get("v", ""))}</div>'
                      f'<div class="k" style="font-size:{30 if P else 26}px">{X.rich(st.get("k", ""))}</div></div>')
        over += f'<i class="abs orule" style="left:{x}px;top:{sy}px;width:{920 if P else l["hw"]}px;height:4px;background:var(--fg)"></i>' + cells
    else:
        cy = l["hy"] + (60 if P else 0)
    hh, hgt, f = head_html(X, name, x, cy, 920 if P else l["hw"], 140 if P else 120, 70, 2, accent="none")
    head = hh
    yc = cy + hgt + 20
    if b.get("sub"):
        X.used_text.update(str(b["sub"]))
        over += f'<div class="rl-sub osub" style="left:{x}px;top:{yc:.0f}px;font-size:{40 if P else 34}px">{X.rich(b["sub"])}</div>'
        yc += 70
    cta = b.get("cta") or "关注"
    X.used_text.update("+ " + str(cta))
    over += f'<div class="chip" style="left:{x}px;top:{yc + 30:.0f}px">+ {X.rich(cta)}</div>'
    otx = b.get("outline_big")
    if otx:
        X.used_text.update(str(otx))
        if P:
            gy = yc + 150
            gh = min(330, 1310 - gy)
            gpx = min(gh / 0.727, 920 / max(nw(otx), 0.5))
            gy = gy + (max(gy, 1300 - gpx * 0.727) - gy) * 0.65      # between the chip and the foot of the zone, nearer the foot
            gx = 80
        else:
            gy = 330
            gpx = min(420 / 0.727, l["ew"] / max(nw(otx), 0.5))
            gx = l["ex"]
        gh = gpx * 0.727
        ev += (f'<svg class="rl-gnum" data-safe="ignore" aria-hidden="true" data-layout-allow-overlap data-layout-allow-occlusion data-layout-allow-overflow width="{nw(otx) * gpx + 20:.0f}" height="{gh + 20:.0f}" style="left:{gx - 4}px;top:{gy:.0f}px">'
               f'<text class="gt" x="4" y="{gh + 2:.0f}" font-family="var(--f-num)" font-weight="900" font-size="{gpx:.0f}" fill="none" stroke="#4a4540" stroke-width="3" pathLength="1">{X.rich(otx)}</text></svg>')
    s = page(X, b, cid, t, d, head, ev, over, outline=b.get("outline"))
    if stats:
        X.tw(f'tl.from("{s} .orule", {{scaleX:0, transformOrigin:"0% 50%", duration:0.35, ease:"power3.inOut"}}, {t + 0.05:.3f});')
        for k in range(len(stats)):
            rise_in(X, f"{s} .st{k}", t + 0.06 + 0.1 * k)
    th = T(X, b, "at", t, t + 0.5)
    reveal(X, f"{s} .rl-hd", th, f.n, underline=False)
    X.sfx(th, "title")
    if b.get("sub"):
        rise_in(X, f"{s} .osub", t + 0.8)
    X.tw(f'tl.from("{s} .chip", {{scaleX:0, transformOrigin:"0% 50%", duration:0.3, ease:"back.out(1.6)"}}, {max(t + 1.0, th + 0.4):.3f});')
    X.sfx(max(t + 1.0, th + 0.4), "pop")
    if otx:
        X.tw(f'tl.fromTo("{s} .rl-gnum .gt", {{strokeDasharray:"0 1"}}, {{strokeDasharray:"1 0", duration:1.4, ease:"sine.inOut"}}, {t + 0.6:.3f});')
    if X.v.get("meta", {}).get("mascot") and X.S.get("outro", {}).get("move", True):
        m = (X.S.get("outro", {}) or {}).get("mascot_portrait" if P else "mascot", {"x": 420, "y": -260, "scale": 1.7} if not P else {"x": 600, "y": -420, "scale": 1.3})
        X.tw(f'tl.to("#mascot", {{x:{m["x"]}, y:{m["y"]}, scale:{m["scale"]}, transformOrigin:"50% 100%", duration:0.8, ease:"expo.out"}}, {t:.3f});')


def rank(b, X, t, d, cid):
    """horizontal bars, widths in true ratio, up to 5 rows 120 px tall, sorted; values right-aligned; bars race to
    length (16 frames) and the top one turns orange."""
    l = L(X)
    P = X.portrait
    items = sorted((b.get("items") or [])[:6], key=lambda it: -float(it.get("value", 0) or 0))
    n = len(items)
    vmax = max([float(it.get("value", 0) or 0) for it in items] or [1]) or 1
    head = ""
    hh = 0
    nlines = 1
    if b.get("head"):
        head, hh, f = head_html(X, b["head"], l["x"], l["hy"], l["hw"], 130 if P else l["hpx"], 70, 2, accent="none")
        nlines = f.n
    if P:
        x0, wmax = 80, 850
        y0 = l["hy"] + hh + 50 if head else l["hy"]
        rh = min(120, (1290 - y0) / max(n, 1) - 12)
    else:
        x0, wmax = l["ex"], l["ew"] - 20
        y0 = 180
        rh = min(120, (880 - y0) / max(n, 1) - 12)
    bh = rh * 0.55
    rows = ""
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = max(8.0, wmax * v / vmax)
        y = y0 + k * (rh + 12)
        nm, lv = str(it.get("name", "")), str(it.get("label", it.get("value", "")))
        X.used_text.update(nm + lv)
        fs = min(36 if P else 30, rh * 0.32)
        rows += (f'<div class="lab rn{k}" style="left:{x0}px;top:{y:.0f}px;font-size:{fs:.0f}px;color:var(--fg)">{X.rich(nm)}</div>'
                 f'<div class="abs num rv{k}" style="right:{X.W - (x0 + wmax):.0f}px;top:{y - 4:.0f}px;font-size:{fs * 1.2:.0f}px;color:var(--fg)">{X.rich(lv)}</div>'
                 f'<i class="bar rb{k}" style="left:{x0}px;top:{y + rh - bh:.0f}px;width:{w:.1f}px;height:{bh:.0f}px;background:{GREY2 if k else FG}"></i>')
    s = page(X, b, cid, t, d, head, rows, "", outline=b.get("outline"))
    if head:
        reveal(X, f"{s} .rl-hd", t + 0.1, nlines, underline=False)
    t0 = min(T(X, b, "at", t, t + 0.45), t + 0.45)
    for k in range(n):
        tk = t0 + 0.07 * k
        X.tw(f'tl.from("{s} .rb{k}", {{scaleX:0, duration:{16 * F:.3f}, ease:"power2.out"}}, {tk:.3f});')
        rise_in(X, f"{s} .rn{k}", tk - 0.05, 0.25)
        rise_in(X, f"{s} .rv{k}", tk + 0.3, 0.25)
    if n:
        X.tw(f'tl.to("{s} .rb0", {{backgroundColor:"{ACC}", duration:0.15, ease:"none"}}, {t0 + 16 * F + 0.1:.3f});')
        X.sfx(t0, "whoosh_soft")
        X.sfx(t0 + 16 * F + 0.1, "hit")


def split(b, X, t, d, cid):
    """share of total: one 920 × 140 segmented bar splits apart; its blocks slide down into a column, each with its
    percentage. The part marked "hot" is the orange one."""
    l = L(X)
    P = X.portrait
    items = (b.get("items") or [])[:5]
    n = len(items)
    tot = sum(float(it.get("value", 0) or 0) for it in items) or 1
    head = ""
    hh = 0
    nl = 1
    if b.get("head"):
        head, hh, f = head_html(X, b["head"], l["x"], l["hy"], l["hw"], 130 if P else l["hpx"], 70, 2, accent="none")
        nl = f.n
    gap = 30
    if P:      # 9:16: the blocks split apart sideways and drop under the track, 200 px tall, percentages under them
        bx, bw, by, bh = 80, 920, max(620, l["hy"] + hh + 40), 140
        ry0 = by + bh + 50
        rh = 200
        cw = bw - gap * max(n - 1, 0)
    else:
        bx, bw, by, bh = l["ex"], l["ew"], 180, 120
        ry0 = by + bh + 70
        rh = min(120, (880 - ry0) / max(n, 1) - 26)
    blocks, labs = "", ""
    x = 0.0
    fx = 0.0
    finals = []
    spx = 150.0
    if P:      # one percentage size for all parts: as big as fits each part's width, never past x 930 (safe area)
        cx = bx
        for it in items:
            wk = cw * float(it.get("value", 0) or 0) / tot
            pct0 = str(it.get("pct") or f"{100 * float(it.get('value', 0) or 0) / tot:.1f}%")
            room = min(cx + wk, 930) - cx
            spx = min(spx, room * 0.97 / max(nw(pct0), 1))
            cx += wk + gap
    hot = next((k for k, it in enumerate(items) if it.get("hot")), 0)
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = bw * v / tot
        col = ACC if k == hot else (GREY2 if k % 2 else GREY)
        fgc = BG if k == hot else FG
        nm = str(it.get("name", ""))
        X.used_text.update(nm)
        if P:
            wk = cw * v / tot
            finals.append((bx + fx - (bx + x), ry0 - by, wk))
            ry = ry0
        else:
            ry = ry0 + k * (rh + 30)
        dy = ry - by
        dx = -x
        blocks += (f'<div class="blk b{k}" data-dx="{dx:.1f}" data-dy="{dy:.1f}" style="left:{bx + x:.1f}px;top:{by}px;width:{w - (4 if k < n - 1 else 0):.1f}px;height:{bh}px;background:{col}">'
                   f'<span class="bn" style="color:{fgc};font-size:{min(34, rh * 0.3):.0f}px">{X.rich(nm) if w > fit.width(nm) * 34 + 44 else ""}</span></div>')
        pct = str(it.get("pct") or f"{100 * v / tot:.1f}%")
        val = str(it.get("label", ""))
        X.used_text.update(pct + val)
        if P:
            tx = bx + fx
            ppx = spx
            py = ry0 + rh + 14
            labs += (f'<div class="abs num sp{k}" style="left:{tx:.0f}px;top:{py:.0f}px;font-size:{ppx:.0f}px;color:var(--fg)">{X.rich(pct)}</div>'
                     + (f'<div class="lab sv{k}" style="left:{tx:.0f}px;top:{py + ppx * 1.02:.0f}px;font-size:30px;color:var(--muted);font-weight:600">{X.rich(val)}</div>' if val else ""))
            fx += finals[-1][2] + gap
        else:
            tx = bx + w + 30
            ppx = min(80, rh * 0.72)
            if tx + nw(pct) * ppx > bx + bw:
                tx = bx + bw - nw(pct) * ppx
            labs += (f'<div class="abs num sp{k}" style="left:{tx:.0f}px;top:{ry - 6:.0f}px;font-size:{ppx:.0f}px;color:var(--fg)">{X.rich(pct)}</div>'
                     + (f'<div class="lab sv{k}" style="left:{tx:.0f}px;top:{ry + ppx * 0.98:.0f}px;font-size:26px;color:var(--muted);font-weight:600">{X.rich(val)}</div>' if val else ""))
        x += w
    if P and b.get("note"):
        X.used_text.update(str(b["note"]))
        labs += f'<div class="lab snote" style="left:{bx}px;top:{ry0 + rh + 14 + spx * 1.02 + 70:.0f}px;font-size:42px;color:var(--fg)">{X.rich(b["note"])}</div>'
    # the empty track stays where the bar was: a 2 px frame with the total in it
    foot = b.get("total") or ""
    X.used_text.update(str(foot) + "100%")
    track = (f'<div class="abs strk" style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px;box-shadow:inset 0 0 0 2px {GREY};'
             f'display:flex;align-items:center;justify-content:space-between;padding:0 28px;font-family:var(--f-display);font-weight:800;'
             f'font-size:{40 if P else 32}px;color:var(--muted)"><span>{X.rich(foot)}</span><span class="num">100%</span></div>')
    s = page(X, b, cid, t, d, head, track + blocks + labs, "", outline=b.get("outline"))
    if head:
        reveal(X, f"{s} .rl-hd", t + 0.1, nl, underline=False)
    tb = t + 0.35
    X.tw(f'tl.fromTo("{s} .blk", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power3.inOut"}}, {tb:.3f});')
    ts = min(T(X, b, "at", t, tb + 0.9), tb + 0.9)
    x = 0.0
    for k, it in enumerate(items):
        v = float(it.get("value", 0) or 0)
        w = bw * v / tot
        ry = ry0 + k * (rh + 30)
        X.tw(f'tl.to("{s} .b{k}", {{y:{12 + 6 * k}, duration:0.12, ease:"power2.out"}}, {ts + 0.1 * k:.3f});')
        if P:
            ddx, ddy, wk = finals[k]
            X.tw(f'tl.to("{s} .b{k}", {{x:{ddx:.1f}, y:{ddy:.1f}, width:{wk:.1f}, height:{rh:.0f}, duration:0.45, ease:"power3.inOut"}}, {ts + 0.12 + 0.1 * k:.3f});')
        else:
            X.tw(f'tl.to("{s} .b{k}", {{x:{-x:.1f}, y:{ry - by:.1f}, height:{rh:.0f}, duration:0.45, ease:"power3.inOut"}}, {ts + 0.12 + 0.1 * k:.3f});')
        rise_in(X, f"{s} .sp{k}", ts + 0.5 + 0.1 * k)
        if it.get("label"):
            wipe_in(X, f"{s} .sv{k}", ts + 0.65 + 0.1 * k)
        x += w
    X.sfx(ts, "whoosh_soft")
    if P and b.get("note"):
        rise_in(X, f"{s} .snote", ts + 0.9 + 0.1 * n)
    X.tw(f'tl.from("{s} .strk", {{opacity:0, duration:0.01}}, {ts + 0.1:.3f});')
    rise_in(X, f"{s} .strk span", ts + 0.45, 0.3)


def trend(b, X, t, d, cid):
    """a thick 10 px line with a 12 % area fill, drawn left to right; the last point is tagged with a big value;
    year labels 28 px."""
    l = L(X)
    P = X.portrait
    pts = (b.get("points") or [])[:12]
    n = len(pts)
    head = ""
    hh = 0
    nl = 1
    if b.get("head"):
        head, hh, f = head_html(X, b["head"], l["x"], l["hy"], l["hw"], 130 if P else l["hpx"], 70, 2, accent="none")
        nl = f.n
    sub = b.get("sub") or ""
    over = ""
    if sub:
        X.used_text.update(str(sub))
        sy = l["hy"] + hh + 14
        over += f'<div class="abs mono tsub" style="left:{l["x"]}px;top:{sy:.0f}px;font-size:{28 if P else 24}px;color:var(--muted)">{X.rich(sub)}</div>'
        hh += 50
    if P:
        px0, px1 = 110, 860
        top = max(l["hy"] + hh + 200, 700)
        bot = 1230
    else:
        px0, px1 = l["ex"] + 20, l["ex"] + l["ew"] - 40
        top, bot = 330, 830
    vals = [float(p.get("value", 0) or 0) for p in pts]
    vmax = max(vals or [1]) or 1
    xs = [px0 + (px1 - px0) * k / max(n - 1, 1) for k in range(n)]
    ys = [bot - (bot - top) * v / vmax for v in vals]
    W, H = X.W, X.H
    dpath = " ".join(f"{'M' if k == 0 else 'L'}{xs[k]:.1f},{ys[k]:.1f}" for k in range(n))
    apath = dpath + f" L{xs[-1]:.1f},{bot} L{xs[0]:.1f},{bot} Z" if n else ""
    grid = ""
    for q in (0.5, 1.0):
        gy = bot - (bot - top) * q
        grid += f'<line x1="{px0 - 20}" y1="{gy:.1f}" x2="{px1 + 30}" y2="{gy:.1f}" stroke="{LINE}" stroke-width="2" stroke-dasharray="6 10"/>'
    svg = (f'<svg class="abs tch" width="{W}" height="{H}" style="left:0;top:0">{grid}'
           f'<line x1="{px0 - 20}" y1="{bot}" x2="{px1 + 30}" y2="{bot}" stroke="{GREY2}" stroke-width="3"/>'
           f'<path class="ta" d="{apath}" fill="{ACC}" fill-opacity=".12"/>'
           f'<path class="tl" d="{dpath}" fill="none" stroke="{ACC}" stroke-width="10" stroke-linejoin="round" stroke-linecap="round" pathLength="1"/>'
           + "".join(f'<circle class="td{k}" cx="{xs[k]:.1f}" cy="{ys[k]:.1f}" r="11" fill="{BG}" stroke="{FG}" stroke-width="5"/>' for k in range(n))
           + '</svg>')
    labs = ""
    for k, p in enumerate(pts):
        X.used_text.update(str(p.get("x", "")) + str(p.get("label", "")))
        labs += f'<div class="abs mono tx{k}" style="left:{xs[k] - 60:.0f}px;width:120px;text-align:center;top:{bot + 16}px;font-size:28px;color:var(--muted)">{X.rich(p.get("x", ""))}</div>'
        if k < n - 1 and p.get("label"):
            labs += f'<div class="abs num tv{k}" style="left:{xs[k] - 80:.0f}px;width:160px;text-align:center;top:{ys[k] - 74:.0f}px;font-size:34px;color:var(--fg)">{X.rich(p["label"])}</div>'
    tag = b.get("tag") or (pts[-1].get("label") if pts else "")
    if n and tag:
        X.used_text.update(str(tag))
        tpx = 110 if P else 90
        labs += (f'<div class="abs num ttag" style="right:{W - (xs[-1] + 16):.0f}px;top:{ys[-1] - tpx * 1.2 - 14:.0f}px;font-size:{tpx}px;color:var(--fg);text-align:right">{X.rich(tag)}</div>')
    s = page(X, b, cid, t, d, head, svg + labs, over, outline=b.get("outline"))
    if head:
        reveal(X, f"{s} .rl-hd", t + 0.1, nl, underline=False)
    if sub:
        wipe_in(X, f"{s} .tsub", t + 0.3)
    t0 = min(T(X, b, "at", t, t + 0.5), t + 0.15)
    dur = 1.3
    X.tw(f'tl.fromTo("{s} .tl", {{strokeDasharray:"0 1"}}, {{strokeDasharray:"1 0", duration:{dur}, ease:"sine.inOut"}}, {t0:.3f});')
    X.tw(f'tl.fromTo("{s} .ta", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{dur}, ease:"sine.inOut"}}, {t0:.3f});')
    for k in range(n):
        tk = t0 + dur * (xs[k] - px0) / max(px1 - px0, 1)
        X.tw(f'tl.from("{s} .td{k}", {{scale:0, transformOrigin:"50% 50%", duration:0.2, ease:"back.out(2.4)"}}, {tk:.3f});')
        rise_in(X, f"{s} .tx{k}", t0 - 0.2 + 0.05 * k, 0.25)
        if k < n - 1:
            rise_in(X, f"{s} .tv{k}", tk + 0.05, 0.25)
    if n and tag:
        sn = split_num(str(tag))
        X.tw(f'tl.from("{s} .ttag", {{y:40, clipPath:"inset(100% 0% 0% 0%)", duration:0.3, ease:"power3.out"}}, {t0 + dur:.3f});')
        X.sfx(t0 + dur, "hit")


SCENES = {"title": title, "number": number, "compare": compare, "statement": statement, "quote": quote, "outro": outro,
          "rank": rank, "split": split, "trend": trend}


# ---------------------------------------------------------------- shared effects in this style
CAP_CSS = r"""
/* subtitles (the shared caption pages): plain type, no plate */
.st-reel .clip.cap .cp { letter-spacing:.02em; line-height:1.3; }
.st-reel .clip.cap::before { content:""; position:absolute; left:0; right:0; top:-150px; bottom:-12px; z-index:-1; pointer-events:none;
  background:linear-gradient(180deg, rgba(18,17,16,0) 0%, rgba(18,17,16,.85) 62%, rgba(18,17,16,.85) 100%);
  -webkit-mask-image:linear-gradient(90deg, transparent 12%, #000 29%, #000 71%, transparent 78%); mask-image:linear-gradient(90deg, transparent 12%, #000 29%, #000 71%, transparent 78%); }
#root.v.st-reel .clip.cap::before { -webkit-mask-image:none; mask-image:none; }
#root.v.st-reel { --cap-bottom:470px; }
#root.h.st-reel { --cap-bottom:96px; }
"""
FX_CSS = r"""
.ctx.rlx .rk { position:absolute; display:flex; align-items:center; font-family:var(--f-mono); font-size:28px; letter-spacing:.08em; color:var(--fg); white-space:nowrap; height:42px; }
.ctx.rlx .rk .sq { width:12px; height:12px; background:var(--accent); margin-right:16px; flex:none; }
.ctx.rlx .rk .kc { position:static; margin-left:28px; color:var(--muted); }   /* inline: effects keep their own corner tags top-right */ .ctx.rlx .rk .kc b { color:var(--fg); font-weight:700; }
.ctx.rlx .rk .kl { max-width:72%; overflow:hidden; text-overflow:ellipsis; }
.ctx.rlx .cap > span { color:var(--fg); font-weight:700; padding:6px 12px 8px; border-radius:0; letter-spacing:.02em; text-shadow:0 2px 0 color-mix(in srgb, var(--bg) 70%, #000);
  background:color-mix(in srgb, var(--bg) 86%, transparent); box-shadow:0 0 22px 16px color-mix(in srgb, var(--bg) 86%, transparent); }
.ctx.rlx .cap .em .emt { background:none; color:var(--accent); padding:0; }
.ctx.rlx .rfade { position:absolute; left:0; right:0; }
.ctx.rlx .ft { opacity:1; color:var(--muted); font-family:var(--f-body); font-size:22px; letter-spacing:.02em; }
.ctx.rlx .rl-row { position:absolute; left:0; }
.ctx.rlx.photo .rk { color:#fff; text-shadow:0 1px 8px rgba(0,0,0,.6); } .ctx.rlx.photo .rk .kc { color:rgba(255,255,255,.8); }
.ctx.rlx.photo .cap > span { color:#fff; text-shadow:0 2px 0 #000, 0 0 16px rgba(0,0,0,.6); }
.ctx.rlx.photo .ft { color:rgba(255,255,255,.85); }
#root.v .ctx.rlx .cap { top:1340px; } #root.v .ctx.rlx .cap > span { font-size:44px; }
#root.v .ctx.rlx .ft { top:1450px; line-height:1.25; }   /* foot + source end by y 1510: inside the 1:1 / 4:5 windows (base y 170–1520) */
"""
STYLE["css"] = FX_CSS + CAP_CSS


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around a shared effect in reel: the kicker row (orange square + topic, beat counter), the caption as
    plain type over a gradient to the page colour (the key word orange), the source / footnote row, and — on plain
    pages — the outline-numeral floor below the safe area."""
    on = _caps_on(X) and p.get("caption") is not False
    W, H, P = X.W, X.H, X.portrait
    i, n = X.beat["i"], X.beat["n"]
    topic = parts["topic"] or X.rich(X.channel)
    X.used_text.update(X.channel + "0123456789/")
    kx, ky, kw = (56, 220, 968) if P else (96, 40, 1728)
    kick = (f'<div class="rk" style="left:{kx}px;top:{ky}px;width:{kw}px"><i class="sq"></i><span class="kl">{topic}</span>'
            f'<span class="kc"><b>{i + 1:02d}</b>/{max(n, 1):02d}</span></div>')
    floor = ""
    if not parts["photo"] and P:      # the outline floor sits UNDER the effect (its own clip below the scene), never over it
        fl, _ = outline_row(X, f"{i + 1:02d}", 1530, 380, W, stroke=LINE, H=X.H)
        X.clip(f"{cid}f", t, d, fl, "ctx rlx rlf", 1, track=19, attrs="data-layout-allow-overflow")
        floor = fl
    cap = ""
    fade = ""
    if not on:     # the film's own subtitle pages are off: the effect page carries its spoken line
        cap = f'<div class="cap"><span style="font-size:{parts["cap_px"]}px">{parts["cap"]}</span></div>'
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "") + kick + cap
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx rlx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .rk .sq", {{scale:0, duration:0.2, ease:"back.out(2.4)"}}, {t + 0.02:.3f});')
    wipe_in(X, f"{s} .rk .kl", t + 0.06, 0.3)
    if cap:
        X.tw(f'tl.fromTo("{s} .cap > span", {{clipPath:"inset(100% 0% 0% 0%)", y:20}}, {{clipPath:"inset(0% 0% 0% 0%)", y:0, duration:0.3, ease:"power3.out"}}, {t + 0.05:.3f});')
    if floor:
        r0 = -((30 * t) % 900)
        X.tw(f'tl.fromTo("#{cid}f .rl-row", {{x:{r0:.1f}}}, {{x:{r0 - 30 * d:.1f}, duration:{d:.3f}, ease:"none"}}, {t:.3f});')
