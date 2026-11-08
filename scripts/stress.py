#!/usr/bin/env python3
"""Stress test: every effect and scene with deliberately awkward inputs, in 16:9 and 9:16.

  python3 scripts/stress.py                      # everything (effects + press + poster scenes)
  python3 scripts/stress.py --only pop,notify    # some targets (effect ids, or press:split, poster:quote)
  python3 scripts/stress.py --jobs 3 --no-snap   # parallel builds; skip contact sheets
  python3 scripts/stress.py --plugins            # also the plugin effects, using examples/aefx/variants.json

Inputs per target: tiny / typical / extreme text, 1·3·6·12 pictures mixing landscape, portrait, square and
panorama, short and long lists, and a moving clip where the effect takes video (`media`: 0 to 500 items). Each target becomes one
composition (one beat per variant) under examples/stress/build/, checked with `hyperframes check --json` at each
beat's settled moment. It fails on any error and on text that overflows its box, the canvas or its container,
or overlaps other text — except findings allow-listed below as intentional. Contact sheets (one labelled frame
per variant) land in examples/stress/sheets/. A summary is written to examples/stress/report.md.

Safe area (9:16): visible text must stay out of the platform chrome — top 200 px, bottom 400 px, right 120 px of the
lower half (scripts/h9/safearea.cjs, run with the Chrome + puppeteer-core that HyperFrames already installed). Exempt:
data-safe="ignore", a style's STYLE["safe_exempt"], SAFE_EXEMPT below (page furniture), SAFE_ALLOW per target. --no-safe skips it.
Duration (--durations, on with --plugins): a subset of effects at 0.8 s and 6 s beats (targets "pop@0.8", "pop@6").
Work packages add targets in examples/stress/targets/<pkg>.json, any of three shapes:
  {"base", "beats": [{fx, ...}]}  ·  {"base", "targets": {fx: [variant]}, "durations": [1, 3, 8], "meta": {}, "allow": [[fx, code, rx]]}
  ·  {fx: [variant]}.

Test pictures: examples/aefx/assets/broll/*.jpg when present (Mixkit stills, never committed) plus placeholders
drawn here in every aspect. Test video: clips under $H9_MEDIA/broll (your own media library), referenced by path; skipped when unset.
"""
import os, argparse, json, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
OUT = SKILL / "examples" / "stress"
BUILD, SHEETS, IMG = OUT / "build", OUT / "sheets", OUT / "build" / "img"
# file params in target beats are made absolute against the target's base when the file exists there
MEDIA_RX = re.compile(r"\.(jpe?g|png|webp|gif|avif|svg|pdf|mp4|mov|webm|m4v|mp3|wav|m4a|aac|ogg|flac|json|csv|xlsx?|txt|md|srt|vtt|html?)$", re.I)
HF = ["npx", "--yes", "hyperframes@0.8.191"]
FAIL = {"text_box_overflow", "canvas_overflow", "container_overflow", "content_overlap", "text_occluded"}
SAFE_EXEMPT = [".pr-hd", ".pr-ft", ".ctx .ft", ".fx-tag", ".hud-read", ".po .hd", ".po .ft", ".po .tick"]   # page furniture (show name, source line, grid ticks) may sit under chrome
SAFE_ALLOW = [("timeline", "right", r"\.tly"), ("danmaku", "right", r"wpd-i")]   # (target prefix, zone, selector regex): the timeline's neighbouring years slide off on purpose
# known issues left for each effect's owner: reported in the report, not counted as failures (target prefix, regex on the finding, note)
KNOWN = [
    ("profile_card", r"text_box_overflow div\.wpp\.grid", "WP4 profile_card: in the 6-person grid (9:16) the one-line bios overflow their cells"),
    ("im_chat", r"(text_box|canvas)_overflow", "WP4 im_chat: avatar monogram / long-thread bubble boxes (info level)"),
    ("china_map", r"safe right", "WP4 china_map: ranking labels at the right edge cross the 9:16 button zone"),
    ("map_route", r"safe right", "E map_route: an end-point label near the right edge crosses the 9:16 button zone"),
    ("media", r"canvas_overflow .*> b:nth-of-type", "G media: the flood counter's box grazes the canvas for its first frames"),
    ("cite_post", r"text_box_overflow", "H cite_post: serif zh line box taller than its box (info level, ink is inside)"),
    ("cite_article", r"canvas_overflow", "H cite_article: a long URL line box (ellipsised) reaches the canvas edge"),
    ("cite_video", r"safe right", "H cite_video: the caption under a portrait clip spans the full width in 9:16"),
    ("scale_compare", r"safe right", "WP2 scale_compare: the full-width title line crosses the 9:16 button zone"),
    ("stacked_bars", r"safe right", "WP2 stacked_bars: the last bar's value label sits in the 9:16 button zone"),
    ("bar_race", r"text_box_overflow", "WP2 bar_race: value labels overflow their span box while counting (info level)"),
    ("ranking", r"safe right", "WP1 ranking: the unit after a long value reaches the 9:16 button zone"),
    ("interlude", r"safe right .*div\.src", "WP5 interlude: the source credit is right-aligned into the 9:16 button zone"),
    ("cold_open", r"(safe right .*span\.fl|text_box_overflow|canvas_overflow)", "WP5 cold_open: a long 2-line title slams full-width (and past the canvas at 3 s)"),
    ("chapter_breather", r"(safe right|text_box_overflow)", "WP5 chapter_breather: a long next-chapter title runs full width"),
]
DUR_FX = ["pop", "mask_up", "apple_blur", "stomp", "odometer", "impact", "tracking", "burst", "bars", "donut", "list_stack", "table", "media"]
DUR_SET = (0.8, 6.0)
# extra aspects (laid out as 9:16 behind a window, see core.CANVAS): a representative subset, on with --plugins
EXTRA_ASPECTS = ("1:1", "3:4")
ASPECT_SUBSET = ["press:hook", "press:split", "press:chain", "press:wheel", "mask_up", "stomp", "notify", "media", "table", "cite_quote", "list_stack"]
# platform watermarks (approximate boxes where each app stamps its logo / account id), checked on the already-built
# 9:16 / 16:9 pages of a subset: readable text must not sit under them. Furniture is exempt (SAFE_EXEMPT + WM_EXEMPT:
# the show-name row, the effect tag, the thesis page's giant quote mark). Douyin's download stamp also visits the top
# left, which is the page header's place by design, so only its bottom-right box is checked. Saved Douyin videos carry
# a moving logo + account id at the bottom right; the box is an estimate that starts under the 9:16 caption band (~1500).
WM = {
    "douyin":      ("9:16", [{"n": "wm-douyin-br", "x0": 640, "y0": 1500, "x1": 1050, "y1": 1640, "tx": 6, "ty": 10}]),
    "xiaohongshu": ("9:16", [{"n": "wm-xhs-br", "x0": 690, "y0": 1690, "x1": 1060, "y1": 1870, "tx": 6, "ty": 10}]),
    "bilibili":    ("16:9", [{"n": "wm-bili-tr", "x0": 1500, "y0": 26, "x1": 1894, "y1": 110, "tx": 6, "ty": 8}]),
}
WM_EXEMPT = [".ctx .hd", ".pr-thesis .qm"]
WM_SUBSET = ["press:hook", "press:stores", "press:thesis", "mask_up", "apple_blur", "lower3", "odometer", "cite_quote", "list_stack", "table"]
TMETA = {}               # target -> extra meta for its composition (e.g. bpm for beat-cut effects)
# (target prefix, code, selector regex) that are intentional
ALLOW = [
    ("*", "container_overflow", r"\.ln|> span"),           # line-mask reveals: the line box is the mask
    ("*", "content_overlap", r"\.ctx|cap|\.fx-tag"),      # the caption pill may sit over full-bleed pictures
    ("press:split", "canvas_overflow", r"zm|\.flag|\.pct|\.pl|\.tot|\.chip|\.to|\.hl|\.kick"),   # the dive scales the page ×70
    ("press:split", "container_overflow", r"zm|\.tot"),
    ("press:split", "content_overlap", r"zm|\.tot|\.flag|\.pl"),
    ("press:split", "text_box_overflow", r"zm|\.tot"),
    ("poster:", "container_overflow", r"^#s\d+ > div:nth-of-type\(1\) > div:nth-of-type\(1\) > div:nth-of-type\(1\)$"),   # the page camera's 2.5% creep
    ("poster:price", "container_overflow", r"div:nth-of-type\(4\)$"),   # the ↓ / ↑ glyph box (Archivo has no arrow; the fallback's box is wide)
    ("poster:thesis", "canvas_overflow", r"span:nth-of-type\(1\) > span:nth-of-type\(1\)$"),   # a 600 px word's inline box (not its ink) grazes the top edge
    ("timeline", "canvas_overflow", r"."), ("timeline", "text_box_overflow", r"."),   # a scroller: the neighbouring years slide off-frame by design
    ("ghost_type", "canvas_overflow", r"\.gh"),
    ("parallax", "content_overlap", r"\.pxt"),            # the title sits between the plate and the cut-out on purpose
    ("countdown", "canvas_overflow", r"."), ("countdown", "content_overlap", r"cd-dg"),        # off-stage digits of the flip (WP1)
    ("term_card", "text_box_overflow", r"."), ("term_card", "canvas_overflow", r"."),         # the decorative ghost glyph (WP1)
    ("word_swap", "container_overflow", r"."), ("word_swap", "text_box_overflow", r"."), ("word_swap", "canvas_overflow", r"."),   # the reel clipped by its slot (WP1)
    ("danmaku", "canvas_overflow", r"."), ("danmaku", "text_box_overflow", r"."),            # bullet comments fly in and out of frame (WP4)
    ("comment_thread", "canvas_overflow", r"."), ("receipt", "canvas_overflow", r"."),       # a long thread scrolls / a long receipt prints past the frame (WP4)
    ("glitch", "content_overlap", r"\.r|\.cy|\.m"),
    ("slice_text", "content_overlap", r"\.a|\.b"),
]


