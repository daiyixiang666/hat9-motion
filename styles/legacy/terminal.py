"""terminal · 终端快剪 —— Fireship 的 100 秒密度 + 半佛仙人的梗图节奏。
深色代码面板、等宽字、标题栏三个圆点；橙色是强调、青色是注释；贴纸和标签 1–3 秒一换，硬切为主。
适合：AI 新闻速递、"100 秒讲清"、工具横评。
"""
STYLE = {
    "name": "终端快剪", "en": "Terminal Cut", "benchmarks": ["Fireship", "半佛仙人", "AI Explained", "毕导"],
    "tokens": {
        "bg": "#11111b", "fg": "#cdd6f4", "muted": "#7f849c", "accent": "#FF9F1C", "accent2": "#2EC4B6", "alert": "#f38ba8",
        "line": "#313244", "paper": "#11111b", "ink": "#0b0b12", "card": "#1e1e2e", "card-fg": "#cdd6f4",
        "display-weight": "800", "display-tracking": "0", "title-size": "112px", "stmt-size": "104px", "quote-size": "72px", "pad": "150px",
        "radius": "12px", "lab-bg": "#FF9F1C", "lab-fg": "#11111b", "lab-size": "30px", "lab-radius": "6px",
        "chip-bg": "#1e1e2e", "chip-fg": "#2EC4B6", "chip-radius": "8px", "dot-on": "#45475a", "dot-radius": "3px", "split-a": "#45475a",
        "num-fg": "#FF9F1C", "num-unit": "#cdd6f4", "veil": "linear-gradient(90deg, rgba(17,17,27,.95) 0%, rgba(17,17,27,.6) 60%, rgba(17,17,27,.3) 100%)",
        "cap-fg": "#cdd6f4", "cap-size": "40px", "cap-weight": "700", "cap-bg": "rgba(17,17,27,.85)", "cap-pad": "6px 18px", "cap-radius": "8px", "cap-shadow": "none", "cap-em": "#FF9F1C",
        "mark": "#2EC4B6", "mark-size": "28px", "mascot-bg": "#1e1e2e", "mascot-shadow": "0 0 0 3px #FF9F1C",
    },
    "fonts": {"display": ["jetbrains-mono", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "num": "jetbrains-mono", "mark": "jetbrains-mono"},
    "motion": {"ease": "expo.out", "dur": 0.3, "stagger": 0.012, "text": "type", "heading": "type", "media": "zoom",
               "accent": "pop", "quote": "type", "camera": "none", "transition": "glitch", "cut": "hard", "em": "box"},
    "layers": [("dots", {"color": "#1f1f2e", "step": 40, "opacity": 1}), ("scanlines", {"alpha": 0.08})],
    "title": {"layout": "card", "image": "none", "rule": False, "stagger": 0.02},
    "statement": {"layout": "left", "stagger": 0.02},
    "compare": {"variant": "windows", "camera": "none", "in_a": "zoom", "in_b": "zoom", "lab_verb": "pop"},
    "number": {"layout": "left", "viz": "bar"},
    "quote": {"layout": "lower"},
    "outro": {"layout": "right"},
    "mascot": {"mode": "corner", "frame": "circle", "landscape": {"left": 50, "bottom": 40, "h": 220}, "portrait": {"left": 50, "bottom": 300, "h": 250}},
    "mark_width": 5,
    "sfx": {"transition": ("glitch", 0.45), "title": ("type", 0.45), "line": ("type", 0.4), "enter": ("whoosh", 0.3), "pop": ("pop", 0.45),
            "hit": ("beep", 0.4), "count": ("type", 0.4), "mark": ("click", 0.5), "mascot": ("beep", 0.3)},
}

STYLE["css"] = """
.st-terminal .em .emb { left:-.1em; right:-.1em; top:.05em; bottom:0; background:var(--accent); border-radius:4px; }
.st-terminal .em .emt { color:#11111b; }
.st-terminal .s-title .L-card .panel { background:#1e1e2e; color:var(--fg); border-radius:14px; box-shadow:0 30px 80px rgba(0,0,0,.6), 0 0 0 1px #313244; padding:90px 70px 50px; align-items:flex-start; position:relative; }
.st-terminal .s-title .L-card .panel::before { content:'● ● ●'; position:absolute; left:24px; top:18px; color:#45475a; font-size:20px; letter-spacing:.2em; }
.st-terminal .s-title .kick { color:var(--accent2); text-transform:none; letter-spacing:0; font-size:30px; }
.st-terminal .s-title .kick::before { content:'$ '; color:var(--accent); }
.st-terminal .s-title .ttl { color:var(--fg); }
.st-terminal .s-title .sub { font-family:var(--f-mono); color:var(--muted); font-size:32px; }
.st-terminal .s-title .sub::before { content:'// '; color:var(--accent2); }
.st-terminal .s-statement .box::before { content:'// 结论'; font-family:var(--f-mono); color:var(--accent2); font-size:30px; margin-bottom:20px; }
.st-terminal .s-compare.v-windows .side { background:#1e1e2e; border-color:#313244; border-radius:12px; }
.st-terminal .s-compare .lab { font-family:var(--f-mono); font-weight:800; }
.st-terminal .s-compare .chip { font-family:var(--f-mono); font-weight:500; border:1px solid #313244; }
.st-terminal .s-compare .chip::before { content:'> '; color:var(--accent); }
.st-terminal .s-compare .stk { font-family:var(--f-body); border-radius:6px; }
.st-terminal .s-number .bar { border-radius:6px; height:44px; background:#1e1e2e; box-shadow:0 0 0 1px #313244; } .st-terminal .s-number .bar b { background:repeating-linear-gradient(90deg, var(--accent) 0 34px, transparent 34px 40px); }
.st-terminal .s-number .sub { color:var(--accent2); } .st-terminal .s-number .sub::before { content:'// '; }
.st-terminal .s-quote .q { color:var(--fg); }
.st-terminal .s-outro .cta { border-radius:8px; color:#11111b; font-family:var(--f-mono); }
.st-terminal .s-outro .cta::before { content:'$ '; }
"""
