"""shared helpers for the map effects (not an effect: files starting with _ are skipped by the loader).
d3 + topojson-client load from jsdelivr (ISC, like GSAP); the land outline is inlined once per page so it is
ready synchronously when the timeline script runs."""
from pathlib import Path

D3 = "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"
TOPO = "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"
DATA = Path(__file__).parent / "data"


def need_geo(X):
    if "H9GEO" in X.extra_head: return
    land = (DATA / "land-50m.topo.json").read_text()
    X.extra_head += (f'<script src="{D3}"></script>\n<script src="{TOPO}"></script>\n'
                     f'<script>window.H9GEO = window.H9GEO || {{}}; H9GEO.land = {land};</script>\n')
