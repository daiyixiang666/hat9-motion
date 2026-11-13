"""thread · 一线长卷 —— 整条片子是一张比画面大得多的暖色纸，卡片成组摆在纸上，一根细细的橙色线从第一张卡走到最后一张；
镜头从不切，只是沿着这根线滑到下一组。论证就是观众走过的一条路。

材料：纸 #efe9dc，四角压暗到 #e4dccb，纸纹约 6%；墨 #1d1b18；浅卡 #f7f3ea（1 px #d8cfbd 边、圆角 14、软投影），
深卡 #24211d（字 #f1ece0）。橙 #e8602c 是唯一的饱和色，只用于：线本身、每页一个高亮的数或词、勾和叉。
浅底上的高亮是橙色小标签配墨色字（橙字配浅纸只有 3:1），深卡上直接用橙字（4.7:1）。
字：思源黑体 400 / 700；数字和拉丁字母 Space Grotesk 700；代码样的小签 JetBrains Mono。

画布（WORLD，整片一个连续场景）：竖屏是一条宽 2400 px 的长纸，每组之间纵向 1250 px，组的中心左右交替（x 900 / 1500，邻组总有一角留在画面里），
每组排满一个 940 × 950 的框，停留时镜头按组的外框缩放，让它占满画面 x 70–1010、y 330–1280；横屏每组排满 1150 × 670，占画面 60% × 62%。
线 5 px（支线 3–10 px 按数值），在组之间走 S 形三次贝塞尔（控制臂约为间距的一半），从卡片边上的插口（16 px 橙环）进、从另一个插口出；
线只画到故事走到的地方，最新的 600 px 带一层 14 px、18% 的柔光，眼睛总能找到线头；镜头移动时线头比镜头早到一步。
横屏把画布重排成一条横向长卷（每组 1400 px，上下交替），镜头从左往右走。
镜头：两组之间 1.05 s，缓动 (0.65, 0, 0.35, 1)，中途拉远到 0.82 再推回，最快的三分之一里画布沿运动方向模糊（0 → 10 px → 0），
页眉、字幕和出处在画布外，不跟着模糊；停在一组上时镜头还在漂 16 px。开场先在 0.35 倍看见前三组的空卡轮廓 0.8 s，再推进第一组。
结尾：拉远看整条路并停 1.2 s——这时字隐去、每张卡变成实心色块、线按屏幕 6 px 画粗，整条 S 形路像一幅画；
然后镜头顺着线走到路的尽头，总结卡作为线的终点插上，插口收成一个实心圆点。不活动的组 3 px 模糊 + 55% 不透明（景深）。

固定家具（不在画布上）：左上页眉（x 96，y 220–300：26 px 页码签 + 46 px 标题，换页时遮罩上滚）；
字幕在 y 1380–1460，墨字 44 px 压在 92% 纸色小底板上；出处 24 px 在 y 1476–1506。y 1520 以下只是画布继续，没有要读的字。

卡片组就是图表（beat 的 scene）：
  figure  一张大浅卡 + 上方深色小签 + 逐位插上的大数字（Space Grotesk 220 px）+ 说明行 + 一条按真实比例的对比细条
  split   线分成 2–4 支，每支末端一张卡，卡宽按真实比例（最小 140 px），支线粗细 2–10 px 也按比例
  steps   3–5 张小卡排在线上，线按顺序穿过，线头经过时卡从轮廓变实心
  compare 两张并排的卡，高度按真实比例，一深一浅，两卡顶端之间一道橙色大括号，尖端指着 96 px 的倍数
  gate    线经过一道关：主线穿过画橙勾的卡继续走；画叉的卡伸出一条支线，落进它右下方的纸篓（算 / 不算）
  stack   一张账本卡：行从线这一侧逐行滑入，合计行是深色
  sum     结尾：整条路的远景（实心色块 + 粗线）→ 路尽头的深色总结卡（三个数，≥ 96 px），线的终点
其它 scene（例如 "fx"）照常按效果页渲染在画布之上，FX_FRAME 给它们这张纸、页眉、字幕和一段穿过画面的线。
动作：插上（线头到插口，插口环 1.0 → 1.6 → 1.0，8 帧）→ 填充（卡从插口那一侧擦成实心 6 帧，内容按阅读顺序 2–3 帧错开上升 40 px）
→ 停留漂移 → 沿线移动。没有原地淡入，回弹不超过 4%。不出主持人。
"""
import json, math
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
F = 1 / 30

PAPER, PAPER2, INK = "#efe9dc", "#e4dccb", "#1d1b18"
CARD, EDGE, DARK, DARKTX = "#f7f3ea", "#d8cfbd", "#24211d", "#f1ece0"
OR = "#e8602c"
MUTED = "#675f53"          # labels on paper / light cards (≥ 4.5:1 on both)
SRCC = "#6d6558"           # source line
DMUTED = "#b9b09e"         # labels on dark cards

CX0, CX1 = 900, 1500        # 9:16: group centres alternate left / right of the strip's middle (neighbours stay partly in frame)
HPITCH = 1400             # 16:9: canvas px between two groups along the wide strip
PITCH = 1250              # 9:16: canvas px between two groups (neighbours peek in above and below)
GLOW = 600                 # the newest 600 px of the thread carry a soft glow, so the eye finds the tip
FORMS = ("figure", "split", "steps", "compare", "gate", "stack", "sum")

STYLE = {
    "name": "一线长卷", "en": "Thread", "benchmarks": ["连续画布上的镜头游走（一镜到底的信息图）", "Kurzgesagt / Vox 的镜头穿行", "纸面便签墙 + 一根红线"],
    "tokens": {
        "bg": PAPER, "fg": INK, "muted": MUTED, "accent": "#e05a26", "accent2": INK, "alert": OR,
        "line": EDGE, "paper": PAPER, "ink": INK, "card": CARD, "card-fg": INK,
        "cap-bg": "rgba(239,233,220,.92)", "cap-fg": INK, "cap-size": "44px", "cap-weight": "700", "cap-pad": "10px 22px",
        "cap-radius": "10px", "cap-shadow": "none", "cap-em": INK, "cap-bottom": "460px",
        "punch-top": "70%", "punch-size": "72px",
    },
    "fonts": {"display": ["noto-sans-sc"], "body": ["noto-sans-sc"], "zh": ["noto-sans-sc"], "cap": ["noto-sans-sc"],
              "num": ["space-grotesk", "noto-sans-sc"], "latin": "space-grotesk", "mono": ["jetbrains-mono", "noto-sans-sc"]},
    "motion": {"ease": "power3.out", "dur": 0.4, "stagger": 2 * F, "cut": "hard", "transition": "hard", "em": "static", "camera": "none"},
    "layers": [],
    "mascot": {"mode": "none"},
    "caption_plate": False,
    # groups that are not the active one are blurred by depth (3 px, 55 % opacity): picture, not something to read
    "safe_exempt": ['.th-g[data-far="1"]', '.th-g[data-wide="1"]', ".thx .wire"],
    "sfx": {"enter": None, "hit": None, "pop": None, "slam": None, "count": None, "click": None, "mascot": None, "transition": None,
            "cut": None, "line": None, "tick": None, "draw": None, "paper": None, "whoosh": None, "title": None, "fly": None, "pin": None},
}

GRAIN = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='320' height='320'>"
         "<filter id='g'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' seed='11' stitchTiles='stitch'/>"
         "<feColorMatrix values='0 0 0 0 .32  0 0 0 0 .26  0 0 0 0 .16  0 0 0 .9 -.4'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23g)'/></svg>")

CSS = r"""
.th-cam { position:absolute; inset:0; overflow:hidden; background-color:#efe9dc;
  background-image:url("__GRAIN__"), radial-gradient(ellipse 72% 62% at 50% 46%, rgba(228,220,203,0) 58%, rgba(228,220,203,.55) 84%, rgba(222,212,192,.85) 100%);
  background-size:320px, 100% 100%; }
.th-zoom { position:absolute; inset:0; }
.th-world { position:absolute; left:0; top:0; }
.th-world svg { position:absolute; overflow:visible; }
.th-world .main { fill:none; stroke:#e8602c; stroke-width:calc(5px * var(--k, 1)); stroke-linecap:round; stroke-linejoin:round; }
.th-world .glow { fill:none; stroke:#e8602c; stroke-opacity:.18; stroke-width:calc(14px * var(--k, 1)); stroke-linecap:round; filter:blur(2px); }
.th-g { position:absolute; left:0; top:0; width:0; height:0; filter:blur(3px); opacity:.55; }
.th-g .br { fill:none; stroke:#e8602c; stroke-linecap:round; }
.th-g .ink { fill:none; stroke:#1d1b18; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; }
.th-g .acc { fill:none; stroke:#e8602c; stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
.th-sk { fill:#efe9dc; stroke:#e8602c; stroke-width:3; }
.th-cd { position:absolute; }
.th-cd > .ol { position:absolute; inset:0; border:2px dashed rgba(29,27,24,.55); border-radius:14px; background:rgba(247,243,234,.7); }
.th-cd > .bg { position:absolute; inset:0; background:#f7f3ea; border:1px solid #d8cfbd; border-radius:14px; box-shadow:0 10px 30px rgba(60,45,20,.10);
  clip-path:inset(0% 100% 0% 0%); }
.th-cd.dk > .bg { background:#24211d; border-color:#24211d; box-shadow:0 10px 30px rgba(30,20,10,.18); }
.th-cd > .ct { position:absolute; inset:0; color:#1d1b18; font-family:var(--f-zh); }
.th-cd.dk > .ct { color:#f1ece0; }
.th-cd .rv { position:absolute; opacity:0; white-space:nowrap; line-height:1.2; }
.th-cd.chip { width:auto; white-space:nowrap; padding:0 18px; }
.th-cd.chip > .ct { position:relative; inset:auto; }
.th-cd.chip .rv { position:relative; display:inline-block; color:#f1ece0; line-height:inherit; vertical-align:top; }
.th-cd .lb { font-size:30px; font-weight:400; color:#675f53; letter-spacing:.02em; }
.th-cd.dk .lb { color:#b9b09e; }
.th-cd .vl { font-family:var(--f-num); font-weight:700; color:inherit; letter-spacing:-.01em; }
.th-cd .vl .u { font-family:var(--f-zh); font-weight:700; letter-spacing:0; }
.th-cd .tx { font-size:34px; font-weight:400; }
.th-cd .tx b { font-weight:700; }
.th .em { font-style:normal; }
.th .em .emt { background:#e8602c; color:#1d1b18; padding:0 .16em; border-radius:6px; box-decoration-break:clone; -webkit-box-decoration-break:clone; }
.th .em .emb { display:none; }
.th-g[data-far="1"] .em .emt { background:none; color:inherit; }   /* a group out of focus keeps no highlight */
.th .dk .em .emt { background:none; color:#e8602c; padding:0; }
.th-cd .hero { font-family:var(--f-num); font-weight:700; line-height:1; letter-spacing:-.015em; white-space:nowrap; }
.th-cd .hero .dg { display:inline-block; overflow:hidden; vertical-align:bottom; padding-top:.06em; margin-top:-.06em; }
.th-cd .hero .dg > b { display:inline-block; font-weight:700; }
.th-cd .hero .u { font-family:var(--f-zh); font-size:64px; font-weight:700; letter-spacing:0; margin-left:16px; display:inline-block; opacity:0; }
.th-hd { position:absolute; left:96px; top:220px; width:860px; height:84px; font-family:var(--f-zh); color:#1d1b18; }
.th-hd .k, .th-hd .t { position:absolute; left:0; overflow:hidden; width:860px; }
.th-hd .k { top:0; height:32px; }
.th-hd .t { top:28px; height:64px; }
.th-hd .k span, .th-hd .t span { position:absolute; left:0; top:0; white-space:nowrap; background:rgba(239,233,220,.92); padding:0 12px; margin-left:-12px; border-radius:8px; }
.th-hd .k span { font-family:var(--f-mono); font-size:26px; line-height:32px; font-weight:500; color:#675f53; letter-spacing:.04em; }
.th-hd .t span { font-size:46px; line-height:62px; font-weight:700; }
.th-src { position:absolute; left:120px; top:1474px; height:34px; width:840px; overflow:hidden; }
.th-src span { position:absolute; left:0; top:0; white-space:nowrap; font-family:var(--f-zh); font-size:24px; line-height:34px; color:#6d6558;
  background:rgba(239,233,220,.92); padding:0 10px; margin-left:-10px; border-radius:6px; }
#root.h .th-hd { top:58px; }
#root.h .th-src { left:96px; top:auto; bottom:44px; width:1300px; }
.st-thread .mascot { display:none !important; }
#root.h.st-thread { --cap-bottom:112px; }
"""


