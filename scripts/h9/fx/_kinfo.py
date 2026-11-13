"""shared pieces for the key-info-beside-a-subject effects (stack_build · side_stat · key_card · stamp_compare ·
strike_fix · action_card · chip_cycle). Not an effect (files starting with _ are skipped by the loader).

skin()      the style's look for these layouts: radii, border, shadow, highlight kind, kicker font, tilt — read from the
            active style (its id and tokens), so every layout re-skins across all styles without touching style files
root()      the theme page + spoken-line context (via _clip) and an untimed stage on top that holds everything,
            including a playing subject video (timed <video> may not sit inside a timed clip)
subject()   the subject (image or video, any aspect) in a styled card at a given rect, or full-bleed
beside()    where the subject card and the text column go, for 16:9 and 9:16, subject on the left or right
cues()      n moments for n items: "@词" / seconds into the beat / when the narration says the item / evenly spread
fit()       text fitted to a box → (px, lines)
"""
import importlib.util, os, pathlib, sys
from h9 import fit as FT
from h9.aefx import _clip, THEMES


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


S = load("_screens")
U = load("_ui")

# ---------------------------------------------------------------- per-style skin
# r card radius · rs chip radius · bw border px · sh shadow kind · hl highlight kind · kick kicker font · tilt degrees
# sub subject frame (card | bracket | polaroid | plain)
SKINS = {
    "reel":     {"r": 18, "rs": 10, "bw": 0, "sh": "soft", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "press":    {"r": 8, "rs": 6, "bw": 0, "sh": "soft", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "poster":   {"r": 0, "rs": 0, "bw": 0, "sh": "none", "hl": "block", "kick": "latin", "tilt": 0, "sub": "plain"},
    "zine":     {"r": 0, "rs": 0, "bw": 4, "sh": "hard", "hl": "block", "kick": "mono", "tilt": 2.2, "sub": "polaroid"},
    "screen":   {"r": 16, "rs": 999, "bw": 1, "sh": "glow", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "hud":      {"r": 2, "rs": 2, "bw": 1, "sh": "glow", "hl": "block", "kick": "mono", "tilt": 0, "sub": "bracket"},
    "doc":      {"r": 0, "rs": 0, "bw": 0, "sh": "none", "hl": "under", "kick": "latin", "tilt": 0, "sub": "plain"},
    "papercut": {"r": 4, "rs": 4, "bw": 0, "sh": "hard", "hl": "block", "kick": "body", "tilt": 1.2, "sub": "card"},
    "sketch":   {"r": 14, "rs": 12, "bw": 3, "sh": "none", "hl": "marker", "kick": "hand", "tilt": 1.4, "sub": "card"},
    "ink":      {"r": 2, "rs": 2, "bw": 0, "sh": "none", "hl": "wash", "kick": "body", "tilt": 0, "sub": "plain"},
    "flat":     {"r": 30, "rs": 999, "bw": 0, "sh": "none", "hl": "block", "kick": "body", "tilt": 0, "sub": "card"},
    "pixel":    {"r": 0, "rs": 0, "bw": 4, "sh": "hard", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "minimal":  {"r": 2, "rs": 0, "bw": 0, "sh": "line", "hl": "under", "kick": "body", "tilt": 0, "sub": "plain"},
    "atlas":    {"r": 4, "rs": 4, "bw": 1, "sh": "soft", "hl": "under", "kick": "mono", "tilt": 0, "sub": "card"},
    "iso3d":    {"r": 26, "rs": 999, "bw": 0, "sh": "soft", "hl": "block", "kick": "body", "tilt": 0, "sub": "card"},
    "chrome3d": {"r": 18, "rs": 999, "bw": 1, "sh": "glow", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "clay":     {"r": 22, "rs": 999, "bw": 0, "sh": "soft", "hl": "block", "kick": "body", "tilt": 0, "sub": "card"},
    "studio":   {"r": 14, "rs": 8, "bw": 1, "sh": "glow", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
    "brand_qingzhou": {"r": 6, "rs": 6, "bw": 0, "sh": "soft", "hl": "block", "kick": "mono", "tilt": 0, "sub": "card"},
}

SHADOW = {
    "soft": "0 0 0 1px color-mix(in srgb, var(--card-fg) 9%, transparent), 0 26px 64px rgba(0,0,0,.26), 0 6px 16px rgba(0,0,0,.12)",
    "hard": "10px 10px 0 var(--k-ink)",
    "glow": "0 0 0 1px color-mix(in srgb, var(--accent) 45%, transparent), 0 0 46px color-mix(in srgb, var(--accent) 22%, transparent), 0 26px 64px rgba(0,0,0,.5)",
    "line": "0 0 0 1.5px color-mix(in srgb, var(--fg) 70%, transparent)",
    "none": "none",
}
KICK = {"mono": "var(--f-mono, monospace)", "latin": "var(--f-latin, var(--f-body))", "body": "var(--f-body)", "hand": "var(--f-hand, var(--f-body))"}


def style_id(X):
    mod = X.S.get("_mod")
    name = getattr(mod, "__name__", "") or ""
    return name.rsplit(".", 1)[-1]


def _on(color):
    """black or white text, whichever reads better on `color`."""
    from h9.aefx import _contrast
    dark = _contrast("#111111", color)
    light = _contrast("#ffffff", color)
    if dark >= light:
        return "#111111"
    return "#ffffff"


def skin(X):
    sid = style_id(X)
    k = dict(SKINS.get(sid) or SKINS["reel"])
    k["sid"] = sid
    tok = X.S.get("tokens", {})
    k["alert"] = tok.get("alert") or tok.get("accent") or "#e2321f"
    return k


def ground(X, p):
    """the colours of the page this beat draws on. A beat that names a theme gets that theme; otherwise, in a film
    with chapters (scripts/h9/device.py: beat.chapter.bg), the chapter's colour world, so the type always reads on
    the chapter ground; otherwise the style's own ground (its tokens, as fx2's stage does)."""
    if p.get("theme") in THEMES:
        return dict(THEMES[p["theme"]])
    try:
        from h9 import device
    except ImportError:
        device = None
    beats = X.v.get("beats") or []
    beat = getattr(X, "beat", None) or {}
    if device and beats and "i" in beat:
        times = []
        for _ in beats:
            times.append((0.0, 0.0))
        chs = device.chapters(X.v, beats, times, X.S)
        i = int(beat["i"]) - int((X.v.get("meta") or {}).get("beat_offset", 0))
        if chs and 0 <= i < len(chs["of_beat"]):
            w = chs["list"][chs["of_beat"][i]]["world"]
            out = dict(THEMES["paper"])
            for key in ("bg", "fg", "muted", "line", "card", "card-fg", "accent"):
                if w.get(key):
                    out[key] = w[key]
            return out
    return style_ground(X)


GROUND_DEFAULTS = (("bg", "#f0ece3"), ("fg", "#111111"), ("muted", "#625d56"), ("line", "#d3ccbf"), ("card", "#fbfaf6"),
                   ("card-fg", "#111111"), ("accent", "#e2321f"))


def style_ground(X):
    """the active style's own colours (its tokens), for a beat that names no theme."""
    tok = X.S.get("tokens", {})
    out = {}
    for key, dflt in GROUND_DEFAULTS:
        out[key] = tok.get(key, dflt)
    return out


def _dark(c):
    from h9.aefx import _lum
    v = _lum(c)
    return v is not None and v < 0.2


def root_vars(X, p, k):
    th = ground(X, p)
    acc = th.get("accent", "#e2321f")
    ink = th.get("fg", "#111")
    if k["sh"] == "hard" and k["sid"] == "papercut":
        ink = "#1e1b18"
    k["on"] = _on(acc)
    k["fg"] = th.get("fg", "#111")
    parts = []
    for key in ("bg", "fg", "muted", "line", "card", "card-fg", "accent"):
        if th.get(key):
            parts.append(f"--{key}:{th[key]}")
    parts += [
        f"--k-r:{k['r']}px", f"--k-rs:{k['rs']}px", f"--k-bw:{k['bw']}px", f"--k-sh:{SHADOW[k['sh']]}",
        f"--k-kf:{KICK[k['kick']]}", f"--k-on:{_on(acc)}", f"--k-alert:{k['alert']}", f"--k-on-alert:{_on(k['alert'])}",
        f"--k-ink:{ink}",
    ]
    return "; ".join(parts)


CSS = r"""
.ki { position:absolute; inset:0; overflow:hidden; color:var(--fg); }
.ki .k-kick { position:absolute; font:700 22px var(--k-kf); letter-spacing:.16em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }
.ki .k-card { position:absolute; background:var(--card); color:var(--card-fg); border-radius:var(--k-r); box-shadow:var(--k-sh);
  outline:var(--k-bw) solid var(--k-ink); outline-offset:calc(var(--k-bw) * -1); }
.ki.sk-sketch .k-card, .ki.sk-sketch .k-sub { border-radius:28px 6px 24px 8px / 8px 26px 6px 30px; }
.ki .k-sub { position:absolute; overflow:hidden; border-radius:var(--k-r); box-shadow:var(--k-sh); background:color-mix(in srgb, var(--accent) 16%, var(--bg));
  outline:var(--k-bw) solid var(--k-ink); outline-offset:calc(var(--k-bw) * -1); }
.ki .k-sub > img, .ki .k-sub > video { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; display:block; }
.ki .k-sub.contain > img, .ki .k-sub.contain > video { object-fit:contain; object-position:50% 100%; }
.ki .k-sub.full { border-radius:0; box-shadow:none; outline:0; }
.ki .k-sub.polaroid { overflow:visible; background:#fbf8f0; box-shadow:0 18px 40px rgba(0,0,0,.28); outline:0; border-radius:0; }
.ki .k-sub.polaroid .k-pin { position:absolute; left:14px; top:14px; right:14px; bottom:58px; overflow:hidden; background:#ddd; }
.ki .k-sub.polaroid .k-pin > img, .ki .k-sub.polaroid .k-pin > video { width:100%; height:100%; object-fit:cover; display:block; }
.ki .k-sub.polaroid .k-tape { position:absolute; left:50%; top:-18px; width:130px; height:34px; margin-left:-65px; background:color-mix(in srgb, var(--accent) 70%, transparent); transform:rotate(-4deg); }
.ki .k-sub.plain { border-radius:0; box-shadow:none; outline:0; }
.ki .k-sub .k-stag { position:absolute; left:16px; top:16px; z-index:3; display:flex; align-items:center; gap:8px; font:700 17px var(--f-mono, monospace); letter-spacing:.12em;
  color:#fff; background:rgba(0,0,0,.55); padding:5px 10px; border-radius:var(--k-rs); white-space:nowrap; }
.ki .k-sub .k-stag i { width:9px; height:9px; border-radius:50%; background:#ff3b30; }
.ki .k-brk { position:absolute; pointer-events:none; }
.ki .k-brk i { position:absolute; width:46px; height:46px; border:5px solid var(--accent); }
.ki .k-brk i:nth-child(1) { left:0; top:0; border-right:0; border-bottom:0; } .ki .k-brk i:nth-child(2) { right:0; top:0; border-left:0; border-bottom:0; }
.ki .k-brk i:nth-child(3) { left:0; bottom:0; border-right:0; border-top:0; } .ki .k-brk i:nth-child(4) { right:0; bottom:0; border-left:0; border-top:0; }
.ki .k-scrim { position:absolute; inset:0; pointer-events:none; }
/* the stressed word: a filled block (most styles), an underline bar (minimal, doc, atlas), a marker swipe (sketch), an ink wash (ink) */
.ki .k-hl { position:relative; display:inline-block; z-index:0; }
.ki .k-hl > b { position:absolute; z-index:-1; left:-.12em; right:-.12em; top:.04em; bottom:-.02em; background:var(--accent); transform-origin:0 50%; border-radius:calc(var(--k-rs) * .6); }
.ki.hl-under .k-hl > b { top:auto; height:.13em; bottom:-.08em; left:0; right:0; border-radius:0; }
.ki.hl-marker .k-hl > b { top:.38em; bottom:-.04em; background:color-mix(in srgb, var(--accent) 55%, transparent); border-radius:.4em .1em .5em .1em; transform:rotate(-1.2deg); }
.ki.hl-wash .k-hl > b { top:.2em; bottom:-.06em; background:color-mix(in srgb, var(--accent) 40%, transparent); box-shadow:inset 0 -.1em 0 var(--accent); border-radius:0; filter:blur(.6px); }
.ki.sk-pixel .k-hl > b { border-radius:0; box-shadow:.08em .08em 0 var(--k-ink); }
.ki.sk-zine .k-hl > b { transform:rotate(-1.5deg); }
.ki .k-chip { position:absolute; display:inline-flex; align-items:center; gap:10px; white-space:nowrap; font:800 26px var(--f-body); border-radius:var(--k-rs); padding:8px 16px; }
.ki .k-stamp { position:absolute; display:inline-flex; align-items:center; gap:10px; white-space:nowrap; font:900 40px var(--f-display); color:var(--k-alert);
  border:5px solid var(--k-alert); border-radius:calc(var(--k-rs) * .5 + 4px); padding:6px 18px; background:color-mix(in srgb, var(--card) 82%, transparent); letter-spacing:.04em; }
.ki.sk-ink .k-stamp { background:var(--k-alert); color:var(--k-on-alert); border-color:var(--k-alert); border-radius:6px; }
.ki.sk-pixel .k-stamp, .ki.sk-poster .k-stamp, .ki.sk-zine .k-stamp { border-radius:0; }
#root.v .ki .k-kick, #root.v .ki .sb-en, #root.v .ki .sf-margin small, #root.v .ki .kc-pg,
#root.v .ki .ss-bar span, #root.v .ki .cc-file, #root.v .ki .k-sub .k-stag { font-size:26px !important; }
#root.v .ki .sc-lab small { font-size:26px; }
.ki .k-flash { position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none; z-index:40; }
"""

ICON_X = '<svg viewBox="0 0 24 24" style="width:.8em;height:.8em"><path d="M5 5L19 19M19 5L5 19" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" fill="none"/></svg>'
ICON_OK = '<svg viewBox="0 0 24 24" style="width:.8em;height:.8em"><path d="M4.5 12.5l5 5L19.5 6.5" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>'
ICON_LOCK = '<svg viewBox="0 0 24 24" style="width:.85em;height:.85em"><rect x="5" y="10.5" width="14" height="10" rx="2" fill="currentColor"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5" stroke="currentColor" stroke-width="2.6" fill="none"/></svg>'
ICON_LINK = '<svg viewBox="0 0 24 24" style="width:1em;height:1em"><path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" fill="none"/></svg>'


def ease(X):
    """the style's entrance ease (steps for pixel / zine, a springy back for flat / iso3d, expo for most)."""
    return X.M.get("ease", "expo.out")


def area(X, p):
    """the content box (under the page header, above the caption). Inside a presenter region (scripts/h9/presenter.py
    shrinks X.W / X.H to the space the presenter leaves) a tall region can be shorter than the 9:16 caption band, so
    the box is also kept inside the region."""
    x0, y0, x1, y1 = S.area(X, p)
    if y1 > X.H - 24:
        y1 = X.H - 24
    if x1 > X.W - 24:
        x1 = X.W - 24
    return x0, y0, x1, y1


def low(X, p):
    """how far down a picture (subject card, window — no text) may reach. 9:16 full frame: down to the top of the
    platform's bottom zone (the last 400 px), so the card runs behind the caption band instead of leaving it empty;
    text stays above the caption (area()). Elsewhere: the content box bottom."""
    x0, y0, x1, y1 = area(X, p)
    if X.portrait and X.H >= 1900:
        return X.H - 400
    return y1


def src_of(p):
    """the subject: subject | video | image (in that order); $H9_MEDIA / ~ paths are expanded."""
    for key in ("subject", "video", "image"):
        v = p.get(key)
        if v:
            return os.path.expandvars(os.path.expanduser(str(v)))
    return None


def subject_ar(X, src, dflt=0.8):
    if not src:
        return dflt
    a = FT._abs(X, src)
    if FT.is_video(src):
        import subprocess
        try:
            out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(a)], text=True)
            first = out.strip().splitlines()[0]
            w, h = first.split(",")[:2]
            return float(w) / float(h)
        except Exception:
            return 16 / 9
    sz = FT.size(a)
    if not sz:
        return dflt
    return sz[0] / sz[1]


def subject(X, p, x, y, w, h, t, d, k, cls="", full=False):
    """the subject in a card at (x, y, w, h) — or full-bleed when full=True. A .webm (a transparent mascot) is
    contained on a tinted set; photos and footage are cover-cropped around subject_focus."""
    src = src_of(p)
    if not src:
        return ""
    focus = p.get("subject_focus") or p.get("focus")
    fit_mode = p.get("subject_fit") or ("contain" if str(src).lower().endswith(".webm") else "cover")
    frame = "full" if full else (p.get("subject_frame") or k["sub"])
    pin_w, pin_h = w, h
    if frame == "polaroid":
        pin_w = w - 28
        pin_h = h - 72
    if FT.is_video(src):
        media = S.vtag(X, src, t, d, pin_w, pin_h, float(p.get("subject_start", 0)), focus)
    else:
        media = f'<img src="{X.asset(src)}" alt="" style="object-position:{FT.focus_css(focus)}">'
    tag = ""
    if p.get("subject_tag"):
        X.used_text.update(str(p["subject_tag"]))
        tag = f'<div class="k-stag"><i></i>{X.rich(p["subject_tag"])}</div>'
    classes = f"k-sub {cls}"
    if fit_mode == "contain":
        classes += " contain"
    if frame in ("polaroid", "plain", "full"):
        classes += f" {frame}"
    style = f"left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px;"
    if k.get("tilt") and not full:
        style += f" transform:rotate({k['tilt']:.1f}deg);"        # zine / papercut / sketch: the card sits a little askew
    if frame == "polaroid":
        return f'<div class="{classes}" style="{style}"><div class="k-pin">{media}</div><i class="k-tape"></i>{tag}</div>'
    extra = ""
    if frame == "bracket":
        extra = brackets(x - 18, y - 18, w + 36, h + 36, cls="k-sbrk")
    return f'<div class="{classes}" style="{style}">{media}{tag}</div>{extra}'


def brackets(x, y, w, h, cls=""):
    return f'<div class="k-brk {cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px"><i></i><i></i><i></i><i></i></div>'


def beside(X, p, sub_ar=0.78, side="right", sub_share=None):
    """→ (subject rect, text rect) inside the content area. 16:9: the card is as tall as the area allows (capped at a
    share of the width); 9:16: the card takes the lower part of the frame at full width when it is wide, else a
    tall card beside a narrow text column — both fill the frame top to bottom."""
    x0, y0, x1, y1 = area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    gap = 64 if not X.portrait else 40
    share = sub_share or (0.42 if not X.portrait else 0.52)
    if X.portrait and sub_ar > 0.74:
        sub_ar = 0.74          # 9:16: a taller card fills the column instead of floating as a small square
    sh = ah * 0.94
    sw = sh * sub_ar
    if sw > aw * share:
        sw = aw * share
        sh = sw / sub_ar
    if sh > ah:
        sh = ah
    sy = y0 + (ah - sh) / 2
    if side == "left":
        sx = x0
        tx = x0 + sw + gap
    else:
        sx = x1 - sw
        tx = x0
    tw = aw - sw - gap
    return (sx, sy, sw, sh), (tx, y0, tw, ah)


def cues(X, p, key, t, d, n, start=0.35, end=0.82, texts=None):
    """n absolute times: p[key][i] when given ("@词" or seconds into the beat), else when the narration says
    texts[i] inside the beat (U.follow), else spread over [start, end] of the beat."""
    given = p.get(key)
    if not isinstance(given, (list, tuple)):
        given = []
    auto = U.spread(n, t + d * start if n > 1 else t + min(0.5, d * start), t + d * end)
    out = []
    fixed = []
    for i in range(n):
        v = given[i] if i < len(given) else None
        out.append(U.when(X, v, t, auto[i] if i < len(auto) else t))
        fixed.append(v is not None)
    if texts:
        out = U.follow(X, texts, t, d, out, fixed, gap=0.25)
    for i in range(1, n):
        if out[i] < out[i - 1] + 0.25:
            out[i] = out[i - 1] + 0.25
    return out


def fit(text, w, h, max_px, min_px, max_lines=2, lh=1.12, mono=False):
    f = FT.fit_text(str(text), w, h, max_px, min_px, lh=lh, max_lines=max_lines, mono=mono)
    return f.px, f.lines


def hl_html(X, text):
    """*词* → the stressed span with its highlight block; plain text otherwise."""
    s = str(text)
    out = []
    parts = s.split("*")
    for i in range(len(parts)):
        part = parts[i]
        if not part:
            continue
        X.used_text.update(part)
        if i % 2 == 1:
            out.append(f'<span class="k-hl"><b></b><span class="k-hlt">{X.rich(part)}</span></span>')
        else:
            out.append(X.rich(part))
    return "".join(out)


def strip(s):
    return str(s).replace("*", "")


def root(X, cid, t, d, p, inner, k, cls=""):
    """theme page + context underneath, the stage with `inner` on top → '#stage_id'."""
    U.base(X)
    X.css("fx-kinfo", CSS)
    _clip(X, cid, t, d, "", p)
    body = f'<div class="ki sk-{k["sid"]} hl-{k["hl"]} {cls}" style="{root_vars(X, p, k)}">{inner}</div>'
    dark = p.get("theme") == "ink" or (p.get("theme") not in THEMES and _dark(ground(X, p).get("bg", "")))
    sid = S.stage(X, cid, t, d, body, p, dark_chrome=dark)
    return f"#{sid}"


def hl_tween(X, sel, at, k):
    """the highlight block wipes in under the stressed word; with a filled block the word turns to the on-accent colour."""
    X.tw(f'tl.fromTo("{sel} .k-hl > b", {{scaleX:0}}, {{scaleX:1, duration:0.32, ease:"power3.out", immediateRender:true}}, {at:.3f});')
    if k["hl"] == "block":
        X.tw(f'tl.to("{sel} .k-hl .k-hlt", {{color:"{k['on']}", duration:0.12}}, {at + 0.1:.3f});')


def rise(X, sel, at, e, dist=40, dur=0.5):
    """masked rise: the element slides up out of an invisible slot (clip-path), never a plain fade."""
    X.tw(f'tl.fromTo("{sel}", {{y:{dist}, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 -20% 0)", duration:{dur:.2f}, ease:"{e}", immediateRender:true}}, {at:.3f});')


def subject_in(X, sel, at, e, full=False):
    if full:
        X.tw(f'tl.fromTo("{sel}", {{scale:1.12}}, {{scale:1.0, duration:0.9, ease:"power3.out"}}, {at:.3f});')
        return
    X.tw(f'tl.fromTo("{sel}", {{y:60, scale:0.92, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.6, ease:"{e}", immediateRender:true}}, {at:.3f});')


def subject_drift(X, sel, t, d, full=False):
    """keep the subject alive: a slow push."""
    amt = 1.06 if full else 1.03
    X.tw(f'tl.fromTo("{sel}", {{scale:1}}, {{scale:{amt}, duration:{max(0.5, d - 0.9):.2f}, ease:"none", immediateRender:false}}, {t + 0.9:.3f});')
