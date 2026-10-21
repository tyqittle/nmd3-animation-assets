#!/usr/bin/env python3
"""Audit only archived real images; pending candidates are not missing files.

Fails the workflow on corruption, missing archived files, or metadata mismatches.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "catalog/assets.json").read_text(encoding="utf-8"))
records, sha_groups = [], defaultdict(list)
invalid = []

for asset in catalog["assets"]:
    row = {"id": asset["id"], "name": asset["name"], "file": asset["local_path"]}
    if asset.get("download_status") != "downloaded":
        row["status"] = "not_downloaded"
        records.append(row)
        continue
    path = ROOT / asset["local_path"]
    if not path.is_file():
        row["status"] = "missing"
        invalid.append(asset["id"])
    else:
        try:
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            with Image.open(path) as img:
                img.verify()
            with Image.open(path) as img:
                row.update(
                    status="ok", width=img.width, height=img.height,
                    format=img.format, alpha=("A" in img.getbands()),
                    bytes=len(data), sha256=sha
                )
            sha_groups[sha].append(asset["id"])
            mismatch = []
            for key in ("bytes", "width", "height"):
                if asset.get(key) != row[key]:
                    mismatch.append(f"{key}: {asset.get(key)} != {row[key]}")
            if asset.get("has_alpha") != row["alpha"]:
                mismatch.append("alpha metadata differs from stored image")
            if asset.get("sha256") != sha:
                mismatch.append("sha256 differs from catalog")
            if mismatch:
                row["status"] = "mismatch"
                row["details"] = mismatch
                invalid.append(asset["id"])
        except Exception as exc:
            row.update(status="invalid", error=str(exc))
            invalid.append(asset["id"])
    records.append(row)

duplicates = {sha: ids for sha, ids in sha_groups.items() if len(ids) > 1}
dest = ROOT / "reports/audit.json"
dest.parent.mkdir(exist_ok=True)
output = {
    "summary": dict(Counter(r["status"] for r in records)),
    "duplicates": duplicates,
    "issues": invalid,
    "items": records,
}
dest.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("Image integrity audit:", output["summary"],
      "duplicates:", len(duplicates), "corrupt:", len(invalid))
if invalid or duplicates:
    raise SystemExit("Image audit FAILED: inspect reports/audit.json")
