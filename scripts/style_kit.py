#!/usr/bin/env python3
"""Make your own style from one of ours, look at it, check it, and add it to the gallery.

  python3 scripts/style_kit.py new 我的id --from ink [--name 我的水墨] [--fits "适合…"]   换皮：只改颜色/字体/质感/CSS
  python3 scripts/style_kit.py new 我的id --from ink --copy                              整份复制：连场景代码一起改
  python3 scripts/style_kit.py preview 我的id [--aspect 9:16] [--render]                  用底稿的示例片 + 动效片出预览
  python3 scripts/style_kit.py check 我的id                                               字体、对比度、横竖屏构建
  python3 scripts/style_kit.py publish 我的id                                             渲染预览片放进画廊（再跑 catalog.py）

(also `python3 scripts/hat9.py style …`)
"""
import argparse, json, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
STYLES = SKILL / "styles"
sys.path.insert(0, str(HERE))
from h9 import derive, fonts  # noqa: E402

HF = ["npx", "--yes", "hyperframes@0.8.191"]
PY = sys.executable
SHOWCASE = {"press": "mixue", "reel": "demo", "hud": "styled-hud", "studio": "demo", "clay": "demo"}
TOKEN_NOTES = {
    "bg": "底色", "fg": "正文字色", "muted": "次要文字", "accent": "强调色（只用一个最好）", "accent2": "第二强调", "alert": "警示",
    "line": "细线 / 分隔", "paper": "纸色", "ink": "墨色", "card": "卡片底", "card-fg": "卡片上的字",
    "cap-bg": "字幕底", "cap-fg": "字幕字", "cap-em": "字幕里的关键词", "cap-size": "字幕字号", "radius": "圆角",
}


def style_name(sid):
    return derive.load_base(sid).STYLE.get("name", sid)


def lineage(sid):
    """the style, what it derives from, and what a full copy was forked from."""
    out = derive.chain(sid)
    m = re.search(r'^FORKED_FROM\s*=\s*"(\w+)"', (STYLES / f"{out[-1]}.py").read_text(encoding="utf-8"), re.M)
    return out + (lineage(m.group(1)) if m and m.group(1) not in out else [])


def showcase(sid):
    """the example film that shows a style best: its own, else its base's."""
    for c in lineage(sid):
        name = SHOWCASE.get(c, c)
        for d in (SKILL / "examples" / name, SKILL / "examples" / f"styled-{c}"):
            if (d / "video.json").exists(): return d / "video.json"
    return SKILL / "examples" / "demo" / "video.json"


def fx_reel(sid):
    for c in lineage(sid):
        p = SKILL / "examples" / f"styled-{c}" / "video.json"
        if p.exists(): return p
    return None


def pylit(v, indent):
    """a dict as Python source, one key per line, with a short note for the tokens people change most."""
    pad = " " * indent
    lines = ["{"]
    for k, x in v.items():
        note = f"   # {TOKEN_NOTES[k]}" if k in TOKEN_NOTES else ""
        lines.append(f"{pad}    {json.dumps(k, ensure_ascii=False)}: {json.dumps(x, ensure_ascii=False)},{note}")
    lines.append(pad + "}")
    return "\n".join(lines)


def themes_lit(v, indent):
    pad = " " * indent
    lines = ["{"]
    for k, x in v.items():
        lines.append(f"{pad}    {json.dumps(k)}: {json.dumps(x, ensure_ascii=False)},")
    lines.append(pad + "}")
    return "\n".join(lines)


