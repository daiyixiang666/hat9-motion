"""过去对现在 Then vs now (VideoHive Infographic Maker 2.6K; the「before / after」split is a staple of every
explainer pack): the old figure fills the frame first, then a slanted wipe sweeps the new figure across until the
frame is split, both numbers count, and a change badge (×N or +N%) lands on the seam.

Adapts: numbers of any size (万 / 亿), with or without units; labels and captions from a word to a sentence; an
optional picture or footage behind each side (`image`); 16:9 splits left | right, 9:16 splits top / bottom.
The badge is computed (×N when the ratio ≥ 2, otherwise ±N%) unless `change` is given.
p: then {label, value, unit, caption, image} · now {…} · change · dec · title · note · mock
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")


def _side(X, q, cls, x, y, w, h, P, dec, pad):
    """pad: (top, right, bottom, left) px kept clear inside the panel (the change badge sits on the seam)."""
    v = W.num(q.get("value"))
    div, suf = W.F.compact(abs(v)) if v is not None else (1, "")
    unit = suf + str(q.get("unit", ""))
    big = f"{v / div:,.{dec}f}" if v is not None else ""
    aw = w - pad[1] - pad[3]
    cs, cl = W.fit_px(X, q.get("caption", ""), aw, 120, 34, 20, 2) if q.get("caption") else (0, [])
    ls = min(60, aw / max(1, W.F.em(str(q.get("label", "")))))
    room = h - pad[0] - pad[2] - ls * 1.3 - 10 - (16 + cs * 1.3 * len(cl) if cl else 0)
    bs = min(260 if not P else 230, room / 1.05, aw * 0.94 / max(0.6, W.F.em(big) * 0.8 + W.F.em(unit) * 0.4 + 0.1))     # display digits run wide
    img = ""
    if q.get("image"):
        img = f'<img class="tnimg" src="{X.asset(q["image"])}" alt="">'
    return (f'<div class="tnsd {cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">{img}<div class="tnin" style="padding:{pad[0]:.0f}px {pad[1]:.0f}px {pad[2]:.0f}px {pad[3]:.0f}px">'
            f'<div class="tnl" style="font-size:{ls:.0f}px">{X.rich(q.get("label", ""))}</div>'
            f'<div class="tnv w3k" style="font-size:{bs:.0f}px"><span class="n">{"0" if v is not None else ""}</span><small>{X.rich(unit)}</small></div>'
            + (f'<div class="tnc" style="font-size:{cs:.0f}px">{W.lines_html(X, cl)}</div>' if cl else "") + '</div></div>'), (v / div if v is not None else None)


def then_now(X, cid, t, d, p):
    W.base(X)
    a, b = p["then"], p["now"]
    va, vb = W.num(a.get("value")), W.num(b.get("value"))
    dec = int(p.get("dec", W.dec_of([v for v in (va, vb) if v is not None] or [0])))
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx
    change = p.get("change")
    if not change and va and vb:
        r = vb / va
        change = (f"×{r:.1f}".replace(".0", "") if r < 100 else f"×{r:,.0f}") if r >= 2 else (f"+{(r - 1) * 100:.0f}%" if r >= 1 else f"−{(1 - r) * 100:.0f}%")
    bw = (W.F.em(str(change)) * 44 * 0.62 + 56) if change else 0       # badge size, kept clear of both panels' text
    if P:
        h = (y1 - top - 20) / 2
        A, va_ = _side(X, a, "a", x0, top, x1 - x0, h, P, dec, (24, 56, 50 if change else 24, 56))
        B, vb_ = _side(X, b, "b", x0, top + h + 20, x1 - x0, h, P, dec, (50 if change else 24, 56, 24, 56))
        seam = (x0, top + h + 10, x1, top + h + 10)
    else:
        w = (x1 - x0 - 40) / 2
        A, va_ = _side(X, a, "a", x0, top, w, y1 - top, P, dec, (30, max(50, bw / 2 + 4), 30, 56))
        B, vb_ = _side(X, b, "b", x0 + w + 40, top, w, y1 - top, P, dec, (30, 50, 30, max(56, bw / 2 + 4)))
        seam = (x0 + w + 20, top, x0 + w + 20, y1)
    bx, by = (seam[0] + seam[2]) / 2, (seam[1] + seam[3]) / 2
    X.css("fx-thennow", """
