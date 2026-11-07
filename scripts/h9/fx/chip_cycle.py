"""步骤 + 标签轮换 (chip cycle · the reference promo's 47–50 s: ① 下载 .motion ② 发给 AI 助手, then WorkBuddy / 豆包 /
Codex light up one after another): numbered steps light in one by one, and under the step they belong to a row of
chips (tool names) where a highlight hops from chip to chip on its cues; a window beside the steps re-titles itself to
the lit chip, and the subject sits in a card over the window's corner.

p: title ("Motion 模板 *非常简单*") · kicker · steps ["下载 .motion", "发给 AI 助手"] (1–5) · chips ["WorkBuddy",
   "豆包", "Codex", "…等助手"] (2–8) · chip_step (which step the chips hang under; default the last) · at [cues per
   step] · chip_at [cues per chip] · window (the window's title before the first hop; default "AI 助手") · attach
   (a file chip that drops into the window at the end, e.g. "模板.motion") · subject | video | image (+ subject_focus,
   subject_start, subject_fit, subject_tag)
Adapts: 1–5 steps, 2–8 chips (wrapping to a second row), long step text (fitted); 16:9: steps on the left, window +
subject on the right; 9:16: steps and chips fill the top half, window and subject card side by side fill the bottom;
no subject: the window takes the whole right side / bottom.
Re-skins with the style: pill and chip shape, highlight colour, window frame (radius, border, shadow), fonts, the
style's ease.
"""
from h9 import fit as FT
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


K = _load("_kinfo")

CSS = r"""
.ki .cc-title { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.15; white-space:nowrap; color:var(--fg); }
.ki .cc-title .sl { display:block; }
.ki .cc-st { position:absolute; display:flex; align-items:center; gap:.45em; white-space:nowrap; font-family:var(--f-display); font-weight:900; color:var(--fg);
  padding:.28em .8em .28em .32em; border-radius:var(--k-rs); background:color-mix(in srgb, var(--fg) 8%, transparent); }
.ki .cc-st i { font-style:normal; display:grid; place-items:center; width:1.5em; height:1.5em; border-radius:var(--k-rs); font-family:var(--f-num, var(--f-display));
  background:var(--fg); color:var(--bg); font-size:.8em; }
.ki .cc-st .cc-on { position:absolute; inset:0; border-radius:inherit; background:var(--accent); opacity:0; z-index:-1; }
.ki .cc-st { z-index:0; }
.ki .cc-row { position:absolute; }
.ki .cc-chip { position:absolute; z-index:2; display:flex; align-items:center; justify-content:center; white-space:nowrap; font-family:var(--f-body); font-weight:800; color:var(--fg);
  border-radius:var(--k-rs); box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--fg) 26%, transparent); }
.ki .cc-chip span { position:relative; z-index:2; }
.ki .cc-hop { position:absolute; left:0; top:0; border-radius:var(--k-rs); background:var(--accent); z-index:0; box-shadow:0 8px 22px color-mix(in srgb, var(--accent) 40%, transparent); }
.ki.sk-zine .cc-hop, .ki.sk-pixel .cc-hop, .ki.sk-papercut .cc-hop { box-shadow:5px 5px 0 var(--k-ink); }
.ki.sk-minimal .cc-hop, .ki.sk-poster .cc-hop, .ki.sk-doc .cc-hop, .ki.sk-ink .cc-hop { box-shadow:none; }
.ki .cc-win { overflow:hidden; }
.ki .cc-win .cc-bar { position:absolute; left:0; right:0; top:0; height:64px; display:flex; align-items:center; gap:10px; padding:0 22px; border-bottom:2px solid color-mix(in srgb, var(--card-fg) 10%, transparent); }
.ki .cc-win .cc-bar u { width:14px; height:14px; border-radius:50%; background:#ff5f57; } .ki .cc-win .cc-bar u:nth-child(2) { background:#febc2e; } .ki .cc-win .cc-bar u:nth-child(3) { background:#28c840; }
.ki.sk-pixel .cc-win .cc-bar u, .ki.sk-poster .cc-win .cc-bar u { border-radius:0; }
.ki .cc-win .cc-tt { position:relative; margin-left:14px; height:40px; overflow:hidden; flex:1; }
.ki .cc-win .cc-tt b { position:absolute; left:0; top:0; height:40px; line-height:40px; font:900 30px var(--f-body); color:var(--card-fg); white-space:nowrap; }
.ki .cc-win .cc-ln { position:absolute; height:16px; border-radius:8px; background:color-mix(in srgb, var(--card-fg) 10%, transparent); transform-origin:0 50%; }
.ki .cc-win .cc-file { position:absolute; display:inline-flex; align-items:center; gap:10px; white-space:nowrap; font:700 24px var(--f-mono, monospace); color:var(--accent);
  padding:8px 14px; border-radius:var(--k-rs); box-shadow:inset 0 0 0 2px var(--accent); background:color-mix(in srgb, var(--accent) 8%, var(--card)); }
.ki .cc-win .cc-caret { position:absolute; width:3px; height:30px; background:var(--accent); }
"""


