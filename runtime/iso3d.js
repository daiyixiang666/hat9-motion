// 九帽动效 · iso3d — one continuous isometric miniature world seen through an orthographic camera.
// Floating toy islands (one per beat) on a pastel void, joined by a road; soft long shadows from a low sun, a coloured
// hemisphere fill, contact blobs under everything (the ambient-occlusion feel), gentle bloom.
// Deterministic: a frame is drawn from the seek time alone (hf-seek). Tweens live on one paused GSAP timeline;
// streams (belts, trucks, the parcel pile) are pure functions of t.
// CFG and GLYPHS are injected by styles/iso3d.py.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const CFG = window.__H9_ISO;
const GLYPHS = window.__H9_GLYPHS || {};
const W = CFG.w, H = CFG.h, PORTRAIT = H > W;
const gsap = window.gsap;
const PAL = CFG.pal;
const SPACING = 40;                       // island slots along +x
const Q = Math.PI / 4;

// ---------- seeded random (mulberry32)
let _s = CFG.seed || 11;
const rnd = () => { _s |= 0; _s = (_s + 0x6d2b79f5) | 0; let t = Math.imul(_s ^ (_s >>> 15), 1 | _s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => a + (b - a) * rnd();
const pick = (a) => a[Math.floor(rnd() * a.length)];
const clamp01 = (v) => Math.max(0, Math.min(1, v));
const easeOut = (v) => 1 - Math.pow(1 - clamp01(v), 3);
const easeIO = (v) => { v = clamp01(v); return v < 0.5 ? 4 * v * v * v : 1 - Math.pow(-2 * v + 2, 3) / 2; };
const backOut = (v) => { v = clamp01(v); const c = 1.7; return 1 + (c + 1) * Math.pow(v - 1, 3) + c * Math.pow(v - 1, 2); };

// ---------- renderer / scene
const canvas = document.getElementById("iso3d");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.NoToneMapping;          // pastel colours stay as authored; lights are balanced so tops never clip
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = (() => {             // the pastel void: a vertical gradient in screen space
  const c = document.createElement("canvas"); c.width = 4; c.height = 512; const g = c.getContext("2d");
  const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, PAL.sky0); gr.addColorStop(0.55, PAL.sky1); gr.addColorStop(1, PAL.sky2);
  g.fillStyle = gr; g.fillRect(0, 0, 4, 512); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();

const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -600, 900);
const cam = { tx: 0, ty: 0, tz: 0, view: 30, az: 45, el: 33, fx: 0.5, fy: 0.5, fw: 0 };   // fx/fy: where the target sits on screen

const hemi = new THREE.HemisphereLight(PAL.hemiSky, PAL.hemiGround, 1.5 * (CFG.exposure || 1)); scene.add(hemi);
const sun = new THREE.DirectionalLight(PAL.sun, 2.0 * (CFG.exposure || 1));
const SUN = new THREE.Vector3(-40, 33, 25).normalize();       // low and from the left: long shadows falling right
sun.castShadow = true; sun.shadow.mapSize.set(2048, 2048); sun.shadow.bias = -0.0005; sun.shadow.normalBias = 0.03;
const sc = sun.shadow.camera;
scene.add(sun); scene.add(sun.target);

// the islands float: an invisible floor far below only catches their soft shadows
const catcher = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.ShadowMaterial({ color: PAL.shadow, opacity: 0.2 }));
catcher.rotation.x = -Math.PI / 2; catcher.position.y = -5.5; catcher.receiveShadow = true; scene.add(catcher);

// contact shadow blob (fake ambient occlusion under every object)
const blobTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d");
  const gr = g.createRadialGradient(64, 64, 4, 64, 64, 62); gr.addColorStop(0, "rgba(70,50,110,.6)"); gr.addColorStop(0.55, "rgba(70,50,110,.25)"); gr.addColorStop(1, "rgba(70,50,110,0)");
  g.fillStyle = gr; g.fillRect(0, 0, 128, 128); return new THREE.CanvasTexture(c); })();
const blobMat = new THREE.MeshBasicMaterial({ map: blobTex, transparent: true, depthWrite: false, opacity: 0.5 });
const blobGeo = new THREE.PlaneGeometry(1, 1);
function blob(parent, w, d, x = 0, z = 0, y = 0.02) { const m = new THREE.Mesh(blobGeo, blobMat); m.rotation.x = -Math.PI / 2; m.scale.set(w, d, 1); m.position.set(x, y, z); m.renderOrder = 1; parent.add(m); return m; }

