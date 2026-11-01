"""引用 PDF 原文 (document zoom + highlighter — the 口播 staple for court rulings, filings, reports, papers):
the real page is rendered at build time (PyMuPDF), it slides into a document viewer on a paper shadow, the camera
dives into the quoted passage found on the page, everything else washes out and a marker sweeps it line by line;
beside it a card carries the quote, an optional translation and the full citation.

p: pdf · page (1-based; omitted → the first page that contains `quote`) · page_label (e.g. "p. 8 / 286" for an extract) · quote (text to find and highlight) ·
   hl (text to highlight if it differs from quote) · box ([x, y, w, h] % or a list — for scanned pages without text) · zh (translation) · cite (str | {title, meta, page}) · file (shown name) · dpi
Adapts: any page size / orientation; quotes from a few words to a paragraph over 1–8 lines (zoom depth follows the
passage size); missing quote → the page still lands, the card shows the text; 16:9 = viewer left + card right,
9:16 = viewer on top + card below. Needs `pip install pymupdf`.
"""
import hashlib, importlib.util, pathlib, re, sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = _load("_cite")


def _render(X, p):
    """-> (url, img_w, img_h, page_w_pt, page_h_pt, [rects in page fractions], page_no, page_count)"""
    try:
        import fitz
    except ImportError:
        raise SystemExit("cite_pdf needs PyMuPDF: pip install pymupdf")
    src = pathlib.Path(p["pdf"]); src = src if src.is_absolute() else X.src / src
    if not src.exists(): raise SystemExit(f"cite_pdf: missing pdf {src}")
    doc = fitz.open(str(src))
    want = re.sub(r"\s+", " ", str(p.get("hl") or p.get("quote") or "")).strip()
    idx = int(p["page"]) - 1 if p.get("page") else None
    rects = []
    if idx is None and want:
        for probe in (want, want[:60], want[:30]):
            idx = next((i for i in range(doc.page_count) if doc[i].search_for(probe)), None)
            if idx is not None: break
    idx = 0 if idx is None else max(0, min(idx, doc.page_count - 1))
    page = doc[idx]
    if want:
        for probe in (want, want[:60], want[:30]):
            rects = page.search_for(probe)
            if rects: break
    pw, ph = page.rect.width, page.rect.height
    dpi = int(p.get("dpi", 180))
    key = hashlib.sha1(f"{src}|{idx}|{dpi}|{src.stat().st_mtime}".encode()).hexdigest()[:10]
    out = X.out / "assets" / "img" / f"pdf_{key}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        page.get_pixmap(dpi=dpi, alpha=False).save(str(out))
    from PIL import Image
    with Image.open(out) as im: iw, ih = im.size
    fr = [((r.x0 - 2) / pw, (r.y0 - 1.5) / ph, (r.x1 + 2) / pw, (r.y1 + 1.5) / ph) for r in rects]
    if not fr and p.get("box"):            # scanned PDFs have no text layer: mark the passage by hand, [x, y, w, h] % (or a list of them)
        bxs = p["box"] if isinstance(p["box"][0], (list, tuple)) else [p["box"]]
        fr = [(b[0] / 100, b[1] / 100, (b[0] + b[2]) / 100, (b[1] + b[3]) / 100) for b in bxs]
    return f"assets/img/{out.name}", iw, ih, pw, ph, fr, idx + 1, doc.page_count


