"""screen · AI 工具台 —— 给 AI 工具 / AI 变现类口播的暗色产品界面语言。
对标 Linear / Raycast / Arc 的发布片、OpenAI DevDay 的数据图、归藏的产品视频：近黑蓝底 + 极淡的紫 / 青柠光晕和点阵，
内容全部装在"窗口"里——仪表盘、终端、定价页、预测图、命令面板、截图墙；一个会移动、会点击的光标把视线带过去；
数字用表格数字滚动，唯一强调色是青柠绿。全部 HTML/CSS/SVG，界面是通用的，不仿任何品牌。

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

STYLE = {
    "name": "AI 工具台", "en": "Screen", "benchmarks": ["Linear / Raycast 发布片", "OpenAI DevDay 数据图", "归藏产品视频"],
    "tokens": {
        "bg": "#0a0c10", "fg": "#edf0f5", "muted": "#8a93a3", "accent": "#c6f45a", "accent2": "#9c8cff", "alert": "#ff7a59",
        "line": "rgba(255,255,255,.08)", "paper": "#0a0c10", "ink": "#0a0c10", "card": "#12161c", "card-fg": "#edf0f5",
        "lime": "#c6f45a", "violet": "#9c8cff", "dim": "#2a303a", "surf": "#12161c", "surf2": "#181d25",
        "cap-bg": "rgba(18,22,28,.86)", "cap-fg": "#edf0f5", "cap-size": "38px", "cap-weight": "600", "cap-pad": "10px 26px 12px",
        "cap-radius": "14px", "cap-shadow": "none", "cap-bottom": "60px", "cap-em": "#c6f45a",
        "punch-top": "70%", "punch-size": "68px",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": ["inter", "noto-sans-sc"], "mono": "jetbrains-mono", "num": "inter"},
    "motion": {"ease": "expo.out", "dur": 0.55, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static", "camera": "none"},
    "layers": [("grain", {"opacity": 0.035})],
    "mascot": {"mode": "cameo", "frame": "glow", "landscape": {"right": 60, "bottom": 0, "h": 380}, "portrait": {"left": 390, "bottom": 600, "h": 300}},
    "sfx": {"transition": ("whoosh_soft", 0.3), "enter": ("whoosh_soft", 0.28), "pop": ("pop", 0.4), "hit": ("hit", 0.35),
            "count": ("type", 0.25), "click": ("click", 0.45), "type": ("type", 0.3), "mascot": ("whoosh_soft", 0.3), "line": ("click", 0.3)},
    "css": r"""
.st-screen .cap .cp { border:1px solid rgba(255,255,255,.1); box-shadow:0 12px 40px rgba(0,0,0,.45); }
.st-screen .cap-punch .cp { font-weight:800; }
""",
}

CSS = r"""
.st-screen .em .emb { display:none; } .sc .em .emt { color:var(--lime); }
.sc { position:absolute; inset:0; background:var(--bg); overflow:hidden; }
.sc .bgfx { position:absolute; inset:-10%; background:
  radial-gradient(40% 50% at 12% 8%, rgba(156,140,255,.16), transparent 70%),
  radial-gradient(38% 46% at 92% 96%, rgba(198,244,90,.10), transparent 70%),
  radial-gradient(1.2px 1.2px at 1px 1px, rgba(255,255,255,.07) 1px, transparent 1.5px) 0 0/28px 28px; }
