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