# ---------------------------------------------------------------- inputs
T_TINY, T_SHORT = "钱", "看懂谁在*赚钱*"
T_LONG = "一杯 4 块钱的柠檬水，一年净赚 *44 亿*，比麦当劳还多。"
T_XL = "AI 时代，工具人人都有，真正拉开差距的不是你会不会用，而是你知道哪一张*不能要*。"
T_LATIN = "Focusing is about saying *no* — and meaning it."
T_BREAK = "差别不在工具|在判断"
TEXTS = [T_TINY, T_SHORT, T_LONG, T_XL, T_LATIN, T_BREAK]
LINES = ["钱。", "一杯 4 块钱的柠檬水，一年净赚 *44 亿*。",
         "这句台词故意写得很长很长，用来测试字幕在两行之内能不能放下，以及放不下的时候会不会自动缩小字号，*而不是溢出画面*。"]


def pictures():
    """test stills: real B-roll when available, plus drawn placeholders in every aspect."""
    IMG.mkdir(parents=True, exist_ok=True)
    from PIL import Image, ImageDraw
    shapes = {"portrait34": (900, 1200), "tall916": (720, 1280), "square": (1000, 1000), "pano41": (2400, 600), "tall13": (500, 1500)}
    out = {}
    for k, (w, h) in shapes.items():
        p = IMG / f"{k}.png"
        if not p.exists():
            im = Image.new("RGB", (w, h)); dr = ImageDraw.Draw(im)
            for y in range(h):
                a = y / h
                dr.line([(0, y), (w, y)], fill=(int(40 + 150 * a), int(70 + 60 * (1 - a)), int(120 + 90 * a)))
            for i in range(0, w + h, 80):
                dr.line([(i, 0), (i - h, h)], fill=(255, 255, 255), width=3)
            dr.rectangle([w * 0.1, h * 0.1, w * 0.9, h * 0.9], outline=(255, 230, 120), width=10)
            dr.ellipse([w * 0.4, h * 0.4, w * 0.6, h * 0.6], fill=(240, 80, 50))
            im.save(p)
        out[k] = str(p)
    broll = SKILL / "examples" / "aefx" / "assets" / "broll"
    land = sorted(str(p) for p in broll.glob("*.jpg") if "_plate" not in p.name) if broll.exists() else []
    out["land"] = land or [str(IMG / "square.png")]
    out["fg"] = str(broll / "silhou_fg.png") if (broll / "silhou_fg.png").exists() else None
    out["plate"] = str(broll / "silhou_plate.jpg") if (broll / "silhou_plate.jpg").exists() else out["land"][0]
    vids = sorted((Path(os.environ["H9_MEDIA"]) / "broll").glob("*/*.mp4")) if os.environ.get("H9_MEDIA") else []
    pick = [v for v in vids if "traffic-light" in v.name or "tokyo" in v.name] or vids
    out["video"] = str(pick[0]) if pick else None
    own = [SKILL / "assets" / "previews" / f for f in ("mixue_16x9.mp4", "atlas_16x9.mp4", "screen_9x16.mp4")]
    out["clips"] = [str(v) for v in own if v.exists()]
    out["video"] = out["video"] or (out["clips"][0] if out["clips"] else None)
    fr = SKILL / "examples" / "media" / "assets" / "frames"          # python3 examples/media/make_frames.py
    out["pool"] = sorted(str(p) for p in fr.glob("*.jpg")) if fr.exists() else []
    return out


