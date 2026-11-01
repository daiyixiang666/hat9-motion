"""shared helpers for media-heavy effects (not an effect: files starting with _ are skipped by the loader).

items()  — normalise `items` / `images` / `media` (paths, or dicts {src | video, caption, focus, fit}) into
           [{src, video, caption, focus, fit, ar}], any count, stills and clips mixed
poster() — a still frame of a clip, written into the build (for tiles that should not play)
atlas()  — many pictures packed into one JPEG with Pillow, for walls of 25+ tiles: each tile is then just a
           background-position, so a 500-tile sea renders as fast as a 5-tile one, and identically every time
stage()  — an untimed layer at the root for effects whose tiles hold timed <video>: HyperFrames only seeks timed
           media and a timed video may not sit inside a timed clip, so the moving part lives here and the timeline
           shows / hides it for the beat
vtile()  — the timed <video> for one tile (cover + focal point)
"""
import hashlib, math, subprocess
from pathlib import Path

from h9 import fit


def items(X, p):
    raw = p.get("items")
    if raw in (None, "", []): raw = p.get("media")
    if raw in (None, "", []): raw = p.get("images")
    if raw in (None, "", []): raw = [p.get("video") or p.get("image")] if (p.get("video") or p.get("image")) else []
    if isinstance(raw, str): raw = fit.as_list(raw)
    out = []
    for r in raw:
        d = dict(r) if isinstance(r, dict) else {}
        src = (d.get("video") or d.get("src") or d.get("image")) if d else r
        if not src: continue
        vid = bool(d.get("video")) or fit.is_video(src)
        ar = fit.aspect(X, src)
        out.append({"src": src, "video": vid, "caption": d.get("caption", "") or "", "focus": d.get("focus"), "fit": d.get("fit", "auto"),
                    "start": float(d.get("start", 0) or 0), "ar": max(0.25, min(4.0, ar))})
    return out


def _key(*parts):
    return hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:12]


def poster(X, src, at=1.0):
    """(project url, absolute path) of a still from a clip."""
    a = fit._abs(X, src)
    dst = X.out / "assets" / "img" / f"vp_{_key(a, at)}.jpg"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dur = fit.duration(a) or 2.0
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{min(at, dur * 0.4):.2f}", "-i", str(a), "-frames:v", "1",
                        "-vf", "scale=960:-2", "-q:v", "3", str(dst)], check=True)
    return f"assets/img/{dst.name}", dst


def still(X, it):
    """a project url for the item as a still picture (clips → their poster)."""
    return poster(X, it["src"])[0] if it["video"] else X.asset(it["src"])


def _centering(focus):
    f = fit.focus_css(focus).replace("%", "").split()
    try: return (float(f[0]) / 100, float(f[1]) / 100)
    except (ValueError, IndexError): return (0.5, 0.5)


def atlas(X, its, tw, th):
    """pack every item, cropped to tw×th px, into one JPEG. Returns (url, cols, atlas_w, atlas_h)."""
    from PIL import Image, ImageOps
    n = len(its)
    cols = max(1, min(n, int(math.ceil(math.sqrt(n * th / tw)))))
    rows = int(math.ceil(n / cols))
    k = _key(tw, th, *[(it["src"], it.get("focus")) for it in its])
    dst = X.out / "assets" / "img" / f"atlas_{k}.jpg"
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        sheet = Image.new("RGB", (cols * tw, rows * th), (24, 24, 24))
        cache = {}
        for i, it in enumerate(its):
            path = poster(X, it["src"])[1] if it["video"] else fit._abs(X, it["src"])
            key = (str(path), it.get("focus"))
            if key not in cache:
                with Image.open(path) as im:
                    cache[key] = ImageOps.fit(im.convert("RGB"), (tw, th), Image.LANCZOS, centering=_centering(it.get("focus")))
            r, c = divmod(i, cols)
            sheet.paste(cache[key], (c * tw, r * th))
        sheet.save(dst, quality=84)
    return f"assets/img/{dst.name}", cols, cols * tw, rows * th


def atlas_bg(url, cols, aw, ah, tw, th, i, w, h):
    """CSS background for tile i of an atlas, drawn at w×h px."""
    r, c = divmod(i, cols)
    sx, sy = w / tw, h / th
    return f"background-image:url({url}); background-size:{aw * sx:.1f}px {ah * sy:.1f}px; background-position:{-c * tw * sx:.1f}px {-r * th * sy:.1f}px"


def vtile(X, src, t, d, focus=None, start=0.0):
    a = fit._abs(X, src)
    url = X.asset(src, "video")
    dur = fit.duration(a) or d
    ms = min(max(0.0, float(start)), max(0.0, dur - d)) if dur > d else 0.0
    fit._TRACK[0] += 1
    return (f'<video id="mxv{fit._TRACK[0]}" class="clip" src="{url}" muted playsinline data-start="{t:.3f}" data-duration="{d:.3f}" data-track-index="{fit._TRACK[0]}" '
            f'data-media-start="{ms:.3f}" style="object-fit:cover; object-position:{fit.focus_css(focus)}"></video>')


def stage(X, cid, t, d, inner, theme_vars="", z=4, cls=""):
    """append the untimed root layer; returns its id (selectors: '#<id> …')."""
    sid = f"{cid}_st"
    X.els.append(f'<div id="{sid}" class="fx mx-root {cls}" style="position:absolute; inset:0; overflow:hidden; z-index:{z}; visibility:hidden; {theme_vars}">{inner}</div>')
    X.tw(f'tl.set("#{sid}", {{visibility:"visible"}}, {t:.3f});')
    X.tw(f'tl.set("#{sid}", {{visibility:"hidden"}}, {t + d:.3f});')
    return sid
