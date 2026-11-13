"""screen · AI 工具台 —— 给 AI 工具 / AI 变现类口播的桌面界面语言（新粗野主义桌面 UI）。
对标 Linear / Raycast / Arc 的发布片、OpenAI DevDay 的数据图、归藏的产品视频：暖白桌面底 #f3efe6 + 轻颗粒，
内容全部装在"窗口"里——1.5 px 墨线描边、彩色标题条（番茄 / 钴蓝 / 薄荷 / 芥黄）、硬投影的仪表盘、终端、定价页、
预测图、命令面板、截图墙；顶部一条菜单栏（频道 · 栏目 · 页码），底部一排 Dock（五个应用图标 + 来源状态栏）；
一个会移动、会点击的光标把视线带过去；数字用表格数字滚动，唯一强调色是钴蓝 #2f5bff。字幕是一条系统通知弹窗
（白卡、墨线、硬投影、应用小图标），每句在菜单栏下和 Dock 上方之间换位置；主持人只出现在一个视频通话小窗里。
全部 HTML/CSS/SVG，界面是通用的，不仿任何品牌。

场景（SCENES）：dash 指标仪表盘 · api 终端 + 吞吐计数 · pricing 定价卡 + 百人格 · forecast 预测图 + 通知 ·
shots 截图墙 · palette 命令面板判断句 · outro 应用图标落版。每页有镜头调度；横竖屏各自排版。

输入自适应（每个场景都一样）：
- 文字：1 个字到一整句都行。按框自动定字号（有上下限），用 jieba 分词做平衡断行，不在词中间断，数字 + 单位不拆开；
  `|` 可以强制换行，`*重点*` 标青柠色。
- 列表：项数可变（曲线点 2–12、方案 1–8、图例 1–6、柱子 1–6、命令结果 1–12+），布局和字号随项数变；放不下时收成「还有 N 项」。
- 图片 / 截图：0 到很多张，任意比例。网格按张数和平均比例自动排列（最后一行居中），超过上限显示「+N」；
  每张 `{"src", "focus": [x%, y%], "fit": "cover|contain|auto"}`，auto 时比例差太多就整图放下 + 同图模糊垫底。
  0 张时：截图墙显示骨架卡片，其余场景用自带内容。
"""
import math, struct
from pathlib import Path
from h9 import captions

INK = "#1b1b1f"
ACC = {"tomato": "#ff5a3c", "cobalt": "#2f5bff", "mint": "#19c39a", "sun": "#ffc21a"}

STYLE = {
    "name": "AI 工具台", "en": "Screen", "benchmarks": ["Linear / Raycast 发布片", "OpenAI DevDay 数据图", "归藏产品视频", "Neo-brutalist desktop UI"],
    "tokens": {
        "bg": "#f3efe6", "fg": INK, "muted": "#55555f", "accent": "#2f5bff", "accent2": "#ff5a3c", "alert": "#e8432a",
        "line": "rgba(27,27,31,.16)", "paper": "#f3efe6", "ink": INK, "card": "#ffffff", "card-fg": INK,
        "lime": "#2f5bff", "violet": "#ff5a3c", "dim": "#e6e2d8", "surf": "#ffffff", "surf2": "#f4f1ea",
        "tomato": ACC["tomato"], "cobalt": ACC["cobalt"], "mint": ACC["mint"], "sun": ACC["sun"],
        "cap-bg": "#ffffff", "cap-fg": INK, "cap-size": "38px", "cap-weight": "700", "cap-pad": "16px 30px 18px 22px",
        "cap-radius": "14px", "cap-shadow": "none", "cap-bottom": "150px", "cap-em": "#2f5bff",
        "punch-top": "70%", "punch-size": "68px",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": ["inter", "noto-sans-sc"], "mono": "jetbrains-mono", "num": "jetbrains-mono"},
    "motion": {"ease": "back.out(1.4)", "dur": 0.35, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.06})],
    # the host only ever appears inside a "video call" window (see .mascot css), never as a free sticker
    "mascot": {"mode": "cameo", "frame": "call", "landscape": {"right": 88, "bottom": 236, "h": 300}, "portrait": {"right": 70, "bottom": 600, "h": 290}},
    "sfx": {"transition": ("whoosh_soft", 0.3), "enter": ("whoosh_soft", 0.28), "pop": ("pop", 0.4), "hit": ("hit", 0.35),
            "count": ("type", 0.25), "click": ("click", 0.45), "type": ("type", 0.3), "mascot": ("whoosh_soft", 0.3), "line": ("click", 0.3)},
    "css": r"""
/* caption = a system notification toast: white card, ink outline, hard shadow, an app chip; it alternates top / above the dock */
.st-screen .cap .cp { border:1.5px solid #1b1b1f; box-shadow:8px 8px 0 #1b1b1f; text-align:left; line-height:1.3; }
.st-screen .cap .cp::before { content:""; display:inline-block; width:.82em; height:.82em; margin-right:.55em; vertical-align:-.08em;
  border-radius:.22em; border:1.5px solid #1b1b1f; background:#ffc21a; }
.st-screen .cap-punch .cp { font-weight:800; }
#root.v .clip.cap { padding-left:150px; padding-right:124px; text-align:right; }
#root.h .clip.cap { padding-right:90px; padding-left:90px; text-align:var(--cap-align, right); }
/* the host sits inside a small video-call window drawn by the scene (callwin) */
.st-screen .mascot { object-fit:contain; object-position:50% 100%; }
""",
    # effect cards (aefx): dark mode · light mode · indigo · lime ground — four "app themes" of the same product UI
    # effect cards (aefx): four "app themes" of the same desktop — warm wallpaper · cool wallpaper · tomato · sun
    "fx_themes": {
        "paper": {"bg": "#ffffff", "fg": "#1b1b1f", "muted": "#55555f", "accent": "#2f5bff", "card": "#ffffff", "card-fg": "#1b1b1f", "line": "rgba(27,27,31,.22)"},
        "ink":   {"bg": "#dfe8ff", "fg": "#1b1b1f", "muted": "#4a4f66", "accent": "#e8432a", "card": "#ffffff", "card-fg": "#1b1b1f", "line": "rgba(27,27,31,.22)"},
        "red":   {"bg": "#ff5a3c", "fg": "#1b1b1f", "muted": "#4a1f14", "accent": "#ffffff", "card": "#ffffff", "card-fg": "#1b1b1f", "line": "rgba(27,27,31,.3)"},
        "lemon": {"bg": "#ffc21a", "fg": "#1b1b1f", "muted": "#4d3a00", "accent": "#2f5bff", "card": "#ffffff", "card-fg": "#1b1b1f", "line": "rgba(27,27,31,.3)"},
    },
}

CSS = r"""
.st-screen .em .emb { display:none; } .sc .em .emt { color:var(--cobalt); }
.sc { position:absolute; inset:0; background:linear-gradient(165deg, #f3efe6 0%, #ece9ee 45%, #dfe8ff 100%); overflow:hidden; }
.sc .bgfx { position:absolute; inset:0; background:radial-gradient(circle at 2px 2px, rgba(27,27,31,.16) 1.6px, transparent 2.2px) 0 0/32px 32px; }
.sc .cam { position:absolute; inset:0; }
/* menu bar */
.sc-hd { position:absolute; left:0; right:0; top:0; height:58px; display:flex; align-items:center; justify-content:space-between; z-index:6; padding:0 34px;
  background:rgba(255,255,255,.86); border-bottom:1.5px solid #1b1b1f; font-family:var(--f-body); font-size:24px; color:#1b1b1f; }
.sc-hd .l { display:flex; align-items:center; gap:14px; } .sc-hd .l i { width:22px; height:22px; border-radius:6px; background:#ff5a3c; border:1.5px solid #1b1b1f; }
.sc-hd .l b { font-weight:800; } .sc-hd .l span { color:#1b1b1f; font-weight:500; }
.sc-hd .r { display:flex; align-items:center; gap:16px; font-family:var(--f-mono); font-size:24px; color:#1b1b1f; white-space:nowrap; }
.sc-hd .r em { font-style:normal; color:#fff; background:#1b1b1f; border-radius:8px; padding:2px 12px; }
#root.v .sc-hd { top:64px; height:64px; padding:0 40px; }
/* dock: five app icons (the open one has a dot) + the source as the dock's status text */
.dock { position:absolute; z-index:7; display:flex; align-items:center; gap:18px; padding:14px 22px; background:rgba(255,255,255,.9);
  border:1.5px solid #1b1b1f; border-radius:24px; box-shadow:8px 8px 0 #1b1b1f; }
.dock .ic { position:relative; flex:none; width:80px; height:80px; border-radius:20px; border:1.5px solid #1b1b1f; display:grid; place-items:center; }
.dock .ic svg { width:46px; height:46px; }
.dock .ic.on::after { content:""; position:absolute; left:50%; bottom:-12px; width:8px; height:8px; margin-left:-4px; border-radius:50%; background:#1b1b1f; }
.dock .src { flex:1; min-width:0; font-family:var(--f-mono); font-size:24px; line-height:1.28; color:#1b1b1f; border-left:1.5px solid #1b1b1f; padding-left:18px; }
.dock .src b { font-weight:700; }
#root.v .dock { left:50%; transform:translateX(-50%); top:1752px; height:128px; box-sizing:border-box; }
/* 9:16 source: a status line just above the platform's bottom bar (readable band ends at y 1504; right 120 px kept clear) */
.pst { position:absolute; left:40px; width:880px; top:1350px; z-index:6; font-family:var(--f-mono); font-size:22px; line-height:1.3; color:#1b1b1f;
  background:rgba(255,255,255,.82); border:1.5px solid #1b1b1f; border-radius:10px; padding:6px 14px; box-sizing:border-box; }
.pst b { font-weight:800; margin-right:.4em; }
.stub { position:absolute; left:110px; width:860px; top:1560px; height:300px; z-index:5; rotate:-1.2deg; background:#ffffff; border:1.5px solid #1b1b1f;
  border-radius:14px; box-shadow:8px 8px 0 #1b1b1f; overflow:hidden; }
.stub .sb { height:44px; background:var(--mint); border-bottom:1.5px solid #1b1b1f; display:flex; gap:9px; align-items:center; padding:0 16px; }
.stub .sb i { width:15px; height:15px; border-radius:50%; background:#fff; border:1.5px solid #1b1b1f; }
.stub u { position:absolute; left:28px; height:12px; border-radius:6px; background:#e6e2d8; }
#root.h .dock { left:50%; transform:translateX(-50%); width:1360px; bottom:18px; height:104px; box-sizing:border-box; padding:10px 20px; }
#root.h .dock .ic { width:72px; height:72px; } #root.h .dock .ic svg { width:40px; height:40px; }
/* windows: white, ink outline, 14 px radius, hard offset shadow, a coloured title bar */
.win { position:absolute; border-radius:14px; background:#ffffff; border:1.5px solid #1b1b1f; box-shadow:8px 8px 0 #1b1b1f; overflow:hidden; }
.win .tb { position:relative; z-index:3; height:46px; display:flex; align-items:center; gap:9px; padding:0 16px; border-bottom:1.5px solid #1b1b1f; background:var(--bar, #ff5a3c);
  font-family:var(--f-mono); font-size:26px; font-weight:700; color:#1b1b1f; white-space:nowrap; }
.win .tb i { width:15px; height:15px; border-radius:50%; background:#fff; border:1.5px solid #1b1b1f; flex:none; }
.win .tb span { margin-left:10px; overflow:hidden; text-overflow:ellipsis; }
.win .tb .tag { margin-left:auto; color:#fff; background:#1b1b1f; border-radius:999px; padding:1px 12px; font-size:24px; }
.win .bd { position:absolute; left:0; right:0; top:46px; bottom:0; }
.sc .ab { position:absolute; }
.sc .ft { display:inline-block; white-space:nowrap; vertical-align:baseline; }
.sc .lbl { font-family:var(--f-body); font-weight:600; color:#3a3a44; letter-spacing:.01em; }
.sc .num { font-family:var(--f-num); font-weight:800; font-variant-numeric:tabular-nums; letter-spacing:-.05em; color:#1b1b1f; line-height:1; white-space:nowrap; }
.sc .mono { font-family:var(--f-mono); }
.sc .lime { color:var(--cobalt); }
.sc .cur { position:absolute; left:0; top:0; width:64px; height:76px; z-index:8; }
.sc .cur svg { display:block; width:64px; height:76px; overflow:visible; }
.sc .cur .rp { position:absolute; left:-30px; top:-30px; width:64px; height:64px; border-radius:50%; border:4px solid #1b1b1f; opacity:0; }
.sc .caret { display:inline-block; width:4px; height:1.0em; background:var(--cobalt); vertical-align:-.12em; margin-left:4px; }
/* adaptive image grid */
.sc .gr { position:absolute; }
.sc .ph { position:absolute; border-radius:10px; overflow:hidden; background:#f4f1ea; border:1.5px solid #1b1b1f; }
.sc .ph img { position:absolute; inset:0; width:100%; height:100%; display:block; }
.sc .ph img.bk { object-fit:cover; filter:blur(18px) brightness(.9) saturate(.8); transform:scale(1.15); }
.sc .ph .more { position:absolute; inset:0; display:grid; place-items:center; background:rgba(255,255,255,.8); font-family:var(--f-num); font-weight:700; color:#1b1b1f; }
.sc .ph .cap2 { position:absolute; left:10px; bottom:8px; right:10px; font-size:26px; color:#1b1b1f; background:rgba(255,255,255,.85); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sc .ph.sk { background:#fbfaf6; }
.sc .ph.sk i { position:absolute; left:10%; height:8%; border-radius:6px; background:#e6e2d8; }
.sc .ph .hl { position:absolute; inset:0; border-radius:10px; border:4px solid var(--cobalt); opacity:0; }
"""

