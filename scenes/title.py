"""title — the hook / chapter card.
params: title (支持 *强调* 与 | 换行), kicker, sub, image, at_sub
style S['title']: layout = center | left | stack | bracket | card ;  image = full | frame | tv | none
"""

CSS = """
.s-title .bgimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.s-title .veil { position:absolute; inset:0; background:var(--veil, linear-gradient(180deg, rgba(0,0,0,.15), rgba(0,0,0,.55))); }
.s-title .box { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; gap:var(--title-gap, 22px); padding:0 var(--pad, 140px); }
.s-title .kick { font-family:var(--f-mono, var(--f-body)); font-size:var(--kick-size, 26px); letter-spacing:.28em; color:var(--muted); text-transform:uppercase; }
.s-title .ttl { font-family:var(--f-display); font-weight:var(--display-weight, 800); font-size:var(--title-size, 168px); line-height:1.02; letter-spacing:var(--display-tracking, -0.01em); color:var(--fg); }
.s-title .sub { font-size:var(--sub-size, 40px); color:var(--muted); font-weight:500; letter-spacing:.06em; }
.s-title .rule { width:120px; height:3px; background:var(--accent); transform-origin:0 50%; }
.s-title .L-center { align-items:center; text-align:center; }
.s-title .L-center .rule { transform-origin:50% 50%; }
.s-title .L-left { align-items:flex-start; justify-content:flex-end; padding-bottom:180px; }
.s-title .L-stack .ttl { font-size:var(--title-size, 220px); line-height:.92; }
.s-title .L-bracket { align-items:center; text-align:center; }
.s-title .L-bracket .ttl::before { content:'【'; color:var(--accent); margin-right:.08em; }
.s-title .L-bracket .ttl::after { content:'】'; color:var(--accent); margin-left:.08em; }
.s-title .L-card { align-items:center; }
.s-title .L-card .panel { background:var(--card, #fff); color:var(--card-fg, #111); border:var(--border, 0); border-radius:var(--radius, 0); box-shadow:var(--shadow, none); padding:46px 70px; display:flex; flex-direction:column; align-items:center; gap:14px; }
.s-title .L-card .ttl { color:var(--card-fg, #111); }
.s-title .L-chapter { align-items:center; text-align:center; gap:30px; }
.s-title .L-chapter .ttl { font-weight:300; letter-spacing:.32em; font-size:var(--title-size, 96px); margin-right:-.32em; }
.s-title .L-chapter .kick { letter-spacing:.5em; }
.s-title .L-lower { align-items:center; text-align:center; justify-content:flex-end; padding-bottom:210px; }
.s-title .L-poster { align-items:flex-start; justify-content:center; gap:0; }
.s-title .L-poster .ttl { font-size:var(--title-size, 260px); line-height:.9; letter-spacing:-0.03em; }
.s-title .frame { position:absolute; overflow:hidden; border-radius:var(--radius, 0); box-shadow:var(--shadow, none); }
.s-title.img-frame .frame { right:var(--pad, 140px); top:50%; width:46%; aspect-ratio:3/2; transform:translateY(-50%); }
.s-title.img-frame .box { right:50%; }
.s-title.img-tv .frame { left:50%; top:50%; width:62%; aspect-ratio:4/3; transform:translate(-50%,-50%); border-radius:48px / 40px; box-shadow:inset 0 0 80px rgba(0,0,0,.8), 0 30px 80px rgba(0,0,0,.5); }
.s-title .frame img { width:100%; height:100%; object-fit:cover; }
#root.v .s-title .box { padding:0 80px; }
#root.v .s-title .ttl { font-size:calc(var(--title-size, 168px) * .82); }
#root.v .s-title.img-frame .frame { left:80px; right:80px; width:auto; top:240px; transform:none; }
#root.v .s-title.img-frame .box { right:0; top:auto; height:55%; bottom:0; }
"""


def build(b, X, t, d, cid):
    o = X.S.get("title", {})
    lay, im = o.get("layout", "center"), o.get("image", "full")
    if not b.get("image"): im = "none"
    X.css("s-title", CSS)
    img = ""
    if im == "full":
        img = f'<div class="cam"><img class="bgimg" src="{X.asset(b["image"])}" alt=""></div><div class="veil"></div>'
    elif im in ("frame", "tv"):
        img = f'<div class="frame"><img class="cam" src="{X.asset(b["image"])}" alt=""></div>'
    kick = f'<div class="kick">{X.rich(b["kicker"])}</div>' if b.get("kicker") else ""
    sub = f'<div class="sub">{X.rich(b["sub"])}</div>' if b.get("sub") else ""
    ttl = f'<h1 class="ttl">{X.rich(b["title"], split="chars")}</h1>'
    rule = '<i class="rule"></i>' if o.get("rule", True) else ""
    body = f'{kick}{ttl}{sub}{rule}'
    if lay == "card": body = f'<div class="panel">{body}</div>'
    X.clip(cid, t, d, f'{img}<div class="box L-{lay}">{body}</div>', f"scene s-title img-{im}", 2)
    if img:
        X.enter(f"#{cid} .cam", t, "media", dur=0.9)
        X.camera(f"#{cid} .cam", t, d)
    X.enter(f"#{cid} .kick", t + 0.1, "text")
    X.enter(f"#{cid} .ttl .c", t + 0.18, "heading", stagger=o.get("stagger", 0.05))
    X.sfx(t + 0.18, "title")
    X.enter(f"#{cid} .rule", t + 0.5, "line", verb=o.get("rule_verb", "wipe"), dur=0.5)
    X.enter(f"#{cid} .sub", X.T(b.get("at_sub")) if b.get("at_sub") else t + 0.55, "text")
    X.emph(f"#{cid} .ttl", t + 0.7)
