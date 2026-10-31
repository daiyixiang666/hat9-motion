"""reel · 动效库展示 —— a neutral, refined stage for showing the AE 动效库 effects one by one (not a content style)."""
STYLE = {
    "name": "动效库展示", "en": "FX Reel", "benchmarks": [],
    "tokens": {"bg": "#121110", "fg": "#f2ede4", "muted": "#8a847a", "accent": "#ff5a1f", "accent2": "#ff5a1f", "alert": "#ff5a1f",
               "line": "#2a2826", "paper": "#ece7dd", "ink": "#121110", "card": "#1b1a18", "card-fg": "#f2ede4", "display-weight": "900"},
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "latin": "eb-garamond-italic", "num": "inter", "hand": "ma-shan-zheng", "quote": "noto-serif-sc"},
    "motion": {"ease": "expo.out", "dur": 0.6, "stagger": 0.03, "cut": "hard", "transition": "flash", "em": "static"},
    "captions": False, "layers": [("grain", {"opacity": 0.05})],
    "sfx": {"transition": ("whoosh", 0.35), "pop": ("pop", 0.45), "enter": ("whoosh_soft", 0.35), "slam": ("slam", 0.5), "count": ("type", 0.35),
            "type": ("type", 0.4), "brush": ("brush", 0.5), "boing": ("boing", 0.45), "glitch": ("glitch", 0.45), "whoosh_soft": ("whoosh_soft", 0.35), "whoosh_deep": ("whoosh_deep", 0.4), "paper": ("paper", 0.45), "click": ("click", 0.3), "hit": ("hit", 0.5)},
    "css": "",
}
