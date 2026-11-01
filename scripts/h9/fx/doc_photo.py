"""拍照的文档 / 白板 (a phone photo of a page or whiteboard — skewed, shadowed): the photo lands as shot, the four
corners are found and outlined like a scanner app, the page flattens into a clean sheet (perspective-corrected and
evened out at build time), a scan line passes, then the passages you point at get marked.

p: image (the photo) · corners ([[x,y], ×4] in % of the photo, any order; omitted → auto-detected) · hl ([x, y, w, h] %
   of the flattened page, or a list of them) · ratio (page w/h; default from the corners) · title · caption · kicker
Adapts: any photo size / orientation; pages or whiteboards; 0–6 marks; when detection fails the whole photo is used
(no crash); 16:9 page left + text right, 9:16 page on top. Needs OpenCV (cv2) + numpy at build time.
"""
from h9 import fit
from h9.aefx import _clip
import pathlib, importlib.util, sys

_s = importlib.util.spec_from_file_location("h9fx__docs2", pathlib.Path(__file__).with_name("_docs2.py"))
D = sys.modules.get("h9fx__docs2") or importlib.util.module_from_spec(_s)
if "h9fx__docs2" not in sys.modules: sys.modules["h9fx__docs2"] = D; _s.loader.exec_module(D)


def _order(pts):
    pts = sorted(pts, key=lambda q: q[1])
    top = sorted(pts[:2], key=lambda q: q[0]); bot = sorted(pts[2:], key=lambda q: q[0])
    return [top[0], top[1], bot[1], bot[0]]


def _detect(img):
    import cv2, numpy as np
    h, w = img.shape[:2]
    k = 900 / max(h, w); sm = cv2.resize(img, (int(w * k), int(h * k)))
    g = cv2.GaussianBlur(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY), (7, 7), 0)
    best = None
    for th in (cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1], cv2.dilate(cv2.Canny(g, 40, 120), None, iterations=2)):
        cs, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in sorted(cs, key=cv2.contourArea, reverse=True)[:5]:
            ap = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(ap) == 4 and cv2.contourArea(ap) > 0.15 * sm.shape[0] * sm.shape[1]:
                best = [(float(x) / k, float(y) / k) for x, y in ap.reshape(4, 2)]; break
        if best: break
    return _order(best) if best else [(0, 0), (w, 0), (w, h), (0, h)]


def _flatten(X, src, corners, ratio):
    import cv2, numpy as np
    a = fit._abs(X, src)
    img = cv2.imread(str(a))
    if img is None: raise SystemExit(f"doc_photo: cannot read {a}")
    h, w = img.shape[:2]
    if corners: pts = _order([(x / 100 * w, y / 100 * h) for x, y in corners])
    else: pts = _detect(img)
    tl, tr, br, bl = [np.array(q, dtype=np.float32) for q in pts]
    pw = max(np.linalg.norm(tr - tl), np.linalg.norm(br - bl)); ph = max(np.linalg.norm(bl - tl), np.linalg.norm(br - tr))
    ar = float(ratio) if ratio else pw / max(ph, 1)
    OW = 1400; OH = int(OW / ar)
    f, url = D.cache(X, f"{a}|{a.stat().st_mtime}|{pts}|{OW}|{OH}", "jpg")
    if not f.exists():
        M = cv2.getPerspectiveTransform(np.array(pts, dtype=np.float32), np.array([[0, 0], [OW, 0], [OW, OH], [0, OH]], dtype=np.float32))
        flat = cv2.warpPerspective(img, M, (OW, OH), flags=cv2.INTER_CUBIC)
        # even out the lighting like a scanner app: divide by a heavily blurred copy, then lift the paper to white
        g = cv2.GaussianBlur(flat, (0, 0), 41)
        norm = cv2.divide(flat, g, scale=235)
        norm = cv2.addWeighted(norm, 0.82, flat, 0.18, 8)
        cv2.imwrite(str(f), norm, [cv2.IMWRITE_JPEG_QUALITY, 90])
    return url, (w, h), [(x / w * 100, y / h * 100) for x, y in pts], OW / OH


