"""下期预告 Next Teaser (系列账号片尾的「下期预告」：封面一闪、标题解码、周五见): a white flash, the next
episode's cover flickers in out of a blur with a short RGB-split jitter, a NEXT tape slaps across its corner, the
episode tag counts up, the title lifts line by line, 1–3 hint chips blink on and the 「周五见」 pill slams last.
No image → a typographic cover (a huge outlined question mark over the title's first glyph).

Adapts: title 1 glyph to ~40 (≤ 3 lines), 0–3 hints, cover image or video of any aspect, ep / when optional.
p: title · kicker (下期预告) · ep (EP.08) · when (周五见) · image | video · hints · note
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .nt { position:absolute; inset:0; }
.fx .nt .nt-cv { position:absolute; overflow:hidden; border-radius:1.2vmin; background:#111; box-shadow:0 3vmin 7vmin rgba(0,0,0,.35); }
.fx .nt .nt-cv img, .fx .nt .nt-cv .ph { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .nt .nt-cv .ph { display:grid; place-items:center; background:radial-gradient(circle at 30% 30%, color-mix(in srgb, var(--accent) 55%, #111), #111 70%); }
.fx .nt .nt-cv .ph b { position:absolute; font-family:var(--f-display); font-weight:900; color:color-mix(in srgb, #fff 10%, transparent); line-height:1; }
.fx .nt .nt-cv .ph i { position:relative; font-style:normal; font-family:var(--f-display); font-weight:900; line-height:1; color:#161412; -webkit-text-stroke:.5vmin #fff; }
.fx .nt .nt-cv .rgb { position:absolute; inset:0; mix-blend-mode:screen; opacity:0; }
.fx .nt .nt-cv .rgb.r { background:rgba(255,40,40,.35); } .fx .nt .nt-cv .rgb.c { background:rgba(40,220,255,.35); }
.fx .nt .nt-cv .scan { position:absolute; left:0; right:0; height:22%; background:linear-gradient(180deg, transparent, rgba(255,255,255,.12), transparent); }
.fx .nt .nt-tape { position:absolute; background:var(--accent); color:var(--bg); font-family:var(--f-mono, monospace); font-weight:700; letter-spacing:.3em;
  text-align:center; white-space:nowrap; transform:rotate(-12deg); box-shadow:0 .8vmin 2vmin rgba(0,0,0,.3); }
.fx .nt .nt-k { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--bg); background:var(--fg); padding:.15em .6em; border-radius:.3em; letter-spacing:.12em; white-space:nowrap; }
.fx .nt .nt-ep { position:absolute; font-family:var(--f-mono, monospace); font-weight:700; color:var(--muted); letter-spacing:.12em; white-space:nowrap; }
.fx .nt .nt-t { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .nt .nt-t .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .nt .gl > span { display:inline-block; }
.fx .nt .nt-h { position:absolute; display:flex; flex-direction:column; gap:.5em; }
.fx .nt .nt-h span { align-self:flex-start; font-family:var(--f-body); font-weight:700; color:var(--fg); border:.14em solid var(--fg); border-radius:999px; padding:.15em .8em; white-space:nowrap; }
.fx .nt .nt-w { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--bg); background:var(--accent); border-radius:999px; padding:.2em .9em; white-space:nowrap; }
.fx .nt .nt-flash { position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none; }
"""


