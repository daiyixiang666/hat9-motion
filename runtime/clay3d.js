// 九帽动效 · clay world — one continuous take on a seamless paper sweep: a small clay figure acts out every beat
// (it drags, jumps, pumps, pulls, stacks, hops, rolls and waves) and its action makes the chart change.
// Matte clay, plaster white, one terracotta object per beat, soft real shadows. Character and objects move "on twos"
// (a new pose every 2 frames at 30 fps); the camera moves smoothly. Deterministic: every frame is a function of the
// seek time alone (hf-seek). CFG + GLYPHS are injected by styles/clay.py.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";

const CFG = window.__H9_CLAY;
const GLYPHS = window.__H9_GLYPHS;
const W = CFG.w, H = CFG.h, PORTRAIT = H > W;
const COL = { sweep: 0xe9e2d6, plaster: 0xf6f1e7, clay: 0xd8c9b4, terra: 0xc8572f, dark: 0x3a332d, sage: 0x9aa58d, body: 0xd5bf9f };
const INK = "#3a332d", INK_EM = "#9a3e1b";
const SP = 3.6;                 // the camera trucks one set-up width to the right between beats (24 frames)
const WZ = -1.4, SR = 0.95;      // back wall plane and the sweep's curve radius

// ---------------------------------------------------------------- deterministic helpers
let _s = 7;
const rnd = () => { _s |= 0; _s = (_s + 0x6d2b79f5) | 0; let t = Math.imul(_s ^ (_s >>> 15), 1 | _s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => a + (b - a) * rnd();
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const lerp = (a, b, k) => a + (b - a) * k;
function hash3(x, y, z) { const s = Math.sin(x * 127.1 + y * 311.7 + z * 74.7) * 43758.5453; return s - Math.floor(s); }
function vnoise(x, y, z) {   // smooth value noise, -1..1
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf), w = zf * zf * (3 - 2 * zf);
  let acc = 0;
  for (let dz = 0; dz < 2; dz++) for (let dy = 0; dy < 2; dy++) for (let dx = 0; dx < 2; dx++) {
    const h = hash3(xi + dx, yi + dy, zi + dz);
    acc += h * (dx ? u : 1 - u) * (dy ? v : 1 - v) * (dz ? w : 1 - w);
  }
  return acc * 2 - 1;
}
// hand-made irregularity: every vertex moves by a smooth 3D noise field (same position -> same offset, so no cracks)
function lumpy(geo, size, amt = 0.009, freq = 3.2, seed = 1) {
  const p = geo.attributes.position, a = size * amt;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const f = freq / Math.max(size, 0.2);
    p.setXYZ(i, x + a * vnoise(x * f + seed, y * f, z * f), y + a * vnoise(x * f, y * f + seed * 1.7, z * f + 3.1), z + a * vnoise(x * f + 5.3, y * f, z * f + seed * 2.3));
  }
  p.needsUpdate = true;
  if (geo.index) geo.computeVertexNormals();
  return geo;
}

// ---------------------------------------------------------------- keyframe tracks (pure functions of time)
const EASE = {
  none: (p) => p, lin: (p) => p,
  in2: (p) => p * p, out2: (p) => 1 - (1 - p) * (1 - p), io2: (p) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2),
  in3: (p) => p * p * p, out3: (p) => 1 - Math.pow(1 - p, 3), io3: (p) => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
  sine: (p) => -(Math.cos(Math.PI * p) - 1) / 2,
  back: (p) => { const c1 = 2.2, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  back1: (p) => { const c1 = 1.3, c3 = c1 + 1; return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2); },
  rock: (p) => 1 - Math.cos(p * Math.PI * 4.5) * Math.exp(-4.2 * p) * (1 - p),          // damped rocking, settles at 1
  jig: (p) => 1 - Math.cos(p * Math.PI * 3) * Math.exp(-5 * p) * (1 - p),
  pulse: (p) => Math.sin(Math.PI * p),                                                   // there and back (value returns to start)
};
class Track {
  constructor(v) { this.v0 = v; this.cur = v; this.segs = []; this.last = -1e9; }
  to(t, dur, v, ease = "io2") {
    if (t < this.last - 1e-6) t = this.last;           // keep segments in order (a later key never rewrites the past)
    const seg = [t, t + Math.max(dur, 1e-4), this.cur, v, EASE[ease] || EASE.io2, ease === "pulse"];
    this.segs.push(seg); this.cur = ease === "pulse" ? this.cur : v; this.last = seg[1]; return this;
  }
  set(t, v) { return this.to(t, 1e-4, v, "none"); }
  at(t) {
    let val = this.v0;
    for (const s of this.segs) {
      if (t < s[0]) break;
      if (t >= s[1]) { val = s[5] ? s[2] : s[3]; continue; }
      const k = s[4]((t - s[0]) / (s[1] - s[0]));
      val = s[5] ? s[2] + (s[3] - s[2]) * k : s[2] + (s[3] - s[2]) * k;
      break;
    }
    return val;
  }
}
// an animated thing: named tracks; .to(t, dur, {x:..}, ease); .v(t) -> current values
function A(init) {
  const tr = {}; for (const k in init) tr[k] = new Track(init[k]);
  return {
    tr,
    to(t, dur, props, ease) { for (const k in props) { if (!tr[k]) tr[k] = new Track(props[k]); tr[k].to(t, dur, props[k], ease); } return this; },
    set(t, props) { for (const k in props) { if (!tr[k]) tr[k] = new Track(props[k]); tr[k].set(t, props[k]); } return this; },
    cur(k) { return tr[k].cur; },
    v(t) { const o = {}; for (const k in tr) o[k] = tr[k].at(t); return o; },
  };
}

// ---------------------------------------------------------------- renderer, sweep, light
const canvas = document.getElementById("w3d");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.VSMShadowMap;
renderer.localClippingEnabled = true;

const scene = new THREE.Scene();
scene.background = new THREE.Color(COL.sweep);
const VFOV = PORTRAIT ? 2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(37.8) / 2) / (W / H)) : THREE.MathUtils.degToRad(37.8);   // 35 mm: 37.8° across the short side
const HFOV = 2 * Math.atan(Math.tan(VFOV / 2) * (W / H));
const camera = new THREE.PerspectiveCamera(THREE.MathUtils.radToDeg(VFOV), W / H, 0.1, 80);

// a faint thumbprint / bump texture, drawn once from the seed (no downloaded textures)
const bumpTex = (() => {
  const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
  g.fillStyle = "#808080"; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 1400; i++) { const v = 110 + R(0, 40) | 0; g.fillStyle = `rgba(${v},${v},${v},.22)`; g.beginPath(); g.arc(R(0, 256), R(0, 256), R(1, 4.5), 0, 7); g.fill(); }
  for (let k = 0; k < 7; k++) {         // thumbprint arcs
    const cx = R(0, 256), cy = R(0, 256);
    for (let r = 4; r < 34; r += 3.2) { g.strokeStyle = `rgba(${r % 2 ? 150 : 100},${r % 2 ? 150 : 100},${r % 2 ? 150 : 100},.18)`; g.lineWidth = 1.2; g.beginPath(); g.arc(cx, cy, r, R(0, 3), R(3.5, 6)); g.stroke(); }
  }
  const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1.5, 1.5); return t;
})();
const MATS = {};
function clay(hex, bump = 0.012) {
  const k = hex + "|" + bump;
  if (!MATS[k]) MATS[k] = new THREE.MeshStandardMaterial({ color: hex, roughness: 0.92, metalness: 0, bumpMap: bumpTex, bumpScale: bump });
  return MATS[k];
}

// the sweep: floor curving up into the back wall, one colour
{
  const prof = [];
  for (let z = 14; z > WZ + SR; z -= 1) prof.push([z, 0]);
  for (let k = 0; k <= 16; k++) { const a = (k / 16) * Math.PI / 2; prof.push([WZ + SR - Math.sin(a) * SR, SR - Math.cos(a) * SR]); }
  prof.push([WZ, 4]); prof.push([WZ, 14]);
  const x0 = -16, x1 = 34, nx = 50;
  const pos = [], idx = [], nor = [], uv = [];
  for (let j = 0; j < prof.length; j++) for (let i = 0; i <= nx; i++) {
    pos.push(x0 + (x1 - x0) * i / nx, prof[j][1], prof[j][0]); uv.push(i / 4, j / 4); nor.push(0, 1, 0);
  }
  for (let j = 0; j < prof.length - 1; j++) for (let i = 0; i < nx; i++) {
    const a = j * (nx + 1) + i, b = a + 1, c = a + nx + 1, d = c + 1; idx.push(a, b, c, b, d, c);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3)); g.setAttribute("uv", new THREE.Float32BufferAttribute(uv, 2));
  g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: COL.sweep, roughness: 1, metalness: 0 }));
  m.receiveShadow = true; scene.add(m);
}
const hemi = new THREE.HemisphereLight(0xfbf7f0, 0xd6c8b4, 1.5); scene.add(hemi);
const key = new THREE.DirectionalLight(0xfff7ee, 2.2);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 14; key.shadow.blurSamples = 20; key.shadow.bias = -0.0006; key.shadow.normalBias = 0.01;
{ const sc = key.shadow.camera; sc.left = -5.5; sc.right = 5.5; sc.top = 5.5; sc.bottom = -5.5; sc.near = 1; sc.far = 30; sc.updateProjectionMatrix(); }
key.target = new THREE.Object3D(); scene.add(key, key.target);

// soft contact-shadow blob under every object
const blobTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d");
  const gr = g.createRadialGradient(64, 64, 2, 64, 64, 62); gr.addColorStop(0, "rgba(58,40,25,.55)"); gr.addColorStop(0.55, "rgba(58,40,25,.22)"); gr.addColorStop(1, "rgba(58,40,25,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
function blob(w, d, op = 0.75) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false, opacity: op }));
  m.rotation.x = -Math.PI / 2; m.scale.set(w, d, 1); m.position.y = 0.004; m.renderOrder = 1; return m;
}

