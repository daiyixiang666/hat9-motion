"""邮件截图 (an email as evidence — a quote from a mail thread, an offer, a notice): a neutral mail client opens,
the message row is picked from the inbox, the message pane slides in with sender, recipients, date and subject, the
body types out paragraph by paragraph and the *marked* sentence gets the highlighter.

p: subject · sender ("名字 <地址>" or {name, addr}) · to · date · body (list of paragraphs or "a|b") · attachments (list) ·
   inbox (list of {sender, subject, time} shown first; omitted → a minimal list built around this message) · stamp ("示意" etc.) · title
Adapts: subject 1–3 lines, body 1–6 paragraphs (one size for all, shrinking to 20 px; short bodies set larger), 0–4 attachments, any name length;
16:9 inbox column + message pane, 9:16 message pane only. Generic client chrome — no real product's look or logo.
Fabricated or example emails must carry a stamp such as 「示意」.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys, re

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def _who(v):
    if isinstance(v, dict): return str(v.get("name", "")), str(v.get("addr", ""))
    m = re.match(r"\s*(.*?)\s*<([^>]+)>", str(v or ""))
    return (m.group(1), m.group(2)) if m else (str(v or ""), "")


def email_card(X, cid, t, d, p):
    name, addr = _who(p.get("sender") or p.get("from"))
    subj = fit.as_text(p.get("subject"), " ")
    body = [str(b) for b in fit.as_list(p.get("body"))]
    atts = [str(a) for a in fit.as_list(p.get("attachments"))][:4]
    x0, y0, x1, y1 = D.box(X, p, text=True)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    inbox = p.get("inbox")
    if inbox is None:
        inbox = [{"sender": name or "发件人", "subject": subj, "time": p.get("date", "")}]
    show_inbox = (not P) and bool(inbox)
    lw = bw * 0.3 if show_inbox else 0
    mx, my, mw, mh = x0 + lw, y0, bw - lw, bh
    pad = 34 if not P else 30
    sf = D.C.fitted(X, subj, mw - 2 * pad, 150, 46 if not P else 44, 26, max_lines=3, lh=1.18)
    meta_h = 96
    att_h = 64 if atts else 0
    bh_avail = mh - pad * 2 - sf.n * sf.px * 1.18 - 24 - meta_h - att_h - 20
    # body: one size for all paragraphs, fitted to the room left
    joined = "|".join(body) if body else ""
    bpx = (34 if not P else 32) if len(joined) > 60 else (44 if not P else 42)
    while bpx > 20:
        tot = 0; fits = []
        for b in body:
            f = D.wrap(b, bpx, mw - 2 * pad)
            fits.append(f); tot += f.n * bpx * 1.45 + bpx * 0.6
        if tot <= bh_avail or bpx <= 21: break
        bpx -= 2
    tone = D.C.tone(name)
    mono = D.C.mono(name)
    X.used_text.update(name + addr + subj + "".join(body) + "".join(atts) + str(p.get("to", "")) + str(p.get("date", "")) + str(p.get("stamp", "")) + "发件人收件人收件箱附件 ")
    paras = "".join(f'<div class="em-p" data-k="{i}" style="font-size:{bpx}px">{D.C.lines(X, f, "em-l")}</div>' for i, f in enumerate(fits))
    att_html = ("<div class='em-atts'>" + "".join(f'<div class="em-att"><i></i><span>{X.rich(a)}</span></div>' for a in atts) + "</div>") if atts else ""
    stamp = f'<div class="em-stamp">{X.rich(p["stamp"])}</div>' if p.get("stamp") else ""
    pane = (f'<div class="em-pane" style="left:{mx:.0f}px; top:{my:.0f}px; width:{mw:.0f}px; height:{mh:.0f}px; padding:{pad}px">'
            f'<div class="em-subj" style="font-size:{sf.px}px">{D.C.lines(X, sf)}</div>'
            f'<div class="em-meta"><div class="ct-mono" style="width:60px; height:60px; font-size:{26 if len(mono) > 1 else 30}px; background:{tone}">{X.rich(mono)}</div>'
            f'<div class="em-who"><b>{X.rich(name)}</b><span>{X.rich(addr)}</span><em>收件人：{X.rich(p.get("to", ""))}</em></div><time>{X.rich(p.get("date", ""))}</time></div>'
            f'<div class="em-body">{paras}</div>{att_html}{stamp}</div>')
    inbox_html = ""
    if show_inbox:
        rows = []
        for i, it in enumerate(inbox[:7]):
            s_, f_ = str(it.get("subject", "")), str(it.get("sender", ""))
            X.used_text.update(s_ + f_ + str(it.get("time", "")))
            rows.append(f'<div class="em-row" data-k="{i}"><b>{X.rich(f_)}</b><span>{X.rich(s_)}</span><time>{X.rich(it.get("time", ""))}</time></div>')
        pick = next((i for i, it in enumerate(inbox) if str(it.get("subject", "")) == subj), 0)
        inbox_html = f'<div class="em-list" style="left:{x0:.0f}px; top:{y0:.0f}px; width:{lw - 16:.0f}px; height:{bh:.0f}px"><div class="em-lh">收件箱</div>{"".join(rows)}</div>'
    else:
        pick = 0
    X.css("fx-d2", D.CSS)
    X.css("fx-cite-base", D.C.CSS)
    X.css("fx-email", """
