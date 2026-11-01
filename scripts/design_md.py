#!/usr/bin/env python3
"""DESIGN.md -> a hat9 style: your brand's colours, type and radius on top of an existing style's scenes.

  python3 scripts/design_md.py examples/brand/DESIGN.md --name qingzhou [--base press|reel] [--tokens tokens.css]
      -> styles/brand_qingzhou.py      then:  python3 scripts/build.py <video.json> --style brand_qingzhou

Reads the DESIGN.md layout used by OpenDesign's design systems (Apache-2.0, `design-systems/_schema`):
  ## … Color        bullets  "- **Primary:** `#0F7B6C` — …"   (Primary / Secondary / Background / Surface / Text / Muted / Border / Danger …)
  ## … Typography   "- **Families:** primary=…, display=…, mono=…"  or  "- **Display:** …" bullets;  "radius" anywhere, e.g. "**Radius:** 6px"
and, when present, a sibling tokens.css (or a ```css block in the file) with --bg / --fg / --accent / --font-display / --radius-md …
Only fonts in assets/fonts.json can be used (OFL); unknown families are reported and the base style's font stays.
Python standard library only.
"""
import argparse, json, re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
REG = json.loads((SKILL / "assets" / "fonts.json").read_text())
CJK = {"noto-sans-sc", "noto-serif-sc", "lxgw-wenkai", "smiley-sans", "zcool-kuaile", "zcool-xiaowei", "zcool-qingke", "ma-shan-zheng", "long-cang"}
ALIAS = {"思源黑体": "noto-sans-sc", "source han sans": "noto-sans-sc", "sourcehansans": "noto-sans-sc", "思源宋体": "noto-serif-sc",
         "source han serif": "noto-serif-sc", "霞鹜文楷": "lxgw-wenkai", "得意黑": "smiley-sans", "马善政": "ma-shan-zheng"}
ROLES = {   # DESIGN.md colour label -> hat9 token role
    "accent": ["primary", "accent", "brand", "主色", "强调"], "accent2": ["secondary", "辅色", "辅助", "次要色"],
    "bg": ["background", "canvas", "bg", "背景", "底色"], "card": ["surface", "card", "卡片", "表面"],
    "fg": ["text", "foreground", "ink", "文字", "正文"], "muted": ["muted", "subtle", "caption", "次要文字", "说明"],
    "line": ["border", "line", "divider", "rule", "边框", "分隔"], "alert": ["danger", "error", "警示", "危险"], "neutral": ["neutral", "中性"],
}


def norm(s): return re.sub(r"[\s_\-\[\]().,]|regular|vf|variable|opsz|wght|wdth|soft|wonk", "", s.lower())


FONT_INDEX = {norm(Path(m["file"]).stem.split("[")[0]): fid for fid, m in REG.items()}


def font_id(family):
    f = family.strip().strip("'\"`")
    if f in ALIAS or f.lower() in ALIAS: return ALIAS.get(f) or ALIAS[f.lower()]
    n = norm(f)
    return FONT_INDEX.get(n) or next((fid for k, fid in FONT_INDEX.items() if k.startswith(n) or n.startswith(k) and len(k) > 4), None)


def section(md, *names):
    for m in re.finditer(r"^##\s+(.+?)\n(.*?)(?=^##\s|\Z)", md, re.M | re.S):
        if any(n.lower() in m.group(1).lower() for n in names): return m.group(2)
    return ""