// ---------------------------------------------------------------- flat type (canvas textures) and extruded type
const FONT_HEAD = "'h9-noto-serif-sc', 'h9-fraunces', serif";
const FONT_NUM = "'h9-fraunces', 'h9-noto-serif-sc', serif";
const FONT_LAB = "'h9-noto-sans-sc', sans-serif";
// draw "a *b* c" into a canvas: the *word* in terracotta. returns {tex, w, h} (px)
function richRuns(s) { const out = []; let em = false; for (const part of String(s).split("*")) { if (part) out.push([part, em]); em = !em; } return out; }
function textCanvas(str, { px = 92, font = FONT_HEAD, weight = 800, color = INK, em = INK_EM, bg = null, padX = 0, padY = 0, w = null, h = null, align = "left", lines = null, lh = 1.18 } = {}) {
  const c = document.createElement("canvas"), g = c.getContext("2d");
  const ls = lines || [str];
  g.font = `${weight} ${px}px ${font}`;
  const widths = ls.map((l) => richRuns(l).reduce((a, [t]) => a + g.measureText(t).width, 0));
  const tw = Math.max(...widths, 1);
  c.width = Math.ceil(w || tw + padX * 2); c.height = Math.ceil(h || px * lh * ls.length + padY * 2);
  if (bg) { g.fillStyle = bg; g.fillRect(0, 0, c.width, c.height); }
  g.font = `${weight} ${px}px ${font}`; g.textBaseline = "middle";
  ls.forEach((l, i) => {
    let x = align === "center" ? (c.width - widths[i]) / 2 : align === "right" ? c.width - padX - widths[i] : padX;
    const y = (c.height - px * lh * ls.length) / 2 + px * lh * (i + 0.5);
    for (const [t, isEm] of richRuns(l)) { g.fillStyle = isEm ? em : color; g.fillText(t, x, y); x += g.measureText(t).width; }
  });
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  return { tex, w: c.width, h: c.height, tw };
}
// a printed label: a plane carrying the text, lit like the surface it is printed on
function label(str, wWorld, opts = {}) {
  const t = textCanvas(str, { px: opts.px || 64, font: opts.font || FONT_LAB, weight: opts.weight || 700, color: opts.color || INK, em: opts.em || INK_EM, align: opts.align || "center", lines: opts.lines, padX: opts.padX || 6, padY: opts.padY || 4 });
  const hWorld = wWorld * t.h / t.w;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(wWorld, hWorld), new THREE.MeshStandardMaterial({ map: t.tex, transparent: true, roughness: 1, metalness: 0, polygonOffset: true, polygonOffsetFactor: -2, depthWrite: false }));
  m.receiveShadow = true; m.userData.h = hWorld; m.renderOrder = 2;
  return m;
}
const geoCache = {};
function glyphGeo(ch, depth, bevel) {
  const k = ch + "|" + depth + "|" + bevel;
  if (geoCache[k]) return geoCache[k];
  const gl = GLYPHS[ch]; if (!gl) return null;
  const sp = new THREE.ShapePath();
  for (const c of gl.p) {
    if (c[0] === "M") sp.moveTo(c[1], c[2]); else if (c[0] === "L") sp.lineTo(c[1], c[2]);
    else if (c[0] === "Q") sp.quadraticCurveTo(c[1], c[2], c[3], c[4]); else if (c[0] === "C") sp.bezierCurveTo(c[1], c[2], c[3], c[4], c[5], c[6]);
  }
  const shapes = sp.toShapes(false);
  const geo = new THREE.ExtrudeGeometry(shapes, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel * 0.8, bevelSegments: 4, curveSegments: 8 });
  lumpy(geo, 0.7, 0.008, 2.6, ch.charCodeAt(0) % 7);
  geo.computeVertexNormals();
  return (geoCache[k] = geo);
}
// extruded clay word; size = em in world units. baseline at y=0, left at x=0 unless centred. returns group with .userData {w, cap, glyphs}
function word3d(str, size, mat, { depth = 0.34, align = "center", track = -0.01 } = {}) {
  const grp = new THREE.Group(); let x = 0; const glyphs = [];
  for (const ch of str) {
    if (ch === " ") { x += 0.25; continue; }
    const gl = GLYPHS[ch]; if (!gl) continue;
    const geo = glyphGeo(ch, depth / size, 0.045);
    const piv = new THREE.Group(); const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.receiveShadow = true;
    m.position.set(-gl.a / 2, 0, -depth / size / 2); piv.add(m); piv.position.x = x + gl.a / 2; grp.add(piv); glyphs.push({ piv, a: gl.a, ch });
    x += gl.a + track;
  }
  const off = align === "center" ? -x / 2 : align === "right" ? -x : 0;
  glyphs.forEach((g) => (g.piv.position.x += off));
  grp.scale.setScalar(size);
  grp.userData = { w: x * size, cap: (GLYPHS.__cap || 0.7) * size, glyphs, left: off * size };
  return grp;
}
function rbox(w, h, d, r, hex, seed = 1) {
  const rr = Math.max(Math.min(w, h, d) * 0.12, Math.min(r, Math.min(w, h, d) * 0.45));
  const g = lumpy(new RoundedBoxGeometry(w, h, d, 4, rr), Math.min(w, h, d), 0.01, 2.2, seed);
  const m = new THREE.Mesh(g, clay(hex)); m.castShadow = true; m.receiveShadow = true; return m;
}

// ---------------------------------------------------------------- the clay figure
const FS = 1.15;           // figure scale
const CH = 1.29 * FS;      // standing height in world units (legs 0.22 + body + head)
function makeFigure() {
  const root = new THREE.Group(), sq = new THREE.Group(), hip = new THREE.Group(), torso = new THREE.Group(), head = new THREE.Group();
  root.add(sq); sq.add(hip); hip.position.y = 0.22; hip.add(torso);
  const bodyM = clay(COL.body, 0.016), dark = clay(COL.dark, 0.004), terra = clay(COL.terra, 0.01);
  const legs = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.set(s * 0.095, 0, 0); hip.add(p);
    const m = new THREE.Mesh(lumpy(new THREE.CapsuleGeometry(0.075, 0.08, 6, 14), 0.2, 0.012, 3, s + 3), bodyM); m.position.y = -0.12; m.castShadow = true; p.add(m);
    const foot = new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.085, 16, 12), 0.2, 0.012, 3, s + 5), bodyM); foot.scale.set(0.95, 0.55, 1.25); foot.position.set(0, -0.19, 0.03); foot.castShadow = true; p.add(foot);
    return p;
  });
  const body = new THREE.Mesh(lumpy(new THREE.CapsuleGeometry(0.215, 0.27, 8, 22), 0.43, 0.012, 2.6, 11), bodyM);
  body.scale.set(1.0, 1.0, 0.9); body.position.y = 0.3; body.castShadow = true; body.receiveShadow = true; torso.add(body);
  head.position.y = 0.62; torso.add(head);
  const skull = new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.255, 28, 22), 0.5, 0.012, 2.4, 17), bodyM);
  skull.scale.set(1.04, 0.93, 0.97); skull.position.y = 0.21; skull.castShadow = true; skull.receiveShadow = true; head.add(skull);
  const eyes = [-1, 1].map((s) => { const e = new THREE.Mesh(new THREE.SphereGeometry(0.031, 14, 10), dark); e.position.set(s * 0.088, 0.235, 0.236); e.scale.set(1, 1.25, 0.6); head.add(e); return e; });
  const scarf = new THREE.Mesh(lumpy(new THREE.TorusGeometry(0.18, 0.058, 12, 30), 0.35, 0.02, 3, 23), terra);
  scarf.rotation.x = Math.PI / 2; scarf.position.y = 0.58; scarf.castShadow = true; torso.add(scarf);
  const tailP = new THREE.Group(); tailP.position.set(0.09, 0.56, 0.15); torso.add(tailP);
  const tail = new THREE.Mesh(lumpy(new THREE.CapsuleGeometry(0.045, 0.14, 6, 12), 0.2, 0.02, 3, 29), terra); tail.position.y = -0.1; tail.scale.set(1.2, 1, 0.6); tail.castShadow = true; tailP.add(tail);
  const arms = [-1, 1].map((s) => {
    const p = new THREE.Group(); p.position.set(s * 0.215, 0.43, 0); torso.add(p);
    const m = new THREE.Mesh(lumpy(new THREE.CapsuleGeometry(0.058, 0.16, 6, 12), 0.2, 0.012, 3, s + 31), bodyM); m.position.y = -0.12; m.castShadow = true; p.add(m);
    return p;
  });
  const shadowBlob = blob(0.75, 0.55, 0.8); scene.add(shadowBlob);
  root.scale.setScalar(FS);
  scene.add(root);
  return { root, sq, hip, torso, head, legs, arms, eyes, tailP, shadowBlob };
}
const FIG = makeFigure();
// the figure's animated pose: position, facing, walk phase, squash, joints (radians)
const P = A({ x: -4, z: 0.25, y: 0, ry: Math.PI / 2, ph: 0, wk: 0, back: 0, sq: 0, lean: 0, tilt: 0, look: 0, turn: 0,
  aLx: 0, aLz: 0.12, aRx: 0, aRz: 0.12, legL: 0, legR: 0, sit: 0, blink: 0, hold: 0 });
const STRIDE = 0.3;
function face(t, dir, dur = 0.16) { const c = P.cur("ry"); while (dir - c > Math.PI) dir -= 2 * Math.PI; while (dir - c < -Math.PI) dir += 2 * Math.PI; P.to(t, dur, { ry: dir }, "io2"); }
const RIGHT = Math.PI / 2, LEFT = -Math.PI / 2, FRONT = 0;
function walkTo(t, dur, x, z = null, { back = false, faceEnd = null, turn = true } = {}) {
  const x0 = P.cur("x"), z0 = P.cur("z"); z = z === null ? z0 : z;
  const dx = x - x0, dz = z - z0, dist = Math.hypot(dx, dz);
  if (dist < 1e-3) return t;
  const dir = Math.atan2(dx, dz) + (back ? Math.PI : 0);
  if (turn) face(t - 0.08, dir, 0.14);
  P.to(t, 0.12, { wk: 1 }, "out2");
  P.to(t, dur, { x, z, ph: P.cur("ph") + (back ? -1 : 1) * dist / STRIDE * Math.PI }, "lin");
  P.to(t + dur - 0.1, 0.14, { wk: 0 }, "out2");
  if (faceEnd !== null) face(t + dur - 0.02, faceEnd, 0.18);
  return t + dur;
}
// a hop with anticipation, stretch on take-off and squash on landing (±12 %)
function hop(t, dur, x, yLand, height = 0.35, z = null) {
  const y0 = P.cur("y"); z = z === null ? P.cur("z") : z;
  P.to(t - 0.1, 0.1, { sq: -0.12 }, "out2");
  P.to(t, 0.1, { sq: 0.12 }, "out2");
  P.to(t, dur, { x, z }, "lin");
  P.to(t, dur / 2, { y: Math.max(y0, yLand) + height }, "out2");
  P.to(t + dur / 2, dur / 2, { y: yLand }, "in2");
  P.to(t + 0.12, dur - 0.16, { sq: 0 }, "io2");
  P.to(t + dur, 0.07, { sq: -0.12 }, "out2");
  P.to(t + dur + 0.07, 0.2, { sq: 0 }, "back1");
  return t + dur + 0.12;
}
function idleArms(t, dur = 0.25) { P.to(t, dur, { aLx: 0, aLz: 0.12, aRx: 0, aRz: 0.12 }, "io2"); }
function wipeBrow(t) {          // right hand sweeps across the forehead, head tips
  P.to(t, 0.18, { aRx: -2.55, aRz: -0.35, look: 0.15 }, "out2");
  P.to(t + 0.18, 0.32, { aRz: 0.55 }, "io2");
  P.to(t + 0.5, 0.18, { aRz: -0.3 }, "io2");
  P.to(t + 0.72, 0.28, { aRx: 0, aRz: 0.12, look: 0 }, "io2");
  P.to(t + 0.3, 0.3, { lean: -0.12 }, "io2"); P.to(t + 0.75, 0.3, { lean: 0 }, "io2");
  return t + 1.0;
}
function poseAt(t) {
  const p = P.v(t);
  const r = FIG.root; r.position.set(p.x, p.y, p.z); r.rotation.y = p.ry; r.scale.setScalar(FS);
  const sy = 1 + p.sq, sxz = 1 / Math.sqrt(sy); FIG.sq.scale.set(sxz, sy, sxz);
  const s = Math.sin(p.ph), bob = Math.abs(s) * 0.035 * p.wk;
  FIG.hip.position.y = 0.22 + bob - p.sit * 0.0;
  const breath = Math.sin(t * Math.PI * 2 / 1.7) * 0.016;
  FIG.torso.scale.set(1 - breath * 0.4, 1 + breath, 1 - breath * 0.4);
  FIG.torso.rotation.x = p.lean + 0.06 * p.wk; FIG.torso.rotation.z = p.tilt + Math.sin(p.ph) * 0.04 * p.wk;
  FIG.head.rotation.x = -p.look; FIG.head.rotation.y = p.turn;
  const legSwing = s * 0.62 * p.wk;
  FIG.legs[0].rotation.x = legSwing + p.legL - p.sit * 1.45; FIG.legs[1].rotation.x = -legSwing + p.legR - p.sit * 1.45;
  FIG.arms[0].rotation.x = -p.aLx - legSwing * 0.7; FIG.arms[0].rotation.z = -p.aLz;
  FIG.arms[1].rotation.x = -p.aRx + legSwing * 0.7; FIG.arms[1].rotation.z = p.aRz;
  FIG.tailP.rotation.x = 0.25 + Math.sin(t * 3.1) * 0.12 + p.wk * 0.4 + p.sq * 1.5;
  // blink: a quick close every ~2.6 s (held on twos)
  const bl = ((t + 0.7) % 2.6) < 0.1 ? 0.12 : 1;
  FIG.eyes.forEach((e) => (e.scale.y = 1.25 * bl * (1 - p.blink)));
  // contact shadow follows the feet; shrinks as the figure leaves the ground
  const lift = Math.max(0, p.y - (p.ground || 0));
  FIG.shadowBlob.position.set(p.x, 0.006 + (p.ground || 0), p.z); FIG.shadowBlob.scale.set(0.78 * FS / (1 + lift * 1.6), 0.56 * FS / (1 + lift * 1.6), 1);
  FIG.shadowBlob.material.opacity = 0.8 / (1 + lift * 2.4);
}
P.to(0, 0, { ground: 0 }, "none");