.em-list { position:absolute; border-radius:14px; background:color-mix(in srgb, var(--fg) 6%, var(--bg)); padding:14px; display:flex; flex-direction:column; gap:8px; overflow:hidden; }
.em-lh { font:800 20px var(--f-body); color:var(--muted); letter-spacing:.1em; padding:4px 8px 8px; }
.em-row { position:relative; display:grid; grid-template-columns:1fr auto; gap:2px 10px; padding:12px 14px; border-radius:10px; background:var(--card); box-shadow:0 1px 0 rgba(0,0,0,.05); }
.em-row b { font:800 19px var(--f-body); color:var(--card-fg, var(--fg)); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.em-row span { grid-column:1 / 3; font:500 17px var(--f-body); color:var(--muted); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.em-row time { font:500 16px var(--f-mono, monospace); color:var(--muted); }
.em-row.sel { box-shadow:0 0 0 2.5px var(--accent); }
.em-pane { position:absolute; box-sizing:border-box; border-radius:16px; background:var(--card); color:var(--card-fg, var(--fg)); box-shadow:0 26px 70px rgba(0,0,0,.26); overflow:hidden; display:flex; flex-direction:column; gap:20px; }
.em-subj { font-family:var(--f-display); font-weight:900; line-height:1.18; }
.em-meta { display:flex; align-items:center; gap:16px; padding-bottom:18px; border-bottom:1.5px solid color-mix(in srgb, var(--card-fg, var(--fg)) 12%, transparent); }
.em-who { display:flex; flex-direction:column; min-width:0; flex:1; }
.em-who b { font:800 22px var(--f-body); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.em-who span, .em-who em { font:500 16px var(--f-mono, monospace); color:var(--muted); font-style:normal; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.em-meta time { font:500 16px var(--f-mono, monospace); color:var(--muted); white-space:nowrap; }
.em-body { display:flex; flex-direction:column; gap:.6em; overflow:hidden; flex:1; }
.em-p { font-family:var(--f-body); font-weight:500; line-height:1.45; }
.em-atts { display:flex; gap:12px; flex-wrap:wrap; }
.em-att { display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:10px; background:color-mix(in srgb, var(--card-fg, var(--fg)) 7%, transparent); font:600 17px var(--f-body); }
.em-att i { width:22px; height:26px; border-radius:3px; background:var(--accent); }
.em-stamp { position:absolute; right:26px; top:22px; font:900 22px var(--f-body); color:#c1271b; border:3px solid #c1271b; border-radius:8px; padding:2px 12px; transform:rotate(6deg); opacity:.85; }
.em-row .em-sel { position:absolute; inset:0; border-radius:10px; box-shadow:0 0 0 2.5px var(--accent); opacity:0; }
""")
    inbox_html = inbox_html.replace(f'<div class="em-row" data-k="{pick}">', f'<div class="em-row" data-k="{pick}"><i class="em-sel"></i>', 1) if show_inbox else ""
    _clip(X, cid, t, d, f'<div class="d2 em">{inbox_html}{pane}</div>', p)
    S = f"#{cid}"
    t_open = t
    if show_inbox:
        X.tw(f'tl.from("{S} .em-list", {{x:-40, opacity:0, duration:0.5, ease:"expo.out"}}, {t:.3f});')
        X.tw(f'tl.from("{S} .em-row", {{y:16, opacity:0, duration:0.35, ease:"power3.out", stagger:0.06}}, {t + 0.1:.3f});')
        X.tw(f'tl.to("{S} .em-row[data-k=\'{pick}\'] .em-sel", {{opacity:1, duration:0.2}}, {t + 0.55:.3f});')
        X.tw(f'tl.fromTo("{S} .em-row[data-k=\'{pick}\']", {{scale:1}}, {{keyframes:[{{scale:0.96, duration:0.08}}, {{scale:1, duration:0.2}}]}}, {t + 0.6:.3f});')
        X.sfx(t + 0.6, "click")
        t_open = t + 0.7
    X.tw(f'tl.from("{S} .em-pane", {{x:60, opacity:0, duration:0.6, ease:"expo.out"}}, {t_open:.3f});')
    X.tw(f'tl.from("{S} .em-subj .ct-l > span, {S} .em-meta", {{yPercent:60, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t_open + 0.15:.3f});')
    tb = t_open + 0.55
    span = max(0.4, (t + d) - tb - 1.2)
    for i in range(len(body)):
        X.tw(f'tl.from("{S} .em-p[data-k=\'{i}\']", {{opacity:0, y:12, duration:0.35, ease:"power2.out"}}, {tb + span * i / max(1, len(body)):.3f});')
    if atts: X.tw(f'tl.from("{S} .em-att", {{scale:0.8, opacity:0, duration:0.3, ease:"back.out(2)", stagger:0.08}}, {tb + span * 0.8:.3f});')
    if p.get("stamp"): X.tw(f'tl.from("{S} .em-stamp", {{scale:1.6, opacity:0, duration:0.3, ease:"back.out(2)"}}, {t_open + 0.4:.3f});')
    if "*" in joined: D.C.marker(X, f"{S} .em-body", tb + span + 0.15)
    hold = tb + span + 0.7
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .em-pane", {{scale:1.02, duration:{t + d - hold:.2f}, ease:"none"}}, {hold:.3f});')


FX = {"email_card": email_card}
