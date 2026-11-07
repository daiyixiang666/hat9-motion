"""Form-family lint: does the film keep changing the SHAPE of its information, or is it one centred phrase after
another?  Every effect / scene maps to a layout family in form_families.json (one table; new effects add a line).

  form-repeat   the same family on two neighbouring beats                                  (P1)
  slogan-share  share of beats that are full-frame slogans                                 (P1 above 25 %, P0 above 40 %)
  form-variety  fewer than 5 distinct families in a film longer than 60 s                  (P1)
  form-unknown  an effect or scene missing from the table (counted as its own family)      (warning)

A slogan effect laid out beside the presenter (beat presenter "card" / "side") counts as "beside", not "slogan".
Used by review.py --video and brief.py check.
"""
import json
from pathlib import Path

TABLE_PATH = Path(__file__).resolve().with_name("form_families.json")

SLOGAN_P1 = 0.25
SLOGAN_P0 = 0.40
MIN_FAMILIES = 5
VARIETY_MIN_SECONDS = 60.0


def load_table():
    return json.loads(TABLE_PATH.read_text(encoding="utf-8"))


def presenter_positions(video):
    """where the presenter sits on each beat (None without a presenter layer); a beat without a "presenter" key keeps
    the previous position."""
    meta = video.get("meta") or {}
    beats = video.get("beats") or []
    out = []
    if not meta.get("presenter"):
        for _ in beats:
            out.append(None)
        return out
    spec = meta["presenter"]
    current = "full"
    if isinstance(spec, dict) and spec.get("at"):
        current = spec["at"]
    for b in beats:
        p = b.get("presenter")
        if isinstance(p, str):
            current = p
        elif isinstance(p, dict) and p.get("at"):
            current = p["at"]
        out.append(current)
    return out


def family_of(beat, table, position=None):
    """(family, known): the layout family of one beat."""
    scene = beat.get("scene")
    if scene == "fx":
        name = beat.get("fx")
        fam = table["fx"].get(name)
        label = f"fx:{name}"
    else:
        name = scene
        fam = table["scenes"].get(name)
        label = f"scene:{name}"
    if fam is None:
        return label, False
    if fam == "slogan" and position in table.get("beside_when_presenter", []):
        fam = "beside"
    return fam, True


def film_seconds(video, timeline=None):
    if timeline and timeline.get("duration"):
        return float(timeline["duration"])
    meta = video.get("meta") or {}
    if meta.get("duration"):
        return float(meta["duration"])
    last = 0.0
    for b in video.get("beats") or []:
        t = b.get("t")
        if isinstance(t, (int, float)):
            end = float(t) + float(b.get("d") or 0)
            if end > last:
                last = end
    return last


def beat_where(i, times):
    if i < len(times) and times[i] is not None:
        return f"#{i} {times[i]:.1f}s"
    return f"#{i}"


def lint(video, timeline=None):
    """[(level, rule, message)] for one video.json (timeline = the build's timeline.json, for beat times)."""
    table = load_table()
    beats = video.get("beats") or []
    found = []
    if not beats:
        return found
    positions = presenter_positions(video)
    times = []
    if timeline and timeline.get("beats"):
        for x in timeline["beats"]:
            times.append(x.get("t"))
    families = []
    unknown = []
    for i, b in enumerate(beats):
        fam, known = family_of(b, table, positions[i])
        families.append(fam)
        if not known and fam not in unknown:
            unknown.append(fam)

    if unknown:
        found.append(("WARN", "form-unknown", "不在 form_families.json 里（各算一个家族，请补表）：" + "、".join(unknown)))

    run_start = 0
    for i in range(1, len(families) + 1):
        same = i < len(families) and families[i] == families[i - 1]
        if same:
            continue
        run_len = i - run_start
        if run_len >= 2:
            fam = families[run_start]
            found.append(("P1", "form-repeat", f"{beat_where(run_start, times)} 起连续 {run_len} 个 beat 都是「{fam}」版式：换一种载体（贴人 / 图表 / 界面 / 比喻）"))
        run_start = i

    n_slogan = 0
    for fam in families:
        if fam == "slogan":
            n_slogan += 1
    share = n_slogan / len(families)
    if share > SLOGAN_P0:
        found.append(("P0", "slogan-share", f"{n_slogan}/{len(families)} 个 beat（{share:.0%}）是全屏大字：最多 25%，其余换成贴人排版、数据、界面或比喻"))
    elif share > SLOGAN_P1:
        found.append(("P1", "slogan-share", f"{n_slogan}/{len(families)} 个 beat（{share:.0%}）是全屏大字（上限 25%）"))

    seconds = film_seconds(video, timeline)
    distinct = []
    for fam in families:
        if fam not in distinct:
            distinct.append(fam)
    if seconds > VARIETY_MIN_SECONDS and len(distinct) < MIN_FAMILIES:
        found.append(("P1", "form-variety", f"{seconds:.0f} 秒只用了 {len(distinct)} 种版式（{'、'.join(distinct)}）：至少 {MIN_FAMILIES} 种"))
    return found


def summary(video):
    """'slogan ×12 · ui ×3 …' for printing."""
    table = load_table()
    positions = presenter_positions(video)
    counts = {}
    order = []
    for i, b in enumerate(video.get("beats") or []):
        fam, _ = family_of(b, table, positions[i])
        if fam not in counts:
            counts[fam] = 0
            order.append(fam)
        counts[fam] += 1
    parts = []
    for fam in order:
        parts.append(f"{fam} ×{counts[fam]}")
    return " · ".join(parts)
