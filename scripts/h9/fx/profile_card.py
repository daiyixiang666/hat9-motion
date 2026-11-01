"""人物名片 (profile card / person intro — Envato "Lower Thirds"、"Social Profile Cards" and every 商业拆解 that
introduces a founder): the avatar ring draws on, the monogram (or photo) springs in, the name lifts out of its
mask, role and one-liner follow, stats count up; a follow button can be pressed (关注 → 已关注). 2–6 people sit
side by side (多人并列) and one can be spotlit on a cue.

Adapts: 1–6 people; names from 2 glyphs to a long Latin name, roles and one-liners of any length (fitted, ≤3
lines); photo or monogram avatar; 0–4 stats on a single card.
p: people [{name, role, line, avatar, stats:[[label, value]], tags}] | "名字|身份|一句话" — or name / role / line /
   avatar / stats / bio for one person (`line` is reserved for the spoken caption) · follow · t_follow · hl (index) · t_hl · mock
"""
from h9.aefx import _clip
from h9 import fit as FT
import importlib.util, pathlib, re, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")


def _people(p):
    out = []
    for it in FT.as_list(p.get("people")):
        if isinstance(it, dict): out.append({**it, "line": it.get("line", it.get("bio", it.get("desc", "")))})
        elif isinstance(it, (list, tuple)): out.append({"name": it[0], "role": it[1] if len(it) > 1 else "", "line": it[2] if len(it) > 2 else ""})
        else:
            parts = str(it).split("|"); out.append({"name": parts[0], "role": parts[1] if len(parts) > 1 else "", "line": parts[2] if len(parts) > 2 else ""})
    if not out: out = [{**{k: p.get(k) for k in ("name", "role", "avatar", "stats", "tags")}, "line": p.get("bio", p.get("desc", ""))}]   # `line` is the spoken caption
    return out[:6]


def _fit1(X, text, w, h, max_vm, lines=1):
    f = FT.fit_text(str(text or ""), SO.px(X, w), SO.px(X, h), SO.px(X, max_vm), SO.px(X, max_vm) * 0.45, max_lines=lines, lh=1.25)
    return SO.vm(X, f.px), "<br>".join(X.rich(l) for l in f.lines)


def _card(X, k, pp, w, h, orient, av, big):
    """one card: orient 'h' = avatar left, 'v' = stacked. sizes in vmin."""
    name, role, line = pp.get("name", ""), pp.get("role", ""), pp.get("line", "")
    tw = (w - av - 9) if orient == "h" else (w - 6)
    nm_s, nm = _fit1(X, name, tw, av * (0.42 if orient == "h" else 0.36), 9.5 if big else 5.6)
    rl_s, rl = _fit1(X, role, tw, 7 if big else 5, 3.4 if big else 2.5, 2)
    ln_s, ln = _fit1(X, line, tw, 12 if big else 7, 3.0 if big else 2.2, 3)
    stats = ""
    if big and pp.get("stats"):
        cells = []
        for j, sv in enumerate(FT.as_list(pp.get("stats"))[:4]):
            lab, val = (sv[0], sv[1]) if isinstance(sv, (list, tuple)) else (str(sv), "")
            m = re.match(r"^(\D*?)([-+]?[\d,]*\.?\d+)(.*)$", str(val))
            attrs = f' data-p="{X.rich(m.group(1))}" data-v="{m.group(2).replace(",", "")}" data-u="{X.rich(m.group(3))}"' if m else ""
            cells.append(f'<div class="wpp-st"><b{attrs}>{X.rich(val)}</b><span>{X.rich(lab)}</span></div>')
        stats = f'<div class="wpp-sts">{"".join(cells)}</div>'
    fol = '<div class="wpp-fo" data-layout-allow-overlap><span class="a" data-layout-allow-overlap>＋ 关注</span><span class="b" data-layout-allow-overlap>已关注</span></div>' if pp.get("_follow") else ""
    tags = "".join(f'<i class="wpp-tg">{X.rich(tg)}</i>' for tg in FT.as_list(pp.get("tags"))[:3])
    ring = (f'<svg class="wpp-rg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="47" pathLength="1"/></svg>')
    avh = SO.avatar(X, name, pp.get("avatar"), "wpp-av", f"width:{av * 0.86:.2f}vmin; height:{av * 0.86:.2f}vmin; font-size:{av * 0.4:.2f}vmin")
    return (f'<div class="wpp-cd {orient}" data-k="{k}" style="width:{w:.1f}vmin; height:{h:.1f}vmin">'
            f'<div class="wpp-aw" style="width:{av:.1f}vmin; height:{av:.1f}vmin">{ring}{avh}</div>'
            f'<div class="wpp-tx"><div class="wpp-nw"><div class="wpp-nm" style="font-size:{nm_s:.2f}vmin">{nm}</div></div>'
            f'<div class="wpp-rl" style="font-size:{rl_s:.2f}vmin">{rl}</div>{f"<div class=wpp-tgs>{tags}</div>" if tags else ""}'
            f'<div class="wpp-ln" style="font-size:{ln_s:.2f}vmin">{ln}</div>{stats}{fol}</div></div>')


