"""Step navigator + pinned chapter header: one film-level layer above the beats (like the chapter device).

video.json
  meta.nav = {"steps": ["选题", "找素材", "写稿", "配音字幕", "剪辑", "封面发布"], "numbered": true}
  beat.step = 3  or  "写稿"            this beat is step 3: the navigator shows, step 3 active
                                     (a beat without "step" hides the navigator; it comes back with the next step beat)
  beat.pin  = {"index": 1, "text": "工作室和团队"}  or  "工作室和团队"
                                     a running header for a stretch of beats (stays while consecutive beats share it)

16:9  navigator = one row of chips across the top (y 62–130, from x 110, 16 px gaps, padding 0 22 px, 34 px labels
      shrinking to 28 px, a 26 px "01" index); the active chip is filled with the style's ink, the others are outlined
      at 45 % opacity, finished steps carry a 3 px accent underline. The fill is one pill that slides to the next chip
      (10 frames, 6 % overshoot); too many long labels switch the row to compact (inactive chips show only "03").
      pin = x 110, y 60–124 (accent index 28 px + text 44 px / 800, floor 32 px); with the navigator on, a 34 px tag
      after the row's last chip.
9:16  navigator = a vertical rail (x 40–58, y 320–1300, 22 px nodes, the active one 30 px: done filled, future hollow)
      + one header chip with the active step only (y 208–284, 42 px name / 34 px mono index, "03 / 06 · 写稿", up to
      x 960, floor 34 px); a change runs the fill down the rail and rolls the header text up like an odometer
      (9 frames). The rail is furniture (data-safe="ignore"); the page under it is scaled 0.95 about (1000, 1600).
      pin = x 80, from y 208, 46 px / index 32 px (floor 36 px); with the navigator on, under the header chip
      (y 300–360) and the rail starts at y 400.
Other aspects use the 9:16 page (core.CANVAS shows it through a window).

While the navigator or a pin is on screen it takes the style's header slot: the style's own header row (kicker row,
status row, page header …) is hidden for those beats. Each style's header is listed in HEADER below; a style may
declare its own with STYLE["nav_slot"] = {"hide": [css selectors], "16:9": {"y": 70}, "9:16": {"y": 214}}
("hide" replaces the list here, "y" moves the navigator / pin row). Everything else (captions, meta.presenter,
meta.device chrome) stays: with a device on, the row moves under the device's top chrome.

Every motion is a GSAP tween on the one timeline (or a proxy tween redrawing from its value), so any frame renders on
its own. Colours come from the style tokens (ink / paper / fg / bg / accent) with contrast rules, never fixed values.
"""
import importlib.util
import json
import pathlib
import re

from h9 import fit
from h9 import device as DV

Z_NAV = 46            # above the beats, transitions (40) and the device chrome (44); under the captions (50)
F = 1 / 30
RAIL_SCALE = 0.95     # 9:16 beats under the rail: scaled about (1000, 1600): page x 20 → 69, x 56 → 103 (the rail ends at x 64), y 300 → 365 (under a pin)

# the style's own header furniture, hidden while the navigator / a pin holds the slot (selectors inside #root)
HEADER_COMMON = [".ctx .hd", ".ctx .rk", ".rk"]
HEADER = {
    "reel": [".rl-kick", ".rk"],
    "press": [".pr-hd"],
    "poster": [".po .hd"],
    "hud": [".hud-top", ".hud-read", ".hd-row", ".q > .title-zh"],
    "atlas": [".at-frame .hd"],
    "iso3d": [".iso-ov .hd"],
    "riso": [".rz-slug"],
}

CSS = r"""
.nv { pointer-events:none; }
.nv .nv-row { position:absolute; left:0; top:0; }
.nv .nv-chip { position:absolute; top:0; z-index:2; box-sizing:border-box; display:flex; align-items:center; white-space:nowrap;
  border-radius:var(--nv-r); padding:0 22px; }
.nv .nv-chip .nv-bd { position:absolute; inset:0; border-radius:var(--nv-r); border:2px solid var(--nv-fg); opacity:.45; }
.nv .nv-pl { position:absolute; top:0; border-radius:var(--nv-r); background:var(--nv-plate); z-index:0; }
.nv .nv-chip .nv-fl { position:absolute; inset:0; border-radius:var(--nv-r); background:var(--nv-fill); opacity:0; z-index:1; }
.nv .nv-chip { --nv-o:.45; --nv-c:var(--nv-fg); }
.nv .nv-chip b { position:relative; z-index:2; font:600 var(--nv-ipx) var(--f-mono, monospace); letter-spacing:.04em; color:var(--nv-c); opacity:var(--nv-o); }
.nv .nv-chip span { position:relative; z-index:2; font-family:var(--f-body); font-weight:700; color:var(--nv-c); filter:opacity(var(--nv-o)); white-space:nowrap; overflow:hidden; }
.nv .nv-chip .nv-u { position:absolute; left:14px; right:14px; bottom:-11px; height:3px; background:var(--nv-acc); transform-origin:0 50%; }
.nv .nv-pill { position:absolute; top:0; left:0; z-index:1; border-radius:var(--nv-r); background:var(--nv-fill); transform-origin:0 50%; }
.nv .nv-rail { position:absolute; }
.nv .nv-track { position:absolute; left:9px; width:4px; border-radius:2px; background:var(--nv-fg); opacity:.28; }
.nv .nv-run { position:absolute; left:9px; width:4px; border-radius:2px; background:var(--nv-acc); transform-origin:50% 0; }
.nv .nv-node { position:absolute; left:0; width:22px; height:22px; border-radius:50%; box-sizing:border-box; border:3px solid var(--nv-fg);
  background:var(--nv-plate-solid); }
.nv .nv-node i { position:absolute; inset:-3px; border-radius:50%; background:var(--nv-acc); transform:scale(0); }
.nv .nv-hd { position:absolute; box-sizing:border-box; height:76px; border-radius:var(--nv-r); background:var(--nv-fill); overflow:hidden; }
.nv .nv-hd .nv-ln { position:absolute; left:0; top:0; height:76px; display:flex; align-items:center; gap:16px; white-space:nowrap;
  padding:0 26px; color:var(--nv-on); }
.nv .nv-hd .nv-ln b { font:700 34px var(--f-mono, monospace); letter-spacing:.02em; }
.nv .nv-hd .nv-ln em { font-style:normal; font:700 var(--hd-px) var(--f-body); opacity:.6; }
.nv .nv-hd .nv-ln span { font:800 var(--hd-px) var(--f-body); }
.nv .nv-pin { position:absolute; display:flex; align-items:center; gap:12px; white-space:nowrap; box-sizing:border-box;
  border-radius:var(--nv-r); background:var(--nv-plate); padding:0 18px; transform-origin:0 0; }
.nv .nv-pin b { font:800 var(--pn-ipx) var(--f-mono, monospace); color:var(--nv-acc); letter-spacing:.02em; }
.nv .nv-pin span { font-family:var(--f-body); font-weight:800; color:var(--nv-fg); }
.nv .nv-pin.tag { border:2px solid var(--nv-acc); }
"""


