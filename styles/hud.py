"""hud · 暗场 HUD —— 所长林超的编号栈 + 小Lin说的票据数字卡 + 回形针的引线标注。
近黑底、取景框四角、黄铜色胶囊（图标方块 + 粗中文 + 斜体英文小字）、奶黄大数字、细线 HUD 读数。
画面在同一个"控制台"里累加：旧元素压暗让位，新元素推入；背景不切。
适合：拆解、排序、"到底差在哪"、数字类判断。

这个风格的场景全部自己实现（SCENES），不使用共享模板。
"""
import math

STYLE = {
    "name": "暗场 HUD", "en": "Dark HUD", "benchmarks": ["所长林超", "小Lin说", "回形针PaperClip"],
    "tokens": {
        "bg": "#090b0e", "fg": "#f2efe6", "muted": "#7f8a8f", "accent": "#e9c46a", "accent2": "#d9b25a", "alert": "#e2574c",
        "line": "#1d2328", "paper": "#090b0e", "ink": "#000", "card": "#11161a", "card-fg": "#f2efe6",
        "cream": "#f6e7b0", "brass-a": "#d8b255", "brass-b": "#6e5420", "corner": "#4b5b5e", "glow": "rgba(233,196,106,.55)",
        "cap-fg": "#f2efe6", "cap-size": "40px", "cap-weight": "700", "cap-shadow": "0 2px 0 rgba(0,0,0,.9), 0 0 14px rgba(0,0,0,.8)", "cap-em": "#f6e7b0",
        "mascot-bg": "#11161a",
    },
    "fonts": {"display": ["inter", "noto-sans-sc"], "body": "noto-sans-sc", "mono": "jetbrains-mono", "num": "barlow-cond", "latin": "archivo"},
    "motion": {"ease": "expo.out", "dur": 0.5, "stagger": 0.03, "text": "rise", "heading": "rise", "media": "fade",
               "accent": "fade", "camera": "none", "transition": "dip", "cut": "hard", "em": "static"},
    "layers": [("grain", {"opacity": 0.06}), ("vignette", {"alpha": 0.6, "inner": 45})],
    "mascot": {"mode": "cameo", "frame": "none", "landscape": {"right": 70, "bottom": 40, "h": 300}, "portrait": {"right": 60, "bottom": 300, "h": 320}},
    "outro": {"move": False},
    "sfx": {"transition": ("whoosh_soft", 0.3), "title": ("hit", 0.35), "line": ("click", 0.45), "enter": ("whoosh_soft", 0.3), "pop": ("tick", 0.5),
            "hit": ("hit", 0.4), "count": ("type", 0.35), "mark": ("tick", 0.4), "mascot": ("whoosh_soft", 0.3), "hud": ("beep", 0.12)},
    # effect cards (aefx): four console modes, all on a dark field — standard · night-ops slate · brass · alert
    "fx_themes": {
        "ink":   {"bg": "#090b0e", "fg": "#f2efe6", "muted": "#8a9497", "accent": "#e9c46a", "card": "#12171b", "card-fg": "#f2efe6", "line": "#232a2f"},
        "paper": {"bg": "#0a141a", "fg": "#eef3f2", "muted": "#86999e", "accent": "#e9c46a", "card": "#10202a", "card-fg": "#eef3f2", "line": "#1f3440"},
        "lemon": {"bg": "#15110a", "fg": "#f6e7b0", "muted": "#a8946a", "accent": "#f3d98b", "card": "#221b0f", "card-fg": "#f6e7b0", "line": "#3a2f19"},
        "red":   {"bg": "#170909", "fg": "#f6e7d8", "muted": "#b58f86", "accent": "#ff6a55", "card": "#241110", "card-fg": "#f6e7d8", "line": "#3e1b18"},
    },
}

