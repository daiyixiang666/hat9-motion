"""fx4 · working windows for "how I do it" explainers: doc_edit · wave_align · qc_sheet · pair_check.

doc_edit     a document is typed in with a caret, then a few spans are struck and rewritten (track-changes style)
wave_align   a voice waveform; a playhead sweeps it and each caption chunk snaps up onto its span; a wrong word is fixed
qc_sheet     a contact sheet is scanned row by row, once per check; a failing frame is flagged, replaced and passes
pair_check   before / after panels; each point circles a region of the better panel, lights a word and dims the other

All four share one window chrome (title bar with three plain dots, a path line, a body) drawn from the style tokens
(--card --card-fg --accent --k-r --k-sh --k-bw …), so they re-skin with every style. Every motion is a pure function of
the timeline time (GSAP tweens, or one proxy tween whose onUpdate redraws from the time), so any frame renders on its
own. 16:9 and 9:16 each get their own composition; 1:1 / 4:5 / 3:4 reuse the 9:16 one through the canvas fit.
"""
import importlib.util
import math
import pathlib
import re
import sys
import zlib

if "h9fx__fx2" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fx2", pathlib.Path(__file__).with_name("_fx2.py"))
    sys.modules["h9fx__fx2"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx__fx2"])
A = sys.modules["h9fx__fx2"]
K = A.K

CSS = r"""
.w4 { font-family:var(--f-body); }
.w4 .w4-win { position:absolute; box-sizing:border-box; background:var(--card); color:var(--card-fg); border-radius:var(--k-r);
  box-shadow:var(--k-sh); outline:var(--k-bw) solid var(--k-ink); outline-offset:calc(var(--k-bw) * -1); overflow:hidden; }
.w4 .w4-bar { position:absolute; left:0; right:0; top:0; box-sizing:border-box; display:flex; align-items:center; gap:18px;
  background:color-mix(in srgb, var(--card-fg) 6%, var(--card)); border-bottom:1.5px solid color-mix(in srgb, var(--card-fg) 12%, var(--card)); }
.w4 .w4-dots { display:flex; gap:10px; flex:none; }
.w4 .w4-dots i { display:block; width:14px; height:14px; border-radius:50%; background:color-mix(in srgb, var(--card-fg) 26%, var(--card)); }
.ki.sk-pixel .w4 .w4-dots i, .ki.sk-poster .w4 .w4-dots i, .ki.sk-zine .w4 .w4-dots i { border-radius:0; }
.w4 .w4-path { flex:1 1 auto; min-width:0; font-family:var(--f-mono, var(--f-body)); white-space:nowrap; overflow:hidden; color:color-mix(in srgb, var(--card-fg) 52%, var(--card)); }
.w4 .w4-path b { font-weight:700; color:var(--card-fg); }
.w4 .w4-right { flex:none; font-family:var(--f-mono, var(--f-body)); white-space:nowrap; color:color-mix(in srgb, var(--card-fg) 60%, var(--card)); font-variant-numeric:tabular-nums; }
.w4 .w4-body { position:absolute; left:0; right:0; bottom:0; overflow:hidden; }

/* doc_edit */
.w4 .de-head { position:absolute; font-family:var(--f-mono, var(--f-body)); font-weight:700; white-space:nowrap; color:var(--mark); }
.w4 .de-clip { position:absolute; overflow:hidden; }
.w4 .de-doc { position:absolute; left:0; top:0; right:0; }
.w4 .de-para { position:absolute; left:0; right:0; }
.w4 .de-v { position:absolute; left:0; right:0; top:0; }
.w4 .de-row { position:absolute; left:0; white-space:pre; color:var(--card-fg); }
.w4 .de-row i { font-style:normal; }
.w4 .de-st { position:relative; }
.w4 .de-st::after { content:""; position:absolute; left:-2px; right:-2px; top:50%; height:max(3px, .085em); margin-top:-.02em; background:var(--bad);
  transform:scaleX(var(--p, 0)); transform-origin:0 50%; border-radius:2px; }
.w4 .de-in { background:color-mix(in srgb, var(--accent) 24%, transparent); box-shadow:inset 0 -.09em 0 var(--accent); border-radius:3px; }
.w4 .de-caret { display:inline-block; width:3px; height:1.12em; margin:0 -1.5px; vertical-align:-.2em; background:var(--accent); border-radius:1px; }
.w4 .de-save { display:inline-flex; align-items:center; gap:8px; }
.w4 .de-save s { display:block; width:12px; height:12px; border-radius:50%; background:var(--bad); text-decoration:none; }
.w4 .de-col { position:absolute; }
.w4 .de-kick { position:absolute; font-family:var(--k-kf); font-weight:700; letter-spacing:.14em; color:var(--muted); white-space:nowrap; }
.w4 .de-verb { position:absolute; left:0; right:0; }
.w4 .de-verb .g { position:absolute; left:0; top:0; font-family:var(--f-display); font-weight:900; line-height:1; color:var(--muted); white-space:nowrap; }
.w4 .de-verb .dt { position:absolute; font-weight:700; color:var(--muted); white-space:nowrap; }
.w4 .de-verb .rule { position:absolute; left:0; height:6px; background:var(--accent); transform-origin:0 50%; border-radius:3px; }
.w4 .de-verb .ok { position:absolute; color:var(--accent); opacity:0; }
.w4 .de-count { position:absolute; white-space:nowrap; }
.w4 .de-count small { display:block; font-family:var(--k-kf); font-weight:700; letter-spacing:.12em; color:var(--muted); }
.w4 .de-count b { display:block; font-family:var(--f-num, var(--f-display)); font-weight:900; line-height:1; color:var(--fg); font-variant-numeric:tabular-nums; }
.w4 .w4-chip { position:absolute; display:inline-flex; align-items:center; gap:10px; white-space:nowrap; box-sizing:border-box; font-weight:800;
  border-radius:var(--k-rs); color:var(--fg); background:color-mix(in srgb, var(--fg) 9%, var(--bg)); border:1.5px solid color-mix(in srgb, var(--fg) 22%, var(--bg)); }
.w4 .w4-chip .ic { display:inline-flex; color:var(--accent); }
.w4 .de-vchip { position:absolute; box-sizing:border-box; display:flex; align-items:center; gap:14px; white-space:nowrap; border-radius:var(--k-rs);
  background:color-mix(in srgb, var(--fg) 7%, var(--bg)); border:2px solid color-mix(in srgb, var(--fg) 18%, var(--bg)); color:var(--muted); }
.w4 .de-vchip .g { font-family:var(--f-display); font-weight:900; line-height:1; }
.w4 .de-vchip .dt { font-weight:700; }
.w4 .de-vchip .ok { color:var(--accent); opacity:0; display:inline-flex; }

/* wave_align */
.w4 .wa-lane { position:absolute; }
.w4 .wa-wave { position:absolute; left:0; top:0; overflow:visible; }
.w4 .wa-wave rect { fill:var(--accent); }
.w4 .wa-base { opacity:.28; }
.w4 .wa-mid { position:absolute; left:0; right:0; height:1.5px; background:color-mix(in srgb, var(--card-fg) 16%, var(--card)); }
.w4 .wa-ph { position:absolute; width:3px; margin-left:-1.5px; background:var(--card-fg); border-radius:2px; }
.w4 .wa-ph::before { content:""; position:absolute; left:50%; top:-10px; width:16px; height:16px; margin-left:-8px; border-radius:50%; background:var(--card-fg); }
.w4 .wa-tick { position:absolute; width:1.5px; background:color-mix(in srgb, var(--card-fg) 22%, var(--card)); }
.w4 .wa-tl { position:absolute; font-family:var(--f-mono, var(--f-body)); color:color-mix(in srgb, var(--card-fg) 50%, var(--card)); white-space:nowrap; transform:translateX(-50%); }
.w4 .wa-brk { position:absolute; height:12px; box-sizing:border-box; border:3px solid var(--accent); border-top:0; transform-origin:50% 0; }
.w4 .wa-stem { position:absolute; width:3px; margin-left:-1.5px; background:var(--accent); transform-origin:50% 0; }
.w4 .wa-box { position:absolute; box-sizing:border-box; display:flex; align-items:center; justify-content:center; white-space:nowrap; font-weight:800;
  border-radius:var(--k-rs); border:2.5px solid var(--accent); background:color-mix(in srgb, var(--accent) 14%, var(--card)); color:var(--card-fg); overflow:hidden; }
.w4 .wa-box.out { background:color-mix(in srgb, var(--accent) 14%, var(--bg)); color:var(--fg); }
.w4 .wa-slot { position:relative; display:inline-block; height:1.3em; vertical-align:top; }
.w4 .wa-slot > span { position:absolute; left:0; top:0; white-space:nowrap; line-height:1.3em; }
.w4 .wa-slot .fr { color:var(--bad); }
.w4 .wa-slot .fr::after { content:""; position:absolute; left:-2px; right:-2px; top:52%; height:max(3px, .09em); background:var(--bad); transform:scaleX(var(--p, 0)); transform-origin:0 50%; }
.w4 .wa-slot .to { color:var(--good-ink); opacity:0; }
.w4 .wa-fix { position:absolute; display:flex; align-items:center; gap:18px; white-space:nowrap; font-weight:800; color:var(--fg); }
.w4 .wa-fix small { font-family:var(--k-kf); font-weight:700; letter-spacing:.12em; color:var(--muted); }
.w4 .wa-fix .fr { position:relative; color:var(--muted); }
.w4 .wa-fix .fr::after { content:""; position:absolute; left:-3px; right:-3px; top:52%; height:4px; background:var(--bad); transform:scaleX(var(--p, 0)); transform-origin:0 50%; }
.w4 .wa-fix .ar { color:var(--muted); }
.w4 .wa-fix .to { color:var(--accent); }
.w4 .wa-card { position:absolute; box-sizing:border-box; border-radius:var(--k-r); background:color-mix(in srgb, var(--fg) 6%, var(--bg));
  border:1.5px solid color-mix(in srgb, var(--fg) 16%, var(--bg)); overflow:hidden; }
.w4 .wa-ch { position:absolute; left:28px; right:28px; display:flex; justify-content:space-between; align-items:center; white-space:nowrap; }
.w4 .wa-ch small { font-family:var(--k-kf); font-weight:700; letter-spacing:.12em; color:var(--muted); }
.w4 .wa-ch b { font-family:var(--f-mono, var(--f-body)); color:var(--fg); font-variant-numeric:tabular-nums; }
.w4 .wa-rows { position:absolute; left:0; right:0; overflow:hidden; }
.w4 .wa-list { position:absolute; left:0; right:0; top:0; }
.w4 .wa-row { position:absolute; left:28px; right:28px; display:flex; align-items:center; gap:20px; white-space:nowrap; border-top:1.5px solid color-mix(in srgb, var(--fg) 10%, var(--bg)); }
.w4 .wa-row .tc { flex:none; font-family:var(--f-mono, var(--f-body)); color:var(--accent); font-variant-numeric:tabular-nums; }
.w4 .wa-row .tx { flex:1 1 auto; min-width:0; overflow:hidden; font-weight:700; color:var(--fg); }
.w4 .wa-row .tx .fr { position:relative; color:var(--muted); }
.w4 .wa-row .tx .fr::after { content:""; position:absolute; left:-2px; right:-2px; top:52%; height:3px; background:var(--bad); transform:scaleX(var(--p, 0)); transform-origin:0 50%; }
.w4 .wa-row .tx .to { color:var(--accent); }

/* qc_sheet */
.w4 .qc-grid { position:absolute; }
.w4 .qc-f { position:absolute; box-sizing:border-box; border-radius:min(calc(var(--k-rs) * .6), 10px); overflow:visible; perspective:900px; }
.w4 .qc-in { position:absolute; inset:0; border-radius:inherit; overflow:hidden; transform-style:preserve-3d; background:color-mix(in srgb, var(--card-fg) 10%, var(--card)); }
.w4 .qc-in img { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; display:block; }
.w4 .qc-sk { position:absolute; display:block; }
.w4 .qc-def { position:absolute; inset:0; }
.w4 .qc-def.blk { background:#000; }
.w4 .qc-def.wht { background:#fff; opacity:.92; }
.w4 .qc-def.ovl i { position:absolute; display:block; border-radius:2px; }
.w4 .qc-def.oth { background:repeating-linear-gradient(45deg, color-mix(in srgb, var(--bad) 55%, transparent) 0 6px, transparent 6px 12px); }
.w4 .qc-ring { position:absolute; inset:-3px; border-radius:inherit; border:3px solid var(--accent); opacity:0; pointer-events:none; }
.w4 .qc-flag { position:absolute; inset:-6px; border-radius:inherit; border:5px solid var(--bad); opacity:0; pointer-events:none; }
.w4 .qc-dots { position:absolute; right:5px; bottom:5px; display:flex; gap:4px; }
.w4 .qc-dots i { display:block; border-radius:50%; background:var(--accent); box-shadow:0 0 0 1.5px var(--card); opacity:0; }
.w4 .qc-lab { position:absolute; display:inline-flex; align-items:center; gap:8px; white-space:nowrap; font-weight:800; padding:4px 12px;
  border-radius:var(--k-rs); background:var(--bad); color:var(--on-bad); opacity:0; z-index:5; }
.w4 .qc-lab.ok { background:var(--good); color:var(--on-good); }
.w4 .qc-scan { position:absolute; width:4px; margin-left:-2px; background:var(--accent); border-radius:2px;
  box-shadow:0 0 18px 4px color-mix(in srgb, var(--accent) 55%, transparent); opacity:0; z-index:4; }
.w4 .qc-list { position:absolute; }
.w4 .qc-item { position:absolute; left:0; right:0; }
.w4 .qc-box { position:absolute; left:0; box-sizing:border-box; border:4px solid color-mix(in srgb, var(--fg) 30%, var(--bg)); border-radius:min(calc(var(--k-rs) * .7), 14px);
  display:flex; align-items:center; justify-content:center; color:var(--good); }
.w4 .qc-box svg { opacity:0; }
.w4 .qc-box .x { position:absolute; color:var(--bad); opacity:0; display:flex; }
.w4 .qc-nm { position:absolute; font-family:var(--f-display); font-weight:900; white-space:nowrap; color:var(--muted); line-height:1.15; }
.w4 .qc-st { position:absolute; font-family:var(--f-mono, var(--f-body)); white-space:nowrap; color:var(--muted); font-variant-numeric:tabular-nums; }
.w4 .qc-bar { position:absolute; left:0; right:0; height:4px; border-radius:2px; background:color-mix(in srgb, var(--fg) 12%, var(--bg)); overflow:hidden; }
.w4 .qc-bar i { position:absolute; left:0; top:0; bottom:0; width:100%; background:var(--accent); transform-origin:0 50%; transform:scaleX(0); }

/* pair_check */
.w4 .pc-pic { position:absolute; left:0; top:0; overflow:hidden; background:color-mix(in srgb, var(--card-fg) 8%, var(--card)); }
.w4 .pc-pic img { position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; display:block; }
.w4 .pc-sk { position:absolute; display:block; }
.w4 .pc-dim { position:absolute; inset:0; background:var(--bg); opacity:0; pointer-events:none; }
.w4 .pc-tab { position:absolute; left:16px; top:14px; display:inline-flex; align-items:center; gap:12px; white-space:nowrap; font-weight:800; padding:6px 16px;
  border-radius:var(--k-rs); background:color-mix(in srgb, var(--card) 86%, transparent); color:var(--card-fg); z-index:3; }
.w4 .pc-tab .w4-dots i { width:11px; height:11px; }
.w4 .pc-tab.win { background:var(--accent); color:var(--k-on); }
.w4 .pc-mk { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; z-index:4; }
.w4 .pc-mk ellipse, .w4 .pc-mk rect { fill:none; stroke:var(--accent); stroke-width:5; stroke-linecap:round; }
.w4 .pc-num { position:absolute; display:flex; align-items:center; justify-content:center; border-radius:50%; font-family:var(--f-num, var(--f-display)); font-weight:900;
  background:var(--accent); color:var(--k-on); z-index:5; }
.w4 .pc-pt { position:absolute; display:flex; align-items:center; justify-content:center; gap:12px; white-space:nowrap; font-weight:900; color:var(--muted); }
.w4 .pc-pt .n { font-family:var(--f-num, var(--f-display)); color:var(--muted); }
.w4 .pc-pt .w { position:relative; white-space:nowrap; }
.w4 .pc-pt .u { position:absolute; left:-4px; right:-4px; bottom:0; height:6px; border-radius:3px; background:var(--accent); transform-origin:0 50%; }
.w4 .pc-pt.chip { box-sizing:border-box; border-radius:var(--k-rs); border:2px solid color-mix(in srgb, var(--fg) 18%, var(--bg)); background:color-mix(in srgb, var(--fg) 6%, var(--bg)); }
"""

ICON_OK = ('<svg viewBox="0 0 24 24" style="width:1em;height:1em"><path d="M4.5 12.5l5 5L19.5 6.5" stroke="currentColor" '
           'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>')
ICON_X = ('<svg viewBox="0 0 24 24" style="width:1em;height:1em"><path d="M6 6L18 18M18 6L6 18" stroke="currentColor" '
          'stroke-width="3.4" stroke-linecap="round" fill="none"/></svg>')


# ------------------------------------------------------------------------------------------------ shared helpers
TXT_FLOOR_V = 1350.0      # 9:16: readable text stops here, above the reel caption band; pictures run on to the bottom edge


def _css(X):
    X.css("fx-f4-work", CSS)


def _t(X, s):
    """plain text → escaped html (no markup), glyphs registered for the font subset."""
    from h9.core import esc
    s = str(s)
    X.used_text.update(s)
    return esc(s)


def _hex(c):
    c = str(c).strip()
    if not c.startswith("#") or len(c) not in (4, 7):
        return None
    if len(c) == 4:
        c = "#" + c[1] * 2 + c[2] * 2 + c[3] * 2
    try:
        return (int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))
    except ValueError:
        return None


