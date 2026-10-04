import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "verify", Path(__file__).parents[1] / "scripts" / "02_verify.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def _run(d):
    results = []
    m.verify_dir(d, lambda ok, what: results.append((ok, what)))
    return results


def _write_manifest(d, *names):
    entries = {}
    for n in names:
        b = (d / n).read_bytes()
        entries[n] = {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
    (d / "MANIFEST.json").write_text(json.dumps(entries))


def test_a_good_zip_passes_and_its_csv_is_counted(tmp_path):
    with zipfile.ZipFile(tmp_path / "a.zip", "w") as z:
        z.writestr("t.csv", "x,y\n1,2\n3,4\n")
        z.writestr("t.shp", b"\0" * 10)
    _write_manifest(tmp_path, "a.zip")
    results = _run(tmp_path)
    assert all(ok for ok, _ in results)
    assert any("t.csv: 2 rows" in w for _, w in results)


def test_a_changed_file_fails(tmp_path):
    with zipfile.ZipFile(tmp_path / "a.zip", "w") as z:
        z.writestr("t.txt", "hello")
    _write_manifest(tmp_path, "a.zip")
    with open(tmp_path / "a.zip", "ab") as f:
        f.write(b"x")
    assert not all(ok for ok, _ in _run(tmp_path))


def test_a_file_outside_the_manifest_fails(tmp_path):
    (tmp_path / "a.csv").write_text("x\n1\n")
    _write_manifest(tmp_path)
    assert not all(ok for ok, _ in _run(tmp_path))


def test_a_broken_zip_fails(tmp_path):
    (tmp_path / "a.zip").write_bytes(b"PK not really")
    _write_manifest(tmp_path, "a.zip")
    assert not all(ok for ok, _ in _run(tmp_path))


def _shapefile(tmp_path, geom_sql):
    import duckdb

    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    shp = tmp_path / "t_jpn.shp"
    con.execute(
        f"copy (select 'Sapporo Shi' as laa, 1880863 as pop, {geom_sql} as geom) to '{shp}' "
        "(format gdal, driver 'ESRI Shapefile', srs 'EPSG:4612')"
    )
    return shp


def test_the_dbf_reader_gives_the_raw_text(tmp_path):
    shp = _shapefile(tmp_path, "st_point(141.35, 43.06)")
    fields, rows, _ = m.read_dbf(shp.with_suffix(".dbf").read_bytes())
    assert [f for f, _ in fields] == ["laa", "pop"]
    assert [t for _, t in fields] == ["C", "N"]
    assert [m.raw_value(v, t) for v, (_, t) in zip(rows[0], fields, strict=True)] == [
        "Sapporo Shi",
        1880863,
    ]


def test_raw_value_trims_as_gdal_does():
    assert m.raw_value(" Ogasawara Mura   ", "C") == "Ogasawara Mura"
    assert m.raw_value("   -99999999", "N") == -99999999
    assert m.raw_value("     ", "N") is None


def test_the_shp_reader_and_the_wkb_reader_agree(tmp_path):
    import duckdb

    shp = _shapefile(tmp_path, "st_geomfromtext('POLYGON ((140 36, 141 36, 141 37, 140 36))')")
    (xy, ms), = m.read_shp(shp.read_bytes())
    assert ms == []
    con = duckdb.connect()
    con.execute("load spatial")
    wkb = con.sql(f"select st_aswkb(geom) from st_read('{shp}')").fetchone()[0]
    assert m.wkb_xy(bytes(wkb)) == xy
    assert len(xy) == 4 and set(xy) == {(140.0, 36.0), (141.0, 36.0), (141.0, 37.0)}
