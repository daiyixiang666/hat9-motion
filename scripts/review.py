#!/usr/bin/env python3
"""Pre-delivery review of a rendered film: contact sheets to look at, plus the checks a viewer would complain about.

  python3 scripts/review.py work/renders/press_9x16.mp4 [--video work/video.json] [--ref ref.mp4] [--out work/review] [--strict]
  python3 scripts/review.py --gate work/renders/review_press_9x16/review.md      # delivery gate: every score filled and ≥ 8

Writes <out>/sheet_NN.jpg (2 frames per second, time-stamped) and <out>/review.md, and prints the findings:
  freeze        the picture does not change for more than 2.5 s                       (P0)
  hook          nothing changes in the first 2 s                                      (P0)
  slides        share of frames that are a flat ground with a little text (PPT look)  (P0 above 30 %)
  caption-dup   on-screen big text that only repeats the spoken line                  (P1, P0 above 30 % of text beats)
  cut-gap       more than 6 s without a cut or a big change                           (P1)
  fx-repeat     the same effect used more than 3 times                                (P1)
  form-repeat   with --video: the same layout family on 2 neighbouring beats             (P1)
  slogan-share  with --video: share of full-frame slogan beats                            (P1 above 25 %, P0 above 40 %)
  form-variety  with --video: fewer than 5 layout families in a film over 60 s           (P1)
  number-repeat with --video: two neighbouring beats that are each a big number + small caption (P1)
                (families: scripts/h9/form_families.json; `review.py --video video.json` alone runs only these)
  loudness      integrated loudness outside -16…-12 LUFS, or true peak above -1 dBTP     (P1)
  dead-air      more than 1.2 s of silence inside the film                              (P1)
  pace          with --ref: the film's median shot is longer than the reference's p75   (P1)
  av-sync       with --video and measured music beats: share of picture cuts in voiceless (music-forward) stretches
                that land within ±2 frames of a beat (P1 below 70 %), and sfx whose visual hit is off by > 2 frames (P1)
  music-level   with --video and its build folder: the music bed under speech vs the voice, and in the gaps
                (P1 when the bed is less than 10 dB under the voice)
  with --video and its build folder (also run by `brief.py check`, before any render):
  caption-frag  caption pages under 4 glyphs or cut inside a word / number / English run   (P1, P0 above 15 % of pages)
  sync-head     a beat's headline (text / title / big) spoken > 1 s after the beat starts, or before it   (P1, P0 above 3 beats)
  text-on-face  real presenter footage at "full" under an effect not made to sit on a person   (P1)
  tiny-text     font sizes under 28 px (9:16, 1080 wide) / 22 px (16:9) in the built page      (P1)
  contrast      sampled caption band / big-text frames under 3:1 text-vs-ground contrast    (P1)
Then look at every sheet and score the rubric in review.md (references/director.md); deliver only when every score ≥ 8.
Needs ffmpeg and Pillow.
"""
import argparse, json, re, subprocess, sys, tempfile
from array import array
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h9.beatsync import flat  # noqa: E402,F401  (re-exported: montage.py and older callers use review.flat)
from h9 import forms  # noqa: E402

TEXT_FX = {"stomp", "black_slam", "tracking", "word_swap", "lockup", "mask_up", "flying_words", "text_mask", "typewriter",
           "scramble", "ghost_type", "write_on", "handwrite", "vertical_title", "glitch", "neon", "shine", "apple_blur", "diffuse"}
PUN = re.compile(r"[\s，。、；：！？,.;:!?…—“”‘’（）()《》「」*·\-]")


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)])
    return float(out.strip())


def freezes(path, dur):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "scale=270:-2,freezedetect=n=-48dB:d=2.5", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = []
    start = None
    for line in r.stderr.splitlines():
        if "freeze_start:" in line:
            start = float(line.split("freeze_start:")[1].split()[0])
        if "freeze_end:" in line and start is not None:
            out.append((start, float(line.split("freeze_end:")[1].split()[0])))
            start = None
    if start is not None:
        out.append((start, dur))
    return out


def scene_changes(path):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(path), "-vf", "scale=270:-2,select='gt(scene,0.14)',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m.group(1)) for m in re.finditer(r"pts_time:([0-9.]+)", r.stderr)]


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[0-9.]+) LUFS", tail)
    p = re.search(r"Peak:\s+(-?[0-9.]+) dBFS", tail)
    return (float(i.group(1)) if i else None), (float(p.group(1)) if p else None)


def silences(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "silencedetect=n=-45dB:d=1.2", "-vn", "-f", "null", "-"], capture_output=True, text=True)
    out = []
    start = None
    for line in r.stderr.splitlines():
        if "silence_start:" in line:
            start = float(line.split("silence_start:")[1].split()[0])
        if "silence_end:" in line and start is not None:
            out.append((start, float(line.split("silence_end:")[1].split()[0].rstrip("|"))))
            start = None
    return out


