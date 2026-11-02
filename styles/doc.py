"""doc · 实拍纪录 —— 商业纪录片的语言：Bloomberg Originals / Netflix 商业纪录片的实拍空镜 + 数据叠字，
Vox Atlas 的档案影像，小Lin说 的实拍段落。画面一直是真的在动的视频：2.39 遮幅、统一调色（预调 LUT）、
胶片颗粒、按口播切镜、推镜和变速；叠在画面上的是细线下三分之一、衬线大数字、取景框追踪标签、章节卡、清单。
左上角一个"年份计数器"贯穿全片，时间跳转时整列滚动。

beat = 一个镜头（scene "shot"）或一张卡（scene "card"）。

镜头的素材（media）—— 任意数量、任意比例、视频或静帧都行：
  "media": "x.mp4" | ["a.mp4", "b.jpg", {"src": "c.mp4", "in": 3.2, "focus": [0.3, 0.6], "to": [0.6, 0.5], "w": 2, "fit": "auto"}]
  多个素材平分（或按 w 加权）这一个镜头的时长，依次硬切。视频是顶层计时元素，从 in 秒开始播；静帧做 Ken Burns。
  focus = 画面里要保住的点（0–1），竖屏 / 横屏裁切都围着它；to = 镜头结束时的焦点（推拉摇移）。
  fit: cover（铺满裁切）| contain（完整显示 + 模糊铺底）| auto（素材比画幅窄很多时 contain，否则 cover）。
  没写 media 时用 clip / image，再没有就用 assets/clips/<id>.mp4（examples/doc/prep_clips.py 预调色、预变速的产物）。
叠层：stamp 居中大字 · l3 下三分之一 · call 数据卡（可多张依次替换）· list 清单（2–8 项）· trk 追踪框 · say 判断句 · tag 画面说明。
所有文字按长度自动定字号，太长就按词均衡断行（最多 2–3 行），见 fit()；输入范围见 examples/doc/variants.json。
"""
import functools, math, re, subprocess

STYLE = {
    # page themes an effect beat can ask for: night print (ink) · Atlas map paper (paper) · darkroom oxblood (red) · tungsten amber (lemon)
    "fx_themes": {
        "ink":   {"bg": "#0b0b0a", "fg": "#f4efe6", "muted": "#a39b8f", "accent": "#f0a640", "card": "#171614", "card-fg": "#f4efe6", "line": "#34302a"},
        "paper": {"bg": "#e6dece", "fg": "#18140e", "muted": "#5e5547", "accent": "#b4501c", "card": "#f3ede1", "card-fg": "#18140e", "line": "#c8baa0"},
        "red":   {"bg": "#3d110d", "fg": "#f6ece0", "muted": "#cfb0a2", "accent": "#f0a640", "card": "#521a14", "card-fg": "#f6ece0", "line": "#6e2b22"},
        "lemon": {"bg": "#e8a240", "fg": "#16100a", "muted": "#4f3414", "accent": "#6a1a0f", "card": "#fbf3e3", "card-fg": "#16100a", "line": "rgba(22,16,10,.28)"},
    },
    "name": "实拍纪录", "en": "Documentary", "benchmarks": ["Bloomberg Originals", "Netflix 商业纪录片", "Vox Atlas", "小Lin说 实拍段落"],
    "tokens": {
        "bg": "#050505", "fg": "#f4efe6", "muted": "rgba(244,239,230,.62)", "accent": "#f0a640", "accent2": "#f0a640", "alert": "#f0a640",
        "line": "rgba(244,239,230,.35)", "paper": "#050505", "ink": "#050505", "card": "#0c0c0c", "card-fg": "#f4efe6",
        "cap-fg": "#f4efe6", "cap-size": "34px", "cap-weight": "500", "cap-shadow": "0 1px 2px rgba(0,0,0,.6)", "cap-bottom": "46px", "cap-em": "#f0a640",
        "mascot-bg": "#0c0c0c",
    },
    "fonts": {"display": "noto-serif-sc", "serif": "noto-serif-sc", "num": ["playfair", "noto-serif-sc"], "numi": ["playfair-italic", "noto-serif-sc"],
              "body": "noto-sans-sc", "mono": ["ibm-plex-mono", "noto-sans-sc"], "latin": "inter"},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "caption_mode": "reading",
    "layers": [("letterbox", {"ratio": 2.39}), ("vignette", {"alpha": 0.5, "inner": 48}), ("grain", {"opacity": 0.14, "fps": 24})],
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 150, "bottom": 140, "h": 380}, "portrait": {"left": 400, "bottom": 610, "h": 290}},
    "outro": {"move": False},
    "sfx": {"transition": ("whoosh_deep", 0.35), "hit": ("hit", 0.32), "count": ("type", 0.25), "line": ("click", 0.25), "lock": ("beep", 0.12),
            "enter": ("whoosh_soft", 0.25), "mascot": ("whoosh_soft", 0.25), "title": ("hit", 0.3)},
}

