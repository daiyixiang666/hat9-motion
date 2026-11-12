"""shared bits for the image & document effects (files starting with _ are not effects; load by path).

box(): the content box (16:9 under the header / above the caption; 9:16 clear of the platform chrome) ·
colors(): the beat's theme colours as real hex values (for build-time image processing) ·
pdf_pages() / pdf_find(): PyMuPDF page renders, cached in the build · wordmark(): a made-up logo as inline SVG ·
loop_mp4(): GIF → looping mp4 sized to the beat · paper(): the paper sheet CSS.
"""
import hashlib, importlib.util, pathlib, re, subprocess, sys
from h9 import fit
from h9.aefx import THEMES, SAFE_R


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = load("_cite")

CSS = r"""
.d2 { position:absolute; inset:0; }
.d2 .em { white-space:nowrap; }
.d2 .em .emb { left:-.06em; right:-.06em; top:.04em; bottom:-.02em; background:#f6ce3a; border-radius:.08em; }
.d2-sheet { position:absolute; background:#fbfaf6; color:#1b1b1b; box-shadow:0 1px 0 rgba(0,0,0,.05), 0 16px 44px rgba(0,0,0,.26), 0 3px 10px rgba(0,0,0,.12); overflow:hidden; }
.d2-sheet img { position:absolute; left:0; top:0; width:100%; height:100%; display:block; }
.d2-tag { position:absolute; font-family:var(--f-mono, monospace); font-size:17px; letter-spacing:.04em; color:var(--fg); background:color-mix(in srgb, var(--bg) 82%, transparent);
  padding:4px 10px; border-radius:6px; white-space:nowrap; }
.d2-ttl { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.1; letter-spacing:-.01em; }
.d2-kick { position:absolute; font:700 19px var(--f-body); letter-spacing:.14em; color:var(--bg); background:var(--fg); padding:5px 12px; border-radius:6px; white-space:nowrap; }
.d2-mk { position:absolute; background:#f6ce3a; mix-blend-mode:multiply; transform-origin:0 50%; border-radius:3px; }
"""


def box(X, p, text=False):
    """(x0, y0, x1, y1) px. 9:16 keeps the platform chrome clear; `text` also keeps the right 120 px of the lower half."""
    W, H = X.W, X.H
    if X.portrait:
        m = SAFE_R if text else 72
        return m, 252, W - m, (1300 if p.get("line") else 1480)
    return C.area(X, p)


def colors(X, p):
    """{'fg','bg','accent','muted','card'} as hex for the beat (theme override, else the style's tokens)."""
    tok = dict(X.S.get("tokens", {}))
    th = THEMES.get(p.get("theme")) or {}
    out = {k: th.get(k, tok.get(k)) for k in ("fg", "bg", "accent", "muted", "card")}
    out = {k: (v if isinstance(v, str) and v.startswith("#") else None) for k, v in out.items()}
    return {"fg": out["fg"] or "#111111", "bg": out["bg"] or "#f0ece3", "accent": out["accent"] or "#e2321f",
            "muted": out["muted"] or "#625d56", "card": out["card"] or "#fbfaf6"}


def hexrgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def cache(X, key, ext, sub="img"):
    """a cache path inside the build for a derived file, and its project-relative url."""
    k = hashlib.sha1(key.encode()).hexdigest()[:12]
    out = (X.out / "assets" / sub / f"d2_{k}.{ext}").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    return out, f"assets/{sub}/{out.name}"


def _fitz():
    try:
        import fitz
        return fitz
    except ImportError:
        raise SystemExit("this effect reads PDFs with PyMuPDF: pip install pymupdf")


def pdf_path(X, pdf):
    p = fit._abs(X, pdf)
    if not p.exists(): raise SystemExit(f"missing pdf {p}")
    return p


def pdf_count(X, pdf):
    return _fitz().open(str(pdf_path(X, pdf))).page_count