# ---------------------------------------------------------------- shared HUD furniture (this style only)
CSS = r"""
.st-hud { --cr: var(--corner); }
.st-hud .em .emb { display:none; } .st-hud .em .emt { color:var(--cream); }
/* viewfinder corners: four L brackets on every scene */
.hud-vf { position:absolute; inset:46px 54px; pointer-events:none; }
.hud-vf i { position:absolute; width:44px; height:44px; border:2px solid var(--cr); }
.hud-vf i:nth-child(1) { left:0; top:0; border-right:0; border-bottom:0; } .hud-vf i:nth-child(2) { right:0; top:0; border-left:0; border-bottom:0; }
.hud-vf i:nth-child(3) { left:0; bottom:0; border-right:0; border-top:0; } .hud-vf i:nth-child(4) { right:0; bottom:0; border-left:0; border-top:0; }
.hud-read { position:absolute; font-family:var(--f-mono); font-size:15px; letter-spacing:.16em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.hud-read b { color:var(--fg); font-weight:500; }
.hud-read.tl { left:118px; top:58px; } .hud-read.tr { right:118px; top:58px; text-align:right; }
/* the capsule (林超's stack item) */
.cps { position:relative; display:flex; align-items:center; gap:22px; height:118px; padding:0 40px 0 18px; border-radius:16px;
  background:linear-gradient(180deg, rgba(216,178,85,.30), rgba(110,84,32,.28)); border:1.5px solid rgba(233,196,106,.55);
  box-shadow:inset 0 1px 0 rgba(255,240,200,.25), 0 10px 30px rgba(0,0,0,.45); }
.cps .ico { width:78px; height:78px; border-radius:14px; background:rgba(242,239,230,.92); display:grid; place-items:center; flex:none; }
.cps .ico svg { width:46px; height:46px; stroke:#1b1d1f; fill:none; stroke-width:2.2; stroke-linecap:round; stroke-linejoin:round; }
.cps .tx { display:flex; flex-direction:column; align-items:center; flex:1; }
.cps .zh { font-family:var(--f-display); font-weight:900; font-size:56px; line-height:1; color:var(--fg); letter-spacing:.04em; text-shadow:0 2px 0 rgba(0,0,0,.35); }
.cps .en { font-family:var(--f-latin); font-style:italic; font-weight:700; font-size:19px; letter-spacing:.22em; color:rgba(246,231,176,.85); margin-top:8px; }
.cps.on { background:linear-gradient(180deg, rgba(232,196,98,.55), rgba(126,96,36,.5)); border-color:#f3d98b;
  box-shadow:inset 0 1px 0 rgba(255,244,210,.5), 0 0 0 2px rgba(243,217,139,.35), 0 0 46px var(--glow), 0 16px 40px rgba(0,0,0,.5); }
.cps .lit { position:absolute; inset:-2px; border-radius:17px; border:2px solid #f3d98b; pointer-events:none; opacity:0;
  background:linear-gradient(180deg, rgba(243,217,139,.22), rgba(243,217,139,0)); box-shadow:0 0 0 2px rgba(243,217,139,.3), 0 0 50px var(--glow), inset 0 1px 0 rgba(255,244,210,.6); }
.cps.on .lit { opacity:1; }
.cps .strike { position:absolute; left:120px; right:30px; top:50%; height:5px; margin-top:-2px; background:var(--alert); border-radius:3px; transform-origin:0 50%; }
.num { font-family:var(--f-num); font-weight:700; font-size:92px; line-height:1; color:#c9cdd0; width:90px; text-align:right; opacity:.85; }
/* media frame with a lit edge */
.mf { position:absolute; border-radius:22px; overflow:hidden; box-shadow:0 0 0 2px rgba(233,196,106,.5), 0 0 40px rgba(233,196,106,.22), 0 30px 80px rgba(0,0,0,.6); }
.mf img { width:100%; height:100%; object-fit:cover; display:block; }
.mf .tag { position:absolute; left:18px; top:16px; font-family:var(--f-mono); font-size:15px; letter-spacing:.18em; color:var(--fg); background:rgba(9,11,14,.7); padding:6px 12px; border-radius:6px; }
/* ticket card (小Lin's money frame): double rule border */
.ticket { position:absolute; background:linear-gradient(180deg, rgba(23,29,33,.92), rgba(13,17,20,.92)); border-radius:10px;
  box-shadow:0 30px 90px rgba(0,0,0,.6); }
.ticket::before, .ticket::after { content:''; position:absolute; border:1.5px solid rgba(233,196,106,.6); border-radius:6px; pointer-events:none; }
.ticket::before { inset:14px; } .ticket::after { inset:22px; border-color:rgba(233,196,106,.28); }
.pill { display:inline-block; font-family:var(--f-num); font-weight:700; font-size:30px; letter-spacing:.06em; color:#1a1408;
  background:linear-gradient(180deg, #f3d98b, #c99d3d); padding:4px 22px; border-radius:8px; box-shadow:0 4px 0 rgba(0,0,0,.35); }
.micro { font-family:var(--f-latin); font-style:italic; font-weight:600; letter-spacing:.24em; color:rgba(246,231,176,.75); font-size:18px; text-transform:uppercase; }
.title-zh { font-family:var(--f-display); font-weight:900; color:var(--fg); letter-spacing:.03em; line-height:1.04; }
.foot { position:absolute; left:118px; bottom:150px; font-size:20px; color:var(--muted); }
#root.v .hud-vf { inset:60px 40px; }
"""

ICONS = {
    "spark": '<path d="M24 4v10M24 34v10M4 24h10M34 24h10M10 10l7 7M31 31l7 7M38 10l-7 7M17 31l-7 7"/>',
    "chip": '<rect x="12" y="12" width="24" height="24" rx="3"/><path d="M18 6v6M24 6v6M30 6v6M18 36v6M24 36v6M30 36v6M6 18h6M6 24h6M6 30h6M36 18h6M36 24h6M36 30h6"/>',
    "wrench": '<path d="M30 8a9 9 0 0 0-9 12L8 33a3 3 0 0 0 4 4l13-13a9 9 0 0 0 12-9l-5 5-5-1-1-5z"/>',
    "eye": '<path d="M4 24s7-12 20-12 20 12 20 12-7 12-20 12S4 24 4 24z"/><circle cx="24" cy="24" r="6"/>',
    "image": '<rect x="6" y="9" width="36" height="30" rx="3"/><circle cx="17" cy="19" r="4"/><path d="M6 34l11-10 9 8 6-5 10 9"/>',
    "check": '<path d="M10 25l9 9 19-20"/>',
    "x": '<path d="M12 12l24 24M36 12L12 36"/>',
    "hat": '<path d="M14 30V12h20v18M6 34c6 3 30 3 36 0M14 30c3 2 17 2 20 0"/><path d="M14 24h20"/>',
}


def icon(k): return f'<svg viewBox="0 0 48 48">{ICONS[k]}</svg>'


def furniture(X, left="", right=""):
    X.css("hud", CSS)
    X.used_text.update(left + right)
    l = f'<div class="hud-read tl">{left}</div>' if left else ""      # trusted markup (readouts may hold a counter <b>)
    r = f'<div class="hud-read tr">{right}</div>' if right else ""
    return f'<div class="hud-vf"><i></i><i></i><i></i><i></i></div>{l}{r}'


def furn_in(X, cid, t):
    X.tw(f'tl.from("#{cid} .hud-vf i", {{scale:1.35, opacity:0, duration:0.45, ease:"expo.out", stagger:0.04}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .hud-read", {{opacity:0, duration:0.3, stagger:0.08}}, {t + 0.15:.3f});')


def counter(X, sel, t, a, b, dur=1.2, fmt="int"):
    js = "Math.round(o.v).toLocaleString('en-US')" if fmt == "int" else f"o.v.toFixed(0)"
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.to(o, {{v:{b}, duration:{dur}, ease:"power2.out", onUpdate:()=>{{el.textContent={js};}}}}, {t:.3f});}})();')


