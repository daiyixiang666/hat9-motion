"""title · 片头字幕 —— a main-title sequence scratched into black film: the Se7en / Imaginary Forces manner, not a slate.

Ground: film black #0b0a09 that never sits still. One seeded engine (per frame, from the frame index and the beat index,
so every render is identical) breathes the exposure (±2.5 % luma, re-stepped 3 times a second), re-seats heavy 16 mm grain
every 2 frames, weaves the gate ±2 px every 2–3 frames, drifts 1–3 bone scratches (each lives 6–20 frames), drops 2–5
dust specks and hairs per frame, flashes at most one 2-frame amber light leak per beat, and re-seeds the turbulence that
makes the hand-scratched type boil every 3 frames.

Palette, nothing else: bone #e8e2d2 for type, tungsten amber #c8741d for one word or unit per beat, dried-blood
#7c1712 only for hand marks (strike-outs, underlines, circles). Two voices: hand-scratched (Long Cang / Permanent Marker
through an SVG displacement) for headlines and hero numerals, and a typewriter (Special Elite, CJK falls back to Noto Sans
SC 500) for labels, sources and the subtitle. Every hero carries a 140 %, 6 px blurred, 12 % double exposure drifting
behind it at its own speed.

Layout (9:16): off-centre and layered; the hero crosses the centreline but is anchored to one side, a small typewriter
label sits in the opposite corner, one label per beat runs up the left edge (x 60–110). Film edge with sprocket holes on
the left 34 px, a keykode column down the right edge above y 960, slug "REEL 01 · 03/08" at y 204, source line at
y 1452, subtitle on a lifted-black strip at y 1334–1400, left x 110. Below y 1520 only texture: the hero's ghost, a burned
frame-edge glow, scratched tally marks.

Charts are scratches on film: tally marks in fives (tally), two hatched bars in true ratio (bars), a hand-drawn circle
with the share hatched in stroke by stroke (circle), a vertical strip of film frames with the key frame burned (strip).
Numbers are scratched in digit by digit; the old value is struck out in red and the new one written bigger (cross).
Everything moves on 2s and 3s while the grain runs at full rate; a hero lands through 2–3 flash-frame jump cuts (one a
negative). Beat to beat: 2 frames of white-amber flare, 2 frames of a frame slipped 40 % with the frame line showing, cut.

Scenes (SCENES): cross · strip · tally · quote · bars · circle · end. No host.
"""
import math
import random

from h9 import fit

BLACK, BONE, AMBER, BLOOD, LIFT = "#0b0a09", "#e8e2d2", "#c8741d", "#7c1712", "#1a1816"
FPS = 30

STYLE = {
    "name": "片头字幕", "en": "Main Title", "benchmarks": ["Kyle Cooper · Se7en main titles", "Imaginary Forces", "Saul Bass (rhythm)"],
    "tokens": {
        "bg": BLACK, "fg": BONE, "muted": "#a8a293", "accent": AMBER, "accent2": BONE, "alert": BLOOD,
        "line": "rgba(232,226,210,.28)", "paper": BLACK, "ink": BONE, "card": LIFT, "card-fg": BONE,
        "bone": BONE, "amber": AMBER, "blood": BLOOD, "lift": LIFT,
        "cap-bg": LIFT, "cap-fg": BONE, "cap-size": "44px", "cap-weight": "500", "cap-pad": "7px 20px 9px", "cap-radius": "0",
        "cap-shadow": "none", "cap-bottom": "110px", "cap-em": AMBER, "punch-top": "70%", "punch-size": "72px",
    },
    "fonts": {"display": ["long-cang"], "hand": ["long-cang"], "num": ["permanent-marker", "long-cang"],
              "body": ["special-elite", "noto-sans-sc"], "mono": ["special-elite", "noto-sans-sc"], "cap": ["special-elite", "noto-sans-sc"],
              "latin": ["special-elite", "noto-sans-sc"], "serif": ["special-elite", "noto-sans-sc"], "punch": ["long-cang"], "quiet": ["special-elite", "noto-sans-sc"]},
    "motion": {"ease": "steps(4)", "dur": 0.4, "stagger": 0.067, "cut": "hard", "transition": "hard", "em": "color", "camera": "none"},
    "layers": [],
    "caption_plate": False,
    "safe_exempt": [".ti-kk", ".ti-tex", ".ti-edge"],     # film furniture (keykode pattern, bottom texture) is not text to read
    "mascot": {"mode": "none"},
    "outro": {"move": False},
    "sfx": {"transition": None, "enter": None, "pop": None, "hit": None, "slam": None, "count": None, "click": None,
            "mascot": None, "cut": None, "line": None, "title": None, "write": None},
}


# ---------------------------------------------------------------- textures (seeded SVG noise, tiled)
def _noise(seed, freq=0.92, alpha=1.0):
    return ("url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='256' height='256'>"
            f"<filter id='n'><feTurbulence type='fractalNoise' baseFrequency='{freq}' numOctaves='2' seed='{seed}' stitchTiles='stitch'/>"
            f"<feColorMatrix values='0 0 0 0 .91  0 0 0 0 .89  0 0 0 0 .82  {2.2 * alpha:.2f} 0 0 0 {-0.95 * alpha:.2f}'/></filter>"
            "<rect width='256' height='256' filter='url(%23n)'/></svg>\")")


GRAIN = [_noise(s) for s in (3, 11, 23, 41)]


def _q(css):
    return css.replace('"', "&quot;")

GRAIN_FINE = [_noise(s, 1.3, 0.8) for s in (5, 17)]

CSS = r"""
.st-title .mascot { display:none !important; }
.ti { position:absolute; inset:0; overflow:hidden; background:#0b0a09; color:var(--bone); }
.ti .ti-gate { position:absolute; inset:-6px; }
.ti .ti-gr { position:absolute; inset:0; overflow:hidden; opacity:.26; pointer-events:none; }
.ti .ti-gr i, .ti .ti-gr2 i { position:absolute; left:-256px; top:-256px; right:-256px; bottom:-256px; display:none; background-size:256px 256px; }
.ti .ti-gr2 { position:absolute; inset:0; overflow:hidden; opacity:.075; pointer-events:none; z-index:20; }
.ti .ti-cam { position:absolute; inset:6px; }
.ti .ti-ex { position:absolute; inset:0; opacity:0; pointer-events:none; z-index:22; }
.ti .ti-lk { position:absolute; inset:0; opacity:0; pointer-events:none; z-index:23; mix-blend-mode:screen; }
.ti .ti-fl { position:absolute; inset:0; opacity:0; pointer-events:none; z-index:30;
  background:radial-gradient(ellipse 70% 60% at 50% 45%, #d9ccb2 0%, #cfb48a 38%, #b5691c 78%, #4a2307 100%); }
.ti .ti-fline { position:absolute; left:0; right:0; height:44px; display:none; z-index:29; background:#050404;
  box-shadow:0 -2px 0 rgba(232,226,210,.35), 0 2px 0 rgba(232,226,210,.18); }
.ti .ti-scr { position:absolute; inset:0; pointer-events:none; z-index:21; }
.ti .ti-scr i { position:absolute; top:-20px; bottom:-20px; width:2px; display:none;
  background:linear-gradient(180deg, transparent, rgba(232,226,210,.8) 8%, rgba(232,226,210,.55) 50%, rgba(232,226,210,.85) 92%, transparent); }
.ti .ti-du { position:absolute; inset:0; pointer-events:none; z-index:21; }
.ti .ti-du svg { position:absolute; left:0; top:0; display:none; overflow:visible; }
/* film edge (left 34 px, sprocket holes 22×30 every 96 px, slightly out of focus) */
.ti .ti-edge { position:absolute; left:0; top:0; bottom:0; width:34px; background:#131110; filter:blur(1.2px); z-index:5; }
.ti .ti-edge i { position:absolute; left:6px; width:22px; height:30px; border-radius:4px; background:rgba(232,226,210,.42); }
/* keykode column down the right edge (pattern, not content) */
.ti .ti-kk { position:absolute; right:14px; top:30px; width:26px; z-index:0 !important; font-family:var(--f-mono); font-size:20px; line-height:1; color:rgba(232,226,210,.3);
  writing-mode:vertical-rl; letter-spacing:.18em; white-space:nowrap; z-index:5; overflow:hidden; }
.ti .ti-slug { position:absolute; left:72px; top:204px; font-family:var(--f-mono); font-size:26px; letter-spacing:.3em; color:rgba(232,226,210,.82);
  text-shadow:1px 0 0 rgba(232,226,210,.32); white-space:nowrap; z-index:6; }
.ti .ti-src { position:absolute; left:72px; top:1452px; max-width:828px; font-family:var(--f-mono); font-size:24px; letter-spacing:.16em; line-height:1.35;
  color:#e8e2d2; text-shadow:1px 0 0 rgba(232,226,210,.3); white-space:nowrap; overflow:hidden; z-index:6; }
/* texture below the safe area */
.ti .ti-tex { position:absolute; left:0; right:0; bottom:0; height:420px; pointer-events:none; }
.ti .ti-tex .glow { position:absolute; left:-10%; right:-10%; bottom:-120px; height:300px;
  background:radial-gradient(ellipse 60% 55% at 50% 100%, rgba(200,116,29,.20), rgba(200,116,29,.06) 55%, transparent 75%); }
.ti .ti-tex svg { position:absolute; left:0; top:0; overflow:visible; }
.ti .ti-tex .gb { position:absolute; opacity:.12; filter:blur(6px); white-space:nowrap; font-family:var(--f-num); color:var(--bone); line-height:1; }
/* the two voices */
.ti .hs { position:absolute; white-space:nowrap; line-height:1; color:var(--bone); font-family:var(--f-display); font-weight:400; font-synthesis:none;
  text-shadow:0 0 5px rgba(232,226,210,.22); }
.ti .hs.num { font-family:var(--f-num); }
.ti .hs .ln { display:block; }
.ti .hs .am, .ti .hs.am { color:var(--amber); text-shadow:none; }
.ti .hs i { font-style:normal; display:inline-block; }
.ti .gh { position:absolute; opacity:.12; filter:blur(6px); pointer-events:none; transform-origin:30% 50%; }
.ti .tw { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.3em; line-height:1.45; color:#e8e2d2;
  text-shadow:1px 0 0 rgba(232,226,210,.34); white-space:nowrap; text-transform:uppercase; }
.ti .tw .am { color:var(--amber); }
.ti .tw.rot { transform-origin:0 0; transform:rotate(-90deg); }
.ti svg.mk { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.ti svg.mk path { fill:none; stroke-linecap:round; stroke-linejoin:round; }
#root.h .ti .ti-slug { top:40px; left:80px; }
#root.h .ti .ti-src { top:1018px; left:80px; max-width:1500px; }
#root.h .ti .ti-tex { height:120px; }
/* subtitle: typewriter on a strip of lifted black, feathered, no border; left-aligned at x 110 */
#root.st-title .clip.cap { text-align:left; padding-left:110px; padding-right:130px; }
#root.st-title .clip.cap .cp { font-family:var(--f-cap); font-size:44px; font-weight:500; letter-spacing:.12em; line-height:1.3; color:#e8e2d2;
  background:rgba(26,24,22,.92); box-shadow:0 0 6px 3px rgba(26,24,22,.92); padding:7px 20px 9px; text-shadow:none; border-radius:0; }
#root.st-title .clip.cap .cp .em .emt { color:#c8741d; }
#root.v.st-title { --cap-bottom:520px; }
#root.h.st-title { --cap-bottom:118px; }
"""


