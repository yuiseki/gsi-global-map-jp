#!/usr/bin/env python3
"""Check every fetched file against data/raw/<version>/MANIFEST.json.

For each version directory:
  - every file in the manifest exists, has the bytes and sha256 recorded
  - no file in the directory is missing from the manifest
  - every zip passes zipfile.testzip
  - every gzip reads to the end
  - every CSV (loose, or a member of a zip) is counted with the csv module

For each vector version, its Parquet against the Shapefiles in the zips:
  - every theme zip holds byte-identical copies (CRC) of the all-layers zip's
    members, so converting the all-layers zip covers them
  - every layer has a Parquet, with as many rows as the DBF header and the
    .shp records say
  - every attribute value of every record equals the text of the DBF, read
    here with a small reader of its own (not GDAL): text trimmed, integers
    parsed; every DBF byte is ASCII, so the code page does not matter. GDAL
    trims leading spaces as well as trailing ones; the values that had one
    are listed and pinned (one, in polbnda)
  - every geometry has the x and y of its .shp record, coordinate by
    coordinate, read here with a small reader of its own; empty records are
    the rows without a geometry; the M values dropped were only 0 or the
    Shapefile no-data value
  - every column has the type column_type gives its name
  - the GeoParquet metadata states the CRS the layer's .prj names
  - a plain DuckDB without the spatial extension opens every file
  - no row group carries a bloom filter
  - the boundary polygons of 2.2 differ from those of 2.1 only in the rows
    GSI corrected in 2023 (printed), with the same geometry

Prints one ok/FAIL line per check and exits 1 if any failed.

    uv run python scripts/02_verify.py
"""

import csv
import gzip
import hashlib
import importlib.util
import io
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PQ = ROOT / "data" / "parquet"
EXPECTED_ROWS = {
    "vector-2.0": {
        "airp": 93, "builtupa": 221, "builtupp": 1640, "coastl": 1201, "ferryl": 556,
        "inwatera": 825, "miscl": 29, "miscp": 271, "polbnda": 2924, "polbndl": 4877,
        "portp": 128, "raill": 3377, "riverl": 4795, "roadl": 31460, "rstatp": 89,
    },
    "vector-2.1": {
        "airp": 92, "builtupa": 221, "builtupp": 1640, "coastl": 1204, "ferryl": 556,
        "inwatera": 825, "miscl": 29, "miscp": 271, "polbnda": 2914, "polbndl": 4866,
        "portp": 128, "raill": 3377, "riverl": 4795, "roadl": 31451, "rstatp": 89,
    },
    "vector-2.2": {
        "airp": 92, "builtupa": 221, "builtupp": 1640, "coastl": 1204, "ferryl": 556,
        "inwatera": 825, "miscl": 29, "miscp": 271, "polbnda": 2914, "polbndl": 4866,
        "portp": 128, "raill": 3420, "riverl": 4795, "roadl": 31642, "rstatp": 108,
    },
}  # fmt: skip
# text values that start with a space in every version (GDAL trims them)
LEADING_SPACES = {"polbnda": 1}
# Shapefile M values below this are "no data" (the specification's -10^38)
M_NO_DATA = -1e38


