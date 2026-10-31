// 九帽动效 · studio world — one continuous 3D set the camera flies through, beat by beat.
// Real extruded CJK type (font outlines from the build), PBR materials, image environment light,
// bloom + depth of field. Deterministic: every frame is drawn from the seek time alone (hf-seek).
// CFG and GLYPHS are injected by styles/studio.py.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const CFG = window.__H9_WORLD;
const GLYPHS = window.__H9_GLYPHS;
const W = CFG.w, H = CFG.h, T = CFG.t;
const gsap = window.gsap;
const CLAY = CFG.look === "clay";

// ---------- seeded random (mulberry32)
let _s = 9;
const rnd = () => { _s |= 0; _s = (_s + 0x6d2b79f5) | 0; let t = Math.imul(_s ^ (_s >>> 15), 1 | _s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => a + (b - a) * rnd();

// ---------- renderer / scene
const canvas = document.getElementById("w3d");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.background = new THREE.Color(CFG.bg);
scene.fog = new THREE.Fog(CFG.bg, 14, 34);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = CFG.look === "clay" ? 0.9 : 0.55;
if (CFG.look === "clay") { renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap; renderer.toneMappingExposure = 1.0; }

const camera = new THREE.PerspectiveCamera(32, W / H, 0.1, 200);
const look = new THREE.Vector3();

const key = new THREE.DirectionalLight(0xffdcb0, CFG.look === "clay" ? 2.0 : 2.6); key.position.set(-6, 9, 8); scene.add(key);
if (CFG.look === "clay") { key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 6; key.shadow.bias = -0.0004;
  const sc = key.shadow.camera; sc.left = -9; sc.right = 9; sc.top = 9; sc.bottom = -9; sc.near = 0.5; sc.far = 40; key.target = new THREE.Object3D(); scene.add(key.target); }
const rim = new THREE.DirectionalLight(0x8fb4ff, 1.6); rim.position.set(7, 4, -10); scene.add(rim);
const spot = new THREE.SpotLight(0xfff1d6, 0, 30, 0.42, 0.6, 1.2); scene.add(spot); scene.add(spot.target);

// floor: dark satin with a soft sheen
const floor = new THREE.Mesh(new THREE.PlaneGeometry(400, 400), new THREE.MeshStandardMaterial({ color: CFG.floor, roughness: CLAY ? 0.95 : 0.32, metalness: CLAY ? 0 : 0.55 }));
floor.rotation.x = -Math.PI / 2; floor.position.y = CFG.floorY; floor.receiveShadow = true; scene.add(floor);

// contact shadow texture
const shTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d");
  const gr = g.createRadialGradient(64, 64, 4, 64, 64, 62); gr.addColorStop(0, "rgba(0,0,0,.75)"); gr.addColorStop(1, "rgba(0,0,0,0)"); g.fillStyle = gr; g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c); })();
function shadow(w, d, x, z) { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), new THREE.MeshBasicMaterial({ map: shTex, transparent: true, depthWrite: false, opacity: CFG.look === "clay" ? 0.35 : 1 }));
  m.rotation.x = -Math.PI / 2; m.position.set(x, CFG.floorY + 0.005, z); scene.add(m); return m; }

