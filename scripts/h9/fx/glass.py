"""液态玻璃卡片 Liquid Glass Card (2025 趋势：Bricks「Animate Like Apple (Liquid Glass UI)」76 万播放；Envato Elements
「Real Glass FX」Elements 分类 Popular 第 4): over drifting footage a frosted pane springs in — blur + saturation
behind it, a bright rim, a specular streak that sweeps once — and the number inside counts up.

Adapts: background = a still ("image", any aspect), footage ("video") or nothing (a slow colour-mesh); the value
can be tiny or huge (auto 万 / 亿 or K / M / B, "compact"), negative, or a word ("value_text"); kicker and text
from a word to a sentence (fitted); 0–4 extra rows of small stats ("rows": [[label, value], ...]).
p: image | video · value | value_text · unit · dec · kicker · tag · text · rows · compact · video_start
"""
from h9 import aefx
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]

aefx.PHOTO.add("glass")


def glass(X, cid, t, d, p):
    Wv, Hv = F.frame_vmin(X)
    cw = min(78.0, Wv * 0.8)
    if p.get("value_text") is not None:
        vtxt, num = str(p["value_text"]), None
        div, unit, dec = 1, p.get("unit", ""), 0
    else:
        num = float(p["value"])
        div, suf = F.compact(abs(num), p.get("compact", "cn"))
        unit = (suf + p.get("unit", "")) if div != 1 else p.get("unit", "")
        dec = int(p.get("dec", 1 if div != 1 else (0 if num == int(num) else 1)))
        vtxt = f"{num / div:,.{dec}f}"
    vs = min(17.0, (cw - 12) / max(F.em(vtxt) + F.em(unit) * 0.4, 1))
    ts, tl_ = F.fit(p.get("text", ""), cw - 12, 9, 2.8, 1.8, 2)
    rows = p.get("rows", [])[:4]
    X.css("fx-glass", """
.fx .gsi { position:absolute; inset:-4%; width:108%; height:108%; object-fit:cover; }
.fx .gsm { position:absolute; inset:-10%; background:radial-gradient(40% 50% at 30% 40%, color-mix(in srgb, var(--accent) 80%, transparent), transparent 70%),
  radial-gradient(45% 45% at 72% 60%, rgba(90,120,255,.75), transparent 70%), radial-gradient(35% 40% at 55% 25%, rgba(255,90,140,.6), transparent 70%), #101014; filter:blur(4vmin); }
.fx .gsc { position:relative; padding:5vmin 6vmin 5.4vmin; border-radius:4.4vmin; overflow:hidden;
  background:linear-gradient(135deg, rgba(255,255,255,.22), rgba(255,255,255,.04)), rgba(12,12,16,.34); backdrop-filter:blur(28px) saturate(160%) brightness(.8); -webkit-backdrop-filter:blur(28px) saturate(160%) brightness(.8);
  box-shadow:inset 0 0 0 .2vmin rgba(255,255,255,.55), inset 0 .6vmin 1.2vmin rgba(255,255,255,.35), inset 0 -.8vmin 2vmin rgba(0,0,0,.18), 0 4vmin 10vmin rgba(0,0,0,.35); color:#fff; }
.fx .gsc .sp { position:absolute; top:-30%; bottom:-30%; width:28%; left:-40%; background:linear-gradient(100deg, transparent, rgba(255,255,255,.55), transparent); transform:skewX(-18deg); }
.fx .gsc .k { font:700 2.4vmin var(--f-body); letter-spacing:.14em; opacity:.9; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:80%; }
.fx .gsc .v { margin-top:1.4vmin; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; letter-spacing:-.03em; font-variant-numeric:tabular-nums; text-shadow:0 .4vmin 3vmin rgba(0,0,0,.25); white-space:nowrap; }
.fx .gsc .v small { font-size:.4em; margin-left:.12em; }
.fx .gsc .s { margin-top:1.6vmin; font-family:var(--f-body); font-weight:600; line-height:1.45; opacity:.95; } .fx .gsc .s .fl { display:block; white-space:nowrap; }
.fx .gsc .pill { position:absolute; right:3.4vmin; top:3.4vmin; font:700 1.9vmin var(--f-mono, monospace); background:rgba(255,255,255,.22); padding:.5vmin 1.4vmin; border-radius:9vmin; box-shadow:inset 0 0 0 .15vmin rgba(255,255,255,.5); }
.fx .gsc .rw { margin-top:2.6vmin; padding-top:2vmin; border-top:.15vmin solid rgba(255,255,255,.35); display:grid; gap:1vmin; }
.fx .gsc .rw div { display:flex; justify-content:space-between; gap:3vmin; font:600 2.4vmin var(--f-body); white-space:nowrap; } .fx .gsc .rw b { font-family:var(--f-num, var(--f-display)); }
""")
    X.used_text.update("0123456789.,-%" + unit)
    if p.get("image"): bg = f'<img class="gsi" src="{X.asset(p["image"])}" alt="">'
    elif p.get("video"): bg = ""
    else: bg = '<div class="gsm"></div>'
    vhtml = f'<span class="n">{"0" if num is not None else X.rich(vtxt)}</span><small>{X.rich(unit)}</small>'
    rw = ('<div class="rw">' + "".join(f'<div><span>{X.rich(a)}</span><b>{X.rich(b)}</b></div>' for a, b in rows) + "</div>") if rows else ""
    inner = (f'{bg}<div class="gsc" style="width:{cw:.1f}vmin"><i class="sp"></i>' + (f'<div class="pill">{X.rich(p["tag"])}</div>' if p.get("tag") else "")
             + f'<div class="k">{X.rich(p.get("kicker", ""))}</div><div class="v" style="font-size:{vs:.2f}vmin">{vhtml}</div>'
             f'<div class="s" style="font-size:{ts:.2f}vmin">{F.lines_html(X, tl_)}</div>{rw}</div>')
    if p.get("video") and not p.get("image"):
        vsel = F.video_bg(X, cid, t, d, p["video"], p.get("video_start", 0))
        _clip(X, cid, t, d, inner, F.no_bg(p))
        X.tw(f'tl.fromTo("{vsel}", {{scale:1.0}}, {{scale:1.08, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    else:
        _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.fromTo("{s} .gsi", {{scale:1.0, xPercent:-1.5}}, {{scale:1.08, xPercent:1.5, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{s} .gsm", {{rotation:0, scale:1}}, {{rotation:25, scale:1.15, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{s} .gsc", {{y:120, scale:0.86, rotationX:18, opacity:0, transformPerspective:900, duration:0.9, ease:"elastic.out(1, 0.75)"}}, {t + 0.15:.3f});')
    X.tw(f'tl.fromTo("{s} .gsc .sp", {{xPercent:0}}, {{xPercent:620, duration:1.0, ease:"power2.inOut"}}, {t + 0.7:.3f});')
    X.tw(f'tl.from("{s} .gsc .k, {s} .gsc .pill", {{y:12, opacity:0, duration:0.4, ease:"expo.out", stagger:0.06}}, {t + 0.45:.3f});')
    if num is not None:
        fj = F.js_fmt(dec)
        X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{s} .n"), f={fj}; tl.to(o, {{v:{num / div}, duration:1.0, ease:"power3.out", onUpdate:()=>{{el.textContent=f(o.v);}}}}, {t + 0.5:.3f});}})();')
    else:
        X.tw(f'tl.from("{s} .gsc .v", {{y:20, opacity:0, duration:0.5, ease:"expo.out"}}, {t + 0.5:.3f});')
    X.tw(f'tl.from("{s} .gsc .s, {s} .gsc .rw div", {{y:16, opacity:0, duration:0.45, ease:"expo.out", stagger:0.07}}, {t + 0.95:.3f});')
    X.sfx(t + 0.15, "whoosh_soft"); X.sfx(t + 0.5, "tick")


FX = {"glass": glass}
