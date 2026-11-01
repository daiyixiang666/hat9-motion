"""data — tables straight from a spreadsheet, so a data beat can say {"csv": "sales.csv", "x": "年份", "y": "销量"}.

  read(path)                         -> (header, rows)   CSV (UTF-8 / UTF-8-BOM / GBK), TSV, or .xlsx (needs openpyxl)
  num(cell)                          -> float | None     "1,286.6" "12.5%" "(167.7)" "−3" "4.6万" "44.5亿" "—"
  column(header, name_or_index)      -> index            a header name, a 0-based index, or an Excel letter ("B")
  series(path, x, y)                 -> [[label, value]] one numeric column against a label column
  wide(path, x, cols=None)           -> (labels, {name: [values]})   one label column + several numeric columns
  grid(path, cols=None, rows=None)   -> [[cells]]        the table as text (header first), optionally sliced

Paths are relative to the video.json (pass X.src as `base`). Nothing here needs a browser.
"""
import csv, io, re
from pathlib import Path

UNIT = {"万": 1e4, "亿": 1e8, "千": 1e3, "百万": 1e6, "k": 1e3, "K": 1e3, "M": 1e6, "B": 1e9, "bn": 1e9}
BLANK = {"", "—", "–", "-", "--", "n/a", "N/A", "NA", "null", "None", "/"}


def _path(path, base=None):
    p = Path(path)
    if not p.is_absolute() and base is not None: p = Path(base) / p
    if not p.exists(): raise SystemExit(f"data: file not found: {p}")
    return p


def read(path, base=None, sheet=None):
    """-> (header, rows) with every cell as a stripped string."""
    p = _path(path, base)
    if p.suffix.lower() in (".xlsx", ".xlsm"):
        try:
            import openpyxl
        except ImportError:
            raise SystemExit(f"data: {p.name} is an Excel file — `pip install openpyxl`, or save it as CSV")
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        rows = [["" if c is None else str(c).strip() for c in r] for r in ws.iter_rows(values_only=True)]
    else:
        raw = p.read_bytes()
        for enc in ("utf-8-sig", "gb18030"):
            try: text = raw.decode(enc); break
            except UnicodeDecodeError: continue
        dialect = "excel-tab" if p.suffix.lower() == ".tsv" or text.count("\t") > text.count(",") else "excel"
        rows = [[c.strip() for c in r] for r in csv.reader(io.StringIO(text), dialect=dialect)]
    rows = [r for r in rows if any(c for c in r)]
    if not rows: raise SystemExit(f"data: {p.name} is empty")
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    return rows[0], rows[1:]


def num(cell):
    """a spreadsheet cell -> float (None when blank / not a number). Handles 千分位, %, (负数), −, 万 / 亿 / K / M / B."""
    if cell is None: return None
    if isinstance(cell, (int, float)): return float(cell)
    s = str(cell).strip().replace(",", "").replace("，", "").replace(" ", "")
    if s in BLANK: return None
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()").replace("−", "-").replace("–", "-").replace("＋", "+")
    s = re.sub(r"^[¥$€£￥]", "", s)
    mul = 1.0
    if s.endswith("%"): s = s[:-1]
    for u in sorted(UNIT, key=len, reverse=True):
        if s.endswith(u) and re.match(r"^[+-]?[\d.]+$", s[: -len(u)]):
            mul = UNIT[u]; s = s[: -len(u)]; break
    try: v = float(s) * mul
    except ValueError: return None
    return -v if neg else v


def column(header, key):
    if isinstance(key, int): return key
    k = str(key).strip()
    if k in header: return header.index(k)
    low = [h.lower() for h in header]
    if k.lower() in low: return low.index(k.lower())
    if re.fullmatch(r"[A-Za-z]{1,2}", k):            # Excel letters
        i = 0
        for ch in k.upper(): i = i * 26 + (ord(ch) - 64)
        return i - 1
    if k.isdigit(): return int(k)
    raise SystemExit(f"data: no column {key!r}; have: {', '.join(header)}")


def series(path, x=0, y=1, base=None):
    header, rows = read(path, base)
    xi, yi = column(header, x), column(header, y)
    out = [[r[xi], num(r[yi])] for r in rows]
    return [[a, b] for a, b in out if b is not None]


def wide(path, x=0, cols=None, base=None):
    """-> (labels, {series_name: [values]}) — every numeric column (or just `cols`) against the label column."""
    header, rows = read(path, base)
    xi = column(header, x)
    idx = [column(header, c) for c in cols] if cols else [i for i in range(len(header)) if i != xi and any(num(r[i]) is not None for r in rows)]
    labels = [r[xi] for r in rows]
    return labels, {header[i]: [num(r[i]) or 0.0 for r in rows] for i in idx}


def grid(path, cols=None, rows=None, base=None):
    """the table as text: header row first. cols = names/indices to keep (in order); rows = max data rows."""
    header, body = read(path, base)
    idx = [column(header, c) for c in cols] if cols else list(range(len(header)))
    body = body[:rows] if rows else body
    return [[header[i] for i in idx]] + [[r[i] for i in idx] for r in body]
