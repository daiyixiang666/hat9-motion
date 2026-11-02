// 九帽动效 · chrome3d — Y2K liquid chrome. Each beat is a display "station" floating in a black void; the camera
// whips from one to the next. Real extruded type (font outlines from the build), a procedural studio HDRI for sharp
// chrome reflections, iridescent + holographic materials, bloom glints, chromatic edge.
// Deterministic: every frame is drawn from the seek time alone (hf-seek). CFG and GLYPHS come from styles/chrome3d.py.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const CFG = window.__H9_CHROME;
const GLYPHS = window.__H9_GLYPHS;
const W = CFG.w, H = CFG.h, P = CFG.portrait, D = CFG.D;
const gsap = window.gsap;
const PINK = new THREE.Color(CFG.accent);
const FOV = P ? 44 : 30;
const SHIFT = P ? 100 : 30;          // px the subject band sits above the frame centre (captions live below)
const FLOOR = -2.9;
// a whip flight takes FLY s and lands ARR s before its sentence starts (inside the narration pause);
// each station pre-rolls its main object so it is readable on the first spoken word
const ARR = 0.08, FLY = 0.45;
CFG.beats.forEach((c, i) => { c.ta = i ? c.t - ARR : 0; });
const pre = (c, k = 0.35) => Math.max(0, c.ta - k);