CURSOR = ('<div class="cur"><i class="rp"></i><svg viewBox="0 0 34 40"><path d="M3 2 L3 31 L10.5 24.5 L15.5 36 L21 33.5 L16 22.5 L26 22.5 Z" '
          'fill="#1b1b1f" stroke="#fff" stroke-width="2.2" stroke-linejoin="round"/></svg></div>')

DOCK_ICONS = [   # (colour, glyph) — generic app icons: chart, terminal, price tag, bars, command
    ("cobalt", '<path d="M8 36 L18 24 L26 30 L38 12" fill="none" stroke="#1b1b1f" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'),
    ("tomato", '<path d="M9 14 L19 23 L9 32 M23 33 H37" fill="none" stroke="#1b1b1f" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'),
    ("mint",   '<path d="M8 22 V9 H21 L38 26 L25 39 Z" fill="none" stroke="#1b1b1f" stroke-width="4" stroke-linejoin="round"/><circle cx="15" cy="16" r="2.6" fill="#1b1b1f"/>'),
    ("sun",    '<path d="M10 38 V26 M19 38 V18 M28 38 V22 M37 38 V10" stroke="#1b1b1f" stroke-width="5" stroke-linecap="round"/>'),
    ("cobalt", '<path d="M16 12 a5 5 0 1 0 0 10 h16 a5 5 0 1 0 -5 -5 v16 a5 5 0 1 0 5 -5 h-16 a5 5 0 1 0 5 5 v-16 a5 5 0 1 0 -5 5" fill="none" stroke="#1b1b1f" stroke-width="3.4"/>'),
]
SCENE_ICON = {"dash": 0, "api": 1, "pricing": 2, "forecast": 3, "shots": 0, "palette": 4, "outro": 4}

# ---------------------------------------------------------------- text fitting
NUMS = set("0123456789零〇一二三四五六七八九十百千万亿两.,%+-×≈~")
UNITS = set("年月日号亿万元个家人倍次分秒天周岁")
PUNCT = set("，。、：；！？）》」’”,.:;!?)%")


def _w(ch):
    if ord(ch) > 0x2E80: return 1.0
    if ch == " ": return 0.28
    if ch in ".,:;'!|": return 0.3
    if ch.isdigit(): return 0.62
    if ch == "%": return 0.9
    if ch.isupper(): return 0.66
    return 0.55


def est_w(s):
    """width in em, *markers* and | ignored."""
    return sum(_w(c) for c in str(s) if c not in "*|")


def _tokens(s):
    """unbreakable pieces: jieba words, Latin words, numerals + their unit, *emphasis* runs; punctuation sticks to the left."""
    try:
        import jieba  # noqa: F401
        from h9 import core
        raw = core.words(s)
    except Exception:
        raw = list(s)
    out = []
    for tk in raw:
        if not tk: continue
        if out and (all(c in NUMS for c in tk) and all(c in NUMS for c in out[-1]) or
                    tk[0] in UNITS and all(c in NUMS for c in out[-1]) or all(c in PUNCT for c in tk)):
            out[-1] += tk
        else:
            out.append(tk)
    merged, em = [], False        # keep *...* together
    for tk in out:
        if em: merged[-1] += tk
        else: merged.append(tk)
        if tk.count("*") % 2: em = not em
    return merged


