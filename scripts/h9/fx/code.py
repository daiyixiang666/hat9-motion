"""代码 / 终端 (code typing · Askiko Typewriter Text Effect 113.3 万播放; 「代码动画」趋势 — MoSidd Vox-style with Claude Code
25.1 万): an editor window types the code line by line with a caret (or reveals it), then lights the lines being talked
about while the rest dims; `diff` strikes the removed lines red and wipes the added ones in green; `terminal` types a
command and streams its output.

p: code (text) | file ("path#L10-L40", relative to video.json or the skill) · lang (python | js | bash | json | css | html;
   default from the file) · title (file name) · mode ("type" | "lines" | "diff" | "terminal"; default type, lines for long code)
   · hl (line numbers: [3, 4] or "3-5") · at_hl · cmd / output (terminal) · prompt ("$")
Adapts: 1–60+ lines (font solved for the window; past ~32 lines the view scrolls with the caret), lines up to ~110
characters (longer ones run under a fade), any title length; 16:9 and 9:16 windows sized separately.
"""
import importlib.util, pathlib, re, sys, unicodedata
from h9 import fit
from h9.aefx import _clip
from h9.core import esc


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


S = _load("_screens")
SKILL = pathlib.Path(__file__).resolve().parents[3]

KW = {
    "python": "def class return if elif else for while in import from as with try except finally lambda None True False and or not yield pass break continue raise global async await is",
    "js": "const let var function return if else for while import from export default class new this async await true false null undefined of in typeof",
    "bash": "if then fi for do done case esac in export echo cd sudo npm npx pip python3 node git brew",
    "css": "", "json": "true false null", "html": "",
}
EXT = {".py": "python", ".js": "js", ".mjs": "js", ".ts": "js", ".sh": "bash", ".json": "json", ".css": "css", ".html": "html"}


def cols(s):
    """terminal columns: CJK / fullwidth glyphs take two."""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))


def _tok(line, lang):
    """→ html with .k .s .n .c .f spans (one pass, regex alternation; deterministic)."""
    kws = KW.get(lang, "").split()
    com = r"#.*$" if lang in ("python", "bash") else (r"//.*$|/\*.*?\*/" if lang in ("js", "css") else r"<!--.*?-->")
    pat = re.compile(rf"(?P<c>{com})|(?P<s>[fbr]?\"(?:\\.|[^\"\\])*\"|[fbr]?'(?:\\.|[^'\\])*'|`[^`]*`)|(?P<n>\b\d+(?:\.\d+)?\b)"
                     rf"|(?P<w>[A-Za-z_][A-Za-z0-9_]*)(?P<p>\s*\()?|(?P<o>[{{}}()\[\],.:;=+\-*/<>!&|%@]+)")
    out, i = [], 0
    for m in pat.finditer(line):
        out.append(esc(line[i:m.start()])); i = m.end()
        g = m.lastgroup
        if m.group("c") is not None: out.append(f'<span class="c">{esc(m.group(0))}</span>')
        elif m.group("s") is not None: out.append(f'<span class="s">{esc(m.group(0))}</span>')
        elif m.group("n") is not None: out.append(f'<span class="n">{esc(m.group(0))}</span>')
        elif m.group("w") is not None:
            w = m.group("w"); tail = m.group("p") or ""
            cls = "k" if w in kws else ("f" if tail else "")
            out.append((f'<span class="{cls}">{esc(w)}</span>' if cls else esc(w)) + esc(tail))
        else: out.append(f'<span class="o">{esc(m.group(0))}</span>')
    out.append(esc(line[i:]))
    return "".join(out)