// ---------------------------------------------------------------- objects with their own tracks
const LIVE = [];     // per-frame updaters (called with the stepped time)
function animObj(obj, init) {
  const a = A({ x: obj.position.x, y: obj.position.y, z: obj.position.z, rx: 0, ry: obj.rotation.y, rz: 0, s: 1, sx: 1, sy: 1, sz: 1, ...init });
  LIVE.push((t) => { const v = a.v(t); obj.position.set(v.x, v.y, v.z); obj.rotation.set(v.rx, v.ry, v.rz); obj.scale.set(v.s * v.sx, v.s * v.sy, v.s * v.sz); obj.visible = v.s * v.sy > 0.002; });
  return a;
}
// pop up from the floor with squash-and-stretch
function popUp(a, t, { dur = 0.42, from = -0.2 } = {}) {
  a.set(t - 0.001, { sy: 0.0, sx: 1.25, sz: 1.25 });
  a.to(t, dur * 0.55, { sy: 1.16, sx: 0.9, sz: 0.9 }, "out2");
  a.to(t + dur * 0.55, dur * 0.25, { sy: 0.9, sx: 1.07, sz: 1.07 }, "io2");
  a.to(t + dur * 0.8, dur * 0.3, { sy: 1, sx: 1, sz: 1 }, "out2");
}
// the old set is pressed down into the floor as the camera leaves it
const SETS = [];
function sinkSet(i, t) {
  for (const a of SETS[i] || []) { a.to(t, 0.42, { sy: 0.0, sx: 1.18, sz: 1.18 }, "in2"); }
}

// ---------------------------------------------------------------- camera fit (from fov / aspect / bbox, no constants)
const PITCH = THREE.MathUtils.degToRad(-12);
const FIT = PORTRAIT ? { frac: 0.84, y0: 450, y1: 1290, cx: 540 } : { frac: 0.56, y0: 96, y1: 850, cx: 1180 };
function poseFor(C, d, ndcY, offX = 0) {
  const a = Math.atan(ndcY * Math.tan(VFOV / 2));          // the group centre sits this far above the optical axis
  const p2 = PITCH + a, L = d / Math.cos(a);
  const pos = new THREE.Vector3(C.x + offX, C.y - L * Math.sin(p2), C.z + L * Math.cos(p2));
  const look = new THREE.Vector3(pos.x, pos.y + Math.sin(PITCH) * 10, pos.z - Math.cos(PITCH) * 10);
  return { pos, look, d };
}
function fitStation(bb, O) {    // bb = [x0,y0,z0,x1,y1,z1] world
  const C = new THREE.Vector3((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2);
  const w = bb[3] - bb[0], h = bb[4] - bb[1];
  // first guess from the frustum: width -> distance, then refine on the projected corners
  const hFrac = (FIT.y1 - FIT.y0) / H;
  let d = Math.max((w / FIT.frac) / (2 * Math.tan(HFOV / 2)), (h / hFrac) / (2 * Math.tan(VFOV / 2)));
  const want = 1 - 2 * ((FIT.y0 + FIT.y1) / 2) / H;
  const wantX = 2 * FIT.cx / W - 1;
  let ny = want, ox = 0, st = poseFor(C, d, ny, ox);
  const corners = [];
  const cornersY = [];         // width from the whole box; height measured on the group's mid depth (where the chart stands)
  for (const x of [bb[0], bb[3]]) for (const y of [bb[1], bb[4]]) for (const z of [bb[2], bb[5]]) corners.push(new THREE.Vector3(x, y, z));
  for (const x of [bb[0], bb[3]]) for (const y of [bb[1], bb[4]]) cornersY.push(new THREE.Vector3(x, y, Math.min(Math.max(0, bb[2]), bb[5])));
  for (let it = 0; it < 8; it++) {
    let sx0 = 1e9, sx1 = -1e9, sy0 = 1e9, sy1 = -1e9;
    for (const c of corners) { const [sx] = project(st, c); sx0 = Math.min(sx0, sx); sx1 = Math.max(sx1, sx); }
    for (const c of cornersY) { const [, sy] = project(st, c); sy0 = Math.min(sy0, sy); sy1 = Math.max(sy1, sy); }
    const f = Math.max((sx1 - sx0) / (FIT.frac * W), (sy1 - sy0) / (FIT.y1 - FIT.y0));
    const cy = 1 - (sy0 + sy1) / H;              // ndc of the projected box centre
    const cxn = (sx0 + sx1) / W - 1;
    d *= f; ny += want - cy; ox -= (wantX - cxn) * d * Math.tan(HFOV / 2);
    st = poseFor(C, d, ny, ox);
  }
  if (PORTRAIT && O !== undefined) {   // the figure stays 300–380 px tall on screen (aim 310–370)
    for (let it = 0; it < 4; it++) {
      const a = project(st, new THREE.Vector3(O, 0, 0.2)), b = project(st, new THREE.Vector3(O, CH, 0.2)), px = a[1] - b[1];
      const k = px > 376 ? px / 376 : px < 300 ? px / 300 : 1;
      if (k === 1) break;
      d *= k; st = poseFor(C, d, ny, ox);
    }
  }
  return st;
}
// a screen point (px) -> where its ray meets a plane (z = const or y = const), for a camera pose
const _cam = new THREE.PerspectiveCamera(THREE.MathUtils.radToDeg(VFOV), W / H, 0.1, 80);
function screenTo(st, px, py, plane) {
  _cam.position.copy(st.pos); _cam.lookAt(st.look); _cam.updateMatrixWorld(); _cam.updateProjectionMatrix();
  const v = new THREE.Vector3((px / W) * 2 - 1, 1 - (py / H) * 2, 0.5).unproject(_cam);
  const dir = v.sub(st.pos).normalize();
  const k = plane.z !== undefined ? (plane.z - st.pos.z) / dir.z : (plane.y - st.pos.y) / dir.y;
  return st.pos.clone().add(dir.multiplyScalar(k));
}
function project(st, p) {
  _cam.position.copy(st.pos); _cam.lookAt(st.look); _cam.updateMatrixWorld(); _cam.updateProjectionMatrix();
  const v = p.clone().project(_cam); return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H];
}

// ---------------------------------------------------------------- the headline printed on the back wall
const HEAD_RECT = PORTRAIT ? { x0: 110, x1: 960, y0: 230, y1: 400 } : { x0: 110, x1: 1180, y0: 70, y1: 222 };
function wallHead(st, head, sub, tIn, tOut) {
  if (!head) return;
  const r = HEAD_RECT;
  const pxHead = PORTRAIT ? 92 : 84, pxSub = PORTRAIT ? 38 : 34;
  // fit: 84–100 px display serif; shrink only down to 84 if the line is long
  const probe = textCanvas(head, { px: pxHead * 2 });
  const maxW = (r.x1 - r.x0) * 2;
  const k = Math.min(1, maxW / probe.tw), headPx = Math.max(52, pxHead * k);
  const cw = (r.x1 - r.x0) * 2, chh = (r.y1 - r.y0) * 2;
  const c = document.createElement("canvas"); c.width = cw; c.height = chh; const g = c.getContext("2d");
  g.textBaseline = "alphabetic";
  let x = 0; const base = headPx * 2 * 0.98;
  g.font = `800 ${headPx * 2}px ${FONT_HEAD}`;
  for (const [t, em] of richRuns(head)) { g.fillStyle = em ? INK_EM : INK; g.fillText(t, x, base); x += g.measureText(t).width; }
  if (sub) {
    g.font = `600 ${pxSub * 2}px ${FONT_LAB}`; g.fillStyle = "#5b5249";
    let xs = 4; for (const [t, em] of richRuns(sub)) { g.fillStyle = em ? INK_EM : "#5b5249"; g.fillText(t, xs, base + pxSub * 2 * 1.75); xs += g.measureText(t).width; }
  }
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const tl = screenTo(st, r.x0, r.y0, { z: WZ + 0.01 }), br = screenTo(st, r.x1, r.y1, { z: WZ + 0.01 });
  const ww = br.x - tl.x, hh = tl.y - br.y;
  const clipL = new THREE.Plane(new THREE.Vector3(1, 0, 0), -tl.x), clipR = new THREE.Plane(new THREE.Vector3(-1, 0, 0), tl.x);
  const mat = new THREE.MeshStandardMaterial({ map: tex, transparent: true, roughness: 1, metalness: 0, depthWrite: false, clippingPlanes: [clipL, clipR] });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(ww, hh), mat);
  m.position.set(tl.x + ww / 2, br.y + hh / 2, WZ + 0.012); m.receiveShadow = true; scene.add(m);
  // printed on by a roller sweeping left to right; lifted off the same way when the camera leaves
  const a = A({ r: tl.x, l: tl.x });
  a.to(tIn, 0.26, { r: tl.x + ww + 0.05 }, "out2");
  if (tOut !== null) a.to(tOut, 0.26, { l: tl.x + ww + 0.05 }, "in2");
  LIVE.push((t) => { const v = a.v(t); clipR.constant = v.r; clipL.constant = -v.l; m.visible = v.r > v.l + 1e-3; });
  // the roller itself: a small clay cylinder that prints the line
  const roll = new THREE.Mesh(lumpy(new THREE.CylinderGeometry(0.05, 0.05, hh * 1.06, 18), 0.1, 0.02, 3, 3), clay(COL.clay));
  roll.position.set(tl.x, br.y + hh / 2, WZ + 0.07); roll.castShadow = true; scene.add(roll);
  LIVE.push((t) => { const v = a.v(t); const pIn = (t - tIn) / 0.26; const on = pIn > 0 && pIn < 1.02; roll.visible = on; roll.position.x = v.r; roll.rotation.y = v.r * 6; });
}

