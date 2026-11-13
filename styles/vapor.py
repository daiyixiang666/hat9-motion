"""vapor · 蒸汽波桌面 —— a late-90s desktop floating in a vaporwave dusk. Every figure arrives inside a grey system dialog.

Behind the windows, one continuous set that never stops (a single clip for the whole film, driven per frame): sky
#1a0b3b → #5a1e8c → #ff5fa2 down to the horizon at 46 % of the frame; below it a #12062b floor with a magenta perspective
grid (#ff4fd8 at 70 %, 2 px, 14 columns, rows on an exponential spacing scrolling toward the viewer one row per 0.6 s);
a 560 px striped sun centred on the horizon (#ffe66d → #ff7a59 → #ff3d9a, 7 dark bands that thicken toward the bottom
and drift down one band per 2 s); a cyan wireframe icosahedron turning 20°/s beside it.

Windows are drawn generically: face #c3c7cb, 2 px white bevel top/left, #7d8288 + #1b1b1b bevels bottom/right, a
#1f2a8a → #6fa8ff title bar (grey when inactive) with a white 30 px bold title and three square caption buttons drawn as
plain shapes; sunken white fields with the inverse bevel; data colours magenta #ff3d9a, cyan #19d3e6, yellow #ffe66d.
Numerals in VT323, window labels in Fusion Pixel 12 (24 / 36 px), title bars and the subtitle in Noto Sans SC bold.

Charts are the desktop's own objects: dialog (hero number in a sunken field) · error (cascading error boxes, the last one
carries the figure) · wizard (setup wizard = timeline) · progress (segmented progress bars = comparison) · explorer
(details-view file list = ranking) · paint (a paint program floods a 10×10 grid = share) · shutdown (summary dialog, the
screen dims in a dither). A drawn white arrow cursor moves on eased paths and clicks to cause every state change.

Seams: into beats 1, 3, 5, 7 a 5-frame scanline glitch (rows shifted ±24 px with an RGB split), caused by the cursor's
last click; into beats 2, 4, 6 the old window is dragged off with 4 ghost outlines (10 frames) and the new one opens from
a desktop icon with the classic 6-outline zoom (6 frames).

9:16: menu bar y 200–256 (film title left, beat clock right) · main window x 90–990 from y 320–380 · tooltip subtitle
y 1380–1456 · source strip y 1470–1506 · below y 1520 the grid floor with desktop icons. 16:9: sun centred, main window
left-centre 1040 px wide, secondary window right, taskbar y 1010–1070 holding the title, the subtitle and the clock.
No host. Every beat writes "src"; scene fields are listed in each scene's docstring.
"""
import math

FACE, HI, SH, DK, WHITE, INK = "#c3c7cb", "#ffffff", "#7d8288", "#1b1b1b", "#ffffff", "#111111"
NAVY, LBLUE = "#1f2a8a", "#6fa8ff"
MAG, CYAN, YEL = "#ff3d9a", "#19d3e6", "#ffe66d"
SKY0, SKY1, SKY2, FLOOR, GRID = "#1a0b3b", "#5a1e8c", "#ff5fa2", "#12062b", "#ff4fd8"
TIP = "#ffffe1"
F = 1 / 30

RAISED = f"inset -2px -2px 0 {DK}, inset 2px 2px 0 {HI}, inset -4px -4px 0 {SH}, inset 4px 4px 0 #dfe2e5"
PRESSED = f"inset 2px 2px 0 {DK}, inset -2px -2px 0 {HI}, inset 4px 4px 0 {SH}, inset -4px -4px 0 #dfe2e5"
SUNKEN = f"inset 2px 2px 0 {SH}, inset -2px -2px 0 {HI}, inset 4px 4px 0 {DK}, inset -4px -4px 0 #dfe2e5"

STYLE = {
    "name": "蒸汽波桌面", "en": "Vapor Desktop", "benchmarks": ["90 年代桌面系统对话框", "Vaporwave 霓虹日落网格", "像素位图界面"],
    "tokens": {
        "bg": SKY0, "fg": WHITE, "muted": "#d9c8ff", "accent": MAG, "accent2": CYAN, "alert": "#d10000",
        "line": "rgba(255,255,255,.3)", "paper": FACE, "ink": INK, "card": FACE, "card-fg": INK,
        "face": FACE, "navy": NAVY, "mag": MAG, "cyan": CYAN, "yel": YEL, "tip": TIP,
        # subtitle: a tooltip plate (pale yellow, 2 px black border, 6 px hard black shadow, black bold sans)
        "cap-bg": TIP, "cap-fg": INK, "cap-size": "42px", "cap-weight": "700", "cap-pad": "11px 26px 11px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "464px", "cap-em": "#b0005e",
        "punch-top": "66%", "punch-size": "72px",
    },
    "fonts": {"display": "noto-sans-sc", "body": "noto-sans-sc", "cap": "noto-sans-sc", "num": "vt323", "mono": "vt323",
              "pixel": "fusion-pixel", "latin": "vt323"},
    "motion": {"ease": "power2.out", "dur": 0.3, "stagger": 0.066, "cut": "hard", "transition": "hard", "em": "static", "camera": "none"},
    "layers": [],
    "caption_plate": False,
    "mascot": {"mode": "none"},
    "outro": {"move": False},
    "safe_exempt": [".vp-ico", ".vp-deco"],      # desktop icons and their labels are furniture, not text to read
    "sfx": {"transition": ("glitch", 0.35), "enter": ("pop", 0.3), "pop": ("pop", 0.35), "hit": ("beep", 0.35), "slam": ("hit", 0.35),
            "count": ("type", 0.22), "click": ("click", 0.32), "mascot": None, "line": ("tick", 0.25), "tear": ("whoosh_soft", 0.3),
            "glitch": ("glitch", 0.35), "error": ("beep", 0.4), "drag": ("whoosh_soft", 0.3), "open": ("whoosh_soft", 0.25)},
}


# ---------------------------------------------------------------- layout per aspect
def L(X):
    """fixed architecture per aspect. main = (x, top, width, height): every main window ends at y 1290 (9:16) / 960 (16:9)."""
    if X.portrait:
        return {"hz": 883, "sun": (880, 883), "wire": (130, 120, 80), "main": (90, 330, 900, 960), "menu": True,
                "src": (120, 1470, 840), "icons": [(96, 1600, "folder", "年报"), (276, 1600, "sheet", "表格"), (456, 1600, "disk", "A:")]}
    return {"hz": 497, "sun": (1500, 497), "wire": (1290, 150, 80), "main": (60, 60, 1120, 900), "menu": False,
            "src": (60, 966, 1120), "icons": [(1790, 120, "folder", "年报"), (1790, 290, "sheet", "表格"), (1790, 460, "disk", "A:")]}


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


# ---------------------------------------------------------------- css
CSS = r"""
.st-vapor .mascot { display:none !important; }
.vp { position:absolute; inset:0; overflow:hidden; color:#111; font-family:var(--f-pixel); }
.vp * { box-sizing:border-box; }
.vp .vw { position:absolute; background:#c3c7cb; padding:6px; box-shadow:__RAISED__, 10px 12px 0 rgba(18,6,43,.55); }
.vp .vw.hid { visibility:hidden; }
.vp .tb { position:absolute; left:6px; right:6px; top:6px; height:50px; background:linear-gradient(90deg, #1f2a8a 0%, #1f2a8a 30%, #6fa8ff 100%); display:flex; align-items:center;
  padding:0 8px 0 14px; color:#fff; font-family:var(--f-display); font-weight:700; font-size:30px; white-space:nowrap; overflow:hidden; }
.vp .vw.ina .tb { background:#6e7378; color:#fff; }
.vp .tb .tt { flex:1; overflow:hidden; text-overflow:clip; letter-spacing:.01em; }
.vp .tb .cbs { display:flex; gap:4px; margin-left:12px; }
.vp .cb { position:relative; width:40px; height:34px; background:#c3c7cb; box-shadow:__RAISED__; display:block; }
.vp .cb.mn::after { content:""; position:absolute; left:11px; right:13px; bottom:9px; height:4px; background:#111; }
.vp .cb.mx::after { content:""; position:absolute; left:10px; right:12px; top:7px; bottom:9px; border:2px solid #111; border-top-width:5px; }
.vp .cb.cl { margin-left:4px; }
.vp .cb.cl::before, .vp .cb.cl::after { content:""; position:absolute; left:18px; top:6px; width:4px; height:20px; background:#111; transform:rotate(45deg); }
.vp .cb.cl::after { transform:rotate(-45deg); }
.vp .bd { position:absolute; left:6px; right:6px; top:62px; bottom:6px; }
.vp .sk { position:absolute; background:#fff; box-shadow:__SUNKEN__; overflow:hidden; }
.vp .sk.gr { background:#c3c7cb; }
.vp .btn { position:absolute; height:58px; background:#c3c7cb; box-shadow:__RAISED__; display:flex; align-items:center; justify-content:center;
  font-family:var(--f-pixel); font-size:28px; color:#111; white-space:nowrap; }
.vp .btn.def { outline:2px solid #111; outline-offset:0; }
.vp .btn .fr { position:absolute; left:10px; top:9px; width:calc(100% - 20px); height:calc(100% - 18px); overflow:visible; pointer-events:none; }
.vp .lb { position:absolute; font-family:var(--f-pixel); color:#111; white-space:nowrap; line-height:1.2; }
.vp .num { position:absolute; font-family:var(--f-num); color:#111; white-space:nowrap; line-height:1; }
.vp .hr { position:absolute; height:4px; box-shadow:inset 0 2px 0 #7d8288, inset 0 -2px 0 #fff; }
.vp .ol { position:absolute; border:3px dotted #fff; outline:1px solid rgba(18,6,43,.6); visibility:hidden; pointer-events:none; }
.vp .gh { position:absolute; border:3px dotted rgba(255,255,255,.9); visibility:hidden; pointer-events:none; }
.vp .cur { position:absolute; left:0; top:0; width:30px; height:46px; z-index:90; transform-origin:0 0; filter:drop-shadow(3px 3px 0 rgba(18,6,43,.45)); }
.vp .caret { display:inline-block; width:.36em; height:.56em; background:#111; vertical-align:baseline; margin-left:.04em; }
.vp .blk { position:absolute; top:6px; width:18px; height:26px; }
.vp .radio { position:absolute; width:30px; height:30px; border-radius:50%; background:#fff;
  box-shadow:inset 2px 2px 0 #7d8288, inset -2px -2px 0 #fff, inset 4px 4px 0 #1b1b1b, inset -4px -4px 0 #dfe2e5; }
.vp .radio i { position:absolute; left:10px; top:10px; width:10px; height:10px; border-radius:50%; background:#111; visibility:hidden; }
/* furniture */
.vp .menu { position:absolute; left:60px; top:200px; width:960px; height:56px; background:#c3c7cb; box-shadow:__RAISED__; display:flex; align-items:center;
  padding:0 12px 0 14px; font-family:var(--f-pixel); font-size:28px; color:#111; z-index:75; }
.vp .menu .ttl { flex:1; display:flex; align-items:center; gap:14px; white-space:nowrap; }
.vp .menu .clk, .vp .task .clk { height:40px; padding:0 14px; display:flex; align-items:center; box-shadow:inset 2px 2px 0 #7d8288, inset -2px -2px 0 #fff;
  font-family:var(--f-num); font-size:36px; color:#111; white-space:nowrap; }
.vp .task { position:absolute; left:0; right:0; top:1010px; height:60px; background:#c3c7cb; box-shadow:inset 0 2px 0 #fff, inset 0 4px 0 #dfe2e5; z-index:75; }
.vp .task .start { position:absolute; left:10px; top:6px; height:48px; padding:0 18px 0 12px; display:flex; align-items:center; gap:12px; box-shadow:__RAISED__;
  font-family:var(--f-pixel); font-size:28px; color:#111; white-space:nowrap; }
.vp .task .clk { position:absolute; right:12px; top:10px; }
.vp .src { position:absolute; height:36px; padding:0 14px; display:flex; align-items:center; background:rgba(0,0,0,.65); color:#fff;
  font-family:var(--f-body); font-size:24px; white-space:nowrap; z-index:75; overflow:hidden; }
.vp .vp-ico { position:absolute; width:120px; text-align:center; z-index:5; }
.vp .vp-ico svg { display:block; margin:0 auto; }
.vp .vp-ico span { display:inline-block; margin-top:6px; padding:1px 8px; font-family:var(--f-pixel); font-size:24px; color:#fff; background:rgba(18,6,43,.0); }
.vp .vp-ico.sel span { background:#1f2a8a; outline:2px dotted #fff; }
.vp .vp-ico .hl { position:absolute; left:22px; top:0; width:76px; height:76px; background:rgba(31,42,138,.55); visibility:hidden; }
/* error glyph */
.vp .eg { position:absolute; }
/* the dither dim of the shutdown */
.vp .dim { position:absolute; left:0; right:0; top:0; height:0; z-index:70;
  background-image:conic-gradient(rgba(0,0,0,.78) 25%, transparent 0 50%, rgba(0,0,0,.78) 0 75%, transparent 0); background-size:4px 4px; }
"""

