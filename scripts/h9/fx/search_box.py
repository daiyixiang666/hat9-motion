"""搜索框打字 → 结果出现 (search · the 「我搜了一下」 beat of every explainer; Envato Elements Popular #7 "Search Screen Pro -
Typing Animation", #23 "Search Bars"): a neutral search page — the bar sits in the middle, the query types in with a caret,
suggestions drop down (one is hovered), Enter: the bar slides up and result cards cascade in with the keyword
highlighted; the pointer can click one result.

p: query · engine (the wordmark above the bar; neutral text, default 「搜索」) · suggest [str] (0–8) · results [str |
   "标题｜网址｜摘要" | {title, url, snippet}] (0–10) · count (e.g. 「约 120 万条结果」) · hl (keyword to highlight;
   default: the query's words) · pick (index of the result to click) · mock
Adapts: queries of 1–40 glyphs (bar font fitted), 0–8 suggestions, 0–10 results (row height and snippet lines solved
from the count; 9:16 shows up to 6), titles / urls / snippets of any length (fitted, ellipsized last).
"""
import html, importlib.util, pathlib, re, sys
from h9 import fit as FT
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


U = _load("_ui")
LENS = '<svg viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5L21 21"/></svg>'


def _results(v):
    out = []
    for r in FT.as_list(v):
        if isinstance(r, dict): out.append((str(r.get("title", "")), str(r.get("url", "")), str(r.get("snippet", ""))))
        else:
            a = (str(r).replace("|", "｜").split("｜") + ["", "", ""])[:3]
            out.append((a[0].strip(), a[1].strip(), a[2].strip()))
    return out[:10]


def _mark(X, text, kws):
    """escape + wrap every keyword hit in <b class="sb-k">."""
    X.used_text.update(text)
    if not kws: return html.escape(text)
    rx = re.compile("(" + "|".join(re.escape(k) for k in sorted(kws, key=len, reverse=True) if k) + ")")
    return "".join(f'<b class="sb-k">{html.escape(s)}</b>' if rx.fullmatch(s) else html.escape(s) for s in rx.split(text) if s)


