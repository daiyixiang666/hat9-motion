"""关系图：谁投资谁 (relation graph · the 「背后都是谁」 board of 商业拆解; Envato "Network / Connections Infographic"
packs, the detective-board look of 回形针 / 所长林超 videos): company and people cards are laid out automatically —
investors on one side and the invested on the other when the graph is two-sided, otherwise a hub with a ring —
then the links draw on as arrows with their amounts, thickness by value; competitors / partners are dashed arcs.
A highlight dims everything but one path.

p: nodes [str | {id, name, sub, img}] (names in edges are added automatically) · edges [{from, to, label, kind:
   invest|own|partner|compete, value}] · layout ("auto" | "columns" | "hub" | "ring") · hl ([from, to] or a node id) · t_hl
Adapts: 2–12 nodes (card size and type solved from the spacing), 1–20 edges, labels of any length (one line,
fitted; colliding labels are nudged apart), names of any script.
"""
import importlib.util, math, pathlib, sys
from h9 import fit as FT
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


U = _load("_ui")
SO = U.SO
DIRECTED = {"invest", "own", "fund", "acquire", ""}


def _graph(p):
    nodes, idx = [], {}
    def add(n):
        if isinstance(n, dict):
            k = str(n.get("id", n.get("name", "")))
            if k not in idx: idx[k] = len(nodes); nodes.append({"id": k, "name": str(n.get("name", k)), "sub": str(n.get("sub", "")), "img": n.get("img")})
        else:
            k = str(n)
            if k not in idx: idx[k] = len(nodes); nodes.append({"id": k, "name": k, "sub": "", "img": None})
        return idx[k if not isinstance(n, dict) else str(n.get("id", n.get("name", "")))]
    for n in FT.as_list(p.get("nodes")): add(n)
    edges = []
    for e in FT.as_list(p.get("edges")):
        if isinstance(e, (list, tuple)): e = {"from": e[0], "to": e[1], "label": e[2] if len(e) > 2 else ""}
        a, b = add(str(e.get("from"))), add(str(e.get("to")))
        if a == b: continue
        v = e.get("value")
        try: v = float(v) if v is not None else None
        except (TypeError, ValueError): v = None
        edges.append({"a": a, "b": b, "label": str(e.get("label", "")), "kind": str(e.get("kind", "invest")), "v": v})
    return nodes[:12], [e for e in edges if e["a"] < 12 and e["b"] < 12][:20]


