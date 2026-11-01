"""竖排标题 / 竖排古文 Vertical Title (书法字幕、古籍竖排、日式竖版海报；B 站国风 / 纪录片片名的竖排标题):
Chinese set top-to-bottom, columns right-to-left. Title mode: one to three big columns that drop in glyph by glyph
out of an ink blur, a red seal stamps beside them. Classical mode: a page of 竖排古文 — thin column rules, each
column brushed on top-to-bottom in reading order (right first), the source in small vertical type, a seal.
Works for simplified or traditional Chinese (繁體), and for Japanese kana.

Adapts: 1–200 glyphs; "|" forces a column break, long columns wrap to the page height; the size solves for the
column count so it always fits the box; seal 1–4 glyphs (2×2 grid), optional.
p: text · sub (source / author, vertical) · seal · mode ("title" | "classical") · font ("serif" | "display" | "hand")
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__text2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__text2", pathlib.Path(__file__).with_name("_text2.py"))
    sys.modules["h9fx__text2"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__text2"])
T2 = sys.modules["h9fx__text2"]
S = T2.S
from h9 import fit
from h9.core import esc

CSS = """
.fx .vt { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .vt .vt-col { position:absolute; writing-mode:vertical-rl; text-orientation:upright; white-space:nowrap; color:var(--fg); line-height:1; }
.fx .vt .vt-col i { font-style:normal; display:inline-block; }
.fx .vt .vt-rule { position:absolute; width:.18vmin; background:color-mix(in srgb, var(--fg) 22%, transparent); transform-origin:50% 0; }
.fx .vt .vt-frame { position:absolute; border:.3vmin solid color-mix(in srgb, var(--fg) 40%, transparent); }
.fx .vt .vt-sub { position:absolute; writing-mode:vertical-rl; text-orientation:upright; white-space:nowrap; color:var(--muted); font-family:var(--f-body); font-weight:500; letter-spacing:.18em; }
.fx .vt .vt-seal { position:absolute; display:grid; background:#c8302a; color:#fbf3e4; border-radius:.5vmin; box-shadow:inset 0 0 0 .35vmin rgba(255,240,220,.35);
  font-family:var(--f-quote, var(--f-display)); font-weight:900; place-items:center; line-height:1; }
"""
FONT = {"serif": "var(--f-quote, var(--f-display))", "display": "var(--f-display)", "hand": "var(--f-hand, var(--f-display))"}


def _columns(text, per):
    cols = []
    for seg in str(text).split("|"):
        seg = seg.strip()
        while len(seg) > per:
            cut = per
            # never leave a closing mark at the top of the next column
            while cut < len(seg) and seg[cut] in "，。、！？；：」』）,.!?": cut += 1
            cols.append(seg[:cut]); seg = seg[cut:]
        if seg: cols.append(seg)
    return cols or [""]


def vertical_title(X, cid, t, d, p):
    P = X.portrait
    text = fit.plain(fit.as_text(p.get("text") or "竖排"))
    raw = fit.as_text(p.get("text") or "竖排").replace("*", "")
    mode = p.get("mode") or ("classical" if len(text) > 14 else "title")
    sub, seal = fit.as_text(p.get("sub")), fit.plain(fit.as_text(p.get("seal")))[:4]
    font = FONT.get(p.get("font") or ("serif" if mode == "classical" else "display"), FONT["display"])
    x, y, w, h = S.box(X, p)
    gap = 1.9 if mode == "classical" else 1.35         # column pitch in em
    usable_h = h * (0.86 if mode == "classical" else 0.9)
    best = None
    max_px = S.vm(X, 16 if mode == "title" else 8.4)
    px = max_px
    seg_max = max(len(sg.strip()) for sg in raw.split("|"))
    while px >= S.vm(X, 3.2):
        per = max(1, int(usable_h / (px * 1.04)))
        if mode == "title" and per < seg_max:      # a title keeps each "|" column whole: shrink instead of wrapping
            px *= 0.94; continue
        cols = _columns(raw, per)
        extra = (2.2 if sub else 0) + (1.6 if seal else 0)
        need = (len(cols) * gap + extra) * px
        if need <= w * 0.96:
            best = (px, per, cols); break
        px *= 0.94
    if best is None:
        px = S.vm(X, 3.2); per = max(1, int(usable_h / (px * 1.04))); best = (px, per, _columns(raw, per))
    px, per, cols = best
    n = len(cols)
    longest = max(len(c) for c in cols)
    col_h = longest * px * 1.04
    block_w = n * gap * px
    sub_w = px * 1.4 if sub else 0
    seal_px = px * (0.95 if mode == "title" else 1.4)
    total_w = block_w + sub_w + (seal_px * 1.2 if seal else 0)
    x0 = x + (w - total_w) / 2 + total_w        # right edge of the block (columns run right → left)
    y0 = y + (h - col_h) / 2
    X.css("fx-vt", CSS)
    html = []
    if mode == "classical":
        html.append(f'<div class="vt-frame" style="left:{x0 - block_w - px * 0.3:.0f}px; top:{y0 - px * 0.6:.0f}px; width:{block_w + px * 0.3:.0f}px; height:{col_h + px * 1.2:.0f}px"></div>')
    for i, c in enumerate(cols):
        cxr = x0 - (i + 0.5) * gap * px - px / 2
        glyphs = "".join(f"<i>{esc(ch)}</i>" for ch in c)
        html.append(f'<div class="vt-col" data-c="{i}" style="left:{cxr:.0f}px; top:{y0:.0f}px; font-size:{px:.0f}px; font-family:{font}; font-weight:{900 if mode == "title" else 700}">{glyphs}</div>')
        if mode == "classical" and i < n - 1:
            html.append(f'<i class="vt-rule" data-c="{i}" style="left:{x0 - (i + 1) * gap * px:.0f}px; top:{y0 - px * 0.6:.0f}px; height:{col_h + px * 1.2:.0f}px"></i>')
    xl = x0 - block_w
    if sub:
        nsub = max(1, len(fit.plain(sub)))
        spx = min(max(S.vm(X, 2.6), px * 0.36), col_h / (nsub * 1.18))     # the source never runs past the columns
        html.append(f'<div class="vt-sub" style="left:{xl - sub_w * 0.8:.0f}px; top:{y0 + col_h - nsub * spx * 1.18:.0f}px; font-size:{spx:.0f}px">{X.rich(sub)}</div>')
        xl -= sub_w
    if seal:
        g = 2 if len(seal) > 1 else 1
        cells = "".join(f"<span>{esc(ch)}</span>" for ch in (seal[2:4] + seal[0:2] if len(seal) == 4 else seal))
        sz = seal_px * (1.15 if g == 2 else 0.95)
        html.append(f'<div class="vt-seal" style="left:{xl - sz - px * 0.25:.0f}px; top:{y0 + col_h - sz:.0f}px; width:{sz:.0f}px; height:{sz:.0f}px; '
                    f'grid-template-columns:repeat({g}, 1fr); font-size:{sz / g * 0.78:.0f}px; transform:rotate(-4deg)">{cells}</div>')
    _clip(X, cid, t, d, f'<div class="vt">{"".join(html)}</div>', p)
    s = f"#{cid} .vt"
    nglyph = sum(len(c) for c in cols)
    if mode == "classical":
        X.tw(f'tl.from("{s} .vt-frame", {{opacity:0, scale:1.03, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
        X.tw(f'tl.from("{s} .vt-rule", {{scaleY:0, duration:0.5, ease:"expo.out", stagger:0.04}}, {t + 0.1:.3f});')
        span = max(0.6, d * 0.62)
        each = span / max(n, 1)
        for i in range(n):
            X.tw(f'tl.fromTo("{s} .vt-col[data-c=\'{i}\']", {{clipPath:"inset(0 0 100% 0)"}}, {{clipPath:"inset(0 0 0% 0)", duration:{max(0.25, each * 0.95):.2f}, ease:"power1.inOut"}}, {t + 0.3 + i * each:.3f});')
        X.sfx(t + 0.3, "brush")
    else:
        st = min(0.09, d * 0.45 / max(nglyph, 1))
        X.tw(f'tl.from("{s} .vt-col i", {{opacity:0, y:"-0.5em", filter:"blur(16px)", duration:0.55, ease:"expo.out", stagger:{st:.3f}}}, {t + 0.1:.3f});')
        X.sfx(t + 0.1, "enter")
    t_end = t + 0.3 + (d * 0.62 if mode == "classical" else min(0.09, d * 0.45 / max(nglyph, 1)) * nglyph + 0.3)
    if sub: X.tw(f'tl.from("{s} .vt-sub", {{opacity:0, y:-20, duration:0.5, ease:"expo.out"}}, {min(t + d - 0.6, t_end):.3f});')
    if seal:
        ts = min(t + d - 0.5, t_end + 0.2)
        X.tw(f'tl.from("{s} .vt-seal", {{scale:1.8, opacity:0, rotation:-18, duration:0.32, ease:"power4.out"}}, {ts:.3f});')
        X.sfx(ts + 0.12, "hit")


FX = {"vertical_title": vertical_title}
