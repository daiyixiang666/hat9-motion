"""editorial · 影像杂志 —— a photo-led magazine feature (NYT Magazine feature openers, Businessweek spreads, Monocle,
Kinfolk): real photographs, page white, one huge serif headline or numeral, thin rules and small tracked sans labels.

Material: page white #fbfaf7, ink #141414, ONE accent per film (vermilion #e2401c: rules, a single word, figure units).
Three grounds: the white page, a full-bleed photograph, and a solid ink page with white type (1–2 beats per film).
Every photo gets the same grade (contrast 1.08, saturate 0.86, warm multiply #f3e9dc at 25 %) under fine grain.

Four page templates, cycled, never the same twice in a row (TEMPLATE maps scene → template):
  A  full-bleed photo, the bottom darkened by a scrim to 62 % black; kicker with a 120 px vermilion rule, then the
     headline (150–200 px serif, white) at y 980–1340 from x 72.                         scenes: cover · ranking
  B  white page: the photo cropped to a tall rectangle with a 1 px ink frame, a 2-column 26 px caption block under
     it like a magazine photo caption, then the numeral (330–520 px serif) with its unit in vermilion.
                                                                                          scenes: figure · compare
  C  split: the photo edge to edge on the top 52 %, a white field below carrying a 3-line pull statement
     (110–140 px serif) hung on an 8 px vermilion bar.                                     scene: statement
  D  ink page: no photo; one chart drawn in white hairlines and a 420–560 px numeral.     scenes: timeline · share
Folio furniture on every page: a running head at y 200 ("FEATURE · 03/08", tracked sans) over a hairline, the page
number bottom-left. Below y 1520 (9:16) the page is never blank: the photo continues (A), a contact strip of three
small crops from the film's other photos (B, C), or the chart's axis field (D).

Charts are magazine infographics: 2 px hairlines, the one series that matters filled vermilion, direct labels, no
legend, no gridlines beyond a baseline, numerals in the serif. Share = one full-column bar; comparison = two numerals
in true size ratio (font size ∝ √value) on one baseline; timeline = a hairline with ticks drawn left to right;
ranking = hairline bars, the leader a solid vermilion bar.

Motion: photos open from a 1 px slit to their rectangle in 12 frames (quint out) and push 1.00 → 1.06 over the beat;
headlines rise line by line from behind a mask (no fade, 4-frame stagger); numerals roll on an odometer and settle
without bounce; rules draw from the left margin outward. Between pages a horizontal page turn: the page slides left
while the next comes in from the right, its photo 3 frames behind the type; entering or leaving the ink page is a
hard cut. Caption: no box, 42 px sans between two hairlines, ink on white, white on photo / ink.

Beat fields (all scenes): "photo" (path), "focus" ("50% 40%"), "kicker", "src", "strip" (three photo paths for the
contact strip; default = the film's other photos), and per scene: cover "head" · figure "num", "unit", "notes"
[2 strings] · compare "items" [{label, value, show, unit}] + "notes" · statement "lines" [3, *word* = vermilion] ·
timeline "num", "unit", "sub", "ticks" [{year, value, now, note}] · share "num", "pct", "parts" [{label, value, on}] ·
ranking "num", "unit", "rows" [{label, value}].
"""
import json, math

from h9 import fit

PAPER, INK, VERM, GREY, LGREY = "#fbfaf7", "#141414", "#e2401c", "#6b6b6b", "#c9c9c9"
TR = 0.55            # page-turn length (s)
LAG = 3 / 30         # the photo arrives 3 frames after the type
TEMPLATE = {"cover": "A", "ranking": "A", "figure": "B", "compare": "B", "statement": "C", "timeline": "D", "share": "D"}
# DM Serif Display advance widths (em) for the odometer columns and numeral fitting
ADV = {"0": .502, "1": .35, "2": .532, "3": .532, "4": .538, "5": .532, "6": .53, "7": .489, "8": .502, "9": .532,
       ".": .3, ",": .3, "%": .871, "+": .541, " ": .218, "−": .541, "-": .4}

STYLE = {
    "name": "影像杂志", "en": "Editorial", "fits": "商业特写、品牌、消费公司、人物与城市",
    "benchmarks": ["The New York Times Magazine feature openers", "Bloomberg Businessweek (2010s)", "Monocle", "Kinfolk", "Pentagram editorial"],
    "tokens": {
        "bg": PAPER, "fg": INK, "muted": GREY, "accent": VERM, "accent2": INK, "alert": VERM,
        "line": "#d9d6cf", "paper": PAPER, "ink": INK, "card": PAPER, "card-fg": INK, "verm": VERM, "grey": GREY,
        "cap-bg": "none", "cap-fg": INK, "cap-size": "42px", "cap-weight": "500", "cap-pad": "10px 0 10px", "cap-radius": "0",
        "cap-shadow": "none", "cap-em": VERM, "cap-bottom": "60px", "punch-top": "70%", "punch-size": "64px", "punch-stroke": "0",
    },
    # a high-contrast display serif for headlines and numerals (DM Serif Display for Latin + digits, Noto Serif SC for 汉字),
    # a neutral grotesque for labels (Archivo + Noto Sans SC), Noto Sans SC medium for the caption
    "fonts": {"display": ["dm-serif", "noto-serif-sc"], "num": ["dm-serif", "noto-serif-sc"], "serif": ["dm-serif", "noto-serif-sc"],
              "body": ["archivo", "noto-sans-sc"], "label": ["archivo", "noto-sans-sc"], "cap": "noto-sans-sc",
              "mono": ["archivo", "noto-sans-sc"], "quote": ["dm-serif", "noto-serif-sc"]},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.133, "cut": "hard", "transition": "hard", "em": "color", "camera": "none"},
    "layers": [("grain", {"opacity": 0.06})],
    "mascot": {"mode": "none"},
    "caption_plate": False,
    "safe_exempt": [".ed-pn"],
    "sfx": {"enter": ("whoosh_soft", 0.12), "transition": ("paper", 0.22), "pop": ("tick", 0.15), "hit": ("tick", 0.2), "count": ("tick", 0.12),
            "mascot": None, "cut": None, "line": ("click", 0.12), "draw": ("brush", 0.08)},
}

GRADE = "contrast(1.08) saturate(.86)"

