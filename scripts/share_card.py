#!/usr/bin/env python3
"""One shareable takeaway card (金句卡) as a still PNG — the same card the `share_card` effect animates in a film.

  python3 scripts/share_card.py "看懂谁在*赚钱*，比看懂谁在卖货更重要。" --by "第九顶帽子 · 商业拆解第 07 期" --handle @第九顶帽子
  python3 scripts/share_card.py "..." --aspect 1:1 --theme ink --out covers/quote_1x1.png

*关键词* gets the marker. Aspects: 3:4 (default, 小红书), 4:5, 1:1, 9:16. Themes: paper / ink / red / lemon.
Builds a one-beat page with `export: true` (no animation, no page around the card), checks it with `hyperframes check`
and saves one frame with `hyperframes snapshot`. Local only: no network beyond the pinned npx package, no paid APIs.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
HF = ["npx", "--yes", "hyperframes@0.8.191"]
ASPECTS = ("3:4", "4:5", "1:1", "9:16")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("quote", nargs="?", help="the line; *word* is marked")
    ap.add_argument("--quote", dest="quote_opt"); ap.add_argument("--text", dest="quote_txt")
    ap.add_argument("--by", default=""); ap.add_argument("--handle", default="")
    ap.add_argument("--kicker", default="今日金句"); ap.add_argument("--date", default="")
    ap.add_argument("--theme", default="paper", choices=("paper", "ink", "red", "lemon"))
    ap.add_argument("--aspect", default="3:4", choices=ASPECTS)
    ap.add_argument("--out", default="share_card.png")
    ap.add_argument("--keep", help="keep the build folder here (for inspection)")
    a = ap.parse_args()
    quote = a.quote_opt or a.quote_txt or a.quote
    if not quote: ap.error("give the quote (positional, --quote or --text)")
    beat = {"scene": "fx", "fx": "share_card", "t": 0, "d": 1.0, "theme": a.theme, "export": True,
            "quote": quote, "by": a.by, "handle": a.handle, "kicker": a.kicker, "date": a.date}
    video = {"meta": {"title": "share card", "duration": 1.0, "aspect": a.aspect, "canvas": False}, "beats": [beat]}
    tmp = Path(tempfile.mkdtemp(prefix="h9-share-"))
    try:
        (tmp / "video.json").write_text(json.dumps(video, ensure_ascii=False))
        build = Path(a.keep).resolve() if a.keep else tmp / "build"
        r = subprocess.run([sys.executable, str(HERE / "build.py"), str(tmp / "video.json"), "--style", "reel",
                            "--aspect", a.aspect, "--out", str(build)], capture_output=True, text=True)
        if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit("build failed")
        chk = subprocess.run(HF + ["check", "--json"], cwd=build, capture_output=True, text=True).stdout
        try:
            j = json.loads(chk[chk.find("{"):])
            errs = [f for v in j.values() if isinstance(v, dict) for f in v.get("findings", []) if f.get("severity") == "error"]
        except ValueError:
            errs = []
        for f in errs: print(f"  check: {f['code']} {f.get('selector', '')[:60]} {f['message'][:90]}")
        shots = tmp / "shots"
        subprocess.run(HF + ["snapshot", "-o", str(shots), "--at", "0.5", "--no-end"], cwd=build, capture_output=True, text=True)
        png = sorted(shots.glob("frame-*.png"))
        if not png: raise SystemExit("snapshot produced no frame")
        out = Path(a.out).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(png[0], out)
        print(f"{out}  ({a.aspect}, {a.theme}{', check errors: ' + str(len(errs)) if errs else ''})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
