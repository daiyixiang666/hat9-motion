"""引用新闻 / 文章 (article card — "据某某报道" in 口播): either a clean article page built from fields — outlet name
(plain text, never a logo), section, headline, dek, byline and date, an excerpt swept by a marker — or a real
screenshot in a browser window that scrolls to the passage and boxes it; beside it 1–4 key points tick in.

p: outlet · section · headline · dek · byline · date · excerpt · hl (phrase to mark) · url (shown in the bar) ·
   image (screenshot; switches to screenshot mode) · focus (y% to scroll to) · box ([x, y, w, h] % of the image) ·
   points (list of 0–4 short lines) · kicker
Adapts: headlines from 4 words to 3 lines, any outlet/byline length, excerpt from a phrase to a paragraph, screenshots
of any height (tall pages scroll), 0–4 points (none → the page takes the full width); 16:9 = page left + points right,
9:16 = page on top + points below.
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


def cite_article(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    pts = [str(x) for x in fit.as_list(p.get("points"))][:4]
    if P:
        ax, ay, aw = x0, y0, x1 - x0
        ah = round((y1 - y0) * (0.66 if pts else 1.0))
        px_, py_, pw_, ph_ = x0, ay + ah + 26, x1 - x0, y1 - (ay + ah + 26)
    else:
        aw = round((x1 - x0) * (0.6 if pts else 0.86)); ax = x0 if pts else x0 + ((x1 - x0) - aw) // 2
        ay, ah = y0, y1 - y0
        px_, py_, pw_, ph_ = x0 + aw + 56, y0, x1 - (x0 + aw + 56), y1 - y0
    shot = p.get("image")
    url = str(p.get("url", ""))
    bar = 52
    X.used_text.update(url + "↻←→")
    head = f'<div class="ca-bar"><i></i><i></i><i></i><span>{X.rich(url)}</span></div>'
    if shot:
        src = X.asset(shot)
        ar = fit.aspect(X, shot)
        iw = aw; ih = iw / ar
        vh = ah - bar
        fy = float(p.get("focus", 30)) / 100
        scroll = max(0.0, min(ih - vh, ih * fy - vh * 0.4))
        bx = p.get("box")
        boxh = (f'<i class="ca-box" style="left:{bx[0]}%; top:{bx[1]}%; width:{bx[2]}%; height:{bx[3]}%"></i>' if bx else "")
        body = (f'<div class="ca-shotv" style="height:{vh}px"><div class="ca-shot" style="width:{iw}px; height:{ih:.0f}px">'
                f'<img src="{src}" alt="" style="width:100%; height:100%">{boxh}</div></div>')
    else:
        pad = 40 if not P else 34
        iw = aw - 2 * pad
        hf = C.fitted(X, p.get("headline", ""), iw, ah * 0.3, 56 if not P else 50, 26, max_lines=3, lh=1.14)
        df = C.fitted(X, p.get("dek", ""), iw, ah * 0.14, 28, 18, max_lines=2, lh=1.35) if p.get("dek") else None
        ex = str(p.get("excerpt", ""))
        if p.get("hl") and p["hl"] in ex and "*" not in ex: ex = ex.replace(p["hl"], f"*{p['hl']}*", 1)
        used = bar + pad * 2 + 70 + hf.n * hf.px * 1.14 + (df.n * df.px * 1.35 if df else 0) + 60
        ef = C.fitted(X, f"“{ex}”" if ex else "", iw, max(90, ah - used), 34 if not P else 32, 18, max_lines=5, lh=1.45) if ex else None
        need = used - 60 + 40 + (ef.n * ef.px * 1.45 + 30 if ef else 0)
        full = ah
        ah = round(min(full, max(need, full * (0.52 if not P else 0.44))))
        if not P: ay = y0 + (full - ah) // 2
        else: py_, ph_ = ay + ah + 26, y1 - (ay + ah + 26)
        meta = " · ".join(x for x in (str(p.get("byline", "")), str(p.get("date", ""))) if x)
        X.used_text.update(str(p.get("outlet", "")) + str(p.get("section", "")) + meta)
        body = (f'<div class="ca-page" style="padding:{pad}px {pad}px 0">'
                f'<div class="ca-top"><b>{X.rich(p.get("outlet", ""))}</b><span>{X.rich(p.get("section", ""))}</span></div>'
                f'<div class="ca-h" style="font-size:{hf.px}px">{C.lines(X, hf, "ca-hl")}</div>'
                + (f'<div class="ca-dek" style="font-size:{df.px}px">{C.lines(X, df)}</div>' if df else "")
                + (f'<div class="ca-meta">{X.rich(meta)}</div>' if meta else "")
                + (f'<div class="ca-ex" style="font-size:{ef.px}px">{C.lines(X, ef, "ca-el")}</div>' if ef else "")
                + '</div>')
    page = f'<div class="ca-win" style="left:{ax}px; top:{ay}px; width:{aw}px; height:{ah}px">{head}{body}</div>'
    # key points
    side = ""
    if pts:
        kick = p.get("kicker", "报道要点")
        X.used_text.update(kick + "0123456789")
        per = (ph_ - 70) / max(len(pts), 1)
        items = []
        for i, s in enumerate(pts):
            f = C.fitted(X, s, pw_ - 70, per * 0.78, 40 if not P else 38, 20, max_lines=2, lh=1.25)
            items.append(f'<div class="ca-pt"><em>{i + 1:02d}</em><div style="font-size:{f.px}px">{C.lines(X, f)}</div></div>')
        side = (f'<div class="ca-side" style="left:{px_}px; top:{py_}px; width:{pw_}px; height:{ph_}px">'
                f'<div class="ct-kick ca-kick">{X.rich(kick)}</div>{"".join(items)}</div>')
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-article", """
.ca-win { position:absolute; background:#fbfaf6; color:#111; border-radius:12px; overflow:hidden; box-shadow:0 24px 60px rgba(0,0,0,.26), 0 0 0 1.5px rgba(0,0,0,.08); }
.ca-bar { height:52px; display:flex; align-items:center; gap:10px; padding:0 18px; background:#e9e4d9; border-bottom:1.5px solid #d6cfc2; }
.ca-bar i { width:13px; height:13px; border-radius:50%; background:#c9c2b4; } .ca-bar i:first-child { background:#e2321f; }
.ca-bar span { margin-left:14px; flex:1; height:32px; line-height:32px; border-radius:16px; background:#fbfaf6; padding:0 16px; font:500 17px var(--f-mono, monospace); color:#555; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.ca-page { display:flex; flex-direction:column; gap:16px; }
.ca-top { display:flex; align-items:baseline; gap:16px; border-bottom:3px solid #111; padding-bottom:12px; }
.ca-top b { font:900 34px var(--f-quote, serif); letter-spacing:.06em; text-transform:uppercase; }
.ca-top span { font:700 16px var(--f-mono, monospace); letter-spacing:.18em; text-transform:uppercase; color:#e2321f; }
.ca-h { font-family:var(--f-quote, serif); font-weight:800; line-height:1.14; letter-spacing:-.01em; }
.ca-hl { overflow:hidden; }
.ca-dek { font-family:var(--f-body); font-weight:500; color:#444; line-height:1.35; }
.ca-meta { font:600 17px var(--f-mono, monospace); color:#77716a; letter-spacing:.03em; }
.ca-ex { font-family:var(--f-quote, serif); font-weight:500; line-height:1.45; color:#2a2826; border-left:5px solid #111; padding-left:20px; margin-top:6px; }
.ca-shotv { position:relative; overflow:hidden; } .ca-shot { position:absolute; left:0; top:0; }
.ca-shot img { display:block; }
.ca-box { position:absolute; border:4px solid #e2321f; border-radius:8px; box-shadow:0 0 0 9999px rgba(17,17,17,.35); opacity:0; }
.ca-side { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:22px; color:var(--fg); }
.ca-kick { margin-bottom:6px; }
.ca-pt { display:flex; gap:18px; align-items:baseline; border-top:2px solid color-mix(in srgb, var(--fg) 18%, transparent); padding-top:16px; }
.ca-pt em { font-style:normal; font:800 22px var(--f-mono, monospace); color:var(--accent); flex:none; }
.ca-pt > div { font-family:var(--f-body); font-weight:800; line-height:1.25; }
#root.v .ca-side { justify-content:flex-start; gap:14px; }
""")
    _clip(X, cid, t, d, f'<div class="ct-root"><div class="ca-cam">{page}{side}</div></div>', p)
    X.css("fx-cite-article-cam", ".ca-cam { position:absolute; inset:0; }")
    S = f"#{cid}"
    X.tw(f'tl.fromTo("{S} .ca-win", {{y:{ah * 0.3:.0f}, opacity:0, scale:0.97}}, {{y:0, opacity:1, scale:1, duration:0.75, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    if shot:
        X.tw(f'tl.to("{S} .ca-shot", {{y:{-scroll:.0f}, duration:1.4, ease:"power3.inOut"}}, {t + 0.6:.3f});')
        X.tw(f'tl.fromTo("{S} .ca-box", {{opacity:0, scale:1.15}}, {{opacity:1, scale:1, duration:0.35, ease:"back.out(2)"}}, {t + 2.0:.3f});')
        X.sfx(t + 2.0, "hit")
    else:
        X.tw(f'tl.from("{S} .ca-top", {{opacity:0, y:-10, duration:0.4}}, {t + 0.3:.3f});')
        X.tw(f'tl.from("{S} .ca-hl > *", {{yPercent:110, duration:0.7, ease:"expo.out", stagger:0.08}}, {t + 0.4:.3f});')
        X.tw(f'tl.from("{S} .ca-dek, {S} .ca-meta", {{opacity:0, y:12, duration:0.45, stagger:0.1}}, {t + 0.7:.3f});')
        X.tw(f'tl.from("{S} .ca-el", {{opacity:0, y:12, duration:0.45, ease:"power3.out", stagger:0.07}}, {t + 0.95:.3f});')
        C.marker(X, f"{S} .ca-ex", t + 1.4, each=0.4)
        X.sfx(t + 1.4, "click")
    if pts:
        X.tw(f'tl.from("{S} .ca-kick", {{opacity:0, x:30, duration:0.45, ease:"expo.out"}}, {t + 0.4:.3f});')
        X.tw(f'tl.from("{S} .ca-pt", {{opacity:0, x:40, duration:0.5, ease:"expo.out", stagger:0.22}}, {t + 0.9:.3f});')
        for i in range(len(pts)): X.sfx(t + 0.9 + i * 0.22, "click")
    C.drift(X, f"{S} .ca-cam", t + 0.8, d - 0.8, s=1.025)


FX = {"cite_article": cite_article}
