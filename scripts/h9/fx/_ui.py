"""shared bits for the UI / product / people effects (app_flow · cursor · form_fill · turntable · search_box ·
relation_graph · dialogue · interview); files starting with _ are not effects.

base()     css for the generic, unbranded UI kit (+ the screen effects' cursor / ripple / tag classes)
area()     content box under the page header and above the caption (same as the screen effects)
typed()    a string as one <i class="tc"> per glyph, so typing can reveal it glyph by glyph
type_in()  the typing tween (one glyph every 1/cps s) + a deterministic caret blink; returns when typing ends
when()     '@词' / seconds into the beat / None → an absolute time
spread()   n evenly spaced moments inside (a, b)
"""
import importlib.util, pathlib, sys
from h9 import fit as FT


def load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        s = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        sys.modules[key] = importlib.util.module_from_spec(s); s.loader.exec_module(sys.modules[key])
    return sys.modules[key]


S = load("_screens")
SO = load("_social")

CSS = r"""
.fx .ui-card { position:absolute; background:var(--card); color:var(--card-fg); border-radius:22px; box-shadow:0 0 0 1px color-mix(in srgb, var(--card-fg) 10%, transparent), 0 30px 80px rgba(0,0,0,.18), 0 6px 18px rgba(0,0,0,.08); }
.fx .ui-lab { font:700 22px var(--f-body); color:color-mix(in srgb, var(--card-fg) 62%, transparent); letter-spacing:.02em; }
.fx .ui-in { position:relative; display:flex; align-items:center; gap:10px; border-radius:12px; background:color-mix(in srgb, var(--card-fg) 5%, var(--card)); box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--card-fg) 14%, transparent);
  font:600 26px var(--f-body); color:var(--card-fg); padding:0 18px; white-space:nowrap; overflow:hidden; }
.fx .ui-in.on { box-shadow:inset 0 0 0 3px var(--accent), 0 0 0 6px color-mix(in srgb, var(--accent) 18%, transparent); }
.fx .ui-in .ph { color:color-mix(in srgb, var(--card-fg) 35%, transparent); font-weight:500; }
.fx .tc { font-style:normal; }
.fx .ui-caret { display:inline-block; width:3px; height:1.1em; background:var(--accent); vertical-align:-.15em; margin-left:2px; }
.fx .ui-tg { position:relative; flex:none; width:72px; height:40px; border-radius:20px; background:color-mix(in srgb, var(--card-fg) 18%, transparent); }
.fx .ui-tg i { position:absolute; left:4px; top:4px; width:32px; height:32px; border-radius:50%; background:#fff; box-shadow:0 2px 6px rgba(0,0,0,.3); }
.fx .ui-tg b { position:absolute; inset:0; border-radius:20px; background:var(--accent); opacity:0; }
.fx .ui-ck { position:relative; flex:none; width:34px; height:34px; border-radius:8px; box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--card-fg) 30%, transparent); }
.fx .ui-ck b { position:absolute; inset:0; border-radius:8px; background:var(--accent); opacity:0; }
.fx .ui-ck svg { position:absolute; inset:5px; stroke:#fff; stroke-width:4; fill:none; stroke-linecap:round; stroke-linejoin:round; }
.fx .ui-rd { position:relative; flex:none; width:32px; height:32px; border-radius:50%; box-shadow:inset 0 0 0 3px color-mix(in srgb, var(--card-fg) 30%, transparent); }
.fx .ui-rd b { position:absolute; inset:8px; border-radius:50%; background:var(--accent); transform:scale(0); }
.fx .ui-btn { display:flex; align-items:center; justify-content:center; border-radius:14px; background:var(--accent); color:var(--card); font:800 28px var(--f-body); letter-spacing:.06em; }
.fx .ui-chip { display:inline-flex; align-items:center; gap:8px; white-space:nowrap; font:700 20px var(--f-body); color:var(--card-fg); background:color-mix(in srgb, var(--card-fg) 7%, var(--card)); padding:6px 14px; border-radius:999px; }
.fx .ui-mock { position:absolute; z-index:6; white-space:nowrap; font:700 18px/1 var(--f-body); letter-spacing:.1em; color:var(--card); background:var(--card-fg); padding:6px 12px; border-radius:6px; opacity:.82; }
.fx .ui-toast { position:absolute; display:flex; align-items:center; gap:14px; white-space:nowrap; font:800 28px var(--f-body); color:#fff; background:#1f9d6b; padding:16px 26px; border-radius:16px; box-shadow:0 18px 40px rgba(0,0,0,.25); opacity:0; z-index:9; }
.fx .ui-toast svg { width:30px; height:30px; stroke:#fff; stroke-width:3.5; fill:none; stroke-linecap:round; stroke-linejoin:round; }
.fx .ui-cur { position:absolute; left:0; top:0; width:42px; height:42px; margin:-4px 0 0 -8px; z-index:12; filter:drop-shadow(0 4px 8px rgba(0,0,0,.45)); pointer-events:none; }
.fx .ui-rip { position:absolute; left:0; top:0; width:96px; height:96px; margin:-48px 0 0 -48px; border-radius:50%; border:4px solid var(--accent); background:color-mix(in srgb, var(--accent) 22%, transparent); opacity:0; z-index:11; pointer-events:none; }
.fx .ui-touch { position:absolute; left:0; top:0; width:64px; height:64px; margin:-32px 0 0 -32px; border-radius:50%; background:rgba(255,255,255,.55); box-shadow:0 0 0 3px rgba(0,0,0,.25), 0 6px 18px rgba(0,0,0,.25); opacity:0; z-index:12; pointer-events:none; }
"""

TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
CURSOR = ('<svg class="ui-cur" viewBox="0 0 24 24"><path d="M4 2.5 L4 19.5 L8.6 15.4 L11.6 22 L14.6 20.7 L11.7 14.2 L18 14.2 Z" '
          'fill="#fff" stroke="#111" stroke-width="1.4" stroke-linejoin="round"/></svg>')


SAFE = ["#c4291a", "#2457b8", "#127a52", "#8f5600", "#6a3fc0", "#a5305f", "#0f6470", "#4a515c"]   # white text ≥ 4.5:1 on each


def tone(name):
    return SAFE[SO.TONES.index(SO.tone(name))]


def avatar(X, name, img=None, style=""):
    return SO.avatar(X, name, img, style=("" if img else f"background:{tone(name)};") + style)


def base(X):
    X.css("fx-screens", S.CSS); X.css("fx-ui2", CSS); SO.base_css(X)


def area(X, p): return S.area(X, p)


def typed(X, text):
    return "".join(f'<i class="tc">{X.rich(ch)}</i>' if ch != " " else '<i class="tc">&nbsp;</i>' for ch in str(text))


def type_in(X, sel, t, n, cps=16.0, caret=None, until=None):
    """reveal `n` glyphs of sel's .tc one by one from t; blink `caret` (a selector) until `until`. → end time."""
    if n <= 0: return t
    st = 1.0 / cps
    X.tw(f'tl.from("{sel} .tc", {{opacity:0, duration:0.01, stagger:{st:.4f}, ease:"none"}}, {t:.3f});')
    end = t + n * st
    if caret and until and until > end + 0.3:
        k = int((until - end) / 0.5)
        if k >= 1:
            X.tw(f'tl.fromTo("{caret}", {{opacity:1}}, {{opacity:0, duration:0.25, ease:"steps(1)", repeat:{2 * k - 1}, yoyo:true, immediateRender:false}}, {end + 0.25:.3f});')
    return end


def when(X, v, t, dflt):
    if v is None: return dflt
    if isinstance(v, (int, float)): return t + float(v)
    r = X.T(v, t)
    return float(r) if r is not None else dflt


def spread(n, a, b):
    if n <= 0: return []
    if n == 1: return [a]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def mock(X, p, x, y, right=False):
    """a small 「示意」 badge when the content is illustrative; right=True: x is its right edge."""
    m = p.get("mock")
    if not m: return ""
    lab = "示意" if m is True else str(m)
    tf = " transform:translateX(-100%);" if right else ""
    return f'<div class="ui-mock" style="left:{x:.0f}px; top:{y:.0f}px;{tf}">{X.rich(lab)}</div>'


def px_fit(text, w, h, max_px, min_px=16, max_lines=2, lh=1.25):
    return FT.fit_text(str(text), w, h, max_px, min_px, lh=lh, max_lines=max_lines)