// ---------- materials + primitives
const matCache = {};
const mat = (c, r = 0.85) => matCache[c + "|" + r] || (matCache[c + "|" + r] = new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0 }));
const geoCache = {};
function rbox(w, h, d, r) { const k = [w, h, d, r].map((v) => v.toFixed(3)).join("|"); return geoCache[k] || (geoCache[k] = new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2.05, h / 2.05, d / 2.05))); }
function box(parent, w, h, d, color, x = 0, y = 0, z = 0, r = 0.12, m) {
  const mesh = new THREE.Mesh(rbox(w, h, d, r), m || mat(color)); mesh.position.set(x, y + h / 2, z);
  mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function cyl(parent, r, h, color, x = 0, y = 0, z = 0, seg = 28, m) {
  const k = "c" + r + "|" + h + "|" + seg; const g = geoCache[k] || (geoCache[k] = new THREE.CylinderGeometry(r, r, h, seg));
  const mesh = new THREE.Mesh(g, m || mat(color)); mesh.position.set(x, y + h / 2, z); mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh); return mesh;
}
function slab(parent, w, d, color, x = 0, z = 0) {           // an island: a thick rounded base with a coloured top
  const g = new THREE.Group(); g.position.set(x, 0, z); parent.add(g);
  box(g, w, 1.5, d, PAL.slabSide, 0, -1.62, 0, 0.5);
  box(g, w - 0.36, 0.16, d - 0.36, color, 0, -0.16, 0, 0.3);
  return g;
}
function tree(parent, x, z, s = 1) {
  const g = new THREE.Group(); g.position.set(x, 0, z); parent.add(g);
  cyl(g, 0.13 * s, 0.6 * s, PAL.trunk, 0, 0, 0, 10);
  const geo = geoCache.ico || (geoCache.ico = new THREE.IcosahedronGeometry(0.62, 1));
  const c = new THREE.Mesh(geo, mat(rnd() < 0.5 ? PAL.leaf0 : PAL.leaf1, 0.9)); c.position.y = 1.08 * s; c.scale.set(s, s * 1.12, s); c.castShadow = true; c.receiveShadow = true; g.add(c);
  blob(g, 1.8 * s, 1.8 * s);
  return g;
}
function building(parent, x, z, w, d, h, color, roof) {
  const g = new THREE.Group(); g.position.set(x, 0, z); parent.add(g);
  box(g, w, h, d, color, 0, 0, 0, 0.16);
  box(g, w + 0.16, 0.2, d + 0.16, roof || PAL.roof, 0, h, 0, 0.09);
  const rows = Math.floor((h - 0.3) / 0.9), cw = Math.max(1, Math.floor(w / 0.8)), cd = Math.max(1, Math.floor(d / 0.8));
  for (let r = 0; r < rows; r++) {                                   // windows on the two faces the camera sees
    const wy = 0.38 + r * 0.9;
    for (let c = 0; c < cw; c++) box(g, 0.32, 0.42, 0.06, PAL.window, -w / 2 + (c + 0.5) * (w / cw), wy, d / 2 + 0.01, 0.05);
    for (let c = 0; c < cd; c++) box(g, 0.06, 0.42, 0.32, PAL.window, w / 2 + 0.01, wy, -d / 2 + (c + 0.5) * (d / cd), 0.05);
  }
  blob(g, w * 1.6, d * 1.6);
  return g;
}
function truck(parent, color, cargo) {
  const g = new THREE.Group(); parent.add(g);
  box(g, 2.6, 1.3, 1.25, cargo || PAL.cargo, -0.35, 0.28, 0, 0.14);
  box(g, 0.95, 1.0, 1.2, color, 1.35, 0.28, 0, 0.18);
  box(g, 0.08, 0.4, 0.96, PAL.glass, 1.83, 0.76, 0, 0.04);
  for (const [wx, wz] of [[-1.15, 0.6], [-1.15, -0.6], [1.3, 0.6], [1.3, -0.6]]) {
    const wh = cyl(g, 0.3, 0.2, PAL.tyre, 0, 0, 0, 16); wh.rotation.x = Math.PI / 2; wh.position.set(wx, 0.3, wz);
  }
  blob(g, 4.4, 2.2, 0, 0, 0.03);
  return g;
}
function person(parent, color, x, z, s = 1) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s); parent.add(g);
  const geo = geoCache.cap || (geoCache.cap = new THREE.CapsuleGeometry(0.28, 0.5, 6, 14));
  const b = new THREE.Mesh(geo, mat(color)); b.position.y = 0.55; b.castShadow = true; g.add(b);
  const hgeo = geoCache.head || (geoCache.head = new THREE.SphereGeometry(0.25, 20, 14));
  const hd = new THREE.Mesh(hgeo, mat(PAL.skin)); hd.position.y = 1.3; hd.castShadow = true; g.add(hd);
  blob(g, 1.1, 1.1);
  return g;
}
function scooter(parent, color) {
  const g = new THREE.Group(); parent.add(g);
  box(g, 1.3, 0.22, 0.4, color, 0, 0.22, 0, 0.1); box(g, 0.16, 0.9, 0.16, PAL.ink, 0.55, 0.3, 0, 0.06);
  box(g, 0.66, 0.5, 0.66, PAL.kraft[0], -0.4, 0.44, 0, 0.08);
  for (const wx of [-0.5, 0.55]) { const wh = cyl(g, 0.2, 0.14, PAL.tyre, 0, 0, 0, 14); wh.rotation.x = Math.PI / 2; wh.position.set(wx, 0.2, 0); }
  const p = person(g, PAL.mint, 0.05, 0, 0.8); p.position.y = 0.32;
  blob(g, 1.8, 1, 0, 0, 0.03);
  return g;
}
function cloud(parent, x, y, z, s) {
  const g = new THREE.Group(); g.position.set(x, y, z); g.scale.setScalar(s); parent.add(g);
  const geo = geoCache.cl || (geoCache.cl = new THREE.SphereGeometry(1, 18, 12));
  for (const [cx, cy, cr] of [[0, 0, 1.2], [1.3, -0.2, 0.9], [-1.25, -0.25, 0.85], [0.5, 0.55, 0.8]]) {
    const m = new THREE.Mesh(geo, mat(PAL.cloud, 1)); m.position.set(cx, cy, 0); m.scale.set(cr, cr * 0.8, cr); g.add(m);
  }
  return g;
}

// ---------- real 3D type (outlines from the build)
const tGeo = {};
function glyphGeo(ch, depth) {
  const k = ch + depth; if (tGeo[k]) return tGeo[k];
  const gl = GLYPHS[ch]; if (!gl) return null;
  const sp = new THREE.ShapePath();
  for (const c of gl.p) {
    if (c[0] === "M") sp.moveTo(c[1], c[2]); else if (c[0] === "L") sp.lineTo(c[1], c[2]);
    else if (c[0] === "Q") sp.quadraticCurveTo(c[1], c[2], c[3], c[4]); else if (c[0] === "C") sp.bezierCurveTo(c[1], c[2], c[3], c[4], c[5], c[6]);
  }
  const geo = new THREE.ExtrudeGeometry(sp.toShapes(false), { depth, bevelEnabled: true, bevelThickness: 0.025, bevelSize: 0.016, bevelSegments: 2, curveSegments: 5 });
  geo.computeVertexNormals(); return (tGeo[k] = geo);
}
function textWidth(str, track = 0.04) { let x = 0; for (const ch of String(str)) x += ch === " " ? 0.3 : (GLYPHS[ch] ? GLYPHS[ch].a + track : 0); return x; }
function text3(parent, str, { size = 1, depth = 0.22, color = PAL.ink, colors, track = 0.04, flat = false, face = true, m } = {}) {
  const g = new THREE.Group(); parent.add(g); const inner = new THREE.Group(); g.add(inner); let x = 0; const glyphs = [];
  for (const ch of String(str)) {
    if (ch === " ") { x += 0.3; continue; }
    const gl = GLYPHS[ch]; if (!gl) continue;
    const piv = new THREE.Group(); const mesh = new THREE.Mesh(glyphGeo(ch, depth), m || mat(colors ? colors[glyphs.length % colors.length] : color, 0.55));
    mesh.position.set(-gl.a / 2, -0.38, -depth / 2); mesh.castShadow = true; mesh.receiveShadow = true;
    piv.add(mesh); piv.position.x = x + gl.a / 2; inner.add(piv); glyphs.push(piv); x += gl.a + track;
  }
  glyphs.forEach((p) => (p.position.x -= (x - track) / 2));
  inner.scale.setScalar(size);
  g.rotation.order = "YXZ";
  if (flat) g.rotation.set(-Math.PI / 2, Q, 0);   // lying on the island, baseline level on screen
  else if (face) g.rotation.set(0, Q, 0);         // standing, facing the camera
  g.userData = { glyphs, width: (x - track) * size };
  return g;
}

// ---------- the timeline + streams
const tl = gsap["timeline"]({ paused: true });   // seeked by hf-seek below
const streams = [];                                // f(t), every frame
const pins = [];                                   // DOM labels that follow 3D points
const at = (v) => Math.max(0, v);

