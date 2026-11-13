"""fx3 · one transition: anchor_match — a match cut on a persistent element. Written on the next beat:
"tr": "anchor_match", optional "tr_anchor": a CSS selector or a data-anchor name.

The anchor is found at page load (so every frame is the same however the timeline is seeked):
  outgoing: the element carrying data-anchor (or tr_anchor), else the scene's hero = the visible text with the largest
            font size (ties: the wider one)
  incoming: the element with the same data-anchor name (or tr_anchor), else the incoming hero
Over 16 frames (the cut is at frame 6): frames 0–6 the incoming ground rises over everything in the outgoing scene except
the anchor (expo.in); frames 4–14 the anchor flies from its old box to its new one on cubic-bezier(0.65, 0, 0.35, 1),
its colour, background and corner radius blending into the new look; frames 10–16 the ground lifts and the incoming
scene builds in around it. The anchor travels as an overlay clone (like whip_carry's chip), so it works whatever the
two scenes are; the real incoming anchor is shown once it is fully visible (at most 0.8 s after the window).

This module exports no effects (FX = {}); scripts/h9/fx.py's transition() dispatches the id to TRS below.
"""
import importlib.util
import pathlib
import sys

from h9 import fx as TRM

if "h9fx_fx2_transitions" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx_fx2_transitions", pathlib.Path(__file__).with_name("fx2_transitions.py"))
    sys.modules["h9fx_fx2_transitions"] = importlib.util.module_from_spec(_s)
    _s.loader.exec_module(sys.modules["h9fx_fx2_transitions"])
T2 = sys.modules["h9fx_fx2_transitions"]

CSS = r"""
.tr3 { pointer-events:none; overflow:hidden; }
.tr3 .tr3-ground { position:absolute; inset:0; background:var(--bg); clip-path:inset(100% 0 0 0); }
.tr3 .tr3-clone { position:absolute; left:0; top:0; margin:0; transform-origin:0 0; box-sizing:border-box; }
"""

