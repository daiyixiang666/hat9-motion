"""Custom styles built on an existing one: a style file that says `BASE = "ink"` inherits that style's scenes, effects
framing, camera and sound, and only overrides what it writes. Used by styles made with `hat9.py style new`.

  from h9 import derive
  BASE = "ink"
  _b = derive.load_base(BASE)
  STYLE = derive.merge(_b.STYLE, {"name": ..., "tokens": {...}, "css": "..."})

The rendered root carries both classes (`st-<yours> st-<base>`), so the base's own CSS keeps working untouched and
yours, appended after it, wins.
"""
import importlib.util, re
from pathlib import Path

STYLES = Path(__file__).resolve().parent.parent.parent / "styles"
DEEP = ("tokens", "fonts", "motion", "mascot", "sfx", "fx_themes", "moods")


def load_base(sid):
    p = STYLES / f"{sid}.py"
    if not p.exists(): raise SystemExit(f"base style {sid!r} not found in styles/")
    spec = importlib.util.spec_from_file_location(f"_base_{sid}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def merge(base, over):
    """base STYLE + your changes. Dict-valued keys (tokens, fonts, motion …) merge one level deep; css is appended
    after the base's; a key set to None is dropped (e.g. "fx_themes": None -> effect grounds follow your tokens)."""
    out = dict(base)
    for k, v in over.items():
        if v is None:
            out.pop(k, None)
        elif k == "css":
            out["css"] = base.get("css", "") + "\n" + v
        elif k in DEEP and isinstance(v, dict) and isinstance(base.get(k), dict):
            merged = dict(base[k])
            merged.update(v)
            out[k] = merged
        else:
            out[k] = v
    return out


def base_of(sid):
    p = STYLES / f"{sid}.py"
    if not p.exists(): return None
    m = re.search(r'^BASE\s*=\s*["\'](\w+)["\']', p.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def chain(sid):
    """[sid, its base, the base's base …] — e.g. ["myink", "ink"]."""
    out = [sid]
    while True:
        b = base_of(out[-1])
        if not b or b in out: return out
        out.append(b)