# ---------------------------------------------------------------- scenes
def title(b, X, t, d, cid):
    """hook: a wall of generated thumbnails floods the console, the headline lands on it."""
    r = X.rand
    cols, rows = 16, 9
    tiles = []
    pool = [X.asset(p) for p in b.get("wall", [])] or ([X.asset(b["image"])] if b.get("image") else [])
    for k in range(cols * rows):
        if pool and r.random() < 0.7:
            u = r.choice(pool)
            tiles.append(f'<i style="background:url({u}) {r.randint(0, 100)}% {r.randint(0, 100)}%/{r.randint(250, 520)}% auto; filter:hue-rotate({r.randint(-40, 40)}deg) saturate({r.uniform(.6, 1.2):.2f})"></i>')
        else:
            h1, h2 = r.randint(0, 360), r.randint(0, 360)
            tiles.append(f'<i style="background:linear-gradient({r.randint(0, 180)}deg, hsl({h1} 35% {r.randint(18, 36)}%), hsl({h2} 30% {r.randint(10, 26)}%))"></i>')
    wall = f'<div class="wall">{"".join(tiles)}</div>'
    img = f'<img class="wimg" src="{X.asset(b["image"])}" alt="">' if b.get("image") else ""
    X.css("hud-title", """
.s-hudtitle .wall { position:absolute; inset:-40px; display:grid; grid-template-columns:repeat(16, 1fr); grid-auto-rows:1fr; gap:10px; transform:rotate(-8deg) scale(1.25); opacity:.7; }
.s-hudtitle .wall i { display:block; border-radius:6px; aspect-ratio:16/10; box-shadow:inset 0 0 0 1px rgba(255,255,255,.06); }
.s-hudtitle .wimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.0; }
.s-hudtitle .shade { position:absolute; inset:0; background:radial-gradient(ellipse 46% 40% at 50% 50%, rgba(9,11,14,.95), rgba(9,11,14,.78) 55%, rgba(9,11,14,.9) 100%); }
.s-hudtitle .box { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px; }
.s-hudtitle .title-zh { font-size:150px; text-shadow:0 6px 40px rgba(0,0,0,.8); }
.s-hudtitle .title-zh .em .emt { color:var(--cream); }
.s-hudtitle .micro { font-size:24px; }
""")
    kick = f'<div class="pill">{X.rich(b.get("kicker_pill", "2026"))}</div>'
    inner = (wall + img + '<div class="shade"></div>' + furniture(X, b.get("hud_l", X.channel), "GENERATED <b class=\"gc\">0</b>")
             + f'<div class="box">{kick}<div class="title-zh">{X.rich(b["title"], split="chars")}</div><div class="micro">{X.rich(b.get("en", "everyone is using ai"))}</div></div>')
    X.clip(cid, t, d, inner, "scene s-hudtitle", 2)
    X.tw(f'tl.from("#{cid} .wall i", {{opacity:0, scale:0.4, duration:0.35, ease:"back.out(2)", stagger:{{each:0.004, from:"random"}}}}, {t:.3f});')
    X.tw(f'tl.fromTo("#{cid} .wall", {{yPercent:0}}, {{yPercent:-6, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.to("#{cid} .wall", {{opacity:0.35, duration:0.5, ease:"power2.out"}}, {t + 0.35:.3f});')
    furn_in(X, cid, t)
    X.enter(f"#{cid} .pill", t + 0.05, "accent", verb="pop", dur=0.4)
    X.enter(f"#{cid} .title-zh .c", t + 0.1, "heading", verb="blurin", stagger=0.035, dur=0.35)
    X.enter(f"#{cid} .micro", t + 0.35, "text", verb="fade")
    counter(X, f"#{cid} .gc", t, 1_200_000, 1_284_903_221, dur=max(1.0, d))
    X.sfx(t + 0.1, "title")