# ---------------------------------------------------------------- the film engine (one per build, runs on the timeline)
ENGINE = r"""
(()=>{
const FPS=__FPS__, BONE="232,226,210";
const H=(a,b,c)=>{let x=Math.imul(a|0,374761393)^Math.imul((b|0)+7,668265263)^Math.imul((c|0)+13,2246822519);
  x=Math.imul(x^(x>>>13),1274126177); x^=x>>>16; return (x>>>0)/4294967296;};
let P=null;
function pages(){
  if(P) return P;
  P=[];
  document.querySelectorAll('.ti').forEach(p=>{
    P.push({p:p, i:+p.dataset.i, t0:+p.dataset.t0, t1:+p.dataset.t1, leak:+p.dataset.leak, ls:p.dataset.ls||"l",
      gate:p.querySelector('.ti-gate'), gr:[...p.querySelectorAll('.ti-gr i')], gr2:[...p.querySelectorAll('.ti-gr2 i')],
      ex:p.querySelector('.ti-ex'), lk:p.querySelector('.ti-lk'), scr:[...p.querySelectorAll('.ti-scr i')],
      du:[...p.querySelectorAll('.ti-du svg')], turb:[...p.querySelectorAll('feTurbulence.boil')],
      W:__W__, Hh:__H__});
  });
  return P;
}
function frame(T){
  const f=Math.round(T*FPS);
  for(const o of pages()){
    if(T<o.t0-0.05||T>o.t1+0.05) continue;
    const i=o.i, W=o.W, Hh=o.Hh;
    // exposure breathes: +-2.5 % luma, a new value 3 times a second
    const e=(H(Math.floor(f/10),i,1)*2-1)*0.025;
    o.ex.style.background = e>0 ? "rgb("+BONE+")" : "#000";
    o.ex.style.opacity = (Math.abs(e)*(e>0?1.15:3)).toFixed(4);
    // heavy grain re-seeded every 2 frames; a finer layer over the type every frame
    const k2=Math.floor(f/2), g=Math.floor(H(k2,i,2)*o.gr.length);
    o.gr.forEach((el,j)=>{ el.style.display = j===g ? "block" : "none"; });
    o.gr[g].style.transform="translate("+Math.round(H(k2,i,3)*256)+"px,"+Math.round(H(k2,i,4)*256)+"px)";
    const g2=f%o.gr2.length;
    o.gr2.forEach((el,j)=>{ el.style.display = j===g2 ? "block" : "none"; });
    o.gr2[g2].style.transform="translate("+Math.round(H(f,i,5)*256)+"px,"+Math.round(H(f,i,6)*256)+"px)";
    // gate weave: +-2 px, held 2 or 3 frames
    const kw=Math.floor(f/5)*2+((f%5)>=2?1:0);
    o.gate.style.transform="translate("+((H(kw,i,7)*2-1)*2).toFixed(2)+"px,"+((H(kw,i,8)*2-1)*2).toFixed(2)+"px)";
    // scratches: three slots, each a line living 6-20 frames, drifting sideways
    o.scr.forEach((el,s)=>{
      const L=26, ph=f+s*9, ep=Math.floor(ph/L), loc=ph-ep*L;
      const st=Math.floor(H(ep,s,9)*5), life=6+Math.floor(H(ep,s,10)*15);
      const on=H(ep,s+i*3,11) < (s===0?0.92:0.5) && loc>=st && loc<st+life;
      if(!on){ el.style.display="none"; return; }
      const x=W*(0.06+0.88*H(ep,s,12)) + (loc-st)*((H(ep,s,13)*2-1)*1.6);
      el.style.display="block"; el.style.left=x.toFixed(1)+"px";
      el.style.width=(1+Math.round(H(ep,s,14)))+"px";
      el.style.opacity=(0.28+0.3*H(f,s,15)).toFixed(3);
    });
    // dust and hair: 2-5 per frame
    const n=2+Math.floor(H(f,i,16)*4);
    o.du.forEach((el,s)=>{
      if(s>=n){ el.style.display="none"; return; }
      el.style.display="block";
      const x=H(f,s,17)*W, y=H(f,s,18)*Hh, r=H(f,s,19)*360, sc=0.6+H(f,s,20)*1.2;
      el.style.transform="translate("+x.toFixed(0)+"px,"+y.toFixed(0)+"px) rotate("+r.toFixed(0)+"deg) scale("+sc.toFixed(2)+")";
      el.style.opacity=(0.45+0.4*H(f,s,21)).toFixed(2);
    });
    // light leak: at most once per beat, 2 frames, amber from one edge
    const lf=o.leak;
    if(lf>=0 && (f===lf || f===lf+1)){
      const side={l:"0% 50%",r:"100% 50%",t:"50% 0%",b:"50% 100%"}[o.ls];
      o.lk.style.background="radial-gradient(ellipse 75% 85% at "+side+", rgba(200,116,29,1), rgba(200,116,29,.45) 40%, transparent 72%)";
      o.lk.style.opacity=(f===lf?0.25:0.17).toFixed(2);
    } else o.lk.style.opacity="0";
    // the scratched type boils: new turbulence seed every 3 frames
    const sd=(Math.floor(f/3)*7+i*13)%89+1;
    o.turb.forEach((el,j)=>el.setAttribute("seed", String(sd+j)));
  }
}
tl.to({}, {duration:__D__, ease:"none", onUpdate:function(){ frame(this.time()); }, onStart:function(){ frame(this.time()); }}, 0);
})();
"""


def engine(X):
    if getattr(X, "_ti_engine", False): return
    X._ti_engine = True
    X.tw(ENGINE.replace("__W__", str(X.W)).replace("__H__", str(X.H)).replace("__FPS__", str(X.fps)).replace("__D__", f"{max(1.0, X.duration or 60):.3f}"))


def _rng(X, cid, salt=0):
    seed = sum((k + 1) * ord(c) for k, c in enumerate(str(cid))) * 31 + salt + int(X.v.get("meta", {}).get("seed", 9)) * 7919
    return random.Random(seed)


