"""shared pieces for the screen effects (scroll_shot · screencast · spotlight · code); files starting with _ are not effects.

area()      content box under the page header and above the caption pill
stage()     an untimed root layer shown only during the beat: timed <video> may not sit inside a timed clip, so the
            moving picture, its device frame and everything that rides on it live here (one element to move = one camera)
prep()      a still sized for the browser: very tall screenshots are scaled to ≤ 16k px (Chrome's texture limit) and cached
frame()     device chrome around a viewport: browser (tab + address bar) · phone (bezel + island) · none
vtag()      the timed <video> for a viewport (cover)
cursor()    the pointer, drawn in viewport space so it scales with the zoom
pt()        a point/box given as 0–1 fractions or source pixels → viewport pixels
"""
import hashlib
from pathlib import Path
from h9 import fit
from h9.aefx import THEMES, _cap_clear

CSS = r"""
.scr-root { pointer-events:none; }
.scr-frame { position:absolute; transform-origin:50% 50%; }
.scr-frame.browser { background:var(--scr-chrome); border-radius:14px; box-shadow:0 0 0 1px var(--scr-edge), 0 30px 80px rgba(0,0,0,.35), 0 8px 20px rgba(0,0,0,.18); overflow:hidden; }
.scr-frame.browser .scr-bar { position:absolute; left:0; right:0; top:0; height:var(--scr-barh); display:flex; align-items:center; gap:10px; padding:0 16px; }
.scr-frame.browser .scr-dots { display:flex; gap:8px; flex:none; } .scr-frame.browser .scr-dots i { width:12px; height:12px; border-radius:50%; background:var(--scr-dot); }
.scr-frame.browser .scr-dots i:nth-child(1) { background:#ff5f57; } .scr-frame.browser .scr-dots i:nth-child(2) { background:#febc2e; } .scr-frame.browser .scr-dots i:nth-child(3) { background:#28c840; }
.scr-frame.browser .scr-url { flex:1; min-width:0; height:30px; border-radius:8px; background:var(--scr-field); color:var(--scr-ink); display:flex; align-items:center; gap:8px; padding:0 12px;
  font:500 15px var(--f-mono, monospace); white-space:nowrap; overflow:hidden; }
.scr-frame.browser .scr-url b { color:var(--scr-dim); font-weight:500; }
.scr-frame.browser .scr-tab { flex:none; max-width:30%; font:600 14px var(--f-body); color:var(--scr-ink); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.scr-frame.phone { background:#0b0c0e; border-radius:var(--scr-r); box-shadow:0 0 0 2px #2b2d31, 0 0 0 5px #0b0c0e, 0 34px 90px rgba(0,0,0,.42); }
.scr-frame.phone .scr-isl { position:absolute; left:50%; top:calc(var(--scr-pad) + 12px); width:30%; height:26px; margin-left:-15%; border-radius:14px; background:#000; z-index:6; }
.scr-frame.none { border-radius:12px; box-shadow:0 24px 70px rgba(0,0,0,.32); overflow:hidden; }
.scr-vp { position:absolute; overflow:hidden; background:var(--scr-page); }
.scr-frame.phone .scr-vp { border-radius:calc(var(--scr-r) - var(--scr-pad)); }
.scr-zoom { position:absolute; left:0; top:0; transform-origin:0 0; }
.scr-zoom > img, .scr-zoom > video { position:absolute; left:0; top:0; display:block; }
.scr-cur { position:absolute; left:0; top:0; width:34px; height:34px; margin:-3px 0 0 -6px; z-index:8; filter:drop-shadow(0 3px 6px rgba(0,0,0,.45)); }
.scr-rip { position:absolute; left:0; top:0; width:90px; height:90px; margin:-45px 0 0 -45px; border-radius:50%; border:4px solid var(--accent); background:color-mix(in srgb, var(--accent) 22%, transparent); opacity:0; z-index:7; }
.scr-hl { position:absolute; border:4px solid var(--accent); border-radius:10px; box-shadow:0 0 0 9999px rgba(0,0,0,0); z-index:5; opacity:0; }
.scr-tag { position:absolute; z-index:9; white-space:nowrap; font:800 26px var(--f-body); color:#111; background:#f6ce3a; padding:6px 14px; border-radius:8px; box-shadow:0 8px 24px rgba(0,0,0,.25); opacity:0; }
.scr-tag i { font-style:normal; font:700 15px var(--f-mono, monospace); margin-right:8px; opacity:.6; }
"""

