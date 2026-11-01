"""直播切片 Clip Style (直播 / 访谈切片号的通用包装：顶部大标题条 + 回放红点 + 名牌 + 粗描边黄字幕 + 飘屏评论
与点赞爱心): the footage plays (video or still, any aspect), the title ribbon slams in, the 「直播回放」 pill blinks,
the name tag slides, the spoken line appears as the big stroked subtitle (the page caption is hidden for this beat
so it is not doubled), comments drift up the side and hearts float from the corner. Generic — no platform's UI.

Adapts: footage video / image of any aspect (transparent video sits on a soft stage), title 1 glyph to ~28 (≤ 2
lines), subtitle = `quote` or the beat's `line` (≤ 2 lines), 0–8 comments, name / viewers / time optional.
p: video | image · title · quote · name · role · live_text (直播回放) · viewers · time · comments · hearts (true) · note
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

RED = "#e8312a"
CSS = """
.fx .cs { position:absolute; inset:0; }
.fx .cs .cs-frame { position:absolute; border-radius:1.4vmin; overflow:hidden; }
.fx .cs .cs-frame img { width:100%; height:100%; object-fit:cover; display:block; }
.fx .cs .cs-tt { position:absolute; font-family:var(--f-display); font-weight:900; color:#fff; line-height:1.12; text-align:center;
  -webkit-text-stroke:.16em #111; paint-order:stroke fill; }
.fx .cs .cs-tt .gl { display:block; white-space:nowrap; }
.fx .cs .cs-rib { position:absolute; background:var(--accent); border-radius:.6vmin; transform-origin:50% 50%; }
.fx .cs .cs-live { position:absolute; display:flex; align-items:center; gap:.45em; font-family:var(--f-body); font-weight:700; color:#fff; background:rgba(0,0,0,.55); border-radius:999px; padding:.2em .75em; white-space:nowrap; }
.fx .cs .cs-live i { width:.55em; height:.55em; border-radius:50%; background:""" + RED + """; }
.fx .cs .cs-live span { opacity:.8; font-family:var(--f-mono, monospace); font-weight:500; font-size:.85em; }
.fx .cs .cs-name { position:absolute; display:flex; flex-direction:column; color:#fff; background:linear-gradient(90deg, rgba(0,0,0,.72), rgba(0,0,0,0)); padding:.35em 2.4em .35em .7em; border-left:.3em solid var(--accent); white-space:nowrap; }
.fx .cs .cs-name b { font-family:var(--f-display); font-weight:900; }
.fx .cs .cs-name span { font-family:var(--f-body); font-size:.62em; opacity:.85; }
.fx .cs .cs-sub { position:absolute; font-family:var(--f-display); font-weight:900; color:#ffd400; line-height:1.18; text-align:center;
  -webkit-text-stroke:.14em #111; paint-order:stroke fill; }
.fx .cs .cs-sub .gl { display:block; white-space:nowrap; }
.fx .cs .cs-cm { position:absolute; display:flex; flex-direction:column; gap:.45em; overflow:hidden; }
.fx .cs .cs-cm div { align-self:flex-start; font-family:var(--f-body); font-weight:500; color:#fff; background:rgba(0,0,0,.45); border-radius:.9em; padding:.25em .7em; white-space:nowrap; }
.fx .cs .cs-cm div b { color:#ffd400; font-weight:700; margin-right:.35em; }
.fx .cs .cs-ht { position:absolute; color:#ff4d6d; font-style:normal; line-height:1; }
"""
HEART = '<svg viewBox="0 0 24 24" width="100%" height="100%"><path d="M12 21s-7.5-4.6-9.6-9.3C.8 8 3 4 6.8 4c2.2 0 3.6 1.2 5.2 3 1.6-1.8 3-3 5.2-3C21 4 23.2 8 21.6 11.7 19.5 16.4 12 21 12 21z" fill="currentColor"/></svg>'


def clip_style(X, cid, t, d, p):
    P = X.portrait
    src = p.get("video") or p.get("image")
    title = fit.as_text(p.get("title"))
    quote = fit.as_text(p.get("quote") or p.get("line") or "")
    name, role = fit.as_text(p.get("name")), fit.as_text(p.get("role"))
    live = fit.as_text(p.get("live_text") or "直播回放")
    meta = " · ".join(x for x in (fit.as_text(p.get("time")), fit.as_text(p.get("viewers"))) if x)
    comments = fit.as_list(p.get("comments"))[:8]
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.2)
    X.css("fx-gn", G.CSS); X.css("fx-cs", CSS)
    if p.get("line"):   # the big subtitle IS the line: hide this beat's page caption so it is not doubled
        X.css(f"fx-cs-cap-{cid}", f"#{cid}c .cap {{ display:none; }}")
    # the footage frame
    if P:
        fx_, fy, fw = x, y, w
        fh = min(h * (0.9 if p.get("line") else 0.74), w * 1.4)   # no page caption under it → the frame takes that room
    else:
        fx_, fy, fw, fh = x, y, w, h
    vid = fit.is_video(src)
    transparent_src = vid and str(src).lower().endswith(".webm")
    bg = "radial-gradient(circle at 50% 38%, color-mix(in srgb, var(--accent) 45%, #2a2320), #141210 72%)"
    stage = (f'<div class="cs-frame" style="left:{fx_:.0f}px; top:{fy:.0f}px; width:{fw:.0f}px; height:{fh:.0f}px; '
             f'background:{"transparent" if vid else bg}">')
    vsel = None
    if vid:   # the stage colour rides on the video's own wrapper, so it sits under the footage; overlays stay above
        cover = "contain" if transparent_src else "cover"
        _, vsel = fit.media(X, cid, "foot", src, t, d, "csv", z=3,
                            extra_style=f"inset:auto; left:{fx_:.0f}px; top:{fy:.0f}px; width:{fw:.0f}px; height:{fh:.0f}px; border-radius:1.4vmin; background:{bg};")
        X.css(f"fx-cs-fit-{cid}", f"#{cid}_foot video {{ object-fit:{cover} !important; object-position:50% 100% !important; }}")
        stage += "</div>"
    elif src:
        stage += f'<img src="{X.asset(src)}" alt=""></div>'
    else:
        stage += "</div>"
    html = []
    # title ribbon across the top of the footage
    tt_html = rib = ""
    rib_bot = fy
    if title:
        tf = fit.fit_text(title, fw * 0.86, fh * (0.2 if not P else 0.24), G.vm(X, 7.2 if not P else 7.6), G.vm(X, 3.6), max_lines=2 if not P else 3, lh=1.12)
        tw_ = max(fit.width(l) for l in tf.lines) * tf.px
        ty = fy + G.vm(X, 3.2)
        rh = tf.n * tf.px * 1.12 + tf.px * 0.5
        rib = f'<i class="cs-rib" style="left:{fx_ + (fw - tw_) / 2 - tf.px * 0.5:.0f}px; top:{ty - tf.px * 0.2:.0f}px; width:{tw_ + tf.px:.0f}px; height:{rh:.0f}px; transform:rotate(-1.5deg)"></i>'
        tt_html = f'<div class="cs-tt" style="left:{fx_:.0f}px; width:{fw:.0f}px; top:{ty:.0f}px; font-size:{tf.px}px">{G.line_html(X, tf)}</div>'
        rib_bot = ty - tf.px * 0.2 + rh
    lpx = G.vm(X, 2.4)
    live_html = (f'<div class="cs-live" style="left:{fx_ + G.vm(X, 2):.0f}px; top:{(rib_bot + G.vm(X, 1.4) if title else fy + G.vm(X, 2)) if P else fy + G.vm(X, 2):.0f}px; font-size:{lpx:.0f}px">'
                 f'<i></i>{X.rich(live)}{f"<span>{X.rich(meta)}</span>" if meta else ""}</div>')
    if title and not P:   # in 16:9 the pill goes top-right so the ribbon has the centre
        lw = (fit.width(live) + (fit.width(meta) * 0.85 + 1 if meta else 0) + 2.4) * lpx
        live_html = live_html.replace(f"left:{fx_ + G.vm(X, 2):.0f}px", f"left:{fx_ + fw - lw - G.vm(X, 2):.0f}px")
    # subtitle near the bottom of the footage
    sub_html = name_html = ""
    if quote:
        sf = fit.fit_text(quote, fw * 0.9, fh * 0.2, G.vm(X, 6 if not P else 6.6), G.vm(X, 3.2), max_lines=2, lh=1.18)
        sy = fy + fh - sf.n * sf.px * 1.18 - G.vm(X, 3)
        sub_html = f'<div class="cs-sub" style="left:{fx_:.0f}px; width:{fw:.0f}px; top:{sy:.0f}px; font-size:{sf.px}px">{G.line_html(X, sf)}</div>'
        top_sub = sy
    else:
        top_sub = fy + fh
    if name:
        npx = G.vm(X, 3.2)
        name_html = (f'<div class="cs-name" style="left:{fx_ + G.vm(X, 2):.0f}px; top:{top_sub - npx * 2.6 - g:.0f}px; font-size:{npx:.0f}px">'
                     f'<b>{X.rich(name)}</b>{f"<span>{X.rich(role)}</span>" if role else ""}</div>')
    cm_html = ""
    if comments:
        cpx = G.vm(X, 2.4)
        cw_ = fw * (0.3 if not P else 0.62)
        cx_ = fx_ + fw - cw_ - G.vm(X, 2) if not P else fx_ + G.vm(X, 2)
        cy_ = fy + fh * 0.22 if not P else max(fy + fh * 0.42, rib_bot + lpx * 2.8 + g)
        ch_ = (top_sub - g - (G.vm(X, 3.2) * 2.8 if (name and P) else 0)) - cy_
        rows = []
        for it in comments:
            if isinstance(it, (list, tuple)): u, c = str(it[0]), str(it[1]) if len(it) > 1 else ""
            else:
                u, sep, c = str(it).partition("：")
                if not sep: u, c = "", str(it)
            cf = fit.fit_text(c, cw_ - cpx * (len(u) + 2), cpx * 1.3, cpx, cpx * 0.8, max_lines=1)
            rows.append(f'<div data-safe="ignore">{f"<b>{X.rich(u)}</b>" if u else ""}{X.rich(cf.lines[0])}</div>')
        cm_html = f'<div class="cs-cm" data-layout-allow-overflow style="left:{cx_:.0f}px; top:{cy_:.0f}px; width:{cw_:.0f}px; height:{max(ch_, cpx * 2):.0f}px; font-size:{cpx:.0f}px">{"".join(rows)}</div>'
    hearts = ""
    if p.get("hearts", True):
        rs = G.seeded(X, 24, f"{cid}-h")
        hx0 = fx_ + fw - G.vm(X, 10)
        for k in range(8):
            sz = G.vm(X, 3 + rs[k] * 2.6)
            hearts += f'<i class="cs-ht" data-k="{k}" data-safe="ignore" style="left:{hx0 + rs[8 + k] * G.vm(X, 6):.0f}px; top:{top_sub - sz:.0f}px; width:{sz:.0f}px; height:{sz:.0f}px; opacity:0">{HEART}</i>'
    note = fit.as_text(p.get("note"))
    if note: html.append(G.note_tag(X, note, fx_ + G.vm(X, 2), fy + fh + G.vm(X, 1) if P else fy + fh - G.vm(X, 4.6), G.vm(X, 1.9)))
    inner = stage + rib + tt_html + live_html + cm_html + name_html + sub_html + hearts + "".join(html)
    _clip(X, cid, t, d, f'<div class="cs">{inner}</div>', p, transparent=bool(vsel))
    if vsel: G.paint_bg(X, cid, t, d, p)
    if vsel:   # the footage sits under the overlays but over the painted stage: overlays need their own layer above it
        X.css(f"fx-cs-z-{cid}", f"#{cid} {{ z-index:4 !important; }} #{cid} .cs-frame {{ z-index:0; }}")
    s = f"#{cid} .cs"
    X.tw(f'tl.from("{s} .cs-frame", {{opacity:0, scale:1.04, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    if vsel: X.tw(f'tl.from("{vsel}", {{opacity:0, duration:0.4}}, {t + 0.05:.3f});')
    elif src: X.tw(f'tl.fromTo("{s} .cs-frame img", {{scale:1.0}}, {{scale:1.08, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if title:
        X.tw(f'tl.fromTo("{s} .cs-rib", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"expo.out"}}, {t + 0.15:.3f});')
        X.tw(f'tl.fromTo("{s} .cs-tt", {{scale:1.7, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"power4.in", immediateRender:true}}, {t + 0.2:.3f});')
        X.sfx(t + 0.48, "slam")
    X.tw(f'tl.from("{s} .cs-live", {{opacity:0, x:-14, duration:0.35}}, {t + 0.3:.3f});')
    n = max(1, int((d - 0.6) / 1.0))
    X.tw(f'tl.fromTo("{s} .cs-live i", {{opacity:1}}, {{opacity:0.2, duration:0.5, ease:"steps(1)", yoyo:true, repeat:{n * 2 - 1}, immediateRender:false}}, {t + 0.6:.3f});')
    if name: X.tw(f'tl.from("{s} .cs-name", {{x:-60, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.5:.3f});')
    if quote:
        X.tw(f'tl.from("{s} .cs-sub .gl", {{scale:0.6, opacity:0, duration:0.25, ease:"back.out(2.6)", stagger:0.12}}, {t + 0.45:.3f});')
    if comments:
        X.tw(f'tl.from("{s} .cs-cm div", {{y:30, opacity:0, duration:0.35, ease:"expo.out", stagger:{max(0.18, min(0.5, (d - 1.2) / len(comments))):.2f}}}, {t + 0.6:.3f});')
        X.tw(f'tl.fromTo("{s} .cs-cm", {{y:0}}, {{y:{-G.vm(X, 4):.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    if p.get("hearts", True):
        rs = G.seeded(X, 24, f"{cid}-hm")
        for k in range(8):
            tk = t + 0.5 + k * max(0.2, (d - 1.6) / 8)
            X.tw(f'tl.fromTo("{s} .cs-ht[data-k=\'{k}\']", {{opacity:0, y:0, x:0, scale:0.6}}, {{keyframes:[{{opacity:1, scale:1, duration:0.2}}, '
                 f'{{y:{-G.vm(X, 22 + rs[k] * 14):.0f}, x:{G.vm(X, (rs[8 + k] - 0.5) * 8):.0f}, opacity:0, duration:1.1, ease:"sine.out"}}], immediateRender:false}}, {tk:.3f});')


FX = {"clip_style": clip_style}
