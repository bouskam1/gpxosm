GPX OSM Toolkit
===============
MIT License
Copyright (c) 2025 Martin Bouška (https://github.com/bouskam1)
© OpenStreetMap contributors
This project generates maps using OpenStreetMap tiles.
Portions of this software were developed with the assistance of an AI tool.

Requirements:
- bash
- xmllint
- python3

Python packages:
pip install gpxpy matplotlib contextily pyproj

xmllint:
brew install libxml2

Usage:
1. Put GPX files into ./gpx
2. chmod +x process_gpx.sh
3. ./process_gpx.sh
4. Check content of ./output folder. If center or margins of map tiles need corrections, adjust first 5 lines of render2_osm.py file and run it again.

Output:
- output/merged.gpx
- output/maps/*.png
