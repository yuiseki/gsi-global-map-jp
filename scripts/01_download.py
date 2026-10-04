#!/usr/bin/env python3
"""Fetch every zip in the download table of Global Map Japan (地球地図日本).

The Geospatial Information Authority of Japan lists the files in one table on
https://www.gsi.go.jp/kankyochiri/gm_jpn.html: a column per map version
(vector 2.2, 2.1 and 2.0, raster 1.1 and 1.0) and a row per layer. The URLs
are read from that table, never built. Each zip goes, as served, into
data/raw/<map version>/ (vector-2.2, vector-2.1, vector-2.0, raster-1.1,
raster-1.0); the directories are named after the map version, not the fetch
date, because each version is a fixed release.

GSI has replaced files after publication (gm-jpn-all_u_2_2.zip carries a
2023 Last-Modified for a 2016 release). Before fetching, every file is asked
for with HEAD; one already in a MANIFEST.json whose size or Last-Modified has
changed upstream is reported and left alone, and the script exits 1, so the
copy we hold is never silently overwritten.

data/raw/<version>/MANIFEST.json records, for each file: url, bytes, sha256,
last_modified, fetched_at (UTC), and what the page states about it (layer,
publication year, Global Map Specifications version, the link text with its
rounded size). A file already in the manifest whose sha256 matches is not
fetched again.

gsi.go.jp still needs TLS legacy renegotiation, which OpenSSL 3 refuses by
default; the SSL context below turns on OP_LEGACY_SERVER_CONNECT for these
two hosts only.

    uv run python scripts/01_download.py
"""

import hashlib
import json
import re
import shutil
import ssl
import sys
import time
import urllib.request
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PAGE_URL = "https://www.gsi.go.jp/kankyochiri/gm_jpn.html"
DATA_PREFIX = "https://www1.gsi.go.jp/geowww/globalmap-gsi/download/data/gm-japan/"
UA = "gsi-global-map-jp/1 (+https://github.com/yuiseki/gsi-global-map-jp)"
LIMIT_BYTES = 200 * 1000 * 1000
PAUSE = 1.0
TABLE_SUMMARY = "地球地図日本のデータ一覧"

CTX = ssl.create_default_context()
CTX.options |= ssl.OP_LEGACY_SERVER_CONNECT


def version_from_header(text: str) -> str:
    """'第2.2版ベクタ（2016年公開）' -> 'vector-2.2'; '第2版ベクタ' -> 'vector-2.0'."""
    mt = re.search(r"第(\d+)(?:\.(\d+))?版(ベクタ|ラスタ)", text)
    if not mt:
        raise ValueError(f"not a version header: {text!r}")
    kind = {"ベクタ": "vector", "ラスタ": "raster"}[mt.group(3)]
    return f"{kind}-{mt.group(1)}.{mt.group(2) or '0'}"


def version_from_filename(name: str) -> str:
    """'gm-jpn-all_u_2_2.zip' -> 'vector-2.2'; major 1 is raster, 2 is vector."""
    mt = re.fullmatch(r"gm-jpn-[a-z]+_u_(\d+)(?:_(\d+))?\.zip", name)
    if not mt:
        raise ValueError(f"not a Global Map Japan file name: {name!r}")
    kind = {"1": "raster", "2": "vector"}[mt.group(1)]
    return f"{kind}-{mt.group(1)}.{mt.group(2) or '0'}"


