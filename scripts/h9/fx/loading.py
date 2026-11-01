"""等待 / 加载 Loading (S14 · 「AI 正在生成……」; 教程录屏里的等待、渲染进度):
a status card fills the wait — the progress bar eases forward with two believable stalls, the percentage counts,
status lines tick through (each turns into a check), typing dots pulse, and at the end it lands on 100 % with a
done state. Everything is stretched to the beat, so a 1 s blip and an 8 s render both read naturally.

Adapts: 1–8 s+; label from a word to a sentence (fitted); 0–6 status steps (shown one after another, the list
scrolls when there are more than fit); style bar | ring.
p: label · steps [text] · done (final word, default 完成) · style bar | ring
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


F, P = _load("_fit"), _load("_pace")


def loading(X, cid, t, d, p):
    Wv, Hv = F.frame_vmin(X)
    cw = min(70.0, Wv * 0.86)
    ls, ll = F.fit(p.get("label", "正在生成"), cw - 11 - 16, 6, 3.6, 2.0, 1)      # leave room for the dots and the % counter
    steps = [str(x) for x in (p.get("steps") or [])][:6]
    style = p.get("style", "bar")
    X.css("fx-p5lo", """
.fx .p5lo { position:relative; padding:5vmin 5.5vmin; border-radius:3vmin; background:var(--card); color:var(--card-fg, var(--fg));
  box-shadow:0 0 0 .2vmin color-mix(in srgb, var(--fg) 14%, transparent), 0 3vmin 8vmin rgba(0,0,0,.25); }
