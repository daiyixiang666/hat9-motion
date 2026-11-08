"""stage · 主持人剧场 —— Kurzgesagt 的发光扁平宇宙 + Cleo Abram 的"观众代理"。
深紫夜空、星点慢漂、所有东西自带光；圆角大卡片、弹性的小道具；主持人是主角，站在台前发光。
适合：类比、入门、日常场景里的判断题。
"""
STYLE = {
    "name": "主持人剧场", "en": "Mascot Stage", "benchmarks": ["Kurzgesagt", "Cleo Abram", "柴知道"],
    "tokens": {
        "bg": "#140e33", "fg": "#ffffff", "muted": "#b7b0e8", "accent": "#FFC145", "accent2": "#ff5a7a", "alert": "#ff5a7a",
        "line": "#3a2f72", "paper": "#140e33", "ink": "#0b0820", "card": "#ffffff", "card-fg": "#1b1446",
        "display-weight": "900", "display-tracking": "0", "title-size": "150px", "stmt-size": "124px", "quote-size": "84px", "pad": "150px",
        "radius": "28px", "lab-bg": "#FFC145", "lab-fg": "#1b1446", "lab-size": "40px", "lab-radius": "999px",
        "chip-bg": "#ffffff", "chip-fg": "#1b1446", "chip-radius": "999px", "dot-on": "#5a4fa3", "split-a": "#5a4fa3",
        "num-fg": "#FFC145", "num-unit": "#ffffff", "veil": "linear-gradient(180deg, rgba(20,14,51,.35), rgba(20,14,51,.85))",
        "cap-fg": "#ffffff", "cap-size": "42px", "cap-weight": "800", "cap-shadow": "0 3px 0 rgba(11,8,32,.9), 0 0 18px rgba(11,8,32,.7)", "cap-em": "#FFC145",
        "mark": "#FFC145", "mascot-glow": "rgba(255,193,69,.5)", "card-border": "10px solid #fff", "mascot-w": "360px",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "space-mono", "num": "inter", "mark": "zcool-kuaile"},
    "motion": {"ease": "back.out(1.6)", "dur": 0.55, "stagger": 0.03, "text": "rise", "heading": "pop", "media": "pop",
               "accent": "pop", "quote": "rise", "camera": "drift", "transition": "iris", "cut": "zoom", "em": "box"},
    "layers": [("bgcolor", {"css": "radial-gradient(ellipse 90% 70% at 50% 115%, #5b2fa0 0%, #2a1a6b 45%, #140e33 80%)"}), ("stars", {"n": 110})],
    "title": {"layout": "center", "image": "frame", "rule": False},
    "statement": {"layout": "center"},
    "compare": {"variant": "cards", "tilt": 5, "camera": "drift", "in_a": "pop", "in_b": "pop", "lab_verb": "pop"},
    "number": {"layout": "left", "viz": "dots"},
    "quote": {"layout": "center"},
    "outro": {"layout": "right", "mascot": {"x": 380, "y": -220, "scale": 1.45}},
    "mascot": {"mode": "corner", "frame": "glow", "landscape": {"left": 30, "bottom": 0, "h": 360}, "portrait": {"left": 30, "bottom": 280, "h": 380}},
    "sfx": {"transition": ("whoosh", 0.4), "title": ("pop", 0.45), "line": ("pop", 0.35), "enter": ("boing", 0.35), "pop": ("pop", 0.45),
            "hit": ("boing", 0.45), "count": ("tick", 0.3), "mark": ("pop", 0.4), "cut": ("whoosh_soft", 0.3), "mascot": ("boing", 0.45)},
}

STYLE["css"] = """
.st-stage .em .emb { left:-.12em; right:-.12em; top:.08em; bottom:-.02em; background:var(--accent2); border-radius:.3em; box-shadow:0 0 30px rgba(255,90,122,.6); }
.st-stage .s-title .ttl { text-shadow:0 0 40px rgba(255,193,69,.35); }
.st-stage .s-title.img-frame .frame { left:auto; right:150px; width:40%; border-radius:32px; border:10px solid #fff; box-shadow:0 0 0 0 #fff, 0 30px 80px rgba(0,0,0,.5), 0 0 80px rgba(255,193,69,.35); transform:translateY(-50%) rotate(3deg); }
.st-stage .s-title.img-frame .box { right:46%; align-items:flex-start; text-align:left; }
.st-stage .s-title .kick { font-family:var(--f-mark); color:var(--accent); letter-spacing:.1em; font-size:34px; text-transform:none; }
.st-stage .s-title .sub { color:var(--muted); font-weight:700; }
.st-stage .s-compare.v-cards .side { box-shadow:0 30px 80px rgba(0,0,0,.45), 0 0 60px rgba(167,139,250,.35); }
.st-stage .s-compare .lab { font-family:var(--f-mark); font-weight:400; bottom:-90px; }
.st-stage .s-compare .chip { font-family:var(--f-mark); font-weight:400; font-size:34px; }
.st-stage .s-compare .stk { font-family:var(--f-mark); font-weight:400; border-radius:999px; box-shadow:0 6px 0 #a80000, 0 0 30px rgba(255,45,45,.5); }
.st-stage .s-number .dots i { box-shadow:none; } .st-stage .s-number .dots i.hl { box-shadow:0 0 18px rgba(255,193,69,.9); }
.st-stage .s-number .val { text-shadow:0 0 50px rgba(255,193,69,.4); }
.st-stage .s-number .sub { font-family:var(--f-mark); color:var(--muted); letter-spacing:.06em; font-size:30px; }
.st-stage .s-outro .cta { color:#1b1446; font-family:var(--f-mark); font-weight:400; }
"""
