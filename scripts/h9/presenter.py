"""Presenter layer: one subject (a talking head, a screen recording, a mascot or a still) that stays on screen for the
whole film and moves between places — full frame, a large card under the graphic, a full-height side column, a corner,
a round bubble, a split half, a picture-in-picture window, hidden — while each beat's graphics lay themselves out in
the space it leaves. The video keeps playing across beats (one untimed wrapper, timed <video> segments inside it,
looped when the source is shorter than the film).

video.json
  meta.presenter = {"src": "assets/host.mp4", "form": "full" | "bubble" | "split" | "pip" | "cutout",
                    "pos": "top-right", "size": 0.45, "zoom": 1.4,
                    "at": "full", "fit": "cover" | "contain", "focus": [50, 35],
                    "loop": true, "start": 0, "audio": false, "tag": "ON AIR", "ground": "#…", "scrim": true}
    (a plain string is the src). .webm / .png / .gif subjects default to fit "contain" (a cut-out on its ground).
    form   the film's framing (主播出镜形式), picked once; every beat without its own "presenter" follows it:
             full    全屏口播 — the speaker fills the frame; beats whose graphic needs room move to card (9:16) / side (16:9)
             bubble  圆形头像 — the speaker in a circle (pos top-right | top-left | bottom-right | bottom-left, size =
                     diameter as a share of the width in 9:16 / of the height in 16:9, zoom = how tight on the face)
             split   上下分屏 — 9:16 speaker in one half (pos bottom | top, size = share of the height), graphics in
                     the other; 16:9 left / right (pos right | left)
             pip     小窗 — a rounded window in a corner (pos as bubble, size = share of the width), graphics own the rest
             cutout  抠像站位 — a cut-out (src with alpha: .webm / .png / .gif / .webp) standing on the bottom
           pos / size / zoom on meta.presenter apply to the form's own place; a beat object can override them.
           Without a form, a beat without "presenter" keeps the place of the beat before (the subject stays).
  beat.presenter = "full" | "card" | "side" | "corner" | "bubble" | "split" | "pip" | "hidden"
                or {"at": "side", "flip": true, "rect": [x, y, w, h], "move": 0.65, "pos": "top-left", "size": 0.4}
    flip   mirror left / right (side / card / corner on the left)
    rect   a custom place, px in the layout frame (1080×1920 or 1920×1080); the graphics get the rest
  beat.presenter_force = true   keep "full" even when the beat's graphic would normally move the speaker aside

Places (9:16; 16:9 in brackets) — the speaker stays large and the graphics get a real page, never a floating thumbnail:
  full    the frame (a cut-out stands on the bottom bar, graphics above its head) [cut-out on the right, graphics left]
  card    a framed card the full content width over the lower 55 % of the frame, graphics the full width of the top
          45 % [a framed full-height card on the right 40 %, graphics left]
  side    a full-height column on the right 40 % of the frame, graphics in the column beside it [right 40 %]
  corner  a small card top-right, graphics under it [top-right, graphics left]
  bubble / split / pip   as the forms above (the bubble brings the face to its middle)
  hidden  nobody on screen, the graphics get the whole frame
With a chapter device (camera / browser / phone chrome) the tall places stop above its bottom bar and side / split
stay inside the content width.
The crop follows presenter.focus (the face's position in the source, %): object-position and the zoom origin sit on
it, so the face stays in every crop.

Text never sits on a real face. With real footage (fit cover), a beat that lands on "full" whose graphic needs its own
area (every fx except the ON_PERSON effects, which are designed to sit beside a subject, and caption-only beats) is
moved to card (9:16) / side (16:9) — or to the film's form place for bubble / split / pip — and one line is printed.
"presenter_force": true keeps it full; the beat then gets a dark scrim on the footage and light text.

How the graphics make room: while a beat is built, the build context's frame (X.W, X.H) is narrowed to the free
region and everything the beat adds is wrapped in an untimed box at that region — effects lay out as usual, just in
a smaller frame. "full" and "hidden" give the graphics the whole frame. The chapter device (device.py) adds the
chapter's colour world (CSS variables) to the same wrapper.

Preview the forms on your own clip (one still per form on one board):
  python3 scripts/h9/presenter.py preview assets/talk.mp4 --focus 50,32 --out work/forms
"""
import json
import re
import subprocess
import sys
from pathlib import Path

if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from h9 import fit, device  # noqa: E402

Z_PRESENTER = 2
PLACES = ("full", "card", "side", "corner", "bubble", "split", "pip", "hidden")
FORMS = {"full": "full", "bubble": "bubble", "split": "split", "pip": "pip", "cutout": "full"}
FORM_NAMES = {"full": "全屏口播", "bubble": "圆形头像", "split": "上下分屏", "pip": "小窗", "cutout": "抠像站位"}
CORNERS = ("top-right", "top-left", "bottom-right", "bottom-left")
ALPHA_EXT = (".webm", ".png", ".gif", ".webp")
# effects built to sit on / beside a subject: they may stay on a full-frame speaker
ON_PERSON = ("lower3", "callout", "key_card", "side_stat", "stack_build", "strike_fix", "chip_cycle", "talking_head", "host_point")
FRAMED = ("card", "side", "corner", "pip", "bubble")
MOVE = 0.65            # seconds a move takes; it straddles the beat boundary
LEAD = 0.3             # how long before the boundary the move starts
GAP = 28               # px between the speaker and the graphics

