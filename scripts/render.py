#!/usr/bin/env python3
"""build -> check -> render -> (optional) small web preview, for one or many styles.

  python3 scripts/render.py examples/demo/video.json --styles schematic,archive [--aspect 16:9] [--preview]
  python3 scripts/render.py examples/demo/video.json --styles all --preview
  python3 scripts/render.py examples/demo/video.json --styles press --lint    # + craft lint (AI-design tells), report only

Outputs  <video dir>/renders/<style>_<aspect>.mp4  (+ previews/<style>_<aspect>.mp4 and .jpg poster with --preview).

  --gate   (what `hat9.py render` always passes) the quality gate in code, not in instructions:
           before: `brief check` on the first style — any P0 refuses to render (exit 2) unless --force;
           after:  review.py on each mp4 — 2 fps contact sheets in renders/review_<name>/, the automatic checks
                   (caption fragments, headline sync, text on face, tiny text, contrast, freeze, loudness …),
                   a short pass / fail list, and exit 1 when any P0 is left.
"""
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
HF = ["npx", "--yes", "hyperframes@0.8.191"]


def run(cmd, cwd=None, ok_fail=False):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode and not ok_fail: print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit(f"failed: {' '.join(map(str, cmd))}")
    return r.stdout


def has_audio(mp4):
    return bool(run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(mp4)]).strip())


