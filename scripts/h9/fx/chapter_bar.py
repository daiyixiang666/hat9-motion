"""章节进度条 Chapter Progress (talkcraft chapter-progress-list / chapter-title-card; B 站长视频的分 P 目录; 所长林超
每章开头的目录页): the whole table of contents in one bar — segments draw on, the finished chapters fill solid,
the current one fills in the accent while its title swells and a 「现在」 pin drops over it; the rest stay muted.

Adapts: 2–8 chapters, titles a word to a phrase (one shared size, ≤ 2 lines), any current index; a horizontal
bar in 16:9, a vertical rail with titles beside it in 9:16.
p: chapters [..] · hl (current, default 0) · title · now ("现在")
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .cb { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .cb .cb-k { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .cb .cb-k .sl, .fx .cb .cb-t .sl { display:block; white-space:nowrap; }
.fx .cb .cb-s { position:absolute; border-radius:.6vmin; background:color-mix(in srgb, var(--fg) 14%, transparent); overflow:hidden; }
.fx .cb .cb-s i { position:absolute; inset:0; background:var(--fg); transform-origin:0 50%; }
.fx .cb .cb-s.now i { background:var(--accent); }
.fx .cb .cb-t { position:absolute; font-family:var(--f-display); font-weight:800; color:var(--fg); line-height:1.2; }
.fx .cb .cb-t small { display:block; font-family:var(--f-num, var(--f-mono)); font-weight:700; color:var(--muted); letter-spacing:.08em; margin-bottom:.6vmin; }
.fx .cb .cb-t.later { color:var(--muted); }
.fx .cb .cb-pin { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--bg); background:var(--accent); border-radius:999px; white-space:nowrap; }
"""


