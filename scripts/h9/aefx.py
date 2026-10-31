"""AE 动效库 —— re-creations of the most popular After Effects motion techniques as seekable HTML/CSS/SVG/GSAP.

Each effect: fx(X, cid, t, d, p) -> adds one clip (and its tweens) to the build.  p = params dict.
Works at any aspect: sizes are in vmin/% where it matters. Colours come from the style tokens.
Only generic techniques are re-created (no template designs or assets copied).
"""
import math

CSS = r"""
.fx { overflow:hidden; }
.fx > .stage { display:flex; align-items:center; justify-content:center; }
.fx i { font-style:normal; }
.fx .ln { display:block; overflow:hidden; padding:.08em .1em .14em; margin:-.08em -.1em -.14em; }
.fx .c, .fx .w { display:inline-block; will-change:transform; }
.fx .big { font-family:var(--f-display); font-weight:var(--display-weight, 800); font-size:var(--fx-size, 15vmin); line-height:1.05; color:var(--fg); letter-spacing:var(--display-tracking, 0); text-align:center; }
.fx .sub { font-family:var(--f-latin, var(--f-body)); font-size:2.2vmin; letter-spacing:.42em; color:var(--muted); text-transform:uppercase; margin-top:2.2vmin; text-align:center; }
.fx .col { display:flex; flex-direction:column; align-items:center; }
.fx-tag { position:absolute; left:4vmin; bottom:4vmin; font:500 1.6vmin/1.4 var(--f-mono, monospace); color:var(--muted); letter-spacing:.12em; text-transform:uppercase; }
.fx-tag b { color:var(--accent); font-weight:500; }
"""


def _chars(X, s, cls="c"):
    return "".join(f'<i class="{cls}">{X.rich(ch)}</i>' if ch.strip() else " " for ch in s)


def _tag(X, p):
    if not p.get("label"): return ""
    return f'<div class="fx-tag"><b>{X.rich(p["label"])}</b>{("　" + X.rich(p["ref"])) if p.get("ref") else ""}</div>'


# page themes for a beat ("theme": "paper" | "ink" | "red" | "lemon"): the effect inherits the colours through CSS variables
THEMES = {
    "paper": {"bg": "#f0ece3", "fg": "#111111", "muted": "#625d56", "accent": "#e2321f", "card": "#fbfaf6", "card-fg": "#111111", "line": "#d3ccbf"},
    "ink":   {"bg": "#121212", "fg": "#f3efe6", "muted": "#958f85", "accent": "#f6ce3a", "card": "#1d1c1a", "card-fg": "#f3efe6", "line": "#2c2a27"},
    "red":   {"bg": "#e2321f", "fg": "#fbfaf6", "muted": "rgba(255,255,255,.78)", "accent": "#111111", "card": "#fbfaf6", "card-fg": "#111111", "line": "rgba(255,255,255,.3)"},
    "lemon": {"bg": "#f6ce3a", "fg": "#111111", "muted": "#5b4a12", "accent": "#e2321f", "card": "#fbfaf6", "card-fg": "#111111", "line": "rgba(0,0,0,.2)"},
}
CTX_CSS = r"""
.ctx { pointer-events:none; }
.ctx .hd { position:absolute; left:96px; right:96px; top:40px; height:44px; display:flex; align-items:center; justify-content:space-between; border-bottom:2px solid var(--fg);
  font-family:var(--f-body); font-size:22px; color:var(--fg); }
.ctx .hd b { font-weight:900; letter-spacing:.04em; } .ctx .hd span { opacity:.7; margin-left:14px; }
.ctx .hd .fxid { font-family:var(--f-mono); font-size:18px; letter-spacing:.06em; background:var(--fg); color:var(--bg); padding:2px 10px; }
.ctx .cap { position:absolute; left:0; right:0; bottom:66px; text-align:center; }
.ctx .cap > span { display:inline-block; font-family:var(--f-body); font-weight:700; font-size:40px; line-height:1.3; color:var(--bg); background:var(--fg); padding:8px 24px 10px; border-radius:8px; max-width:80%; }
.ctx .cap .em .emt { background:#f6ce3a; color:#111; padding:0 .12em; } .ctx .cap .em .emb { display:none; }
.ctx .ft { position:absolute; left:96px; right:96px; bottom:22px; display:flex; justify-content:space-between; font-family:var(--f-mono); font-size:16px; color:var(--fg); opacity:.6; letter-spacing:.04em; }
.ctx.photo .hd, .ctx.photo .ft { color:#fff; border-color:rgba(255,255,255,.7); text-shadow:0 1px 8px rgba(0,0,0,.6); opacity:1; }
.ctx.photo .hd .fxid { background:#fff; color:#111; text-shadow:none; }
.ctx.photo .scrim { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.55), rgba(0,0,0,0) 18%, rgba(0,0,0,0) 72%, rgba(0,0,0,.6)); }
#root.v .ctx .hd { left:56px; right:56px; top:176px; } #root.v .ctx .ft { left:56px; right:56px; bottom:auto; top:1478px; }
#root.v .ctx .cap { bottom:auto; top:1330px; padding:0 56px; } #root.v .ctx .cap > span { font-size:44px; max-width:100%; }
"""
PHOTO = {"parallax", "portal", "mosaic", "callout", "match_cut", "plate"}


def _theme_style(p):
    th = THEMES.get(p.get("theme"))
    return (";".join(f"--{k}:{v}" for k, v in th.items()) + ";background:var(--bg)") if th else ""


def _context(X, cid, t, d, p):
    """the page around an effect, so a preview reads like a frame of a real 口播: header (show · topic · effect id),
    the spoken line as a caption with its keyword marked, and the effect's popularity as the footnote."""
    if not p.get("line"): return
    X.css("aefx-ctx", CTX_CSS)
    photo = p.get("fx") in PHOTO and not p.get("theme_over_photo")
    th = THEMES.get(p.get("theme"))
    sty = ";".join(f"--{k}:{v}" for k, v in th.items()) if th else ""
    fxid = p.get("fxid") or p.get("fx", "")
    foot = (X.rich(p["label"]) + ("　" + X.rich(p["ref"]) if p.get("ref") else "")) if p.get("label") else ""
    inner = (('<div class="scrim"></div>' if photo else "")
             + f'<div class="hd"><div><b>第九顶帽子</b><span>{X.rich(p.get("topic", ""))}</span></div><div class="fxid">{X.rich(fxid)}</div></div>'
             + f'<div class="cap"><span>{X.rich(p["line"])}</span></div><div class="ft"><div>{foot}</div><div>{X.rich(p.get("src", ""))}</div></div>')
    X.clip(f"{cid}c", t, d, inner, f"ctx{' photo' if photo else ''}", 30, track=20, sty=sty)
    if p.get("host"):    # the faceless host (talking shiba) in the corner, as a presenter would be
        src = X.v.get("meta", {}).get("host_video")
        if src:
            url = X.asset(src, "video")
            pos = "right:40px; top:236px; width:270px; height:270px" if X.portrait else "right:64px; top:auto; bottom:0; width:330px; height:330px"
            X.clip(f"{cid}m", t, d, "", "mascot mf-sticker", 31, track=21, tag="video",
                   attrs=f'src="{url}" muted playsinline data-media-start="{(t * 1.7) % 12:.3f}"', sty=f"left:auto; bottom:auto; {pos}")
            X.tw(f'tl.from("#{cid}m", {{scale:0.7, yPercent:12, opacity:0, transformOrigin:"50% 100%", duration:0.4, ease:"back.out(1.7)"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("#{cid}c .cap > span", {{y:16, opacity:0, duration:0.3, ease:"power3.out"}}, {t + 0.05:.3f});')


