"""Fetch every UK pub from OpenStreetMap and split them into 1-degree tiles.

Writes <out>/<floor(lat)>_<floor(lon)>.json, each a list of [lat, lon, name].
Uses only the standard library so the GitHub Action needs no installs.
"""

import json
import math
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
QUERY = """
[out:json][timeout:600];
area["ISO3166-1"="GB"][admin_level=2]->.uk;
nwr["amenity"="pub"](area.uk);
out center tags qt;
"""


def fetch_pubs():
    body = urllib.parse.urlencode({"data": QUERY}).encode()
    request = urllib.request.Request(
        OVERPASS_URL,
        data=body,
        headers={"User-Agent": "beercompass (github.com/sbmooc/beercompass)"},
    )
    with urllib.request.urlopen(request, timeout=900) as response:
        elements = json.load(response)["elements"]

    pubs = []
    for element in elements:
        # Nodes carry lat/lon directly; ways and relations get a computed centre.
        point = element.get("center", element)
        if "lat" not in point:
            continue
        name = element.get("tags", {}).get("name")
        pubs.append([round(point["lat"], 5), round(point["lon"], 5), name])
    return pubs


def write_tiles(pubs, out_dir):
    tiles = defaultdict(list)
    for pub in pubs:
        tiles[f"{math.floor(pub[0])}_{math.floor(pub[1])}"].append(pub)

    out_dir.mkdir(parents=True, exist_ok=True)
    for key, tile_pubs in tiles.items():
        path = out_dir / f"{key}.json"
        path.write_text(json.dumps(tile_pubs, ensure_ascii=False, separators=(",", ":")))
    return tiles


def main():
    out_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    pubs = fetch_pubs()
    if len(pubs) < 10000:
        # Overpass occasionally returns partial results; don't deploy a broken dataset.
        sys.exit(f"Only got {len(pubs)} pubs, refusing to write tiles")
    tiles = write_tiles(pubs, out_dir)
    print(f"Wrote {len(pubs)} pubs into {len(tiles)} tiles in {out_dir}/")


if __name__ == "__main__":
    main()