// ---------- materials (look = "gold" | "clay")
const matte = (c, r = 0.82) => () => new THREE.MeshStandardMaterial({ color: c, roughness: r, metalness: 0 });
const MAT_CLAY = {
  gold: matte(0xc2643f, 0.7), cream: matte(0x3d3833, 0.8), clay: matte(0x9b958c, 0.9), chrome: matte(0xe9e4da, 0.6),
  red: matte(0xb5523a, 0.6), frame: matte(0xf4f0e8, 0.9), satin: matte(0x2a2826, 0.7),
};
const MAT = CLAY ? MAT_CLAY : {
  gold: () => new THREE.MeshPhysicalMaterial({ color: 0xe9c47c, metalness: 1, roughness: 0.3, clearcoat: 0.5, clearcoatRoughness: 0.2 }),
  cream: () => new THREE.MeshPhysicalMaterial({ color: 0xd9d0bd, metalness: 0, roughness: 0.5, clearcoat: 0.2 }),
  clay: () => new THREE.MeshStandardMaterial({ color: 0x5d636b, metalness: 0, roughness: 0.75 }),
  chrome: () => new THREE.MeshPhysicalMaterial({ color: 0xdfe3ea, metalness: 1, roughness: 0.18 }),
  red: () => new THREE.MeshPhysicalMaterial({ color: 0xe0392f, metalness: 0, roughness: 0.35, clearcoat: 0.8 }),
  frame: () => new THREE.MeshPhysicalMaterial({ color: 0x1b1d22, metalness: 0.8, roughness: 0.35 }),
  satin: () => new THREE.MeshPhysicalMaterial({ color: 0x0e0e11, metalness: 0.1, roughness: 0.45, sheen: 0.6, sheenColor: new THREE.Color(0x3a3a44), clearcoat: 0.15 }),
};

// ---------- real 3D type
const geoCache = {};
function glyphGeo(ch, depth, bevel) {
  const k = ch + "|" + depth + "|" + bevel;
  if (geoCache[k]) return geoCache[k];
  const g = GLYPHS[ch]; if (!g) return null;
  const sp = new THREE.ShapePath();
  for (const c of g.p) {
    if (c[0] === "M") sp.moveTo(c[1], c[2]); else if (c[0] === "L") sp.lineTo(c[1], c[2]);
    else if (c[0] === "Q") sp.quadraticCurveTo(c[1], c[2], c[3], c[4]); else if (c[0] === "C") sp.bezierCurveTo(c[1], c[2], c[3], c[4], c[5], c[6]);
  }
  const shapes = sp.toShapes(CFG.ccw);
  const geo = new THREE.ExtrudeGeometry(shapes, { depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.7, bevelSegments: 3, curveSegments: 6 });
  geo.computeVertexNormals();
  return (geoCache[k] = geo);
}
// a word = one group per glyph (so glyphs can move on their own); size = cap height in world units
function text(str, { size = 1, depth = 0.18, bevel = 0.012, mat = MAT.gold(), track = 0.02, align = "center" } = {}) {
  const grp = new THREE.Group(); let x = 0; const glyphs = [];
  for (const ch of str) {
    if (ch === " ") { x += 0.32; continue; }
    const g = GLYPHS[ch]; if (!g) continue;
    const geo = glyphGeo(ch, depth, bevel);
    const piv = new THREE.Group(); const m = new THREE.Mesh(geo, mat); m.castShadow = true; m.receiveShadow = true;
    m.position.set(-g.a / 2, -0.38, -depth / 2);     // pivot at glyph centre
    piv.add(m); piv.position.x = x + g.a / 2; grp.add(piv); glyphs.push(piv);
    x += g.a + track;
  }
  const off = align === "center" ? -x / 2 : 0;
  glyphs.forEach((p) => (p.position.x += off));
  grp.scale.setScalar(size); grp.userData = { glyphs, width: x * size, mat };
  return grp;
}

// ---------- images
const loader = new THREE.TextureLoader();
const texPromises = [];
function tex(url) { const p = new Promise((res) => { const t = loader.load(url, () => res(t), undefined, () => res(t)); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; }); texPromises.push(p); return p; }
const IMG = {}; for (const [k, u] of Object.entries(CFG.images)) IMG[k] = tex(u);

function framed(texP, w, h, { border = 0.07 } = {}) {
  const g = new THREE.Group();
  const fr = new THREE.Mesh(new RoundedBoxGeometry(w + border * 2, h + border * 2, 0.09, 3, 0.03), MAT.frame()); fr.position.z = -0.05; fr.castShadow = true; g.add(fr);
  const pm = new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false });
  texP.then((t) => { pm.map = t; pm.needsUpdate = true; });
  const pic = new THREE.Mesh(new THREE.PlaneGeometry(w, h), pm); pic.position.z = 0.002; g.add(pic);
  g.userData = { pic: pm };
  return g;
}

