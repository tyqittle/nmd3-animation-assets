#!/usr/bin/env python3
"""Creative-agnostic video production runner.

A project supplies its OWN renderer, edit style, soundtrack and output. This
runner checks the process (assets -> preview -> final -> technical QA), not the
composition. No layout, actors, dialogue, aspect ratio, or effects are assumed.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent


def confined(path, base):
    path = Path(path).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Path outside allowed workspace: " + str(path))
    return path


def load_manifest(path):
    source = confined(ROOT / path if not Path(path).is_absolute() else path, ROOT)
    if not source.is_file():
        raise FileNotFoundError(source)
    document = json.loads(source.read_text(encoding="utf-8"))
    if str(document.get("schema_version")) != "1":
        raise ValueError("Expected schema_version 1")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{1,80}", str(document.get("id", ""))):
        raise ValueError("Invalid project id")
    if not isinstance(document.get("title"), str) or not document["title"].strip():
        raise ValueError("Project title required")
    rendering = document.get("render", {})
    if not isinstance(rendering, dict) or "final" not in rendering:
        raise ValueError("Each project must define render.final")
    for stage, settings in rendering.items():
        if stage not in ("preview", "final"):
            raise ValueError("Unsupported render stage: " + stage)
        if not isinstance(settings, dict):
            raise ValueError("Render stage must be an object")
        argv = settings.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) and a for a in argv):
            raise ValueError("Expected argv string array for " + stage)
        if not isinstance(settings.get("output"), str):
            raise ValueError("Expected output path for " + stage)
        output = settings["output"].format(id=document["id"])
        confined(WORKSPACE / output, WORKSPACE / "output")
        if Path(output).suffix.lower() not in (".mp4", ".mov", ".webm", ".mkv"):
            raise ValueError("Render output must be a playable video filename")
    setup = document.get("setup", [])
    if not isinstance(setup, list):
        raise ValueError("setup must be an array of argv arrays")
    for command in setup:
        if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
            raise ValueError("setup command must be a nonempty argv array")
    if not isinstance(document.get("required_files", []), list):
        raise ValueError("required_files should be an array (can be empty)")
    for item in document.get("required_files", []):
        if not isinstance(item, str) or not item:
            raise ValueError("Invalid required_files entry")
        confined(WORKSPACE / item, WORKSPACE)
    return document


def ensure_assets(document):
    missing = []
    for item in document.get("required_files", []):
        if not (WORKSPACE / item).is_file():
            missing.append(item)
    if missing:
        raise FileNotFoundError("Missing production assets:\n" + "\n".join(missing))
    print("PASS: required source files:", len(document.get("required_files", [])), flush=True)


def output_for(document, stage):
    return confined(WORKSPACE / document["render"][stage]["output"].format(id=document["id"]),
                    WORKSPACE / "output")


def prepare(document):
    for command in document.get("setup", []):
        print("PREPARE:", " ".join(command), flush=True)
        subprocess.run(command, cwd=WORKSPACE, check=True, timeout=600)


def invoke(document, stage):
    if stage not in document["render"]:
        print("SKIP: this production does not define a " + stage + " renderer", flush=True)
        return None
    settings = document["render"][stage]
    out = output_for(document, stage)
    out.parent.mkdir(parents=True, exist_ok=True)
    substitutions = {"id": document["id"], "output": str(out),
                     "repo": str(ROOT), "workspace": str(WORKSPACE)}
    argv = [arg.format_map(substitutions) for arg in settings["argv"]]
    executable = shutil.which(argv[0])
    if executable is None:
        raise RuntimeError("Renderer executable unavailable: " + argv[0])
    print("RENDER", document["id"], stage, "via", argv[0], flush=True)
    timeout = int(settings.get("timeout_seconds", 1800))
    if timeout < 1 or timeout > 7200:
        raise ValueError("Invalid render timeout")
    subprocess.run(argv, cwd=WORKSPACE, check=True, timeout=timeout)
    return verify(out, settings.get("checks", {}))


def verify(path, checks=None):
    checks = checks or {}
    if not path.is_file() or not path.stat().st_size:
        raise RuntimeError("Renderer did not create a non-empty video: " + str(path))
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    info = json.loads(probe.stdout)
    streams = info.get("streams", [])
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    if not videos:
        raise RuntimeError("No decodable video stream")
    if checks.get("audio_required", False) and not audios:
        raise RuntimeError("Soundtrack/dialogue was required but audio is missing")
    duration = float(info.get("format", {}).get("duration", 0))
    if duration <= 0:
        raise RuntimeError("Invalid video duration")
    for setting, compare in (("min_seconds", lambda n: duration >= n),
                             ("max_seconds", lambda n: duration <= n)):
        if setting in checks and not compare(float(checks[setting])):
            raise RuntimeError("Video violates " + setting + ": " + str(duration))
    v = videos[0]
    for setting, key in (("min_width", "width"), ("min_height", "height")):
        if setting in checks and int(v.get(key, 0)) < int(checks[setting]):
            raise RuntimeError("Video violates " + setting)
    result = {"file": str(path), "seconds": round(duration, 3),
              "width": v.get("width"), "height": v.get("height"),
              "video_codec": v.get("codec_name"),
              "audio_codecs": [stream.get("codec_name") for stream in audios],
              "bytes": path.stat().st_size}
    print("QA PASS:", json.dumps(result, ensure_ascii=False), flush=True)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", help="Path inside repository to project.json")
    parser.add_argument("--stage", choices=("validate", "preview", "final", "all", "validate-all"),
                        default="all")
    args = parser.parse_args(argv)
    if args.stage == "validate-all":
        manifests = sorted((ROOT / "video" / "projects").glob("**/project.json"))
        if not manifests:
            raise RuntimeError("No project manifests")
        for path in manifests:
            d = load_manifest(path)
            ensure_assets(d)
            print("PROJECT PASS:", d["id"])
        print("PASS:", len(manifests), "independent productions")
        return
    if not args.project:
        parser.error("--project required except for validate-all")
    document = load_manifest(args.project)
    ensure_assets(document)
    print("PROJECT:", document["title"], " | project:", document["id"], flush=True)
    if args.stage in ("preview", "final", "all"):
        prepare(document)
    if args.stage in ("preview", "all"):
        invoke(document, "preview")
    if args.stage in ("final", "all"):
        invoke(document, "final")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("PRODUCTION FAILED:", exc, file=sys.stderr)
        sys.exit(1)