// ---------------------------------------------------------------- floor props below the stage (pebbles, a block)
function props(st, i) {
  const spots = PORTRAIT ? [[170, 1650, "p"], [860, 1600, "b"], [610, 1820, "p"]] : [[130, 1000, "p"], [1800, 960, "b"]];
  spots.forEach(([sx, sy, k], j) => {
    const p = screenTo(st, sx, sy, { y: 0 });
    let m;
    if (k === "b") { m = rbox(0.34, 0.22, 0.3, 0.06, j % 2 ? COL.plaster : COL.clay, i * 7 + j); m.position.set(p.x, 0.11, p.z); m.rotation.y = R(-0.5, 0.5); }
    else if (k === "s") { m = new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.09, 16, 12), 0.2, 0.06, 2.5, i + 9), clay(COL.clay)); m.scale.set(1.2, 0.55, 1); m.position.set(p.x, 0.04, p.z); m.castShadow = true; }
    else { m = new THREE.Mesh(lumpy(new THREE.SphereGeometry(0.16, 20, 14), 0.3, 0.06, 2.5, i + j), clay(j % 2 ? COL.clay : COL.plaster)); m.scale.set(R(0.9, 1.3), 0.5, R(0.8, 1.1)); m.position.set(p.x, 0.07, p.z); m.castShadow = true; m.receiveShadow = true; }
    scene.add(m);
    const b = blob(0.6, 0.5, 0.6); b.position.set(p.x, 0.004, p.z); scene.add(b);
  });
}

// ---------------------------------------------------------------- the eight acts
// each returns { bb: local bbox [x0,y0,z0,x1,y1,z1], parts: [anims to sink on exit] }. O = set origin x.
function T(b, k, dflt) { const v = b.p[k]; return v === undefined || v === null ? dflt : v; }
const NUMMAT = () => clay(COL.terra, 0.01);
function string3d() {        // a drag string: a thin clay cylinder stretched between two points each frame
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 1, 6), clay(COL.dark, 0)); m.castShadow = true; scene.add(m); return m;
}
function stretch(m, a, b) { const d = b.clone().sub(a); const L = d.length(); m.position.copy(a).addScaledVector(d, 0.5); m.scale.set(1, Math.max(L, 1e-3), 1); m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), d.normalize()); }

const ACTS = {};
// 1 · the figure walks in from the left dragging the extruded numeral on a string, lets go; it rocks and settles
ACTS.title = (b, O, a, k, first) => {
  const txt = T(b, "obj", "2024");
  const N = word3d(txt, T(b, "size", 2.0), NUMMAT(), { depth: 0.5 });
  const w = N.userData.w, nx = O - 0.35;
  const piv = new THREE.Group(); piv.add(N); N.position.set(0, 0, 0); scene.add(piv);
  const nb = blob(w * 1.15, 0.9, 0.7); piv.add(nb); nb.position.y = 0.004;
  const endX = nx + w / 2 + 0.55;
  const L = endX - nx + 0.15;             // string length from the hand to the numeral's right edge
  const t0 = a, walkDur = 2.1 * k;
  const startX = first ? O - 2.0 : P.cur("x");
  const na = animObj(piv, { x: startX - L, y: 0, z: 0, rz: 0 });
  if (first) { P.set(0, { x: startX, z: 0.12, ry: RIGHT }); }
  // drag: lean forward, right arm back holding the string
  P.to(t0 - 0.05, 0.2, { lean: 0.22, aRx: -0.7, aRz: 0.25, aLx: 0.35 }, "out2");
  walkTo(t0, walkDur, endX, 0.12, { turn: !first });
  na.to(t0 + 0.05, walkDur, { x: nx }, "lin");
  na.to(t0, 0.25, { rz: -0.09 }, "out2");          // tipped back on its trailing edge while dragged
  const tLet = t0 + walkDur + 0.12;
  P.to(tLet, 0.2, { lean: 0, aRx: 0.25, aRz: 0.12, aLx: 0 }, "out2");
  na.to(tLet, 1.3 * Math.max(k, 0.8), { rz: 0 }, "rock");
  na.to(tLet, 0.12, { y: 0.0 }, "none");
  face(tLet + 0.3, LEFT, 0.2);
  const capH = N.userData.cap, topX = nx + w / 2 - 0.42;
  hop(tLet + 0.62, 0.5, topX, capH, 0.45, 0.06);
  P.to(tLet + 1.0, 0.01, { ground: capH }, "none");
  na.to(tLet + 1.1, 0.08, { rz: -0.03 }, "out2"); na.to(tLet + 1.18, 0.35, { rz: 0 }, "jig");
  const tL2 = tLet + 0.85;
  face(tL2 + 0.35, FRONT, 0.25);
  P.to(tL2 + 0.4, 0.3, { turn: -0.55, look: 0.12, aRx: 0 }, "io2");
  P.to(tL2 + 0.75, 0.2, { sq: -0.06 }, "out2"); P.to(tL2 + 0.95, 0.25, { sq: 0 }, "back1");    // a small proud bounce
  // string: from the hand to the numeral's top-right corner until let go, then it drops to the floor and is gone
  const s = string3d();
  LIVE.push((t) => {
    const v = P.v(t), nv = na.v(t);
    if (t > tLet + 0.35 || t < (first ? 0 : t0 - 0.5)) { s.visible = false; return; }
    s.visible = true;
    const hand = new THREE.Vector3(v.x - 0.34 * Math.sin(v.ry), 0.5 * FS + v.y, v.z + 0.1);
    const end = new THREE.Vector3(nv.x + w / 2 + 0.02, 0.45 + Math.sin(nv.rz) * w * 0.5, 0.05);
    if (t > tLet) { const k2 = (t - tLet) / 0.35; hand.y = lerp(hand.y, 0.02, k2); end.y = lerp(end.y, 0.03, k2); }
    stretch(s, hand, end);
  });
  // pivot of the rocking: the numeral's base centre
  // unit tag pops up from the floor after the numeral settles
  const parts = [na];
  if (b.p.unit) {
    const tg = new THREE.Group(); const bx = rbox(0.95, 0.26, 0.16, 0.05, COL.plaster, 4); bx.position.y = 0.13; tg.add(bx);
    const lb = label(b.p.unit, 0.86, { px: 60 }); lb.position.set(0, 0.13, 0.082); tg.add(lb);
    tg.position.set(nx + w / 2 - 0.35, 0, 0.62); tg.rotation.y = -0.12; scene.add(tg);
    const ta = animObj(tg, { sy: 0 }); popUp(ta, tLet + 0.55); parts.push(ta);
    const tb = blob(1.1, 0.4, 0.6); tb.position.set(0, 0.004, 0); tg.add(tb);
  }
  return { hero: [nx - w / 2 - O, nx + w / 2 - O], heroY: [0, N.userData.cap], bb: [nx - w / 2 - O - 0.05, 0, -0.3, Math.max(nx + w / 2 + 0.1, topX + 0.3) - O, N.userData.cap + CH + 0.05, 0.75], parts, end: { x: topX, z: 0.06, y: N.userData.cap } };
};

// 2 · it jumps on a clay plunger; each landing raises the plinth and pops the next digit up on top of it
ACTS.number = (b, O, a, k) => {
  const val = String(T(b, "value", "13")), unit = T(b, "unit", "");
  const size = T(b, "size", 2.3);
  let x = 0; const items = [];
  for (const ch of val) { const gw = (GLYPHS[ch] ? GLYPHS[ch].a : 0.6) * size; items.push({ ch, s: size, x: x + gw / 2, gw }); x += gw - 0.03; }
  if (unit) { const s = size * 0.45; const gw = (GLYPHS[unit] ? GLYPHS[unit].a : 0.8) * s; items.push({ ch: unit, s, x: x + gw / 2 + 0.02, gw }); x += gw + 0.04; }
  const tot = x, x0 = O - tot / 2 + 0.3;
  const PH = T(b, "plinth", 1.5), pw = tot + 0.16, pX = x0 + tot / 2;
  const parts = [];
  // the plinth the digits stand on: it rises a step with every landing
  const plin = new THREE.Group(); scene.add(plin); plin.position.set(pX, 0, -0.05);
  const pbox = rbox(pw, PH, 0.8, 0.1, COL.plaster, 70); pbox.position.y = PH / 2; plin.add(pbox);
  const pb = blob(pw * 1.15, 1.1, 0.7); plin.add(pb);
  if (b.p.label) { const lb = label(b.p.label, Math.min(pw * 0.62, 2.1), { px: 64 }); lb.position.set(pw * 0.12, PH * 0.5, 0.405); plin.add(lb); }
  const pa = animObj(plin, { sy: 0 }); parts.push(pa);
  // the plunger: a sage box with a T-handle, left of the plinth
  const plX = x0 - 0.5;
  const pl = new THREE.Group(); scene.add(pl); pl.position.set(plX, 0, 0.42);
  const base = rbox(0.5, 0.36, 0.46, 0.08, COL.sage, 6); base.position.y = 0.18; pl.add(base);
  const rodG = new THREE.Group(); pl.add(rodG); rodG.position.y = 0.36;
  const rod = new THREE.Mesh(lumpy(new THREE.CylinderGeometry(0.045, 0.045, 0.3, 12), 0.1, 0.02, 3, 2), clay(COL.dark)); rod.position.y = 0.15; rod.castShadow = true; rodG.add(rod);
  const bar = rbox(0.5, 0.1, 0.18, 0.04, COL.sage, 8); bar.position.y = 0.33; rodG.add(bar);
  const plb = blob(0.8, 0.7, 0.7); pl.add(plb);
  const rodA = animObj(rodG, { y: 0.36 });
  const plA = animObj(pl, { sy: 0 }); popUp(plA, b.e + 0.1, { dur: 0.4 }); parts.push(plA);
  const TOP = 0.36 + 0.33 + 0.05;
  walkTo(b.e, a - b.e - 0.12, plX - 0.55, 0.42, { faceEnd: RIGHT });
  hop(a, 0.44 * Math.max(k, 0.8), plX, TOP, 0.42, 0.42);
  P.to(a + 0.3, 0.01, { ground: TOP }, "none");
  face(a + 0.2, RIGHT * 0.45, 0.2);
  const nums = items.map((it) => {
    const g = word3d(it.ch, it.s, NUMMAT(), { depth: 0.46 }); const piv = new THREE.Group(); piv.add(g); scene.add(piv);
    piv.position.set(x0 + it.x, PH, -0.05);
    const na = animObj(piv, { sy: 0, y: 0 }); parts.push(na); return na;
  });
  const n = nums.length;
  let t = a + 0.44 * Math.max(k, 0.8);
  pa.set(t - 0.01, { sy: 0.02 });
  for (let j = 0; j < n; j++) {
    const hy = PH * (j + 1) / n;
    rodA.to(t, 0.08, { y: 0.2 }, "out2"); rodA.to(t + 0.1, 0.22, { y: 0.36 }, "back1");
    P.to(t, 0.08, { y: TOP - 0.16 }, "out2");
    pa.to(t + 0.04, 0.26, { sy: (j + 1) / n }, "back1");
    for (let q = 0; q < j; q++) nums[q].to(t + 0.04, 0.26, { y: hy }, "back1");
    nums[j].set(t + 0.03, { y: hy });
    popUp(nums[j], t + 0.06, { dur: 0.46 });
    if (j < n - 1) { P.to(t + 0.1, 0.22, { y: TOP }, "out2"); t = hop(t + 0.32, 0.3 * Math.max(k, 0.75), plX, TOP, 0.28) - 0.12; }
    else { P.to(t + 0.1, 0.18, { y: TOP }, "out2"); t += 0.3; }
  }
  face(t, 0.5, 0.25);
  P.to(t + 0.1, 0.35, { look: 0.55, turn: 0.3, lean: -0.1 }, "io2");
  P.to(t + 0.9, 0.3, { aRz: 1.1, aRx: 0.5 }, "out2"); P.to(t + 1.5, 0.3, { aRz: 0.12, aRx: 0 }, "io2");
  const capH = (GLYPHS.__cap || 0.7) * size;
  return { hero: [x0 - O, x0 + tot - O], heroY: [PH, PH + capH], bb: [plX - 0.35 - O, 0, -0.45, x0 + tot - O + 0.08, PH + capH + 0.05, 0.45], parts, end: { x: plX, z: 0.42, y: TOP } };
};

