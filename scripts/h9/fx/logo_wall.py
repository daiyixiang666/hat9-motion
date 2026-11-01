"""Logo 墙 (client / partner / portfolio wall — the explainer staple "这些公司都在用"): logos arrive dim, light up one
by one in a seeded order, then one is pulled out to the centre, enlarged, with its name and a line.

p: logos (list of names → made-up wordmarks drawn here, or {src, name, sub} for your own logo files) · hl (index or name) ·
   t_hl ("@词" / seconds) · title · kicker · names (true = small name under every tile) · sub (line under the pulled-out logo)
Adapts: 1–60 logos (the grid maximises tile area for the box; above ~30 the names hide); any logo aspect (contained);
16:9 title left on top, 9:16 title on top of a taller grid. Only use logos you own or made-up names — never real brands' marks.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def logo_wall(X, cid, t, d, p):
    items = []
    for i, it in enumerate(fit.as_list(p.get("logos"))):
        if isinstance(it, dict): items.append({"name": str(it.get("name", "")), "src": it.get("src"), "sub": it.get("sub", "")})
        else: items.append({"name": str(it), "src": None, "sub": ""})
    if not items: items = [{"name": "示例品牌", "src": None, "sub": ""}]
    n = len(items)
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    title = fit.as_text(p.get("title"))
    tf = D.C.fitted(X, title, (x1 - x0) * (1 if P else 0.7), 120 if P else 100, 64 if P else 58, 30, max_lines=2) if title else None
    th = (tf.n * tf.px * 1.12 + 26) if tf else 0
    kick = p.get("kicker")
    kh = 44 if kick else 0
    gx0, gy0, gx1, gy1 = x0, y0 + kh + th + 18, x1, y1
    gap = 18 if n <= 12 else (12 if n <= 30 else 8)
    cols, rows = fit.grid(n, gx1 - gx0, gy1 - gy0, item_ar=2.1, gap=gap)
    tw = min((gx1 - gx0 - gap * (cols - 1)) / cols, (gx1 - gx0) * 0.5); thh = min((gy1 - gy0 - gap * (rows - 1)) / rows, tw / 1.25)
    tot_h = rows * thh + gap * (rows - 1)
    oy = gy0 + max(0, (gy1 - gy0 - tot_h) / 2)
    show_names = p.get("names", n <= 18) and thh > 90
    hl = p.get("hl", 0)
    if isinstance(hl, str): hl = next((i for i, it in enumerate(items) if it["name"] == hl), 0)
    hl = max(0, min(int(hl), n - 1))
    tiles = []
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        inrow = min(cols, n - r * cols)
        ox = gx0 + (gx1 - gx0 - (inrow * tw + gap * (inrow - 1))) / 2
        lx, ly = ox + c * (tw + gap), oy + r * (thh + gap)
        lh = thh * (0.62 if show_names else 0.78)
        if it["src"]:
            logo = f'<img src="{X.asset(it["src"])}" alt="" style="width:{tw * 0.8:.0f}px; height:{lh * 0.9:.0f}px; object-fit:contain">'
        else:
            svg, ar = D.wordmark(it["name"])
            lw = min(tw * 0.78, lh * 0.5 * ar)
            logo = f'<div class="lw-svg" style="width:{lw:.0f}px; height:{lw / ar:.0f}px">{svg}</div>'
        X.used_text.update(it["name"])
        nm = f'<b style="font-size:{max(14, min(22, thh * 0.13)):.0f}px">{X.rich(it["name"])}</b>' if show_names and it["src"] else ""
        tiles.append((lx, ly, f'<div class="lw-t" data-k="{i}" style="left:{lx:.1f}px; top:{ly:.1f}px; width:{tw:.1f}px; height:{thh:.1f}px">{logo}{nm}<i class="lw-ring"></i></div>'))
    # where the pulled-out logo goes: the middle of the grid, ~2.2× (capped by the box)
    hx, hy = tiles[hl][0], tiles[hl][1]
    s_hl = min(max(1.2, min(2.6, (gx1 - gx0) * 0.42 / tw, (gy1 - gy0) * 0.5 / thh)), (gx1 - gx0) * 0.9 / (tw * 1.04))
    cx, cy = (gx0 + gx1) / 2, (gy0 + gy1) / 2 - (24 if p.get("sub") else 0)
    dx, dy = cx - (hx + tw / 2), cy - (hy + thh / 2)
    sub = p.get("sub") or items[hl]["sub"] or ""
    sf = D.C.fitted(X, sub, (gx1 - gx0) * 0.7, 80, 34, 22, max_lines=2) if sub else None
    sub_html = (f'<div class="lw-sub" style="left:{gx0:.0f}px; width:{gx1 - gx0:.0f}px; top:{cy + thh * s_hl / 2 + 22:.0f}px; font-size:{sf.px}px">{D.C.lines(X, sf)}</div>' if sf else "")
    head = (f'<div class="d2-kick" style="left:{x0}px; top:{y0}px">{X.rich(kick)}</div>' if kick else "") + \
           (f'<div class="d2-ttl lw-ttl" style="left:{x0}px; top:{y0 + kh}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else "")
    X.used_text.update(str(kick or "") + title)
    X.css("fx-d2", D.CSS)
    X.css("fx-logo-wall", """
