"""阶段进度 / 甘特图 Gantt & phases (Envato Popular「Infographics 6 Roadmaps」「Horizontal Timeline」; VideoHive Company
Timeline 3.2K): the time axis draws, each task's bar grows from its start to its end in order (overlaps read as
"in parallel"), milestones drop in as diamonds, and a "now" line sweeps to the current point, lighting what is done.

Adapts: 2–14 tasks (row height from the count; 9:16 puts each label above its bar), any time unit — numbers
(hours, days, weeks, years) with `unit`, or dates "YYYY-MM" / "YYYY-MM-DD" (axis ticks pick months / quarters /
years by span); up to 4 groups (colour + legend); optional milestones and a `now` marker; one task can be singled out.
p: tasks [[label, start, end, group?], ...] · milestones [[label, at], ...] · now · unit · hl · title · note · mock
"""
from h9.aefx import _clip
import datetime as _dt
import importlib.util, pathlib, sys


def _load(n):
    k = f"h9fx_{n}"
    if k not in sys.modules:
        s = importlib.util.spec_from_file_location(k, pathlib.Path(__file__).with_name(f"{n}.py"))
        sys.modules[k] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[k])
    return sys.modules[k]


W = _load("_w3")
GC = ["var(--accent)", "color-mix(in srgb, var(--fg) 70%, var(--bg))", "color-mix(in srgb, var(--accent) 50%, var(--fg))", "color-mix(in srgb, var(--fg) 40%, var(--bg))"]


def _t(v):
    """number or date string -> (float position, is_date)."""
    if isinstance(v, (int, float)): return float(v), False
    s = str(v).strip()
    try:
        parts = [int(x) for x in s.split("-")]
        y, m, d = (parts + [1, 1])[:3]
        dt = _dt.date(y, m, d)
        return (dt - _dt.date(1970, 1, 1)).days, True
    except Exception:
        return float(W.num(s) or 0), False


