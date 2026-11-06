#!/usr/bin/env python3
"""Craft lint: flag the tells of default "AI" design in a built composition (index.html).

  python3 scripts/craft_lint.py examples/mixue/build/press_16x9        # a build dir or an index.html
  python3 scripts/craft_lint.py examples/*/build/*_16x9 --json         # many at once, machine-readable
  python3 scripts/craft_lint.py BUILD --strict                         # exit 1 when any P0 is found

Rules are adapted for video from OpenDesign's craft/anti-ai-slop.md (itself from refero_skill, MIT),
design-templates/hyperframes/house-style.md, references/typography.md and motion-principles.md (Apache-2.0).
P0 = must fix · P1 = should fix · P2 = worth a look. Python standard library only.
"""
import argparse, colorsys, json, re, sys
from html.parser import HTMLParser
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REG = json.loads((SKILL / "assets" / "fonts.json").read_text())

# Tailwind's default indigo / violet / purple: the textbook "AI accent"
INDIGO = {"#6366f1", "#4f46e5", "#4338ca", "#3730a3", "#8b5cf6", "#7c3aed", "#a855f7"}
# training-data default faces (Latin). CJK families (Noto Sans SC etc.) are exempt: a Chinese video needs them.
BANNED_FONTS = ["Inter", "Roboto", "Open Sans", "Noto Sans", "Arimo", "Lato", "Source Sans", "PT Sans", "Nunito", "Poppins", "Outfit",
                "Sora", "Playfair Display", "Cormorant Garamond", "Bodoni Moda", "EB Garamond", "Cinzel", "Prata", "Syne"]
BANNED_IDS = {"inter", "playfair", "playfair-italic", "eb-garamond", "eb-garamond-italic"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
METRIC = re.compile(r"(\d+(?:\.\d+)?\s*[×xX]\s*(?:faster|better|more|更快|提升|效率))|(99\.9+\s*%)|((?:提升|提高|增长|快了|节省|降低)\s*\d+(?:\.\d+)?\s*(?:%|倍))")
SOURCED = re.compile(r"来源|出处|source|Source|据|报告|公告|年报|10-K|示意|虚构|估算|预测")
FILLER = re.compile(r"lorem ipsum|placeholder text|sample content|feature (?:one|two|three)|示例文字|占位", re.I)
# generic labels a template leaves behind: always generic, or numbered stand-ins ("Step 1") with nothing beside them
GENERIC = re.compile(r"(your (?:text|title|logo|headline) here|click here|text here|lorem(?: ipsum)?|"
                     r"标题文字|这里是标题|这里写标题|正文内容|示例标题|按钮文字|在此输入.*)", re.I)
WEAK = re.compile(r"(title|subtitle|heading|headline|label|text|button|标题|副标题|小标题|正文|按钮|示例)", re.I)
NUMBERED = re.compile(r"(feature|step|item|card|option|section|point|benefit|功能|步骤|特点|要点|卖点|选项|优势)\s*"
                      r"(?:\d{1,2}|[一二三四五六七八九十]|[a-d])", re.I)
FUNCTIONAL = {"#ff5f57", "#febc2e", "#28c840",                                  # window traffic lights
              "#c4291a", "#2457b8", "#127a52", "#8f5600", "#6a3fc0", "#a5305f", "#0f6470", "#4a515c",   # avatar identity tones
              "#1f9d6b"}                                                          # success toast
COL = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)")
PLACEHOLDER_CDN = re.compile(r"unsplash\.com|placehold\.co|picsum\.photos|placekitten\.com|via\.placeholder\.com")


def hue_sat(c):
    """'#abc' / '#aabbcc' / 'rgb(…)' -> (hue°, saturation, lightness) or None."""
    c = c.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if m:
        h = m.group(1)
        if len(h) == 3: h = "".join(x * 2 for x in h)
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    else:
        m = re.fullmatch(r"rgba?\(\s*([\d.]+)[ ,]+([\d.]+)[ ,]+([\d.]+).*\)", c)
        if not m: return None
        r, g, b = (float(x) / 255 for x in m.groups())
    hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
    return hh * 360, ss, ll