CSS = r"""
.st-doc .em .emb { display:none; }
.dv { background:#000; }
.dm { overflow:hidden; } .dm img { position:absolute; display:block; max-width:none; }
.dm .bl, .dv.bl { filter:blur(38px) brightness(.42) saturate(.8); }
.dov { pointer-events:none; }
#root.v .cap { bottom:auto; top:1330px; padding:0 70px; } #root.v .cap .cp { font-size:44px; text-shadow:0 2px 14px rgba(0,0,0,.85), 0 1px 2px #000; }
/* running bug + year counter (inside the top letterbox bar in 16:9) */
.d-bug { position:absolute; left:96px; right:96px; top:44px; height:52px; display:flex; align-items:center; justify-content:space-between; z-index:60; }
.d-yr { display:flex; align-items:baseline; gap:16px; }
.d-yr small { font-family:var(--f-mono); font-size:18px; letter-spacing:.32em; color:var(--muted); }
.d-yr .dg { display:inline-flex; font-family:var(--f-num); font-weight:700; font-size:44px; line-height:1; color:var(--accent); font-variant-numeric:lining-nums tabular-nums; }
.d-yr .col { display:inline-block; height:1em; overflow:hidden; } .d-yr .col span { display:block; height:1em; }
.d-mark { font-family:var(--f-mono); font-size:18px; letter-spacing:.3em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.d-mark b { color:var(--fg); font-weight:500; font-family:var(--f-body); letter-spacing:.12em; margin-right:14px; }
#root.v .d-bug { left:60px; right:60px; top:170px; }
/* scrims for legibility over footage */
.d-scrim { position:absolute; inset:0; background:linear-gradient(90deg, rgba(0,0,0,.74) 0%, rgba(0,0,0,.42) 42%, rgba(0,0,0,0) 72%); }
.d-l3s { position:absolute; inset:0; opacity:0; background:linear-gradient(20deg, rgba(0,0,0,.7) 0%, rgba(0,0,0,.25) 35%, rgba(0,0,0,0) 55%); }
.d-top { display:none; }
#root.v .d-top { display:block; position:absolute; left:0; right:0; top:0; height:420px; background:linear-gradient(180deg, rgba(0,0,0,.6), rgba(0,0,0,0)); }
#root.v .d-l3s { background:linear-gradient(0deg, rgba(0,0,0,0) 30%, rgba(0,0,0,.55) 45%, rgba(0,0,0,0) 62%); }
.d-scrim.strong { background:linear-gradient(90deg, rgba(0,0,0,.82) 0%, rgba(0,0,0,.6) 50%, rgba(0,0,0,.2) 80%); }
#root.v .d-scrim.strong { background:linear-gradient(180deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.62) 55%, rgba(0,0,0,.3) 75%, rgba(0,0,0,.5) 100%); }
#root.v .d-scrim:not(.strong) { background:linear-gradient(180deg, rgba(0,0,0,.6) 0%, rgba(0,0,0,.25) 40%, rgba(0,0,0,.05) 55%, rgba(0,0,0,.45) 100%); }
/* data callout: rule, label, serif figure, sub, source */
.d-call { position:absolute; left:150px; top:240px; width:1100px; }
.d-call .rule { width:72px; height:3px; background:var(--accent); transform-origin:0 50%; }
.d-call .lab, .d-call .sub, .d-stamp .big, .d-l3 .nm, .d-list .ttl, .d-list .it .tx, .d-say .l, .d-card .t { white-space:nowrap; }
.d-call .lab { margin-top:22px; font-family:var(--f-serif); font-weight:600; line-height:1.3; color:var(--fg); letter-spacing:.04em; }
.d-call .fig { margin-top:6px; display:flex; flex-wrap:wrap; align-items:baseline; column-gap:.08em; font-family:var(--f-num); font-weight:800; line-height:.95; color:var(--fg); letter-spacing:-.02em; font-variant-numeric:lining-nums; }
.d-call .fig .u { font-family:var(--f-serif); font-weight:700; color:var(--accent); letter-spacing:0; }
.d-call .fig .pre { color:var(--accent); }
.d-call .sub { margin-top:14px; font-family:var(--f-body); font-weight:500; line-height:1.4; color:var(--muted); }
.d-call .src { margin-top:16px; font-family:var(--f-mono); font-size:19px; line-height:1.4; letter-spacing:.04em; color:rgba(244,239,230,.55); }
.d-call .bar { margin-top:24px; width:620px; height:10px; background:rgba(244,239,230,.18); position:relative; }
.d-call .bar i { position:absolute; inset:0; right:auto; background:var(--accent); transform-origin:0 50%; }
#root.v .d-call { left:64px; top:330px; width:950px; } #root.v .d-call .bar { width:860px; }
/* stamp: a centred title (e.g. the year) that tracks in */
.d-stamp { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; text-align:center; }
.d-stamp .big { font-family:var(--f-num); font-weight:800; line-height:1.02; color:var(--fg); letter-spacing:.02em; font-variant-numeric:lining-nums; text-shadow:0 4px 40px rgba(0,0,0,.4); }
.d-stamp .big .c { display:inline-block; }
.d-stamp .sm { font-family:var(--f-mono); font-size:20px; line-height:1.5; letter-spacing:.4em; color:var(--fg); opacity:.85; max-width:80%; }
/* lower third */
.d-l3 { position:absolute; left:150px; bottom:190px; width:1000px; }
.d-l3 .bar { height:3px; background:var(--accent); transform-origin:0 50%; }
.d-l3 .nm { margin-top:16px; font-family:var(--f-serif); font-weight:700; line-height:1.18; color:var(--fg); letter-spacing:.04em; overflow:hidden; }
.d-l3 .nm span, .d-l3 .la span, .d-l3 .ro span { display:inline-block; }
.d-l3 .la { margin-top:2px; font-family:var(--f-numi); font-style:italic; font-weight:500; line-height:1.25; color:var(--fg); opacity:.88; overflow:hidden; }
.d-l3 .ro { margin-top:10px; font-family:var(--f-mono); font-size:17px; line-height:1.5; letter-spacing:.2em; color:var(--muted); overflow:hidden; }
#root.v .d-l3 { left:64px; bottom:auto; top:1040px; width:950px; }
/* tag: archive / illustrative footage label */
.d-tag { position:absolute; right:150px; bottom:168px; max-width:700px; font-family:var(--f-mono); font-size:18px; line-height:1.45; letter-spacing:.12em; color:rgba(244,239,230,.75); border:1px solid rgba(244,239,230,.4); padding:5px 12px; text-align:right; }
#root.v .d-tag { right:60px; bottom:auto; top:1250px; max-width:620px; }
/* tracking bracket */
.d-trk { position:absolute; }
.d-trk i { position:absolute; width:26px; height:26px; border:2.5px solid var(--fg); }
.d-trk i:nth-child(1) { left:0; top:0; border-right:0; border-bottom:0; } .d-trk i:nth-child(2) { right:0; top:0; border-left:0; border-bottom:0; }
.d-trk i:nth-child(3) { left:0; bottom:0; border-right:0; border-top:0; } .d-trk i:nth-child(4) { right:0; bottom:0; border-left:0; border-top:0; }
.d-trk .lb { position:absolute; left:0; bottom:calc(100% + 14px); white-space:nowrap; font-family:var(--f-mono); letter-spacing:.12em; color:#111; background:var(--accent); padding:4px 10px; }
.d-trk .ch { position:absolute; left:50%; top:50%; width:14px; height:14px; margin:-7px 0 0 -7px; border-radius:50%; border:2px solid var(--accent); }
/* list: 2–8 numbered items */
.d-list { position:absolute; left:150px; top:230px; width:1100px; }
.d-list .ttl { font-family:var(--f-serif); font-weight:700; line-height:1.25; color:var(--fg); letter-spacing:.04em; margin-bottom:.5em; }
.d-list .ttl::after { content:''; display:block; width:72px; height:3px; background:var(--accent); margin-top:.45em; }
.d-list .it { display:flex; align-items:baseline; gap:.7em; border-top:1px solid rgba(244,239,230,.22); }
.d-list .it .no { font-family:var(--f-mono); font-size:.5em; letter-spacing:.1em; color:var(--accent); flex:none; width:2.6em; }
.d-list .it .tx { font-family:var(--f-serif); font-weight:600; line-height:1.25; color:var(--fg); }
#root.v .d-list { left:64px; top:330px; width:950px; }
/* statement */
.d-say { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:0 140px; }
.d-say .l { font-family:var(--f-serif); font-weight:700; line-height:1.3; color:var(--fg); letter-spacing:.04em; text-shadow:0 2px 30px rgba(0,0,0,.55); }
.d-say .l .c { display:inline-block; }
.d-say .l .em .emt { color:var(--accent); }
.d-say .rule { width:90px; height:3px; background:var(--accent); margin-bottom:34px; transform-origin:50% 50%; }
#root.v .d-say { padding:0 70px; }
/* chapter card / outro */
.d-card { background:#050505; }
.d-card .in { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:18px; text-align:center; padding:0 120px; }
.d-card .k { font-family:var(--f-mono); font-size:18px; line-height:1.5; letter-spacing:.4em; color:var(--accent); }
.d-card .t { font-family:var(--f-serif); font-weight:900; color:var(--fg); letter-spacing:.06em; line-height:1.15; }
.d-card .t .c { display:inline-block; }
.d-card .s { font-family:var(--f-numi); font-style:italic; font-size:34px; line-height:1.3; color:var(--fg); opacity:.8; }
.d-card .m { font-family:var(--f-mono); font-size:17px; line-height:1.6; letter-spacing:.24em; color:var(--muted); }
.d-card .hr { width:120px; height:2px; background:var(--accent); transform-origin:50% 50%; }
#root.v .d-card .in { justify-content:flex-start; padding:600px 64px 0; }
"""


