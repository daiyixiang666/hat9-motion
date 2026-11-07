"""数字贴在主体旁 (side stat · the big-number-beside-the-subject layout seen in an open-source portrait-template promo):
a big number with its unit and a small caption, pinned beside the subject; it counts up (or swaps) and an optional
coloured tag drops in under it. Several values can replace each other in the same slot inside one beat — each on
its own "@词" cue — and with side "both" they alternate left and right of a centred subject.

p: values [{v: "174", unit: "个", cap: "动效 · 含 12 种转场", kicker: "已收录", tag: "还在涨", at: "@词", side}] (1–6;
   a plain string works) · or value / unit / cap / kicker / tag for one · count (default true: numbers count from
   the previous one) · side left | right | both · subject | video | image (+ subject_focus, subject_start,
   subject_fit, subject_tag)
Adapts: 1–6 values; numbers with separators / decimals / a trailing + or %, or words (swapped, not counted); the
number is sized once for the widest value so the slot never jumps; with no subject the number owns the left of the
frame and a column of bars on the right grows one bar per value (the current one in the accent). 16:9 and 9:16
(9:16: a tall subject card, the number in the column beside it, both filling the frame).
Re-skins with the style: number font (f-num), card frame, tag shape, the style's ease.
"""
import re
from h9 import fit as FT
import importlib.util, pathlib, sys


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s)
        s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


K = _load("_kinfo")

CSS = r"""
.ki .ss-slot { position:absolute; }
.ki .ss-it { position:absolute; left:0; top:0; width:100%; }
.ki .ss-kick { font-family:var(--f-display); font-weight:900; line-height:1.1; white-space:nowrap; }
.ki .ss-row { display:flex; align-items:baseline; white-space:nowrap; }
.ki .ss-num { font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:.96; letter-spacing:-.03em; font-variant-numeric:tabular-nums; color:var(--fg); }
.ki .ss-it.acc .ss-num { color:var(--accent); }
.ki .ss-suf { font-family:var(--f-num, var(--f-display)); font-weight:900; color:var(--accent); align-self:flex-start; line-height:1; }
.ki .ss-unit { font-family:var(--f-display); font-weight:900; margin-left:.25em; }
.ki .ss-cap { font-family:var(--f-body); font-weight:700; color:var(--muted); white-space:nowrap; margin-top:.35em; letter-spacing:.04em; }
.ki .ss-tag { display:inline-flex; align-items:center; gap:.4em; margin-top:.7em; font-family:var(--f-body); font-weight:800; white-space:nowrap;
  color:var(--k-on-alert); background:var(--k-alert); padding:.28em .7em; border-radius:var(--k-rs); }
.ki.sk-ink .ss-tag { border-radius:4px; }
.ki .ss-bars { position:absolute; display:flex; align-items:flex-end; }
.ki .ss-bar { position:relative; flex:1; height:100%; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; }
.ki .ss-bar b { display:block; width:100%; background:color-mix(in srgb, var(--fg) 18%, transparent); transform-origin:50% 100%; border-radius:var(--k-rs) var(--k-rs) 0 0; }
.ki.sk-flat .ss-bar b, .ki.sk-iso3d .ss-bar b, .ki.sk-screen .ss-bar b, .ki.sk-chrome3d .ss-bar b, .ki.sk-clay .ss-bar b { border-radius:14px 14px 0 0; }
.ki .ss-bar b { position:relative; } .ki .ss-bar b i { position:absolute; inset:0; background:var(--accent); border-radius:inherit; opacity:0; }
.ki .ss-bar span { position:absolute; bottom:-46px; font:700 24px var(--f-num, var(--k-kf)); color:var(--muted); white-space:nowrap; }
.ki .ss-base { position:absolute; height:3px; background:var(--fg); transform-origin:0 50%; }
"""

NUM = re.compile(r"^(\D*?)([\d][\d,]*(?:\.\d+)?)(.*)$")


def _parse(v):
    """'174+' → ('', '174', '+', 174.0); words → (v, None, '', None)."""
    s = str(v).strip()
    m = NUM.match(s)
    if not m:
        return s, None, "", None
    digits = m.group(2)
    val = float(digits.replace(",", ""))
    return m.group(1), digits, m.group(3), val


