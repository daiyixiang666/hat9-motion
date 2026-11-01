#!/usr/bin/env python3
"""Covers in 16:9, 4:3 and 3:4 from a frame of the finished film + the title, in the film's style.

  python3 scripts/cover.py examples/mixue --at 2.5
  python3 scripts/cover.py examples/mixue --at 9 --title "一杯 4 块钱的柠檬水|一年净赚 44 亿" --kicker "商业拆解"

Reads <example>/video.json (meta.title / meta.section, meta.style) and <example>/renders/<style>_16x9.mp4 (and _9x16
for the 3:4 cover when it exists, so the tall cover is cut from the tall film). The title is fitted to its box with
scripts/h9/fit.py (shrink → balanced wrap by words), so it never overflows; `hyperframes check` verifies each cover.
Writes <example>/covers/cover_16x9.jpg, cover_4x3.jpg, cover_3x4.jpg.
"""
import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from h9 import core, fit, fonts  # noqa: E402
import build as B                 # noqa: E402

HF = ["npx", "--yes", "hyperframes@0.8.191"]
SIZES = {"16:9": (1920, 1080), "4:3": (1440, 1080), "3:4": (1080, 1440)}


def frame(src, at, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.2f}", "-i", str(src), "-frames:v", "1", "-q:v", "2", str(dst)], check=True)


def page(X, style, img, title, kicker, focus):
    W, H = X.W, X.H
    tok = style["tokens"]
    m = min(W, H)
    portrait = H > W
    panel = 0.44 if portrait else 0.42                       # the title sits on a solid panel; the frame stays clean above it
    box_w = W * 0.86
    box_h = H * panel * 0.62
    f = fit.fit_text(title, box_w, box_h, m * 0.15, m * 0.06, lh=1.08, max_lines=3)
    X.used_text.update(title + kicker)
    lines = "<br>".join(X.rich(l) for l in f.lines)
    css_tok = ":root { " + " ".join(f"--{k}:{v};" for k, v in tok.items()) + " }"
    font_css = fonts.build(X, "".join(X.used_text))
    pad = round(m * 0.07)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="{B.GSAP}"></script>
<style>{font_css}
{css_tok}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#000; }}
#root {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; }}
.bg {{ position:absolute; left:0; top:0; width:100%; height:{(1 - panel) * 100 + 2:.1f}%; object-fit:cover; object-position:{focus}; }}
.scrim {{ position:absolute; left:0; right:0; bottom:0; height:{panel * 100:.1f}%; background:var(--ink, #111); }}
.scrim::before {{ content:""; position:absolute; left:0; right:0; top:-{round(m * 0.12)}px; height:{round(m * 0.12)}px; background:linear-gradient(180deg, rgba(0,0,0,0), var(--ink, #111)); }}
.box {{ position:absolute; left:{pad}px; right:{pad}px; bottom:0; height:{panel * 100:.1f}%; display:flex; flex-direction:column; justify-content:center; align-items:flex-start; gap:{round(m * 0.022)}px; }}
.kick {{ font-family:var(--f-display, var(--f-body)); font-weight:900; font-size:{round(m * 0.034)}px; color:var(--ink, #111); background:var(--accent2, var(--accent)); padding:.18em .6em; letter-spacing:.06em; }}
.ttl {{ font-family:var(--f-display, var(--f-body)); font-weight:900; font-size:{f.px:.0f}px; line-height:1.08; color:#fff; letter-spacing:-.01em; max-width:{box_w:.0f}px;
  text-shadow:0 .04em .3em rgba(0,0,0,.45); }}
.ttl .em .emt {{ color:var(--accent2, var(--accent)); }} .ttl .em .emb {{ display:none; }}
.bar {{ width:{round(m * 0.09)}px; height:{max(6, round(m * 0.008))}px; background:var(--accent); }}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="1" data-width="{W}" data-height="{H}">
<img class="bg" src="{img}" alt=""><div class="scrim"></div>
<div class="box">{f'<div class="kick">{X.rich(kicker)}</div>' if kicker else ''}<div class="ttl">{lines}</div><div class="bar"></div></div>
</div>
<script>window.__timelines = window.__timelines || {{}}; const tl = gsap.timeline({{ paused: true }}); tl.set({{}}, {{}}, 1); window.__timelines["main"] = tl;</script>
</body></html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("example"); ap.add_argument("--at", type=float, default=2.5)
    ap.add_argument("--title"); ap.add_argument("--kicker"); ap.add_argument("--style"); ap.add_argument("--focus", default="50% 45%")
    ap.add_argument("--check", action="store_true", help="run hyperframes check on each cover (overflow gate)")
    ap.add_argument("--out", help="folder for the covers (default <example>/covers)")
    a = ap.parse_args()
    ex = Path(a.example).resolve()
    video = json.loads((ex / "video.json").read_text())
    meta = video.get("meta", {})
    sid = a.style or meta.get("style", "press")
    style = B.load_style(sid)
    title = a.title or meta.get("title", "")
    kicker = a.kicker if a.kicker is not None else meta.get("section", "")
    r16, r9 = ex / "renders" / f"{sid}_16x9.mp4", ex / "renders" / f"{sid}_9x16.mp4"
    if not r16.exists(): raise SystemExit(f"render first: {r16}")
    outd = Path(a.out).resolve() if a.out else ex / "covers"; outd.mkdir(parents=True, exist_ok=True)
    for asp, (W, H) in SIZES.items():
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            X = core.Ctx(video, style, td, ex, asp)
            (td / "assets").mkdir(exist_ok=True)
            frame(r9 if asp == "3:4" and r9.exists() else r16, a.at, td / "assets" / "frame.jpg")
            (td / "index.html").write_text(page(X, style, "assets/frame.jpg", title, kicker, a.focus))
            (td / "hyperframes.json").write_text(json.dumps({"paths": {"assets": "assets"}}))
            if a.check:
                c = subprocess.run(HF + ["check", "--json"], cwd=td, capture_output=True, text=True).stdout
                j = json.loads(c[c.find("{"):])
                bad = [f for v in j.values() if isinstance(v, dict) for f in v.get("findings", [])
                       if f["code"] in ("text_box_overflow", "canvas_overflow") or f["severity"] == "error"]
                for f in bad: print(f"  ! {asp} {f['code']} {f.get('selector', '')} {f['message'][:90]}")
            subprocess.run(HF + ["snapshot", "-o", str(td / "snap"), "--at", "0.5", "--no-end"], cwd=td, capture_output=True, text=True)
            png = sorted((td / "snap").glob("frame-*.png"))
            if not png: raise SystemExit(f"snapshot failed for {asp}")
            from PIL import Image
            Image.open(png[0]).convert("RGB").save(outd / f"cover_{asp.replace(':', 'x')}.jpg", quality=90)
        print(outd / f"cover_{asp.replace(':', 'x')}.jpg")


if __name__ == "__main__":
    main()
