"""compare — A / B 对比（同一个工具，两种结果）。
params: left:{img,label,note}, right:{img,label,note,stickers:[..]}, chip, verdict: left|right (赢家),
        at_left, at_right, at_stickers, at_chip, at_verdict (都可写 "@关键词")
style S['compare']: variant = halves | cards | windows | float ; tilt (cards 的倾斜度) ; tape (cards 贴胶带)
"""

CSS = """
.s-compare .side { position:absolute; overflow:hidden; }
.s-compare .side img { width:100%; height:100%; object-fit:cover; display:block; }
.s-compare .lab { position:absolute; font-family:var(--f-display); font-weight:var(--display-weight, 700); font-size:var(--lab-size, 46px); color:var(--lab-fg, var(--fg));
  background:var(--lab-bg, rgba(0,0,0,.6)); padding:8px 26px; letter-spacing:.06em; white-space:nowrap; border-radius:var(--lab-radius, 0); }
.s-compare .note { position:absolute; font-family:var(--f-mono, var(--f-body)); font-size:22px; color:var(--muted); letter-spacing:.12em; }
.s-compare .stk { position:absolute; font-family:var(--f-display); font-weight:900; font-size:42px; color:#fff; background:#ff2d2d; padding:6px 18px; border-radius:10px; box-shadow:0 6px 0 #a80000; white-space:nowrap; }
.s-compare .chip { position:absolute; left:50%; top:var(--chip-top, 56px); transform:translateX(-50%); font-family:var(--f-body); font-weight:700; font-size:30px;
  color:var(--chip-fg, var(--bg)); background:var(--chip-bg, var(--fg)); padding:10px 28px; border-radius:var(--chip-radius, 40px); white-space:nowrap; z-index:3; }
.s-compare .dim { position:absolute; inset:0; background:rgba(0,0,0,.62); opacity:0; }
.s-compare .x { position:absolute; left:50%; top:50%; width:46%; aspect-ratio:1; transform:translate(-50%,-50%); }
.s-compare .x i { position:absolute; left:-10%; right:-10%; top:50%; height:10px; margin-top:-5px; background:var(--alert, #e5484d); border-radius:5px; transform-origin:0 50%; }
.s-compare .x i:first-child { transform:rotate(45deg); } .s-compare .x i:last-child { transform:rotate(-45deg); }
/* halves */
.s-compare.v-halves .side { top:0; bottom:0; width:50%; }
.s-compare.v-halves .A { left:0; border-right:4px solid var(--bg); } .s-compare.v-halves .B { right:0; }
.s-compare.v-halves .lab { left:50%; top:150px; transform:translateX(-50%); }
.s-compare.v-halves .note { left:50%; bottom:150px; transform:translateX(-50%); }
#root.v .s-compare.v-halves .side { left:0; right:0; width:auto; height:50%; } #root.v .s-compare.v-halves .A { top:0; bottom:auto; border-right:0; border-bottom:4px solid var(--bg); } #root.v .s-compare.v-halves .B { top:50%; }
#root.v .s-compare.v-halves .lab { top:60px; }
/* cards */
.s-compare.v-cards .side { top:50%; width:var(--card-w, 38%); aspect-ratio:3/2; border-radius:var(--radius, 0); box-shadow:var(--shadow, 0 30px 80px rgba(0,0,0,.45)); border:var(--card-border, 0); background:var(--card, #fff); padding:var(--card-pad, 0); }
.s-compare.v-cards .A { left:var(--card-x, 9%); transform:translateY(-50%) rotate(calc(var(--tilt, 0deg) * -1)); }
.s-compare.v-cards .B { right:var(--card-x, 9%); transform:translateY(-50%) rotate(var(--tilt, 0deg)); }
.s-compare.v-cards .lab { left:50%; bottom:-86px; transform:translateX(-50%); }
.s-compare.v-cards .side { overflow:visible; } .s-compare.v-cards .side .ph { position:relative; width:100%; height:100%; overflow:hidden; border-radius:inherit; }
#root.v .s-compare.v-cards .side { left:12%; right:12%; width:auto; } #root.v .s-compare.v-cards .A { top:26%; } #root.v .s-compare.v-cards .B { top:66%; }
/* float: two panels hanging in 3D space, facing each other */
.s-compare.v-float .stage { perspective:1600px; }
.s-compare.v-float .side { top:50%; width:38%; aspect-ratio:3/2; overflow:visible; transform-style:preserve-3d; }
.s-compare.v-float .ph { position:absolute; inset:0; overflow:hidden; border-radius:var(--radius, 6px); border:1px solid var(--float-border, rgba(255,255,255,.35)); box-shadow:0 40px 120px rgba(0,0,0,.7); }
.s-compare.v-float .A { left:8%; transform:translateY(-50%) rotateY(18deg); } .s-compare.v-float .B { right:8%; transform:translateY(-50%) rotateY(-18deg); }
.s-compare.v-float .lab { left:0; bottom:-74px; background:none; padding:0; font-weight:300; letter-spacing:.24em; }
#root.v .s-compare.v-float .side { left:14%; right:14%; width:auto; } #root.v .s-compare.v-float .A { top:28%; transform:translateY(-50%) rotateX(12deg); } #root.v .s-compare.v-float .B { top:68%; transform:translateY(-50%) rotateX(-12deg); }
.s-compare .tape { position:absolute; left:50%; top:-22px; width:150px; height:44px; margin-left:-75px; background:var(--tape, rgba(240,226,180,.82)); transform:rotate(-3deg); box-shadow:0 2px 4px rgba(0,0,0,.15); z-index:4; }
/* windows */
.s-compare.v-windows .side { top:50%; width:40%; aspect-ratio:4/3; transform:translateY(-50%); background:var(--card, #111); border:1px solid var(--line); border-radius:var(--radius, 10px); overflow:hidden; }
.s-compare.v-windows .A { left:7%; } .s-compare.v-windows .B { right:7%; }
.s-compare.v-windows .bar { height:44px; display:flex; align-items:center; gap:9px; padding:0 16px; border-bottom:1px solid var(--line); font-family:var(--f-mono); font-size:18px; color:var(--muted); }
.s-compare.v-windows .bar b { width:12px; height:12px; border-radius:50%; background:var(--line); display:inline-block; }
.s-compare.v-windows .ph { position:absolute; top:44px; left:0; right:0; bottom:0; overflow:hidden; }
.s-compare.v-windows .lab { left:16px; bottom:16px; }
"""


