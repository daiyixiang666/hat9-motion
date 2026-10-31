"""指哪说哪 —— annotation marks drawn onto whatever the narration names (Vox annotate / Johnny Harris red pen / 3b1b Indicate).

beat["marks"] = [{"on": ".B", "verb": "circle", "at": "@海报", "label": "廉价感从这来"}]
  on    : selector inside the scene (any element; the mark is attached to it and follows its layout)
  verb  : circle | underline | box | strike | arrow | highlight | indicate
  label : optional note with a leader line, side: top|bottom|left|right
SVG paths use pathLength=1 and stretch to the target, so no measuring is needed; a seeded wobble makes them hand-drawn.
"""
import math

CSS = """
.mk { position:absolute; pointer-events:none; overflow:visible; z-index:20; }
.mk { --p:0; -webkit-mask-image:var(--mkm); mask-image:var(--mkm); }
.mk-c { --mkm:conic-gradient(from -135deg, #000 calc(var(--p) * 1%), transparent 0); }
.mk-u, .mk-s, .mk-b { --mkm:linear-gradient(90deg, #000 calc(var(--p) * 1% - 2%), transparent calc(var(--p) * 1% + 2%)); }
.mk-a { --mkm:linear-gradient(225deg, #000 calc(var(--p) * 1% - 2%), transparent calc(var(--p) * 1% + 2%)); }
.mk path { fill:none; stroke:var(--mark, var(--accent)); stroke-linecap:round; stroke-linejoin:round; vector-effect:non-scaling-stroke; }
.mk-c { left:-8%; top:-14%; width:116%; height:128%; } .mk-u { left:-2%; top:88%; width:104%; height:24%; }
.mk-b { left:-4%; top:-8%; width:108%; height:116%; } .mk-s { left:-3%; top:42%; width:106%; height:16%; }
.mk-a { left:100%; top:-70%; width:60%; height:120%; }
.mk-h { left:-2%; right:-2%; top:52%; height:42%; background:var(--hl, rgba(255,226,0,.6)); mix-blend-mode:multiply; transform-origin:0 50%; }
.mk-l { position:absolute; white-space:nowrap; font-family:var(--f-mark, var(--f-mono, var(--f-body))); font-size:var(--mark-size, 28px); font-weight:700;
  color:var(--mark-fg, var(--mark, var(--accent))); pointer-events:none; z-index:21; }
.mk-l.top { left:0; bottom:calc(100% + 26px); } .mk-l.bottom { left:0; top:calc(100% + 26px); }
.mk-l.right { left:calc(100% + 30px); top:0; } .mk-l.left { right:calc(100% + 30px); top:0; }
"""


def wobble(pts, rnd, amt):
    return [(x + rnd.uniform(-amt, amt), y + rnd.uniform(-amt, amt)) for x, y in pts]


def path(verb, rnd):
    if verb == "circle":   # loop that overshoots its start, like a real pen
        pts = [(50 + 48 * math.cos(-2.3 + 2 * math.pi * i / 40 * 1.1), 50 + 46 * math.sin(-2.3 + 2 * math.pi * i / 40 * 1.1)) for i in range(41)]
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in wobble(pts, rnd, 1.2))
    if verb == "underline":
        return f"M0,{40 + rnd.uniform(-8, 8):.0f} C30,{60 + rnd.uniform(-10, 10):.0f} 70,{30 + rnd.uniform(-10, 10):.0f} 100,{52 + rnd.uniform(-8, 8):.0f}"
    if verb == "box":
        p = wobble([(0, 2), (100, 0), (99, 100), (1, 98), (2, 4)], rnd, 1.0)
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p)
    if verb == "strike":
        return f"M0,{55 + rnd.uniform(-10, 10):.0f} L100,{45 + rnd.uniform(-10, 10):.0f}"
    if verb == "arrow":
        return "M95,5 C70,20 40,45 6,82 M6,82 L26,78 M6,82 L10,62"
    return ""


CLS = {"circle": "mk-c", "underline": "mk-u", "box": "mk-b", "strike": "mk-s", "arrow": "mk-a"}


def build(X, cid, b):
    """returns hidden HTML for the marks (moved into their targets at load) and queues their tweens."""
    marks = b.get("marks") or []
    if not marks: return ""
    X.css("marks", CSS)
    html, moves = [], []
    for k, m in enumerate(marks):
        v = m.get("verb", "circle")
        mid = f"{cid}-m{k}"
        t = X.T(m.get("at"), X.beat["t"]) or X.beat["t"] + 0.6
        if v == "highlight":
            html.append(f'<i id="{mid}" class="mk mk-h"></i>')
            X.tw(f'tl.fromTo("#{mid}", {{scaleX:0}}, {{scaleX:1, duration:0.38, ease:"power2.out"}}, {t:.3f});')
        elif v == "indicate":   # 3b1b Indicate: scale up, tint, settle
            X.tw(f'tl.to("#{cid} {m["on"]}", {{scale:1.12, color:"var(--accent)", duration:0.25, ease:"power2.out", yoyo:true, repeat:1}}, {t:.3f});')
            X.sfx(t, "mark"); continue
        else:
            sw = m.get("width", X.S.get("mark_width", 6))
            html.append(f'<svg id="{mid}" class="mk {CLS[v]}" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="{path(v, X.rand)}" stroke-width="{sw}"/></svg>')
            X.tw(f'tl.fromTo("#{mid}", {{"--p":0}}, {{"--p":104, duration:{m.get("dur", 0.45)}, ease:"power2.inOut"}}, {t:.3f});')
        moves.append((mid, m["on"]))
        X.sfx(t, "mark")
        if m.get("label"):
            html.append(f'<div id="{mid}l" class="mk-l {m.get("side", "top")}">{X.rich(m["label"])}</div>')
            moves.append((f"{mid}l", m["on"]))
            X.enter(f"#{mid}l", t + 0.3, "accent", verb="fade", dur=0.3)
    # attach each mark to its target (pure DOM move, no measuring -> deterministic)
    js = ";".join(f'(()=>{{const t=document.querySelector("#{cid} {on}"), e=document.getElementById("{e}"); if(t&&e){{ if(getComputedStyle(t).position==="static") t.style.position="relative"; t.appendChild(e); }}}})()'
                  for e, on in moves)
    X.tws.insert(0, js + ";")
    return "".join(html)
