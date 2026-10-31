"""signal · 红色数据 —— PolyMatter 的整屏品牌红 + Wendover / Economist 的图表规矩。
整屏一个红，白色窄体大字层层堆叠；图表标题就是结论，只突出一个系列，其余是半透明白。
适合：数字、收入、市场规模、对比。
"""
STYLE = {
    "name": "红色数据", "en": "Signal Red", "benchmarks": ["PolyMatter", "Wendover Productions", "The Economist charts", "地球知识局", "小Lin说"],
    "tokens": {
        "bg": "#B5121B", "fg": "#ffffff", "muted": "#f2b8bb", "accent": "#FFD23F", "accent2": "#FFD23F", "alert": "#FFD23F",
        "line": "#c93a42", "paper": "#B5121B", "ink": "#3a0306", "card": "#ffffff", "card-fg": "#B5121B",
        "display-weight": "900", "display-tracking": "0.01em", "title-size": "170px", "stmt-size": "140px", "quote-size": "92px", "pad": "150px",
        "lab-bg": "#ffffff", "lab-fg": "#B5121B", "lab-size": "40px", "chip-bg": "#ffffff", "chip-fg": "#B5121B", "chip-radius": "0",
        "dot-on": "rgba(255,255,255,.4)", "dot-radius": "0", "split-a": "rgba(255,255,255,.45)", "num-fg": "#ffffff", "num-unit": "#FFD23F", "num-size": "320px",
        "veil": "linear-gradient(90deg, rgba(181,18,27,.92) 0%, rgba(181,18,27,.7) 50%, rgba(181,18,27,.25) 100%)",
        "cap-fg": "#ffffff", "cap-size": "42px", "cap-weight": "800", "cap-shadow": "0 2px 0 rgba(0,0,0,.45)", "cap-em": "#FFD23F",
        "mark": "#FFD23F", "mascot-bg": "#ffffff",
    },
    "fonts": {"display": ["barlow-cond-black", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "ibm-plex-mono", "num": "barlow-cond-black"},
    "motion": {"ease": "expo.out", "dur": 0.45, "stagger": 0.015, "text": "rise", "heading": "lift", "media": "wipe",
               "accent": "pop", "quote": "lift", "camera": "push", "transition": "wipe", "cut": "slide", "em": "static"},
    "layers": [("grain", {"opacity": 0.05})],
    "title": {"layout": "left", "image": "full", "rule": True},
    "statement": {"layout": "left"},
    "compare": {"variant": "halves", "camera": "push", "lab_verb": "wipe"},
    "number": {"layout": "left", "viz": "split"},
    "quote": {"layout": "center"},
    "outro": {"layout": "right"},
    "mascot": {"mode": "cameo", "frame": "circle", "landscape": {"left": 50, "bottom": 40, "h": 230}, "portrait": {"left": 50, "bottom": 300, "h": 260}},
    "sfx": {"transition": ("whoosh", 0.4), "title": ("hit", 0.4), "line": ("click", 0.4), "enter": ("whoosh", 0.3), "pop": ("pop", 0.4),
            "hit": ("hit", 0.45), "count": ("type", 0.35), "mark": ("tick", 0.4), "cut": ("whoosh_soft", 0.3), "mascot": ("pop", 0.35)},
}

STYLE["css"] = """
.st-signal .em .emb { display:none; } .st-signal .em .emt { color:var(--accent); }
.st-signal .s-title .ttl, .st-signal .s-statement .ln, .st-signal .s-number .val { text-transform:uppercase; }
.st-signal .s-title .kick { font-family:var(--f-mono); color:#fff; background:rgba(0,0,0,.25); padding:6px 14px; letter-spacing:.2em; font-weight:500; }
.st-signal .s-title .sub { color:#fff; font-weight:700; }
.st-signal .s-title .rule { background:var(--accent); height:10px; width:200px; }
.st-signal .s-compare .lab { font-family:var(--f-display); letter-spacing:.06em; top:120px; }
.st-signal .s-compare .chip { font-family:var(--f-mono); font-weight:500; letter-spacing:.1em; font-size:26px; }
.st-signal .s-compare .stk { border-radius:0; box-shadow:4px 4px 0 rgba(0,0,0,.35); background:#FFD23F; color:#111; }
.st-signal .s-compare.v-halves .A { border-right:8px solid var(--bg); }
.st-signal .s-number .lbl { font-weight:900; }
.st-signal .s-number .sub { color:#fff; font-family:var(--f-mono); background:rgba(0,0,0,.22); padding:6px 14px; align-self:flex-start; }
.st-signal .s-number .split .tags { font-family:var(--f-display); font-size:46px; }
.st-signal .s-number .split .tags .a { color:rgba(255,255,255,.75); }
.st-signal .s-outro .cta { background:#fff; color:var(--bg); border-radius:0; }
"""