def _partition(toks, n):
    """split tokens into n lines minimising the widest line (dp, n small)."""
    ws = [est_w(t) for t in toks]; m = len(toks)
    pre = [0]
    for w in ws: pre.append(pre[-1] + w)
    INF = float("inf")
    best = [[INF] * (m + 1) for _ in range(n + 1)]; cut = [[0] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for k in range(1, n + 1):
        for j in range(1, m + 1):
            for i in range(k - 1, j):
                seg = pre[j] - pre[i] - (0.28 if toks[i].startswith(" ") else 0)
                v = max(best[k - 1][i], seg)
                if v < best[k][j]: best[k][j], cut[k][j] = v, i
    lines, j = [], m
    for k in range(n, 0, -1):
        i = cut[k][j]; lines.append("".join(toks[i:j]).strip()); j = i
    return [x for x in reversed(lines) if x], best[n][m]


def fit(X, s, w, h, mx, mn=14, lines=3, lh=1.18, cls=""):
    """auto-fit text into a w×h box: font size in [mn, mx], balanced lines (never inside a word), `|` forces a break.
    returns (html, px, n_lines)."""
    s = str(s or "").strip()
    if not s: return "", mn, 0
    segs = [x.strip() for x in s.split("|") if x.strip()]
    best = None
    for n in range(len(segs), max(lines, len(segs)) + 1):
        # distribute the n lines over the forced segments by width
        out = []; widest = 0
        extra = n - len(segs); widths = [est_w(x) for x in segs]
        alloc = [1] * len(segs)
        for _ in range(extra):
            k = max(range(len(segs)), key=lambda q: widths[q] / alloc[q]); alloc[k] += 1
        for seg, a in zip(segs, alloc):
            toks = _tokens(seg); a = min(a, len(toks))
            ls, wd = _partition(toks, a)
            out += ls; widest = max(widest, wd)
        nl = len(out)
        px = min(mx, w / max(widest, 0.5), h / (nl * lh))
        if best is None or px > best[1] * 1.15: best = (out, px, nl)    # more lines only if it buys ≥15% size
    ls, px, nl = best
    px = max(mn, math.floor(px))
    X.used_text.update(s)
    html = "<br>".join(X.rich(x) for x in ls)
    return f'<span class="ft {cls}" style="font-size:{px}px; line-height:{lh}">{html}</span>', px, nl


def fit_px(s, w, mx, mn=12):
    return max(mn, min(mx, math.floor(w / max(est_w(s), 0.5))))


# ---------------------------------------------------------------- images
def _img_size(p):
    try:
        from PIL import Image
        with Image.open(p) as im: return im.size
    except Exception:
        pass
    try:
        b = Path(p).read_bytes()[:64]
        if b[:8] == b"\x89PNG\r\n\x1a\n": return struct.unpack(">II", b[16:24])
    except Exception:
        pass
    return (16, 10)


def norm_images(X, imgs):
    out = []
    for it in imgs or []:
        d = {"src": it} if isinstance(it, str) else dict(it)
        p = Path(d["src"]); p = p if p.is_absolute() else X.src / p
        w, h = _img_size(p)
        d["ar"] = w / max(h, 1); d["url"] = X.asset(d["src"])
        out.append(d)
    return out


def grid_rects(n, W, H, gap, ar=1.6):
    """cols × rows that waste the least area for images of aspect ar; last row centred."""
    best = None
    for cols in range(1, n + 1):
        rows = math.ceil(n / cols)
        cw, ch = (W - gap * (cols - 1)) / cols, (H - gap * (rows - 1)) / rows
        if cw < 40 or ch < 30: continue
        used = min(cw, ch * ar) * min(ch, cw / ar) * n
        if best is None or used > best[0]: best = (used, cols, rows, cw, ch)
    if not best: best = (0, n, 1, (W - gap * (n - 1)) / n, H)
    _, cols, rows, cw, ch = best
    rects = []
    for k in range(n):
        r, c = divmod(k, cols)
        inrow = min(cols, n - r * cols)
        x0 = (W - (inrow * cw + (inrow - 1) * gap)) / 2
        rects.append((x0 + c * (cw + gap), r * (ch + gap), cw, ch))
    return rects


def gallery(X, imgs, W, H, gap=14, cap_max=None, cls="gr", sty=""):
    """adaptive grid of images / screenshots inside a W×H box; 0 images -> skeleton cards."""
    imgs = norm_images(X, imgs)
    cap_max = cap_max or (16 if not X.portrait else 12)
    more = max(0, len(imgs) - cap_max)
    show = imgs[:cap_max]
    if not show:
        rects = grid_rects(6, W, H, gap, 1.4)
        cells = "".join(f'<div class="ph sk" data-k="{k}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">'
                        f'<i style="top:14%; width:46%"></i><i style="top:30%; width:72%; background:#ece8df"></i><i style="top:44%; width:60%; background:#ece8df"></i>'
                        f'<i style="top:70%; width:34%; height:12%; background:rgba(47,91,255,.18)"></i></div>' for k, (x, y, w, h) in enumerate(rects))
        return f'<div class="{cls}" style="width:{W}px; height:{H}px; {sty}">{cells}</div>', 6
    ars = sorted(d["ar"] for d in show); ar = ars[len(ars) // 2]
    rects = grid_rects(len(show), W, H, gap, ar)
    cells = []
    for k, (d, (x, y, w, h)) in enumerate(zip(show, rects)):
        fx, fy = (d.get("focus") or [50, 50])[:2]
        fitm = d.get("fit", "auto")
        if fitm == "auto": fitm = "contain" if max(d["ar"], w / h) / min(d["ar"], w / h) > 1.35 else "cover"
        bk = f'<img class="bk" src="{d["url"]}" alt="">' if fitm == "contain" else ""
        img = f'<img class="fg" src="{d["url"]}" alt="" style="object-fit:{fitm}; object-position:{fx}% {fy}%">'
        cap = f'<div class="cap2">{X.rich(d["label"])}</div>' if d.get("label") and h > 90 else ""
        mo = (f'<div class="more" style="font-size:{min(60, h * 0.32):.0f}px">+{more}</div>' if more and k == len(show) - 1 else "")
        cells.append(f'<div class="ph" data-k="{k}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">{bk}{img}{cap}{mo}<i class="hl"></i></div>')
    X.used_text.update(f"+{more}")
    return f'<div class="{cls}" style="width:{W}px; height:{H}px; {sty}">{"".join(cells)}</div>', len(show)


# ---------------------------------------------------------------- shared helpers
def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def furn(X, b):
    """menu bar (channel · section · case · page) + the dock (five app icons, this scene's one open) with the source as its
    status text. Also moves the caption toast for this beat: even beats under the menu bar, odd beats above the dock."""
    X.css("screen", CSS)
    i, n = X.beat["i"], X.beat["n"]
    t = X.beat["t"]
    meta = X.v.get("meta", {})
    src = b.get("src", meta.get("src", ""))
    sec, case = meta.get("section", "AI 工具台"), meta.get("case", "")
    X.used_text.update(sec + case + src + "0123456789/来源：")
    on = SCENE_ICON.get(b.get("scene", ""), 0)
    icons = "".join(f'<i class="ic{" on" if k == on else ""}" style="background:var(--{c})"><svg viewBox="0 0 46 46">{g}</svg></i>' for k, (c, g) in enumerate(DOCK_ICONS))
    top = i % 2 == 0
    if X.portrait:
        captions.place(X, t, bottom=1920 - 200 - 82 if top else 424)     # both clear of the platform chrome (top 200 px / bottom 400 px)
    else:   # 16:9: always just above the dock, alternating right / left so it never sits on the same window twice
        captions.place(X, t, bottom=132, align="right" if top else "left")
    X.tw(f'tl.fromTo("#root .clip.cap .cp", {{x:420, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"back.out(1.4)", immediateRender:false}}, {t + 0.02:.3f});')
    hd = (f'<div class="sc-hd" data-safe="ignore"><div class="l"><i></i><b>{X.rich(X.channel)}</b><span>{X.rich(sec)}</span></div>'
          f'<div class="r">{X.rich(case)}<em>{i + 1:02d}/{n:02d}</em></div></div>')
    if X.portrait:   # 9:16: the Dock is decoration in the platform's bottom bar; the source is a status line above the safe line
        st = f'<div class="pst">{"<b>来源</b> " + X.rich(src) if src else ""}</div>' if src else ""
        stub = ('<div class="stub" data-safe="ignore"><div class="sb"><i></i><i></i><i></i></div>'
                + "".join(f'<u style="top:{70 + 30 * k}px; width:{w}%"></u>' for k, w in enumerate((62, 84, 48, 72, 56, 80)))
                + '</div>')      # a minimised window behind the Dock: keeps the platform's bottom bar alive, carries no text
        return hd + st + stub + f'<div class="dock">{icons}</div>'
    return hd + f'<div class="dock">{icons}<div class="src">{"<b>来源</b> " + X.rich(src) if src else ""}</div></div>'


def dock_xy(X, k):
    """centre of dock icon k in frame px (windows open from / close into it)."""
    return (300 + 120 * k, 1400) if X.portrait else (336 + 90 * k, 1010)   # 9:16: from above the safe line, toward the Dock


def callwin(X, b):
    """the video-call window the host appears in (only when the film has a host and this beat shows it)."""
    if not X.v.get("meta", {}).get("mascot") or not (b.get("host") or b.get("scene") == "outro"):
        return ""
    m = STYLE["mascot"]["portrait" if X.portrait else "landscape"]
    hgt = m["h"]; x = X.W - m["right"] - hgt - 18; y = X.H - m["bottom"] - hgt - 46 - 4
    X.used_text.update("call · host●")
    body = '<div class="ab mono" style="left:18px; bottom:12px; font-size:26px; font-weight:700; color:#1b1b1f; z-index:2"><b style="color:#e8432a">●</b> live</div>'
    return win(X, "call", "call", body, sty=box(x, y, hgt + 36, hgt + 46 + 22) + "; background:#f4f1ea", bar="mint", tilt=0)


def win(X, cls, title, body, tag="", sty="", bar="tomato", tilt=0.0):
    tg = f'<b class="tag">{X.rich(tag)}</b>' if tag else ""
    rot = f" rotate:{tilt:.2f}deg;" if tilt else ""
    return (f'<div class="win {cls}" style="{sty};--bar:var(--{bar});{rot}"><div class="tb"><i></i><i></i><i></i><span data-layout-allow-overlap data-layout-allow-occlusion>{X.rich(title)}</span>{tg}</div>'
            f'<div class="bd">{body}</div></div>')


def box(x, y, w, h): return f"left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px"


def fmt_num(v, dec=0):
    return f"{v:,.{dec}f}" if dec else f"{round(v):,}"


def counter(X, sel, t, a, b, dur=1.0, dec=0, ease="power3.out", suffix=""):
    """the number types in: its final digits appear left to right and land at t + dur (when the narration says it)."""
    full = (f"{b:,.{dec}f}" if dec else f"{round(b):,}") + suffix
    X.used_text.update("0123456789.,_" + full)
    td = min(dur, 0.09 * len(full) + 0.15)
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{sel}"), s={full!r}; el.textContent="_"; tl.to(o, {{v:s.length, duration:{td:.2f}, ease:"steps({len(full)})", '
         f'onUpdate:()=>{{const k=Math.round(o.v); el.textContent=s.slice(0, k)+(k<s.length?"_":"");}}}}, {t + dur - td:.3f});}})();')


def rise(X, sel, t, st=0.08, dur=0.35, icon=0):
    """windows open out of their dock icon: scale from the icon, snap into place (back.out 1.4, 0.35 s)."""
    ix, iy = dock_xy(X, icon)
    X.tw(f'(()=>{{document.querySelectorAll("{sel}").forEach((el,k)=>{{const x=parseFloat(el.style.left)+parseFloat(el.style.width)/2, y=parseFloat(el.style.top)+parseFloat(el.style.height)/2;'
         f'tl.from(el, {{x:{ix}-x, y:{iy}-y, scale:0.06, opacity:0, duration:{dur}, ease:"back.out(1.4)"}}, {t:.3f}+k*{st});}});}})();')


def drag_in(X, s, wsel, wbox, t, dx, dy, dur=0.45):
    """the cursor grabs a window by its title bar off to the side and drags it into place."""
    gx, gy = wbox[0] + min(220, wbox[2] * 0.3), wbox[1] + 22
    X.tw(f'tl.fromTo("{wsel}", {{x:{dx}, y:{dy}}}, {{x:0, y:0, duration:{dur}, ease:"back.out(1.4)"}}, {t + 0.15:.3f});')
    return [(t, gx + dx, gy + dy, True), (t + 0.15 + dur, gx, gy, False)]


def tiles_in(X, sel, t, n):
    X.tw(f'tl.from("{sel} .ph", {{y:30, opacity:0, scale:0.92, duration:0.55, ease:"expo.out", stagger:{min(0.08, 0.9 / max(n, 1)):.3f}}}, {t:.3f});')


def shots(X, sel, t, d, keys):
    """camera choreography: keys = [(time, scale, fx, fy)], fx/fy = point to centre (0–1). expo.inOut moves, slow creep while holding."""
    W, H = X.W, X.H
    def xy(sc, fx, fy):
        return min(0, max(W - sc * W, W / 2 - sc * fx * W)), min(0, max(H - sc * H, H / 2 - sc * fy * H))
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    keys = sorted(k for k in keys if k[0] < t + d - 0.2) or [keys[0]]
    keys = [(k[0], min(k[1], 1.04), k[2], k[3]) for k in keys]      # gentle: windows and their shadows stay in frame
    for k, (tk, sc, fx, fy) in enumerate(keys):
        x, y = xy(sc, fx, fy)
        nxt = keys[k + 1][0] if k + 1 < len(keys) else t + d
        if k == 0:
            X.tw(f'tl.set("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}}}, {tk:.3f});'); hold0 = tk
        else:
            mv = min(0.9, max(0.3, nxt - tk - 0.05))
            X.tw(f'tl.to("{sel}", {{scale:{sc}, x:{x:.1f}, y:{y:.1f}, duration:{mv:.2f}, ease:"expo.inOut"}}, {tk:.3f});'); hold0 = tk + mv
        if nxt - hold0 > 0.25:
            x2, y2 = xy(sc * 1.018, fx, fy)
            X.tw(f'tl.to("{sel}", {{scale:{sc * 1.018:.4f}, x:{x2:.1f}, y:{y2:.1f}, duration:{nxt - hold0 - 0.03:.2f}, ease:"none"}}, {hold0:.3f});')


def cursor_path(X, sel, pts):
    """pts = [(time, x, y, click?)]: glide between points (power2.inOut), click = press + ripple + sfx."""
    pts = sorted(pts)
    for k, (tk, x, y, clk) in enumerate(pts):
        if k == 0:
            X.tw(f'tl.set("{sel}", {{x:{x:.0f}, y:{y:.0f}}}, {tk:.3f});')
            X.tw(f'tl.from("{sel}", {{opacity:0, duration:0.25}}, {tk:.3f});')
        else:
            pt = pts[k - 1][0]
            X.tw(f'tl.to("{sel}", {{x:{x:.0f}, y:{y:.0f}, duration:{max(0.2, min(0.55, tk - pt - 0.02)):.2f}, ease:"power3.inOut"}}, {max(pt + 0.02, tk - 0.55):.3f});')
        if clk:
            X.tw(f'tl.fromTo("{sel} svg", {{scale:1}}, {{keyframes:[{{scale:0.82, duration:0.08}}, {{scale:1, duration:0.18}}], transformOrigin:"10% 5%", immediateRender:false}}, {tk:.3f});')
            X.tw(f'tl.fromTo("{sel} .rp", {{scale:0.3, opacity:0.9}}, {{scale:1.8, opacity:0, duration:0.45, ease:"power2.out", immediateRender:false}}, {tk:.3f});')
            X.sfx(tk, "click")


def typing(X, sel, t, n, each=0.055):
    """chars appear one by one (display, so the caret travels with the text)."""
    if n <= 0: return
    X.tw(f'tl.from("{sel} .c", {{display:"none", duration:0.01, stagger:{each}, ease:"none"}}, {t:.3f});')
    for k in range(0, n, 3): X.sfx(t + k * each, "type", 0.18)


def chars(X, s, px=None):
    X.used_text.update(s)
    st = f' style="font-size:{px}px"' if px else ""
    return f'<span{st}>' + "".join(f'<i class="c">{X.rich(ch) if ch.strip() else "&nbsp;"}</i>' for ch in s) + "</span>"


# ---------------------------------------------------------------- scenes
def dash(b, X, t, d, cid):
    """weekly-users counter + growth line (2–12 points) + share donut + a chat pane (or screenshots) asking the question.
    params: value, label, series [[label, value]], series_unit, hl (index), tag0, paid, paid_label, q, answer, input, images."""
    P = X.portrait
    X.css("sc-dash", """
.sc-dash .chat .q { position:absolute; right:24px; top:16px; color:#ffffff; background:var(--fg); border-radius:18px 18px 4px 18px; padding:10px 18px; font-weight:600; }
.sc-dash .chat .a { position:absolute; left:24px; color:var(--fg); background:var(--surf2); border:1px solid rgba(27,27,31,.14); border-radius:18px 18px 18px 4px; padding:12px 18px; }
.sc-dash .chat .in { position:absolute; left:24px; right:24px; bottom:16px; height:56px; border-radius:12px; border:1.5px solid #1b1b1f; background:#f4f1ea; font-size:28px; color:var(--muted); display:flex; align-items:center; padding:0 18px; white-space:nowrap; overflow:hidden; }
""")
    imgs = b.get("images") or []
    # ---- layout per orientation
    if P:   # four windows stacked down the whole portrait frame: metric · chart · paid share · chat
        M = (40, 300, 1000, 540); CH = (24, 870, 560, 470); Pw = (590, 880, 370, 460); C = None   # all inside y 300–1340
        big_box, lab_y, chart = (910, 0), 0, (16, 18, 528, 384)
        dn = (20, 20, 150)
    else:
        M = (60, 100, 1120, 740); Pw = (1232, 100, 630, 360); C = (1232, 500, 630, 340)   # 2 columns, metric 58 % wide
        big_box, lab_y, chart = (1030, 160), 206, (44, 280, 1030, 380)
        dn = (40, 30, 270)
    value = b.get("value", 800_000_000)
    vtxt = fmt_num(value, int(b.get("value_dec", 0)))
    npx = fit_px(vtxt, big_box[0], 150 if not P else 118, 40)
    lab, _, _ = fit(X, b.get("label", ""), big_box[0], 62 if not P else 80, 28 if not P else 34, 16 if not P else 26, 2, 1.2, "lbl")
    big = b.get("big"); bunit = str(b.get("big_unit", ""))
    if P and big is not None:      # 9:16: the headline figure in its short form (8 亿), the full number typed under it
        bnpx = fit_px(f"{float(big):g}" + "中" * len(bunit) * 1, big_box[0] * 0.9, 380, 120)
    # ---- chart: 2..12 points
    pts = b.get("series") or [["", value]]
    unit = b.get("series_unit", "M")
    cx, cy, cw, chh = chart
    n = len(pts); vmax = max(float(v) for _, v in pts) * 1.12 or 1
    xs = [40 + (k * (cw - 80) / (n - 1) if n > 1 else (cw - 80) / 2) for k in range(n)]
    ys = [chh - 30 - (float(v) / vmax) * (chh - 76) for _, v in pts]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = path + f" L{xs[-1]:.1f},{chh - 30} L{xs[0]:.1f},{chh - 30} Z"
    step = 1 if n <= 6 else math.ceil(n / 6)
    fs = (24 if n <= 6 else 20) if not P else 30
    grid = "".join(f'<line x1="0" x2="{cw}" y1="{chh - 30 - g * (chh - 76) / 4:.1f}" y2="{chh - 30 - g * (chh - 76) / 4:.1f}" stroke="rgba(27,27,31,.12)"/>' for g in range(5))
    dots = []
    for k, (x, y, (lab_k, v)) in enumerate(zip(xs, ys, pts)):
        show = k % step == 0 or k == n - 1
        vt = f"{float(v):,.0f}{unit}" if float(v) == int(float(v)) else f"{float(v):g}{unit}"
        dots.append(f'<g class="pt" data-k="{k}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{9 if n <= 8 else 7}" fill="#ffffff" stroke="#2f5bff" stroke-width="4"/>'
                    + (f'<text x="{x:.1f}" y="{chh - 2}" fill="#5b5b66" font-size="{fs - 4 if not P else 24}" text-anchor="middle" font-family="JetBrains Mono, monospace">{X.rich(lab_k)}</text>'
                       f'<text x="{x:.1f}" y="{y - 20:.1f}" fill="#1b1b1f" font-size="{fs}" font-weight="700" text-anchor="middle" font-family="Inter, sans-serif">{X.rich(vt)}</text>' if show else "")
                    + "</g>")
        X.used_text.update(vt + str(lab_k))
    hk = min(max(int(b.get("hl", 0)), 0), n - 1)
    t0txt = str(b.get("tag0", ""))
    tw_ = 24 + 21 * est_w(t0txt)
    tx = xs[hk] + 36 if xs[hk] + 36 + tw_ < cw else xs[hk] - 36 - tw_
    ring = (f'<circle class="ring0" cx="{xs[hk]:.1f}" cy="{ys[hk]:.1f}" r="26" fill="none" stroke="#2f5bff" stroke-width="3"/>'
            + (f'<g class="t0"><rect x="{tx:.1f}" y="{max(4, ys[hk] - 62):.1f}" width="{tw_:.0f}" height="40" rx="9" fill="#2f5bff"/>'
               f'<text x="{tx + 12:.1f}" y="{max(4, ys[hk] - 62) + 28:.1f}" fill="#ffffff" font-size="22" font-weight="700" font-family="Inter, sans-serif">{X.rich(t0txt)}</text></g>' if t0txt else ""))
    svg = (f'<svg class="ch ab" viewBox="0 0 {cw} {chh}" style="{box(cx, cy, cw, chh)}; overflow:visible"><defs><linearGradient id="ar{cid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f5bff" stop-opacity=".28"/>'
           f'<stop offset="1" stop-color="#2f5bff" stop-opacity="0"/></linearGradient></defs>{grid}<path class="ar" d="{area}" fill="url(#ar{cid})"/>'
           f'<path class="ln" d="{path}" pathLength="1" fill="none" stroke="#2f5bff" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>{"".join(dots)}{ring}</svg>')
    # ---- share card
    pv = float(b.get("paid", 5)); pvs = f"{pv:g}"
    dx, dy, dsz = dn
    pvx = dx + dsz + 30; pvw = Pw[2] - pvx - 24
    pnpx = fit_px(pvs + "%", pvw, 120 if not P else 104, 36)
    if P:
        pvx, pvw = dx, Pw[2] - 2 * dx
        pnpx = 110
        dx, dy = Pw[2] - dsz - 26, 20
    plab, _, _ = fit(X, b.get("paid_label", ""), pvw, (Pw[3] - 44 - (dy + pnpx + 24) - 12) if not P else 120, 24 if not P else 27, 14 if not P else 22, 4, 1.4, "lbl")
    pvw = max(pvw, 200)
    donut = (f'<svg class="dn ab" viewBox="0 0 120 120" style="{box(dx, dy, dsz, dsz)}"><circle cx="60" cy="60" r="48" fill="none" stroke="#e6e2d8" stroke-width="16"/>'
             f'<circle class="arc" cx="60" cy="60" r="48" fill="none" stroke="#2f5bff" stroke-width="16" pathLength="100" stroke-dasharray="0 100" transform="rotate(-90 60 60)"/>'
             f'<text x="60" y="56" text-anchor="middle" fill="#5b5b66" font-size="{10 if not P else 14}" font-family="JetBrains Mono, monospace">{X.rich(b.get("donut_tag", "PAID"))}</text>'
             f'<text x="60" y="74" text-anchor="middle" fill="#1b1b1f" font-size="{16 if not P else 20}" font-weight="700" font-family="Inter, sans-serif">≈{pvs}%</text></svg>')
    X.used_text.update(f"≈{pvs}%")
    pbody = (f'{donut}<div class="ab pv" style="left:{pvx}px; top:{(dy + 12) if not P else 40}px; width:{pvw}px"><div class="num" style="font-size:{pnpx}px; color:var(--lime)"><span class="n2">0</span>%</div>'
             f'<div class="lbl" style="margin-top:{12 if not P else 70}px">{plab}</div></div>')
    # ---- chat pane or screenshots
    cbody, ctitle, nimg = "", "chat", 0
    q = str(b.get("q", ""))
    if C:
        if imgs:
            g, nimg = gallery(X, imgs, C[2] - 40, C[3] - 44 - 36, 12, sty="left:20px; top:18px")
            cbody, ctitle = g, b.get("images_title", "screenshots")
        else:
            qpx = fit_px(q, C[2] - 48 - 140, 30 if P else 26, 24 if P else 16) if q else 22
            ahtml, apx, anl = fit(X, b.get("answer", ""), C[2] - 48 - 40, C[3] - 44 - 16 - 48 - 16 - 88 - 26 + (40 if P else 0), 28 if P else 24, 24 if P else 15, 3, 1.4)
            cbody = (f'<div class="q">{chars(X, q, qpx)}<i class="caret"></i></div>'
                     f'<div class="a" style="top:{30 + qpx * 1.3 + 28:.0f}px; max-width:{C[2] - 48}px">{ahtml}</div>'
                     f'<div class="in">{X.rich(b.get("input", "问点什么……"))}</div>')
    if P and big is not None:
        X.used_text.update(f"{float(big):g}" + bunit)
        mbody = (f'<div class="ab" style="left:40px; top:6px"><div class="num" style="font-size:{bnpx}px"><span class="n">0</span>'
                 f'<small style="font-family:var(--f-display); font-size:.8em; font-weight:800; margin-left:14px; letter-spacing:0">{X.rich(bunit)}</small></div></div>'
                 f'<div class="ab mono" style="left:44px; top:{bnpx * 0.96 + 6:.0f}px; font-size:40px; font-weight:700; color:var(--cobalt)"><span class="nf">0</span></div>'
                 f'<div class="ab" style="left:44px; top:{bnpx * 0.96 + 66:.0f}px; width:{big_box[0]}px">{lab}</div>')
    elif P:
        mbody = (f'<div class="ab" style="left:44px; top:30px"><div class="num n" style="font-size:{npx}px">0</div></div>'
                 f'<div class="ab" style="left:44px; top:{npx + 60}px; width:{big_box[0]}px">{lab}</div>')
    else:
        mbody = (f'<div class="ab" style="left:44px; top:34px"><div class="num n" style="font-size:{npx}px">0</div></div>'
                 f'<div class="ab" style="left:44px; top:{lab_y}px; width:{big_box[0]}px">{lab}</div>{svg}')
    inner = (f'<div class="sc sc-dash"><div class="bgfx"></div><div class="cam">'
             + win(X, "m", b.get("title", "weekly_active_users"), mbody, tag="" if P else "LIVE", sty=box(*M), bar="cobalt", tilt=-0.8 if P else 0)
             + (win(X, "chw", "growth.chart", svg, sty=box(*CH), bar="sun", tilt=1.4) if P else "")
             + win(X, "p drag", "paid_share", pbody, sty=box(*Pw), bar="mint", tilt=-1.6 if P else 0)
             + (win(X, "chat", ctitle, cbody, sty=box(*C), bar="tomato", tilt=0.9 if P else 0) if C else "")
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.used_text.update("%")
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn, tp, t0 = T(X, b, "at_num", t, t + 0.5), T(X, b, "at_paid", t, t + d * 0.45), T(X, b, "at_then", t, t + d * 0.7)
    rise(X, f"{s} .win:not(.drag)", t, st=0.1, icon=SCENE_ICON["dash"])
    X.sfx(t, "enter")
    if P and big is not None:
        counter(X, f"{s} .n", t + 0.1, 0, float(big), dur=max(0.4, tn - t - 0.1), dec=len(f"{float(big):g}".split(".")[1]) if "." in f"{float(big):g}" else 0)
        counter(X, f"{s} .nf", t + 0.1, 0, float(value), dur=max(1.0, tn + 0.5 - t - 0.1))
    else:
        counter(X, f"{s} .n", t + 0.1, 0, float(value), dur=max(1.0, tn + 0.3 - t - 0.1), dec=int(b.get("value_dec", 0)), ease="power2.inOut")
    X.sfx(t + 0.1, "count")
    X.tw(f'tl.fromTo("{s} .ln", {{strokeDasharray:"1 1", strokeDashoffset:1}}, {{strokeDashoffset:0, duration:1.4, ease:"power2.inOut"}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{s} .ar", {{opacity:0, duration:0.8}}, {t + 0.9:.3f});')
    X.tw(f'tl.from("{s} .pt", {{opacity:0, scale:0.4, transformOrigin:"50% 50%", duration:0.4, ease:"back.out(2.5)", stagger:{min(0.25, 1.2 / n):.3f}}}, {t + 0.5:.3f});')
    X.tw(f'tl.to("{s} .arc", {{attr:{{"stroke-dasharray":"{pv:g} {100 - pv:g}"}}, duration:0.8, ease:"power3.out"}}, {tp - 0.2:.3f});')
    counter(X, f"{s} .n2", tp - 0.2, 0, pv, dur=0.8, dec=1 if pv != int(pv) else 0)
    X.tw(f'tl.from("{s} .pv .num", {{opacity:0, y:20, duration:0.4, ease:"expo.out"}}, {tp - 0.25:.3f});')
    X.tw(f'tl.from("{s} .pv .lbl", {{opacity:0, x:20, duration:0.5}}, {tp:.3f});')
    X.sfx(tp - 0.1, "pop")
    if C and nimg:
        tiles_in(X, f"{s} .chat", t + 0.4, nimg)
    if C and not imgs:
        typing(X, f"{s} .chat .q", t + 0.6, len(q), min(0.05, 1.4 / max(len(q), 1)))
        X.tw(f'tl.from("{s} .chat .a", {{opacity:0, y:16, duration:0.5, ease:"expo.out"}}, {t + 0.7 + min(len(q) * 0.05, 1.4):.3f});')
    if not P:
        cursor_path(X, f"{s} .cur", [(t + 0.3, 1500, 860, False), (t + 0.55, 1560, 836, True), (tp - 0.3, 1420, 330, False),
                                    (max(t0 - 0.2, tp + 0.4), M[0] + cx + xs[hk] + 40, M[1] + 44 + cy + ys[hk] + 40, False)])
    else:   # the cursor drags the paid-share window in, clicks it (the donut fills), then clicks the 2023 point
        pts = drag_in(X, s, f"{s} .p", Pw, t + 0.2, -240, -140)
        pts += [(tp - 0.25, Pw[0] + 150, Pw[1] + 200, True),
                (max(t0 - 0.1, tp + 0.5), CH[0] + 46 + chart[0] + xs[hk], CH[1] + 46 + chart[1] + ys[hk], True)]
        cursor_path(X, f"{s} .cur", pts)
    if not P:
        X.tw(f'tl.from("{s} .p", {{x:200, opacity:0, duration:0.35, ease:"back.out(1.4)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.set("{s} .ring0{", " + s + " .t0" if t0txt else ""}", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .ring0", {{scale:0.3, opacity:0, transformOrigin:"50% 50%"}}, {{scale:1, opacity:1, duration:0.45, ease:"back.out(2.5)", immediateRender:false}}, {t0:.3f});')
    if t0txt: X.tw(f'tl.to("{s} .t0", {{opacity:1, duration:0.35}}, {t0 + 0.1:.3f});')
    X.sfx(t0, "pop")
    hx = (M[0] + cx + xs[hk]) / X.W; hy = (M[1] + 44 + cy + ys[hk]) / X.H
    if P:
        shots(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5)])
    else:
        shots(X, f"{s} .cam", t, d, [(t, 1.1, 0.3, 0.22), (tp - 0.45, 1.0, 0.5, 0.5), (t0 - 0.25, 1.12, max(0.2, min(0.8, hx)), max(0.3, min(0.7, hy)))])


