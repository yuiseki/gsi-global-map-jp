# gsi-global-map-jp

A reproducible copy of Global Map Japan (地球地図日本), the 1:1,000,000 map of
Japan that the Geospatial Information Authority of Japan (GSI) made to the
Global Map Specifications of the International Steering Committee for Global
Mapping (ISCGM).

- Vector data (Shapefile): administrative boundaries, drainage, population
  centres and transportation, in versions 2.0 (published 2011), 2.1 (2015) and
  2.2 (2016). Versions 2.1 and 2.2 updated only some layers; each version's
  all-layer zip holds every layer.
- Raster data (GeoTIFF): elevation, land cover, land use and vegetation, in
  versions 1.0 (2000) and 1.1 (2006).

GSI is the only primary distributor of the Japanese edition; the Global Map
data archives on GitHub point back to it.

## Source

- Page and download table: <https://www.gsi.go.jp/kankyochiri/gm_jpn.html>
  (English: <https://www.gsi.go.jp/kankyochiri/gm_japan_e.html>)
- Files: `https://www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/`
- Specifications: <https://github.com/globalmaps/specifications>

GSI has replaced some files after publication (for example the all-layer zip
of version 2.2 carries a 2023 Last-Modified). The download script reports such
a change instead of overwriting the copy it holds.

## Licence

The data is under the GSI Content Terms of Use (国土地理院コンテンツ利用規約),
which apply the Public Data License 1.0 (公共データ利用規約 第1.0版, PDL1.0),
compatible with CC BY 4.0: reuse, including commercial use, is allowed with
attribution to GSI.
<https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html>

## Usage

```sh
uv run python scripts/01_download.py        # fetch every zip in the download table
uv run python scripts/03_export_parquet.py  # one GeoParquet per vector version and layer
uv run python scripts/02_verify.py          # check the zips, and the Parquet against them
uv run python src/publish.py                # dry run: list what would be uploaded
uv run python src/publish.py --push         # upload to huggingface.co/datasets/yuiseki/gsi-global-map-jp
uv run python -m pytest                     # unit tests
```

`03_export_parquet.py` extracts the all-layers zip of each vector version
(2.0, 2.1, 2.2) to `data/work/`, reads each of its 15 Shapefiles with
DuckDB's spatial extension and writes `data/parquet/<version>/<layer>.parquet`
(GeoParquet, zstd, no bloom filters), then deletes the extracted files.
Column types come from the column names (the Global Map attribute codes,
`pop` and `ypc` are INTEGER, everything else text); a value that does not
fit stops the run. Coordinates are not reprojected: each file states the CRS
its `.prj` names (ITRF94 for most layers, JGD2000 for `airp` of 2.1 and 2.2
and `roadl` of 2.2), and a `.prj` the script has no rule for stops the run.
The rasters are published as GSI's zips only.

`02_verify.py` checks every zip against its manifest and, once the Parquet
exists, every layer against the Shapefiles in the zip, read with small
readers of its own (DBF, SHP, WKB): row counts, every attribute value, every
coordinate, column types, the CRS, that a DuckDB without extensions opens
the files, and that there are no bloom filters.

`src/publish.py` uploads `data/README.md` (the dataset card),
`data/LICENSE`, `data/provenance.yaml`, the Parquet and the raw zips with
their manifests. It is a dry run unless `--push` is given, and refuses to
run if a raw file's sha256 differs from its manifest or the card does not
declare every Parquet file as a subset.

`01_download.py` reads the file URLs from the download table on the page,
needs only the Python standard library, and turns on TLS legacy renegotiation
(`ssl.OP_LEGACY_SERVER_CONNECT`), which gsi.go.jp still requires. It is
idempotent: a file whose sha256 matches its manifest entry is not fetched again.

## Layout

```
scripts/01_download.py        fetch the zips listed on the page
scripts/02_verify.py          re-hash and test every fetched file, check the Parquet
scripts/03_export_parquet.py  Shapefiles to GeoParquet
src/publish.py                upload to the Hugging Face Hub
tests/                        unit tests; fixtures trimmed from the page
data/README.md                the dataset card
data/LICENSE                  the licence and what the Parquet changes
data/provenance.yaml          source, versions, files, counts, checks
data/parquet/<version>/       <layer>.parquet, made by 03 (not in git)
data/work/                    extracted Shapefiles, deleted after 03 (not in git)
data/raw/<map version>/       the zips as served (not in git)
    vector-2.2/ vector-2.1/ vector-2.0/ raster-1.1/ raster-1.0/
    MANIFEST.json             url, bytes, sha256, last_modified, fetched_at,
                              and the layer, publication year, specification
                              version and link text the page gives each file
```
