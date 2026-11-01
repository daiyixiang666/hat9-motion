#!/usr/bin/env python3
"""hat9 — 九帽动效的统一命令行。

  python3 scripts/hat9.py doctor                         检查环境（Node / HyperFrames / FFmpeg / Chrome / 字体）
  python3 scripts/hat9.py quick "一段文案" [--aspect 9:16] [--style reel] [--voice my.wav] [--out dir]
                                                         文案 → 自动分镜 → 配音 → 渲染 mp4（60 秒出第一条）
  python3 scripts/hat9.py plan "一段文案" --out dir       只生成 video.json（自动分镜），给 AI / 人再改
  python3 scripts/hat9.py build|render <video.json> [--style s] [--aspect a]
  python3 scripts/hat9.py fx [name]                      列出效果 / 看一个效果的说明和参数
  python3 scripts/hat9.py styles                         列出风格
  python3 scripts/hat9.py pack                           打包单文件 skill + zip
"""
import argparse, json, re, shutil, subprocess, sys, wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))
PY = sys.executable
HF = ["npx", "--yes", "hyperframes@0.8.191"]


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ------------------------------------------------------------------ doctor
def doctor(_):
    ok = True
    def line(name, good, hint=""):
        nonlocal ok
        ok &= bool(good)
        print(f"  {'✓' if good else '✗'} {name}" + ("" if good else f"   → {hint}"))
    print("九帽动效 · 环境检查")
    line(f"Python {sys.version.split()[0]}", sys.version_info >= (3, 9), "需要 Python 3.9+")
    node = shutil.which("node"); line(f"Node.js {sh(['node', '-v']).stdout.strip() if node else ''}", node, "安装 Node.js 22+ (https://nodejs.org)")
    line("FFmpeg", shutil.which("ffmpeg"), "macOS: brew install ffmpeg · Windows: winget install ffmpeg")
    if node:
        r = sh(HF + ["--version"]); line(f"HyperFrames {r.stdout.strip()[:20]}", r.returncode == 0, "首次会自动下载；检查网络后重试")
    from h9 import fonts
    miss = [k for k in ("noto-sans-sc", "noto-serif-sc", "inter", "jetbrains-mono") if not fonts.find(fonts.REG[k]["file"])]
    line("核心字体（思源黑体 / 思源宋体 / Inter / JetBrains Mono）", not miss, f"缺 {', '.join(miss)}：放进 assets/fonts/，地址见 assets/fonts.json")
    for mod, pkg, why in (("fontTools", "fonttools", "字体子集化，渲染更快"), ("jieba", "jieba", "字幕按词断行"),
                          ("faster_whisper", "faster-whisper", "自己的录音自动对齐出逐字时间（scripts/align.py）"),
                          ("whisperx", "whisperx", "更准的强制对齐，二选一即可")):
        try: __import__(mod); print(f"  ✓ {mod}（可选）")
        except ImportError: print(f"  · {mod} 未安装（可选：pip install {pkg}，{why}）")
    print("  · 没装对齐模型也行：scripts/align.py --backend silence 按停顿切分（也可用 --transcript 导入已有逐字时间）")
    opt = [k for k in ("noto-sans-jp", "noto-sans-kr", "noto-sans-tc") if k in fonts.REG and not fonts.find(fonts.REG[k]["file"])]
    if opt: print(f"  · 可选字体未装：{', '.join(opt)}（做日文 / 韩文 / 繁体版时用，地址见 assets/fonts.json；不装也能显示，用系统字体）")
    ven = Path(__file__).resolve().parent.parent / "assets" / "vendor"
    have = all((ven / f).exists() for f in ("d3-array.min.js", "d3-geo.min.js", "topojson-client.min.js"))
    print(f"  {'✓' if have else '·'} 地图库本地副本（assets/vendor，离线也能渲染地图）" + ("" if have else "：没有时从 jsdelivr 加载"))
    print("  · GSAP 始终从 jsdelivr 加载（许可不允许随仓库分发）：完全离线渲染需要本机浏览器缓存过它")
    print("全部就绪 ✓" if ok else "有缺项，按提示补齐后再试")


# ------------------------------------------------------------------ planner: text -> beats
NUM = re.compile(r"(百分之[一二三四五六七八九十百零两\d]+|\d+(?:\.\d+)?\s*[%％倍万亿]|[一二三四五六七八九十百千万]+倍)")
CN = {"零": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}


