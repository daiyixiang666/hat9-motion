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

// ---- real UI components (scripts/ui_capture.py) --------------------------------------------------------------------
// captureUI({url, out, picks:[css], auto, width, height, scale, mobile, dark, wait, max, maxHeight}) -> writes out/page.png,
// out/<n>-<kind>.png (one tight 2x crop per component) and out/raw.json { url, title, site, width, height, scale, components:
// [{id, kind, selector, file, box:{x,y,w,h} (CSS px on the page), text, hot:[{text, tag, x,y,w,h} relative to the crop, CSS px]}] }.
// Cookie / consent overlays are hidden; the nav stays. Nothing is clicked, typed or submitted.
export async function captureUI(o) {
  const width = o.width || (o.mobile ? 390 : 1280), scale = o.scale || 2;
  fs.mkdirSync(o.out, { recursive: true });
  const browser = await launch();
  try {
    const page = await openPage(browser, o.url, { width, height: o.height || 900, scale, mobile: !!o.mobile, dark: !!o.dark, wait: o.wait ?? 1500 });
    const info = await page.evaluate((picks, auto, max) => {
      const vis = (el) => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
        return r.width > 8 && r.height > 8 && cs.visibility !== "hidden" && cs.display !== "none" && +cs.opacity > 0.05; };
      // overlays that are not the site: cookie / consent / newsletter dialogs
      for (const el of document.querySelectorAll("body *")) {
        const cs = getComputedStyle(el);
        if ((cs.position === "fixed" || cs.position === "sticky") && /cookie|consent|gdpr|subscribe|newsletter|隐私|同意/i.test((el.id + " " + el.className + " " + el.innerText).slice(0, 400))
            && el.getBoundingClientRect().height < innerHeight * 0.7) el.style.setProperty("display", "none", "important");
        if (cs.position === "fixed" && el.getBoundingClientRect().top > innerHeight * 0.5) el.style.setProperty("display", "none", "important");
      }
      const abs = (r) => ({ x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height) });
      const W = document.documentElement.clientWidth;
      const sel = (el) => {                                            // a selector that finds this element again
        if (el.id && /^[a-zA-Z][\w-]*$/.test(el.id)) return `#${el.id}`;
        const parts = [];
        for (let e = el; e && e !== document.body && parts.length < 5; e = e.parentElement) {
          let s = e.tagName.toLowerCase();
          const cls = [...e.classList].filter((c) => /^[a-zA-Z][\w-]*$/.test(c) && c.length < 30).slice(0, 2);
          if (cls.length) s += "." + cls.join(".");
          const sib = e.parentElement ? [...e.parentElement.children].filter((x) => x.tagName === e.tagName) : [];
          if (sib.length > 1) s += `:nth-of-type(${sib.indexOf(e) + 1})`;
          parts.unshift(s);
          if (e.id && /^[a-zA-Z][\w-]*$/.test(e.id)) { parts[0] = `#${e.id}`; break; }
        }
        return parts.join(" > ");
      };
      const text = (el) => (el.innerText || el.value || el.getAttribute("aria-label") || "").replace(/\s+/g, " ").trim();
      const hots = (el, rect) => {                                     // clickable things inside, for cursor clicks
        const r0 = rect ? { left: rect.x - scrollX, top: rect.y - scrollY, right: rect.x - scrollX + rect.w, bottom: rect.y - scrollY + rect.h }
                        : el.getBoundingClientRect(), out = [];
        for (const h of (rect ? document : el).querySelectorAll("a, button, input, select, textarea, [role=button], summary")) {
          if (!vis(h)) continue;
          const r = h.getBoundingClientRect();
          if (r.left < r0.left - 1 || r.top < r0.top - 1 || r.right > r0.right + 1 || r.bottom > r0.bottom + 1) continue;
          const t = text(h) || h.getAttribute("placeholder") || h.getAttribute("title") || "";
          if (!t || t.length > 40) continue;
          out.push({ text: t.slice(0, 40), tag: h.tagName.toLowerCase(), type: h.getAttribute("type") || "",
                     x: Math.round(r.left - r0.left), y: Math.round(r.top - r0.top), w: Math.round(r.width), h: Math.round(r.height) });
        }
        return out.slice(0, 16);
      };
      const comps = [];
      const add = (el, kind, why, box) => {                          // box: a region instead of one element (the first screen)
        if (box) { comps.push({ el, kind, why, box, region: true }); return; }
        if (!el || !vis(el)) return;
        const r = el.getBoundingClientRect();
        if (r.width * r.height < 900) return;
        comps.push({ el, kind, why, box: abs(r) });
      };
      for (const p of picks) {
        let el = null; try { el = document.querySelector(p); } catch (e) {}
        if (el) add(el, "pick", p); else comps.push({ missing: p });
      }
      if (auto) {
        const main = document.querySelector("main, [role=main]") || document.body;
        const nav = [...document.querySelectorAll("header nav, nav, [role=navigation], header")].find((n) => vis(n) && n.getBoundingClientRect().top + scrollY < 300);
        add(nav && (nav.closest("header") || nav), "nav", "top navigation");
        const h1 = [...document.querySelectorAll("h1")].find(vis);
        if (h1) {                                                      // the hero: the smallest block around the h1 that holds more than it
          let e = h1;
          while (e.parentElement && e.parentElement !== document.body) {
            const r = e.parentElement.getBoundingClientRect();
            if (r.height > innerHeight * 1.1 || r.width < W * 0.5) break;
            e = e.parentElement;
            if (r.height > 260 && (e.querySelector("p, a, button, img, svg"))) break;
          }
          const rh = e.getBoundingClientRect();
          if (rh.height >= 220) add(e, "hero", "block around the h1");
          else {                                                       // no wrapper of its own: the first screen around it
            const top = nav ? Math.round(nav.getBoundingClientRect().bottom + scrollY) : 0;
            const y = Math.max(top, Math.round(rh.top + scrollY) - 40);
            add(h1, "hero", "first screen", { x: 0, y, w: W, h: Math.min(Math.round(innerHeight * 0.8), document.documentElement.scrollHeight - y) });
          }
        }
        const btns = [...document.querySelectorAll("a, button, [role=button], input[type=submit]")].filter(vis).map((b) => {
          const cs = getComputedStyle(b), r = b.getBoundingClientRect();
          const bg = cs.backgroundColor, filled = bg && !/rgba\(0, 0, 0, 0\)|transparent/.test(bg);
          const m = (bg || "").match(/\d+(\.\d+)?/g) || [0, 0, 0];
          const sat = filled ? (Math.max(m[0], m[1], m[2]) - Math.min(m[0], m[1], m[2])) / 255 : 0;
          const verb = /sign ?up|get started|start|try|download|install|buy|join|subscribe|注册|开始|下载|安装|免费|立即|购买|试用/i.test(text(b));
          const look = (filled && (sat > 0.25 || verb)) || (verb && /btn|button|cta/i.test(b.className + ""));
          return { b, look, score: (1 + 2 * sat + (verb ? 1 : 0)) * r.width * r.height * (r.top + scrollY < innerHeight * 1.5 ? 2 : 1), t: text(b) };
        }).filter((x) => { const r = x.b.getBoundingClientRect();
          return x.look && x.t && x.t.length <= 30 && r.height >= 24 && r.height < 90 && r.width >= 60; });
        btns.sort((a, b) => b.score - a.score);
        for (const x of btns.slice(0, 2)) add(x.b, "cta", "prominent button");
        // card groups: >= 3 same-shaped siblings
        const groups = [];
        for (const par of main.querySelectorAll("*")) {
          const kids = [...par.children].filter(vis);
          if (kids.length < 3 || kids.length > 24) continue;
          const sig = (k) => k.tagName + "." + [...k.classList].sort().join(".");
          const s0 = sig(kids[0]);
          const same = kids.filter((k) => sig(k) === s0);
          if (same.length < 3 || same.length < kids.length * 0.6) continue;
          const r = same[0].getBoundingClientRect();
          if (r.width < 120 || r.height < 80 || r.width > W * 0.95 || r.height > 900) continue;
          if (!same.every((k) => text(k).length > 8)) continue;
          groups.push({ par, same, area: r.width * r.height * same.length });
        }
        groups.sort((a, b) => b.area - a.area);
        const used = [];
        for (const g of groups) {
          if (used.some((u) => u.contains(g.par) || g.par.contains(u))) continue;
          used.push(g.par);
          const PRICE = /(\$|¥|€|£)\s?\d+(\.\d+)?\s*(\/|per|每|元)|\/\s?(mo|month|yr|year)\b|per month|元\s*\/\s*(月|年)/i;
          const price = g.same.filter((k) => PRICE.test(text(k))).length >= 2;
          if (g.par.getBoundingClientRect().height <= innerHeight * 1.6) add(g.par, price ? "pricing" : "cards", `${g.same.length} cards`);
          add(g.same[0], price ? "plan" : "card", "first card");
          if (used.length >= 2) break;
        }
        const form = [...document.querySelectorAll("form, [role=search]")].find((f) => vis(f) && f.querySelector("input, textarea, select"));
        add(form, "form", "form");
        const code = [...document.querySelectorAll("pre")].filter((c) => vis(c) && c.getBoundingClientRect().height > 40)[0];
        add(code && (code.closest("figure, .highlight, [class*=code]") || code), "code", "code block");
        const tbl = [...document.querySelectorAll("table")].find((t) => vis(t) && t.rows.length >= 3);
        add(tbl, "table", "table");
      }
      // drop near-duplicates (same box), keep order of priority
      const keep = [];
      const iou = (a, b) => { const x = Math.max(0, Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x)), y = Math.max(0, Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y));
        return (x * y) / (a.w * a.h + b.w * b.h - x * y); };
      for (const c of comps) {
        if (c.missing) { keep.push(c); continue; }
        if (keep.some((k) => k.box && iou(k.box, c.box) > 0.85)) continue;
        keep.push(c);
      }
      const out = keep.filter((c) => c.missing || true).slice(0, max + picks.length).map((c, i) => c.missing ? { missing: c.missing } : ({
        kind: c.kind, why: c.why, selector: c.region ? "" : sel(c.el), box: c.box, text: text(c.el).slice(0, 300),
        head: (c.region ? text(c.el) : text(c.el.querySelector("h1,h2,h3,h4,strong,b,label,button") || c.el)).slice(0, 60),
        hot: c.region ? hots(null, c.box) : hots(c.el), tag: c.el.tagName.toLowerCase() }));
      const meta = (n) => document.querySelector(`meta[property="${n}"],meta[name="${n}"]`)?.content || "";
      const headings = [...document.querySelectorAll("h1,h2,h3")].filter(vis).map((h) => ({ text: h.innerText.trim().slice(0, 80), level: +h.tagName[1], ...abs(h.getBoundingClientRect()) }));
      return { title: document.title, description: meta("og:description") || meta("description"), site: meta("og:site_name") || location.hostname,
               docW: W, docH: document.documentElement.scrollHeight, headings, components: out };
    }, o.picks || [], !!o.auto, o.max || 8);
    // what sticks to the viewport would cover the component being shot (and repeat on the long page): pin it in place
    await page.evaluate(() => { for (const el of document.querySelectorAll("body *")) { const cs = getComputedStyle(el);
      if (cs.position === "fixed" && el.getBoundingClientRect().height < innerHeight * 0.6) el.style.setProperty("position", "absolute", "important");
      if (cs.position === "sticky") el.style.setProperty("position", "relative", "important"); } });
    const comps = [];
    let n = 0;
    for (const c of info.components) {
      if (c.missing) { comps.push(c); continue; }
      n += 1;
      const file = `${String(n).padStart(2, "0")}-${c.kind}.png`;
      const b = c.box;
      await page.evaluate((y) => scrollTo(0, Math.max(0, y - 100)), b.y);
      await new Promise((r) => setTimeout(r, 250));
      await page.screenshot({ path: path.join(o.out, file), clip: { x: b.x, y: b.y, width: Math.min(b.w, info.docW - b.x), height: b.h }, captureBeyondViewport: true });
      comps.push({ id: n, file, ...c });
    }
    await page.evaluate(() => scrollTo(0, 0));
    // the page for context, with the components' boxes: hide what sticks to the viewport so it shows once, at the top
    await page.evaluate(() => { for (const el of document.querySelectorAll("body *")) { const cs = getComputedStyle(el);
      if (cs.position === "fixed" && el.getBoundingClientRect().height < innerHeight * 0.6) el.style.setProperty("position", "absolute", "important");
      if (cs.position === "sticky") el.style.setProperty("position", "relative", "important"); } });
    const H = Math.min(info.docH, o.maxHeight || 8000);
    await page.screenshot({ path: path.join(o.out, "page.png"), clip: { x: 0, y: 0, width: info.docW, height: H }, captureBeyondViewport: true });
    const raw = { url: o.url, title: info.title, description: info.description, site: info.site, width: info.docW, height: H, scale,
                  headings: info.headings.filter((h) => h.y < H), components: comps };
    fs.writeFileSync(path.join(o.out, "raw.json"), JSON.stringify(raw, null, 1));
    return raw;
  } finally { await browser.close(); }
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
