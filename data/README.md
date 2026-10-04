---
license: cc-by-4.0
language:
- en
pretty_name: Global Map Japan (地球地図日本)
tags:
- geospatial
- geoparquet
- gis
- japan
- global-map
- administrative-boundaries
- roads
- railways
- rivers
size_categories:
- 10K<n<100K
configs:
- config_name: 'vector-2.2.airp'
  data_files: parquet/vector-2.2/airp.parquet
- config_name: 'vector-2.2.builtupa'
  data_files: parquet/vector-2.2/builtupa.parquet
- config_name: 'vector-2.2.builtupp'
  data_files: parquet/vector-2.2/builtupp.parquet
- config_name: 'vector-2.2.coastl'
  data_files: parquet/vector-2.2/coastl.parquet
- config_name: 'vector-2.2.ferryl'
  data_files: parquet/vector-2.2/ferryl.parquet
- config_name: 'vector-2.2.inwatera'
  data_files: parquet/vector-2.2/inwatera.parquet
- config_name: 'vector-2.2.miscl'
  data_files: parquet/vector-2.2/miscl.parquet
- config_name: 'vector-2.2.miscp'
  data_files: parquet/vector-2.2/miscp.parquet
- config_name: 'vector-2.2.polbnda'
  data_files: parquet/vector-2.2/polbnda.parquet
  default: true
- config_name: 'vector-2.2.polbndl'
  data_files: parquet/vector-2.2/polbndl.parquet
- config_name: 'vector-2.2.portp'
  data_files: parquet/vector-2.2/portp.parquet
- config_name: 'vector-2.2.raill'
  data_files: parquet/vector-2.2/raill.parquet
- config_name: 'vector-2.2.riverl'
  data_files: parquet/vector-2.2/riverl.parquet
- config_name: 'vector-2.2.roadl'
  data_files: parquet/vector-2.2/roadl.parquet
- config_name: 'vector-2.2.rstatp'
  data_files: parquet/vector-2.2/rstatp.parquet
- config_name: 'vector-2.1.airp'
  data_files: parquet/vector-2.1/airp.parquet
- config_name: 'vector-2.1.builtupa'
  data_files: parquet/vector-2.1/builtupa.parquet
- config_name: 'vector-2.1.builtupp'
  data_files: parquet/vector-2.1/builtupp.parquet
- config_name: 'vector-2.1.coastl'
  data_files: parquet/vector-2.1/coastl.parquet
- config_name: 'vector-2.1.ferryl'
  data_files: parquet/vector-2.1/ferryl.parquet
- config_name: 'vector-2.1.inwatera'
  data_files: parquet/vector-2.1/inwatera.parquet
- config_name: 'vector-2.1.miscl'
  data_files: parquet/vector-2.1/miscl.parquet
- config_name: 'vector-2.1.miscp'
  data_files: parquet/vector-2.1/miscp.parquet
- config_name: 'vector-2.1.polbnda'
  data_files: parquet/vector-2.1/polbnda.parquet
- config_name: 'vector-2.1.polbndl'
  data_files: parquet/vector-2.1/polbndl.parquet
- config_name: 'vector-2.1.portp'
  data_files: parquet/vector-2.1/portp.parquet
- config_name: 'vector-2.1.raill'
  data_files: parquet/vector-2.1/raill.parquet
- config_name: 'vector-2.1.riverl'
  data_files: parquet/vector-2.1/riverl.parquet
- config_name: 'vector-2.1.roadl'
  data_files: parquet/vector-2.1/roadl.parquet
- config_name: 'vector-2.1.rstatp'
  data_files: parquet/vector-2.1/rstatp.parquet
- config_name: 'vector-2.0.airp'
  data_files: parquet/vector-2.0/airp.parquet
- config_name: 'vector-2.0.builtupa'
  data_files: parquet/vector-2.0/builtupa.parquet
- config_name: 'vector-2.0.builtupp'
  data_files: parquet/vector-2.0/builtupp.parquet