BG_CSS = r"""
.vp-bg { position:absolute; inset:0; overflow:hidden; background:#1a0b3b; }
.vp-bg svg { position:absolute; left:0; top:0; overflow:visible; }
.vp-bg .scan { position:absolute; inset:0; background:repeating-linear-gradient(0deg, rgba(10,0,30,.10) 0 2px, transparent 2px 4px); pointer-events:none; }
"""


# ---------------------------------------------------------------- the continuous set (one clip, per-frame engine)
ENGINE = r"""
(()=>{
const W=__W__, H=__H__, HZ=__HZ__, SX=__SX__, SR=280, WX=__WX__, WY=__WY__, WR=__WR__;
const rows=[...document.querySelectorAll('#vpbg .gr')];
const bands=[...document.querySelectorAll('#vpbg .sb')];
const ico=document.querySelector('#vpbg .ico');
const Q=0.66, NB=7;
const phi=(1+Math.sqrt(5))/2;
const V=[[-1,phi,0],[1,phi,0],[-1,-phi,0],[1,-phi,0],[0,-1,phi],[0,1,phi],[0,-1,-phi],[0,1,-phi],[phi,0,-1],[phi,0,1],[-phi,0,-1],[-phi,0,1]];
const E=[]; for(let a=0;a<12;a++) for(let b=a+1;b<12;b++){ const d=Math.hypot(V[a][0]-V[b][0],V[a][1]-V[b][1],V[a][2]-V[b][2]); if(Math.abs(d-2)<1e-6) E.push([a,b]); }
function frame(tt){
  // grid rows: y = HZ + (H-HZ) * Q^(k - phase), one row per 0.6 s toward the viewer
  const ph=(tt/0.6)%1;
  rows.forEach((el,k)=>{ const y=HZ+(H-HZ)*Math.pow(Q,k-ph); el.setAttribute('y1',y.toFixed(1)); el.setAttribute('y2',y.toFixed(1));
    el.setAttribute('stroke-opacity',(0.7*Math.min(1,(y-HZ)/40)).toFixed(3)); });
  // sun bands: 7 dark bands in the visible half, thicker toward the horizon, drifting down one band per 2 s
  const bp=(tt/2)%1;
  bands.forEach((el,j)=>{ const u=(j+bp)/NB; const y=HZ-SR*0.92+SR*0.92*u; const h=2+20*Math.pow(u,1.35);
    el.setAttribute('y',(y-h/2).toFixed(1)); el.setAttribute('height',Math.max(0,Math.min(h, HZ-(y-h/2))).toFixed(1)); });
  // wireframe icosahedron, 20 deg/s about its vertical axis, tilted 18 deg
  const a=tt*20*Math.PI/180, c=Math.cos(a), s=Math.sin(a), ct=Math.cos(0.31), st=Math.sin(0.31);
  const P=V.map(v=>{ const x=v[0]*c+v[2]*s, z=-v[0]*s+v[2]*c; const y=v[1]*ct-z*st, z2=v[1]*st+z*ct; const k=WR/phi/(1+z2*0.12); return [WX+x*k, WY-y*k]; });
  let d=''; E.forEach(e=>{ d+='M'+P[e[0]][0].toFixed(1)+' '+P[e[0]][1].toFixed(1)+'L'+P[e[1]][0].toFixed(1)+' '+P[e[1]][1].toFixed(1); });
  ico.setAttribute('d',d);
}
tl.to({}, {duration:__D__, ease:"none", onUpdate:function(){ frame(this.time()); }, onStart:function(){ frame(this.time()); }}, 0);
frame(0);
})();
"""


def _glitch_filters(W, H, rnd):
    """5 SVG filters: rows of random height shifted ±24 px (displacement by a band image) with an RGB split."""
    from urllib.parse import quote
    out = ""
    for k in range(5):
        y, rects = 0, ""
        while y < H:
            h = rnd.choice([18, 24, 36, 48, 72, 110, 160])
            r = 128 if rnd.random() < 0.35 else rnd.choice([64, 80, 96, 160, 176, 192])
            rects += f"<rect x='0' y='{y}' width='{W}' height='{h}' fill='rgb({r},128,0)'/>"
            y += h
        img = "data:image/svg+xml," + quote(f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}'>{rects}</svg>", safe="")
        sp = 8 + 3 * k % 6
        out += (f'<filter id="vgl{k}" x="0" y="0" width="{W}" height="{H}" filterUnits="userSpaceOnUse" primitiveUnits="userSpaceOnUse" color-interpolation-filters="sRGB">'
                f'<feImage href="{img}" x="0" y="0" width="{W}" height="{H}" preserveAspectRatio="none" result="m"/>'
                f'<feDisplacementMap in="SourceGraphic" in2="m" scale="96" xChannelSelector="R" yChannelSelector="G" result="d"/>'
                f'<feOffset in="d" dx="{sp}" result="dr"/><feColorMatrix in="dr" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r"/>'
                f'<feColorMatrix in="d" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g"/>'
                f'<feOffset in="d" dx="{-sp}" result="db"/><feColorMatrix in="db" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b"/>'
                f'<feComposite in="r" in2="g" operator="arithmetic" k2="1" k3="1" result="rg"/>'
                f'<feComposite in="rg" in2="b" operator="arithmetic" k2="1" k3="1"/></filter>')
    return out


def backdrop(X):
    """the sky, sun, wireframe and grid floor: one clip for the whole film, so the set never stops at a cut."""
    if getattr(X, "_vp_bg", False): return
    X._vp_bg = True
    X.css("vapor-bg", BG_CSS)
    W, H = X.W, X.H
    l = L(X)
    hz = l["hz"]
    sx, sy = l["sun"]
    wx, wy, wr = l["wire"]
    D = X.duration or 60
    # perspective columns: 15 lines (14 columns) from the vanishing point, spread past both edges at the bottom
    cols = ""
    n = 14
    spread = W * (2.6 if X.portrait else 1.9)
    for k in range(n + 1):
        xb = W / 2 + (k - n / 2) * spread / n
        cols += f'<line x1="{W / 2:.1f}" y1="{hz}" x2="{xb:.1f}" y2="{H + 40}"/>'
    rows = "".join(f'<line class="gr" x1="-10" x2="{W + 10}" y1="{hz}" y2="{hz}"/>' for _ in range(18))
    bands = "".join(f'<rect class="sb" x="{sx - 300}" width="600" y="0" height="0" fill="#000"/>' for _ in range(8))
    sky = (f'<linearGradient id="vpsky" x1="0" y1="0" x2="0" y2="{hz}" gradientUnits="userSpaceOnUse">'
           f'<stop offset="0" stop-color="{SKY0}"/><stop offset=".55" stop-color="{SKY1}"/><stop offset="1" stop-color="{SKY2}"/></linearGradient>'
           f'<linearGradient id="vpsun" x1="0" y1="{sy - 280}" x2="0" y2="{sy + 280}" gradientUnits="userSpaceOnUse">'
           f'<stop offset="0" stop-color="{YEL}"/><stop offset=".45" stop-color="#ff7a59"/><stop offset=".8" stop-color="{MAG}"/></linearGradient>'
           f'<radialGradient id="vpglow" cx="{sx}" cy="{hz}" r="{W * 0.75:.0f}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ff5fa2" stop-opacity=".55"/>'
           f'<stop offset="1" stop-color="#ff5fa2" stop-opacity="0"/></radialGradient>'
           f'<mask id="vpsm" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#fff"/><g>{bands}</g></mask>')
    # tiny stars in the upper sky (seeded), the sun, the horizon glow
    stars = "".join(f'<rect x="{X.rand.uniform(0, W):.0f}" y="{X.rand.uniform(0, hz * 0.55):.0f}" width="3" height="3" fill="#fff" opacity="{X.rand.uniform(.25, .7):.2f}"/>' for _ in range(28))
    svg = (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>{sky}{_glitch_filters(W, H, X.rand)}</defs>'
           f'<rect width="{W}" height="{hz}" fill="url(#vpsky)"/>{stars}'
           f'<rect width="{W}" height="{hz}" fill="url(#vpglow)"/>'
           f'<circle cx="{sx}" cy="{sy}" r="280" fill="url(#vpsun)" mask="url(#vpsm)"/>'
           f'<path class="ico" d="" fill="none" stroke="{CYAN}" stroke-width="2.6" stroke-linejoin="round"/>'
           f'<rect y="{hz}" width="{W}" height="{H - hz}" fill="{FLOOR}"/>'
           f'<g stroke="{GRID}" stroke-width="2" stroke-opacity=".7">{cols}</g>'
           f'<g stroke="{GRID}" stroke-width="2">{rows}</g>'
           f'<rect y="{hz - 1}" width="{W}" height="3" fill="#ff9ad0"/></svg>')
    X.clip("vpbg", 0, D, f'<div class="vp-bg">{svg}<div class="scan"></div></div>', "vpbgc", 1, track=5)
    X.tw(ENGINE.replace("__W__", str(W)).replace("__H__", str(H)).replace("__HZ__", str(hz)).replace("__SX__", str(sx))
         .replace("__WX__", str(wx)).replace("__WY__", str(wy)).replace("__WR__", str(wr)).replace("__D__", f"{D:.3f}"))


