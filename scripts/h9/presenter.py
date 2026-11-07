"""Presenter layer: one subject (a talking head, a screen recording, a mascot or a still) that stays on screen for the
whole film and moves between places — full frame, a small card under the graphic, the side, a corner, hidden — while
each beat's graphics lay themselves out in the space it leaves. The video keeps playing across beats (one untimed
wrapper, timed <video> segments inside it, looped when the source is shorter than the film).

video.json
  meta.presenter = {"src": "assets/host.mp4", "at": "full", "fit": "cover" | "contain", "focus": [50, 35],
                    "loop": true, "start": 0, "audio": false, "tag": "ON AIR · 第九顶帽子", "ground": "#…"}
    (a plain string is the src). .webm / .png / .gif subjects default to fit "contain" (a cut-out on its ground).
  beat.presenter = "full" | "card" | "side" | "corner" | "hidden"
                or {"at": "side", "flip": true, "rect": [x, y, w, h], "move": 0.65}
    flip   mirror left / right (side on the left, corner top-left)
    rect   a custom place, px in the layout frame (1080×1920 or 1920×1080); the graphics get the rest
    A beat without "presenter" keeps the place of the beat before (the subject stays).

How the graphics make room: while a beat is built, the build context's frame (X.W, X.H) is narrowed to the free
region and everything the beat adds is wrapped in an untimed box at that region — effects lay out as usual, just in
a smaller frame. "full" and "hidden" give the graphics the whole frame. The chapter device (device.py) adds the
chapter's colour world (CSS variables) to the same wrapper.
"""
import re

from h9 import fit, device

Z_PRESENTER = 2
PLACES = ("full", "card", "side", "corner", "hidden")
MOVE = 0.65            # seconds a move takes; it straddles the beat boundary
LEAD = 0.3             # how long before the boundary the move starts

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
.pz .pzt { position:absolute; left:16px; top:16px; display:flex; align-items:center; gap:8px; white-space:nowrap; font:700 20px var(--f-mono, monospace);
  letter-spacing:.08em; color:var(--pz-tag-fg); background:var(--pz-tag-bg); padding:6px 12px 6px 10px; border-radius:var(--pz-tag-r); opacity:0; }
