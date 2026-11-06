#!/usr/bin/env python3
"""video.json -> a HyperFrames project (index.html + assets) in the chosen style.

  python3 scripts/build.py examples/demo/video.json [--style ledger] [--aspect 9:16] [--out DIR]
  cd DIR && npx --yes hyperframes@0.8.191 check && npx --yes hyperframes@0.8.191 render -o out.mp4

Python standard library only (fontTools optional, for font subsetting).
"""
import argparse, importlib.util, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
from h9 import core, fx, captions, fonts, marks, pacing, delivery, fit, aefx, derive, beatsync  # noqa: E402

GSAP = "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"


def load_mod(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def load_style(sid):
    p = SKILL / "styles" / f"{sid}.py"
    if not p.exists(): raise SystemExit(f"no style {sid!r}; have: {', '.join(sorted(x.stem for x in (SKILL / 'styles').glob('[!_]*.py')))}")
    m = load_mod(p)
    st = dict(m.STYLE); st["_mod"] = m
    st["_chain"] = derive.chain(sid)                     # a custom style also wears its base's root class
    return st


def scene_fn(name, style):
    over = getattr(style["_mod"], "SCENES", {})
    if name in over: return over[name]
    p = SKILL / "scenes" / f"{name}.py"
    if not p.exists(): raise SystemExit(f"no scene {name!r}; have: {', '.join(sorted(x.stem for x in (SKILL / 'scenes').glob('[!_]*.py')))}")
    return load_mod(p).build


def probe(path):
    try:
        return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)]).strip())
    except Exception:
        return 0.0


