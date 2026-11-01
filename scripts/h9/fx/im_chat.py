"""双人聊天记录 (IM chat screenshot — 微信式聊天截图是口播里最常见的"证据"之一; Envato "Text Messages" /
"Chat Mockup" packs, 3.8K+ sales): a neutral messenger window (no app branding). Bubbles spring out of their
side's corner in order, the header flips to 「对方正在输入…」 before each incoming message, time stamps and
recalls sit centred, a voice message shows its length, the last sent message can turn 已读; the conversation
scrolls once it outgrows the window.

Adapts: 2–30 messages; each a word to a paragraph (≤5 lines, then ellipsis); group chats show names; image
messages keep their aspect. Type size is solved from the count.
p: messages [[who, text] | {from|who, text, time, voice (秒), recall, img, name}] (who = 我 / me / right for
   the sender) · title (contact) · read (last sent message turns 已读) · mock · t_end (when the last arrives)
"""
from h9.aefx import _clip
from h9 import fit as FT
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")
ME = {"我", "me", "right", "r", "self", "user", "自己"}
THEM = {"对方", "them", "left", "l", "other", "ta", "他", "她"}
WAVE = '<svg viewBox="0 0 24 24"><path d="M6 12h.01M10 8.5a5 5 0 0 1 0 7M14 5a10 10 0 0 1 0 14"/></svg>'


def _norm(v):
    out = []
    for m in FT.as_list(v):
        if isinstance(m, dict):
            who = str(m.get("from", m.get("who", m.get("role", "")))).strip()
            out.append({**m, "me": who.lower() in ME or who in ME, "name": m.get("name", "" if (who.lower() in ME or who in ME or who.lower() in THEM or who in THEM) else who)})
        elif isinstance(m, (list, tuple)):
            who = str(m[0]).strip(); out.append({"me": who.lower() in ME or who in ME, "name": "" if (who in ME or who in THEM or who.lower() in THEM) else who, "text": m[1] if len(m) > 1 else ""})
        else:
            out.append({"me": False, "name": "", "text": str(m)})
    return out