def api(b, X, t, d, cid):
    """an API console streaming request logs, a big per-minute counter with a full-number ticker, and a throughput strip
    (or screenshots). params: label, big, big_unit, value, unit, note, endpoints[], images."""
    P = X.portrait
    X.css("sc-api", """
.sc-api .tm .rows { position:absolute; left:28px; right:28px; top:16px; font-family:var(--f-mono); color:var(--muted); white-space:nowrap; }
.sc-api .tm .rows b { color:var(--lime); font-weight:500; } .sc-api .tm .rows u { text-decoration:none; color:var(--fg); }
.sc-api .tm .fade { position:absolute; left:0; right:0; top:0; height:120px; background:linear-gradient(180deg, #ffffff, transparent); }
.sc-api .bars { position:absolute; overflow:hidden; }
.sc-api .bars .strip { position:absolute; left:0; bottom:0; display:flex; align-items:flex-end; gap:8px; }
.sc-api .bars i { flex:none; width:20px; border-radius:5px 5px 0 0; background:linear-gradient(180deg, #2f5bff, rgba(47,91,255,.25)); }
.sc-api .note { color:var(--fg); } .sc-api .note .em .emt { color:var(--lime); }
""")
    if P:   # metric on top, throughput graph and the log tail stacked under it to the dock
        K, GB, TM = (40, 300, 1000, 600), (600, 930, 360, 410), (24, 940, 560, 400)
        lw, nw, BX = 900, 900, (22, 22, 316, 320)
    else:
        K, TM = (60, 100, 1120, 740), (1232, 100, 630, 740)   # 2 columns: metric 58 % wide, log tail beside it
        lw, nw, BX = 1030, 1030, (40, 0, 1040, 230)
    kb = K[3] - 44
    lab, lpx, lnl = fit(X, b.get("label", ""), lw, 64 if not P else 90, 24 if not P else 36, 15 if not P else 26, 2, 1.25, "lbl")
    big = float(b.get("big", 60)); bu = str(b.get("big_unit", ""))
    btxt = f"{big:g}"
    npx = fit_px(btxt + "".join("中" for _ in bu) * 1, nw, 260 if not P else 320, 48)
    ny = 36 + lnl * lpx * 1.25 + 14
    unit = str(b.get("unit", ""))
    vtxt = fmt_num(b.get("value", 0)) + " " + unit if b.get("value") is not None else unit
    upx = fit_px(vtxt, nw, 26 if not P else 36, 13 if not P else 24)
    uy = ny + npx * 1.0 + 16
    imgs = b.get("images") or []
    if P:
        bx, by, bw, bh = BX
        nh_html, nh_px, _ = fit(X, b.get("note", ""), lw, kb - (uy + upx + 24) - 20, 32, 24, 3, 1.4, "note")
        note_y = uy + upx + 24
    else:
        nh_html, nh_px, nnl = fit(X, b.get("note", ""), lw, 110, 24, 14, 3, 1.45, "note")
        note_y = kb - 40 - nnl * nh_px * 1.45
        bx, bw = BX[0], BX[2]; by = uy + upx + 30; bh = max(80, note_y - 24 - by)
    r = X.rand
    eps = b.get("endpoints") or ["/v1/responses", "/v1/chat/completions", "/v1/embeddings", "/v1/responses", "/v1/realtime", "/v1/images", "/v1/responses"]
    lh = 44 if P else 42; fs = 26 if P else 22
    rows = []
    for k in range(60):
        tok = r.randint(180, 9000); ms = r.randint(90, 1800)
        rows.append(f'<div>{(k * 7) % 60:02d}:{(k * 13) % 60:02d}.{r.randint(100, 999)}  <u>POST</u> {X.rich(eps[k % len(eps)])}  <b>200</b>  {tok:,} tok  {ms}ms</div>')
    X.used_text.update("".join(eps) + "POST200tokms:.,")
    if imgs:
        right, nimg = gallery(X, imgs, bw, bh, 10, sty=f"left:{bx}px; top:{by:.0f}px")
    else:
        nimg = 0
        bars = "".join(f'<i style="height:{int(bh * (0.25 + 0.7 * (0.5 + 0.5 * math.sin(k * 0.7) * math.cos(k * 0.23))))}px"></i>' for k in range(70))
        right = f'<div class="bars" style="{box(bx, by, bw, bh)}"><div class="strip">{bars}</div></div>'
    kbody = (f'<div class="ab" style="left:40px; top:36px; width:{lw}px">{lab}</div>'
             f'<div class="ab num" style="left:36px; top:{ny:.0f}px; font-size:{npx}px"><span class="n">0</span><small style="font-family:var(--f-display); font-size:{.47 if not P else .62}em; font-weight:800; margin-left:8px; letter-spacing:0">{X.rich(bu)}</small></div>'
             f'<div class="ab mono lime" style="left:40px; top:{uy:.0f}px; font-size:{upx}px; white-space:nowrap">'
             + (f'<span class="n3">0</span> {X.rich(unit)}' if b.get("value") is not None else X.rich(unit)) + '</div>'
             f'{"" if P else right}<div class="ab note" style="left:40px; top:{note_y:.0f}px; width:{lw}px">{nh_html}</div>')
    inner = (f'<div class="sc sc-api"><div class="bgfx"></div><div class="cam">'
             + win(X, "k", "throughput", kbody, sty=box(*K), bar="cobalt", tilt=-0.7 if P else 0)
             + (win(X, "gb drag", "tokens / min", right, sty=box(*GB), bar="sun", tilt=1.8) if P else "")
             + win(X, "tm", b.get("log_title", "api.log — tail -f"), f'<div class="rows" style="font-size:{fs}px; line-height:{lh}px">{"".join(rows)}</div><div class="fade"></div>', tag="STREAMING", sty=box(*TM), bar="tomato", tilt=-1.1 if P else 0)
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + d * 0.6)
    rise(X, f"{s} .win:not(.drag)", t, st=0.1, icon=SCENE_ICON["api"])
    X.sfx(t, "enter")
    X.tw(f'tl.fromTo("{s} .rows", {{y:0}}, {{y:{-lh * 40}, duration:{d + 0.5:.2f}, ease:"none"}}, {t:.3f});')
    if imgs:
        tiles_in(X, s, t + 0.3, nimg)
    else:
        X.tw(f'tl.fromTo("{s} .strip", {{x:0}}, {{x:-560, duration:{d + 0.5:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.from("{s} .bars i", {{scaleY:0, transformOrigin:"50% 100%", duration:0.5, ease:"expo.out", stagger:0.012}}, {t + 0.2:.3f});')
    c0 = t + 0.2; cd = max(1.0, tn + 0.3 - c0)
    counter(X, f"{s} .n", c0, 0, big, dur=cd, dec=len(btxt.split(".")[1]) if "." in btxt else 0, ease="power2.inOut")
    if b.get("value") is not None:
        counter(X, f"{s} .n3", c0, 0, float(b["value"]), dur=cd, ease="power2.inOut")
    X.sfx(c0, "count")
    X.tw(f'tl.from("{s} .note", {{opacity:0, y:14, duration:0.5, ease:"expo.out"}}, {tn + 0.4:.3f});')
    if P:   # the cursor drags the graph window in, then hits the STREAMING tag as the figure lands
        pts = drag_in(X, s, f"{s} .gb", GB, t + 0.15, -320, 300)
        pts += [(tn - 0.15, TM[0] + TM[2] - 90, TM[1] + 22, True), (tn + 0.6, K[0] + 300, K[1] + 260, False)]
        cursor_path(X, f"{s} .cur", pts)
        X.tw(f'tl.fromTo("{s} .k .num", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.1}}, {{scale:1, duration:0.25}}], transformOrigin:"0 60%", immediateRender:false}}, {tn:.3f});')
        shots(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5)])
    else:
        cursor_path(X, f"{s} .cur", [(t + 0.3, 700, 900, False), (tn - 0.15, TM[0] + TM[2] - 90, TM[1] + 22, True), (tn + 0.6, K[0] + 300, K[1] + 300, False)])
        shots(X, f"{s} .cam", t, d, [(t, 1.12, 0.3, 0.45), (tn - 0.4, 1.08, 0.72, 0.42)])