# ------------------------------------------------------------------ colours
def colours(style):
    tok = style.get("tokens") or {}
    bg = tok.get("bg", "#111111")
    fg = tok.get("fg", "#f2f2f2")
    if DV.to_rgb(bg) is None:
        bg = "#111111"
    if DV.to_rgb(fg) is None:
        fg = "#f2f2f2"
    fill = tok.get("ink")
    if not fill or DV.to_rgb(fill) is None or DV.contrast(fill, bg) < 3.0:
        fill = fg
    on = None
    for key in ("paper", "bg", "card"):
        c = tok.get(key)
        if c and DV.to_rgb(c) is not None and DV.contrast(c, fill) >= 4.5:
            on = c
            break
    if on is None:
        if DV.contrast("#111111", fill) >= DV.contrast("#ffffff", fill):
            on = "#111111"
        else:
            on = "#ffffff"
    acc = tok.get("accent", fill)
    if DV.to_rgb(acc) is None or DV.contrast(acc, bg) < 2.0:
        acc = fill
    rgb = DV.to_rgb(bg)
    plate = f"rgba({int(rgb[0])},{int(rgb[1])},{int(rgb[2])},.78)"
    return {"bg": bg, "fg": fg, "fill": fill, "on": on, "acc": acc, "plate": plate, "plate_solid": bg}


def radius(style):
    """the style's chip radius (the same skin table the key-info effects use), capped to a pill."""
    sid = ""
    chain = style.get("_chain") or []
    if chain:
        sid = chain[0]
    try:
        p = pathlib.Path(__file__).with_name("fx") / "_kinfo.py"
        key = "h9fx__kinfo"
        import sys
        if key not in sys.modules:
            s = importlib.util.spec_from_file_location(key, p)
            sys.modules[key] = importlib.util.module_from_spec(s)
            s.loader.exec_module(sys.modules[key])
        skins = sys.modules[key].SKINS
    except Exception:
        skins = {}
    k = None
    for cand in chain:
        if cand in skins:
            k = skins[cand]
            break
    if k is None:
        return 10
    r = int(k.get("rs", 10))
    if r > 28:
        r = 28
    return r


def world_colours(w):
    """navigator colours on a chapter ground (scripts/h9/device.py colour worlds)."""
    bg = w["bg"]
    fg = w["fg"]
    acc = w.get("accent", fg)
    if DV.to_rgb(acc) is None or DV.contrast(acc, bg) < 2.0:
        acc = fg
    rgb = DV.to_rgb(bg)
    plate = f"rgba({int(rgb[0])},{int(rgb[1])},{int(rgb[2])},.78)"
    return {"fg": fg, "fill": fg, "on": bg, "acc": acc, "plate": plate, "plate_solid": bg}


def chapter_colours(X, video, beats, times, style):
    """with chapter grounds (meta.device / beat "chapter": {...}) the navigator re-inks at every chapter, so its accent
    never vanishes on an accent-coloured ground."""
    try:
        chs = DV.chapters(video, beats, times, style)
    except Exception:
        chs = None
    if not chs:
        return
    for ch in chs["list"]:
        c = world_colours(ch["world"])
        props = []
        for key, var in (("fg", "--nv-fg"), ("fill", "--nv-fill"), ("on", "--nv-on"), ("acc", "--nv-acc"), ("plate", "--nv-plate"), ("plate_solid", "--nv-plate-solid")):
            props.append(f'"{var}":"{c[key]}"')
        X.tw(f'tl.set("#root", {{{", ".join(props)}}}, {max(0.001, ch["t0"] - 0.05):.3f});')
        if ch["k"] == 0:
            X._nv_col = dict(X._nv_col, fg=c["fg"], on=c["on"])


# ------------------------------------------------------------------ text
def text_w(s, px, mono=False, ls=0.0):
    t = fit.plain(s)
    return (fit.width(t, mono) + ls * len(t)) * px


def trunc(s, max_w, px, mono=False):
    """s cut with an ellipsis so it is at most max_w px wide at px."""
    s = fit.plain(s)
    if text_w(s, px, mono) <= max_w:
        return s
    cut = ""
    for ch in s:
        if text_w(cut + ch + "…", px, mono) > max_w:
            break
        cut += ch
    return cut.rstrip() + "…"


def norm(s):
    return re.sub(r"[\s*|·・:：，,。.!！?？]", "", str(s or ""))


# ------------------------------------------------------------------ plan
def spec_of(meta):
    nv = meta.get("nav")
    if not nv:
        return None
    if isinstance(nv, list):
        nv = {"steps": nv}
    if not isinstance(nv, dict):
        raise SystemExit("meta.nav must be {\"steps\": [...]} or a list of step names")
    steps = []
    for s in nv.get("steps") or []:
        if isinstance(s, dict):
            s = s.get("text") or s.get("label") or s.get("title") or ""
        s = str(s).strip()
        if s:
            steps.append(s)
    if len(steps) < 2:
        raise SystemExit(f"meta.nav needs 2–8 steps, got {len(steps)}")
    if len(steps) > 8:
        raise SystemExit(f"meta.nav takes at most 8 steps, got {len(steps)} — group them into chapters of ≤ 8 steps")
    return {"steps": steps, "numbered": nv.get("numbered", True) is not False}


