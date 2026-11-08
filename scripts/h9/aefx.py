"""AE 动效库 —— re-creations of the most popular After Effects motion techniques as seekable HTML/CSS/SVG/GSAP.

Each effect: fx(X, cid, t, d, p) -> adds one clip (and its tweens) to the build.  p = params dict.
Works at any aspect: sizes are in vmin/% where it matters. Colours come from the style tokens.
Any input size: text is fitted (shrink → balanced wrap by words → ellipsis), lists and image sets lay out by count,
pictures of any aspect are placed with a focal point, and video works where it is marked below (see references/inputs.md).
Only generic techniques are re-created (no template designs or assets copied).
"""
import math

from h9 import fit
from h9.core import RTL_RX

CSS = r"""
.fx { overflow:hidden; }
.fx > .stage { display:flex; align-items:center; justify-content:center; }
.fx i { font-style:normal; }
.fx .ln { display:block; overflow:hidden; padding:.08em .1em .14em; margin:-.08em -.1em -.14em; }
.fx .c, .fx .w { display:inline-block; will-change:transform; }
.fx .big { font-family:var(--f-display); font-weight:var(--display-weight, 800); font-size:var(--fx-size, 15vmin); line-height:1.05; color:var(--fg); letter-spacing:var(--display-tracking, 0); text-align:center; }
.fx .sub { font-family:var(--f-latin, var(--f-body)); font-size:2.2vmin; letter-spacing:.42em; color:var(--muted); text-transform:uppercase; margin-top:2.2vmin; text-align:center; max-width:84vw; line-height:1.5; }
.fx .col { display:flex; flex-direction:column; align-items:center; max-width:100%; }
.fx-tag { position:absolute; left:4vmin; bottom:4vmin; font:500 1.6vmin/1.4 var(--f-mono, monospace); color:var(--muted); letter-spacing:.12em; text-transform:uppercase; }
.fx-tag b { color:var(--accent); font-weight:500; }
"""


def _chars(X, s, cls="c"):
    """every glyph in its own <i class="c"> (for staggers); *强调* survives."""
    if cls == "c": return X.rich(s, split="chars")
    if RTL_RX.search(str(s)): return f'<i class="{cls}">{X.rich(s)}</i>'      # Arabic / Hebrew keep their joins: one run
    return "".join(f'<i class="{cls}">{X.rich(ch)}</i>' if ch.strip() else " " for ch in fit.plain(s))


def _tag(X, p):
    if not p.get("label"): return ""
    return f'<div class="fx-tag"><b>{X.rich(p["label"])}</b>{("　" + X.rich(p["ref"])) if p.get("ref") else ""}</div>'


# page themes for a beat ("theme": "paper" | "ink" | "red" | "lemon"): the effect inherits the colours through CSS variables
THEMES = {
    "paper": {"bg": "#f0ece3", "fg": "#111111", "muted": "#625d56", "accent": "#e2321f", "card": "#fbfaf6", "card-fg": "#111111", "line": "#d3ccbf"},
    "ink":   {"bg": "#121212", "fg": "#f3efe6", "muted": "#958f85", "accent": "#f6ce3a", "card": "#1d1c1a", "card-fg": "#f3efe6", "line": "#2c2a27"},
    "red":   {"bg": "#e2321f", "fg": "#fbfaf6", "muted": "rgba(255,255,255,.78)", "accent": "#111111", "card": "#fbfaf6", "card-fg": "#111111", "line": "rgba(255,255,255,.3)"},
    "lemon": {"bg": "#f6ce3a", "fg": "#111111", "muted": "#5b4a12", "accent": "#e2321f", "card": "#fbfaf6", "card-fg": "#111111", "line": "rgba(0,0,0,.2)"},
}
CTX_CSS = r"""
.ctx { pointer-events:none; }
.ctx .hd { position:absolute; left:96px; right:96px; top:40px; height:44px; display:flex; align-items:center; justify-content:space-between; border-bottom:2px solid var(--fg);
  font-family:var(--f-body); font-size:22px; color:var(--fg); }
.ctx .hd b { font-weight:900; letter-spacing:.04em; } .ctx .hd span { opacity:.7; margin-left:14px; }
.ctx .hd .fxid { font-family:var(--f-mono); font-size:18px; letter-spacing:.06em; background:var(--fg); color:var(--bg); padding:2px 10px; }
.ctx .cap { position:absolute; left:0; right:0; bottom:66px; text-align:center; }
.ctx .cap > span { display:inline-block; font-family:var(--f-body); font-weight:700; font-size:40px; line-height:1.3; color:var(--bg); background:var(--fg); padding:8px 24px 10px; border-radius:8px; max-width:80%; }
.ctx .cap .em .emt { background:var(--cap-em-bg, #f6ce3a); color:var(--cap-em-fg, #111); padding:0 .12em; } .ctx .cap .em .emb { display:none; }
.ctx .ft { position:absolute; left:96px; right:96px; bottom:22px; display:flex; justify-content:space-between; font-family:var(--f-mono); font-size:16px; color:var(--fg); opacity:.6; letter-spacing:.04em; }
.ctx .ft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:60%; }
.ctx.photo .hd, .ctx.photo .ft { color:#fff; border-color:rgba(255,255,255,.7); text-shadow:0 1px 8px rgba(0,0,0,.6); opacity:1; }
.ctx.photo .hd .fxid { background:#fff; color:#111; text-shadow:none; }
.ctx.photo .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.55), rgba(0,0,0,0) 18%, rgba(0,0,0,0) 72%, rgba(0,0,0,.6)); }
#root.v .fx .sub { max-width:840px; } #root.v .ctx .hd { left:56px; right:56px; top:206px; } #root.v .ctx .ft { left:56px; right:56px; bottom:auto; top:1478px; }
#root.v .ctx .cap { bottom:auto; top:1330px; padding:0 120px; } #root.v .ctx .cap > span { font-size:44px; max-width:100%; }
"""
PHOTO = {"parallax", "portal", "mosaic", "callout", "match_cut", "plate"}
BASE_THEMES = {k: dict(v) for k, v in THEMES.items()}
_DARK = {"bg": "#121212", "fg": "#efeae1", "muted": "#8f897f", "line": "#2c2a27", "card": "#1c1b19", "card-fg": "#efeae1"}


def _lum(c):
    c = str(c).strip()
    if not (c.startswith("#") and len(c) in (4, 7)): return None
    if len(c) == 4: c = "#" + "".join(ch * 2 for ch in c[1:])
    rgb = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a, b):
    la, lb = _lum(a), _lum(b)
    if la is None or lb is None: return 21.0     # rgba() / named colours: trust the style
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def apply_style(S):
    """point the four page themes (paper / ink / red / lemon) at the active style, in place, so every effect and every
    plugin that imported THEMES follows the style's palette. reel keeps the classic set. Derived from the style tokens
    (falling back to the card colour when text would not read on the ground); STYLE["fx_themes"] overrides any of them."""
    sid = getattr(S.get("_mod"), "__name__", "").rsplit(".", 1)[-1]
    THEMES.clear(); THEMES.update({k: dict(v) for k, v in BASE_THEMES.items()})
    if sid in ("", "reel"): return
    tok = S.get("tokens", {})
    paper = {k: tok.get(k, v) for k, v in BASE_THEMES["paper"].items()}
    if _contrast(paper["fg"], paper["bg"]) < 4.5:
        paper.update(bg=paper["card"], fg=paper["card-fg"])
    ink = {**paper, **_DARK, **((S.get("moods") or {}).get("heavy") or {})}
    ink = {k: ink[k] for k in paper}
    red = dict(paper)
    if _contrast(paper["card"], paper["accent"]) >= 3:
        red.update(bg=paper["accent"], fg=paper["card"], muted=paper["card"], accent=paper["fg"], line=paper["card"])
    lemon = {**paper, "bg": paper["card"], "fg": paper["card-fg"]}
    THEMES.update(paper=paper, ink=ink, red=red, lemon=lemon)
    for k, v in (S.get("fx_themes") or {}).items():
        THEMES[k] = {**THEMES.get(k, paper), **v}


def _theme_style(p, paint=True):
    th = THEMES.get(p.get("theme"))
    return (";".join(f"--{k}:{v}" for k, v in th.items()) + (";background:var(--bg)" if paint else "")) if th else ""


def ctx_parts(X, p):
    """the pieces of the page around an effect, already fitted: topic, effect id, caption (html lines + px), footnote,
    source, whether it sits over a photo, and the theme variables. A style's FX_FRAME lays these out its own way."""
    photo = p.get("fx") in PHOTO and not p.get("theme_over_photo")
    th = THEMES.get(p.get("theme"))
    sty = ";".join(f"--{k}:{v}" for k, v in th.items()) if th else ""
    fxid = p.get("fxid") or p.get("fx", "")
    foot_s = (fit.plain(p["label"]) + ("　" + fit.plain(p["ref"]) if p.get("ref") else "")) if p.get("label") else ""
    fpx = 17 if X.portrait else 16
    avail = (X.W - 112) if X.portrait else (X.W - 192)
    wpx = lambda s: (fit.width(s, mono=True) + 0.04 * len(fit.plain(s))) * fpx      # mono + .04em tracking
    src_s, src = p.get("src", ""), X.rich(p.get("src", ""))
    if src_s:      # label 60 % / source 60 % as before; when both are long they split the row instead of overlapping
        sw = min(wpx(src_s), avail * 0.6)
        fw = max(avail * 0.4, min(avail * 0.6, avail - sw - 32))
        sw = min(sw, avail - fw - 32)
        if wpx(src_s) > sw: src = X.rich(fit.fit_text(src_s, sw, fpx * 1.4, fpx, fpx, max_lines=1, mono=True, ls=0.04).lines[0])
    else:
        fw = avail * 0.96
    if p.get("ref") and wpx(fit.plain(p["label"]) + "　") > fw - 6 * fpx: foot_s = fit.plain(p["label"])   # no room for the ref: drop it, not the label
    foot = X.rich(fit.fit_text(foot_s, fw, fpx * 1.4, fpx, fpx, max_lines=1, mono=True, ls=0.04).lines[0]) if foot_s else ""   # ellipsized to its slot
    cw = (X.W - 2 * SAFE_R - 48) if X.portrait else X.W * 0.8 - 48   # caption: two lines (three in 9:16), shrinking to 28 px;
    mx = 44 if X.portrait else 40                                     # 9:16 keeps 120 px both sides for the platform buttons
    ml = 3 if X.portrait else 2
    cf = fit.fit_text(fit.as_text(p["line"], " "), cw, mx * 1.3 * ml, mx, 28, lh=1.3, max_lines=ml)
    cap = "<br>".join(X.rich(l) for l in cf.lines)
    return {"topic": X.rich(p.get("topic", "")), "fxid": X.rich(fxid), "cap": cap, "cap_lines": [X.rich(l) for l in cf.lines],
            "cap_px": cf.px, "foot": foot, "src": src, "photo": photo, "sty": sty}


