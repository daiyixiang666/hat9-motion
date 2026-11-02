#!/usr/bin/env python3
"""One demo reel per style for the gallery: every effect card is shown in the style that suits it.

  python3 scripts/style_reels.py            -> examples/styled-<style>/video.json for each style in STYLE_OF
  python3 scripts/render.py examples/styled-ink/video.json --styles ink [--aspect 9:16]   (renders reel as <style>_<aspect>.mp4)

The beats come from the effect demo reels (catalog.REELS), re-timed back to back with hard cuts; asset paths are
rewritten so they still resolve. Effects not listed stay in their original reel (the default `reel` look).
"""
import json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(HERE))

# card key (effect id, or "<id>-<band>" for a variant card) -> the style its gallery card is rendered in
STYLE_OF = {}
for sid, keys in {
    "press":    "table statement_table waterfall stacked_bars bars_csv formula odometer then_now deal_card review_card notice_card email_card "
                "media-3 media-5 media-12",
    "poster":   "stomp tracking lockup mask_up black_slam word_swap quadrant choose_one converge flip3d scale_compare slides",
    "zine":     "collage meme_stage gif_clip halftone logo_wall cite_post cite_article comment_thread danmaku scribble sponsor_card poll_card cartoon",
    "screen":   "code screencast scroll_shot spotlight cursor app_flow form_fill search_box notify glass ghost_type scramble pip media-video",
    "hud":      "hud_lock ranking countdown radar scatter glitch neon scanline relation_graph equity_tree bar_race news_flash",
    "doc":      "parallax portal match_cut callout footage freeze_frame speed_ramp cite_video earth_zoom map_route area_overlay "
                "map_timeline street_map timeline media-1",
    "papercut": "china_map china_map-dots burst gooey opener share_card next_teaser impact donut icon_unit",
    "sketch":   "steps decision_tree pros_cons list_stack term_card write_on handwrite gantt line_draw question_card",
    "ink":      "cite_quote vertical_title typewriter text_pages chapter_bar cite_paper cite_pdf cite_stack doc_flip doc_pick doc_photo "
                "apple_blur diffuse shine",
    "flat":     "chat im_chat triple lower3 dialogue interview podcast talking_head host_point audio_quote profile_card "
                "profile_card-group receipt funnel svg_art",
    "pixel":    "bars number_pages combo flying_words turntable text_mask clip_style media-2",
}.items():
    for k in keys.split():
        STYLE_OF[k] = sid

MEDIA_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".mp4", ".webm", ".mov", ".mp3", ".wav", ".pdf", ".json", ".csv", ".xlsx", ".txt", ".md", ".geojson", ".topojson", ".srt", ".vtt", ".html")


def card_key(b):
    band = b.get("preview")
    return f"{b['fx']}-{band}" if band else b["fx"]


def repath(v, src, dst):
    """relative asset paths in a beat (any depth) re-pointed from the source reel folder to the new one."""
    if isinstance(v, dict): return {k: repath(x, src, dst) for k, x in v.items()}
    if isinstance(v, list): return [repath(x, src, dst) for x in v]
    if isinstance(v, str) and not v.startswith(("http", "@", "/")) and v.lower().endswith(MEDIA_EXT) and (src / v).exists():
        return os.path.relpath(src / v, dst)
    return v


def retime(v, t0, d, t1):
    """`t_*` seconds that some effects take as absolute film time (receipt t_total, china_map t_hl / t_focus, danmaku
    t_hl) move with the beat; a number inside the beat's original span is absolute, anything else is an offset."""
    if isinstance(v, dict):
        return {k: (round(x - t0 + t1, 3) if k.startswith("t_") and isinstance(x, (int, float)) and t0 - 0.01 <= x <= t0 + d + 0.5 and t0 > d
                    else retime(x, t0, d, t1)) for k, x in v.items()}
    if isinstance(v, list): return [retime(x, t0, d, t1) for x in v]
    return v


def main():
    from catalog import REELS
    groups = {}
    seen = set()
    for ex in REELS:
        vj = ex / "video.json"
        if not vj.exists(): continue
        v = json.loads(vj.read_text())
        if v.get("meta", {}).get("words"): continue          # narration-timed reels (pacing) keep their own render
        for b in v["beats"]:
            if b.get("scene") != "fx" or b.get("fx") == "plate": continue
            k = card_key(b)
            sid = STYLE_OF.get(k)
            if not sid or k in seen: continue
            seen.add(k)
            groups.setdefault(sid, []).append((ex, b))
    host = "../mixue/assets/video/shiba.webm"
    for sid, items in groups.items():
        out = SKILL / "examples" / f"styled-{sid}"
        out.mkdir(parents=True, exist_ok=True)
        beats, t = [], 0.0
        for ex, b in items:
            d = float(b.get("d") or 3.0)
            nb = retime(repath({k: v for k, v in b.items() if k not in ("t", "tr")}, ex, out), float(b.get("t") or 0), d, t)
            nb["t"] = round(t, 3); nb["d"] = d; nb["tr"] = "hard"
            beats.append(nb); t += d
        video = {"meta": {"title": f"动效 · {sid} 风格", "aspect": "16:9", "style": sid, "duration": round(t, 3), "host_video": host},
                 "beats": beats}
        (out / "video.json").write_text(json.dumps(video, ensure_ascii=False, indent=1) + "\n")
        print(f"{sid:9s} {len(beats):2d} effects  {t:5.1f} s  -> {out.relative_to(SKILL)}/video.json")
    missing = sorted(set(STYLE_OF) - seen)
    if missing: print("not found in any demo reel:", " ".join(missing))


if __name__ == "__main__":
    main()