# ---------------------------------------------------------------- hand marks (seeded geometry, build time)
def rough(r, x1, y1, x2, y2, amp=6.0, over=0.06):
    """a scratched stroke: overshoots both ends a little, bows once, wobbles."""
    dx, dy = x2 - x1, y2 - y1
    x1 -= dx * over * r.random(); y1 -= dy * over * r.random()
    x2 += dx * over * r.random(); y2 += dy * over * r.random()
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    b = r.uniform(-amp, amp)
    mx, my = (x1 + x2) / 2 + nx * b, (y1 + y2) / 2 + ny * b
    return f"M{x1:.1f} {y1:.1f} Q{mx:.1f} {my:.1f} {x2 + r.uniform(-amp, amp) * 0.3:.1f} {y2 + r.uniform(-amp, amp) * 0.3:.1f}"


def rough_circle(r, cx, cy, rad, turns=1.12, n=28, amp=0.035):
    pts = []
    a0 = r.uniform(-math.pi * 0.7, -math.pi * 0.4)
    for k in range(n + 1):
        a = a0 + 2 * math.pi * turns * k / n
        rr = rad * (1 + r.uniform(-amp, amp) + 0.04 * k / n)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for k in range(1, len(pts) - 1, 2):
        d += f" Q{pts[k][0]:.1f} {pts[k][1]:.1f} {pts[k + 1][0]:.1f} {pts[k + 1][1]:.1f}"
    return d


def boil_filter(cid, scale=4.0, freq=0.045):
    return (f'<svg width="0" height="0" style="position:absolute"><filter id="tib{cid}" x="-5%" y="-10%" width="110%" height="120%">'
            f'<feTurbulence class="boil" type="fractalNoise" baseFrequency="{freq}" numOctaves="2" seed="1" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{scale}" xChannelSelector="R" yChannelSelector="G"/></filter>'
            f'<filter id="tim{cid}" x="-5%" y="-5%" width="110%" height="110%">'
            f'<feTurbulence class="boil" type="fractalNoise" baseFrequency="0.08" numOctaves="1" seed="2" result="t"/>'
            f'<feDisplacementMap in="SourceGraphic" in2="t" scale="3" xChannelSelector="R" yChannelSelector="G"/></filter></svg>')


def digits(X, s, amber_tail=""):
    """a number as one <i class="dg"> per glyph (scratched in digit by digit); a unit tail can be amber."""
    out = []
    for ch in str(s):
        out.append(f'<i class="dg">{X.rich(ch)}</i>' if ch.strip() else " ")
    if amber_tail:
        out.append(f'<i class="dg am">{X.rich(amber_tail)}</i>')
    return "".join(out)


def hand_lines(X, lines, amber=""):
    """hand-scratched lines; the amber word (at most one) is coloured where it first appears."""
    out = []
    done = False
    for ln in lines:
        h = X.rich(ln)
        if amber and not done and amber in ln:
            a = ln.index(amber)
            h = X.rich(ln[:a]) + f'<span class="am">{X.rich(amber)}</span>' + X.rich(ln[a + len(amber):])
            done = True
        out.append(f'<span class="ln">{h}</span>')
    return "".join(out)


# ---------------------------------------------------------------- page + furniture + motion verbs
def leak_frame(X, cid, t, d):
    """the beat's one light leak (or none): a frame index well inside the beat, and the edge it comes from."""
    r = _rng(X, cid, 5)
    if r.random() < 0.25 or d < 1.6: return -1, "l"
    tt = t + d * r.uniform(0.35, 0.8)
    return int(round(tt * X.fps)), r.choice("lrtb")


def furniture(X, cid, b):
    P, W, H = X.portrait, X.W, X.H
    i, n = X.beat["i"], X.beat["n"]
    holes = "".join(f'<i style="top:{30 + 96 * k}px"></i>' for k in range(int(H / 96) + 1))
    r = _rng(X, cid, 11)
    kk = "  ".join(f"KN{r.randint(10, 99)} {r.randint(1000, 9999)} {r.randint(10, 99)}+{r.randint(0, 15):02d}" for _ in range(6))
    kh = (960 - 30) if P else (H - 60)
    slug = b.get("slug") or f"REEL 01 · {i + 1:02d}/{n:02d}"
    X.used_text.update(slug + "0123456789")
    kimg = ("url(&quot;data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='26' height='" + str(kh) + "'>"
            "<text transform='translate(6 0) rotate(90)' x='0' y='0' font-family='Courier New,monospace' font-size='20' letter-spacing='3.6' "
            "fill='rgb(232,226,210)' fill-opacity='.3'>" + kk.replace("+", "%2B") + "</text></svg>&quot;)")
    src = b.get("src", "")
    X._ti_kk = f'<div class="ti-kk" style="height:{kh}px;background-image:{kimg}"></div>'
    return (f'<div class="ti-edge">{holes}</div>'
            f'<div class="ti-slug">{X.rich(slug)}</div>'
            + (f'<div class="ti-src">{X.rich(src)}</div>' if src else ""))


def texture(X, cid, ghost_text=""):
    """below the safe area: a burned frame-edge glow, scratched tally marks and the hero's ghost."""
    P, W = X.portrait, X.W
    r = _rng(X, cid, 13)
    h = 420 if P else 120
    paths = []
    x = r.uniform(80, 160)
    y0 = h - (r.uniform(150, 230) if P else r.uniform(60, 90))
    for g in range(r.randint(3, 5)):
        for k in range(4):
            xx = x + k * 18
            paths.append(rough(r, xx, y0, xx + r.uniform(-4, 4), y0 + (70 if P else 46), 3))
        paths.append(rough(r, x - 10, y0 + (52 if P else 34), x + 66, y0 + (14 if P else 8), 3))
        x += r.uniform(110, 150)
    marks = "".join(f'<path d="{p}" stroke="rgba(232,226,210,.16)" stroke-width="3" fill="none"/>' for p in paths)
    gb = ""
    if ghost_text and P:
        gb = f'<div class="gb" data-layout-allow-overlap style="left:{r.uniform(-60, 140):.0f}px;top:{r.uniform(100, 170):.0f}px;font-size:{r.uniform(300, 380):.0f}px">{X.rich(ghost_text)}</div>'
    return (f'<div class="ti-tex"><div class="glow"></div>{gb}'
            f'<svg width="{W}" height="{h}" viewBox="0 0 {W} {h}">{marks}</svg></div>')


DUST = [
    '<svg width="8" height="8" viewBox="-4 -4 8 8"><circle r="2.6" fill="rgb(232,226,210)"/></svg>',
    '<svg width="10" height="10" viewBox="-5 -5 10 10"><path d="M-3 -1 Q0 -4 3 -1 Q4 2 0 3 Q-4 3 -3 -1Z" fill="rgb(232,226,210)"/></svg>',
    '<svg width="6" height="6" viewBox="-3 -3 6 6"><circle r="1.6" fill="rgb(232,226,210)"/></svg>',
    '<svg width="90" height="60" viewBox="0 0 90 60"><path d="M2 40 C20 10 40 58 58 26 S84 18 88 6" stroke="rgb(232,226,210)" stroke-width="1.4" fill="none"/></svg>',
    '<svg width="14" height="14" viewBox="-7 -7 14 14"><path d="M-5 -2 L2 -5 L5 1 L-1 5 Z" fill="rgb(232,226,210)"/></svg>',
]


def film_layers(X):
    """grain under the type, then the per-frame layers over it (scratches, dust, fine grain, exposure, leak, run-out)."""
    gr = "".join(f'<i style="background-image:{_q(g)}"></i>' for g in GRAIN)
    gr2 = "".join(f'<i style="background-image:{_q(g)}"></i>' for g in GRAIN_FINE)
    return (f'<div class="ti-gr">{gr}</div>',
            '<div class="ti-scr"><i></i><i></i><i></i></div>'
            f'<div class="ti-du">{"".join(DUST)}</div>'
            f'<div class="ti-gr2">{gr2}</div><div class="ti-ex"></div><div class="ti-lk"></div>'
            '<div class="ti-fline"></div><div class="ti-fl"></div>')


