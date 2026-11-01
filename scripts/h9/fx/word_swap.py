"""句中换词 Word Slot (talkcraft word-slot-cycle; Apple 发布会「It's a ___, a ___, and a ___」; 老虎机式 Rotating
Words 标题模板): one slot inside a sentence rolls through its words like a reel — each roll overshoots and
settles, the slot's width and underline follow the word — and the last word locks in the accent.
mode "replace" is 「不是 A，是 B」: the first word is struck through, then the reel turns to the answer.

Adapts: sentence of any length (one line when it fits at a strong size, else the text before the slot takes its
own line), 2–8 words of different lengths (the slot resizes per word), Latin or Chinese.
p: pre · words [..] · post · mode cycle|replace · hold (seconds on the last word, auto)
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__struct" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__struct", pathlib.Path(__file__).with_name("_struct.py"))
    sys.modules["h9fx__struct"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__struct"])
S = sys.modules["h9fx__struct"]
from h9 import fit

CSS = """
.fx .ws { position:absolute; left:0; top:0; width:100%; height:100%; }
.fx .ws .ws-b { position:absolute; font-family:var(--f-display); font-weight:900; color:var(--fg); line-height:1.25; white-space:nowrap; }
.fx .ws .ws-line { display:block; }
.fx .ws .ws-txt { display:inline-block; vertical-align:top; }
.fx .ws .ws-slot { display:inline-block; vertical-align:top; position:relative; height:1.25em; overflow:hidden; margin:0 .12em; text-align:center; }
.fx .ws .ws-slot .ws-bg { position:absolute; inset:.06em 0; border-radius:.14em; background:color-mix(in srgb, var(--accent) 22%, transparent); }
.fx .ws .ws-reel { position:relative; display:block; z-index:1; }
.fx .ws .ws-reel span { display:block; height:1.25em; white-space:nowrap; }
.fx .ws .ws-reel span.last { color:var(--accent); }
.fx .ws .ws-u { position:absolute; left:0; right:0; bottom:.04em; height:.08em; background:var(--accent); transform-origin:0 50%; }
.fx .ws .ws-x { position:absolute; z-index:2; left:-.05em; right:-.05em; top:52%; height:.1em; background:var(--fg); transform-origin:0 50%; }
"""


def word_swap(X, cid, t, d, p):
    words = [str(w) for w in fit.as_list(p.get("words"))] or ["……"]
    words = words[:8]
    mode = p.get("mode") or "cycle"
    pre, post = fit.as_text(p.get("pre")), fit.as_text(p.get("post"))
    x, y, w, h = S.box(X, p)
    long_w = max(words, key=fit.width)
    pad = 0.36
    one = f"{pre}{long_w}{post}"
    em1 = fit.width(one) + pad
    px = min(S.vm(X, 13 if X.portrait else 12), w * 0.92 / max(em1, 1), h * 0.4 / 1.25)
    two = px < S.vm(X, 7.5) and pre
    if two:
        em2 = max(fit.width(pre), fit.width(long_w) + pad + fit.width(post))
        px = min(S.vm(X, 13 if X.portrait else 12), w * 0.92 / max(em2, 1), h * 0.6 / 2.5)
    px = max(px, S.vm(X, 4))
    X.css("fx-ws", CSS)
    wid = [(fit.width(wd) + pad) * px for wd in words]
    reel = "".join(f'<span class="{"last" if i == len(words) - 1 else ""}">{X.rich(wd)}</span>' for i, wd in enumerate(words))
    slot = (f'<span class="ws-slot" style="width:{wid[0]:.0f}px"><i class="ws-bg"></i><i class="ws-u"></i><span class="ws-reel">{reel}</span>'
            f'{"<i class=ws-x></i>" if mode == "replace" else ""}</span>')
    pre_h = f'<span class="ws-txt ws-pre">{X.rich(pre)}</span>' if pre else ""
    post_h = f'<span class="ws-txt ws-post">{X.rich(post)}</span>' if post else ""
    body = (f'<span class="ws-line">{pre_h}</span><span class="ws-line">{slot}{post_h}</span>' if two else f'<span class="ws-line">{pre_h}{slot}{post_h}</span>')
    lines_w = [fit.width(pre) * px, (fit.width(long_w) + pad + fit.width(post)) * px] if two else [em1 * px]
    bw = max(lines_w); bh = px * 1.25 * (2 if two else 1)
    bx = x + (w - bw) / 2 if not p.get("host") or X.portrait else x + (w * 0.8 - bw) / 2
    by = y + (h - bh) / 2
    _clip(X, cid, t, d, f'<div class="ws"><div class="ws-b" style="left:{bx:.0f}px; top:{by:.0f}px; font-size:{px:.0f}px; text-align:{"left" if two else "left"}">{body}</div></div>', p)
    s = f"#{cid} .ws"
    X.tw(f'tl.from("{s} .ws-pre, {s} .ws-post", {{opacity:0, y:30, filter:"blur(10px)", duration:0.55, ease:"expo.out", stagger:0.1}}, {t + 0.05:.3f});')
    X.tw(f'tl.from("{s} .ws-slot", {{scaleY:0, duration:0.4, ease:"back.out(2)"}}, {t + 0.25:.3f});')
    X.tw(f'tl.set("{s} .ws-u", {{scaleX:0}}, {t:.3f});')
    X.sfx(t + 0.05, "enter")
    n = len(words)
    if mode == "replace" and n >= 2:
        ts, tr = t + max(0.8, d * 0.3), t + max(1.25, d * 0.48)
        X.tw(f'tl.set("{s} .ws-x", {{scaleX:0}}, {t:.3f});')
        X.tw(f'tl.to("{s} .ws-x", {{scaleX:1, duration:0.3, ease:"power4.out"}}, {ts:.3f});')
        X.tw(f'tl.to("{s} .ws-reel span:first-child", {{opacity:0.45, duration:0.2}}, {ts + 0.1:.3f});')
        X.sfx(ts, "slam")
        X.tw(f'tl.to("{s} .ws-x", {{opacity:0, duration:0.15}}, {tr - 0.05:.3f});')
        X.tw(f'tl.to("{s} .ws-reel", {{yPercent:{-100 * (n - 1) / n:.4f}, duration:0.55, ease:"back.out(1.6)"}}, {tr:.3f});')
        X.tw(f'tl.to("{s} .ws-slot", {{width:{wid[-1]:.0f}, duration:0.45, ease:"expo.inOut"}}, {tr:.3f});')
        X.tw(f'tl.to("{s} .ws-u", {{scaleX:1, duration:0.4, ease:"power3.out"}}, {tr + 0.35:.3f});')
        X.sfx(tr, "pop")
        return
    span = max(0.6, d * 0.62 - 0.5)
    step = span / max(n - 1, 1)
    for i in range(1, n):
        ti = t + 0.6 + (i - 1) * step if n > 1 else t + 0.6
        mv = min(0.42, step * 0.85)
        last = i == n - 1
        X.tw(f'tl.to("{s} .ws-reel", {{yPercent:{-100 * i / n:.4f}, duration:{mv + (0.15 if last else 0):.2f}, ease:"{"back.out(1.8)" if last else "back.out(1.2)"}"}}, {ti:.3f});')
        X.tw(f'tl.to("{s} .ws-slot", {{width:{wid[i]:.0f}, duration:{mv:.2f}, ease:"expo.inOut"}}, {ti:.3f});')
        X.sfx(ti, "tick" if not last else "pop")
    tl_ = t + 0.6 + (n - 2) * step + 0.4 if n > 1 else t + 0.6
    X.tw(f'tl.to("{s} .ws-u", {{scaleX:1, duration:0.4, ease:"power3.out"}}, {tl_:.3f});')
    X.tw(f'tl.fromTo("{s} .ws-b", {{scale:1}}, {{keyframes:[{{scale:1.04, duration:0.15}}, {{scale:1, duration:0.35, ease:"back.out(3)"}}], immediateRender:false, transformOrigin:"50% 50%"}}, {tl_:.3f});')


FX = {"word_swap": word_swap}