JS = r"""
(()=>{
  const OUT = __OUT__, IN = __IN__, WANT = __WANT__;
  const T0 = __T0__, FPS = __FPS__, HOLD = __HOLD__;
  const box = document.getElementById(__CID__);
  if (!box) return;
  const root = document.getElementById("root");
  const ground = box.querySelector(".tr3-ground");

  function scopes(ids) {
    const out = [];
    for (const id of ids) {
      if (!id) continue;
      const a = document.getElementById(id);
      const b = document.getElementById(id + "_scr");
      if (a) out.push(a);
      if (b) out.push(b);
    }
    return out;
  }
  function ownText(el) {
    for (const n of el.childNodes) {
      if (n.nodeType === 3 && n.textContent.trim()) return true;
    }
    return false;
  }
  function pick(list, want) {
    // 1. a selector or a data-anchor name
    if (want) {
      const sel = /^[.#\[]|\s|>/.test(want) ? want : '[data-anchor="' + want + '"]';
      for (const s of list) {
        const hit = s.querySelector(sel);
        if (hit) return hit;
      }
      return null;
    }
    // 2. anything marked data-anchor
    for (const s of list) {
      const hit = s.querySelector("[data-anchor]");
      if (hit) return hit;
    }
    return null;
  }
  function hero(list) {
    let best = null, bestSize = 0, bestW = 0;
    for (const s of list) {
      for (const el of s.querySelectorAll("*")) {
        if (!ownText(el) || el.closest('[data-safe="ignore"], .ctx, script, style')) continue;
        const size = parseFloat(getComputedStyle(el).fontSize) || 0;
        const w = el.offsetWidth || 0;
        if (size > bestSize || (size === bestSize && w > bestW)) {
          best = el; bestSize = size; bestW = w;
        }
      }
    }
    return best;
  }
  function layoutBox(el) {
    // the box of the element's own ink (its text, not a full-width line box) in frame px, before transforms:
    // the layout position comes from the offset chain, the ink's place inside it from a Range, unscaled
    let x = 0, y = 0, e = el;
    while (e && e !== root && e.offsetParent !== undefined) {
      x += e.offsetLeft || 0;
      y += e.offsetTop || 0;
      e = e.offsetParent;
    }
    const w = el.offsetWidth || 1, h = el.offsetHeight || 1;
    const er = el.getBoundingClientRect();
    const rg = document.createRange();
    rg.selectNodeContents(el);
    const ir = rg.getBoundingClientRect();
    if (!er.width || !ir.width) return { x: x, y: y, w: w, h: h };
    const k = w / er.width;
    const ix = (ir.left - er.left) * k, iw = ir.width * k;
    if (iw >= w - 1) return { x: x, y: y, w: w, h: h };
    return { x: x + ix, y: y, w: iw, h: h };
  }
  function groundOf(el) {
    // the page ground behind el: the outermost ancestor that is painted and nearly as wide as the frame (not a card)
    const chain = [];
    let e = el;
    while (e && e !== root) { chain.unshift(e); e = e.parentElement; }
    for (const a of chain) {
      const c = getComputedStyle(a).backgroundColor;
      const painted = c && c !== "transparent" && !/rgba\([^)]*,\s*0\)$/.test(c);
      if (painted && a.offsetWidth >= root.offsetWidth * 0.9) return c;
    }
    return getComputedStyle(el).getPropertyValue("--bg") || "#000";
  }
  const KEEP = ["font-family", "font-size", "font-weight", "font-style", "letter-spacing", "line-height", "text-align", "white-space",
                "color", "background-color", "border-radius", "padding", "-webkit-text-stroke", "font-variant-numeric", "text-transform"];
  function cloneOf(el, b) {
    const c = el.cloneNode(true);
    c.removeAttribute("id");
    c.removeAttribute("data-anchor");
    const cs = getComputedStyle(el);
    let st = "";
    for (const k of KEEP) st += k + ":" + cs.getPropertyValue(k) + ";";
    c.setAttribute("style", st + "position:absolute;left:0;top:0;margin:0;width:" + b.w + "px;height:" + b.h + "px;text-align:center;opacity:0;visibility:visible;transform:none;");
    c.className = "tr3-clone";
    for (const k of c.querySelectorAll("*")) k.style.opacity = "1";
    box.appendChild(c);
    return { el: c, color: cs.color, bg: cs.backgroundColor, radius: parseFloat(cs.borderRadius) || 0 };
  }
  function rgba(s) {
    let h = String(s).trim();
    if (h[0] === "#") {
      if (h.length === 4) h = "#" + h[1] + h[1] + h[2] + h[2] + h[3] + h[3];
      return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16), 1];
    }
    const m = h.match(/[\d.]+/g) || [0, 0, 0, 0];
    return [+m[0] || 0, +m[1] || 0, +m[2] || 0, m.length > 3 ? +m[3] : 1];
  }
  function mix(a, b, u) {
    const p = rgba(a), q = rgba(b);
    const r = [];
    for (let i = 0; i < 4; i++) r.push(p[i] + (q[i] - p[i]) * u);
    return "rgba(" + r[0].toFixed(0) + "," + r[1].toFixed(0) + "," + r[2].toFixed(0) + "," + r[3].toFixed(3) + ")";
  }
  function bezier(x1, y1, x2, y2) {
    // cubic-bezier easing, solved for x by bisection (plain and exact enough for 16 frames)
    function at(a, b, s) { return 3 * a * s * (1 - s) * (1 - s) + 3 * b * s * s * (1 - s) + s * s * s; }
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let lo = 0, hi = 1, s = x;
      for (let i = 0; i < 30; i++) {
        s = (lo + hi) / 2;
        if (at(x1, x2, s) < x) lo = s; else hi = s;
      }
      return at(y1, y2, s);
    };
  }
  function lum(c) {
    const p = rgba(c);
    const lin = [];
    for (let i = 0; i < 3; i++) {
      const v = p[i] / 255;
      lin.push(v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4));
    }
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
  }
  function contrast(a, b) {
    const x = lum(a), y = lum(b);
    return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
  }
  function clamp(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }
  function expoIn(u) { return u <= 0 ? 0 : Math.pow(2, 10 * u - 10); }
  function shown(el) {
    // the real incoming anchor reads fully: every ancestor up to the scene opaque
    let op = 1, e = el;
    while (e && e !== root) { op *= parseFloat(getComputedStyle(e).opacity); e = e.parentElement; }
    return op >= 0.98;
  }

  const outList = scopes(OUT), inList = scopes(IN);
  let src = pick(outList, WANT);
  const name = src && !WANT ? src.getAttribute("data-anchor") : WANT;
  let dst = pick(inList, name);
  if (!src) src = hero(outList);
  if (!dst) dst = hero(inList);
  const groundColour = dst ? groundOf(dst) : "";
  ground.style.background = groundColour || "var(--bg)";
  const move = bezier(0.65, 0, 0.35, 1);
  let A = null, B = null, a = null, b = null, measured = false;
  function measure() {
    // once, on the first frame drawn: by then the web fonts are in, so the boxes are the real ones
    measured = true;
    if (!src || !dst) return;
    a = layoutBox(src);
    b = layoutBox(dst);
    A = cloneOf(src, a);
    B = cloneOf(dst, b);
  }

  function place(c, base, u) {
    // a clone of size `base` drawn on the box between a and b at progress u (centres travel, one uniform scale)
    const w = a.w + (b.w - a.w) * u, h = a.h + (b.h - a.h) * u;
    const cx = a.x + a.w / 2 + (b.x + b.w / 2 - a.x - a.w / 2) * u;
    const cy = a.y + a.h / 2 + (b.y + b.h / 2 - a.y - a.h / 2) * u;
    const s = Math.min(w / base.w, h / base.h);
    const x = cx - base.w * s / 2, y = cy - base.h * s / 2;
    c.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px) scale(" + s.toFixed(4) + ")";
  }
  function draw(f) {
    const active = f > 0.0001;
    // frames 0–6: the incoming ground rises from the bottom; 10–16: it lifts off the incoming scene
    const rise = expoIn(clamp(f / 6));
    ground.style.clipPath = "inset(" + ((1 - rise) * 100).toFixed(2) + "% 0 0 0)";
    ground.style.opacity = (1 - clamp((f - 10) / 6)).toFixed(3);
    if (!active) {
      if (A) { A.el.style.opacity = "0"; B.el.style.opacity = "0"; src.style.visibility = ""; dst.style.visibility = ""; }
      return;
    }
    if (!measured) measure();
    if (!A) return;
    const u = move(clamp((f - 4) / 10));
    // the anchor takes its new colours while the new ground rises behind it; when its new colour would vanish on that
    // ground (it really sits on a card), it keeps the old colours until the ground lifts off the incoming scene
    let cu = Math.max(u, clamp(f / 6));
    if (groundColour && contrast(B.color, groundColour) < 2.5) cu = clamp((f - 10) / 4);
    place(A.el, a, u);
    place(B.el, b, u);
    A.el.style.color = mix(A.color, B.color, cu);
    A.el.style.backgroundColor = mix(A.bg, B.bg, cu);
    A.el.style.borderRadius = (A.radius + (B.radius - A.radius) * cu).toFixed(1) + "px";
    const late = clamp((u - 0.35) / 0.5);
    let handed = f >= 14 && shown(dst);
    if (f >= 16 + HOLD * FPS) handed = true;
    A.el.style.opacity = !handed ? "1" : "0";        // the old look stays solid; the new look fades in over it
    B.el.style.opacity = !handed ? late.toFixed(3) : "0";
    src.style.visibility = "hidden";
    dst.style.visibility = !handed ? "hidden" : "";
  }
  const V = { f: 0 };
  draw(0);
  tl.fromTo(V, { f: 0 }, { f: 16 + HOLD * FPS, duration: (16 / FPS) + HOLD, ease: "none", immediateRender: false, onUpdate: () => draw(V.f) }, T0);
})();
"""