// ---------- seeded random (mulberry32)
let _s = 23;
const rnd = () => { _s |= 0; _s = (_s + 0x6d2b79f5) | 0; let t = Math.imul(_s ^ (_s >>> 15), 1 | _s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const R = (a, b) => a + (b - a) * rnd();
const clamp01 = (x) => Math.max(0, Math.min(1, x));
const expoOut = (x) => (x >= 1 ? 1 : 1 - Math.pow(2, -10 * x));

// ---------- renderer / scene
const canvas = document.getElementById("w3d");
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
renderer.setPixelRatio(1);
renderer.setSize(W, H, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0x000000, 14, 32);
const U = { uT: { value: 0 } };       // shared time uniform (seek time)

// background: near-black with a faint violet lift behind the subject
scene.background = (() => {
  const c = document.createElement("canvas"); c.width = 256; c.height = 256; const g = c.getContext("2d");
  const gr = g.createRadialGradient(128, P ? 112 : 120, 4, 128, 128, 190);
  gr.addColorStop(0, "#1a1520"); gr.addColorStop(0.45, "#09080c"); gr.addColorStop(1, "#000000");
  g.fillStyle = gr; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();

// procedural studio HDRI: black void, white softboxes and strip lights, a hard horizon line with a silver ground band just below it
// (flat type faces reflect that band: the classic chrome banding), one pink neon tube.
// Pixels near white are boosted ×4 so chrome gets true HDR highlights (and bloom glints).
function studioHDRI() {
  const w = 1024, h = 512, c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d");
  const gr = g.createLinearGradient(0, 0, 0, h);
  gr.addColorStop(0, "#000"); gr.addColorStop(0.3, "#040405"); gr.addColorStop(0.44, "#18181e"); gr.addColorStop(0.493, "#55555f");
  gr.addColorStop(0.5, "#e6e6ee"); gr.addColorStop(0.53, "#9c9ca6"); gr.addColorStop(0.6, "#3a3a42"); gr.addColorStop(0.72, "#121216"); gr.addColorStop(1, "#030304");
  g.fillStyle = gr; g.fillRect(0, 0, w, h);
  g.fillStyle = "#fff";
  g.filter = "blur(5px)";
  g.fillRect(400, 26, 240, 64);            // overhead softbox
  g.fillRect(140, 110, 24, 250);           // left strip
  g.fillRect(872, 100, 20, 270);           // right strip
  g.fillRect(560, 176, 280, 12);           // back strip
  g.fillRect(40, 150, 70, 120);            // fill card
  g.filter = "blur(2px)";
  g.fillRect(0, 254, w, 4);                // horizon line, exactly at eye level
  g.filter = "blur(3px)"; g.fillStyle = CFG.accent;
  g.fillRect(250, 296, 460, 9);            // pink neon tube
  g.fillRect(960, 70, 8, 170);
  g.filter = "blur(36px)"; g.fillStyle = "rgba(150,120,255,.35)";
  g.fillRect(640, 330, 260, 110);          // cool violet bounce (feeds the iridescence)
  g.filter = "none";
  const px = g.getImageData(0, 0, w, h).data, n = w * h;
  const data = new Uint16Array(n * 4), toH = THREE.DataUtils.toHalfFloat;
  for (let i = 0; i < n; i++) {
    for (let k = 0; k < 3; k++) { const v = px[i * 4 + k] / 255; let L = Math.pow(v, 2.2); if (v > 0.92) L *= 4; data[i * 4 + k] = toH(L); }
    data[i * 4 + 3] = toH(1);
  }
  const t = new THREE.DataTexture(data, w, h, THREE.RGBAFormat, THREE.HalfFloatType);
  t.mapping = THREE.EquirectangularReflectionMapping; t.colorSpace = THREE.LinearSRGBColorSpace;
  t.magFilter = t.minFilter = THREE.LinearFilter; t.needsUpdate = true;
  return t;
}
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromEquirectangular(studioHDRI()).texture;

const camera = new THREE.PerspectiveCamera(FOV, W / H, 0.1, 400);
camera.setViewOffset(W, H, 0, SHIFT, W, H);
const lookV = new THREE.Vector3();

// floor: a fine wire grid fading into the fog (acid-graphics ground plane)
const grid = new THREE.GridHelper(800, 400, 0x3a3a46, 0x1b1b22); grid.position.y = FLOOR;
grid.material.transparent = true; grid.material.opacity = 0.55; scene.add(grid);

// ---------- materials
function liquid(mat, amp0 = 0.004) {   // ripples the surface + its normals: reflections slide like liquid metal
  const ua = { value: amp0 };
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uT = U.uT; sh.uniforms.uAmp = ua;
    sh.vertexShader = "uniform float uT; uniform float uAmp;\n" + sh.vertexShader
      .replace("#include <beginnormal_vertex>", `#include <beginnormal_vertex>
        float lq1 = cos(position.x * 6.0 + uT * 7.0), lq2 = cos(position.y * 5.0 - uT * 5.0);
        objectNormal = normalize(objectNormal + vec3(-lq1 * 6.0 * uAmp, -lq2 * 3.0 * uAmp, 0.0));`)
      .replace("#include <begin_vertex>", `#include <begin_vertex>
        transformed.z += (sin(position.x * 6.0 + uT * 7.0) + 0.6 * sin(position.y * 5.0 - uT * 5.0)) * uAmp;
        transformed.x += sin(position.y * 7.0 + uT * 6.0) * uAmp * 0.35;`);
  };
  mat.customProgramCacheKey = () => "liquid";
  mat.userData.amp = ua;
  return mat;
}
const M = {
  chrome: () => new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 1, roughness: 0.045 }),
  steel: () => new THREE.MeshPhysicalMaterial({ color: 0x8d929c, metalness: 1, roughness: 0.2 }),
  irid: () => new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 1, roughness: 0.07, iridescence: 1, iridescenceIOR: 1.75, iridescenceThicknessRange: [260, 620] }),
  pink: () => new THREE.MeshPhysicalMaterial({ color: PINK, metalness: 1, roughness: 0.1, clearcoat: 1, clearcoatRoughness: 0.04, emissive: PINK, emissiveIntensity: 0.12 }),
  black: () => new THREE.MeshPhysicalMaterial({ color: 0x050507, metalness: 0.3, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.03 }),
  neon: (k = 1.8, op = 1) => new THREE.MeshBasicMaterial({ color: PINK.clone().multiplyScalar(k), toneMapped: false, transparent: op < 1, opacity: op, fog: false }),
};
function holo() {   // holographic foil: pink → lilac → ice ramp by view angle + position, a light band sweeping across
  return new THREE.ShaderMaterial({
    uniforms: { uT: U.uT, uA: { value: PINK.clone() } },
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      void main(){ vUv = uv; vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz; vN = normalize(mat3(modelMatrix) * normal);
        vV = normalize(cameraPosition - wp.xyz); gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uT; uniform vec3 uA; varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      vec3 ramp(float h){ vec3 p = uA, l = vec3(0.5, 0.3, 1.0), c = vec3(0.9, 0.55, 1.0); h = fract(h) * 3.0;
        return h < 1.0 ? mix(p, l, h) : (h < 2.0 ? mix(l, c, h - 1.0) : mix(c, p, h - 2.0)); }
      void main(){ float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
        float h = f * 1.3 + vUv.x * 0.3 + vUv.y * 0.2 + vW.x * 0.07 + vW.y * 0.05 - uT * 0.16;
        vec3 col = ramp(h) * (0.42 + 0.4 * f);
        float band = 1.0 - smoothstep(0.0, 0.05, abs(fract(vW.x * 0.11 - vW.y * 0.08 - uT * 0.32) - 0.5));
        col += band * vec3(0.7, 0.62, 0.72);
        gl_FragColor = vec4(col, 1.0);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}
function blobMat(base) {    // a sphere that breathes into a liquid blob (normals rebuilt by finite differences)
  const ub = { value: 0.12 };
  base.onBeforeCompile = (sh) => {
    sh.uniforms.uT = U.uT; sh.uniforms.uBlob = ub;
    sh.vertexShader = sh.vertexShader.replace("#include <common>", `#include <common>
      uniform float uT; uniform float uBlob;
      float bf(vec3 p){ return uBlob * (0.55 * sin(2.1 * p.x + uT * 1.3) * sin(1.7 * p.y + uT * 1.1 + 1.0) * sin(1.9 * p.z + uT * 0.9 + 2.0)
                                     + 0.28 * sin(3.6 * p.y + uT * 1.7 + p.x * 1.3) + 0.18 * sin(4.4 * p.z - uT * 1.2 + p.y)); }
      vec3 bp(vec3 n){ return n * (1.0 + bf(n * 1.6)); }`)
      .replace("#include <beginnormal_vertex>", `#include <beginnormal_vertex>
        vec3 bn0 = normalize(position);
        vec3 bt = normalize(cross(bn0, abs(bn0.y) < 0.99 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0)));
        vec3 bb = cross(bn0, bt);
        vec3 q0 = bp(bn0), q1 = bp(normalize(bn0 + bt * 0.01)), q2 = bp(normalize(bn0 + bb * 0.01));
        objectNormal = normalize(cross(q1 - q0, q2 - q0));`)
      .replace("#include <begin_vertex>", "vec3 transformed = bp(normalize(position)) * length(position);");
  };
  base.customProgramCacheKey = () => "blob";
  base.userData.blob = ub;
  return base;
}

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
  // winding differs between fonts: the largest contour is always an outer one
  let big = null, ba = 0;
  for (const s of sp.subPaths) { const pts = s.getPoints(); const a = Math.abs(THREE.ShapeUtils.area(pts)); if (a > ba) { ba = a; big = pts; } }
  const shapes = sp.toShapes(big ? !THREE.ShapeUtils.isClockWise(big) : false);
  const geo = new THREE.ExtrudeGeometry(shapes, { depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.8, bevelSegments: 4, curveSegments: 7 });
  geo.computeBoundingBox();
  return (geoCache[k] = geo);
}
function glyphPivot(ch, depth, bevel, mat, cy) {
  const g = GLYPHS[ch], piv = new THREE.Group();
  const m = new THREE.Mesh(glyphGeo(ch, depth, bevel), mat);
  m.position.set(-g.a / 2, -cy, -depth / 2);
  piv.add(m); piv.userData.a = g.a;
  return piv;
}
function vExtent(str, depth, bevel) {
  let y0 = Infinity, y1 = -Infinity;
  for (const ch of str) { if (!GLYPHS[ch]) continue; const bb = glyphGeo(ch, depth, bevel).boundingBox; y0 = Math.min(y0, bb.min.y); y1 = Math.max(y1, bb.max.y); }
  return y0 === Infinity ? [0, 0.7] : [y0, y1];
}
// a word = one pivot group per glyph (glyphs move on their own); 1 unit = 1 em before scaling
function word(str, { depth = 0.26, bevel = 0.022, mat = M.chrome(), track = -0.012 } = {}) {
  const grp = new THREE.Group(); const glyphs = [];
  const [y0, y1] = vExtent(str, depth, bevel), cy = (y0 + y1) / 2;
  let x = 0;
  for (const ch of str) {
    if (ch === " ") { x += 0.3; continue; }
    if (!GLYPHS[ch]) continue;
    const piv = glyphPivot(ch, depth, bevel, mat, cy);
    piv.position.x = x + GLYPHS[ch].a / 2; grp.add(piv); glyphs.push(piv);
    x += GLYPHS[ch].a + track;
  }
  x = Math.max(0.01, x - track);
  glyphs.forEach((p) => (p.position.x -= x / 2));
  grp.userData = { glyphs, w: x, h: Math.max(0.01, y1 - y0), mat };
  return grp;
}
function fitTo(grp, mw, mh) { const s = Math.min(mw / grp.userData.w, mh / grp.userData.h); grp.scale.setScalar(s); grp.userData.s = s; return s; }
// a counting number: every slot holds one pivot per possible glyph, the visible ones are re-laid out each frame
const ticks = [];
function counter3d({ from = 0, to, dec = 0, pre = "", suf = "" }, { depth = 0.26, bevel = 0.022, mat = M.chrome(), track = -0.012 } = {}) {
  const fmt = (v) => pre + Math.max(0, v).toFixed(dec) + suf;
  const tmpl = fmt(to), alpha = [...new Set((tmpl + "0123456789").split(""))].filter((ch) => GLYPHS[ch]);
  const [y0, y1] = vExtent(tmpl, depth, bevel), cy = (y0 + y1) / 2;
  const grp = new THREE.Group(), slots = [];
  for (let i = 0; i < tmpl.length; i++) {
    const m = {}; for (const ch of alpha) { const p = glyphPivot(ch, depth, bevel, mat, cy); p.visible = false; grp.add(p); m[ch] = p; }
    slots.push(m);
  }
  let w = 0; for (const ch of tmpl) if (GLYPHS[ch]) w += GLYPHS[ch].a + track;
  const st = { v: from };
  const show = () => {
    const s = fmt(st.v); let x = 0; const used = [];
    for (let i = 0; i < s.length && i < slots.length; i++) { const g = GLYPHS[s[i]]; if (!g) continue; used.push([i, s[i], x + g.a / 2]); x += g.a + track; }
    for (const m of slots) for (const k in m) m[k].visible = false;
    for (const [i, ch, cx] of used) { const p = slots[i][ch]; if (p) { p.visible = true; p.position.x = cx - (x - track) / 2; } }
  };
  show(); ticks.push(show);
  grp.userData = { st, w: Math.max(0.01, w - track), h: y1 - y0, mat };
  return grp;
}

// ---------- sprites: star glints and twinkles
const starTex = (() => {
  const c = document.createElement("canvas"); c.width = c.height = 128; const g = c.getContext("2d");
  const rg = g.createRadialGradient(64, 64, 0, 64, 64, 30); rg.addColorStop(0, "rgba(255,255,255,1)"); rg.addColorStop(0.25, "rgba(255,235,250,.55)"); rg.addColorStop(1, "rgba(255,200,240,0)");
  g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
  for (const [w, len, a] of [[3, 62, 0], [3, 62, Math.PI / 2], [1.6, 30, Math.PI / 4], [1.6, 30, -Math.PI / 4]]) {
    g.save(); g.translate(64, 64); g.rotate(a);
    const lg = g.createLinearGradient(-len, 0, len, 0); lg.addColorStop(0, "rgba(255,255,255,0)"); lg.addColorStop(0.5, "rgba(255,255,255,1)"); lg.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = lg; g.beginPath(); g.moveTo(-len, 0); g.lineTo(0, -w); g.lineTo(len, 0); g.lineTo(0, w); g.closePath(); g.fill(); g.restore();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
function sprite(size = 1, tint = 1) {
  const m = new THREE.SpriteMaterial({ map: starTex, color: new THREE.Color(1, 1, 1).multiplyScalar(2.2 * tint), blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, toneMapped: false, fog: false });
  const s = new THREE.Sprite(m); s.scale.setScalar(size); return s;
}
function glint(parent, x, y, z, t0, size = 1) {
  const s = sprite(0.001); s.position.set(x, y, z); parent.add(s);
  tl.fromTo(s.scale, { x: 0.001, y: 0.001 }, { x: size, y: size, duration: 0.14, ease: "power2.out" }, t0);
  tl.to(s.scale, { x: 0.001, y: 0.001, duration: 0.5, ease: "power2.in" }, t0 + 0.14);
  tl.fromTo(s.material, { rotation: 0 }, { rotation: 1.4, duration: 0.64, ease: "none" }, t0);
  return s;
}
function twinkles(parent, n, bw, bh, z0 = -4, z1 = 1.5, size = 0.5) {
  for (let i = 0; i < n; i++) {
    const s = sprite(0.001, R(0.6, 1.1)); s.position.set(R(-bw, bw), R(-bh, bh), R(z0, z1)); parent.add(s);
    const w = R(1.1, 2.6), ph = R(0, 6.28), sz = size * R(0.5, 1.2);
    ticks.push((t) => { const k = Math.pow(Math.max(0, Math.sin(t * w + ph)), 14); s.scale.setScalar(0.001 + sz * k); s.material.rotation = t * 0.6 + ph; });
  }
}

// ---------- ambient Y2K objects (chrome sparkle stars, iridescent rings, pink capsules) at the frame edges
const sparkGeo = (() => {
  const s = new THREE.Shape(); s.moveTo(0, 1); s.quadraticCurveTo(0.08, 0.08, 1, 0); s.quadraticCurveTo(0.08, -0.08, 0, -1); s.quadraticCurveTo(-0.08, -0.08, -1, 0); s.quadraticCurveTo(-0.08, 0.08, 0, 1);
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.16, bevelEnabled: true, bevelThickness: 0.07, bevelSize: 0.05, bevelSegments: 4, curveSegments: 16 }); g.center(); return g;
})();
const SHAPES = [
  () => new THREE.Mesh(sparkGeo, M.chrome()),
  () => new THREE.Mesh(new THREE.TorusGeometry(1, 0.34, 32, 80), M.irid()),
  () => new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), M.chrome()),
  () => new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 1.0, 8, 24), M.pink()),
  () => new THREE.Mesh(sparkGeo, M.irid()),
];
function floaters(parent, F, t0, n = 3, seed = 0) {
  for (let i = 0; i < n; i++) {
    const m = SHAPES[(seed + i) % SHAPES.length]();
    const side = i % 2 ? 1 : -1;
    const x = side * F.uw * R(0.46, 0.6), y = (i % 3 - 1) * F.uh * R(0.32, 0.5) + R(-0.3, 0.3), z = R(-3.2, -0.8);
    const sc = Math.min(F.uw, F.uh) * R(0.045, 0.075);
    m.position.set(x, y, z); m.scale.setScalar(sc); parent.add(m);
    const w = R(0.4, 0.9) * (rnd() < 0.5 ? -1 : 1), ph = R(0, 6.28);
    ticks.push((t) => { m.rotation.set(t * w * 0.7 + ph, t * w + ph, t * 0.25); m.position.y = y + Math.sin(t * 0.9 + ph) * 0.18; });
    tl.from(m.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.6, ease: "back.out(2)" }, Math.max(0, t0 - 0.4) + i * 0.08);
  }
}
function haze(parent, w, h, z = -9, op = 0.38, beat = null) {   // soft pink-violet glow card behind a subject; only lit while its station is on screen
  const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
  const rg = g.createRadialGradient(128, 128, 0, 128, 128, 128); rg.addColorStop(0, "rgba(255,62,200,.55)"); rg.addColorStop(0.4, "rgba(120,60,200,.22)"); rg.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = rg; g.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false, fog: false }));
  m.position.z = z; parent.add(m);
  if (beat) ticks.push((t) => { const k = clamp01((t - beat.ta + 0.3) / 0.3) * clamp01((beat.t + beat.d - ARR - FLY - 0.05 - t) / 0.15); m.material.opacity = op * k; m.visible = k > 0; });
  return m;
}
function shockRing(parent, t0, r1, y = 0, z = 0.2, flat = false) {
  const m = new THREE.Mesh(new THREE.TorusGeometry(1, 0.012, 8, 160), M.neon(2.2, 1)); m.material.transparent = true;
  m.position.set(0, y, z); if (flat) m.rotation.x = Math.PI / 2; parent.add(m);
  tl.fromTo(m.scale, { x: 0.05, y: 0.05, z: 0.05 }, { x: r1, y: r1, z: r1, duration: 0.75, ease: "expo.out" }, t0);
  tl.fromTo(m.material, { opacity: 0 }, { opacity: 1, duration: 0.02 }, t0);
  tl.to(m.material, { opacity: 0, duration: 0.55, ease: "power2.in" }, t0 + 0.2);
  return m;
}

