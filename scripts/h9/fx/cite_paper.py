"""引用论文 (paper title page — research citations in 知识口播): a white title-page sheet rises on a paper shadow —
venue + arXiv/DOI chip, title, authors, the abstract with the cited sentence swept by a marker, an optional figure;
beside it the year, an optional citation count that counts up, a row of author monograms and a one-line takeaway.

p: title · authors (list | "A, B, C") · venue · year · arxiv | doi (shown as a chip) · abstract · hl (phrase to mark) ·
   figure (image) · cites (number) · takeaway · max_authors (default 6; more → first 3 + "等 N 人")
Adapts: 1 author … 1,000+ (names truncate, monograms cap at 8 + "+N"); titles of 2 words to 3 lines; abstract
from a line to a paragraph (auto size, ≤ 6 lines); figure of any aspect or none; 16:9 = sheet left + facts right,
9:16 = sheet on top + facts below.
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


def cite_paper(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    authors = [a.strip() for a in (fit.as_list(p.get("authors"), ",") if isinstance(p.get("authors"), str) else fit.as_list(p.get("authors")))] if p.get("authors") else []
    n = len(authors); mx = int(p.get("max_authors", 6))
    alist = ", ".join(authors) if n <= mx else ", ".join(authors[:3]) + f" 等 {n} 人"
    if P:
        sx, sy, sw = x0, y0, x1 - x0
        sh = round((y1 - y0) * (0.66 if p.get("figure") else 0.62))
        fx_, fy_, fw, fh = x0, sy + sh + 30, x1 - x0, y1 - (sy + sh + 30)
    else:
        sw = round((x1 - x0) * 0.6); sx, sy, sh = x0, y0, y1 - y0
        fx_, fy_, fw, fh = x0 + sw + 60, y0, x1 - (x0 + sw + 60), y1 - y0
    pad = 44 if not P else 36
    iw = sw - 2 * pad
    fig = p.get("figure")
    fig_h = round(sh * 0.3) if fig else 0
    tf = C.fitted(X, p.get("title", ""), iw, sh * 0.26, 58 if not P else 52, 26, max_lines=3, lh=1.14)
    af = C.fitted(X, alist, iw, 70, 24, 16, max_lines=2, lh=1.4) if alist else None
    abs_txt = str(p.get("abstract", ""))
    if p.get("hl") and p["hl"] in abs_txt and "*" not in abs_txt: abs_txt = abs_txt.replace(p["hl"], f"*{p['hl']}*", 1)
    used = pad * 2 + 44 + tf.n * tf.px * 1.14 + (af.n * af.px * 1.4 if af else 0) + 70 + fig_h
    bf = C.fitted(X, abs_txt, iw, max(80, sh - used), 30 if not P else 30, 17, max_lines=6, lh=1.45) if abs_txt else None
    # the sheet is as tall as its content (never a half-empty page), centred in its column
    content = pad * 2 + 8 + 36 + tf.n * tf.px * 1.14 + (af.n * af.px * 1.4 if af else 0) + ((24 + 8 + bf.n * bf.px * 1.45 + 16) if bf else 0) + (fig_h if fig else 0) + 18 * (2 + bool(af) + bool(bf) + bool(fig))
    full = sh
    sh = round(min(full, max(content, full * (0.5 if not P else 0.42))))
    if not P: sy = y0 + (full - sh) // 2
    else: fy_, fh = sy + sh + 30, y1 - (sy + sh + 30)
    chip = " · ".join(x for x in (str(p.get("venue", "")), str(p.get("arxiv") or p.get("doi") or "")) if x and x != "None")
    X.used_text.update(chip + "Abstract摘要等人")
    figure = ""
    if fig:
        mh, _ = fit.media(X, cid, "cpf", fig, t, d, "cp-fimg", fill="contain", box_ar=iw / max(fig_h, 1))
        figure = f'<div class="cp-fig" style="height:{fig_h}px">{mh}</div>'
    ghost = f'<div class="cp-ghost" style="left:{sx + 18}px; top:{sy + 16}px; width:{sw}px; height:{sh}px"></div>'
    sheet = ghost + (f'<div class="cp-sheet" style="left:{sx}px; top:{sy}px; width:{sw}px; height:{sh}px; padding:{pad}px">'
             + (f'<div class="cp-chip">{X.rich(chip)}</div>' if chip else "")
             + f'<div class="cp-title" style="font-size:{tf.px}px">{C.lines(X, tf, "cp-tl")}</div>'
             + (f'<div class="cp-auth" style="font-size:{af.px}px">{C.lines(X, af)}</div>' if af else "")
             + (f'<div class="cp-abs"><b>Abstract</b><div style="font-size:{bf.px}px">{C.lines(X, bf, "cp-al")}</div></div>' if bf else "")
             + figure + '</div>')
    # facts column / row
    year = str(p.get("year", ""))
    yr_px = min(fw * 0.42, fh * 0.3) if not P else min(fw * 0.28, fh * 0.34)
    mono_n = min(n, 8)
    msz = 66 if not P else 58
    monos = "".join(f'<div class="cp-m">{C.mono_html(X, a, msz)}</div>' for a in authors[:mono_n]) + (f'<div class="cp-m cp-more" style="width:{msz}px; height:{msz}px">+{n - mono_n}</div>' if n > mono_n else "")
    X.used_text.update(f"+{n - mono_n}被引用作者位")
    take = p.get("takeaway")
    used_f = yr_px * 0.9 + (80 if p.get("cites") else 0) + ((msz + 10) * (1 + (mono_n + (n > mono_n)) * (msz + 10) // max(fw, 1)) + 40 if n else 0) + 22 * 3
    room = fh - used_f
    kf = C.fitted(X, take, fw, min(fh * 0.3, room), 44 if not P else 40, 20, max_lines=3, lh=1.28) if take and room > 48 else None
    facts = (f'<div class="cp-facts" style="left:{fx_}px; top:{fy_}px; width:{fw}px; height:{fh}px">'
             + (f'<div class="cp-year" data-layout-allow-overlap style="font-size:{yr_px:.0f}px">{X.rich(year)}</div>' if year else "")
             + (f'<div class="cp-cites"><span class="cp-cn">0</span><em>次被引用</em></div>' if p.get("cites") else "")
             + (f'<div class="cp-monos">{monos}</div><div class="cp-mlab">{n} 位作者</div>' if n else "")
             + (f'<div class="cp-take" style="font-size:{kf.px}px">{C.lines(X, kf)}</div>' if kf else "")
             + '</div>')
    X.used_text.update(f"{n} 位作者次被引用")
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-paper", """
.cp-sheet { position:absolute; box-sizing:border-box; background:#fbfaf6; color:#111; border-radius:6px; display:flex; flex-direction:column; gap:18px; overflow:hidden;
  box-shadow:0 2px 0 rgba(0,0,0,.05), 0 24px 60px rgba(0,0,0,.26), 0 6px 14px rgba(0,0,0,.1); }
