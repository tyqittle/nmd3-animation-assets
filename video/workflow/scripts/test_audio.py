#!/usr/bin/env python3
"""Offline audio regressions: use generated waveforms, never call a TTS service."""
import json
import sys
import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audio


class AudioWorkflowTests(unittest.TestCase):
    def sine(self, seconds):
        t = np.arange(round(seconds * audio.SR), dtype=np.float32) / audio.SR
        return (0.2 * np.sin(2 * np.pi * 225 * t)).astype(np.float32)

    def test_two_characters_use_different_voices(self):
        voices = [audio.PROFILES[k]["voice"] for k in ("hayabusa", "xiaohei", "lin")]
        self.assertEqual(len(set(voices)), 3)

    def test_long_speech_is_accelerated_not_hard_cropped(self):
        shot = {"start": 2.0, "end": 5.3, "voice": "测试完整保留所有台词"}
        aligned, start, original, tempo = audio.fit_to_shot(self.sine(3.4), shot)
        self.assertAlmostEqual(start, 2.16, places=2)
        self.assertAlmostEqual(original, 3.4, places=2)
        self.assertGreater(tempo, 1)
        self.assertGreater(len(aligned) / audio.SR, 2)
        self.assertLessEqual(start + len(aligned) / audio.SR, 5.3 - audio.VOICE_END_MARGIN + .02)

    def test_impossible_long_speech_fails_instead_of_clipping(self):
        shot = {"start": 0, "end": 2, "voice": "台词太长会报警"}
        with self.assertRaisesRegex(ValueError, "longer shot"):
            audio.fit_to_shot(self.sine(5), shot)

    def test_audio_report_and_voice_order(self):
        characters = {k: {"name": k} for k in ("xiaohei", "lin")}
        episode = {"characters": characters, "shots": [
            {"start": 0, "end": 4, "speaker": "xiaohei", "voice": "报告！"},
            {"start": 4, "end": 8, "speaker": "lin", "voice": "先别吵。"},
        ]}
        def fake_synth(shot, episode, mode, cache, temp):
            return self.sine(1.6), audio.PROFILES[shot["speaker"]]
        with tempfile.TemporaryDirectory() as work:
            out = Path(work) / "audio.wav"
            report_path = Path(work) / "report.json"
            with patch.object(audio, "synthesize", side_effect=fake_synth):
                data = audio.create(episode, out, 8, tts="edge", report_path=report_path)
            self.assertEqual(data["voice_count"], 2)
            self.assertFalse(data["speech_clipped"])
            self.assertGreater(data["peak"], 0)
            self.assertLessEqual(data["peak"], .96)
            self.assertLess(data["clips"][0]["end"], data["clips"][1]["start"])
            self.assertLess(data["clips"][1]["end"], 8)
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["voice_count"], 2)
            with wave.open(str(out), "rb") as stream:
                self.assertEqual(stream.getframerate(), 24000)
                self.assertEqual(stream.getnframes(), 8 * audio.SR)

    def test_offline_music_only_keeps_exact_length(self):
        episode = {"characters": {}, "shots": [{"start": 0, "end": 3}]}
        with tempfile.TemporaryDirectory() as work:
            output = Path(work) / "off.wav"
            report = audio.create(episode, output, 3, tts="off")
            self.assertEqual(report["voice_count"], 0)
            with wave.open(str(output), "rb") as stream:
                self.assertEqual(stream.getnframes(), 3 * audio.SR)


if __name__ == "__main__":
    unittest.main()