// 3 · it works a pump from behind: two columns rise from the floor in true ratio; it wipes its brow on the pump
ACTS.compare = (b, O, a, k) => {
  const items = b.p.items && b.p.items.length >= 2 ? b.p.items.slice(0, 2) : [{ label: "A", value: 1 }, { label: "B", value: 0.8 }];
  const hi = Math.max(items[0].value, items[1].value) || 1;
  const HMAX = T(b, "hmax", 2.75), CW = 1.35, CD = 0.7;
  const xs = [O - 1.12, O + 0.33];
  const winner = items[0].value >= items[1].value ? 0 : 1;
  const parts = [];
  const cols = items.map((it, j) => {
    const h = Math.max(0.12, HMAX * (it.value / hi));
    const win = j === winner;
    const g = new THREE.Group(); g.position.set(xs[j], 0, 0); scene.add(g);
    const col = rbox(CW, h, CD, 0.1, win ? COL.terra : COL.plaster, 10 + j); col.position.y = h / 2; g.add(col);
    const bl = blob(CW * 1.35, 1.0, 0.7); bl.position.set(0, 0.004, 0); g.add(bl);
    if (it.label) { const lb = label(it.label, CW * 0.72, { px: 64, color: win ? "#fbf3e8" : INK }); lb.position.set(0, 0.24, CD / 2 + 0.005); g.add(lb); }
    const ga = animObj(g, { sy: 0 }); parts.push(ga); ga.set(b.e + 0.2 + j * 0.08, { sy: 0.03 });
    let na = null, va = null;
    const disp = String(it.display === "" ? "" : (it.display || it.value));
    if (disp && win) {           // the bigger value: extruded clay numerals riding on top
      const nv = word3d(disp, T(b, "vsize", 1.16), clay(COL.terra), { depth: 0.3 });
      const np = new THREE.Group(); np.add(nv); scene.add(np); np.position.set(xs[j] + 0.12, h + 0.02, 0.0);
      na = animObj(np, { sy: 0, y: 0.02 }); parts.push(na);
    } else if (disp) {           // the smaller value: printed big on the column's face
      const lv = label(disp, CW * 0.86, { px: 120, font: FONT_NUM, weight: 700 }); lv.position.set(0, h - 0.42, CD / 2 + 0.006); g.add(lv);
      va = animObj(lv, { s: 0, y: h - 0.42, z: CD / 2 + 0.006 });
    }
    return { ga, na, va, h };
  });
  // the pump: plaster box, the lever points back toward the figure behind it
  const pX = O + 1.42;
  const pump = new THREE.Group(); pump.position.set(pX, 0, 0.2); scene.add(pump);
  const box = rbox(0.38, 0.42, 0.38, 0.07, COL.plaster, 12); box.position.y = 0.21; pump.add(box);
  const lev = new THREE.Group(); lev.position.set(0, 0.44, 0); pump.add(lev);
  const arm = new THREE.Mesh(lumpy(new THREE.CapsuleGeometry(0.035, 0.42, 4, 10), 0.1, 0.02, 3, 4), clay(COL.dark)); arm.rotation.z = Math.PI / 2; arm.position.x = 0.2; arm.castShadow = true; lev.add(arm);
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.06, 14, 10), clay(COL.dark)); knob.position.x = 0.44; lev.add(knob);
  lev.rotation.y = Math.PI / 2;
  const pa = animObj(pump, { sy: 0 }); parts.push(pa); popUp(pa, b.e + 0.1, { dur: 0.4 });
  const la = animObj(lev, { rz: 0.35, ry: Math.PI / 2 });
  const pb = blob(0.7, 0.6, 0.7); pb.position.set(0, 0.004, 0); pump.add(pb);
  const cx = pX, cz = -0.48;
  let t = walkTo(b.e, a - b.e + 0.1, cx, cz, { faceEnd: FRONT });
  P.to(t, 0.18, { aLx: 1.2, aRx: 1.2, aLz: -0.05, aRz: -0.05, lean: 0.12 }, "out2");
  const step = 0.3 * Math.max(k, 0.8);
  t += 0.16;
  for (let n = 0; n < 6; n++) {
    const c = cols[n < 3 ? 0 : 1], frac = ((n % 3) + 1) / 3;
    la.to(t, step * 0.45, { rz: -0.3 }, "in2"); la.to(t + step * 0.45, step * 0.55, { rz: 0.35 }, "out2");
    P.to(t, step * 0.45, { sq: -0.1, lean: 0.3, aLx: 0.85, aRx: 0.85 }, "in2"); P.to(t + step * 0.45, step * 0.55, { sq: 0, lean: 0.12, aLx: 1.2, aRx: 1.2 }, "out2");
    c.ga.to(t + step * 0.4, step * 0.5, { sy: frac * 1.05 }, "out2"); c.ga.to(t + step * 0.9, step * 0.3, { sy: frac }, "io2");
    if (n % 3 === 2) {
      if (c.na) { c.na.set(t + step * 0.85, { y: c.h + 0.02 }); popUp(c.na, t + step * 0.9, { dur: 0.4 }); }
      if (c.va) c.va.to(t + step * 0.9, 0.25, { s: 1 }, "back");
    }
    t += step;
  }
  idleArms(t, 0.2);
  const ex = pX, ez = 0.2;
  t = hop(t + 0.12, 0.42, ex, 0.42, 0.3, ez);
  P.to(t - 0.15, 0.01, { ground: 0.42 }, "none");
  la.to(t - 0.15, 0.1, { rz: -0.3 }, "out2");
  face(t, -0.3, 0.2);
  t = wipeBrow(t + 0.05);
  P.to(t - 0.2, 0.3, { look: 0.45, turn: winner ? -0.5 : -0.9 }, "io2");
  const topH = HMAX + (GLYPHS.__cap || 0.7) * T(b, "vsize", 1.16);
  return { hero: [xs[0] - CW / 2 - O, xs[1] + CW / 2 - O], heroY: [0, topH], bb: [xs[0] - CW / 2 - O - 0.05, 0, -0.5, pX + 0.3 - O, topH + 0.05, 0.3], parts, end: { x: ex, z: ez, y: 0.42 } };
};

// 4 · a clay wheel standing on its rim, like a coin: it pulls out the true-fraction wedge and drags it 0.6 units away
function sectorGeo(r, th, a0, a1) {
  const s = new THREE.Shape(); s.moveTo(0, 0);
  const n = Math.max(4, Math.ceil((a1 - a0) / 0.06));
  for (let i = 0; i <= n; i++) { const t = a0 + (a1 - a0) * i / n; s.lineTo(Math.cos(t) * r, Math.sin(t) * r); }
  s.lineTo(0, 0);
  const g = new THREE.ExtrudeGeometry(s, { depth: th - 0.1, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05, bevelSegments: 4, curveSegments: 24 });
  g.translate(0, 0, -(th - 0.1) / 2);
  return lumpy(g, r, 0.007, 2.4, 5);
}
ACTS.share = (b, O, a, k) => {
  const pct = clamp(Number(T(b, "value", 46)), 1, 99) / 100;
  const r = T(b, "radius", 1.32), th = 0.55, cx = O - 0.45, cy = r + 0.02;
  const half = pct * Math.PI;
  const parts = [];
  const gRest = new THREE.Group(); gRest.position.set(cx, cy, 0); scene.add(gRest);
  const rest = new THREE.Mesh(sectorGeo(r, th, half + 0.015, 2 * Math.PI - half - 0.015), clay(COL.plaster)); rest.castShadow = true; rest.receiveShadow = true; gRest.add(rest);
  const gW = new THREE.Group(); gW.position.set(cx, cy, 0); scene.add(gW);
  const wedge = new THREE.Mesh(sectorGeo(r, th, -half, half), clay(COL.terra)); wedge.castShadow = true; wedge.receiveShadow = true; gW.add(wedge);
  // chocks that hold the wheel upright
  [-1, 1].forEach((s) => { const c = rbox(0.34, 0.2, th + 0.2, 0.06, COL.clay, 80 + s); c.position.set(s * 0.42, -cy + 0.1, 0); gRest.add(c); });
  const bl = blob(r * 2.2, 1.2, 0.7); bl.position.set(0, -cy + 0.004, 0); gRest.add(bl);
  const wbl = blob(r * 1.1, 1.0, 0.6); wbl.position.set(r * 0.4, -cy + 0.004, 0); gW.add(wbl);
  // the figure on the wedge: big numerals, the share label under them; the rest of the wheel carries the total
  const disp = String(T(b, "display", Math.round(pct * 100) + "%"));
  const numStr = disp.replace("%", ""), hasPct = disp.includes("%");
  const nm = word3d(numStr, T(b, "vsize", 1.25), clay(COL.plaster, 0.008), { depth: 0.16 });
  nm.position.set(r * 0.5, 0.0, th / 2 + 0.04); gW.add(nm);
  if (hasPct) { const pc = word3d("%", 0.6, clay(COL.plaster, 0.008), { depth: 0.12 }); pc.position.set(r * 0.5, -0.58, th / 2 + 0.04); gW.add(pc); }
  if (b.p.label) { const lw = label(b.p.label, 0.9, { px: 64, color: "#fbf3e8" }); lw.position.set(r * 0.5, -0.92, th / 2 + 0.01); gW.add(lw); }
  if (b.p.rest) { const lr = label(b.p.rest, 1.2, { px: 64, lines: String(b.p.rest).split("|") }); lr.position.set(-r * 0.5, 0.05, th / 2 + 0.01); gRest.add(lr); }
  const ra = animObj(gRest, { sy: 0, y: cy }); parts.push(ra);
  const wa = animObj(gW, { sy: 0, y: cy }); parts.push(wa);
  popUp(ra, b.e + 0.2, { dur: 0.45 }); popUp(wa, b.e + 0.2, { dur: 0.45 });
  // the figure takes the wedge's rim from the right and walks backwards, pulling it out along the floor
  const pull = 0.6, grabX = cx + r + 0.3;
  let t = walkTo(b.e, a - b.e, grabX, 0.5, { faceEnd: LEFT });
  P.to(t, 0.2, { aLx: 1.35, aRx: 1.35, aLz: -0.12, aRz: -0.12, lean: 0.25, sq: -0.06 }, "out2");
  t += 0.25;
  P.to(t, 0.2, { lean: -0.28, sq: 0 }, "out2");
  const tP = t + 0.08, dP = 0.85 * Math.max(k, 0.8);
  P.to(tP, 0.1, { wk: 1 }, "out2");
  P.to(tP, dP, { x: grabX + pull, ph: P.cur("ph") - pull / STRIDE * Math.PI }, "io2");
  P.to(tP + dP - 0.1, 0.14, { wk: 0 }, "out2");
  wa.to(tP + 0.04, dP, { x: cx + pull }, "io2");
  wa.to(tP, 0.12, { rz: -0.04 }, "out2"); wa.to(tP + dP, 0.3, { rz: 0 }, "jig");
  t = tP + dP + 0.1;
  P.to(t, 0.25, { lean: 0, aLx: 0, aRx: 0, aLz: 0.12, aRz: 0.12 }, "io2");
  face(t + 0.15, 0.2, 0.25);
  P.to(t + 0.45, 0.25, { aLx: 1.5, aLz: 0.5, turn: -0.45, look: 0.05 }, "out2");
  return { hero: [cx - r - O, cx + r + pull - O], heroY: [0, 2 * r], bb: [cx - r - O - 0.06, 0, -0.35, grabX + pull + 0.32 - O, 2 * r + 0.06, 0.45], parts, end: { x: grabX + pull, z: 0.5 } };
};

