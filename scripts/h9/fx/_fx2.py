"""shared pieces for the second effects family (physics · camera · type as image · data that tells · organic · match
cut). Not an effect (files starting with _ are skipped by the loader).

need()      missing content is a build error (the effect never draws an empty skeleton); skeleton: true opts in
texts()     a list parameter given as strings or dicts → validated list of dicts with a "text"
number()    a numeric parameter, checked and clamped        choice()   one of a fixed set, else a build error
head()      the fitted title (+ note) of a beat → (html, height)
cues()      one moment per item: its own `at`, else when the narration says it (U.follow), else evenly spread
fall()      a body with weight: gravity drop that lands on a given frame, squash and settle
shake()     a decaying jolt (the frame or a part takes the impact)
count()     a number that counts on screen (deterministic, seek-safe)
All sizes are px in the layout frame (X.W × X.H); colours and shapes come from the style through _kinfo.skin().
"""
import importlib.util
import math
import pathlib
import sys
from h9 import fit as FT


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


K = load("_kinfo")
SS = load("side_stat")

CSS = r"""
.ki .f2-title { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.18; color:var(--fg); }
.ki .f2-title .sl { display:block; white-space:nowrap; }
.ki .f2-note { position:absolute; font:600 24px var(--f-body); color:var(--muted); white-space:nowrap; }
#root.v .ki .f2-note { font-size:30px; }
.ki .f2-ground { position:absolute; left:0; right:0; bottom:0; background:color-mix(in srgb, var(--fg) 12%, var(--bg)); border-top:4px solid var(--fg); }
.ki .f2-num { font-family:var(--f-num, var(--f-display)); font-weight:900; letter-spacing:-.03em; line-height:1; white-space:nowrap; }
.ki .f2-abs { position:absolute; left:0; top:0; }
.ki .f2-body { position:absolute; inset:0; }
"""


def base(X):
    X.css("fx-f2", CSS)


def need(fx, t, p, missing):
    """missing = [text, ...] of what the beat lacks. Returns True when the beat asked for a deliberate skeleton."""
    if not missing:
        return False
    if p.get("skeleton") is True:
        return True
    raise SystemExit(f"{fx} at {t:.2f}s is missing content, it would render an empty skeleton: " + "; ".join(missing)
                     + " — or pass skeleton: true on purpose")


def texts(fx, p, key, lo, hi, text_keys=("text", "label", "name", "title")):
    """p[key] as a list of dicts, each with a non-empty "text". Strings become {"text": s}. More than `hi` items is
    an error (say so, rather than silently dropping content); fewer than `lo` returns what there is (need() reports)."""
    raw = p.get(key)
    if raw is None:
        return []
    if isinstance(raw, str):
        raw = [s for s in raw.split("|") if s.strip()]
    if not isinstance(raw, (list, tuple)):
        raise SystemExit(f"{fx}: `{key}` must be a list")
    out = []
    for it in raw:
        if isinstance(it, dict):
            row = dict(it)
            txt = ""
            for tk in text_keys:
                if str(row.get(tk) or "").strip():
                    txt = str(row[tk]).strip()
                    break
            row["text"] = txt
        elif isinstance(it, (list, tuple)) and len(it) >= 1:
            row = {"text": str(it[0]).strip()}
            if len(it) >= 2:
                row["value"] = it[1]
        else:
            row = {"text": str(it).strip()}
        if row["text"]:
            out.append(row)
    if len(out) > hi:
        raise SystemExit(f"{fx}: `{key}` takes at most {hi} items, got {len(out)} — split the beat in two")
    return out


def number(fx, p, key, dflt=None, lo=None, hi=None):
    """p[key] as a float ("46,479" and "40.9%" are read too). None when absent and no default."""
    v = p.get(key)
    if v is None or v == "":
        return dflt
    if isinstance(v, bool):
        raise SystemExit(f"{fx}: `{key}` must be a number")
    if isinstance(v, str):
        s = v.replace(",", "").replace("%", "").strip()
        try:
            v = float(s)
        except ValueError:
            raise SystemExit(f"{fx}: `{key}` must be a number, got {p.get(key)!r}")
    if not isinstance(v, (int, float)) or v != v:
        raise SystemExit(f"{fx}: `{key}` must be a number")
    v = float(v)
    if lo is not None and v < lo:
        v = float(lo)
    if hi is not None and v > hi:
        v = float(hi)
    return v


def choice(fx, p, key, options, dflt):
    v = p.get(key)
    if v is None or v == "":
        return dflt
    if v not in options:
        raise SystemExit(f"{fx}: `{key}` must be one of {', '.join(str(o) for o in options)}; got {v!r}")
    return v