# per-style skin of the card: corner radius, border, shadow, and the small name tag
SKIN_DEFAULT = {"radius": 28, "border": 0, "border_colour": "fg", "shadow": "0 28px 60px rgba(0,0,0,.32), 0 6px 16px rgba(0,0,0,.18)",
                "tag_bg": "rgba(14,14,16,.7)", "tag_fg": "#ffffff", "tag_radius": "8px"}
SKIN = {
    "minimal":  {"radius": 24, "border": 0, "shadow": "0 24px 50px rgba(43,41,37,.22)"},
    "poster":   {"radius": 0, "border": 6, "shadow": "14px 14px 0 var(--accent)", "tag_bg": "#0a0a0a", "tag_radius": "0px"},
    "flat":     {"radius": 44, "border": 8, "border_colour": "card", "shadow": "0 18px 0 rgba(0,0,0,.18)", "tag_radius": "999px"},
    "ink":      {"radius": 6, "border": 3, "shadow": "0 10px 26px rgba(23,22,18,.25)", "tag_radius": "3px"},
    "screen":   {"radius": 18, "border": 1, "border_colour": "line", "shadow": "0 0 0 1px rgba(255,255,255,.06), 0 30px 80px rgba(0,0,0,.6), 0 0 60px color-mix(in srgb, var(--accent) 22%, transparent)"},
    "pixel":    {"radius": 0, "border": 6, "shadow": "8px 8px 0 rgba(0,0,0,.45)", "tag_radius": "0px"},
    "sketch":   {"radius": 16, "border": 4, "shadow": "7px 7px 0 var(--fg)", "tag_radius": "12px"},
    "zine":     {"radius": 0, "border": 5, "shadow": "11px 11px 0 var(--accent)", "tag_radius": "0px"},
    "papercut": {"radius": 10, "border": 0, "shadow": "0 3px 0 rgba(0,0,0,.18), 0 18px 34px rgba(0,0,0,.28)"},
    "press":    {"radius": 2, "border": 3, "shadow": "0 16px 40px rgba(0,0,0,.2)", "tag_radius": "2px"},
    "doc":      {"radius": 0, "border": 1, "border_colour": "line", "shadow": "0 30px 80px rgba(0,0,0,.6)", "tag_radius": "0px"},
    "hud":      {"radius": 0, "border": 2, "border_colour": "accent", "shadow": "0 0 40px color-mix(in srgb, var(--accent) 25%, transparent)", "tag_radius": "0px"},
    "atlas":    {"radius": 12, "border": 3, "border_colour": "accent", "shadow": "0 24px 60px rgba(0,0,0,.4)"},
}

CSS = """
.pz { position:absolute; overflow:hidden; pointer-events:none; border-style:solid; }
.pzsh { position:absolute; }
.pz .pzm { position:absolute; inset:0; overflow:hidden; border-radius:inherit; }
.pz .pzm video, .pz .pzm img { position:absolute; inset:0; width:100%; height:100%; display:block; }
.pz .pzs { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.38), rgba(0,0,0,0) 22%, rgba(0,0,0,0) 58%, rgba(0,0,0,.5)); opacity:0; }
.pz .pzo { position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,.62) 0%, rgba(0,0,0,.22) 28%, rgba(0,0,0,.16) 46%, rgba(0,0,0,.5) 66%, rgba(0,0,0,.78) 100%); opacity:0; }
.pz .pzt { position:absolute; left:16px; top:16px; display:flex; align-items:center; gap:8px; white-space:nowrap; font:700 20px var(--f-mono, monospace);
  letter-spacing:.08em; color:var(--pz-tag-fg); background:var(--pz-tag-bg); padding:6px 12px 6px 10px; border-radius:var(--pz-tag-r); opacity:0; }
.pz .pzt i { width:10px; height:10px; border-radius:50%; background:#ff453a; display:block; }
"""

# light text on a full-frame speaker when a graphic was forced over the footage
LIGHT_VARS = "--fg:#ffffff; --card-fg:#ffffff; --muted:rgba(255,255,255,.84); text-shadow:0 2px 16px rgba(0,0,0,.55);"


def skin_for(style):
    s = dict(SKIN_DEFAULT)
    chain = list(style.get("_chain") or [])
    chain.reverse()
    for sid in chain:
        if sid in SKIN:
            s.update(SKIN[sid])
    s.update(style.get("presenter_skin") or {})
    return s


def spec_of(meta):
    p = meta.get("presenter")
    if not p:
        return None
    if isinstance(p, str):
        return {"src": p}
    return dict(p)


def default_fit(src):
    low = str(src).lower()
    for ext in (".webm", ".png", ".gif", ".webp"):
        if low.endswith(ext):
            return "contain"
    return "cover"


def has_alpha(src):
    low = str(src).lower()
    for ext in ALPHA_EXT:
        if low.endswith(ext):
            return True
    return False


def place_of(beat, current):
    """(place, options) of one beat; a beat without "presenter" takes `current`."""
    p = beat.get("presenter")
    if p is None:
        return current, {}
    if isinstance(p, str):
        return p, {}
    return p.get("at", current), p