// ---------- timeline (driven by seek; never by a clock)
const tl = gsap["timeline"]({ paused: true });   // seeked by hf-seek below, not by the runtime registry
const cam = { x: 0, y: 0.2, z: 6, lx: 0, ly: 0, lz: 0, focus: 6, roll: 0 };
const ST = CFG.stations;   // [{cam:[x,y,z], look:[x,y,z], focus}]
function setCam(i) { const s = ST[i]; return { x: s.cam[0], y: s.cam[1], z: s.cam[2], lx: s.look[0], ly: s.look[1], lz: s.look[2], focus: s.focus }; }
Object.assign(cam, setCam(0));
CFG.beats.forEach((b, i) => {
  if (i > 0) tl.to(cam, { ...setCam(i), duration: 1.0, ease: "power2.inOut" }, Math.max(0, b.t - 0.5));
  const s = ST[i];   // gentle dolly inside the beat, finished before the next flight starts
  const dd = b.d - 1.0;
  if (dd > 0.3) tl.to(cam, { z: ST[i].cam[2] - (s.drift || 0.35), duration: dd, ease: "none" }, b.t + 0.5);
});

// ---------- S1 · the flood of AI images + the hook title
const S1 = CFG.s1;
const flood = [];
const keys = Object.keys(IMG).filter((k) => k !== "quote");
for (let i = 0; i < 64; i++) {
  const k = keys[i % keys.length];
  const w = R(1.1, 1.9), h = w * 0.62;
  const pm = new THREE.MeshBasicMaterial({ color: 0xffffff, toneMapped: false, side: THREE.DoubleSide });
  IMG[k].then((t) => { const c = t.clone(); c.repeat.set(R(0.35, 0.7), R(0.35, 0.7)); c.offset.set(R(0, 1 - c.repeat.x), R(0, 1 - c.repeat.y)); c.needsUpdate = true; pm.map = c; pm.needsUpdate = true; });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), pm);
  const z = R(-8.6, -2.2), x = (rnd() < 0.5 ? -1 : 1) * R(2.2, 9.5) * (1 + (-z) / 9), y = R(-1.2, 4.8);
  m.position.set(x, y, z); m.rotation.set(R(-0.25, 0.25), R(-0.6, 0.6), R(-0.2, 0.2));
  scene.add(m); flood.push(m);
  const t0 = S1.t + R(0, 0.9);
  tl.from(m.position, { y: y + R(6, 10), duration: R(0.9, 1.4), ease: "power2.out" }, t0);
  tl.from(m.rotation, { x: R(-1.4, 1.4), z: R(-1, 1), duration: R(1, 1.5), ease: "power2.out" }, t0);
  tl.to(m.rotation, { y: `+=${R(-0.25, 0.25)}`, duration: 18, ease: "none" }, t0 + 1);
}
const title = text(S1.title, { size: 0.95, depth: 0.22, mat: MAT.gold() }); title.position.set(0, 0.25, 0); scene.add(title);
title.userData.glyphs.forEach((g, i) => {
  tl.from(g.position, { y: -0.9, duration: 0.55, ease: "back.out(1.6)" }, S1.t + 0.08 + i * 0.05);
  tl.from(g.rotation, { x: -1.2, duration: 0.55, ease: "power3.out" }, S1.t + 0.08 + i * 0.05);
  tl.from(g.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "power3.out" }, S1.t + 0.08 + i * 0.05);
});
const sub1 = text(S1.sub, { size: 0.26, depth: 0.05, bevel: 0.004, mat: MAT.cream() }); sub1.position.set(0, -0.55, 0.1); scene.add(sub1);
tl.from(sub1.position, { y: -1.0, duration: 0.6, ease: "power3.out" }, S1.t + 0.45);
tl.from(sub1.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4 }, S1.t + 0.45);
shadow(8, 1.4, 0, 0.2);