# ---------------------------------------------------------------- drawing vocabulary
CURSOR = ('<svg class="cur" viewBox="0 0 15 23" width="30" height="46" shape-rendering="crispEdges">'
          '<path d="M0 0 V19 L4 15 L7 22 L10 21 L7 14 H13 Z" fill="#fff" stroke="#111" stroke-width="1.2" stroke-linejoin="miter"/></svg>')


def window(cls, x, y, w, h, title, body, state="act", extra=""):
    st = "" if state == "act" else " ina"
    return (f'<div class="vw {cls}{st}" data-layout-allow-overlap style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px;{extra}">'
            f'<div class="tb"><span class="tt">{title}</span><span class="cbs"><i class="cb mn"></i><i class="cb mx"></i><i class="cb cl"></i></span></div>'
            f'<div class="bd">{body}</div></div>')


def button(cls, x, y, w, label, default=False, h=58):
    fr = ('<svg class="fr"><rect width="100%" height="100%" fill="none" stroke="#111" stroke-width="2" stroke-dasharray="2 2"/></svg>' if default else "")
    return f'<div class="btn {cls}{" def" if default else ""}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h}px">{fr}{label}</div>'


def icon_svg(kind, s=76):
    if kind == "folder":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 19 19" shape-rendering="crispEdges"><path d="M1 4h6l2 2h9v11H1z" fill="#ffe66d" stroke="#111" stroke-width="1"/>'
                '<path d="M1 7h17" stroke="#c99a1a" stroke-width="1"/></svg>')
    if kind == "sheet":
        return (f'<svg width="{s}" height="{s}" viewBox="0 0 19 19" shape-rendering="crispEdges"><path d="M4 1h8l4 4v13H4z" fill="#fff" stroke="#111" stroke-width="1"/>'
                '<path d="M6 8h8M6 10h8M6 12h8M6 14h6" stroke="#19d3e6" stroke-width="1"/><path d="M12 1v4h4" fill="none" stroke="#111"/></svg>')
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 19 19" shape-rendering="crispEdges"><path d="M2 2h14l1 1v14H2z" fill="#1f2a8a" stroke="#111" stroke-width="1"/>'
            '<path d="M5 2h8v6H5z" fill="#c3c7cb"/><path d="M10 3h2v4h-2z" fill="#1f2a8a"/><path d="M4 11h11v6H4z" fill="#fff"/></svg>')


def error_glyph(s=96):
    return (f'<svg class="eg" width="{s}" height="{s}" viewBox="0 0 32 32" shape-rendering="crispEdges"><circle cx="16" cy="16" r="14" fill="#d10000" stroke="#111" stroke-width="1.4"/>'
            '<path d="M10 10L22 22M22 10L10 22" stroke="#fff" stroke-width="3.6" stroke-linecap="square"/></svg>')


def info_glyph(s=80):
    return (f'<svg class="eg" width="{s}" height="{s}" viewBox="0 0 32 32" shape-rendering="crispEdges"><circle cx="16" cy="16" r="14" fill="#fff" stroke="#111" stroke-width="1.4"/>'
            '<rect x="14" y="13" width="4" height="11" fill="#1f2a8a"/><rect x="14" y="7" width="4" height="4" fill="#1f2a8a"/></svg>')


def four_squares(s=30):
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 10 10" shape-rendering="crispEdges"><rect x="0" y="0" width="4" height="4" fill="#ff3d9a"/>'
            '<rect x="5" y="0" width="4" height="4" fill="#19d3e6"/><rect x="0" y="5" width="4" height="4" fill="#1f2a8a"/><rect x="5" y="5" width="4" height="4" fill="#ffe66d"/></svg>')


def tool_glyph(kind):
    g = {"pencil": '<path d="M3 13l8-8 2 2-8 8H3z" fill="#ffe66d" stroke="#111"/>',
         "bucket": '<path d="M3 8l5-5 5 5-5 5z" fill="#c3c7cb" stroke="#111"/><path d="M12 9c1 2 2 3 1 4" stroke="#ff3d9a" stroke-width="2" fill="none"/>',
         "brush": '<path d="M10 2l3 3-5 5-3-3z" fill="#19d3e6" stroke="#111"/><path d="M4 9l3 3-3 2-2-2z" fill="#111"/>',
         "text": '<path d="M3 13L8 2l5 11M5 9h6" stroke="#111" stroke-width="1.6" fill="none"/>',
         "erase": '<path d="M2 10l6-6 6 6-3 3H5z" fill="#ff9ad0" stroke="#111"/>',
         "select": '<rect x="2" y="2" width="12" height="12" fill="none" stroke="#111" stroke-dasharray="2 1.5"/>'}[kind]
    return f'<svg width="44" height="44" viewBox="0 0 16 16" shape-rendering="crispEdges">{g}</svg>'


class Cur:
    """the drawn arrow cursor of one beat: it moves on eased paths and clicks to cause every change."""
    def __init__(self, X, x, y):
        self.X, self.x, self.y = X, x, y
        self.html = CURSOR
        self.s = None

    def bind(self, s):
        self.s = f"{s} .cur"

    def to(self, x, y, t, dur=None, ease="power2.inOut"):
        dist = math.hypot(x - self.x, y - self.y)
        dur = dur if dur is not None else min(0.6, 0.22 + 0.35 * math.sqrt(dist / 1920))
        self.X.tw(f'tl.to("{self.s}", {{x:{x:.0f}, y:{y:.0f}, duration:{dur:.3f}, ease:"{ease}"}}, {t:.3f});')
        self.x, self.y = x, y
        return t + dur

    def click(self, t, sfx=True):
        self.X.tw(f'tl.set("{self.s}", {{scale:0.85}}, {t:.3f}); tl.set("{self.s}", {{scale:1}}, {t + 2 * F:.3f});')
        if sfx: self.X.sfx(t, "click")

    def start(self, t):
        self.X.tw(f'tl.set("{self.s}", {{x:{self.x:.0f}, y:{self.y:.0f}, scale:1}}, {t:.3f});')


def press(X, sel, t, frames=3):
    """a button press: the bevel inverts for 3 frames and the label shifts 2 px."""
    X.tw(f'tl.set("{sel}", {{boxShadow:"{PRESSED}", backgroundColor:"#b8bcc1"}}, {t:.3f});')
    X.tw(f'tl.set("{sel}", {{boxShadow:"{RAISED}", backgroundColor:"#c3c7cb"}}, {t + frames * F:.3f});')


def outlines(rect_from, rect_to, n=6):
    """the 6 outline rectangles of the window zoom (eased from the icon box to the window rect)."""
    fx, fy, fw, fh = rect_from
    tx, ty, tw_, th = rect_to
    out = ""
    for k in range(1, n + 1):
        e = 1 - (1 - k / n) ** 2
        out += (f'<div class="ol ol{k}" style="left:{fx + (tx - fx) * e:.0f}px;top:{fy + (ty - fy) * e:.0f}px;'
                f'width:{fw + (tw_ - fw) * e:.0f}px;height:{fh + (th - fh) * e:.0f}px"></div>')
    return out


def zoom_open(X, s, win_sel, t, n=6):
    """outline k shows on frames k-1..k (a short trail), then the window appears on frame 6."""
    for k in range(1, n + 1):
        X.tw(f'tl.set("{s} .ol{k}", {{visibility:"visible"}}, {t + (k - 1) * F:.3f}); tl.set("{s} .ol{k}", {{visibility:"hidden"}}, {t + (k + 1) * F:.3f});')
    X.tw(f'tl.set("{s} {win_sel}", {{visibility:"visible"}}, {t + n * F:.3f});')
    X.sfx(t, "open")
    return t + n * F


def ghosts(rect, n=4):
    x, y, w, h = rect
    return "".join(f'<div class="gh gh{k}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px"></div>' for k in range(n))


def drag_off(X, s, cur, sel, rect, t_end, dx=None, dy=None):
    """grab the title bar, then the window slides off along a path in 10 frames with 4 ghost outlines trailing it."""
    x, y, w, h = rect
    dx = dx if dx is not None else -(x + w + 80)
    dy = dy if dy is not None else 360
    t_drag = t_end - 10 * F
    gx, gy = x + min(260, w * 0.3), y + 32
    cur.to(gx, gy, t_drag - 0.42, 0.3)
    X.tw(f'tl.set("{cur.s}", {{scale:0.85}}, {t_drag - 0.08:.3f});')
    X.sfx(t_drag - 0.08, "click")
    X.tw(f'tl.to("{sel}, {cur.s}", {{x:"+={dx:.0f}", y:"+={dy:.0f}", duration:{10 * F:.3f}, ease:"power2.in"}}, {t_drag:.3f});')
    for k in range(4):
        X.tw(f'tl.set("{s} .gh{k}", {{visibility:"visible"}}, {t_drag + (k + 1) * F:.3f});')
        X.tw(f'tl.to("{s} .gh{k}", {{x:{dx:.0f}, y:{dy:.0f}, duration:{10 * F:.3f}, ease:"power2.in"}}, {t_drag + (k + 1) * 2 * F:.3f});')
    X.sfx(t_drag, "drag")


def glitch(X, t, out_cid, in_cid):
    """5-frame scanline glitch on the whole frame: 2 frames of the old beat, 3 of the new."""
    for f in range(-2, 3):
        tgt = f"#vpbg, #{out_cid} .stage" if f < 0 else f"#vpbg, #{in_cid} .stage"
        k = f + 2
        X.tw(f'tl.set("{tgt}", {{filter:"url(#vgl{k})"}}, {t + f * F:.3f}); tl.set("{tgt}", {{filter:"none"}}, {t + (f + 1) * F:.3f});')
    X.sfx(t - 2 * F, "glitch")


def type_digits(X, sel, text, t, every=3):
    """digits type into a field one by one behind a block caret (the caret leaves when the figure is complete)."""
    for k in range(len(text) + 1):
        X.tw(f'tl.set("{sel} .tx", {{textContent:"{text[:k]}"}}, {t + k * every * F:.3f});')
    X.tw(f'tl.set("{sel} .caret", {{visibility:"hidden"}}, {t + (len(text) * every + 3) * F:.3f});')
    X.sfx(t, "count")
    return t + len(text) * every * F


