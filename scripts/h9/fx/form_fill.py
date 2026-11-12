"""表单填写 / 设置开关 (form fill · the "Settings & Forms" scenes of UI-explainer packs; Envato Elements Popular
"Checklist Pack"): a neutral form card; the pointer visits each field in turn — text fields type with a caret, toggles slide
on, checkboxes tick, radio dots fill, a select drops its options and picks one — then the button is pressed and a
success toast confirms. Good for 「发布前要勾选什么」「这个设置一定要打开」.

p: title · sub · fields [{label, value, kind: text|password|textarea|toggle|check|radio|select, on (bool), options:[...],
   note}] (or "标签：值" strings = text fields) · submit (button text) · done (toast text) · cursor (true) · mock
Adapts: 1–10 fields (16:9 switches to two columns past 6), labels / values of any length (fitted, values ≤1 line,
textarea ≤3), 0–6 select options.
"""
import importlib.util, pathlib, sys
from h9 import fit as FT
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


U = _load("_ui")


def _norm(v):
    out = []
    for f in FT.as_list(v):
        if isinstance(f, dict): out.append({"kind": "text", **f})
        elif isinstance(f, (list, tuple)): out.append({"label": f[0], "value": f[1] if len(f) > 1 else "", "kind": f[2] if len(f) > 2 else "text"})
        else:
            a, _, b = str(f).replace(":", "：").partition("：")
            out.append({"label": a.strip(), "value": b.strip(), "kind": "text"} if b else {"label": str(f), "kind": "check", "on": True})
    return out[:10] or [{"label": "名字", "value": "示例频道", "kind": "text"}, {"label": "接收通知", "kind": "toggle", "on": True}]