LIGHT = {"scr-chrome": "#ecebe8", "scr-edge": "rgba(0,0,0,.12)", "scr-field": "#ffffff", "scr-ink": "#1d1d1f", "scr-dim": "#6a6a6f", "scr-dot": "#c9c9cc", "scr-page": "#ffffff"}
DARK = {"scr-chrome": "#25272b", "scr-edge": "rgba(255,255,255,.10)", "scr-field": "#16181b", "scr-ink": "#e8e8ea", "scr-dim": "#8b8f96", "scr-dot": "#4a4d52", "scr-page": "#0f1012"}


def area(X, p):
    """(x0, y0, x1, y1) px for the content: under the page header, above the caption pill (or the 9:16 caption band)."""
    W, H = X.W, X.H
    if X.portrait:
        return 56, 248, W - 56, (1304 if p.get("line") else 1460)
    bot = H - (_cap_clear(X, p) if p.get("line") else 56) - 6
    return 96, 104 if p.get("line") else 64, W - 96, bot


def theme_vars(p, dark_chrome=None):
    th = THEMES.get(p.get("theme")) or THEMES["paper"]
    dark = dark_chrome if dark_chrome is not None else (p.get("theme") in ("ink",))
    v = dict(th); v.update(DARK if dark else LIGHT)
    return ";".join(f"--{k}:{x}" for k, x in v.items())


def stage(X, cid, t, d, inner, p, z=4, dark_chrome=None):
    X.css("fx-screens", CSS)
    sid = f"{cid}_scr"
    X.els.append(f'<div id="{sid}" class="fx scr-root" style="position:absolute; inset:0; overflow:hidden; z-index:{z}; visibility:hidden; {theme_vars(p, dark_chrome)}">{inner}</div>')
    X.tw(f'tl.set("#{sid}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.set("#{sid}", {{visibility:"hidden"}}, {t + d:.3f});')
    return sid


def prep(X, src, max_w=1600, max_h=16000):
    """(url, w, h) of a still; oversized ones are scaled down once and cached in the build (Chrome won't paint >16k px)."""
    a = fit._abs(X, src)
    sz = fit.size(a) or (1280, 800)
    w, h = sz
    k = min(1.0, max_w / w, max_h / h)
    if k >= 0.999:
        return X.asset(src), w, h
    from PIL import Image
    key = hashlib.sha1(f"{a}:{a.stat().st_mtime}:{k:.4f}".encode()).hexdigest()[:10]
    dst = X.out / "assets" / "img" / f"{a.stem}-{key}.jpg"
    nw, nh = int(w * k), int(h * k)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(a) as im:
            im.convert("RGB").resize((nw, nh), Image.LANCZOS).save(dst, quality=88)
    return f"assets/img/{dst.name}", nw, nh


def sidecar(X, src):
    """the webpage.mjs json next to a screenshot (headings / find boxes), if any."""
    if not src: return {}
    j = fit._abs(X, src).with_suffix(".json")
    if j.exists():
        import json
        try: return json.loads(j.read_text())
        except Exception: return {}
    return {}


def frame_geom(kind, box_w, box_h, ar, P):
    """fit a device of viewport aspect `ar` (w/h) into box_w × box_h → dict(frame w/h, viewport offset/size)."""
    if kind == "browser":
        bar = 46 if not P else 52
        vw = min(box_w, (box_h - bar) * ar); vh = vw / ar
        return {"w": vw, "h": vh + bar, "vx": 0, "vy": bar, "vw": vw, "vh": vh, "bar": bar}
    if kind == "phone":
        pad = 14
        vw = min(box_w - 2 * pad, (box_h - 2 * pad) * ar); vh = vw / ar
        return {"w": vw + 2 * pad, "h": vh + 2 * pad, "vx": pad, "vy": pad, "vw": vw, "vh": vh, "pad": pad, "r": max(28, min(64, vw * 0.13))}
    vw = min(box_w, box_h * ar); vh = vw / ar
    return {"w": vw, "h": vh, "vx": 0, "vy": 0, "vw": vw, "vh": vh}


