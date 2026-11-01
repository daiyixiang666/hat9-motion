"""delivery — film-level switches in video.json `meta` that are not about timing.

  lang      = "en"            any string in the video.json may be {"zh": "...", "en": "..."}; the build picks one
                              (default meta.lang, else "zh"; missing language → the first one given). voice / words /
                              music may be per-language dicts too, so one file holds every language version.
  brand     = "brand.json"    {"colors": {bg, fg, accent, accent2, muted, line, ...}, "tokens": {...}, "fonts": {display, body,
                              num, mono, serif: font id from assets/fonts.json}, "logo": "logo.svg", "logo_pos": "tr",
                              "name": "…"} — recolours and refonts whatever style is used; scripts/design_md.py writes one.
  series    = {"name": "商业拆解", "ep": 12, "opener": true, "opener_dur": 1.8, "cover": "press"}
                              a series card opens the film (the narration is moved back by opener_dur); cover.py reads it.
  ai_label  = true | "AI 生成" | {"text": "…", "pos": "tl|tr|bl|br"}   a small corner badge for the whole film.
  moods     = per beat "mood": "heavy" | "light" (carried forward until changed); STYLE["moods"] may define token sets,
              otherwise heavy = a dark ground, light = the style's own tokens. meta.music_moods = {"heavy": "x.mp3"}
              swaps the music bed at mood changes (crossfaded).
"""
import json
from pathlib import Path

from . import core


LANGS = {"zh", "zh-CN", "zh-TW", "zh-HK", "en", "ja", "ko", "fr", "de", "es", "pt", "ru", "ar", "fa", "ur", "he", "it", "vi", "th", "id", "ms"}
RTL = {"ar", "fa", "ur", "he"}


def _is_lang_dict(o):
    """{"zh": …, "en": …}: every key a known language code, at least one of them zh / en (so {"sh": …, "rt": …} place
    tables and other short-key dicts are left alone)."""
    return bool(o) and all(isinstance(k, str) and k in LANGS for k in o) and bool({"zh", "en", "zh-CN"} & set(o))


def resolve_lang(obj, lang):
    """{"zh": a, "en": b} -> the chosen language, recursively (missing language -> zh, else the first given)."""
    if isinstance(obj, dict):
        if _is_lang_dict(obj):
            pick = obj.get(lang, obj.get(lang.split("-")[0], obj.get("zh", next(iter(obj.values())))))
            return resolve_lang(pick, lang)
        return {k: resolve_lang(v, lang) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_lang(v, lang) for v in obj]
    return obj


# each style's own names for its accent hues (a brand's accent / accent2 are poured into these too)
ALIASES = {"press": (("red", "cap-em"), ("lemon",)), "screen": (("lime",), ("violet",)), "atlas": (("route1",), ("route2",)),
           "poster": (("blue",), ()), "hud": (("cream",), ()), "doc": ((), ()), "reel": ((), ())}
BRAND_COLORS = ("bg", "fg", "muted", "accent", "accent2", "alert", "line", "paper", "ink", "card", "card-fg")


def apply_brand(style, meta, src_dir):
    """recolour / refont a loaded style from meta.brand (a path or an inline dict). Returns the brand dict or None."""
    b = meta.get("brand")
    if not b: return None
    if isinstance(b, str):
        p = Path(b) if Path(b).is_absolute() else Path(src_dir) / b
        b = json.loads(p.read_text())
        b["_dir"] = str(p.parent)
    tok = dict(style["tokens"])
    for k, v in (b.get("colors") or {}).items():
        tok[k] = v
    # styles name their extra hues differently (press: red / lemon; screen: lime …): map the brand accent onto them
    acc, acc2 = (b.get("colors") or {}).get("accent"), (b.get("colors") or {}).get("accent2")
    sid = getattr(style.get("_mod"), "__name__", "")
    a1, a2 = style.get("accent_aliases") or ALIASES.get(sid, ((), ()))[0], style.get("accent2_aliases") or ALIASES.get(sid, ((), ()))[1]
    for k in a1:
        if acc: tok[k] = acc
    for k in a2:
        if acc2: tok[k] = acc2
    if b.get("colors", {}).get("card") and sid == "press": tok["white"] = b["colors"]["card"]
    tok.update(b.get("tokens") or {})
    style["tokens"] = tok
    fonts = dict(style.get("fonts", {}))
    for role, fid in (b.get("fonts") or {}).items():
        fonts[role] = fid
    style["fonts"] = fonts
    style["_brand"] = b
    return b


