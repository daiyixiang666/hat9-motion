"""素材墙 Media — one effect for any number of pictures and clips, where the COUNT picks the choreography:

  1        hero: full-bleed iris-open + slow push, caption parallaxing the other way (a picture of the wrong shape
           becomes a framed card over a blurred copy of itself)
  2        pair: diagonal split wipes B over A, a VS badge rides the divider, a quick slider drag; hl → winner takes 3/4
  3        deal: three cards dealt from off-frame into a stack, fanned out, then one comes forward (hl)
  4–6      bento: an editorial grid, each card landing on the beat from its own side with a counter-zoom
  7–24     wall: tiles assemble in a diagonal wave, the camera pans the wall, then flies to the hl tile
  25–99    mosaic: tiles flip in from the centre outwards, the camera dollies back with a focus pull, a second
           flip wave crosses the wall, then a rack focus onto the hl picture
  100–2000 flood: starts INSIDE one picture and pulls out into a sea of all of them while a counter runs up;
           the columns drift like a waterfall (texture atlas: one JPEG, so 500 tiles cost what 5 do)

Benchmarks: Mosaic Photo Reveal / Photo Wall templates (VideoHive), Apple keynote photo walls, the "zoom out of one
photo into thousands" opener (e.g. Google Photos / year-in-review reels), before–after sliders.

p: items (list of paths or {src|video, caption, focus, fit}; also `images` / `media`) · hl (index to spotlight) ·
   t_hl (cue or seconds) · count / count_label (flood counter number and unit, default n and 张/段) · sub ·
   max_video (clips that play at once, default 6; the rest show a still) · plus theme / line / topic / host / label / ref.
Clips: bands 1–24 play them (timed, properly seeked); 25+ use a still of each clip.
"""
import math

