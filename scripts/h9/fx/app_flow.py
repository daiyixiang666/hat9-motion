"""App 操作流程 (app flow · VideoHive "Phone 7 App & Gestures" 2.6K, the staple of every 工具教程): a phone
frame shows one screen at a time; a touch dot travels to the tap target, presses (ripple), and the next screen
pushes in (or rises as a sheet / fades). Beside the phone (16:9) or under it (9:16) the step list advances.

Screens are either your screenshots (any aspect — the phone takes the first one's aspect) or generated, neutral
app screens (status bar, title, list rows, an optional hero block and button) — no app branding.
p: screens [path | {img, tap:[x,y] (0–1 of the screen), label, at} | {title, rows:[str | "主｜副" | {title, sub}],
   hero, cta, tap, tap_row, label, at}] · flow ("push" | "sheet" | "fade") · steps (false hides the list) · mock
Adapts: 1–8 screens (1 = a slow scroll-like push on one screen), 0–8 rows per generated screen (row height solved),
labels of any length (fitted, ≤2 lines).
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


U = _load("_ui")
S, SO = U.S, U.SO

CHEV = '<svg viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>'
BACK = '<svg viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7"/></svg>'
SIG = '<svg viewBox="0 0 30 12"><rect x="0" y="8" width="4" height="4"/><rect x="7" y="5" width="4" height="7"/><rect x="14" y="2" width="4" height="10"/><rect x="21" y="0" width="4" height="12" opacity=".35"/></svg>'


def _norm(p):
    out = []
    for s in FT.as_list(p.get("screens")):
        if isinstance(s, str): out.append({"img": s})
        elif isinstance(s, dict): out.append({**s, "img": s.get("img") or s.get("image")})
    if not out:
        out = [{"title": "首页", "rows": ["推荐｜今天的精选", "关注｜你关注的人", "消息｜3 条新消息"], "label": "打开 App"},
               {"title": "详情", "rows": ["说明", "评论"], "cta": "开始", "label": "进入详情"}]
    return out[:8]


def _rows(s):
    rows = []
    for r in FT.as_list(s.get("rows")):
        if isinstance(r, dict): rows.append((str(r.get("title", "")), str(r.get("sub", ""))))
        else:
            a, _, b = str(r).replace("|", "｜").partition("｜"); rows.append((a.strip(), b.strip()))
    return rows[:8]


def _gen(X, s, i, vw, vh):
    """a neutral app screen in viewport px; returns (html, default tap point)."""
    pad = vw * 0.07
    sb = vh * 0.055
    tt = max(16, vw * 0.075)
    back = f'<i class="af-back">{BACK}</i>' if i > 0 else ""
    head = (f'<div class="af-sb" style="height:{sb:.0f}px; font-size:{vw * 0.042:.0f}px; padding:0 {pad:.0f}px"><b>9:41</b><i>{SIG}</i></div>'
            f'<div class="af-nav" style="top:{sb:.0f}px; height:{vh * 0.075:.0f}px; padding:0 {pad:.0f}px; font-size:{tt:.0f}px">{back}<span>{X.rich(s.get("title", ""))}</span></div>')
    y = sb + vh * 0.09
    body = ""
    if s.get("hero"):
        hh = vh * 0.2
        body += (f'<div class="af-hero" style="left:{pad:.0f}px; top:{y:.0f}px; width:{vw - 2 * pad:.0f}px; height:{hh:.0f}px; font-size:{vw * 0.07:.0f}px">'
                 f'{X.rich(s["hero"])}</div>')
        y += hh + vh * 0.025
    cta_h = vh * 0.075 if s.get("cta") else 0
    rows = _rows(s)
    tap = (0.5, 0.5)
    if rows:
        avail = vh - y - (cta_h + vh * 0.06 if cta_h else vh * 0.04)
        rh = min(vh * 0.105, avail / len(rows))
        for k, (a, b) in enumerate(rows):
            ic = rh * 0.62
            f = FT.fit_text(a, vw - 2 * pad - ic - vw * 0.16, rh * 0.42, vw * 0.058, 10, max_lines=1)
            sub = f'<em style="font-size:{max(9, f.px * 0.72):.0f}px">{X.rich(b)}</em>' if b else ""
            body += (f'<div class="af-row" data-k="{k}" style="left:{pad:.0f}px; top:{y + k * rh:.0f}px; width:{vw - 2 * pad:.0f}px; height:{rh:.0f}px">'
                     f'<i class="af-ic" style="width:{ic:.0f}px; height:{ic:.0f}px; background:{U.tone(a)}; font-size:{ic * 0.46:.0f}px">{X.rich(SO.mono(a))}</i>'
                     f'<span><b style="font-size:{f.px}px">{X.rich(f.lines[0] if f.lines else a)}</b>{sub}</span><i class="af-chev">{CHEV}</i></div>')
        k = min(int(s.get("tap_row", 0)), len(rows) - 1)
        tap = (0.5, (y + (k + 0.5) * rh) / vh)
    if cta_h:
        cy = vh - vh * 0.05 - cta_h
        body += (f'<div class="ui-btn af-cta" style="left:{pad:.0f}px; top:{cy:.0f}px; width:{vw - 2 * pad:.0f}px; height:{cta_h:.0f}px; font-size:{vw * 0.055:.0f}px; position:absolute">'
                 f'{X.rich(s["cta"])}</div>')
        tap = (0.5, (cy + cta_h / 2) / vh)
    return head + body, tap


def app_flow(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    scr = _norm(p)
    n = len(scr)
    imgs = [s["img"] for s in scr if s.get("img")]
    ar = (FT.aspect(X, imgs[0], 0.4615) if imgs else 0.4615)
    ar = max(0.38, min(0.75, ar))
    labels = [str(s.get("label") or s.get("title") or "") for s in scr]
    show_steps = p.get("steps", True) and any(labels)
    x0, y0, x1, y1 = U.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    if P:
        band = 130 if show_steps else 0
        g = S.frame_geom("phone", aw * 0.86, ah - band - 40, ar, P)
        fx_, fy_ = x0 + (aw - g["w"]) / 2, y0 + 30
    else:
        g = S.frame_geom("phone", aw * 0.42, ah, ar, P)
        fx_ = x0 + (aw * (0.3 if show_steps else 0.5)) - g["w"] / 2
        fy_ = y0 + (ah - g["h"]) / 2
    vw, vh = g["vw"], g["vh"]
    screens, taps, live = [], [], []
    for i, s in enumerate(scr):
        if s.get("img"):
            url = S.prep(X, s["img"])[0]
            html = f'<img src="{url}" alt="" style="width:100%; height:100%; object-fit:cover; object-position:50% 0%">'
            tap = (0.5, 0.6)
        else:
            html, tap = _gen(X, s, i, vw, vh)
        if s.get("tap"):
            tp = s["tap"]; tap = (float(tp[0]), float(tp[1]))
        taps.append((tap[0] * vw, tap[1] * vh))
        live.append([c for c in ("af-row", "af-hero", "af-cta") if re.search(rf'class="[^"]*\b{c}\b', html)])
        screens.append(f'<div class="af-scr" data-i="{i}" data-layout-allow-overlap>{html}</div>')    # two screens share the viewport mid-push
    inner = "".join(screens) + '<i class="ui-rip af-rip"></i><i class="ui-touch af-touch"></i>'
    phone = S.frame(X, "phone", g, fx_, fy_, inner, cls="af-ph")
    steps = ""
    if show_steps:
        if P:
            chips = "".join(f'<div class="af-chip" data-i="{i}"><b>{i + 1}</b><span>{X.rich(FT.fit_text(l, aw - 120, 80, 40, 22, max_lines=2).lines[0] if l else "")}</span></div>' for i, l in enumerate(labels))
            steps = f'<div class="af-chips" style="left:{x0:.0f}px; top:{fy_ + g["h"] + 26:.0f}px; width:{aw:.0f}px">{chips}</div>'
        else:
            lx = fx_ + g["w"] + 90
            lw = x1 - lx
            per = min(130, ah * 0.9 / n)
            rows = []
            for i, l in enumerate(labels):
                f = FT.fit_text(l, lw - 90, per * 0.8, 46, 20, max_lines=2, lh=1.2)
                rows.append(f'<div class="af-step" data-i="{i}" style="height:{per:.0f}px"><b><i class="af-on"></i><em>{i + 1}</em></b><span style="font-size:{f.px}px">{"<br>".join(X.rich(x) for x in f.lines)}</span></div>')
            steps = f'<div class="af-steps" style="left:{lx:.0f}px; top:{y0 + (ah - per * n) / 2:.0f}px; width:{lw:.0f}px">{"".join(rows)}</div>'
    X.used_text.update("0123456789:")
    X.css("fx-app-flow", """
