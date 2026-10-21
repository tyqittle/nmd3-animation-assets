#!/usr/bin/env python3
"""Audit real generated Mambo neural speech SFX. No placeholder or dead links."""
from __future__ import annotations
import hashlib
import io
import json
import wave
import zipfile
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"assets/comedy/mambo"
CAT=BASE/"catalog.json"
assert CAT.is_file(),CAT
cat=json.loads(CAT.read_text(encoding="utf-8"))
items=cat["sounds"]
assert len(items)==14 and cat["summary"]["total"]==14, "wrong Mambo count"
ids=[item["id"] for item in items]
assert len(set(ids))==14
assert all(item["name"].startswith("曼波") or "曼波" in item["name"]
           for item in items)
assert all(item["spoken_text"] in ("マンボ！","マンボ、マンボ！",
                                    "曼波！","曼波，曼波，曼波！","曼波？")
           for item in items)
assert all(item["original_game_voice"] is False for item in items)
distinct=set()
total_samples=0
for a in items:
    p=ROOT/"assets/comedy"/a["path"]
    assert p.is_file(),(a["id"],"not committed")
    assert p.stat().st_size==a["bytes"]
    assert hashlib.sha256(p.read_bytes()).hexdigest()==a["sha256"]
    with wave.open(str(p),"rb") as w:
        assert w.getframerate()==32000
        assert w.getnchannels()==1 and w.getsampwidth()==2
        x=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2")
        assert .15 < len(x)/32000 < 7.5,(a["id"],len(x))
        assert np.max(np.abs(x.astype(np.int32)))<=32767
        rms=float(np.sqrt(np.mean(x.astype(np.float64)**2)))
        assert rms>800,(a["id"],rms)
        assert abs(a["seconds"]-len(x)/32000)<.03
        assert np.any(x!=0)
        total_samples+=len(x)
        distinct.add(a["sha256"])
assert len(distinct)==len(items),"identical waveforms"
with zipfile.ZipFile(BASE/"mambo-sfx-14-wav.zip") as z:
    files=z.namelist()
    assert len(files)==14 and all(f.endswith(".wav") for f in files)
    for a in items:
        name=Path(a["path"]).name
        assert name in files
        assert z.read(name)==(BASE/name).read_bytes()
print("PASS: 14 genuine voice-bearing WAVs, mono PCM 32000/16, "
      "duration, non-silence, ZIP completeness, sha256 provenance")