def _items(p):
    raw = p.get("values")
    if not raw:
        raw = [{"v": p.get("value", "100"), "unit": p.get("unit", ""), "cap": p.get("cap", p.get("caption", "")),
                "kicker": p.get("kicker", ""), "tag": p.get("tag", ""), "at": p.get("at")}]
    out = []
    for it in list(raw)[:6]:
        if not isinstance(it, dict):
            it = {"v": it}
        out.append(it)
    return out


def _count_js(X, sel, a, b, digits, t, dur):
    raw = digits.replace(",", "")
    dec = 0
    if "." in raw:
        dec = len(raw.split(".")[1])
    if "," in digits:
        fmt = f"o.v.toLocaleString('en-US', {{minimumFractionDigits:{dec}, maximumFractionDigits:{dec}}})"
    else:
        fmt = f"o.v.toFixed({dec})"
    X.tw(f'(()=>{{const o={{v:{a}}}, el=document.querySelector("{sel}"); tl.fromTo(o, {{v:{a}}}, {{v:{b}, duration:{dur:.2f}, ease:"power3.out", immediateRender:false, '
         f'onUpdate:()=>{{el.textContent={fmt};}}}}, {t:.3f});}})();')


def side_stat(X, cid, t, d, p):
    k = K.skin(X)
    e = K.ease(X)
    P = X.portrait
    src = K.src_of(p)
    its = _items(p)
    n = len(its)
    side = p.get("side", "left")
    x0, y0, x1, y1 = K.area(X, p)
    aw = x1 - x0
    ah = y1 - y0
    inner = []
    slots = {}            # side → (x, y, w, h)
    if src:
        ar = K.subject_ar(X, src)
        if side == "both":
            if P:
                sw = aw * 0.5
            else:
                sw = aw * 0.3
            sh = min(ah * 0.94, sw / max(0.6, min(1.0, ar)))
            sx = x0 + (aw - sw) / 2
            sy = y0 + (ah - sh) / 2 + (ah * 0.06 if P else 0)
            inner.append(K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="ss-subj"))
            gap = 30 if P else 56
            if P:
                # 9:16: one value above the card, the next below it, the card in the middle
                sh = ah * 0.44
                sw = min(aw * 0.8, max(aw * 0.62, sh * max(0.62, min(1.4, ar))))
                sx = x0 + (aw - sw) / 2
                sy = y0 + ah * 0.29
                inner[-1] = K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="ss-subj")
                slots["left"] = (x0, y0 + 24, aw * 0.94, ah * 0.27 - 24)
                slots["right"] = (x0 + aw * 0.06, sy + sh + ah * 0.02, aw * 0.94, y1 - sy - sh - ah * 0.02)
            else:
                slots["left"] = (x0, y0 + ah * 0.2, sx - x0 - gap, ah * 0.6)
                slots["right"] = (sx + sw + gap, y0 + ah * 0.2, x1 - sx - sw - gap, ah * 0.6)
        elif P:
            # 9:16: the number across the top, the subject card filling the rest of the frame
            slots[side] = (x0, y0 + ah * 0.01, aw, ah * 0.34)
            sy = y0 + ah * 0.37
            sh = K.low(X, p) - sy
            sw = min(aw * 0.9, max(aw * 0.62, sh * max(0.62, min(1.4, ar))))
            sx = x0 + (aw - sw) / 2
            inner.append(K.subject(X, p, sx, sy, sw, sh, t, d, k, cls="ss-subj"))
        else:
            card_side = "right" if side == "left" else "left"
            sar = min(1.1, max(0.62, ar))
            sr, tr = K.beside(X, p, sub_ar=sar, side=card_side, sub_share=0.5 if P else 0.44)
            inner.append(K.subject(X, p, sr[0], sr[1], sr[2], sr[3], t, d, k, cls="ss-subj"))
            slots[side] = (tr[0], tr[1] + tr[3] * 0.18, tr[2], tr[3] * 0.64)
    else:
        if P:
            slots[side if side != "both" else "left"] = (x0, y0 + ah * 0.04, aw, ah * 0.42)
        else:
            slots[side if side != "both" else "left"] = (x0 + 20, y0 + ah * 0.16, aw * 0.5, ah * 0.68)
    # which slot each value goes to
    keys = list(slots.keys())
    where = []
    for i in range(n):
        s = its[i].get("side")
        if s not in slots:
            if side == "both" and len(keys) > 1:
                s = keys[i % 2]
            else:
                s = keys[0]
        where.append(s)
    # one number size per slot, for its widest value
    sizes = {}
    for key in keys:
        bx, by, bw, bh = slots[key]
        best = 300 if not P else 330
        for i in range(n):
            if where[i] != key:
                continue
            it = its[i]
            pre, digits, suf, val = _parse(it.get("v", ""))
            unit = str(it.get("unit", ""))
            em = FT.width(str(it.get("v", ""))) + FT.width(unit) * 0.34 + (0.3 if unit else 0)
            extra = 0.0
            if it.get("kicker"):
                extra += 0.36
            if it.get("cap"):
                extra += 0.3
            if it.get("tag"):
                extra += 0.42
            px_w = bw * 0.96 / max(1.0, em)
            px_h = bh / (1.0 + extra)
            px = min(px_w, px_h)
            if px < best:
                best = px
        sizes[key] = max(40, best)
    # the value pieces
    nums = []
    for i in range(n):
        it = its[i]
        key = where[i]
        bx, by, bw, bh = slots[key]
        px = sizes[key]
        pre, digits, suf, val = _parse(it.get("v", ""))
        nums.append((pre, digits, suf, val))
        parts = []
        if it.get("kicker"):
            X.used_text.update(str(it["kicker"]))
            parts.append(f'<div class="ss-kick" style="font-size:{px * 0.3:.0f}px">{X.rich(it["kicker"])}</div>')
        row = ""
        if pre:
            row += f'<span class="ss-unit" style="font-size:{px * 0.34:.0f}px; margin:0 .2em 0 0">{X.rich(pre)}</span>'
        if digits is None:
            row += f'<span class="ss-num">{X.rich(it.get("v", ""))}</span>'
        else:
            X.used_text.update("0123456789,.")
            row += f'<span class="ss-num" data-n="{i}">{digits}</span>'
            if suf.strip():
                row += f'<span class="ss-suf" style="font-size:{px * 0.5:.0f}px">{X.rich(suf.strip())}</span>'
        if it.get("unit"):
            X.used_text.update(str(it["unit"]))
            row += f'<span class="ss-unit" style="font-size:{px * 0.3:.0f}px">{X.rich(it["unit"])}</span>'
        parts.append(f'<div class="ss-row" style="font-size:{px:.0f}px">{row}</div>')
        if it.get("cap"):
            cpx, cl = K.fit(it["cap"], bw, px * 0.4, max(22, px * 0.17), 18, max_lines=1)
            X.used_text.update(str(it["cap"]))
            parts.append(f'<div class="ss-cap" style="font-size:{cpx}px">{X.rich(cl[0] if cl else it["cap"])}</div>')
        if it.get("tag"):
            X.used_text.update(str(it["tag"]))
            parts.append(f'<div class="ss-tag" style="font-size:{max(22, px * 0.16):.0f}px">{X.rich(it["tag"])}</div>')
        est = px * 0.98
        if it.get("kicker"):
            est += px * 0.33
        if it.get("cap"):
            est += max(22, px * 0.17) * 1.6
        if it.get("tag"):
            est += max(22, px * 0.16) * 2.3
        top_off = max(0.0, (bh - est) / 2)
        acc = " acc" if (i == n - 1 and n > 1 and not it.get("tag")) else ""
        inner.append(f'<div class="ss-slot" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">'
                     f'<div class="ss-it{acc}" data-i="{i}" style="top:{top_off:.0f}px">{"".join(parts)}</div></div>')
    # no subject: one bar per numeric value on the right
    bars = []
    if not src:
        for i in range(n):
            if nums[i][3] is not None:
                bars.append(i)
        if bars:
            vmax = 0.0
            for i in bars:
                if nums[i][3] > vmax:
                    vmax = nums[i][3]
            if P:
                gx, gy, gw, gh = x0 + aw * 0.08, y0 + ah * 0.52, aw * 0.84, ah * 0.38
            else:
                gx, gy, gw, gh = x0 + aw * 0.6, y0 + ah * 0.14, aw * 0.36, ah * 0.66
            cols = []
            for i in bars:
                hh = max(0.04, nums[i][3] / vmax) * 100
                lab = str(its[i].get("v", ""))
                X.used_text.update(lab)
                cols.append(f'<div class="ss-bar" data-b="{i}"><b style="height:{hh:.1f}%"><i></i></b><span>{X.rich(lab)}</span></div>')
            gap = max(12, gw * 0.12 / max(1, len(bars)))
            inner.append(f'<div class="ss-bars" style="left:{gx:.0f}px; top:{gy:.0f}px; width:{gw:.0f}px; height:{gh:.0f}px; gap:{gap:.0f}px">{"".join(cols)}</div>')
            inner.append(f'<i class="ss-base" style="left:{gx - 20:.0f}px; top:{gy + gh:.0f}px; width:{gw + 40:.0f}px"></i>')
    X.css("fx-side-stat", CSS)
    s_ = K.root(X, cid, t, d, p, "".join(inner), k)
    # ---- motion
    if src:
        K.subject_in(X, f"{s_} .ss-subj", t, e)
        K.subject_drift(X, f"{s_} .ss-subj > img, {s_} .ss-subj > video, {s_} .ss-subj .k-pin > *", t, d)
    if bars:
        X.tw(f'tl.fromTo("{s_} .ss-base", {{scaleX:0}}, {{scaleX:1, duration:0.6, ease:"power3.out", immediateRender:true}}, {t + 0.1:.3f});')
    times = K.cues(X, p, "at_list", t, d, n, start=0.12, end=0.66)
    for i in range(n):
        v_at = its[i].get("at")
        if v_at is not None:
            times[i] = K.U.when(X, v_at, t, times[i])
    for i in range(1, n):
        if times[i] < times[i - 1] + 0.6:
            times[i] = times[i - 1] + 0.6
    last_in_slot = {}
    count = p.get("count", True)
    for i in range(n):
        ti = times[i]
        key = where[i]
        sel = f'{s_} .ss-it[data-i=\\"{i}\\"]'
        prev = last_in_slot.get(key)
        if prev is not None:
            psel = f'{s_} .ss-it[data-i=\\"{prev}\\"]'
            X.tw(f'tl.to("{psel}", {{y:-60, opacity:0, duration:0.3, ease:"power2.in"}}, {ti - 0.12:.3f});')
        X.tw(f'tl.fromTo("{sel}", {{y:70, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"{e}", immediateRender:true}}, {ti:.3f});')
        X.tw(f'tl.fromTo("{sel} .ss-row", {{scale:1.18, transformOrigin:"0% 80%"}}, {{scale:1, duration:0.55, ease:"power3.out", immediateRender:true}}, {ti:.3f});')
        pre, digits, suf, val = nums[i]
        if digits is not None and count:
            start = 0.0
            if prev is not None and nums[prev][3] is not None:
                start = nums[prev][3]
            else:
                for j in range(i - 1, -1, -1):
                    if nums[j][3] is not None:
                        start = nums[j][3]
                        break
            if start < val:
                _count_js(X, f'{s_} .ss-num[data-n=\\"{i}\\"]', start, val, digits, ti, min(0.9, max(0.45, (times[i + 1] - ti - 0.3) if i + 1 < n else 0.9)))
        X.sfx(ti, "count" if digits is not None else "pop")
        if its[i].get("cap"):
            X.tw(f'tl.fromTo("{sel} .ss-cap", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -2% 0 0)", duration:0.45, ease:"power2.out", immediateRender:true}}, {ti + 0.3:.3f});')
        if its[i].get("tag"):
            X.tw(f'tl.fromTo("{sel} .ss-tag", {{scale:0.4, opacity:0, rotation:-6}}, {{scale:1, opacity:1, rotation:0, duration:0.4, ease:"back.out(2.4)", immediateRender:true}}, {ti + 0.5:.3f});')
            X.sfx(ti + 0.5, "pop")
        if bars and i in bars:
            X.tw(f'tl.fromTo("{s_} .ss-bar[data-b=\\"{i}\\"] b", {{scaleY:0}}, {{scaleY:1, duration:0.6, ease:"power3.out", immediateRender:true}}, {ti:.3f});')
            X.tw(f'tl.fromTo("{s_} .ss-bar[data-b=\\"{i}\\"] span", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.3, immediateRender:true}}, {ti + 0.3:.3f});')
            X.tw(f'tl.to("{s_} .ss-bar[data-b=\\"{i}\\"] b i", {{opacity:1, duration:0.2}}, {ti:.3f});')
            for j in bars:
                if j < i:
                    X.tw(f'tl.to("{s_} .ss-bar[data-b=\\"{j}\\"] b i", {{opacity:0, duration:0.2}}, {ti:.3f});')
        last_in_slot[key] = i


FX = {"side_stat": side_stat}
