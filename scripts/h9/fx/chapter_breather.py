"""章节喘息 Chapter Breather (S07 · 第一章讲完，过渡到第二章; L04 章节进度; 所长林超 / 回形针 的章节页):
a 2–4 s rest between chapters — the finished chapter's title slides up and dims, its takeaways tick off with check
marks, the progress rail advances one segment, the next chapter number rolls over and its title rises in.

Adapts: 1–8 s (with < 2 s the recap is skipped and only the rail and the next title move); chapter titles from a word
to a phrase (fitted); 0–4 recap points; any chapter count 2–12 (rail segments).
p: done · next · n (index of the next chapter, 1-based) · total · recap [text]
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


def chapter_breather(X, cid, t, d, p):
    Wv, Hv = F.frame_vmin(X)
    total = max(2, int(p.get("total", 3))); n = max(1, min(total, int(p.get("n", 2))))
    recap = [str(x) for x in (p.get("recap") or [])][:4] if d >= 2 else []
    bw = Wv * (0.84 if X.portrait else 0.7)
    ds, dl = F.fit(p.get("done", ""), bw, 7, 3.2, 2.0, 1) if p.get("done") else (0, [])
    ns, nl = F.fit(p.get("next", ""), bw, Hv * 0.22, 9 if X.portrait else 8, 3.2, 2)
    X.css("fx-p5cb", """
.fx .p5cb { position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; padding:0 var(--pad); gap:2.6vmin; }
.fx .p5cb .dn { font-family:var(--f-body); font-weight:700; color:var(--muted); white-space:nowrap; display:flex; align-items:center; gap:1.4vmin; }
.fx .p5cb .dn s { text-decoration:none; position:relative; } .fx .p5cb .dn s::after { content:''; position:absolute; left:0; right:0; top:55%; height:.3vmin; background:currentColor; transform:scaleX(var(--k, 0)); transform-origin:0 50%; }
.fx .p5cb .rc { display:grid; gap:1.2vmin; } .fx .p5cb .rc div { display:flex; gap:1.4vmin; align-items:center; font:600 2.5vmin var(--f-body); color:var(--fg); white-space:nowrap; }
.fx .p5cb .rc div i { width:2.6vmin; height:2.6vmin; border-radius:50%; background:var(--accent); color:var(--bg); display:grid; place-items:center; font-style:normal; font-size:1.7vmin; flex:none; }
.fx .p5cb .rail { display:flex; gap:.8vmin; margin:1.4vmin 0; } .fx .p5cb .rail i { flex:1; height:.7vmin; border-radius:.35vmin; background:color-mix(in srgb, var(--fg) 15%, transparent); position:relative; overflow:hidden; }
.fx .p5cb .rail i b { position:absolute; inset:0; background:var(--fg); transform-origin:0 50%; } .fx .p5cb .rail i.cur b { background:var(--accent); }
.fx .p5cb .no { font:900 2.4vmin var(--f-mono, monospace); letter-spacing:.3em; color:var(--accent); height:3vmin; overflow:hidden; }
.fx .p5cb .no span { display:block; }
.fx .p5cb .nx { font-family:var(--f-display); font-weight:900; line-height:1.1; color:var(--fg); } .fx .p5cb .nx .fl { display:block; white-space:nowrap; overflow:hidden; }
.fx .p5cb .nx .fl > span { display:inline-block; }
""")
    rail = "".join(f'<i class="{"cur" if k == n - 1 else ""}"><b style="transform:scaleX({1 if k < n - 1 else 0})"></b></i>' for k in range(total))
    X.used_text.update("0123456789CHAPTER ✓")
    inner = (f'<div class="p5cb" style="--pad:{(7 if X.portrait else 14):.0f}vmin">'
             + (f'<div class="dn" style="font-size:{ds:.2f}vmin"><span>✓</span><s>{X.rich(dl[0])}</s></div>' if dl else "")
             + ('<div class="rc">' + "".join(f"<div><i>✓</i>{X.rich(r)}</div>" for r in recap) + "</div>" if recap else "")
             + f'<div class="rail">{rail}</div><div class="no"><span>CHAPTER {n - 1:02d}</span><span>CHAPTER {n:02d}</span></div>'
             + f'<div class="nx" style="font-size:{ns:.2f}vmin">' + "".join(f'<span class="fl"><span>{X.rich(l)}</span></span>' for l in P.fix_em(nl)) + "</div></div>")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    u = d / 4
    X.tw(f'tl.from("{s} .p5cb .dn", {{opacity:0, x:-20, duration:0.4, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.to("{s} .p5cb .dn s", {{"--k":1, duration:0.45, ease:"power2.inOut"}}, {t + 0.25:.3f});')
    if recap:
        X.tw(f'tl.from("{s} .p5cb .rc div", {{opacity:0, x:-14, duration:0.35, ease:"expo.out", stagger:{min(0.35, u / max(len(recap), 1)):.3f}}}, {t + 0.35:.3f});')
        X.tw(f'tl.from("{s} .p5cb .rc div i", {{scale:0, duration:0.3, ease:"back.out(3)", stagger:{min(0.35, u / max(len(recap), 1)):.3f}}}, {t + 0.45:.3f});')
    ta = t + (min(1.4, d * 0.4) if recap else min(0.5, d * 0.15))
    X.tw(f'tl.to("{s} .p5cb .rail i.cur b", {{scaleX:1, duration:{max(0.35, min(0.9, d * 0.25)):.2f}, ease:"power2.inOut"}}, {ta:.3f});')
    lift = min(0.7, d * 0.4)                         # a 1 s breather still lands its title inside the beat
    X.tw(f'tl.to("{s} .p5cb .no span", {{yPercent:-100, duration:{min(0.4, d * 0.25):.2f}, ease:"expo.inOut"}}, {ta + min(0.15, d * 0.05):.3f});')
    X.tw(f'tl.from("{s} .p5cb .nx .fl > span", {{yPercent:110, duration:{lift:.2f}, ease:"expo.out", stagger:0.08}}, {ta + min(0.25, d * 0.08):.3f});')
    if recap or dl: X.tw(f'tl.to("{s} .p5cb .dn, {s} .p5cb .rc", {{opacity:0.35, duration:0.5}}, {ta + 0.25:.3f});')
    P.push(X, f"{s} .p5cb", t, d, base=0.008, cap=0.05, origin="0% 50%")
    X.sfx(ta, "whoosh_soft", 0.3); X.sfx(ta + 0.25, "hit", 0.25)


FX = {"chapter_breather": chapter_breather}