- config_name: 'vector-2.0.coastl'
  data_files: parquet/vector-2.0/coastl.parquet
- config_name: 'vector-2.0.ferryl'
  data_files: parquet/vector-2.0/ferryl.parquet
- config_name: 'vector-2.0.inwatera'
  data_files: parquet/vector-2.0/inwatera.parquet
- config_name: 'vector-2.0.miscl'
  data_files: parquet/vector-2.0/miscl.parquet
- config_name: 'vector-2.0.miscp'
  data_files: parquet/vector-2.0/miscp.parquet
- config_name: 'vector-2.0.polbnda'
  data_files: parquet/vector-2.0/polbnda.parquet
- config_name: 'vector-2.0.polbndl'
  data_files: parquet/vector-2.0/polbndl.parquet
- config_name: 'vector-2.0.portp'
  data_files: parquet/vector-2.0/portp.parquet
- config_name: 'vector-2.0.raill'
  data_files: parquet/vector-2.0/raill.parquet
- config_name: 'vector-2.0.riverl'
  data_files: parquet/vector-2.0/riverl.parquet
- config_name: 'vector-2.0.roadl'
  data_files: parquet/vector-2.0/roadl.parquet
- config_name: 'vector-2.0.rstatp'
  data_files: parquet/vector-2.0/rstatp.parquet
---

# gsi-global-map-jp

Global Map Japan (地球地図日本): the 1:1,000,000 map of the whole of Japan
that the Geospatial Information Authority of Japan (GSI) made to the Global
Map Specifications of the International Steering Committee for Global
Mapping (ISCGM). Vector layers of administrative boundaries, drainage,
population centres and transportation, one GeoParquet subset per version and
layer, beside the zips GSI serves; and four rasters (elevation, land cover,
land use, vegetation) as GSI's zips only.

GSI Content Terms of Use, which apply the Public Data License 1.0 (PDL1.0),
compatible with CC BY 4.0 (see Licence). Credit GSI as shown there.

## Versions

