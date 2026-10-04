#!/usr/bin/env python3
"""Turn every layer of every vector version into a GeoParquet, for the Hub viewer and DuckDB.

Each vector version (2.0, 2.1, 2.2) has an all-layers zip holding the 15
Shapefiles of the four themes; the theme zips of the same version hold
byte-identical copies (02_verify.py checks this by CRC), so the all-layers zip
is the one read. It is extracted to data/work/<version>/, each <layer>_jpn.shp
is read with DuckDB's spatial extension (ST_Read, which uses GDAL), and
written to data/parquet/<version>/<layer>.parquet. The extracted files are
deleted afterwards. The rasters (versions 1.0 and 1.1) are published as the
zips GSI serves and are not converted.

Types come from the column's name, never from inference (GDAL's reading of
the DBF header is cast back to text first): the Global Map attribute codes
and the counts (pop, ypc, acc, exs, rst, med, rtt, rsu, loc, use, zv3, hyc,
hyt, lit, bst, tuc, fco) are INTEGER; everything else, including adm_code
with its leading zeros, stays text. A value that does not fit stops the run
instead of being rounded or nulled. Column names are kept as in the DBF
(roadl has an upper-case RSU); fid, the record's position in the Shapefile
from 0, is added, and rows keep that order.

The geometry is the Shapefile's own, in the CRS its .prj names, never
reprojected. The .prj texts in these zips name either ITRF94
(GCS_ITRF_1994, EPSG:8994) or JGD2000 (GCS_JGD_2000 and JGD2000, both
EPSG:4612); crs_from_prj holds that table, and a .prj it does not know, or
one GDAL identifies otherwise, stops the run. M values (the PolyLineM
layers carry only 0 or the Shapefile no-data value) are dropped, because
GeoParquet 1.0 has no M; 02_verify.py checks there was nothing else in them.

    uv run python scripts/03_export_parquet.py
"""

import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "parquet"
WORK = ROOT / "data" / "work"

# the all-layers zip of each vector version
VERSIONS = {
    "vector-2.0": "gm-jpn-all_u_2.zip",
    "vector-2.1": "gm-jpn-all_u_2_1.zip",
    "vector-2.2": "gm-jpn-all_u_2_2.zip",
}
LAYERS = (
    "airp", "builtupa", "builtupp", "coastl", "ferryl", "inwatera", "miscl", "miscp",
    "polbnda", "polbndl", "portp", "raill", "riverl", "roadl", "rstatp",
)  # fmt: skip

INTEGERS = {
    "pop", "ypc", "acc", "exs", "rst", "med", "rtt", "rsu", "loc", "use", "zv3",
    "hyc", "hyt", "lit", "bst", "tuc", "fco",
}  # fmt: skip

# the GEOGCS name in the .prj -> the CRS the GeoParquet states
PRJ_CRS = {
    "GCS_ITRF_1994": "EPSG:8994",
    "GCS_JGD_2000": "EPSG:4612",
    "JGD2000": "EPSG:4612",
}


def column_type(name: str) -> str:
    return "INTEGER" if name.lower() in INTEGERS else "VARCHAR"


def crs_from_prj(text: str) -> str:
    mt = re.match(r'\s*GEOGCS\["([^"]+)"', text)
    if not mt or mt.group(1) not in PRJ_CRS:
        raise ValueError(f"no rule for the .prj {text[:80]!r}")
    return PRJ_CRS[mt.group(1)]


def _expr(label: str, name: str) -> str:
    c = f'cast("{name}" as varchar)'
    if column_type(name) == "VARCHAR":
        return f'{c} as "{name}"'
    return (
        f"case when {c} is null then null "
        f"when regexp_full_match({c}, '-?[0-9]{{1,9}}') then cast({c} as integer) "
        f"else error('{label}: {name} is not an integer: ' || {c}) end as \"{name}\""
    )


def select_sql(src: str, names: list[str], label: str) -> str:
    """src gives OGC_FID, the attribute columns and geom, as ST_Read does."""
    cols = ['cast("OGC_FID" as bigint) as fid']
    cols += [_expr(label, n) for n in names]
    cols.append("st_force2d(geom) as geometry")
    return f"select {', '.join(cols)} from {src}"


def export_layer(con, shp: Path, out: Path) -> int:
    want = crs_from_prj(shp.with_suffix(".prj").read_text(encoding="ascii"))
    src = f"st_read('{shp}')"
    types = dict(con.sql(f"select column_name, column_type from (describe select * from {src})").fetchall())
    got = types.pop("geom")
    if got != f"GEOMETRY('{want}')":
        raise ValueError(f"{shp.name}: GDAL reads the .prj as {got}, the rule says {want}")
    names = [n for n in types if n != "OGC_FID"]
    out.parent.mkdir(parents=True, exist_ok=True)
    con.execute(
        f"copy ({select_sql(src, names, shp.name)} order by fid) to '{out}' "
        "(format parquet, compression zstd, write_bloom_filter false)"
    )
    n = con.sql(f"select count(*) from '{out}'").fetchone()[0]
    expected = con.sql(f"select count(*) from {src}").fetchone()[0]
    if n != expected:
        raise SystemExit(f"{shp.name}: {n} rows written, ST_Read gives {expected}")
    return n


def main() -> int:
    import duckdb

    con = duckdb.connect()
    con.execute("set memory_limit = '8GB'; install spatial; load spatial")
    for version, zname in VERSIONS.items():
        work = WORK / version
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        with zipfile.ZipFile(RAW / version / zname) as z:
            z.extractall(work)  # CRC checked by zipfile on read
        shps = {p.stem.removesuffix("_jpn"): p for p in work.rglob("*_jpn.shp")}
        if sorted(shps) != sorted(LAYERS):
            raise SystemExit(f"{version}: layers {sorted(shps)}, expected {sorted(LAYERS)}")
        for layer in LAYERS:
            p = OUT / version / f"{layer}.parquet"
            n = export_layer(con, shps[layer], p)
            print(f"{version}.{layer}: {n:,} rows, {p.stat().st_size:,} bytes", flush=True)
        shutil.rmtree(work)
    if WORK.exists() and not any(WORK.iterdir()):
        WORK.rmdir()
    return 0


if __name__ == "__main__":
    sys.exit(main())