// ---------- timeline (driven by seek; never by a clock)
const tl = gsap["timeline"]({ paused: true });
const impacts = [];       // [time, amplitude] camera kicks
const caKicks = [];

// ---------- stations: camera orbit per kind; separate framing for 9:16
const STN = {
  hero:     { L: { r: [11.6, 10.4], az: [-0.22, 0.2], el: [0.1, 0.03] },     P: { r: [13.6, 12.3], az: [-0.2, 0.18], el: [0.1, 0.03] } },
  bars:     { L: { r: [12.6, 11.8], az: [0.4, -0.12], el: [-0.05, 0.14] },   P: { r: [15.0, 14.0], az: [0.32, -0.1], el: [-0.03, 0.12] } },
  multiple: { L: { r: [12.4, 9.8], az: [0.16, -0.1], el: [0.05, 0.0] },      P: { r: [14.4, 11.8], az: [0.14, -0.08], el: [0.05, 0.0] } },
  coins:    { L: { r: [12.8, 11.9], az: [-0.17, 0.14], el: [0.07, 0.02] },   P: { r: [15.2, 14.3], az: [-0.15, 0.12], el: [0.07, 0.02] } },
  moat:     { L: { r: [12.2, 11.0], az: [-0.45, 0.16], el: [0.66, 0.3] },    P: { r: [14.8, 13.4], az: [-0.4, 0.12], el: [0.66, 0.3] } },
  swarm:    { L: { r: [12.6, 11.6], az: [0.32, -0.18], el: [0.22, 0.07] },   P: { r: [14.8, 13.8], az: [0.3, -0.15], el: [0.2, 0.06] } },
  shovel:   { L: { r: [12.0, 11.0], az: [0.24, -0.16], el: [0.05, 0.1] },    P: { r: [14.4, 13.4], az: [0.2, -0.14], el: [0.05, 0.1] } },
  outro:    { L: { r: [11.0, 10.0], az: [-0.2, 0.16], el: [0.12, 0.04] },    P: { r: [13.2, 12.2], az: [-0.18, 0.14], el: [0.12, 0.04] } },
};
const stnOf = (kind) => (STN[kind] || STN.hero)[P ? "P" : "L"];
function frameOf(kind) {
  const s = stnOf(kind), rm = (s.r[0] + s.r[1]) / 2;
  const fh = 2 * rm * Math.tan((FOV * Math.PI) / 360), fw = (fh * W) / H;
  return { fw, fh, uw: fw * (P ? 0.86 : 0.84), uh: fh * (P ? 0.44 : 0.6) };
}
const origin = (i) => new THREE.Vector3(Math.sin(i * 1.7) * 9, 0, -i * 34);

// ================================================================ station builders
const B = {};

