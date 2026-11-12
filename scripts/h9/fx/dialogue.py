"""双人对话 / 采访卡 (dialogue · the two-shot of 访谈节目 graphics; VideoHive "Text Messages" 3.8K, Lower Thirds #1 6.3K):
speaker cards face each other; whoever is talking lifts, rings up and shows a live voice meter while the other
dims; their line lands big in the middle with a quote mark in their colour, and the previous lines step back
into a small transcript above it.

p: speakers [str | {name, role, img}] (2–3; first is left) · lines [[who, text] | {who, text, at}] (who = a name or
   0/1/2) · mock (e.g. "示意对话")
Adapts: 2–3 speakers (3 → a row of cards on top), 1–12 lines of 1 glyph to a paragraph (main line fitted ≤4 lines,
transcript ≤1 line each), names / roles of any length.
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


def _speakers(p):
    out = []
    for s in FT.as_list(p.get("speakers")):
        out.append(dict(s) if isinstance(s, dict) else {"name": str(s)})
    return out[:3]


def _lines(p, sp):
    names = [s["name"] for s in sp]
    out = []
    for ln in FT.as_list(p.get("lines")):
        if isinstance(ln, dict): who, text, at = ln.get("who", 0), str(ln.get("text", "")), ln.get("at")
        elif isinstance(ln, (list, tuple)): who, text, at = ln[0], str(ln[1]) if len(ln) > 1 else "", None
        else:
            a, _, b = str(ln).replace(":", "：").partition("："); who, text, at = (a, b, None) if b else (len(out) % 2, str(ln), None)
        if isinstance(who, int) or (isinstance(who, str) and who.isdigit()): k = int(who) % max(1, len(sp))
        elif who in names: k = names.index(who)
        else:
            sp.append({"name": str(who)}); names.append(str(who)); k = len(sp) - 1
        out.append({"k": k, "text": text, "at": at})
    return out[:12]


def dialogue(X, cid, t, d, p):
    U.base(X)
    P = X.portrait
    sp = _speakers(p) or [{"name": "主持人"}, {"name": "嘉宾"}]
    L = _lines(p, sp)
    sp = sp[:3]
    L = [l for l in L if l["k"] < len(sp)] or [{"k": 0, "text": "……", "at": None}]
    m = len(sp)
    x0, y0, x1, y1 = U.area(X, p)
    if P: y0 += 30
    aw, ah = x1 - x0, y1 - y0
    top_row = P or m == 3
    cards = []
    if top_row:
        cw = min(320, (aw - 30 * (m - 1)) / m); chh = 230 if not P else 250
        gx = x0 + (aw - (cw * m + 30 * (m - 1))) / 2
        boxes = [(gx + k * (cw + 30), y0, cw, chh) for k in range(m)]
        qx0, qy0, qw, qh = x0 + (0 if P else aw * 0.08), y0 + chh + 50, aw * (1 if P else 0.84), ah - chh - 60
    else:
        cw, chh = aw * 0.2, min(ah * 0.78, 470)
        boxes = [(x0, y0 + (ah - chh) / 2, cw, chh), (x1 - cw, y0 + (ah - chh) / 2, cw, chh)]
        qx0, qy0, qw, qh = x0 + cw + aw * 0.05, y0 + 20, aw - 2 * cw - aw * 0.1, ah - 40
    for k, s in enumerate(sp):
        bx, by, bw, bh = boxes[k]
        av = min(bw * 0.56, bh * 0.46)
        nf = FT.fit_text(s["name"], bw - 30, 54, 40 if not P else 36, 16, max_lines=1)
        rf = FT.fit_text(str(s.get("role", "")), bw - 30, 60, 22, 12, max_lines=2) if s.get("role") else None
        role = f'<em style="font-size:{rf.px}px">{"<br>".join(X.rich(x) for x in rf.lines)}</em>' if rf else ""
        bars = "".join(f'<i style="height:{h}%"></i>' for h in (40, 75, 55, 90, 45, 70, 35))
        cards.append(f'<div class="dl-c" data-k="{k}" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px; --tone:{U.tone(s["name"])}">'
                     f'{U.avatar(X, s["name"], s.get("img"), style=f"width:{av:.0f}px; height:{av:.0f}px; font-size:{av * 0.42:.0f}px")}'
                     f'<b style="font-size:{nf.px}px">{X.rich(nf.lines[0] if nf.lines else s["name"])}</b>{role}<span class="dl-mtr">{bars}</span><i class="dl-ring"></i></div>')
    main_h = qh * 0.62
    rows = []
    for j, l in enumerate(L):
        f = FT.fit_text(l["text"], qw - 90, main_h - 20, 60 if not P else 54, 22, max_lines=4, lh=1.3)
        tone = U.tone(sp[l["k"]]["name"])
        align = "left" if (top_row or l["k"] == 0) else "right"
        rows.append(f'<div class="dl-l" data-j="{j}" style="left:{qx0:.0f}px; top:{qy0 + qh - main_h:.0f}px; width:{qw:.0f}px; height:{main_h:.0f}px; text-align:{align}; --tone:{tone}">'
                    f'<i class="dl-q" data-layout-allow-overlap>“</i><span style="font-size:{f.px}px">{"<br>".join(X.rich(x) for x in f.lines)}</span>'
                    f'<em>{X.rich(sp[l["k"]]["name"])}</em></div>')
    X.css("fx-dialogue", """
.dl-c { position:absolute; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:10px; border-radius:22px; background:var(--card); color:var(--card-fg);
  box-shadow:0 0 0 2px color-mix(in srgb, var(--card-fg) 10%, transparent), 0 20px 46px rgba(0,0,0,.16); text-align:center; padding:12px; box-sizing:border-box; }
