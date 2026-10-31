"""statement — 一句观点，逐行上屏，关键词强调。
params: lines: ["差别不在*工具*", "在*判断*"] ; at: ["@差别", "@在判断"] (每行出现时间，可省)；image（可选背景）; label（小标签）
style S['statement']: layout = center | left ; mode = stack (lines accumulate) | swap (each line replaces the last: line-swap)
"""

CSS = """
.s-statement .bgimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.s-statement .veil { position:absolute; inset:0; background:var(--veil, rgba(0,0,0,.55)); }
.s-statement .box { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; gap:var(--line-gap, 10px); padding:0 var(--pad, 140px); }
.s-statement .lbl { font-family:var(--f-mono, var(--f-body)); font-size:24px; letter-spacing:.24em; color:var(--muted); margin-bottom:22px; }
.s-statement .ln { font-family:var(--f-display); font-weight:var(--display-weight, 800); font-size:var(--stmt-size, 120px); line-height:1.12; letter-spacing:var(--display-tracking, 0); color:var(--fg); }
.s-statement .ln.mute { color:var(--muted); }
.s-statement .L-center { align-items:center; text-align:center; }
.s-statement .L-left { align-items:flex-start; }
.s-statement .mask { overflow:hidden; padding:.12em .25em .14em; margin:-.12em -.25em -.14em; }
.s-statement.m-swap .mask { position:absolute; left:var(--pad, 140px); right:var(--pad, 140px); top:50%; transform:translateY(-50%); }
.s-statement.m-swap .L-center .mask { text-align:center; }
#root.v .s-statement .box { padding:0 70px; }
#root.v .s-statement .ln { font-size:calc(var(--stmt-size, 120px) * .78); }
"""


def build(b, X, t, d, cid):
    o = X.S.get("statement", {})
    lay = o.get("layout", "center")
    X.css("s-statement", CSS)
    img = f'<div class="cam"><img class="bgimg" src="{X.asset(b["image"])}" alt=""></div><div class="veil"></div>' if b.get("image") else ""
    lbl = f'<div class="lbl">{X.rich(b["label"])}</div>' if b.get("label") else ""
    lines = b["lines"]
    split = "chars" if o.get("split", True) else None
    rows = "".join(f'<div class="mask"><div class="ln{" mute" if str(s).startswith("~") else ""}">{X.rich(str(s).lstrip("~"), split=split)}</div></div>' for s in lines)
    mode = o.get("mode", "stack")
    X.clip(cid, t, d, f'{img}<div class="box L-{lay}">{lbl}{rows}</div>', f"scene s-statement m-{mode}", 2)
    if img:
        X.enter(f"#{cid} .cam", t, "media", dur=0.8); X.camera(f"#{cid} .cam", t, d)
    X.enter(f"#{cid} .lbl", t, "text")
    at = b.get("at") or []
    span = min(d * 0.5, 0.45 * len(lines))
    for i in range(len(lines)):
        ti = X.T(at[i], t) if i < len(at) else t + 0.12 + i * span / max(len(lines), 1)
        sel = f"#{cid} .mask:nth-of-type({i + 1 + (1 if lbl else 0)}) .ln"
        verb = o.get("verb")
        if split: X.enter(sel + " .c", ti, "heading", verb=verb, stagger=o.get("stagger", 0.03))
        else: X.enter(sel, ti, "heading", verb=verb)
        X.sfx(ti, "line")
        X.emph(sel, ti + 0.35)
        if mode == "swap" and i + 1 < len(lines):   # old line leaves up through its mask as the next arrives
            tn = X.T(at[i + 1], t) if i + 1 < len(at) else t + 0.12 + (i + 1) * span / max(len(lines), 1)
            X.tw(f'tl.to("{sel}", {{yPercent:-115, duration:0.28, ease:"power3.in"}}, {max(ti + 0.3, tn - 0.3):.3f});')