def _date_ticks(lo, hi):
    a = _dt.date(1970, 1, 1) + _dt.timedelta(days=lo); b = _dt.date(1970, 1, 1) + _dt.timedelta(days=hi)
    months = (b.year - a.year) * 12 + b.month - a.month
    step = 1 if months <= 8 else 3 if months <= 30 else 12
    out = []
    y, m = a.year, a.month
    if step == 12: m = 1
    elif step == 3: m = ((m - 1) // 3) * 3 + 1
    while True:
        d = _dt.date(y, m, 1)
        if d > b: break
        if d >= a - _dt.timedelta(days=1):
            lab = f"{y}" if step == 12 else (f"{y}.{m:02d}" if m == 1 or not out else f"{m}月")
            out.append(((d - _dt.date(1970, 1, 1)).days, lab))
        m += step
        while m > 12: m -= 12; y += 1
    return out


def gantt(X, cid, t, d, p):
    W.base(X)
    tasks = []
    isdate = False
    for q in p["tasks"][:14]:
        a, da = _t(q[1]); b, db = _t(q[2]); isdate = isdate or da
        tasks.append({"lab": str(q[0]), "a": a, "b": max(b, a), "g": q[3] if len(q) > 3 else None})
    ms = [(str(m[0]), _t(m[1])[0]) for m in (p.get("milestones") or [])]
    n = len(tasks)
    lo = min([q["a"] for q in tasks] + [m[1] for m in ms]); hi = max([q["b"] for q in tasks] + [m[1] for m in ms])
    if "lo" in p: lo = _t(p["lo"])[0]
    if "hi" in p: hi = _t(p["hi"])[0]
    groups = []
    for q in tasks:
        if q["g"] is not None and q["g"] not in groups: groups.append(q["g"])
    hl = int(p.get("hl", -1))
    P = X.portrait
    x0, y0, x1, y1 = W.box(X)
    hh, hhpx = W.head(X, p, x0, y0, x1 - x0)
    top = y0 + hhpx + 44
    lab_w = 0 if P else min(420, max(W.F.em(q["lab"]) for q in tasks) * 30 + 30)
    ax0, ax1 = x0 + lab_w, x1 - 10
    rh = min(110 if P else 82, (y1 - top - 40) / n)
    top += max(0, min(120, (y1 - top - 40 - rh * n - (70 if ms else 0)) * 0.35))     # few rows: sit a little lower, not glued to the title
    bar_h = rh * (0.4 if P else 0.56)
    X_ = lambda v: ax0 + (v - lo) / ((hi - lo) or 1) * (ax1 - ax0)
    if isdate: ticks = _date_ticks(lo, hi)
    else:
        yearish = 1000 <= lo and hi <= 3000 and all(float(v).is_integer() for v in W.nice_ticks(lo, hi, 6))
        ticks = [(v, (f"{v:.0f}" if yearish else W.tick_label(v)) + (p.get("unit", "") if i == 0 and not yearish else "")) for i, v in enumerate(W.nice_ticks(lo, hi, 6)) if lo - 1e-9 <= v <= hi + 1e-9]
    els = []
    for v, lab in ticks:
        xx = X_(v)
        els.append(f'<i class="gtg" style="left:{xx:.1f}px; top:{top - 8:.0f}px; height:{rh * n + 8:.0f}px"></i><div class="gtt" style="left:{xx:.1f}px; top:{top - 40:.0f}px">{X.rich(lab)}</div>')
    for i, q in enumerate(tasks):
        yr = top + i * rh
        col = GC[groups.index(q["g"]) % 4] if q["g"] is not None else (GC[0] if (i == hl or hl < 0) else GC[1])
        bx, bw = X_(q["a"]), max(8, X_(q["b"]) - X_(q["a"]))
        by = yr + (rh - bar_h) / 2 + (rh * 0.18 if P else 0)
        ls = min(30 if not P else 26, rh * 0.42)
        if P:
            els.append(f'<div class="gtl" data-i="{i}" style="left:{max(x0, min(bx, x1 - W.F.em(q["lab"]) * ls - 10)):.0f}px; top:{yr + 2:.0f}px; font-size:{ls:.0f}px">{X.rich(q["lab"])}</div>')
        else:
            els.append(f'<div class="gtl" data-i="{i}" style="right:{X.W - ax0 + 20:.0f}px; top:{by + bar_h / 2 - ls * 0.62:.0f}px; font-size:{ls:.0f}px">{X.rich(q["lab"])}</div>')
        els.append(f'<i class="gtb{" hl" if i == hl else ""}" data-i="{i}" style="left:{bx:.1f}px; top:{by:.1f}px; width:{bw:.1f}px; height:{bar_h:.1f}px; background:{col}"></i>')
    for j, (lab, at) in enumerate(ms):
        xx = X_(at)
        els.append(f'<i class="gtm" data-j="{j}" style="left:{xx - 13:.1f}px; top:{top + rh * n + 6:.0f}px"></i><div class="gtml" data-j="{j}" style="left:{xx:.1f}px; top:{top + rh * n + 38:.0f}px">{X.rich(lab)}</div>')
    now = _t(p["now"])[0] if p.get("now") is not None else None
    if now is not None:
        els.append(f'<i class="gtn" style="left:{X_(lo) - 2:.1f}px; top:{top - 14:.0f}px; height:{rh * n + 20:.0f}px"></i>')
    legend = "".join(f'<div class="gtlg"><i style="background:{GC[gi % 4]}"></i>{X.rich(str(g))}</div>' for gi, g in enumerate(groups))
    X.css("fx-gantt", """
.fx .gt .gtg { position:absolute; width:1px; background:color-mix(in srgb, var(--fg) 12%, transparent); }
.fx .gt .gtt { position:absolute; transform:translateX(-50%); font:700 20px var(--f-num, var(--f-mono, monospace)); color:var(--muted); white-space:nowrap; }
.fx .gt .gtl { position:absolute; font-family:var(--f-body); font-weight:800; color:var(--fg); white-space:nowrap; line-height:1.2; }
.fx .gt .gtb { position:absolute; border-radius:6px; transform-origin:0 50%; }
.fx .gt .gtb.hl { box-shadow:0 0 0 4px var(--bg), 0 0 0 7px var(--accent); }
.fx .gt .gtm { position:absolute; width:26px; height:26px; background:var(--fg); transform:rotate(45deg); }
.fx .gt .gtml { position:absolute; transform:translateX(-50%); font:700 20px var(--f-body); color:var(--fg); white-space:nowrap; }
.fx .gt .gtn { position:absolute; width:4px; background:var(--accent); box-shadow:0 0 10px var(--accent); }
.fx .gt .gtlgs { position:absolute; display:flex; gap:24px; } .fx .gt .gtlg { display:flex; align-items:center; gap:10px; font:700 20px var(--f-body); color:var(--muted); }
.fx .gt .gtlg i { width:18px; height:18px; border-radius:4px; }
""")
    inner = (f'<div class="w3 gt">{hh}{"".join(els)}<div class="gtlgs" style="left:{ax0:.0f}px; top:{y1 - 24:.0f}px">{legend}</div>'
             f'{W.mock_tag(X, p, x1 - 70, y0)}</div>')
    X.used_text.update("0123456789.月年")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    W.head_in(X, s, t, p)
    X.tw(f'tl.from("{s} .gtg", {{scaleY:0, transformOrigin:"50% 0", duration:0.5, ease:"expo.out", stagger:0.04}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{s} .gtt", {{opacity:0, y:-8, duration:0.35, stagger:0.04}}, {t + 0.2:.3f});')
    span = min(d * 0.55, 0.5 + n * 0.35)
    order = sorted(range(n), key=lambda i: tasks[i]["a"])
    for k, i in enumerate(order):
        ti = t + 0.4 + span * k / max(1, n)
        X.tw(f'tl.from("{s} .gtl[data-i=\'{i}\']", {{opacity:0, x:-14, duration:0.35}}, {ti:.3f});')
        X.tw(f'tl.from("{s} .gtb[data-i=\'{i}\']", {{scaleX:0, duration:0.6, ease:"power3.out"}}, {ti + 0.05:.3f});')
        X.sfx(ti, "tick")
    te = t + 0.5 + span
    if ms: X.tw(f'tl.from("{s} .gtm", {{y:-40, opacity:0, duration:0.45, ease:"back.out(2.5)", stagger:0.1}}, {te:.3f});')
    if ms or groups: X.tw(f'tl.from("{s} .gtml, {s} .gtlg", {{opacity:0, duration:0.35, stagger:0.06}}, {te + 0.1:.3f});')
    if now is not None:
        X.tw(f'tl.from("{s} .gtn", {{opacity:0, duration:0.2}}, {te:.3f});')
        X.tw(f'tl.to("{s} .gtn", {{x:{X_(now) - X_(lo):.1f}, duration:{min(1.4, d * 0.25):.2f}, ease:"power2.inOut"}}, {te + 0.1:.3f});')
        late = [i for i in range(n) if tasks[i]["a"] > now]
        if late:
            X.tw(f'tl.to("{", ".join(f"{s} .gtb[data-i=\'{i}\']" for i in late)}", {{opacity:0.35, duration:0.4}}, {te + 0.6:.3f});')
    if 0 <= hl < n:
        X.tw(f'tl.fromTo("{s} .gtb.hl", {{scaleY:1}}, {{keyframes:[{{scaleY:1.35, duration:0.12}}, {{scaleY:1, duration:0.3, ease:"back.out(3)"}}], immediateRender:false}}, {te + 0.3:.3f});')
        X.sfx(te + 0.3, "hit")


FX = {"gantt": gantt}