def _context(X, cid, t, d, p):
    """the page around an effect, so a preview reads like a frame of a real 口播: header (show · topic · effect id),
    the spoken line as a caption with its keyword marked, and the effect's popularity as the footnote.
    A style can draw its own page with FX_FRAME(X, cid, t, d, p, parts) (parts = ctx_parts); it then owns the clip
    "<cid>c" and its caption entrance. Styles that only restyle the default page override .ctx rules in their css."""
    if not p.get("line"): return
    X.css("aefx-ctx", CTX_CSS)
    k = ctx_parts(X, p)
    frame = getattr(X.S.get("_mod"), "FX_FRAME", None)
    if frame:
        frame(X, cid, t, d, p, k)
    else:
        inner = (('<div class="scrim"></div>' if k["photo"] else "")
                 + f'<div class="hd"><div><b>{X.rich(X.channel)}</b><span>{k["topic"]}</span></div><div class="fxid">{k["fxid"]}</div></div>'
                 + f'<div class="cap"><span style="font-size:{k["cap_px"]}px">{k["cap"]}</span></div><div class="ft"><div>{k["foot"]}</div><div>{k["src"]}</div></div>')
        X.clip(f"{cid}c", t, d, inner, f"ctx{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
        X.tw(f'tl.from("#{cid}c .cap > span", {{y:16, opacity:0, duration:0.3, ease:"power3.out"}}, {t + 0.05:.3f});')
    if p.get("host"):    # the talking host in the corner, as a presenter would be
        src = X.v.get("meta", {}).get("host_video")
        if src:
            url = X.asset(src, "video")
            pos = "right:40px; top:236px; width:270px; height:270px" if X.portrait else "right:64px; top:auto; bottom:0; width:330px; height:330px"
            X.clip(f"{cid}m", t, d, "", "mascot mf-sticker", 31, track=21, tag="video",
                   attrs=f'src="{url}" muted playsinline data-media-start="{(t * 1.7) % 12:.3f}"', sty=f"left:auto; bottom:auto; {pos}")
            X.tw(f'tl.from("#{cid}m", {{scale:0.7, yPercent:12, opacity:0, transformOrigin:"50% 100%", duration:0.4, ease:"back.out(1.7)"}}, {t + 0.15:.3f});')


def _cap_clear(X, p):
    """px from the bottom edge that the caption pill of `line` occupies (16:9 only; in 9:16 it sits at 1330 px)."""
    if not p.get("line") or X.portrait: return 0
    cf = fit.fit_text(fit.as_text(p["line"], " "), X.W * 0.8 - 48, 40 * 1.3 * 2, 40, 28, lh=1.3, max_lines=2)
    return 66 + cf.n * cf.px * 1.3 + 18 + 24


def _clip(X, cid, t, d, inner, p, extra_cls="", transparent=False):
    """transparent=True when a moving picture sits under the clip (fit.media video layers are root siblings)."""
    X.css("aefx", CSS)
    tag = "" if p.get("line") else _tag(X, p)
    X.clip(cid, t, d, inner + tag, f"scene fx {extra_cls}", 3, sty=_theme_style(p, paint=not transparent))
    _context(X, cid, t, d, p)


# ------------------------------------------------------------------ fitting
def _vm(X, v): return min(X.W, X.H) * v / 100


SAFE_R = 120     # 9:16: platform buttons sit in the right 120 px of the lower half — centred text keeps that margin on both sides


def _fit(X, text, box=(0.84, 0.46), max_vmin=15, min_vmin=4.2, max_lines=3, mono=False, lh=1.12, ls=0.0):
    bw = min(X.W * box[0], X.W - 2 * SAFE_R) if X.portrait else X.W * box[0]
    return fit.fit_text(fit.as_text(text), bw, X.H * box[1], _vm(X, max_vmin), _vm(X, min_vmin),
                        lh=lh, max_lines=max_lines, mono=mono, ls=ls)


def _lines(X, f, mode="br"):
    if mode == "chars": return "<br>".join(_chars(X, l) for l in f.lines)
    if mode == "ln": return "".join(f'<span class="ln"><span class="w">{X.rich(l)}</span></span>' for l in f.lines)
    return "<br>".join(X.rich(l) for l in f.lines)


def _big(X, p, key="text", mode="br", cls="big", style="", dflt="", **kw):
    """the effect's headline, fitted to the frame: returns (html, Fit)."""
    f = _fit(X, p.get(key) if p.get(key) not in (None, "") else dflt, **kw)
    return f'<div class="{cls}" style="font-size:{f.px}px;{style}">{_lines(X, f, mode)}</div>', f


def _sub(X, p, key="sub"):
    return f'<div class="sub">{X.rich(p[key])}</div>' if p.get(key) else ""


def _nglyph(f): return max(1, sum(1 for l in f.lines for c in fit.plain(l) if c.strip()))


def _st(d, n, each, share=0.45):
    """a stagger that never runs past `share` of the beat, however many items."""
    return min(each, d * share / max(n, 1))


# ------------------------------------------------------------------ text
def pop(X, cid, t, d, p):
    """逐字弹出 (Animation Composer 'Pop' / Bounce): scale 0 → 1.18 → 1, 1 frame stagger, back ease."""
    big, f = _big(X, p, mode="chars")
    _clip(X, cid, t, d, f'<div class="col">{big}{_sub(X, p)}</div>', p)
    X.tw(f'tl.from("#{cid} .big .c", {{scale:0, y:"0.2em", duration:0.42, ease:"back.out(2.6)", stagger:{_st(d, _nglyph(f), 0.035):.4f}}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, y:14, duration:0.6, ease:"power3.out"}}, {t + 0.45:.3f});')
    X.sfx(t + 0.1, "pop")


def mask_up(X, cid, t, d, p):
    """行遮罩上移 (the most-used title reveal): each line rises out of its own mask, expo.out."""
    big, f = _big(X, p, mode="ln", max_lines=4)
    _clip(X, cid, t, d, f'<div class="col">{big}{_sub(X, p)}</div>', p)
    X.tw(f'tl.from("#{cid} .ln .w", {{yPercent:115, duration:0.85, ease:"expo.out", stagger:{_st(d, f.n, 0.12, 0.3):.3f}}}, {t + 0.1:.3f});')
    if p.get("sub"): X.tw(f'tl.from("#{cid} .sub", {{yPercent:100, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.5:.3f});')
    if d >= 1.8:      # the exit only when the beat is long enough to read the line first
        X.tw(f'tl.to("#{cid} .ln .w", {{yPercent:-115, duration:0.45, ease:"power3.in", stagger:0.06}}, {t + d - 0.55:.3f});')
    X.sfx(t + 0.1, "enter")


def tracking(X, cid, t, d, p):
    """字距收拢 (Tracking In): glyphs start spread wide and drift together while sharpening — done with transforms
    (x offset ∝ distance from the centre of its own line), so it never snaps to whole pixels like letter-spacing would."""
    big, f = _big(X, p, mode="chars", cls="big trk", max_lines=2)
    _clip(X, cid, t, d, f'<div class="col">{big}{_sub(X, p)}</div>', p)
    offs = []
    for l in f.lines:
        m = sum(1 for c in fit.plain(l) if c.strip())
        spread = min(float(p.get("spread", 90)), X.W * 0.6 / max(m, 1)) * f.px / _vm(X, 15)
        offs += [round((i - (m - 1) / 2) * spread, 1) for i in range(m)]
    X.tw(f'tl.from("#{cid} .trk .c", {{x:(i)=>[{",".join(map(str, offs))}][i] || 0, opacity:0, filter:"blur(10px)", duration:1.6, ease:"power3.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .sub .c, #{cid} .sub", {{opacity:0, duration:0.8}}, {t + 0.9:.3f});')
    X.sfx(t, "whoosh_soft")


def blur_focus(X, cid, t, d, p):
    """模糊聚焦 (Don't quit 式): words arrive out of a heavy blur at different times, then lock sharp."""
    f = _fit(X, p.get("text", ""))
    rows = []
    for l in f.lines:
        ws = l.split(" ") if " " in fit.plain(l) else fit.tokens(fit.plain(l)) if "*" not in l else [l]
        rows.append(" ".join(f"<i class=w>{X.rich(w)}</i>" for w in ws if w))
    n = sum(r.count("<i class=w>") for r in rows)
    rank = fit.seeded_order(n, X.rand)
    _clip(X, cid, t, d, f'<div class="big" style="font-size:{f.px}px">{"<br>".join(rows)}</div>', p)
    each = _st(d, n, 0.22, 0.4)
    X.tw(f'tl.from("#{cid} .w", {{opacity:0, filter:"blur(28px)", scale:1.25, duration:0.9, ease:"power2.out", stagger:(i)=>[{",".join(map(str, rank))}][i]*{each:.3f}}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")


def typewriter(X, cid, t, d, p):
    """打字机 + 光标: one glyph per 2 frames, blinking caret (deterministic blink on the timeline)."""
    f = _fit(X, p.get("text", ""), mono=True, max_lines=4)
    _clip(X, cid, t, d, f'<div class="big tw" style="font-family:var(--f-mono); font-size:{f.px}px">{_lines(X, f, "chars")}<i class="caret">▍</i></div>', p)
    X.tw(f'tl.from("#{cid} .tw .c", {{display:"none", duration:0.01, stagger:{_st(d - 0.4, _nglyph(f), 0.066, 0.7):.4f}}}, {t + 0.2:.3f});')
    for k in range(int(d / 0.5)):
        X.tw(f'tl.set("#{cid} .caret", {{opacity:{k % 2}}}, {t + k * 0.5:.3f});')
    X.sfx(t + 0.2, "type")


def scramble(X, cid, t, d, p):
    """乱码解码 (Decoder / Scramble): every slot is a reel of random glyphs that steps (not slides) onto its real
    character, slots settling left→right. Pure transforms with a steps() ease, so it seeks in any order."""
    pool = p.get("pool", "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#$%&@")
    f = _fit(X, p.get("text", ""), mono=True, max_lines=3)
    X.used_text.update(pool + "".join(f.lines))
    k = 9; rows, i = [], 0
    for l in f.lines:
        slots = []
        for ch in fit.plain(l):
            reel = "".join(f'<i class="g">{X.rich(pool[X.rand.randrange(len(pool))])}</i>' for _ in range(k)) + f'<i class="f">{X.rich(ch)}</i>'
            slots.append(f'<span class="sc" data-i="{i}" data-layout-allow-overflow><span class="rl">{reel}</span></span>'); i += 1
        rows.append(f'<div class="scl">{"".join(slots)}</div>')
    _clip(X, cid, t, d, f'<div class="big scr" style="font-family:var(--f-mono); font-size:{f.px}px">{"".join(rows)}</div>', p)
    X.css("aefx-sc", ".fx .scl { display:flex; justify-content:center; } .fx .sc { display:inline-block; height:1.1em; overflow:hidden; align-self:flex-start; contain:paint; } .fx .sc .rl { display:flex; flex-direction:column; } .fx .sc i { display:block; height:1.1em; font-style:normal; text-align:center; } .fx .sc .g { color:var(--accent); }")
    step = _st(d - 1.0, i, 0.07, 0.6)
    for j in range(i):
        X.tw(f'tl.fromTo("#{cid} .sc[data-i=\'{j}\'] .rl", {{yPercent:0}}, {{yPercent:{-100 * k / (k + 1):.3f}, duration:{0.5 + j * step:.2f}, ease:"steps({k})"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "type")


def write_on(X, cid, t, d, p):
    """描边书写 → 填色 (Trim Paths on text / 手写签名): glyph outlines draw on, then the fill floods in."""
    f = _fit(X, p.get("text", ""), max_lines=3, max_vmin=20)
    X.used_text.update("".join(f.lines))
    fs = 220; lh = 260
    vb_w = max(1000, int(f.em * fs * 1.06) + 60); vb_h = lh * f.n + 40
    texts = "".join(f'<text x="{vb_w // 2}" y="{215 + k * lh}" text-anchor="middle" style="font-family:var(--f-hand, var(--f-display));font-size:{fs}px;font-weight:var(--display-weight,800)">{X.rich(fit.plain(l))}</text>' for k, l in enumerate(f.lines))
    wpct = min(86, 78 * vb_w / 1000) if f.n == 1 else 86
    _clip(X, cid, t, d, f'<svg class="wo" viewBox="0 0 {vb_w} {vb_h}" preserveAspectRatio="xMidYMid meet" style="width:{wpct:.0f}%;max-height:64%;height:auto;overflow:visible">{texts}</svg>', p)
    X.css("aefx-wo", ".fx .wo text { fill:transparent; stroke:var(--fg); stroke-width:3; stroke-dasharray:1400; stroke-dashoffset:1400; paint-order:stroke; }")
    X.tw(f'tl.to("#{cid} .wo text", {{strokeDashoffset:0, duration:1.6, ease:"power1.inOut", stagger:0.2}}, {t + 0.1:.3f});')
    X.tw(f'tl.to("#{cid} .wo text", {{fill:"var(--fg)", strokeWidth:0, duration:0.5, ease:"power2.out"}}, {t + 1.5 + 0.2 * (f.n - 1):.3f});')
    X.sfx(t + 0.1, "brush")


def flip3d(X, cid, t, d, p):
    """逐字三维翻转 (3D Flip per character): rotateX from -100°, transform-origin bottom, perspective on the line."""
    big, f = _big(X, p, mode="chars", cls="big f3", style="perspective:900px")
    _clip(X, cid, t, d, big, p)
    X.tw(f'tl.from("#{cid} .f3 .c", {{rotationX:-100, opacity:0, transformOrigin:"50% 100% -20px", duration:0.7, ease:"back.out(1.5)", stagger:{_st(d, _nglyph(f), 0.05):.4f}}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "enter")


def slice_text(X, cid, t, d, p):
    """斜切分割 (Slice / Split text): the word is cut diagonally; the halves slide apart and snap back."""
    f = _fit(X, p.get("text", ""))
    s = _lines(X, f); fs = f"font-size:{f.px}px;"
    _clip(X, cid, t, d, f'<div class="sl" data-layout-allow-overlap style="position:relative"><div class="big a" style="{fs}clip-path:polygon(0 0,100% 0,100% 38%,0 62%)">{s}</div>'
                        f'<div class="big b" style="{fs}position:absolute;inset:0;clip-path:polygon(0 62%,100% 38%,100% 100%,0 100%)">{s}</div></div>', p)
    X.tw(f'tl.from("#{cid} .sl .a", {{xPercent:-60, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sl .b", {{xPercent:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.to("#{cid} .sl .a", {{xPercent:-4, yPercent:-4, duration:0.25, ease:"power2.out", yoyo:true, repeat:1}}, {t + 0.9:.3f});')
    X.tw(f'tl.to("#{cid} .sl .b", {{xPercent:4, yPercent:4, duration:0.25, ease:"power2.out", yoyo:true, repeat:1}}, {t + 0.9:.3f});')
    X.sfx(t + 0.1, "slam")


def shine(X, cid, t, d, p):
    """光泽扫过 (Shine / CC Light Sweep) on a title: a bright band travels across the glyphs once."""
    big, f = _big(X, p, cls="big sh")
    _clip(X, cid, t, d, big, p)
    X.css("aefx-sh", ".fx .sh { background:linear-gradient(110deg, var(--fg) 0%, var(--fg) 40%, #fff 50%, var(--fg) 60%, var(--fg) 100%); background-size:300% 100%; -webkit-background-clip:text; background-clip:text; color:transparent; }")
    X.tw(f'tl.from("#{cid} .sh", {{opacity:0, y:30, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("#{cid} .sh", {{backgroundPosition:"100% 0"}}, {{backgroundPosition:"0% 0", duration:1.1, ease:"power2.inOut"}}, {t + 0.6:.3f});')


def glitch(X, cid, t, d, p):
    """故障 RGB 分离 (Glitch / RGB split): red & cyan copies jitter on stepped frames, then lock."""
    f = _fit(X, p.get("text", ""))
    s = _lines(X, f); fs = f"font-size:{f.px}px;"
    _clip(X, cid, t, d, f'<div class="gl" data-layout-allow-overlap style="position:relative"><div class="big r" style="{fs}position:absolute;inset:0;color:#ff2a4d;mix-blend-mode:screen">{s}</div>'
                        f'<div class="big cy" style="{fs}position:absolute;inset:0;color:#24e0ff;mix-blend-mode:screen">{s}</div><div class="big m" style="{fs}">{s}</div></div>', p)
    for k in range(10):
        tt = t + 0.1 + k * 0.05
        a, b = X.rand.uniform(-14, 14), X.rand.uniform(-6, 6)
        X.tw(f'tl.set("#{cid} .r", {{x:{a:.0f}, y:{b:.0f}, clipPath:"inset({X.rand.randint(0, 60)}% 0 {X.rand.randint(0, 30)}% 0)"}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .cy", {{x:{-a:.0f}, y:{-b:.0f}, clipPath:"inset({X.rand.randint(0, 30)}% 0 {X.rand.randint(0, 60)}% 0)"}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .m", {{x:{X.rand.uniform(-6, 6):.0f}}}, {tt:.3f});')
    X.tw(f'tl.set("#{cid} .r, #{cid} .cy, #{cid} .m", {{x:0, y:0, clipPath:"inset(0 0 0 0)"}}, {t + 0.62:.3f});')
    X.sfx(t + 0.1, "glitch")


def ghost_type(X, cid, t, d, p):
    """巨型虚影背景字 (Ghost / outline background type): a huge outlined word drifts behind small foreground copy."""
    ghost = fit.plain(fit.as_text(p.get("ghost") or p.get("text", ""), " "))
    gpx = min(_vm(X, 52), X.W * 1.25 / max(fit.width(ghost), 1))
    big, f = _big(X, p, max_vmin=7, min_vmin=3.4, box=(0.78, 0.3))
    _clip(X, cid, t, d, f'<div class="gh" data-layout-allow-overlap data-layout-allow-overflow style="font-size:{gpx:.0f}px">{X.rich(ghost)}</div><div class="fg col">{big}{_sub(X, p)}</div>', p)
    X.css("aefx-gh", ".fx .gh { position:absolute; left:-5%; top:50%; transform:translateY(-50%); font-family:var(--f-display); font-weight:900; font-size:52vmin; line-height:1; color:color-mix(in srgb, var(--fg) 5%, transparent); -webkit-text-stroke:2px color-mix(in srgb, var(--fg) 24%, transparent); white-space:nowrap; } .fx .fg { position:relative; }")
    X.tw(f'tl.fromTo("#{cid} .gh", {{xPercent:6, opacity:0}}, {{xPercent:-8, opacity:1, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.set("#{cid} .gh", {{opacity:1}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("#{cid} .fg .big", {{y:40, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("#{cid} .fg .sub", {{opacity:0, duration:0.6}}, {t + 0.6:.3f});')


def lockup(X, cid, t, d, p):
    """中英双语锁定 + 注释引线 (type specimen lockup): headline, latin line, 0–4 leader-line annotations."""
    notes = [str(n) for n in fit.as_list(p.get("notes", ["字体 · 思源宋体", "Latin · EB Garamond"]))][:4]
    big, f = _big(X, p, box=(0.56 if not X.portrait else 0.84, 0.36), max_lines=2)
    an = "".join(f'<div class="an a{k + 1}" data-layout-allow-overflow><i></i><span>{X.rich(n)}</span></div>' for k, n in enumerate(notes))
    _clip(X, cid, t, d, f'<div class="lk">{big}{_sub(X, p)}{an}</div>', p)
    X.css("aefx-lk", ".fx .lk { position:relative; display:flex; flex-direction:column; align-items:center; } .fx .an { position:absolute; display:flex; align-items:center; gap:1vmin; font:400 1.7vmin var(--f-mono, monospace); color:var(--muted); white-space:nowrap; } .fx .an i { display:block; width:9vmin; height:1px; background:var(--muted); transform-origin:0 50%; }"
          " .fx .a1 { right:100%; top:18%; margin-right:2vmin; flex-direction:row-reverse; } .fx .a2 { left:100%; bottom:12%; margin-left:2vmin; } .fx .a3 { left:100%; top:18%; margin-left:2vmin; } .fx .a4 { right:100%; bottom:12%; margin-right:2vmin; flex-direction:row-reverse; }"
          " #root.v .fx .an { position:relative; left:auto; right:auto; top:auto; bottom:auto; margin:1.6vmin 0 0; flex-direction:row; font-size:2.2vmin; } #root.v .fx .an i { width:6vmin; }")
    X.tw(f'tl.from("#{cid} .lk .big", {{opacity:0, scale:0.92, duration:0.7, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .lk .sub", {{opacity:0, y:12, duration:0.5}}, {t + 0.45:.3f});')
    if notes:
        X.tw(f'tl.from("#{cid} .an i", {{scaleX:0, duration:0.5, ease:"power3.out", stagger:{_st(d, len(notes), 0.2, 0.3):.3f}}}, {t + 0.8:.3f});')
        X.tw(f'tl.from("#{cid} .an span", {{opacity:0, x:8, duration:0.4, stagger:{_st(d, len(notes), 0.2, 0.3):.3f}}}, {t + 1.1:.3f});')


def odometer(X, cid, t, d, p):
    """数字滚轮 (Odometer / number wheel): each digit column spins down to its value, staggered.
    value: 46479 | "46,479" | -3.5 | "97.5" | 1.2e9 (numbers get thousands separators; zh:true → 万/亿)."""
    v = p.get("value", 0)
    v = fit.fmt_num(v, zh=bool(p.get("zh"))) if isinstance(v, (int, float)) else str(v)
    unit = str(p.get("unit", ""))
    px = min(_vm(X, 15), X.W * 0.84 * 0.96 / max(fit.width(v) + 0.4 * fit.width(unit), 1), X.H * 0.42)
    cols, k = [], 0
    for ch in v:
        if ch.isdigit():
            seq = "".join(f"<i>{(int(ch) + j) % 10}</i>" for j in range(10, -1, -1))   # ends on ch
            cols.append(f'<span class="od" data-k="{k}" data-layout-allow-overflow><span class="rl">{seq}</span></span>'); k += 1
        else:
            cols.append(f'<span class="od0">{X.rich(ch)}</span>')
    X.used_text.update("0123456789,.-" + unit)
    _clip(X, cid, t, d, f'<div class="col"><div class="big odm" style="font-size:{px:.0f}px">{"".join(cols)}<small>{X.rich(unit)}</small></div>{_sub(X, p)}</div>', p)
    X.css("aefx-od", ".fx .odm { display:flex; align-items:flex-end; font-variant-numeric:tabular-nums; font-family:var(--f-num, var(--f-display)); } .fx .od { display:inline-block; height:1.05em; overflow:hidden; } .fx .od .rl { display:flex; flex-direction:column; } .fx .od i { display:block; height:1.05em; font-style:normal; } .fx .odm small { font-size:.4em; margin:0 0 .18em .08em; color:var(--accent); }")
    step = _st(d - 1.3, k, 0.25, 0.5)
    for j in range(k):
        X.tw(f'tl.fromTo("#{cid} .od[data-k=\'{j}\'] .rl", {{yPercent:0}}, {{yPercent:{-100 * 10 / 11:.3f}, duration:{1.2 + j * step:.2f}, ease:"power3.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, duration:0.5}}, {t + 0.8:.3f});')
    X.sfx(t + 0.1, "count")


# ------------------------------------------------------------------ shapes & backgrounds
def burst(X, cid, t, d, p):
    """形状元素爆发 (Shape Elements burst): radial lines + ring + dots fire as the word slams in."""
    lines = "".join(f'<i class="ray" style="transform:rotate({k * 30}deg)"><b></b></i>' for k in range(12))
    dots = "".join(f'<i class="dot" style="--a:{k * 45 + 22}deg"></i>' for k in range(8))
    big, f = _big(X, p, cls="big w0", box=(0.7, 0.34), max_lines=2)
    _clip(X, cid, t, d, f'<div class="bu"><div class="rays">{lines}</div><i class="ring"></i>{dots}{big}</div>', p)
    X.css("aefx-bu", ".fx .bu { position:relative; display:grid; place-items:center; } .fx .rays { position:absolute; width:60vmin; height:60vmin; } .fx .ray { position:absolute; left:50%; top:50%; width:0; height:0; } .fx .ray b { position:absolute; left:-0.4vmin; top:-30vmin; width:0.8vmin; height:7vmin; border-radius:1vmin; background:var(--accent); transform-origin:50% 30vmin; } .fx .ring { position:absolute; width:20vmin; height:20vmin; border-radius:50%; border:0.8vmin solid var(--accent); } .fx .dot { position:absolute; width:2vmin; height:2vmin; border-radius:50%; background:var(--fg); transform:rotate(var(--a)) translateY(-22vmin); } .fx .bu .big { position:relative; }")
    X.tw(f'tl.from("#{cid} .w0", {{scale:2.2, opacity:0, duration:0.35, ease:"power4.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("#{cid} .ray b", {{scaleY:0, y:"10vmin"}}, {{scaleY:1, y:"0vmin", duration:0.25, ease:"power2.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.to("#{cid} .ray b", {{scaleY:0, y:"-6vmin", duration:0.3, ease:"power2.in"}}, {t + 0.55:.3f});')
    X.tw(f'tl.fromTo("#{cid} .ring", {{scale:0.2, opacity:1}}, {{scale:2.6, opacity:0, duration:0.6, ease:"power2.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("#{cid} .dot", {{opacity:0}}, {{opacity:1, duration:0.05}}, {t + 0.32:.3f});')
    X.tw(f'tl.to("#{cid} .dot", {{scale:0, duration:0.5, ease:"power2.in"}}, {t + 0.4:.3f});')
    X.sfx(t + 0.1, "slam")


def diffuse(X, cid, t, d, p):
    """弥散光 (diffuse gradient blobs): 1–5 soft colour blobs orbit slowly behind a calm title."""
    cols = [str(c) for c in fit.as_list(p.get("colors", ["#ff6ad5", "#7d6bff", "#ffb36b"]))][:5] or ["#7d6bff"]
    blobs = "".join(f'<i class="bl" style="background:{c}"></i>' for c in cols)
    big, f = _big(X, p, max_lines=3)
    _clip(X, cid, t, d, f'<div class="dfw">{blobs}</div><div class="col" style="position:relative">{big}{_sub(X, p)}</div>', p)
    X.css("aefx-df", ".fx .dfw { position:absolute; inset:0; filter:blur(9vmin); } .fx .bl { position:absolute; display:block; width:46vmin; height:46vmin; border-radius:50%; left:50%; top:50%; margin:-23vmin; opacity:.85; }")
    for i in range(len(cols)):
        a0 = i * 2.1
        pts = [(math.cos(a0 + k * 0.9) * 18, math.sin(a0 + k * 1.1) * 12) for k in range(4)]
        X.tw(f'tl.set("#{cid} .bl:nth-child({i + 1})", {{x:"{pts[0][0]:.1f}vmin", y:"{pts[0][1]:.1f}vmin"}}, {t:.3f});')
        for k in range(1, 4):
            X.tw(f'tl.to("#{cid} .bl:nth-child({i + 1})", {{x:"{pts[k][0]:.1f}vmin", y:"{pts[k][1]:.1f}vmin", duration:{d / 3:.2f}, ease:"sine.inOut"}}, {t + (k - 1) * d / 3:.3f});')
    X.tw(f'tl.from("#{cid} .dfw", {{opacity:0, duration:1.0}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .big", {{opacity:0, filter:"blur(12px)", duration:1.0, ease:"power2.out"}}, {t + 0.3:.3f});')


def gooey(X, cid, t, d, p):
    """粘性碰撞 (gooey metaballs): two balls approach, merge with a liquid neck, bounce apart; squash & stretch.
    labels: optional [左, 右] — two words that ride under the balls (e.g. 流量 / 供应链)."""
    lab = [str(x) for x in fit.as_list(p.get("labels"))][:2]
    lpx = 0
    if lab:
        lpx = min(_vm(X, 4.4), _vm(X, 30) / max(max(fit.width(x) for x in lab), 1))
    labs = "".join(f'<b class="gl{k + 1}" style="font-size:{lpx:.0f}px">{X.rich(x)}</b>' for k, x in enumerate(lab))
    _clip(X, cid, t, d, '<svg width="0" height="0" style="position:absolute"><filter id="goo-%s"><feGaussianBlur in="SourceGraphic" stdDeviation="18"/><feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 28 -12"/></filter></svg>'
          '<div class="gw"><div class="go" style="filter:url(#goo-%s)"><i class="b1"></i><i class="b2"></i></div><div class="gol">%s</div></div>' % (cid, cid, labs), p)
    X.css("aefx-go", ".fx .gw { position:relative; width:80vmin; height:40vmin; } .fx .go { position:absolute; inset:0; } .fx .go i { position:absolute; top:50%; width:16vmin; height:16vmin; margin-top:-8vmin; border-radius:50%; background:var(--accent); } .fx .b1 { left:10%; } .fx .b2 { right:10%; background:var(--fg) !important; }"
          " .fx .gol b { position:absolute; top:calc(50% + 10vmin); width:30vmin; text-align:center; font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; } .fx .gl1 { left:calc(10% + 8vmin - 15vmin); } .fx .gl2 { right:calc(10% + 8vmin - 15vmin); }")
    X.tw(f'tl.to("#{cid} .b1, #{cid} .gl1", {{x:"22vmin", duration:0.7, ease:"power2.in"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .b2, #{cid} .gl2", {{x:"-22vmin", duration:0.7, ease:"power2.in"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .go i", {{scaleX:1.25, scaleY:0.8, duration:0.12, yoyo:true, repeat:1}}, {t + 0.85:.3f});')
    X.tw(f'tl.to("#{cid} .b1, #{cid} .gl1", {{x:"-4vmin", duration:0.9, ease:"elastic.out(1,0.45)"}}, {t + 1.1:.3f});')
    X.tw(f'tl.to("#{cid} .b2, #{cid} .gl2", {{x:"4vmin", duration:0.9, ease:"elastic.out(1,0.45)"}}, {t + 1.1:.3f});')
    if lab: X.tw(f'tl.from("#{cid} .gol b", {{opacity:0, y:12, duration:0.4, stagger:0.1}}, {t + 0.1:.3f});')
    X.sfx(t + 0.85, "boing")


def callout(X, cid, t, d, p):
    """标注引线 (Callout title): a dot pops on the subject, the leader line draws out, the label slides along it.
    image | video (+focus) as the ground; one point (x, y, text, sub) or points: [{x, y, text, sub}, …] up to 4.
    Labels turn left when the point is on the right third, and drop below when it is near the top."""
    src = p.get("video") or p.get("image")
    mh, sel = fit.media(X, cid, "cimg", src, t, d, "cimg", focus=p.get("focus"), z=1, fill="cover") if src else ("", None)   # points are frame coordinates
    pts = p.get("points") or [{"x": p.get("x", 40), "y": p.get("y", 55), "text": p.get("text", ""), "sub": p.get("sub", "")}]
    pts = [q if isinstance(q, dict) else {"text": str(q)} for q in fit.as_list(pts)][:4]
    html = []
    for k, q in enumerate(pts):
        x, y = float(q.get("x", 30 + 40 * k / max(len(pts) - 1, 1))), float(q.get("y", 50))
        left, down = x > 58, y < 30
        rot = (28 if down else -28) if not left else (180 - 28 if down else 180 + 28)
        lpx = min(_vm(X, 4.4), X.W * 0.3 / max(fit.width(q.get("text", "")), 1))
        lbx = "right:19vmin;" if left else "left:19vmin;"
        lby = "top:9vmin;" if down else "top:-13vmin;"
        al = "align-items:flex-end;" if left else ""
        html.append(f'<div class="co" data-k="{k}" style="left:{x}%;top:{y}%"><i class="dt"></i><i class="ld" style="transform:rotate({rot}deg)"></i>'
                    f'<div class="lb" style="{lbx}{lby}{al}"><b style="font-size:{lpx:.0f}px">{X.rich(q.get("text", ""))}</b><span>{X.rich(q.get("sub", ""))}</span></div></div>')
    _clip(X, cid, t, d, mh + "".join(html), p, transparent=bool(src) and fit.is_video(src))
    X.css("aefx-co", ".fx .cimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .co { position:absolute; } .fx .dt { position:absolute; width:2.2vmin; height:2.2vmin; margin:-1.1vmin; border-radius:50%; background:var(--accent); box-shadow:0 0 0 0.8vmin color-mix(in srgb, var(--accent) 35%, transparent); } .fx .ld { position:absolute; left:0; top:0; width:22vmin; height:2px; background:var(--fg); transform-origin:0 50%; transform:rotate(-28deg); } .fx .lb { position:absolute; left:19vmin; top:-13vmin; white-space:nowrap; display:flex; flex-direction:column; gap:.6vmin; } .fx .lb b { font:800 4.4vmin var(--f-display); color:var(--fg); background:color-mix(in srgb, var(--bg) 70%, transparent); padding:.4vmin 1.4vmin; } .fx .lb span { font:500 1.8vmin var(--f-mono, monospace); color:var(--fg); letter-spacing:.14em; padding-left:1.4vmin; }")
    for k in range(len(pts)):
        tk = t + 0.3 + k * _st(d - 1.4, len(pts), 0.5, 0.6)
        q = f'#{cid} .co[data-k=\'{k}\']'
        X.tw(f'tl.from("{q} .dt", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {tk:.3f});')
        X.tw(f'tl.from("{q} .ld", {{scaleX:0, duration:0.45, ease:"power3.out"}}, {tk + 0.25:.3f});')
        X.tw(f'tl.from("{q} .lb b", {{clipPath:"inset(0 100% 0 0)", duration:0.5, ease:"power3.out"}}, {tk + 0.6:.3f});')
        X.tw(f'tl.from("{q} .lb span", {{opacity:0, x:-10, duration:0.4}}, {tk + 0.9:.3f});')
        X.sfx(tk, "pop")
    if sel: X.camera(sel, t, d, "push")


TRI_ICONS = ['<path d="M7 22V11l5-8a2 2 0 0 1 3 2l-1 6h6a2 2 0 0 1 2 2l-2 7a2 2 0 0 1-2 2H7zM3 11h4v11H3z"/>',
             '<circle cx="12" cy="12" r="9"/><path d="M8 9h8M9 12h6M12 9v9"/>',
             '<path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.2L12 17.4 6.5 20.3l1-6.2L3 9.7l6.2-.9z"/>',
             '<path d="M14 4l7 7-7 7M21 11H9a6 6 0 0 0-6 6v3"/>',
             '<path d="M4 5h16v11H9l-5 4z"/>']


def triple(X, cid, t, d, p):
    """三连 (like · coin · favourite …): 1–5 icons pop in sequence, each with a ring burst; the B站/抖音 staple ending.
    labels: list of 1–5 (icons in order: 点赞 投币 收藏 转发 评论); icons: optional indices into that set."""
    lbl = [str(x) for x in fit.as_list(p.get("labels", ["点赞", "投币", "收藏"]))][:5] or ["点赞"]
    idx = [int(i) % len(TRI_ICONS) for i in fit.as_list(p.get("icons"))] or list(range(len(lbl)))
    n = len(lbl)
    avail = (X.W - 2 * SAFE_R - _vm(X, 6)) if X.portrait else X.W * 0.7      # 9:16: labels stay clear of the right-hand buttons
    isz = min(12.0, avail / _vm(X, 1) / (n * 1.9))          # icon size in vmin
    gap = min(12.0, (avail / _vm(X, 1) - n * isz) / max(n - 1, 1))
    lpx = min(_vm(X, 2.6), _vm(X, isz * 1.6) / max(max(fit.width(l) for l in lbl), 1))
    items = "".join(f'<div class="ti"><i class="rg"></i><svg viewBox="0 0 24 24">{TRI_ICONS[idx[k % len(idx)]]}</svg><span style="font-size:{lpx:.0f}px">{X.rich(l)}</span></div>' for k, l in enumerate(lbl))
    _clip(X, cid, t, d, f'<div class="tri" style="gap:{gap:.1f}vmin; --isz:{isz:.1f}vmin">{items}</div>', p)
    X.css("aefx-tri", ".fx .tri { display:flex; gap:12vmin; } .fx .ti { position:relative; display:flex; flex-direction:column; align-items:center; gap:2vmin; } .fx .ti svg { width:var(--isz, 12vmin); height:var(--isz, 12vmin); fill:none; stroke:var(--fg); stroke-width:1.6; stroke-linejoin:round; } .fx .ti span { font:600 2.6vmin var(--f-body); color:var(--fg); letter-spacing:.2em; white-space:nowrap; } .fx .ti .rg { position:absolute; top:calc(var(--isz, 12vmin) / 2); left:50%; width:var(--isz, 12vmin); height:var(--isz, 12vmin); margin:calc(var(--isz, 12vmin) / -2); border-radius:50%; border:0.6vmin solid var(--accent); opacity:0; }")
    each = _st(d - 0.8, n, 0.35, 0.6)
    for k in range(n):
        tk = t + 0.2 + k * each
        X.tw(f'tl.from("#{cid} .ti:nth-child({k + 1}) svg", {{scale:0, rotation:-25, duration:0.45, ease:"back.out(3)"}}, {tk:.3f});')
        X.tw(f'tl.to("#{cid} .ti:nth-child({k + 1}) svg", {{fill:"var(--accent)", stroke:"var(--accent)", duration:0.2}}, {tk + 0.25:.3f});')
        X.tw(f'tl.fromTo("#{cid} .ti:nth-child({k + 1}) .rg", {{scale:0.4, opacity:1}}, {{scale:1.9, opacity:0, duration:0.5, ease:"power2.out"}}, {tk + 0.25:.3f});')
        X.tw(f'tl.from("#{cid} .ti:nth-child({k + 1}) span", {{opacity:0, y:10, duration:0.3}}, {tk + 0.2:.3f});')
        X.sfx(tk + 0.25, "pop")


def plate(X, cid, t, d, p):
    """整屏图版 (full-bleed plate with a slow push) — image | video (+focus); used to show transitions between frames."""
    src = p.get("video") or p.get("image")
    mh, sel = fit.media(X, cid, "pl", src, t, d, "pl", focus=p.get("focus"), z=1)
    big = ""
    if p.get("text"):
        f = _fit(X, p["text"], max_vmin=9, min_vmin=4, box=(0.8, 0.4))
        big = f'<div class="plt" style="font-size:{f.px}px">{_lines(X, f)}</div>'
    _clip(X, cid, t, d, mh + big, p, transparent=fit.is_video(src))
    X.css("aefx-pl", ".fx .pl { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .plt { position:relative; font:800 9vmin var(--f-display); color:#fff; text-shadow:0 6px 40px rgba(0,0,0,.6); text-align:center; line-height:1.1; }")
    if sel: X.camera(sel, t, d, "push")


# ------------------------------------------------------------------ round 2: the remaining top-ranked effects (references/ae_popular.md)
def parallax(X, cid, t, d, p):
    """2.5D 照片视差 (#2, VoluMax/Photomotion; MDMZ 1171万播放): clean plate + cut-out subject on separate depths,
    the camera dollies in so the subject separates from the background; optional title sits BETWEEN the layers.
    plate | image | video as the ground (+focus); fg optional (a transparent PNG cut-out)."""
    src = p.get("video") or p.get("plate") or p.get("image")
    mh, sel = fit.media(X, cid, "pxb", src, t, d, "pxb", focus=p.get("focus"), z=1, fill="cover" if p.get("fg") else "auto")
    title = ""
    if p.get("text"):
        f = _fit(X, p["text"], max_vmin=(14 if X.portrait else 22), min_vmin=5, box=(0.92, 0.3), max_lines=2, lh=1.0)
        title = f'<div class="pxt" style="font-size:{f.px}px">{_lines(X, f)}</div>'
    fg = f'<img class="pxf" src="{X.asset(p["fg"])}" alt="" style="object-position:{fit.focus_css(p.get("focus"))}">' if p.get("fg") else ""
    _clip(X, cid, t, d, f'{mh}{title}{fg}', p, transparent=fit.is_video(src))
    X.css("aefx-px", ".fx .pxb, .fx .pxf { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } #root.v .fx .pxt { top:14%; } .fx .pxt { position:absolute; left:0; right:0; top:9%; text-align:center; font:900 22vmin/1 var(--f-display); color:#fff; letter-spacing:-.02em; opacity:.92; }")
    if sel: X.tw(f'tl.fromTo("{sel}", {{scale:1.12, xPercent:1.5}}, {{scale:1.18, xPercent:-1.5, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    if fg: X.tw(f'tl.fromTo("#{cid} .pxf", {{scale:1.0, xPercent:-1}}, {{scale:1.16, xPercent:2.5, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    if title:
        X.tw(f'tl.fromTo("#{cid} .pxt", {{scale:1.0, yPercent:10, opacity:0}}, {{scale:1.07, yPercent:0, opacity:.92, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


def stomp(X, cid, t, d, p):
    """重拍排版 Stomp (#4, TypoKing 1.34万份; B站动态歌词排版 898万): one word per beat slams full-frame,
    sizes alternate, every third beat inverts the frame; a 2-frame jolt on each hit.
    words: 1–12 (a list, "a|b|c", or just text → split into words). Long words wrap to two lines.
    With narration timestamps each word lands the moment it is spoken (like lyric typography)."""
    words = [str(w) for w in fit.as_list(p.get("words"))] or [w for w in fit.tokens(fit.plain(p.get("text", ""))) if w.strip()][:12] or ["—"]
    words = words[:12]
    beat = p.get("beat", min(0.42, (d - 0.3) / max(len(words), 1)))
    times, after = [], t
    for i, w in enumerate(words):
        tt = None
        if X.chars:
            try: tt = float(X.T("@" + fit.plain(w).replace(" ", ""), after))
            except SystemExit: tt = None
        if tt is None or tt > t + d - 0.2: tt = (times[-1] + beat) if times else t + 0.1
        tt = max(tt - 2 / X.fps, (times[-1] + 0.12) if times else t)
        times.append(tt); after = tt + 0.05
    base = {0: 24, 1: 34, 2: 16}
    items = []
    for i, w in enumerate(words):
        f = _fit(X, w, box=(0.86, 0.62), max_vmin=base[i % 3], min_vmin=6, max_lines=2, lh=0.98)
        items.append(f'<div class="sw s{i % 3}" data-i="{i}" style="font-size:{f.px}px">{_lines(X, f)}</div>')
    _clip(X, cid, t, d, f'<div class="sbg"></div>{"".join(items)}', p)
    X.css("aefx-st", ".fx .sbg { position:absolute; inset:0; background:var(--bg); } .fx .sw { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:var(--f-display); font-weight:900; line-height:.95; color:var(--fg); opacity:0; text-align:center; white-space:nowrap; } .fx .sw.s2 { color:var(--bg); }")
    for i, tt in enumerate(times):
        inv = i % 3 == 2
        X.tw(f'tl.set("#{cid} .sw", {{opacity:0}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .sbg", {{background:"{ "var(--accent)" if inv else "var(--bg)"}"}}, {tt:.3f});')
        X.tw(f'tl.fromTo("#{cid} .sw[data-i=\'{i}\']", {{opacity:1, scale:1.5}}, {{scale:1, duration:0.16, ease:"power4.out"}}, {tt:.3f});')
        X.tw(f'tl.fromTo("#{cid} > .stage", {{x:{X.rand.choice([-14, 14])}, y:{X.rand.choice([-8, 8])}}}, {{x:0, y:0, duration:0.1, ease:"steps(2)"}}, {tt:.3f});')
        X.sfx(tt, "slam" if i % 2 == 0 else "pop")
    # an inverted last hit stays inverted to the end of the beat (its word is drawn in the background colour)
    if len(times) % 3 != 0:
        X.tw(f'tl.set("#{cid} .sbg", {{background:"var(--bg)"}}, {times[-1] + 0.5:.3f});')


def mosaic(X, cid, t, d, p):
    """照片墙拼合 (#6, Mosaic Photo Reveal 1.6万份): tiles fly in from depth and assemble a wall, then the camera
    pushes into one tile until it fills the frame. images: 1…24 of any aspect (fewer than 12 → varied crops;
    12–24 → one tile each, the grid re-shapes to the count); clips may be mixed in (up to 6 play, the rest show a still)."""
    srcs = [s for s in fit.as_list(p.get("images")) if s] or [p.get("image") or p.get("video")]
    srcs = [s for s in srcs if s]
    m = min(24, max(12, len(srcs)))
    import sys; M = sys.modules.get("h9fx__media")                 # clips play in up to 6 tiles (see fx/_media.py)
    play = [k for k in range(m) if srcs and fit.is_video(srcs[k % len(srcs)])][:6] if M else []
    R = f"#{cid}_st" if play else f"#{cid}"
    r = X.rand
    bw, bh, ar = (X.W * 0.84, X.H * 0.63, 1.0) if X.portrait else (X.W * 0.86, X.H * 0.86, 4 / 3)
    gap = _vm(X, 1.4)
    cols, rows = fit.grid(m, bw, bh, item_ar=ar, gap=gap)
    tw_ = min((bw - gap * (cols - 1)) / cols, ((bh - gap * (rows - 1)) / rows) * ar)
    th_ = tw_ / ar
    ww, wh = cols * tw_ + gap * (cols - 1), rows * th_ + gap * (rows - 1)
    tiles = []
    for k in range(m):
        if srcs:
            src = srcs[k % len(srcs)]
            if k in play:
                tiles.append(f'<i class="mt mtv">{M.vtile(X, src, t, d, p.get("focus"), start=k * 1.3)}</i>'); continue
            u = M.poster(X, src)[0] if (M and fit.is_video(src)) else X.asset(src)
            bg = (f"url({u}) {fit.focus_css(p.get('focus'))}/cover" if len(srcs) > 12
                  else f"url({u}) {r.randint(0, 100)}% {r.randint(0, 100)}%/{r.randint(180, 320)}% auto")
        else:
            bg = f"hsl({(k * 37) % 360} 30% {30 + (k * 7) % 30}%)"
        tiles.append(f'<i class="mt" style="background:{bg}"></i>')
    wall = f'<div class="mw" style="grid-template-columns:repeat({cols}, 1fr); grid-auto-rows:{th_:.1f}px; width:{ww:.0f}px; height:{wh:.0f}px">{"".join(tiles)}</div>'
    if play:
        _clip(X, cid, t, d, "", p)
        M.stage(X, cid, t, d, f'<div class="stage">{wall}</div>', _theme_style(p, paint=False))
    else:
        _clip(X, cid, t, d, wall, p)
    X.css("aefx-mo", ".fx .mw { display:grid; gap:1.4vmin; } .fx .mt { display:block; border-radius:.8vmin; box-shadow:0 1vmin 3vmin rgba(0,0,0,.45); } .fx .mt.mtv { position:relative; overflow:hidden; }")
    rots = [r.randint(-25, 25) for _ in range(m)]
    rank = fit.seeded_order(m, r)
    X.tw(f'tl.from("{R} .mt", {{opacity:0, scale:0.2, z:-400, rotation:(i)=>[{",".join(map(str, rots))}][i], duration:0.7, ease:"back.out(1.4)", stagger:(i)=>[{",".join(map(str, rank))}][i]*{_st(d - 1.6, m, 0.05, 0.5):.3f}}}, {t + 0.05:.3f});')
    tk = (rows // 2) * cols + min(cols - 1, cols // 2 + 1) if m > 2 else 0          # a tile right of centre
    rr, cc = divmod(tk, cols)
    ox = (cc * (tw_ + gap) + tw_ / 2) / ww * 100; oy = (rr * (th_ + gap) + th_ / 2) / wh * 100
    sc = max(X.W / tw_, X.H / th_) * 1.08
    X.tw(f'tl.to("{R} .mw", {{scale:{sc:.2f}, transformOrigin:"{ox:.1f}% {oy:.1f}%", duration:0.9, ease:"power3.inOut"}}, {t + d - 1.1:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")


def cartoon(X, cid, t, d, p):
    """卡通冲击特效 (#7, 140 Flash FX 1.47万份): speed lines, a jagged impact star, smoke puffs — on twos (12 fps steps)."""
    lines = "".join(f'<line x1="{500 + 120 * math.cos(a):.0f}" y1="{500 + 120 * math.sin(a):.0f}" x2="{500 + 700 * math.cos(a):.0f}" y2="{500 + 700 * math.sin(a):.0f}" />'
                    for a in [2 * math.pi * k / 28 + X.rand.uniform(-.05, .05) for k in range(28)])
    star = " ".join(f"{500 + (300 if k % 2 == 0 else 150) * math.cos(math.pi * k / 9):.0f},{500 + (300 if k % 2 == 0 else 150) * math.sin(math.pi * k / 9):.0f}" for k in range(18))
    puffs = "".join(f'<circle class="pf" cx="{500 + 260 * math.cos(a):.0f}" cy="{500 + 260 * math.sin(a):.0f}" r="70"/>' for a in [k * 1.05 for k in range(6)])
    txt = fit.plain(fit.as_text(p.get("text", "啪！"), " ")) or "啪！"
    f = fit.fit_text(txt, 760, 420, 170, 70, lh=1.0, max_lines=2)
    y0 = 560 - (f.n - 1) * f.px * 0.5
    spans = "".join(f'<tspan x="500" y="{y0 + k * f.px:.0f}">{X.rich(l)}</tspan>' for k, l in enumerate(f.lines))
    _clip(X, cid, t, d, f'<svg class="ct" viewBox="0 0 1000 1000"><g class="spd">{lines}</g>{puffs}<polygon class="star" points="{star}"/>'
                        f'<text text-anchor="middle" class="pow" style="font-size:{f.px}px">{spans}</text></svg>', p)
    X.css("aefx-ct", ".fx .ct { width:80vmin; height:80vmin; overflow:visible; } .fx .spd line { stroke:var(--fg); stroke-width:6; stroke-linecap:round; } .fx .star { fill:var(--accent); stroke:var(--fg); stroke-width:10; stroke-linejoin:round; } .fx .pf { fill:var(--fg); opacity:.9; } .fx .pow { font-family:var(--f-display); font-weight:900; font-size:170px; fill:var(--fg); stroke:#000; stroke-width:8; paint-order:stroke; }")
    X.tw(f'tl.from("#{cid} .star", {{scale:0, rotation:-30, transformOrigin:"50% 50%", duration:0.25, ease:"steps(3)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .pow", {{scale:2.2, transformOrigin:"50% 50%", duration:0.2, ease:"steps(3)"}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("#{cid} .spd", {{scale:0.6, opacity:1, transformOrigin:"50% 50%"}}, {{scale:1.3, opacity:0, duration:0.5, ease:"steps(6)"}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("#{cid} .pf", {{scale:0.2, transformOrigin:"50% 50%"}}, {{scale:1.4, opacity:0, duration:0.66, ease:"steps(8)", stagger:0.03}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .star", {{rotation:6, duration:0.17, ease:"steps(2)", yoyo:true, repeat:{max(1, int((d - 0.6) / 0.17))}}}, {t + 0.4:.3f});')
    X.sfx(t + 0.1, "slam")


def apple_blur(X, cid, t, d, p):
    """苹果式逐字模糊渐显 (#9, 206.8万 2025): each glyph fades up out of a soft blur and a small rise, grey→white."""
    big, f = _big(X, p, mode="chars", cls="big ab")
    _clip(X, cid, t, d, f'<div class="col">{big}{_sub(X, p)}</div>', p)
    X.tw(f'tl.from("#{cid} .ab .c", {{opacity:0, filter:"blur(12px)", y:"0.18em", color:"#6e6e73", duration:0.7, ease:"power2.out", stagger:{_st(d, _nglyph(f), 0.045):.4f}}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, filter:"blur(6px)", duration:0.7}}, {t + 0.7:.3f});')


def portal(X, cid, t, d, p):
    """瞳孔穿梭 / 穿洞推进 (#10, B站364.5万 2025): a hole opens on a point of frame A showing frame B,
    then the camera dives through the hole until B fills the screen. image|video and image2|video2 (+focus, focus2)."""
    x, y = p.get("x", 50), p.get("y", 50)
    a_src, b_src = p.get("video") or p.get("image"), p.get("video2") or p.get("image2")
    ha, sa = fit.media(X, cid, "pa", a_src, t, d, "pa", focus=p.get("focus"), z=1, fill="cover")      # the hole is a frame coordinate
    hb, sb = fit.media(X, cid, "pb", b_src, t, d, "pb", focus=p.get("focus2"), z=2, fill="cover", extra_style=f"clip-path:circle(0% at {x}% {y}%)")
    _clip(X, cid, t, d, f'{ha}{hb}<div class="pt" style="transform-origin:{x}% {y}%"><i class="ring" style="left:{x}%;top:{y}%"></i></div>', p,
          transparent=fit.is_video(a_src) or fit.is_video(b_src))
    X.css("aefx-pt", ".fx .pt { position:absolute; inset:0; } .fx .pa, .fx .pb { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .pt .ring { position:absolute; width:2vmin; height:2vmin; margin:-1vmin; border-radius:50%; box-shadow:0 0 0 .5vmin #fff, 0 0 4vmin 1vmin rgba(255,255,255,.6); opacity:0; }")
    layers = ", ".join(s for s in (sa, sb, f"#{cid} .pt") if s)
    t1 = t + 0.5
    X.tw(f'tl.set("{layers}", {{transformOrigin:"{x}% {y}%"}}, {t:.3f});')
    X.tw(f'tl.to("#{cid} .pt .ring", {{opacity:1, scale:4, duration:0.4, ease:"power2.out"}}, {t1 - 0.2:.3f});')
    if sb:
        X.tw(f'tl.fromTo("{sb}", {{clipPath:"circle(0% at {x}% {y}%)"}}, {{clipPath:"circle(5% at {x}% {y}%)", duration:0.4, ease:"power2.out"}}, {t1:.3f});')
        X.tw(f'tl.to("{sb}", {{clipPath:"circle(150% at {x}% {y}%)", duration:1.0, ease:"power3.in"}}, {t1 + 0.4:.3f});')
    X.tw(f'tl.to("{layers}", {{scale:14, duration:1.0, ease:"power3.in"}}, {t1 + 0.4:.3f});')
    X.tw(f'tl.to("#{cid} .pt .ring", {{opacity:0, duration:0.3}}, {t1 + 0.6:.3f});')
    X.tw(f'tl.set("{layers}", {{scale:1}}, {t1 + 1.4:.3f});')
    if sa: X.tw(f'tl.set("{sa}", {{opacity:0}}, {t1 + 1.4:.3f});')
    if sb:
        X.tw(f'tl.set("{sb}", {{clipPath:"none"}}, {t1 + 1.4:.3f});')
        X.tw(f'tl.from("{sb}", {{scale:1.15, duration:0.6, ease:"power2.out", immediateRender:false}}, {t1 + 1.4:.3f});')
    X.sfx(t1 + 0.3, "whoosh_deep")


def neon(X, cid, t, d, p):
    """霓虹点亮 (#12, Neon Sign Kit 1万份): tube text stutters on (stepped flicker pattern), then holds with a steady glow."""
    big, f = _big(X, p, cls="big ne", box=(0.84, 0.44))
    _clip(X, cid, t, d, big, p)
    col = p.get("color", "#ff4fd8")
    X.css("aefx-ne", f".fx .ne {{ color:#fff3fd; font-weight:400; text-shadow:0 0 .04em #fff, 0 0 .12em {col}, 0 0 .3em {col}, 0 0 .6em {col}; }}")
    pat = [0, 1, 0, 0.2, 1, 0, 1, 0.5, 1]
    for k, o in enumerate(pat):
        X.tw(f'tl.set("#{cid} .ne", {{opacity:{o}}}, {t + 0.1 + k * 0.07:.3f});')
    X.tw(f'tl.set("#{cid} .ne", {{opacity:0.35}}, {t + 1.4:.3f});')
    X.tw(f'tl.set("#{cid} .ne", {{opacity:1}}, {t + 1.47:.3f});')
    X.sfx(t + 0.1, "glitch")


def notify(X, cid, t, d, p):
    """手机通知界面 (#13, Envato Elements「Elements」热门第1): iOS-style banners drop in one after another and stack.
    items: 1–6 of "应用：消息" | [应用, 消息] | {app, text}; long messages wrap to two lines; the stack scales to fit."""
    items = fit.as_pairs(p.get("items")) or [("小红书", "有人收藏了你的笔记"), ("抖音", "你的视频播放量破 10 万"), ("B站", "新增 128 个粉丝")]
    items = items[:6]
    n = len(items)
    ctx_v = X.portrait and p.get("line")                     # 9:16 with a caption at 1330 px: keep the stack inside 260–1300
    avail = 1000 if ctx_v else X.H * (0.56 if X.portrait else 0.66)
    need = n * _vm(X, 12.6)
    ns = min(1.0, avail / need)
    lift = max(0.0, (X.H / 2 + need * ns / 2) - 1300) if ctx_v else 0.0
    cards = "".join(f'<div class="nt"><i class="ic">{X.rich((a or "·")[:1])}</i><div class="tx"><b>{X.rich(a)}</b><span>{X.rich(b)}</span></div><em>现在</em></div>' for a, b in items)
    _clip(X, cid, t, d, f'<div class="nst" style="--ns:{ns:.3f};{f"margin-bottom:{2 * lift:.0f}px" if lift else ""}">{cards}</div>', p)
    X.css("aefx-nt", ".fx .nst { display:flex; flex-direction:column; gap:calc(var(--ns, 1) * 1.6vmin); width:min(80vmin, 92%); } .fx .nt { display:flex; align-items:center; gap:2vmin; padding:calc(var(--ns, 1) * 2vmin) 2.4vmin; border-radius:3vmin; background:rgba(245,245,247,.82); backdrop-filter:blur(20px); box-shadow:0 2vmin 5vmin rgba(0,0,0,.35); color:#111; }"
          " .fx .nt .ic { width:calc(var(--ns, 1) * 7vmin); height:calc(var(--ns, 1) * 7vmin); border-radius:1.8vmin; background:var(--accent); color:#fff; display:grid; place-items:center; font:800 calc(var(--ns, 1) * 3.4vmin) var(--f-body); flex:none; } .fx .nt .tx { display:flex; flex-direction:column; gap:.4vmin; flex:1; min-width:0; }"
          " .fx .nt b { font:700 calc(var(--ns, 1) * 2.8vmin) var(--f-body); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; } .fx .nt span { font:400 calc(var(--ns, 1) * 2.5vmin)/1.3 var(--f-body); color:#333; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; } .fx .nt em { font:400 calc(var(--ns, 1) * 2vmin) var(--f-body); color:#777; align-self:flex-start; flex:none; }")
    each = _st(d - 0.9, n, 0.45, 0.7)
    X.tw(f'tl.from("#{cid} .nt", {{y:"-40vmin", opacity:0, scale:0.92, duration:0.6, ease:"back.out(1.3)", stagger:{each:.3f}}}, {t + 0.15:.3f});')
    for k in range(n): X.sfx(t + 0.15 + k * each, "pop")


def lower3(X, cid, t, d, p):
    """下三分之一字条 (#14, Lower Thirds 第1名 6.3K): accent bar grows, name slides out of a mask, role follows."""
    nf = _fit(X, p.get("text", ""), box=(0.7, 0.14), max_vmin=7, min_vmin=3.6, max_lines=1)
    rf = _fit(X, p.get("sub", ""), box=(0.7, 0.08), max_vmin=2.6, min_vmin=1.8, max_lines=2, ls=0.18) if p.get("sub") else None
    role = f'<div class="rl"><span style="font-size:{rf.px}px">{_lines(X, rf)}</span></div>' if rf else ""
    lift = max(0, _cap_clear(X, p) - _vm(X, 14))             # clear a two-line caption
    _clip(X, cid, t, d, f'<div class="l3" style="margin-bottom:{lift:.0f}px"><i class="bar"></i><div class="nm"><span style="font-size:{nf.px}px">{_lines(X, nf)}</span></div>{role}</div>', p, "fx-l3")
    X.css("aefx-l3", ".fx-l3 > .stage { align-items:flex-end !important; justify-content:flex-start !important; padding:0 0 14vmin 10vmin; } #root.v .fx-l3 > .stage { padding:0 0 620px 10vmin; } .fx .l3 { position:relative; padding-left:3vmin; max-width:80%; } .fx .l3 .bar { position:absolute; left:0; top:0; bottom:0; width:.9vmin; background:var(--accent); transform-origin:50% 100%; } .fx .l3 .nm, .fx .l3 .rl { overflow:hidden; } .fx .l3 .nm span { display:block; font:800 7vmin var(--f-display); color:var(--fg); white-space:nowrap; } .fx .l3 .rl span { display:block; font:500 2.6vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.18em; margin-top:1vmin; line-height:1.4; }")
    X.tw(f'tl.from("#{cid} .l3 .bar", {{scaleY:0, duration:0.4, ease:"power3.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .l3 .nm span", {{xPercent:-105, duration:0.6, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("#{cid} .l3 .rl span", {{yPercent:110, duration:0.5, ease:"expo.out"}}, {t + 0.55:.3f});')


def collage(X, cid, t, d, p):
    """拼贴剪纸 (#21, Fakeplastictree Collage 203.5万): torn-edge photo pieces land on paper on twos, tape, a hand-drawn arrow.
    images: 1–9 of any aspect (each piece keeps its picture's shape; clips play inside their frames); text: the handwritten note."""
    srcs = [s for s in fit.as_list(p.get("images")) if s][:9] or ([p.get("image") or p.get("video")] if (p.get("image") or p.get("video")) else [])
    r = X.rand
    import sys; M = sys.modules.get("h9fx__media")                 # clips play inside their torn frames (fx/_media.py)
    play = {i for i, s_ in enumerate(srcs) if fit.is_video(s_)} if M else set()
    R = f"#{cid}_st" if play else f"#{cid}"
    ars = [min(2.4, max(0.5, fit.aspect(X, s))) for s in srcs] or [1.5]
    ars = [1.5 if 1.3 <= a <= 1.9 else a for a in ars]          # ordinary landscape photos print as 3:2
    if len(srcs) == 3 and not X.portrait and all(a == 1.5 for a in ars):
        pos = [(14, 18, 34, -6), (46, 12, 30, 5), (30, 52, 36, -2)]   # the designed three-piece layout
    else:
        pos = fit.scatter(len(srcs) or 1, X.portrait, r, ars)
    if X.portrait and pos:     # 9:16: the pieces live between the header and the note, never under the caption
        hs = [w / (ars[i] if i < len(ars) else 1.5) * X.W / X.H for i, (x, y, w, rot) in enumerate(pos)]
        top, bot = min(y for _, y, _, _ in pos), max(y + h for (_, y, _, _), h in zip(pos, hs))
        lo, hi = 12.0, 58.0
        if bot > hi or top < lo:
            s = min(1.0, (hi - lo) / max(bot - top, 1e-6))
            pos = [(x + w * (1 - s) / 2, lo + (y - top) * s, w * s, rot) for x, y, w, rot in pos]
    clips = ["polygon(2% 4%,30% 0,62% 3%,98% 1%,100% 30%,97% 64%,99% 98%,64% 100%,32% 96%,1% 99%,3% 62%,0 28%)",
             "polygon(0 2%,40% 4%,100% 0,98% 40%,100% 100%,55% 97%,0 100%,2% 50%)",
             "polygon(3% 0,100% 3%,96% 52%,100% 97%,48% 100%,1% 96%,4% 45%)"]
    def face(i):
        if i in play: return f'<div class="cpv" style="aspect-ratio:{ars[i]:.3f}">{M.vtile(X, srcs[i], t, d, p.get("focus"))}</div>'
        u = M.poster(X, srcs[i])[0] if (M and fit.is_video(srcs[i])) else X.asset(srcs[i])
        return f'<img src="{u}" alt="" style="aspect-ratio:{ars[i]:.3f}; object-position:{fit.focus_css(p.get("focus"))}">'
    pieces = "".join(f'<div class="cp" style="left:{x}%;top:{y}%;width:{w}%;transform:rotate({rot}deg)"><div class="ph" style="clip-path:{clips[i % 3]}">'
                     f'{face(i)}</div><i class="tp"></i></div>'
                     for i, (x, y, w, rot) in enumerate(pos) if i < len(srcs))
    note = fit.as_text(p.get("text", "这张才对"), " ")
    nf = fit.fit_text(note, X.W * 0.3, X.H * 0.14, _vm(X, 6), _vm(X, 3.2), lh=1.1, max_lines=2)
    nx, ny = (50, 63) if X.portrait else (66, 72)      # 9:16: above the caption and clear of the platform's bottom bar
    body = (f'<div class="cbg"></div>{pieces}<svg class="arw" viewBox="0 0 300 200" style="left:{nx - 10}%;top:{ny - 16}%"><path d="M20 160 C 90 40, 200 30, 270 80 M270 80 l-34 -6 M270 80 l-14 30"/></svg>'
            f'<div class="cnote" style="left:{nx}%;top:{ny}%;font-size:{nf.px}px">{"<br>".join(X.rich(l) for l in nf.lines)}</div>')
    if play:
        _clip(X, cid, t, d, "", p)
        M.stage(X, cid, t, d, body, _theme_style(p, paint=False))
    else:
        _clip(X, cid, t, d, body, p)
    X.css("aefx-clv", ".fx .cp .cpv { position:relative; width:100%; overflow:hidden; }")
    X.css("aefx-cl", ".fx .cbg { position:absolute; inset:0; background:#ece6da; } .fx .cp { position:absolute; } .fx .cp .ph { background:#fff; padding:1vmin; box-shadow:0 1vmin 2.4vmin rgba(60,40,10,.3); } .fx .cp img { display:block; width:100%; aspect-ratio:3/2; object-fit:cover; } .fx .cp .tp { position:absolute; left:50%; top:-1.4vmin; width:9vmin; height:2.8vmin; margin-left:-4.5vmin; background:rgba(235,220,170,.85); transform:rotate(-4deg); } .fx .arw { position:absolute; width:22%; overflow:visible; } .fx .arw path { fill:none; stroke:#d1281f; stroke-width:7; stroke-linecap:round; stroke-linejoin:round; } .fx .cnote { position:absolute; font:400 6vmin var(--f-hand, cursive); color:#d1281f; transform:rotate(-4deg); white-space:nowrap; line-height:1.1; }")
    each = _st(d - 1.2, max(len(srcs), 1), 0.33, 0.55)
    X.tw(f'tl.from("{R} .cp", {{y:"-30vmin", rotation:"+=18", opacity:0, duration:0.33, ease:"steps(4)", stagger:{each:.3f}}}, {t + 0.1:.3f});')
    ta = t + 0.1 + each * max(len(srcs) - 1, 0) + 0.45
    X.tw(f'tl.fromTo("{R} .arw path", {{strokeDasharray:600, strokeDashoffset:600}}, {{strokeDashoffset:0, duration:0.5, ease:"steps(6)"}}, {min(ta, t + d - 0.9):.3f});')
    X.tw(f'tl.from("{R} .cnote", {{opacity:0, scale:0.6, duration:0.25, ease:"steps(3)"}}, {min(ta + 0.4, t + d - 0.5):.3f});')
    for k in range(min(len(srcs), 4)): X.sfx(t + 0.1 + k * each, "paper")


def match_cut(X, cid, t, d, p):
    """文字匹配剪辑 Text Match Cut (#23, Envato Elements 标题热门第1/2): the word holds its exact place while
    everything around it hard-cuts — background, colour field and typeface change every few frames.
    Each cut is a designed pair (ground + type treatment), so the word always reads. images: 0…N (all are cycled; clips play as grounds)."""
    srcs = [s for s in fit.as_list(p.get("images")) if s]
    import sys; M = sys.modules.get("h9fx__media")                 # clip grounds: one timed layer per clip, shown on its cuts
    vk = {s_: j for j, s_ in enumerate(dict.fromkeys(x for x in srcs if fit.is_video(x)))} if M else {}
    R = f"#{cid}_st" if vk else f"#{cid}"
    D_ = "var(--f-display)"; S_ = "'h9-noto-serif-sc', serif"; H_ = "var(--f-hand, cursive)"; M_ = "var(--f-mono, monospace)"
    combos = [("img", D_, 900, "#fff"), ("#ece6da", S_, 700, "#111"), ("img", H_, 400, "#fff"), ("#1a3bd8", D_, 900, "#fff"),
              ("img", S_, 700, "#fff"), ("#111", M_, 700, "var(--accent)"), ("img", D_, 900, "#fff"), ("var(--accent)", S_, 700, "#111")]
    n = int((d - 0.4) / 0.22)
    f = _fit(X, p.get("text", ""), max_vmin=20, min_vmin=6, box=(0.84, 0.5), max_lines=2, lh=1.0)
    vl = "".join(f'<div class="mcv" data-k="{j}">{M.vtile(X, s_, t, d)}</div>' for s_, j in vk.items())
    body = f'<div class="mcb"></div>{vl}<div class="mcw" style="font-size:{f.px}px">{_lines(X, f)}</div>'
    if vk:
        _clip(X, cid, t, d, "", p)
        M.stage(X, cid, t, d, f'<div class="stage">{body}</div>', _theme_style(p, paint=False))
        X.css("aefx-mcv", ".fx .mcv { position:absolute; inset:0; opacity:0; overflow:hidden; }")
    else:
        _clip(X, cid, t, d, body, p)
    X.css("aefx-mc", ".fx .mcb { position:absolute; inset:0; background-size:cover; background-position:center; } .fx .mcw { position:relative; font-size:20vmin; line-height:1; text-shadow:0 .03em .25em rgba(0,0,0,.35); text-align:center; }")
    ii = 0
    for k in range(n):
        tt = t + 0.1 + k * 0.22
        g, fnt, w, c = combos[k % len(combos)]
        shown = None
        if g == "img":
            if srcs:
                cur = srcs[ii % len(srcs)]; ii += 1
                if cur in vk: shown, bg = vk[cur], "#111"
                else: bg = fit.bg_css(X, cur, p.get("focus"))
            else: bg = "#111"
        else: bg = g
        X.tw(f'tl.set("{R} .mcb", {{background:"{bg}"}}, {tt:.3f});')
        if vk:
            X.tw(f'tl.set("{R} .mcv", {{opacity:0}}, {tt:.3f});')
            if shown is not None: X.tw(f'tl.set("{R} .mcv[data-k=\'{shown}\']", {{opacity:1}}, {tt:.3f});')
        X.tw(f'tl.set("{R} .mcw", {{fontFamily:"{fnt}", fontWeight:{w}, color:"{c}"}}, {tt:.3f});')
        X.sfx(tt, "click")


def impact(X, cid, t, d, p):
    """冲击抖动 (#24, Bricks 106.8万 2025): the title slams in and the whole frame takes a decaying camera shake."""
    big, f = _big(X, p, cls="big im")
    _clip(X, cid, t, d, f'<div class="col">{big}{_sub(X, p)}</div>', p)
    X.tw(f'tl.from("#{cid} .im", {{scale:2.6, opacity:0, duration:0.22, ease:"power4.in"}}, {t + 0.1:.3f});')
    amp = 26
    for k in range(9):
        a = amp * (0.72 ** k)
        X.tw(f'tl.to("#{cid} > .stage", {{x:{X.rand.uniform(-a, a):.1f}, y:{X.rand.uniform(-a, a):.1f}, rotation:{X.rand.uniform(-a, a) / 20:.2f}, duration:0.035, ease:"none"}}, {t + 0.32 + k * 0.035:.3f});')
    X.tw(f'tl.to("#{cid} > .stage", {{x:0, y:0, rotation:0, duration:0.08}}, {t + 0.32 + 9 * 0.035:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, y:12, duration:0.4}}, {t + 0.6:.3f});')
    X.sfx(t + 0.32, "hit")


def dual(X, cid, t, d, p):
    """横竖双屏 (one composition, two aspect ratios): a landscape screen and a portrait phone slide in showing the same frame.
    img_h / img_v (any aspect, cropped with focus); either may be left out and the other is used for both."""
    ih, iv = p.get("img_h") or p.get("image") or p.get("img_v"), p.get("img_v") or p.get("image") or p.get("img_h")
    fc = fit.focus_css(p.get("focus"))
    tf = _fit(X, p.get("text", ""), box=(0.8, 0.08), max_vmin=5, min_vmin=2.6, max_lines=1) if p.get("text") else None
    _clip(X, cid, t, d, f'<div class="du"><div class="dh"><img src="{X.asset(ih)}" alt="" style="object-position:{fc}"><span>16:9</span></div><div class="dv"><img src="{X.asset(iv)}" alt="" style="object-position:{fc}"><span>9:16</span></div></div>'
                        + (f'<div class="dut" style="font-size:{tf.px}px; bottom:{max(_vm(X, 9), _cap_clear(X, p)):.0f}px">{_lines(X, tf)}</div>' if tf else ""), p)
    X.css("aefx-du", ".fx .du { display:flex; align-items:center; gap:5vmin; } #root.v .fx .du { flex-direction:column; gap:4vmin; } .fx .dh, .fx .dv { position:relative; border-radius:2vmin; overflow:hidden; box-shadow:0 0 0 .6vmin #2a2826, 0 3vmin 8vmin rgba(0,0,0,.6); } .fx .dh { width:62vmin; aspect-ratio:16/9; } .fx .dv { width:22vmin; aspect-ratio:9/16; border-radius:3vmin; } #root.v .fx .dh { width:66vmin; } #root.v .fx .dv { width:26vmin; } #root.v .fx .du { gap:3vmin; } #root.v .fx .dut { bottom:auto; top:330px; } .fx .du img { width:100%; height:100%; object-fit:cover; display:block; } .fx .du span { position:absolute; left:1.4vmin; bottom:1.2vmin; font:600 2vmin var(--f-mono, monospace); color:#fff; background:rgba(0,0,0,.55); padding:.3vmin 1vmin; border-radius:.6vmin; } .fx .dut { position:absolute; left:0; right:0; bottom:9vmin; text-align:center; font:800 5vmin var(--f-display); color:var(--fg); white-space:nowrap; }")
    X.tw(f'tl.from("#{cid} .dh", {{x:"-30vmin", opacity:0, rotationY:25, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .dv", {{x:"30vmin", opacity:0, rotationY:-25, duration:0.7, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("#{cid} .dut", {{opacity:0, y:20, duration:0.5}}, {t + 0.5:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")


FX = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in ("math", "fit")}


def _plugins():
    """more effects live one-per-file in scripts/h9/fx/<name>.py (each exports FX = {"name": fn}); they may use
    this module's helpers (_clip, _chars, THEMES). Lets several people add effects without touching this file."""
    import importlib.util, pathlib
    for f in sorted((pathlib.Path(__file__).parent / "fx").glob("[!_]*.py")):
        spec = importlib.util.spec_from_file_location(f"h9fx_{f.stem}", f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for k, v in getattr(m, "FX", {}).items():
            if k in FX: raise SystemExit(f"effect {k!r} in {f.name} clashes with an existing effect")
            FX[k] = v


_plugins()