def fmt(v, dec=None):
    """46479 → "46,479"; 40.9 → "40.9"."""
    if dec is None:
        dec = 0
        if abs(v - round(v)) > 1e-9:
            dec = 1
            if abs(v * 10 - round(v * 10)) > 1e-9:
                dec = 2
    return f"{v:,.{dec}f}"


def decimals(v):
    s = str(v)
    if "." in s:
        return len(s.replace("%", "").split(".")[1])
    return 0


def head(X, p, x0, y0, w, align="left", max_px=None):
    """the beat's title (+ small note under it) at the top of a box → (html, height used, including a gap below)."""
    title = p.get("title")
    note = p.get("note")
    P = X.portrait
    html = ""
    y = y0
    if title:
        mx = max_px or (72 if P else 54)
        f = FT.fit_text(str(title), w, mx * 2.5, mx, 30, lh=1.18, max_lines=2)
        ls = ""
        for ln in f.lines:
            ls += f'<span class="sl">{K.hl_html(X, ln)}</span>'
        html += f'<div class="f2-title" style="left:{x0:.0f}px; top:{y:.0f}px; width:{w:.0f}px; font-size:{f.px:.0f}px; text-align:{align}">{ls}</div>'
        y += f.px * 1.18 * len(f.lines) + 10
    if note:
        npx = 30 if P else 24
        nf = FT.fit_text(str(note), w, npx * 1.4, npx, npx, max_lines=1)
        pos = f"left:{x0:.0f}px; width:{w:.0f}px; text-align:{align}"
        html += f'<div class="f2-note" style="{pos}; top:{y:.0f}px">{X.rich(nf.lines[0])}</div>'
        y += npx * 1.5
    if y > y0:
        y += 18 if P else 12
    return html, y - y0


def head_in(X, s_, t, k):
    """the title wipes in from its left edge, then its stressed word gets the style's highlight."""
    X.tw(f'tl.fromTo("{s_} .f2-title .sl", {{clipPath:"inset(0 100% 0 0)", x:-24}}, {{clipPath:"inset(0 -3% 0 0)", x:0, duration:0.5, ease:"power3.out", stagger:0.08, immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s_} .f2-note", {{opacity:0}}, {{opacity:1, duration:0.4, immediateRender:true}}, {t + 0.3:.3f});')
    K.hl_tween(X, f"{s_} .f2-title", t + 0.6, k)


def cues(X, p, items, t, d, start=0.3, end=0.8, gap=0.3):
    """one absolute time per item: item["at"] ("@词" or seconds into the beat) first, else the moment the narration
    says item["text"] inside the beat, else spread over [start, end] of the beat. Monotonic, `gap` apart."""
    n = len(items)
    if n == 0:
        return []
    a = t + d * start
    if n == 1:
        a = t + min(0.6, d * start)
    auto = K.U.spread(n, a, t + d * end)
    out = []
    fixed = []
    say = []
    for i in range(n):
        v = items[i].get("at")
        out.append(K.U.when(X, v, t, auto[i]))
        fixed.append(v is not None)
        say.append(K.strip(items[i].get("text", "")))
    out = K.U.follow(X, say, t, d, out, fixed, gap=gap)
    for i in range(1, n):
        if out[i] < out[i - 1] + gap:
            out[i] = out[i - 1] + gap
    last = t + d - 0.35
    for i in range(n):
        if out[i] > last:
            out[i] = last
    return out


def fall_time(height):
    """seconds a body takes to fall `height` px under the house gravity (≈ 5200 px/s²), kept in a readable range."""
    s = math.sqrt(max(1.0, height) / 2600.0)
    if s < 0.24:
        s = 0.24
    if s > 0.62:
        s = 0.62
    return s


def fall(X, sel, land, height, squash=0.12, origin="50% 100%", settle=True):
    """`sel` drops `height` px and touches down at `land`: accelerating (gravity), squashing on contact and springing
    back. Returns the moment it starts to fall."""
    dur = fall_time(height)
    X.tw(f'tl.fromTo("{sel}", {{y:{-height:.0f}}}, {{y:0, duration:{dur:.3f}, ease:"power2.in", immediateRender:true}}, {land - dur:.3f});')
    if settle and squash > 0:
        X.tw(f'tl.to("{sel}", {{scaleY:{1 - squash:.3f}, scaleX:{1 + squash * 0.5:.3f}, transformOrigin:"{origin}", duration:0.07, ease:"power2.out"}}, {land:.3f});')
        X.tw(f'tl.to("{sel}", {{scaleY:1, scaleX:1, duration:0.42, ease:"elastic.out(1.1, 0.45)"}}, {land + 0.07:.3f});')
    return land - dur