# ---------------------------------------------------------------- text fitting
def _w(ch):
    """advance of one glyph in em (good enough to size type before the browser does)."""
    o = ord(ch)
    if o >= 0x2E80: return 1.0
    if ch == " ": return 0.3
    if ch.isdigit(): return 0.62
    if ch.isupper(): return 0.7
    if ch in ".,:;·'’!|()-–": return 0.32
    if ch in "%$¥€≈+−→": return 0.75
    return 0.56


def em(s): return sum(_w(c) for c in str(s).replace("*", ""))


def _tokens(s):
    """words that must not be split: jieba words for Chinese, runs for Latin/numbers; punctuation sticks to the left."""
    try:
        import jieba
        parts = list(jieba.cut(s))
    except ImportError:
        parts = re.findall(r"[A-Za-z0-9.,%$¥€'’\-–·]+\s*|\*|.", s)
    toks = []
    for p in parts:
        if toks and (p in "，。、：；！？,.;:!?）」》*" or p.strip() == "" ):
            toks[-1] += p
        else:
            toks.append(p)
    # keep "*" opening markers with the word they open
    out = []
    for tk in toks:
        if out and out[-1].endswith("*") and out[-1].count("*") % 2 == 1 and out[-1].strip("*") == "": out[-1] += tk
        else: out.append(tk)
    return out


def balance(s, k):
    """break s into k lines whose widest line is as narrow as possible (breaks after punctuation are preferred)."""
    toks = _tokens(s); n = len(toks)
    if k <= 1 or n <= 1: return [s]
    k = min(k, n)
    pre = [0.0]
    for tk in toks: pre.append(pre[-1] + em(tk))

    @functools.lru_cache(None)
    def best(i, kk):
        if kk == 1: return (pre[n] - pre[i], (n,))
        res = None
        for j in range(i + 1, n - kk + 2):
            m, cuts = best(j, kk - 1)
            pen = 0.0 if toks[j - 1].rstrip()[-1:] in "，、：；,;:。" else 0.12
            val = max(pre[j] - pre[i], m) + pen
            if res is None or val < res[0]: res = (val, (j,) + cuts)
        return res
    _, cuts = best(0, k)
    lines, i = [], 0
    for j in cuts:
        lines.append("".join(toks[i:j]).strip()); i = j
    return [x for x in lines if x]


def fit(s, width, maxpx, minpx, maxlines=1, track=0.0, safety=0.92):
    """-> (px, 'line1|line2'). Explicit '|' breaks are kept. Otherwise shrink to one line down to minpx, then try
    2..maxlines balanced lines; if even that is too wide the size goes below minpx rather than overflow."""
    s = str(s); width = width * safety          # glyph estimates are approximate; keep a margin
    if "|" in s:
        lines = s.split("|")
        wm = max(em(x) + track * len(x) for x in lines) or 1
        return min(maxpx, width / wm), s
    best = None
    for k in range(1, maxlines + 1):
        lines = [s] if k == 1 else balance(s, k)
        wm = max(em(x) + track * len(x) for x in lines) or 1
        px = min(maxpx, width / wm)
        best = (px, "|".join(lines))
        if px >= minpx: break
    return best


def _chars(X, s):
    """per-glyph spans (for tracking-in), '|' = line break."""
    out = []
    for ln in str(s).split("|"):
        out.append("".join(f'<i class="c">{X.rich(ch)}</i>' if ch.strip() else " " for ch in ln))
    return "<br>".join(out)


def _T(X, b, k, t, dflt):
    v = b.get(k)
    return float(X.T(v, t)) if v is not None else dflt


# ---------------------------------------------------------------- media (any count, any aspect, video or still)
IMG = (".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")
_DIMS = {}


def _dims(path):
    p = str(path)
    if p not in _DIMS:
        try:
            o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", p]).decode().split(",")
            _DIMS[p] = (int(o[0]), int(o[1]))
        except Exception:
            _DIMS[p] = (1920, 1080)
    return _DIMS[p]


def _items(b):
    m = b.get("media")
    if m is None:
        m = [b.get("clip") or b.get("image") or f"assets/clips/{b['id']}.mp4"]
    elif isinstance(m, (str, dict)):
        m = [m]
    out = []
    for it in m:
        it = {"src": it} if isinstance(it, str) else dict(it)
        out.append(it)
    return out


def _picture(X):
    """the visible picture box (inside the letterbox in 16:9)."""
    if X.portrait: return 0, X.H
    bar = round((X.H - X.W / 2.39) / 2)
    return bar, X.H - 2 * bar


def _cover(X, sw, sh, fx, fy):
    s = max(X.W / sw, X.H / sh); ew, eh = sw * s, sh * s
    x = min(0, max(X.W - ew, X.W / 2 - fx * ew)); y = min(0, max(X.H - eh, X.H / 2 - fy * eh))
    return x, y, ew, eh