def im_chat(X, cid, t, d, p):
    SO.base_css(X)
    msgs = _norm(p.get("messages") or p.get("items") or [])[:30]
    if not msgs: msgs = [{"me": False, "name": "", "text": "在吗？"}, {"me": True, "name": "", "text": "在的"}]
    P = X.portrait
    ww, wh = (90.0, 88.0) if P else (78.0, 76.0)
    area = wh - 7.6 - 8.0
    texts = [m for m in msgs if not m.get("recall") and not m.get("voice") and not m.get("img")]
    n = len(msgs)
    base = 3.2 if n <= 4 else 2.9 if n <= 8 else 2.6 if n <= 14 else 2.4
    if P: base += 0.4
    spx = SO.px(X, base)
    names = {m["name"] for m in msgs if not m["me"] and m.get("name")}
    group = len(names) > 1
    bw_px = SO.px(X, ww * 0.68 - 6)
    rows, y = [], 1.6
    title = p.get("title") or (next(iter(names)) if len(names) == 1 else "群聊" if group else "对方")
    last_me = max((i for i, m in enumerate(msgs) if m["me"] and not m.get("recall")), default=-1)
    for i, m in enumerate(msgs):
        if m.get("time"):
            rows.append(("time", i, y, f'<div class="wpi-tm" data-t="{i}" style="top:{y:.2f}vmin">{X.rich(m["time"])}</div>')); y += 4.0
        side = "me" if m["me"] else "them"
        if m.get("recall"):
            who = "你" if m["me"] else "对方"
            rows.append(("recall", i, y, f'<div class="wpi-rc" data-i="{i}" style="top:{y:.2f}vmin">{who}撤回了一条消息</div>')); y += 4.4
            continue
        nm = f'<div class="wpi-nm">{X.rich(m.get("name", ""))}</div>' if group and not m["me"] else ""
        if m.get("voice"):
            sec = int(SO.num(m["voice"]) or 3)
            vw = 11 + min(sec, 60) * 0.55
            body = f'<div class="wpi-bb wpi-vo {side}" style="width:{vw:.1f}vmin; font-size:{base:.2f}vmin">{WAVE}<span>{sec}″</span></div>'
            h = base * 1.45 + 3.0
        elif m.get("img"):
            ar = FT.aspect(X, m["img"], 1.0)
            iw = min(ww * 0.42, 30.0 * ar) if ar < 1 else ww * 0.42
            ih = iw / ar
            body = f'<div class="wpi-im" style="width:{iw:.1f}vmin; height:{ih:.1f}vmin; background:#ccc url({X.asset(m["img"])}) center/cover"></div>'
            h = ih + 0.6
        else:
            fpx, lines = SO.lines_for(m.get("text", ""), bw_px, spx, max_lines=5)
            body = f'<div class="wpi-bb {side}" style="font-size:{SO.vm(X, fpx):.2f}vmin">{"<br>".join(X.rich(l) for l in lines)}</div>'
            h = SO.vm(X, fpx) * 1.45 * len(lines) + 3.0
        h += (2.6 if nm else 0)
        rd = '<div class="wpi-rd">已读</div>' if (p.get("read") and i == last_me) else ""
        av = SO.avatar(X, "我" if m["me"] else (m.get("name") or title), m.get("avatar"), "wpi-av")
        rows.append((side, i, y, f'<div class="wpi-r {side}" data-i="{i}" style="top:{y:.2f}vmin">{av}<div class="wpi-c">{nm}{body}{rd}</div></div>'))
        y += h + (2.4 if rd else 0) + 1.8
    total = y
    if total < area:                                      # a short exchange: the window hugs it
        area = max(total + 2.0, 30.0); wh = area + 7.6 + 8.0
    X.css("fx-wpi", """
.fx .wpi { position:relative; border-radius:3vmin; overflow:hidden; background:color-mix(in srgb, var(--card-fg) 5%, var(--card)); color:var(--card-fg);
  box-shadow:0 0 0 .3vmin color-mix(in srgb, var(--card-fg) 14%, transparent), 0 4vmin 10vmin rgba(0,0,0,.28); font-family:var(--f-body); }
#root.v .fx .wpi { margin-top:-15vmin; }
.fx .wpi-hd { height:7.6vmin; display:grid; grid-template-columns:8vmin 1fr 8vmin; align-items:center; background:var(--card); border-bottom:.2vmin solid color-mix(in srgb, var(--card-fg) 10%, transparent); }
.fx .wpi-hd > i { font-style:normal; font-size:3.6vmin; opacity:.6; text-align:center; }
.fx .wpi-tt { position:relative; height:7.6vmin; text-align:center; }
.fx .wpi-tt span { position:absolute; left:0; right:0; top:50%; transform:translateY(-50%); font-weight:700; font-size:2.7vmin; white-space:nowrap; }
.fx .wpi-tt .ty { font-weight:500; font-size:2.2vmin; opacity:0; }
.fx .wpi-v { position:relative; overflow:hidden; }
.fx .wpi-l { position:absolute; left:0; right:0; top:0; }
.fx .wpi-r { position:absolute; left:2.4vmin; right:2.4vmin; display:flex; gap:1.6vmin; align-items:flex-start; }
.fx .wpi-r.me { flex-direction:row-reverse; }
.fx .wpi-av { width:5.6vmin; height:5.6vmin; border-radius:1vmin !important; font-size:2.6vmin; }
.fx .wpi-c { display:flex; flex-direction:column; max-width:72%; }
.fx .wpi-r.me .wpi-c { align-items:flex-end; }
.fx .wpi-nm { font-size:1.8vmin; opacity:.55; margin:0 0 .6vmin .4vmin; }
.fx .wpi-bb { position:relative; padding:1.2vmin 2vmin; border-radius:1.2vmin; line-height:1.45; font-weight:500; }
.fx .wpi-bb.them { background:var(--card); transform-origin:0 0; }
.fx .wpi-bb.me { background:#95ec69; color:#111; transform-origin:100% 0; }
.fx .wpi-vo { display:flex; align-items:center; gap:1vmin; }
.fx .wpi-vo.me { flex-direction:row-reverse; } .fx .wpi-vo.me svg { transform:scaleX(-1); }
.fx .wpi-vo svg { width:1.4em; height:1.4em; fill:none; stroke:currentColor; stroke-width:2.2; stroke-linecap:round; }
.fx .wpi-im { border-radius:1.2vmin; box-shadow:0 0 0 .2vmin color-mix(in srgb, var(--card-fg) 12%, transparent); }
.fx .wpi-rd { font-size:1.7vmin; opacity:.5; margin-top:.5vmin; }
.fx .wpi-tm, .fx .wpi-rc { position:absolute; left:0; right:0; text-align:center; font-size:1.8vmin; opacity:.5; }
.fx .wpi-rc { font-size:1.9vmin; }
.fx .wpi-in { position:absolute; left:0; right:0; bottom:0; height:8vmin; display:flex; align-items:center; gap:1.4vmin; padding:0 2vmin; background:var(--card);
  border-top:.2vmin solid color-mix(in srgb, var(--card-fg) 10%, transparent); }
.fx .wpi-in i { flex:none; width:4.4vmin; height:4.4vmin; border-radius:50%; border:.25vmin solid color-mix(in srgb, var(--card-fg) 45%, transparent); font-style:normal; display:grid; place-items:center; font-size:2.2vmin; opacity:.7; }
.fx .wpi-in b { flex:1; height:5vmin; border-radius:.8vmin; background:color-mix(in srgb, var(--card-fg) 6%, transparent); }
""")
    mock = f'<i class="wp-mock" style="right:9vmin; top:2.2vmin">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    inner = (f'<div class="wpi" style="width:{ww:.1f}vmin; height:{wh:.1f}vmin">'
             f'<div class="wpi-hd"><i>‹</i><div class="wpi-tt"><span class="nm">{X.rich(title)}</span><span class="ty">对方正在输入…</span></div><i>···</i></div>{mock}'
             f'<div class="wpi-v" style="height:{area:.1f}vmin"><div class="wpi-l" style="height:{total:.1f}vmin">{"".join(r[3] for r in rows)}</div></div>'
             f'<div class="wpi-in"><i>◉</i><b></b><i>☺</i><i>+</i></div></div>')
    X.used_text.update("‹···对方正在输入…你撤回了一条消息已读″◉☺+0123456789群聊")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    X.tw(f'tl.from("{s} .wpi", {{y:60, opacity:0, scale:0.97, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    t_end = SO.cue(X, p, "t_end", t, t + d - 0.6)
    t0 = t + 0.45
    ev = [r for r in rows]
    step = min(0.7, max(0.12, (t_end - t0) / max(len(ev), 1)))
    typed_until = -1.0
    for k, (kind, i, top, _) in enumerate(ev):
        tk = t0 + k * step
        sel = f'{s} .wpi-tm[data-t=\'{i}\']' if kind == "time" else f'{s} .wpi-l > [data-i=\'{i}\']'
        if kind == "them" and step >= 0.3 and tk - 0.3 > typed_until + 0.02:
            typed_until = tk + 0.1
            X.tw(f'tl.to("{s} .wpi-tt .nm", {{opacity:0, duration:0.1}}, {tk - 0.3:.3f});')
            X.tw(f'tl.to("{s} .wpi-tt .ty", {{opacity:0.7, duration:0.1}}, {tk - 0.3:.3f});')
            X.tw(f'tl.to("{s} .wpi-tt .ty", {{opacity:0, duration:0.1}}, {tk:.3f});')
            X.tw(f'tl.to("{s} .wpi-tt .nm", {{opacity:1, duration:0.1}}, {tk:.3f});')
        if kind in ("me", "them"):
            X.tw(f'tl.from("{sel} .wpi-bb, {sel} .wpi-im", {{scale:0.4, opacity:0, duration:0.38, ease:"back.out(1.9)"}}, {tk:.3f});')
            X.tw(f'tl.from("{sel} .wpi-av, {sel} .wpi-nm", {{opacity:0, duration:0.2}}, {tk:.3f});')
            if k < 10: X.sfx(tk, "pop")
        else:
            X.tw(f'tl.from("{sel}", {{opacity:0, y:8, duration:0.3}}, {tk:.3f});')
        bottom = ev[k + 1][2] if k + 1 < len(ev) else total
        if total > area and bottom > area:
            X.tw(f'tl.to("{s} .wpi-l", {{y:"{-(min(bottom, total) - area + 1.6):.2f}vmin", duration:{min(0.4, step * 0.85):.2f}, ease:"power2.inOut"}}, {tk - 0.05:.3f});')
    if p.get("read") and last_me >= 0:
        X.tw(f'tl.from("{s} .wpi-rd", {{opacity:0, duration:0.3}}, {t0 + len(ev) * step + 0.1:.3f});')


FX = {"im_chat": im_chat}