BASE_CSS = """
* { margin:0; padding:0; box-sizing:border-box; }
html, body { width:{W}px; height:{H}px; overflow:hidden; background:var(--bg); }
#root { position:relative; width:{W}px; height:{H}px; overflow:hidden; background:var(--bg); color:var(--fg); font-family:var(--f-body, sans-serif);
  -webkit-font-smoothing:antialiased; text-rendering:geometricPrecision; font-kerning:normal; }
.clip { position:absolute; inset:0; }
.scene { overflow:hidden; }
.stage { position:absolute; inset:0; }
.cam { position:absolute; inset:0; transform-origin:50% 50%; }
.em { font-style:normal; position:relative; display:inline-block; white-space:nowrap; }
.em .emt { position:relative; z-index:1; }
.em .emb { position:absolute; z-index:0; display:block; pointer-events:none; transform-origin:0 50%; }
i.c { font-style:normal; display:inline-block; }
img { display:block; }
.cap { top:auto; height:auto; bottom:var(--cap-bottom, 56px); left:0; right:0; text-align:center; pointer-events:none; }
.cap .cp { display:inline-block; font-family:var(--f-cap, var(--f-body)); font-size:var(--cap-size, 46px); font-weight:var(--cap-weight, 700); color:var(--cap-fg, #fff);
  text-shadow:var(--cap-shadow, 0 2px 0 rgba(0,0,0,.8), 0 0 18px rgba(0,0,0,.6)); background:var(--cap-bg, none); padding:var(--cap-pad, 0); letter-spacing:.02em; border-radius:var(--cap-radius, 0); }
.cap .em .emb { display:none; } .cap .em .emt { color:var(--cap-em, var(--accent)); }
#root.v .cap { padding-left:120px; padding-right:120px; }   /* 9:16: clear of the platform's right-hand buttons */
.mascot { pointer-events:none; }
.mascot.mf-tv { background:var(--tv-screen, #1d2b2a); border-radius:26px / 22px; padding:10px; object-fit:contain;
  box-shadow:0 0 0 12px var(--tv-bezel, #2a2622), 0 0 0 14px #000, inset 0 0 40px rgba(0,0,0,.8), 0 24px 50px rgba(0,0,0,.55); }
.mascot.mf-circle { background:var(--mascot-bg, var(--accent)); border-radius:50%; object-fit:cover; object-position:50% 20%; box-shadow:var(--mascot-shadow, 0 10px 30px rgba(0,0,0,.35)); }
.mascot.mf-glow { filter:drop-shadow(0 0 30px var(--mascot-glow, rgba(255,200,120,.45))); }
.mascot.mf-sticker { filter:drop-shadow(0 0 0 #fff) drop-shadow(5px 0 0 #fff) drop-shadow(-5px 0 0 #fff) drop-shadow(0 5px 0 #fff) drop-shadow(0 -5px 0 #fff) drop-shadow(6px 10px 0 rgba(0,0,0,.25)); }
/* keep bottom-left text clear of the mascot */
#root.has-mascot .s-quote .L-lower, #root.has-mascot .s-title .L-left { padding-left:calc(var(--pad, 140px) + var(--mascot-w, 300px)); }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--style"); ap.add_argument("--aspect"); ap.add_argument("--out")
    ap.add_argument("--lang", help="pick this language from multilingual fields (default meta.lang, else zh)")
    a = ap.parse_args()
    vpath = Path(a.video).resolve()
    video = json.loads(vpath.read_text())
    lang = a.lang or (video.get("meta") or {}).get("lang") or "zh"
    video = delivery.resolve_lang(video, lang)          # {"zh": …, "en": …} anywhere in the file -> one language
    meta = video.setdefault("meta", {})
    meta["lang"] = lang
    sid = a.style or meta.get("style", "ledger")
    style = load_style(sid)
    brand = delivery.apply_brand(style, meta, vpath.parent)
    aefx.apply_style(style)                                               # effects' page themes follow the style's palette
    series = meta.get("series") or {}
    if series.get("opener") and not meta.get("lead"):
        meta["lead"] = float(series.get("opener_dur", 1.8))     # the narration starts after the series card
    aspect = a.aspect or meta.get("aspect", "16:9")
    out = Path(a.out).resolve() if a.out else vpath.parent / "build" / f"{sid}_{aspect.replace(':', 'x')}"
    out.mkdir(parents=True, exist_ok=True)
    X = core.Ctx(video, style, out, vpath.parent, aspect)
    if isinstance(meta.get("music"), str) and meta["music"][:1] in ("$", "~"):      # "$H9_MEDIA/music/…" library paths
        meta["music"] = os.path.expandvars(os.path.expanduser(meta["music"]))
    # measured music beats (meta.music_beats or <music>.beats.json): cuts, sfx and quick-cut runs land on them
    X.music_beats = beatsync.load(meta, vpath.parent)
    X.snapper = beatsync.Snapper(X.music_beats, X.fps) if X.music_beats else None

    # narration + timing
    voice = meta.get("voice")
    if meta.get("words"):
        X.load_words(vpath.parent / meta["words"])
        data = json.loads((vpath.parent / meta["words"]).read_text())
        X._words = [w for x in data for w in (x["words"] if "words" in x else [x])]
    else:
        X._words = []
    # time edits: inserted silences (meta.gaps) and a silent lead-in (meta.lead) move the voice and every cue
    voice_url = X.asset(voice, "audio") if voice else None
    voice_url, lead, _ = pacing.time_edits(X, meta, voice_url)
    D = float(meta.get("duration") or 0) or (lead + probe(out / voice_url) + float(meta.get("tail", 0.6)) if voice else 0)
    beats = video["beats"]
    times = []
    pinned = set()
    for i, b in enumerate(beats):
        t = X.T(b.get("t", 0 if i == 0 else None) if b.get("t") is not None else (times[-1][0] + times[-1][1]))
        d = b.get("d")
        if b.get("fx") == "montage" and not d and (i + 1 == len(beats) or beats[i + 1].get("t") is None):
            # a quick-cut run followed by a chained beat: start it on a beat and make it exactly as long as the run
            if X.snapper and i and b.get("snap") is not False:
                t = X.snapper.snap(t, b.get("t"), f"beat {i} (montage)", times[-1][0] + 4 / X.fps, None, X.snapper.period() * 1.02)
            d = beatsync.run_end(X, b, t) - t
            pinned.add(i)
        times.append([t, d])
    if series.get("opener") and times and times[0][0] < lead:     # the first page starts when the series card ends
        times[0][0] = lead
    if X.snapper:
        beatsync.snap_beats(beats, times, X.snapper, lead if series.get("opener") else 0.0, skip=pinned)
    for i, (t, d) in enumerate(times):
        nxt = times[i + 1][0] if i + 1 < len(times) else D
        times[i][1] = float(d) if d else nxt - t
    if not D: D = times[-1][0] + times[-1][1]
    X.duration = D

    # a "world" style builds the whole film as one continuous set (e.g. the 3D studio); otherwise scene by scene
    X.extra_head = X.extra_body = ""
    world = getattr(style["_mod"], "WORLD", None)
    if world: world(beats, times, X, D)
    prev, mood, spans = None, None, []
    for i, (b, (t, d)) in enumerate(zip(beats, times)):
        if world: break
        # scenes + seams: inside a chapter = (velocity-matched) cut; a new chapter = the style's signature transition
        cid = b.get("id") or X.uid("s")
        X.beat = {"t": t, "d": d, "i": i + int(meta.get("beat_offset", 0)), "n": int(meta.get("beat_total", len(beats)))}   # longform chapters keep global page numbers
        X.beat_marks = marks.build(X, cid, b)
        n_tw, n_audio, n_els = len(X.tws), len(X.audio), len(X.els)
        scene_fn(b["scene"], style)(b, X, t, d, cid)
        mood = b.get("mood", mood) if i else b.get("mood")
        delivery.paint_mood(X, cid, n_els, mood)                          # "mood": "heavy" → the dark token set for this beat
        pacing.rate_adapt(X, b, t, d, cid, n_tw, n_audio, n_els)          # speaking rate sets the tempo (meta.rate_adapt)
        pacing.elastic(X, b, t, d, cid, n_tw, n_audio, n_els, i)     # keep the beat alive / fit a short entrance
        pacing.sound_moments(X, b, t, d, cid)                             # "sfx": sound + visual hit on one frame
        spans.append((cid, t, d, b.get("hold") == "static"))
        if i > 0:
            tr = b.get("tr")
            if isinstance(tr, str) and tr not in ("cut", "hard", "slide", "zoom", "rise", "step", "zoomin", "whip", "spin"): fx.transition(X, t, tr)
            elif b.get("chapter") or tr is True: fx.transition(X, t, None)
            else: fx.cut(X, prev, cid, t, tr if isinstance(tr, str) else None)
        prev = cid
    pacing.breaths(X, spans, D)                                           # a small inhale in each narration pause (meta.breath)
    fit.scope_media(X)                                                    # video wrappers only while their video plays
    if series.get("opener"): delivery.series_opener(X, meta, float(meta.get("lead") or 1.8))
    delivery.ai_label(X, D, meta)
    delivery.logo_mark(X, D, brand)
    fx.overlays(X, D)
    captions.build(X, D, meta.get("caption_fix"), meta.get("caption_len"))
    captions.srt(X, D, out / "captions.srt", meta.get("caption_fix"))

    # mascot (faceless host): a transparent talking video. corner = always on; cameo = only on beats with "host": true + the outro
    if meta.get("mascot"):
        m = style.get("mascot", {})
        url = X.asset(meta["mascot"], "video")
        frame = m.get("frame", "none")
        if m.get("mode", "corner") == "corner":
            wins = [(0.0, D)]
        else:
            wins = [(t, d) for b, (t, d) in zip(beats, times) if b.get("host") or b["scene"] == "outro"]
        src_d = probe(X.out / url) or D
        for k, (a, dur) in enumerate(wins):
            mid = "mascot" if a + dur >= D - 0.01 else f"mascot{k}"
            ms = a % src_d if a + dur <= src_d or src_d <= dur else min(a % src_d, max(0.0, src_d - dur))   # a short talking loop: start inside it
            X.clip(mid, a, dur, "", f"mascot mf-{frame}", 45, track=13 + k % 2, tag="video", attrs=f'src="{url}" muted playsinline data-media-start="{ms:.3f}"')
            if a > 0.01:
                X.tw(f'tl.from("#{mid}", {{scale:0.6, yPercent:20, opacity:0, transformOrigin:"50% 100%", duration:0.45, ease:"back.out(1.7)"}}, {a:.3f});')
                X.sfx(a, "mascot")
        key = "portrait" if X.portrait else "landscape"
        pos = m.get(key, m.get("landscape", {"left": 24, "bottom": 0, "h": 380}))
        X.css("mascot-pos", ".mascot { top:auto; right:auto; left:auto; bottom:auto; " + " ".join(f"{k}:{v}px;" for k, v in pos.items() if k != "h") + f" width:{pos['h']}px; height:{pos['h']}px; }}")

    # audio
    aud = []
    X.music_up = beatsync.up_windows(beats, times, meta) if meta.get("music") else []
    mvol = meta.get("music_volume", 0.12)
    if voice:
        aud.append(f'<audio id="voice" class="clip" src="{voice_url}" data-start="{(f"{lead:.3f}" if lead else "0")}" data-duration="{D - lead:.3f}" data-track-index="40" data-volume="1"></audio>')
    mm = meta.get("music_moods") or {}
    if meta.get("music") and mm and not world:
        # mood changes swap the music bed: one clip per segment, each starting at the same point of its own track, crossfaded
        for k, (m0, m1, md) in enumerate(delivery.mood_segments(beats, times, D)):
            src = mm.get(md, meta["music"])
            url = pacing.duck(X, meta, X.asset(src, "audio"))
            a0, a1 = max(0.0, m0 - (0.4 if k else 0)), min(D, m1 + 0.4)
            aud.append(f'<audio id="music{k}" class="clip" src="{url}" data-start="{a0:.3f}" data-duration="{a1 - a0:.3f}" data-media-start="{a0:.3f}" data-track-index="{41 if k % 2 == 0 else 39}" '
                       f'data-volume="{beatsync.bed_volume(X, mvol)}" data-fade-in="{0.8 if k == 0 else 0.4}" data-fade-out="{2 if a1 >= D - 0.01 else 0.4}"></audio>')
    elif meta.get("music"):
        music_url = pacing.duck(X, meta, X.asset(meta["music"], "audio"))
        aud.append(f'<audio id="music" class="clip" src="{music_url}" data-start="0" data-duration="{D:.3f}" data-track-index="41" data-volume="{beatsync.bed_volume(X, mvol)}" data-fade-in="0.8" data-fade-out="2"></audio>')
    lanes = []   # greedy lane allocation so no two SFX share a track while overlapping
    for i, (t, url, vol) in enumerate(sorted(X.audio)):
        if t >= D - 0.05: continue
        t = max(t, 0); dur = min(probe(out / url) or 1.0, D - t)
        k = next((j for j, end in enumerate(lanes) if end <= t), None)
        if k is None: lanes.append(0); k = len(lanes) - 1
        lanes[k] = t + dur
        aud.append(f'<audio id="fx{i}" class="clip" src="{url}" data-start="{t:.3f}" data-duration="{dur:.3f}" data-track-index="{42 + k}" data-volume="{vol}"></audio>')

    # css: tokens + fonts + base + transitions + scenes + style
    for s in style.get("folio", []): X.used_text.update(s)
    tok = style["tokens"]
    tok_css = ":root { " + " ".join(f"--{k}:{v};" for k, v in tok.items()) + " }"
    font_css = fonts.build(X, "".join(X.used_text))
    base_css = BASE_CSS.replace("{W}", str(X.W)).replace("{H}", str(X.H))
    TW, TH = X.target
    if X.canvas:     # laid out as the base aspect, shown through a window of the target size
        sc, tx, ty = X.canvas
        # the runtime sizes #root and its timed children to the target, so the base-size page lives in an untimed
        # #canvas inside it (timed clips nested in an untimed wrapper keep their own timing); audio stays at the root
        base_css = base_css.replace(f"html, body {{ width:{X.W}px; height:{X.H}px;", f"html, body {{ width:{TW}px; height:{TH}px;")
        base_css = base_css.replace(f"#root {{ position:relative; width:{X.W}px; height:{X.H}px;", f"#root {{ position:relative; width:{TW}px; height:{TH}px;")
        base_css += (f"\n#canvas {{ position:absolute; left:0; top:0; width:{X.W}px; height:{X.H}px; overflow:hidden; background:var(--bg);"
                     f" transform:translate({tx:.2f}px, {ty:.2f}px) scale({sc}); transform-origin:0 0; }}\n")
    if lang in delivery.RTL:     # Arabic / Hebrew lines run right to left (punctuation on the correct side); the layout itself is not mirrored
        base_css += "\n#root :is(h1, h2, h3, p, div, span, b, em, i, li, td, th) { unicode-bidi:plaintext; }\n"
    base_css += "\nsup.ss, sub.ss { font-size:.58em; line-height:0; position:relative; vertical-align:baseline; } sup.ss { top:-.62em; } sub.ss { top:.24em; }\n"
    css = "\n".join([font_css, tok_css, base_css, fx.TR_CSS,
                     *X.css_parts.values(), style.get("css", "")])
    page = f"""<!doctype html>
