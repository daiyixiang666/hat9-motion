#!/usr/bin/env python3
"""Hand a finished build to an editor: silent picture + audio stems + captions, and an FCPXML timeline.

  python3 scripts/export_edit.py examples/mixue/build/press_16x9 --render examples/mixue/renders/press_16x9.mp4 --out handoff/

Writes into --out:
  film_silent.mp4     the render without sound (H.264 copied, no re-encode)
  voice.wav           narration stem, full length, placed where it plays in the film (meta.lead / gaps included)
  music.wav           music bed stem (ducked if meta.duck was on), full length
  sfx.wav             every sound effect at its time and level, mixed to one stem
  captions.srt        copied from the build
  timeline.fcpxml     FCPXML 1.9: film on the spine, the three stems as connected clips (lanes −1…−3), captions as
                      Basic Title clips on lane 1. Opens in Final Cut Pro 10.4.1+ and DaVinci Resolve (File → Import Timeline).

剪映 / CapCut: their project ("草稿") format is private and changes between versions (recent ones encrypt it), so no
draft file is written. Instead: new project → import film_silent.mp4 + the three .wav files → drop all four at 0:00
on separate tracks → 文本 → 识别字幕 / 导入字幕 → captions.srt. Every stem is full length from 0, so they line up.
Premiere Pro reads FCP 7 XML, not FCPXML: use the same four files + captions.srt there.
"""
import argparse, html, re, shutil, subprocess
from pathlib import Path

AUDIO = re.compile(r'<audio id="([^"]+)" class="clip" src="([^"]+)" data-start="([\d.]+)" data-duration="([\d.]+)"(?: data-media-start="([\d.]+)")?[^>]*?data-volume="([\d.]+)"([^>]*)>')


def run(*a): subprocess.run(a, check=True)


def stem(build, clips, D, dst):
    """mix clips [(src, start, dur, media_start, vol, fade_in, fade_out)] into one full-length wav."""
    if not clips:
        run("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{D:.3f}", str(dst)); return
    inp, f = [], []
    for k, (src, st, du, ms, vol, fi, fo) in enumerate(clips):
        inp += ["-i", str(build / src)]
        fx = f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=start={ms:.3f}:duration={du:.3f},asetpts=PTS-STARTPTS,volume={vol}"
        if fi: fx += f",afade=t=in:d={fi}"
        if fo: fx += f",afade=t=out:st={max(0, du - fo):.3f}:d={fo}"
        fx += f",adelay={int(st * 1000)}|{int(st * 1000)}[a{k}]"
        f.append(fx)
    f.append("".join(f"[a{k}]" for k in range(len(clips))) + f"amix=inputs={len(clips)}:normalize=0:dropout_transition=0,apad,atrim=duration={D:.3f}[o]")
    script = dst.with_suffix(".filter.txt"); script.write_text(";".join(f))
    run("ffmpeg", "-v", "error", "-y", *inp, "-filter_complex_script", str(script), "-map", "[o]", str(dst))
    script.unlink()


def srt_items(p):
    if not p.exists(): return []
    out = []
    for blk in p.read_text(encoding="utf-8").strip().split("\n\n"):
        ls = blk.strip().splitlines()
        if len(ls) < 3: continue
        def sec(x):
            h, m, s = x.replace(",", ".").split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
        a, b = [sec(x.strip()) for x in ls[1].split("-->")]
        out.append((a, b, " ".join(ls[2:])))
    return out


def fcpxml(out, D, W, H, fps, title, stems, caps):
    fr = lambda s: f"{round(s * fps)}/{fps}s"      # frame-accurate rational time
    res = [f'<format id="r1" name="FFVideoFormat{H}p{fps}" frameDuration="1/{fps}s" width="{W}" height="{H}"/>',
           '<effect id="r9" name="Basic Title" uid=".../Titles.localized/Bumper:Opener.localized/Basic Title.localized/Basic Title.moti"/>',
           f'<asset id="a0" name="film_silent" start="0s" duration="{fr(D)}" hasVideo="1" format="r1"><media-rep kind="original-media" src="{(out / "film_silent.mp4").resolve().as_uri()}"/></asset>']
    for k, n in enumerate(stems, 1):
        res.append(f'<asset id="a{k}" name="{n}" start="0s" duration="{fr(D)}" hasAudio="1" audioSources="1" audioChannels="2" audioRate="48000">'
                   f'<media-rep kind="original-media" src="{(out / (n + ".wav")).resolve().as_uri()}"/></asset>')
    conn = [f'<asset-clip ref="a{k}" lane="-{k}" offset="0s" name="{n}" duration="{fr(D)}" start="0s" audioRole="{"dialogue" if n == "voice" else ("music" if n == "music" else "effects")}"/>'
            for k, n in enumerate(stems, 1)]
    for i, (a, b, txt) in enumerate(caps):
        conn.append(f'<title ref="r9" lane="1" offset="{fr(a)}" name="cap {i + 1}" duration="{fr(max(b - a, 1 / fps))}" start="0s">'
                    f'<text><text-style ref="ts{i}">{html.escape(txt)}</text-style></text>'
                    f'<text-style-def id="ts{i}"><text-style font="PingFang SC" fontSize="{int(H * 0.045)}" fontColor="1 1 1 1" bold="1" alignment="center"/></text-style-def></title>')
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n<fcpxml version="1.9">\n<resources>\n' + "\n".join(res) + "\n</resources>\n"
           f'<library><event name="hat9-motion"><project name="{html.escape(title)}"><sequence format="r1" duration="{fr(D)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">'
           f'<spine><asset-clip ref="a0" offset="0s" name="film_silent" duration="{fr(D)}" start="0s">\n' + "\n".join(conn) +
           "\n</asset-clip></spine></sequence></project></event></library>\n</fcpxml>\n")
    (out / "timeline.fcpxml").write_text(xml, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("build"); ap.add_argument("--render", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    build, out = Path(a.build), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    page = (build / "index.html").read_text()
    D = float(re.search(r'id="root"[^>]*data-duration="([\d.]+)"', page).group(1))
    W = int(re.search(r'data-width="(\d+)"', page).group(1)); H = int(re.search(r'data-height="(\d+)"', page).group(1))
    title = re.search(r"<title>(.*?)</title>", page).group(1)
    groups = {"voice": [], "music": [], "sfx": []}
    for cid, src, st, du, ms, vol, rest in AUDIO.findall(page):
        fi = re.search(r'data-fade-in="([\d.]+)"', rest); fo = re.search(r'data-fade-out="([\d.]+)"', rest)
        g = "voice" if cid == "voice" else ("music" if cid.startswith("music") else "sfx")
        groups[g].append((src, float(st), float(du), float(ms or 0), float(vol), float(fi.group(1)) if fi else 0, float(fo.group(1)) if fo else 0))
    run("ffmpeg", "-v", "error", "-y", "-i", a.render, "-an", "-c:v", "copy", str(out / "film_silent.mp4"))
    for n, clips in groups.items(): stem(build, clips, D, out / f"{n}.wav")
    if (build / "captions.srt").exists(): shutil.copy2(build / "captions.srt", out / "captions.srt")
    fps = 30
    fcpxml(out, D, W, H, fps, title, list(groups), srt_items(out / "captions.srt"))
    print(f"{out}: film_silent.mp4 · voice/music/sfx.wav ({sum(len(v) for v in groups.values())} clips) · captions.srt · timeline.fcpxml ({D:.2f} s, {W}x{H})")


if __name__ == "__main__":
    main()
