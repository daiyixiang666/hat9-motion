"""股权穿透 / 组织架构 (ownership tree — 企查查/天眼查式股权图 in every 商业拆解; Envato "Organizational Chart" and
"Family Tree" infographic packs): the company lands first, the shareholders' lines draw out from it level by
level while each stake counts up, subsidiaries branch below; on a cue the controlling path lights up and a
summary badge (e.g. 「实际控制 85.56%」) pops. mode "org" turns it into a top-down org chart (no stakes).

Adapts: 1–8 nodes per level, 2–4 levels (holders of holders above, subsidiaries of subsidiaries below); names
of any length are fitted into the node; person nodes get a monogram, organisations a block.
p: root · holders [{name, pct, kind: person|org, note, holders:[…]}] · subs [{name, pct, role, note, subs:[…]}]
   · mode equity|org · hl [names to light] · summary · t_hl · mock
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
ORG = re.compile(r"公司|集团|资本|基金|平台|投资|合伙|有限|控股|银行|科技|信托|中心|Ltd|LLC|Inc|Capital|Fund|Holding|Partners|GP|LP", re.I)


def _node(v, key):
    if isinstance(v, dict): n = dict(v)
    elif isinstance(v, (list, tuple)): n = {"name": v[0], "pct": v[1] if len(v) > 1 else None}
    else: n = {"name": str(v)}
    kids = [_node(c, key) for c in FT.as_list(n.get(key))]
    n["_kids"] = kids
    if not n.get("kind"):
        nm = str(n.get("name", ""))
        n["kind"] = "org" if ORG.search(nm) else ("person" if 2 <= len(nm) <= 3 and not re.search(r"[A-Za-z]", nm) else "org")
    return n


def _leaves(n): return max(1, sum(_leaves(c) for c in n["_kids"])) if n["_kids"] else 1


def _depth(n): return 1 + max((_depth(c) for c in n["_kids"]), default=0)


def _place(n, x0, unit, lvl, out, parent=None):
    """tidy layout: leaves spaced by unit, parents centred over children. Appends (node, x, lvl, parent)."""
    if not n["_kids"]:
        x = x0 + unit / 2
    else:
        xs = []; cur = x0
        for c in n["_kids"]:
            w = _leaves(c) * unit
            xs.append(_place(c, cur, unit, lvl + 1, out, n)); cur += w
        x = sum(xs) / len(xs)
    out.append((n, x, lvl, parent))
    return x


def equity_tree(X, cid, t, d, p):
    SO.base_css(X)
    org = p.get("mode") == "org"
    root = _node(p.get("root", "公司"), "subs")
    holders = [] if org else [_node(h, "holders") for h in FT.as_list(p.get("holders"))[:8]]
    subs = [_node(s, "subs") for s in FT.as_list(p.get("subs"))[:8]] or root["_kids"][:8]
    root["_kids"] = []
    W, H, P = X.W, X.H, X.portrait
    bx0, bx1 = (50, W - 50) if P else (110, W - 110)
    by0, by1 = (280, 1270) if P else (150, 905)
    up = {"name": "_", "_kids": holders}
    dn = {"name": "_", "_kids": subs}
    nu = _depth(up) - 1 if holders else 0
    nd = _depth(dn) - 1 if subs else 0
    levels = nu + 1 + nd
    lw = max(_leaves(up) if holders else 1, _leaves(dn) if subs else 1)
    unit = (bx1 - bx0) / max(lw, 1)
    nw = min(SO.px(X, 30 if P else 27), unit * 0.9)
    nh = SO.px(X, 8.2 if levels <= 3 else 7.0)
    ys = [by0 + (by1 - by0) * (i + 0.5) / levels for i in range(levels)]
    cx = (bx0 + bx1) / 2
    placed = []                                    # (node, x, y, parent, side)
    if holders:
        tmp = []; _place(up, cx - _leaves(up) * unit / 2, unit, 0, tmp)
        for n, x, lv, par in tmp:
            if n is up: continue
            placed.append((n, x, ys[nu - lv], None if par is up else par, "up"))
    placed.append((root, cx, ys[nu], None, "root"))
    if subs:
        tmp = []; _place(dn, cx - _leaves(dn) * unit / 2, unit, 0, tmp)
        for n, x, lv, par in tmp:
            if n is dn: continue
            placed.append((n, x, ys[nu + lv], None if par is dn else par, "dn"))
    pos = {id(n): (x, y) for n, x, y, _, _ in placed}
    rw = min(nw * 1.25, SO.px(X, 36))
    hl = set(FT.as_list(p.get("hl")))
    nodes, edges, pcts, hl_edges, hl_nodes = [], [], [], [], set()
    order = {}
    for k, (n, x, y, par, side) in enumerate(placed):
        w = rw if side == "root" else nw
        nm = str(n.get("name", ""))
        sub = n.get("role") or n.get("note") or ""
        avw = nh * 0.62 if n["kind"] == "person" else 0
        tw = w - avw - SO.px(X, 3.2)
        f = FT.fit_text(nm, tw, nh * (0.5 if sub else 0.62), SO.px(X, 3.4 if side != "root" else 3.9), SO.px(X, 1.6), max_lines=2, lh=1.15)
        fs = f"<span>{X.rich(sub)}</span>" if sub else ""
        av = SO.avatar(X, nm, n.get("avatar"), "wpe-av", f"width:{avw:.0f}px; height:{avw:.0f}px; font-size:{avw * 0.45:.0f}px") if avw else ""
        cls = "root" if side == "root" else n["kind"]
        nodes.append(f'<div class="wpe-n {cls}" data-k="{k}" style="left:{x - w / 2:.0f}px; top:{y - nh / 2:.0f}px; width:{w:.0f}px; height:{nh:.0f}px">'
                     f'<i class="wpe-hi"></i>{av}<div class="wpe-t"><b style="font-size:{f.px}px">{"<br>".join(X.rich(l) for l in f.lines)}</b>{fs}</div></div>')
        order[id(n)] = k
    for n, x, y, par, side in placed:
        if side == "root": continue
        px_, py_ = pos[id(par)] if par is not None else (cx, ys[nu])
        k = order[id(n)]
        if side == "up":            # parent (lower) → this holder (upper): draw from the company outwards
            y0, y1 = py_ - nh / 2, y + nh / 2
        else:
            y0, y1 = py_ + nh / 2, y - nh / 2
        my = (y0 + y1) / 2
        dpath = f"M{px_:.1f},{y0:.1f} V{my:.1f} H{x:.1f} V{y1:.1f}"
        L = abs(my - y0) + abs(x - px_) + abs(y1 - my)
        edges.append(f'<path class="wpe-e" data-k="{k}" d="{dpath}" style="stroke-dasharray:{L:.1f}; stroke-dashoffset:{L:.1f}"/>')
        on_path = str(n.get("name")) in hl or any(str(c.get("name")) in hl for c in _desc(n))
        if on_path:
            hl_edges.append(f'<path class="wpe-eh" data-k="{k}" d="{dpath}" style="stroke-dasharray:{L:.1f}; stroke-dashoffset:{L:.1f}"/>'); hl_nodes.add(k)
        pv = n.get("pct")
        if pv is not None and pv != "":
            v = SO.num(pv)
            ly = (y1 + my) / 2 if side == "up" else (my + y1) / 2
            pcts.append(f'<div class="wpe-p" data-k="{k}" data-v="{v if v is not None else ""}" data-d="{len(str(pv).split(".")[1].rstrip("%")) if "." in str(pv) else 0}" '
                        f'style="left:{x:.0f}px; top:{ly:.0f}px">{X.rich(str(pv) if "%" in str(pv) or v is None else f"{pv}%")}</div>')
    if hl: hl_nodes.add(order[id(root)])
    X.css("fx-wpe", """