def shake(X, sel, at, amp=14, n=6, seed=0):
    """a decaying jolt on `sel` (vertical first: the floor took a weight)."""
    step = 0.04
    for j in range(n):
        a = amp * (0.62 ** j)
        sign = 1 if j % 2 == 0 else -1
        dx = a * 0.35 * (1 if (j + seed) % 3 == 0 else -1)
        X.tw(f'tl.to("{sel}", {{y:{sign * a:.1f}, x:{dx:.1f}, duration:{step}, ease:"none"}}, {at + j * step:.3f});')
    X.tw(f'tl.to("{sel}", {{y:0, x:0, duration:0.08, ease:"power2.out"}}, {at + n * step:.3f});')


def count(X, sel, a, b, at, dur, dec=0, comma=True, ease="power2.out"):
    """the text of `sel` counts from a to b (dec decimals), a pure function of timeline time."""
    if comma:
        js = f"o.v.toLocaleString('en-US', {{minimumFractionDigits:{dec}, maximumFractionDigits:{dec}}})"
    else:
        js = f"o.v.toFixed({dec})"
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); if(!el) return; tl.fromTo(o, {{v:{a}}}, {{v:{b}, duration:{dur:.2f}, ease:"{ease}", immediateRender:false, '
         f'onUpdate:()=>{{el.textContent={js};}}}}, {at:.3f});}})();')


def fit_px(text, w, h, max_px, min_px=20, max_lines=2, lh=1.15):
    f = FT.fit_text(str(text), w, h, max_px, min_px, lh=lh, max_lines=max_lines)
    return f.px, f.lines


def lines_html(X, lines):
    out = ""
    for ln in lines:
        out += f'<span class="sl" style="display:block; white-space:nowrap">{K.hl_html(X, ln)}</span>'
    return out


# ---------------------------------------------------------------- frame + stage for the fx2 family
def frame(X, p):
    """the layout of a beat → dict. Text lives in [x0, x1] × [y0, y1] (under the header, above the caption band);
    pictures may run on to the bottom edge (`floor`, a little above it) — in 9:16 that is the 600 px under the
    caption that the shared skeleton used to leave dead."""
    x0, y0, x1, y1 = K.area(X, p)
    P = X.portrait
    return {"P": P, "W": X.W, "H": X.H, "x0": x0, "y0": y0, "x1": x1, "y1": y1, "w": x1 - x0, "h": y1 - y0,
            "floor": X.H - (56 if P else 34), "cx": X.W / 2}


def stage(X, cid, t, d, p, inner, cls=""):
    """theme page + spoken-line context (the style's own frame) under an untimed stage holding `inner`
    → (selector, skin). Colours inside come only from the style tokens (--bg --fg --muted --line --card --card-fg
    --accent and the --k-* skin variables)."""
    base(X)
    k = K.skin(X)
    # layered type is the point of these effects (extrusion slices, glyph mosaics, chips under the caption): the layout
    # checker's text-overlap rule is waived inside the scene, not for the page around it
    inner = f'<div class="f2-wrap" data-layout-allow-overlap style="position:absolute; inset:0">{inner}</div>'
    beats = X.v.get("beats") or []
    chaptered = any(isinstance(b, dict) and b.get("chapter") for b in beats)
    if p.get("theme") or chaptered:
        s = K.root(X, cid, t, d, p, inner, k, cls=("f2 " + cls).strip())
        return s, k
    # no theme named: draw on the style's own ground (its tokens), not on the shared paper theme
    K.U.base(X)
    X.css("fx-kinfo", K.CSS)
    from h9.aefx import _clip
    _clip(X, cid, t, d, "", p)
    tok = X.S.get("tokens", {})
    th = {}
    for key, dflt in (("bg", "#f0ece3"), ("fg", "#111111"), ("muted", "#625d56"), ("line", "#d3ccbf"), ("card", "#fbfaf6"), ("card-fg", "#111111"), ("accent", "#e2321f")):
        th[key] = tok.get(key, dflt)
    acc = th["accent"]
    k["on"] = K._on(acc)
    k["fg"] = th["fg"]
    parts = [f"--{key}:{v}" for key, v in th.items()]
    parts += [f"--k-r:{k['r']}px", f"--k-rs:{k['rs']}px", f"--k-bw:{k['bw']}px", f"--k-sh:{K.SHADOW[k['sh']]}",
              f"--k-kf:{K.KICK[k['kick']]}", f"--k-on:{k['on']}", f"--k-alert:{k['alert']}", f"--k-on-alert:{K._on(k['alert'])}",
              f"--k-ink:{th['fg']}"]
    body = f'<div class="ki sk-{k["sid"]} hl-{k["hl"]} f2 {cls}" style="{"; ".join(parts)}">{inner}</div>'
    sid = K.S.stage(X, cid, t, d, body, p, dark_chrome=_is_dark(th["bg"]))
    return f"#{sid}", k


def _is_dark(c):
    from h9.aefx import _lum
    v = _lum(c)
    return v is not None and v < 0.2


def pal(X, p):
    """the real colours behind --bg --fg --muted --accent --card --card-fg (+ "on": text on the accent), for tweens:
    GSAP cannot interpolate var(--x), so colour tweens get the resolved values of the same tokens the stage uses."""
    beats = X.v.get("beats") or []
    chaptered = any(isinstance(b, dict) and b.get("chapter") for b in beats)
    if p.get("theme") or chaptered:
        th = dict(K.ground(X, p))
    else:
        tok = X.S.get("tokens", {})
        th = {}
        for key, dflt in (("bg", "#f0ece3"), ("fg", "#111111"), ("muted", "#625d56"), ("line", "#d3ccbf"), ("card", "#fbfaf6"), ("card-fg", "#111111"), ("accent", "#e2321f")):
            th[key] = tok.get(key, dflt)
    th["on"] = K._on(th.get("accent", "#e2321f"))
    return th


def js(v):
    import json
    return json.dumps(v, ensure_ascii=False, separators=(",", ":"))


def font_file(X, role="display"):
    """path of the first font file of a style role (for build-time rasters that must match the screen), or None."""
    from h9 import fonts as FO
    ids = (X.S.get("fonts") or {}).get(role) or (X.S.get("fonts") or {}).get("display") or "noto-sans-sc"
    if not isinstance(ids, list):
        ids = [ids]
    cjk = None
    for fid in ids:
        meta = FO.REG.get(fid) or {}
        f = FO.find(meta.get("file", "")) if meta.get("file") else None
        if f and cjk is None:
            cjk = f
        if f and fid.startswith(("noto-sans-sc", "noto-serif-sc", "ma-shan", "lxgw", "zcool", "smiley", "long-cang", "zhi-mang", "liu-jian", "alibaba", "harmony", "misans", "fusion")):
            return f                                       # a CJK face covers the headline glyphs
    if cjk:
        return cjk
    meta = FO.REG.get("noto-sans-sc") or {}
    f = FO.find(meta.get("file", "NotoSansSC-VF.ttf"))
    if f:
        return f
    for sysf in ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc", "/System/Library/Fonts/STHeiti Medium.ttc",
                 "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "C:/Windows/Fonts/msyhbd.ttc"):
        if pathlib.Path(sysf).exists():
            return pathlib.Path(sysf)                      # no style font installed: the browser falls back to the system face too
    raise SystemExit("no CJK font found for the build-time glyph raster; install the style's fonts (see references/fonts.md)")


def variable_weight(X, role="display"):
    """True when the style's font for `role` has a weight axis (fonts.json "weight": "100 900")."""
    from h9 import fonts as FO
    ids = (X.S.get("fonts") or {}).get(role) or []
    if not isinstance(ids, list):
        ids = [ids]
    for fid in ids:
        w = str((FO.REG.get(fid) or {}).get("weight", "400"))
        if fid.startswith(("inter", "archivo", "roboto")) and len(ids) > 1:
            continue                                       # a Latin face first in the stack: the CJK one decides
        return " " in w.strip()
    return False


def chars_of(text):
    """visible glyph units of a headline: one per CJK glyph, one per Latin word (keeps *stress* marks out)."""
    s = strip(text)
    out = []
    run = ""
    for ch in s:
        if ch.isascii() and (ch.isalnum() or ch in ".,%-+$"):
            run += ch
            continue
        if run:
            out.append(run)
            run = ""
        if ch.strip() and ch != "|":
            out.append(ch)
    if run:
        out.append(run)
    return out


def strip(s):
    return str(s or "").replace("*", "")


def spoken_units_times(X, text, t, d):
    """per-glyph spoken times of `text` inside the beat, from the word timestamps (None when it is not said)."""
    if not getattr(X, "chars", None):
        return None
    hit = X.spoken_at(strip(text), t, t + d)
    if hit is None:
        return None
    i0 = None
    for i in range(len(X.chars)):
        if abs(X.chars[i][1] - hit) < 1e-3:
            i0 = i
            break
    if i0 is None:
        return None
    want = [c for c in strip(text) if c.isalnum()]
    out = []
    j = i0
    for c in want:
        while j < len(X.chars) and not X.chars[j][0].isalnum():
            j += 1
        if j >= len(X.chars):
            break
        out.append(X.chars[j][1])
        j += 1
    if len(out) < len(want):
        return None
    return out


def hold_push(X, sel, a, b, amt=1.045, origin="50% 45%"):
    """a slow push-in over a held stretch [a, b] so a settled frame never reads as frozen (review.py freeze gate)."""
    if b - a < 0.6:
        return
    X.tw(f'tl.fromTo("{sel}", {{scale:1}}, {{scale:{amt}, transformOrigin:"{origin}", duration:{b - a:.2f}, ease:"sine.inOut", immediateRender:false}}, {a:.3f});')
