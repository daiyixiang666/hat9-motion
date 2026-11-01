"""九帽动效 core: the build context every scene and style talks to.

A beat is a dict from video.json; a scene turns it into HyperFrames clips (HTML) plus GSAP lines
on ONE paused master timeline with absolute times. Nothing here depends on a browser.
"""
import html, json, math, random, re, shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]

ASPECTS = {"16:9": (1920, 1080), "9:16": (1080, 1920), "1:1": (1080, 1080), "4:3": (1440, 1080), "3:4": (1080, 1440), "4:5": (1080, 1350)}
# aspects without layouts of their own are laid out as a base aspect and shown through a window (scale, top of the
# window in base px): every style keeps working. 9:16 content lives in y 170–1520 (clear of the platform chrome), so
# 4:5 and 3:4 show that band at full size and 1:1 shows it at 0.8 with the ground colour at the sides; 4:3 letterboxes 16:9.
# meta.canvas = false lays the page out at the real size instead (only for styles that handle it themselves).
CANVAS = {"1:1": ("9:16", 0.8, 170), "4:5": ("9:16", 1.0, 170), "3:4": ("9:16", 1.0, 140), "4:3": ("16:9", 0.75, None)}
RTL_RX = re.compile(r"[\u0590-\u08ff\ufb1d-\ufdff\ufe70-\ufeff]")    # Hebrew / Arabic: animated as whole runs, never glyph by glyph
VENDOR = SKILL / "assets" / "vendor"   # optional local copies of render-time JS (d3, topojson) for offline builds

# entrance verbs: GSAP "from" vars (+ default ease).  manim-style names where they exist.
VERBS = {
    "rise":   ("{y:44, opacity:0}", "power3.out"),
    "fade":   ("{opacity:0}", "power2.out"),
    "slam":   ("{scale:1.9, opacity:0}", "expo.out"),
    "pop":    ("{scale:0, opacity:0}", "back.out(2.2)"),
    "blur":   ("{opacity:0, scale:1.06, filter:'blur(18px)'}", "power3.out"),
    "ink":    ("{opacity:0, scale:1.12, filter:'blur(26px)'}", "sine.out"),
    "drop":   ("{y:-140, opacity:0}", "bounce.out"),
    "jitter": ("{y:36, rotation:-5, opacity:0}", "steps(4)"),
    "flip":   ("{rotationX:-95, opacity:0, transformOrigin:'50% 100%'}", "back.out(1.4)"),
    "left":   ("{x:-90, opacity:0}", "expo.out"),
    "right":  ("{x:90, opacity:0}", "expo.out"),
    "zoom":   ("{scale:0.7, opacity:0}", "expo.out"),
    "type":   ("{opacity:0}", "none"),
    "lift":   ("{yPercent:115}", "expo.out"),          # inside an overflow-clipped line = line-mask reveal
    "blurin": ("{opacity:0, filter:'blur(8px)'}", "power2.out"),
}
# clip-path verbs need fromTo
CLIPS = {
    "mask":  ("inset(0 0 100% 0)", "inset(0 0 0% 0)"),
    "wipe":  ("inset(0 100% 0 0)", "inset(0 0% 0 0)"),
    "unveil": ("inset(50% 0 50% 0)", "inset(0% 0 0% 0)"),
    "iris":  ("circle(0% at 50% 50%)", "circle(75% at 50% 50%)"),
}


def esc(s): return html.escape(str(s), quote=True)


class Cue(float):
    """a time that came from the narration ("@词"): entrances aimed at it land ON the word, not after it."""


# fraction of a tween's duration at which it is 90% there (perceived landing), per ease
P90 = {"expo.out": .33, "power4.out": .37, "power3.out": .44, "power2.out": .54, "power1.out": .68, "sine.out": .71, "none": 1.0}


def words(text):
    """Chinese word segmentation (jieba if installed; otherwise 2-glyph chunks), Latin runs kept whole."""
    try:
        import jieba
        return list(jieba.cut(text))
    except ImportError:
        return re.findall(r"[A-Za-z0-9%.]+|\s+|[^A-Za-z0-9%.\s]{1,2}", text)