def _export():
    spec = importlib.util.spec_from_file_location("export", ROOT / "scripts" / "03_export_parquet.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def csv_rows(f) -> int:
    """Data rows of a CSV given as a binary file, header excluded."""
    text = io.TextIOWrapper(f, encoding="utf-8-sig", errors="replace", newline="")
    return max(sum(1 for _ in csv.reader(text)) - 1, 0)


def check_zip(path: Path) -> tuple[bool, str]:
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad:
                return False, f"bad member {bad}"
            names = z.namelist()
            notes = [f"{len(names)} members"]
            for n in names:
                if n.lower().endswith(".csv"):
                    with z.open(n) as f:
                        notes.append(f"{n}: {csv_rows(f):,} rows")
            return True, ", ".join(notes)
    except zipfile.BadZipFile as e:
        return False, str(e)


def check_gzip(path: Path) -> tuple[bool, str]:
    try:
        n = 0
        with gzip.open(path) as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                n += len(block)
        return True, f"{n:,} bytes uncompressed"
    except (OSError, EOFError) as e:
        return False, str(e)


def verify_dir(d: Path, check) -> None:
    mpath = d / "MANIFEST.json"
    if not mpath.exists():
        check(False, f"{d.name}: MANIFEST.json missing")
        return
    manifest = json.loads(mpath.read_text())
    extra = sorted(
        p.name for p in d.iterdir() if p.is_file() and p.name != "MANIFEST.json"
        and p.name not in manifest
    )  # fmt: skip
    check(not extra, f"{d.name}: no files outside the manifest {extra or ''}".rstrip())
    for name, m in sorted(manifest.items()):
        p = d / name
        if not p.exists():
            check(False, f"{d.name}/{name}: missing")
            continue
        size = p.stat().st_size
        check(size == m["bytes"], f"{d.name}/{name}: {size:,} bytes")
        check(sha256(p) == m["sha256"], f"{d.name}/{name}: sha256 matches")
        low = name.lower()
        if low.endswith(".zip"):
            ok, note = check_zip(p)
            check(ok, f"{d.name}/{name}: zip test ({note})")
        elif low.endswith(".gz"):
            ok, note = check_gzip(p)
            check(ok, f"{d.name}/{name}: gzip reads ({note})")
        elif low.endswith(".csv"):
            with open(p, "rb") as f:
                check(True, f"{d.name}/{name}: {csv_rows(f):,} rows")


def read_dbf(b: bytes) -> tuple[list[tuple[str, str]], list[list[str]], int]:
    """Fields (name, type), records as raw text, and the language driver byte."""
    n, header_len, rec_len = struct.unpack("<IHH", b[4:12])
    fields, i = [], 32
    while b[i] != 0x0D:
        fields.append((b[i : i + 11].split(b"\0")[0].decode("ascii"), chr(b[i + 11]), b[i + 16]))
        i += 32
    rows = []
    for r in range(n):
        rec = b[header_len + r * rec_len : header_len + (r + 1) * rec_len]
        if rec[:1] != b" ":
            raise ValueError(f"record {r} is marked deleted")
        p, row = 1, []
        for _, _, width in fields:
            row.append(rec[p : p + width].decode("ascii"))  # fails on any non-ASCII byte
            p += width
        rows.append(row)
    return [(f, t) for f, t, _ in fields], rows, b[29]


def read_shp(b: bytes) -> list[tuple[list[tuple[float, float]], list[float]]]:
    """Each record's x, y in file order (parts in order) and its M values."""
    out, p = [], 100
    while p < len(b):
        length = struct.unpack(">i", b[p + 4 : p + 8])[0] * 2
        rec = b[p + 8 : p + 8 + length]
        p += 8 + length
        kind = struct.unpack("<i", rec[:4])[0]
        if kind == 0:
            out.append(([], []))
        elif kind == 1:
            out.append(([struct.unpack("<2d", rec[4:20])], []))
        elif kind in (3, 5, 23):
            parts, points = struct.unpack("<2i", rec[36:44])
            q = 44 + 4 * parts
            xy = [struct.unpack("<2d", rec[q + 16 * k : q + 16 * k + 16]) for k in range(points)]
            ms = []
            if kind == 23:
                q += 16 * points + 16
                ms = list(struct.unpack(f"<{points}d", rec[q : q + 8 * points]))
            out.append((xy, ms))
        else:
            raise ValueError(f"shape type {kind} not handled")
    return out


def wkb_xy(b: bytes | None) -> list[tuple[float, float]]:
    """The x, y of a 2D WKB geometry, in order."""
    if b is None:
        return []
    out: list[tuple[float, float]] = []

    def geom(p: int) -> int:
        bo = "<" if b[p] == 1 else ">"
        kind = struct.unpack(bo + "I", b[p + 1 : p + 5])[0]
        p += 5
        if kind == 1:
            out.append(struct.unpack(bo + "2d", b[p : p + 16]))
            return p + 16
        if kind == 2:
            return ring(bo, p)
        if kind == 3:
            (n,) = struct.unpack(bo + "I", b[p : p + 4])
            p += 4
            for _ in range(n):
                p = ring(bo, p)
            return p
        if kind in (4, 5, 6):
            (n,) = struct.unpack(bo + "I", b[p : p + 4])
            p += 4
            for _ in range(n):
                p = geom(p)
            return p
        raise ValueError(f"WKB type {kind} not handled")

    def ring(bo: str, p: int) -> int:
        (n,) = struct.unpack(bo + "I", b[p : p + 4])
        p += 4
        out.extend(struct.unpack(bo + "2d", b[p + 16 * k : p + 16 * k + 16]) for k in range(n))
        return p + 16 * n

    geom(0)
    return out


def raw_value(text: str, kind: str):
    """The DBF text as GDAL gives it: trimmed on both sides, integers parsed."""
    s = text.strip(" ")
    if kind == "N":
        return int(s) if s else None
    return s


def verify_vector(version: str, check, con) -> None:
    import duckdb

    export = _export()
    d = RAW / version
    zname = export.VERSIONS[version]
    allz = zipfile.ZipFile(d / zname)
    members = {Path(i.filename).name: i for i in allz.infolist() if not i.is_dir()}
    for other in sorted(d.glob("*.zip")):
        if other.name == zname:
            continue
        with zipfile.ZipFile(other) as z:
            diff = [
                i.filename for i in z.infolist()
                if not i.is_dir() and Path(i.filename).suffix in (".shp", ".shx", ".dbf", ".prj", ".met")
                and (Path(i.filename).name not in members or members[Path(i.filename).name].CRC != i.CRC)
            ]  # fmt: skip
        check(not diff, f"{version}: {other.name} holds the same layer files as {zname} {diff or ''}".rstrip())

    for layer in export.LAYERS:
        label = f"{version}.{layer}"
        p = PQ / version / f"{layer}.parquet"
        if not p.exists():
            check(False, f"{label}: {p.relative_to(ROOT)} missing")
            continue
        fields, rows, _ = read_dbf(allz.read(members[f"{layer}_jpn.dbf"]))
        shapes = read_shp(allz.read(members[f"{layer}_jpn.shp"]))
        prj = allz.read(members[f"{layer}_jpn.prj"]).decode("ascii")
        n = con.sql(f"select count(*) from '{p}'").fetchone()[0]
        check(
            n == len(rows) == len(shapes) == EXPECTED_ROWS[version][layer],
            f"{label}: {n:,} rows (DBF {len(rows):,}, .shp {len(shapes):,})",
        )

        names = [f for f, _ in fields]
        quoted = ", ".join(f'"{c}"' for c in names)
        got = con.sql(
            f"select fid, {quoted}, st_aswkb(geometry) "
            f"from '{p}' order by fid"
        ).fetchall()
        fid_ok = [r[0] for r in got] == list(range(len(rows)))
        bad_values = sum(
            1 for want, have in zip(rows, got, strict=False)
            for (_, kind), w, h in zip(fields, want, have[1:-1], strict=True)
            if raw_value(w, kind) != h
        )  # fmt: skip
        check(fid_ok and bad_values == 0,
              f"{label}: every attribute value equals the DBF ({len(rows) * len(names):,} values)")  # fmt: skip
        leading = [
            (i, f, w) for i, row in enumerate(rows) for (f, kind), w in zip(fields, row, strict=True)
            if kind == "C" and w.startswith(" ") and w.strip()
        ]  # fmt: skip
        check(len(leading) == LEADING_SPACES.get(layer, 0),
              f"{label}: text with a leading space, which GDAL trims: {leading or 'none'}")  # fmt: skip
        bad_geom = sum(
            1 for (xy, _), have in zip(shapes, got, strict=False)
            if xy != wkb_xy(bytes(have[-1]) if have[-1] is not None else None)
        )
        empty = sum(1 for xy, _ in shapes if not xy)
        npts = sum(len(xy) for xy, _ in shapes)
        check(bad_geom == 0,
              f"{label}: every geometry has the .shp coordinates ({npts:,} points, {empty} empty)")  # fmt: skip
        ms = {m if m > M_NO_DATA else "no data" for _, mm in shapes for m in mm}
        check(ms <= {0.0, "no data"}, f"{label}: M values dropped were {sorted(map(str, ms)) or 'none'}")

        types = dict(
            con.sql(f"select column_name, column_type from (describe select * from '{p}')").fetchall()
        )
        geometry_type = types.pop("geometry")
        wrong = {c: t for c, t in types.items()
                 if t != ("BIGINT" if c == "fid" else export.column_type(c))}  # fmt: skip
        check(not wrong and list(types) == ["fid", *names],
              f"{label}: every column has its type ({wrong or 'all as named'})")  # fmt: skip

        want_crs = export.crs_from_prj(prj)
        geo = json.loads(con.sql(
            f"select decode(value) from parquet_kv_metadata('{p}') where decode(key) = 'geo'"
        ).fetchone()[0])  # fmt: skip
        g = geo["columns"]["geometry"]
        crs_id = "{authority}:{code}".format(**g["crs"]["id"])
        check(crs_id == want_crs and want_crs in geometry_type,
              f"{label}: GeoParquet {geo['version']}, {g['geometry_types']}, CRS {crs_id} as the .prj says")  # fmt: skip

        plain = duckdb.connect()
        pn = plain.sql(f"select count(*) from '{p}'").fetchone()[0]
        check(pn == n, f"{label}: a DuckDB without spatial opens it")
        bloom = con.sql(
            f"select count(*) filter (where bloom_filter_offset is not null) from parquet_metadata('{p}')"
        ).fetchone()[0]
        check(bloom == 0, f"{label}: no bloom filters")


def verify_2023_fix(check, con) -> None:
    """The 2.2 boundary polygons were replaced in 2023; 2.1 was not."""
    a, b = (PQ / v / "polbnda.parquet" for v in ("vector-2.1", "vector-2.2"))
    if not (a.exists() and b.exists()):
        return
    diff = con.sql(
        f"select o.fid, o.nam, o.laa, n.nam, n.laa, o.adm_code from '{a}' o join '{b}' n using (fid) "
        "where (o.nam, o.laa, o.adm_code, o.pop, o.ypc) is distinct from (n.nam, n.laa, n.adm_code, n.pop, n.ypc) "
        "order by o.fid"
    ).fetchall()
    same_geom = con.sql(
        f"select count(*) from '{a}' o join '{b}' n using (fid) where st_equals(o.geometry, n.geometry) "
        "and st_astext(o.geometry) = st_astext(n.geometry)"
    ).fetchone()[0]
    for fid, onam, olaa, nnam, nlaa, code in diff:
        print(f"      fid {fid} ({code}): {onam} / {olaa}  ->  {nnam} / {nlaa}")
    check(len(diff) == 5 and same_geom == 2914,
          f"polbnda 2.1 -> 2.2: {len(diff)} rows of attributes differ, {same_geom:,} geometries identical")  # fmt: skip


def main() -> int:
    failures = []

    def check(ok: bool, what: str) -> None:
        print(("ok    " if ok else "FAIL  ") + what)
        if not ok:
            failures.append(what)

    dirs = sorted(p for p in RAW.iterdir() if p.is_dir()) if RAW.exists() else []
    check(bool(dirs), f"{len(dirs)} version directories under data/raw")
    for d in dirs:
        verify_dir(d, check)
    if PQ.exists():
        import duckdb

        con = duckdb.connect()
        con.execute("set memory_limit = '8GB'; install spatial; load spatial")
        for version in EXPECTED_ROWS:
            verify_vector(version, check, con)
        verify_2023_fix(check, con)
    if failures:
        print(f"\n{len(failures)} checks failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