def profile_card(X, cid, t, d, p):
    SO.base_css(X)
    ppl = _people(p)
    if p.get("follow") and len(ppl) == 1: ppl[0]["_follow"] = True
    n = len(ppl); P = X.portrait
    if n == 1:
        cards = [_card(X, 0, ppl[0], 88 if P else 128, 88 if P else 54, "v" if P else "h", 30 if P else 28, True)]
        lay = "one"
    elif n <= 3:
        if P: cards = [_card(X, k, pp, 88, min(27, 82 / n - 3), "h", min(19, 82 / n - 9), False) for k, pp in enumerate(ppl)]
        else: cards = [_card(X, k, pp, min(50, 152 / n - 3), 58, "v", 18, False) for k, pp in enumerate(ppl)]
        lay = "row"
    else:
        cols = 2 if P else 3
        rows = -(-n // cols)
        cw = (88 if P else 150) / cols - 2.5
        ch = (90 if P else 70) / rows - 2.5
        cards = [_card(X, k, pp, cw, ch, "v" if P else "h", min(ch * 0.42, 13) if P else min(ch * 0.62, 14), False) for k, pp in enumerate(ppl)]
        lay = "grid"
    X.css("fx-wpp", """
.fx .wpp { position:relative; display:flex; flex-wrap:wrap; justify-content:center; align-content:center; gap:2.5vmin; }
#root.v .fx .wpp { margin-top:-14vmin; max-width:92vmin; }
.fx .wpp.row { flex-wrap:nowrap; } #root.v .fx .wpp.row { flex-direction:column; }
.fx .wpp.grid { max-width:156vmin; }
.fx .wpp-cd { position:relative; display:flex; gap:3vmin; padding:3vmin; border-radius:2.4vmin; background:var(--card); color:var(--card-fg); overflow:hidden;
  box-shadow:0 0 0 .25vmin color-mix(in srgb, var(--card-fg) 12%, transparent), 0 3vmin 8vmin rgba(0,0,0,.22); font-family:var(--f-body); }
.fx .wpp-cd.h { flex-direction:row; align-items:center; } .fx .wpp-cd.v { flex-direction:column; align-items:center; text-align:center; }
.fx .wpp-aw { position:relative; flex:none; display:grid; place-items:center; }
.fx .wpp-rg { position:absolute; inset:0; width:100%; height:100%; transform:rotate(-90deg); overflow:visible; }
.fx .wpp-rg circle { fill:none; stroke:var(--accent); stroke-width:2.6; stroke-dasharray:1 1; stroke-linecap:round; }
.fx .wpp-av { position:relative; }
.fx .wpp-tx { min-width:0; display:flex; flex-direction:column; gap:1vmin; }
.fx .wpp-cd.v .wpp-tx { align-items:center; }
.fx .wpp-nw { overflow:hidden; padding-bottom:.1em; }
.fx .wpp-nm { font-weight:900; line-height:1.12; letter-spacing:-.01em; }
.fx .wpp-rl { font-weight:700; color:var(--accent); line-height:1.3; }
.fx .wpp-ln { font-weight:500; line-height:1.45; opacity:.72; }
.fx .wpp-tgs { display:flex; gap:.8vmin; flex-wrap:wrap; } .fx .wpp-tg { font-style:normal; font-size:1.8vmin; font-weight:700; padding:.3vmin 1vmin; border-radius:.6vmin; background:color-mix(in srgb, var(--card-fg) 8%, transparent); }
.fx .wpp-sts { display:flex; gap:3vmin; margin-top:1vmin; flex-wrap:wrap; }
.fx .wpp-cd.v .wpp-sts { justify-content:center; }
.fx .wpp-st { display:flex; flex-direction:column; } .fx .wpp-st b { font:900 4.4vmin/1.1 var(--f-num, var(--f-body)); font-variant-numeric:tabular-nums; }
.fx .wpp-st span { font-size:1.9vmin; opacity:.6; }
.fx .wpp-fo { position:relative; align-self:flex-start; margin-top:1.2vmin; height:5.4vmin; min-width:17vmin; border-radius:99vmin; overflow:hidden; font:900 2.4vmin var(--f-body); }
.fx .wpp-cd.v .wpp-fo { align-self:center; }
.fx .wpp-fo span { position:absolute; inset:0; display:grid; place-items:center; border-radius:99vmin; }
.fx .wpp-fo .a { background:var(--accent); color:#fff; } .fx .wpp-fo .b { background:color-mix(in srgb, var(--card-fg) 10%, transparent); color:var(--card-fg); opacity:0; }
""")
    mock = f'<i class="wp-mock" style="right:1vmin; top:-4vmin">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    X.used_text.update("＋关注已0123456789.%亿万")
    _clip(X, cid, t, d, f'<div class="wpp {lay}">{mock}{"".join(cards)}</div>', p)
    s = f"#{cid}"
    st = min(0.18, 0.9 / max(n, 1))
    for k in range(n):
        tk = t + 0.1 + k * st
        c = f'{s} .wpp-cd[data-k=\'{k}\']'
        X.tw(f'tl.from("{c}", {{y:"6vmin", opacity:0, duration:0.6, ease:"expo.out"}}, {tk:.3f});')
        X.tw(f'tl.fromTo("{c} .wpp-rg circle", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.8, ease:"power2.inOut"}}, {tk + 0.1:.3f});')
        X.tw(f'tl.from("{c} .wpp-av", {{scale:0.3, opacity:0, duration:0.5, ease:"back.out(2)"}}, {tk + 0.2:.3f});')
        X.tw(f'tl.from("{c} .wpp-nm", {{yPercent:110, duration:0.65, ease:"expo.out"}}, {tk + 0.3:.3f});')
        X.tw(f'tl.from("{c} .wpp-rl, {c} .wpp-tgs, {c} .wpp-ln, {c} .wpp-sts, {c} .wpp-fo", {{y:14, opacity:0, duration:0.45, ease:"expo.out", stagger:0.08}}, {tk + 0.45:.3f});')
        if k < 4: X.sfx(tk + 0.2, "pop")
    # numeric stats count up
    X.tw(f'document.querySelectorAll("{s} .wpp-st b[data-v]").forEach((el)=>{{const raw=el.dataset.v, v=parseFloat(raw); if(isNaN(v)) return; const pre=el.dataset.p||"", u=el.dataset.u||""; const dec=(raw.split(".")[1]||"").length; const o={{v:0}};'
         f' tl.to(o, {{v:v, duration:1.0, ease:"power2.out", onUpdate:()=>{{el.textContent=pre+(v>=1000&&!dec ? Math.round(o.v).toLocaleString("en-US") : o.v.toFixed(dec))+u;}}}}, {t + 0.7:.3f});}});')
    if p.get("follow") and n == 1:
        tf = SO.cue(X, p, "t_follow", t, t + d * 0.7)
        X.tw(f'tl.to("{s} .wpp-fo", {{keyframes:[{{scale:0.88, duration:0.08}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}]}}, {tf:.3f});')
        X.tw(f'tl.to("{s} .wpp-fo .b", {{opacity:1, duration:0.15}}, {tf + 0.05:.3f});')
        X.sfx(tf, "click")
    if p.get("hl") is not None and n > 1:
        th = SO.cue(X, p, "t_hl", t, t + d * 0.65)
        h = int(p["hl"])
        X.tw(f'tl.to("{s} .wpp-cd:not([data-k=\'{h}\'])", {{opacity:0.35, scale:0.97, duration:0.4}}, {th:.3f});')
        X.tw(f'tl.to("{s} .wpp-cd[data-k=\'{h}\']", {{scale:1.04, duration:0.45, ease:"back.out(2)"}}, {th:.3f});')
        X.sfx(th, "hit")
    X.camera(f"{s} .wpp", t, d, "push")


FX = {"profile_card": profile_card}