def fx_variants(P):
    L, por, tall, sq, pano = P["land"], P["portrait34"], P["tall916"], P["square"], P["pano41"]
    mixed = [L[0], por, sq, L[1 % len(L)], tall, pano]
    vid = P["video"]
    tx = lambda **k: [{"text": x, **k} for x in TEXTS]
    V = {k: tx() for k in ("pop", "tracking", "blur_focus", "typewriter", "scramble", "write_on", "flip3d", "slice_text", "shine",
                          "glitch", "apple_blur", "neon", "impact", "burst", "diffuse")}
    V["mask_up"] = tx(sub="a long latin subline that should wrap instead of running off the page")
    V["ghost_type"] = [{"ghost": "钱", "text": T_SHORT}, {"ghost": "供应链生意", "text": T_LONG, "sub": "same model · same prompt"}, {"ghost": "JUDGMENT", "text": T_XL}]
    V["lockup"] = [{"text": T_SHORT, "notes": []}, {"text": "判断力", "sub": "JUDGMENT", "notes": ["思源黑体 Heavy"]},
                   {"text": T_LONG, "notes": ["一", "二", "三", "四个注释"]}, {"text": T_TINY, "notes": ["字体 · 思源宋体", "Latin · EB Garamond"]}]
    V["odometer"] = [{"value": 7}, {"value": 46479, "unit": "家", "sub": "蜜雪冰城全球门店"}, {"value": -3.5, "unit": "%"},
                     {"value": 1284903221, "unit": "次"}, {"value": "97.5", "unit": "%"}, {"value": 4450000000, "zh": True, "unit": "元"}]
    V["stomp"] = [{"words": ["钱", "赚"]}, {"words": ["一杯", "4 块钱", "柠檬水", "一年净赚", "44 亿"]},
                  {"words": [str(i) for i in "一二三四五六七八九十百千"]}, {"words": ["一年净赚四十四亿多", "比麦当劳还多的门店数量", "AI"]},
                  {"text": "大家都在用 AI 差别到底在哪里"}]
    V["notify"] = [{"items": ["抖音：你的视频播放量破 10 万"]}, {},
                   {"items": [["抖音", "你的视频播放量破 10 万，还在继续上涨，评论区已经吵起来了"], ["小红书", "有 326 人收藏了你的笔记"], "B站：新增 128 个粉丝",
                              {"app": "微信", "text": "有人转发了你的文章"}, ["视频号", "推荐量 +200%"], ["知乎", "你的回答进入热榜"]]}]
    V["triple"] = [{"labels": ["关注"]}, {}, {"labels": ["点赞", "投币", "收藏", "转发", "评论"]}, {"labels": ["一键三连支持一下", "收藏"]}]
    V["callout"] = [{"image": L[0], "x": 30, "y": 55, "text": "一道硬光", "sub": "KEY LIGHT"},
                    {"image": por, "points": [{"x": 20, "y": 60, "text": "左边", "sub": "A"}, {"x": 78, "y": 50, "text": "右边的标签往左", "sub": "B"},
                                              {"x": 50, "y": 18, "text": "靠上往下", "sub": "C"}]},
                    {"image": L[0], "x": 40, "y": 60, "text": "增长不等于利润，这个标签很长很长", "sub": "GROWTH IS NOT PROFIT"}]
    if vid: V["callout"].append({"video": vid, "x": 45, "y": 50, "text": "视频上的标注", "sub": "VIDEO"})
    V["plate"] = [{"image": L[0], "text": "转场"}, {"image": por, "text": T_LONG}, {"image": pano}, {"image": P["tall13"], "text": T_TINY}]
    if vid: V["plate"].append({"video": vid, "text": "视频图版"})
    V["parallax"] = [{"plate": P["plate"], "fg": P["fg"], "text": "成交"} if P["fg"] else {"image": L[0], "text": "成交"},
                     {"image": por, "text": T_LONG}, {"image": sq, "text": T_TINY}]
    if vid: V["parallax"].append({"video": vid, "text": "流动的背景"})
    V["mosaic"] = [{"images": [L[0]]}, {"images": mixed[:4]}, {"images": (L * 3)[:12]}, {"images": (mixed * 4)[:20]}]
    V["collage"] = [{"images": [L[0]], "text": "就这张"}, {"images": [L[0], por], "text": "对比"}, {"images": L[:3], "text": "这张才对"},
                    {"images": mixed[:5], "text": "五张不同比例的图"}, {"images": (mixed * 2)[:9], "text": T_LONG}]
    V["match_cut"] = [{"text": "生意", "images": []}, {"text": "判断", "images": L[:2]}, {"text": T_LONG, "images": mixed}, {"text": T_TINY, "images": [por]}]
    V["portal"] = [{"image": L[0], "image2": L[1 % len(L)], "x": 40, "y": 50}, {"image": por, "image2": sq, "x": 60, "y": 35}]
    if vid: V["portal"].append({"video": vid, "image2": L[0], "x": 50, "y": 50})
    V["lower3"] = [{"text": "频道"}, {"text": "示例频道", "sub": "商业拆解 · 每期拆一家公司怎么赚钱"},
                   {"text": "一个特别特别长的账号名字用来测试下三分之一", "sub": "A VERY LONG ROLE LINE THAT HAS TO WRAP ONTO A SECOND LINE GRACEFULLY"}]
    V["cartoon"] = [{"text": "啪"}, {"text": "翻车了！"}, {"text": "这个拟声词特别特别长"}]
    V["gooey"] = [{}, {"labels": ["流量", "供应链"]}, {"labels": ["很长很长的左边标签", "右"]}]
    V["dual"] = [{"img_h": L[0], "img_v": tall, "text": "横竖双屏"}, {"image": por, "text": T_LONG}]
    clips = P.get("clips") or []
    if clips:     # clips mixed into the picture sets
        V["mosaic"].append({"images": [clips[0], L[0], por, clips[-1], sq, L[1 % len(L)]]})
        V["collage"].append({"images": [clips[0], por, L[0]], "text": "视频也能贴"})
        V["match_cut"].append({"text": "生意", "images": [L[0], clips[0], por, clips[-1]]})
    # media: the count picks the choreography — 1 · 2 · 3 · 5 · 8 · 24 · 60 · 200 · 500, mixed shapes, clips
    pool = P.get("pool") or []
    base = pool or (L + [por, tall, sq, pano])
    many = lambda k: [base[i % len(base)] for i in range(k)]
    cap = lambda xs, cs: [{"src": x, "caption": c} for x, c in zip(xs, cs)]
    V["media"] = [{"items": cap([L[0]], [T_LONG])}, {"items": [por]}, {"items": cap([L[0], tall], ["横屏 16:9", "竖屏 9:16"]), "hl": 1},
                  {"items": cap([L[0], por, pano], ["AI 工具台", "一个特别特别长的卡片标签用来测试截断", "全景"]), "hl": 0},
                  {"items": cap(many(5), ["财经刊", "AI 工具台", "地图纪录", "瑞士海报", "竖屏版"]), "hl": 2},
                  {"items": [por, pano, sq, tall, L[0], L[1 % len(L)], P["tall13"], sq]},
                  {"items": many(24), "hl": 5}, {"items": many(60), "hl": 11}, {"items": many(200), "count_label": "帧", "sub": "四条成片"},
                  {"items": many(500), "hl": 77}, {"items": []}]
    if clips:
        V["media"] += [{"items": [{"video": clips[0], "caption": "视频"}]}, {"items": [clips[0], clips[-1]]},
                       {"items": cap([clips[0], L[0], clips[1 % len(clips)], por], ["视频", "图", "视频", "竖图"]), "hl": 0},
                       {"items": [clips[i % len(clips)] if i % 4 == 0 else base[i % len(base)] for i in range(12)]},
                       {"items": [clips[0]] + many(39), "hl": 0}]
    for k, vs in V.items():
        for i, v in enumerate(vs):
            v.setdefault("line", LINES[i % len(LINES)])
            v.setdefault("theme", ["paper", "ink", "lemon", "red"][i % 4])
            v.setdefault("topic", "压力测试")
    return V


