#!/usr/bin/env python3
"""Quick-cut montage on the music's beats — the "啪啪啪" run between talking parts — and laying it into the film.

  python3 scripts/montage.py montage.json [--into work/renders/press_9x16.mp4] [--out montage.mp4]

montage.json:
  {"size": [1080, 1920], "fps": 30,
   "beats": "music/tech/Song.beats.json",   # or "bpm": 117.45, "beat0": 0.277
   "music_offset": 0,                       # film second where the song starts
   "start": 23.0,                           # film second; the run starts on the next beat
   "per": 1,                                # beats per cut (0.5 = half beats)
   "clips": [{"src": "renders/ink_9x16.mp4", "in": "auto", "label": "水墨", "line": "17 种风格"}, ...]}

Rules it enforces (references/director.md):
- every clip names the `line` it illustrates — a cut that is not about what is being said does not go in;
- `"in": "auto"` takes the clip's best window: a full, readable picture the whole time, no cut or transition wipe
  inside, a little motion preferred — never a blind middle frame; a number is used as given;
- each cut lands on a beat (frame edges are cumulative, so the run never drifts off the music);
- a label is optional: a solid tag in the top band (the film's captions sit low), ≥ 80 px at 1080 wide, ≤ 8 characters;
- each cut opens with a short push-in for impact.
With --into, the run is laid over the film at its start time; the film's sound is kept (bring the music up there).
Inside the film, prefer a "montage" beat in video.json (same picker, cut on the music's beats, music lifted): see
references/video-json.md.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import review  # noqa: E402
from h9 import beatsync  # noqa: E402


def probe(src):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                                   "-of", "json", str(src)])
    data = json.loads(out)
    s = data["streams"][0]
    return s["width"], s["height"], float(data["format"]["duration"])


def beat_grid(spec, base):
    if spec.get("beats"):
        _, grid = beatsync.read_beats(base / spec["beats"])
    else:
        step = 60.0 / float(spec["bpm"])
        grid = []
        t = float(spec.get("beat0", 0))
        while t < 600:
            grid.append(t)
            t += step
    return beatsync.grid(grid, float(spec.get("per", 1)), float(spec.get("music_offset", 0)))


best_moment = beatsync.best_moment      # shared with the in-film "montage" effect (scripts/h9/fx/montage.py)


def label_png(text, W, H, path):
    from PIL import Image, ImageDraw
    size = max(80, W // 11)
    font = review.label_font(size)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = d.textbbox((0, 0), text, font=font)
    tw = box[2] - box[0]
    th = box[3] - box[1]
    pad = size // 3
    x = (W - tw) // 2
    y = int(H * 0.10)          # top band: the film's own captions live in the bottom third
    d.rectangle([x - pad, y - pad // 2, x + tw + pad, y + th + pad], fill=(255, 214, 0, 255))
    d.text((x - box[0], y - box[1] + pad // 4), text, font=font, fill=(10, 10, 10))
    im.save(path)


def cut(clip, frames, fps, W, H, base, tmp, k):
    src = base / clip["src"]
    w, h, dur = probe(src)
    length = frames / fps
    start = best_moment(src, length, dur, tmp) if clip.get("in", "auto") == "auto" else float(clip["in"])
    f = max(W / w, H / h)
    cw = int(w * f / 2) * 2
    scale = f"scale=w='trunc({cw}*(1+0.07*max(0,1-n/6))/2)*2':h=-2:eval=frame,crop={W}:{H},fps={fps},setsar=1"
    out = tmp / f"c{k:03d}.mp4"
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(src)]
    if clip.get("label"):
        png = tmp / f"l{k:03d}.png"
        label_png(clip["label"], W, H, png)
        cmd += ["-i", str(png), "-filter_complex", f"[0:v]{scale}[v];[v][1:v]overlay=0:0[o]", "-map", "[o]"]
    else:
        cmd += ["-vf", scale]
    cmd += ["-frames:v", str(frames), "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps), str(out)]
    subprocess.run(cmd, check=True)
    return out, start


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--into", help="film to lay the run over")
    ap.add_argument("--out")
    a = ap.parse_args()
    spath = Path(a.spec).resolve()
    base = spath.parent
    spec = json.loads(spath.read_text())
    W, H = spec.get("size", [1080, 1920])
    fps = int(spec.get("fps", 30))
    clips = spec["clips"]
    for c in clips:
        if not c.get("line"):
            raise SystemExit(f"{c['src']}: 写上它对应哪句话（\"line\"）——和口播无关的画面不进快切")
        if len(c.get("label", "")) > 8:
            print(f"  注意：标签「{c['label']}」超过 8 个字，半秒读不完")
    grid = [b for b in beat_grid(spec, base) if b >= float(spec["start"]) - 1e-3]
    if len(grid) < len(clips) + 1:
        raise SystemExit("节拍不够：检查 beats / start")
    t0 = grid[0]
    edges = [round((g - t0) * fps) for g in grid[:len(clips) + 1]]
    out = Path(a.out).resolve() if a.out else spath.with_suffix(".mp4")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        parts = []
        for k, c in enumerate(clips):
            p, start = cut(c, edges[k + 1] - edges[k], fps, W, H, base, tmp, k)
            parts.append(p)
            print(f"  {t0 + edges[k] / fps:7.2f}s  {Path(c['src']).name} @ {start:.2f}s  「{c.get('label', '')}」 ← {c['line']}")
        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(out)], check=True)
    end = t0 + edges[-1] / fps
    print(f"快切：{out}  {t0:.2f}–{end:.2f}s  {len(clips)} 刀")
    if a.into:
        film = Path(a.into).resolve()
        dst = film.with_name(film.stem + "_montage.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(film), "-itsoffset", f"{t0:.3f}", "-i", str(out),
                        "-filter_complex", "[0:v][1:v]overlay=0:0:eof_action=pass[v]", "-map", "[v]", "-map", "0:a?",
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", str(dst)], check=True)
        print(f"已放进成片：{dst}（这段 {t0:.2f}–{end:.2f}s 记得把配乐推上来）")


if __name__ == "__main__":
    main()