def needs_area(beat):
    """True when the beat's graphic needs its own page (it must not be drawn over a speaker's face)."""
    scene = beat.get("scene", "fx")
    if scene != "fx":
        return True
    name = beat.get("fx")
    if not name:
        return False
    return name not in ON_PERSON


def effective_places(video, portrait=True):
    """where the speaker really ends up on each beat, the same way the build decides it (form defaults + the
    auto-switch off a full-frame face); None per beat when the film has no presenter. Lint and review use this so
    their checks agree with the render. Returns a list of (place, forced) — forced = a graphic kept on full footage."""
    meta = video.get("meta") or {}
    beats = video.get("beats") or []
    spec = meta.get("presenter")
    out = []
    if not spec:
        for _ in beats:
            out.append((None, False))
        return out
    if isinstance(spec, str):
        spec = {"src": spec}
    src = spec.get("src", "")
    form = spec.get("form")
    form_place = FORMS.get(form) if form else None
    fit_mode = spec.get("fit") or default_fit(src)
    if form == "cutout":
        fit_mode = "contain"
    contain = fit_mode == "contain"
    current = "full"
    if form_place:
        current = form_place
    if spec.get("at"):
        current = spec["at"]
    start_place = current
    for b in beats:
        if form:
            place, opts = place_of(b, start_place)
        else:
            place, opts = place_of(b, current)
        current = place
        if portrait and place == "side" and not opts.get("rect"):
            place = "card"
        forced = False
        if not contain and place == "full" and not opts.get("rect") and needs_area(b):
            if b.get("presenter_force"):
                forced = True
            elif form_place in ("bubble", "split", "pip"):
                place = form_place
            elif portrait:
                place = "card"
            else:
                place = "side"
        out.append((place, forced))
    return out


# ------------------------------------------------------------------ geometry
def rects(X, place, box, opts, contain=False, kind="none"):
    """(presenter rect, graphics region) for a place; rects are (x, y, w, h) in layout px, region None = whole frame.
    kind = the chapter device: with device chrome (camera / browser / phone) the speaker stops above its bottom bar
    and stays inside the content width instead of running edge to edge."""
    W = X.W
    H = X.H
    L, T, R, B = box
    cw = R - L
    ch = B - T
    chrome = kind != "none"
    bottom = H - round(H * 0.05)          # where a tall speaker ends (9:16)
    if chrome:
        bottom = round(H * 0.8)           # just above the device's bottom bar
    if opts.get("rect"):
        x, y, w, h = opts["rect"]
        pres = (x, y, w, h)
        region = free_region(box, pres, X.portrait)
        return pres, region
    if place == "hidden":
        return (0, 0, W, H), None             # nobody on screen: the graphics get the whole frame
    if place == "full":
        if not contain:
            return (0, 0, W, H), None
        # a cut-out (mascot) owns the frame standing on the bottom chrome; the graphics go above its head (9:16)
        if X.portrait:
            w = round(W * 0.7)
            h = round(w * 0.98)
            y = round(H * 0.806) - h          # stands just above the device's bottom bar
            pres = ((W - w) / 2, y, w, h)
            # the text gets a real block above the head (its centre stays clear of the ears; the box may overlap them)
            rh = max(round(cw * 0.7), y - T + 120)
            return pres, (L, T, cw, rh)
        h = round(H * 0.9)
        w = round(h * 1.04)
        x = round(W * 0.7 - w / 2)
        return (x, H - h, w, h), (L, T, x - L, ch)
    if place == "bubble":
        return bubble_rects(X, box, opts)
    if place == "split":
        return split_rects(X, box, opts, chrome, bottom)
    if place == "pip":
        return pip_rects(X, box, opts)
    if X.portrait:
        if place == "card":
            # the graphics own the full width of the top 45 %, the speaker a large card over the lower 55 %
            split_y = round(H * 0.45)
            region = (L, T, cw, split_y - GAP - T)
            x = L
            y = split_y
            w = cw
            h = bottom - y
        elif place == "side":
            # the speaker a full-height column on the right, the graphics a tall page beside it
            w = round(W * 0.4)
            h = H
            x = W - w
            y = 0
            if chrome:
                x = R - w
                y = T
                h = bottom - T
            if contain:
                # a cut-out stands at the bottom of a shorter card instead of an empty column
                h = round(w * 1.3)
                y = bottom - h
            region = (L, T, x - GAP - L, ch)
        else:   # corner
            w = round(cw * 0.27)
            h = round(w * 1.14)
            x = R - w
            y = T
            region = (L, y + h + GAP, cw, ch - h - GAP)
    else:
        if place == "card":
            w = round(cw * 0.4)
            h = ch
            x = R - w
            y = T
            region = (L, T, x - 40 - L, ch)
        elif place == "side":
            w = round(W * 0.4)
            h = H
            x = W - w
            y = 0
            if chrome:
                x = R - w
                y = T
                h = ch
            region = (L, T, x - 40 - L, ch)
        else:   # corner
            w = round(cw * 0.2)
            h = round(w * 0.8)
            x = R - w
            y = T
            region = (L, T, cw - w - 36, ch)
    pres = (x, y, w, h)
    if opts.get("flip"):
        pres = (W - x - w, y, w, h)
        rx, ry, rw, rh = region
        region = (W - rx - rw, ry, rw, rh)
    return pres, region


