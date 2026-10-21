#!/usr/bin/env python3
"""Regression test for actual, committed comedy media assets."""
import hashlib, io, json, math, wave, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
base=ROOT/"assets/comedy"
cat=json.loads((base/"catalog.json").read_text(encoding="utf-8"))
assert cat["schema_version"]=="1.0.0"
sounds,effects=cat["sounds"],cat["effects"]
assert len(sounds)>=24 and len(effects)>=16
assert cat["summary"]["total"]==len(sounds)+len(effects)
ids=[a["id"] for a in sounds+effects]
assert len(set(ids))==len(ids),"duplicate id"
for a in sounds+effects:
    p=base/a["path"]
    assert p.is_file(),str(p)
    assert len(p.read_bytes())==a["bytes"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"]
for a in sounds:
    with wave.open(str(base/a["path"]),"rb") as w:
        assert w.getnchannels()==1
        assert w.getsampwidth()==2
        assert w.getframerate()==32000
        samples=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2")
        assert abs(len(samples)/32000-a["seconds"])<.025,a["id"]
        assert samples.size>3200
        assert np.max(np.abs(samples.astype(np.int32)))<=32767
        assert np.sqrt(np.mean(samples.astype(np.float64)**2))>75,a["id"]
for a in effects:
    anim=base/a["path"]
    with Image.open(anim) as im:
        assert im.n_frames==16,a["id"]
        assert im.size==(360,360)
        visible=False
        for frame in (0,4,8,12,15):
            im.seek(frame)
            rgba=im.convert("RGBA")
            alpha=rgba.getchannel("A")
            mn,mx=alpha.getextrema()
            assert mn==0,(a["id"],frame,"not transparent")
            visible=visible or mx>0
        assert visible
    with Image.open(base/a["poster"]) as pic:
        assert pic.mode=="RGBA" and pic.size==(360,360)
        assert pic.getchannel("A").getextrema()[0]==0
    z=base/a["frames_zip"]
    with zipfile.ZipFile(z) as f:
        frames=sorted(p for p in f.namelist() if p.endswith(".png"))
        assert len(frames)==16,a["id"]
        for fname in (frames[0],frames[8],frames[-1]):
            with Image.open(io.BytesIO(f.read(fname))) as fr:
                assert fr.mode=="RGBA" and fr.size==(360,360)
with zipfile.ZipFile(base/"comedy-sfx-24-wav.zip") as z:
    assert len(z.namelist())==len(sounds)
    assert all(name.endswith(".wav") for name in z.namelist())
print(f"PASS: {len(sounds)} non-silent authentic WAVs and {len(effects)} real-alpha animated WebPs,"
      " 16-frame PNG ZIPs, cover PNGs; checksums, durations and manifest validated.")
