#!/usr/bin/python3
# custom viewport settings BEGIN
MARGIN_ARCSEC = 300          # margins of map tiles
OFFSETLON = 0		     # correction of center of tiles - longitude
OFFSETLAT = 0.07	     # correction of center of tiles - latitude
# custom viewport settings END

MARGIN_DEG = MARGIN_ARCSEC / 3600.0
import sys
import os
import gpxpy
import matplotlib.pyplot as plt
import contextily as cx
from pyproj import Transformer

def load_tracks(path):
    with open(path) as f:
        gpx = gpxpy.parse(f)

    tracks = []
    for trk in gpx.tracks:
        pts = []
        for seg in trk.segments:
            for p in seg.points:
                pts.append((p.longitude, p.latitude))
        if pts:
            tracks.append(pts)
    return tracks


def project(points):
    t = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    xs, ys = zip(*[t.transform(lon, lat) for lon, lat in points])
    return xs, ys


def flatten_tracks(tracks):
    """Zploštění: list[list[(lon, lat)]] -> list[(lon, lat)]"""
    return [pt for trk in tracks for pt in trk]


all_gpx, part_gpx, out_png, title = sys.argv[1:]
fig, ax = plt.subplots(figsize=(10, 8))

if os.path.exists(all_gpx):
    all_tracks = load_tracks(all_gpx)
    for trk in all_tracks:
        x, y = project(trk)
        ax.plot(x, y, color="gray", linewidth=2)

if os.path.exists(part_gpx):
    part_tracks = load_tracks(part_gpx)
    for trk in part_tracks:
        x, y = project(trk)
        ax.plot(x, y, color="red", linewidth=3)


# extent v zeměpisných souřadnicích
#all_pts = flatten_tracks(all_tracks + part_tracks)
all_pts = flatten_tracks(all_tracks)
lons = [p[0] for p in all_pts]
lats = [p[1] for p in all_pts]

min_lon = min(lons) - MARGIN_DEG + OFFSETLON
max_lon = max(lons) + MARGIN_DEG + OFFSETLON
min_lat = min(lats) - MARGIN_DEG + OFFSETLAT  
max_lat = max(lats) + MARGIN_DEG + OFFSETLAT

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

plt.savefig(out_png, dpi=300, bbox_inches="tight")
plt.close()
