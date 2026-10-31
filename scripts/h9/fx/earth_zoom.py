"""地球推近 Earth Zoom (#8, Ultimate Earth Zoom Toolkit 9.5K; Google Earth Studio 缩放教程 207 万播放):
the globe turns to bring the target round, then the camera dives in exponentially (so the zoom reads as one
constant speed) until the region fills the frame; a pin drops on the spot with its label.

Adapts: any lon/lat (the turn always takes the short way round); how close it ends is "km" (width of the final
view, default 900) or "zoom"; place names from 1 glyph to a long name and subtitles up to a sentence are fitted
(label goes beside the pin in 16:9, under it in 9:16). p: lon · lat · text · sub · km | zoom · from_lon · from_lat"""
from h9 import aefx
from h9.aefx import _clip
import importlib.util, pathlib, sys
if "h9fx__geo" not in sys.modules:    # scripts/h9/fx.py shadows this folder as a package, so load the helper by path
    _s = importlib.util.spec_from_file_location("h9fx__geo", pathlib.Path(__file__).with_name("_geo.py"))
    sys.modules["h9fx__geo"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__geo"])
need_geo = sys.modules["h9fx__geo"].need_geo
if "h9fx__fit" not in sys.modules:
    _s = importlib.util.spec_from_file_location("h9fx__fit", pathlib.Path(__file__).with_name("_fit.py"))
    sys.modules["h9fx__fit"] = importlib.util.module_from_spec(_s); _s.loader.exec_module(sys.modules["h9fx__fit"])
F = sys.modules["h9fx__fit"]


aefx.PHOTO.add("earth_zoom")     # map fills the frame: header/footer get the on-image treatment


def earth_zoom(X, cid, t, d, p):
    need_geo(X)
    W, H = X.W, X.H
    lon, lat = float(p.get("lon", 121.5)), float(p.get("lat", 31.2))
    l0, f0 = float(p.get("from_lon", lon - 75)), float(p.get("from_lat", 8))
    r0 = 0.30 * min(W, H)
    if p.get("zoom"): Z = float(p["zoom"])
    else:                                     # final view ≈ km wide: radius_px = W / (km / 6371)
        Z = max(4.0, min(400.0, (W / (float(p.get("km", 900)) / 6371.0)) / r0))
    dl = ((lon - l0 + 180) % 360) - 180; l0 = lon - dl          # shortest way round
    Wv, Hv = F.frame_vmin(X)
    lw = (Wv * 0.8) if X.portrait else (Wv * 0.5 - 8)
    ls, ll = F.fit(p.get("text", ""), lw, 22, 9.0, 3.5, 2)
    ss, sl = F.fit(p.get("sub", ""), lw, 8, 2.6, 1.6, 2)
    X.css("fx-ez", """
.fx .ez { position:absolute; inset:0; width:100%; height:100%; }
.fx .ez .ezs { fill:color-mix(in srgb, var(--fg) 7%, var(--bg)); stroke:color-mix(in srgb, var(--fg) 35%, transparent); stroke-width:1.5; }
.fx .ez .ezg { fill:none; stroke:color-mix(in srgb, var(--fg) 13%, transparent); stroke-width:1; }
.fx .ez .ezl { fill:color-mix(in srgb, var(--fg) 82%, var(--bg)); stroke:var(--bg); stroke-width:1; stroke-linejoin:round; }
.fx .ezpin { position:absolute; left:50%; top:50%; width:0; height:0; }
.fx .ezpin i { position:absolute; left:-1.1vmin; top:-1.1vmin; width:2.2vmin; height:2.2vmin; border-radius:50%; background:var(--accent); box-shadow:0 0 0 .5vmin var(--bg); }
.fx .ezpin b { position:absolute; left:-1.1vmin; top:-1.1vmin; width:2.2vmin; height:2.2vmin; border-radius:50%; border:.35vmin solid var(--accent); }
.fx .ezlab { position:absolute; left:3.6vmin; top:-5.4vmin; }
.fx .ezlab strong { display:block; font-family:var(--f-display); font-weight:900; line-height:1.05; color:var(--fg); letter-spacing:-.01em; text-shadow:0 0 .4vmin var(--bg), 0 .2vmin 1.4vmin var(--bg), 0 0 3.6vmin color-mix(in srgb, var(--bg) 85%, transparent); }
.fx .ezlab strong .fl, .fx .ezlab em .fl { display:block; white-space:nowrap; }
.fx .ezlab em { display:inline-block; font-style:normal; margin-top:1.2vmin; font-family:var(--f-body); font-weight:700; line-height:1.35; color:var(--bg); background:var(--accent); padding:.4vmin 1.2vmin; }
.fx .ezco { position:absolute; left:3.6vmin; top:calc(100% + 1vmin); font:500 1.7vmin var(--f-mono, monospace); color:var(--fg); opacity:.75; letter-spacing:.08em; white-space:nowrap; }
#root.v .fx .ezlab { left:0; top:5vmin; transform:translateX(-50%); text-align:center; } #root.v .fx .ezco { left:50%; transform:translateX(-50%); }
""")
    co = f'{abs(lat):.2f}°{"N" if lat >= 0 else "S"}  {abs(lon):.2f}°{"E" if lon >= 0 else "W"}'
    X.used_text.update(co)
    inner = (f'<svg class="ez" viewBox="0 0 {W} {H}"><defs><radialGradient id="{cid}hal"><stop offset=".86" style="stop-color:var(--accent);stop-opacity:0"/>'
             f'<stop offset=".9" style="stop-color:var(--accent);stop-opacity:.22"/><stop offset="1" style="stop-color:var(--accent);stop-opacity:0"/></radialGradient></defs>'
             f'<circle class="halo" cx="{W / 2}" cy="{H / 2}" r="{r0 * 1.12:.1f}" fill="url(#{cid}hal)"/><path class="ezs"/><path class="ezg"/><path class="ezl"/></svg>'
             f'<div class="ezpin"><b></b><b></b><i></i><div class="ezlab"><strong style="font-size:{ls:.2f}vmin">{F.lines_html(X, ll)}</strong>'
             f'<em style="font-size:{ss:.2f}vmin">{F.lines_html(X, sl)}</em><div class="ezco">{co}</div></div></div>')
    _clip(X, cid, t, d, inner, p)
    dz = max(1.4, d * 0.7)
    X.tw(f'''(()=>{{const G=H9GEO.land, land=topojson.feature(G,G.objects.land), sv=document.querySelector("#{cid} .ez");
const pr=d3.geoOrthographic().translate([{W / 2},{H / 2}]).clipAngle(90).precision(0.4), pa=d3.geoPath(pr), gr=d3.geoGraticule10();
const S=sv.querySelector(".ezs"), Gr=sv.querySelector(".ezg"), L=sv.querySelector(".ezl"), Ha=sv.querySelector(".halo");
function draw(k){{const q=Math.min(1,k/0.6), e=q<.5?4*q*q*q:1-Math.pow(-2*q+2,3)/2;
pr.rotate([-({l0}+({lon}-{l0})*e), -({f0}+({lat}-{f0})*e)]); const s={r0:.1f}*Math.pow({Z},k); pr.scale(s);
S.setAttribute("d",pa({{type:"Sphere"}})); Gr.setAttribute("d",pa(gr)||""); L.setAttribute("d",pa(land)||""); Ha.setAttribute("r",(s*1.12).toFixed(1));}}
draw(0); const o={{k:0}}; tl.to(o,{{k:1,duration:{dz:.2f},ease:"power2.inOut",onUpdate:()=>draw(o.k)}},{t + 0.1:.3f});}})();''')
    tp = t + 0.1 + dz - 0.15
    X.tw(f'tl.from("#{cid} .ezpin i", {{scale:0, duration:0.4, ease:"back.out(3)"}}, {tp:.3f});')
    X.tw(f'tl.fromTo("#{cid} .ezpin b", {{scale:1, opacity:1}}, {{scale:4.5, opacity:0, duration:1.1, ease:"power2.out", stagger:0.35}}, {tp + 0.05:.3f});')
    X.tw(f'tl.from("#{cid} .ezlab strong", {{x:-30, opacity:0, duration:0.5, ease:"expo.out"}}, {tp + 0.1:.3f});')
    X.tw(f'tl.from("#{cid} .ezlab em, #{cid} .ezco", {{y:14, opacity:0, duration:0.4, ease:"expo.out", stagger:0.08}}, {tp + 0.25:.3f});')
    X.sfx(t + 0.1, "whoosh_deep"); X.sfx(tp, "pop")


FX = {"earth_zoom": earth_zoom}
