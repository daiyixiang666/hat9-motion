#!/usr/bin/env python3
"""Only a URL? Turn it into ready-to-edit beats: a full-page screenshot that scrolls and stops at the page's sections
(scroll_shot) plus an article card with its title, description and a first excerpt (cite_article).

  python3 scripts/url_brief.py <url> --out work/brief [--find "phrase"]... [--selector article] [--mobile] [--stops 3]
      -> work/brief/page.png  page.json  beats.json  (paste the beats into your video.json and write the `line`s)

Uses scripts/webpage.mjs (the Chrome that HyperFrames installs). Nothing is summarised by a model: headings become
stops, the page's own description and first paragraph become the card text, so every word on screen is the page's.
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url"); ap.add_argument("--out", required=True)
    ap.add_argument("--find", action="append", default=[]); ap.add_argument("--selector", default="")
    ap.add_argument("--mobile", action="store_true"); ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--stops", type=int, default=3); ap.add_argument("--max-height", type=int, default=14000)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    png, js = out / "page.png", out / "page.json"
    cmd = ["node", str(HERE / "webpage.mjs"), a.url, str(png), "--json", str(js), "--max-height", str(a.max_height)]
    if a.selector: cmd += ["--selector", a.selector]
    if a.mobile: cmd += ["--mobile"]
    if a.width: cmd += ["--width", str(a.width)]
    for f in a.find: cmd += ["--find", f]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"url_brief: could not capture {a.url}\n{r.stderr.strip()}")
    page = json.loads(js.read_text())
    heads = [h for h in page.get("headings", []) if h.get("level", 2) <= 2 and h.get("y", 0) > 200]
    if len(heads) > a.stops:                       # spread the stops over the page instead of taking the first few
        step = len(heads) / a.stops
        heads = [heads[int(i * step)] for i in range(a.stops)]
    stops = [{"find": f, "label": f} for f in a.find if any(b["find"] == f for b in page.get("boxes", []))] or \
            [{"heading": h["text"], "label": h["text"][:24]} for h in heads]
    desc = page.get("description", "")
    paras = [p for p in page.get("paragraphs", []) if p.strip() and p.strip()[:40] != desc.strip()[:40]]
    excerpt = next((p for p in paras if 20 <= len(p) <= 240), (paras or [""])[0])[:120]
    beats = [
        {"scene": "fx", "fx": "scroll_shot", "image": str(png.name), "url": a.url, "tab": page.get("title", "")[:30],
         "frame": "phone" if a.mobile else "browser", "stops": stops, "line": "（写这一句口播）", "src": a.url},
        {"scene": "fx", "fx": "cite_article", "outlet": page.get("site", ""), "headline": page.get("title", ""), "dek": page.get("description", ""),
         "excerpt": excerpt, "url": a.url, "image": str(png.name), "line": "（写这一句口播）", "src": a.url},
    ]
    (out / "beats.json").write_text(json.dumps(beats, ensure_ascii=False, indent=1))
    print(f"{png}  {page['width']}×{page['height']}  {len(stops)} stops · {out / 'beats.json'}")


if __name__ == "__main__":
    main()