.fx .wpe { position:absolute; inset:0; font-family:var(--f-body); }
.fx .wpe svg { position:absolute; inset:0; width:100%; height:100%; overflow:visible; }
.fx .wpe-e { fill:none; stroke:color-mix(in srgb, var(--fg) 45%, transparent); stroke-width:3; stroke-linejoin:round; }
.fx .wpe-eh { fill:none; stroke:var(--accent); stroke-width:6; stroke-linejoin:round; stroke-linecap:round; }
.fx .wpe-n { position:absolute; display:flex; align-items:center; gap:1.2vmin; padding:0 1.6vmin; background:var(--card); color:var(--card-fg); border-radius:1.2vmin;
  box-shadow:0 0 0 .25vmin color-mix(in srgb, var(--card-fg) 16%, transparent), 0 1.6vmin 4vmin rgba(0,0,0,.18); }
.fx .wpe-n.person { border-radius:99vmin; padding-left:.8vmin; }
.fx .wpe-n.org { box-shadow:inset 0 .7vmin 0 color-mix(in srgb, var(--card-fg) 75%, transparent), 0 0 0 .25vmin color-mix(in srgb, var(--card-fg) 16%, transparent), 0 1.6vmin 4vmin rgba(0,0,0,.18); }
.fx .wpe-n.root { background:var(--fg); color:var(--bg); justify-content:center; text-align:center; }
.fx .wpe-hi { position:absolute; inset:-.5vmin; border-radius:inherit; box-shadow:0 0 0 .6vmin var(--accent); opacity:0; pointer-events:none; }
.fx .wpe-av { position:relative; }
.fx .wpe-t { position:relative; min-width:0; flex:1; display:flex; flex-direction:column; line-height:1.15; }
.fx .wpe-n.root .wpe-t { align-items:center; }
.fx .wpe-t b { font-weight:900; } .fx .wpe-t span { font-size:1.8vmin; opacity:.6; margin-top:.3vmin; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.fx .wpe-p { position:absolute; transform:translate(-50%,-50%); font:900 2.4vmin var(--f-num, var(--f-body)); font-variant-numeric:tabular-nums; color:var(--accent);
  background:var(--bg); padding:.2vmin 1vmin; border-radius:.6vmin; white-space:nowrap; }
.fx .wpe-sum { position:absolute; transform:translateY(-50%); font:900 3vmin var(--f-body); color:#fff; background:var(--accent); padding:1vmin 2vmin; border-radius:1vmin; white-space:nowrap; opacity:0; }
""")
    rx, ry = cx, ys[nu]
    summ = ""
    if p.get("summary"):
        sx = rx + rw / 2 + SO.px(X, 2.5)
        sy = ry
        if P: sx, sy = rx - SO.px(X, 20), ry + nh / 2 + SO.px(X, 4.5)
        summ = f'<div class="wpe-sum" style="left:{sx:.0f}px; top:{sy:.0f}px">{X.rich(p["summary"])}</div>'
    mock = f'<i class="wp-mock" style="right:{SO.px(X, 4):.0f}px; top:{by0 - SO.px(X, 4):.0f}px">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    inner = (f'<div class="wpe"><svg viewBox="0 0 {W} {H}">{"".join(edges)}{"".join(hl_edges)}</svg>{"".join(nodes)}{"".join(pcts)}{summ}{mock}</div>')
    X.used_text.update("0123456789.%")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    rk = order[id(root)]
    th = SO.cue(X, p, "t_hl", t, t + d * 0.7)
    X.tw(f'tl.from("{s} .wpe-n[data-k=\'{rk}\']", {{scale:0.5, opacity:0, duration:0.5, ease:"back.out(2)"}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "pop")
    # reveal level by level outwards from the company
    by_ring = {}
    for n, x, y, par, side in placed:
        if side == "root": continue
        ring = round(abs(y - ry) / max(1, (ys[1] - ys[0]) if levels > 1 else 1))
        by_ring.setdefault(ring, []).append(order[id(n)])
    t_avail = max(0.6, min(th, t + d - 0.4) - (t + 0.5))
    rings = sorted(by_ring)
    per = t_avail / max(len(rings), 1)
    for j, ring in enumerate(rings):
        tr = t + 0.5 + j * per
        ks = by_ring[ring]
        st = min(0.12, per * 0.4 / max(len(ks), 1))
        for q, k in enumerate(ks):
            tk = tr + q * st
            dur = min(0.7, per * 0.7)
            X.tw(f'tl.to("{s} .wpe-e[data-k=\'{k}\']", {{strokeDashoffset:0, duration:{dur:.2f}, ease:"power2.inOut"}}, {tk:.3f});')
            X.tw(f'tl.from("{s} .wpe-n[data-k=\'{k}\']", {{scale:0.6, opacity:0, duration:0.4, ease:"back.out(2)"}}, {tk + dur * 0.7:.3f});')
            X.tw(f'tl.from("{s} .wpe-p[data-k=\'{k}\']", {{opacity:0, scale:0.6, duration:0.3, ease:"back.out(2)"}}, {tk + dur * 0.5:.3f});')
            X.tw(f'(()=>{{const el=document.querySelector("{s} .wpe-p[data-k=\'{k}\']"); if(!el||el.dataset.v==="") return; const v=+el.dataset.v, dd=+el.dataset.d, o={{v:0}};'
                 f' tl.to(o, {{v:v, duration:{dur:.2f}, ease:"power2.out", onUpdate:()=>{{el.textContent=o.v.toFixed(dd)+"%";}}}}, {tk + dur * 0.5:.3f});}})();')
        X.sfx(tr, "line")
    if hl:
        X.tw(f'tl.to("{s} .wpe-eh", {{strokeDashoffset:0, duration:0.6, ease:"power2.inOut", stagger:0.05}}, {th:.3f});')
        dim = ", ".join(f'{s} .wpe-n[data-k=\'{k}\']' for k in range(len(placed)) if k not in hl_nodes)
        if dim: X.tw(f'tl.to("{dim}", {{opacity:0.35, duration:0.4}}, {th:.3f});')
        lit = ", ".join(f'{s} .wpe-n[data-k=\'{k}\'] .wpe-hi' for k in sorted(hl_nodes))
        if lit: X.tw(f'tl.to("{lit}", {{opacity:1, duration:0.3}}, {th + 0.2:.3f});')
        X.sfx(th, "hit")
    if summ:
        X.tw(f'tl.to("{s} .wpe-sum", {{opacity:1, duration:0.01}}, {th + 0.45:.3f});')
        X.tw(f'tl.from("{s} .wpe-sum", {{scale:0.5, x:-20, duration:0.45, ease:"back.out(2.2)"}}, {th + 0.45:.3f});')


def _desc(n):
    out = []
    for c in n["_kids"]: out.append(c); out += _desc(c)
    return out


FX = {"equity_tree": equity_tree}