B.hero = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004);
  const tx = word(c.value, { depth: 0.3, bevel: 0.026, mat });
  fitTo(tx, F.uw * 0.86, F.uh * 0.5); G.add(tx);
  const s = tx.userData.s, tw = tx.userData.w * s, th = tx.userData.h * s;
  const tE = c.enter != null && c.enter > c.t + 0.01 ? c.enter : pre(c, 0.3);
  tx.userData.glyphs.forEach((p, j) => {
    const t0 = tE + 0.02 + j * 0.055, y0 = p.position.y;
    tl.from(p.position, { z: 7, y: y0 + R(-1.4, 1.4), duration: 0.9, ease: "expo.out" }, t0);
    tl.from(p.rotation, { y: (j % 2 ? 1 : -1) * Math.PI, x: R(-0.8, 0.8), duration: 1.0, ease: "expo.out" }, t0);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.5, ease: "power3.out" }, t0);
  });
  tl.fromTo(mat.userData.amp, { value: 0.09 }, { value: 0.004, duration: 1.8, ease: "power2.out" }, tE);
  ticks.push((t) => { tx.rotation.y = 0.12 * Math.sin((t - c.t) * 0.8); tx.rotation.x = 0.04 * Math.sin((t - c.t) * 0.6); });
  // punch on the cue: bump + liquid splash + glints + neon underline + camera kick
  tl.fromTo(tx.scale, { x: s * 1.1, y: s * 1.1, z: s * 1.1 }, { x: s, y: s, z: s, duration: 0.6, ease: "elastic.out(1, 0.45)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.05 }, { value: 0.004, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at);
  glint(G, tw * 0.46, th * 0.42, 0.4, c.at + 0.05, th * 0.9);
  glint(G, -tw * 0.38, -th * 0.4, 0.4, c.at + 0.22, th * 0.6);
  const ul = new THREE.Mesh(new THREE.BoxGeometry(tw, Math.max(0.03, th * 0.035), 0.03), M.neon(2));
  ul.position.set(0, -th * 0.62, 0.2); G.add(ul);
  tl.from(ul.scale, { x: 0.001, duration: 0.6, ease: "expo.out" }, c.at);
  impacts.push([c.at, 0.12]); caKicks.push(c.at);
  haze(G, F.fw * 1.4, F.fw * 1.0, -8, 0.32, c);
  if (c.deco === "blob") {
    const bl = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 48), blobMat(M.irid()));
    const br = Math.max(th * 0.95, Math.min(F.uh * 0.5, tw * 0.42));
    bl.position.set(tw * 0.18, 0, -2.8); bl.scale.setScalar(br); G.add(bl);
    tl.from(bl.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 1.0, ease: "expo.out" }, pre(c, 0.38));
    tl.fromTo(bl.material.userData.blob, { value: 0.1 }, { value: 0.34, duration: 0.25, ease: "power2.out", immediateRender: false }, c.at);
    tl.to(bl.material.userData.blob, { value: 0.14, duration: 1.4, ease: "power2.out" }, c.at + 0.25);
    ticks.push((t) => { bl.rotation.set(t * 0.2, t * 0.3, 0); });
    shockRing(G, c.at, Math.max(tw, th) * 0.95);
    shockRing(G, c.at + 0.1, Math.max(tw, th) * 1.3);
    const orb = new THREE.Mesh(new THREE.TorusGeometry(1, 0.01, 8, 200), M.neon(2.2));
    orb.scale.setScalar(Math.max(tw * 0.62, th)); orb.position.z = -0.6; G.add(orb);
    ticks.push((t) => { orb.rotation.set(1.25, 0.3 * Math.sin(t * 0.7), t * 0.5); });
    tl.from(orb.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.9, ease: "expo.out" }, c.at - 0.2);
  } else {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1, 0.05, 48, 240), M.irid());
    ring.scale.setScalar(Math.max(tw * 0.68, th * 1.7)); ring.position.z = -4.2; G.add(ring);
    ticks.push((t) => { ring.rotation.set(1.12 + 0.14 * Math.sin(t * 0.7), 0.28 * Math.sin(t * 0.5), t * 0.35); });
    tl.fromTo(ring.scale, { x: 0.3, y: 0.3, z: 0.3 }, { x: ring.scale.x, y: ring.scale.x, z: ring.scale.x, duration: 1.3, ease: "expo.out" }, pre(c, 0.35));
    for (let k = 0; k < 3; k++) {
      const b = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), k === 1 ? M.pink() : M.chrome()); b.scale.setScalar(0.07); ring.add(b);
      ticks.push((t) => { const a = t * 0.9 + k * 2.1; b.position.set(Math.cos(a), Math.sin(a), 0); });
    }
    shockRing(G, c.at, Math.max(tw, th) * 0.9);
  }
  twinkles(G, 14, F.uw * 0.6, F.uh * 0.7, -4, 1.2, Math.min(F.uw, F.uh) * 0.07);
  floaters(G, F, c.t, 3, i);
  return {};
};

B.bars = (c, G, F, i) => {
  const n = c.items.length, vals = c.items.map((x) => x[1]), maxv = Math.max(...vals, 1e-6);
  const Hmax = F.uh * (P ? 0.6 : 0.56);
  const bw = Math.min((F.uw * 0.74) / (n + (n - 1) * 0.5), Hmax * 0.42), gap = bw * 0.5;
  const total = n * bw + (n - 1) * gap, base = -Hmax * 0.62;
  const plate = new THREE.Mesh(new RoundedBoxGeometry(total + bw * 0.9, bw * 0.14, bw * 1.6, 3, bw * 0.05), M.black());
  plate.position.set(0, base - bw * 0.07, 0); G.add(plate);
  tl.from(plate.scale, { x: 0.001, duration: 0.5, ease: "expo.out" }, pre(c, 0.42));
  const labMat = M.chrome(), valMat = M.chrome();
  const grow = [];
  c.items.forEach(([lab, v], j) => {
    const last = j === n - 1, h = Math.max(bw * 0.12, (v / maxv) * Hmax);
    const geo = new RoundedBoxGeometry(bw, h, bw, 4, Math.min(bw * 0.12, h * 0.45)); geo.translate(0, h / 2, 0);
    const mesh = new THREE.Mesh(geo, last ? M.irid() : j === n - 2 ? M.chrome() : M.steel());
    const x = -total / 2 + bw / 2 + j * (bw + gap); mesh.position.set(x, base, 0); G.add(mesh);
    const t0 = last ? c.at_v - 0.55 : Math.min(c.at, pre(c, 0.4)) + j * 0.16, dur = last ? 1.3 : 0.6;
    tl.from(mesh.scale, { y: 0.001, duration: dur, ease: last ? "power3.out" : "expo.out" }, t0);
    grow.push(t0);
    const lb = word(lab, { depth: 0.08, bevel: 0.008, mat: labMat }); fitTo(lb, bw * 1.25, bw * 0.34);
    lb.position.set(x, base - bw * 0.42, bw * 0.95); G.add(lb);
    const tl0 = Math.min(c.at - 0.1, pre(c, 0.38)) + j * 0.05;
    tl.from(lb.position, { y: base - bw * 1.2, duration: 0.5, ease: "expo.out" }, tl0);
    tl.from(lb.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(2)" }, tl0);
    if (!last) {
      const vl = word(v.toFixed(c.dec), { depth: 0.1, bevel: 0.01, mat: valMat }); fitTo(vl, bw * 1.2, bw * 0.36);
      vl.position.set(x, base + h + bw * 0.34, 0); G.add(vl);
      tl.from(vl.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.45, ease: "back.out(2.2)" }, t0 + dur * 0.55);
    } else {
      const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), new THREE.LineBasicMaterial({ color: PINK.clone().multiplyScalar(2.2), toneMapped: false, fog: false }));
      mesh.add(edges);
      const ctr = counter3d({ from: 0, to: v, dec: c.dec, pre: c.pre, suf: c.suf }, { depth: 0.26, bevel: 0.022, mat: liquid(M.chrome(), 0.006) });
      fitTo(ctr, Math.min(F.uw * 0.5, total * 0.9), bw * 0.9);
      const cw = ctr.userData.w * ctr.userData.s, chh = ctr.userData.h * ctr.userData.s;
      const cx = Math.min(x, F.uw / 2 - cw / 2);
      ctr.position.set(cx, base + h + chh * 0.5 + bw * 0.3, 0.2); G.add(ctr);
      tl.fromTo(ctr.userData.st, { v: 0 }, { v, duration: dur, ease: "power3.out" }, t0);
      tl.from(ctr.position, { y: base + bw * 0.5, duration: dur, ease: "power3.out" }, t0);
      tl.from(ctr.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.35, ease: "back.out(2)" }, t0);
      glint(G, cx + cw * 0.45, base + h + chh * 0.9 + bw * 0.3, 0.5, t0 + dur - 0.1, chh * 1.2);
      impacts.push([c.at_v, 0.08]); caKicks.push(c.at_v);
      const scan = new THREE.Mesh(new THREE.BoxGeometry(bw * 1.1, Math.max(0.02, bw * 0.025), bw * 1.1), M.neon(2.4, 0.9));
      scan.position.set(x, base, 0); G.add(scan);
      ticks.push((t) => { const k = t - (t0 + dur); scan.visible = k > 0; if (k > 0) scan.position.y = base + ((k * 0.7) % 1) * h; });
    }
  });
  haze(G, F.fw * 1.3, F.fw * 0.9, -9, 0.26, c);
  twinkles(G, 12, F.uw * 0.6, F.uh * 0.7, -4, 1, Math.min(F.uw, F.uh) * 0.06);
  floaters(G, F, c.t, 2, i);
  return {};
};