def _layout_chips(names, px, max_w, gap):
    """→ [(x, y, w, h)] chips left to right, wrapping to the next row."""
    out = []
    x = 0.0
    y = 0.0
    h = px * 1.9
    for nm in names:
        w = FT.width(str(nm)) * px + px * 1.5
        if x > 0 and x + w > max_w:
            x = 0.0
            y += h + gap
        out.append((x, y, w, h))
        x += w + gap
    return out


def chip_cycle(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    steps = list(FT.as_list(p.get("steps") or ["下载模板", "发给 AI 助手"]))[:5]
    chips = list(FT.as_list(p.get("chips") or ["WorkBuddy", "豆包", "Codex"]))[:8]
    ns = len(steps)
    nc = len(chips)
    cstep = int(p.get("chip_step", ns)) - 1
    if cstep < 0 or cstep >= ns:
        cstep = ns - 1
    # ---- columns
    if P:
        lx, ly, lw, lh = x0, y0 + 10, aw, ah * 0.5
        bx, by = x0, y0 + ah * 0.53
        bw, bh = aw, K.low(X, p) - by
    else:
        lx, ly, lw, lh = x0, y0 + ah * 0.04, aw * 0.5, ah * 0.92
        bx, by, bw, bh = x0 + aw * 0.54, y0 + ah * 0.02, aw * 0.46, ah * 0.96
    inner = []
    y = ly
    kick = p.get("kicker")
    if kick:
        X.used_text.update(str(kick))
        inner.append(f'<div class="k-kick cc-k" style="left:{lx:.0f}px; top:{y:.0f}px">{X.rich(kick)}</div>')
        y += 48
    title = p.get("title")
    if title:
        tpx, tl = K.fit(K.strip(title), lw, lh * 0.32, 92 if not P else 100, 40, max_lines=2)
        f = FT.fit_text(title, lw, lh, tpx, tpx, max_lines=2)
        ls = ""
        for ln in f.lines:
            ls += f'<span class="sl">{K.hl_html(X, ln)}</span>'
        inner.append(f'<div class="cc-title" style="left:{lx:.0f}px; top:{y:.0f}px; font-size:{tpx}px">{ls}</div>')
        y += f.n * tpx * 1.15 + (36 if not P else 40)
    # steps + chips share the rest
    rest = ly + lh - y
    spx = 44 if not P else 48
    for s in steps:
        f = FT.fit_text(str(s), lw * 0.86, spx * 1.4, spx, 26, max_lines=1)
        if f.px < spx:
            spx = f.px
    chip_px = max(24, spx * 0.66)
    chip_gap = 14
    lay = _layout_chips(chips, chip_px, lw, chip_gap)
    rows_h = lay[-1][1] + lay[-1][3] if lay else 0
    step_h = spx * 2.0
    need = ns * step_h + rows_h + 30
    if need < rest and P:
        # 9:16: the steps and chips grow to fill the top half instead of leaving a band under them
        grow = min(1.45, rest / need)
        for st in steps:
            fw = FT.fit_text(str(st), lw * 0.8, 400, 200, 20, max_lines=1)
            if fw.px / spx < grow:
                grow = max(1.0, fw.px / spx)
        chip_w = lay[-1][0] + lay[-1][2] if lay else 1
        if lay and lay[-1][1] == 0 and chip_w * grow > lw:
            grow = max(1.0, lw / chip_w)
        spx = spx * grow
        chip_px = chip_px * grow
        lay = _layout_chips(chips, chip_px, lw, chip_gap)
        rows_h = lay[-1][1] + lay[-1][3] if lay else 0
        step_h = spx * 2.0
        need = ns * step_h + rows_h + 30
    if need > rest:
        sc = rest / need
        spx = spx * sc
        chip_px = chip_px * sc
        lay = _layout_chips(chips, chip_px, lw, chip_gap)
        rows_h = lay[-1][1] + lay[-1][3] if lay else 0
        step_h = spx * 2.0
    chip_origin = (lx, y)
    for i in range(ns):
        X.used_text.update(str(steps[i]) + "0123456789")
        inner.append(f'<div class="cc-st" data-i="{i}" style="left:{lx:.0f}px; top:{y:.0f}px; font-size:{spx:.0f}px"><b class="cc-on"></b><i>{i + 1}</i>{X.rich(steps[i])}</div>')
        y += step_h
        if i == cstep:
            chip_origin = (lx + 8, y - spx * 0.1)
            y += rows_h + 24
    cxo, cyo = chip_origin
    hop0 = lay[0] if lay else (0, 0, 10, 10)
    row = [f'<i class="cc-hop" style="width:{hop0[2]:.0f}px; height:{hop0[3]:.0f}px"></i>']
    for j in range(nc):
        cx, cy, cw, chh = lay[j]
        X.used_text.update(str(chips[j]))
        row.append(f'<div class="cc-chip" data-j="{j}" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{chh:.0f}px; font-size:{chip_px:.0f}px">'
                   f'<span>{X.rich(chips[j])}</span></div>')
    inner.append(f'<div class="cc-row" style="left:{cxo:.0f}px; top:{cyo:.0f}px">{"".join(row)}</div>')
    # ---- window (+ subject over its corner)
    if src:
        ar = K.subject_ar(X, src)
        if P:
            ww, wh = bw * 0.6, bh
            wx, wy = bx, by
            sw = bw * 0.44
            sh = min(bh * 0.9, sw / max(0.62, min(1.0, ar)))
            sx, sy = bx + bw - sw, by + bh - sh
        else:
            ww, wh = bw * 0.78, bh * 0.82
            wx, wy = bx, by + bh * 0.04
            sw = bw * 0.44
            sh = min(bh * 0.7, sw / max(0.62, min(1.0, ar)))
            sx, sy = bx + bw - sw, by + bh - sh
    else:
        ww, wh = bw, bh * (0.92 if not P else 1.0)
        wx, wy = bx, by + (bh - wh) / 2
    win_t = p.get("window", "AI 助手")
    titles = [win_t] + chips
    tt = ""
    for j in range(len(titles)):
        X.used_text.update(str(titles[j]))
        tt += f'<b data-w="{j}">{X.rich(titles[j])}</b>'
    lines = ""
    ly2 = 110
    if p.get("attach"):
        ly2 = 176                 # the file chip lands at the top of the window, clear of the caption band
    widths = (0.72, 0.9, 0.56, 0.8, 0.64, 0.86, 0.5)
    li = 0
    while ly2 < wh - 120 and li < 7:
        lines += f'<i class="cc-ln" data-l="{li}" style="left:28px; top:{ly2:.0f}px; width:{(ww - 56) * widths[li]:.0f}px"></i>'
        ly2 += 46
        li += 1
    attach = p.get("attach")
    file_html = ""
    if attach:
        X.used_text.update(str(attach) + "▤")
        file_html = f'<div class="cc-file" style="left:28px; top:92px">▤ {X.rich(attach)}</div>'
    inner.append(f'<div class="k-card cc-win" style="left:{wx:.0f}px; top:{wy:.0f}px; width:{ww:.0f}px; height:{wh:.0f}px">'
                 f'<div class="cc-bar"><u></u><u></u><u></u><div class="cc-tt">{tt}</div></div>{lines}{file_html}</div>')
    if src:
        inner.append(K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="cc-subj"))
    X.css("fx-chip-cycle", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    if kick:
        X.tw(f'tl.fromTo("{s_} .cc-k", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -5% 0 0)", duration:0.4, ease:"power2.out", immediateRender:true}}, {t + 0.02:.3f});')
    if title:
        K.rise(X, f"{s_} .cc-title", t + 0.08, e, dist=50, dur=0.55)
        K.hl_tween(X, f"{s_} .cc-title", t + 0.55, k)
    X.tw(f'tl.fromTo("{s_} .cc-win", {{x:80, opacity:0}}, {{x:0, opacity:1, duration:0.6, ease:"{e}", immediateRender:true}}, {t + 0.15:.3f});')
    X.tw(f'tl.fromTo("{s_} .cc-ln", {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:"power2.out", stagger:0.06, immediateRender:true}}, {t + 0.45:.3f});')
    X.tw(f'tl.set("{s_} .cc-tt b", {{y:44}}, {t:.3f});')
    X.tw(f'tl.set("{s_} .cc-tt b[data-w=\\"0\\"]", {{y:0}}, {t:.3f});')
    if src:
        K.subject_in(X, f"{s_} .cc-subj", t + 0.25, e)
        K.subject_drift(X, f"{s_} .cc-subj > img, {s_} .cc-subj > video, {s_} .cc-subj .k-pin > *", t, d)
    st_times = K.cues(X, p, "at", t, d, ns, start=0.12, end=0.32 if ns > 1 else 0.12)
    for i in range(ns):
        ti = st_times[i]
        sel = f'{s_} .cc-st[data-i=\\"{i}\\"]'
        X.tw(f'tl.fromTo("{sel}", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"{e}", immediateRender:true}}, {ti:.3f});')
        X.tw(f'tl.to("{sel} .cc-on", {{opacity:1, duration:0.2}}, {ti + 0.15:.3f});')
        X.tw(f'tl.to("{sel}", {{color:"{k['on']}", duration:0.2}}, {ti + 0.15:.3f});')
        if i > 0:
            psel = f'{s_} .cc-st[data-i=\\"{i - 1}\\"]'
            X.tw(f'tl.to("{psel} .cc-on", {{opacity:0, duration:0.2}}, {ti + 0.15:.3f});')
            X.tw(f'tl.to("{psel}", {{color:"{k['fg']}", duration:0.2}}, {ti + 0.15:.3f});')
        X.sfx(ti, "tick")
    t_row = st_times[cstep] + 0.35
    X.tw(f'tl.fromTo("{s_} .cc-chip", {{y:24, opacity:0}}, {{y:0, opacity:1, duration:0.4, ease:"{e}", stagger:0.06, immediateRender:true}}, {t_row:.3f});')
    X.tw(f'tl.set("{s_} .cc-hop", {{opacity:0}}, {t:.3f});')
    X.tw(f'tl.set("{s_} .cc-hop", {{opacity:1}}, {t_row + 0.45:.3f});')
    given = p.get("chip_at") or []
    first = max(t_row + 0.5, st_times[-1] + 0.3)
    auto = K.U.spread(nc, first, t + d * 0.84)
    hop_t = []
    for j in range(nc):
        v = given[j] if j < len(given) else None
        tj = K.U.when(X, v, t, auto[j])
        if hop_t and tj < hop_t[-1] + 0.45:
            tj = hop_t[-1] + 0.45
        hop_t.append(tj)
    for j in range(nc):
        tj = hop_t[j]
        cx, cy, cw, chh = lay[j]
        if j == 0:
            X.tw(f'tl.fromTo("{s_} .cc-hop", {{x:{cx:.0f}, y:{cy:.0f}, width:{cw:.0f}, scale:0.6}}, {{x:{cx:.0f}, y:{cy:.0f}, width:{cw:.0f}, scale:1, duration:0.3, ease:"back.out(2.5)", immediateRender:false}}, {tj:.3f});')
        else:
            X.tw(f'tl.to("{s_} .cc-hop", {{x:{cx:.0f}, y:{cy:.0f}, width:{cw:.0f}, duration:0.32, ease:"power3.inOut"}}, {tj - 0.16:.3f});')
            X.tw(f'tl.to("{s_} .cc-chip[data-j=\\"{j - 1}\\"] span", {{color:"{k['fg']}", duration:0.14}}, {tj - 0.12:.3f});')
        X.tw(f'tl.to("{s_} .cc-chip[data-j=\\"{j}\\"] span", {{color:"{k['on']}", duration:0.14}}, {tj + 0.05:.3f});')
        X.tw(f'tl.to("{s_} .cc-tt b[data-w=\\"{j}\\"]", {{y:-44, duration:0.3, ease:"power3.inOut"}}, {tj:.3f});')
        X.tw(f'tl.to("{s_} .cc-tt b[data-w=\\"{j + 1}\\"]", {{y:0, duration:0.3, ease:"power3.inOut"}}, {tj:.3f});')
        X.sfx(tj, "click")
    if attach:
        ta = min(t + d - 0.6, hop_t[-1] + 0.45)
        X.tw(f'tl.fromTo("{s_} .cc-file", {{y:-200, opacity:0, rotation:-8}}, {{y:0, opacity:1, rotation:0, duration:0.5, ease:"bounce.out", immediateRender:true}}, {ta:.3f});')
        X.sfx(ta + 0.3, "pop")


FX = {"chip_cycle": chip_cycle}
