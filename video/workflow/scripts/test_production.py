#!/usr/bin/env python3
"""Contract tests: process controls do not prescribe artistic structure."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import production


class OpenProductionTests(unittest.TestCase):
    def manifest(self, folder, **changes):
        data = {
            "schema_version": "1",
            "id": "independent-test",
            "title": "An independent project with no required characters or captions",
            "required_files": [],
            "render": {
                "final": {
                    "argv": ["python", "-c", "print('any project-specific renderer')"],
                    "output": "output/{id}-final.mp4",
                }
            },
        }
        data.update(changes)
        path = Path(folder) / "project.json"
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return path

    def test_no_dialogue_actors_shots_or_music_required(self):
        with tempfile.TemporaryDirectory(dir=production.ROOT) as folder:
            source = self.manifest(folder)
            info = production.load_manifest(source)
            self.assertNotIn("characters", info)
            self.assertNotIn("shots", info)
            self.assertNotIn("background", info)
            self.assertNotIn("voice", info)

    def test_preview_is_optional_not_style_mandate(self):
        with tempfile.TemporaryDirectory(dir=production.ROOT) as folder:
            info = production.load_manifest(self.manifest(folder))
            self.assertIsNone(production.invoke(info, "preview"))

    def test_escape_from_output_folder_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=production.ROOT) as folder:
            bad = {"final": {"argv": ["python", "-V"],
                             "output": "output/../../bad.mp4"}}
            with self.assertRaises(ValueError):
                production.load_manifest(self.manifest(folder, render=bad))

    def test_examples_use_distinct_renderers(self):
        a = production.load_manifest("video/projects/deep-abyss-meeting/project.json")
        b = production.load_manifest("video/projects/shadow-protocol-mv/project.json")
        self.assertNotEqual(a["render"]["final"]["argv"][1],
                            b["render"]["final"]["argv"][1])

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "Needs FFmpeg")
    def test_independent_silent_video_and_any_aspect_ratio(self):
        project_id = "independent-test"
        output = production.WORKSPACE / "output" / (project_id + "-preview.mp4")
        try:
            with tempfile.TemporaryDirectory(dir=production.ROOT) as folder:
                command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                           "-f", "lavfi", "-i", "color=c=blue:s=480x270:r=12",
                           "-t", "0.75", "-c:v", "libx264", "-pix_fmt",
                           "yuv420p", "{output}"]
                render = {
                    "preview": {"argv": command, "output": "output/{id}-preview.mp4",
                                "checks": {"min_seconds": 0.5}},
                    "final": {"argv": command, "output": "output/{id}-final.mp4"}
                }
                info = production.load_manifest(self.manifest(folder, render=render))
                result = production.invoke(info, "preview")
                self.assertEqual(result["width"], 480)
                self.assertEqual(result["height"], 270)
                self.assertEqual(result["audio_codecs"], [])
        finally:
            output.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