GSI publishes every version from one page,
<https://www.gsi.go.jp/kankyochiri/gm_jpn.html>, and is the only primary
distributor of the Japanese edition: the Global Map data archives on GitHub
(<https://globalmaps.github.io/>) point back to it. Each version is a fixed
release, so each is kept here under its own name.

| version | published | what changed, in GSI's words | zips here |
|---|---|---|---|
| `vector-2.2` | 2016 | "地球地図第2.1版のうち、交通のうち道路・鉄道・鉄道駅を時点修正（2016年3月26日現在）" (roads, railways and stations of 2.1 brought up to 26 March 2016) | all layers, transportation |
| `vector-2.1` | 2015 | "地球地図第2版のうち、境界及び交通のうち空港のみを時点修正（2015年1月1日現在）" (boundaries and, of transportation, only airports of 2.0 brought up to 1 January 2015) | all layers, boundaries, transportation |
| `vector-2.0` | 2011 | the second edition | all layers, boundaries, drainage, population centres, transportation |
| `raster-1.1` | 2006 | | elevation, land cover, land use, vegetation |
| `raster-1.0` | 2000 | | elevation, land cover, land use, vegetation |

Every vector version's all-layers zip holds all 15 layers, including those
the version did not update. The theme zips of a version hold byte-identical
copies of the same files (checked by CRC), so the Parquet is made from the
all-layers zip. The page's table also gives a Global Map Specifications
version for each file (2.2 for the vectors, 1.2.1 for the rasters); that is
the specification, not the map version.

## Subsets and columns

One subset per vector version and layer, named `<version>.<layer>`, for
example `vector-2.2.coastl`, at `parquet/<version>/<layer>.parquet`. The
layer is the Shapefile's name without `_jpn`.

| theme | layer | geometry | f_code | 2.0 | 2.1 | 2.2 | attribute columns |
|---|---|---|---|---:|---:|---:|---|
| boundaries | `polbnda` administrative areas | Polygon | FA001 | 2,924 | 2,914 | 2,914 | `f_code`, `coc`, `nam`, `laa`, `pop`, `ypc`, `adm_code`, `salb`, `soc` |
| boundaries | `polbndl` administrative boundary lines | LineString | FA000 | 4,877 | 4,866 | 4,866 | `f_code`, `bst`, `use`, `soc` |
| boundaries | `coastl` coastline | LineString | BA010 | 1,201 | 1,204 | 1,204 | `f_code`, `acc`, `exs`, `soc` |
| drainage | `riverl` rivers | LineString | BH140 | 4,795 | 4,795 | 4,795 | `f_code`, `hyc`, `lit`, `nam`, `soc` |
| drainage | `inwatera` inland water | Polygon | BH000 | 825 | 825 | 825 | `f_code`, `hyc`, `hyt`, `nam`, `soc` |
| drainage | `miscl` | LineString | BI020 | 29 | 29 | 29 | `f_code`, `soc` |
| drainage | `miscp` | Point | BI020 | 271 | 271 | 271 | `f_code`, `soc` |
| population centres | `builtupa` built-up areas | Polygon | AL020 | 221 | 221 | 221 | `f_code`, `pop`, `ypc`, `nam`, `soc` |
| population centres | `builtupp` built-up places | Point | AL020 | 1,640 | 1,640 | 1,640 | `f_code`, `pop`, `ypc`, `nam`, `soc` |
| transportation | `roadl` roads | LineString | AP030 | 31,460 | 31,451 | 31,642 | `f_code`, `acc`, `exs`, `rst`, `med`, `rtt`, `RSU`, `loc`, `soc` |
| transportation | `raill` railways | LineString | AN010 | 3,377 | 3,377 | 3,420 | `f_code`, `exs`, `fco`, `loc`, `soc` |
| transportation | `rstatp` railway stations | Point | AQ125 | 89 | 89 | 108 | `f_code`, `nam`, `soc` |
| transportation | `airp` airports | Point | GB005 | 93 | 92 | 92 | `f_code`, `iko`, `ita`, `nam`, `use`, `zv3`, `soc` |
| transportation | `portp` ports | Point | AQ080 | 128 | 128 | 128 | `f_code`, `nam`, `soc` |
| transportation | `ferryl` ferry routes | LineString | AQ070 | 556 | 556 | 556 | `f_code`, `tuc`, `soc` |

The attribute names and codes are those of the Global Map Specifications
(<https://github.com/globalmaps/specifications>), which define each one;
`f_code` is the feature class, `soc` the country (`JPN` in every row), `nam`
the name, `laa` the municipality, `adm_code` the five-digit municipality code
(`01100` is Sapporo), `iko` and `ita` the ICAO and IATA codes, `pop` the
population and `ypc` its year.

The type of a column comes from its name, never from inference:

| columns | type |
|---|---|
| `fid` | BIGINT, added here: the record's position in the Shapefile, from 0; rows keep that order |
| `pop`, `ypc`, `acc`, `exs`, `rst`, `med`, `rtt`, `RSU`, `loc`, `use`, `zv3`, `hyc`, `hyt`, `lit`, `bst`, `tuc`, `fco` | INTEGER |
| everything else (`f_code`, `coc`, `nam`, `laa`, `adm_code`, `salb`, `soc`, `iko`, `ita`) | the text of the DBF; `adm_code` keeps its leading zeros |
| `geometry` | the Shapefile's geometry, in the CRS its `.prj` names (below) |

Column names are as in the DBF. `roadl` has an upper-case `RSU`; it clashes
with no other column, so it is kept as it is.

### Coordinate reference systems

Coordinates are longitude and latitude in degrees, never reprojected. Each
GeoParquet states the CRS that its Shapefile's `.prj` names; the `.prj` texts
are not all the same:

| `.prj` says | identified as | layers |
|---|---|---|
| `GEOGCS["GCS_ITRF_1994",DATUM["D_ITRF_1994",SPHEROID["GRS_1980",6378137.0,298.257222101]],...]` | EPSG:8994 (ITRF94) | every layer of 2.0; every layer of 2.1 and 2.2 except those below |
| `GEOGCS["GCS_JGD_2000",DATUM["D_JGD_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],...]` | EPSG:4612 (JGD2000) | `airp` of 2.1 and 2.2 |
| `GEOGCS["JGD2000",DATUM["D_JGD_2000",SPHEROID["GRS_1980",6378137,298.257222101]],...]` | EPSG:4612 (JGD2000) | `roadl` of 2.2 |

The metadata of 2.1 and 2.2 (`.met`, Global Map Metadata Profile XML) names
ITRF94 and GRS80 for every theme, transportation included. GSI's FAQ
(<https://www.gsi.go.jp/kankyochiri/gm_faq.html>) says that at the accuracy
and scale of Global Map the difference from WGS 84 is negligible ("地球地図データ
の精度や縮尺レベルの場合、WGS84座標系との差はほとんど無い"). So the change of
name in two layers is a change of label, not of datum in any sense that
matters at 1:1,000,000; but the files say what they say, and so do the
GeoParquet files. ITRF94 is identified by GDAL as EPSG:8994, a dynamic frame
with epoch 1993.0, which some tools handle less well than EPSG:4612 or
EPSG:4326.

```sql
-- DuckDB, straight off the Hub: the most populous municipalities of Hokkaido in 2.2
SELECT laa, adm_code, pop, ypc
FROM 'hf://datasets/yuiseki/gsi-global-map-jp/parquet/vector-2.2/polbnda.parquet'
WHERE nam = 'Hokkai Do' AND pop >= 0
ORDER BY pop DESC LIMIT 10;
```

```sql
-- three airports with their coordinates (the spatial extension reads the geometry)
INSTALL spatial; LOAD spatial;
SELECT nam, iko, ita, ST_X(geometry) AS lon, ST_Y(geometry) AS lat
FROM 'hf://datasets/yuiseki/gsi-global-map-jp/parquet/vector-2.2/airp.parquet'
WHERE ita IN ('HND', 'NRT', 'KIX');
```

```sql
-- roads by their rtt code in 2.0 and 2.2
SELECT '2.0' AS version, rtt, count(*) FROM 'hf://datasets/yuiseki/gsi-global-map-jp/parquet/vector-2.0/roadl.parquet' GROUP BY ALL
UNION ALL
SELECT '2.2', rtt, count(*) FROM 'hf://datasets/yuiseki/gsi-global-map-jp/parquet/vector-2.2/roadl.parquet' GROUP BY ALL
ORDER BY 2, 1;
```

### Rasters

The rasters are published only as GSI's zips, under `raw/raster-1.0/` and
`raw/raster-1.1/`: `gm-jpn-<el|lc|lu|ve>_u_<1_0|1_1>.zip`, each holding
`jpn/<kind>.tif`, a world file `.tfw`, an ArcGIS `.aux` and `Read_me.txt`.
The images are 8-bit with a colour map, 30 arc-seconds a pixel (0.00833333
degrees), the centre of the upper-left pixel at 120.004 E, 49.996 N. Those of 1.0 are PackBits
compressed TIFF without GeoTIFF keys, placed by the world file alone; those
of 1.1 are uncompressed GeoTIFF. The 1.1 elevation is 4,199 pixels wide, the
others 4,200; all are 3,600 high. GSI's page says there is no legend for
elevation ("標高については凡例はございません") and refers to the Global Map
Specifications for the others.

## Things to know

- All names are romanised; there is no Japanese text in any DBF. Prefectures
  and municipalities separate the kind of body (`Hokkai Do`, `Sapporo Shi`);
  points, built-up areas, airports, ports and stations are upper case
  (`SAPPORO`, `ABASHIRI PORT`).
- The DBFs carry no `.cpg`. Their language driver byte is 0x13 (code page
  932, Japanese) in most layers, and 0 (none) in `airp`, `coastl`,
  `polbnda`, `polbndl` and `roadl` of 2.1 and 2.2 and in `rstatp` of 2.2.
  Every byte of every DBF is ASCII, so the code page makes no difference.
- `pop` has two codes that are not counts: `-99999999` and `-89999999`. In
  `builtupa` and `builtupp` every row is `-99999999`, with `ypc` 0: no
  population is given for built-up areas in any version. In `polbnda` a
  municipality made of several polygons carries its population on one of
  them and `-89999999` on the others (1,159 rows in 2.2, 1,160 in 2.0);
  14 rows are `-99999999` with `ypc` 0: eight with `adm_code` `UNK` (in
  Tokyo and Aichi) and the six villages of the Northern Territories
  (`01695` to `01700`). Filter on
  `pop >= 0` before summing; in 2.2 that gives 128,438,348 for `ypc` 2014,
  in 2.0 127,767,994 for 2005.
- GSI replaced the all-layers zip of 2.2 in July 2023 without announcing
  it (Last-Modified 19 July 2023; only `polbnda_jpn.*` inside is dated
  2023-07-19). Its `polbnda` differs from that of 2.1 in five rows, all
  romanisation and attribution fixes, with identical geometry:

  | fid | `adm_code` | 2.1 (`nam` / `laa`) | 2.2 |
  |---:|---|---|---|
  | 52, 53, 54 | 01331 | Hokkai Do / Masaki Cho | Hokkai Do / Matsumae Cho |
  | 403 | 06024 | Akita Ken / Higashinaruse Mura | Yamagata Ken / Sakata Shi |
  | 2110 | 38401 | Ehime Ken / Matsumae Cho | Ehime Ken / Masaki Cho |

  The 2.1 zips (`gm-jpn-bnd_u_2_1.zip` and `gm-jpn-all_u_2_1.zip`) were not
  corrected, and neither was 2.0, so `vector-2.1.polbnda` and
  `vector-2.0.polbnda` still have the two Matsumae and Masaki swapped and
  06024 under Akita. The copy of the 2.2 zip from before July 2023 is not
  available.
- The transportation zip of 2.2 was also replaced, in May 2017: its
  `roadl_jpn.*` are dated 2017-04-28 and its `.prj` names JGD2000 where
  every other layer names ITRF94. The all-layers zip of 2.2 holds the same
  `roadl`. The earlier copy is not available either.
- One record of `vector-2.2.roadl` (fid 31615) and one of
  `vector-2.2.raill` (fid 2704) have an empty shape in the Shapefile; their
  `geometry` is NULL.
- `laa` of `polbnda` reads `" Ogasawara Mura"` with a leading space in the
  DBF of every version (fid 2916 in 2.0, 881 in 2.1 and 2.2). GDAL trims it,
  so the Parquet has `Ogasawara Mura`.
- `ferryl`, `miscl` and `riverl` of every version, `raill` of 2.0 and 2.1,
  and `coastl` and `polbndl` of 2.0 are PolyLineM Shapefiles. Their M values are
  all 0 or the Shapefile no-data value; they were dropped, since GeoParquet
  1.0 has no M.
- A theme zip holds a byte-identical subset of its version's all-layers
  zip, except that the 2.1 transportation zip adds a `Read_me.txt` the
  all-layers zip lacks. That `Read_me.txt` and the `.met` metadata of 2.1
  and 2.2 carry an old condition of use; see Licence.

## Checked before upload

`scripts/02_verify.py` in the source repository checks, with DuckDB, every
vector layer of every version against the Shapefiles in GSI's zip, read with
a small reader of its own rather than GDAL:

- the zips have the sha256 in their `MANIFEST.json`, and every theme zip
  holds byte-identical copies (CRC) of the all-layers zip's layer files
- the row count equals the DBF header and the `.shp` records, and the pinned
  count in the table above
- every attribute value of every record equals the DBF text (trimmed;
  integers parsed), 1,176,455 values in all
- every geometry has the x and y of its `.shp` record, coordinate by
  coordinate, in order (2,999,080 points in all); empty shapes are the NULL
  geometries; the M values dropped were only 0 or no-data
- every column has the type the rule gives its name
- the GeoParquet 1.0.0 metadata states the CRS the layer's `.prj` names
- a DuckDB without the spatial extension opens every file
- no row group carries a bloom filter
- `polbnda` of 2.2 differs from that of 2.1 in exactly the five rows above,
  with all 2,914 geometries identical

## Licence

GSI's page for Global Map Japan
(<https://www.gsi.go.jp/kankyochiri/gm_jpn.html>):

> 本データには、「国土地理院コンテンツ利用規約」が適用されます。

(The GSI Content Terms of Use apply to this data.)

GSI Content Terms of Use
(<https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html>, as amended on
20 November 2025, read on 2026-10-03):

> 本サイトのコンテンツには特段の記載が無い限り公共データ利用規約（第1.0 版）（PDL1.0）が適用されています。

(Unless stated otherwise, the Public Data License version 1.0 (PDL1.0)
applies to the content of this site.)

> ア　コンテンツを利用する際は、出典を記載してください。出典の記載方法は以下の例を参考にしてください。
> （出典記載例）
> 出典：国土地理院ウェブサイト　（当該ページのURL）

> イ　コンテンツを編集・加工等して利用する場合は、上記出典とは別に、編集・加工等を行ったことを記載してください。（略）なお、編集・加工した情報を、あたかも国土地理院が作成したかのような態様で公表・利用してはいけません。

(Credit the source, for example "出典：国土地理院ウェブサイト" with the URL of
the page. When you edit or process the content, say so separately from the
credit, and do not present the edited information as if GSI had made it.)

GSI's Global Map FAQ (<https://www.gsi.go.jp/kankyochiri/gm_faq.html>, read
on 2026-10-03):

> 地球地図日本の場合、商用・非商用に関わらず、出典の記載をお願いしています。

(For Global Map Japan, credit the source whether the use is commercial or
not.) Its example credit is `Global Map Japan` and
`© Geospatial Information Authority of Japan`.

PDL1.0 is compatible with CC BY 4.0, which is why the card says
`cc-by-4.0`: reuse, commercial use and redistribution are allowed with
credit. The terms that apply are GSI's, quoted above. Credit, for example:

    出典：国土地理院ウェブサイト（https://www.gsi.go.jp/kankyochiri/gm_jpn.html）
    Global Map Japan, © Geospatial Information Authority of Japan
    GeoParquet converted from GSI's Shapefiles by yuiseki/gsi-global-map-jp

The `Read_me.txt` in the 2.0 and raster zips says the same: "The data is
available at no charge, regardless of the non-profit objectives and
commercial use, under the "Geospatial Information Authority of Japan Website
Terms of Use"".

The `.met` metadata in the 2.1 and 2.2 zips (dated 2015 and 2016) still
carries an older condition, in `otherConstraints`, and the `Read_me.txt` of
the 2.1 transportation zip carries the same words:

> Global Map Japan is subject to copyright law of Japan and copyright
> protection by an international treaty. Application procedure is required
> in using the product, except for non-commercial purpose and use in small
> quantity. Acknowledgement of written sources and report of utilization in
> an appropriate manner is necessary in using the product. (In case of use in
> small quantity, acknowledgement of written sources is necessary, but report
> of utilization is not required.)

That condition is outdated. The current terms are those of GSI's page, its
FAQ and the Content Terms of Use quoted above (no application, commercial use
allowed, credit required). The `.met` and `Read_me.txt` files are left inside
GSI's zips as they are.

The zips under `raw/` are GSI's, byte for byte. The Parquet is made from
them; what was changed is listed in `LICENSE` beside this file. GSI did not
make the Parquet and has not reviewed it.

## Citation

Geospatial Information Authority of Japan. Global Map Japan (地球地図日本),
vector versions 2.0 (2011), 2.1 (2015) and 2.2 (2016), raster versions 1.0
(2000) and 1.1 (2006). GSI Technical Reports D1-No.576 (vector, second
edition), D1-No.459 (version 1.0) and D1-No.464 (version 1.1).
https://www.gsi.go.jp/kankyochiri/gm_jpn.html
