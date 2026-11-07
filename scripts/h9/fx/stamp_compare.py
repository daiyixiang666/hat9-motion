"""截图标注对比 (stamp compare · the reference promo's 24–26 s and 60–64 s): a real screenshot gets clean UI annotation —
a rectangle or ellipse draws itself round the problem, a「× 问题」stamp slams down beside it; then an arrow draws to
the "after" screenshot, its fix is boxed in the good colour and ✓ tags stack in one by one. Clean vector marks, not
hand-drawn ones (scribble does hand-drawn).

p: image (before; also "before") · box [x, y, w, h] (0–1 of that image, or its px) · mark rect | circle · stamp ("被挡住")
   · before_label ("旧版") · after (image) · after_box · after_label ("新版") · checks ["稳定", "聚焦"] (0–5)
   · box_at · after_at · check_at [cues] · mock (a 「示意」 badge)
Adapts: any screenshot aspect, shown whole (never cropped, so box coordinates stay exact); with an after image the two
sit side by side (16:9, or 9:16 when both are tall) or one above the other (9:16 with wide shots); without one the
tags stack beside the single shot; with no image at all a skeleton screen stands in (marked 示意). 0–5 tags.
Re-skins with the style: shot frame (radius, border, shadow), stamp shape, tag shape, the style's alert and accent
colours, the style's ease.
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
S = K.S

CSS = r"""
.ki .sc-shot { position:absolute; border-radius:var(--k-r); box-shadow:var(--k-sh); background:var(--card); overflow:visible; }
.ki .sc-shot .sc-img { position:absolute; inset:0; overflow:hidden; border-radius:inherit; outline:var(--k-bw) solid var(--k-ink); outline-offset:calc(var(--k-bw) * -1); }
.ki .sc-shot .sc-img img { width:100%; height:100%; display:block; object-fit:fill; }
.ki .sc-lab { position:absolute; display:flex; align-items:baseline; gap:.5em; white-space:nowrap; font-family:var(--f-display); font-weight:900; color:var(--fg); }
.ki .sc-lab small { font:700 .55em var(--k-kf); letter-spacing:.14em; color:var(--muted); text-transform:uppercase; }
.ki .sc-lab.good b { color:var(--accent); }
.ki svg.sc-marks { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.ki svg.sc-marks .bad { fill:color-mix(in srgb, var(--k-alert) 10%, transparent); stroke:var(--k-alert); stroke-width:6; }
.ki svg.sc-marks .good { fill:color-mix(in srgb, var(--accent) 12%, transparent); stroke:var(--accent); stroke-width:6; }
.ki svg.sc-marks .arr { fill:none; stroke:var(--fg); stroke-width:7; stroke-linecap:round; stroke-linejoin:round; }
.ki.sk-pixel svg.sc-marks .bad, .ki.sk-pixel svg.sc-marks .good { stroke-width:8; }
.ki .sc-ck { position:absolute; display:inline-flex; align-items:center; gap:.4em; white-space:nowrap; font-family:var(--f-display); font-weight:900;
  color:var(--k-on); background:var(--accent); padding:.25em .65em .25em .5em; border-radius:var(--k-rs); box-shadow:0 10px 26px rgba(0,0,0,.22); }
.ki.sk-zine .sc-ck, .ki.sk-pixel .sc-ck, .ki.sk-papercut .sc-ck { box-shadow:6px 6px 0 var(--k-ink); }
.ki.sk-minimal .sc-ck, .ki.sk-poster .sc-ck, .ki.sk-doc .sc-ck { box-shadow:none; }
.ki .sc-skel { position:absolute; inset:0; padding:8%; display:flex; flex-direction:column; gap:5%; background:var(--card); }
.ki .sc-skel i { display:block; height:7%; border-radius:6px; background:color-mix(in srgb, var(--card-fg) 12%, transparent); }
.ki .sc-skel i.hd { height:12%; width:60%; background:color-mix(in srgb, var(--card-fg) 22%, transparent); }
.ki .sc-skel i.bx { height:28%; }
"""


def _shot(X, src, x, y, w, h, cls):
    if src:
        img = f'<img src="{X.asset(src)}" alt="">'
    else:
        img = '<div class="sc-skel"><i class="hd"></i><i></i><i style="width:80%"></i><i class="bx"></i><i style="width:70%"></i><i></i></div>'
    return f'<div class="sc-shot {cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px"><div class="sc-img">{img}</div></div>'


def _box_px(b, sw, sh, ow, oh):
    """a box on the source image (0–1 or source px) → px on the shown shot (ow × oh)."""
    bx, by, bw, bh = S.box_of(b, sw, sh)
    k = ow / sw
    return bx * k, by * k, bw * k, bh * k


def _mark(kind, x, y, w, h, cls, key):
    if kind == "circle":
        rx = w / 2 + 16
        ry = h / 2 + 16
        return f'<ellipse class="{cls} sc-m" data-k="{key}" cx="{x + w / 2:.1f}" cy="{y + h / 2:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" pathLength="1" stroke-dasharray="1 1"/>'
    pad = 10
    return (f'<rect class="{cls} sc-m" data-k="{key}" x="{x - pad:.1f}" y="{y - pad:.1f}" width="{w + 2 * pad:.1f}" height="{h + 2 * pad:.1f}" rx="8" '
            f'pathLength="1" stroke-dasharray="1 1"/>')


def stamp_compare(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    before = p.get("image") or p.get("before")
    after = p.get("after")
    checks = list(FT.as_list(p.get("checks") or []))[:5]
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    lab_h = 64 if not P else 86
    sz_b = FT.size(FT._abs(X, before)) if before else (900, 1100)
    ar_b = sz_b[0] / sz_b[1]
    if after:
        sz_a = FT.size(FT._abs(X, after)) or (900, 1100)
    else:
        sz_a = (1, 1)
    ar_a = sz_a[0] / sz_a[1]
    stacked = bool(after) and P and (ar_b > 1.15 or ar_a > 1.15)
    shots = []            # (x, y, w, h)
    if after and not stacked:
        gap = 150 if not P else 64
        cw = (aw - gap) / 2
        chh = ah - lab_h - (40 if checks and P else 10)
        for ar in (ar_b, ar_a):
            w = min(cw, chh * ar)
            h = w / ar
            shots.append([w, h])
        hmax = max(shots[0][1], shots[1][1])
        top = y0 + lab_h + (chh - hmax) / 2
        if P:
            # 9:16: shots + a row of tags under them, centred as one group
            group = lab_h + hmax + (130 if checks else 0)
            top = y0 + (ah - group) / 2 + lab_h
        shots[0] = (x0 + (cw - shots[0][0]) / 2, top, shots[0][0], shots[0][1])
        shots[1] = (x0 + cw + gap + (cw - shots[1][0]) / 2, top, shots[1][0], shots[1][1])
    elif after:
        gap = 110
        chh = (ah - gap - 2 * lab_h) / 2
        cw = aw * 0.86
        ys = (y0 + lab_h, y0 + lab_h + chh + gap + lab_h)
        idx = 0
        for ar in (ar_b, ar_a):
            w = min(cw, chh * ar)
            h = w / ar
            shots.append((x0 + (aw - w) / 2 - aw * 0.04, ys[idx] + (chh - h) / 2, w, h))
            idx += 1
    else:
        if P:
            cw = aw * 0.9
            chh = ah * (0.66 if checks else 0.9) - lab_h
        else:
            cw = aw * (0.56 if checks else 0.8)
            chh = ah - lab_h - 10
        w = min(cw, chh * ar_b)
        h = w / ar_b
        if P:
            shots.append((x0 + (aw - w) / 2, y0 + lab_h, w, h))
        else:
            left = x0 + (aw * (0.6 if checks else 1.0) - w) / 2
            shots.append((left, y0 + lab_h + (chh - h) / 2, w, h))
    inner = []
    grp = []              # the before shot, its label, its box and its stamp move as one group
    bx, by, bw, bh = shots[0]
    grp.append(_shot(X, before, bx, by, bw, bh, "sc-b"))
    lab_px = 34 if not P else 50
    bl = p.get("before_label", "旧版" if after else "")
    if bl:
        X.used_text.update(str(bl) + "BEFORE")
        grp.append(f'<div class="sc-lab sc-lb" style="left:{bx:.0f}px; top:{by - lab_h + 8:.0f}px; font-size:{lab_px}px"><b>{X.rich(bl)}</b><small>Before</small></div>')
    marks = []
    if before is None and p.get("box") is None:
        p = dict(p)
        p["box"] = [0.12, 0.42, 0.76, 0.26]
    box = None
    if p.get("box") is not None:
        box = _box_px(p["box"], sz_b[0], sz_b[1], bw, bh)
        bad = _mark(p.get("mark", "rect"), bx + box[0], by + box[1], box[2], box[3], "bad", "b")
        grp.append(f'<svg class="sc-marks" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{bad}</svg>')
    if after:
        ax, ay, aw2, ah2 = shots[1]
        inner.append(_shot(X, after, ax, ay, aw2, ah2, "sc-a"))
        al = p.get("after_label", "新版")
        X.used_text.update(str(al) + "AFTER")
        inner.append(f'<div class="sc-lab sc-la good" style="left:{ax:.0f}px; top:{ay - lab_h + 8:.0f}px; font-size:{lab_px}px"><b>{X.rich(al)}</b><small>After</small></div>')
        if p.get("after_box") is not None:
            ab = _box_px(p["after_box"], sz_a[0], sz_a[1], aw2, ah2)
            marks.append(_mark(p.get("mark", "rect"), ax + ab[0], ay + ab[1], ab[2], ab[3], "good", "a"))
        # the arrow between them
        if stacked:
            mx = bx + bw / 2
            a0 = by + bh + 18
            a1 = ay - lab_h - 6
            marks.append(f'<path class="arr sc-arr" pathLength="1" stroke-dasharray="1 1" d="M{mx:.0f} {a0:.0f} L{mx:.0f} {a1:.0f} M{mx - 22:.0f} {a1 - 24:.0f} L{mx:.0f} {a1:.0f} L{mx + 22:.0f} {a1 - 24:.0f}"/>')
        else:
            my = by + bh * 0.5
            a0 = bx + bw + 28
            a1 = ax - 28
            marks.append(f'<path class="arr sc-arr" pathLength="1" stroke-dasharray="1 1" d="M{a0:.0f} {my:.0f} L{a1:.0f} {my:.0f} M{a1 - 26:.0f} {my - 22:.0f} L{a1:.0f} {my:.0f} L{a1 - 26:.0f} {my + 22:.0f}"/>')
    inner.append(f'<svg class="sc-marks" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{"".join(marks)}</svg>')
    # the stamp beside the problem box
    stamp = p.get("stamp")
    if stamp and box:
        X.used_text.update(str(stamp))
        spx = 40 if not P else 46
        sw_est = (FT.width(str(stamp)) + 1.4) * spx + 40
        sx = bx + box[0] + box[2] - sw_est * 0.5
        sy = by + box[1] + box[3] + 22
        if sy + spx * 1.8 > by + bh + 30:
            sy = by + box[1] - spx * 1.9 - 18
        if sx + sw_est > X.W - 30:
            sx = X.W - 30 - sw_est
        if sx < 30:
            sx = 30
        grp.append(f'<div class="k-stamp sc-st" style="left:{sx:.0f}px; top:{sy:.0f}px; font-size:{spx}px; transform:rotate(-6deg)">{K.ICON_X}{X.rich(stamp)}</div>')
    inner.insert(0, f'<div class="sc-gb" style="position:absolute; inset:0; transform-origin:{bx + bw / 2:.0f}px {by + bh / 2:.0f}px">{"".join(grp)}</div>')
    # ✓ tags
    ck_px = 38 if not P else 54
    ck_pos = []
    if checks:
        if after:
            ax, ay, aw2, ah2 = shots[1]
            if stacked:
                cx = ax + aw2 - 40
                cy = ay + ah2 * 0.2
            else:
                cx = ax + aw2 * 0.55
                cy = ay + ah2 * 0.52
        elif P:
            cx = x0 + 10
            cy = by + bh + 50
        else:
            cx = x0 + aw * 0.62
            cy = by + bh * 0.25
        step = ck_px * 1.9
        row = bool(after) and P and not stacked
        if row:
            ax, ay, aw2, ah2 = shots[1]
            cx = shots[0][0]
            cy = max(shots[0][1] + shots[0][3], ay + ah2) + 40
        run_x = cx
        for i in range(len(checks)):
            if row:
                ck_pos.append((run_x, cy))
                run_x += (FT.width(str(checks[i])) + 2.4) * ck_px
            else:
                ck_pos.append((cx + (i % 2) * 18, cy + i * step))
        for i in range(len(checks)):
            X.used_text.update(str(checks[i]))
            inner.append(f'<div class="sc-ck" data-i="{i}" style="left:{ck_pos[i][0]:.0f}px; top:{ck_pos[i][1]:.0f}px; font-size:{ck_px}px">{K.ICON_OK}{X.rich(checks[i])}</div>')
    if p.get("mock"):
        inner.append(K.U.mock(X, p, bx + 16, by + 16))
    X.css("fx-stamp-compare", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    X.tw(f'tl.fromTo("{s_} .sc-b", {{y:70, opacity:0, rotation:-1.5}}, {{y:0, opacity:1, rotation:0, duration:0.6, ease:"{e}", immediateRender:true}}, {t + 0.02:.3f});')
    X.tw(f'tl.fromTo("{s_} .sc-lb", {{x:-30, opacity:0}}, {{x:0, opacity:1, duration:0.4, ease:"power3.out", immediateRender:true}}, {t + 0.2:.3f});')
    X.sfx(t + 0.02, "whoosh_soft")
    if after:
        t_box = K.U.when(X, p.get("box_at"), t, t + min(0.75, d * 0.14))
        t_after = K.U.when(X, p.get("after_at"), t, t + d * 0.42)
    else:
        t_box = K.U.when(X, p.get("box_at"), t, t + min(0.8, d * 0.18))
        t_after = t_box + 1.0
    if after and not stacked:
        # the before shot opens big in the middle of the frame, then steps aside for the after shot
        big = min(1.7, aw * 0.88 / bw, (ah - lab_h) * 0.9 / bh)
        if big > 1.05:
            dx = x0 + aw / 2 - (bx + bw / 2)
            dy = y0 + lab_h / 2 + ah / 2 - (by + bh / 2)
            X.tw(f'tl.set("{s_} .sc-gb", {{x:{dx:.0f}, y:{dy:.0f}, scale:{big:.3f}}}, {t:.3f});')
            X.tw(f'tl.to("{s_} .sc-gb", {{x:0, y:0, scale:1, duration:0.6, ease:"power3.inOut"}}, {t_after - 0.55:.3f});')
    if box:
        X.tw(f'tl.fromTo("{s_} .sc-m[data-k=\\"b\\"]", {{strokeDashoffset:1, fillOpacity:0}}, {{strokeDashoffset:0, fillOpacity:1, duration:0.45, ease:"power2.inOut", immediateRender:true}}, {t_box:.3f});')
        X.sfx(t_box, "click")
        # the shot leans in toward the problem
        ox = (box[0] + box[2] / 2) / bw * 100
        oy = (box[1] + box[3] / 2) / bh * 100
        X.tw(f'tl.fromTo("{s_} .sc-b .sc-img img", {{scale:1}}, {{scale:1.05, transformOrigin:"{ox:.0f}% {oy:.0f}%", duration:{max(0.5, t_after - t_box):.2f}, ease:"power1.inOut", immediateRender:false}}, {t_box:.3f});')
    if stamp and box:
        ts = t_box + 0.5
        X.tw(f'tl.fromTo("{s_} .sc-st", {{scale:2.2, opacity:0, rotation:-14}}, {{scale:1, opacity:1, rotation:-6, duration:0.32, ease:"power4.in", immediateRender:true}}, {ts:.3f});')
        X.tw(f'tl.fromTo("{s_} .sc-b", {{x:0}}, {{keyframes:[{{x:-7, duration:0.04}}, {{x:6, duration:0.04}}, {{x:-3, duration:0.04}}, {{x:0, duration:0.05}}], immediateRender:false}}, {ts + 0.32:.3f});')
        X.sfx(ts + 0.3, "slam")
    if after:
        X.tw(f'tl.fromTo("{s_} .sc-arr", {{strokeDashoffset:1}}, {{strokeDashoffset:0, duration:0.4, ease:"power2.inOut", immediateRender:true}}, {t_after:.3f});')
        if stacked:
            X.tw(f'tl.fromTo("{s_} .sc-a", {{y:120, opacity:0, scale:0.92}}, {{y:0, opacity:1, scale:1, duration:0.6, ease:"{e}", immediateRender:true}}, {t_after:.3f});')
        else:
            X.tw(f'tl.fromTo("{s_} .sc-a", {{x:140, opacity:0, scale:0.92}}, {{x:0, opacity:1, scale:1, duration:0.6, ease:"{e}", immediateRender:true}}, {t_after:.3f});')
        X.tw(f'tl.fromTo("{s_} .sc-la", {{x:-30, opacity:0}}, {{x:0, opacity:1, duration:0.4, ease:"power3.out", immediateRender:true}}, {t_after + 0.2:.3f});')
        X.tw(f'tl.to("{s_} .sc-b", {{opacity:0.55, filter:"saturate(.4)", duration:0.5}}, {t_after:.3f});')
        X.sfx(t_after, "whoosh")
        if p.get("after_box") is not None:
            X.tw(f'tl.fromTo("{s_} .sc-m[data-k=\\"a\\"]", {{strokeDashoffset:1, fillOpacity:0}}, {{strokeDashoffset:0, fillOpacity:1, duration:0.45, ease:"power2.inOut", immediateRender:true}}, {t_after + 0.55:.3f});')
    if checks:
        start = t_after + (0.95 if after else 0.0)
        auto = K.U.spread(len(checks), start, max(start + 0.4 * len(checks), t + d - 0.9))
        given = p.get("check_at") or []
        for i in range(len(checks)):
            v = given[i] if i < len(given) else None
            ti = K.U.when(X, v, t, auto[i])
            X.tw(f'tl.fromTo("{s_} .sc-ck[data-i=\\"{i}\\"]", {{x:40, scale:0.5, opacity:0}}, {{x:0, scale:1, opacity:1, duration:0.4, ease:"back.out(2.4)", immediateRender:true}}, {ti:.3f});')
            X.sfx(ti, "pop")


FX = {"stamp_compare": stamp_compare}