class _Table(HTMLParser):
    """Collects the rows of the download table as lists of (tag, text, hrefs).

    The page lays itself out in an outer table, so the download table is the
    one whose summary is TABLE_SUMMARY; tables nested in it are not expected.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows: list[list[tuple[str, str, list[str]]]] = []
        self.links: list[tuple[str, str]] = []  # every <a> on the page: href, text
        self._stack: list[bool] = []  # one per open table: is it the download table
        self._cell: tuple[str, list[str], list[str]] | None = None
        self._a: tuple[str, list[str]] | None = None

    @property
    def _inside(self) -> bool:
        return bool(self._stack) and self._stack[-1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self._a = (a["href"], [])
        if tag == "table":
            self._stack.append(a.get("summary") == TABLE_SUMMARY)
        elif self._inside and tag == "tr":
            self.rows.append([])
        elif self._inside and tag in ("td", "th"):
            self._cell = (tag, [], [])
        elif self._inside and tag == "br" and self._cell:
            self._cell[1].append("\n")
        if tag == "a" and self._cell and a.get("href"):
            self._cell[2].append(a["href"])

    def handle_endtag(self, tag):
        if tag == "a" and self._a:
            self.links.append((self._a[0], "".join(self._a[1]).strip()))
            self._a = None
        if tag in ("td", "th") and self._cell and self.rows:
            t, text, hrefs = self._cell
            self.rows[-1].append((t, "".join(text).strip(), hrefs))
            self._cell = None
        elif tag == "table" and self._stack:
            self._stack.pop()

    def handle_data(self, data):
        if self._a:
            self._a[1].append(data)
        if self._cell:
            self._cell[1].append(data)


def parse_page(html: str) -> list[dict]:
    """The zips of the download table, each with what its row and column say."""
    p = _Table()
    p.feed(html)
    if len(p.rows) < 3:
        raise ValueError("download table not found on the page")
    header = p.rows[0]
    columns = [version_from_header(t) for _, t, _ in header[1:]]
    published = [re.search(r"(\d{4})年公開", t).group(1) for _, t, _ in header[1:]]
    spec = {}
    link_text = {urljoin(PAGE_URL, h): t for h, t in p.links}
    files = []
    for row in p.rows[1:]:
        label = row[0][1]
        if label == "地球地図仕様":
            spec = dict(zip(columns, (t for _, t, _ in row[1:]), strict=True))
            continue
        for i, (_, _, hrefs) in enumerate(row[1:]):
            for h in hrefs:
                url = urljoin(PAGE_URL, h)
                if not (url.startswith(DATA_PREFIX) and url.endswith(".zip")):
                    continue
                files.append(
                    {
                        "url": url,
                        "version": columns[i],
                        "layer": label,
                        "published": published[i],
                        "spec_version": spec.get(columns[i], ""),
                        "link_text": link_text.get(url, ""),
                    }
                )
    if not files:
        raise ValueError("no data files in the download table")
    return files


def licence_url(html: str) -> str:
    """The link the page gives for its terms of use (国土地理院コンテンツ利用規約)."""
    p = _Table()
    p.feed(html)
    for h, t in p.links:
        if "コンテンツ利用規約" in t:
            return urljoin(PAGE_URL, h)
    raise ValueError("terms of use link not found")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _open(url: str, method: str = "GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=300, context=CTX)


def head(url: str) -> dict:
    with _open(url, "HEAD") as r:
        return {
            "bytes": int(r.headers["Content-Length"]),
            "last_modified": r.headers.get("Last-Modified", ""),
        }


def fetch(url: str, dest: Path) -> dict:
    tmp = dest.with_suffix(dest.suffix + ".part")
    with _open(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
        length = r.headers.get("Content-Length")
        lm = r.headers.get("Last-Modified", "")
    got = tmp.stat().st_size
    if length is not None and got != int(length):
        tmp.unlink()
        raise SystemExit(f"{url}: got {got} bytes, the server stated {length}")
    tmp.replace(dest)
    return {
        "url": url,
        "bytes": got,
        "sha256": sha256(dest),
        "last_modified": lm,
        "fetched_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    with _open(PAGE_URL) as r:
        html = r.read().decode("utf-8")
    files = parse_page(html)
    licence = licence_url(html)
    for f in files:
        name = Path(f["url"]).name
        if version_from_filename(name) != f["version"]:
            raise SystemExit(f"{name}: in the {f['version']} column of the table")
    print(f"{len(files)} files in the table; terms of use {licence}")

    heads = {}
    for f in files:
        time.sleep(PAUSE)
        heads[f["url"]] = head(f["url"])
    total = sum(h["bytes"] for h in heads.values())
    print(f"{total:,} bytes in all")
    if total > LIMIT_BYTES:
        raise SystemExit(f"{total:,} bytes is over the limit of {LIMIT_BYTES:,}; nothing fetched")

    changed = []
    for version in dict.fromkeys(f["version"] for f in files):
        d = RAW / version
        d.mkdir(parents=True, exist_ok=True)
        mpath = d / "MANIFEST.json"
        manifest = json.loads(mpath.read_text()) if mpath.exists() else {}
        for f in (f for f in files if f["version"] == version):
            name = Path(f["url"]).name
            h = heads[f["url"]]
            old = manifest.get(name)
            if old and (d / name).exists() and sha256(d / name) == old["sha256"]:
                if (old["bytes"], old["last_modified"]) != (h["bytes"], h["last_modified"]):
                    changed.append(name)
                    print(
                        f"CHANGED {version}/{name}: we hold {old['bytes']:,} bytes of "
                        f"{old['last_modified']}, the server now has {h['bytes']:,} of "
                        f"{h['last_modified']}; left alone"
                    )
                continue
            time.sleep(PAUSE)
            entry = fetch(f["url"], d / name)
            if entry["bytes"] != h["bytes"]:
                raise SystemExit(f"{name}: {entry['bytes']} bytes, HEAD said {h['bytes']}")
            entry.update(
                source_page=PAGE_URL,
                terms_of_use=licence,
                **{k: f[k] for k in ("layer", "published", "spec_version", "link_text")},
            )
            manifest[name] = entry
            mpath.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
            print(f"{version}/{name}: {entry['bytes']:,} bytes, {entry['last_modified']}")
        mpath.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    if changed:
        print(f"{len(changed)} files changed upstream; see above")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