def anchor_match(X, t):
    """锚点匹配 Anchor Match: a match cut on one persistent element — the outgoing scene is covered by the incoming ground
    except the anchor (a number, a word, a card), which flies to its place in the next beat and takes on its new look."""
    X.css("tr3", CSS)
    prev, nxt = T2._scenes(X, t)
    nb = T2._beat(X, 0)
    want = nb.get("tr_anchor")
    fps = float(X.fps)
    t0 = t - 6.0 / fps
    hold = 0.8
    cid = X.uid("tr3a")
    X.clip(cid, t0, 16.0 / fps + hold + 0.05, '<div class="tr3-ground"></div>', "tr3", TRM.Z_TR)
    js = (JS.replace("__OUT__", T2.A.js([prev] if prev else []))
            .replace("__IN__", T2.A.js([nxt] if nxt else []))
            .replace("__WANT__", T2.A.js(str(want)) if want else "null")
            .replace("__T0__", f"{t0:.3f}")
            .replace("__FPS__", f"{fps:.0f}")
            .replace("__HOLD__", f"{hold}")
            .replace("__CID__", T2.A.js(cid)))
    X.tw(js)
    X.sfx(t0, "whoosh_soft")


TRS = {"anchor_match": anchor_match}      # dispatched by fx.transition()
FX = {}