def frame(X, kind, g, x, y, inner, url="", tab="", cls=""):
    """device chrome at (x, y) holding `inner` in its viewport (.scr-vp)."""
    style = f"left:{x:.0f}px; top:{y:.0f}px; width:{g['w']:.0f}px; height:{g['h']:.0f}px;"
    vp = f'<div class="scr-vp" style="left:{g["vx"]:.0f}px; top:{g["vy"]:.0f}px; width:{g["vw"]:.0f}px; height:{g["vh"]:.0f}px">{inner}</div>'
    if kind == "browser":
        X.used_text.update(str(url) + str(tab))
        host, _, rest = str(url).replace("https://", "").replace("http://", "").partition("/")
        u = f'<div class="scr-url">🔒 {X.rich(host)}<b>{X.rich("/" + rest if rest else "")}</b></div>' if url else '<div class="scr-url"></div>'
        t = f'<div class="scr-tab">{X.rich(tab)}</div>' if tab else ""
        X.used_text.update("🔒/")
        return f'<div class="scr-frame browser {cls}" style="{style} --scr-barh:{g["bar"]}px"><div class="scr-bar"><div class="scr-dots"><i></i><i></i><i></i></div>{u}{t}</div>{vp}</div>'
    if kind == "phone":
        return f'<div class="scr-frame phone {cls}" style="{style} --scr-pad:{g["pad"]}px; --scr-r:{g["r"]:.0f}px"><i class="scr-isl"></i>{vp}</div>'
    return f'<div class="scr-frame none {cls}" style="{style}">{vp}</div>'


def vtag(X, src, t, d, w, h, start=0.0, focus=None):
    url = X.asset(src, "video")
    dur = fit.duration(fit._abs(X, src)) or d
    ms = min(max(0.0, float(start)), max(0.0, dur - 0.1))
    fit._TRACK[0] += 1
    return (f'<video id="scv{fit._TRACK[0]}" class="clip" src="{url}" muted playsinline data-start="{t:.3f}" data-duration="{d:.3f}" '
            f'data-track-index="{fit._TRACK[0]}" data-media-start="{ms:.3f}" style="width:{w:.0f}px; height:{h:.0f}px; object-fit:cover; object-position:{fit.focus_css(focus)}"></video>')


CURSOR = ('<svg class="scr-cur" viewBox="0 0 24 24"><path d="M4 2.5 L4 19.5 L8.6 15.4 L11.6 22 L14.6 20.7 L11.7 14.2 L18 14.2 Z" '
          'fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>')


def frac(v, size):
    """0–1 → fraction of size; >1 → source pixels."""
    v = float(v)
    return v * size if v <= 1.0 else v


def box_of(b, sw, sh):
    """{x,y,w,h} | [x,y,w,h] in fractions or source px → (x, y, w, h) source px."""
    if isinstance(b, dict): x, y, w, h = b.get("x", 0), b.get("y", 0), b.get("w", 0.3), b.get("h", 0.12)
    else: x, y, w, h = (list(b) + [0.3, 0.12])[:4]
    return frac(x, sw), frac(y, sh), frac(w, sw), frac(h, sh)


def cue(X, v, t, dflt):
    """'@词' / seconds from the beat start (number < beat length) / absolute seconds → absolute time."""
    if v is None: return dflt
    if isinstance(v, (int, float)):
        return t + float(v)
    r = X.T(v, t)
    return float(r) if r is not None else dflt


def zoom_xy(vw, vh, s, px, py):
    """translate for a top-left-origin zoom of scale s that centres (px, py) and never shows an edge."""
    x = min(0.0, max(vw - s * vw, vw / 2 - s * px)); y = min(0.0, max(vh - s * vh, vh / 2 - s * py))
    return x, y