CSS = r"""
.st-editorial .mascot { display:none !important; }
.ed { position:absolute; inset:0; overflow:hidden; color:var(--ed-fg); --ed-fg:#141414; --ed-src:#6b6b6b; --ed-rule:#141414; }
.ed.dark { --ed-fg:#fff; --ed-src:#c9c9c9; --ed-rule:rgba(255,255,255,.55); }
.ed .gr { position:absolute; inset:0; background:#fbfaf7; z-index:0; }
#root.v .ed-C .hd { color:#fff; } #root.v .ed-C .hl { background:rgba(255,255,255,.6); }
.ed.ed-D .gr, .ed.ed-A .gr { background:#141414; }
.ed .phl { position:absolute; inset:0; z-index:1; }
.ed .ty { position:absolute; inset:0; z-index:2; }
.ed .ph { position:absolute; overflow:visible; }
.ed .ph .msk { position:absolute; inset:0; overflow:hidden; }
.ed .ph .msk img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; filter:""" + GRADE + """; transform-origin:50% 50%; }
.ed .ph .msk::after { content:""; position:absolute; inset:0; background:#f3e9dc; mix-blend-mode:multiply; opacity:.25; pointer-events:none; }
.ed .ph .fr { position:absolute; inset:-1px; border:1px solid #141414; pointer-events:none; }
.ed .scrim { position:absolute; inset:0; pointer-events:none; }
/* furniture */
.ed .hd { position:absolute; display:flex; justify-content:space-between; align-items:baseline; font-family:var(--f-label); font-size:24px; font-weight:500;
  letter-spacing:.14em; text-transform:uppercase; color:var(--ed-fg); white-space:nowrap; line-height:1.2; }
.ed .hd b { font-weight:600; }
.ed .hl { position:absolute; height:1px; background:var(--ed-rule); transform-origin:0 50%; }
.ed .ed-pn { position:absolute; font-family:var(--f-num); font-size:34px; color:var(--ed-fg); line-height:1; white-space:nowrap; }
.ed .ed-pn small { font-family:var(--f-label); font-size:24px; letter-spacing:.14em; margin-left:14px; opacity:.7; }
.ed .src { position:absolute; font-family:var(--f-label); font-size:24px; color:var(--ed-src); letter-spacing:.02em; line-height:1.3; white-space:nowrap; }
.ed .kick { position:absolute; font-family:var(--f-label); font-size:26px; font-weight:500; letter-spacing:.14em; text-transform:uppercase; color:var(--ed-fg); white-space:nowrap; line-height:1.2; }
.ed .rule { position:absolute; height:4px; background:#e2401c; transform-origin:0 50%; }
.ed .hair { position:absolute; height:2px; background:var(--ed-fg); transform-origin:0 50%; }
/* headline: serif, line-masked */
.ed .head { position:absolute; font-family:var(--f-display); font-weight:600; font-synthesis:none; color:var(--ed-fg); white-space:nowrap; }
.ed .ln { display:block; overflow:hidden; padding:0 .04em .08em 0; margin-bottom:-.08em; }
.ed .ln > span { display:block; }
.ed .head .v, .ed .stm .v { color:#e2401c; }
/* numerals: serif, odometer columns */
.ed .num { position:absolute; font-family:var(--f-num); font-weight:400; font-synthesis:none; color:var(--ed-fg); white-space:nowrap; line-height:1; }
.ed .od, .ed .os { display:inline-block; height:1em; overflow:hidden; vertical-align:top; line-height:1; }
.ed .od .odc, .ed .os > span { display:block; }
.ed .od .odc b { display:block; height:1em; font-weight:400; text-align:center; }
.ed .unit { position:absolute; font-family:var(--f-display); font-weight:600; font-synthesis:none; color:#e2401c; line-height:1; white-space:nowrap; }
.ed .lbl { position:absolute; font-family:var(--f-label); font-size:26px; font-weight:500; letter-spacing:.14em; color:var(--ed-fg); white-space:nowrap; line-height:1.2; }
.ed .lbl .v { color:#e2401c; }
.ed .cols { position:absolute; display:flex; gap:32px; font-family:var(--f-label); font-size:26px; line-height:1.45; color:var(--ed-fg); }
.ed .cols > div { flex:1; }
.ed .cols b { font-weight:600; }
/* statement (C) */
.ed .stm { position:absolute; font-family:var(--f-display); font-weight:600; font-synthesis:none; color:#141414; white-space:nowrap; line-height:1.2; }
.ed .qbar { position:absolute; width:8px; background:#e2401c; transform-origin:50% 0; }
/* contact strip + axis field (below the platform line in 9:16: picture only) */
.ed .strip .ph .fr { border-color:rgba(20,20,20,.7); }
.ed .axis { position:absolute; left:0; top:0; width:1500px; height:100%; }
.ed .axis i { position:absolute; width:2px; background:rgba(255,255,255,.26); }
/* charts */
.ed .bar { position:absolute; }
.ed .bar .out { position:absolute; inset:0; border:2px solid var(--ed-fg); opacity:.55; }
.ed .bar .fill { position:absolute; left:0; top:0; bottom:0; background:#e2401c; transform-origin:0 50%; }
.ed .bar .seg { position:absolute; top:0; bottom:0; width:2px; background:var(--ed-fg); opacity:.55; }
.ed .tick { position:absolute; width:2px; background:var(--ed-fg); }
.ed .tick.now { background:#e2401c; width:4px; }
.ed .tlab { position:absolute; font-family:var(--f-num); color:var(--ed-fg); white-space:nowrap; line-height:1; }
.ed .tlab small { font-family:var(--f-label); font-size:24px; letter-spacing:.14em; margin-left:10px; opacity:.75; }
.ed .rowb { position:absolute; height:2px; background:#fff; transform-origin:0 50%; }
.ed .rowb.on { background:#e2401c; }
/* caption: no box, sans between two hairlines; its colour, rules and place change with the page (set on #root per beat) */
#root.st-editorial .clip.cap { top:var(--ec-top, auto); bottom:auto; left:0; right:0; padding-left:var(--ec-pl, 96px); padding-right:var(--ec-pr, 96px); text-align:center; }
#root.st-editorial .clip.cap .cp { display:block; font-family:var(--f-cap); font-size:42px; font-weight:500; line-height:1.35; letter-spacing:.04em; color:var(--ec-fg, #141414);
  text-shadow:none; border-radius:0; padding:10px 24px; border-top:1px solid var(--ec-rule, #141414); border-bottom:1px solid var(--ec-rule, #141414);
  background:var(--ec-band, none); }
#root.st-editorial .clip.cap .em .emt { color:inherit; }
"""

# 9:16 / 16:9 caption skins per template: colour, hairlines, the band behind it, where it sits
CAP = {
    True: {"A": {"--ec-fg": "#ffffff", "--ec-rule": "rgba(255,255,255,.6)", "--ec-top": "1362px", "--ec-pl": "72px", "--ec-pr": "120px", "--ec-band": "none"},
           "B": {"--ec-fg": INK, "--ec-rule": INK, "--ec-top": "1318px", "--ec-pl": "72px", "--ec-pr": "120px", "--ec-band": "none"},
           "C": {"--ec-fg": "#ffffff", "--ec-rule": "rgba(255,255,255,.6)", "--ec-top": "890px", "--ec-pl": "72px", "--ec-pr": "120px",
                 "--ec-band": "linear-gradient(90deg, rgba(0,0,0,0), rgba(0,0,0,.4) 14%, rgba(0,0,0,.4) 86%, rgba(0,0,0,0))"},
           "D": {"--ec-fg": "#ffffff", "--ec-rule": "rgba(255,255,255,.5)", "--ec-top": "1318px", "--ec-pl": "72px", "--ec-pr": "120px", "--ec-band": "none"}},
    False: {"A": {"--ec-fg": "#ffffff", "--ec-rule": "rgba(255,255,255,.6)", "--ec-top": "912px", "--ec-pl": "96px", "--ec-pr": "1000px", "--ec-band": "none"},
            "B": {"--ec-fg": INK, "--ec-rule": INK, "--ec-top": "912px", "--ec-pl": "96px", "--ec-pr": "96px", "--ec-band": "none"},
            "C": {"--ec-fg": INK, "--ec-rule": INK, "--ec-top": "912px", "--ec-pl": "1000px", "--ec-pr": "96px", "--ec-band": "none"},
            "D": {"--ec-fg": "#ffffff", "--ec-rule": "rgba(255,255,255,.5)", "--ec-top": "912px", "--ec-pl": "96px", "--ec-pr": "96px", "--ec-band": "none"}},
}


# ---------------------------------------------------------------- helpers
def esc(s):
    import html
    return html.escape(str(s), quote=True)


def numw(text, px):
    """width in px of a numeral string set in the serif (CJK glyphs count 1 em)."""
    w = 0.0
    for ch in str(text):
        w += ADV.get(ch, 1.0 if ord(ch) > 0x2e80 else 0.55)
    return w * px


