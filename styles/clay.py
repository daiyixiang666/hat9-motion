"""clay · 陶土影棚 —— C4D 陶土渲染式的三维：哑光陶土、石膏白、赤陶唯一强调，柔和的真实投影，三维衬线立体字。
没有镀金、没有辉光；高级感来自材质、光和留白。对标：Buck / Ordinary Folk 的陶土风、Apple「iPhone 拍摄」陶土片、Airbnb 三维图标。
适合：观点、审美、需要温度又要高级的选题。
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("studio", Path(__file__).with_name("studio.py"))
_studio = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_studio)

STYLE = dict(_studio.STYLE)
STYLE.update({
    "name": "陶土影棚", "en": "Clay Studio", "benchmarks": ["Buck", "Ordinary Folk", "Apple iPhone 陶土片"],
    "look": "clay", "bg3d": "#cfc8be", "floor3d": "#cfc8be", "font3d": "noto-serif-sc", "aperture": 0.0011,
    "tokens": {**_studio.STYLE["tokens"], "bg": "#cfc8be", "fg": "#2b2723", "muted": "#7b7268", "accent": "#ad5632", "accent2": "#ad5632",
               "cap-fg": "#2b2723", "cap-shadow": "none", "cap-bg": "rgba(241,235,224,.82)", "cap-pad": "4px 16px", "cap-radius": "6px", "cap-em": "#c2643f"},
    "fonts": {"display": ["eb-garamond", "noto-serif-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono"},
    "layers": [("grain", {"opacity": 0.05, "blend": "multiply"})],
})
STYLE["css"] = _studio.STYLE["css"].replace(".st-studio", ".st-clay") + """
.st-clay .w-q .q { color:#2b2723; text-shadow:none; font-family:var(--f-display); font-weight:600; }
.st-clay .w-q .k { color:#a8502f; } .st-clay .w-tag { color:#4f4840; }
.st-clay .w-out .s { color:#6f665c; } .st-clay .w-out .c { background:#c2643f; color:#f6f1e8; }
"""
WORLD = _studio.WORLD