def lum(h):
    h = h.lstrip("#"); h = "".join(c * 2 for c in h) if len(h) == 3 else h
    ch = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    ch = [c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4 for c in ch]
    return .2126 * ch[0] + .7152 * ch[1] + .0722 * ch[2]


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def parse(md, css=""):
    out = {"colors": {}, "fonts": {}, "radius": None, "name": None}
    h1 = re.search(r"^#\s+(.+)$", md, re.M)
    if h1: out["name"] = re.sub(r"^design system (inspired by )?", "", h1.group(1).strip(), flags=re.I)
    for label, hexv in re.findall(r"^\s*[-*]\s*\*\*([^*:]+):?\*\*:?\s*`?(#[0-9a-fA-F]{3,6})\b", section(md, "color", "colour", "颜色", "配色") or md, re.M):
        low = label.strip().lower()
        role = next((r for r, keys in ROLES.items() if any(k in low for k in keys)), None)
        if role and role not in out["colors"]: out["colors"][role] = hexv.lower()
    typo = section(md, "typography", "type", "字体") or md
    fam = re.search(r"\*\*Families:?\*\*:?\s*(.+)", typo)
    if fam:
        for k, v in re.findall(r"(\w+)\s*=\s*([^,\n]+)", fam.group(1)): out["fonts"][k.lower()] = v.strip()
    for label, v in re.findall(r"^\s*[-*]\s*\*\*(Display|Heading|Body|Mono|Latin|Primary|标题|正文|等宽)[^*]*\*\*:?\s*(.+)$", typo, re.M):
        key = {"标题": "display", "heading": "display", "正文": "body", "等宽": "mono"}.get(label.lower(), label.lower())
        out["fonts"].setdefault(key, v.split("—")[0].split("（")[0].strip().strip("`"))
    r = re.search(r"radius[^0-9\n]{0,24}(\d+(?:\.\d+)?)\s*px", md, re.I)
    if r: out["radius"] = f"{r.group(1)}px"
    # tokens.css wins where it speaks
    block = css or "\n".join(re.findall(r"```css\n(.*?)```", md, re.S))
    tok = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);", block))
    for k, role in (("bg", "bg"), ("surface", "card"), ("fg", "fg"), ("muted", "muted"), ("border", "line"), ("accent", "accent"), ("danger", "alert")):
        if re.fullmatch(r"#[0-9a-fA-F]{3,6}", tok.get(k, "").strip()): out["colors"][role] = tok[k].strip().lower()
    for k, role in (("font-display", "display"), ("font-body", "body"), ("font-mono", "mono")):
        if tok.get(k): out["fonts"][role] = tok[k].split(",")[0].strip().strip("'\"")
    if tok.get("radius-md"): out["radius"] = tok["radius-md"].strip()
    return out


def tokens_for(base, d):
    c = d["colors"]
    bg = c.get("bg") or c.get("neutral"); fg = c.get("fg"); acc = c.get("accent")
    t = {}
    if bg: t.update(bg=bg, paper=bg)
    if fg: t.update(fg=fg, ink=fg, **{"card-fg": fg})
    if c.get("muted"): t["muted"] = c["muted"]
    if c.get("line"): t["line"] = c["line"]
    if c.get("card"): t["card"] = c["card"]
    if acc: t.update(accent=acc, alert=c.get("alert", acc))
    if c.get("accent2"): t["accent2"] = c["accent2"]
    if base == "press":      # press scenes paint with --red / --lemon / --white / --ink directly
        if acc: t["red"] = acc
        if c.get("accent2"): t["lemon"] = c["accent2"]
        if c.get("card"): t["white"] = c["card"]
        if fg: t["cap-bg"] = fg
        if bg: t["cap-fg"] = bg
        if c.get("accent2"): t["cap-em"] = c["accent2"]
    if d["radius"]: t.update(radius=d["radius"], **{"cap-radius": d["radius"]})
    return t