def num_px(text, w, lo, hi):
    return max(lo, min(hi, w / max(0.3, numw(text, 1))))


def tpl_at(X, i):
    bs = X.v.get("beats", [])
    if 0 <= i < len(bs):
        return bs[i].get("page") or TEMPLATE.get(bs[i].get("scene"), "B")
    return None


def T(X, b, k, dflt):
    v = b.get(k)
    if v is None:
        return dflt
    return float(X.T(v))


def rich_v(X, s):
    """*word* → the one vermilion word of the line."""
    out, on = [], False
    for part in str(s).split("*"):
        if part:
            out.append(f'<span class="v">{X.rich(part)}</span>' if on else X.rich(part))
        on = not on
    return "".join(out)


def lines_html(X, lines):
    return "".join(f'<span class="ln"><span>{rich_v(X, l)}</span></span>' for l in lines)


def odo(X, text):
    """an odometer numeral: every digit a column (blank, 0–9) inside a 1 em mask; other glyphs rise from their own mask."""
    X.used_text.update("0123456789" + str(text))
    out = []
    for ch in str(text):
        if ch.isdigit():
            col = "<b>&#8203;</b>" + "".join(f"<b>{k}</b>" for k in range(10))      # a blank first row: nothing shows before the roll
            out.append(f'<span class="od" data-d="{ch}" style="width:{ADV[ch]:.3f}em"><span class="odc">{col}</span></span>')
        else:
            out.append(f'<span class="os"><span>{esc(ch)}</span></span>')
    return "".join(out)


ROLL = 10 / 30       # one digit column rolls in 10 frames
ROLL_ST = 2 / 30     # the next column starts 2 frames later


def roll(X, sel, t, dur=None):
    """digits roll up to their value in 10 frames each, 2 frames apart, and settle without overshoot (quint out);
    non-digits rise from their masks with them."""
    X.tw(f'(()=>{{document.querySelectorAll("{sel} .od").forEach((el,k)=>{{const d=+el.dataset.d; '
         f'tl.fromTo(el.firstElementChild, {{yPercent:0}}, {{yPercent:-(1+d)*100/11, duration:{ROLL:.4f}, ease:"power4.out"}}, {t:.3f}+{ROLL_ST:.4f}*k);}});}})();')
    X.tw(f'tl.from("{sel} .os > span", {{yPercent:105, duration:{ROLL:.4f}, ease:"power4.out", stagger:{ROLL_ST:.4f}}}, {t + ROLL_ST:.3f});')
    X.sfx(t, "count")


def rise(X, sel, t, dur=0.6):
    """headline lines rise 100 % from behind their masks, 4 frames apart."""
    X.tw(f'tl.from("{sel} .ln > span", {{yPercent:100, duration:{dur}, ease:"expo.out", stagger:{4 / 30:.4f}}}, {t:.3f});')


def draw(X, sel, t, dur=0.5, ease="power3.inOut"):
    """a rule draws from the left margin outward."""
    X.tw(f'tl.fromTo("{sel}", {{scaleX:0}}, {{scaleX:1, duration:{dur}, ease:"{ease}"}}, {t:.3f});')


def slit(X, sel, t):
    """the image mask opens from a 1 px slit to its rectangle in 12 frames (ease-out quint)."""
    X.tw(f'tl.fromTo("{sel} .msk", {{clipPath:"inset(0% 49.95% 0% 49.95%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.4, ease:"power4.out"}}, {t:.3f});')
    X.tw(f'tl.from("{sel} .fr", {{scaleX:0, duration:0.4, ease:"power4.out"}}, {t:.3f});')


def photo(X, src, x, y, w, h, focus="50% 50%", frame=True, cls=""):
    url = X.asset(src)
    fr = '<i class="fr"></i>' if frame else ""
    return (f'<div class="ph {cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
            f'<div class="msk"><img src="{url}" alt="" style="object-position:{focus}"></div>{fr}</div>')


def film_photos(X):
    out = list(X.v.get("meta", {}).get("strip_extra", []))
    for b in X.v.get("beats", []):
        if b.get("photo") and b["photo"] not in out:
            out.append(b["photo"])
    return out


def strip(X, b, y0=1556, y1=1840):
    """contact strip: three small crops from the film's other photos, under the platform line (picture only)."""
    if not X.portrait:
        return ""
    pool = b.get("strip") or [p for p in film_photos(X) if p != b.get("photo")]
    if not pool:
        return ""
    k0 = X.beat["i"]
    picks = [pool[(k0 + j) % len(pool)] for j in range(3)]
    gap = 24
    w = (936 - 2 * gap) / 3
    html = ""
    for j, p in enumerate(picks):
        html += photo(X, p, 72 + j * (w + gap), y0, w, y1 - y0, "50% 50%", True, f"sp sp{j}")
    return f'<div class="strip">{html}</div>'


def axis(X, y0=1560, y1=1880):
    """the chart's axis field continued under the platform line: a ruler of white hairlines (picture only)."""
    if not X.portrait:
        return ""
    ticks = ""
    for k in range(0, 31):
        x = 72 + k * 936 / 20
        h = (y1 - y0) if k % 5 == 0 else (y1 - y0) * 0.38
        ticks += f'<i style="left:{x:.1f}px;top:{y0}px;height:{h:.0f}px"></i>'
    return f'<div class="axis">{ticks}<i style="left:72px;top:{y0}px;width:1404px;height:1px"></i></div>'


