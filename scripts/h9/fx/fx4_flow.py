"""fx4 flow · three effects for "how my day / my run / my output looks" explainers: time_budget · run_clock · tilt_board.

time_budget   a day as a thick ring: "my share" is one true-angle accent slice with a leader to its label, the rest is
              segments that fill clockwise one by one (3 frames each, a tick each) while finished pieces stack up
run_clock     a real run told by a rolling digital wall clock and a growing track: every stage rolls the clock to its
              time, pops its node, draws the line from the last node and slides its thumbnail out; a bracket totals
              the elapsed time (computed, midnight-safe)
tilt_board    a 3D-tilted board of many small cards scrolling past, a big tabular counter beside it; every k-th step
              of the counter a new card drops on to the board with a squash

Each effect has two compositions: 16:9 uses the wide frame (ring left + tower right, a full-width horizontal track,
counter column left + board bleeding off the right edge); 9:16 stacks (ring top + a dealt fan of cards, a vertical
track with a following camera, title / counter on top of a board bleeding off the bottom right). 1:1 / 4:5 / 3:4 reuse
the 9:16 layout through the canvas window. Every motion is a pure function of timeline time; colours come only from the
style tokens (--bg --fg --muted --accent --card --card-fg --line and the --k-* skin variables).
"""
import importlib.util
import math
import pathlib
import re
import sys

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]
K = A.K
from h9 import fit as FT

CSS = r"""
.f4 { position:absolute; inset:0; }
.f4 .abs { position:absolute; left:0; top:0; }
.f4 svg.f4-svg { position:absolute; left:0; top:0; overflow:visible; }
.f4 .lbl { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--fg); white-space:nowrap; line-height:1.25; }
.f4 .mut { color:var(--muted); }
.f4 .acc { color:var(--mark); }
.f4 .num { font-family:var(--f-num, var(--f-display)); font-weight:900; font-variant-numeric:tabular-nums; line-height:1; white-space:nowrap; }
.f4 .card { position:absolute; box-sizing:border-box; background:var(--card); border-radius:min(var(--k-rs), 18px); overflow:hidden;
  box-shadow:var(--k-sh); border:var(--k-bw) solid color-mix(in srgb, var(--card-fg) 16%, transparent); }
.f4 .card img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; }

/* time_budget */
.f4 .tb-total { position:absolute; text-align:center; color:var(--fg); }
.f4 .tb-unit { position:absolute; text-align:center; font-family:var(--f-body); font-weight:800; color:var(--muted); white-space:nowrap; }
.f4 .tb-mine { position:absolute; white-space:nowrap; line-height:1.2; transform-origin:0% 50%; }
.f4 .tb-mine b { font-family:var(--f-display); font-weight:900; color:var(--mark); }
.f4 .tb-mine span { font-family:var(--f-body); font-weight:800; color:var(--fg); }
.f4 .tb-rest { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.3; }
.f4 .tb-rest .sw { display:inline-block; width:.62em; height:.62em; margin-right:.32em; vertical-align:.02em; background:var(--seg-on); border-radius:2px; }
.f4 .tb-count { position:absolute; font-family:var(--f-display); font-weight:900; white-space:nowrap; background:var(--mark); color:var(--on-mark);
  padding:.16em .5em; border-radius:min(var(--k-rs), 18px); line-height:1.2; }
.f4 .tb-piece .pl { position:absolute; left:50%; top:50%; width:0; height:0; border-style:solid; border-color:transparent transparent transparent var(--mark); }
.f4 .tb-piece .ln { position:absolute; left:10%; height:9%; border-radius:3px; background:color-mix(in srgb, var(--card-fg) 22%, transparent); }

/* run_clock */
.f4 .rc-clock { position:absolute; display:flex; align-items:flex-start; color:var(--fg); }
.f4 .rc-col { position:relative; overflow:hidden; }
.f4 .rc-strip { position:absolute; left:0; top:0; width:100%; }
.f4 .rc-strip i { display:block; font-style:normal; text-align:center; }
.f4 .rc-colon { text-align:center; }
.f4 .rc-day { position:absolute; font-family:var(--f-body); font-weight:900; color:var(--on-mark); background:var(--mark); border-radius:min(var(--k-rs), 18px); padding:.1em .4em; white-space:nowrap; }
.f4 .rc-note { position:absolute; font-family:var(--f-body); font-weight:700; color:var(--muted); line-height:1.35; }
.f4 .rc-cap { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--muted); letter-spacing:.08em; white-space:nowrap; }
.f4 .rc-cam { position:absolute; left:0; top:0; }
.f4 .rc-view { position:absolute; overflow:hidden; }
.f4 .rc-node { position:absolute; border-radius:50%; background:var(--bg); border:6px solid var(--mark); box-sizing:border-box; }
.f4 .rc-node.st { background:var(--fg); border-color:var(--fg); }
.f4 .rc-time { position:absolute; font-family:var(--f-mono, var(--f-body)); font-weight:800; color:var(--mark); white-space:nowrap; font-variant-numeric:tabular-nums; }
.f4 .rc-lab { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--fg); line-height:1.25; }
.f4 .rc-tcard { position:absolute; box-sizing:border-box; background:var(--card); color:var(--card-fg); border-radius:min(var(--k-rs), 18px); box-shadow:var(--k-sh);
  border:var(--k-bw) solid color-mix(in srgb, var(--card-fg) 16%, transparent); padding:14px 16px; overflow:hidden; }
.f4 .rc-tcard .ix { font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--mark-card); line-height:1; display:block; }
.f4 .rc-tcard .tx { font-family:var(--f-body); font-weight:800; line-height:1.25; display:block; }
.f4 .rc-plate { position:absolute; box-sizing:border-box; background:var(--card); color:var(--card-fg); border-radius:min(var(--k-rs), 18px); box-shadow:var(--k-sh); white-space:nowrap;
  border:var(--k-bw) solid color-mix(in srgb, var(--card-fg) 16%, transparent); }
.f4 .rc-plate b { font-family:var(--f-display); font-weight:900; color:var(--card-fg); }
.f4 .rc-plate span { font-family:var(--f-mono, var(--f-body)); font-weight:700; color:color-mix(in srgb, var(--card-fg) 62%, transparent); }

/* tilt_board */
.f4 .tlt-persp { position:absolute; }
.f4 .tlt-board { position:absolute; overflow:hidden; border-radius:min(calc(var(--k-r) * 1.5), 28px);
  background:color-mix(in srgb, var(--fg) 7%, var(--bg));
  background-image:radial-gradient(circle, color-mix(in srgb, var(--fg) 16%, transparent) 1.6px, transparent 2px);
  box-shadow:0 40px 90px rgba(0,0,0,.28); border:2px solid color-mix(in srgb, var(--fg) 14%, transparent); }
.f4 .tlt-row { position:absolute; left:0; }
.f4 .tlt-c { position:absolute; top:0; }
.f4 .tlt-c .card { left:0; top:0; width:100%; height:100%; }
.f4 .tlt-slot { position:absolute; top:0; box-sizing:border-box; border:2px dashed color-mix(in srgb, var(--fg) 13%, transparent); border-radius:min(var(--k-rs), 18px); }
.f4 .tlt-shadow { position:absolute; left:4%; top:8%; width:92%; height:92%; border-radius:min(var(--k-rs), 18px); background:rgba(0,0,0,.35); filter:blur(14px); opacity:0; }
.f4 .sk i { position:absolute; display:block; border-radius:3px; background:color-mix(in srgb, var(--card-fg) 20%, transparent); }
.f4 .sk i.a { background:var(--mark-card); }
.f4 .sk .q { position:absolute; color:var(--mark-card); overflow:visible; }
.f4 .tlt-index { position:absolute; font-family:var(--f-mono, var(--f-body)); font-weight:800; color:var(--mark); letter-spacing:.1em; white-space:nowrap; }
.f4 .tlt-title { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.25; }
.f4 .tlt-title .sl { display:block; white-space:nowrap; }
.f4 .tlt-val { position:absolute; color:var(--fg); }
.f4 .tlt-unit { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--mark); white-space:nowrap; line-height:1.1; }
.f4 .tlt-bar { position:absolute; height:8px; background:var(--mark); transform-origin:0 50%; }
"""

# digit glyph height ÷ font size for the numeral faces the styles use (Inter / Archivo / JetBrains Mono / Noto ≈ .72–.74)
DIGIT_H = 0.72
FRAME = 1.0 / 30


def _css(X):
    X.css("fx-f4-flow", CSS)


def _warn(msg):
    print(f"warning: {msg}", file=sys.stderr)


def _colors(X, p):
    """(palette, mark, on_mark, mark_card): the stressed colour on the page ground and on cards (accent when it reads
    ≥ 3:1 there, else the next token that does), and the text colour on the mark."""
    from h9.aefx import _contrast
    pal = A.pal(X, p)

    def pick(ground):
        for key in ("accent", "fg", "card-fg", "bg"):
            c = pal.get(key)
            if c and ground and _contrast(c, ground) >= 3.0:
                return c
        return pal.get("accent", "#e2321f")
    mark = pick(pal.get("bg"))
    mark_card = pick(pal.get("card"))
    on = K._on(mark)
    return pal, mark, on, mark_card


def _esc_attr(s):
    return str(s).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def _fit(text, w, max_px, min_px, lines=1, lh=1.2):
    """(px, [lines]) — the biggest size ≤ max_px that fits w (and `lines` lines); past min_px the last line is ellipsised."""
    f = FT.fit_text(A.strip(text), w, max_px * lh * lines + 1, max_px, min_px, lh=lh, max_lines=lines)
    return f.px, f.lines


def _num_w(txt):
    """width in em of a figure set in the heavy numeral faces (digits ≈ .66 em, separators ≈ .3 em)."""
    w = 0.0
    for ch in str(txt):
        if ch.isdigit():
            w += 0.66
        elif ch in ",.:":
            w += 0.3
        elif ch in "+-%":
            w += 0.62
        else:
            w += FT.width(ch)
    return w


def _lines_html(X, lines):
    out = ""
    for ln in lines:
        out += f'<span class="sl" style="display:block; white-space:nowrap">{X.rich(ln)}</span>'
    return out


# ------------------------------------------------------------------------------------------------ parsing
CN_DIG = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def _cn_int(s):
    """一 … 九十九 → int (None for anything else)."""
    if not s:
        return None
    if "十" in s:
        a, _, b = s.partition("十")
        ta = CN_DIG.get(a, None) if a else 1
        tb = CN_DIG.get(b, None) if b else 0
        if ta is None or tb is None:
            return None
        return ta * 10 + tb
    if len(s) == 1 and s in CN_DIG:
        return CN_DIG[s]
    return None


UNIT_MIN = [("天", 1440), ("日", 1440), ("days", 1440), ("day", 1440), ("d", 1440),
            ("个小时", 60), ("小时", 60), ("钟头", 60), ("hours", 60), ("hour", 60), ("hrs", 60), ("hr", 60), ("h", 60),
            ("分钟", 1), ("分", 1), ("minutes", 1), ("minute", 1), ("mins", 1), ("min", 1), ("m", 1),
            ("秒钟", 1 / 60), ("秒", 1 / 60), ("seconds", 1 / 60), ("second", 1 / 60), ("sec", 1 / 60)]
