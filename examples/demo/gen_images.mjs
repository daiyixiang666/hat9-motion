// Neutral demo images for the style gallery (our own, GPT Image 2 via the local bridge).
import { genImage } from "../../../../video/toolkit/lib/imagegen.mjs";
import fs from "node:fs";
const OUT = new URL("./assets/img/", import.meta.url).pathname;
const NO = "No text, no letters, no logos, no watermark.";
const jobs = [
  ["desk", null, `Cinematic still, horizontal 16:9: a person seen from behind at a desk late at night, face not visible, a wide monitor filled with a grid of dozens of AI-generated thumbnail images glowing in the dark room. Single cool monitor light, warm tungsten lamp far in the background, deep shadows, shallow depth of field, 35mm film grain, slight halation. Quiet, slightly lonely mood. ${NO}`],
  ["cup_mag", null, `Editorial still-life photograph for a design magazine, horizontal: a single handmade off-white ceramic cup on a raw oak table beside a tall window. One hard diagonal beam of late-afternoon sun cuts across the cup, long soft shadow, the rest of the frame falls into warm darkness. Limited palette: sand, bone white, umber. Subject placed off-centre on the left third with generous negative space. Shot on medium-format film, fine grain, gentle halation on highlights. ${NO}`],
  ["cup_cheap", "cup_mag", `Re-shoot the exact same ceramic cup as a cheap, garish e-commerce promotional image: cup dead-centre, flat shadowless lighting, oversaturated red and yellow gradient background with lens-flare sparkles and fake glossy reflections, plastic-looking CGI surfaces, cluttered decorative swirls and starbursts, typical low-budget online shop banner look, horizontal frame. ${NO}`],
  ["hands", null, `Cinematic close-up, horizontal 16:9: a hand holding a red pencil hovering over a contact sheet of many similar printed images spread on a light table, choosing which one to cross out. Soft top light from the light table, warm room, shallow depth of field, 35mm film grain. Face not visible. ${NO}`],
];
for (const [id, ref, prompt] of jobs) {
  if (fs.existsSync(`${OUT}${id}.png`)) continue;
  try { await genImage({ prompt, size: "1536x1024", refs: ref ? [`${OUT}${ref}.png`] : [], out: `${OUT}${id}.png` }); console.log("ok", id); }
  catch (e) { console.log("fail", id, e.message); }
}
