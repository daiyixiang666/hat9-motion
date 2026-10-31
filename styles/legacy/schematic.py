"""schematic · 图解推导 —— 回形针PaperClip 的系统性 + 3Blue1Brown 的"每个动作都有目的"。
炭黑底、细线框 + 角标、引线标注、【】标题、等宽小标签；橙色是唯一的强调，元素逐步累积而不跳换。
适合：原理、流程、技术拆解。
"""
STYLE = {
    "name": "图解推导",
    "en": "Schematic",
    "benchmarks": ["回形针PaperClip", "3Blue1Brown", "飞天闪客", "Ele实验室"],
    "tokens": {
        "bg": "#17181a", "fg": "#f1efe9", "muted": "#8d8f93", "accent": "#ff8a1e", "accent2": "#f5c242", "alert": "#e5484d",
        "line": "#2b2d31", "paper": "#17181a", "ink": "#0c0c0d", "card": "#1c1e21", "card-fg": "#f1efe9",
        "veil": "linear-gradient(90deg, rgba(23,24,26,.92) 0%, rgba(23,24,26,.55) 60%, rgba(23,24,26,.25) 100%)",
        "display-weight": "800", "display-tracking": "0.01em", "title-size": "150px", "stmt-size": "118px", "quote-size": "84px",
        "radius": "2px", "pad": "150px", "lab-bg": "#17181a", "lab-size": "30px", "lab-radius": "0",
        "chip-bg": "transparent", "chip-fg": "#f1efe9", "chip-radius": "0", "dot-radius": "2px", "dot-on": "#55575c",
        "cap-size": "42px", "cap-weight": "500", "cap-em": "#ff8a1e",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "num": "inter"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.025, "text": "rise", "heading": "rise", "media": "unveil",
               "accent": "fade", "quote": "type", "camera": "drift", "transition": "dip", "em": "underline"},
    "layers": [("grid", {"step": 60, "color": "#212327", "opacity": 0.9}), ("grain", {"opacity": 0.06}),
               ("folio", {"right": "VOL.01 · 判断力"})],
    "title": {"layout": "bracket", "image": "frame", "rule": False},
    "statement": {"layout": "left"},
    "compare": {"variant": "windows", "in_a": "unveil", "in_b": "unveil", "camera": "none"},
    "number": {"layout": "left", "viz": "dots"},
    "quote": {"layout": "lower"},
    "outro": {"layout": "right"},
    "mascot": {"mode": "cameo", "landscape": {"left": 40, "bottom": 20, "h": 300}, "portrait": {"left": 40, "bottom": 300, "h": 320}},
    "sfx": {"transition": ("whoosh_soft", 0.35), "title": ("tick", 0.5), "line": ("click", 0.45), "enter": ("whoosh_soft", 0.3),
            "pop": ("tick", 0.45), "hit": ("hit", 0.45), "count": ("type", 0.35), "mascot": ("pop", 0.4)},
}

CSS = """
.st-schematic .em .emb { left:0; right:0; bottom:.02em; height:.09em; background:var(--accent); }
.st-schematic .em .emt { color:var(--accent); }
/* title: image in a hairline frame with corner ticks + a leader label */
.st-schematic .s-title .frame { border:1px solid #4a4c51; padding:14px; overflow:visible; background:#141517; }
.st-schematic .s-title .frame img { position:absolute; inset:14px; width:calc(100% - 28px); height:calc(100% - 28px); }
.st-schematic .s-title .frame::before, .st-schematic .s-title .frame::after { content:''; position:absolute; width:26px; height:26px; border:2px solid var(--accent); }
.st-schematic .s-title .frame::before { left:-8px; top:-8px; border-right:0; border-bottom:0; }
.st-schematic .s-title .frame::after { right:-8px; bottom:-8px; border-left:0; border-top:0; }
.st-schematic .s-title.img-frame .box { align-items:flex-start; text-align:left; }
.st-schematic .s-title .kick { color:var(--accent); letter-spacing:.2em; }
.st-schematic .s-title .ttl { font-size:118px; }
.st-schematic .s-title .sub { font-size:36px; }
/* compare windows */
.st-schematic .s-compare.v-windows .side { background:#141517; border-color:#3a3c41; }
.st-schematic .s-compare .lab { font-family:var(--f-mono); font-weight:500; border-left:3px solid var(--accent); padding:6px 18px; }
.st-schematic .s-compare .chip { font-family:var(--f-mono); font-weight:500; font-size:26px; border:1px solid #4a4c51; letter-spacing:.08em; }
.st-schematic .s-compare .stk { font-size:30px; border-radius:4px; box-shadow:none; }
/* number */
.st-schematic .s-number .val { color:var(--fg); font-weight:300; }
.st-schematic .s-number .val small { color:var(--accent); }
.st-schematic .s-number .sub { color:var(--accent); }
/* statement + quote */
.st-schematic .s-statement .ln { font-weight:800; }
.st-schematic .s-quote .q { font-weight:600; }
/* folio */
.ov-folio { top:44px; bottom:auto; left:60px; right:60px; height:30px; display:flex; align-items:center; gap:18px; font-family:var(--f-mono); font-size:18px; color:var(--muted); letter-spacing:.18em; pointer-events:none; }
.ov-folio .fr-rule { flex:1; height:1px; background:#34363b; }
.st-schematic .cap .cp { font-family:var(--f-body); }
"""
STYLE["css"] = CSS