.lw-t { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; border-radius:14px;
  background:var(--card); color:var(--card-fg, var(--fg)); box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--fg) 12%, transparent); }
.lw-t b { font-family:var(--f-body); font-weight:700; color:var(--muted); white-space:nowrap; }
.lw-svg svg { width:100%; height:100%; display:block; }
.lw-svg .acc { fill:var(--accent); }
.lw-ring { position:absolute; inset:0; border-radius:14px; box-shadow:0 18px 50px rgba(0,0,0,.28), inset 0 0 0 2.5px var(--accent); opacity:0; pointer-events:none; }
.lw-sub { position:absolute; text-align:center; font-family:var(--f-body); font-weight:800; color:var(--fg); line-height:1.25; }
""")
    _clip(X, cid, t, d, f'<div class="d2 lw">{head}{"".join(h for _, _, h in tiles)}{sub_html}</div>', p)
    S = f"#{cid}"
    rank = fit.seeded_order(n, X.rand)
    if head: X.tw(f'tl.from("{S} .lw-ttl .ct-l > span, {S} .d2-kick", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t:.3f});')
    t_in = t + 0.1; spread = min(0.7, 0.03 * n)
    for i in range(n):
        X.tw(f'tl.fromTo("{S} .lw-t[data-k=\'{i}\']", {{opacity:0, scale:0.86}}, {{opacity:0.28, scale:1, duration:0.4, ease:"power3.out"}}, {t_in + spread * rank[i] / max(1, n - 1):.3f});')
    t_hl = D.times(X, p, t, d, 1, key="t_hl", lead=d * 0.55)[0] if p.get("t_hl") else t + max(1.4, d * 0.55)
    light = max(0.4, min(t_hl - t_in - spread - 0.25, 0.09 * n + 0.4))
    for i in range(n):
        t_on = max(t_in + spread * rank[i] / max(1, n - 1) + 0.42, t_in + spread + 0.1 + light * rank[i] / max(1, n - 1))
        X.tw(f'tl.to("{S} .lw-t[data-k=\'{i}\']", {{opacity:1, duration:0.22, ease:"power2.out"}}, {t_on:.3f});')
    X.sfx(t_in + spread + 0.1, "pop")
    others = f"{S} .lw-t:not([data-k='{hl}'])"
    X.tw(f'tl.to("{others}", {{opacity:0.12, scale:0.94, duration:0.45, ease:"power2.out"}}, {t_hl:.3f});')
    X.tw(f'tl.to("{S} .lw-t[data-k=\'{hl}\']", {{x:{dx:.1f}, y:{dy:.1f}, scale:{s_hl:.3f}, zIndex:5, duration:0.75, ease:"expo.inOut"}}, {t_hl:.3f});')
    X.tw(f'tl.to("{S} .lw-t[data-k=\'{hl}\'] .lw-ring", {{opacity:1, duration:0.3}}, {t_hl + 0.3:.3f});')
    if sf: X.tw(f'tl.from("{S} .lw-sub .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t_hl + 0.55:.3f});')
    X.sfx(t_hl, "whoosh_soft")
    if t + d - (t_hl + 0.8) > 0.3:
        X.tw(f'tl.to("{S} .lw-t[data-k=\'{hl}\']", {{scale:{s_hl * 1.04:.3f}, duration:{t + d - t_hl - 0.8:.2f}, ease:"none"}}, {t_hl + 0.8:.3f});')


FX = {"logo_wall": logo_wall}