// 5 · it builds a staircase of slabs with true-ratio widths, carrying the last one overhead and setting it on top
ACTS.rank = (b, O, a, k) => {
  const items = (b.p.items || []).slice(0, 4);
  while (items.length < 4) items.push({ label: "", value: (items[items.length - 1] || { value: 1 }).value * 0.6 });
  const vmax = Math.max(...items.map((x) => x.value)) || 1;
  const WMAX = T(b, "wmax", 3.0), SD = 0.8, L = O - WMAX / 2 - 0.2;
  const HS = [1.0, 0.75, 0.75, 0.75];
  const parts = [];
  let y0 = 0;
  const slabs = items.map((it, j) => {
    const w = Math.max(0.12, WMAX * it.value / vmax), h = HS[j];
    const g = new THREE.Group(); scene.add(g);
    const sl = rbox(w, h, SD, 0.06, j === 0 ? COL.terra : COL.plaster, 20 + j); g.add(sl);
    g.position.set(L + w / 2, y0 + h / 2, 0);
    const ga = animObj(g, {}); parts.push(ga);
    const s = { g, ga, w, h, y: y0 + h / 2, top: y0 + h };
    y0 += h; return s;
  });
  // labels: the big slab prints its name and its value on its front; the narrow ones carry a tag right of their step
  const s0 = slabs[0], it0 = items[0];
  if (it0.label) {
    const nm = String(it0.label).replace(/\s*[\d,.]+$/, ""), vv = String(it0.label).match(/[\d,.]+$/);
    const ln = label(nm, 1.2, { px: 64, color: "#fbf3e8" }); ln.position.set(-s0.w / 2 + 0.75, 0, SD / 2 + 0.005); s0.g.add(ln);
    if (vv) { const lv = label(vv[0], 1.5, { px: 120, font: FONT_NUM, weight: 700, color: "#fbf3e8" }); lv.position.set(-s0.w / 2 + 2.22, 0, SD / 2 + 0.006); s0.g.add(lv); }
  }
  const tags = items.map((it, j) => {
    if (!j || !it.label) return null;
    const s = slabs[j];
    const tg = new THREE.Group(); scene.add(tg);
    const tw = 1.3; const bd = rbox(tw, 0.44, 0.08, 0.03, COL.plaster, 30 + j); tg.add(bd);
    const lb = label(it.label, tw * 0.9, { px: 64 }); lb.position.z = 0.045; tg.add(lb);
    tg.position.set(L + s.w + 0.08 + tw / 2, s.y, SD / 2 - 0.06);
    const ta = animObj(tg, { sy: 0 }); parts.push(ta); return ta;
  });
  const bl = blob(WMAX * 1.2, 1.4, 0.7); bl.position.set(-s0.w / 2 + WMAX / 2, -s0.h / 2 + 0.004, 0); s0.g.add(bl);
  // 1: push the big slab in from the right
  s0.ga.set(0, { x: s0.g.position.x + 1.4, sy: 0 });
  popUp(s0.ga, a - 0.3, { dur: 0.35 });
  const pushX0 = s0.g.position.x + 1.4 + s0.w / 2 + 0.3;
  let t = walkTo(b.e, a - b.e, pushX0, 0.0, { faceEnd: LEFT });
  P.to(t, 0.14, { aLx: 1.45, aRx: 1.45, lean: 0.3 }, "out2");
  const dPush = 0.65 * Math.max(k, 0.8);
  walkTo(t + 0.12, dPush, pushX0 - 1.4, 0.0, { turn: false });
  s0.ga.to(t + 0.14, dPush, { x: s0.g.position.x }, "lin");
  t += 0.12 + dPush;
  P.to(t, 0.2, { lean: 0, aLx: 0, aRx: 0 }, "io2");
  // 2, 3: they drop into place, each one pointed at
  for (let j = 1; j <= 2; j++) {
    const s = slabs[j];
    s.ga.set(0, { y: s.y + 3.0, sy: 0 }); s.ga.set(t + 0.02, { sy: 1 });
    s.ga.to(t + 0.05, 0.3, { y: s.y }, "in2");
    s.ga.to(t + 0.35, 0.08, { sy: 0.84, sx: 1.06 }, "out2"); s.ga.to(t + 0.43, 0.2, { sy: 1, sx: 1 }, "back1");
    if (tags[j]) popUp(tags[j], t + 0.45, { dur: 0.35 });
    P.to(t, 0.18, { aRx: 1.5, aRz: 0.2 - 0.3 * j, turn: 0.2, look: 0.25 * j }, "out2");
    t += 0.42 * Math.max(k, 0.8);
  }
  idleArms(t, 0.18);
  // 4: pick up the last slab, lift it overhead, hop onto the big step and set it on the top
  const s3 = slabs[3];
  const pickX = L + WMAX + 0.05, pickZ = 0.95;
  s3.ga.set(0, { x: pickX, y: 0.4, z: pickZ, sy: 0 }); popUp(s3.ga, a + 0.1, { dur: 0.3 });
  s3.ga.set(a + 0.1, { y: s3.h / 2 });
  t = walkTo(t, 0.35, pickX + 0.02, pickZ - 0.38, { faceEnd: FRONT });
  P.to(t, 0.16, { lean: 0.45, sq: -0.08, aLx: 1.2, aRx: 1.2, look: 0 }, "out2");
  P.to(t + 0.18, 0.24, { lean: 0, sq: 0, aLx: 3.0, aRx: 3.0, aLz: 0.3, aRz: 0.3 }, "out2");
  s3.ga.to(t + 0.18, 0.24, { y: CH + 0.12 + s3.h / 2, x: pickX + 0.02, z: pickZ - 0.38 }, "out2");
  t += 0.48;
  const standX = L + WMAX - 0.38;
  face(t, LEFT, 0.12);
  const tH = t;
  hop(t, 0.42, standX, s0.h, 0.3, 0.0);
  s3.ga.to(tH, 0.42, { x: standX, z: 0.0, y: s0.h + CH + 0.12 + s3.h / 2 }, "io2");
  t = tH + 0.6;
  P.to(t - 0.12, 0.01, { ground: s0.h }, "none");
  // set it on top: a lob from overhead to the top of the stair
  P.to(t, 0.2, { aLx: 2.0, aRx: 2.0, lean: 0.3, sq: -0.08 }, "out2");
  s3.ga.to(t + 0.05, 0.25, { x: (standX + L + s3.w / 2) / 2, y: s3.y + 0.7, z: 0 }, "out2");
  s3.ga.to(t + 0.3, 0.25, { x: L + s3.w / 2, y: s3.y }, "in2");
  s3.ga.to(t + 0.55, 0.07, { sy: 0.8, sx: 1.12 }, "out2"); s3.ga.to(t + 0.62, 0.2, { sy: 1, sx: 1 }, "back1");
  if (tags[3]) popUp(tags[3], t + 0.6, { dur: 0.35 });
  t += 0.6;
  P.to(t, 0.25, { lean: 0, sq: 0, aLx: 0, aRx: 0, aLz: 0.12, aRz: 0.12 }, "io2");
  face(t + 0.05, -0.35, 0.25);
  P.to(t + 0.15, 0.25, { look: 0.45, turn: -0.4 }, "io2");
  return { hero: [L - O, L + WMAX - O], heroY: [0, y0], bb: [L - O - 0.05, 0, -SD / 2, L + WMAX + 0.12 - O, y0 + 0.05, 0.95], parts, end: { x: standX, z: 0.0, y: s0.h } };
};