def loud(mp4, lufs):
    """two-pass loudnorm to `lufs` with true peak under -1 dBTP (target -2: AAC adds a little); the picture is copied untouched."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", f"loudnorm=I={lufs}:TP=-2:LRA=11:print_format=json", "-vn", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rfind("{"):r.stderr.rfind("}") + 1])
    tmp = mp4.with_name(mp4.stem + ".loud.mp4")
    af = (f"loudnorm=I={lufs}:TP=-2:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-c:v", "copy", "-af", af, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", str(tmp)])
    tmp.replace(mp4)


GATE_RULES = (("caption-frag", "字幕不碎（≥4 字、不切词）"), ("sync-head", "大字和口播同步"), ("text-on-face", "字不压脸"),
              ("tiny-text", "字号够大"), ("contrast", "字和底对比够"), ("freeze", "画面不冻住"), ("hook", "前 2 秒有变化"),
              ("slides", "不是 PPT"), ("caption-dup", "大字不只重复字幕"), ("loudness", "响度"), ("dead-air", "没有空白声音"))


def findings_of(text):
    """[(level, rule, message)] from the '  P0 rule message' lines a gate script prints."""
    out = []
    for line in text.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) >= 2 and parts[0] in ("P0", "P1"):
            msg = parts[2] if len(parts) > 2 else ""
            out.append((parts[0], parts[1], msg))
    return out


def pre_gate(v, style, aspect, force):
    """brief check before rendering; a P0 stops here unless --force."""
    sys.path.insert(0, str(HERE))
    import brief
    print("== 渲染前检查（brief check）")
    found, _ = brief.check(v, style, aspect)
    p0 = 0
    for lv, rule, msg in found:
        print(f"  {lv} {rule:<12} {msg}")
        if lv == "P0":
            p0 += 1
    if not found:
        print("  分镜检查通过")
    if p0 and not force:
        print(f"✗ 有 {p0} 个 P0，不渲染。先改 video.json 再来；确实要先出一版看看：加 --force")
        raise SystemExit(2)
    if p0:
        print(f"  ! 有 {p0} 个 P0，--force 继续渲染")


def post_gate(mp4, v, build):
    """review.py on the render: contact sheets + automatic checks; → number of P0."""
    r = subprocess.run([sys.executable, str(HERE / "review.py"), str(mp4), "--video", str(v), "--build", str(build)],
                       capture_output=True, text=True)
    found = findings_of(r.stdout)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        print("  ✗ 自检没跑完（见上）")
        return 1
    print("  自动检查：")
    for rule, name in GATE_RULES:
        hits = []
        for item in found:
            if item[1] == rule:
                hits.append(item)
        if not hits:
            print(f"    ✓ {name}")
            continue
        worst = "P1"
        for item in hits:
            if item[0] == "P0":
                worst = "P0"
        print(f"    ✗ {name}  {worst} ×{len(hits)}  {hits[0][2][:110]}")
    others = []
    for item in found:
        known = False
        for rule, name in GATE_RULES:
            if item[1] == rule:
                known = True
        if not known:
            others.append(item)
    for lv, rule, msg in others:
        print(f"    · {lv} {rule} {msg[:110]}")
    sheets_dir = mp4.parent / f"review_{mp4.stem}"
    sheet_files = sorted(sheets_dir.glob("sheet_*.jpg"))
    for f in sheet_files:
        print(f"  静帧板（每秒 2 帧）：{f}")
    print(f"  打分表：{sheets_dir / 'review.md'}（逐张看完静帧板再打分，python3 scripts/review.py --gate 过关才交付）")
    p0 = 0
    for item in found:
        if item[0] == "P0":
            p0 += 1
    return p0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--styles", default="all"); ap.add_argument("--aspect", default=None)
    ap.add_argument("--preview", action="store_true"); ap.add_argument("--quality", default="standard")
    ap.add_argument("--lint", action="store_true", help="run scripts/craft_lint.py on each build (report only, never blocks the render)")
    ap.add_argument("--lufs", type=float, default=-14.0, help="normalise the sound to this loudness (platforms play about -14); 0 = leave it")
    ap.add_argument("--gate", action="store_true", help="brief check before (P0 refuses) and review after (contact sheet + checks; exit 1 on P0)")
    ap.add_argument("--force", action="store_true", help="with --gate: render even when brief check finds a P0")
    a = ap.parse_args()
    v = Path(a.video).resolve()
    styles = sorted(p.stem for p in (SKILL / "styles").glob("[!_]*.py")) if a.styles == "all" else a.styles.split(",")
    aspect = a.aspect or json.loads(v.read_text()).get("meta", {}).get("aspect", "16:9")
    tag = aspect.replace(":", "x")
    (v.parent / "renders").mkdir(exist_ok=True)
    if a.gate:
        pre_gate(v, styles[0], aspect, a.force)
    gate_p0 = 0
    for sid in styles:
        out = v.parent / "build" / f"{sid}_{tag}"
        print(f"== {sid}")
        run([sys.executable, str(HERE / "build.py"), str(v), "--style", sid, "--aspect", aspect, "--out", str(out)])
        chk = run(HF + ["check", "--json"], cwd=out, ok_fail=True)
        j = json.loads(chk[chk.find("{"):])
        errs = [(sec, f) for sec, v in j.items() if isinstance(v, dict) for f in v.get("findings", []) if f["severity"] == "error"]
        for sec, f in errs: print(f"  {sec} error", f["code"], f.get("selector", ""), f.get("time", ""), f["message"][:140])
        if errs and a.gate:
            print("  ✗ hyperframes check 有 error，这个风格不渲染（算 P0）")
        if a.lint:
            lint = subprocess.run([sys.executable, str(HERE / "craft_lint.py"), str(out)], capture_output=True, text=True).stdout
            print("  " + lint.strip().replace("\n", "\n  "))
        if errs:
            if a.gate:
                gate_p0 += 1
            continue
        mp4 = v.parent / "renders" / f"{sid}_{tag}.mp4"
        run(HF + ["render", "--quality", a.quality, "--output", str(mp4)], cwd=out)
        if a.lufs and has_audio(mp4):
            loud(mp4, a.lufs)
        print("  ->", mp4)
        if a.gate:
            gate_p0 += post_gate(mp4, v, out)
        if a.preview:
            pv = v.parent / "previews"; pv.mkdir(exist_ok=True)
            w = 1280 if aspect == "16:9" else 720
            run(["ffmpeg", "-v", "error", "-y", "-i", str(mp4), "-vf", f"scale={w}:-2", "-c:v", "libx264", "-preset", "slow", "-crf", "26",
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "96k", str(pv / f"{sid}_{tag}.mp4")])
            run(["ffmpeg", "-v", "error", "-y", "-ss", "1.2", "-i", str(mp4), "-frames:v", "1", "-vf", f"scale={w}:-2", "-q:v", "4", str(pv / f"{sid}_{tag}.jpg")])
    if a.gate and gate_p0:
        print(f"✗ 成片还有 {gate_p0} 个 P0：改完重新渲染，不要交付")
        sys.exit(1)


if __name__ == "__main__":
    main()
