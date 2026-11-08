#!/usr/bin/env python3
"""Font specimens for gallery/fonts.html: one PNG per registered font + the page's data block.

  H9_MEDIA=~/your/media/library python3 assets/previews/fonts/make_specimens.py

Fonts are looked up the same way the build does (scripts/h9/fonts.py). A font that is not installed gets a
"可选 · 未安装" card instead of a sample, so the page always lists every id in assets/fonts.json.
"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SKILL = HERE.parents[2]
sys.path.insert(0, str(SKILL / "scripts"))
from h9 import fonts  # noqa: E402

W, H = 1200, 300
BG, CARD, INK, DIM, HOT, RULE = (17, 17, 16), (25, 24, 23), (239, 233, 223), (149, 143, 133), (255, 106, 43), (42, 40, 38)
SAMPLE = {
    "sc": "一条口播，变成动效成片",
    "tc": "一條口播，變成動效成片",
    "jp": "ひとつの語りを、動くフィルムに",
    "kr": "한 편의 내레이션을 모션 영상으로",
    "latin": "One voiceover, one finished motion film.",
    "arabic": "الجميع يستخدم الذكاء الاصطناعي",
    "hebrew": "כולם משתמשים בבינה מלאכותית",
}
SAMPLE_ID = {   # a few faces read better with their own line
    "press-start-2p": "PRESS START  LEVEL 07",
    "vt323": "$ hat9 render work/video.json --aspect 9:16",
    "jetbrains-mono": "hat9 quick \"一段文案\" --aspect 9:16",
    "ibm-plex-mono": "SOURCE: 2024 ANNUAL RESULTS  p.47",
    "space-mono": "SOURCE: 2024 ANNUAL RESULTS  p.47",
    "courier-prime": "INT. NIGHT — THE LEDGER, PAGE 47",
    "special-elite": "CASE FILE No. 2024-07 — CONFIDENTIAL",
    "unifraktur": "The Daily Ledger",
    "bebas": "ONE VOICEOVER",
    "anton": "ONE VOICEOVER",
    "oswald": "MOTION FILM · 46,479",
    "barlow-cond": "46,479  STORES  +39.8%",
    "barlow-cond-black": "46,479  STORES  +39.8%",
    "ma-shan-zheng": "一条口播，十种写法",
    "zhi-mang-xing": "一条口播，十种写法",
    "liu-jian-mao-cao": "一条口播，十种写法",
}


def ui(size, bold=False):
    p = fonts.find("NotoSansSC-VF.ttf")
    f = ImageFont.truetype(str(p), size)
    try: f.set_variation_by_axes([700 if bold else 400])
    except Exception: pass
    return f


def mono(size):
    return ImageFont.truetype(str(fonts.find("JetBrainsMono[wght].ttf")), size)


def axes_of(f):
    try: return f.get_variation_axes()
    except Exception: return []


def set_weight(f, wght):
    ax = axes_of(f)
    if not ax: return False
    vals = []
    for a in ax:
        name = a.get("name", b"")
        name = name.decode() if isinstance(name, bytes) else str(name)
        if name.lower().startswith("weight") or name.lower() == "wght":
            vals.append(max(a["minimum"], min(a["maximum"], wght)))
        else:
            vals.append(a.get("default", a["minimum"]))
    try:
        f.set_variation_by_axes(vals); return True
    except Exception:
        return False


def weight_range(f):
    for a in axes_of(f):
        name = a.get("name", b"")
        name = name.decode() if isinstance(name, bytes) else str(name)
        if name.lower().startswith("weight") or name.lower() == "wght":
            return int(a["minimum"]), int(a["maximum"])
    return None


def fit(path, text, maxw, maxh, start=96):
    size = start
    while size > 18:
        f = ImageFont.truetype(str(path), size)
        x0, y0, x1, y1 = f.getbbox(text)
        if x1 - x0 <= maxw and y1 - y0 <= maxh: return f, size
        size -= 2
    return ImageFont.truetype(str(path), size), size


def card(fid, meta, out):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([8, 8, W - 8, H - 8], radius=16, fill=CARD)
    d.text((40, 30), fid, font=mono(24), fill=HOT)
    tag = f"{meta.get('cat', '')} · {meta.get('role', '')}"
    d.text((40, 64), tag, font=ui(20), fill=DIM)
    lic = meta.get("license", "")
    lic_short = "OFL" if lic.startswith("OFL") else ("Apache" if lic.startswith("Apache") else ("IPA" if lic.startswith("IPA") else "免费商用"))
    lw = d.textlength(lic_short, font=ui(18, True))
    d.rounded_rectangle([W - 60 - lw - 24, 30, W - 60, 62], radius=14, outline=RULE, width=2)
    d.text((W - 60 - lw - 12, 34), lic_short, font=ui(18, True), fill=INK if lic_short != "免费商用" else (240, 190, 80))
    path = fonts.find(meta["file"])
    script = meta.get("script", "latin")
    if not path:
        d.text((40, 130), "可选字体 · 本机未安装", font=ui(40, True), fill=INK)
        d.text((40, 190), (meta.get("url") or "")[:90], font=mono(18), fill=DIM)
        im.save(out, optimize=True); return {"installed": False, "weights": None}
    text = SAMPLE_ID.get(fid, SAMPLE.get(script, SAMPLE["latin"]))
    f, size = fit(path, text, W - 80, 120)
    wr = weight_range(f)
    if wr: set_weight(f, min(wr[1], 800) if wr[1] >= 700 else wr[1])
    d.text((40, 110), text, font=f, fill=INK)
    if wr and wr[1] - wr[0] >= 300:
        y = 238
        x = 40
        for w in sorted({wr[0], (wr[0] + wr[1]) // 2 // 100 * 100, wr[1]}):
            g = ImageFont.truetype(str(path), 30); set_weight(g, w)
            short = "字重 永" if script in ("sc", "tc") else "Aa 01"
            d.text((x, y), f"{w}", font=mono(16), fill=DIM)
            d.text((x + 48, y - 8), short, font=g, fill=INK)
            x += 200
    im.save(out, optimize=True)
    return {"installed": True, "weights": list(wr) if wr else None}


def main():
    reg = json.loads((SKILL / "assets" / "fonts.json").read_text())
    rows = []
    for fid, meta in reg.items():
        info = card(fid, meta, HERE / f"{fid}.png")
        rows.append({"id": fid, "cat": meta.get("cat", ""), "role": meta.get("role", ""), "mood": meta.get("mood", []), "script": meta.get("script", ""),
                     "license": meta.get("license", ""), "redistribute": meta.get("redistribute", True), "url": meta.get("url", ""),
                     "installed": info["installed"], "weights": info["weights"]})
    page = SKILL / "gallery" / "fonts.html"
    if page.exists():
        s = page.read_text()
        s = re.sub(r"(<script id=\"font-data\" type=\"application/json\">).*?(</script>)", lambda m: m.group(1) + json.dumps(rows, ensure_ascii=False) + m.group(2), s, flags=re.S)
        page.write_text(s)
    print(len(rows), "fonts,", sum(r["installed"] for r in rows), "installed")


if __name__ == "__main__":
    main()
