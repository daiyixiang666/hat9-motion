#!/usr/bin/env python3
"""Build the standalone style gallery page from styles/*.py + the showcase films in assets/previews/.

  python3 scripts/gallery.py [press,ink,…]   -> dist/gallery/index.html  (+ files.json, the files map for publishing)
(the repo's own gallery/index.html reads assets/previews/ directly; this is the one-page version to share)
"""
import html, importlib.util, json, re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PV = SKILL / "assets" / "previews"
OUT = SKILL / "dist" / "gallery"
import sys
ORDER = sys.argv[1].split(",") if len(sys.argv) > 1 else ["press", "minimal", "poster", "zine", "screen", "atlas", "doc", "papercut", "sketch",
                                                          "ink", "flat", "pixel", "iso3d", "chrome3d"]
FILM = {"press": "mixue"}      # style id -> its showcase film's preview name in assets/previews (when they differ)
LINKS = {   # one representative real video per benchmark (what we studied)
    "Vox": "https://www.youtube.com/watch?v=VYJtb2YXae8", "The Economist": "https://www.youtube.com/@TheEconomist",
    "Financial Times": "https://www.youtube.com/@FinancialTimes", "Johnny Harris": "https://www.youtube.com/watch?v=4S25FfbFw4M",
    "NYT Visual Investigations": "https://www.nytimes.com/spotlight/visual-investigations", "Vox Atlas": "https://www.youtube.com/@Vox",
    "Pursuit of Wonder": "https://www.youtube.com/@PursuitofWonder", "Nathaniel Drew": "https://www.youtube.com/@NathanielDrew",
    "LEMMiNO": "https://www.youtube.com/watch?v=I2O7blSSzpI", "Apple keynote": "https://www.youtube.com/@Apple",
    "Vercel Ship": "https://vercel.com/ship", "Linear": "https://linear.app", "Dan Koe": "https://www.youtube.com/@DanKoeTalks",
    "Alex Hormozi": "https://www.youtube.com/@AlexHormozi", "PolyMatter": "https://www.youtube.com/watch?v=j2QEieIiiXg",
    "Wendover Productions": "https://www.youtube.com/@Wendoverproductions", "The Economist charts": "https://www.youtube.com/@TheEconomist",
    "回形针PaperClip": "https://www.youtube.com/watch?v=k8H7YWcq_Sg", "3Blue1Brown": "https://www.youtube.com/@3blue1brown",
    "LEMMiNO ": "https://www.youtube.com/watch?v=I2O7blSSzpI", "Kurzgesagt": "https://www.youtube.com/watch?v=ujkD4SxPKOI",
    "Cleo Abram": "https://www.youtube.com/watch?v=MWHN6ojlVXI", "Fireship": "https://www.youtube.com/watch?v=TbkUKCm3CHQ",
    "半佛仙人": "https://www.bilibili.com/video/BV1yjen6QEN3/", "AI Explained": "https://www.youtube.com/@aiexplained-official",
    "秋芝2046": "https://www.bilibili.com/video/BV1DLYC6oEKT/", "漫士沉思录": "https://www.bilibili.com/video/BV1ANpM6HEHU/",
    "智能路障": "https://www.bilibili.com/video/BV1ZGJ96aES6/", "小约翰可汗": "https://www.bilibili.com/video/BV1ocsd6jErz/",
    "何同学": "https://www.bilibili.com/video/BV12peP6kEnK/", "影视飓风": "https://www.bilibili.com/video/BV1tg4y1371e/",
    "林亦LYi": "https://www.bilibili.com/video/BV1o4gw6ZExs/", "地球知识局": "https://www.bilibili.com/video/BV1EwtZ6NErF/",
    "小Lin说": "https://www.bilibili.com/video/BV1yUHP6rEYD/", "飞天闪客": "https://www.bilibili.com/video/BV17x6hYZEzJ/",
    "Ele实验室": "https://www.bilibili.com/video/BV1Sf4y147J9/", "柴知道": "https://www.bilibili.com/video/BV1e64y1b7AV/",
    "毕导": "https://www.bilibili.com/video/BV1cpJ86BEys/", "所长林超": "https://www.bilibili.com/video/BV1U1RTBTEVa/",
}


def load(sid):
    sys.path.insert(0, str(SKILL / "scripts"))         # styles import h9 helpers
    p = SKILL / "styles" / f"{sid}.py"
    if not p.exists():
        p = SKILL / "styles" / "legacy" / f"{sid}.py"
    spec = importlib.util.spec_from_file_location(sid, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    doc = (m.__doc__ or "").strip().splitlines()
    return m.STYLE, doc


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tpl = (SKILL / "scripts" / "gallery_template.html").read_text()
    cards, files = [], {}
    for sid in ORDER:
        st, doc = load(sid)
        mp4, jpg = PV / f"{FILM.get(sid, sid)}_16x9.mp4", PV / f"{FILM.get(sid, sid)}_16x9.jpg"
        if not mp4.exists(): continue
        files[f"v/{sid}.mp4"] = str(mp4); files[f"v/{sid}.jpg"] = str(jpg)
        body = " ".join(doc[1:]).strip()
        vibe, fit = (body.split("适合：") + [""])[:2]
        bm = " · ".join(f'<a href="{LINKS.get(b, "#")}" target="_blank" rel="noopener">{html.escape(b)}</a>' for b in st.get("benchmarks", []))
        tok = st["tokens"]
        sw = "".join(f'<i style="background:{tok[k]}" title="{k}"></i>' for k in ("bg", "fg", "accent") if k in tok)
        cards.append(f"""
<article class="card" id="{sid}">
  <div class="frame"><video src="v/{sid}.mp4" poster="v/{sid}.jpg" controls playsinline preload="metadata"></video></div>
  <div class="meta">
    <div class="row"><code class="sid">{sid}</code><span class="sw">{sw}</span></div>
    <h2>{html.escape(st['name'])} <span class="en">{html.escape(st.get('en', ''))}</span></h2>
    <p class="bm">对标 {bm}</p>
    <p class="vibe">{html.escape(vibe.strip())}</p>
    <p class="fit"><b>适合</b>{html.escape(fit.strip().rstrip('。'))}</p>
  </div>
</article>""")
    log = (SKILL / "CHANGELOG.md").read_text()
    log_html = "".join(f"<li>{html.escape(l[2:])}</li>" for l in log.splitlines() if l.startswith("- "))
    if len(cards) == 1:
        kick, h1 = "九帽动效 v0.2 · 样板", "先把一种风格做到位"
        lede = ("0.1 的 10 种风格作废：它们共用一套模板只换了皮，所以彼此很像、手法很套。这一版先只做一种，按新做法从头写："
                "先看标杆大图，再给这个风格写专属的场景和招牌组件。<b>请看这个水准是不是你要的方向</b>，确认后用同样的标准重做其他风格。")
    else:
        kick, h1 = "九帽动效", f"{len(cards)} 种风格，各一条示例片"
        lede = "每种风格一条示例片，横屏 16:9。每种风格都<b>对标真实的顶级创作者</b>，有自己的场景、组件和动作语言。点开带声音看。"
    page = (tpl.replace("{{CARDS}}", "".join(cards)).replace("{{CHANGELOG}}", log_html).replace("{{KICK}}", kick).replace("{{H1}}", h1)
            .replace("{{LEDE}}", lede).replace("{{SOLO}}", " solo" if len(cards) == 1 else ""))
    (OUT / "index.html").write_text(page)
    (OUT / "files.json").write_text(json.dumps(files, indent=1))
    print(OUT / "index.html", len(cards), "styles")


if __name__ == "__main__":
    main()