def step_of(b, steps, i):
    v = b.get("step")
    if v is None or v is False or v == "":
        return None
    if isinstance(v, bool):
        raise SystemExit(f"beat {i}: step must be a number (1-based) or a step name")
    if isinstance(v, (int, float)):
        k = int(v)
        if k < 1 or k > len(steps):
            raise SystemExit(f"beat {i}: step {k} is outside 1–{len(steps)}")
        return k - 1
    s = str(v).strip()
    if s.isdigit():
        return step_of(dict(b, step=int(s)), steps, i)
    for k, name in enumerate(steps):
        if name == s:
            return k
    for k, name in enumerate(steps):
        if norm(name) == norm(s) or norm(name).startswith(norm(s)) or norm(s) in norm(name):
            return k
    raise SystemExit(f"beat {i}: step {s!r} is not one of {', '.join(steps)}")


def pin_of(b):
    v = b.get("pin")
    if not v:
        return None
    if isinstance(v, str):
        return {"index": None, "text": v.strip()}
    if isinstance(v, dict):
        txt = str(v.get("text") or v.get("title") or "").strip()
        if not txt:
            return None
        idx = v.get("index")
        if isinstance(idx, str) and idx.strip().isdigit():
            idx = int(idx)
        if not isinstance(idx, int) or isinstance(idx, bool):
            idx = None
        return {"index": idx, "text": txt}
    return None


def has_text(obj, want):
    """True when `want` appears as (part of) a string anywhere in obj (a beat's parameters)."""
    if isinstance(obj, str):
        n = norm(obj)
        return bool(want) and (n == want or n.startswith(want) or (len(want) >= 2 and want in n))
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("line", "src", "topic", "scene", "fx", "tr", "t", "d", "label", "pin", "step", "caption", "id"):
                continue
            if has_text(v, want):
                return True
        return False
    if isinstance(obj, (list, tuple)):
        for v in obj:
            if has_text(v, want):
                return True
    return False


def slot(style, portrait):
    s = style.get("nav_slot") or {}
    key = "9:16" if portrait else "16:9"
    out = {}
    if isinstance(s.get(key), dict):
        out = dict(s[key])
    return out


def hide_list(style):
    s = style.get("nav_slot") or {}
    if isinstance(s.get("hide"), list):
        return list(s["hide"])
    out = list(HEADER_COMMON)
    for sid in style.get("_chain") or []:
        for sel in HEADER.get(sid, []):
            if sel not in out:
                out.append(sel)
    return out


def device_top(X, video):
    """with meta.device on, the row sits under the device's top chrome (its content box top)."""
    meta = video.get("meta") or {}
    spec = DV.device_spec(meta)
    if spec["kind"] == "none":
        return None
    return DV.content_box(X, spec["kind"], False)[1]


# ------------------------------------------------------------------ build
def build(X, video, beats, times, D, style, cids=None):
    """the navigator and pin clips, their moves and the header hand-over. Nothing when the film uses neither."""
    meta = video.get("meta") or {}
    spec = spec_of(meta)
    pins = []
    any_pin = False
    for b in beats:
        p = pin_of(b)
        pins.append(p)
        if p:
            any_pin = True
    if not spec and not any_pin:
        return
    steps = spec["steps"] if spec else []
    act = []
    for i, b in enumerate(beats):
        if spec:
            act.append(step_of(b, steps, i))
        else:
            if b.get("step") is not None:
                raise SystemExit(f"beat {i} has a step but the film has no meta.nav")
            act.append(None)
    col = colours(style)
    X._nv_col = col
    r = radius(style)
    X.css("nv-base", CSS)
    X.css("nv-vars", f"#root {{ --nv-fg:{col['fg']}; --nv-fill:{col['fill']}; --nv-on:{col['on']}; --nv-acc:{col['acc']};"
                     f" --nv-plate:{col['plate']}; --nv-plate-solid:{col['plate_solid']}; --nv-r:{r}px; }}")
    chapter_colours(X, video, beats, times, style)
    P = X.portrait
    sl = slot(style, P)
    top_dev = device_top(X, video)
    geo = {}
    if P:
        y = int(sl.get("y", 208))
        if top_dev is not None:
            y = max(y, top_dev + 6)
        geo = {"hd_y": y, "hd_x": 80, "rail_y0": max(320, y + 76 + 36), "rail_y1": 1300, "pin_y": y, "pin_y_nav": y + 92}
        if any_pin and spec:
            geo["rail_y0"] = max(geo["rail_y0"], y + 92 + 60 + 40)     # the pin sits under the header chip: the rail starts below it
    else:
        y = int(sl.get("y", 62))
        if top_dev is not None:
            y = max(y, top_dev + 4)
        geo = {"row_y": y, "x0": 110, "x1": X.W - 110, "pin_y": max(60, y - 2), "pin_x": 110}
    # runs of consecutive step beats
    runs = []
    for i in range(len(beats)):
        if act[i] is None:
            continue
        if runs and runs[-1]["i1"] == i - 1:
            runs[-1]["i1"] = i
        else:
            runs.append({"i0": i, "i1": i})
    for ru in runs:
        ru["t0"] = times[ru["i0"]][0]
        ru["t1"] = times[ru["i1"]][0] + times[ru["i1"]][1]
    nav_on = []
    for i in range(len(beats)):
        nav_on.append(act[i] is not None)
    # pin reserve on the 16:9 row
    pin_w16 = 0
    if not P and spec and any_pin:
        for i in range(len(beats)):
            if pins[i] and nav_on[i]:
                w = pin_tag_w(X, pins[i])
                pin_w16 = max(pin_w16, w)
    if not P and spec:
        budget = geo["x1"] - geo["x0"]
        if pin_w16:
            budget -= pin_w16 + 28
        lay = chip_layout(steps, spec["numbered"], budget)
        widest = 0
        for a in range(len(steps)):
            widest = max(widest, row_width(lay, a))
        geo["tag_x"] = geo["x0"] + widest + 28
    for k, ru in enumerate(runs):
        if P:
            rail_run(X, k, ru, act, times, steps, spec["numbered"], geo, D)
        else:
            row_run(X, k, ru, act, times, steps, spec["numbered"], geo, D, pin_w16)
    pin_layer(X, beats, times, pins, nav_on, geo, D, cids or [], P)
    # the header hand-over: while the navigator or a pin is up, the style's own header row steps aside
    hold = []
    for i in range(len(beats)):
        on = nav_on[i] or bool(pins[i])
        if on and hold and hold[-1][1] >= times[i][0] - 0.01:
            hold[-1][1] = times[i][0] + times[i][1]
        elif on:
            hold.append([times[i][0], times[i][0] + times[i][1]])
    if hold:
        sels = []
        for s in hide_list(style):
            sels.append(f'#root[data-h9nav="1"] {s}')
        X.css("nv-hide", ", ".join(sels) + " { visibility:hidden !important; }")
        # every style's page frame around an effect (.ctx: kicker row, status row, window bar, effect tag …) gives up
        # the band above the navigator / pin bottom; its caption and footer further down stay
        band = geo["row_y"] + ROW_H + 30 if not P else (geo["pin_y_nav"] + 60 + 12 if any_pin and spec else geo["hd_y"] + 76 + 12)
        X.css("nv-band", f'#root[data-h9nav="1"] .clip.ctx {{ clip-path:inset({band}px 0 0 0); }}')
        for a, b in hold:
            X.tw(f'tl.set("#root", {{attr:{{"data-h9nav":"1"}}}}, {max(0.001, a - 0.001):.3f});')
            X.tw(f'tl.set("#root", {{attr:{{"data-h9nav":"0"}}}}, {b:.3f});')
    if P and runs:
        # 9:16: the rail owns x 34–64, so the beat's page is scaled to 0.95 about a point on the right-hand safe line for
        # the run: nothing moves towards the platform buttons and the left margin clears the rail (edges fade, no seam)
        X.css("nv-rail-room", f'#root[data-h9rail="1"] :is(.clip.scene > .stage, .fx.scr-root > *, .fx.mx-root > *) {{ scale:{RAIL_SCALE}; transform-origin:1000px 1600px;'
              ' -webkit-mask-image:linear-gradient(90deg, transparent 0, #000 20px), linear-gradient(180deg, transparent 0, #000 40px, #000 calc(100% - 40px), transparent 100%);'
              ' -webkit-mask-composite:source-in; mask-composite:intersect; }')
        for ru in runs:
            X.tw(f'tl.set("#root", {{attr:{{"data-h9rail":"1"}}}}, {max(0.001, ru["t0"] - 0.001):.3f});')
            X.tw(f'tl.set("#root", {{attr:{{"data-h9rail":"0"}}}}, {ru["t1"]:.3f});')