.sc .cam { position:absolute; inset:0; }
.sc .band { position:absolute; left:0; right:0; z-index:5; pointer-events:none; }
.sc .band.t { top:0; height:120px; background:linear-gradient(180deg, #0a0c10 62%, rgba(10,12,16,0)); }
.sc .band.b { bottom:0; height:70px; background:linear-gradient(0deg, #0a0c10 40%, rgba(10,12,16,0)); }
#root.v .sc .band.t { height:260px; } #root.v .sc .band.b { top:1440px; bottom:auto; height:480px; background:linear-gradient(180deg, rgba(10,12,16,0), #0a0c10 20%); }
.sc-hd { position:absolute; left:96px; right:96px; top:34px; height:44px; display:flex; align-items:center; justify-content:space-between; z-index:6;
  font-family:var(--f-body); font-size:20px; color:var(--fg); }
.sc-hd .l { display:flex; align-items:center; gap:12px; } .sc-hd .l i { width:12px; height:12px; border-radius:4px; background:var(--lime); box-shadow:0 0 14px rgba(198,244,90,.6); }
.sc-hd .l b { font-weight:700; letter-spacing:.02em; } .sc-hd .l span { color:var(--muted); }
.sc-hd .r { display:flex; align-items:center; gap:14px; font-family:var(--f-mono); font-size:16px; color:var(--muted); }
.sc-hd .r em { font-style:normal; color:var(--fg); border:1px solid rgba(255,255,255,.14); border-radius:999px; padding:3px 12px; }
.sc-ft { position:absolute; left:96px; right:96px; bottom:22px; display:flex; justify-content:space-between; align-items:center; z-index:6;
  font-family:var(--f-mono); font-size:15px; color:var(--muted); }
.sc-ft > div:first-child { max-width:80%; line-height:1.4; }
.sc-ft .pg { display:flex; gap:6px; } .sc-ft .pg i { width:6px; height:6px; border-radius:50%; background:#2f3540; } .sc-ft .pg i.on { background:var(--lime); }
#root.v .sc-hd { left:56px; right:56px; top:170px; } #root.v .sc-ft { left:56px; right:56px; bottom:auto; top:1478px; }
.win { position:absolute; border-radius:18px; background:linear-gradient(180deg, #161b23, #10141a); border:1px solid rgba(255,255,255,.09);
  box-shadow:0 30px 80px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.06); overflow:hidden; }
.win .tb { height:44px; display:flex; align-items:center; gap:8px; padding:0 16px; border-bottom:1px solid rgba(255,255,255,.06); font-family:var(--f-mono); font-size:15px; color:var(--muted); white-space:nowrap; }
.win .tb i { width:11px; height:11px; border-radius:50%; background:#323843; flex:none; } .win .tb span { margin-left:10px; overflow:hidden; text-overflow:ellipsis; }
.win .tb .tag { margin-left:auto; color:var(--lime); border:1px solid rgba(198,244,90,.35); border-radius:999px; padding:1px 10px; font-size:13px; }
.win .bd { position:absolute; left:0; right:0; top:44px; bottom:0; }
.sc .ab { position:absolute; }
.sc .ft { display:inline-block; white-space:nowrap; vertical-align:baseline; }
.sc .lbl { font-family:var(--f-body); font-weight:600; color:var(--muted); letter-spacing:.02em; }
.sc .num { font-family:var(--f-num); font-weight:700; font-variant-numeric:tabular-nums; letter-spacing:-.03em; color:var(--fg); line-height:1; white-space:nowrap; }
.sc .mono { font-family:var(--f-mono); }
.sc .lime { color:var(--lime); }
.sc .cur { position:absolute; left:0; top:0; width:34px; height:40px; z-index:8; filter:drop-shadow(0 6px 10px rgba(0,0,0,.5)); }
.sc .cur .rp { position:absolute; left:-18px; top:-18px; width:40px; height:40px; border-radius:50%; border:2px solid var(--lime); opacity:0; }
.sc .caret { display:inline-block; width:3px; height:1.05em; background:var(--lime); vertical-align:-.15em; margin-left:3px; }
/* adaptive image grid */
.sc .gr { position:absolute; }
.sc .ph { position:absolute; border-radius:12px; overflow:hidden; background:#0d1015; border:1px solid rgba(255,255,255,.08); }
.sc .ph img { position:absolute; inset:0; width:100%; height:100%; display:block; }
.sc .ph img.bk { object-fit:cover; filter:blur(18px) brightness(.45) saturate(.8); transform:scale(1.15); }
.sc .ph .more { position:absolute; inset:0; display:grid; place-items:center; background:rgba(10,12,16,.72); font-family:var(--f-num); font-weight:700; color:var(--fg); }
.sc .ph .cap2 { position:absolute; left:10px; bottom:8px; right:10px; font-size:16px; color:var(--fg); text-shadow:0 1px 6px rgba(0,0,0,.8); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sc .ph.sk { background:linear-gradient(180deg, #151a22, #10141a); }
.sc .ph.sk i { position:absolute; left:10%; height:8%; border-radius:6px; background:#222833; }
.sc .ph .hl { position:absolute; inset:0; border-radius:12px; border:3px solid var(--lime); box-shadow:inset 0 0 0 3px rgba(198,244,90,.2); opacity:0; }
"""

CURSOR = '<div class="cur"><i class="rp"></i><svg viewBox="0 0 34 40"><path d="M3 2 L3 31 L10.5 24.5 L15.5 36 L21 33.5 L16 22.5 L26 22.5 Z" fill="#fff" stroke="#0a0c10" stroke-width="2.4" stroke-linejoin="round"/></svg></div>'

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
                        f'<i style="top:14%; width:46%"></i><i style="top:30%; width:72%; background:#1b2029"></i><i style="top:44%; width:60%; background:#1b2029"></i>'
                        f'<i style="top:70%; width:34%; height:12%; background:rgba(198,244,90,.18)"></i></div>' for k, (x, y, w, h) in enumerate(rects))
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
    X.css("screen", CSS)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    src = b.get("src", meta.get("src", ""))
    sec, case = meta.get("section", "AI 工具台"), meta.get("case", "")
    pg = "".join(f'<i class="{"on" if k <= i else ""}"></i>' for k in range(n))
    X.used_text.update(sec + case + src + "0123456789/")
    return (f'<div class="band t"></div><div class="band b"></div>'
            f'<div class="sc-hd"><div class="l"><i></i><b>第九顶帽子</b><span>{X.rich(sec)}</span></div>'
            f'<div class="r">{X.rich(case)}<em>{i + 1:02d} / {n:02d}</em></div></div>'
            f'<div class="sc-ft"><div>{"来源：" + X.rich(src) if src else ""}</div><div class="pg">{pg}</div></div>')


def win(X, cls, title, body, tag="", sty=""):
    tg = f'<b class="tag">{X.rich(tag)}</b>' if tag else ""
    return f'<div class="win {cls}" style="{sty}"><div class="tb"><i></i><i></i><i></i><span data-layout-allow-overlap>{X.rich(title)}</span>{tg}</div><div class="bd">{body}</div></div>'


def box(x, y, w, h): return f"left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px"


def fmt_num(v, dec=0):
    return f"{v:,.{dec}f}" if dec else f"{round(v):,}"


def counter(X, sel, t, a, b, dur=1.0, dec=0, ease="power3.out", suffix=""):
    js = f"o.v.toLocaleString('en-US', {{minimumFractionDigits:{dec}, maximumFractionDigits:{dec}}})" if dec else "Math.round(o.v).toLocaleString('en-US')"
    X.used_text.update("0123456789.,")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"{ease}", onUpdate:()=>{{el.textContent={js}+"{suffix}";}}}}, {t:.3f});}})();')


def rise(X, sel, t, st=0.08, dur=0.7):
    X.tw(f'tl.from("{sel}", {{y:46, opacity:0, scale:0.965, duration:{dur}, ease:"expo.out", stagger:{st}}}, {t:.3f});')


def tiles_in(X, sel, t, n):
    X.tw(f'tl.from("{sel} .ph", {{y:30, opacity:0, scale:0.92, duration:0.55, ease:"expo.out", stagger:{min(0.08, 0.9 / max(n, 1)):.3f}}}, {t:.3f});')


def shots(X, sel, t, d, keys):
    """camera choreography: keys = [(time, scale, fx, fy)], fx/fy = point to centre (0–1). expo.inOut moves, slow creep while holding."""
    W, H = X.W, X.H
    def xy(sc, fx, fy):
        return min(0, max(W - sc * W, W / 2 - sc * fx * W)), min(0, max(H - sc * H, H / 2 - sc * fy * H))
    X.tw(f'tl.set("{sel}", {{transformOrigin:"0 0"}}, {t:.3f});')
    keys = sorted(k for k in keys if k[0] < t + d - 0.2) or [keys[0]]
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
            X.tw(f'tl.to("{sel}", {{x:{x:.0f}, y:{y:.0f}, duration:{max(0.25, min(0.75, tk - pt - 0.05)):.2f}, ease:"power2.inOut"}}, {max(pt + 0.05, tk - 0.75):.3f});')
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
.sc-dash .chat .q { position:absolute; right:24px; top:16px; color:#0a0c10; background:var(--fg); border-radius:18px 18px 4px 18px; padding:10px 18px; font-weight:600; }
.sc-dash .chat .a { position:absolute; left:24px; color:var(--fg); background:var(--surf2); border:1px solid rgba(255,255,255,.07); border-radius:18px 18px 18px 4px; padding:12px 18px; }
.sc-dash .chat .in { position:absolute; left:24px; right:24px; bottom:16px; height:48px; border-radius:14px; border:1px solid rgba(255,255,255,.1); background:#0d1015; font-size:20px; color:var(--muted); display:flex; align-items:center; padding:0 18px; white-space:nowrap; overflow:hidden; }
""")
    imgs = b.get("images") or []
    # ---- layout per orientation
    if P:
        M = (56, 260, 968, 620); side = bool(imgs)
        Pw = (56, 910, 470 if side else 968, 340); C = (546, 910, 478, 340) if side else None
        big_box, lab_y, chart = (880, 130), 172, (44, 236, 880, 300)
        dn = (24, 40, 200) if side else (30, 30, 250)
    else:
        M = (96, 120, 1000, 760); Pw = (1136, 120, 688, 380); C = (1136, 530, 688, 350)
        big_box, lab_y, chart = (912, 160), 206, (44, 280, 912, 400)
        dn = (40, 30, 270)
    value = b.get("value", 800_000_000)
    vtxt = fmt_num(value, int(b.get("value_dec", 0)))
    npx = fit_px(vtxt, big_box[0], 150 if not P else 118, 40)
    lab, _, _ = fit(X, b.get("label", ""), big_box[0], 62, 28, 16, 2, 1.2, "lbl")
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
    fs = 24 if n <= 6 else 20
    grid = "".join(f'<line x1="0" x2="{cw}" y1="{chh - 30 - g * (chh - 76) / 4:.1f}" y2="{chh - 30 - g * (chh - 76) / 4:.1f}" stroke="rgba(255,255,255,.06)"/>' for g in range(5))
    dots = []
    for k, (x, y, (lab_k, v)) in enumerate(zip(xs, ys, pts)):
        show = k % step == 0 or k == n - 1
        vt = f"{float(v):,.0f}{unit}" if float(v) == int(float(v)) else f"{float(v):g}{unit}"
        dots.append(f'<g class="pt" data-k="{k}"><circle cx="{x:.1f}" cy="{y:.1f}" r="{9 if n <= 8 else 7}" fill="#0a0c10" stroke="#c6f45a" stroke-width="4"/>'
                    + (f'<text x="{x:.1f}" y="{chh - 2}" fill="#8a93a3" font-size="{fs - 4}" text-anchor="middle" font-family="JetBrains Mono, monospace">{X.rich(lab_k)}</text>'
                       f'<text x="{x:.1f}" y="{y - 20:.1f}" fill="#edf0f5" font-size="{fs}" font-weight="700" text-anchor="middle" font-family="Inter, sans-serif">{X.rich(vt)}</text>' if show else "")
                    + "</g>")
        X.used_text.update(vt + str(lab_k))
    hk = min(max(int(b.get("hl", 0)), 0), n - 1)
    t0txt = str(b.get("tag0", ""))
    tw_ = 24 + 21 * est_w(t0txt)
    tx = xs[hk] + 36 if xs[hk] + 36 + tw_ < cw else xs[hk] - 36 - tw_
    ring = (f'<circle class="ring0" cx="{xs[hk]:.1f}" cy="{ys[hk]:.1f}" r="26" fill="none" stroke="#c6f45a" stroke-width="3"/>'
            + (f'<g class="t0"><rect x="{tx:.1f}" y="{max(4, ys[hk] - 62):.1f}" width="{tw_:.0f}" height="40" rx="9" fill="#c6f45a"/>'
               f'<text x="{tx + 12:.1f}" y="{max(4, ys[hk] - 62) + 28:.1f}" fill="#0a0c10" font-size="22" font-weight="700" font-family="Inter, sans-serif">{X.rich(t0txt)}</text></g>' if t0txt else ""))
    svg = (f'<svg class="ch ab" viewBox="0 0 {cw} {chh}" style="{box(cx, cy, cw, chh)}; overflow:visible"><defs><linearGradient id="ar{cid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c6f45a" stop-opacity=".28"/>'
           f'<stop offset="1" stop-color="#c6f45a" stop-opacity="0"/></linearGradient></defs>{grid}<path class="ar" d="{area}" fill="url(#ar{cid})"/>'
           f'<path class="ln" d="{path}" pathLength="1" fill="none" stroke="#c6f45a" stroke-width="5" stroke-linejoin="round" stroke-linecap="round"/>{"".join(dots)}{ring}</svg>')
    # ---- share card
    pv = float(b.get("paid", 5)); pvs = f"{pv:g}"
    dx, dy, dsz = dn
    pvx = dx + dsz + 30; pvw = Pw[2] - pvx - 24
    pnpx = fit_px(pvs + "%", pvw, 120 if not P else 104, 36)
    plab, _, _ = fit(X, b.get("paid_label", ""), pvw, Pw[3] - 44 - (dy + pnpx + 24) - 12, 24, 14, 4, 1.45, "lbl")
    donut = (f'<svg class="dn ab" viewBox="0 0 120 120" style="{box(dx, dy, dsz, dsz)}"><circle cx="60" cy="60" r="48" fill="none" stroke="#2a303a" stroke-width="16"/>'
             f'<circle class="arc" cx="60" cy="60" r="48" fill="none" stroke="#c6f45a" stroke-width="16" pathLength="100" stroke-dasharray="0 100" transform="rotate(-90 60 60)"/>'
             f'<text x="60" y="56" text-anchor="middle" fill="#8a93a3" font-size="10" font-family="JetBrains Mono, monospace">{X.rich(b.get("donut_tag", "PAID"))}</text>'
             f'<text x="60" y="74" text-anchor="middle" fill="#edf0f5" font-size="16" font-weight="700" font-family="Inter, sans-serif">≈{pvs}%</text></svg>')
    X.used_text.update(f"≈{pvs}%")
    pbody = (f'{donut}<div class="ab pv" style="left:{pvx}px; top:{dy + 12}px; width:{pvw}px"><div class="num" style="font-size:{pnpx}px; color:var(--lime)"><span class="n2">0</span>%</div>'
             f'<div class="lbl" style="margin-top:12px">{plab}</div></div>')
    # ---- chat pane or screenshots
    cbody, ctitle, nimg = "", "chat", 0
    q = str(b.get("q", ""))
    if C:
        if imgs:
            g, nimg = gallery(X, imgs, C[2] - 40, C[3] - 44 - 36, 12, sty="left:20px; top:18px")
            cbody, ctitle = g, b.get("images_title", "screenshots")
        else:
            qpx = fit_px(q, C[2] - 48 - 140, 26, 16) if q else 22
            ahtml, apx, anl = fit(X, b.get("answer", ""), C[2] - 48 - 40, C[3] - 44 - 16 - 48 - 16 - 88 - 26, 24, 15, 3, 1.5)
            cbody = (f'<div class="q">{chars(X, q, qpx)}<i class="caret"></i></div>'
                     f'<div class="a" style="top:{30 + qpx * 1.3 + 28:.0f}px; max-width:{C[2] - 48}px">{ahtml}</div>'
                     f'<div class="in">{X.rich(b.get("input", "问点什么……"))}</div>')
    inner = (f'<div class="sc sc-dash"><div class="bgfx"></div><div class="cam">'
             + win(X, "m", b.get("title", "weekly_active_users"), f'<div class="ab" style="left:44px; top:{30 if P else 34}px"><div class="num n" style="font-size:{npx}px">0</div></div>'
                   f'<div class="ab" style="left:44px; top:{lab_y}px; width:{big_box[0]}px">{lab}</div>{svg}', tag="LIVE", sty=box(*M))
             + win(X, "p", "paid_share", pbody, sty=box(*Pw))
             + (win(X, "chat", ctitle, cbody, sty=box(*C)) if C else "")
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.used_text.update("%")
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn, tp, t0 = T(X, b, "at_num", t, t + 0.5), T(X, b, "at_paid", t, t + d * 0.45), T(X, b, "at_then", t, t + d * 0.7)
    rise(X, f"{s} .win", t, st=0.1)
    X.sfx(t, "enter")
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
    if C and not imgs and not P:
        typing(X, f"{s} .chat .q", t + 0.6, len(q), min(0.05, 1.4 / max(len(q), 1)))
        X.tw(f'tl.from("{s} .chat .a", {{opacity:0, y:16, duration:0.5, ease:"expo.out"}}, {t + 0.7 + min(len(q) * 0.05, 1.4):.3f});')
    if not P:
        cursor_path(X, f"{s} .cur", [(t + 0.3, 1500, 860, False), (t + 0.55, 1560, 836, True), (tp - 0.3, 1420, 330, False),
                                    (max(t0 - 0.2, tp + 0.4), M[0] + cx + xs[hk] + 40, M[1] + 44 + cy + ys[hk] + 40, False)])
    else:
        X.tw(f'tl.set("{s} .cur", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.set("{s} .ring0{", " + s + " .t0" if t0txt else ""}", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .ring0", {{scale:0.3, opacity:0, transformOrigin:"50% 50%"}}, {{scale:1, opacity:1, duration:0.45, ease:"back.out(2.5)", immediateRender:false}}, {t0:.3f});')
    if t0txt: X.tw(f'tl.to("{s} .t0", {{opacity:1, duration:0.35}}, {t0 + 0.1:.3f});')
    X.sfx(t0, "pop")
    hx = (M[0] + cx + xs[hk]) / X.W; hy = (M[1] + 44 + cy + ys[hk]) / X.H
    if P:
        shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.5, 0.25), (tp - 0.5, 1.0, 0.5, 0.5), (t0 - 0.2, 1.06, max(0.3, min(0.7, hx)), 0.35)])
    else:
        shots(X, f"{s} .cam", t, d, [(t, 1.1, 0.3, 0.22), (tp - 0.45, 1.0, 0.5, 0.5), (t0 - 0.25, 1.12, max(0.2, min(0.8, hx)), max(0.3, min(0.7, hy)))])


def api(b, X, t, d, cid):
    """an API console streaming request logs, a big per-minute counter with a full-number ticker, and a throughput strip
    (or screenshots). params: label, big, big_unit, value, unit, note, endpoints[], images."""
    P = X.portrait
    X.css("sc-api", """
.sc-api .tm .rows { position:absolute; left:28px; right:28px; top:16px; font-family:var(--f-mono); color:var(--muted); white-space:nowrap; }
.sc-api .tm .rows b { color:var(--lime); font-weight:500; } .sc-api .tm .rows u { text-decoration:none; color:var(--fg); }
.sc-api .tm .fade { position:absolute; left:0; right:0; top:0; height:120px; background:linear-gradient(180deg, #13171e, transparent); }
.sc-api .bars { position:absolute; overflow:hidden; }
.sc-api .bars .strip { position:absolute; left:0; bottom:0; display:flex; align-items:flex-end; gap:8px; }
.sc-api .bars i { flex:none; width:20px; border-radius:5px 5px 0 0; background:linear-gradient(180deg, #c6f45a, rgba(198,244,90,.25)); }
.sc-api .note { color:var(--fg); } .sc-api .note .em .emt { color:var(--lime); }
""")
    if P:
        TM, K = (56, 260, 968, 520), (56, 810, 968, 440)
        lw, nw, BX = 888, 480, (560, 0, 368, 300)
    else:
        TM, K = (96, 120, 1060, 760), (1196, 120, 628, 760)
        lw, nw, BX = 548, 548, (40, 0, 548, 230)
    kb = K[3] - 44
    lab, lpx, lnl = fit(X, b.get("label", ""), lw, 64, 24, 15, 2, 1.25, "lbl")
    big = float(b.get("big", 60)); bu = str(b.get("big_unit", ""))
    btxt = f"{big:g}"
    npx = fit_px(btxt + "".join("中" for _ in bu) * 1, nw, 190 if not P else 170, 48)
    ny = 36 + lnl * lpx * 1.25 + 14
    unit = str(b.get("unit", ""))
    vtxt = fmt_num(b.get("value", 0)) + " " + unit if b.get("value") is not None else unit
    upx = fit_px(vtxt, nw, 26, 13)
    uy = ny + npx * 1.0 + 16
    imgs = b.get("images") or []
    if P:
        bx, bw, bh = BX[0], BX[2], BX[3]; by = kb - 36 - bh
        nh_html, nh_px, _ = fit(X, b.get("note", ""), BX[0] - 80, kb - (uy + upx + 24) - 30, 24, 14, 3, 1.45, "note")
        note_y = uy + upx + 24
    else:
        nh_html, nh_px, nnl = fit(X, b.get("note", ""), lw, 110, 24, 14, 3, 1.45, "note")
        note_y = kb - 40 - nnl * nh_px * 1.45
        bx, bw = BX[0], BX[2]; by = uy + upx + 30; bh = max(80, note_y - 24 - by)
    r = X.rand
    eps = b.get("endpoints") or ["/v1/responses", "/v1/chat/completions", "/v1/embeddings", "/v1/responses", "/v1/realtime", "/v1/images", "/v1/responses"]
    lh = 36 if P else 42; fs = 19 if P else 22
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
             f'<div class="ab num" style="left:36px; top:{ny:.0f}px; font-size:{npx}px"><span class="n">0</span><small style="font-family:var(--f-display); font-size:.47em; font-weight:800; margin-left:8px; letter-spacing:0">{X.rich(bu)}</small></div>'
             f'<div class="ab mono lime" style="left:40px; top:{uy:.0f}px; font-size:{upx}px; white-space:nowrap">'
             + (f'<span class="n3">0</span> {X.rich(unit)}' if b.get("value") is not None else X.rich(unit)) + '</div>'
             f'{right}<div class="ab note" style="left:40px; top:{note_y:.0f}px; width:{(BX[0] - 80) if P else lw}px">{nh_html}</div>')
    inner = (f'<div class="sc sc-api"><div class="bgfx"></div><div class="cam">'
             + win(X, "tm", b.get("log_title", "api.log — tail -f"), f'<div class="rows" style="font-size:{fs}px; line-height:{lh}px">{"".join(rows)}</div><div class="fade"></div>', tag="STREAMING", sty=box(*TM))
             + win(X, "k", "throughput", kbody, sty=box(*K))
             + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + d * 0.6)
    rise(X, f"{s} .win", t, st=0.1)
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
    if P:
        shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.5, 0.3), (tn - 0.3, 1.0, 0.5, 0.5)])
    else:
        shots(X, f"{s} .cam", t, d, [(t, 1.12, 0.3, 0.45), (tn - 0.4, 1.08, 0.72, 0.42)])


def pricing(b, X, t, d, cid):
    """headline counter, 1–8 plan cards the cursor visits, and a 100-person grid with the paying share lit.
    params: value, unit, label, plans [[name, price, per, note]], focus [i, j], paid_cells (0–100), legend [[name, value, on|'']]."""
    P = X.portrait
    plans = b.get("plans") or [["Free", "$0", "/ 月", ""]]
    N = len(plans)
    X.css("sc-pr", """
.sc-pr .cd { position:absolute; border-radius:16px; background:#0e1217; border:1px solid rgba(255,255,255,.08); overflow:hidden; }
.sc-pr .cd h4 { margin:0; font-family:var(--f-body); font-weight:700; color:var(--fg); white-space:nowrap; }
.sc-pr .cd .pr { font-family:var(--f-num); font-weight:700; letter-spacing:-.03em; color:var(--fg); line-height:1; white-space:nowrap; }
.sc-pr .cd .pr small { font-size:.32em; color:var(--muted); font-weight:500; margin-left:6px; letter-spacing:0; }
.sc-pr .cd p { margin:0; color:var(--muted); }
.sc-pr .cd .bt { position:absolute; border-radius:12px; display:grid; place-items:center; font-weight:700; color:var(--fg); border:1px solid rgba(255,255,255,.14); }
.sc-pr .cd .hv { position:absolute; inset:0; border-radius:16px; border:2px solid var(--lime); box-shadow:inset 0 0 0 4px rgba(198,244,90,.10); opacity:0; }
.sc-pr .grid { position:absolute; display:grid; }
.sc-pr .grid i { border-radius:22%; background:#232933; }
.sc-pr .grid i.on { background:var(--lime); box-shadow:0 0 18px rgba(198,244,90,.45); }
.sc-pr .leg div { display:flex; justify-content:space-between; align-items:baseline; color:var(--muted); border-top:1px solid rgba(255,255,255,.07); white-space:nowrap; gap:12px; }
.sc-pr .leg b { font-family:var(--f-num); color:var(--fg); letter-spacing:-.02em; } .sc-pr .leg .on b { color:var(--lime); }
""")
    if P:
        PW, GW = (56, 260, 968, 640), (56, 930, 968, 320)
        area = (28, 210, 912, 640 - 44 - 210 - 24); maxcols = 3
        gcols, gcell, ggap, gpos = 20, 19, 6, (36, 30); legbox = (580, 24, 352, 250)
    else:
        PW, GW = (96, 120, 1100, 760), (1236, 120, 588, 760)
        area = (40, 240, 1020, 760 - 44 - 240 - 30); maxcols = 4
        gcols, gcell, ggap, gpos = 10, 38, 12, (44, 40); legbox = (44, 40 + 10 * 50 + 24, 500, 760 - 44 - (40 + 10 * 50 + 24) - 24)
    head_v = float(b.get("value", 0)); htxt = fmt_num(head_v)
    hu = str(b.get("unit", ""))
    hpx = fit_px(htxt + hu, area[2] * 0.8, 104 if not P else 96, 40)
    lab, _, _ = fit(X, b.get("label", ""), area[2], 50, 24, 14, 1, 1.2, "lbl")
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
        nh = fit(X, note, cw - 2 * pad, nbox, 22 * max(sc, .75), 13, 3, 1.5)[0] if note and nbox > 22 else ""
        btn = "当前方案" if k == 0 and b.get("first_is_current", True) else b.get("cta", "升级")
        cards.append(f'<div class="cd" data-k="{k}" style="{box(x, y, cw, chh)}"><i class="hv"></i>'
                     f'<h4 class="ab" style="left:{pad:.0f}px; top:{pad:.0f}px; font-size:{npx_}px">{X.rich(name)}</h4>'
                     f'<div class="pr ab" style="left:{pad:.0f}px; top:{pad + npx_ * 1.2 + 18 * sc:.0f}px; font-size:{ppx}px">{X.rich(price)}<small>{X.rich(per)}</small></div>'
                     f'<p class="ab" style="left:{pad:.0f}px; right:{pad:.0f}px; top:{top_used:.0f}px">{nh}</p>'
                     + (f'<div class="bt" style="left:{pad:.0f}px; right:{pad:.0f}px; bottom:{pad:.0f}px; height:{bh:.0f}px; font-size:{max(13, 22 * sc):.0f}px">{X.rich(btn)}</div>' if bh else "") + '</div>')
    X.used_text.update("当前方案升级")
    paid = max(0, min(100, int(b.get("paid_cells", 5))))
    order = list(range(100)); X.rand.shuffle(order); lit = set(order[:paid])
    grid = "".join(f'<i class="{"on" if k in lit else ""}" style="width:{gcell}px; height:{gcell}px"></i>' for k in range(100))
    legs = b.get("legend") or []
    nl = max(1, len(legs)); rowh = min(64, legbox[3] / nl)
    lfs = max(14, min(24, rowh * 0.42)); bfs = max(18, min(44, rowh * 0.7))
    leg = "".join(f'<div class="{c if len(it) > 2 else ""}" style="height:{rowh:.0f}px; font-size:{fit_px(str(a), legbox[2] * 0.6, lfs, 12)}px"><span>{X.rich(a)}</span>'
                  f'<b style="font-size:{fit_px(str(v), legbox[2] * 0.4, bfs, 14)}px">{X.rich(v)}</b></div>'
                  for it in legs for a, v, c in [(it[0], it[1], it[2] if len(it) > 2 else "")])
    gtitle = b.get("grid_title", "100 users")
    inner = (f'<div class="sc sc-pr"><div class="bgfx"></div><div class="cam">'
             + win(X, "pw", b.get("title", "pricing"), f'<div class="ab" style="left:40px; top:{30 if P else 34}px; white-space:nowrap"><span class="num n" style="font-size:{hpx}px; color:var(--lime)">0</span>'
                   f'<span style="font-size:{hpx * 0.38:.0f}px; font-weight:700; color:var(--fg); margin-left:16px">{X.rich(hu)}</span></div>'
                   f'<div class="ab" style="left:40px; top:{area[1] - 70 if not P else 150}px; width:{area[2]}px">{lab}</div>{"".join(cards)}', sty=box(*PW))
             + win(X, "gw", gtitle, f'<div class="grid" style="left:{gpos[0]}px; top:{gpos[1]}px; grid-template-columns:repeat({gcols}, {gcell}px); gap:{ggap}px">{grid}</div>'
                   f'<div class="leg ab" style="{box(*legbox)}">{leg}</div>', sty=box(*GW))
             + CURSOR + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tn = T(X, b, "at_num", t, t + 0.6)
    t1, t2, tf = T(X, b, "at_p1", t, t + d * 0.35), T(X, b, "at_p2", t, t + d * 0.5), T(X, b, "at_free", t, t + d * 0.72)
    rise(X, f"{s} .win", t, st=0.1)
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
    if P:
        X.tw(f'tl.set("{s} .cur", {{opacity:0}}, {t:.3f});')
        shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.5, 0.25), (t1 - 0.5, 1.0, 0.5, 0.45), (tf - 0.4, 1.06, 0.5, 0.55)])
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
.sc-fc .toast { position:absolute; border-radius:16px; background:#1b212b; border:1px solid rgba(255,255,255,.1); padding:18px 22px; box-shadow:0 20px 60px rgba(0,0,0,.5); display:flex; gap:16px; }
.sc-fc .toast > i { flex:none; width:44px; height:44px; border-radius:12px; background:var(--violet); display:grid; place-items:center; color:#0a0c10; font-style:normal; font-weight:800; font-size:24px; }
.sc-fc .toast b { display:block; color:var(--fg); font-weight:700; } .sc-fc .toast span.bd2 { display:block; margin-top:6px; color:var(--muted); }
.sc-fc .toast em { font-style:normal; display:inline-block; margin-top:8px; font-family:var(--f-mono); font-size:15px; color:var(--alert); border:1px solid rgba(255,122,89,.45); border-radius:999px; padding:1px 10px; white-space:nowrap; }
""")
    FW = (56, 260, 968, 990) if P else (96, 120, 1728, 760)
    cw, ch = FW[2], FW[3] - 44
    bars = b.get("bars") or []
    nb = max(1, len(bars))
    toast = b.get("toast") or []
    if P:
        tbox = (36, ch - 36 - 170, cw - 72, 170)
    else:
        tbox = (cw - 40 - 560, 40, 560, 190)
    aw = (tbox[0] - 44 - 30) if (any(toast) and not P) else cw - 88
    hd, hpx, _ = fit(X, b.get("heading", ""), aw, 44, 34, 18, 1, 1.2, "hd2")
    hs, spx, _ = fit(X, b.get("heading_sub", ""), aw, 34, 26, 14, 1, 1.2, "lbl")
    sub_inline = (not P) and hs and est_w(b.get("heading", "")) * hpx + 14 + est_w(b.get("heading_sub", "")) * spx <= aw
    tt = (toast + ["", "", ""])[:3]
    t_title = fit(X, tt[0], tbox[2] - 110, 32, 24, 14, 1)[0]
    t_body = fit(X, tt[1], tbox[2] - 110, tbox[3] - 36 - 32 - 40, 20, 13, 3, 1.45)[0]
    num_y = 28 + hpx * 1.2 + 10 + (0 if (not hs or sub_inline) else spx * 1.2 + 4)
    v = float(b.get("value", 0)); vt = f"{v:g}"
    unit = str(b.get("unit", ""))
    npx = fit_px(vt + unit, (cw - 88) * 0.45, 96, 36)
    tlab = fit(X, b.get("label", ""), (cw - 88) * 0.5, 34, 22, 13, 1)[0]
    base = ch - ((tbox[3] + 150) if P else 110); top = num_y + npx + 60
    if any(toast) and not P: top = max(top, tbox[1] + tbox[3] + 80)   # tall bars stay clear of the toast
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
            out.append(f'<rect class="bb" data-k="{k}" x="{x:.0f}" y="{base - h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="12" fill="#c6f45a"/>')
        else:
            out.append(f'<rect class="bb" data-k="{k}" x="{x:.0f}" y="{base - h:.0f}" width="{bw:.0f}" height="{h:.0f}" rx="12" fill="rgba(156,140,255,.14)" stroke="#9c8cff" stroke-width="3" stroke-dasharray="12 9"/>')
        vfs = fit_px(lab, spacing * 0.92, 44 if not P else 40, 16)
        yfs = fit_px(yr, spacing * 0.92, 26, 13)
        out.append(f'<text class="bv" data-k="{k}" x="{xs[k]:.0f}" y="{base - h - 20:.0f}" text-anchor="middle" fill="#edf0f5" font-size="{vfs}" font-weight="700" font-family="Inter, sans-serif">{X.rich(lab)}</text>')
        out.append(f'<text x="{xs[k]:.0f}" y="{base + 44:.0f}" text-anchor="middle" fill="#8a93a3" font-size="{yfs}" font-family="JetBrains Mono, monospace">{X.rich(yr)}</text>')
        if k < len(notes) and notes[k]:
            nfs = fit_px(str(notes[k]), spacing * 0.95, 24, 12)
            out.append(f'<text class="bn" data-k="{k}" x="{xs[k]:.0f}" y="{base + 84:.0f}" text-anchor="middle" fill="#edf0f5" font-size="{nfs}" font-family="Inter, sans-serif">{X.rich(notes[k])}</text>')
        X.used_text.update(yr + lab)
    ax = f'<line x1="40" x2="{cw - 40}" y1="{base}" y2="{base}" stroke="rgba(255,255,255,.15)" stroke-width="2"/>'
    arw = mult = ""
    if nb >= 2:
        x1, x2 = xs[0] + bw / 2 + 20, xs[-1] - bw / 2 - 24
        h0 = (float(bars[0][1]) / vmax) * (base - top); h1 = (float(bars[-1][1]) / vmax) * (base - top)
        arw = f'<path class="arw" d="M{x1:.0f},{base - h0 - 40:.0f} C{(x1 + x2) / 2:.0f},{base - h0 - 60:.0f} {(x1 + x2) / 2:.0f},{base - h1 + 20:.0f} {x2:.0f},{base - h1 + 40:.0f}" pathLength="1" fill="none" stroke="#9c8cff" stroke-width="4" stroke-dasharray="1 1"/>'
        if b.get("mult"):
            mult = f'<text class="mx" x="{(x1 + x2) / 2:.0f}" y="{(base - h0 + base - h1) / 2 - 20:.0f}" text-anchor="middle" fill="#9c8cff" font-size="{fit_px(str(b["mult"]), spacing * 0.6, 40, 16)}" font-weight="700" font-family="Inter, sans-serif">{X.rich(b["mult"])}</text>'
    tst = (f'<div class="toast" style="{box(*tbox)}"><i>i</i><div style="min-width:0">'
           f'<b>{t_title}</b><span class="bd2">{t_body}</span>' + (f'<em>{X.rich(tt[2])}</em>' if tt[2] else "") + '</div></div>') if any(tt) else ""
    X.used_text.update("i")
    inner = (f'<div class="sc sc-fc"><div class="bgfx"></div><div class="cam">'
             + win(X, "fw", b.get("title", "forecast"), f'<svg viewBox="0 0 {cw} {ch}">{ax}{"".join(out)}{arw}{mult}</svg>'
                   f'<div class="ab" style="left:44px; top:28px; white-space:nowrap">{hd}' + (f'<span style="margin-left:14px">{hs}</span>' if sub_inline else "") + '</div>'
                   + (f'<div class="ab" style="left:44px; top:{28 + hpx * 1.2 + 4:.0f}px">{hs}</div>' if hs and not sub_inline else "")
                   + f'<div class="ab ttl" style="left:44px; top:{num_y:.0f}px"><div class="num" style="font-size:{npx}px; color:var(--lime)"><span class="n">0</span>{X.rich(unit)}</div>'
                   f'<div style="margin-top:10px">{tlab}</div></div>{tst}', sty=box(*FW))
             + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tp, tn = T(X, b, "at_year", t, t + d * 0.3), T(X, b, "at_num", t, t + d * 0.65)
    rise(X, f"{s} .win", t)
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
    if tst:
        X.tw(f'tl.from("{s} .toast", {{x:{0 if P else 80}, y:{60 if P else 0}, opacity:0, duration:0.55, ease:"expo.out"}}, {t + 0.9:.3f});')
        X.sfx(t + 0.9, "pop")
    if P:
        shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.4, 0.45), (tn - 0.6, 1.0, 0.5, 0.45)])
    else:
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
.sc-pal .tha .ft { text-decoration:line-through; text-decoration-thickness:4px; text-decoration-color:rgba(138,147,163,.8); }
.sc-pal .thb { font-family:var(--f-display); font-weight:800; color:var(--fg); letter-spacing:-.02em; }
.sc-pal .pl .in { position:absolute; left:0; right:0; top:0; height:84px; display:flex; align-items:center; gap:16px; padding:0 28px; color:var(--fg); border-bottom:1px solid rgba(255,255,255,.08); white-space:nowrap; overflow:hidden; }
.sc-pal .pl .in svg { width:30px; height:30px; flex:none; }
.sc-pal .pl .rs { position:absolute; left:14px; right:14px; top:100px; }
.sc-pal .pl .r { position:relative; display:flex; align-items:center; justify-content:space-between; padding:0 22px; border-radius:12px; color:var(--fg); white-space:nowrap; gap:20px; }
.sc-pal .pl .r span { display:flex; align-items:center; gap:16px; overflow:hidden; } .sc-pal .pl .r span i { width:12px; height:12px; border-radius:3px; background:#3a414d; flex:none; }
.sc-pal .pl .r b { font-family:var(--f-num); font-weight:700; color:var(--muted); letter-spacing:-.02em; }
.sc-pal .pl .r.hot b { color:var(--lime); } .sc-pal .pl .r.hot span i { background:var(--lime); }
.sc-pal .pl .r.more { color:var(--muted); }
.sc-pal .pl .sel { position:absolute; left:14px; right:14px; top:100px; border-radius:12px; background:rgba(198,244,90,.10); border:1px solid rgba(198,244,90,.45); }
.sc-pal .pl .kb { position:absolute; right:24px; bottom:14px; font-family:var(--f-mono); font-size:16px; color:var(--muted); }
""")
    L = (56, 270, 968) if P else (96, 126, 1180)
    ah, apx, anl = fit(X, b.get("a", ""), L[2], 130, 54 if not P else 46, 22, 2, 1.3)
    bh, bpx, bnl = fit(X, b.get("b", ""), L[2], 240 if not P else 260, 104 if not P else 96, 34, 2, 1.12)
    by = L[1] + (anl * apx * 1.3 + max(34, bpx * 0.3) if anl else 0)
    wy = by + bnl * bpx * 1.12 + 28
    wb = (920 if not P else 990) - wy
    if P and b.get("host"): wb = min(wb, 990 - wy)
    q = str(b.get("query", ""))
    qpx = fit_px(q, L[2] - 140, 34, 18)
    res = b.get("results") or []
    area = wb - 44 - 100 - 44
    rowh = min(74, area / max(len(res), 1))
    cap = len(res)
    if rowh < 40:
        cap = max(1, int(area // 40) - 1); rowh = area / (cap + 1)
    shown = res[:cap]; more = len(res) - len(shown)
    rfs = max(15, min(30, rowh * 0.42))
    rows = "".join(f'<div class="r{" hot" if (len(r) > 2 and r[2]) else ""}" style="height:{rowh:.0f}px; font-size:{rfs:.0f}px"><span><i></i>{X.rich(r[0])}</span><b>{X.rich(r[1] if len(r) > 1 else "")}</b></div>' for r in shown)
    if more: rows += f'<div class="r more" style="height:{rowh:.0f}px; font-size:{rfs * 0.85:.0f}px"><span>{X.rich(f"…… 还有 {more} 项")}</span></div>'
    sk = next((k for k, r in enumerate(shown) if len(r) > 2 and r[2]), 0)
    srch = '<svg viewBox="0 0 30 30"><circle cx="13" cy="13" r="9" fill="none" stroke="#8a93a3" stroke-width="3"/><path d="M20 20l7 7" stroke="#8a93a3" stroke-width="3" stroke-linecap="round"/></svg>'
    inner = (f'<div class="sc sc-pal"><div class="bgfx"></div><div class="cam">'
             + (f'<div class="ab tha" style="left:{L[0]}px; top:{L[1]}px; width:{L[2]}px">{ah}</div>' if anl else "")
             + f'<div class="ab thb" style="left:{L[0]}px; top:{by:.0f}px; width:{L[2]}px">{bh}</div>'
             + win(X, "pl", "⌘K", f'<div class="in" style="font-size:{qpx}px">{srch}<span class="qq">{chars(X, q)}<i class="caret"></i></span></div>'
                   f'<i class="sel" style="height:{rowh:.0f}px"></i><div class="rs">{rows}</div><div class="kb">↑↓ 选择 · ↵ 打开</div>', sty=box(L[0], wy, L[2], wb))
             + f'</div>{furn(X, b)}</div>')
    X.used_text.update("⌘K↑↓选择↵打开")
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    tb, ts = T(X, b, "at_b", t, t + d * 0.4), T(X, b, "at_sel", t, t + d * 0.6)
    rise(X, f"{s} .win", t)
    if anl: X.tw(f'tl.from("{s} .tha", {{opacity:0, y:20, duration:0.5, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .thb", {{opacity:0, y:30, filter:"blur(10px)", duration:0.6, ease:"expo.out"}}, {tb - 0.25:.3f});')
    each = min(0.07, 1.2 / max(len(q), 1))
    typing(X, f"{s} .qq", t + 0.35, len(q), each)
    X.tw(f'tl.from("{s} .r", {{opacity:0, x:-20, duration:0.35, ease:"expo.out", stagger:{min(0.08, 0.7 / max(len(shown), 1)):.3f}}}, {t + 0.45 + len(q) * each:.3f});')
    X.tw(f'tl.from("{s} .sel", {{opacity:0, duration:0.2}}, {t + 0.5 + len(q) * each:.3f});')
    X.tw(f'tl.to("{s} .sel", {{y:{rowh * sk:.1f}, duration:0.45, ease:"power3.inOut"}}, {ts - 0.2:.3f});')
    X.sfx(ts, "click")
    if any(len(r) > 2 and r[2] for r in shown): X.tw(f'tl.fromTo("{s} .r.hot", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.15}}, {{scale:1, duration:0.3}}], transformOrigin:"0 50%", immediateRender:false}}, {ts + 0.25:.3f});')
    shots(X, f"{s} .cam", t, d, [(t, 1.06, 0.4 if not P else 0.5, 0.5 if not P else 0.45), (tb - 0.4, 1.0, 0.5, 0.5)])


def outro(b, X, t, d, cid):
    P = X.portrait
    X.css("sc-out", """
.sc-out .ic { position:absolute; border-radius:24%; background:linear-gradient(160deg, #d8ff7a, #9fd23a);
  box-shadow:0 30px 80px rgba(198,244,90,.25), inset 0 2px 0 rgba(255,255,255,.5); display:grid; place-items:center; font-family:var(--f-num); font-weight:800; color:#0a0c10; }
.sc-out .ttl { font-family:var(--f-display); font-weight:800; color:var(--fg); letter-spacing:-.01em; }
.sc-out .sub { color:var(--muted); }
.sc-out .cta { position:absolute; font-weight:700; color:#0a0c10; background:var(--lime); padding:12px 30px; border-radius:999px; white-space:nowrap; }
""")
    title = str(b.get("title", "第九顶帽子"))
    if P:
        ic = (56, 420, 150); tx, ty, tw_ = 56, 610, 968
    else:
        ic = (160, 320, 180); tx, ty, tw_ = 380, 330, 1380
    tpx = fit_px(title, tw_, 110, 40)
    sub, spx, snl = fit(X, b.get("sub", ""), tw_, 90, 34, 18, 2, 1.3)
    cta = str(b.get("cta", ""))
    cy = (ty + tpx * 1.2 + snl * spx * 1.3 + 40) if P else max(ic[1] + ic[2] + 70, ty + tpx * 1.2 + snl * spx * 1.3 + 40)
    inner = (f'<div class="sc sc-out"><div class="bgfx"></div><div class="cam"><div class="ic" style="{box(ic[0], ic[1], ic[2], ic[2])}; font-size:{ic[2] * 0.6:.0f}px">{X.rich(b.get("icon", "9"))}</div>'
             f'<div class="ab ttl" style="left:{tx}px; top:{ty}px; font-size:{tpx}px; white-space:nowrap">{X.rich(title, split="chars")}</div>'
             f'<div class="ab sub" style="left:{tx + 4}px; top:{ty + tpx * 1.25:.0f}px; width:{tw_}px">{sub}</div>'
             + (f'<div class="cta" style="left:{ic[0]}px; top:{cy:.0f}px; font-size:{fit_px(cta, 700, 30, 16)}px">{X.rich(cta)}</div>' if cta else "")
             + f'</div>{furn(X, b)}</div>')
    X.clip(cid, t, d, inner, "scene", 2)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .ic", {{scale:0.4, rotation:-20, opacity:0, duration:0.7, ease:"back.out(1.8)"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .ttl .c", {{y:40, opacity:0, duration:0.55, ease:"expo.out", stagger:{min(0.05, 0.5 / max(len(title), 1)):.3f}}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .sub", {{opacity:0, y:16, duration:0.5}}, {t + 0.5:.3f});')
    if cta: X.tw(f'tl.from("{s} .cta", {{scale:0.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.75:.3f});')
    X.tw(f'tl.fromTo("{s} .cam", {{scale:1}}, {{scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.sfx(t + 0.1, "hit")


SCENES = {"dash": dash, "api": api, "pricing": pricing, "forecast": forecast, "shots": shots_wall, "palette": palette, "outro": outro}