def logo_mark(X, D, brand):
    """the brand's logo as a small corner mark for the whole film (svg / png)."""
    if not brand or not brand.get("logo"): return
    p = Path(brand["logo"])
    if not p.is_absolute(): p = Path(brand.get("_dir", X.src)) / p
    url = X.asset(p, "img")
    pos = brand.get("logo_pos") or {}
    if isinstance(pos, dict):     # per orientation; 9:16 defaults to bottom left, in the free band between captions and footer
        pos = pos.get("9:16" if X.portrait else "16:9") or ("bl" if X.portrait else "tr")
    h = brand.get("logo_h") or (52 if X.portrait and pos[0] == "b" else 72 if X.portrait else 64)
    lab = X.v.get("meta", {}).get("ai_label")
    lab_pos = (lab.get("pos") if isinstance(lab, dict) else None) or ("br" if X.portrait else "tr")
    stack = 52 if lab and lab_pos == pos else 0          # the AI badge holds the corner: the logo sits just inside it
    css = _corner(X, pos, extra=(26 if pos[0] == "t" else 0) + stack)
    # a light plate keeps a dark logo readable on dark pages (logo_plate: false to drop it, or a CSS colour)
    plate = brand.get("logo_plate", True)
    plate_css = "" if plate is False else f"background:{plate if isinstance(plate, str) else 'rgba(255,255,255,.88)'};padding:6px 10px;border-radius:10px;box-sizing:content-box;"
    if pos == "tr" and not X.portrait:     # press's thesis page hangs a giant quote mark in that corner: drop it under the logo
        X.css("logo-room", "#root.h .pr-thesis .qm { top:270px; }")
    # the runtime lays timed root clips out full-frame, so the clip IS full-frame and the mark sits in its corner inside it
    X.clip("brandlogo", 0, D, f'<img src="{url}" alt="" style="position:absolute;{css}height:{h}px;width:auto;display:block;{plate_css}'
           f'opacity:{brand.get("logo_opacity", 0.92)}">', "ov-logo", 46, track=18, sty="pointer-events:none")


def _corner(X, pos, extra=0):
    """css offsets for a corner badge that stays clear of the page furniture and (9:16) the platform chrome."""
    if X.portrait:      # 9:16: under the header row / between the caption band (≤ 1420) and the footer line (1478)
        top, bottom, side = 236 + extra, 452, 48
    else:
        top, bottom, side = 104 + extra, 120, 40
    v = f"top:{top}px;" if pos[0] == "t" else f"bottom:{bottom + extra}px;"
    hz = f"left:{side}px;" if pos[1] == "l" else f"right:{side + (120 if X.portrait and pos[0] == 'b' else 0)}px;"
    return v + hz


def ai_label(X, D, meta):
    lab = meta.get("ai_label")
    if not lab: return
    if lab is True: lab = {}
    if isinstance(lab, str): lab = {"text": lab}
    text = lab.get("text", "AI 生成")
    pos = lab.get("pos", "br" if X.portrait else "tr")
    X.used_text.update(text)
    X.css("ai-label", """.ov-ai { pointer-events:none; }
.ov-ai span { position:absolute; display:inline-block; font-family:var(--f-body, sans-serif); font-weight:700; font-size:22px; letter-spacing:.06em; line-height:1;
  color:#fff; background:rgba(0,0,0,.46); border:1px solid rgba(255,255,255,.35); padding:7px 12px 8px; border-radius:6px; }
#root.v .ov-ai span { font-size:26px; }""")
    X.clip("ailabel", 0, D, f'<span style="{_corner(X, pos)}">{core.esc(text)}</span>', "ov-ai", 47, track=19)   # full-frame clip, badge in its corner