// ---------- S2 · two framed outputs on the set; labels, price stickers, verdict
const S2 = CFG.s2; const Z2 = ST[1].look[2];
const fw = 3.1, fh = fw * 2 / 3;
const fA = framed(IMG.a, fw, fh), fB = framed(IMG.b, fw, fh);
fA.position.set(-1.85, 0.25, Z2); fA.rotation.y = 0.16; fB.position.set(1.85, 0.25, Z2); fB.rotation.y = -0.16;
scene.add(fA, fB); shadow(3.6, 1.1, -1.85, Z2 + 0.2); shadow(3.6, 1.1, 1.85, Z2 + 0.2);
tl.from(fA.position, { x: -7, duration: 0.9, ease: "power3.out" }, S2.t - 0.3);
tl.from(fB.position, { x: 7, duration: 0.9, ease: "power3.out" }, S2.t - 0.2);
tl.from(fA.rotation, { y: 1.1, duration: 0.9, ease: "power3.out" }, S2.t - 0.3);
tl.from(fB.rotation, { y: -1.1, duration: 0.9, ease: "power3.out" }, S2.t - 0.2);
const labA = text(S2.la, { size: 0.3, depth: 0.06, bevel: 0.005, mat: MAT.cream() }); labA.position.set(-1.85, -1.0, Z2 + 0.35); scene.add(labA);
const labB = text(S2.lb, { size: 0.3, depth: 0.06, bevel: 0.005, mat: MAT.cream() }); labB.position.set(1.85, -1.0, Z2 + 0.35); scene.add(labB);
[[labA, S2.ta], [labB, S2.tb]].forEach(([l, t]) => l.userData.glyphs.forEach((g, i) => {
  tl.from(g.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.35, ease: "back.out(2)" }, t - 0.1 + i * 0.04);
}));
const stickers = S2.stickers.map((s, i) => {
  const g = new THREE.Group();
  const pill = new THREE.Mesh(new RoundedBoxGeometry(0.34 * s.length + 0.36, 0.42, 0.08, 4, 0.1), MAT.red()); g.add(pill);
  const tx = text(s, { size: 0.24, depth: 0.03, bevel: 0.003, mat: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.4 }) }); tx.position.z = 0.05; g.add(tx);
  const pos = [[0.95, 0.55], [-0.95, -0.45], [0.85, -0.5]][i % 3];
  g.position.set(1.85 + pos[0], 0.25 + pos[1], Z2 + 0.18); g.rotation.z = [-0.18, 0.12, 0.2][i % 3];
  scene.add(g);
  tl.from(g.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(3)" }, S2.ts + i * 0.12);
  return g;
});
if (S2.tv) {
  tl.to(fB.position, { z: Z2 - 1.2, y: -0.1, duration: 0.7, ease: "power3.inOut" }, S2.tv);
  tl.to(fB.rotation, { x: -0.35, duration: 0.7, ease: "power3.inOut" }, S2.tv);
  stickers.forEach((g) => tl.to(g.position, { z: Z2 - 1.0, y: g.position.y - 0.4, duration: 0.7, ease: "power3.inOut" }, S2.tv));
  tl.to(fB.userData.pic.color, { r: 0.22, g: 0.22, b: 0.24, duration: 0.6 }, S2.tv);
  tl.to(labB.position, { y: -1.5, duration: 0.6 }, S2.tv);
  tl.to(fA.position, { x: -1.2, z: Z2 + 0.7, duration: 0.8, ease: "power3.inOut" }, S2.tv);
  tl.to(fA.rotation, { y: 0.06, duration: 0.8, ease: "power3.inOut" }, S2.tv);
  tl.to(labA.position, { x: -1.2, z: Z2 + 1.05, duration: 0.8, ease: "power3.inOut" }, S2.tv);
  tl.fromTo(spot, { intensity: 0 }, { intensity: 60, duration: 0.6 }, S2.tv);
}
spot.position.set(-1.2, 6, Z2 + 3); spot.target.position.set(-1.2, 0, Z2);

