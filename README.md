# beercompass

A single static page that points your phone at the nearest pub in the UK, with its name and distance.

- `index.html` – the compass. Tap "Find beer", allow location and motion access.
- `scripts/build_tiles.py` – pulls every UK `amenity=pub` from OpenStreetMap (Overpass) and splits them into 1° tiles at `data/<lat>_<lon>.json`.
- `.github/workflows/deploy.yml` – runs the script weekly (and on push to `main`) and deploys the page plus tiles to GitHub Pages.

Run locally:

```sh
python3 scripts/build_tiles.py data
python3 -m http.server
```

Geolocation and compass need HTTPS on a real phone, so test on the deployed Pages URL.

Pub data © OpenStreetMap contributors, ODbL.