// 6 · tall stepping stones of true-ratio heights; it hops along in front, each stone's value appears as it lands
ACTS.timeline = (b, O, a, k) => {
  const items = (b.p.items || []).slice(0, 6);
  const vmax = Math.max(...items.map((x) => x.value)) || 1;
  const HM = T(b, "hmax", 2.2 * CH), SW = 0.62, gap = 0.72, n = items.length;
  const x0 = O - (n - 1) * gap / 2 - 0.2;
  const parts = [];
  const stones = items.map((it, j) => {
    const h = Math.max(0.2, HM * it.value / vmax);
    const last = j === n - 1;
    const g = new THREE.Group(); g.position.set(x0 + j * gap, 0, 0); scene.add(g);
    const st = rbox(SW, h, 0.64, 0.08, last ? COL.terra : COL.plaster, 40 + j); st.position.y = h / 2; g.add(st);
    const bl = blob(0.85, 0.85, 0.7); bl.position.set(0, 0.004, 0); g.add(bl);
    const ga = animObj(g, { sy: 0 }); parts.push(ga);
    const fg = last ? "#fbf3e8" : INK;
    const lv = label(String(it.label || it.value), SW * 0.92, { px: 76, font: FONT_NUM, weight: 700, color: fg }); lv.position.set(0, h - 0.2, 0.325); g.add(lv);
    const ly = label(String(it.year || ""), SW * 0.84, { px: 60, color: last ? "#f6e9dc" : "#5b5249", weight: 700 }); ly.position.set(0, h - 0.46, 0.325); g.add(ly);
    const la = animObj(lv, { s: 0, y: h - 0.2, z: 0.325 }); const lya = animObj(ly, { s: 0, y: h - 0.46, z: 0.325 });
    return { g, ga, h, la, lya, x: x0 + j * gap };
  });
  stones.forEach((s, j) => popUp(s.ga, b.e + 0.25 + j * 0.06, { dur: 0.42 }));
  // the hero value: extruded numerals that land on top of the last stone
  const lastS = stones[n - 1];
  const hv = String(T(b, "hero", items[n - 1].label || items[n - 1].value));
  const hsz = T(b, "vsize", 1.25), hn = word3d(hv, hsz, clay(COL.terra), { depth: 0.3 });
  const hcx = lastS.x - 0.35;
  const hp = new THREE.Group(); hp.add(hn); scene.add(hp); hp.position.set(hcx, lastS.h + 0.02, -0.08);
  const ha = animObj(hp, { sy: 0, y: lastS.h + 0.02 }); parts.push(ha);
  // it hops along the front of the stones; landing in front of each one makes its numbers appear
  const fz = 0.62;
  let t = walkTo(b.e, a - b.e, x0 - 0.5, fz, { faceEnd: RIGHT });
  const hd = 0.32 * clamp(k, 0.85, 1.1);
  stones.forEach((s, j) => {
    const tl = hop(t + 0.02, hd, s.x, 0, 0.42, fz);
    const land = t + 0.02 + hd;
    s.ga.to(land, 0.07, { sy: 0.95 }, "out2"); s.ga.to(land + 0.07, 0.18, { sy: 1 }, "back1");
    s.la.to(land, 0.22, { s: 1 }, "back"); s.lya.to(land + 0.05, 0.2, { s: 1 }, "back");
    t = tl;
  });
  popUp(ha, t + 0.05, { dur: 0.45 });
  face(t + 0.05, -0.3, 0.2); t += 0.2;
  P.to(t, 0.3, { aLz: 2.4, aRz: 2.4, look: 0.5, turn: -0.3 }, "back1");
  P.to(t + 0.6, 0.3, { aLz: 0.12, aRz: 0.12 }, "io2");
  const topH = lastS.h + (GLYPHS.__cap || 0.7) * hsz;
  return { hero: [x0 - SW / 2 - O, lastS.x + SW / 2 - O], heroY: [0, lastS.h], bb: [x0 - 0.7 - O, 0, -0.32, Math.max(lastS.x + 0.4, hcx + hn.userData.w / 2) - O, topH + 0.03, 0.5], parts, end: { x: lastS.x, z: fz } };
};

// 7 · it rolls a scroll across a sloped clay lectern, printing the sentence, then sits on the end
ACTS.statement = (b, O, a, k) => {
  const lines = b.p.lines && b.p.lines.length ? b.p.lines : [String(T(b, "text", ""))];
  const LEN = T(b, "len", 3.1), DEP = 1.1, HB = 0.15, HF = 3.0;   // low front, high back: the top faces the camera
  const L = O - LEN / 2 + 0.45;
  const parts = [];
  // lectern as an extruded side profile
  const sh = new THREE.Shape(); sh.moveTo(-DEP / 2, 0); sh.lineTo(DEP / 2, 0); sh.lineTo(DEP / 2, HF); sh.lineTo(-DEP / 2, HB); sh.lineTo(-DEP / 2, 0);
  const lg = lumpy(new THREE.ExtrudeGeometry(sh, { depth: LEN - 0.1, bevelEnabled: true, bevelThickness: 0.05, bevelSize: 0.05, bevelSegments: 4 }), DEP, 0.008, 2.4, 9);
  lg.rotateY(Math.PI / 2);        // profile x -> world -z (so low edge is at the front), extrude along +x
  const lect = new THREE.Mesh(lg, clay(COL.clay)); lect.castShadow = true; lect.receiveShadow = true;
  const gL = new THREE.Group(); gL.add(lect); gL.position.set(L + 0.05, 0, 0); scene.add(gL);
  const la = animObj(gL, { sy: 0 }); parts.push(la);
  popUp(la, a - 0.38, { dur: 0.42 });
  const bl = blob(LEN * 1.15, 1.2, 0.7); bl.position.set(LEN / 2 - 0.05, 0.004, 0); gL.add(bl);
  // the banner on the slope: plaster strip with the sentence printed on it
  const slope = Math.atan2(HF - HB, DEP), sl = Math.hypot(HF - HB, DEP);
  const bw = LEN - 0.12, bh = sl * 0.86, asp = bw / bh;
  const bm = new THREE.MeshStandardMaterial({ roughness: 1, metalness: 0, polygonOffset: true, polygonOffsetFactor: -2 });
  const clip = new THREE.Plane(new THREE.Vector3(-1, 0, 0), L);
  bm.clippingPlanes = [clip]; bm.clipShadows = true;
  const ban = new THREE.Mesh(new THREE.PlaneGeometry(bw, bh), bm); ban.receiveShadow = true;
  const mid = new THREE.Vector3(L + 0.06 + LEN / 2, (HB + HF) / 2 + 0.06 * Math.cos(slope), 0.06 * Math.sin(slope));
  ban.position.copy(mid); ban.rotation.x = -(Math.PI / 2 - slope); scene.add(ban);
  // keep the canvas from stretching: redraw at the banner's aspect
  {
    const cw = 2048, chh = Math.round(cw / asp);
    const cv = document.createElement("canvas"); cv.width = cw; cv.height = chh; const g = cv.getContext("2d");
    g.fillStyle = "#f6f1e7"; g.fillRect(0, 0, cw, chh);
    g.font = `800 100px ${FONT_HEAD}`;
    const wmax = Math.max(...lines.map((l) => g.measureText(l.replace(/\*/g, "")).width), 1);
    const px = Math.min(chh / (lines.length * 1.25) * 0.92, 300, (cw - 150) / wmax * 100);
    g.font = `800 ${px}px ${FONT_HEAD}`; g.textBaseline = "middle";
    lines.forEach((l, i) => { let x = 70; const y = chh / 2 + (i - (lines.length - 1) / 2) * px * 1.25; for (const [t, em] of richRuns(l)) { g.fillStyle = em ? INK_EM : INK; g.fillText(t, x, y); x += g.measureText(t).width; } });
    const t2 = new THREE.CanvasTexture(cv); t2.colorSpace = THREE.SRGBColorSpace; t2.anisotropy = 8; bm.map = t2; bm.needsUpdate = true;
  }
  const ba = A({ x: L });
  // the roll (terracotta) travels along the slope, unrolling the banner behind it
  const roll = new THREE.Mesh(lumpy(new THREE.CylinderGeometry(0.14, 0.14, bh * 1.04, 22), 0.28, 0.012, 3, 5), clay(COL.terra));
  roll.castShadow = true; scene.add(roll);
  const tR = a + 0.35, dR = 1.5 * Math.max(k, 0.8);
  ba.to(tR, dR, { x: L + LEN + 0.02 }, "out3");
  const rollA = A({ s: 0 }); rollA.to(a - 0.1, 0.3, { s: 1 }, "back");
  rollA.to(tR + dR + 0.05, 0.3, { s: 0 }, "in2");
  LIVE.push((t) => {
    const v = ba.v(t); clip.constant = v.x;
    const rs = rollA.v(t).s;
    roll.visible = rs > 0.01; roll.scale.set(rs, rs, rs);
    roll.position.set(v.x + 0.02, mid.y + 0.14 * Math.cos(slope), mid.z + 0.14 * Math.sin(slope));
    roll.rotation.set(-(Math.PI / 2 - slope), 0, 0); roll.rotateY(-v.x * 5);
  });
  parts.push(animObj(ban, { y: mid.y, z: mid.z, rx: -(Math.PI / 2 - slope) }));
  // the figure walks along in front of the lectern pushing the roll
  // the figure stands at the left end, gives the roll one shove; the roll runs out across the slope on its own
  const fz = DEP / 2 + 0.2;
  let t = walkTo(b.e, a - b.e, L - 0.45, fz - 0.05, { faceEnd: RIGHT });
  P.to(tR - 0.3, 0.25, { aLx: 0.9, aRx: 0.9, lean: -0.1, sq: -0.06 }, "in2");            // wind up
  P.to(tR - 0.05, 0.14, { aLx: 1.5, aRx: 1.5, lean: 0.35, sq: 0.06 }, "out2");          // shove
  P.to(tR + 0.1, 0.12, { x: L - 0.3 }, "out2");
  P.to(tR + 0.25, 0.3, { lean: 0, sq: 0, aLx: 0, aRx: 0 }, "io2");
  P.to(tR + 0.3, dR * 0.7, { turn: -0.9, look: 0.08 }, "io2");                          // watches it go
  t = tR + dR * 0.75;
  // the end block on the left: it sits down on it
  const ebx = L - 0.75, ebz = -0.05;
  const eb = rbox(0.5, 0.56, 0.5, 0.08, COL.plaster, 50); eb.position.set(ebx, 0.28, ebz); scene.add(eb);
  const ea = animObj(eb, { sy: 0 }); parts.push(ea); popUp(ea, a - 0.3, { dur: 0.35 });
  const eblob = blob(0.8, 0.7, 0.6); eblob.position.set(0, -0.276, 0); eb.add(eblob);
  P.to(t, 0.2, { turn: 0 }, "io2");
  face(t, LEFT + 0.6, 0.15);
  t = hop(t + 0.15, 0.4, ebx, 0.36, 0.3, ebz + 0.12);
  face(t - 0.3, FRONT + 0.25, 0.25);
  P.to(t - 0.25, 0.3, { sit: 1, lean: -0.08 }, "out2");
  P.to(t - 0.2, 0.01, { ground: 0.56 }, "none");
  P.to(t + 0.2, 0.3, { aLx: 0.6, aRx: 0.6, turn: 0.45, look: 0.05 }, "io2");
  return { hero: [L - O, L + LEN - O], bb: [ebx - 0.32 - O, 0, -DEP / 2, L + LEN - O, Math.max(HF + 0.1, 0.36 + CH * 0.85), fz], parts, end: { x: ebx, z: ebz + 0.12, y: 0.36, sit: true } };
};

