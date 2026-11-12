"""梗图舞台 (one picture per sentence — the reaction-image rhythm of 口播 commentary): each picture slams onto the
stage like a sticker on its word, with a little camera jolt; earlier ones stay in the pile behind (or get swapped out),
each with an optional impact-style caption.

p: items (paths, or {src, caption, at}) · at (list of "@词" / seconds, one per item; else evenly spaced) ·
   mode ("pile" | "swap") · captions (list, if not given per item) · title
Adapts: 1–12 pictures of any aspect (each keeps its own shape, sized to the box); captions 0 to ~2 lines each;
16:9 and 9:16. Use pictures you have the rights to.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def meme_stage(X, cid, t, d, p):
    raw = fit.as_list(p.get("items") or p.get("images"))
    caps = fit.as_list(p.get("captions"))
    items = []
    for i, it in enumerate(raw):
        if isinstance(it, dict): items.append({"src": it.get("src") or it.get("image"), "cap": it.get("caption", caps[i] if i < len(caps) else ""), "at": it.get("at")})
        else: items.append({"src": it, "cap": caps[i] if i < len(caps) else "", "at": None})
    if not items: raise SystemExit("meme_stage needs `items`")
    n = len(items)
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    mode = p.get("mode", "pile")
    at = [it["at"] for it in items] if any(it["at"] for it in items) else p.get("at")
    say = []
    for it in items:
        say.append(str(it["cap"] or ""))
    ts = D.times(X, {"at": at}, t, d, n, key="at", lead=0.15, tail=min(0.9, d * 0.2), texts=say)
    r = X.rand
    cards = []
    for i, it in enumerate(items):
        ar = fit.aspect(X, it["src"], 1.4)
        has_cap = bool(it["cap"])
        mw, mh = bw * (0.62 if not P else 0.86), bh * (0.66 if has_cap else 0.78)
        w = min(mw, mh * ar); h = w / ar
        cx = x0 + bw / 2 + (r.uniform(-1, 1) * bw * (0.08 if mode == "pile" and n > 1 else 0))
        cy = y0 + bh * (0.44 if has_cap else 0.5) + (r.uniform(-1, 1) * bh * (0.04 if mode == "pile" and n > 1 else 0))
        rot = r.choice([-1, 1]) * r.uniform(1.5, 5.5)
        cap = ""; W, H = w, h
        if has_cap:      # the card box holds picture + caption, so the caption never hangs outside its own box
            cf = D.C.fitted(X, it["cap"], min(bw * 0.9, max(w, bw * 0.6)), 130, 64 if not P else 58, 30, max_lines=2, lh=1.08)
            W = max(w, cf.em * cf.px * 1.12 + 16); H = h + 14 + cf.n * cf.px * 1.08 + cf.px * 0.2
            cap = f'<div class="ms-cap" style="top:{h + 14:.1f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>'
            X.used_text.update(it["cap"])
        cards.append(f'<div class="ms-c" data-k="{i}" style="left:{cx - W / 2:.1f}px; top:{cy - h / 2:.1f}px; width:{W:.1f}px; height:{H:.1f}px; --r:{rot:.1f}deg">'
                     f'<div class="ms-pic" style="left:{(W - w) / 2:.1f}px; width:{w:.1f}px; height:{h:.1f}px"><img src="{X.asset(it["src"])}" alt=""></div>{cap}</div>')
    title = fit.as_text(p.get("title"))
    head = ""
    if title:
        tf = D.C.fitted(X, title, bw * 0.8, 80, 44, 24, max_lines=1)
        head = f'<div class="d2-ttl ms-ttl" style="left:{x0}px; top:{y0}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>'
        X.used_text.update(title)
    X.css("fx-d2", D.CSS)
    X.css("fx-meme", """
.ms-spot { position:absolute; inset:0; background:radial-gradient(ellipse 55% 50% at 50% 48%, color-mix(in srgb, var(--fg) 8%, transparent), transparent 70%); }
.ms-c { position:absolute; transform:rotate(var(--r)); opacity:0; }
.ms-pic { position:absolute; top:0; box-sizing:border-box; background:#fbfaf6; padding:10px; box-shadow:0 2px 0 rgba(0,0,0,.08), 0 22px 50px rgba(0,0,0,.32); border-radius:6px; }
.ms-pic img { width:100%; height:100%; object-fit:cover; display:block; border-radius:2px; }
.ms-cap { position:absolute; left:0; right:0; text-align:center;
  font-family:var(--f-display); font-weight:900; line-height:1.08; color:#fff; -webkit-text-stroke:.09em #111; paint-order:stroke fill; letter-spacing:.01em; }
""")
    _clip(X, cid, t, d, f'<div class="d2 ms"><i class="ms-spot"></i><div class="ms-stage">{"".join(cards)}</div>{head}</div>', p)
    S = f"#{cid}"
    if title: X.tw(f'tl.from("{S} .ms-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
    for i, tt in enumerate(ts):
        sel = f"{S} .ms-c[data-k='{i}']"
        X.tw(f'tl.fromTo("{sel}", {{opacity:0, scale:1.45, rotation:"+=8"}}, {{opacity:1, scale:1, rotation:"-=8", duration:0.32, ease:"back.out(2.2)"}}, {max(t, tt - 0.12):.3f});')
        X.tw(f'tl.set("{S} .ms-stage", {{x:{r.choice([-10, 10])}, y:{r.choice([-6, 6])}}}, {tt + 0.05:.3f});')
        X.tw(f'tl.to("{S} .ms-stage", {{x:0, y:0, duration:0.12, ease:"steps(2)"}}, {tt + 0.05:.3f});')
        X.sfx(tt, "slam" if i % 2 == 0 else "pop")
        if i > 0:
            prev = f"{S} .ms-c[data-k='{i - 1}']"
            if mode == "swap": X.tw(f'tl.to("{prev}", {{opacity:0, scale:0.9, duration:0.18, ease:"power2.in"}}, {max(t, tt - 0.12):.3f});')
            else:
                X.tw(f'tl.to("{prev}", {{scale:0.92, filter:"brightness(.82)", duration:0.3, ease:"power2.out"}}, {tt:.3f});')
                X.tw(f'tl.to("{prev} .ms-cap", {{opacity:0, duration:0.15}}, {max(t, tt - 0.12):.3f});')
    last = ts[-1] + 0.3
    if t + d - last > 0.3:
        X.tw(f'tl.to("{S} .ms-c[data-k=\'{n - 1}\']", {{scale:1.04, duration:{t + d - last:.2f}, ease:"none"}}, {last:.3f});')


FX = {"meme_stage": meme_stage}
