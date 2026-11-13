// 九帽动效 · chrome3d — Y2K liquid chrome in a bright studio. Each beat is a display "station" above an endless mirror
// floor; a pale sky runs down to a hot orange horizon band and a deep violet floor that mirrors every object. The camera
// sits low and close, looks slightly up, orbits each station and whips from one to the next through ring gates.
// Real extruded type (font outlines from the build), a procedural studio HDRI (sky + orange band + violet floor + three
// strip lights) so chrome reflects colour and the strips slide across it as the camera moves; one hot accent for glints.
// Deterministic: every frame is drawn from the seek time alone (hf-seek). CFG and GLYPHS come from styles/chrome3d.py.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { Reflector } from "three/addons/objects/Reflector.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const CFG = window.__H9_CHROME;
const GLYPHS = window.__H9_GLYPHS;
const W = CFG.w, H = CFG.h, P = CFG.portrait, D = CFG.D;
const gsap = window.gsap;
const ACC = new THREE.Color(CFG.accent);          // hot pink: glints, shock rings, flashes only
const NAVY = new THREE.Color("#151538");
const FOV = P ? 40 : 36;
const FPX = (H / 2) / Math.tan((FOV * Math.PI) / 360);   // focal length in px
// framing: the subject (look point) sits at 45 % of the frame height, the horizon at 70 % (the mirror floor fills the
// bottom 30 %). A lens shift places the subject, a fixed upward tilt places the horizon: a low camera looking up.
const SUBJ_Y = 0.45, HOR_Y = 0.70;
const SHIFT = (0.5 - SUBJ_Y) * H;
const EL0 = -Math.atan(((HOR_Y - SUBJ_Y) * H) / FPX);
const CAM_H = 0.34;                    // camera height above the floor at the middle of each station's dolly
const FLOOR = 0;
// a whip flight takes FLY s and lands ARR s before its sentence starts (inside the narration pause);
// each station pre-rolls its main object so it is readable on the first spoken word
const ARR = 0.08, FLY = 0.45;
const LATE = { outro: 0.55 };   // the outro station arrives a little after its line starts, so the last line holds still first
CFG.beats.forEach((c, i) => { c.ta = i ? c.t - ARR + (LATE[c.kind] || 0) : 0; });
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
scene.fog = new THREE.Fog(new THREE.Color("#f6c3a0"), 14, 32);
const U = { uT: { value: 0 } };       // shared time uniform (seek time)

// sky by elevation (degrees): pale studio grey-blue overhead, warming to a hot orange band on the horizon; below the
// horizon deep violet (only ever seen in reflections). Shared by the backdrop and the reflection HDRI.
const SKY = [[90, "#dfe6f2"], [30, "#dfe6f2"], [19, "#e6e0e6"], [11, "#f4d4c0"], [5.5, "#ffb889"], [2, "#ff9a52"], [0.4, "#ff8a3c"],
  [0, "#ff8a3c"], [-0.6, "#5a2f86"], [-8, "#2b1a6b"], [-90, "#170e40"]];
// the reflection world is the same studio with its horizon raised to +24°: a vertical type face seen from the low camera
// reflects about +5…+16°, so front faces mirror the deep violet floor (dark, legible on the pale sky) while bevels and
// top faces, which tilt upward, catch the orange band, the pale sky and the strip lights (chrome edges)
const ENV = [[90, "#f3f5fb"], [48, "#dfe6f2"], [34, "#ebe2e6"], [29, "#ffc49a"], [25.6, "#ff8a3c"], [24.4, "#ff7a30"], [24.15, "#fff4ea"],
  [23.85, "#3c2183"], [18, "#2b1a6b"], [4, "#22145a"], [-10, "#170d45"], [-90, "#0b0726"]];
function skyFill(g, w, h, stops = SKY) {
  const gr = g.createLinearGradient(0, 0, 0, h);
  for (const [e, col] of stops) gr.addColorStop(clamp01(0.5 - e / 180), col);
  g.fillStyle = gr; g.fillRect(0, 0, w, h);
}
scene.background = (() => {
  const w = 1024, h = 2048, c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d");
  skyFill(g, w, h);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.mapping = THREE.EquirectangularReflectionMapping; return t;
})();