# ================================================================ geometry
def add(a, b): return (a[0] + b[0], a[1] + b[1])
def sub(a, b): return (a[0] - b[0], a[1] - b[1])
def mul(a, k): return (a[0] * k, a[1] * k)
def dist(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])


def bez(p0, p1, p2, p3, u):
    v = 1 - u
    return (v * v * v * p0[0] + 3 * v * v * u * p1[0] + 3 * v * u * u * p2[0] + u * u * u * p3[0],
            v * v * v * p0[1] + 3 * v * v * u * p1[1] + 3 * v * u * u * p2[1] + u * u * u * p3[1])


def seg_len(s, n=64):
    L, prev = 0.0, s[0]
    for k in range(1, n + 1):
        q = bez(*s, k / n)
        L += dist(prev, q)
        prev = q
    return L


def curve(a, da, b, db, arm=None, lo=60, hi=700):
    """cubic from a (leaving along da) to b (arriving along db)."""
    if arm is None: arm = max(lo, min(hi, 0.5 * dist(a, b)))
    return (a, add(a, mul(da, arm)), sub(b, mul(db, arm)), b)


def line(a, b):
    return (a, add(a, mul(sub(b, a), 1 / 3)), add(a, mul(sub(b, a), 2 / 3)), b)


def d_of(segs):
    if not segs: return ""
    out = [f"M{segs[0][0][0]:.1f} {segs[0][0][1]:.1f}"]
    for s in segs:
        out.append(f"C{s[1][0]:.1f} {s[1][1]:.1f} {s[2][0]:.1f} {s[2][1]:.1f} {s[3][0]:.1f} {s[3][1]:.1f}")
    return "".join(out)


def through(pts, d0, d1):
    """Catmull-Rom through pts as cubic segments, with the end directions given."""
    segs = []
    n = len(pts)
    tans = []
    for i in range(n):
        if i == 0: tans.append(mul(d0, dist(pts[0], pts[1])))
        elif i == n - 1: tans.append(mul(d1, dist(pts[-1], pts[-2])))
        else: tans.append(mul(sub(pts[i + 1], pts[i - 1]), 0.5))
    for i in range(n - 1):
        segs.append((pts[i], add(pts[i], mul(tans[i], 1 / 3)), sub(pts[i + 1], mul(tans[i + 1], 1 / 3)), pts[i + 1]))
    return segs


# ================================================================ text
def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def plain(s):
    return str(s).replace("*", "").replace("|", "")


SG = {"0": .648, "1": .452, "2": .594, "3": .608, "4": .636, "5": .6, "6": .618, "7": .554, "8": .6, "9": .618, ",": .294, ".": .298,
      "%": .758, "×": .62, "+": .62, "−": .62, "-": .432, " ": .254}


def num_w(s, px):
    """width of a Space Grotesk 700 run (CJK glyphs count 1 em at the same size)."""
    w = 0.0
    for ch in plain(s):
        w += SG.get(ch, 1.0 if ord(ch) > 0x2E80 else 0.6)
    return w * px


def zh_w(s, px):
    w = 0.0
    for ch in plain(s):
        w += 1.0 if ord(ch) > 0x2E80 else (SG.get(ch, 0.56))
    return w * px


