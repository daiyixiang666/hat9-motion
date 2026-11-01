"""引用名人原话 (quote card — "某某说过"): a giant quote mark swings in, the original words arrive one by one out of a
blur, the translation lifts in under them, the speaker block (portrait or a monogram) slides in with name, role and
the exact source; a big outlined year (or the source) holds the other side of the frame.

p: text (original words) · zh (translation; omit when the original is Chinese) · name · role · source · date ·
   image (portrait, optional) · year (big side mark; default = first 4-digit year in date) · hl (phrase to mark)
Adapts: a 3-word line to a long paragraph (auto size; ≤ 5 lines original + ≤ 3 lines translation), Chinese or Latin
originals, with or without a portrait, any name/role length; 16:9 = quote left + year right, 9:16 = stacked.
"""
import importlib.util, pathlib, re, sys
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = _load("_cite")


def cite_quote(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    year = str(p.get("year") or (re.search(r"(1[5-9]|20)\d\d", str(p.get("date", ""))) or [""])[0])
    if P:
        qx, qw, qh = x0, x1 - x0, round((y1 - y0) * 0.5)
    else:
        qw = round((x1 - x0) * 0.74); qx, qh = x0 + 60, round((y1 - y0) * 0.6)
    txt = str(p.get("text", ""))
    if p.get("hl") and p["hl"] in txt and "*" not in txt: txt = txt.replace(p["hl"], f"*{p['hl']}*", 1)
    zh = p.get("zh")
    of = C.fitted(X, txt, qw, qh * (0.62 if zh else 0.95), 96 if not P else 84, 30, max_lines=5, lh=1.16)
    zf = C.fitted(X, zh, qw, qh * 0.34, 46 if not P else 44, 22, max_lines=3, lh=1.3) if zh else None
    block = of.n * of.px * 1.16 + (zf.n * zf.px * 1.3 + 24 if zf else 0) + 44 + 100
    qy = y0 + max(130 if P else 110, (y1 - y0 - block) / 2 + (40 if P else 30))
    words = lambda line: "".join(f'<i class="cq-w">{X.rich(w)}</i>' if w.strip() else " " for w in re.findall(r"\*[^*]+\*|[A-Za-z0-9’'.,;:!?\-]+|\s+|.", line))
    orig = "".join(f'<span class="cq-l">{words(l)}</span>' for l in of.lines)
    msz = 92 if not P else 84
    who = " · ".join(x for x in (str(p.get("role", "")), ) if x)
    srcl = " · ".join(x for x in (str(p.get("source", "")), str(p.get("date", ""))) if x)
    X.used_text.update(str(p.get("name", "")) + who + srcl + year + "“”")
    by_top = qy + of.n * of.px * 1.16 + (zf.n * zf.px * 1.3 + 26 if zf else 0) + 44
    by = (f'<div class="cq-by" style="left:{qx}px; top:{by_top:.0f}px; width:{qw}px">{C.mono_html(X, p.get("name"), msz, p.get("image"))}'
          f'<div><b>{X.rich(p.get("name", ""))}</b>{f"<span>{X.rich(who)}</span>" if who else ""}{f"<em>{X.rich(srcl)}</em>" if srcl else ""}</div></div>')
    mark_px = (300 if not P else 260)
    side = ""
    if year:
        ysz = min(300, (x1 - x0) * (0.3 if P else 0.17))
        pos = f"right:{X.W - x1}px; top:{y0 - 10}px" if P else f"right:{X.W - x1}px; bottom:{X.H - y1 + 4}px"
        side = f'<div class="cq-year" data-layout-allow-overlap style="{pos}; font-size:{ysz:.0f}px">{X.rich(year)}</div>'
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-quote", """
.cq-mark { position:absolute; font-family:var(--f-quote, serif); font-weight:900; line-height:1; color:var(--accent); transform-origin:50% 60%; }
.cq-o { position:absolute; font-family:var(--f-quote, serif); font-weight:700; line-height:1.16; letter-spacing:-.01em; color:var(--fg); }
.cq-l { display:block; white-space:nowrap; } .cq-w { font-style:normal; display:inline-block; }
.cq-zh { position:absolute; font-family:var(--f-body); font-weight:800; line-height:1.3; color:var(--fg); opacity:.86; }
.cq-zh .ct-l { overflow:hidden; }
.cq-by { position:absolute; display:flex; align-items:center; gap:22px; }
.cq-by > div:last-child { display:flex; flex-direction:column; gap:4px; }
.cq-by b { font:900 34px var(--f-body); color:var(--fg); } .cq-by span { font:600 22px var(--f-body); color:var(--muted); }
.cq-by em { font-style:normal; font:600 18px var(--f-mono, monospace); color:var(--muted); letter-spacing:.03em; }
.cq-by::before { content:''; position:absolute; left:0; right:0; top:-22px; height:2px; background:color-mix(in srgb, var(--fg) 20%, transparent); transform-origin:0 50%; }
.cq-year { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.82; letter-spacing:-.03em; color:color-mix(in srgb, var(--fg) 7%, transparent); -webkit-text-stroke:3px color-mix(in srgb, var(--fg) 55%, transparent); white-space:nowrap; }
.cq-vert { writing-mode:vertical-rl; text-align:right; }
""")
    inner = (f'<div class="ct-root"><div class="cq-cam">{side}<div class="cq-mark" style="left:{qx - (40 if not P else 10)}px; top:{qy - mark_px * 0.55:.0f}px; font-size:{mark_px}px">“</div>'
             f'<div class="cq-o" style="left:{qx}px; top:{qy}px; width:{qw}px; font-size:{of.px}px">{orig}</div>'
             + (f'<div class="cq-zh" style="left:{qx}px; top:{qy + of.n * of.px * 1.16 + 24:.0f}px; width:{qw}px; font-size:{zf.px}px">{C.lines(X, zf)}</div>' if zf else "")
             + by + '</div></div>')
    _clip(X, cid, t, d, inner, p)
    X.css("fx-cite-quote-cam", ".cq-cam { position:absolute; inset:0; }")
    S = f"#{cid}"
    X.tw(f'tl.fromTo("{S} .cq-mark", {{scale:0.3, rotation:-30, opacity:0}}, {{scale:1, rotation:0, opacity:1, duration:0.7, ease:"back.out(1.8)"}}, {t + 0.05:.3f});')
    nw = sum(len(re.findall(r"\*[^*]+\*|[A-Za-z0-9’'.,;:!?\-]+|\S", l)) for l in of.lines)
    st = max(0.03, min(0.12, 1.1 / max(nw, 1)))
    X.tw(f'tl.from("{S} .cq-w", {{opacity:0, y:18, filter:"blur(10px)", duration:0.45, ease:"power3.out", stagger:{st:.3f}}}, {t + 0.25:.3f});')
    X.sfx(t + 0.25, "whoosh_soft")
    tz = t + 0.25 + nw * st + 0.15
    if zf: X.tw(f'tl.from("{S} .cq-zh .ct-l > *", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {tz:.3f});')
    X.tw(f'tl.from("{S} .cq-by", {{opacity:0, x:-30, duration:0.55, ease:"expo.out"}}, {tz + 0.2:.3f});')
    X.tw(f'tl.from("{S} .cq-year", {{opacity:0, x:60, duration:0.9, ease:"expo.out"}}, {t + 0.15:.3f});')
    C.marker(X, f"{S} .cq-o", tz + 0.1, each=0.4)
    C.drift(X, f"{S} .cq-cam", t + 0.6, d - 0.6, s=1.03)


FX = {"cite_quote": cite_quote}
