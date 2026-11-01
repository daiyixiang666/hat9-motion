"""决策树 / 分叉 Decision tree (Envato Popular「Infographics 6 Roadmaps」; VideoHive Infographic Maker 2.6K; the
「如果……就……」branching chart of advice videos): the first question lands, branches grow level by level with
their yes / no tags, then one path lights up end to end — a dot travels down it — and the answer it reaches pops,
while the paths not taken fade back.

Adapts: 2–5 levels and up to ~12 leaves (spacing from the leaf count; 16:9 grows left → right, 9:16 top → down),
node text from a word to a sentence (fitted, 2 lines), any branch labels (default 是 / 否), binary or n-ary
branches. The tree is nested: {"q": "...", "branches": [["是", {...}], ["否", "结论"]]} or the {"q", "yes", "no"}
shorthand; a leaf is a string or {"a": "...", "good": true|false}.
p: tree · path [branch labels or indices] · title · note · mock
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


def _norm(node):
    if isinstance(node, str): return {"leaf": True, "text": node, "good": None, "kids": []}
    if "a" in node and "q" not in node: return {"leaf": True, "text": node["a"], "good": node.get("good"), "kids": []}
    br = node.get("branches") or [[k, node[k]] for k in ("yes", "no") if k in node]
    lab = {"yes": "是", "no": "否"}
    return {"leaf": False, "text": node["q"], "kids": [(lab.get(str(b[0]), str(b[0])), _norm(b[1])) for b in br]}


def decision_tree(X, cid, t, d, p):
    W.base(X)
    root = _norm(p["tree"])
    nodes = []

    def walk(nd, depth, parent, blab):
        i = len(nodes); nd["i"] = i; nd["depth"] = depth; nd["parent"] = parent; nd["blab"] = blab
        nodes.append(nd)
        for lab, k in nd["kids"]: walk(k, depth + 1, i, lab)
    walk(root, 0, None, None)
    leaves = [nd for nd in nodes if not nd["kids"]]
    for j, nd in enumerate(leaves): nd["slot"] = j

    def slot(nd):
        if not nd["kids"]: return nd["slot"]
        ss = [slot(k) for _, k in nd["kids"]]; nd["slot"] = (min(ss) + max(ss)) / 2; return nd["slot"]
    slot(root)
    depth = max(nd["depth"] for nd in nodes) + 1
    # chosen path
    on = {0}
    cur = root
    for step in p.get("path", []):
        if not cur["kids"]: break
        k = next((k for lab, k in cur["kids"] if lab == str(step) or {"yes": "是", "no": "否"}.get(str(step)) == lab), None)
        if k is None and isinstance(step, int) and step < len(cur["kids"]): k = cur["kids"][step][1]
        if k is None: break
        on.add(k["i"]); cur = k
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx
    L = len(leaves)
    down = P and L <= 4      # 9:16 grows top -> down; a wide tree (5+ leaves) grows left -> right there too, so nodes stay readable
    if down:   # top -> down: depth on y, slots on x
        nw = min(300, (x1 - x0 - 20 * (L - 1)) / L) if L > 1 else 420
        nh = min(130, (y1 - top - 60 * (depth - 1)) / depth)
        gy = (y1 - top - nh) / max(1, depth - 1)
        gx = (x1 - x0 - nw) / max(1, L - 1) if L > 1 else 0
        pos = lambda nd: (x0 + (nd["slot"] * gx if L > 1 else (x1 - x0 - nw) / 2), top + nd["depth"] * gy)
    else:   # left -> right
        nw = min(360, (x1 - x0 - 90 * (depth - 1)) / depth)
        nh = min(120, (y1 - top - 16 * (L - 1)) / L)
        gx = (x1 - x0 - nw) / max(1, depth - 1)
        gy = (y1 - top - nh) / max(1, L - 1) if L > 1 else 0
        pos = lambda nd: (x0 + nd["depth"] * gx, top + (nd["slot"] * gy if L > 1 else (y1 - top - nh) / 2))
    html, edges, tags = [], [], []
    path_pts = []
    for nd in nodes:
        x, y = pos(nd)
        nd["xy"] = (x, y)
        fs, fl = W.fit_px(X, nd["text"], nw - 36, nh - 20, 34 if not P else 28, 18, 2)
        cls = "dtn" + (" lf" if not nd["kids"] else "") + (" on" if nd["i"] in on else "") + (" good" if nd.get("good") else " bad" if nd.get("good") is False else "")
        html.append(f'<div class="{cls}" data-i="{nd["i"]}" data-d="{nd["depth"]}" style="left:{x:.0f}px; top:{y:.0f}px; width:{nw:.0f}px; height:{nh:.0f}px; font-size:{fs:.0f}px">{W.lines_html(X, fl)}</div>')
    for nd in nodes:
        if nd["parent"] is None: continue
        pa = nodes[nd["parent"]]
        (px_, py_), (cx_, cy_) = pa["xy"], nd["xy"]
        if down:
            a = (px_ + nw / 2, py_ + nh); b = (cx_ + nw / 2, cy_); my = (a[1] + b[1]) / 2
            dd = f"M{a[0]:.1f},{a[1]:.1f} L{a[0]:.1f},{my:.1f} L{b[0]:.1f},{my:.1f} L{b[0]:.1f},{b[1]:.1f}"
            pts = [a, (a[0], my), (b[0], my), b]
            tx, ty = b[0], my - 16
        else:
            a = (px_ + nw, py_ + nh / 2); b = (cx_, cy_ + nh / 2); mx = (a[0] + b[0]) / 2
            dd = f"M{a[0]:.1f},{a[1]:.1f} L{mx:.1f},{a[1]:.1f} L{mx:.1f},{b[1]:.1f} L{b[0]:.1f},{b[1]:.1f}"
            pts = [a, (mx, a[1]), (mx, b[1]), b]
            tx, ty = (mx + b[0]) / 2, b[1] - 34
        is_on = nd["i"] in on and pa["i"] in on
        edges.append(f'<path class="dte{" on" if is_on else ""}" data-d="{nd["depth"]}" d="{dd}" pathLength="1"/>')
        tags.append(f'<div class="dtt{" on" if is_on else ""}" data-d="{nd["depth"]}" style="left:{tx:.0f}px; top:{ty:.0f}px">{X.rich(nd["blab"])}</div>')
        if is_on: path_pts.append((nd["depth"], pts))
    path_pts.sort()
    X.css("fx-dtree", """