// ---------- S3 · "工具" sinks, "判断" rises gold and glows
const S3 = CFG.s3; const Z3 = ST[2].look[2];
const wTool = text(S3.a, { size: 0.95, depth: 0.25, mat: MAT.clay() }); wTool.position.set(-1.7, 0.1, Z3); scene.add(wTool);
const goldJ = MAT.gold(); goldJ.emissive = new THREE.Color(0x3d2a06); goldJ.emissiveIntensity = 0;
const wJudge = text(S3.b, { size: 1.25, depth: 0.3, mat: goldJ }); wJudge.position.set(1.7, 0.2, Z3); scene.add(wJudge);
shadow(5, 1.2, -1.7, Z3 + 0.2); shadow(5, 1.2, 1.7, Z3 + 0.2);
wTool.userData.glyphs.forEach((g, i) => tl.from(g.position, { y: -1.6, duration: 0.6, ease: "back.out(1.4)" }, S3.ta - 0.15 + i * 0.06));
tl.to(wTool.rotation, { z: 0.22, x: -0.5, duration: 0.6, ease: "power2.in" }, S3.tb);
tl.to(wTool.position, { y: -1.2, duration: 0.6, ease: "power2.in" }, S3.tb);
wJudge.userData.glyphs.forEach((g, i) => {
  tl.from(g.position, { y: -2.2, duration: 0.7, ease: "back.out(1.5)" }, S3.tb + i * 0.07);
  tl.from(g.rotation, { y: -1.4, duration: 0.8, ease: "power3.out" }, S3.tb + i * 0.07);
});
tl.to(goldJ, { emissiveIntensity: 1.6, duration: 0.4, ease: "power2.out" }, S3.tb + 0.5);
tl.to(goldJ, { emissiveIntensity: 0.5, duration: 1.2, ease: "power2.out" }, S3.tb + 0.9);