def corner_of(opts, default="top-right"):
    pos = opts.get("pos") or default
    if pos not in CORNERS:
        raise SystemExit(f"presenter pos {pos!r}; have: {', '.join(CORNERS)}")
    top = pos.startswith("top")
    right = pos.endswith("right")
    return top, right


def window_rects(X, box, d_w, d_h, opts):
    """a speaker window of d_w × d_h in one corner of the content box, the graphics in the biggest page left over."""
    L, T, R, B = box
    cw = R - L
    top, right = corner_of(opts)
    if right:
        x = R - d_w
    else:
        x = L
    if top:
        y = T
    else:
        y = B - d_h
    if X.portrait:
        if top:
            ry = y + d_h + GAP
            region = (L, ry, cw, B - ry)
        else:
            region = (L, T, cw, y - GAP - T)
    else:
        if right:
            region = (L, T, x - GAP - L, B - T)
        else:
            rx = x + d_w + GAP
            region = (rx, T, R - rx, B - T)
    return (x, y, d_w, d_h), region


def bubble_rects(X, box, opts):
    if X.portrait:
        d = round(X.W * float(opts.get("size", 0.45)))
    else:
        d = round(X.H * float(opts.get("size", 0.5)))
    return window_rects(X, box, d, d, opts)


def pip_rects(X, box, opts):
    if X.portrait:
        w = round(X.W * float(opts.get("size", 0.34)))
    else:
        w = round(X.W * float(opts.get("size", 0.22)))
    h = round(w * 1.25)
    return window_rects(X, box, w, h, opts)


def split_rects(X, box, opts, chrome=False, bottom=None):
    """the speaker edge to edge in one half, the graphics in the other (inside the device frame when there is one)."""
    W = X.W
    H = X.H
    L, T, R, B = box
    cw = R - L
    share = float(opts.get("size", 0.5))
    if X.portrait:
        pos = opts.get("pos") or "bottom"
        ph = round(H * share)
        if pos == "bottom":
            y = H - ph
            pres = (0, y, W, ph)
            if chrome:
                pres = (L, y, cw, bottom - y)
            region = (L, T, cw, y - GAP - T)
        elif pos == "top":
            pres = (0, 0, W, ph)
            ry = max(ph + GAP, T)
            region = (L, ry, cw, max(200, B - ry))
        else:
            raise SystemExit(f"split pos {pos!r} in 9:16; have: bottom, top")
        return pres, region
    pos = opts.get("pos") or "right"
    pw = round(W * share)
    if pos == "right":
        pres = (W - pw, 0, pw, H)
        region = (L, T, W - pw - GAP - L, B - T)
    elif pos == "left":
        pres = (0, 0, pw, H)
        rx = pw + GAP
        region = (rx, T, R - rx, B - T)
    else:
        raise SystemExit(f"split pos {pos!r} in 16:9; have: right, left")
    return pres, region


def free_region(box, pres, portrait):
    """the biggest box-aligned rectangle beside a custom presenter rect."""
    L, T, R, B = box
    x, y, w, h = pres
    candidates = []
    candidates.append((L, T, x - L - 32, B - T))                 # left of it
    candidates.append((x + w + 32, T, R - x - w - 32, B - T))    # right of it
    candidates.append((L, T, R - L, y - T - 32))                 # above
    candidates.append((L, y + h + 32, R - L, B - y - h - 32))    # below
    best = None
    best_area = 0
    for c in candidates:
        if c[2] < 200 or c[3] < 200:
            continue
        area = c[2] * c[3]
        if area > best_area:
            best = c
            best_area = area
    return best


def centred_position(focus, src_ar, box_w, box_h):
    """object-position (%) that brings the focus point to the middle of a cover-cropped box as far as the crop allows,
    and where the focus then sits in the box (%) — the zoom grows around that point."""
    fx = focus[0] / 100.0
    fy = focus[1] / 100.0
    box_ar = box_w / max(box_h, 1)
    px = focus[0]
    py = focus[1]
    face_x = focus[0]
    face_y = focus[1]
    if src_ar < box_ar:
        # taller than the box: the picture spans the width, the crop slides vertically
        img_h = box_w / src_ar
        over = img_h - box_h
        if over > 0:
            off = fy * img_h - box_h / 2
            off = max(0.0, min(over, off))
            py = off / over * 100
            face_y = (fy * img_h - off) / box_h * 100
    else:
        img_w = box_h * src_ar
        over = img_w - box_w
        if over > 0:
            off = fx * img_w - box_w / 2
            off = max(0.0, min(over, off))
            px = off / over * 100
            face_x = (fx * img_w - off) / box_w * 100
    return (round(px, 1), round(py, 1)), (round(face_x, 1), round(face_y, 1))


def bleeds(rect, W, H):
    """True when the rect runs edge to edge across the frame (no border or rounded corners then)."""
    x, y, w, h = rect
    across = x <= 0 and x + w >= W - 1
    down = y <= 0 and y + h >= H - 1
    return across or down