def cite_pdf(X, cid, t, d, p):
    url, iw, ih, pw_pt, ph_pt, rects, pno, pcount = _render(X, p)
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    # viewer + card boxes
    if P:
        vx, vy, vw, vh = x0, y0, x1 - x0, round((y1 - y0) * 0.6)
        cx, cy, cw, ch = x0, vy + vh + 28, x1 - x0, y1 - (vy + vh + 28)
    else:
        vw = round((x1 - x0) * 0.47)
        vx, vy, vh = x0, y0, y1 - y0
        cx, cy, cw, ch = x0 + vw + 64, y0 + 10, x1 - (x0 + vw + 64), y1 - y0 - 10
    bar = 46
    ar = pw_pt / ph_pt
    sh = vh - bar - 64; sw = sh * ar
    if sw > vw - 64: sw = vw - 64; sh = sw / ar
    sx, sy = (vw - sw) / 2, bar + (vh - bar - sh) / 2
    # zoom: centre the passage in the viewer, sized to ~84% of its width
    if rects:
        ux0 = min(r[0] for r in rects); uy0 = min(r[1] for r in rects); ux1 = max(r[2] for r in rects); uy1 = max(r[3] for r in rects)
    else:
        ux0, uy0, ux1, uy1 = 0.1, 0.1, 0.9, 0.3
    pcx, pcy = sx + (ux0 + ux1) / 2 * sw, sy + (uy0 + uy1) / 2 * sh
    s = max(1.15, min(2.8, (vw * 0.84) / max((ux1 - ux0) * sw, 1), (vh - bar) * 0.55 / max((uy1 - uy0) * sh, 1)))
    fx, fy = vw / 2, bar + (vh - bar) * 0.46
    clamp = lambda v, lo, hi: min(max(v, lo), hi)
    cam = lambda k: (clamp(fx - k * pcx, vw - k * (sx + sw) - 24, -k * sx + 24), clamp(fy - k * pcy, vh - k * (sy + sh), bar - k * sy))   # no empty viewer showing
    tx, ty = cam(s)
    img = f'<img class="ct-pg" src="{url}" alt="" style="width:{sw:.1f}px; height:{sh:.1f}px">'
    hls = "".join(
        f'<div class="ct-hl" style="left:{r[0] * sw:.1f}px; top:{r[1] * sh:.1f}px; width:{(r[2] - r[0]) * sw:.1f}px; height:{(r[3] - r[1]) * sh:.1f}px">'
        f'<img src="{url}" alt="" style="left:{-r[0] * sw:.1f}px; top:{-r[1] * sh:.1f}px; width:{sw:.1f}px; height:{sh:.1f}px"><i class="ct-mk"></i></div>' for r in rects)
    fname = p.get("file") or pathlib.Path(str(p["pdf"])).name
    plabel = p.get("page_label") or f"p. {pno} / {pcount}"
    X.used_text.update("PDF" + plabel + fname)
    viewer = (f'<div class="ct-view" style="left:{vx}px; top:{vy}px; width:{vw}px; height:{vh}px">'
              f'<div class="ct-vbar"><b>PDF</b><span>{X.rich(fname)}</span><em>{X.rich(plabel)}</em></div>'
              f'<div class="ct-zoom"><div class="ct-sheet" style="left:{sx:.1f}px; top:{sy:.1f}px; width:{sw:.1f}px; height:{sh:.1f}px">{img}<i class="ct-veil"></i>{hls}</div></div></div>')
    # the card: quote (original) · translation · citation
    cite = p.get("cite") or {}
    if isinstance(cite, str): cite = {"title": cite}
    q = str(p.get("quote", ""))
    qf = C.fitted(X, f"“{q}”" if q else "", cw, ch * (0.42 if p.get("zh") else 0.6), 64 if not P else 54, 26, max_lines=5, lh=1.22)
    zf = C.fitted(X, p["zh"], cw, ch * 0.24, 46 if not P else 44, 24, max_lines=3, lh=1.28) if p.get("zh") else None
    tf = C.fitted(X, cite.get("title", ""), cw, 64, 34, 20, max_lines=2, lh=1.2) if cite.get("title") else None
    kick = p.get("kicker", "原文 · PDF")
    X.used_text.update(kick)
    card = (f'<div class="ct-card" style="left:{cx}px; top:{cy}px; width:{cw}px; height:{ch}px">'
            f'<div class="ct-kick">{X.rich(kick)}</div>'
            + (f'<div class="ct-q" style="font-size:{qf.px}px">{C.lines(X, qf)}</div>' if q else "")
            + (f'<div class="ct-zh" style="font-size:{zf.px}px">{C.lines(X, zf)}</div>' if zf else "")
            + '<i class="ct-rule"></i>'
            + (f'<div class="ct-ttl" style="font-size:{tf.px}px">{C.lines(X, tf)}</div>' if tf else "")
            + (f'<div class="ct-meta">{X.rich(cite["meta"])}</div>' if cite.get("meta") else "")
            + (f'<div class="ct-meta">{X.rich(cite["page"])}</div>' if cite.get("page") else "")
            + '</div>')
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-pdf", """
.ct-view { position:absolute; overflow:hidden; border-radius:14px; background:color-mix(in srgb, var(--fg) 7%, var(--bg)); box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fg) 14%, transparent); }
.ct-vbar { position:absolute; left:0; right:0; top:0; height:46px; display:flex; align-items:center; gap:14px; padding:0 18px; z-index:3;
  font-family:var(--f-mono, monospace); font-size:17px; color:var(--muted); background:color-mix(in srgb, var(--fg) 10%, var(--bg)); }
