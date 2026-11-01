"""公告 / 通知文件 (an announcement or notice shown as a document): a neutral A4-style sheet — issuer, document number,
centred title, numbered clauses, signature and date — rises into view, the clauses set line by line, the *marked*
clause gets the highlighter and the camera leans in on it.

p: org (issuer line) · kind ("公告" | "通知" | "说明" | …) · no (document number) · title · body (list of clauses or "a|b") ·
   date · signer · watermark (default "版式示意" — keep it unless this is your own document) · numbered (true)
Adapts: title 1–3 lines, 1–8 clauses of any length (one size, shrinking to fit), long issuer names; 16:9 sheet centre-left
with room for the caption, 9:16 sheet full width. Deliberately plain: no red masthead, no seal — never imitate a real
official document's look.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)

NUM = "一二三四五六七八九十"


def notice_card(X, cid, t, d, p):
    org, kind = fit.as_text(p.get("org")), fit.as_text(p.get("kind", "公告"))
    title = fit.as_text(p.get("title"), " ")
    body = [str(b) for b in fit.as_list(p.get("body"))] or ["……"]
    x0, y0, x1, y1 = D.box(X, p, text=True)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    ar = 0.72
    sh = bh * 0.93; sw = min(bw * (0.96 if P else 0.6), sh * ar if not P else bw * 0.96)
    if P: sh = min(bh * 0.93, sw / ar * 1.12)
    sx, sy = x0 + (bw - sw) / 2, y0 + (bh - sh) / 2
    pad = sw * 0.085
    iw = sw - 2 * pad
    opx = max(12, min(26, iw * 0.94 / max(fit.width(org) * 1.04 + fit.width(kind) * 1.3 + 1.5, 1)))
    tf = D.C.fitted(X, title, iw, sh * 0.16, 46 if not P else 44, 24, max_lines=3, lh=1.25)
    room = sh - pad * 2 - opx * 2.6 - tf.n * tf.px * 1.25 - 40 - 90
    numbered = p.get("numbered", True) and len(body) > 1
    texts = [(f"{NUM[i]}、" if numbered and i < len(NUM) else "") + b for i, b in enumerate(body)]
    bpx = 30 if not P else 30
    while bpx > 17:
        fits = [D.wrap(s_, bpx, iw) for s_ in texts]
        if sum(f.n * bpx * 1.6 + bpx * 0.5 for f in fits) <= room or bpx <= 18: break
        bpx -= 2
    wm = p.get("watermark", "版式示意")
    X.used_text.update(org + kind + title + "".join(texts) + str(p.get("no", "")) + str(p.get("date", "")) + str(p.get("signer", "")) + str(wm or "") + "编号")
    clauses = "".join(f'<div class="nt-c" data-k="{i}" style="font-size:{bpx}px">{D.C.lines(X, f, "nt-l")}</div>' for i, f in enumerate(fits))
    sheet = (f'<div class="d2-sheet nt-sh" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{sw:.0f}px; height:{sh:.0f}px; padding:{pad:.0f}px">'
             f'<div class="nt-org" style="font-size:{opx:.0f}px"><b>{X.rich(org)}</b><span>{X.rich(kind)}</span></div>'
             + (f'<div class="nt-no" style="font-size:{max(15, opx * 0.72):.0f}px">编号：{X.rich(p["no"])}</div>' if p.get("no") else "")
             + '<i class="nt-rule"></i>'
             + f'<div class="nt-ttl" style="font-size:{tf.px}px">{D.C.lines(X, tf)}</div>'
             + f'<div class="nt-body">{clauses}</div>'
             + f'<div class="nt-sig" style="font-size:{max(18, bpx * 0.9):.0f}px"><b>{X.rich(p.get("signer") or org)}</b><span>{X.rich(p.get("date", ""))}</span></div>'
             + (f'<div class="nt-wm">{X.rich(wm)}</div>' if wm else "") + '</div>')
    X.css("fx-d2", D.CSS)
    X.css("fx-notice", """
.nt-sh { box-sizing:border-box; display:flex; flex-direction:column; color:#1b1b1b; }
.nt-org { display:flex; justify-content:space-between; align-items:baseline; gap:1em; font-family:var(--f-body); }
.nt-org b { font-weight:900; letter-spacing:.04em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.nt-org span { font-weight:700; color:#555; letter-spacing:.3em; white-space:nowrap; }
.nt-no { font-family:var(--f-mono, monospace); color:#666; margin-top:6px; }
.nt-rule { display:block; height:2px; background:#1b1b1b; margin:14px 0 26px; transform-origin:0 50%; }
.nt-ttl { font-family:var(--f-quote, var(--f-display)); font-weight:900; text-align:center; line-height:1.25; margin-bottom:22px; }
.nt-body { display:flex; flex-direction:column; gap:.5em; flex:1; }
.nt-c { font-family:var(--f-body); font-weight:500; line-height:1.6; }
.nt-l { overflow:hidden; }
.nt-sig { display:flex; flex-direction:column; align-items:flex-end; gap:4px; font-family:var(--f-body); }
.nt-sig b { font-weight:800; } .nt-sig span { color:#555; font-family:var(--f-mono, monospace); font-size:.85em; }
.nt-wm { position:absolute; left:50%; top:50%; transform:translate(-50%,-50%) rotate(-24deg); font:900 72px var(--f-body); color:rgba(0,0,0,.06); letter-spacing:.3em; white-space:nowrap; pointer-events:none; }
""")
    _clip(X, cid, t, d, f'<div class="d2 nt">{sheet}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .nt-sh", {{y:90, opacity:0, duration:0.65, ease:"expo.out"}}, {t:.3f});')
    X.sfx(t, "paper")
    X.tw(f'tl.from("{S} .nt-org, {S} .nt-no", {{opacity:0, y:10, duration:0.4, stagger:0.08}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("{S} .nt-rule", {{scaleX:0, duration:0.5, ease:"power3.out"}}, {t + 0.35:.3f});')
    X.tw(f'tl.from("{S} .nt-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.5, ease:"expo.out", stagger:0.06}}, {t + 0.45:.3f});')
    tb = t + min(0.85, d * 0.22)                         # short beats: every line has landed by ~60 % of the beat
    span = max(0.3, min(d * 0.28, 0.35 * len(body) + 0.3))
    X.tw(f'tl.from("{S} .nt-l > span", {{yPercent:105, duration:{min(0.4, d * 0.12):.2f}, ease:"expo.out", stagger:{span / max(1, sum(f.n for f in fits)):.3f}}}, {tb:.3f});')
    X.tw(f'tl.from("{S} .nt-sig", {{opacity:0, duration:0.4}}, {tb + span:.3f});')
    tm = tb + span + 0.2
    if any("*" in b for b in body):
        D.C.marker(X, f"{S} .nt-body", tm)
        k = next(i for i, b in enumerate(body) if "*" in b)
        X.tw(f'tl.to("{S} .nt-sh", {{scale:1.035, transformOrigin:"50% {min(85, 30 + 60 * (k + 0.5) / len(body)):.0f}%", duration:{max(0.6, t + d - tm):.2f}, ease:"power2.out"}}, {tm:.3f});')
    elif t + d - tm > 0.3:
        X.tw(f'tl.to("{S} .nt-sh", {{scale:1.03, duration:{t + d - tm:.2f}, ease:"none"}}, {tm:.3f});')


FX = {"notice_card": notice_card}