B.multiple = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004); mat.emissive = PINK.clone(); mat.emissiveIntensity = 0;
  const tx = word(c.value, { depth: 0.34, bevel: 0.028, mat });
  fitTo(tx, F.uw * 0.9, F.uh * 0.56); G.add(tx);
  const s = tx.userData.s, tw = tx.userData.w * s, th = tx.userData.h * s;
  tl.from(tx.position, { z: -16, duration: 0.6, ease: "expo.out" }, pre(c, 0.4));
  tx.userData.glyphs.forEach((p, j) => {
    tl.from(p.rotation, { x: -Math.PI / 2, duration: 0.6, ease: "back.out(1.4)" }, pre(c, 0.32) + j * 0.04);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.4, ease: "power3.out" }, pre(c, 0.32) + j * 0.04);
  });
  tl.fromTo(mat, { emissiveIntensity: 0.8 }, { emissiveIntensity: 0, duration: 0.55, ease: "power2.out", immediateRender: false }, c.at);
  tl.fromTo(tx.scale, { x: s * 1.14, y: s * 1.14, z: s * 1.14 }, { x: s, y: s, z: s, duration: 0.7, ease: "elastic.out(1, 0.4)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.07 }, { value: 0.004, duration: 1.0, ease: "power2.out", immediateRender: false }, c.at);
  ticks.push((t) => { tx.rotation.y = 0.1 * Math.sin((t - c.t) * 1.1); });
  shockRing(G, c.at, Math.max(tw, th) * 0.8); shockRing(G, c.at + 0.08, Math.max(tw, th) * 1.15);
  impacts.push([c.at, 0.16]); caKicks.push(c.at);
  for (let k = 0; k < 12; k++) {    // sparkle burst
    const a = (k / 12) * Math.PI * 2 + 0.2, sp = sprite(0.001); G.add(sp);
    const r1 = Math.max(tw, th) * R(0.5, 0.8);
    tl.fromTo(sp.position, { x: 0, y: 0, z: 0.5 }, { x: Math.cos(a) * r1, y: Math.sin(a) * r1 * 0.7, z: 0.5, duration: 0.7, ease: "expo.out" }, c.at);
    tl.fromTo(sp.scale, { x: 0.001, y: 0.001 }, { x: th * 0.5, y: th * 0.5, duration: 0.12 }, c.at);
    tl.to(sp.scale, { x: 0.001, y: 0.001, duration: 0.5, ease: "power2.in" }, c.at + 0.25);
  }
  // speed streaks rushing past the camera for the whole beat
  const streaks = [];
  for (let k = 0; k < 70; k++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.018, R(1.2, 2.6)), k % 7 === 0 ? M.neon(2) : new THREE.MeshBasicMaterial({ color: 0xc9ccd6, fog: false }));
    const a = R(0, Math.PI * 2), r = R(2.2, 8); m.userData = { x: Math.cos(a) * r * (W / H > 1 ? 1.6 : 0.8), y: Math.sin(a) * r, z0: R(0, 44), v: R(26, 40) };
    G.add(m); streaks.push(m);
  }
  ticks.push((t) => {
    const k = t - c.t, on = k > -0.4 && k < c.d + 0.2;
    for (const m of streaks) { m.visible = on; if (!on) continue; const u = m.userData; m.position.set(u.x, u.y, ((u.z0 + (k + 0.4) * u.v) % 44) - 32); }
  });
  haze(G, F.fw * 1.4, F.fw, -8, 0.4, c);
  floaters(G, F, c.t, 2, i + 1);
  return {};
};

B.coins = (c, G, F, i) => {
  const N = c.n, cols = Math.ceil(Math.sqrt(N)), rows = Math.ceil(N / cols);
  const gw = P ? F.uw * 0.84 : F.uw * 0.46, gh = P ? F.uh * 0.56 : F.uh * 0.74;
  const pitch = Math.min(gw / cols, gh / rows), cr = pitch * 0.43;
  const gx = P ? 0 : -F.uw * 0.2, gy = P ? F.uh * 0.2 : -F.uh * 0.05;
  const geo = new THREE.CylinderGeometry(cr, cr, cr * 0.2, 44, 1); geo.rotateX(Math.PI / 2);
  const mats = [M.steel(), M.chrome(), holo()];
  const coins = [];
  for (let j = 0; j < N; j++) {
    const r = Math.floor(j / cols), col = j % cols;
    const m = new THREE.Mesh(geo, mats);
    m.position.set(gx + (col - (cols - 1) / 2) * pitch, gy + ((rows - 1) / 2 - r) * pitch, 0); G.add(m); coins.push(m);
    const ta = Math.min(c.at_show - 0.25, pre(c, 0.36)) + (r + col) * 0.012;
    tl.from(m.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(2)" }, ta);
    tl.from(m.rotation, { y: -Math.PI / 2, duration: 0.55, ease: "expo.out" }, ta);
    if (j < c.hit) tl.to(m.rotation, { y: Math.PI, duration: 0.5, ease: "power2.inOut" }, c.at_hit + (j / Math.max(1, c.hit)) * 0.9);
  }
  const zs = coins.map((m) => m.position.z);
  ticks.push((t) => coins.forEach((m, j) => { m.position.z = zs[j] + Math.sin(t * 2.2 + j * 0.37) * cr * 0.3; m.rotation.x = Math.sin(t * 1.6 + j * 0.21) * 0.14; }));
  const ctr = counter3d({ from: 0, to: c.to, dec: c.dec, pre: c.pre, suf: c.suf }, { depth: 0.3, bevel: 0.026, mat: liquid(M.chrome(), 0.006) });
  fitTo(ctr, P ? F.uw * 0.6 : F.uw * 0.36, P ? F.uh * 0.24 : F.uh * 0.42);
  ctr.position.set(P ? 0 : F.uw * 0.27, P ? -F.uh * 0.27 : 0, 0.3); G.add(ctr);
  tl.from(ctr.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(1.8)" }, pre(c, 0.25));
  tl.fromTo(ctr.userData.st, { v: 0 }, { v: c.to, duration: 1.3, ease: "power2.out" }, c.at_hit);
  const cw = ctr.userData.w * ctr.userData.s, ch = ctr.userData.h * ctr.userData.s;
  glint(G, ctr.position.x + cw * 0.42, ctr.position.y + ch * 0.4, 0.6, c.at_hit + 1.25, ch * 0.8);
  impacts.push([c.at_hit + 1.2, 0.06]);
  ticks.push((t) => { ctr.rotation.y = 0.14 * Math.sin((t - c.t) * 0.9); });
  twinkles(G, 10, F.uw * 0.6, F.uh * 0.7, -4, 1, Math.min(F.uw, F.uh) * 0.05);
  floaters(G, F, c.t, 2, i + 2);
  return {};
};

B.moat = (c, G, F, i) => {
  const sc = Math.min(1, (F.uw * 0.32) / 2.0, (F.uh * 0.5) / 2.0) * 1.15;
  const isle = new THREE.Group(); isle.scale.setScalar(sc); G.add(isle);
  const chip = new THREE.Group(); isle.add(chip);
  chip.add(new THREE.Mesh(new RoundedBoxGeometry(2.0, 0.26, 2.0, 4, 0.06), M.black()));
  const lidMat = M.chrome();
  const lid = new THREE.Mesh(new RoundedBoxGeometry(1.25, 0.08, 1.25, 3, 0.03), lidMat); lid.position.y = 0.16; chip.add(lid);
  const pinGeo = new THREE.BoxGeometry(0.09, 0.05, 0.24), pinMat = M.chrome();
  for (let s = 0; s < 4; s++) for (let k = 0; k < 7; k++) {
    const p = new THREE.Mesh(pinGeo, pinMat), o = (k - 3) * 0.24;
    if (s === 0) p.position.set(o, -0.06, 1.08); else if (s === 1) p.position.set(o, -0.06, -1.08);
    else { p.rotation.y = Math.PI / 2; p.position.set(s === 2 ? 1.08 : -1.08, -0.06, o); }
    chip.add(p);
  }
  const lab = word(c.chip, { depth: 0.04, bevel: 0.004, mat: M.neon(1.6) }); fitTo(lab, 0.95, 0.4);
  lab.rotation.x = -Math.PI / 2; lab.position.y = 0.215; chip.add(lab);
  tl.from(chip.position, { y: 3.0, duration: 0.7, ease: "bounce.out" }, pre(c, 0.4));
  tl.from(chip.rotation, { y: -1.4, duration: 0.8, ease: "expo.out" }, pre(c, 0.4));
  ticks.push((t) => { if (t < c.at_chip) chip.rotation.z = 0; else { const k = t - c.at_chip; chip.position.x = k < 0.45 ? Math.sin(k * 90) * 0.05 * (1 - k / 0.45) : 0; } });
  // the moat
  const ringMat = liquid(M.irid(), 0.01);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.3, 0.2, 40, 220), ringMat); ring.rotation.x = Math.PI / 2; isle.add(ring);
  const water = new THREE.Mesh(new THREE.CircleGeometry(2.2, 96), M.black()); water.rotation.x = -Math.PI / 2; water.position.y = -0.16; isle.add(water);
  tl.from(ring.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.9, ease: "elastic.out(1, 0.6)" }, c.at_moat - 0.1);
  tl.from(water.scale, { x: 0.001, y: 0.001, duration: 0.7, ease: "expo.out" }, c.at_moat);
  ticks.push((t) => { ring.rotation.z = t * 0.5; });
  tl.fromTo(ringMat.userData.amp, { value: 0.06 }, { value: 0.012, duration: 1.4, ease: "power2.out", immediateRender: false }, c.at_moat);
  // "not the chip": a neon X stamps on it, then it sinks
  const X = new THREE.Group(); X.position.y = 0.5; isle.add(X);
  for (const a of [Math.PI / 4, -Math.PI / 4]) { const bar = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.06, 0.2), M.neon(2.4)); bar.rotation.y = a; X.add(bar); }
  tl.fromTo(X.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: 1, y: 1, z: 1, duration: 0.3, ease: "back.out(3)" }, c.at_chip);
  tl.to(lidMat.color, { r: 0.25, g: 0.25, b: 0.28, duration: 0.3 }, c.at_chip);
  const sink = Math.min(c.at_chip + 0.55, c.at_word - 0.35);
  tl.to(chip.position, { y: -7, duration: 0.55, ease: "power3.in" }, sink);
  ticks.push((t) => { chip.visible = t < sink + 0.6; X.visible = t < sink + 0.5; });
  tl.to(X.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.3, ease: "power2.in" }, sink + 0.15);
  impacts.push([c.at_chip, 0.08]); caKicks.push(c.at_chip);
  // the real moat rises out of the ring
  const wm = liquid(M.irid(), 0.004);
  const tx = word(c.word, { depth: 0.3, bevel: 0.026, mat: wm }); fitTo(tx, F.uw * 0.5, F.uh * 0.4);
  const th = tx.userData.h * tx.userData.s, tw = tx.userData.w * tx.userData.s;
  const ty = th * 0.5 + 0.25 * sc;
  tx.position.set(0, ty, 0.1 * sc); tx.rotation.x = -0.18; G.add(tx);
  tl.fromTo(tx.position, { y: -th * 1.4 }, { y: ty, duration: 0.8, ease: "back.out(1.5)" }, c.at_word);
  tl.from(tx.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.45, ease: "power3.out" }, c.at_word);
  tl.fromTo(wm.userData.amp, { value: 0.09 }, { value: 0.004, duration: 1.6, ease: "power2.out", immediateRender: false }, c.at_word);
  ticks.push((t) => { tx.rotation.y = 0.16 * Math.sin((t - c.at_word) * 0.9); });
  const inner = new THREE.Mesh(new THREE.TorusGeometry(1.95, 0.02, 8, 200), M.neon(2.4)); inner.rotation.x = Math.PI / 2; inner.position.y = 0.02; isle.add(inner);
  tl.from(inner.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.7, ease: "expo.out" }, c.at_word + 0.1);
  shockRing(isle, c.at_word + 0.1, 3.4, 0.05, 0, true);
  glint(G, tw * 0.45, ty + th * 0.45, 0.6, c.at_word + 0.55, th * 0.9);
  glint(G, -tw * 0.4, ty - th * 0.3, 0.6, c.at_word + 0.75, th * 0.6);
  impacts.push([c.at_word + 0.2, 0.1]); caKicks.push(c.at_word + 0.2);
  twinkles(G, 12, F.uw * 0.6, F.uh * 0.8, -4, 1, Math.min(F.uw, F.uh) * 0.06);
  floaters(G, F, c.t, 2, i + 3);
  return { ly: 0.25 * sc };
};

