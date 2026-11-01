"""shared bits for the citation effects (files starting with _ are not effects; load by path).

area(): the content box clear of the page header and the caption pill · mono(): initials for a name ·
marker(): the highlighter sweep over *marked* words · src_line(): the small "来源" footnote ·
fitted(): fit.fit_text in px with house markup kept · counter(): a deterministic count-up.
"""
import re
from h9 import fit
from h9.aefx import _cap_clear

PAPER, INK, LEMON = "#fbfaf6", "#111111", "#f6ce3a"

CSS = r"""
.ct-root { position:absolute; inset:0; }
.ct-root .em { white-space:nowrap; }
.ct-root .em .emb { left:-.06em; right:-.06em; top:.04em; bottom:-.02em; background:#f6ce3a; border-radius:.08em; }
.ct-src { position:absolute; font-family:var(--f-mono, monospace); letter-spacing:.02em; color:var(--muted); display:flex; align-items:center; gap:.7em; white-space:nowrap; }
.ct-src b { font-weight:700; color:var(--fg); }
.ct-src i { font-style:normal; display:inline-block; padding:.12em .55em; border:.12em solid currentColor; border-radius:.3em; font-weight:700; }
.ct-kick { align-self:flex-start; display:inline-block; font:700 20px var(--f-body); letter-spacing:.14em; color:var(--bg); background:var(--fg); padding:6px 14px; border-radius:6px; }
.ct-mono { display:grid; place-items:center; border-radius:50%; font-family:var(--f-display); font-weight:900; color:#fbfaf6; letter-spacing:-.02em; flex:none; }
"""

TONES = ["#e2321f", "#2b59c3", "#1f8a5b", "#c9861a", "#7a4bc2", "#c23b75", "#2f8f9d", "#5b6470"]


def area(X, p):
    """(x0, y0, x1, y1) px: under the page header, above the caption pill (16:9) / above the 9:16 caption band."""
    W, H = X.W, X.H
    if X.portrait:
        return 56, 252, W - 56, (1300 if p.get("line") else 1440)
    bot = H - (_cap_clear(X, p) if p.get("line") else 60) - 8
    return 96, 108 if p.get("line") else 70, W - 96, bot


def fitted(X, text, w, h, max_px, min_px=None, max_lines=3, lh=1.18, mono=False):
    """fit.fit_text, with a little extra room for Latin text (serif Latin runs wider than the per-glyph estimate)."""
    s = fit.as_text(text)
    latin = sum(1 for c in s if c.isascii() and c.isalpha()) / max(len(s), 1)
    return fit.fit_text(s, w * (1 - 0.1 * latin), h, max_px, min_px, lh=lh, max_lines=max_lines, mono=mono)


def lines(X, f, cls="ct-l"):
    """one block per fitted line, each holding an inline-block (so lines can lift out of their own mask)."""
    return "".join(f'<span class="{cls}" style="display:block"><span style="display:inline-block; white-space:nowrap">{X.rich(l)}</span></span>' for l in f.lines)


def mono(name):
    """'Sam Altman' → 'SA' · '史蒂夫·乔布斯' → '乔' · 'OpenAI' → 'O'."""
    s = re.sub(r"[@＠]", "", str(name or "?")).strip()
    if not s: return "?"
    if re.search(r"[⺀-鿿]", s):
        return s.replace("·", "").replace(" ", "")[0]
    parts = [w for w in re.split(r"[\s\-_.]+", s) if w]
    return (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")).upper()


def tone(name):
    return TONES[sum(map(ord, str(name or ""))) % len(TONES)]


def mono_html(X, name, size_px, image=None, cls="ct-mono"):
    if image:
        return f'<img class="{cls}" src="{X.asset(image)}" alt="" style="width:{size_px}px; height:{size_px}px; object-fit:cover; border-radius:50%">'
    m = mono(name)
    X.used_text.update(m)
    return f'<div class="{cls}" style="width:{size_px}px; height:{size_px}px; font-size:{size_px * (0.42 if len(m) > 1 else 0.5):.0f}px; background:{tone(name)}">{X.rich(m)}</div>'


def marker(X, sel, t, each=0.32, ink=True):
    """sweep the highlighter under every *marked* run inside sel, one after another; the marked text turns ink."""
    X.tw(f'tl.fromTo("{sel} .em .emb", {{scaleX:0}}, {{scaleX:1, duration:{each:.2f}, ease:"power2.inOut", stagger:{each * 0.85:.2f}}}, {t:.3f});')
    if ink: X.tw(f'tl.to("{sel} .em .emt", {{color:"{INK}", duration:0.12, stagger:{each * 0.85:.2f}}}, {t + 0.08:.3f});')


def src_html(X, text, tag="来源", size_px=18, style="", cls="ct-src"):
    """the small footnote: [来源] text — set where the effect wants it (absolute; style gives the position)."""
    if not text: return ""
    X.used_text.update(str(text) + str(tag))
    return f'<div class="{cls}" style="font-size:{size_px}px; {style}"><i>{X.rich(tag)}</i><span>{X.rich(text)}</span></div>'


def counter(X, sel, t, a, b, dur=1.0, fmt="int"):
    js = {"int": "Math.round(o.v).toLocaleString('en-US')", "zh": "(o.v>=1e8?(o.v/1e8).toFixed(1)+'亿':o.v>=1e4?(o.v/1e4).toFixed(1)+'万':Math.round(o.v).toLocaleString('en-US'))"}[fmt]
    X.used_text.update("0123456789.,万亿")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power3.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


def drift(X, sel, t, d, s=1.03, y=0):
    X.tw(f'tl.fromTo("{sel}", {{scale:1, y:0}}, {{scale:{s}, y:{y}, duration:{max(d, 0.1):.2f}, ease:"none"}}, {t:.3f});')