def compare(b, X, t, d, cid):
    """two monitors on the console; spec chips above, verdict capsules below."""
    L, R = b["left"], b["right"]
    X.css("hud-cmp", """
.s-hudcmp .mf { top:262px; width:690px; height:430px; }
.s-hudcmp .A { left:178px; } .s-hudcmp .B { right:178px; }
.s-hudcmp .spec { position:absolute; left:0; right:0; top:150px; display:flex; justify-content:center; gap:22px; }
.s-hudcmp .spec span { font-family:var(--f-mono); font-size:22px; letter-spacing:.12em; color:var(--fg); border:1.5px solid rgba(233,196,106,.45); border-radius:10px; padding:9px 18px; background:rgba(17,22,26,.8); }
.s-hudcmp .spec span b { color:var(--cream); font-weight:500; margin-right:10px; }
.s-hudcmp .eq { position:absolute; left:50%; top:452px; transform:translate(-50%,-50%); font-family:var(--f-num); font-size:84px; color:var(--muted); }
.s-hudcmp .lab { position:absolute; top:730px; width:690px; display:flex; justify-content:center; }
.s-hudcmp .lab.A { left:178px; } .s-hudcmp .lab.B { right:178px; }
.s-hudcmp .lab .cps { height:96px; min-width:430px; } .s-hudcmp .lab .cps .zh { font-size:46px; } .s-hudcmp .lab .ico { width:64px; height:64px; } .s-hudcmp .lab .ico svg { width:38px; height:38px; }
.s-hudcmp .warn { position:absolute; font-family:var(--f-display); font-weight:900; font-size:30px; color:#fff; background:var(--alert); padding:6px 14px; border-radius:6px; box-shadow:0 0 24px rgba(226,87,76,.55); }
.s-hudcmp .ring { position:absolute; inset:-10px; border-radius:28px; border:3px solid #f3d98b; box-shadow:0 0 50px var(--glow); opacity:0; }
.s-hudcmp .dim { position:absolute; inset:0; background:rgba(9,11,14,.7); opacity:0; }
""")
    warns = "".join(f'<div class="warn" style="{p}">{X.rich(w)}</div>' for w, p in zip(R.get("stickers", []), ["right:22px;top:24px", "left:24px;bottom:30px", "right:30px;bottom:96px"]))
    inner = (furniture(X, "SAME MODEL · SAME PROMPT", "A / B")
             + f'<div class="spec"><span><b>MODEL</b>同一个模型</span><span><b>PROMPT</b>同样的提示词</span></div>'
             + f'<div class="mf A"><img src="{X.asset(L["img"])}" alt=""><div class="tag">OUTPUT · A</div><div class="dim"></div></div>'
             + f'<div class="mf B"><img src="{X.asset(R["img"])}" alt=""><div class="tag">OUTPUT · B</div>{warns}<div class="dim"></div></div>'
             + '<div class="eq">=</div>'
             + f'<div class="lab A"><div class="cps">{"<div class=ico>" + icon("eye") + "</div>"}<div class="tx"><div class="zh">{X.rich(L["label"])}</div><div class="en">EDITORIAL</div></div><i class="lit"></i></div></div>'
             + f'<div class="lab B"><div class="cps">{"<div class=ico>" + icon("x") + "</div>"}<div class="tx"><div class="zh">{X.rich(R["label"])}</div><div class="en">CHEAP POSTER</div></div></div></div>')
    X.clip(cid, t, d, inner, "scene s-hudcmp", 2)
    furn_in(X, cid, t)
    X.tw(f'tl.from("#{cid} .spec span", {{y:-24, opacity:0, duration:0.4, ease:"expo.out", stagger:0.12}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .mf.A", {{x:-120, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .mf.B", {{x:120, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("#{cid} .eq", {{scale:0.4, opacity:0, duration:0.4, ease:"back.out(2)"}}, {t + 0.45:.3f});')
    X.sfx(t, "enter")
    ta, tb = X.T(b.get("at_left"), t) or t + 1, X.T(b.get("at_right"), t) or t + 2
    for k, tt in (("A", ta), ("B", tb)):
        X.enter(f"#{cid} .lab.{k} .cps", tt, "accent", verb="left", dur=0.45)
        X.sfx(tt, "line")
    X.tw(f'tl.to("#{cid} .eq", {{opacity:0, duration:0.3}}, {tb:.3f});')
    ts = X.T(b.get("at_stickers"), t) or tb + 0.6
    X.tw(f'tl.from("#{cid} .warn", {{scale:0, rotation:-12, duration:0.35, ease:"back.out(3)", stagger:0.12}}, {ts:.3f});')
    for i in range(len(R.get("stickers", []))): X.sfx(ts + i * 0.12, "pop")
    tv = X.T(b.get("at_verdict"), t)
    if tv:
        X.tw(f'tl.to("#{cid} .B .dim", {{opacity:1, duration:0.4}}, {tv:.3f});')
        X.tw(f'tl.to("#{cid} .lab.B .cps", {{filter:"saturate(.3) brightness(.5)", duration:0.4}}, {tv:.3f});')
        X.tw(f'tl.to("#{cid} .lab.A .cps .lit", {{opacity:1, duration:0.3}}, {tv:.3f});')
        X.tw(f'tl.fromTo("#{cid} .mf.A", {{scale:1}}, {{scale:1.05, duration:0.5, ease:"expo.out"}}, {tv:.3f});')
        X.sfx(tv, "hit")


def statement(b, X, t, d, cid):
    """the numbered stack: wrong answer gets struck and dimmed, the right one lights up and grows."""
    items = b.get("stack") or [{"zh": "工具", "en": "THE TOOL", "icon": "wrench", "off": True}, {"zh": "判断", "en": "YOUR JUDGMENT", "icon": "eye", "on": True}]
    at = b.get("at") or []
    X.css("hud-stack", """
.s-hudstack .stk { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%); display:grid; grid-template-columns:110px 640px; row-gap:44px; column-gap:34px; align-items:center; }
.s-hudstack .rail { position:absolute; left:142px; top:60px; bottom:60px; width:2px; background:linear-gradient(180deg, transparent, rgba(233,196,106,.6), transparent); transform-origin:50% 0; }
.s-hudstack .q { position:absolute; left:0; right:0; top:170px; text-align:center; }
.s-hudstack .q .title-zh { font-size:54px; font-weight:700; color:var(--muted); }
""")
    rows = "".join(f'<div class="num" data-k="{i}">{i + 1}</div><div class="cps" data-k="{i}"><div class="ico">{icon(it.get("icon", "spark"))}</div><div class="tx"><div class="zh">{X.rich(it["zh"])}</div><div class="en">{X.rich(it["en"])}</div></div>{"<i class=strike></i>" if it.get("off") else ""}<i class="lit"></i></div>' for i, it in enumerate(items))
    q = f'<div class="q"><div class="title-zh">{X.rich(b.get("q", "差别在哪？"))}</div></div>'
    X.clip(cid, t, d, furniture(X, "WHAT MAKES THE DIFFERENCE", "RANK") + q + f'<div class="stk"><i class="rail"></i>{rows}</div>', "scene s-hudstack", 2)
    furn_in(X, cid, t)
    X.enter(f"#{cid} .q", t, "text", verb="fade", dur=0.4)
    X.tw(f'tl.from("#{cid} .rail", {{scaleY:0, duration:0.6, ease:"power2.inOut"}}, {t:.3f});')
    for i, it in enumerate(items):
        ti = X.T(at[i], t) if i < len(at) else t + 0.2 + i * 0.6
        X.tw(f'tl.from("#{cid} .num[data-k=\'{i}\']", {{opacity:0, x:-20, duration:0.35}}, {max(t, ti - 0.1):.3f});')
        X.enter(f"#{cid} .cps[data-k=\'{i}\']", ti, "accent", verb="left", dur=0.45)
        X.sfx(ti, "line")
        if it.get("off"):
            ts = X.T(at[i + 1], t) if i + 1 < len(at) else ti + 0.8
            X.tw(f'tl.fromTo("#{cid} .cps[data-k=\'{i}\'] .strike", {{scaleX:0}}, {{scaleX:1, duration:0.3, ease:"power3.out"}}, {ts - 0.05:.3f});')
            X.tw(f'tl.to("#{cid} .cps[data-k=\'{i}\']", {{filter:"saturate(.25) brightness(.85)", scale:0.94, duration:0.4}}, {ts:.3f});')
        if it.get("on"):
            X.tw(f'tl.to("#{cid} .cps[data-k=\'{i}\'] .lit", {{opacity:1, duration:0.3}}, {ti + 0.35:.3f});')
            X.tw(f'tl.to("#{cid} .cps[data-k=\'{i}\']", {{scale:1.15, duration:0.5, ease:"back.out(1.6)"}}, {ti + 0.35:.3f});')
            X.sfx(ti + 0.35, "hit")


