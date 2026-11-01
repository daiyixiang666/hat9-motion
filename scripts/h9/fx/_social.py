"""shared helpers for the social / people / China-map effects (files starting with _ are not effects).

Avatars are monograms by default (a person's first glyph on a colour picked from their name, stable across
builds); an image path turns it into a photo avatar. Sizes are in vmin so 16:9 and 9:16 share one design."""
import hashlib, re
from h9 import fit as FT

TONES = ["#e2321f", "#2f6fdb", "#1f9d6b", "#d98a00", "#7b4fd1", "#c2417a", "#127a8a", "#5a6270"]


def tone(name):
    return TONES[int(hashlib.md5(str(name).encode("utf-8")).hexdigest(), 16) % len(TONES)]


def mono(name):
    """the glyph on a monogram: first Latin letter (upper-case) or the first CJK glyph."""
    s = str(name or "").strip().lstrip("@#")
    if not s: return "?"
    return s[0].upper() if re.match(r"[A-Za-z0-9]", s) else s[0]


def avatar(X, name, img=None, cls="", style=""):
    if img:
        return f'<i class="wp-av {cls}" style="background:#ccc url({X.asset(img)}) center/cover;{style}"></i>'
    return f'<i class="wp-av {cls}" style="background:{tone(name)};{style}">{X.rich(mono(name))}</i>'


def cue(X, p, key, t, dflt):
    v = p.get(key)
    return float(X.T(v, t)) if v is not None else dflt


def px(X, v): return min(X.W, X.H) * v / 100       # vmin → px


def vm(X, v): return v * 100 / min(X.W, X.H)       # px → vmin


def likes(v):
    """1234 → "1234", 12345 → "1.2万"; strings pass through."""
    if v is None or v == "": return ""
    if isinstance(v, str) and not re.fullmatch(r"-?[\d.,]+", v.strip()): return v
    n = float(str(v).replace(",", ""))
    return FT.fmt_num(n) if n >= 1e4 else f"{int(n)}"


def num(v):
    try: return float(str(v).replace(",", "").replace("%", ""))
    except (TypeError, ValueError): return None


def items(v, keys=("name", "text")):
    """"名字：内容" | [名字, 内容, …] | {...} → dicts with at least keys[0], keys[1]."""
    out = []
    for it in FT.as_list(v):
        if isinstance(it, dict): out.append(dict(it)); continue
        if isinstance(it, (list, tuple)):
            d = {keys[0]: it[0] if len(it) > 0 else "", keys[1]: it[1] if len(it) > 1 else ""}
            if len(it) > 2: d["likes"] = it[2]
            out.append(d); continue
        m = re.split(r"[：:]", str(it), maxsplit=1)
        out.append({keys[0]: m[0].strip(), keys[1]: m[1].strip()} if len(m) == 2 else {keys[0]: "", keys[1]: str(it)})
    return out


def lines_for(text, w_px, size_px, max_lines=4):
    """balanced lines of `text` at (about) size_px in a column w_px wide → (px, [lines])."""
    f = FT.fit_text(str(text), w_px, size_px * 1.5 * max_lines, size_px, size_px * 0.86, lh=1.45, max_lines=max_lines)
    return f.px, f.lines


CSS = r"""
.fx .wp-av { flex:none; display:grid; place-items:center; border-radius:50%; color:#fff; font-family:var(--f-body); font-weight:900; font-style:normal; line-height:1; }
.fx .wp-mock { position:absolute; z-index:4; font:700 1.7vmin/1 var(--f-body); letter-spacing:.1em; color:var(--card); background:var(--card-fg); padding:.5vmin 1.1vmin; border-radius:.5vmin; opacity:.82; }
.fx .wp-hand { display:inline-block; }
"""


def base_css(X): X.css("fx-wp-social", CSS)


HEART = '<svg viewBox="0 0 24 24"><path d="M12 21s-7.5-4.6-9.6-9.1C1 8.8 2.9 5 6.6 5c2.2 0 3.6 1.2 4.4 2.5C11.8 6.2 13.2 5 15.4 5 19.1 5 21 8.8 19.6 11.9 17.5 16.4 12 21 12 21z"/></svg>'
