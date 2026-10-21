#!/usr/bin/env python3
"""Original synthetic music/FX and optional temporary eSpeak Mandarin voice."""
import shutil,subprocess,tempfile,wave
from pathlib import Path
import numpy as np
SR=24000
def create(episode,output,duration,tts):
    if tts=="placeholder" and not shutil.which("espeak-ng"):
        raise RuntimeError("Need espeak-ng for scratch narration; use --tts off otherwise")
    samples=int(duration*SR)
    data=np.zeros(samples,dtype=np.float32)
    rng=np.random.default_rng(2026)
    def add(sound,seconds,scale=1.):
        ix=int(seconds*SR)
        if ix<0 or ix>=samples:return
        end=min(samples,ix+len(sound))
        data[ix:end]+=sound[:end-ix]*scale
    def note(f,secs,level=.04):
        t=np.arange(int(secs*SR))/SR
        env=np.minimum(1,t/.012)*np.minimum(1,np.maximum(0,(secs-t)/.15))
        return np.sin(2*np.pi*f*t)*env*level
    beat=60/112
    pitches=(220,196,174.6,164.8)
    for i in range(int(duration/beat)+1):
        when=2.4+i*beat
        if when>=duration:break
        times=np.arange(int(.17*SR))/SR
        kick=np.sin(2*np.pi*(90*times-26*times*times))*np.exp(-times*26)*.22
        add(kick,when)
        snare=rng.standard_normal(len(times))*np.exp(-times*41)*.06
        add(snare,when+beat/2)
        add(note(pitches[(i//4)%4],.3),when)
        add(note(pitches[(i//4)%4]*2,.16,.025),when+beat*.62)
    for shot in episode["shots"][1:]:
        add(note(670,.15,.07),shot["start"])
    for shot in episode["shots"]:
        if shot["kind"]=="system":
            for ix in range(3):
                add(note((520,390,260)[ix],.24,.10),shot["start"]+ix*.2)
        elif shot.get("effect")=="panic":
            for ix in range(4):
                add(note(110+110*ix,.3,.10),shot["start"]+.03+ix*.13)
    if tts=="placeholder":
        with tempfile.TemporaryDirectory() as temp:
            for i,shot in enumerate(episode["shots"]):
                phrase=shot.get("voice")
                if not phrase or shot["start"]>=duration:continue
                target=Path(temp)/f"voice-{i}.wav"
                subprocess.run(["espeak-ng","-v","zh","-s","185","-p","62","-a","150","-w",str(target),phrase],
                    check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
                with wave.open(str(target),"rb") as reader:
                    hz=reader.getframerate()
                    channels=reader.getnchannels()
                    if reader.getsampwidth()!=2:raise RuntimeError("Unsupported eSpeak PCM format")
                    pcm=np.frombuffer(reader.readframes(reader.getnframes()),dtype="<i2").astype(np.float32)/32768
                if channels>1:pcm=pcm.reshape(-1,channels).mean(axis=1)
                n=int(len(pcm)*SR/hz)
                if n<1:continue
                y=np.interp(np.arange(n)*hz/SR,np.arange(len(pcm)),pcm).astype(np.float32)
                allowed=int(max(0,shot["end"]-shot["start"]-.28)*SR)
                y=y[:allowed]
                if len(y)>600:
                    fade=min(1200,len(y))
                    y[-fade:]*=np.linspace(1,0,fade,dtype=np.float32)
                add(.26*np.tanh(y*2.5),shot["start"]+.13)
    pcm=(np.clip(np.tanh(data*.83),-1,1)*32767).astype("<i2")
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(output),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(SR)
        wav.writeframes(pcm.tobytes())
