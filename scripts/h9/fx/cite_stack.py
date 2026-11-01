"""多方信源交叉验证 (source stack — "三个来源都对得上"): the claim sits on top, 2–5 source cards deal in under it
(type chip, outlet, date, the snippet), each gets a verdict stamp — ✓ 一致 / ✗ 不符 / ? 存疑 — connector lines draw
up to the claim and a tally counts the agreeing sources.

p: claim · sources: [{kind (新闻 / 推文 / 论文 / PDF / 视频 / 官方…), name, date, text, verdict ("ok" | "no" | "?")}, …] ·
   tally (label, default "来源一致") · kicker
Adapts: 1–5 sources (cards share the width in 16:9, stack as rows in 9:16), snippets from a phrase to 4 lines,
mixed verdicts (the tally counts only ✓), long outlet names.
"""
import importlib.util, pathlib, sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = _load("_cite")
VERDICT = {"ok": ("#1f8a5b", "一致", '<path d="M6 12.5l4 4 8-9"/>'), "no": ("#e2321f", "不符", '<path d="M7 7l10 10M17 7L7 17"/>'),
           "?": ("#c9861a", "存疑", '<path d="M9.2 9a3 3 0 1 1 4.3 2.7c-1 .5-1.5 1.2-1.5 2.3M12 17.5h.01"/>')}