.ct-vbar b { background:#e2321f; color:#fff; font-weight:800; padding:2px 8px; border-radius:4px; font-size:14px; letter-spacing:.06em; }
.ct-vbar span { color:var(--fg); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; } .ct-vbar em { margin-left:auto; font-style:normal; }
.ct-zoom { position:absolute; inset:0; transform-origin:0 0; }
.ct-sheet { position:absolute; background:#fbfaf6; box-shadow:0 2px 0 rgba(0,0,0,.06), 0 18px 50px rgba(0,0,0,.28), 0 4px 12px rgba(0,0,0,.12); }
.ct-sheet .ct-pg { position:absolute; left:0; top:0; display:block; }
.ct-veil { position:absolute; inset:0; background:rgba(251,250,246,.78); opacity:0; }
.ct-hl { position:absolute; overflow:hidden; }
.ct-hl img { position:absolute; max-width:none; }
.ct-mk { position:absolute; inset:0; background:#f6ce3a; mix-blend-mode:multiply; transform-origin:0 50%; }
.ct-card { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:22px; color:var(--fg); }
.ct-card .ct-q { font-family:var(--f-quote, var(--f-display)); font-weight:700; line-height:1.22; letter-spacing:-.005em; }
.ct-card .ct-zh { font-family:var(--f-body); font-weight:800; line-height:1.28; }
.ct-rule { display:block; height:3px; width:120px; background:var(--accent); transform-origin:0 50%; }
.ct-card .ct-ttl { font-family:var(--f-quote, var(--f-display)); font-weight:700; font-style:italic; line-height:1.2; }
.ct-card .ct-meta { font-family:var(--f-mono, monospace); font-size:19px; color:var(--muted); line-height:1.4; }
""")
    X.css("fx-cite-pdf-v", "#root.v .ct-card { gap:16px; justify-content:flex-start; } #root.v .ct-card .ct-meta { font-size:20px; }")
    _clip(X, cid, t, d, f'<div class="ct-root">{viewer}{card}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .ct-view", {{opacity:0, scale:0.96, duration:0.5, ease:"power3.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{S} .ct-sheet", {{y:{vh * 0.5:.0f}, rotation:-7, opacity:0}}, {{y:0, rotation:-2.5, opacity:1, duration:0.8, ease:"expo.out"}}, {t + 0.08:.3f});')
    X.tw(f'tl.from("{S} .ct-card > *", {{x:44, opacity:0, duration:0.55, ease:"expo.out", stagger:0.07}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{S} .ct-rule", {{scaleX:0, duration:0.5, ease:"power3.out"}}, {t + 0.5:.3f});')
    X.sfx(t + 0.08, "paper")
    tz = t + min(0.95, d * 0.25)
    X.tw(f'tl.to("{S} .ct-zoom", {{scale:{s:.3f}, x:{tx:.1f}, y:{ty:.1f}, duration:1.0, ease:"power3.inOut"}}, {tz:.3f});')
    X.tw(f'tl.to("{S} .ct-sheet", {{rotation:0, duration:1.0, ease:"power3.inOut"}}, {tz:.3f});')
    X.sfx(tz, "whoosh_soft")
    X.tw(f'tl.to("{S} .ct-veil", {{opacity:1, duration:0.45, ease:"power2.out"}}, {tz + 0.55:.3f});')
    each = max(0.18, min(0.42, 1.2 / max(len(rects), 1)))
    X.tw(f'tl.fromTo("{S} .ct-mk", {{scaleX:0}}, {{scaleX:1, duration:{each:.2f}, ease:"power2.inOut", stagger:{each * 0.9:.2f}}}, {tz + 0.75:.3f});')
    X.sfx(tz + 0.75, "click")
    if p.get("zh") and "*" in str(p["zh"]): C.marker(X, f"{S} .ct-zh", tz + 1.0)
    hold = tz + 1.05
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .ct-zoom", {{scale:{s * 1.035:.3f}, x:{cam(s * 1.035)[0]:.1f}, y:{cam(s * 1.035)[1]:.1f}, duration:{t + d - hold:.2f}, ease:"none"}}, {hold:.3f});')


FX = {"cite_pdf": cite_pdf}