// one instanced mesh per heap of cardboard boxes; a taped-box texture tinted per instance
const tapeTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 64; const g = c.getContext("2d");
  g.fillStyle = "#ffffff"; g.fillRect(0, 0, 64, 64); g.fillStyle = "#d9ccb6"; g.fillRect(27, 0, 10, 64);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
const parcelGeo = new RoundedBoxGeometry(0.62, 0.46, 0.62, 2, 0.07);
const parcelMat = new THREE.MeshStandardMaterial({ roughness: 0.88, map: tapeTex });
function parcels(parent, n) {
  const im = new THREE.InstancedMesh(parcelGeo, parcelMat, n); im.castShadow = true; im.receiveShadow = true;
  const col = new THREE.Color();
  for (let i = 0; i < n; i++) { col.set(PAL.kraft[i % PAL.kraft.length]); col.offsetHSL(0, 0, R(-0.035, 0.035)); im.setColorAt(i, col); }
  im.instanceMatrix.setUsage(THREE.DynamicDrawUsage); parent.add(im); return im;
}
const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _p = new THREE.Vector3(), _sv = new THREE.Vector3();
function setInst(im, i, x, y, z, ry = 0, s = 1) { _e.set(0, ry, 0); _q.setFromEuler(_e); _p.set(x, y, z); s = Math.max(s, 0.0001); _sv.set(s, s, s); _m.compose(_p, _q, _sv); im.setMatrixAt(i, _m); }
const heroMat = new THREE.MeshStandardMaterial({ color: PAL.coral, roughness: 0.7, map: tapeTex, emissive: new THREE.Color(PAL.coral), emissiveIntensity: 0.18 });

