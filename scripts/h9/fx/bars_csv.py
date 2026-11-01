"""柱状图 · 直接读表格 (bars from a spreadsheet): {"csv": "sales.csv", "x": "年份", "y": "销量"} → the `bars` effect.
Everything else is passed through to `bars` (unit, dec, hl, title, note, growth, orient, compact). Extra: "sort": "desc" | "asc",
"limit": N (keep the first N after sorting), "scale": a number to divide the column by (e.g. 10000 for 万).
Categories that are not periods (brands, cities…) are sorted biggest-first by default ("sort": "keep" to keep file order).
"""
import importlib.util, pathlib, re, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]


def bars_csv(X, cid, t, d, p):
    from h9 import aefx
    rows = U.series_of(p, X)
    k = float(p.get("scale", 1) or 1)
    rows = [[a, b / k] for a, b in rows]
    timeish = all(re.fullmatch(r"\s*(\d{2,4}|\d{4}[-/.年]\S*|Q\d.*|\d{1,2}月|第.+[年季月周])\s*", str(r[0])) for r in rows)
    sort = p.get("sort", "keep" if timeish else "desc")
    if sort in ("desc", "asc"): rows.sort(key=lambda r: r[1], reverse=sort == "desc")
    if p.get("limit"): rows = rows[: int(p["limit"])] if "bars" == "bars" else rows[-int(p["limit"]):]
    q = {k_: v for k_, v in p.items() if k_ not in ("csv", "x", "y", "sort", "limit", "scale")}
    q["items"] = rows or [["—", 0]]
    q["fxid"] = p.get("fxid", "bars_csv")
    if sort == "desc" and "hl" not in p: q["hl"] = 0      # the leader; no growth chip on a ranking
    aefx.FX["bars"](X, cid, t, d, q)


FX = {"bars_csv": bars_csv}
