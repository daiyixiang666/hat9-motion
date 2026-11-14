"""hud · 暗场 HUD —— a dark analytical instrument panel for 拆解 / 排序 / "到底差在哪".

Ground #0a0b0d with a 60 px grid of #14161a hairlines and a radial lift to #15171c at the centre. Panels #111317 with a
1 px #2a2d33 border and a 1 px #3a3e46 inner top highlight. One warm accent: brass #e8b85a for lines and text, bright
#ffd98a for the single live element of a beat, alert #ff5a4d for the negative figure only; neutral text #f1ede4, muted
#8f949c. Chinese display in HarmonyOS Sans Black, numerals in Barlow Condensed with tabular figures, micro-labels in
JetBrains Mono caps (22–24 px, .18em tracking).

Furniture that never leaves (one clip for the whole film): four viewfinder brackets (9:16 at x 60/1020, y 200/1520,
48 px arms, 3 px, brass 60 %), a 2 px scan line sweeping the bracketed area every 4 s, a tick ruler scrolling along the
bottom edge. Per beat: a status row (beat index · film title · a live readout), the headline block (kicker + one line,
one word in bright brass), the instrument (the chart object, 920 px wide in 9:16), a readout strip of three mono
key-value cells that tick, the source line, and a 5 % beat numeral below the safe area.

Instruments (scene names): ticket (hero number on a double-rule ticket, digits roll per column, delta chip) · stack
(numbered capsules, width in true ratio, the live one lights) · gauge (270° arc, needle sweeps with a 4 % overshoot) ·
diff (two columns compared row by row under a stepping cursor bar) · scope (oscilloscope trace on a 10×8 graticule) ·
matrix (10×10 cells light in reading order in the true count) · summary (three ticket stubs, the brackets close in).
Verbs: roll, tick, sweep, step, lock-on (a reticle snaps onto the live element with a 2-frame overshoot).
Seams alternate: a 6-frame shutter of 12 slats, and the brackets contracting to the centre and re-opening (8 frames).
No host. The older scenes (title, compare, statement, number, quote, outro) are kept for existing films.
"""
import math

BG, GRIDC, LIFT = "#0a0b0d", "#14161a", "#15171c"
PANEL, EDGE, HILITE = "#111317", "#2a2d33", "#3a3e46"
BRASS, LIVE, ALERT = "#e8b85a", "#ffd98a", "#ff5a4d"
FG, MUTED = "#f1ede4", "#8f949c"
F = 1 / 30