def doc_photo(X, cid, t, d, p):
    src = p.get("image") or p.get("src")
    if not src: raise SystemExit("doc_photo needs `image`")
    furl, (iw, ih), quad, par = _flatten(X, src, p.get("corners"), p.get("ratio"))
    x0, y0, x1, y1 = D.box(X, p)
    P = X.portrait
    bw, bh = x1 - x0, y1 - y0
    title, caption = fit.as_text(p.get("title")), fit.as_text(p.get("caption"))
    tw_ = bw * (0.95 if P else 0.38)
    tf = D.C.fitted(X, title, tw_, 160 if not P else 110, 56 if not P else 50, 26, max_lines=3) if title else None
    cf = D.C.fitted(X, caption, tw_, 140, 32, 20, max_lines=4) if caption else None
    if P:
        tblock = ((tf.n * tf.px * 1.12 + 18) if tf else 0) + ((cf.n * cf.px * 1.3 + 10) if cf else 0)
        fx, fy, fw, fh = x0, y0, bw, bh - tblock - (20 if tblock else 0)
        tx, ty = x0, y0 + fh + 20
    else:
        fw = bw * (0.58 if (tf or cf) else 1.0); fx, fy, fh = x0, y0, bh
        tblock = ((tf.n * tf.px * 1.12 + 18) if tf else 0) + ((cf.n * cf.px * 1.3) if cf else 0)
        tx, ty = x0 + fw + 48, y0 + (bh - tblock) / 2
    # the photo, contained in the frame
    iar = iw / ih
    pw_ = min(fw, fh * iar); ph_ = pw_ / iar
    px_, py_ = fx + (fw - pw_) / 2, fy + (fh - ph_) / 2
    # the flattened page, contained (a little smaller, centred)
    dw = min(fw * 0.9, fh * 0.94 * par); dh = dw / par
    dx, dy = fx + (fw - dw) / 2, fy + (fh - dh) / 2
    qpx = [(px_ + qx / 100 * pw_, py_ + qy / 100 * ph_) for qx, qy in quad]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in qpx)
    qbx0 = min(x for x, _ in qpx); qbx1 = max(x for x, _ in qpx); qby0 = min(y for _, y in qpx); qby1 = max(y for _, y in qpx)
    s0 = max(0.3, min((qbx1 - qbx0) / dw, (qby1 - qby0) / dh))
    ddx, ddy = (qbx0 + qbx1) / 2 - (dx + dw / 2), (qby0 + qby1) / 2 - (dy + dh / 2)
    hls = p.get("hl") or []
    if hls and not isinstance(hls[0], (list, tuple)): hls = [hls]
    marks = "".join(f'<i class="d2-mk dp-mk" style="left:{b[0]}%; top:{b[1]}%; width:{b[2]}%; height:{b[3]}%"></i>' for b in hls[:6])
    corners = "".join(f'<i class="dp-cn" style="left:{x:.1f}px; top:{y:.1f}px"></i>' for x, y in qpx)
    X.used_text.update(title + caption + str(p.get("kicker", "")) + "已摆正 · 已增强")
    kick = f'<div class="d2-kick" style="left:{fx + 18:.0f}px; top:{fy + 18:.0f}px">{X.rich(p["kicker"])}</div>' if p.get("kicker") else ""
    tag = f'<div class="d2-tag dp-tag" style="left:{dx:.0f}px; top:{dy + dh + 10 if dy + dh + 44 < fy + fh else dy + dh - 40:.0f}px">已摆正 · 已增强</div>'
    head = (f'<div class="d2-ttl dp-ttl" style="left:{tx:.0f}px; top:{ty:.0f}px; font-size:{tf.px}px">{D.C.lines(X, tf)}</div>' if tf else "")
    cap = (f'<div class="dp-cap" style="left:{tx:.0f}px; top:{ty + ((tf.n * tf.px * 1.12 + 18) if tf else 0):.0f}px; width:{tw_:.0f}px; font-size:{cf.px}px">{D.C.lines(X, cf)}</div>' if cf else "")
    body = (f'<img class="dp-ph" src="{X.asset(src)}" alt="" style="left:{px_:.1f}px; top:{py_:.1f}px; width:{pw_:.1f}px; height:{ph_:.1f}px">'
            f'<svg class="dp-q" viewBox="0 0 {X.W} {X.H}" style="width:{X.W}px; height:{X.H}px"><polygon points="{poly}" pathLength="1"/></svg>{corners}'
            f'<div class="d2-sheet dp-flat" style="left:{dx:.1f}px; top:{dy:.1f}px; width:{dw:.1f}px; height:{dh:.1f}px"><img src="{furl}" alt="">{marks}<i class="dp-scan"></i></div>'
            + tag + kick + head + cap)
    X.css("fx-d2", D.CSS)
    X.css("fx-doc-photo", """
.dp-ph { position:absolute; object-fit:cover; border-radius:8px; box-shadow:0 20px 60px rgba(0,0,0,.3); }
.dp-q { position:absolute; left:0; top:0; overflow:visible; pointer-events:none; }
.dp-q polygon { fill:rgba(246,206,58,.14); stroke:#f6ce3a; stroke-width:4; stroke-linejoin:round; stroke-dasharray:1 1; stroke-dashoffset:1; }
.dp-cn { position:absolute; width:26px; height:26px; margin:-13px 0 0 -13px; border-radius:50%; background:#f6ce3a; box-shadow:0 0 0 5px rgba(246,206,58,.35); }
.dp-flat { opacity:0; }
.dp-scan { position:absolute; left:0; right:0; top:0; height:16%; background:linear-gradient(180deg, rgba(246,206,58,0), rgba(246,206,58,.35) 85%, #f6ce3a); opacity:0; }
.dp-cap { position:absolute; font-family:var(--f-body); font-weight:600; color:var(--muted); line-height:1.3; }
.dp-tag { opacity:0; }
""")
    _clip(X, cid, t, d, f'<div class="d2 dp">{body}</div>', p)
    S = f"#{cid}"
    X.tw(f'tl.from("{S} .dp-ph", {{y:70, rotation:-4, opacity:0, duration:0.6, ease:"expo.out"}}, {t:.3f});')
    X.sfx(t, "paper")
    t1 = t + min(0.55, d * 0.14)
    X.tw(f'tl.from("{S} .dp-cn", {{scale:0, duration:0.3, ease:"back.out(3)", stagger:0.08}}, {t1:.3f});')
    X.tw(f'tl.to("{S} .dp-q polygon", {{strokeDashoffset:0, duration:0.55, ease:"power2.inOut"}}, {t1 + 0.1:.3f});')
    X.sfx(t1, "click")
    t2 = t1 + min(0.75, d * 0.2)
    X.tw(f'tl.fromTo("{S} .dp-flat", {{opacity:0, x:{ddx:.1f}, y:{ddy:.1f}, scale:{s0:.3f}, rotation:-3}}, {{opacity:1, x:0, y:0, scale:1, rotation:0, duration:0.8, ease:"expo.inOut"}}, {t2:.3f});')
    X.tw(f'tl.to("{S} .dp-ph, {S} .dp-q, {S} .dp-cn", {{opacity:0, duration:0.45, ease:"power2.out"}}, {t2 + 0.15:.3f});')
    X.sfx(t2, "whoosh_soft")
    t3 = t2 + 0.8
    X.tw(f'tl.fromTo("{S} .dp-scan", {{opacity:1, yPercent:-100}}, {{yPercent:{100 / 0.16:.0f}, duration:0.75, ease:"power1.inOut"}}, {t3:.3f});')
    X.tw(f'tl.to("{S} .dp-scan", {{opacity:0, duration:0.15}}, {t3 + 0.75:.3f});')
    X.tw(f'tl.to("{S} .dp-tag", {{opacity:1, duration:0.3}}, {t3 + 0.3:.3f});')
    if marks:
        X.tw(f'tl.fromTo("{S} .dp-mk", {{scaleX:0}}, {{scaleX:1, duration:0.35, ease:"power2.inOut", stagger:0.25}}, {t3 + 0.8:.3f});')
        X.sfx(t3 + 0.8, "click")
    if tf: X.tw(f'tl.from("{S} .dp-ttl .ct-l > span", {{yPercent:100, opacity:0, duration:0.55, ease:"expo.out", stagger:0.06}}, {t + 0.25:.3f});')
    if cf: X.tw(f'tl.from("{S} .dp-cap", {{opacity:0, y:14, duration:0.5}}, {t3:.3f});')
    hold = t3 + 1.2
    if t + d - hold > 0.3:
        X.tw(f'tl.to("{S} .dp-flat", {{scale:1.04, duration:{t + d - hold:.2f}, ease:"none"}}, {hold:.3f});')


FX = {"doc_photo": doc_photo}