# ------------------------------------------------------------------ 16:9 row
PAD = 22
GAP_IN = 12
GAP = 16
IPX = 26
ROW_H = 68
PX_SIZES = (34, 32, 30, 28)    # label px: 34, shrinking to the 28 px floor before any ellipsis


def chip_layout(steps, numbered, budget):
    """the row's look: {"mode", "labels", "px", "states"}; states(a) = [(x, w, label shown)] with step a active.
    full     every chip carries its label: 34 px, shrinking to 28 px, else every label longer than a common cap is
             ellipsized (while that still leaves ≥ 3 glyphs)
    compact  too many long labels: the inactive chips shrink to their index ("03"), the active chip carries its
             label; the row reflows when the active step changes"""
    idx_w = text_w("00", IPX, mono=True)
    fixed = 2 * PAD + (idx_w + GAP_IN if numbered else 0)
    n = len(steps)
    for px in PX_SIZES:
        ws = []
        for s_ in steps:
            ws.append(fixed + text_w(s_, px, ls=0.02))
        if sum(ws) + GAP * (n - 1) <= budget:
            return full_layout(list(steps), ws, px)
    px = PX_SIZES[-1]
    room = budget - GAP * (n - 1) - fixed * n
    natural = []
    for s_ in steps:
        natural.append(text_w(s_, px, ls=0.02))
    lo = 0.0
    hi = max(natural)
    for _ in range(40):
        mid = (lo + hi) / 2
        tot = 0.0
        for w in natural:
            tot += min(w, mid)
        if tot <= room:
            lo = mid
        else:
            hi = mid
    if lo >= px * 4.0:
        labels = []
        ws = []
        for s_ in steps:
            lab = trunc(s_, lo / 1.02, px)
            labels.append(lab)
            ws.append(fixed + text_w(lab, px, ls=0.02))
        return full_layout(labels, ws, px)
    # compact
    px = PX_SIZES[0]
    small = 2 * PAD + idx_w
    big_room = budget - GAP * (n - 1) - small * (n - 1) - (2 * PAD + idx_w + GAP_IN)
    labels = []
    for s_ in steps:
        labels.append(trunc(s_, big_room / 1.02, px))

    def states(a):
        out = []
        x = 0.0
        for j in range(n):
            if j == a:
                w = 2 * PAD + idx_w + GAP_IN + text_w(labels[j], px, ls=0.02)
                out.append((round(x), round(w), True))
            else:
                w = small
                out.append((round(x), round(w), False))
            x += w + GAP
        return out
    return {"mode": "compact", "labels": labels, "px": px, "states": states}


def full_layout(labels, ws, px):
    pos = []
    x = 0.0
    for w in ws:
        pos.append((round(x), round(w), True))
        x += w + GAP

    def states(a):
        return pos
    return {"mode": "full", "labels": labels, "px": px, "states": states}


def row_width(lay, a):
    st = lay["states"](a)
    return st[-1][0] + st[-1][1]


def pin_tag_w(X, pin):
    px = 34
    w = 2 * 18 + text_w(pin["text"], px)
    if pin.get("index"):
        w += 12 + text_w(f"{pin['index']:02d}", 26, mono=True)
    return min(round(w), PIN_TAG_MAX)


PIN_TAG_MAX = 460


