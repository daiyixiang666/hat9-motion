"""排行榜倒数 Countdown Ranking (盘点类「年度十大」的固定格式; talkcraft number-slab-pop / count-badge-title;
VideoHive Infographics 包里的 Leaderboard / Top List): the board fills from the bottom — last place first —
each row flipping in with its value counting up behind a bar; before No.1 the board holds on a hidden card,
the rest dims, then the card flips over to the winner in the accent with a burst.

Adapts: 2–15 entries (one column up to 8 in 16:9 / 10 in 9:16, then two), names a word to a phrase (one shared
size, ≤ 2 lines), values optional (bars only when every entry has one; huge numbers shown as 万 / 亿), sub-lines.
p: items [[name, value?, sub?] | {"name", "value", "sub"}] (No.1 first) · unit · title · hide_top (default true)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .rk { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .rk .rk-k { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; }
.fx .rk .rk-k .sl { display:block; white-space:nowrap; }
.fx .rk .rk-r { position:absolute; perspective:1200px; }
.fx .rk .rk-in { position:absolute; inset:0; display:flex; align-items:center; gap:2.2vmin; padding:0 2.4vmin 0 1.2vmin; border-radius:1vmin;
  background:color-mix(in srgb, var(--fg) 6%, transparent); transform-origin:50% 50%; backface-visibility:hidden; overflow:hidden; }
.fx .rk .rk-bar { position:absolute; left:0; top:0; bottom:0; background:color-mix(in srgb, var(--fg) 12%, transparent); transform-origin:0 50%; }
.fx .rk .rk-no { position:relative; flex:none; text-align:center; font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--fg); line-height:1; font-variant-numeric:tabular-nums; }
.fx .rk .rk-nm { position:relative; flex:1; min-width:0; font-family:var(--f-display); font-weight:800; color:var(--fg); line-height:1.15; }
.fx .rk .rk-nm .sl, .fx .rk .rk-sb .sl { display:block; white-space:nowrap; }
.fx .rk .rk-sb { font-family:var(--f-body); font-weight:500; color:var(--muted); line-height:1.25; margin-top:.3vmin; }
.fx .rk .rk-v { position:relative; flex:none; font-family:var(--f-num, var(--f-display)); font-weight:800; color:var(--fg); font-variant-numeric:tabular-nums; white-space:nowrap; }
.fx .rk .rk-v small { font-family:var(--f-body); font-weight:700; margin-left:.3vmin; }
.fx .rk .rk-q { position:absolute; inset:0; display:grid; place-items:center; border-radius:1vmin; background:var(--fg); color:var(--bg);
  font-family:var(--f-display); font-weight:900; backface-visibility:hidden; }
.fx .rk .rk-r.top .rk-in { background:var(--accent); }
.fx .rk .rk-r.top .rk-no, .fx .rk .rk-r.top .rk-nm, .fx .rk .rk-r.top .rk-v, .fx .rk .rk-r.top .rk-sb { color:var(--bg); }
.fx .rk .rk-r.top .rk-bar { background:color-mix(in srgb, var(--bg) 14%, transparent); }
.fx .rk .rk-burst { position:absolute; left:0; top:0; width:0; height:0; }
.fx .rk .rk-burst i { position:absolute; left:0; top:0; width:.5vmin; background:var(--accent); transform-origin:50% 0; border-radius:.3vmin; }
"""


def _items(v):
    out = []
    for it in fit.as_list(v):
        if isinstance(it, dict): out.append((str(it.get("name") or it.get("text") or ""), it.get("value"), str(it.get("sub") or "")))
        elif isinstance(it, (list, tuple)):
            out.append((str(it[0]), it[1] if len(it) > 1 else None, str(it[2]) if len(it) > 2 and it[2] else ""))
        else: out.append((str(it), None, ""))
    return out


