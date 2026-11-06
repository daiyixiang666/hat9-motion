#!/usr/bin/env python3
"""A product URL -> its REAL interface, cut into components you can animate (never invent UI).

  python3 scripts/ui_capture.py <url> --auto [--out work/ui]                    # hero, nav, CTA, cards, pricing, form, code, table
  python3 scripts/ui_capture.py <url> --pick ".pricing" --pick "form#signup"    # exactly these elements (CSS selectors)
      [--aspect 9:16] [--video-dir work] [--mobile] [--width 1280] [--dark] [--max 8] [--page-width 1600]
  --aspect 9:16 captures the mobile layout (390 CSS px) so page text stays readable on a phone, and emits portrait beats
  -> work/ui/ui-page.jpg + .json       the page for context, ≤ --page-width px wide (the .json = the sidecar scroll_shot reads)
     work/ui/ui-screen.jpg             its first screen, cut to one frame's shape (for spotlight)
     work/ui/ui-01-hero.png …          one tight 2x capture per component (big photographic ones as .jpg)
     (files are prefixed with the --out folder's name, so captures of two sites can share one video)
     work/ui/ui.json                   per component: file, kind, selector, box (page CSS px) and box_px (page image px), size,
                                       visible text, its clickable children (hot, in capture px) and dominant colours
     work/ui/beats.json                ready-to-paste video.json beats that only use those files (write the `line`s);
                                       paths are relative to --video-dir (the folder of video.json; default: the parent of --out)

Uses scripts/webpage.mjs (the Chrome + puppeteer-core that HyperFrames installs). Loads the page read-only: nothing is
clicked, typed, submitted or logged into. Beats reference captured files only, and every label is text from the page.
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIND_ZH = {"hero": "首屏", "nav": "导航", "cta": "按钮", "cards": "卡片组", "card": "卡片", "pricing": "价格表", "plan": "套餐",
           "form": "表单", "code": "代码块", "table": "表格", "pick": "组件"}


def colours(png, n=4):
    """dominant colours of a capture: [{hex, share}] (largest first), from a small quantised copy."""
    from PIL import Image
    with Image.open(png) as im:
        im = im.convert("RGB")
        im.thumbnail((160, 160))
        q = im.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()
        counts = sorted(q.getcolors(), reverse=True)
        total = sum(c for c, _ in counts)
    out = []
    for c, idx in counts[:n]:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        out.append({"hex": f"#{r:02x}{g:02x}{b:02x}", "share": round(c / total, 3)})
    return out


EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002190-\U000027BF\U0000FE0F\U00002B00-\U00002BFF]")


def short(s, n=16):
    s = " ".join(EMOJI.sub("", str(s)).split())
    first = s.split(" ")[0]
    if len(s) > n and 2 <= len(first) <= n: return first          # a card's title, not its whole text
    return s if len(s) <= n else s[:n - 1] + "…"


def capture(a, out):
    opts = {"url": a.url, "out": str(out), "picks": a.pick, "auto": a.auto or not a.pick, "width": a.width or None,
            "scale": 2, "mobile": a.mobile, "dark": a.dark, "wait": a.wait, "max": a.max, "maxHeight": a.max_height}
    js = f"import({json.dumps((HERE / 'webpage.mjs').as_uri())}).then((m) => m.captureUI(JSON.parse(process.argv[1])))" \
         ".then(() => process.exit(0), (e) => { console.error(String(e && e.message || e)); process.exit(1); })"
    r = subprocess.run(["node", "-e", js, json.dumps(opts)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ui_capture: could not capture {a.url}\n{r.stderr.strip()[-1500:]}")
    return json.loads((out / "raw.json").read_text())


def beats_for(comps, raw, url, portrait, rel):
    """beats in existing effects (plus ui_lift), each only pointing at captured files; rel(name) -> path for video.json.
    9:16 beats keep page text readable on a phone (≥ ~36 px at 1080 wide): the page is a mobile-width capture shown at full
    frame width, components fill the width, and nothing shows a whole desktop page shrunk to fit."""
    host = url.split("://", 1)[-1].rstrip("/")
    tab = short(raw.get("title", ""), 30)
    frame = "browser"
    beats = []
    page_h = raw["page_h"]
    narrow = raw["width"] <= 520                               # a mobile-width page: readable at full frame width in 9:16
    on_page = [c for c in comps if c["box_px"][1] + c["box_px"][3] <= page_h]      # inside the part the page image kept
    rank = {"pick": 0, "hero": 1, "card": 2, "plan": 2, "form": 3, "cards": 4, "pricing": 4, "code": 5, "table": 5, "cta": 6, "nav": 7}
    lift = sorted([c for c in on_page if not (c["kind"] == "hero" and c.get("region")) and c["kind"] != "nav"],
                  key=lambda c: rank.get(c["kind"], 9))
    if portrait:      # a lifted piece fills ~92 % of 1080: keep the ones whose text stays big (≤ ~420 CSS px wide) and not too tall
        lift = [c for c in lift if c["box"]["w"] <= 440 and c["box"]["h"] <= c["box"]["w"] * 1.0] or lift
    hero = lift[0] if lift else None
    demo = [c for c in comps if (c["hot"] or c["tag"] in ("a", "button")) and (not portrait or c["box"]["w"] <= 440)]

    def path_of(c, n=3):
        if not c["hot"]:                                       # the component is itself the link: hover it
            return [{"act": "hover", "x": 0.5, "y": 0.5, "label": short(c["head"] or c["text"], 14)}]
        hot = sorted(c["hot"], key=lambda h: (h["y"] // 40, h["x"]))
        seen, path = set(), []
        for h in hot:
            if h["text"] in seen or h["w"] * h["h"] < 200: continue
            seen.add(h["text"])
            path.append({"act": "click" if h["tag"] in ("button", "input", "select", "summary") or len(path) == n - 1 else "hover",
                         "x": round(h["x"] + h["w"] / 2), "y": round(h["y"] + h["h"] / 2), "label": short(h["text"], 14)})
        return path[:n]

    # 1 · the main component lifts out of its page and gets demoed
    if hero:
        beats.append({"scene": "fx", "fx": "ui_lift", "image": rel(raw["page"]), "box": hero["box_px"], "piece": rel(hero["file"]),
                      "url": host, "tab": tab, "frame": frame, "path": path_of(hero, 2 if portrait else 3), "line": "（写这一句口播）", "src": url})
    # 2 · the page scrolls to each component and boxes it (scroll_shot reads page.json beside the page image);
    #     9:16 only when the page is mobile-width — a desktop page would be unreadable — else a second component lifts out
    inside = lambda a, b: a[0] >= b[0] - 4 and a[1] >= b[1] - 4 and a[0] + a[2] <= b[0] + b[2] + 4 and a[1] + a[3] <= b[1] + b[3] + 4
    stops = []
    for c in sorted((c for c in on_page if c["kind"] != "nav"), key=lambda c: c["box_px"][1]):
        if any(inside(c["box_px"], st["box"]) or inside(st["box"], c["box_px"]) for st in stops): continue
        stops.append({"box": c["box_px"], "label": short(c["head"] or c["text"], 14)})
    stops = stops[:3 if portrait else 4]
    if stops and (narrow or not portrait):
        b = {"scene": "fx", "fx": "scroll_shot", "image": rel(raw["page"]), "url": host, "tab": tab, "frame": frame,
             "stops": stops, "line": "（写这一句口播）", "src": url}
        if portrait: b["toc"] = False                         # the stop list would shrink the page; labels sit on the page
        beats.append(b)
    elif portrait and len(lift) > 1:
        c = lift[1]
        beats.append({"scene": "fx", "fx": "ui_lift", "image": rel(raw["page"]), "box": c["box_px"], "piece": rel(c["file"]),
                      "url": host, "tab": tab, "frame": frame, "path": path_of(c, 2), "line": "（写这一句口播）", "src": url})
    # 3 · a component with real buttons: the pointer clicks them (cursor on the capture itself)
    pref = {"pick": 0, "form": 1, "table": 2, "plan": 3, "card": 3, "pricing": 4, "cards": 4, "cta": 5, "code": 6, "nav": 7}
    other = next((c for c in sorted(demo, key=lambda c: pref.get(c["kind"], 9)) if c is not hero and c["kind"] in pref
                  and (not portrait or c["box"]["h"] <= c["box"]["w"] * 1.8)), None)
    if other:
        wide = other["box"]["w"] > (440 if portrait else 900)
        steps = path_of(other, 2)
        if len(steps) == 1: steps[0]["at"] = 1.2               # a lone click lands early, so its label has time to be read
        beats.append({"scene": "fx", "fx": "cursor", "image": rel(other["file"]), "frame": "none", "zoom": 1.5 if wide else 1.0,
                      "path": steps, "line": "（写这一句口播）", "src": url})
    # 4 · "look at this one": spotlight the components on the first screen (screen image = one frame's shape)
    if narrow or not portrait:
        boxes = [{"box": c["box_px"], "label": short(c["head"] or c["text"], 14)} for c in on_page
                 if c["kind"] in ("cta", "card", "plan", "form", "code", "table", "pick") and c["box_px"][1] + c["box_px"][3] <= raw["screen_h"]][:3]
        if boxes:
            beats.append({"scene": "fx", "fx": "spotlight", "image": rel(raw["screen"]), "frame": frame, "url": host,
                          "zoom": 1.0 if portrait else 1.25, "boxes": boxes, "line": "（写这一句口播）", "src": url})
    # 5 · several real pieces side by side (cards / plans / buttons) as a stack of captures (16:9: room for several)
    pieces = [rel(c["file"]) for c in comps if c["kind"] in ("card", "plan", "cta", "form", "code", "table", "pick") and c["size"][1] <= c["size"][0] * 2.5][:4]
    if len(pieces) >= 2 and not portrait:
        beats.append({"scene": "fx", "fx": "collage", "images": pieces, "text": short(raw.get("site", ""), 12),
                      "line": "（写这一句口播）", "src": url})
    return beats


def save_small(src, dst, max_w=None, max_h=16000, quality=84):
    """src image -> dst JPEG no wider than max_w (and ≤ max_h tall); returns the scale applied."""
    from PIL import Image
    with Image.open(src) as im:
        im = im.convert("RGB")
        k = min(1.0, (max_w or im.width) / im.width, max_h / im.height)
        if k < 0.999: im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        im.save(dst, quality=quality, optimize=True, progressive=True)
    return k


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("url"); ap.add_argument("--out", default="work/ui")
    ap.add_argument("--pick", action="append", default=[], help="CSS selector of a component to capture (repeatable)")
    ap.add_argument("--auto", action="store_true", help="find hero / nav / CTA / cards / pricing / form / code / table")
    ap.add_argument("--aspect", default="16:9", choices=["16:9", "9:16"], help="9:16 captures the mobile layout and emits phone-readable beats")
    ap.add_argument("--mobile", action="store_true"); ap.add_argument("--dark", action="store_true")
    ap.add_argument("--width", type=int, default=0); ap.add_argument("--wait", type=int, default=1500)
    ap.add_argument("--max", type=int, default=8, help="most components with --auto")
    ap.add_argument("--video-dir", default=None, help="folder of the video.json the beats go into (default: parent of --out)")
    ap.add_argument("--max-height", type=int, default=0, help="longest page part kept (CSS px; default 8000, 4000 for 9:16)")
    ap.add_argument("--page-width", type=int, default=1600, help="widest page image kept (px; the component captures stay 2x)")
    a = ap.parse_args()
    portrait = a.aspect == "9:16"
    a.mobile = a.mobile or (portrait and not a.width)
    a.max_height = a.max_height or (4000 if portrait else 8000)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    raw = capture(a, out)
    from PIL import Image
    pre = re.sub(r"[^\w-]+", "-", out.name).strip("-") or "ui"      # every file carries the capture's name: two sites never collide
    for c in raw["components"]:
        if c.get("file") and (out / c["file"]).exists():
            (out / c["file"]).rename(out / f"{pre}-{c['file']}"); c["file"] = f"{pre}-{c['file']}"
    k = raw["scale"]                                           # component captures: CSS px -> capture px
    # the page as a JPEG, capped in width: kp = CSS px -> page image px
    page_f, screen_f = f"{pre}-page.jpg", f"{pre}-screen.jpg"
    kp = k * save_small(out / "page.png", out / page_f, max_w=a.page_width)
    (out / "page.png").unlink()
    with Image.open(out / page_f) as im:
        raw["page"], raw["page_h"] = page_f, im.height
        raw["screen_h"] = min(im.height, round(im.width * (1.09 if portrait else 0.62)))   # one frame's shape
        im.crop((0, 0, im.width, raw["screen_h"])).save(out / screen_f, quality=84, optimize=True)
        raw["screen"], page_w = screen_f, im.width
    comps, missing = [], []
    for c in raw["components"]:
        if c.get("missing"): missing.append(c["missing"]); continue
        f = out / c["file"]
        if not f.exists(): continue
        if f.stat().st_size > 200_000:                         # big photographic pieces: JPEG keeps the 2x size, a tenth of the bytes
            save_small(f, f.with_suffix(".jpg"), quality=88); f.unlink(); f = f.with_suffix(".jpg"); c["file"] = f.name
        with Image.open(f) as im: size = list(im.size)
        b = c["box"]
        comps.append({"id": c["id"], "file": c["file"], "kind": c["kind"], "kind_zh": KIND_ZH.get(c["kind"], c["kind"]), "selector": c["selector"],
                      "region": not c["selector"], "tag": c.get("tag", ""),
                      "box": b, "box_px": [round(b["x"] * kp), round(b["y"] * kp), round(b["w"] * kp), round(b["h"] * kp)], "size": size,
                      "head": c.get("head", ""), "text": c["text"],
                      "hot": [{**h, "x": round(h["x"] * k), "y": round(h["y"] * k), "w": round(h["w"] * k), "h": round(h["h"] * k)} for h in c["hot"]],
                      "colors": colours(f)})
    # page.json: the sidecar scroll_shot / cite_article read (headings in page image px)
    S = lambda o: {**o, "x": round(o["x"] * kp), "y": round(o["y"] * kp), "w": round(o["w"] * kp), "h": round(o["h"] * kp)}
    page = {"url": a.url, "title": raw["title"], "description": raw.get("description", ""), "site": raw.get("site", ""),
            "width": page_w, "height": raw["page_h"], "scale": round(kp, 4),
            "headings": [S(h) for h in raw.get("headings", [])], "boxes": [], "paragraphs": []}
    (out / page_f).with_suffix(".json").write_text(json.dumps(page, ensure_ascii=False, indent=1))
    ui = {"url": a.url, "title": raw["title"], "site": raw.get("site", ""), "aspect": a.aspect, "page": page_f, "screen": screen_f,
          "page_size": [page_w, raw["page_h"]], "page_scale": round(kp, 4), "scale": k, "components": comps, "missing": missing}
    (out / "ui.json").write_text(json.dumps(ui, ensure_ascii=False, indent=1))
    (out / "raw.json").unlink(missing_ok=True)
    vdir = Path(a.video_dir) if a.video_dir else out.parent
    rel = lambda name: os.path.relpath(out / name, vdir).replace(os.sep, "/")
    beats = beats_for(comps, raw, a.url, portrait, rel)
    (out / "beats.json").write_text(json.dumps(beats, ensure_ascii=False, indent=1))
    print(f"{out / page_f}  {page_w}×{raw['page_h']}")
    for c in comps:
        print(f"  {c['file']:<16} {c['kind_zh']:<4} {c['size'][0]}×{c['size'][1]}  {len(c['hot'])} 可点  {short(c['head'] or c['text'], 28)}")
    for m in missing: print(f"  ! no element matches {m!r}")
    print(f"{len(beats)} beats ({a.aspect}) · {out / 'beats.json'}  (paths relative to {vdir})")


if __name__ == "__main__":
    main()