def row_run(X, k, ru, act, times, steps, numbered, geo, D, pin_w):
    x0 = geo["x0"]
    budget = geo["x1"] - x0
    if pin_w:
        budget -= pin_w + 28
    lay = chip_layout(steps, numbered, budget)
    px = lay["px"]
    compact = lay["mode"] == "compact"
    col = X._nv_col
    H = ROW_H
    a0 = act[ru["i0"]]
    st0 = lay["states"](a0)
    parts = []
    plates = []      # the chips' grounds sit under the pill, the chips' labels over it (three layers)
    for j in range(len(steps)):
        x, w, shown = st0[j]
        lab = lay["labels"][j]
        X.used_text.update(lab + f"{j + 1:02d}…")
        idx = f"<b>{j + 1:02d}</b>" if (numbered or compact) else ""
        sp = f"font-size:{px}px; max-width:{text_w(lab, px, ls=0.02) + 4:.0f}px"
        if idx:
            sp += f"; margin-left:{GAP_IN}px"
        if not shown:
            sp = f"font-size:{px}px; margin-left:0; max-width:0; opacity:0; overflow:hidden"
        plates.append(f'<i class="nv-pl" data-k="{j}" style="left:{x}px; width:{w}px; height:{H}px"></i>')
        parts.append(f'<div class="nv-chip" data-k="{j}" style="left:{x}px; width:{w}px; height:{H}px">'
                     f'<i class="nv-bd"></i><i class="nv-fl"></i>{idx}<span style="{sp}">{X.rich(lab)}</span><i class="nv-u"></i></div>')
    pill = f'<div class="nv-pill" style="width:{st0[a0][1]}px; height:{H}px"></div>'
    inner = f'<div class="nv-row" style="left:{x0}px; top:{geo["row_y"]}px; --nv-ipx:{IPX}px">{"".join(plates)}{pill}{"".join(parts)}</div>'
    cid = f"nav{k}"
    t0 = ru["t0"]
    t1 = ru["t1"] if ru["t1"] < D - 0.05 else D
    X.clip(cid, t0, t1 - t0, inner, "nv nv16", Z_NAV, track=15 + k % 2, attrs='data-layout-allow-overlap')
    S = f"#{cid}"
    # first appearance: the chips rise out of their own masks, 2 frames apart; the pill grows from the active chip
    # (the mask sits on the row, not on each chip: a clip-path on a chip would make it its own stacking context and the
    # sliding pill would then cover the active label)
    X.tw(f'tl.fromTo("{S} .nv-row", {{clipPath:"inset(-20px -40px 100% -40px)"}}, {{clipPath:"inset(-20px -40px -30px -40px)", duration:0.4, ease:"expo.out", immediateRender:true}}, {t0 + 0.04:.3f});')
    X.tw(f'tl.set("{S} .nv-row", {{clipPath:"none"}}, {t0 + 0.46:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-chip", {{y:40}}, {{y:0, duration:0.36, ease:"expo.out", stagger:{2 * F:.4f}, immediateRender:true}}, {t0 + 0.04:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-pl", {{y:40}}, {{y:0, duration:0.36, ease:"expo.out", stagger:{2 * F:.4f}, immediateRender:true}}, {t0 + 0.04:.3f});')
    # initial transforms are GSAP state, not CSS (a CSS transform under a GSAP transform tween fails the HyperFrames lint)
    X.tw(f'tl.set("{S} .nv-u", {{scaleX:0, immediateRender:true}}, {t0:.3f});')
    X.tw(f'tl.set("{S} .nv-pill", {{x:{st0[a0][0]}, immediateRender:true}}, {t0:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-pill", {{scaleX:0}}, {{scaleX:1, duration:0.34, ease:"expo.out", immediateRender:true}}, {t0 + 0.04 + 2 * F * a0:.3f});')
    set_state(X, S, a0, t0 + 0.04 + 2 * F * a0, col, instant=True)
    for j in range(a0):
        X.tw(f'tl.set("{S} .nv-chip[data-k=\'{j}\'] .nv-u", {{scaleX:1}}, {t0:.3f});')
    prev = a0
    for i in range(ru["i0"] + 1, ru["i1"] + 1):
        cur = act[i]
        if cur == prev:
            continue
        t = times[i][0]
        sa = lay["states"](prev)
        sb = lay["states"](cur)
        ax = sa[prev][0]
        bx = sb[cur][0]
        bw = sb[cur][1]
        over = bx + (bx - ax) * 0.06
        # the pill travels: 7 frames to 6 % past the target, 3 frames back
        X.tw(f'tl.to("{S} .nv-pill", {{x:{over:.1f}, width:{bw}, duration:{7 * F:.3f}, ease:"power3.out"}}, {t - 2 * F:.3f});')
        X.tw(f'tl.to("{S} .nv-pill", {{x:{bx}, duration:{3 * F:.3f}, ease:"sine.inOut"}}, {t + 5 * F:.3f});')
        if compact:
            # the row reflows with the pill: chips slide to their new places, the old label folds, the new one opens
            for j in range(len(steps)):
                if sa[j][:2] != sb[j][:2]:
                    # x (a transform) from the chip's first place, not `left`: layout properties snap to whole pixels
                    X.tw(f'tl.to("{S} .nv-chip[data-k=\'{j}\'], {S} .nv-pl[data-k=\'{j}\']", {{x:{sb[j][0] - st0[j][0]}, width:{sb[j][1]}, duration:{10 * F:.3f}, ease:"power3.inOut"}}, {t - 2 * F:.3f});')
            lw = text_w(lay["labels"][cur], px, ls=0.02) + 4
            # the label fades while the chip's width moves; its own box (max-width / margin) switches once, unseen
            X.tw(f'tl.to("{S} .nv-chip[data-k=\'{prev}\'] > span", {{opacity:0, duration:{5 * F:.3f}, ease:"power2.in"}}, {t - 2 * F:.3f});')
            X.tw(f'tl.set("{S} .nv-chip[data-k=\'{prev}\'] > span", {{maxWidth:0, marginLeft:0}}, {t + 3 * F:.3f});')
            X.tw(f'tl.set("{S} .nv-chip[data-k=\'{cur}\'] > span", {{maxWidth:{lw:.0f}, marginLeft:{GAP_IN}}}, {t + 3 * F:.3f});')
            X.tw(f'tl.to("{S} .nv-chip[data-k=\'{cur}\'] > span", {{opacity:1, duration:{6 * F:.3f}, ease:"power3.out"}}, {t + 3 * F:.3f});')
        # the outgoing chip keeps its own fill until the pill has left it, so no frame shows a half-painted chip
        X.tw(f'tl.set("{S} .nv-chip[data-k=\'{prev}\'] .nv-fl", {{opacity:1}}, {t - 2 * F:.3f});')
        X.tw(f'tl.set("{S} .nv-chip[data-k=\'{prev}\'] .nv-fl", {{opacity:0}}, {t + 4 * F:.3f});')
        set_state(X, S, cur, t + 2 * F, col, prev=prev)
        if cur > prev:
            for j in range(prev, cur):
                X.tw(f'tl.to("{S} .nv-chip[data-k=\'{j}\'] .nv-u", {{scaleX:1, duration:0.3, ease:"power3.out"}}, {t + 3 * F + (j - prev) * F:.3f});')
        else:
            for j in range(cur, prev):
                X.tw(f'tl.to("{S} .nv-chip[data-k=\'{j}\'] .nv-u", {{scaleX:0, transformOrigin:"100% 50%", duration:0.24, ease:"power2.in"}}, {t:.3f});')
        X.sfx(t - 2 * F, "click", 0.25)
        prev = cur
    if t1 < D:
        X.tw(f'tl.to("{S} .nv-row > *", {{y:-110, duration:0.2, ease:"power3.in", stagger:{F / 3:.4f}}}, {t1 - 0.24:.3f});')


