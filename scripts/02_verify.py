#!/usr/bin/env python3
"""Check every fetched file against data/raw/<version>/MANIFEST.json.

For each version directory:
  - every file in the manifest exists, has the bytes and sha256 recorded
  - no file in the directory is missing from the manifest
  - every zip passes zipfile.testzip
  - every gzip reads to the end
  - every CSV (loose, or a member of a zip) is counted with the csv module

Prints one ok/FAIL line per check and exits 1 if any failed.

    uv run python scripts/02_verify.py
"""

import csv
import gzip
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"


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
    if failures:
        print(f"\n{len(failures)} checks failed")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