.fx .tn .tnsd { position:absolute; overflow:hidden; border-radius:10px; }
.fx .tn .tnsd.a { background:color-mix(in srgb, var(--fg) 7%, var(--bg)); }
.fx .tn .tnsd.b { background:color-mix(in srgb, var(--accent) 14%, var(--bg)); }
.fx .tn .tnimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; opacity:.28; }
.fx .tn .tnin { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; }
.fx .tn .tnl { font:700 1em var(--f-mono, monospace); letter-spacing:.06em; color:var(--muted); }
.fx .tn .tnsd.b .tnl { color:var(--accent); }
.fx .tn .tnv { margin-top:10px; display:flex; align-items:flex-end; gap:8px; white-space:nowrap; line-height:1; color:color-mix(in srgb, var(--fg) 60%, var(--bg)); }
.fx .tn .tnsd.b .tnv { color:var(--fg); }
.fx .tn .tnv small { font-size:.36em; padding-bottom:.08em; flex:none; }
.fx .tn .tnc { margin-top:16px; font-family:var(--f-body); font-weight:700; color:var(--fg); line-height:1.3; } .fx .tn .tnc .fl { display:block; white-space:nowrap; }
.fx .tn .tnseam { position:absolute; background:var(--fg); }
.fx .tn .tnbad { position:absolute; transform:translate(-50%,-50%); font:900 44px var(--f-num, var(--f-display)); color:var(--bg); background:var(--accent);
  padding:10px 22px; border-radius:999px; box-shadow:0 0 0 6px var(--bg); white-space:nowrap; }
""")
    seam_el = (f'<i class="tnseam" style="left:{seam[0]:.0f}px; top:{seam[1] - 2:.0f}px; width:{seam[2] - seam[0]:.0f}px; height:4px"></i>' if P
               else f'<i class="tnseam" style="left:{seam[0] - 2:.0f}px; top:{seam[1]:.0f}px; width:4px; height:{seam[3] - seam[1]:.0f}px"></i>')
    inner = (f'<div class="w3 tn">{hh}{A}{B}{seam_el}' + (f'<div class="tnbad" style="left:{bx:.0f}px; top:{by:.0f}px">{X.rich(change)}</div>' if change else "")
             + f'{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    X.used_text.update(str(change) + "×−+0123456789.,%")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .tnsd.a", {{opacity:0, scale:0.96, duration:0.5, ease:"expo.out"}}, {t + 0.1:.3f});')
    if va_ is not None: W.count(X, f"{s} .tnsd.a .n", t + 0.25, va_, dur=0.8, dec=dec)
    tb = t + min(1.4, d * 0.32)
    wipe_from = "inset(0 0 100% 0)" if P else "polygon(0 0, 0 0, -20% 100%, -20% 100%)"
    wipe_to = "inset(0 0 0% 0)" if P else "polygon(0 0, 120% 0, 100% 100%, -20% 100%)"
    X.tw(f'tl.fromTo("{s} .tnsd.b", {{clipPath:"{wipe_from}"}}, {{clipPath:"{wipe_to}", duration:0.75, ease:"power3.inOut"}}, {tb:.3f});')
    X.tw(f'tl.from("{s} .tnseam", {{{"scaleX" if P else "scaleY"}:0, duration:0.6, ease:"expo.inOut"}}, {tb + 0.1:.3f});')
    X.sfx(tb, "whoosh_soft")
    if vb_ is not None: W.count(X, f"{s} .tnsd.b .n", tb + 0.3, vb_, dur=1.0, dec=dec)
    X.tw(f'tl.from("{s} .tnbad", {{scale:0, rotation:-25, duration:0.5, ease:"back.out(2.4)"}}, {tb + 1.1:.3f});')
    X.tw(f'tl.to("{s} .tnsd.a", {{opacity:0.75, duration:0.4}}, {tb + 1.1:.3f});')
    X.sfx(tb + 1.15, "hit")


FX = {"then_now": then_now}
