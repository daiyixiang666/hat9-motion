"""Chapter device: one frame around the whole film — a generic camera viewfinder, a browser window or a phone screen —
whose mode label / tab title changes at every chapter, while the background colour world changes with it.

video.json
  meta.device = "camera" | "browser" | "phone" | "none"   or   {"kind": "camera", "brand": "我的频道", "url": "example.com"}
  beat.chapter = {"label": "PANO", "sub": "全景", "bg": "ink" | "#1d4ed8", "title": "开源", "device": "browser", "url": "…"}
    label   the mode name (camera pill / carousel), tab title (browser), screen title (phone)
    sub     a short local-language name shown with it (camera: 「全景 PANO」)
    bg      the chapter's ground: a style token (bg, fg, ink, paper, accent, card, muted) or a colour; default = the
            next colour of the style's palette, never the same as the chapter before
    title   a few words shown in the corner (camera: // 02 — 全景 · title) / page title (browser)
    device  this chapter only, in another device (e.g. one chapter in a browser)
  "chapter": true (the old flag) still means "new chapter" without a device label.

The chrome is one timed clip per run of chapters in the same device (z 44: above transitions, under the captions)
and the ground is one clip under everything (z 0). Colours, radius and type come from the style (SKIN below), so the
device re-skins with the style. The content box (where the presenter and the effects may go) leaves the chrome and
the caption band clear.
"""
import re

from h9 import fit

Z_BG = 0
Z_CHROME = 44
DEVICES = ("camera", "browser", "phone", "none")

# per-style skin of the chrome: pill / tab radius, stroke of the viewfinder brackets, pill ground, typeface roles
SKIN_DEFAULT = {"radius": "999px", "stroke": 4, "pill_bg": "rgba(14,14,16,.62)", "pill_fg": "#ffffff", "tab_radius": "14px",
                "label_font": "var(--f-body)", "small_font": "var(--f-mono, monospace)", "bracket": 58}
SKIN = {
    "minimal":  {"radius": "999px", "stroke": 3, "pill_bg": "rgba(43,41,37,.78)", "bracket": 50},
    "poster":   {"radius": "0px", "stroke": 8, "pill_bg": "#0a0a0a", "tab_radius": "0px", "label_font": "var(--f-display)", "bracket": 72},
    "flat":     {"radius": "999px", "stroke": 6, "pill_bg": "rgba(36,37,90,.72)", "tab_radius": "22px", "bracket": 64},
    "ink":      {"radius": "4px", "stroke": 3, "pill_bg": "rgba(23,22,18,.82)", "tab_radius": "4px", "label_font": "var(--f-display)", "bracket": 46},
    "screen":   {"radius": "8px", "stroke": 2, "pill_bg": "rgba(10,12,16,.72)", "tab_radius": "10px", "bracket": 40},
    "pixel":    {"radius": "0px", "stroke": 6, "pill_bg": "#1a1c2c", "tab_radius": "0px", "bracket": 48},
    "sketch":   {"radius": "999px", "stroke": 4, "pill_bg": "rgba(31,31,34,.85)", "tab_radius": "18px", "bracket": 54},
    "zine":     {"radius": "0px", "stroke": 7, "pill_bg": "#141414", "tab_radius": "0px", "label_font": "var(--f-display)", "bracket": 66},
    "papercut": {"radius": "6px", "stroke": 5, "pill_bg": "rgba(30,27,24,.82)", "tab_radius": "6px", "bracket": 60},
    "press":    {"radius": "2px", "stroke": 4, "pill_bg": "#111111", "tab_radius": "2px", "label_font": "var(--f-display)", "bracket": 52},
    "doc":      {"radius": "0px", "stroke": 2, "pill_bg": "rgba(5,5,5,.8)", "tab_radius": "0px", "bracket": 44},
    "hud":      {"radius": "0px", "stroke": 2, "pill_bg": "rgba(9,11,14,.8)", "tab_radius": "0px", "bracket": 70},
    "atlas":    {"radius": "6px", "stroke": 3, "pill_bg": "rgba(11,29,38,.8)", "tab_radius": "6px", "bracket": 52},
}
RECORDING = ("REC", "VIDEO", "LIVE", "TIME-LAPSE", "SLO-MO", "CINEMATIC", "录像", "视频", "延时", "慢动作")
TOKEN_NAMES = ("bg", "fg", "ink", "paper", "accent", "card", "muted", "line")