def axis_drift(X, s, t, d):
    """the axis field keeps sliding left under the chart, one major division per beat (linear, never stops)."""
    if X.portrait:
        X.tw(f'tl.fromTo("{s} .axis", {{x:0}}, {{x:{-936 / 4:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def cap_skin(X, t, tpl):
    X.tw(f'tl.set("#root", {json.dumps(CAP[X.portrait][tpl])}, {max(0.0, t - 0.02):.3f});')


def folio(X, b, dark, tpl="B"):
    """running head + hairline, source line, page number."""
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    P = X.portrait
    kicker = meta.get("folio", "FEATURE")
    chan = X.channel if i == n - 1 else meta.get("issue", "")      # the channel placeholder only on the last page
    src = b.get("src", "")
    X.used_text.update(kicker + chan + src + "0123456789/·来源：P.")
    if P:
        hd = (f'<div class="hd" style="left:72px;right:72px;top:200px"><span><b>{X.rich(kicker)}</b> · {i + 1:02d}/{n:02d}</span><span>{X.rich(chan)}</span></div>'
              f'<i class="hl" style="left:72px;width:936px;top:242px"></i>')
        pn = f'<div class="ed-pn" style="left:72px;top:1862px">{i + 1:02d}<small>{X.rich(meta.get("folio_tag", ""))}</small></div>'
        sx, sy, sw = 72, 1462, 888
    else:
        hd = (f'<div class="hd" style="left:96px;right:96px;top:40px"><span><b>{X.rich(kicker)}</b> · {i + 1:02d}/{n:02d}</span><span>{X.rich(chan)}</span></div>'
              f'<i class="hl" style="left:96px;width:1728px;top:82px"></i>')
        pn = f'<div class="ed-pn" style="right:96px;top:1016px">{i + 1:02d}</div>'
        sx, sy, sw = (1000, 1010, 760) if tpl == "C" else (96, 1010, 1500)
    s = ""
    if src:
        f = fit.fit_text("来源：" + src, sw, 34, 24, 22, max_lines=1)
        s = f'<div class="src" style="left:{sx}px;top:{sy}px;font-size:{f.px:.0f}px">{X.rich(f.lines[0] if f.lines else "")}</div>'
    return hd + pn + s


def page(X, b, cid, t, d, tpl, phot, body, scrim=""):
    """one magazine page: ground, photo layer, type layer, folio. Between two non-ink pages it turns like a page
    (horizontal push, the photo 3 frames behind the type); into or out of the ink page it is a hard cut."""
    i = X.beat["i"]
    dark = tpl in ("A", "D")
    prev_t, next_t = tpl_at(X, i - 1), tpl_at(X, i + 1)
    push_in = i > 0 and prev_t is not None and prev_t != "D" and tpl != "D"
    push_out = next_t is not None and next_t != "D" and tpl != "D"
    D_ = X.duration or (t + d)
    ext = min(d + TR, max(d, D_ - t)) if push_out else d
    html = (f'<div class="ed ed-{tpl}{" dark" if dark else ""}"><div class="gr"></div><div class="phl">{phot}{scrim}</div>'
            f'<div class="ty">{body}{folio(X, b, dark, tpl)}</div></div>')
    X.clip(cid, t, ext, html, "scene", 2 + i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    W = X.W
    if push_in:
        X.tw(f'tl.from("{s} .gr, {s} .ty", {{x:{W}, duration:{TR}, ease:"power3.inOut"}}, {t:.3f});')
        X.tw(f'tl.from("{s} .phl", {{x:{W}, duration:{TR}, ease:"power3.inOut"}}, {t + LAG:.3f});')
        X.sfx(t, "transition")
    if push_out:
        X.tw(f'tl.to("{s} .ed", {{x:{-W}, duration:{TR}, ease:"power3.inOut"}}, {t + d:.3f});')
    cap_skin(X, t, tpl)
    # furniture: the running-head hairline draws from the margin, the head and page number rise
    t0 = t + (TR * 0.6 if push_in else 0.05)
    if tpl != "D":          # the ink page arrives on a hard cut with its folio already printed
        draw(X, f"{s} .hl", t0, 0.6, "power3.out")
        X.tw(f'tl.from("{s} .hd > span, {s} .ed-pn", {{yPercent:110, opacity:0, duration:0.45, ease:"expo.out", stagger:0.05}}, {t0 + 0.1:.3f});')
    X.tw(f'tl.from("{s} .src", {{x:-24, opacity:0, duration:0.45, ease:"expo.out"}}, {t0 + 0.6:.3f});')
    return s, t0, ext


def push(X, sel, t, dur):
    """the photo's slow push, 1.00 → 1.06 over the beat."""
    X.tw(f'tl.fromTo("{sel} .msk img", {{scale:1.0}}, {{scale:1.06, duration:{dur:.2f}, ease:"none"}}, {t:.3f});')


def strip_in(X, s, t):
    for j in range(3):
        slit(X, f"{s} .sp{j}", t + 0.08 * j)


def kicker(X, text, x, y, rule=True):
    if not text:
        return ""
    X.used_text.update(text)
    r = f'<i class="rule" style="left:{x}px;top:{y - 22}px;width:120px"></i>' if rule else ""
    return r + f'<div class="kick" style="left:{x}px;top:{y}px">{X.rich(text)}</div>'


def kicker_in(X, s, t):
    draw(X, f"{s} .rule", t, 0.45, "power3.out")
    X.tw(f'tl.from("{s} .kick", {{yPercent:100, opacity:0, duration:0.45, ease:"expo.out"}}, {t + 0.12:.3f});')


# ---------------------------------------------------------------- A · full-bleed photo
SCRIM_A = {
    True: ("linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 17%, rgba(0,0,0,0) {a}%, rgba(0,0,0,.62) {b}%, rgba(0,0,0,.62) 100%)"),
    False: ("linear-gradient(90deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.62) 34%, rgba(0,0,0,0) 66%), "
            "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 14%, rgba(0,0,0,0) 70%, rgba(0,0,0,.5) 100%)"),
}


def scrim_a(X, a=46, b_=62):
    g = SCRIM_A[X.portrait].format(a=a, b=b_)
    return f'<div class="scrim" style="background:{g}"></div>'


def cover(b, X, t, d, cid):
    """A · cover: full-bleed photo opens from a slit and pushes in; the kicker's vermilion rule draws, then the serif
    headline rises line by line out of its masks."""
    P, W, H = X.portrait, X.W, X.H
    head = [l for l in str(b.get("head", "")).split("|") if l]
    X.used_text.update("".join(head))
    if P:
        hf = fit.fit_text("|".join(h.replace("*", "") for h in head), 888, 380, 200, 150, lh=1.2, max_lines=len(head) or 1)
        px = max(150, hf.px)
        y0 = 1340 - px * 1.2 * len(head)
        ky = y0 - 56
        body = kicker(X, b.get("kicker", ""), 72, ky) + f'<div class="head" style="left:72px;top:{y0:.0f}px;font-size:{px:.0f}px;line-height:1.2">{lines_html(X, head)}</div>'
    else:
        hf = fit.fit_text("|".join(h.replace("*", "") for h in head), 860, 360, 170, 120, lh=1.2, max_lines=len(head) or 1)
        px = hf.px
        y0 = 840 - px * 1.2 * len(head)
        body = kicker(X, b.get("kicker", ""), 96, y0 - 56) + f'<div class="head" style="left:96px;top:{y0:.0f}px;font-size:{px:.0f}px;line-height:1.2">{lines_html(X, head)}</div>'
    ph = photo(X, b["photo"], 0, 0, W, H, b.get("focus", "50% 50%"), False, "hero")
    s, t0, ext = page(X, b, cid, t, d, "A", ph, body, scrim_a(X, 34, 54))
    slit(X, f"{s} .hero", t + (0.3 if t0 > t + 0.1 else 0.05))
    push(X, f"{s} .hero", t, ext)
    kicker_in(X, s, t0 + 0.35)
    rise(X, f"{s} .head", T(X, b, "at_head", t0 + 0.55), 0.7)
    X.sfx(t0 + 0.55, "enter")


def ranking(b, X, t, d, cid):
    """A · ranking: full-bleed photo under a deep scrim; the total rolls up on the odometer, then hairline bars draw out
    one by one, the leader a solid vermilion bar, each value landing at its bar's end."""
    P, W, H = X.portrait, X.W, X.H
    rows = b.get("rows", [])[:4]
    vmax = max([float(r.get("value", 0) or 0) for r in rows] or [1]) or 1
    num, unit = str(b.get("num", "")), b.get("unit", "")
    X.used_text.update(unit)
    if P:
        x0, ny, bx, bw, ry, rh = 72, 700, 272, 500, 1030, 96
        npx = num_px(num, 640, 230, 280)
    else:
        x0, ny, bx, bw, ry, rh = 96, 200, 300, 560, 540, 92
        npx = num_px(num, 620, 220, 280)
    nw = numw(num, npx)
    body = kicker(X, b.get("kicker", ""), x0, ny - 50)
    body += f'<div class="num big" style="left:{x0}px;top:{ny}px;font-size:{npx:.0f}px">{odo(X, num)}</div>'
    body += f'<div class="unit" style="left:{x0 + nw + 18:.0f}px;top:{ny + npx * 0.62:.0f}px;font-size:{64 if P else 56}px;color:#fff">{X.rich(unit)}</div>'
    for k, r in enumerate(rows):
        v = float(r.get("value", 0) or 0)
        y = ry + k * rh
        L = max(24, bw * v / vmax)              # true ratio, but never thinner than 24 px so the smallest still shows
        X.used_text.update(str(r.get("label", "")) + str(r.get("show", v)))
        bh = 14 if k == 0 else 10
        body += (f'<div class="lbl rl" data-k="{k}" style="left:{x0}px;top:{y + 8:.0f}px;font-size:34px;letter-spacing:.08em">{X.rich(r.get("label", ""))}</div>'
                 f'<i class="rowb{" on" if k == 0 else ""}" data-k="{k}" style="left:{bx}px;top:{y + 30 - bh / 2:.0f}px;width:{L:.0f}px;height:{bh}px"></i>'
                 f'<div class="tlab rv" data-k="{k}" style="left:{bx + L + 20:.0f}px;top:{y:.0f}px;font-size:58px">{X.rich(r.get("show", v))}</div>')
    ph = photo(X, b["photo"], 0, 0, W, H, b.get("focus", "50% 50%"), False, "hero")
    scr = scrim_a(X, 12, 30) if P else ('<div class="scrim" style="background:linear-gradient(90deg, rgba(0,0,0,.66) 0%, '
                                         'rgba(0,0,0,.62) 55%, rgba(0,0,0,.2) 85%)"></div>')
    s, t0, ext = page(X, b, cid, t, d, "A", ph, body, scr)
    slit(X, f"{s} .hero", t + (0.3 if t0 > t + 0.1 else 0.05))
    push(X, f"{s} .hero", t, ext)
    kicker_in(X, s, t0 + 0.3)
    tn = T(X, b, "at_num", t0 + 0.45)
    roll(X, f"{s} .big", tn, 1.3)
    X.tw(f'tl.from("{s} .unit", {{yPercent:60, opacity:0, duration:0.45, ease:"expo.out"}}, {tn + 0.9:.3f});')
    for k in range(len(rows)):
        tk = tn + 0.9 + 0.32 * k
        X.tw(f'tl.from("{s} .rl[data-k=\'{k}\']", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {tk:.3f});')
        draw(X, f"{s} .rowb[data-k='{k}']", tk + 0.05, 0.6, "power3.out")
        X.tw(f'tl.from("{s} .rv[data-k=\'{k}\']", {{yPercent:60, opacity:0, duration:0.4, ease:"expo.out"}}, {tk + 0.5:.3f});')
        X.sfx(tk + 0.05, "line")


# ---------------------------------------------------------------- B · white page, tall photo + numeral
def b_frame(X, b):
    """photo rectangle, caption block, numeral box for template B."""
    if X.portrait:
        return {"ph": (72, 268, 936, 624), "cols": (72, 914, 888), "nx": 72, "ny": 990, "nw": 888}
    return {"ph": (1008, 128, 816, 752), "cols": (96, 742, 816), "nx": 96, "ny": 330, "nw": 816}


def notes_html(X, notes, x, y, w):
    X.used_text.update("".join(notes))
    return f'<div class="cols" style="left:{x}px;top:{y}px;width:{w}px">' + "".join(f'<div>{rich_b(X, n)}</div>' for n in notes[:2]) + "</div>"


def rich_b(X, s):
    """**bold** inside a caption block; | = line break."""
    out, on = [], False
    for part in str(s).split("**"):
        if part:
            out.append(f"<b>{X.rich(part)}</b>" if on else X.rich(part))
        on = not on
    return "".join(out)


def figure(b, X, t, d, cid):
    """B · figure: the tall photo opens from a slit; its caption block rises; the huge serif numeral rolls in on the
    odometer and its vermilion unit drops into place beside it."""
    P = X.portrait
    F = b_frame(X, b)
    num, unit = str(b.get("num", "")), b.get("unit", "")
    X.used_text.update(unit)
    upx = 90
    ulines = [u for u in str(unit).split("|") if u]
    uw = max([fit.width(u) for u in ulines] or [0]) * upx
    npx = num_px(num, F["nw"] - uw - 18, 330, 520)
    nw = numw(num, npx)
    ph = photo(X, b["photo"], *F["ph"], b.get("focus", "50% 50%"), True, "hero")
    cx, cy, cw = F["cols"]
    body = notes_html(X, b.get("notes", []), cx, cy, cw)
    if not P:
        body += kicker(X, b.get("kicker", ""), 96, 240)
    ny = F["ny"]
    body += f'<div class="num big" style="left:{F["nx"]}px;top:{ny}px;font-size:{npx:.0f}px">{odo(X, num)}</div>'
    body += (f'<div class="unit" style="left:{F["nx"] + nw + 18:.0f}px;top:{ny + npx * 0.2:.0f}px;font-size:{upx}px;line-height:1.05">'
             + "<br>".join(X.rich(u) for u in ulines) + "</div>")
    body += strip(X, b)
    s, t0, ext = page(X, b, cid, t, d, "B", ph, body)
    slit(X, f"{s} .hero", t0 + 0.05)
    push(X, f"{s} .hero", t, ext)
    if not P:
        kicker_in(X, s, t0 + 0.2)
    X.tw(f'tl.from("{s} .cols > div", {{yPercent:40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t0 + 0.35:.3f});')
    tn = T(X, b, "at_num", t0 + 0.45)
    roll(X, f"{s} .big", tn, 1.4)
    X.tw(f'tl.from("{s} .unit", {{y:-40, opacity:0, duration:0.5, ease:"expo.out"}}, {tn + 1.0:.3f});')
    strip_in(X, s, t0 + 0.6)


def compare(b, X, t, d, cid):
    """B · compare: two numerals side by side in true size ratio (font size ∝ √value) sharing one baseline; both roll
    up together, the larger one's vermilion rule draws under it."""
    P = X.portrait
    F = b_frame(X, b)
    items = b.get("items", [])[:2]
    vals = [float(it.get("value", 1) or 1) for it in items]
    shows = [str(it.get("show", it.get("value", ""))) for it in items]
    gap = 64
    k = [math.sqrt(v / max(vals)) for v in vals]
    em = sum(numw(sh, 1) * kk for sh, kk in zip(shows, k))
    big = min(300, (F["nw"] - gap) / max(0.3, em))
    ph = photo(X, b["photo"], *F["ph"], b.get("focus", "50% 50%"), True, "hero")
    cx, cy, cw = F["cols"]
    body = notes_html(X, b.get("notes", []), cx, cy, cw)
    if not P:
        body += kicker(X, b.get("kicker", ""), 96, 240)
    base = (F["ny"] + 300) if P else (F["ny"] + 330)       # shared baseline (ink bottom) of both numerals
    x = F["nx"]
    for j, (it, sh, kk) in enumerate(zip(items, shows, k)):
        px = big * kk
        top = base - px * 0.87                              # ink bottom sits 0.87 em below the line box top (line-height 1)
        lab = it.get("label", "")
        X.used_text.update(lab + it.get("unit", ""))
        body += (f'<div class="lbl cl" data-k="{j}" style="left:{x:.0f}px;top:{top + px * 0.12 - 46:.0f}px">{X.rich(lab)}'
                 + (f' <span class="v">{X.rich(it.get("unit", ""))}</span>' if it.get("unit") else "") + "</div>"
                 f'<div class="num cn" data-k="{j}" style="left:{x:.0f}px;top:{top:.0f}px;font-size:{px:.0f}px">{odo(X, sh)}</div>')
        if j == 0:
            body += f'<i class="rule cr" style="left:{x:.0f}px;top:{base + 16:.0f}px;width:{numw(sh, px):.0f}px"></i>'
        x += numw(sh, px) + gap
    body += f'<i class="hair base" style="left:{F["nx"]}px;top:{base + 2:.0f}px;width:{x - gap - F["nx"]:.0f}px;height:1px;opacity:.5"></i>'
    body += strip(X, b)
    s, t0, ext = page(X, b, cid, t, d, "B", ph, body)
    slit(X, f"{s} .hero", t0 + 0.05)
    push(X, f"{s} .hero", t, ext)
    if not P:
        kicker_in(X, s, t0 + 0.2)
    X.tw(f'tl.from("{s} .cols > div", {{yPercent:40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.08}}, {t0 + 0.35:.3f});')
    tn = T(X, b, "at_num", t0 + 0.5)
    draw(X, f"{s} .base", tn - 0.15, 0.6, "power3.out")
    for j in range(len(items)):
        X.tw(f'tl.from("{s} .cl[data-k=\'{j}\']", {{yPercent:100, opacity:0, duration:0.45, ease:"expo.out"}}, {tn + 0.25 * j:.3f});')
        roll(X, f"{s} .cn[data-k='{j}']", tn + 0.25 * j, 1.3)
    draw(X, f"{s} .cr", tn + 1.3, 0.5, "power3.out")
    strip_in(X, s, t0 + 0.6)


# ---------------------------------------------------------------- C · split: photo on top, pull statement below
def statement(b, X, t, d, cid):
    """C · statement: the photo opens edge to edge across the top 52 %; the vermilion quotation bar drops down the
    margin and the three serif lines rise out of their masks beside it."""
    P, W, H = X.portrait, X.W, X.H
    lines = [l for l in b.get("lines", []) if l][:3]
    X.used_text.update("".join(l.replace("*", "") for l in lines))
    if P:
        ph = photo(X, b["photo"], 0, 0, W, 1000, b.get("focus", "50% 50%"), False, "hero")
        f = fit.fit_text("|".join(l.replace("*", "") for l in lines), 840, 420, 140, 110, lh=1.2, max_lines=len(lines))
        px = max(110, f.px)
        x, y = 112, 1036
        bar = f'<i class="qbar" style="left:72px;top:{y + px * 0.12:.0f}px;height:{px * 1.2 * len(lines) - px * 0.3:.0f}px"></i>'
        scrim = ('<div class="scrim" style="height:1000px;background:linear-gradient(180deg, rgba(0,0,0,.55) 0%, rgba(0,0,0,0) 30%, '
                 'rgba(0,0,0,0) 70%, rgba(0,0,0,.62) 100%)"></div>')
        body = bar + f'<div class="stm" style="left:{x}px;top:{y}px;font-size:{px:.0f}px">{lines_html(X, lines)}</div>' + strip(X, b)
    else:
        ph = photo(X, b["photo"], 0, 0, 900, H, b.get("focus", "50% 50%"), False, "hero")
        f = fit.fit_text("|".join(l.replace("*", "") for l in lines), 820, 560, 140, 96, lh=1.2, max_lines=len(lines))
        px = f.px
        x, y = 1010, 180 + (600 - px * 1.2 * len(lines)) / 2
        bar = f'<i class="qbar" style="left:966px;top:{y + px * 0.12:.0f}px;height:{px * 1.2 * len(lines) - px * 0.3:.0f}px"></i>'
        scrim = '<div class="scrim" style="left:0;width:900px;background:linear-gradient(180deg, rgba(0,0,0,.42) 0%, rgba(0,0,0,0) 16%)"></div>'
        body = bar + f'<div class="stm" style="left:{x}px;top:{y:.0f}px;font-size:{px:.0f}px">{lines_html(X, lines)}</div>'
    s, t0, ext = page(X, b, cid, t, d, "C", ph, body, scrim)
    slit(X, f"{s} .hero", t + (0.3 if t0 > t + 0.1 else 0.05))
    push(X, f"{s} .hero", t, ext)
    ts = T(X, b, "at_lines", t0 + 0.4)
    X.tw(f'tl.from("{s} .qbar", {{scaleY:0, duration:0.55, ease:"power3.out"}}, {ts - 0.1:.3f});')
    rise(X, f"{s} .stm", ts, 0.7)
    X.sfx(ts, "enter")
    strip_in(X, s, t0 + 0.7)
    if not P:     # 16:9: the running head crosses photo and paper, so it is set in ink on a paper slip at the right
        X.css("ed-c16", "#root.h .ed-C .hd { left:1000px !important; } #root.h .ed-C .hl { left:1000px !important; width:824px !important; }")


# ---------------------------------------------------------------- D · ink page, white hairline chart
def timeline(b, X, t, d, cid):
    """D · timeline: hard cut to ink with the hero numeral rolling on the cut; a hairline draws left to right and each
    tick stands up as the line reaches it, the current year in vermilion; last, the forecast stretch draws dashed with
    its growth label."""
    P = X.portrait
    num, unit, sub = str(b.get("num", "")), b.get("unit", ""), b.get("sub", "")
    ticks = b.get("ticks", [])[:5]
    X.used_text.update(unit + sub)
    if P:
        x0, w, ny, npx = 72, 936, 330, num_px(num, 888, 420, 560)
        ly, uy = 1150, ny + npx * 0.95
    else:
        x0, w, ny, npx = 96, 1728, 100, 500              # 16:9: the numeral at ≥ 45 % of the frame height
        ly, uy = 720, ny + npx * 0.42
    nw = numw(num, npx)
    body = kicker(X, b.get("kicker", ""), x0, ny - 30) if P else kicker(X, b.get("kicker", ""), x0 + nw + 34, ny + npx * 0.7)
    body += f'<div class="num big" style="left:{x0}px;top:{ny}px;font-size:{npx:.0f}px">{odo(X, num)}</div>'
    if P:
        body += f'<div class="unit" style="left:{x0}px;top:{uy:.0f}px;font-size:72px">{X.rich(unit)}</div>'
        body += f'<div class="lbl sb" style="left:{x0 + fit.width(unit) * 72 + 30:.0f}px;top:{uy + 26:.0f}px;font-size:36px">{X.rich(sub)}</div>'
    else:
        body += f'<div class="unit" style="left:{x0 + nw + 30:.0f}px;top:{ny + npx * 0.22:.0f}px;font-size:80px">{X.rich(unit)}</div>'
        body += f'<div class="lbl sb" style="left:{x0 + nw + 34:.0f}px;top:{ny + npx * 0.22 + 110:.0f}px;font-size:34px">{X.rich(sub)}</div>'
    n = max(1, len(ticks))
    kn = next((k for k, tk in enumerate(ticks) if tk.get("now")), n - 1)
    fn = (kn + 0.5) / n if kn < n - 1 else 1.0          # the solid line runs to "now"; the forecast part is dashed
    body += f'<i class="hair tl" style="left:{x0}px;top:{ly}px;width:{w * fn:.0f}px"></i>'
    if fn < 1:          # the forecast zone: a faint panel behind the projected years, wiped in with the dashed stretch
        zx = x0 + w * fn
        body += (f'<i class="fz" style="position:absolute;left:{zx:.0f}px;top:{ly - 190:.0f}px;width:{x0 + w - zx + (0 if P else 0):.0f}px;'
                 f'height:{(150 if P else 140) + 190:.0f}px;background:rgba(255,255,255,.09);transform-origin:0 50%"></i>')
        body += (f'<i class="hair tld" style="left:{x0 + w * fn:.0f}px;top:{ly}px;width:{w * (1 - fn):.0f}px;'
                 f'background:repeating-linear-gradient(90deg, #fff 0 14px, transparent 14px 26px)"></i>')
    for k, tk in enumerate(ticks):
        fx = (k + 0.5) / n
        x = x0 + w * fx
        now = tk.get("now")
        dashed = tk.get("note")
        X.used_text.update(str(tk.get("year", "")) + str(tk.get("value", "")) + str(tk.get("note", "")))
        th = 70 if now else 44
        dsh = ";background:repeating-linear-gradient(180deg, #fff 0 8px, transparent 8px 14px)" if dashed else ""
        body += f'<i class="tick{" now" if now else ""}" data-k="{k}" style="left:{x - (2 if now else 1):.0f}px;top:{ly - th:.0f}px;height:{th}px{dsh}"></i>'
        body += (f'<div class="tlab ty_" data-k="{k}" style="left:{x - 120:.0f}px;width:240px;text-align:center;top:{ly - th - 52:.0f}px;font-size:38px">'
                 f'{X.rich(tk.get("year", ""))}</div>')
        vcol = VERM if now else ("#dcdcdc" if dashed else "#fff")
        body += (f'<div class="tlab tv" data-k="{k}" style="left:{x - 160:.0f}px;width:320px;text-align:center;top:{ly + 24:.0f}px;font-size:{(92 if now else 76) if P else (120 if now else 100)}px;color:{vcol}">'
                 f'{X.rich(tk.get("value", ""))}</div>')
        if dashed:          # the forecast note sits above its year label, clear of the caption band
            body += (f'<div class="lbl tv" data-k="{k}" style="left:{x - 120:.0f}px;width:240px;text-align:center;top:{ly - th - 96:.0f}px;font-size:26px;color:#c9c9c9">'
                     f'{X.rich(dashed)}</div>')
    arc = None
    for k in range(len(ticks) - 1):
        if ticks[k].get("now") and ticks[k + 1].get("delta"):
            xa, xb = x0 + w * (k + 0.5) / n, x0 + w * (k + 1.5) / n
            top = ly - 70 - 120
            X.used_text.update(str(ticks[k + 1]["delta"]))
            body += (f'<div class="lbl arcl" style="left:{(xa + xb) / 2 - 100:.0f}px;width:200px;text-align:center;top:{ly - 58:.0f}px;'
                     f'font-size:{40 if P else 52}px;color:{VERM}">{X.rich(ticks[k + 1]["delta"])}</div>')
            arc = True
    body += axis(X)
    s, t0, ext = page(X, b, cid, t, d, "D", "", body)
    axis_drift(X, s, t, d)
    kicker_in(X, s, t)
    tn = T(X, b, "at_num", t)                        # the numeral rolls on the cut
    roll(X, f"{s} .big", tn)
    X.tw(f'tl.from("{s} .unit, {s} .sb", {{yPercent:80, opacity:0, duration:0.4, ease:"expo.out", stagger:0.08}}, {tn + 0.3:.3f});')
    tl0 = T(X, b, "at_line", t + 0.6)
    dur = 2.4                                        # slow enough that each year lands as its own moment
    draw(X, f"{s} .tl", tl0, dur * fn, "sine.in" if fn < 1 else "sine.inOut")
    if fn < 1:      # the forecast stretch draws later, as its own step
        tf_ = tl0 + dur * fn + 1.0
        draw(X, f"{s} .tld", tf_, max(0.6, dur * (1 - fn)), "power2.inOut")
        draw(X, f"{s} .fz", tf_ - 0.1, 0.7, "power3.out")
        X.sfx(tf_, "draw")
        if arc:
            X.tw(f'tl.from("{s} .arcl", {{yPercent:80, opacity:0, duration:0.45, ease:"expo.out"}}, {tf_ + 0.35:.3f});')
    X.sfx(tl0, "draw")
    for k in range(len(ticks)):
        tk = tl0 + dur * (k + 0.5) / n
        if fn < 1 and k > kn:
            tk = tf_ + 0.45            # forecast ticks stand up as the dashed stretch reaches them
        X.tw(f'tl.from("{s} .tick[data-k=\'{k}\']", {{scaleY:0, transformOrigin:"50% 100%", duration:0.35, ease:"power3.out"}}, {tk - 0.1:.3f});')
        X.tw(f'tl.from("{s} .ty_[data-k=\'{k}\'], {s} .tv[data-k=\'{k}\']", {{yPercent:50, opacity:0, duration:0.4, ease:"expo.out", stagger:0.06}}, {tk:.3f});')
    X.tw(f'tl.from("{s} .axis i", {{scaleY:0, transformOrigin:"50% 0%", duration:0.5, ease:"power3.out", stagger:0.015}}, {t + 0.2:.3f});')


def share(b, X, t, d, cid):
    """D · share: hard cut to ink with the giant percentage rolling on the cut; a 50 % mark drops onto an empty
    full-column bar, the vermilion fill runs past it, then the remainder splits at hairlines and each part is labelled
    on its own segment; the sum underneath closes the page."""
    P = X.portrait
    num = str(b.get("num", ""))
    pct = max(0.5, min(99.5, float(b.get("pct", 50))))
    parts = b.get("parts", [])[:3]
    tot = sum(float(p.get("value", 0) or 0) for p in parts) or 1
    core_ = num.rstrip("%")
    if P:
        x0, w, ny, npx = 72, 936, 330, num_px(core_, 760, 420, 520)
        by, bh = 950, 120
    else:
        x0, w, ny, npx = 96, 1728, 110, 500            # 16:9: the numeral at ≥ 45 % of the frame height
        by, bh = 690, 110
    nw = numw(core_, npx)
    body = kicker(X, b.get("kicker", ""), x0, ny - 30) if P else kicker(X, b.get("kicker", ""), x0 + nw + 30, ny + npx * 0.7)
    body += f'<div class="num big" style="left:{x0}px;top:{ny}px;font-size:{npx:.0f}px">{odo(X, core_)}</div>'
    body += f'<div class="unit pc" style="left:{x0 + nw + 10:.0f}px;top:{ny + npx * 0.2:.0f}px;font-size:{npx * 0.42:.0f}px;font-family:var(--f-num);font-weight:400">%</div>'
    segs, labs = "", ""
    acc = 0.0
    for k, p in enumerate(parts):
        v = float(p.get("value", 0) or 0)
        a = acc / tot
        acc += v
        X.used_text.update(str(p.get("label", "")) + str(p.get("show", "")))
        if k:
            segs += f'<i class="seg" style="left:{a * 100:.2f}%;opacity:.8"></i>'
        if p.get("on"):            # the series that matters: one white line above its fill, ≥ 40 px
            labs += (f'<div class="tlab pl on" data-k="{k}" style="left:{x0}px;top:{by - 70}px;font-size:44px">'
                     f'<span style="font-family:var(--f-label);font-size:34px;letter-spacing:.08em;margin-right:16px">{X.rich(p.get("label", ""))}</span>{X.rich(p.get("show", ""))}</div>')
        else:                       # the rest: labelled inside their own segment
            sx = x0 + w * a + 14
            lab = p.get("label", "")
            labs += (f'<div class="pl in" data-k="{k}" style="position:absolute;left:{sx:.0f}px;top:{by + 14}px;color:#fff;line-height:1.1">'
                     f'<div style="font-family:var(--f-label);font-size:26px;letter-spacing:.06em;white-space:nowrap">{X.rich(lab)}</div>'
                     f'<div style="font-family:var(--f-num);font-size:50px;white-space:nowrap">{X.rich(p.get("show", ""))}</div></div>')
    body += (f'<div class="bar" style="left:{x0}px;top:{by}px;width:{w}px;height:{bh}px"><i class="out" style="opacity:.8"></i>'
             f'<i class="fill" style="width:{pct:.2f}%"></i>{segs}</div>' + labs)
    hx = x0 + w * 0.5
    body += (f'<i class="half" style="position:absolute;left:{hx - 1:.0f}px;top:{by - 22}px;width:2px;height:{bh + 44}px;background:#fff;transform-origin:50% 0"></i>'
             f'<div class="lbl halfl" style="left:{hx + 10:.0f}px;top:{by - 40}px;font-size:24px">50%</div>')
    X.used_text.update("50%")
    if b.get("sum"):
        X.used_text.update(str(b["sum"]))
        body += f'<div class="lbl sum" style="left:{x0}px;top:{by + bh + (40 if P else 26)}px;font-size:{34 if P else 30}px;letter-spacing:.04em;opacity:.9">{rich_v(X, b["sum"])}</div>'
    body += axis(X)
    s, t0, ext = page(X, b, cid, t, d, "D", "", body)
    axis_drift(X, s, t, d)
    kicker_in(X, s, t)
    tn = T(X, b, "at_num", t)                       # the numeral rolls on the cut
    roll(X, f"{s} .big", tn)
    X.tw(f'tl.from("{s} .pc", {{yPercent:60, opacity:0, duration:0.35, ease:"expo.out"}}, {tn + 0.2:.3f});')
    draw(X, f"{s} .bar .out", tn + 0.3, 0.6, "power3.out")
    X.tw(f'tl.from("{s} .half", {{scaleY:0, duration:0.4, ease:"power3.out"}}, {tn + 0.7:.3f});')
    X.tw(f'tl.from("{s} .halfl", {{yPercent:80, opacity:0, duration:0.4, ease:"expo.out"}}, {tn + 0.85:.3f});')
    tf = T(X, b, "at_fill", tn + 1.2)
    draw(X, f"{s} .bar .fill", tf, 0.9, "power3.inOut")
    X.sfx(tf, "draw")
    X.tw(f'tl.from("{s} .pl.on", {{yPercent:60, opacity:0, duration:0.45, ease:"expo.out"}}, {tf + 0.5:.3f});')
    X.tw(f'tl.from("{s} .bar .seg", {{scaleY:0, duration:0.3, ease:"power3.out", stagger:0.12}}, {tf + 0.9:.3f});')
    X.tw(f'tl.from("{s} .pl.in", {{yPercent:40, opacity:0, duration:0.4, ease:"expo.out", stagger:0.15}}, {tf + 1.05:.3f});')
    X.tw(f'tl.from("{s} .sum", {{yPercent:80, opacity:0, duration:0.45, ease:"expo.out"}}, {tf + 1.6:.3f});')
    X.tw(f'tl.from("{s} .axis i", {{scaleY:0, transformOrigin:"50% 0%", duration:0.5, ease:"power3.out", stagger:0.015}}, {t + 0.2:.3f});')


SCENES = {"cover": cover, "ranking": ranking, "figure": figure, "compare": compare, "statement": statement,
          "timeline": timeline, "share": share}


# ---------------------------------------------------------------- effects in this style (gallery cards / fx beats)
STYLE["fx_themes"] = {
    "paper": {"bg": PAPER, "fg": INK, "muted": GREY, "accent": VERM, "card": "#ffffff", "card-fg": INK, "line": "#d9d6cf"},
    "ink":   {"bg": INK, "fg": "#f4f1ea", "muted": LGREY, "accent": VERM, "card": "#1f1f1f", "card-fg": "#f4f1ea", "line": "#3a3a3a"},
    "red":   {"bg": VERM, "fg": PAPER, "muted": "rgba(251,250,247,.85)", "accent": INK, "card": PAPER, "card-fg": INK, "line": "rgba(251,250,247,.4)"},
    "lemon": {"bg": "#efebe3", "fg": INK, "muted": GREY, "accent": VERM, "card": PAPER, "card-fg": INK, "line": "#d0cbc0"},
}

FX_CSS = r"""
/* effects in this style: serif display type, square corners, hairline rules instead of filled cards */
.fx .big, .fx .op .op-t, .fx .nt-t, .fx .dn .dnc b { font-family:var(--f-display); font-weight:600; font-synthesis:none; letter-spacing:0; }
.fx .col > .sub { font-family:var(--f-label); font-weight:500; letter-spacing:.14em; text-transform:uppercase; border-top:1px solid currentColor; padding-top:1.2vmin; }
.fx [class*="card"], .fx .sc .sc-c, .fx .nt .nt-cv, .fx .wpm-lb, .fx .iu .iuper { border-radius:0 !important; box-shadow:none !important; }
.fx img { filter:""" + GRADE + """; }
/* the page around an effect (FX_FRAME): running head over a hairline, the line as a caption between hairlines, footnote */
.ctx.edx .hd { left:96px; right:96px; top:40px; height:auto; border:none; font-family:var(--f-label); font-size:24px; letter-spacing:.14em; text-transform:uppercase; }
.ctx.edx .hd b { font-weight:600; } .ctx.edx .hd span { opacity:.75; }
.ctx.edx .hd .fxid { background:none; color:var(--fg); font-family:var(--f-label); font-size:24px; padding:0; }
.ctx.edx .hl { position:absolute; left:96px; right:96px; top:80px; height:1px; background:var(--fg); transform-origin:0 50%; }
.ctx.edx .cap { bottom:70px; padding:0 15%; }
.ctx.edx .cap > span { display:block; background:none; color:var(--fg); border-radius:0; font-family:var(--f-cap); font-weight:500; padding:10px 24px;
  border-top:1px solid var(--fg); border-bottom:1px solid var(--fg); max-width:none; }
.ctx.edx .cap .em .emt { background:none; color:var(--accent); padding:0; }
.ctx.edx .ft { font-family:var(--f-label); font-size:22px; letter-spacing:.06em; opacity:.75; }
.ctx.edx.photo .cap > span { color:#fff; border-color:rgba(255,255,255,.6); background:linear-gradient(90deg, rgba(0,0,0,0), rgba(0,0,0,.4) 14%, rgba(0,0,0,.4) 86%, rgba(0,0,0,0)); }
.ctx.edx.photo .hl { background:#fff; }
#root.v .ctx.edx .hd { left:72px; right:72px; top:200px; } #root.v .ctx.edx .hl { left:72px; right:72px; top:242px; }
#root.v .ctx.edx .cap { top:1318px; bottom:auto; padding:0 120px 0 72px; } #root.v .ctx.edx .cap > span { font-size:42px; }
#root.v .ctx.edx .ft { left:72px; right:120px; top:1462px; bottom:auto; font-size:22px; }
"""
STYLE["css"] = CSS + FX_CSS


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect in editorial: a running head over a hairline that draws from the margin, the spoken
    line as a sans caption between two hairlines, the footnote and source as a small tracked line."""
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + f'<div class="hd"><div><b>{X.rich(X.channel)}</b> <span>{parts["topic"]}</span></div><div class="fxid">{parts["fxid"]}</div></div><i class="hl"></i>'
             + f'<div class="cap"><span style="font-size:{max(parts["cap_px"], 38)}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx edx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .hl", {{scaleX:0}}, {{scaleX:1, duration:0.6, ease:"power3.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .hd > div", {{yPercent:110, opacity:0, duration:0.45, ease:"expo.out", stagger:0.06}}, {t + 0.12:.3f});')
    X.tw(f'tl.from("{s} .cap > span", {{clipPath:"inset(0 50% 0 50%)", duration:0.45, ease:"power4.out"}}, {t + 0.1:.3f});')