PRESS = {
    "hook": [{"price": "¥4", "value": 44.5, "item": "冰鲜柠檬水", "kicker": "2024 年 · 净利润", "sub": "净利润同比 *+39.8%*"},
             {"price": "¥19.9", "value": 1284903221, "unit": "次", "unit2": "", "item": "一个特别长的商品名字，看它会不会换行", "kicker": "播放量", "sub": "这一行副标题也故意写得很长很长，测试两行以内的自适应"},
             {"price": "$5.5", "value": 3, "unit": "%", "unit2": "", "item": "咖啡"}],
    "stores": [{"kicker": "门店数", "title": "比麦当劳还多", "a": {"name": "蜜雪冰城", "n": 46479}, "b": {"name": "麦当劳", "n": 43477}},
               {"kicker": "差距悬殊", "title": "一个标题很长很长的对比页，看它会不会两行", "a": {"name": "一家很小的店", "n": 12}, "b": {"name": "一个名字很长的连锁品牌", "n": 3000}},
               {"kicker": "B 更大", "title": "后者更多", "a": {"name": "A", "n": 850}, "b": {"name": "B", "n": 920}, "unit": "个"},
               {"kicker": "百万级", "title": "百万级的对比", "a": {"name": "甲", "n": 1200000}, "b": {"name": "乙", "n": 980000}}],
    "turn": [{"q": "但它真正的生意", "pre": "不是", "struck": "卖奶茶"},
             {"q": "这一句引导语写得特别长，看它会不会换行而不压到下面的大字", "pre": "不是靠", "struck": "卖更多的奶茶赚钱"}],
    "split": [{"kicker": "收入构成", "title": "248.3 亿元，从哪来", "pct": 97.5, "pl_pre": "卖给加盟店的", "pl": "商品和设备", "pl_sub": "242.1 亿元",
               "total": "全年收入 248.3 亿元", "items": [["lemon", "原料"], ["pack", "包材"], ["machine", "设备"]], "to": "→ 卖给加盟店", "small": {"q": "加盟费呢？", "label": "加盟和相关服务", "tag": "6.2 亿元"}},
              {"kicker": "一半一半", "title": "60%", "pct": 60, "pl": "主营业务", "items": [["box", "只有一个标签"]], "total": "总收入", "small": {"q": "剩下的？", "label": "其他", "tag": "40%"}},
              {"kicker": "小头", "title": "一个很长很长的标题，测试两行", "pct": 12.5, "pl_pre": "占比很小的", "pl": "一个名字特别特别长的业务板块",
               "total": "全年收入", "items": [["lemon", "原料采购"], ["pack", "包装材料"], ["machine", "门店设备"], ["truck", "冷链物流"], ["store", "加盟服务"]],
               "small": {"q": "其余部分呢？", "label": "其余的大头业务收入，名字也很长", "tag": "87.5%"}},
              {"kicker": "极端", "title": "99.9%", "pct": 99.9, "pl": "几乎全部", "items": [["box", "全部"]], "small": {"q": "余下", "label": "零头", "tag": "0.1%"}}],
    "chain": [{"kicker": "三节点", "title": "最短的链", "nodes": [{"name": "工厂", "icon": "factory"}, {"name": "门店", "icon": "store"}, {"name": "你", "icon": "person"}],
               "hot": 1, "bracket": "供应链"},
              {"kicker": "七节点", "title": "一条很长的链||每个节点名字都很长", "nodes": [{"name": "种植基地", "sub": "柠檬 · 茶", "icon": "lemon"}, {"name": "初加工厂", "sub": "原料", "icon": "factory"},
               {"name": "中央工厂", "sub": "包材", "icon": "factory"}, {"name": "区域仓", "sub": "仓储", "icon": "truck"}, {"name": "冷链配送车队", "sub": "直送", "icon": "truck"},
               {"name": "四万多家加盟店", "sub": "46,479 家", "icon": "store"}, {"name": "你", "sub": "¥4 / 杯", "icon": "person"}], "hot": 5, "bracket": "一整条供应链", "bracket_sub": "= 收入"}],
    "wheel": [{"kicker": "三站", "q": "所以", "big": "不怕*便宜*", "stations": ["价格低", "卖得多", "成本降"], "sum": "三站飞轮"},
              {"kicker": "六站", "q": "所以它", "big": "越转*越快*的飞轮", "stations": ["价格更低", "卖得更多", "原料走量", "采购更便宜", "效率更高", "利润再投入降价"],
               "sum": "价格越低 → 卖得越多 → 原料走得越多 → 采购越便宜 → 效率更高 → 利润再投入降价 → 价格还能更低", "center": "增长飞轮"}],
    "thesis": [{"kicker": "判断", "l1": "看懂谁在赚钱", "em": "赚钱", "l2": "比看懂谁在卖货更重要", "struck": "卖货"},
               {"kicker": "长句", "l1": "真正决定一门生意能不能赚钱的，是谁在为它买单", "em": "买单", "l2": "比起热闹的卖货，更该看懂背后那条看不见的供应链", "struck": "卖货"},
               {"kicker": "短", "l1": "钱", "em": "钱", "l2": "就这样"}],
    "outro": [{"title": "示例频道", "sub": "商业拆解", "cta": "关注"},
              {"title": "一个非常非常长的账号名字", "sub": "这一行定位语也写得很长很长，测试会不会超出画面", "cta": "关注我，下期拆一家你天天在用的公司"}],
}
POSTER = {
    "hundred": [{"pre": "人人一口气生成", "big": "一百个|答案", "count": 100}, {"pre": "一句很长很长的引子，看它会不会换行", "big": "一千个可能的答案", "count": 1000, "en": "a much longer english line that should wrap within its column instead of running away"},
                {"pre": "少", "big": "十二", "count": 12}],
    "problem": [{"big": "问题", "q": "从来不是", "claim": "答案|不够多", "strike": "不够多"},
                {"big": "问题在哪里", "q": "真正的问题从来都不是", "claim": "我们手里可用的答案还不够多", "strike": "不够多"}],
    "quote": [{"year": "1997", "q1": "专注，", "q2": "就是学会", "q3": "说不。", "en": "“Focusing is about saying no.” — Steve Jobs"},
              {"year": "1997年5月", "who": "一位说话很长的嘉宾 · 某个很长的大会名字", "q1": "一句很长的引语前半段，", "q2": "后半段也写得很长很长", "q3": "最后的结论也不短。",
               "en": "“A much longer quotation in English that keeps going for several lines so the shrink-to-the-footnote move has to cope with it.”"}],
    "price": [{"left": ["生成", "变便宜"], "right": ["判断", "变贵"]}, {"left": ["内容生产", "越来越便宜了"], "right": ["审美判断力", "越来越值钱了"]}],
    "keep": [{"frames": 24}, {"frames": 6, "a": ["做出", "几张", "不重要"], "b": ["扔掉", "几张", "才重要"]},
             {"frames": 36, "a": ["你一天能做出", "多少张图", "根本不重要"], "b": ["你敢扔掉", "多少张图", "才真正重要"]}],
    "thesis": [{"big": "选择", "rest": "才是|新的创作"}, {"big": "学会选择", "rest": "才是这个时代新的创作方式", "mo": "THESIS — A MUCH LONGER MONO LINE"}],
    "outro": [{"title": "示例频道", "sub": "一句定位"}, {"title": "一个非常非常长的账号名字", "sub": "这一行定位语也写得很长很长很长很长"}],
}
SETTLE = {"notify": 0.9, "mask_up": 0.6, "mosaic": 0.5, "portal": 0.9, "typewriter": 0.85, "scramble": 0.85, "write_on": 0.85, "stomp": 0.95, "media": 0.93}
BEAT = {"media": 4.6}      # per-variant beat length for effects that need longer than the default 2.6 s


