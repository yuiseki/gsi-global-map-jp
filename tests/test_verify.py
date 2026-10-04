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