B.swarm = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004);
  const tx = word(c.value, { depth: 0.3, bevel: 0.026, mat });
  fitTo(tx, P ? F.uw * 0.74 : F.uw * 0.46, P ? F.uh * 0.3 : F.uh * 0.5); G.add(tx);
  const tw = tx.userData.w * tx.userData.s, th = tx.userData.h * tx.userData.s;
  tx.userData.glyphs.forEach((p, j) => {
    tl.from(p.rotation, { x: Math.PI / 2, duration: 0.6, ease: "back.out(1.5)" }, pre(c, 0.32) + j * 0.05);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.4, ease: "power3.out" }, pre(c, 0.32) + j * 0.05);
  });
  tl.fromTo(tx.scale, { x: tx.userData.s * 1.1, y: tx.userData.s * 1.1, z: tx.userData.s * 1.1 }, { x: tx.userData.s, y: tx.userData.s, z: tx.userData.s, duration: 0.6, ease: "elastic.out(1, 0.45)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.06 }, { value: 0.004, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at);
  glint(G, tw * 0.46, th * 0.4, 0.5, c.at + 0.1, th * 0.9);
  impacts.push([c.at, 0.08]); caKicks.push(c.at);
  ticks.push((t) => { tx.rotation.y = 0.12 * Math.sin((t - c.t) * 0.8); });
  // the developers: a galaxy of chrome beads (a few pink) orbiting the number
  const N = 900, im = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 2), M.chrome(), N); im.frustumCulled = false;
  const sw = new THREE.Group(); sw.rotation.x = P ? 1.22 : 1.12; sw.rotation.z = -0.12; G.add(sw); sw.add(im);
  const rho0 = Math.max(tw * 0.6, th * 0.9), rho1 = Math.max(rho0 * 1.2, Math.min(P ? F.uw * 0.44 : F.uw * 0.3, rho0 * 2.0));
  const pk = PINK.clone(), wh = new THREE.Color(1, 1, 1);
  const par = [];
  for (let k = 0; k < N; k++) {
    const u = Math.pow(rnd(), 0.8), rho = rho0 + (rho1 - rho0) * u;
    par.push({ rho, a: R(0, Math.PI * 2), w: (0.9 / rho) * R(0.7, 1.3), y: R(-1, 1) * (0.12 + 0.35 * u) * rho0 * 0.5, s: R(0.018, 0.055) * Math.min(F.uw, F.uh) * 0.12 });
    im.setColorAt(k, k % 9 === 0 ? pk : wh);
  }
  im.instanceColor.needsUpdate = true;
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v3 = new THREE.Vector3(), s3 = new THREE.Vector3();
  ticks.push((t) => {
    const k = expoOut(clamp01((t - pre(c, 0.4)) / 1.2)), far = 1 + (1 - k) * 3.2;
    const pulse = 1 + 0.08 * Math.exp(-Math.max(0, t - c.at) * 4) * (t > c.at ? 1 : 0);
    for (let j = 0; j < N; j++) {
      const p = par[j], a = p.a + t * p.w + (1 - k) * 2;
      v3.set(Math.cos(a) * p.rho * far * pulse, Math.sin(a) * p.rho * far * pulse, p.y);
      s3.setScalar(p.s * (0.3 + 0.7 * k)); m4.compose(v3, q, s3); im.setMatrixAt(j, m4);
    }
    im.instanceMatrix.needsUpdate = true;
  });
  twinkles(G, 10, F.uw * 0.6, F.uh * 0.7, -4, 1, Math.min(F.uw, F.uh) * 0.05);
  floaters(G, F, c.t, 2, i + 4);
  return P ? { ly: -F.fh * 0.065 } : { lx: -F.fw * 0.17 };
};

