"""editorial · 社论版 —— Vox 解说 + The Economist / FT 图表编辑部。
纸白底、粗黑体标题 + 宋体引文 + 等宽标签；社论红是唯一的强调，黄色只做马克笔底块。纸纹每秒抖 3 次（Vox 的手作感）。
适合：观点、趋势、"大家都在说 X，其实……"。
"""
STYLE = {
    "name": "社论版", "en": "Editorial", "benchmarks": ["Vox", "The Economist", "Financial Times", "秋芝2046", "漫士沉思录"],
    "tokens": {
        "bg": "#F3EDE2", "fg": "#141414", "muted": "#6b655c", "accent": "#E3120B", "accent2": "#FFE600", "alert": "#E3120B",
        "line": "#d8cfbf", "paper": "#F3EDE2", "ink": "#141414", "card": "#fffdf8", "card-fg": "#141414", "hl": "rgba(255,230,0,.85)",
        "display-weight": "900", "display-tracking": "-0.01em", "title-size": "112px", "stmt-size": "112px", "quote-size": "78px",
        "pad": "150px", "radius": "0", "lab-bg": "#141414", "lab-fg": "#ffffff", "lab-size": "34px",
        "chip-bg": "#141414", "chip-fg": "#F3EDE2", "chip-radius": "0", "dot-on": "#b9b0a2", "split-a": "#b9b0a2",
        "veil": "linear-gradient(0deg, rgba(243,237,226,.0), rgba(243,237,226,0))",
        "cap-fg": "#ffffff", "cap-bg": "#141414", "cap-pad": "4px 16px", "cap-shadow": "none", "cap-size": "40px", "cap-weight": "600", "cap-em": "#FFE600",
        "mark": "#E3120B", "mark-size": "30px", "num-fg": "#141414", "num-unit": "#E3120B",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "quote": "noto-serif-sc", "mono": "jetbrains-mono", "num": "inter", "mark": "noto-sans-sc"},
    "motion": {"ease": "power3.out", "dur": 0.5, "stagger": 0.02, "text": "rise", "heading": "lift", "media": "wipe",
               "accent": "pop", "quote": "lift", "camera": "push", "transition": "paper", "cut": "hard", "em": "marker"},
    "layers": [("paper", {"jitter": 3, "alpha": 0.16, "tint": "0.42 0.34 0.22"}), ("grain", {"opacity": 0.05, "blend": "multiply"}),
               ("folio", {"right": "观点 · 2026"})],
    "title": {"layout": "left", "image": "frame", "rule": True},
    "statement": {"layout": "left"},
    "compare": {"variant": "cards", "tilt": 0, "camera": "none", "in_a": "wipe", "in_b": "wipe"},
    "number": {"layout": "left", "viz": "split"},
    "quote": {"layout": "center"},
    "outro": {"layout": "right"},
    "mascot": {"mode": "cameo", "landscape": {"left": 40, "bottom": 0, "h": 300}, "portrait": {"left": 40, "bottom": 280, "h": 320}},
    "sfx": {"transition": ("paper", 0.5), "title": ("tick", 0.4), "line": ("click", 0.35), "enter": ("paper", 0.35), "pop": ("pop", 0.35),
            "hit": ("hit", 0.35), "count": ("type", 0.3), "mark": ("brush", 0.6), "mascot": ("pop", 0.35)},
}

STYLE["css"] = """
.st-editorial .em .emb { left:-.08em; right:-.08em; top:.42em; bottom:.02em; background:var(--hl); mix-blend-mode:multiply; }
.st-editorial .s-quote .q { font-family:var(--f-quote); font-weight:600; background:#fffdf8; padding:34px 52px 40px; box-shadow:0 20px 50px rgba(0,0,0,.35); display:inline-block; }
.st-editorial .s-title.img-frame .box { right:44%; } .st-editorial .s-title .ttl { white-space:nowrap; }
.st-editorial .s-quote .q .em .emt { color:var(--fg); }
/* title: heavy left headline, photo on the right as a framed print with a mono caption */
.st-editorial .s-title.img-frame .frame { border:12px solid #fffdf8; box-shadow:0 18px 40px rgba(60,40,10,.25); right:120px; width:44%; }
.st-editorial .s-title .kick { color:var(--accent); font-weight:700; letter-spacing:.18em; }
.st-editorial .s-title .rule { background:var(--fg); height:6px; width:160px; }
.st-editorial .s-title .sub { font-family:var(--f-quote); color:var(--fg); font-weight:500; }
/* compare: two prints on the page, black caption bars */
.st-editorial .s-compare.v-cards .side { border:12px solid #fffdf8; box-shadow:0 18px 40px rgba(60,40,10,.22); }
.st-editorial .s-compare .lab { font-family:var(--f-body); font-weight:800; letter-spacing:.04em; bottom:-92px; }
.st-editorial .s-compare .chip { font-family:var(--f-mono); font-size:24px; letter-spacing:.12em; font-weight:500; }
.st-editorial .s-compare .stk { font-family:var(--f-body); border-radius:0; box-shadow:none; }
/* chart: Economist red bar on top + conclusion title */
.st-editorial .s-number .box::before { content:''; position:absolute; left:150px; top:150px; width:90px; height:14px; background:var(--accent); }
.st-editorial .s-number .val { font-weight:900; }
.st-editorial .s-number .sub { color:var(--muted); font-size:22px; }
.st-editorial .s-number .split .tags .b { color:var(--accent); }
.st-editorial .s-number .seg.b { background:var(--accent); }
.ov-folio { top:44px; bottom:auto; left:60px; right:60px; height:30px; display:flex; align-items:center; gap:18px; font-family:var(--f-mono); font-size:18px; color:var(--muted); letter-spacing:.18em; pointer-events:none; }
.ov-folio .fr-rule { flex:1; height:2px; background:var(--fg); }
"""
