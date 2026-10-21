#!/usr/bin/env python3
"""Download cataloged image candidates without bypassing source restrictions."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import time
from io import BytesIO
from pathlib import Path
from urllib import request, parse, error

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "catalog/assets.json"
REPORT = ROOT / "reports/download_report.json"
MAX_BYTES = 20 * 1024 * 1024

def inspect_image(data):
    from PIL import Image
    with Image.open(BytesIO(data)) as im:
        im.verify()
    with Image.open(BytesIO(data)) as im:
        return im.size, im.format, "A" in im.getbands()

def fetch(entry, timeout=18, dry_run=False):
    output = ROOT / entry["local_path"]
    base = (ROOT / "assets").resolve()
    if not str(output.resolve()).startswith(str(base) + os.sep):
        return {"id": entry["id"], "status": "invalid_output_path"}
    result = {"id": entry["id"], "name": entry["name"], "path": entry["local_path"]}
    if output.exists():
        try:
            raw = output.read_bytes()
            size, fmt, alpha = inspect_image(raw)
            return {**result, "status": "exists", "width": size[0], "height": size[1], "format": fmt,
                    "has_alpha": alpha, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        except Exception as exc:
            return {**result, "status": "invalid_existing", "error": str(exc)}
    url = entry["image_url"]
    host = parse.urlsplit(url).hostname
    if not url.startswith("https://") or not host:
        return {**result, "status": "invalid_url"}
    if dry_run:
        return {**result, "status": "dry_run", "url": url}
    encoded = parse.quote(url, safe=":/?&=%+#")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; personal NMD3 asset reference index)",
               "Accept": "image/png,image/jpeg,image/webp,image/*;q=0.8"}
    if host.endswith("biligame.com"):
        headers["Referer"] = "https://wiki.biligame.com/"
    try:
        req = request.Request(encoded, headers=headers)
        with request.urlopen(req, timeout=timeout) as res:
            if "text/html" in res.headers.get("Content-Type", "").lower():
                raise ValueError("HTML page rather than image")
            data = res.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError("File exceeds maximum size")
        (w, h), fmt, alpha = inspect_image(data)
        if max(w, h) < 260:
            raise ValueError(f"Image too small: {w}x{h}")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        return {**result, "status": "downloaded", "width": w, "height": h, "format": fmt,
                "has_alpha": alpha, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    except (error.URLError, OSError, ValueError) as exc:
        return {**result, "status": "failed", "error": str(exc)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=["all", "characters", "bosses", "weapons", "scenes", "wallpapers", "promos", "effects"], default="all")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=18)
    parser.add_argument("--delay", type=float, default=0.8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    entries = [a for a in catalog["assets"] if args.category == "all" or args.category == a["category"]]
    if args.limit > 0:
        entries = entries[:args.limit]
    results = []
    for i, entry in enumerate(entries, 1):
        record = fetch(entry, args.timeout, args.dry_run)
        results.append(record)
        if record["status"] in ("exists", "downloaded"):
            entry.update(download_status="downloaded", bytes=record["bytes"],
                         width=record["width"], height=record["height"],
                         sha256=record["sha256"], has_alpha=record["has_alpha"])
        print(f"[{i}/{len(entries)}] {entry['name']}: {record['status']} {record.get('error', '')}", flush=True)
        if i < len(entries) and record["status"] == "downloaded":
            time.sleep(max(0, args.delay))
    if not args.dry_run:
        CATALOG.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    from collections import Counter
    print("Summary:", dict(Counter(v["status"] for v in results)))

if __name__ == "__main__":
    main()
