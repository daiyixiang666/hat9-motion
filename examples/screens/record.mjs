#!/usr/bin/env node
// Demo material for the screens reel: a real screen recording of our own gallery page (desktop and phone),
// frame by frame through headless Chrome, plus where each click happened (for screencast's `clicks`).
//   node examples/screens/record.mjs            -> assets/gallery_rec.mp4 (+ .json), assets/gallery_phone_rec.mp4 (+ .json)
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { launch, openPage } from "../../scripts/webpage.mjs";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const URL_ = "https://daiyixiang666.github.io/hat9-motion/gallery/";
const FPS = 30;

async function record(name, { width, height, scale, mobile }, script) {
  const browser = await launch();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "h9rec-"));
  const clicks = [];
  try {
    const page = await openPage(browser, URL_, { width, height, scale, mobile, dark: true, wait: 2500 });
    await page.evaluate(() => scrollTo(0, 0));
    let f = 0, mx = width * 0.5, my = height * 0.4;
    const shot = async () => { await page.screenshot({ path: path.join(tmp, `f${String(f++).padStart(5, "0")}.jpg`), type: "jpeg", quality: 88 }); };
    const hold = async (s) => { for (let i = 0; i < Math.round(s * FPS); i++) await shot(); };
    const ease = (u) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
    const scrollTo = async (y, s) => {
      const y0 = await page.evaluate(() => scrollY), n = Math.round(s * FPS);
      for (let i = 1; i <= n; i++) { await page.evaluate((v) => scrollTo(0, v), y0 + (y - y0) * ease(i / n)); await shot(); }
    };
    const moveTo = async (x, y, s) => {
      const x0 = mx, y0 = my, n = Math.round(s * FPS);
      for (let i = 1; i <= n; i++) { const u = ease(i / n); mx = x0 + (x - x0) * u; my = y0 + (y - y0) * u; await page.mouse.move(mx, my); await shot(); }
    };
    const rect = (sel, text) => page.evaluate((sel, text) => {
      const el = [...document.querySelectorAll(sel)].find((e) => !text || e.textContent.trim().startsWith(text));
      if (!el) return null; const r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
    }, sel, text);
    const click = async (sel, text, label) => {
      const r = await rect(sel, text); if (!r) throw new Error(`not found: ${sel} ${text || ""}`);
      await moveTo(r.x, r.y, 0.7);
      clicks.push({ t: +(f / FPS).toFixed(3), x: +(r.x / width).toFixed(4), y: +(r.y / height).toFixed(4), label });
      await page.mouse.click(r.x, r.y); await shot();
    };
    const type = async (text) => { for (const ch of text) { await page.keyboard.type(ch); await hold(0.18); } };
    await script({ hold, scrollTo, moveTo, click, type, rect, page });
    const mp4 = path.join(HERE, "assets", `${name}.mp4`);
    execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(tmp, "f%05d.jpg"), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", mp4]);
    fs.writeFileSync(mp4.replace(/\.mp4$/, ".json"), JSON.stringify({ url: URL_, fps: FPS, frames: f, duration: +(f / FPS).toFixed(3), viewport: [width, height], clicks }, null, 1));
    console.log(mp4, `${(f / FPS).toFixed(1)}s`, clicks.length, "clicks");
  } finally { await browser.close(); fs.rmSync(tmp, { recursive: true, force: true }); }
}

await record("gallery_rec", { width: 1280, height: 800, scale: 1, mobile: false }, async ({ hold, scrollTo, click, type, rect }) => {
  await hold(1.0);
  const bar = await rect(".bar");
  await scrollTo(Math.max(0, (bar ? bar.y : 700) - 120), 1.4);
  await hold(0.4);
  await click(".chip", "数据", "点「数据」分类");
  await hold(1.0);
  await click("#q", "", "点搜索框");
  await type("增长");
  await hold(0.8);
  await click(".card .id", "", "点效果名，复制 id");
  await hold(1.4);
});

await record("gallery_phone_rec", { width: 390, height: 844, scale: 2, mobile: true }, async ({ hold, scrollTo, click, rect }) => {
  await hold(0.8);
  const bar = await rect(".bar");
  await scrollTo(Math.max(0, (bar ? bar.y : 900) - 160), 1.4);
  await hold(0.3);
  await click("#o-v", "", "切到竖屏预览");
  await hold(0.8);
  await scrollTo(Math.max(0, (bar ? bar.y : 900) + 700), 1.6);
  await hold(0.8);
});
