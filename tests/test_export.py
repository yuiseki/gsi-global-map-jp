import importlib.util
import json
from pathlib import Path

import duckdb
import pytest

_spec = importlib.util.spec_from_file_location(
    "export", Path(__file__).parents[1] / "scripts" / "03_export_parquet.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

ITRF94_PRJ = (
    'GEOGCS["GCS_ITRF_1994",DATUM["D_ITRF_1994",SPHEROID["GRS_1980",6378137.0,'
    '298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
)
JGD2000_PRJ_AIRP = (
    'GEOGCS["GCS_JGD_2000",DATUM["D_JGD_2000",SPHEROID["GRS_1980",6378137.0,'
    '298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]]'
)
JGD2000_PRJ_ROADL = (
    'GEOGCS["JGD2000",DATUM["D_JGD_2000",SPHEROID["GRS_1980",6378137,298.257222101]],'
    'PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]]'
)


@pytest.mark.parametrize(
    ("name", "sql"),
    [
        ("pop", "INTEGER"),
        ("ypc", "INTEGER"),
        ("exs", "INTEGER"),
        ("RSU", "INTEGER"),
        ("rsu", "INTEGER"),
        ("zv3", "INTEGER"),
        ("f_code", "VARCHAR"),
        ("adm_code", "VARCHAR"),
        ("nam", "VARCHAR"),
        ("soc", "VARCHAR"),
        ("iko", "VARCHAR"),
        ("a_column_no_version_has", "VARCHAR"),
    ],
)
def test_column_type(name, sql):
    assert m.column_type(name) == sql


@pytest.mark.parametrize(
    ("prj", "crs"),
    [(ITRF94_PRJ, "EPSG:8994"), (JGD2000_PRJ_AIRP, "EPSG:4612"), (JGD2000_PRJ_ROADL, "EPSG:4612")],
)
def test_crs_from_prj(prj, crs):
    assert m.crs_from_prj(prj) == crs


def test_an_unknown_prj_stops_the_run():
    with pytest.raises(ValueError, match="no rule for the .prj"):
        m.crs_from_prj('GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984"]]')


def _rel(rows):
    """A relation of text columns, as ST_Read would give after the cast to text."""
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    names = ["OGC_FID", "f_code", "adm_code", "pop", "RSU"]
    values = ", ".join(
        "(" + ", ".join("null" if v is None else f"'{v}'" for v in r) + ", st_point(140, 36))"
        for r in rows
    )
    src = f"(select * from (values {values}) t({', '.join(names)}, geom))"
    return con.sql(m.select_sql(src, names[1:], "t.shp"))


def test_values_are_typed_and_text_stays_text():
    rel = _rel([("0", "FA001", "01100", "1880863", "-99999999")])
    row = dict(zip(rel.columns, rel.fetchone(), strict=True))
    assert row["fid"] == 0
    assert row["adm_code"] == "01100" and row["f_code"] == "FA001"
    assert row["pop"] == 1880863 and row["RSU"] == -99999999
    assert [c for c in rel.columns] == ["fid", "f_code", "adm_code", "pop", "RSU", "geometry"]


def test_a_null_stays_null():
    rel = _rel([("0", "FA001", None, None, "1")])
    assert rel.select("adm_code, pop").fetchone() == (None, None)


@pytest.mark.parametrize(
    ("row", "message"),
    [
        (("0", "FA001", "01100", "12a", "1"), "t.shp: pop is not an integer: 12a"),
        (("0", "FA001", "01100", "1.5", "1"), "t.shp: pop is not an integer: 1.5"),
        (("0", "FA001", "01100", "", "1"), "t.shp: pop is not an integer: "),
        (("0", "FA001", "01100", "1", "***"), r"t.shp: RSU is not an integer: \*\*\*"),
        (("0", "FA001", "01100", "99999999999", "1"), "t.shp: pop is not an integer: 99999999999"),
    ],
)
def test_a_value_that_does_not_fit_stops_the_run(row, message):
    with pytest.raises(duckdb.Error, match=message):
        _rel([row]).fetchall()


def _shapefile(tmp_path, srs, geom_sql):
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    d = tmp_path / "src"
    d.mkdir()
    shp = d / "t_jpn.shp"
    con.execute(
        f"copy (select 'AP030' as f_code, 1880863 as pop, {geom_sql} as geom) to '{shp}' "
        f"(format gdal, driver 'ESRI Shapefile', srs '{srs}')"
    )
    return shp


def test_a_layer_keeps_its_crs_and_is_written_as_geoparquet(tmp_path):
    shp = _shapefile(tmp_path, "EPSG:4612", "st_geomfromtext('LINESTRING (140 36, 141 37)')")
    shp.with_suffix(".prj").write_text(JGD2000_PRJ_ROADL)
    out = tmp_path / "t.parquet"
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    n = m.export_layer(con, shp, out)
    assert n == 1
    geo = json.loads(
        con.sql(
            f"select decode(value) from parquet_kv_metadata('{out}') where decode(key) = 'geo'"
        ).fetchone()[0]
    )
    g = geo["columns"]["geometry"]
    assert g["geometry_types"] == ["LineString"]
    assert g["crs"]["id"] == {"authority": "EPSG", "code": 4612}
    row = con.sql(f"select fid, f_code, pop, st_astext(geometry) from '{out}'").fetchone()
    assert row == (0, "AP030", 1880863, "LINESTRING (140 36, 141 37)")


def test_a_layer_with_an_unknown_prj_stops_the_run(tmp_path):
    shp = _shapefile(tmp_path, "EPSG:4612", "st_point(140, 36)")
    shp.with_suffix(".prj").write_text(ITRF94_PRJ.replace("1994", "1997"))
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    with pytest.raises(ValueError, match="no rule for the .prj"):
        m.export_layer(con, shp, tmp_path / "t.parquet")


def test_m_values_are_dropped_and_x_y_kept(tmp_path):
    shp = _shapefile(
        tmp_path, "EPSG:8994", "st_geomfromtext('LINESTRING M (140.5 36.25 0, 141 37 0)')"
    )
    shp.with_suffix(".prj").write_text(ITRF94_PRJ)
    out = tmp_path / "t.parquet"
    con = duckdb.connect()
    con.execute("install spatial; load spatial")
    m.export_layer(con, shp, out)
    assert con.sql(f"select st_hasm(geometry), st_astext(geometry) from '{out}'").fetchone() == (
        False,
        "LINESTRING (140.5 36.25, 141 37)",
    )
