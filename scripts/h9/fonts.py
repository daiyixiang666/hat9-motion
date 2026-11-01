"""Font roles -> @font-face. Fonts are looked up by file name in the search roots, then subset to the
glyphs actually used (needs fontTools; without it the whole file is copied)."""
import json, os, shutil
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2]
REG = json.loads((SKILL / "assets" / "fonts.json").read_text())


def roots():
    r = [SKILL / "assets" / "fonts"]
    r += [Path(p) for p in os.environ.get("H9_FONT_DIRS", "").split(os.pathsep) if p]
    r += [*([Path(os.environ["H9_MEDIA"]) / "fonts"] if os.environ.get("H9_MEDIA") else []), Path.home() / "Library/Fonts", Path("/Library/Fonts"),
          Path.home() / ".fonts", Path("/usr/share/fonts"), Path("C:/Windows/Fonts")]
    return [p for p in r if p.exists()]


def find(fname):
    for r in roots():
        p = r / fname
        if p.exists(): return p
        for dp, _, fs in os.walk(r):
            if fname in fs: return Path(dp) / fname
    return None


def build(X, text):
    """returns CSS: @font-face rules + role variables (--f-display etc.)."""
    faces, roles = [], {}
    out = X.out / "assets" / "fonts"; out.mkdir(parents=True, exist_ok=True)
    chars = "".join(sorted(set(text))) + "".join(chr(c) for c in range(32, 127)) + "，。、：；！？“”‘’（）《》·—…「」"
    done = {}
    # other scripts: the language's font joins every role's stack (optional fonts; the system font covers a missing file)
    lang = X.v.get("meta", {}).get("lang", "zh")
    extra = {"ja": "noto-sans-jp", "ko": "noto-sans-kr", "zh-TW": "noto-sans-tc", "zh-HK": "noto-sans-tc",
             "ar": "noto-sans-arabic", "fa": "noto-sans-arabic", "ur": "noto-sans-arabic", "he": "noto-sans-hebrew"}.get(lang)
    for role, ids in X.S.get("fonts", {}).items():
        ids = ids if isinstance(ids, list) else [ids]
        if extra and extra not in ids: ids = ids + [extra]
        stack = []
        for fid in ids:
            meta = REG.get(fid)
            if not meta: raise SystemExit(f"unknown font id {fid!r} (see assets/fonts.json)")
            fam = f"h9-{fid}"
            if fid not in done:
                src = find(meta["file"])
                if not src:
                    if not meta.get("optional") or fid == extra:
                        print(f"  ! font {fid} ({meta['file']}) not found — falls back to {meta.get('fallback', 'sans-serif')}. Get it: {meta.get('url', '')}")
                    done[fid] = None
                else:
                    dst = out / f"{fid}.ttf"
                    try:
                        from fontTools import subset
                        opts = subset.Options(); opts.layout_features = ["*"]; opts.notdef_outline = True
                        f = subset.load_font(str(src), opts)
                        s = subset.Subsetter(opts); s.populate(text=chars); s.subset(f)
                        subset.save_font(f, str(dst), opts)
                    except ImportError:
                        shutil.copy2(src, dst)
                    w = meta.get("weight", "400")
                    st = meta.get("style", "normal")
                    faces.append(f"@font-face {{ font-family:'{fam}'; src:url('assets/fonts/{fid}.ttf'); font-weight:{w}; font-style:{st}; }}")
                    done[fid] = fam
            if done[fid]: stack.append(f"'{done[fid]}'")
        stack.append(REG.get(ids[-1], {}).get("fallback", "sans-serif") if not extra else REG.get(extra, {}).get("fallback", "sans-serif") + ", " + REG.get(ids[0], {}).get("fallback", "sans-serif"))
        roles[role] = ", ".join(stack)
    css = "\n".join(faces) + "\n:root { " + " ".join(f"--f-{k}:{v};" for k, v in roles.items()) + " }"
    return css