def search_box(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    q = str(p.get("query", "")) or "搜索"
    sug = [str(x) for x in FT.as_list(p.get("suggest"))][:8]
    res = _results(p.get("results"))
    if P: res = res[:6]
    kws = [k for k in FT.as_list(p.get("hl"))] or [w for w in re.split(r"\s+", q) if len(w) >= 2] or [q]
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 24
    aw, ah = x1 - x0, y1 - y0
    bw = aw if P else min(aw * 0.7, 1150)
    bh = 96 if P else 86
    bx = x0 + (aw - bw) / 2
    by_mid = y0 + ah * (0.36 if P else 0.38)
    by_top = y0 + (44 if p.get("mock") else 10)    # the 示意 badge sits above the risen bar
    qf = FT.fit_text(q, bw - 190, bh * 0.6, 40 if not P else 38, 20, max_lines=1)
    eng = str(p.get("engine", "搜索"))
    # suggestions
    sh = 62 if not P else 66
    room = y1 - (by_mid + bh + 8) - 20     # the drop never runs into the caption: shorter rows, then fewer of them
    if sug and len(sug) * sh > room:
        sh = max(46, room / len(sug))
        sug = sug[:max(1, int(room // sh))]
    sug_html = "".join(f'<div class="sb-s" data-k="{k}" style="height:{sh}px"><i>{LENS}</i><span>{_mark(X, FT.fit_text(sg, bw - 120, sh * 0.6, 28, 16, max_lines=1).lines[0] if sg else "", kws)}</span></div>' for k, sg in enumerate(sug))
    drop = f'<div class="sb-drop" style="left:{bx:.0f}px; top:{by_mid + bh + 8:.0f}px; width:{bw:.0f}px">{sug_html}</div>' if sug else ""
    # results
    cnt = f'<div class="sb-count" style="left:{bx:.0f}px; top:{by_top + bh + 22:.0f}px">{X.rich(p.get("count", ""))}</div>' if p.get("count") else ""
    ry0 = by_top + bh + (70 if p.get("count") else 30)
    rows, rpts = [], []
    if res:
        per = (y1 - ry0 - 10) / len(res)
        per = min(per, 170 if not P else 190)
        tpx = max(18, min(34, per * 0.24)); upx = max(13, tpx * 0.58); spx = max(14, tpx * 0.66)
        snip_lines = 2 if per > tpx * 3.6 else (1 if per > tpx * 2.6 else 0)
        for k, (ti, url, sn) in enumerate(res):
            tf = FT.fit_text(ti, bw - 40, tpx * 1.3, tpx, 14, max_lines=1)
            body = f'<div class="sb-u" style="font-size:{upx:.0f}px">{X.rich(url)}</div>' if url else ""
            body += f'<div class="sb-t" style="font-size:{tf.px}px">{_mark(X, tf.lines[0] if tf.lines else ti, kws)}</div>'
            if sn and snip_lines:
                sf = FT.fit_text(sn, bw - 40, spx * 1.4 * snip_lines, spx, 12, max_lines=snip_lines, lh=1.4)
                body += f'<div class="sb-n" style="font-size:{sf.px}px">{"<br>".join(_mark(X, FT.plain(l), kws) for l in sf.lines)}</div>'
            rows.append(f'<div class="sb-r" data-k="{k}" style="left:{bx:.0f}px; top:{ry0 + k * per:.0f}px; width:{bw:.0f}px; height:{per - 12:.0f}px">{body}<i class="sb-ring"></i></div>')
            rpts.append((bx + min(bw * 0.3, 240), ry0 + k * per + per * 0.38))
    bar = (f'<div class="sb-bar" style="left:{bx:.0f}px; top:{by_mid:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">'
           f'<i class="sb-lens">{LENS}</i><span class="sb-q" style="font-size:{qf.px}px">{U.typed(X, qf.lines[0] if qf.lines else q)}<i class="ui-caret sb-car"></i></span>'
           f'<b class="sb-go">{X.rich(p.get("button", "搜索"))}</b></div>')
    ef = FT.fit_text(eng, bw, 120, 96 if not P else 80, 30, max_lines=1)
    wm = f'<div class="sb-eng" style="left:{bx:.0f}px; top:{by_mid - ef.px * 1.5:.0f}px; width:{bw:.0f}px; font-size:{ef.px}px">{X.rich(eng)}</div>'
    cur = '<div class="sb-ptr">' + U.CURSOR + '</div><i class="ui-rip sb-rip"></i>'
    X.css("fx-search-box", """
.sb-eng { position:absolute; text-align:center; font-family:var(--f-display, var(--f-body)); font-weight:900; letter-spacing:-.02em; color:var(--fg); }
.sb-bar { position:absolute; display:flex; align-items:center; gap:18px; padding:0 14px 0 28px; border-radius:999px; background:var(--card); color:var(--card-fg);
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 14%, transparent), 0 18px 44px rgba(0,0,0,.14); z-index:4; }
.sb-lens svg, .sb-s i svg { width:30px; height:30px; stroke:currentColor; stroke-width:2.4; fill:none; stroke-linecap:round; opacity:.55; }
.sb-lens { display:grid; }
.sb-q { flex:1; min-width:0; white-space:nowrap; overflow:hidden; font-family:var(--f-body); font-weight:700; }
.sb-go { flex:none; font:800 24px var(--f-body); color:var(--card); background:var(--accent); padding:12px 26px; border-radius:999px; }
.sb-drop { position:absolute; z-index:3; opacity:0; background:var(--card); border-radius:22px; padding:8px; box-shadow:0 22px 50px rgba(0,0,0,.16), 0 0 0 1px color-mix(in srgb, var(--card-fg) 10%, transparent); transform-origin:50% 0; }
.sb-s { display:flex; align-items:center; gap:16px; padding:0 20px; border-radius:14px; font:600 26px var(--f-body); color:var(--card-fg); white-space:nowrap; }
.sb-s i { display:grid; }
.sb-s.on, .sb-s .on { background:color-mix(in srgb, var(--accent) 12%, transparent); }
.sb-hov { position:absolute; left:8px; right:8px; border-radius:14px; background:color-mix(in srgb, var(--accent) 13%, transparent); opacity:0; }
.sb-k { color:var(--accent); font-weight:900; }
.sb-count { position:absolute; font:600 22px var(--f-body); color:var(--muted); }
.sb-r { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:4px; padding:0 20px; border-radius:16px; background:var(--card); color:var(--card-fg);
  box-shadow:0 0 0 1px color-mix(in srgb, var(--card-fg) 9%, transparent); }
.sb-u { font-family:var(--f-mono, monospace); color:color-mix(in srgb, var(--card-fg) 55%, transparent); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sb-t { font-family:var(--f-body); font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.sb-n { font-family:var(--f-body); line-height:1.4; color:color-mix(in srgb, var(--card-fg) 70%, transparent); }
.sb-ring { position:absolute; inset:-4px; border-radius:18px; border:4px solid var(--accent); opacity:0; }
.sb-ptr { position:absolute; left:0; top:0; z-index:12; opacity:0; }
""")
    hov = f'<i class="sb-hov" style="top:8px; height:{sh}px"></i>' if sug else ""
    drop = drop.replace('<div class="sb-drop"', '<div class="sb-drop"', 1).replace(f'width:{bw:.0f}px">', f'width:{bw:.0f}px">{hov}', 1) if drop else ""
    mk = U.mock(X, p, x1, y0, right=True)
    _clip(X, cid, t, d, f'{wm}{drop}{cnt}{"".join(rows)}{bar}{cur}{mk}', p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .sb-eng", {{y:30, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .sb-bar", {{y:40, scale:0.96, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.1:.3f});')
    X.sfx(t + 0.1, "whoosh_soft")
    n = len(FT.plain(qf.lines[0] if qf.lines else q))
    has_res = bool(res)
    t_type = t + 0.55
    type_dur = min(1.8, max(0.5, n / 9))
    if has_res: type_dur = min(type_dur, max(0.5, d * 0.28))
    end_type = U.type_in(X, f"{s} .sb-q", t_type, n, cps=n / type_dur)
    X.sfx(t_type, "type")
    t_enter = end_type + (0.35 + (0.6 if sug else 0))
    X.tw(f'tl.fromTo("{s} .sb-car", {{opacity:1}}, {{opacity:0, duration:0.25, ease:"steps(1)", repeat:{max(1, int((t_enter - t_type) / 0.5)) * 2 - 1}, yoyo:true, immediateRender:false}}, {t_type:.3f});')
    if sug:
        ts = t_type + type_dur * 0.4
        X.tw(f'tl.fromTo("{s} .sb-drop", {{opacity:0, scaleY:0.7}}, {{opacity:1, scaleY:1, duration:0.3, ease:"expo.out", immediateRender:false}}, {ts:.3f});')
        X.tw(f'tl.from("{s} .sb-s", {{opacity:0, x:-12, duration:0.25, ease:"expo.out", stagger:0.04}}, {ts + 0.05:.3f});')
        X.tw(f'tl.to("{s} .sb-hov", {{opacity:1, duration:0.15}}, {end_type:.3f});')
        if len(sug) > 1:
            X.tw(f'tl.to("{s} .sb-hov", {{y:{sh:.0f}, duration:0.25, ease:"power2.inOut"}}, {end_type + 0.25:.3f});')
        X.tw(f'tl.to("{s} .sb-drop", {{opacity:0, duration:0.2}}, {t_enter:.3f});')
    X.tw(f'tl.fromTo("{s} .sb-go", {{scale:1}}, {{keyframes:[{{scale:0.9, duration:0.08}}, {{scale:1, duration:0.16}}], immediateRender:false}}, {t_enter:.3f});')
    X.sfx(t_enter, "click")
    if has_res:
        X.tw(f'tl.to("{s} .sb-bar", {{y:{by_top - by_mid:.0f}, duration:0.55, ease:"power3.inOut"}}, {t_enter + 0.05:.3f});')
        X.tw(f'tl.to("{s} .sb-eng", {{opacity:0, y:-40, duration:0.4}}, {t_enter + 0.05:.3f});')
        tr = t_enter + 0.4
        if cnt: X.tw(f'tl.from("{s} .sb-count", {{opacity:0, duration:0.3}}, {tr:.3f});')
        X.tw(f'tl.from("{s} .sb-r", {{y:30, opacity:0, duration:0.45, ease:"expo.out", stagger:{min(0.09, 0.8 / len(res)):.3f}}}, {tr + 0.05:.3f});')
        X.sfx(tr, "whoosh_soft")
        pk = p.get("pick")
        X.tw(f'tl.set("{s} .sb-ptr, {s} .sb-rip", {{x:{bx + bw * 0.85:.0f}, y:{y1 - 30:.0f}}}, {t:.3f});')
        if pk is not None and 0 <= int(pk) < len(res):
            k = int(pk); tp = max(tr + 0.6 + 0.08 * len(res), t + d - 1.1)
            X.tw(f'tl.to("{s} .sb-ptr", {{opacity:1, duration:0.2}}, {tp - 0.7:.3f});')
            X.tw(f'tl.to("{s} .sb-ptr", {{x:{rpts[k][0]:.0f}, y:{rpts[k][1]:.0f}, duration:0.5, ease:"power2.inOut"}}, {tp - 0.5:.3f});')
            X.tw(f'tl.set("{s} .sb-rip", {{x:{rpts[k][0]:.0f}, y:{rpts[k][1]:.0f}}}, {tp:.3f});')
            X.tw(f'tl.fromTo("{s} .sb-rip", {{scale:0.2, opacity:1}}, {{scale:1.3, opacity:0, duration:0.5, ease:"power2.out", immediateRender:false}}, {tp:.3f});')
            X.tw(f'tl.to("{s} .sb-r[data-k=\'{k}\'] .sb-ring", {{opacity:1, duration:0.25}}, {tp:.3f});')
            if len(res) > 1: X.tw(f'tl.to("{s} .sb-r:not([data-k=\'{k}\'])", {{opacity:0.45, duration:0.3}}, {tp:.3f});')
            X.sfx(tp, "click")
    else:
        X.tw(f'tl.fromTo("{s} .sb-bar", {{scale:1}}, {{scale:1.04, duration:{max(0.3, t + d - t_enter - 0.2):.2f}, ease:"none", immediateRender:false}}, {t_enter + 0.2:.3f});')


FX = {"search_box": search_box}