def page(X, b, cid, t, d, inner, ghost_text="", runout=True):
    """one beat of film: gate (grain, camera with the content, furniture), then the per-frame damage over it.
    Ends with the reel's run-out into the next beat: 2 frames of white-amber flare, 2 frames slipped 40 % with the frame line."""
    X.css("title", CSS)
    engine(X)
    i, n = X.beat["i"], X.beat["n"]
    lf, ls = leak_frame(X, cid, t, d)
    under, over = film_layers(X)
    furn = furniture(X, cid, b)
    html = (f'<div class="ti" data-i="{i}" data-t0="{t:.3f}" data-t1="{t + d:.3f}" data-leak="{lf}" data-ls="{ls}">'
            f'{boil_filter(cid)}<div class="ti-gate">{under}{X._ti_kk}<div class="ti-cam">{texture(X, cid, ghost_text)}{inner}</div>{furn}</div>{over}</div>')
    X.clip(cid, t, d, html, "scene", 2 + i, track=1 + i % 2, attrs="data-layout-allow-overflow")
    s = f"#{cid}"
    if runout and i < n - 1 and d > 0.6:
        f = 1 / X.fps
        te = t + d
        X.tw(f'tl.set("{s} .ti-fl", {{opacity:1}}, {te - 4 * f:.3f});')
        X.tw(f'tl.set("{s} .ti-fl", {{opacity:0.6}}, {te - 3 * f:.3f});')
        X.tw(f'tl.set("{s} .ti-fl", {{opacity:0}}, {te - 2 * f:.3f});')
        X.tw(f'tl.set("{s} .ti-cam", {{y:{X.H * 0.4:.0f}}}, {te - 2 * f:.3f});')
        X.tw(f'tl.set("{s} .ti-fline", {{display:"block", top:{X.H * 0.4 - 22:.0f}}}, {te - 2 * f:.3f});')
        X.tw(f'tl.set("{s} .ti-cam", {{y:{X.H * 0.43:.0f}}}, {te - f:.3f});')
        X.tw(f'tl.set("{s} .ti-fline", {{top:{X.H * 0.43 - 22:.0f}}}, {te - f:.3f});')
    return s


def scratch_in(X, sel, t, frames=10, stagger=0.0):
    """type is scratched in: a reveal along the glyph run, on 2s (frames/2 steps)."""
    dur = frames / X.fps
    st = f", stagger:{stagger:.3f}" if stagger else ""
    X.tw(f'tl.fromTo("{sel}", {{clipPath:"inset(-20% 100% -20% -10%)"}}, {{clipPath:"inset(-20% -30% -20% -10%)", duration:{dur:.3f}, ease:"steps({max(2, frames // 2)})"{st}, immediateRender:true}}, {t:.3f});')


def scratch_digits(X, sel, t, per=4):
    """digit by digit, each one scratched in over `per` frames on 2s."""
    dur = per / X.fps
    X.tw(f'tl.fromTo("{sel} .dg", {{clipPath:"inset(-20% 100% -20% -25%)"}}, {{clipPath:"inset(-20% -25% -20% -25%)", duration:{dur:.3f}, ease:"steps({max(2, per // 2)})", stagger:{dur:.3f}, immediateRender:true}}, {t:.3f});')


def draw(X, sel, t, dur, stagger=0.0):
    """scratched strokes (pathLength=1) drawn on 2s."""
    steps = max(2, round(dur * X.fps / 2))
    st = f", stagger:{stagger:.3f}" if stagger else ""
    X.tw(f'tl.fromTo("{sel}", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{dur:.3f}, ease:"steps({steps})"{st}, immediateRender:true}}, {t:.3f});')


def jump(X, sel, t, r, big=1.0):
    """flash frames before the hero settles: 2-3 snaps of position/scale, 1-2 frames each, one of them a negative."""
    f = 1 / X.fps
    a = (r.uniform(-120, -40) * big, r.uniform(-60, 60) * big, r.uniform(1.18, 1.32))
    b_ = (r.uniform(40, 110) * big, r.uniform(-50, 40) * big, r.uniform(0.82, 0.92))
    X.tw(f'tl.set("{sel}", {{x:{a[0]:.0f}, y:{a[1]:.0f}, scale:{a[2]:.2f}}}, {t:.3f});')
    X.tw(f'tl.set("{sel}", {{x:{b_[0]:.0f}, y:{b_[1]:.0f}, scale:{b_[2]:.2f}, filter:"invert(1)"}}, {t + 2 * f:.3f});')
    X.tw(f'tl.set("{sel}", {{x:{a[0] * 0.3:.0f}, y:{-a[1] * 0.4:.0f}, scale:1.06, filter:"none"}}, {t + 3 * f:.3f});')
    X.tw(f'tl.set("{sel}", {{x:0, y:0, scale:1}}, {t + 5 * f:.3f});')


