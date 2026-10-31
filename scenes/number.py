"""number — 一个数字，画出来而不是念出来。
params: value (90), unit ("%"), from (0), label ("的人只会多生成几张"), at (数字开始滚动), sub,
        viz: dots | bar | split | none   (dots = 10×10 点阵；hl = 剩下几个点用强调色；split = 一根 100% 横条按 value / 剩余 切开，两端各带标签 split_labels)
style S['number']: layout = center | left ; viz 默认
"""

CSS = """
.s-number .box { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:110px; padding:0 var(--pad, 140px); }
.s-number .txt { display:flex; flex-direction:column; gap:18px; }
.s-number .val { font-family:var(--f-num, var(--f-display)); font-weight:var(--num-weight, 800); font-size:var(--num-size, 300px); line-height:.9; color:var(--num-fg, var(--accent)); letter-spacing:-0.03em; font-variant-numeric:tabular-nums; white-space:nowrap; }
.s-number .val small { font-size:.42em; margin-left:.06em; color:var(--num-unit, var(--fg)); }
.s-number .lbl { font-family:var(--f-display); font-size:var(--numlbl-size, 56px); font-weight:var(--display-weight, 700); color:var(--fg); max-width:820px; line-height:1.25; }
.s-number .sub { font-family:var(--f-mono, var(--f-body)); font-size:22px; color:var(--muted); letter-spacing:.14em; }
.s-number .dots { display:grid; grid-template-columns:repeat(10, 40px); gap:16px; }
.s-number .dots i { width:40px; height:40px; border-radius:var(--dot-radius, 50%); background:var(--line); }
.s-number .dots i.on { background:var(--dot-on, var(--muted)); } .s-number .dots i.hl { background:var(--accent); }
.s-number .bar { width:760px; height:56px; background:var(--line); position:relative; border-radius:var(--radius, 0); overflow:hidden; }
.s-number .bar b { position:absolute; left:0; top:0; bottom:0; background:var(--accent); transform-origin:0 50%; }
.s-number .L-center { flex-direction:column; gap:50px; text-align:center; } .s-number .L-center .txt { align-items:center; }
.s-number .split { width:1640px; display:flex; flex-direction:column; gap:22px; }
.s-number .split .row { display:flex; height:120px; gap:6px; }
.s-number .split .seg { position:relative; height:100%; background:var(--split-a, var(--muted)); transform-origin:0 50%; }
.s-number .split .seg.b { background:var(--accent); }
.s-number .split .tags { display:flex; justify-content:space-between; font-family:var(--f-display); font-size:40px; font-weight:700; }
.s-number .split .tags .b { color:var(--accent); }
.s-number.viz-split .box { flex-direction:column; align-items:flex-start; justify-content:center; gap:60px; }
#root.v .s-number .split { width:900px; }
#root.v .s-number .box { flex-direction:column; gap:70px; text-align:center; } #root.v .s-number .txt { align-items:center; }
#root.v .s-number .dots { grid-template-columns:repeat(10, 52px); } #root.v .s-number .dots i { width:52px; height:52px; }
"""


def build(b, X, t, d, cid):
    o = X.S.get("number", {})
    lay, viz = o.get("layout", "left"), b.get("viz", o.get("viz", "dots"))
    X.css("s-number", CSS)
    v, f0, unit = float(b["value"]), float(b.get("from", 0)), b.get("unit", "")
    X.used_text.update("0123456789.%" + unit)
    val = f'<div class="val"><span class="n">{X.rich(b.get("from_text", int(f0)))}</span><small>{X.rich(unit)}</small></div>'
    lbl = f'<div class="lbl">{X.rich(b["label"])}</div>' if b.get("label") else ""
    sub = f'<div class="sub">{X.rich(b["sub"])}</div>' if b.get("sub") else ""
    vz = ""
    if viz == "dots":
        n_on, hl = int(round(v)), int(b.get("hl", 0))
        cells = []
        for i in range(100):
            k = "on" if i < n_on else ("hl" if i < n_on + hl else "")
            cells.append(f'<i class="{k}"></i>')
        vz = f'<div class="dots">{"".join(cells)}</div>'
    elif viz == "bar":
        vz = f'<div class="bar"><b style="width:{v}%"></b></div>'
    elif viz == "split":
        la, lb = b.get("split_labels", ["", ""])
        vz = (f'<div class="split"><div class="row"><i class="seg a" style="width:{v}%"></i><i class="seg b" style="width:{100 - v}%"></i></div>'
              f'<div class="tags"><span class="a">{X.rich(la)}</span><span class="b">{X.rich(lb)}</span></div></div>')
    X.clip(cid, t, d, f'<div class="box L-{lay}"><div class="txt">{sub}{val}{lbl}</div>{vz}</div>', f"scene s-number viz-{viz}", 2)
    ta = X.T(b.get("at"), t) or t + 0.2
    X.enter(f"#{cid} .sub", t, "text")
    X.enter(f"#{cid} .val", t, "heading", verb=o.get("verb", "rise"))
    dec = int(b.get("decimals", 0))
    X.tw(f'(()=>{{const o={{v:{f0}}}; const el=document.querySelector("#{cid} .n"); tl.to(o, {{v:{v}, duration:{o.get("count", 1.1)}, ease:"power3.out", onUpdate:()=>{{el.textContent=o.v.toFixed({dec});}}}}, {ta:.3f});}})();')
    X.sfx(ta, "count")
    X.enter(f"#{cid} .lbl", ta + 0.3, "text")
    X.emph(f"#{cid} .lbl", ta + 0.7)
    if viz == "dots":
        X.tw(f'tl.from("#{cid} .dots i", {{scale:0, duration:0.25, ease:"back.out(2)", stagger:{{each:0.008, grid:[10,10], from:"start"}}}}, {ta:.3f});')
        if b.get("hl"):
            th = X.T(b.get("at_hl"), t) or ta + 1.2
            X.tw(f'tl.from("#{cid} .dots i.hl", {{backgroundColor:"rgba(0,0,0,0)", scale:1.6, duration:0.4, ease:"back.out(3)", stagger:0.05}}, {th:.3f});')
            X.sfx(th, "pop")
    elif viz == "bar":
        X.tw(f'tl.from("#{cid} .bar b", {{scaleX:0, duration:1.1, ease:"power3.out"}}, {ta:.3f});')
    elif viz == "split":
        X.tw(f'tl.from("#{cid} .seg.a", {{scaleX:0, duration:1.0, ease:"power3.out"}}, {ta:.3f});')
        th = X.T(b.get("at_hl"), t) or ta + 1.0
        X.tw(f'tl.from("#{cid} .seg.b", {{scaleX:0, duration:0.5, ease:"power3.out"}}, {th:.3f});')
        X.enter(f"#{cid} .tags .a", ta + 0.5, "text", verb="fade"); X.enter(f"#{cid} .tags .b", th + 0.2, "accent", verb="rise")
        X.sfx(th, "pop")