def form_fill(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    F = _norm(p.get("fields"))
    n = len(F)
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 24
    aw, ah = x1 - x0, y1 - y0
    cols = 2 if (not P and n > 6) else 1
    cw = (aw * 0.62 if cols == 1 else aw * 0.86) if not P else aw * 0.94
    head_h = (164 if p.get("sub") else 124) if p.get("title") else 40
    btn_h = 84 if p.get("submit", "提交") else 0
    rows = -(-n // cols)
    avail = ah - head_h - btn_h - 90
    rh = max(70, min(130, avail / rows))
    ch = head_h + rows * rh + btn_h + 70
    if ch > ah: rh = max(60, (ah - head_h - btn_h - 70) / rows); ch = head_h + rows * rh + btn_h + 70
    cx, cy = x0 + (aw - cw) / 2, y0 + (ah - ch) / 2
    pad = 44
    colw = (cw - 2 * pad - (40 if cols == 2 else 0)) / cols
    lab_px = max(16, min(24, rh * 0.22))
    val_px = max(18, min(30, rh * 0.26))
    parts, pts = [], []
    for i, f in enumerate(F):
        r, c = i % rows, i // rows
        fx_ = pad + c * (colw + 40)
        fy_ = head_h + r * rh
        kind = str(f.get("kind", "text"))
        lab = FT.fit_text(str(f.get("label", "")), colw * (0.62 if kind in ("toggle", "check", "radio") else 1), lab_px * 1.3, lab_px, 13, max_lines=1)
        lab_t = lab.lines[0] if lab.lines else ""
        if kind in ("toggle", "check", "radio"):
            ctl = {"toggle": '<span class="ui-tg"><b></b><i></i></span>', "check": f'<span class="ui-ck"><b></b>{U.TICK}</span>',
                   "radio": '<span class="ui-rd"><b></b></span>'}[kind]
            note = f'<em style="font-size:{lab_px * 0.82:.0f}px">{X.rich(f.get("note", ""))}</em>' if f.get("note") else ""
            parts.append(f'<div class="ff-f ff-sw" data-i="{i}" style="left:{fx_:.0f}px; top:{fy_:.0f}px; width:{colw:.0f}px; height:{rh * 0.8:.0f}px">'
                         f'<span class="ff-st"><b style="font-size:{val_px:.0f}px">{X.rich(lab_t)}</b>{note}</span>{ctl}</div>')
            ctl_x = fx_ + colw - (36 if kind == "toggle" else 17)
            pts.append((cx + ctl_x, cy + fy_ + rh * 0.4))
        else:
            ih = max(48, min(70, rh * 0.5))
            val = str(f.get("value", ""))
            shown = "•" * max(len(val), 6) if kind == "password" else val
            if kind == "select":
                vf = FT.fit_text(shown, colw - 90, ih * 0.7, val_px, 14, max_lines=1)
                opts = [str(o) for o in FT.as_list(f.get("options"))][:6] or [shown]
                pick = opts.index(val) if val in opts else 0
                ol = "".join(f'<div class="ff-op{" pk" if j == pick else ""}" style="height:{ih * 0.82:.0f}px; font-size:{vf.px}px">{X.rich(o)}</div>' for j, o in enumerate(opts))
                box = (f'<div class="ui-in ff-in" style="height:{ih:.0f}px; font-size:{vf.px}px"><span class="ff-sel">{X.rich(vf.lines[0] if vf.lines else shown)}</span><i class="ff-arr">▾</i></div>'
                       f'<div class="ff-drop" data-layout-allow-overlap style="top:{lab_px * 1.6 + ih + 6:.0f}px">{ol}</div>')
            else:
                vf = FT.fit_text(shown, colw - 50, ih * 0.7, val_px, 14, max_lines=1)
                typed = U.typed(X, vf.lines[0] if vf.lines else shown)
                box = f'<div class="ui-in ff-in" style="height:{ih:.0f}px; font-size:{vf.px}px"><span>{typed}</span><i class="ui-caret ff-car"></i></div>'
            parts.append(f'<div class="ff-f" data-i="{i}" style="left:{fx_:.0f}px; top:{fy_:.0f}px; width:{colw:.0f}px">'
                         f'<div class="ui-lab" style="font-size:{lab_px:.0f}px; margin-bottom:{lab_px * 0.35:.0f}px">{X.rich(lab_t)}</div>{box}</div>')
            pts.append((cx + fx_ + min(colw * 0.3, 160), cy + fy_ + lab_px * 1.6 + ih * 0.5))
    title = ""
    if p.get("title"):
        tf = FT.fit_text(str(p["title"]), cw - 2 * pad, 56, 46, 22, max_lines=1)
        sub = f'<div class="ff-sub">{X.rich(p["sub"])}</div>' if p.get("sub") else ""
        title = f'<div class="ff-h" style="left:{pad}px; top:30px; width:{cw - 2 * pad:.0f}px"><b style="font-size:{tf.px}px">{X.rich(tf.lines[0] if tf.lines else "")}</b>{sub}</div>'
    btn = ""
    if btn_h:
        bw = min(cw - 2 * pad, 420 if not P else cw - 2 * pad)
        bx_, by_ = (cw - bw) / 2 if not P else pad, ch - btn_h - 34
        btn = f'<div class="ui-btn ff-btn" style="position:absolute; left:{bx_:.0f}px; top:{by_:.0f}px; width:{bw:.0f}px; height:{btn_h - 10:.0f}px">{X.rich(p.get("submit", "提交"))}</div>'
        bpt = (cx + bx_ + bw / 2, cy + by_ + (btn_h - 10) / 2)
    done = str(p.get("done", "已提交"))
    toast = f'<div class="ui-toast ff-toast" style="left:{cx + cw / 2:.0f}px; top:{cy - 10:.0f}px">{U.TICK}{X.rich(done)}</div>'
    card = f'<div class="ui-card ff-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{ch:.0f}px">{title}{"".join(parts)}{btn}</div>'
    cur = '<div class="ff-ptr">' + U.CURSOR + '</div><i class="ui-rip ff-rip"></i>' if p.get("cursor", True) else ""
    X.css("fx-form-fill", """
.ff-h { position:absolute; display:flex; flex-direction:column; gap:6px; }
.ff-h b { font-family:var(--f-display, var(--f-body)); font-weight:900; color:var(--card-fg); white-space:nowrap; }
.ff-sub { font:500 22px var(--f-body); color:color-mix(in srgb, var(--card-fg) 55%, transparent); }
.ff-f { position:absolute; }
.ff-sw { display:flex; align-items:center; justify-content:space-between; gap:16px; border-bottom:1px solid color-mix(in srgb, var(--card-fg) 10%, transparent); }
.ff-st { display:flex; flex-direction:column; gap:4px; min-width:0; }
.ff-st b { font-family:var(--f-body); font-weight:800; color:var(--card-fg); white-space:nowrap; }
.ff-st em { font-style:normal; color:color-mix(in srgb, var(--card-fg) 55%, transparent); }
.ff-arr { margin-left:auto; font-style:normal; opacity:.6; }
.ff-drop { position:absolute; left:0; right:0; z-index:5; background:var(--card); border-radius:12px; box-shadow:0 18px 40px rgba(0,0,0,.25), 0 0 0 1px color-mix(in srgb, var(--card-fg) 12%, transparent); padding:6px; opacity:0; transform-origin:50% 0; }
.ff-op { display:flex; align-items:center; padding:0 14px; border-radius:8px; font-family:var(--f-body); font-weight:600; color:var(--card-fg); }
.ff-op.pk { background:color-mix(in srgb, var(--accent) 16%, transparent); }
.ff-ptr { position:absolute; left:0; top:0; z-index:12; }
.ff-car { opacity:0; }
""")
    mk = U.mock(X, p, cx + cw - 16, cy + 14, right=True)
    _clip(X, cid, t, d, f'{card}{toast}{cur}{mk}', p)
    s = f"#{cid}"
    X.tw(f'tl.set("{s} .ff-toast", {{xPercent:-50, yPercent:-100}}, {t:.3f});')
    X.tw(f'tl.from("{s} .ff-card", {{y:60, scale:0.96, opacity:0, duration:0.65, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .ff-f, {s} .ff-btn", {{y:18, opacity:0, duration:0.4, ease:"expo.out", stagger:0.04}}, {t + 0.2:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    end = t + d - (1.4 if btn_h else 0.4)
    T = U.spread(n, t + 0.8, max(t + 0.9, end - 0.6))
    fixed = []
    say = []
    for i, f in enumerate(F):
        if f.get("at") is not None: T[i] = U.when(X, f["at"], t, T[i])
        fixed.append(f.get("at") is not None)
        say.append([str(f.get("value", "")), str(f.get("label", ""))])
    T = U.follow(X, say, t + 0.8, max(0.3, end - t - 0.8), T, fixed, gap=0.15)    # a field fills when it is said
    if cur: X.tw(f'tl.set("{s} .ff-ptr, {s} .ff-rip", {{x:{cx + cw * 0.8:.0f}, y:{cy + ch + 40:.0f}}}, {t:.3f});')
    gap = (T[1] - T[0]) if n > 1 else (end - T[0])
    mv = max(0.15, min(0.45, gap - 0.04))      # many fields in a short beat: quicker hops, no overlapping moves
    rd = max(0.2, min(0.5, gap - 0.02))
    for i, f in enumerate(F):
        ti = T[i]; kind = str(f.get("kind", "text"))
        fs = f'{s} .ff-f[data-i=\'{i}\']'
        if cur:
            X.tw(f'tl.to("{s} .ff-ptr", {{x:{pts[i][0]:.0f}, y:{pts[i][1]:.0f}, duration:{mv:.2f}, ease:"power2.inOut"}}, {ti - mv:.3f});')
            X.tw(f'tl.set("{s} .ff-rip", {{x:{pts[i][0]:.0f}, y:{pts[i][1]:.0f}}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{s} .ff-rip", {{scale:0.2, opacity:1}}, {{scale:1.2, opacity:0, duration:{rd:.2f}, ease:"power2.out", immediateRender:false}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{s} .ff-ptr .ui-cur", {{scale:1}}, {{keyframes:[{{scale:0.8, duration:0.08}}, {{scale:1, duration:0.14}}], immediateRender:false}}, {ti:.3f});')
        X.sfx(ti, "click")
        if kind == "toggle" and f.get("on", True):
            X.tw(f'tl.to("{fs} .ui-tg i", {{x:32, duration:0.28, ease:"back.out(2)"}}, {ti + 0.05:.3f});')
            X.tw(f'tl.to("{fs} .ui-tg b", {{opacity:1, duration:0.25}}, {ti + 0.05:.3f});')
        elif kind == "check" and f.get("on", True):
            X.tw(f'tl.to("{fs} .ui-ck b", {{opacity:1, duration:0.15}}, {ti + 0.04:.3f});')
            X.tw(f'tl.from("{fs} .ui-ck svg", {{scale:0.2, opacity:0, duration:0.3, ease:"back.out(3)"}}, {ti + 0.06:.3f});')
        elif kind == "radio" and f.get("on", True):
            X.tw(f'tl.to("{fs} .ui-rd b", {{scale:1, duration:0.3, ease:"back.out(3)"}}, {ti + 0.05:.3f});')
        elif kind == "select":
            X.tw(f'tl.to("{fs} .ui-in", {{boxShadow:"inset 0 0 0 3px rgba(226,50,31,1)", duration:0.15}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{fs} .ff-drop", {{opacity:0, scaleY:0.6}}, {{opacity:1, scaleY:1, duration:0.25, ease:"expo.out", immediateRender:false}}, {ti + 0.05:.3f});')
            X.tw(f'tl.to("{fs} .ff-drop", {{opacity:0, duration:0.2}}, {ti + max(0.6, min(1.2, gap - 0.3)):.3f});')
            X.tw(f'tl.from("{fs} .ff-sel", {{opacity:0, duration:0.2}}, {ti + max(0.6, min(1.2, gap - 0.3)):.3f});')
            X.tw(f'tl.to("{fs} .ui-in", {{boxShadow:"inset 0 0 0 2px rgba(0,0,0,.12)", duration:0.2}}, {ti + max(0.8, min(1.3, gap - 0.2)):.3f});')
        elif kind not in ("toggle", "check", "radio"):
            val = str(f.get("value", ""))
            shown = "•" * max(len(val), 6) if kind == "password" else val
            m = len(shown)
            nxt = T[i + 1] if i + 1 < n else end
            cps = max(12.0, m / max(0.35, (nxt - ti) * 0.6))
            X.tw(f'tl.to("{fs} .ui-in", {{boxShadow:"inset 0 0 0 3px rgba(226,50,31,1)", duration:0.15}}, {ti:.3f});')
            U.type_in(X, fs, ti + 0.1, m, cps=cps)
            X.tw(f'tl.fromTo("{fs} .ff-car", {{opacity:0}}, {{opacity:1, duration:0.01, immediateRender:false}}, {ti:.3f});')
            X.tw(f'tl.to("{fs} .ff-car", {{opacity:0, duration:0.01}}, {max(nxt - 0.1, ti + 0.02):.3f});')
            X.tw(f'tl.to("{fs} .ui-in", {{boxShadow:"inset 0 0 0 2px rgba(0,0,0,.12)", duration:0.2}}, {max(nxt - 0.1, ti + 0.16):.3f});')
            X.sfx(ti + 0.1, "type")
    if btn_h:
        tb = end + 0.1
        if cur:
            X.tw(f'tl.to("{s} .ff-ptr", {{x:{bpt[0]:.0f}, y:{bpt[1]:.0f}, duration:0.45, ease:"power2.inOut"}}, {tb - 0.45:.3f});')
            X.tw(f'tl.set("{s} .ff-rip", {{x:{bpt[0]:.0f}, y:{bpt[1]:.0f}}}, {tb:.3f});')
            X.tw(f'tl.fromTo("{s} .ff-rip", {{scale:0.2, opacity:1}}, {{scale:1.4, opacity:0, duration:0.55, ease:"power2.out", immediateRender:false}}, {tb:.3f});')
        X.tw(f'tl.fromTo("{s} .ff-btn", {{scale:1}}, {{keyframes:[{{scale:0.94, duration:0.1}}, {{scale:1, duration:0.2, ease:"back.out(3)"}}], immediateRender:false}}, {tb:.3f});')
        X.tw(f'tl.fromTo("{s} .ff-toast", {{opacity:0, y:20}}, {{opacity:1, y:0, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {tb + 0.25:.3f});')
        X.sfx(tb, "click"); X.sfx(tb + 0.25, "pop")
    X.tw(f'tl.fromTo("{s} .ff-card", {{rotationX:0}}, {{rotationX:{0 if P else 2}, scale:1.02, duration:{d:.2f}, ease:"sine.inOut", immediateRender:false}}, {t + 0.7:.3f});')


FX = {"form_fill": form_fill}