# ---------------------------------------------------------------- the page shared by every beat
def page(X, b, cid, t, d, inner, cur, open_win=None, open_from=0, drag=None, end_click=None, end_at=None):
    """one beat on the desktop: icons, the beat's windows, menu bar (9:16) or taskbar (16:9), the source strip, the cursor.
    open_win = (selector, rect): the window zoom-opens from desktop icon `open_from` (beats 0, 2, 4, 6);
    beats 1, 3, 5, 7 are revealed by the glitch the previous beat's last click causes.
    drag = (selector, rect): the window is dragged off at the end (beats 1, 3, 5).
    end_click = (cursor x, y, button selector): the last click that sets off the glitch into the next beat."""
    X.css("vapor", CSS.replace("__RAISED__", RAISED).replace("__SUNKEN__", SUNKEN))
    backdrop(X)
    W, H, P = X.W, X.H, X.portrait
    l = L(X)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    title = meta.get("title", "")
    src = b.get("src", "")
    clock = b.get("clock") or f"{i + 1:02d}/{n:02d}"
    X.used_text.update(title + src + clock + "0123456789/")
    icons = ""
    for k, (ix, iy, kind, lab) in enumerate(l["icons"]):
        X.used_text.update(lab)
        icons += (f'<div class="vp-ico ic{k}" data-safe="ignore" style="left:{ix}px;top:{iy}px"><i class="hl"></i>{icon_svg(kind)}'
                  f'<span>{X.rich(lab)}</span></div>')
    if P:
        furn = (f'<div class="menu"><div class="ttl">{four_squares()}<span>{X.rich(title)}</span></div><div class="clk">{X.rich(clock)}</div></div>')
    else:
        furn = (f'<div class="task"><div class="start">{four_squares(26)}<span>{X.rich(title)}</span></div><div class="clk">{X.rich(clock)}</div></div>')
    sx, sy, sw = l["src"]
    if src:
        furn += f'<div class="src" style="left:{sx}px;top:{sy}px;max-width:{sw}px">来源：{X.rich(src)}</div>'
        X.used_text.update("来源：")
    ol = ""
    if open_win:
        ix, iy = l["icons"][open_from][:2]
        ol = outlines((ix + 22, iy, 76, 76), open_win[1])
    gh = ghosts(drag[1]) if drag else ""
    html = f'<div class="vp">{icons}{inner}{ol}{gh}{furn}{cur.html}</div>'
    X.clip(cid, t, d, html, "scene", 10 + i, track=1 + i % 2)
    s = f"#{cid}"
    cur.bind(s)
    cur.start(t)
    prev = getattr(X, "_vp_prev", None)
    if i > 0 and i % 2 == 1 and prev:
        glitch(X, t, prev, cid)
    X._vp_prev = cid
    t_open = t
    if open_win:      # the cursor double-clicks the desktop icon, the icon highlights, the window zooms open from it
        ix, iy = l["icons"][open_from][:2]
        cx, cy = ix + 64, iy + 44
        X.tw(f'tl.set("{cur.s}", {{x:{cx}, y:{cy}}}, {t:.3f});')
        cur.x, cur.y = cx, cy
        cur.click(t + 0.03, sfx=False)
        cur.click(t + 0.1)
        X.tw(f'tl.set("{s} .ic{open_from}", {{attr:{{class:"vp-ico ic{open_from} sel"}}}}, {t + 0.03:.3f}); tl.set("{s} .ic{open_from} .hl", {{visibility:"visible"}}, {t + 0.03:.3f});')
        X.tw(f'tl.set("{s} .ic{open_from}", {{attr:{{class:"vp-ico ic{open_from}"}}}}, {t + 0.5:.3f}); tl.set("{s} .ic{open_from} .hl", {{visibility:"hidden"}}, {t + 0.5:.3f});')
        t_open = zoom_open(X, s, open_win[0], t + 0.12)
    if drag:
        drag_off(X, s, cur, f"{s} {drag[0]}", drag[1], t + d)
    if end_click:
        ex, ey, bsel = end_click
        tc = end_at if end_at is not None else t + d - 0.2
        cur.to(ex, ey, tc - 0.45, 0.4)
        cur.click(tc)
        press(X, f"{s} {bsel}", tc)
    return s, t_open


def field_num(X, cls, x, y, w, h, px, unit="", upx=48, pad=34, text="", unit_top=False, color=""):
    """a sunken white field holding a VT323 numeral (typed in later via .tx, behind a block caret); its unit is pinned to
    the field's bottom-right (or top-right) corner, so the figure never shifts while it types."""
    X.used_text.update(unit + "0123456789.,%+-−")
    base = (h - px * 0.56) / 2 + (upx * 0.35 if unit and unit_top else 0)      # VT323 digits are 0.56 em tall
    if unit and unit_top:
        u = f'<span class="lb" style="right:{pad}px;top:14px;font-size:{upx}px;line-height:1">{X.rich(unit)}</span>'
    elif unit:
        u = f'<span class="lb" style="right:{pad}px;bottom:{(h - px * 0.56) / 2:.0f}px;font-size:{upx}px;line-height:1">{X.rich(unit)}</span>'
    else:
        u = ""
    col = f";color:{color}" if color else ""
    return (f'<div class="sk {cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
            f'<span class="num" style="left:{pad}px;top:{base - px * 0.24:.0f}px;font-size:{px}px;line-height:1{col}"><span class="tx">{X.rich(text)}</span><i class="caret"></i></span>{u}</div>')


def num_px(text, avail, cap):
    """the VT323 size whose advance (0.4 em a glyph) fills avail px, capped."""
    return int(min(cap, avail / (0.4 * max(1, len(str(text))))))


def small_field(X, cls, x, y, w, h, label, value, unit, cap=150):
    """a smaller sunken field: a 32 px label over a VT323 figure and its unit (the previous year, a comparison)."""
    X.used_text.update(label + str(value) + unit)
    upx = 32
    px = int(min(cap, (w - 40 - (len(unit) * upx + 14 if unit else 0)) / (0.4 * max(1, len(str(value))))))
    it = 58
    return (f'<div class="sk {cls}" style="left:{x:.0f}px;top:{y:.0f}px;width:{w:.0f}px;height:{h:.0f}px">'
            f'<span class="lb" style="left:20px;top:12px;font-size:{upx}px">{X.rich(label)}</span>'
            f'<span class="num" style="left:20px;top:{it + (h - it - px * 0.56) / 2 - px * 0.24:.0f}px;font-size:{px}px"><span class="tx">{X.rich(str(value))}</span>'
            f'<span class="lb" style="position:static;font-size:{upx}px;margin-left:12px">{X.rich(unit)}</span></span></div>')