def ranking(X, cid, t, d, p):
    its = (_items(p.get("items")) or [("第一名", None, "")])[:15]
    n = len(its)
    x, y, w, h = S.box(X, p)
    title = fit.as_text(p.get("title"))
    kh = 0
    if title:
        kf = fit.fit_text(title, w * 0.9, S.vm(X, 12), S.vm(X, 6 if X.portrait else 5.2), S.vm(X, 3.2), max_lines=2)
        kh = kf.n * kf.px * 1.12 + S.vm(X, 3)
    cap = 10 if X.portrait else 8
    cols = 1 if n <= cap else 2
    per = -(-n // cols)
    gx = S.vm(X, 3)
    cw = (w - gx * (cols - 1)) / cols
    if not X.portrait and cols == 1: cw = min(cw, w * 0.78)
    area = h - kh
    rh = min(area / per, S.vm(X, 15 if n <= 4 else 12) if X.portrait else S.vm(X, 20 if n <= 3 else 16 if n <= 5 else 12.5))
    gap = rh * 0.14
    ih = rh - gap
    vals = [S.num(v) for _, v, _ in its]
    has_v = all(v is not None for v in vals)
    vmax = max((abs(v) for v in vals if v is not None), default=0) or 1
    unit = fit.as_text(p.get("unit"))
    vtxt = [(fit.fmt_num(v, zh=False) if abs(v) < 1e6 else fit.fmt_num(v)) if v is not None else "" for v in vals]
    nopx = ih * 0.62
    now = fit.width(str(n)) * nopx + S.vm(X, 1)
    vpx = min(ih * 0.42, S.vm(X, 5))
    vw = max((fit.width(v) * vpx + fit.width(unit) * vpx * 0.55 for v in vtxt), default=0) + S.vm(X, 1)
    nw = cw - now - vw - S.vm(X, 12)
    has_sub = any(sb for _, _, sb in its)
    npx, nfs = S.fitpx([a for a, _, _ in its], nw, ih * (0.6 if has_sub else 0.84), min(ih * 0.48, S.vm(X, 6)), S.vm(X, 2.6), max_lines=2)
    spx, sfs = S.fitpx([sb or " " for _, _, sb in its], nw, ih * 0.3, max(S.vm(X, 2.4), npx * 0.5), S.vm(X, 2.2), max_lines=1)
    x0 = x + (w - (cw * cols + gx * (cols - 1))) / 2
    if X.portrait:
        ty = y; y0 = y + kh + max(0, (area - per * rh) / 2)
    else:                # 16:9: title + board as one block, optically centred
        ty = y + max(0, (h - kh - per * rh) / 2) * 0.88; y0 = ty + kh
    X.css("fx-rk", CSS)
    BG, FG, AC = S.col(X, p, "bg"), S.col(X, p, "fg"), S.col(X, p, "accent")
    rows, pos = [], []
    for k, (a, v, sb) in enumerate(its):
        c, r = divmod(k, per)
        rx, ry = x0 + c * (cw + gx), y0 + r * rh
        pos.append((rx, ry))
        bar = f'<i class="rk-bar" style="width:{abs(vals[k]) / vmax * 100:.1f}%"></i>' if has_v else ""
        val = f'<div class="rk-v" style="font-size:{vpx:.0f}px"><span class="rv">{vtxt[k]}</span><small>{X.rich(unit)}</small></div>' if vtxt[k] else ""
        sub = f'<div class="rk-sb" style="font-size:{spx}px">{S.lines(X, sfs[k])}</div>' if sb else ""
        q = f'<div class="rk-q" data-layout-allow-occlusion data-layout-allow-overlap style="font-size:{ih * 0.5:.0f}px">?</div>' if k == 0 and p.get("hide_top", True) and n > 1 else ""
        rows.append(f'<div class="rk-r{" top" if k == 0 else ""}" data-k="{k}" style="left:{rx:.0f}px; top:{ry:.0f}px; width:{cw:.0f}px; height:{ih:.0f}px">'
                    f'<div class="rk-in">{bar}<div class="rk-no" style="font-size:{nopx:.0f}px; width:{now:.0f}px">{k + 1}</div>'
                    f'<div class="rk-nm" style="font-size:{npx}px">{S.lines(X, nfs[k])}{sub}</div>{val}</div>{q}</div>')
    head = f'<div class="rk-k" style="left:{x0:.0f}px; top:{ty:.0f}px; font-size:{kf.px}px">{S.lines(X, kf)}</div>' if title else ""
    bx, by = pos[0][0] + now / 2 + S.vm(X, 1.2), pos[0][1] + ih / 2
    rays = "".join(f'<i style="height:{S.vm(X, 3.4):.0f}px; transform:rotate({a}deg) translateY({S.vm(X, 4.5):.0f}px)"></i>' for a in range(0, 360, 30))
    burst = f'<div class="rk-burst" style="left:{bx:.0f}px; top:{by:.0f}px">{rays}</div>'
    _clip(X, cid, t, d, f'<div class="rk">{head}{"".join(rows)}{burst}</div>', p)
    s = f"#{cid} .rk"
    if title: X.tw(f'tl.from("{s} .rk-k .sl", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.02:.3f});')
    order = list(range(n - 1, 0, -1)) if n > 1 else [0]
    T = S.beats(X, p, t, d, len(order), start=0.45 if title else 0.25, share=0.5)
    X.tw(f'tl.set("{s} .rk-burst i", {{scaleY:0, opacity:0}}, {t:.3f});')
    for k, tk in zip(order, T):
        r_ = f"{s} .rk-r[data-k='{k}']"
        X.tw(f'tl.from("{r_} .rk-in", {{rotationX:-95, opacity:0, duration:0.5, ease:"back.out(1.6)", transformOrigin:"50% 0%"}}, {tk - 0.1:.3f});')
        if has_v:
            X.tw(f'tl.from("{r_} .rk-bar", {{scaleX:0, duration:0.7, ease:"expo.out"}}, {tk:.3f});')
            v = vals[k]
            if v == int(v) and abs(v) < 1e6:
                X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{r_} .rv"); tl.to(o, {{v:{v}, duration:0.7, ease:"power2.out", onUpdate:()=>{{el.textContent=Math.round(o.v).toLocaleString("en-US");}}}}, {tk:.3f});}})();')
        X.sfx(tk - 0.1, "click")
    if n > 1:
        tq = T[-1] + max(0.45, d * 0.08)
        top = f"{s} .rk-r[data-k='0']"
        X.tw(f'tl.from("{top}", {{opacity:0, y:20, duration:0.35, ease:"expo.out"}}, {T[-1] + 0.15:.3f});')
        if p.get("hide_top", True):
            X.tw(f'tl.set("{top} .rk-in", {{rotationX:-180}}, {t:.3f});')
            X.tw(f'tl.set("{top} .rk-q", {{rotationX:0}}, {t:.3f});')
            X.tw(f'tl.to("{s} .rk-r:not(.top)", {{opacity:0.35, duration:0.35}}, {tq - 0.35:.3f});')
            X.tw(f'tl.fromTo("{top}", {{scale:1}}, {{scale:1.03, duration:0.35, ease:"sine.inOut", yoyo:true, repeat:1, immediateRender:false}}, {tq - 0.45:.3f});')
            X.tw(f'tl.to("{top} .rk-q", {{rotationX:180, duration:0.55, ease:"power3.inOut"}}, {tq:.3f});')
            X.tw(f'tl.to("{top} .rk-in", {{rotationX:0, duration:0.55, ease:"power3.inOut"}}, {tq:.3f});')
        if has_v: X.tw(f'tl.from("{top} .rk-bar", {{scaleX:0, duration:0.8, ease:"expo.out"}}, {tq + 0.3:.3f});')
        X.tw(f'tl.to("{s} .rk-burst i", {{keyframes:[{{scaleY:1, opacity:1, duration:0.18}}, {{scaleY:0.2, opacity:0, duration:0.4, ease:"power2.in"}}]}}, {tq + 0.45:.3f});')
        X.tw(f'tl.fromTo("{top}", {{scale:1}}, {{keyframes:[{{scale:1.07, duration:0.16}}, {{scale:1.03, duration:0.35, ease:"back.out(3)"}}], immediateRender:false}}, {tq + 0.45:.3f});')
        X.sfx(tq + 0.45, "hit")
    X.tw(f'tl.fromTo("{s}", {{scale:1}}, {{scale:1.02, duration:{d:.2f}, ease:"none", transformOrigin:"50% 30%"}}, {t:.3f});')


FX = {"ranking": ranking}
