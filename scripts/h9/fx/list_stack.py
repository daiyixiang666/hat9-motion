"""要点列表 Numbered List Stack (Envato Elements「Checklist Pack」热门; talkcraft numbered-step-stack / alt-block-lines;
所长林超、小Lin说的「三个原因」编号栈): the heading lands big, then shrinks into a kicker while the points enter
one by one out of their own masks; a highlight block slides to the point being spoken, earlier points dim and
step back. style "check" ticks each point off (清单); style "recap" brings everything back and sweeps (结尾总结).

Adapts: 1–14 points (one column up to 5 in 16:9 / 7 in 9:16, then two), each point a word to a sentence with an
optional sub-line (one shared size, ≤ 2 lines), heading optional and any length.
p: items ["…" | ["point", "sub"] | {"text", "sub"}] · title · style focus|check|recap · hl (index left lit) · at [cues]
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .ls { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .ls .ls-h { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.12; transform-origin:0 0; white-space:nowrap; }
.fx .ls .ls-h .sl { display:block; }
.fx .ls .ls-rule { position:absolute; height:.5vmin; background:var(--fg); transform-origin:0 50%; }
.fx .ls .ls-hi { position:absolute; left:0; top:0; background:var(--accent); border-radius:1.2vmin; opacity:0; }
.fx .ls .ls-row { position:absolute; display:flex; align-items:center; gap:2.4vmin; transform-origin:0 50%; }
.fx .ls .ls-n { flex:none; display:grid; place-items:center; border-radius:50%; border:.45vmin solid var(--fg); color:var(--fg);
  font-family:var(--f-num, var(--f-display)); font-weight:900; font-variant-numeric:tabular-nums; position:relative; }
.fx .ls .ls-n svg { position:absolute; inset:18%; width:64%; height:64%; fill:none; stroke:var(--bg); stroke-width:3.4; stroke-linecap:round; stroke-linejoin:round; }
.fx .ls .ls-tx { min-width:0; clip-path:inset(0 0 0 0); }
.fx .ls .ls-t { display:inline-block; font-family:var(--f-display); font-weight:800; color:var(--fg); line-height:1.18; }
.fx .ls .ls-t .sl, .fx .ls .ls-s .sl { display:block; white-space:nowrap; }
.fx .ls .ls-s { font-family:var(--f-body); font-weight:500; color:var(--muted); line-height:1.3; margin-top:.5vmin; }
.fx .ls .ls-row.on .ls-t, .fx .ls .ls-row.on .ls-s { color:var(--bg); }
.fx .ls .ls-x { position:absolute; left:0; right:0; top:50%; height:.45vmin; background:currentColor; transform-origin:0 50%; }
"""

TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7"/></svg>'