def set_state(X, S, cur, t, col, instant=False, prev=None):
    """the active chip's text takes the fill's paper colour (the others go back to the outline look). The colours are
    the --nv-* variables, so a chapter change re-inks them."""
    dur = 0.01 if instant else 0.16
    if prev is not None:
        X.tw(f'tl.set("{S} .nv-chip[data-k=\'{prev}\']", {{"--nv-c":"var(--nv-fg)"}}, {t:.3f});')
        X.tw(f'tl.to("{S} .nv-chip[data-k=\'{prev}\']", {{"--nv-o":0.45, duration:{dur}}}, {t:.3f});')
        X.tw(f'tl.to("{S} .nv-chip[data-k=\'{prev}\'] .nv-bd", {{opacity:0.45, duration:{dur}}}, {t:.3f});')
    X.tw(f'tl.set("{S} .nv-chip[data-k=\'{cur}\']", {{"--nv-c":"var(--nv-on)"}}, {t:.3f});')
    X.tw(f'tl.to("{S} .nv-chip[data-k=\'{cur}\']", {{"--nv-o":1, duration:{dur}}}, {t:.3f});')
    X.tw(f'tl.to("{S} .nv-chip[data-k=\'{cur}\'] .nv-bd", {{opacity:0, duration:{dur}}}, {t:.3f});')


# ------------------------------------------------------------------ 9:16 rail + header chip
def header_text(k, n, label, numbered):
    if numbered:
        return f"{k + 1:02d} / {n:02d}", label
    return "", label