def _media(X, b, t, d, cid):
    """lay the shot's media on the timeline: sub-cuts by weight, focal-point framing, push / pan, Ken Burns on stills,
    narrow sources shown whole over a blurred copy of themselves."""
    items = _items(b)
    ws = [float(it.get("w", 1)) for it in items]; tot = sum(ws)
    legacy = b.get("pan")                       # old form: [x0, x1] = horizontal focus at start / end
    p_def = b.get("push")
    tk = t
    for k, it in enumerate(items):
        dk = d * ws[k] / tot
        url = X.asset(it["src"], "video" if not it["src"].lower().endswith(IMG) else "img")
        still = url.lower().endswith(IMG)
        sw, sh = _dims(X.out / url)
        f0 = it.get("focus") or b.get("focus") or ([legacy[0], 0.5] if legacy else [0.5, 0.5])
        f1 = it.get("to") or b.get("to") or ([legacy[1], f0[1]] if legacy else f0)
        fitm = it.get("fit", b.get("fit", "auto"))
        if fitm == "auto": fitm = "contain" if sw / sh < (X.W / X.H) * 0.7 else "cover"
        p0, p1 = it.get("push") or p_def or ([1.0, 1.12] if still else [1.0, 1.07])
        ease = it.get("ease", b.get("ease", "sine.inOut" if not still else "none"))
        tr = 2 + (X.beat["i"] * 3 + k) % 2
        sid = f"{cid}m{k}"
        layers = []
        if fitm == "contain":   # blurred cover copy behind, the whole frame in front
            x, y, ew, eh = _cover(X, sw, sh, 0.5, 0.5)
            layers.append(("bl", x, y, ew, eh, [1.1, 1.16], (0.5, 0.5), (0.5, 0.5)))
            top, ph = _picture(X)
            s = min(X.W * 0.92 / sw, ph / sh); ew, eh = sw * s, sh * s
            layers.append(("", (X.W - ew) / 2, top + (ph - eh) / 2, ew, eh, [max(1.0, min(p0, 1.05)), max(1.0, min(p1, 1.05))], (0.5, 0.5), (0.5, 0.5)))
        else:
            x, y, ew, eh = _cover(X, sw, sh, *f0)
            layers.append(("", x, y, ew, eh, [max(1.0, p0), max(1.0, p1)], tuple(f0), tuple(f1)))
        for j, (cls, x, y, ew, eh, (q0, q1), fa, fb) in enumerate(layers):
            lid = f"{sid}{'b' if cls else ''}"
            xa = min(0, max(X.W - ew, X.W / 2 - fa[0] * ew)) if not (cls == "" and fitm == "contain") else x
            xb = min(0, max(X.W - ew, X.W / 2 - fb[0] * ew)) if not (cls == "" and fitm == "contain") else x
            ya = min(0, max(X.H - eh, X.H / 2 - fa[1] * eh)) if not (cls == "" and fitm == "contain") else y
            yb = min(0, max(X.H - eh, X.H / 2 - fb[1] * eh)) if not (cls == "" and fitm == "contain") else y
            geo = f"left:{xa:.0f}px; top:{ya:.0f}px; width:{ew:.0f}px; height:{eh:.0f}px"
            org = f"{fa[0] * ew:.0f}px {fa[1] * eh:.0f}px"
            if still:
                X.clip(lid, tk, dk + 0.04, f'<img class="{cls}" src="{url}" alt="" style="{geo}">', "dm", 2 + j, track=tr + 4 * j, attrs="data-layout-allow-overflow")
                sel = f"#{lid} img"
            else:
                X.clip(lid, tk, dk + 0.04, "", f"dv {cls}".strip(), 2 + j, track=tr + 4 * j, tag="video",
                       attrs=f'src="{url}" muted playsinline data-media-start="{float(it.get("in", 0)):.3f}"',
                       sty=f"right:auto; bottom:auto; {geo}; object-fit:fill")
                sel = f"#{lid}"
            X.tw(f'tl.fromTo("{sel}", {{x:0, y:0, scale:{q0}, transformOrigin:"{org}"}}, {{x:{xb - xa:.0f}, y:{yb - ya:.0f}, scale:{q1}, duration:{dk:.2f}, ease:"{ease}"}}, {tk:.3f});')
        tk += dk


# ---------------------------------------------------------------- persistent bug
def _persistent(X):
    """the running bug and the rolling year counter, once, for the whole film."""
    meta = X.v.get("meta", {})
    yr = meta.get("year_roll")
    cols = ""
    if yr:
        a, z = str(yr["from"]), str(yr["to"])
        n = max(len(a), len(z)); a, z = a.rjust(n), z.rjust(n)
        X.used_text.update(a + z)
        cols = "".join(f'<span class="col"><span>{x if x.strip() else "&nbsp;"}</span><span>{y if y.strip() else "&nbsp;"}</span></span>' for x, y in zip(a, z))
    mark = f'<div class="d-mark"><b>第九顶帽子</b>{X.rich(meta.get("section", "商业拆解"))}</div>'
    X.used_text.update("YEAR")
    X.clip("dbug", 0, X.duration, f'<div class="d-top"></div><div class="d-bug"><div class="d-yr">{"<small>YEAR</small>" if yr else ""}<span class="dg">{cols}</span></div>{mark}</div>',
           "dov dbug", 60, track=24, attrs="data-layout-allow-overflow")
    X.tw('tl.from("#dbug .d-bug", {opacity:0, duration:0.6, ease:"power2.out"}, 0.15);')
    if yr:
        ta = float(X.T(yr["at"]))
        X.tw(f'tl.to("#dbug .col span", {{yPercent:-100, duration:0.55, ease:"expo.inOut", stagger:0.07}}, {ta:.3f});')
        X.sfx(ta, "count")