def cn2num(s):
    s = s.replace("百分之", "")
    if s.isdigit(): return int(s)
    if "十" in s:
        a, _, b = s.partition("十"); return (CN.get(a, 1) if a else 1) * 10 + (CN.get(b, 0) if b else 0)
    return CN.get(s, 0)


def sentences(text):
    parts = re.split(r"(?<=[。！？!?；;])\s*|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def plan(text, aspect="16:9"):
    """one sentence → one beat. Sentence type → effect, chosen from what ranks highest for that job (research/ae_popular.md)."""
    ss = sentences(text)
    beats, rot = [], ["apple_blur", "mask_up", "stomp", "impact", "blur_focus", "tracking", "flip3d"]
    k = 0
    for i, s in enumerate(ss):
        clean = re.sub(r"[，。！？、；：,.!?;:\s]", "", s)
        b = {"scene": "fx", "t": f"@{clean[:3]}"}
        m = NUM.search(s)
        if i == 0:
            b.update(fx="pop" if len(clean) <= 10 else "mask_up", text=_wrap(s))
        elif i == len(ss) - 1 and len(ss) > 2:
            b.update(fx="lower3", text=s.rstrip("。！!"), sub="关注 · 一起练判断")
        elif m:
            raw = m.group(1); unit = "%" if ("百分之" in raw or "%" in raw or "％" in raw) else ("倍" if "倍" in raw else "")
            val = cn2num(raw) if not raw[0].isdigit() else re.match(r"\d+(?:\.\d+)?", raw).group(0)
            b.update(fx="odometer", value=str(val), unit=unit, sub=s.replace(raw, "").strip("，。 "))
        elif re.search(r"有人.+有人|一边.+一边|不是.+而是|不在.+在", s):
            parts = [p for p in re.split(r"[，,]", s) if p]
            b.update(fx="stomp", words=_chunks(s))
        elif len(clean) <= 6:
            b.update(fx="impact", text=clean)
        else:
            fx = rot[k % len(rot)]; k += 1
            if fx == "stomp": b.update(fx=fx, words=_chunks(s))
            else: b.update(fx=fx, text=_wrap(s.rstrip("。")))
        beats.append(b)
    beats[0]["t"] = 0
    for b in beats[1:]: b["tr"] = "hard"
    if len(beats) > 3: beats[len(beats) // 2]["tr"] = "zoomin"
    return {"meta": {"title": ss[0][:12] if ss else "hat9", "aspect": aspect}, "beats": beats}


def _wrap(s, n=10):
    s = s.strip("。！？!? ")
    if len(s) <= n: return s
    cut = max((m.end() for m in re.finditer(r"[，,、]", s) if m.end() <= len(s) - 2), default=len(s) // 2)
    return s[:cut].rstrip("，,、") + "|" + s[cut:]


def _chunks(s):
    """stomp pages: clause by clause; a long clause is cut into ≤4-glyph word groups (never across a comma)."""
    try:
        import jieba
        cut = lambda x: [t for t in jieba.cut(x) if t.strip()]
    except ImportError:
        cut = lambda x: [x[i:i + 2] for i in range(0, len(x), 2)]
    out = []
    for clause in re.split(r"[，,。！？、；;：\s]+", s):
        if not clause: continue
        if len(clause) <= 5: out.append(clause); continue
        cur = ""
        for t in cut(clause):
            if len(cur) + len(t) > 4 and cur: out.append(cur); cur = ""
            cur += t
        if cur: out.append(cur)
    return out[:8]


# ------------------------------------------------------------------ voice: user file > local TTS > macOS say > silent
def voice_for(text, outdir, user=None):
    a = outdir / "assets" / "audio"; a.mkdir(parents=True, exist_ok=True)
    if user:
        dst = a / ("voice" + Path(user).suffix); shutil.copy2(user, dst)
        return dst, None
    clean = re.sub(r"\s+", "", text)
    r = sh([PY, str(HERE / "voice.py"), text, str(a)])                       # edge-tts (word timings)
    if r.returncode == 0 and (a / "words.json").exists(): return a / "voice.mp3", a / "words.json"
    if shutil.which("say"):                                                   # macOS built-in, timings estimated
        aiff = a / "voice.aiff"
        r = sh(["say", "-v", "Tingting", "-r", "210", "-o", str(aiff), text])
        if r.returncode == 0:
            wav = a / "voice.wav"; sh(["ffmpeg", "-v", "error", "-y", "-i", str(aiff), "-ar", "48000", str(wav)]); aiff.unlink(missing_ok=True)
            with wave.open(str(wav)) as w: dur = w.getnframes() / w.getframerate()
            return wav, _estimate_words(clean, dur, a)
    return None, _estimate_words(clean, len(clean) / 4.6, a)                 # silent: ~4.6 字/秒


def _estimate_words(clean, dur, a):
    """spread the script's characters evenly over the audio (pauses at punctuation weigh 2 chars)."""
    weights = [2.0 if ch in "，。！？、；：,.!?;:" else 1.0 for ch in clean]
    total = sum(weights); t = 0.15; per = (dur - 0.3) / total; words = []
    for ch, w in zip(clean, weights):
        words.append({"w": ch, "s": round(t, 3), "e": round(t + per * w, 3)}); t += per * w
    p = a / "words.json"; p.write_text(json.dumps(words, ensure_ascii=False)); return p


def quick(a):
    out = Path(a.out or f"hat9-out/{re.sub(r'[^0-9A-Za-z一-龥]', '', a.text)[:8] or 'video'}").resolve()
    out.mkdir(parents=True, exist_ok=True)
    print(f"① 分镜：{len(sentences(a.text))} 句 → {len(sentences(a.text))} 个画面")
    v = plan(a.text, a.aspect)
    print("② 配音 …")
    wav, words = voice_for(a.text, out, a.voice)
    if wav: v["meta"]["voice"] = str(wav.relative_to(out))
    v["meta"]["words"] = str(words.relative_to(out))
    if not wav:
        v["meta"]["duration"] = round(json.loads(words.read_text())[-1]["e"] + 0.8, 2)
        print("   （没有可用的 TTS，先出静音版；加 --voice 你的录音.wav 即可带声音）")
    (out / "video.json").write_text(json.dumps(v, ensure_ascii=False, indent=1))
    print("③ 渲染 …")
    r = subprocess.run([PY, str(HERE / "render.py"), str(out / "video.json"), "--styles", a.style, "--aspect", a.aspect])
    mp4 = out / "renders" / f"{a.style}_{a.aspect.replace(':', 'x')}.mp4"
    print(f"✓ {mp4}" if mp4.exists() else "渲染没有完成，看上面的报错")
    print(f"  想改哪一句：编辑 {out / 'video.json'} 后运行  python3 scripts/hat9.py render {out / 'video.json'}")


def cmd_plan(a):
    out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    (out / "video.json").write_text(json.dumps(plan(a.text, a.aspect), ensure_ascii=False, indent=1))
    print(out / "video.json")


def fx(a):
    from h9 import aefx
    if a.name:
        f = aefx.FX.get(a.name)
        print((f.__doc__ or "").strip() if f else f"没有 {a.name}")
        return
    for k in sorted(aefx.FX):
        print(f"  {k:<12} {(aefx.FX[k].__doc__ or '').strip().splitlines()[0][:70]}")


def styles(_):
    import importlib.util
    for p in sorted((SKILL / "styles").glob("[!_]*.py")):
        spec = importlib.util.spec_from_file_location(p.stem, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        st = m.STYLE; print(f"  {p.stem:<10} {st.get('name', ''):<8} {' · '.join(st.get('benchmarks', [])[:3])}")


def main():
    ap = argparse.ArgumentParser(prog="hat9", description="九帽动效：文案 → 动效视频")
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("doctor").set_defaults(fn=doctor)
    q = sp.add_parser("quick"); q.add_argument("text"); q.add_argument("--aspect", default="16:9"); q.add_argument("--style", default="reel")
    q.add_argument("--voice"); q.add_argument("--out"); q.set_defaults(fn=quick)
    p = sp.add_parser("plan"); p.add_argument("text"); p.add_argument("--aspect", default="16:9"); p.add_argument("--out", required=True); p.set_defaults(fn=cmd_plan)
    for c in ("build", "render"):
        x = sp.add_parser(c); x.add_argument("video"); x.add_argument("--style"); x.add_argument("--aspect"); x.add_argument("--preview", action="store_true")
        x.set_defaults(fn=lambda a, c=c: subprocess.run([PY, str(HERE / f"{c}.py"), a.video] + (["--style" if c == "build" else "--styles", a.style] if a.style else [])
                                                        + (["--aspect", a.aspect] if a.aspect else []) + (["--preview"] if c == "render" and a.preview else [])))
    f = sp.add_parser("fx"); f.add_argument("name", nargs="?"); f.set_defaults(fn=fx)
    sp.add_parser("styles").set_defaults(fn=styles)
    sp.add_parser("pack").set_defaults(fn=lambda a: subprocess.run([PY, str(HERE / "pack.py")]))
    a = ap.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