# ---------------------------------------------------------------- build / check
def compose(target, variants, d):
    """one video.json for a target: one beat per variant."""
    kind, _, name = target.split("@")[0].rpartition(":")
    beats, t = [], 0.0
    for v in variants:
        if kind == "":
            b = {"scene": "fx", "fx": name, **v}
        else:
            b = {"scene": name, **v}
        b["t"] = round(t, 2); b["d"] = d
        if beats: b["tr"] = "hard"
        beats.append(b); t += d
    style = "reel" if kind == "" else kind
    meta = {"title": f"stress · {target}", "duration": round(t, 2), "style": style, "section": "压力测试", "case": "stress", "src": "压力测试数据", **TMETA.get(target, {})}
    return {"meta": meta, "beats": beats}, style


def settle_times(target, n, d):
    name = target.split("@")[0].rpartition(":")[2]
    f = SETTLE.get(name, 0.62 if ":" not in target else 0.93)
    if "@" in target: f = 0.92 if d < 1.5 else max(f * 2.6 / d, 0.5) if d > 3 else f    # short beats: the end; long: soon after landing
    return [round(i * d + d * f, 2) for i in range(n)]


def allowed(target, f):
    for pre, code, rx in ALLOW:
        if (pre == "*" or target.startswith(pre)) and f["code"] == code and re.search(rx, f.get("selector", "") or ""):
            return True
    return False