# ------------------------------------------------------------------ colours
def to_rgb(c):
    """'#abc' / '#aabbcc' / 'rgb(…)' / 'rgba(…)' -> (r, g, b) 0–255, or None."""
    s = str(c).strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = h[0] * 2 + h[1] * 2 + h[2] * 2
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return (r, g, b)
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+).*\)", s)
    if m:
        return (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return None


def to_hex(rgb):
    parts = []
    for v in rgb:
        v = int(round(max(0, min(255, v))))
        parts.append(f"{v:02x}")
    return "#" + "".join(parts)


def mix(a, b, share_a):
    """a colour share_a of the way from b to a (hex); falls back to a when either is not parseable."""
    ra = to_rgb(a)
    rb = to_rgb(b)
    if ra is None or rb is None:
        return a
    out = []
    for k in range(3):
        out.append(ra[k] * share_a + rb[k] * (1 - share_a))
    return to_hex(out)


def lum(c):
    rgb = to_rgb(c)
    if rgb is None:
        return 0.5
    lin = []
    for v in rgb:
        v = v / 255
        if v <= 0.03928:
            lin.append(v / 12.92)
        else:
            lin.append(((v + 0.055) / 1.055) ** 2.4)
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la = lum(a)
    lb = lum(b)
    hi = max(la, lb)
    lo = min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def resolve_colour(value, tokens):
    if value in TOKEN_NAMES:
        return tokens.get(value, tokens.get("bg"))
    return value


def palette(tokens):
    """the style's own grounds, in the order chapters take them by default."""
    out = []
    for key in ("bg", "ink", "accent", "paper", "card", "fg"):
        c = tokens.get(key)
        if c and to_rgb(c) is not None and c not in out:
            out.append(c)
    return out


def next_distinct(pal, prev_bg, wanted):
    """the first palette colour after `wanted` that is clearly different from the previous chapter's ground."""
    start = 0
    if wanted in pal:
        start = pal.index(wanted) + 1
    for k in range(len(pal)):
        c = pal[(start + k) % len(pal)]
        if contrast(c, prev_bg) >= 1.3:
            return c
    return wanted


def world(bg, tokens):
    """the colour world of a chapter ground: the token set its pages paint with."""
    candidates = []
    for key in ("ink", "fg", "bg", "paper", "card"):
        c = tokens.get(key)
        if c and to_rgb(c) is not None:
            candidates.append(c)
    darkest = "#111111"
    lightest = "#f6f3ec"
    if candidates:
        darkest = candidates[0]
        lightest = candidates[0]
        for c in candidates:
            if lum(c) < lum(darkest):
                darkest = c
            if lum(c) > lum(lightest):
                lightest = c
    if lum(darkest) > 0.08:
        darkest = "#111111"
    if lum(lightest) < 0.6:
        lightest = "#f6f3ec"
    if contrast(darkest, bg) >= contrast(lightest, bg):
        fg = darkest
        other = lightest
    else:
        fg = lightest
        other = darkest
    accent = tokens.get("accent", fg)
    if to_rgb(accent) is None or contrast(accent, bg) < 2.2:
        accent = other if contrast(other, bg) > contrast(fg, bg) * 0.5 else fg
        if contrast(accent, bg) < 2.2:
            accent = fg
    light_ground = lum(bg) > 0.4
    if light_ground:
        card = mix("#ffffff", bg, 0.6)
    else:
        card = mix(fg, bg, 0.09)
    return {"bg": bg, "fg": fg, "muted": mix(fg, bg, 0.82), "line": mix(fg, bg, 0.2), "card": card, "card-fg": fg,
            "accent": accent, "light": light_ground}


def world_vars(w):
    """CSS custom properties for a chapter's pages (set on the region wrapper of each beat)."""
    parts = []
    for key in ("bg", "fg", "muted", "line", "card", "card-fg", "accent"):
        parts.append(f"--{key}:{w[key]}")
    return ";".join(parts)


# ------------------------------------------------------------------ chapters
def device_spec(meta):
    d = meta.get("device")
    if isinstance(d, str):
        return {"kind": d}
    if isinstance(d, dict):
        out = dict(d)
        if not out.get("kind"):
            out["kind"] = "camera"
        return out
    return {"kind": "none"}


def chapters(video, beats, times, style):
    """[{i0, i1, t0, t1, label, sub, title, bg, world, device, url, k}] and the chapter index of every beat.
    None when the film has no device and no chapter objects."""
    meta = video.get("meta") or {}
    spec = device_spec(meta)
    has_obj = False
    for b in beats:
        if isinstance(b.get("chapter"), dict):
            has_obj = True
    if spec["kind"] == "none" and not has_obj:
        return None
    tokens = style["tokens"]
    pal = palette(tokens)
    out = []
    of_beat = []
    for i, b in enumerate(beats):
        ch = b.get("chapter")
        starts = isinstance(ch, dict) or i == 0
        if starts:
            info = ch if isinstance(ch, dict) else {}
            prev_bg = out[-1]["bg"] if out else None
            bg = info.get("bg")
            if bg:
                bg = resolve_colour(bg, tokens)
            elif pal:
                bg = pal[len(out) % len(pal)]
            else:
                bg = tokens.get("bg", "#111111")
            if prev_bg and contrast(bg, prev_bg) < 1.3 and len(pal) > 1:
                # a new chapter must look new: styles whose bg / ink / paper are one colour step to the next ground
                bg = next_distinct(pal, prev_bg, bg)
            label = str(info.get("label") or spec.get("label") or "PHOTO")
            item = {"i0": i, "i1": i, "t0": times[i][0], "t1": times[i][0] + times[i][1], "label": label,
                    "sub": str(info.get("sub") or ""), "title": str(info.get("title") or ""), "bg": bg,
                    "world": world(bg, tokens), "device": info.get("device") or spec["kind"],
                    "url": str(info.get("url") or spec.get("url") or ""), "k": len(out)}
            out.append(item)
        cur = out[-1]
        cur["i1"] = i
        cur["t1"] = times[i][0] + times[i][1]
        of_beat.append(cur["k"])
    return {"spec": spec, "list": out, "of_beat": of_beat}


def skin_for(style):
    s = dict(SKIN_DEFAULT)
    chain = list(style.get("_chain") or [])
    chain.reverse()                    # base first, the style itself last (wins)
    for sid in chain:
        if sid in SKIN:
            s.update(SKIN[sid])
    s.update(style.get("device_skin") or {})
    return s


# ------------------------------------------------------------------ geometry
def content_box(X, kind, captions):
    """(left, top, right, bottom) px where the presenter and the beat's graphics may go: clear of the device chrome,
    the platform's top bar (9:16) and the caption band."""
    W = X.W
    H = X.H
    if X.portrait:
        tops = {"camera": 304, "browser": 356, "phone": 318, "none": 250}
        top = tops.get(kind, 250)
        bottom = 1296 if captions else 1480
        if H != 1920:
            bottom = int(H * bottom / 1920)
        return (48, top, W - 48, bottom)
    tops = {"camera": 120, "browser": 150, "phone": 132, "none": 84}
    top = tops.get(kind, 84)
    right = W - 72
    if kind == "camera":
        right = W - 220
    bottom = H - 176 if captions else H - 72
    return (72, top, right, bottom)


# ------------------------------------------------------------------ chrome
CSS = """
.dvbg { position:absolute; inset:0; }
.dv { pointer-events:none; font-family:var(--dv-small); color:var(--dv-fg, #fff); }
.dv .br { position:absolute; width:var(--dv-br); height:var(--dv-br); border:0 solid currentColor; opacity:.78; }
.dv .br.tl { border-left-width:var(--dv-st); border-top-width:var(--dv-st); }
.dv .br.tr { border-right-width:var(--dv-st); border-top-width:var(--dv-st); }
.dv .br.bl { border-left-width:var(--dv-st); border-bottom-width:var(--dv-st); }
.dv .br.bk { border-right-width:var(--dv-st); border-bottom-width:var(--dv-st); }
.dv .chap { position:absolute; white-space:nowrap; font-size:22px; letter-spacing:.06em; opacity:.82; }
.dv .chap span { position:absolute; left:0; top:0; }
.dv .tc { position:absolute; white-space:nowrap; font-size:22px; letter-spacing:.08em; font-weight:700; }
.dv .tc i { display:inline-block; width:14px; height:14px; border-radius:50%; background:#ff453a; margin-right:10px; vertical-align:1px; }
.dv .brand { position:absolute; text-align:right; white-space:nowrap; }
.dv .brand b { display:block; font:800 30px var(--dv-label); letter-spacing:.01em; }
.dv .brand small { display:block; font-size:18px; letter-spacing:.14em; opacity:.6; margin-top:4px; }
.dv .pillrow { position:absolute; left:0; right:0; text-align:center; }
.dv .pill { display:inline-flex; white-space:nowrap; align-items:center; gap:12px;
  background:var(--dv-pill-bg); color:var(--dv-pill-fg); border-radius:var(--dv-r); padding:9px 22px 9px 18px; font:700 26px var(--dv-label); letter-spacing:.04em; }
.dv .pill i { width:13px; height:13px; border-radius:50%; background:var(--accent); flex:none; }
.dv .pill em { font-style:normal; font-family:var(--dv-small); font-size:22px; letter-spacing:.12em; opacity:.92; }
.dv .modes { position:absolute; white-space:nowrap; }
.dv .modes span { position:absolute; top:0; width:300px; text-align:center; font:600 26px var(--dv-label); letter-spacing:.06em; opacity:.5; }
.dv .modes.vrt span { width:auto; text-align:right; }
.dv .shut { position:absolute; border-radius:50%; border:7px solid currentColor; }
.dv .shut i { position:absolute; inset:8px; border-radius:50%; background:currentColor; }
.dv .thumb { position:absolute; border-radius:14px; border:3px solid currentColor; overflow:hidden; }
.dv .thumb i { position:absolute; inset:0; }
.dv .flip { position:absolute; border-radius:50%; background:color-mix(in srgb, currentColor 16%, transparent); display:grid; place-items:center; }
.dv .flip svg { width:58%; height:58%; }
.dv .flash { position:absolute; inset:0; background:#fff; opacity:0; }
/* browser */
.dv .bwin { position:absolute; left:0; right:0; top:0; }
.dv .tabs { position:absolute; display:flex; align-items:flex-end; gap:8px; }
.dv .dots { position:absolute; display:flex; gap:12px; }
.dv .dots i { width:20px; height:20px; border-radius:50%; display:block; }
.dv .tab { position:absolute; bottom:0; height:100%; border-radius:var(--dv-tab-r) var(--dv-tab-r) 0 0; overflow:hidden; }
.dv .tab span { position:absolute; left:26px; right:20px; top:0; bottom:0; display:flex; align-items:center; white-space:nowrap; overflow:hidden; font:700 24px var(--dv-label); }
.dv .url { position:absolute; border-radius:var(--dv-r); display:flex; align-items:center; gap:14px; padding:0 26px; overflow:hidden; }
.dv .url b { font:500 24px var(--dv-small); letter-spacing:.02em; white-space:nowrap; }
.dv .url svg { width:22px; height:22px; flex:none; opacity:.7; }
.dv .load { position:absolute; height:4px; background:var(--accent); transform-origin:0 50%; transform:scaleX(0); }
/* phone */
.dv .sbar { position:absolute; display:flex; justify-content:space-between; align-items:center; font:700 28px var(--dv-label); }
.dv .sbar .ic { display:flex; gap:10px; align-items:center; }
.dv .sbar .bat { width:46px; height:22px; border:2.5px solid currentColor; border-radius:7px; position:relative; opacity:.9; }
.dv .sbar .bat::after { content:''; position:absolute; left:3px; top:3px; bottom:3px; width:70%; background:currentColor; border-radius:3px; }
.dv .sbar .sig { display:flex; gap:4px; align-items:flex-end; height:22px; } .dv .sbar .sig i { width:6px; background:currentColor; border-radius:2px; display:block; }
.dv .apphd { position:absolute; display:flex; align-items:center; justify-content:space-between; }
.dv .apphd .ttl { position:absolute; left:80px; right:80px; top:0; bottom:0; overflow:hidden; }
.dv .apphd .ttl span { position:absolute; left:0; right:0; top:0; bottom:0; display:flex; align-items:center; justify-content:center; font:800 34px var(--dv-label); white-space:nowrap; }
.dv .home { position:absolute; height:10px; border-radius:6px; background:currentColor; opacity:.55; }
"""

FLIP_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M4 12a8 8 0 0 1 13.7-5.6L20 8.7"/><path d="M20 4v4.7h-4.7"/><path d="M20 12a8 8 0 0 1-13.7 5.6L4 15.3"/>'
            '<path d="M4 20v-4.7h4.7"/></svg>')