.fx .dt .dtn { position:absolute; display:flex; flex-direction:column; justify-content:center; padding:0 18px; border-radius:12px; background:var(--card); color:var(--card-fg);
  box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--fg) 16%, transparent); font-family:var(--f-body); font-weight:800; line-height:1.2; }
.fx .dt .dtn .fl { display:block; white-space:nowrap; }
.fx .dt .dtn.lf { border-radius:999px; align-items:center; text-align:center; }
.fx .dt .dtn.on { box-shadow:inset 0 0 0 4px var(--accent); }
.fx .dt .dtn.lf.on { background:var(--accent); color:var(--bg); box-shadow:none; }
.fx .dt .dte { fill:none; stroke:color-mix(in srgb, var(--fg) 30%, transparent); stroke-width:3; }
.fx .dt .dte.on { stroke:var(--accent); stroke-width:6; }
.fx .dt .dtt { position:absolute; transform:translateX(-50%); font:800 20px var(--f-body); color:var(--muted); background:var(--bg); padding:0 8px; white-space:nowrap; }
.fx .dt .dtt.on { color:var(--accent); }
.fx .dt .dtdot { position:absolute; left:0; top:0; width:20px; height:20px; margin:-10px 0 0 -10px; border-radius:50%; background:var(--accent); box-shadow:0 0 0 5px var(--bg), 0 0 18px var(--accent); opacity:0; }
""")
    svg = f'<svg class="w3s" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(edges)}</svg>'
    inner = f'<div class="w3 dt">{hh}{svg}{"".join(tags)}{"".join(html)}<i class="dtdot"></i>{W.mock_tag(X, p, x1 - 70, y0)}</div>'
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    lv = min(0.45, max(0.25, (d * 0.35) / depth))
    for k in range(depth):
        tk = t + 0.25 + k * lv
        if k > 0:
            X.tw(f'tl.fromTo("{s} .dte[data-d=\'{k}\']", {{strokeDasharray:1, strokeDashoffset:1}}, {{strokeDashoffset:0, duration:{lv:.2f}, ease:"power2.inOut"}}, {tk - lv * 0.5:.3f});')
            X.tw(f'tl.from("{s} .dtt[data-d=\'{k}\']", {{opacity:0, scale:0.6, duration:0.3}}, {tk:.3f});')
        X.tw(f'tl.from("{s} .dtn[data-d=\'{k}\']", {{scale:0.6, opacity:0, duration:0.4, ease:"back.out(2)", stagger:0.05}}, {tk:.3f});')
        X.sfx(tk, "pop")
    tp = t + 0.25 + (depth - 1) * lv + min(1.5, max(0.5, d * 0.27))     # the last level stays readable before the others fade
    X.tw(f'tl.to("{s} .dtn:not(.on), {s} .dte:not(.on), {s} .dtt:not(.on)", {{opacity:0.28, duration:0.4}}, {tp:.3f});')
    seg = min(0.5, max(0.25, (t + d - tp - 0.6) / max(1, len(path_pts))))
    tt = tp + 0.1
    for _, pts in path_pts:
        W.travel(X, f"{s} .dtdot", pts, tt, seg)
        tt += seg
    leaf = [i for i in on if not nodes[i]["kids"]]
    if leaf:
        X.tw(f'tl.fromTo("{s} .dtn[data-i=\'{leaf[0]}\']", {{scale:1}}, {{keyframes:[{{scale:1.12, duration:0.14}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tt:.3f});')
        X.sfx(tt, "hit")


FX = {"decision_tree": decision_tree}