.dl-c b { font-family:var(--f-display, var(--f-body)); font-weight:900; white-space:nowrap; line-height:1.1; }
.dl-c em { font-style:normal; font-family:var(--f-body); color:color-mix(in srgb, var(--card-fg) 58%, transparent); line-height:1.3; }
.dl-ring { position:absolute; inset:-6px; border-radius:26px; border:5px solid var(--tone); opacity:0; }
.dl-mtr { display:flex; align-items:center; gap:5px; height:28px; opacity:0; }
.dl-mtr i { display:block; width:6px; border-radius:3px; background:var(--tone); transform-origin:50% 50%; }
.dl-l { position:absolute; display:flex; flex-direction:column; justify-content:center; gap:10px; opacity:0; transform-origin:0 100%; }
.dl-l .dl-q { font-style:normal; font:900 110px/0.6 var(--f-serif, Georgia, serif); color:var(--tone); height:44px; }
.dl-l span { font-family:var(--f-display, var(--f-body)); font-weight:900; color:var(--fg); line-height:1.3; }
.dl-l em { font-style:normal; font:700 22px var(--f-mono, monospace); letter-spacing:.06em; color:var(--tone); }
""")
    mk = U.mock(X, p, qx0 + qw, qy0, right=True)
    _clip(X, cid, t, d, f'{"".join(cards)}{"".join(rows)}{mk}', p)
    s = f"#{cid}"
    for k in range(m):
        X.tw(f'tl.from("{s} .dl-c[data-k=\'{k}\']", {{y:40, opacity:0, duration:0.45, ease:"expo.out"}}, {t + 0.05 + k * 0.08:.3f});')
    settled = t + 0.52 + (m - 1) * 0.08    # cards finish entering before the first speaker lights up
    X.sfx(t + 0.05, "whoosh_soft")
    end_t = t + d - min(1.6, d * 0.3)
    fit = max(1, int((end_t - t - 0.6) / 0.9) + 1)
    # more lines than the beat can show at ~0.9 s each: the earlier ones are already said (the last of them waits in the transcript)
    skip = len(L) - fit if len(L) > fit and all(l["at"] is None for l in L) else 0
    auto = U.spread(len(L) - skip, t + 0.6, end_t)
    base = []
    fixed = []
    say = []
    for j in range(skip, len(L)):
        base.append(U.when(X, L[j]["at"], t, auto[j - skip]))
        fixed.append(L[j]["at"] is not None)
        say.append(str(L[j].get("text", "")))
    base = U.follow(X, say, t, d, base, fixed, gap=0.5)        # a line pops when the narration says it
    T = [None] * skip
    for j in range(skip, len(L)):
        T.append(max(T[-1] + 0.5 if j > skip else t + 0.4, base[j - skip]))
    lift = main_h * 0.72
    if skip:
        ls = f"{s} .dl-l[data-j=\'{skip - 1}\']"
        X.tw(f'tl.set("{ls}", {{y:{-lift:.0f}, scale:0.5, opacity:0.42}}, {t:.3f});')
        if skip + 1 < len(L): X.tw(f'tl.to("{ls}", {{y:{-lift * 1.55:.0f}, opacity:0, duration:0.4, ease:"power3.inOut"}}, {T[skip + 1]:.3f});')
    for j in range(skip, len(L)):
        l = L[j]
        tj = T[j]; nxt = T[j + 1] if j + 1 < len(L) else t + d
        ls = f"{s} .dl-l[data-j=\'{j}\']"
        X.tw(f'tl.fromTo("{ls}", {{opacity:0, y:30}}, {{opacity:1, y:0, duration:0.45, ease:"expo.out", immediateRender:false}}, {tj:.3f});')
        if j + 1 < len(L):
            X.tw(f'tl.to("{ls}", {{y:{-lift:.0f}, scale:0.5, opacity:0.42, duration:0.45, ease:"power3.inOut"}}, {nxt:.3f});')
            if j + 2 < len(L):
                X.tw(f'tl.to("{ls}", {{y:{-lift * 1.55:.0f}, opacity:0, duration:0.4, ease:"power3.inOut"}}, {T[j + 2]:.3f});')
        ck = f"{s} .dl-c[data-k=\'{l['k']}\']"
        prev = L[j - 1]["k"] if j > skip else None
        if prev != l["k"]:
            for k in range(m):
                on = k == l["k"]
                X.tw(f'tl.to("{s} .dl-c[data-k=\'{k}\']", {{opacity:{1 if on else 0.5}, y:{-10 if on else 0}, scale:{1.04 if on else 0.97}, duration:0.35, ease:"power3.out"}}, {max(tj - 0.05, settled):.3f});')
                X.tw(f'tl.to("{s} .dl-c[data-k=\'{k}\'] .dl-ring, {s} .dl-c[data-k=\'{k}\'] .dl-mtr", {{opacity:{1 if on else 0}, duration:0.25}}, {max(tj - 0.05, settled):.3f});')
        # the meter of the one who talks
        dur = max(0.3, nxt - tj - 0.1)
        reps = max(1, int(dur / 0.36))
        X.tw(f'tl.fromTo("{ck} .dl-mtr i", {{scaleY:0.35}}, {{scaleY:1, duration:0.18, ease:"sine.inOut", repeat:{2 * reps - 1}, yoyo:true, stagger:{{each:0.05, from:"center"}}, immediateRender:false}}, {tj:.3f});')
        X.sfx(tj, "pop")


FX = {"dialogue": dialogue}