// procedural studio HDRI (reflections only): the same sky / orange band / violet floor, plus three tall white strip lights
// behind and beside the camera (u≈0.75 is straight behind it). Front faces of the type reflect the band (sunset chrome
// banding); the strips are the clear highlights that slide across the chrome when the camera orbits.
// Pixels near white are boosted ×4 so the strips are true HDR highlights (and small bloom glints).
function studioHDRI() {
  const w = 2048, h = 1024, c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d");
  skyFill(g, w, h, ENV);
  g.fillStyle = "#fff";
  g.filter = "blur(3px)";
  for (const [u, sw] of [[0.65, 16], [0.785, 22], [0.91, 13]]) g.fillRect(u * w - sw / 2, h * 0.16, sw, h * 0.36);   // three strips, +61° … -4°
  g.fillRect(w * 0.3, h * 0.05, w * 0.18, 30);                                                                    // a far overhead bar (top faces)
  g.filter = "none";
  const px = g.getImageData(0, 0, w, h).data, n = w * h;
  const data = new Uint16Array(n * 4), toH = THREE.DataUtils.toHalfFloat;
  for (let i = 0; i < n; i++) {
    // DataTexture rows run bottom-up (v = 0 is straight down): flip the canvas rows so the sky is overhead
    const o = ((h - 1 - Math.floor(i / w)) * w + (i % w)) * 4;
    const hot = px[i * 4] > 246 && px[i * 4 + 1] > 246 && px[i * 4 + 2] > 246;
    for (let k = 0; k < 3; k++) { const v = px[i * 4 + k] / 255; let L = Math.pow(v, 2.2); if (hot) L *= 3; data[o + k] = toH(L); }
    data[o + 3] = toH(1);
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

// floor: an endless glossy violet mirror. Grazing angles near the horizon mirror the orange band strongly, the near floor
// is mostly deep violet with the stations' reflections on it; a chrome horizon line is drawn at its far edge (a few px
// wide, measured in screen px so it stays crisp at any camera height).
const floor = new Reflector(new THREE.PlaneGeometry(3000, 3000), {
  textureWidth: W, textureHeight: H, clipBias: 0.003, multisample: 4,
  shader: {
    uniforms: { color: { value: null }, tDiffuse: { value: null }, textureMatrix: { value: null }, uT: { value: 0 },
      uBase: { value: new THREE.Color("#2b1a6b") }, uF: { value: FPX } },
    vertexShader: `uniform mat4 textureMatrix; varying vec4 vUv; varying vec3 vW;
      void main(){ vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz; vUv = textureMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform vec3 color; uniform sampler2D tDiffuse; uniform float uT; uniform vec3 uBase; uniform float uF; varying vec4 vUv; varying vec3 vW;
      void main(){ vec2 uv = vUv.xy / vUv.w;
        float hd = length(vW.xz - cameraPosition.xz), dep = atan(max(cameraPosition.y, 0.001), hd);
        float rip = 0.5 * sin(vW.z * 1.7 + uT * 1.5) + 0.5 * sin(vW.x * 1.2 - uT * 1.0 + vW.z * 0.6);
        uv += vec2(0.0025, 0.004) * rip * exp(-hd * 0.06);
        vec3 r = vec3(0.0);
        for (int k = -2; k <= 2; k++) r += texture2D(tDiffuse, uv + vec2(0.0, float(k) * 0.0016)).rgb;
        r *= 0.2;
        float fres = mix(0.74, 0.2, smoothstep(0.0, 0.12, dep));
        vec3 col = mix(uBase, r * color, fres);
        vec2 gq = vW.xz / 3.0, gl = abs(fract(gq - 0.5) - 0.5) / fwidth(gq);
        col += (1.0 - min(min(gl.x, gl.y), 1.0)) * vec3(0.5, 0.36, 0.9) * 0.05 * exp(-hd * 0.025);
        float px = dep * uF, aa = max(fwidth(px), 0.5), bw = uF / 300.0;      // ≈ 9 px tall in 9:16
        float band = 1.0 - smoothstep(bw, bw + aa, px);
        vec3 chromeC = mix(vec3(2.4, 2.38, 2.34), vec3(0.5, 0.52, 0.7), smoothstep(0.18, 0.45, px / bw));
        chromeC = mix(chromeC, vec3(0.012, 0.01, 0.05), smoothstep(0.55, 0.8, px / bw));
        col = mix(col, chromeC, band);
        gl_FragColor = vec4(col, 1.0); }`,
  },
});
floor.material.uniforms.uT = U.uT; floor.material.uniforms.color.value = new THREE.Color(0.8, 0.7, 1);
floor.rotation.x = -Math.PI / 2; floor.position.y = FLOOR; scene.add(floor);

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
  steel: () => new THREE.MeshPhysicalMaterial({ color: 0xc4c2d6, metalness: 1, roughness: 0.16 }),
  irid: () => new THREE.MeshPhysicalMaterial({ color: 0xffffff, metalness: 1, roughness: 0.07, iridescence: 1, iridescenceIOR: 1.75, iridescenceThicknessRange: [260, 620] }),
  navy: () => new THREE.MeshPhysicalMaterial({ color: NAVY, metalness: 0.5, roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.03 }),
  black: () => new THREE.MeshPhysicalMaterial({ color: 0x0c0a24, metalness: 0.3, roughness: 0.18, clearcoat: 1, clearcoatRoughness: 0.03 }),
  neon: (k = 1.8, op = 1) => new THREE.MeshBasicMaterial({ color: ACC.clone().multiplyScalar(k), toneMapped: false, transparent: op < 1, opacity: op, fog: false }),
};
function holo() {   // holographic foil (the "hit" face of a coin): hot pink → orange → ice ramp by view angle + position, a light band sweeping across
  return new THREE.ShaderMaterial({
    uniforms: { uT: U.uT, uA: { value: ACC.clone() } },
    vertexShader: `varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      void main(){ vUv = uv; vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz; vN = normalize(mat3(modelMatrix) * normal);
        vV = normalize(cameraPosition - wp.xyz); gl_Position = projectionMatrix * viewMatrix * wp; }`,
    fragmentShader: `uniform float uT; uniform vec3 uA; varying vec3 vN; varying vec3 vV; varying vec3 vW; varying vec2 vUv;
      vec3 ramp(float h){ vec3 p = uA, l = vec3(1.0, 0.54, 0.24), c = vec3(0.92, 0.9, 1.0); h = fract(h) * 3.0;
        return h < 1.0 ? mix(p, l, h) : (h < 2.0 ? mix(l, c, h - 1.0) : mix(c, p, h - 2.0)); }
      void main(){ float f = 1.0 - abs(dot(normalize(vN), normalize(vV)));
        float h = f * 1.3 + vUv.x * 0.3 + vUv.y * 0.2 + vW.x * 0.07 + vW.y * 0.05 - uT * 0.16;
        vec3 col = ramp(h) * (0.6 + 0.4 * f);
        float band = 1.0 - smoothstep(0.0, 0.05, abs(fract(vW.x * 0.11 - vW.y * 0.08 - uT * 0.32) - 0.5));
        col += band * vec3(0.7, 0.68, 0.7);
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
  const rg = g.createRadialGradient(64, 64, 0, 64, 64, 34); rg.addColorStop(0, "rgba(255,255,255,1)"); rg.addColorStop(0.2, "rgba(255,170,205,.85)"); rg.addColorStop(0.55, "rgba(255,61,127,.35)"); rg.addColorStop(1, "rgba(255,61,127,0)");
  g.fillStyle = rg; g.fillRect(0, 0, 128, 128);
  for (const [w, len, a] of [[3, 62, 0], [3, 62, Math.PI / 2], [1.6, 30, Math.PI / 4], [1.6, 30, -Math.PI / 4]]) {
    g.save(); g.translate(64, 64); g.rotate(a);
    const lg = g.createLinearGradient(-len, 0, len, 0); lg.addColorStop(0, "rgba(255,255,255,0)"); lg.addColorStop(0.5, "rgba(255,255,255,1)"); lg.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = lg; g.beginPath(); g.moveTo(-len, 0); g.lineTo(0, -w); g.lineTo(len, 0); g.lineTo(0, w); g.closePath(); g.fill(); g.restore();
  }
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
function sprite(size = 1, tint = 1) {
  const m = new THREE.SpriteMaterial({ map: starTex, color: new THREE.Color(1, 1, 1).multiplyScalar(1.6 * tint), depthWrite: false, transparent: true, toneMapped: false, fog: false });
  const s = new THREE.Sprite(m); s.scale.setScalar(size); return s;
}
function glint(parent, x, y, z, t0, size = 1) {
  const s = sprite(0.001); s.position.set(x, y, z); parent.add(s);
  tl.fromTo(s.scale, { x: 0.001, y: 0.001 }, { x: size, y: size, duration: 0.14, ease: "power2.out" }, t0);
  tl.to(s.scale, { x: 0.001, y: 0.001, duration: 0.5, ease: "power2.in" }, t0 + 0.14);
  tl.fromTo(s.material, { rotation: 0 }, { rotation: 1.4, duration: 0.64, ease: "none" }, t0);
  return s;
}
function twinkles() {}       // no starfield in the bright studio

// ---------- ambient Y2K objects (chrome sparkle stars, iridescent rings and capsules) at the frame edges
const sparkGeo = (() => {
  const s = new THREE.Shape(); s.moveTo(0, 1); s.quadraticCurveTo(0.08, 0.08, 1, 0); s.quadraticCurveTo(0.08, -0.08, 0, -1); s.quadraticCurveTo(-0.08, -0.08, -1, 0); s.quadraticCurveTo(-0.08, 0.08, 0, 1);
  const g = new THREE.ExtrudeGeometry(s, { depth: 0.16, bevelEnabled: true, bevelThickness: 0.07, bevelSize: 0.05, bevelSegments: 4, curveSegments: 16 }); g.center(); return g;
})();
const SHAPES = [
  () => new THREE.Mesh(sparkGeo, M.chrome()),
  () => new THREE.Mesh(new THREE.TorusGeometry(1, 0.34, 32, 80), M.irid()),
  () => new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), M.chrome()),
  () => new THREE.Mesh(new THREE.CapsuleGeometry(0.42, 1.0, 8, 24), M.irid()),
  () => new THREE.Mesh(sparkGeo, M.irid()),
];
function floaters(parent, F, t0, n = 2, seed = 0) {      // a few Y2K objects at the frame edges, always above the floor
  for (let i = 0; i < n; i++) {
    const m = SHAPES[(seed + i) % SHAPES.length]();
    const side = (i + seed) % 2 ? 1 : -1;
    const sc = F.px * R(46, 70);
    const x = side * F.fw * R(0.4, 0.47), y = F.base + F.px * R(330, 700), z = R(-3.2, -1.2);
    m.position.set(x, y, z); m.scale.setScalar(sc); parent.add(m);
    const w = R(0.4, 0.9) * (rnd() < 0.5 ? -1 : 1), ph = R(0, 6.28);
    ticks.push((t) => { m.rotation.set(t * w * 0.7 + ph, t * w + ph, t * 0.25); m.position.y = y + Math.sin(t * 0.9 + ph) * F.px * 14; });
    tl.from(m.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.6, ease: "back.out(1.4)" }, Math.max(0, t0 - 0.4) + i * 0.08);
  }
}
function shockRing(parent, t0, r1, y = 0, z = 0.2, flat = false) {    // a hot-pink glint ring on a hit; gone in 0.75 s
  const m = new THREE.Mesh(new THREE.TorusGeometry(1, 0.012, 8, 160), M.neon(1.6, 1)); m.material.transparent = true;
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

// weight: fall from `from` onto `to`, one small bounce, settle (never an endless wobble)
function settle(obj, key, from, to, t0, dur = 0.55, b = 0.07) {
  const up = to + (from - to) * b;
  tl.fromTo(obj, { [key]: from }, { [key]: to, duration: dur * 0.6, ease: "power2.in" }, t0);
  tl.fromTo(obj, { [key]: to }, { [key]: up, duration: dur * 0.2, ease: "power2.out", immediateRender: false }, t0 + dur * 0.6);
  tl.fromTo(obj, { [key]: up }, { [key]: to, duration: dur * 0.2, ease: "power2.in", immediateRender: false }, t0 + dur * 0.8);
}
const appear = (obj, t0) => tl.fromTo(obj.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: obj.scale.x, y: obj.scale.y, z: obj.scale.z, duration: 0.01 }, t0);

// ---------- stations: dolly (r) and orbit half-angle (a, rad; the camera swings 2a ≈ 25–32° per beat, direction alternates).
// Elevation is fixed at EL0 so the horizon holds at 70 % of the frame; only moat looks down at its chip, then tilts up.
const STN = {
  hero:     { L: { r: [11.4, 10.2], a: 0.24 },  P: { r: [13.4, 12.0], a: 0.24 } },
  bars:     { L: { r: [12.6, 11.6], a: 0.26 },  P: { r: [14.6, 13.6], a: 0.22 } },
  multiple: { L: { r: [12.6, 10.4], a: 0.22 },  P: { r: [14.2, 12.0], a: 0.22 } },
  coins:    { L: { r: [12.8, 11.9], a: 0.24 },  P: { r: [14.8, 13.9], a: 0.22 } },
  moat:     { L: { r: [12.4, 11.4], a: 0.28, el: [0.13, 0.04] },  P: { r: [14.6, 13.4], a: 0.26, el: [0.14, 0.04] } },
  swarm:    { L: { r: [12.6, 11.6], a: 0.26 },  P: { r: [14.6, 13.6], a: 0.24 } },
  shovel:   { L: { r: [12.0, 11.0], a: 0.24 },  P: { r: [14.2, 13.2], a: 0.22 } },
  outro:    { L: { r: [11.0, 10.0], a: 0.22 },  P: { r: [13.2, 12.2], a: 0.22 } },
};
const stnOf = (kind) => (STN[kind] || STN.hero)[P ? "P" : "L"];
// frame at the station's mean distance: width/height in world units, px → world scale, and the floor level (local y)
function frameOf(kind) {
  const s = stnOf(kind), rm = (s.r[0] + s.r[1]) / 2;
  const fh = 2 * rm * Math.tan((FOV * Math.PI) / 360), fw = (fh * W) / H;
  const Yc = CAM_H - rm * Math.sin(EL0);
  return { fw, fh, px: rm / FPX, Yc, base: -Yc, Y: (ypx) => (SUBJ_Y * H - ypx) * (rm / FPX) };
}
const origin = (i) => new THREE.Vector3(Math.sin(i * 1.7) * 9, frameOf(CFG.beats[i].kind).Yc, -i * 34);

// ================================================================ station builders
const B = {};

B.hero = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004);
  const tx = word(c.value, { depth: 0.34, bevel: 0.03, mat });
  fitTo(tx, F.fw * (P ? 1.0 : 0.6), F.fh * (P ? 0.27 : 0.42)); G.add(tx);
  const s = tx.userData.s, tw = tx.userData.w * s, th = tx.userData.h * s;
  const tE = c.enter != null && c.enter > c.t + 0.01 ? c.enter : pre(c, 0.45);
  // each glyph drops in from above the frame, tumbles upright and lands with one small bounce
  tx.userData.glyphs.forEach((p, j) => {
    const t0 = tE + j * 0.06;
    appear(p, t0);
    settle(p.position, "y", (F.fh * 0.75) / s, 0, t0, 0.6, 0.06);
    tl.from(p.rotation, { x: (j % 2 ? 1 : -1) * 1.1, z: R(-0.3, 0.3), duration: 0.42, ease: "power2.out" }, t0);
  });
  tl.fromTo(mat.userData.amp, { value: 0.07 }, { value: 0.0015, duration: 1.4, ease: "power2.out", immediateRender: false }, tE + 0.36);
  // punch on the cue: one overshoot, glints, a pink shock ring, a camera kick
  tl.fromTo(tx.scale, { x: s * 1.08, y: s * 1.08, z: s * 1.08 }, { x: s, y: s, z: s, duration: 0.5, ease: "back.out(1.7)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.05 }, { value: 0.0015, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at);
  glint(G, tw * 0.44, th * 0.42, 0.4, c.at + 0.05, th * 0.8);
  glint(G, -tw * 0.36, -th * 0.38, 0.4, c.at + 0.22, th * 0.55);
  impacts.push([c.at, 0.1]); caKicks.push(c.at);
  if (c.deco === "blob") {
    const bl = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 48), blobMat(M.irid()));
    const br = Math.min(F.fw * 0.24, Math.max(th * 0.4, tw * 0.2));
    bl.position.set(tw * 0.3, th * 0.55, -3.6); bl.scale.setScalar(br); G.add(bl);
    tl.from(bl.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.9, ease: "back.out(1.4)" }, pre(c, 0.5));
    tl.fromTo(bl.material.userData.blob, { value: 0.1 }, { value: 0.3, duration: 0.25, ease: "power2.out", immediateRender: false }, c.at);
    tl.to(bl.material.userData.blob, { value: 0.13, duration: 1.4, ease: "power2.out" }, c.at + 0.25);
    ticks.push((t) => { bl.rotation.set(t * 0.2, t * 0.3, 0); });
    shockRing(G, c.at, Math.max(tw, th) * 0.8);
    shockRing(G, c.at + 0.1, Math.max(tw, th) * 1.1);
  } else {
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1, 0.045, 48, 240), M.irid());
    ring.scale.setScalar(Math.max(tw * 0.62, th * 1.6)); ring.position.z = -4.2; G.add(ring);
    ticks.push((t) => { ring.rotation.set(1.18 + 0.1 * Math.sin(t * 0.7), 0.24 * Math.sin(t * 0.5), t * 0.35); });
    tl.fromTo(ring.scale, { x: 0.3, y: 0.3, z: 0.3 }, { x: ring.scale.x, y: ring.scale.x, z: ring.scale.x, duration: 1.1, ease: "back.out(1.3)" }, pre(c, 0.45));
    for (let k = 0; k < 3; k++) {
      const b = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 20), M.chrome()); b.scale.setScalar(0.07); ring.add(b);
      ticks.push((t) => { const a = t * 0.9 + k * 2.1; b.position.set(Math.cos(a), Math.sin(a), 0); });
    }
    shockRing(G, c.at, Math.max(tw, th) * 0.75);
  }
  floaters(G, F, c.t, 2, i);
  return {};
};

B.bars = (c, G, F, i) => {
  const n = c.items.length, vals = c.items.map((x) => x[1]), maxv = Math.max(...vals, 1e-6);
  const base = F.base, top = F.Y(P ? 830 : 390), Hmax = top - base;
  const total = F.fw * (P ? 0.7 : 0.46), bw = total / (n + (n - 1) * 0.45), gap = bw * 0.45;
  const plate = new THREE.Mesh(new RoundedBoxGeometry(total + bw * 0.8, bw * 0.12, bw * 1.7, 3, bw * 0.05), M.navy());
  plate.position.set(0, base + bw * 0.06, 0); G.add(plate);
  tl.from(plate.scale, { x: 0.001, duration: 0.5, ease: "expo.out" }, pre(c, 0.5));
  const labMat = M.navy(), valMat = M.chrome();
  const floor0 = base + bw * 0.12;
  c.items.forEach(([lab, v], j) => {
    const last = j === n - 1, h = Math.max(bw * 0.12, (v / maxv) * (Hmax - bw * 0.12));
    const geo = new RoundedBoxGeometry(bw, h, bw, 4, Math.min(bw * 0.1, h * 0.45)); geo.translate(0, h / 2, 0);
    const mesh = new THREE.Mesh(geo, last ? M.irid() : j === n - 2 ? M.chrome() : M.steel());
    const x = -total / 2 + bw / 2 + j * (bw + gap); mesh.position.set(x, floor0, 0); G.add(mesh);
    const t0 = last ? c.at_v - 0.55 : Math.min(c.at, pre(c, 0.45)) + j * 0.16, dur = last ? 1.2 : 0.6;
    tl.from(mesh.scale, { y: 0.001, duration: dur, ease: "back.out(1.3)" }, t0);
    const lb = word(lab, { depth: 0.05, bevel: 0.006, mat: labMat }); fitTo(lb, bw * 0.84, F.px * (P ? 46 : 38));
    const lh = lb.userData.h * lb.userData.s;
    lb.position.set(x, floor0 + lh * 0.5 + bw * 0.08, bw * 0.53); G.add(lb);
    appear(lb, t0 + Math.min(dur * 0.3, 0.2));
    if (!last) {
      const vl = word(v.toFixed(c.dec), { depth: 0.1, bevel: 0.01, mat: valMat }); fitTo(vl, bw * 1.1, F.px * (P ? 56 : 44));
      vl.position.set(x, floor0 + h + F.px * (P ? 50 : 40), bw * 0.3); G.add(vl);
      tl.from(vl.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.45, ease: "back.out(1.8)" }, t0 + dur * 0.55);
    } else {
      // the headline figure: one big chrome counter across the sky, counting with the last bar's growth
      const ctr = counter3d({ from: 0, to: v, dec: c.dec, pre: c.pre, suf: c.suf }, { depth: 0.3, bevel: 0.026, mat: liquid(M.chrome(), 0.006) });
      fitTo(ctr, F.fw * (P ? 0.88 : 0.44), F.px * (P ? 190 : 150));
      const cw = ctr.userData.w * ctr.userData.s, chh = ctr.userData.h * ctr.userData.s, cy = F.Y(P ? 610 : 220);
      ctr.position.set(0, cy, 0.2); G.add(ctr);
      tl.fromTo(ctr.userData.st, { v: 0 }, { v, duration: dur, ease: "power3.out" }, t0);
      tl.from(ctr.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(1.7)" }, t0);
      glint(G, cw * 0.45, cy + chh * 0.4, 0.5, t0 + dur - 0.1, chh * 1.0);
      shockRing(G, c.at_v, cw * 0.5, cy, 0.4);
      impacts.push([c.at_v, 0.08]); caKicks.push(c.at_v);
    }
  });
  floaters(G, F, c.t, 2, i);
  return {};
};

B.multiple = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004); mat.emissive = ACC.clone(); mat.emissiveIntensity = 0;
  const tx = word(c.value, { depth: 0.36, bevel: 0.03, mat });
  fitTo(tx, F.fw * (P ? 1.04 : 0.6), F.fh * (P ? 0.28 : 0.42)); G.add(tx);
  const s = tx.userData.s, tw = tx.userData.w * s, th = tx.userData.h * s;
  // rushes in from deep behind the station, glyphs flip up and land with one overshoot
  tl.from(tx.position, { z: -18, duration: 0.6, ease: "expo.out" }, pre(c, 0.45));
  tx.userData.glyphs.forEach((p, j) => {
    tl.from(p.rotation, { x: -Math.PI / 2, duration: 0.6, ease: "back.out(1.4)" }, pre(c, 0.38) + j * 0.04);
    tl.from(p.scale, { x: 0.01, y: 0.01, z: 0.01, duration: 0.4, ease: "power3.out" }, pre(c, 0.38) + j * 0.04);
  });
  tl.fromTo(mat, { emissiveIntensity: 0.55 }, { emissiveIntensity: 0, duration: 0.5, ease: "power2.out", immediateRender: false }, c.at);
  tl.fromTo(tx.scale, { x: s * 1.12, y: s * 1.12, z: s * 1.12 }, { x: s, y: s, z: s, duration: 0.55, ease: "back.out(1.8)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.07 }, { value: 0.0015, duration: 1.0, ease: "power2.out", immediateRender: false }, c.at);
  shockRing(G, c.at, Math.max(tw, th) * 0.6); shockRing(G, c.at + 0.08, Math.max(tw, th) * 0.9);
  impacts.push([c.at, 0.14]); caKicks.push(c.at);
  for (let k = 0; k < 12; k++) {    // glint burst
    const a = (k / 12) * Math.PI * 2 + 0.2, sp = sprite(0.001); G.add(sp);
    const r1 = Math.max(tw, th) * R(0.42, 0.62);
    tl.fromTo(sp.position, { x: 0, y: 0, z: 0.5 }, { x: Math.cos(a) * r1, y: Math.sin(a) * r1 * 0.6, z: 0.5, duration: 0.7, ease: "expo.out" }, c.at);
    tl.fromTo(sp.scale, { x: 0.001, y: 0.001 }, { x: th * 0.4, y: th * 0.4, duration: 0.12 }, c.at);
    tl.to(sp.scale, { x: 0.001, y: 0.001, duration: 0.5, ease: "power2.in" }, c.at + 0.25);
  }
  // speed streaks rushing past the camera for the whole beat (violet on the pale sky)
  const streakMat = new THREE.MeshBasicMaterial({ color: new THREE.Color("#3a2580"), fog: false, transparent: true, opacity: 0.55 });
  const streaks = [];
  for (let k = 0; k < 60; k++) {
    const m = new THREE.Mesh(new THREE.BoxGeometry(0.016, 0.016, R(1.2, 2.6)), k % 9 === 0 ? M.neon(1.4) : streakMat);
    const a = R(0, Math.PI * 2), r = R(2.2, 8); m.userData = { x: Math.cos(a) * r * (W / H > 1 ? 1.6 : 0.8), y: Math.max(F.base + 0.3, Math.sin(a) * r), z0: R(0, 44), v: R(26, 40) };
    G.add(m); streaks.push(m);
  }
  ticks.push((t) => {
    const k = t - c.t, on = k > -0.4 && k < c.d + 0.2;
    for (const m of streaks) { m.visible = on; if (!on) continue; const u = m.userData; m.position.set(u.x, u.y, ((u.z0 + (k + 0.4) * u.v) % 44) - 32); }
  });
  floaters(G, F, c.t, 2, i + 1);
  return {};
};

B.coins = (c, G, F, i) => {
  const N = c.n, cols = Math.ceil(Math.sqrt(N)), rows = Math.ceil(N / cols);
  const gw = P ? F.fw * 0.78 : F.fw * 0.4, gh = F.px * (P ? 430 : 560);
  const pitch = Math.min(gw / cols, gh / rows), cr = pitch * 0.43;
  const gx = P ? 0 : -F.fw * 0.17, gy = P ? F.Y(780) : F.Y(470);
  const geo = new THREE.CylinderGeometry(cr, cr, cr * 0.2, 44, 1); geo.rotateX(Math.PI / 2);
  const mats = [M.steel(), M.chrome(), holo()];
  const coins = [];
  for (let j = 0; j < N; j++) {
    const r = Math.floor(j / cols), col = j % cols;
    const m = new THREE.Mesh(geo, mats);
    m.position.set(gx + (col - (cols - 1) / 2) * pitch, gy + ((rows - 1) / 2 - r) * pitch, 0); G.add(m); coins.push(m);
    const ta = Math.min(c.at_show - 0.25, pre(c, 0.45)) + (r + col) * 0.012;
    tl.from(m.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(1.6)" }, ta);
    tl.from(m.rotation, { y: -Math.PI / 2, duration: 0.55, ease: "expo.out" }, ta);
    if (j < c.hit) tl.to(m.rotation, { y: Math.PI, duration: 0.5, ease: "back.out(1.3)" }, c.at_hit + (j / Math.max(1, c.hit)) * 0.9);
  }
  const zs = coins.map((m) => m.position.z);
  ticks.push((t) => coins.forEach((m, j) => { m.position.z = zs[j] + Math.sin(t * 2.2 + j * 0.37) * cr * 0.25; m.rotation.x = Math.sin(t * 1.6 + j * 0.21) * 0.12; }));
  const ctr = counter3d({ from: 0, to: c.to, dec: c.dec, pre: c.pre, suf: c.suf }, { depth: 0.32, bevel: 0.028, mat: liquid(M.chrome(), 0.006) });
  fitTo(ctr, P ? F.fw * 0.64 : F.fw * 0.32, F.px * (P ? 250 : 330));
  ctr.position.set(P ? 0 : F.fw * 0.2, P ? F.Y(1170) : F.Y(486), 0.3); G.add(ctr);
  appear(ctr, pre(c, 0.3));
  settle(ctr.position, "y", ctr.position.y + F.px * 900, ctr.position.y, pre(c, 0.3), 0.6, 0.07);
  tl.fromTo(ctr.userData.st, { v: 0 }, { v: c.to, duration: 1.3, ease: "power2.out" }, c.at_hit);
  const cw = ctr.userData.w * ctr.userData.s, ch = ctr.userData.h * ctr.userData.s;
  glint(G, ctr.position.x + cw * 0.42, ctr.position.y + ch * 0.4, 0.6, c.at_hit + 1.25, ch * 0.8);
  impacts.push([c.at_hit + 1.2, 0.06]);
  floaters(G, F, c.t, 2, i + 2);
  return {};
};

B.moat = (c, G, F, i) => {
  const base = F.base;
  const sc = (F.fw * (P ? 0.94 : 0.56)) / 5.0;
  const isle = new THREE.Group(); isle.scale.setScalar(sc); isle.position.y = base; G.add(isle);
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
  const lab = word(c.chip, { depth: 0.04, bevel: 0.004, mat: M.navy() }); fitTo(lab, 0.95, 0.4);
  lab.rotation.x = -Math.PI / 2; lab.position.y = 0.215; chip.add(lab);
  chip.position.y = 0.16;
  settle(chip.position, "y", 4.0, 0.16, pre(c, 0.5), 0.6, 0.08);
  tl.from(chip.rotation, { y: -1.4, duration: 0.8, ease: "expo.out" }, pre(c, 0.5));
  ticks.push((t) => { if (t >= c.at_chip) { const k = t - c.at_chip; chip.position.x = k < 0.45 ? Math.sin(k * 90) * 0.05 * (1 - k / 0.45) : 0; } });
  // the moat
  const ringMat = liquid(M.irid(), 0.01);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(2.3, 0.2, 40, 220), ringMat); ring.rotation.x = Math.PI / 2; ring.position.y = 0.2; isle.add(ring);
  const water = new THREE.Mesh(new THREE.CircleGeometry(2.2, 96), M.black()); water.rotation.x = -Math.PI / 2; water.position.y = 0.02; isle.add(water);
  tl.from(ring.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.8, ease: "back.out(1.5)" }, c.at_moat - 0.1);
  tl.from(water.scale, { x: 0.001, y: 0.001, duration: 0.7, ease: "expo.out" }, c.at_moat);
  ticks.push((t) => { ring.rotation.z = t * 0.5; });
  tl.fromTo(ringMat.userData.amp, { value: 0.06 }, { value: 0.012, duration: 1.4, ease: "power2.out", immediateRender: false }, c.at_moat);
  // "not the chip": a navy X stamps on it, then it sinks through the floor
  const X = new THREE.Group(); X.position.y = 0.55; isle.add(X);
  for (const a of [Math.PI / 4, -Math.PI / 4]) { const bar = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.08, 0.26), M.navy()); bar.rotation.y = a; X.add(bar); }
  tl.fromTo(X.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: 1, y: 1, z: 1, duration: 0.3, ease: "back.out(2.2)" }, c.at_chip);
  tl.to(lidMat.color, { r: 0.3, g: 0.28, b: 0.36, duration: 0.3 }, c.at_chip);
  const sink = Math.min(c.at_chip + 0.55, c.at_word - 0.35);
  tl.to(chip.position, { y: -4, duration: 0.55, ease: "power3.in" }, sink);
  ticks.push((t) => { chip.visible = t < sink + 0.6; X.visible = t < sink + 0.5; });
  tl.to(X.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.3, ease: "power2.in" }, sink + 0.15);
  impacts.push([c.at_chip, 0.08]); caKicks.push(c.at_chip);
  // the real moat rises out of the ring and stands on the floor
  const wm = liquid(M.chrome(), 0.0015);
  const tx = word(c.word, { depth: 0.34, bevel: 0.03, mat: wm }); fitTo(tx, F.fw * (P ? 0.92 : 0.5), F.fh * (P ? 0.3 : 0.4));
  const th = tx.userData.h * tx.userData.s, tw = tx.userData.w * tx.userData.s;
  const ty = base + th * 0.5 + 0.3 * sc;
  tx.position.set(0, ty, 0.1 * sc); G.add(tx);
  tl.fromTo(tx.position, { y: base - th * 0.7 }, { y: ty, duration: 0.8, ease: "back.out(1.5)" }, c.at_word);
  tl.from(tx.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.45, ease: "power3.out" }, c.at_word);
  tl.fromTo(wm.userData.amp, { value: 0.09 }, { value: 0.0015, duration: 1.6, ease: "power2.out", immediateRender: false }, c.at_word);
  shockRing(isle, c.at_word + 0.1, 3.4, 0.05, 0, true);
  glint(G, tw * 0.45, ty + th * 0.45, 0.6, c.at_word + 0.55, th * 0.8);
  glint(G, -tw * 0.4, ty - th * 0.3, 0.6, c.at_word + 0.75, th * 0.5);
  impacts.push([c.at_word + 0.2, 0.1]); caKicks.push(c.at_word + 0.2);
  floaters(G, F, c.t, 2, i + 3);
  return { ly: base + th * 0.55 + 0.3 * sc };
};

B.swarm = (c, G, F, i) => {
  const mat = liquid(M.chrome(), 0.004);
  const tx = word(c.value, { depth: 0.34, bevel: 0.03, mat });
  fitTo(tx, P ? F.fw * 0.86 : F.fw * 0.44, P ? F.fh * 0.22 : F.fh * 0.4); G.add(tx);
  const tw = tx.userData.w * tx.userData.s, th = tx.userData.h * tx.userData.s, ny = P ? F.Y(760) : 0;
  tx.position.y = ny;
  tx.userData.glyphs.forEach((p, j) => {
    const t0 = pre(c, 0.45) + j * 0.06;
    appear(p, t0);
    settle(p.position, "y", (F.fh * 0.7) / tx.userData.s, 0, t0, 0.6, 0.06);
  });
  tl.fromTo(tx.scale, { x: tx.userData.s * 1.08, y: tx.userData.s * 1.08, z: tx.userData.s * 1.08 }, { x: tx.userData.s, y: tx.userData.s, z: tx.userData.s, duration: 0.5, ease: "back.out(1.7)", immediateRender: false }, c.at);
  tl.fromTo(mat.userData.amp, { value: 0.06 }, { value: 0.0015, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at);
  glint(G, tw * 0.46, ny + th * 0.4, 0.5, c.at + 0.1, th * 0.8);
  impacts.push([c.at, 0.08]); caKicks.push(c.at);
  // the developers: a galaxy of chrome beads (a few navy) orbiting the number
  const N = 900, im = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 2), M.chrome(), N); im.frustumCulled = false;
  const sw = new THREE.Group(); sw.position.y = ny; sw.rotation.x = P ? 1.3 : 1.16; sw.rotation.z = -0.12; G.add(sw); sw.add(im);
  const rho0 = Math.max(tw * 0.56, th * 0.9), rho1 = Math.max(rho0 * 1.15, Math.min(P ? F.fw * 0.44 : F.fw * 0.25, rho0 * 1.6));
  const pk = new THREE.Color(0.12, 0.1, 0.35), wh = new THREE.Color(1, 1, 1);
  const par = [];
  for (let k = 0; k < N; k++) {
    const u = Math.pow(rnd(), 0.8), rho = rho0 + (rho1 - rho0) * u;
    par.push({ rho, a: R(0, Math.PI * 2), w: (0.9 / rho) * R(0.7, 1.3), y: R(-1, 1) * (0.12 + 0.35 * u) * rho0 * 0.5, s: R(0.018, 0.055) * Math.min(F.fw, F.fh) * 0.11 });
    im.setColorAt(k, k % 7 === 0 ? pk : wh);
  }
  im.instanceColor.needsUpdate = true;
  const m4 = new THREE.Matrix4(), q = new THREE.Quaternion(), v3 = new THREE.Vector3(), s3 = new THREE.Vector3();
  ticks.push((t) => {
    const k = expoOut(clamp01((t - pre(c, 0.45)) / 1.2)), far = 1 + (1 - k) * 3.2;
    const pulse = 1 + 0.08 * Math.exp(-Math.max(0, t - c.at) * 4) * (t > c.at ? 1 : 0);
    for (let j = 0; j < N; j++) {
      const p = par[j], a = p.a + t * p.w + (1 - k) * 2;
      v3.set(Math.cos(a) * p.rho * far * pulse, Math.sin(a) * p.rho * far * pulse, p.y);
      s3.setScalar(p.s * (0.3 + 0.7 * k)); m4.compose(v3, q, s3); im.setMatrixAt(j, m4);
    }
    im.instanceMatrix.needsUpdate = true;
  });
  floaters(G, F, c.t, 2, i + 4);
  return P ? {} : { lx: -F.fw * 0.17 };
};

B.shovel = (c, G, F, i) => {
  const base = F.base;
  // the shovel: chrome handle + D-grip, iridescent blade, planted in a pile of chrome nuggets on the floor
  const sh = new THREE.Group(), spin = new THREE.Group(); sh.add(spin);
  const ch = M.chrome();
  const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 2.3, 32), ch); handle.position.y = 0.5; spin.add(handle);
  const grip = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.05, 16, 48, Math.PI), ch); grip.position.y = 1.65; spin.add(grip);
  const bar = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.5, 24), ch); bar.rotation.z = Math.PI / 2; bar.position.y = 1.65; spin.add(bar);
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.12, 0.34, 32), ch); collar.position.y = -0.78; spin.add(collar);
  const bs = new THREE.Shape(); bs.moveTo(-0.46, 0); bs.lineTo(0.46, 0); bs.lineTo(0.46, -0.78); bs.quadraticCurveTo(0.42, -1.05, 0, -1.25); bs.quadraticCurveTo(-0.42, -1.05, -0.46, -0.78); bs.lineTo(-0.46, 0);
  const bg = new THREE.ExtrudeGeometry(bs, { depth: 0.04, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 4, curveSegments: 24 }); bg.translate(0, 0, -0.02);
  const blade = new THREE.Mesh(bg, M.irid()); blade.position.y = -0.92; spin.add(blade);
  const ssc = (F.px * (P ? 860 : 700)) / 4.1;
  sh.scale.setScalar(ssc);
  const sx = P ? F.fw * 0.1 : F.fw * 0.22, sy = base + 2.0 * ssc;
  sh.position.set(sx, sy, -1.0); sh.rotation.z = -0.2; G.add(sh);
  appear(sh, pre(c, 0.5));
  settle(sh.position, "y", sy + F.px * 1400, sy, pre(c, 0.5), 0.6, 0.06);
  ticks.push((t) => { spin.rotation.y = (t - c.t) * 0.9; });
  tl.to(sh.rotation, { z: 0.1, duration: 0.16, ease: "power2.out" }, c.at_title - 0.05);
  tl.to(sh.rotation, { z: -0.2, duration: 0.5, ease: "back.out(1.6)" }, c.at_title + 0.11);
  // gold-rush nuggets: chrome (a few iridescent) raining onto a pile around the blade
  const nugGeo = new THREE.IcosahedronGeometry(1, 0), nm = M.chrome(); nm.flatShading = true;
  const pm = M.irid(); pm.flatShading = true;
  for (let k = 0; k < 46; k++) {
    const m = new THREE.Mesh(nugGeo, k % 5 === 0 ? pm : nm);
    const r = ssc * R(0.1, 0.22), x = sx + R(-1.7, 1.7) * ssc * (P ? 1.5 : 0.9) * (1 - 0.4 * rnd()), z = R(-0.6, 1.2), y = base + r * 0.7 + R(0, 0.25) * ssc * (1 - Math.abs(x - sx) / (2.6 * ssc));
    m.scale.setScalar(r); m.position.set(x, Math.max(base + r * 0.6, y), z); G.add(m);
    const t0 = Math.min(c.at_rain, pre(c, 0.35)) + k * 0.025;
    settle(m.position, "y", m.position.y + R(6, 9), m.position.y, t0, R(0.6, 0.85), 0.1);
    const w = R(-2, 2), ph = R(0, 6);
    ticks.push((t) => { const kk = clamp01((t - t0) / 0.8); m.rotation.set(ph + w * kk * 3, ph * 0.5 + w * kk, w * kk); });
  }
  // two lines of chrome type in the sky above it
  const [l1, l2] = [c.lines[0] || "", c.lines[1] || ""];
  const m1 = liquid(M.chrome(), 0.0015), m2 = liquid(M.chrome(), 0);
  const w1 = word(l1, { depth: 0.3, bevel: 0.026, mat: m1 }), w2 = word(l2, { depth: 0.34, bevel: 0.03, mat: m2 });
  fitTo(w1, F.fw * (P ? 0.92 : 0.5), F.px * (P ? 190 : 170)); fitTo(w2, F.fw * (P ? 0.92 : 0.5), F.px * (P ? 300 : 250));
  const h1 = w1.userData.h * w1.userData.s, h2 = w2.userData.h * w2.userData.s;
  const tx = P ? 0 : -F.fw * 0.18;
  w1.position.set(tx, F.Y(P ? 560 : 260), 0.3); w2.position.set(tx, F.Y(P ? 830 : 470), 0.3); G.add(w1, w2);
  w1.userData.glyphs.forEach((p, j) => {
    const t0 = c.at_title + j * 0.05;
    appear(p, t0);
    settle(p.position, "y", (F.fh * 0.5) / w1.userData.s, 0, t0, 0.55, 0.06);
  });
  const t2 = c.at_line2 || c.at_title + 0.6;
  ticks.push((t) => w2.userData.glyphs.forEach((p, j) => { p.visible = t >= t2 + j * 0.05; }));
  w2.userData.glyphs.forEach((p, j) => {
    tl.from(p.scale, { x: 2.2, y: 2.2, z: 2.2, duration: 0.22, ease: "back.out(1.4)" }, t2 + j * 0.03);
    tl.from(p.position, { z: 4, duration: 0.22, ease: "expo.out" }, t2 + j * 0.03);
  });
  tl.fromTo(m2.userData.amp, { value: 0.03 }, { value: 0, duration: 0.3, ease: "power2.out", immediateRender: false }, t2);
  tl.fromTo(m1.userData.amp, { value: 0.06 }, { value: 0.0015, duration: 1.2, ease: "power2.out", immediateRender: false }, c.at_title);
  impacts.push([c.at_title, 0.08], [t2 + 0.1, 0.12]); caKicks.push(t2 + 0.1);
  const ww2 = w2.userData.w * w2.userData.s;
  glint(G, tx + ww2 * 0.48, w2.position.y + h2 * 0.45, 0.7, t2 + 0.35, h2 * 0.8);
  floaters(G, F, c.t, 1, i + 1);
  return {};
};

B.outro = (c, G, F, i) => {
  const base = F.base;
  const prof = [[0, 0], [1.05, 0], [1.08, 0.04], [1.02, 0.07], [0.62, 0.08], [0.57, 0.14], [0.6, 0.3], [0.64, 0.5], [0.635, 0.66], [0.6, 0.84], [0.56, 1.0], [0.57, 1.05], [0.5, 1.08], [0, 1.08]].map(([x, y]) => new THREE.Vector2(x, y));
  const hat = new THREE.Group(), spin = new THREE.Group(); hat.add(spin);
  const crown = new THREE.Mesh(new THREE.LatheGeometry(prof, 120), M.chrome()); crown.material.side = THREE.DoubleSide; spin.add(crown);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.606, 0.606, 0.17, 120, 1, true), M.navy()); band.position.y = 0.24; spin.add(band);
  const nm = liquid(M.chrome(), 0.004);
  const name = word(c.title, { depth: 0.3, bevel: 0.026, mat: nm }); fitTo(name, F.fw * (P ? 0.9 : 0.5), F.px * (P ? 250 : 190));
  const nh = name.userData.h * name.userData.s, nw = name.userData.w * name.userData.s;
  const hs = (F.px * (P ? 520 : 400)) / 1.08;
  hat.scale.setScalar(hs);
  hat.position.set(0, base, -0.6); G.add(hat);
  settle(hat.position, "y", base + F.px * 1500, base, pre(c, 0.45), 0.7, 0.07);
  ticks.push((t) => { spin.rotation.y = (t - c.t) * 1.1 - 1.2; });
  const ny = F.Y(P ? 600 : 250);
  name.position.set(0, ny, 0.6); G.add(name);
  name.userData.glyphs.forEach((p, j) => {
    const t0 = c.ta + 0.1 + j * 0.07;
    appear(p, t0);
    settle(p.position, "y", (F.fh * 0.5) / name.userData.s, 0, t0, 0.55, 0.06);
  });
  tl.fromTo(nm.userData.amp, { value: 0.06 }, { value: 0.0015, duration: 0.8, ease: "power2.out", immediateRender: false }, c.ta + 0.4);
  impacts.push([c.t + 0.75, 0.1]); caKicks.push(c.t + 0.75);
  glint(G, nw * 0.47, ny + nh * 0.45, 0.9, c.t + 1.2, nh * 0.8);
  glint(G, -hs * 0.9, base + hs * 0.95, 0.4, c.t + 1.5, nh * 0.5);
  for (let k = 0; k < 4; k++) {     // chrome sparkle stars orbiting the hat
    const st = new THREE.Mesh(sparkGeo, k % 2 ? M.irid() : M.chrome()); st.scale.setScalar(hs * 0.12); G.add(st);
    const ph = (k / 4) * Math.PI * 2;
    ticks.push((t) => { const a = ph + (t - c.t) * 0.9; st.position.set(Math.cos(a) * hs * 1.5, base + hs * 0.7 + Math.sin(a * 2) * hs * 0.2, Math.sin(a) * hs * 0.9 - 0.6); st.rotation.set(0, a * 2, a); });
    tl.from(st.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.6, ease: "back.out(1.6)" }, c.t + 0.6 + k * 0.08);
  }
  return {};
};

// ================================================================ assemble
const look = [];
CFG.beats.forEach((c, i) => {
  const G = new THREE.Group(); G.position.copy(origin(i)); scene.add(G);
  const F = frameOf(c.kind);
  const o = (B[c.kind] || B.hero)(c, G, F, i) || {};
  // a station exists only from its incoming flight to the end of its outgoing one (no ghosts of far stations in the haze)
  const nx = CFG.beats[i + 1], v0 = i ? c.ta - FLY - 0.05 : -1, v1 = nx ? nx.ta + 0.05 : D + 1;
  ticks.push((t) => { G.visible = t >= v0 && t <= v1; });
  if (i) glint(G, F.fw * (i % 2 ? 0.34 : -0.34), F.Y(SUBJ_Y * H - 300), 0.8, c.ta, F.px * 120);   // arrival glint, local
  look.push({ x: G.position.x + (o.lx || 0), y: G.position.y + (o.ly || 0), z: G.position.z });
});

// camera: fly-in, a 25–32° orbit + dolly inside each beat (low, looking slightly up), whip flight with roll to the next station
const cam = { lx: 0, ly: 0, lz: 0, r: 10, az: 0, el: EL0, roll: 0 };
const stQ = (i, k) => {
  const s = stnOf(CFG.beats[i].kind), d = i % 2 ? 1 : -1;
  return { lx: look[i].x, ly: look[i].y, lz: look[i].z, r: s.r[k], az: (k ? d : -d) * s.a, el: s.el ? s.el[k] : EL0 };
};
const stA = (i) => stQ(i, 0), stB = (i) => stQ(i, 1);
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

// dolly-through: each whip flight passes through a short tunnel of chrome / iridescent ring gates with chrome shards whizzing by
// (the gates sit exactly on the camera path; they exist only during that flight)
const camPos = (q) => { const ce = Math.cos(q.el); return new THREE.Vector3(q.lx + q.r * Math.sin(q.az) * ce, q.ly + q.r * Math.sin(q.el), q.lz + q.r * Math.cos(q.az) * ce); };
const lerpSt = (a, b, u) => { const o = {}; for (const k of ["lx", "ly", "lz", "r", "az", "el"]) o[k] = a[k] + (b[k] - a[k]) * u; return o; };
const gateGeo = new THREE.TorusGeometry(1, 0.035, 16, 160), gateChrome = M.chrome(), gateIrid = M.irid();
CFG.beats.forEach((c, i) => {
  if (!i) return;
  const a = stB(i - 1), b = stA(i), t0 = c.ta - FLY, on = (t) => t > t0 - 0.03 && t < c.ta + 0.03;
  [0.16, 0.33, 0.5, 0.67, 0.84].forEach((u, k) => {
    const g = new THREE.Mesh(gateGeo, k === 2 ? gateIrid : gateChrome);
    g.position.copy(camPos(lerpSt(a, b, u))); g.lookAt(camPos(lerpSt(a, b, u + 0.02)));
    g.scale.setScalar(k === 2 ? 2.4 : 1.9); scene.add(g);
    ticks.push((t) => { g.visible = on(t); g.rotation.z = t * 2 + k; });
  });
  for (let k = 0; k < 9; k++) {
    const u = 0.08 + k * 0.105, p = camPos(lerpSt(a, b, u)), ang = R(0, Math.PI * 2), d = R(0.9, 2.2);
    const m = new THREE.Mesh(sparkGeo, k % 3 === 0 ? gateIrid : gateChrome);
    m.position.set(p.x + Math.cos(ang) * d, Math.max(0.2, p.y + Math.sin(ang) * d * 0.7), p.z); m.scale.setScalar(R(0.12, 0.26)); scene.add(m);
    const w = R(2, 5);
    ticks.push((t) => { m.visible = on(t); m.rotation.set(t * w, t * w * 0.7, k); });
  }
});

// ---------- post: low bloom (strip-light glints only), chromatic edge, a faint vignette, flash
const composer = new EffectComposer(renderer);
composer.setPixelRatio(1); composer.setSize(W, H);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(W, H), 0.3, 0.4, 0.93));
const fin = new ShaderPass({
  uniforms: { tDiffuse: { value: null }, uFlash: { value: 0 }, uCA: { value: 0.0004 } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: `uniform sampler2D tDiffuse; uniform float uFlash; uniform float uCA; varying vec2 vUv;
    void main(){ vec2 d = vUv - 0.5; float r2 = dot(d, d); vec2 off = d * uCA * (1.0 + 6.0 * r2);
      vec3 c = vec3(texture2D(tDiffuse, vUv + off).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - off).b);
      c *= 1.0 - 0.07 * smoothstep(0.1, 0.62, r2 * 1.6);
      c += uFlash * vec3(0.9, 0.95, 1.0);
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
  fin.uniforms.uCA.value = 0.0004 + kick(t, caKicks, 0.4, (dt) => 0.006 * Math.exp(-dt * 10));
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
