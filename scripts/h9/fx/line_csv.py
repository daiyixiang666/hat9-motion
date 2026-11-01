"""折线 · 直接读表格 (line_draw from a spreadsheet): {"csv": "nev.csv", "x": "年份", "y": "合计"} → the `line_draw` effect.
Everything else is passed through to `line_draw` (unit, dec, title, note, compact). Extra: "limit": N (last N rows),
"scale": a number to divide the column by.
"""
import importlib.util, pathlib, sys
if "h9fx__dt" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__dt", pathlib.Path(__file__).with_name("_dt.py"))
    sys.modules["h9fx__dt"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__dt"])
U = sys.modules["h9fx__dt"]


def line_csv(X, cid, t, d, p):
    from h9 import aefx
    rows = U.series_of(p, X)
    k = float(p.get("scale", 1) or 1)
    rows = [[a, b / k] for a, b in rows]
    if p.get("sort") in ("desc", "asc"): rows.sort(key=lambda r: r[1], reverse=p["sort"] == "desc")
    if p.get("limit"): rows = rows[: int(p["limit"])] if "line" == "bars" else rows[-int(p["limit"]):]
    q = {k_: v for k_, v in p.items() if k_ not in ("csv", "x", "y", "sort", "limit", "scale")}
    q["points"] = rows or [["—", 0]]
    q["fxid"] = p.get("fxid", "line_csv")
    aefx.FX["line_draw"](X, cid, t, d, q)


FX = {"line_csv": line_csv}