def cmd_new(a):
    sid, base = a.id, a.base
    if not re.fullmatch(r"[a-z][a-z0-9_]*", sid): raise SystemExit("风格 id 只用小写字母、数字、下划线，字母开头，例如 my_ink")
    out = STYLES / f"{sid}.py"
    if out.exists() and not a.force: raise SystemExit(f"{out.relative_to(SKILL)} 已经存在（覆盖加 --force）")
    if not (STYLES / f"{base}.py").exists(): raise SystemExit(f"没有底稿风格 {base!r}；python3 scripts/hat9.py styles 看全部")
    b = derive.load_base(base)
    S = b.STYLE
    name = a.name or f"我的{S.get('name', base)}"
    fits = a.fits or ""

    if a.copy:
        src = (STYLES / f"{base}.py").read_text(encoding="utf-8")
        src = re.sub(rf"st-{base}\b", f"st-{sid}", src)
        src = re.sub(r'("name"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(name, ensure_ascii=False), src, count=1)
        src = re.sub(r'("en"\s*:\s*)"[^"]*"', lambda m: m.group(1) + json.dumps(sid), src, count=1)
        head = f'"""{sid} · {name} —— 整份复制自 {base}（{S.get("name", base)}），场景代码可以随便改。\n\n'
        src = re.sub(r'^"""', head.replace("\\", "\\\\"), src, count=1) if src.startswith('"""') else head + '"""\n' + src
        src = src.replace('\nimport ', f'\nFORKED_FROM = "{base}"   # 示例片和动效片沿用它的\nimport ', 1)
        if fits: src = src.replace('"en": ' + json.dumps(sid), '"en": ' + json.dumps(sid) + ', "fits": ' + json.dumps(fits, ensure_ascii=False), 1)
        out.write_text(src, encoding="utf-8")
    else:
        themes = S.get("fx_themes")
        themes_block = (f'    # 动效页的四种底色。改了上面的颜色，这里跟着改；或者整段换成 None，按上面的 tokens 自动推\n'
                        f'    "fx_themes": {themes_lit(themes, 4)},\n') if themes else \
                       '    # 动效页的四种底色：不写就按上面的 tokens 自动推（想手动定见 references/styles.md）\n'
        layers = json.dumps(S.get("layers", []), ensure_ascii=False).replace("[[", "[(").replace("]]", ")]").replace("], [", "), (")
        hooks = "".join(f'if hasattr(_b, "{h}"): {h} = _b.{h}\n' for h in ("SCENES", "WORLD", "FX_FRAME") if hasattr(b, h))
        out.write_text(f'''"""{sid} · {name} —— 在 {base}（{S.get("name", base)}）上改出来的自定义风格。
没写的都沿用 {base}：场景、动效页、镜头、音效全部继承。这里改颜色、字体、质感层和 CSS；要改场景本身，用 `style new --copy`。

  预览：python3 scripts/hat9.py style preview {sid}
  检查：python3 scripts/hat9.py style check {sid}
  使用：python3 scripts/hat9.py render 你的/video.json --style {sid}
"""
from h9 import derive

BASE = "{base}"
_b = derive.load_base(BASE)

STYLE = derive.merge(_b.STYLE, {{
    "name": {json.dumps(name, ensure_ascii=False)}, "en": {json.dumps(sid)},
    "fits": {json.dumps(fits, ensure_ascii=False)},   # 适合什么选题（画廊里显示）
    # 颜色：直接改值；删掉的 key 沿用 {base}
    "tokens": {pylit(S.get("tokens", {}), 4)},
    # 字体：只能用 assets/fonts.json 里的 id（全部字体和样张见 references/fonts.md）
    "fonts": {pylit(S.get("fonts", {}), 4)},
{themes_block}    # 质感层：("grain", {{"opacity": 0.05}})、("paper", …)、("vignette", …) 等，见 references/styles.md
    "layers": {layers},
    # 额外的 CSS：写在 .st-{sid} 下，排在 {base} 自己的 CSS 后面，同名规则以这里为准
    "css": """
""",
}})
{hooks}''', encoding="utf-8")
    print(f"新风格：{out.relative_to(SKILL)}（底稿 {base}{'，整份复制' if a.copy else ''}）")
    print(f"下一步：改文件里的颜色 / 字体，然后  python3 scripts/hat9.py style preview {sid}")


def build(video, sid, aspect):
    tag = aspect.replace(":", "x")
    out = video.parent / "build" / f"{sid}_{tag}"
    r = subprocess.run([PY, str(HERE / "build.py"), str(video), "--style", sid, "--aspect", aspect, "--out", str(out)], capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:], r.stderr[-1500:]); raise SystemExit(f"构建失败：{video.relative_to(SKILL)} · {sid} · {aspect}")
    return out


def hf_errors(out):
    r = subprocess.run(HF + ["check", "--json"], cwd=out, capture_output=True, text=True)
    j = json.loads(r.stdout[r.stdout.find("{"):] or "{}")
    return [f"{sec}: {f['code']} {f['message'][:120]}" for sec, v in j.items() if isinstance(v, dict) for f in v.get("findings", []) if f["severity"] == "error"]


