"""引用视频片段 (embedded clip — "我们看一段当年的影像 / 他在采访里说"): the clip plays inside a player — title bar,
scrub bar that really advances, a running timecode, a quoted subtitle or a descriptive caption over the picture —
while an info column carries the source, year, licence and what the clip shows. The video is properly timed
media (a root-level timed <video>, see fit.media), so every rendered frame is the right frame of the clip.

p: video (or image as a still fallback) · start (seconds into the clip) · title · source · year · license ·
   caption (what the clip shows) · quote (words said in it — shown as a subtitle in quotes) · hl · kicker · focus
Adapts: 16:9, 4:3, square or 9:16 sources (the player takes the source's shape; portrait sources sit beside a wider
info column), any caption length, still image instead of video; 16:9 frame = player left + info right,
9:16 frame = player on top + info below.
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = _load("_cite")


def _tc(s):
    s = max(0, int(round(s))); return f"{s // 60:02d}:{s % 60:02d}"


def cite_video(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    src = p.get("video") or p.get("image")
    ar = fit.aspect(X, src, 16 / 9) if src else 16 / 9
    bz, top = 12, 44                                   # bezel padding, title bar height
    if P:
        maxw, maxh = x1 - x0, (y1 - y0) * (0.58 if ar >= 1 else 0.52)
    else:
        maxw, maxh = (x1 - x0) * (0.64 if ar >= 1 else 0.5), (y1 - y0)
    vw = min(maxw - 2 * bz, (maxh - 2 * bz - top) * ar); vh = vw / ar
    bw, bh = vw + 2 * bz, vh + 2 * bz + top
    if P:
        bx, by = x0 + (x1 - x0 - bw) / 2, y0
        ix, iy, iw, ih = x0, by + bh + 30, x1 - x0, y1 - (by + bh + 30)
    else:
        bx, by = x0, y0 + (y1 - y0 - bh) / 2
        ix, iy, iw, ih = bx + bw + 60, y0, x1 - (bx + bw + 60), y1 - y0
    vx, vy = bx + bz, by + bz + top
    dur = fit.duration(fit._abs(X, src)) if src and fit.is_video(src) else d
    start = float(p.get("start", 0))
    # the picture: timed video above the effect clip (z 4), or a still inside it
    still = ""
    rect = f"inset:auto; left:{vx:.0f}px; top:{vy:.0f}px; width:{vw:.0f}px; height:{vh:.0f}px; border-radius:6px;"
    if src and fit.is_video(src):
        _, vsel = fit.media(X, cid, "cvv", src, t, d, "cv-vid", focus=p.get("focus"), fill="cover", z=4, start=start, extra_style=rect)
    else:
        vsel = None
        if src:
            m, _ = fit.media(X, cid, "cvs", src, t, d, "cv-still", focus=p.get("focus"), fill="cover", box_ar=ar)
            still = f'<div class="cv-sbox" style="left:{vx:.0f}px; top:{vy:.0f}px; width:{vw:.0f}px; height:{vh:.0f}px">{m}</div>'
    title = str(p.get("title", ""))
    X.used_text.update(title + "▶引用片段0123456789:/")
    bezel = (f'<div class="cv-bz" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">'
             f'<div class="cv-tb"><i>▶</i><span>{X.rich(title)}</span><em>引用片段</em></div></div>{still}')
    # over the picture: subtitle / caption, scrub bar, timecode (its own clip above the video)
    sub = p.get("quote")
    sub_txt = f"“{sub}”" if sub else ""
    sf = C.fitted(X, sub_txt, vw * 0.86, vh * 0.26, 40 if not P else 36, 18, max_lines=2, lh=1.3) if sub_txt else None
    end = start + min(d, max(dur - start, 0.1))
    X.used_text.update(_tc(start) + _tc(end) + _tc(dur))
    ov = (f'<div class="cv-ov" style="left:{vx:.0f}px; top:{vy:.0f}px; width:{vw:.0f}px; height:{vh:.0f}px">'
          + (f'<div class="cv-sub" style="font-size:{sf.px}px">{C.lines(X, sf)}</div>' if sf else "")
          + f'<div class="cv-ctl"><span class="cv-tc">{_tc(start)}</span><div class="cv-track"><i class="cv-buf"></i><i class="cv-prog"></i><span class="cv-kw"><b class="cv-knob"></b></span></div><span>{_tc(dur)}</span></div></div>')
    X.clip(f"{cid}o", t, d, ov, "cv-layer", 5, track=22)
    # info column
    kick = p.get("kicker", "视频引用")
    tf = C.fitted(X, title, iw, ih * 0.2, 52 if not P else 44, 22, max_lines=2 if P else 3, lh=1.18)
    meta = [x for x in (str(p.get("source", "")), str(p.get("year", "")), str(p.get("license", ""))) if x and x != "None"]
    cap = p.get("caption", "")
    if p.get("hl") and p["hl"] in str(cap) and "*" not in str(cap): cap = str(cap).replace(p["hl"], f"*{p['hl']}*", 1)
    cf = C.fitted(X, cap, iw, ih * (0.3 if not P else 0.24), 34 if not P else 32, 18, max_lines=4 if not P else 2, lh=1.35) if cap else None
    X.used_text.update(kick + "".join(meta) + "片段")
    info = (f'<div class="cv-info" style="left:{ix:.0f}px; top:{iy:.0f}px; width:{iw:.0f}px; height:{ih:.0f}px">'
            f'<div class="ct-kick">{X.rich(kick)}</div><div class="cv-t" style="font-size:{tf.px}px">{C.lines(X, tf)}</div>'
            + "".join(f'<div class="cv-m">{X.rich(m)}</div>' for m in meta)
            + (f'<div class="cv-cap" style="font-size:{cf.px}px">{C.lines(X, cf)}</div>' if cf else "")
            + f'<div class="cv-range">▶ {_tc(start)} – {_tc(end)}</div></div>')
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-video", """
.cv-bz { position:absolute; background:#0d0d0d; border-radius:16px; box-shadow:0 30px 80px rgba(0,0,0,.4), 0 0 0 1.5px rgba(255,255,255,.06); }
.cv-tb { position:absolute; left:12px; right:12px; top:0; height:44px; display:flex; align-items:center; gap:12px; color:#ddd; font:600 18px var(--f-body); }
.cv-tb i { font-style:normal; color:#e2321f; font-size:16px; } .cv-tb span { flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.cv-tb em { font-style:normal; font:700 14px var(--f-mono, monospace); letter-spacing:.12em; color:#111; background:#f6ce3a; padding:3px 9px; border-radius:4px; }
.cv-sbox { position:absolute; overflow:hidden; border-radius:6px; } .cv-sbox .cv-still { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.cv-layer { pointer-events:none; }
.cv-ov { position:absolute; border-radius:6px; overflow:hidden; }
.cv-ov::after { content:''; position:absolute; left:0; right:0; bottom:0; height:38%; background:linear-gradient(0deg, rgba(0,0,0,.72), rgba(0,0,0,0)); }
.cv-sub { position:absolute; left:7%; right:7%; bottom:64px; z-index:1; text-align:center; font-family:var(--f-body); font-weight:800; line-height:1.3; color:#fff; text-shadow:0 2px 12px rgba(0,0,0,.6); }
.cv-sub .ct-l { overflow:hidden; }
.cv-ctl { position:absolute; left:18px; right:18px; bottom:16px; z-index:1; display:flex; align-items:center; gap:14px; font:600 16px var(--f-mono, monospace); color:#eee; }
.cv-track { position:relative; flex:1; height:6px; border-radius:3px; background:rgba(255,255,255,.25); }
.cv-buf { position:absolute; left:0; top:0; bottom:0; width:72%; border-radius:3px; background:rgba(255,255,255,.35); }
.cv-prog { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:3px; background:#e2321f; transform-origin:0 50%; }
.cv-kw { position:absolute; inset:0; }
.cv-knob { position:absolute; top:50%; left:0; width:16px; height:16px; margin:-8px 0 0 -8px; border-radius:50%; background:#fff; box-shadow:0 1px 6px rgba(0,0,0,.4); }
.cv-info { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:16px; color:var(--fg); }
.cv-t { font-family:var(--f-quote, var(--f-display)); font-weight:800; line-height:1.18; }
.cv-m { font:600 19px var(--f-mono, monospace); color:var(--muted); letter-spacing:.03em; }
.cv-cap { font-family:var(--f-body); font-weight:700; line-height:1.35; border-left:6px solid var(--accent); padding-left:18px; margin-top:6px; }
.cv-range { align-self:flex-start; font:700 18px var(--f-mono, monospace); color:var(--bg); background:var(--fg); padding:5px 12px; border-radius:6px; }
#root.v .cv-info { justify-content:flex-start; gap:12px; }
""")
    _clip(X, cid, t, d, f'<div class="ct-root">{bezel}{info}</div>', p)
    S = f"#{cid}"
    player = f"{S} .cv-bz, #{cid}o .cv-ov" + (f", {vsel}" if vsel else f", {S} .cv-sbox")
    X.tw(f'tl.fromTo("{player}", {{y:70, scale:0.93, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.75, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    X.tw(f'tl.from("{S} .cv-info > *", {{x:40, opacity:0, duration:0.55, ease:"expo.out", stagger:0.08}}, {t + 0.25:.3f});')
    run = max(0.2, min(d - 0.35, end - start))
    p0, p1 = start / max(dur, 0.1), min(1.0, end / max(dur, 0.1))
    X.tw(f'tl.fromTo("#{cid}o .cv-prog", {{scaleX:{p0:.4f}}}, {{scaleX:{p1:.4f}, duration:{run:.2f}, ease:"none"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("#{cid}o .cv-kw", {{xPercent:{p0 * 100:.2f}}}, {{xPercent:{p1 * 100:.2f}, duration:{run:.2f}, ease:"none"}}, {t + 0.3:.3f});')
    X.tw(f'(()=>{{const o={{v:{start}}}, el=document.querySelector("#{cid}o .cv-tc"); tl.to(o, {{v:{start + run:.2f}, duration:{run:.2f}, ease:"none", onUpdate:()=>{{const s=Math.max(0,Math.round(o.v)); el.textContent=String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");}}}}, {t + 0.3:.3f});}})();')
    if sf: X.tw(f'tl.from("#{cid}o .cv-sub .ct-l > *", {{yPercent:110, duration:0.55, ease:"expo.out", stagger:0.08}}, {t + 0.9:.3f});')
    if cf: C.marker(X, f"{S} .cv-cap", t + 1.2, each=0.4)
    hold = t + 0.8
    X.tw(f'tl.to("{player}", {{scale:1.025, duration:{max(0.2, t + d - hold):.2f}, ease:"none"}}, {hold:.3f});')


FX = {"cite_video": cite_video}