# ---------------------------------------------------------------- scenes
def shot(b, X, t, d, cid):
    """one shot: media (see the module doc) + whatever sits on it. Every text block is auto-fitted."""
    X.css("doc", CSS)
    if X.beat["i"] == 0: _persistent(X)
    _media(X, b, t, d, cid)
    P = X.portrait
    BOX = 950 if P else 1100                      # text column width for callouts / lists / lower thirds
    top, ph = _picture(X)
    over, s = [], f"#{cid}"
    if b.get("scrim", bool(b.get("call") or b.get("say") or b.get("list"))):
        over.append(f'<div class="d-scrim{" strong" if b.get("list") or b.get("scrim") == "strong" else ""}"></div>')

    # centred stamp (e.g. a year), tracking in; its own layer so it may outlive a quick shot (until: a cue)
    dst = 0
    if b.get("stamp"):
        st = b["stamp"]
        px, txt = fit(st["big"], X.W - (160 if P else 300), 230 if P else 300, 96 if P else 120, maxlines=3, track=0.02)
        dst = max(0.6, (_T(X, st, "until", t, t + d) - t))
        X.clip(f"{cid}st", t, dst, f'<div class="d-stamp"><div class="big" style="font-size:{px:.0f}px">{_chars(X, txt)}</div><div class="sm">{X.rich(st.get("small", ""))}</div></div>', "dov", 13, track=7)
    if b.get("l3"):
        l = b["l3"]
        npx, ntx = fit(l["name"], BOX, 56, 34, maxlines=2, track=0.04)
        lpx, ltx = fit(l.get("latin", ""), BOX, 32, 22, maxlines=2)
        barw = min(360, max(120, em(ntx.split("|")[0]) * npx * 0.7))
        tl3 = _T(X, b, "at_l3", t, t + 0.2)
        dl3 = max(1.2, _T(X, l, "until", t, t + d) - tl3 + 0.3)
        X.clip(f"{cid}l3", tl3 - 0.3, dl3, f'<div class="d-l3s"></div><div class="d-l3"><div class="bar" style="width:{barw:.0f}px"></div>'
               f'<div class="nm" style="font-size:{npx:.0f}px"><span>{X.rich(ntx)}</span></div><div class="la" style="font-size:{lpx:.0f}px"><span>{X.rich(ltx)}</span></div>'
               f'<div class="ro"><span>{X.rich(l.get("role", ""))}</span></div></div>', "dov", 13, track=8)
    for k, c in enumerate(b.get("call", [])):
        bar = f'<div class="bar"><i style="width:{c["bar"]}%"></i></div>' if c.get("bar") else ""
        fig, pre, unit = str(c["fig"]), str(c.get("pre", "")), str(c.get("unit", ""))
        # figure line: pre at .65, unit at .31 of the figure size; the unit wraps under the figure if it must
        need = em(pre) * 0.65 + em(fig) + em(unit) * 0.31 + 0.2
        fpx = max(78.0, min(230 if not P else 200, BOX / need))
        if em(fig) * fpx > BOX: fpx = BOX / em(fig)
        labpx, labtx = fit(c.get("label", ""), BOX, 36, 26, maxlines=2)
        subpx, subtx = fit(c.get("sub", ""), BOX, 28, 22, maxlines=3)
        prespan = f'<span class="pre" style="font-size:{fpx * 0.65:.0f}px">{X.rich(pre)}</span>' if pre else ""
        over.append(f'<div class="d-call" data-k="{k}"><div class="rule"></div><div class="lab" style="font-size:{labpx:.0f}px">{X.rich(labtx)}</div>'
                    f'<div class="fig" style="font-size:{fpx:.0f}px">{prespan}<span class="n">{X.rich(c.get("from", fig))}</span><span class="u" style="font-size:{max(26, fpx * 0.31):.0f}px">{X.rich(unit)}</span></div>'
                    f'<div class="sub" style="font-size:{subpx:.0f}px">{X.rich(subtx)}</div>{bar}<div class="src">{X.rich(c.get("src", ""))}</div></div>')
        X.used_text.update(fig + "0123456789.,")
    if b.get("list"):
        L = b["list"]; items = L["items"][:8]; n = len(items)
        avail = (1250 - 330 if P else top + ph - 60 - 230) - (90 if L.get("title") else 0)
        row = min(120.0, avail / max(n, 1))
        ipx = min(52.0, row * 0.46)
        longest = max(items, key=em)
        ipx2, _ = fit(longest, BOX - ipx * 2.6 * 0.5 - ipx * 0.7, ipx, 22, maxlines=2)
        ipx = min(ipx, max(ipx2, 22))
        rows = []
        for j, it in enumerate(items):
            _, tx = fit(it, BOX - ipx * 2.0, ipx, ipx, maxlines=2)
            rows.append(f'<div class="it" data-j="{j}" style="font-size:{ipx:.0f}px; padding:{max(6, (row - ipx * 1.25 * tx.count("|") - ipx * 1.25) / 2):.0f}px 0"><span class="no">{j + 1:02d}</span><span class="tx">{X.rich(tx)}</span></div>')
        tpx, ttx = fit(L.get("title", ""), BOX, 44, 30, maxlines=2)
        ttl = f'<div class="ttl" style="font-size:{tpx:.0f}px">{X.rich(ttx)}</div>' if L.get("title") else ""
        over.append(f'<div class="d-list">{ttl}{"".join(rows)}</div>')
        X.used_text.update("0123456789")
    if b.get("trk"):
        k = b["trk"]
        # the label hangs off the side of the box that has more room, and shrinks (then wraps) to stay on screen
        left_px = X.W * k["x"] / 100; bw = k.get("w", 200)
        room_r, room_l = X.W - left_px - 40, left_px + bw - 40
        side = "left:0; right:auto" if room_r >= room_l else "left:auto; right:0"
        room = max(room_r, room_l)
        lbpx, _ = fit(k["label"], room - 24, 18, 12, track=0.12)
        wrap = "" if em(k["label"]) * lbpx * 1.12 <= room - 24 else f"white-space:normal; width:{room - 24:.0f}px;"
        over.append(f'<div class="d-trk" style="left:{k["x"]}%; top:{k["y"]}%; width:{bw}px; height:{k.get("h", 120)}px"><i></i><i></i><i></i><i></i><b class="ch"></b>'
                    f'<div class="lb" style="font-size:{max(lbpx, 12):.0f}px; {side}; {wrap}">{X.rich(k["label"])}</div></div>')
    if b.get("say"):
        spx, stx = fit(b["say"], X.W - (140 if P else 280), 74 if P else 80, 44 if P else 52, maxlines=4 if P else 3, track=0.04)
        lines = "".join(f'<div class="l" style="font-size:{spx:.0f}px">{X.rich(x, split="chars")}</div>' for x in stx.split("|"))
        over.append(f'<div class="d-say"><div class="rule"></div>{lines}</div>')
    if b.get("tag"): over.append(f'<div class="d-tag">{X.rich(b["tag"])}</div>')
    if over:
        X.clip(cid, t, d, "".join(over), "dov", 12, track=6)

    # ---- motion
    if b.get("stamp"):
        q = f"#{cid}st"
        X.tw(f'tl.from("{q} .d-stamp .big .c", {{opacity:0, x:(i, el, all)=>(i - (all.length - 1) / 2) * 60, filter:"blur(14px)", duration:0.7, ease:"expo.out", stagger:0.04}}, {t:.3f});')
        X.tw(f'tl.from("{q} .d-stamp .sm", {{opacity:0, duration:0.4}}, {t + 0.25:.3f});')
        X.tw(f'tl.to("{q} .d-stamp", {{opacity:0, scale:1.06, filter:"blur(8px)", duration:0.3, ease:"power2.in"}}, {t + dst - 0.3:.3f});')
        X.sfx(t, "title")
    if b.get("l3"):
        q = f"#{cid}l3"
        X.tw(f'tl.from("{q} .d-l3 .bar", {{scaleX:0, duration:0.6, ease:"expo.inOut"}}, {tl3 - 0.2:.3f});')
        X.tw(f'tl.from("{q} .d-l3 .nm span, {q} .d-l3 .la span, {q} .d-l3 .ro span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {tl3:.3f});')
        X.tw(f'tl.to("{q} .d-l3s", {{opacity:1, duration:0.4}}, {tl3 - 0.3:.3f});')
        X.tw(f'tl.to("{q} .d-l3, {q} .d-l3s", {{opacity:0, duration:0.3, ease:"power2.in"}}, {tl3 - 0.3 + dl3 - 0.3:.3f});')
        X.sfx(tl3, "line")
    calls = b.get("call", [])
    for k, c in enumerate(calls):
        tc = _T(X, b, f"at_call{k}" if k else "at_call", t, t + 0.2 + k * (d - 0.4) / max(len(calls), 1))
        q = f"{s} .d-call[data-k='{k}']"
        X.tw(f'tl.from("{q} .rule", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {max(t, tc - 0.35):.3f});')
        X.tw(f'tl.from("{q} .lab", {{x:-24, opacity:0, duration:0.5, ease:"expo.out"}}, {max(t, tc - 0.3):.3f});')
        X.tw(f'tl.from("{q} .fig", {{y:40, opacity:0, filter:"blur(10px)", duration:0.6, ease:"expo.out"}}, {max(t, tc - 0.25):.3f});')
        X.tw(f'tl.from("{q} .sub, {q} .src, {q} .bar", {{opacity:0, y:12, duration:0.5, stagger:0.08}}, {tc + 0.25:.3f});')
        if c.get("count") is not None:
            dec = c.get("dec", 0)
            js = f"o.v.toFixed({dec})" if dec else "Math.round(o.v).toLocaleString('en-US')"
            X.tw(f'(()=>{{const o={{v:{c["count"]}}}, el=document.querySelector("{q} .n"); tl.to(o, {{v:{c["fig"]}, duration:0.9, ease:"power3.out", onUpdate:()=>{{el.textContent={js};}}}}, {max(t, tc - 0.25):.3f});}})();')
            X.sfx(tc - 0.25, "count")
        if c.get("bar"):
            X.tw(f'tl.from("{q} .bar i", {{scaleX:0, duration:0.9, ease:"power3.inOut"}}, {tc:.3f});')
        X.sfx(tc, "hit")
        if k + 1 < len(calls):   # the next callout replaces this one
            tn = _T(X, b, f"at_call{k + 1}", t, t + 0.2 + (k + 1) * (d - 0.4) / len(calls))
            X.tw(f'tl.to("{q}", {{opacity:0, y:-20, duration:0.3, ease:"power2.in"}}, {tn - 0.5:.3f});')
    if b.get("list"):
        L = b["list"]; n = len(L["items"][:8]); at = L.get("at") or []
        X.tw(f'tl.from("{s} .d-list .ttl", {{x:-24, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
        step = min(0.35, (d - 0.8) / max(n, 1))
        for j in range(n):
            tj = float(X.T(at[j], t)) if j < len(at) else t + 0.25 + j * step
            X.tw(f'tl.from("{s} .d-list .it[data-j=\'{j}\']", {{x:-30, opacity:0, duration:0.45, ease:"expo.out"}}, {max(t, tj - 0.15):.3f});')
            X.sfx(tj - 0.1, "line")
    if b.get("trk"):
        tk = _T(X, b, "at_trk", t, t + 0.15)
        X.tw(f'tl.from("{s} .d-trk", {{scale:1.5, opacity:0, duration:0.35, ease:"expo.out"}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .d-trk .ch", {{opacity:0}}, {{keyframes:[{{opacity:1, duration:0.08}}, {{opacity:0.2, duration:0.08}}, {{opacity:1, duration:0.08}}], immediateRender:false}}, {tk + 0.3:.3f});')
        X.tw(f'tl.from("{s} .d-trk .lb", {{clipPath:"inset(0 100% 0 0)", duration:0.4, ease:"power3.out"}}, {tk + 0.25:.3f});')
        X.tw(f'tl.to("{s} .d-trk", {{x:{b["trk"].get("dx", 0)}, y:{b["trk"].get("dy", 0)}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.sfx(tk + 0.3, "lock")
    if b.get("say"):
        ts = _T(X, b, "at_say", t, (t + dst) if b.get("stamp") else t + 0.1)   # never on top of a stamp
        n = len(str(b["say"]).replace("|", "").replace("*", ""))
        X.tw(f'tl.from("{s} .d-say .rule", {{scaleX:0, duration:0.6, ease:"expo.out"}}, {max(t, ts - 0.2):.3f});')
        X.tw(f'tl.from("{s} .d-say .l .c", {{opacity:0, y:18, filter:"blur(10px)", duration:0.5, ease:"power3.out", stagger:{min(0.045, max(0.012, (d * 0.5) / max(n, 1))):.3f}}}, {ts:.3f});')
        X.sfx(ts, "enter")
    if b.get("tag"):
        X.tw(f'tl.from("{s} .d-tag", {{opacity:0, duration:0.4}}, {t + 0.2:.3f});')


def card(b, X, t, d, cid):
    """chapter card or outro: black, serif title (auto-fitted, up to 2 balanced lines), a mono line."""
    X.css("doc", CSS)
    if X.beat["i"] == 0: _persistent(X)
    P = X.portrait
    tpx, ttx = fit(b["title"], X.W - (128 if P else 240), 104 if P else 120, 56 if P else 64, maxlines=2, track=0.06)
    k = f'<div class="k">{X.rich(b.get("kicker", ""))}</div>' if b.get("kicker") else ""
    sub = f'<div class="s">{X.rich(b["sub"])}</div>' if b.get("sub") else ""
    m = f'<div class="m">{X.rich(b["meta"])}</div>' if b.get("meta") else ""
    X.clip(cid, t, d, f'<div class="in">{k}<div class="t" style="font-size:{tpx:.0f}px">{_chars(X, ttx)}</div><div class="hr"></div>{sub}{m}</div>', "scene d-card", 4)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .k", {{opacity:0, y:10, duration:0.4}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .t .c", {{opacity:0, x:(i, el, all)=>(i - (all.length - 1) / 2) * 30, filter:"blur(12px)", duration:0.6, ease:"expo.out", stagger:{min(0.04, 0.5 / max(len(ttx), 1)):.3f}}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .hr", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{s} .s, {s} .m", {{opacity:0, y:12, duration:0.5, stagger:0.1}}, {t + 0.35:.3f});')
    X.sfx(t + 0.05, "title")


# ---------------------------------------------------------------- effects in this style
# Every gallery effect rendered in doc sits in the same frame as the film: the letterbox bars carry the furniture
# (16:9: top bar = FX counter + effect name + show mark, a hairline and a mono metadata row; bottom bar = the spoken line
# as a film subtitle). In 9:16 the same pieces sit at the platform-safe positions (header 206, caption 1330, foot 1478).
FX_CSS = r"""
.ctx.dfx { pointer-events:none; }
.dfx .dfx-hd { position:absolute; left:96px; right:96px; top:30px; height:48px; display:flex; align-items:center; justify-content:space-between; gap:28px; color:#f4efe6; }
.dfx .dfx-l { display:flex; align-items:center; gap:18px; min-width:0; }
.dfx .dfx-id { display:flex; align-items:baseline; gap:12px; flex:none; }
.dfx .dfx-id small { font:500 16px var(--f-mono); letter-spacing:.32em; color:rgba(244,239,230,.62); }
.dfx .dfx-id .dg { display:inline-flex; font-family:var(--f-num); font-weight:700; font-size:42px; line-height:1; color:#f0a640; font-variant-numeric:lining-nums tabular-nums; }
.dfx .dfx-id .col { display:inline-block; height:1em; overflow:hidden; } .dfx .dfx-id .col span { display:block; height:1em; }
.dfx .dfx-dv { width:1px; height:30px; background:rgba(244,239,230,.35); flex:none; }
.dfx .dfx-nm { white-space:nowrap; overflow:hidden; color:#f4efe6; }
.dfx .dfx-nm b { font-family:var(--f-serif); font-weight:600; letter-spacing:.06em; }
.dfx .dfx-nm em { font-family:var(--f-numi); font-style:italic; opacity:.66; margin-left:.7em; }
.dfx .dfx-mk { flex:none; font:500 16px var(--f-mono); letter-spacing:.3em; color:rgba(244,239,230,.62); white-space:nowrap; }
.dfx .dfx-mk b { font:500 17px var(--f-body); letter-spacing:.12em; color:#f4efe6; margin-right:14px; }
.dfx .dfx-rl { position:absolute; left:96px; right:96px; top:88px; height:1px; background:rgba(244,239,230,.16); }
.dfx .dfx-ft { position:absolute; left:96px; right:96px; top:98px; display:flex; justify-content:space-between; gap:40px; font:400 16px/1.45 var(--f-mono); color:rgba(244,239,230,.58); letter-spacing:.04em; }
.dfx .dfx-ft > div { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0; }
.dfx .dfx-ft .tg { display:inline-block; border:1px solid rgba(244,239,230,.42); padding:0 8px; margin-right:12px; color:rgba(244,239,230,.85); letter-spacing:.1em; }
.dfx .dfx-capw { position:absolute; left:0; right:0; top:942px; height:138px; display:flex; align-items:center; justify-content:center; }
.ctx.dfx .cap { position:static; padding:0 120px; text-align:center; }
.ctx.dfx .cap > span { display:inline-block; background:none; padding:0; border-radius:0; max-width:none; font-family:var(--f-body); font-weight:500; line-height:1.3;
  color:#f4efe6; letter-spacing:.02em; text-shadow:0 1px 2px rgba(0,0,0,.6); }
.ctx.dfx .cap .em .emt { background:none; color:#f0a640; padding:0; } .ctx.dfx .cap .em .emb { display:none; }
.dfx .dfx-tg, .dfx .dfx-bg { display:none; }
/* 9:16: platform-safe positions; dark grounds get soft scrims, light grounds (paper / lemon) take the theme ink with a paper halo */
#root.v .dfx .dfx-hd { left:56px; right:56px; top:206px; }
#root.v .dfx .dfx-rl { display:none; }
#root.v .dfx .dfx-ft { top:1478px; left:56px; right:136px; flex-direction:column; gap:2px; font-size:17px; }
#root.v .dfx .dfx-capw { position:static; }
#root.v .ctx.dfx .cap { position:absolute; left:0; right:0; top:1330px; padding:0 120px; }
#root.v .ctx.dfx .cap > span { font-weight:600; text-shadow:0 2px 14px rgba(0,0,0,.85), 0 1px 2px #000; }
#root.v .dfx.dk .dfx-tg { display:block; position:absolute; left:0; right:0; top:0; height:520px; background:linear-gradient(180deg, rgba(0,0,0,.66), rgba(0,0,0,.58) 52%, rgba(0,0,0,0)); }
#root.v .dfx.dk .dfx-hd { text-shadow:0 1px 3px rgba(0,0,0,.8), 0 0 14px rgba(0,0,0,.6); }
#root.v .dfx.dk .dfx-bg { display:block; position:absolute; left:0; right:0; top:1230px; height:420px; background:linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.5) 35%, rgba(0,0,0,.5) 65%, rgba(0,0,0,0)); }
#root.v .dfx.lt .dfx-hd, #root.v .dfx.lt .dfx-nm, #root.v .dfx.lt .dfx-mk b { color:var(--fg); }
#root.v .dfx.lt .dfx-id small, #root.v .dfx.lt .dfx-mk, #root.v .dfx.lt .dfx-ft { color:var(--fg); }
#root.v .dfx.lt .dfx-hd { left:0; right:0; top:204px; height:64px; padding:0 56px; background:color-mix(in srgb, var(--bg) 94%, transparent); border-bottom:1px solid var(--line); }
#root.v .dfx.lt .dfx-id .dg { color:var(--accent); } #root.v .dfx.lt .dfx-nm em { opacity:1; color:var(--fg); } #root.v .dfx.lt .dfx-dv { background:var(--line); }
#root.v .dfx.lt .dfx-ft .tg { color:var(--fg); border-color:var(--muted); }
#root.v .ctx.dfx.lt .cap > span { color:var(--fg); text-shadow:0 0 3px var(--bg), 0 0 10px var(--bg), 0 0 20px var(--bg); }
#root.v .ctx.dfx.lt .cap .em .emt { color:var(--accent); }

/* ---- effect internals in the doc language: serif heads, mono tags, square corners, hairlines, one amber, graded pictures */
.fx .big { letter-spacing:.04em; }
.fx .sub { font-family:var(--f-mono); letter-spacing:.32em; }
.fx img:not(.mb), .fxv video:not([src*="shiba"]) { filter:saturate(.8) contrast(1.06) sepia(.07); }
/* tags & chips -> amber mono labels (the film's tracking label) */
.fx .mx-lab .mx-pill, .fx .pp-tag i, .fx .ff-lab b, .fx .sr-badge span, .fx .fg-band span, .fx .fg-l3 span, .fx .cv-tb em, .fx .ezlab em, .fx .sm .smrl, .fx .w3 .w3tag, .fx .w3 .w3mock {
  font-family:var(--f-mono); font-weight:600; letter-spacing:.08em; background:#f0a640; color:#14110c; border-radius:0; text-shadow:none; }
.fx .ff-lab b { font-size:28px; padding:4px 12px; }
/* boxes -> square, hairline-edged prints */
.fx .mx-card, .fx .mx-c, .fx .mx-t, .fx .mx-hl, .fx .cv-bz, .fx .cv-sbox, .fx .cv-ov, .fx .ff-box.card, .fx .ff-hole, .fx .sr-graph { border-radius:2px; }
.fx .mx-card, .fx .mx-c { box-shadow:0 0 0 1px rgba(244,239,230,.16), 0 3vmin 7vmin rgba(0,0,0,.55); }
.fx .mx-c .mx-tag, .fx .mx-idx { font-family:var(--f-mono); letter-spacing:.06em; font-weight:500; }
.fx .sr-graph { background:rgba(8,8,8,.72); box-shadow:inset 0 0 0 1px rgba(244,239,230,.18); }
.fx .sr-graph polyline, .fx .ff-mk rect, .fx .ff-mk ellipse { stroke:#f0a640; }
.fx .ff-mk rect, .fx .ff-mk ellipse { stroke-width:3; stroke-linecap:square; }
.fx .sr-head, .fx .sr-head::before, .fx .ff-lead, .fx .cv-prog { background:#f0a640; }
.fx .sr-head { width:1.5px; }
.fx .sr-badge b { -webkit-text-stroke:0; font-weight:800; text-shadow:0 4px 34px rgba(0,0,0,.65); }
.fx .sr-badge.fast b { color:#f0a640; }
.fx .ff-stamp { border-radius:0; background:rgba(8,8,8,.78); box-shadow:inset 0 0 0 1px rgba(244,239,230,.2); }
.fx .ff-stamp i, .fx .cv-tb i { color:#f0a640; }
.fx .fg-band { border:1.5px dashed rgba(240,166,64,.9); border-radius:0; }
/* lower thirds -> the film's: amber rule, serif name, no box */
.fx .fg-l3 b, .fx .pp-tag { background:none; border-radius:0; border-top:3px solid #f0a640; padding:10px 0 0; font-family:var(--f-serif); text-shadow:0 2px 14px rgba(0,0,0,.75), 0 1px 2px rgba(0,0,0,.6); }
.fx .pp-chip { font-family:var(--f-mono); font-weight:600; border-radius:0; }
.fx .pp-ring { border-width:3px; box-shadow:0 18px 40px rgba(0,0,0,.4); }
/* callout -> reticle + hairline leader + serif label on an amber rule */
.fx .dt { background:transparent; border:2px solid #f0a640; box-shadow:0 0 0 1px rgba(0,0,0,.35); width:3vmin; height:3vmin; margin:-1.5vmin; }
.fx .ld { height:1.5px; }
.fx .lb b { background:rgba(8,8,8,.62); font-family:var(--f-serif); font-weight:700; border-top:3px solid #f0a640; padding:.7vmin 1.4vmin .8vmin; color:#f4efe6; }
.fx .lb span { text-shadow:0 1px 6px rgba(0,0,0,.9), 0 0 2px #000; color:#f4efe6; }
/* 16:9: keep effect headlines that sit near the top edge out from under the 2.39 bar */
#root:not(.v) .fx .pxt { top:15.5%; }
#root:not(.v) .fx .mx-cap1 { margin-top:40px; }
/* cite: archive card */
.fx .ct-root .em .emb { background:#f0a640; border-radius:0; }
.fx .ct-kick { background:none; color:var(--fg); box-shadow:inset 0 0 0 1px color-mix(in srgb, var(--fg) 45%, transparent); font-family:var(--f-mono); font-weight:500; letter-spacing:.2em; }
.fx .cv-cap { border-left-width:3px; } .fx .cv-range { border-radius:0; font-weight:500; }
.fx .cv-t { font-family:var(--f-serif); }
/* maps & timelines -> Atlas: dotted full route under the drawn one, rule-topped figures, tick marks, a chapter bar on titles */
.fx .mr .rt0 { stroke:color-mix(in srgb, var(--fg) 45%, transparent); stroke-width:2; stroke-dasharray:1 9; }
.fx .mr .rt { stroke-width:3.5; }
.fx .mrc div { background:transparent; border:0; border-top:3px solid var(--accent); box-shadow:none; padding:1.1vmin .2vmin 0; font-family:var(--f-serif); color:var(--fg);
  text-shadow:0 0 .8vmin var(--bg), 0 0 1.6vmin var(--bg); }
.fx .tlw .tlr { height:.2vmin; margin-top:-.1vmin; } .fx .tlw .tlf { height:.3vmin; margin-top:-.15vmin; }
.fx .tlw .tlm i { border-radius:0; border:0; width:.45vmin; height:3.6vmin; left:-.22vmin; top:-1.8vmin; background:var(--fg); }
.fx .tlw .tlm.last i { background:var(--accent); width:.7vmin; left:-.35vmin; }
.fx .tlw .tlm .tlc { font-family:var(--f-serif); font-weight:600; }
.fx .w3 .w3t::before { content:''; position:absolute; left:-24px; top:.16em; bottom:.16em; width:4px; background:var(--accent); }
.fx .w3 .w3n { letter-spacing:.12em; }
.fx .ao .aol i { border-radius:0; }
.fx .ao .aob, .fx .ao .aoa { stroke-width:2; }
.fx .sm .smp b { font-family:var(--f-serif); }
.fx .ezlab strong { letter-spacing:.04em; }
"""

STYLE["css"] = STYLE.get("css", "") + FX_CSS     # style css lands after every effect's own css, so these win ties


def _fx_name(p):
    """'#2 2.5D 照片视差 · Photo Parallax' -> ('2.5D 照片视差', 'Photo Parallax')."""
    lab = re.sub(r"^(#\d+|[A-Z]\d+)\s+", "", str(p.get("label") or "").strip())
    if not lab: return str(p.get("fxid") or p.get("fx", "")), ""
    zh, _, en = lab.partition(" · ")
    return zh.strip(), en.strip()


def _bg_light(sty):
    m = re.search(r"--bg:(#[0-9a-fA-F]{6})", sty or "")
    if not m: return False
    r, g, b = (int(m.group(1)[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.5


def FX_FRAME(X, cid, t, d, p, parts):
    """the doc frame around a gallery effect (see FX_CSS). Called by aefx for every effect beat with a spoken line."""
    P = X.portrait
    i = X.beat["i"]
    a, z = f"{i:02d}", f"{i + 1:02d}"
    cols = "".join(f'<span class="col"><span>{x}</span><span>{y}</span></span>' for x, y in zip(a, z))
    zh, en = _fx_name(p)
    mark_w = 140 if P else 380
    room = (X.W - 112 - 130 - 40 - mark_w - 28) if P else (X.W - 192 - 150 - 40 - mark_w - 28)
    # effect name: Chinese serif + English italic on one line; the English goes first when it does not fit
    zpx = 26.0
    if em(zh) * zpx + (em(en) * 0.62 * zpx + 0.7 * zpx if en else 0) > room * 0.94:
        en = ""
        zpx = max(16.0, min(26.0, room * 0.94 / max(em(zh), 1)))
    name = f'<b style="font-size:{zpx:.0f}px">{X.rich(zh)}</b>' + (f'<em style="font-size:{zpx * 0.86:.0f}px">{X.rich(en)}</em>' if en else "")
    topic = "" if P else parts["topic"]
    mark = f'<div class="dfx-mk"><b>第九顶帽子</b>{topic}</div>'
    fxid = X.rich(p.get("fxid") or p.get("fx", ""))
    ref = X.rich(p.get("ref", ""))
    src = f'来源：{parts["src"]}' if parts["src"] else ""
    foot = f'<div><span class="tg">{fxid}</span>{ref}</div><div>{src}</div>'
    # caption: the film's subtitle. 16:9 sits in the bottom bar (one line 34 px, two lines 30 px); 9:16 keeps aefx's fit
    n = len(parts["cap_lines"])
    cpx = parts["cap_px"] if P else (min(34.0, parts["cap_px"]) if n == 1 else min(30.0, parts["cap_px"] * 1.07))
    light = _bg_light(parts["sty"]) and not parts["photo"]
    X.used_text.update(f"FX{a}{z}第九顶帽子来源：" + zh + en)
    inner = (f'<div class="dfx-tg"></div><div class="dfx-bg"></div>'
             f'<div class="dfx-hd"><div class="dfx-l"><div class="dfx-id"><small>FX</small><span class="dg">{cols}</span></div><i class="dfx-dv"></i>'
             f'<div class="dfx-nm">{name}</div></div>{mark}</div><i class="dfx-rl"></i><div class="dfx-ft">{foot}</div>'
             f'<div class="dfx-capw"><div class="cap"><span style="font-size:{cpx:.0f}px">{parts["cap"]}</span></div></div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx dfx {'lt' if light else 'dk'}", 45, track=20, sty=parts["sty"])
    q = f"#{cid}c"
    X.tw(f'tl.to("{q} .dfx-id .col span", {{yPercent:-100, duration:0.5, ease:"expo.inOut", stagger:0.06}}, {t + 0.05:.3f});')
    X.tw(f'tl.set("{q} .dfx-id .col span:first-child", {{visibility:"hidden"}}, {t + 0.7:.3f});')   # the rolled-out digit is gone, not just masked
    X.tw(f'tl.from("{q} .dfx-nm", {{clipPath:"inset(0 100% 0 0)", duration:0.5, ease:"power3.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{q} .dfx-ft", {{opacity:0, duration:0.4}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{q} .cap > span", {{opacity:0, duration:0.16, ease:"none"}}, {t + 0.08:.3f});')


SCENES = {"shot": shot, "card": card}
