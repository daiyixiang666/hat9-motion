"""播客切片 (podcast clip): a player card — cover art over a spinning record, show and episode titles, the hosts'
avatars with the speaker's ring pulsing to the real loudness of the clip, a progress bar with timecodes and the
words lighting up as they are said. The clip really plays.

p: audio · words (words.json for that audio; optional) · a / b (seconds in the audio) · show · episode · ep (number)
   · hosts [{name, avatar}] (1–4) · speaker (index) · turns [[seconds into the clip, host index], …] · art (cover
   image; default a typographic cover) · vol
Adapts: 1–4 hosts (avatars shrink), turns between speakers, no timestamps (the subtitle line is skipped and the
waveform carries the beat), long show / episode names (fitted to 1–2 lines), 16:9 side-by-side or 9:16 stacked.
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
.pc-disc { position:absolute; border-radius:50%; background:repeating-radial-gradient(circle at 50% 50%, #161616 0 3px, #222 3px 5px); box-shadow:0 20px 60px rgba(0,0,0,.4); }
.pc-disc::after { content:''; position:absolute; inset:36%; border-radius:50%; background:var(--accent); box-shadow:inset 0 0 0 6px rgba(0,0,0,.25); }
.pc-art { position:absolute; border-radius:18px; overflow:hidden; box-shadow:0 26px 70px rgba(0,0,0,.35); }
.pc-art img { width:100%; height:100%; object-fit:cover; display:block; }
.pc-gen { position:absolute; inset:0; padding:9%; display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(150deg, var(--accent), color-mix(in srgb, var(--accent) 35%, #111)); color:#fbfaf6; }
.pc-gen b { font-family:var(--f-display); font-weight:900; line-height:1.05; }
.pc-gen span { font:800 0.9em var(--f-mono, monospace); letter-spacing:.14em; opacity:.85; }
.pc-gen i { font-style:normal; align-self:flex-start; font:900 1em var(--f-mono, monospace); color:#111; background:#f6ce3a; padding:.15em .5em; border-radius:.25em; }
.pc-info { position:absolute; display:flex; flex-direction:column; gap:14px; color:var(--fg); }
.pc-show { font:800 22px var(--f-body); letter-spacing:.12em; color:var(--muted); }
.pc-ep { font-family:var(--f-display); font-weight:900; line-height:1.15; }
.pc-hosts { display:flex; gap:16px; align-items:center; margin-top:6px; }
.pc-host { position:relative; display:flex; align-items:center; gap:10px; font:700 22px var(--f-body); color:var(--fg); }
.pc-host .rg { position:absolute; left:-6px; top:-6px; border-radius:50%; border:4px solid var(--accent); opacity:0; }
.pc-bar { position:relative; height:8px; border-radius:4px; background:color-mix(in srgb, var(--fg) 18%, transparent); margin-top:8px; }
.pc-bar i { position:absolute; left:0; top:0; bottom:0; width:100%; border-radius:4px; background:var(--accent); transform-origin:0 50%; }
.pc-tc { display:flex; justify-content:space-between; font:700 19px var(--f-mono, monospace); color:var(--muted); }
.pc-ctl { display:flex; gap:26px; align-items:center; font:900 30px var(--f-body); color:var(--fg); }
.pc-ctl b { display:grid; place-items:center; width:68px; height:68px; border-radius:50%; background:var(--fg); color:var(--bg); font-size:28px; }
"""


