"""keynote · 发布会 —— Apple 发布会陈述卡 + Vercel Ship / Linear 产品片。
纯黑、只有主体带色；巨大的紧排标题、渐变强调字；面板悬浮在透视空间，底下一团光。剪辑隐形：推进穿越。
适合：AI 工具和产品、"新东西来了"、年度盘点。
"""
STYLE = {
    "name": "发布会", "en": "Keynote", "benchmarks": ["Apple keynote", "Vercel Ship", "Linear", "何同学", "影视飓风"],
    "tokens": {
        "bg": "#000000", "fg": "#f5f5f7", "muted": "#86868b", "accent": "#a78bfa", "accent2": "rgba(124,92,255,.32)", "alert": "#ff453a",
        "line": "#1d1d1f", "paper": "#000", "ink": "#000", "card": "#0c0c0e", "card-fg": "#f5f5f7",
        "display-weight": "700", "display-tracking": "-0.035em", "title-size": "190px", "stmt-size": "150px", "quote-size": "92px", "pad": "160px",
        "radius": "22px", "lab-bg": "transparent", "lab-fg": "#86868b", "lab-size": "30px", "chip-bg": "#1d1d1f", "chip-fg": "#f5f5f7",
        "dot-on": "#2c2c2e", "num-fg": "#f5f5f7", "num-unit": "#86868b", "num-size": "340px", "num-weight": "700", "split-a": "#2c2c2e",
        "veil": "linear-gradient(180deg, rgba(0,0,0,.5), rgba(0,0,0,.85))", "float-border": "rgba(255,255,255,.12)",
        "cap-fg": "#f5f5f7", "cap-size": "38px", "cap-weight": "500", "cap-shadow": "0 0 14px rgba(0,0,0,.9)", "cap-em": "#c4b5fd",
        "mark": "#a78bfa", "mascot-glow": "rgba(167,139,250,.55)",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "num": "inter"},
    "motion": {"ease": "expo.out", "dur": 0.85, "stagger": 0.025, "text": "rise", "heading": "blurin", "media": "zoom",
               "accent": "fade", "quote": "blurin", "camera": "pull", "transition": "dip", "cut": "zoom", "em": "static"},
    "layers": [("glow", {})],
    "title": {"layout": "center", "image": "none", "rule": False, "stagger": 0.04},
    "statement": {"layout": "center"},
    "compare": {"variant": "float", "camera": "none", "in_a": "zoom", "in_b": "zoom", "lab_verb": "fade"},
    "number": {"layout": "center", "viz": "bar"},
    "quote": {"layout": "center", "camera": "pull"},
    "outro": {"layout": "right"},
    "mascot": {"mode": "cameo", "frame": "glow", "landscape": {"left": 50, "bottom": 0, "h": 300}, "portrait": {"left": 50, "bottom": 280, "h": 320}},
    "sfx": {"transition": ("whoosh_deep", 0.3), "title": ("boom", 0.3), "line": None, "enter": ("whoosh_soft", 0.25), "pop": None,
            "hit": ("hit", 0.3), "count": ("tick", 0.2), "mark": ("tick", 0.25), "cut": ("whoosh_soft", 0.15), "mascot": ("whoosh_soft", 0.2)},
}

STYLE["css"] = """
.st-keynote .em .emb { display:none; }
.st-keynote .em .emt { background:linear-gradient(95deg, #ff8a4c 0%, #ff4d8d 45%, #8b5cff 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.st-keynote .s-title .kick { letter-spacing:.06em; text-transform:none; font-family:var(--f-body); font-size:30px; font-weight:600; color:var(--muted); }
.st-keynote .s-title .sub { color:var(--muted); font-weight:600; }
.st-keynote .s-compare.v-float .ph { border-radius:22px; box-shadow:0 60px 140px rgba(124,92,255,.25), 0 0 0 1px rgba(255,255,255,.1); }
.st-keynote .s-compare .lab { left:50%; transform:translateX(-50%); font-weight:600; letter-spacing:0; font-family:var(--f-body); }
.st-keynote .s-compare .chip { font-weight:600; font-size:26px; }
.st-keynote .s-compare .stk { border-radius:999px; box-shadow:none; font-size:28px; }
.st-keynote .s-number .val { background:linear-gradient(180deg, #fff 30%, #8e8e93 100%); -webkit-background-clip:text; background-clip:text; color:transparent; }
.st-keynote .s-number .val small { -webkit-text-fill-color:#86868b; }
.st-keynote .s-number .bar { height:10px; border-radius:5px; width:900px; background:#1d1d1f; } .st-keynote .s-number .bar b { background:linear-gradient(90deg, #ff8a4c, #ff4d8d, #8b5cff); border-radius:5px; }
.st-keynote .s-number .sub { font-family:var(--f-body); font-weight:600; letter-spacing:0; font-size:28px; }
.st-keynote .s-outro .cta { background:#f5f5f7; color:#000; font-weight:600; }
"""