.fx .p5lo .hd { display:flex; align-items:center; gap:2vmin; font-family:var(--f-display); font-weight:800; white-space:nowrap; min-width:0; }
.fx .p5lo .hd > span:first-child { min-width:0; overflow:hidden; text-overflow:ellipsis; }
.fx .p5lo .hd .dots i { display:inline-block; width:1vmin; height:1vmin; margin-left:.6vmin; border-radius:50%; background:currentColor; }
.fx .p5lo .pc { margin-left:auto; font:700 3.2vmin var(--f-mono, monospace); font-variant-numeric:tabular-nums; }
.fx .p5lo .tr { margin-top:3vmin; height:1.4vmin; border-radius:.7vmin; background:color-mix(in srgb, var(--fg) 12%, transparent); overflow:hidden; }
.fx .p5lo .tr b { display:block; height:100%; width:100%; background:var(--accent); transform-origin:0 50%; border-radius:.7vmin; }
.fx .p5lo .rg { width:14vmin; height:14vmin; margin:3vmin auto 0; display:block; }
.fx .p5lo .rg circle { fill:none; stroke-width:6; } .fx .p5lo .rg .bk { stroke:color-mix(in srgb, var(--fg) 12%, transparent); } .fx .p5lo .rg .fg { stroke:var(--accent); stroke-linecap:round; }
.fx .p5lo .st { margin-top:3vmin; display:grid; gap:1.3vmin; height:var(--sh); overflow:hidden; }
.fx .p5lo .st div { display:flex; align-items:center; gap:1.6vmin; font:600 2.4vmin var(--f-body); white-space:nowrap; opacity:.35; }
.fx .p5lo .st div i { width:2.4vmin; height:2.4vmin; border-radius:50%; border:.35vmin solid currentColor; display:grid; place-items:center; font-style:normal; font-size:1.6vmin; flex:none; }
.fx .p5lo .ok { position:absolute; right:5.5vmin; top:-2.4vmin; font:800 2.2vmin var(--f-body); background:var(--accent); color:var(--bg); padding:.6vmin 1.8vmin; border-radius:9vmin; opacity:0; }
""")
    vis = min(len(steps), 4)
    row = 2.4 * 1.6                                   # 2.4vmin type at line-height 1.6
    sh = vis * row + max(vis - 1, 0) * 1.3 + 0.4
    meter = ('<div class="tr"><b></b></div>' if style == "bar" else
             '<svg class="rg" viewBox="0 0 100 100"><circle class="bk" cx="50" cy="50" r="42"/><circle class="fg" cx="50" cy="50" r="42" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" transform="rotate(-90 50 50)"/></svg>')
    st = (f'<div class="st" style="--sh:{sh:.1f}vmin">' + "".join(f'<div><i></i>{X.rich(x)}</div>' for x in steps) + "</div>") if steps else ""
    X.used_text.update("0123456789%✓")
    inner = (f'<div class="p5lo" style="width:{cw:.1f}vmin"><div class="hd" style="font-size:{ls:.2f}vmin"><span>{X.rich(ll[0])}</span><span class="dots"><i></i><i></i><i></i></span>'
             f'<span class="pc">0%</span></div>{meter}{st}<div class="ok">✓ {X.rich(p.get("done", "完成"))}</div></div>')
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    run = max(0.5, d - 0.45)
    # progress with two stalls: 0→38 % (fast), stall, →71 %, stall, →100 %
    marks = [(0.0, 0), (0.28, 38), (0.42, 41), (0.66, 71), (0.8, 74), (1.0, 100)]
    for (fa, va), (fb, vb) in zip(marks, marks[1:]):
        a, dd = t + 0.15 + fa * run, (fb - fa) * run
        if style == "bar": X.tw(f'tl.fromTo("{s} .p5lo .tr b", {{scaleX:{va / 100:.3f}}}, {{scaleX:{vb / 100:.3f}, duration:{dd:.3f}, ease:"power1.inOut", immediateRender:{"true" if fa == 0 else "false"}}}, {a:.3f});')
        else: X.tw(f'tl.fromTo("{s} .p5lo .rg .fg", {{strokeDashoffset:{100 - va}}}, {{strokeDashoffset:{100 - vb}, duration:{dd:.3f}, ease:"power1.inOut", immediateRender:{"true" if fa == 0 else "false"}}}, {a:.3f});')
        X.tw(f'(()=>{{const o={{v:{va}}}, el=document.querySelector("{s} .p5lo .pc"); tl.to(o, {{v:{vb}, duration:{dd:.3f}, ease:"power1.inOut", onUpdate:()=>{{el.textContent=Math.round(o.v)+"%";}}}}, {a:.3f});}})();')
    X.tw(f'tl.to("{s} .p5lo .dots i", {{y:"-0.8vmin", duration:0.22, ease:"sine.inOut", yoyo:true, repeat:{max(1, int(run / 0.22)) | 1}, stagger:0.1}}, {t + 0.1:.3f});')
    X.tw(f'tl.from("{s} .p5lo", {{y:40, opacity:0, scale:0.96, duration:0.45, ease:"expo.out"}}, {t:.3f});')
    for k in range(len(steps)):
        tk = t + 0.2 + run * (k + 0.6) / max(len(steps), 1)
        X.tw(f'tl.to("{s} .p5lo .st div:nth-child({k + 1})", {{opacity:1, duration:0.15}}, {tk:.3f});')
        if k + 1 < len(steps) or True:
            X.tw(f'tl.set("{s} .p5lo .st div:nth-child({k + 1}) i", {{background:"currentColor"}}, {tk + run / max(len(steps), 1) * 0.8:.3f});')
        if k >= vis:
            X.tw(f'tl.to("{s} .p5lo .st div", {{y:"-={row + 1.3:.2f}vmin", duration:0.25, ease:"power2.out"}}, {tk - 0.1:.3f});')
        X.sfx(tk, "tick", 0.2)
    X.tw(f'tl.fromTo("{s} .p5lo .ok", {{opacity:0, y:8}}, {{opacity:1, y:0, duration:0.3, ease:"back.out(2)", immediateRender:false}}, {t + d - 0.32:.3f});')
    X.sfx(t + d - 0.32, "bell", 0.35)


FX = {"loading": loading}