STYLE = {
    "name": "暗场 HUD", "en": "Dark HUD", "benchmarks": ["所长林超", "小Lin说", "示波器 / 仪表盘读数"],
    "tokens": {
        "bg": BG, "fg": FG, "muted": MUTED, "accent": BRASS, "accent2": LIVE, "alert": ALERT,
        "line": EDGE, "paper": BG, "ink": "#000", "card": PANEL, "card-fg": FG,
        "cream": LIVE, "brass-a": "#d8a94e", "brass-b": "#6a4f1c", "corner": "rgba(232,184,90,.6)", "glow": "rgba(232,184,90,.45)",
        # subtitle: a panel plate with a 3 px brass bar on the left (x 100–960, y 1384–1460 in 9:16)
        "cap-bg": "rgba(17,19,23,.92)", "cap-fg": FG, "cap-size": "44px", "cap-weight": "700", "cap-pad": "10px 26px 12px 26px",
        "cap-radius": "0", "cap-shadow": "none", "cap-em": LIVE, "cap-bottom": "460px",
        "mascot-bg": PANEL,
    },
    "fonts": {"display": ["harmonyos-sans-black", "noto-sans-sc"], "body": "noto-sans-sc", "cap": "noto-sans-sc",
              "mono": ["jetbrains-mono", "noto-sans-sc"], "num": ["barlow-cond", "noto-sans-sc"], "latin": "archivo"},
    "motion": {"ease": "expo.out", "dur": 0.4, "stagger": 0.03, "text": "rise", "heading": "rise", "media": "fade",
               "accent": "pop", "camera": "none", "transition": "hard", "cut": "hard", "em": "static"},
    "layers": [("grain", {"opacity": 0.06})],
    "caption_plate": False,
    "mascot": {"mode": "none"},
    "outro": {"move": False},
    "safe_exempt": [".hx-ghost", ".hx-ruler", ".hud-read"],     # the 5 % beat numeral and the tick ruler are furniture
    "sfx": {"transition": ("whoosh_soft", 0.25), "title": ("hit", 0.35), "line": ("click", 0.4), "enter": ("whoosh_soft", 0.25), "pop": ("tick", 0.45),
            "hit": ("hit", 0.35), "count": ("type", 0.3), "mark": ("tick", 0.4), "mascot": None, "hud": ("beep", 0.12),
            "lock": ("tick", 0.5), "step": ("click", 0.3), "shutter": ("whoosh_soft", 0.25)},
    # effect pages (aefx): four console modes, all on a dark field — standard · night slate · brass · alert
    "fx_themes": {
        "ink":   {"bg": BG, "fg": FG, "muted": MUTED, "accent": BRASS, "card": PANEL, "card-fg": FG, "line": EDGE},
        "paper": {"bg": "#0b1013", "fg": "#eef1f0", "muted": "#8e9aa0", "accent": BRASS, "card": "#111a1f", "card-fg": "#eef1f0", "line": "#24323a"},
        "lemon": {"bg": "#14110a", "fg": "#f6e7c0", "muted": "#a8946a", "accent": LIVE, "card": "#1e1a10", "card-fg": "#f6e7c0", "line": "#3a2f19"},
        "red":   {"bg": "#160b0b", "fg": "#f6e7de", "muted": "#b39089", "accent": ALERT, "card": "#221211", "card-fg": "#f6e7de", "line": "#3e1d1a"},
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




# ================================================================ the instrument panel (0.19 rebuild)
def L(X):
    """fixed architecture per aspect (px). box = the instrument (x, y, w, h)."""
    if X.portrait:
        return {"br": (60, 200, 1020, 1520), "status": (100, 214, 880), "kick": (100, 290), "h1": (100, 326, 880, 92),
                "box": (80, 500, 920, 800), "ro": (100, 1310, 860), "src": (100, 1474, 860),
                "ghost": (52, 1528, 700), "ruler": 1858, "scan": (206, 1514), "lede": None, "carrier": (0, 1650, 1080, 90)}
    return {"br": (40, 36, 1880, 1044), "status": (100, 52, 1720), "kick": (100, 150), "h1": (100, 190, 700, 88),
            "box": (860, 128, 980, 762), "ro": (860, 904, 980), "src": (100, 948, 700),
            "ghost": (88, 300, 560), "ruler": 1052, "scan": (44, 1036), "lede": (100, 420, 660), "carrier": (860, 962, 980, 74)}


HX_CSS = r"""
.st-hud .mascot { display:none !important; }
.hx-bg { position:absolute; inset:0; background:
  linear-gradient(__GRID__ 1px, transparent 1px) 0 0/60px 60px,
  linear-gradient(90deg, __GRID__ 1px, transparent 1px) 0 0/60px 60px,
  radial-gradient(ellipse 72% 58% at 50% 50%, __LIFT__, __BG__ 78%), __BG__; }
.hx-ov { position:absolute; inset:0; pointer-events:none; }
.hx-ov .br { position:absolute; width:48px; height:48px; border:3px solid rgba(232,184,90,.6); }
.hx-ov .b0 { border-right:0; border-bottom:0; } .hx-ov .b1 { border-left:0; border-bottom:0; }
.hx-ov .b2 { border-right:0; border-top:0; } .hx-ov .b3 { border-left:0; border-top:0; }
.hx-ov .scan { position:absolute; height:2px; background:rgba(232,184,90,.25); }
.hx-ov .scan::after { content:''; position:absolute; left:0; right:0; bottom:2px; height:48px; background:linear-gradient(0deg, rgba(232,184,90,.22), rgba(232,184,90,.07) 60%, rgba(232,184,90,0)); }
.hx-ruler { position:absolute; left:0; height:40px; opacity:.85; background:
  repeating-linear-gradient(90deg, rgba(143,148,156,.55) 0 2px, transparent 2px 24px) left bottom/100% 14px no-repeat,
  repeating-linear-gradient(90deg, rgba(232,184,90,.7) 0 3px, transparent 3px 120px) left bottom/100% 34px no-repeat,
  linear-gradient(rgba(143,148,156,.5), rgba(143,148,156,.5)) left bottom/100% 1px no-repeat; }
.hx { position:absolute; inset:0; color:__FG__; }
.hx * { box-sizing:border-box; }
.hx .mono { font-family:var(--f-mono); text-transform:uppercase; letter-spacing:.18em; }
.hx .st { position:absolute; height:40px; display:flex; align-items:center; justify-content:space-between; }
.hx .st .ix { font-family:var(--f-mono); font-size:24px; letter-spacing:.18em; color:__BRASS__; white-space:nowrap; }
.hx .st .ttl { position:absolute; left:50%; transform:translateX(-50%); font-family:var(--f-body); font-weight:700; font-size:28px; color:__FG__; white-space:nowrap; letter-spacing:.04em; }
.hx .st .lv { font-family:var(--f-mono); font-size:24px; letter-spacing:.14em; color:__LIVE__; white-space:nowrap; display:flex; align-items:center; gap:12px; }
.hx .st .lv i { width:12px; height:12px; background:__LIVE__; display:inline-block; }
.hx .kick { position:absolute; font-family:var(--f-mono); font-size:24px; letter-spacing:.18em; color:__BRASS__; white-space:nowrap; text-transform:uppercase; }
.hx .h1 { position:absolute; font-family:var(--f-display); font-weight:900; color:__FG__; line-height:1.08; letter-spacing:.02em; }
.hx .h1 .ln { display:block; overflow:hidden; padding-bottom:.06em; }
.hx .h1 .em .emt { color:__LIVE__; } .hx .h1 .em .emb { display:none; }
.hx .lede { position:absolute; font-family:var(--f-body); font-weight:500; font-size:30px; line-height:1.6; color:__MUTED__; }
.hx .box { position:absolute; }
.hx .ro { position:absolute; height:50px; display:flex; gap:10px; }
.hx .ro > div { flex:1; display:flex; align-items:center; justify-content:space-between; padding:0 16px; background:__PANEL__; border:1px solid __EDGE__;
  box-shadow:inset 0 1px 0 __HILITE__; font-family:var(--f-mono); font-size:28px; letter-spacing:.06em; white-space:nowrap; overflow:hidden; }
.hx .ro .k { color:__MUTED__; } .hx .ro b { color:__FG__; font-weight:600; letter-spacing:.06em; }
.hx .src { position:absolute; height:32px; font-family:var(--f-body); font-size:22px; line-height:32px; color:__MUTED__; white-space:nowrap; overflow:hidden; }
.hx .hx-ghost { position:absolute; font-family:var(--f-num); font-weight:700; line-height:1; color:#17181b; letter-spacing:-.02em; white-space:nowrap; }
.hx .pn { position:absolute; background:__PANEL__; border:1px solid __EDGE__; box-shadow:inset 0 1px 0 __HILITE__; }
/* the lock-on reticle */
.hx .rt { position:absolute; left:0; top:0; width:0; height:0; opacity:0; pointer-events:none; z-index:20; }
.hx .rt i { position:absolute; left:0; top:0; width:30px; height:30px; border:3px solid __LIVE__; }
.hx .rt i:nth-child(1) { border-right:0; border-bottom:0; } .hx .rt i:nth-child(2) { border-left:0; border-bottom:0; }
.hx .rt i:nth-child(3) { border-right:0; border-top:0; } .hx .rt i:nth-child(4) { border-left:0; border-top:0; }
/* rolling digits */
.hx .roll { font-family:var(--f-num); font-weight:700; line-height:1; white-space:nowrap; font-variant-numeric:tabular-nums; display:flex; align-items:flex-start; }
.hx .roll .dc { display:inline-block; height:1em; overflow:hidden; }
.hx .roll .ds { display:block; }
.hx .roll .ds b { display:block; height:1em; font-weight:700; }
.hx .roll .dd { display:inline-block; height:1em; }
/* ticket */
.hx .tk { position:absolute; background:linear-gradient(180deg, #14161b, __PANEL__); border:1px solid __EDGE__; box-shadow:inset 0 1px 0 __HILITE__; }
.hx .tk .r1, .hx .tk .r2 { position:absolute; pointer-events:none; }
.hx .tk .r1 { inset:12px; border:2px solid rgba(232,184,90,.62); } .hx .tk .r2 { inset:20px; border:1px solid rgba(232,184,90,.28); }
.hx .tk .hole { position:absolute; border-radius:50%; background:__BG__; }
.hx .tk .punch { position:absolute; border-radius:50%; background:__BG__; box-shadow:inset 0 0 0 1px __EDGE__; }
.hx .tk .stub { position:absolute; left:0; top:0; bottom:0; display:flex; flex-direction:column; align-items:center; justify-content:space-between; padding:46px 0; }
.hx .tk .stub .sv { writing-mode:vertical-rl; font-family:var(--f-mono); font-size:24px; letter-spacing:.3em; color:__BRASS__; white-space:nowrap; }
.hx .tk .stub .sn { font-family:var(--f-num); font-size:44px; color:__MUTED__; }
.hx .tk .lab { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.12em; color:__BRASS__; white-space:nowrap; }
.hx .tk .was { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.08em; color:__MUTED__; white-space:nowrap; }
.hx .chip { position:absolute; height:64px; padding:0 22px; display:flex; align-items:center; font-family:var(--f-num); font-weight:700; font-size:46px; white-space:nowrap;
  border:2px solid currentColor; background:rgba(10,11,13,.6); letter-spacing:.02em; }
.hx .chip.alert { color:__ALERT__; } .hx .chip.brass { color:__LIVE__; font-family:var(--f-body); font-size:36px; }
.hx .rail { position:absolute; left:0; right:0; }
.hx .rail .rk { position:absolute; left:0; font-family:var(--f-mono); font-size:28px; letter-spacing:.12em; color:__MUTED__; }
.hx .rail .bar { position:absolute; height:24px; background:#3a3e46; transform-origin:0 50%; }
.hx .rail .bar.on { background:__BRASS__; }
.hx .rail .gapx { position:absolute; height:24px; background:repeating-linear-gradient(135deg, rgba(255,90,77,.75) 0 4px, transparent 4px 10px); box-shadow:inset 0 0 0 1px rgba(255,90,77,.8); transform-origin:100% 50%; }
.hx .rail .rv { position:absolute; font-family:var(--f-num); font-weight:700; font-size:40px; line-height:1; color:__MUTED__; white-space:nowrap; }
.hx .rail .rv.on { color:__FG__; }
/* gauge */
.hx .gg svg { position:absolute; left:0; top:0; overflow:visible; }
.hx .gg .gl { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.06em; color:__MUTED__; white-space:nowrap; }
.hx .gg .gnum { position:absolute; text-align:center; font-family:var(--f-num); font-weight:700; line-height:1; color:__FG__; white-space:nowrap; font-variant-numeric:tabular-nums; }
.hx .gg .gnum small { font-size:.36em; color:__BRASS__; margin-left:.04em; }
.hx .gg .glab { position:absolute; text-align:center; font-family:var(--f-body); font-weight:700; font-size:32px; color:__MUTED__; white-space:nowrap; }
.hx .gg .gap { position:absolute; font-family:var(--f-mono); font-size:30px; letter-spacing:.06em; color:__LIVE__; white-space:nowrap; }
.hx .fact { position:absolute; display:flex; flex-direction:column; justify-content:center; padding:0 26px; gap:8px; }
.hx .fact .k { font-family:var(--f-mono); font-size:28px; letter-spacing:.14em; color:__MUTED__; white-space:nowrap; }
.hx .fact b { font-family:var(--f-body); font-weight:700; font-size:40px; color:__FG__; white-space:nowrap; line-height:1.1; }
/* diff */
.hx .df .hdr { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.14em; color:__MUTED__; white-space:nowrap; }
.hx .df .row { position:absolute; left:0; }
.hx .df .row .k { position:absolute; left:28px; top:0; bottom:0; display:flex; align-items:center; font-family:var(--f-body); font-weight:700; font-size:36px; color:__FG__; white-space:nowrap; }
.hx .df .row .v { position:absolute; top:0; bottom:0; display:flex; align-items:center; justify-content:flex-end; font-family:var(--f-num); font-weight:700; font-size:66px; line-height:1; white-space:nowrap; font-variant-numeric:tabular-nums; }
.hx .df .row .va { color:__MUTED__; } .hx .df .row .vb { color:__FG__; }
.hx .df .row .mk { position:absolute; top:0; bottom:0; display:flex; flex-direction:column; align-items:flex-end; justify-content:center; gap:4px; white-space:nowrap; }
.hx .df .row .mk .eq { font-family:var(--f-num); font-weight:700; font-size:56px; line-height:1; color:__MUTED__; }
.hx .df .row .mk .dl { font-family:var(--f-mono); font-size:28px; letter-spacing:.04em; color:__MUTED__; }
.hx .df .row .mk .dl.alert { color:__ALERT__; font-size:28px; } .hx .df .row .mk .dl.hot { color:__LIVE__; font-family:var(--f-num); font-weight:700; font-size:40px; letter-spacing:0; }
.hx .df .row .mk .tg { font-family:var(--f-mono); font-size:28px; letter-spacing:.16em; color:__MUTED__; }
.hx .df .bk { position:absolute; border:3px solid __LIVE__; pointer-events:none; }
.hx .df .bk::before, .hx .df .bk::after { content:''; position:absolute; left:6%; right:6%; height:3px; background:__BG__; }
.hx .df .bk::before { top:-3px; } .hx .df .bk::after { bottom:-3px; }
.hx .df .cur { position:absolute; left:-12px; background:rgba(232,184,90,.08); border-top:2px solid rgba(232,184,90,.7); border-bottom:2px solid rgba(232,184,90,.7); pointer-events:none; }
.hx .df .cur::before, .hx .df .cur::after { content:''; position:absolute; top:50%; width:0; height:0; border:12px solid transparent; margin-top:-12px; }
.hx .df .cur::before { left:-12px; border-left-color:__BRASS__; } .hx .df .cur::after { right:-12px; border-right-color:__BRASS__; }
.hx .df .lg { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.1em; color:__MUTED__; white-space:nowrap; }
/* stack */
.hx .sk .ix { position:absolute; font-family:var(--f-num); font-weight:700; font-size:64px; line-height:1; color:__MUTED__; }
.hx .sk .trk { position:absolute; border:1px solid __EDGE__; background:rgba(17,19,23,.6); }
.hx .sk .pill { position:absolute; background:rgba(232,184,90,.38); box-shadow:inset 0 1px 0 rgba(255,255,255,.08); }
.hx .sk .pill.on { background:__LIVE__; }
.hx .sk .nm { position:absolute; display:flex; align-items:center; font-family:var(--f-body); font-weight:700; font-size:34px; color:__FG__; white-space:nowrap; }
.hx .sk .vc { position:absolute; display:flex; flex-direction:column; align-items:flex-end; justify-content:center; gap:2px; white-space:nowrap; }
.hx .sk .vc .vl { font-family:var(--f-num); font-weight:700; font-size:48px; line-height:1; color:__FG__; font-variant-numeric:tabular-nums; }
.hx .sk .vc .pc { font-family:var(--f-mono); font-size:32px; line-height:1.1; letter-spacing:.02em; color:#b6bac1; }
.hx .sk .dark, .hx .sk .dark .vl { color:#14110a; } .hx .sk .vc.dark .pc { color:#4a3b18; }
.hx .sk .hdr { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.14em; color:__MUTED__; white-space:nowrap; }
/* scope */
.hx .sc svg { position:absolute; left:0; top:0; overflow:visible; }
.hx .sc .yl { position:absolute; font-family:var(--f-mono); font-size:28px; color:__MUTED__; white-space:nowrap; text-align:right; }
.hx .sc .xl { position:absolute; font-family:var(--f-mono); font-size:30px; letter-spacing:.06em; color:__MUTED__; white-space:nowrap; text-align:center; width:120px; }
.hx .sc .tag { position:absolute; display:flex; flex-direction:column; gap:2px; padding:8px 14px; white-space:nowrap; }
.hx .sc .tag .k { font-family:var(--f-mono); font-size:28px; letter-spacing:.14em; color:__MUTED__; }
.hx .sc .tag b { font-family:var(--f-num); font-weight:700; font-size:52px; line-height:1; color:__FG__; }
.hx .sc .tag.on { border:2px solid __LIVE__; background:rgba(10,11,13,.85); } .hx .sc .tag.on b { color:__LIVE__; }
.hx .sc .tag.big b { font-size:44px; } .hx .sc .tag.sm { padding:0; align-items:flex-end; } .hx .sc .tag.sm b { font-size:30px; color:__FG__; }
.hx .sc .tag.pk { border:1px solid __EDGE__; background:rgba(17,19,23,.85); }
.hx .sc .head { position:absolute; left:0; top:0; width:20px; height:20px; margin:-10px 0 0 -10px; border-radius:50%; background:__LIVE__; box-shadow:0 0 12px rgba(255,217,138,.95); }
/* matrix */
.hx .mx .cnt { position:absolute; left:0; top:0; font-family:var(--f-num); font-weight:700; line-height:1; color:__FG__; white-space:nowrap; font-variant-numeric:tabular-nums; }
.hx .mx .cnt small { font-size:.4em; color:__BRASS__; margin-left:.05em; }
.hx .mx .c { position:absolute; background:#1b1f25; box-shadow:inset 0 0 0 1px #30343b; overflow:hidden; }
.hx .mx .c i { position:absolute; left:0; top:0; bottom:0; width:100%; background:__BRASS__; transform-origin:0 50%; transform:scaleX(0); }
.hx .mx .lgd { position:absolute; display:flex; flex-direction:column; gap:6px; white-space:nowrap; }
.hx .mx .lgd .k { display:flex; align-items:center; gap:12px; font-family:var(--f-body); font-weight:700; font-size:34px; color:__FG__; }
.hx .mx .lgd .k i { width:26px; height:26px; background:#16191e; box-shadow:inset 0 0 0 1px __EDGE__; }
.hx .mx .lgd.on .k i { background:__BRASS__; }
.hx .mx .lgd b { font-family:var(--f-num); font-weight:700; font-size:46px; line-height:1; color:__MUTED__; }
.hx .mx .lgd.on b { color:__LIVE__; }
.hx .mx .tk2 { position:absolute; font-family:var(--f-mono); font-size:28px; color:__MUTED__; letter-spacing:.06em; }
/* summary stubs */
.hx .sm .stb { position:absolute; }
.hx .sm .stb .lab { position:absolute; font-family:var(--f-mono); font-size:28px; letter-spacing:.12em; color:__BRASS__; white-space:nowrap; }
.hx .sm .stb .un { position:absolute; display:flex; flex-direction:column; align-items:flex-start; gap:6px; white-space:nowrap; }
.hx .sm .stb .un span { font-family:var(--f-body); font-weight:700; font-size:40px; color:__MUTED__; }
.hx .sm .stb .un em { font-style:normal; font-family:var(--f-mono); font-size:28px; letter-spacing:.04em; color:__MUTED__; }
.hx .sm .stb .un em.alert { color:__ALERT__; } .hx .sm .stb .un em.live { color:__LIVE__; }
/* the 12-slat shutter */
.hx-sh { pointer-events:none; }
.hx-sh i { position:absolute; left:0; right:0; background:__BG__; border-bottom:1px solid rgba(232,184,90,.35); transform:scaleY(0); }
"""


def _css(X):
    rep = {"__GRID__": GRIDC, "__LIFT__": LIFT, "__BG__": BG, "__FG__": FG, "__MUTED__": MUTED, "__BRASS__": BRASS, "__LIVE__": LIVE,
           "__ALERT__": ALERT, "__PANEL__": PANEL, "__EDGE__": EDGE, "__HILITE__": HILITE}
    s = HX_CSS
    for k, v in rep.items():
        s = s.replace(k, v)
    X.css("hud-hx", s)


def _T(X, b, k, t, dflt):
    v = X.T(b.get(k), t) if b.get(k) is not None else None
    return float(v) if v is not None else dflt


def _w(s, px, latin=0.5):
    """rough advance of a mixed string: CJK = 1 em, ASCII ~ latin em."""
    n = 0.0
    for c in str(s):
        n += latin if ord(c) < 0x2E80 else 1.0
    return n * px


def num_w(s, px):
    """Barlow Condensed Bold advance: a rolling digit column is as wide as its widest digit (.484 em), '.' .223 em."""
    n = 0.0
    for c in str(s):
        n += 0.485 if c.isdigit() else (0.223 if c in ".," else 0.42)
    return n * px


def backdrop(X):
    """ground + brackets + scan line + ruler: one clip each for the whole film, so the panel never blinks at a cut."""
    if getattr(X, "_hx_bg", False): return
    X._hx_bg = True
    _css(X)
    D = X.duration or 60
    W, H = X.W, X.H
    l = L(X)
    x0, y0, x1, y1 = l["br"]
    X.clip("hxbg", 0, D, '<div class="hx-bg"></div>', "hxbgc", 1, track=5)
    brs = (f'<i class="br b0" style="left:{x0}px;top:{y0}px"></i><i class="br b1" style="left:{x1 - 48}px;top:{y0}px"></i>'
           f'<i class="br b2" style="left:{x0}px;top:{y1 - 48}px"></i><i class="br b3" style="left:{x1 - 48}px;top:{y1 - 48}px"></i>')
    sy0, sy1 = l["scan"]
    ruler = f'<i class="hx-ruler" style="top:{l["ruler"]}px;width:{W + 240}px"></i>'
    # a carrier trace that never stops scrolling (one period = 360 px): the panel is always live, even on a held figure
    cx0, cy0, cw0, ch0 = l["carrier"]
    pts = []
    for k in range(0, int(cw0 + 361), 6):
        u = k / 360 * 2 * math.pi
        pts.append((k, ch0 / 2 - ch0 * 0.42 * (0.62 * math.sin(u) + 0.38 * math.sin(3 * u + 0.8))))
    dline = "M" + " L".join(f"{x:.0f} {y:.1f}" for x, y in pts)
    dfill = dline + f" L{pts[-1][0]:.0f} {ch0} L0 {ch0} Z"
    ruler += (f'<svg class="hx-car" style="position:absolute;left:{cx0}px;top:{cy0}px;overflow:hidden" width="{cw0}" height="{ch0}" viewBox="0 0 {cw0} {ch0}">'
              f'<g class="cw"><path d="{dfill}" fill="rgba(232,184,90,.065)"/><path d="{dline}" fill="none" stroke="rgba(232,184,90,.22)" stroke-width="2"/></g></svg>')
    X.clip("hxov", 0, D, f'<div class="hx-ov">{brs}<i class="scan" style="left:{x0 + 6}px;width:{x1 - x0 - 12}px;top:0"></i>{ruler}</div>', "hxovc", 40, track=6)
    n = max(1, int(math.ceil(D / 4.0)))
    X.tw(f'tl.fromTo("#hxov .scan", {{y:{sy0}}}, {{y:{sy1}, duration:4, ease:"none", repeat:{n - 1}, immediateRender:true}}, 0);')
    m = max(1, int(math.ceil(D / 2.0)))
    X.tw(f'tl.fromTo("#hxov .hx-ruler", {{x:0}}, {{x:-120, duration:2, ease:"none", repeat:{m - 1}, immediateRender:true}}, 0);')
    X.tw(f'tl.from("#hxov .br", {{scale:1.6, opacity:0, duration:0.4, ease:"expo.out", stagger:0.04}}, 0.05);')
    q = max(1, int(math.ceil(D / 3.0)))
    X.tw(f'tl.fromTo("#hxov .hx-car .cw", {{x:0}}, {{x:-360, duration:3, ease:"none", repeat:{q - 1}, immediateRender:true}}, 0);')


def _brackets_to(X, t, dur, inset, ease):
    """move the four persistent brackets: inset = px toward the centre (0 = home)."""
    l = L(X)
    x0, y0, x1, y1 = l["br"]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(4):
        sx = 1 if k in (0, 2) else -1
        sy = 1 if k in (0, 1) else -1
        if isinstance(inset, str):          # "centre": collapse to ±70 px around the middle
            dx = sx * ((cx - x0) - 70 - (0 if sx > 0 else 48)) if sx > 0 else sx * ((x1 - cx) - 70 - 48 + 48)
            dx = (cx - 70 - x0) if sx > 0 else -(x1 - (cx + 70))
            dy = (cy - 70 - y0) if sy > 0 else -(y1 - (cy + 70))
        else:
            dx, dy = sx * inset, sy * inset
        X.tw(f'tl.to("#hxov .b{k}", {{x:{dx:.0f}, y:{dy:.0f}, duration:{dur:.3f}, ease:"{ease}"}}, {t:.3f});')


def seam(X, prev, cid, t, i):
    """beat-to-beat: odd seams a 6-frame shutter of 12 slats; even seams the brackets contract and re-open (8 frames)."""
    if i % 2 == 1:
        sid = X.uid("hxsh")
        H = X.H
        sl = "".join(f'<i style="top:{H * k / 12:.1f}px;height:{H / 12 + 1:.1f}px"></i>' for k in range(12))
        X.clip(sid, t - 3 * F, 6 * F + 0.02, sl, "hx-sh", 45, track=7)
        X.tw(f'tl.fromTo("#{sid} i", {{scaleY:0, transformOrigin:"50% 0%"}}, {{scaleY:1, duration:{3 * F:.3f}, ease:"power2.in", stagger:0.002}}, {t - 3 * F:.3f});')
        X.tw(f'tl.to("#{sid} i", {{scaleY:0, transformOrigin:"50% 100%", duration:{3 * F:.3f}, ease:"power2.out", stagger:0.002}}, {t + F * 0.2:.3f});')
        X.sfx(t - 3 * F, "shutter")
    else:
        _brackets_to(X, t - 4 * F, 4 * F, "centre", "power3.in")
        _brackets_to(X, t, 4 * F, 0, "power3.out")
        X.tw(f'tl.fromTo("#{prev} > .stage", {{clipPath:"inset(0% 0% 0% 0%)"}}, {{clipPath:"inset(46% 44% 46% 44%)", duration:{4 * F:.3f}, ease:"power3.in", immediateRender:false}}, {t - 4 * F:.3f});')
        X.tw(f'tl.fromTo("#{cid} > .stage", {{clipPath:"inset(46% 44% 46% 44%)"}}, {{clipPath:"inset(0% 0% 0% 0%)", duration:{4 * F:.3f}, ease:"power3.out", immediateRender:false}}, {t:.3f});')
        X.sfx(t - 4 * F, "transition")


def reticle_html():
    return '<div class="rt"><i></i><i></i><i></i><i></i></div>'


def lock(X, s, t, rect, sel=".rt"):
    """lock-on: four corners fly in from a loose box, snap 6 px past the target and settle back (2 frames).
    Moved with transforms only (x / y), so nothing snaps to whole pixels."""
    x, y, w, h = rect
    pad, arm = 14, 30

    def corners(bx, by, bw, bh):
        return [(bx, by), (bx + bw - arm, by), (bx, by + bh - arm), (bx + bw - arm, by + bh - arm)]

    loose = corners(x - 90, y - 90, w + 180, h + 180)
    over = corners(x - pad + 6, y - pad + 6, w + 2 * pad - 12, h + 2 * pad - 12)
    final = corners(x - pad, y - pad, w + 2 * pad, h + 2 * pad)
    X.tw(f'tl.fromTo("{s} {sel}", {{opacity:0}}, {{opacity:1, duration:{2 * F:.3f}, ease:"none", immediateRender:true}}, {t:.3f});')
    for k in range(4):
        (lx, ly), (ox, oy), (fx_, fy_) = loose[k], over[k], final[k]
        X.tw(f'tl.fromTo("{s} {sel} i:nth-child({k + 1})", {{x:{lx:.0f}, y:{ly:.0f}}}, {{x:{ox:.0f}, y:{oy:.0f}, duration:{5 * F:.3f}, ease:"power3.out", immediateRender:true}}, {t:.3f});')
        X.tw(f'tl.to("{s} {sel} i:nth-child({k + 1})", {{x:{fx_:.0f}, y:{fy_:.0f}, duration:{2 * F:.3f}, ease:"power1.out"}}, {t + 5 * F:.3f});')
    X.sfx(t + 5 * F, "lock")


def roll_html(text, px, cls="roll", style=""):
    out = ""
    j = 0
    for c in str(text):
        if c.isdigit():
            strip = "".join(f"<b>{k % 10}</b>" for k in range(20))
            out += f'<span class="dc d{j}"><span class="ds">{strip}</span></span>'
            j += 1
        else:
            out += f'<span class="dd">{c}</span>'
    return f'<div class="{cls}" style="font-size:{px}px;{style}">{out}</div>'


def roll(X, sel, t, text, frames=14, gap=2):
    """every digit column rolls on its own: 0 → (one full turn) → its digit, 14 frames, columns 2 frames apart."""
    digs = [c for c in str(text) if c.isdigit()]
    for k, c in enumerate(digs):
        d = int(c)
        X.tw(f'tl.fromTo("{sel} .d{k} .ds", {{yPercent:0}}, {{yPercent:{-(10 + d) * 5}, duration:{frames * F:.3f}, ease:"power3.out", immediateRender:true}}, {t + k * gap * F:.3f});')
    X.sfx(t, "count")
    return t + (len(digs) - 1) * gap * F + frames * F


def _fix_roll_selectors(html):
    return html


def counter(X, sel, t, a, b, dur, dec=1, ease="power2.out", suffix=""):
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); if(!el) return; tl.fromTo(o, {{v:{a}}}, {{v:{b}, duration:{dur:.3f}, ease:"{ease}", immediateRender:true, '
         f'onUpdate:()=>{{el.textContent=o.v.toFixed({dec})+"{suffix}";}}}}, {t:.3f});}})();')


def type_in(X, sel, text, t, every=2):
    text = str(text)
    X.tw(f'tl.set("{sel}", {{textContent:""}}, {X.beat["t"]:.3f});')
    for k in range(1, len(text) + 1):
        js = text[:k].replace("\\", "\\\\").replace('"', '\\"')
        X.tw(f'tl.set("{sel}", {{textContent:"{js}"}}, {t + (k - 1) * every * F:.3f});')
    return t + len(text) * every * F


def page(X, b, cid, t, d, inst):
    """one beat on the panel: status row, headline block, the instrument, readout strip, source, the 5 % beat numeral."""
    backdrop(X)
    W, H, P = X.W, X.H, X.portrait
    l = L(X)
    i, n = X.beat["i"], X.beat["n"]
    meta = X.v.get("meta", {})
    title = meta.get("title", "")
    sx, sy, sw = l["status"]
    live = str(b.get("live", ""))
    X.used_text.update(title + live + "0123456789/ ·.:+-−▲▼%")
    st = (f'<div class="st" style="left:{sx}px;top:{sy}px;width:{sw}px"><span class="ix">{i + 1:02d} / {n:02d}</span>'
          f'<span class="ttl">{X.rich(title)}</span><span class="lv"><i></i><span class="lvt">{X.rich(live)}</span></span></div>')
    kx, ky = l["kick"]
    hx, hy, hw, hpx = l["h1"]
    head = str(b.get("head", ""))
    plain = head.replace("*", "")
    px = hpx
    if not P:
        lines = head.split("|")
    else:
        lines = [head.replace("|", "")]
        if _w(plain, hpx) > hw: px = max(78, int(hw / max(1.0, _w(plain, 1))))
    hl = "".join(f'<span class="ln">{X.rich(ln, split="chars")}</span>' for ln in lines)
    kick = str(b.get("kicker", ""))
    hd = (f'<div class="kick" style="left:{kx}px;top:{ky}px">{X.rich(kick)}</div>'
          f'<div class="h1" style="left:{hx}px;top:{hy}px;width:{hw}px;font-size:{px}px">{hl}</div>')
    if l["lede"] and b.get("lede"):
        lx, ly, lw = l["lede"]
        hd += f'<div class="lede" style="left:{lx}px;top:{ly}px;width:{lw}px">{X.rich(b["lede"])}</div>'
    bx, by, bw, bh = l["box"]
    box = f'<div class="box" style="left:{bx}px;top:{by}px;width:{bw}px;height:{bh}px">{inst}</div>'
    rx, ry, rw = l["ro"]
    cells = list(b.get("readout") or [])[:2]
    while len(cells) < 2: cells.append(["", ""])
    ro = "".join(f'<div><span class="k">{X.rich(k)}</span><b class="rv{j}">{X.rich(v)}</b></div>' for j, (k, v) in enumerate(cells))
    ro += '<div><span class="k">T+</span><b class="clk">00.0</b></div>'
    X.used_text.update("T+0123456789.")
    ro = f'<div class="ro" style="left:{rx}px;top:{ry}px;width:{rw}px">{ro}</div>'
    srx, sry, srw = l["src"]
    src = str(b.get("src", ""))
    if src: X.used_text.update("来源：")
    sr = f'<div class="src" style="left:{srx}px;top:{sry}px;width:{srw}px">来源：{X.rich(src)}</div>' if src else ""
    gx, gy, gpx = l["ghost"]
    ghost = f'<div class="hx-ghost" style="left:{gx}px;top:{gy}px;font-size:{gpx}px">{i + 1:02d}</div>'
    html = f'<div class="hx">{ghost}{st}{hd}{box}{ro}{sr}{reticle_html()}</div>'
    X.clip(cid, t, d, html, "scene", 10 + i, track=1 + i % 2)
    s = f"#{cid}"
    prev = getattr(X, "_hx_prev", None)
    if i > 0 and prev:
        seam(X, prev, cid, t, i)
    X._hx_prev = cid
    # status row: index ticks over, the live readout types in
    X.tw(f'tl.from("{s} .st .ix", {{opacity:0, x:-16, duration:0.3, ease:"power3.out"}}, {t + 0.06:.3f});')
    if live: type_in(X, f"{s} .lvt", live, t + 0.15, 2)
    X.tw(f'tl.fromTo("{s} .st .lv i", {{scale:0}}, {{scale:1, duration:{3 * F:.3f}, ease:"steps(3)", immediateRender:true}}, {t + 0.1:.3f});')
    # headline: kicker types, the line rises out of its mask one glyph a frame
    if kick: type_in(X, f"{s} .kick", kick, t + 0.05, 1)
    X.tw(f'tl.from("{s} .h1 .c", {{yPercent:110, duration:0.42, ease:"power4.out", stagger:{F:.4f}}}, {t + 0.12:.3f});')
    if l["lede"] and b.get("lede"):
        X.tw(f'tl.from("{s} .lede", {{x:-24, opacity:0, duration:0.4, ease:"power3.out"}}, {t + 0.5:.3f});')
    # readout strip: cells drop from the strip line, values type in, the clock runs the whole beat
    X.tw(f'tl.from("{s} .ro > div", {{scaleY:0, transformOrigin:"50% 0%", duration:0.22, ease:"power3.out", stagger:0.05}}, {t + 0.2:.3f});')
    for j, (k, v) in enumerate(cells):
        if v: type_in(X, f"{s} .rv{j}", v, t + 0.5 + j * 0.25, 2)
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .clk"); tl.fromTo(o, {{v:0}}, {{v:{d:.2f}, duration:{d:.2f}, ease:"none", immediateRender:true, '
         f'onUpdate:()=>{{el.textContent=o.v.toFixed(1).padStart(4,"0");}}}}, {t:.3f});}})();')
    if sr: X.tw(f'tl.fromTo("{s} .src", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.45, ease:"steps(12)", immediateRender:true}}, {t + 0.6:.3f});')
    X.tw(f'tl.fromTo("{s} .hx-ghost", {{y:40}}, {{y:-110, duration:{d:.2f}, ease:"none", immediateRender:true}}, {t:.3f});')   # the beat numeral rolls up like a counter tape
    return s, (bx, by, bw, bh)


# ---------------------------------------------------------------- instruments
def ticket(b, X, t, d, cid):
    """hero number on a double-rule ticket. Fields: kicker, head, label, big, stub, was, chip, chip_tone (alert|brass),
    rail [{k, v, show, live}], live, readout, src, at_big."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    rail = list(b.get("rail") or [])
    cw = 880 if P else 940
    ch = (610 if len(rail) < 3 else 580) if P else (530 if len(rail) < 3 else 500)
    cx, cy = (bw - cw) / 2, 6
    big = str(b.get("big", ""))
    stw = 112
    avail = cw - stw - 100
    px = int(min(340 if P else 300, avail / max(0.5, num_w(big, 1))))
    X.used_text.update(big + str(b.get("label", "")) + str(b.get("was", "")) + str(b.get("chip", "")) + str(b.get("stub", "")) + "No.0123456789")
    i = X.beat["i"]
    holes = "".join(f'<i class="hole" style="left:{stw - 5}px;top:{40 + k * ((ch - 80) / 13):.0f}px;width:10px;height:10px"></i>' for k in range(14))
    notches = (f'<i class="hole" style="left:{stw - 18}px;top:-18px;width:36px;height:36px"></i>'
               f'<i class="hole" style="left:{stw - 18}px;top:{ch - 18}px;width:36px;height:36px"></i>')
    ny = (90 + ch - 110) / 2 - 0.545 * px        # the figure's glyphs centred between the label row and the 'was' row
    card = (f'<div class="tk" style="left:{cx:.0f}px;top:{cy:.0f}px;width:{cw}px;height:{ch}px"><i class="r1"></i><i class="r2"></i>'
            f'<div class="stub" style="width:{stw}px"><span class="sv">{X.rich(b.get("stub", ""))}</span><span class="sn">{i + 1:02d}</span></div>'
            f'{holes}{notches}<i class="punch" style="right:-30px;top:-30px;width:60px;height:60px"></i>'
            f'<div class="lab" style="left:{stw + 40}px;top:44px">{X.rich(b.get("label", ""))}</div>'
            + roll_html(big, px, "roll big", f"position:absolute;left:{stw + 30}px;top:{ny}px;color:{FG}")
            + f'<div class="was" style="left:{stw + 40}px;bottom:52px">{X.rich(b.get("was", ""))}</div>'
            f'<div class="chip {b.get("chip_tone", "alert")}" style="right:46px;bottom:38px">{X.rich(b.get("chip", ""))}</div></div>')
    vmax = max([float(r["v"]) for r in rail] or [1])
    top = cy + ch + 40
    rh = min(96, (bh - 44 - top) / max(1, len(rail) - 1)) if len(rail) > 1 else 0   # the last bar sits on the instrument's foot
    barx, barmax = 112, (590 if P else 660)
    rows = ""
    for k, r in enumerate(rail):
        y = top + k * rh
        w = barmax * float(r["v"]) / vmax
        on = " on" if r.get("live") else ""
        gapped = bool(r.get("live")) and b.get("chip_tone", "alert") == "alert" and w < barmax - 4
        X.used_text.update(str(r.get("k", "")) + str(r.get("show", "")))
        rows += (f'<div class="rk" style="top:{y:.0f}px;line-height:40px">{X.rich(r.get("k", ""))}</div>'
                 f'<i class="bar b{k}{on}" style="left:{barx}px;top:{y + 8:.0f}px;width:{w:.0f}px"></i>'
                 f'<div class="rv{on} v{k}" style="left:{barx + (barmax if gapped else w) + 18:.0f}px;top:{y:.0f}px">{X.rich(r.get("show", ""))}</div>')
        if gapped:
            rows += f'<i class="gapx" style="left:{barx + w:.0f}px;top:{y + 8:.0f}px;width:{barmax - w:.0f}px"></i>'
    inst = card + f'<div class="rail" style="top:0">{rows}</div>'
    s, box = page(X, b, cid, t, d, inst)
    # the ticket feeds up out of the instrument slot, then the digits roll
    X.tw(f'tl.fromTo("{s} .tk", {{clipPath:"inset(100% 0% 0% 0%)", y:40}}, {{clipPath:"inset(0% 0% 0% 0%)", y:0, duration:0.45, ease:"power4.out", immediateRender:true}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .tk .lab, {s} .tk .stub", {{x:-20, opacity:0, duration:0.3, ease:"power3.out", stagger:0.06}}, {t + 0.35:.3f});')
    tr = max(t + 0.45, _T(X, b, "at_big", t, t + 0.45))
    te = roll(X, f"{s} .big", tr, big)
    # the delta chip slides in from the right once the roll lands; the reticle locks onto the figure
    X.tw(f'tl.fromTo("{s} .chip", {{x:300, opacity:0}}, {{x:0, opacity:1, duration:0.32, ease:"expo.out", immediateRender:true}}, {te + 0.05:.3f});')
    X.tw(f'tl.from("{s} .tk .was", {{opacity:0, x:-18, duration:0.3, ease:"power3.out"}}, {te + 0.15:.3f});')
    X.sfx(te + 0.05, "hit")
    nw = num_w(big, px)
    lock(X, s, te + 0.25, (box[0] + cx + stw + 30, box[1] + cy + ny + px * 0.1, nw, px * 0.78))
    # the rail ticks out bar by bar after the figure
    for k, r in enumerate(rail):
        tk = te + 0.35 + k * 0.22
        X.tw(f'tl.fromTo("{s} .rail .b{k}", {{scaleX:0}}, {{scaleX:1, duration:0.4, ease:"steps(14)", immediateRender:true}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .rail .v{k}", {{opacity:0, x:-12, duration:0.25, ease:"power3.out"}}, {tk + 0.35:.3f});')
    X.tw(f'tl.from("{s} .rail .rk", {{opacity:0, duration:0.2, stagger:0.22}}, {te + 0.3:.3f});')
    X.tw(f'tl.fromTo("{s} .rail .gapx", {{scaleX:0}}, {{scaleX:1, duration:0.3, ease:"power3.out", immediateRender:true}}, {te + 0.35 + len(rail) * 0.22 + 0.2:.3f});')


def gauge(b, X, t, d, cid):
    """a 270° arc gauge for a percentage. Fields: pct, big, label, second {pct, label}, gap, facts [[k, v], [k, v]]."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    D = 640 if P else 600
    R = D / 2 - 26
    cx, cy = bw / 2 if P else D / 2 + 40, D / 2 + 6
    pct = float(b.get("pct", 0))

    def ang(p):
        return math.radians(135 + 270 * p / 100)

    def pt(p, r):
        a = ang(p)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    ticks = ""
    labels = ""
    for k in range(21):
        p = k * 5
        major = k % 5 == 0
        x1, y1 = pt(p, R - 22)
        x2, y2 = pt(p, R - (52 if major else 38))
        ticks += f'<line class="tk" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{BRASS if major else MUTED}" stroke-width="{3 if major else 2}"/>'
        if major and p in (0, 50, 100):
            lx, ly = pt(p, R - 82)
            labels += f'<div class="gl" style="left:{lx - 30:.0f}px;top:{ly - 14:.0f}px;width:60px;text-align:center">{p}</div>'
    X.used_text.update("0255075100")
    arc_len = 2 * math.pi * R * 0.75
    ax0, ay0 = pt(0, R)
    ax1, ay1 = pt(100, R)
    arc = f'M{ax0:.1f} {ay0:.1f} A{R:.1f} {R:.1f} 0 1 1 {ax1:.1f} {ay1:.1f}'
    sec = b.get("second") or {}
    spct = float(sec.get("pct", 0)) if sec else 0
    extra = ""
    if sec:
        mx1, my1 = pt(spct, R + 10)
        mx2, my2 = pt(spct, R - 30)
        extra += f'<line class="smk" x1="{mx1:.1f}" y1="{my1:.1f}" x2="{mx2:.1f}" y2="{my2:.1f}" stroke="{FG}" stroke-width="4" opacity=".7"/>'
        rr = R + 30
        gx0, gy0 = pt(spct, rr)
        gx1, gy1 = pt(pct, rr)
        large = 1 if (pct - spct) * 2.7 > 180 else 0
        extra += f'<path class="gpth" d="M{gx0:.1f} {gy0:.1f} A{rr:.1f} {rr:.1f} 0 {large} 1 {gx1:.1f} {gy1:.1f}" fill="none" stroke="{LIVE}" stroke-width="3"/>'
        for p in (spct, pct):
            e1x, e1y = pt(p, rr - 9)
            e2x, e2y = pt(p, rr + 9)
            extra += f'<line class="gcap" x1="{e1x:.1f}" y1="{e1y:.1f}" x2="{e2x:.1f}" y2="{e2y:.1f}" stroke="{LIVE}" stroke-width="3"/>'
    hx_, hy_ = pt(0, R - 64)
    svg = (f'<svg width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}">'
           f'<path d="{arc}" fill="none" stroke="#1d2026" stroke-width="16"/>'
           f'<path class="prog" d="{arc}" fill="none" stroke="{BRASS}" stroke-width="16" stroke-dasharray="{arc_len:.1f} {arc_len + 10:.1f}" stroke-dashoffset="{arc_len:.1f}"/>'
           f'<g class="tks">{ticks}</g>{extra}'
           f'<g class="ndl"><line x1="{cx + R - 118:.1f}" y1="{cy:.1f}" x2="{cx + R + 14:.1f}" y2="{cy:.1f}" stroke="{LIVE}" stroke-width="6" stroke-linecap="butt"/>'
           f'<path d="M{cx + R - 118:.1f} {cy - 10:.1f} L{cx + R - 140:.1f} {cy:.1f} L{cx + R - 118:.1f} {cy + 10:.1f} Z" fill="{LIVE}"/></g>'
           f'</svg>')
    big = str(b.get("big", ""))
    npx = 242 if P else 210
    X.used_text.update(big + "%" + str(b.get("label", "")) + str(sec.get("label", "")) + str(b.get("gap", "")))
    num = (f'<div class="gnum" style="left:{cx - 260:.0f}px;width:520px;top:{cy - npx * 0.545:.0f}px;font-size:{npx}px"><span class="gv">0.0</span><small>%</small></div>'
           f'<div class="glab" style="left:{cx - 200:.0f}px;width:400px;top:{cy + npx * 0.355 + 18:.0f}px">{X.rich(b.get("label", ""))}</div>')
    side = ""
    if sec:
        lx, ly = pt(spct, R + 64)
        side += f'<div class="gl sl" style="left:{lx - 160:.0f}px;top:{ly - 30:.0f}px;width:150px;text-align:right;line-height:1.25;color:{FG}">{X.rich(sec.get("label", ""))}<br>{spct:g}%</div>'
        gx, gy = pt((spct + pct) / 2, R + 54)
        side += f'<div class="gap" style="left:{gx - 160:.0f}px;top:{gy - 40:.0f}px;width:150px;text-align:right">{X.rich(b.get("gap", ""))}</div>'
    facts = ""
    fl = list(b.get("facts") or [])[:2]
    if P:
        fw, fh, fy = (bw - 40) / 2 - 10, 120, D + 30
        for k, (fk, fv) in enumerate(fl):
            X.used_text.update(str(fk) + str(fv))
            facts += f'<div class="pn fact f{k}" style="left:{k * (fw + 20):.0f}px;top:{fy:.0f}px;width:{fw:.0f}px;height:{fh}px"><span class="k">{X.rich(fk)}</span><b>{X.rich(fv)}</b></div>'
    else:
        fw, fh = bw - D - 100, 150
        for k, (fk, fv) in enumerate(fl):
            X.used_text.update(str(fk) + str(fv))
            facts += f'<div class="pn fact f{k}" style="left:{D + 100:.0f}px;top:{150 + k * (fh + 30):.0f}px;width:{fw:.0f}px;height:{fh}px"><span class="k">{X.rich(fk)}</span><b>{X.rich(fv)}</b></div>'
    inst = f'<div class="gg">{svg}{labels}{num}{side}</div>{facts}'
    s, box = page(X, b, cid, t, d, inst)
    t0 = t + 0.2
    X.tw(f'tl.from("{s} .tks line", {{opacity:0, duration:0.01, stagger:{F:.4f}}}, {t0:.3f});')
    X.tw(f'tl.from("{s} .gl:not(.sl)", {{opacity:0, duration:0.15, stagger:0.1}}, {t0 + 0.1:.3f});')
    X.sfx(t0, "pop")
    ts = max(t0 + 0.65, _T(X, b, "at_big", t, t0 + 0.65))
    a0, a1, a2 = 135, 135 + 270 * (pct + 4) / 100, 135 + 270 * pct / 100
    X.tw(f'tl.fromTo("{s} .ndl", {{rotation:{a0}, svgOrigin:"{cx:.1f} {cy:.1f}"}}, {{rotation:{a1:.2f}, svgOrigin:"{cx:.1f} {cy:.1f}", duration:0.75, ease:"power3.out", immediateRender:true}}, {ts:.3f});')
    X.tw(f'tl.to("{s} .ndl", {{rotation:{a2:.2f}, svgOrigin:"{cx:.1f} {cy:.1f}", duration:0.3, ease:"sine.inOut"}}, {ts + 0.75:.3f});')
    off1, off2 = arc_len * (1 - (pct + 4) / 100), arc_len * (1 - pct / 100)
    X.tw(f'tl.fromTo("{s} .prog", {{strokeDashoffset:{arc_len:.1f}}}, {{strokeDashoffset:{off1:.1f}, duration:0.75, ease:"power3.out", immediateRender:true}}, {ts:.3f});')
    X.tw(f'tl.to("{s} .prog", {{strokeDashoffset:{off2:.1f}, duration:0.3, ease:"sine.inOut"}}, {ts + 0.75:.3f});')
    counter(X, f"{s} .gv", ts, 0, pct + 4, 0.75, 1, "power3.out")
    counter(X, f"{s} .gv", ts + 0.75, pct + 4, pct, 0.3, 1, "sine.inOut")
    X.tw(f'tl.from("{s} .glab", {{opacity:0, y:12, duration:0.3, ease:"power3.out"}}, {ts + 0.3:.3f});')
    X.sfx(ts, "count")
    tl_ = ts + 1.1
    nw = num_w(big, npx) + npx * 0.36 * 0.6
    lock(X, s, tl_, (box[0] + cx - nw / 2, box[1] + cy - npx * 0.36, nw, npx * 0.72))
    if sec:
        tg = tl_ + 0.35
        X.tw(f'tl.from("{s} .smk, {s} .sl", {{opacity:0, duration:0.2, ease:"steps(4)"}}, {tg:.3f});')
        glen = 2 * math.pi * (R + 30) * (pct - spct) * 0.75 / 100
        X.tw(f'tl.fromTo("{s} .gpth", {{strokeDasharray:"0 {glen + 20:.1f}"}}, {{strokeDasharray:"{glen + 20:.1f} 0", duration:0.4, ease:"power2.inOut", immediateRender:true}}, {tg + 0.2:.3f});')
        X.tw(f'tl.from("{s} .gcap", {{opacity:0, duration:0.1, stagger:0.3}}, {tg + 0.2:.3f});')
        X.tw(f'tl.from("{s} .gap", {{opacity:0, x:-14, duration:0.25, ease:"power3.out"}}, {tg + 0.55:.3f});')
        X.sfx(tg + 0.2, "mark")
    X.tw(f'tl.from("{s} .fact", {{y:30, opacity:0, duration:0.35, ease:"power4.out", stagger:0.12}}, {t0 + 0.4:.3f});')   # the frame is full by 45 % of the beat


def diff(b, X, t, d, cid):
    """到底差在哪: two columns compared row by row under a stepping cursor bar. Fields: cols [a, b], unit, rows
    [{k, a, b, mark ("ref" | "=" | "hot"), delta}], legend."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    rows = list(b.get("rows") or [])
    cols = b.get("cols") or ["", ""]
    hh = 64
    n = max(1, len(rows))
    gap = 18
    rh = min(150, (bh - hh - 70 - gap * (n - 1)) / n)
    wk, wa, wb = (280, 190, 190) if P else (320, 210, 210)
    xa = wk + wa            # right edge of column a
    xb = xa + 30 + wb       # right edge of column b
    rw = 880 if P else bw
    xm = rw - 24            # right edge of the marker column
    X.used_text.update("".join(str(c) for c in cols) + str(b.get("unit", "")) + "=▲▼REF" + str(b.get("legend", "")))
    hdr = (f'<div class="hdr" style="left:28px;top:16px">{X.rich(b.get("unit", ""))}</div>'
           f'<div class="hdr" style="left:{xa - 160}px;width:160px;text-align:right;top:16px">{X.rich(cols[0])}</div>'
           f'<div class="hdr" style="left:{xb - 160}px;width:160px;text-align:right;top:16px;color:{FG}">{X.rich(cols[1])}</div>'
           f'<div class="hdr" style="left:{xm - 160}px;width:160px;text-align:right;top:16px">Δ</div>')
    body = ""
    hot = None
    for k, r in enumerate(rows):
        y = hh + k * (rh + gap)
        mk = r.get("mark", "=")
        X.used_text.update(str(r.get("k", "")) + str(r.get("a", "")) + str(r.get("b", "")) + str(r.get("delta", "")))
        if mk == "hot":
            hot = k
            mark = f'<span class="dl hot">{X.rich(r.get("delta", ""))}</span>'
        elif mk == "ref":
            mark = f'<span class="tg">REF</span><span class="dl alert">{X.rich(r.get("delta", ""))}</span>'
        else:
            mark = f'<span class="eq">=</span><span class="dl">{X.rich(r.get("delta", ""))}</span>'
        body += (f'<div class="row pn r{k}" style="top:{y:.0f}px;width:{rw}px;height:{rh:.0f}px">'
                 f'<span class="k">{X.rich(r.get("k", ""))}</span>'
                 f'<span class="v va" style="right:{rw - xa}px">{X.rich(r.get("a", ""))}</span>'
                 f'<span class="v vb" style="right:{rw - xb}px">{X.rich(r.get("b", ""))}</span>'
                 f'<span class="mk m{k}" style="right:{rw - xm}px">{mark}</span></div>')
    cur = f'<i class="cur" style="top:{hh - 6}px;width:{rw + 24}px;height:{rh + 12:.0f}px"></i>'
    bk = ""
    if hot is not None:
        yk = hh + hot * (rh + gap)
        bk = f'<i class="bk" style="left:-10px;top:{yk - 10:.0f}px;width:{rw + 20}px;height:{rh + 20:.0f}px"></i>'
    lg = f'<div class="lg" style="left:28px;top:{hh + n * (rh + gap) + 6:.0f}px">{X.rich(b.get("legend", ""))}</div>' if b.get("legend") else ""
    inst = f'<div class="df">{hdr}{body}{cur}{bk}{lg}</div>'
    s, box = page(X, b, cid, t, d, inst)
    X.tw(f'tl.from("{s} .df .hdr", {{opacity:0, y:-10, duration:0.25, ease:"power3.out", stagger:0.05}}, {t + 0.2:.3f});')
    X.tw(f'tl.from("{s} .df .row", {{x:-60, opacity:0, duration:0.3, ease:"power4.out", stagger:{2 * F:.4f}}}, {t + 0.25:.3f});')
    X.tw(f'tl.set("{s} .df .mk", {{visibility:"hidden"}}, {t:.3f});')
    X.tw(f'tl.set("{s} .df .cur, {s} .df .bk", {{opacity:0}}, {t:.3f});')
    tc = t + 0.75
    X.tw(f'tl.set("{s} .df .cur", {{opacity:1}}, {tc:.3f});')
    dwell = max(0.42, min(0.62, (d - 2.6) / max(1, n)))
    for k, r in enumerate(rows):
        tk = tc + k * dwell
        if k:
            X.tw(f'tl.to("{s} .df .cur", {{y:{k * (rh + gap):.0f}, duration:{6 * F:.3f}, ease:"power3.inOut"}}, {tk - 6 * F:.3f});')
            X.sfx(tk - 6 * F, "step")
        X.tw(f'tl.set("{s} .df .m{k}", {{visibility:"visible"}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .df .m{k} > span", {{x:24, duration:0.18, ease:"steps(3)", stagger:0.04}}, {tk:.3f});')
        if r.get("mark") != "hot":
            X.tw(f'tl.to("{s} .df .r{k} .vb", {{color:"{MUTED if r.get("mark") == "=" else ALERT}", duration:0.01}}, {tk:.3f});')
    if hot is not None:
        th = tc + hot * dwell
        X.tw(f'tl.to("{s} .df .cur", {{opacity:0, duration:0.15}}, {th + 0.1:.3f});')
        X.tw(f'tl.set("{s} .df .bk", {{opacity:1}}, {th:.3f});')
        X.tw(f'tl.fromTo("{s} .df .bk", {{scaleX:1.08, scaleY:1.5}}, {{scaleX:1, scaleY:1, duration:{4 * F:.3f}, ease:"back.out(3)", immediateRender:false}}, {th:.3f});')
        X.tw(f'tl.to("{s} .df .r{hot} .vb", {{color:"{LIVE}", duration:0.01}}, {th:.3f});')
        X.sfx(th, "hit")
        yk = hh + hot * (rh + gap)
        lock(X, s, th + 0.3, (box[0] + xa + 30, box[1] + yk + 10, xm - xa - 30, rh - 20))
    X.tw(f'tl.from("{s} .df .lg", {{opacity:0, duration:0.3}}, {tc + n * dwell:.3f});')


def stack(b, X, t, d, cid):
    """numbered capsule stack for a breakdown / ranking: each row is a bar inside a full-width track, bar WIDTH in true
    ratio; the live one lights bright brass. Fields: unit, items [{name, value, show, pct}], live_i (default 0)."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    items = list(b.get("items") or [])[:6]
    n = max(1, len(items))
    hh = 50
    rh = (bh - hh) / n
    ch = min(108, rh - 30)
    tw_ = 880 if P else bw                  # the track: full instrument width
    x0 = 84                                 # bars start after the index numeral
    vcol = 200                              # value column (right-aligned at the track's right edge)
    maxw = tw_ - x0 - 8
    vmax = max([float(it["value"]) for it in items] or [1])
    li = int(b.get("live_i", 0))
    X.used_text.update(str(b.get("unit", "")) + "单位·占比")
    rows = f'<div class="hdr" style="left:{x0}px;top:6px">单位 · {X.rich(b.get("unit", ""))}</div>'
    geo = []
    for k, it in enumerate(items):
        y = hh + k * rh + (rh - ch) / 2
        w = max(ch * 0.4, maxw * float(it["value"]) / vmax)
        geo.append((y, w))
        name = str(it.get("name", ""))
        X.used_text.update(name + str(it.get("show", "")) + str(it.get("pct", "")))
        nw = _w(name, 34)
        inside = w >= nw + 48 + (vcol if w > maxw - vcol else 0)
        rows += (f'<i class="trk" style="left:0;top:{y:.0f}px;width:{tw_}px;height:{ch:.0f}px"></i>'
                 f'<div class="ix i{k}" style="left:22px;top:{y + (ch - 64) / 2:.0f}px">{k + 1}</div>'
                 f'<i class="pill c{k}" style="left:{x0}px;top:{y + 8:.0f}px;width:{w:.0f}px;height:{ch - 16:.0f}px"></i>'
                 f'<div class="nm t{k}" style="left:{x0 + (24 if inside else w + 24):.0f}px;top:{y:.0f}px;height:{ch:.0f}px">{X.rich(name)}</div>'
                 f'<div class="vc t{k}" style="right:{bw - tw_ + 26}px;top:{y:.0f}px;height:{ch:.0f}px"><b class="vl v{k}">{X.rich(it.get("show", ""))}</b>'
                 f'<span class="pc">{X.rich(it.get("pct", ""))}</span></div>')
    inst = f'<div class="sk">{rows}</div>'
    s, box = page(X, b, cid, t, d, inst)
    t0 = t + 0.2
    X.tw(f'tl.from("{s} .sk .trk", {{scaleX:0, transformOrigin:"0% 50%", duration:0.3, ease:"power3.out", stagger:{2 * F:.4f}}}, {t0:.3f});')
    X.tw(f'tl.from("{s} .sk .pill", {{y:-160, opacity:0, duration:0.38, ease:"expo.out", stagger:{2 * F:.4f}}}, {t0 + 0.1:.3f});')
    X.tw(f'tl.from("{s} .sk .ix", {{y:-160, opacity:0, duration:0.38, ease:"expo.out", stagger:{2 * F:.4f}}}, {t0 + 0.1:.3f});')
    X.tw(f'tl.from("{s} .sk .nm, {s} .sk .vc", {{x:-30, opacity:0, duration:0.3, ease:"power3.out", stagger:{F:.4f}}}, {t0 + 0.35:.3f});')
    X.tw(f'tl.from("{s} .sk .hdr", {{opacity:0, duration:0.2}}, {t0:.3f});')
    X.sfx(t0, "enter")
    for k, it in enumerate(items):
        v = float(it["value"])
        dec = len(str(it.get("show", "")).split(".")[1]) if "." in str(it.get("show", "")) else 0
        counter(X, f"{s} .sk .v{k}", t0 + 0.35 + k * 2 * F, 0, v, 0.6, dec, "power2.out")
    tl_ = max(t0 + 1.15, _T(X, b, "at_live", t, t0 + 1.15))
    if items:
        y, w = geo[li]
        X.tw(f'tl.set("{s} .sk .pill.c{li}", {{attr:{{class:"pill c{li} on"}}}}, {tl_:.3f});')
        X.tw(f'tl.set("{s} .sk .ix.i{li}", {{color:"{LIVE}"}}, {tl_:.3f});')
        if w >= maxw - vcol:             # the value column sits on the lit bar: dark ink
            X.tw(f'tl.set("{s} .sk .vc.t{li}", {{attr:{{class:"vc t{li} dark"}}}}, {tl_:.3f});')
        if w >= _w(str(items[li].get("name", "")), 34) + 48:
            X.tw(f'tl.set("{s} .sk .nm.t{li}", {{attr:{{class:"nm t{li} dark"}}}}, {tl_:.3f});')
        X.sfx(tl_, "hit")
        lock(X, s, tl_ + 0.1, (box[0], box[1] + y, tw_, ch))


def scope(b, X, t, d, cid):
    """time series as an oscilloscope trace on a 10×8 graticule: a 6 px trace with a glowing head, the area under it
    filling as it runs, a value tag on every point (the peak and the last one larger). Fields: unit, points [{x, v}],
    ymax, peak (index), tag."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    pts = list(b.get("points") or [])
    gx0, gy0 = 96, 20
    gw = (880 if P else bw) - gx0 - 6
    gh = bh - 30
    dvx, dvy = gw / 10, gh / 8
    ymax = float(b.get("ymax") or max(p["v"] for p in pts) * 1.2)
    lines = ""
    for k in range(11):
        x = gx0 + k * dvx
        lines += f'<line x1="{x:.1f}" y1="{gy0}" x2="{x:.1f}" y2="{gy0 + gh:.1f}" stroke="{"#2a2d33" if k in (0, 10) else "#1c1f24"}" stroke-width="{2 if k in (0, 10) else 1}"/>'
    for k in range(9):
        y = gy0 + k * dvy
        lines += f'<line x1="{gx0}" y1="{y:.1f}" x2="{gx0 + gw:.1f}" y2="{y:.1f}" stroke="{"#2a2d33" if k in (0, 8) else "#1c1f24"}" stroke-width="{2 if k in (0, 8) else 1}"/>'
    mid_y, mid_x = gy0 + gh / 2, gx0 + gw / 2
    for k in range(51):          # minor ticks on the centre lines, 5 per division
        x = gx0 + k * dvx / 5
        lines += f'<line x1="{x:.1f}" y1="{mid_y - (8 if k % 5 == 0 else 5):.1f}" x2="{x:.1f}" y2="{mid_y + (8 if k % 5 == 0 else 5):.1f}" stroke="#3a3e46" stroke-width="1.5"/>'
    for k in range(41):
        y = gy0 + k * dvy / 5
        lines += f'<line x1="{mid_x - (8 if k % 5 == 0 else 5):.1f}" y1="{y:.1f}" x2="{mid_x + (8 if k % 5 == 0 else 5):.1f}" y2="{y:.1f}" stroke="#3a3e46" stroke-width="1.5"/>'
    ylab = ""
    for k in range(2, 9, 2):
        v = ymax * k / 8
        y = gy0 + gh - k * dvy
        ylab += f'<div class="yl" style="left:0;width:{gx0 - 14}px;top:{y - 15:.0f}px">{v:.0f}</div>'
        X.used_text.update(f"{v:.0f}")
    n = len(pts)
    xy = []
    for k, p in enumerate(pts):
        x = gx0 + dvx * (1 + 2 * k) if n == 5 else gx0 + gw * (k + 0.5) / n
        y = gy0 + gh - float(p["v"]) / ymax * gh
        xy.append((x, y))
    xl = ""
    for k, p in enumerate(pts):        # year labels sit inside the graticule, on its floor
        X.used_text.update(str(p["x"]))
        xl += f'<div class="xl x{k}" style="left:{xy[k][0] - 60:.0f}px;top:{gy0 + gh - 48:.0f}px">{X.rich(p["x"])}</div>'
    seg = [math.hypot(xy[k + 1][0] - xy[k][0], xy[k + 1][1] - xy[k][1]) for k in range(n - 1)]
    total = sum(seg) or 1
    dpath = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in xy)
    darea = dpath + f" L{xy[-1][0]:.1f} {gy0 + gh:.1f} L{xy[0][0]:.1f} {gy0 + gh:.1f} Z"
    dots = "".join(f'<circle class="pd p{k}" cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{BRASS}" stroke="{BG}" stroke-width="2"/>' for k, (x, y) in enumerate(xy))
    svg = (f'<svg width="{bw}" height="{bh}" viewBox="0 0 {bw} {bh}"><g class="grat">{lines}</g>'
           f'<path class="ar" d="{darea}" fill="rgba(232,184,90,.10)" style="clip-path:inset(0 100% 0 0)"/>'
           f'<path class="tr" d="{dpath}" fill="none" stroke="{LIVE}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round" '
           f'stroke-dasharray="{total:.1f} {total + 10:.1f}" stroke-dashoffset="{total:.1f}" style="filter:drop-shadow(0 0 4px rgba(255,217,138,.55))"/>{dots}</svg>')
    X.used_text.update(str(b.get("unit", "")) + str(b.get("tag", "")) + "PEAKLAST0123456789.")
    pk = b.get("peak")
    pk = int(pk) if pk is not None else None
    tags = ""
    for k, p in enumerate(pts):
        x, y = xy[k]
        val = f'{float(p["v"]):.1f}'
        if k == n - 1:
            tags += (f'<div class="tag on big t{k}" style="left:{x - 200:.0f}px;top:{y + 34:.0f}px"><span class="k">LAST {X.rich(p["x"])}</span>'
                     f'<b>{X.rich(b.get("tag", val))}</b></div>')
        elif k == pk:
            tags += (f'<div class="tag pk big t{k}" style="left:{x - 96:.0f}px;top:{max(gy0 + 4, y - 118):.0f}px"><span class="k">PEAK {X.rich(p["x"])}</span>'
                     f'<b>{val}</b></div>')
        else:
            tags += f'<div class="tag sm t{k}" style="left:{x - 156:.0f}px;top:{y - 58:.0f}px;width:140px"><b>{val}</b></div>'
    unit = f'<div class="yl" style="left:{gx0 + 14}px;top:{gy0 + 10}px;text-align:left;letter-spacing:.14em">{X.rich(b.get("unit", ""))}</div>'
    inst = f'<div class="sc">{svg}{ylab}{xl}{unit}{tags}<i class="head"></i></div>'
    s, box = page(X, b, cid, t, d, inst)
    t0 = t + 0.15
    X.tw(f'tl.from("{s} .grat line", {{opacity:0, duration:0.01, stagger:0.003}}, {t0:.3f});')
    X.tw(f'tl.from("{s} .sc .yl", {{opacity:0, x:-10, duration:0.2, stagger:0.04}}, {t0 + 0.2:.3f});')
    X.tw(f'tl.set("{s} .sc .pd, {s} .sc .tag", {{opacity:0}}, {t:.3f});')
    td = max(t0 + 0.45, _T(X, b, "at_trace", t, t0 + 0.45))
    dur = 1.9
    X.tw(f'tl.fromTo("{s} .tr", {{strokeDashoffset:{total:.1f}}}, {{strokeDashoffset:0, duration:{dur}, ease:"none", immediateRender:true}}, {td:.3f});')
    js_pts = "[" + ",".join(f"[{x:.1f},{y:.1f}]" for x, y in xy) + "]"
    X.tw(f'(()=>{{const P={js_pts}, el=document.querySelector("{s} .head"), ar=document.querySelector("{s} .ar"); const L=[]; let T=0; for(let k=0;k<P.length-1;k++){{const l=Math.hypot(P[k+1][0]-P[k][0],P[k+1][1]-P[k][1]); L.push(l); T+=l;}} '
         f'const o={{u:0}}; const put=()=>{{let r=o.u*T, k=0; while(k<L.length-1 && r>L[k]){{r-=L[k]; k++;}} const f=Math.min(1,r/L[k]); '
         f'const hx=P[k][0]+(P[k+1][0]-P[k][0])*f, hy=P[k][1]+(P[k+1][1]-P[k][1])*f; '
         f'el.style.transform="translate("+hx.toFixed(1)+"px,"+hy.toFixed(1)+"px)"; ar.style.clipPath="inset(0 "+Math.max(0,{bw}-hx).toFixed(1)+"px 0 0)";}}; '
         f'tl.fromTo(o, {{u:0}}, {{u:1, duration:{dur}, ease:"none", immediateRender:true, onUpdate:put}}, {td:.3f}); put();}})();')
    X.tw(f'tl.fromTo("{s} .head", {{opacity:0}}, {{opacity:1, duration:0.05, immediateRender:true}}, {td:.3f});')
    acc = 0.0
    for k in range(n):
        tk = td + dur * (acc / total)
        X.tw(f'tl.set("{s} .sc .p{k}", {{opacity:1}}, {tk:.3f}); tl.to("{s} .sc .x{k}", {{color:"{FG}", duration:0.01}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{s} .sc .tag.t{k}", {{opacity:0, y:10}}, {{opacity:1, y:0, duration:0.22, ease:"power3.out", immediateRender:false}}, {tk + 0.04:.3f});')
        if k < n - 1: acc += seg[k]
        X.sfx(tk, "mark")
    te = td + dur
    X.sfx(te, "hit")
    lx, ly = xy[-1]
    lock(X, s, te + 0.2, (box[0] + lx - 14, box[1] + ly - 14, 28, 28))


def matrix(b, X, t, d, cid):
    """share of total as a 10×10 cell matrix: cells light in reading order in the true count, a counter runs with them.
    Fields: pct, big, legend [{k, v, on}]."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    pct = float(b.get("pct", 0))
    big = str(b.get("big", f"{pct:g}"))
    if P:
        npx = 270
        my = 250
        cw_, chh, g = 62, 49, 6
        mx0 = 0
    else:
        npx = 200
        my = 196
        cw_, chh, g = 80, 51, 6
        mx0 = 0
    cells = ""
    for k in range(100):
        r, c = divmod(k, 10)
        cells += f'<div class="c c{k}" style="left:{mx0 + c * (cw_ + g)}px;top:{my + r * (chh + g)}px;width:{cw_}px;height:{chh}px"><i></i></div>'
    mw = 10 * cw_ + 9 * g
    mh = 10 * chh + 9 * g
    X.used_text.update(big + "%0123456789.")
    if P:
        cnt = f'<div class="cnt" style="font-size:{npx}px;top:-14px"><span class="cv">0.00</span><small>%</small></div>'
    else:
        cnt = f'<div class="cnt" style="font-size:{npx}px;top:-30px;left:0"><span class="cv">0.00</span><small>%</small></div>'
    lg = ""
    lgx = mx0 + mw + 30 if P else 0
    for k, it in enumerate(list(b.get("legend") or [])[:2]):
        X.used_text.update(str(it.get("k", "")) + str(it.get("v", "")))
        ly = (my + 300 + k * 150) if P else 16
        if not P: lgx = 560 + k * 220
        lg += f'<div class="lgd l{k}{" on" if it.get("on") else ""}" style="left:{lgx}px;top:{ly}px"><span class="k"><i></i>{X.rich(it.get("k", ""))}</span><b>{X.rich(it.get("v", ""))}</b></div>'
    ticks = ""
    inst = f'<div class="mx">{cnt}{cells}{lg}{ticks}</div>'
    s, box = page(X, b, cid, t, d, inst)
    t0 = t + 0.15
    X.tw(f'tl.from("{s} .mx .c", {{scale:0, duration:0.18, ease:"power3.out", stagger:{{each:0.004, grid:[10,10], from:"start"}}}}, {t0:.3f});')
    X.tw(f'tl.from("{s} .mx .cnt", {{x:-30, opacity:0, duration:0.35, ease:"power4.out"}}, {t0 + 0.1:.3f});')
    tf = max(t0 + 0.7, _T(X, b, "at_fill", t, t0 + 0.7))
    full = int(pct)
    frac = pct - full
    for k in range(full):
        X.tw(f'tl.set("{s} .mx .c{k} i", {{scaleX:1}}, {tf + k * F:.3f});')
    if frac > 0.005:
        X.tw(f'tl.fromTo("{s} .mx .c{full} i", {{scaleX:0}}, {{scaleX:{frac:.3f}, duration:{max(F, frac * F) * 4:.3f}, ease:"none", immediateRender:true}}, {tf + full * F:.3f});')
    span = (pct) * F
    counter(X, f"{s} .mx .cv", tf, 0, pct, span, 2, "none")
    X.sfx(tf, "count")
    te = tf + span + 0.15
    X.tw(f'tl.from("{s} .mx .lgd", {{x:-20, opacity:0, duration:0.3, ease:"power3.out", stagger:0.12}}, {te:.3f});')
    rows_lit = full // 10 + (1 if (full % 10 or frac) else 0)
    lock(X, s, te + 0.2, (box[0] + mx0, box[1] + my, mw, rows_lit * (chh + g) - g))
    X.sfx(te, "hit")


def summary(b, X, t, d, cid):
    """three ticket stubs (stacked in 9:16, side by side in 16:9); then the brackets close in 40 px and the status reads END.
    Fields: stubs [{k, v, unit, tone (alert|live), note}]."""
    P = X.portrait
    bx, by, bw, bh = L(X)["box"]
    stubs = list(b.get("stubs") or [])[:3]
    out = ""
    if P:
        sw, sh, gp = 880, 250, 25
        npx = 240
    else:
        sw, sh, gp = bw, 236, 25
        npx = 226
    P = True            # the stubs stack in both aspects (16:9 has the same 980-px instrument column)
    for k, st in enumerate(stubs):
        x, y = (0, k * (sh + gp)) if P else (k * (sw + gp), 30)
        v = str(st.get("v", ""))
        X.used_text.update(str(st.get("k", "")) + v + str(st.get("unit", "")) + str(st.get("note", "")) + "0123456789")
        tone = st.get("tone", "")
        col = ALERT if tone == "alert" else (LIVE if tone == "live" else FG)
        col = FG if tone == "alert" else col
        holes = "".join(f'<i class="hole" style="left:{(78 if P else 30) + (0 if P else 0)}px;top:{30 + j * ((sh - 60) / 9):.0f}px;width:8px;height:8px"></i>' for j in range(10)) if P else \
            "".join(f'<i class="hole" style="left:{30 + j * ((sw - 60) / 9):.0f}px;top:96px;width:8px;height:8px"></i>' for j in range(10))
        if P:
            lab = f'<div class="lab" style="left:120px;top:16px">{X.rich(st.get("k", ""))}</div>'
            num = roll_html(v, npx, "roll sv", f"position:absolute;left:112px;top:{54 - 0.19 * npx:.0f}px;color:{col}")
            nw = num_w(v, npx)
            un = (f'<div class="un" style="left:{112 + nw + 22:.0f}px;top:{54 + npx * 0.71 - 52:.0f}px"><span>{X.rich(st.get("unit", ""))}</span></div>'
                  f'<div class="un" style="right:34px;top:16px"><em class="{tone}">{X.rich(st.get("note", ""))}</em></div>')
            sn = f'<div class="lab" style="left:26px;top:{sh / 2 - 16:.0f}px;color:{MUTED}">{k + 1:02d}</div>'
        else:
            lab = f'<div class="lab" style="left:30px;top:34px">{k + 1:02d} · {X.rich(st.get("k", ""))}</div>'
            num = roll_html(v, npx, "roll sv", f"position:absolute;left:30px;top:{150 - 0.19 * npx:.0f}px;color:{col}")
            un = f'<div class="un" style="left:34px;top:{150 + npx * 0.71 + 30:.0f}px"><span>{X.rich(st.get("unit", ""))}</span><em class="{tone}">{X.rich(st.get("note", ""))}</em></div>'
            sn = ""
        out += (f'<div class="tk stb s{k}" style="left:{x}px;top:{y}px;width:{sw}px;height:{sh}px"><i class="r1"></i><i class="r2"></i>'
                f'{holes}{sn}{lab}{num}{un}</div>')
    inst = f'<div class="sm">{out}</div>'
    s, box = page(X, b, cid, t, d, inst)
    live_pre = "REC"
    X.used_text.update(live_pre + "END")
    t0 = t + 0.2
    tend = t0
    for k, st in enumerate(stubs):
        tk = t0 + k * 0.32
        X.tw(f'tl.fromTo("{s} .stb.s{k}", {{clipPath:"{"inset(0% 0% 0% 100%)" if P else "inset(100% 0% 0% 0%)"}", x:{60 if P else 0}, y:{0 if P else 40}}}, '
             f'{{clipPath:"inset(0% 0% 0% 0%)", x:0, y:0, duration:0.38, ease:"power4.out", immediateRender:true}}, {tk:.3f});')
        tend = roll(X, f"{s} .stb.s{k} .sv", tk + 0.2, str(st.get("v", "")), 12, 2)
        X.tw(f'tl.from("{s} .stb.s{k} .un", {{opacity:0, x:-16, duration:0.25, ease:"power3.out"}}, {tend:.3f});')
    tcl = max(tend + 0.5, t + d - 1.6)
    _brackets_to(X, tcl, 0.3, 40, "back.out(2)")
    # the status row and the source step aside so the closed brackets frame them instead of crossing them
    X.tw(f'tl.to("{s} .st .ix", {{x:60, duration:0.3, ease:"power3.out"}}, {tcl:.3f}); tl.to("{s} .st .lv", {{x:-60, duration:0.3, ease:"power3.out"}}, {tcl:.3f});')
    X.tw(f'tl.to("{s} .src", {{x:60, duration:0.3, ease:"power3.out"}}, {tcl:.3f});')
    type_in(X, f"{s} .lvt", "END", tcl + 0.05, 2)
    X.sfx(tcl, "lock")


# ---------------------------------------------------------------- legacy scenes keep their names; new instruments join
SCENES = {"title": title, "compare": compare, "statement": statement, "number": number, "quote": quote, "outro": outro,
          "ticket": ticket, "stack": stack, "gauge": gauge, "diff": diff, "scope": scope, "matrix": matrix, "summary": summary}
STYLE["css"] = ("#root.v.st-hud .fx .rk .rk-v { margin-right:48px; }   /* 9:16: ranking values clear of the right-hand buttons */\n"
                # the subtitle: a panel plate with a 3 px brass bar, left aligned (9:16 x 100–960, y 1384–1460)
                ".st-hud .clip.cap .cp { display:block; text-align:left; border-left:3px solid #e8b85a; line-height:54px; letter-spacing:.02em;"
                " box-shadow:inset 0 1px 0 rgba(58,62,70,.9); }\n"
                "#root.v.st-hud .clip.cap { padding-left:100px; padding-right:120px; z-index:50 !important; }\n"
                "#root.h.st-hud { --cap-bottom:166px; }\n"
                "#root.h.st-hud .clip.cap { padding-left:100px; padding-right:1120px; }\n"
                "#root.h.st-hud .clip.cap .cp { font-size:40px; line-height:50px; }\n")


# ---------------------------------------------------------------- effect pages (aefx FX_FRAME)
# A shared effect rendered in this style sits inside the same instrument panel: the 60 px hairline grid with its radial
# lift, the four brass viewfinder brackets, a status row (numbered capsule · topic · effect id on the left, a REC
# timecode that ticks on the right), the scan line, the spoken line on the brass-barred panel plate and the source on a
# tick ruler. Nodes, ranking slabs and cards inside effects turn into panel pieces.
HF_CSS = r"""
.st-hud .fx[style*="background:var(--bg)"]::before { content:''; position:absolute; inset:0; z-index:-1; pointer-events:none; background:
  linear-gradient(color-mix(in srgb, var(--fg) 4%, transparent) 1px, transparent 1px) 0 0/60px 60px,
  linear-gradient(90deg, color-mix(in srgb, var(--fg) 4%, transparent) 1px, transparent 1px) 0 0/60px 60px,
  radial-gradient(ellipse 72% 58% at 50% 50%, color-mix(in srgb, var(--fg) 4%, transparent), transparent 78%); }
.hf { pointer-events:none; }
.hf .hf-vf { position:absolute; left:40px; right:40px; top:36px; bottom:36px; }
.hf .hf-vf i { position:absolute; width:48px; height:48px; border:3px solid color-mix(in srgb, var(--accent) 60%, transparent); }
.hf .hf-vf i:nth-child(1) { left:0; top:0; border-right:0; border-bottom:0; transform-origin:0 0; } .hf .hf-vf i:nth-child(2) { right:0; top:0; border-left:0; border-bottom:0; transform-origin:100% 0; }
.hf .hf-vf i:nth-child(3) { left:0; bottom:0; border-right:0; border-top:0; transform-origin:0 100%; } .hf .hf-vf i:nth-child(4) { right:0; bottom:0; border-left:0; border-top:0; transform-origin:100% 100%; }
.hf .hf-cps { position:absolute; left:100px; top:50px; display:flex; align-items:center; gap:14px; height:44px; }
.hf .hf-no { height:40px; padding:0 12px; border:2px solid var(--accent); color:var(--accent); display:grid; place-items:center;
  font-family:var(--f-num); font-weight:700; font-size:30px; line-height:1; }
.hf .hf-tx { display:flex; align-items:baseline; gap:14px; }
.hf .hf-tx b { font-family:var(--f-body); font-weight:700; font-size:28px; line-height:1; color:var(--fg); letter-spacing:.04em; white-space:nowrap; }
.hf .hf-tx em { font-family:var(--f-mono); font-style:normal; font-size:22px; letter-spacing:.18em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.hf .hf-rd { position:absolute; right:100px; top:56px; text-align:right; font-family:var(--f-mono); font-size:22px; line-height:1.4; letter-spacing:.14em; color:var(--muted); text-transform:uppercase; white-space:nowrap; }
.hf .hf-rd b { color:#ffd98a; font-weight:500; } .hf .hf-rd .rec { display:inline-block; width:12px; height:12px; background:#ff5a4d; margin-right:10px; }
.hf .hf-scan { position:absolute; left:46px; right:46px; top:0; height:2px; background:color-mix(in srgb, var(--accent) 25%, transparent); }
.hf .hf-cap { position:absolute; left:100px; right:100px; bottom:78px; display:flex; justify-content:flex-start; }
.hf .hf-tkt { position:relative; max-width:860px; padding:10px 26px 12px; background:rgba(17,19,23,.92); border-left:3px solid #e8b85a; box-shadow:inset 0 1px 0 #3a3e46; text-align:left; }
.hf .hf-line { position:relative; font-family:var(--f-body); font-weight:700; line-height:1.3; color:#f1ede4; letter-spacing:.02em; white-space:nowrap; }
.hf .hf-line .em .emt { color:#ffd98a; }
.hf .hf-line .em .emb { display:none; }
.hf .hf-ft { position:absolute; left:100px; right:100px; bottom:22px; height:40px; }
.hf .hf-ft .hf-rule { position:absolute; left:0; right:0; bottom:0; height:12px; opacity:.7; background:
  repeating-linear-gradient(90deg, var(--muted) 0 1px, transparent 1px 24px) left bottom/100% 6px no-repeat,
  repeating-linear-gradient(90deg, var(--muted) 0 2px, transparent 2px 120px) left bottom/100% 12px no-repeat,
  linear-gradient(var(--muted), var(--muted)) left bottom/100% 1px no-repeat; }
.hf .hf-ft .hf-fr { position:absolute; left:0; right:0; bottom:18px; display:flex; justify-content:space-between; gap:30px;
  font-family:var(--f-body); font-size:22px; color:var(--muted); white-space:nowrap; }
.hf .hf-ft .hf-fr > span { overflow:hidden; text-overflow:ellipsis; min-width:0; }
.hf .hf-ft .hf-fr > span:first-child::before { content:'▸ '; color:var(--accent); }
#root.v .hf .hf-vf { left:60px; right:60px; top:200px; bottom:400px; }
#root.v .hf .hf-cps { left:100px; top:212px; }
#root.v .hf .hf-rd { right:100px; top:210px; font-size:22px; }
#root.v .hf .hf-scan { left:66px; right:66px; }
#root.v .hf .hf-cap { left:100px; right:120px; bottom:460px; }
#root.v .hf .hf-tkt { max-width:860px; } #root.v .hf .hf-line { white-space:normal; word-break:break-all; }
#root.v .hf .hf-ft { left:100px; right:120px; bottom:auto; top:1466px; height:46px; }
#root.v .hf .hf-ft .hf-fr { flex-direction:column; gap:0; bottom:10px; } #root.v .hf .hf-ft .hf-fr > span { line-height:1.4; }
/* effect internals */
.st-hud .fx .rk .rk-in { background:#111317; box-shadow:inset 0 0 0 1px #2a2d33, inset 0 1px 0 #3a3e46; border-radius:999px; }
.st-hud .fx .rk .rk-r.top .rk-in { background:#ffd98a; box-shadow:inset 0 0 0 1px #ffd98a; }
.st-hud .fx .rk .rk-r.top .rk-no, .st-hud .fx .rk .rk-r.top .rk-nm, .st-hud .fx .rk .rk-r.top .rk-v, .st-hud .fx .rk .rk-r.top .rk-sb { color:#14110a; }
.st-hud .fx .wpe-n, .st-hud .rg-n { background:#111317; color:var(--fg); border-radius:0; box-shadow:inset 0 0 0 1px #2a2d33, inset 0 1px 0 #3a3e46; }
.st-hud .fx .wpe-n.person { border-radius:99vmin; }
.st-hud .fx .wpe-n.root { background:#ffd98a; color:#14110a; box-shadow:none; }
.st-hud .rg-n em { color:color-mix(in srgb, var(--fg) 55%, transparent); }
.st-hud .fx .dtr .dtr-b { border-radius:0; }
.st-hud .fx .nf .nf-band, .st-hud .fx .nf .nf-tk { border-radius:0; }
"""


def FX_FRAME(X, cid, t, d, p, k):
    X.css("hud-fx", HF_CSS)
    P = X.portrait
    i, n = X.beat["i"] + 1, X.beat["n"]
    host = bool(p.get("host"))
    rd_pos = ' style="right:330px"' if (host and P) else ""                     # 9:16: the presenter sits top-right
    ft_pad = ' style="padding-right:330px"' if (host and not P) else ""         # 16:9: the presenter sits bottom-right
    X.used_text.update(f"{i:02d}{X.channel} · CH09RECT+0123456789.▸ ")
    inner = ('<div class="hf-vf"><i></i><i></i><i></i><i></i></div><i class="hf-scan"></i>'
             f'<div class="hf-cps"><span class="hf-no">{i:02d}</span><span class="hf-tx"><b>{k["topic"]}</b><em>{k["fxid"]}</em></span></div>'
             f'<div class="hf-rd"{rd_pos}><i class="rec"></i>REC <b class="hf-tc">T+00.0</b></div>'
             f'<div class="hf-cap"><div class="hf-tkt"><div class="hf-line" style="font-size:{max(42 if P else 40, k["cap_px"])}px">{k["cap"]}</div></div></div>'
             f'<div class="hf-ft"><div class="hf-fr"{ft_pad}><span>{k["foot"]}</span><span>{k["src"]}</span></div>' + ('' if P else '<i class="hf-rule"></i>') + '</div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx hf{' photo' if k['photo'] else ''}", 30, track=20, sty=k["sty"])
    s = f"#{cid}c"
    X.tw(f'tl.from("{s} .hf-vf i", {{scale:1.45, opacity:0, duration:0.4, ease:"expo.out", stagger:0.04}}, {t:.3f});')
    X.tw(f'tl.from("{s} .hf-cps", {{x:-30, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.04:.3f});')
    X.tw(f'tl.from("{s} .hf-rd, {s} .hf-ft", {{opacity:0, duration:0.3, stagger:0.05}}, {t + 0.08:.3f});')
    X.tw(f'tl.fromTo("{s} .hf-tkt", {{scaleX:0.05, transformOrigin:"0% 50%"}}, {{scaleX:1, duration:0.28, ease:"expo.out", immediateRender:true}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .hf-line", {{x:-16, opacity:0, duration:0.3, ease:"power3.out"}}, {t + 0.16:.3f});')
    y0, y1 = (206, 1514) if P else (42, X.H - 42)
    X.tw(f'tl.fromTo("{s} .hf-scan", {{y:{y0}}}, {{y:{y1}, duration:{max(d, 0.5):.2f}, ease:"none", immediateRender:true}}, {t:.3f});')
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .hf-tc"); tl.to(o, {{v:{d:.2f}, duration:{d:.2f}, ease:"none", '
         f'onUpdate:()=>{{el.textContent="T+"+o.v.toFixed(1).padStart(4,"0");}}}}, {t:.3f});}})();')