def run_target(target, variants, aspect, snap=True, safe=True):
    d = 4.4 if ":" in target else BEAT.get(target, 2.6)
    if target.startswith("press:split"): d = 6.0
    if "@" in target: d = float(target.rsplit("@", 1)[1])
    vj, style = compose(target, variants, d)
    tag = aspect.replace(":", "x")
    work = BUILD / f"{target.replace(':', '_')}_{tag}"
    work.mkdir(parents=True, exist_ok=True)
    (work.parent / f"{work.name}.json").write_text(json.dumps(vj, ensure_ascii=False, indent=1))
    r = subprocess.run([sys.executable, "-W", "ignore", str(HERE / "build.py"), str(work.parent / f"{work.name}.json"), "--style", style, "--aspect", aspect, "--out", str(work)],
                       capture_output=True, text=True)
    if r.returncode:
        return {"target": target, "aspect": aspect, "ok": False, "fails": [f"build failed: {(r.stderr or r.stdout)[-400:]}"]}
    at = settle_times(target, len(variants), d)
    c = subprocess.run(HF + ["check", "--json", "--max-issues", "500", "--at", ",".join(map(str, at))], cwd=work, capture_output=True, text=True)
    s = c.stdout
    try: j = json.loads(s[s.find("{"):])
    except Exception: return {"target": target, "aspect": aspect, "ok": False, "fails": ["check output unreadable: " + (c.stderr or s)[-300:]]}
    fails, seen = [], set()
    for sec, v in j.items():
        if not isinstance(v, dict): continue
        for f in v.get("findings", []):
            if f["code"] in ("nested_structure_needs_subcomposition", "timeline_track_too_dense", "composition_file_too_large"): continue
            bad = f["severity"] == "error" or (f["code"] in FAIL and not (f["code"] == "text_occluded" and f["severity"] != "error"))   # an opted-out occlusion drops to info
            if f["code"] == "container_overflow" and not (f.get("text") or "text" in f.get("message", "").lower()): bad = f["severity"] == "error"   # graphics may bleed
            if not bad or allowed(target, f): continue
            tt = f.get("time"); vi = int(float(tt) // d) if tt not in (None, "") else -1
            if tt not in (None, "") and min(abs(float(tt) - x) for x in at) > 0.06: continue   # mid-animation: not a layout state
            key = (f["code"], vi, (f.get("selector") or "")[-60:])
            if key in seen: continue
            seen.add(key)
            fails.append(f"v{vi} {f['severity']} {f['code']} {(f.get('selector') or '')[-80:]} @{tt}: {f['message'][:90]}")
    if safe and aspect == "9:16":
        fails += safe_area(target, style, work, at, d)
    known = [f for f in fails if any(target.startswith(p) and re.search(rx, f) for p, rx, _ in KNOWN)]
    fails = [f for f in fails if f not in known]
    if snap:
        sdir = work / "snap"
        subprocess.run(HF + ["snapshot", "-o", str(sdir), "--at", ",".join(map(str, at)), "--no-end"], cwd=work, capture_output=True, text=True)
        sheet(sorted(sdir.glob("frame-*.png")), SHEETS / f"{target.replace(':', '_')}_{tag}.jpg", target, aspect, fails)
    return {"target": target, "aspect": aspect, "ok": not fails, "fails": fails, "known": known, "n": len(variants)}

_TOOLS = {}


def safe_tools():
    """(puppeteer-core path, chrome path) from the HyperFrames install, or None (then the safe-area rule is skipped)."""
    if "v" in _TOOLS: return _TOOLS["v"]
    v = None
    try:
        pp = os.environ.get("H9_PUPPETEER")
        if not pp:
            r = subprocess.run(["npm", "exec", "--yes", "--package=hyperframes@0.8.191", "--", "node", "-e",
                                "console.log(process.env.PATH.split(require('path').delimiter).find(x=>x.includes('_npx'))||'')"],
                               capture_output=True, text=True, cwd=str(SKILL), timeout=120)
            b = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            pp = str(Path(b).parent / "puppeteer-core") if b else ""
        ch = os.environ.get("H9_CHROME") or subprocess.run(HF + ["browser", "path"], capture_output=True, text=True, timeout=120).stdout.strip().splitlines()[-1]
        if pp and Path(pp).exists() and ch and Path(ch).exists(): v = (pp, ch)
    except Exception:
        v = None
    _TOOLS["v"] = v
    return v


def safe_area(target, style, work, at, d, zones=None, W=1080, H=1920, extra_ex=()):
    tools = safe_tools()
    if not tools: return []
    try:
        sys.path.insert(0, str(HERE))
        import build as _b
        ex = list(SAFE_EXEMPT) + list(_b.load_style(style).get("safe_exempt", [])) + list(extra_ex)
    except Exception:
        ex = list(SAFE_EXEMPT) + list(extra_ex)
    env = dict(os.environ, H9_PUPPETEER=tools[0], H9_CHROME=tools[1])
    args = ["node", str(HERE / "h9" / "safearea.cjs"), str(work / "index.html"), ",".join(map(str, at)), str(W), str(H), "||".join(ex)]
    if zones: args.append(json.dumps(zones))
    r = subprocess.run(args, capture_output=True, text=True, env=env, timeout=300)
    if r.returncode: return [f"safe-area probe failed: {(r.stderr or r.stdout)[-200:]}"]
    out, seen = [], set()
    for v in json.loads(r.stdout or "[]"):
        if any(target.startswith(p) and v["zone"] == z and re.search(rx, v["sel"]) for p, z, rx in SAFE_ALLOW): continue
        vi = int(float(v["t"]) // d)
        key = (vi, v["zone"], v["sel"][-50:])
        if key in seen: continue
        seen.add(key)
        out.append(f"v{vi} safe {v['zone']} {v['sel'][-70:]} @{v['t']}: 「{v['text']}」 at {v['rect']}")
    return out


def sheet(frames, dst, target, aspect, fails):
    if not frames: return
    from PIL import Image, ImageDraw
    dst.parent.mkdir(parents=True, exist_ok=True)
    w = 480 if aspect == "16:9" else 220
    ims = [Image.open(f).convert("RGB") for f in frames]
    h = round(ims[0].height * w / ims[0].width)
    cols = min(len(ims), 4 if aspect == "16:9" else 6)
    rows = -(-len(ims) // cols)
    bad = {int(x.split()[0][1:]) for x in fails if x.startswith("v") and x.split()[0][1:].lstrip("-").isdigit()}
    S = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 30) + 40), (20, 20, 20))
    dr = ImageDraw.Draw(S)
    dr.text((10, 10), f"{target}  {aspect}  {'PASS' if not fails else f'FAIL ({len(fails)})'}", fill=(255, 255, 255))
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = 8 + c * (w + 8), 40 + r * (h + 30)
        S.paste(im.resize((w, h)), (x, y))
        dr.text((x, y + h + 6), f"v{i}" + ("  ✗" if i in bad else ""), fill=(255, 90, 80) if i in bad else (180, 180, 180))
    S.save(dst, quality=82)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=""); ap.add_argument("--aspect", default="16:9,9:16")
    ap.add_argument("--jobs", type=int, default=3); ap.add_argument("--no-snap", action="store_true")
    ap.add_argument("--plugins", action="store_true"); ap.add_argument("--skip-builtin", action="store_true")
    ap.add_argument("--targets", action="store_true", help="also run examples/stress/targets/*.json (on with --plugins)")
    ap.add_argument("--durations", action="store_true", help="also the 0.8 s / 6 s duration targets (on with --plugins)")
    ap.add_argument("--no-safe", action="store_true", help="skip the 9:16 safe-area rule")
    ap.add_argument("--aspects-extra", action="store_true", help="also 1:1 and 3:4 on a subset (on with --plugins)")
    ap.add_argument("--watermark", action="store_true", help="platform watermark zones on a subset (on with --plugins)")
    ap.add_argument("--only-aspects", action="store_true", help=argparse.SUPPRESS)
    a = ap.parse_args()
    P = pictures()
    targets = {}
    if not a.skip_builtin:
        targets.update(fx_variants(P))
        targets.update({f"press:{k}": v for k, v in PRESS.items()})
        targets.update({f"poster:{k}": v for k, v in POSTER.items()})
    if a.plugins:     # plugin effects carry their own variant beats (examples/aefx/variants.json, written with them)
        vp = SKILL / "examples" / "aefx" / "variants.json"
        base = SKILL / "examples" / "aefx"
        def absolutise(o):    # the plugin variants name their media relative to examples/aefx
            if isinstance(o, dict): return {k: absolutise(v) for k, v in o.items()}
            if isinstance(o, list): return [absolutise(v) for v in o]
            if isinstance(o, str) and MEDIA_RX.search(o) and not o.startswith("/") and (base / o).exists():
                return str((base / o).resolve())
            return o
        if vp.exists():
            vj = json.loads(vp.read_text())
            for b in vj.get("beats", vj if isinstance(vj, list) else []):
                b = absolutise({k: v for k, v in b.items() if k not in ("t", "d", "tr", "scene")})
                targets.setdefault(b["fx"], []).append({k: v for k, v in b.items() if k != "fx"})
        # and their gallery beat, as the "typical" variant
        av = json.loads((SKILL / "examples" / "aefx" / "video.json").read_text())
        from h9 import aefx   # noqa
        builtin = set(fx_variants(P))
        for b in av["beats"]:
            if b["fx"] not in builtin and b["fx"] != "plate" and b["fx"] in aefx.FX:
                targets.setdefault(b["fx"], []).insert(0, absolutise({k: v for k, v in b.items() if k not in ("t", "d", "tr", "scene", "fx")}))
    if a.plugins or a.targets:     # each work package ships its own entries: examples/stress/targets/<pkg>.json (three shapes, see top)
        for tf in sorted((SKILL / "examples" / "stress" / "targets").glob("*.json")):
            tj = json.loads(tf.read_text())
            tbase = (SKILL / tj["base"]).resolve() if isinstance(tj.get("base"), str) and tj.get("base") else tf.parent
            def tabs(o, tbase=tbase):
                if isinstance(o, dict): return {k: tabs(v) for k, v in o.items()}
                if isinstance(o, list): return [tabs(v) for v in o]
                if isinstance(o, str) and MEDIA_RX.search(o) and not o.startswith("/") and (tbase / o).exists():
                    return str((tbase / o).resolve())
                return o
            groups = {}
            if isinstance(tj.get("beats"), list):
                for b in tj["beats"]:
                    if b.get("fx"): groups.setdefault(b["fx"], []).append({k: v for k, v in b.items() if k not in ("t", "d", "tr", "scene", "fx")})
            elif isinstance(tj.get("targets"), dict):
                groups = tj["targets"]
            else:
                groups = {k: v for k, v in tj.items() if isinstance(v, list) and k not in ("allow", "durations")}
            for row in tj.get("allow", []):
                ALLOW.append(tuple(row))
            durs = tj.get("durations") or [None]
            for fxn, vs in groups.items():
                vs = [tabs(v) for v in vs]
                for dd in durs:
                    key = fxn if dd is None else f"{fxn}@{float(dd):g}"
                    targets.setdefault(key, []).extend(vs)
                    if tj.get("meta"): TMETA[key] = dict(tj["meta"])
    if a.plugins or a.durations:    # the same effect in a 0.8 s and a 6 s beat (elastic timing: fast entrance / kept alive)
        for fxn in DUR_FX:
            if fxn in targets and targets[fxn]:
                for dd in DUR_SET:
                    targets.setdefault(f"{fxn}@{dd:g}", targets[fxn][:2])
    if a.only:
        keep = set(a.only.split(","))
        targets = {k: v for k, v in targets.items() if k in keep or k.split(":")[-1] in keep or k.split("@")[0].split(":")[-1] in keep}
    jobs = [(t, v, asp) for t, v in targets.items() for asp in a.aspect.split(",")]
    if (a.plugins or a.aspects_extra) and not a.only_aspects:
        jobs += [(t, targets[t], asp) for t in ASPECT_SUBSET if t in targets for asp in EXTRA_ASPECTS]
    print(f"{len(targets)} targets × {len(a.aspect.split(','))} aspects (+ {len(EXTRA_ASPECTS)} extra aspects on a subset) = {len(jobs)} builds")
    res = []
    with ThreadPoolExecutor(max_workers=a.jobs) as ex:
        for r in ex.map(lambda j: run_target(j[0], j[1], j[2], not a.no_snap, not a.no_safe), jobs):
            res.append(r)
            print(("PASS " if r["ok"] else "FAIL ") + f"{r['target']:<18} {r['aspect']:<5} " + ("" if r["ok"] else f"{len(r['fails'])} issues"), flush=True)
            for f in r["fails"][:6]: print("      ", f)
    if (a.plugins or a.watermark) and not a.no_safe:
        for plat, (asp, zones) in WM.items():
            W_, H_ = (1080, 1920) if asp == "9:16" else (1920, 1080)
            for t in WM_SUBSET:
                if t not in targets or asp not in a.aspect.split(","): continue
                work = BUILD / f"{t.replace(':', '_')}_{asp.replace(':', 'x')}"
                if not (work / "index.html").exists(): continue
                d = 4.4 if ":" in t else BEAT.get(t, 2.6)
                if t.startswith("press:split"): d = 6.0
                style = "reel" if ":" not in t else t.split(":")[0]
                fl = safe_area(t, style, work, settle_times(t, len(targets[t]), d), d, zones=zones, W=W_, H=H_, extra_ex=WM_EXEMPT)
                r = {"target": f"{t} [wm {plat}]", "aspect": asp, "ok": not fl, "fails": fl, "known": [], "n": len(targets[t])}
                res.append(r)
                print(("PASS " if r["ok"] else "FAIL ") + f"{r['target']:<28} {asp:<5} " + ("" if r["ok"] else f"{len(fl)} issues"), flush=True)
                for f in fl[:4]: print("      ", f)
    ok = sum(r["ok"] for r in res)
    rep = [f"# 压力测试报告", "", f"{ok} / {len(res)} 通过（每个目标一个合成，每种输入一个 beat，横竖屏各一遍）。联系表在 `sheets/`。", "",
           "| 目标 | 画幅 | 变体 | 结果 |", "|---|---|---|---|"]
    for r in sorted(res, key=lambda r: (r["target"], r["aspect"])):
        rep.append(f"| `{r['target']}` | {r['aspect']} | {r.get('n', '')} | {'通过' if r['ok'] else '✗ ' + str(len(r['fails']))} |")
    kn = [r for r in res if r.get("known")]
    if kn:
        rep += ["", "## 已知问题（不计入失败，留给效果作者）", ""]
        notes = {}
        for r in kn:
            for p, rx, note in KNOWN:
                if r["target"].startswith(p) and any(re.search(rx, x) for x in r["known"]): notes.setdefault(note, []).append(f"{r['target']} {r['aspect']}")
        rep += [f"- {n}（{', '.join(v)}）" for n, v in notes.items()]
    fails = [r for r in res if not r["ok"]]
    if fails:
        rep += ["", "## 未通过", ""]
        for r in fails:
            rep.append(f"### `{r['target']}` {r['aspect']}"); rep += [f"- {x}" for x in r["fails"][:20]]; rep.append("")
    rp = OUT / ("report.md" if not a.only else f"report_{re.sub(r'[^A-Za-z0-9_]+', '-', a.only)[:60]}.md")   # partial runs never overwrite the full report
    rp.write_text("\n".join(rep) + "\n")
    print(f"\n{ok}/{len(res)} passed → {rp}")
    sys.exit(0 if ok == len(res) else 1)


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