LOCK_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">'
            '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>')


def chrome_fg(w):
    """chrome ink on a chapter ground: near-black on light grounds, white on dark ones."""
    if w["light"]:
        return mix(w["fg"], "#000000", 0.85)
    return "#ffffff"


def runs(chs):
    """contiguous runs of chapters in the same device: [(device, [chapter, …])]."""
    out = []
    for ch in chs["list"]:
        if out and out[-1][0] == ch["device"]:
            out[-1][1].append(ch)
        else:
            out.append((ch["device"], [ch]))
    return out


def mode_name(ch):
    if ch["sub"]:
        return ch["sub"]
    return ch["label"]


def build(X, chs, D, style):
    """the ground clip, the chrome clips and every chapter change."""
    if not chs:
        return
    skin = skin_for(style)
    chs["skin"] = skin
    X.css("dv-base", CSS)
    root_vars = (f"#root {{ --dv-r:{skin['radius']}; --dv-tab-r:{skin['tab_radius']}; --dv-st:{skin['stroke']}px; --dv-br:{skin['bracket']}px;"
                 f" --dv-pill-bg:{skin['pill_bg']}; --dv-pill-fg:{skin['pill_fg']}; --dv-label:{skin['label_font']}; --dv-small:{skin['small_font']}; }}")
    X.css("dv-vars", root_vars)
    # the ground: one clip, its colour steps with the chapters
    first = chs["list"][0]
    X.clip("dvbg", 0, D, "", "dvbg", Z_BG, track=9, sty=f"background:{first['bg']};")
    for ch in chs["list"][1:]:
        X.tw(f'tl.to("#dvbg", {{backgroundColor:"{ch["bg"]}", duration:0.5, ease:"power2.inOut"}}, {ch["t0"] - 0.2:.3f});')
    k = 0
    for kind, group in runs(chs):
        t0 = group[0]["t0"]
        t1 = group[-1]["t1"]
        if group[-1] is chs["list"][-1]:
            t1 = D
        cid = f"dv{k}"
        k += 1
        if kind == "camera":
            camera(X, cid, group, t0, t1, chs)
        elif kind == "browser":
            browser(X, cid, group, t0, t1, chs)
        elif kind == "phone":
            phone(X, cid, group, t0, t1, chs)
        else:
            continue
        # chrome ink follows the ground
        X.tw(f'tl.set("#{cid}", {{color:"{chrome_fg(group[0]["world"])}"}}, {t0:.3f});')
        for ch in group[1:]:
            X.tw(f'tl.to("#{cid}", {{color:"{chrome_fg(ch["world"])}", duration:0.4, ease:"power2.inOut"}}, {ch["t0"] - 0.15:.3f});')