def rail_run(X, k, ru, act, times, steps, numbered, geo, D):
    n = len(steps)
    y0 = geo["rail_y0"]
    y1 = geo["rail_y1"]
    ys = []
    for j in range(n):
        ys.append(round(y0 + (y1 - y0) * j / (n - 1)))
    rail = []
    rail.append(f'<i class="nv-track" style="top:{ys[0] + 11}px; height:{ys[-1] - ys[0]}px"></i>')
    rail.append(f'<i class="nv-run" style="top:{ys[0] + 11}px; height:{ys[-1] - ys[0]}px"></i>')
    for j in range(n):
        rail.append(f'<div class="nv-node" data-k="{j}" style="top:{ys[j]}px"><i></i></div>')
    # header chip: one line per step in the run (only the visited ones get built)
    seen = []
    for i in range(ru["i0"], ru["i1"] + 1):
        if act[i] not in seen:
            seen.append(act[i])
    max_w = 960 - geo["hd_x"]
    # one header size for the run: 42 px, shrinking to 34 px for the longest visited label, then an ellipsis
    hd_px = 42
    for cand in (42, 40, 38, 36, 34):
        hd_px = cand
        ok = True
        for j in seen:
            num, label = header_text(j, n, steps[j], numbered)
            fixed = 52 + (text_w(num, 34, mono=True) + 16 + text_w("·", cand) + 16 if numbered else 0)
            if fixed + text_w(label, cand) > max_w - 6:
                ok = False
        if ok:
            break
    lines = []
    widths = {}
    for j in seen:
        num, label = header_text(j, n, steps[j], numbered)
        fixed = 52 + (text_w(num, 34, mono=True) + 16 + text_w("·", hd_px) + 16 if numbered else 0)
        lab = trunc(label, max_w - fixed - 6, hd_px)
        X.used_text.update(num + "·…" + lab)
        w = round(fixed + text_w(lab, hd_px))
        widths[j] = w
        inner = ""
        if numbered:
            inner += f"<b>{X.rich(num)}</b><em>·</em>"
        inner += f"<span>{X.rich(lab)}</span>"
        lines.append(f'<div class="nv-ln" data-k="{j}">{inner}</div>')
    a0 = act[ru["i0"]]
    hd = f'<div class="nv-hd" style="left:{geo["hd_x"]}px; top:{geo["hd_y"]}px; width:{widths[a0]}px; --hd-px:{hd_px}px">{"".join(lines)}</div>'
    inner = f'<div class="nv-rail" data-safe="ignore" style="left:38px; top:0; width:22px">{"".join(rail)}</div>{hd}'
    cid = f"nav{k}"
    t0 = ru["t0"]
    t1 = ru["t1"] if ru["t1"] < D - 0.05 else D
    X.clip(cid, t0, t1 - t0, inner, "nv nv9", Z_NAV, track=15 + k % 2, attrs='data-layout-allow-overlap')
    S = f"#{cid}"
    span = ys[-1] - ys[0]
    # first appearance: the header chip rises out of its mask, the nodes drop in 2 frames apart, the run fills to the step
    for j in seen:      # the header lines' resting offsets (GSAP state, not a CSS transform)
        X.tw(f'tl.set("{S} .nv-ln[data-k=\'{j}\']", {{y:{0 if j == act[ru["i0"]] else 80}, immediateRender:true}}, {ru["t0"]:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-hd", {{y:30, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 0% 0)", duration:0.36, ease:"expo.out", immediateRender:true}}, {t0 + 0.04:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-node", {{y:-26, scale:0.4, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.3, ease:"back.out(1.6)", stagger:{2 * F:.4f}, immediateRender:true}}, {t0 + 0.04:.3f});')
    X.tw(f'tl.fromTo("{S} .nv-track", {{scaleY:0, transformOrigin:"50% 0"}}, {{scaleY:1, duration:{0.3 + 2 * F * n:.2f}, ease:"power2.out", immediateRender:true}}, {t0 + 0.04:.3f});')
    fill0 = (ys[a0] - ys[0]) / span if span else 0
    t_fill = t0 + 0.1 + 2 * F * n
    X.tw(f'tl.fromTo("{S} .nv-run", {{scaleY:0}}, {{scaleY:{fill0:.4f}, duration:0.4, ease:"power2.inOut", immediateRender:true}}, {t_fill:.3f});')
    for j in range(a0 + 1):
        X.tw(f'tl.fromTo("{S} .nv-node[data-k=\'{j}\'] i", {{scale:0}}, {{scale:1, duration:0.2, ease:"back.out(2)", immediateRender:true}}, {t_fill + 0.4 * (j / max(1, a0)) if a0 else t_fill:.3f});')
    X.tw(f'tl.to("{S} .nv-node[data-k=\'{a0}\']", {{scale:1.364, duration:0.2, ease:"back.out(2)"}}, {t_fill + 0.4:.3f});')
    prev = a0
    for i in range(ru["i0"] + 1, ru["i1"] + 1):
        cur = act[i]
        if cur == prev:
            continue
        t = times[i][0]
        fill = (ys[cur] - ys[0]) / span if span else 0
        # the fill runs down (or back up) the rail in 9 frames; the new node fills when it arrives
        X.tw(f'tl.to("{S} .nv-run", {{scaleY:{fill:.4f}, duration:{9 * F:.3f}, ease:"power2.inOut"}}, {t - 2 * F:.3f});')
        X.tw(f'tl.to("{S} .nv-node[data-k=\'{prev}\']", {{scale:1, duration:0.16, ease:"power2.out"}}, {t - 2 * F:.3f});')
        if cur > prev:
            for j in range(prev + 1, cur + 1):
                land = t - 2 * F + 9 * F * (ys[j] - ys[prev]) / max(1, ys[cur] - ys[prev])
                X.tw(f'tl.to("{S} .nv-node[data-k=\'{j}\'] i", {{scale:1, duration:0.16, ease:"back.out(2)"}}, {land - 2 * F:.3f});')
        else:
            for j in range(cur + 1, prev + 1):
                X.tw(f'tl.to("{S} .nv-node[data-k=\'{j}\'] i", {{scale:0, duration:0.16, ease:"power2.in"}}, {t - 2 * F:.3f});')
        X.tw(f'tl.to("{S} .nv-node[data-k=\'{cur}\']", {{scale:1.364, duration:0.2, ease:"back.out(2)"}}, {t + 6 * F:.3f});')
        # the header text rolls up like an odometer: the old line leaves upward, the new one rises in (9 frames)
        X.tw(f'tl.to("{S} .nv-ln[data-k=\'{prev}\']", {{y:-80, duration:{9 * F:.3f}, ease:"power3.inOut"}}, {t - 2 * F:.3f});')
        X.tw(f'tl.fromTo("{S} .nv-ln[data-k=\'{cur}\']", {{y:80}}, {{y:0, duration:{9 * F:.3f}, ease:"power3.inOut", immediateRender:false}}, {t - 2 * F:.3f});')
        X.tw(f'tl.to("{S} .nv-hd", {{width:{widths[cur]}, duration:{9 * F:.3f}, ease:"power3.inOut"}}, {t - 2 * F:.3f});')
        X.sfx(t - 2 * F, "click", 0.25)
        prev = cur
    if t1 < D:
        X.tw(f'tl.to("{S} .nv-hd", {{y:-90, duration:0.2, ease:"power3.in"}}, {t1 - 0.22:.3f});')
        X.tw(f'tl.to("{S} .nv-rail", {{x:-90, duration:0.2, ease:"power3.in"}}, {t1 - 0.22:.3f});')


# ------------------------------------------------------------------ pin
PIN_JS = r"""
(()=>{
  const PIN = __PIN__, SCOPE = __SCOPE__, WANT = __WANT__, T0 = __T0__, FR = __FR__, FPS = __FPS__;
  const root = document.getElementById("root");
  const pin = document.querySelector(PIN);
  if (!pin) return;
  function nrm(s) { return String(s || "").replace(/[\s*|·・:：，,。.!！?？]/g, ""); }
  function offs(el) {
    let x = 0, y = 0, e = el;
    while (e && e !== root && e.id !== "canvas") { x += e.offsetLeft || 0; y += e.offsetTop || 0; e = e.offsetParent; }
    return { x: x, y: y, w: el.offsetWidth || 1, h: el.offsetHeight || 1 };
  }
  function find() {
    const els = [];
    for (const n of document.querySelectorAll('[id^="' + SCOPE + '"]')) {
      if (n.closest(".nv")) continue;
      els.push(n);
      for (const k of n.querySelectorAll("*")) els.push(k);
    }
    let best = null, area = 1e12, part = null, parea = 1e12;
    for (const el of els) {
      if (el.closest(".ctx, script, style, [data-safe='ignore']")) continue;
      const t = nrm(el.textContent);
      if (!t) continue;
      const a = (el.offsetWidth || 0) * (el.offsetHeight || 0);
      if (!a) continue;
      if (t === WANT && a < area) { best = el; area = a; }
      else if (t.indexOf(WANT) === 0 && a < parea) { part = el; parea = a; }
    }
    return best || part;
  }
  let m = null, tried = false;
  function measure() {
    tried = true;
    const src = find();
    if (!src) return;
    const a = offs(src);
    const span = pin.querySelector("span");
    const b = offs(span || pin);
    const pb = offs(pin);
    const s = Math.max(0.4, Math.min(4, a.h / b.h));
    // translate the pin so its text box sits on the source text box at scale s (origin: the pin's top-left)
    m = { dx: a.x - (pb.x + (b.x - pb.x) * s), dy: a.y + (a.h - b.h * s) / 2 - (pb.y + (b.y - pb.y) * s), s: s };
  }
  function ease(u) { return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; }
  function draw(f) {
    if (!tried) measure();
    if (!m) { pin.style.transform = ""; return; }
    const u = ease(Math.max(0, Math.min(1, f / FR)));
    const s = m.s + (1 - m.s) * u;
    pin.style.transform = "translate(" + (m.dx * (1 - u)).toFixed(1) + "px," + (m.dy * (1 - u)).toFixed(1) + "px) scale(" + s.toFixed(4) + ")";
  }
  const V = { f: 0 };
  tl.fromTo(V, { f: 0 }, { f: FR, duration: FR / FPS, ease: "none", immediateRender: false, onUpdate: () => draw(V.f) }, T0);
})();
"""