DUR_RX = re.compile(r"(\d+(?:\.\d+)?|[零〇一二两三四五六七八九十]+)\s*(" + "|".join(re.escape(u) for u, _ in UNIT_MIN) + r")(?![a-z])")


def _minutes(s):
    """a duration in minutes from "24 小时" · "30 分钟" · "1.5h" · "1 小时 30 分" · "半小时" · "两天" · "90min" · "38.4 秒"; None
    when no number + unit can be read."""
    if s is None:
        return None
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return None                       # a bare number has no unit: not a duration
    txt = str(s).strip().lower().replace("个半小时", ".5小时")
    if re.fullmatch(r"半(个)?小时", txt):
        return 30.0
    total = 0.0
    found = False
    for m in DUR_RX.finditer(txt):
        n = m.group(1)
        if n[0].isdigit():
            v = float(n)
        else:
            v = _cn_int(n)
            if v is None:
                continue
        mult = 1
        for u, mm in UNIT_MIN:
            if u == m.group(2):
                mult = mm
                break
        total += v * mult
        found = True
    if not found or total <= 0:
        return None
    return total


def _split_num(s):
    """"24 小时" → ("24", "小时"); "1,234 个" → ("1,234", "个"); "一整天" → ("", "一整天")."""
    m = re.match(r"\s*([-+]?\d[\d,]*(?:\.\d+)?)\s*(.*)$", str(s))
    if not m:
        return "", str(s).strip()
    return m.group(1), m.group(2).strip()


def _hm(s):
    """"23:29" · "1:05" · "23：29" · "23点29" · "23.29" → minutes after midnight; None otherwise."""
    if s is None:
        return None
    m = re.fullmatch(r"\s*(\d{1,2})\s*[:：点时.]\s*(\d{1,2})\s*分?\s*", str(s))
    if not m:
        return None
    h = int(m.group(1))
    mi = int(m.group(2))
    if h > 24 or mi > 59 or (h == 24 and mi > 0):
        return None
    return h * 60 + mi


def _hm_str(m):
    m = int(round(m)) % 1440
    return f"{m // 60:02d}:{m % 60:02d}"


def _span_label(minutes):
    """114 → "1 小时 54 分"; 45 → "45 分钟"; 120 → "2 小时"."""
    m = int(round(minutes))
    h = m // 60
    r = m % 60
    if h and r:
        return f"{h} 小时 {r} 分"
    if h:
        return f"{h} 小时"
    return f"{r} 分钟"


def _arc(cx, cy, r, a0, a1):
    """SVG path of a circular arc from angle a0 to a1 (degrees, 0 = 12 o'clock, clockwise)."""
    x0 = cx + r * math.sin(math.radians(a0))
    y0 = cy - r * math.cos(math.radians(a0))
    x1 = cx + r * math.sin(math.radians(a1))
    y1 = cy - r * math.cos(math.radians(a1))
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{x0:.2f} {y0:.2f} A{r:.2f} {r:.2f} 0 {large} 1 {x1:.2f} {y1:.2f}"


def _pt(cx, cy, r, a):
    return cx + r * math.sin(math.radians(a)), cy - r * math.cos(math.radians(a))


def _media_list(X, raw):
    """a list of pictures / clips → [project url of a still]."""
    if not raw:
        return []
    M = A.load("_media")
    its = M.items(X, {"media": raw})
    out = []
    for it in its:
        src = str(it["src"])
        if not it["video"] and src.lower().endswith((".gif", ".webp", ".apng", ".png")):
            # an animated picture would play by wall clock, not timeline time: use its first frame
            out.append(_first_frame(X, src))
            continue
        out.append(M.still(X, it))
    return out


def _first_frame(X, src):
    from PIL import Image
    a = FT._abs(X, src)
    with Image.open(a) as im:
        if getattr(im, "n_frames", 1) <= 1:
            return X.asset(src)
        M = A.load("_media")
        dst = X.out / "assets" / "img" / f"ff_{M._key(a)}.jpg"
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.seek(0)
            im.convert("RGB").save(dst, quality=88)
    return f"assets/img/{dst.name}"