# ------------------------------------------------------------------ the plan
class Layers:
    """per-beat places, regions and chapter worlds; begin()/end() wrap each beat, build() adds the layers."""

    def __init__(self, X, video, beats, times, D, style):
        meta = video.get("meta") or {}
        self.spec = spec_of(meta)
        self.chs = device.chapters(video, beats, times, style)
        self.style = style
        self.times = times
        self.D = D
        self.places = []
        self.opts = []
        self.pres = []
        self.regions = []
        self.overlay = []      # scrim strength on full-frame footage under a graphic (0 = none)
        self.light = []        # light text vars on this beat's graphics (a graphic forced over footage)
        self.form = None
        self.contain = False
        kind = "none"
        if self.chs:
            kind = self.chs["spec"]["kind"]
        if self.spec:
            src = self.spec.get("src", "")
            form = self.spec.get("form")
            if form is not None and form not in FORMS:
                raise SystemExit(f"meta.presenter.form {form!r}; have: {', '.join(FORMS)}")
            if form == "cutout":
                if not has_alpha(src):
                    raise SystemExit(f"presenter form 'cutout' needs a source with alpha ({', '.join(ALPHA_EXT)}); {src!r} is not — use 'full', 'bubble', 'split' or 'pip'")
                self.spec["fit"] = "contain"
            self.form = form
            fit_mode = self.spec.get("fit") or default_fit(src)
            self.contain = fit_mode == "contain"
        form_place = None
        if self.form:
            form_place = FORMS[self.form]
        current = "full"
        if form_place:
            current = form_place
        if self.spec and self.spec.get("at"):
            current = self.spec["at"]
        start_place = current
        has_captions = bool(X.chars) and style.get("captions") is not False
        for i, b in enumerate(beats):
            if self.form:
                place, opts = place_of(b, start_place)     # with a form, a beat without a value follows the form
            else:
                place, opts = place_of(b, current)         # without one, the subject stays where it was
            if place not in PLACES:
                raise SystemExit(f"beat {i}: presenter place {place!r}; have: {', '.join(PLACES)}")
            current = place
            if X.portrait and place == "side" and not (isinstance(opts, dict) and opts.get("rect")):
                # 9:16 is too narrow for a side column: the graphics end up unreadably small, so stack instead
                print(f"presenter: beat {i} side → card: in 9:16 a side column leaves the graphics too little width")
                place = "card"
            opts = self.merged_opts(place, form_place, opts)
            overlay = 0.0
            light = False
            if self.spec and not self.contain and place == "full" and not opts.get("rect"):
                if needs_area(b):
                    if b.get("presenter_force"):
                        overlay = 1.0
                        light = True
                    else:
                        new_place = self.fallback(X, form_place)
                        what = b.get("fx") or b.get("scene", "fx")
                        print(f"presenter: beat {i} ({what}) full → {new_place}: its graphic needs its own area, so it never sits on the face "
                              f'(set "presenter_force": true on the beat to keep full)')
                        place = new_place
                        opts = self.merged_opts(place, form_place, {})
                elif b.get("fx"):
                    overlay = 0.6
            beat_kind = kind
            if self.chs:
                beat_kind = self.chs["list"][self.chs["of_beat"][i]]["device"]
            box = device.content_box(X, beat_kind, has_captions)
            if not self.spec:
                pres = (0, 0, X.W, X.H)
                region = None
                place = "none"
            else:
                pres, region = rects(X, place, box, opts, self.contain, beat_kind)
            self.places.append(place)
            self.opts.append(opts)
            self.pres.append(pres)
            self.regions.append(region)
            self.overlay.append(overlay)
            self.light.append(light)
        self._saved = None
        self._n0 = 0
        self.frame_w = X.W
        self.frame_h = X.H

    def merged_opts(self, place, form_place, opts):
        """the form's pos / size / zoom (meta.presenter) for the form's own place, under the beat's own options."""
        out = {}
        if self.spec and place == form_place and place != "full":
            for key in ("pos", "size", "zoom"):
                if self.spec.get(key) is not None:
                    out[key] = self.spec[key]
        for key in opts:
            out[key] = opts[key]
        return out

    def fallback(self, X, form_place):
        """where a speaker goes when a beat's graphic needs room."""
        if form_place in ("bubble", "split", "pip"):
            return form_place
        if X.portrait:
            return "card"
        return "side"

    def active(self):
        return bool(self.spec or self.chs)

    # --- around each beat's build
    def begin(self, X, i):
        self._saved = (X.W, X.H, X.portrait)
        self._n0 = len(X.els)
        region = self.regions[i]
        if region:
            X.W = int(round(region[2]))
            X.H = int(round(region[3]))
            X.portrait = X.H > X.W

    def end(self, X, i):
        W, H, portrait = self._saved
        X.W = W
        X.H = H
        X.portrait = portrait
        region = self.regions[i]
        if region:
            x, y, w, h = region
            box = f"left:{x:.0f}px; top:{y:.0f}px; width:{w:.0f}px; height:{h:.0f}px; overflow:hidden;"
            orient = "v" if h > w else "h"
        else:
            box = f"left:0; top:0; width:{W}px; height:{H}px;"
            orient = "v" if portrait else "h"
        vars_css = ""
        if self.chs:
            ch = self.chs["list"][self.chs["of_beat"][i]]
            vars_css = device.world_vars(ch["world"]) + ";"
        if self.light[i]:
            vars_css = vars_css + " " + LIGHT_VARS
        place = self.places[i]
        X.els.insert(self._n0, f'<div class="pz-reg pz-at-{place} {orient}" data-beat="{i}" style="position:absolute; z-index:3; container-type:size; {box} {vars_css}">')
        X.els.append("</div>")

    def owns_transition(self, beat):
        return device.owns_transition(self.chs, beat)

    # --- the layers
    def build(self, X):
        self.caption_plates(X)
        if self.chs:
            device.build(X, self.chs, self.D, self.style)
        if self.spec:
            self.build_presenter(X)

    def caption_plates(self, X):
        """reading captions sit on a plate in the beat's ground colour, so they read over the subject, a chart or a
        light chapter alike (captions are always above the presenter: z 50 vs 2). Stroked punch captions read on
        anything and keep their look."""
        if not X.chars or self.style.get("captions") is False:
            return
        if device.caption_mode(X) != "reading":
            return
        if X.v.get("meta", {}).get("caption_style"):
            return            # the film fixed its own subtitle look
        last = None
        for i in range(len(self.places)):
            w = self.world_at(i)
            key = (w["bg"], w["fg"])
            if key == last:
                continue
            last = key
            t = max(0.0, self.times[i][0] - 0.05)
            plate = w["bg"] + "eb"            # 92 % of the ground
            props = []
            props.append(f'"--cap-fg":"{w["fg"]}"')
            props.append(f'"--cap-bg":"{plate}"')
            props.append('"--cap-shadow":"none"')
            props.append('"--cap-pad":"6px 20px 9px"')
            props.append('"--cap-radius":"10px"')
            props.append(f'"--cap-em":"{w["accent"]}"')
            X.tw(f'tl.set("#root", {{{", ".join(props)}}}, {t:.3f});')

    def world_at(self, i):
        if not self.chs:
            tok = self.style["tokens"]
            return device.world(tok.get("bg", "#111111"), tok)
        return self.chs["list"][self.chs["of_beat"][i]]["world"]

    def framed(self, i):
        place = self.places[i]
        if place not in FRAMED:
            return False
        return not bleeds(self.pres[i], self.frame_w, self.frame_h)

    def look(self, i, skin):
        """the CSS values of the presenter on beat i (all tweenable)."""
        place = self.places[i]
        x, y, w, h = self.pres[i]
        w_ = self.world_at(i)
        framed = self.framed(i)
        bw = skin["border"] if framed else 0
        radius = skin["radius"] if framed else 0
        colour_key = skin["border_colour"]
        border_colour = w_.get(colour_key, w_["fg"])
        if place == "bubble":
            radius = round(w / 2)                 # a circle with a thin ring in the chapter's accent
            bw = 6
            border_colour = w_["accent"]
        ground = self.spec.get("ground")
        if not ground:
            if framed:
                ground = w_["card"]
            else:
                ground = device.mix(w_["bg"], "#000000", 1.0)        # the chapter ground itself, as hex (tweenable)
        if place == "full" and w >= self.frame_w - 1:
            # a full-frame subject: no border inside the frame
            x = -bw
            y = -bw
        zoom = 1.0
        if not self.contain:
            if place == "bubble":
                zoom = 1.4                        # tighter on the face
            zoom = float(self.opts[i].get("zoom", zoom))
        out = {"x": round(x, 1), "y": round(y, 1), "width": round(w, 1), "height": round(h, 1),
               "borderRadius": radius, "borderWidth": bw, "borderColor": border_colour, "backgroundColor": ground}
        out["opacity"] = 0 if place == "hidden" else 1
        out["shadow"] = 1 if framed else 0
        out["zoom"] = round(zoom, 3)
        # where the crop sits: on the focus; a bubble brings the face to its middle
        objpos = (self.focus[0], self.focus[1])
        origin = (self.focus[0], self.focus[1])
        if place == "bubble" and not self.contain:
            objpos, origin = centred_position(self.focus, self.src_ar, w, h)
        out["objpos"] = f"{objpos[0]}% {objpos[1]}%"
        out["origin"] = f"{origin[0]}% {origin[1]}%"
        return out

    def build_presenter(self, X):
        sp = self.spec
        src = sp.get("src")
        if not src:
            raise SystemExit("meta.presenter needs src")
        skin = skin_for(self.style)
        X.css("pz-base", CSS)
        X.css("pz-vars", f"#root {{ --pz-tag-bg:{skin['tag_bg']}; --pz-tag-fg:{skin['tag_fg']}; --pz-tag-r:{skin['tag_radius']}; }}")
        D = self.D
        fit_mode = sp.get("fit") or default_fit(src)
        focus = sp.get("focus") or ([50, 100] if fit_mode == "contain" else [50, 35])
        self.focus = (float(focus[0]), float(focus[1]))
        self.src_ar = fit.aspect(X, src, 9 / 16)
        first = self.look(0, skin)
        pos = first["objpos"]
        media = ""
        if fit.is_video(src):
            url = X.asset(src, "video")
            src_d = fit.duration(fit._abs(X, src)) or D
            start = float(sp.get("start", 0))
            loop = sp.get("loop", True)
            seg_len = max(0.5, src_d - start)
            t = 0.0
            k = 0
            vol = "1" if sp.get("audio") else "0"
            muted = "" if sp.get("audio") else " muted"
            while t < D - 0.01:
                d = min(seg_len, D - t)
                if not loop and k > 0:
                    break
                media += (f'<video id="pzv{k}" class="clip" src="{url}"{muted} playsinline data-start="{t:.3f}" data-duration="{d:.3f}" '
                          f'data-media-start="{start:.3f}" data-track-index="{80 + k % 2}" data-volume="{vol}" '
                          f'style="object-fit:{fit_mode}; object-position:{pos}"></video>')
                t += d
                k += 1
        else:
            url = X.asset(src)
            media = f'<img class="pzi" src="{url}" alt="" style="object-fit:{fit_mode}; object-position:{pos}">'
        tag = sp.get("tag", "")
        tag_html = ""
        if tag:
            X.used_text.update(str(tag))
            tag_html = f'<div class="pzt"><i></i>{X.rich(tag)}</div>'
        sty = (f"left:0; top:0; width:{first['width']}px; height:{first['height']}px; "
               f"border-radius:{first['borderRadius']}px; border-width:{first['borderWidth']}px; border-color:{first['borderColor']}; "
               f"background-color:{first['backgroundColor']}; z-index:{Z_PRESENTER}; opacity:{first['opacity']};")
        # the shadow is a sibling (the subject clips its own overflow), shown only when the subject is framed
        sh_sty = (f"left:0; top:0; width:{first['width']}px; height:{first['height']}px; border-radius:{first['borderRadius']}px; "
                  f"box-shadow:{skin['shadow']}; z-index:{Z_PRESENTER - 1}; opacity:{first['shadow']};")
        # the zoom grows around the focus point: object-position maps the source's focus to the same % of the box
        pzm_sty = f"transform-origin:{first['origin']}; transform:scale({first['zoom']});"
        X.els.append(f'<div id="pzsh" class="pzsh" style="position:absolute; pointer-events:none; {sh_sty}"></div>')
        X.tw(f'tl.set("#pzsh", {{x:{first["x"]}, y:{first["y"]}}}, 0);')
        X.els.append(f'<div id="pz" class="pz" style="{sty}"><div class="pzm" style="{pzm_sty}">{media}</div><div class="pzs"></div><div class="pzo"></div>{tag_html}</div>')
        X.tw(f'tl.set("#pz", {{x:{first["x"]}, y:{first["y"]}}}, 0);')
        # still subjects breathe slowly so a held card never freezes
        if not fit.is_video(src):
            X.tw(f'tl.fromTo("#pz .pzi", {{scale:1.0}}, {{scale:1.08, duration:{D:.2f}, ease:"none"}}, 0);')
        self.set_extras(X, 0, 0.0, instant=True)
        for i in range(1, len(self.places)):
            a = self.look(i - 1, skin)
            b = self.look(i, skin)
            t = self.times[i][0]
            mv = float(self.opts[i].get("move", MOVE))
            t0 = max(0.0, t - LEAD)
            if a == b:
                self.set_extras(X, i, t0)
                continue
            props = []
            for key in ("x", "y", "width", "height", "borderRadius", "borderWidth"):
                props.append(f"{key}:{b[key]}")
            props.append(f'borderColor:"{b["borderColor"]}"')
            props.append(f'backgroundColor:"{b["backgroundColor"]}"')
            props.append(f"opacity:{b['opacity']}")
            X.tw(f'tl.to("#pz", {{{", ".join(props)}, duration:{mv:.2f}, ease:"power3.inOut"}}, {t0:.3f});')
            sh_props = []
            for key in ("x", "y", "width", "height", "borderRadius"):
                sh_props.append(f"{key}:{b[key]}")
            sh_props.append(f"opacity:{b['shadow']}")
            X.tw(f'tl.to("#pzsh", {{{", ".join(sh_props)}, duration:{mv:.2f}, ease:"power3.inOut"}}, {t0:.3f});')
            if a["zoom"] != b["zoom"] or a["origin"] != b["origin"]:
                X.tw(f'tl.to("#pz .pzm", {{scale:{b["zoom"]}, transformOrigin:"{b["origin"]}", duration:{mv:.2f}, ease:"power3.inOut"}}, {t0:.3f});')
            if a["objpos"] != b["objpos"]:
                X.tw(f'tl.to("#pz .pzm video, #pz .pzm img", {{objectPosition:"{b["objpos"]}", duration:{mv:.2f}, ease:"power3.inOut"}}, {t0:.3f});')
            self.set_extras(X, i, t0)
            if self.places[i] != self.places[i - 1]:
                X.sfx(t0 + 0.05, "whoosh_soft", 0.35)

    def set_extras(self, X, i, t, instant=False):
        """the caption scrim (full frame only), the overlay scrim (full-frame footage under a graphic) and the name
        tag (framed places except the round bubble)."""
        place = self.places[i]
        wants_scrim = self.spec.get("scrim")
        if wants_scrim is None:
            wants_scrim = not self.contain     # a cut-out stands on its ground: no scrim
        scrim = 0
        overlay = 0
        if place == "full" and wants_scrim:
            scrim = 1
            overlay = self.overlay[i]
        tag = 0
        if self.framed(i) and place != "bubble":
            tag = 1
        dur = 0.01 if instant else 0.4
        X.tw(f'tl.to("#pz .pzs", {{opacity:{scrim}, duration:{dur}}}, {t:.3f});')
        X.tw(f'tl.to("#pz .pzo", {{opacity:{overlay}, duration:{dur}}}, {t:.3f});')
        if self.spec.get("tag"):
            X.tw(f'tl.to("#pz .pzt", {{opacity:{tag}, duration:{dur}}}, {t + (0 if instant else 0.3):.3f});')