def caption_mode(X):
    """the caption mode captions.build will pick (reading / punch / karaoke)."""
    meta = X.v.get("meta") or {}
    mode = meta.get("caption_mode")
    if mode:
        return mode
    preset = meta.get("caption_preset")
    if preset in ("xiaohongshu", "bilibili", "youtube"):
        return "reading"
    if preset in ("douyin", "shipinhao"):
        if X.portrait:
            return "punch"
        return "reading"
    mode = X.S.get("caption_mode")
    if mode:
        return mode
    return "reading"


def text_px(s, px):
    return fit.width(s) * px


def swap(X, sel_out, sel_in, t, axis="y", dist=44):
    """the label change: the old one leaves upward (or left), the new one rises (or slides) in."""
    X.tw(f'tl.to("{sel_out}", {{{axis}:{-dist}, opacity:0, duration:0.28, ease:"power3.in"}}, {t - 0.2:.3f});')
    X.tw(f'tl.fromTo("{sel_in}", {{{axis}:{dist}, opacity:0}}, {{{axis}:0, opacity:1, duration:0.42, ease:"expo.out", immediateRender:false}}, {t + 0.06:.3f});')


def timecode_js(X, sel, t0, t1):
    """REC 00:00:00 counting with the film (seekable: computed from the tween's value)."""
    lines = []
    lines.append("(function(){")
    lines.append(f'  var o = {{v:{t0:.3f}}};')
    lines.append(f'  var el = document.querySelector("{sel}");')
    lines.append("  function pad(n){ return (n < 10 ? '0' : '') + n; }")
    lines.append("  function show(){ var s = Math.floor(o.v); var m = Math.floor(s / 60); el.textContent = '00:' + pad(m) + ':' + pad(s % 60); }")
    lines.append(f'  tl.to(o, {{v:{t1:.3f}, duration:{t1 - t0:.3f}, ease:"none", onUpdate:show}}, {t0:.3f});')
    lines.append("})();")
    X.tw("\n".join(lines))


