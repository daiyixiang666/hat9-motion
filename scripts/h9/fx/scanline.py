"""扫描线逐块标注 Scanline (Terminator / 科技纪录片的扫描 HUD；AE 的 scan-line reveal；扫描文件找重点):
a glowing scan line sweeps across a document or picture; the area behind it turns into a faint scanned grid, and
each target block lights up the moment the line crosses it — corner brackets snap on, a label chip pops out with
a mono readout — the rest of the picture dims a touch so the blocks read.

Adapts: an image of any aspect (document pages, screenshots, photos), or a paragraph of text as the "document";
1–8 blocks given in % (sorted along the scan direction automatically); labels a word to a short line; down or
across; timing from "at" cues (one per block) or the line's own travel.
p: image | text · blocks: [{box: [x,y,w,h] %, label, value}] · dir ("down" | "right") · at
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit

CSS = """
.fx .sl2 { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .sl2 .sl-doc { position:absolute; overflow:hidden; border-radius:.6vmin; box-shadow:0 2vmin 5vmin rgba(0,0,0,.3); background:#f4f1ea; }
.fx .sl2 .sl-doc img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .sl2 .sl-doc .sl-txt { position:absolute; inset:6%; font-family:var(--f-quote, var(--f-body)); color:#1b1b1b; line-height:1.7; }
.fx .sl2 .sl-dim { position:absolute; inset:0; background:rgba(0,0,0,.28); opacity:0; }
.fx .sl2 .sl-grid { position:absolute; inset:0; background-image:linear-gradient(rgba(0,200,255,.18) 1px, transparent 1px), linear-gradient(90deg, rgba(0,200,255,.18) 1px, transparent 1px);
  background-size:2.4vmin 2.4vmin; background-color:rgba(0,180,255,.06); }
.fx .sl2 .sl-line { position:absolute; background:#38d9ff; box-shadow:0 0 1.6vmin .4vmin rgba(56,217,255,.85), 0 0 5vmin 1vmin rgba(56,217,255,.35); }
.fx .sl2 .sl-blk { position:absolute; }
.fx .sl2 .sl-blk i { position:absolute; width:1.6vmin; height:1.6vmin; border-color:#38d9ff; border-style:solid; border-width:0; }
.fx .sl2 .sl-blk i:nth-child(1) { left:0; top:0; border-left-width:.4vmin; border-top-width:.4vmin; }
.fx .sl2 .sl-blk i:nth-child(2) { right:0; top:0; border-right-width:.4vmin; border-top-width:.4vmin; }
.fx .sl2 .sl-blk i:nth-child(3) { left:0; bottom:0; border-left-width:.4vmin; border-bottom-width:.4vmin; }
.fx .sl2 .sl-blk i:nth-child(4) { right:0; bottom:0; border-right-width:.4vmin; border-bottom-width:.4vmin; }
.fx .sl2 .sl-blk .fill { position:absolute; inset:0; background:rgba(56,217,255,.16); }
.fx .sl2 .sl-chip { position:absolute; white-space:nowrap; font-family:var(--f-body); font-weight:800; color:#06131a; background:#38d9ff; border-radius:.5vmin; }
.fx .sl2 .sl-chip small { font-size:1em; font-family:var(--f-mono, monospace); font-weight:600; margin-left:.6em; opacity:.8; }
"""


def scanline(X, cid, t, d, p):
    P = X.portrait
    img = p.get("image")
    text = fit.as_text(p.get("text") or "")
    blocks = [b for b in fit.as_list(p.get("blocks")) if isinstance(b, dict)][:8]
    down = (p.get("dir") or "down") != "right"
    x, y, w, h = S.box(X, p)
    ar = fit.aspect(X, img, 0.77) if img else (0.8 if not P else 0.72)
    # leave room for chips on one side in 16:9
    room_w = w * (0.94 if P else 0.6)
    bw = min(room_w, h * 0.94 * ar); bh = bw / ar
    if bh > h * 0.94: bh = h * 0.94; bw = bh * ar
    dx = x + (w - bw) / 2 - (0 if P else w * 0.16)
    dy = y + (h - bh) / 2
    key = (lambda b: b.get("box", [0, 0, 0, 0])[1]) if down else (lambda b: b.get("box", [0, 0, 0, 0])[0])
    blocks = sorted(blocks, key=key)
    X.css("fx-sl2", CSS)
    inner = f'<img src="{X.asset(img)}" alt="">' if img else ""
    if not img:
        tf = fit.fit_text(text or "……", bw * 0.88, bh * 0.88, S.vm(X, 3.6), S.vm(X, 1.6), max_lines=12, lh=1.7)
        inner = f'<div class="sl-txt" style="font-size:{tf.px}px">' + "<br>".join(X.rich(l) for l in tf.lines) + "</div>"
    lw = S.vm(X, 0.5)
    html = [f'<div class="sl-doc" style="left:{dx:.0f}px; top:{dy:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">{inner}<div class="sl-dim"></div>'
            f'<div class="sl-grid" style="clip-path:inset(0 {"0 100% 0" if down else "100% 0 0"})"></div>'
            + (f'<div class="sl-line" style="left:0; right:0; top:0; height:{lw:.0f}px"></div>' if down else f'<div class="sl-line" style="top:0; bottom:0; left:0; width:{lw:.0f}px"></div>')
            + "</div>"]
    cpx = S.vm(X, 2.8 if P else 2.6)
    for k, b in enumerate(blocks):
        bx0, by0, bw0, bh0 = b.get("box", [10, 10, 30, 10])
        px_, py_, pw_, ph_ = dx + bw * bx0 / 100, dy + bh * by0 / 100, bw * bw0 / 100, bh * bh0 / 100
        html.append(f'<div class="sl-blk" data-k="{k}" style="left:{px_:.0f}px; top:{py_:.0f}px; width:{pw_:.0f}px; height:{ph_:.0f}px; opacity:0"><i></i><i></i><i></i><i></i><b class="fill"></b></div>')
        lab, val = fit.as_text(b.get("label")), fit.as_text(b.get("value"))
        if lab:
            if P:
                cx_, cy_ = dx + bw * 0.02, (py_ + ph_ + S.vm(X, 1.2)) if (py_ + ph_ + cpx * 2 < dy + bh) else (py_ - cpx * 2)
            else:
                cx_, cy_ = dx + bw + S.vm(X, 3), py_ + ph_ / 2 - cpx * 0.9
            maxw = (x + w - cx_) if not P else bw
            lf = fit.fit_text(lab + (" " + val if val else ""), maxw, cpx * 1.8, cpx, S.vm(X, 2.6), max_lines=1)
            html.append(f'<div class="sl-chip" data-k="{k}" style="left:{cx_:.0f}px; top:{cy_:.0f}px; font-size:{lf.px}px; padding:{lf.px * 0.3:.0f}px {lf.px * 0.6:.0f}px; opacity:0">'
                        f'{X.rich(lab)}{f"<small>{X.rich(val)}</small>" if val else ""}</div>')
    _clip(X, cid, t, d, f'<div class="sl2">{"".join(html)}</div>', p)
    s = f"#{cid} .sl2"
    X.tw(f'tl.from("{s} .sl-doc", {{opacity:0, y:30, scale:0.96, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    t0, t1 = t + 0.5, t + max(1.2, d - 0.6)
    travel = bh if down else bw
    prop = "y" if down else "x"
    X.tw(f'tl.fromTo("{s} .sl-line", {{{prop}:0}}, {{{prop}:{travel - lw:.0f}, duration:{t1 - t0:.2f}, ease:"none"}}, {t0:.3f});')
    X.tw(f'tl.fromTo("{s} .sl-grid", {{clipPath:"inset(0 {"0 100% 0" if down else "100% 0 0"})"}}, {{clipPath:"inset(0 0 0% 0)", duration:{t1 - t0:.2f}, ease:"none"}}, {t0:.3f});')
    X.tw(f'tl.to("{s} .sl-dim", {{opacity:1, duration:0.5}}, {t0:.3f});')
    X.tw(f'tl.to("{s} .sl-line", {{opacity:0, duration:0.3}}, {t1:.3f});')
    X.sfx(t0, "whoosh_soft")
    at = fit.as_list(p.get("at"))
    for k, b in enumerate(blocks):
        pos = (b.get("box", [0, 0, 0, 0])[1] if down else b.get("box", [0, 0, 0, 0])[0]) / 100
        tk = t0 + (t1 - t0) * pos
        if k < len(at) and X.chars:
            try: tk = float(X.T(at[k], t))
            except SystemExit: pass
        X.tw(f'tl.fromTo("{s} .sl-blk[data-k=\'{k}\']", {{opacity:0, scale:1.15}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .sl-chip[data-k=\'{k}\']", {{opacity:0, x:-16}}, {{opacity:1, x:0, duration:0.3, ease:"expo.out", immediateRender:false}}, {tk + 0.08:.3f});')
        X.sfx(tk, "click")


FX = {"scanline": scanline}
