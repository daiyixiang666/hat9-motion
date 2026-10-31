"""kinetic · 大字快板 —— Dan Koe 的黑白极简 + Hormozi 的大字节奏。
黑底白字，只有一个荧光黄；字本身就是画面，一句一页地弹出、换页，金句页带一下震动。不烧额外字幕。
适合：金句、观点总结、开场钩子、片尾 CTA。
"""
STYLE = {
    "name": "大字快板", "en": "Kinetic Type", "benchmarks": ["Dan Koe", "Alex Hormozi", "林亦LYi"],
    "tokens": {
        "bg": "#0a0a0a", "fg": "#fafafa", "muted": "#6f6f6f", "accent": "#FDE047", "accent2": "#FDE047", "alert": "#ff3b30",
        "line": "#1f1f1f", "paper": "#0a0a0a", "ink": "#000", "card": "#fafafa", "card-fg": "#0a0a0a",
        "display-weight": "400", "display-tracking": "0", "title-size": "250px", "stmt-size": "180px", "quote-size": "110px", "pad": "140px",
        "lab-bg": "#fafafa", "lab-fg": "#0a0a0a", "lab-size": "54px", "chip-bg": "#FDE047", "chip-fg": "#0a0a0a", "chip-radius": "0",
        "dot-on": "#3a3a3a", "num-fg": "#FDE047", "num-unit": "#fafafa", "num-size": "380px", "numlbl-size": "64px", "split-a": "#3a3a3a",
        "veil": "rgba(10,10,10,.7)", "mark": "#FDE047",
    },
    "fonts": {"display": ["anton", "smiley-sans"], "body": "smiley-sans", "mono": "space-mono", "num": "anton"},
    "motion": {"ease": "expo.out", "dur": 0.35, "stagger": 0.02, "text": "zoom", "heading": "zoom", "media": "zoom",
               "accent": "pop", "quote": "pop", "camera": "none", "transition": "flash", "cut": "hard", "em": "static"},
    "captions": False,
    "layers": [],
    "title": {"layout": "poster", "image": "none", "rule": False, "stagger": 0.0},
    "statement": {"layout": "center", "mode": "swap", "split": False},
    "compare": {"variant": "halves", "camera": "none", "in_a": "left", "in_b": "right", "lab_verb": "pop"},
    "number": {"layout": "center", "viz": "none"},
    "quote": {"layout": "center", "image": False},
    "outro": {"layout": "right"},
    "mascot": {"mode": "cameo", "frame": "sticker", "landscape": {"left": 40, "bottom": 10, "h": 250}, "portrait": {"left": 40, "bottom": 280, "h": 280}},
    "sfx": {"transition": ("whoosh", 0.45), "title": ("slam", 0.55), "line": ("slam", 0.5), "enter": ("whoosh", 0.4), "pop": ("pop", 0.45),
            "hit": ("hit", 0.55), "count": ("riser", 0.35), "mark": ("pop", 0.4), "mascot": ("boing", 0.4)},
}

STYLE["css"] = """
.st-kinetic .em .emb { display:none; } .st-kinetic .em .emt { color:var(--accent); display:inline-block; transform:scale(1.12); }
.st-kinetic .s-title .kick { font-family:var(--f-mono); color:var(--accent); font-size:28px; letter-spacing:.2em; }
.st-kinetic .s-title .sub { font-family:var(--f-body); font-size:56px; color:var(--fg); }
.st-kinetic .s-compare .lab { font-family:var(--f-body); border-radius:0; padding:6px 30px; }
.st-kinetic .s-compare .chip { font-family:var(--f-body); font-size:40px; padding:10px 34px; }
.st-kinetic .s-compare .stk { font-family:var(--f-body); }
.st-kinetic .s-number .lbl { font-family:var(--f-body); }
.st-kinetic .s-number .sub { font-family:var(--f-mono); color:var(--muted); }
.st-kinetic .s-quote .q { line-height:1.15; }
.st-kinetic .s-outro .ttl { font-size:150px; } .st-kinetic .s-outro .sub { font-family:var(--f-body); color:var(--fg); font-size:44px; }
.st-kinetic .s-outro .cta { border-radius:0; color:#0a0a0a; font-family:var(--f-body); font-size:36px; }
"""