# ---------------------------------------------------------------- scenes
def dialog(b, X, t, d, cid):
    """hero number in a system dialog. Fields: title, label, sub, big (digits), unit, old {label, value, unit},
    side {title, label, value, note} (optional secondary window), icon, at_big."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    bw, bh = mw - 12, mh - 68
    big, unit = str(b.get("big", "")), b.get("unit", "")
    lab, sub = b.get("label", ""), b.get("sub", "")
    old = b.get("old") or {}
    side = b.get("side")
    X.used_text.update(lab + sub + "确定详细信息 >>")
    fw, fh, pad = bw - 60, 360, 14
    px = num_px(big, fw - 2 * pad - 8, 400 if P else 420)
    srect = None
    if side:
        if P:
            srect = (470, my + 62 + 520, 520, my + mh - 30 - (my + 62 + 520))
        else:
            srect = (mx + mw - 80, my + 500, 560, 380)
    ow = (srect[0] - mx - 6 - 30 - 30) if (side and P) else fw
    oy = 136 + fh + 24
    body = (f'<div style="position:absolute;left:30px;top:24px">{info_glyph(84)}</div>'
            f'<div class="lb" style="left:136px;top:22px;font-size:36px">{X.rich(lab)}</div>'
            f'<div class="lb" style="left:136px;top:74px;font-size:28px;color:#333">{X.rich(sub)}</div>'
            + field_num(X, "hf", 30, 136, fw, fh, px, unit, 40, pad=pad, unit_top=True)
            + small_field(X, "old", 30, oy, ow, 170, old.get("label", ""), old.get("value", ""), old.get("unit", ""))
            + button("ok", bw / 2 - 110 if not side else 30, bh - 96, 160 if side else 220, "确定", True)
            + (button("more", 200, bh - 96, 160, "详细 >>") if side else ""))
    X.used_text.update("详细 >>")
    win = window("main hid", mx, my, mw, mh, X.rich(b.get("title", "")), body)
    sec = ""
    if side:
        sx_, sy_, sw_, sh_ = srect
        X.used_text.update("".join(str(side.get(k, "")) for k in ("title", "label", "value", "note")))
        vpx = 200 if P else 210
        sfh = vpx * 0.56 + 44
        sbody = (f'<div class="lb" style="left:24px;top:16px;font-size:30px">{X.rich(side.get("label", ""))}</div>'
                 + field_num(X, "sf", 24, 62, sw_ - 60, sfh, vpx, "", pad=20, text=str(side.get("value", "")))
                 + f'<div class="lb" style="left:24px;top:{74 + sfh:.0f}px;font-size:28px">{X.rich(side.get("note", ""))}</div>')
        sbody = sbody.replace('<i class="caret"></i>', '')
        sec = window("side hid", sx_, sy_, sw_, sh_, X.rich(side.get("title", "")), sbody)
        sec += outlines((mx + 36, my + 62 + 136, fw, fh), srect).replace('class="ol ol', 'class="ol so ol')
    cur = Cur(X, mx + mw * 0.6, my + mh - 60)
    i = X.beat["i"]
    bx_ok = mx + 6 + (bw / 2 if not side else 110)
    by_btn = my + 62 + bh - 96 + 30
    ends = i % 2 == 0 and i + 1 < X.beat["n"]
    t_press = (t + d - 0.9) if not side else (t + d - 0.2)
    s, to = page(X, b, cid, t, d, win + sec, cur, open_win=(".main", (mx, my, mw, mh)), open_from=b.get("icon", 0),
                 end_click=(bx_ok, by_btn, ".main .ok") if ends else None, end_at=t_press if ends else None)
    X.tw(f'tl.set("{s} .hf .tx", {{textContent:""}}, {t:.3f});')
    tb = max(to + 0.15, T(X, b, "at_big", t, to + 0.15))
    type_digits(X, f"{s} .hf", big, tb, 3)
    # the cursor clicks the empty previous-year slot: its sunken box draws, then the old figure types in digit by digit
    ov = str(old.get("value", ""))
    t_old = tb + len(big) * 3 * F + (0.9 if not side else 0.3)
    X.tw(f'tl.set("{s} .old", {{visibility:"hidden"}}, {t:.3f}); tl.set("{s} .old .tx", {{textContent:""}}, {t:.3f});')
    cur.to(mx + 6 + 30 + 120, my + 62 + oy + 60, t_old - 0.42, 0.38)
    cur.click(t_old)
    X.tw(f'tl.set("{s} .old", {{visibility:"visible"}}, {t_old + F:.3f});')
    X.tw(f'tl.fromTo("{s} .old", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.2, ease:"steps(5)"}}, {t_old + F:.3f});')
    for k in range(len(ov) + 1):
        X.tw(f'tl.set("{s} .old .tx", {{textContent:"{ov[:k]}"}}, {t_old + 0.25 + k * 3 * F:.3f});')
    X.sfx(t_old + 0.25, "count")
    if ends:
        # the cursor heads for 确定 and the default button's focus rectangle starts marching; the press deactivates the window
        tm0 = t_old + 0.25 + len(ov) * 3 * F + 0.25
        X.tw(f'tl.fromTo("{s} .main .ok .fr rect", {{strokeDashoffset:0}}, {{strokeDashoffset:-16, duration:0.27, ease:"steps(4)", repeat:{max(1, int((t + d - tm0) / 0.27))}}}, {tm0:.3f});')
        if not side:
            X.tw(f'tl.set("{s} .main", {{attr:{{class:"vw main ina"}}}}, {t_press + 0.1:.3f});')
    if side:
        tm = t_old + 0.25 + len(ov) * 3 * F + 0.45
        cur.to(mx + 6 + 280, by_btn, tm - 0.45, 0.4)
        cur.click(tm)
        press(X, f"{s} .more", tm)
        X.tw(f'tl.set("{s} .main", {{attr:{{class:"vw main ina"}}}}, {tm + 0.1:.3f});')
        for k in range(1, 7):
            X.tw(f'tl.set("{s} .so.ol{k}", {{visibility:"visible"}}, {tm + 0.05 + (k - 1) * F:.3f}); tl.set("{s} .so.ol{k}", {{visibility:"hidden"}}, {tm + 0.05 + (k + 1) * F:.3f});')
        X.tw(f'tl.set("{s} .side", {{visibility:"visible"}}, {tm + 0.05 + 6 * F:.3f});')
        X.sfx(tm + 0.05, "open")
        X.tw(f'tl.set("{s} .main", {{attr:{{class:"vw main"}}}}, {t + d - 0.65:.3f}); tl.set("{s} .side", {{attr:{{class:"vw side ina"}}}}, {t + d - 0.65:.3f});')


def error(b, X, t, d, cid):
    """the bad news: an error box spawns 5 cascading copies 28 px down-right, one every 2 frames (the window trail bug);
    the last one carries the figure. Fields: title, msg, big (e.g. "-30.3%"), cmp {label, a, b}."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    fx_, fy_ = mx, my + 112
    bw_, bh_ = mw, mh - 112
    msg, big = b.get("msg", ""), str(b.get("big", ""))
    cmp_ = b.get("cmp") or {}
    num, pc = (big[:-1], "%") if big.endswith("%") else (big, "")
    X.used_text.update(msg + big + "确定→" + "".join(str(v) for v in cmp_.values()))
    iw, ih = bw_ - 12, bh_ - 68
    px = int(min(420, (iw - 24) / (0.4 * len(num) + (0.18 if pc else 0))))
    boxes = ""
    for k in range(5):
        x, y = fx_ - 28 * (4 - k), my + 28 * k
        last = k == 4
        body = (f'<div style="position:absolute;left:30px;top:26px">{error_glyph(96)}</div>'
                f'<div class="lb" style="left:150px;top:46px;font-size:36px">{X.rich(msg)}</div>')
        if last:
            it = 160
            body += (f'<div class="num bn" style="left:2px;top:{it - px * 0.24:.0f}px;font-size:{px}px;color:#a30000">{X.rich(num)}'
                     + (f'<span style="font-size:.4em;vertical-align:.95em;margin-left:-.04em">{pc}</span>' if pc else "") + '</div>')
            cy = it + px * 0.56 + 30
            cpx = 120
            body += (f'<div class="sk cmp" style="left:30px;top:{cy:.0f}px;width:{iw - 60}px;height:170px">'
                     f'<span class="lb" style="left:20px;top:12px;font-size:32px">{X.rich(cmp_.get("label", ""))}</span>'
                     f'<span class="num" style="left:20px;top:{58 + (112 - cpx * 0.56) / 2 - cpx * 0.24:.0f}px;font-size:{cpx}px">'
                     f'{X.rich(str(cmp_.get("a", "")))} <span style="font-size:.5em;vertical-align:.3em">→</span> {X.rich(str(cmp_.get("b", "")))}</span></div>')
        body += button("ok", iw / 2 - 110, ih - 92, 220, "确定", last)
        boxes += window(f"eb eb{k}" + (" front" if last else ""), x, y, bw_, bh_, X.rich(b.get("title", "错误")), body, "act" if last else "ina",
                        extra="visibility:hidden")
    cur = Cur(X, fx_ + bw_ * 0.7, fy_ + bh_ - 40)
    frect = (fx_, fy_, bw_, bh_)
    s, _ = page(X, b, cid, t, d, f'<div class="casc">{boxes}</div>', cur, drag=(".casc", frect))
    for k in range(5):
        X.tw(f'tl.set("{s} .eb{k}", {{visibility:"visible"}}, {t + 2 * k * F:.3f});')
        if k < 4: X.tw(f'tl.set("{s} .eb{k} .tb", {{background:"#6e7378"}}, {t + 2 * (k + 1) * F:.3f});')
    X.sfx(t + 0.05, "error")
    th = t + 10 * F
    X.tw(f'tl.from("{s} .bn", {{scaleY:0.1, transformOrigin:"50% 80%", duration:0.18, ease:"steps(3)"}}, {th:.3f});')
    # 确定 never closes the box (it's the bug): the first press prints the comparison row, the second makes the whole
    # cascade redraw — every box flashes inactive and back, then the cursor gives up and drags the pile away
    tc = t + 1.2
    okx, oky = fx_ + 6 + iw / 2, fy_ + 62 + ih - 92 + 30
    cur.to(okx, oky, tc - 0.5, 0.45)
    cur.click(tc)
    press(X, f"{s} .front .ok", tc)
    X.tw(f'tl.set("{s} .cmp", {{visibility:"hidden"}}, {t:.3f}); tl.set("{s} .cmp", {{visibility:"visible"}}, {tc + 2 * F:.3f});')
    X.tw(f'tl.fromTo("{s} .cmp", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.2, ease:"steps(5)"}}, {tc + 2 * F:.3f});')
    X.sfx(tc, "error")
    tc2 = tc + max(0.9, (d - 1.2 - 0.9) / 2)
    cur.click(tc2)
    press(X, f"{s} .front .ok", tc2)
    for k in range(3):
        X.tw(f'tl.set("{s} .front .tb", {{background:"#6e7378"}}, {tc2 + (1 + 4 * k) * F:.3f}); tl.set("{s} .front .tb", {{background:"linear-gradient(90deg, #1f2a8a 0%, #1f2a8a 30%, #6fa8ff 100%)"}}, {tc2 + (3 + 4 * k) * F:.3f});')
    X.tw(f'tl.fromTo("{s} .bn", {{x:0}}, {{x:10, duration:{2 * F:.3f}, ease:"steps(1)", yoyo:true, repeat:5}}, {tc2 + F:.3f});')
    X.sfx(tc2, "error")


