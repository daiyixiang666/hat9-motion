#!/usr/bin/env python3
"""Cut a long talk down to its best minute — from word timestamps, no speech recognition here.

  python3 scripts/cut_list.py talk_words.json --audio talk.wav --target 60 --out work/cut [--keep 关键词,…] [--aspect 9:16]

In:  words.json of the whole talk ([{w,s,e}] or segments; from scripts/align.py or any aligner) + optional audio.
Out (in --out):
  cut.json       the edit decision list: [{src_start, src_end, text, score, why}] in talk order
  voice.wav      the kept sentences joined with short breaths (when --audio is given)
  words.json     word timestamps re-timed to voice.wav
  video.json     a first storyboard of the cut (scripts/hat9.py plan rules), ready for build.py / render.py

Choosing: the talk is split into sentences at 。！？ and at pauses over 0.8 s. Each sentence scores for numbers,
turns (但 / 其实 / 真正 / 关键 / 本质 / 所以 / 原来 …), questions, a quotable length, the --keep terms; filler openers and
very long sentences lose points. The best opener in the first fifth and the best closer in the last fifth are always kept;
the rest fills the target length by score, then everything goes back into talk order.
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PUNCT = "，。、！？；：,.!?;:"
TURN = ("但", "其实", "真正", "关键", "本质", "所以", "原来", "没想到", "核心", "结果", "问题是", "换句话说", "说白了", "重点")
FILLER = ("嗯", "啊", "那个", "就是说", "然后呢", "对吧", "怎么说")
NUM = re.compile(r"\d|[一二两三四五六七八九十百千万亿]+(?:倍|成|%|个|家|元|年|亿|万)|百分之")


def load_words(p):
    data = json.loads(Path(p).read_text())
    ws = []
    for x in data:
        ws += x["words"] if isinstance(x, dict) and "words" in x else [x]
    return [{"w": str(w.get("w", w.get("t", ""))), "s": float(w["s"]), "e": float(w["e"])} for w in ws]


def sentences(ws, pause=0.8):
    out, cur = [], []
    for i, w in enumerate(ws):
        cur.append(w)
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        end = w["w"].strip() and w["w"].strip()[-1] in "。！？!?"
        gap = nxt is not None and nxt["s"] - w["e"] > pause
        if end or gap or nxt is None:
            spoken = [x for x in cur if x["w"].strip() and x["w"].strip() not in PUNCT and x["e"] > x["s"]]
            if spoken:
                text = "".join(x["w"] for x in cur).strip()
                out.append({"src_start": spoken[0]["s"], "src_end": spoken[-1]["e"], "text": text, "words": cur})
            cur = []
    return out


def score(s, keep):
    t = s["text"]
    n = len(re.sub(f"[{PUNCT}\\s]", "", t))
    sc, why = 0.0, []
    if NUM.search(t): sc += 2; why.append("数字")
    if any(k in t for k in TURN): sc += 2; why.append("转折")
    if t.rstrip().endswith(("？", "?")): sc += 1.5; why.append("设问")
    if 8 <= n <= 28: sc += 1; why.append("好记的长度")
    elif n > 40: sc -= 1.5; why.append("太长")
    if any(k and k in t for k in keep): sc += 2.5; why.append("关键词")
    if t.startswith(FILLER): sc -= 1; why.append("口头语开头")
    return sc, why


def pick(ss, target, gap=0.25):
    for s in ss: s["dur"] = s["src_end"] - s["src_start"]
    n = len(ss)
    chosen = set()
    if n:
        head = max(range(max(1, n // 5)), key=lambda i: ss[i]["score"])
        tail = max(range(n - max(1, n // 5), n), key=lambda i: ss[i]["score"])
        chosen |= {head, tail}
    total = sum(ss[i]["dur"] + gap for i in chosen)
    for i in sorted(range(n), key=lambda i: -ss[i]["score"]):
        if i in chosen: continue
        if total + ss[i]["dur"] + gap > target: continue
        chosen.add(i); total += ss[i]["dur"] + gap
    return [ss[i] for i in sorted(chosen)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("words"); ap.add_argument("--audio"); ap.add_argument("--target", type=float, default=60.0)
    ap.add_argument("--out", required=True); ap.add_argument("--keep", default=""); ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--gap", type=float, default=0.25, help="breath between kept sentences (s)")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ws = load_words(a.words)
    ss = sentences(ws)
    keep = [k for k in a.keep.split(",") if k]
    for s in ss: s["score"], s["why"] = score(s, keep)
    kept = pick(ss, a.target, a.gap)
    (out / "cut.json").write_text(json.dumps([{k: s[k] for k in ("src_start", "src_end", "text", "score", "why")} for s in kept], ensure_ascii=False, indent=1))
    # re-time the words onto the joined voice
    words, t = [], 0.0
    for s in kept:
        off = t - s["src_start"]
        for w in s["words"]:
            words.append({"w": w["w"], "s": round(max(t, w["s"] + off), 3), "e": round(max(t, w["e"] + off), 3)})
        t += s["dur"] + a.gap
    (out / "words.json").write_text(json.dumps(words, ensure_ascii=False))
    if a.audio:
        parts, f = [], []
        for k, s in enumerate(kept):
            f.append(f"[0:a]atrim=start={max(0, s['src_start'] - 0.04):.3f}:end={s['src_end'] + 0.08:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={s['dur'] + 0.1:.3f}:d=0.02[c{k}]")
            parts.append(f"[c{k}]")
            if k < len(kept) - 1:
                f.append(f"anullsrc=r=48000:cl=mono,atrim=duration={max(0.0, a.gap - 0.12):.3f}[g{k}]"); parts.append(f"[g{k}]")
        f.append("".join(parts) + f"concat=n={len(parts)}:v=0:a=1,aresample=48000[o]")
        script = out / ".cut_filter.txt"; script.write_text(";".join(f))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.audio, "-filter_complex_script", str(script), "-map", "[o]", "-ac", "1", str(out / "voice.wav")], check=True)
        script.unlink()
    sys.path.insert(0, str(HERE))
    import hat9
    v = hat9.plan("".join(s["text"] for s in kept), a.aspect)
    v["meta"].update({"voice": "voice.wav" if a.audio else None, "words": "words.json", "tail": 0.8,
                      "source_cut": {"from": str(Path(a.words).name), "sentences": len(kept), "of": len(ss)}})
    if not a.audio: v["meta"].pop("voice"); v["meta"]["duration"] = round(t + 0.8, 2)
    (out / "video.json").write_text(json.dumps(v, ensure_ascii=False, indent=1))
    print(f"{len(ss)} sentences → kept {len(kept)} ({t:.1f} s of {ws[-1]['e'] if ws else 0:.1f} s) → {out}")
    for s in kept: print(f"  {s['src_start']:7.2f}–{s['src_end']:7.2f}  {s['score']:+.1f}  {s['text'][:40]}  [{' · '.join(s['why'])}]")


if __name__ == "__main__":
    main()
