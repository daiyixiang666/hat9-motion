"""一个 → 一群 One to many ("one person, a whole team of agents behind them"): one tile sits alone with a big "1";
then it shrinks into the middle of a grid while dozens of small working tiles (terminals, cards, avatars or real
pictures) ripple out around it, the "1" flies to the tile's corner and counts up to the total, a title lands over the
grid, and the tiles keep working (progress bars run, ticks land).

Adapts: 6–200 tiles (grid from the frame and the count), four tile kinds, subject as a still / clip or a text card,
any title length (fitted); tiles take the style's card colour, corners, mono face and accent.
p: subject (the one; else `one` text card) · subject_label · count · kind (terminal | card | avatar | image) · items /
   folder (kind image) · names (tile titles) · lines (text pool for terminal / card tiles) · one_unit (e.g. "人") ·
   unit (after the total) · title · mock
"""
import importlib.util
import math
import pathlib
import random
import sys
from h9 import fit
from h9.aefx import _clip


def _load(name):
    key = f"h9fx_{name}"
    if key not in sys.modules:
        spec = importlib.util.spec_from_file_location(key, pathlib.Path(__file__).with_name(f"{name}.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
    return sys.modules[key]


M = _load("_metaphor")
MD = M.MD

CSS = """
.fx .om .om-grid { position:absolute; left:0; top:0; transform-origin:50% 50%; }
.fx .om .om-t { position:absolute; overflow:hidden; background:var(--card); color:var(--card-fg); border-radius:var(--mt-tr);
  box-shadow:0 0 0 1px color-mix(in srgb, var(--card-fg) 10%, transparent); }
.fx .om .om-t .tb { display:flex; align-items:center; gap:.4em; padding:.45em .6em .35em; font:700 1em var(--f-mono, monospace); white-space:nowrap;
  border-bottom:1px solid color-mix(in srgb, var(--card-fg) 12%, transparent); }
.fx .om .om-t .tb i { width:.6em; height:.6em; border-radius:var(--mt-dot); background:color-mix(in srgb, var(--card-fg) 25%, transparent); flex:none; }
.fx .om .om-t .tb i.on { background:var(--accent); }
.fx .om .om-t .tb span { overflow:hidden; text-overflow:ellipsis; }
.fx .om .om-t .ln { padding:0 .6em; font:500 .9em/1.55 var(--f-mono, monospace); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  color:color-mix(in srgb, var(--card-fg) 62%, transparent); }
.fx .om .om-t .ln b { color:var(--accent); font-weight:700; }
.fx .om .om-t .pb { position:absolute; left:.6em; right:.6em; bottom:.6em; height:.35em; border-radius:var(--mt-tr); background:color-mix(in srgb, var(--card-fg) 10%, transparent); overflow:hidden; }
.fx .om .om-t .pb u { position:absolute; left:0; top:0; bottom:0; width:100%; background:var(--accent); transform-origin:0 50%; }
.fx .om .om-t .ok { position:absolute; right:.5em; bottom:1.2em; font:900 1.6em var(--f-body); color:var(--accent); opacity:0; }
.fx .om .om-t.av { display:flex; flex-direction:column; align-items:center; justify-content:center; gap:.4em; }
.fx .om .om-t.av .face { width:46%; aspect-ratio:1; border-radius:var(--mt-dot); display:grid; place-items:center; font:900 2.2em var(--f-display); color:var(--card); }
.fx .om .om-t.av .nm { font:700 1em var(--f-body); white-space:nowrap; max-width:90%; overflow:hidden; text-overflow:ellipsis; }
.fx .om .om-t.img { background-repeat:no-repeat; }
.fx .om .om-one { position:absolute; overflow:hidden; border-radius:var(--mt-r); background:var(--card); box-shadow:var(--mt-shadow), 0 0 0 4px var(--accent); transform-origin:0 0; }
.fx .om .om-one > img { position:absolute; inset:0; width:100%; height:100%; object-fit:cover; }
.fx .om .om-one .txt { position:absolute; inset:0; display:grid; place-items:center; font-family:var(--f-display); font-weight:900; color:var(--card-fg); }
.fx .om .om-num { position:absolute; display:flex; align-items:baseline; gap:.08em; color:var(--accent); transform-origin:0 100%;
  background:var(--bg); padding:.04em .18em .08em; border-radius:var(--mt-r); }
.fx .om .om-num .us { display:inline-grid; } .fx .om .om-num .us small { grid-area:1 / 1; }
.fx .om .om-num small { font-family:var(--f-body); font-weight:900; font-size:.36em; color:var(--fg); }
.fx .om .om-ttl { position:absolute; text-align:center; }
.fx .om .om-ttl .fl { display:table; margin:0 auto; background:var(--bg); padding:.06em .4em .12em; border-radius:var(--mt-r); box-shadow:var(--mt-shadow); }
.fx .om .om-ttl .em .emt { color:var(--accent); }
"""

LINES = ["$ run eval --suite motion", "<b>✓</b> build 16:9 · 9:16", "fetch refs … 24 ok", "render frame 0412/0900", "lint: 0 P0 · 2 P1",
         "<b>→</b> retry with seed 9", "write captions.srt", "diff +184 −37", "tests 128 passed", "queue: 3 waiting", "upload preview.webp",
         "<b>✓</b> contact sheet", "scan fonts · 60 faces", "tts: 41.2 s audio", "beat grid 128 bpm", "<b>!</b> text overflow → fit"]
NAMES = ["agent-01", "planner", "writer", "render", "review", "fetch", "lint", "captions", "music", "cover", "qa", "deploy"]
FACES = ["var(--accent)", "var(--fg)", "color-mix(in srgb, var(--accent) 55%, var(--fg))", "color-mix(in srgb, var(--accent) 50%, var(--card))"]


def one_to_many(X, cid, t, d, p):
    M.base(X)
    X.css("fx-om", CSS)
    sk = M.skin(X)
    P = X.portrait
    W = X.W
    H = X.H
    rnd = random.Random(int(p.get("seed", 9)) * 7919 + 5)
    count = max(6, min(200, int(p.get("count", 48))))
    kind = p.get("kind", "terminal")
    # grid over the whole frame (a 2×2 block in the middle is the one)
    pad = 26
    top = 110 if not P else 250
    bottom = 96 if not P else 420
    aw = W - 2 * pad
    ah = H - top - bottom
    ar = 1.35 if not P else 1.0
    if kind == "avatar":
        ar = 0.9
    cells = count + 4
    cols = max(4, int(round(math.sqrt(cells * aw / ah / ar))))
    rows = max(4, int(math.ceil(cells / cols)))
    gap = max(6.0, min(aw / cols, ah / rows) * 0.06)
    cw = (aw - gap * (cols - 1)) / cols
    chh = (ah - gap * (rows - 1)) / rows
    c0 = cols // 2 - 1
    r0 = rows // 2 - 1
    bx = pad + c0 * (cw + gap)
    by = top + r0 * (chh + gap)
    bw = 2 * cw + gap
    bh = 2 * chh + gap
    names = p.get("names") or NAMES
    pool_lines = p.get("lines") or LINES
    tile_font = max(9.0, min(cw / 15.0, chh / 7.5))
    url = None
    if kind == "image":
        its = M.pool(X, p, cap=200)
        if not its:
            raise SystemExit("one_to_many kind image: give `items` or `folder`")
        tw = 160
        th = int(round(tw / ar))
        url, acols, aw_, ah_ = MD.atlas(X, its, tw, th)
        X.css(f"fx-om-bg-{cid}", f"#{cid} .om-t.img {{ background-image:url({url}); background-size:{aw_ * cw / tw:.1f}px {ah_ * chh / th:.1f}px; }}")
    tiles = []
    cx = W / 2
    cy = H / 2
    maxd = math.hypot(W / 2, H / 2)
    n = 0
    ok_tiles = []
    # take the cells nearest the block first, so a small count still sits round the one
    free = []
    bcx = c0 + 0.5
    bcy = r0 + 0.5
    for r in range(rows):
        for c in range(cols):
            if r0 <= r <= r0 + 1 and c0 <= c <= c0 + 1:
                continue
            gd = math.hypot((c - bcx) * cw, (r - bcy) * chh)
            free.append((gd, r, c))
    free.sort()
    picked = []
    for gd, r, c in free[:count]:
        picked.append((r, c))
    picked.sort()
    for r, c in picked:
        x = pad + c * (cw + gap)
        y = top + r * (chh + gap)
        dist = math.hypot(x + cw / 2 - cx, y + chh / 2 - cy) / maxd
        ring = min(9, int(dist * 12))
        style = f"left:{x:.1f}px; top:{y:.1f}px; width:{cw:.1f}px; height:{chh:.1f}px; font-size:{tile_font:.1f}px"
        nm = names[n % len(names)]
        if kind == "terminal" or kind == "card":
            k_lines = max(1, int((chh / tile_font - 4.2) / 1.55))
            body = ""
            for j in range(k_lines):
                body += f'<div class="ln">{pool_lines[rnd.randrange(len(pool_lines))]}</div>'
            dot = ' class="on"' if rnd.random() < 0.5 else ""
            tb = f'<div class="tb"><i{dot}></i><span>{X.rich(nm)}</span></div>' if kind == "terminal" else f'<div class="tb"><span>{X.rich(nm)}</span></div>'
            inner = tb + body + '<div class="pb"><u></u></div><b class="ok">✓</b>'
            tiles.append(f'<div class="om-t q{ring}" data-n="{n}" style="{style}">{inner}</div>')
        elif kind == "avatar":
            face = FACES[rnd.randrange(len(FACES))]
            init = fit.plain(nm)[:1].upper()
            tiles.append(f'<div class="om-t av q{ring}" data-n="{n}" style="{style}"><i class="face" style="background:{face}">{X.rich(init)}</i>'
                         f'<span class="nm">{X.rich(nm)}</span></div>')
        else:
            k = rnd.randrange(len(its))
            ar_r, ar_c = divmod(k, acols)
            bp = f"background-position:{-ar_c * cw:.1f}px {-ar_r * chh:.1f}px"
            tiles.append(f'<div class="om-t img q{ring}" data-n="{n}" style="{style}; {bp}"></div>')
        if kind in ("terminal", "card") and rnd.random() < 0.35:
            ok_tiles.append(n)
        n += 1
    X.used_text.update("✓" + "".join(names))
    for ln in pool_lines:
        X.used_text.update(fit.plain(ln))
    # the one: big and centred first, then into its 2×2 block
    big_w = W * (0.38 if not P else 0.62)
    big_h = big_w * bh / bw
    if big_h > H * 0.42:
        big_h = H * 0.42
        big_w = big_h * bw / bh
    num_px = big_h * 0.8
    one_x = (W - big_w) / 2 - (num_px * 0.35 if not P else 0)
    one_y = (H - big_h) / 2 - (0 if not P else 60)
    k_scale = big_w / bw
    src = p.get("subject")
    one_html = ""
    one_sel = f"#{cid} .om-one"
    if src and fit.is_video(src):
        rect = f"inset:auto; left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px; border-radius:var(--mt-r, 14px); overflow:hidden; transform-origin:0 0; {M.skin_vars(sk)}"
        _, vsel = fit.media(X, cid, "one", src, t, d, "om-onev", fill="cover", z=4, start=float(p.get("subject_start", 0)), extra_style=rect)
        if str(src).lower().endswith(".webm"):
            X.css(f"om-fit-{cid}", f"{vsel} video {{ object-fit:contain !important; object-position:50% 100% !important; }} "
                                   f"{vsel} {{ background:radial-gradient(ellipse 70% 70% at 50% 40%, color-mix(in srgb, var(--card) 85%, var(--accent) 15%), var(--card)); }}")
        one_html = f'<div class="om-one" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px"></div>'
        one_sel = f"#{cid} .om-one, {vsel}"
    elif src:
        one_html = (f'<div class="om-one" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">'
                    f'<img src="{X.asset(src)}" alt="" style="object-position:{fit.focus_css(p.get("subject_focus"))}"></div>')
    else:
        one = p.get("one", "你")
        o_px, o_lines, _ = M.fit_text(X, one, bw * 0.9, bh * 0.8, bh * 0.5, 16, 2)
        one_html = (f'<div class="om-one" style="left:{bx:.0f}px; top:{by:.0f}px; width:{bw:.0f}px; height:{bh:.0f}px">'
                    f'<div class="txt" style="font-size:{o_px:.0f}px">{o_lines}</div></div>')
    # the number: "1" beside the big tile, later at the block's corner counting to the total
    unit1 = p.get("one_unit", "")
    unit = p.get("unit", unit1)
    X.used_text.update(str(unit1) + str(unit) + "0123456789")
    num_html = (f'<div class="om-num mt-k" style="left:0; top:0; font-size:{num_px:.0f}px"><span class="n">1</span>'
                f'<span class="us"><small class="u1">{X.rich(unit1)}</small><small class="u2" style="opacity:0">{X.rich(unit)}</small></span></div>')
    if P:
        n1x = W / 2 - num_px * 0.35
        n1y = one_y + big_h + 20
    else:
        n1x = one_x + big_w + 40
        n1y = one_y + big_h - num_px
    end_px = min(bh * 0.42, 150)
    # the element scales about its bottom-left corner: park that corner just inside the block's bottom-left
    n2x = bx + 14
    n2y = by + bh - num_px * 1.12 - 10
    k2 = end_px / num_px
    title = p.get("title", "")
    ttl_html = ""
    if title:
        tt_w = W - 2 * (120 if P else 160)
        tt_px, tt_lines, tt_n = M.fit_text(X, title, tt_w, (H * 0.2), 110 if not P else 96, 40, 2)
        tt_y = by - tt_px * 1.3 * tt_n - 40
        tt_y = max(tt_y, 150 if not P else 250)
        ttl_html = f'<div class="om-ttl mt-t" style="left:{(W - tt_w) / 2:.0f}px; top:{tt_y:.0f}px; width:{tt_w:.0f}px; font-size:{tt_px:.0f}px">{tt_lines}</div>'
    lab_html = ""
    grid = f'<div class="om-grid" data-layout-allow-overlap style="width:{W}px; height:{H}px">{"".join(tiles)}</div>'
    mock = M.mock_tag(X, p, W - 160, 150 if not P else 250)
    _clip(X, cid, t, d, M.wrap(X, sk, grid + one_html + lab_html + ttl_html + mock, "om"), p)
    s = f"#{cid}"
    sn = M.over(X, cid, "n", t, d, sk, num_html, "om")
    e = M.ease_in(sk)
    t1 = t + min(1.5, max(0.9, d * 0.26))
    # 1 · alone
    big_dx = one_x - bx
    big_dy = one_y - by
    X.tw(f'tl.set("{one_sel}", {{x:{big_dx:.1f}, y:{big_dy:.1f}, scale:{k_scale:.4f}, transformOrigin:"0 0"}}, {t:.3f});')
    X.tw(f'tl.from("{one_sel}", {{opacity:0, y:"+=60", duration:0.55, ease:"{e}"}}, {t + 0.02:.3f});')
    X.tw(f'tl.set("{sn} .om-num", {{x:{n1x:.1f}, y:{n1y:.1f}, scale:1}}, {t:.3f});')
    X.tw(f'tl.from("{sn} .om-num", {{opacity:0, scale:0.5, duration:0.45, ease:"back.out(2.2)"}}, {t + 0.3:.3f});')
    X.sfx(t + 0.3, "pop")
    # 2 · the one settles into the grid, the many ripple out
    X.tw(f'tl.to("{one_sel}", {{x:0, y:0, scale:1, duration:0.8, ease:"expo.inOut"}}, {t1:.3f});')
    X.tw(f'tl.to("{sn} .om-num", {{x:{n2x:.1f}, y:{n2y:.1f}, scale:{k2:.4f}, duration:0.8, ease:"expo.inOut"}}, {t1:.3f});')
    X.tw(f'tl.to("{sn} .om-num .u1", {{opacity:0, duration:0.2}}, {t1:.3f});')
    X.sfx(t1, "whoosh")
    for ring in range(10):
        X.tw(f'tl.from("{s} .om-t.q{ring}", {{scale:0, opacity:0, duration:0.4, ease:"back.out(1.8)"}}, {t1 + 0.35 + ring * 0.06:.3f});')
    t2 = t1 + 0.9
    W3 = M.W3
    W3.count(X, f"{sn} .om-num .n", t1 + 0.4, count + 1, dur=0.9, dec=0, ease="power2.out", start=1)
    if unit:
        X.tw(f'tl.to("{sn} .om-num .u2", {{opacity:1, duration:0.2}}, {t1 + 1.0:.3f});')
    X.sfx(t1 + 0.4, "count")
    if p.get("subject_label"):
        chip = f'<div class="mt-subl" style="left:{bx + bw / 2:.0f}px; top:{by - 20:.0f}px">{X.rich(p["subject_label"])}</div>'
        M.label_over(X, cid, t, d, sk, chip, t1 + 0.8)
    # 3 · the title lands over the grid; the tiles keep working
    if title:
        X.tw(f'tl.from("{s} .om-ttl .fl", {{yPercent:70, opacity:0, scale:0.9, duration:0.55, ease:"{e}", stagger:0.08}}, {t2:.3f});')
        X.sfx(t2, "hit")
    if kind in ("terminal", "card"):
        for i in range(n):
            st = t1 + 0.5 + rnd.uniform(0, 0.6)
            du = rnd.uniform(1.2, max(1.3, t + d - st))
            to = rnd.uniform(0.35, 1.0)
            X.tw(f'tl.fromTo("{s} .om-t[data-n=\'{i}\'] .pb u", {{scaleX:0}}, {{scaleX:{to:.2f}, duration:{du:.2f}, ease:"power1.inOut"}}, {st:.3f});')
        for i in ok_tiles:
            when = rnd.uniform(t2 + 0.2, max(t2 + 0.3, t + d - 0.4))
            X.tw(f'tl.fromTo("{s} .om-t[data-n=\'{i}\'] .ok", {{opacity:0, scale:2}}, {{opacity:1, scale:1, duration:0.25, ease:"back.out(2)", immediateRender:false}}, {when:.3f});')
    X.tw(f'tl.fromTo("{s} .om-grid", {{scale:1.08}}, {{scale:1.02, duration:1.0, ease:"power2.out"}}, {t1:.3f});')
    X.tw(f'tl.to("{s} .om-grid", {{scale:1, duration:{max(0.3, t + d - t1 - 1.0):.2f}, ease:"none"}}, {t1 + 1.0:.3f});')


FX = {"one_to_many": one_to_many}
