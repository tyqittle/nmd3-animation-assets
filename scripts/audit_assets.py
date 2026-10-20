#!/usr/bin/env python3
"""Audit actual asset files, formats, sizes and identical duplicates."""
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image
import hashlib, json

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "catalog/assets.json").read_text(encoding="utf-8"))
records, sha_groups = [], defaultdict(list)
for asset in catalog["assets"]:
    path = ROOT / asset["local_path"]
    row = {"id": asset["id"], "name": asset["name"], "file": asset["local_path"]}
    if not path.is_file():
        row["status"] = "missing"
    else:
        try:
            data = path.read_bytes()
            sha = hashlib.sha256(data).hexdigest()
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                row.update(status="ok", width=im.width, height=im.height,
                           format=im.format, alpha=("A" in im.getbands()),
                           bytes=len(data), sha256=sha)
            sha_groups[sha].append(asset["id"])
        except Exception as exc:
            row.update(status="invalid", error=str(exc))
    records.append(row)
out = {"summary": dict(Counter(r["status"] for r in records)),
       "duplicates": {k: v for k, v in sha_groups.items() if len(v) > 1},
       "items": records}
dest = ROOT / "reports/audit.json"
dest.parent.mkdir(exist_ok=True)
dest.write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print("Audit:", out["summary"], "duplicates:", len(out["duplicates"]))