.cp-ghost { position:absolute; background:#e9e3d7; border-radius:6px; transform:rotate(2deg); box-shadow:0 14px 40px rgba(0,0,0,.18); }
.cp-sheet::before { content:''; position:absolute; left:0; right:0; top:0; height:8px; background:var(--accent); }
.cp-chip { align-self:flex-start; font:600 18px var(--f-mono, monospace); letter-spacing:.04em; color:#111; border:2px solid #111; border-radius:5px; padding:4px 12px; }
.cp-title { font-family:var(--f-quote, serif); font-weight:800; line-height:1.14; letter-spacing:-.01em; }
.cp-tl { overflow:hidden; } .cp-tl > * { display:inline-block; }
.cp-auth { font-family:var(--f-body); font-weight:500; color:#444; line-height:1.4; }
.cp-abs { border-top:1.5px solid #ddd6c8; padding-top:16px; display:flex; flex-direction:column; gap:8px; }
.cp-abs b { font:700 16px var(--f-mono, monospace); letter-spacing:.2em; text-transform:uppercase; color:#8a847a; }
.cp-abs > div { font-family:var(--f-quote, serif); font-weight:500; line-height:1.45; color:#2a2826; }
.cp-fig { position:relative; flex:none; border-radius:4px; overflow:hidden; background:#eee9df; }
.cp-fig .cp-fimg { position:absolute; inset:0; width:100%; height:100%; object-fit:contain; }
.cp-facts { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:22px; color:var(--fg); }
.cp-year { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.85; letter-spacing:-.03em; color:color-mix(in srgb, var(--fg) 7%, transparent); -webkit-text-stroke:3px var(--fg); }
.cp-cites { display:flex; align-items:baseline; gap:12px; } .cp-cites .cp-cn { font:900 64px var(--f-num, var(--f-display)); color:var(--accent); }
.cp-cites em { font-style:normal; font:700 24px var(--f-body); color:var(--muted); }
.cp-monos { display:flex; flex-wrap:wrap; gap:10px; } .cp-m { flex:none; } .cp-m .ct-mono { box-shadow:0 0 0 3px var(--bg); }
.cp-more { display:grid; place-items:center; border-radius:50%; background:var(--fg); color:var(--bg); font:800 22px var(--f-body); }
.cp-mlab { font:600 18px var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; }
.cp-take { font-family:var(--f-body); font-weight:800; line-height:1.28; border-left:6px solid var(--accent); padding-left:20px; }
#root.v .cp-facts { justify-content:flex-start; gap:16px; } #root.v .cp-year { -webkit-text-stroke:2.5px var(--fg); }
""")
    _clip(X, cid, t, d, f'<div class="ct-root"><div class="cp-cam">{sheet}{facts}</div></div>', p)
    X.css("fx-cite-paper-cam", ".cp-cam { position:absolute; inset:0; }")
    S = f"#{cid}"
    X.tw(f'tl.fromTo("{S} .cp-sheet", {{y:{sh * 0.35:.0f}, rotation:{-3 if not P else -2}, opacity:0}}, {{y:0, rotation:0, opacity:1, duration:0.8, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "paper")
    X.tw(f'tl.fromTo("{S} .cp-ghost", {{y:{sh * 0.4:.0f}, opacity:0}}, {{y:0, opacity:1, duration:0.9, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{S} .cp-chip", {{opacity:0, x:-20, duration:0.4}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{S} .cp-tl > *", {{yPercent:110, duration:0.7, ease:"expo.out", stagger:0.08}}, {t + 0.4:.3f});')
    X.tw(f'tl.from("{S} .cp-auth", {{opacity:0, y:12, duration:0.5}}, {t + 0.65:.3f});')
    X.tw(f'tl.from("{S} .cp-abs b, {S} .cp-al", {{opacity:0, y:14, duration:0.45, ease:"power3.out", stagger:0.06}}, {t + 0.8:.3f});')
    if fig: X.tw(f'tl.from("{S} .cp-fig", {{opacity:0, scale:0.96, duration:0.6, ease:"power3.out"}}, {t + 1.0:.3f});')
    X.tw(f'tl.from("{S} .cp-year", {{opacity:0, x:40, duration:0.6, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("{S} .cp-m", {{scale:0, duration:0.35, ease:"back.out(2.4)", stagger:0.05}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("{S} .cp-mlab, {S} .cp-take", {{opacity:0, y:16, duration:0.5, ease:"power3.out", stagger:0.12}}, {t + 1.0:.3f});')
    X.sfx(t + 0.6, "pop")
    if p.get("cites"):
        X.tw(f'tl.from("{S} .cp-cites", {{opacity:0, y:16, duration:0.4}}, {t + 0.5:.3f});')
        C.counter(X, f"{S} .cp-cn", t + 0.5, 0, float(p["cites"]), dur=1.3)
    C.marker(X, f"{S} .cp-abs", t + 1.35, each=0.4)
    X.sfx(t + 1.35, "click")
    C.drift(X, f"{S} .cp-cam", t + 0.9, d - 0.9, s=1.025)


FX = {"cite_paper": cite_paper}
