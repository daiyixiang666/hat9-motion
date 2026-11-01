"""评论楼层 (comment section / 热评 — the 抖音 / B站 评论区截图 every 口播 quotes; Envato "Social Media
Comments" packs are a staple of the Social category): floors pop in one by one with their like counts ticking
up, replies nest under their parent, the feed scrolls when it outgrows the panel, then the hot comment lifts
out (others dim, a 热评 tag, the heart beats).

Adapts: 1–20 comments, each a word to a paragraph (≤4 lines, then ellipsis), 0–3 replies each; type size is
solved from the count; past the panel height the feed scrolls with the newest floor kept in view.
p: items [{name, text, likes, time, hot, replies:[…]} | "名字：内容" | [名字, 内容, 赞]] · total (header count)
   · title · sort · hl (index of the hot one; default the item marked hot, else the most liked) · t_hl · mock
"""
from h9.aefx import _clip
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


SO = _load("_social")


def comment_thread(X, cid, t, d, p):
    SO.base_css(X)
    rows = SO.items(p.get("items") or p.get("comments") or [])
    if not rows: rows = [{"name": "观众", "text": p.get("text", "说得太对了")}]
    rows = rows[:20]
    P = X.portrait
    pw = 92.0 if P else 100.0                              # panel width, vmin
    ph = 96.0 if P else 74.0                               # panel height
    view_h = ph - 7.0 - 7.6                                # minus header and input bar
    n = len(rows) + sum(len(SO.items(r.get("replies"))) for r in rows)
    base = 3.5 if n <= 3 else 3.1 if n <= 6 else 2.8 if n <= 10 else 2.5
    if P: base += 0.5
    size_px = SO.px(X, base)
    text_w = SO.px(X, pw - 6 - 7.2 - 9)                    # padding, avatar, like column

    def layout(r, reply=False):
        s = size_px * (0.86 if reply else 1.0)
        w = text_w - (SO.px(X, 7) if reply else 0)
        fpx, lines = SO.lines_for(r.get("text", ""), w, s, max_lines=3 if reply else 4)
        h = SO.vm(X, fpx) * 1.45 * len(lines) + (2.0 if reply else 2.4) + 2.6
        return fpx, lines, h

    hot = p.get("hl")
    if hot is None:
        hot = next((i for i, r in enumerate(rows) if r.get("hot")), None)
    if hot is None and any(SO.num(r.get("likes")) for r in rows):
        hot = max(range(len(rows)), key=lambda i: SO.num(rows[i].get("likes")) or 0)
    html, tops, y = [], [], 0.0
    for i, r in enumerate(rows):
        fpx, lines, h = layout(r)
        reps = SO.items(r.get("replies"))
        rep_html = ""
        for rr in reps[:3]:
            rpx, rl, rh = layout(rr, True)
            rep_html += (f'<div class="wpc-rp"><b>{X.rich(rr.get("name", ""))}</b>：<span style="font-size:{SO.vm(X, rpx):.2f}vmin">{"<br>".join(X.rich(l) for l in rl)}</span></div>')
            h += rh
        lk = SO.likes(r.get("likes"))
        tag = '<em class="wpc-hot">热评</em>' if i == hot else ""
        tm = f'<span class="wpc-tm">{X.rich(r.get("time", ""))}</span>' if r.get("time") else ""
        hi = '<i class="wpc-hi"></i>' if i == hot else ""
        html.append(f'<div class="wpc-r" data-i="{i}" style="top:{y:.2f}vmin">{hi}{SO.avatar(X, r.get("name", "?"), r.get("avatar"), "wpc-av")}'
                    f'<div class="wpc-b"><div class="wpc-n">{X.rich(r.get("name", ""))}{tag}{tm}</div>'
                    f'<div class="wpc-x" style="font-size:{SO.vm(X, fpx):.2f}vmin">{"<br>".join(X.rich(l) for l in lines)}</div>{rep_html}</div>'
                    f'<div class="wpc-lk"><span class="wpc-hs">{SO.HEART}{SO.HEART.replace("<svg", "<svg class=wpc-hf")}</span><b class="wpc-c" data-v="{SO.num(r.get("likes")) or 0:.0f}">{lk}</b></div></div>')
        tops.append((y, y + h)); y += h + 1.2
    total_h = y
    scroll = total_h > view_h
    if not scroll:                                         # short threads: the panel hugs its comments
        view_h = max(total_h + 1.0, 18.0); ph = view_h + 7.0 + 7.6
    X.css("fx-wpc", """
.fx .wpc { position:relative; background:var(--card); color:var(--card-fg); border-radius:2.4vmin; overflow:hidden;
  box-shadow:0 0 0 .25vmin color-mix(in srgb, var(--card-fg) 12%, transparent), 0 4vmin 10vmin rgba(0,0,0,.25); }
#root.v .fx .wpc { margin-top:-15vmin; }
.fx .wpc-hd { height:7vmin; display:flex; align-items:center; gap:1.4vmin; padding:0 3vmin; border-bottom:.2vmin solid color-mix(in srgb, var(--card-fg) 10%, transparent); font-family:var(--f-body); }
.fx .wpc-hd b { font-size:2.8vmin; font-weight:900; } .fx .wpc-hd span { font-size:2.2vmin; opacity:.55; font-variant-numeric:tabular-nums; }
.fx .wpc-hd i { margin-left:auto; font-style:normal; font-size:2vmin; opacity:.6; border:.2vmin solid color-mix(in srgb, var(--card-fg) 25%, transparent); border-radius:99vmin; padding:.4vmin 1.4vmin; }
.fx .wpc-v { position:relative; overflow:hidden; }
.fx .wpc-l { position:absolute; left:0; right:0; top:0; }
.fx .wpc-r { position:absolute; left:2.4vmin; right:2.4vmin; display:flex; gap:1.8vmin; padding:1.3vmin 1.4vmin; border-radius:1.6vmin; transform-origin:0 50%; }
.fx .wpc-av { position:relative; width:5.4vmin; height:5.4vmin; font-size:2.5vmin; }
.fx .wpc-b { position:relative; flex:1; min-width:0; font-family:var(--f-body); }
.fx .wpc-n { font-size:2.1vmin; font-weight:700; opacity:.6; display:flex; align-items:center; gap:1vmin; margin-bottom:.6vmin; }
.fx .wpc-tm { font-weight:500; opacity:.8; }
.fx .wpc-hot { font-style:normal; font-size:1.7vmin; font-weight:900; color:#fff; background:var(--accent); padding:.25vmin .9vmin; border-radius:.5vmin; opacity:0; }
.fx .wpc-x { font-weight:500; line-height:1.45; }
.fx .wpc-rp { margin-top:1vmin; padding:1vmin 1.6vmin; border-radius:1.2vmin; background:color-mix(in srgb, var(--card-fg) 6%, transparent); font-size:2vmin; line-height:1.45; }
.fx .wpc-rp b { font-weight:700; opacity:.7; }
.fx .wpc-lk { position:relative; flex:none; width:7vmin; display:flex; flex-direction:column; align-items:center; gap:.4vmin; padding-top:2.6vmin; font-family:var(--f-body); }
.fx .wpc-lk svg { width:3vmin; height:3vmin; fill:none; stroke:currentColor; stroke-width:2; opacity:.55; overflow:visible; }
.fx .wpc-lk b { font-size:1.9vmin; font-weight:700; opacity:.6; font-variant-numeric:tabular-nums; }
.fx .wpc-hi { position:absolute; inset:0; border-radius:1.6vmin; background:color-mix(in srgb, var(--accent) 10%, transparent); box-shadow:inset .6vmin 0 0 var(--accent); opacity:0; }
.fx .wpc-hs { position:relative; display:block; width:3vmin; height:3vmin; } .fx .wpc-hs svg { position:absolute; inset:0; }
.fx .wpc-lk svg.wpc-hf { fill:var(--accent); stroke:var(--accent); opacity:0; }
.fx .wpc-in { position:absolute; left:2.4vmin; right:2.4vmin; bottom:1.6vmin; height:4.8vmin; border-radius:99vmin; background:color-mix(in srgb, var(--card-fg) 7%, transparent);
  display:flex; align-items:center; padding:0 2.2vmin; font:500 2vmin var(--f-body); opacity:.75; }
""")
    mock = f'<i class="wp-mock" style="right:3vmin; top:1.8vmin">{X.rich(p.get("mock_label", "示意"))}</i>' if p.get("mock") else ""
    total = p.get("total")
    head = (f'<div class="wpc-hd"><b>{X.rich(p.get("title", "评论"))}</b>'
            f'<span>{X.rich((SO.likes(total) + " 条") if total else "")}</span><i style="{"margin-right:7vmin" if mock else ""}">{X.rich(p.get("sort", "按热度"))}</i></div>')
    inner = (f'<div class="wpc" style="width:{pw:.1f}vmin; height:{ph:.1f}vmin">{head}{mock}'
             f'<div class="wpc-v" style="height:{view_h:.1f}vmin"><div class="wpc-l" style="height:{total_h:.1f}vmin">{"".join(html)}</div></div>'
             f'<div class="wpc-in">{X.rich(p.get("placeholder", "说点什么…"))}</div></div>')
    X.used_text.update("评论条按热度说点什么…热评0123456789万.")
    _clip(X, cid, t, d, inner, p)
    s = f"#{cid}"
    th = SO.cue(X, p, "t_hl", t, t + d * 0.72)
    X.tw(f'tl.from("{s} .wpc", {{y:60, opacity:0, scale:0.97, duration:0.55, ease:"expo.out"}}, {t:.3f});')
    t0 = t + 0.35
    span = max(0.4, (min(th, t + d - 0.6) - 0.35) - t0)
    step = min(0.45, span / max(len(rows), 1))
    for i, (top, bot) in enumerate(tops):
        ti = t0 + i * step
        X.tw(f'tl.from("{s} .wpc-r[data-i=\'{i}\']", {{x:-30, opacity:0, scale:0.94, duration:0.42, ease:"back.out(1.6)"}}, {ti:.3f});')
        X.tw(f'(()=>{{const el=document.querySelector("{s} .wpc-r[data-i=\'{i}\'] .wpc-c"); if(!el) return; const v=+el.dataset.v; if(!v) return; const o={{v:0}};'
             f' tl.to(o, {{v:v, duration:{min(0.8, step * 1.6):.2f}, ease:"power2.out", onUpdate:()=>{{el.textContent = v>=1e4 ? (o.v/1e4).toFixed(1).replace(/\\.0$/,"")+"万" : String(Math.round(o.v));}}}}, {ti + 0.1:.3f});}})();')
        if scroll and bot > view_h:
            X.tw(f'tl.to("{s} .wpc-l", {{y:"{-(bot - view_h + 1):.2f}vmin", duration:0.45, ease:"power2.inOut"}}, {ti - 0.05:.3f});')
        if i < 6: X.sfx(ti, "pop")
    if hot is not None and 0 <= hot < len(rows):
        top, bot = tops[hot]
        if scroll:
            tgt = min(max(0.0, top - (view_h - (bot - top)) / 2), total_h - view_h)
            X.tw(f'tl.to("{s} .wpc-l", {{y:"{-tgt:.2f}vmin", duration:0.6, ease:"power3.inOut"}}, {th - 0.35:.3f});')
        X.tw(f'tl.to("{s} .wpc-r:not([data-i=\'{hot}\'])", {{opacity:0.32, duration:0.35}}, {th:.3f});')
        X.tw(f'tl.to("{s} .wpc-r[data-i=\'{hot}\'] .wpc-hi, {s} .wpc-r[data-i=\'{hot}\'] .wpc-hf", {{opacity:1, duration:0.3}}, {th:.3f});')
        X.tw(f'tl.fromTo("{s} .wpc-r[data-i=\'{hot}\']", {{scale:1}}, {{scale:1.035, duration:0.4, ease:"back.out(2)"}}, {th:.3f});')
        X.tw(f'tl.to("{s} .wpc-r[data-i=\'{hot}\'] .wpc-hot", {{opacity:1, duration:0.01}}, {th + 0.1:.3f});')
        X.tw(f'tl.from("{s} .wpc-r[data-i=\'{hot}\'] .wpc-hot", {{scale:0, duration:0.35, ease:"back.out(3)"}}, {th + 0.1:.3f});')
        X.tw(f'tl.fromTo("{s} .wpc-r[data-i=\'{hot}\'] .wpc-hs", {{scale:1}}, {{keyframes:[{{scale:1.5, duration:0.14}}, {{scale:1, duration:0.3, ease:"back.out(3)"}}], transformOrigin:"50% 50%"}}, {th + 0.15:.3f});')
        X.sfx(th, "hit")


FX = {"comment_thread": comment_thread}
