"""Glyph outlines for real 3D text: font file -> {char: {"a": advance, "p": [[op, x, y, ...], ...]}} in em units (1 em = 1.0).

Three.js builds Shapes from these paths and extrudes them (bevel, metal/glass materials, real light).
Variable fonts are instanced first (e.g. wght=900) so heavy CJK titles keep their weight.
"""
from pathlib import Path


def outlines(font_path, text, axes=None):
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    if not font_path or not Path(str(font_path)).exists():     # fonts.find() gave None: say which file and how to fix it
        from h9 import fonts
        fonts.need(None if not font_path else Path(str(font_path)).name)
    f = TTFont(str(font_path))
    if axes and "fvar" in f:
        from fontTools.varLib import instancer
        f = instancer.instantiateVariableFont(f, axes)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    gs = f.getGlyphSet()
    out = {}
    for ch in sorted(set(text)):
        if ch.isspace() or ord(ch) not in cmap: continue
        name = cmap[ord(ch)]
        pen = DecomposingRecordingPen(gs)   # composite glyphs (common in calligraphy fonts) become plain contours
        gs[name].draw(pen)
        cmds = []
        for op, pts in pen.value:
            flat = [round(c / upm, 4) for p in pts for c in p]
            if op == "moveTo": cmds.append(["M", *flat])
            elif op == "lineTo": cmds.append(["L", *flat])
            elif op == "qCurveTo":   # may hold several implied on-curve points: split into single quads
                pts_n = [(round(x / upm, 4), round(y / upm, 4)) for x, y in pts]
                ctrl = pts_n[:-1]; end = pts_n[-1]
                for i, c in enumerate(ctrl):
                    nxt = end if i == len(ctrl) - 1 else ((c[0] + ctrl[i + 1][0]) / 2, (c[1] + ctrl[i + 1][1]) / 2)
                    cmds.append(["Q", c[0], c[1], round(nxt[0], 4), round(nxt[1], 4)])
            elif op == "curveTo": cmds.append(["C", *flat])
            elif op in ("closePath", "endPath"): cmds.append(["Z"])
        out[ch] = {"a": round(gs[name].width / upm, 4), "p": cmds}
    return out