def chapter_bar(X, cid, t, d, p):
    ch = S.flat(p.get("chapters"))[:8] or ["第一章", "第二章"]
    n = len(ch)
    hl = max(0, min(n - 1, int(p.get("hl", 0))))
    title = fit.as_text(p.get("title"))
    x, y, w, h = S.box(X, p)
    kh = 0
    if title:
        kf = fit.fit_text(title, w * 0.9, S.vm(X, 12), S.vm(X, 6 if X.portrait else 5.2), S.vm(X, 3.2), max_lines=2)
        kh = kf.n * kf.px * 1.12 + S.vm(X, 4)
    X.css("fx-cb", CSS)
    P = X.portrait
    gap = S.vm(X, 1.2)
    nopx = S.vm(X, 2.4)
    html, segs = [], []
    if not P:
        segw = (w - gap * (n - 1)) / n
        bh = S.vm(X, 3)
        nopx = S.vm(X, 3)
        tpx, fs = S.fitpx(ch, segw * 0.94, S.vm(X, 18), S.vm(X, 7 if n <= 3 else 6 if n <= 4 else 4.6), S.vm(X, 2.6), max_lines=2)
        nl = max(f.n for f in fs)
        blockh = nopx * 1.6 + nl * tpx * 1.2 + S.vm(X, 3) + bh + S.vm(X, 7)       # titles, bar, the 「现在」 pin
        top = y + kh + max(0, (h - kh - blockh) / 2) * 0.9
        by = top + nopx * 1.6 + nl * tpx * 1.2 + S.vm(X, 3)
        for k in range(n):
            sx = x + k * (segw + gap)
            segs.append((sx, by, segw, bh))
            html.append(f'<div class="cb-t{" later" if k > hl else ""}" data-k="{k}" style="left:{sx:.0f}px; top:{by - S.vm(X, 3) - fs[k].n * tpx * 1.2 - nopx * 1.6:.0f}px; width:{segw:.0f}px; font-size:{tpx}px">'
                        f'<small style="font-size:{nopx:.0f}px">{k + 1:02d}</small>{S.lines(X, fs[k])}</div>')
    else:
        segh = min((h - kh - gap * (n - 1)) / n, S.vm(X, 30))
        bw = S.vm(X, 2.4)
        ppx_ = S.vm(X, 2.8)
        pinw = (fit.width(fit.as_text(p.get("now") or "现在")) + 2.6) * ppx_ + S.vm(X, 2)
        tpx, fs = S.fitpx(ch, w - bw - S.vm(X, 6) - pinw, segh * 0.7, S.vm(X, 6.4), S.vm(X, 2.8), max_lines=2)
        y0 = y + kh + (h - kh - (segh * n + gap * (n - 1))) / 2
        for k in range(n):
            sy = y0 + k * (segh + gap)
            segs.append((x, sy, bw, segh))
            th = fs[k].n * tpx * 1.2 + nopx * 1.6
            html.append(f'<div class="cb-t{" later" if k > hl else ""}" data-k="{k}" style="left:{x + bw + S.vm(X, 4):.0f}px; top:{sy + (segh - th) / 2:.0f}px; font-size:{tpx}px">'
                        f'<small style="font-size:{nopx:.0f}px">{k + 1:02d}</small>{S.lines(X, fs[k])}</div>')
    for k, (sx, sy, sw_, sh_) in enumerate(segs):
        html.append(f'<div class="cb-s{" now" if k == hl else ""}" data-k="{k}" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{sw_:.0f}px; height:{sh_:.0f}px"><i></i></div>')
    sx, sy, sw_, sh_ = segs[hl]
    ppx = S.vm(X, 2.8)
    now = fit.as_text(p.get("now") or "现在")
    if not P: pin = f'<div class="cb-pin" style="left:{sx:.0f}px; top:{sy + sh_ + S.vm(X, 1.6):.0f}px; font-size:{ppx:.0f}px; padding:{ppx * 0.2:.0f}px {ppx * 0.7:.0f}px">▲ {X.rich(now)}</div>'
    else: pin = f'<div class="cb-pin" style="left:{min(x + w, X.W - 120 - ppx * 0.4) - fit.width(now) * ppx - ppx * 2.6:.0f}px; top:{sy + sh_ / 2 - ppx * 0.8:.0f}px; font-size:{ppx:.0f}px; padding:{ppx * 0.2:.0f}px {ppx * 0.7:.0f}px">◀ {X.rich(now)}</div>'
    html.append(pin)
    head = f'<div class="cb-k" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{kf.px}px">{S.lines(X, kf)}</div>' if title else ""
    _clip(X, cid, t, d, f'<div class="cb">{head}{"".join(html)}</div>', p)
    s = f"#{cid} .cb"
    ax = "scaleY" if P else "scaleX"
    org = "50% 0%" if P else "0% 50%"
    if title: X.tw(f'tl.from("{s} .cb-k .sl", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .cb-s", {{{ax}:0, transformOrigin:"{org}", duration:0.45, ease:"expo.out", stagger:0.08}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .cb-t", {{y:24, opacity:0, duration:0.45, ease:"expo.out", stagger:0.08}}, {t + 0.18:.3f});')
    X.tw(f'tl.set("{s} .cb-s i", {{{ax}:0, transformOrigin:"{org}"}}, {t:.3f});')
    t1 = t + 0.5 + 0.08 * n
    for k in range(hl):
        X.tw(f'tl.to("{s} .cb-s[data-k=\'{k}\'] i", {{{ax}:1, duration:0.35, ease:"power2.inOut"}}, {t1 + k * 0.3:.3f});')
        X.tw(f'tl.to("{s} .cb-t[data-k=\'{k}\']", {{opacity:0.5, duration:0.3}}, {t1 + k * 0.3 + 0.2:.3f});')
    tn = t1 + hl * 0.3
    X.tw(f'tl.to("{s} .cb-s[data-k=\'{hl}\'] i", {{{ax}:1, duration:{max(0.6, d * 0.4):.2f}, ease:"power1.inOut"}}, {tn:.3f});')
    X.tw(f'tl.fromTo("{s} .cb-t[data-k=\'{hl}\']", {{scale:1}}, {{scale:1.12, duration:0.45, ease:"back.out(2)", transformOrigin:"0% 100%", immediateRender:false}}, {tn:.3f});')
    X.tw(f'tl.from("{s} .cb-pin", {{y:-24, opacity:0, duration:0.45, ease:"bounce.out"}}, {tn + 0.1:.3f});')
    X.sfx(tn, "click")


FX = {"chapter_bar": chapter_bar}
