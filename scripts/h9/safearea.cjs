// Safe-area probe for 9:16: which visible text sits under the platform's chrome at given times.
//   node safearea.cjs <index.html> <t1,t2,...> <W> <H> [exempt selectors joined by ||]
// Prints JSON [{t, zone, text, sel, rect}]. Needs puppeteer-core (H9_PUPPETEER = its path) and Chrome (H9_CHROME);
// scripts/stress.py finds both inside the HyperFrames install, so nothing extra is downloaded.
// Zones (Douyin-style): top 200 px (tabs), bottom 400 px (title / music / comment bar), right 120 px of the lower half (buttons).
// Opt out: data-safe="ignore" on an element, or a style's STYLE["safe_exempt"] selectors.
const path = require("path");
const puppeteer = require(process.env.H9_PUPPETEER || "puppeteer-core");

(async () => {
  const [file, times, W, H, exempt, zonesJson] = process.argv.slice(2);   // zonesJson: optional [{n,x0,y0,x1,y1,tx,ty}] replacing the default zones (platform watermarks)
  const browser = await puppeteer.launch({ executablePath: process.env.H9_CHROME, headless: true, args: ["--allow-file-access-from-files", "--no-sandbox"] });
  const page = await browser.newPage();
  await page.setViewport({ width: +W, height: +H });
  await page.goto("file://" + path.resolve(file), { waitUntil: "load", timeout: 30000 });
  await page.waitForFunction(() => !!(window.__timelines && window.__timelines.main), { timeout: 15000, polling: 100 });
  await page.evaluate(() => (document.fonts ? document.fonts.ready : null));
  const out = [];
  for (const t of times.split(",").map(Number)) {
    const r = await page.evaluate((t, W, H, exempt, zonesJson) => {
      window.__timelines.main.seek(t, false);
      // the HyperFrames runtime shows/hides timed clips; a raw page has to do it itself
      document.querySelectorAll("#root [data-start]").forEach((el) => {
        const s = +el.dataset.start, d = +el.dataset.duration;
        el.style.visibility = t >= s - 1e-3 && t < s + d ? "" : "hidden";
      });
      const zones = zonesJson ? JSON.parse(zonesJson) : [
        { n: "top", x0: 0, y0: 0, x1: W, y1: 200, tx: 4, ty: 20 },          // tolerances: a line box grazing the edge is not covered ink
        { n: "bottom", x0: 0, y0: H - 400, x1: W, y1: H, tx: 4, ty: 16 },
        { n: "right", x0: W - 120, y0: H / 2, x1: W, y1: H, tx: 30, ty: 4 },
      ];
      const ex = exempt ? exempt.split("||") : [];
      const res = [];
      const walker = document.createTreeWalker(document.getElementById("root"), NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walker.nextNode())) {
        const txt = n.textContent.trim();
        const el = n.parentElement;
        if (!txt || !el || el.closest('[data-safe="ignore"], script, style')) continue;
        if (ex.some((s) => { try { return el.closest(s); } catch (e) { return false; } })) continue;
        let op = 1, e = el, hidden = false;
        while (e && e !== document.body) {
          const cs = getComputedStyle(e);
          if (cs.display === "none" || cs.visibility === "hidden") { hidden = true; break; }
          op *= parseFloat(cs.opacity);
          e = e.parentElement;
        }
        if (hidden || op < 0.15) continue;
        // ghost / outline type (fill nearly transparent) is decoration by design, not something to read
        const cs0 = getComputedStyle(el);
        const alpha = (c) => {      // rgb()/rgba() and color(srgb r g b / a) (what color-mix() computes to)
          c = c || ""; if (c === "transparent") return 0;
          const sl = /\/\s*([\d.]+%?)\s*\)/.exec(c); if (sl) return sl[1].endsWith("%") ? parseFloat(sl[1]) / 100 : parseFloat(sl[1]);
          const m = /rgba\(([^)]+)\)/.exec(c); if (m) { const p = m[1].split(/[ ,]+/).filter(Boolean); return p.length > 3 ? parseFloat(p[3]) : 1; }
          return 1; };
        const fillA = cs0.webkitTextFillColor && cs0.webkitTextFillColor !== cs0.color ? alpha(cs0.webkitTextFillColor) : alpha(cs0.color);
        if (fillA < 0.3) continue;
        // what is actually visible: clip by every ancestor that clips (slot reels, masks, scrollers)
        let cx0 = 0, cy0 = 0, cx1 = W, cy1 = H;
        for (let a = el; a && a !== document.body; a = a.parentElement) {
          const cs = getComputedStyle(a);
          if (cs.overflowX !== "visible" || cs.overflowY !== "visible" || (cs.clipPath && cs.clipPath !== "none")) {
            const b = a.getBoundingClientRect();
            if (cs.overflowX !== "visible") { cx0 = Math.max(cx0, b.left); cx1 = Math.min(cx1, b.right); }
            if (cs.overflowY !== "visible") { cy0 = Math.max(cy0, b.top); cy1 = Math.min(cy1, b.bottom); }
          }
        }
        const rg = document.createRange();
        rg.selectNodeContents(n);
        for (const r of rg.getClientRects()) {
          const x0 = Math.max(cx0, r.left), y0 = Math.max(cy0, r.top), x1 = Math.min(cx1, r.right), y1 = Math.min(cy1, r.bottom);
          if (x1 - x0 < 2 || y1 - y0 < 2) continue;
          for (const z of zones) {
            const ix = Math.min(x1, z.x1) - Math.max(x0, z.x0), iy = Math.min(y1, z.y1) - Math.max(y0, z.y0);
            if (ix > z.tx && iy > z.ty) {
              const cls = typeof el.className === "string" && el.className ? "." + el.className.trim().split(/\s+/).join(".") : "";
              const clip = el.closest("[data-start]");
              res.push({ t, zone: z.n, text: txt.slice(0, 24), sel: (clip ? "#" + clip.id + " " : "") + el.tagName.toLowerCase() + cls,
                         rect: [x0, y0, x1, y1].map(Math.round) });
            }
          }
        }
      }
      return res;
    }, t, +W, +H, exempt || "", zonesJson || "");
    out.push(...r);
  }
  console.log(JSON.stringify(out));
  await browser.close();
})().catch((e) => { console.error(String(e && e.stack || e)); process.exit(2); });
