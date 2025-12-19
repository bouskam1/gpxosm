#!/usr/bin/python3
MARGIN_ARCSEC = 200          # uživatelské nastavení
MARGIN_DEG = MARGIN_ARCSEC / 3600.0
import sys
import gpxpy
import matplotlib.pyplot as plt
import contextily as cx
from pyproj import Transformer

def load_points(path):
    with open(path) as f:
        gpx = gpxpy.parse(f)
    pts = []
    for trk in gpx.tracks:
        for seg in trk.segments:
            for p in seg.points:
                pts.append((p.longitude, p.latitude))
    return pts

def project(pts):
    t = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    xs, ys = zip(*[t.transform(lon, lat) for lon, lat in pts])
    return xs, ys

all_gpx, part_gpx, out_png, title = sys.argv[1:]

all_pts = load_points(all_gpx)
part_pts = load_points(part_gpx)

ax_x, ax_y = project(all_pts)
px, py = project(part_pts)

fig, ax = plt.subplots(figsize=(10, 8))
ax.plot(ax_x, ax_y, color="gray", linewidth=3)
ax.plot(px, py, color="red", linewidth=3)

#ax.set_xlim(min(ax_x), max(ax_x))
#ax.set_ylim(min(ax_y), max(ax_y))
# extent v zeměpisných souřadnicích
lons = [p[0] for p in all_pts]
lats = [p[1] for p in all_pts]

min_lon = min(lons) - MARGIN_DEG
max_lon = max(lons) + MARGIN_DEG
min_lat = min(lats) - MARGIN_DEG
max_lat = max(lats) + MARGIN_DEG

# projekce extentu
x0, y0 = Transformer.from_crs(
    "EPSG:4326", "EPSG:3857", always_xy=True
).transform(min_lon, min_lat)

x1, y1 = Transformer.from_crs(
    "EPSG:4326", "EPSG:3857", always_xy=True
).transform(max_lon, max_lat)

ax.set_xlim(x0, x1)
ax.set_ylim(y0, y1)

cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
ax.set_title(title)
ax.axis("off")

plt.savefig(out_png, dpi=200, bbox_inches="tight")
plt.close()
