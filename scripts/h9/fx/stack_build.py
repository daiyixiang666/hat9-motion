"""字叠在主体旁 (stack build · the reference promo's opener: 开源的 / AI 剪辑 / [竖屏模板] stacked beside the host):
a small kicker, then the lines arrive one by one under each other, each rising out of its own slot; the stressed
word (*…*, default the whole last line) gets a filled highlight block. A name-card variant stacks 我是 / name / role
and can end on a follow button being pressed.

p: lines ["开源的", "AI 剪辑", "*竖屏模板*"] (1–6) · kicker · sub (a small line under the stack) · at [cues per line]
   · subject | video | image (+ subject_focus, subject_start, subject_fit, subject_tag) · layout full | side | none
   · side left | right (where the subject card goes in "side")
   variant "name": pre ("我是") · name · role (accent line) · desc · en (small mono line) · follow (true | "关注")
   · follow_at
Adapts: with a subject, "full" (default) lays the stack over the footage on a scrim, "side" puts the subject in a
styled card beside the stack; with no subject the stack owns the frame — bigger type on the left, the stressed word
as a huge outline ghost on the right and a running 01 / 03 counter. 16:9 and 9:16; long lines wrap to two and the
whole stack shrinks to fit. Re-skins with the style: fonts, highlight kind (block / underline / marker / wash),
card frame, radii and the style's ease.
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
U = K.U

CSS = r"""
.ki .sb-ln { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1.12; white-space:nowrap; letter-spacing:-.01em; }
.ki .sb-ln .sl { display:block; }
.ki .sb-pre { position:absolute; font-family:var(--f-display); font-weight:800; white-space:nowrap; }
.ki .sb-role { position:absolute; font-family:var(--f-latin, var(--f-display)); font-weight:900; color:var(--accent); white-space:nowrap; }
.ki .sb-desc { position:absolute; font-family:var(--f-body); font-weight:800; white-space:nowrap; }
.ki .sb-en { position:absolute; font:700 20px var(--k-kf); letter-spacing:.2em; text-transform:uppercase; color:var(--muted); white-space:nowrap; }
.ki .sb-sub { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); white-space:nowrap; }
.ki .sb-rule { position:absolute; height:2px; background:color-mix(in srgb, var(--fg) 22%, transparent); transform-origin:0 50%; }
.ki .sb-bar { position:absolute; width:10px; background:var(--accent); transform-origin:50% 0; }
.ki .sb-ghost { position:absolute; font-family:var(--f-display); font-weight:900; line-height:1; white-space:nowrap; color:var(--bg);
  -webkit-text-stroke:3px color-mix(in srgb, var(--fg) 16%, transparent); }