def pricing(b, X, t, d, cid):
    """headline counter, 1–8 plan cards the cursor visits, and a 100-person grid with the paying share lit.
    params: value, unit, label, plans [[name, price, per, note]], focus [i, j], paid_cells (0–100), legend [[name, value, on|'']]."""
    P = X.portrait
    plans = b.get("plans") or [["Free", "$0", "/ 月", ""]]
    N = len(plans)
    X.css("sc-pr", """
.sc-pr .cd { position:absolute; border-radius:12px; background:#fbfaf6; border:1.5px solid #1b1b1f; overflow:hidden; }
.sc-pr .cd h4 { margin:0; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; }
.sc-pr .cd .pr { font-family:var(--f-num); font-weight:700; letter-spacing:-.03em; color:var(--fg); line-height:1; white-space:nowrap; }
.sc-pr .cd .pr small { font-size:.32em; color:var(--muted); font-weight:500; margin-left:6px; letter-spacing:0; }
.sc-pr .cd p { margin:0; color:var(--muted); }
.sc-pr .cd .bt { position:absolute; border-radius:12px; display:grid; place-items:center; font-weight:700; color:var(--fg); border:1px solid rgba(27,27,31,.28); }
.sc-pr .cd .hv { position:absolute; inset:0; border-radius:12px; border:5px solid var(--cobalt); background:rgba(47,91,255,.08); opacity:0; }
.sc-pr .grid { position:absolute; display:grid; }
.sc-pr .grid i { border-radius:22%; background:#e6e2d8; }
.sc-pr .grid i.on { background:var(--cobalt); box-shadow:3px 3px 0 #1b1b1f; }
.sc-pr .leg div { display:flex; justify-content:space-between; align-items:baseline; color:var(--muted); border-top:1px solid rgba(27,27,31,.14); white-space:nowrap; gap:12px; }
.sc-pr .leg b { font-family:var(--f-num); color:var(--fg); letter-spacing:-.02em; } .sc-pr .leg .on b { color:var(--lime); }
""")
    if P:   # pricing page on top, the 100-user grid and the share legend overlapping it down to the dock
        PW, GW, LW = (40, 300, 1000, 800), (32, 1110, 620, 230), (630, 1100, 330, 240)
        area = (28, 380, 944, 800 - 46 - 380 - 26); maxcols = 3
        gcols, gcell, ggap, gpos = 20, 22, 6, (32, 22); legbox = (22, 18, 286, 160)
    else:
        PW, GW = (60, 100, 1120, 740), (1232, 100, 630, 740)
        area = (40, 240, 1020, 740 - 46 - 240 - 30); maxcols = 4
        gcols, gcell, ggap, gpos = 10, 38, 12, (44, 40); legbox = (44, 40 + 10 * 50 + 14, 540, 740 - 46 - (40 + 10 * 50 + 14) - 14)
    head_v = float(b.get("value", 0)); htxt = fmt_num(head_v)
    hu = str(b.get("unit", ""))
    hpx = fit_px(htxt + hu, area[2] * 0.8, 104, 40) if not P else fit_px(htxt, area[2] * 0.74, 320, 120)
    lab, _, _ = fit(X, b.get("label", ""), area[2], 50, 24 if not P else 34, 14 if not P else 26, 1, 1.2, "lbl")
    cols = min(N, maxcols) if N <= maxcols else math.ceil(N / math.ceil(N / maxcols))
    rows = math.ceil(N / cols); gap = 22 if not P else 14
    cw = (area[2] - gap * (cols - 1)) / cols; chh = (area[3] - gap * (rows - 1)) / rows
    sc = max(0.42, min(1.0, chh / 420, cw / 300))
    pad = 26 * sc
    cards = []
    for k, pl in enumerate(plans):
        name, price = str(pl[0]), str(pl[1]); per = str(pl[2]) if len(pl) > 2 else ""; note = str(pl[3]) if len(pl) > 3 else ""
        r_, c_ = divmod(k, cols)
        inrow = min(cols, N - r_ * cols); x0 = area[0] + (area[2] - (inrow * cw + (inrow - 1) * gap)) / 2
        x = x0 + c_ * (cw + gap); y = area[1] + r_ * (chh + gap)
        npx_ = fit_px(name, cw - 2 * pad, 28 * max(sc, .7), 14)
        ppx = fit_px(price + per[:2], cw - 2 * pad, 76 * sc, 22)
        bh = max(30, 56 * sc)
        top_used = pad + npx_ * 1.2 + 18 * sc + ppx + 18 * sc
        if chh - top_used - pad < bh: bh = 0                     # compact card: no room for a button
        nbox = chh - top_used - bh - 2 * pad
        nh = fit(X, note, cw - 2 * pad, nbox, 22 * max(sc, .75) if not P else 27, 13 if not P else 24, 3, 1.4)[0] if note and nbox > 22 else ""
        btn = "当前方案" if k == 0 and b.get("first_is_current", True) else b.get("cta", "升级")
        cards.append(f'<div class="cd" data-k="{k}" style="{box(x, y, cw, chh)}"><i class="hv"></i>'
                     f'<h4 class="ab" style="left:{pad:.0f}px; top:{pad:.0f}px; font-size:{npx_}px">{X.rich(name)}</h4>'
                     f'<div class="pr ab" style="left:{pad:.0f}px; top:{pad + npx_ * 1.2 + 18 * sc:.0f}px; font-size:{ppx}px">{X.rich(price)}<small>{X.rich(per)}</small></div>'
                     f'<p class="ab" style="left:{pad:.0f}px; right:{pad:.0f}px; top:{top_used:.0f}px">{nh}</p>'
                     + (f'<div class="bt" style="left:{pad:.0f}px; right:{pad:.0f}px; bottom:{pad:.0f}px; height:{bh:.0f}px; font-size:{max(13 if not P else 26, 22 * sc):.0f}px">{X.rich(btn)}</div>' if bh else "") + '</div>')
    X.used_text.update("当前方案升级")
    paid = max(0, min(100, int(b.get("paid_cells", 5))))
    order = list(range(100)); X.rand.shuffle(order); lit = set(order[:paid])
    grid = "".join(f'<i class="{"on" if k in lit else ""}" style="width:{gcell}px; height:{gcell}px"></i>' for k in range(100))
    legs = b.get("legend") or []
    nl = max(1, len(legs)); rowh = min(64, legbox[3] / nl)
    lfs = max(14, min(24 if not P else 32, rowh * 0.42)); bfs = max(18, min(44 if not P else 60, rowh * 0.7))
    leg = "".join(f'<div class="{c if len(it) > 2 else ""}" style="height:{rowh:.0f}px; font-size:{fit_px(str(a), legbox[2] * 0.6, lfs, 12)}px"><span>{X.rich(a)}</span>'
                  f'<b style="font-size:{fit_px(str(v), legbox[2] * 0.4, bfs, 14)}px">{X.rich(v)}</b></div>'
                  for it in legs for a, v, c in [(it[0], it[1], it[2] if len(it) > 2 else "")])
    gtitle = b.get("grid_title", "100 users")
    inner = (f'<div class="sc sc-pr"><div class="bgfx"></div><div class="cam">'
             + win(X, "pw", b.get("title", "pricing"), f'<div class="ab" style="left:40px; top:{12 if P else 34}px; white-space:nowrap"><span class="num n" style="font-size:{hpx}px; color:var(--lime)">0</span>'
                   f'<span style="font-size:{(hpx * 0.38) if not P else 52:.0f}px; font-weight:800; color:var(--fg); margin-left:16px">{X.rich(hu)}</span></div>'
                   f'<div class="ab" style="left:40px; top:{area[1] - 70 if not P else hpx + 36:.0f}px; width:{area[2]}px">{lab}</div>{"".join(cards)}', sty=box(*PW), bar="cobalt", tilt=-0.6 if P else 0)
             + win(X, "gw", gtitle, f'<div class="grid" style="left:{gpos[0]}px; top:{gpos[1]}px; grid-template-columns:repeat({gcols}, {gcell}px); gap:{ggap}px">{grid}</div>'
                   + ("" if P else f'<div class="leg ab" style="{box(*legbox)}">{leg}</div>'), sty=box(*GW), bar="mint", tilt=1.2 if P else 0)
             + (win(X, "lw drag", "share", f'<div class="leg ab" style="{box(*legbox)}">{leg}</div>', sty=box(*LW), bar="sun", tilt=-1.8) if P else "")
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + 0.6)
    t1, t2, tf = T(X, b, "at_p1", t, t + d * 0.35), T(X, b, "at_p2", t, t + d * 0.5), T(X, b, "at_free", t, t + d * 0.72)
    rise(X, f"{s} .win:not(.drag)", t, st=0.1, icon=SCENE_ICON["pricing"])
    X.tw(f'tl.from("{s} .cd", {{y:40, opacity:0, duration:0.6, ease:"expo.out", stagger:{min(0.08, 0.6 / N):.3f}}}, {t + 0.2:.3f});')
    X.sfx(t, "enter")
    c0 = t + 0.15
    counter(X, f"{s} .n", c0, 0, head_v, dur=max(1.0, tn + 0.3 - c0), ease="power2.inOut")
    X.sfx(c0, "count")
    X.tw(f'tl.from("{s} .grid i", {{scale:0, duration:0.3, ease:"back.out(2)", stagger:{{from:"start", amount:0.8}}}}, {t + 0.35:.3f});')
    foc = [k for k in (b.get("focus") or ([1, 2] if N >= 3 else list(range(N)))) if 0 <= k < N][:2]
    times = [t1, t2][:len(foc)]
    for j, (k, tk) in enumerate(zip(foc, times)):
        X.tw(f'tl.to("{s} .cd[data-k=\'{k}\'] .hv", {{opacity:1, duration:0.2}}, {tk:.3f});')
        X.tw(f'tl.to("{s} .cd[data-k=\'{k}\']", {{y:-10, duration:0.35, ease:"back.out(2)"}}, {tk:.3f});')
        if j == 0 and len(foc) > 1:
            X.tw(f'tl.to("{s} .cd[data-k=\'{k}\'] .hv", {{opacity:0.25, duration:0.3}}, {times[1]:.3f});')
            X.tw(f'tl.to("{s} .cd[data-k=\'{k}\']", {{y:0, duration:0.3}}, {times[1]:.3f});')
    if paid:
        X.tw(f'tl.fromTo("{s} .grid i.on", {{scale:1.8}}, {{scale:1, duration:0.5, ease:"expo.out", stagger:{min(0.06, 0.6 / paid):.3f}, immediateRender:false}}, {tn + 0.2:.3f});')
    X.tw(f'tl.to("{s} .grid i:not(.on)", {{opacity:0.4, duration:0.25, stagger:{{from:"end", amount:0.6}}}}, {tf - 0.1:.3f});')
    if legs:
        X.tw(f'tl.from("{s} .leg > div", {{opacity:0, x:24, duration:0.45, ease:"expo.out", stagger:0.12}}, {tn + 0.3:.3f});')
        X.tw(f'tl.fromTo("{s} .leg > div:last-child", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.15}}, {{scale:1, duration:0.3}}], transformOrigin:"0 50%", immediateRender:false}}, {tf:.3f});')
    X.sfx(tf, "pop")
    def cc(k):
        r_, c_ = divmod(k, cols); inrow = min(cols, N - r_ * cols); x0 = area[0] + (area[2] - (inrow * cw + (inrow - 1) * gap)) / 2
        return PW[0] + x0 + c_ * (cw + gap) + cw / 2, PW[1] + 46 + area[1] + r_ * (chh + gap) + chh * 0.62
    if P:   # the cursor clicks Plus, then Pro (each card lifts), then drags the share legend in as "95% free" is said
        cps = [(t + 0.3, 700, 1250, False)] + [(tk, *cc(k), True) for k, tk in zip(foc, times)]
        cps += drag_in(X, s, f"{s} .lw", LW, max(tf - 0.6, (times[-1] if times else t) + 0.4), -320, -220)
        X.tw(f'tl.set("{s} .lw", {{opacity:0}}, {t:.3f}); tl.set("{s} .lw", {{opacity:1}}, {max(tf - 0.6, (times[-1] if times else t) + 0.4):.3f});')
        cursor_path(X, f"{s} .cur", cps)
        shots(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5)])
    else:
        def cc(k):
            r_, c_ = divmod(k, cols); inrow = min(cols, N - r_ * cols); x0 = area[0] + (area[2] - (inrow * cw + (inrow - 1) * gap)) / 2
            return PW[0] + x0 + c_ * (cw + gap) + cw / 2, PW[1] + 44 + area[1] + r_ * (chh + gap) + chh * 0.62
        cps = [(t + 0.3, 1000, 950, False)] + [(tk, *cc(k), True) for k, tk in zip(foc, times)] + [(tf - 0.2, 1500, 520, False)]
        cursor_path(X, f"{s} .cur", cps)
        shots(X, f"{s} .cam", t, d, [(t, 1.12, 0.25, 0.22), (t1 - 0.5, 1.05, 0.4, 0.55), (tf - 0.4, 1.1, 0.78, 0.5)])