// ---------- S4 · 100 tiles on the floor: 90 rise grey, the last 10 rise gold; the number counts up behind
const S4 = CFG.s4; const Z4 = ST[3].look[2];
const tileGeo = new RoundedBoxGeometry(0.42, 0.22, 0.42, 3, 0.05);
const greyM = CLAY ? new THREE.MeshStandardMaterial({ color: 0xd8d1c6, roughness: 0.9 }) : new THREE.MeshPhysicalMaterial({ color: 0x3f454d, roughness: 0.55, metalness: 0.2, clearcoat: 0.3 });
const goldT = MAT.gold(); goldT.emissive = new THREE.Color(0x3d2a06); goldT.emissiveIntensity = 0;
for (let i = 0; i < 100; i++) {
  const r = Math.floor(i / 10), c = i % 10;
  const hl = i >= S4.v && i < S4.v + S4.hl;
  const m = new THREE.Mesh(tileGeo, hl ? goldT : greyM); m.castShadow = true; m.receiveShadow = true;
  m.position.set((c - 4.5) * 0.52, CFG.floorY + 0.11, Z4 - (r - 4.5) * 0.52 + 0.4);   // last row (the 10 that matter) sits at the back, in view
  scene.add(m);
  const dist = Math.hypot(c - 4.5, r - 4.5);
  tl.from(m.position, { y: CFG.floorY - 0.4, duration: 0.45, ease: "back.out(2)" }, S4.ta + dist * 0.06);
  if (hl) tl.to(m.position, { y: CFG.floorY + 0.55, duration: 0.5, ease: "back.out(2.4)" }, S4.th + (i - S4.v) * 0.04);
}
tl.to(goldT, { emissiveIntensity: 1.4, duration: 0.4 }, S4.th);
// counting number: one mesh per digit per slot, visibility switched by the counter value
const numGrp = new THREE.Group(); numGrp.position.set(0, 0.55, Z4 - 2.4); scene.add(numGrp);
const numMat = MAT.cream();
const slots = [[], []];
for (let s = 0; s < 2; s++) for (let d = 0; d <= 9; d++) { const t3 = text(String(d), { size: 2.2, depth: 0.35, mat: numMat }); t3.position.x = (s - 0.5) * 1.35 - 0.55; t3.visible = false; numGrp.add(t3); slots[s].push(t3); }
const pct = text("%", { size: 1.1, depth: 0.25, mat: MAT.gold() }); pct.position.set(1.4, -0.4, 0); numGrp.add(pct);
const ctr = { v: 0 };
tl.fromTo(ctr, { v: 0 }, { v: S4.v, duration: 1.3, ease: "power2.out" }, S4.ta);
tl.from(numGrp.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(1.6)" }, S4.t);
function showCounter() { const n = Math.max(0, Math.min(99, Math.round(ctr.v))); const tens = Math.floor(n / 10), ones = n % 10;
  slots[0].forEach((m, d) => (m.visible = n >= 10 && d === tens)); slots[1].forEach((m, d) => (m.visible = d === ones)); }

// ---------- S5 · the reject pile: big image panel the camera pushes on (the line itself is a crisp DOM layer)
const S5 = CFG.s5; const Z5 = ST[4].look[2];
const pq = framed(IMG.quote, 4.2, 4.2 * 2 / 3, { border: 0.05 }); pq.position.set(1.7, 0.35, Z5); pq.rotation.y = -0.34; scene.add(pq);
tl.from(pq.position, { y: -3, duration: 0.9, ease: "power3.out" }, S5.t - 0.3);
tl.from(pq.rotation, { x: -0.9, duration: 0.9, ease: "power3.out" }, S5.t - 0.3);
shadow(4.8, 1.2, 1.7, Z5 + 0.3);

// ---------- S6 · the hat + the name
const S6 = CFG.s6; const Z6 = ST[5].look[2];
const prof = [[0, 0], [1.05, 0], [1.08, 0.04], [1.02, 0.07], [0.62, 0.08], [0.6, 0.14], [0.58, 1.0], [0.6, 1.05], [0.6, 1.08], [0, 1.08]].map(([x, y]) => new THREE.Vector2(x, y));
const hat = new THREE.Group();
const crown = new THREE.Mesh(new THREE.LatheGeometry(prof, 96), MAT.satin()); crown.material.side = THREE.DoubleSide; hat.add(crown);
const band = new THREE.Mesh(new THREE.CylinderGeometry(0.605, 0.605, 0.16, 96, 1, true), MAT.gold()); band.position.y = 0.24; hat.add(band);
hat.scale.setScalar(0.7); hat.position.set(0, 0.95, Z6); hat.rotation.x = 0.12; scene.add(hat);
tl.from(hat.position, { y: 4.5, duration: 0.9, ease: "bounce.out" }, S6.t - 0.1);
tl.fromTo(hat.rotation, { y: -1.2 }, { y: 0.5, duration: Math.max(1, S6.d), ease: "power1.out" }, S6.t - 0.1);
const name = text(S6.title, { size: 0.62, depth: 0.16, mat: MAT.gold() }); name.position.set(0, -0.05, Z6 + 0.2); scene.add(name);
name.userData.glyphs.forEach((g, i) => tl.from(g.position, { y: -1.4, duration: 0.55, ease: "back.out(1.6)" }, S6.t + 0.3 + i * 0.06));
shadow(4, 1.2, 0, Z6 + 0.2);

// ---------- post: bloom on the brightest points only, shallow depth of field
const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
const bokeh = new BokehPass(scene, camera, { focus: 6, aperture: CFG.aperture, maxblur: 0.006 });
composer.addPass(bokeh);
if (!CLAY) composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.22, 0.45, 0.93));
composer.addPass(new OutputPass());

function renderAt(t) {
  tl.seek(Math.max(0, t), false);
  if (CLAY) { key.position.set(cam.lx - 6, 9, cam.lz + 8); key.target.position.set(cam.lx, 0, cam.lz); key.target.updateMatrixWorld(); }
  camera.position.set(cam.x, cam.y, cam.z);
  look.set(cam.lx, cam.ly, cam.lz); camera.lookAt(look);
  bokeh.uniforms.focus.value = cam.focus;
  showCounter();
  composer.render();
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
Promise.all(texPromises).then(() => {
  renderAt(0);
  window.addEventListener("hf-seek", (e) => { renderAt(e.detail.time); renderer.getContext().finish(); });
  window.__h9WorldReady && window.__h9WorldReady();
});