// island entrance: the slab rises out of the void and its contents pop in, staggered
function arrive(group, t, kids, first) {
  if (!first) tl.from(group.position, { y: -9, duration: 0.95, ease: "back.out(1.2)" }, at(t - 1.0));
  (kids || []).forEach((k, i) => { tl.from(k.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(2.2)" }, at(t - 0.55 + i * 0.045)); });
}
const bounce = (obj, t, amt = 0.16) => tl.fromTo(obj.scale, { y: 1 - amt, x: 1 + amt * 0.5, z: 1 + amt * 0.5 }, { y: 1, x: 1, z: 1, duration: 0.6, ease: "elastic.out(1.1,0.45)", immediateRender: false }, at(t));

const MODS = CFG.mods;
const world = new THREE.Group(); scene.add(world);

// ---------------------------------------------------------------- modules
// framing: each island is fitted into the screen region the overlay cards leave free; the target sits at its centre
// each island is framed into the screen region the overlay cards leave free; the target sits at that region's centre
const REG = PORTRAIT ? { cw: 0.94, ch: 0.42, fx: 0.5, fy: 0.6 } : { cw: 0.6, ch: 0.76, fx: 0.665, fy: 0.5 };
const REG0 = PORTRAIT ? { cw: 0.92, ch: 0.5, fx: 0.5, fy: 0.5 } : { cw: 0.86, ch: 0.74, fx: 0.5, fy: 0.47 };
const AZ0 = 45, EL0 = PORTRAIT ? 35 : 32;
function viewFor(size, reg, azDeg) {
  const [dx, dy, dz] = size; const a = (azDeg * Math.PI) / 180, e = (EL0 * Math.PI) / 180;
  const sw = Math.abs(dx * Math.cos(a)) + Math.abs(dz * Math.sin(a));
  const sh = (Math.abs(dx * Math.sin(a)) + Math.abs(dz * Math.cos(a))) * Math.sin(e) + dy * Math.cos(e);
  return Math.max(sh / reg.ch, ((sw / reg.cw) * H) / W);
}
const ZOOM = CFG.zoom || 0.88;

const BUILD = {};

// the parcel mountain, a price tag swinging from a crane
BUILD.pile = (m, cx, first) => {
  const g = slab(world, 26, 24, PAL.slab, cx, 0);
  const base = m.base || 16; const spots = [];
  for (let L = 0; base - L * 2 > 0; L++) { const side = base - L * 2; for (let i = 0; i < side; i++) for (let j = 0; j < side; j++) spots.push([(i - side / 2 + 0.5) * 0.66 - 1.5, L * 0.48, (j - side / 2 + 0.5) * 0.66 + 0.5, L]); }
  const n = spots.length; const im = parcels(g, n + 1);
  im.setColorAt(n, new THREE.Color(PAL.coral)); im.instanceColor.needsUpdate = true;
  const t0 = m.t - 0.15, t1 = Math.max(m.t + 1.2, (m.at_num || m.t + 1.2) + 0.7);
  const delay = spots.map(([, , , L]) => (L / (base / 2)) * 0.75 + rnd() * 0.25);
  const top = spots[n - 1];
  streams.push((t) => {
    for (let i = 0; i < n; i++) {
      const [x, y, z] = spots[i]; const p = clamp01((t - t0 - delay[i] * (t1 - t0 - 0.45)) / 0.45);
      setInst(im, i, x, y + 0.23 + (1 - easeOut(p)) * 7, z, 0, p <= 0 ? 0 : 0.6 + 0.4 * backOut(p));
    }
    const pt = clamp01((t - t1) / 0.55);
    setInst(im, n, top[0], top[1] + 0.75 + (1 - backOut(pt)) * 6, top[2], 0.35, pt <= 0 ? 0 : 1.2);
    im.instanceMatrix.needsUpdate = true;
  });
  blob(g, 14, 14, -1.5, 0.5);
  const crane = new THREE.Group(); crane.position.set(8.2, 0, -5.5); g.add(crane);
  box(crane, 0.5, 10.4, 0.5, PAL.lilac, 0, 0, 0, 0.14); box(crane, 7.2, 0.44, 0.44, PAL.lilac, -3.2, 10.2, 0, 0.14);
  box(crane, 1.4, 0.9, 1.4, PAL.ink, 0, 0, 0, 0.2);
  const tag = new THREE.Group(); tag.position.set(-6.4, 10.2, 0); tag.scale.setScalar(1.35); crane.add(tag);
  cyl(tag, 0.045, 1.6, PAL.ink, 0, -1.6, 0, 6);
  const tw = Math.max(3.2, textWidth(m.tag || "¥8") * 1.5 + 1.2);
  box(tag, tw, 2.1, 0.28, PAL.card, 0, -3.7, 0, 0.32);
  const yen = text3(tag, m.tag || "¥8", { size: 1.5, depth: 0.18, color: PAL.coral, face: false }); yen.position.set(0, -2.62, 0.2);
  const tagT = m.at_tag || m.t + 1.8;
  tl.from(tag.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.55, ease: "back.out(2.2)" }, at(tagT - 0.3));
  streams.push((t) => { const k = Math.max(0, t - tagT); tag.rotation.z = Math.sin(k * 3.2) * 0.22 * Math.exp(-k * 1.2) + Math.sin(t * 1.1) * 0.02; tag.rotation.y = 0.75 + Math.sin(t * 0.7) * 0.05; });
  const kids = [crane];
  [[-10.5, -9.5], [-11, 8.5], [10.5, 9.5], [-6, 10.5], [4, -10]].forEach(([x, z]) => kids.push(tree(g, x, z, R(0.9, 1.3))));
  const tk = truck(g, PAL.coral); tk.position.set(6.5, 0, 7.2); tk.rotation.y = -0.35; kids.push(tk);
  kids.push(person(g, PAL.sky, 4.2, 4.6, 1.3), person(g, PAL.mint, -8, 4, 1.3));
  arrive(g, m.t, kids, first);
  return { g, focus: [cx, 3.6, -0.5], size: [22, 10, 18], card: true };
};

// a city block: houses, a looping conveyor, one person and their year of parcels
function loopPath(Lx, Lz) {
  const per = 2 * (2 * Lx + 2 * Lz);
  return (u) => { let s = (((u % 1) + 1) % 1) * per;
    if (s < 2 * Lx) return [-Lx + s, Lz]; s -= 2 * Lx; if (s < 2 * Lz) return [Lx, Lz - s]; s -= 2 * Lz;
    if (s < 2 * Lx) return [Lx - s, -Lz]; s -= 2 * Lx; return [-Lx, -Lz + s]; };
}
function heading(f, u) { const a = f(u), b = f(u + 0.002); return Math.atan2(-(b[1] - a[1]), b[0] - a[0]); }
BUILD.city = (m, cx, first) => {
  const g = slab(world, 26, 24, PAL.slab2, cx, 0);
  const cols = [PAL.b0, PAL.b1, PAL.b2, PAL.b3, PAL.b4, PAL.b5];
  const kids = [];
  for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++) {
    if (i === 2 && j === 2) continue;
    kids.push(building(g, -7 + i * 5.2, -7 + j * 5.2, R(2.8, 3.6), R(2.8, 3.6), R(1.9, 6.2), cols[(i * 3 + j) % cols.length]));
  }
  const Lx = 11.3, Lz = 10.1, N = 54; const im = parcels(g, N);
  const along = loopPath(Lx, Lz);
  box(g, 2 * Lx + 1.1, 0.24, 1.0, PAL.belt, 0, 0, Lz, 0.08); box(g, 2 * Lx + 1.1, 0.24, 1.0, PAL.belt, 0, 0, -Lz, 0.08);
  box(g, 1.0, 0.24, 2 * Lz - 1.0, PAL.belt, Lx, 0, 0, 0.08); box(g, 1.0, 0.24, 2 * Lz - 1.0, PAL.belt, -Lx, 0, 0, 0.08);
  streams.push((t) => { const on = clamp01((t - (m.t - 0.5)) / 0.6);
    for (let i = 0; i < N; i++) { const [x, z] = along(i / N + t * 0.05); setInst(im, i, x, 0.47, z, 0, on); }
    im.instanceMatrix.needsUpdate = true; });
  const who = person(g, PAL.coral, 4.0, 6.0, 1.7); kids.push(who);
  const cnt = Math.max(1, Math.min(400, Math.round(m.count || 124))); const stack = parcels(g, cnt);
  const sx = 5.6, sz = 4.9, t0 = m.at_cap || m.t + 1.4;
  streams.push((t) => { const k = easeIO((t - t0) / 1.25) * cnt;
    for (let i = 0; i < cnt; i++) { const c = i % 5, r = Math.floor(i / 5) % 5, l = Math.floor(i / 25);
      const p = clamp01((k - i) / 4); setInst(stack, i, sx + c * 0.5, 0.18 + l * 0.37 + (1 - p) * 1.5, sz + r * 0.5, 0, p * 0.78); }
    stack.instanceMatrix.needsUpdate = true; });
  blob(g, 3.6, 3.6, sx + 1, sz + 1);
  const inner = loopPath(Lx - 1.6, Lz - 1.6);
  const s1 = scooter(g, PAL.sky), s2 = scooter(g, PAL.lilac);
  streams.push((t) => { const u1 = t * 0.03 + 0.1, u2 = 0.6 - t * 0.026; const [x1, z1] = inner(u1), [x2, z2] = inner(u2);
    s1.position.set(x1, 0, z1); s1.rotation.y = heading(inner, u1); s2.position.set(x2, 0, z2); s2.rotation.y = heading(inner, u2) + Math.PI; });
  kids.push(tree(g, -10.5, 9.5), tree(g, 10.5, -9.5, 1.2), tree(g, 1, 8.4, 0.8));
  arrive(g, m.t, kids, first);
  return { g, focus: [cx + 0.5, 2, 0.5], size: [24, 7, 21], card: true };
};

// a 3D bar chart, block by block
BUILD.bars = (m, cx, first) => {
  const vals = m.values, labels = m.labels || vals.map(String), yrs = m.years || []; const n = vals.length;
  const step = Math.min(3.5, 28 / n), bw = step * 0.64, gapW = m.gap_after != null ? step * 0.45 : 0;
  const span = (n - 1) * step + gapW;
  const g = slab(world, Math.max(18, span + 8), 16, PAL.slab, cx, 0);
  const mx = Math.max(...vals.map(Math.abs)) || 1, HMAX = 11; const kids = [];
  const lsz = Math.min(0.95, ...labels.map((l) => (step * 0.95) / Math.max(0.5, textWidth(l))));
  const ysz = Math.min(0.85, ...yrs.map((y) => (step * 0.95) / Math.max(0.5, textWidth(String(y)))));
  const hl = m.hl != null ? m.hl : n - 1;
  vals.forEach((v, i) => {
    const x = -span / 2 + i * step + (m.gap_after != null && i > m.gap_after ? gapW : 0); const hgt = Math.max(0.3, (Math.abs(v) / mx) * HMAX);
    const isH = i === hl;
    const bar = box(g, bw, 1, bw, isH ? PAL.coral : [PAL.b2, PAL.b4, PAL.b1, PAL.b3][i % 4], x, 0, 0, Math.min(0.25, bw * 0.12));
    const t0 = (m.at_bars || m.t + 0.1) + i * Math.min(0.14, 1.1 / n);
    tl.fromTo(bar.scale, { y: 0.001 }, { y: hgt, duration: 0.85, ease: "back.out(1.25)" }, at(t0));
    tl.fromTo(bar.position, { y: 0 }, { y: hgt / 2, duration: 0.85, ease: "back.out(1.25)" }, at(t0));
    const val = text3(g, labels[i], { size: lsz, depth: 0.14, color: isH ? PAL.coral : PAL.ink }); val.position.set(x, hgt + 0.75, 0);
    tl.from(val.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(2)" }, at(t0 + 0.55));
    if (yrs[i] != null) { const yr = text3(g, String(yrs[i]), { size: ysz, depth: 0.08, color: PAL.ink, flat: true }); yr.position.set(x - 0.2, 0.03, bw / 2 + 1.1); }
    blob(g, bw * 1.7, bw * 1.7, x + 0.2, 0.2);
  });
  if (m.gap_after != null) { const gx = -span / 2 + (m.gap_after + 0.5) * step + gapW / 2; for (let k = -1; k <= 1; k++) cyl(g, 0.11, 0.1, PAL.muted, gx + k * 0.34, 0, bw / 2 + 1.0, 10); }
  kids.push(tree(g, -span / 2 - 3.2, -5.5, 1.1), tree(g, span / 2 + 3, 5, 1.2));
  arrive(g, m.t, kids, first);
  return { g, focus: [cx, 5.6, 0.5], size: [span + bw + 2, 13, 7], card: true };
};

// stations a parcel passes through; the camera rides along with the coral parcel
const STATION = {
  shop(p) {
    const s = new THREE.Group(); p.add(s);
    box(s, 4.2, 2.6, 3.4, PAL.b3, -0.6, 0, -0.8, 0.18); box(s, 4.6, 0.26, 3.8, PAL.roof, -0.6, 2.6, -0.8, 0.1);
    for (let k = 0; k < 6; k++) box(s, 0.66, 0.2, 1.1, k % 2 ? PAL.card : PAL.coral, -2.25 + k * 0.66, 2.0, 1.4, 0.06);
    box(s, 2.6, 0.9, 1.0, PAL.card, 0.4, 0, 1.9, 0.12);
    person(s, PAL.sky, 2.6, 0.2, 1.25); blob(s, 6, 5, -0.4, 0);
    const pk = parcels(s, 5); [[-1.8, 0, 2.6], [-2.4, 0, 2.2], [-1.6, 0.47, 2.4], [-3, 0, 1.9], [-2.6, 0.47, 2.1]].forEach(([x, y, z], i) => setInst(pk, i, x, y + 0.23, z, i * 0.4));
    return { s, a: [0.0, 1.19, 1.9], b: [1.4, 1.19, 1.9], pin: [-0.6, 4.6, -0.8] };
  },
  hub(p) {
    const s = new THREE.Group(); p.add(s);
    box(s, 12, 0.2, 9.5, PAL.floor, 0, 0, 0, 0.1); box(s, 12, 3.4, 0.4, PAL.b1, 0, 0, -4.8, 0.14); box(s, 0.4, 3.4, 9.5, PAL.b1, -6, 0, 0, 0.14);
    for (let k = 0; k < 3; k++) box(s, 0.5, 0.2, 9.4, PAL.b5, -2 + k * 3.6, 3.4, 0, 0.08);
    const lanes = [-2.6, 0, 2.6]; lanes.forEach((z) => box(s, 10.5, 0.5, 1.1, PAL.belt, 0, 0.2, z, 0.1));
    const im = parcels(s, 33);
    streams.push((t) => { for (let i = 0; i < 33; i++) { const lane = i % 3; if (lane === 1) { setInst(im, i, 0, -5, 0, 0, 0); continue; }
      const u = (((i / 33) * 3 + t * 0.16 * (lane === 2 ? 1.25 : 1)) % 1); setInst(im, i, -5 + u * 10, 0.93, lanes[lane], 0, 1); } im.instanceMatrix.needsUpdate = true; });
    for (let k = 0; k < 2; k++) { const arm = new THREE.Group(); arm.position.set(-1.8 + k * 4, 0, -1.3 + k * 2.6); s.add(arm); cyl(arm, 0.25, 1.4, PAL.ink, 0, 0, 0, 12);
      box(arm, 2.4, 0.26, 0.26, PAL.coral, 1.0, 1.4, 0, 0.1); streams.push((t) => { arm.rotation.y = Math.sin(t * 1.8 + k * 2) * 0.7; }); }
    blob(s, 14, 11);
    return { s, a: [-4.8, 0.93, 0], b: [4.8, 0.93, 0], pin: [0, 5, -1] };
  },
  road(p, ts, dwell) {
    const s = new THREE.Group(); p.add(s);
    box(s, 15, 0.12, 5, PAL.road, 0, 0, 0, 0.05);
    for (let k = 0; k < 6; k++) box(s, 1.3, 0.03, 0.2, PAL.lane, -6.2 + k * 2.5, 0.12, 0, 0.02);
    const others = [0, 1].map((k) => { const tr = truck(s, [PAL.sky, PAL.lilac][k]); tr.position.y = 0.12; return tr; });
    streams.push((t) => others.forEach((tr, k) => { const u = ((t * 0.09 + k * 0.5) % 1); tr.position.set(6.5 - u * 13, 0.12, -1.2); tr.rotation.y = Math.PI; }));
    const mine = truck(s, PAL.mint); mine.position.y = 0.12;
    streams.push((t) => { const u = clamp01((t - ts) / dwell); mine.position.x = -5 + easeIO(u) * 10 + Math.max(0, t - ts - dwell) * 6; mine.position.z = 1.2;
      mine.visible = mine.position.x < 7.6; });
    return { s, a: [-5.35, 2.03, 1.2], b: [4.65, 2.03, 1.2], pin: [0, 3.6, 0] };
  },
  hub2(p) {
    const s = new THREE.Group(); p.add(s);
    box(s, 8.5, 0.2, 7, PAL.floor, 0, 0, 0, 0.1); box(s, 8.5, 2.8, 0.4, PAL.b4, 0, 0, -3.5, 0.14); box(s, 0.4, 2.8, 7, PAL.b4, -4.25, 0, 0, 0.14);
    box(s, 7, 0.5, 1.1, PAL.belt, 0, 0.2, 0, 0.1); box(s, 1.1, 0.5, 2.6, PAL.belt, 2.9, 0.2, 1.8, 0.1);
    const im = parcels(s, 10);
    streams.push((t) => { for (let i = 0; i < 10; i++) setInst(im, i, -3.4 + ((i / 10 + t * 0.15) % 1) * 6.8, 0.93, 0, 0, 1); im.instanceMatrix.needsUpdate = true; });
    const pk = parcels(s, 8); for (let i = 0; i < 8; i++) setInst(pk, i, -3 + (i % 4) * 0.7, 0.43 + Math.floor(i / 4) * 0.47, 2.4, 0, 1);
    blob(s, 10, 8.5);
    return { s, a: [-3.4, 0.93, 0], b: [2.9, 0.93, 2.9], pin: [0, 4.2, -1] };
  },
  home(p, ts, dwell) {
    const s = new THREE.Group(); p.add(s);
    box(s, 4.4, 2.9, 4.2, PAL.b0, 0, 0, -1.4, 0.2);
    const rf = new THREE.Mesh(new THREE.ConeGeometry(3.5, 1.9, 4), mat(PAL.coral)); rf.position.set(0, 3.85, -1.4); rf.rotation.y = Q; rf.castShadow = true; s.add(rf);
    box(s, 1.0, 1.7, 0.12, PAL.door, 0.9, 0, 0.72, 0.08); box(s, 0.9, 0.7, 0.06, PAL.window, -1.0, 1.2, 0.72, 0.05);
    box(s, 3, 0.08, 1.6, PAL.path, 0.9, 0, 1.6, 0.04);
    tree(s, -3.8, 2.0, 1.1); tree(s, 3.6, -3.5, 0.9); blob(s, 6.4, 6.2, 0, -1.4);
    const sc2 = scooter(s, PAL.sky);
    streams.push((t) => { const u = clamp01((t - ts + 0.5) / (dwell + 0.5)); sc2.position.set(-6.2 + easeIO(u) * 4.4, 0, 2.6); });
    return { s, a: [-2.2, 0.98, 2.6], b: [0.9, 0.3, 1.25], pin: [0, 5.6, -1.4] };
  },
};
BUILD.route = (m, cx, first) => {
  const names = m.names && m.names.length ? m.names : ["揽收", "分拨", "干线", "再分拨", "派送"]; const k = names.length;
  const kinds = m.kinds || names.map((_, i) => (i === 0 ? "shop" : i === k - 1 ? "home" : ["hub", "road", "hub2"][(i - 1) % 3]));
  const gapX = 17, L = (k - 1) * gapX + 18;
  const stripX = cx - 13 + L / 2;
  const g = slab(world, L, 16, PAL.slab2, stripX, 0);
  const ts = (m.at && m.at.length === k) ? m.at : names.map((_, i) => (m.t2 || m.t + 1) + i * 0.6);
  const st = kinds.map((kd, i) => {
    const gap = i < k - 1 ? ts[i + 1] - ts[i] : 1.4; const dwell = Math.max(0.25, Math.min(0.7, gap * 0.5));
    const o = STATION[kd](g, ts[i], dwell); o.s.position.x = -L / 2 + 9 + i * gapX; o.kd = kd; o.dwell = dwell; return o;
  });
  // the coral parcel: keyframes at each station's entry (on its word) and exit
  const hero = new THREE.Mesh(parcelGeo, heroMat); hero.castShadow = true; g.add(hero);
  const mark = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.8, 4), heroMat); mark.rotation.x = Math.PI; g.add(mark);
  const KP = [], KT = [];
  st.forEach((o, i) => { const x0 = o.s.position.x;
    KP.push([x0 + o.a[0], o.a[1], o.a[2]]); KT.push(ts[i] - (i ? 0.02 : 0));
    KP.push([x0 + o.b[0], o.b[1], o.b[2]]); KT.push(ts[i] + o.dwell); });
  const heroAt = (t) => {
    if (t <= KT[0]) return KP[0];
    for (let j = 1; j < KT.length; j++) if (t <= KT[j]) {
      const inside = j % 2 === 1; const u = (t - KT[j - 1]) / Math.max(0.05, KT[j] - KT[j - 1]); const e = easeIO(u);
      const a = KP[j - 1], b = KP[j]; const arc = inside ? 0 : Math.sin(clamp01(u) * Math.PI) * (2.2 + Math.abs(b[0] - a[0]) * 0.06);
      return [a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e + arc, a[2] + (b[2] - a[2]) * e];
    }
    return KP[KP.length - 1];
  };
  const hT0 = m.t - 0.3;
  streams.push((t) => { const p = heroAt(t); const s = Math.max(0.0001, 1.6 * backOut((t - hT0) / 0.5));
    hero.position.set(p[0], p[1] + 0.07 + 0.08, p[2]); hero.rotation.y = Q * 0.3 + Math.sin(t * 2) * 0.08; hero.scale.setScalar(s);
    mark.position.set(p[0], p[1] + 1.6 + Math.sin(t * 5) * 0.18, p[2]); mark.rotation.y = t * 2.4; mark.scale.setScalar(s / 1.6); });
  st.forEach((o, i) => bounce(o.s, ts[i] + 0.02, 0.1));
  // DOM pins over the stations: pop one by one on the count ("五站"), stay until the ride ends
  const pinT = m.at_pins || m.t + 0.6, endT = m.t + m.d + (m.d2 || 0);
  st.forEach((o, i) => pins.push({ id: "pin" + i, p: [stripX + o.s.position.x + o.pin[0], o.pin[1], o.pin[2]], on: Math.min(pinT + i * 0.12, ts[i] - 0.2), off: endT - 0.1, hi: ts[i] }));
  arrive(g, m.t, st.map((o) => o.s), first);
  const follow = (t) => { let x = 0, z = 0; for (let j = 0; j < 5; j++) { const p = heroAt(t - j * 0.09); x += p[0]; z += p[2]; } return [stripX + x / 5, 1.5, z / 5]; };
  return { g, focus: [stripX, 1.6, 0], size: [L - 2, 5, 12], card: true, slots: (L + 14) / SPACING, cont: { size: [34, 5, 12], follow } };
};