def pdf_pages(X, pdf, pages, dpi=90):
    """[(url, w, h)] for the 1-based page numbers given (clamped), rendered once per build."""
    fz = _fitz(); src = pdf_path(X, pdf)
    doc = fz.open(str(src)); out = []
    for n in pages:
        i = max(0, min(int(n) - 1, doc.page_count - 1))
        f, url = cache(X, f"{src}|{src.stat().st_mtime}|{i}|{dpi}", "jpg")
        if not f.exists():
            pix = doc[i].get_pixmap(dpi=dpi, alpha=False)
            pix.save(str(f.with_suffix(".png")))
            from PIL import Image
            with Image.open(f.with_suffix(".png")) as im: im.convert("RGB").save(f, quality=86)
            f.with_suffix(".png").unlink()
        r = doc[i].rect
        out.append((url, r.width, r.height))
    return out


def pdf_find(X, pdf, quote, page=None):
    """(1-based page, [rects as page fractions]) of a quote; page given → search only there."""
    fz = _fitz(); doc = fz.open(str(pdf_path(X, pdf)))
    want = re.sub(r"\s+", " ", str(quote or "")).strip()
    order = [int(page) - 1] if page else range(doc.page_count)
    for probe in ([want, want[:60], want[:30]] if want else []):
        for i in order:
            if not 0 <= i < doc.page_count: continue
            rs = doc[i].search_for(probe)
            if rs:
                pw, ph = doc[i].rect.width, doc[i].rect.height
                return i + 1, [((r.x0 - 2) / pw, (r.y0 - 1.5) / ph, (r.x1 + 2) / pw, (r.y1 + 1.5) / ph) for r in rs]
    return (int(page) if page else 1), []


def page_list(X, p, default_n=12):
    """pages as [(url, w, h)] from p['pages'] (images) or p['pdf'] (+ p['range'] like [1, 24] or 'all')."""
    if p.get("pdf"):
        n = pdf_count(X, p["pdf"])
        rg = p.get("range")
        if rg == "all": nums = list(range(1, n + 1))
        elif isinstance(rg, (list, tuple)) and len(rg) == 2: nums = list(range(int(rg[0]), min(int(rg[1]), n) + 1))
        elif isinstance(rg, (list, tuple)): nums = [int(x) for x in rg]
        else: nums = list(range(1, min(n, default_n) + 1))
        return pdf_pages(X, p["pdf"], nums, dpi=int(p.get("dpi", 90))), nums
    imgs = fit.as_list(p.get("pages") or p.get("images"))
    out = []
    for s in imgs:
        src = s.get("src") if isinstance(s, dict) else s
        sz = fit.size(fit._abs(X, src)) or (1240, 1754)
        out.append((X.asset(src), sz[0], sz[1]))
    return out, list(range(1, len(out) + 1))


MARKS = ["circle", "square", "tri", "bars", "ring", "half", "diamond", "dots"]


def wordmark(name, k=0, accent="currentColor"):
    """a made-up logo (geometric mark + name) as inline SVG, deterministic per name; colours follow currentColor."""
    s = str(name)
    h = sum((i + 1) * ord(c) for i, c in enumerate(s)) + k * 7
    kind = MARKS[h % len(MARKS)]
    m = {
        "circle": '<circle cx="20" cy="20" r="15" fill="currentColor"/><circle cx="26" cy="14" r="5" fill="{a}"/>',
        "square": '<rect x="6" y="6" width="28" height="28" rx="6" fill="currentColor"/><rect x="14" y="14" width="12" height="12" rx="2" fill="{a}"/>',
        "tri": '<path d="M20 5 L36 34 H4 Z" fill="currentColor"/><circle cx="20" cy="24" r="4.5" fill="{a}"/>',
        "bars": '<rect x="5" y="20" width="7" height="15" fill="currentColor"/><rect x="16" y="12" width="7" height="23" fill="currentColor"/><rect x="27" y="5" width="7" height="30" fill="{a}"/>',
        "ring": '<circle cx="20" cy="20" r="13" fill="none" stroke="currentColor" stroke-width="6"/><circle cx="20" cy="20" r="4" fill="{a}"/>',
        "half": '<path d="M20 5 A15 15 0 0 1 20 35 Z" fill="currentColor"/><path d="M20 5 A15 15 0 0 0 20 35 Z" fill="{a}"/>',
        "diamond": '<path d="M20 4 L36 20 L20 36 L4 20 Z" fill="currentColor"/><path d="M20 13 L27 20 L20 27 L13 20 Z" fill="{a}"/>',
        "dots": '<circle cx="11" cy="11" r="6" fill="currentColor"/><circle cx="29" cy="11" r="6" fill="{a}"/><circle cx="11" cy="29" r="6" fill="{a}"/><circle cx="29" cy="29" r="6" fill="currentColor"/>',
    }[kind].replace('fill="{a}"', 'class="acc"')
    tw = max(1.0, fit.width(s)) * 24
    w = 50 + tw
    return (f'<svg viewBox="0 0 {w:.0f} 40" xmlns="http://www.w3.org/2000/svg" style="overflow:visible">{m}'
            f'<text x="48" y="28.5" font-size="24" font-weight="900" fill="currentColor" style="font-family:var(--f-display)">{_esc(s)}</text></svg>'), w / 40


