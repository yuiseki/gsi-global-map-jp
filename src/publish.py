#!/usr/bin/env python3
"""Push the card, the GeoParquet of every vector layer and every raw zip to the Hugging Face Hub.

Each version's zips go up unchanged after their sha256 is checked against
data/raw/<version>/MANIFEST.json, and the card must declare every Parquet
file under data/parquet/ as a subset (config_name '<version>.<layer>').
The rasters have no Parquet; their zips go up as served.

    uv run python src/publish.py             # dry run
    uv run python src/publish.py --push
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "yuiseki/gsi-global-map-jp"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    data = ROOT / "data"
    card = (data / "README.md").read_text(encoding="utf-8")
    files = ["README.md", "LICENSE", "provenance.yaml"]
    for d in sorted(p for p in (data / "raw").iterdir() if p.is_dir()):
        manifest = json.loads((d / "MANIFEST.json").read_text())
        for name, m in manifest.items():
            if sha256(d / name) != m["sha256"]:
                raise SystemExit(f"raw/{d.name}/{name} is not the file in its manifest")
        files += [f"raw/{d.name}/MANIFEST.json"] + [f"raw/{d.name}/{n}" for n in manifest]
    parquets = sorted((data / "parquet").glob("*/*.parquet"))
    if not parquets:
        raise SystemExit("no Parquet under data/parquet; run scripts/03_export_parquet.py")
    for p in parquets:
        version, layer = p.parent.name, p.stem
        if (
            f"- config_name: '{version}.{layer}'\n  data_files: parquet/{version}/{layer}.parquet\n"
            not in card
        ):
            raise SystemExit(f"the card does not declare the subset {version}.{layer}")
        files.append(f"parquet/{version}/{layer}.parquet")
    total = sum((data / f).stat().st_size for f in files)
    print(a.repo)
    for f in files:
        print(f"  {(data / f).stat().st_size:>12,}  {f}")
    print(f"  {len(files)} files, {total / 1e6:.1f} MB")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return 0

    from huggingface_hub import HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True, private=False)
    api.upload_folder(
        folder_path=str(data), repo_id=a.repo, repo_type="dataset", allow_patterns=files
    )
    print(f"\npushed to https://huggingface.co/datasets/{a.repo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