def _clip(X, cid, t, d, inner, p, extra_cls=""):
    X.css("aefx", CSS)
    tag = "" if p.get("line") else _tag(X, p)
    X.clip(cid, t, d, inner + tag, f"scene fx {extra_cls}", 3, sty=_theme_style(p))
    _context(X, cid, t, d, p)


# ------------------------------------------------------------------ text
def pop(X, cid, t, d, p):
    """逐字弹出 (Animation Composer 'Pop' / Bounce): scale 0 → 1.18 → 1, 1 frame stagger, back ease."""
    _clip(X, cid, t, d, f'<div class="col"><div class="big">{_chars(X, p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.tw(f'tl.from("#{cid} .big .c", {{scale:0, y:"0.2em", duration:0.42, ease:"back.out(2.6)", stagger:0.035}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, y:14, duration:0.6, ease:"power3.out"}}, {t + 0.45:.3f});')
    X.sfx(t + 0.1, "pop")


def mask_up(X, cid, t, d, p):
    """行遮罩上移 (the most-used title reveal): each line rises out of its own mask, expo.out."""
    lines = p["text"].split("|")
    rows = "".join(f'<span class="ln"><span class="w">{X.rich(s)}</span></span>' for s in lines)
    _clip(X, cid, t, d, f'<div class="col"><div class="big">{rows}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.tw(f'tl.from("#{cid} .ln .w", {{yPercent:115, duration:0.85, ease:"expo.out", stagger:0.12}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{yPercent:100, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.5:.3f});')
    X.tw(f'tl.to("#{cid} .ln .w", {{yPercent:-115, duration:0.45, ease:"power3.in", stagger:0.06}}, {t + d - 0.55:.3f});')
    X.sfx(t + 0.1, "enter")


def tracking(X, cid, t, d, p):
    """字距收拢 (Tracking In): glyphs start spread wide and drift together while sharpening — done with transforms
    (x offset ∝ distance from the centre), so it never snaps to whole pixels like letter-spacing would."""
    txt = p["text"]
    _clip(X, cid, t, d, f'<div class="col"><div class="big trk">{_chars(X, txt)}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    n = len([c for c in txt if c.strip()])
    X.tw(f'tl.from("#{cid} .trk .c", {{x:(i)=>(i-{(n - 1) / 2:.2f})*{p.get("spread", 90)}, opacity:0, filter:"blur(10px)", duration:1.6, ease:"power3.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .sub .c, #{cid} .sub", {{opacity:0, duration:0.8}}, {t + 0.9:.3f});')
    X.sfx(t, "whoosh_soft")


def blur_focus(X, cid, t, d, p):
    """模糊聚焦 (Don't quit 式): words arrive out of a heavy blur at different times, then lock sharp."""
    words = p["text"].split(" ")
    _clip(X, cid, t, d, f'<div class="big">{" ".join(f"<i class=w>{X.rich(w)}</i>" for w in words)}</div>', p)
    X.tw(f'tl.from("#{cid} .w", {{opacity:0, filter:"blur(28px)", scale:1.25, duration:0.9, ease:"power2.out", stagger:{{each:0.22, from:"random"}}}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")


def typewriter(X, cid, t, d, p):
    """打字机 + 光标: one glyph per 2 frames, blinking caret (deterministic blink on the timeline)."""
    _clip(X, cid, t, d, f'<div class="big tw" style="font-family:var(--f-mono)">{_chars(X, p["text"])}<i class="caret">▍</i></div>', p)
    n = len(p["text"])
    X.tw(f'tl.from("#{cid} .tw .c", {{display:"none", duration:0.01, stagger:0.066}}, {t + 0.2:.3f});')
    for k in range(int(d / 0.5)):
        X.tw(f'tl.set("#{cid} .caret", {{opacity:{k % 2}}}, {t + k * 0.5:.3f});')
    X.sfx(t + 0.2, "type")


def scramble(X, cid, t, d, p):
    """乱码解码 (Decoder / Scramble): every slot is a reel of random glyphs that steps (not slides) onto its real
    character, slots settling left→right. Pure transforms with a steps() ease, so it seeks in any order."""
    s = p["text"]; pool = p.get("pool", "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#$%&@")
    X.used_text.update(pool + s)
    k = 9
    slots = []
    for ch in s:
        reel = "".join(f'<i class="g">{X.rich(pool[X.rand.randrange(len(pool))])}</i>' for _ in range(k)) + f'<i class="f">{X.rich(ch)}</i>'
        slots.append(f'<span class="sc"><span class="rl">{reel}</span></span>')
    _clip(X, cid, t, d, f'<div class="big scr" style="font-family:var(--f-mono);display:flex">{"".join(slots)}</div>', p)
    X.css("aefx-sc", ".fx .sc { display:inline-block; height:1.1em; overflow:hidden; align-self:flex-start; contain:paint; } .fx .sc .rl { display:flex; flex-direction:column; } .fx .sc i { display:block; height:1.1em; font-style:normal; text-align:center; } .fx .sc .g { color:var(--accent); }")
    for i in range(len(s)):
        X.tw(f'tl.fromTo("#{cid} .sc:nth-child({i + 1}) .rl", {{yPercent:0}}, {{yPercent:{-100 * k / (k + 1):.3f}, duration:{0.5 + i * 0.07:.2f}, ease:"steps({k})"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "type")


def write_on(X, cid, t, d, p):
    """描边书写 → 填色 (Trim Paths on text / 手写签名): glyph outlines draw on, then the fill floods in."""
    txt = p["text"]
    X.used_text.update(txt)
    _clip(X, cid, t, d, f'<svg class="wo" viewBox="0 0 1000 300" preserveAspectRatio="xMidYMid meet" style="width:78%;height:auto;overflow:visible">'
                        f'<text x="500" y="215" text-anchor="middle" style="font-family:var(--f-hand, var(--f-display));font-size:220px;font-weight:var(--display-weight,800)">{X.rich(txt)}</text></svg>', p)
    X.css("aefx-wo", ".fx .wo text { fill:transparent; stroke:var(--fg); stroke-width:3; stroke-dasharray:1400; stroke-dashoffset:1400; paint-order:stroke; }")
    X.tw(f'tl.to("#{cid} .wo text", {{strokeDashoffset:0, duration:1.6, ease:"power1.inOut"}}, {t + 0.1:.3f});')
    X.tw(f'tl.to("#{cid} .wo text", {{fill:"var(--fg)", strokeWidth:0, duration:0.5, ease:"power2.out"}}, {t + 1.5:.3f});')
    X.sfx(t + 0.1, "brush")


def flip3d(X, cid, t, d, p):
    """逐字三维翻转 (3D Flip per character): rotateX from -100°, transform-origin bottom, perspective on the line."""
    _clip(X, cid, t, d, f'<div class="big f3" style="perspective:900px">{_chars(X, p["text"])}</div>', p)
    X.tw(f'tl.from("#{cid} .f3 .c", {{rotationX:-100, opacity:0, transformOrigin:"50% 100% -20px", duration:0.7, ease:"back.out(1.5)", stagger:0.05}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "enter")


def slice_text(X, cid, t, d, p):
    """斜切分割 (Slice / Split text): the word is cut diagonally; the halves slide apart and snap back."""
    s = X.rich(p["text"])
    _clip(X, cid, t, d, f'<div class="sl" data-layout-allow-overlap style="position:relative"><div class="big a" style="clip-path:polygon(0 0,100% 0,100% 38%,0 62%)">{s}</div>'
                        f'<div class="big b" style="position:absolute;inset:0;clip-path:polygon(0 62%,100% 38%,100% 100%,0 100%)">{s}</div></div>', p)
    X.tw(f'tl.from("#{cid} .sl .a", {{xPercent:-60, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sl .b", {{xPercent:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.to("#{cid} .sl .a", {{xPercent:-4, yPercent:-4, duration:0.25, ease:"power2.out", yoyo:true, repeat:1}}, {t + 0.9:.3f});')
    X.tw(f'tl.to("#{cid} .sl .b", {{xPercent:4, yPercent:4, duration:0.25, ease:"power2.out", yoyo:true, repeat:1}}, {t + 0.9:.3f});')
    X.sfx(t + 0.1, "slam")


def shine(X, cid, t, d, p):
    """光泽扫过 (Shine / CC Light Sweep) on a title: a bright band travels across the glyphs once."""
    s = X.rich(p["text"])
    _clip(X, cid, t, d, f'<div class="big sh">{s}</div>', p)
    X.css("aefx-sh", ".fx .sh { background:linear-gradient(110deg, var(--fg) 0%, var(--fg) 40%, #fff 50%, var(--fg) 60%, var(--fg) 100%); background-size:300% 100%; -webkit-background-clip:text; background-clip:text; color:transparent; }")
    X.tw(f'tl.from("#{cid} .sh", {{opacity:0, y:30, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("#{cid} .sh", {{backgroundPosition:"100% 0"}}, {{backgroundPosition:"0% 0", duration:1.1, ease:"power2.inOut"}}, {t + 0.6:.3f});')


def glitch(X, cid, t, d, p):
    """故障 RGB 分离 (Glitch / RGB split): red & cyan copies jitter on stepped frames, then lock."""
    s = X.rich(p["text"])
    _clip(X, cid, t, d, f'<div class="gl" data-layout-allow-overlap style="position:relative"><div class="big r" style="position:absolute;inset:0;color:#ff2a4d;mix-blend-mode:screen">{s}</div>'
                        f'<div class="big cy" style="position:absolute;inset:0;color:#24e0ff;mix-blend-mode:screen">{s}</div><div class="big m">{s}</div></div>', p)
    for k in range(10):
        tt = t + 0.1 + k * 0.05
        a, b = X.rand.uniform(-14, 14), X.rand.uniform(-6, 6)
        X.tw(f'tl.set("#{cid} .r", {{x:{a:.0f}, y:{b:.0f}, clipPath:"inset({X.rand.randint(0, 60)}% 0 {X.rand.randint(0, 30)}% 0)"}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .cy", {{x:{-a:.0f}, y:{-b:.0f}, clipPath:"inset({X.rand.randint(0, 30)}% 0 {X.rand.randint(0, 60)}% 0)"}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .m", {{x:{X.rand.uniform(-6, 6):.0f}}}, {tt:.3f});')
    X.tw(f'tl.set("#{cid} .r, #{cid} .cy, #{cid} .m", {{x:0, y:0, clipPath:"inset(0 0 0 0)"}}, {t + 0.62:.3f});')
    X.sfx(t + 0.1, "glitch")


def ghost_type(X, cid, t, d, p):
    """巨型虚影背景字 (Ghost / outline background type): a huge outlined word drifts behind small foreground copy."""
    _clip(X, cid, t, d, f'<div class="gh" data-layout-allow-overlap>{X.rich(p["ghost"])}</div><div class="fg col"><div class="big" style="font-size:7vmin">{X.rich(p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.css("aefx-gh", ".fx .gh { position:absolute; left:-5%; top:50%; transform:translateY(-50%); font-family:var(--f-display); font-weight:900; font-size:52vmin; line-height:1; color:color-mix(in srgb, var(--fg) 5%, transparent); -webkit-text-stroke:2px color-mix(in srgb, var(--fg) 24%, transparent); white-space:nowrap; } .fx .fg { position:relative; }")
    X.tw(f'tl.fromTo("#{cid} .gh", {{xPercent:6, opacity:0}}, {{xPercent:-8, opacity:1, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.set("#{cid} .gh", {{opacity:1}}, {t + 0.6:.3f});')
    X.tw(f'tl.from("#{cid} .fg .big", {{y:40, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("#{cid} .fg .sub", {{opacity:0, duration:0.6}}, {t + 0.6:.3f});')


def lockup(X, cid, t, d, p):
    """中英双语锁定 + 注释引线 (type specimen lockup): headline, latin line, two leader-line annotations."""
    notes = p.get("notes", ["字体 · 思源宋体", "Latin · EB Garamond"])
    _clip(X, cid, t, d, f'<div class="lk"><div class="big">{X.rich(p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div>'
                        f'<div class="an a1"><i></i><span>{X.rich(notes[0])}</span></div><div class="an a2"><i></i><span>{X.rich(notes[1])}</span></div></div>', p)
    X.css("aefx-lk", ".fx .lk { position:relative; display:flex; flex-direction:column; align-items:center; } .fx .an { position:absolute; display:flex; align-items:center; gap:1vmin; font:400 1.7vmin var(--f-mono, monospace); color:var(--muted); white-space:nowrap; } .fx .an i { display:block; width:9vmin; height:1px; background:var(--muted); transform-origin:100% 50%; } .fx .a1 { right:100%; top:18%; margin-right:2vmin; flex-direction:row-reverse; } .fx .a1 i { transform-origin:0 50%; } .fx .a2 { left:100%; bottom:12%; margin-left:2vmin; } .fx .a2 i { transform-origin:0 50%; }")
    X.tw(f'tl.from("#{cid} .lk .big", {{opacity:0, scale:0.92, duration:0.7, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .lk .sub", {{opacity:0, y:12, duration:0.5}}, {t + 0.45:.3f});')
    X.tw(f'tl.from("#{cid} .an i", {{scaleX:0, duration:0.5, ease:"power3.out", stagger:0.2}}, {t + 0.8:.3f});')
    X.tw(f'tl.from("#{cid} .an span", {{opacity:0, x:8, duration:0.4, stagger:0.2}}, {t + 1.1:.3f});')


def odometer(X, cid, t, d, p):
    """数字滚轮 (Odometer / number wheel): each digit column spins down to its value, staggered."""
    v = str(p["value"]); unit = p.get("unit", "")
    cols = []
    for i, ch in enumerate(v):
        if ch.isdigit():
            seq = "".join(f"<i>{(int(ch) + k) % 10}</i>" for k in range(10, -1, -1))   # ends on ch
            cols.append(f'<span class="od"><span class="rl">{seq}</span></span>')
        else:
            cols.append(f'<span class="od0">{X.rich(ch)}</span>')
    X.used_text.update("0123456789" + unit)
    _clip(X, cid, t, d, f'<div class="col"><div class="big odm">{"".join(cols)}<small>{X.rich(unit)}</small></div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.css("aefx-od", ".fx .odm { display:flex; align-items:flex-end; font-variant-numeric:tabular-nums; font-family:var(--f-num, var(--f-display)); } .fx .od { display:inline-block; height:1.05em; overflow:hidden; } .fx .od .rl { display:flex; flex-direction:column; } .fx .od i { display:block; height:1.05em; font-style:normal; } .fx .odm small { font-size:.4em; margin:0 0 .18em .08em; color:var(--accent); }")
    n_dig = sum(c.isdigit() for c in v)
    for k in range(n_dig):
        X.tw(f'tl.fromTo("#{cid} .od:nth-of-type({k + 1}) .rl", {{yPercent:0}}, {{yPercent:{-100 * 10 / 11:.3f}, duration:{1.2 + k * 0.25:.2f}, ease:"power3.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, duration:0.5}}, {t + 0.8:.3f});')
    X.sfx(t + 0.1, "count")


# ------------------------------------------------------------------ shapes & backgrounds
def burst(X, cid, t, d, p):
    """形状元素爆发 (Shape Elements burst): radial lines + ring + dots fire as the word slams in."""
    lines = "".join(f'<i class="ray" style="transform:rotate({k * 30}deg)"><b></b></i>' for k in range(12))
    dots = "".join(f'<i class="dot" style="--a:{k * 45 + 22}deg"></i>' for k in range(8))
    _clip(X, cid, t, d, f'<div class="bu"><div class="rays">{lines}</div><i class="ring"></i>{dots}<div class="big w0">{X.rich(p["text"])}</div></div>', p)
    X.css("aefx-bu", ".fx .bu { position:relative; display:grid; place-items:center; } .fx .rays { position:absolute; width:60vmin; height:60vmin; } .fx .ray { position:absolute; left:50%; top:50%; width:0; height:0; } .fx .ray b { position:absolute; left:-0.4vmin; top:-30vmin; width:0.8vmin; height:7vmin; border-radius:1vmin; background:var(--accent); transform-origin:50% 30vmin; } .fx .ring { position:absolute; width:20vmin; height:20vmin; border-radius:50%; border:0.8vmin solid var(--accent); } .fx .dot { position:absolute; width:2vmin; height:2vmin; border-radius:50%; background:var(--fg); transform:rotate(var(--a)) translateY(-22vmin); }")
    X.tw(f'tl.from("#{cid} .w0", {{scale:2.2, opacity:0, duration:0.35, ease:"power4.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("#{cid} .ray b", {{scaleY:0, y:"10vmin"}}, {{scaleY:1, y:"0vmin", duration:0.25, ease:"power2.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.to("#{cid} .ray b", {{scaleY:0, y:"-6vmin", duration:0.3, ease:"power2.in"}}, {t + 0.55:.3f});')
    X.tw(f'tl.fromTo("#{cid} .ring", {{scale:0.2, opacity:1}}, {{scale:2.6, opacity:0, duration:0.6, ease:"power2.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.fromTo("#{cid} .dot", {{opacity:0}}, {{opacity:1, duration:0.05}}, {t + 0.32:.3f});')
    X.tw(f'tl.to("#{cid} .dot", {{scale:0, duration:0.5, ease:"power2.in"}}, {t + 0.4:.3f});')
    X.sfx(t + 0.1, "slam")


def diffuse(X, cid, t, d, p):
    """弥散光 (diffuse gradient blobs): 3 soft colour blobs orbit slowly behind a calm title."""
    cols = p.get("colors", ["#ff6ad5", "#7d6bff", "#ffb36b"])
    blobs = "".join(f'<i class="bl" style="background:{c}"></i>' for c in cols)
    _clip(X, cid, t, d, f'<div class="dfw">{blobs}</div><div class="col" style="position:relative"><div class="big">{X.rich(p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.css("aefx-df", ".fx .dfw { position:absolute; inset:0; filter:blur(9vmin); } .fx .bl { position:absolute; display:block; width:46vmin; height:46vmin; border-radius:50%; left:50%; top:50%; margin:-23vmin; opacity:.85; }")
    for i in range(len(cols)):
        a0 = i * 2.1
        pts = [(math.cos(a0 + k * 0.9) * 18, math.sin(a0 + k * 1.1) * 12) for k in range(4)]
        X.tw(f'tl.set("#{cid} .bl:nth-child({i + 1})", {{x:"{pts[0][0]:.1f}vmin", y:"{pts[0][1]:.1f}vmin"}}, {t:.3f});')
        for k in range(1, 4):
            X.tw(f'tl.to("#{cid} .bl:nth-child({i + 1})", {{x:"{pts[k][0]:.1f}vmin", y:"{pts[k][1]:.1f}vmin", duration:{d / 3:.2f}, ease:"sine.inOut"}}, {t + (k - 1) * d / 3:.3f});')
    X.tw(f'tl.from("#{cid} .dfw", {{opacity:0, duration:1.0}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .big", {{opacity:0, filter:"blur(12px)", duration:1.0, ease:"power2.out"}}, {t + 0.3:.3f});')


def gooey(X, cid, t, d, p):
    """粘性碰撞 (gooey metaballs): two balls approach, merge with a liquid neck, bounce apart; squash & stretch."""
    _clip(X, cid, t, d, '<svg width="0" height="0" style="position:absolute"><filter id="goo-%s"><feGaussianBlur in="SourceGraphic" stdDeviation="18"/><feColorMatrix values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 28 -12"/></filter></svg>'
          '<div class="go" style="filter:url(#goo-%s)"><i class="b1"></i><i class="b2"></i></div>' % (cid, cid), p)
    X.css("aefx-go", ".fx .go { position:relative; width:80vmin; height:40vmin; } .fx .go i { position:absolute; top:50%; width:16vmin; height:16vmin; margin-top:-8vmin; border-radius:50%; background:var(--accent); } .fx .b1 { left:10%; } .fx .b2 { right:10%; background:var(--fg) !important; }")
    X.tw(f'tl.to("#{cid} .b1", {{x:"22vmin", duration:0.7, ease:"power2.in"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .b2", {{x:"-22vmin", duration:0.7, ease:"power2.in"}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .go i", {{scaleX:1.25, scaleY:0.8, duration:0.12, yoyo:true, repeat:1}}, {t + 0.85:.3f});')
    X.tw(f'tl.to("#{cid} .b1", {{x:"-4vmin", duration:0.9, ease:"elastic.out(1,0.45)"}}, {t + 1.1:.3f});')
    X.tw(f'tl.to("#{cid} .b2", {{x:"4vmin", duration:0.9, ease:"elastic.out(1,0.45)"}}, {t + 1.1:.3f});')
    X.sfx(t + 0.85, "boing")


def callout(X, cid, t, d, p):
    """标注引线 (Callout title): a dot pops on the subject, the leader line draws out, the label slides along it."""
    img = f'<img class="cimg" src="{X.asset(p["image"])}" alt="">' if p.get("image") else ""
    _clip(X, cid, t, d, f'{img}<div class="co" style="left:{p.get("x", 40)}%;top:{p.get("y", 55)}%"><i class="dt"></i><i class="ld"></i><div class="lb"><b>{X.rich(p["text"])}</b><span>{X.rich(p.get("sub", ""))}</span></div></div>', p)
    X.css("aefx-co", ".fx .cimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .co { position:absolute; } .fx .dt { position:absolute; width:2.2vmin; height:2.2vmin; margin:-1.1vmin; border-radius:50%; background:var(--accent); box-shadow:0 0 0 0.8vmin color-mix(in srgb, var(--accent) 35%, transparent); } .fx .ld { position:absolute; left:0; top:0; width:22vmin; height:2px; background:var(--fg); transform-origin:0 50%; transform:rotate(-28deg); } .fx .lb { position:absolute; left:19vmin; top:-13vmin; white-space:nowrap; display:flex; flex-direction:column; gap:.6vmin; } .fx .lb b { font:800 4.4vmin var(--f-display); color:var(--fg); background:color-mix(in srgb, var(--bg) 70%, transparent); padding:.4vmin 1.4vmin; } .fx .lb span { font:500 1.8vmin var(--f-mono, monospace); color:var(--fg); letter-spacing:.14em; padding-left:1.4vmin; }")
    X.tw(f'tl.from("#{cid} .dt", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("#{cid} .ld", {{scaleX:0, duration:0.45, ease:"power3.out"}}, {t + 0.55:.3f});')
    X.tw(f'tl.from("#{cid} .lb b", {{clipPath:"inset(0 100% 0 0)", duration:0.5, ease:"power3.out"}}, {t + 0.9:.3f});')
    X.tw(f'tl.from("#{cid} .lb span", {{opacity:0, x:-10, duration:0.4}}, {t + 1.2:.3f});')
    if img: X.camera(f"#{cid} .cimg", t, d, "push")
    X.sfx(t + 0.3, "pop")


def triple(X, cid, t, d, p):
    """三连 (like · coin · favourite): icons pop in sequence, each with a ring burst; the B站/抖音 staple ending."""
    icons = ['<path d="M7 22V11l5-8a2 2 0 0 1 3 2l-1 6h6a2 2 0 0 1 2 2l-2 7a2 2 0 0 1-2 2H7zM3 11h4v11H3z"/>',
             '<circle cx="12" cy="12" r="9"/><path d="M8 9h8M9 12h6M12 9v9"/>',
             '<path d="M12 3l2.8 5.8 6.2.9-4.5 4.4 1 6.2L12 17.4 6.5 20.3l1-6.2L3 9.7l6.2-.9z"/>']
    lbl = p.get("labels", ["点赞", "投币", "收藏"])
    items = "".join(f'<div class="ti"><i class="rg"></i><svg viewBox="0 0 24 24">{ic}</svg><span>{X.rich(l)}</span></div>' for ic, l in zip(icons, lbl))
    _clip(X, cid, t, d, f'<div class="tri">{items}</div>', p)
    X.css("aefx-tri", ".fx .tri { display:flex; gap:12vmin; } .fx .ti { position:relative; display:flex; flex-direction:column; align-items:center; gap:2vmin; } .fx .ti svg { width:12vmin; height:12vmin; fill:none; stroke:var(--fg); stroke-width:1.6; stroke-linejoin:round; } .fx .ti span { font:600 2.6vmin var(--f-body); color:var(--fg); letter-spacing:.2em; } .fx .ti .rg { position:absolute; top:6vmin; left:50%; width:12vmin; height:12vmin; margin:-6vmin; border-radius:50%; border:0.6vmin solid var(--accent); opacity:0; }")
    for k in range(3):
        tk = t + 0.2 + k * 0.35
        X.tw(f'tl.from("#{cid} .ti:nth-child({k + 1}) svg", {{scale:0, rotation:-25, duration:0.45, ease:"back.out(3)"}}, {tk:.3f});')
        X.tw(f'tl.to("#{cid} .ti:nth-child({k + 1}) svg", {{fill:"var(--accent)", stroke:"var(--accent)", duration:0.2}}, {tk + 0.25:.3f});')
        X.tw(f'tl.fromTo("#{cid} .ti:nth-child({k + 1}) .rg", {{scale:0.4, opacity:1}}, {{scale:1.9, opacity:0, duration:0.5, ease:"power2.out"}}, {tk + 0.25:.3f});')
        X.tw(f'tl.from("#{cid} .ti:nth-child({k + 1}) span", {{opacity:0, y:10, duration:0.3}}, {tk + 0.2:.3f});')
        X.sfx(tk + 0.25, "pop")


def plate(X, cid, t, d, p):
    """整屏图版 (full-bleed plate with a slow push) — used to show transitions between complete frames."""
    _clip(X, cid, t, d, f'<img class="pl" src="{X.asset(p["image"])}" alt=""><div class="plt">{X.rich(p.get("text", ""))}</div>', p)
    X.css("aefx-pl", ".fx .pl { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .plt { position:relative; font:800 9vmin var(--f-display); color:#fff; text-shadow:0 6px 40px rgba(0,0,0,.6); }")
    X.camera(f"#{cid} .pl", t, d, "push")

# ------------------------------------------------------------------ round 2: the remaining top-ranked effects (research/ae_popular.md)
def parallax(X, cid, t, d, p):
    """2.5D 照片视差 (#2, VoluMax/Photomotion; MDMZ 1171万播放): clean plate + cut-out subject on separate depths,
    the camera dollies in so the subject separates from the background; optional title sits BETWEEN the layers."""
    title = f'<div class="pxt">{X.rich(p["text"])}</div>' if p.get("text") else ""
    _clip(X, cid, t, d, f'<img class="pxb" src="{X.asset(p["plate"])}" alt="">{title}<img class="pxf" src="{X.asset(p["fg"])}" alt="">', p)
    X.css("aefx-px", ".fx .pxb, .fx .pxf { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } #root.v .fx .pxt { font-size:14vmin; top:14%; } .fx .pxt { position:absolute; left:0; right:0; top:9%; text-align:center; font:900 22vmin/1 var(--f-display); color:#fff; letter-spacing:-.02em; opacity:.92; }")
    X.tw(f'tl.fromTo("#{cid} .pxb", {{scale:1.12, xPercent:1.5}}, {{scale:1.18, xPercent:-1.5, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    X.tw(f'tl.fromTo("#{cid} .pxf", {{scale:1.0, xPercent:-1}}, {{scale:1.16, xPercent:2.5, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    if title:
        X.tw(f'tl.fromTo("#{cid} .pxt", {{scale:1.0, yPercent:10, opacity:0}}, {{scale:1.07, yPercent:0, opacity:.92, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')


def stomp(X, cid, t, d, p):
    """重拍排版 Stomp (#4, TypoKing 1.34万份; B站动态歌词排版 898万): one word per beat slams full-frame,
    sizes alternate, every third beat inverts the frame; a 2-frame jolt on each hit.
    With narration timestamps each word lands the moment it is spoken (like lyric typography)."""
    words = p["words"]
    beat = p.get("beat", min(0.42, (d - 0.3) / max(len(words), 1)))
    times, after = [], t
    for i, w in enumerate(words):
        tt = None
        if X.chars:
            try: tt = float(X.T("@" + w.replace(" ", ""), after))
            except SystemExit: tt = None
        if tt is None or tt > t + d - 0.2: tt = (times[-1] + beat) if times else t + 0.1
        tt = max(tt - 2 / X.fps, (times[-1] + 0.12) if times else t)
        times.append(tt); after = tt + 0.05
    base = {0: 24, 1: 34, 2: 16}
    items = "".join(f'<div class="sw s{i % 3}" data-i="{i}" style="font-size:min({base[i % 3]}vmin, calc({86 / max(len(w), 1):.1f}vw))">{X.rich(w)}</div>' for i, w in enumerate(words))
    _clip(X, cid, t, d, f'<div class="sbg"></div>{items}', p)
    X.css("aefx-st", ".fx .sbg { position:absolute; inset:0; background:var(--bg); } .fx .sw { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; font-family:var(--f-display); font-weight:900; line-height:.95; color:var(--fg); opacity:0; text-align:center; white-space:nowrap; } .fx .sw.s2 { -webkit-text-stroke:3px var(--fg); color:color-mix(in srgb, var(--fg) 8%, transparent); }")
    for i, tt in enumerate(times):
        inv = i % 3 == 2
        X.tw(f'tl.set("#{cid} .sw", {{opacity:0}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .sbg", {{background:"{ "var(--accent)" if inv else "var(--bg)"}"}}, {tt:.3f});')
        X.tw(f'tl.fromTo("#{cid} .sw[data-i=\'{i}\']", {{opacity:1, scale:1.5}}, {{scale:1, duration:0.16, ease:"power4.out"}}, {tt:.3f});')
        X.tw(f'tl.fromTo("#{cid} > .stage", {{x:{X.rand.choice([-14, 14])}, y:{X.rand.choice([-8, 8])}}}, {{x:0, y:0, duration:0.1, ease:"steps(2)"}}, {tt:.3f});')
        X.sfx(tt, "slam" if i % 2 == 0 else "pop")
    X.tw(f'tl.set("#{cid} .sbg", {{background:"var(--bg)"}}, {times[-1] + 0.5:.3f});')


def mosaic(X, cid, t, d, p):
    """照片墙拼合 (#6, Mosaic Photo Reveal 1.6万份): 12 tiles fly in from depth and assemble a wall,
    then the camera pushes into one tile until it fills the frame."""
    imgs = [X.asset(u) for u in p["images"]]
    r = X.rand
    tiles = "".join(f'<i class="mt" style="background:url({imgs[k % len(imgs)]}) {r.randint(0, 100)}% {r.randint(0, 100)}%/{r.randint(180, 320)}% auto"></i>' for k in range(12))
    _clip(X, cid, t, d, f'<div class="mw">{tiles}</div>', p)
    X.css("aefx-mo", ".fx .mw { display:grid; grid-template-columns:repeat(4, 1fr); gap:1.4vmin; width:86%; aspect-ratio:16/9; } #root.v .fx .mw { grid-template-columns:repeat(3, 1fr); width:84%; aspect-ratio:9/12; } .fx .mt { display:block; border-radius:.8vmin; box-shadow:0 1vmin 3vmin rgba(0,0,0,.45); }")
    X.tw(f'tl.from("#{cid} .mt", {{opacity:0, scale:0.2, z:-400, rotation:(i)=>[{",".join(str(X.rand.randint(-25, 25)) for _ in range(12))}][i % 12], duration:0.7, ease:"back.out(1.4)", stagger:{{each:0.05, from:"random"}}}}, {t + 0.05:.3f});')
    X.tw(f'tl.to("#{cid} .mw", {{scale:4.2, transformOrigin:"62% 40%", duration:0.9, ease:"power3.inOut"}}, {t + d - 1.1:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")


def cartoon(X, cid, t, d, p):
    """卡通冲击特效 (#7, 140 Flash FX 1.47万份): speed lines, a jagged impact star, smoke puffs — on twos (12 fps steps)."""
    lines = "".join(f'<line x1="{500 + 120 * math.cos(a):.0f}" y1="{500 + 120 * math.sin(a):.0f}" x2="{500 + 700 * math.cos(a):.0f}" y2="{500 + 700 * math.sin(a):.0f}" />'
                    for a in [2 * math.pi * k / 28 + X.rand.uniform(-.05, .05) for k in range(28)])
    star = " ".join(f"{500 + (300 if k % 2 == 0 else 150) * math.cos(math.pi * k / 9):.0f},{500 + (300 if k % 2 == 0 else 150) * math.sin(math.pi * k / 9):.0f}" for k in range(18))
    puffs = "".join(f'<circle class="pf" cx="{500 + 260 * math.cos(a):.0f}" cy="{500 + 260 * math.sin(a):.0f}" r="70"/>' for a in [k * 1.05 for k in range(6)])
    _clip(X, cid, t, d, f'<svg class="ct" viewBox="0 0 1000 1000"><g class="spd">{lines}</g>{puffs}<polygon class="star" points="{star}"/>'
                        f'<text x="500" y="560" text-anchor="middle" class="pow">{X.rich(p.get("text", "啪！"))}</text></svg>', p)
    X.css("aefx-ct", ".fx .ct { width:80vmin; height:80vmin; overflow:visible; } .fx .spd line { stroke:var(--fg); stroke-width:6; stroke-linecap:round; } .fx .star { fill:var(--accent); stroke:var(--fg); stroke-width:10; stroke-linejoin:round; } .fx .pf { fill:var(--fg); opacity:.9; } .fx .pow { font-family:var(--f-display); font-weight:900; font-size:170px; fill:var(--fg); stroke:#000; stroke-width:8; paint-order:stroke; }")
    X.tw(f'tl.from("#{cid} .star", {{scale:0, rotation:-30, transformOrigin:"50% 50%", duration:0.25, ease:"steps(3)"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .pow", {{scale:2.2, transformOrigin:"50% 50%", duration:0.2, ease:"steps(3)"}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("#{cid} .spd", {{scale:0.6, opacity:1, transformOrigin:"50% 50%"}}, {{scale:1.3, opacity:0, duration:0.5, ease:"steps(6)"}}, {t + 0.12:.3f});')
    X.tw(f'tl.fromTo("#{cid} .pf", {{scale:0.2, transformOrigin:"50% 50%"}}, {{scale:1.4, opacity:0, duration:0.66, ease:"steps(8)", stagger:0.03}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .star", {{rotation:6, duration:0.17, ease:"steps(2)", yoyo:true, repeat:{max(1, int((d - 0.6) / 0.17))}}}, {t + 0.4:.3f});')
    X.sfx(t + 0.1, "slam")


def apple_blur(X, cid, t, d, p):
    """苹果式逐字模糊渐显 (#9, 206.8万 2025): each glyph fades up out of a soft blur and a small rise, grey→white."""
    _clip(X, cid, t, d, f'<div class="col"><div class="big ab">{_chars(X, p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.tw(f'tl.from("#{cid} .ab .c", {{opacity:0, filter:"blur(12px)", y:"0.18em", color:"#6e6e73", duration:0.7, ease:"power2.out", stagger:0.045}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, filter:"blur(6px)", duration:0.7}}, {t + 0.7:.3f});')


def portal(X, cid, t, d, p):
    """瞳孔穿梭 / 穿洞推进 (#10, B站364.5万 2025): a hole opens on a point of frame A showing frame B,
    then the camera dives through the hole until B fills the screen."""
    x, y = p.get("x", 50), p.get("y", 50)
    _clip(X, cid, t, d, f'<div class="pt" style="transform-origin:{x}% {y}%"><img class="pa" src="{X.asset(p["image"])}" alt=""><img class="pb" src="{X.asset(p["image2"])}" alt="" style="clip-path:circle(0% at {x}% {y}%)"><i class="ring" style="left:{x}%;top:{y}%"></i></div>', p)
    X.css("aefx-pt", ".fx .pt { position:absolute; inset:0; } .fx .pa, .fx .pb { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; } .fx .pt .ring { position:absolute; width:2vmin; height:2vmin; margin:-1vmin; border-radius:50%; box-shadow:0 0 0 .5vmin #fff, 0 0 4vmin 1vmin rgba(255,255,255,.6); opacity:0; }")
    t1 = t + 0.5
    X.tw(f'tl.to("#{cid} .pt .ring", {{opacity:1, scale:4, duration:0.4, ease:"power2.out"}}, {t1 - 0.2:.3f});')
    X.tw(f'tl.to("#{cid} .pb", {{clipPath:"circle(5% at {x}% {y}%)", duration:0.4, ease:"power2.out"}}, {t1:.3f});')
    X.tw(f'tl.to("#{cid} .pt", {{scale:14, duration:1.0, ease:"power3.in"}}, {t1 + 0.4:.3f});')
    X.tw(f'tl.to("#{cid} .pb", {{clipPath:"circle(150% at {x}% {y}%)", duration:1.0, ease:"power3.in"}}, {t1 + 0.4:.3f});')
    X.tw(f'tl.to("#{cid} .pt .ring", {{opacity:0, duration:0.3}}, {t1 + 0.6:.3f});')
    X.tw(f'tl.set("#{cid} .pt", {{scale:1}}, {t1 + 1.4:.3f});')
    X.tw(f'tl.set("#{cid} .pa", {{opacity:0}}, {t1 + 1.4:.3f});')
    X.tw(f'tl.set("#{cid} .pb", {{clipPath:"none"}}, {t1 + 1.4:.3f});')
    X.tw(f'tl.from("#{cid} .pb", {{scale:1.15, duration:0.6, ease:"power2.out", immediateRender:false}}, {t1 + 1.4:.3f});')
    X.sfx(t1 + 0.3, "whoosh_deep")


def neon(X, cid, t, d, p):
    """霓虹点亮 (#12, Neon Sign Kit 1万份): tube text stutters on (stepped flicker pattern), then holds with a steady glow."""
    _clip(X, cid, t, d, f'<div class="big ne">{X.rich(p["text"])}</div>', p)
    col = p.get("color", "#ff4fd8")
    X.css("aefx-ne", f".fx .ne {{ color:#fff3fd; font-weight:400; text-shadow:0 0 .04em #fff, 0 0 .12em {col}, 0 0 .3em {col}, 0 0 .6em {col}; }}")
    pat = [0, 1, 0, 0.2, 1, 0, 1, 0.5, 1]
    for k, o in enumerate(pat):
        X.tw(f'tl.set("#{cid} .ne", {{opacity:{o}}}, {t + 0.1 + k * 0.07:.3f});')
    X.tw(f'tl.set("#{cid} .ne", {{opacity:0.35}}, {t + 1.4:.3f});')
    X.tw(f'tl.set("#{cid} .ne", {{opacity:1}}, {t + 1.47:.3f});')
    X.sfx(t + 0.1, "glitch")


def notify(X, cid, t, d, p):
    """手机通知界面 (#13, Envato Elements「Elements」热门第1): iOS-style banners drop in one after another and stack."""
    items = p.get("items", [["小红书", "有人收藏了你的笔记"], ["抖音", "你的视频播放量破 10 万"], ["B站", "新增 128 个粉丝"]])
    cards = "".join(f'<div class="nt"><i class="ic">{X.rich(a[:1])}</i><div class="tx"><b>{X.rich(a)}</b><span>{X.rich(b)}</span></div><em>现在</em></div>' for a, b in items)
    _clip(X, cid, t, d, f'<div class="nst">{cards}</div>', p)
    X.css("aefx-nt", ".fx .nst { display:flex; flex-direction:column; gap:1.6vmin; width:min(80vmin, 92%); } .fx .nt { display:flex; align-items:center; gap:2vmin; padding:2vmin 2.4vmin; border-radius:3vmin; background:rgba(245,245,247,.82); backdrop-filter:blur(20px); box-shadow:0 2vmin 5vmin rgba(0,0,0,.35); color:#111; } .fx .nt .ic { width:7vmin; height:7vmin; border-radius:1.8vmin; background:var(--accent); color:#fff; display:grid; place-items:center; font:800 3.4vmin var(--f-body); flex:none; } .fx .nt .tx { display:flex; flex-direction:column; gap:.4vmin; flex:1; } .fx .nt b { font:700 2.8vmin var(--f-body); } .fx .nt span { font:400 2.5vmin var(--f-body); color:#333; } .fx .nt em { font:400 2vmin var(--f-body); color:#777; align-self:flex-start; }")
    X.tw(f'tl.from("#{cid} .nt", {{y:"-40vmin", opacity:0, scale:0.92, duration:0.6, ease:"back.out(1.3)", stagger:0.45}}, {t + 0.15:.3f});')
    for k in range(len(items)): X.sfx(t + 0.15 + k * 0.45, "pop")


def lower3(X, cid, t, d, p):
    """下三分之一字条 (#14, Lower Thirds 第1名 6.3K): accent bar grows, name slides out of a mask, role follows."""
    _clip(X, cid, t, d, f'<div class="l3"><i class="bar"></i><div class="nm"><span>{X.rich(p["text"])}</span></div><div class="rl"><span>{X.rich(p.get("sub", ""))}</span></div></div>', p, "fx-l3")
    X.css("aefx-l3", ".fx-l3 > .stage { align-items:flex-end !important; justify-content:flex-start !important; padding:0 0 14vmin 10vmin; } .fx .l3 { position:relative; padding-left:3vmin; } .fx .l3 .bar { position:absolute; left:0; top:0; bottom:0; width:.9vmin; background:var(--accent); transform-origin:50% 100%; } .fx .l3 .nm, .fx .l3 .rl { overflow:hidden; } .fx .l3 .nm span { display:block; font:800 7vmin var(--f-display); color:var(--fg); } .fx .l3 .rl span { display:block; font:500 2.6vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.18em; margin-top:1vmin; }")
    X.tw(f'tl.from("#{cid} .l3 .bar", {{scaleY:0, duration:0.4, ease:"power3.out"}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .l3 .nm span", {{xPercent:-105, duration:0.6, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.tw(f'tl.from("#{cid} .l3 .rl span", {{yPercent:110, duration:0.5, ease:"expo.out"}}, {t + 0.55:.3f});')


def collage(X, cid, t, d, p):
    """拼贴剪纸 (#21, Fakeplastictree Collage 203.5万): torn-edge photo pieces land on paper on twos, tape, a hand-drawn arrow."""
    imgs = [X.asset(u) for u in p["images"]]
    r = X.rand
    clips = ["polygon(2% 4%,30% 0,62% 3%,98% 1%,100% 30%,97% 64%,99% 98%,64% 100%,32% 96%,1% 99%,3% 62%,0 28%)",
             "polygon(0 2%,40% 4%,100% 0,98% 40%,100% 100%,55% 97%,0 100%,2% 50%)",
             "polygon(3% 0,100% 3%,96% 52%,100% 97%,48% 100%,1% 96%,4% 45%)"]
    pos = [(14, 18, 34, -6), (46, 12, 30, 5), (30, 52, 36, -2)]
    pieces = "".join(f'<div class="cp" style="left:{x}%;top:{y}%;width:{w}%;transform:rotate({rot}deg)"><div class="ph" style="clip-path:{clips[i % 3]}"><img src="{imgs[i % len(imgs)]}" alt=""></div><i class="tp"></i></div>' for i, (x, y, w, rot) in enumerate(pos))
    _clip(X, cid, t, d, f'<div class="cbg"></div>{pieces}<svg class="arw" viewBox="0 0 300 200"><path d="M20 160 C 90 40, 200 30, 270 80 M270 80 l-34 -6 M270 80 l-14 30"/></svg><div class="cnote">{X.rich(p.get("text", "这张才对"))}</div>', p)
    X.css("aefx-cl", ".fx .cbg { position:absolute; inset:0; background:#ece6da; } .fx .cp { position:absolute; } .fx .cp .ph { background:#fff; padding:1vmin; box-shadow:0 1vmin 2.4vmin rgba(60,40,10,.3); } .fx .cp img { display:block; width:100%; aspect-ratio:3/2; object-fit:cover; } .fx .cp .tp { position:absolute; left:50%; top:-1.4vmin; width:9vmin; height:2.8vmin; margin-left:-4.5vmin; background:rgba(235,220,170,.85); transform:rotate(-4deg); } .fx .arw { position:absolute; left:58%; top:44%; width:22%; overflow:visible; } .fx .arw path { fill:none; stroke:#d1281f; stroke-width:7; stroke-linecap:round; stroke-linejoin:round; } .fx .cnote { position:absolute; left:66%; top:66%; font:400 6vmin var(--f-hand, cursive); color:#d1281f; transform:rotate(-4deg); }")
    X.tw(f'tl.from("#{cid} .cp", {{y:"-30vmin", rotation:"+=18", opacity:0, duration:0.33, ease:"steps(4)", stagger:0.33}}, {t + 0.1:.3f});')
    X.tw(f'tl.fromTo("#{cid} .arw path", {{strokeDasharray:600, strokeDashoffset:600}}, {{strokeDashoffset:0, duration:0.5, ease:"steps(6)"}}, {t + 1.2:.3f});')
    X.tw(f'tl.from("#{cid} .cnote", {{opacity:0, scale:0.6, duration:0.25, ease:"steps(3)"}}, {t + 1.6:.3f});')
    for k in range(3): X.sfx(t + 0.1 + k * 0.33, "paper")


def match_cut(X, cid, t, d, p):
    """文字匹配剪辑 Text Match Cut (#23, Envato Elements 标题热门第1/2): the word holds its exact place while
    everything around it hard-cuts — background, colour field and typeface change every few frames.
    Each cut is a designed pair (ground + type treatment), so the word always reads."""
    imgs = [X.asset(u) for u in p.get("images", [])]
    D_ = "var(--f-display)"; S_ = "'h9-noto-serif-sc', serif"; H_ = "var(--f-hand, cursive)"; M_ = "var(--f-mono, monospace)"
    combos = [("img0", D_, 900, "#fff"), ("#ece6da", S_, 700, "#111"), ("img1", H_, 400, "#fff"), ("#1a3bd8", D_, 900, "#fff"),
              ("img2", S_, 700, "#fff"), ("#111", M_, 700, "var(--accent)"), ("img3", D_, 900, "#fff"), ("var(--accent)", S_, 700, "#111")]
    n = int((d - 0.4) / 0.22)
    _clip(X, cid, t, d, f'<div class="mcb"></div><div class="mcw">{X.rich(p["text"])}</div>', p)
    X.css("aefx-mc", ".fx .mcb { position:absolute; inset:0; background-size:cover; background-position:center; } .fx .mcw { position:relative; font-size:20vmin; line-height:1; text-shadow:0 .03em .25em rgba(0,0,0,.35); }")
    for k in range(n):
        tt = t + 0.1 + k * 0.22
        g, f, w, c = combos[k % len(combos)]
        if g.startswith("img"):
            u = imgs[int(g[3:]) % len(imgs)] if imgs else None
            bg = f"url({u}) center/cover" if u else "#111"
        else: bg = g
        X.tw(f'tl.set("#{cid} .mcb", {{background:"{bg}"}}, {tt:.3f});')
        X.tw(f'tl.set("#{cid} .mcw", {{fontFamily:"{f}", fontWeight:{w}, color:"{c}"}}, {tt:.3f});')
        X.sfx(tt, "click")


def impact(X, cid, t, d, p):
    """冲击抖动 (#24, Bricks 106.8万 2025): the title slams in and the whole frame takes a decaying camera shake."""
    _clip(X, cid, t, d, f'<div class="col"><div class="big im">{X.rich(p["text"])}</div><div class="sub">{X.rich(p.get("sub", ""))}</div></div>', p)
    X.tw(f'tl.from("#{cid} .im", {{scale:2.6, opacity:0, duration:0.22, ease:"power4.in"}}, {t + 0.1:.3f});')
    amp = 26
    for k in range(9):
        a = amp * (0.72 ** k)
        X.tw(f'tl.to("#{cid} > .stage", {{x:{X.rand.uniform(-a, a):.1f}, y:{X.rand.uniform(-a, a):.1f}, rotation:{X.rand.uniform(-a, a) / 20:.2f}, duration:0.035, ease:"none"}}, {t + 0.32 + k * 0.035:.3f});')
    X.tw(f'tl.to("#{cid} > .stage", {{x:0, y:0, rotation:0, duration:0.08}}, {t + 0.32 + 9 * 0.035:.3f});')
    X.tw(f'tl.from("#{cid} .sub", {{opacity:0, y:12, duration:0.4}}, {t + 0.6:.3f});')
    X.sfx(t + 0.32, "hit")


def dual(X, cid, t, d, p):
    """横竖双屏 (one composition, two aspect ratios): a landscape screen and a portrait phone slide in showing the same frame."""
    _clip(X, cid, t, d, f'<div class="du"><div class="dh"><img src="{X.asset(p["img_h"])}" alt=""><span>16:9</span></div><div class="dv"><img src="{X.asset(p["img_v"])}" alt=""><span>9:16</span></div></div>'
                        f'<div class="dut">{X.rich(p.get("text", ""))}</div>', p)
    X.css("aefx-du", ".fx .du { display:flex; align-items:center; gap:5vmin; } #root.v .fx .du { flex-direction:column; gap:4vmin; } .fx .dh, .fx .dv { position:relative; border-radius:2vmin; overflow:hidden; box-shadow:0 0 0 .6vmin #2a2826, 0 3vmin 8vmin rgba(0,0,0,.6); } .fx .dh { width:62vmin; aspect-ratio:16/9; } .fx .dv { width:22vmin; aspect-ratio:9/16; border-radius:3vmin; } #root.v .fx .dh { width:78vmin; } #root.v .fx .dv { width:34vmin; } .fx .du img { width:100%; height:100%; object-fit:cover; display:block; } .fx .du span { position:absolute; left:1.4vmin; bottom:1.2vmin; font:600 2vmin var(--f-mono, monospace); color:#fff; background:rgba(0,0,0,.55); padding:.3vmin 1vmin; border-radius:.6vmin; } .fx .dut { position:absolute; left:0; right:0; bottom:9vmin; text-align:center; font:800 5vmin var(--f-display); color:var(--fg); }")
    X.tw(f'tl.from("#{cid} .dh", {{x:"-30vmin", opacity:0, rotationY:25, duration:0.7, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .dv", {{x:"30vmin", opacity:0, rotationY:-25, duration:0.7, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("#{cid} .dut", {{opacity:0, y:20, duration:0.5}}, {t + 0.5:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")


FX = {k: v for k, v in globals().items() if callable(v) and not k.startswith("_") and k not in ("math",)}


def _plugins():
    """more effects live one-per-file in scripts/h9/fx/<name>.py (each exports FX = {"name": fn}); they may use
    this module's helpers (_clip, _chars, THEMES). Lets several people add effects without touching this file."""
    import importlib.util, pathlib
    for f in sorted((pathlib.Path(__file__).parent / "fx").glob("[!_]*.py")):
        spec = importlib.util.spec_from_file_location(f"h9fx_{f.stem}", f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for k, v in getattr(m, "FX", {}).items():
            if k in FX: raise SystemExit(f"effect {k!r} in {f.name} clashes with an existing effect")
            FX[k] = v


_plugins()