def _esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def loop_mp4(X, src, d, bg="#ffffff", speed=1.0, max_w=960):
    """a GIF (or animated WebP) → an H.264 mp4 that loops to cover d seconds, transparency flattened onto bg.
    -> (path, w, h, native_duration)."""
    a = fit._abs(X, src)
    if not a.exists(): raise SystemExit(f"missing gif {a}")
    from PIL import Image
    with Image.open(a) as im:
        w, h = im.size
        n = getattr(im, "n_frames", 1); total = 0
        for i in range(n):
            im.seek(i); total += im.info.get("duration", 100) or 100
    native = max(0.1, total / 1000)
    k = min(1.0, max_w / w); ow, oh = int(w * k) // 2 * 2, int(h * k) // 2 * 2
    out, _ = cache(X, f"{a}|{a.stat().st_mtime}|{d:.2f}|{bg}|{speed}|{ow}", "mp4", "video")
    if not out.exists():
        r = hexrgb(bg)
        fc = (f"color=c=0x{r[0]:02x}{r[1]:02x}{r[2]:02x}:s={ow}x{oh}:r=30[bgc];"
              f"[0:v]setpts=PTS/{speed},scale={ow}:{oh}:flags=lanczos,format=rgba[g];[bgc][g]overlay=shortest=1,format=yuv420p[o]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ignore_loop", "0", "-i", str(a), "-filter_complex", fc, "-map", "[o]",
                        "-t", f"{d + 0.5:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-movflags", "+faststart", str(out)], check=True)
    return out, ow, oh, native / speed


def drift(X, sel, t, d, s=1.03, y=0):
    X.tw(f'tl.fromTo("{sel}", {{scale:1, y:0}}, {{scale:{s}, y:{y}, duration:{max(d, 0.1):.2f}, ease:"none"}}, {t:.3f});')


def times(X, p, t, d, n, key="at", lead=0.25, tail=0.6, texts=None):
    """n switch times inside the beat: from p[key] (list of "@词" / seconds) where given, else when the narration
    says texts[i] inside the beat, else evenly spaced."""
    given = fit.as_list(p.get(key))
    span = max(0.3, d - lead - tail)
    out = []
    fixed = []
    for i in range(n):
        tt = None
        if i < len(given):
            try: tt = X.T(given[i], t)
            except SystemExit: tt = None
            if tt is not None and not (t <= tt < t + d): tt = None
        out.append(float(tt) if tt is not None else t + lead + span * i / max(1, n))
        fixed.append(tt is not None)
    if texts:
        out = load("_ui").follow(X, texts, t, d, out, fixed, gap=0.18)
    for i in range(1, n): out[i] = max(out[i], out[i - 1] + 0.18)
    return out


def wrap(text, px, box_w, max_lines=12):
    """house-markup text set at a FIXED size, wrapped into as many balanced lines as it needs (fit.fit_text would
    shrink or ellipsize instead). Returns an object with .px, .lines, .n like fit.Fit."""
    import math
    segs, mask = fit._parse(fit.as_text(text))
    flat = [c for sg in segs for c in sg]
    lines = []
    for sg in segs:
        w = fit.width("".join(sg)) * px
        k = max(1, math.ceil(w / (box_w * 0.96)))
        while k < max_lines:
            br = fit._break(sg, k)
            if max(fit.width(l) for l in br) * px <= box_w * 0.97: break
            k += 1
        lines += fit._break(sg, k)
    marked = fit._remark([fit.plain(l) for l in lines], flat, mask) if any(mask) else [fit.plain(l) for l in lines]
    return fit.Fit(int(px), marked, max(fit.width(l) for l in lines) if lines else 0)
