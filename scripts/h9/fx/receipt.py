"""小票 (printed receipt — 「一张小票看懂客单价」, the go-to prop for 消费 / 餐饮 拆解; Envato "Receipt" mockups): a
thermal receipt feeds out of a printer slot, line by line, items with quantity and price, then the total lands
large and gets a marker sweep; a long receipt keeps feeding (the paper scrolls). Totals are computed from the
lines unless given. A barcode closes it.

Adapts: 1–24 lines (names of any length, ellipsized to the paper), optional discount / note / time / number.
p: store · items [[name, qty, price] | "名称 ×2 ¥8" | {name, qty, price}] · currency · discount · total · paid
   · time · no · note · t_total · mock
"""
from h9.aefx import _clip
from h9 import fit as FT
import importlib.util, pathlib, random, re, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")


def _row(it):
    if isinstance(it, dict): return str(it.get("name", "")), SO.num(it.get("qty")) or 1, SO.num(it.get("price")) or 0
    if isinstance(it, (list, tuple)): return str(it[0]), SO.num(it[1] if len(it) > 2 else 1) or 1, SO.num(it[-1]) or 0
    m = re.match(r"^(.*?)\s*[×x\*]\s*(\d+)\s*[¥$€]?\s*([\d.]+)\s*$", str(it))
    if m: return m.group(1).strip(), float(m.group(2)), float(m.group(3))
    m = re.match(r"^(.*?)\s*[¥$€]?\s*([\d.]+)\s*$", str(it))
    return (m.group(1).strip(), 1, float(m.group(2))) if m else (str(it), 1, 0)


