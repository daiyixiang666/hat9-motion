"""quote — 金句 / 结论。大字、留白、关键词强调。
params: text ("真正拉开差距的，|是你知道哪一张*不能要*"), by, image (可选，压暗做底), at_em
style S['quote']: layout = center | left | lower ; mark (是否画引号)
"""

CSS = """
.s-quote .bgimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.s-quote .veil { position:absolute; inset:0; background:var(--veil, rgba(0,0,0,.6)); }
.s-quote .box { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; gap:28px; padding:0 var(--pad, 160px); }
.s-quote .q { font-family:var(--f-quote, var(--f-display)); font-weight:var(--quote-weight, var(--display-weight, 700)); font-size:var(--quote-size, 96px); line-height:1.25; color:var(--fg); letter-spacing:var(--display-tracking, 0); }
.s-quote .qmk { font-family:var(--f-latin, Georgia, serif); font-size:220px; line-height:.6; height:90px; color:var(--accent); }
.s-quote .by { font-family:var(--f-mono, var(--f-body)); font-size:26px; color:var(--muted); letter-spacing:.2em; }
.s-quote .L-center { align-items:center; text-align:center; }
.s-quote .L-lower { justify-content:flex-end; padding-bottom:200px; }
#root.v .s-quote .box { padding:0 70px; } #root.v .s-quote .q { font-size:calc(var(--quote-size, 96px) * .8); }
"""


def build(b, X, t, d, cid):
    o = X.S.get("quote", {})
    lay = o.get("layout", "center")
    X.css("s-quote", CSS)
    img = f'<div class="cam"><img class="bgimg" src="{X.asset(b["image"])}" alt=""></div><div class="veil"></div>' if b.get("image") and o.get("image", True) else ""
    mk = '<div class="qmk">“</div>' if o.get("mark", False) else ""
    by = f'<div class="by">{X.rich(b["by"])}</div>' if b.get("by") else ""
    X.clip(cid, t, d, f'{img}<div class="box L-{lay}">{mk}<div class="q">{X.rich(b["text"], split="chars")}</div>{by}</div>', "scene s-quote", 2)
    if img:
        X.enter(f"#{cid} .cam", t, "media", dur=1.0); X.camera(f"#{cid} .cam", t, d, o.get("camera"))
    X.enter(f"#{cid} .qmk", t, "accent", verb="fade")
    n = len(str(b["text"]).replace("*", "").replace("|", ""))
    st = min(0.05, max(0.018, (d * 0.45) / max(n, 1)))
    X.enter(f"#{cid} .q .c", t + 0.15, "quote", verb=o.get("verb", X.M.get("quote", "blur")), stagger=st, dur=0.5)
    X.sfx(t + 0.15, "line")
    X.emph(f"#{cid} .q", X.T(b.get("at_em"), t) or t + 0.15 + n * st + 0.1)
    X.enter(f"#{cid} .by", t + 0.15 + n * st + 0.3, "text", verb="fade")