def fonts_for(base_fonts, d, warn):
    f = dict(base_fonts)
    want = {"display": d["fonts"].get("display") or d["fonts"].get("primary"), "body": d["fonts"].get("body") or d["fonts"].get("primary"),
            "mono": d["fonts"].get("mono")}
    for role, fam in want.items():
        if not fam: continue
        fid = font_id(fam)
        if not fid: warn.append(f"字体「{fam}」不在 assets/fonts.json（只能用 OFL 字体），{role} 保持原风格的字体"); continue
        if role in ("display", "body") and fid not in CJK:    # a Latin face still needs a Chinese fallback inside the stack
            cjk = "noto-serif-sc" if REG[fid].get("fallback", "").lower().find("serif") >= 0 and "sans" not in REG[fid].get("fallback", "").lower() else "noto-sans-sc"
            f[role] = [fid, cjk]
        else:
            f[role] = fid
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design_md"); ap.add_argument("--name", required=True); ap.add_argument("--base", default="press", choices=["press", "reel"])
    ap.add_argument("--tokens", help="tokens.css (default: next to DESIGN.md if present)")
    ap.add_argument("--brand-json", help="also write a style-independent brand.json (use with meta.brand on ANY style)")
    a = ap.parse_args()
    src = Path(a.design_md); md = src.read_text(encoding="utf-8")
    tk = Path(a.tokens) if a.tokens else src.with_name("tokens.css")
    d = parse(md, tk.read_text(encoding="utf-8") if tk.exists() else "")
    slug = re.sub(r"[^a-z0-9_]", "_", a.name.lower()); sid = f"brand_{slug}"
    import importlib.util
    spec = importlib.util.spec_from_file_location("_base", SKILL / "styles" / f"{a.base}.py"); base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
    warn = []
    tokens = tokens_for(a.base, d)
    fonts = fonts_for(base.STYLE["fonts"], d, warn)
    merged = {**base.STYLE["tokens"], **tokens}
    for fgk, bgk, need, what in (("fg", "bg", 4.5, "正文对底色"), ("accent", "bg", 3.0, "强调色对底色")):
        if merged.get(fgk, "").startswith("#") and merged.get(bgk, "").startswith("#"):
            r = contrast(merged[fgk], merged[bgk])
            if r < need: warn.append(f"{what}对比度只有 {r:.1f}:1（建议 ≥ {need}:1），画面上会发灰")
    missing = [k for k in ("bg", "fg", "accent") if k not in tokens]
    if missing: warn.append(f"DESIGN.md 里没找到 {', '.join(missing)}，沿用 {a.base} 的值")
    out = SKILL / "styles" / f"{sid}.py"
    out.write_text(f'''"""{sid} · {d["name"] or a.name} — generated by scripts/design_md.py from {src.as_posix()}; base style: {a.base}.
Re-run the script after editing DESIGN.md instead of editing this file by hand."""
import importlib.util as _u
from pathlib import Path as _P

_s = _u.spec_from_file_location("_base_{a.base}", _P(__file__).with_name("{a.base}.py"))
_b = _u.module_from_spec(_s); _s.loader.exec_module(_b)
for _k, _v in list(vars(_b).items()):          # the base scopes a few rules to its own root class; re-point them here
    if isinstance(_v, str) and ".st-{a.base}" in _v: setattr(_b, _k, _v.replace(".st-{a.base}", ".st-{sid}"))

STYLE = {{**_b.STYLE, "name": {json.dumps((d["name"] or a.name) + "（品牌）", ensure_ascii=False)}, "en": {json.dumps(sid)},
         "tokens": {{**_b.STYLE["tokens"], **{json.dumps(tokens, ensure_ascii=False)}}},
         "fonts": {json.dumps(fonts, ensure_ascii=False)},
         "css": _b.STYLE.get("css", "").replace(".st-{a.base}", ".st-{sid}")}}
SCENES = getattr(_b, "SCENES", {{}})
if hasattr(_b, "WORLD"): WORLD = _b.WORLD
''', encoding="utf-8")
    if a.brand_json:
        c = d["colors"]
        brand = {"name": d["name"] or a.name, "source": src.as_posix(),
                 "colors": {k: v for k, v in {"bg": c.get("bg") or c.get("neutral"), "fg": c.get("fg"), "muted": c.get("muted"), "line": c.get("line"),
                                             "card": c.get("card"), "accent": c.get("accent"), "accent2": c.get("accent2"), "alert": c.get("alert")}.items() if v},
                 "fonts": {k: fonts[k] for k in ("display", "body", "mono") if k in fonts and fonts[k] != base.STYLE["fonts"].get(k)},
                 "tokens": {k: v for k, v in (("radius", d["radius"]), ("cap-radius", d["radius"])) if v}}
        Path(a.brand_json).write_text(json.dumps(brand, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{a.brand_json}  (brand.json for meta.brand)")
    print(f"{out}  ({len(tokens)} tokens from DESIGN.md, base {a.base})")
    for k, v in tokens.items(): print(f"  --{k}: {v}")
    print("  fonts:", json.dumps({k: fonts[k] for k in ("display", "body", "mono") if k in fonts}, ensure_ascii=False))
    for w in warn: print("  !", w)


if __name__ == "__main__":
    main()