def receipt(X, cid, t, d, p):
    SO.base_css(X)
    rows = [_row(it) for it in FT.as_list(p.get("items"))][:24] or [("商品", 1, 0)]
    cur = p.get("currency", "¥")
    sub = sum(q * pr for _, q, pr in rows)
    disc = SO.num(p.get("discount")) or 0
    total = SO.num(p.get("total")) if p.get("total") is not None else sub - disc
    P = X.portrait
    pw = 72.0 if P else 58.0
    fs = 3.0 if P else 2.7
    if len(rows) > 12: fs *= 0.9
    money = lambda v: f"{cur}{v:,.2f}".rstrip("0").rstrip(".") if v != int(v) else f"{cur}{int(v):,}"
    lines = [f'<div class="wpr-st">{X.rich(p.get("store", "某某小店"))}</div>']
    meta = " · ".join(x for x in (p.get("time"), (f'No.{p["no"]}' if p.get("no") else None)) if x)
    if meta: lines.append(f'<div class="wpr-mt">{X.rich(meta)}</div>')
    lines.append('<div class="wpr-hr"></div>')
    namew = int((pw - 22) / fs)
    for nm, q, pr in rows:
        nm_s = nm if FT.width(nm) <= namew else nm[: max(1, namew - 1)] + "…"
        lines.append(f'<div class="wpr-it"><span class="n">{X.rich(nm_s)}</span><span class="q">×{int(q)}</span><span class="p">{X.rich(money(q * pr))}</span></div>')
    lines.append('<div class="wpr-hr"></div>')
    if disc:
        lines.append(f'<div class="wpr-it"><span class="n">小计</span><span class="q"></span><span class="p">{X.rich(money(sub))}</span></div>')
        lines.append(f'<div class="wpr-it"><span class="n">优惠</span><span class="q"></span><span class="p">-{X.rich(money(disc))}</span></div>')
    lines.append(f'<div class="wpr-tt"><span>合计</span><b><i class="wpr-mk"></i><em>{X.rich(money(total))}</em></b></div>')
    if p.get("paid"): lines.append(f'<div class="wpr-mt">{X.rich(p["paid"])}</div>')
    if p.get("note"): lines.append(f'<div class="wpr-nt">{X.rich(p["note"])}</div>')
    rnd = random.Random(int(p.get("seed", 5)))
    bars = "".join(f'<i style="width:{rnd.choice([1, 1, 2, 3])}px; margin-right:{rnd.choice([1, 2, 2, 3])}px"></i>' for _ in range(70))
    lines.append(f'<div class="wpr-bc">{bars}</div>')
    body = "".join(f'<div class="wpr-l" data-k="{k}">{l}</div>' for k, l in enumerate(lines))
    nl = len(lines)
    est_h = nl * fs * 1.75 + 16                         # vmin
    view_h = 92.0 if P else 78.0
    X.css("fx-wpr", """
.fx .wpr { position:relative; display:flex; flex-direction:column; align-items:center; }
#root.v .fx .wpr { margin-top:-14vmin; }
.fx .wpr-slot { position:relative; z-index:2; height:5vmin; border-radius:1.4vmin; background:linear-gradient(180deg, color-mix(in srgb, var(--fg) 85%, var(--bg)), var(--fg));
  box-shadow:0 2vmin 4vmin rgba(0,0,0,.3); }
.fx .wpr-slot::after { content:''; position:absolute; left:6%; right:6%; bottom:1.2vmin; height:.7vmin; border-radius:.35vmin; background:#000; opacity:.6; }
.fx .wpr-win { position:relative; overflow:hidden; margin-top:-2.2vmin; }
.fx .wpr-pp { position:absolute; left:0; right:0; top:0; background:#fbfaf6; color:#1a1a1a; padding:6vmin 3.2vmin 3vmin; font-family:var(--f-mono, monospace);
  box-shadow:0 2vmin 5vmin rgba(0,0,0,.25); -webkit-mask:linear-gradient(#000, #000) top/100% calc(100% - 1.4vmin) no-repeat, radial-gradient(circle at 50% 0, transparent .9vmin, #000 1vmin) bottom/2.4vmin 1.4vmin repeat-x; }
.fx .wpr-l { line-height:1.75; }
.fx .wpr-st { text-align:center; font-family:var(--f-body); font-weight:900; font-size:1.35em; }
.fx .wpr-mt { text-align:center; opacity:.6; font-size:.85em; }
.fx .wpr-nt { text-align:center; font-size:.85em; opacity:.75; font-family:var(--f-body); }
.fx .wpr-hr { border-top:.25vmin dashed rgba(0,0,0,.45); margin:.9vmin 0; }
.fx .wpr-it { display:grid; grid-template-columns:minmax(0, 1fr) 4em 6em; gap:1vmin; font-family:var(--f-body); }
.fx .wpr-it .n { white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.fx .wpr-it .q { text-align:center; opacity:.65; font-family:var(--f-mono, monospace); } .fx .wpr-it .p { text-align:right; font-family:var(--f-mono, monospace); }
.fx .wpr-tt { display:flex; justify-content:space-between; align-items:baseline; font-family:var(--f-body); font-weight:900; font-size:1.25em; margin-top:.6vmin; }
.fx .wpr-tt b { position:relative; font:900 2em var(--f-num, var(--f-mono, monospace)); }
.fx .wpr-tt b em { position:relative; font-style:normal; }
.fx .wpr-mk { position:absolute; left:-.1em; right:-.1em; bottom:.12em; height:.42em; background:#f6ce3a; transform-origin:0 50%; }
.fx .wpr-bc { display:flex; justify-content:center; height:5vmin; margin-top:1.6vmin; } .fx .wpr-bc i { display:block; height:100%; background:#1a1a1a; }
""")
    mock = f'<i class="wp-mock" style="right:-8vmin; top:6vmin">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    win_h = min(view_h, est_h)
    inner = (f'<div class="wpr" style="font-size:{fs:.2f}vmin">{mock}<div class="wpr-slot" style="width:{pw + 6:.1f}vmin"></div>'
             f'<div class="wpr-win" style="width:{pw:.1f}vmin; height:{win_h:.1f}vmin"><div class="wpr-pp">{body}</div></div></div>')
    X.used_text.update("×合计小计优惠¥$0123456789.,-No某某小店…")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    tt = SO.cue(X, p, "t_total", t, t + d * 0.72)
    X.tw(f'tl.from("{s} .wpr-slot", {{y:-30, opacity:0, duration:0.45, ease:"expo.out"}}, {t:.3f});')
    # paper feeds: it starts tucked up inside the slot and slides down as lines print
    X.tw(f'tl.fromTo("{s} .wpr-pp", {{yPercent:-100}}, {{yPercent:0, duration:{max(0.6, tt - t - 0.3):.2f}, ease:"power1.inOut"}}, {t + 0.25:.3f});')
    step = max(0.05, (tt - t - 0.5) / max(nl, 1))
    X.tw(f'tl.from("{s} .wpr-l", {{opacity:0, duration:0.05, stagger:{step:.3f}, ease:"none"}}, {t + 0.35:.3f});')
    if est_h > view_h:     # long receipts keep feeding upward after the window fills
        X.tw(f'tl.to("{s} .wpr-pp", {{y:"{-(est_h - view_h):.1f}vmin", duration:{max(0.5, tt - t - 1.0):.2f}, ease:"none"}}, {t + 0.9:.3f});')
    X.tw(f'tl.fromTo("{s} .wpr-mk", {{scaleX:0}}, {{scaleX:1, duration:0.4, ease:"power3.out", immediateRender:true}}, {tt:.3f});')
    X.tw(f'tl.fromTo("{s} .wpr-tt b", {{scale:1}}, {{keyframes:[{{scale:1.12, duration:0.12}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], transformOrigin:"100% 50%"}}, {tt:.3f});')
    X.sfx(t + 0.3, "type"); X.sfx(tt, "hit")


FX = {"receipt": receipt}
