#!/usr/bin/env node
// A web page as one long screenshot plus what is on it, for scroll_shot / cite_article / url_brief.
//
//   node scripts/webpage.mjs <url> <out.png> [--json out.json] [--width 1280] [--scale 1.5] [--max-height 14000]
//                            [--selector "article"] [--find "phrase"]... [--mobile] [--dark] [--wait 1500]
//
// out.json = { url, title, description, site, width, height, scale, headings: [{text, level, y}], boxes: [{find, x, y, w, h}],
//              paragraphs: [first few paragraph texts] }   — all coordinates in output pixels of out.png.
// Fixed / sticky overlays (nav bars, cookie banners) are hidden so the long shot reads cleanly.
// Uses the Chrome + puppeteer-core that HyperFrames installs on its first render (no extra dependency);
// set CHROME_PATH / PUPPETEER_CORE to point elsewhere.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { pathToFileURL } from "node:url";

const newest = (dir, sub) => {
  if (!fs.existsSync(dir)) return null;
  const c = fs.readdirSync(dir).map((d) => path.join(dir, d, sub)).filter((p) => fs.existsSync(p));
  return c.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs)[0] || null;
};

export async function launch() {
  const pptr = process.env.PUPPETEER_CORE || newest(path.join(os.homedir(), ".npm/_npx"), "node_modules/puppeteer-core");
  if (!pptr) throw new Error("puppeteer-core not found — run one HyperFrames render first (npx --yes hyperframes@0.8.191 render), or set PUPPETEER_CORE");
  const home = os.homedir();
  const cands = [process.env.CHROME_PATH];
  for (const root of [path.join(home, ".cache/puppeteer/chrome"), path.join(home, ".cache/puppeteer/chrome-headless-shell")]) {
    const d = newest(root, "");
    if (!d) continue;
    for (const sub of ["chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                       "chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
                       "chrome-linux64/chrome", "chrome-win64/chrome.exe",
                       "chrome-headless-shell-mac-arm64/chrome-headless-shell", "chrome-headless-shell-linux64/chrome-headless-shell"])
      cands.push(path.join(d, sub));
  }
  cands.push("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium");
  const exe = cands.find((p) => p && fs.existsSync(p));
  if (!exe) throw new Error("no Chrome found — set CHROME_PATH");
  const pkg = JSON.parse(fs.readFileSync(path.join(pptr, "package.json"), "utf8"));
  const entry = pkg.exports?.["."]?.import || pkg.module || pkg.main;
  const mod = await import(pathToFileURL(path.join(pptr, typeof entry === "string" ? entry : entry.default)).href);
  const puppeteer = mod.default || mod;
  return puppeteer.launch({ executablePath: exe, headless: true, args: ["--no-sandbox", "--hide-scrollbars", "--lang=zh-CN"] });
}

export async function openPage(browser, url, { width = 1280, height = 900, scale = 1.5, mobile = false, dark = false, wait = 1500 } = {}) {
  const page = await browser.newPage();
  if (mobile) await page.setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1");
  await page.setViewport({ width, height, deviceScaleFactor: scale, isMobile: mobile, hasTouch: mobile });
  await page.emulateMediaFeatures([{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }, { name: "prefers-reduced-motion", value: "reduce" }]);
  await page.goto(url, { waitUntil: "networkidle2", timeout: 60000 }).catch(() => {});
  // lazy images only load near the viewport: make them eager and walk the page once
  await page.evaluate(async () => {
    document.querySelectorAll("img[loading=lazy]").forEach((i) => { i.loading = "eager"; });
    const H = document.documentElement.scrollHeight;
    for (let y = 0; y < H; y += innerHeight * 0.8) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 120)); }
    scrollTo(0, 0);
    await Promise.all([...document.images].filter((i) => !i.complete).map((i) => new Promise((r) => { i.onload = i.onerror = r; setTimeout(r, 8000); })));
  });
  await new Promise((r) => setTimeout(r, wait));
  return page;
}