# ------------------------------------------------------------------ CSS inside regions
PSEUDO_END = re.compile(r"(::?(?:before|after|placeholder|marker|selection|first-line|first-letter))$")
RULE_HEAD = re.compile(r"([^{}]+)\{")
VIEW_UNIT = re.compile(r"(?<=[\d.])(vmin|vmax|vw|vh)\b")
CQ = {"vmin": "cqmin", "vmax": "cqmax", "vw": "cqw", "vh": "cqh"}


def scope_selector(sel):
    """'#root.v X' -> ':is(#root.v, .pz-reg.v) X:not(.pz-reg.h *)': a portrait rule follows the region's own shape."""
    s = sel.strip()
    if "#root.v" in s:
        mine = "v"
        other = "h"
    elif "#root.h" in s:
        mine = "h"
        other = "v"
    else:
        return sel
    s = s.replace(f"#root.{mine}", f":is(#root.{mine}, .pz-reg.{mine})")
    guard = f":not(.pz-reg.{other} *)"
    m = PSEUDO_END.search(s)
    if m:
        s = s[:m.start()] + guard + m.group(1)
    else:
        s = s + guard
    return s


def scope_head(m):
    head = m.group(1)
    if head.strip().startswith("@") or "#root." not in head:
        return m.group(0)
    parts = head.split(",")
    out = []
    for part in parts:
        out.append(scope_selector(part))
    return ", ".join(out) + " {"


