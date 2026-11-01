"""引用一段音频 (audio / podcast quote — "他在节目里是这么说的"): the clip really plays; its waveform fills as it is
heard, a playhead runs, and the words light up character by character from their timestamps (karaoke), one line at
a time. Speaker, role, source and date frame the card. Without timestamps the quote is shown whole and the
waveform still runs.

p: audio · words (words.json for that audio; optional) · a / b (seconds in the audio; default the whole file, up to
   the beat) · quote (shown when there are no words) · who · role · source · date · avatar · kicker ("音频引用") ·
   bars (waveform bars; default by width) · vol (1)
Adapts: any clip length (plays min(b−a, beat)), 1 to many karaoke lines (all at one size, the longest fits),
no timestamps (static quote, fitted to 3 lines), no avatar (initials), 16:9 card or 9:16 stacked card.
"""
import importlib.util, pathlib, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


A, C = _load("_av"), _load("_cite")

CSS = """
.aq-card { position:absolute; background:var(--card); color:var(--card-fg, var(--fg)); border-radius:22px; box-shadow:0 30px 80px rgba(0,0,0,.28); --kr-dim:color-mix(in srgb, var(--card-fg, var(--fg)) 28%, transparent); --wave-dim:color-mix(in srgb, var(--card-fg, var(--fg)) 22%, transparent); }
.aq-head { position:absolute; display:flex; align-items:center; gap:18px; }
.aq-who b { display:block; font:900 34px var(--f-display); line-height:1.1; }
.aq-who span { font:600 21px var(--f-mono, monospace); color:var(--muted); }
.aq-src { position:absolute; text-align:right; font:700 20px var(--f-mono, monospace); color:var(--muted); line-height:1.5; }
.aq-src b { color:var(--card-fg, var(--fg)); }
.aq-kick { position:absolute; display:flex; align-items:center; gap:10px; font:800 20px var(--f-body); letter-spacing:.14em; color:var(--card); background:var(--card-fg, var(--fg)); padding:6px 14px; border-radius:6px; }
.aq-kick i { font-style:normal; }
.aq-q { position:absolute; font-family:var(--f-body); font-weight:900; line-height:1.25; }
.aq-tc { position:absolute; display:flex; justify-content:space-between; font:700 19px var(--f-mono, monospace); color:var(--muted); }
.aq-mark { position:absolute; font:900 160px/1 var(--f-quote, var(--f-display)); color:var(--accent); opacity:.9; }
"""