class Ctx:
    def __init__(self, video, style, out, src_dir, aspect=None):
        self.v, self.S, self.out, self.src = video, style, Path(out), Path(src_dir)
        meta = video.get("meta", {})
        self.aspect = aspect or meta.get("aspect", "16:9")
        if self.aspect not in ASPECTS: raise SystemExit(f"unknown aspect {self.aspect!r}; have: {', '.join(ASPECTS)}")
        self.target = ASPECTS[self.aspect]          # the size of the video file
        self.canvas = None                          # (scale, tx, ty) when laid out as a base aspect behind a window
        base = self.aspect
        if self.aspect in CANVAS and meta.get("canvas", True) is not False:
            base, sc, y0 = CANVAS[self.aspect]
            bw, bh = ASPECTS[base]; tw, th = self.target
            ty = (th - bh * sc) / 2 if y0 is None else -y0 * sc
            self.canvas = (sc, (tw - bw * sc) / 2, ty)
        self.layout = base
        self.W, self.H = ASPECTS[base]
        self.portrait = self.H > self.W
        self.fps = meta.get("fps", 30)
        self.M = {"ease": "expo.out", "dur": 0.6, "stagger": 0.06, "text": "rise", "heading": "rise",
                  "media": "fade", "accent": "pop", "camera": "push", "transition": "dip", "exit": 0.0,
                  "em": "marker", **style.get("motion", {})}
        self.els, self.tws, self.css_parts, self.audio = [], [], {}, []
        self._ids = {}
        self.chars = []
        self.duration = float(meta.get("duration", 0) or 0)
        self.rand = random.Random(meta.get("seed", 9))
        self.used_text = set()

    # ---------------- time
    def load_words(self, path):
        """words.json = [{w,s,e}] (or segments with words). Flattened to per-character times."""
        data = json.loads(Path(path).read_text())
        words = []
        for x in data:
            if "words" in x: words += x["words"]
            else: words.append(x)
        for w in words:
            tok = str(w["w"]).strip(); k = max(len(tok), 1)
            for j, ch in enumerate(tok):
                self.chars.append((ch, w["s"] + (w["e"] - w["s"]) * j / k, w["s"] + (w["e"] - w["s"]) * (j + 1) / k))
        self.text = "".join(c[0] for c in self.chars)
        return self.chars

    def T(self, x, after=0.0):
        """number -> seconds;  "@词" -> when 词 starts (first hit after `after`);  "@词$" -> when it ends;  "@词+0.3"."""
        if x is None: return None
        if isinstance(x, (int, float)): return float(x)
        m = re.fullmatch(r"@(.+?)(\$)?([+-][\d.]+)?", str(x).strip())
        if not m: return float(x)
        word, end, off = m.group(1), m.group(2), float(m.group(3) or 0)
        if not self.chars: raise SystemExit(f"cue {x!r} needs meta.words (word timestamps)")
        i = -1
        while True:
            i = self.text.find(word, i + 1)
            if i < 0: raise SystemExit(f"cue {x!r}: '{word}' not found in narration text:\n{self.text}")
            if self.chars[i][1] >= after - 0.05: break
        t = self.chars[i + len(word) - 1][2] if end else self.chars[i][1]
        return Cue(round(t + off, 3))

    def speaker_at(self, t):
        """who is speaking at t (words may carry "spk"; meta.speakers names them) — a layout hint for dialogue scenes,
        e.g. put the visual on the side opposite the speaker's caption. None when unknown."""
        for w in getattr(self, "_words", []):
            if w.get("spk") is not None and w["s"] - 0.05 <= t <= w["e"] + 0.3: return w["spk"]
        return None

    # ---------------- output pieces
    def uid(self, p):
        self._ids[p] = self._ids.get(p, 0) + 1
        return f"{p}{self._ids[p]}"

    def clip(self, cid, t, d, inner, cls="", z=2, track=1, tag="div", attrs="", sty=""):
        if cls.startswith("ov-") or cls.startswith("tr-"): attrs += ' data-motion-blur="off"'   # texture jumps are not motion
        if "scene" in cls.split():
            inner = f'<div class="stage">{inner}{getattr(self, "beat_marks", "")}</div>'; self.beat_marks = ""
        self.els.append(f'<{tag} id="{cid}" class="clip {cls}" data-start="{t:.3f}" data-duration="{max(d, 0.05):.3f}" '
                        f'data-track-index="{track}" style="z-index:{z};{sty}" {attrs}>{inner}</{tag}>')

    def tw(self, line): self.tws.append(line)

    def geo_scripts(self):
        """<script> tags for d3-geo + topojson-client: the vendored copies (offline-safe) or the CDN."""
        if all((VENDOR / f).exists() for f in ("d3-array.min.js", "d3-geo.min.js", "topojson-client.min.js")):
            return "".join(f'<script src="{self.asset(VENDOR / f, "vendor")}"></script>' for f in ("d3-array.min.js", "d3-geo.min.js", "topojson-client.min.js"))
        if self.v.get("meta", {}).get("offline"): raise SystemExit("offline build: assets/vendor/{d3-array,d3-geo,topojson-client}.min.js missing")
        return ('<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'
                '<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>')

    def vendor_js(self, file, cdn):
        """a render-time library: the local copy under assets/vendor/<file> when present (copied into the build), else
        the CDN url. meta.offline = true makes a missing local copy an error instead of a silent CDN fallback."""
        p = VENDOR / file
        if p.exists(): return self.asset(p, "vendor")
        if self.v.get("meta", {}).get("offline"): raise SystemExit(f"offline build: assets/vendor/{file} missing (run: python3 scripts/hat9.py vendor)")
        return cdn

    def css(self, key, text):
        if key not in self.css_parts: self.css_parts[key] = text

    def asset(self, rel, sub="img"):
        """copy a source file into the project, return its project-relative url."""
        if rel is None: return None
        p = Path(rel)
        if not p.is_absolute(): p = (self.src / rel)
        if not p.exists(): raise SystemExit(f"missing asset: {p}")
        dst = self.out / "assets" / sub / p.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_mtime < p.stat().st_mtime: shutil.copy2(p, dst)
        return f"assets/{sub}/{p.name}"

    def sfx(self, t, role, vol=None):
        """role = a style SFX role (enter/hit/transition/type/pop...) or a file name in assets/sfx."""
        if t is None: return
        spec = self.S.get("sfx", {}).get(role, role)
        if not spec: return
        name, v = (spec if isinstance(spec, (list, tuple)) else (spec, 0.5))
        src = SKILL / "assets" / "sfx" / f"{name}.wav"
        if not src.exists(): return
        url = self.asset(src, "sfx")
        self.audio.append((t, url, vol if vol is not None else v))

    # ---------------- text
    def rich(self, s, split=None):
        """escape, *强调* -> <em>, | -> line break; split='chars' wraps every glyph in <i class="c"> for staggers."""
        s = str(s)
        self.used_text.update(re.sub(r"[\^_]\{|\}", "", s))
        if split in ("chars", "words") and RTL_RX.search(s): split = "runs"     # Arabic / Hebrew: split glyphs would lose their joins and order
        out, em = [], False
        for part in re.split(r"(\*|\||\^\{[^}]*\}|_\{[^}]*\})", s):
            if part == "*": out.append("<em class=\"em\"><span class=\"emt\">" if not em else "</span><i class=\"emb\"></i></em>"); em = not em; continue
            if part == "|": out.append("<br>"); continue
            if part[:2] in ("^{", "_{") and part.endswith("}"):     # x^{2} · H_{2}O · CO_{2}: superscript / subscript
                tag = "sup" if part[0] == "^" else "sub"
                inner = f'<{tag} class="ss">{esc(part[2:-1])}</{tag}>'
                out.append(f'<i class="c">{inner}</i>' if split in ("chars", "words", "runs") else inner); continue
            if split == "chars":
                out.append("".join(f'<i class="c">{esc(ch)}</i>' if ch.strip() else " " for ch in part))
            elif split == "runs":
                out.append(f'<i class="c">{esc(part)}</i>' if part.strip() else esc(part))
            elif split == "words":
                out.append("".join(f'<i class="c">{esc(w)}</i>' if w.strip() else " " for w in words(part)))
            else:
                out.append(esc(part))
        if em: out.append("</span><i class=\"emb\"></i></em>")
        return "".join(out)

    # ---------------- motion
    def enter(self, sel, t, role="text", verb=None, dur=None, stagger=None, ease=None, extra=""):
        if t is None: return
        verb = verb or self.M.get(role, "rise")
        dur = dur if dur is not None else self.M["dur"]
        st = self.M["stagger"] if stagger is None else stagger
        if verb == "none": return
        if isinstance(t, Cue):   # land on the word: start = word − p90·dur − 2 frames (ITU-R BT.1359: picture early is invisible)
            e = ease or VERBS.get(verb, (None, self.M["ease"]))[1]
            e = self.M["ease"] if e in ("expo.out", "power3.out") else e
            t = max(getattr(self, "beat", {}).get("t", 0), t - P90.get(e, .45) * dur - 2 / self.fps)
        if verb == "type":
            self.tw(f'tl.from("{sel}", {{opacity:0, duration:0.01, stagger:{st or 0.045}, ease:"none"}}, {t:.3f});'); return
        if verb in CLIPS:
            a, b = CLIPS[verb]
            self.tw(f'tl.fromTo("{sel}", {{clipPath:"{a}"}}, {{clipPath:"{b}", duration:{dur:.2f}, ease:"{ease or "power3.inOut"}", stagger:{st}{extra}}}, {t:.3f});'); return
        frm, e0 = VERBS.get(verb, VERBS["rise"])
        e = ease or (self.M["ease"] if e0 in ("expo.out", "power3.out") else e0)
        self.tw(f'tl.from("{sel}", {{...{frm}, duration:{dur:.2f}, ease:"{e}", stagger:{st}{extra}}}, {t:.3f});')

    def emph(self, sel, t):
        """animate the *强调* marks inside sel, in this style's way."""
        if t is None: return
        k = self.M["em"]
        if k == "marker": self.tw(f'tl.fromTo("{sel} .emb", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"power3.out", stagger:0.1}}, {t:.3f});')
        elif k == "underline": self.tw(f'tl.fromTo("{sel} .emb", {{scaleX:0}}, {{scaleX:1, duration:0.5, ease:"power2.inOut", stagger:0.1}}, {t:.3f});')
        elif k == "color": self.tw(f'tl.from("{sel} .emt", {{color:"inherit", duration:0.3, stagger:0.1}}, {t:.3f});')
        elif k == "box": self.tw(f'tl.fromTo("{sel} .emb", {{scale:0}}, {{scale:1, duration:0.35, ease:"back.out(2)", stagger:0.1}}, {t:.3f});')
        elif k == "circle": self.tw(f'tl.fromTo("{sel} .emb", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"power2.inOut", stagger:0.1}}, {t:.3f});')
        elif k == "glow": self.tw(f'tl.from("{sel} .emt", {{textShadow:"0 0 0px rgba(0,0,0,0)", color:"inherit", duration:0.6, stagger:0.1}}, {t:.3f});')

    def camera(self, sel, t, d, kind=None):
        kind = kind or self.M["camera"]
        if kind == "push": self.tw(f'tl.fromTo("{sel}", {{scale:1.0}}, {{scale:1.06, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        elif kind == "pull": self.tw(f'tl.fromTo("{sel}", {{scale:1.08}}, {{scale:1.0, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        elif kind == "drift": self.tw(f'tl.fromTo("{sel}", {{xPercent:-1.5, scale:1.04}}, {{xPercent:1.5, scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.3f});')
        elif kind == "handheld":
            self.tw(f'tl.set("{sel}", {{scale:1.05}}, {t:.3f});')
            k = max(2, int(d / 0.9))
            for i in range(k):
                x, y, r = self.rand.uniform(-9, 9), self.rand.uniform(-6, 6), self.rand.uniform(-0.35, 0.35)
                self.tw(f'tl.to("{sel}", {{x:{x:.1f}, y:{y:.1f}, rotation:{r:.2f}, duration:{d / k:.2f}, ease:"sine.inOut"}}, {t + i * d / k:.3f});')
        elif kind == "dolly": self.tw(f'tl.fromTo("{sel}", {{rotationY:-8, scale:0.98}}, {{rotationY:6, scale:1.04, duration:{d:.2f}, ease:"power1.inOut"}}, {t:.3f});')
        elif kind == "stop":  # stop-motion: tiny stepped wobble
            k = max(2, int(d / 0.25))
            for i in range(k):
                self.tw(f'tl.set("{sel}", {{x:{self.rand.uniform(-3, 3):.1f}, y:{self.rand.uniform(-3, 3):.1f}, rotation:{self.rand.uniform(-0.4, 0.4):.2f}}}, {t + i * d / k:.3f});')