def has_audio(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", str(path)])
    return bool(out.strip())


def gate(md):
    """the delivery gate: every rubric row scored, every score ≥ 8, the three worst problems written down."""
    text = Path(md).read_text(encoding="utf-8")
    problems = []
    rows = [l for l in text.splitlines() if l.startswith("| ") and "：" in l.split("|")[1]]
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        name = cells[0].split("：")[0]
        score = cells[1] if len(cells) > 1 else ""
        if not score:
            problems.append(f"{name} 没打分")
        elif not score.replace(".", "").isdigit() or float(score) < 8:
            problems.append(f"{name} {score} 分（< 8）")
    if "**P0**" in text:
        problems.append("自动检查还有 P0")
    worst = re.findall(r"^\d\. (.+)$", text, re.M)
    if len([w for w in worst if w.strip()]) < 3:
        problems.append("没写最差的 3 个问题")
    return problems


def frames(path, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-vf", "fps=2,scale=216:-2", str(Path(tmp) / "f_%05d.jpg")], check=True)
    return sorted(Path(tmp).glob("f_*.jpg"))


def sheets(files, out):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.load_default(18)
    cols, rows = 10, 4
    per = cols * rows
    w, h = Image.open(files[0]).size
    made = []
    for s in range(0, len(files), per):
        chunk = files[s:s + per]
        board = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), (24, 24, 24))
        d = ImageDraw.Draw(board)
        for i, f in enumerate(chunk):
            x = (i % cols) * (w + 4)
            y = (i // cols) * (h + 4)
            board.paste(Image.open(f), (x, y))
            t = (s + i) / 2
            d.rectangle([x, y, x + 54, y + 22], fill=(0, 0, 0))
            d.text((x + 4, y + 2), f"{t:.1f}s", fill=(255, 220, 0), font=font)
        p = out / f"sheet_{len(made) + 1:02d}.jpg"
        board.save(p, quality=85)
        made.append(p)
    return made


def label_font(size):
    """a font that can draw Chinese labels on boards: the skill's Noto Sans SC, else the system's, else Pillow's default."""
    from PIL import ImageFont
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from h9 import fonts
    cands = [fonts.find("NotoSansSC-VF.ttf"), fonts.find("HarmonyOS_Sans_SC_Bold.ttf"),
             Path("/System/Library/Fonts/PingFang.ttc"), Path("/System/Library/Fonts/STHeiti Medium.ttc"),
             Path("C:/Windows/Fonts/msyh.ttc"), Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")]
    for c in cands:
        if c and Path(c).exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default(size)


def load_words(vpath):
    """the flat word list [{w, s, e}] named by meta.words, or [] when there is none."""
    meta = json.loads(vpath.read_text()).get("meta", {})
    if not meta.get("words"):
        return []
    data = json.loads((vpath.parent / meta["words"]).read_text())
    return [w for x in data for w in (x["words"] if "words" in x else [x])]


def spoken(words, a, b):
    return "".join(w["w"] for w in words if a - 0.1 <= w["s"] < b)


def screen_text(beat):
    parts = []
    for k in ("words", "hits", "text", "pre", "post", "sub"):
        v = beat.get(k)
        if isinstance(v, list):
            parts += [str(x) for x in v]
        elif isinstance(v, str):
            parts.append(v)
    return PUN.sub("", "".join(parts))


def caption_dups(vpath):
    v = json.loads(vpath.read_text())
    words = load_words(vpath)
    if not words:
        return [], 0
    beats = [b for b in v["beats"] if isinstance(b.get("t"), (int, float))]
    dups, texty = [], 0
    for i, b in enumerate(beats):
        if b.get("fx") not in TEXT_FX:
            continue
        txt = screen_text(b)
        if not txt:
            continue
        texty += 1
        end = beats[i + 1]["t"] if i + 1 < len(beats) else b["t"] + 6
        line = PUN.sub("", spoken(words, b["t"], end + 1.0))
        if all(ch in line for ch in txt):
            dups.append((b["t"], b["fx"], txt))
    return dups, texty


def build_dir(film, vpath, given=None):
    """the build folder a render came from: renders/<style>_<aspect>.mp4 ↔ build/<style>_<aspect>/."""
    if given: return Path(given).resolve()
    d = vpath.parent / "build" / film.stem
    return d if (d / "index.html").exists() else None


def sync_facts(vpath, bdir):
    """(fps, beat grid, speech spans, music-up windows, sfx hits) from the build's timeline.json; falls back to the
    beats.json next to meta.music and the words shifted by meta.lead. None when the film has no measured beats."""
    tl = {}
    if bdir and (bdir / "timeline.json").exists():
        tl = json.loads((bdir / "timeline.json").read_text())
    if tl.get("grid"):
        return tl.get("fps", 30), tl["grid"], tl.get("speech", []), tl.get("music_up", []), tl.get("sfx", [])
    from h9 import beatsync, pacing
    meta = json.loads(vpath.read_text()).get("meta", {})
    if isinstance(meta.get("music"), str):
        meta["music"] = beatsync._path(meta["music"], vpath.parent)
    try: info = beatsync.load(meta, vpath.parent)
    except SystemExit: info = None
    if not info: return None
    lead = float(meta.get("lead") or 0)
    words = [dict(w, s=w["s"] + lead, e=w["e"] + lead) for w in load_words(vpath)]
    return meta.get("fps", 30), info["beats"], pacing.speech_spans(words) if words else [], [], []


def in_spans(t, spans, pre=0.0, post=0.0):
    for x in spans:
        if x[0] - pre <= t <= x[1] + post: return True
    return False


def gray_frames(path, fps, w=64):
    """every frame of the film as a small grey image (bytes), for frame-exact hit checks."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:-2", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    size = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0",
                                    str(path)], text=True).strip().split(",")
    h = int(round(int(size[1]) * w / int(size[0]) / 2) * 2)
    n = w * h
    return [raw[i:i + n] for i in range(0, len(raw) - n + 1, n)]


def hit_offset(frames, fps, t, kind):
    """frames from the sfx time to the strongest visual hit of its kind within ±6 frames (None when nothing shows)."""
    k0 = int(round(t * fps))
    best, best_k = 0.0, None
    for k in range(max(1, k0 - 6), min(len(frames), k0 + 7)):
        a, b = frames[k - 1], frames[k]
        if kind in ("flash", "dark"):
            ma = sum(a) / len(a)
            mb = sum(b) / len(b)
            v = (mb - ma) if kind == "flash" else (ma - mb)
        else:
            diff = 0
            for i in range(0, len(a), 4):
                diff += abs(a[i] - b[i])
            v = diff / (len(a) / 4)
        if v > best:
            best, best_k = v, k
    if best_k is None or best < 3: return None
    return best_k - k0


def pcm(src, sr=8000):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    a = array("f")
    a.frombytes(raw[:len(raw) // 4 * 4])
    return a


def music_levels(bdir, speech, dur, sr=8000):
    """(voice dB, music dB under speech, music dB in voiceless stretches) of the placed audio clips in index.html."""
    import math
    html = (bdir / "index.html").read_text()
    clips = []
    for tag in re.findall(r"<audio [^>]*>", html):
        at = dict(re.findall(r'([\w-]+)="([^"]*)"', tag))
        cid = at.get("id", "")
        if cid == "voice" or cid.startswith("music"):
            clips.append(at)
    if not any(c["id"] == "voice" for c in clips) or not any(c["id"].startswith("music") for c in clips): return None
    n = int(dur * sr)
    tracks = {"voice": [0.0] * n, "music": [0.0] * n}
    for c in clips:
        x = pcm(bdir / c["src"], sr)
        st, d = float(c.get("data-start", 0)), float(c.get("data-duration", dur))
        ms, vol = float(c.get("data-media-start", 0)), float(c.get("data-volume", 1))
        fi, fo = float(c.get("data-fade-in", 0)), float(c.get("data-fade-out", 0))
        dst = tracks["voice" if c["id"] == "voice" else "music"]
        i0 = int(st * sr)
        i1 = min(n, int((st + d) * sr))
        off = int(ms * sr) - i0
        for i in range(i0, i1):
            j = i + off
            if j < 0 or j >= len(x): continue
            g = vol
            tt = i / sr - st
            if fi and tt < fi: g *= tt / fi
            if fo and d - tt < fo: g *= max(0.0, d - tt) / fo
            dst[i] += x[j] * g
    def rms(tr, want_speech):
        acc, cnt = 0.0, 0
        for i in range(sr, n - 2 * sr, 4):          # skip the fades at both ends
            if in_spans(i / sr, speech, 0.05, 0.05) != want_speech: continue
            if not want_speech and in_spans(i / sr, speech, 0.6, 0.6): continue    # release / attack ramps are not the gap level
            acc += tr[i] * tr[i]
            cnt += 1
        return 10 * math.log10(acc / cnt + 1e-12) if cnt > 200 else None
    return rms(tracks["voice"], True), rms(tracks["music"], True), rms(tracks["music"], False)


def av_checks(film, vpath, bdir, cuts, dur, found):
    facts = sync_facts(vpath, bdir)
    if facts:
        fps, grid, speech, ups, hits = facts
        tol = 2 / fps + 0.5 / fps
        last = grid[-1] if grid else 0
        free = [c for c in cuts if 0.5 < c < min(dur - 0.5, last + 0.3)
                and (not in_spans(c, speech, 0.15, 0.3) or in_spans(c, [u[:2] for u in ups]))]
        on = [c for c in free if any(abs(c - g) <= tol for g in grid)]
        offs = []
        for c in free:
            near = min(grid, key=lambda g: abs(g - c))
            offs.append(round((c - near) * fps))
        print(f"  卡拍：无人声段 {len(on)}/{len(free)} 刀落在节拍 ±2 帧内" + (f"（偏差帧数 {offs}）" if free else ""))
        if len(free) >= 3 and len(on) / len(free) < 0.70:
            bad = [f"{c:.2f}s" for c in free if c not in on][:8]
            found.append(("P1", "av-sync", f"无人声段只有 {len(on)}/{len(free)} 刀卡在拍上（±2 帧）：{'、'.join(bad)}"))
        hits = [h for h in hits if h.get("hit")]
        if hits:
            frames = gray_frames(film, fps)
            for h in hits:
                k = hit_offset(frames, fps, h["t"], h["hit"])
                if k is None:
                    found.append(("P1", "av-sync", f"{h['t']:.2f}s 音效 {h['name']} 的画面冲击（{h['hit']}）看不出来"))
                elif abs(k) > 2:
                    found.append(("P1", "av-sync", f"{h['t']:.2f}s 音效 {h['name']} 和画面冲击差 {k:+d} 帧"))
            print(f"  音画：{len(hits)} 个带画面冲击的音效已逐帧核对")
    if bdir:
        speech = facts[2] if facts else None
        if speech is None:
            from h9 import pacing
            meta = json.loads(vpath.read_text()).get("meta", {})
            lead = float(meta.get("lead") or 0)
            words = [dict(w, s=w["s"] + lead, e=w["e"] + lead) for w in load_words(vpath)]
            speech = pacing.speech_spans(words) if words else []
        lv = music_levels(bdir, speech, dur) if speech else None
        if lv and lv[0] is not None and lv[1] is not None:
            v, m_sp, m_gap = lv
            gap_s = f"，无人声处 {m_gap:.1f} dB（比说话时高 {m_gap - m_sp:.1f} dB）" if m_gap is not None else ""
            print(f"  配乐：人声 {v:.1f} dB，说话时配乐 {m_sp:.1f} dB（低 {v - m_sp:.1f} dB）{gap_s}")
            if v - m_sp < 10:
                found.append(("P1", "music-level", f"说话时配乐只比人声低 {v - m_sp:.1f} dB（至少 10–12 dB）：调低 music_volume 或开 duck"))


def timeline_for(vpath, bdir=None):
    """the build's timeline.json (beat times) when there is one, else None."""
    if bdir and (Path(bdir) / "timeline.json").exists():
        return json.loads((Path(bdir) / "timeline.json").read_text())
    builds = sorted((vpath.parent / "build").glob("*/timeline.json"))
    if builds:
        return json.loads(builds[0].read_text())
    return None


# ------------------------------------------------------------------ automatic gates on the built project
# They read what the build actually produced (index.html caption pages, beat times, CSS sizes), so they hold
# whatever model wrote the video.json and whatever the caption builder does today.

ON_PERSON_FX = {"lower3", "key_card", "side_stat", "stack_build", "strike_fix", "chip_cycle", "talking_head", "host_point"}
FACE_SCENES = {"statement", "title", "quote", "number", "compare"}
FOOTAGE_EXT = (".mp4", ".mov", ".m4v", ".webm", ".mkv")


def core_chars(text):
    """the glyphs a viewer reads: letters, digits and CJK; punctuation, spaces and markup dropped."""
    out = []
    for ch in str(text):
        if is_core(ch):
            out.append(ch)
    return out


def is_core(ch):
    return ch.isalnum() or ch in "%％"


def is_ascii_alnum(ch):
    return ch.isascii() and ch.isalnum()


def caption_pages(bdir):
    """[(start, duration, text)] of the on-screen caption pages in the build's index.html (bilingual lines excluded)."""
    import html as htmlmod
    if not bdir or not (Path(bdir) / "index.html").exists():
        return []
    doc = (Path(bdir) / "index.html").read_text(encoding="utf-8")
    pages = []
    for m in re.finditer(r'<div id="cap(\d+)" class="clip cap[^"]*" data-start="([0-9.]+)" data-duration="([0-9.]+)"[^>]*>(.*?)</div>', doc):
        inner = m.group(4)
        inner = re.sub(r'<b class="spkn">.*?</b>', "", inner)
        inner = re.sub(r"<[^>]+>", "", inner)
        text = htmlmod.unescape(inner)
        pages.append((float(m.group(2)), float(m.group(3)), text))
    pages.sort()
    return pages


def _word_boundaries(core_list, soft):
    """positions j (a cut between core[j-1] and core[j]) that are word boundaries, from jieba; None when jieba is missing."""
    import warnings
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import jieba
    except ImportError:
        return None
    jieba.setLogLevel(60)
    cuts = set()
    start = 0
    n = len(core_list)
    for j in range(1, n + 1):
        if j == n or soft[j]:
            chunk = "".join(core_list[start:j])
            pos = start
            for tok in jieba.cut(chunk):
                pos += len(tok)
                cuts.add(pos)
            cuts.add(start)
            start = j
    return cuts


def caption_fragments(vpath, bdir):
    """caption pages that are fragments: under 4 glyphs (unless a whole clause between punctuation), or cut inside a
    word / an ASCII run. → (findings, n_pages, n_fragments, used_jieba)"""
    pages = caption_pages(bdir)
    if not pages:
        return [], 0, 0, False
    video = json.loads(vpath.read_text())
    fixes = video.get("meta", {}).get("caption_fix") or {}
    words = load_words(vpath)
    script = ""
    for w in words:
        script += str(w["w"])
    for k in fixes:
        script = script.replace(k, fixes[k])
    # transcript as core glyphs + whether punctuation / a space sits before each one
    core_list = []
    soft = []
    gap = True
    for ch in script:
        if is_core(ch):
            core_list.append(ch)
            soft.append(gap)
            gap = False
        else:
            gap = True
    core_str = "".join(core_list)
    soft.append(True)              # the end of the script is a boundary
    cuts = _word_boundaries(core_list, soft) if core_list else None
    # place each page in the transcript, in order
    where = []
    ptr = 0
    for st, du, text in pages:
        pc = "".join(core_chars(text))
        idx = -1
        if pc and core_str:
            idx = core_str.find(pc, ptr)
            if idx < 0 or idx - ptr > 40:
                idx = -1
        if idx >= 0:
            where.append((idx, idx + len(pc)))
            ptr = idx + len(pc)
        else:
            where.append(None)
    bad = []
    for i in range(len(pages)):
        st, du, text = pages[i]
        n = len(core_chars(text))
        if n == 0:
            continue
        pos = where[i]
        reason = ""
        if n < 4:
            whole = pos is not None and soft[pos[0]] and soft[pos[1]]
            if not whole:
                reason = f"{n} 字"
        if pos is not None and not reason:
            j = pos[1]
            if 0 < j < len(core_list) and not soft[j]:
                if is_ascii_alnum(core_list[j - 1]) and is_ascii_alnum(core_list[j]):
                    reason = "切在英文 / 数字中间"
                elif core_list[j - 1].isdigit() and core_list[j].isdigit():
                    reason = "切在数字中间"
                elif cuts is not None and j not in cuts:
                    reason = "切在词中间"
        if reason:
            bad.append((st, text.strip(), reason))
    found = []
    share = len(bad) / max(1, len(pages))
    if bad:
        level = "P0" if share > 0.15 else "P1"
        examples = []
        for st, text, reason in bad[:8]:
            examples.append(f"{st:.1f}s「{text}」{reason}")
        found.append((level, "caption-frag", f"{len(bad)}/{len(pages)}（{share:.0%}）页字幕是碎片：" + "；".join(examples)
                      + "。每页一个完整意群（≥4 字，不切词）"))
    return found, len(pages), len(bad), cuts is not None


def _spoken_index(bdir, vpath, lead):
    """(core glyph string, time of each glyph) in film time: from the caption pages when there are any, else the words."""
    chars = []
    times = []
    pages = caption_pages(bdir)
    if pages:
        for st, du, text in pages:
            cc = core_chars(text)
            n = len(cc)
            for k in range(n):
                chars.append(cc[k])
                times.append(st + 2 / 30 + du * k / max(1, n))
        return "".join(chars), times
    for w in load_words(vpath):
        cc = core_chars(w["w"])
        n = len(cc)
        for k in range(n):
            chars.append(cc[k])
            times.append(float(w["s"]) + lead + (float(w["e"]) - float(w["s"])) * k / max(1, n))
    return "".join(chars), times


def _headline(beat):
    for key in ("text", "title", "big"):
        v = beat.get(key)
        if isinstance(v, list):
            v = "".join(str(x) for x in v)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def graphics_timing(vpath, bdir, tl):
    """each beat's headline (text / title / big) should be spoken within 1 s after the beat starts — not seconds
    later (graphic shows too early) and not before it (graphic shows too late)."""
    video = json.loads(vpath.read_text())
    if not tl:
        return []
    spoken_str, times = _spoken_index(bdir, vpath, float(tl.get("lead") or 0))
    if not spoken_str:
        return []
    off = []
    for b, x in zip(video["beats"], tl["beats"]):
        head = "".join(core_chars(_headline(b)))
        if len(head) < 2:
            continue
        needle = head
        if spoken_str.find(needle) < 0:
            needle = ""
            if len(head) > 4:
                for k in range(0, len(head) - 3):
                    win = head[k:k + 4]
                    if spoken_str.find(win) >= 0:
                        needle = win
                        break
        if not needle:
            continue               # not spoken at all: caption-dup / big-text rules cover it
        best = None
        pos = spoken_str.find(needle)
        while pos >= 0:
            delta = times[pos] - x["t"]
            if best is None or abs(delta) < abs(best):
                best = delta
            pos = spoken_str.find(needle, pos + 1)
        if best is None or abs(best) > 8.0:
            continue
        if best > 1.0:
            off.append((x["i"], x["t"], head, f"画面早 {best:.1f}s（字先出，话后到）"))
        elif best < -0.3:
            off.append((x["i"], x["t"], head, f"画面晚 {-best:.1f}s（话说完才出）"))
    found = []
    if len(off) > 3:
        items = []
        for i, t, head, why in off[:8]:
            items.append(f"#{i} {t:.1f}s「{head[:10]}」{why}")
        found.append(("P0", "sync-head", f"{len(off)} 个 beat 的大字和口播对不上：" + "；".join(items)
                      + "。把 t 写成 \"@词\" 锚到说出大字的那个词"))
    else:
        for i, t, head, why in off:
            found.append(("P1", "sync-head", f"#{i} {t:.1f}s「{head[:10]}」{why}：t 用 \"@词\" 锚到说出它的词"))
    return found


def presenter_is_footage(meta):
    p = meta.get("presenter")
    src = p.get("src", "") if isinstance(p, dict) else (p or "")
    return str(src).lower().endswith(FOOTAGE_EXT)


def text_on_face(vpath, tl):
    """real presenter footage: the build moves the speaker off any graphic that needs room (presenter.effective_places);
    what is left on the face is a beat kept full with "presenter_force" (dimmed footage + light text) → check it by eye."""
    from h9 import presenter
    video = json.loads(vpath.read_text())
    meta = video.get("meta", {})
    if not presenter_is_footage(meta):
        return []
    portrait = str(meta.get("aspect", "9:16")) in ("9:16", "3:4", "4:5")
    places = presenter.effective_places(video, portrait)
    found = []
    beat_times = tl["beats"] if tl else []
    for i in range(len(places)):
        place, forced = places[i]
        if not forced:
            continue
        b = video["beats"][i]
        name = b.get("fx") if b.get("scene") == "fx" else b.get("scene")
        t = beat_times[i]["t"] if i < len(beat_times) else 0.0
        found.append(("P1", "text-on-face", f"#{i} {t:.1f}s {name} 用 presenter_force 留在全屏真人上（已压暗）：看静帧确认字读得清、没挡脸"))
    return found


def _px(num, unit):
    v = float(num)
    if unit == "px":
        return v
    if unit == "vmin":
        return v * 10.8                 # the layout frame is 1080 × 1920 or 1920 × 1080: 1 vmin = 10.8 px
    return None


def tiny_text(bdir, portrait):
    """font sizes in the built index.html below 28 px (9:16, 1080 wide) or 22 px (16:9, 1920 × 1080)."""
    if not bdir or not (Path(bdir) / "index.html").exists():
        return []
    doc = (Path(bdir) / "index.html").read_text(encoding="utf-8")
    limit = 28 if portrait else 22
    other = "#root.h" if portrait else "#root.v"
    small = {}
    size_re = re.compile(r"(?:^|[;{\s])font-size\s*:\s*([0-9.]+)(px|vmin)")
    short_re = re.compile(r"(?:^|[;{\s])font\s*:\s*([^;}]*)")
    num_re = re.compile(r"([0-9.]+)(px|vmin)")

    def sizes_in(decl):
        out = []
        for m in size_re.finditer(decl):
            out.append(_px(m.group(1), m.group(2)))
        for m in short_re.finditer(decl):
            n = num_re.search(m.group(1))
            if n:
                out.append(_px(n.group(1), n.group(2)))
        return out

    for block in re.findall(r"<style[^>]*>(.*?)</style>", doc, re.S):
        block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block):
            sel = " ".join(m.group(1).split())
            if other in sel or sel.startswith("@"):
                continue
            for v in sizes_in(m.group(2)):
                if v is not None and 6 <= v < limit:
                    key = sel[:60]
                    if key not in small or v < small[key]:
                        small[key] = v
    for m in re.finditer(r'<(\w+)([^>]*?)\sstyle="([^"]*)"', doc):
        cls = re.search(r'class="([^"]*)"', m.group(2))
        name = "." + ".".join(cls.group(1).split()) if cls else m.group(1)
        for v in sizes_in(m.group(3)):
            if v is not None and 6 <= v < limit:
                key = f"{name[:50]} (inline)"
                if key not in small or v < small[key]:
                    small[key] = v
    if not small:
        return []
    items = []
    for sel in small:
        items.append((small[sel], sel))
    items.sort()
    shown = []
    for v, sel in items[:8]:
        shown.append(f"{sel} {v:.0f}px")
    frame = "9:16 1080 宽" if portrait else "16:9 1920×1080"
    return [("P1", "tiny-text", f"{len(items)} 处字号小于 {limit}px（{frame}，手机上读不清）：" + "；".join(shown))]


def static_checks(vpath, bdir, tl=None, portrait=None):
    """the gates that need only the build (no render): caption fragments, headline sync, text on face, tiny text."""
    found = []
    if tl is None:
        tl = timeline_for(vpath, bdir)
    if portrait is None:
        meta = json.loads(vpath.read_text()).get("meta", {})
        portrait = "9x16" in str(bdir) or meta.get("aspect") == "9:16"
    frag, n_pages, n_bad, used_jieba = caption_fragments(vpath, bdir)
    found += frag
    if n_pages and not used_jieba:
        found.append(("P1", "caption-frag", "没装 jieba，查不出切在词中间的字幕：pip install jieba"))
    found += graphics_timing(vpath, bdir, tl)
    found += text_on_face(vpath, tl)
    found += tiny_text(bdir, portrait)
    return found


def _lum(v):
    c = v / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def _ratio(a, b):
    la = _lum(a)
    lb = _lum(b)
    hi = max(la, lb)
    lo = min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def region_contrast(img, box, tail):
    """WCAG-style contrast of the text against its ground in one region of a grey frame: the ground is the median,
    the text is whichever extreme (the `tail` share of brightest or darkest pixels) stands further from it."""
    crop = img.crop(box)
    hist = crop.histogram()
    total = sum(hist)
    if total == 0:
        return None

    def pct(q):
        want = total * q
        acc = 0
        for v in range(256):
            acc += hist[v]
            if acc >= want:
                return v
        return 255
    mid = pct(0.5)
    dark = pct(tail)
    light = pct(1 - tail)
    return max(_ratio(light, mid), _ratio(dark, mid))


def contrast_check(film, vpath, bdir, tl):
    """sample caption pages and text-only beats in the render; text vs ground under 3:1 → P1."""
    from PIL import Image
    pages = caption_pages(bdir)
    video = json.loads(vpath.read_text())
    size = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", str(film)], text=True).strip().split(",")
    W = int(size[0])
    H = int(size[1])
    portrait = H > W
    probes = []                   # (time, what, box in a 540-wide frame, tail)
    sw = 540
    sh = int(round(H * sw / W))
    if portrait:
        band = (int(sw * 0.08), int(sh * 0.66), int(sw * 0.92), int(sh * 0.80))
    else:
        band = (int(sw * 0.10), int(sh * 0.84), int(sw * 0.90), int(sh * 0.97))
    step = max(1, len(pages) // 12)
    for k in range(0, len(pages), step):
        st, du, text = pages[k]
        probes.append((st + min(du * 0.6, 0.6), f"字幕「{text.strip()[:8]}」", band, 0.005))
    if tl:
        cats = {}
        try:
            data = json.loads((Path(__file__).resolve().parent.parent / "gallery" / "effects.json").read_text())
            for e in data["effects"]:
                cats[e["id"]] = e.get("cat", "")
        except (OSError, ValueError, KeyError):
            pass
        for b, x in zip(video["beats"], tl["beats"]):
            texty = b.get("scene") in ("statement", "title", "quote")
            if b.get("scene") == "fx" and (b.get("fx") in TEXT_FX or cats.get(b.get("fx")) == "字效"):
                texty = True
            if texty:
                box = (int(sw * 0.15), int(sh * 0.2), int(sw * 0.85), int(sh * 0.8))
                probes.append((x["t"] + min(x["d"] * 0.6, 1.5), f"#{x['i']} {b.get('fx') or b.get('scene')} 大字", box, 0.01))
    low = []
    with tempfile.TemporaryDirectory() as tmp:
        for n in range(len(probes)):
            t, what, box, tail = probes[n]
            jpg = Path(tmp) / f"c_{n}.png"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(film), "-frames:v", "1",
                            "-vf", f"scale={sw}:{sh},format=gray", str(jpg)], check=False)
            if not jpg.exists():
                continue
            img = Image.open(jpg).convert("L")
            r = region_contrast(img, box, tail)
            if r is not None and r < 3.0:
                low.append((t, what, r))
    found = []
    for t, what, r in low[:6]:
        found.append(("P1", "contrast", f"{t:.1f}s {what} 对比度约 {r:.1f}:1（< 3:1）：加描边 / 底板，或换深浅相反的底"))
    if len(low) > 6:
        found.append(("P1", "contrast", f"另有 {len(low) - 6} 处对比度不足"))
    return found, len(probes)


