#!/usr/bin/env python3
"""Build small WebP gallery thumbnails without changing any original artwork."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
MAX_SIZE = (420, 560)
QUALITY = 78


def preview_path(original: str) -> Path:
    relative = Path(original)
    if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "assets":
        raise ValueError(f"Unsafe asset path: {original!r}")
    return ROOT / "previews" / relative.with_suffix(".webp")


def build() -> None:
    catalog = json.loads((ROOT / "catalog/assets.json").read_text(encoding="utf-8"))
    expected: set[Path] = set()
    written = 0
    unchanged = 0
    original_bytes = 0
    preview_bytes = 0
    missing = []

    for entry in catalog["assets"]:
        if entry.get("download_status") != "downloaded" or not entry.get("local_path"):
            continue
        path = ROOT / entry["local_path"]
        output = preview_path(entry["local_path"])
        if not path.is_file():
            missing.append(entry["local_path"])
            continue

        expected.add(output)
        try:
            with Image.open(path) as source:
                source.seek(0)
                image = ImageOps.exif_transpose(source)
                image.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
                has_alpha = "A" in image.getbands() or "transparency" in image.info
                image = image.convert("RGBA" if has_alpha else "RGB")
                buffer = io.BytesIO()
                image.save(buffer, format="WEBP", quality=QUALITY, method=5)
                content = buffer.getvalue()
        except (OSError, UnidentifiedImageError, ValueError) as exc:
            raise RuntimeError(f"Cannot build preview for {path}: {exc}") from exc

        original_bytes += path.stat().st_size
        preview_bytes += len(content)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.is_file() and output.read_bytes() == content:
            unchanged += 1
        else:
            output.write_bytes(content)
            written += 1

    # Only remove thumbnails that this script previously owned.
    preview_root = ROOT / "previews" / "assets"
    removed = 0
    if preview_root.exists():
        for leftover in preview_root.rglob("*.webp"):
            if leftover not in expected:
                leftover.unlink()
                removed += 1

    print(f"Preview build: written={written}, unchanged={unchanged}, removed={removed}")
    print(f"Source bytes={original_bytes}; thumbnail bytes={preview_bytes}; "
          f"estimated transfer reduction={(1-preview_bytes/original_bytes)*100:.1f}%"
          if original_bytes else "No artwork found")
    if missing:
        raise SystemExit(f"Downloaded assets missing from repository: {missing}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    build()