// unit price melts while volume climbs: a coin stack loses coins, a parcel tower grows beside it
BUILD.coins = (m, cx, first) => {
  const g = slab(world, 24, 18, PAL.slab, cx, 0);
  const coinG = new THREE.CylinderGeometry(1.6, 1.6, 0.34, 44), faceG = new THREE.CylinderGeometry(1.26, 1.26, 0.36, 44);
  const cm = new THREE.MeshStandardMaterial({ color: PAL.gold, roughness: 0.45, emissive: new THREE.Color(PAL.gold), emissiveIntensity: 0.08 });
  const fm = new THREE.MeshStandardMaterial({ color: PAL.gold2, roughness: 0.5 });
  const N = Math.max(1, Math.min(40, Math.round(m.a))), keep = Math.max(1, Math.min(N, Math.round(m.b)));
  const coins = []; const cX = -3.6;
  for (let i = 0; i < N; i++) { const c = new THREE.Group(); c.position.set(cX + R(-0.07, 0.07), 0.17 + i * 0.36, R(-0.07, 0.07)); g.add(c);
    const a = new THREE.Mesh(coinG, cm), b = new THREE.Mesh(faceG, fm); a.castShadow = b.castShadow = true; a.receiveShadow = true; c.add(a, b); coins.push(c); }
  blob(g, 5.6, 5.6, cX, 0);
  coins.forEach((c, i) => tl.from(c.position, { y: c.position.y + 9, duration: 0.45, ease: "bounce.out" }, at(m.t - 0.3 + i * Math.min(0.045, 0.7 / N))));
  const tb = m.at_drop || m.t + 1.8;
  coins.slice(keep).reverse().forEach((c, i) => {           // the extra coins hop off the top one by one, flip and drop into the void
    const t1 = tb + i * 0.09, side = i % 2 ? 1 : -1, y0 = c.position.y;
    tl.to(c.position, { y: y0 + 1.6, duration: 0.18, ease: "power2.out" }, at(t1));
    tl.to(c.position, { x: cX + side * (3.2 + i * 0.25), z: 3.6 + i * 0.25, y: -10, duration: 0.7, ease: "power2.in" }, at(t1 + 0.18));
    tl.to(c.rotation, { x: 1.9 * side, z: 0.6, duration: 0.88, ease: "none" }, at(t1));
  });
  const TN = 108; const tower = parcels(g, TN);
  streams.push((t) => { const k = easeIO((t - (m.t + 0.2)) / Math.max(1, m.d - 0.6)) * TN;
    for (let i = 0; i < TN; i++) { const c = i % 3, r = Math.floor(i / 3) % 3, l = Math.floor(i / 9); const p = clamp01(k - i);
      setInst(tower, i, 2.4 + c * 0.66, 0.23 + l * 0.47 + (1 - p) * 2, -0.66 + r * 0.66, 0, p); }
    tower.instanceMatrix.needsUpdate = true; });
  blob(g, 4.2, 4.2, 3.06, 0);
  const ya = text3(g, String(m.ya || ""), { size: 0.85, depth: 0.08, color: PAL.ink, flat: true }); ya.position.set(cX - 0.3, 0.03, 3.0);
  const yb = text3(g, String(m.yb || ""), { size: 0.85, depth: 0.08, color: PAL.ink, flat: true }); yb.position.set(3.0, 0.03, 3.0);
  const kids = [tree(g, -10, -6.5), tree(g, 10, 6.5, 1.2), tree(g, 9, -6, 0.9), person(g, PAL.sky, 7.2, 3.2, 1.3)];
  arrive(g, m.t, kids, first);
  return { g, focus: [cx - 0.3, 3.4, 0.3], size: [14, 9, 7], card: true };
};

