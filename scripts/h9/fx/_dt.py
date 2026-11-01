"""shared bits for the WP2 data effects (table, statement_table, waterfall, scale_compare, bar_race, stacked_bars,
formula, bars_csv / line_csv). Files starting with _ are helpers, not effects; effects load this one by path.

box(X)            content rectangle in vmin that stays clear of the page header and the caption pill, both aspects
compact(vals)     (divisor, suffix) so a column of huge numbers reads 万 / 亿 (or K / M / B)
fmt / js_fmt      the same number format in Python (static text) and in the browser (counters)
count(...)        a GSAP counter on one element (deterministic: driven by the master timeline)
rows_of(p, X)     a table from p["rows"] or p["csv"] (+ cols / limit); wide_of / series_of for charts
"""
import importlib.util, json, pathlib, sys

if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]
from h9 import data as D  # noqa: E402

em, fit, lines_html = F.em, F.fit, F.lines_html


def frame(X):
    m = min(X.W, X.H); return X.W / m * 100, X.H / m * 100


def box(X):
    """(x, y, w, h) in vmin — under the header, above the caption, inside the side margins."""
    Wv, Hv = frame(X)
    if X.portrait: return 6.0, 24.0, Wv - 12.0, 95.0
    return 9.0, 13.0, Wv - 18.0, 71.0


def compact(vals, mode="cn"):
    vabs = max([abs(v) for v in vals if v is not None] or [0])
    return F.compact(vabs, mode)


def decimals(vals, div=1):
    return 1 if div != 1 or any(v is not None and abs(v / div - round(v / div)) > 1e-9 for v in vals) else 0


def fmt(v, dec=0, div=1, paren=False, sign=False):
    if v is None: return "—"
    x = v / div
    s = f"{abs(x):,.{dec}f}"
    if x < 0: return f"({s})" if paren else f"−{s}"
    return f"+{s}" if sign and x > 0 else s


def js_fmt(dec=0, paren=False, sign=False):
    neg = '"("+s+")"' if paren else '"−"+s'
    pos = '"+"+s' if sign else "s"
    return (f'(x)=>{{const s=Math.abs(x).toLocaleString("en-US",{{minimumFractionDigits:{dec},maximumFractionDigits:{dec}}});'
            f'return x<-1e-9?{neg}:(x>1e-9?{pos}:s);}}')


def count(X, sel, t, a, b, dur=0.9, dec=0, paren=False, sign=False, ease="power3.out"):
    X.used_text.update("0123456789.,−+()%")
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"), f={js_fmt(dec, paren, sign)}; if(!el) return; '
         f'tl.to(o, {{v:{b}, duration:{dur:.3f}, ease:"{ease}", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {t:.3f});}})();')


def cue(X, p, key, t, default):
    v = p.get(key)
    if v is None: return default
    try: return float(X.T(v, t))
    except SystemExit: return default


def rows_of(p, X):
    """table rows (header first) from p["rows"] or a spreadsheet: {"csv": "x.csv", "cols": [...], "limit": 8}."""
    if p.get("csv"):
        return D.grid(p["csv"], cols=p.get("cols"), rows=p.get("limit"), base=X.src)
    return [[("" if c is None else c) for c in r] for r in p.get("rows", [])]


def series_of(p, X, key="items"):
    if p.get("csv"):
        return D.series(p["csv"], p.get("x", 0), p.get("y", 1), base=X.src)
    return [[str(a), float(b)] for a, b in p.get(key, [])]


def wide_of(p, X):
    """-> (labels, [(name, [values])]) from p["csv"] (x + series columns) or p["labels"] + p["series"]."""
    if p.get("csv"):
        labels, s = D.wide(p["csv"], p.get("x", 0), p.get("series_cols"), base=X.src)
        return labels, list(s.items())
    ser = p.get("series", {})
    items = list(ser.items()) if isinstance(ser, dict) else [(a, b) for a, b in ser]
    return [str(x) for x in p.get("labels", [])], [(str(k), [float(v) for v in vs]) for k, vs in items]


def is_num(c):
    return D.num(c) is not None and not (isinstance(c, str) and c.strip() and not any(ch.isdigit() for ch in c))


J = json.dumps
