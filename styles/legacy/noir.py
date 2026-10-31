"""noir · 暗场纪录 —— LEMMiNO 的克制与精准。
近黑底、1px 白色细线框、悬在三维空间里微微转向的窗口、宽字距细体字；琥珀色只占画面 <10%。慢、准、不回弹。
适合：悬疑、未解问题、"AI 会不会取代审美"这类大命题。
"""
STYLE = {
    "name": "暗场纪录", "en": "Dark Documentary", "benchmarks": ["LEMMiNO", "所长林超"],
    "tokens": {
        "bg": "#0b0b0c", "fg": "#e9e8e4", "muted": "#7c7c7a", "accent": "#ffb000", "accent2": "#ffb000", "alert": "#ff6b4a",
        "line": "#262628", "paper": "#0b0b0c", "ink": "#000", "card": "#111113", "card-fg": "#e9e8e4",
        "display-weight": "300", "display-tracking": "0.12em", "title-size": "92px", "stmt-size": "88px", "quote-size": "66px", "pad": "180px",
        "lab-bg": "transparent", "lab-fg": "#e9e8e4", "lab-size": "28px", "chip-bg": "transparent", "chip-fg": "#7c7c7a",
        "dot-on": "#3a3a3c", "dot-radius": "50%", "num-fg": "#e9e8e4", "num-unit": "#ffb000", "num-weight": "200", "split-a": "#3a3a3c",
        "veil": "linear-gradient(180deg, rgba(11,11,12,.55), rgba(11,11,12,.85))", "float-border": "rgba(233,232,228,.45)",
        "cap-fg": "#e9e8e4", "cap-size": "38px", "cap-weight": "300", "cap-shadow": "0 0 12px rgba(0,0,0,.9)", "cap-em": "#ffb000",
        "mark": "#ffb000", "mark-size": "22px", "mascot-bg": "#141416", "mascot-shadow": "0 0 0 1px rgba(233,232,228,.4)",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "num": "inter"},
    "motion": {"ease": "power2.out", "dur": 0.9, "stagger": 0.045, "text": "blurin", "heading": "blurin", "media": "fade",
               "accent": "fade", "quote": "blurin", "camera": "drift", "transition": "dip", "cut": "hard", "em": "static"},
    "layers": [("grain", {"opacity": 0.07}), ("vignette", {"alpha": 0.6, "inner": 45})],
    "title": {"layout": "chapter", "image": "full", "rule": False},
    "statement": {"layout": "center"},
    "compare": {"variant": "float", "camera": "none", "in_a": "blurin", "in_b": "blurin", "lab_verb": "fade"},
    "number": {"layout": "left", "viz": "dots"},
    "quote": {"layout": "center", "camera": "drift"},
    "outro": {"layout": "right", "mascot": {"x": -860, "y": -330, "scale": 1.7}},
    "mascot": {"mode": "corner", "frame": "circle", "landscape": {"right": 60, "bottom": 50, "h": 200}, "portrait": {"right": 60, "bottom": 300, "h": 240}},
    "mark_width": 2,
    "sfx": {"transition": ("whoosh_deep", 0.35), "title": ("boom", 0.35), "line": None, "enter": ("whoosh_soft", 0.2), "pop": None,
            "hit": ("boom", 0.4), "count": ("tick", 0.2), "mark": ("tick", 0.3), "cut": None, "mascot": ("whoosh_soft", 0.25)},
}

STYLE["css"] = """
.st-noir img { filter:grayscale(1) contrast(1.08) brightness(.95); }
.st-noir .em .emb { display:none; } .st-noir .em .emt { color:var(--accent); }
.st-noir .s-title .kick { font-family:var(--f-mono); color:var(--accent); letter-spacing:.5em; font-size:20px; }
.st-noir .s-title .sub { font-weight:300; letter-spacing:.3em; font-size:28px; }
.st-noir .s-compare .lab { font-family:var(--f-mono); font-size:22px; letter-spacing:.3em; color:var(--muted); }
.st-noir .s-compare .chip { font-family:var(--f-mono); font-size:20px; letter-spacing:.4em; font-weight:400; border-top:1px solid #444; border-bottom:1px solid #444; padding:10px 24px; }
.st-noir .s-compare .stk { background:none; color:var(--accent); border:1px solid var(--accent); box-shadow:none; font-weight:300; font-size:26px; border-radius:0; }
.st-noir .s-compare .dim { background:rgba(11,11,12,.75); }
.st-noir .s-statement .ln { font-weight:300; }
.st-noir .s-number .val { font-weight:200; }
.st-noir .s-number .sub { font-family:var(--f-mono); color:var(--accent); letter-spacing:.4em; font-size:18px; }
.st-noir .s-number .dots i { width:14px; height:14px; } .st-noir .s-number .dots { grid-template-columns:repeat(10, 14px); gap:26px; }
.st-noir .s-number .lbl { font-weight:300; font-size:46px; letter-spacing:.06em; }
.st-noir .s-quote .q { font-weight:300; letter-spacing:.08em; }
.st-noir .s-outro .ttl { font-weight:300; letter-spacing:.3em; font-size:80px; }
.st-noir .s-outro .cta { background:none; color:var(--accent); border:1px solid var(--accent); border-radius:0; font-weight:400; font-family:var(--f-mono); font-size:22px; letter-spacing:.3em; }
"""