def number(b, X, t, d, cid):
    """ticket card: capsule tag, huge cream number, small unit, footnote; beside it a 10×10 matrix."""
    v = int(b["value"]); hl = int(b.get("hl", 0))
    X.css("hud-num", """
.s-hudnum .ticket { left:160px; top:220px; width:760px; height:560px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; }
.s-hudnum .lbl { font-family:var(--f-display); font-weight:700; font-size:34px; color:var(--fg); letter-spacing:.12em; }
.s-hudnum .big { font-family:var(--f-num); font-weight:700; font-size:300px; line-height:.9; color:var(--cream); text-shadow:0 0 40px rgba(246,231,176,.25); font-variant-numeric:tabular-nums; }
.s-hudnum .big small { font-size:110px; margin-left:6px; }
.s-hudnum .sub { font-family:var(--f-display); font-weight:700; font-size:40px; color:var(--fg); }
.s-hudnum .sub .em .emt { color:var(--cream); }
.s-hudnum .mx { position:absolute; right:190px; top:250px; display:grid; grid-template-columns:repeat(10, 38px); gap:12px; }
.s-hudnum .mx i { width:38px; height:38px; border-radius:7px; background:#1a2025; box-shadow:inset 0 0 0 1px rgba(255,255,255,.05); }
.s-hudnum .mx i.on { background:#39434a; } .s-hudnum .mx i.hl { background:linear-gradient(180deg, #f3d98b, #c99d3d); box-shadow:0 0 18px var(--glow); }
.s-hudnum .mxl { position:absolute; right:190px; top:760px; width:500px; display:flex; justify-content:space-between; font-family:var(--f-mono); font-size:17px; letter-spacing:.14em; color:var(--muted); }
.s-hudnum .mxl b { color:var(--cream); font-weight:500; }
""")
    cells = "".join(f'<i class="{"on" if i < v else ("hl" if i < v + hl else "")}"></i>' for i in range(100))
    la, lb = b.get("split_labels", ["", ""])
    inner = (furniture(X, "SURVEY · 示意", "N = 100")
             + f'<div class="ticket"><div class="pill">{X.rich(b.get("sub", "大多数人"))}</div><div class="big"><span class="n">0</span><small>{X.rich(b.get("unit", "%"))}</small></div>'
             + f'<div class="sub">{X.rich(b["label"])}</div><div class="micro">{X.rich(b.get("en", "just generate more, then pick one"))}</div></div>'
             + f'<div class="mx">{cells}</div><div class="mxl"><span>■ {X.rich(la)}</span><span><b>■ {X.rich(lb)}</b></span></div>'
             + f'<div class="foot">{X.rich(b.get("foot", "注：示意数据，用来说明比例"))}</div>')
    X.used_text.update("0123456789%")
    X.clip(cid, t, d, inner, "scene s-hudnum", 2)
    furn_in(X, cid, t)
    ta = X.T(b.get("at"), t) or t + 0.2
    X.tw(f'tl.from("#{cid} .ticket", {{y:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.enter(f"#{cid} .pill", t + 0.25, "accent", verb="pop", dur=0.35)
    counter(X, f"#{cid} .n", ta, 0, v, dur=1.3)
    X.sfx(ta, "count")
    X.enter(f"#{cid} .sub", ta + 0.4, "text", verb="rise")
    X.enter(f"#{cid} .micro", ta + 0.6, "text", verb="fade")
    X.tw(f'tl.from("#{cid} .mx i", {{opacity:0, scale:0.3, duration:0.25, ease:"back.out(2)", stagger:{{each:0.006, grid:[10,10], from:"start"}}}}, {ta:.3f});')
    th = X.T(b.get("at_hl"), t) or ta + 1.3
    X.tw(f'tl.fromTo("#{cid} .mx i.hl", {{filter:"brightness(.12) saturate(0)"}}, {{filter:"brightness(1) saturate(1)", duration:0.35, ease:"power2.out", stagger:0.05, immediateRender:true}}, {th:.3f});')
    X.tw(f'tl.fromTo("#{cid} .mx i.hl", {{scale:1}}, {{scale:1.35, duration:0.18, ease:"power2.out", yoyo:true, repeat:1, stagger:0.05, immediateRender:false}}, {th:.3f});')
    X.tw(f'tl.from("#{cid} .mxl", {{opacity:0, duration:0.4}}, {th:.3f});')
    X.sfx(th, "pop")
    X.enter(f"#{cid} .foot", t + 0.8, "text", verb="fade")


def quote(b, X, t, d, cid):
    """media frame on the left, the judgment line on the right with a cream key phrase."""
    X.css("hud-q", """
.s-hudq .mf { left:150px; top:190px; width:780px; height:560px; }
.s-hudq .box { position:absolute; left:1010px; right:150px; top:0; bottom:0; display:flex; flex-direction:column; justify-content:center; gap:26px; }
.s-hudq .title-zh { font-size:84px; }
.s-hudq .title-zh .em .emt { color:var(--cream); }
.s-hudq .box .pill { align-self:flex-start; }
.s-hudq .rule { width:120px; height:4px; background:linear-gradient(90deg, #f3d98b, transparent); transform-origin:0 50%; }
""")
    img = f'<div class="mf"><img class="cam" src="{X.asset(b["image"])}" alt=""><div class="tag">SELECT · REJECT</div></div>' if b.get("image") else ""
    inner = furniture(X, "THE JUDGMENT", "∎") + img + f'<div class="box"><div class="pill">{X.rich(b.get("kicker_pill", "结论"))}</div><div class="title-zh">{X.rich(b["text"], split="chars")}</div><i class="rule"></i><div class="micro">{X.rich(b.get("en", "knowing which one to throw away"))}</div></div>'
    X.clip(cid, t, d, inner, "scene s-hudq", 2)
    furn_in(X, cid, t)
    X.tw(f'tl.from("#{cid} .mf", {{x:-80, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.camera(f"#{cid} .mf img", t, d, "push")
    X.enter(f"#{cid} .pill", t + 0.15, "accent", verb="pop", dur=0.35)
    n = len(str(b["text"]).replace("*", "").replace("|", ""))
    X.enter(f"#{cid} .title-zh .c", t + 0.25, "heading", verb="blurin", stagger=min(0.04, 1.2 / n), dur=0.35)
    X.enter(f"#{cid} .rule", t + 0.25 + n * min(0.04, 1.2 / n), "text", verb="wipe", dur=0.5)
    X.enter(f"#{cid} .micro", t + 0.4 + n * min(0.04, 1.2 / n), "text", verb="fade")
    X.sfx(t + 0.25, "line")


def outro(b, X, t, d, cid):
    """the host's badge: a ring of ticks around the host, name + positioning line + one CTA capsule."""
    X.css("hud-out", """
.s-hudout .badge { position:absolute; left:260px; top:50%; width:520px; height:520px; margin-top:-260px; }
.s-hudout .badge svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.s-hudout .badge .tk { stroke:rgba(233,196,106,.65); stroke-width:3; }
.s-hudout .badge .rg { fill:none; stroke:rgba(233,196,106,.35); stroke-width:2; }
.s-hudout .box { position:absolute; left:870px; right:150px; top:0; bottom:0; display:flex; flex-direction:column; justify-content:center; gap:24px; }
.s-hudout .title-zh { font-size:120px; }
.s-hudout .sub { font-size:38px; color:var(--muted); font-weight:500; }
.s-hudout .cps { align-self:flex-start; height:96px; } .s-hudout .cps .zh { font-size:40px; } .s-hudout .cps .ico { width:62px; height:62px; } .s-hudout .cps .ico svg { width:36px; height:36px; }
""")
    ticks = "".join(f'<line class="tk" x1="{260 + 250 * math.cos(a):.1f}" y1="{260 + 250 * math.sin(a):.1f}" x2="{260 + (232 if k % 5 else 222) * math.cos(a):.1f}" y2="{260 + (232 if k % 5 else 222) * math.sin(a):.1f}"/>'
                    for k in range(60) for a in [2 * math.pi * k / 60])
    badge = f'<div class="badge"><svg viewBox="0 0 520 520"><circle class="rg" cx="260" cy="260" r="206"/><g class="tks">{ticks}</g></svg></div>'
    inner = (furniture(X, "HOST · " + X.channel, "FOLLOW") + badge
             + f'<div class="box"><div class="micro">ON AIR</div><div class="title-zh">{X.rich(b.get("title", X.channel), split="chars")}</div><div class="sub">{X.rich(b.get("sub", ""))}</div>'
             + f'<div class="cps on"><div class="ico">{icon("hat")}</div><div class="tx"><div class="zh">{X.rich(b.get("cta", "关注"))}</div><div class="en">TRAIN YOUR JUDGMENT</div></div><i class="lit"></i></div></div>')
    X.clip(cid, t, d, inner, "scene s-hudout", 2)
    furn_in(X, cid, t)
    X.tw(f'tl.from("#{cid} .badge .tk", {{opacity:0, duration:0.02, stagger:0.008}}, {t:.3f});')
    X.tw(f'tl.fromTo("#{cid} .badge .tks", {{rotation:-30, transformOrigin:"260px 260px"}}, {{rotation:0, duration:1.2, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .badge .rg", {{scale:0.6, opacity:0, transformOrigin:"260px 260px", duration:0.7, ease:"expo.out"}}, {t:.3f});')
    X.enter(f"#{cid} .micro", t + 0.2, "text", verb="fade")
    X.enter(f"#{cid} .title-zh .c", t + 0.3, "heading", verb="blurin", stagger=0.05, dur=0.4)
    X.enter(f"#{cid} .sub", t + 0.7, "text", verb="rise")
    X.enter(f"#{cid} .cps", t + 0.95, "accent", verb="left", dur=0.45)
    X.sfx(t + 0.3, "title")
    if X.v.get("meta", {}).get("mascot"):   # the host stands inside the badge
        X.css("hud-out-m", f".mascot#mascot {{ left:{260 + 40}px !important; right:auto !important; bottom:{(1080 - 520) // 2 + 40}px !important; width:440px !important; height:440px !important; }}")


SCENES = {"title": title, "compare": compare, "statement": statement, "number": number, "quote": quote, "outro": outro}
STYLE["css"] = "#root.v.st-hud .fx .rk .rk-v { margin-right:48px; }   /* 9:16: ranking values clear of the right-hand buttons */\n"


# ---------------------------------------------------------------- effect cards (aefx FX_FRAME)
# Every gallery effect in this style is framed as one console readout: brass viewfinder corners, a numbered capsule
# (card index · topic · effect id in italic caps), a REC timecode that ticks, side tick rulers, a slow scan line,
# the spoken line on a notched ticket with a double brass rule, and a tick-mark ruler carrying label and source.
# The effect gets a crosshair grid + vignette ground; nodes, ranking slabs and cards inside effects turn into brass-ruled
# console pieces. Injected only here (the hud scenes keep their own CSS).
HF_CSS = r"""
.st-hud .fx[style*="background:var(--bg)"]::before { content:''; position:absolute; inset:0; z-index:-1; pointer-events:none; background:
  radial-gradient(ellipse 78% 72% at 50% 46%, transparent 52%, rgba(0,0,0,.55)),
  url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120'><path d='M60 53v14M53 60h14' stroke='%23f2efe6' stroke-opacity='.16' stroke-width='1.4'/></svg>") 0 0/120px 120px,
  linear-gradient(color-mix(in srgb, var(--fg) 3.5%, transparent) 1px, transparent 1px) 0 0/120px 120px,
  linear-gradient(90deg, color-mix(in srgb, var(--fg) 3.5%, transparent) 1px, transparent 1px) 0 0/120px 120px; }
.hf { pointer-events:none; }
.hf .hf-vf { position:absolute; left:36px; right:36px; top:30px; bottom:30px; }
.hf .hf-vf i { position:absolute; width:52px; height:52px; border:2.5px solid var(--accent); opacity:.85; }
.hf .hf-vf i:nth-child(1) { left:0; top:0; border-right:0; border-bottom:0; transform-origin:0 0; } .hf .hf-vf i:nth-child(2) { right:0; top:0; border-left:0; border-bottom:0; transform-origin:100% 0; }
.hf .hf-vf i:nth-child(3) { left:0; bottom:0; border-right:0; border-top:0; transform-origin:0 100%; } .hf .hf-vf i:nth-child(4) { right:0; bottom:0; border-left:0; border-top:0; transform-origin:100% 100%; }
.hf .hf-cps { position:absolute; left:74px; top:40px; display:flex; align-items:center; gap:14px; height:56px; padding:0 22px 0 8px; border-radius:14px;
  background:linear-gradient(180deg, rgba(216,178,85,.32), rgba(110,84,32,.30)); border:1.5px solid rgba(233,196,106,.6);
  box-shadow:inset 0 1px 0 rgba(255,240,200,.25), 0 10px 30px rgba(0,0,0,.45); }
.hf .hf-no { width:42px; height:42px; border-radius:10px; background:rgba(242,239,230,.94); color:#15110a; display:grid; place-items:center;
  font-family:var(--f-num); font-weight:700; font-size:32px; line-height:1; letter-spacing:.02em; }
.hf .hf-tx { display:flex; flex-direction:column; gap:3px; }
.hf .hf-tx b { font-family:var(--f-display); font-weight:900; font-size:22px; line-height:1; color:#f2efe6; letter-spacing:.06em; white-space:nowrap; }
.hf .hf-tx em { font-family:var(--f-latin); font-style:italic; font-weight:700; font-size:13px; letter-spacing:.24em; color:rgba(246,231,176,.85); text-transform:uppercase; white-space:nowrap; }
.hf .hf-rd { position:absolute; right:74px; top:44px; text-align:right; font-family:var(--f-mono); font-size:15px; line-height:1.6; letter-spacing:.16em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.hf .hf-rd { color:color-mix(in srgb, var(--fg) 62%, transparent); } .hf .hf-rd b { color:var(--fg); font-weight:500; } .hf .hf-rd .rec { display:inline-block; width:9px; height:9px; border-radius:50%; background:#e2574c; margin-right:8px; box-shadow:0 0 10px rgba(226,87,76,.8); }
.hf .hf-tk { position:absolute; top:50%; width:12px; height:220px; margin-top:-110px; opacity:.55;
  background:repeating-linear-gradient(180deg, var(--muted) 0 1px, transparent 1px 22px) 0 0/12px 100% no-repeat, linear-gradient(var(--muted), var(--muted)) 0 0/1px 100% no-repeat; }
.hf .hf-tk.l { left:44px; } .hf .hf-tk.r { right:44px; transform:scaleX(-1); }
.hf .hf-scan { position:absolute; left:36px; right:36px; top:0; height:2px; opacity:.2;
  background:linear-gradient(90deg, transparent, var(--accent) 18%, var(--accent) 82%, transparent); box-shadow:0 0 14px var(--accent); }
.hf .hf-cap { position:absolute; left:0; right:0; bottom:72px; display:flex; justify-content:center; }
.hf .hf-tkt { position:relative; max-width:calc(80% + 110px); padding:16px 44px 18px; border-radius:6px; text-align:center;
  background:linear-gradient(180deg, rgba(24,29,33,.95), rgba(12,15,18,.95)); box-shadow:0 24px 60px rgba(0,0,0,.55);
  -webkit-mask:radial-gradient(circle 11px at 0 50%, transparent 97%, #000) left/51% 100% no-repeat, radial-gradient(circle 11px at 100% 50%, transparent 97%, #000) right/51% 100% no-repeat;
  mask:radial-gradient(circle 11px at 0 50%, transparent 97%, #000) left/51% 100% no-repeat, radial-gradient(circle 11px at 100% 50%, transparent 97%, #000) right/51% 100% no-repeat; }
.hf .hf-tkt::before, .hf .hf-tkt::after { content:''; position:absolute; border-radius:4px; pointer-events:none; }
.hf .hf-tkt::before { inset:6px; border:1.5px solid color-mix(in srgb, var(--accent) 72%, transparent); }
.hf .hf-tkt::after { inset:11px; border:1px solid color-mix(in srgb, var(--accent) 30%, transparent); }
.hf .hf-line { position:relative; font-family:var(--f-body); font-weight:700; line-height:1.3; color:#f2efe6; letter-spacing:.02em; text-shadow:0 2px 0 rgba(0,0,0,.6); white-space:nowrap; }
.hf .hf-line .em .emt { background:linear-gradient(180deg, #f3d98b, #c99d3d); color:#1a1408; text-shadow:none; padding:0 .22em; border-radius:4px;
  box-shadow:0 3px 0 rgba(0,0,0,.4); box-decoration-break:clone; -webkit-box-decoration-break:clone; }
.hf .hf-line .em .emb { display:none; }
.hf .hf-ft { position:absolute; left:74px; right:74px; bottom:28px; height:40px; }
.hf .hf-ft .hf-rule { position:absolute; left:0; right:0; bottom:0; height:12px; opacity:.7; background:
  repeating-linear-gradient(90deg, var(--muted) 0 1px, transparent 1px 24px) left bottom/100% 6px no-repeat,
  repeating-linear-gradient(90deg, var(--muted) 0 2px, transparent 2px 120px) left bottom/100% 12px no-repeat,
  linear-gradient(var(--muted), var(--muted)) left bottom/100% 1px no-repeat; }
.hf .hf-ft .hf-fr { position:absolute; left:0; right:0; bottom:18px; display:flex; justify-content:space-between; gap:30px;
  font-family:var(--f-mono); font-size:14px; letter-spacing:.1em; color:var(--muted); white-space:nowrap; }
.hf .hf-ft .hf-fr > span { overflow:hidden; text-overflow:ellipsis; min-width:0; }
.hf .hf-ft .hf-fr > span:first-child::before { content:'▸ '; color:var(--accent); }
#root.v .hf .hf-vf { left:28px; right:28px; top:186px; bottom:392px; }
#root.v .hf .hf-cps { left:58px; top:202px; height:42px; gap:10px; padding:0 16px 0 6px; border-radius:11px; }
#root.v .hf .hf-no { width:31px; height:31px; border-radius:8px; font-size:22px; }
#root.v .hf .hf-tx { flex-direction:row; align-items:baseline; gap:10px; } #root.v .hf .hf-tx b { font-size:18px; } #root.v .hf .hf-tx em { font-size:11px; }
#root.v .hf .hf-rd { right:58px; top:200px; font-size:14px; line-height:1.5; }
#root.v .hf .hf-tk { top:700px; } #root.v .hf .hf-tk.l { left:36px; } #root.v .hf .hf-tk.r { right:36px; }
#root.v .hf .hf-scan { left:28px; right:28px; }
#root.v .hf .hf-cap { bottom:458px; padding:0 120px; } #root.v .hf .hf-tkt { max-width:100%; padding:16px 22px 18px; }
#root.v .hf .hf-ft { left:58px; right:130px; bottom:auto; top:1470px; height:46px; }
/* effect internals */
.st-hud .fx .rk .rk-in { background:linear-gradient(180deg, rgba(24,30,34,.94), rgba(13,17,20,.94)); box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--accent) 34%, transparent); border-radius:10px; }
.st-hud .fx .rk .rk-r.top .rk-in { background:linear-gradient(180deg, #ebc866, #a8802f); box-shadow:inset 0 1px 0 rgba(255,244,210,.6), 0 0 0 2px rgba(243,217,139,.35), 0 0 46px rgba(233,196,106,.45); }
.st-hud .fx .rk .rk-r.top .rk-no, .st-hud .fx .rk .rk-r.top .rk-nm, .st-hud .fx .rk .rk-r.top .rk-v, .st-hud .fx .rk .rk-r.top .rk-sb { color:#15110a; }
.st-hud .fx .wpe-n, .st-hud .rg-n { background:linear-gradient(180deg, rgba(26,33,38,.96), rgba(14,18,22,.96)); color:var(--fg); border-radius:8px;
  box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--accent) 45%, transparent), 0 16px 40px rgba(0,0,0,.45); }
.st-hud .fx .wpe-n.person { border-radius:99vmin; }
.st-hud .fx .wpe-n.root { background:linear-gradient(180deg, #ebc866, #a8802f); color:#15110a; box-shadow:inset 0 1px 0 rgba(255,244,210,.6), 0 0 40px rgba(233,196,106,.35); }
.st-hud .rg-n em { color:color-mix(in srgb, var(--fg) 55%, transparent); }
.st-hud .fx .dtr .dtr-b { border-radius:0 3px 3px 0; box-shadow:inset 0 1px 0 rgba(255,255,255,.22); }
.st-hud .fx .nf .nf-band, .st-hud .fx .nf .nf-tk { border-radius:3px; }
"""


def FX_FRAME(X, cid, t, d, p, k):
    X.css("hud-fx", HF_CSS)
    P = X.portrait
    i, n = X.beat["i"] + 1, X.beat["n"]
    host = bool(p.get("host"))
    rd_pos = ' style="right:330px"' if (host and P) else ""                     # 9:16: the presenter sits top-right
    ft_pad = ' style="padding-right:330px"' if (host and not P) else ""         # 16:9: the presenter sits bottom-right
    X.used_text.update(f"{i:02d}{X.channel} · CH09RECT+0123456789.▸ ")
    inner = ('<div class="hf-vf"><i></i><i></i><i></i><i></i></div><i class="hf-tk l"></i><i class="hf-tk r"></i><i class="hf-scan"></i>'
             f'<div class="hf-cps"><span class="hf-no">{i:02d}</span><span class="hf-tx"><b>{k["topic"]}</b><em>{k["fxid"]}</em></span></div>'
             f'<div class="hf-rd"{rd_pos}>{X.rich(X.channel)} · <b>CH09</b><br><i class="rec"></i>REC <b class="hf-tc">T+00.0</b></div>'
             f'<div class="hf-cap"><div class="hf-tkt"><div class="hf-line" style="font-size:{k["cap_px"]}px">{k["cap"]}</div></div></div>'
             f'<div class="hf-ft"><div class="hf-fr"{ft_pad}><span>{k["foot"]}</span><span>{k["src"]}</span></div><i class="hf-rule"></i></div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx hf{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .hf-vf i", {{scale:1.45, opacity:0, duration:0.4, ease:"expo.out", stagger:0.04}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hf-cps", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.04:.3f});')
    X.tw(f'tl.from("{s} .hf-rd, {s} .hf-tk, {s} .hf-ft", {{opacity:0, duration:0.3, stagger:0.05}}, {t + 0.08:.3f});')
    X.tw(f'tl.fromTo("{s} .hf-tkt", {{scaleY:0.15, opacity:0}}, {{scaleY:1, opacity:1, duration:0.32, ease:"expo.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .hf-line", {{y:12, opacity:0, duration:0.3, ease:"power3.out"}}, {t + 0.16:.3f});')
    y0, y1 = (250, 1440) if P else (96, X.H - 150)
    X.tw(f'tl.fromTo("{s} .hf-scan", {{y:{y0}}}, {{y:{y1}, duration:{d:.2f}, ease:"none", immediateRender:true}}, {t:.3f});')
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .hf-tc"); tl.to(o, {{v:{d:.2f}, duration:{d:.2f}, ease:"none", '
         f'onUpdate:()=>{{el.textContent="T+"+o.v.toFixed(1).padStart(4,"0");}}}}, {t:.3f});}})();')
    blinks = max(0, int((d - 0.2) / 0.5))
    if blinks:
        X.tw(f'tl.to("{s} .rec", {{opacity:0.15, duration:0.01, repeat:{blinks}, yoyo:true, repeatDelay:0.49, ease:"none"}}, {t + 0.2:.3f});')