def audio_quote(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    au = p.get("audio")
    a = float(p.get("a", 0))
    full = fit.duration(A.src_abs(X, au)) if au else d
    b = float(p.get("b") or full)
    lead = 0.4
    run = max(0.3, min(b - a, d - lead - 0.2))
    x0, y0, x1, y1 = C.area(X, p)
    cw = (x1 - x0) if P else min(1360, x1 - x0)
    chh = min(y1 - y0, 760 if P else 600)
    cx, cy = x0 + (x1 - x0 - cw) / 2, y0 + (y1 - y0 - chh) / 2
    pad = 44 if not P else 40
    who, role = p.get("who", ""), p.get("role", "")
    X.used_text.update(str(who) + str(role))
    av = C.mono_html(X, who or "?", 84, image=p.get("avatar"))
    head = f'<div class="aq-head" style="left:{pad}px; top:{pad}px">{av}<div class="aq-who"><b>{X.rich(who)}</b><span>{X.rich(role)}</span></div></div>'
    src_txt = [x for x in (p.get("source", ""), p.get("date", "")) if x]
    X.used_text.update("".join(map(str, src_txt)))
    src = (f'<div class="aq-src" style="right:{pad}px; top:{pad + 8}px">' + "".join(f"<div>{'<b>' if i == 0 else ''}{X.rich(s)}{'</b>' if i == 0 else ''}</div>" for i, s in enumerate(src_txt)) + "</div>") if not P else \
          (f'<div class="aq-src" style="left:{pad}px; right:auto; text-align:left; top:{pad + 100}px">' + " · ".join(X.rich(s) for s in src_txt) + "</div>")
    kick = p.get("kicker", "音频引用")
    X.used_text.update(kick + "▶")
    # waveform at the bottom of the card
    ww = cw - 2 * pad; wh = 84 if not P else 96
    tw = min(ww, X.W - 120 - cx - pad) if P else ww     # 9:16: text keeps out of the right 120 px button zone (the bars may run on)
    wy = chh - pad - wh - 34
    n = int(p.get("bars") or max(40, min(140, ww / 11)))
    pk = A.peaks(X, au, a, a + run, n) if au else [0.3] * n
    wave = A.wave_html(X, pk, pad, wy, ww, wh, "aw aq-w")
    tc = f'<div class="aq-tc" style="left:{pad}px; width:{tw:.0f}px; top:{wy + wh + 12:.0f}px"><span class="aq-t0">{A.tc(0)}</span><span>{A.tc(run)}</span></div>'
    X.used_text.update("0123456789:")
    # the words
    qy = (pad + 120) if not P else (pad + 160)
    qh = wy - qy - 30
    lines = A.karaoke(X, p["words"], a, a + run, maxlen=14 if not P else 9) if p.get("words") else []
    if lines:
        kr, px = A.kara_html(X, lines, pad, qy, tw, qh, 66 if not P else 64, 30, "kr aq-k")
        words = kr
    else:
        q = p.get("quote", "")
        f = C.fitted(X, f"“{q}”", tw - 40, qh, 60 if not P else 56, 28, max_lines=3 if not P else 4, lh=1.25)     # the marks are measured too
        words = f'<div class="aq-q" style="left:{pad + 20}px; top:{qy + (qh - f.n * f.px * 1.25) / 2:.0f}px; width:{tw - 40:.0f}px; font-size:{f.px}px">{C.lines(X, f)}</div>'
    mark = f'<div class="aq-mark" style="left:{pad - 12}px; top:{qy - 40}px">“</div>' if lines else ""
    card = (f'<div class="aq-card" style="left:{cx:.0f}px; top:{cy:.0f}px; width:{cw:.0f}px; height:{chh:.0f}px">'
            f'<div class="aq-kick" style="left:{pad}px; top:-18px"><i>▶</i>{X.rich(kick)}</div>{head}{src}{mark}{words}{wave}{tc}</div>')
    X.css("fx-aq", CSS)
    X.css("fx-cite-base", C.CSS)     # .ct-mono discs, .ct-l lines
    _clip(X, cid, t, d, card, p)
    if au: A.audio(X, cid, au, t + lead, run, start=a, vol=float(p.get("vol", 1)))
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .aq-card", {{y:60, scale:0.95, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{S} .aq-kick, {S} .aq-head > *, {S} .aq-src", {{y:16, opacity:0, duration:0.4, ease:"expo.out", stagger:0.06}}, {t + 0.15:.3f});')
    X.tw(f'tl.from("{S} .aq-w .row i", {{scaleY:0, duration:0.4, ease:"expo.out", stagger:{{each:0.004, from:"start"}}}}, {t + 0.1:.3f});')
    A.wave_tweens(X, f"{S} .aq-w", t + lead, run, ww)
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{S} .aq-t0"); tl.to(o, {{v:{run:.2f}, duration:{run:.2f}, ease:"none", onUpdate:()=>{{const s=Math.max(0,Math.round(o.v)); el.textContent=String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");}}}}, {t + lead:.3f});}})();')
    if lines:
        A.kara_tweens(X, f"{S} .aq-k", lines, t + lead, t + d)
        X.tw(f'tl.from("{S} .aq-mark", {{scale:0.4, opacity:0, duration:0.4, ease:"back.out(2)"}}, {t + 0.3:.3f});')
    else:
        X.tw(f'tl.from("{S} .aq-q .ct-l > *", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.1}}, {t + 0.4:.3f});')
    t_end = min(t + d, t + lead + run)        # the card creeps while the clip plays; after it ends, a clear push so the tail never stands still
    X.tw(f'tl.to("{S} .aq-card", {{scale:1.02, duration:{max(0.2, t_end - t - 0.6):.2f}, ease:"none"}}, {t + 0.6:.3f});')
    if t + d - t_end > 0.4:
        X.tw(f'tl.to("{S} .aq-card", {{scale:1.07, y:-14, duration:{t + d - t_end:.2f}, ease:"power1.inOut"}}, {max(t + 0.8, t_end):.3f});')


FX = {"audio_quote": audio_quote}
