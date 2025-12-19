#!/usr/bin/env bash
set -euo pipefail

# ===============================
# KONFIGURACE
# ===============================
GPX_DIR="gpx"
OUT_DIR="output"
MAP_DIR="$OUT_DIR/maps"

mkdir -p "$OUT_DIR" "$MAP_DIR"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# ===============================
# 1) NAČTENÍ ČASŮ (namespace-safe)
# ===============================
META="$TMP/meta.txt"
> "$META"

for f in "$GPX_DIR"/*.gpx; do
  start=$(xmllint --xpath \
    'string((//*[local-name()="trkpt"]/*[local-name()="time"])[1])' "$f")

  end=$(xmllint --xpath \
    'string((//*[local-name()="trkpt"]/*[local-name()="time"])[last()])' "$f")

  if [[ -z "$start" || -z "$end" ]]; then
    echo "❌ Chybí časový údaj v $f"
    exit 1
  fi

  echo "$start|$end|$f" >> "$META"
done

# ===============================
# 2) ŘAZENÍ + KONTROLA PŘEKRYVŮ
# ===============================
SORTED="$TMP/sorted.txt"
sort "$META" > "$SORTED"

prev_end=""
while IFS='|' read -r start end file; do
  if [[ -n "$prev_end" && "$start" < "$prev_end" ]]; then
    echo "❌ Časový překryv detekován:"
    echo "   $file"
    echo "   start=$start < prev_end=$prev_end"
    exit 1
  fi
  prev_end="$end"
done < "$SORTED"

# ===============================
# 3) PŘÍPRAVA NÁZVŮ TRAS
# ===============================
NAMED="$TMP/named.txt"
> "$NAMED"

while IFS='|' read -r start end file; do
  label="route ${start:0:10} ${start:11:5}"
  echo "$file|$label" >> "$NAMED"
done < "$SORTED"
# ===============================
# 4) MERGE GPX (FINÁLNÍ SPRÁVNÁ)
# ===============================
MERGED="$OUT_DIR/merged.gpx"

shopt -s nullglob
files=("$GPX_DIR"/*.gpx)
(( ${#files[@]} )) || { echo "❌ Žádné GPX soubory"; exit 1; }
FIRST_GPX=$(head -n 1 "$SORTED" | cut -d '|' -f3)
tail -n +2 $SORTED > $TMP/rest.txt

{
  # XML hlavička
  echo '<?xml version="1.0" encoding="UTF-8"?>'

  # otevření <gpx ...> BEZ uzavření
  xmllint --xpath '/*[local-name()="gpx"]' "$FIRST_GPX" \
    | sed 's|</gpx>||'

  # metadata jen jednou (pokud existují)
  xmllint --xpath '//*[local-name()="metadata"]' "$FIRST_GPX" 2>/dev/null || true

  # všechny dalsi tracky v časovém pořadí
  while IFS='|' read -r start end file; do
    xmllint --xpath '//*[local-name()="trk"]' "$file"
#  done < "$SORTED"
   done < $TMP/rest.txt

  # korektní uzavření
  echo '</gpx>'
} > "$MERGED"
# ===============================
# 5) GENEROVÁNÍ MAP (OSM tiles)
# ===============================
idx=1
while IFS='|' read -r file label; do
  python3 render2_osm.py \
    "$MERGED" \
    "$file" \
    "$MAP_DIR/route_$idx.png" \
    "$label"

  echo "🗺️  vytvořena mapa route_$idx.png"
  ((idx++))
done < "$NAMED"

# ===============================
# 6) MAPA CELÉ TRASY (merged)
# ===============================
python3 render2_osm.py \
  "$MERGED" \
  "$MERGED" \
  "$MAP_DIR/route_all.png" \
  "Complete route"

echo "🗺️  vytvořena mapa celé trasy route_all.png"

python3 render2_osm.py \
  "$MERGED" \
  "null" \
  "$MAP_DIR/route_inactive.png" \
  "Complete route - inactive"
echo "🗺️   vytvořena mapa celé trasy route_inactive.png"

echo "🎉 Hotovo"