def unit_swap(m):
    return CQ[m.group(1)]


def scope_css(css):
    """the page CSS when regions exist: aspect rules follow each region's shape, viewport units become the region's
    container units (outside any region they fall back to the viewport, so nothing else changes)."""
    css = RULE_HEAD.sub(scope_head, css)
    return VIEW_UNIT.sub(unit_swap, css)


def scope_units(html):
    return VIEW_UNIT.sub(unit_swap, html)


def plan(X, video, beats, times, D, style):
    """the Layers plan, or None when the film has no presenter, no device and no chapter objects."""
    ly = Layers(X, video, beats, times, D, style)
    if not ly.active():
        return None
    return ly


# ------------------------------------------------------------------ form preview
PREVIEW_BEAT = 3.0      # seconds per form in the preview film


def preview_video(src, focus=None, fit_mode=None):
    """a tiny video.json that shows the same headline once per form (cutout only for a source with alpha)."""
    src_path = Path(src).resolve()
    names = ["full", "bubble", "split", "pip"]
    if has_alpha(src_path):
        names.append("cutout")
    presenter_spec = {"src": str(src_path), "loop": True, "audio": False}
    if focus:
        presenter_spec["focus"] = list(focus)
    if fit_mode:
        presenter_spec["fit"] = fit_mode
    beats = []
    t = 0.0
    for name in names:
        label = FORM_NAMES[name]
        beat = {"scene": "fx", "t": t, "d": PREVIEW_BEAT}
        if name == "full":
            beat["fx"] = "lower3"
            beat["text"] = f"{label} · full"
            beat["sub"] = "主播铺满全屏，字条在下方"
            beat["presenter"] = "full"
        elif name == "cutout":
            beat["fx"] = "mask_up"
            beat["text"] = f"*{label}* cutout"
            beat["sub"] = "抠像站在底部，字在头顶"
            beat["presenter"] = "full"
        else:
            beat["fx"] = "mask_up"
            beat["text"] = f"*{label}* {name}"
            beat["sub"] = "图形占剩下的版面"
            beat["presenter"] = FORMS[name]
        beats.append(beat)
        t = t + PREVIEW_BEAT
    meta = {"title": "主播出镜形式", "duration": t, "presenter": presenter_spec}
    return {"meta": meta, "beats": beats}