.pz .pzt i { width:10px; height:10px; border-radius:50%; background:#ff453a; display:block; }
"""


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


def place_of(beat, current):
    """(place, options) of one beat; a beat without "presenter" keeps the current place."""
    p = beat.get("presenter")
    if p is None:
        return current, {}
    if isinstance(p, str):
        return p, {}
    return p.get("at", current), p


# ------------------------------------------------------------------ geometry
def rects(X, place, box, opts, contain=False):
    """(presenter rect, graphics region) for a place; rects are (x, y, w, h) in layout px, region None = whole frame.
    The regions keep shapes effects already know: 9:16 card leaves a 16:9 page above it, side leaves a tall page."""
    W = X.W
    H = X.H
    L, T, R, B = box
    cw = R - L
    ch = B - T
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
    if X.portrait:
        if place == "card":
            rh = round(cw * 9 / 16)
            h = ch - rh - 32
            w = round(h * 0.92)
            x = L + (cw - w) / 2
            y = B - h
            region = (L, T, cw, rh)
        elif place == "side":
            w = round(cw * 0.42)
            h = round(ch * 0.66)
            x = R - w
            y = B - h
            region = (L, T, cw - w - 32, ch)
        else:   # corner
            w = round(cw * 0.27)
            h = round(w * 1.14)
            x = R - w
            y = T
            region = (L, y + h + 32, cw, ch - h - 32)
    else:
        if place == "card":
            h = round(ch * 0.44)
            w = round(h * 0.96)
            x = R - w
            y = B - h
            region = (L, T, cw - w - 40, ch)
        elif place == "side":
            w = round(cw * 0.36)
            h = ch
            x = R - w
            y = T
            region = (L, T, cw - w - 40, ch)
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
        kind = "none"
        if self.chs:
            kind = self.chs["spec"]["kind"]
        current = "full"
        if self.spec and self.spec.get("at"):
            current = self.spec["at"]
        has_captions = bool(X.chars) and style.get("captions") is not False
        for i, b in enumerate(beats):
            place, opts = place_of(b, current)
            if place not in PLACES:
                raise SystemExit(f"beat {i}: presenter place {place!r}; have: {', '.join(PLACES)}")
            current = place
            beat_kind = kind
            if self.chs:
                beat_kind = self.chs["list"][self.chs["of_beat"][i]]["device"]
            box = device.content_box(X, beat_kind, has_captions)
            if not self.spec:
                pres = (0, 0, X.W, X.H)
                region = None
                place = "none"
            else:
                contain = (self.spec.get("fit") or default_fit(self.spec.get("src", ""))) == "contain"
                pres, region = rects(X, place, box, opts, contain)
            self.places.append(place)
            self.opts.append(opts)
            self.pres.append(pres)
            self.regions.append(region)
        self._saved = None
        self._n0 = 0
        self.frame_w = X.W

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

    def look(self, i, skin):
        """the CSS values of the presenter on beat i (all tweenable)."""
        place = self.places[i]
        x, y, w, h = self.pres[i]
        w_ = self.world_at(i)
        framed = place in ("card", "side", "corner")
        bw = skin["border"] if framed else 0
        radius = skin["radius"] if framed else 0
        colour_key = skin["border_colour"]
        border_colour = w_.get(colour_key, w_["fg"])
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
        out = {"x": round(x, 1), "y": round(y, 1), "width": round(w, 1), "height": round(h, 1),
               "borderRadius": radius, "borderWidth": bw, "borderColor": border_colour, "backgroundColor": ground}
        out["opacity"] = 0 if place == "hidden" else 1
        out["shadow"] = 1 if framed else 0
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
        pos = f"{focus[0]}% {focus[1]}%"
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
        first = self.look(0, skin)
        sty = (f"left:0; top:0; width:{first['width']}px; height:{first['height']}px; "
               f"border-radius:{first['borderRadius']}px; border-width:{first['borderWidth']}px; border-color:{first['borderColor']}; "
               f"background-color:{first['backgroundColor']}; z-index:{Z_PRESENTER}; opacity:{first['opacity']};")
        # the shadow is a sibling (the subject clips its own overflow), shown only when the subject is framed
        sh_sty = (f"left:0; top:0; width:{first['width']}px; height:{first['height']}px; border-radius:{first['borderRadius']}px; "
                  f"box-shadow:{skin['shadow']}; z-index:{Z_PRESENTER - 1}; opacity:{first['shadow']};")
        X.els.append(f'<div id="pzsh" class="pzsh" style="position:absolute; pointer-events:none; {sh_sty}"></div>')
        X.tw(f'tl.set("#pzsh", {{x:{first["x"]}, y:{first["y"]}}}, 0);')
        X.els.append(f'<div id="pz" class="pz" style="{sty}"><div class="pzm">{media}</div><div class="pzs"></div>{tag_html}</div>')
        X.tw(f'tl.set("#pz", {{x:{first["x"]}, y:{first["y"]}}}, 0);')
        # still subjects breathe slowly so a held card never freezes
        if not fit.is_video(src):
            X.tw(f'tl.fromTo("#pz .pzi", {{scale:1.0}}, {{scale:1.08, duration:{D:.2f}, ease:"none"}}, 0);')
        self.set_extras(X, 0, 0.0, instant=True)
        for i in range(1, len(self.places)):
            a = self.look(i - 1, skin)
            b = self.look(i, skin)
            if a == b:
                continue
            t = self.times[i][0]
            mv = float(self.opts[i].get("move", MOVE))
            t0 = max(0.0, t - LEAD)
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
            self.set_extras(X, i, t0)
            if self.places[i] != self.places[i - 1]:
                X.sfx(t0 + 0.05, "whoosh_soft", 0.35)

    def set_extras(self, X, i, t, instant=False):
        """the scrim (full frame only, for caption contrast) and the name tag (framed places only)."""
        place = self.places[i]
        wants_scrim = self.spec.get("scrim")
        if wants_scrim is None:
            wants_scrim = default_fit(self.spec["src"]) == "cover"     # a cut-out stands on its ground: no scrim
        scrim = 0
        if place == "full" and wants_scrim:
            scrim = 1
        tag = 1 if place in ("card", "side", "corner") else 0
        dur = 0.01 if instant else 0.4
        X.tw(f'tl.to("#pz .pzs", {{opacity:{scrim}, duration:{dur}}}, {t:.3f});')
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