async function main() {
  const args = process.argv.slice(2);
  const opt = (k, d) => { const i = args.indexOf(`--${k}`); return i >= 0 ? args[i + 1] : d; };
  const flag = (k) => args.includes(`--${k}`);
  const finds = args.flatMap((a, i) => (a === "--find" ? [args[i + 1]] : []));
  const valued = new Set(["json", "width", "scale", "max-height", "selector", "find", "wait"]);
  const pos = args.filter((a, i) => !a.startsWith("--") && !(i > 0 && args[i - 1].startsWith("--") && valued.has(args[i - 1].slice(2))));
  const [url, out] = pos;
  if (!url || !out) { console.error("usage: node scripts/webpage.mjs <url> <out.png> [--json out.json] [--width 1280] [--selector css] [--find text]..."); process.exit(2); }
  const width = +opt("width", flag("mobile") ? 390 : 1280), scale = +opt("scale", flag("mobile") ? 2 : 1.5), maxH = +opt("max-height", 14000);
  const browser = await launch();
  try {
    const page = await openPage(browser, url, { width, scale, mobile: flag("mobile"), dark: flag("dark"), wait: +opt("wait", 1500) });
    const info = await page.evaluate((sel, finds) => {
      for (const el of document.querySelectorAll("body *")) {
        const cs = getComputedStyle(el);
        if ((cs.position === "fixed" || cs.position === "sticky") && el.getBoundingClientRect().height < innerHeight * 0.6) el.style.setProperty("display", "none", "important");
      }
      const root = (sel && document.querySelector(sel)) || document.documentElement;
      const r0 = root.getBoundingClientRect(), ox = r0.left + scrollX, oy = r0.top + scrollY;
      const meta = (n) => document.querySelector(`meta[property="${n}"],meta[name="${n}"]`)?.content || "";
      const rel = (r) => ({ x: r.left + scrollX - ox, y: r.top + scrollY - oy, w: r.width, h: r.height });
      const main = sel ? root : (document.querySelector("article") || document.querySelector("main, [role=main]") || root);   // skip site chrome
      const headings = [...main.querySelectorAll("h1,h2,h3")].map((h) => ({ text: h.innerText.trim().slice(0, 80), level: +h.tagName[1], ...rel(h.getBoundingClientRect()) })).filter((h) => h.text && h.h > 0);
      const paragraphs = [...main.querySelectorAll("p")].map((p) => p.innerText.trim()).filter((s) => s.length > 20).slice(0, 6);
      const boxes = [];
      for (const f of finds) {
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        let n; while ((n = walker.nextNode())) {
          const i = n.textContent.indexOf(f);
          if (i < 0) continue;
          const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + f.length);
          const r = rg.getBoundingClientRect(); boxes.push({ find: f, ...rel(r) }); break;
        }
      }
      return { title: document.title, description: meta("og:description") || meta("description"), site: meta("og:site_name") || location.hostname,
               box: { x: ox, y: oy, w: r0.width, h: root === document.documentElement ? document.documentElement.scrollHeight : r0.height }, headings, paragraphs, boxes };
    }, opt("selector", ""), finds);
    const clipH = Math.min(info.box.h, maxH);
    await page.screenshot({ path: out, clip: { x: info.box.x, y: info.box.y, width: Math.min(info.box.w, width), height: clipH }, captureBeyondViewport: true });
    const k = scale, S = (o) => ({ ...o, x: Math.round(o.x * k), y: Math.round(o.y * k), w: Math.round(o.w * k), h: Math.round(o.h * k) });
    const json = { url, title: info.title, description: info.description, site: info.site, width: Math.round(Math.min(info.box.w, width) * k), height: Math.round(clipH * k), scale: k,
                   headings: info.headings.filter((h) => h.y < clipH).map(S), boxes: info.boxes.map(S), paragraphs: info.paragraphs };
    fs.writeFileSync(opt("json", out.replace(/\.\w+$/, ".json")), JSON.stringify(json, null, 1));
    console.log(`${out}  ${json.width}×${json.height}  ${json.headings.length} headings  ${json.boxes.length} boxes`);
  } finally { await browser.close(); }
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) main().catch((e) => { console.error(String(e.message || e)); process.exit(1); });