.af-scr { position:absolute; left:0; top:0; width:100%; height:100%; background:var(--scr-page); color:var(--scr-ink); overflow:hidden; font-family:var(--f-body); }
.af-scr:not([data-i="0"]) { visibility:hidden; }
.af-sb { position:absolute; left:0; right:0; top:0; display:flex; align-items:center; justify-content:space-between; font-weight:700; }
.af-sb svg { width:1.6em; height:.7em; fill:currentColor; }
.af-nav { position:absolute; left:0; right:0; display:flex; align-items:center; gap:.3em; font-weight:900; letter-spacing:-.01em; }
.af-back svg, .af-chev svg { width:1em; height:1em; stroke:currentColor; stroke-width:2.6; fill:none; stroke-linecap:round; stroke-linejoin:round; }
.af-back { display:grid; color:var(--accent); }
.af-hero { position:absolute; display:flex; align-items:flex-end; padding:.6em .7em; box-sizing:border-box; border-radius:.5em; font-weight:900; color:#fff;
  background:linear-gradient(135deg, var(--accent), color-mix(in srgb, var(--accent) 55%, #111)); }
.af-row { position:absolute; display:flex; align-items:center; gap:4%; border-bottom:1px solid color-mix(in srgb, var(--scr-ink) 10%, transparent); box-sizing:border-box; }
.af-ic { flex:none; display:grid; place-items:center; border-radius:24%; color:#fff; font-weight:900; font-style:normal; }
.af-row span { flex:1; min-width:0; display:flex; flex-direction:column; gap:.15em; }
.af-row b { font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.af-row em { font-style:normal; color:var(--scr-dim); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.af-chev { flex:none; color:var(--scr-dim); display:grid; font-size:1.4em; }
.af-steps { position:absolute; display:flex; flex-direction:column; }
.af-step { display:flex; align-items:center; gap:22px; color:var(--fg); opacity:.32; }
.af-step b { flex:none; width:54px; height:54px; border-radius:50%; display:grid; place-items:center; font:800 24px var(--f-mono, monospace); border:3px solid currentColor; }
.af-step span { font-family:var(--f-display, var(--f-body)); font-weight:800; line-height:1.2; }
.af-step b { position:relative; } .af-step b em { position:relative; font-style:normal; }
.af-step .af-on { position:absolute; inset:-3px; border-radius:50%; background:var(--accent); opacity:0; }
.af-chips { position:absolute; height:100px; }
.af-chip { position:absolute; left:0; right:0; top:0; display:flex; align-items:center; justify-content:center; gap:16px; opacity:0; color:var(--fg); }
.af-chip b { flex:none; width:52px; height:52px; border-radius:50%; display:grid; place-items:center; font:800 24px var(--f-mono, monospace); background:var(--accent); color:var(--bg); }
.af-chip span { font:800 40px var(--f-display, var(--f-body)); white-space:nowrap; }
""")
    sh = U.mock(X, p, fx_ + g["w"] + 16, fy_ + 14)
    _clip(X, cid, t, d, f'<div class="af" style="position:absolute; inset:0; {S.theme_vars(p, p.get("dark_chrome", False))}">{phone}{steps}{sh}</div>', p)
    s = f"#{cid}"
    # appearance times: screen 0 at t, screen i at its cue or evenly spread
    T = [t]
    auto = U.spread(n - 1, t + min(1.4, d * 0.28), t + d - min(1.6, d * 0.3)) if n > 1 else []    # the last screen stays long enough to read
    for i in range(1, n):
        T.append(max(T[-1] + 0.55, U.when(X, scr[i].get("at"), t, auto[i - 1])))
    flow = p.get("flow", "push")
    X.tw(f'tl.from("{s} .af-ph", {{y:70, scale:0.94, opacity:0, duration:0.7, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.tw(f'tl.fromTo("{s} .af-ph", {{rotation:0}}, {{rotation:{-1.2 if not P else 0}, duration:{d:.2f}, ease:"sine.inOut"}}, {t:.3f});')
    if n > 1: X.tw(f'tl.set("{s} .af-scr:not([data-i=\'0\'])", {{visibility:"hidden"}}, {t:.3f});')    # CSS hides them too (a set at 0 can be reverted)
    X.sfx(t + 0.05, "whoosh_soft")
    if steps:
        if P: X.tw(f'tl.to("{s} .af-chip[data-i=\'0\']", {{opacity:1, duration:0.3}}, {t + 0.35:.3f});')
        else:
            X.tw(f'tl.from("{s} .af-step", {{x:30, opacity:0, duration:0.45, ease:"expo.out", stagger:0.07}}, {t + 0.25:.3f});')
            on0 = t + 0.25 + 0.45 + 0.07 * (n - 1)    # after the list has slid in
            X.tw(f'tl.to("{s} .af-step[data-i=\'0\']", {{opacity:1, duration:0.3}}, {on0:.3f});')
            X.tw(f'tl.to("{s} .af-step[data-i=\'0\'] .af-on", {{opacity:1, duration:0.3}}, {on0:.3f});')
    if n > 1 and T[1] - t > 1.6:
        X.tw(f'tl.fromTo("{s} .af-scr[data-i=\'0\']", {{scale:1}}, {{scale:1.035, transformOrigin:"50% 0%", duration:{T[1] - t - 0.8:.2f}, ease:"sine.inOut", immediateRender:false}}, {t + 0.6:.3f});')
    if n == 1:      # one screen: let it breathe (a slow push inside the phone)
        X.tw(f'tl.fromTo("{s} .af-scr[data-i=\'0\']", {{scale:1}}, {{scale:1.06, transformOrigin:"50% 30%", duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    px_, py_ = vw * 0.72, vh * 0.86
    X.tw(f'tl.set("{s} .af-touch, {s} .af-rip", {{x:{px_:.0f}, y:{py_:.0f}}}, {t:.3f});')
    MV = [0.0] + [min(0.5, max(0.25, (T[i] - T[i - 1]) * 0.35)) for i in range(1, n)]
    for i in range(1, n):
        tx, ty = taps[i - 1]
        ti = T[i]
        mv = MV[i]
        stay_in = i > 1 and T[i] - MV[i] - 0.25 < T[i - 1] + 0.3     # taps close together: the finger stays down between them
        stay_out = i + 1 < n and T[i + 1] - MV[i + 1] - 0.25 < ti + 0.3
        if not stay_in: X.tw(f'tl.to("{s} .af-touch", {{opacity:1, duration:0.2}}, {ti - mv - 0.25:.3f});')
        X.tw(f'tl.to("{s} .af-touch", {{x:{tx:.0f}, y:{ty:.0f}, duration:{mv:.2f}, ease:"power2.inOut"}}, {ti - mv - 0.2:.3f});')
        X.tw(f'tl.set("{s} .af-rip", {{x:{tx:.0f}, y:{ty:.0f}}}, {ti - 0.18:.3f});')
        X.tw(f'tl.fromTo("{s} .af-touch", {{scale:1}}, {{keyframes:[{{scale:0.78, duration:0.08}}, {{scale:1, duration:0.14}}], immediateRender:false}}, {ti - 0.18:.3f});')
        X.tw(f'tl.fromTo("{s} .af-rip", {{scale:0.2, opacity:1}}, {{scale:1.3, opacity:0, duration:0.5, ease:"power2.out", immediateRender:false}}, {ti - 0.18:.3f});')
        if not stay_out: X.tw(f'tl.to("{s} .af-touch", {{opacity:0, duration:0.2}}, {ti + 0.05:.3f});')
        X.sfx(ti - 0.18, "click")
        a, b = f'{s} .af-scr[data-i=\'{i - 1}\']', f'{s} .af-scr[data-i=\'{i}\']'
        X.tw(f'tl.set("{b}", {{visibility:"visible"}}, {ti:.3f});')
        X.tw(f'tl.set("{a}", {{visibility:"hidden"}}, {ti + 0.58:.3f});')
        if flow == "sheet":
            X.tw(f'tl.set("{b}", {{xPercent:0}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{b}", {{yPercent:100}}, {{yPercent:0, duration:0.55, ease:"expo.out", immediateRender:false}}, {ti:.3f});')
            X.tw(f'tl.to("{a}", {{scale:0.92, filter:"brightness(.6)", duration:0.55, ease:"expo.out"}}, {ti:.3f});')
        elif flow == "fade":
            X.tw(f'tl.set("{b}", {{xPercent:0, opacity:0}}, {ti:.3f});')
            X.tw(f'tl.to("{b}", {{opacity:1, duration:0.4}}, {ti:.3f});')
        else:
            X.tw(f'tl.fromTo("{b}", {{xPercent:100}}, {{xPercent:0, duration:0.5, ease:"power3.inOut", immediateRender:false}}, {ti:.3f});')
            X.tw(f'tl.to("{a}", {{xPercent:-28, filter:"brightness(.65)", duration:0.5, ease:"power3.inOut"}}, {ti:.3f});')
        X.sfx(ti, "whoosh_soft")
        if steps:
            if P:
                X.tw(f'tl.to("{s} .af-chip[data-i=\'{i - 1}\']", {{opacity:0, y:-16, duration:0.25}}, {ti:.3f});')
                X.tw(f'tl.fromTo("{s} .af-chip[data-i=\'{i}\']", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.35, ease:"expo.out", immediateRender:false}}, {ti + 0.05:.3f});')
            else:
                X.tw(f'tl.to("{s} .af-step[data-i=\'{i - 1}\']", {{opacity:0.55, duration:0.3}}, {ti:.3f});')
                X.tw(f'tl.to("{s} .af-step[data-i=\'{i - 1}\'] .af-on", {{opacity:0, duration:0.3}}, {ti:.3f});')
                X.tw(f'tl.to("{s} .af-step[data-i=\'{i}\']", {{opacity:1, duration:0.3}}, {ti:.3f});')
                X.tw(f'tl.to("{s} .af-step[data-i=\'{i}\'] .af-on", {{opacity:1, duration:0.3}}, {ti:.3f});')
        # the new screen keeps living: its rows settle in
        hold_end = T[i + 1] if i + 1 < n else t + d
        if hold_end - ti > 1.0:     # while a screen is held it leans in a touch, so the phone never freezes (9:16 has no sway)
            X.tw(f'tl.fromTo("{b}", {{scale:1}}, {{scale:1.035, transformOrigin:"50% 0%", duration:{hold_end - ti - 0.6:.2f}, ease:"sine.inOut", immediateRender:false}}, {ti + 0.6:.3f});')
        if live[i]: X.tw(f'tl.from("{", ".join(f"{b} .{c}" for c in live[i])}", {{y:24, opacity:0, duration:0.4, ease:"expo.out", stagger:0.05}}, {ti + 0.2:.3f});')


FX = {"app_flow": app_flow}