def preview(src, out, aspect="9:16", style="press", focus=None, fit_mode=None):
    """render one still per form from the user's own presenter clip onto one board; returns the board paths."""
    out_dir = Path(out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    video = preview_video(src, focus, fit_mode)
    vpath = out_dir / "video.json"
    vpath.write_text(json.dumps(video, ensure_ascii=False, indent=1))
    stills = Path(__file__).resolve().parents[1] / "stills.py"
    cmd = [sys.executable, str(stills), str(vpath), "--style", style, "--aspect", aspect, "--out", str(out_dir / "stills")]
    subprocess.run(cmd, check=True)
    boards = sorted((out_dir / "stills").glob("board_*.jpg"))
    for b in boards:
        print(f"forms board: {b}")
    return boards


def main():
    import argparse
    ap = argparse.ArgumentParser(description="presenter forms preview: one still per form from your own clip")
    ap.add_argument("cmd", choices=["preview"])
    ap.add_argument("src", help="the presenter clip or image")
    ap.add_argument("--out", default="work/forms")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--style", default="press")
    ap.add_argument("--focus", help="the face's position in the source, x,y in %, e.g. 50,32")
    ap.add_argument("--fit", choices=["cover", "contain"])
    a = ap.parse_args()
    focus = None
    if a.focus:
        parts = a.focus.split(",")
        focus = [float(parts[0]), float(parts[1])]
    preview(a.src, a.out, a.aspect, a.style, focus, a.fit)


if __name__ == "__main__":
    main()