// the reveal: the whole world from far away, a field of little towns rising around it, one word above
BUILD.scale = (m) => {
  const g = new THREE.Group(); world.add(g);
  const holder = new THREE.Group(); g.add(holder);
  const word = text3(holder, m.word || "规模", { size: 1, depth: 0.16, color: PAL.coral });
  const wt = m.at_word || m.t + 1.5;
  word.userData.glyphs.forEach((p, i) => tl.from(p.position, { y: -0.8, duration: 0.7, ease: "back.out(1.7)" }, at(wt - 0.3 + i * 0.1)));
  tl.from(word.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(1.7)" }, at(wt - 0.32));
  return { g, focus: [0, 2, 0], size: [100, 14, 50], card: true, late: (minX, maxX) => {
    // a medium-wide look back over the last islands while a field of little towns rises all around them
    const fx = Math.max(minX + 50, maxX - 62);
    for (let k = 0; k < 34; k++) {
      const side = k % 2 ? 1 : -1; const x = fx - 70 + (k / 34) * 150 + R(-5, 5), z = side * R(20, 40);
      const isl = slab(g, R(7, 10), R(7, 10), pick([PAL.slab, PAL.slab2, PAL.slab3]), x, z);
      for (let b = 0; b < 3; b++) building(isl, R(-2.2, 2.2), R(-2.2, 2.2), R(1.4, 2.2), R(1.4, 2.2), R(1.2, 4.6), pick([PAL.b0, PAL.b1, PAL.b2, PAL.b3, PAL.b4, PAL.b5]));
      tree(isl, R(-3, 3), R(-3, 3), 0.9);
      const pk = parcels(isl, 6); for (let i = 0; i < 6; i++) setInst(pk, i, 2.4 + (i % 3) * 0.66, 0.23 + Math.floor(i / 3) * 0.47, -2.6, 0, 1);
      const tr = at(m.t - 0.1 + (k % 14) * 0.09);
      tl.from(isl.position, { y: -14, duration: 0.9, ease: "back.out(1.3)" }, tr);
      tl.from(isl.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(1.6)" }, tr);
    }
    const size = [100, 14, 50];
    const view = viewFor(size, REG, AZ0) * ZOOM, ww = (view * W) / H;
    const s = ((PORTRAIT ? 0.62 : 0.34) * ww) / Math.max(0.5, textWidth(m.word || "规模"));
    const wy = 4 + view * (PORTRAIT ? 0.07 : 0.2);
    holder.scale.setScalar(s); holder.position.set(fx, wy, 0);
    streams.push((t) => { holder.position.y = wy + Math.sin(t * 1.3) * view * 0.006; });
    return { focus: [fx, 4, 0], size };
  } };
};

// the outro: toy letters and a pastel top hat
BUILD.outro = (m, cx, first) => {
  const g = slab(world, 22, 16, PAL.slab3, cx, 0);
  const title = m.title || "第九顶帽子";
  const name = text3(g, title, { size: Math.min(2.2, 12 / Math.max(1, textWidth(title))), depth: 0.55, colors: [PAL.coral, PAL.sky, PAL.mint, PAL.lilac, PAL.gold2] }); name.position.set(PORTRAIT ? -0.2 : -1.6, 1.25, 4.4);
  name.userData.glyphs.forEach((p, i) => tl.from(p.position, { y: 7, duration: 0.75, ease: "bounce.out" }, at(m.t + 0.05 + i * 0.08)));
  const prof = [[0, 0], [1.05, 0], [1.08, 0.04], [1.02, 0.07], [0.62, 0.08], [0.6, 0.14], [0.58, 1.0], [0.6, 1.05], [0.6, 1.08], [0, 1.08]].map(([x, y]) => new THREE.Vector2(x, y));
  const hat = new THREE.Group(); hat.position.set(3.4, 0, -3.6); hat.scale.setScalar(2.6); g.add(hat);
  const crown = new THREE.Mesh(new THREE.LatheGeometry(prof, 64), mat(PAL.ink, 0.6)); crown.castShadow = true; crown.receiveShadow = true; hat.add(crown);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.606, 0.606, 0.16, 64, 1, true), mat(PAL.coral)); band.position.y = 0.24; hat.add(band);
  blob(g, 6, 6, 3.4, -3.6);
  tl.from(hat.position, { y: 9, duration: 0.9, ease: "bounce.out" }, at(m.t - 0.15));
  streams.push((t) => { hat.rotation.y = t * 0.6; });
  const pk = parcels(g, 7); [[-7, 0, -3], [-7.66, 0, -3], [-7.33, 0.47, -3], [-6.4, 0, -2.2], [7.5, 0, 2], [7.5, 0.47, 2], [8.1, 0, 2.5]].forEach(([x, y, z], i) => setInst(pk, i, x, y + 0.23, z, i * 0.3, 1.1));
  const kids = [tree(g, -8.5, 4.5, 1.1), tree(g, 8.5, -5, 1.0), tree(g, -4, -6, 0.8)];
  arrive(g, m.t, kids, first);
  return { g, focus: [cx, 2.2, 0], size: PORTRAIT ? [25, 6, 12] : [17, 6, 9], card: false };
};

