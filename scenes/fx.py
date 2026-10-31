"""fx — one effect from the AE 动效库 (scripts/h9/aefx.py) as a beat: {"scene": "fx", "fx": "pop", "text": "...", ...}"""
from h9 import aefx


def build(b, X, t, d, cid):
    fn = aefx.FX.get(b["fx"])
    if not fn: raise SystemExit(f"unknown fx {b['fx']!r}; have: {', '.join(sorted(aefx.FX))}")
    fn(X, cid, t, d, b)
