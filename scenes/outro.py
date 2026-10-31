"""outro — 柴犬主持人收尾 + 账号名 + 一句定位。柴犬从角落走到台前（若 meta.mascot 存在）。
params: title ("第九顶帽子"), sub ("大家都在用 AI，结果凭什么是你的"), cta ("关注，一起练判断")
style S['outro']: layout = right | center ; mascot = {x, y, scale} 柴犬在收尾时的位置（相对角落原位的位移）
"""

CSS = """
.s-outro .box { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; gap:22px; padding:0 var(--pad, 140px); }
.s-outro .L-right { align-items:flex-start; padding-left:52%; }
.s-outro .L-center { align-items:center; text-align:center; }
.s-outro .ttl { font-family:var(--f-display); font-weight:var(--display-weight, 800); font-size:var(--outro-size, 120px); line-height:1.05; color:var(--fg); }
.s-outro .sub { font-size:40px; color:var(--muted); font-weight:500; }
.s-outro .cta { margin-top:24px; font-family:var(--f-body); font-weight:700; font-size:30px; color:var(--chip-fg, var(--bg)); background:var(--chip-bg, var(--accent)); padding:12px 30px; border-radius:var(--chip-radius, 40px); }
#root.v .s-outro .L-right { padding:0 80px; justify-content:flex-start; padding-top:300px; align-items:center; text-align:center; }
"""


def build(b, X, t, d, cid):
    o = X.S.get("outro", {})
    lay = o.get("layout", "right")
    X.css("s-outro", CSS)
    sub = f'<div class="sub">{X.rich(b["sub"])}</div>' if b.get("sub") else ""
    cta = f'<div class="cta">{X.rich(b["cta"])}</div>' if b.get("cta") else ""
    X.clip(cid, t, d, f'<div class="box L-{lay}"><div class="ttl">{X.rich(b.get("title", "第九顶帽子"), split="chars")}</div>{sub}{cta}</div>', "scene s-outro", 2)
    X.enter(f"#{cid} .ttl .c", t + 0.25, "heading", stagger=0.05)
    X.enter(f"#{cid} .sub", t + 0.6, "text")
    X.enter(f"#{cid} .cta", t + 0.9, "accent", verb="pop")
    X.sfx(t + 0.25, "title")
    if X.v.get("meta", {}).get("mascot") and X.S.get("outro", {}).get("move", True):
        m = o.get("mascot_portrait" if X.portrait else "mascot", {"x": 420, "y": -260, "scale": 1.7})
        X.tw(f'tl.to("#mascot", {{x:{m["x"]}, y:{m["y"]}, scale:{m["scale"]}, transformOrigin:"50% 100%", duration:0.8, ease:"expo.out"}}, {t:.3f});')
        X.sfx(t, "mascot")