<html lang="{ {"zh": "zh-CN", "en": "en", "ja": "ja", "ko": "ko"}.get(lang, lang) }"><head><meta charset="UTF-8"><meta name="viewport" content="width={TW}, height={TH}">
<title>{core.esc(meta.get('title', 'hat9'))} · {sid}</title>
<script src="{GSAP}"></script>
{X.extra_head}
<style>{css}</style></head>
<body>
<div id="root" class="{' '.join('st-' + c for c in style['_chain'])} {'v' if X.portrait else 'h'}{' has-mascot' if meta.get('mascot') and style.get('mascot', {}).get('mode', 'corner') == 'corner' else ''}" data-composition-id="main"{' data-motion-blur="on"' if style.get("motion_blur", False) else ''} data-start="0" data-duration="{D:.3f}" data-width="{TW}" data-height="{TH}">
{(f'<div id="canvas">' + chr(10).join(X.els) + '</div>') if X.canvas else chr(10).join(X.els)}
{chr(10).join(aud)}
</div>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(X.tws)}
tl.set({{}}, {{}}, {D:.3f});
window.__timelines["main"] = tl;
</script>
{X.extra_body}
</body></html>
"""
    (out / "index.html").write_text(page)
    (out / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
        "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"}, "media": {"autoProxy": True}}, indent=2))
    (out / "meta.json").write_text(json.dumps({"id": f"hat9-{sid}", "name": f"{meta.get('title', 'hat9')} · {style['name']}"}, ensure_ascii=False))
    (out / "package.json").write_text(json.dumps({"name": f"hat9-{sid}", "private": True, "type": "module"}, indent=2))
    # resolved beat times, for the storyboard check, the stills board and samples (scripts/brief.py, stills.py, sample.py)
    tl_json = {"duration": round(D, 3), "lead": lead, "beats": [
        {"i": i, "t": round(t, 3), "d": round(d, 3), "scene": b.get("scene"), "fx": b.get("fx")} for i, (b, (t, d)) in enumerate(zip(beats, times))]}
    if X.music_beats:      # beat sync: what moved onto the music's beats, and what review.py's av-sync check needs
        beatsync.record(X, tl_json, beats, D)
    (out / "timeline.json").write_text(json.dumps(tl_json, ensure_ascii=False, indent=1))
    print(f"{out}  {TW}x{TH}{f' (laid out as {X.layout})' if X.canvas else ''}  {D:.2f}s  {len(X.els)} clips  {len(X.tws)} tweens  style={sid}")


if __name__ == "__main__":
    main()