class Page(HTMLParser):
    """collects CSS, scripts, and the visible text of every timed clip (text goes to its nearest clip ancestor)."""
    VOID = {"img", "br", "hr", "input", "meta", "link", "source", "track", "wbr", "area", "base", "col", "embed", "param"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.css, self.js, self.inline, self.text, self.srcs = [], [], [], {}, []
        self.stack, self.kids = [], []        # (tag, attrs, clip_id), and child signatures per open element
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("style", "script"): self._in = tag; return
        for k in ("src", "href", "poster"):
            if a.get(k): self.srcs.append(a[k])
        if a.get("style"): self.inline.append((a.get("id", ""), a["style"]))
        clip = a.get("id") if "clip" in (a.get("class") or "").split() else (self.stack[-1][2] if self.stack else "")
        self.classes = getattr(self, "classes", set()); self.classes.update((a.get("class") or "").split())
        self.cls_n = getattr(self, "cls_n", {})
        for c in (a.get("class") or "").split(): self.cls_n[c] = self.cls_n.get(c, 0) + 1
        self.clip_cls = getattr(self, "clip_cls", {})
        cc = self.clip_cls.setdefault(clip or "-", [set(), []])
        cc[0].update((a.get("class") or "").split())
        if a.get("style"): cc[1].append(a["style"])
        if self.kids: self.kids[-1].append((tag, a.get("class", "")))
        if tag in self.VOID: return
        self.stack.append((tag, a, clip)); self.kids.append([])

    def handle_endtag(self, tag):
        if tag in ("style", "script"): self._in = None; return
        if tag in self.VOID or not self.stack: return
        t, a, _ = self.stack.pop(); kids = self.kids.pop()
        self.grids = getattr(self, "grids", [])
        texty = [k for k in kids if k[1] and k[0] in ("div", "li", "article", "section", "figure")]   # cards, not glyph spans
        if len(texty) >= 6 and len({k for k in texty}) == 1:
            self.grids.append((a.get("class", t), len(texty), texty[0][1]))

    def handle_data(self, data):
        if self._in == "style": self.css.append(data); return
        if self._in == "script": self.js.append(data); return
        if data.strip() and self.stack:
            tag, a, clip = self.stack[-1]
            self.text.setdefault(clip or "-", []).append((tag, a.get("class", ""), data.strip()))


def rules(css):
    """yield (selector, body) for every flat rule (good enough for generated CSS)."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        yield m.group(1).strip(), m.group(2)


def lint(index):
    html = Path(index).read_text(encoding="utf-8", errors="replace")
    p = Page(); p.feed(html)
    css = "\n".join(p.css); js = "\n".join(p.js)
    out = []
    add = lambda sev, rule, msg, where="": out.append({"sev": sev, "rule": rule, "msg": msg, "where": where})

    # P0 · default indigo accent
    hexes = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", css + " ".join(s for _, s in p.inline))}
    for h in sorted(hexes & INDIGO): add("P0", "indigo-accent", f"Tailwind 默认靛紫 {h}：AI 设计最典型的标志色，换成风格自己的强调色", h)

    for sel, body in rules(css):
        b = body.lower()
        # P0 · two-stop "trust" gradient (purple→blue, blue→cyan, indigo→pink)
        for g in re.findall(r"(?:linear|radial)-gradient\(([^;]*)\)", b):
            cols = re.findall(r"#[0-9a-f]{3,6}\b|rgba?\([^)]*\)", g)
            hs = [x for x in (hue_sat(c) for c in cols) if x and x[1] > .35 and .15 < x[2] < .85]
            if len(cols) == 2 and len(hs) == 2:
                h1, h2 = sorted((hs[0][0], hs[1][0]))
                purple_blue = (180 <= h1 <= 250 and 255 <= h2 <= 300)
                indigo_pink = (230 <= h1 <= 265 and 300 <= h2 <= 345)
                if purple_blue or indigo_pink:
                    add("P0", "trust-gradient", "紫→蓝 / 蓝→青 / 靛→粉 的两色渐变：换成纯色面 + 有意图的字", sel[:80])
        # P1 · gradient text
        if "background-clip:text" in b.replace(" ", "") and "gradient" in b:
            add("P1", "gradient-text", "渐变字（background-clip:text）：常见的 AI 默认手法，确认它是为内容服务的", sel[:80])
        # P1 · rounded card + coloured left border = the "AI dashboard tile"
        bl = re.search(r"border-left\s*:\s*(\d+(?:\.\d+)?)px\s+solid", b)
        br = re.search(r"border-radius\s*:\s*(\d+(?:\.\d+)?)", b)
        if bl and float(bl.group(1)) >= 2 and br and float(br.group(1)) > 0:
            add("P1", "left-border-card", "圆角卡片 + 彩色左边条：去掉圆角或去掉左边条", sel[:80])
        # P1 · pure black / white grounds on big surfaces
        if re.search(r"(^|[\s,])(:root|body|html|#root|\.scene|\.stage)\b", sel):
            for v in re.findall(r"(?:--bg|background(?:-color)?)\s*:\s*([^;]+)", b):
                if re.fullmatch(r"\s*(#000|#000000|#fff|#ffffff|black|white)\s*", v):
                    add("P2", "pure-ground", f"纯 {v.strip()} 作底：往强调色方向带一点色温", sel[:80])
    for cid, sty in p.inline:
        if re.search(r"background(?:-color)?\s*:\s*(#000|#000000|#fff|#ffffff)\s*(;|$)", sty.lower()):
            add("P2", "pure-ground", "片段内联了纯黑 / 纯白底", cid)

    # P1 · banned "safe" display faces (Latin only)
    m = re.search(r"--f-display\s*:\s*([^;]+);", css)
    if m:
        first = m.group(1).split(",")[0].strip().strip("'\"")
        fid = first[3:] if first.startswith("h9-") else None
        if fid in BANNED_IDS:
            add("P1", "banned-display-font", f"标题字体是 {fid}：训练数据里的默认款，换一款更有性格的（中文部分不受影响）", "--f-display")
    for sel, body in rules(css):
        for fam in re.findall(r"font-family\s*:\s*([^;]+)", body):
            lead = fam.split(",")[0].strip().strip("'\"")
            if lead in BANNED_FONTS and re.search(r"h1|h2|title|ttl|big|display|hl\b", sel):
                add("P1", "banned-display-font", f"标题直接写了 {lead}", sel[:80])

    # visible text checks, per clip
    for cid, items in p.text.items():
        whole = " ".join(t for _, _, t in items)
        if FILLER.search(whole): add("P0", "filler-copy", "占位文案（lorem ipsum / 示例文字）：用真实内容", cid)
        for tag, cls, t in items:
            if EMOJI.search(t) and (tag in ("h1", "h2", "h3", "button", "li") or "icon" in cls or "ico" in cls):
                add("P1", "emoji-icon", f"emoji 当图标用：「{t[:20]}」，换成线性 SVG 图标", cid)
        mm = METRIC.search(whole)
        if mm and not SOURCED.search(whole):
            add("P1", "unsourced-metric", f"「{mm.group(0)}」这类数字没有来源：标出处，或标「示意」", cid)
    for s in p.srcs:
        if PLACEHOLDER_CDN.search(s): add("P1", "placeholder-cdn", f"外链占位图 {s[:60]}", s[:60])

    # P2 · identical card grids
    for cls, n, kid in getattr(p, "grids", []):
        if not re.search(r"dots|cells|mx|wall|tiles|grid|pg|bar|rail|tok|arw|stn", cls + " " + kid):
            add("P2", "identical-cards", f"{n} 个完全一样的卡片排成一格：拉开主次（大小、位置、颜色至少一项）", f".{kid}")

    # motion: durations, ease monoculture, t=0 starts
    tweens = re.findall(r"tl\.(from|to|fromTo)\(\"[^\"]*\",\s*(\{.*?\})(?:,\s*\{(.*?)\})?,\s*([\d.]+)\);", js)
    eases, slow_in, fast, zero = [], 0, 0, 0
    for kind, a1, a2, at in tweens:
        vars_ = a2 if kind == "fromTo" else a1
        d = re.search(r"duration:\s*([\d.]+)", vars_ or "")
        e = re.search(r"ease:\s*\"([^\"]+)\"", vars_ or "")
        dur, ease = (float(d.group(1)) if d else 0.5), (e.group(1) if e else "power1.out")
        if ease == "none" or "repeat" in (vars_ or "") or "keyframes" in (vars_ or ""): continue   # drifts, loops, jolts: by design
        eases.append(ease.split("(")[0])
        if kind in ("from", "fromTo") and dur > 1.2 and "inOut" not in ease: slow_in += 1
        if 0 < dur < 0.12 and not ease.startswith("steps"): fast += 1
        if kind == "from" and float(at) == 0.0: zero += 1
    if slow_in: add("P2", "slow-entrance", f"{slow_in} 个入场超过 1.2 秒：除非是有意的电影感，入场 0.3–0.8 秒更利落")
    if fast: add("P2", "too-fast", f"{fast} 个动作短于 0.12 秒（约 3 帧）：观众看不到它在动")
    if eases:
        top = max(set(eases), key=eases.count)
        share = eases.count(top) / len(eases)
        if share > .7 and len(eases) >= 12:
            add("P2", "ease-monoculture", f"{share:.0%} 的动作都用 {top}：换几种缓动，像换字重一样区分角色")
    if zero: add("P2", "starts-at-zero", f"{zero} 个入场从第 0 帧开始：第一个动作晚 0.1–0.3 秒，开场不会像跳切")
    studio_rules(html, p, css, js, add)
    return out


def _alpha(c):
    a = re.findall(r"[\d.]+", c) if c.startswith("rgba") else []
    return float(a[3]) if len(a) == 4 else 1.0


def _accent_hue(c):
    """hue of a colour that reads as an accent (saturated, mid lightness, mostly opaque), else None."""
    x = hue_sat(c)
    if not x or _alpha(c) < 0.5: return None
    h, s_, l = x
    return h if s_ > 0.45 and 0.25 < l < 0.75 else None


def _hue_d(a, b): return min(abs(a - b), 360 - abs(a - b))


def _opaque_multi(g):
    """a gradient of at least two clearly different, mostly opaque colours (not a scrim or a vignette)."""
    if "transparent" in g or "color-mix" in g: return False      # glows and scrims, not a painted ground
    hs = []
    for c in COL.findall(g):
        if _alpha(c) < 0.6: return False
        x = hue_sat(c.lower())
        if x: hs.append(x)
    return any(abs(hs[i][2] - hs[j][2]) > .12 or (_hue_d(hs[i][0], hs[j][0]) > 30 and min(hs[i][1], hs[j][1]) > .25)
               for i in range(len(hs)) for j in range(i))


def _live(sel, classes):
    """a rule can paint something: every class of the last compound of one of its selectors is in the document."""
    for part in sel.split(","):
        last = re.split(r"[\s>+~]+", part.strip())[-1]
        if all(n in classes for n in re.findall(r"\.([\w-]+)", last)): return True
    return False


def _font_lead(v, tok, depth=0):
    """the registered face (h9-<id>) a font-family value resolves to, following var(--f-*) tokens."""
    v = v.strip()
    m = re.match(r"var\(\s*(--[\w-]+)\s*(?:,\s*(.*))?\)\s*$", v, re.S)
    if m:
        if m.group(1) in tok and depth < 6: return _font_lead(tok[m.group(1)], tok, depth + 1)
        return _font_lead(m.group(2), tok, depth + 1) if m.group(2) else None
    f = v.split(",")[0].strip().strip("'\"")
    return f[3:] if f.startswith("h9-") else None


def _family(fid):
    """the italic of a family counts with it (playfair-italic = playfair); heavy cuts are registered as their own faces."""
    return re.sub(r"-italic$", "", fid)


FONT_MIN = 3     # elements a face must reach to count as "in use" (one-off spice — a single handwritten note — is fine)


def studio_rules(html, p, css, js, add):
    """the "studio rules": one display + one body face, one accent beyond the style's tokens, not everything fading in,
    no centred title on a gradient, no generic labels."""
    classes = getattr(p, "classes", set())
    live = [(sel, body) for sel, body in rules(css) if not sel.startswith("@") and _live(sel, classes)]

    # fonts in use (resolved through the --f-* tokens), grouped by role
    tok = {}
    for sel, body in rules(css):
        for k, v in re.findall(r"(--f-[\w-]+)\s*:\s*([^;]+)", body): tok.setdefault(k, v)
    decls = []                                   # (value, how many elements the rule reaches)
    cls_n = getattr(p, "cls_n", {})
    for sel, body in live:
        last = re.findall(r"\.([\w-]+)", re.split(r"[\s>+~]+", sel.split(",")[0].strip())[-1])
        n = max(1, min((cls_n.get(c, 0) for c in last), default=1))
        decls += [(v, n) for v in re.findall(r"font-family\s*:\s*([^;]+)", body)]
        for v in re.findall(r"(?<![-\w])font\s*:\s*([^;]+)", body):
            m = re.search(r"(var\(.*\)|'[^']+'.*|\"[^\"]+\".*)$", v.strip())
            if m: decls.append((m.group(1), n))
    for _, sty in p.inline: decls += [(v, 1) for v in re.findall(r"font-family\s*:\s*([^;]+)", sty)]
    use = {}
    for d, n in decls:
        f = _font_lead(d, tok)
        if f: use[_family(f)] = use.get(_family(f), 0) + n
    body_f = _family(_font_lead(tok.get("--f-body", ""), tok) or "")
    disp = {"latin": [], "cjk": []}
    sans_body = []
    for fam, n in use.items():
        r = REG.get(fam) or REG.get(fam + "-italic") or {}
        if r.get("cat") == "等宽与像素" or n < FONT_MIN: continue          # code / pixel faces have their own job; one-off spice is fine
        if r.get("cat") == "黑体": sans_body.append(fam)
        if fam == body_f: continue
        disp["latin" if r.get("script") == "latin" else "cjk"].append(fam)
    for script, fams in disp.items():
        if len(fams) > 2:
            add("P1", "font-count", f"{'拉丁' if script == 'latin' else '中文'}标题字体用了 {len(fams)} 款（{'、'.join(sorted(fams))}）："
                "一条片子一款标题字 + 一款正文字（数字 / 代码各可再配一款），多了就像拼凑", script)
    if len(sans_body) > 1:
        add("P1", "font-count", f"正文黑体用了 {len(sans_body)} 款（{'、'.join(sorted(sans_body))}）：正文只留一款", "body")

    # accents beyond the style's tokens (the ones the style declares in --vars, plus the page themes)
    tok_h = [h for v in re.findall(r"--[\w-]+\s*:\s*([^;\"}]+)", css + " " + " ".join(s_ for _, s_ in p.inline))
             for c in COL.findall(v) for h in [_accent_hue(c.lower())] if h is not None]
    extra = {}
    for sel, body in live + [(i, s_) for i, s_ in p.inline]:
        for c in COL.findall(re.sub(r"--[\w-]+\s*:[^;]+;?", "", body)):
            c = c.lower()
            h = _accent_hue(c)
            if h is None or c in FUNCTIONAL or any(_hue_d(h, t) < 25 for t in tok_h): continue
            extra.setdefault(int(((h + 15) % 360) // 30), []).append(c)
    big = sorted((v for v in extra.values() if len(v) >= 3), key=len, reverse=True)
    if len(big) >= 3:
        ex = "、".join(max(set(v), key=v.count) for v in big[:4])
        add("P2", "extra-accent", f"风格配色之外还有 {len(big)} 种强调色在反复出现（{ex}）：一条片子一个强调色，其余用风格自己的颜色", ex)

    # everything fades in: share of entrances that only animate opacity (the beat chrome — captions, footers — is not counted)
    ent = fade = 0
    meta = {"duration", "ease", "stagger", "immediateRender", "delay", "transformOrigin", "overwrite"}
    for m in re.finditer(r'tl\.(from|fromTo)\("([^"]*)",\s*\{', js):
        kind, sel = m.group(1), m.group(2)
        if re.match(r"#s\d+c\b", sel) or ".cap" in sel: continue
        a, e = _obj(js, m.end() - 1)
        A = _keys(a)
        B = A
        if kind == "fromTo":
            nb = js.find("{", e)
            if nb >= 0 and js[e:nb].strip() == ",": B = _keys(_obj(js, nb)[0])
        try: dur = float(B.get("duration", "0.5"))
        except ValueError: dur = 0.5
        if dur < 0.08 or "repeat" in B or "keyframes" in B or A.get("opacity") not in ("0", "0.0"): continue
        ent += 1
        if not (set(A) - meta - {"opacity"}): fade += 1
    if ent >= 10 and fade / ent >= 0.35:
        add("P1" if fade / ent >= 0.5 else "P2", "all-fades", f"{fade}/{ent}（{fade / ent:.0%}）的入场只是透明度淡入：给入场配一个方向、"
            "缩放、遮罩或擦除，淡入只留给需要安静的地方")

    # centred title on a gradient ground (a full-frame layer with a 2-colour gradient + one short centred line)
    full = re.compile(r"inset\s*:\s*0|width\s*:\s*100%[^}]*height\s*:\s*100%|height\s*:\s*100%[^}]*width\s*:\s*100%|width\s*:\s*1[0-9]{3}px")
    grad_cls, center_cls = set(), set()
    for sel, body in live:
        b = body.lower()
        last = set(re.findall(r"\.([\w-]+)", re.split(r"[\s>+~]+", sel.split(",")[-1].strip())[-1]))
        if "gradient" in b and _opaque_multi(b) and (full.search(b) or re.search(r"\b(scene|bg|stage|ground)\b", sel)): grad_cls |= last
        if re.search(r"text-align\s*:\s*center|place-items\s*:\s*center", b) or ("justify-content:center" in b.replace(" ", "") and "align-items:center" in b.replace(" ", "")):
            center_cls |= last
    for cid, (cls, stys) in getattr(p, "clip_cls", {}).items():
        sty = " ".join(stys).lower()
        g = bool(cls & grad_cls) or ("gradient" in sty and _opaque_multi(sty) and bool(full.search(sty)))
        c = bool(cls & center_cls) or "text-align:center" in sty.replace(" ", "")
        items = [t for _, _, t in p.text.get(cid, [])]
        if g and c and 1 <= len(items) <= 3 and max(len(t) for t in items) <= 40:
            add("P1", "gradient-title", "渐变底 + 居中一行标题：最典型的 AI 片头；换成纯色面 / 真实画面，标题贴边放", cid)

    # generic placeholder labels
    for cid, items in p.text.items():
        texts = [t.strip() for _, _, t in items if t.strip()]
        real = [t for t in texts if not (GENERIC.fullmatch(t) or WEAK.fullmatch(t) or NUMBERED.fullmatch(t)) and len(t) > 2]
        for t in texts:       # "标题" next to its value is a form label; alone it is a template leftover
            if GENERIC.fullmatch(t) or ((NUMBERED.fullmatch(t) or WEAK.fullmatch(t)) and len(real) < 2):
                add("P1", "generic-label", f"「{t}」是模板占位标签：写成这一屏真正的内容", cid)
                break


def _obj(s, i):
    """s[i] == '{' -> (the text inside the braces, index after the closing brace)."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{": depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0: return s[i + 1:j], j + 1
    return s[i + 1:], len(s)


def _keys(o):
    """top-level keys of a GSAP vars object written as JS -> {key: raw value}."""
    out, depth, cur, parts = {}, 0, "", []
    for ch in o:
        if ch in "{[(": depth += 1
        if ch in "}])": depth -= 1
        if ch == "," and depth == 0: parts.append(cur); cur = ""
        else: cur += ch
    parts.append(cur)
    for part in parts:
        if ":" in part:
            k, v = part.split(":", 1); out[k.strip().strip('"')] = v.strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+"); ap.add_argument("--json", action="store_true"); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    report, p0 = {}, 0
    for raw in a.paths:
        f = Path(raw); f = f / "index.html" if f.is_dir() else f
        if not f.exists(): print(f"  ! no index.html at {raw}", file=sys.stderr); continue
        found = lint(f); report[str(f)] = found
        p0 += sum(x["sev"] == "P0" for x in found)
    if a.json: print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        for f, found in report.items():
            counts = {s: sum(x["sev"] == s for x in found) for s in ("P0", "P1", "P2")}
            print(f"== {f}  P0 {counts['P0']} · P1 {counts['P1']} · P2 {counts['P2']}")
            for x in sorted(found, key=lambda x: x["sev"]):
                print(f"  {x['sev']} {x['rule']:<20} {x['msg']}" + (f"  [{x['where']}]" if x["where"] else ""))
    if a.strict and p0: raise SystemExit(1)


if __name__ == "__main__":
    main()