def forecast(b, X, t, d, cid):
    """1–6 bars (actual solid, projection dashed) with values, years and notes; an arrow + multiple between the first and
    last; a toast that says who made the projection. params: heading, heading_sub, value, unit, label, bars, notes, mult, toast."""
    P = X.portrait
    X.css("sc-fc", """
.sc-fc .fw svg { position:absolute; left:0; top:0; width:100%; height:100%; overflow:visible; }
.sc-fc .hd2 { font-family:var(--f-display); font-weight:700; color:var(--fg); }
.sc-fc .toast { position:absolute; border-radius:12px; background:#ffffff; padding:18px 22px; display:flex; gap:16px; }
.sc-fc .toast > i { flex:none; width:44px; height:44px; border-radius:12px; background:var(--violet); display:grid; place-items:center; color:#ffffff; font-style:normal; font-weight:800; font-size:28px; }
.sc-fc .toast b { display:block; color:var(--fg); font-weight:700; } .sc-fc .toast span.bd2 { display:block; margin-top:6px; color:var(--muted); }
.sc-fc .toast em { font-style:normal; display:inline-block; margin-top:10px; font-family:var(--f-mono); font-size:var(--em-px, 15px); color:var(--alert); border:1px solid rgba(255,90,60,.45); border-radius:999px; padding:1px 10px; white-space:nowrap; }
""")
    # 9:16: three windows — headline figure, the chart, and the projection notice — stacked to the dock
    HW, FW, TW = (40, 300, 1000, 530), (24, 852, 936, 488), (690, 326, 350, 480)   # notice overlaps the headline window's empty right side
    if not P: FW = (60, 100, 1120, 740)
    cw, ch = FW[2], FW[3] - 44
    bars = b.get("bars") or []
    nb = max(1, len(bars))
    toast = b.get("toast") or []
    if P:
        tbox = (10, 10, TW[2] - 20, TW[3] - 46 - 20)
    else:
        TW = (1232, 100, 630, 420)
        tbox = (10, 10, TW[2] - 20, TW[3] - 46 - 20)
    aw = cw - 88
    hd, hpx, _ = fit(X, b.get("heading", ""), aw, 44 if not P else 56, 34 if not P else 46, 18, 1, 1.2, "hd2")
    hs, spx, _ = fit(X, b.get("heading_sub", ""), aw, 34 if not P else 40, 26 if not P else 32, 14 if not P else 26, 1, 1.2, "lbl")
    sub_inline = (not P) and hs and est_w(b.get("heading", "")) * hpx + 14 + est_w(b.get("heading_sub", "")) * spx <= aw
    tt = (toast + ["", "", ""])[:3]
    t_title = fit(X, tt[0], tbox[2] - 110 if not P else tbox[2] - 90, 32 if not P else 80, 24 if not P else 34, 14 if not P else 28, 1 if not P else 2, 1.2)[0]
    t_body = fit(X, tt[1], tbox[2] - 110 if not P else tbox[2] - 90, (tbox[3] - 36 - 32 - 40) if not P else 220, 28 if not P else 28, 22 if not P else 24, 4 if not P else 6, 1.35)[0]
    num_y = 28 + hpx * 1.2 + 10 + (0 if (not hs or sub_inline) else spx * 1.2 + 4)
    v = float(b.get("value", 0)); vt = f"{v:g}"
    unit = str(b.get("unit", ""))
    npx = fit_px(vt + unit, (cw - 88) * 0.45, 96, 36) if not P else fit_px(vt + unit, 620, 290, 120)
    tlab = fit(X, b.get("label", ""), (cw - 88) * 0.5, 34, 22, 13, 1)[0] if not P else fit(X, b.get("label", ""), 900, 44, 32, 26, 1)[0]
    base = ch - (130 if P else 110); top = (num_y + npx + 60) if not P else 90
    vmax = max([float(x[1]) for x in bars] + [1]) * 1.12
    lo, hi = (0.18, 0.82) if nb > 1 else (0.5, 0.5)
    xs = [cw * (lo + (hi - lo) * k / max(nb - 1, 1)) for k in range(nb)]
    spacing = (xs[1] - xs[0]) if nb > 1 else cw * 0.4
    bw = min(200, spacing * 0.5)
    notes = b.get("notes") or []
    out = []
    for k, bar in enumerate(bars):
        yr, val = str(bar[0]), float(bar[1]); kind = bar[2] if len(bar) > 2 else "actual"; lab = str(bar[3]) if len(bar) > 3 else f"{val:g}"
        h = max(4, (val / vmax) * (base - top)); x = xs[k] - bw / 2
        if kind == "actual":
            out.append(f'<rect class="bb" data-k="{k}" x="{x:.0f}" y="{base - h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="12" fill="#2f5bff"/>')
        else:
            out.append(f'<rect class="bb" data-k="{k}" x="{x:.0f}" y="{base - h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="12" fill="rgba(255,90,60,.14)" stroke="#ff5a3c" stroke-width="3" stroke-dasharray="12 9"/>')
        vfs = fit_px(lab, spacing * 0.92, 44 if not P else 56, 16)
        yfs = fit_px(yr, spacing * 0.92, 26 if not P else 30, 13 if not P else 24)
        out.append(f'<text class="bv" data-k="{k}" x="{xs[k]:.0f}" y="{base - h - 20:.0f}" text-anchor="middle" fill="#1b1b1f" font-size="{vfs}" font-weight="700" font-family="Inter, sans-serif">{X.rich(lab)}</text>')
        out.append(f'<text x="{xs[k]:.0f}" y="{base + 44:.0f}" text-anchor="middle" fill="#5b5b66" font-size="{yfs}" font-family="JetBrains Mono, monospace">{X.rich(yr)}</text>')
        if k < len(notes) and notes[k]:
            nfs = fit_px(str(notes[k]), spacing * 0.95 if not P else spacing * 1.1, 24 if not P else 28, 12 if not P else 24)
            out.append(f'<text class="bn" data-k="{k}" x="{xs[k]:.0f}" y="{base + 84:.0f}" text-anchor="middle" fill="#1b1b1f" font-size="{nfs}" font-family="Inter, sans-serif">{X.rich(notes[k])}</text>')
        X.used_text.update(yr + lab)
    ax = f'<line x1="40" x2="{cw - 40}" y1="{base}" y2="{base}" stroke="rgba(27,27,31,.30)" stroke-width="2"/>'
    arw = mult = ""
    if nb >= 2:
        x1, x2 = xs[0] + bw / 2 + 20, xs[-1] - bw / 2 - 24
        h0 = (float(bars[0][1]) / vmax) * (base - top); h1 = (float(bars[-1][1]) / vmax) * (base - top)
        arw = f'<path class="arw" d="M{x1:.0f},{base - h0 - 40:.0f} C{(x1 + x2) / 2:.0f},{base - h0 - 60:.0f} {(x1 + x2) / 2:.0f},{base - h1 + 20:.0f} {x2:.0f},{base - h1 + 40:.0f}" pathLength="1" fill="none" stroke="#ff5a3c" stroke-width="4" stroke-dasharray="1 1"/>'
        if b.get("mult"):
            mult = f'<text class="mx" x="{(x1 + x2) / 2:.0f}" y="{(base - h0 + base - h1) / 2 - 20:.0f}" text-anchor="middle" fill="#ff5a3c" font-size="{fit_px(str(b["mult"]), spacing * 0.6, 40, 16)}" font-weight="700" font-family="Inter, sans-serif">{X.rich(b["mult"])}</text>'
    tst = (f'<div class="toast" style="{box(*tbox)}{"; --em-px:22px" if P else "; --em-px:22px"}"><i>i</i><div style="min-width:0">'
           f'<b>{t_title}</b><span class="bd2">{t_body}</span>' + (f'<em>{X.rich(tt[2])}</em>' if tt[2] else "") + '</div></div>') if any(tt) else ""
    X.used_text.update("i")
    heads = (f'<div class="ab" style="left:44px; top:28px; white-space:nowrap">{hd}' + (f'<span style="margin-left:14px">{hs}</span>' if sub_inline else "") + '</div>'
             + (f'<div class="ab" style="left:44px; top:{28 + hpx * 1.2 + 4:.0f}px">{hs}</div>' if hs and not sub_inline else "")
             + f'<div class="ab ttl" style="left:40px; top:{num_y - (6 if P else 0):.0f}px"><div class="num" style="font-size:{npx}px; color:var(--lime)"><span class="n">0</span>'
             + (f'<small style="font-family:var(--f-display); font-size:.36em; font-weight:800; margin-left:12px; color:#1b1b1f">{X.rich(unit)}</small>' if P else X.rich(unit))
             + f'</div><div style="margin-top:{4 if P else 10}px">{tlab}</div></div>')
    svg_ = f'<svg viewBox="0 0 {cw} {ch}">{ax}{"".join(out)}{arw}{mult}</svg>'
    if P:
        body = (win(X, "hw", "forecast.app", heads, sty=box(*HW), bar="sun", tilt=-0.8)
                + win(X, "fw", b.get("title", "forecast"), svg_, sty=box(*FW), bar="cobalt", tilt=1.0)
                + (win(X, "tw drag", "notification", tst, sty=box(*TW), bar="tomato", tilt=-1.2) if tst else ""))
    else:
        body = (win(X, "fw", b.get("title", "forecast"), svg_ + heads, sty=box(*FW), bar="sun")
                + (win(X, "tw", "notification", tst, sty=box(*TW), bar="tomato", tilt=1.0) if tst else ""))
    inner = (f'<div class="sc sc-fc"><div class="bgfx"></div><div class="cam">' + body
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tp, tn = T(X, b, "at_year", t, t + d * 0.3), T(X, b, "at_num", t, t + d * 0.65)
    rise(X, f"{s} .win:not(.drag)", t, st=0.1, icon=SCENE_ICON["forecast"])
    X.tw(f'tl.from("{s} .fw .bd > .ab:not(.ttl)", {{opacity:0, x:-20, duration:0.5, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.sfx(t, "enter")
    last = nb - 1
    for k in range(nb):
        tk = (t + 0.25 + k * 0.25) if k < last or nb == 1 else tn - 0.5
        if nb > 1 and k == last: tk = tn - 0.5
        X.tw(f'tl.from("{s} .bb[data-k=\'{k}\']", {{scaleY:0, transformOrigin:"50% 100%", duration:0.8, ease:"expo.out"}}, {tk:.3f});')
        sel_k = f"{s} .bv[data-k='{k}']" + (f", {s} .bn[data-k='{k}']" if k < len(notes) and notes[k] else "")
        X.tw(f'tl.from("{sel_k}", {{opacity:0, y:12, duration:0.4}}, {tk + 0.35:.3f});')
    if arw:
        X.tw(f'tl.fromTo("{s} .arw", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut"}}, {tp - 0.2:.3f});')
    if mult:
        X.tw(f'tl.from("{s} .mx", {{opacity:0, y:12, duration:0.4}}, {tn:.3f});')
    counter(X, f"{s} .n", tn - 0.5, 0, v, dur=0.9, dec=len(vt.split(".")[1]) if "." in vt else 0)
    X.sfx(tn - 0.5, "count")
    X.tw(f'tl.from("{s} .ttl", {{opacity:0, y:20, duration:0.45, ease:"expo.out"}}, {tn - 0.55:.3f});')
    if tst and not P:
        X.tw(f'tl.from("{s} .toast", {{x:80, opacity:0, duration:0.35, ease:"back.out(1.4)"}}, {t + 0.9:.3f});')
        X.sfx(t + 0.9, "pop")
    if P:   # the cursor drags the projection notice up into view, then clicks the 2030 bar as it grows
        pts = drag_in(X, s, f"{s} .tw", TW, t + 0.7, -240, 260) if tst else [(t + 0.5, 800, 1200, False)]
        x_last = FW[0] + xs[-1]; y_last = FW[1] + 46 + base - 60
        pts += [(tn - 0.55, x_last, y_last, True), (tn + 0.5, HW[0] + 420, HW[1] + 300, False)]
        cursor_path(X, f"{s} .cur", pts)
        shots(X, f"{s} .cam", t, d, [(t, 1.0, 0.5, 0.5)])
    else:
        cursor_path(X, f"{s} .cur", [(t + 0.4, 900, 950, False), (tn - 0.55, FW[0] + xs[-1], FW[1] + 44 + base - 60, True)])
        shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.38, 0.56), (tp - 0.2, 1.0, 0.5, 0.5), (tn - 0.3, 1.06, 0.56, 0.52)])