B.shovel = (c, G, F, i) => {
  // the shovel: chrome handle + D-grip, pink chrome blade
  const sh = new THREE.Group(), spin = new THREE.Group(); sh.add(spin);
  const ch = M.chrome();
  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.3, 32), ch); handle.position.y = 0.5; spin.add(handle);
  const grip = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.05, 16, 48, Math.PI), ch); grip.position.y = 1.65; spin.add(grip);
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.5, 24), ch); bar.rotation.z = Math.PI / 2; bar.position.y = 1.65; spin.add(bar);
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.12, 0.34, 32), ch); collar.position.y = -0.78; spin.add(collar);
  const bs = new THREE.Shape(); bs.moveTo(-0.46, 0); bs.lineTo(0.46, 0); bs.lineTo(0.46, -0.78); bs.quadraticCurveTo(0.42, -1.05, 0, -1.25); bs.quadraticCurveTo(-0.42, -1.05, -0.46, -0.78); bs.lineTo(-0.46, 0);
  const bg = new THREE.ExtrudeGeometry(bs, { depth: 0.04, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 4, curveSegments: 24 }); bg.translate(0, 0, -0.02);
  const blade = new THREE.Mesh(bg, M.pink()); blade.position.y = -0.92; spin.add(blade);
  const SH = 4.0, ssc = (P ? F.uh * 0.44 : F.uh * 0.82) / SH;
  sh.scale.setScalar(ssc);
  const sx = P ? 0 : F.uw * 0.3, sy = P ? -F.uh * 0.22 : 0.0;
  sh.position.set(sx, sy, 0); sh.rotation.z = -0.24; G.add(sh);
  tl.from(sh.position, { x: sx + F.uw * 0.9, duration: 0.7, ease: "expo.out" }, pre(c, 0.4));
  tl.from(sh.rotation, { z: 1.3, duration: 0.85, ease: "back.out(1.6)" }, pre(c, 0.4));
  ticks.push((t) => { spin.rotation.y = (t - c.t) * 1.1; });
  tl.to(sh.rotation, { z: 0.15, duration: 0.16, ease: "power2.out" }, c.at_title - 0.05);
  tl.to(sh.rotation, { z: -0.24, duration: 0.5, ease: "back.out(2)" }, c.at_title + 0.11);
  // gold-rush nuggets: chrome (a few pink) raining onto a pile at the blade
  const nugGeo = new THREE.IcosahedronGeometry(1, 0), nm = M.chrome(); nm.flatShading = true;
  const pm = M.pink(); pm.flatShading = true;
  const groundY = sy - 2.1 * ssc;
  for (let k = 0; k < 46; k++) {
    const m = new THREE.Mesh(nugGeo, k % 6 === 0 ? pm : nm);
    const r = ssc * R(0.12, 0.26), x = sx + R(-1.6, 1.6) * ssc * (P ? 1.4 : 1.2), z = R(-0.8, 0.9), y = groundY + R(0, 0.35) * ssc + r;
    m.scale.setScalar(r); m.position.set(x, y, z); G.add(m);
    const t0 = Math.min(c.at_rain, pre(c, 0.3)) + k * 0.025;
    tl.from(m.position, { y: y + R(6, 9), duration: R(0.7, 1.0), ease: "bounce.out" }, t0);
    const w = R(-2, 2), ph = R(0, 6);
    ticks.push((t) => { const kk = clamp01((t - t0) / 1.0); m.rotation.set(ph + w * kk * 3, ph * 0.5 + t * 0.2, w * kk); });
  }
  // two lines of chrome type
  const [l1, l2] = [c.lines[0] || "", c.lines[1] || ""];
  const m1 = liquid(M.chrome(), 0.004), m2 = liquid(M.pink(), 0.004);
  const w1 = word(l1, { depth: 0.3, bevel: 0.024, mat: m1 }), w2 = word(l2, { depth: 0.32, bevel: 0.026, mat: m2 });
  const tw = P ? F.uw * 0.9 : F.uw * 0.52, lh = P ? F.uh * 0.17 : F.uh * 0.24;
  fitTo(w1, tw, lh); fitTo(w2, tw, lh * 1.15);
  const h1 = w1.userData.h * w1.userData.s, h2 = w2.userData.h * w2.userData.s;
  const tx = P ? 0 : -F.uw * 0.2, ty = P ? F.uh * 0.24 : 0.05;
  const gapY = Math.min(h1, h2) * 0.32;
  w1.position.set(tx, ty + (h2 + gapY) / 2, 0.3); w2.position.set(tx, ty - (h1 + gapY) / 2, 0.3); G.add(w1, w2);
  w1.userData.glyphs.forEach((p, j) => {
    tl.from(p.rotation, { x: -Math.PI / 2, duration: 0.6, ease: "back.out(1.6)" }, c.at_title + j * 0.05);
    tl.from(p.position, { y: -0.6, duration: 0.6, ease: "expo.out" }, c.at_title + j * 0.05);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.4, ease: "power3.out" }, c.at_title + j * 0.05);
  });
  const t2 = c.at_line2 || c.at_title + 0.6;
  ticks.push((t) => w2.userData.glyphs.forEach((p, j) => { p.visible = t >= t2 + j * 0.05; }));
  w2.userData.glyphs.forEach((p, j) => {
    tl.from(p.scale, { x: 3, y: 3, z: 3, duration: 0.45, ease: "expo.out" }, t2 + j * 0.05);
    tl.from(p.position, { z: 4, duration: 0.45, ease: "expo.out" }, t2 + j * 0.05);
  });
  tl.fromTo(m2.userData.amp, { value: 0.08 }, { value: 0.004, duration: 1.4, ease: "power2.out", immediateRender: false }, t2);
  tl.fromTo(m1.userData.amp, { value: 0.06 }, { value: 0.004, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at_title);
  impacts.push([c.at_title, 0.08], [t2 + 0.1, 0.12]); caKicks.push(t2 + 0.1);
  const ww2 = w2.userData.w * w2.userData.s;
  glint(G, tx + ww2 * 0.48, w2.position.y + h2 * 0.45, 0.7, t2 + 0.35, h2 * 0.9);
  ticks.push((t) => { w1.rotation.y = w2.rotation.y = 0.08 * Math.sin((t - c.t) * 0.8); });
  haze(G, F.fw * 1.3, F.fw * 0.9, -9, 0.3, c);
  twinkles(G, 12, F.uw * 0.6, F.uh * 0.7, -4, 1, Math.min(F.uw, F.uh) * 0.06);
  floaters(G, F, c.t, 2, i + 1);
  return {};
};

B.outro = (c, G, F, i) => {
  const prof = [[0, 0], [1.05, 0], [1.08, 0.04], [1.02, 0.07], [0.62, 0.08], [0.6, 0.14], [0.58, 1.0], [0.6, 1.05], [0.6, 1.08], [0, 1.08]].map(([x, y]) => new THREE.Vector2(x, y));
  const hat = new THREE.Group(), spin = new THREE.Group(); hat.add(spin);
  const crown = new THREE.Mesh(new THREE.LatheGeometry(prof, 120), liquid(M.chrome(), 0.006)); crown.material.side = THREE.DoubleSide; spin.add(crown);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.606, 0.606, 0.17, 120, 1, true), M.neon(1.9)); band.position.y = 0.24; spin.add(band);
  const nm = liquid(M.chrome(), 0.004);
  const name = word(c.title, { depth: 0.28, bevel: 0.024, mat: nm }); fitTo(name, F.uw * 0.8, F.uh * 0.24);
  const nh = name.userData.h * name.userData.s, nw = name.userData.w * name.userData.s;
  const hs = (P ? F.uh * 0.38 : F.uh * 0.46) / 1.08, hatH = 1.08 * hs, gap = nh * 0.22 + hs * 0.22;
  hat.scale.setScalar(hs);
  const hy = (gap + nh - hatH) / 2;
  hat.position.set(0, hy, -0.4); hat.rotation.x = 0.2; G.add(hat);
  name.position.set(0, hy - gap - nh / 2, 0.6); G.add(name);
  tl.from(hat.position, { y: hy + F.uh * 1.2, duration: 0.9, ease: "bounce.out" }, pre(c, 0.35));
  ticks.push((t) => { spin.rotation.y = (t - c.t) * 1.3 - 1.2; });
  name.userData.glyphs.forEach((p, j) => {
    tl.from(p.position, { y: -1.4, duration: 0.6, ease: "back.out(1.6)" }, c.t + 0.45 + j * 0.07);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.4, ease: "power3.out" }, c.t + 0.45 + j * 0.07);
  });
  tl.fromTo(nm.userData.amp, { value: 0.08 }, { value: 0.004, duration: 1.6, ease: "power2.out", immediateRender: false }, c.t + 0.5);
  impacts.push([c.t + 0.75, 0.1]); caKicks.push(c.t + 0.75);
  glint(G, nw * 0.47, name.position.y + nh * 0.45, 0.9, c.t + 1.2, nh * 0.9);
  glint(G, -hs * 0.9, hy + hs * 0.95, 0.4, c.t + 1.5, nh * 0.6);
  for (let k = 0; k < 4; k++) {     // chrome sparkle stars orbiting the hat
    const st = new THREE.Mesh(sparkGeo, k % 2 ? M.irid() : M.chrome()); st.scale.setScalar(hs * 0.13); G.add(st);
    const ph = (k / 4) * Math.PI * 2;
    ticks.push((t) => { const a = ph + (t - c.t) * 0.9; st.position.set(Math.cos(a) * hs * 1.6, hy + hs * 0.6 + Math.sin(a * 2) * hs * 0.2, Math.sin(a) * hs * 0.9); st.rotation.set(0, a * 2, a); });
    tl.from(st.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.6, ease: "back.out(2)" }, c.t + 0.6 + k * 0.08);
  }
  haze(G, F.fw * 1.4, F.fw, -8, 0.4, c);
  twinkles(G, 16, F.uw * 0.6, F.uh * 0.8, -4, 1.2, Math.min(F.uw, F.uh) * 0.07);
  return P ? { ly: -F.uh * 0.14 } : {};      // 9:16: sit higher, the mascot cameo takes the lower left
};