// 8 · the recap on a clay display shelf, one figure per shelf; it walks up, pats the bottom one, turns and waves once;
//     the light drops to a warm dusk
ACTS.outro = (b, O, a, k, first, D) => {
  const items = (b.p.items || []).slice(0, 3);
  const n = items.length, parts = [];
  LIGHT.to(a + 0.4, Math.max(1.5, D - 0.8), { kr: 1.0, kg: 0.72, kb: 0.5, ki: 1.6, hi: 1.05 }, "sine");
  if (!n) {
    let t0 = walkTo(b.e, a - b.e + 0.3, O, 0.3, { faceEnd: FRONT });
    P.to(t0 + 0.2, 0.2, { aRz: 2.5 }, "out2"); P.to(t0 + 0.4, 0.18, { aRz: 2.0 }, "io2"); P.to(t0 + 0.58, 0.18, { aRz: 2.6 }, "io2"); P.to(t0 + 0.8, 0.3, { aRz: 0.12 }, "io2");
    return { bb: [-1.6, 0, -0.3, 1.6, CH + 0.1, 0.8], parts, end: { x: O, z: 0.3 } };
  }
  const sz = T(b, "vsize", 1.13);
  const widths = items.map((it) => [...String(it.v)].reduce((s, ch) => s + (GLYPHS[ch] ? GLYPHS[ch].a : 0.6) * sz, 0));
  const SWD = Math.max(...widths) + 0.36, SDP = 0.62, BASE = 0.34, LIP = 0.27, ROW = (GLYPHS.__cap || 0.7) * sz + LIP + 0.16;
  const sx = O;
  const shelf = new THREE.Group(); shelf.position.set(sx, 0, 0); scene.add(shelf);
  const hTot = BASE + n * ROW + 0.12;
  const back = rbox(SWD, hTot, 0.1, 0.04, COL.plaster, 90); back.position.set(0, hTot / 2, -SDP / 2 + 0.05); shelf.add(back);
  [-1, 1].forEach((s) => { const post = rbox(0.12, hTot, SDP, 0.04, COL.clay, 91 + s); post.position.set(s * (SWD / 2 - 0.06), hTot / 2, 0); shelf.add(post); });
  const sb = blob(SWD * 1.2, 1.1, 0.7); shelf.add(sb);
  const sa = animObj(shelf, { sy: 0 }); parts.push(sa); popUp(sa, b.e + 0.2, { dur: 0.45 });
  // rows from the bottom: the last item on the bottom shelf, the first on top
  const rows = items.map((it, j) => {
    const r = n - 1 - j;                     // item j sits on row r (0 = bottom)
    const yTop = r === 0 ? BASE : BASE + r * ROW;
    const g = new THREE.Group(); g.position.set(sx, 0, 0); scene.add(g);
    const brd = rbox(SWD - 0.2, r === 0 ? BASE : LIP, SDP, 0.05, COL.plaster, 95 + j); brd.position.set(0, r === 0 ? BASE / 2 : yTop - LIP / 2, 0.02); g.add(brd);
    if (it.label) { const lb = label(it.label, 0.92, { px: 64, padY: 0 }); lb.position.set(-SWD / 2 + 0.12 + 0.46, r === 0 ? BASE / 2 : yTop - LIP / 2, SDP / 2 + 0.03); g.add(lb); }
    const hero = j === 0;
    const nv = word3d(String(it.v), sz, clay(hero ? COL.terra : COL.dark, hero ? 0.01 : 0.006), { depth: 0.24 });
    const np = new THREE.Group(); np.add(nv); np.position.set(sx - SWD / 2 + 0.16 + nv.userData.w / 2, yTop + 0.01, 0.04); scene.add(np);   // left-aligned: the figure stands in the free space on the right
    const ga = animObj(g, { sy: 0 }); parts.push(ga);
    const na = animObj(np, { sy: 0, y: yTop + 0.01 }); parts.push(na);
    return { ga, na, yTop };
  });
  // the figure walks in along the front (the shelf is still empty), the figures pop onto their shelves behind it
  const ex = sx + SWD / 2 - 0.42, ez = 0.62;
  let t = walkTo(b.e, a - b.e + 0.5, ex, ez, { faceEnd: LEFT });
  rows.forEach((rw, j) => { popUp(rw.ga, b.e + 0.3 + 0.08 * j, { dur: 0.4 }); popUp(rw.na, t - 0.1 + 0.18 * (n - 1 - j), { dur: 0.42 }); });
  t += 0.18 * n + 0.1;
  // pat the bottom one
  const bot = rows[n - 1];
  P.to(t, 0.16, { aLx: 1.5, aLz: 0.2, lean: 0.2 }, "out2");
  for (let q = 0; q < 2; q++) {
    P.to(t + 0.16 + q * 0.22, 0.1, { aLx: 1.15 }, "in2"); P.to(t + 0.26 + q * 0.22, 0.12, { aLx: 1.5 }, "out2");
    bot.na.to(t + 0.25 + q * 0.22, 0.06, { sy: 0.9, sx: 1.04, sz: 1.04 }, "out2"); bot.na.to(t + 0.31 + q * 0.22, 0.14, { sy: 1, sx: 1, sz: 1 }, "back1");
  }
  t += 0.7;
  P.to(t, 0.2, { aLx: 0, aLz: 0.12, lean: 0 }, "io2");
  face(t + 0.05, FRONT, 0.3);
  t += 0.4;
  P.to(t, 0.2, { aRz: 2.5, aRx: 0.2 }, "out2");
  P.to(t + 0.2, 0.18, { aRz: 2.0 }, "io2"); P.to(t + 0.38, 0.18, { aRz: 2.6 }, "io2");
  P.to(t + 0.56, 0.18, { aRz: 2.05 }, "io2"); P.to(t + 0.74, 0.3, { aRz: 0.12, aRx: 0 }, "io2");
  P.to(t, 0.25, { tilt: -0.08 }, "io2"); P.to(t + 0.8, 0.3, { tilt: 0 }, "io2");
  return { hero: [sx - SWD / 2 - O, sx + SWD / 2 - O], heroY: [0, hTot], bb: [sx - SWD / 2 - 0.05 - O, 0, -0.35, sx + SWD / 2 + 0.05 - O, hTot + 0.05, 0.5], parts, end: { x: ex, z: ez } };
};

ACTS.fx = (b, O, a) => {     // an effect page covers the frame; the figure waits on an empty stretch of sweep
  walkTo(b.e, a - b.e, O, 0.2, { faceEnd: FRONT });
  return { bb: [-1.5, 0, -0.3, 1.5, CH, 0.5], parts: [], end: { x: O, z: 0.2 } };
};

// ---------------------------------------------------------------- build the film
{   // the printed type uses the film's own faces: wait until they are loaded
  const sample = CFG.beats.map((b) => [b.head, b.sub, ...(b.p.lines || []), ...((b.p.items || []).map((x) => [x.label, x.year, x.v].join("")))].join("")).join("") + "0123456789";
  try { await Promise.all([document.fonts.load(`800 100px 'h9-noto-serif-sc'`, sample), document.fonts.load(`700 100px 'h9-noto-sans-sc'`, sample),
    document.fonts.load(`700 100px 'h9-fraunces'`, "0123456789%")]); } catch (e) { /* fall back to the stack */ }
}
const LIGHT = A({ kr: 1.0, kg: 0.97, kb: 0.93, ki: 2.2, hi: 1.5 });
const STATIONS = [], HEROES = [], HEROY = [];
const camA = A({ px: 0, py: 0, pz: 0, lx: 0, ly: 0, lz: 0 });
let prevEnd = null;
CFG.beats.forEach((b, i) => {
  const O = i * SP;
  const first = i === 0;
  const a = first ? b.t + 0.05 : b.t + 0.45;           // the act starts when the camera has arrived
  const avail = b.d - (a - b.t) - 0.75;
  const k = clamp(avail / (b.nominal || 3.2), 0.65, 1.25);
  // carry the figure out of a sitting pose (or down from a step) before it walks on
  // (the previous beat holds its finished picture until 0.3 s before the cut)
  b.e = b.t - 0.3;
  if (!first) { P.to(b.t - 0.32, 0.16, { look: 0, turn: 0, tilt: 0, lean: 0 }, "io2"); idleArms(b.t - 0.32, 0.16); }
  if (prevEnd && prevEnd.sit) P.to(b.t - 0.3, 0.16, { sit: 0 }, "io2");
  if (prevEnd && prevEnd.y) {     // standing on something: hop down first
    face(b.t - 0.3, 0.6, 0.08);
    hop(b.t - 0.22, 0.3, P.cur("x") + 0.3, 0, 0.2, P.cur("z") + 0.55);
    P.to(b.t - 0.05, 0.01, { ground: 0 }, "none");
    b.e = b.t + 0.12;
  }
  const fn = ACTS[b.kind] || ACTS.statement;
  const r = fn(b, O, a, k, first, b.d);
  SETS[i] = r.parts; prevEnd = r.end || null; HEROES[i] = r.hero ? [r.hero[0], r.hero[1], r.hz || 0] : null; HEROY[i] = r.heroY || null;
  const bb = [O + r.bb[0], r.bb[1], r.bb[2], O + r.bb[3], r.bb[4], r.bb[5]];
  const st = fitStation(bb, O); STATIONS.push(st);
  props(st, i);
  const last = i === CFG.beats.length - 1;
  wallHead(st, b.head, b.sub, b.t, last ? null : CFG.beats[i + 1].t - 0.27);
  if (!last) sinkSet(i, CFG.beats[i + 1].t - 0.28);
});
// camera: hold each station with a slow push, truck to the next in 24 frames (0.8 s), centred on the cut
STATIONS.forEach((st, i) => {
  const b = CFG.beats[i];
  const v = { px: st.pos.x, py: st.pos.y, pz: st.pos.z, lx: st.look.x, ly: st.look.y, lz: st.look.z };
  if (i === 0) camA.set(0, v);
  else camA.to(b.t - 0.3, 0.8, v, "io2");
  const end = i + 1 < STATIONS.length ? CFG.beats[i + 1].t - 0.3 : CFG.duration;
  const hold = end - (b.t + 0.5);
  if (hold > 0.4) camA.to(b.t + 0.5, hold, { pz: st.pos.z - 0.12, lz: st.look.z - 0.12, px: st.pos.x + 0.04, lx: st.look.x + 0.04 }, "lin");
});

const look = new THREE.Vector3();
function renderAt(t) {
  const tq = Math.floor(t * 15 + 1e-4) / 15;           // character and objects: a new pose every 2 frames ("on twos")
  poseAt(tq);
  for (const f of LIVE) f(tq);
  const c = camA.v(t);                                  // the camera stays smooth
  camera.position.set(c.px, c.py, c.pz); look.set(c.lx, c.ly, c.lz); camera.lookAt(look);
  const L = LIGHT.v(t);
  key.color.setRGB(L.kr, L.kg, L.kb); key.intensity = L.ki; hemi.intensity = L.hi;
  key.position.set(c.px - 2.4, 4.4, 4.4); key.target.position.set(c.px, 0.3, -0.6); key.target.updateMatrixWorld();
  renderer.render(scene, camera);
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
renderAt(0);
window.addEventListener("hf-seek", (e) => { renderAt(e.detail.time); renderer.getContext().finish(); });
window.__clayRender = renderAt;
window.__clayFit = STATIONS.map((st, i) => { const O = i * SP; const a = project(st, new THREE.Vector3(O, 0, 0.2)), b = project(st, new THREE.Vector3(O, CH, 0.2));
  const h = HEROES[i] || [0, 0, 0]; const l = project(st, new THREE.Vector3(O + h[0], 0.3, h[2])), r = project(st, new THREE.Vector3(O + h[1], 0.3, h[2]));
  const hy = HEROY[i] || [0, 0]; const y0 = project(st, new THREE.Vector3(O, hy[0], 0)), y1 = project(st, new THREE.Vector3(O, hy[1], 0));
  return { figure: Math.round(a[1] - b[1]), hero: Math.round(r[0] - l[0]), chartY: [Math.round(y1[1]), Math.round(y0[1])] }; });
window.__h9WorldReady && window.__h9WorldReady();
