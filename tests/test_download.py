import importlib.util
from pathlib import Path

import pytest

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location(
    "download", HERE.parent / "scripts" / "01_download.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

PAGE = (HERE / "fixtures" / "gm_jpn_table.html").read_text(encoding="utf-8")
BASE = "https://www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/"


@pytest.mark.parametrize(
    ("header", "version"),
    [
        ("第2.2版ベクタ（2016年公開）", "vector-2.2"),
        ("第2.1版ベクタ\n（2015年公開）", "vector-2.1"),
        ("第2版ベクタ（2011年公開）", "vector-2.0"),
        ("第1.1版ラスタ（2006年公開）", "raster-1.1"),
        ("第1.0版ラスタ（2000年公開）", "raster-1.0"),
    ],
)
def test_version_from_header(header, version):
    assert m.version_from_header(header) == version


def test_version_from_header_rejects_unknown():
    with pytest.raises(ValueError):
        m.version_from_header("データ名")


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("gm-jpn-all_u_2_2.zip", "vector-2.2"),
        ("gm-jpn-bnd_u_2_1.zip", "vector-2.1"),
        ("gm-jpn-pop_u_2.zip", "vector-2.0"),
        ("gm-jpn-el_u_1_1.zip", "raster-1.1"),
        ("gm-jpn-ve_u_1_0.zip", "raster-1.0"),
    ],
)
def test_version_from_filename(name, version):
    assert m.version_from_filename(name) == version


def test_parse_page_finds_the_18_files_of_the_table():
    files = m.parse_page(PAGE)
    assert len(files) == 18
    assert all(f["url"].startswith(BASE) and f["url"].endswith(".zip") for f in files)
    assert len({f["url"] for f in files}) == 18
    # the viewer below the table is software, not data
    assert not any("Viewer" in f["url"] for f in files)


def test_parse_page_reads_the_row_and_column_of_each_link():
    by_name = {Path(f["url"]).name: f for f in m.parse_page(PAGE)}
    f = by_name["gm-jpn-all_u_2_2.zip"]
    assert f["version"] == "vector-2.2"
    assert f["layer"] == "全レイヤ"
    assert f["published"] == "2016"
    assert f["spec_version"] == "第2.2版"
    assert f["link_text"] == "Shape (ZIP, 9.2MB)"
    g = by_name["gm-jpn-hydro_u_2.zip"]
    assert (g["version"], g["layer"], g["published"]) == ("vector-2.0", "水系", "2011")
    h = by_name["gm-jpn-el_u_1_0.zip"]
    assert (h["version"], h["layer"], h["spec_version"]) == ("raster-1.0", "標高", "第1.2.1版")


def test_parse_page_versions_agree_with_filenames():
    for f in m.parse_page(PAGE):
        assert f["version"] == m.version_from_filename(Path(f["url"]).name)


def test_parse_page_counts_per_version():
    counts = {}
    for f in m.parse_page(PAGE):
        counts[f["version"]] = counts.get(f["version"], 0) + 1
    assert counts == {
        "vector-2.2": 2,
        "vector-2.1": 3,
        "vector-2.0": 5,
        "raster-1.1": 4,
        "raster-1.0": 4,
    }


def test_parse_page_finds_the_licence_link():
    assert m.licence_url(PAGE) == "https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html"


def test_parse_page_without_the_table_fails():
    with pytest.raises(ValueError):
        m.parse_page("<html><body><p>moved</p></body></html>")