def next_teaser(X, cid, t, d, p):
    P = X.portrait
    title = fit.as_text(p.get("title") or p.get("text") or "下期见")
    kick = fit.as_text(p.get("kicker") or "下期预告")
    ep, when = fit.as_text(p.get("ep")), fit.as_text(p.get("when"))
    hints = [str(x) for x in fit.as_list(p.get("hints"))][:3]
    src = p.get("image") or p.get("video")
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-gn", G.CSS); X.css("fx-nt", CSS)
    html = []
    kpx, hpx, wpx = G.vm(X, 3.2), G.vm(X, 3), G.vm(X, 4.6)
    if P:
        cw, ch = w, min(h * 0.42, w * 0.75)
        tw, th = w, h - ch - g * 1.6
    else:
        cw = w * 0.52; ch = min(h * 0.86, cw * 0.62)
        tw, th = w - cw - g * 2.4, h
    tf = fit.fit_text(title, tw, th * (0.42 if hints else 0.55), G.vm(X, 8.5 if not P else 9), G.vm(X, 3.8), max_lines=3, lh=1.12)
    parts = [kpx * 1.5, tf.n * tf.px * 1.12, (len(hints) * hpx * 2.1 if hints else 0), (wpx * 1.5 if when else 0)]
    if P:   # the text block keeps its size; the cover gives up height when the block needs it
        need = sum(parts) + g * 3
        ch = max(min(ch, h * 0.2), min(ch, h - g * 1.6 - need))
        cx, cy = x, y
        tx, ty, th = x, y + ch + g * 1.6, h - ch - g * 1.6
    else:
        cx, cy = x, y + (h - ch) / 2
        tx, ty = x + cw + g * 2.4, y
    vid_sel = None
    if src and fit.is_video(src):
        _, vid_sel = fit.media(X, cid, "cv", src, t, d, "ntv", extra_style=f"inset:auto; left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px; border-radius:1.2vmin;")
        cover = ""
    elif src:
        cover = f'<img src="{X.asset(src)}" alt="">'
    else:
        qpx = ch * 0.7
        cover = (f'<div class="ph"><b style="font-size:{ch * 0.9:.0f}px">{X.rich(fit.plain(title)[:1])}</b>'
                 f'<i data-layout-allow-overlap style="font-size:{qpx:.0f}px">?</i></div>')
    html.append(f'<div class="nt-cv" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px{"; background:transparent" if vid_sel else ""}">'
                f'{cover}<i class="rgb r"></i><i class="rgb c"></i><i class="scan"></i></div>')
    tpw = min(cw * 0.5, G.vm(X, 30)); tph = G.vm(X, 5)
    html.append(f'<div class="nt-tape" data-layout-allow-overlap style="left:{cx + cw - tpw * 0.82:.0f}px; top:{cy + G.vm(X, 1.6):.0f}px; width:{tpw:.0f}px; height:{tph:.0f}px; '
                f'line-height:{tph:.0f}px; font-size:{tph * 0.46:.0f}px">NEXT</div>')
    note = fit.as_text(p.get("note"))
    if note: html.append(G.note_tag(X, note, cx + G.vm(X, 1.6), cy + ch - G.vm(X, 5), G.vm(X, 2)))
    yy = ty + max(0.0, (th - sum(parts) - g * 3) / 2)
    html.append(f'<div class="nt-k" style="left:{tx:.0f}px; top:{yy:.0f}px; font-size:{kpx:.0f}px">{X.rich(kick)}</div>')
    if ep: html.append(f'<div class="nt-ep" style="left:{tx + (fit.width(kick) * 1.15 + 1.6) * kpx + g:.0f}px; top:{yy + kpx * 0.25:.0f}px; font-size:{kpx * 0.9:.0f}px">{X.rich(ep)}</div>')
    yy += parts[0] + g
    html.append(f'<div class="nt-t" style="left:{tx:.0f}px; top:{yy:.0f}px; font-size:{tf.px}px">{G.line_html(X, tf)}</div>')
    yy += parts[1] + g
    if hints:
        hf = [fit.fit_text(s_, tw - hpx * 2, hpx * 1.4, hpx, G.vm(X, 2.2), max_lines=1) for s_ in hints]
        html.append(f'<div class="nt-h" style="left:{tx:.0f}px; top:{yy:.0f}px; font-size:{min(f.px for f in hf)}px">' + "".join(f"<span>{X.rich(f.lines[0])}</span>" for f in hf) + "</div>")
        yy += parts[2] + g
    if when: html.append(f'<div class="nt-w" style="left:{tx:.0f}px; top:{yy:.0f}px; font-size:{wpx:.0f}px">{X.rich(when)}</div>')
    html.append('<i class="nt-flash"></i>')
    _clip(X, cid, t, d, f'<div class="nt">{"".join(html)}</div>', p, transparent=bool(vid_sel))
    if vid_sel: G.paint_bg(X, cid, t, d, p)
    s = f"#{cid} .nt"
    X.tw(f'tl.fromTo("{s} .nt-flash", {{opacity:0.9}}, {{opacity:0, duration:0.35, ease:"power2.out", immediateRender:false}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .nt-cv", {{opacity:0, scale:1.14, filter:"blur(18px)"}}, {{keyframes:[{{opacity:1, duration:0.06}}, {{opacity:0.2, duration:0.06}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.5, ease:"expo.out"}}]}}, {t + 0.05:.3f});')
    if vid_sel: X.tw(f'tl.from("{vid_sel}", {{opacity:0, duration:0.3}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("{s} .rgb.r", {{opacity:0, x:0}}, {{keyframes:[{{opacity:0.9, x:-14, duration:0.05}}, {{x:10, duration:0.05}}, {{x:-6, duration:0.05}}, {{opacity:0, x:0, duration:0.1}}], immediateRender:false}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("{s} .rgb.c", {{opacity:0, x:0}}, {{keyframes:[{{opacity:0.9, x:12, duration:0.05}}, {{x:-9, duration:0.05}}, {{x:5, duration:0.05}}, {{opacity:0, x:0, duration:0.1}}], immediateRender:false}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("{s} .scan", {{yPercent:-120}}, {{yPercent:520, duration:{max(1.2, d * 0.6):.2f}, ease:"none", repeat:1}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .nt-cv img, {s} .nt-cv .ph b", {{scale:1.0}}, {{scale:1.08, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.sfx(t, "glitch")
    X.tw(f'tl.from("{s} .nt-tape", {{x:120, opacity:0, duration:0.4, ease:"back.out(1.8)"}}, {t + 0.45:.3f});')
    X.tw(f'tl.from("{s} .nt-k", {{scale:0.5, opacity:0, duration:0.35, ease:"back.out(2)"}}, {t + 0.3:.3f});')
    if ep: X.tw(f'tl.fromTo("{s} .nt-ep", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.4, ease:"steps({max(3, len(ep))})"}}, {t + 0.45:.3f});')
    X.tw(f'tl.from("{s} .nt-t .gl > span", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.09}}, {t + 0.5:.3f});')
    X.tw(f'tl.fromTo("{s} .nt-t", {{opacity:1}}, {{keyframes:[{{opacity:0.35, duration:0.05}}, {{opacity:1, duration:0.05}}, {{opacity:0.5, duration:0.04}}, {{opacity:1, duration:0.06}}], immediateRender:false}}, {t + 0.9 + tf.n * 0.09:.3f});')
    if hints:
        X.tw(f'tl.fromTo("{s} .nt-h span", {{opacity:0}}, {{keyframes:[{{opacity:1, duration:0.05}}, {{opacity:0.2, duration:0.05}}, {{opacity:1, duration:0.08}}], stagger:0.22}}, {t + 1.1:.3f});')
        X.sfx(t + 1.1, "click")
    if when:
        tw_ = min(t + d - 0.8, t + 1.4 + len(hints) * 0.22)
        X.tw(f'tl.fromTo("{s} .nt-w", {{scale:1.8, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"power4.in", immediateRender:true}}, {tw_:.3f});')
        X.sfx(tw_ + 0.28, "slam")


FX = {"next_teaser": next_teaser}