def corner_brackets(x0, y0, x1, y1, size):
    out = []
    out.append(f'<i class="br tl" style="left:{x0}px; top:{y0}px"></i>')
    out.append(f'<i class="br tr" style="left:{x1 - size}px; top:{y0}px"></i>')
    out.append(f'<i class="br bl" style="left:{x0}px; top:{y1 - size}px"></i>')
    out.append(f'<i class="br bk" style="left:{x1 - size}px; top:{y1 - size}px"></i>')
    return "".join(out)


def chap_line(ch):
    s = f"// {ch['k'] + 1:02d} — {mode_name(ch)}"
    if ch["title"]:
        s += f" · {ch['title']}"
    return s


def camera(X, cid, group, t0, t1, chs):
    """a generic camera viewfinder: brackets, chapter line + REC timecode, mode pill, brand, mode carousel, shutter."""
    W = X.W
    H = X.H
    P = X.portrait
    spec = chs["spec"]
    brand = str(spec.get("brand") or (X.v.get("meta") or {}).get("show") or "hat9")
    fps = int(X.fps)
    small = f"{X.aspect} · {fps}P"
    skin_br = int(chs["skin"]["bracket"])
    parts = []
    if P:
        bx0, by0, bx1, by1 = 40, 176, W - 40, 1748
        top_y = 206
    else:
        bx0, by0, bx1, by1 = 32, 28, W - 32, H - 28
        top_y = 46
    parts.append(corner_brackets(bx0, by0, bx1, by1, skin_br))
    # chapter line (top-left) + REC timecode under it
    chap = []
    for ch in group:
        X.used_text.update(chap_line(ch))
        chap.append(f'<span data-k="{ch["k"]}" style="opacity:0">{X.rich(chap_line(ch))}</span>')
    left_x = bx0 + 34
    parts.append(f'<div class="chap" style="left:{left_x}px; top:{top_y}px">{"".join(chap)}</div>')
    parts.append(f'<div class="tc" style="left:{left_x}px; top:{top_y + 36}px"><i></i>REC <b>00:00:00</b></div>')
    X.used_text.update("REC 0123456789:" + brand + small)
    # brand (top-right)
    parts.append(f'<div class="brand" style="right:{W - bx1 + 34}px; top:{top_y - 6}px"><b>{X.rich(brand)}</b><small>{X.rich(small)}</small></div>')
    # mode pill (top-centre): one pill per chapter, swapped at the boundary
    pills = []
    for ch in group:
        zh = ch["sub"]
        en = ch["label"]
        X.used_text.update(zh + en)
        inner = "<i></i>"
        if zh:
            inner += f"<b>{X.rich(zh)}</b><em>{X.rich(en)}</em>"
        else:
            inner += f"<b>{X.rich(en)}</b>"
        pill_sty = ""
        if not ch["world"]["light"] and lum(ch["bg"]) < 0.05:
            pill_sty = ' style="background:rgba(255,255,255,.16)"'      # a dark pill would vanish on a dark ground
        pills.append(f'<div class="pillrow" data-k="{ch["k"]}" style="top:{top_y + 6}px; opacity:0"><span class="pill"{pill_sty}>{inner}</span></div>')
    parts.append("".join(pills))
    # mode carousel + shutter row
    every = []                      # the carousel lists every camera chapter of the film, so it keeps its place
    for ch in chs["list"]:
        if ch["device"] == "camera":
            every.append(ch)
    names = []
    for ch in every:
        names.append(mode_name(ch))
    gap = 64
    px = 26
    centres = []
    x = 0.0
    for j, nm in enumerate(names):
        w = text_px(nm, px) + 0.06 * px * len(nm)
        if j:
            x += gap
        centres.append(x + w / 2)
        x += w
    spans = []
    for j, nm in enumerate(names):
        spans.append(f'<span data-k="{every[j]["k"]}" style="left:{centres[j] - 150:.0f}px">{X.rich(nm)}</span>')
    if P:
        row_y = 1568
        shut_c = (W / 2, 1668)
        shut_r = 50
        thumb = (120, 1668, 76)
        flip = (W - 120, 1668, 76)
        modes_x = W / 2
        parts.append(f'<div class="modes" style="left:{modes_x:.0f}px; top:{row_y}px">{"".join(spans)}</div>')
    else:
        rail_x = W - 112
        shut_c = (rail_x, H / 2)
        shut_r = 44
        thumb = (rail_x, H / 2 + 190, 64)
        flip = (rail_x, H / 2 - 190, 64)
        # 16:9: the carousel runs down the rail, beside the shutter
        vspans = []
        for j, nm in enumerate(names):
            vspans.append(f'<span data-k="{every[j]["k"]}" style="right:0; top:{j * 52}px">{X.rich(nm)}</span>')
        parts.append(f'<div class="modes vrt" style="right:{W - rail_x + 76}px; top:{H / 2 - 16:.0f}px; width:220px">{"".join(vspans)}</div>')
    parts.append(f'<div class="shut" style="left:{shut_c[0] - shut_r:.0f}px; top:{shut_c[1] - shut_r:.0f}px; width:{2 * shut_r}px; height:{2 * shut_r}px"><i></i></div>')
    parts.append(f'<div class="thumb" style="left:{thumb[0] - thumb[2] / 2:.0f}px; top:{thumb[1] - thumb[2] / 2:.0f}px; width:{thumb[2]}px; height:{thumb[2]}px"><i style="background:{group[0]["bg"]}"></i></div>')
    parts.append(f'<div class="flip" style="left:{flip[0] - flip[2] / 2:.0f}px; top:{flip[1] - flip[2] / 2:.0f}px; width:{flip[2]}px; height:{flip[2]}px">{FLIP_SVG}</div>')
    parts.append('<i class="flash"></i>')
    X.clip(cid, t0, t1 - t0, "".join(parts), "dv dv-camera", Z_CHROME, track=10)
    S = f"#{cid}"
    timecode_js(X, f"{S} .tc b", t0, t1)
    # first chapter of the run: everything shows
    c0 = group[0]["k"]
    X.tw(f'tl.set("{S} .chap span[data-k=\'{c0}\'], {S} .pillrow[data-k=\'{c0}\']", {{opacity:1}}, {t0:.3f});')
    X.tw(f'tl.from("{S} .br", {{scale:1.25, opacity:0, duration:0.5, ease:"expo.out", stagger:0.04}}, {t0:.3f});')
    carousel(X, S, group[0], every.index(group[0]), centres, P, t0, True)
    shutter_mode(X, S, group[0], t0, instant=True)
    for j in range(1, len(group)):
        prev = group[j - 1]
        ch = group[j]
        t = ch["t0"]
        swap(X, f'{S} .pillrow[data-k=\'{prev["k"]}\']', f'{S} .pillrow[data-k=\'{ch["k"]}\']', t)
        swap(X, f'{S} .chap span[data-k=\'{prev["k"]}\']', f'{S} .chap span[data-k=\'{ch["k"]}\']', t)
        carousel(X, S, ch, every.index(ch), centres, P, t, False)
        shutter_mode(X, S, ch, t)
        # the capture: brackets breathe in, a faint flash, the last ground lands in the thumbnail
        X.tw(f'tl.fromTo("{S} .br", {{scale:1}}, {{scale:0.94, duration:0.14, ease:"power2.out", yoyo:true, repeat:1, immediateRender:false}}, {t - 0.12:.3f});')
        X.tw(f'tl.fromTo("{S} .flash", {{opacity:0}}, {{opacity:0.22, duration:0.06, ease:"none", yoyo:true, repeat:1, immediateRender:false}}, {t - 0.04:.3f});')
        X.tw(f'tl.to("{S} .thumb i", {{backgroundColor:"{prev["bg"]}", duration:0.01}}, {t:.3f});')
        X.tw(f'tl.fromTo("{S} .thumb", {{scale:1.18}}, {{scale:1, duration:0.4, ease:"back.out(2)", immediateRender:false}}, {t:.3f});')
        X.sfx(t - 0.05, "shutter", 0.3)