.ki.hl-block .sb-ghost { -webkit-text-stroke:0; color:color-mix(in srgb, var(--accent) 12%, transparent); }
.ki .sb-cnt { position:absolute; font:700 26px var(--f-num, var(--k-kf)); letter-spacing:.08em; color:var(--muted); white-space:nowrap; }
.ki .sb-cnt b { color:var(--fg); font-weight:900; }
.ki .sb-cnt .sb-d { display:inline-block; position:relative; height:1.15em; overflow:hidden; vertical-align:bottom; }
.ki .sb-cnt .sb-d i { display:block; font-style:normal; height:1.15em; }
.ki.photo { --fg:#ffffff !important; --muted:rgba(255,255,255,.78) !important; }
.ki.photo .sb-ln, .ki.photo .sb-pre, .ki.photo .sb-desc { text-shadow:0 2px 18px rgba(0,0,0,.35); }
.ki .sb-btn { position:absolute; display:flex; align-items:center; justify-content:center; gap:10px; white-space:nowrap; font:900 34px var(--f-body);
  border-radius:var(--k-rs); }
.ki .sb-btn .a, .ki .sb-btn .b { position:absolute; inset:0; display:flex; align-items:center; justify-content:center; gap:10px; border-radius:inherit; }
.ki .sb-btn .a { background:var(--accent); color:var(--k-on); }
.ki .sb-btn .b { background:color-mix(in srgb, var(--fg) 14%, transparent); color:var(--fg); box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--fg) 40%, transparent); opacity:0; }
.ki.sk-pixel .sb-btn, .ki.sk-poster .sb-btn, .ki.sk-zine .sb-btn { border-radius:0; }
"""


def _lines_html(X, lines):
    out = []
    for ln in lines:
        out.append(f'<span class="sl">{K.hl_html(X, ln)}</span>')
    return "".join(out)


def _mark_last(items):
    """no *…* anywhere → the whole last line is the stressed one."""
    for s in items:
        if "*" in str(s):
            return items
    if not items:
        return items
    out = list(items[:-1])
    out.append("*" + str(items[-1]) + "*")
    return out


def _crowded(p):
    """more than three lines, or one longer than about six glyphs: too much for the narrow 9:16 side column."""
    items = list(FT.as_list(p.get("lines") or p.get("text") or []))
    if len(items) > 3:
        return True
    for s in items:
        if FT.width(K.strip(s)) > 6.5:
            return True
    return False


def stack_build(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    layout = p.get("layout") or ("full" if src else "none")
    if not src:
        layout = "none"
    name_mode = p.get("variant") == "name"
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    inner = []
    cls = ""
    # where the stack goes
    if layout == "full":
        cls = "photo"
        inner.append(K.subject(X, p, 0, 0, X.W, X.H, t, d, k, cls="sb-subj", full=True))
        if P:
            grad = "linear-gradient(0deg, rgba(0,0,0,.72) 0%, rgba(0,0,0,.45) 38%, rgba(0,0,0,0) 62%)"
            bx, bw = x0, aw * 0.9
            box_top, box_bot = y0 + ah * 0.34, y1 - 24
        else:
            grad = "linear-gradient(90deg, rgba(0,0,0,.66) 0%, rgba(0,0,0,.38) 40%, rgba(0,0,0,0) 66%)"
            bx, bw = x0 + 24, aw * 0.52
            box_top, box_bot = y0 + ah * 0.18, y1 - 30
        inner.append(f'<div class="k-scrim" style="background:{grad}"></div>')
    elif layout == "side" and P and not name_mode and _crowded(p):
        # 9:16 with many or long lines: the stack across the top, the subject card under it
        ar = K.subject_ar(X, src)
        sy = y0 + ah * 0.5
        sh = K.low(X, p) - sy
        sw = min(aw * 0.9, max(aw * 0.62, sh * max(0.62, min(1.5, ar))))
        inner.append(K.subject(X, p, x0 + (aw - sw) / 2, sy, sw, sh, t, d, k, cls="sb-subj"))
        bx, bw = x0, aw
        box_top, box_bot = y0 + 10, sy - 40
    elif layout == "side":
        ar = K.subject_ar(X, src)
        side = p.get("side", "right")
        sr, tr = K.beside(X, p, sub_ar=min(1.2, max(0.62, ar)), side=side)
        if P:
            # 9:16: the card runs the full height of its column, down into the caption band
            top = y0 + ah * 0.06
            sr = (sr[0], top, sr[2], K.low(X, p) - top)
        inner.append(K.subject(X, p, sr[0], sr[1], sr[2], sr[3], t, d, k, cls="sb-subj"))
        bx, bw = tr[0], tr[2]
        box_top, box_bot = tr[1] + tr[3] * 0.08, tr[1] + tr[3] * 0.92
    else:
        bx, bw = x0 + (0 if P else 20), aw * (0.96 if P else 0.6)
        box_top, box_bot = y0 + ah * (0.2 if P else 0.12), y1 - ah * 0.06
    box_h = box_bot - box_top
    rows = []          # (kind, html-maker data)
    kick = p.get("kicker")
    # ---- build the rows
    if name_mode:
        pre = p.get("pre", "我是")
        name = p.get("name") or (p.get("lines") or ["主讲"])[0]
        role = p.get("role", "")
        desc = p.get("desc", "")
        en = p.get("en", "")
        name_px, name_lines = K.fit(name, bw, box_h * 0.42, 230 if not P else 250, 60, max_lines=1)
        rows.append(("pre", pre, max(30, name_px * 0.3)))
        rows.append(("name", name, name_px))
        if role:
            rp, _ = K.fit(role, bw, box_h * 0.14, name_px * 0.42, 26, max_lines=1)
            rows.append(("role", role, rp))
        if desc:
            dp, _ = K.fit(desc, bw, box_h * 0.12, name_px * 0.34, 24, max_lines=1)
            rows.append(("desc", desc, dp))
        if en:
            rows.append(("en", en, 20 if not P else 24))
    else:
        items = list(FT.as_list(p.get("lines") or p.get("text") or ["开源的", "AI 剪辑", "*竖屏模板*"]))[:6]
        items = _mark_last(items)
        n = len(items)
        share = box_h * 0.82 / max(1, n)
        mx = 150 if layout == "none" else 128
        if P:
            mx = 150 if layout != "side" else 96
        px = mx
        for s in items:
            f = FT.fit_text(K.strip(s), bw * 0.94, share / 1.12, mx, 30, lh=1.12, max_lines=2)
            if f.px < px:
                px = f.px
        for s in items:
            f = FT.fit_text(s, bw * 0.94, box_h, px, px, lh=1.12, max_lines=2)
            rows.append(("ln", f.lines, px))
    sub = p.get("sub")
    # ---- stack heights → place the block (bottom-anchored over footage, centred otherwise)
    heights = []
    kick_h = 0
    if kick:
        kick_h = 52
    for row in rows:
        kind = row[0]
        px = row[2]
        if kind == "ln":
            heights.append(len(row[1]) * px * 1.12 + px * 0.06)
        elif kind == "name":
            heights.append(px * 1.04)
        elif kind == "en":
            heights.append(px * 1.9)
        else:
            heights.append(px * 1.32)
    sub_h = 0
    sub_px = 26 if not P else 32
    if sub:
        sub_h = sub_px * 2.1
    btn_h = 0
    follow = p.get("follow")
    if name_mode and follow:
        btn_h = 96 if not P else 110
    total = kick_h + sum(heights) + sub_h + btn_h
    if layout == "full":
        top = box_bot - total
    else:
        top = box_top + (box_h - total) / 2
    if top < box_top - 40:
        top = box_top - 40
    y = top
    s_ = None
    if kick:
        X.used_text.update(str(kick))
        inner.append(f'<div class="k-kick sb-k" style="left:{bx:.0f}px; top:{y:.0f}px">{X.rich(kick)}</div>')
        y += kick_h
    first_y = y
    for i in range(len(rows)):
        kind, val, px = rows[i]
        h = heights[i]
        pos = f"left:{bx:.0f}px; top:{y:.0f}px; font-size:{px:.0f}px"
        if kind == "ln":
            inner.append(f'<div class="sb-ln sb-r" data-i="{i}" style="{pos}">{_lines_html(X, val)}</div>')
            if layout == "none":
                inner.append(f'<i class="sb-rule" data-i="{i}" style="left:{bx:.0f}px; top:{y + h - 4:.0f}px; width:{bw:.0f}px"></i>')
        elif kind == "pre":
            X.used_text.update(str(val))
            inner.append(f'<div class="sb-pre sb-r" data-i="{i}" style="{pos}">{X.rich(val)}</div>')
        elif kind == "name":
            inner.append(f'<div class="sb-ln sb-r sb-name" data-i="{i}" style="{pos}; line-height:1">{K.hl_html(X, val)}</div>')
        elif kind == "role":
            X.used_text.update(str(val))
            inner.append(f'<div class="sb-role sb-r" data-i="{i}" style="{pos}">{X.rich(val)}</div>')
        elif kind == "desc":
            X.used_text.update(str(val))
            inner.append(f'<div class="sb-desc sb-r" data-i="{i}" style="{pos}">{K.hl_html(X, val)}</div>')
        else:
            X.used_text.update(str(val))
            inner.append(f'<div class="sb-en sb-r" data-i="{i}" style="{pos}">{X.rich(val)}</div>')
        y += h
    stack_bot = y
    if sub:
        sp, sl = K.fit(sub, bw, sub_px * 1.4, sub_px, 18, max_lines=1)
        X.used_text.update(str(sub))
        inner.append(f'<div class="sb-sub" style="left:{bx:.0f}px; top:{y + sub_px * 0.5:.0f}px; font-size:{sp}px">{X.rich(sl[0] if sl else sub)}</div>')
        y += sub_h
    btn = None
    if btn_h:
        lab = follow if isinstance(follow, str) else "关注"
        done = p.get("follow_done", "已" + lab)
        X.used_text.update("+✓" + lab + done)
        bwid = 260 if not P else 300
        bht = btn_h - 26
        btn = (bx, y + 18, bwid, bht)
        inner.append(f'<div class="sb-btn" style="left:{bx:.0f}px; top:{y + 18:.0f}px; width:{bwid}px; height:{bht:.0f}px">'
                     f'<div class="a">+ {X.rich(lab)}</div><div class="b">{K.ICON_OK} {X.rich(done)}</div></div>')
        inner.append(f'<i class="ui-rip sb-rip" style="left:{bx + bwid * 0.55:.0f}px; top:{y + 18 + bht / 2:.0f}px"></i>')
        inner.append(f'<div class="ui-touch sb-touch" style="left:0; top:0"></div>')
    # a vertical accent bar beside the stack (full / none) and, with no subject, the ghost word + counter
    n_rows = len(rows)
    if layout != "side":
        inner.append(f'<i class="sb-bar" style="left:{bx - 30:.0f}px; top:{first_y + 6:.0f}px; height:{stack_bot - first_y - 12:.0f}px"></i>')
    ghost_txt = ""
    if layout == "none":
        if name_mode:
            ghost_txt = K.strip(p.get("name") or "")
        else:
            last = rows[-1][1]
            ghost_txt = K.strip("".join(last))
            for row in rows:
                joined = "".join(row[1])
                if "*" in joined:
                    part = joined.split("*")
                    if len(part) > 1 and part[1]:
                        ghost_txt = part[1]
        if P:
            g_h, g_w = X.H * 0.3, X.W * 0.88
        else:
            g_h, g_w = X.H * 0.5, X.W * 0.42
        gpx = min(g_h, g_w / max(1.0, FT.width(ghost_txt)))
        if P:
            gx = X.W * 0.06
            gy = y0 + ah * 0.02
        else:
            gx = X.W * 0.96 - gpx * FT.width(ghost_txt)
            gy = (X.H - gpx) / 2
        X.used_text.update(ghost_txt)
        inner.append(f'<div class="sb-ghost" style="left:{gx:.0f}px; top:{gy:.0f}px; font-size:{gpx:.0f}px">{X.rich(ghost_txt)}</div>')
        digits = ""
        for j in range(n_rows):
            digits += f"<i>{j + 1:02d}</i>"
        if P:
            cpos = f"left:{x0:.0f}px; top:{y1 - 40:.0f}px"
        else:
            cpos = f"right:{X.W - x1:.0f}px; top:{y0 + 8:.0f}px"
        X.used_text.update("0123456789/ ")
        inner.append(f'<div class="sb-cnt" style="{cpos}"><b class="sb-d">{digits}</b> / {n_rows:02d}</div>')
    X.css("fx-stack-build", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k, cls=cls)
    # ---- motion
    if src:
        K.subject_in(X, f"{s_} .sb-subj", t, e, full=(layout == "full"))
        K.subject_drift(X, f"{s_} .sb-subj > img, {s_} .sb-subj > video, {s_} .sb-subj .k-pin > *", t, d, full=(layout == "full"))
    if layout == "none":
        X.tw(f'tl.fromTo("{s_} .sb-ghost", {{x:80, opacity:0}}, {{x:0, opacity:1, duration:0.8, ease:"power3.out"}}, {t:.3f});')
        X.tw(f'tl.to("{s_} .sb-ghost", {{x:-60, duration:{max(0.5, d - 1.0):.2f}, ease:"none"}}, {t + 1.0:.3f});')
    end_share = 0.55 if (name_mode and follow) else 0.62
    times = K.cues(X, p, "at", t, d, n_rows, start=0.08, end=end_share)
    if kick:
        X.tw(f'tl.fromTo("{s_} .sb-k", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -5% 0 0)", duration:0.45, ease:"power2.out", immediateRender:true}}, {max(t, times[0] - 0.25):.3f});')
    if layout != "side":
        X.tw(f'tl.fromTo("{s_} .sb-bar", {{scaleY:0}}, {{scaleY:1, duration:{min(1.1, max(0.4, times[-1] - times[0] + 0.4)):.2f}, ease:"power2.out", immediateRender:true}}, {times[0]:.3f});')
    for i in range(n_rows):
        ti = times[i]
        kind = rows[i][0]
        sel = f'{s_} .sb-r[data-i=\\"{i}\\"]'
        if kind == "name":
            X.tw(f'tl.fromTo("{sel}", {{y:{rows[i][2] * 0.5:.0f}, scale:1.08, clipPath:"inset(0 0 100% 0)"}}, {{y:0, scale:1, clipPath:"inset(-10% -5% -20% -5%)", duration:0.6, ease:"{e}", immediateRender:true}}, {ti:.3f});')
            X.sfx(ti, "hit")
        else:
            K.rise(X, sel, ti, e, dist=max(24, rows[i][2] * 0.45 if kind != "en" else 20), dur=0.5)
            X.sfx(ti, "whoosh_soft" if i == 0 else "tick")
        if layout == "none":
            X.tw(f'tl.fromTo("{s_} .sb-rule[data-i=\\"{i}\\"]", {{scaleX:0}}, {{scaleX:1, duration:0.6, ease:"power2.inOut", immediateRender:true}}, {ti + 0.1:.3f});')
            if i > 0:
                X.tw(f'tl.to("{s_} .sb-cnt .sb-d i", {{yPercent:{-100 * i}, duration:0.35, ease:"power3.inOut"}}, {ti:.3f});')
    t_hl = times[-1] + 0.38
    if name_mode:
        t_hl = times[min(1, n_rows - 1)] + 0.3
    K.hl_tween(X, s_, t_hl, k)
    X.sfx(t_hl, "pop")
    if sub:
        X.tw(f'tl.fromTo("{s_} .sb-sub", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.45, ease:"power1.out", immediateRender:true}}, {t_hl + 0.15:.3f});')
    if btn:
        tb_in = U.when(X, p.get("follow_at"), t, max(times[-1] + 0.5, t + d * 0.68))
        tb_in = min(tb_in, t + d - 1.0)
        X.tw(f'tl.fromTo("{s_} .sb-btn", {{scale:0.6, opacity:0}}, {{scale:1, opacity:1, duration:0.4, ease:"back.out(2.2)", immediateRender:true}}, {tb_in:.3f});')
        tp = tb_in + 0.55
        cx = btn[0] + btn[2] * 0.55
        cy = btn[1] + btn[3] / 2
        X.tw(f'tl.set("{s_} .sb-touch", {{x:{cx + 140:.0f}, y:{cy + 120:.0f}, opacity:0}}, {t:.3f});')
        X.tw(f'tl.to("{s_} .sb-touch", {{x:{cx:.0f}, y:{cy:.0f}, opacity:1, duration:0.4, ease:"power2.out"}}, {tp - 0.42:.3f});')
        X.tw(f'tl.to("{s_} .sb-touch", {{scale:0.8, duration:0.08, yoyo:true, repeat:1}}, {tp:.3f});')
        X.tw(f'tl.to("{s_} .sb-touch", {{opacity:0, duration:0.3}}, {tp + 0.4:.3f});')
        X.tw(f'tl.fromTo("{s_} .sb-rip", {{scale:0.2, opacity:1}}, {{scale:1.6, opacity:0, duration:0.55, ease:"power2.out", immediateRender:false}}, {tp:.3f});')
        X.tw(f'tl.to("{s_} .sb-btn .a", {{opacity:0, duration:0.12}}, {tp + 0.05:.3f});')
        X.tw(f'tl.to("{s_} .sb-btn .b", {{opacity:1, duration:0.12}}, {tp + 0.05:.3f});')
        X.tw(f'tl.fromTo("{s_} .sb-btn", {{scale:0.92}}, {{scale:1, duration:0.4, ease:"back.out(3)", immediateRender:false}}, {tp + 0.05:.3f});')
        X.sfx(tp, "click")


FX = {"stack_build": stack_build}