def sheet(out, frames, dst):
    snap = out / ".hyperframes" / "kit"
    subprocess.run(HF + ["snapshot", str(out), "--frames", str(frames), "-o", str(snap)], capture_output=True, text=True)
    pngs = sorted(snap.glob("*.png"), key=lambda p: p.stat().st_mtime)
    shots = [p for p in pngs if "contact" not in p.name and "sheet" not in p.name]
    if not shots: return None
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in shots]
    w = 640 if ims[0].width >= ims[0].height else 300
    ims = [im.resize((w, round(im.height * w / im.width))) for im in ims]
    cols = 3 if w == 640 else 4
    rows = (len(ims) + cols - 1) // cols
    h = ims[0].height
    board = Image.new("RGB", (cols * w + (cols + 1) * 12, rows * h + (rows + 1) * 12), (24, 24, 24))
    for i, im in enumerate(ims):
        board.paste(im, (12 + (i % cols) * (w + 12), 12 + (i // cols) * (h + 12)))
    dst.parent.mkdir(parents=True, exist_ok=True)
    board.save(dst, quality=88)
    return dst


def cmd_preview(a):
    sid = a.id
    if not (STYLES / f"{sid}.py").exists(): raise SystemExit(f"没有风格 {sid!r}")
    tag = a.aspect.replace(":", "x")
    vids = [showcase(sid)] + ([fx_reel(sid)] if fx_reel(sid) and not a.film_only else [])
    for v in vids:
        if a.render:
            subprocess.run([PY, str(HERE / "render.py"), str(v), "--styles", sid, "--aspect", a.aspect, "--preview"], check=True)
            print("  成片：", (v.parent / "renders" / f"{sid}_{tag}.mp4").relative_to(SKILL))
            continue
        out = build(v, sid, a.aspect)
        dst = v.parent / "previews" / f"{sid}_{tag}_sheet.jpg"
        got = sheet(out, 9 if "styled-" in v.parent.name else 6, dst)
        print(f"  {v.parent.name:<16} 静帧：{got.relative_to(SKILL) if got else '（截图失败，直接打开构建目录看）'}")
        print(f"  {'':<16} 构建：{out.relative_to(SKILL)}   实时预览：cd {out.relative_to(SKILL)} && npx --yes hyperframes@0.8.191 preview")


def safe_text(out, sid):
    """9:16 safe-area probe (scripts/h9/safearea.cjs) over a built example, twice per beat (settled, and just before the
    cut): readable text under the platform's top tabs, bottom bar or right-hand buttons. Furniture listed in
    stress.SAFE_EXEMPT, the style's STYLE["safe_exempt"] and data-safe="ignore" are skipped. [] when Chrome is missing."""
    import stress
    tl = json.loads((out / "timeline.json").read_text())
    at = []
    for x in tl["beats"]:
        at.append(round(x["t"] + x["d"] * 0.55, 2))
        at.append(round(max(x["t"], x["t"] + x["d"] - 0.35), 2))
    found = stress.safe_area(f"style:{sid}", sid, out, at, 1.0)
    out_ = []
    for f in found:
        out_.append(re.sub(r"^v\d+ safe ", "", f))
    return out_


def cmd_check(a):
    sid = a.id
    p = STYLES / f"{sid}.py"
    if not p.exists(): raise SystemExit(f"没有风格 {sid!r}")
    m = derive.load_base(sid)
    S = m.STYLE
    probs, notes = [], []
    for role, fid in (S.get("fonts") or {}).items():
        for f in (fid if isinstance(fid, list) else [fid]):
            if f not in fonts.REG: probs.append(f"字体 {role}={f!r} 不在 assets/fonts.json 里")
    for fid, fname, url in fonts.missing(S):      # registered but not on this machine: the build silently uses a system face
        print(f"  ! 字体 {fid}（{fname}）本机找不到：构建会退回系统字体，看到的不是这个风格的样子。{fonts.HOW}" + (f"；下载：{url}" if url else ""))
    tok = S.get("tokens", {})
    from h9.aefx import _contrast
    for fg, bg, need in (("fg", "bg", 4.5), ("card-fg", "card", 4.5), ("cap-fg", "cap-bg", 4.5), ("accent", "bg", 3.0)):
        if fg in tok and bg in tok:
            r = _contrast(tok[fg], tok[bg])
            if r < need: probs.append(f"{fg} 对 {bg} 对比度 {r:.1f}:1（至少 {need}:1）")
    base = getattr(m, "BASE", None)
    if base:
        B = derive.load_base(base).STYLE
        if S.get("fx_themes") and S.get("fx_themes") == B.get("fx_themes") and tok != B.get("tokens"):
            notes.append("颜色改了但 fx_themes 还是底稿的：动效页会是底稿配色（换成 None 让它跟着 tokens 走，或者手动改）")
        if tok == B.get("tokens") and S.get("fonts") == B.get("fonts") and S.get("css", "").strip() == B.get("css", "").strip():
            notes.append(f"和 {base} 还完全一样：至少改颜色、字体或质感，不然不算新风格")
    v = showcase(sid)
    for aspect in ("16:9", "9:16"):
        out = build(v, sid, aspect)
        errs = hf_errors(out)
        print(f"  构建 {v.parent.name} {aspect}：{'通过' if not errs else f'{len(errs)} 个错误'}")
        probs += [f"{aspect} {e}" for e in errs]
        if aspect == "9:16":          # captions must sit clear of the platform's bottom bar, top tabs and right-hand buttons
            import review
            safe, span = review.caption_safety(out)
            if span:
                print("  9:16 字幕位置：" + " · ".join(f"{'字幕' if k == 'cap' else '效果页字幕'} y {a}–{b}" for k, (a, b) in span.items()))
            probs += [f"9:16 {msg}" for lv, rule, msg in safe if lv == "P0"]
            notes += [msg for lv, rule, msg in safe if lv != "P0"]
            for f in safe_text(out, sid):          # every readable text of the example film clear of the platform chrome
                probs.append(f"9:16 安全区 {f}")
    for x in notes: print("  提示：", x)
    for x in probs: print("  问题：", x)
    print("检查通过" if not probs else f"{len(probs)} 个问题要改")
    if probs: raise SystemExit(1)


def cmd_publish(a):
    """render the showcase film in both aspects into assets/previews, so the gallery's style wall picks it up."""
    sid = a.id
    v = showcase(sid)
    dst = SKILL / "assets" / "previews"
    for aspect in ("16:9", "9:16"):
        tag = aspect.replace(":", "x")
        subprocess.run([PY, str(HERE / "render.py"), str(v), "--styles", sid, "--aspect", aspect, "--preview", "--gate"], check=True)
        for ext in ("mp4", "jpg"):
            src = v.parent / "previews" / f"{sid}_{tag}.{ext}"
            if src.exists(): shutil.copy2(src, dst / f"{sid}_{tag}.{ext}")
    print(f"已放进 assets/previews/{sid}_16x9 / _9x16。再跑  python3 scripts/catalog.py  更新画廊。")


def main():
    ap = argparse.ArgumentParser(prog="style_kit", description="自定义风格：派生、预览、检查、进画廊")
    sp = ap.add_subparsers(dest="cmd", required=True)
    n = sp.add_parser("new", help="从现有风格派生")
    n.add_argument("id"); n.add_argument("--from", dest="base", required=True); n.add_argument("--name"); n.add_argument("--fits")
    n.add_argument("--copy", action="store_true", help="整份复制底稿（要改场景代码时用）"); n.add_argument("--force", action="store_true")
    n.set_defaults(fn=cmd_new)
    p = sp.add_parser("preview", help="构建示例片 + 动效片，出静帧拼图")
    p.add_argument("id"); p.add_argument("--aspect", default="16:9"); p.add_argument("--render", action="store_true"); p.add_argument("--film-only", action="store_true")
    p.set_defaults(fn=cmd_preview)
    c = sp.add_parser("check", help="字体、对比度、横竖屏构建"); c.add_argument("id"); c.set_defaults(fn=cmd_check)
    u = sp.add_parser("publish", help="渲染预览片放进画廊"); u.add_argument("id"); u.set_defaults(fn=cmd_publish)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