# ================================================================ the film
class Thread:
    def __init__(self, beats, times, X, D):
        self.X, self.D, self.beats, self.times = X, D, beats, times
        self.V = X.portrait
        self.meta = X.v.get("meta", {})
        # each group is laid out in a BW × BH box and held so that its bounding box fills the target area TW × TH,
        # centred on the focus point (9:16: x 70–1010, y 330–1280; 16:9: 60 % × 62 % of the frame)
        self.BW, self.BH = (940, 950) if self.V else (1150, 670)
        self.TW, self.TH = (940, 950) if self.V else (1152, 670)
        self.fx, self.fy = (540, 805) if self.V else (960, 525)
        self.uid = 0

    def tw(self, s): self.X.tw(s)

    def nid(self, p):
        self.uid += 1
        return f"th{p}{self.uid}"

    # ---------------------------------------------------- layout of the strip
    def place(self, k):
        if self.V:
            return (CX0 if k % 2 == 0 else CX1, 1000 + k * PITCH)
        return (1000 + k * HPITCH, 800 if k % 2 == 0 else 1300)

    def run(self):
        X = self.X
        tb = [(i, b, t, d) for i, (b, (t, d)) in enumerate(zip(self.beats, self.times)) if b.get("scene") in FORMS]
        other = [(i, b, t, d) for i, (b, (t, d)) in enumerate(zip(self.beats, self.times)) if b.get("scene") not in FORMS]
        for i, b, t, d in other:
            self.foreign(i, b, t, d)
        if not tb: return
        X.css("thread", CSS.replace('url("__GRAIN__")', f'url("{GRAIN}")'))
        self.tb = tb
        self.build_world()
        self.build_furniture()

    def foreign(self, i, b, t, d):
        """a beat that is not a card group (e.g. an effect): rendered as its own page over the canvas."""
        from h9 import aefx
        import importlib.util
        X = self.X
        cid = b.get("id") or X.uid("s")
        X.beat = {"t": t, "d": d, "i": i, "n": len(self.beats)}
        X.beat_marks = ""
        if b.get("scene") == "fx":
            fn = aefx.FX.get(b["fx"])
            if not fn: raise SystemExit(f"unknown fx {b['fx']!r}")
            fn(X, cid, t, d, b)
            return
        p = SKILL / "scenes" / f"{b['scene']}.py"
        if not p.exists(): raise SystemExit(f"thread: no scene {b['scene']!r}")
        spec = importlib.util.spec_from_file_location(f"scene_{b['scene']}", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.build(b, X, t, d, cid)

    # ---------------------------------------------------- the world: groups, thread, camera
    def build_world(self):
        X, V = self.X, self.V
        n = len(self.tb)
        self.G = []
        for k, (i, b, t, d) in enumerate(self.tb):
            gx, gy = self.place(k)
            prev = self.place(k - 1) if k else (gx - (CX1 - CX0 if V else HPITCH), gy - (PITCH if V else 0) - (0 if V else 420))
            nxt = self.place(k + 1) if k + 1 < n else None
            ctx = {"k": k, "i": i, "b": b, "t": t, "d": d, "c": (gx, gy), "prev": prev, "next": nxt}
            form = b["scene"]
            g = getattr(self, "g_" + form)(ctx)
            g.update(ctx)
            self.G.append(g)
        # the strip's extent
        xs = [g["c"][0] for g in self.G]; ys = [g["c"][1] for g in self.G]
        self.CW = int(max(xs) + (900 if V else 1300)); self.CH = int(max(ys) + (1100 if V else 800))
        if V: self.CW = max(self.CW, 2400)
        # main thread: lead-in → (inner → link)* → end knot
        g0 = self.G[0]
        S0 = add(g0["E"], (-560, -760)) if V else add(g0["E"], (-900, -260))
        segs = [curve(S0, (0.35, 0.94) if V else (0.94, 0.35), g0["E"], g0["dE"], 520)]
        marks = {}
        for k, g in enumerate(self.G):
            marks[("E", k)] = len(segs)
            for s in g.get("inner", []): segs.append(s)
            marks[("O", k)] = len(segs)
            if k + 1 < n:
                h = self.G[k + 1]
                arm = max(200.0, min(700.0, 0.5 * dist(g["O"], h["E"])))      # arms ~half the gap: an S, never a loop
                a1 = g.get("arm_out", arm)
                segs.append((g["O"], add(g["O"], mul(g["dO"], a1)), sub(h["E"], mul(h["dE"], arm)), h["E"]))
        lens = [seg_len(s) for s in segs]
        cum = [0.0]
        for L in lens: cum.append(cum[-1] + L)
        self.Ltot = cum[-1]
        self.L = {key: cum[ix] for key, ix in marks.items()}
        for g in self.G:          # cumulative length of named points inside a group (steps cards, compare bars)
            base = self.L[("E", g["k"])]
            acc = [base]
            for s in g.get("inner", []): acc.append(acc[-1] + seg_len(s))
            g["Lin"] = acc
        world = [f'<svg class="mainsvg" style="left:0;top:0" width="{self.CW}" height="{self.CH}" viewBox="0 0 {self.CW} {self.CH}">'
                 f'<path id="thglow" class="glow" d="{d_of(segs)}" style="stroke-dasharray:{GLOW} {self.Ltot + 2 * GLOW:.1f};stroke-dashoffset:{GLOW}"/>'
                 f'<path id="thp" class="main" d="{d_of(segs)}" style="stroke-dasharray:{self.Ltot:.1f};stroke-dashoffset:{self.Ltot:.1f}"/></svg>']
        for g in self.G:
            world.append(self.group_html(g))
        mb = ('<svg width="0" height="0" style="position:absolute"><filter id="thmb" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB">'
              '<feGaussianBlur id="thmbg" stdDeviation="0 0"/></filter></svg>')
        inner = (f'{mb}<div class="th-cam" id="thcam"><div class="th-zoom" id="thzoom" style="transform-origin:{self.fx}px {self.fy}px">'
                 f'<div class="th-world th" id="thworld" style="width:{self.CW}px;height:{self.CH}px">{"".join(world)}</div></div></div>')
        X.clip("thw", 0, self.D, inner, "th-root", 2, track=2)
        self.camera()
        for g in self.G:
            getattr(self, "a_" + g["b"]["scene"])(g)
            self.depth(g)
            self.show_sock(f'#{g["ids"]["E"]}', g["plug"] - 0.15)      # a socket appears only as the thread reaches it
        self.links()

    def links(self):
        """the thread between groups: once a group is complete a short stub already leaves it toward the next one
        (hanging out of frame), then the rest runs ahead of the camera and reaches the next socket before it settles."""
        t0, dur = self.G[0]["lead"]
        self.tip(0, self.L[("E", 0)], t0, dur, "power1.inOut")
        for k in range(1, len(self.G)):
            g, h = self.G[k - 1], self.G[k]
            t0, dur = h["link"]
            LO, LE = self.L[("O", k - 1)], self.L[("E", k)]
            r0 = g.get("out_ready", t0)
            if t0 - r0 > 0.6:
                stub = LO + min(260.0, 0.3 * (LE - LO))
                self.tip(LO, stub, r0, 0.5, "power2.out")
                LO = stub
            self.tip(LO, LE, t0, dur, "power1.inOut")

    def group_html(self, g):
        k = g["k"]
        x0, y0, w, h = g.get("box", (g["c"][0] - 700, g["c"][1] - 760, 1400, 1520))
        vb = f'viewBox="{x0} {y0} {w} {h}" width="{w}" height="{h}" style="left:{x0}px;top:{y0}px"'
        under = f'<svg {vb}>{"".join(g.get("under", []))}</svg>'
        over = f'<svg {vb}>{"".join(g.get("over", []))}</svg>'
        return f'<div class="th-g" id="thg{k}" data-far="1" data-layout-allow-overlap>{under}{"".join(g.get("html", []))}{over}</div>'

    # ---------------------------------------------------- cards and sockets
    def card(self, x, y, w, h, inner, dark=False, cid=None):
        cid = cid or self.nid("c")
        return cid, (f'<div class="th-cd{" dk" if dark else ""}" id="{cid}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
                     f'<i class="ol"></i><i class="bg"></i><div class="ct">{inner}</div></div>')

    def chip(self, x, y, h, html, cid=None):
        """a dark chip whose width follows its text (18 px padding each side)."""
        cid = cid or self.nid("c")
        return cid, (f'<div class="th-cd dk chip" id="{cid}" style="left:{x:.0f}px;top:{y:.0f}px;height:{h:.0f}px;line-height:{h:.0f}px">'
                     f'<i class="ol"></i><i class="bg"></i><div class="ct"><span class="rv lb">{html}</span></div></div>')

    def rv(self, x, y, html, cls="", extra=""):
        return f'<div class="rv {cls}" style="left:{x:.0f}px;top:{y:.0f}px;{extra}">{html}</div>'

    def sock(self, p, sid=None):
        sid = sid or self.nid("k")
        return sid, f'<circle class="th-sk" id="{sid}" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="6.5" style="transform-box:fill-box;transform-origin:50% 50%"/>'

    @staticmethod
    def edge(rect, side, at=0.5):
        x, y, w, h = rect
        if side == "t": return (x + w * at, y), (0, 1)
        if side == "b": return (x + w * at, y + h), (0, 1)
        if side == "l": return (x, y + h * at), (1, 0)
        return (x + w, y + h * at), (1, 0)

    def v_exit(self, g, rect):
        """9:16 exit: a socket near the bottom corner facing the next group, the thread leaving sideways, so in a hold
        the stub runs out of frame above the caption plate and source line instead of down through them."""
        nx = g["next"][0] if g["next"] else g["c"][0] + 1
        side = 1 if nx > g["c"][0] else -1
        O, _ = self.edge(rect, "b", 0.92 if side > 0 else 0.08)
        return O, (side, 0)

    def h_at(self, g, which):
        """16:9: where along a side edge the thread enters / leaves, given whether the neighbour sits higher or lower."""
        cy = g["c"][1]
        if which == "in":
            return 0.8 if g["prev"][1] > cy else 0.2
        ny = g["next"][1] if g["next"] else cy
        return 0.15 if ny < cy else 0.85

    def ends(self, g, rect_in, rect_out, at_in=None, at_out=None):
        """entry / exit sockets on the edges facing the previous / next group."""
        cx, cy = g["c"]
        px, py = g["prev"]
        if self.V:
            ai = at_in if at_in is not None else (0.22 if px < cx else 0.78)
            E, dE = self.edge(rect_in, "t", ai)
            nx = g["next"][0] if g["next"] else cx
            ao = at_out if at_out is not None else (0.25 if nx < cx else 0.75)
            O, dO = self.edge(rect_out, "b", ao)
        else:
            E, dE = self.edge(rect_in, "l", at_in if at_in is not None else 0.5)
            O, dO = self.edge(rect_out, "r", at_out if at_out is not None else 0.5)
        return E, dE, O, dO

    # ---------------------------------------------------- motion verbs
    def plug(self, sel, t):
        """the socket ring pulses 1.0 → 1.6 → 1.0 (its radius, so the ring never leaves its spot)."""
        self.tw(f'tl.fromTo("{sel}", {{attr:{{r:6.5}}}}, {{attr:{{r:10.4}}, duration:{4 * F:.4f}, ease:"power2.out", immediateRender:false}}, {t:.3f});')
        self.tw(f'tl.fromTo("{sel}", {{attr:{{r:10.4}}}}, {{attr:{{r:6.5}}, duration:{4 * F:.4f}, ease:"power2.in", immediateRender:false}}, {t + 4 * F:.3f});')

    def show_sock(self, sel, t):
        self.tw(f'tl.fromTo("{sel}", {{opacity:0, attr:{{r:1.5}}}}, {{opacity:1, attr:{{r:6.5}}, duration:{5 * F:.4f}, ease:"power3.out", immediateRender:false}}, {t:.3f});')
        self.tw(f'tl.set("{sel}", {{opacity:0}}, 0);')

    def fill(self, cid, t, side="l"):
        frm = {"l": "inset(0% 100% 0% 0%)", "r": "inset(0% 0% 0% 100%)", "t": "inset(0% 0% 100% 0%)", "b": "inset(100% 0% 0% 0%)"}[side]
        self.tw(f'tl.fromTo("#{cid} > .bg", {{clipPath:"{frm}"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{6 * F:.4f}, ease:"power2.out", immediateRender:false}}, {t:.3f});')
        self.tw(f'tl.fromTo("#{cid} > .ol", {{opacity:1}}, {{opacity:0, duration:{6 * F:.4f}, ease:"none", immediateRender:false}}, {t + 3 * F:.3f});')

    def rise(self, sel, t, stagger=2 * F, dx=0, dy=40):
        self.tw(f'tl.fromTo("{sel}", {{opacity:0, x:{dx}, y:{dy}}}, {{opacity:1, x:0, y:0, duration:0.42, ease:"power3.out", stagger:{stagger:.4f}, immediateRender:false}}, {t:.3f});')

    def draw_path(self, sel, L, t, dur, ease="power1.inOut"):
        self.tw(f'tl.fromTo("{sel}", {{strokeDashoffset:{L:.1f}}}, {{strokeDashoffset:0, duration:{dur:.3f}, ease:"{ease}", immediateRender:false}}, {t:.3f});')

    def path(self, segs, cls, w=None, pid=None):
        pid = pid or self.nid("p")
        L = sum(seg_len(s) for s in segs)
        sw = f"stroke-width:calc({w:.1f}px * var(--k, 1));" if w else ""
        return pid, L, f'<path id="{pid}" class="{cls}" d="{d_of(segs)}" style="{sw}stroke-dasharray:{L:.1f};stroke-dashoffset:{L:.1f}"/>'

    def tip(self, a, b, t, dur, ease="power1.inOut"):
        """the main thread grows from length a to b."""
        self.tw(f'tl.fromTo("#thp", {{strokeDashoffset:{self.Ltot - a:.1f}}}, {{strokeDashoffset:{self.Ltot - b:.1f}, duration:{dur:.3f}, ease:"{ease}", immediateRender:false}}, {t:.3f});')
        self.tw(f'tl.fromTo("#thglow", {{strokeDashoffset:{GLOW - a:.1f}}}, {{strokeDashoffset:{GLOW - b:.1f}, duration:{dur:.3f}, ease:"{ease}", immediateRender:false}}, {t:.3f});')

    def hero_html(self, value, unit, px):
        out = []
        for ch in str(value):
            out.append(f'<i class="dg"><b>{esc(ch)}</b></i>')
        u = f'<span class="u">{esc(unit)}</span>' if unit else ""
        return f'<div class="hero" style="font-size:{px}px">{"".join(out)}{u}</div>'

    # ================================================================ forms: layout (g_*) and motion (a_*)
    # every group is laid out to fill a box of BW × BH canvas px around its centre c (9:16: 940 × 950, 16:9: 1150 × 670);
    # the camera then holds on the group's real bounding box ("rect") at the scale that fits the target area of the frame.
    def box(self, g):
        cx, cy = g["c"]
        return cx - self.BW / 2, cy - self.BH / 2, self.BW, self.BH

    def bars_html(self, rows, x, y, wmax, labw, gap=110, h=60):
        """a thin comparison strip: one bar per row, lengths in true ratio, label left, value right of the bar."""
        X = self.X
        vmax = max(float(r["v"]) for r in rows)
        out = []
        for j, r in enumerate(rows):
            w = max(8.0, wmax * float(r["v"]) / vmax)
            yy = y + j * gap
            dark = j == len(rows) - 1
            out.append(self.rv(x, yy + h / 2 - 20, X.rich(r.get("k", "")), "lb bl"))
            out.append(f'<div class="rv bar" style="left:{x + labw:.0f}px;top:{yy:.0f}px;width:{w:.0f}px;height:{h}px;opacity:1;'
                       f'background:{DARK if dark else EDGE};border-radius:6px;clip-path:inset(0% 100% 0% 0%)"></div>')
            out.append(self.rv(x + labw + w + 18, yy + h / 2 - 24, X.rich(r.get("show", "")), "vl bv", "font-size:40px;line-height:48px"))
        return "".join(out)

    def g_figure(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        px = 220
        val, unit = str(b.get("value", "")), b.get("unit", "")
        chip = b.get("chip", "")
        ch = 64
        x, y, w, h = bx, by + ch + 20, bw, bh - ch - 20
        hero = f'<div class="rv hz" style="left:52px;top:44px;opacity:1">{self.hero_html(val, unit, px)}</div>'
        lines = b.get("lines", [])
        ly, lh = (300, 52) if V else (276, 46)
        ls = "".join(self.rv(56, ly + j * lh, f'<span class="tx">{X.rich(l)}</span>', "ln") for j, l in enumerate(lines))
        rows = b.get("bars", [])
        strip = ""
        if rows:
            sy = ly + len(lines) * lh + (60 if V else 14)
            if V:
                strip = self.rv(56, sy, X.rich(b.get("bars_title", "")), "lb st") + self.bars_html(rows, 56, sy + 64, 470, 190, 104, 64)
            else:
                strip = self.rv(56, sy, X.rich(b.get("bars_title", "")), "lb st") + self.bars_html(rows, 56, sy + 44, 640, 190, 68, 50)
        cid, html = self.card(x, y, w, h, hero + ls + strip)
        chid, chtml = self.chip(x, by, ch, X.rich(chip))
        if V:
            if g["prev"][0] < g["c"][0]:
                E, dE = (x + 70, by), (0, 1)
            else:
                E, dE = self.edge((x, y, w, h), "t", 0.8)
            O, dO = self.v_exit(g, (x, y, w, h))
        else:
            E, dE = self.edge((x, y, w, h), "l", self.h_at(g, "in"))
            O, dO = self.edge((x, y, w, h), "r", self.h_at(g, "out"))
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        return {"html": [chtml, html], "over": [e_svg, o_svg], "E": E, "dE": dE, "O": O, "dO": dO, "inner": [curve(E, dE, O, dO, 220)],
                "ids": {"card": cid, "chip": chid, "E": e_id, "O": o_id, "nb": len(rows)}, "rect": (bx, by, bw, bh)}

    def a_figure(self, g):
        ids, p = g["ids"], g["plug"]
        c = ids["card"]
        self.plug(f'#{ids["E"]}', p)
        self.fill(ids["chip"], p + F, "l")
        self.rise(f'#{ids["chip"]} .rv', p + 3 * F, dy=24)
        self.fill(c, p + 4 * F, "t")
        self.tw(f'tl.set("#{c} .dg > b", {{yPercent:110}}, 0);')
        self.tw(f'tl.fromTo("#{c} .dg > b", {{yPercent:110}}, {{yPercent:0, duration:0.38, ease:"power3.out", stagger:{2 * F:.4f}, immediateRender:false}}, {p + 0.22:.3f});')
        nd = len(str(g["b"].get("value", "")))
        t1 = p + 0.22 + nd * 2 * F
        self.rise(f'#{c} .hero .u', t1, dy=30)
        self.rise(f'#{c} .ln', t1 + 0.08, 3 * F)
        tb = t1 + 0.22
        if ids["nb"]:
            self.rise(f'#{c} .st, #{c} .bl', tb, 3 * F, dx=-30, dy=0)
            self.tw(f'tl.fromTo("#{c} .bar", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power3.out", stagger:0.15, immediateRender:false}}, {tb + 0.1:.3f});')
            self.rise(f'#{c} .bv', tb + 0.45, 0.15, dx=-20, dy=0)
        t_in = tb + 0.4
        self.tip(g["Lin"][0], g["Lin"][-1], t_in, 0.45, "none")
        self.show_sock(f'#{ids["O"]}', t_in + 0.45)
        g["out_ready"] = t_in + 0.5

    def g_split(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        items = b.get("items", [])[:4]
        vmax = max(float(it["value"]) for it in items)
        n = len(items)
        if V:
            root = (bx, by, 540, 110)
            x0 = bx + 150
            rh, gap = 150, 40
            ytop = by + 110 + 85
        else:
            root = (bx, by + bh / 2 - 60, 420, 120)
            x0 = bx + 510
            rh, gap = 136, 30
            ytop = by + (bh - (n * rh + (n - 1) * gap)) / 2
        maxw = bx + bw - x0
        html, under, over, ids = [], [], [], {"txt": []}
        rid, rhtml = self.card(*root, self.rv(28, 30 if V else 35, X.rich(b.get("root", "")), "vl", "color:#f1ece0;font-size:40px;line-height:50px;font-family:var(--f-zh)"), dark=True)
        html.append(rhtml)
        ids["root"] = rid
        rb = (root[0] + 80, root[1] + root[3]) if V else (root[0] + root[2], root[1] + root[3] / 2)
        rbd = (0, 1) if V else (1, 0)
        cards = []
        for j, it in enumerate(items):
            v = float(it["value"])
            w = max(140.0, maxw * v / vmax)
            yc = ytop + j * (rh + gap) + rh / 2
            rect = (x0, yc - rh / 2, w, rh)
            lab, val = X.rich(it.get("label", "")), X.rich(it.get("show", ""))
            if w >= 300:
                inner = self.rv(28, 16, lab, "lb") + self.rv(28, 54, val, "vl", "font-size:72px;line-height:1.1")
                cid, chtml = self.card(*rect, inner)
                ids["txt"].append(None)
            else:      # a thin card: its value and label sit just outside it, on the paper
                cid, chtml = self.card(*rect, "")
                lid = self.nid("o")
                html.append(f'<div class="th-cd" id="{lid}" style="left:{x0 + w + 24:.0f}px;top:{yc - rh / 2:.0f}px;width:10px;height:10px">'
                            f'<div class="rv vl" style="left:0;top:10px;font-size:72px;line-height:1.1">{val}</div>'
                            f'<div class="rv lb" style="left:0;top:{rh - 44}px">{lab}</div></div>')
                ids["txt"].append(lid)
            html.append(chtml)
            S, dS = self.edge(rect, "l")
            sid, ssvg = self.sock(S)
            over.append(ssvg)
            bwid = 3 + 7 * v / vmax
            if V:
                segs = [(rb, (rb[0], rb[1] + 0.6 * (S[1] - rb[1])), (S[0] - 0.7 * (S[0] - rb[0]), S[1]), S)]
            else:
                segs = [curve(rb, rbd, S, dS, None, 60, 160)]
            cards.append({"rect": rect, "id": cid, "sk": sid, "segs": segs, "w": bwid, "S": S})
        main_j = n - 1 if V else 0      # 16:9: the main thread runs through the top (largest) card and leaves by its right edge
        for j, c in enumerate(cards):
            if j == main_j: continue
            pid, L, psvg = self.path(c["segs"], "br", c["w"])
            under.append(psvg)
            c["pid"], c["L"] = pid, L
        last = cards[main_j]["rect"]
        if V:
            E, dE = self.edge(root, "t", 0.5)
            O, dO = self.v_exit(g, last)
            inner = [curve(E, dE, rb, (0, 1), 40), *cards[main_j]["segs"], curve(cards[main_j]["S"], (1, 0), O, dO, 60)]
        else:
            E, dE = self.edge(root, "l", 0.5)
            O, dO = self.edge(last, "r", 0.5)
            inner = [curve(E, dE, rb, rbd, 120), *cards[main_j]["segs"], curve(cards[main_j]["S"], (1, 0), O, dO, 60)]
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        over += [e_svg, o_svg]
        ids.update({"E": e_id, "O": o_id})
        g["cards"] = cards; g["main_j"] = main_j
        return {"html": html, "under": under, "over": over, "E": E, "dE": dE, "O": O, "dO": dO, "inner": inner, "ids": ids,
                "rect": (bx, by, bw, bh)}

    def a_split(self, g):
        ids, p = g["ids"], g["plug"]
        self.plug(f'#{ids["E"]}', p)
        self.fill(ids["root"], p + F, "t" if self.V else "l")
        self.rise(f'#{ids["root"]} .rv', p + 3 * F, dy=24)
        t0 = p + 0.32
        Lin = g["Lin"]
        for j, c in enumerate(g["cards"]):
            tj = t0 + j * 0.16
            dur = 0.5
            if j == g["main_j"]:
                self.tip(Lin[0], Lin[2], tj - 0.12, dur + 0.12, "power1.inOut")
            else:
                self.draw_path(f'#{c["pid"]}', c["L"], tj, dur)
            ta = tj + dur
            self.show_sock(f'#{c["sk"]}', ta - 2 * F)
            self.plug(f'#{c["sk"]}', ta)
            self.fill(c["id"], ta + F, "l")
            self.rise(f'#{c["id"]} .rv', ta + 3 * F, 2 * F)
            if ids["txt"][j]:
                self.rise(f'#{ids["txt"][j]} .rv', ta + 5 * F, 3 * F, dx=-30, dy=0)
        tl = t0 + (len(g["cards"]) - 1) * 0.16 + 0.5
        self.tip(Lin[2], Lin[3], tl + 0.25, 0.3, "none")
        self.show_sock(f'#{ids["O"]}', tl + 0.55)
        g["out_ready"] = tl + 0.6

    def g_steps(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        cx, cy = g["c"]
        items = b.get("items", [])[:5]
        n = len(items)
        if V:
            w, h = 430, 210
            cs = [(cx + (-(bw - w) / 2 if j % 2 == 0 else (bw - w) / 2), by + h / 2 + j * (bh - h) / max(1, n - 1)) for j in range(n)]
            vpx, upx = 76, 32
        else:
            w, h = 300, 250
            cs = [(bx + w / 2 + j * (bw - w) / max(1, n - 1), cy + (-(bh - h) / 2 if j % 2 == 0 else (bh - h) / 2)) for j in range(n)]
            vpx, upx = 64, 28
        html, cards = [], []
        for j, (it, c) in enumerate(zip(items, cs)):
            rect = (c[0] - w / 2, c[1] - h / 2, w, h)
            v = X.rich(it.get("v", ""))
            u = f'<span class="u" style="font-size:{upx}px;margin-left:8px">{X.rich(it["u"])}</span>' if it.get("u") else ""
            inner = self.rv(30, 26, X.rich(it.get("k", "")), "lb") + self.rv(30, 86, f'{v}{u}', "vl", f"font-size:{vpx}px;line-height:1.1")
            cid, chtml = self.card(*rect, inner)
            html.append(chtml)
            cards.append({"rect": rect, "id": cid, "c": c})
        first, last = cards[0]["rect"], cards[-1]["rect"]
        if V:
            E, dE = self.edge(first, "t", 0.5)
            O, dO = self.v_exit(g, last)
        else:
            E, dE = self.edge(first, "l", 0.5)
            O, dO = self.edge(last, "r", 0.5)
        inner = through([E] + [c["c"] for c in cards] + [O], dE, dO)
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        g["cards"] = cards
        return {"html": html, "over": [e_svg, o_svg], "E": E, "dE": dE, "O": O, "dO": dO, "inner": inner,
                "ids": {"E": e_id, "O": o_id}, "rect": (bx, by, bw, bh)}

    def a_steps(self, g):
        ids, p = g["ids"], g["plug"]
        self.plug(f'#{ids["E"]}', p)
        Lin = g["Lin"]
        n = len(g["cards"])
        dur = 0.45 * (n + 1)
        t0 = p + 0.08
        L0, L1 = Lin[0], Lin[-1]
        self.tip(L0, L1, t0, dur, "none")
        for j, c in enumerate(g["cards"]):
            Lc = Lin[j + 1]
            near = Lc - 90
            tj = t0 + dur * max(0.0, (near - L0) / (L1 - L0))
            self.fill(c["id"], tj, "t" if self.V else "l")
            self.rise(f'#{c["id"]} .rv', tj + 2 * F, 3 * F)
        self.show_sock(f'#{ids["O"]}', t0 + dur)
        g["out_ready"] = t0 + dur + 0.05

    def g_compare(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        a, c2 = b["a"], b["b"]
        va, vb = float(a["value"]), float(c2["value"])
        ch = 64
        if V:
            w, gap = 360, 220
            x_a = bx
        else:
            w, gap = 400, 300
            x_a = bx + (bw - 2 * w - gap) / 2
        base = by + bh
        hmax = bh - ch - 24
        ha, hb = hmax * va / max(va, vb), hmax * vb / max(va, vb)
        ra = (x_a, base - ha, w, ha)
        rb = (x_a + w + gap, base - hb, w, hb)
        def inner(it):
            return self.rv(30, 28, X.rich(it.get("show", "")), "vl", "font-size:92px;line-height:1") + self.rv(32, 136, X.rich(it.get("label", "")), "lb")
        aid, ahtml = self.card(*ra, inner(a), dark=True)
        bid, bhtml = self.card(*rb, inner(c2))
        kick = b.get("kicker", "")
        kid, khtml = self.chip(ra[0], ra[1] - ch - 20, ch, X.rich(kick))
        # one curly brace in the gap, from the top of the taller card down to the top of the shorter one, its point toward the multiple
        x0, bwd = ra[0] + w + 40, 54
        y1, y2 = ra[1], rb[1]
        ym = (y1 + y2) / 2
        r = min(40.0, (y2 - y1) / 4)
        xm = x0 + bwd / 2
        br = (f'M{x0:.1f} {y1:.1f} Q{xm:.1f} {y1:.1f} {xm:.1f} {y1 + r:.1f} L{xm:.1f} {ym - r:.1f} Q{xm:.1f} {ym:.1f} {x0 + bwd:.1f} {ym:.1f} '
              f'Q{xm:.1f} {ym:.1f} {xm:.1f} {ym + r:.1f} L{xm:.1f} {y2 - r:.1f} Q{xm:.1f} {y2:.1f} {x0:.1f} {y2:.1f}')
        Lb = 2 * (y2 - y1) + 4 * bwd
        brid = self.nid("b")
        over = [f'<path id="{brid}" class="acc" d="{br}" style="stroke-dasharray:{Lb:.1f};stroke-dashoffset:{Lb:.1f}"/>']
        ratio = b.get("ratio", "")
        rid = self.nid("r")
        rpx = 96
        rx = rb[0] + 10            # the multiple sits above the shorter card, level with the brace's point
        ry = min(ym - rpx / 2, rb[1] - rpx - 24)
        ratio_html = (f'<div class="th-cd" id="{rid}" style="left:{rx:.0f}px;top:{ry:.0f}px;width:10px;height:10px">'
                      f'<div class="rv vl" style="left:0;top:0;font-size:{rpx}px;line-height:1;color:#1d1b18">{esc(ratio)}</div></div>')
        E, dE = self.edge(ra, "t", 0.78) if V else self.edge(ra, "l", self.h_at(g, "in"))
        O, dO = self.v_exit(g, rb) if V else self.edge(rb, "r", self.h_at(g, "out"))
        pa, pb = (ra[0] + w * 0.78, base - 50), (rb[0] + w * 0.3, base - 50)
        inner_segs = [line(E, pa) if V else curve(E, dE, pa, (0, 1), 80), line(pa, pb), curve(pb, (1, 0), O, dO, 40)]
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        over += [e_svg, o_svg]
        return {"html": [khtml, ahtml, bhtml, ratio_html], "over": over, "E": E, "dE": dE, "O": O, "dO": dO, "inner": inner_segs,
                "ids": {"a": aid, "b": bid, "k": kid, "br": brid, "Lb": Lb, "r": rid, "E": e_id, "O": o_id},
                "rect": (bx, ra[1] - ch - 20, bw, base - (ra[1] - ch - 20))}

    def a_compare(self, g):
        ids, p = g["ids"], g["plug"]
        Lin = g["Lin"]
        self.plug(f'#{ids["E"]}', p)
        self.fill(ids["k"], p + F, "l")
        self.rise(f'#{ids["k"]} .rv', p + 3 * F, dy=24)
        self.tw(f'tl.fromTo("#{ids["a"]} > .bg", {{clipPath:"inset(0% 0% 100% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.5, ease:"power3.out", immediateRender:false}}, {p + 3 * F:.3f});')
        self.tw(f'tl.fromTo("#{ids["a"]} > .ol", {{opacity:1}}, {{opacity:0, duration:0.2, ease:"none", immediateRender:false}}, {p + 0.2:.3f});')
        self.rise(f'#{ids["a"]} .rv', p + 0.3, 3 * F)
        self.tip(Lin[0], Lin[2], p + 0.15, 0.6, "power1.inOut")
        tb = p + 0.75
        self.tw(f'tl.fromTo("#{ids["b"]} > .bg", {{clipPath:"inset(100% 0% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.45, ease:"power3.out", immediateRender:false}}, {tb:.3f});')
        self.tw(f'tl.fromTo("#{ids["b"]} > .ol", {{opacity:1}}, {{opacity:0, duration:0.2, ease:"none", immediateRender:false}}, {tb + 0.15:.3f});')
        self.rise(f'#{ids["b"]} .rv', tb + 0.2, 3 * F)
        self.draw_path(f'#{ids["br"]}', ids["Lb"], tb + 0.55, 12 * F, "power2.inOut")
        self.rise(f'#{ids["r"]} .rv', tb + 0.55 + 9 * F, dy=40)
        self.tip(Lin[2], Lin[3], tb + 0.4, 0.3, "none")
        self.show_sock(f'#{ids["O"]}', tb + 0.7)
        g["out_ready"] = tb + 0.75

    def g_gate(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        yes, no = b["yes"], b["no"]
        binh = 110
        if V:
            root = (bx, by, 600, 110)
            cw, ch = 440, bh - 220 - 60 - binh
            ry = (bx, by + 110 + 110, cw, ch)
            rn = (bx + bw - cw, by + 110 + 110, cw, ch)
        else:
            root = (bx, by + 150, 300, 150)
            cw, ch = 380, bh - 60 - binh - 40      # 16:9: root · crossed card · ticked card, so the main thread leaves to the right
            rn = (bx + 360, by + 40, cw, ch)
            ry = (bx + bw - cw, by + 40, cw, ch)
        rl = b.get("root", "")
        if V:
            rinner = self.rv(28, 30, X.rich(rl), "vl", "color:#f1ece0;font-size:36px;line-height:50px;font-family:var(--f-zh)")
        else:
            rinner = "".join(self.rv(26, 26 + j * 50, X.rich(s), "vl", "color:#f1ece0;font-size:32px;line-height:46px;font-family:var(--f-zh)") for j, s in enumerate(rl.split(" · ")))
        rid, rhtml = self.card(*root, rinner, dark=True)

        ly = max(150, ch * 0.42)        # label / value / note spread down a tall card

        def gcard(rect, it):
            inner = (self.rv(32, ly, X.rich(it.get("k", "")), "lb")
                     + self.rv(32, ly + 46, X.rich(it.get("v", "")), "vl", "font-size:68px;line-height:1.15")
                     + self.rv(32, ly + 46 + max(104, ch * 0.2), X.rich(it.get("note", "")), "lb"))
            return self.card(*rect, inner)
        yid, yhtml = gcard(ry, yes)
        nid_, nhtml = gcard(rn, no)
        over, under = [], []
        # a big tick and a big cross, drawn in orange at the top of each card
        tx, ty = ry[0] + 80, ry[1] + max(82, ch * 0.2)
        tick = f'M{tx - 44:.1f} {ty + 4:.1f} L{tx - 10:.1f} {ty + 38:.1f} L{tx + 52:.1f} {ty - 40:.1f}'
        Lt = math.hypot(34, 34) + math.hypot(62, 78)
        kx, ky = rn[0] + 80, rn[1] + max(82, ch * 0.2)
        cross = f'M{kx - 38:.1f} {ky - 38:.1f} L{kx + 38:.1f} {ky + 38:.1f} M{kx + 38:.1f} {ky - 38:.1f} L{kx - 38:.1f} {ky + 38:.1f}'
        Lc = 2 * math.hypot(76, 76)
        tid, cid2 = self.nid("t"), self.nid("x")
        over.append(f'<path id="{tid}" class="acc" d="{tick}" style="stroke-width:9;stroke-dasharray:{Lt:.1f};stroke-dashoffset:{Lt:.1f}"/>')
        over.append(f'<path id="{cid2}" class="acc" d="{cross}" style="stroke-width:9;stroke-dasharray:{Lc:.1f};stroke-dashoffset:{Lc:.1f}"/>')
        # the main thread: root → ticked card → on. A branch from the root to the crossed card, and from it into the bin
        if V:
            E, dE = self.edge(root, "t", 0.5)
            r_out = (ry[0] + cw * 0.5, root[1] + root[3])
            Sy, dSy = self.edge(ry, "t", 0.5)
            r_br = (root[0] + root[2] - 60, root[1] + root[3])
            Sn, dSn = self.edge(rn, "t", 0.5)
            brn = [curve(r_br, (0, 1), Sn, dSn, None, 40, 80)]
            nx = g["next"][0] if g["next"] else g["c"][0]
            O, dO = self.v_exit(g, ry)
            inner = [curve(E, dE, r_out, (0, 1), 40), line(r_out, Sy), curve(Sy, dSy, O, dO, 120)]
            g["iy"] = 2
        else:
            E, dE = self.edge(root, "l", self.h_at(g, "in"))
            r_out = (root[0] + root[2], root[1] + root[3] * 0.5)
            r_top = (root[0] + root[2] * 0.6, root[1])
            Sn, dSn = self.edge(rn, "l", 0.5)
            brn = [curve(r_out, (1, 0), Sn, dSn, None, 20, 40)]
            Sy, dSy = self.edge(ry, "t", 0.5)
            apex = (rn[0] + cw * 0.5, rn[1] - 40)          # the main thread arcs over the crossed card to the ticked one
            O, dO = self.edge(ry, "r", self.h_at(g, "out"))
            inner = [curve(E, dE, r_top, (0, -1), 60),
                     (r_top, (r_top[0], apex[1]), (apex[0] - 200, apex[1]), apex),
                     (apex, (apex[0] + 200, apex[1]), (Sy[0], apex[1] - 0), Sy),
                     curve(Sy, dSy, O, dO, 120)]
            g["iy"] = 3
        pn_, Ln, pns = self.path(brn, "br", 3)
        under.append(pns)
        sy_id, sy_svg = self.sock(Sy); sn_id, sn_svg = self.sock(Sn)
        # the bin: 110 px tall, just below-right of the crossed card (60 px gap); the branch ends inside it
        bwid = 96
        bxx = rn[0] + rn[2] - bwid / 2 - 10
        btop = rn[1] + rn[3] + 60
        Bo, dBo = self.edge(rn, "b", 1 - (rn[0] + rn[2] - bxx) / rn[2])
        bend = (bxx, btop + binh * 0.55)
        pb_, Lbn, pbs = self.path([line(Bo, bend)], "br", 3)
        under.append(pbs)
        sb_id, sb_svg = self.sock(Bo)
        hw, top, bot = bwid / 2, btop, btop + binh
        binp = (f'M{bxx - hw:.1f} {top + 14:.1f} L{bxx - hw + 10:.1f} {bot:.1f} L{bxx + hw - 10:.1f} {bot:.1f} L{bxx + hw:.1f} {top + 14:.1f} '
                f'M{bxx - hw - 10:.1f} {top + 14:.1f} L{bxx + hw + 10:.1f} {top + 14:.1f} M{bxx - 14:.1f} {top:.1f} L{bxx + 14:.1f} {top:.1f} '
                f'M{bxx - 18:.1f} {top + 34:.1f} L{bxx - 15:.1f} {bot - 14:.1f} M{bxx + 18:.1f} {top + 34:.1f} L{bxx + 15:.1f} {bot - 14:.1f}')
        bin_id = self.nid("n")
        over.append(f'<g id="{bin_id}" style="transform-box:fill-box;transform-origin:50% 100%"><path class="ink" d="{binp}" style="stroke-width:5"/></g>')
        over += [sy_svg, sn_svg, sb_svg]
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        over += [e_svg, o_svg]
        top_y = min(root[1], ry[1])
        return {"html": [rhtml, yhtml, nhtml], "under": under, "over": over, "E": E, "dE": dE, "O": O, "dO": dO, "inner": inner,
                "ids": {"root": rid, "y": yid, "n": nid_, "t": tid, "x": cid2, "Lt": Lt, "Lc": Lc, "pn": pn_, "Ln": Ln,
                        "pb": pb_, "Lb": Lbn, "sy": sy_id, "sn": sn_id, "sb": sb_id, "bin": bin_id, "E": e_id, "O": o_id},
                "rect": (bx, top_y, bw, bot - top_y)}

    def a_gate(self, g):
        ids, p = g["ids"], g["plug"]
        Lin = g["Lin"]
        self.plug(f'#{ids["E"]}', p)
        self.fill(ids["root"], p + F, "t" if self.V else "l")
        self.rise(f'#{ids["root"]} .rv', p + 3 * F, 3 * F, dy=24)
        t1 = p + 0.3
        iy = g["iy"]
        self.tip(Lin[0], Lin[iy], t1 - 0.1, 0.45, "power1.inOut")
        self.show_sock(f'#{ids["sy"]}', t1 + 0.3); self.plug(f'#{ids["sy"]}', t1 + 0.36)
        self.fill(ids["y"], t1 + 0.36 + F, "t")
        self.rise(f'#{ids["y"]} .rv', t1 + 0.36 + 3 * F, 3 * F)
        self.draw_path(f'#{ids["t"]}', ids["Lt"], t1 + 0.7, 8 * F, "power2.out")
        t2 = t1 + 0.9
        self.draw_path(f'#{ids["pn"]}', ids["Ln"], t2, 0.4)
        self.show_sock(f'#{ids["sn"]}', t2 + 0.34); self.plug(f'#{ids["sn"]}', t2 + 0.4)
        self.fill(ids["n"], t2 + 0.4 + F, "t" if self.V else "l")
        self.rise(f'#{ids["n"]} .rv', t2 + 0.4 + 3 * F, 3 * F)
        self.draw_path(f'#{ids["x"]}', ids["Lc"], t2 + 0.75, 8 * F, "power2.out")
        t3 = t2 + 1.05
        self.tw(f'tl.fromTo("#{ids["bin"]}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.35, ease:"power3.out", immediateRender:false}}, {t3 - 0.3:.3f});')
        self.show_sock(f'#{ids["sb"]}', t3 - 2 * F)
        self.draw_path(f'#{ids["pb"]}', ids["Lb"], t3, 0.3, "power2.in")
        self.tw(f'tl.fromTo("#{ids["bin"]}", {{rotation:0}}, {{rotation:-3, duration:{3 * F:.3f}, ease:"power2.out", yoyo:true, repeat:1, immediateRender:false}}, {t3 + 0.3:.3f});')
        self.tip(Lin[iy], Lin[-1], t3 + 0.2, 0.35, "none")
        self.show_sock(f'#{ids["O"]}', t3 + 0.55)
        g["out_ready"] = t3 + 0.6

    def g_stack(self, g):
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        rows, tot = b.get("rows", []), b.get("total", {})
        note = b.get("note", "")
        x, y, w, h = bx, by, bw, bh
        hh = 100 if V else 70
        th = 210 if V else 170
        nh = 80 if note else 30
        rh = (h - hh - th - nh - 30) / max(1, len(rows))
        vk, vv, tk, tv = (38, 84, 42, 108) if V else (34, 72, 38, 96)
        parts = [self.rv(44, 28, X.rich(b.get("head", "单位：亿元")), "lb hd")]
        for j, r in enumerate(rows):
            ry = hh + j * rh
            parts.append(f'<div class="rv row" style="left:0;top:{ry:.0f}px;width:{w}px;height:{rh:.0f}px">'
                         f'<span class="tx" style="position:absolute;left:44px;top:{rh / 2 - vk * 0.7:.0f}px;font-size:{vk}px">{X.rich(r.get("k", ""))}</span>'
                         f'<span class="vl" style="position:absolute;right:44px;top:{rh / 2 - vv * 0.62:.0f}px;font-size:{vv}px;line-height:1.15">{X.rich(r.get("v", ""))}</span>'
                         f'<i style="position:absolute;left:44px;right:44px;bottom:0;height:1px;background:#d8cfbd"></i></div>')
        ty = hh + len(rows) * rh + 30
        parts.append(f'<div class="rv tot dk" style="left:22px;top:{ty:.0f}px;width:{w - 44}px;height:{th}px;background:#24211d;border-radius:10px;opacity:1;clip-path:inset(0% 100% 0% 0%)">'
                     f'<span class="tx" style="position:absolute;left:28px;top:{th / 2 - tk * 0.7:.0f}px;font-size:{tk}px;font-weight:700;color:#f1ece0">{X.rich(tot.get("k", ""))}</span>'
                     f'<span class="vl" style="position:absolute;right:28px;top:{th / 2 - tv * 0.62:.0f}px;font-size:{tv}px;line-height:1.15;color:#e8602c">{X.rich(tot.get("v", ""))}</span></div>')
        if note:
            parts.append(self.rv(44, ty + th + 22, X.rich(note), "lb nt"))
        cid, html = self.card(x, y, w, h, "".join(parts))
        if V:
            E, dE = self.edge((x, y, w, h), "l", 0.2)
            nx = g["next"][0] if g["next"] else g["c"][0]
            O, dO = self.v_exit(g, (x, y, w, h))
        else:
            E, dE = self.edge((x, y, w, h), "l", self.h_at(g, "in"))
            O, dO = self.edge((x, y, w, h), "r", self.h_at(g, "out"))
        e_id, e_svg = self.sock(E); o_id, o_svg = self.sock(O)
        return {"html": [html], "over": [e_svg, o_svg], "E": E, "dE": dE, "O": O, "dO": dO, "inner": [curve(E, dE, O, dO, 200)],
                "ids": {"card": cid, "E": e_id, "O": o_id, "n": len(rows)}, "rect": (x, y, w, h)}

    def a_stack(self, g):
        ids, p = g["ids"], g["plug"]
        Lin = g["Lin"]
        c = ids["card"]
        self.plug(f'#{ids["E"]}', p)
        self.fill(c, p + F, "l")
        self.rise(f'#{c} .hd', p + 4 * F, dy=24)
        for j in range(ids["n"]):
            self.rise(f'#{c} .row:nth-of-type({j + 2})', p + 0.3 + j * 0.3, dx=-60, dy=0)
        tt = p + 0.3 + ids["n"] * 0.3 + 0.1
        self.tw(f'tl.fromTo("#{c} .tot", {{clipPath:"inset(0% 100% 0% 0%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{8 * F:.4f}, ease:"power2.out", immediateRender:false}}, {tt:.3f});')
        self.rise(f'#{c} .tot .tx, #{c} .tot .vl', tt + 4 * F, 3 * F, dy=30)
        self.rise(f'#{c} .nt', tt + 0.4, dy=24)
        self.tip(Lin[0], Lin[-1], tt + 0.3, 0.35, "none")
        self.show_sock(f'#{ids["O"]}', tt + 0.65)
        g["out_ready"] = tt + 0.7

    def g_sum(self, g):
        """the thread's terminal: the summary card, plugged in at the end of the path, with a closed end-dot."""
        X, V, b = self.X, self.V, g["b"]
        bx, by, bw, bh = self.box(g)
        figs = b.get("figures", [])[:3]
        x, y, w, h = bx, by, bw, bh
        head = 100 if V else 90
        rh = (h - head - 30) / max(1, len(figs))
        vpx, upx, kpx = (110, 40, 36) if V else (100, 36, 34)
        parts = [self.rv(48, 40, X.rich(b.get("label", "")), "lb", "font-size:30px")]
        for j, f in enumerate(figs):
            yy = head + j * rh
            u = f'<span class="u" style="font-size:{upx}px;margin-left:12px">{X.rich(f.get("u", ""))}</span>' if f.get("u") else ""
            parts.append(self.rv(48, yy + rh / 2 - kpx * 0.7, X.rich(f.get("k", "")), "lb fk", f"font-size:{kpx}px"))
            parts.append(f'<div class="rv vl fv" style="right:48px;top:{yy + rh / 2 - vpx * 0.6:.0f}px;font-size:{vpx}px;line-height:1.15">{X.rich(f.get("v", ""))}{u}</div>')
            if j: parts.append(f'<i class="rv rule" style="left:48px;right:48px;top:{yy:.0f}px;height:1px;opacity:1;background:rgba(241,236,224,.2)"></i>')
        cid, html = self.card(x, y, w, h, "".join(parts), dark=True)
        if V:
            E, dE = self.edge((x, y, w, h), "t", 0.22 if g["prev"][0] < g["c"][0] else 0.78)
        else:
            E, dE = self.edge((x, y, w, h), "l", 0.5)
        e_id, e_svg = self.sock(E)
        dot_id = self.nid("z")
        dot = f'<circle id="{dot_id}" cx="{E[0]:.1f}" cy="{E[1]:.1f}" r="12" fill="#e8602c" style="transform-box:fill-box;transform-origin:50% 50%;opacity:0"/>'
        return {"html": [html], "over": [e_svg, dot], "E": E, "dE": dE, "O": E, "dO": dE, "inner": [],
                "ids": {"E": e_id, "dot": dot_id, "card": cid}, "rect": (x, y, w, h)}

    def a_sum(self, g):
        ids, p = g["ids"], g["plug"]
        c = ids["card"]
        self.plug(f'#{ids["E"]}', p)
        self.tw(f'tl.fromTo("#{ids["dot"]}", {{opacity:0, attr:{{r:4}}}}, {{opacity:1, attr:{{r:12}}, duration:{6 * F:.4f}, ease:"power3.out", immediateRender:false}}, {p + 8 * F:.3f});')
        self.fill(c, p + 2 * F, "t" if self.V else "l")
        self.rise(f'#{c} .rv:not(.rule)', p + 0.2, 3 * F, dy=40)

    # ---------------------------------------------------- camera
    def fit(self, g):
        x, y, w, h = g["rect"]
        return (x + w / 2, y + h / 2), min(self.TW / w, self.TH / h, 1.4)

    def cam_to(self, a, sa, b, sb, m, dur, dip=True, blur=True):
        fx, fy = self.fx, self.fy
        self.tw(f'tl.fromTo("#thworld", {{x:{fx - a[0]:.1f}, y:{fy - a[1]:.1f}}}, {{x:{fx - b[0]:.1f}, y:{fy - b[1]:.1f}, duration:{dur}, ease:"power2.inOut", immediateRender:false}}, {m:.3f});')
        if dip:
            sd = 0.82 * min(sa, sb)
            self.tw(f'tl.fromTo("#thzoom", {{scale:{sa:.4f}}}, {{scale:{sd:.4f}, duration:{dur / 2:.3f}, ease:"sine.inOut", immediateRender:false}}, {m:.3f});')
            self.tw(f'tl.fromTo("#thzoom", {{scale:{sd:.4f}}}, {{scale:{sb:.4f}, duration:{dur / 2:.3f}, ease:"sine.inOut", immediateRender:false}}, {m + dur / 2:.3f});')
        else:
            self.tw(f'tl.fromTo("#thzoom", {{scale:{sa:.4f}}}, {{scale:{sb:.4f}, duration:{dur}, ease:"power2.inOut", immediateRender:false}}, {m:.3f});')
        if blur:      # directional blur in the fastest third, along the move
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            bx, by = 10 * abs(dx) / ln, 10 * abs(dy) / ln
            t1, t2 = m + dur / 3, m + 2 * dur / 3
            self.tw(f'tl.set("#thcam", {{filter:"url(#thmb)"}}, {t1 - 2 * F:.3f});')
            self.tw(f'(()=>{{const o={{v:0}}, el=document.getElementById("thmbg"); '
                    f'tl.fromTo(o, {{v:0}}, {{v:1, duration:{(t2 - t1) / 2:.3f}, ease:"sine.inOut", immediateRender:false, onUpdate:()=>el.setAttribute("stdDeviation", (o.v*{bx:.2f}).toFixed(2)+" "+(o.v*{by:.2f}).toFixed(2))}}, {t1:.3f}); '
                    f'tl.fromTo(o, {{v:1}}, {{v:0, duration:{(t2 - t1) / 2:.3f}, ease:"sine.inOut", immediateRender:false, onUpdate:()=>el.setAttribute("stdDeviation", (o.v*{bx:.2f}).toFixed(2)+" "+(o.v*{by:.2f}).toFixed(2))}}, {(t1 + t2) / 2:.3f});}})();')
            self.tw(f'tl.set("#thcam", {{filter:"none"}}, {t2 + 2 * F:.3f});')

    def drift(self, c, s, v, a, end):
        if end - a <= 0.2: return
        fx, fy = self.fx, self.fy
        d = (16 / s * v[0], 16 / s * v[1])
        self.tw(f'tl.fromTo("#thworld", {{x:{fx - c[0]:.1f}, y:{fy - c[1]:.1f}}}, {{x:{fx - c[0] - d[0]:.1f}, y:{fy - c[1] - d[1]:.1f}, duration:{end - a - 0.01:.3f}, ease:"sine.inOut", immediateRender:false}}, {a:.3f});')
        return (c[0] + d[0], c[1] + d[1])

    def camera(self):
        G, n = self.G, len(self.G)
        fx, fy = self.fx, self.fy
        for g in G:
            g["cc"], g["s"] = self.fit(g)
        for k, g in enumerate(G):       # drift direction: toward the next group
            nxt = G[k + 1]["cc"] if k + 1 < n else (g["cc"][0], g["cc"][1] + 1)
            vx, vy = nxt[0] - g["cc"][0], nxt[1] - g["cc"][1]
            vl = math.hypot(vx, vy) or 1
            g["dv"] = (vx / vl, vy / vl)
        # opening: wide over the first three groups, the cards still empty outlines; then push in
        first = G[:3]
        o = (sum(q["cc"][0] for q in first) / len(first), sum(q["cc"][1] for q in first) / len(first))
        s0 = 0.35
        self.tw(f'tl.set("#thworld", {{x:{fx - o[0]:.1f}, y:{fy - o[1]:.1f}}}, 0);')
        self.tw(f'tl.set("#thzoom", {{scale:{s0}}}, 0);')
        push0, pushd = 0.8, 1.1
        self.cam_to(o, s0, G[0]["cc"], G[0]["s"], push0, pushd, dip=False, blur=False)
        G[0]["a"] = push0 + pushd
        G[0]["plug"] = push0 + pushd - 0.12
        G[0]["lead"] = (push0 + 0.1, pushd - 0.22)
        self.path_log = [("open", o, s0), (0, G[0]["cc"], G[0]["s"])]
        self.wide = None
        end0 = G[1]["t"] - 0.55 if n > 1 else self.D
        G[0]["rest"] = self.drift(G[0]["cc"], G[0]["s"], G[0]["dv"], G[0]["a"], end0) or G[0]["cc"]
        for k in range(1, n):
            g, h = G[k - 1], G[k]
            m = h["t"] - 0.55
            here = g.get("rest", g["cc"])
            if h["b"]["scene"] == "sum":
                # (a) pull back over the whole path and hold: every card a solid block, the thread drawn 6 px wide on screen
                xs0 = [q["rect"][0] for q in G]; xs1 = [q["rect"][0] + q["rect"][2] for q in G]
                ys0 = [q["rect"][1] for q in G]; ys1 = [q["rect"][1] + q["rect"][3] for q in G]
                bx0, bx1, by0, by1 = min(xs0) - 60, max(xs1) + 60, min(ys0) - 60, max(ys1) + 60
                sw = min((960 if self.V else 1800) / (bx1 - bx0), (1600 if self.V else 860) / (by1 - by0))
                wc = ((bx0 + bx1) / 2 - ((540 if self.V else 960) - fx) / sw, (by0 + by1) / 2 - ((960 if self.V else 540) - fy) / sw)
                dur = 1.5
                self.cam_to(here, g["s"], wc, sw, m, dur, dip=False, blur=False)
                self.wide = (m, sw, m + dur, m + dur + 1.2)
                self.path_log.append(("wide", wc, sw))
                self.wide_state(m + 0.35, m + dur + 1.2, sw)
                # (b) then on along the thread to the terminal: the summary card
                m2 = m + dur + 1.2
                d2 = 1.2
                self.cam_to(wc, sw, h["cc"], h["s"], m2, d2, dip=False, blur=True)
                h["a"] = m2 + d2
                h["plug"] = m2 + d2 - 0.15
                h["link"] = (m2 - 0.05, d2 - 0.1)
                h["move"] = (m2, d2)
                self.path_log.append((k, h["cc"], h["s"]))
                break
            dur = 1.05
            self.cam_to(here, g["s"], h["cc"], h["s"], m, dur)
            h["a"] = m + dur
            h["plug"] = m + 0.86
            h["link"] = (m - 0.05, 0.9)
            self.path_log.append((k, h["cc"], h["s"]))
            # the hold on h drifts until the next move
            nxt_m = G[k + 1]["t"] - 0.55 if k + 1 < n else self.D
            h["rest"] = self.drift(h["cc"], h["s"], h["dv"], h["a"], nxt_m) or h["cc"]
        last = G[-1]
        if last["b"]["scene"] == "sum" and "a" in last:
            self.drift(last["cc"], last["s"], (0, 1) if self.V else (1, 0), last["a"], self.D)

    def wide_state(self, t_on, t_off, sw):
        """the pull-back: text off, light cards become solid blocks, the thread and branches drawn at a 6 px screen width."""
        kw = 1.2 / sw
        on, off = 0.45, 0.4
        self.tw(f'tl.fromTo("#thworld", {{"--k":1}}, {{"--k":{kw:.3f}, duration:{on}, ease:"power2.out", immediateRender:false}}, {t_on:.3f});')
        self.tw(f'tl.fromTo("#thworld", {{"--k":{kw:.3f}}}, {{"--k":1, duration:{off}, ease:"power2.in", immediateRender:false}}, {t_off:.3f});')
        self.tw(f'tl.fromTo(".th-g .ct, .th-g .th-cd > .rv", {{opacity:1}}, {{opacity:0, duration:{on}, ease:"none", immediateRender:false}}, {t_on:.3f});')
        self.tw(f'tl.fromTo(".th-g .ct, .th-g .th-cd > .rv", {{opacity:0}}, {{opacity:1, duration:{off}, ease:"none", immediateRender:false}}, {t_off:.3f});')
        self.tw(f'tl.fromTo(".th-cd:not(.dk) > .bg", {{backgroundColor:"#f7f3ea"}}, {{backgroundColor:"#cbbd9f", duration:{on}, ease:"none", immediateRender:false}}, {t_on:.3f});')
        self.tw(f'tl.fromTo(".th-cd:not(.dk) > .bg", {{backgroundColor:"#cbbd9f"}}, {{backgroundColor:"#f7f3ea", duration:{off}, ease:"none", immediateRender:false}}, {t_off:.3f});')
        self.tw(f'tl.fromTo(".th-cd > .ol", {{backgroundColor:"rgba(247,243,234,.7)"}}, {{backgroundColor:"rgba(203,189,159,.9)", duration:{on}, ease:"none", immediateRender:false}}, {t_on:.3f});')
        self.tw(f'tl.fromTo(".th-cd > .ol", {{backgroundColor:"rgba(203,189,159,.9)"}}, {{backgroundColor:"rgba(247,243,234,.7)", duration:{off}, ease:"none", immediateRender:false}}, {t_off:.3f});')

    def depth(self, g):
        """the active group is sharp; the others sit back (3 px blur, 55 % opacity)."""
        k = g["k"]
        sel = f"#thg{k}"
        on = g["a"] - 0.55
        self.tw(f'tl.set("{sel}", {{filter:"blur(0px)", opacity:1, attr:{{"data-far":"0"}}}}, 0);')
        if k:
            self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"1"}}}}, 0.8);')
            self.tw(f'tl.fromTo("{sel}", {{filter:"blur(0px)", opacity:1}}, {{filter:"blur(3px)", opacity:0.55, duration:0.5, ease:"power2.inOut", immediateRender:false}}, 0.8);')
        W = self.wide
        is_sum = g["b"]["scene"] == "sum"
        if k and not is_sum:
            self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"0"}}}}, {on:.3f});')
            self.tw(f'tl.fromTo("{sel}", {{filter:"blur(3px)", opacity:0.55}}, {{filter:"blur(0px)", opacity:1, duration:0.45, ease:"power2.out", immediateRender:false}}, {on:.3f});')
        nxt = self.G[k + 1] if k + 1 < len(self.G) else None
        sharp_into_wide = nxt is not None and nxt["b"]["scene"] == "sum"
        if nxt is not None and not sharp_into_wide and not is_sum:
            off = nxt["t"] - 0.55 + 0.25
            self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"1"}}}}, {off:.3f});')
            self.tw(f'tl.fromTo("{sel}", {{filter:"blur(0px)", opacity:1}}, {{filter:"blur(3px)", opacity:0.55, duration:0.45, ease:"power2.inOut", immediateRender:false}}, {off:.3f});')
        if W:
            m, sw, w_in, w_out = W
            self.tw(f'tl.set("{sel}", {{attr:{{"data-wide":"1"}}}}, {m + 0.2:.3f});')
            self.tw(f'tl.set("{sel}", {{attr:{{"data-wide":"0"}}}}, {w_out + 0.5:.3f});')
            if not sharp_into_wide:
                self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"0"}}}}, {m:.3f});')
                self.tw(f'tl.fromTo("{sel}", {{filter:"blur(3px)", opacity:0.55}}, {{filter:"blur(0px)", opacity:1, duration:0.6, ease:"power2.out", immediateRender:false}}, {m:.3f});')
            # leaving the wide shot for the terminal: everything but the summary card sits back again
            if not is_sum:
                self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"1"}}}}, {w_out + 0.3:.3f});')
                self.tw(f'tl.fromTo("{sel}", {{filter:"blur(0px)", opacity:1}}, {{filter:"blur(3px)", opacity:0.55, duration:0.5, ease:"power2.inOut", immediateRender:false}}, {w_out + 0.3:.3f});')
            else:
                self.tw(f'tl.set("{sel}", {{attr:{{"data-far":"0"}}}}, {m:.3f});')
                self.tw(f'tl.fromTo("{sel}", {{filter:"blur(3px)", opacity:0.55}}, {{filter:"blur(0px)", opacity:1, duration:0.6, ease:"power2.out", immediateRender:false}}, {m:.3f});')


    # ---------------------------------------------------- page furniture outside the canvas
    def build_furniture(self):
        X = self.X
        n = len(self.beats)
        ks, ts, ss = [], [], []
        show = self.meta.get("show", "")
        for k, g in enumerate(self.G):
            i, b = g["i"], g["b"]
            kk = f'{i + 1:02d} / {n:02d}' + (f' · {show}' if show and k == 0 else "")
            ks.append(f'<span id="thk{k}">{esc(kk)}</span>')
            ts.append(f'<span id="tht{k}">{X.rich(b.get("title", ""))}</span>')
            ss.append(f'<span id="ths{k}">{X.rich(b.get("src", ""))}</span>')
            X.used_text.update(kk)
        X.clip("thhd", 0, self.D, f'<div class="th-hd"><div class="k">{"".join(ks)}</div><div class="t">{"".join(ts)}</div></div>'
                                  f'<div class="th-src">{"".join(ss)}</div>', "th-frame", 40, track=4)
        self.tw('tl.set(".th-hd span, .th-src span", {yPercent:115, visibility:"hidden"}, 0);')
        for k, g in enumerate(self.G):
            t_in = max(0.25, g["t"]) if k else 0.3
            for p in ("k", "t", "s"):
                self.tw(f'tl.set("#th{p}{k}", {{visibility:"visible"}}, {t_in + (0.06 if p == "t" else 0):.3f});')
                self.tw(f'tl.fromTo("#th{p}{k}", {{yPercent:115}}, {{yPercent:0, duration:0.35, ease:"power3.out", immediateRender:false}}, {t_in + (0.06 if p == "t" else 0):.3f});')
                if k + 1 < len(self.G):
                    t_out = self.G[k + 1]["t"]
                    self.tw(f'tl.fromTo("#th{p}{k}", {{yPercent:0}}, {{yPercent:-115, duration:0.3, ease:"power2.in", immediateRender:false}}, {t_out - 0.3 + (0.06 if p == "t" else 0):.3f});')
                    self.tw(f'tl.set("#th{p}{k}", {{visibility:"hidden"}}, {t_out + (0.06 if p == "t" else 0) + 0.02:.3f});')


