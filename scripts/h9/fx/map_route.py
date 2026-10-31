"""地图路线 Map Route (#19, Map Route Generator 3.5K; Ignace Aleya 动画旅行地图 169.5 万播放):
a land-only map fitted to the route, the route draws on as a great-circle line with a glowing head that carries
the vehicle; start and end pins pop with their names, and the trip's numbers count in as chips.

Adapts: 2 points up to a long multi-stop corridor ("points"), optional named stops along it ("stops": [[name,
lon, lat], ...]), routes that cross the date line (the map re-centres on the route), any name length (fitted),
0–5 chips (wrap). Land only, no borders. p: points · from · to · from_sub · to_sub · stops · chips"""
import json
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__geo" not in sys.modules:    # scripts/h9/fx.py shadows this folder as a package, so load the helper by path
    _s = importlib.util.spec_from_file_location("h9fx__geo", pathlib.Path(__file__).with_name("_geo.py"))
    sys.modules["h9fx__geo"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__geo"])
need_geo = sys.modules["h9fx__geo"].need_geo


def map_route(X, cid, t, d, p):
    need_geo(X)
    W, H = X.W, X.H
    pts = [list(map(float, q)) for q in p["points"]]   # [[lon, lat], ...] start → end (waypoints keep the line on its real corridor)
    for i in range(1, len(pts)):              # unwrap longitudes so a trans-Pacific line stays continuous
        while pts[i][0] - pts[i - 1][0] > 180: pts[i][0] -= 360
        while pts[i][0] - pts[i - 1][0] < -180: pts[i][0] += 360
    clon = (min(q[0] for q in pts) + max(q[0] for q in pts)) / 2
    stops = p.get("stops", [])
    nm = lambda txt: min(3.6, 30 / max(len(str(txt)) * 1.0, 1))
    a, b = p.get("from", ""), p.get("to", "")
    pad = (dict(l=90, r=90, t=330, b=640) if X.portrait else dict(l=200, r=200, t=170, b=230))
    X.css("fx-mr", """
.fx .mrw, .fx .mr { position:absolute; inset:0; width:100%; height:100%; }
.fx .mr .mrl { fill:color-mix(in srgb, var(--fg) 20%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 30%, transparent); stroke-width:1; }
.fx .mr .mrg { fill:none; stroke:color-mix(in srgb, var(--fg) 8%, transparent); stroke-width:1; }
.fx .mr .rt0 { fill:none; stroke:color-mix(in srgb, var(--accent) 30%, transparent); stroke-width:10; stroke-linecap:round; stroke-linejoin:round; }
.fx .mr .rt { fill:none; stroke:var(--accent); stroke-width:5; stroke-linecap:round; stroke-linejoin:round; }
.fx .mr .mrh { fill:var(--accent); } .fx .mr .mrhr { fill:none; stroke:var(--accent); stroke-width:3; }
.fx .mrp { position:absolute; left:0; top:0; width:0; height:0; }
.fx .mrp i { position:absolute; left:-1vmin; top:-1vmin; width:2vmin; height:2vmin; border-radius:50%; background:var(--fg); box-shadow:0 0 0 .45vmin var(--bg); }
.fx .mrp.e i { background:var(--accent); }
.fx .mrp span { position:absolute; bottom:2vmin; left:50%; transform:translateX(-50%); white-space:nowrap; font-family:var(--f-display); font-weight:900; color:var(--fg); text-shadow:0 0 .8vmin var(--bg), 0 0 .8vmin var(--bg); }
.fx .mrp.st i { width:1.4vmin; height:1.4vmin; left:-.7vmin; top:-.7vmin; background:var(--bg); border:.35vmin solid var(--accent); box-shadow:none; }
.fx .mrp.st span { font-weight:700; color:var(--muted); }
.fx .mrp small { position:absolute; top:2vmin; left:50%; transform:translateX(-50%); white-space:nowrap; font:500 1.7vmin var(--f-mono, monospace); color:var(--muted); letter-spacing:.06em; }
.fx .mrc { position:absolute; left:50%; bottom:18vmin; transform:translateX(-50%); display:flex; flex-wrap:wrap; justify-content:center; gap:2vmin; width:max-content; max-width:88vw; }
.fx .mrc div { font:900 4.2vmin var(--f-display); color:var(--fg); background:var(--card); border:.3vmin solid var(--fg); padding:.6vmin 2.2vmin; box-shadow:.6vmin .6vmin 0 var(--fg); white-space:nowrap; }
.fx .mrc div em { font-style:normal; color:var(--accent); }
#root.v .fx .mrc { bottom:auto; top:58%; flex-direction:column; align-items:center; }
""")
    chips = "".join(f'<div>{X.rich(c)}</div>' for c in p.get("chips", []))
    inner = (f'<div class="mrw"><svg class="mr" viewBox="0 0 {W} {H}"><g class="cam"><path class="mrg"/><path class="mrl"/><path class="rt0"/><path class="rt"/>'
             f'<circle class="mrhr" r="16"/><circle class="mrh" r="9"/></g></svg>'
             + "".join(f'<div class="mrp st" data-k="{k}"><i></i><span style="font-size:{nm(sn) * 0.7:.2f}vmin">{X.rich(sn)}</span></div>' for k, (sn, _, _) in enumerate(stops))
             + f'<div class="mrp s"><i></i><span style="font-size:{nm(a):.2f}vmin">{X.rich(a)}</span><small>{X.rich(p.get("from_sub", ""))}</small></div>'
             f'<div class="mrp e"><i></i><span style="font-size:{nm(b):.2f}vmin">{X.rich(b)}</span><small>{X.rich(p.get("to_sub", ""))}</small></div></div><div class="mrc">{chips}</div>')
    _clip(X, cid, t, d, inner, p)
    dr = max(1.2, d * 0.55)
    X.tw(f'''(()=>{{const G=H9GEO.land, land=topojson.feature(G,G.objects.land), sv=document.querySelector("#{cid} .mr"), P={json.dumps(pts)};
const line={{type:"LineString",coordinates:P}};
const pr=d3.geoMercator().rotate([{-clon:.2f},0]).fitExtent([[{pad["l"]},{pad["t"]}],[{W - pad["r"]},{H - pad["b"]}]], line), pa=d3.geoPath(pr);
sv.querySelector(".mrl").setAttribute("d",pa(land)); sv.querySelector(".mrg").setAttribute("d",pa(d3.geoGraticule().step([10,10])()));
const R=sv.querySelector(".rt"), R0=sv.querySelector(".rt0"), hd=sv.querySelector(".mrh"), hr=sv.querySelector(".mrhr");
R.setAttribute("d",pa(line)); R0.setAttribute("d",pa(line)); const L=R.getTotalLength();
const s=pr(P[0]), e=pr(P[P.length-1]), root=document.getElementById("{cid}");
root.querySelector(".mrp.s").style.transform=`translate(${{s[0]}}px,${{s[1]}}px)`; root.querySelector(".mrp.e").style.transform=`translate(${{e[0]}}px,${{e[1]}}px)`;
const ST={json.dumps([[lo_, la_] for _, lo_, la_ in stops])}; root.querySelectorAll(".mrp.st").forEach((el,k)=>{{const q=pr(ST[k]); el.style.transform=`translate(${{q[0]}}px,${{q[1]}}px)`;}});
function draw(k){{const off=L*(1-k); R.style.strokeDasharray=L; R.style.strokeDashoffset=off; R0.style.strokeDasharray=L; R0.style.strokeDashoffset=off;
const q=R.getPointAtLength(L*k); hd.setAttribute("cx",q.x); hd.setAttribute("cy",q.y); hr.setAttribute("cx",q.x); hr.setAttribute("cy",q.y);
hd.style.opacity=k>0.001&&k<0.999?1:0; hr.style.opacity=hd.style.opacity;}}
draw(0); const o={{k:0}}; tl.to(o,{{k:1,duration:{dr:.2f},ease:"power2.inOut",onUpdate:()=>draw(o.k)}},{t + 0.45:.3f});}})();''')
    X.tw(f'tl.fromTo("#{cid} .mrw", {{scale:1.08, transformOrigin:"50% 50%"}}, {{scale:1, duration:{d:.2f}, ease:"power1.out"}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .mr .mrl, #{cid} .mr .mrg", {{opacity:0, duration:0.5}}, {t:.3f});')
    X.tw(f'tl.from("#{cid} .mrp.s i", {{scale:0, duration:0.35, ease:"back.out(3)"}}, {t + 0.25:.3f});')
    X.tw(f'tl.from("#{cid} .mrp.s span, #{cid} .mrp.s small", {{y:12, opacity:0, duration:0.4, ease:"expo.out", stagger:0.06}}, {t + 0.3:.3f});')
    te = t + 0.45 + dr
    X.tw(f'tl.from("#{cid} .mrp.e i", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {te - 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .mrp.e span, #{cid} .mrp.e small", {{y:12, opacity:0, duration:0.4, ease:"expo.out", stagger:0.06}}, {te:.3f});')
    X.tw(f'tl.from("#{cid} .mrc div", {{y:30, opacity:0, duration:0.45, ease:"back.out(2)", stagger:0.12}}, {te + 0.1:.3f});')
    for k, (sn, slo, sla) in enumerate(stops):             # each stop pops as the head passes (by order along the route)
        tk = t + 0.45 + dr * (k + 1) / (len(stops) + 1)
        X.tw(f'tl.from("#{cid} .mrp.st[data-k=\'{k}\'] i, #{cid} .mrp.st[data-k=\'{k}\'] span", {{scale:0, opacity:0, duration:0.3, ease:"back.out(3)"}}, {tk:.3f});')
    X.sfx(t + 0.45, "whoosh_soft"); X.sfx(te, "pop")


FX = {"map_route": map_route}