def _source(X, p):
    if p.get("code") is not None:
        return str(p["code"]).replace("\t", "    ").rstrip("\n").split("\n"), p.get("lang", "python"), p.get("title", "")
    spec = str(p.get("file") or p.get("path") or "")
    if not spec: raise SystemExit("code needs `code` (text) or `file` (\"path#L10-L40\")")
    path, _, rng = spec.partition("#")
    f = pathlib.Path(path)
    if not f.is_absolute():
        f = (X.src / path) if (X.src / path).exists() else (SKILL / path)
    lines = f.read_text().replace("\t", "    ").split("\n")
    m = re.match(r"L(\d+)(?:-L?(\d+))?", rng)
    first = 1
    if m:
        a, b = int(m.group(1)), int(m.group(2) or m.group(1)); first = a
        lines = lines[a - 1:b]
    while lines and not lines[-1].strip(): lines.pop()
    return lines, p.get("lang", EXT.get(f.suffix, "python")), p.get("title", f.name), first


def _hl_set(v):
    out = set()
    for x in fit.as_list(v, ","):
        x = str(x).strip()
        if "-" in x: a, b = x.split("-", 1); out.update(range(int(a), int(b) + 1))
        elif x: out.add(int(x))
    return out


def code(X, cid, t, d, p):
    P = X.portrait
    mode = p.get("mode", "type")
    first = 1
    if mode == "terminal":
        cmd = str(p.get("cmd", ""))
        out_lines = [str(x) for x in fit.as_list(p.get("output"), "\n")] if isinstance(p.get("output"), str) else [str(x) for x in fit.as_list(p.get("output"))]
        lines = [cmd] + out_lines; lang = "bash"; title = p.get("title", "Terminal")
    else:
        src = _source(X, p)
        lines, lang, title = src[0], src[1], src[2]
        if len(src) > 3: first = src[3]
    if mode == "type" and sum(len(l) for l in lines) > 1100: mode = "lines"
    diff = mode == "diff"
    signs = []
    if diff:
        for i, l in enumerate(lines):
            sg = l[:1] if l[:1] in "+-" else " "
            signs.append(sg); lines[i] = l[1:] if sg != " " else l
    n = len(lines)
    L = max([cols(l) for l in lines] + [12])
    x0, y0, x1, y1 = S.area(X, p)
    aw, ah = x1 - x0, y1 - y0
    bar, padv, padh = 52, 26, 30
    digits = len(str(first + n - 1)) if mode != "terminal" else 0
    gut = (digits + 1.6 if digits else 0) + (1.6 if diff else 0)          # gutter width in ch (1ch = .6em in the mono face)
    maxw, maxh = aw * (0.96 if P else 0.86), ah
    px = min(34 if not P else 30, (maxw - 2 * padh) / ((L + gut) * 0.6), (maxh - bar - 2 * padv) / (min(n, 34) * 1.55))
    px = max(16.0 if not P else 15.0, px)
    vis = int((maxh - bar - 2 * padv) // (px * 1.55))
    scroll = n > vis
    lh = px * 1.55
    ww = min(maxw, (min(L, 110) + gut) * 0.6 * px + 2 * padh + 8)
    ww = max(ww, min(maxw, 760 if not P else 640))
    wh = min(maxh, bar + 2 * padv + min(n, vis) * lh)
    wx, wy = x0 + (aw - ww) / 2, y0 + (ah - wh) / 2
    hl = _hl_set(p.get("hl"))
    rows = []
    for i, l in enumerate(lines):
        num = first + i
        g = f'<b class="cd-n">{num}</b>' if digits else ""
        if diff: g += f'<b class="cd-sg">{"+" if signs[i] == "+" else ("−" if signs[i] == "-" else "")}</b>'
        if mode == "terminal":
            body = (f'<span class="cd-pr">{esc(p.get("prompt", "$"))}</span> ' + _tok(l, "bash")) if i == 0 else esc(l)
            tone = " ok" if re.match(r"\s*(✓|✔|OK|ok\b|done|Done)", l) else (" bad" if re.match(r"\s*(✗|✘|!|error|Error|ERROR|failed)", l) else "")
        else:
            body = _tok(l, lang); tone = ""
        cls = f"cd-l{tone}" + (" add" if diff and signs[i] == "+" else "") + (" del" if diff and signs[i] == "-" else "") + (" hl" if num in hl else "")
        rows.append(f'<div class="{cls}" data-i="{i}" style="height:{lh:.1f}px">{g}<span class="cd-t" data-len="{len(l)}">{body or "&#8203;"}</span>{"<i class=cd-x></i>" if diff and signs[i] == "-" else ""}</div>')
    X.used_text.update(title + "0123456789+−$✓")
    term = mode == "terminal"
    head = f'<div class="cd-bar"><div class="scr-dots"><i></i><i></i><i></i></div><span class="cd-title">{X.rich(title)}</span>{"<em>" + esc(lang) + "</em>" if not term else ""}</div>'
    caret = '<i class="cd-caret"></i>' if mode in ("type", "terminal") else ""
    body = (f'<div class="cd-win{" term" if term else ""}" style="left:{wx:.0f}px; top:{wy:.0f}px; width:{ww:.0f}px; height:{wh:.0f}px; font-size:{px:.1f}px; --g:{max(digits, 1)}">{head}'
            f'<div class="cd-view" style="top:{bar}px; padding:{padv}px {padh}px"><div class="cd-code" data-layout-allow-overflow>{"".join(rows)}{caret}</div>'
            f'{"<i class=cd-fade></i>" if L > 110 else ""}</div></div>')
    X.css("fx-code", """
.cd-win { position:absolute; border-radius:14px; background:#0f1218; color:#d9d4c7; box-shadow:0 0 0 1px rgba(255,255,255,.08), 0 30px 80px rgba(0,0,0,.4); overflow:hidden; }
.cd-win.term { background:#07090c; }
.cd-bar { position:absolute; left:0; right:0; top:0; height:52px; display:flex; align-items:center; gap:14px; padding:0 18px; background:rgba(255,255,255,.04); border-bottom:1px solid rgba(255,255,255,.06); }
.cd-bar .scr-dots { display:flex; gap:8px; } .cd-bar .scr-dots i { width:12px; height:12px; border-radius:50%; background:#3a3e45; }
.cd-bar .scr-dots i:nth-child(1) { background:#ff5f57; } .cd-bar .scr-dots i:nth-child(2) { background:#febc2e; } .cd-bar .scr-dots i:nth-child(3) { background:#28c840; }
.cd-title { font:600 17px var(--f-mono, monospace); color:#e7e2d6; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; min-width:0; }
.cd-bar em { margin-left:auto; font:500 14px var(--f-mono, monospace); font-style:normal; color:#8b8f96; text-transform:uppercase; letter-spacing:.1em; }
.cd-view { position:absolute; left:0; right:0; bottom:0; overflow:hidden; }
.cd-code { position:relative; font-family:var(--f-mono, monospace), var(--f-body, sans-serif); white-space:pre; }
.cd-l { position:relative; display:flex; align-items:center; }
.cd-n { flex:none; width:calc(var(--g, 3) * 1ch); text-align:right; margin-right:1.6ch; color:#565c66; font-weight:400; }
.cd-sg { flex:none; width:1.6ch; font-weight:700; } .cd-l.add .cd-sg { color:#7bd88f; } .cd-l.del .cd-sg { color:#ff7b72; }
.cd-t { position:relative; }
.cd-l.add, .cd-l.del { margin:0 -30px; padding:0 30px; }
.cd-l .cd-bg { position:absolute; inset:0; }
.cd-l.del::before, .cd-l.add::before { content:''; position:absolute; inset:0; transform-origin:0 50%; transform:scaleX(var(--w, 0)); }
.cd-l.del::before { background:rgba(255,123,114,.16); } .cd-l.add::before { background:rgba(123,216,143,.16); }
.cd-x { position:absolute; left:5ch; right:30px; top:50%; height:2px; background:#ff7b72; transform-origin:0 50%; }
.cd-win .k { color:#ff8f6b; } .cd-win .s { color:#b8d77e; } .cd-win .n { color:#f2c14e; } .cd-win .c { color:#6b727d; font-style:italic; }
.cd-win .f { color:#7cc4ff; } .cd-win .o { color:#a0a7b4; }
.cd-pr { color:#7bd88f; font-weight:700; } .cd-l.ok { color:#7bd88f; } .cd-l.bad { color:#ff7b72; }
.cd-caret { position:absolute; left:0; top:0; width:.6em; height:1.25em; margin-top:.15em; background:#f6ce3a; opacity:.9; }
.cd-fade { position:absolute; right:0; top:0; bottom:0; width:90px; background:linear-gradient(90deg, rgba(15,18,24,0), #0f1218); }
""")
    _clip(X, cid, t, d, "", p)
    sid = S.stage(X, cid, t, d, body, p)
    s = f"#{sid}"
    X.tw(f'tl.from("{s} .cd-win", {{y:50, scale:0.95, opacity:0, duration:0.6, ease:"expo.out"}}, {t + 0.05:.3f});')
    X.sfx(t + 0.05, "whoosh_soft")
    gx = gut * 0.6 * px                       # where the code text starts (px from the code box's left)
    t0 = t + 0.6
    budget = max(0.8, d * (0.62 if hl else (0.6 if mode == "terminal" else 0.78)) - 0.6)
    def caret_to(i, chars, at, dur=0.0):
        X.tw(f'tl.to("{s} .cd-caret", {{x:{gx + chars * 0.6 * px:.1f}, y:{i * lh:.1f}, duration:{dur:.2f}, ease:"none"}}, {at:.3f});')
    marks = {}                                # line → when it starts; the view scrolls once, linearly, from the first
    def follow(i, at):                        # line that would fall off the bottom to the last one
        marks[i] = at
    if mode == "type":
        tot = sum(max(1, len(l)) for l in lines) + 3 * n
        rate = budget / tot
        ti = t0
        X.tw(f'tl.set("{s} .cd-t", {{clipPath:"inset(0 100% 0 0)"}}, {t:.3f});')
        X.tw(f'tl.set("{s} .cd-n", {{opacity:0}}, {t:.3f});')
        for i, l in enumerate(lines):
            c = max(1, len(l)); dur = c * rate
            X.tw(f'tl.set("{s} .cd-l[data-i=\'{i}\'] .cd-n", {{opacity:1}}, {ti:.3f});')
            X.tw(f'tl.to("{s} .cd-l[data-i=\'{i}\'] .cd-t", {{clipPath:"inset(0 0% 0 0)", duration:{dur:.3f}, ease:"steps({min(c, 60)})"}}, {ti:.3f});')
            caret_to(i, 0, ti); caret_to(i, cols(l), ti, dur)
            follow(i, ti)
            if i % 3 == 0: X.sfx(ti, "type")
            ti += dur + 3 * rate
        t_done = ti
    elif mode == "terminal":
        c = max(1, len(lines[0])); dur = min(1.0, 0.03 * c + 0.2)
        X.tw(f'tl.set("{s} .cd-l:not([data-i=\'0\'])", {{opacity:0}}, {t:.3f});')
        X.tw(f'tl.fromTo("{s} .cd-l[data-i=\'0\'] .cd-t", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:{dur:.2f}, ease:"steps({min(c + 2, 60)})"}}, {t0:.3f});')
        caret_to(0, 2, t0); caret_to(0, cols(lines[0]) + 2, t0, dur)
        X.sfx(t0, "type")
        ti = t0 + dur + 0.35
        step = min(0.22, max(0.05, (budget - dur - 0.35) / max(n - 1, 1)))
        for i in range(1, n):
            X.tw(f'tl.set("{s} .cd-l[data-i=\'{i}\']", {{opacity:1}}, {ti:.3f});')
            caret_to(i, cols(lines[i]), ti)
            follow(i, ti)
            ti += step * (2.5 if i == n - 2 else 1)
        t_done = ti
    elif diff:
        X.tw(f'tl.from("{s} .cd-l:not(.add)", {{opacity:0, y:8, duration:0.35, ease:"power2.out", stagger:{min(0.05, 0.6 / max(n, 1)):.3f}}}, {t0:.3f});')
        X.tw(f'tl.set("{s} .cd-l.add", {{opacity:0}}, {t:.3f});')
        X.tw(f'tl.set("{s} .cd-l.add, {s} .cd-l.del", {{"--w":0}}, {t:.3f});')
        X.tw(f'tl.set("{s} .cd-x", {{scaleX:0}}, {t:.3f});')
        t1 = t0 + 0.9
        X.tw(f'tl.to("{s} .cd-l.del", {{"--w":1, duration:0.4, ease:"power2.out", stagger:0.08}}, {t1:.3f});')
        X.tw(f'tl.to("{s} .cd-l.del .cd-x", {{scaleX:1, duration:0.35, ease:"power3.out", stagger:0.08}}, {t1 + 0.2:.3f});')
        X.tw(f'tl.to("{s} .cd-l.del .cd-t", {{opacity:0.45, duration:0.3}}, {t1 + 0.4:.3f});')
        X.sfx(t1, "click")
        t2 = t1 + 1.0
        X.tw(f'tl.to("{s} .cd-l.add", {{opacity:1, duration:0.25, stagger:0.1}}, {t2:.3f});')
        X.tw(f'tl.to("{s} .cd-l.add", {{"--w":1, duration:0.45, ease:"power2.out", stagger:0.1}}, {t2:.3f});')
        X.tw(f'tl.fromTo("{s} .cd-l.add .cd-t", {{clipPath:"inset(0 100% 0 0)"}}, {{clipPath:"inset(0 0% 0 0)", duration:0.5, ease:"power2.out", stagger:0.1, immediateRender:false}}, {t2:.3f});')
        X.sfx(t2, "pop")
        t_done = t2 + 0.6
    else:   # lines
        st = min(0.12, budget / max(n, 1))
        X.tw(f'tl.from("{s} .cd-l", {{opacity:0, x:-14, duration:0.35, ease:"power3.out", stagger:{st:.3f}}}, {t0:.3f});')
        if scroll:
            X.tw(f'tl.to("{s} .cd-code", {{y:{-(n - vis + 1) * lh:.1f}, duration:{max(0.5, n * st - vis * st):.2f}, ease:"none"}}, {t0 + vis * st:.3f});')
        t_done = t0 + n * st
    scroll_end = t
    if scroll and mode in ("type", "terminal") and marks:
        a_i = vis - 2
        if a_i in marks:
            a_t, b_t = marks[a_i], marks[max(marks)] + 0.2
            X.tw(f'tl.to("{s} .cd-code", {{y:{-(n - vis + 1) * lh:.1f}, duration:{max(0.3, b_t - a_t):.2f}, ease:"none"}}, {a_t:.3f});')
            scroll_end = a_t + max(0.3, b_t - a_t)
    elif scroll and mode == "lines":
        scroll_end = t_done
    if caret:
        reps = int(max(0, (t + d - t_done) / 0.5))
        if reps: X.tw(f'tl.to("{s} .cd-caret", {{opacity:0, duration:0.01, repeat:{reps}, yoyo:true, repeatDelay:0.49}}, {t_done:.3f});')
    if hl:
        th = S.cue(X, p.get("at_hl"), t, max(t_done + 0.2, t + d * 0.62))
        first_hl = min(hl) - first
        if scroll:
            X.tw(f'tl.to("{s} .cd-code", {{y:{-max(0, min(first_hl - 2, n - vis + 1)) * lh:.1f}, duration:0.6, ease:"power3.inOut"}}, {max(th - 0.3, scroll_end + 0.05):.3f});')
        X.tw(f'tl.to("{s} .cd-l:not(.hl)", {{opacity:0.28, duration:0.35}}, {th:.3f});')
        X.tw(f'tl.to("{s} .cd-l.hl", {{backgroundColor:"rgba(246,206,58,.12)", boxShadow:"inset 6px 0 0 #f6ce3a", duration:0.35}}, {th:.3f});')
        X.css("fx-code-hl", ".cd-l.hl { margin:0 -30px; padding:0 30px; }")
        X.sfx(th, "click")


FX = {"code": code}