def podcast(X, cid, t, d, p):
    W, H, P = X.W, X.H, X.portrait
    au = p.get("audio")
    a = float(p.get("a", 0))
    full = fit.duration(A.src_abs(X, au)) if au else d
    b = float(p.get("b") or full)
    lead = 0.45
    run = max(0.3, min(b - a, d - lead - 0.2))
    x0, y0, x1, y1 = C.area(X, p)
    if P:
        art = min(500, x1 - x0 - 120); ax, ay = x0 + (x1 - x0 - art) / 2 - 60, y0 + 10
        ix, iy, iw = x0, ay + art + 40, min(x1, X.W - 120) - x0      # the lower half keeps the right 120 px for the platform buttons
    else:
        art = min(480, (y1 - y0) - 40); ax, ay = x0 + 20, y0 + (y1 - y0 - art) / 2
        ix, iy, iw = ax + art + art * 0.42 + 70, ay - 10, (x1 - (ax + art + art * 0.42 + 70))
    disc = art * 0.94
    show, ep_t, epn = p.get("show", ""), p.get("episode", ""), p.get("ep", "")
    X.used_text.update(str(show) + str(ep_t) + str(epn) + "EP.▶⏮⏭")
    if p.get("art"):
        art_html = f'<img src="{X.asset(p["art"])}" alt="">'
    else:
        sf = fit.fit_text(str(show), art * 0.8, art * 0.5, art * 0.17, 20, lh=1.05, max_lines=3)
        art_html = (f'<div class="pc-gen" style="font-size:{art * 0.05:.0f}px"><span>PODCAST</span>'
                    f'<b style="font-size:{sf.px}px">{"<br>".join(X.rich(l) for l in sf.lines)}</b>' + (f"<i>EP.{X.rich(epn)}</i>" if epn else "<i>EP</i>") + "</div>")
    hosts = p.get("hosts") or [{"name": "主持人"}]
    hosts = [h if isinstance(h, dict) else {"name": str(h)} for h in hosts][:4]
    asz = 62 if len(hosts) <= 2 else 52
    hh = "".join(f'<div class="pc-host" data-i="{i}"><i class="rg" style="width:{asz + 12}px; height:{asz + 12}px"></i>{C.mono_html(X, h.get("name"), asz, image=h.get("avatar"))}<span>{X.rich(h.get("name", ""))}</span></div>'
                 for i, h in enumerate(hosts))
    X.used_text.update("".join(h.get("name", "") for h in hosts))
    ef = fit.fit_text(str(ep_t), iw, 130 if not P else 120, 54 if not P else 50, 26, lh=1.15, max_lines=2)
    lines = A.karaoke(X, p["words"], a, a + run, maxlen=13 if not P else 10) if p.get("words") else []
    kr_h = 92 if not P else 96
    info = (f'<div class="pc-info" style="left:{ix:.0f}px; top:{iy:.0f}px; width:{iw:.0f}px">'
            f'<div class="pc-show">{X.rich(show)}</div><div class="pc-ep" style="font-size:{ef.px}px">{"<br>".join(X.rich(l) for l in ef.lines)}</div>'
            f'<div class="pc-hosts">{hh}</div><div class="pc-bar"><i></i></div>'
            f'<div class="pc-tc"><span class="pc-t0">{A.tc(0)}</span><span>-{A.tc(run)}</span></div>'
            f'<div class="pc-ctl"><span>⏮</span><b>▶</b><span>⏭</span></div></div>')
    kr = ""
    if lines:
        ky = (iy + 520) if not P else (iy + 470)
        ky = min(ky, y1 - kr_h)
        kr, _ = A.kara_html(X, lines, x0 if P else ix, ky, iw, kr_h, 62 if not P else 60, 30, "kr pc-k")
    shell = (f'<div class="pc-disc" style="left:{ax + art - disc * 0.62:.0f}px; top:{ay + (art - disc) / 2:.0f}px; width:{disc:.0f}px; height:{disc:.0f}px"></div>'
             f'<div class="pc-art" style="left:{ax:.0f}px; top:{ay:.0f}px; width:{art:.0f}px; height:{art:.0f}px">{art_html}</div>{info}{kr}')
    X.css("fx-podcast", CSS)
    X.css("fx-cite-base", C.CSS)     # .ct-mono discs, .ct-l lines
    _clip(X, cid, t, d, shell, p)
    if au: A.audio(X, cid, au, t + lead, run, start=a, vol=float(p.get("vol", 1)))
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .pc-art", {{x:-60, opacity:0, rotation:-4, duration:0.7, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.fromTo("{S} .pc-disc", {{x:{-disc * 0.4:.0f}, opacity:0}}, {{x:0, opacity:1, duration:0.8, ease:"expo.out"}}, {t + 0.15:.3f});')
    X.tw(f'tl.fromTo("{S} .pc-disc", {{rotation:0}}, {{rotation:{min(720, 200 * d):.0f}, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
    X.tw(f'tl.from("{S} .pc-info > *", {{x:40, opacity:0, duration:0.5, ease:"expo.out", stagger:0.07}}, {t + 0.2:.3f});')
    X.tw(f'tl.fromTo("{S} .pc-bar i", {{scaleX:0}}, {{scaleX:1, duration:{run:.2f}, ease:"none"}}, {t + lead:.3f});')
    X.tw(f'(()=>{{const o={{v:0}}, el=document.querySelector("{S} .pc-t0"); tl.to(o, {{v:{run:.2f}, duration:{run:.2f}, ease:"none", onUpdate:()=>{{const s=Math.max(0,Math.round(o.v)); el.textContent=String(Math.floor(s/60)).padStart(2,"0")+":"+String(s%60).padStart(2,"0");}}}}, {t + lead:.3f});}})();')
    # who speaks when, and the speaker's ring breathing with the clip's loudness (10 samples a second)
    turns = sorted([(float(x[0]), int(x[1])) for x in (p.get("turns") or [])]) or [(0.0, int(p.get("speaker", 0)))]
    env = A.peaks(X, au, a, a + run, max(4, int(run * 10))) if au else [0.4] * max(4, int(run * 10))
    step = run / len(env)
    for j, (ts, hi) in enumerate(turns):
        hi = min(hi, len(hosts) - 1)
        te = turns[j + 1][0] if j + 1 < len(turns) else run
        sel = f'{S} .pc-host[data-i="{hi}"] .rg'
        X.tw(f"tl.set('{sel}', {{opacity:1}}, {t + lead + ts:.3f}); tl.set('{sel}', {{opacity:0}}, {t + lead + te:.3f});")
        k0, k1 = int(ts / step), int(te / step)
        frames = ",".join(f"{{scale:{1 + 0.16 * v:.3f}, duration:{step:.3f}}}" for v in env[k0:k1]) or f"{{scale:1, duration:{te - ts:.2f}}}"
        X.tw(f"tl.to('{sel}', {{keyframes:[{frames}], ease:'none'}}, {t + lead + ts:.3f});")
    if lines: A.kara_tweens(X, f"{S} .pc-k", lines, t + lead, t + d)


FX = {"podcast": podcast}
