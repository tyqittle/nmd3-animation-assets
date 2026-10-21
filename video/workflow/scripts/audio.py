#!/usr/bin/env python3
"""Ninja 3 audio production: Chinese multi-voice TTS, timing and ducked mixing.

edge: natural Mandarin via online Edge voices (requires network, never silently
      replaces failed speech with espeak). placeholder: legacy offline test.
off: instrumental soundtrack and sound effects only.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
import wave
from pathlib import Path

import numpy as np

SR = 24000
# Voices are recognizable *synthetic presets*, NOT imitation of game actors.
PROFILES = {
    "hayabusa": {"voice": "zh-CN-YunyangNeural", "rate": "+9%", "pitch": "-5Hz"},
    "xiaohei": {"voice": "zh-CN-YunxiNeural", "rate": "+13%", "pitch": "+4Hz"},
    "cangya": {"voice": "zh-CN-YunjianNeural", "rate": "+6%", "pitch": "-4Hz"},
    "ali": {"voice": "zh-CN-YunxiaNeural", "rate": "+12%", "pitch": "+2Hz"},
    "lin": {"voice": "zh-CN-XiaoxiaoNeural", "rate": "+8%", "pitch": "+0Hz"},
    "blood": {"voice": "zh-CN-YunyangNeural", "rate": "-7%", "pitch": "-16Hz"},
}
MAX_TEMPO = 1.70
VOICE_INSET = 0.16
VOICE_END_MARGIN = 0.24


def checked(command, *, binary=False, timeout=65):
    process = subprocess.run(command, capture_output=True, timeout=timeout, check=False)
    if process.returncode:
        error = process.stderr.decode("utf-8", errors="replace")[-1600:]
        raise RuntimeError("Command failed: " + " ".join(map(str, command[:5])) + "\n" + error)
    return process.stdout if binary else None


def decode(path):
    raw = checked(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "pipe:1"],
        binary=True,
    )
    samples = np.frombuffer(raw, dtype="<f4").copy()
    if not len(samples) or not np.isfinite(samples).all():
        raise RuntimeError("Empty or invalid speech audio: " + str(path))
    return samples


def trim_silence(samples):
    # Preserve consonants and light breaths; remove TTS encoder padding only.
    peak = float(np.max(np.abs(samples)))
    if peak < 0.002:
        raise RuntimeError("Generated speech is silent")
    active = np.flatnonzero(np.abs(samples) >= max(0.006, peak * 0.022))
    if not len(active):
        raise RuntimeError("Generated speech has no audible content")
    start = max(0, int(active[0]) - int(SR * 0.055))
    end = min(len(samples), int(active[-1]) + int(SR * 0.100))
    return samples[start:end]


def accelerate(samples, tempo):
    if tempo <= 1.005:
        return samples
    with tempfile.TemporaryDirectory() as tmp:
        incoming, outgoing = Path(tmp) / "input.wav", Path(tmp) / "output.wav"
        write_wav(incoming, samples)
        checked(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                 "-i", str(incoming), "-af", "atempo=" + format(tempo, ".5f"),
                 "-ar", str(SR), "-ac", "1", str(outgoing)])
        return decode(outgoing)


def write_wav(path, samples):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm.tobytes())


def get_edge_speech(phrase, profile, cache):
    executable = shutil.which("edge-tts")
    if not executable:
        raise RuntimeError("Natural Mandarin voices require 'pip install edge-tts'")
    cache.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(json.dumps(
        [phrase, profile], ensure_ascii=False, sort_keys=True
    ).encode("utf-8")).hexdigest()
    target = cache / (key + ".mp3")
    if not target.exists() or target.stat().st_size < 500:
        error = None
        for attempt in range(3):
            try:
                checked([executable, "--voice", profile["voice"],
                         "--rate=" + profile["rate"],
                         "--pitch=" + profile["pitch"], "--text", phrase,
                         "--write-media", str(target)], timeout=75)
                if target.stat().st_size < 500:
                    raise RuntimeError("TTS returned an empty MP3")
                error = None
                break
            except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
                error = exc
                target.unlink(missing_ok=True)
                if attempt < 2:
                    time.sleep(attempt + 1)
        if error is not None:
            raise RuntimeError(
                "Natural voice generation failed; no robot-voice substitution. "
                "Check Edge TTS connectivity, or explicitly choose --tts placeholder. "
                + str(error)
            ) from error
    return decode(target)


def get_placeholder_speech(phrase, target):
    if not shutil.which("espeak-ng"):
        raise RuntimeError("Offline placeholder requires espeak-ng")
    checked(["espeak-ng", "-v", "zh", "-s", "205", "-p", "60", "-a", "150",
             "-w", str(target), phrase])
    return decode(target)


def synthesize(shot, episode, mode, cache, temp):
    key = shot["speaker"]
    profile = dict(PROFILES.get(key, PROFILES["hayabusa"]))
    # Allow character or shot overrides without adding voice actors to the code.
    profile.update(episode["characters"][key].get("voice_profile", {}))
    profile.update(shot.get("voice_profile", {}))
    phrase = shot["voice"].strip()
    if mode == "edge":
        samples = get_edge_speech(phrase, profile, cache)
    elif mode == "placeholder":
        samples = get_placeholder_speech(phrase, temp / "placeholder.wav")
    else:
        raise ValueError("Unknown narration mode: " + str(mode))
    return trim_silence(samples), profile


def fit_to_shot(samples, shot):
    begin = float(shot["start"]) + VOICE_INSET
    end = float(shot["end"]) - VOICE_END_MARGIN
    available = end - begin
    if available <= 0.2:
        raise ValueError("Shot too short for narration: " + str(shot))
    source_sec = len(samples) / SR
    # Better than the old hard crop: keep every spoken syllable.
    tempo = max(1.0, source_sec / available * 1.035)
    if tempo > MAX_TEMPO:
        raise ValueError(
            "Dialogue needs a longer shot or shorter script: "
            + repr(shot.get("voice", "")) + " ("
            + format(source_sec, ".2f") + "s speech in "
            + format(available, ".2f") + "s slot; speed would be "
            + format(tempo, ".2f") + "x)"
        )
    result = accelerate(samples, tempo)
    if len(result) / SR > available + 0.018:
        # Never quietly lose the last words.
        raise RuntimeError("Voice duration exceeds shot after tempo adjustment")
    # 12 ms entrance/exit avoids clicks without destroying last words.
    ramp = min(int(SR * 0.012), len(result) // 4)
    if ramp:
        result[:ramp] *= np.linspace(0, 1, ramp, dtype=np.float32)
        result[-ramp:] *= np.linspace(1, 0, ramp, dtype=np.float32)
    return result, begin, source_sec, tempo


def add_at(target, samples, seconds, gain=1.0):
    index = round(seconds * SR)
    if index < 0 or index >= len(target):
        return
    end = min(len(target), index + len(samples))
    if end > index:
        target[index:end] += samples[:end-index] * gain


def note(frequency, seconds, level=0.04):
    t = np.arange(int(seconds * SR), dtype=np.float32) / SR
    env = np.minimum(1, t / 0.012) * np.minimum(1, np.maximum(0, (seconds-t) / 0.15))
    return np.sin(2 * np.pi * frequency * t) * env * level


def create(episode, output, duration, tts="edge", report_path=None):
    if tts not in ("edge", "placeholder", "off"):
        raise ValueError("Expected narration: edge, placeholder, off")
    total = int(round(duration * SR))
    music = np.zeros(total, dtype=np.float32)
    effects = np.zeros(total, dtype=np.float32)
    vocals = np.zeros(total, dtype=np.float32)
    duck = np.ones(total, dtype=np.float32)
    rng = np.random.default_rng(2026)
    beat = 60 / 112
    pitches = (220, 196, 174.6, 164.8)
    for i in range(int(duration / beat) + 1):
        at = 2.4 + i * beat
        if at >= duration:
            break
        ts = np.arange(int(.17 * SR), dtype=np.float32) / SR
        kick = np.sin(2*np.pi*(90*ts-26*ts*ts)) * np.exp(-ts*26) * .13
        add_at(music, kick, at)
        add_at(music, rng.standard_normal(len(ts)).astype(np.float32) * np.exp(-ts*41) * .04, at + beat/2)
        add_at(music, note(pitches[(i//4) % 4], .3, .036), at)
        add_at(music, note(pitches[(i//4) % 4]*2, .16, .02), at + beat*.62)
    for shot in episode["shots"][1:]:
        add_at(effects, note(670, .11, .045), shot["start"])
    for i in range(3):
        add_at(effects, note((520, 390, 260)[i], .24, .075), 18.4 + i*.2)
    for i in range(4):
        add_at(effects, note(110+110*i, .3, .065), 31.62 + i*.13)

    report = {"mode": tts, "sample_rate": SR, "duration": duration,
              "clips": [], "speech_clipped": False}
    if tts != "off":
        cache = Path(os.environ.get("NMD3_VOICE_CACHE", "output/.voice-cache"))
        with tempfile.TemporaryDirectory() as work:
            for n, shot in enumerate(episode["shots"]):
                phrase = shot.get("voice")
                if not phrase or shot["start"] >= duration:
                    continue
                samples, profile = synthesize(shot, episode, tts, cache, Path(work))
                aligned, start, raw_duration, tempo = fit_to_shot(samples, shot)
                if start + len(aligned)/SR > duration + .002:
                    raise ValueError("Narration crosses requested video duration")
                # Consistent intelligibility; normalize by both peak and RMS.
                peak = float(np.max(np.abs(aligned)))
                rms = float(np.sqrt(np.mean(aligned**2)))
                gain = min(2.4, .74/max(.001, peak), .145/max(.001, rms))
                aligned *= gain
                add_at(vocals, aligned, start)
                # Music ducking with 80ms attack and 230ms release.
                attack, release = int(.08*SR), int(.23*SR)
                left = max(0, round(start*SR)-attack)
                right = min(total, round(start*SR)+len(aligned)+release)
                fade = np.ones(right-left, dtype=np.float32)
                a = round(start*SR)-left
                b = min(right-left, a+len(aligned))
                if a > 0:
                    fade[:a] = np.linspace(1, .28, a, dtype=np.float32)
                fade[a:b] = .28
                if right-left > b:
                    fade[b:] = np.linspace(.28, 1, right-left-b, dtype=np.float32)
                duck[left:right] = np.minimum(duck[left:right], fade)
                item = {"shot": n, "speaker": shot["speaker"], "text": phrase,
                        "voice": profile["voice"] if tts == "edge" else "espeak-ng/zh",
                        "start": round(start, 3),
                        "end": round(start+len(aligned)/SR, 3),
                        "source_seconds": round(raw_duration, 3),
                        "final_seconds": round(len(aligned)/SR, 3),
                        "tempo": round(tempo, 3)}
                report["clips"].append(item)
                print("VOICE:", json.dumps(item, ensure_ascii=False), flush=True)
    # Voice-first mix. The music never overpowers the dialogue.
    mixed = music * duck + effects * .80 + vocals
    peak = float(np.max(np.abs(mixed))) if len(mixed) else 0
    if peak > .96:
        mixed *= .96 / peak
    report["peak"] = round(float(np.max(np.abs(mixed))) if len(mixed) else 0, 4)
    report["voice_count"] = len(report["clips"])
    write_wav(output, mixed)
    if report_path:
        dest = Path(report_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