def wizard(b, X, t, d, cid):
    """timeline as a setup wizard: picture strip on the left, steps with radio marks filling in order, each with a year,
    a value and a mini segmented bar in true ratio; "下一步 >" is pressed between states. Fields: title, head, sub,
    hero_unit, items [{when, value, at}], icon."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    items = b.get("items", [])[:4]
    n = len(items)
    head, sub = b.get("head", ""), b.get("sub", "")
    X.used_text.update(head + sub + "< 上一步下一步 >取消完成")
    bw, bh = mw - 12, mh - 68
    side = 230 if P else 300
    vmax = max(float(it.get("value", 0)) for it in items) or 1
    rx = side + 34
    rw = bw - rx - 24
    steps = ""
    for k, it in enumerate(items):
        y = 116 + 72 * k
        v = float(it.get("value", 0))
        when = it.get("when", "")
        X.used_text.update(when + str(it.get("value", "")))
        nb = 6 * v / vmax
        blks = ""
        for j in range(int(math.ceil(nb))):
            wj = 18 if j + 1 <= nb else 18 * (nb - j)
            blks += f'<i class="blk" style="left:{6 + 22 * j}px;width:{wj:.1f}px;background:{MAG if v == vmax else NAVY}"></i>'
        steps += (f'<div class="st st{k}" style="position:absolute;left:{rx}px;top:{y}px;width:{rw}px;height:64px">'
                  f'<div class="radio" style="left:0;top:17px"><i></i></div>'
                  f'<div class="lb" style="left:46px;top:12px;font-size:34px">{X.rich(when)}</div>'
                  f'<div class="sk sbar" style="left:{rw - 146 - 104 - 14}px;top:13px;width:146px;height:38px">{blks}</div>'
                  f'<div class="num" style="right:0;top:2px;font-size:64px">{X.rich(str(it.get("value", "")))}</div></div>')
    hero_y = 116 + 72 * n + 16
    fh = bh - 92 - 16 - hero_y
    hpx = 380 if P else 330
    first = str(items[0].get("value", "")) if items else ""
    sh_ = bh - 120
    strip = (f'<div class="sk" style="left:16px;top:16px;width:{side}px;height:{sh_}px;background:linear-gradient(180deg, #1f2a8a, #5a1e8c 55%, #ff3d9a);">'
             f'<svg viewBox="0 0 100 100" style="position:absolute;left:{side / 2 - 80:.0f}px;top:{sh_ * 0.28:.0f}px;width:160px;height:160px" fill="none" stroke="#19d3e6" stroke-width="2.2">'
             '<polygon points="50,6 92,30 92,72 50,96 8,72 8,30"/><path d="M50 6L50 50M92 30L50 50M8 30L50 50M50 96L50 50M8 72L50 50M92 72L50 50"/></svg>'
             f'<svg viewBox="0 0 19 19" style="position:absolute;left:{side / 2 - 40:.0f}px;top:{sh_ * 0.72:.0f}px;width:80px;height:80px" shape-rendering="crispEdges">'
             '<path d="M2 2h14l1 1v14H2z" fill="#c3c7cb" stroke="#111"/><path d="M5 2h8v6H5z" fill="#fff"/><path d="M4 11h11v6H4z" fill="#111"/></svg></div>')
    body = (strip + f'<div class="lb" style="left:{rx}px;top:20px;font-size:36px">{X.rich(head)}</div>'
            f'<div class="lb" style="left:{rx}px;top:72px;font-size:28px;color:#333">{X.rich(sub)}</div>' + steps
            + field_num(X, "rd", rx, hero_y, rw, fh, hpx, b.get("hero_unit", ""), 44, text=first)
            + f'<div class="hr" style="left:16px;right:16px;top:{bh - 92}px"></div>'
            + button("prev", bw - 24 - 3 * 190 - 24, bh - 74, 190, "< 上一步")
            + f'<div class="btn nxt def" style="left:{bw - 24 - 2 * 190 - 12:.0f}px;top:{bh - 74}px;width:190px;height:58px"><span class="nl">下一步 &gt;</span></div>'
            + button("cnl", bw - 24 - 190, bh - 74, 190, "取消"))
    win = window("main hid", mx, my, mw, mh, X.rich(b.get("title", "")), body)
    cur = Cur(X, mx + mw * 0.5, my + mh - 60)
    i = X.beat["i"]
    bx_next = mx + 6 + bw - 24 - 2 * 190 - 12 + 95
    by_btn = my + 62 + bh - 74 + 30
    s, to = page(X, b, cid, t, d, win, cur, open_win=(".main", (mx, my, mw, mh)), open_from=b.get("icon", 1),
                 end_click=(bx_next, by_btn, ".nxt") if i % 2 == 0 and i + 1 < X.beat["n"] else None)
    for k in range(n):
        X.tw(f'tl.set("{s} .st{k}", {{visibility:"hidden"}}, {t:.3f});')
        X.tw(f'tl.set("{s} .st{k} .sbar .blk", {{visibility:"hidden"}}, {t:.3f});')
    gaps = max(0.5, (d - (to - t) - 1.75) / max(1, n))
    tk = to + 0.15
    for k in range(n):
        it = items[k]
        if k > 0:
            tk = max(tk + 0.5, T(X, it, "at", t, tk + gaps))
            if k == 1: cur.to(bx_next, by_btn, tk - 0.45, 0.4)
            cur.click(tk)
            press(X, f"{s} .nxt", tk)
        X.tw(f'tl.set("{s} .st{k}", {{visibility:"visible"}}, {tk + F:.3f}); tl.set("{s} .st{k} .radio i", {{visibility:"visible"}}, {tk + F:.3f});')
        if k > 0: X.tw(f'tl.set("{s} .st{k - 1} .radio i", {{visibility:"hidden"}}, {tk + F:.3f});')
        blk = f"{s} .st{k} .sbar .blk"
        nbk = int(math.ceil(6 * float(it.get("value", 0)) / vmax))
        for j in range(nbk):
            X.tw(f'tl.set("{blk}:nth-child({j + 1})", {{visibility:"visible"}}, {tk + (2 + j // 2) * F:.3f});')
        X.tw(f'tl.set("{s} .rd .tx", {{textContent:"{it.get("value", "")}"}}, {tk + F:.3f});')
        X.tw(f'tl.set("{s} .rd .num", {{color:"{"#c4006a" if float(it.get("value", 0)) == vmax else "#111"}"}}, {tk + F:.3f});')
        X.sfx(tk + F, "line")
    X.tw(f'tl.set("{s} .rd .caret", {{visibility:"hidden"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .nl", {{textContent:"完成"}}, {tk + 0.3:.3f});')
    # back to the peak: the cursor clicks the strongest quarter's row; it is selected and highlighted, the readout shows it
    pk = max(range(n), key=lambda k: float(items[k].get("value", 0)))
    tb = tk + 0.75
    cur.to(mx + 6 + rx + 120, my + 62 + 116 + 72 * pk + 32, tb - 0.4, 0.36)
    cur.click(tb)
    X.tw(f'tl.set("{s} .st .radio i", {{visibility:"hidden"}}, {tb + F:.3f}); tl.set("{s} .st{pk} .radio i", {{visibility:"visible"}}, {tb + F:.3f});')
    X.tw(f'tl.set("{s} .st{pk}", {{background:"#ffe66d", outline:"2px dotted #111"}}, {tb + F:.3f});')
    X.tw(f'tl.set("{s} .rd .tx", {{textContent:"{items[pk].get("value", "")}"}}, {tb + F:.3f}); tl.set("{s} .rd .num", {{color:"#c4006a"}}, {tb + F:.3f});')
    X.sfx(tb + F, "line")


def progress(b, X, t, d, cid):
    """comparison as segmented progress bars (26×38 blocks) filling to true proportions, 2 blocks a frame, the share
    right-aligned in sunken fields; the first bar's share runs live in the hero readout. Fields: title, head,
    bars [{label, pct, note}], at_go."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    bars = b.get("bars", [])[:4]
    head = b.get("head", "")
    X.used_text.update(head + "开始取消%")
    bw, bh = mw - 12, mh - 68
    track_w = bw - 60 - 190
    nblk = int((track_w - 12) // 30)
    hpx = 380 if P else 360
    hfh = hpx * 0.56 + 80
    first = bars[0] if bars else {"pct": 0}
    html = (f'<div class="lb" style="left:30px;top:22px;font-size:36px">{X.rich(head)}</div>'
            + field_num(X, "hero", 30, 80, bw - 60, hfh, hpx, "", pad=24)
            + f'<div class="lb" style="right:54px;top:{80 + hfh - 50:.0f}px;font-size:28px;position:absolute">{X.rich(first.get("note", ""))}</div>')
    y0 = 80 + hfh + 36
    pitch = 190 if P else 180
    rows = ""
    for k, bar in enumerate(bars):
        y = y0 + k * pitch
        pct = float(bar.get("pct", 0))
        nb = nblk * pct / 100
        blks = ""
        for j in range(int(math.ceil(nb))):
            wj = 26 if j + 1 <= nb else 26 * (nb - j)
            blks += f'<i class="blk b{j}" style="left:{6 + 30 * j}px;top:6px;width:{wj:.1f}px;height:38px;background:{[MAG, CYAN, NAVY, MAG][k]}"></i>'
        X.used_text.update(bar.get("label", "") + bar.get("note", "") + f"{pct:g}")
        rows += (f'<div class="lb" style="left:30px;top:{y:.0f}px;font-size:36px">{X.rich(bar.get("label", ""))}</div>'
                 f'<div class="sk tr tr{k}" style="left:30px;top:{y + 54:.0f}px;width:{track_w}px;height:50px">{blks}</div>'
                 f'<div class="sk pf pf{k}" style="left:{30 + track_w + 16}px;top:{y + 50:.0f}px;width:174px;height:58px;display:flex;align-items:center;justify-content:flex-end;padding-right:12px">'
                 f'<span class="num" style="position:static;font-size:58px"><span class="pv">0.0</span>%</span></div>')
    html += rows
    by = bh - 74
    html += button("go", bw - 24 - 2 * 190 - 12, by, 190, "开始", True) + button("cnl", bw - 24 - 190, by, 190, "取消")
    win = window("main", mx, my, mw, mh, X.rich(b.get("title", "")), html)
    cur = Cur(X, mx + mw - 160, my + mh - 40)
    s, _ = page(X, b, cid, t, d, win, cur, drag=(".main", (mx, my, mw, mh)))
    X.tw(f'tl.set("{s} .hero .tx", {{textContent:"0.0%"}}, {t:.3f}); tl.set("{s} .hero .caret", {{display:"none"}}, {t:.3f}); tl.set("{s} .blk", {{visibility:"hidden"}}, {t:.3f});')
    tg = max(t + 0.45, T(X, b, "at_go", t, t + 0.45))
    gx, gy = mx + 6 + bw - 24 - 2 * 190 - 12 + 95, my + 62 + by + 30
    cur.to(gx, gy, tg - 0.45, 0.42)
    cur.click(tg)
    press(X, f"{s} .go", tg)
    ts = tg + 0.12
    X.used_text.update("0.%")
    for k, bar in enumerate(bars):
        pct = float(bar.get("pct", 0))
        nb = int(math.ceil(nblk * pct / 100))
        for j in range(nb):
            X.tw(f'tl.set("{s} .tr{k} .b{j}", {{visibility:"visible"}}, {ts + (j // 2) * F:.3f});')
        tdur = (nb // 2 + 1) * F
        hero = f', h=document.querySelector("{s} .hero .tx")' if k == 0 else ""
        upd = 'el.textContent=o.v.toFixed(1);' + ('h.textContent=o.v.toFixed(1)+"%";' if k == 0 else "")
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .pf{k} .pv"){hero}; tl.to(o, {{v:{pct}, duration:{tdur:.3f}, ease:"none", onUpdate:()=>{{{upd}}}}}, {ts:.3f});}})();')
        X.sfx(ts, "count")
        ts += tdur + 0.35


def explorer(b, X, t, d, cid):
    """ranking as a details-view file list: 名称 / 数值 / 占比 with a small bar in true ratio; rows appear top-down in name
    order (2-frame stagger), a click on the 数值 header flips the sort arrow and re-sorts them, the top row is selected and
    opened into a properties window with the hero share. Fields: title, path, items [{name, value, unit, share}], status,
    prop {title, label, value}, icon."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    items = b.get("items", [])[:5]
    ranked = sorted(range(len(items)), key=lambda k: -float(items[k].get("value", 0)))
    order0 = sorted(range(len(items)), key=lambda k: items[k].get("name", ""))
    status = b.get("status", "")
    X.used_text.update(status + "名称数值占比文件编辑查看帮助▲▼" + b.get("path", ""))
    bw, bh = mw - 12, mh - 68
    menu = "".join(f'<span style="margin-right:30px">{w}</span>' for w in ("文件", "编辑", "查看", "帮助"))
    lx, ly, lw = 16, 112, bw - 32
    rowh = 96
    lh_ = bh - 60 - ly
    c1, c2, c3 = lw * 0.42, lw * 0.26, lw * 0.32
    hdr = (f'<div class="btn" style="left:4px;top:4px;width:{c1:.0f}px;height:52px;justify-content:flex-start;padding-left:16px;font-size:30px">名称</div>'
           f'<div class="btn h2" style="left:{4 + c1:.0f}px;top:4px;width:{c2:.0f}px;height:52px;justify-content:flex-start;padding-left:16px;font-size:30px">数值'
           f'<span class="arr" style="margin-left:14px;font-size:24px;display:inline-block">▲</span></div>'
           f'<div class="btn" style="left:{4 + c1 + c2:.0f}px;top:4px;width:{c3 - 8:.0f}px;height:52px;justify-content:flex-start;padding-left:16px;font-size:30px">占比</div>')
    tot = sum(float(it.get("value", 0)) for it in items) or 1
    rows = ""
    for k, it in enumerate(items):
        pos = order0.index(k)
        y = 60 + rowh * pos
        sh = float(it.get("share", 100 * float(it.get("value", 0)) / tot))
        X.used_text.update(it.get("name", "") + str(it.get("value", "")) + it.get("unit", "") + f"{sh:.1f}%")
        barw = (c3 - 150) * sh / 100
        hh = rowh - 8
        rows += (f'<div class="row r{k}" style="position:absolute;left:4px;top:{y}px;width:{lw - 8:.0f}px;height:{hh}px">'
                 f'<div class="sel" style="position:absolute;inset:0;background:#1f2a8a;visibility:hidden"></div>'
                 f'<div style="position:absolute;left:12px;top:{hh / 2 - 22:.0f}px">{icon_svg("sheet", 44)}</div>'
                 f'<div class="lb nm" style="left:70px;top:{hh / 2 - 22:.0f}px;font-size:36px">{X.rich(it.get("name", ""))}</div>'
                 f'<div class="num vl" style="left:{c1 + 14:.0f}px;top:{hh / 2 - 34:.0f}px;font-size:70px">{X.rich(str(it.get("value", "")))}'
                 f'<span class="lb" style="position:static;font-size:26px;margin-left:8px">{X.rich(it.get("unit", ""))}</span></div>'
                 f'<div style="position:absolute;left:{c1 + c2 + 12:.0f}px;top:{hh / 2 - 15:.0f}px;width:{c3 - 150:.0f}px;height:30px;background:#e4e6ea;box-shadow:inset 1px 1px 0 #7d8288">'
                 f'<i style="position:absolute;left:0;top:0;bottom:0;width:{barw:.1f}px;background:{MAG}"></i></div>'
                 f'<div class="num sv" style="left:{c1 + c2 + c3 - 132:.0f}px;top:{hh / 2 - 26:.0f}px;font-size:56px">{sh:.1f}%</div></div>')
    body = (f'<div class="lb" style="left:16px;top:8px;font-size:24px">{menu}</div>'
            f'<div class="sk gr" style="left:12px;top:44px;width:{bw - 24}px;height:52px;display:flex;align-items:center;padding-left:14px">'
            f'<span class="lb" style="position:static;font-size:24px;background:#fff;padding:4px 12px;box-shadow:inset 2px 2px 0 #7d8288">{X.rich(b.get("path", ""))}</span></div>'
            f'<div class="sk lst" style="left:{lx}px;top:{ly}px;width:{lw}px;height:{lh_}px">{hdr}{rows}</div>'
            f'<div class="sk gr" style="left:12px;top:{bh - 50}px;width:{bw - 24}px;height:44px;display:flex;align-items:center;padding-left:14px">'
            f'<span class="lb" style="position:static;font-size:26px">{X.rich(status)}</span></div>')
    win = window("main hid", mx, my, mw, mh, X.rich(b.get("title", "")), body)
    pr = b.get("prop") or {}
    X.used_text.update("".join(str(pr.get(k, "")) for k in ("title", "label", "value")) + "确定")
    if P:
        pw, ph, vpx = 580, 420, 270
        px_, py_ = 380, my + mh - 20 - ph
    else:
        pw, ph, vpx = 620, 370, 220
        px_, py_ = mx + mw - 80, my + mh - ph
    pfh = vpx * 0.56 + 40
    pbody = (f'<div class="lb" style="left:24px;top:14px;font-size:30px">{X.rich(pr.get("label", ""))}</div>'
             + field_num(X, "pv", 16, 58, pw - 44, pfh, vpx, "", pad=12, text=str(pr.get("value", "")), color="#c4006a").replace('<i class="caret"></i>', '')
             + button("pok", pw - 12 - 24 - 170, ph - 68 - 66, 170, "确定", True))
    prop = window("prop hid", px_, py_, pw, ph, X.rich(pr.get("title", "属性")), pbody)
    top_k = ranked[0]
    r_abs = lambda pos: (mx + 6 + lx + 4, my + 62 + ly + 60 + rowh * pos, lw - 8, rowh - 8)
    prop += outlines(r_abs(0), (px_, py_, pw, ph)).replace('class="ol ol', 'class="ol po ol')
    cur = Cur(X, mx + mw * 0.7, my + mh - 40)
    i = X.beat["i"]
    s, to = page(X, b, cid, t, d, win + prop, cur, open_win=(".main", (mx, my, mw, mh)), open_from=b.get("icon", 0),
                 end_click=(px_ + pw - 6 - 24 - 85, py_ + 62 + ph - 68 - 66 + 30, ".prop .pok") if i % 2 == 0 and i + 1 < X.beat["n"] else None)
    for k in range(len(items)):
        X.tw(f'tl.set("{s} .r{k}", {{visibility:"hidden"}}, {t:.3f}); tl.set("{s} .r{k}", {{visibility:"visible"}}, {to + 0.1 + 2 * F * order0.index(k):.3f});')
    X.sfx(to + 0.1, "line")
    ts = max(to + 0.9, T(X, b, "at_sort", t, to + 0.9))
    hx, hy = mx + 6 + lx + 4 + c1 + c2 * 0.4, my + 62 + ly + 30
    cur.to(hx, hy, ts - 0.45, 0.42)
    cur.click(ts)
    press(X, f"{s} .h2", ts)
    X.tw(f'tl.set("{s} .arr", {{rotation:180}}, {ts + F:.3f});')
    for k in range(len(items)):
        dy = rowh * (ranked.index(k) - order0.index(k))
        if dy: X.tw(f'tl.to("{s} .r{k}", {{y:{dy}, duration:0.3, ease:"power2.inOut"}}, {ts + 2 * F:.3f});')
    X.sfx(ts + 2 * F, "line")
    tsel = ts + 0.75
    rx_, ry_, _, _ = r_abs(0)
    cur.to(rx_ + 260, ry_ + 50, tsel - 0.35, 0.32)
    cur.click(tsel, sfx=False)
    X.tw(f'tl.set("{s} .r{top_k} .sel", {{visibility:"visible"}}, {tsel + F:.3f}); tl.set("{s} .r{top_k} .lb, {s} .r{top_k} .num", {{color:"#fff"}}, {tsel + F:.3f});')
    cur.click(tsel + 0.16)
    tp = tsel + 0.24
    for k in range(1, 7):
        X.tw(f'tl.set("{s} .po.ol{k}", {{visibility:"visible"}}, {tp + (k - 1) * F:.3f}); tl.set("{s} .po.ol{k}", {{visibility:"hidden"}}, {tp + (k + 1) * F:.3f});')
    X.tw(f'tl.set("{s} .prop", {{visibility:"visible"}}, {tp + 6 * F:.3f}); tl.set("{s} .main", {{attr:{{class:"vw main ina"}}}}, {tp + 6 * F:.3f});')
    X.sfx(tp, "open")


def paint(b, X, t, d, cid):
    """share-of-total in a paint program: the cursor picks the bucket, then the magenta swatch, then clicks the 10×10 grid;
    the fill floods the true count of cells (a half cell is dithered); the text tool types the figure under the grid.
    Fields: title, label, pct, big, note."""
    P = X.portrait
    l = L(X)
    mx, my, mw, mh = l["main"]
    if P:
        my, mh = 300, 1030          # the tallest window of the film: a 640 px grid with the figure under it
    pct = max(0.0, min(100.0, float(b.get("pct", 50))))
    big, lab, note = b.get("big", f"{pct:g}%"), b.get("label", ""), b.get("note", "")
    X.used_text.update(big + lab + note + "文件编辑查看图像颜色帮助")
    bw, bh = mw - 12, mh - 68
    menu = "".join(f'<span style="margin-right:28px">{w}</span>' for w in ("文件", "编辑", "查看", "图像", "颜色"))
    tools = ["select", "erase", "bucket", "pencil", "brush", "text"]
    tb = "".join(f'<div class="btn tl t{k}" style="left:{8 + 50 * (k % 2)}px;top:{48 + 52 * (k // 2)}px;width:48px;height:50px">{tool_glyph(g)}</div>' for k, g in enumerate(tools))
    cv_x, cv_y = 112, 48
    cv_w = bw - cv_x - 16
    pal_y = bh - 40
    cv_h = pal_y - 8 - cv_y
    cell = 60 if P else 48
    gx, gy = 24, 24
    gs = 10 * cell
    cells = ""
    full = int(pct)
    frac = pct - full
    order = []
    for k in range(100):
        r_, c_ = divmod(k, 10)
        cells += f'<i class="cl c{k}" style="position:absolute;left:{gx + c_ * cell}px;top:{gy + r_ * cell}px;width:{cell}px;height:{cell}px;box-shadow:inset 0 0 0 1px #b8bcc2"></i>'
    grid_fill = ""
    for k in range(full + (1 if frac > 0.01 else 0)):
        r_, c_ = divmod(k, 10)
        half = k == full
        bgc = (f"background-image:conic-gradient({MAG} 25%, transparent 0 50%, {MAG} 0 75%, transparent 0);background-size:8px 8px" if half else f"background:{MAG}")
        grid_fill += f'<i class="fl f{k}" style="position:absolute;left:{gx + c_ * cell}px;top:{gy + r_ * cell}px;width:{cell}px;height:{cell}px;{bgc};visibility:hidden"></i>'
        order.append((r_ + c_, k))
    npx = 308 if P else 300
    nit = gy + gs + 28                                   # ink top of the figure, 28 px under the grid
    labels = ""
    if not P:      # 16:9: the label and the previous year sit right of the grid
        rx = gx + gs + 36
        labels = (f'<div class="lb" style="left:{rx}px;top:{gy + 4}px;font-size:40px">{X.rich(lab)}</div>'
                  f'<div class="lb" style="left:{rx}px;top:{gy + 70}px;font-size:30px;line-height:1.5;white-space:normal;width:{cv_w - rx - 20}px">{X.rich(note)}</div>')
    canvas = (f'<div class="sk cv" style="left:{cv_x}px;top:{cv_y}px;width:{cv_w}px;height:{cv_h}px">'
              f'{cells}{grid_fill}{labels}'
              f'<div class="num pn" style="left:{gx - 6}px;top:{nit - npx * 0.24:.0f}px;font-size:{npx}px;color:#111"><span class="tx"></span><i class="caret"></i></div>'
              '</div>')
    sw = [MAG, CYAN, YEL, NAVY, "#111111", "#ffffff", "#7d8288", "#ff7a59"]
    pal = "".join(f'<i class="sw sw{k}" style="position:absolute;left:{70 + 40 * k}px;top:{pal_y + 4}px;width:34px;height:34px;background:{c};box-shadow:{SUNKEN}"></i>' for k, c in enumerate(sw))
    pal += f'<i class="fg" style="position:absolute;left:16px;top:{pal_y}px;width:42px;height:42px;background:#111;box-shadow:{SUNKEN}"></i>'
    if P:          # 9:16: the label and the previous year on the colour-box row
        pal += f'<div class="lb" style="left:{70 + 40 * len(sw) + 20}px;top:{pal_y + 4}px;font-size:28px">{X.rich(lab + " · " + note.split("|")[-1])}</div>'
    body = f'<div class="lb" style="left:16px;top:6px;font-size:24px">{menu}</div>{tb}{canvas}{pal}'
    win = window("main", mx, my, mw, mh, X.rich(b.get("title", "")), body)
    cur = Cur(X, mx + mw * 0.55, my + mh - 40)
    s, _ = page(X, b, cid, t, d, win, cur, drag=(".main", (mx, my, mw, mh)))
    ox, oy = mx + 6, my + 62
    tb_ = t + 0.45
    cur.to(ox + 8 + 24, oy + 48 + 52 + 25, tb_ - 0.4, 0.36)     # the bucket (index 2: column 0, row 1)
    cur.click(tb_)
    X.tw(f'tl.set("{s} .t2", {{boxShadow:"{PRESSED}", background:"#dfe2e5"}}, {tb_ + F:.3f});')
    tsw = tb_ + 0.5
    cur.to(ox + 70 + 17, oy + pal_y + 20, tsw - 0.4, 0.36)
    cur.click(tsw)
    X.tw(f'tl.set("{s} .fg", {{background:"{MAG}"}}, {tsw + F:.3f});')
    tf = max(tsw + 0.55, T(X, b, "at_fill", t, tsw + 0.55))
    cur.to(ox + cv_x + gx + cell * 1.5, oy + cv_y + gy + cell * 1.5, tf - 0.42, 0.38)
    cur.click(tf)
    for dist, k in sorted(order):
        X.tw(f'tl.set("{s} .f{k}", {{visibility:"visible"}}, {tf + (dist + 1) * F:.3f});')
    X.sfx(tf, "pop")
    tt_ = tf + (max(dd for dd, _ in order) + 2) * F + 0.25
    cur.to(ox + 8 + 50 + 24, oy + 48 + 52 * 2 + 25, tt_ - 0.36, 0.3)      # the text tool
    cur.click(tt_)
    X.tw(f'tl.set("{s} .t5", {{boxShadow:"{PRESSED}", background:"#dfe2e5"}}, {tt_ + F:.3f}); tl.set("{s} .t2", {{boxShadow:"{RAISED}", background:"#c3c7cb"}}, {tt_ + F:.3f});')
    tw_ = tt_ + 0.4
    cur.to(ox + cv_x + gx + 10, oy + cv_y + nit + 30, tw_ - 0.35, 0.32)
    cur.click(tw_)
    X.tw(f'tl.set("{s} .pn .caret", {{visibility:"hidden"}}, {t:.3f}); tl.set("{s} .pn .caret", {{visibility:"visible"}}, {tw_ + F:.3f});')
    type_digits(X, f"{s} .pn", big, tw_ + 0.05, 2)


def shutdown(b, X, t, d, cid):
    """the summary: a centred dialog lists three figures with radio buttons; the cursor ticks each, presses 确定 and the
    screen behind dims in a dither. Fields: title, head, rows [{k, v, unit}]."""
    P = X.portrait
    rows = b.get("rows", [])[:3]
    head = b.get("head", "")
    X.used_text.update(head + "确定取消")
    if P:
        dx, dy, dw, dh = 120, 300, 840, 1000
    else:
        dx, dy, dw, dh = 400, 60, 1120, 900
    bw, bh = dw - 12, dh - 68
    mon = (f'<svg viewBox="0 0 24 24" width="104" height="104" shape-rendering="crispEdges" style="position:absolute;left:28px;top:20px">'
           f'<path d="M2 3h20v14H2z" fill="#c3c7cb" stroke="#111"/><path d="M4 5h16v10H4z" fill="{NAVY}"/><path d="M5 13h14v1H5z" fill="{MAG}"/>'
           f'<path d="M9 17h6v2H9zM6 19h12v2H6z" fill="#7d8288" stroke="#111" stroke-width=".6"/></svg>')
    html = mon + f'<div class="lb" style="left:156px;top:44px;font-size:36px;white-space:normal;width:{bw - 190}px;line-height:1.35">{X.rich(head)}</div>'
    y0 = 140
    rh = 205 if P else 192
    npx = 216 if P else 200
    for k, r in enumerate(rows):
        y = y0 + rh * k
        X.used_text.update(r.get("k", "") + str(r.get("v", "")) + r.get("unit", ""))
        html += (f'<div class="opt o{k}" style="position:absolute;left:30px;top:{y}px;width:{bw - 60}px;height:{rh - 10}px">'
                 f'<div class="hi" style="position:absolute;inset:0;border:2px dotted #111;visibility:hidden"></div>'
                 f'<div class="radio" style="left:14px;top:{(rh - 10) / 2 - 15:.0f}px"><i></i></div>'
                 f'<div class="lb" style="left:66px;top:10px;font-size:32px">{X.rich(r.get("k", ""))}</div>'
                 f'<div class="num" style="left:60px;top:{58 - npx * 0.24:.0f}px;font-size:{npx}px">{X.rich(str(r.get("v", "")))}'
                 f'<span class="lb" style="position:static;font-size:36px;margin-left:16px">{X.rich(r.get("unit", ""))}</span></div></div>')
    html += button("ok", bw - 24 - 2 * 200 - 16, bh - 80, 200, "确定", True) + button("cnl", bw - 24 - 200, bh - 80, 200, "取消")
    win = window("main", dx, dy, dw, dh, X.rich(b.get("title", "")), html, extra="z-index:80")
    dim = '<div class="dim"></div>'
    cur = Cur(X, dx + dw * 0.5, dy + dh - 40)
    s, _ = page(X, b, cid, t, d, dim + win, cur)
    tk = t + 0.4
    gap = max(0.42, min(0.7, (d - 2.2) / 3))
    for k in range(len(rows)):
        tk = max(tk, T(X, rows[k], "at", t, tk))
        ox, oy = dx + 6 + 30 + 29, dy + 62 + y0 + rh * k + (rh - 10) / 2
        cur.to(ox, oy, tk - 0.36, 0.32)
        cur.click(tk)
        X.tw(f'tl.set("{s} .o{k} .radio i, {s} .o{k} .hi", {{visibility:"visible"}}, {tk + F:.3f});')
        if k: X.tw(f'tl.set("{s} .o{k - 1} .hi, {s} .o{k - 1} .radio i", {{visibility:"hidden"}}, {tk + F:.3f});')
        tk += gap
    to = tk + 0.1
    cur.to(dx + 6 + bw - 24 - 2 * 200 - 16 + 100, dy + 62 + bh - 80 + 30, to - 0.4, 0.36)
    cur.click(to)
    press(X, f"{s} .ok", to)
    for k in range(1, 7):
        X.tw(f'tl.set("{s} .dim", {{height:"{100 * k / 6:.1f}%"}}, {to + 0.08 + k * F:.3f});')
    X.sfx(to + 0.08, "hit")


SCENES = {"dialog": dialog, "error": error, "wizard": wizard, "progress": progress, "explorer": explorer, "paint": paint, "shutdown": shutdown}


# ---------------------------------------------------------------- effects in this style (shared fx beats)
STYLE["fx_themes"] = {
    "paper": {"bg": FACE, "fg": INK, "muted": "#3b3f45", "accent": "#c4006a", "card": "#ffffff", "card-fg": INK, "line": "rgba(17,17,17,.2)"},
    "ink":   {"bg": SKY0, "fg": "#ffffff", "muted": "#d9c8ff", "accent": MAG, "card": FACE, "card-fg": INK, "line": "rgba(255,255,255,.25)"},
    "red":   {"bg": "#5a1e8c", "fg": "#ffffff", "muted": "#f0d8ff", "accent": YEL, "card": FACE, "card-fg": INK, "line": "rgba(255,255,255,.3)"},
    "lemon": {"bg": TIP, "fg": INK, "muted": "#4a4a3a", "accent": "#c4006a", "card": "#ffffff", "card-fg": INK, "line": "rgba(17,17,17,.2)"},
}

FX_CSS = r"""
/* an effect's page is the client area of a system window: grey face or dusk purple, with a faint magenta grid at the foot */
.st-vapor .fx { background-image:linear-gradient(0deg, rgba(255,79,216,.16) 2px, transparent 2px), linear-gradient(90deg, rgba(255,79,216,.12) 2px, transparent 2px) !important;
  background-size:90px 90px !important; background-position:0 100% !important; }
.st-vapor .fx .big, .st-vapor .fx .op .op-t { font-family:var(--f-num); letter-spacing:0; }
.st-vapor .fx .col > .sub { background:#c3c7cb; color:#111; padding:.6vmin 2vmin; box-shadow:__RAISED__; font-family:var(--f-pixel); }
/* the page around an effect (FX_FRAME): window chrome with a title bar, the menu bar as the header, the tooltip subtitle */
.ctx.vpx .vfr { position:absolute; inset:0; pointer-events:none; }
.ctx.vpx .vfr .rim { position:absolute; inset:0; border:14px solid #c3c7cb; box-shadow:inset -2px -2px 0 #1b1b1b, inset 2px 2px 0 #fff; }
.ctx.vpx .vfr .rim::after { content:""; position:absolute; inset:-14px; box-shadow:inset 2px 2px 0 #fff, inset -2px -2px 0 #1b1b1b, inset -4px -4px 0 #7d8288; }
.ctx.vpx .hd { left:14px; right:14px; top:14px; height:56px; border:none; display:flex; align-items:center; justify-content:space-between; padding:0 12px 0 18px;
  background:linear-gradient(90deg, #1f2a8a, #6fa8ff); color:#fff; font-family:var(--f-display); font-weight:700; font-size:30px; }
.ctx.vpx .hd .fxid { font-family:var(--f-num); font-size:34px; background:#c3c7cb; color:#111; padding:0 12px; box-shadow:__RAISED__; }
.ctx.vpx .cap { bottom:80px; padding:0 220px; }
.ctx.vpx .cap > span { background:#ffffe1; color:#111; font-family:var(--f-cap); font-weight:700; border:2px solid #000; box-shadow:6px 6px 0 #000; padding:8px 24px; border-radius:0; }
.ctx.vpx .cap .em .emt { color:#b0005e; } .ctx.vpx .cap .em .emb { display:none; }
.ctx.vpx .ft { left:30px; right:30px; bottom:26px; opacity:1; color:#fff; font-size:22px; }
.ctx.vpx .ft > div { background:rgba(0,0,0,.65); padding:4px 12px; }
#root.v .ctx.vpx .hd { top:200px; left:60px; right:60px; }
#root.v .ctx.vpx .cap { top:1380px; bottom:auto; padding:0 120px; }
#root.v .ctx.vpx .ft { left:120px; right:120px; top:1470px; bottom:auto; flex-direction:column; align-items:flex-start; gap:4px; }
"""
STYLE["css"] = FX_CSS.replace("__RAISED__", RAISED)


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around a shared effect in vapor: the effect sits in a window's client area (grey bevelled rim), the topic
    is the blue title bar with the effect id on a raised chip, the spoken line a tooltip plate, the footnote a dark strip."""
    th = p.get("theme") if p.get("theme") in STYLE["fx_themes"] else "ink"
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (('<div class="scrim"></div>' if parts["photo"] else "")
             + '<div class="vfr"><div class="rim"></div></div>'
             + f'<div class="hd"><span>{parts["topic"] or X.rich(X.channel)}</span><span class="fxid">{parts["fxid"]}</span></div>'
             + f'<div class="cap"><span style="font-size:{max(40, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             + f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update(X.channel)
    X.clip(f"{cid}c", t, d, inner, f"ctx vpx{' photo' if parts['photo'] else ''}", 30, track=20, sty=parts["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .hd", {{scaleY:0, transformOrigin:"50% 0%", duration:0.2, ease:"steps(4)"}}, {t + 0.03:.3f});')
    X.tw(f'tl.from("{s} .cap > span", {{scale:0.6, opacity:0, transformOrigin:"0% 100%", duration:0.16, ease:"steps(3)"}}, {t + 0.12:.3f});')


# the subtitle: a tooltip / status plate — pale yellow, 2 px black border, 6 px hard black shadow, black bold sans, left aligned
STYLE["css"] += """
.st-vapor .clip.cap .cp { display:block; text-align:left; border:2px solid #000; box-shadow:6px 6px 0 #000; line-height:50px; letter-spacing:.02em; }
#root.v.st-vapor .clip.cap { padding-left:120px; padding-right:120px; }
#root.h.st-vapor { --cap-bottom:14px; }
#root.h.st-vapor .clip.cap { padding-left:380px; padding-right:250px; z-index:65 !important; }
#root.h.st-vapor .clip.cap .cp { font-size:40px; line-height:44px; padding:2px 20px; box-shadow:4px 4px 0 #000; }
"""