def shots_wall(b, X, t, d, cid):
    """截图墙: a headline over an adaptive grid of screenshots / images (0..many, any aspect); one tile can be highlighted
    on a cue. params: kicker, title, images [{src, focus, fit, label}], hl (index), at_hl."""
    P = X.portrait
    X.css("sc-sh", """
.sc-sh .kk { font-family:var(--f-mono); font-size:20px; color:var(--lime); letter-spacing:.08em; white-space:nowrap; }
.sc-sh .tt { font-family:var(--f-display); font-weight:800; color:var(--fg); letter-spacing:-.01em; }
""")
    L = (56, 270, 968) if P else (96, 120, 1728)
    kk = str(b.get("kicker", ""))
    ky = L[1]
    th, tpx, tnl = fit(X, b.get("title", ""), L[2], 200 if P else 130, 60 if P else 64, 26, 3 if P else 2, 1.15, "tt")
    ty = ky + (36 if kk else 0)
    wy = ty + (tnl * tpx * 1.15 if tnl else 0) + 26
    wb = (1250 if P else 900) - wy
    WN = (L[0], wy, L[2], wb)
    g, n = gallery(X, b.get("images") or [], WN[2] - 36, WN[3] - 44 - 36, 14 if not P else 10, sty="left:18px; top:18px")
    inner = (f'<div class="sc sc-sh"><div class="bgfx"></div><div class="cam">'
             + (f'<div class="ab kk" style="left:{L[0]}px; top:{ky}px">{X.rich(kk)}</div>' if kk else "")
             + f'<div class="ab" style="left:{L[0]}px; top:{ty}px; width:{L[2]}px">{th}</div>'
             + win(X, "sw", b.get("win_title", "screenshots"), g, tag=b.get("tag", ""), sty=box(*WN))
             + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    rise(X, f"{s} .win", t)
    if kk: X.tw(f'tl.from("{s} .kk", {{opacity:0, x:-20, duration:0.4}}, {t:.3f});')
    X.tw(f'tl.from("{s} .tt", {{opacity:0, y:30, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    tiles_in(X, s, t + 0.3, n)
    X.sfx(t, "enter")
    th_ = T(X, b, "at_hl", t, t + d * 0.6)
    hk = b.get("hl")
    if hk is not None and b.get("images") and 0 <= int(hk) < n:
        X.tw(f'tl.to("{s} .ph[data-k=\'{int(hk)}\'] .hl", {{opacity:1, duration:0.25}}, {th_:.3f});')
        if n > 1: X.tw(f'tl.to("{s} .ph:not([data-k=\'{int(hk)}\'])", {{opacity:0.35, duration:0.4}}, {th_:.3f});')
        X.sfx(th_, "pop")
    shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.5, 0.35 if P else 0.4), (t + d * 0.45, 1.0, 0.5, 0.5)])


def palette(b, X, t, d, cid):
    """a command palette: the judgment typed as a query, 1–12+ results ranked, selection moves to the one that matters.
    params: a (struck line), b (the judgment, *emphasis*), query, results [[name, value, hot]], at_b, at_sel."""
    P = X.portrait
    X.css("sc-pal", """
.sc-pal .tha { font-family:var(--f-display); font-weight:700; color:var(--muted); }
.sc-pal .tha .ft { text-decoration:line-through; text-decoration-thickness:6px; text-decoration-color:rgba(91,91,102,.8); }
.sc-pal .thb { font-family:var(--f-display); font-weight:800; color:var(--fg); letter-spacing:-.02em; }
.sc-pal .pl .in { position:absolute; left:0; right:0; top:0; height:84px; display:flex; align-items:center; gap:16px; padding:0 28px; color:var(--fg); border-bottom:1px solid rgba(27,27,31,.16); white-space:nowrap; overflow:hidden; }
.sc-pal .pl .in svg { width:30px; height:30px; flex:none; }
.sc-pal .pl .rs { position:absolute; left:14px; right:14px; top:100px; }
.sc-pal .pl .r { position:relative; display:flex; align-items:center; justify-content:space-between; padding:0 22px; border-radius:12px; color:var(--fg); white-space:nowrap; gap:20px; }
.sc-pal .pl .r span { display:flex; align-items:center; gap:16px; overflow:hidden; } .sc-pal .pl .r span i { width:12px; height:12px; border-radius:3px; background:#cfcabd; flex:none; }
.sc-pal .pl .r b { font-family:var(--f-num); font-weight:700; color:var(--muted); letter-spacing:-.02em; }
.sc-pal .pl .r.hot b { color:var(--lime); } .sc-pal .pl .r.hot span i { background:var(--lime); }
.sc-pal .pl .r.more { color:var(--muted); }
.sc-pal .pl .sel { position:absolute; left:14px; right:14px; top:100px; border-radius:10px; background:rgba(47,91,255,.12); border:3px solid var(--cobalt); }
.sc-pal .pl .kb { position:absolute; left:28px; bottom:16px; font-family:var(--f-mono); font-size:24px; color:var(--muted); }
""")
    L = (56, 270, 968) if P else (96, 126, 1180)
    ah, apx, anl = fit(X, b.get("a", ""), L[2] if not P else 640, 130 if not P else 200, 54 if not P else 76, 22 if not P else 64, 2, 1.2)
    bh, bpx, bnl = fit(X, b.get("b", ""), L[2], 240 if not P else 270, 104 if not P else 120, 34, 2, 1.12)
    if P:   # the old belief on a sticky note window, the judgment big on the desktop, the palette under it, the host on a call
        NW = (40, 300, 800, 46 + 30 + anl * apx * 1.2 + 34)
        by = NW[1] + NW[3] + 40
    else:
        by = L[1] + (anl * apx * 1.3 + max(34, bpx * 0.3) if anl else 0)
    wy = by + bnl * bpx * 1.12 + 34
    wb = (840 if not P else 1340) - wy
    PLW = 620 if (P and callwin(X, b)) else L[2]      # 9:16 with a host: the palette leaves the right side to the call window
    q = str(b.get("query", ""))
    qpx = fit_px(q, L[2] - 140, 34 if not P else 44, 18)
    res = b.get("results") or []
    area = wb - 44 - 100 - 44
    rowh = min(74 if not P else 136, area / max(len(res), 1))
    cap = len(res)
    if rowh < 40:
        cap = max(1, int(area // 40) - 1); rowh = area / (cap + 1)
    shown = res[:cap]; more = len(res) - len(shown)
    rfs = max(15, min(30 if not P else 46, rowh * 0.4))
    rows = "".join(f'<div class="r{" hot" if (len(r) > 2 and r[2]) else ""}" style="height:{rowh:.0f}px; font-size:{rfs:.0f}px"><span><i></i>{X.rich(r[0])}</span><b>{X.rich(r[1] if len(r) > 1 else "")}</b></div>' for r in shown)
    if more: rows += f'<div class="r more" style="height:{rowh:.0f}px; font-size:{rfs * 0.85:.0f}px"><span>{X.rich(f"…… 还有 {more} 项")}</span></div>'
    sk = next((k for k, r in enumerate(shown) if len(r) > 2 and r[2]), 0)
    srch = '<svg viewBox="0 0 30 30"><circle cx="13" cy="13" r="9" fill="none" stroke="#5b5b66" stroke-width="3"/><path d="M20 20l7 7" stroke="#5b5b66" stroke-width="3" stroke-linecap="round"/></svg>'
    if P:
        note = win(X, "nw", "note.txt", f'<div class="ab tha" style="left:34px; top:26px; width:{NW[2] - 60}px">{ah}</div>', sty=box(*NW), bar="sun", tilt=-1.6) if anl else ""
    else:
        note = f'<div class="ab tha" style="left:{L[0]}px; top:{L[1]}px; width:{L[2]}px">{ah}</div>' if anl else ""
    inner = (f'<div class="sc sc-pal"><div class="bgfx"></div><div class="cam">' + note
             + f'<div class="ab thb" style="left:{L[0]}px; top:{by:.0f}px; width:{L[2]}px">{bh}</div>'
             + win(X, "pl", "⌘K", f'<div class="in" style="font-size:{qpx}px">{srch}<span class="qq">{chars(X, q)}<i class="caret"></i></span></div>'
                   f'<i class="sel" style="height:{rowh:.0f}px"></i><div class="rs">{rows}</div><div class="kb">↑↓ 选择 · ↵ 打开</div>', sty=box(L[0], wy, PLW, wb), bar="cobalt", tilt=0.8 if P else 0)
             + CURSOR + f'</div>{callwin(X, b)}{furn(X, b)}</div>')
    X.used_text.update("⌘K↑↓选择↵打开")
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tb, ts = T(X, b, "at_b", t, t + d * 0.4), T(X, b, "at_sel", t, t + d * 0.6)
    rise(X, f"{s} .win", t, st=0.1, icon=SCENE_ICON["palette"])
    if anl and not P: X.tw(f'tl.from("{s} .tha", {{opacity:0, y:20, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .thb", {{opacity:0, y:30, scale:0.94, transformOrigin:"0 50%", duration:0.35, ease:"back.out(1.4)"}}, {tb - 0.2:.3f});')
    rows_y = wy + 46 + 100
    cursor_path(X, f"{s} .cur", [(t + 0.25, L[0] + 520, wy + 46 + 42, True), (ts - 0.05, L[0] + PLW - 260, rows_y + rowh * (sk + 0.5), True),
                                 (ts + 0.8, L[0] + PLW - 300, rows_y + rowh * (sk + 1.6), False)])
    each = min(0.05, 0.8 / max(len(q), 1))       # the query types fast; results list right after it (no empty window)
    typing(X, f"{s} .qq", t + 0.25, len(q), each)
    X.tw(f'tl.from("{s} .r", {{opacity:0, x:-20, duration:0.25, ease:"back.out(1.4)", stagger:0.05}}, {t + 0.3 + len(q) * each:.3f});')
    X.tw(f'tl.from("{s} .sel", {{opacity:0, duration:0.2}}, {t + 0.35 + len(q) * each:.3f});')
    X.tw(f'tl.to("{s} .sel", {{y:{rowh * sk:.1f}, duration:0.45, ease:"power3.inOut"}}, {ts - 0.2:.3f});')
    X.sfx(ts, "click")
    if any(len(r) > 2 and r[2] for r in shown): X.tw(f'tl.fromTo("{s} .r.hot", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.15}}, {{scale:1, duration:0.3}}], transformOrigin:"0 50%", immediateRender:false}}, {ts + 0.25:.3f});')
    shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.4, 0.5), (tb - 0.4, 1.0, 0.5, 0.5)] if not P else [(t, 1.0, 0.5, 0.5)])