def carousel(X, S, ch, j, centres, portrait, t, first):
    """centre the active mode (index j) in the carousel; the active name takes the chapter's accent."""
    dur = 0.01 if first else 0.5
    at = t if first else t - 0.1
    if portrait:
        X.tw(f'tl.to("{S} .modes", {{x:{-centres[j]:.0f}, duration:{dur}, ease:"power3.inOut"}}, {at:.3f});')
    else:
        X.tw(f'tl.to("{S} .modes", {{y:{-52 * j}, duration:{dur}, ease:"power3.inOut"}}, {at:.3f});')
    ink = chrome_fg(ch["world"])
    X.tw(f'tl.set("{S} .modes span", {{opacity:0.66, color:"{ink}", scale:1}}, {at:.3f});')
    X.tw(f'tl.set("{S} .modes span[data-k=\'{ch["k"]}\']", {{opacity:1, color:"{ch["world"]["accent"]}", scale:1.08}}, {at:.3f});')


def shutter_mode(X, S, ch, t, instant=False):
    """recording modes turn the shutter's core into a red rounded square; photo modes keep the disc in the chrome ink."""
    rec = False
    for word in RECORDING:
        if word.lower() in (ch["label"] + " " + ch["sub"]).lower():
            rec = True
    dur = 0.01 if instant else 0.35
    if rec:
        X.tw(f'tl.to("{S} .shut i", {{backgroundColor:"#ff453a", borderRadius:"24%", scale:0.6, duration:{dur}, ease:"power2.inOut"}}, {t:.3f});')
    else:
        ink = chrome_fg(ch["world"])
        X.tw(f'tl.to("{S} .shut i", {{backgroundColor:"{ink}", borderRadius:"50%", scale:1, duration:{dur}, ease:"power2.inOut"}}, {t:.3f});')