def cite_stack(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    srcs = [s if isinstance(s, dict) else {"name": str(s)} for s in (p.get("sources") or [])][:5]
    n = max(len(srcs), 1)
    kick = p.get("kicker", "多方信源 · 交叉验证")
    clf = C.fitted(X, p.get("claim", ""), (x1 - x0) * (0.72 if not P else 1.0), 150 if not P else 170, 60 if not P else 56, 28, max_lines=2, lh=1.18)
    claim_h = 52 + clf.n * clf.px * 1.18
    ok = sum(1 for s in srcs if str(s.get("verdict", "ok")) == "ok")
    tally = p.get("tally", "来源一致")
    X.used_text.update(kick + tally + f"{ok}/{len(srcs)}" + "".join(v[1] for v in VERDICT.values()))
    gy = y0 + claim_h + (70 if not P else 56)
    cards = []
    room_top, room_bot = gy, (y1 - 90 if P else y1 - 10)
    fits = []
    if P:
        gap = 18; cw = x1 - x0
        for s in srcs: fits.append(C.fitted(X, s.get("text", ""), cw - 300, 150, 44, 20, max_lines=3, lh=1.3))
        hs = [max(150, 44 + f.n * f.px * 1.3 + 40) for f in fits]
        tot = sum(hs) + gap * (n - 1)
        want = (room_bot - room_top) * 0.62
        if tot < want: hs = [h * (want - gap * (n - 1)) / max(sum(hs), 1) for h in hs]; tot = want
        k = min(1.0, (room_bot - room_top) / max(tot, 1)); hs = [h * k for h in hs]
        yy = room_top + max(0, (room_bot - room_top - sum(hs) - gap * (n - 1)) / 2)
        rects = []
        for h in hs: rects.append((x0, yy, cw, h)); yy += h + gap
    else:
        gap = 26; cw = (x1 - x0 - gap * (n - 1)) / n
        for s in srcs: fits.append(C.fitted(X, s.get("text", ""), cw - 48, (room_bot - room_top) * 0.5, 46 if n <= 3 else 36, 20, max_lines=4, lh=1.3))
        hmax = max([22 * 2 + 110 + f.n * f.px * 1.3 + 70 for f in fits] or [200])
        ch_ = min(room_bot - room_top, max(hmax, (room_bot - room_top) * 0.5))
        yy = room_top + (room_bot - room_top - ch_) / 2
        rects = [(x0 + i * (cw + gap), yy, cw, ch_) for i in range(n)]
    gy = min(r[1] for r in rects) if rects else gy
    for i, (s, (rx, ry, rw, rh)) in enumerate(zip(srcs, rects)):
        col, lab, path = VERDICT.get(str(s.get("verdict", "ok")), VERDICT["ok"])
        X.used_text.update(str(s.get("kind", "")) + str(s.get("name", "")) + str(s.get("date", "")))
        tf = fits[i]
        cards.append(f'<div class="ck-card" data-i="{i}" style="left:{rx:.0f}px; top:{ry:.0f}px; width:{rw:.0f}px; height:{rh:.0f}px">'
                     f'<div class="ck-hd"><i>{X.rich(s.get("kind", "来源"))}</i><b>{X.rich(s.get("name", ""))}</b><em>{X.rich(s.get("date", ""))}</em></div>'
                     f'<div class="ck-tx" style="font-size:{tf.px}px">{C.lines(X, tf)}</div>'
                     f'<div class="ck-v" style="--vc:{col}"><svg viewBox="0 0 24 24">{path}</svg><span>{lab}</span></div></div>')
    # connectors: from each card's top centre (16:9) / left edge (9:16) up to the claim
    cy_ = y0 + claim_h + 8
    if P:
        lines_ = "".join(f'<path d="M{x0 - 22:.0f},{cy_:.0f} V{ry + rh / 2:.0f} H{x0:.0f}"/>' for rx, ry, rw, rh in rects)
    else:
        mid = (x0 + x1) / 2
        lines_ = "".join(f'<path d="M{mid:.0f},{cy_:.0f} V{(cy_ + gy) / 2:.0f} H{rx + rw / 2:.0f} V{gy:.0f}"/>' for rx, ry, rw, rh in rects)
    svg = f'<svg class="ck-wires" viewBox="0 0 {X.W} {X.H}" width="{X.W}" height="{X.H}">{lines_}</svg>'
    head = (f'<div class="ck-claim" style="left:{x0}px; top:{y0}px; width:{x1 - x0}px"><div class="ct-kick">{X.rich(kick)}</div>'
            f'<div class="ck-ct" style="font-size:{clf.px}px">{C.lines(X, clf)}</div></div>'
            f'<div class="ck-tally" style="{"right:" + str(X.W - x1) + "px; top:" + str(y0) + "px" if not P else "left:" + str(x0) + "px; top:" + str(int(y1 - 70)) + "px"}"><b><span class="ck-n">0</span>/{len(srcs)}</b><em>{X.rich(tally)}</em></div>')
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-stack", """
.ck-claim { position:absolute; display:flex; flex-direction:column; gap:14px; }
.ck-ct { font-family:var(--f-display); font-weight:900; line-height:1.18; color:var(--fg); }
.ck-ct .ct-l { overflow:hidden; }
.ck-tally { position:absolute; display:flex; align-items:baseline; gap:12px; color:var(--fg); }
.ck-tally b { font:900 92px var(--f-num, var(--f-display)); line-height:.9; color:#1f8a5b; letter-spacing:-.02em; } .ck-tally em { font-style:normal; font:800 26px var(--f-body); color:var(--muted); }
#root.v .ck-tally b { font-size:64px; }
.ck-wires { position:absolute; left:0; top:0; overflow:visible; } .ck-wires path { fill:none; stroke:color-mix(in srgb, var(--fg) 30%, transparent); stroke-width:2.5; stroke-dasharray:1400; stroke-dashoffset:1400; }
.ck-card { position:absolute; box-sizing:border-box; background:var(--card); color:var(--card-fg); border-radius:16px; padding:22px 24px; display:flex; flex-direction:column; gap:14px;
  box-shadow:0 18px 44px rgba(0,0,0,.2), 0 0 0 1.5px color-mix(in srgb, var(--card-fg) 10%, transparent); }
.ck-hd { display:flex; flex-wrap:wrap; align-items:center; gap:8px 12px; }
.ck-hd i { font-style:normal; font:800 15px var(--f-body); letter-spacing:.12em; background:var(--card-fg); color:var(--card); padding:3px 9px; border-radius:4px; }
.ck-hd b { font:900 24px var(--f-body); } .ck-hd em { font-style:normal; font:600 17px var(--f-mono, monospace); opacity:.55; width:100%; }
.ck-tx { font-family:var(--f-body); font-weight:600; line-height:1.3; flex:1; }
.ck-v { position:absolute; right:18px; bottom:18px; display:flex; align-items:center; gap:8px; color:var(--vc); border:3px solid var(--vc); border-radius:10px; padding:4px 12px 4px 8px; transform:rotate(-6deg); background:color-mix(in srgb, var(--card) 85%, transparent); }
.ck-v svg { width:30px; height:30px; fill:none; stroke:currentColor; stroke-width:3; stroke-linecap:round; stroke-linejoin:round; } .ck-v span { font:900 22px var(--f-body); }
#root.v .ck-card { flex-direction:row; align-items:center; gap:22px; padding:18px 22px; }
#root.v .ck-hd { flex-direction:column; align-items:flex-start; width:220px; flex:none; } #root.v .ck-hd em { width:auto; }
#root.v .ck-v { right:16px; bottom:auto; top:16px; }
""")
    _clip(X, cid, t, d, f'<div class="ct-root"><div class="ck-cam">{svg}{head}{"".join(cards)}</div></div>', p)
    X.css("fx-cite-stack-cam", ".ck-cam { position:absolute; inset:0; }")
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .ck-claim .ct-kick", {{opacity:0, x:-20, duration:0.4}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{S} .ck-ct .ct-l > *", {{yPercent:110, duration:0.65, ease:"expo.out", stagger:0.08}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{S} .ck-tally", {{opacity:0, y:20, duration:0.5, ease:"expo.out"}}, {t + 0.3:.3f});')
    step = max(0.18, min(0.38, (d - 1.8) / max(n, 1)))
    t0 = t + 0.45
    for i in range(len(srcs)):
        ti = t0 + i * step
        X.tw(f'tl.fromTo("{S} .ck-card[data-i=\'{i}\']", {{y:90, rotation:{(-1) ** i * 5}, opacity:0}}, {{y:0, rotation:0, opacity:1, duration:0.6, ease:"expo.out"}}, {ti:.3f});')
        X.tw(f'tl.to("{S} .ck-wires path:nth-child({i + 1})", {{strokeDashoffset:0, duration:0.6, ease:"power2.inOut"}}, {ti + 0.15:.3f});')
        X.tw(f'tl.fromTo("{S} .ck-card[data-i=\'{i}\'] .ck-v", {{scale:2.4, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(2.2)"}}, {ti + 0.45:.3f});')
        X.sfx(ti, "whoosh_soft"); X.sfx(ti + 0.45, "hit")
    C.counter(X, f"{S} .ck-n", t0 + 0.45, 0, ok, dur=max(0.3, step * len(srcs)))
    C.drift(X, f"{S} .ck-cam", t + 0.6, d - 0.6, s=1.02)


FX = {"cite_stack": cite_stack}
