// 九帽动效 · studio world — one continuous 3D set the camera flies through, beat by beat.
// Real extruded CJK type (font outlines from the build), PBR materials, image environment light, depth of field.
// Deterministic: every frame is drawn from the seek time alone (hf-seek). CFG and GLYPHS are injected by styles/studio.py.
// Two sets live here: studioWorld() (the showroom, one fitted station per beat) and legacyWorld() (the 0.x six-beat set,
// kept unchanged for styles built on it, e.g. clay). styles/studio.py marks the second with CFG.legacy.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";
import { Reflector } from "three/addons/objects/Reflector.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

// ================================================================ the showroom (studio 0.19)
// A dark lacquer showroom: one station per beat, a camera fitted to each station's hero group (frustum maths, any text
// length frames itself), the chart object of the beat placed on the floor under the hero by a ray from the screen point
// where it must appear. Deterministic: every frame is a function of the seek time.
function studioWorld() {
  const CFG = window.__H9_WORLD, GL = window.__H9_GLYPHS, GL2 = window.__H9_GLYPHS2 || {};
  const W = CFG.w, H = CFG.h, P = CFG.portrait, D = CFG.D;
  const gsap = window.gsap;
  const DEG = Math.PI / 180;
  const FPS = 30, FLY = 24 / FPS, FLY_OUT = 28 / FPS;      // station moves: 24 frames (the outro pull-back 28)

  let _s = 7;
  const rnd = () => { _s |= 0; _s = (_s + 0x6d2b79f5) | 0; let t = Math.imul(_s ^ (_s >>> 15), 1 | _s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };

  // ---------- renderer
  const canvas = document.getElementById("w3d");
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false);
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  RectAreaLightUniformsLib.init();

  const scene = new THREE.Scene();
  // cyclorama: a soft vertical wall gradient, lit at the horizon and dark at the top (screen-fixed, so it never bands with the
  // camera). The stops are set so that after the filmic tone curve and the black lift below, the wall reads ≈ #2a2d36 at the
  // horizon and ≈ #0d0e12 at the top.
  const BG = CFG.bgStops || ["#0c0d10", "#15171c", "#262931"];
  const bgTex = (() => { const c = document.createElement("canvas"); c.width = 8; c.height = 512; const g = c.getContext("2d");
    const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, BG[0]); gr.addColorStop(0.5, BG[1]); gr.addColorStop(1, BG[2]);
    g.fillStyle = gr; g.fillRect(0, 0, 8, 512); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; })();
  scene.background = bgTex;
  scene.fog = new THREE.Fog(new THREE.Color(BG[2]).multiplyScalar(0.8), 40, 120);      // the far floor dissolves into the wall

  // studio environment: three soft boxes in a black room (what the metal and lacquer reflect)
  const envScene = new THREE.Scene(); envScene.background = new THREE.Color(0x030304);
  const softbox = (w, h, pos, col, k) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(col).multiplyScalar(k), side: THREE.DoubleSide }));
    m.position.set(...pos); m.lookAt(0, 0, 0); envScene.add(m); };
  softbox(12, 7, [-11, 12, 9], 0xffc690, 5.0);       // key, warm 3400 K, top-left
  softbox(2.5, 14, [12, 6, -10], 0x7fb2ff, 4.0);     // rim, cool, back-right
  softbox(18, 2.5, [0, -1, 14], 0xfff4e6, 0.55);     // low fill
  softbox(1.2, 24, [0, 16, 0], 0xffffff, 1.2);       // a thin ceiling strip (the line that runs along the type)
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(envScene, 0.0).texture;
  scene.environmentIntensity = 0.85;

  // ---------- camera
  const FOV = P ? 30 : 24;
  const camera = new THREE.PerspectiveCamera(FOV, W / H, 0.1, 600);
  const tmpV = new THREE.Vector3();

  // ---------- lights: key (warm spot, the one shadow caster), rim (cool area, back-right), fill (low area)
  const key = new THREE.SpotLight(0xffc690, 900, 80, 0.62, 0.75, 1.6);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0003; key.shadow.normalBias = 0.02; key.shadow.radius = 4;
  key.shadow.camera.near = 4; key.shadow.camera.far = 70;
  scene.add(key, key.target);
  const rim = new THREE.RectAreaLight(0x7fb2ff, 9, 4, 10); scene.add(rim);
  const fill = new THREE.RectAreaLight(0xfff1e0, 3.2, 20, 3); scene.add(fill);
  const rimAll = new THREE.DirectionalLight(0x7fb2ff, 0); scene.add(rimAll, rimAll.target);     // the outro's set-wide rim
  const wash = new THREE.DirectionalLight(0xffc690, 0); scene.add(wash, wash.target);            // the outro's low warm wash
  const LIGHT = { kx: -10, ky: 15, kz: 11, key: 900, rim: 9, fill: 3.2, env: 0.85, all: 0, wash: 0 };

  // ---------- floor: polished dark lacquer (#0b0c10, roughness ≈ .18): a blurred mirror mixed by Fresnel, plus contact shadows
  const FLOOR_Y = 0;
  const floor = new Reflector(new THREE.PlaneGeometry(4000, 4000), {
    textureWidth: Math.round(W / 2), textureHeight: Math.round(H / 2), clipBias: 0.002,
    shader: {
      uniforms: { color: { value: null }, tDiffuse: { value: null }, textureMatrix: { value: null }, uBase: { value: new THREE.Color(CFG.floorBase || "#16181d") } },
      vertexShader: `uniform mat4 textureMatrix; varying vec4 vUv; varying vec3 vW;
        void main(){ vec4 wp = modelMatrix * vec4(position, 1.0); vW = wp.xyz; vUv = textureMatrix * vec4(position, 1.0); gl_Position = projectionMatrix * viewMatrix * wp; }`,
      fragmentShader: `uniform vec3 color; uniform sampler2D tDiffuse; uniform vec3 uBase; varying vec4 vUv; varying vec3 vW;
        void main(){ vec2 uv = vUv.xy / vUv.w;
          vec3 v = normalize(cameraPosition - vW); float c = clamp(v.y, 0.0, 1.0);
          float hd = length(vW.xz - cameraPosition.xz);
          float bl = 0.0022 + 0.0016 * (1.0 - c);
          vec3 r = vec3(0.0); float wsum = 0.0;
          for (int i = -3; i <= 3; i++) { for (int j = -1; j <= 1; j++) { float w = exp(-float(i * i) / 6.0); r += w * texture2D(tDiffuse, uv + vec2(float(j) * bl * 0.6, float(i) * bl)).rgb; wsum += w; } }
          r /= wsum;
          float fres = 0.05 + 0.6 * pow(1.0 - c, 4.0);
          vec3 col = uBase * (0.7 + 0.3 * exp(-hd * 0.02)) + r * fres * color;
          gl_FragColor = vec4(col, 1.0);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`,
    },
  });
  floor.material.uniforms.color.value = new THREE.Color(1, 1, 1);
  floor.rotation.x = -Math.PI / 2; floor.position.y = FLOOR_Y; scene.add(floor);
  const shadowPlane = new THREE.Mesh(new THREE.PlaneGeometry(4000, 4000), new THREE.ShadowMaterial({ opacity: 0.62 }));
  shadowPlane.rotation.x = -Math.PI / 2; shadowPlane.position.y = FLOOR_Y + 0.002; shadowPlane.receiveShadow = true; scene.add(shadowPlane);
  const _fb = floor.onBeforeRender;
  floor.onBeforeRender = function (...a) { shadowPlane.visible = false; _fb.apply(this, a); shadowPlane.visible = true; };

  // ---------- materials
  const M = {
    metal: () => new THREE.MeshPhysicalMaterial({ color: 0xd9c7a3, metalness: 1, roughness: 0.32, envMapIntensity: 1.15 }),
    ceramic: () => new THREE.MeshPhysicalMaterial({ color: 0xece8df, metalness: 0, roughness: 0.36, clearcoat: 0.55, clearcoatRoughness: 0.22 }),
    verm: () => new THREE.MeshPhysicalMaterial({ color: 0xe2432a, metalness: 0, roughness: 0.26, clearcoat: 1, clearcoatRoughness: 0.06 }),
    glass: () => new THREE.MeshPhysicalMaterial({ color: 0x232833, metalness: 0, roughness: 0.05, transparent: true, opacity: 0.34, clearcoat: 1, clearcoatRoughness: 0.03, envMapIntensity: 1.4, depthWrite: false }),
    lacq: () => new THREE.MeshPhysicalMaterial({ color: 0x15171c, metalness: 0, roughness: 0.2, clearcoat: 0.9, clearcoatRoughness: 0.08 }),
    steel: () => new THREE.MeshPhysicalMaterial({ color: 0x8a8d94, metalness: 1, roughness: 0.3 }),
    dim: () => new THREE.MeshPhysicalMaterial({ color: 0x3a3d45, metalness: 0, roughness: 0.4, clearcoat: 0.4 }),
  };
  const MAT = { m: M.metal(), c: M.ceramic(), v: M.verm(), l: M.lacq(), s: M.steel(), d: M.dim(),
    deck: new THREE.MeshPhysicalMaterial({ color: 0x1d2027, metalness: 0, roughness: 0.28, clearcoat: 0.8, clearcoatRoughness: 0.1 }) };

  // ---------- real 3D type (glyph outlines from the build). 1 unit = 1 em before scaling
  const geoCache = {};
  function glyphGeo(tab, ch, depth, bevel) {
    const k = (tab === GL2 ? "2|" : "1|") + ch + "|" + depth.toFixed(4) + "|" + bevel;
    if (geoCache[k]) return geoCache[k];
    const g = tab[ch]; if (!g) return null;
    const sp = new THREE.ShapePath();
    for (const c of g.p) {
      if (c[0] === "M") sp.moveTo(c[1], c[2]); else if (c[0] === "L") sp.lineTo(c[1], c[2]);
      else if (c[0] === "Q") sp.quadraticCurveTo(c[1], c[2], c[3], c[4]); else if (c[0] === "C") sp.bezierCurveTo(c[1], c[2], c[3], c[4], c[5], c[6]);
    }
    let big = null, ba = 0;      // winding differs between fonts: the largest contour is always an outer one
    for (const s of sp.subPaths) { const pts = s.getPoints(); const a = Math.abs(THREE.ShapeUtils.area(pts)); if (a > ba) { ba = a; big = pts; } }
    const shapes = sp.toShapes(big ? !THREE.ShapeUtils.isClockWise(big) : false);
    const geo = depth > 0
      ? new THREE.ExtrudeGeometry(shapes, { depth, bevelEnabled: bevel > 0, bevelThickness: bevel, bevelSize: bevel * 0.8, bevelSegments: 3, curveSegments: 6 })
      : new THREE.ShapeGeometry(shapes, 6);
    geo.computeBoundingBox();
    return (geoCache[k] = geo);
  }
  function inkY(tab, str) {
    let y0 = Infinity, y1 = -Infinity;
    for (const ch of str) { const g = tab[ch]; if (!g) continue; const geo = glyphGeo(tab, ch, 0, 0); y0 = Math.min(y0, geo.boundingBox.min.y); y1 = Math.max(y1, geo.boundingBox.max.y); }
    return y0 === Infinity ? [0, 0.72] : [y0, y1];
  }
  // a line of type: runs = [[text, matKey], …] or a string. Base of the ink sits at y = 0, centred on x = 0 (align "c"),
  // starting at x = 0 ("l") or ending at x = 0 ("r"). Extrusion depth = 0.18 × cap height, bevel 0.02.
  function word(runs, { mat = "m", track = 0.01, align = "c", tab = GL, flat = false, mats = MAT } = {}) {
    if (typeof runs === "string") runs = [[runs, mat]];
    const str = runs.map((r) => r[0]).join("");
    const [y0, y1] = inkY(tab, str), cap = Math.max(0.3, y1 - y0);
    const depth = flat ? 0 : 0.18 * cap, bevel = flat ? 0 : 0.02;
    const grp = new THREE.Group(); const glyphs = []; let x = 0;
    for (const [s, mk] of runs) for (const ch of s) {
      if (ch === " ") { x += 0.28; continue; }
      const g = tab[ch]; if (!g) continue;
      const piv = new THREE.Group();
      const m = new THREE.Mesh(glyphGeo(tab, ch, depth, bevel), typeof mk === "string" ? mats[mk] : mk);
      m.castShadow = !flat; m.receiveShadow = !flat;
      m.position.set(-g.a / 2, -y0, -depth / 2 - bevel);
      piv.add(m); piv.position.x = x + g.a / 2; piv.userData.mat = mk; grp.add(piv); glyphs.push(piv);
      x += g.a + track;
    }
    x = Math.max(0.01, x - track);
    const off = align === "c" ? -x / 2 : align === "r" ? -x : 0;
    glyphs.forEach((p) => (p.position.x += off));
    grp.userData = { glyphs, w: x, h: cap, depth };
    return grp;
  }
  // a counting number: per slot one pivot for each digit, shown by the counter value each frame
  const ticks = [];
  function counter(final, { mat = "c", track = 0.01 } = {}) {
    const digits = String(final).replace(/[^0-9]/g, "").length;
    const dw = Math.max(...[..."0123456789"].map((d) => (GL[d] ? GL[d].a : 0.6)));
    const [y0, y1] = inkY(GL, "0123456789"), cap = y1 - y0, depth = 0.18 * cap;
    const grp = new THREE.Group(); const slots = [];
    const total = digits * dw + (digits - 1) * track;
    for (let s = 0; s < digits; s++) {
      const set = [];
      for (let d = 0; d <= 9; d++) {
        const ch = String(d), g = GL[ch]; if (!g) { set.push(null); continue; }
        const piv = new THREE.Group(); const m = new THREE.Mesh(glyphGeo(GL, ch, depth, 0.02), MAT[mat]); m.castShadow = true;
        m.position.set(-g.a / 2, -y0, -depth / 2 - 0.02); piv.add(m);
        piv.position.x = -total / 2 + s * (dw + track) + dw / 2; piv.visible = false; grp.add(piv); set.push(piv);
      }
      slots.push(set);
    }
    const st = { v: final };
    const show = () => { const n = Math.max(0, Math.round(st.v)), str = String(n).padStart(digits, " ");
      slots.forEach((set, i) => set.forEach((p, d) => { if (p) p.visible = str[i] === String(d); })); };
    ticks.push(show); show();
    grp.userData = { w: total, h: cap, depth, st };
    return grp;
  }

  // ---------- helpers
  const tl = gsap["timeline"]({ paused: true });     // seeked by hf-seek, never by a clock
  const rbox = (w, h, d, r = 0.06, mat = MAT.l) => { const m = new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 3, Math.min(r, w / 2, h / 2, d / 2)), mat); m.castShadow = true; m.receiveShadow = true; return m; };
  const cyl = (r, h, mat, seg = 72) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), mat); m.castShadow = true; m.receiveShadow = true; return m; };
  const boxOf = (o) => { o.updateWorldMatrix(true, true); return new THREE.Box3().setFromObject(o); };
  const fmax = (a) => Math.max(...a.map((x) => x.value));

  // ================================================================ station builders
  // each returns { hero, chart?, anim(at), opt } with everything at its settled state; anim registers the tweens
  const B = {};

  // 1 · stacked extruded headline, rising out of the lacquer floor while the key light sweeps across
  B.title = (c) => {
    const hero = new THREE.Group(); const lines = c.lines.map((ln) => word(ln, { mat: "m" }));
    const wmax = Math.max(...lines.map((l) => l.userData.w));
    let y = 0; const gap = 0.3;
    for (let i = lines.length - 1; i >= 0; i--) { const l = lines[i]; const s = Math.min(1.25, wmax / l.userData.w) > 1.0 && i === lines.length - 1 ? Math.min(1.25, wmax / l.userData.w) : 1; l.scale.setScalar(s); l.position.y = y; y += l.userData.h * s + gap; hero.add(l); }
    // the teaser on the floor: three slim ceramic bars on a lacquer base = the film's three recap figures as shares of net
    // sales (100 %, iPhone 50.4 %, gross margin 46.9 %); the middle one is the beat's vermilion object
    const chart = new THREE.Group();
    const T = c.teaser && c.teaser.length ? c.teaser : [1, 1, 1];
    const LB = 6.4, base = rbox(LB + 0.6, 0.16, T.length * 0.62 + 0.4, 0.06); base.position.y = 0.08; chart.add(base);
    const tbars = T.map((v, k) => {
      const L = Math.max(0.2, LB * Math.min(1, v));
      const bar = rbox(L, 0.26, 0.36, 0.08, k === 1 ? MAT.v : MAT.c); bar.position.set(-LB / 2 + L / 2, 0.16 + 0.13, (k - (T.length - 1) / 2) * 0.62); chart.add(bar);
      return { bar, L };
    });
    const lit = null;
    return { hero, chart, opt: P ? {} : { cx: W / 2, cy: 420, wantW: 0.5, maxH: 470 }, chartAt: P ? null : { x: W / 2, y: 820, w: 700, h: 140 }, anim: (t) => {
      tl.from(hero.scale, { y: 0.001, duration: 1.1, ease: "expo.out" }, t + 0.25);
      lines.forEach((l, i) => l.userData.glyphs.forEach((g, j) => tl.from(g.rotation, { x: 0.5, duration: 0.9, ease: "power3.out" }, t + 0.25 + (lines.length - 1 - i) * 0.08 + j * 0.025)));
      tl.from(chart.position, { z: chart.position.z + 2.2, duration: 0.9, ease: "expo.out" }, t + 0.7);
      tbars.forEach(({ bar, L }, k) => { tl.from(bar.scale, { x: 0.001, duration: 0.8, ease: "expo.out" }, t + 0.9 + k * 0.12); tl.from(bar.position, { x: -LB / 2, duration: 0.8, ease: "expo.out" }, t + 0.9 + k * 0.12); });
      sweeps.push([t + 0.2, 1.6]);
    } };
  };

  // 2 · ceramic numerals on a turntable that rotates 14° and settles; unit in metal; a row of blocks lights the true count
  B.number = (c) => {
    const hero = new THREE.Group();
    const num = counter(c.value.replace(/[^0-9]/g, "") || "0");
    const unit = word(c.unit || "", { mat: "m" });
    const nh = num.userData.h; unit.scale.setScalar(Math.min((nh * 0.3) / Math.max(0.3, unit.userData.h), (num.userData.w * 0.7) / unit.userData.w));
    const disc = new THREE.Group();
    const R = num.userData.w * 0.4 + 0.06;
    const top = cyl(R, 0.22, MAT.l, 96); top.position.y = 0.11; disc.add(top);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(R, 0.045, 12, 128), MAT.m); ring.rotation.x = Math.PI / 2; ring.position.y = 0.22; disc.add(ring);
    const turn = new THREE.Group(); turn.position.y = 0.22; turn.add(num); disc.add(turn);
    unit.position.set(0, 0, R + 0.45); hero.add(unit);      // the unit stands on the floor just in front of the disc
    hero.add(disc);
    const chart = new THREE.Group();
    const n = c.of === 10 ? 10 : 100, cols = 10, rows = n / 10, sz = 0.36, gp = 0.1;
    const litMat = M.ceramic(); const blocks = [];
    for (let i = 0; i < n; i++) {
      const r = Math.floor(i / cols), cc = i % cols, isLit = (rows - 1 - r) * cols + cc < c.lit;     // counted from the front-left block
      const b = rbox(sz, sz * 0.62, sz, 0.05, isLit ? litMat : MAT.c);
      b.position.set((cc - (cols - 1) / 2) * (sz + gp), sz * 0.31, (r - (rows - 1) / 2) * (sz + gp));
      chart.add(b); blocks.push({ b, r, cc, isLit, y0: b.position.y });
    }
    return { hero, chart, opt: P ? { cx: 540, wantW: 0.89 } : {}, anim: (t) => {
      tl.from(disc.scale, { x: 0.001, z: 0.001, duration: 0.7, ease: "expo.out" }, t + 0.2);
      tl.from(turn.position, { y: -nh * 1.2, duration: 0.8, ease: "expo.out" }, t + 0.35);
      tl.from(unit.rotation, { x: -Math.PI / 2, duration: 0.6, ease: "back.out(1.5)" }, t + 1.2);
      tl.fromTo(turn.rotation, { y: -14 * DEG }, { y: 0, duration: 1.6, ease: "back.out(1.3)", immediateRender: true }, t + 0.35);
      tl.fromTo(num.userData.st, { v: 0 }, { v: Number(c.value.replace(/[^0-9]/g, "")) || 0, duration: 1.3, ease: "power2.out", immediateRender: true }, t + 0.4);
      blocks.forEach(({ b, r, cc }) => tl.from(b.position, { y: -sz, duration: 0.4, ease: "back.out(1.8)" }, t + 0.6 + (r + cc) * 0.025));
      blocks.filter((x) => x.isLit).forEach(({ b, y0 }, k) => tl.to(b.position, { y: y0 + 0.14, duration: 0.3, ease: "back.out(2)" }, t + 1.7 + k * 0.08));
      tl.to(litMat.color, { r: 0.761, g: 0.0561, b: 0.0242, duration: 0.5, ease: "power2.out" }, t + 1.7);       // #e2432a in linear
      tl.to(litMat, { clearcoatRoughness: 0.06, roughness: 0.26, duration: 0.5 }, t + 1.7);
      ticks.push((tt) => { disc.rotation.y = tt > t ? (tt - t) * 0.035 : 0; });      // the turntable keeps turning, slowly
    } };
  };

  // 3 · two pedestals in true ratio, rising at the same speed (the shorter stops first); the taller one vermilion
  B.compare = (c) => {
    const hero = new THREE.Group(); const sides = [c.left, c.right];
    const vmax = Math.max(sides[0].value, sides[1].value), HMAX = 4.6, R = 0.95, X0 = 1.55;
    const peds = sides.map((s, i) => {
      const h = HMAX * (s.value / vmax), g = new THREE.Group(); g.position.x = (i ? 1 : -1) * X0;
      const base = cyl(R * 1.18, 0.12, MAT.l, 96); base.position.y = 0.06; g.add(base);
      const col = cyl(R, 1, i === c.hi ? MAT.v : MAT.c, 96); col.scale.y = h; col.position.y = 0.12 + h / 2; g.add(col);
      const lab = word(s.show || s.label, { mat: i === c.hi ? "m" : "c" }); const sc = Math.min(0.9, (2 * R * 1.25) / lab.userData.w); lab.scale.setScalar(sc);
      lab.position.set(0, 0.12 + h + 0.12, 0); g.add(lab);
      hero.add(g); return { g, col, lab, h };
    });
    // each pedestal's label stands on its base, facing the camera; the floor plate carries the change between them
    sides.forEach((s, i) => {
      const lb = word(s.label, { mat: "c" }); lb.scale.setScalar(Math.min(0.44 / Math.max(0.3, lb.userData.h), (R * 2.0) / lb.userData.w));
      const pw = lb.userData.w * lb.scale.x + 0.4;
      const plq = rbox(pw, 0.74, 0.1, 0.05, MAT.l); plq.position.set((i ? 1 : -1) * X0, 0.13 + 0.37, R * 1.18 + 0.06); hero.add(plq);
      lb.position.set((i ? 1 : -1) * X0, 0.28, R * 1.18 + 0.14); hero.add(lb);
    });
    const chart = new THREE.Group();
    const d = sides[1].value / sides[0].value - 1;
    const delta = c.delta || ((d >= 0 ? "+" : "") + Math.round(d * 100) + "%");
    const plate = rbox(3.6, 0.3, 1.2, 0.08, MAT.l); plate.position.y = 0.15; chart.add(plate);
    const lip = rbox(3.62, 0.03, 1.22, 0.01, MAT.m); lip.position.y = 0.3; chart.add(lip);
    const dt = word([[delta, "v"]]); dt.scale.setScalar(Math.min(0.75 / Math.max(0.3, dt.userData.h), 3.0 / dt.userData.w)); dt.position.set(0, 0.31, 0.05); chart.add(dt);
    return { hero, chart, anim: (t) => {
      const p = { h: 0 }; const t0 = t + 0.35, speed = HMAX / 1.5;
      tl.fromTo(p, { h: 0 }, { h: HMAX, duration: HMAX / speed, ease: "none", immediateRender: true }, t0);
      ticks.push(() => { peds.forEach(({ col, lab, h }) => { const hh = Math.max(0.001, Math.min(p.h, h)); col.scale.y = hh; col.position.y = 0.12 + hh / 2; lab.position.y = 0.12 + hh + 0.12; }); });
      peds.forEach(({ lab }) => tl.from(lab.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(1.8)" }, t0 + 0.05));
      tl.from(chart.position, { z: chart.position.z + 1.6, duration: 0.8, ease: "expo.out" }, t + 0.5);
      tl.from(chart.scale, { x: 0.001, duration: 0.7, ease: "expo.out" }, t + 0.5);
      tl.from(dt.rotation, { x: -Math.PI / 2, duration: 0.6, ease: "back.out(1.6)" }, t + 0.35 + 1.5);     // the change flips up when both pedestals stop
    } };
  };

  // 4 · lying bars on the floor, receding in depth, lengths in true ratio; labels on their near faces; camera 35° down
  B.rank = (c) => {
    const hero = new THREE.Group(); const items = c.items; const vmax = fmax(items), LMAX = 7.2, ROW = 4.4, TH = 0.8, DP = 1.1;
    const rows = items.map((it, i) => {
      const g = new THREE.Group(); g.position.z = -i * ROW;
      const L = Math.max(0.12, LMAX * (it.value / vmax));
      const track = rbox(LMAX, 0.08, DP * 0.96, 0.03, MAT.d); track.position.set(LMAX / 2, 0.16, 0); g.add(track);      // the full-length slot each bar runs in
      const bar = rbox(L, TH, DP, 0.1, i === 0 ? MAT.v : MAT.c); bar.position.set(L / 2, 0.2 + TH / 2, 0); g.add(bar);
      const lab = word(it.label, { mat: "c", align: "r" }); lab.scale.setScalar(0.86 / Math.max(0.5, lab.userData.h)); lab.rotation.x = -0.75; lab.position.set(-0.3, 0.02, DP / 2 - 0.1); g.add(lab);
      const val = word(it.show, { mat: "c", align: "l" }); val.scale.setScalar(0.74 / Math.max(0.3, val.userData.h)); val.rotation.x = -0.75; val.position.set(L + 0.3, 0.24, 0.15); g.add(val);
      hero.add(g); return { g, bar, lab, val, L };
    });
    const deck = new THREE.Group(); hero.add(deck);
    const DW = LMAX + 7.6, DD = items.length * ROW + 0.6;
    const slab = rbox(DW, 0.16, DD, 0.05, MAT.deck); slab.position.set(LMAX / 2 - 1.4, 0.08, -(items.length - 1) * ROW / 2); slab.castShadow = false; deck.add(slab);
    const edge = rbox(DW, 0.03, 0.05, 0.01, MAT.m); edge.position.set(LMAX / 2 - 1.4, 0.16, DD / 2 - (items.length - 1) * ROW / 2); deck.add(edge);
    rows.forEach(({ g }) => (g.position.y = 0.16));
    return { hero, chart: null, opt: { el: 46, cx: P ? 505 : W / 2, cy: P ? 860 : 480, wantW: P ? 0.86 : 0.6, maxH: P ? 880 : 760 }, anim: (t) => {
      rows.forEach(({ bar, val, lab, L }, i) => {
        const t0 = t + 0.35 + i * 0.12;
        tl.from(bar.scale, { x: 0.001, duration: 0.9, ease: "expo.out" }, t0);
        tl.from(bar.position, { x: 0, duration: 0.9, ease: "expo.out" }, t0);
        tl.from(val.position, { x: 0.3, duration: 0.9, ease: "expo.out" }, t0);
        tl.from(val.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.5, ease: "back.out(1.6)" }, t0 + 0.4);
        lab.userData.glyphs.forEach((g, j) => tl.from(g.rotation, { x: -Math.PI / 2, duration: 0.5, ease: "back.out(1.4)" }, t0 + j * 0.03));
      });
    } };
  };

  // 5 · a thick ring on a tilted stand; the true fraction is a vermilion segment that slides 0.3 units out of the ring
  B.share = (c) => {
    const hero = new THREE.Group(); const R = 2.2, TUBE = 0.46, f = Math.max(0.02, Math.min(0.98, c.frac));
    const stand = new THREE.Group();
    const base = rbox(2.6, 0.22, 1.5, 0.08, MAT.l); base.position.y = 0.11; stand.add(base);
    const post = cyl(0.12, 1.1, MAT.s, 32); post.position.y = 0.22 + 0.55; stand.add(post);
    hero.add(stand);
    const ringG = new THREE.Group(); ringG.position.y = 0.22 + 1.1 + R + TUBE * 0.4; ringG.rotation.x = -12 * DEG; hero.add(ringG);
    const spin = new THREE.Group(); ringG.add(spin);
    const a0 = Math.PI / 2;     // the vermilion segment starts at 12 o'clock and runs clockwise
    const grey = new THREE.Mesh(new THREE.TorusGeometry(R, TUBE, 28, 160, Math.PI * 2 * (1 - f) - 0.05), MAT.c); grey.castShadow = true;
    grey.rotation.z = a0 + 0.025; spin.add(grey);
    const segG = new THREE.Group(); spin.add(segG);
    const seg = new THREE.Mesh(new THREE.TorusGeometry(R, TUBE, 28, 160, Math.PI * 2 * f - 0.05), MAT.v); seg.castShadow = true;
    seg.rotation.z = a0 - Math.PI * 2 * f + 0.025; segG.add(seg);
    const mid = a0 - Math.PI * f;
    const out = new THREE.Vector3(Math.cos(mid), Math.sin(mid), 0).multiplyScalar(0.3);
    const num = word([[c.show, "c"]]); num.scale.setScalar((R - TUBE) * 1.45 / num.userData.w); num.position.y = -num.userData.h * num.scale.x / 2; ringG.add(num);
    const chart = new THREE.Group();
    if (c.label) {
      const plinth = rbox(5.2, 0.34, 1.1, 0.08, MAT.l); plinth.position.y = 0.17; chart.add(plinth);
      const lb = word(c.label, { mat: "m" }); lb.scale.setScalar(Math.min(0.62, 4.6 / lb.userData.w)); lb.position.set(0, 0.34, 0.15); chart.add(lb);
    } else { const plinth = rbox(5.2, 0.34, 1.1, 0.08, MAT.l); plinth.position.y = 0.17; chart.add(plinth); }
    return { hero, chart, opt: { wantW: P ? 0.74 : 0.36 }, anim: (t) => {
      tl.from(stand.scale, { x: 0.001, z: 0.001, duration: 0.6, ease: "expo.out" }, t + 0.2);
      tl.from(ringG.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.9, ease: "expo.out" }, t + 0.3);
      tl.from(spin.rotation, { z: -Math.PI * 0.9, duration: 1.3, ease: "expo.out" }, t + 0.3);
      tl.to(segG.position, { x: out.x, y: out.y, duration: 0.6, ease: "back.out(2)" }, t + 1.25);
      tl.from(num.rotation, { x: -Math.PI / 2, duration: 0.7, ease: "back.out(1.4)" }, t + 1.3);
      tl.from(num.scale, { y: 0.001, duration: 0.5, ease: "expo.out" }, t + 1.3);
      tl.from(chart.position, { z: chart.position.z + 1.8, duration: 0.8, ease: "expo.out" }, t + 0.6);
      ticks.push((tt) => { ringG.rotation.y = tt > t ? Math.sin((tt - t) * 0.5) * 0.05 : 0; });
    } };
  };

  // 6 · stepping columns on a diagonal, heights in true ratio; a metal sphere hops from top to top, year by year
  B.timeline = (c) => {
    const hero = new THREE.Group(); const items = c.items; const vmax = fmax(items), HMAX = 4.2, SX = 2.25, SZ = 1.0, CW = 1.05;
    const n = items.length;
    const cols = items.map((it, i) => {
      const h = HMAX * (it.value / vmax), g = new THREE.Group();
      g.position.set((i - (n - 1) / 2) * SX, 0, (i - (n - 1) / 2) * SZ);
      const col = rbox(CW, h, CW, 0.06, i === n - 1 ? MAT.v : MAT.c); col.position.y = h / 2; g.add(col);
      const val = word(it.show, { mat: "m" }); val.scale.setScalar(Math.min(0.62 / Math.max(0.3, val.userData.h), (SX * 0.92) / val.userData.w)); val.position.set(0, h + 0.62, 0); g.add(val);
      // the year on a small lacquer plaque standing on the floor in front of its column
      const yr = word(it.label, { mat: "c" }); yr.scale.setScalar(Math.min(0.46 / Math.max(0.3, yr.userData.h), (CW * 1.45) / yr.userData.w));
      const plq = new THREE.Group(); plq.position.set(0, 0, CW / 2 + 0.9); plq.rotation.x = -0.32; g.add(plq);
      const pb = rbox(CW * 1.7, 0.72, 0.12, 0.04, MAT.l); pb.position.y = 0.36; plq.add(pb);
      yr.position.set(0, 0.13, 0.08); plq.add(yr);
      hero.add(g); return { g, col, val, yr, h };
    });
    const ball = new THREE.Mesh(new THREE.SphereGeometry(0.24, 48, 32), MAT.m); ball.castShadow = true; hero.add(ball);
    return { hero, chart: null, opt: { el: 16, cy: P ? 800 : 490, wantW: P ? 0.84 : 0.62, maxH: P ? 1000 : 740 }, anim: (t) => {
      const lands = [];
      cols.forEach(({ col, val, yr, h }, i) => {
        const t0 = t + 0.3 + i * 0.12;
        tl.from(col.scale, { y: 0.001, duration: 0.8, ease: "expo.out" }, t0);
        tl.from(col.position, { y: 0, duration: 0.8, ease: "expo.out" }, t0);
        tl.from(yr.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(1.6)" }, t0 + 0.2);
        const tl_ = t + 1.2 + i * 0.42; lands.push(tl_);
        tl.from(val.rotation, { x: -Math.PI / 2, duration: 0.45, ease: "back.out(1.8)" }, tl_);
        tl.from(val.position, { y: h + 0.2, duration: 0.45, ease: "back.out(1.8)" }, tl_);
      });
      const top = (i) => { const g = cols[i].g; return new THREE.Vector3(g.position.x - CW * 0.28, cols[i].h + 0.24, g.position.z + CW * 0.18); };
      ticks.push((tt) => {
        if (tt < lands[0] - 0.42) { ball.visible = false; return; }
        ball.visible = true;
        let k = 0; while (k + 1 < lands.length && tt >= lands[k + 1]) k++;
        if (tt < lands[0]) { const u = (tt - (lands[0] - 0.42)) / 0.42; const p = top(0); ball.position.set(p.x, p.y + 2.2 * (1 - u) * (1 - u), p.z); ball.rotation.z = 0; return; }
        if (k + 1 >= lands.length) { const p = top(k); ball.position.copy(p); return; }
        const u = Math.min(1, (tt - lands[k]) / (lands[k + 1] - lands[k]));
        const a = top(k), b = top(k + 1);
        ball.position.lerpVectors(a, b, u); ball.position.y += 0.9 * 4 * u * (1 - u);
        ball.rotation.z = -(k + u) * 2.2; ball.rotation.x = (k + u) * 1.4;
      });
    } };
  };

  // 7 · a smoked-glass slab on the floor; the sentence is light type inside the slab plane, one word vermilion
  B.statement = (c) => {
    const hero = new THREE.Group();
    const lineMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xf4f0e6).multiplyScalar(1.15), toneMapped: false, side: THREE.DoubleSide });
    const emMat = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xff4a2e), toneMapped: false, side: THREE.DoubleSide });
    const lines = c.lines.map((s) => {
      const runs = []; let em = false;
      for (const part of String(s).split(/(\*)/)) { if (part === "*") { em = !em; continue; } if (part) runs.push([part, em ? emMat : lineMat]); }
      return word(runs, { tab: GL2, flat: true, track: 0.02 });
    });
    const tw = Math.max(...lines.map((l) => l.userData.w)), lh = Math.max(...lines.map((l) => l.userData.h));
    const SW = tw * 1.0 + 1.2, LH = lh * 1.6, SH = lines.length * LH + 1.0, SD = 0.22;
    const slabG = new THREE.Group(); hero.add(slabG);
    const foot = rbox(SW + 0.3, 0.2, 0.9, 0.06, MAT.l); foot.position.y = 0.1; hero.add(foot);
    const slab = new THREE.Mesh(new RoundedBoxGeometry(SW, SH, SD, 3, 0.05), M.glass()); slab.position.y = 0.2 + SH / 2; slab.renderOrder = 2; slabG.add(slab);
    const edge = rbox(SW, 0.035, SD + 0.02, 0.01, MAT.m); edge.position.y = 0.2 + SH; slabG.add(edge);
    const back = new THREE.Mesh(new THREE.PlaneGeometry(SW - 0.08, SH - 0.08), new THREE.MeshPhysicalMaterial({ color: 0x0c0e12, roughness: 0.3, transparent: true, opacity: 0.55 }));
    back.position.set(0, 0.2 + SH / 2, -SD / 2 + 0.01); slabG.add(back);
    lines.forEach((l, i) => { l.position.set(-tw / 2 + l.userData.w / 2 - (tw - l.userData.w) / 2 * 0 , 0.2 + SH - 0.5 - (i + 1) * LH + (LH - lh) / 2, 0.0); l.position.x = 0; slabG.add(l); });
    let chart = null; const bars = [];
    if (c.bars && c.bars.length) {
      // a small standing bar board in front of the slab: label above, bar below, true length out of 100
      chart = new THREE.Group(); const LMAX = 5.6, RH = 1.15, nb = c.bars.length;
      const stand = rbox(LMAX + 0.6, 0.12, 0.7, 0.04, MAT.l); stand.position.y = 0.06; chart.add(stand);
      c.bars.forEach((it, i) => {
        const g = new THREE.Group(); g.position.y = 0.2 + (nb - 1 - i) * RH * 1.12;
        const track = rbox(LMAX, 0.34, 0.16, 0.05, MAT.d); track.position.set(0, 0.17, 0); g.add(track);
        const L = LMAX * Math.min(1, it.value / 100);
        const bar = rbox(L, 0.38, 0.24, 0.06, i === nb - 1 ? MAT.m : MAT.c); bar.position.set(-LMAX / 2 + L / 2, 0.19, 0.05); g.add(bar);
        const lab = word(it.label + " " + it.show, { mat: "c", align: "l" }); lab.scale.setScalar(Math.min(0.56 / Math.max(0.3, lab.userData.h), LMAX / lab.userData.w));
        lab.position.set(-LMAX / 2, 0.46, 0.05); g.add(lab);
        chart.add(g); bars.push({ bar, lab, LMAX });
      });
    }
    return { hero, chart, opt: { wantW: P ? 0.8 : 0.42 }, anim: (t) => {
      tl.from(slabG.position, { y: -(SH + 0.4), duration: 1.0, ease: "expo.out" }, t + 0.2);
      tl.from(foot.scale, { x: 0.001, duration: 0.6, ease: "expo.out" }, t + 0.15);
      let k = 0;
      lines.forEach((l) => l.userData.glyphs.forEach((g) => { tl.from(g.scale, { x: 0.001, y: 0.001, duration: 0.3, ease: "back.out(1.7)" }, t + 0.9 + k * 0.035); k++; }));
      tl.from(emMat.color, { r: 1.15, g: 1.12, b: 1.05, duration: 0.5, ease: "power2.out" }, t + 0.9 + k * 0.035 + 0.15);
      bars.forEach(({ bar, lab }, i) => {
        tl.from(bar.scale, { x: 0.001, duration: 0.9, ease: "expo.out" }, t + 1.0 + i * 0.15);
        tl.from(bar.position, { x: -bars[i].LMAX / 2, duration: 0.9, ease: "expo.out" }, t + 1.0 + i * 0.15);
        tl.from(lab.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.4, ease: "back.out(1.6)" }, t + 1.2 + i * 0.15);
      });
    } };
  };

  // 8 · the recap: three ceramic numerals on lacquer plinths with their labels on the plinth faces; stepped back and up in
  // 9:16 (they stack on screen), side by side in 16:9; the beat's highlight (c.hi) in vermilion. The camera pulls back so the
  // earlier stations stand small in depth behind them.
  B.outro = (c) => {
    const hero = new THREE.Group(); const n = c.items.length; const plinths = [];
    const PD = 1.5;
    const xs = []; { let acc = 0; const ws = c.items.map((s) => { const p = word([[s, "c"]], { track: -0.035 }); return p.userData.w / p.userData.h + 0.2; });
      const tot = ws.reduce((a, b) => a + b, 0) + 0.22 * (ws.length - 1);
      ws.forEach((w) => { xs.push(-tot / 2 + acc + w / 2); acc += w + 0.22; }); }
    const maxNW = Math.max(...c.items.map((s) => { const p = word([[s, "c"]], { track: -0.035 }); return p.userData.w / p.userData.h * 1.3; }));
    c.items.forEach((s, i) => {
      const g = new THREE.Group();
      const k = n - 1 - i;      // 9:16: the first figure stands at the back (top of the stack)
      const grow = P ? 1 + 0.1 * k : 1;      // back rows a little larger, so perspective leaves every figure the same size on screen
      const NH = (P ? 1.3 : 1.0) * grow;
      const probe = word([[s, "c"]], { track: -0.035 }); const nw = probe.userData.w * (NH / probe.userData.h);
      const PW_ = P ? (maxNW + 0.6) * grow : nw + 0.2;
      const ph = P ? 0.7 + k * (NH + 0.62) : 0.75;
      if (P) g.position.set(0, 0, -k * 1.7); else g.position.set(xs[i], 0, 0);
      const pl = rbox(PW_, ph, PD, 0.06, MAT.l); pl.position.y = ph / 2; g.add(pl);
      const lip = rbox(PW_ + 0.02, 0.04, PD + 0.02, 0.01, MAT.m); lip.position.y = ph; g.add(lip);
      const num = word([[s, i === c.hi ? "v" : "c"]], { track: -0.035 }); num.scale.setScalar(Math.min((PW_ * 0.95) / num.userData.w, NH / num.userData.h)); num.position.set(0, ph + 0.03, 0); g.add(num);
      if (c.labels && c.labels[i]) {
        const lb = word(c.labels[i], { mat: "m" }); lb.scale.setScalar(Math.min(Math.min(0.36 * grow, ph * 0.45) / Math.max(0.3, lb.userData.h), (PW_ * 0.8) / lb.userData.w));
        lb.position.set(0, Math.max(0.08, ph - 0.12 - lb.userData.h * lb.scale.x), PD / 2 + 0.02); g.add(lb);     // just under the lip, clear of the figure in front
      }
      hero.add(g); plinths.push({ g, num, ph });
    });
    return { hero, chart: null, opt: P ? { cx: 540, cy: 920, wantW: 0.86, maxH: 880, el: 10 } : { cx: W / 2, cy: 560, wantW: 0.985, maxH: 660, el: 10 }, anim: (t) => {
      plinths.forEach(({ g, num, ph }, i) => {
        tl.from(g.position, { y: -ph - 0.1, duration: 0.8, ease: "expo.out" }, t + 0.45 + i * 0.14);
        tl.from(num.position, { y: ph + 1.4, duration: 0.6, ease: "bounce.out" }, t + 0.9 + i * 0.14);
      });
    } };
  };

  // ================================================================ layout + camera fitting
  const N = CFG.beats.length;
  // stations step to the right and a little forward: each move is mostly a sideways truck, so mid-move both the outgoing
  // and the incoming hero are in a (widened) frame, and at rest neither neighbour is
  const DXL = CFG.stepX || 24, DZL = CFG.stepZ || 10;
  const origin = (i) => new THREE.Vector3(i * DXL, 0, i * DZL);
  const COMP = P
    ? { cx: 510, cy: 760, wantW: 0.78, maxH: 820, chartX: 510, chartY: 1175, chartW: 760, chartH: 300, el: 9 }
    : { cx: 680, cy: 460, wantW: 0.42, maxH: 0.66, chartX: 1390, chartY: 760, chartW: 720, chartH: 440, el: 9 };
  const toPx = (v) => (v <= 1.5 ? v * (P ? W : W) : v);
  const toPy = (v) => (v <= 1.5 ? v * H : v);

  function poseCam(q) {
    const ce = Math.cos(q.el);
    camera.position.set(q.tx + q.d * Math.sin(q.az) * ce, q.ty + q.d * Math.sin(q.el), q.tz + q.d * Math.cos(q.az) * ce);
    camera.up.set(0, 1, 0); camera.lookAt(q.tx, q.ty, q.tz);
    camera.setViewOffset(W, H, q.ox, q.oy, W, H);
    camera.updateProjectionMatrix(); camera.updateMatrixWorld(true);
  }
  function projBox(box) {
    let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
    for (let k = 0; k < 8; k++) {
      if (box.pts) tmpV.copy(box.pts[k]).project(camera);      // an oriented box (corners given)
      else tmpV.set(k & 1 ? box.max.x : box.min.x, k & 2 ? box.max.y : box.min.y, k & 4 ? box.max.z : box.min.z).project(camera);
      const px = (tmpV.x + 1) / 2 * W, py = (1 - tmpV.y) / 2 * H;
      x0 = Math.min(x0, px); x1 = Math.max(x1, px); y0 = Math.min(y0, py); y1 = Math.max(y1, py);
    }
    return { x0, x1, y0, y1, w: x1 - x0, h: y1 - y0, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2 };
  }
  // fit: the box's projected width = wantW px (or its height = maxH px, whichever binds), its projected centre at (cx, cy)
  function fitBox(box, o) {
    const ctr = box.getCenter(new THREE.Vector3()), size = box.getSize(new THREE.Vector3());
    const hf = Math.tan((FOV * DEG) / 2) * (W / H);
    const q = { tx: ctr.x, ty: ctr.y, tz: ctr.z, az: (o.az || 0) * DEG, el: o.el * DEG, ox: W / 2 - o.cx, oy: H / 2 - o.cy, d: size.x / (o.wantW / W * 2 * hf) + size.z / 2 };
    for (let it = 0; it < 8; it++) {
      poseCam(q); const r = projBox(box);
      const s = Math.max(r.w / o.wantW, r.h / o.maxH);
      q.d *= Math.pow(s, 0.9);
      poseCam(q); const r2 = projBox(box);
      // nudge the target so the projected box (not just its centre point) is centred where asked
      const wpp = (2 * q.d * Math.tan((FOV * DEG) / 2)) / H;
      const right = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 0), up = new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld, 1);
      const dx = (r2.cx - o.cx) * wpp, dy = (r2.cy - o.cy) * wpp;
      q.tx += right.x * dx - up.x * dy; q.ty += right.y * dx - up.y * dy; q.tz += right.z * dx - up.z * dy;
    }
    // clamp: nothing of the group may cross x 60…1020 (9:16)
    if (P) { for (let it = 0; it < 4; it++) { poseCam(q); const r = projBox(box); if (r.x0 >= 60 && r.x1 <= W - 60) break; q.d *= Math.max(r.w / (W - 120), 1.02); } }
    return q;
  }
  const ray = new THREE.Raycaster(), floorPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -FLOOR_Y);
  function floorAt(px, py) { ray.setFromCamera(new THREE.Vector2(px / W * 2 - 1, -(py / H * 2 - 1)), camera); const p = new THREE.Vector3(); return ray.ray.intersectPlane(floorPlane, p) ? p : null; }

  // focus on the middle of the hero group's depth range; the aperture is opened only as far as keeps every corner of the
  // group (and its chart) under one pixel of blur, so no label or numeral is ever soft when settled
  const AP0 = CFG.aperture || 0.0011;
  function focusOf(q, boxes) {
    poseCam(q);
    const fwd = new THREE.Vector3(); camera.getWorldDirection(fwd);
    let lo = Infinity, hi = -Infinity;
    for (const box of boxes) for (let k = 0; k < 8; k++) {
      tmpV.set(k & 1 ? box.max.x : box.min.x, k & 2 ? box.max.y : box.min.y, k & 4 ? box.max.z : box.min.z).sub(camera.position);
      const dpt = tmpV.dot(fwd); lo = Math.min(lo, dpt); hi = Math.max(hi, dpt);
    }
    q.f = (lo + hi) / 2;
    const half = Math.max(0.05, (hi - lo) / 2);
    q.ap = Math.min(1, 0.0008 / (half * AP0));
  }
  const stations = [];
  CFG.beats.forEach((c, i) => {
    const G = new THREE.Group(); G.position.copy(origin(i)); scene.add(G);
    const built = (B[c.kind] || B.title)(c);
    G.add(built.hero);
    stations.push({ c, G, built });
  });

  // camera pose per station (A = arrival, B = end of the hold: a slow 0.4° orbit and a 3 % dolly-in)
  const poses = stations.map(({ c, G, built }, i) => {
    if (c.kind === "outro") return null;
    const o = { ...COMP, ...(built.opt || {}) };
    if (!built.chart && !(built.opt && built.opt.cx)) o.cx = P ? 510 : W / 2;
    o.wantW = toPx(o.wantW); o.maxH = toPy(o.maxH);
    let hbox = boxOf(built.hero);
    if (hbox.isEmpty() || !isFinite(hbox.min.x)) hbox = new THREE.Box3(new THREE.Vector3(G.position.x - 2, 0, G.position.z - 0.5), new THREE.Vector3(G.position.x + 2, 2, G.position.z + 0.5));
    const q = fitBox(hbox, o);
    if (built.chart) {
      // the chart object stands on the floor under the hero: put it where the screen point (chartX, chartY) meets the floor,
      // in front of the hero, sized to chartW × chartH px
      const CA = built.chartAt ? { chartX: built.chartAt.x, chartY: built.chartAt.y, chartW: built.chartAt.w, chartH: built.chartAt.h } : COMP;
      poseCam(q);
      const hb = boxOf(built.hero);
      let p = floorAt(CA.chartX, CA.chartY) || new THREE.Vector3(G.position.x, 0, hb.max.z + 2);
      p.z = Math.max(p.z, hb.max.z + 0.8);
      const ch = built.chart; G.add(ch);
      ch.position.copy(G.worldToLocal(p.clone()));
      for (let it = 0; it < 4; it++) {
        const r = projBox(boxOf(ch));
        const s = Math.min(CA.chartW / r.w, CA.chartH / r.h);
        ch.scale.multiplyScalar(s);
        const r2 = projBox(boxOf(ch));
        const p2 = floorAt(CA.chartX, CA.chartY + (CA.chartY - r2.cy) * 0.0) || p;
        const shiftY = CA.chartY - r2.cy;
        const p3 = floorAt(CA.chartX - (r2.cx - CA.chartX), CA.chartY + shiftY) || p2;
        p3.z = Math.max(p3.z, hb.max.z + 0.8);
        ch.position.copy(G.worldToLocal(p3.clone()));
      }
      const hr = projBox(hb), lim = 1360;
      for (let it = 0; P && it < 6; it++) {
        const r = projBox(boxOf(ch));
        if (r.y0 >= hr.y1 + 14 && r.y1 <= lim) break;
        if (r.y1 > lim || r.h > lim - hr.y1 - 14) ch.scale.multiplyScalar(Math.max(0.6, Math.min(0.97, (lim - hr.y1 - 14) / r.h)));
        const r2 = projBox(boxOf(ch)); const want = Math.max(hr.y1 + 14 + r2.h / 2, Math.min(r2.cy, lim - r2.h / 2));
        const pp = floorAt(CA.chartX - (r2.cx - CA.chartX), r2.cy + (want - r2.cy) + (CA.chartY - r2.cy) * 0) ;
        if (pp) { const cur = floorAt(r2.cx, r2.cy); if (cur) ch.position.add(G.worldToLocal(pp.clone()).sub(G.worldToLocal(cur.clone()))); }
      }
    }
    const dir = i % 2 ? 1 : -1;
    focusOf(q, built.chart ? [boxOf(built.hero), boxOf(built.chart)] : [boxOf(built.hero)]);
    const qb = { ...q, az: q.az + dir * 0.4 * DEG, d: q.d * 0.97, f: q.f * 0.97 };
    return { a: q, b: qb };
  });
  // showroom wall behind every station: tall lacquer fins with a thin light line on each front edge (picture, not empty ground,
  // above the hero; their reflections run down the floor)
  const finLine = new THREE.MeshBasicMaterial({ color: new THREE.Color(0xffe6c8).multiplyScalar(0.55), toneMapped: false });
  const finLineCool = new THREE.MeshBasicMaterial({ color: new THREE.Color(0x9cc2ff).multiplyScalar(0.42), toneMapped: false });
  const walls = [];
  stations.forEach(({ c, G, built }, i) => {
    if (c.kind === "outro") return;
    const hb = boxOf(built.hero), size = hb.getSize(new THREE.Vector3()), ctr = hb.getCenter(new THREE.Vector3());
    const wall = new THREE.Group(); const span = Math.max(size.x * 1.6, 8), n = 10, hgt = Math.max(size.y * 2.0, 7);
    const gap = Math.max(4, size.x * 0.45), half = size.x / 2 * (1 + gap / 40) + 0.3;
    for (let k = 0; k < n; k++) {
      const x = (k / (n - 1) - 0.5) * span;
      const y0 = Math.abs(x) < half ? Math.min(hgt - 1, size.y * 1.25 + 0.8) : 0;      // behind the hero a fin starts above it
      const h = hgt - y0;
      const fin = rbox(0.34, h, 0.5, 0.04, MAT.l); fin.castShadow = false; fin.position.set(x, y0 + h / 2, 0); wall.add(fin);
      if (y0 === 0) {      // the light line runs up the lower part only, so the kicker band at the top stays dark behind its type
        const lh = Math.min(h * 0.62, size.y * 1.15 + 0.6);
        const ln = new THREE.Mesh(new THREE.BoxGeometry(0.035, lh, 0.02), k % 4 === 3 ? finLineCool : finLine); ln.position.set(x, lh / 2, 0.26); wall.add(ln);
      }
    }
    wall.position.copy(G.worldToLocal(new THREE.Vector3(ctr.x, 0, hb.min.z - gap)));
    G.add(wall);
    const nx = CFG.beats[i + 1];
    const v0 = i ? c.t : -1, v1 = nx ? nx.t + 0.4 : D + 1;
    walls.push(wall);
    const oT = (CFG.beats.find((b) => b.kind === "outro") || { t: D + 9 }).t;
    ticks.push((t) => { wall.visible = (t >= v0 && t <= v1 && !(nx && nx.kind === "outro" && t > nx.t - 0.5 && t < nx.t + 0.2)) || t >= oT + 0.2; });     // every wall lights up again for the overview
  });

  // a soft floor-to-wall light pool behind every hero: a radial glow on the wall behind the fins and its spill on the floor
  // (radius ≈ 1.6 × the hero's width, peak ≈ #3a3e4a once graded)
  const poolTex = (() => { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
    const gr = g.createRadialGradient(128, 128, 0, 128, 128, 128); gr.addColorStop(0, "rgba(255,255,255,1)"); gr.addColorStop(0.45, "rgba(255,255,255,0.55)"); gr.addColorStop(1, "rgba(255,255,255,0)");
    g.fillStyle = gr; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c); })();
  const POOL = new THREE.Color(CFG.pool || "#3a3e4a").multiplyScalar(CFG.poolGain || 0.9);
  const poolMat = () => new THREE.MeshBasicMaterial({ map: poolTex, color: POOL, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, fog: false });
  stations.forEach(({ c, G, built }) => {
    const hb = boxOf(built.hero), size = hb.getSize(new THREE.Vector3()), ctr = hb.getCenter(new THREE.Vector3());
    const R = Math.max(size.x, 4) * 1.6;
    const gap = Math.max(4, size.x * 0.45);
    const wallP = new THREE.Mesh(new THREE.PlaneGeometry(R * 2, R * 1.5), poolMat());
    wallP.position.copy(G.worldToLocal(new THREE.Vector3(ctr.x, R * 0.42, hb.min.z - gap - 0.5))); G.add(wallP);
    const floorP = new THREE.Mesh(new THREE.PlaneGeometry(R * 2, R * 1.4), poolMat()); floorP.rotation.x = -Math.PI / 2;
    floorP.position.copy(G.worldToLocal(new THREE.Vector3(ctr.x, 0.012, hb.min.z - gap * 0.35))); G.add(floorP);
  });

  // outro: the camera looks back along the set (towards the centroid of the earlier stations), so they stand small in depth
  // behind the recap plinths
  stations.forEach(({ c, G, built }, i) => {
    if (c.kind !== "outro") return;
    const cen = new THREE.Vector3(); let m = 0; stations.forEach((s, j) => { if (j !== i) { cen.add(s.G.position); m++; } }); if (m) cen.divideScalar(m);
    const az = Math.atan2(G.position.x - cen.x, G.position.z - cen.z) / DEG;
    // the plinths face the camera squarely; fit to their oriented box (an axis-aligned box of a turned group is too big)
    const lb = boxOf(built.hero);
    built.hero.rotation.y = az * DEG; built.hero.updateWorldMatrix(true, true);
    const pivot = built.hero.getWorldPosition(new THREE.Vector3());
    const ob = lb.clone(); ob.pts = [];
    for (let k = 0; k < 8; k++) {
      const v = new THREE.Vector3(k & 1 ? lb.max.x : lb.min.x, k & 2 ? lb.max.y : lb.min.y, k & 4 ? lb.max.z : lb.min.z).sub(pivot);
      v.applyAxisAngle(new THREE.Vector3(0, 1, 0), az * DEG).add(pivot); ob.pts.push(v);
    }
    const o = { ...COMP, ...built.opt, az }; o.wantW = toPx(o.wantW); o.maxH = toPy(o.maxH);
    const q = fitBox(ob, o);
    focusOf(q, [boxOf(built.hero)]);
    poses[i] = { a: q, b: { ...q, d: q.d * 0.97, f: q.f * 0.97, az: q.az - 0.4 * DEG } };
  });

  // ---------- camera timeline: hold drift, then a 24-frame ease-in-out move with a 6° roll-free arc and a focus pull
  const cam = { tx: 0, ty: 0, tz: 0, d: 10, az: 0, el: 0, ox: 0, oy: 0, f: 10, ap: 1 };
  const KEYS = ["tx", "ty", "tz", "d", "az", "el", "ox", "oy", "f", "ap"];
  const pick = (q) => { const o = {}; KEYS.forEach((k) => (o[k] = q[k])); return o; };
  const flights = [];
  CFG.beats.forEach((c, i) => {
    const ps = poses[i]; const next = CFG.beats[i + 1];
    const fl = i ? (c.kind === "outro" ? FLY_OUT : FLY) : 0;
    const arrive = i ? c.t - 0.5 + fl : 0;
    const end = next ? next.t - 0.5 : D;
    if (i === 0) {
      tl.fromTo(cam, { ...pick(ps.a), d: ps.a.d * 1.12, f: ps.a.f * 1.12, el: ps.a.el + 4 * DEG }, { ...pick(ps.a), duration: 0.9, ease: "power2.out", immediateRender: true }, 0);
      tl.fromTo(cam, { ...pick(ps.a) }, { ...pick(ps.b), duration: Math.max(0.3, end - 0.9), ease: "sine.inOut", immediateRender: false }, 0.9);
    } else {
      const t0 = c.t - 0.5;
      flights.push([t0, fl, i % 2 ? 1 : -1]);
      tl.fromTo(cam, { ...pick(poses[i - 1].b) }, { ...pick(ps.a), duration: fl, ease: "power2.inOut", immediateRender: false }, t0);
      tl.fromTo(cam, { ...pick(ps.a) }, { ...pick(ps.b), duration: Math.max(0.3, end - arrive), ease: "sine.inOut", immediateRender: false }, arrive);
    }
  });
  // lights: key + fill dim to the rim in the outro
  const lv = { ...LIGHT };
  const oi = CFG.beats.findIndex((c) => c.kind === "outro");
  if (oi >= 0) {      // the recap: a white-balanced key on the ceramic, rim halved (no lavender cast), a low wash keeps the far set readable
    tl.to(lv, { rim: 4.5, wash: 0.6, duration: 1.0, ease: "power2.inOut" }, CFG.beats[oi].t - 0.3);
    tl.to(key.color, { r: 1, g: 0.96, b: 0.92, duration: 1.0 }, CFG.beats[oi].t - 0.3);
  }
  const sweeps = [];       // key-light sweeps (title)

  // ---------- build every station's tweens
  // a station starts building while the camera is still arriving (arrival = t + 0.3), so no frame is half-empty
  stations.forEach(({ c, built }, i) => built.anim(i ? c.t - 0.6 : c.t));     // the incoming station builds during the flight

  // ---------- post: depth of field (focus follows the camera distance), no wide bloom
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(1); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  const bokeh = new BokehPass(scene, camera, { focus: 20, aperture: CFG.aperture || 0.0011, maxblur: 0.008 });
  composer.addPass(bokeh);
  composer.addPass(new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.12, 0.08, 0.96));
  composer.addPass(new OutputPass());
  // black lift in display space: the deepest shadow lands at ≈ #0e0f12 instead of pure black (a lit showroom, not a void)
  const LIFT = CFG.lift != null ? CFG.lift : 0.055;
  composer.addPass(new ShaderPass({
    uniforms: { tDiffuse: { value: null }, uLift: { value: new THREE.Vector3(LIFT * 0.96, LIFT, LIFT * 1.14) } },
    vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
    fragmentShader: "uniform sampler2D tDiffuse; uniform vec3 uLift; varying vec2 vUv; void main(){ vec4 c = texture2D(tDiffuse, vUv); gl_FragColor = vec4(uLift + c.rgb * (1.0 - uLift), 1.0); }",
  }));

  function renderAt(t) {
    t = Math.max(0, t);
    tl.seek(t, false);
    for (const f of ticks) f(t);
    // the arc + focus pull of the current flight
    let arc = 0, pull = 0;
    for (const [t0, fl, dir] of flights) { const u = (t - t0) / fl; if (u > 0 && u < 1) { arc = dir * 6 * DEG * Math.sin(Math.PI * u); pull = Math.sin(Math.PI * u); } }
    camera.fov = FOV * (1 + 0.9 * pull);
    poseCam({ ...cam, az: cam.az + arc * 0.5, d: cam.d * (1 + 0.8 * pull) });
    // lights follow the station the camera looks at
    let sw = 0; for (const [ts, dur] of sweeps) { const u = (t - ts) / dur; if (u > -0.01 && u < 1.01) sw = (1 - Math.min(1, Math.max(0, u))); }
    // light offsets are given in the camera's frame (key top-left, rim back-right, fill low front) and turned with its azimuth
    const ca = Math.cos(cam.az), sa = Math.sin(cam.az);
    const rot = (x, z) => [cam.tx + x * ca + z * sa, cam.tz - x * sa + z * ca];
    const kp = rot(LIGHT.kx - 10 * sw, LIGHT.kz), kt = rot(6 * sw, 0), rp = rot(9, -9), fp = rot(0, 14);
    key.position.set(kp[0], cam.ty + LIGHT.ky, kp[1]); key.target.position.set(kt[0], cam.ty * 0.4, kt[1]); key.target.updateMatrixWorld();
    key.intensity = lv.key;
    rim.position.set(rp[0], cam.ty + 5, rp[1]); rim.lookAt(cam.tx, cam.ty, cam.tz); rim.intensity = lv.rim;
    fill.position.set(fp[0], 1.2, fp[1]); fill.lookAt(cam.tx, cam.ty, cam.tz); fill.intensity = lv.fill;
    scene.environmentIntensity = lv.env;
    wash.intensity = lv.wash; wash.position.set(cam.tx - 30, cam.ty + 40, cam.tz + 40); wash.target.position.set(cam.tx, 0, cam.tz - 40); wash.target.updateMatrixWorld();
    rimAll.intensity = lv.all; rimAll.position.set(cam.tx + 40, cam.ty + 30, cam.tz - 60); rimAll.target.position.set(cam.tx, 0, cam.tz - 80); rimAll.target.updateMatrixWorld();
    scene.fog.near = cam.d + 14; scene.fog.far = cam.d + 90 + (oi >= 0 && t > CFG.beats[oi].t - 0.6 ? 140 : 0);
    bokeh.uniforms.focus.value = cam.f * (1 + 0.2 * pull);
    // circle of confusion ∝ aperture × |depth − focus| / depth: scale with the camera distance so a close 16:9 camera blurs no more
    bokeh.uniforms.aperture.value = AP0 * (cam.ap + (1 - cam.ap) * pull) * (1 + 1.5 * pull);
    composer.render();
  }

  window.__hf = window.__hf || {}; window.__hf.buildReady = window.__hf.buildReady || {};
  renderAt(0);
  window.addEventListener("hf-seek", (e) => { renderAt(e.detail.time); renderer.getContext().finish(); });
  window.__h9WorldReady && window.__h9WorldReady();
}

// ================================================================ the 0.x six-beat set (unchanged)
function legacyWorld() {
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
}

if (window.__H9_WORLD && window.__H9_WORLD.legacy) legacyWorld(); else studioWorld();