def relation_graph(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    nodes, edges = _graph(p)
    n = len(nodes)
    if n < 2: raise SystemExit("relation_graph needs at least two nodes (or one edge)")
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 30
    aw, ah = x1 - x0, y1 - y0
    srcs = {e["a"] for e in edges if e["kind"] in DIRECTED}
    dsts = {e["b"] for e in edges if e["kind"] in DIRECTED}
    lay = p.get("layout", "auto")
    if lay == "auto":
        lay = "columns" if (srcs and dsts and not (srcs & dsts) and len(srcs | dsts) == n) else "hub"
    pos = {}
    if lay == "columns":
        L = [i for i in range(n) if i in srcs]
        R = [i for i in range(n) if i not in srcs]
        # order the right column by the mean rank of the sources pointing at it (fewer crossings)
        rank = {v: k for k, v in enumerate(L)}
        R.sort(key=lambda j: sum(rank[e["a"]] for e in edges if e["b"] == j and e["a"] in rank) / max(1, sum(1 for e in edges if e["b"] == j and e["a"] in rank)))
        for col, ids in ((0, L), (1, R)):
            m = len(ids)
            for k, i in enumerate(ids):
                f = (k + 0.5) / m
                if P: pos[i] = (x0 + aw * f, y0 + ah * (0.16 if col == 0 else 0.74))
                else: pos[i] = (x0 + aw * (0.17 if col == 0 else 0.8), y0 + 20 + (ah - 40) * f)
        span = (aw / max(len(L), len(R))) if P else ((ah - 40) / max(len(L), len(R)))
    else:
        deg = [sum(1 for e in edges if i in (e["a"], e["b"])) for i in range(n)]
        hub = max(range(n), key=lambda i: deg[i]) if lay == "hub" else None
        cx, cy = x0 + aw / 2, y0 + ah / 2
        ring = [i for i in range(n) if i != hub]
        rx, ry = (aw * 0.36, ah * 0.32) if P else (aw * 0.36, ah * 0.36)
        for k, i in enumerate(ring):
            a = -math.pi / 2 + 2 * math.pi * k / len(ring)
            pos[i] = (cx + rx * math.cos(a), cy + ry * math.sin(a))
        if hub is not None: pos[hub] = (cx, cy)
        span = 2 * math.pi * min(rx, ry) / max(1, len(ring))
    cw = max(170, min(360 if not P else 300, span * (0.9 if lay == "columns" and not P else 0.82)))
    if lay == "columns" and not P: cw = min(cw * 2.2, 420)
    chh = max(64, min(110, (span * 0.62) if lay == "columns" and not P else cw * 0.42))
    av = chh * 0.62
    cards = []
    for i, nd in enumerate(nodes):
        x, y = pos[i]
        nf = FT.fit_text(nd["name"], cw - av - 46, chh * 0.42, chh * 0.34, 14, max_lines=1)
        sub = f'<em style="font-size:{max(12, nf.px * 0.56):.0f}px">{X.rich(nd["sub"])}</em>' if nd["sub"] else ""
        cards.append(f'<div class="rg-n" data-i="{i}" style="left:{x - cw / 2:.0f}px; top:{y - chh / 2:.0f}px; width:{cw:.0f}px; height:{chh:.0f}px">'
                     f'{U.avatar(X, nd["name"], nd.get("img"), style=f"width:{av:.0f}px; height:{av:.0f}px; font-size:{av * 0.46:.0f}px")}'
                     f'<span><b style="font-size:{nf.px}px">{X.rich(nf.lines[0] if nf.lines else nd["name"])}</b>{sub}</span><i class="rg-ring"></i></div>')
    vmax = max([e["v"] for e in edges if e["v"]] or [1])
    paths, chips, mids = [], [], []
    for j, e in enumerate(edges):
        (ax, ay), (bx, by) = pos[e["a"]], pos[e["b"]]
        und = e["kind"] not in DIRECTED
        if lay == "columns" and not und:
            if P: sx, sy, ex, ey = ax, ay + chh / 2, bx, by - chh / 2 - 12; c1, c2 = (sx, sy + (ey - sy) * 0.5), (ex, ey - (ey - sy) * 0.5)
            else: sx, sy, ex, ey = ax + cw / 2, ay, bx - cw / 2 - 12, by; c1, c2 = (sx + (ex - sx) * 0.5, sy), (ex - (ex - sx) * 0.5, ey)
            dpath = f"M{sx:.1f} {sy:.1f} C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {ex:.1f} {ey:.1f}"
            mx, my = (sx + 3 * c1[0] + 3 * c2[0] + ex) / 8, (sy + 3 * c1[1] + 3 * c2[1] + ey) / 8
        else:
            # trim to the card edges along the line, bend sideways
            dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            tr_a = min(cw / 2 / max(abs(ux), 1e-3), chh / 2 / max(abs(uy), 1e-3)) + 6
            tr_b = tr_a + (0 if und else 12)
            sx, sy, ex, ey = ax + ux * tr_a, ay + uy * tr_a, bx - ux * tr_b, by - uy * tr_b
            bend = (0.32 if und else 0.12) * L
            if und and lay == "columns":
                bend = 0.45 * L
            qx, qy = (sx + ex) / 2 - uy * bend, (sy + ey) / 2 + ux * bend
            dpath = f"M{sx:.1f} {sy:.1f} Q{qx:.1f} {qy:.1f} {ex:.1f} {ey:.1f}"
            mx, my = (sx + 2 * qx + ex) / 4, (sy + 2 * qy + ey) / 4
        if e["label"]:                             # nudge colliding labels apart (estimated chip boxes)
            lpx = 26 if not P else 24
            lw, lh = FT.width(e["label"]) * lpx + 32, lpx * 1.7
            base, k = my, 0
            while k < 8 and any(abs(ox - mx) < (lw + ow) / 2 + 8 and abs(oy - my) < (lh + oh) / 2 + 4 for ox, oy, ow, oh in mids):
                k += 1; my = base + ((k + 1) // 2) * (lh + 8) * (1 if k % 2 else -1)
            mids.append((mx, my, lw, lh))
        sw = 3 + (7 * math.sqrt(e["v"] / vmax) if e["v"] else 2)
        cls = "rg-e cmp" if e["kind"] in ("compete", "rival") else ("rg-e und" if und else "rg-e")
        e["arrow"] = not und     # the arrowhead is attached once the link has drawn (a marker ignores the dash reveal)
        paths.append(f'<path class="{cls}" data-j="{j}" d="{dpath}" pathLength="1" style="stroke-width:{sw:.1f}"/>')
        if e["label"]:
            lf = FT.fit_text(e["label"], 340, 40, 26 if not P else 24, 14, max_lines=1)
            chips.append(f'<div class="rg-l{" cmp" if e["kind"] in ("compete", "rival") else ""}" data-j="{j}" style="left:{mx:.0f}px; top:{my:.0f}px; font-size:{lf.px}px">{X.rich(lf.lines[0] if lf.lines else e["label"])}</div>')
    svg = (f'<svg class="rg-svg" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}"><defs><marker id="rgA_{cid}" viewBox="0 0 10 10" refX="2" refY="5" markerWidth="4.2" markerHeight="4.2" orient="auto-start-reverse">'
           f'<path d="M0 0 L10 5 L0 10 z" class="rg-ah"/></marker></defs>{"".join(paths)}</svg>')
    X.css("fx-relation-graph", """
.rg-svg { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.rg-e { fill:none; stroke:var(--accent); stroke-linecap:round; stroke-dasharray:1 1; stroke-dashoffset:1; }
.rg-e.und { stroke:var(--muted); }
.rg-e.cmp { stroke:var(--alert, var(--accent)); }
.rg-ah { fill:var(--accent); }
.rg-n { position:absolute; display:flex; align-items:center; gap:14px; padding:0 18px 0 12px; border-radius:16px; background:var(--card); color:var(--card-fg);
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 12%, transparent), 0 16px 36px rgba(0,0,0,.16); box-sizing:border-box; }
.rg-n span { display:flex; flex-direction:column; min-width:0; gap:2px; }
.rg-n b { font-family:var(--f-display, var(--f-body)); font-weight:900; white-space:nowrap; line-height:1.1; }
.rg-n em { font-style:normal; font-family:var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 55%, transparent); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rg-ring { position:absolute; inset:-6px; border-radius:20px; border:4px solid var(--accent); opacity:0; }
.rg-l { position:absolute; opacity:0; white-space:nowrap; font-family:var(--f-body); font-weight:800; color:var(--bg); background:var(--fg); padding:5px 14px; border-radius:999px; z-index:3; }
.rg-l.cmp { background:var(--card); color:var(--card-fg); box-shadow:0 0 0 2px var(--alert, var(--accent)); }
""")
    mk = U.mock(X, p, x1, y0 - 20, right=True)
    _clip(X, cid, t, d, f'{svg}{"".join(chips)}{"".join(cards)}{mk}', p)
    s = f"#{cid}"
    X.tw(f'tl.set("{s} .rg-l", {{xPercent:-50, yPercent:-50}}, {t:.3f});')
    order = sorted(range(n), key=lambda i: (pos[i][0] if not P else pos[i][1], pos[i][1] if not P else pos[i][0]))
    for k, i in enumerate(order):
        X.tw(f'tl.from("{s} .rg-n[data-i=\'{i}\']", {{scale:0.6, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.1 + k * 0.08:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")
    te0 = t + 0.4 + 0.08 * n
    th = U.when(X, p.get("t_hl"), t, t + d * 0.72) if p.get("hl") is not None else t + d
    per = max(0.3, min(0.7, (th - te0 - 0.4) / max(1, len(edges))))
    for j, e in enumerate(edges):
        tj = te0 + j * per
        dj = max(0.35, per * 1.1)
        X.tw(f'tl.to("{s} .rg-e[data-j=\'{j}\']", {{strokeDashoffset:0, duration:{dj:.2f}, ease:"power2.inOut"}}, {tj:.3f});')
        if e.get("arrow"): X.tw(f'tl.set("{s} .rg-e[data-j=\'{j}\']", {{attr:{{"marker-end":"url(#rgA_{cid})"}}}}, {tj + dj * 0.82:.3f});')
        X.tw(f'tl.fromTo("{s} .rg-l[data-j=\'{j}\']", {{scale:0.5, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(2.5)", immediateRender:false}}, {tj + max(0.3, per * 0.9):.3f});')
        X.sfx(tj + max(0.3, per * 0.9), "pop")
    hl = p.get("hl")
    if hl is not None:
        idx = {nd["id"]: i for i, nd in enumerate(nodes)}
        keep_n, keep_e = set(), set()
        if isinstance(hl, (list, tuple)) and len(hl) == 2:
            a, b = idx.get(str(hl[0])), idx.get(str(hl[1]))
            keep_n = {a, b}; keep_e = {j for j, e in enumerate(edges) if {e["a"], e["b"]} == {a, b}}
        else:
            a = idx.get(str(hl)); keep_n = {a}; keep_e = {j for j, e in enumerate(edges) if a in (e["a"], e["b"])}
            keep_n |= {edges[j]["a"] for j in keep_e} | {edges[j]["b"] for j in keep_e}
        for i in range(n):
            if i not in keep_n: X.tw(f'tl.to("{s} .rg-n[data-i=\'{i}\']", {{opacity:0.28, duration:0.35}}, {th:.3f});')
            else: X.tw(f'tl.to("{s} .rg-n[data-i=\'{i}\'] .rg-ring", {{opacity:1, duration:0.3}}, {th:.3f});')
        for j in range(len(edges)):
            if j not in keep_e: X.tw(f'tl.to("{s} .rg-e[data-j=\'{j}\'], {s} .rg-l[data-j=\'{j}\']", {{opacity:0.2, duration:0.35}}, {th:.3f});')
            else: X.tw(f'tl.fromTo("{s} .rg-l[data-j=\'{j}\']", {{scale:1}}, {{scale:1.15, duration:0.3, ease:"back.out(3)", immediateRender:false}}, {th:.3f});')
        X.sfx(th, "hit")


FX = {"relation_graph": relation_graph}