from h9 import fit
from h9.aefx import _clip, _cap_clear, _theme_style, _vm
import importlib.util, pathlib, sys
if "h9fx__media" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__media", pathlib.Path(__file__).with_name("_media.py"))
    sys.modules["h9fx__media"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__media"])
M = sys.modules["h9fx__media"]

CSS = r"""
.mx-cam { position:absolute; inset:0; transform-origin:50% 50%; }
.mx-full { position:absolute; inset:0; overflow:hidden; }
.mx-cov { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; display:block; overflow:hidden; }
.mx-blur .mx-cov { filter:blur(38px) saturate(1.15) brightness(.62); inset:-8%; width:116%; height:116%; }
.mx-ctn { position:absolute; inset:5%; } .mx-ctn .mx-con { object-fit:contain; filter:drop-shadow(0 2vmin 4vmin rgba(0,0,0,.5)); }
.mx-ctn div.mx-con video { object-fit:contain !important; }
.mx-box { position:absolute; overflow:hidden; }
.mx-card { position:absolute; overflow:hidden; border-radius:1.2vmin; box-shadow:0 3vmin 8vmin rgba(0,0,0,.55); }
.mx-vig { position:absolute; inset:0; pointer-events:none; background:linear-gradient(180deg, rgba(0,0,0,.62), rgba(0,0,0,.12) 34%, rgba(0,0,0,0) 60%, rgba(0,0,0,.5)); }
.mx-ln { display:block; overflow:hidden; padding-bottom:.08em; } .mx-ln > span { display:inline-block; }
.mx-cap1 { position:absolute; color:#fff; text-shadow:0 .4vmin 3vmin rgba(0,0,0,.55); }
.mx-cap1 .mx-ct { font-family:var(--f-display); font-weight:900; line-height:1.08; letter-spacing:-.01em; }
.mx-idx { display:block; font:600 2vmin var(--f-mono, monospace); letter-spacing:.2em; font-style:normal; opacity:.85; margin-bottom:1.4vmin; }
.mx-div { position:absolute; background:var(--accent); box-shadow:0 0 0 .3vmin rgba(0,0,0,.25), 0 0 4vmin rgba(0,0,0,.35); }
.mx-vs { position:absolute; width:13vmin; height:13vmin; margin:-6.5vmin 0 0 -6.5vmin; border-radius:50%; background:var(--accent); color:var(--bg);
  display:grid; place-items:center; box-shadow:0 0 0 .8vmin var(--bg), 0 2vmin 5vmin rgba(0,0,0,.45); }
.mx-vs b { font:900 5.4vmin var(--f-display); letter-spacing:-.04em; }
.mx-lab { position:absolute; display:flex; align-items:center; gap:1.4vmin; color:#fff; text-shadow:0 .3vmin 2vmin rgba(0,0,0,.6); }
.mx-lab .mx-pill { font:800 2.4vmin var(--f-mono, monospace); background:#fff; color:#111; padding:.3vmin 1.2vmin; border-radius:.6vmin; text-shadow:none; }
.mx-lab b { font-family:var(--f-display); font-weight:900; line-height:1.1; }
.mx-c { position:absolute; overflow:hidden; border-radius:1vmin; background:var(--card, #222); box-shadow:0 1.6vmin 4.4vmin rgba(0,0,0,.35); }
.mx-c .mx-tag { position:absolute; left:0; right:0; bottom:0; padding:3vmin 1.6vmin 1.3vmin; color:#fff; font:700 2.2vmin/1.25 var(--f-body);
  background:linear-gradient(180deg, rgba(0,0,0,0), rgba(0,0,0,.66)); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.mx-ring { position:absolute; inset:0; border-radius:inherit; box-shadow:inset 0 0 0 .7vmin var(--accent); opacity:0; pointer-events:none; }
.mx-wall, .mx-grid { position:absolute; }
.mx-t { position:absolute; overflow:hidden; border-radius:.6vmin; background:#222; }
.mx-at { position:absolute; border-radius:.35vmin; background-repeat:no-repeat; backface-visibility:visible; }
.mx-col { position:absolute; top:0; }
.mx-hl { position:absolute; overflow:hidden; border-radius:1.2vmin; box-shadow:0 0 0 .8vmin var(--accent), 0 3vmin 9vmin rgba(0,0,0,.6); opacity:0; }
.mx-scrim { position:absolute; inset:0; background:radial-gradient(ellipse 42% 34% at 50% 50%, rgba(0,0,0,.72), rgba(0,0,0,.25) 70%, rgba(0,0,0,0)); opacity:0; pointer-events:none; }
.mx-count { position:absolute; left:0; right:0; text-align:center; color:#fff; opacity:0; text-shadow:0 .6vmin 4vmin rgba(0,0,0,.6); }
.mx-count b { font-family:var(--f-num, var(--f-display)); font-weight:900; letter-spacing:-.03em; font-variant-numeric:tabular-nums; line-height:.9; }
.mx-count span { font-family:var(--f-display); font-weight:900; margin-left:.12em; }
.mx-count small { display:block; margin-top:1.6vmin; font:700 2.6vmin var(--f-body); letter-spacing:.2em; opacity:.85; }
.mx-sk { position:absolute; border-radius:1vmin; background:linear-gradient(100deg, color-mix(in srgb, var(--fg) 8%, transparent) 30%, color-mix(in srgb, var(--fg) 18%, transparent) 50%, color-mix(in srgb, var(--fg) 8%, transparent) 70%); background-size:300% 100%; }
"""

BENTO = {   # cells (x, y, w, h) as fractions of the content box
    (4, False): [(0, 0, .5, 1), (.5, 0, .5, .52), (.5, .52, .25, .48), (.75, .52, .25, .48)],
    (5, False): [(0, 0, .42, 1), (.42, 0, .33, .56), (.75, 0, .25, .56), (.42, .56, .25, .44), (.67, .56, .33, .44)],
    (6, False): [(0, 0, .36, .6), (.36, 0, .28, .6), (.64, 0, .36, .6), (0, .6, .3, .4), (.3, .6, .4, .4), (.7, .6, .3, .4)],
    (4, True): [(0, 0, 1, .46), (0, .46, .5, .54), (.5, .46, .5, .27), (.5, .73, .5, .27)],
    (5, True): [(0, 0, 1, .38), (0, .38, .5, .31), (.5, .38, .5, .31), (0, .69, .6, .31), (.6, .69, .4, .31)],
    (6, True): [(0, 0, .6, .36), (.6, 0, .4, .36), (0, .36, .4, .32), (.4, .36, .6, .32), (0, .68, .5, .32), (.5, .68, .5, .32)],
}


def band_of(n):
    if n <= 0: return "empty"
    if n == 1: return "hero"
    if n == 2: return "pair"
    if n == 3: return "deal"
    if n <= 6: return "bento"
    if n <= 24: return "wall"
    if n <= 99: return "mosaic"
    return "flood"


def media(X, cid, t, d, p):
    X.css("fx-media", CSS)
    its = M.items(X, p)
    n = len(its)
    band = band_of(n)
    W, H, P = X.W, X.H, X.portrait
    vm = _vm(X, 1)
    hl = p.get("hl")
    hl = None if hl in (None, "") else max(0, min(n - 1, int(hl))) if n else None
    th = X.T(p.get("t_hl"), t) if p.get("t_hl") is not None else None
    th = float(th) if th is not None else t + d * 0.66
    th = min(max(th, t + 0.9), t + d - 0.5)
    maxv = int(p.get("max_video", 6))

    # which clips actually play (others show a still); any playing clip moves the picture layer to the root
    vids = [i for i, it in enumerate(its) if it["video"]]
    if band in ("hero", "pair", "deal", "bento"): play = set(vids)
    elif band == "wall": play = set(vids[:maxv])
    elif band == "mosaic" and hl is not None and its[hl]["video"]: play = {hl}
    else: play = set()
    root = bool(play)
    R = f"#{cid}_st" if root else f"#{cid}"

    def pic(i, cls="mx-cov", allow=True):
        it = its[i]
        if it["video"] and allow and i in play:
            return f'<div class="{cls}">{M.vtile(X, it["src"], t, d, it["focus"], start=it["start"])}</div>'
        return f'<img class="{cls}" src="{M.still(X, it)}" alt="" style="object-position:{fit.focus_css(it["focus"])}">'

    def boxed(i, box_ar, lim=1.8):
        """cover when the picture roughly matches the box; otherwise the whole picture over a blurred copy of itself."""
        it = its[i]
        if it["fit"] == "cover" or (it["fit"] != "contain" and max(it["ar"] / box_ar, box_ar / it["ar"]) <= lim):
            return pic(i)
        return f'<div class="mx-full mx-blur">{pic(i)}</div><div class="mx-ctn">{pic(i, "mx-cov mx-con")}</div>'

    def lines(text, w, h, mx, mn, nmax=3, lh=1.08):
        f = fit.fit_text(fit.as_text(text, " "), w, h, mx, mn, lh=lh, max_lines=nmax)
        return f, "".join(f'<span class="mx-ln"><span>{X.rich(l)}</span></span>' for l in f.lines)

    # content box clear of the header and the caption pill
    if P: bx0, by0, bx1, by1 = 56, 262, W - 56, 1296
    else: bx0, by0, bx1, by1 = 96, 116, W - 96, H - max(_cap_clear(X, p), 70) - 14
    bw, bh = bx1 - bx0, by1 - by0
    photo = band in ("hero", "pair", "wall", "mosaic", "flood")
    q = dict(p, fx="plate" if photo else "media", fxid=p.get("fxid") or f"media ×{n:,}" if n else "media")
    sfx = []

    # ---------------------------------------------------------------- bands
    if band == "empty":
        cells = BENTO[(6, P)]
        inner = '<div class="mx-cam">' + "".join(
            f'<i class="mx-sk" style="left:{bx0 + x * bw + 8:.0f}px; top:{by0 + y * bh + 8:.0f}px; width:{w * bw - 16:.0f}px; height:{h * bh - 16:.0f}px"></i>'
            for x, y, w, h in cells) + "</div>"
        X.tw(f'tl.from("{R} .mx-sk", {{opacity:0, y:20, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.05:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-sk", {{backgroundPosition:"100% 0"}}, {{backgroundPosition:"-50% 0", duration:1.4, ease:"none", repeat:{max(0, int(d / 1.4))}}}, {t:.3f});')

    elif band == "hero":
        it = its[0]; far = W / H
        extreme = it["fit"] == "contain" or (it["fit"] != "cover" and max(it["ar"] / far, far / it["ar"]) > 1.7)
        if extreme:
            cbw, cbh = (W * 0.84, H * 0.5) if P else (W * 0.8, H * 0.72)
            cw = min(cbw, cbh * it["ar"]); chh = cw / it["ar"]
            cx, cy = W / 2, (H * 0.47 if P else H * 0.5)
            body = (f'<div class="mx-full mx-blur">{pic(0)}</div>'
                    f'<div class="mx-card" style="left:{cx - cw / 2:.0f}px; top:{cy - chh / 2:.0f}px; width:{cw:.0f}px; height:{chh:.0f}px">{pic(0)}</div>')
        else:
            body = f'<div class="mx-full">{pic(0)}</div>'
        cap = ""
        if it["caption"] or p.get("sub"):
            cwid = (W - 112) if P else W * 0.5
            f, ln = lines(it["caption"] or p.get("sub"), cwid, H * (0.16 if P else 0.22), vm * 8, vm * 3.4)
            x0, y0 = (56, 262) if P else (96, 132)
            cap = f'<div class="mx-cap1" style="left:{x0}px; top:{y0}px; width:{cwid:.0f}px"><i class="mx-idx">01 / 01</i><div class="mx-ct" style="font-size:{f.px}px">{ln}</div></div>'
        inner = f'<div class="mx-cam">{body}</div><div class="mx-vig"></div>{cap}'
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:1.0, xPercent:0}}, {{scale:1.13, xPercent:-1.6, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
        if extreme:
            X.tw(f'tl.from("{R} .mx-blur", {{opacity:0, duration:0.6, ease:"power2.out"}}, {t:.3f});')
            X.tw(f'tl.from("{R} .mx-card", {{y:90, scale:0.88, rotation:-2.5, opacity:0, duration:0.95, ease:"expo.out"}}, {t + 0.08:.3f});')
            X.tw(f'tl.fromTo("{R} .mx-card .mx-cov", {{scale:1.25}}, {{scale:1.0, duration:{d:.2f}, ease:"power2.out"}}, {t:.3f});')
        else:
            X.tw(f'tl.fromTo("{R} .mx-full", {{clipPath:"inset(10% 14% 10% 14% round 28px)"}}, {{clipPath:"inset(0% 0% 0% 0% round 0px)", duration:1.05, ease:"expo.out"}}, {t:.3f});')
            X.tw(f'tl.fromTo("{R} .mx-full .mx-cov", {{scale:1.3}}, {{scale:1.0, duration:1.4, ease:"expo.out"}}, {t:.3f});')
        if cap:
            X.tw(f'tl.from("{R} .mx-cap1 .mx-ln > span, {R} .mx-idx", {{yPercent:110, opacity:0, duration:0.7, ease:"expo.out", stagger:0.08}}, {t + 0.35:.3f});')
            X.tw(f'tl.fromTo("{R} .mx-cap1", {{x:70}}, {{x:-30, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        sfx += [(t, "whoosh_soft")]

    elif band == "pair":
        K = 5 if P else 7
        if P:
            ang = math.degrees(math.atan2(2 * K / 100 * H, W))
            div = f'<i class="mx-div" style="left:-10%; width:120%; height:1.1vmin; margin-top:-.55vmin; top:110%; transform:rotate({ang:.2f}deg)"></i>'
            vs = '<div class="mx-vs" style="left:50%; top:110%"><b>VS</b></div>'
        else:
            ang = math.degrees(math.atan2(2 * K / 100 * W, H))
            div = f'<i class="mx-div" style="top:-10%; height:120%; width:1.1vmin; margin-left:-.55vmin; left:110%; transform:rotate({ang:.2f}deg)"></i>'
            vs = '<div class="mx-vs" style="top:50%; left:110%"><b>VS</b></div>'
        s0 = 100 + K + 3
        poly0 = f"polygon(0% {s0 - K}%, 100% {s0 + K}%, 100% 100%, 0% 100%)" if P else f"polygon({s0 + K}% 0%, 100% 0%, 100% 100%, {s0 - K}% 100%)"
        labs = ""
        for k, (it, tag) in enumerate(zip(its, "AB")):
            if not it["caption"]: continue
            cwid = (W - 112) if P else W * 0.36
            f, ln = lines(it["caption"], cwid, vm * 9, vm * 4.6, vm * 2.6, nmax=2, lh=1.1)
            if P: pos = "left:56px; top:262px" if k == 0 else "left:56px; top:1188px"
            else: pos = "left:96px; top:134px" if k == 0 else "right:96px; top:134px; flex-direction:row-reverse; text-align:right"
            labs += f'<div class="mx-lab mx-l{tag}" style="{pos}; max-width:{cwid:.0f}px"><span class="mx-pill">{tag}</span><b style="font-size:{f.px}px">{"<br>".join(X.rich(l) for l in f.lines)}</b></div>'
        bxa, bxb = ("left:0; top:0; width:100%; height:82%", "left:0; top:18%; width:100%; height:82%") if P else ("left:0; top:0; width:82%; height:100%", "left:18%; top:0; width:82%; height:100%")
        box_ar = (W / (H * 0.82)) if P else (W * 0.82 / H)
        inner = (f'<div class="mx-cam"><div class="mx-full mx-a"><div class="mx-box" style="{bxa}">{boxed(0, box_ar)}</div></div>'
                 f'<div class="mx-full mx-b" style="clip-path:{poly0}"><div class="mx-box" style="{bxb}">{boxed(1, box_ar)}</div></div>{div}{vs}</div>'
                 f'<div class="mx-vig"></div>{labs}')
        axis = "top" if P else "left"
        polyjs = ("`polygon(0%% ${s-%d}%%, 100%% ${s+%d}%%, 100%% 100%%, 0%% 100%%)`" % (K, K)) if P else ("`polygon(${s+%d}%% 0%%, 100%% 0%%, 100%% 100%%, ${s-%d}%% 100%%)`" % (K, K))
        T1 = t + 0.45
        segs = [(s0, 50, T1, 0.85, "expo.inOut")]
        tt = T1 + 1.1
        if tt + 1.35 < (th if hl is not None else t + d) - 0.1:
            segs += [(50, 41, tt, 0.4, "power2.inOut"), (41, 59, tt + 0.42, 0.5, "power2.inOut"), (59, 50, tt + 0.95, 0.4, "power2.inOut")]
        if hl is not None:
            segs.append((50, 27 if hl == 1 else 73, th, 0.7, "expo.inOut"))
        js = (f'(()=>{{const r=document.querySelector("{R}"), b=r.querySelector(".mx-b"), dv=r.querySelector(".mx-div"), vs=r.querySelector(".mx-vs");'
              f'const o={{s:{s0}}}; const up=()=>{{const s=o.s; b.style.clipPath={polyjs}; dv.style.{axis}=s+"%"; vs.style.{axis}=s+"%";}};')
        for a, b_, ts, du, ea in segs:
            js += f'tl.fromTo(o, {{s:{a}}}, {{s:{b_}, duration:{du}, ease:"{ea}", onUpdate:up, immediateRender:false}}, {ts:.3f});'
        js += "})();"
        X.tw(js)
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:1.0}}, {{scale:1.07, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-vs", {{scale:0, rotation:-120}}, {{scale:1, rotation:0, duration:0.5, ease:"back.out(2.2)", immediateRender:false}}, {T1 + 0.55:.3f});')
        X.tw(f'tl.from("{R} .mx-lab", {{y:24, opacity:0, duration:0.5, ease:"expo.out", stagger:0.5}}, {t + 0.2:.3f});')
        sfx += [(T1, "whoosh_soft"), (T1 + 0.6, "pop")]
        if hl is not None:
            lose = ".mx-a" if hl == 1 else ".mx-b"
            X.tw(f'tl.to("{R} {lose}", {{filter:"grayscale(1) brightness(.5)", duration:0.5}}, {th:.3f});')
            X.tw(f'tl.to("{R} .mx-vs", {{scale:0.7, opacity:0.0, duration:0.35}}, {th:.3f});')
            sfx += [(th, "hit")]

    elif band == "deal":
        rots = [-7, 0, 7] if not P else [-4, 3, -2]
        if P:
            cw = bw * 0.74
            hs = [min(max(cw / it["ar"], cw * 0.42), cw * 1.15) for it in its]
            s = min(1.0, bh * 1.04 / sum(h * 0.86 for h in hs))
            cw *= s; hs = [h * s for h in hs]
            ys = [by0 + bh * f for f in (0.19, 0.5, 0.81)]
            pos = [(W / 2 + dx - cw / 2, y - h / 2, cw, h) for dx, y, h in zip((-44, 30, -18), ys, hs)]
        else:
            ch = bh * 0.8
            ws = [min(max(ch * it["ar"], ch * 0.5), ch * 1.6) for it in its]
            s = min(1.0, bw * 0.98 / (sum(ws) * 0.92))
            ch *= s; ws = [w * s for w in ws]
            xs = [bx0 + bw * f for f in (0.2, 0.5, 0.8)]
            pos = [(x - w / 2, by0 + bh / 2 - ch / 2 + dy, w, ch) for x, w, dy in zip(xs, ws, (14, -6, 14))]
        cards = ""
        for k, (x, y, w, h) in enumerate(pos):
            tsty = ' style="top:0; bottom:auto; padding:1.3vmin 1.6vmin 3vmin; background:linear-gradient(0deg, rgba(0,0,0,0), rgba(0,0,0,.66))"' if P else ""
            tag = f'<b class="mx-tag"{tsty}>{X.rich(its[k]["caption"])}</b>' if its[k]["caption"] else ""
            z = (k + 1) if P else (2 if k == 1 else 1)
            cards += f'<div class="mx-c mx-d" data-k="{k}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px; z-index:{z}">{boxed(k, w / h, 2.2)}{tag}<i class="mx-ring"></i></div>'
        inner = f'<div class="mx-cam" style="perspective:1600px">{cards}</div>'
        cx, cy = (W / 2, by0 + bh / 2)
        for k, (x, y, w, h) in enumerate(pos):
            sx, sy = cx - (x + w / 2), cy - (y + h / 2)
            sel = f'{R} .mx-d[data-k=\'{k}\']'
            X.tw(f'tl.fromTo("{sel}", {{x:{W * 0.7:.0f}, y:{H * 0.55:.0f}, rotation:{38 + k * 9}, scale:0.8, opacity:0}}, {{x:{sx:.0f}, y:{sy:.0f}, rotation:{(k - 1) * 4}, scale:0.92, opacity:1, duration:0.48, ease:"power3.out"}}, {t + 0.1 + k * 0.15:.3f});')
            X.tw(f'tl.to("{sel}", {{x:0, y:0, rotation:{rots[k]}, scale:1, duration:0.75, ease:"expo.inOut"}}, {t + 0.94:.3f});')
            sfx.append((t + 0.1 + k * 0.15, "paper"))
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:1.0}}, {{scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-d .mx-tag", {{opacity:0}}, {{opacity:1, duration:0.3, stagger:0.08}}, {t + 1.6:.3f});')   # labels once the hand is spread (no overlap)
        f = hl if hl is not None else 1
        for k in range(3):
            sel = f'{R} .mx-d[data-k=\'{k}\']'
            if k == f:
                X.tw(f'tl.to("{sel}", {{scale:1.14, rotation:0, zIndex:5, duration:0.55, ease:"back.out(1.6)"}}, {th:.3f});')
                X.tw(f'tl.to("{sel} .mx-ring", {{opacity:1, duration:0.3}}, {th + 0.1:.3f});')
            else:
                X.tw(f'tl.to("{sel}", {{scale:0.9, filter:"brightness(.5) saturate(.6)", {"y" if P else "x"}:{(-1 if k < f else 1) * 26}, duration:0.55, ease:"power3.out"}}, {th:.3f});')
        sfx.append((th, "hit"))

    elif band == "bento":
        cells = BENTO[(n, P)]
        g = 7
        rects = [(bx0 + x * bw + g, by0 + y * bh + g, w * bw - 2 * g, h * bh - 2 * g) for x, y, w, h in cells]
        # tall pictures go to tall cells, wide ones to wide cells
        cell_order = sorted(range(n), key=lambda c: rects[c][2] / rects[c][3])
        item_order = sorted(range(n), key=lambda i: its[i]["ar"])
        assign = {item_order[r]: cell_order[r] for r in range(n)}
        beat = min(0.3, d * 0.42 / n)
        dirs = ["inset(0% 100% 0% 0%)", "inset(0% 0% 100% 0%)", "inset(0% 0% 0% 100%)", "inset(100% 0% 0% 0%)"]
        cards = ""
        for i in range(n):
            x, y, w, h = rects[assign[i]]
            tag = f'<b class="mx-tag">{X.rich(its[i]["caption"])}</b>' if its[i]["caption"] else ""
            cards += f'<div class="mx-c mx-b6" data-k="{i}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">{pic(i)}{tag}<i class="mx-ring"></i></div>'
        inner = f'<div class="mx-cam">{cards}</div>'
        for r in range(n):
            i = sorted(range(n), key=lambda i: assign[i])[r]          # land in reading order of the cells
            sel = f'{R} .mx-b6[data-k=\'{i}\']'
            tk = t + 0.12 + r * beat
            X.tw(f'tl.fromTo("{sel}", {{clipPath:"{dirs[r % 4]}"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:0.55, ease:"expo.out"}}, {tk:.3f});')
            X.tw(f'tl.fromTo("{sel} .mx-cov", {{scale:1.35}}, {{scale:1.0, duration:0.85, ease:"expo.out"}}, {tk:.3f});')
            X.tw(f'tl.to("{sel} .mx-cov", {{scale:1.07, xPercent:{(-1) ** r * 2}, duration:{max(0.4, t + d - tk - 0.9):.2f}, ease:"none"}}, {tk + 0.86:.3f});')
            sfx.append((tk, "click"))
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:1.0}}, {{scale:1.03, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        if hl is not None:
            X.tw(f'tl.to("{R} .mx-b6:not([data-k=\'{hl}\'])", {{filter:"brightness(.42) saturate(.5)", duration:0.45}}, {th:.3f});')
            X.tw(f'tl.to("{R} .mx-b6[data-k=\'{hl}\'] .mx-ring", {{opacity:1, duration:0.3}}, {th:.3f});')
            X.tw(f'tl.fromTo("{R} .mx-b6[data-k=\'{hl}\']", {{scale:1}}, {{scale:1.04, duration:0.5, ease:"back.out(2)", immediateRender:false}}, {th:.3f});')
            sfx.append((th, "hit"))

    elif band == "wall":
        tar = min(1.78, max(0.66, sorted(it["ar"] for it in its)[n // 2]))
        ww0, wh0 = (W * 1.5, H * 1.22) if P else (W * 1.32, H * 1.32)
        gap = vm * 1.2
        cols, rows = fit.grid(n, ww0, wh0, item_ar=tar, gap=gap)
        tw_ = min((ww0 - gap * (cols - 1)) / cols, ((wh0 - gap * (rows - 1)) / rows) * tar); th_ = tw_ / tar
        ww, wh = cols * tw_ + gap * (cols - 1), rows * th_ + gap * (rows - 1)
        L0, T0 = (W - ww) / 2, (H - wh) / 2
        tiles, ranks, centers = "", [], []
        for i in range(n):
            r, c = divmod(i, cols)
            inrow = min(cols, n - r * cols)
            x = (ww - (inrow * tw_ + gap * (inrow - 1))) / 2 + c * (tw_ + gap)
            y = r * (th_ + gap)
            centers.append((L0 + x + tw_ / 2, T0 + y + th_ / 2))
            ranks.append(r + c)
            tag = f'<b class="mx-tag" style="opacity:0">{X.rich(its[i]["caption"])}</b>' if its[i]["caption"] else ""
            tiles += f'<div class="mx-t mx-c" data-k="{i}" style="left:{x:.1f}px; top:{y:.1f}px; width:{tw_:.1f}px; height:{th_:.1f}px">{pic(i)}{tag}<i class="mx-ring"></i></div>'
        inner = f'<div class="mx-cam" style="perspective:1800px"><div class="mx-wall" style="left:{L0:.1f}px; top:{T0:.1f}px; width:{ww:.1f}px; height:{wh:.1f}px">{tiles}</div></div>'
        each = min(0.07, 0.75 / max(1, rows + cols))
        X.tw(f'tl.fromTo("{R} .mx-t", {{opacity:0, scale:0.45, rotationX:-70, y:40}}, {{opacity:1, scale:1, rotationX:0, y:0, duration:0.7, ease:"expo.out", stagger:(i)=>[{",".join(map(str, ranks))}][i]*{each:.3f}}}, {t + 0.05:.3f});')
        panx = max(0.0, (ww - W) / 2) * 0.85; pany = max(0.0, (wh - H) / 2) * 0.6
        f = hl if hl is not None else min(n - 1, (rows // 2) * cols + cols // 2)
        cxh, cyh = centers[f]
        sc = min(1.7, max(1.15, (W * (0.44 if not P else 0.62)) / tw_))
        txh = min(0.0, max(W - sc * W, W / 2 - sc * cxh)); tyh = min(0.0, max(H - sc * H, H / 2 - sc * cyh))
        X.tw(f'tl.set("{R} .mx-cam", {{transformOrigin:"0 0"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-cam", {{x:{panx:.0f}, y:{pany:.0f}, scale:1}}, {{x:{-panx:.0f}, y:{-pany:.0f}, scale:1.04, duration:{th - t - 0.03:.2f}, ease:"sine.inOut"}}, {t:.3f});')
        X.tw(f'tl.to("{R} .mx-cam", {{x:{txh:.0f}, y:{tyh:.0f}, scale:{sc:.3f}, duration:0.85, ease:"expo.inOut"}}, {th:.3f});')
        X.tw(f'tl.to("{R} .mx-t:not([data-k=\'{f}\'])", {{filter:"brightness(.34) saturate(.4)", duration:0.5}}, {th + 0.2:.3f});')
        X.tw(f'tl.to("{R} .mx-t[data-k=\'{f}\'] .mx-ring, {R} .mx-t[data-k=\'{f}\'] .mx-tag", {{opacity:1, duration:0.3}}, {th + 0.5:.3f});')
        sfx += [(t + 0.05, "whoosh_soft"), (th, "whoosh_deep")]

    elif band == "mosaic":
        tar = 1.0 if P else 1.25
        ww0, wh0 = W * 1.16, H * 1.16
        gap = vm * 0.6
        cols, rows = fit.grid(n, ww0, wh0, item_ar=tar, gap=gap)
        tw_ = min((ww0 - gap * (cols - 1)) / cols, ((wh0 - gap * (rows - 1)) / rows) * tar); th_ = tw_ / tar
        ww, wh = cols * tw_ + gap * (cols - 1), rows * th_ + gap * (rows - 1)
        L0, T0 = (W - ww) / 2, (H - wh) / 2
        aw = 320; ah = round(aw / tar)
        url, acols, AW, AH = M.atlas(X, its, aw, ah)
        tiles, dist, colr = "", [], []
        mc, mr = (cols - 1) / 2, (rows - 1) / 2
        for i in range(n):
            r, c = divmod(i, cols)
            inrow = min(cols, n - r * cols)
            x = (ww - (inrow * tw_ + gap * (inrow - 1))) / 2 + c * (tw_ + gap); y = r * (th_ + gap)
            dist.append(round(math.hypot(c - mc, (r - mr) * 1.2), 2)); colr.append(c)
            tiles += f'<i class="mx-at" style="left:{x:.1f}px; top:{y:.1f}px; width:{tw_:.1f}px; height:{th_:.1f}px; {M.atlas_bg(url, acols, AW, AH, aw, ah, i, tw_, th_)}"></i>'
        f = hl if hl is not None else min(n - 1, (rows // 2) * cols + cols // 2)
        hw, hh = ((W * 0.78, W * 0.78 / max(0.6, min(1.8, its[f]["ar"]))) if P else (H * 0.62 * max(0.6, min(1.8, its[f]["ar"])), H * 0.62))
        hy = (H * 0.46 if P else (by0 + by1) / 2)
        hcap = ""
        if its[f]["caption"]:
            hcap = f'<b class="mx-tag">{X.rich(its[f]["caption"])}</b>'
        hlx = f'<div class="mx-hl" style="left:{W / 2 - hw / 2:.0f}px; top:{hy - hh / 2:.0f}px; width:{hw:.0f}px; height:{hh:.0f}px">{pic(f)}{hcap}</div>'
        inner = (f'<div class="mx-cam" style="perspective:1400px"><div class="mx-grid" style="left:{L0:.1f}px; top:{T0:.1f}px; width:{ww:.1f}px; height:{wh:.1f}px">{tiles}</div></div>{hlx}')
        each = min(0.05, 0.9 / max(1.0, max(dist)))
        X.tw(f'tl.fromTo("{R} .mx-at", {{rotationY:-90, opacity:0}}, {{rotationY:0, opacity:1, duration:0.55, ease:"power2.out", stagger:(i)=>[{",".join(map(str, dist))}][i]*{each:.3f}}}, {t + 0.05:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:1.38, filter:"blur(10px)"}}, {{scale:1.0, filter:"blur(0px)", duration:{min(1.6, d * 0.45):.2f}, ease:"power2.inOut"}}, {t:.3f});')
        tw2 = t + d * 0.42
        if tw2 + 0.6 < th - 0.1:
            each2 = min(0.04, 0.5 / max(1, cols))
            X.tw(f'tl.fromTo("{R} .mx-at", {{rotationY:0}}, {{rotationY:360, duration:0.6, ease:"power2.inOut", stagger:(i)=>[{",".join(map(str, colr))}][i]*{each2:.3f}, immediateRender:false}}, {tw2:.3f});')
        X.tw(f'tl.to("{R} .mx-cam", {{scale:1.05, duration:{max(0.3, th - t - min(1.6, d * 0.45)):.2f}, ease:"none"}}, {t + min(1.6, d * 0.45):.3f});')
        X.tw(f'tl.to("{R} .mx-grid", {{filter:"blur(6px) brightness(.42)", duration:0.5}}, {th:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-hl", {{opacity:0, scale:0.55, y:40}}, {{opacity:1, scale:1, y:0, duration:0.7, ease:"expo.out", immediateRender:false}}, {th + 0.05:.3f});')
        sfx += [(t + 0.05, "whoosh_soft"), (th, "hit")]

    else:   # flood
        m = min(n, 2000)
        tar = 1.0 if P else 1.25
        ww0, wh0 = W * 1.06, H * 1.06
        gap = max(2.0, vm * (0.4 if m < 400 else 0.25))
        cols, rows = fit.grid(m, ww0, wh0, item_ar=tar, gap=gap)
        tw_ = min((ww0 - gap * (cols - 1)) / cols, ((wh0 - gap * (rows - 1)) / rows) * tar); th_ = tw_ / tar
        ww, wh = cols * tw_ + gap * (cols - 1), rows * th_ + gap * (rows - 1)
        L0, T0 = (W - ww) / 2, (H - wh) / 2
        aw = 200 if m <= 600 else 120; ah = round(aw / tar)
        url, acols, AW, AH = M.atlas(X, its[:m], aw, ah)
        hero = hl if hl is not None else min(m - 1, (rows // 2) * cols + cols // 2)
        colhtml = []
        for c in range(cols):
            cells = ""
            for r in range(rows):
                i = r * cols + c
                if i >= m: continue
                y = r * (th_ + gap)
                if i == hero:
                    cells += f'<div class="mx-t mx-hero" style="left:0; top:{y:.1f}px; width:{tw_:.1f}px; height:{th_:.1f}px">{pic(i, allow=False)}</div>'
                else:
                    cells += f'<i class="mx-at" data-k="{i}" style="left:0; top:{y:.1f}px; width:{tw_:.1f}px; height:{th_:.1f}px; {M.atlas_bg(url, acols, AW, AH, aw, ah, i, tw_, th_)}"></i>'
            colhtml.append(f'<div class="mx-col" data-c="{c}" style="left:{c * (tw_ + gap):.1f}px; width:{tw_:.1f}px; height:{wh:.1f}px">{cells}</div>')
        num = p.get("count", n)
        try: num = float(str(num).replace(",", ""))
        except ValueError: num = n
        unit = p.get("count_label") or ("段" if all(it["video"] for it in its) else "张")
        npx = vm * (24 if P else 22)
        cy = (H * 0.44) if P else (by0 + by1) / 2
        sub = f'<small>{X.rich(p["sub"])}</small>' if p.get("sub") else ""
        counter = (f'<div class="mx-scrim"></div><div class="mx-count" style="top:{cy - npx * 0.55:.0f}px"><b class="mx-n" style="font-size:{npx:.0f}px">0</b>'
                   f'<span style="font-size:{npx * 0.42:.0f}px">{X.rich(unit)}</span>{sub}</div>')
        inner = (f'<div class="mx-cam"><div class="mx-grid" style="left:{L0:.1f}px; top:{T0:.1f}px; width:{ww:.1f}px; height:{wh:.1f}px">{"".join(colhtml)}</div></div>{counter}')
        hr, hc = divmod(hero, cols)
        hx, hy = L0 + hc * (tw_ + gap) + tw_ / 2, T0 + hr * (th_ + gap) + th_ / 2
        s0 = max(W / tw_, H / th_) * 1.04
        tz0, tz1 = t + 0.25, t + 0.25 + min(2.0, d * 0.5)
        X.tw(f'tl.set("{R} .mx-cam", {{transformOrigin:"0 0"}}, {t:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-cam", {{scale:{s0:.3f}, x:{W / 2 - s0 * hx:.1f}, y:{H / 2 - s0 * hy:.1f}}}, {{scale:1, x:0, y:0, duration:{tz1 - tz0:.2f}, ease:"expo.inOut"}}, {tz0:.3f});')
        X.tw(f'tl.to("{R} .mx-cam", {{scale:1.035, x:{-W * 0.0175:.1f}, y:{-H * 0.0175:.1f}, duration:{max(0.3, t + d - tz1):.2f}, ease:"none"}}, {tz1:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-hero img", {{scale:1.0}}, {{scale:1.06, duration:0.6, ease:"none"}}, {t:.3f});')
        for c in range(cols):
            amp = th_ * (0.35 + 0.25 * ((c * 7) % 3) / 2) * (1 if c % 2 else -1)
            X.tw(f'tl.fromTo("{R} .mx-col[data-c=\'{c}\']", {{y:{-amp:.1f}}}, {{y:{amp:.1f}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
        js = (f'(()=>{{const o={{v:0}}, el=document.querySelector("{R} .mx-n"); '
              f'tl.fromTo(o, {{v:0}}, {{v:{num}, duration:{(tz1 - tz0) * 0.9:.2f}, ease:"power2.in", immediateRender:false, onUpdate:()=>{{el.textContent=Math.round(o.v).toLocaleString("en-US");}}}}, {tz0 + 0.35:.3f});}})();')
        X.tw(js)
        X.tw(f'tl.fromTo("{R} .mx-count", {{opacity:0, scale:0.8}}, {{opacity:1, scale:1, duration:0.5, ease:"expo.out", immediateRender:false}}, {tz0 + 0.3:.3f});')
        X.tw(f'tl.fromTo("{R} .mx-scrim", {{opacity:0}}, {{opacity:1, duration:0.6, immediateRender:false}}, {tz0 + 0.3:.3f});')
        X.used_text.update("0123456789,")
        if hl is not None:
            X.tw(f'tl.to("{R} .mx-count, {R} .mx-scrim", {{opacity:0, duration:0.3}}, {th:.3f});')
            X.tw(f'tl.to("{R} .mx-grid", {{filter:"brightness(.4)", duration:0.4}}, {th:.3f});')
            X.tw(f'tl.fromTo("{R} .mx-hero", {{scale:1, zIndex:3}}, {{scale:{min(4.0, W * 0.3 / tw_):.2f}, zIndex:3, duration:0.6, ease:"back.out(1.4)", immediateRender:false}}, {th:.3f});')
            X.tw(f'tl.set("{R} .mx-col:nth-child({hc + 1})", {{zIndex:3}}, {th:.3f});')
        sfx += [(tz0, "whoosh_deep"), (tz0 + 0.35, "count")]

    # ---------------------------------------------------------------- mount
    if root:
        _clip(X, cid, t, d, "", q)
        M.stage(X, cid, t, d, inner, _theme_style(p, paint=False))
    else:
        _clip(X, cid, t, d, inner, q)
    for tt, k in sfx: X.sfx(tt, k)


FX = {"media": media}
