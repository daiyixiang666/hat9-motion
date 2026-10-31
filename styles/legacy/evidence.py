"""evidence · 证据桌 —— Johnny Harris 的桌面档案 + NYT Visual Investigations。
台灯下的深色桌面，纸片、相片带胶带，唯一的红笔圈画；柴犬在一台老电视里讲话。停格感的切换、手持镜头。
适合：案例拆解、"这个爆款是怎么被做出来的"、调查类口播。
"""
STYLE = {
    "name": "证据桌", "en": "Evidence Desk", "benchmarks": ["Johnny Harris", "NYT Visual Investigations", "Vox Atlas", "智能路障"],
    "tokens": {
        "bg": "#1a1410", "fg": "#f1e7d3", "muted": "#a8977c", "accent": "#D1281F", "accent2": "#e9b949", "alert": "#D1281F",
        "line": "#3b3027", "paper": "#ECE2CC", "ink": "#1d1814", "card": "#ECE2CC", "card-fg": "#1d1814",
        "display-weight": "900", "title-size": "120px", "stmt-size": "96px", "quote-size": "70px", "pad": "160px", "radius": "0",
        "lab-bg": "transparent", "lab-fg": "#D1281F", "lab-size": "46px", "chip-bg": "#ECE2CC", "chip-fg": "#1d1814", "chip-radius": "0",
        "dot-on": "#6e5f4c", "split-a": "#8d7c64", "veil": "radial-gradient(ellipse at 60% 40%, rgba(26,20,16,.1), rgba(26,20,16,.75))",
        "cap-fg": "#f6eedd", "cap-size": "42px", "cap-weight": "700", "cap-em": "#ff5a4e",
        "mark": "#D1281F", "mark-size": "34px", "tape": "rgba(232,220,180,.8)", "tv-screen": "#22302c", "tv-bezel": "#3a322a",
        "num-fg": "#1d1814", "num-unit": "#D1281F", "mascot-w": "330px",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "special-elite", "num": "inter", "mark": "long-cang", "quote": "noto-serif-sc"},
    "motion": {"ease": "power3.out", "dur": 0.45, "stagger": 0.02, "text": "rise", "heading": "lift", "media": "jitter",
               "accent": "pop", "quote": "lift", "camera": "handheld", "transition": "burn", "cut": "step", "em": "underline"},
    "layers": [("bgcolor", {"css": "radial-gradient(ellipse 70% 60% at 55% 35%, #3a2c20 0%, #1f1813 55%, #120e0b 100%)"}),
               ("grain", {"opacity": 0.12}), ("vignette", {"alpha": 0.55, "inner": 45})],
    "title": {"layout": "card", "image": "frame", "rule": False},
    "statement": {"layout": "center"},
    "compare": {"variant": "cards", "tilt": 4, "tape": True, "camera": "none", "in_a": "jitter", "in_b": "jitter", "lab_verb": "fade"},
    "number": {"layout": "left", "viz": "dots"},
    "quote": {"layout": "lower", "camera": "handheld"},
    "outro": {"layout": "right", "mascot": {"x": 520, "y": -300, "scale": 1.6}},
    "mascot": {"mode": "corner", "frame": "tv", "landscape": {"left": 50, "bottom": 40, "h": 270}, "portrait": {"left": 50, "bottom": 300, "h": 300}},
    "mark_width": 7,
    "sfx": {"transition": ("whoosh_soft", 0.4), "title": ("type", 0.45), "line": ("type", 0.4), "enter": ("paper", 0.5), "pop": ("tape", 0.35),
            "hit": ("shutter", 0.5), "count": ("type", 0.35), "mark": ("brush", 0.7), "cut": ("paper", 0.35), "mascot": ("shutter", 0.4)},
}

STYLE["css"] = """
/* everything content-ish sits on paper: clippings on the desk */
.st-evidence .s-title .L-card .panel { background:var(--paper); color:var(--ink); padding:40px 60px 46px; transform:rotate(-1.5deg); box-shadow:0 22px 40px rgba(0,0,0,.55); align-items:flex-start; }
.st-evidence .s-title .kick { font-family:var(--f-mono); color:#7a6a55; letter-spacing:.12em; text-transform:none; }
.st-evidence .s-title .ttl { color:var(--ink); font-size:104px; }
.st-evidence .s-title .sub { color:#5a4d3e; font-family:var(--f-quote); }
.st-evidence .s-title.img-frame .frame { border:16px solid #f4efe4; border-bottom-width:56px; transform:translateY(-50%) rotate(3deg); box-shadow:0 24px 50px rgba(0,0,0,.6); right:150px; width:40%; }
.st-evidence .s-title.img-frame .box { right:44%; }
.st-evidence .s-compare.v-cards .side { border:16px solid #f4efe4; border-bottom-width:60px; box-shadow:0 26px 50px rgba(0,0,0,.6); }
.st-evidence .s-compare .lab { font-family:var(--f-mark); font-weight:400; bottom:-64px; font-size:52px; }
.st-evidence .s-compare .chip { font-family:var(--f-mono); font-weight:400; transform:translateX(-50%) rotate(-1deg); box-shadow:0 10px 20px rgba(0,0,0,.4); padding:12px 30px; }
.st-evidence .s-compare .stk { border-radius:2px; font-size:34px; box-shadow:2px 3px 0 rgba(0,0,0,.4); }
.st-evidence .s-statement .ln { background:var(--paper); color:var(--ink); padding:10px 34px 14px; box-shadow:0 14px 26px rgba(0,0,0,.5); display:inline-block; }
.st-evidence .s-statement .mask { overflow:visible; }
.st-evidence .s-statement .mask:nth-of-type(2) .ln { transform:rotate(-1.4deg); margin-top:18px; }
.st-evidence .s-statement .mask:nth-of-type(1) .ln { transform:rotate(1deg); }
.st-evidence .em .emb { left:-.05em; right:-.05em; bottom:-.06em; height:.1em; background:var(--mark); border-radius:4px; }
.st-evidence .s-number .txt { background:var(--paper); color:var(--ink); padding:40px 56px; box-shadow:0 20px 40px rgba(0,0,0,.55); transform:rotate(-1deg); }
.st-evidence .s-number .lbl { color:var(--ink); font-size:46px; max-width:640px; }
.st-evidence .s-number .sub { font-family:var(--f-mono); color:#7a6a55; }
.st-evidence .s-number .dots i { background:#3b3027; } .st-evidence .s-number .dots i.on { background:#8d7c64; }
.st-evidence .s-quote .q { color:var(--ink); }
.st-evidence .s-quote .q { background:var(--paper); padding:22px 40px 28px; box-shadow:0 18px 36px rgba(0,0,0,.55); display:inline-block; transform:rotate(-1deg); }
.st-evidence .s-quote .L-lower { align-items:flex-start; }
.st-evidence .s-outro .ttl { font-family:var(--f-display); }
.st-evidence .s-outro .cta { background:var(--accent); color:#fff; border-radius:0; font-family:var(--f-mono); font-weight:400; }
"""