def pin_box(X, pin, P, tag):
    """(html inner, width, height, text px) of a pin."""
    if P:
        px = 46
        ipx = 32
        max_w = 960 - 80
        h = 60
        floor = 36
    elif tag:
        px = 34
        ipx = 26
        max_w = PIN_TAG_MAX
        h = ROW_H
        floor = 28
    else:
        px = 44
        ipx = 28
        max_w = 1100
        h = 64
        floor = 32
    idx = ""
    fixed = 36
    if pin.get("index"):
        idx = f"{int(pin['index']):02d}"
        fixed += 12 + text_w(idx, ipx, mono=True)
    room = max_w - fixed
    lab = pin["text"]
    if text_w(lab, px) > room:
        px2 = max(floor, int(px * room / text_w(lab, px)))
        if text_w(lab, px2) <= room:
            px = px2
        else:
            px = floor
            lab = trunc(lab, room, px)
    X.used_text.update(idx + lab + "…")
    w = round(fixed + text_w(lab, px)) + 2
    inner = (f"<b>{idx}</b>" if idx else "") + f'<span style="font-size:{px}px">{X.rich(lab)}</span>'
    return inner, w, h, px, ipx


def pin_layer(X, beats, times, pins, nav_on, geo, D, cids, P):
    """one clip per stretch of beats sharing a pin; the stretch's slot moves when the navigator comes or goes."""
    stretches = []
    for i in range(len(beats)):
        p = pins[i]
        if not p:
            continue
        if stretches and stretches[-1]["i1"] == i - 1 and norm(stretches[-1]["pin"]["text"]) == norm(p["text"]) \
                and stretches[-1]["pin"].get("index") == p.get("index"):
            stretches[-1]["i1"] = i
        else:
            stretches.append({"i0": i, "i1": i, "pin": p})
    for k, st in enumerate(stretches):
        i0 = st["i0"]
        i1 = st["i1"]
        t0 = times[i0][0]
        t1 = times[i1][0] + times[i1][1]
        if t1 > D - 0.05:
            t1 = D
        # where it sits on each beat of the stretch
        spots = []
        for i in range(i0, i1 + 1):
            spots.append(pin_spot(X, geo, nav_on[i], P, st["pin"]))
        tag0 = spots[0][2]
        inner, w, h, px, ipx = pin_box(X, st["pin"], P, tag0)
        x, y, _ = spots[0]
        cid = f"npin{k}"
        cls = "nv-pin tag" if tag0 else "nv-pin"
        body = f'<div class="{cls}" style="left:0; top:0; height:{h}px; --pn-ipx:{ipx}px; transform:none">{inner}</div>'
        out = 0.26
        X.clip(cid, t0, t1 - t0, f'<div class="nv-pslot" style="position:absolute; left:{x}px; top:{y}px">{body}</div>',
               "nv nvp", Z_NAV + 1, track=17 + k % 2, attrs='data-layout-allow-overlap')
        S = f"#{cid}"
        prev_beat = beats[i0 - 1] if i0 > 0 else None
        fly = False
        if prev_beat is not None and not pins[i0 - 1] and has_text(prev_beat, norm(st["pin"]["text"])) and cids and i0 - 1 < len(cids):
            fly = True
        if fly:
            # shared element: the header flies from its place in the list to the pin slot (12 frames)
            frames = 12
            js = (PIN_JS.replace("__PIN__", json.dumps(f"{S} .nv-pin")).replace("__SCOPE__", json.dumps(cids[i0 - 1]))
                  .replace("__WANT__", json.dumps(norm(st["pin"]["text"]), ensure_ascii=False)).replace("__T0__", f"{t0:.3f}")
                  .replace("__FR__", str(frames)).replace("__FPS__", f"{float(X.fps):.0f}"))
            X.tw(js)
            X.tw(f'tl.fromTo("{S} .nv-pin", {{backgroundColor:"rgba(0,0,0,0)"}}, {{backgroundColor:"var(--nv-plate)", duration:{frames * F:.3f}, ease:"power2.in", immediateRender:false}}, {t0:.3f});')
            X.sfx(t0, "whoosh_soft", 0.3)
        else:
            # it slides in from the left edge (behind a mask at its own left), the index snaps on first
            X.tw(f'tl.fromTo("{S} .nv-pin", {{x:-60, clipPath:"inset(0 100% 0 0)"}}, {{x:0, clipPath:"inset(0 -4% 0 0)", duration:0.4, ease:"expo.out", immediateRender:true}}, {t0 + 0.02:.3f});')
            X.tw(f'tl.fromTo("{S} .nv-pin b", {{yPercent:100}}, {{yPercent:0, duration:0.26, ease:"back.out(2)", immediateRender:true}}, {t0 + 0.08:.3f});')
        # the slot follows the navigator coming and going inside the stretch
        for j in range(1, len(spots)):
            if spots[j] == spots[j - 1]:
                continue
            nx, ny, ntag = spots[j]
            t = times[i0 + j][0]
            X.tw(f'tl.to("{S} .nv-pslot", {{x:{nx - spots[0][0]}, y:{ny - spots[0][1]}, duration:0.36, ease:"power3.inOut"}}, {t - 0.08:.3f});')
        if t1 < D:
            X.tw(f'tl.to("{S} .nv-pin", {{x:-140, clipPath:"inset(0 100% 0 0)", duration:0.2, ease:"power3.in"}}, {t1 - 0.22:.3f});')


def pin_spot(X, geo, nav, P, pin):
    """(x, y, tag) of the pin: tag = the small outlined form that follows the 16:9 row's last chip."""
    if P:
        if nav:
            return (80, geo["pin_y_nav"], False)
        return (80, geo["pin_y"], False)
    if nav:
        return (geo["tag_x"], geo["row_y"], True)
    return (geo["pin_x"], geo["pin_y"], False)