def browser(X, cid, group, t0, t1, chs):
    """a generic browser window: tab strip (the tab title is the chapter), address bar (retyped per chapter), load bar."""
    W = X.W
    P = X.portrait
    spec = chs["spec"]
    if P:
        y0 = 172
        tab_h = 64
        url_y = 252
        url_h = 70
        x0 = 40
    else:
        y0 = 14
        tab_h = 56
        url_y = 80
        url_h = 52
        x0 = 28
    first = group[0]["world"]
    bar_bg = mix(first["fg"], first["bg"], 0.07)
    parts = []
    parts.append(f'<div class="bwin" style="height:{url_y + url_h + 18}px; background:{bar_bg}; border-bottom:2px solid {first["line"]}"></div>')
    parts.append(f'<div class="dots" style="left:{x0 + 6}px; top:{y0 + tab_h / 2 - 10:.0f}px"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></div>')
    tab_x = x0 + 120
    tab_w = min(520, W - tab_x - 120)
    tabs = []
    for ch in group:
        name = ch["title"] or ch["label"]
        X.used_text.update(name)
        tabs.append(f'<span data-k="{ch["k"]}" style="opacity:0">{X.rich(name)}</span>')
    parts.append(f'<div class="tab" style="left:{tab_x}px; top:{y0}px; width:{tab_w}px; height:{tab_h}px; background:{first["bg"]}">{"".join(tabs)}</div>')
    parts.append(f'<div class="tab ghost" style="left:{tab_x + tab_w + 10}px; top:{y0 + 8}px; width:{min(220, W - tab_x - tab_w - 60)}px; height:{tab_h - 8}px; opacity:.35; background:{first["line"]}"></div>')
    urls = []
    for ch in group:
        u = ch["url"] or spec.get("url") or "example.com"
        X.used_text.update(u)
        urls.append(f'<b data-k="{ch["k"]}" style="position:absolute; left:{64}px; opacity:0">{X.rich(u)}</b>')
    url_w = W - 2 * x0
    parts.append(f'<div class="url" style="left:{x0}px; top:{url_y}px; width:{url_w}px; height:{url_h}px; background:{first["bg"]}">{LOCK_SVG}{"".join(urls)}</div>')
    parts.append(f'<i class="load" style="left:0; top:{url_y + url_h + 16}px; width:{W}px"></i>')
    X.clip(cid, t0, t1 - t0, "".join(parts), "dv dv-browser", Z_CHROME, track=10)
    S = f"#{cid}"
    for j, ch in enumerate(group):
        t = ch["t0"]
        X.tw(f'tl.to("{S} .tab:not(.ghost), {S} .url", {{backgroundColor:"{ch["bg"]}", duration:0.3}}, {t - 0.1:.3f});')
        X.tw(f'tl.to("{S} .bwin", {{backgroundColor:"{mix(ch["world"]["fg"], ch["bg"], 0.07)}", borderBottomColor:"{ch["world"]["line"]}", duration:0.3}}, {t - 0.1:.3f});')
        if j:
            prev = group[j - 1]
            swap(X, f'{S} .tab span[data-k=\'{prev["k"]}\']', f'{S} .tab span[data-k=\'{ch["k"]}\']', t)
            X.tw(f'tl.to("{S} .url b[data-k=\'{prev["k"]}\']", {{opacity:0, duration:0.15}}, {t - 0.15:.3f});')
        else:
            X.tw(f'tl.set("{S} .tab span[data-k=\'{ch["k"]}\']", {{opacity:1}}, {t:.3f});')
            X.tw(f'tl.from("{S} .bwin, {S} .tab, {S} .url, {S} .dots", {{yPercent:-60, opacity:0, duration:0.45, ease:"expo.out", stagger:0.04}}, {t:.3f});')
        # the address types itself in, the load bar sweeps
        X.tw(f'tl.set("{S} .url b[data-k=\'{ch["k"]}\']", {{opacity:1}}, {t:.3f});')
        X.tw(f'tl.fromTo("{S} .url b[data-k=\'{ch["k"]}\']", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.55, ease:"steps(14)", immediateRender:false}}, {t + 0.05:.3f});')
        X.tw(f'tl.fromTo("{S} .load", {{scaleX:0, opacity:1}}, {{scaleX:1, duration:0.7, ease:"power2.inOut", immediateRender:false}}, {t + 0.1:.3f});')
        X.tw(f'tl.to("{S} .load", {{opacity:0, duration:0.2}}, {t + 0.8:.3f});')
        X.sfx(t + 0.05, "type", 0.25)


