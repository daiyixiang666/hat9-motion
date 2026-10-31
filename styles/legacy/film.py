"""film · 胶片随笔 —— Pursuit of Wonder / Nathaniel Drew 的颗粒怀旧。
暖调分级、常驻颗粒、宽银幕黑边，字幕写在下黑边里；小号宋体、慢淡入；转场是黑场，音效几乎没有。
适合：审美、选择、"慢下来想一想"的情绪类判断。
"""
STYLE = {
    "name": "胶片随笔", "en": "Film Essay", "benchmarks": ["Pursuit of Wonder", "Nathaniel Drew", "小约翰可汗"],
    "tokens": {
        "bg": "#141210", "fg": "#efe6d6", "muted": "#a39a8a", "accent": "#e3a85b", "accent2": "#e3a85b", "alert": "#c8553d",
        "line": "#2c2722", "paper": "#141210", "ink": "#0b0a09", "card": "#1c1916", "card-fg": "#efe6d6",
        "display-weight": "300", "display-tracking": "0.08em", "title-size": "86px", "stmt-size": "72px", "quote-size": "64px", "pad": "220px",
        "lab-bg": "transparent", "lab-fg": "#efe6d6", "lab-size": "30px", "chip-bg": "transparent", "chip-fg": "#a39a8a",
        "dot-on": "#4a433b", "split-a": "#4a433b", "num-fg": "#efe6d6", "num-unit": "#e3a85b", "num-weight": "200", "numlbl-size": "44px",
        "veil": "linear-gradient(180deg, rgba(20,18,16,.15) 0%, rgba(20,18,16,.35) 55%, rgba(20,18,16,.85) 100%)",
        "cap-fg": "#e9dfcd", "cap-size": "32px", "cap-weight": "400", "cap-shadow": "none", "cap-bottom": "30px", "cap-em": "#e3a85b",
        "mark": "#e3a85b", "mascot-w": "0px",
    },
    "fonts": {"display": ["eb-garamond", "noto-serif-sc"], "body": "noto-serif-sc", "cap": "noto-serif-sc", "mono": "courier-prime", "num": "eb-garamond", "quote": "noto-serif-sc"},
    "motion": {"ease": "sine.out", "dur": 1.0, "stagger": 0.05, "text": "blurin", "heading": "blurin", "media": "fade",
               "accent": "fade", "quote": "blurin", "camera": "push", "transition": "leak", "cut": "dip", "em": "static"},
    "layers": [("grain", {"opacity": 0.16, "fps": 24, "alpha": 0.7}), ("vignette", {"alpha": 0.5, "inner": 40}), ("letterbox", {"ratio": 2.2})],
    "title": {"layout": "lower", "image": "full", "rule": False, "stagger": 0.08},
    "statement": {"layout": "center", "stagger": 0.06},
    "compare": {"variant": "halves", "camera": "push", "in_a": "fade", "in_b": "fade", "lab_verb": "fade"},
    "number": {"layout": "center", "viz": "bar"},
    "quote": {"layout": "center", "camera": "push"},
    "outro": {"layout": "center", "mascot": {"x": 0, "y": 0, "scale": 1.0}},
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 70, "bottom": 104, "h": 220}, "portrait": {"right": 60, "bottom": 300, "h": 260}},
    "sfx": {"transition": ("whoosh_soft", 0.18), "title": None, "line": None, "enter": None, "pop": None, "hit": None, "count": None, "mark": None, "cut": None, "mascot": None},
}

STYLE["css"] = """
.st-film .em .emb { display:none; } .st-film .em .emt { color:var(--accent); }
.st-film .s-title .ttl { font-style:normal; }
.st-film .s-title .sub { font-family:var(--f-mono); font-size:22px; letter-spacing:.3em; color:var(--muted); }
.st-film .s-compare .lab { top:auto; bottom:150px; font-family:var(--f-body); font-weight:300; letter-spacing:.3em; }
.st-film .s-compare .chip { top:130px; font-family:var(--f-mono); font-weight:400; letter-spacing:.2em; font-size:22px; }
.st-film .s-compare .stk { display:none; }
.st-film .s-compare.v-halves .A { border-right:2px solid var(--bg); }
.st-film .s-number .bar { height:3px; width:640px; background:#3a332c; } .st-film .s-number .bar b { background:var(--accent); }
.st-film .s-number .val { font-style:italic; }
.st-film .s-number .sub { font-family:var(--f-mono); letter-spacing:.3em; }
.st-film .s-outro .ttl { font-weight:300; letter-spacing:.3em; font-size:72px; }
.st-film .s-outro .cta { background:none; color:var(--muted); font-family:var(--f-mono); font-weight:400; letter-spacing:.2em; font-size:22px; }
.st-film .s-outro .L-center { padding-bottom:60px; }
.st-film #mascot { opacity:.92; }
"""