// ---------------------------------------------------------------- assemble
const built = []; let slot = 0, minX = 1e9, maxX = -1e9;
MODS.forEach((m, i) => {
  if (m.kind === "cont") { built.push(built[built.length - 1]); return; }
  const b = BUILD[m.kind](m, slot * SPACING, i === 0); b.m = m; built.push(b);
  if (m.kind !== "scale") { slot += b.slots || 1; minX = Math.min(minX, b.g.position.x - 14); maxX = Math.max(maxX, b.g.position.x + 14); }
});
built.forEach((b) => { if (b && b.late && !b._done) { Object.assign(b, b.late(minX, maxX)); b._done = true; } });

// the road that joins the islands, with traffic; clouds drifting over the void
const roadL = maxX - minX + 120, roadX = (minX + maxX) / 2;
box(world, roadL, 0.5, 3.6, PAL.road, roadX, -0.7, 15.2, 0.2);
for (let k = 0; k < roadL / 3; k++) box(world, 1.2, 0.03, 0.18, PAL.lane, roadX - roadL / 2 + k * 3, -0.2, 15.2, 0.02);
const fleet = [];
for (let k = 0; k < 10; k++) { const tr = truck(world, [PAL.coral, PAL.mint, PAL.sky, PAL.lilac][k % 4]); fleet.push({ tr, ph: k / 10 + R(0, 0.04), lane: k % 2 }); }
streams.push((t) => fleet.forEach(({ tr, ph, lane }) => {
  const u = ((((t * 9) / roadL + ph) % 1) + 1) % 1; const x = roadX - roadL / 2 + (lane ? 1 - u : u) * roadL;
  tr.position.set(x, -0.2, 15.2 + (lane ? -0.85 : 0.85)); tr.rotation.y = lane ? Math.PI : 0; }));