def ghost_drift(X, sel, t, d, r):
    dx = r.choice([-1, 1]) * r.uniform(50, 80)
    X.tw(f'tl.fromTo("{sel}", {{x:{-dx:.0f}, y:{r.uniform(-20, 20):.0f}}}, {{x:{dx:.0f}, y:{r.uniform(-20, 20):.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def hero(X, cid, key, html, left, top, cls="", rot=0.0, extra=""):
    """the hero element with its double exposure: a second copy 140 % larger, 6 px blur, 12 %, drifting on its own."""
    return (f'<div class="gh gh-{key}" data-layout-allow-overlap data-layout-allow-occlusion style="left:{left:.0f}px;top:{top:.0f}px;transform:scale(1.4) rotate({rot:.2f}deg)">'
            f'<div style="position:relative">{html}</div></div>'
            f'<div class="hero hero-{key} {cls}" style="position:absolute;left:{left:.0f}px;top:{top:.0f}px;transform:rotate({rot:.2f}deg){extra}">'
            f'<div style="position:relative">{html}</div></div>')


def T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def tw_label(X, text, left, top, cls="", size=28, align="left", amber=""):
    X.used_text.update(text)
    lines = str(text).split("|")
    body = "<br>".join(_amber(X, ln, amber) for ln in lines)
    st = f"left:{left:.0f}px;" if align == "left" else f"right:{left:.0f}px;text-align:right;"
    return f'<div class="tw {cls}" style="{st}top:{top:.0f}px;font-size:{size}px">{body}</div>'


def _amber(X, ln, amber):
    if amber and amber in ln:
        a = ln.index(amber)
        return X.rich(ln[:a]) + f'<span class="am">{X.rich(amber)}</span>' + X.rich(ln[a + len(amber):])
    return X.rich(ln)


def rot_label(X, text):
    """the one element per beat turned 90°: a typewriter label running up the left edge (x 60–110, y 400–1400)."""
    X.used_text.update(text)
    if X.portrait:
        return f'<div class="tw rot" style="left:64px;top:1390px;font-size:28px">{X.rich(text)}</div>'
    return f'<div class="tw rot" style="left:62px;top:900px;font-size:28px">{X.rich(text)}</div>'


def label_in(X, s, t, sel=".tw"):
    """typewriter labels type on, a glyph per frame on 2s."""
    X.tw(f'tl.fromTo("{s} {sel}", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"steps(8)", stagger:0.2, immediateRender:true}}, {t:.3f});')


def numw(s, unit=0.0):
    """Permanent Marker advance widths (em) for a numeral run."""
    W = {"0": .687, "1": .322, "2": .65, "3": .562, "4": .582, "5": .58, "6": .501, "7": .576, "8": .537, "9": .529, ".": .229, "%": .644, ",": .204, ">": .5, "+": .55}
    return sum(W.get(c, 1.0) for c in str(s)) + unit


# ---------------------------------------------------------------- scenes
GLYPH = 0.72        # Permanent Marker digit height (em)
TOP = 0.146         # glyph top below the line box top (em), line-height 1
TRACK = -0.05       # hero numerals are set tight


def bignum(X, cid, text, glyph, avail, cls="", small_lead=False):
    """a hero numeral sized by its glyph height (px), condensed (scaleX) only as far as needed to fit `avail`.
    returns (html, font px, rendered width). small_lead: a leading '>' / '+' rides at .62em."""
    text = str(text)
    X.used_text.update(text)
    fs = glyph / GLYPH
    n = len(text)
    em = numw(text) + TRACK * (n - 1)
    lead = ""
    body = text
    if small_lead and text[:1] in ">+":
        em -= numw(text[0]) * 0.38
        lead = f'<i class="dg" style="font-size:.62em;vertical-align:.32em">{X.rich(text[0])}</i>'
        body = text[1:]
    nat = em * fs
    sx = min(1.0, avail / nat)
    html = (f'<div class="hs num {cls}" data-safe="ignore" data-layout-allow-overlap data-layout-allow-occlusion style="left:0;top:0;font-size:{fs:.0f}px;letter-spacing:{TRACK}em;'
            f'transform:scaleX({sx:.3f});transform-origin:0 0;filter:url(#tib{cid})">{lead}{digits(X, body)}</div>')
    return html, fs, nat * sx


def cross(b, X, t, d, cid):
    """hero number: the old value is scratched in large across the middle of the frame, struck out in red; on the
    jump cut it snaps up small into the corner and the new value is scratched in its place, bigger still; the unit
    (amber) lands last. Label in the opposite corner, a side label up the left edge."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    old, new, unit = str(b.get("old", "")), str(b.get("new", "")), b.get("unit", "")
    ou = b.get("old_unit", "")
    X.used_text.update(old + new + unit)
    if P:
        glyph = 460
        newh, fs, nw = bignum(X, cid, new, glyph, 894, "nv")
        nx, ny = 116, 470 - TOP * fs
        opx, ox, oy = 200, 118, 236
        big_o = (1.55, -40, 330)        # where the old value is first written: scale, dx, dy
        ux, uy, upx = 128, 470 + glyph + 10, 250
        lab = tw_label(X, b.get("label", ""), 140, 1190, align="right")
    else:
        glyph = 440
        newh, fs, nw = bignum(X, cid, new, glyph, 1060, "nv")
        nx, ny = 130, 330 - TOP * fs
        opx, ox, oy = 170, 150, 96
        big_o = (1.9, -20, 230)
        ux, uy, upx = nx + nw + 30, 330 + glyph - 260, 260
        lab = tw_label(X, b.get("label", ""), 110, 840, align="right")
    ow = numw(old[:len(old) - len(ou)]) * opx + (opx * 0.62 if ou else 0)
    strike = rough(r, -20, opx * 0.62, ow + 10, opx * 0.38, 8, 0.02)
    strike2 = rough(r, -4, opx * 0.74, ow - 10, opx * 0.55, 6, 0.02)
    oldh = (f'<div class="oldw" style="position:absolute;left:{ox}px;top:{oy}px;transform-origin:0 0">'
            f'<div class="hs num old" style="left:0;top:0;font-size:{opx}px;filter:url(#tib{cid});transform:rotate(-2deg)">{digits(X, old[:len(old) - len(ou)])}'
            f'<i class="dg" style="font-family:var(--f-display);font-size:.62em">{X.rich(ou)}</i></div>'
            f'<svg class="mk" width="{ow + 40:.0f}" height="{opx:.0f}" viewBox="-20 0 {ow + 40:.0f} {opx:.0f}" style="left:-20px;filter:url(#tim{cid})">'
            f'<path class="st" d="{strike}" stroke="{BLOOD}" stroke-width="14" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
            f'<path class="st" d="{strike2}" stroke="{BLOOD}" stroke-width="8" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg></div>')
    unith = f'<div class="hs un" style="left:{ux:.0f}px;top:{uy:.0f}px;font-size:{upx}px;filter:url(#tib{cid})"><span class="am">{X.rich(unit)}</span></div>'
    inner = (lab + rot_label(X, b.get("side", "")) + oldh
             + hero(X, cid, "n", newh, nx, ny, rot=-1.5) + unith)
    s = page(X, b, cid, t, d, inner, ghost_text=new)
    f = 1 / X.fps
    to = t + 3 * f
    tn = T(X, b, "at_new", t, t + d * 0.42)
    # written large across the middle first
    sc, dx, dy = big_o
    X.tw(f'tl.fromTo("{s} .oldw", {{scale:{sc}, x:{dx}, y:{dy}}}, {{scale:{sc}, x:{dx}, y:{dy}, duration:0.01, immediateRender:true}}, {t:.3f});')
    label_in(X, s, t + 0.2)
    scratch_digits(X, f"{s} .old", to, 4)
    ts = max(to + 0.9, min(tn - 0.6, to + 1.6))
    draw(X, f"{s} .oldw .st", ts, 0.3, 0.13)
    # the jump cut: the struck-out value snaps up into the corner, the new one is scratched in its place
    X.tw(f'tl.set("{s} .oldw", {{scale:{sc * 1.08:.2f}, x:{dx + 30}, y:{dy - 40}, filter:"invert(1)"}}, {tn - 3 * f:.3f});')
    X.tw(f'tl.set("{s} .oldw", {{scale:1, x:0, y:0, filter:"none"}}, {tn - f:.3f});')
    jump(X, f"{s} .hero-n", tn - 0.05, r)
    scratch_digits(X, f"{s} .hero-n", tn, 4)
    scratch_digits(X, f"{s} .gh-n", tn, 4)
    tu = tn + len(new) * 4 / X.fps + 0.05
    scratch_in(X, f"{s} .un", tu, 8)
    ghost_drift(X, f"{s} .gh-n", t, d, r)


def strip(b, X, t, d, cid):
    """timeline: a strip of film frames runs up through the gate on 2s and registers; each frame carries its quarter
    and value (with a hatched length in true ratio); the key frame is taller, burns brighter and gets a scratched note."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    items = b.get("items", [])[:5]
    n = len(items)
    key = int(b.get("key", n - 1))
    vmax = max(float(it.get("value", 0)) for it in items) or 1
    if P:
        sx, sw, y0 = 130, 820, 300
        hs = [205] * n; hs[key] = 340
        vp, kvp = 150, 240
    else:
        sx, sw, y0 = 860, 780, 96
        hs = [178] * n; hs[key] = 300
        vp, kvp = 130, 210
    X.css("ti-strip", """
.ti .strip { position:absolute; }
.ti .strip .rail { position:absolute; top:-2000px; bottom:-2000px; width:46px; background:#141210; }
.ti .strip .rail i { position:absolute; left:12px; width:22px; height:30px; border-radius:4px; background:rgba(232,226,210,.32); }
.ti .strip .fr { position:absolute; left:46px; right:46px; background:#15130f; box-shadow:inset 0 0 0 2px rgba(232,226,210,.14); overflow:hidden; }
.ti .strip .fr .q { position:absolute; right:22px; top:14px; font-family:var(--f-mono); font-size:28px; letter-spacing:.3em; color:#e8e2d2; text-shadow:1px 0 0 rgba(232,226,210,.34); }
.ti .strip .fr .v { position:absolute; left:22px; font-family:var(--f-num); line-height:1; color:#e8e2d2; white-space:nowrap; letter-spacing:-.03em; }
.ti .strip .fr .v small { font-family:var(--f-display); font-size:.5em; margin-left:.1em; letter-spacing:0; }
.ti .strip .fr svg { position:absolute; left:0; top:0; overflow:visible; }
.ti .strip .fr .kn { position:absolute; font-family:var(--f-display); font-size:66px; line-height:1.05; color:#0b0a09; display:none; }
.ti .strip .fr.key .kn { display:block; }
.ti .strip .fr.key { background:radial-gradient(ellipse 80% 90% at 45% 50%, #f4ecda, #e6d3ad 60%, #c8741d 125%); box-shadow:0 0 44px rgba(232,226,210,.32); }
.ti .strip .fr.key .q, .ti .strip .fr.key .v { color:#0b0a09; text-shadow:none; }
""")
    fw = sw - 92
    frs = ""
    top = 0
    tops = []
    for k, it in enumerate(items):
        v = float(it.get("value", 0))
        lab = str(it.get("label", v))
        X.used_text.update(it.get("q", "") + lab + it.get("unit", ""))
        kk = k == key
        fh = hs[k]
        vpx = kvp if kk else vp
        hx = 22; hy = fh - 44; hl = (fw - 60) * v / vmax
        col = BLACK if kk else BONE
        hatch = "".join(f'<path d="{rough(r, hx + j * 12, hy + 24, hx + j * 12 + 14, hy, 1.5, 0.0)}" stroke="{col}" stroke-width="3" opacity="{0.85 if kk else 0.6}"/>'
                        for j in range(int(hl / 12)))
        note = ""
        if kk:
            nl = str(b.get("note", "")).split("|")
            X.used_text.update("".join(nl))
            vw = (numw(lab) - 0.03 * len(lab)) * vpx + vpx * 0.55 + 22
            nx_, ny_ = min(fw - 150, vw + 40), fh * 0.2
            ring = rough_circle(r, nx_ + 66, ny_ + 70, 98, 1.15, 24, 0.06)
            note = (f'<div class="kn" style="left:{nx_:.0f}px;top:{ny_:.0f}px">{"<br>".join(X.rich(x) for x in nl)}</div>'
                    f'<svg class="mk kr" width="{fw}" height="{fh}" style="filter:url(#tim{cid})"><path d="{ring}" stroke="{BLOOD}" stroke-width="9" fill="none" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
        frs += (f'<div class="fr{" kf key" if kk else ""}" data-k="{k}" style="top:{top + 8}px;height:{fh - 16}px">'
                f'<div class="q">{X.rich(it.get("q", ""))}</div>'
                f'<div class="v" style="top:{(fh - 16 - 44) / 2 - vpx * 0.5 + 6:.0f}px;font-size:{vpx}px">{X.rich(lab)}<small>{X.rich(it.get("unit", ""))}</small></div>'
                f'<svg class="ht" width="{fw}" height="{fh}">{hatch}</svg>{note}</div>')
        tops.append(top)
        top += fh
    tot = top
    holes = "".join(f'<i style="top:{k * 80 + 2000}px"></i>' for k in range(-26, 40))
    body = (f'<div class="rail" style="left:0">{holes}</div><div class="rail" style="right:0">{holes}</div>{frs}')
    ghost = f'<div class="gh gh-s" data-layout-allow-overlap data-layout-allow-occlusion style="left:{sx}px;top:{y0}px;width:{sw}px;height:{tot}px;transform:scale(1.4)"><div class="strip" style="left:0;top:0;width:{sw}px;height:{tot}px">{body.replace("pathLength", "data-pl")}</div></div>'
    stripm = f'<div class="strip st-m" style="left:{sx}px;top:{y0}px;width:{sw}px;height:{tot}px">{body}</div>'
    lab = tw_label(X, b.get("label", ""), 140 if P else 110, 250 if P else 860, align="right" if P else "left")
    inner = lab + rot_label(X, b.get("side", "")) + ghost + stripm
    s = page(X, b, cid, t, d, inner, ghost_text=str(items[key].get("label", "")) if items else "")
    tk = T(X, b, "at_key", t, t + d * 0.45)
    # the strip runs up through the gate on 2s (already in the frame at the cut), overshoots, registers;
    # then the key frame burns (effect) and the note is scratched on it
    run = 0.7
    X.tw(f'tl.fromTo("{s} .st-m", {{y:{H * 0.42:.0f}}}, {{y:{-60:.0f}, duration:{run:.2f}, ease:"steps({round(run * 15)})", immediateRender:true}}, {t:.3f});')
    X.tw(f'tl.to("{s} .st-m", {{y:0, duration:0.14, ease:"steps(2)"}}, {t + run:.3f});')
    X.tw(f'tl.fromTo("{s} .gh-s", {{y:{H * 0.3:.0f}}}, {{y:{-60:.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .st-m .fr.kf", {{attr:{{class:"fr kf"}}}}, {t:.3f});')
    X.tw(f'tl.set("{s} .st-m .fr.kf", {{attr:{{class:"fr kf key"}}}}, {tk:.3f});')
    X.tw(f'tl.set("{s} .st-m .fr.kf .ht path", {{attr:{{stroke:"{BONE}"}}}}, {t:.3f});')
    X.tw(f'tl.set("{s} .st-m .fr.kf .ht path", {{attr:{{stroke:"{BLACK}"}}}}, {tk:.3f});')
    jump(X, f"{s} .st-m .fr.kf .v", tk, r, 0.5)
    scratch_in(X, f"{s} .st-m .kn", tk + 0.25, 10)
    draw(X, f"{s} .st-m .kr path", tk + 0.65, 0.4)
    label_in(X, s, t + 0.2, ".tw:not(.rot)")


def tally(b, X, t, d, cid):
    """tally: marks scratched in groups of five, one mark per stated unit, several per 2-frame step;
    the total is then scratched in at hero scale, digit by digit, its unit amber."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    n = int(b.get("count", 10))
    total, unit = str(b.get("total", "")), b.get("unit", "")
    X.used_text.update(total + unit)
    if P:
        cols, gw, gh, mh, fx0, fy0 = 3, 260, 152, 118, 140, 840
        glyph = 440
        toth, fs, tw_ = bignum(X, cid, total, glyph, 700, "tot")
        tx, ty = 116, 330 - TOP * fs
        ux, uy, upx = 116 + tw_ + 14, 330 + glyph - 230, 200
        lab = tw_label(X, b.get("label", "").replace("|", " · "), 80, 254, align="right", amber=b.get("amber", ""))
    else:
        cols, gw, gh, mh, fx0, fy0 = 4, 225, 225, 160, 990, 200
        glyph = 420
        toth, fs, tw_ = bignum(X, cid, total, glyph, 720, "tot")
        tx, ty = 120, 300 - TOP * fs
        ux, uy, upx = 120 + tw_ - 160, 300 + glyph + 10, 200
        lab = tw_label(X, b.get("label", ""), 120, 860, align="right", amber=b.get("amber", ""))
    paths = []
    for k in range(n):
        g = k // 5; j = k % 5
        gx, gy = fx0 + (g % cols) * gw, fy0 + (g // cols) * gh
        if j < 4:
            x = gx + 20 + j * 36 + r.uniform(-4, 4)
            paths.append(rough(r, x, gy + r.uniform(-5, 5), x + r.uniform(-10, 10), gy + mh + r.uniform(-6, 6), 5))
        else:
            paths.append(rough(r, gx - 6, gy + mh * 0.8, gx + 160, gy + mh * 0.2, 7))
    def svg(cls):
        return (f'<svg class="mk {cls}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
                + "".join(f'<path class="tm" d="{p}" stroke="{BONE}" stroke-width="{r.uniform(7, 10):.1f}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>' for p in paths) + '</svg>')
    unith = f'<div class="hs un" style="left:{ux:.0f}px;top:{uy:.0f}px;font-size:{upx}px;filter:url(#tib{cid})"><span class="am">{X.rich(unit)}</span></div>'
    field_w = cols * gw
    inner = (lab + rot_label(X, b.get("side", "")) + f'<div class="gh gh-t" data-layout-allow-overlap data-layout-allow-occlusion style="left:0;top:0;transform:scale(1.4);transform-origin:{fx0 + field_w / 2:.0f}px {fy0 + 200}px">{svg("g")}</div>'
             + svg("m") + hero(X, cid, "t", toth, tx, ty) + unith)
    s = page(X, b, cid, t, d, inner, ghost_text=total)
    t0 = t + 0.1
    per = 2 / X.fps
    for g in ("m", "g"):
        X.tw(f'tl.fromTo("{s} .mk.{g} .tm", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{per:.3f}, ease:"steps(1)", stagger:(k)=>Math.floor(k/4)*{per:.4f}, immediateRender:true}}, {t0:.3f});')
    mend = t0 + (n + 3) // 4 * per
    tt = mend + 0.12
    jump(X, f"{s} .hero-t", tt - 0.03, r, 0.6)
    scratch_digits(X, f"{s} .hero-t", tt, 4)
    scratch_in(X, f"{s} .un", tt + len(total) * 4 / X.fps, 8)
    label_in(X, s, t + 0.3, ".tw:not(.rot)")
    X.tw(f'tl.fromTo("{s} .gh-t", {{x:-40}}, {{x:50, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def quote(b, X, t, d, cid):
    """statement: the source's own sentence, hand-scratched in lines (one amber word, a red underline scratch),
    the original typed small in the opposite corner."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    lines = b.get("lines", [])
    am = b.get("amber", "")
    if P:
        px, x0, y0, lh = 200, 100, 360, 1.16
        orig = tw_label(X, b.get("orig", ""), 140, 1080, align="right", size=28)
    else:
        px, x0, y0, lh = 190, 140, 160, 1.12
        orig = tw_label(X, b.get("orig", ""), 110, 700, align="right", size=28)
    X.used_text.update("".join(lines))
    hh = f'<div class="hs q" style="left:0;top:0;font-size:{px}px;line-height:{lh};filter:url(#tib{cid})">{hand_lines(X, lines, am)}</div>'
    # the underline scratch under the amber word
    ul = ""
    for k, ln in enumerate(lines):
        if am and am in ln:
            a = ln.index(am)
            ux0 = x0 + a * px; ux1 = ux0 + len(am) * px
            uy = y0 + (k + 1) * px * lh - px * 0.06
            ul = (f'<svg class="mk ul" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
                  f'<path d="{rough(r, ux0 - 10, uy, ux1 + 20, uy - 14, 6, 0.03)}" stroke="{BLOOD}" stroke-width="14" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                  f'<path d="{rough(r, ux0 + 10, uy + 18, ux1 - 10, uy + 8, 4, 0.03)}" stroke="{BLOOD}" stroke-width="8" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
            break
    inner = orig + rot_label(X, b.get("side", "")) + hero(X, cid, "q", hh, x0, y0, rot=-2.2) + ul
    s = page(X, b, cid, t, d, inner, ghost_text=lines[0] if lines else "")
    tq = T(X, b, "at_q", t, t + 0.12)
    jump(X, f"{s} .hero-q", tq - 0.03, r, 0.7)
    scratch_in(X, f"{s} .hero-q .ln", tq, 12, 0.36)
    scratch_in(X, f"{s} .gh-q .ln", tq, 12, 0.36)
    tu = T(X, b, "at_em", t, tq + 0.42 * len(lines) + 0.2)
    draw(X, f"{s} .ul path", max(tq + 0.5, tu), 0.3, 0.1)
    label_in(X, s, tq + 0.5, ".tw:not(.rot)")
    ghost_drift(X, f"{s} .gh-q", t, d, r)


def bars(b, X, t, d, cid):
    """comparison: two hand-scratched bars of hatching, lengths in true ratio, drawn stroke by stroke;
    the figure scratched at each bar's end; the change (amber, hero scale) lands last."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    items = b.get("items", [])[:2]
    vmax = max(float(it["value"]) for it in items) or 1
    X.used_text.update(b.get("change", ""))
    if P:
        bx, bl, bh, ys, fpx = 110, 480, 96, (880, 1080), 112
        glyph = 440
        chgh, fs, cw = bignum(X, cid, b.get("change", ""), glyph, 894, "chg am")
        cx, cy = 116, 330 - TOP * fs
        lab = tw_label(X, b.get("label", ""), 140, 1196, align="right")
    else:
        bx, bl, bh, ys, fpx = 160, 600, 110, (330, 560), 112
        glyph = 420
        chgh, fs, cw = bignum(X, cid, b.get("change", ""), glyph, 760, "chg am")
        cx, cy = 1080, 330 - TOP * fs
        lab = tw_label(X, b.get("label", ""), 110, 140, align="right")
    out, gho = [], []
    hcounts = []
    for k, it in enumerate(items):
        L = bl * float(it["value"]) / vmax
        y = ys[k]
        X.used_text.update(it.get("year", "") + str(it.get("label", "")))
        hatch = []
        x = bx
        while x < bx + L - 6:
            hatch.append(rough(r, x + r.uniform(-2, 2), y + bh + r.uniform(-4, 4), x + 30 + r.uniform(-4, 4), y + r.uniform(-4, 4), 2.5, 0.04))
            x += r.uniform(13, 17)
        hcounts.append(len(hatch))
        frame = [rough(r, bx, y, bx + L, y + r.uniform(-4, 4), 3, 0.03), rough(r, bx + L, y, bx + L + r.uniform(-3, 3), y + bh, 3, 0.05),
                 rough(r, bx + L, y + bh, bx, y + bh + r.uniform(-4, 4), 3, 0.03)]
        def svg_(cls):
            return (f'<svg class="mk bar b{k} {cls}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
                    + "".join(f'<path class="hb" d="{p}" stroke="{BONE}" stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>' for p in hatch)
                    + "".join(f'<path class="fb" d="{p}" stroke="{BONE}" stroke-width="7" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>' for p in frame)
                    + '</svg>')
        out.append(svg_("m"))
        gho.append(svg_("g"))
        out.append(f'<div class="hs num fig f{k}" style="left:{bx + L + 24:.0f}px;top:{y + bh / 2 - fpx * 0.55:.0f}px;font-size:{fpx}px;filter:url(#tib{cid})">{digits(X, it["label"])}</div>')
        out.append(tw_label(X, it.get("year", ""), bx, y - 50, cls=f"yr y{k}"))
    inner = (lab + rot_label(X, b.get("side", "")) + f'<div class="gh gh-b" data-layout-allow-overlap data-layout-allow-occlusion style="left:0;top:0;transform:scale(1.4);transform-origin:{bx + bl / 2:.0f}px {ys[0] + 150}px">{"".join(gho)}</div>'
             + "".join(out) + hero(X, cid, "c", chgh, cx, cy, rot=-1.5))
    s = page(X, b, cid, t, d, inner, ghost_text=str(items[-1]["label"]) if items else "")
    label_in(X, s, t + 0.1, ".tw:not(.rot)")
    tk = t + 0.1
    for k, it in enumerate(items):
        draw(X, f"{s} .bar.b{k} .fb", tk, 0.2, 0.067)
        X.tw(f'tl.fromTo("{s} .bar.b{k} .hb", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{2 / X.fps:.3f}, ease:"steps(1)", stagger:(j)=>Math.floor(j/2)*{2 / X.fps:.4f}, immediateRender:true}}, {tk + 0.1:.3f});')
        tf = tk + 0.1 + (hcounts[k] + 1) // 2 * 2 / X.fps + 0.05
        scratch_digits(X, f"{s} .fig.f{k}", tf, 4)
        tend = tf + len(str(it["label"])) * 4 / X.fps
        tk = tk + 0.6
    tc = min(max(T(X, b, "at_change", t, t + d * 0.6), tend + 0.1), t + d - 1.0)
    jump(X, f"{s} .hero-c", tc - 0.03, r, 0.6)
    scratch_digits(X, f"{s} .hero-c", tc, 4)
    X.tw(f'tl.fromTo("{s} .gh-b", {{x:-50}}, {{x:40, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def circle(b, X, t, d, cid):
    """share: a hand-drawn circle; the share is hatched in on 2s, stroke by stroke (each stroke counted in);
    only when the hatching is done is the figure scratched in at hero scale; then a red scratch underlines it."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    pct = float(b.get("pct", 50))
    big = str(b.get("big", f"{pct:g}%"))
    if P:
        cx, cy, rad = 690, 1050, 240
        glyph = 440
        numh, fs, nw = bignum(X, cid, big, glyph, 820, "pc", small_lead=True)
        nx, ny = 116, 330 - TOP * fs
        lab = tw_label(X, b.get("label", ""), 120, 880, amber=b.get("amber", ""))
    else:
        cx, cy, rad = 1460, 560, 300
        glyph = 420
        numh, fs, nw = bignum(X, cid, big, glyph, 900, "pc", small_lead=True)
        nx, ny = 120, 330 - TOP * fs
        lab = tw_label(X, b.get("label", ""), 140, 160, amber=b.get("amber", ""))
    a1 = -90 + 360 * pct / 100
    def pt(a, rr=rad): return cx + rr * math.cos(math.radians(a)), cy + rr * math.sin(math.radians(a))
    x1, y1 = pt(-90); x2, y2 = pt(a1)
    wedge = f"M{cx},{cy} L{x1:.1f},{y1:.1f} A{rad},{rad} 0 {1 if pct > 50 else 0} 1 {x2:.1f},{y2:.1f} Z"
    hatch = []
    k = -rad * 0.2
    while k < rad * 2.2:          # only the strokes that can cross the right-hand wedge
        xa, ya = cx + k - rad, cy + rad
        hatch.append(rough(r, xa, ya + 20, xa + 2 * rad * 0.9, ya - 2 * rad - 20, 4, 0.0))
        k += 20
    circ = rough_circle(r, cx, cy, rad)
    edge = [rough(r, cx, cy, x1, y1, 4, 0.04), rough(r, cx, cy, x2, y2, 4, 0.04)]
    def svg_(cls, pre):
        return (f'<svg class="mk ci {cls}" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
                f'<defs><clipPath id="{pre}w{cid}"><path d="{wedge}"/></clipPath></defs>'
                f'<path class="cr" d="{circ}" stroke="{BONE}" stroke-width="9" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>'
                f'<g clip-path="url(#{pre}w{cid})">' + "".join(f'<path class="ht" d="{p}" stroke="{BONE}" stroke-width="6" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>' for p in hatch) + '</g>'
                + "".join(f'<path class="ed" d="{p}" stroke="{BONE}" stroke-width="7" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>' for p in edge) + '</svg>')
    uy = 330 + glyph + 34
    ul = (f'<svg class="mk ul" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
          f'<path d="{rough(r, nx + 20, uy, nx + nw - 10, uy - 18, 6, 0.03)}" stroke="{BLOOD}" stroke-width="14" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
    inner = (lab + rot_label(X, b.get("side", "")) + f'<div class="gh gh-c" data-layout-allow-overlap data-layout-allow-occlusion style="left:0;top:0;transform:scale(1.4);transform-origin:{cx}px {cy}px">{svg_("g", "g")}</div>'
             + svg_("m", "m") + hero(X, cid, "p", numh, nx, ny) + ul)
    s = page(X, b, cid, t, d, inner, ghost_text=big)
    f2 = 2 / X.fps
    draw(X, f"{s} .ci .cr", t + 0.1, 0.5)
    th = T(X, b, "at_hatch", t, t + 0.75)
    draw(X, f"{s} .ci .ed", th - 0.15, 0.13, 0.067)
    X.tw(f'tl.fromTo("{s} .ci .ht", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{f2:.3f}, ease:"steps(1)", stagger:(j)=>Math.floor(j/2)*{f2:.4f}, immediateRender:true}}, {th:.3f});')
    hend = th + (len(hatch) + 1) // 2 * f2
    tp = max(T(X, b, "at_big", t, hend), hend + 0.1)
    jump(X, f"{s} .hero-p", tp - 0.03, r, 0.6)
    scratch_digits(X, f"{s} .hero-p", tp, 4)
    tl_ = max(T(X, b, "at_mark", t, tp + 1.2), tp + len(big) * 4 / X.fps + 0.3)
    draw(X, f"{s} .ul path", tl_, 0.3)
    label_in(X, s, t + 0.15, ".tw:not(.rot)")
    X.tw(f'tl.fromTo("{s} .gh-c", {{x:45, y:-20}}, {{x:-45, y:20, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


def end(b, X, t, d, cid):
    """the last statement: a hand-scratched word ringed in red, the facts typed beside it; a flash-frame
    re-position, then the facts' last line is underlined in red; the placeholder channel slug at the foot."""
    P, W, H = X.portrait, X.W, X.H
    r = _rng(X, cid)
    word = b.get("word", "")
    X.used_text.update(word)
    if P:
        px, x0, y0 = 420, 110, 560
        facts = tw_label(X, b.get("facts", ""), 80, 270, align="right", amber=b.get("amber", ""))
        ch = tw_label(X, b.get("channel", "示例频道"), 120, 1196, size=30)
        nl = len(str(b.get("facts", "")).split("|"))
        fy = 270 + nl * 28 * 1.45 + 4
        fx1, fx0 = W - 80, W - 80 - 420
    else:
        px, x0, y0 = 380, 160, 300
        facts = tw_label(X, b.get("facts", ""), 120, 200, align="right", amber=b.get("amber", ""))
        ch = tw_label(X, b.get("channel", "示例频道"), 120, 820, align="right", size=30)
        nl = len(str(b.get("facts", "")).split("|"))
        fy = 200 + nl * 28 * 1.45 + 4
        fx1, fx0 = W - 120, W - 120 - 420
    ww = len(word) * px
    ring = rough_circle(r, x0 + ww / 2, y0 + px * 0.52, ww * 0.56, 1.18, 30, 0.05)
    ringsvg = (f'<svg class="mk rg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
               f'<g transform="translate({x0 + ww / 2:.0f} {y0 + px * 0.52:.0f}) scale(1 0.55) translate({-(x0 + ww / 2):.0f} {-(y0 + px * 0.52):.0f})">'
               f'<path d="{ring}" stroke="{BLOOD}" stroke-width="18" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" vector-effect="non-scaling-stroke"/></g></svg>')
    fu = (f'<svg class="mk fu" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="filter:url(#tim{cid})">'
          f'<path d="{rough(r, fx0, fy + 6, fx1, fy - 6, 4, 0.03)}" stroke="{BLOOD}" stroke-width="9" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>')
    hh = f'<div class="hs w" style="left:0;top:0;font-size:{px}px;filter:url(#tib{cid})">{X.rich(word)}</div>'
    inner = facts + ch + rot_label(X, b.get("side", "")) + hero(X, cid, "w", hh, x0, y0, rot=-2.5) + ringsvg + fu
    s = page(X, b, cid, t, d, inner, ghost_text=word, runout=False)
    label_in(X, s, t + 0.1, ".tw:not(.rot)")
    tw_ = T(X, b, "at_word", t, t + 0.15)
    jump(X, f"{s} .hero-w", tw_ - 0.03, r)
    scratch_in(X, f"{s} .hero-w .hs", tw_, 12)
    scratch_in(X, f"{s} .gh-w .hs", tw_, 12)
    draw(X, f"{s} .rg path", tw_ + 0.55, 0.5)
    jump(X, f"{s} .hero-w", tw_ + 1.9, r, 0.5)
    draw(X, f"{s} .fu path", tw_ + 3.0, 0.3)
    ghost_drift(X, f"{s} .gh-w", t, d, r)


SCENES = {"cross": cross, "strip": strip, "tally": tally, "quote": quote, "bars": bars, "circle": circle, "end": end}


# ---------------------------------------------------------------- shared effects in this style
STYLE["fx_themes"] = {
    "paper": {"bg": BLACK, "fg": BONE, "muted": "#a8a293", "accent": AMBER, "card": LIFT, "card-fg": BONE, "line": "rgba(232,226,210,.25)"},
    "ink":   {"bg": "#070606", "fg": BONE, "muted": "#9c968a", "accent": AMBER, "card": "#161412", "card-fg": BONE, "line": "rgba(232,226,210,.2)"},
    "red":   {"bg": "#1a0806", "fg": BONE, "muted": "#b39d93", "accent": AMBER, "card": "#2a100c", "card-fg": BONE, "line": "rgba(232,226,210,.22)"},
    "lemon": {"bg": "#17110a", "fg": BONE, "muted": "#b0a48c", "accent": AMBER, "card": "#241b10", "card-fg": BONE, "line": "rgba(232,226,210,.22)"},
}

FX_CSS = r"""
/* effects shown in this style: film-black ground with grain; headlines in the scratched hand, small type on the typewriter */
#root.st-title .fx { background-image:linear-gradient(color-mix(in srgb, var(--bg) 80%, transparent), color-mix(in srgb, var(--bg) 80%, transparent)), __GRAIN__ !important; background-size:100% 100%, 256px 256px !important; }
#root.st-title .fx .big { font-family:var(--f-display) !important; font-weight:400 !important; text-shadow:0 0 5px rgba(232,226,210,.22); }
#root.st-title .fx .sub { font-family:var(--f-mono); letter-spacing:.3em; }
#root.st-title .fx, #root.st-title .fx * { border-radius:0 !important; font-synthesis:none; }
.ctx.tix .hd { left:80px; right:80px; top:40px; border:none; height:auto; display:flex; justify-content:space-between; font-family:var(--f-mono); font-size:24px;
  letter-spacing:.3em; color:rgba(232,226,210,.82); text-shadow:1px 0 0 rgba(232,226,210,.32); }
.ctx.tix .hd b { font-weight:400; } .ctx.tix .hd span { opacity:1; }
.ctx.tix .hd .fxid { background:none; color:rgba(232,226,210,.4); font-size:20px; padding:0; }
.ctx.tix .cap { left:0; right:0; bottom:110px; text-align:left; padding-left:110px; padding-right:130px; }
.ctx.tix .cap > span { font-size:44px !important; font-family:var(--f-cap); font-weight:500; letter-spacing:.12em; color:#e8e2d2; background:rgba(26,24,22,.92);
  box-shadow:0 0 6px 3px rgba(26,24,22,.92); border-radius:0; padding:7px 20px 9px; }
.ctx.tix .cap .em .emt { background:none; color:#c8741d; padding:0; }
.ctx.tix .ft { left:80px; right:80px; bottom:40px; font-family:var(--f-mono); font-size:22px; letter-spacing:.16em; opacity:.8; color:#e8e2d2; }
.ctx.tix .edge { position:absolute; left:0; top:0; bottom:0; width:34px; background:#131110; filter:blur(1.2px); }
.ctx.tix .edge i { position:absolute; left:6px; width:22px; height:30px; border-radius:4px; background:rgba(232,226,210,.42); }
#root.v .ctx.tix .hd { left:72px; right:60px; top:204px; }
#root.v .ctx.tix .cap { top:auto; bottom:520px; padding:0 130px 0 110px; }
#root.v .ctx.tix .cap > span { font-size:44px !important; }
#root.v .ctx.tix .ft { left:72px; right:120px; top:1452px; bottom:auto; flex-direction:column; align-items:flex-start; gap:6px; font-size:24px; }
"""
STYLE["css"] = CSS + FX_CSS.replace("__GRAIN__", GRAIN[0].replace("width='256'", "width='256'"))


def FX_FRAME(X, cid, t, d, p, parts):
    """the page around a shared effect in this style: the film edge, typewriter slug, the subtitle strip and typed source;
    then the same per-frame film damage (grain, scratches, dust, weave, breathing exposure) laid over the effect."""
    X.css("title", CSS)
    engine(X)
    H = X.H
    holes = "".join(f'<i style="top:{30 + 96 * k}px"></i>' for k in range(int(H / 96) + 1))
    src = f'<div>{parts["src"]}</div>' if parts["src"] else ""
    inner = (f'<div class="edge">{holes}</div>'
             f'<div class="hd"><div><b>REEL 01</b><span> · {parts["topic"]}</span></div><div class="fxid">{parts["fxid"]}</div></div>'
             f'<div class="cap"><span style="font-size:{min(40, parts["cap_px"])}px">{parts["cap"]}</span></div>'
             f'<div class="ft"><div>{parts["foot"]}</div>{src}</div>')
    X.used_text.update("REEL 01 · ")
    X.clip(f"{cid}c", t, d, inner, "ctx tix", 30, track=20, sty=parts["sty"])
    # the film over the effect: a transparent .ti page carrying only the damage layers
    i = X.beat["i"] if hasattr(X, "beat") else 0
    lf, ls = leak_frame(X, cid, t, d)
    gr2 = "".join(f'<i style="background-image:{_q(g)}"></i>' for g in GRAIN_FINE)
    grh = "".join(f'<i style="background-image:{_q(g)}"></i>' for g in GRAIN)
    film = (f'<div class="ti tifx" data-i="{i}" data-t0="{t:.3f}" data-t1="{t + d:.3f}" data-leak="{lf}" data-ls="{ls}" style="background:transparent">'
            f'<div class="ti-gate"><div class="ti-gr" style="opacity:.16">{grh}</div></div>'
            f'<div class="ti-scr"><i></i><i></i><i></i></div><div class="ti-du">{"".join(DUST)}</div>'
            f'<div class="ti-gr2">{gr2}</div><div class="ti-ex"></div><div class="ti-lk"></div></div>')
    X.clip(f"{cid}f", t, d, film, "ov-film", 29, track=21)
    s = f"#{cid}c"
    X.tw(f'tl.fromTo("{s} .hd", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"steps(8)", immediateRender:true}}, {t + 0.05:.3f});')