def list_stack(X, cid, t, d, p):
    its = S.items(p.get("items")) or [("要点", "")]
    its = its[:14]
    n = len(its)
    style = p.get("style", "focus")
    x, y, w, h = S.box(X, p)
    title = fit.as_text(p.get("title"))
    hb = 0
    if title:      # the heading's resting size (kicker) — it starts big in the middle and shrinks into place
        kf = fit.fit_text(title, w * 0.9, S.vm(X, 14), S.vm(X, 6.2 if X.portrait else 5.4), S.vm(X, 3.4), max_lines=2)
        hb = kf.n * kf.px * 1.12 + S.vm(X, 3.4)
    cap = 5 if not X.portrait else 7
    cols = 1 if n <= cap else 2
    per = -(-n // cols)
    gx = S.vm(X, 4)
    cw = (w - gx * (cols - 1)) / cols
    area = h - hb
    rh = min(area / per, S.vm(X, 17) if X.portrait else S.vm(X, 25 if n <= 2 else 22 if n <= 3 else 17 if n <= 5 else 14))
    gap = rh * 0.16
    nd = min(rh * 0.62, S.vm(X, 9))
    tw = cw - nd - S.vm(X, 2.4) - S.vm(X, 2.5)
    has_sub = any(s for _, s in its)
    tmax = S.vm(X, 7.2 if X.portrait else 8.6) * (1 if n <= 3 else 0.84 if n <= 5 else 0.74 if n <= 8 else 0.64)
    th = (rh - gap) * (0.62 if has_sub else 0.86)
    tpx, tfs = S.fitpx([a for a, _ in its], tw, th, tmax, S.vm(X, 2.7), max_lines=2)
    spx, sfs = S.fitpx([b or " " for _, b in its], tw, (rh - gap) * 0.34, max(S.vm(X, 2.6), tpx * 0.5), S.vm(X, 2.4), max_lines=1)
    total_h = per * rh
    if X.portrait:
        ty = y
        y0 = y + hb + max(0, (area - total_h) / 2) if title else y + max(0, (h - total_h) / 2)
    else:                # 16:9: heading + rows as one block, optically centred (a touch above the middle)
        ty = y + max(0, (h - hb - total_h) / 2) * 0.88
        y0 = ty + hb
    X.css("fx-ls", CSS)
    rows, pos = [], []
    for k, (a, b) in enumerate(its):
        c, r = divmod(k, per)
        rx, ry = x + c * (cw + gx), y0 + r * rh
        pos.append((rx, ry))
        badge = TICK if style == "check" else X.rich(str(k + 1))
        sub = f'<div class="ls-s" style="font-size:{spx}px">{S.lines(X, sfs[k])}</div>' if b else ""
        rows.append(f'<div class="ls-row" data-k="{k}" style="left:{rx:.0f}px; top:{ry:.0f}px; width:{cw:.0f}px; height:{rh - gap:.0f}px">'
                    f'<div class="ls-n" style="width:{nd:.0f}px; height:{nd:.0f}px; font-size:{nd * 0.5:.0f}px">{badge}</div>'
                    f'<div class="ls-tx" style="width:{tw:.0f}px"><div class="ls-t" style="font-size:{tpx}px; position:relative">{S.lines(X, tfs[k])}'
                    f'{"<i class=ls-x></i>" if style == "check" else ""}</div>{sub}</div></div>')
    head = ""
    if title:
        head = (f'<div class="ls-h" style="left:{x:.0f}px; top:{ty:.0f}px; font-size:{kf.px}px">{S.lines(X, kf)}</div>'
                f'<i class="ls-rule" style="left:{x:.0f}px; top:{ty + kf.n * kf.px * 1.12 + S.vm(X, 1.2):.0f}px; width:{min(w, S.vm(X, 22)):.0f}px"></i>')
    hi = f'<i class="ls-hi" style="width:{cw + S.vm(X, 2.4):.0f}px; height:{rh - gap + S.vm(X, 1.6):.0f}px"></i>'
    glide = not X.portrait and cols == 1 and n > 1       # 16:9: the visible rows stay centred while the list grows
    _clip(X, cid, t, d, f'<div class="ls">{head}<div class="ls-rw" style="position:absolute; inset:0">{hi}{"".join(rows)}</div></div>', p)
    s = f"#{cid} .ls"
    BG, FG, AC = S.col(X, p, "bg"), S.col(X, p, "fg"), S.col(X, p, "accent")
    item_texts = [a for a, _ in its]
    T = S.beats(X, p, t, d, n, start=0.75 if title else 0.25, share=0.58 if style != "recap" else 0.42, texts=item_texts)
    if title:      # big in the middle → kicker in the corner
        bf = fit.fit_text(title, w * 0.86, h * 0.4, S.vm(X, 13), kf.px, max_lines=2)
        kw = fit.width(max(kf.lines, key=lambda l: fit.width(l))) * kf.px
        sc = min(bf.px / kf.px, w * 0.9 / max(kw, 1), h * 0.42 / max(kf.n * kf.px * 1.12, 1))
        bw = kw * sc
        bh = kf.n * kf.px * 1.12 * sc
        dx, dy = x + (w - bw) / 2 - x, y + (h - bh) / 2 - ty
        X.tw(f'tl.from("{s} .ls-h", {{scale:{sc:.3f}, x:{dx:.0f}, y:{dy:.0f}, duration:0.7, ease:"expo.inOut"}}, {T[0] - 0.62:.3f});')
        X.tw(f'tl.from("{s} .ls-h .sl", {{yPercent:110, opacity:0, duration:0.45, ease:"expo.out", stagger:0.06}}, {t + 0.02:.3f});')
        X.tw(f'tl.from("{s} .ls-rule", {{scaleX:0, duration:0.5, ease:"expo.out"}}, {T[0] - 0.2:.3f});')
        X.sfx(t + 0.02, "enter")
    if glide:
        X.tw(f'tl.set("{s} .ls-rw", {{y:{(n - 1) * rh / 2:.0f}}}, {t:.3f});')
        for k in range(1, n):
            X.tw(f'tl.to("{s} .ls-rw", {{y:{(n - 1 - k) * rh / 2:.0f}, duration:0.5, ease:"expo.inOut"}}, {T[k] - 0.28:.3f});')
    hl = int(p.get("hl", n - 1)) if style == "focus" else -1
    if style == "check": X.tw(f'tl.set("{s} .ls-x", {{scaleX:0}}, {t:.3f});')
    for k, tk in enumerate(T):
        rx, ry = pos[k]
        sel = f"{s} .ls-row[data-k='{k}']"
        X.tw(f'tl.from("{sel} .ls-tx", {{clipPath:"inset(0 100% 0 0)", x:-24, duration:0.55, ease:"expo.out"}}, {tk - 0.12:.3f});')
        X.tw(f'tl.from("{sel} .ls-n", {{scale:0, rotation:-90, duration:0.45, ease:"back.out(2.4)"}}, {tk - 0.16:.3f});')
        X.sfx(tk - 0.12, "click")
        if style == "focus":
            hx, hy = rx - S.vm(X, 1.2), ry - S.vm(X, 0.8)
            if k == 0: X.tw(f'tl.set("{s} .ls-hi", {{x:{hx:.0f}, y:{hy:.0f}, opacity:1}}, {tk - 0.12:.3f});')
            else: X.tw(f'tl.to("{s} .ls-hi", {{x:{hx:.0f}, y:{hy:.0f}, duration:0.42, ease:"expo.inOut"}}, {tk - 0.2:.3f});')
            X.tw(f'tl.to("{sel} .ls-t, {sel} .ls-s", {{color:"{BG}", duration:0.2}}, {tk - 0.08:.3f});')
            X.tw(f'tl.to("{sel} .ls-n", {{borderColor:"{BG}", color:"{BG}", duration:0.2}}, {tk - 0.08:.3f});')
            if k > 0:
                prev = f"{s} .ls-row[data-k='{k - 1}']"
                X.tw(f'tl.to("{prev} .ls-t, {prev} .ls-s", {{color:"{FG}", duration:0.25}}, {tk - 0.2:.3f});')
                X.tw(f'tl.to("{prev} .ls-n", {{borderColor:"{FG}", color:"{FG}", duration:0.25}}, {tk - 0.2:.3f});')
                X.tw(f'tl.to("{prev}", {{opacity:0.38, scale:0.97, duration:0.35, ease:"power2.out"}}, {tk - 0.2:.3f});')
        elif style == "check":
            X.tw(f'tl.to("{sel} .ls-n", {{backgroundColor:"{AC}", borderColor:"{AC}", duration:0.2}}, {tk + 0.25:.3f});')
            X.tw(f'tl.fromTo("{sel} .ls-n path", {{strokeDasharray:24, strokeDashoffset:24}}, {{strokeDashoffset:0, duration:0.3, ease:"power2.out", immediateRender:false}}, {tk + 0.3:.3f});')
            X.tw(f'tl.set("{sel} .ls-n path", {{strokeDasharray:24, strokeDashoffset:24}}, {t:.3f});')
            if k < n - 1 and p.get("strike", True):
                X.tw(f'tl.fromTo("{sel} .ls-x", {{scaleX:0}}, {{scaleX:1, duration:0.3, ease:"power3.out", immediateRender:false}}, {tk + 0.45:.3f});')
                X.tw(f'tl.to("{sel} .ls-t, {sel} .ls-s", {{opacity:0.45, duration:0.3}}, {tk + 0.5:.3f});')
            X.sfx(tk + 0.3, "tick")
    end = T[-1] + 0.6
    if style == "focus" and 0 <= hl < n - 1:        # finish on the point that matters, not the last one read
        rx, ry = pos[hl]; last = f"{s} .ls-row[data-k='{n - 1}']"; keep = f"{s} .ls-row[data-k='{hl}']"
        X.tw(f'tl.to("{last}", {{opacity:0.38, scale:0.97, duration:0.35}}, {end:.3f});')
        X.tw(f'tl.to("{last} .ls-t, {last} .ls-s", {{color:"{FG}", duration:0.25}}, {end:.3f});')
        X.tw(f'tl.to("{last} .ls-n", {{borderColor:"{FG}", color:"{FG}", duration:0.25}}, {end:.3f});')
        X.tw(f'tl.to("{s} .ls-hi", {{x:{rx - S.vm(X, 1.2):.0f}, y:{ry - S.vm(X, 0.8):.0f}, duration:0.5, ease:"expo.inOut"}}, {end:.3f});')
        X.tw(f'tl.to("{keep}", {{opacity:1, scale:1.02, duration:0.4}}, {end:.3f});')
        X.tw(f'tl.to("{keep} .ls-t, {keep} .ls-s", {{color:"{BG}", duration:0.25}}, {end + 0.1:.3f});')
        X.tw(f'tl.to("{keep} .ls-n", {{borderColor:"{BG}", color:"{BG}", duration:0.25}}, {end + 0.1:.3f});')
    if style == "recap":       # everything back at once, then one accent sweep down the list
        X.tw(f'tl.to("{s} .ls-n", {{backgroundColor:"{AC}", borderColor:"{AC}", color:"{BG}", duration:0.25, stagger:0.08}}, {end:.3f});')
        X.tw(f'tl.fromTo("{s} .ls-row", {{x:0}}, {{keyframes:[{{x:14, duration:0.12}}, {{x:0, duration:0.3, ease:"back.out(3)"}}], stagger:0.08, immediateRender:false}}, {end:.3f});')
        X.sfx(end, "hit")
    X.tw(f'tl.fromTo("{s}", {{scale:1}}, {{scale:1.025, duration:{d:.2f}, ease:"none", transformOrigin:"50% 40%"}}, {t:.3f});')


FX = {"list_stack": list_stack}