def WORLD(beats, times, X, D):
    Thread(beats, times, X, D).run()


# ---------------------------------------------------------------- effects in this style (gallery cards / fx beats)
STYLE["fx_themes"] = {
    "paper": {"bg": PAPER, "fg": INK, "muted": MUTED, "accent": OR, "card": CARD, "card-fg": INK, "line": EDGE},
    "ink":   {"bg": DARK, "fg": DARKTX, "muted": DMUTED, "accent": OR, "card": "#2e2a25", "card-fg": DARKTX, "line": "#4a443b"},
    "red":   {"bg": PAPER2, "fg": INK, "muted": MUTED, "accent": OR, "card": CARD, "card-fg": INK, "line": EDGE},
    "lemon": {"bg": CARD, "fg": INK, "muted": MUTED, "accent": OR, "card": PAPER, "card-fg": INK, "line": EDGE},
}

FX_CSS = r"""
.fx { background-image:url("__GRAIN__") !important; background-size:320px !important; }
.fx [class*="card"] { border-radius:14px; }
.ctx.thx .wire { position:absolute; inset:0; pointer-events:none; }
.ctx.thx .wire svg { position:absolute; left:0; top:0; overflow:visible; }
.ctx.thx .wire path { fill:none; stroke:#e8602c; stroke-width:3; stroke-linecap:round; }
.ctx.thx .wire circle { fill:#efe9dc; stroke:#e8602c; stroke-width:3; }
.ctx.thx .vig { position:absolute; inset:0; pointer-events:none; background:radial-gradient(ellipse 72% 62% at 50% 46%, rgba(228,220,203,0) 60%, rgba(222,212,192,.7) 100%); }
.ctx.thx .hd { position:absolute; left:96px; right:auto; top:58px; height:auto; border:none; display:block; font-family:var(--f-zh); color:var(--fg); }
.ctx.thx .hd .k { font-family:var(--f-mono); font-size:24px; line-height:32px; color:var(--muted); letter-spacing:.04em; }
.ctx.thx .hd .t { font-size:40px; line-height:56px; font-weight:700; }
.ctx.thx .cap { position:absolute; left:0; right:0; bottom:112px; top:auto; text-align:center; padding:0 120px; }
.ctx.thx .cap > span { display:inline-block; background:rgba(239,233,220,.92); color:#1d1b18; padding:14px 22px; border-radius:10px; font-family:var(--f-zh);
  font-weight:700; line-height:1.3; text-shadow:none; box-shadow:none; }
.ctx.thx .cap .em .emt { background:#e8602c; color:#1d1b18; padding:0 .16em; border-radius:6px; }
.ctx.thx .cap .em .emb { display:none; }
.ctx.thx .ft { position:absolute; left:96px; right:auto; bottom:44px; font-family:var(--f-zh); font-size:22px; color:#6d6558; display:flex; gap:24px; opacity:1; }
.ctx.thx .ft > div { max-width:none; }
#root.v .ctx.thx .hd { top:220px; }
#root.v .ctx.thx .hd .k { font-size:26px; } #root.v .ctx.thx .hd .t { font-size:46px; line-height:62px; }
#root.v .ctx.thx .cap { top:1380px; bottom:auto; }
#root.v .ctx.thx .ft { left:120px; top:1476px; bottom:auto; font-size:24px; flex-direction:column; gap:4px; max-width:840px; }
"""


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around an effect in this style: the same paper (grain + corner vignette), the header top-left (page tag +
    topic), the spoken line on the paper plate, the source line, and a stretch of the orange thread that enters the frame
    at one edge, plugs into a socket and leaves at another — the effect sits on the path like one more card group."""
    P, W, H = X.portrait, X.W, X.H
    if P:
        a, b = (-40, 300), (W + 40, 1720)
        s1, s2 = (150, 360), (930, 1620)
        dpath = f'M{a[0]} {a[1]} C{a[0] + 300} {a[1] - 40} {s1[0] - 260} {s1[1] - 30} {s1[0]} {s1[1]} M{s2[0]} {s2[1]} C{s2[0] + 120} {s2[1] + 40} {b[0] - 120} {b[1] - 80} {b[0]} {b[1]}'
    else:
        a, b = (-40, 230), (W + 40, 960)
        s1, s2 = (110, 250), (1830, 900)
        dpath = f'M{a[0]} {a[1]} C{a[0] + 120} {a[1] - 20} {s1[0] - 90} {s1[1] - 10} {s1[0]} {s1[1]} M{s2[0]} {s2[1]} C{s2[0] + 60} {s2[1] + 20} {b[0] - 60} {b[1] - 40} {b[0]} {b[1]}'
    wire = (f'<div class="wire"><svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><path class="w" d="{dpath}" pathLength="1" style="stroke-dasharray:1;stroke-dashoffset:1"/>'
            f'<circle class="s1" cx="{s1[0]}" cy="{s1[1]}" r="6.5" style="transform-box:fill-box;transform-origin:50% 50%"/>'
            f'<circle class="s2" cx="{s2[0]}" cy="{s2[1]}" r="6.5" style="transform-box:fill-box;transform-origin:50% 50%"/></svg></div>')
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    k = f'{X.beat["i"] + 1:02d} / {X.beat["n"]:02d}' if getattr(X, "beat", None) else ""
    X.used_text.update(k)
    inner = (('<div class="scrim"></div>' if parts["photo"] else "") + wire + '<div class="vig"></div>'
             + f'<div class="hd"><div class="k">{k}</div><div class="t">{parts["topic"]}</div></div>'
             + f'<div class="cap"><span style="font-size:{max(40, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx thx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .w", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.9, ease:"power1.inOut", immediateRender:false}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .s1, {s} .s2", {{attr:{{r:6.5}}}}, {{attr:{{r:10.4}}, duration:{4 * F:.4f}, ease:"power2.out", yoyo:true, repeat:1, immediateRender:false}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .hd .k, {s} .hd .t", {{yPercent:115, opacity:0}}, {{yPercent:0, opacity:1, duration:0.35, ease:"power3.out", stagger:{2 * F:.4f}, immediateRender:false}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{s} .cap > span", {{y:40, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"power3.out", immediateRender:false}}, {t + 0.08:.3f});')


STYLE["css"] = FX_CSS.replace('url("__GRAIN__")', f'url("{GRAIN}")') + r"""
.st-thread .mascot { display:none !important; }
#root.h.st-thread { --cap-bottom:112px; }
"""