def phone(X, cid, group, t0, t1, chs):
    """a generic phone screen: status bar (clock from the film), app header (the chapter title), home indicator."""
    W = X.W
    H = X.H
    P = X.portrait
    if P:
        sb_y = 186
        hd_y = 240
        home_y = 1760
    else:
        sb_y = 18
        hd_y = 60
        home_y = H - 24
    parts = []
    sig = '<span class="sig"><i style="height:8px"></i><i style="height:13px"></i><i style="height:18px"></i><i style="height:22px"></i></span>'
    X.used_text.update("0123456789:")
    parts.append(f'<div class="sbar" style="left:64px; right:64px; top:{sb_y}px"><b class="clk">20:30</b><span class="ic">{sig}<span class="bat"></span></span></div>')
    titles = []
    for ch in group:
        name = ch["title"] or ch["sub"] or ch["label"]
        X.used_text.update(name)
        titles.append(f'<span data-k="{ch["k"]}" style="opacity:0">{X.rich(name)}</span>')
    X.used_text.update("‹···")
    parts.append(f'<div class="apphd" style="left:56px; right:56px; top:{hd_y}px; height:60px"><b style="font:400 56px var(--dv-label); line-height:1">‹</b>'
                 f'<div class="ttl">{"".join(titles)}</div><b style="font:800 34px var(--dv-label); letter-spacing:.1em">···</b></div>')
    parts.append(f'<i class="home" style="left:{W / 2 - 140:.0f}px; width:280px; top:{home_y}px"></i>')
    X.clip(cid, t0, t1 - t0, "".join(parts), "dv dv-phone", Z_CHROME, track=10)
    S = f"#{cid}"
    lines = []
    lines.append("(function(){")
    lines.append(f'  var o = {{v:{t0:.3f}}}; var el = document.querySelector("{S} .clk");')
    lines.append("  function show(){ var m = 30 + Math.floor(o.v / 60); el.textContent = '20:' + (m < 10 ? '0' : '') + m; }")
    lines.append(f'  tl.to(o, {{v:{t1:.3f}, duration:{t1 - t0:.3f}, ease:"none", onUpdate:show}}, {t0:.3f});')
    lines.append("})();")
    X.tw("\n".join(lines))
    X.tw(f'tl.set("{S} .ttl span[data-k=\'{group[0]["k"]}\']", {{opacity:1}}, {t0:.3f});')
    for j in range(1, len(group)):
        prev = group[j - 1]
        ch = group[j]
        swap(X, f'{S} .ttl span[data-k=\'{prev["k"]}\']', f'{S} .ttl span[data-k=\'{ch["k"]}\']', ch["t0"], axis="x", dist=90)


def owns_transition(chs, beat):
    """a chapter object inside a device changes chapter with the device's own move, not the style's full-frame
    transition (an explicit beat "tr" still wins)."""
    if not chs:
        return False
    if chs["spec"]["kind"] == "none":
        return False
    return isinstance(beat.get("chapter"), dict) and beat.get("tr") is None