def _mix(a, b, w):
    """w of colour a over colour b (#rrggbb); unreadable input → a."""
    pa = _hex(a)
    pb = _hex(b)
    if pa is None or pb is None:
        return a
    out = "#"
    for i in range(3):
        out += f"{round(pa[i] * w + pb[i] * (1 - w)):02x}"
    return out


def _cols(X, p):
    """the resolved colours this file needs: the stage palette plus `mark` (what stands out on the card), `bad` (the
    style's alert colour) and `good` (the accent, or the text colour when the accent is the alert colour too)."""
    from h9.aefx import _contrast
    pal = A.pal(X, p)
    k = K.skin(X)
    card = pal.get("card", "#ffffff")
    mark = pal.get("card-fg", "#111111")
    for key in ("accent", "card-fg"):
        c = pal.get(key)
        if c and _contrast(c, card) >= 3.0:
            mark = c
            break
    bad = k.get("alert") or pal.get("accent")
    if _hex(bad) is None:
        bad = pal.get("accent", "#e2321f")
    good = pal.get("accent", "#e2321f")
    pb = _hex(bad)
    pg = _hex(good)
    if pb and pg:
        dist = abs(pb[0] - pg[0]) + abs(pb[1] - pg[1]) + abs(pb[2] - pg[2])
        if dist < 90:
            good = pal.get("fg", "#111111")
    out = dict(pal)
    out["mark"] = mark
    out["bad"] = bad
    out["good"] = good
    out["cmuted"] = _mix(pal.get("card-fg", "#111111"), card, 0.42)
    return out


def _gw(ch):
    """estimated advance of one glyph in em for the body face (CJK = 1)."""
    from h9 import fit as FT
    return FT.gw(ch)


CLOSE = "，。、；：！？）》」』】,.;:!?)%…"


def _fit_line(text, w, max_px, min_px, mono=False):
    """the biggest px ≤ max_px at which one line of `text` fits w; below min_px it is cut with an ellipsis."""
    from h9 import fit as FT
    em = FT.width(text, mono) or 1
    px = min(max_px, w * 0.97 / em)
    if px >= min_px:
        return int(px), text
    px = min_px
    room = w * 0.97 / px
    cut = ""
    for ch in text:
        if FT.width(cut + ch + "…", mono) > room:
            break
        cut += ch
    return int(px), cut.rstrip() + "…"


def _path_html(X, path, w, px):
    """a breadcrumb "a / b / c.md": earlier parts muted, the last part strong; cut from the left when too long."""
    from h9 import fit as FT
    parts = [x.strip() for x in str(path).split("/") if x.strip()]
    if not parts:
        return ""
    room = w * 0.97 / px
    while len(parts) > 1 and FT.width(" / ".join(parts), True) > room:
        parts = parts[1:]
        if parts[0] != "…":
            parts = ["…"] + parts[1:] if len(parts) > 1 else parts
        if len(parts) == 2 and parts[0] == "…":
            break
    last = parts[-1]
    lead = " / ".join(parts[:-1])
    if lead:
        lead = lead + " / "
    if FT.width(lead + last, True) > room:
        lead = ""
        last = _fit_line(last, w, px, px, mono=True)[1]
    return f'{_t(X, lead)}<b>{_t(X, last)}</b>'


def _window(X, x, y, w, h, path, P, body, right="", cls="", bar=None):
    """the shared window chrome → html. Title bar with three plain dots and the path, an optional right-hand readout,
    then `body` (absolutely placed inside .w4-body, which starts under the bar)."""
    bar_h = bar or (66 if P else 58)
    ppx = 28 if P else 24
    pad = 26 if P else 22
    right_w = 0
    if right:
        right_w = 260 if P else 300
    path_w = w - pad * 2 - 62 - 18 - right_w
    ph = _path_html(X, path, path_w, ppx)
    r = f'<div class="w4-right" style="font-size:{ppx}px">{right}</div>' if right else ""
    bleed = " data-layout-allow-overflow" if y + h > X.H else ""      # a 9:16 window may run off the bottom edge (picture)
    return (f'<div class="w4-win {cls}"{bleed} style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px">'
            f'<div class="w4-bar" style="height:{bar_h}px; padding:0 {pad}px"><div class="w4-dots"><i></i><i></i><i></i></div>'
            f'<div class="w4-path" style="font-size:{ppx}px">{ph}</div>{r}</div>'
            f'<div class="w4-body" style="top:{bar_h}px">{body}</div></div>'), bar_h


def _as_list(v, sep="|"):
    if v is None:
        return []
    if isinstance(v, str):
        if "\n" in v:
            return [x for x in v.split("\n") if x.strip()]
        return [x for x in v.split(sep) if x.strip()]
    if isinstance(v, (list, tuple)):
        out = []
        for x in v:
            if isinstance(x, dict):
                x = x.get("text") or x.get("label") or x.get("title") or ""
            x = str(x)
            if x.strip():
                out.append(x)
        return out
    return [str(v)]


def _path(src):
    """$H9_MEDIA / ~ expanded."""
    import os
    return os.path.expandvars(os.path.expanduser(str(src)))


def _warn(msg):
    print(f"  note: {msg}", file=sys.stderr)


def _seed(*parts):
    s = "|".join(str(x) for x in parts)
    return zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF


def _chips_html(X, items, x, y, w, px, P, cls="w4-chip", align="left", gap=14, max_rows=1):
    """a row of status chips (each with a small tick icon), shrunk then cut by rule to fit w → (html, height)."""
    from h9 import fit as FT
    if not items:
        return "", 0
    pad_x = 18 if P else 14
    icon = px * 1.0 + 10
    size = px
    keep = list(items)
    while True:
        widths = []
        for it in keep:
            widths.append(FT.width(it) * size + pad_x * 2 + icon)
        total = sum(widths) + gap * (len(keep) - 1)
        if total <= w or (size <= (28 if P else 24) and len(keep) == 1):
            break
        if size > (28 if P else 24):
            size -= 2
            icon = size + 10
            continue
        keep = keep[:-1]
        if not keep:
            return "", 0
    h = size * 1.75
    out = ""
    cx = x
    if align == "center":
        cx = x + (w - total) / 2
    for i, it in enumerate(keep):
        txt = it
        if widths[i] > w:
            txt = _fit_line(it, w - pad_x * 2 - icon, size, size)[1]
            widths[i] = w
        out += (f'<div class="{cls} ch{i}" style="left:{cx:.0f}px; top:{y:.0f}px; height:{h:.0f}px; padding:0 {pad_x}px; font-size:{size}px">'
                f'<span class="ic">{ICON_OK}</span>{_t(X, txt)}</div>')
        cx += widths[i] + gap
    return out, h


# ------------------------------------------------------------------------------------------------ doc_edit
def _doc_model(lines, edits):
    """the document → paragraphs, each {text, kinds, eds} on its final text. kinds: n (typed while writing), s (typed
    while writing, struck later by edit eds[j]) or i (inserted by edit eds[j])."""
    paras = []
    for ln in lines:
        kinds = []
        eds = []
        for ch in ln:
            kinds.append("n")
            eds.append(-1)
        paras.append({"text": ln, "kinds": kinds, "eds": eds})
    for k, e in enumerate(edits):
        para = paras[e["line"]]
        text = para["text"]
        frm = e["from"]
        pos = -1
        if frm:
            # the first occurrence that is not already struck or inserted
            start = 0
            while True:
                pos = text.find(frm, start)
                if pos < 0:
                    break
                clean = True
                for j in range(pos, pos + len(frm)):
                    if para["kinds"][j] != "n":
                        clean = False
                if clean:
                    break
                start = pos + 1
        span = []
        if frm and pos >= 0:
            for j in range(pos, pos + len(frm)):
                span.append(j)
        elif frm:
            # the span is not in the line: every still-plain glyph of the line is struck
            for j in range(len(text)):
                if para["kinds"][j] == "n":
                    span.append(j)
        for j in span:
            para["kinds"][j] = "s"
            para["eds"][j] = k
        end = span[-1] + 1 if span else len(text)
        ins = e["to"]
        if ins:
            para["text"] = text[:end] + ins + text[end:]
            para["kinds"] = para["kinds"][:end] + ["i"] * len(ins) + para["kinds"][end:]
            para["eds"] = para["eds"][:end] + [k] * len(ins) + para["eds"][end:]
    return paras


def _wrap_idx(text, idxs, max_em):
    """wrap the glyphs text[idxs] into rows no wider than max_em → list of rows, each a list of indices into text.
    Never starts a row with closing punctuation (it may hang ≤ 1 em, so callers wrap 1 em short); leading spaces of a
    row are dropped; a word longer than a row is broken by glyph."""
    s = ""
    for j in idxs:
        s += text[j]
    spans = []
    rs = 0
    re_ = 0
    cw = 0.0

    def place_alone(a, b):
        """put unit s[a:b] at the start of an empty row (breaking it by glyph when it is longer than a row)."""
        nonlocal rs, re_, cw
        rs = a
        re_ = a
        cw = 0.0
        for j in range(a, b):
            g = _gw(s[j])
            if cw + g > max_em and re_ > rs:
                spans.append((rs, re_))
                rs = j
                re_ = j
                cw = 0.0
            re_ = j + 1
            cw += g

    for m in re.finditer(r"[A-Za-z0-9_@#$%&+\-.,:/'’]+\s*|\s+|.", s):
        a = m.start()
        b = m.end()
        u = s[a:b]
        w = 0.0
        for ch in u:
            w += _gw(ch)
        if re_ == rs:
            if u.isspace():
                rs = b
                re_ = b
                continue
            place_alone(a, b)
            continue
        if cw + w <= max_em:
            re_ = b
            cw += w
            continue
        if u[0] in CLOSE and cw + w <= max_em + 1.0:
            re_ = b
            cw += w
            continue
        spans.append((rs, re_))
        if u.isspace():
            rs = b
            re_ = b
            cw = 0.0
            continue
        place_alone(a, b)
    if re_ > rs or not spans:
        spans.append((rs, re_))
    rows = []
    for a, b in spans:
        while b > a and s[b - 1] == " ":
            b -= 1
        row = []
        for q in range(a, b):
            row.append(idxs[q])
        rows.append(row)
    return rows


def _doc_layout(paras, max_em):
    """per paragraph: v0 rows (the text as first written, no inserts) and v1 rows (the final text) when it has inserts."""
    out = []
    for para in paras:
        text = para["text"]
        v0 = []
        allx = []
        has_ins = False
        for j in range(len(text)):
            allx.append(j)
            if para["kinds"][j] != "i":
                v0.append(j)
            else:
                has_ins = True
        r0 = _wrap_idx(text, v0, max_em)
        r1 = _wrap_idx(text, allx, max_em) if has_ins else None
        out.append({"r0": r0, "r1": r1})
    return out