const clouds = [];
for (let k = 0; k < 18; k++) clouds.push({ c: cloud(world, minX - 30 + k * ((maxX - minX + 60) / 18) + R(-5, 5), R(17, 24), R(-46, -30), R(0.9, 1.6)), v: R(0.4, 0.9) });
clouds.forEach((o) => (o.x0 = o.c.position.x));
streams.push((t) => clouds.forEach((o) => { o.c.position.x = o.x0 + t * o.v; }));

// ---------------------------------------------------------------- camera
const keys = MODS.map((m, i) => {
  const b = built[i]; const isCont = m.kind === "cont"; const reg = b.card === false ? REG0 : REG;
  const size = isCont ? b.cont.size : b.size; const az = AZ0 + (i % 2 ? 7 : -7);
  return { tx: b.focus[0], ty: b.focus[1], tz: isCont ? 0 : b.focus[2], view: viewFor(size, reg, az) * ZOOM, az, el: EL0, fx: reg.fx, fy: reg.fy, fw: isCont ? 1 : 0, follow: isCont ? b.cont.follow : null };
});
const flights = MODS.map((m, i) => { const fly = i === 0 ? 1.6 : Math.min(1.05, Math.max(0.55, (MODS[i - 1].d || 1) * 0.32)); return { t0: i === 0 ? 0 : at(m.t - fly * 0.7), fly }; });
{
  const k0 = keys[0];
  Object.assign(cam, { tx: k0.tx - 6, ty: k0.ty + 2, tz: k0.tz - 3, view: k0.view * 1.45, az: k0.az - 16, el: EL0 + 6, fx: k0.fx, fy: k0.fy, fw: 0 });
}
let followFn = null;
keys.forEach((k, i) => {
  const { t0, fly } = flights[i]; const { follow, ...to } = k;
  if (follow) followFn = follow;
  tl.to(cam, { ...to, duration: fly, ease: i === 0 ? "power2.out" : "power3.inOut" }, t0);
  const end = i + 1 < keys.length ? flights[i + 1].t0 : CFG.dur;
  const hold = end - (t0 + fly);
  if (hold > 0.05) tl.to(cam, { az: k.az + (i % 2 ? -6 : 6), view: k.view * (MODS[i].kind === "scale" ? 0.86 : 0.92), duration: hold, ease: "none" }, t0 + fly);
});

const _v = new THREE.Vector3();
function project(p) { _v.set(p[0], p[1], p[2]).project(camera); return [((_v.x + 1) / 2) * W, ((1 - _v.y) / 2) * H]; }

const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), CFG.bloom ?? 0.12, 0.5, 0.96));
composer.addPass(new OutputPass());

function renderAt(t) {
  tl.seek(at(t), false);
  for (const f of streams) f(t);
  let tx = cam.tx, tz = cam.tz;
  if (cam.fw > 0.001 && followFn) { const p = followFn(t); tx += (p[0] - tx) * cam.fw; tz += (p[2] - tz) * cam.fw * 0.4; }
  const az = (cam.az * Math.PI) / 180, el = (cam.el * Math.PI) / 180, r = 220;
  camera.position.set(tx + r * Math.cos(el) * Math.sin(az), cam.ty + r * Math.sin(el), tz + r * Math.cos(el) * Math.cos(az));
  camera.lookAt(tx, cam.ty, tz);
  const hh = cam.view, ww = (hh * W) / H;
  const ox = (0.5 - cam.fx) * ww, oy = (cam.fy - 0.5) * hh;
  camera.left = -ww / 2 + ox; camera.right = ww / 2 + ox; camera.top = hh / 2 + oy; camera.bottom = -hh / 2 + oy; camera.updateProjectionMatrix();
  camera.updateMatrixWorld();
  const big = Math.max(34, Math.hypot(ww, hh) * 0.62);
  sun.position.set(tx + SUN.x * 160, SUN.y * 160, tz + SUN.z * 160); sun.target.position.set(tx, 0, tz); sun.target.updateMatrixWorld();
  sc.left = -big; sc.right = big; sc.top = big; sc.bottom = -big; sc.near = 1; sc.far = 160 + big * 1.6; sc.updateProjectionMatrix();
  for (const pn of pins) {
    const el2 = document.getElementById(pn.id); if (!el2) continue;
    const [sx, sy] = project(pn.p); const a = clamp01((t - pn.on) / 0.25) * (1 - clamp01((t - pn.off) / 0.25));
    const s = 0.6 + 0.4 * backOut((t - pn.on) / 0.35);
    el2.style.transform = `translate(${sx.toFixed(1)}px, ${sy.toFixed(1)}px) translate(-50%, -100%) scale(${s.toFixed(3)})`;
    const inside = sx > -80 && sx < W + 80 && sy > 40 && sy < H + 120;
    el2.style.opacity = inside ? a.toFixed(3) : "0"; el2.style.visibility = inside && a > 0.001 ? "visible" : "hidden";
    el2.classList.toggle("on", t >= pn.hi - 0.05);
  }
  composer.render();
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
renderAt(0);
window.addEventListener("hf-seek", (e) => { renderAt(e.detail.time); renderer.getContext().finish(); });
window.__h9IsoReady && window.__h9IsoReady();
