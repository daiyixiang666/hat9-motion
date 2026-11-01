"""引用社交帖子 (post card — "他发了一条推 / 微博"): a platform-neutral post card drops onto a feed of ghost cards,
the text types in, time and counts tick up, an optional translation lifts in under the card; a big outlined date
holds the background and an optional stat sits beside it. No platform chrome or logos.

p: name · handle · avatar (image, optional → monogram) · verified · text · hl · time · counts ({replies, reposts,
   likes, views} — any subset; omit when unknown) · image (attached media) · zh (translation) · stat ({value, unit, label})
Adapts: a few words to a long post (auto size ≤ 6 lines), with or without media (any aspect), 0–4 counts (big numbers
→ 万/K), Chinese or Latin; 16:9 = card + stat side by side, 9:16 = stacked.
"""
import importlib.util, pathlib, re, sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


C = _load("_cite")
ICON = {"replies": "M4 5h16v10H9l-5 4z", "reposts": "M7 7h9l-2-2M17 17H8l2 2M7 7v6M17 17v-6",
        "likes": "M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z", "views": "M3 12s3.5-6 9-6 9 6 9 6-3.5 6-9 6-9-6-9-6z M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z"}


def cite_post(X, cid, t, d, p):
    x0, y0, x1, y1 = C.area(X, p)
    P = X.portrait
    stat = p.get("stat")
    zh = p.get("zh")
    if P:
        cw = x1 - x0; cx = x0
    else:
        cw = round((x1 - x0) * (0.56 if stat else 0.66)); cx = x0 + (40 if stat else ((x1 - x0) - cw) // 2)
    pad = 36
    txt = str(p.get("text", ""))
    if p.get("hl") and p["hl"] in txt and "*" not in txt: txt = txt.replace(p["hl"], f"*{p['hl']}*", 1)
    media = p.get("image")
    counts = [(k, p["counts"][k]) for k in ("replies", "reposts", "likes", "views") if isinstance(p.get("counts"), dict) and k in p["counts"]]
    avail_h = (y1 - y0) * (0.62 if P else 0.82) - (150 if zh else 0)
    med_h = round(min(avail_h * 0.42, (cw - 2 * pad) / max(fit.aspect(X, media), 0.5))) if media else 0
    tf = C.fitted(X, txt, cw - 2 * pad, max(80, avail_h - 96 - med_h - 60 - (56 if counts else 0)), 44 if not P else 42, 22, max_lines=6, lh=1.35)
    ch = round(pad * 2 + 80 + tf.n * tf.px * 1.35 + (med_h + 18 if media else 0) + 44 + (60 if counts else 0))
    zf = C.fitted(X, zh, cw, 130, 36 if not P else 36, 20, max_lines=3, lh=1.3) if zh else None
    total_h = ch + (zf.n * zf.px * 1.3 + 30 if zf else 0)
    stat_h = 230 if stat and P else 0
    cy = y0 + max(20, (y1 - y0 - total_h - stat_h - (120 if P else 0)) / 2)
    name = str(p.get("name", "")); handle = str(p.get("handle", ""))
    X.used_text.update(name + handle + str(p.get("time", "")) + "0123456789.,万亿KM")
    toks = lambda line: "".join(f'<i class="cs-w">{X.rich(w)}</i>' if w.strip() else " " for w in re.findall(r"\*[^*]+\*|[A-Za-z0-9’'.,;:!?@#\-]+|\s+|.", line))
    body = "".join(f'<span class="cs-l">{toks(l)}</span>' for l in tf.lines)
    mh = ""
    if media:
        m, _ = fit.media(X, cid, "csm", media, t, d, "cs-mimg", fill="cover", box_ar=(cw - 2 * pad) / max(med_h, 1))
        mh = f'<div class="cs-media" style="height:{med_h}px">{m}</div>'
    cnt = "".join(f'<span class="cs-k"><svg viewBox="0 0 24 24"><path d="{ICON[k]}"/></svg><b data-v="{float(v)}">0</b></span>' for k, v in counts)
    ver = '<svg class="cs-ver" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M7.5 12.5l3 3 6-6.5"/></svg>' if p.get("verified") else ""
    card = (f'<div class="cs-card" style="left:{cx}px; top:{cy:.0f}px; width:{cw}px; height:{ch}px; padding:{pad}px">'
            f'<div class="cs-head">{C.mono_html(X, name or handle, 72, p.get("avatar"))}<div><b>{X.rich(name)}{ver}</b><span>{X.rich(handle)}</span></div></div>'
            f'<div class="cs-text" style="font-size:{tf.px}px">{body}</div>{mh}'
            f'<div class="cs-time">{X.rich(p.get("time", ""))}</div>'
            + (f'<div class="cs-counts">{cnt}</div>' if counts else "") + '</div>')
    ghosts = "".join(f'<div class="cs-ghost" style="left:{cx + dx}px; top:{cy + dy:.0f}px; width:{cw}px; height:{ch}px; transform:rotate({r}deg)"></div>'
                     for dx, dy, r in ((-26, 30, -4), (30, -24, 3.5)))
    tr = f'<div class="cs-zh" style="left:{cx}px; top:{cy + ch + 28:.0f}px; width:{cw}px; font-size:{zf.px}px">{C.lines(X, zf)}</div>' if zf else ""
    date = re.sub(r"[-/]", ".", str(p.get("date") or (re.search(r"\d{4}[-./]\d{1,2}[-./]\d{1,2}", str(p.get("time", ""))) or [""])[0]))
    X.used_text.update(date)
    bigdate = f'<div class="cs-date" data-layout-allow-overlap style="font-size:{(x1 - x0) * (0.13 if not P else 0.16):.0f}px; {"right:" + str(X.W - x1) + "px; bottom:" + str(X.H - y1 + 6) + "px" if not P else "left:" + str(x0) + "px; bottom:" + str(X.H - y1 + 10) + "px"}">{X.rich(date)}</div>' if date else ""
    side = ""
    if stat:
        X.used_text.update(str(stat.get("value", "")) + str(stat.get("unit", "")) + str(stat.get("label", "")))
        if P:
            sx, sy_, sw = x0, cy + total_h + 40, x1 - x0
        else:
            sx, sy_, sw = cx + cw + 70, y0 + (y1 - y0) * 0.22, x1 - (cx + cw + 70)
        lf = C.fitted(X, stat.get("label", ""), sw, 110, 34, 20, max_lines=3, lh=1.3)
        side = (f'<div class="cs-stat" style="left:{sx}px; top:{sy_:.0f}px; width:{sw}px"><div><b class="cs-sv">{X.rich(stat.get("value", ""))}</b><em>{X.rich(stat.get("unit", ""))}</em></div>'
                f'<div class="cs-sl" style="font-size:{lf.px}px">{C.lines(X, lf)}</div></div>')
    X.css("fx-cite-base", C.CSS)
    X.css("fx-cite-post", """
.cs-card, .cs-ghost { position:absolute; box-sizing:border-box; border-radius:22px; }
.cs-card { background:var(--card); color:var(--card-fg); display:flex; flex-direction:column; gap:18px; box-shadow:0 26px 70px rgba(0,0,0,.28), 0 0 0 1.5px color-mix(in srgb, var(--card-fg) 10%, transparent); }
.cs-ghost { background:color-mix(in srgb, var(--card) 70%, var(--bg)); box-shadow:0 10px 30px rgba(0,0,0,.12); opacity:.55; }
.cs-head { display:flex; align-items:center; gap:18px; }
.cs-head b { display:flex; align-items:center; gap:8px; font:900 30px var(--f-body); } .cs-head span { display:block; font:500 22px var(--f-mono, monospace); opacity:.55; }
.cs-ver { width:26px; height:26px; } .cs-ver circle { fill:#2b59c3; } .cs-ver path { fill:none; stroke:#fff; stroke-width:2.6; stroke-linecap:round; stroke-linejoin:round; }
.cs-text { font-family:var(--f-body); font-weight:600; line-height:1.35; } .cs-l { display:block; white-space:nowrap; } .cs-w { font-style:normal; display:inline-block; white-space:pre; }
.cs-media { position:relative; border-radius:14px; overflow:hidden; } .cs-media .cs-mimg { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.cs-time { font:600 20px var(--f-mono, monospace); opacity:.55; letter-spacing:.03em; }
.cs-counts { display:flex; gap:34px; border-top:1.5px solid color-mix(in srgb, var(--card-fg) 12%, transparent); padding-top:14px; }
.cs-k { display:flex; align-items:center; gap:10px; font:800 24px var(--f-num, var(--f-body)); }
.cs-k svg { width:26px; height:26px; fill:none; stroke:currentColor; stroke-width:2; stroke-linejoin:round; stroke-linecap:round; opacity:.7; }
.cs-zh { position:absolute; font-family:var(--f-body); font-weight:800; line-height:1.3; color:var(--fg); border-left:6px solid var(--accent); padding-left:20px; }
.cs-zh .ct-l { overflow:hidden; }
.cs-date { position:absolute; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.8; letter-spacing:-.03em; color:color-mix(in srgb, var(--fg) 7%, transparent); -webkit-text-stroke:2.5px color-mix(in srgb, var(--fg) 26%, transparent); white-space:nowrap; }
.cs-stat { position:absolute; display:flex; flex-direction:column; gap:12px; color:var(--fg); }
.cs-stat b { font:900 180px var(--f-num, var(--f-display)); line-height:.85; color:var(--accent); letter-spacing:-.03em; } .cs-stat em { font-style:normal; font:900 56px var(--f-body); margin-left:10px; }
.cs-sl { font-family:var(--f-body); font-weight:700; line-height:1.3; color:var(--muted); }
#root.v .cs-stat b { font-size:140px; }
""")
    _clip(X, cid, t, d, f'<div class="ct-root"><div class="cs-cam">{bigdate}{ghosts}{card}{tr}{side}</div></div>', p)
    X.css("fx-cite-post-cam", ".cs-cam { position:absolute; inset:0; }")
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .cs-date", {{opacity:0, x:60, duration:1.0, ease:"expo.out"}}, {t:.3f});')
    X.tw(f'tl.from("{S} .cs-ghost", {{opacity:0, y:50, duration:0.7, ease:"expo.out", stagger:0.08}}, {t + 0.05:.3f});')
    X.tw(f'tl.fromTo("{S} .cs-card", {{y:-80, rotation:-4, opacity:0}}, {{y:0, rotation:0, opacity:1, duration:0.7, ease:"back.out(1.4)"}}, {t + 0.15:.3f});')
    X.sfx(t + 0.15, "pop")
    nw = sum(len(re.findall(r"\*[^*]+\*|[A-Za-z0-9’'.,;:!?@#\-]+|\S", l)) for l in tf.lines)
    st = max(0.025, min(0.09, 1.2 / max(nw, 1)))
    X.tw(f'tl.from("{S} .cs-w", {{opacity:0, duration:0.01, stagger:{st:.3f}}}, {t + 0.55:.3f});')
    X.sfx(t + 0.55, "type")
    te = t + 0.55 + nw * st
    if media: X.tw(f'tl.from("{S} .cs-media", {{opacity:0, scale:0.95, duration:0.5, ease:"power3.out"}}, {te:.3f});')
    X.tw(f'tl.from("{S} .cs-time, {S} .cs-counts", {{opacity:0, y:10, duration:0.4, stagger:0.1}}, {te + 0.05:.3f});')
    for i, (k, v) in enumerate(counts):
        mode = "zh" if re.search(r"[一-鿿]", txt + str(p.get("zh", ""))) else "int"
        C.counter(X, f"{S} .cs-k:nth-child({i + 1}) b", te + 0.1, 0, float(v), dur=1.0, fmt=mode)
    C.marker(X, f"{S} .cs-text", te + 0.15, each=0.35)
    if zf: X.tw(f'tl.from("{S} .cs-zh .ct-l > *", {{yPercent:110, duration:0.6, ease:"expo.out", stagger:0.08}}, {te + 0.25:.3f});')
    if stat:
        X.tw(f'tl.from("{S} .cs-stat", {{opacity:0, x:40, duration:0.6, ease:"expo.out"}}, {t + 0.6:.3f});')
        try: C.counter(X, f"{S} .cs-sv", t + 0.65, 0, float(stat["value"]), dur=0.9)
        except (TypeError, ValueError): pass
    C.drift(X, f"{S} .cs-cam", t + 0.8, d - 0.8, s=1.025)


FX = {"cite_post": cite_post}