def outro(b, X, t, d, cid):
    P = X.portrait
    X.css("sc-out", """
.sc-out .aic { position:absolute; border-radius:24%; background:var(--cobalt); border:1.5px solid #1b1b1f; box-shadow:8px 8px 0 #1b1b1f;
  display:grid; place-items:center; font-family:var(--f-num); font-weight:800; color:#ffffff; }
.sc-out .ttl { font-family:var(--f-display); font-weight:800; color:var(--fg); letter-spacing:-.01em; }
.sc-out .sub { color:var(--muted); }
.sc-out .cta { position:absolute; font-weight:800; color:#1b1b1f; background:var(--sun); padding:14px 34px; border-radius:12px; border:1.5px solid #1b1b1f; box-shadow:6px 6px 0 #1b1b1f; white-space:nowrap; }
""")
    title = str(b.get("title", X.channel))
    if P:   # an "about" window filled by logo tile + name, a "follow" window with the CTA under it, the host on a call
        AW, SW = (40, 300, 1000, 660), (56, 990, 620, 350)
        ic = (48, 36, 230); tx, ty, tw_ = 48, 296, 900
    else:   # 16:9: about window on the left (58 % wide), follow window on the right
        AW, SW = (60, 100, 1120, 740), (1232, 120, 600, 340)
        ic = (52, 52, 260); tx, ty, tw_ = 52, 360, 1000
    tpx = fit_px(title, tw_, 170, 40)
    sub, spx, snl = fit(X, b.get("sub", ""), tw_, 140, 54 if P else 46, 30, 2, 1.25)
    cta = str(b.get("cta", ""))
    body = (f'<div class="aic" style="{box(ic[0], ic[1], ic[2], ic[2])}; font-size:{ic[2] * 0.6:.0f}px">{X.rich(b.get("icon", "9"))}</div>'
            f'<div class="ab ttl" style="left:{tx}px; top:{ty}px; font-size:{tpx}px; white-space:nowrap">{X.rich(title, split="chars")}</div>'
            f'<div class="ab sub" style="left:{tx + 6}px; top:{ty + tpx * 1.2:.0f}px; width:{tw_}px">{sub}</div>')
    cpx = fit_px(cta, SW[2] - 140, 60 if P else 50, 24)
    cy = (SW[3] - 46) / 2 - cpx * 0.85
    sbody = (f'<div class="ab mono" style="left:34px; top:26px; font-size:28px; font-weight:700; color:#55555f">{X.rich(b.get("follow_label", "follow"))}</div>'
             + (f'<div class="cta" style="left:34px; top:{cy + 30:.0f}px; font-size:{cpx}px">{X.rich(cta)}</div>' if cta else ""))
    X.used_text.update("follow")
    inner = (f'<div class="sc sc-out"><div class="bgfx"></div><div class="cam">'
             + win(X, "aw", "about", body, sty=box(*AW), bar="cobalt", tilt=-1.0 if P else 0)
             + (win(X, "sw", "subscribe", sbody, sty=box(*SW), bar="sun", tilt=1.6 if P else 1.0) if cta else "")
             + CURSOR + f'</div>{callwin(X, b)}{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    rise(X, f"{s} .win", t, st=0.12, icon=SCENE_ICON["outro"])
    X.tw(f'tl.from("{s} .aic", {{scale:0.4, rotation:-20, opacity:0, duration:0.45, ease:"back.out(1.4)"}}, {t + 0.15:.3f});')
    if cta:
        cx_ = SW[0] + 34 + 160; cy_ = SW[1] + 46 + cy + 30 + cpx * 0.7
        cursor_path(X, f"{s} .cur", [(t + 0.5, cx_ + 300, cy_ + 260, False), (t + 1.25, cx_, cy_, True)])
        X.tw(f'tl.fromTo("{s} .cta", {{scale:1}}, {{keyframes:[{{scale:0.92, duration:0.08}}, {{scale:1, duration:0.2}}], immediateRender:false}}, {t + 1.25:.3f});')
    X.tw(f'tl.from("{s} .ttl .c", {{y:40, opacity:0, duration:0.55, ease:"expo.out", stagger:{min(0.05, 0.5 / max(len(title), 1)):.3f}}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .sub", {{opacity:0, y:16, duration:0.5}}, {t + 0.5:.3f});')
    if cta: X.tw(f'tl.from("{s} .cta", {{scale:0.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.75:.3f});')
    X.sfx(t + 0.1, "hit")


SCENES = {"dash": dash, "api": api, "pricing": pricing, "forecast": forecast, "shots": shots_wall, "palette": palette, "outro": outro}


# ---------------------------------------------------------------- effect cards (aefx FX_FRAME)
# Every gallery effect in this style sits inside the same product window: a translucent title bar (window dots ·
# channel breadcrumb · effect id chip), the spoken line as a prompt box (AI spark · typed text · lime keyword chip ·
# caret · return key) and a status bar (label · source). The effect itself gets the dot-grid ground with the two
# glows, and the UI pieces inside effects (toasts, tags, highlight boxes, code colours) are reskinned to match.
# All of it is injected here, so builds without effects (the showcase film) are untouched.
FX_CSS = r"""
/* the effect is the content of one desktop window: wallpaper dots on the ground, an outlined window with a coloured title
   bar and a hard offset shadow; outside the window the wallpaper colour shows (a wide flat shadow paints it) */
.st-screen .fx[style*="background:var(--bg)"]::before { content:''; position:absolute; inset:0; z-index:-1; pointer-events:none; background:
  radial-gradient(circle at 2px 2px, color-mix(in srgb, #1b1b1f 16%, transparent) 1.6px, transparent 2.2px) 0 0/32px 32px; }
.sf { pointer-events:none; font-family:var(--f-body); }
.sf .sf-win { position:absolute; left:26px; right:34px; top:18px; bottom:26px; border-radius:14px;
  box-shadow:0 0 0 1.5px #1b1b1f, 9.5px 9.5px 0 0 #1b1b1f, 0 0 0 2400px #ece9ee; }
.sf .sf-bar { position:absolute; left:26px; right:34px; top:18px; height:52px; border-radius:14px 14px 0 0; display:flex; align-items:center; padding:0 22px;
  background:var(--tomato, #ff5a3c); border-bottom:1.5px solid #1b1b1f; }
.sf .sf-dots { display:flex; gap:9px; flex:none; } .sf .sf-dots i { width:16px; height:16px; border-radius:50%; background:#fff; border:1.5px solid #1b1b1f; }
.sf .sf-crumb { position:absolute; left:50%; top:9px; height:34px; transform:translateX(-50%); display:flex; align-items:center; gap:10px; padding:0 14px;
  font:700 24px var(--f-mono); color:#1b1b1f; white-space:nowrap; }
.sf .sf-crumb b { color:#1b1b1f; font-weight:800; } .sf .sf-crumb em { font-style:normal; opacity:.55; }
.sf .sf-mark { width:18px; height:18px; border-radius:5px; background:#ffc21a; border:1.5px solid #1b1b1f; flex:none; }
.sf .sf-id { margin-left:auto; display:flex; align-items:center; gap:8px; height:32px; padding:0 12px; border-radius:999px; font:700 22px var(--f-mono); color:#fff;
  background:#1b1b1f; white-space:nowrap; }
.sf .sf-id i { color:#ffc21a; font-style:normal; }
.sf .sf-st { position:absolute; left:26px; right:34px; bottom:26px; height:40px; border-radius:0 0 14px 14px; display:flex; align-items:center; justify-content:space-between; gap:24px;
  padding:0 24px; font:600 22px var(--f-mono); color:#1b1b1f; background:#ffffff; border-top:1.5px solid #1b1b1f; }
.sf .sf-st > span { display:flex; align-items:center; gap:10px; white-space:nowrap; overflow:hidden; min-width:0; }
.sf .sf-st > span:last-child { justify-content:flex-end; }
.sf .sf-ok { width:12px; height:12px; border-radius:50%; background:#19c39a; border:1.5px solid #1b1b1f; flex:none; }
.sf .sf-cap { position:absolute; left:0; right:0; bottom:110px; display:flex; justify-content:flex-end; padding-right:90px; }
.sf .sf-box { position:relative; display:flex; align-items:center; gap:16px; max-width:calc(80% + 130px); padding:14px 20px 14px 16px; border-radius:14px;
  background:#ffffff; border:1.5px solid #1b1b1f; box-shadow:8px 8px 0 #1b1b1f; color:#1b1b1f; }
.sf .sf-ai { flex:none; width:40px; height:40px; border-radius:10px; background:#ffc21a; border:1.5px solid #1b1b1f; display:grid; place-items:center; }
.sf .sf-ai svg { width:22px; height:22px; }
.sf .sf-tx { font-weight:700; line-height:1.3; letter-spacing:.005em; text-align:left; white-space:nowrap; }   /* lines arrive pre-broken and fitted */
.sf .sf-tx .em .emt { background:#2f5bff; color:#ffffff; padding:0 .2em; border-radius:.22em; box-decoration-break:clone; -webkit-box-decoration-break:clone; }
.sf .sf-tx .em .emb { display:none; }
.sf .sf-caret { display:inline-block; width:4px; height:1.02em; margin-left:4px; vertical-align:-.14em; background:#2f5bff; border-radius:1px; }
.sf .sf-key { flex:none; width:42px; height:36px; border-radius:8px; display:grid; place-items:center; border:1.5px solid #1b1b1f; box-shadow:0 3px 0 #1b1b1f; }
.sf .sf-key svg { width:18px; height:18px; }
#root.v .sf .sf-win { left:28px; right:36px; top:200px; bottom:400px; }   /* 9:16: under the platform's top tabs */
#root.v .sf .sf-bar { left:28px; right:36px; top:200px; height:58px; padding:0 22px; }
#root.v .sf .sf-crumb { top:12px; font-size:24px; }
#root.v .sf .sf-st { left:28px; right:36px; bottom:400px; height:50px; padding:0 96px 0 30px; font-size:24px; }   /* the source ends clear of the right-hand buttons */
#root.v .sf .sf-cap { bottom:470px; padding:0 124px 0 120px; }   /* 9:16: the prompt box floats in the window's empty lower band, above the status bar */
#root.v .sf .sf-box { max-width:100%; padding:16px 24px; }
#root.v .sf .sf-ai { position:absolute; left:-16px; top:-18px; width:40px; height:40px; border-radius:10px; }
/* effect internals: notes, tags, highlights and code take the desktop UI language */
.st-screen .fx .nt { background:#ffffff; color:#1b1b1f; border:1.5px solid #1b1b1f; border-radius:14px; box-shadow:8px 8px 0 #1b1b1f; }
.st-screen .fx .nt .ic { background:#ffc21a; color:#1b1b1f; border:1.5px solid #1b1b1f; border-radius:10px; }
.st-screen .fx .nt span { color:#3a3a44; } .st-screen .fx .nt em { color:#55555f; font-family:var(--f-mono); }
.st-screen .fx .gh { color:transparent; -webkit-text-stroke:2px color-mix(in srgb, var(--accent) 45%, transparent); }
.st-screen .fx .sc .g { color:#2f5bff; text-shadow:none; }
.st-screen .scr-frame.browser, .st-screen .scr-frame.none { border-radius:14px; box-shadow:0 0 0 1.5px #1b1b1f, 8px 8px 0 #1b1b1f; }
.st-screen .scr-tag { background:#ffc21a; color:#1b1b1f; font-family:var(--f-body); font-weight:800; border:1.5px solid #1b1b1f; border-radius:10px; box-shadow:6px 6px 0 #1b1b1f; }
.st-screen .scr-hl { border-width:4px; border-radius:12px; border-color:#2f5bff; box-shadow:6px 6px 0 #1b1b1f; }
.st-screen .scr-rip { border-color:#2f5bff; background:rgba(47,91,255,.2); }
.st-screen .cd-win { background:#1b1b1f; border-radius:14px; box-shadow:0 0 0 1.5px #1b1b1f, 8px 8px 0 #55555f; }
.st-screen .cd-win.term { background:#141417; }
.st-screen .cd-win .k { color:#b4a8ff; } .st-screen .cd-win .s { color:#7fe0b8; } .st-screen .cd-win .n { color:#ffb37a; } .st-screen .cd-win .f { color:#8fb0ff; }
.st-screen .cd-caret { background:#ffc21a; } .st-screen .cd-pr { color:#ffc21a; }
.st-screen .sp-out { stroke:#2f5bff; }
"""
SPARK = '<svg viewBox="0 0 24 24"><path d="M12 2.5c.7 4.7 2.6 7 7.2 8.1-4.6 1.1-6.5 3.4-7.2 8.1-.7-4.7-2.6-7-7.2-8.1 4.6-1.1 6.5-3.4 7.2-8.1z" fill="#1b1b1f"/><path d="M19 15.5c.25 1.6.9 2.4 2.5 2.8-1.6.4-2.25 1.2-2.5 2.8-.25-1.6-.9-2.4-2.5-2.8 1.6-.4 2.25-1.2 2.5-2.8z" fill="#1b1b1f"/></svg>'
RETURN = '<svg viewBox="0 0 24 24"><path d="M19 5v7a3 3 0 0 1-3 3H6m0 0 4-4m-4 4 4 4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


# the effect's own area = the window interior between title bar and status bar: the effect page is scaled (uniformly,
# about its centre) into it, so nothing it draws — toasts at the top included — ever sits under the bars
FX_AREA = {False: (26, 18 + 52, 1920 - 34, 1080 - 26 - 40), True: (28, 200 + 58, 1080 - 36, 1920 - 400 - 50)}   # 9:16: the window ends at the platform's bottom bar


def FX_FRAME(X, cid, t, d, p, k):
    X.css("screen-fx", FX_CSS)
    P = X.portrait
    x0, y0, x1, y1 = FX_AREA[bool(P)]
    sc = min((x1 - x0) / X.W, (y1 - y0) / X.H)
    dx, dy = (x0 + x1) / 2 - X.W / 2, (y0 + y1) / 2 - X.H / 2
    X.css(f"fxfit-{cid}", f"#{cid} {{ scale:{sc:.4f}; translate:{dx:.1f}px {dy:.1f}px; transform-origin:50% 50%; }}")
    th = STYLE["fx_themes"].get(p.get("theme") or "paper", STYLE["fx_themes"]["paper"])
    X.clip(f"{cid}w", t, d, "", "sfw", 1, track=21, sty=f"background:{th['bg']}; left:{x0}px; top:{y0}px; width:{x1 - x0}px; height:{y1 - y0}px; right:auto; bottom:auto")
    key = "" if P else f'<b class="sf-key">{RETURN}</b>'
    right_pad = ' style="padding-right:380px"' if (p.get("host") and not P) else ""   # the presenter sits bottom-right in 16:9
    X.used_text.update("" + X.channel + "/")
    inner = (f'<div class="sf-win"></div>'
             f'<div class="sf-bar"><span class="sf-dots"><i></i><i></i><i></i></span>'
             f'<span class="sf-crumb"><i class="sf-mark"></i><b>{X.rich(X.channel)}</b><em>/</em>{k["topic"]}</span>'
             f'<span class="sf-id"><i>fx</i>{k["fxid"]}</span></div>'
             f'<div class="sf-cap"><div class="sf-box"><i class="sf-ai">{SPARK}</i>'
             f'<span class="sf-tx" style="font-size:{k["cap_px"]}px">{k["cap"]}<i class="sf-caret"></i></span>{key}</div></div>'
             f'<div class="sf-st"{right_pad}><span><i class="sf-ok"></i>{k["foot"]}</span><span>{k["src"]}</span></div>')
    X.used_text.update("fx")
    X.clip(f"{cid}c", t, d, inner, f"ctx sf{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .sf-bar, {s} .sf-st", {{opacity:0, duration:0.25, ease:"power2.out"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .sf-box", {{y:22, opacity:0, scale:0.97, duration:0.38, ease:"expo.out"}}, {t + 0.05:.3f});')
    ty = min(0.7, max(0.35, d * 0.18))     # the line "types" in left to right, then the caret blinks
    X.tw(f'tl.fromTo("{s} .sf-tx", {{clipPath:"inset(-20% 100% -20% 0)"}}, {{clipPath:"inset(-20% 0% -20% 0)", duration:{ty:.2f}, ease:"steps({max(6, int(ty * 30))})", immediateRender:true}}, {t + 0.12:.3f});')
    blinks = max(0, int((d - 0.3 - ty) / 0.5))
    if blinks:
        X.tw(f'tl.to("{s} .sf-caret", {{opacity:0, duration:0.01, repeat:{blinks}, yoyo:true, repeatDelay:0.49, ease:"none"}}, {t + 0.2 + ty:.3f});')
    X.tw(f'tl.from("{s} .sf-ai", {{scale:0.4, rotation:-30, duration:0.45, ease:"back.out(2.2)"}}, {t + 0.08:.3f});')
