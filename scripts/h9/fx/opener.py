"""栏目片头 Series Opener (系列栏目的固定片头：期数 + 栏目名 + 本期标题；VideoHive Openers 31,965 个，
Fast Intro 2.6K / Corporate Typography Pack 2.8K): guide lines draw out from the centre, the episode number rolls
digit by digit to its value (odometer reels on steps), the show name tracks in, the title rises out of its mask,
a light sweep crosses it and the channel badge settles; the camera keeps creeping for the rest of the beat.

Adapts: ep any number or short code (1–4 digits roll; "EP.07", "第 7 期" accepted), show 1–12 glyphs, title 1 glyph
to ~36 (≤ 2 lines; 3 in 9:16), sub / channel / en optional.
p: show · ep · title · sub · channel · en
"""
from h9.aefx import _clip
import importlib.util, pathlib, re, sys
if "h9fx__genre" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__genre", pathlib.Path(__file__).with_name("_genre.py"))
    sys.modules["h9fx__genre"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__genre"])
G = sys.modules["h9fx__genre"]; S = G.S
from h9 import fit

CSS = """
.fx .op { position:absolute; inset:0; }
.fx .op .op-cam { position:absolute; inset:0; transform-origin:50% 50%; }
.fx .op .op-ln { position:absolute; background:color-mix(in srgb, var(--fg) 18%, transparent); }
.fx .op .op-ep { position:absolute; display:flex; align-items:flex-end; font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--fg); line-height:1; }
.fx .op .op-ep .pre { font-family:var(--f-mono, monospace); font-weight:700; font-size:.16em; letter-spacing:.2em; color:var(--muted); margin-right:.6em; padding-bottom:.9em; white-space:nowrap; }
.fx .op .op-ep .reel { display:inline-block; overflow:hidden; height:1em; }
.fx .op .op-ep .reel i { display:block; font-style:normal; height:1em; line-height:1em; text-align:center; }
.fx .op .op-ep .suf { font-family:var(--f-display); font-size:.22em; font-weight:900; padding-bottom:.55em; margin-left:.25em; white-space:nowrap; }
.fx .op .op-bar { position:absolute; background:var(--accent); transform-origin:50% 0; }
.fx .op .op-show { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--accent); white-space:nowrap; }
.fx .op .op-show i { display:inline-block; font-style:normal; }
.fx .op .op-t { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.1; overflow:hidden; }
.fx .op .op-t .gl { display:block; overflow:hidden; white-space:nowrap; padding-bottom:.06em; } .fx .op .gl > span { display:inline-block; }
.fx .op .op-sweep { position:absolute; left:0; top:0; bottom:0; width:30%; background:linear-gradient(100deg, transparent, rgba(255,255,255,.55), transparent); mix-blend-mode:overlay; }
.fx .op .op-s { position:absolute; font-family:var(--f-body); font-weight:500; color:var(--muted); white-space:nowrap; }
.fx .op .op-en { position:absolute; font-family:var(--f-mono, monospace); color:var(--muted); letter-spacing:.3em; text-transform:uppercase; white-space:nowrap; }
.fx .op .op-ch { position:absolute; display:flex; align-items:center; gap:.5em; font-family:var(--f-display); font-weight:900; color:var(--fg); white-space:nowrap; }
.fx .op .op-ch b { display:inline-grid; place-items:center; width:1.6em; height:1.6em; border-radius:50%; background:var(--fg); color:var(--bg); font-size:.8em; }
"""


def _ep(v):
    s = fit.as_text(v).strip()
    m = re.search(r"\d+", s)
    if not m: return "", s, ""
    return s[:m.start()].strip(), m.group(0), s[m.end():].strip()


def opener(X, cid, t, d, p):
    P = X.portrait
    show = fit.as_text(p.get("show") or "栏目")
    pre, digits, suf = _ep(p.get("ep", ""))
    title = fit.as_text(p.get("title") or p.get("text") or "")
    sub, chn, en = fit.as_text(p.get("sub")), fit.as_text(p.get("channel")), fit.as_text(p.get("en"))
    x, y, w, h = G.area(X, p)
    g = G.vm(X, 2.4)
    X.css("fx-op", CSS)
    html = []
    cxm, cym = x + w / 2, y + h / 2
    # guide lines (a cross through the composition's centre, plus two rails)
    html.append(f'<i class="op-ln h0" style="left:{x:.0f}px; top:{cym:.0f}px; width:{w:.0f}px; height:2px"></i>')
    html.append(f'<i class="op-ln v0" style="left:{(x + w * 0.38) if not P else cxm:.0f}px; top:{y:.0f}px; width:2px; height:{h:.0f}px"></i>')
    nd = max(1, len(digits))
    # the episode block's width in em of its own font size: prefix + digit reels (widest glyph ≈ .72em) + suffix
    pre_em = 0.16 * (fit.width(pre) + 0.2 * len(pre)) + 0.1 if pre and not P else 0
    suf_em = 0.22 * fit.width(suf) + 0.06 if suf else 0
    ep_em = pre_em + nd * 0.72 + suf_em
    shpx = G.vm(X, 4.2 if not P else 4.6)
    if P:
        epx = min(h * 0.26, w * 0.8 / ep_em)
        sw = w
        tf = fit.fit_text(title, sw, h * 0.34, G.vm(X, 9.5), G.vm(X, 4), max_lines=3, lh=1.1) if title else None
        spx_, enpx_ = G.vm(X, 3), G.vm(X, 1.9)
        stack = epx * 1.08 + g * 1.4 + shpx * 1.5 + (tf.n * tf.px * 1.1 + g if tf else 0) + (spx_ * 1.5 if sub else 0) + (enpx_ * 2 if en else 0)
        room = h - (G.vm(X, 2.8) * 2.6 if chn else 0)
        ex, ey = x + (w - ep_em * epx) / 2, y + max(0.0, (room - stack) * 0.42)
        sx, sy = x, ey + epx * 1.08 + g * 1.4
        align = "center"
    else:
        sx, sw = x + w * 0.42, w * 0.58
        ex = x + w * 0.04
        epx = min(h * 0.62, (sx - g * 2.6 - ex) / ep_em)
        ey = cym - epx * 0.55
        sy = None
        align = "left"
    if digits:
        reels = "".join(f'<span class="reel r{j}" data-layout-allow-overflow>{"".join(f"<i>{k}</i>" for k in range(10))}</span>' for j in range(len(digits)))
        html.append(f'<div class="op-ep" style="left:{ex:.0f}px; top:{ey:.0f}px; font-size:{epx:.0f}px">'
                    f'{f"<span class=pre>{X.rich(pre)}</span>" if pre and not P else ""}{reels}{f"<span class=suf>{X.rich(suf)}</span>" if suf else ""}</div>')
    if not P: tf = fit.fit_text(title, sw, h * 0.36, G.vm(X, 9), G.vm(X, 4), max_lines=2, lh=1.1) if title else None
    spx, enpx, chpx = G.vm(X, 3), G.vm(X, 1.9), G.vm(X, 2.8)
    blk = shpx * 1.5 + (tf.n * tf.px * 1.1 + g if tf else 0) + (spx * 1.5 if sub else 0) + (enpx * 2 if en else 0)
    if sy is None: sy = cym - blk / 2
    def xal(wd): return sx + (sw - wd) / 2 if align == "center" else sx
    showw = fit.width(show) * shpx * 1.25
    html.append(f'<div class="op-show" style="left:{xal(showw):.0f}px; top:{sy:.0f}px; font-size:{shpx:.0f}px; letter-spacing:.2em">'
                + "".join(f"<i>{X.rich(ch)}</i>" if ch.strip() else " " for ch in show) + "</div>")
    if not P: html.append(f'<i class="op-bar" style="left:{sx - g * 1.2:.0f}px; top:{sy:.0f}px; width:{G.vm(X, 0.8):.0f}px; height:{blk:.0f}px"></i>')
    yy = sy + shpx * 1.5
    if tf:
        tw_ = max(fit.width(l) for l in tf.lines) * tf.px
        html.append(f'<div class="op-t" style="left:{xal(tw_):.0f}px; top:{yy:.0f}px; font-size:{tf.px}px; text-align:{align}">{G.line_html(X, tf)}<i class="op-sweep"></i></div>')
        yy += tf.n * tf.px * 1.1 + g
    if sub:
        sf = fit.fit_text(sub, sw, spx * 1.3, spx, G.vm(X, 2.2), max_lines=1)
        html.append(f'<div class="op-s" style="left:{xal(fit.width(sf.lines[0]) * sf.px):.0f}px; top:{yy:.0f}px; font-size:{sf.px}px">{X.rich(sf.lines[0])}</div>')
        yy += spx * 1.5
    if en:
        ef = fit.fit_text(en, sw, enpx * 1.3, enpx, enpx * 0.7, max_lines=1, ls=0.3)
        html.append(f'<div class="op-en" style="left:{xal((fit.width(ef.lines[0]) + 0.3 * len(ef.lines[0])) * ef.px):.0f}px; top:{yy:.0f}px; font-size:{ef.px}px">{X.rich(ef.lines[0])}</div>')
    if chn:
        cy_ = y + h - chpx * 2.2
        cwid = (fit.width(chn) + 2.2) * chpx
        chx = x + (w - cwid) / 2 if P else x + w * 0.04
        html.append(f'<div class="op-ch" style="left:{chx:.0f}px; top:{cy_:.0f}px; font-size:{chpx:.0f}px"><b>{X.rich(fit.plain(chn)[:1])}</b>{X.rich(chn)}</div>')
    _clip(X, cid, t, d, f'<div class="op"><div class="op-cam">{"".join(html)}</div></div>', p)
    s = f"#{cid} .op"
    X.tw(f'tl.from("{s} .op-ln.h0", {{scaleX:0, duration:0.7, ease:"expo.inOut"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .op-ln.v0", {{scaleY:0, duration:0.7, ease:"expo.inOut"}}, {t + 0.08:.3f});')
    X.sfx(t, "whoosh_soft")
    if digits:
        for k, ch in enumerate(digits):
            X.tw(f'tl.fromTo("{s} .op-ep .reel.r{k} i", {{yPercent:0}}, {{yPercent:{-100 * int(ch)}, duration:{0.55 + 0.12 * k:.2f}, ease:"steps({max(1, int(ch))})"}}, {t + 0.2 + 0.08 * k:.3f});')
        X.tw(f'tl.from("{s} .op-ep", {{opacity:0, y:30, duration:0.45, ease:"expo.out"}}, {t + 0.15:.3f});')
        X.sfx(t + 0.2, "count")
    X.tw(f'tl.from("{s} .op-show i", {{opacity:0, x:(i)=>({len(show)} / 2 - i) * -18, duration:0.6, ease:"expo.out"}}, {t + 0.45:.3f});')
    if not P: X.tw(f'tl.from("{s} .op-bar", {{scaleY:0, duration:0.5, ease:"expo.out"}}, {t + 0.4:.3f});')
    if tf:
        X.tw(f'tl.from("{s} .op-t .gl > span", {{yPercent:110, duration:0.7, ease:"expo.out", stagger:0.1}}, {t + 0.6:.3f});')
        X.tw(f'tl.fromTo("{s} .op-sweep", {{xPercent:-120}}, {{xPercent:380, duration:0.8, ease:"power2.inOut"}}, {t + 1.25:.3f});')
        X.sfx(t + 0.6, "title")
    if sub: X.tw(f'tl.from("{s} .op-s", {{opacity:0, y:10, duration:0.45}}, {t + 0.95:.3f});')
    if en: X.tw(f'tl.from("{s} .op-en", {{opacity:0, duration:0.5}}, {t + 1.1:.3f});')
    if chn: X.tw(f'tl.from("{s} .op-ch", {{opacity:0, y:16, duration:0.45, ease:"expo.out"}}, {t + 1.2:.3f});')
    X.tw(f'tl.fromTo("{s} .op-cam", {{scale:1.0}}, {{scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.3f});')


FX = {"opener": opener}