// ================================================================ assemble
const look = [];
CFG.beats.forEach((c, i) => {
  const G = new THREE.Group(); G.position.copy(origin(i)); scene.add(G);
  const F = frameOf(c.kind);
  const o = (B[c.kind] || B.hero)(c, G, F, i) || {};
  if (i) glint(G, F.uw * (i % 2 ? 0.34 : -0.34), F.uh * 0.3, 0.8, c.ta, Math.min(F.uw, F.uh) * 0.16);   // arrival glint, local
  look.push({ x: G.position.x + (o.lx || 0), y: G.position.y + (o.ly || 0), z: G.position.z });
});

// camera: fly-in, orbit/dolly inside each beat, whip flight with roll to the next station
const cam = { lx: 0, ly: 0, lz: 0, r: 10, az: 0, el: 0, roll: 0 };
const stA = (i) => { const s = stnOf(CFG.beats[i].kind); return { lx: look[i].x, ly: look[i].y, lz: look[i].z, r: s.r[0], az: s.az[0], el: s.el[0] }; };
const stB = (i) => { const s = stnOf(CFG.beats[i].kind); return { lx: look[i].x, ly: look[i].y, lz: look[i].z, r: s.r[1], az: s.az[1], el: s.el[1] }; };
const post = {};
CFG.beats.forEach((c, i) => {
  const a = stA(i), b = stB(i);
  const end = i + 1 < CFG.beats.length ? CFG.beats[i + 1].ta - FLY : D;
  if (i === 0) {
    tl.fromTo(cam, { ...a, r: a.r * 1.8, az: a.az - 0.55, el: a.el + 0.3, roll: -0.12 }, { ...a, roll: 0, duration: 1.1, ease: "expo.out" }, 0);
    tl.fromTo(cam, { ...a }, { ...b, duration: Math.max(0.3, end - 1.1), ease: "sine.inOut", immediateRender: false }, 1.1);
  } else {
    const t0 = c.ta - FLY, rr = (i % 2 ? 1 : -1) * 0.16;
    tl.fromTo(cam, { ...stB(i - 1) }, { ...a, duration: FLY, ease: "expo.inOut", immediateRender: false }, t0);
    tl.fromTo(cam, { roll: 0 }, { roll: rr, duration: FLY / 2, ease: "power2.in", immediateRender: false }, t0);
    tl.fromTo(cam, { roll: rr }, { roll: 0, duration: FLY / 2, ease: "power2.out", immediateRender: false }, t0 + FLY / 2);
    tl.fromTo(cam, { ...a }, { ...b, duration: Math.max(0.2, end - c.ta), ease: "sine.inOut", immediateRender: false }, c.ta);
  }
});

// dolly-through: each whip flight passes through a short tunnel of chrome / neon ring gates with chrome shards whizzing by
// (the gates sit exactly on the camera path; they exist only during that flight)
const camPos = (q) => { const ce = Math.cos(q.el); return new THREE.Vector3(q.lx + q.r * Math.sin(q.az) * ce, q.ly + q.r * Math.sin(q.el), q.lz + q.r * Math.cos(q.az) * ce); };
const lerpSt = (a, b, u) => { const o = {}; for (const k of ["lx", "ly", "lz", "r", "az", "el"]) o[k] = a[k] + (b[k] - a[k]) * u; return o; };
const gateGeo = new THREE.TorusGeometry(1, 0.035, 16, 160), gateChrome = M.chrome(), gateNeon = M.neon(2);
CFG.beats.forEach((c, i) => {
  if (!i) return;
  const a = stB(i - 1), b = stA(i), t0 = c.ta - FLY, on = (t) => t > t0 - 0.03 && t < c.ta + 0.03;
  [0.16, 0.33, 0.5, 0.67, 0.84].forEach((u, k) => {
    const g = new THREE.Mesh(gateGeo, k === 2 ? gateNeon : gateChrome);
    g.position.copy(camPos(lerpSt(a, b, u))); g.lookAt(camPos(lerpSt(a, b, u + 0.02)));
    g.scale.setScalar(k === 2 ? 2.4 : 1.9); scene.add(g);
    ticks.push((t) => { g.visible = on(t); g.rotation.z = t * 2 + k; });
  });
  for (let k = 0; k < 9; k++) {
    const u = 0.08 + k * 0.105, p = camPos(lerpSt(a, b, u)), ang = R(0, Math.PI * 2), d = R(0.9, 2.2);
    const m = new THREE.Mesh(sparkGeo, k % 3 === 0 ? M.irid() : gateChrome);
    m.position.set(p.x + Math.cos(ang) * d, p.y + Math.sin(ang) * d * 0.7, p.z); m.scale.setScalar(R(0.12, 0.26)); scene.add(m);
    const w = R(2, 5);
    ticks.push((t) => { m.visible = on(t); m.rotation.set(t * w, t * w * 0.7, k); });
  }
});

// ---------- post: bloom glints, chromatic edge + vignette + flash
const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.3, 0.4, 0.93));
const fin = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uFlash: { value: 0 }, uCA: { value: 0.0012 } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uFlash; uniform float uCA; varying vec2 vUv;
    void main(){ vec2 d = vUv - 0.5; float r2 = dot(d, d); vec2 off = d * uCA * (1.0 + 6.0 * r2);
      vec3 c = vec3(texture2D(tDiffuse, vUv + off).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - off).b);
      c *= 1.0 - 0.5 * smoothstep(0.1, 0.62, r2 * 1.6);
      c += uFlash * vec3(1.0, 0.85, 0.97);
      gl_FragColor = vec4(c, 1.0); }`,
});
composer.addPass(fin);
composer.addPass(new OutputPass());
// a full-frame flash only on the few reveals the build marks (c.flash); station changes are flash-free whip moves
CFG.beats.forEach((c) => {
  if (c.flash == null) return;
  tl.fromTo(fin.uniforms.uFlash, { value: 0 }, { value: 0.07, duration: 0.05, ease: "power2.out", immediateRender: false }, c.flash - 0.02);
  tl.fromTo(fin.uniforms.uFlash, { value: 0.07 }, { value: 0, duration: 0.22, ease: "power2.in", immediateRender: false }, c.flash + 0.03);
});

function kick(t, list, len, f) { let v = 0; for (const x of list) { const ti = Array.isArray(x) ? x[0] : x, dt = t - ti; if (dt >= 0 && dt < len) v += f(dt, x); } return v; }

function renderAt(t) {
  t = Math.max(0, t);
  tl.seek(t, false);
  U.uT.value = t;
  for (const f of ticks) f(t);
  const sx = kick(t, impacts, 0.6, (dt, x) => Math.sin(dt * 67) * Math.exp(-dt * 9) * x[1]);
  const sy = kick(t, impacts, 0.6, (dt, x) => Math.cos(dt * 53) * Math.exp(-dt * 9) * x[1]);
  fin.uniforms.uCA.value = 0.0012 + kick(t, caKicks, 0.4, (dt) => 0.006 * Math.exp(-dt * 10));
  const ce = Math.cos(cam.el);
  camera.position.set(cam.lx + cam.r * Math.sin(cam.az) * ce + sx, cam.ly + cam.r * Math.sin(cam.el) + sy, cam.lz + cam.r * Math.cos(cam.az) * ce);
  lookV.set(cam.lx + sx * 0.5, cam.ly + sy * 0.5, cam.lz); camera.lookAt(lookV);
  camera.rotateZ(cam.roll);
  scene.fog.near = cam.r + 7; scene.fog.far = cam.r + 31;     // the next station stays visible through a whip flight
  composer.render();
}

window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
renderAt(0);
window.addEventListener("hf-seek", (e) => { renderAt(e.detail.time); renderer.getContext().finish(); });
window.__h9WorldReady && window.__h9WorldReady();
