"""shared helpers for the genre / narrative effects (review_card, news_flash, deal_card, next_teaser, opener,
sponsor_card, share_card, poll_card, clip_style). Not an effect.

area(): the usable box, clear of header / caption and — in 9:16 — of the right-hand button column (lower half).
counter(): a number that rolls on the timeline (deterministic: GSAP onUpdate on a proxy). stars(): an outlined +
filled 5-star row whose fill is a clip width. ticks(): a seeded set of positions. note_tag(): the 「示意」 badge.
"""
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

STAR = "M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7L12 17.3 5.8 20.9l1.6-7L2 9.2l7.1-.6z"

CSS = """
.fx .gn-note { position:absolute; font-family:var(--f-mono, monospace); font-weight:600; letter-spacing:.06em; color:var(--bg);
  background:var(--muted); border-radius:.4em; padding:.12em .55em; white-space:nowrap; }
.fx .gn-stars { position:absolute; white-space:nowrap; line-height:0; }
.fx .gn-stars svg { display:inline-block; }
.fx .gn-stars .on { position:absolute; left:0; top:0; overflow:hidden; white-space:nowrap; }
"""


def vm(X, v): return S.vm(X, v)


def area(X, p):
    """(x, y, w, h): S.box, narrowed in 9:16 so nothing reaches the right 120 px button column."""
    x, y, w, h = S.box(X, p)
    if X.portrait:
        x = max(x, 60); w = min(w, X.W - 124 - x)
    return x, y, w, h


def num(v):
    try: return float(str(v).replace(",", "").replace("¥", "").replace("$", ""))
    except (TypeError, ValueError): return None


def dec_of(v):
    s = str(v)
    return len(s.split(".")[1]) if "." in s and s.split(".")[1].isdigit() else 0


def counter(X, sel, t, a, b, dur=1.0, dec=0, sep=True, ease="power3.out"):
    fmt = (f"o.v.toLocaleString('en-US',{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}})" if sep
           else f"o.v.toFixed({dec})")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); if(!el) return; '
         f'tl.to(o, {{v:{b}, duration:{dur:.2f}, ease:"{ease}", onUpdate:()=>{{el.textContent={fmt};}}}}, {t:.3f});}})();')


def stars(X, px, cls="gn-stars", style=""):
    """5 stars px tall; the .on layer's width (0–100%) is the fill."""
    one = lambda fill, stroke: (f'<svg width="{px:.0f}" height="{px:.0f}" viewBox="0 0 24 24" style="margin-right:{px * 0.12:.0f}px">'
                                f'<path d="{STAR}" fill="{fill}" stroke="{stroke}" stroke-width="1.4" stroke-linejoin="round"/></svg>')
    off = "".join(one("none", "var(--muted)") for _ in range(5))
    on = "".join(one("var(--accent)", "var(--accent)") for _ in range(5))
    return f'<div class="{cls}" style="{style}">{off}<div class="on" style="width:0%">{on}</div></div>'


def stars_w(px): return px * 5 + px * 0.12 * 5


def paint_bg(X, cid, t, d, p):
    """the beat's theme ground as its own clip under a root-sibling video (fit.media), whose effect clip must stay
    unpainted (transparent=True) so the footage shows through it."""
    from h9 import aefx
    sty = aefx._theme_style(p, paint=True) or "background:var(--bg)"
    X.clip(f"{cid}bg", t, d, "", "fx-ground", 1, track=19, sty=f"position:absolute; inset:0; {sty}")


def note_tag(X, text, x, y, px, cls="gn-note"):
    if not text: return ""
    return f'<div class="{cls}" data-safe="ignore" style="left:{x:.0f}px; top:{y:.0f}px; font-size:{px:.0f}px">{X.rich(text)}</div>'


def line_html(X, f, cls="gl"):
    return "".join(f'<span class="{cls}"><span>{X.rich(l)}</span></span>' for l in f.lines)


def seeded(X, n, key):
    """n deterministic floats in [0, 1) for this beat."""
    import random
    r = random.Random(f"{key}-{X.v.get('meta', {}).get('seed', 9)}-{n}")
    return [r.random() for _ in range(n)]
