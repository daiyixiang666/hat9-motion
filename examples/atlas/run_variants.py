#!/usr/bin/env python3
"""Build every variant in variants.json in both aspects, run `hyperframes check`, and snapshot each beat.

  python3 examples/atlas/run_variants.py [name ...]

Variant json files are written next to this script as .variant_<name>.json (so relative asset paths work) and
built into build/variant_<name>_<aspect>/. Prints the error count per build; stills go to build/variant_*/snaps/.
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent
HF = ["npx", "--yes", "hyperframes@0.8.191"]


def main():
    data = json.loads((HERE / "variants.json").read_text())
    want = set(sys.argv[1:])
    for v in data["variants"]:
        if want and v["name"] not in want: continue
        vj = {"meta": {"title": v["name"], "style": "atlas", **v["meta"]}, "beats": [{"scene": "map", **b} for b in v["beats"]]}
        src = HERE / f".variant_{v['name']}.json"; src.write_text(json.dumps(vj, ensure_ascii=False, indent=1))
        for aspect in ("16:9", "9:16"):
            out = HERE / "build" / f"variant_{v['name']}_{aspect.replace(':', 'x')}"
            subprocess.run([sys.executable, str(SKILL / "scripts/build.py"), str(src), "--aspect", aspect, "--out", str(out)], check=True, capture_output=True)
            r = subprocess.run(HF + ["check", "--json"], cwd=out, capture_output=True, text=True)
            j = json.loads(r.stdout[r.stdout.find("{"):])
            errs = [(sec, f["code"], f.get("selector", "")[:60], f.get("time", "")) for sec, s in j.items() if isinstance(s, dict) for f in s.get("findings", []) if f["severity"] == "error"]
            times = []
            for b in v["beats"]:
                times.append(float(b["t"]))
            ends = times[1:] + [float(v["meta"]["duration"])]
            at = ",".join(f"{a + (e - a) * 0.75:.2f}" for a, e in zip(times, ends))
            subprocess.run(HF + ["snapshot", "-o", str(out / "snaps"), "--at", at, "--no-end"], cwd=out, capture_output=True)
            print(f"{v['name']:<16} {aspect:<5} errors={len(errs)}", *[f"\n    {e}" for e in errs[:8]])


if __name__ == "__main__":
    main()