def form_only(vpath, strict=False):
    """review.py --video video.json without a film: only the layout-family checks (no render needed)."""
    video = json.loads(vpath.read_text())
    found = forms.lint(video, timeline_for(vpath))
    print(f"  版式：{forms.summary(video)}")
    for lv, rule, msg in found:
        print(f"  {lv} {rule:<12} {msg}")
    if not found:
        print("  版式检查通过")
    if strict:
        for lv, _, _ in found:
            if lv == "P0":
                sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("film", nargs="?")
    ap.add_argument("--gate", metavar="REVIEW_MD", help="check a filled review.md: every score ≥ 8, no P0 left")
    ap.add_argument("--ref", help="a reference film: compare the cutting pace")
    ap.add_argument("--video", help="the video.json it was built from (enables caption-dup and fx-repeat)")
    ap.add_argument("--out")
    ap.add_argument("--build", help="the build folder of this render (default <video dir>/build/<film name>)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when a P0 is found")
    a = ap.parse_args()
    if a.gate:
        problems = gate(a.gate)
        for p in problems:
            print(f"  ✗ {p}")
        print("  ✓ 可以交付" if not problems else "不能交付：改完重新渲染、重新打分")
        sys.exit(1 if problems else 0)
    if not a.film and a.video:
        form_only(Path(a.video).resolve(), a.strict)
        return
    if not a.film:
        ap.error("给一个成片，或用 --gate review.md，或只用 --video video.json 查版式")
    film = Path(a.film).resolve()
    out = Path(a.out).resolve() if a.out else film.parent / f"review_{film.stem}"
    out.mkdir(parents=True, exist_ok=True)
    dur = probe(film)
    found = []

    body_end = dur - 1.5
    for s, e in freezes(film, dur):
        if s < body_end and min(e, body_end) - s > 2.5:
            found.append(("P0", "freeze", f"{s:.1f}–{e:.1f}s 画面 {e - s:.1f} 秒没有变化"))
    cuts = scene_changes(film)
    early = [c for c in cuts if c <= 2.0]
    fr = freezes(film, dur)
    if not early and any(s <= 0.2 and e >= 2.0 for s, e in fr):
        found.append(("P0", "hook", "前 2 秒画面没有任何变化"))
    edges = [0.0] + cuts + [dur]
    for x, y in zip(edges, edges[1:]):
        if y - x > 6.0:
            found.append(("P1", "cut-gap", f"{x:.1f}–{y:.1f}s {y - x:.1f} 秒没有切换"))

    if has_audio(film):
        lufs, peak = loudness(film)
        if lufs is not None and not -16.5 <= lufs <= -11.5:
            found.append(("P1", "loudness", f"整体响度 {lufs:.1f} LUFS（平台约 -14）"))
        if peak is not None and peak > -1.0:
            found.append(("P1", "loudness", f"峰值 {peak:.1f} dBTP，会破音（压到 -1 以下）"))
        for s, e in silences(film):
            if 0.5 < s < body_end:
                found.append(("P1", "dead-air", f"{s:.1f}–{e:.1f}s 没有声音 {e - s:.1f} 秒"))
    if a.ref:
        import ref_pacing
        rb, rd = ref_pacing.cuts(Path(a.ref), 0.3)
        fb, fd = ref_pacing.cuts(film, 0.3)
        rs = ref_pacing.stats(rb, rd)
        fs = ref_pacing.stats(fb, fd)
        if fs["median"] > rs["p75"]:
            found.append(("P1", "pace", f"镜头中位 {fs['median']:.1f}s，参考片 {rs['median']:.1f}s（p75 {rs['p75']:.1f}s）：切得太慢"))
        print(f"  节奏：成片 {fs['per_min']:.0f} 刀/分钟 · 参考 {rs['per_min']:.0f} 刀/分钟")

    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        files = frames(film, tmp)
        flats = [flat(Image.open(f)) > 0.82 for f in files]
        made = sheets(files, out)
    ratio = sum(flats) / max(1, len(flats))
    run, best, best_at = 0, 0, 0
    for i, x in enumerate(flats):
        run = run + 1 if x else 0
        if run > best:
            best, best_at = run, i - run + 1
    if ratio > 0.30:
        found.append(("P0", "slides", f"{ratio:.0%} 的画面是纯色底 + 少量文字（最长一段 {best_at / 2:.1f}s 起 {best / 2:.1f} 秒）"))
    elif ratio > 0.15:
        found.append(("P1", "slides", f"{ratio:.0%} 的画面是纯色底 + 少量文字"))

    if a.video:
        vpath = Path(a.video).resolve()
        dups, texty = caption_dups(vpath)
        if dups:
            level = "P0" if texty and len(dups) / texty > 0.30 else "P1"
            found.append((level, "caption-dup", f"{len(dups)}/{texty} 个大字镜头只是在重复字幕：" +
                          "；".join(f"{t:.1f}s {fx}「{txt}」" for t, fx, txt in dups[:8])))
        counts = {}
        for b in json.loads(vpath.read_text())["beats"]:
            if b.get("scene") == "fx":
                counts[b["fx"]] = counts.get(b["fx"], 0) + 1
        for fx, n in sorted(counts.items(), key=lambda x: -x[1]):
            if n > 3:
                found.append(("P1", "fx-repeat", f"{fx} 用了 {n} 次"))
        form_findings = forms.lint(json.loads(vpath.read_text()), timeline_for(vpath, build_dir(film, vpath, a.build)))
        for item in form_findings:
            found.append(item)
        av_checks(film, vpath, build_dir(film, vpath, a.build), cuts, dur, found)
        bdir = build_dir(film, vpath, a.build)
        tl = timeline_for(vpath, bdir)
        if bdir:
            for item in static_checks(vpath, bdir, tl):
                found.append(item)
            low, n_probe = contrast_check(film, vpath, bdir, tl)
            for item in low:
                found.append(item)
            print(f"  对比度：抽查 {n_probe} 处字幕 / 大字")

    lines = [f"# 自检：{film.name}", "", f"时长 {dur:.1f}s · 静帧板 {len(made)} 张（每秒 2 帧）", "", "## 自动检查", ""]
    lines += [f"- **{lv}** `{rule}` {msg}" for lv, rule, msg in found] or ["- 没有发现自动可查的问题"]
    lines += ["", "## 逐张看静帧板后打分（1–10，每项 ≥ 8 才交付）", "",
              "| 项 | 分 | 最差的地方 |", "|---|---|---|",
              "| 钩子：只看前 2 秒会不会继续看 | | |", "| 手机可读：每屏要读的字读得清 | | |",
              "| 节奏：没有 2.5 秒不变的地方 | | |", "| 信息：画面给出字幕之外的东西 | | |",
              "| 多样：版式 / 颜色 / 效果没有一种用到底 | | |", "| 相关：每个画面和那句话有关 | | |",
              "", "## 最差的 3 个问题 → 怎么改", "", "1. ", "2. ", "3. "]
    (out / "review.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for lv, rule, msg in found:
        print(f"  {lv} {rule:<12} {msg}")
    print(f"静帧板：{', '.join(p.name for p in made)}  →  {out}")
    print(f"逐张看完再按 review.md 打分；每项 ≥ 8 才交付：python3 scripts/review.py --gate {out / 'review.md'}")
    if a.strict and any(lv == "P0" for lv, _, _ in found):
        sys.exit(1)


if __name__ == "__main__":
    main()