def series_opener(X, meta, dur):
    """a series card for the first `dur` seconds: series name, episode number, this episode's title."""
    s = meta.get("series") or {}
    name, ep, title = s.get("name", ""), s.get("ep"), meta.get("title", "")
    kick = f"第 {ep} 期" if ep is not None and not s.get("ep_label") else s.get("ep_label", "")
    X.used_text.update(name + kick + title + "0123456789")
    X.css("series-op", """.sx-op { background:var(--bg); display:flex; align-items:center; justify-content:center; }
.sx-op .in { display:flex; flex-direction:column; align-items:flex-start; gap:18px; max-width:78%; }
.sx-op .nm { font-family:var(--f-display); font-weight:900; font-size:clamp(84px, 10vmin, 160px); color:var(--fg); line-height:1.05; }
.sx-op .ep { font-family:var(--f-mono, monospace); font-size:28px; letter-spacing:.18em; color:var(--bg); background:var(--accent); padding:6px 14px; }
.sx-op .tt { font-family:var(--f-display); font-weight:700; font-size:clamp(40px, 4.4vmin, 64px); color:var(--muted); line-height:1.25; }
.sx-op .bar { width:120px; height:8px; background:var(--accent); transform-origin:0 50%; }""")
    inner = (f'<div class="in"><div class="bar"></div><div class="nm">{X.rich(name)}</div>'
             + (f'<div class="ep">{core.esc(kick)}</div>' if kick else "") + (f'<div class="tt">{X.rich(title)}</div>' if title else "") + "</div>")
    X.clip("seriesop", 0, dur, inner, "sx-op", 60, track=17)
    X.tw('tl.from("#seriesop .bar", {scaleX:0, duration:0.45, ease:"expo.out"}, 0.05);')
    X.tw('tl.from("#seriesop .nm", {yPercent:40, opacity:0, duration:0.6, ease:"expo.out"}, 0.12);')
    X.tw('tl.from("#seriesop .ep", {x:-30, opacity:0, duration:0.45, ease:"expo.out"}, 0.35);')
    X.tw('tl.from("#seriesop .tt", {opacity:0, y:16, duration:0.5, ease:"power3.out"}, 0.5);')
    X.tw(f'tl.to("#seriesop .in", {{opacity:0, y:-20, duration:0.3, ease:"power2.in"}}, {max(0.6, dur - 0.32):.3f});')
    X.sfx(0.12, "title")


DEFAULT_MOODS = {
    # dark ground; styles that paint text with --ink and cards with --white / --card (press) get those swapped too
    "heavy": {"bg": "#121212", "fg": "#efeae1", "muted": "#8f897f", "line": "#2c2a27", "card": "#1c1b19", "card-fg": "#efeae1", "paper": "#121212",
              "ink": "#efeae1", "white": "#1c1b19", "surf": "#0c0e12", "surf2": "#12151a"},
}


def mood_vars(X, mood):
    """inline CSS variables for a beat in this mood ('' for the style's own look)."""
    if not mood or mood in ("light", "default", "normal"): return ""
    tok = (X.S.get("moods") or {}).get(mood) or DEFAULT_MOODS.get(mood)
    if not tok: return ""
    return "".join(f"--{k}:{v};" for k, v in tok.items()) + "background:var(--bg);"


def paint_mood(X, cid, n_els, mood):
    """apply a mood to the clips a beat just emitted (the scene root and its sibling layers)."""
    sty = mood_vars(X, mood)
    if not sty: return
    for i in range(n_els, len(X.els)):
        el = X.els[i]
        if f'id="{cid}' not in el[:200]: continue
        X.els[i] = el.replace('style="z-index:', f'style="{sty}z-index:', 1)


def mood_segments(beats, times, D):
    """[(t0, t1, mood)] with the mood carried forward from beat to beat."""
    segs, cur = [], None
    for b, (t, _) in zip(beats, times):
        m = b.get("mood", cur) or "light"
        if m != cur:
            if segs: segs[-1][1] = t
            segs.append([t, D, m]); cur = m
    if segs: segs[0][0] = 0.0
    return segs