def side(X, cls, s, variant):
    img = f'<img src="{X.asset(s["img"])}" alt="">' if s.get("img") else ""
    lab = f'<div class="lab">{X.rich(s["label"])}</div>' if s.get("label") else ""
    note = f'<div class="note">{X.rich(s["note"])}</div>' if s.get("note") else ""
    stk = "".join(f'<div class="stk" style="{pos}">{X.rich(w)}</div>' for w, pos in zip(s.get("stickers", []),
                  ["right:6%;top:18%;transform:rotate(-8deg)", "left:6%;bottom:26%;transform:rotate(5deg);background:#ff7a00;box-shadow:0 6px 0 #a34d00", "right:8%;bottom:16%;transform:rotate(7deg)"]))
    if variant == "windows":
        bar = f'<div class="bar"><b></b><b></b><b></b>&nbsp; {X.rich(s.get("file", "output.png"))}</div>'
        return f'<div class="side {cls}">{bar}<div class="ph">{img}<div class="dim"></div>{stk}</div>{lab}{note}</div>'
    if variant in ("cards", "float"):
        tape = '<i class="tape"></i>' if X.S.get("compare", {}).get("tape") else ""
        return f'<div class="side {cls}">{tape}<div class="ph">{img}<div class="dim"></div>{stk}</div>{lab}{note}</div>'
    return f'<div class="side {cls}">{img}<div class="dim"></div>{stk}{lab}{note}</div>'


def build(b, X, t, d, cid):
    o = X.S.get("compare", {})
    v = o.get("variant", "halves")
    X.css("s-compare", CSS)
    L, R = b["left"], b["right"]
    chip = f'<div class="chip">{X.rich(b["chip"])}</div>' if b.get("chip") else ""
    x = '<div class="x"><i></i><i></i></div>' if b.get("cross") else ""
    X.clip(cid, t, d, side(X, "A", L, v) + side(X, "B", R, v) + chip + x, f"scene s-compare v-{v}", 2,
           sty=f'--tilt:{o.get("tilt", 0)}deg')
    # both sides land at once (no empty frame); each label lands when the narration names it
    ta, tb = X.T(b.get("at_left"), t) or t + 0.4, X.T(b.get("at_right"), t) or t + min(1.6, d * 0.35)
    ia, ib = ("left", "right") if v == "halves" else ("rise", "rise")
    X.enter(f"#{cid} .A", t, "media", verb=o.get("in_a", ia), dur=0.7)
    X.enter(f"#{cid} .B", t + 0.12, "media", verb=o.get("in_b", ib), dur=0.7)
    X.sfx(t, "enter")
    for k, s in (("A", L), ("B", R)):
        tt = ta if k == "A" else tb
        X.camera(f"#{cid} .{k} img", t, d, o.get("camera", "push"))
        X.enter(f"#{cid} .{k} .lab", tt, "accent", verb=o.get("lab_verb", "rise"))
        X.sfx(tt, "pop")
        X.enter(f"#{cid} .{k} .note", tt + 0.3, "text", verb="fade")
    ts = X.T(b.get("at_stickers"), t) or tb + 0.8
    X.enter(f"#{cid} .stk", ts, "accent", verb="pop", stagger=0.14, dur=0.4)
    for i in range(len(R.get("stickers", []))): X.sfx(ts + i * 0.14, "pop")
    X.enter(f"#{cid} .chip", X.T(b.get("at_chip"), t) or t + 0.3, "accent", verb=o.get("chip_verb", "drop" if v == "cards" else "rise"))
    tv = X.T(b.get("at_verdict"), t)
    if tv is not None and b.get("verdict"):
        loser = "B" if b["verdict"] == "left" else "A"
        win = "A" if loser == "B" else "B"
        X.tw(f'tl.to("#{cid} .{loser} .dim", {{opacity:1, duration:0.5, ease:"power2.out"}}, {tv:.3f});')
        X.tw(f'tl.to("#{cid} .{loser} img", {{filter:"grayscale(1)", duration:0.5}}, {tv:.3f});')
        if v != "halves":
            X.tw(f'tl.to("#{cid} .{win}", {{scale:1.06, duration:0.6, ease:"power3.out"}}, {tv:.3f});')
        X.sfx(tv, "hit")
