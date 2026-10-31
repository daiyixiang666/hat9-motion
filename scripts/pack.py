#!/usr/bin/env python3
"""Pack the whole skill into ONE portable file (and a zip), so it can be handed to any assistant.

  python3 scripts/pack.py            -> dist/hat9-motion.skill.md  +  dist/hat9-motion.zip

The .skill.md is plain Markdown: a short guide on top, then every text file of the skill as a fenced block
headed by a `hat9-file` comment. A chat-only assistant (豆包 / DeepSeek web) can read it and write HTML by hand;
an assistant that can run commands unpacks it with the one-liner printed at the top.
Binary files (SFX) are not embedded: `python3 scripts/sfx.py` regenerates them byte-for-byte.
"""
import zipfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
DIST = SKILL / "dist"
TEXT = {".md", ".py", ".json", ".css", ".js", ".mjs", ".html", ".txt"}
SKIP = {"dist", "build", "renders", "previews", "research", "__pycache__", ".hyperframes"}

MARK = "<!-- hat9" + "-file: "      # split so this source file never contains the marker itself
UNPACK = r'''python3 - <<'PY'
import re, pathlib, sys
src = pathlib.Path("hat9-motion.skill.md").read_text(encoding="utf-8")
M = "<!-- hat9" + "-file: "
for path, body in re.findall(re.escape(M) + r"(\S+) -->\n````[a-z]*\n(.*?)\n```` *\n", src, re.S):
    p = pathlib.Path("hat9-motion") / path; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(body + "\n", encoding="utf-8")
pathlib.Path("hat9-motion/SKILL.md").write_text(src.split("\n---\n\n# 单文件包说明")[0] + "\n", encoding="utf-8")
print("unpacked -> hat9-motion/ ; then: python3 hat9-motion/scripts/sfx.py")
PY'''


def files():
    for p in sorted(SKILL.rglob("*")):
        rel = p.relative_to(SKILL)
        if p.is_dir() or any(part in SKIP for part in rel.parts) or rel.parts[0].startswith("."): continue
        if rel.parts[0] == "examples" and p.suffix not in {".json", ".md"}: continue
        yield p, rel


def main():
    DIST.mkdir(exist_ok=True)
    lang = {".py": "python", ".json": "json", ".md": "markdown", ".css": "css", ".js": "js", ".mjs": "js", ".html": "html"}
    head = (SKILL / "SKILL.md").read_text()
    parts = [head, "\n---\n\n# 单文件包说明\n\n这是九帽动效的完整单文件版。能执行命令的助手：把本文件存为 `hat9-motion.skill.md`，运行：\n\n```bash\n" + UNPACK + "\n```\n\n"
             "不能执行命令的助手：直接阅读下面的 references、styles、scenes，按同样的结构手写一个 HyperFrames `index.html`。\n\n# 文件\n"]
    n = 0
    for p, rel in files():
        if p.suffix not in TEXT or rel.as_posix() == "SKILL.md": continue
        parts.append(f"\n{MARK}{rel.as_posix()} -->\n````{lang.get(p.suffix, '')}\n{p.read_text().rstrip()}\n````\n")
        n += 1
    out = DIST / "hat9-motion.skill.md"
    out.write_text("".join(parts))
    with zipfile.ZipFile(DIST / "hat9-motion.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p, rel in files(): z.write(p, f"hat9-motion/{rel.as_posix()}")
    print(f"{out}  ({n} files, {out.stat().st_size // 1024} KB)  +  {DIST / 'hat9-motion.zip'}")


if __name__ == "__main__":
    main()
