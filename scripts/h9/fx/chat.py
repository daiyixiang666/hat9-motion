"""AI 对话界面 (#13 UI / Social Mockups — Envato Elements「Elements」Popular 第 1 名是手机通知，Text Messages 3.8K):
the question types into the input, sends up as a bubble, three dots think on twos, the answer streams in word
by word and one phrase gets a marker sweep. No brand chrome — a neutral assistant window.

Adapts: one exchange (q / a) or a conversation of 2–6 messages ("turns": [["user"|"ai", text], ...]); message
lengths from a word to a paragraph — the type size is solved so every message fits the window, older messages
scroll up as new ones arrive. p: q · a · hl (phrase to mark, in the last AI message) · turns · title · placeholder
"""
from h9.aefx import _clip
from h9.core import words
import importlib.util, pathlib, sys
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


def _height(msgs, size, bw):
    """vmin height of the message column at font size `size` (bubble width bw vmin)."""
    h = 0.0
    for role, txt in msgs:
        per_line = max(1.0, (bw - (5.2 if role == "user" else 7)) / size)
        lines = max(1, -(-int(F.em(txt) + 0.999) // int(per_line)))
        h += lines * size * 1.5 + (3.2 if role == "user" else 1.4) + 2.2
    return h


def chat(X, cid, t, d, p):
    msgs = [(r, str(x)) for r, x in p["turns"]] if p.get("turns") else [("user", p["q"]), ("ai", p["a"])]
    hl = p.get("hl", "")
    Wv, Hv = F.frame_vmin(X)
    cw = min(100.0, Wv * 0.9)
    chh = min(84.0 if X.portrait else 62.0, Hv * (0.40 if X.portrait else 0.62))
    msgs_h = chh - 6.4 - 12.0 - 3
    bw = cw * 0.8 - 6
    size = 3.7
    while size > 2.0 and _height(msgs, size, bw) > msgs_h: size -= 0.1
    overflow = _height(msgs, size, bw) > msgs_h        # still too tall: older messages scroll away
    X.css("fx-chat", """
.fx .cw { position:relative; background:var(--card); color:var(--card-fg); border-radius:2.2vmin;
  box-shadow:0 0 0 .25vmin color-mix(in srgb, var(--card-fg) 14%, transparent), 0 4vmin 10vmin rgba(0,0,0,.28); overflow:hidden; display:flex; flex-direction:column; }
#root.v .fx .cw { margin-top:-14vmin; }
.fx .cw .bar { flex:none; height:6.4vmin; display:flex; align-items:center; gap:1vmin; padding:0 2.4vmin; border-bottom:.2vmin solid color-mix(in srgb, var(--card-fg) 10%, transparent); }
.fx .cw .bar i { width:1.3vmin; height:1.3vmin; border-radius:50%; background:color-mix(in srgb, var(--card-fg) 22%, transparent); }
.fx .cw .bar b { margin-left:1.4vmin; font:700 2.1vmin var(--f-body); opacity:.8; }
.fx .cw .msgv { flex:1; overflow:hidden; position:relative; }
.fx .cw .msgs { position:absolute; left:0; right:0; bottom:0; padding:3vmin 3vmin 1vmin; display:flex; flex-direction:column; gap:2.2vmin; }
.fx .cw .msgs.top { top:0; bottom:auto; }
.fx .cw .u { align-self:flex-end; max-width:80%; background:var(--accent); color:var(--bg); font-family:var(--f-body); font-weight:600; line-height:1.45; padding:1.4vmin 2.6vmin; border-radius:2.4vmin 2.4vmin .6vmin 2.4vmin; transform-origin:100% 100%; }
.fx .cw .ai { align-self:flex-start; display:flex; gap:1.6vmin; max-width:88%; }
.fx .cw .av { flex:none; width:5vmin; height:5vmin; border-radius:50%; background:var(--card-fg); color:var(--card); display:grid; place-items:center; font:900 2.2vmin var(--f-mono, monospace); }
.fx .cw .ab { font-family:var(--f-body); font-weight:500; line-height:1.5; padding-top:.4vmin; }
.fx .cw .ab .w { display:inline; } .fx .cw .ab .hlm { position:relative; display:inline-block; white-space:nowrap; font-weight:800; z-index:0; isolation:isolate; }
.fx .cw .ab .hlm::before { content:''; position:absolute; left:-.1em; right:-.1em; bottom:.05em; height:.45em; background:#f6ce3a; z-index:-1; transform-origin:0 50%; transform:scaleX(var(--m, 0)); }
.fx .cw .dots { display:flex; gap:.9vmin; padding:1.6vmin 0 0; } .fx .cw .dots i { width:1.3vmin; height:1.3vmin; border-radius:50%; background:color-mix(in srgb, var(--card-fg) 45%, transparent); }
.fx .cw .in { flex:none; margin:2vmin 3vmin 3vmin; height:7.2vmin; border-radius:3.6vmin; border:.25vmin solid color-mix(in srgb, var(--card-fg) 18%, transparent); display:flex; align-items:center; padding:0 2.6vmin; font:500 2.8vmin var(--f-body); white-space:nowrap; overflow:hidden; }
.fx .cw .in .ty .c { opacity:1; } .fx .cw .in .cr { flex:none; width:.25vmin; height:3.6vmin; background:var(--accent); margin-left:.3vmin; }
.fx .cw .in .ph { opacity:.35; } .fx .cw .in .ty { overflow:hidden; text-overflow:clip; }
.fx .cw .snd { margin-left:auto; flex:none; width:4.6vmin; height:4.6vmin; border-radius:50%; background:var(--card-fg); color:var(--card); display:grid; place-items:center; font:900 2.4vmin var(--f-body); }
""")
    last_ai = max((i for i, (r, _) in enumerate(msgs) if r != "user"), default=-1)
    first_user = next((i for i, (r, _) in enumerate(msgs) if r == "user"), -1)
    ws = lambda s: "".join(f'<span class="w">{X.rich(x)}</span>' for x in words(s))
    body = []
    for i, (r, txt) in enumerate(msgs):
        if r == "user":
            body.append(f'<div class="u" data-i="{i}" style="font-size:{size:.2f}vmin">{X.rich(txt)}</div>')
        else:
            if i == last_ai and hl and hl in txt:
                a, _, b = txt.partition(hl); ab = ws(a) + f'<span class="w hlm">{X.rich(hl)}</span>' + ws(b)
            else: ab = ws(txt)
            dots = '<div class="dots"><i></i><i></i><i></i></div>' if i == last_ai else ""
            body.append(f'<div class="ai" data-i="{i}"><div class="av">AI</div><div>{dots}<div class="ab" style="font-size:{size:.2f}vmin">{ab}</div></div></div>')
    q0 = msgs[first_user][1] if first_user >= 0 else ""
    ty = "".join(f'<i class="c">{X.rich(ch)}</i>' if ch.strip() else " " for ch in q0[:40])
    inner = (f'<div class="cw" style="width:{cw:.1f}vmin; height:{chh:.1f}vmin"><div class="bar"><i></i><i></i><i></i><b>{X.rich(p.get("title", "AI 助手"))}</b></div>'
             f'<div class="msgv"><div class="msgs{"" if overflow else " top"}">{"".join(body)}</div></div>'
             f'<div class="in"><span class="ph">{X.rich(p.get("placeholder", "问点什么…"))}</span><span class="ty">{ty}</span><i class="cr"></i><span class="snd">↑</span></div></div>')
    X.used_text.update("AI↑")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .cw", {{y:50, opacity:0, scale:0.97, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    # first user message types into the input, the rest just arrive
    nq = len(q0[:40]); tq = min(0.045, 0.8 / max(nq, 1))
    cur = t + 0.3
    X.tw(f'tl.fromTo("{s} .in .cr", {{opacity:1}}, {{opacity:0, duration:0.01, repeat:{int(d / 0.5)}, yoyo:true, repeatDelay:0.25, ease:"steps(1)"}}, {t + 0.3:.3f});')
    if first_user >= 0:
        X.tw(f'tl.set("{s} .in .ph", {{opacity:0}}, {cur:.3f});')
        X.tw(f'tl.from("{s} .in .ty .c", {{opacity:0, duration:0.01, stagger:{tq:.3f}, ease:"none"}}, {cur:.3f});')
        cur += nq * tq + 0.15
        X.tw(f'tl.set("{s} .in .ty", {{opacity:0}}, {cur:.3f});')
        X.tw(f'tl.to("{s} .snd", {{keyframes:[{{scale:0.8, duration:0.08}}, {{scale:1, duration:0.2, ease:"back.out(3)"}}]}}, {cur - 0.08:.3f});')
    budget = max(0.6, t + d - 0.5 - cur)
    weights = [max(1.0, F.em(x) / 8) if r != "user" else 0.6 for r, x in msgs]
    unit = budget / sum(weights)
    for i, (r, txt) in enumerate(msgs):
        X.tw(f'tl.set("{s} .msgs > [data-i=\'{i}\']", {{display:"none"}}, {t:.3f});')
        X.tw(f'tl.set("{s} .msgs > [data-i=\'{i}\']", {{display:"{"block" if r == "user" else "flex"}"}}, {cur:.3f});')
        if r == "user":
            X.tw(f'tl.from("{s} .msgs > [data-i=\'{i}\']", {{y:50, scale:0.6, opacity:0, duration:0.4, ease:"back.out(1.8)"}}, {cur:.3f});')
            X.sfx(cur, "pop")
        else:
            X.tw(f'tl.from("{s} .msgs > [data-i=\'{i}\']", {{opacity:0, y:20, duration:0.3, ease:"expo.out"}}, {cur:.3f});')
            if i == last_ai:
                X.tw(f'tl.fromTo("{s} .dots i", {{y:0}}, {{y:"-0.8vmin", duration:0.16, repeat:3, yoyo:true, ease:"steps(2)", stagger:0.08}}, {cur:.3f});')
                X.tw(f'tl.set("{s} .dots", {{display:"none"}}, {cur + 0.5:.3f});')
                ta = cur + 0.5
            else: ta = cur + 0.1
            nw = max(1, len(words(txt)))
            stg = min(0.06, max(0.012, (unit * weights[i] - 0.4) / nw))
            X.tw(f'tl.from("{s} .msgs > [data-i=\'{i}\'] .ab .w", {{opacity:0, duration:0.1, stagger:{stg:.3f}, ease:"none"}}, {ta:.3f});')
            X.sfx(ta, "type")
            if i == last_ai and hl and hl in txt:
                X.tw(f'tl.to("{s} .ab .hlm", {{"--m":1, duration:0.35, ease:"power3.out"}}, {ta + nw * stg + 0.1:.3f});')
        cur += unit * weights[i]


FX = {"chat": chat}