# ------------------------------------------------------------------------------------------------ time_budget
def time_budget(X, cid, t, d, p):
    """一天的账 Time Budget: a thick ring is the whole day (`total`, big in the centre); `mine` is one thin accent slice at
    its TRUE angle from 12 o'clock, with a leader line out to its label; the rest of the ring is 24 − x segments that
    fill clockwise one by one (3 frames and a tick each, led by a clock hand), each dropping a finished piece on to a
    tower (16:9) or dealing one into a fan of cards (9:16); then `count` lands as a stamp."""
    F_ = "time_budget"
    P = X.portrait
    W, H = X.W, X.H
    G = A.frame(X, p)
    total = str(p.get("total") or "24 小时")
    mine = str(p.get("mine") or "30 分钟")
    mine_label = str(p.get("mine_label") or "我")
    rest_label = str(p.get("rest_label") if p.get("rest_label") is not None else "剩下的，全交给 AI")
    count = str(p.get("count") or "")
    thumbs = _media_list(X, p.get("thumbs") or p.get("media"))

    m_total = _minutes(total)
    m_mine = _minutes(mine)
    note = ""
    frac = None
    if m_total and m_mine and 0 < m_mine < m_total:
        frac = m_mine / m_total
    else:
        note = f"{F_}: could not read mine={mine!r} / total={total!r} as two durations (mine < total); no slice angle is drawn"
        _warn(f"{F_} at {t:.2f}s: {note}")

    # segments of the rest: 24 − (the slice in 24ths, rounded up)
    if frac is None:
        S = 24
        theta = 0.0
    else:
        S = 24 - int(math.ceil(24 * frac - 1e-9))
        if S < 1:
            S = 1
        theta = 360.0 * frac
    units_raw = p.get("units")
    if units_raw in (None, ""):
        units = min(len(thumbs), S) if thumbs else 0
    else:
        try:
            units = int(float(units_raw))
        except (TypeError, ValueError):
            raise SystemExit(f"{F_}: `units` must be a whole number 0–24, got {units_raw!r}")
        if units < 0:
            units = 0
        if units > S:
            _warn(f"{F_} at {t:.2f}s: units={units} but the rest of the ring has {S} segments; filling {S}")
            units = S
    tower = units > 0

    # ---- geometry
    if P:
        cx, cy, R, SW = 540.0, 650.0, 318.0, 46.0
    else:
        cx, cy, R, SW = 600.0, 500.0, 310.0, 46.0
    r_out = R + SW / 2
    r_in = R - SW / 2
    gap = 1.4                                   # degrees between segments
    rest_span = 360.0 - theta - (gap if frac is not None else 0)
    seg = rest_span / S
    a_rest0 = theta + (gap if frac is not None else 0)
    pal, mark, on_mark, mark_card = _colors(X, p)

    svg = []
    # the rest: S segments (track colour), each with a fill path on top that draws in its turn
    for k in range(S):
        a0 = a_rest0 + k * seg + gap / 2
        a1 = a_rest0 + (k + 1) * seg - gap / 2
        if frac is None:
            a0 = k * seg + gap / 2
            a1 = (k + 1) * seg - gap / 2
        path = _arc(cx, cy, R, a0, a1)
        svg.append(f'<path class="tb-seg s{k}" d="{path}" fill="none" stroke="var(--seg-off)" stroke-width="{SW:.0f}"/>')
        if k < units:
            ln = math.radians(a1 - a0) * R
            svg.append(f'<path class="tb-fill f{k}" d="{path}" fill="none" stroke="var(--seg-on)" stroke-width="{SW:.0f}" '
                       f'stroke-dasharray="{ln:.2f} {ln + 4:.2f}" stroke-dashoffset="{ln:.2f}"/>')
            # the tick: a short radial stroke just outside the ring at the segment's end
            tx0, ty0 = _pt(cx, cy, r_out + 6, a1)
            tx1, ty1 = _pt(cx, cy, r_out + 26, a1)
            svg.append(f'<line class="tb-tick k{k}" x1="{tx0:.1f}" y1="{ty0:.1f}" x2="{tx1:.1f}" y2="{ty1:.1f}" stroke="var(--fg)" stroke-width="4" stroke-linecap="round" opacity="0"/>')
    # mine: the true-angle slice, a little thicker than the ring so a thin slice still reads
    lead_html = ""
    mine_html = ""
    lpx = 52 if P else 48
    if frac is not None:
        sl = math.radians(theta) * R
        svg.append(f'<path class="tb-slice" d="{_arc(cx, cy, R, 0.0, max(theta, 0.05))}" fill="none" stroke="var(--mark)" stroke-width="{SW + 14:.0f}" '
                   f'stroke-dasharray="{sl:.2f} {sl + 6:.2f}" stroke-dashoffset="{sl:.2f}"/>')
        mid = min(theta / 2, 14.0)               # the leader leaves the slice near 12 o'clock, toward the label
        lx0, ly0 = _pt(cx, cy, r_out + 14, mid)
    # the label sits in the band above the ring, starting just right of 12 o'clock
    if P:
        # 9:16: right of the ring's top arc, under the page header row
        lab_y = cy - r_out - 12
        lab_x = cx + 150
        lab_w = W - 60 - lab_x
    else:
        # 16:9: right of the ring's top arc as well (the ring fills the height)
        lab_y = cy - r_out + 20
        lab_x = cx + 205
        lab_w = 1140 - lab_x
    mine_txt = f"{A.strip(mine_label)} · {A.strip(mine)}"
    mpx, mlines = _fit(mine_txt, lab_w, lpx, 44, 1)
    if P:
        lab_y = max(lab_y, 200 + mpx * 0.75)
    # split back into the label (accent) and the amount
    sep = mlines[0].find(" · ")
    if sep >= 0:
        inner_m = f'<b>{X.rich(mlines[0][:sep])}</b><span> · {X.rich(mlines[0][sep + 3:])}</span>'
    else:
        inner_m = f'<b>{X.rich(mlines[0])}</b>'
    mine_html = f'<div class="tb-mine" style="left:{lab_x:.0f}px; top:{lab_y - mpx * 0.6:.0f}px; font-size:{mpx}px">{inner_m}</div>'
    if frac is not None:
        ex = lab_x - 14
        ey = lab_y
        svg.append(f'<polyline class="tb-lead" points="{lx0:.1f},{ly0:.1f} {lx0 + (ex - lx0) * 0.35:.1f},{ey:.1f} {ex:.1f},{ey:.1f}" fill="none" stroke="var(--mark)" stroke-width="3"/>')
        svg.append(f'<circle class="tb-dot" cx="{lx0:.1f}" cy="{ly0:.1f}" r="7" fill="var(--mark)"/>')
    else:
        # no true angle: the two amounts as plain text, a dot instead of a leader
        svg.append(f'<circle class="tb-dot" cx="{lab_x - 22:.1f}" cy="{lab_y:.1f}" r="9" fill="var(--mark)"/>')
    # the hand: a short radial stroke across the ring band with a dot outside; turns about the centre
    hx0, hy0 = cx, cy - (r_in - 30)
    hx1, hy1 = cx, cy - (r_out + 9)
    svg.append(f'<g class="tb-hand"><line x1="{hx0:.1f}" y1="{hy0:.1f}" x2="{hx1:.1f}" y2="{hy1:.1f}" stroke="var(--fg)" stroke-width="5" stroke-linecap="round"/>'
               f'<circle cx="{hx1:.1f}" cy="{hy1:.1f}" r="8" fill="var(--fg)"/></g>')
    svg_html = f'<svg class="f4-svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(svg)}</svg>'

    # ---- centre: total (numerals ≥ 170 / 140 px glyph height when they fit the inner circle)
    num, unit = _split_num(total)
    inner_w = (r_in - 20) * 2 * 0.86
    centre = ""
    if num:
        want = (190 if P else 192) / DIGIT_H
        npx = want
        wem = _num_w(num)
        if npx * wem > inner_w:
            npx = inner_w / wem
        upx = 52 if P else 46
        upx2, ulines = _fit(unit, inner_w * 0.8, upx, 34 if P else 30, 1) if unit else (0, [])
        block = npx * 0.86 + (upx2 * 1.3 if unit else 0)
        y_num = cy - block / 2
        centre += f'<div class="tb-total num" style="left:{cx - inner_w / 2:.0f}px; width:{inner_w:.0f}px; top:{y_num - npx * 0.07:.0f}px; font-size:{npx:.0f}px">{X.rich(num)}</div>'
        if unit:
            centre += f'<div class="tb-unit" style="left:{cx - inner_w / 2:.0f}px; width:{inner_w:.0f}px; top:{y_num + npx * 0.9:.0f}px; font-size:{upx2}px">{X.rich(ulines[0])}</div>'
    else:
        tpx, tl_ = _fit(total, inner_w, 110 if P else 100, 36, 2, lh=1.25)
        hh = tpx * 1.25 * len(tl_)
        centre += (f'<div class="tb-total" style="left:{cx - inner_w / 2:.0f}px; width:{inner_w:.0f}px; top:{cy - hh / 2:.0f}px; font:900 {tpx}px/1.25 var(--f-display)">'
                   f'{_lines_html(X, tl_)}</div>')

    # ---- the pieces (tower in 16:9, a dealt fan in 9:16) and the rest label / count
    pieces = []
    rest_html = ""
    count_html = ""
    if tower:
        if not P:
            x0, x1 = 1160.0, 1780.0
            top_lim, bot = 128.0, G["y1"] - (112 if count else 16)
            cw = 290.0
            gx = x1 - x0 - 2 * cw
            rows = int(math.ceil(units / 2))
            ch = min(163.0, (bot - top_lim - (rows - 1) * 12) / rows)
            for k in range(units):
                r_ = k // 2
                c_ = k % 2
                px_ = x0 + c_ * (cw + gx)
                py_ = bot - (r_ + 1) * ch - r_ * 12
                pieces.append((px_, py_, cw, ch, 0.0))
            if count:
                cpx, cl = _fit(count, x1 - x0 - 40, 62, 60, 1)
                count_html = f'<div class="tb-count" style="left:{x0:.0f}px; top:{bot + 20:.0f}px; font-size:{cpx}px">{X.rich(cl[0])}</div>'
            if rest_label:
                rpx, rl = _fit(rest_label, 900, 50, 48, 1)
                rest_html = f'<div class="tb-rest" style="left:{cx - 450:.0f}px; width:900px; text-align:center; top:{cy + r_out + 20:.0f}px; font-size:{rpx}px"><i class="sw"></i>{X.rich(rl[0])}</div>'
        else:
            # 9:16: a fan of cards dealt left to right under the ring (y 1040–1320)
            # 9:16: a fan of 340×191 cards dealt left to right under the ring (x 60–1020, y 1010–1300); at most 7
            # places — later cards land on top of earlier ones in the same place, a few px down, as a stack
            # (the cards are tall and run off the bottom edge: the finished pieces are the picture under the caption)
            cw, ch = 440.0, 782.0
            xl, xr = 40.0, 1040.0
            fan_top = cy + r_out + 18 + 52 * 1.35 + (56 * 1.5 + 24 if count else 0) + 26
            n = units
            slots = min(n, 7)
            step = 0 if slots == 1 else min(cw + 16, (xr - xl - cw) / (slots - 1))
            span = cw + step * (slots - 1)
            sx = (xl + xr) / 2 - span / 2
            for k in range(n):
                j = k % slots
                layer = k // slots
                u = 0.0 if slots == 1 else j / (slots - 1) * 2 - 1
                rot = u * 9
                pieces.append((sx + j * step + layer * 5, fan_top + 26 * u * u + layer * 5, cw, ch, rot))
            if rest_label:
                rpx, rl = _fit(rest_label, 900, 52, 52, 1)
                rest_html = f'<div class="tb-rest" style="left:90px; width:900px; text-align:center; top:{cy + r_out + 18:.0f}px; font-size:{rpx}px"><i class="sw"></i>{X.rich(rl[0])}</div>'
            if count:
                # the count sits under the fan on its own plate, so the pictures stay visible
                cpx, cl = _fit(count, 800, 56, 40, 1)
                ctop = cy + r_out + 18 + 52 * 1.35 + 12                       # under the rest label, above the fan
                count_html = f'<div class="tb-count" style="left:540px; top:{ctop:.0f}px; font-size:{cpx}px; margin-left:{-FT.width(cl[0]) * cpx / 2 - cpx * 0.5:.0f}px">{X.rich(cl[0])}</div>'
    else:
        # nothing fills: the rest label becomes the statement of the free half of the frame
        if not P:
            bx, bw = 1160.0, 640.0
            rpx, rl = _fit(rest_label or " ", bw, 68, 48, 3, lh=1.3)
            hh = rpx * 1.3 * len(rl)
            ch_ = 0
            if count:
                ch_ = 62 * 1.6 + 30
            top = cy - (hh + ch_) / 2
            if rest_label:
                rest_html = f'<div class="tb-rest" style="left:{bx:.0f}px; width:{bw:.0f}px; top:{top:.0f}px; font-size:{rpx}px">{_lines_html(X, rl)}</div>'
            if count:
                cpx, cl = _fit(count, bw - 40, 62, 60, 1)
                count_html = f'<div class="tb-count" style="left:{bx:.0f}px; top:{top + hh + 30:.0f}px; font-size:{cpx}px">{X.rich(cl[0])}</div>'
        else:
            rpx, rl = _fit(rest_label or " ", 860, 68, 52, 2, lh=1.3)
            hh = rpx * 1.3 * len(rl) if rest_label else 0
            cpx, cl = _fit(count, 760, 58, 40, 1) if count else (0, [""])
            blk = hh + (cpx * 1.5 + 40 if count else 0)
            top = (cy + r_out + G["y1"]) / 2 - blk / 2
            if rest_label:
                rest_html = f'<div class="tb-rest" style="left:120px; width:840px; text-align:center; top:{top:.0f}px; font-size:{rpx}px">{_lines_html(X, rl)}</div>'
            if count:
                count_html = f'<div class="tb-count" style="left:540px; top:{top + hh + 40:.0f}px; font-size:{cpx}px; margin-left:{-FT.width(cl[0]) * cpx / 2 - cpx * 0.5:.0f}px">{X.rich(cl[0])}</div>'

    piece_html = ""
    for k in range(len(pieces)):
        px_, py_, pw_, ph_, rot = pieces[k]
        if thumbs:
            body = f'<img src="{thumbs[k % len(thumbs)]}" alt="">'
        else:
            tri = min(pw_, ph_) * 0.16
            body = (f'<i class="pl" style="border-width:{tri:.0f}px 0 {tri:.0f}px {tri * 1.6:.0f}px; margin:{-tri:.0f}px 0 0 {-tri * 0.6:.0f}px"></i>'
                    f'<i class="ln" style="top:76%; width:58%"></i><i class="ln" style="top:88%; width:34%"></i>')
        piece_html += (f'<div class="card tb-piece p{k}"{" data-layout-allow-overflow" if py_ + ph_ > H else ""} style="left:{px_:.0f}px; top:{py_:.0f}px; width:{pw_:.0f}px; height:{ph_:.0f}px; '
                       f'transform:rotate({rot:.1f}deg)">{body}</div>')

    seg_off = f"color-mix(in srgb, var(--fg) 13%, var(--bg))"
    seg_on = "var(--fg)"
    note_attr = f' data-note="{_esc_attr(note)}"' if note else ""
    inner = f'{svg_html}{centre}{mine_html}{piece_html}{rest_html}{count_html}'
    _css(X)
    body = (f'<div class="f2-body f4 tb"{note_attr} style="--mark:{mark}; --on-mark:{on_mark}; --mark-card:{mark_card}; '
            f'--seg-off:{seg_off}; --seg-on:{seg_on}">{inner}</div>')
    s, k_ = A.stage(X, cid, t, d, p, body)
    sv = f"{s} .tb"

    # ---- motion
    # build: the rest segments lay down clockwise (a sweep, 0.45 s), the centre total rises, the slice draws from 12
    # o'clock and its leader runs out to the label
    lay = t + 0.12
    X.tw(f'tl.fromTo("{sv} .tb-seg", {{opacity:0, scale:0.9, transformOrigin:"{cx:.0f}px {cy:.0f}px"}}, {{opacity:1, scale:1, duration:0.22, ease:"power3.out", stagger:{0.45 / S:.4f}, immediateRender:true}}, {lay:.3f});')
    X.tw(f'tl.fromTo("{sv} .tb-total, {sv} .tb-unit", {{y:40, opacity:0, scale:0.9}}, {{y:0, opacity:1, scale:1, duration:0.55, ease:"expo.out", stagger:0.08, immediateRender:true}}, {t + 0.2:.3f});')
    slice_at = t + 0.55
    if frac is not None:
        X.tw(f'tl.to("{sv} .tb-slice", {{strokeDashoffset:0, duration:0.35, ease:"power2.inOut"}}, {slice_at:.3f});')
        X.tw(f'tl.fromTo("{sv} .tb-dot", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.25, ease:"back.out(2)", immediateRender:true}}, {slice_at + 0.3:.3f});')
        X.tw(f'tl.fromTo("{sv} .tb-lead", {{strokeDasharray:"0 2000"}}, {{strokeDasharray:"2000 0", duration:0.4, ease:"power2.out", immediateRender:true}}, {slice_at + 0.35:.3f});')
    else:
        X.tw(f'tl.fromTo("{sv} .tb-dot", {{scale:0, transformOrigin:"50% 50%"}}, {{scale:1, duration:0.25, ease:"back.out(2)", immediateRender:true}}, {slice_at + 0.2:.3f});')
    X.tw(f'tl.fromTo("{sv} .tb-mine", {{clipPath:"inset(0 100% 0 0)", x:-20}}, {{clipPath:"inset(0 -4% 0 0)", x:0, duration:0.45, ease:"power3.out", immediateRender:true}}, {slice_at + 0.55:.3f});')
    X.sfx(slice_at, "pop", 0.4)
    # the rest label wipes in once the ring is down
    if rest_html:
        X.tw(f'tl.fromTo("{sv} .tb-rest", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -3% 0 0)", duration:0.5, ease:"power3.out", immediateRender:true}}, {t + 0.95:.3f});')

    # fill: segment k draws in 3 frames, its tick flashes, its piece lands; a clock hand leads the fill front
    fill0 = slice_at + 1.05
    per = 3 * FRAME
    fill_end = fill0 + units * per
    if fill_end > t + d - 1.0:
        fill0 = max(t + 0.9, t + d - 1.0 - units * per)
        fill_end = fill0 + units * per
    hand0 = theta if frac is not None else 0.0
    X.tw(f'tl.fromTo("{sv} .tb-hand", {{opacity:0}}, {{opacity:1, duration:0.2, immediateRender:true}}, {t + 0.5:.3f});')
    X.tw(f'tl.set("{sv} .tb-hand", {{rotation:{hand0:.2f}, svgOrigin:"{cx:.1f} {cy:.1f}"}}, {t:.3f});')
    slow = 30.0                                   # degrees per second while holding
    if units:
        a_end = a_rest0 + units * seg
        X.tw(f'tl.to("{sv} .tb-hand", {{rotation:{a_end:.2f}, svgOrigin:"{cx:.1f} {cy:.1f}", duration:{units * per:.3f}, ease:"none"}}, {fill0:.3f});')
        js = """(()=>{
  const S = "__S__";
  for (let k = 0; k < __N__; k++) {
    const at = __F0__ + k * __PER__;
    tl.to(S + " .tb-fill.f" + k, { strokeDashoffset: 0, duration: __PER__, ease: "none" }, at);
    tl.fromTo(S + " .tb-tick.k" + k, { opacity: 1 }, { opacity: 0, duration: 0.3, ease: "power2.in", immediateRender: false }, at + __PER__);
  }
})();"""
        X.tw(js.replace("__S__", sv).replace("__N__", str(units)).replace("__F0__", f"{fill0:.3f}").replace("__PER__", f"{per:.4f}"))
        for k in range(len(pieces)):
            land = fill0 + (k + 1) * per + 0.02
            sel = f"{sv} .tb-piece.p{k}"
            rot = pieces[k][4]
            if not P:
                # 16:9: the piece drops on to the tower (gravity, a 4-frame squash on contact)
                X.tw(f'tl.fromTo("{sel}", {{y:-260, opacity:0}}, {{y:0, opacity:1, duration:0.26, ease:"power2.in", immediateRender:true}}, {land - 0.26:.3f});')
                X.tw(f'tl.to("{sel}", {{keyframes:[{{scaleY:0.9, scaleX:1.04, duration:{2 * FRAME:.4f}}}, {{scaleY:1, scaleX:1, duration:{2 * FRAME:.4f}}}], transformOrigin:"50% 100%", ease:"none"}}, {land:.3f});')
            else:
                # 9:16: dealt out of the bottom of the ring, flying along an arc into its place in the fan
                px_, py_, pw_, ph_, rr = pieces[k]
                dx = cx - (px_ + pw_ / 2)
                dy = (cy + r_out - 40) - (py_ + ph_ / 2)
                X.tw(f'tl.fromTo("{sel}", {{x:{dx:.0f}, y:{dy:.0f}, scale:0.35, rotation:{-rr * 2:.1f}, opacity:0}}, '
                     f'{{x:0, y:0, scale:1, rotation:{rr:.1f}, opacity:1, duration:0.42, ease:"power3.out", immediateRender:true}}, {land - 0.12:.3f});')
        # one tick sound every few segments (not 24 clicks)
        for k in range(0, units, max(1, units // 6)):
            X.sfx(fill0 + k * per, "tick", 0.25)
    if count_html:
        land_c = (fill_end if units else t + 1.6) + 0.25
        X.tw(f'tl.fromTo("{sv} .tb-count", {{scale:1.5, rotation:-6, opacity:0}}, {{scale:1, rotation:{0 if P else -2}, opacity:1, duration:0.32, ease:"back.out(1.6)", immediateRender:true}}, {land_c:.3f});')
        X.sfx(land_c, "hit", 0.45)
    # hold: the hand keeps sweeping slowly round the ring; the slice label breathes 2 %
    hold0 = fill_end if units else t + 0.6
    a_hold = (a_rest0 + units * seg) if units else hand0
    rest_t = t + d - hold0
    if rest_t > 0.2:
        X.tw(f'tl.to("{sv} .tb-hand", {{rotation:{a_hold + slow * rest_t:.2f}, svgOrigin:"{cx:.1f} {cy:.1f}", duration:{rest_t:.3f}, ease:"none"}}, {hold0:.3f});')
    br0 = slice_at + 1.0
    if t + d - br0 > 1.0:
        n_br = max(1, int((t + d - br0) / 0.8))
        X.tw(f'tl.to("{sv} .tb-mine", {{scale:1.02, duration:0.8, ease:"sine.inOut", yoyo:true, repeat:{n_br - 1}}}, {br0:.3f});')
    A.hold_push(X, sv, max(hold0, t + 1.6), t + d, 1.025, origin=f"{cx:.0f}px {cy:.0f}px")


# ------------------------------------------------------------------------------------------------ run_clock
def _roll_strips(values, keep=20):
    """per column of an HH:MM display, the digit strip and the index each step shows. values = cumulative minutes
    (monotonic). Between two steps a column passes through every value it really takes (capped at the last `keep`
    changes, so a long gap spins fast instead of building a 2 m tall strip)."""
    def digits(m):
        s = _hm_str(m)
        return [s[0], s[1], s[3], s[4]]
    cols = [[], [], [], []]
    idx = [[], [], [], []]
    first = digits(values[0])
    for c in range(4):
        cols[c].append(first[c])
        idx[c].append(0)
    for i in range(1, len(values)):
        a = int(round(values[i - 1]))
        b = int(round(values[i]))
        for c in range(4):
            seq = []
            last = cols[c][-1]
            for m in range(a + 1, b + 1):
                dg = digits(m)[c]
                if dg != last:
                    seq.append(dg)
                    last = dg
            if len(seq) > keep:
                seq = seq[-keep:]
            cols[c].extend(seq)
            idx[c].append(len(cols[c]) - 1)
    return cols, idx


def run_clock(X, cid, t, d, p):
    """夜里跑完 Run Clock: a digital wall clock (tabular, digits roll per column) and a track. For every stage the clock
    rolls to its time, the node pops (0 → 1.15 → 1 in 6 frames), a line draws from the previous node and the stage's
    thumbnail slides out of the node; positions along the track are proportional to real time (midnight-safe). A
    bracket then totals the elapsed time, computed from start → end. 16:9: clock top right, a full-width horizontal
    track, bracket under it. 9:16: clock on top, a vertical track with one row per stage, a camera that follows the
    newest node, the total in a plate under the last row."""
    F_ = "run_clock"
    P = X.portrait
    W, H = X.W, X.H
    G = A.frame(X, p)
    raw = p.get("stages")
    if raw is None:
        raw = p.get("items")
    stages = A.texts(F_, {"stages": raw}, "stages", 1, 7, text_keys=("label", "text", "name", "title"))
    A.need(F_, t, p, [] if stages else ['stages (a list of {"label", "at"}, 2–7 of them)'])
    if not stages:
        stages = [{"text": "完成", "at": p.get("end") or "01:23"}]
    start_raw = p.get("start")
    end_raw = p.get("end")
    note = str(p.get("note") or "")
    pal, mark, on_mark, mark_card = _colors(X, p)

    # ---- times: parse, make monotonic across midnight, fill the unreadable ones evenly
    pts = []                                   # [(kind, label, raw at, minutes or None, media)]
    if start_raw not in (None, ""):
        pts.append(("start", "", str(start_raw), _hm(start_raw), None))
    for st in stages:
        at_raw = st.get("at") if st.get("at") is not None else st.get("time")
        pts.append(("stage", st["text"], "" if at_raw is None else str(at_raw), _hm(at_raw), st.get("media") or st.get("image") or st.get("src")))
    has_end = end_raw not in (None, "") and str(end_raw).strip() != str(pts[-1][2]).strip()
    if has_end:
        pts.append(("end", "", str(end_raw), _hm(end_raw), None))
    bad = [(q[1] or q[0]) + (f" {q[2]!r}" if q[2] else " (no time)") for q in pts if q[3] is None]
    if bad:
        _warn(f"{F_} at {t:.2f}s: no HH:MM time for {', '.join(bad)}; those stages are spaced evenly and the clock holds")
    absm = []
    prev = None
    for q in pts:
        m = q[3]
        if m is None:
            absm.append(None)
            continue
        m = float(m)
        if prev is not None:
            while m < prev:
                m += 1440
        absm.append(m)
        prev = m
    n = len(pts)
    known = [i for i in range(n) if absm[i] is not None]
    frac = [None] * n
    if len(known) >= 2 and absm[known[-1]] > absm[known[0]]:
        a0 = absm[known[0]]
        span = absm[known[-1]] - a0
        for i in known:
            frac[i] = (absm[i] - a0) / span
        # unknowns before the first / after the last known get evenly spaced room; between knowns: interpolated
        if known[0] > 0 or known[-1] < n - 1:
            lo = known[0]
            hi = n - 1 - known[-1]
            sc = 1.0 / (1 + (lo + hi) / max(1, n - 1))
            off = lo / max(1, n - 1) * sc
            for i in known:
                frac[i] = off + frac[i] * sc
            for i in range(lo):
                frac[i] = i / max(1, n - 1) * sc
            for j in range(hi):
                i = known[-1] + 1 + j
                frac[i] = frac[known[-1]] + (j + 1) / max(1, n - 1) * sc
        for i in range(n):
            if frac[i] is None:
                a = i - 1
                while frac[a] is None:
                    a -= 1
                b = i + 1
                while frac[b] is None:
                    b += 1
                frac[i] = frac[a] + (frac[b] - frac[a]) * (i - a) / (b - a)
    else:
        for i in range(n):
            frac[i] = i / max(1, n - 1)
    if n == 1:
        frac = [1.0]

    # elapsed: computed from start (else first stage) to end (else last stage)
    elapsed = None
    if absm[0] is not None and absm[-1] is not None and absm[-1] >= absm[0]:
        elapsed = absm[-1] - absm[0]
    total_label = str(p.get("total_label") or "")
    shown_total = ""
    if elapsed is not None:
        shown_total = _span_label(elapsed)
        if total_label:
            given = _minutes(total_label)
            if given is None or abs(given - elapsed) > 1.0:
                _warn(f"{F_} at {t:.2f}s: total_label {total_label!r} disagrees with the computed {shown_total!r} "
                      f"({_hm_str(absm[0])} → {_hm_str(absm[-1])}); showing the computed value")
            else:
                shown_total = total_label
    elif total_label:
        shown_total = total_label

    # clock values per step (hold the last readable time); midnight passed → "次日" tag
    clock_vals = []
    last = None
    for i in range(n):
        if absm[i] is not None:
            last = absm[i]
        clock_vals.append(last)
    first_known = None
    for v in clock_vals:
        if v is not None:
            first_known = v
            break
    if first_known is None:
        clock_vals = [0.0] * n
        no_clock = True
    else:
        no_clock = False
        for i in range(n):
            if clock_vals[i] is None:
                clock_vals[i] = first_known
    cols, idx = _roll_strips(clock_vals)
    day_step = None
    for i in range(n):
        if not no_clock and clock_vals[i] >= 1440 and day_step is None:
            day_step = i

    # ---- clock
    gh = 200 if P else 204                       # digit glyph height
    cpx = gh / DIGIT_H
    dw = cpx * 0.62
    colw = cpx * 0.34
    clock_w = dw * 4 + colw
    if P:
        if clock_w > 900:
            cpx *= 900 / clock_w
            dw = cpx * 0.62
            colw = cpx * 0.34
            clock_w = dw * 4 + colw
        clock_x = (W - clock_w) / 2
        clock_y = 300.0
    else:
        clock_x = 1780 - clock_w
        clock_y = 130.0
    lh = cpx * 0.92
    col_html = ""
    for c in range(4):
        if c == 2:
            col_html += f'<div class="rc-colon num" style="width:{colw:.0f}px; height:{lh:.0f}px; font-size:{cpx:.0f}px; line-height:{lh * 0.95:.0f}px">:</div>'
        digs = cols[c] if not no_clock else ["-"]
        items = "".join(f'<i style="height:{lh:.1f}px; line-height:{lh:.1f}px">{dg}</i>' for dg in digs)
        col_html += f'<div class="rc-col" data-layout-allow-overflow style="width:{dw:.0f}px; height:{lh:.0f}px"><div class="rc-strip num c{c}" data-layout-allow-overflow style="font-size:{cpx:.0f}px">{items}</div></div>'
    clock_html = f'<div class="rc-clock" style="left:{clock_x:.0f}px; top:{clock_y:.0f}px; height:{lh:.0f}px">{col_html}</div>'
    day_html = ""
    if day_step is not None:
        dpx = 34 if P else 30
        if P:
            day_html = f'<div class="rc-day" style="left:{clock_x + clock_w - 10:.0f}px; top:{clock_y - 52:.0f}px; font-size:{dpx}px; transform:translateX(-100%)">次日</div>'
        else:
            day_html = f'<div class="rc-day" style="left:{clock_x - 20:.0f}px; top:{clock_y + 6:.0f}px; font-size:{dpx}px; transform:translateX(-100%)">次日</div>'
    note_html = ""
    if note:
        if P:
            npx, nl = _fit(note, 900, 40, 34, 1)
            note_html = f'<div class="rc-note" style="left:90px; width:900px; text-align:center; top:{clock_y + lh + 14:.0f}px; font-size:{npx}px">{X.rich(nl[0])}</div>'
        else:
            nw = clock_x - 110 - (150 if day_step is not None else 60)
            npx, nl = _fit(note, nw, 48, 44, 2, lh=1.35)
            note_html = f'<div class="rc-note" style="left:110px; width:{nw:.0f}px; top:{clock_y + lh / 2 - npx * 1.35 * len(nl) / 2:.0f}px; font-size:{npx}px">{_lines_html(X, nl)}</div>'

    # ---- track
    medias = []
    for q in pts:
        u = _media_list(X, [q[4]]) if q[4] else []
        medias.append(u[0] if u else None)
    any_media = any(medias)
    nodes = []                                    # (x, y) in track-group coordinates
    track_html = ""
    cam = []                                      # 9:16: camera offset (px up) for each step
    plate_html = ""
    lab_html = ""
    card_html = ""
    node_r = 17 if P else 15
    final_off = 0.0
    if not P:
        # 16:9: a full-width track at y 720; thumbnails 320×180 above the nodes (shrunk by rule to 240, then the track
        # grows past the frame and the camera follows the newest node); time + label under the track; bracket + total
        n_st = sum(1 for q in pts if q[0] == "stage")
        gapw = 16.0
        cwid = min(320.0, (1660 - gapw * (n_st - 1)) / max(1, n_st))
        if cwid < 240:
            cwid = 240.0
        chei = cwid * 9 / 16 if any_media else 180.0
        tx0, ty = 140.0, 720.0
        tx1 = max(1780.0, tx0 + n_st * (cwid + gapw) + 20)
        for i in range(n):
            nodes.append((tx0 + (tx1 - tx0) * frac[i], ty))
        want = []
        for i in range(n):
            if pts[i][0] == "stage":
                want.append((i, nodes[i][0]))
        cx_list = _relax([w_[1] for w_ in want], cwid, gapw, tx0 - 30 + cwid / 2, tx1 + 30 - cwid / 2)
        card_y = 680.0 - chei
        k_stage = 0
        for j in range(len(want)):
            i = want[j][0]
            k_stage += 1
            ccx = cx_list[j]
            if medias[i]:
                card_html += (f'<div class="card rc-card r{i}" style="left:{ccx - cwid / 2:.0f}px; top:{card_y:.0f}px; width:{cwid:.0f}px; height:{chei:.0f}px">'
                              f'<img src="{medias[i]}" alt=""></div>')
            else:
                roomy = chei >= 170
                tpx, tl_ = _fit(pts[i][1], cwid - 36, 40 if roomy else 34, 30, 2 if roomy else 1, lh=1.25)
                card_html += (f'<div class="rc-tcard rc-card r{i}" style="left:{ccx - cwid / 2:.0f}px; top:{card_y:.0f}px; width:{cwid:.0f}px; height:{chei:.0f}px">'
                              f'<span class="ix" style="font-size:{44 if roomy else 36}px; margin-bottom:8px">{k_stage:02d}</span><span class="tx" style="font-size:{tpx}px">{_lines_html(X, tl_)}</span></div>')
            track_html += f'<svg class="f4-svg rc-stem r{i}" width="{tx1 + 200:.0f}" height="{H}"><line x1="{ccx:.1f}" y1="{card_y + chei:.1f}" x2="{nodes[i][0]:.1f}" y2="{ty - node_r:.1f}" stroke="var(--line)" stroke-width="3"/></svg>'
        # under the track: time (mono ≥ 30) and, under a picture card, the label (≥ 34); a block that would collide
        # moves above its own card
        TPX, LPX = 30, 36
        blocks = []
        for i in range(n):
            tt = pts[i][2] if pts[i][3] is None else _hm_str(pts[i][3])
            lab = pts[i][1] if (pts[i][0] == "stage" and medias[i]) else ""
            tw_ = FT.width(tt, mono=True) * TPX + 8
            lw_ = 0
            ll_ = []
            lpx_ = LPX
            if lab:
                lpx_, ll_ = _fit(lab, max(cwid, 280), LPX, 34, 1)
                lw_ = FT.width(ll_[0]) * lpx_ + 8
            blocks.append((i, tt, ll_, lpx_, max(tw_, lw_)))
        card_of = {}
        for j in range(len(want)):
            card_of[want[j][0]] = cx_list[j]
        lane_end = -1e9
        blk_h_full = TPX * 1.25 + LPX * 1.3 + 4
        for (i, tt, ll_, lpx_, bw_) in blocks:
            x = nodes[i][0]
            left = x - bw_ / 2
            if left < 110:
                left = 110
            if left + bw_ > tx1 + 30:
                left = tx1 + 30 - bw_
            if left < lane_end + 18 and i in card_of:
                cl = card_of[i] - cwid / 2
                if ll_:
                    lpx_, ll_ = _fit(pts[i][1], cwid, LPX, 34, 1)
                y = card_y - 10 - (blk_h_full if ll_ else TPX * 1.3)
                pos = f"left:{cl:.0f}px; top:{y:.0f}px; width:{cwid:.0f}px"
            else:
                if left < lane_end + 18:
                    left = lane_end + 18
                lane_end = left + bw_
                y = ty + node_r + 8
                pos = f"left:{left:.0f}px; top:{y:.0f}px; width:{bw_:.0f}px"
            inner_b = f'<div class="rc-time" style="left:0; top:0; font-size:{TPX}px">{X.rich(tt)}</div>'
            if ll_:
                inner_b += f'<div class="rc-lab" style="left:0; top:{TPX * 1.25 + 2:.0f}px; font-size:{lpx_}px; white-space:nowrap">{X.rich(ll_[0])}</div>'
            lab_html += f'<div class="abs rc-blk b{i}" style="{pos}; height:{blk_h_full if ll_ else TPX * 1.3:.0f}px">{inner_b}</div>'
        line_svg = f'<line class="rc-base" x1="{tx0:.1f}" y1="{ty:.1f}" x2="{tx1:.1f}" y2="{ty:.1f}" stroke="color-mix(in srgb, var(--fg) 14%, transparent)" stroke-width="7" stroke-linecap="round"/>'
        for i in range(1, n):
            line_svg += f'<line class="rc-seg g{i}" x1="{nodes[i - 1][0]:.1f}" y1="{ty:.1f}" x2="{nodes[i][0]:.1f}" y2="{ty:.1f}" stroke="var(--mark)" stroke-width="7" stroke-linecap="round"/>'
        by = 852.0
        bx0, bx1 = nodes[0][0], nodes[-1][0]
        if bx1 - bx0 < 40:
            bx1 = bx0 + 40
        line_svg += (f'<path class="rc-brk" d="M{bx0:.1f} {by - 18:.1f} L{bx0:.1f} {by:.1f} L{bx1:.1f} {by:.1f} L{bx1:.1f} {by - 18:.1f}" '
                     f'fill="none" stroke="var(--fg)" stroke-width="4" stroke-linejoin="round"/>')
        track_html = f'<svg class="f4-svg rc-lines" width="{tx1 + 200:.0f}" height="{H}">{line_svg}</svg>' + track_html
        for i in range(n):
            cls = "rc-node st" if pts[i][0] != "stage" else "rc-node"
            track_html += f'<div class="{cls} n{i}" style="left:{nodes[i][0] - node_r:.1f}px; top:{ty - node_r:.1f}px; width:{node_r * 2}px; height:{node_r * 2}px"></div>'
        # camera: follow the newest node / card when the track is longer than the frame
        right_of = {}
        for j in range(len(want)):
            right_of[want[j][0]] = cx_list[j] + cwid / 2
        max_off = max(0.0, tx1 + 40 - 1810)
        reach = 0.0
        for i in range(n):
            reach = max(reach, nodes[i][0] + 40, right_of.get(i, 0.0) + 20)
            off = min(max_off, max(0.0, reach - 1810))
            if cam and off < cam[-1]:
                off = cam[-1]
            cam.append(off)
        final_off = cam[-1] if cam else 0.0
        if shown_total:
            rng = ""
            if elapsed is not None:
                rng = f"{_hm_str(absm[0])} → {_hm_str(absm[-1])}"
            ppx = 58
            rpx_ = 30
            bw_ = FT.width(shown_total) * ppx + (FT.width(rng, mono=True) * rpx_ + 28 if rng else 0) + 60
            v0 = max(bx0 - final_off, 110)
            v1 = min(bx1 - final_off, 1810)
            mid = (v0 + v1) / 2
            left = min(max(110, mid - bw_ / 2), 1810 - bw_)
            plate_html = (f'<div class="rc-plate" style="left:{left:.0f}px; top:{by + 8:.0f}px; padding:2px 30px; font-size:{ppx}px; line-height:1.2">'
                          f'<b>{X.rich(shown_total)}</b>' + (f'<span style="font-size:{rpx_}px; margin-left:24px">{rng}</span>' if rng else "") + '</div>')
        group = f'<div class="rc-cam">{track_html}{card_html}{lab_html}</div>'
        if max_off > 0:
            # a track longer than the frame: what scrolls out fades at the frame edges instead of being cut
            fade = "linear-gradient(to right, transparent 0, #000 100px, #000 calc(100% - 70px), transparent 100%)"
            group = (f'<div class="rc-view" style="left:0; top:0; width:{W}px; height:{H}px; -webkit-mask-image:{fade}; mask-image:{fade}">{group}</div>')
        track_block = group + plate_html
    else:
        # 9:16: a vertical track at x 200 from y 660; one row per stage; the camera follows the newest node
        # 9:16: the rows are text (time + label) in a view that stops above the caption band; the stage pictures
        # land in a ribbon of tall cards along the bottom that runs off the bottom edge
        view_top = clock_y + lh + (70 if note else 24)
        view_bot = 1350.0
        tx, ty0 = 200.0, view_top + 40
        row_min = 150.0
        plate_room = 300 if (p.get("total_label") or len(known) >= 2) else 150
        L = view_bot - ty0 - plate_room
        ys = []
        for i in range(n):
            ys.append(ty0 + L * frac[i])
        for i in range(1, n):
            if ys[i] < ys[i - 1] + row_min:
                ys[i] = ys[i - 1] + row_min
        for i in range(n):
            nodes.append((tx, ys[i]))
        thw, thh = 420.0, 236.0
        line_svg = f'<line class="rc-base" x1="{tx:.1f}" y1="{ys[0]:.1f}" x2="{tx:.1f}" y2="{ys[-1]:.1f}" stroke="color-mix(in srgb, var(--fg) 14%, transparent)" stroke-width="7" stroke-linecap="round"/>'
        for i in range(1, n):
            line_svg += f'<line class="rc-seg g{i}" x1="{tx:.1f}" y1="{ys[i - 1]:.1f}" x2="{tx:.1f}" y2="{ys[i]:.1f}" stroke="var(--mark)" stroke-width="7" stroke-linecap="round"/>'
        bxx = tx - 60
        line_svg += (f'<path class="rc-brk" d="M{bxx + 22:.1f} {ys[0]:.1f} L{bxx:.1f} {ys[0]:.1f} L{bxx:.1f} {ys[-1]:.1f} L{bxx + 22:.1f} {ys[-1]:.1f}" '
                     f'fill="none" stroke="var(--fg)" stroke-width="5" stroke-linejoin="round"/>')
        track_html = f'<svg class="f4-svg rc-lines" width="{W}" height="{max(H, ys[-1] + 600):.0f}">{line_svg}</svg>'
        k_stage = 0
        for i in range(n):
            cls = "rc-node st" if pts[i][0] != "stage" else "rc-node"
            track_html += f'<div class="{cls} n{i}" style="left:{tx - node_r:.1f}px; top:{ys[i] - node_r:.1f}px; width:{node_r * 2}px; height:{node_r * 2}px"></div>'
            tt = pts[i][2] if pts[i][3] is None else _hm_str(pts[i][3])
            has_th = bool(medias[i])
            text_w = 960 - 250
            big = True
            tpx_ = 36
            inner_b = f'<div class="rc-time" style="left:0; top:0; font-size:{tpx_}px">{X.rich(tt or "—")}</div>'
            if pts[i][0] == "stage":
                k_stage += 1
                lpx_, ll_ = _fit(pts[i][1], text_w, 48 if big else 46, 44, 2 if not big else 1, lh=1.25)
                inner_b += f'<div class="rc-lab" style="left:0; top:{tpx_ + 10}px; width:{text_w:.0f}px; font-size:{lpx_}px">{_lines_html(X, ll_)}</div>'
            lab_html += f'<div class="abs rc-blk b{i}" style="left:250px; top:{ys[i] - 24:.0f}px; width:{text_w:.0f}px; height:{180 if pts[i][0] == "stage" else 50}px">{inner_b}</div>'
        plate_top = ys[-1] + 116
        if shown_total:
            rng = f"{_hm_str(absm[0])} → {_hm_str(absm[-1])}" if elapsed is not None else ""
            plate_html = (f'<div class="rc-plate" style="left:100px; width:880px; top:{plate_top:.0f}px; padding:8px 30px; font-size:66px; line-height:1.2; text-align:center">'
                          f'<b>{X.rich(shown_total)}</b>' + (f'<span style="display:block; font-size:34px; margin-top:4px">{rng}</span>' if rng else "") + '</div>')
            plate_bot = plate_top + 66 * 1.2 + (34 * 1.4 + 4 if rng else 0) + 16
        else:
            plate_bot = plate_top
        # camera: for each step, keep the newest row (and finally the plate) above the bottom of the view
        def snap(off):
            """the smallest offset ≥ off that puts a row exactly at the top of the view (no half-cut rows)."""
            if off <= 0:
                return 0.0
            for k in range(n):
                if off - 20 <= ys[k] - ty0 <= off + row_min + 2:     # up to 20 px may sit in the bottom fade
                    return ys[k] - ty0
            return off
        for i in range(n):
            row_bot = ys[i] + 100 + 12
            off = snap(max(0.0, row_bot - view_bot))
            if cam and off < cam[-1]:
                off = cam[-1]
            cam.append(off)
        final_off = max(cam[-1] if cam else 0.0, snap(plate_bot - view_bot))
        group = f'<div class="rc-cam">{track_html}{lab_html}{card_html}{plate_html}</div>'
        # the view clips the moving track under the clock; its top edge fades
        fade = "linear-gradient(to bottom, transparent 0, #000 36px, #000 calc(100% - 24px), transparent 100%)"
        track_block = (f'<div class="rc-view" style="left:0; top:{view_top:.0f}px; width:{W}px; height:{view_bot + 16 - view_top:.0f}px; '
                       f'-webkit-mask-image:{fade}; mask-image:{fade}">'
                       f'<div class="abs" style="top:{-view_top:.0f}px; width:{W}px; height:{H}px">{group}</div></div>')
        rib = [i for i in range(n) if medias[i]]
        if rib:
            m_ = len(rib)
            rgap = 16.0
            rw = min(440.0, (1000.0 - rgap * (m_ - 1)) / m_)
            rx0 = (W - (rw * m_ + rgap * (m_ - 1))) / 2
            rtop = 1528.0 if H >= 1900 else view_bot + 44.0      # under the caption band and the source line
            rh = H + 40.0 - rtop
            for q, i in enumerate(rib):
                track_block += (f'<div class="card rc-card r{i}" data-layout-allow-overflow style="left:{rx0 + q * (rw + rgap):.0f}px; top:{rtop:.0f}px; width:{rw:.0f}px; height:{rh:.0f}px">'
                                f'<img src="{medias[i]}" alt=""></div>')

    inner = clock_html + day_html + note_html + track_block
    _css(X)
    body = f'<div class="f2-body f4 rc" style="--mark:{mark}; --on-mark:{on_mark}; --mark-card:{mark_card}">{inner}</div>'
    s, k_ = A.stage(X, cid, t, d, p, body)
    sv = f"{s} .rc"

    # ---- motion
    items = [{"text": pts[i][1] if pts[i][0] == "stage" else "", "at": None} for i in range(n)]
    for i in range(n):
        if pts[i][0] == "stage":
            cue = stages[[j for j in range(n) if pts[j][0] == "stage"].index(i)].get("cue")
            items[i]["at"] = cue
    first = t + 0.35
    last_at = t + d - (1.5 if shown_total else 0.8)
    if last_at < first + 0.45 * (n - 1):
        last_at = first + 0.45 * (n - 1)
    times = A.cues(X, p, items, t, d, start=(first - t) / d, end=min(0.95, (last_at - t) / d), gap=0.45)
    if times:
        times[0] = min(times[0], first)
    X.tw(f'tl.fromTo("{sv} .rc-clock", {{y:-30, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"power3.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{sv} .rc-base", {{opacity:0}}, {{opacity:1, duration:0.3, immediateRender:true}}, {t + 0.1:.3f});')
    if note_html:
        X.tw(f'tl.fromTo("{sv} .rc-note", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -3% 0 0)", duration:0.5, ease:"power3.out", immediateRender:true}}, {t + 0.25:.3f});')
    # the strips start at their first value (a roll in from 00:00 for the opening)
    for c in range(4):
        X.tw(f'tl.set("{sv} .rc-strip.c{c}", {{y:0}}, {t:.3f});')
    for i in range(n):
        at = times[i]
        roll = 0.45
        # clock rolls to this stage's time (each column the short way forward)
        if i > 0 and not no_clock:
            for c in range(4):
                if idx[c][i] != idx[c][i - 1]:
                    X.tw(f'tl.to("{sv} .rc-strip.c{c}", {{y:{-idx[c][i] * lh:.1f}, duration:{roll:.2f}, ease:"power2.inOut"}}, {at - roll:.3f});')
        if day_step == i:
            X.tw(f'tl.fromTo("{sv} .rc-day", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.28, ease:"back.out(2)", immediateRender:true}}, {at:.3f});')
        # node pops 0 → 1.15 → 1 in 6 frames
        X.tw(f'tl.fromTo("{sv} .rc-node.n{i}", {{scale:0}}, {{keyframes:[{{scale:1.15, duration:{3 * FRAME:.4f}}}, {{scale:1, duration:{3 * FRAME:.4f}}}], ease:"none", immediateRender:true}}, {at:.3f});')
        if i > 0:
            # the line draws from the previous node, arriving as the node pops
            if not P:
                X.tw(f'tl.fromTo("{sv} .rc-seg.g{i}", {{attr:{{x2:{nodes[i - 1][0]:.1f}}}}}, {{attr:{{x2:{nodes[i][0]:.1f}}}, duration:0.32, ease:"power2.inOut", immediateRender:true}}, {at - 0.32:.3f});')
            else:
                X.tw(f'tl.fromTo("{sv} .rc-seg.g{i}", {{attr:{{y2:{nodes[i - 1][1]:.1f}}}}}, {{attr:{{y2:{nodes[i][1]:.1f}}}, duration:0.32, ease:"power2.inOut", immediateRender:true}}, {at - 0.32:.3f});')
        # the thumbnail / card slides out of the node
        nx, ny = nodes[i]
        if not P:
            X.tw(f'tl.fromTo("{sv} .rc-card.r{i}", {{y:{90:.0f}, scale:0.2, opacity:0, transformOrigin:"50% 100%"}}, {{y:0, scale:1, opacity:1, duration:0.42, ease:"power3.out", immediateRender:true}}, {at + 0.05:.3f});')
        else:
            X.tw(f'tl.fromTo("{sv} .rc-card.r{i}", {{y:240, rotation:-3, opacity:0}}, {{y:0, rotation:0, opacity:1, duration:0.45, ease:"power3.out", immediateRender:true}}, {at + 0.05:.3f});')
        X.tw(f'tl.fromTo("{sv} .rc-stem.r{i}, {sv} .rc-stem.b{i}", {{opacity:0}}, {{opacity:1, duration:0.2, immediateRender:true}}, {at + 0.1:.3f});')
        X.tw(f'tl.fromTo("{sv} .rc-blk.b{i}", {{clipPath:"inset(0 100% 0 0)", x:-16}}, {{clipPath:"inset(0 -4% 0 0)", x:0, duration:0.4, ease:"power3.out", immediateRender:true}}, {at + 0.08:.3f});')
        X.sfx(at, "tick" if i < n - 1 else "pop", 0.35)
        # camera: follows the newest node (9:16 down the column; 16:9 along a track longer than the frame)
        if i > 0 and cam[i] != cam[i - 1]:
            ax = "y" if P else "x"
            X.tw(f'tl.to("{sv} .rc-cam", {{{ax}:{-cam[i]:.1f}, duration:0.55, ease:"power2.inOut"}}, {at - 0.35:.3f});')
    end_t = times[-1] + 0.45
    if P and final_off > cam[-1]:
        X.tw(f'tl.to("{sv} .rc-cam", {{y:{-final_off:.1f}, duration:0.5, ease:"power2.inOut"}}, {end_t - 0.1:.3f});')
    if not P:
        X.tw(f'tl.fromTo("{sv} .rc-brk", {{strokeDasharray:"0 4000"}}, {{strokeDasharray:"4000 0", duration:0.5, ease:"power2.inOut", immediateRender:true}}, {end_t:.3f});')
    else:
        X.tw(f'tl.fromTo("{sv} .rc-brk", {{strokeDasharray:"0 4000"}}, {{strokeDasharray:"4000 0", duration:0.5, ease:"power2.inOut", immediateRender:true}}, {end_t:.3f});')
    if plate_html:
        X.tw(f'tl.fromTo("{sv} .rc-plate", {{y:30, scale:0.9, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.4, ease:"back.out(1.5)", immediateRender:true}}, {end_t + 0.35:.3f});')
        X.sfx(end_t + 0.35, "hit", 0.45)
    # hold: the newest node keeps a slow ring pulse going; a slow push keeps the frame alive
    A.hold_push(X, f"{sv}", end_t + 0.8, t + d, 1.025, origin=("50% 40%" if P else f"{nodes[-1][0] - final_off:.0f}px 720px"))


def _relax(xs, w, gap, lo, hi):
    """centres for boxes of width w wanted at xs (sorted), pushed apart to `gap` and kept inside [lo, hi]."""
    n = len(xs)
    out = list(xs)
    for i in range(n):
        if out[i] < lo:
            out[i] = lo
        if i > 0 and out[i] < out[i - 1] + w + gap:
            out[i] = out[i - 1] + w + gap
    if n and out[-1] > hi:
        out[-1] = hi
        for i in range(n - 2, -1, -1):
            if out[i] > out[i + 1] - w - gap:
                out[i] = out[i + 1] - w - gap
    return out


# ------------------------------------------------------------------------------------------------ tilt_board
SK_KINDS = ("chart", "text", "window", "quote", "number")


def _skeleton(kind, w, h, seed):
    """a style-coloured stand-in card of one of five kinds, drawn in % so it scales with the card."""
    if kind == "chart":
        out = ""
        hs = (0.38, 0.62, 0.48, 0.8, 0.56)
        for j in range(5):
            hh = hs[(j + seed) % 5]
            cls = ' class="a"' if j == 3 else ""
            out += f'<i{cls} style="left:{12 + j * 16}%; bottom:14%; width:11%; height:{hh * 62:.0f}%"></i>'
        return out + '<i style="left:10%; top:12%; width:44%; height:8%"></i>'
    if kind == "text":
        return ('<i class="a" style="left:10%; top:14%; width:52%; height:11%"></i>'
                '<i style="left:10%; top:36%; width:80%; height:7%"></i><i style="left:10%; top:50%; width:74%; height:7%"></i>'
                '<i style="left:10%; top:64%; width:80%; height:7%"></i><i style="left:10%; top:78%; width:46%; height:7%"></i>')
    if kind == "window":
        return ('<i style="left:0; top:0; width:100%; height:16%; border-radius:0"></i>'
                '<i class="a" style="left:5%; top:5%; width:5%; height:6%; border-radius:50%"></i>'
                '<i style="left:12%; top:5%; width:5%; height:6%; border-radius:50%"></i>'
                '<i style="left:8%; top:26%; width:38%; height:62%"></i>'
                '<i style="left:52%; top:26%; width:40%; height:9%"></i><i style="left:52%; top:42%; width:34%; height:9%"></i>'
                '<i style="left:52%; top:58%; width:40%; height:9%"></i>')
    if kind == "quote":
        return ('<svg class="q" viewBox="0 0 20 12" style="left:10%; top:12%; width:22%; height:24%" preserveAspectRatio="xMinYMin meet">'
                '<path d="M3 0h5L5 12H0zM13 0h5l-3 12h-5z" fill="currentColor"/></svg>'
                '<i style="left:12%; top:50%; width:76%; height:9%"></i><i style="left:12%; top:66%; width:60%; height:9%"></i>'
                '<i class="a" style="left:12%; top:83%; width:22%; height:5%"></i>')
    # number: a fat value bar, a small up mark and a caption line
    return ('<i style="left:10%; top:18%; width:46%; height:34%; border-radius:8px"></i>'
            '<i class="a" style="left:62%; top:24%; width:12%; height:22%; clip-path:polygon(50% 0, 100% 100%, 0 100%); border-radius:0"></i>'
            '<i style="left:10%; top:66%; width:70%; height:8%"></i><i style="left:10%; top:80%; width:40%; height:8%"></i>')


def tilt_board(X, cid, t, d, p):
    """组件墙 Tilt Board: a 3D-tilted board of many small cards that scroll along it continuously, a big tabular counter
    beside it (16:9: title + counter stacked left, the board bleeding off the right edge; 9:16: title and counter on
    top, the board bleeding off the bottom right). The counter climbs to `value` over the beat; every k-th step a new
    card drops on to the board with a 4-frame squash. A non-numeric `value` is shown as text and the board still runs."""
    F_ = "tilt_board"
    P = X.portrait
    W, H = X.W, X.H
    G = A.frame(X, p)
    raw_v = p.get("value")
    A.need(F_, t, p, [] if raw_v not in (None, "") else ['value (the number the counter reaches, e.g. 400)'])
    if raw_v in (None, ""):
        raw_v = 0
    unit = str(p.get("unit") if p.get("unit") is not None else "个组件")
    title = str(p.get("title") or "")
    index = str(p.get("index") or "")
    try:
        rows = int(p.get("rows") or 3)
    except (TypeError, ValueError):
        raise SystemExit(f"{F_}: `rows` must be a whole number 1–6")
    rows = max(1, min(6, rows))
    thumbs = _media_list(X, p.get("media") or p.get("items") or p.get("images"))
    pal, mark, on_mark, mark_card = _colors(X, p)

    # the value: a whole number counts; a number with a short tail ("400+", "2.6万") counts the number, keeps the tail
    vs = str(raw_v).strip()
    count_to = None
    tail = ""
    dec = 0
    m = re.fullmatch(r"([-+]?\d[\d,]*(?:\.\d+)?)\s*(\S{0,3})", vs)
    if m and not (isinstance(raw_v, bool)):
        num = m.group(1).replace(",", "")
        try:
            count_to = float(num)
            tail = m.group(2)
            dec = len(num.split(".")[1]) if "." in num else 0
        except ValueError:
            count_to = None
    if count_to is not None:
        final_txt = A.fmt(count_to, dec) + tail
    else:
        final_txt = vs

    # ---- left column / top block
    if not P:
        col_x, col_w = 110.0, 600.0
        want_gh = 174.0
    else:
        col_x, col_w = 90.0, 900.0
        want_gh = 176.0
    vpx = want_gh / DIGIT_H
    wem = FT.width(final_txt) if count_to is None else _num_w(final_txt)
    upx = 60 if P else 52
    inline_unit = P and unit and (wem * vpx + FT.width(unit) * upx + 24 <= col_w)
    if P and unit and not inline_unit:
        # shrink the counter so the unit still fits on its line (the board needs the room below)
        room = col_w - FT.width(unit) * upx - 24
        if room > col_w * 0.5 and wem * vpx > room:
            vpx = room / max(0.5, wem)
            inline_unit = True
    if wem * vpx > col_w:
        vpx = col_w / max(0.5, wem)
    if count_to is None:
        vpx_, vl = _fit(final_txt, col_w, min(vpx, 200 if P else 170), 40, 2, lh=1.1)
        vpx = vpx_
    else:
        vl = [final_txt]
    idx_html = ""
    title_html = ""
    val_html = ""
    unit_html = ""
    if not P:
        tpx, tl_ = (0, [])
        if title:
            tpx, tl_ = _fit(title, col_w, 64, 56, 2, lh=1.25)
        ipx = 28
        blk = (ipx * 1.6 if index else 0) + (tpx * 1.25 * len(tl_) + 30 if title else 0) + vpx * 1.0 * len(vl) + (upx * 1.3 + 24 if unit else 0)
        y = (G["y0"] + G["y1"]) / 2 - blk / 2
        if index:
            idx_html = f'<div class="tlt-index" style="left:{col_x:.0f}px; top:{y:.0f}px; font-size:{ipx}px">{X.rich(index)}</div>'
            y += ipx * 1.6
        if title:
            title_html = f'<div class="tlt-title" style="left:{col_x:.0f}px; width:{col_w:.0f}px; top:{y:.0f}px; font-size:{tpx}px">{_lines_html(X, tl_)}</div>'
            y += tpx * 1.25 * len(tl_) + 30
        val_y = y
        val_html = (f'<div class="tlt-val num" style="left:{col_x:.0f}px; top:{y - vpx * 0.08:.0f}px; font-size:{vpx:.0f}px; line-height:1">'
                    + "".join(f'<span class="sl" style="display:block">{X.rich(x)}</span>' for x in vl) + '</div>')
        y += vpx * 1.0 * len(vl)
        bar_y = y + 4
        if unit:
            upx2, ul = _fit(unit, col_w, upx, 30, 1)
            unit_html = f'<div class="tlt-unit" style="left:{col_x:.0f}px; top:{y + 24:.0f}px; font-size:{upx2}px">{X.rich(ul[0])}</div>'
        bar_html = f'<div class="tlt-bar" style="left:{col_x:.0f}px; top:{bar_y + 6:.0f}px; width:{min(col_w, 360):.0f}px"></div>'
    else:
        y = 296.0
        if title or index:
            tpx, tl_ = (0, [])
            ipx = 32
            iw = (FT.width(index, mono=True) * ipx + 26) if index else 0
            if title:
                tpx, tl_ = _fit(title, col_w - iw, 58, 34, 2, lh=1.3)
                if len(tl_) > 1:
                    tpx, tl_ = _fit(title, col_w - iw, 46, 34, 2, lh=1.3)
            if index:
                idx_html = f'<div class="tlt-index" style="left:{col_x:.0f}px; top:{y + max(0, (tpx * 1.3 - ipx * 1.3) / 2):.0f}px; font-size:{ipx}px">{X.rich(index)}</div>'
            if title:
                title_html = f'<div class="tlt-title" style="left:{col_x + iw:.0f}px; width:{col_w - iw:.0f}px; top:{y:.0f}px; font-size:{tpx}px">{_lines_html(X, tl_)}</div>'
        val_y = 424.0 if (title or index) else 330.0
        if (title or index) and title and len(tl_) > 1:
            val_y = 436.0
        if len(vl) > 1:
            val_y -= 60
        val_html = (f'<div class="tlt-val num" style="left:{col_x:.0f}px; top:{val_y - vpx * 0.08:.0f}px; font-size:{vpx:.0f}px; line-height:1">'
                    + "".join(f'<span class="sl" style="display:block">{X.rich(x)}</span>' for x in vl) + '</div>')
        if unit:
            if inline_unit:
                ux = col_x + wem * vpx + 22
                unit_html = f'<div class="tlt-unit" style="left:{ux:.0f}px; top:{val_y + vpx * 0.86 - upx * 1.05:.0f}px; font-size:{upx}px">{X.rich(unit)}</div>'
            else:
                upx2, ul = _fit(unit, col_w, 52, 48, 1)
                unit_html = f'<div class="tlt-unit" style="left:{col_x:.0f}px; top:{val_y + vpx * len(vl) + 4:.0f}px; font-size:{upx2}px">{X.rich(ul[0])}</div>'
        bar_html = ""

    # ---- the board: lanes of cards that run along it toward its far end. 16:9: the board turns about its right edge
    # (beyond the frame), its left end recedes; lanes are rows moving left. 9:16: it tilts back about its bottom edge
    # (below the frame), its top recedes; lanes are columns moving up into the distance.
    horiz = not P
    if horiz:
        bw, bh = 1540.0, 880.0
        bx, by = 2030.0 - bw, 104.0
        persp, po = 1150, "58% 50%"
        tr = "rotateY(-22deg) rotateX(8deg)"
        origin = "100% 50%"
    else:
        bw, bh = 1240.0, 1760.0
        bx, by = -20.0, 2024.0 - 1760.0
        persp, po = 1500, "50% 38%"
        tr = "rotateX(38deg) rotateZ(-8deg)"
        origin = "50% 100%"
    pad = 30.0
    gapc = 24.0
    if horiz:
        across = (bh - pad * 2 - gapc * (rows - 1)) / rows
        ch = across
        cw = ch * 1.25
        along_len = bw
        step = cw + gapc
    else:
        across = (bw - pad * 2 - gapc * (rows - 1)) / rows
        cw = across
        ch = cw / 1.25
        along_len = bh
        step = ch + gapc
    # drops: one card every k-th counter step, 4–12 of them over the counting window
    c0 = t + 0.45
    c1 = t + max(1.6, d * 0.72)
    if c1 > t + d - 0.6:
        c1 = max(c0 + 0.6, t + d - 0.6)
    n_drop = int((c1 - c0) / 0.3)
    n_drop = max(4, min(12, n_drop))
    drop_t = []
    for j in range(n_drop):
        drop_t.append(c0 + (c1 - c0) * (j + 1) / n_drop)
    speeds = []
    for r_ in range(rows):
        speeds.append(52.0 + 16.0 * ((r_ * 2) % 3))
    rows_html = ""
    drop_cards = []                              # (lane, slot, drop index)
    for r_ in range(rows):
        travel = speeds[r_] * d
        n_cards = int(math.ceil((along_len + travel) / step)) + 2
        # the slots that receive a dropped card: drops alternate over the lanes and land where the slot is seen at
        # that moment, spread over the near half of the board
        mine = [j for j in range(n_drop) if j % rows == r_]
        slot_for = {}
        used = set()
        for j in mine:
            tau = drop_t[j] - t
            u = 0.3 + 0.5 * (((j // rows) * 3) % 5) / 4
            target = along_len * (u if horiz else 0.35 + 0.5 * u)
            sidx = int(round((target + speeds[r_] * tau - pad) / step))
            while sidx in used:
                sidx += 1
            sidx = max(0, min(n_cards - 1, sidx))
            used.add(sidx)
            slot_for[j] = sidx
        dropped = {}
        for j, sidx in slot_for.items():
            dropped[sidx] = j
        cards = ""
        for c in range(n_cards):
            o = pad + c * step
            pos = f"left:{o:.0f}px; top:0" if horiz else f"left:0; top:{o:.0f}px"
            kind_i = (c * 7 + r_ * 3 + (c * c + r_) // 3) % 5
            if thumbs:
                body = f'<img src="{thumbs[(c * rows + r_) % len(thumbs)]}" alt="">'
                cls_card = "card"
            else:
                body = _skeleton(SK_KINDS[kind_i], cw, ch, c + r_)
                cls_card = "card sk"
            if c in dropped:
                j = dropped[c]
                cards += (f'<div class="tlt-slot" style="{pos}; width:{cw:.0f}px; height:{ch:.0f}px"></div>'
                          f'<div class="tlt-c dr d{j}" style="{pos}; width:{cw:.0f}px; height:{ch:.0f}px"><i class="tlt-shadow"></i><div class="{cls_card}">{body}</div></div>')
                drop_cards.append((r_, c, j))
            else:
                cards += f'<div class="tlt-c" style="{pos}; width:{cw:.0f}px; height:{ch:.0f}px"><div class="{cls_card}">{body}</div></div>'
        if horiz:
            lane_pos = f"left:0; top:{pad + r_ * (across + gapc):.0f}px; height:{ch:.0f}px; width:{n_cards * step + pad:.0f}px"
        else:
            lane_pos = f"top:0; left:{pad + r_ * (across + gapc):.0f}px; width:{cw:.0f}px; height:{n_cards * step + pad:.0f}px"
        rows_html += f'<div class="tlt-row r{r_}" style="{lane_pos}">{cards}</div>'
    board = (f'<div class="tlt-persp" style="left:0; top:0; width:{W}px; height:{H}px; perspective:{persp}px; perspective-origin:{po}">'
             f'<div class="tlt-board" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px; transform:{tr}; transform-origin:{origin}">{rows_html}</div></div>')

    veil = ""
    if P:
        # 9:16: the board fades into the page ground before the caption band, so the caption reads on a calm ground
        veil = ('<div class="tlt-veil" style="position:absolute; left:0; right:0; top:1236px; bottom:0; '
                'background:linear-gradient(to bottom, color-mix(in srgb, var(--bg) 0%, transparent) 0, '
                'color-mix(in srgb, var(--bg) 94%, transparent) 104px, color-mix(in srgb, var(--bg) 94%, transparent) 100%)"></div>')
    inner = board + veil + idx_html + title_html + val_html + unit_html + bar_html
    _css(X)
    body = f'<div class="f2-body f4 tlt" style="--mark:{mark}; --on-mark:{on_mark}; --mark-card:{mark_card}">{inner}</div>'
    s, k_ = A.stage(X, cid, t, d, p, body)
    sv = f"{s} .tlt"

    # ---- motion
    X.tw(f'tl.fromTo("{sv} .tlt-persp", {{x:{300 if horiz else 160}, y:{0 if horiz else 340}, opacity:0}}, {{x:0, y:0, opacity:1, duration:0.75, ease:"expo.out", immediateRender:true}}, {t + 0.05:.3f});')
    for r_ in range(rows):
        ax = "x" if horiz else "y"
        X.tw(f'tl.fromTo("{sv} .tlt-row.r{r_}", {{{ax}:0}}, {{{ax}:{-speeds[r_] * d:.1f}, duration:{d:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')
    if idx_html:
        X.tw(f'tl.fromTo("{sv} .tlt-index", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -4% 0 0)", duration:0.4, ease:"power3.out", immediateRender:true}}, {t + 0.1:.3f});')
    if title_html:
        X.tw(f'tl.fromTo("{sv} .tlt-title .sl", {{clipPath:"inset(0 100% 0 0)", x:-24}}, {{clipPath:"inset(0 -3% 0 0)", x:0, duration:0.5, ease:"power3.out", stagger:0.08, immediateRender:true}}, {t + 0.15:.3f});')
    X.tw(f'tl.fromTo("{sv} .tlt-val", {{y:50, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"expo.out", immediateRender:true}}, {t + 0.25:.3f});')
    if unit_html:
        X.tw(f'tl.fromTo("{sv} .tlt-unit", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -4% 0 0)", duration:0.4, ease:"power3.out", immediateRender:true}}, {t + 0.45:.3f});')
    if bar_html:
        X.tw(f'tl.fromTo("{sv} .tlt-bar", {{scaleX:0}}, {{scaleX:1, duration:{c1 - c0:.3f}, ease:"none", immediateRender:true}}, {c0:.3f});')
    if count_to is not None and count_to != 0:
        js = """(()=>{
  const el = document.querySelector("__S__ .tlt-val .sl");
  if (!el) return;
  const o = { v: 0 };
  const fmt = (v) => v.toLocaleString("en-US", { minimumFractionDigits: __DEC__, maximumFractionDigits: __DEC__ }) + __TAIL__;
  tl.fromTo(o, { v: 0 }, { v: __TO__, duration: __DUR__, ease: "none", immediateRender: false,
    onUpdate: () => { const k = Math.pow(10, __DEC__); el.textContent = fmt(Math.floor(o.v * k + 1e-6) / k); } }, __C0__);
  tl.set(el, { textContent: fmt(__TO__) }, __C1__);
})();"""
        X.tw(js.replace("__S__", sv).replace("__DEC__", str(dec)).replace("__TAIL__", A.js(tail)).replace("__TO__", repr(count_to))
               .replace("__DUR__", f"{c1 - c0:.3f}").replace("__C0__", f"{c0:.3f}").replace("__C1__", f"{c1:.3f}"))
    # the drops: each card falls on to its slot (a 2D fall in the board's plane: big and lifted → down, its shadow
    # tightening), lands with a 4-frame squash
    for (r_, c, j) in drop_cards:
        land = drop_t[j]
        sel = f"{sv} .tlt-c.d{j}"
        X.tw(f'tl.fromTo("{sel}", {{scale:1.7, y:-140, x:30, opacity:0}}, {{scale:1, y:0, x:0, opacity:1, duration:0.28, ease:"power2.in", immediateRender:true}}, {land - 0.28:.3f});')
        X.tw(f'tl.fromTo("{sel} .tlt-shadow", {{opacity:0, scale:1.4}}, {{opacity:0.9, scale:1, duration:0.28, ease:"power2.in", immediateRender:true}}, {land - 0.28:.3f});')
        X.tw(f'tl.to("{sel} .tlt-shadow", {{opacity:0, duration:0.3}}, {land + 0.05:.3f});')
        X.tw(f'tl.to("{sel}", {{keyframes:[{{scaleY:0.9, scaleX:1.05, duration:{2 * FRAME:.4f}}}, {{scaleY:1, scaleX:1, duration:{2 * FRAME:.4f}}}], ease:"none"}}, {land:.3f});')
    for j in range(0, n_drop, 2):
        X.sfx(drop_t[j], "tick", 0.3)
    X.sfx(c1, "hit", 0.4)
    A.hold_push(X, f"{sv} .tlt-val", c1 + 0.2, t + d, 1.03, origin="0% 50%")


FX = {"time_budget": time_budget, "run_clock": run_clock, "tilt_board": tilt_board}