def doc_edit(X, cid, t, d, p):
    """改稿窗口 Doc Edit: a document window — path in the title bar, a heading, then the lines type in with a caret at an
    adaptive speed (all done by 80 % of the beat; long documents scroll by rule). Each edit then strikes its `from`
    span (the text greys) and types the `to` text in after it, marked; the paragraph reflows as it grows. 16:9: window
    right, a left column of big verbs (写 / 删 / 改) lighting in step with a live character count; 9:16: window full
    width, tags and a verb-chip row under it."""
    F_ = "doc_edit"
    lines = _as_list(p.get("lines") if p.get("lines") is not None else p.get("text"))
    A.need(F_, t, p, [] if lines else ["lines (the document, typed in order)"])
    if not lines:
        lines = ["……"]
    if len(lines) > 60:
        _warn(f"{F_}: {len(lines)} lines, typing the first 60")
        lines = lines[:60]
    G = A.frame(X, p)
    P = G["P"]
    path = str(p.get("path") or "草稿 / 口播稿.md")
    heading = str(p.get("heading") if p.get("heading") is not None else "## 正文")
    tags = _as_list(p.get("tags"))
    if len(tags) > 4:
        tags = tags[:4]
    raw_edits = p.get("edits") or []
    if isinstance(raw_edits, dict):
        raw_edits = [raw_edits]
    edits = []
    for e in raw_edits:
        if not isinstance(e, dict):
            continue
        try:
            li = int(e.get("line", 0))
        except (TypeError, ValueError):
            li = 0
        if li < 0:
            li = len(lines) + li
        li = max(0, min(len(lines) - 1, li))
        frm = str(e.get("from") or "")
        to = str(e.get("to") or "")
        if not frm and not to:
            continue
        edits.append({"line": li, "from": frm, "to": to})
    if len(edits) > 4:
        _warn(f"{F_}: {len(edits)} edits, showing the first 4")
        edits = edits[:4]
    col = _cols(X, p)
    paras = _doc_model(lines, edits)

    # ---- geometry. 9:16: verbs row sits on the content floor, tags above it, the window ends above them
    if P:
        # 9:16: the verb chips and tags on top, then the window from under them off the bottom edge (picture); its
        # text stops at the text floor above the caption band
        tx1 = 960.0                     # text clear of the 9:16 button zone on the right
        vchip_h = 84
        tag_h = 56
        vrow_y = 300.0
        tag_y = vrow_y + vchip_h + 16
        wx0, wx1 = 70.0, 1010.0
        wy0 = (tag_y + tag_h + 20) if tags else (vrow_y + vchip_h + 20)
        wy1 = X.H + 40.0
        tx0 = wx0 + 40
        txt_floor = TXT_FLOOR_V
    else:
        wx0, wy0, wx1, wy1 = 800.0, 150.0, 1810.0, 890.0
        tx0 = wx0 + 44
        tx1 = wx1 - 44
    text_w = tx1 - tx0
    bar_h = 66 if P else 58
    head_px = 30 if P else 26
    head_top = 26 if P else 22
    head_h = head_px * 1.6 if heading else 0
    body_top = head_top + head_h + (10 if heading else 0)
    body_h = (wy1 - wy0) - bar_h - body_top - (28 if P else 24)
    if P:
        body_h = (txt_floor - wy0) - bar_h - body_top

    # the body size: the largest step at which the whole final document fits, never under the floor (it scrolls)
    steps = [66, 62, 58, 54, 50, 46, 42, 40] if P else [48, 44, 40, 37, 34]
    px = steps[-1]
    lay = None
    for cand in steps:
        lay = _doc_layout(paras, text_w / cand - 1.0)
        n_final = 0
        for q in lay:
            n_final += len(q["r1"] if q["r1"] is not None else q["r0"])
        px = cand
        if n_final * cand * 1.62 <= body_h:
            break
    rh = px * 1.62
    vis = max(1, int(body_h // rh))

    # ---- timing: everything typed and edited by 80 % of the beat
    ts = t + min(0.5, d * 0.14)
    te = t + d * 0.8
    if te < ts + 0.4:
        te = ts + 0.4
    n_write = 0
    n_ins = 0
    for para in paras:
        for kd in para["kinds"]:
            if kd == "i":
                n_ins += 1
            else:
                n_write += 1
    c0 = 0.05
    natural = n_write * c0 + len(lines) * 0.14 + len(edits) * 0.75 + n_ins * c0 * 1.25
    f = (te - ts) / max(0.01, natural)
    if f > 1.35:
        f = 1.35
    per = c0 * f
    brk = 0.14 * f
    ptimes = []
    for para in paras:
        ptimes.append([0.0] * len(para["text"]))
    events = []                         # caret: [time, para, glyph index it follows (−1: start of the para)]
    tt = ts
    for pi, para in enumerate(paras):
        if pi > 0:
            tt += brk
        for j in range(len(para["text"])):
            if para["kinds"][j] == "i":
                continue
            ptimes[pi][j] = round(tt, 4)
            events.append([round(tt, 4), pi, j])
            tt += per
    write_end = tt
    phases = []                         # (verb, start, end)
    if n_write:
        phases.append(("写", ts, write_end))
    for k, e in enumerate(edits):
        travel = max(0.12, 0.25 * f)
        strike = max(0.18, 0.32 * f)
        gap = max(0.06, 0.16 * f)
        pi = e["line"]
        para = paras[pi]
        s_idx = [j for j in range(len(para["text"])) if para["eds"][j] == k and para["kinds"][j] == "s"]
        i_idx = [j for j in range(len(para["text"])) if para["eds"][j] == k and para["kinds"][j] == "i"]
        if s_idx:
            after = s_idx[-1]
        elif i_idx:
            after = i_idx[0] - 1
        else:
            after = len(para["text"]) - 1
        tt += travel
        events.append([round(tt, 4), pi, after])
        e["_t0"] = tt
        if s_idx:
            e["_strike"] = tt
            phases.append(("删", tt, tt + strike))
            tt += strike + gap
        else:
            e["_strike"] = None
        if i_idx:
            i0 = tt
            for j in i_idx:
                ptimes[pi][j] = round(tt, 4)
                events.append([round(tt, 4), pi, j])
                tt += per * 1.25
            phases.append(("改", i0, tt))
        e["_t1"] = tt
    done = tt
    if not edits:
        phases.append(("存", done + 0.1, done + 0.45))

    # the moment each edited paragraph switches to its final wrap (its first inserted glyph)
    sw = []
    for pi, para in enumerate(paras):
        first = None
        for j in range(len(para["text"])):
            if para["kinds"][j] == "i":
                if first is None or ptimes[pi][j] < first:
                    first = ptimes[pi][j]
        sw.append(first)

    def nrows(pi, tm):
        q = lay[pi]
        if q["r1"] is not None and sw[pi] is not None and tm >= sw[pi]:
            return len(q["r1"])
        return len(q["r0"])

    def row_of(pi, j, tm):
        """global row of glyph j of paragraph pi at time tm (−1 = before the first glyph: the paragraph's first row)."""
        top = 0
        for q in range(pi):
            top += nrows(q, tm)
        rows_ = lay[pi]["r1"] if (lay[pi]["r1"] is not None and sw[pi] is not None and tm >= sw[pi]) else lay[pi]["r0"]
        for r_i, row in enumerate(rows_):
            if j in row:
                return top + r_i
        if j < 0:
            return top
        return top + len(rows_) - 1

    # scroll: keep the caret's row inside the view (one eased step per change)
    events.sort(key=lambda a: a[0])
    scroll = []
    s_cur = 0
    for tm, pi, j in events:
        r = row_of(pi, j, tm)
        total = 0
        for q in range(len(paras)):
            total += nrows(q, tm)
        s_new = s_cur
        if r > s_cur + vis - 2 and r >= vis - 1:
            s_new = min(max(0, total - vis), r - (vis - 2))
            if r - s_new >= vis:
                s_new = r - vis + 1
        if r < s_cur + 1 and s_cur > 0:
            s_new = max(0, r - 1)
        if s_new != s_cur:
            scroll.append([round(tm, 4), s_new - s_cur])
            s_cur = s_new

    # ---- the document html: paragraph blocks → version blocks → rows of glyphs (struck / inserted runs grouped)
    doc = ""
    elem = {}                           # (para, version, glyph) → element index in document order
    el_t = []                           # per element: its typing time
    el_a = []                           # per element: when its version becomes the visible one
    el_b = []                           # … and stops being it
    el_c = []                           # per element: counts as a glyph (not a space)
    top_rows = 0
    para_tops = []
    for pi, para in enumerate(paras):
        para_tops.append(top_rows)
        q = lay[pi]
        vers = [("v0", q["r0"])]
        if q["r1"] is not None:
            vers.append(("v1", q["r1"]))
        block = ""
        for vname, rows_ in vers:
            vb = ""
            for r_i, row in enumerate(rows_):
                seg = ""
                x = 0
                while x < len(row):
                    j = row[x]
                    kind = para["kinds"][j]
                    k = para["eds"][j]
                    run = ""
                    y = x
                    while y < len(row) and para["kinds"][row[y]] == kind and para["eds"][row[y]] == k:
                        jj = row[y]
                        elem[(pi, vname, jj)] = len(el_t)
                        el_t.append(ptimes[pi][jj])
                        if vname == "v0":
                            el_a.append(-1.0)
                            el_b.append(sw[pi] if (q["r1"] is not None and sw[pi] is not None) else 1e9)
                        else:
                            el_a.append(sw[pi])
                            el_b.append(1e9)
                        el_c.append(1 if para["text"][jj].strip() else 0)
                        run += f'<i class="c">{_t(X, para["text"][jj])}</i>'
                        y += 1
                    if kind == "s":
                        seg += f'<span class="de-st e{k}">{run}</span>'
                    elif kind == "i":
                        seg += f'<span class="de-in e{k}">{run}</span>'
                    else:
                        seg += run
                    x = y
                vb += f'<div class="de-row" data-p="{pi}" data-r="{r_i}" style="top:{r_i * rh:.1f}px; height:{rh:.1f}px; line-height:{rh:.1f}px">{seg}</div>'
            hide = ' style="display:none"' if vname == "v1" else ""
            block += f'<div class="de-v {vname}"{hide}>{vb}</div>'
        doc += f'<div class="de-para p{pi}" style="top:{top_rows * rh:.1f}px">{block}</div>'
        top_rows += len(q["r0"])

    caret = []
    for tm, pi, j in events:
        vname = "v1" if (lay[pi]["r1"] is not None and sw[pi] is not None and tm >= sw[pi]) else "v0"
        if j < 0:
            # before the first glyph of the paragraph: follow the previous paragraph's last glyph, else the start
            caret.append([tm, -1])
            continue
        key = (pi, vname, j)
        while key not in elem and j >= 0:
            j -= 1
            key = (pi, vname, j)
        caret.append([tm, elem.get(key, -1)])
    clip_x = tx0 - wx0
    head_html = ""
    if heading:
        hpx, htxt = _fit_line(heading, text_w, head_px, 22)
        head_html = f'<div class="de-head" style="left:{clip_x:.0f}px; top:{head_top}px; font-size:{hpx}px">{_t(X, htxt)}</div>'
    body = (head_html + f'<div class="de-clip" style="left:{clip_x - 6:.0f}px; top:{body_top:.0f}px; width:{text_w + 12:.0f}px; height:{vis * rh + 4:.0f}px">'
            f'<div class="de-doc" style="left:6px; font-size:{px}px">{doc}</div></div>')
    n_chars = 0
    for para in paras:
        for j in range(len(para["text"])):
            if para["kinds"][j] != "i" and para["text"][j].strip():
                n_chars += 1
    if P:
        right = f'<span class="de-n">0</span> 字'
    else:
        right = f'<span class="de-save"><s></s><span class="de-sv">未保存</span></span>' if not edits else f'已改 <span class="de-ne">0</span> 处'
    win, _bh = _window(X, wx0, wy0, wx1 - wx0, wy1 - wy0, path, P, body, right=right, cls="de-win")
    model_edits = edits

    # ---- the verbs: what is happening, in order
    verbs = []
    for v, a, b in phases:
        found = False
        for vv in verbs:
            if vv["v"] == v:
                vv["b"] = b
                found = True
        if not found:
            verbs.append({"v": v, "a": a, "b": b})
    n_lines = len(lines)
    for vv in verbs:
        if vv["v"] == "写":
            vv["dt"] = f"{n_lines} 段 · {n_chars} 字" if not P else f"{n_lines} 段"
        elif vv["v"] == "删":
            vv["dt"] = f"划掉 {sum(1 for e in model_edits if e.get('_strike') is not None)} 处"
        elif vv["v"] == "改":
            vv["dt"] = f"补上 {sum(1 for e in model_edits if e['to'])} 处"
        else:
            vv["dt"] = "已保存"
    side = ""
    if not P:
        # 16:9 left column, x 110 … 740, top aligned with the window
        cx0 = 110.0
        cw = 630.0
        kick = str(p.get("kicker") or ("写稿 · 改稿" if model_edits else "写稿"))
        kpx, ktxt = _fit_line(kick, cw, 26, 24)
        side += f'<div class="de-kick" style="left:{cx0:.0f}px; top:{wy0 + 4:.0f}px; font-size:{kpx}px">{_t(X, ktxt)}</div>'
        gpx = 120 if len(verbs) <= 2 else 104
        row_h = gpx + 54
        vy = wy0 + 70
        for vi, vv in enumerate(verbs):
            dpx, dtxt = _fit_line(vv["dt"], cw - gpx * 1.2 - 90, 30, 24)
            side += (f'<div class="de-verb v{vi}" style="left:{cx0:.0f}px; top:{vy + vi * row_h:.0f}px; width:{cw:.0f}px; height:{row_h:.0f}px">'
                     f'<div class="g" style="font-size:{gpx}px">{_t(X, vv["v"])}</div>'
                     f'<div class="dt" style="left:{gpx * 1.18:.0f}px; top:{gpx * 0.5 - dpx * 0.6:.0f}px; font-size:{dpx}px">{_t(X, dtxt)}</div>'
                     f'<div class="ok" style="left:{gpx * 1.18:.0f}px; top:{gpx * 0.5 + dpx * 0.7:.0f}px; font-size:{dpx + 6}px">{ICON_OK}</div>'
                     f'<div class="rule" style="top:{gpx + 16:.0f}px; width:{cw:.0f}px"></div></div>')
        cy_ = vy + len(verbs) * row_h + 10
        tag_h = 0
        tag_html = ""
        if tags:
            tag_html, tag_h = _chips_html(X, tags, cx0, wy1 - 50, cw, 26, P, cls="w4-chip de-tag")
            if tag_h:
                tag_html, tag_h = _chips_html(X, tags, cx0, wy1 - tag_h, cw, 26, P, cls="w4-chip de-tag")
        count_bottom = wy1 - (tag_h + 24 if tag_h else 0)
        npx = 84
        if count_bottom - cy_ < npx + 40:
            npx = max(56, int(count_bottom - cy_ - 40))
        side += (f'<div class="de-count" style="left:{cx0:.0f}px; top:{count_bottom - npx - 40:.0f}px">'
                 f'<small style="font-size:24px">字数</small><b class="de-cn" style="font-size:{npx}px">0</b></div>')
        side += tag_html
    else:
        # 9:16: tags under the window, then the verbs as a chip row on the content floor (above the caption)
        if tags:
            th, thh = _chips_html(X, tags, wx0, tag_y, tx1 - wx0, 32, P, cls="w4-chip de-tag")
            side += th
        cw = (tx1 - wx0 - 14 * (len(verbs) - 1)) / max(1, len(verbs))
        gpx = 56
        for vi, vv in enumerate(verbs):
            dpx, dtxt = _fit_line(vv["dt"], cw - gpx - 76, 36, 30)
            side += (f'<div class="de-vchip v{vi}" style="left:{wx0 + vi * (cw + 14):.0f}px; top:{vrow_y:.0f}px; width:{cw:.0f}px; height:{vchip_h}px; padding:0 18px">'
                     f'<span class="g" style="font-size:{gpx}px">{_t(X, vv["v"])}</span><span class="dt" style="font-size:{dpx}px">{_t(X, dtxt)}</span>'
                     f'<span class="ok" style="font-size:{dpx + 4}px">{ICON_OK}</span></div>')
    inner = win + side
    _css(X)
    style_vars = f"--mark:{col['mark']}; --bad:{col['bad']}"
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body w4" style="{style_vars}">{inner}</div>')

    # ---- entrances: 16:9 the window slides in from the right and the column rises; 9:16 the window drops from above
    if P:
        X.tw(f'tl.fromTo("{s} .de-win", {{y:-70, scale:0.96, opacity:0}}, {{y:0, scale:1, opacity:1, duration:0.5, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .de-vchip", {{y:60, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 0% 0)", duration:0.4, ease:"power3.out", stagger:0.07, immediateRender:true}}, {t + 0.22:.3f});')
        X.tw(f'tl.fromTo("{s} .de-tag", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.3:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .de-win", {{x:140, opacity:0}}, {{x:0, opacity:1, duration:0.55, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .de-kick", {{x:-30, clipPath:"inset(0 100% 0 0)"}}, {{x:0, clipPath:"inset(0 -5% 0 0)", duration:0.4, ease:"power3.out", immediateRender:true}}, {t + 0.12:.3f});')
        X.tw(f'tl.fromTo("{s} .de-verb .g", {{y:50, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 -10% 0)", duration:0.45, ease:"expo.out", stagger:0.08, immediateRender:true}}, {t + 0.18:.3f});')
        X.tw(f'tl.fromTo("{s} .de-verb .dt, {s} .de-count", {{x:-24, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.3:.3f});')
        X.tw(f'tl.fromTo("{s} .de-tag", {{y:24, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.4:.3f});')

    # ---- verbs light while their action runs, then settle with a tick
    fg = col.get("fg", "#111111")
    acc = col.get("accent", "#e2321f")
    mut = col.get("muted", "#777777")
    for vi, vv in enumerate(verbs):
        a = vv["a"]
        b = max(vv["b"], a + 0.2)
        if P:
            X.tw(f'tl.to("{s} .de-vchip.v{vi}", {{color:"{fg}", borderColor:"{acc}", duration:0.12}}, {a:.3f});')
            X.tw(f'tl.fromTo("{s} .de-vchip.v{vi} .g", {{color:"{mut}"}}, {{color:"{acc}", duration:0.12, immediateRender:false}}, {a:.3f});')
            X.tw(f'tl.fromTo("{s} .de-vchip.v{vi}", {{scale:1}}, {{keyframes:[{{scale:1.06, duration:0.1}}, {{scale:1, duration:0.2}}]}}, {a:.3f});')
            X.tw(f'tl.to("{s} .de-vchip.v{vi} .g", {{color:"{fg}", duration:0.2}}, {b:.3f});')
            X.tw(f'tl.fromTo("{s} .de-vchip.v{vi} .ok", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:true}}, {b:.3f});')
        else:
            X.tw(f'tl.fromTo("{s} .de-verb.v{vi} .g", {{color:"{mut}"}}, {{color:"{acc}", duration:0.12, immediateRender:false}}, {a:.3f});')
            X.tw(f'tl.fromTo("{s} .de-verb.v{vi} .g", {{x:0}}, {{keyframes:[{{x:14, duration:0.12}}, {{x:0, duration:0.3}}]}}, {a:.3f});')
            X.tw(f'tl.to("{s} .de-verb.v{vi} .dt", {{color:"{fg}", duration:0.12}}, {a:.3f});')
            X.tw(f'tl.fromTo("{s} .de-verb.v{vi} .rule", {{scaleX:0}}, {{scaleX:1, duration:{max(0.25, b - a):.3f}, ease:"none", immediateRender:true}}, {a:.3f});')
            X.tw(f'tl.to("{s} .de-verb.v{vi} .g", {{color:"{fg}", duration:0.2}}, {b:.3f});')
            X.tw(f'tl.to("{s} .de-verb.v{vi} .rule", {{scaleY:0.34, opacity:0.5, duration:0.2}}, {b:.3f});')
            X.tw(f'tl.fromTo("{s} .de-verb.v{vi} .ok", {{opacity:0, scale:0.4}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2)", immediateRender:true}}, {b:.3f});')

    # ---- strikes grey the span and draw the bar; the save dot turns into a tick
    cm = col["cmuted"]
    for k, e in enumerate(model_edits):
        if e.get("_strike") is not None:
            X.tw(f'tl.fromTo("{s} .de-st.e{k}", {{"--p":0}}, {{"--p":1, duration:{max(0.18, 0.3 * f):.3f}, ease:"power2.inOut", stagger:0.08, immediateRender:true}}, {e["_strike"]:.3f});')
            X.tw(f'tl.to("{s} .de-st.e{k}", {{color:"{cm}", duration:0.2}}, {e["_strike"] + 0.12:.3f});')
            X.sfx(e["_strike"], "click", 0.35)
    if not model_edits and not P:
        X.tw(f'tl.set("{s} .de-sv", {{textContent:"已保存"}}, {done + 0.1:.3f});')
        X.tw(f'tl.to("{s} .de-save s", {{backgroundColor:"{col["good"]}", scale:1.3, duration:0.15}}, {done + 0.1:.3f});')

    # ---- the typing, caret, counters and scroll: one proxy tween, redrawn from the time
    ne_times = []
    for e in model_edits:
        ne_times.append(round(e["_t1"], 3))
    X.tw(f'''(()=>{{
  const R = document.querySelector("{s}");
  if (!R) return;
  const cs = [...R.querySelectorAll(".de-doc i.c")];
  const doc = R.querySelector(".de-doc");
  const caret = document.createElement("i");
  caret.className = "de-caret";
  const T = {A.js(el_t)}, VA = {A.js(el_a)}, VB = {A.js(el_b)}, CC = {A.js(el_c)};
  const CE = {A.js(caret)}, SC = {A.js(scroll)}, NE = {A.js(ne_times)};
  const N0 = {A.js([len(q["r0"]) for q in lay])}, N1 = {A.js([len(q["r1"]) if q["r1"] is not None else -1 for q in lay])}, SW = {A.js([x if x is not None else 1e9 for x in sw])};
  const paras = [...R.querySelectorAll(".de-para")];
  const v0s = paras.map(e => e.querySelector(".de-v.v0")), v1s = paras.map(e => e.querySelector(".de-v.v1"));
  const rows = [...R.querySelectorAll(".de-row")];
  const rh = {rh:.2f}, t0 = {t:.3f}, VIS = {vis};
  const cn = R.querySelector(".de-cn"), nn = R.querySelector(".de-n"), ne = R.querySelector(".de-ne");
  function ease(u) {{ if (u <= 0) return 0; if (u >= 1) return 1; return 1 - Math.pow(1 - u, 3); }}
  function draw(lt) {{
    const time = t0 + lt;
    let top = 0;
    const tops = [];
    for (let q = 0; q < paras.length; q++) {{
      tops.push(top);
      const late = N1[q] >= 0 && time >= SW[q];
      paras[q].style.top = (top * rh).toFixed(1) + "px";
      v0s[q].style.display = late ? "none" : "";
      if (v1s[q]) v1s[q].style.display = late ? "" : "none";
      top += late ? N1[q] : N0[q];
    }}
    let shown = 0;
    let lastT = -1;
    for (let i = 0; i < cs.length; i++) {{
      const on = time >= T[i];
      cs[i].style.display = on ? "" : "none";
      if (on && time >= VA[i] && time < VB[i]) {{
        shown += CC[i];
        if (T[i] > lastT) lastT = T[i];
      }}
    }}
    let at = -1, ct = -1;
    for (let k = 0; k < CE.length; k++) {{ if (CE[k][0] <= time) {{ at = CE[k][1]; ct = CE[k][0]; }} }}
    if (at >= 0) cs[at].after(caret);
    else if (rows.length) rows[0].prepend(caret);
    const idle = time - Math.max(ct, lastT);
    caret.style.opacity = idle > 0.35 ? ((Math.floor((time - t0) * 2.4) % 2) ? "0.12" : "1") : "1";
    let off = 0;
    for (let k = 0; k < SC.length; k++) off += SC[k][1] * ease((time - SC[k][0]) / 0.22);
    doc.style.transform = "translateY(" + (-off * rh).toFixed(1) + "px)";
    for (let i = 0; i < rows.length; i++) {{
      const y = tops[+rows[i].dataset.p] + (+rows[i].dataset.r) - off;
      rows[i].style.visibility = (y < -0.04 || y > VIS - 0.96) ? "hidden" : "";
    }}
    if (cn) cn.textContent = String(shown);
    if (nn) nn.textContent = String(shown);
    if (ne) {{ let k = 0; for (let j = 0; j < NE.length; j++) if (time >= NE[j]) k++; ne.textContent = String(k); }}
  }}
  const V = {{ t: 0 }};
  draw(0);
  tl.fromTo(V, {{ t: 0 }}, {{ t: {d:.3f}, duration: {d:.3f}, ease: "none", immediateRender: false, onUpdate: () => draw(V.t) }}, {t:.3f});
}})();''')
    A.hold_push(X, f"{s} .w4", done + 0.25, t + d, 1.025, origin=f"{(wx0 + wx1) / 2:.0f}px {(wy0 + wy1) / 2:.0f}px")
    X.sfx(ts, "type", 0.4)
    if model_edits:
        X.sfx(done, "pop", 0.35)


# ------------------------------------------------------------------------------------------------ wave_align
def _tc(sec):
    """seconds → "00:03.2"."""
    if sec < 0:
        sec = 0.0
    m = int(sec // 60)
    s_ = sec - m * 60
    return f"{m:02d}:{s_:04.1f}"


def _weight(text):
    """how long a chunk takes to say, in syllable-ish units: a CJK glyph = 1, a Latin word = 1.5, a digit 0.6."""
    w = 0.0
    for m in re.finditer(r"[A-Za-z]+|\d|[^\sA-Za-z\d]", str(text)):
        tok = m.group(0)
        if tok.isalpha() and tok.isascii():
            w += 1.5
        elif tok.isdigit():
            w += 0.6
        elif tok in "，。、；：！？,.;:!?…—·“”\"'（）()":
            w += 0.2
        else:
            w += 1.0
    return max(0.6, w)


def _spoken_spans(X, chunks, t, d):
    """[(start, end)] per chunk from the film's word timestamps when every chunk is said, in order, inside the beat;
    else None (the caller spreads them by length)."""
    if not getattr(X, "chars", None):
        return None
    starts = []
    cur = t
    for c in chunks:
        hit = X.spoken_at(A.strip(c), cur, t + d)
        if hit is None:
            return None
        starts.append(hit)
        cur = hit + 0.05
    last_end = None
    for item in X.chars:
        if starts[-1] <= item[1] < t + d:
            last_end = item[2]
    if last_end is None or last_end <= starts[-1]:
        last_end = starts[-1] + 0.25 * _weight(chunks[-1])
    out = []
    for i in range(len(starts)):
        if i + 1 < len(starts):
            e = starts[i + 1] - 0.02
        else:
            e = min(last_end, t + d - 0.1)
        if e <= starts[i] + 0.1:
            e = starts[i] + 0.1
        out.append((starts[i], e))
    return out


def _pack(spans, texts, x0, x1, max_px, min_px, pad, gap, mono=False):
    """caption boxes under their spans in one row → (px, [(x, w, text)]). Each box is centred on its span, at least as
    wide as the span (less a hairline) and its text; neighbours are pushed apart, then back inside [x0, x1]. If they
    cannot fit at min_px, every box takes its span's width (≥ 2 em) and its text is cut with an ellipsis."""
    from h9 import fit as FT
    px = max_px
    while px >= min_px:
        boxes = []
        for (a, b), tx in zip(spans, texts):
            w = max(b - a - 6, FT.width(tx, mono) * px + pad * 2)
            boxes.append([(a + b) / 2 - w / 2, w, tx])
        for i in range(len(boxes)):
            if boxes[i][0] < x0:
                boxes[i][0] = x0
            if i > 0 and boxes[i][0] < boxes[i - 1][0] + boxes[i - 1][1] + gap:
                boxes[i][0] = boxes[i - 1][0] + boxes[i - 1][1] + gap
        for i in range(len(boxes) - 1, -1, -1):
            if i == len(boxes) - 1:
                lim = x1
            else:
                lim = boxes[i + 1][0] - gap
            if boxes[i][0] + boxes[i][1] > lim:
                boxes[i][0] = lim - boxes[i][1]
        if boxes and boxes[0][0] >= x0 - 0.5:
            out = []
            for b in boxes:
                out.append((b[0], b[1], b[2]))
            return px, out
        px -= 2
    px = min_px
    out = []
    prev = x0 - gap
    for (a, b), tx in zip(spans, texts):
        w = max(b - a - 6, px * 2 + pad * 2)
        x = max(a + 3, prev + gap)
        if x + w > x1:
            w = max(px + pad * 2, x1 - x)
        fitted = _fit_line(tx, w - pad * 2, px, px, mono)[1]
        out.append((x, w, fitted))
        prev = x + w
    return px, out


def _bars(seed, n, spans_px, x0, step):
    """deterministic speech-like bar heights (0–1) for n bars from x0 at `step` px, shaped by the chunk spans: syllable
    bumps inside a chunk, near-silence in the gaps."""
    import random
    rng = random.Random(seed)
    out = []
    for i in range(n):
        x = x0 + i * step + step / 2
        amp = 0.04 + 0.05 * rng.random()
        for (a, b, syl) in spans_px:
            if a <= x <= b:
                u = (x - a) / max(1.0, b - a)
                bump = abs(math.sin(math.pi * u * syl)) ** 0.6
                edge = min(1.0, u / 0.08, (1 - u) / 0.08)
                amp = (0.22 + 0.78 * bump) * (0.62 + 0.38 * rng.random()) * max(0.15, edge)
                break
        out.append(round(min(1.0, amp), 3))
    return out


def wave_align(X, cid, t, d, p):
    """声画对齐 Wave Align: a voice clip as a waveform window; a playhead sweeps it at constant speed and as it reaches
    each chunk the chunk's caption box snaps up onto its exact span (6 frames, overshoot) tied by a thin bracket.
    With `fix`, the box holding the wrong word shakes, the word is struck and the correction slides in. Chunk spans
    come from the film's word timestamps when the beat has them, else from the chunks' lengths. 16:9: one wide window
    with the boxes under it and the fix line at the bottom left; 9:16: two stacked lanes inside the window (boxes under
    each) and a caption-file card below that fills with timecoded rows."""
    F_ = "wave_align"
    raw = p.get("words") if p.get("words") is not None else p.get("chunks")
    chunks = _as_list(raw)
    A.need(F_, t, p, [] if chunks else ["words (the caption chunks, 3–10)"])
    if not chunks:
        chunks = ["……"]
    while len(chunks) > 10:
        # too many chunks for readable boxes: join neighbours (lightest pair first) until 10 remain
        best = 0
        best_w = None
        for i in range(len(chunks) - 1):
            w = _weight(chunks[i]) + _weight(chunks[i + 1])
            if best_w is None or w < best_w:
                best_w = w
                best = i
        sep = ""
        if chunks[best][-1:].isascii() and chunks[best + 1][:1].isascii():
            sep = " "
        chunks = chunks[:best] + [chunks[best] + sep + chunks[best + 1]] + chunks[best + 2:]
    n = len(chunks)
    title = str(p.get("title") or "口播 / 配音.wav")
    chips = _as_list(p.get("chips"))[:4]
    fix = p.get("fix") if isinstance(p.get("fix"), dict) else None
    if fix and not (str(fix.get("from") or "").strip() and str(fix.get("to") or "").strip()):
        fix = None
    G = A.frame(X, p)
    P = G["P"]
    col = _cols(X, p)
    fr = 1.0 / X.fps

    # ---- time: real spans from the word timestamps, else spread by length over [t + 0.55, t + 0.82 d]
    spans_t = _spoken_spans(X, chunks, t, d)
    if spans_t:
        tp0 = min(spans_t[0][0], t + 0.35)
        tp1 = spans_t[-1][1]
    else:
        tp0 = t + min(0.55, d * 0.15)
        tp1 = t + d * 0.82
        if tp1 < tp0 + 0.6:
            tp1 = tp0 + 0.6
        total_w = 0.0
        for c in chunks:
            total_w += _weight(c)
        gap = min(0.14, (tp1 - tp0) * 0.025)
        avail = (tp1 - tp0) - gap * (n + 1)
        spans_t = []
        cur = tp0 + gap
        for c in chunks:
            dur = avail * _weight(c) / total_w
            spans_t.append((cur, cur + dur))
            cur += dur + gap
    clip_len = tp1 - tp0

    # the fix: the first chunk that holds the wrong word (case-insensitive)
    fix_i = None
    fix_pos = -1
    if fix:
        for i, c in enumerate(chunks):
            pos = c.lower().find(str(fix["from"]).lower())
            if pos >= 0:
                fix_i = i
                fix_pos = pos
                break

    # ---- lanes: 16:9 one; 9:16 two (split at the chunk boundary nearest the middle), one for a single chunk
    if P:
        wx0, wy0, wx1, wy1 = 60.0, 300.0, 1020.0, 880.0
        lx0, lx1 = 100.0, 960.0
        bar_h = 66
        if n >= 2:
            mid = (tp0 + tp1) / 2
            cut = 1
            best_d = None
            for i in range(1, n):
                dd = abs(spans_t[i][0] - mid)
                if best_d is None or dd < best_d:
                    best_d = dd
                    cut = i
            groups = [list(range(0, cut)), list(range(cut, n))]
        else:
            groups = [[0]]
        body_y0 = wy0 + bar_h + 16
        band = (wy1 - 6 - body_y0) / len(groups)
        lanes = []
        for gi, grp in enumerate(groups):
            if gi == 0:
                g_t0 = tp0
            else:
                g_t0 = (spans_t[grp[0]][0] + spans_t[grp[0] - 1][1]) / 2
            if gi == len(groups) - 1:
                g_t1 = tp1
            else:
                g_t1 = (spans_t[grp[-1]][1] + spans_t[grp[-1] + 1][0]) / 2
            y = body_y0 + gi * band
            box_h = 64
            wave_h = band - box_h - 32
            lanes.append({"chunks": grp, "t0": g_t0, "t1": g_t1, "x0": lx0, "x1": lx1, "wy": y, "wh": wave_h,
                          "by": y + wave_h + 6, "box_y": y + wave_h + 24, "box_h": box_h, "inside": True})
        bpx_max, bpx_min = 40, 30
    else:
        wx0, wy0, wx1, wy1 = 110.0, 220.0, 1810.0, 700.0
        lx0, lx1 = 150.0, 1770.0
        bar_h = 58
        y = wy0 + bar_h + 22 + 44
        wave_h = wy1 - 36 - y
        lanes = [{"chunks": list(range(n)), "t0": tp0, "t1": tp1, "x0": lx0, "x1": lx1, "wy": y, "wh": wave_h,
                  "by": wy1 - 28, "box_y": wy1 + 36, "box_h": 70, "inside": False}]
        bpx_max, bpx_min = 34, 24

    def tx_of(lane, tm):
        return lane["x0"] + (tm - lane["t0"]) / max(0.01, lane["t1"] - lane["t0"]) * (lane["x1"] - lane["x0"])

    # ---- boxes per lane (16:9: a second staggered row when one row cannot hold them)
    pad = 16 if P else 14
    seed = _seed(title, *chunks)
    for lane in lanes:
        spans_px = []
        texts = []
        for i in lane["chunks"]:
            a, b = spans_t[i]
            spans_px.append((tx_of(lane, a), tx_of(lane, b)))
            texts.append(chunks[i])
        # the box that gets the correction is sized for the longer of from / to
        sized = list(texts)
        if fix_i is not None and fix_i in lane["chunks"]:
            k = lane["chunks"].index(fix_i)
            frm = str(fix["from"])
            to = str(fix["to"])
            longer = frm if len(frm) >= len(to) else to
            sized[k] = texts[k][:fix_pos] + longer + texts[k][fix_pos + len(frm):]
        bpx, boxes = _pack(spans_px, sized, lane["x0"], lane["x1"], bpx_max, bpx_min, pad, 10)
        rows = [0] * len(boxes)
        truncated = False
        for bx, sz in zip(boxes, sized):
            if bx[2] != sz:
                truncated = True
        if not P and truncated and len(boxes) > 1:
            ev = []
            od = []
            for j in range(len(boxes)):
                if j % 2 == 0:
                    ev.append(j)
                else:
                    od.append(j)
            p_e, b_e = _pack([spans_px[j] for j in ev], [sized[j] for j in ev], lane["x0"], lane["x1"], bpx_max, bpx_min, pad, 10)
            p_o, b_o = _pack([spans_px[j] for j in od], [sized[j] for j in od], lane["x0"], lane["x1"], bpx_max, bpx_min, pad, 10)
            bpx = min(p_e, p_o)
            if p_e != p_o:
                # one size for both rows
                p_e, b_e = _pack([spans_px[j] for j in ev], [sized[j] for j in ev], lane["x0"], lane["x1"], bpx, bpx, pad, 10)
                p_o, b_o = _pack([spans_px[j] for j in od], [sized[j] for j in od], lane["x0"], lane["x1"], bpx, bpx, pad, 10)
            boxes = [None] * len(sized)
            for q, j in enumerate(ev):
                boxes[j] = b_e[q]
            for q, j in enumerate(od):
                boxes[j] = b_o[q]
                rows[j] = 1
        lane["spans_px"] = spans_px
        lane["boxes"] = boxes
        lane["rows"] = rows
        lane["bpx"] = bpx

    def box_inner(text, i, px):
        if i != fix_i:
            return _t(X, text)
        from h9 import fit as FT
        frm = str(fix["from"])
        to = str(fix["to"])
        pre = chunks[i][:fix_pos]
        real_from = chunks[i][fix_pos:fix_pos + len(frm)]
        post = chunks[i][fix_pos + len(frm):]
        longer = frm if len(frm) >= len(to) else to
        if text != pre + longer + post:
            return _t(X, text)                # cut by the ellipsis rule: no room for the slot
        slot_w = max(FT.width(frm), FT.width(to)) * px
        return (f'{_t(X, pre)}<span class="wa-slot" style="width:{slot_w:.0f}px"><span class="fr">{_t(X, real_from)}</span>'
                f'<span class="to">{_t(X, to)}</span></span>{_t(X, post)}')

    # ---- html: lanes (wave, played copy, playhead), brackets in the window; boxes (and 16:9 stems) over it
    step = 5.0                                   # 3 px bars, 2 px gaps
    body = ""
    over = ""
    for li, lane in enumerate(lanes):
        lw = lane["x1"] - lane["x0"]
        nb = int(lw // step)
        syl = []
        for (a, b), i in zip(lane["spans_px"], lane["chunks"]):
            syl.append((a, b, max(2.0, _weight(chunks[i]) * 0.9)))
        hs = _bars(seed + li, nb, syl, lane["x0"], step)
        rects = ""
        hh = lane["wh"]
        for q in range(nb):
            bh = max(3.0, hs[q] * hh)
            rects += f'<rect x="{q * step:.0f}" y="{(hh - bh) / 2:.1f}" width="3" height="{bh:.1f}" rx="1.5"/>'
        svg = f'<svg class="wa-wave" width="{lw:.0f}" height="{hh:.0f}" viewBox="0 0 {lw:.0f} {hh:.0f}">{rects}</svg>'
        body += (f'<div class="wa-lane l{li}" style="left:{lane["x0"] - wx0:.0f}px; top:{lane["wy"] - wy0 - bar_h:.0f}px; width:{lw:.0f}px; height:{hh:.0f}px">'
                 f'<div class="wa-mid" style="top:{hh / 2:.0f}px"></div>'
                 f'<div class="wa-base" style="position:absolute; inset:0">{svg}</div>'
                 f'<div class="wa-played" style="position:absolute; inset:0; clip-path:inset(0 100% 0 0)">{svg}</div></div>')
        body += f'<div class="wa-ph p{li}" style="left:{lane["x0"] - wx0:.0f}px; top:{lane["wy"] - wy0 - bar_h + 6:.0f}px; height:{hh - 6:.0f}px; opacity:0"></div>'
        for q, i in enumerate(lane["chunks"]):
            a, b = lane["spans_px"][q]
            bx, bw, btx = lane["boxes"][q]
            by = lane["box_y"] + lane["rows"][q] * (lane["box_h"] + 14)
            body += f'<div class="wa-brk b{i}" style="left:{a - wx0 + 1:.0f}px; top:{lane["by"] - wy0 - bar_h:.0f}px; width:{max(8.0, b - a - 2):.0f}px"></div>'
            box_cls = "wa-box" if lane["inside"] else "wa-box out"
            box = (f'<div class="{box_cls} x{i}" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{lane["box_h"]}px; font-size:{lane["bpx"]}px">'
                   f'<span>{box_inner(btx, i, lane["bpx"])}</span></div>')
            if not lane["inside"]:
                sx = (a + b) / 2
                if sx < bx + 12:
                    sx = bx + 12
                if sx > bx + bw - 12:
                    sx = bx + bw - 12
                top_ = lane["by"] + 12
                over += f'<div class="wa-stem s{i}" style="left:{sx:.0f}px; top:{top_:.0f}px; height:{by - top_:.0f}px"></div>'
            over += box
    if not P:
        # a time ruler over the wave: a tick every 0.5 s, labelled every second (every 2 s on long clips)
        lane = lanes[0]
        every = 1.0 if clip_len <= 8 else 2.0
        k = 0
        while k * 0.5 <= clip_len + 0.001:
            sec = k * 0.5
            x = tx_of(lane, tp0 + sec) - wx0
            major = abs(sec / every - round(sec / every)) < 1e-6
            body += f'<div class="wa-tick" style="left:{x:.1f}px; top:{22 + (0 if major else 14)}px; height:{30 if major else 16}px"></div>'
            if major and x < lane["x1"] - wx0 - 40:
                body += f'<div class="wa-tl" style="left:{x + 32:.1f}px; top:20px; font-size:24px">{_t(X, f"{sec:g}s")}</div>'
            k += 1
    right = f'<span class="wa-tc">{_t(X, _tc(0))}</span> / {_t(X, _tc(clip_len))}'
    win, _bh = _window(X, wx0, wy0, wx1 - wx0, wy1 - wy0, title, P, body, right=right, cls="wa-win")

    low = ""
    card_vis = 0
    row_h = 76 if P else 66
    if P:
        # 9:16: chips, then the caption-file card filling with one timecoded row per aligned chunk
        y = wy1 + 40
        if chips:
            ch_html, ch_h = _chips_html(X, chips, wx0, y, 960 - wx0, 32, P, cls="w4-chip wa-chip")
            low += ch_html
            y += ch_h + 22
        cy1 = TXT_FLOOR_V                 # the rows (text) stop above the caption band; the card runs off the bottom
        card_x0, card_x1 = wx0, 1020.0
        head_h = 80
        avail = cy1 - y - head_h - 10
        card_vis = max(2, int(avail // row_h))
        card_h = X.H + 40 - y
        rows_h = card_vis * row_h
        rows_html = ""
        tw_ = 960.0 - card_x0 - 56 - 20 - 30 * 0.6 * 7
        for i, c in enumerate(chunks):
            a, b = spans_t[i]
            tc = _tc(a - tp0)
            if i == fix_i:
                frm = str(fix["from"])
                to = str(fix["to"])
                rpx, _x = _fit_line(c + " " + to, tw_, 40, 32)
                txt = (f'{_t(X, c[:fix_pos])}<span class="fr">{_t(X, c[fix_pos:fix_pos + len(frm)])}</span> '
                       f'<span class="to">{_t(X, to)}</span>{_t(X, c[fix_pos + len(frm):])}')
            else:
                rpx, cut_ = _fit_line(c, tw_, 40, 32)
                txt = _t(X, cut_)
            rows_html += (f'<div class="wa-row r{i}" style="top:{i * row_h:.0f}px; height:{row_h}px">'
                          f'<span class="tc" style="font-size:30px">{_t(X, tc)}</span><span class="tx" style="font-size:{rpx}px">{txt}</span></div>')
        low += (f'<div class="wa-card" data-layout-allow-overflow style="left:{card_x0:.0f}px; top:{y:.0f}px; width:{card_x1 - card_x0:.0f}px; height:{card_h:.0f}px">'
                f'<div class="wa-ch" style="top:0; height:{head_h}px; right:{card_x1 - 960 + 28:.0f}px"><small style="font-size:32px">{_t(X, "字幕 · 自动对齐")}</small>'
                f'<b style="font-size:34px"><span class="wa-cnt">0</span> / {n}</b></div>'
                f'<div class="wa-rows" style="top:{head_h}px; height:{rows_h:.0f}px"><div class="wa-list">{rows_html}</div></div></div>')
    else:
        # 16:9: the fix line bottom left, chips bottom right
        fy = 868.0
        if max(lanes[0]["rows"]) > 0:
            fy = 884.0
        if fix:
            frm = str(fix["from"])
            to = str(fix["to"])
            fpx, _x = _fit_line("纠错 " + frm + " → " + to, 860, 40, 28)
            low += (f'<div class="wa-fix" style="left:110px; top:{fy - fpx * 0.65:.0f}px; font-size:{fpx}px">'
                    f'<small style="font-size:24px">纠错</small><span class="fr">{_t(X, frm)}</span><span class="ar">→</span><span class="to">{_t(X, to)}</span></div>')
        if chips:
            from h9 import fit as FT
            cw_ = 0.0
            for c in chips:
                cw_ += FT.width(c) * 26 + 28 + 36 + 14
            cx_ = max(1000.0, 1810 - cw_)
            ch_html, ch_h = _chips_html(X, chips, cx_, fy - 23, 1810 - cx_, 26, P, cls="w4-chip wa-chip")
            low += ch_html

    inner = win + over + low
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body w4" style="--bad:{col["bad"]}; --good-ink:{col["mark"]}">{inner}</div>')

    # ---- entrances: 16:9 the window wipes open from the left edge; 9:16 it rises, then the card slides up
    if P:
        X.tw(f'tl.fromTo("{s} .wa-win", {{y:80, opacity:0}}, {{y:0, opacity:1, duration:0.5, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .wa-card", {{y:120, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 0% 0)", duration:0.55, ease:"expo.out", immediateRender:true}}, {t + 0.2:.3f});')
        X.tw(f'tl.fromTo("{s} .wa-chip", {{x:-40, opacity:0}}, {{x:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.3:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .wa-win", {{clipPath:"inset(0 100% 0 0)", x:-40}}, {{clipPath:"inset(0 0% 0 0)", x:0, duration:0.6, ease:"expo.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .wa-chip", {{y:30, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.35:.3f});')
    X.tw(f'tl.fromTo("{s} .wa-base", {{scaleY:0.1}}, {{scaleY:1, transformOrigin:"50% 50%", duration:0.45, ease:"power3.out", immediateRender:true}}, {t + 0.18:.3f});')
    X.tw(f'tl.to("{s} .wa-ph", {{opacity:1, duration:0.15}}, {max(t + 0.2, tp0 - 0.12):.3f});')

    # ---- snaps: as the playhead reaches each chunk, its box rises onto its span, the bracket draws, the row lands
    cnt_times = []
    for i in range(n):
        at = spans_t[i][0] - 2 * fr
        X.tw(f'tl.fromTo("{s} .wa-box.x{i}", {{y:54, scaleX:0.86, opacity:0}}, {{y:0, scaleX:1, opacity:1, duration:{6 * fr:.3f}, ease:"back.out(2.6)", immediateRender:true}}, {at:.3f});')
        X.tw(f'tl.fromTo("{s} .wa-brk.b{i}", {{scaleX:0, opacity:0}}, {{scaleX:1, opacity:1, duration:{4 * fr:.3f}, ease:"power2.out", immediateRender:true}}, {at:.3f});')
        if not P:
            X.tw(f'tl.fromTo("{s} .wa-stem.s{i}", {{scaleY:0}}, {{scaleY:1, duration:{4 * fr:.3f}, ease:"power2.out", immediateRender:true}}, {at:.3f});')
        else:
            X.tw(f'tl.fromTo("{s} .wa-row.r{i}", {{x:-60, opacity:0}}, {{x:0, opacity:1, duration:0.3, ease:"power3.out", immediateRender:true}}, {at + 2 * fr:.3f});')
        cnt_times.append(round(at + 2 * fr, 3))
        if i < 6 or i == n - 1:
            X.sfx(at, "tick", 0.3)

    # ---- the fix: shake, strike, the correction slides in
    fix_t = None
    if fix:
        if fix_i is not None:
            fix_t = spans_t[fix_i][0] + 6 * fr + 0.22
        else:
            fix_t = tp1 + 0.1
        if fix_t > t + d - 0.75:
            fix_t = t + d - 0.75
        f1 = fix_t + 5 * fr
        if fix_i is not None:
            sel = f"{s} .wa-box.x{fix_i}"
            X.tw(f'tl.to("{sel}", {{keyframes:[{{x:6, duration:{fr:.4f}}}, {{x:-6, duration:{fr:.4f}}}, {{x:5, duration:{fr:.4f}}}, {{x:-4, duration:{fr:.4f}}}, {{x:0, duration:{fr:.4f}}}], ease:"none"}}, {fix_t:.3f});')
            X.tw(f'tl.to("{sel}", {{borderColor:"{col["bad"]}", duration:0.06}}, {fix_t:.3f});')
            X.tw(f'tl.fromTo("{sel} .wa-slot .fr", {{"--p":0}}, {{"--p":1, duration:0.18, ease:"power2.inOut", immediateRender:true}}, {f1:.3f});')
            X.tw(f'tl.to("{sel} .wa-slot .fr", {{y:-30, opacity:0, duration:0.22, ease:"power2.in"}}, {f1 + 0.3:.3f});')
            X.tw(f'tl.fromTo("{sel} .wa-slot .to", {{y:30, opacity:0}}, {{y:0, opacity:1, duration:0.26, ease:"power3.out", immediateRender:true}}, {f1 + 0.36:.3f});')
            X.tw(f'tl.to("{sel}", {{borderColor:"{col["good"]}", duration:0.15}}, {f1 + 0.36:.3f});')
            if P:
                X.tw(f'tl.fromTo("{s} .wa-row.r{fix_i} .fr", {{"--p":0}}, {{"--p":1, duration:0.18, ease:"power2.inOut", immediateRender:true}}, {f1:.3f});')
                X.tw(f'tl.fromTo("{s} .wa-row.r{fix_i} .to", {{opacity:0, x:20}}, {{opacity:1, x:0, duration:0.26, ease:"power3.out", immediateRender:true}}, {f1 + 0.36:.3f});')
        if not P:
            X.tw(f'tl.fromTo("{s} .wa-fix", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 -4% 0 0)", duration:0.4, ease:"power3.out", immediateRender:true}}, {fix_t - 0.1:.3f});')
            X.tw(f'tl.fromTo("{s} .wa-fix .fr", {{"--p":0}}, {{"--p":1, duration:0.2, ease:"power2.inOut", immediateRender:true}}, {f1:.3f});')
            X.tw(f'tl.fromTo("{s} .wa-fix .to", {{opacity:0, x:-16}}, {{opacity:1, x:0, duration:0.26, ease:"power3.out", immediateRender:true}}, {f1 + 0.36:.3f});')
        X.sfx(fix_t, "click", 0.4)

    # ---- the playhead, played fill, timecode and the caption-file scroll: one proxy tween
    lanes_js = []
    for lane in lanes:
        lanes_js.append([round(lane["t0"], 4), round(lane["t1"], 4), round(lane["x0"] - wx0, 1), round(lane["x1"] - lane["x0"], 1)])
    js = """(()=>{
  const R = document.querySelector("__S__");
  if (!R) return;
  const L = __L__;
  const played = [...R.querySelectorAll(".wa-played")], ph = [...R.querySelectorAll(".wa-ph")];
  const tcEl = R.querySelector(".wa-tc"), cnt = R.querySelector(".wa-cnt"), list = R.querySelector(".wa-list");
  const C = __C__, tp0 = __TP0__, tp1 = __TP1__, t0 = __T0__, vis = __VIS__, rowH = __RH__;
  function draw(lt) {
    const time = t0 + lt;
    const tm = Math.max(tp0, Math.min(tp1, time));
    for (let i = 0; i < L.length; i++) {
      const u = Math.max(0, Math.min(1, (tm - L[i][0]) / (L[i][1] - L[i][0])));
      played[i].style.clipPath = "inset(0 " + ((1 - u) * 100).toFixed(2) + "% 0 0)";
      const here = (tm >= L[i][0] && (tm < L[i][1] || i === L.length - 1));
      ph[i].style.visibility = here ? "visible" : "hidden";
      ph[i].style.left = (L[i][2] + u * L[i][3]).toFixed(1) + "px";
    }
    if (tcEl) {
      const sec = tm - tp0, m = Math.floor(sec / 60), r = sec - m * 60;
      tcEl.textContent = String(m).padStart(2, "0") + ":" + r.toFixed(1).padStart(4, "0");
    }
    let k = 0;
    for (let j = 0; j < C.length; j++) if (time >= C[j]) k++;
    if (cnt) cnt.textContent = String(k);
    if (list && vis > 0) {
      let off = 0;
      for (let j = vis; j < C.length; j++) {
        let u = (time - C[j]) / 0.25;
        if (u < 0) u = 0;
        if (u > 1) u = 1;
        off += 1 - Math.pow(1 - u, 3);
      }
      list.style.transform = "translateY(" + (-off * rowH).toFixed(1) + "px)";
    }
  }
  const V = { t: 0 };
  draw(0);
  tl.fromTo(V, { t: 0 }, { t: __D__, duration: __D__, ease: "none", immediateRender: false, onUpdate: () => draw(V.t) }, __T0__);
})();"""
    js = (js.replace("__S__", s).replace("__L__", A.js(lanes_js)).replace("__C__", A.js(cnt_times))
            .replace("__TP0__", f"{tp0:.4f}").replace("__TP1__", f"{tp1:.4f}").replace("__T0__", f"{t:.3f}")
            .replace("__VIS__", str(card_vis)).replace("__RH__", str(row_h)).replace("__D__", f"{d:.3f}"))
    X.tw(js)
    end = tp1
    if fix_t is not None and fix_t + 0.7 > end:
        end = fix_t + 0.7
    A.hold_push(X, f"{s} .w4", end + 0.15, t + d, 1.025, origin=f"{(wx0 + wx1) / 2:.0f}px {(wy0 + wy1) / 2:.0f}px")


# ------------------------------------------------------------------------------------------------ qc_sheet
def _frame_still(X, src, at):
    """(project url) of one frame of a clip at `at` seconds (cached in the build), or the picture itself."""
    import hashlib
    import subprocess
    from h9 import fit as FT
    a = FT._abs(X, src)
    if not FT.is_video(a):
        return X.asset(a)
    key = hashlib.sha1(f"{a}|{at:.2f}".encode("utf-8")).hexdigest()[:12]
    dst = X.out / "assets" / "img" / f"qc_{key}.jpg"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(a), "-frames:v", "1",
                        "-vf", "scale=480:-2", "-q:v", "4", str(dst)], check=True)
    return f"assets/img/{dst.name}"


def _skeleton(rng, k, w, h):
    """one drawn frame of a generic film (no text): title card, chart, talking head, text page, horizon, split.
    Shapes in the style tokens; proportions jittered by the seeded rng so no two frames are the same."""
    kind = k % 6
    out = ""

    def blk(x, y, ww, hh, colr, r=3):
        return (f'<i class="qc-sk" style="left:{x * w:.1f}px; top:{y * h:.1f}px; width:{ww * w:.1f}px; height:{hh * h:.1f}px; '
                f'background:{colr}; border-radius:{r}px"></i>')

    fg = "color-mix(in srgb, var(--card-fg) 70%, transparent)"
    soft = "color-mix(in srgb, var(--card-fg) 28%, transparent)"
    acc = "var(--accent)"
    j = rng.uniform(-0.06, 0.06)
    if kind == 0:
        out += blk(0.12, 0.34 + j, 0.62, 0.14, fg)
        out += blk(0.12, 0.54 + j, 0.4, 0.07, soft)
        out += blk(0.12, 0.66 + j, 0.18, 0.05, acc)
    elif kind == 1:
        base = 0.84
        for q in range(4):
            bh = rng.uniform(0.18, 0.62)
            out += blk(0.16 + q * 0.18, base - bh, 0.12, bh, acc if q == 2 else soft, 2)
        out += blk(0.1, base, 0.8, 0.025, fg, 1)
    elif kind == 2:
        cx = 0.5 + j
        out += (f'<i class="qc-sk" style="left:{(cx - 0.11) * w:.1f}px; top:{0.2 * h:.1f}px; width:{0.22 * w:.1f}px; height:{0.22 * w:.1f}px; '
                f'border-radius:50%; background:{soft}"></i>')
        out += f'<i class="qc-sk" style="left:{(cx - 0.24) * w:.1f}px; top:{0.62 * h:.1f}px; width:{0.48 * w:.1f}px; height:{0.5 * h:.1f}px; border-radius:{0.2 * w:.0f}px {0.2 * w:.0f}px 0 0; background:{soft}"></i>'
        out += blk(0.08, 0.78, 0.36, 0.1, acc)
    elif kind == 3:
        for q in range(4):
            ww = rng.uniform(0.5, 0.78) if q < 3 else 0.34
            out += blk(0.11, 0.24 + q * 0.15, ww, 0.07, fg if q == 0 else soft)
    elif kind == 4:
        hz = 0.56 + j
        out += f'<i class="qc-sk" style="left:0; top:0; width:{w:.1f}px; height:{hz * h:.1f}px; background:color-mix(in srgb, var(--accent) 22%, transparent)"></i>'
        out += (f'<i class="qc-sk" style="left:{0.64 * w:.1f}px; top:{0.16 * h:.1f}px; width:{0.14 * w:.1f}px; height:{0.14 * w:.1f}px; '
                f'border-radius:50%; background:{acc}"></i>')
        out += f'<i class="qc-sk" style="left:0; top:{hz * h:.1f}px; width:{w:.1f}px; height:{(1 - hz) * h:.1f}px; background:{soft}"></i>'
    else:
        out += f'<i class="qc-sk" style="left:0; top:0; width:{0.48 * w:.1f}px; height:{h:.1f}px; background:{soft}"></i>'
        out += blk(0.56, 0.3 + j, 0.34, 0.1, fg)
        out += blk(0.56, 0.48 + j, 0.26, 0.06, soft)
        out += blk(0.56, 0.6 + j, 0.3, 0.06, soft)
    return out


def _defect(name, w, h):
    """the flaw a failing frame shows, chosen from the check's name: black frame, white flash, overlapping text bars,
    else a hatch in the alert colour."""
    nm = str(name)
    if "黑" in nm or "black" in nm.lower():
        return '<div class="qc-def blk"></div>'
    if "闪" in nm or "白" in nm or "flash" in nm.lower():
        return '<div class="qc-def wht"></div>'
    if "重叠" in nm or "文字" in nm or "字幕" in nm or "overlap" in nm.lower() or "text" in nm.lower():
        out = '<div class="qc-def ovl">'
        out += f'<i style="left:{0.1 * w:.1f}px; top:{0.56 * h:.1f}px; width:{0.66 * w:.1f}px; height:{0.13 * h:.1f}px; background:var(--card-fg)"></i>'
        out += f'<i style="left:{0.24 * w:.1f}px; top:{0.62 * h:.1f}px; width:{0.62 * w:.1f}px; height:{0.13 * h:.1f}px; background:var(--bad); opacity:.9"></i>'
        out += f'<i style="left:{0.16 * w:.1f}px; top:{0.5 * h:.1f}px; width:{0.42 * w:.1f}px; height:{0.1 * h:.1f}px; background:color-mix(in srgb, var(--card-fg) 60%, transparent)"></i>'
        return out + '</div>'
    return '<div class="qc-def oth"></div>'


def qc_sheet(X, cid, t, d, p):
    """逐帧检查 QC Sheet: a contact sheet of the film in a window; a scan bar sweeps it row by row, once per check, each
    sweep faster than the last. Frames it passes get a small tick per check; each check in the list lights while its
    sweep runs and gets a big tick when it completes. With `fail`, that check's sweep stops on that frame: the frame is
    outlined in the alert colour and labelled, it flips to a corrected frame (green, the scan resumes) — or stays
    flagged when `fixed` is false. Without `media`, the frames are drawn generically from the style. 16:9: grid window
    left, checklist right with big ticks; 9:16: grid window on top, the checks stacked under it."""
    import random
    F_ = "qc_sheet"
    G = A.frame(X, p)
    P = G["P"]
    col = _cols(X, p)
    title = str(p.get("title") or "成片 / 导出前检查")
    checks = _as_list(p.get("checks")) or ["黑屏", "闪帧", "文字重叠"]
    if len(checks) > 5:
        _warn(f"{F_}: {len(checks)} checks, showing the first 5")
        checks = checks[:5]
    nc = len(checks)

    # ---- frames: media (cycled up to 8, sampled down to 40) or drawn skeletons
    media = p.get("media") or []
    if isinstance(media, (str, dict)):
        media = [media]
    srcs = []
    for m in media:
        if isinstance(m, dict):
            m = m.get("src") or m.get("image") or m.get("video") or ""
        m = str(m).strip()
        if m:
            srcs.append(_path(m))
    frames = []
    if srcs:
        from h9 import fit as FT
        if len(srcs) > 40:
            pick = []
            for q in range(40):
                pick.append(srcs[int(q * len(srcs) / 40)])
            srcs = pick
        # each clip gives as many frames as it appears: evenly spaced through it
        uses = {}
        order = []
        k = 0
        while len(order) < max(8, len(srcs)):
            order.append(srcs[k % len(srcs)])
            k += 1
        for src in order:
            uses[src] = uses.get(src, 0) + 1
        seen = {}
        for src in order:
            q = seen.get(src, 0)
            seen[src] = q + 1
            at = 0.5
            a = FT._abs(X, src)
            if FT.is_video(a):
                dur = FT.duration(a) or 4.0
                at = dur * (q + 0.5) / uses[src]
                if at > dur - 0.2:
                    at = max(0.0, dur - 0.2)
            frames.append({"src": src, "at": at})
        ar_media = FT.aspect(X, srcs[0], 16 / 9)
    else:
        try:
            cnt = int(p.get("count") or (24 if not P else 16))
        except (TypeError, ValueError):
            cnt = 24 if not P else 16
        cnt = max(8, min(40, cnt))
        for q in range(cnt):
            frames.append({"src": None, "at": 0})
        ar_media = 16 / 9
    N = len(frames)

    fail = p.get("fail") if isinstance(p.get("fail"), dict) else None
    fi = fc = None
    fixed = True
    if fail:
        try:
            fi = int(fail.get("index", 0))
        except (TypeError, ValueError):
            fi = 0
        if fi < 0:
            fi = N + fi
        fi = max(0, min(N - 1, fi))
        try:
            fc = int(fail.get("check", 0))
        except (TypeError, ValueError):
            fc = 0
        if fc < 0:
            fc = nc + fc
        fc = max(0, min(nc - 1, fc))
        fixed = fail.get("fixed", True) is not False

    # ---- geometry
    if P:
        # 9:16: the checklist on top, the contact-sheet window under it, running off the bottom edge (picture)
        list_x0, list_x1 = 60.0, 960.0
        list_y0 = 300.0
        list_y1 = list_y0 + 100.0 * nc
        wx0, wx1 = 60.0, 1020.0
        wy0 = list_y1 + 28.0
        wy1 = X.H + 40.0
        cols_opts = [4]
    else:
        wx0, wy0, wx1, wy1 = 110.0, 150.0, 1150.0, 870.0
        cols_opts = [5, 6, 7, 8]
        list_x0, list_x1 = 1230.0, 1810.0
        list_y0, list_y1 = 160.0, 870.0
    bar_h = 66 if P else 58
    gpad = 22 if P else 20
    gap = 12 if P else 10
    gx0 = wx0 + gpad
    gy0 = wy0 + bar_h + gpad
    gw_ = (wx1 - wx0) - gpad * 2
    gh_ = (min(wy1, X.H - 24.0) - wy0) - bar_h - gpad * 2      # cells only in the visible part of a bleeding window
    # cells fill the grid area (pictures are cropped to them); only extreme shapes are limited
    target = max(0.6, min(2.2, ar_media))
    best = None
    for c_ in cols_opts:
        r_ = int(math.ceil(N / c_))
        cw = (gw_ - gap * (c_ - 1)) / c_
        ch = (gh_ - gap * (r_ - 1)) / r_
        ar = cw / ch
        score = abs(math.log(ar / target))
        if best is None or score < best[0]:
            best = (score, c_, r_, cw, ch)
    unused, cols, rows, cw, ch = best
    lo = 0.7 if P else 1.0
    hi = 5.0 if P else 2.5
    if cw / ch > hi:
        cw = ch * hi
    if cw / ch < lo:
        ch = cw / lo
    grid_w = cols * cw + gap * (cols - 1)
    grid_h = rows * ch + gap * (rows - 1)
    ox = gx0 + (gw_ - grid_w) / 2
    oy = gy0 + (gh_ - grid_h) / 2

    # ---- timing: one sweep per check, each 0.72× the last; a pause on the failing frame
    ts = t + min(0.55, d * 0.15)
    te = t + d * 0.85
    pause = 1.15 if fail else 0.0
    if fail and te - ts < 2.2:
        pause = max(0.6, (te - ts) * 0.35)
    gapk = 0.12
    weights = []
    for k in range(nc):
        weights.append(0.72 ** k)
    D0 = (te - ts - pause - gapk * (nc - 1)) / sum(weights)
    if D0 < 0.25:
        D0 = 0.25
    sweeps = []                                  # per check: [start, end, segments [[t0, t1, p0, p1]]]
    cur = ts
    pause_t = None
    for k in range(nc):
        dur = D0 * weights[k]
        segs = []
        if fail and k == fc:
            p_stop = fi + 0.5
            t_stop = cur + dur * p_stop / N
            segs.append([cur, t_stop, 0.0, p_stop])
            segs.append([t_stop, t_stop + pause, p_stop, p_stop])
            segs.append([t_stop + pause, cur + dur + pause, p_stop, float(N)])
            pause_t = t_stop
            end = cur + dur + pause
        else:
            segs.append([cur, cur + dur, 0.0, float(N)])
            end = cur + dur
        sweeps.append([round(cur, 4), round(end, 4), [[round(a, 4), round(b, 4), round(c, 3), round(e, 3)] for a, b, c, e in segs]])
        cur = end + gapk

    def time_at(k, pos):
        for a, b, p0, p1 in sweeps[k][2]:
            if p1 > p0 and p0 <= pos <= p1:
                return a + (b - a) * (pos - p0) / (p1 - p0)
        return sweeps[k][1]

    passed = []                                  # per check, per frame: when the scan passes its centre
    for k in range(nc):
        row = []
        for j in range(N):
            row.append(round(time_at(k, j + 0.5), 4))
        passed.append(row)

    # ---- html: the grid
    rng = random.Random(_seed(title, N, *checks))
    dot = 7 if (ch < 70 or cw < 110) else 10
    grid = ""
    for j, fr_ in enumerate(frames):
        r_ = j // cols
        c_ = j % cols
        x = ox + c_ * (cw + gap) - wx0
        y = oy + r_ * (ch + gap) - wy0 - bar_h
        if fr_["src"]:
            pic = f'<img src="{_frame_still(X, fr_["src"], fr_["at"])}" alt="">'
        else:
            pic = _skeleton(rng, j * 5 + rng.randrange(6), cw, ch)
        defect = ""
        if fail and j == fi:
            defect = _defect(checks[fc], cw, ch)
        dots = ""
        for k in range(nc):
            dots += f'<i class="d{k}" style="width:{dot}px; height:{dot}px"></i>'
        grid += (f'<div class="qc-f f{j}" style="left:{x:.1f}px; top:{y:.1f}px; width:{cw:.1f}px; height:{ch:.1f}px">'
                 f'<div class="qc-in">{pic}{defect}</div><div class="qc-ring"></div>'
                 + ('<div class="qc-flag"></div>' if (fail and j == fi) else "")
                 + f'<div class="qc-dots">{dots}</div></div>')
    scan = f'<div class="qc-scan" style="top:0; height:{ch + 10:.0f}px"></div>'
    label = ""
    if fail:
        lpx = 32 if P else 24
        r_ = fi // cols
        c_ = fi % cols
        fx_ = ox + c_ * (cw + gap) - wx0
        fy_ = oy + r_ * (ch + gap) - wy0 - bar_h
        from h9 import fit as FT
        lab_w = FT.width(checks[fc]) * lpx + lpx + 40
        lab_w2 = FT.width("已替换") * lpx + lpx + 40
        lw_ = max(lab_w, lab_w2)
        lx = fx_ + cw / 2 - lw_ / 2
        lx = max(8.0, min(gw_ + gpad * 2 - lw_ - 8, lx))
        if P:
            lx = max(8.0, min(960.0 - wx0 - lw_, lx))      # a label is text: clear of the 9:16 button zone
        ly = fy_ - lpx * 1.6 - 6
        if ly < 6:
            ly = fy_ + ch + 8
        label = (f'<div class="qc-lab bad" style="left:{lx:.0f}px; top:{ly:.0f}px; font-size:{lpx}px">{ICON_X}{_t(X, _fit_line(checks[fc], 300, lpx, lpx)[1])}</div>'
                 f'<div class="qc-lab ok" style="left:{lx:.0f}px; top:{ly:.0f}px; font-size:{lpx}px">{ICON_OK}{_t(X, "已替换")}</div>')
    right = f'<span class="qc-fr">0</span> / {N} 帧'
    win, _bh = _window(X, wx0, wy0, wx1 - wx0, wy1 - wy0, title, P, grid + scan + label, right=right, cls="qc-win")

    # ---- html: the checklist
    lst = ""
    lh_ = list_y1 - list_y0
    if P:
        row_h = min(104.0, lh_ / nc)
        npx = int(min(52, row_h * 0.62))
        if npx < 40:
            npx = 40
        box = int(min(60, row_h * 0.7))
        spx = 30
    else:
        row_h = min(170.0, lh_ / nc)
        npx = 60 if row_h >= 126 else max(44, int(row_h * 0.46))
        box = int(min(84, npx * 1.3))
        spx = 24
    for k, nm in enumerate(checks):
        y = k * row_h
        if P:
            name_w = (list_x1 - list_x0) - box - 24 - 250
            nfit = _fit_line(nm, name_w, npx, 36)
            lst += (f'<div class="qc-item i{k}" style="top:{y:.0f}px; height:{row_h:.0f}px">'
                    f'<div class="qc-box" style="top:{(row_h - box) / 2:.0f}px; width:{box}px; height:{box}px; font-size:{box * 0.7:.0f}px">{ICON_OK}<span class="x">{ICON_X}</span></div>'
                    f'<div class="qc-nm" style="left:{box + 24}px; top:{(row_h - nfit[0] * 1.15) / 2:.0f}px; font-size:{nfit[0]}px">{_t(X, nfit[1])}</div>'
                    f'<div class="qc-st" style="right:0; top:{(row_h - spx * 1.2) / 2:.0f}px; font-size:{spx}px">待检查</div>'
                    f'<div class="qc-bar" style="left:{box + 24}px; top:{row_h - 8:.0f}px"><i></i></div></div>')
        else:
            name_w = (list_x1 - list_x0) - box - 28
            nfit = _fit_line(nm, name_w, npx, 40)
            ny = (row_h - nfit[0] * 1.15 - spx * 1.5 - 10) / 2
            lst += (f'<div class="qc-item i{k}" style="top:{y:.0f}px; height:{row_h:.0f}px">'
                    f'<div class="qc-box" style="top:{ny + (nfit[0] * 1.15 - box) / 2 + 4:.0f}px; width:{box}px; height:{box}px; font-size:{box * 0.7:.0f}px">{ICON_OK}<span class="x">{ICON_X}</span></div>'
                    f'<div class="qc-nm" style="left:{box + 28}px; top:{ny:.0f}px; font-size:{nfit[0]}px">{_t(X, nfit[1])}</div>'
                    f'<div class="qc-st" style="left:{box + 28}px; top:{ny + nfit[0] * 1.15 + 8:.0f}px; font-size:{spx}px">待检查</div>'
                    f'<div class="qc-bar" style="left:{box + 28}px; top:{row_h - 14:.0f}px"><i></i></div></div>')
    lst = f'<div class="qc-list" style="left:{list_x0:.0f}px; top:{list_y0:.0f}px; width:{list_x1 - list_x0:.0f}px; height:{lh_:.0f}px">{lst}</div>'
    inner = win + lst
    _css(X)
    from h9.aefx import _contrast
    on_bad = "#111111" if _contrast("#111111", col["bad"]) >= _contrast("#ffffff", col["bad"]) else "#ffffff"
    on_good = "#111111" if _contrast("#111111", col["good"]) >= _contrast("#ffffff", col["good"]) else "#ffffff"
    sv = f"--bad:{col['bad']}; --good:{col['good']}; --on-bad:{on_bad}; --on-good:{on_good}"
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body w4" style="{sv}">{inner}</div>')

    # ---- entrances: 16:9 frames deal in column by column from the left, list from the right; 9:16 rows drop in
    if P:
        X.tw(f'tl.fromTo("{s} .qc-win", {{y:-60, opacity:0}}, {{y:0, opacity:1, duration:0.45, ease:"power4.out", immediateRender:true}}, {t + 0.03:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-f", {{y:-30, opacity:0}}, {{y:0, opacity:1, duration:0.3, ease:"power3.out", stagger:{{each:{min(0.02, 0.3 / N):.4f}, from:"start"}}, immediateRender:true}}, {t + 0.15:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-item", {{y:40, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 0% 0)", duration:0.4, ease:"expo.out", stagger:0.06, immediateRender:true}}, {t + 0.25:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .qc-win", {{x:-80, opacity:0}}, {{x:0, opacity:1, duration:0.5, ease:"power4.out", immediateRender:true}}, {t + 0.03:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-f", {{scale:0.6, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(1.6)", stagger:{{each:{min(0.018, 0.3 / N):.4f}, grid:[{rows}, {cols}], axis:"x"}}, immediateRender:true}}, {t + 0.15:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-item", {{x:80, opacity:0}}, {{x:0, opacity:1, duration:0.45, ease:"expo.out", stagger:0.07, immediateRender:true}}, {t + 0.2:.3f});')
    X.tw(f'tl.to("{s} .qc-scan", {{opacity:1, duration:0.1}}, {ts - 0.08:.3f});')
    X.tw(f'tl.to("{s} .qc-scan", {{opacity:0, duration:0.2}}, {sweeps[-1][1]:.3f});')

    # ---- each check: lights while its sweep runs, then its tick lands (or the cross, when the fault stays)
    fg = col.get("fg", "#111111")
    acc = col.get("accent", "#e2321f")
    for k in range(nc):
        a, b = sweeps[k][0], sweeps[k][1]
        X.tw(f'tl.to("{s} .qc-item.i{k} .qc-nm", {{color:"{acc}", duration:0.12}}, {a:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-item.i{k} .qc-nm", {{x:0}}, {{keyframes:[{{x:10, duration:0.1}}, {{x:0, duration:0.25}}]}}, {a:.3f});')
        X.tw(f'tl.to("{s} .qc-item.i{k} .qc-nm", {{color:"{fg}", duration:0.2}}, {b:.3f});')
        bad_end = fail and k == fc and not fixed
        if bad_end:
            X.tw(f'tl.to("{s} .qc-item.i{k} .qc-box", {{borderColor:"{col["bad"]}", duration:0.1}}, {b:.3f});')
            X.tw(f'tl.fromTo("{s} .qc-item.i{k} .qc-box .x", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2.2)", immediateRender:true}}, {b:.3f});')
        else:
            X.tw(f'tl.to("{s} .qc-item.i{k} .qc-box", {{borderColor:"{col["good"]}", duration:0.1}}, {b:.3f});')
            X.tw(f'tl.fromTo("{s} .qc-item.i{k} .qc-box svg", {{opacity:0, scale:0.3}}, {{opacity:1, scale:1, duration:0.3, ease:"back.out(2.2)", immediateRender:true}}, {b:.3f});')
        X.sfx(b, "tick", 0.4)

    # ---- the failing frame: flag + label, flip to the corrected frame, green
    if fail:
        sel = f"{s} .qc-f.f{fi}"
        X.tw(f'tl.fromTo("{sel} .qc-flag", {{opacity:0, scale:1.25}}, {{opacity:1, scale:1, duration:0.2, ease:"power3.out", immediateRender:true}}, {pause_t:.3f});')
        X.tw(f'tl.fromTo("{s} .qc-lab.bad", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.22, ease:"back.out(2)", immediateRender:true}}, {pause_t + 0.05:.3f});')
        X.tw(f'tl.fromTo("{sel}", {{x:0}}, {{keyframes:[{{x:5, duration:0.035}}, {{x:-5, duration:0.035}}, {{x:3, duration:0.035}}, {{x:0, duration:0.035}}]}}, {pause_t:.3f});')
        X.sfx(pause_t, "beep", 0.35)
        if fixed:
            f0 = pause_t + pause * 0.45
            X.tw(f'tl.to("{sel} .qc-in", {{rotationY:90, duration:0.15, ease:"power2.in"}}, {f0:.3f});')
            X.tw(f'tl.set("{sel} .qc-def", {{opacity:0}}, {f0 + 0.15:.3f});')
            X.tw(f'tl.fromTo("{sel} .qc-in", {{rotationY:-90}}, {{rotationY:0, duration:0.2, ease:"power2.out", immediateRender:false}}, {f0 + 0.15:.3f});')
            X.tw(f'tl.to("{sel} .qc-flag", {{borderColor:"{col["good"]}", duration:0.15}}, {f0 + 0.3:.3f});')
            X.tw(f'tl.to("{s} .qc-lab.bad", {{opacity:0, y:-10, duration:0.15}}, {f0 + 0.2:.3f});')
            X.tw(f'tl.fromTo("{s} .qc-lab.ok", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.22, ease:"back.out(2)", immediateRender:true}}, {f0 + 0.3:.3f});')
            X.sfx(f0, "whoosh_soft", 0.3)
        else:
            # left flagged: the warning frame keeps pulsing through the pause, so the hold is never a still frame
            X.tw(f'tl.to("{sel} .qc-flag", {{scale:1.07, duration:{pause / 4:.3f}, ease:"sine.inOut", yoyo:true, repeat:3}}, {pause_t + 0.2:.3f});')
            X.tw(f'tl.fromTo("{s} .qc-lab.bad", {{y:0}}, {{y:-6, duration:{pause / 4:.3f}, ease:"sine.inOut", yoyo:true, repeat:3, immediateRender:false}}, {pause_t + 0.27:.3f});')

    # ---- scan bar, rings, ticks per frame, item counters + bars, window readout: one proxy tween
    status_end = []
    for k in range(nc):
        if fail and k == fc:
            status_end.append("修复 1 帧" if fixed else "发现 1 帧")
        else:
            status_end.append(f"通过 {N} 帧")
    js = """(()=>{
  const R = document.querySelector("__S__");
  if (!R) return;
  const SW = __SW__, PS = __PS__, END = __END__;
  const N = __N__, cols = __COLS__, cw = __CW__, ch = __CH__, gap = __GAP__, ox = __OX__, oy = __OY__, t0 = __T0__;
  const fs = [...R.querySelectorAll(".qc-f")];
  const rings = fs.map(e => e.querySelector(".qc-ring"));
  const dots = fs.map(e => [...e.querySelectorAll(".qc-dots i")]);
  const scan = R.querySelector(".qc-scan"), frEl = R.querySelector(".qc-fr");
  const items = [...R.querySelectorAll(".qc-item")];
  const sts = items.map(e => e.querySelector(".qc-st")), bars = items.map(e => e.querySelector(".qc-bar i"));
  function posAt(k, time) {
    const segs = SW[k][2];
    if (time <= segs[0][0]) return 0;
    for (let i = 0; i < segs.length; i++) {
      const s = segs[i];
      if (time <= s[1]) return s[2] + (s[3] - s[2]) * (time - s[0]) / Math.max(1e-4, s[1] - s[0]);
    }
    return N;
  }
  function draw(lt) {
    const time = t0 + lt;
    let k = -1;
    for (let i = 0; i < SW.length; i++) if (time >= SW[i][0] && time < SW[i][1] + 0.06) k = i;
    let pos = -1;
    if (k >= 0) {
      pos = Math.min(N - 0.001, posAt(k, time));
      const row = Math.floor(pos / cols);
      const inRow = pos - row * cols;
      scan.style.left = (ox + inRow * (cw + gap) - (inRow >= cols ? gap : 0)).toFixed(1) + "px";
      scan.style.top = (oy + row * (ch + gap) - 5).toFixed(1) + "px";
    }
    let shown = 0;
    for (let j = 0; j < N; j++) {
      const near = pos >= 0 && Math.abs(pos - (j + 0.5)) < 0.7;
      rings[j].style.opacity = near ? "1" : "0";
      for (let q = 0; q < dots[j].length; q++) dots[j][q].style.opacity = time >= PS[q][j] ? "1" : "0";
    }
    if (k >= 0) shown = Math.min(N, Math.floor(pos + 0.5));
    else if (time >= SW[SW.length - 1][1]) shown = N;
    if (frEl) frEl.textContent = String(shown);
    for (let q = 0; q < items.length; q++) {
      let n = 0;
      for (let j = 0; j < N; j++) if (time >= PS[q][j]) n++;
      let txt = "待检查";
      if (time >= SW[q][1]) txt = END[q];
      else if (time >= SW[q][0]) txt = n + " / " + N;
      sts[q].textContent = txt;
      bars[q].style.transform = "scaleX(" + (n / N).toFixed(3) + ")";
    }
  }
  const V = { t: 0 };
  draw(0);
  tl.fromTo(V, { t: 0 }, { t: __D__, duration: __D__, ease: "none", immediateRender: false, onUpdate: () => draw(V.t) }, __T0__);
})();"""
    js = (js.replace("__S__", s).replace("__SW__", A.js(sweeps)).replace("__PS__", A.js(passed)).replace("__END__", A.js(status_end))
            .replace("__N__", str(N)).replace("__COLS__", str(cols)).replace("__CW__", f"{cw:.2f}").replace("__CH__", f"{ch:.2f}")
            .replace("__GAP__", str(gap)).replace("__OX__", f"{ox - wx0:.2f}").replace("__OY__", f"{oy - wy0 - bar_h:.2f}")
            .replace("__T0__", f"{t:.3f}").replace("__D__", f"{d:.3f}"))
    X.tw(js)
    X.used_text.update("待检查通过修复发现帧 /0123456789")
    A.hold_push(X, f"{s} .w4", sweeps[-1][1] + 0.2, t + d, 1.02, origin=f"{(wx0 + wx1) / 2:.0f}px {(wy0 + wy1) / 2:.0f}px")


# ------------------------------------------------------------------------------------------------ pair_check
REGIONS = [(0.04, 0.70, 0.92, 0.26), (0.28, 0.20, 0.44, 0.46), (0.64, 0.06, 0.33, 0.58), (0.015, 0.02, 0.97, 0.96),
           (0.03, 0.08, 0.30, 0.56)]


def _pair_skeleton(w, h, rich, uid):
    """a generic frame of a finished video, drawn from the style. The plain one: a flat picture block and a thin
    caption. The rich one adds what the default regions point at: a bold caption strip with a highlighted word
    (bottom), a moving shape with trails (centre), a growing bar chart (right third), beat ticks + corner brackets
    (the whole frame). No text, so it never competes with the real labels."""
    out = ""

    def blk(x, y, ww, hh, colr, r=4, cls=""):
        return (f'<i class="pc-sk {cls}" style="left:{x * w:.1f}px; top:{y * h:.1f}px; width:{ww * w:.1f}px; height:{hh * h:.1f}px; '
                f'background:{colr}; border-radius:{r}px"></i>')

    soft = "color-mix(in srgb, var(--card-fg) 22%, transparent)"
    mid = "color-mix(in srgb, var(--card-fg) 45%, transparent)"
    if not rich:
        out += blk(0.22, 0.16, 0.56, 0.5, soft, 6)
        out += blk(0.34, 0.80, 0.32, 0.045, mid, 3)
        return out
    out += f'<i class="pc-sk" style="left:0; top:0; width:{w:.0f}px; height:{h:.0f}px; background:radial-gradient(ellipse at 40% 40%, color-mix(in srgb, var(--accent) 20%, transparent), transparent 70%)"></i>'
    # centre: a disc with motion trails
    for q in range(3):
        out += (f'<i class="pc-sk pc-tr{q} u{uid}" style="left:{(0.38 - q * 0.07) * w:.1f}px; top:{0.28 * h:.1f}px; width:{0.2 * h:.1f}px; height:{0.2 * h:.1f}px; '
                f'border-radius:50%; background:var(--accent); opacity:{0.85 - q * 0.28:.2f}"></i>')
    # right third: a bar chart
    for q in range(4):
        bh = (0.18, 0.3, 0.24, 0.44)[q]
        out += blk(0.70 + q * 0.065, 0.58 - bh, 0.045, bh, "var(--accent)" if q == 3 else mid, 2, f"pc-bar u{uid}")
    out += blk(0.68, 0.585, 0.27, 0.012, mid, 1)
    # bottom: a bold caption strip with a highlighted word
    out += blk(0.14, 0.78, 0.72, 0.11, "color-mix(in srgb, var(--card) 80%, transparent)", 6)
    out += blk(0.19, 0.81, 0.24, 0.05, "var(--card-fg)", 3)
    out += blk(0.45, 0.80, 0.16, 0.07, "var(--accent)", 3)
    out += blk(0.63, 0.81, 0.18, 0.05, "var(--card-fg)", 3)
    # whole frame: beat ticks along the top and corner brackets
    for q in range(12):
        out += blk(0.06 + q * 0.075, 0.035, 0.012, 0.04 if q % 4 else 0.07, mid if q % 4 else "var(--accent)", 1)
    for (x, y, bl, bt) in ((0.025, 0.12, 1, 1), (0.935, 0.12, 0, 1), (0.025, 0.86, 1, 0), (0.935, 0.86, 0, 0)):
        st = "border-left" if bl else "border-right"
        sb = "border-top" if bt else "border-bottom"
        out += (f'<i class="pc-sk" style="left:{x * w:.1f}px; top:{y * h:.1f}px; width:{0.04 * w:.1f}px; height:{0.04 * w:.1f}px; '
                f'{st}:3px solid var(--card-fg); {sb}:3px solid var(--card-fg); opacity:.7"></i>')
    return out


def pair_check(X, cid, t, d, p):
    """前后对照 Pair Check: two panels — before and after — enter together; then for each point a marker circles the
    matching region of the better panel (numbered), the point word lights under the panels with an underline wipe,
    and the other panel dims another 12 %. Regions default to bottom strip, centre, right third, whole frame (then
    left third); `regions` overrides them. Without media, the panels are drawn frames of visibly different richness.
    16:9: side by side, points in one row; 9:16: stacked — the loser on top at 720 px, the winner under it at 900 px —
    points as a grid of chips."""
    F_ = "pair_check"
    pts = _as_list(p.get("points"))
    A.need(F_, t, p, [] if pts else ["points (2–5 words: what is better in the winning panel)"])
    if not pts:
        pts = ["……"]
    if len(pts) > 5:
        _warn(f"{F_}: {len(pts)} points, showing the first 5")
        pts = pts[:5]
    npt = len(pts)
    winner = A.choice(F_, p, "winner", ["left", "right"], "right")
    G = A.frame(X, p)
    P = G["P"]
    col = _cols(X, p)
    sides = {}
    for key, dflt in (("left", "以前"), ("right", "现在")):
        v = p.get(key)
        if isinstance(v, str):
            v = {"label": v}
        if not isinstance(v, dict):
            v = {}
        sides[key] = {"label": str(v.get("label") or dflt), "media": v.get("media") or v.get("image") or v.get("src")}
    loser = "left" if winner == "right" else "right"
    regs = p.get("regions") if isinstance(p.get("regions"), list) else []
    regions = []
    for i in range(npt):
        r = None
        if i < len(regs) and isinstance(regs[i], (list, tuple)) and len(regs[i]) == 4:
            try:
                r = tuple(max(0.0, min(1.0, float(x))) for x in regs[i])
            except (TypeError, ValueError):
                r = None
        regions.append(r or REGIONS[i % len(REGIONS)])

    # ---- geometry: (x, y, w, h) of each panel's picture; 16:9 also a title bar above it
    if P:
        bar = 0
        # the point chips on top; the loser under them, the winner in front of its lower edge, nearly full width,
        # with a floor reflection that runs on to the bottom edge (picture under the caption band)
        cols_ = 2 if npt <= 4 else 3
        rows_ = int(math.ceil(npt / cols_))
        pts_y0 = 300.0
        pts_y1 = pts_y0 + rows_ * 88.0 + (rows_ - 1) * 12.0
        lw, lh = 820.0, 461.0
        ww_, wh_ = 920.0, 518.0                      # x 40–960: what the pictures show stays clear of the 9:16 button zone
        top = pts_y1 + 34.0
        over_ = 72.0                                 # the winner overlaps the loser's lower edge (it sits in front)
        rects = {loser: (90.0, top, lw, lh), winner: (40.0, top + lh - over_, ww_, wh_)}
        if loser == "right":
            rects[loser] = (170.0, top, lw, lh)
    else:
        bar = 58
        pw, ph = 760.0, 428.0
        y0 = 170.0
        rects = {"left": (160.0, y0 + bar, pw, ph), "right": (1000.0, y0 + bar, pw, ph)}
        pts_y0 = y0 + bar + ph + 40
        pts_y1 = 860.0

    def pic_html(key, w, h):
        m = sides[key]["media"]
        if m:
            m = _path(m)
            return f'<img src="{_frame_still(X, m, 1.0)}" alt="">'
        return _pair_skeleton(w, h, key == winner, key[0])

    panels = ""
    tab_w = 420.0
    for key in ((loser, winner) if P else ("left", "right")):
        x, y, w, h = rects[key]
        body = f'<div class="pc-pic" style="width:{w:.0f}px; height:{h:.0f}px">{pic_html(key, w, h)}<div class="pc-dim"></div></div>'
        cls = f"pc-win pc-{key} " + ("pc-w" if key == winner else "pc-l")
        if P:
            lpx, ltxt = _fit_line(sides[key]["label"], min(w * 0.7, 960.0 - x - 120), 34 if key == winner else 32, 30)
            if key == winner:
                from h9 import fit as FT
                tab_w = FT.width(ltxt) * lpx + 130          # dots + padding: where a badge must not sit
            tab = (f'<div class="pc-tab{" win" if key == winner else ""}" style="font-size:{lpx}px"><div class="w4-dots"><i></i><i></i><i></i></div>'
                   f'{_t(X, ltxt)}</div>')
            refl = "; -webkit-box-reflect:below 14px linear-gradient(transparent 58%, rgba(0,0,0,.24))" if key == winner else ""
            panels += (f'<div class="w4-win {cls}" style="left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px{refl}">'
                       f'<div class="w4-body" style="top:0">{body}</div>{tab}</div>')
        else:
            win, _bh = _window(X, x, y - bar, w, h + bar, sides[key]["label"], P, body, right="", cls=cls)
            panels += win

    # markers: one ellipse (dash-drawn) + a numbered badge per point, on the winner's picture
    wx, wy, wW, wH = rects[winner]
    mk = ""
    svg = ""
    npx_ = 30 if P else 28
    for i, (rx, ry, rw, rh) in enumerate(regions):
        cx = wx + (rx + rw / 2) * wW
        cy = wy + (ry + rh / 2) * wH
        ex = rw * wW / 2 + 10
        ey = rh * wH / 2 + 10
        if rw > 0.85 and rh > 0.85:
            # the whole frame: an inset rounded rectangle, not an ellipse that would cover everything else
            ex = rw * wW / 2 - 4
            ey = rh * wH / 2 - 4
            svg += (f'<rect class="e{i}" x="{cx - ex:.1f}" y="{cy - ey:.1f}" width="{ex * 2:.1f}" height="{ey * 2:.1f}" rx="18" '
                    f'pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>')
            bx = cx + ex - npx_ * 1.6 - 14
            by = cy + ey - npx_ * 1.6 - 14
        else:
            svg += f'<ellipse class="e{i}" cx="{cx:.1f}" cy="{cy:.1f}" rx="{ex:.1f}" ry="{ey:.1f}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="1"/>'
            # the badge sits just outside the ellipse's upper-left, off the thing it circles
            bx = cx - ex * 0.71 - npx_ * 1.6 * 0.95
            by = cy - ey * 0.71 - npx_ * 1.6 * 0.95
        bx = max(wx + 6, min(wx + wW - npx_ * 1.6 - 6, bx))
        by = max(wy + 6, min(wy + wH - npx_ * 1.6 - 6, by))
        if P and by < wy + 72 and bx < wx + tab_w:
            bx = wx + tab_w + 8                      # beside the panel's label tab, not on it or on what is under it
        mk += f'<div class="pc-num m{i}" style="left:{bx:.0f}px; top:{by:.0f}px; width:{npx_ * 1.6:.0f}px; height:{npx_ * 1.6:.0f}px; font-size:{npx_}px">{i + 1}</div>'
    mk = f'<svg class="pc-mk" width="{X.W}" height="{X.H}" viewBox="0 0 {X.W} {X.H}">{svg}</svg>' + mk

    # points under the panels
    pts_html = ""
    if P:
        cols = 2 if npt <= 4 else 3
        rows = int(math.ceil(npt / cols))
        gx = 14
        gy = 12
        avail_h = pts_y1 - pts_y0
        ch_h = min(88.0, (avail_h - gy * (rows - 1)) / rows)
        cw = (960 - 90 - gx * (cols - 1)) / cols
        top_px = int(max(34, min(44, ch_h * 0.55)))
        for w_ in pts:
            top_px = min(top_px, _fit_line(w_, cw - 70, top_px, 34)[0])
        for i, w_ in enumerate(pts):
            r_ = i // cols
            c_ = i % cols
            fpx, ftxt = _fit_line(w_, cw - 70, top_px, 30)
            pts_html += (f'<div class="pc-pt chip p{i}" style="left:{90 + c_ * (cw + gx):.0f}px; top:{pts_y0 + r_ * (ch_h + gy):.0f}px; width:{cw:.0f}px; height:{ch_h:.0f}px; font-size:{fpx}px">'
                         f'<span class="w"><span class="n">{i + 1}</span> {_t(X, ftxt)}<i class="u" style="bottom:-6px"></i></span></div>')
    else:
        slot = 1600.0 / npt
        hh = pts_y1 - pts_y0
        top_px = 52
        for w_ in pts:
            top_px = min(top_px, _fit_line(w_, slot - 80, top_px, 34)[0])
        for i, w_ in enumerate(pts):
            fpx, ftxt = _fit_line(w_, slot - 80, top_px, 26)
            pts_html += (f'<div class="pc-pt p{i}" style="left:{160 + i * slot:.0f}px; top:{pts_y0:.0f}px; width:{slot:.0f}px; height:{min(hh, fpx * 1.9):.0f}px; font-size:{fpx}px">'
                         f'<span class="w"><span class="n" style="font-size:{fpx * 0.7:.0f}px">{i + 1}</span> {_t(X, ftxt)}<i class="u" style="bottom:-12px"></i></span></div>')
    inner = panels + mk + pts_html
    _css(X)
    s, k_ = A.stage(X, cid, t, d, p, f'<div class="f2-body w4">{inner}</div>')

    # ---- entrances: 16:9 the panels slide in from their own sides; 9:16 the loser drops in, the winner rises
    if P:
        X.tw(f'tl.fromTo("{s} .pc-l", {{y:-80, opacity:0, rotation:-2}}, {{y:0, opacity:1, rotation:0, duration:0.5, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-w", {{y:120, opacity:0}}, {{y:0, opacity:1, duration:0.55, ease:"expo.out", immediateRender:true}}, {t + 0.1:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-pt", {{y:30, clipPath:"inset(0 0 100% 0)"}}, {{y:0, clipPath:"inset(0 0 0% 0)", duration:0.4, ease:"power3.out", stagger:0.05, immediateRender:true}}, {t + 0.28:.3f});')
    else:
        X.tw(f'tl.fromTo("{s} .pc-left", {{x:-160, opacity:0}}, {{x:0, opacity:1, duration:0.55, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-right", {{x:160, opacity:0}}, {{x:0, opacity:1, duration:0.55, ease:"power4.out", immediateRender:true}}, {t + 0.04:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-pt", {{y:24, opacity:0}}, {{y:0, opacity:1, duration:0.35, ease:"power3.out", stagger:0.05, immediateRender:true}}, {t + 0.3:.3f});')
    # the rich panel keeps moving: bars grow and breathe, the disc travels with its trails
    uid = winner[0]
    X.tw(f'tl.fromTo("{s} .pc-bar.u{uid}", {{scaleY:0.2, transformOrigin:"50% 100%"}}, {{scaleY:1, duration:0.6, ease:"power3.out", stagger:0.06, immediateRender:true}}, {t + 0.35:.3f});')
    X.tw(f'tl.to("{s} .pc-bar.u{uid}", {{keyframes:[{{scaleY:0.8, duration:{max(0.4, d * 0.2):.2f}}}, {{scaleY:1.05, duration:{max(0.4, d * 0.2):.2f}}}, {{scaleY:0.92, duration:{max(0.4, d * 0.2):.2f}}}], ease:"sine.inOut", stagger:0.1}}, {t + 1.0:.3f});')
    for q in range(3):
        X.tw(f'tl.fromTo("{s} .pc-tr{q}.u{uid}", {{x:{-wW * 0.12:.0f}}}, {{x:{wW * 0.14:.0f}, duration:{max(0.8, d - 0.4):.2f}, ease:"sine.inOut", immediateRender:true}}, {t + 0.2 + q * 0.06:.3f});')

    # ---- per point: the marker draws, the badge pops, the word lights with its underline, the other panel dims
    cues = A.cues(X, p, [{"text": x} for x in pts], t, d, start=0.3, end=0.82)
    fg = col.get("fg", "#111111")
    for i in range(npt):
        a = cues[i]
        X.tw(f'tl.fromTo("{s} .pc-mk .e{i}", {{attr:{{"stroke-dashoffset":1}}}}, {{attr:{{"stroke-dashoffset":0}}, duration:0.4, ease:"power2.inOut", immediateRender:true}}, {a:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-num.m{i}", {{scale:0, opacity:0}}, {{scale:1, opacity:1, duration:0.3, ease:"back.out(2.2)", immediateRender:true}}, {a + 0.2:.3f});')
        X.tw(f'tl.to("{s} .pc-pt.p{i}, {s} .pc-pt.p{i} .n", {{color:"{fg}", duration:0.15}}, {a + 0.1:.3f});')
        X.tw(f'tl.fromTo("{s} .pc-pt.p{i} .u", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"power3.out", immediateRender:true}}, {a + 0.12:.3f});')
        X.tw(f'tl.to("{s} .pc-{loser} .pc-dim", {{opacity:{min(0.6, 0.12 * (i + 1)):.2f}, duration:0.3}}, {a + 0.1:.3f});')
        X.tw(f'tl.to("{s} .pc-{loser} .pc-pic", {{filter:"saturate({max(0.2, 1 - 0.2 * (i + 1)):.2f})", duration:0.3}}, {a + 0.1:.3f});')
        if i > 0:
            X.tw(f'tl.to("{s} .pc-mk .e{i - 1}, {s} .pc-num.m{i - 1}", {{opacity:0.35, duration:0.25}}, {a:.3f});')
        X.sfx(a, "pop", 0.35)
    last = cues[-1] + 0.6
    A.hold_push(X, f"{s} .w4", last, t + d, 1.02, origin=f"50% {(wy + wH / 2):.0f}px")


FX = {"doc_edit": doc_edit, "wave_align": wave_align, "qc_sheet": qc_sheet, "pair_check": pair_check}
