"""访谈切片 (interview clip · the layout of 访谈 / 播客切片 accounts: a framed shot of the guest, a name bar, the
question on a card and the answer as big subtitles; VideoHive Lower Thirds category, #1 6.3K):
the footage (video or still, any aspect, reframed by focus) sits in a rounded frame with a running timecode and a
「访谈切片」 tag; the name bar slides in; the question card lands; the answer types in line by line with its
keyword marked. An optional host picture-in-picture sits in the frame's corner.

p: video | image (the guest) · focus · start · name · role · org · q (the question) · a (the answer; *keyword*) ·
   topic (default 「访谈切片」) · ep · tc (start timecode "12:34") · host {name, video | image} · mock
Adapts: landscape / portrait / square footage (cover with focus), names and roles of any length (fitted), questions
≤3 lines, answers ≤5 lines (fitted), no question / no answer.
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
SO = U.SO


def _tc(s):
    try:
        mm, ss = str(s).split(":"); return int(mm) * 60 + int(ss)
    except Exception: return 0


def _show(X, sel, t, d):
    """FT.media's video wrapper is an untimed root sibling: show it only inside the beat."""
    X.tw(f'tl.set("{sel}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.set("{sel}", {{visibility:"hidden"}}, {t + d:.3f});')


def interview(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    src = p.get("video") or p.get("image")
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 30
    aw, ah = x1 - x0, y1 - y0
    if P:
        fw = aw; fh = min(ah * 0.46, aw * 0.8)
        fx_, fy_ = x0, y0
        px0, py0, pw, ph = x0, fy_ + fh + 34, aw, y1 - (fy_ + fh + 34)
    else:
        fw = min(aw * 0.58, ah * 16 / 9 * 0.98); fh = min(ah, fw * 9 / 16 * 1.18)
        fx_, fy_ = x0, y0 + (ah - fh) / 2
        px0, py0, pw, ph = fx_ + fw + 70, y0 + 30, x1 - (fx_ + fw + 70), ah - 60
    rad = 26
    # footage
    pic, vsel = "", None
    if src:
        if FT.is_video(src):
            _, vsel = FT.media(X, cid, "iv", src, t, d, "iv-m", focus=p.get("focus", "50% 35%"), z=3, start=float(p.get("start", 0)),
                               extra_style=f"inset:auto; left:{fx_:.0f}px; top:{fy_:.0f}px; width:{fw:.0f}px; height:{fh:.0f}px; border-radius:{rad}px; background:radial-gradient(ellipse at 50% 30%, color-mix(in srgb, var(--fg) 16%, var(--bg)), color-mix(in srgb, var(--fg) 4%, var(--bg))); visibility:hidden;")
            _show(X, vsel, t, d)
        else:
            pic = f'<img class="iv-m" src="{X.asset(src)}" alt="" style="object-position:{FT.focus_css(p.get("focus", "50% 35%"))}">'
    tc0 = _tc(p.get("tc", "00:00"))
    topic = str(p.get("topic", "访谈切片")) + (f" · {p['ep']}" if p.get("ep") else "")
    nbw = min(fw * 0.78, 620)
    nf = FT.fit_text(str(p.get("name", "")), nbw - 40, 54, 42 if not P else 40, 18, max_lines=1)
    role = " · ".join(x for x in (str(p.get("role", "")), str(p.get("org", ""))) if x)
    rf = FT.fit_text(role, nbw - 40, 36, 24, 13, max_lines=1) if role else None
    namebar = (f'<div class="iv-nb" style="left:{fx_ + 26:.0f}px; top:{fy_ + fh - (118 if role else 84):.0f}px; max-width:{nbw:.0f}px">'
               f'<b style="font-size:{nf.px}px">{X.rich(nf.lines[0] if nf.lines else "")}</b>'
               + (f'<em style="font-size:{rf.px}px">{X.rich(rf.lines[0] if rf.lines else "")}</em>' if rf else "") + '</div>') if p.get("name") else ""
    host = ""
    hp = p.get("host") or {}
    if isinstance(hp, dict) and (hp.get("image") or hp.get("video") or hp.get("name")):
        hs = fh * 0.3
        hx, hy = fx_ + fw - hs - 22, fy_ + 22
        hsrc = hp.get("image")
        if hp.get("video"):
            _, hsel = FT.media(X, cid, "ih", hp["video"], t, d, "ih-m", z=4, extra_style=f"inset:auto; left:{hx:.0f}px; top:{hy:.0f}px; width:{hs:.0f}px; height:{hs:.0f}px; border-radius:50%; box-shadow:0 0 0 5px var(--card); visibility:hidden;")
            _show(X, hsel, t, d)
            X.tw(f'tl.from("{hsel}", {{scale:0.4, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.7:.3f});')
            inner = ""
        elif hsrc:
            inner = f'<img src="{X.asset(hsrc)}" alt="">'
        else:
            inner = U.avatar(X, hp.get("name", "主持"), style=f"width:100%; height:100%; font-size:{hs * 0.4:.0f}px")
        tag = f'<em>{X.rich(hp.get("name", ""))}</em>' if hp.get("name") else ""
        host = f'<div class="iv-host" style="left:{hx:.0f}px; top:{hy:.0f}px; width:{hs:.0f}px; height:{hs:.0f}px">{inner}{tag}</div>'
    frame = (f'<div class="iv-f{" vid" if vsel else ""}" style="left:{fx_:.0f}px; top:{fy_:.0f}px; width:{fw:.0f}px; height:{fh:.0f}px; border-radius:{rad}px">{pic}<i class="iv-grad"></i></div>'
             f'<div class="iv-top" style="left:{fx_ + 22:.0f}px; top:{fy_ + 22:.0f}px"><i class="iv-dot"></i><span>{X.rich(topic)}</span><b class="iv-tc">{tc0 // 60:02d}:{tc0 % 60:02d}</b></div>'
             f'{namebar}{host}')
    # panel: question + answer
    pan = []
    qy = py0
    if p.get("q"):
        qf = FT.fit_text(str(p["q"]), pw - 100, ph * 0.26, 34 if not P else 34, 16, max_lines=3, lh=1.3)
        qh = qf.n * qf.px * 1.3 + 44
        pan.append(f'<div class="iv-q" style="left:{px0:.0f}px; top:{qy:.0f}px; width:{pw:.0f}px; min-height:{qh:.0f}px"><b>Q</b><span style="font-size:{qf.px}px">{"<br>".join(X.rich(x) for x in qf.lines)}</span></div>')
        qy += qh + (34 if not P else 28)
    if p.get("a"):
        af = FT.fit_text(str(p["a"]), pw - 20, (py0 + ph) - qy - 20, 58 if not P else 54, 22, max_lines=5, lh=1.3)
        rows = "".join(f'<span class="ln"><span>{X.rich(x)}</span></span>' for x in af.lines)
        pan.append(f'<div class="iv-a" style="left:{px0:.0f}px; top:{qy:.0f}px; width:{pw:.0f}px; font-size:{af.px}px"><i class="iv-am">A</i>{rows}</div>')
    X.used_text.update("0123456789:QA")
    X.css("fx-interview", """
.iv-f { position:absolute; overflow:hidden; background:radial-gradient(ellipse at 50% 30%, color-mix(in srgb, var(--fg) 14%, var(--bg)), color-mix(in srgb, var(--fg) 4%, var(--bg)));
  box-shadow:0 0 0 2px color-mix(in srgb, var(--fg) 10%, transparent), 0 26px 60px rgba(0,0,0,.25); }
.iv-f.vid { background:none; }
.iv-f .iv-m { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.iv-grad { position:absolute; inset:0; background:linear-gradient(to top, rgba(0,0,0,.55), transparent 42%); pointer-events:none; z-index:2; }
.iv-top { position:absolute; z-index:6; display:flex; align-items:center; gap:12px; font:700 22px var(--f-body); color:#fff; background:rgba(0,0,0,.45); padding:8px 16px; border-radius:999px; white-space:nowrap; }
.iv-dot { width:12px; height:12px; border-radius:50%; background:#ff3b30; }
.iv-tc { font:600 20px var(--f-mono, monospace); opacity:.85; margin-left:6px; }
.iv-nb { position:absolute; z-index:6; display:flex; flex-direction:column; gap:4px; padding:12px 22px 14px 20px; background:var(--card); color:var(--card-fg); border-left:8px solid var(--accent); border-radius:6px;
  box-shadow:0 14px 34px rgba(0,0,0,.3); }
.iv-nb b { font-family:var(--f-display, var(--f-body)); font-weight:900; white-space:nowrap; }
.iv-nb em { font-style:normal; font-family:var(--f-body); font-weight:600; color:color-mix(in srgb, var(--card-fg) 60%, transparent); white-space:nowrap; }
.iv-host { position:absolute; z-index:6; border-radius:50%; overflow:visible; box-shadow:0 0 0 5px var(--card), 0 12px 28px rgba(0,0,0,.35); }
.iv-host img { width:100%; height:100%; object-fit:cover; border-radius:50%; }
.iv-host em { position:absolute; left:50%; bottom:-14px; transform:translateX(-50%); font:800 18px var(--f-body); font-style:normal; color:var(--bg); background:var(--fg); padding:2px 10px; border-radius:999px; white-space:nowrap; }
.iv-q { position:absolute; display:flex; align-items:flex-start; gap:18px; padding:20px 24px; border-radius:18px; background:var(--card); color:var(--card-fg); box-sizing:border-box;
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 10%, transparent); }
.iv-q b { flex:none; font:900 30px var(--f-mono, monospace); color:var(--card); background:var(--accent); width:46px; height:46px; display:grid; place-items:center; border-radius:10px; }
.iv-q span { font-family:var(--f-body); font-weight:700; line-height:1.3; }
.iv-a { position:absolute; font-family:var(--f-display, var(--f-body)); font-weight:900; color:var(--fg); line-height:1.3; }
.iv-a .ln { display:block; overflow:hidden; padding-bottom:.05em; } .iv-a .ln > span { display:inline-block; }
.iv-am { display:block; font:900 24px var(--f-mono, monospace); font-style:normal; color:var(--accent); letter-spacing:.1em; margin-bottom:8px; }
.iv-a .em .emt { color:var(--accent); }
""")
    mk = U.mock(X, p, fx_ + fw, fy_ + fh + 10, right=True) if not host else U.mock(X, p, fx_ + 22, fy_ + 74)
    _clip(X, cid, t, d, f'{frame}{"".join(pan)}{mk}', p, transparent=bool(vsel))
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .iv-f", {{scale:0.94, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.02:.3f});')
    if vsel: X.tw(f'tl.from("{vsel}", {{scale:0.94, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.02:.3f});')
    X.tw(f'tl.from("{s} .iv-top", {{x:-20, opacity:0, duration:0.4, ease:"expo.out"}}, {t + 0.3:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    # running timecode
    X.tw(f'(()=>{{const o={{v:{tc0}}}, el=document.querySelector("{s} .iv-tc"); tl.to(o, {{v:{tc0 + d:.2f}, duration:{d:.2f}, ease:"none", onUpdate:()=>{{const v=Math.floor(o.v); el.textContent=String(Math.floor(v/60)).padStart(2,"0")+":"+String(v%60).padStart(2,"0");}}}}, {t:.3f});}})();')
    X.tw(f'tl.fromTo("{s} .iv-dot", {{opacity:1}}, {{opacity:0.25, duration:0.5, ease:"steps(1)", repeat:{max(1, int(d / 0.5)) - 1}, yoyo:true, immediateRender:false}}, {t:.3f});')
    if not vsel and pic:
        X.tw(f'tl.fromTo("{s} .iv-f .iv-m", {{scale:1.04}}, {{scale:1.1, duration:{d:.2f}, ease:"none", immediateRender:false}}, {t:.3f});')
    if namebar:
        X.tw(f'tl.fromTo("{s} .iv-nb", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.55, ease:"expo.out", immediateRender:false}}, {t + 0.5:.3f});')
        X.sfx(t + 0.5, "whoosh_soft")
    if host:
        X.tw(f'tl.from("{s} .iv-host", {{scale:0.4, opacity:0, duration:0.45, ease:"back.out(2)"}}, {t + 0.7:.3f});')
    ta = t + 0.8
    if p.get("q"):
        tq = U.when(X, p.get("at_q"), t, t + min(0.75, d * 0.2))
        X.tw(f'tl.from("{s} .iv-q", {{y:30, opacity:0, duration:0.5, ease:"expo.out"}}, {tq:.3f});')
        X.sfx(tq, "pop")
        ta = tq + (min(1.4, d * 0.25) if d >= 4 else d * 0.18)     # short beats: the answer follows the question sooner
    if p.get("a"):
        ta = U.when(X, p.get("at_a"), t, ta)
        X.tw(f'tl.from("{s} .iv-am", {{opacity:0, duration:0.3}}, {ta:.3f});')
        nl = max(1, len(af.lines))
        room = max(0.5, max(ta + 0.5, t + d * 0.55) - ta - 0.05)     # short beats: the lines land sooner, never still rising at the beat's settle point
        ld = min(0.6, room * 0.6)
        lst = min(0.16, (room - ld) / max(1, nl - 1))
        X.tw(f'tl.from("{s} .iv-a .ln > span", {{yPercent:110, duration:{ld:.2f}, ease:"expo.out", stagger:{lst:.3f}}}, {ta + 0.05:.3f});')
        X.sfx(ta, "enter")


FX = {"interview": interview}
