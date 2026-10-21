#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Make a reusable ORIGINAL 'mambo!' meme-inspired vocal SFX add-on.

The Japanese/CN phrases are newly spoken by neutral generic neural TTS.
NO Umamusume voice samples, RVC character impersonation, Bilibili rips,
memetic copyrighted audio, or sampled third-party music are included.

Prerequisites: numpy, edge-tts CLI, ffmpeg. Fail loudly if actual voice
synthesis fails: do not silently publish synthetic nonverbal placeholders.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import tempfile
import wave
import zipfile
from pathlib import Path
import numpy as np

SR=32000
BASE_PHRASES={
    "ja_one":("ja-JP-NanamiNeural","マンボ！"),
    "ja_two":("ja-JP-NanamiNeural","マンボ、マンボ！"),
    "zh_one":("zh-CN-XiaoxiaoNeural","曼波！"),
    "zh_three":("zh-CN-XiaoxiaoNeural","曼波，曼波，曼波！"),
    "zh_ask":("zh-CN-YunxiNeural","曼波？"),
}
RECIPES=[
    ("mambo_ja_single","曼波！·日语单发","ja_one","plain",1.0,"短促呆萌，适合角色突然出场","出场"),
    ("mambo_ja_double","曼波曼波！·双连","ja_two","plain",1.0,"被动整活、连续小失误","重复"),
    ("mambo_zh_single","曼波！·中文单发","zh_one","plain",1.0,"中文向短剧的反应音","出场"),
    ("mambo_zh_triple","曼波×3 · 洗脑三连","zh_three","plain",1.0,"三连抽卡、反复横跳","重复"),
    ("mambo_fast","高速曼波 · 1.45倍","ja_two","fast",1.45,"加速乱斗、技能连点","变速"),
    ("mambo_slow","迟钝曼波 · 慢放","ja_one","slow",0.74,"反应慢半拍、惊呆凝固","变速"),
    ("mambo_helium","尖声曼波 · 高音","zh_one","helium",1.35,"可爱夸张、角色蹦起","变声"),
    ("mambo_deep","低音曼波 · 震惊","ja_one","deep",0.80,"Boss反应、严肃怪话","变声"),
    ("mambo_echo","空谷曼波 · 回声","ja_one","echo",1.0,"一人整活全村回应","空间"),
    ("mambo_robot","机械曼波 · 故障","zh_three","robot",1.0,"机械Boss、抽象AI、鬼畜","鬼畜"),
    ("mambo_win","出货曼波 · 喜报","ja_two","win",1.0,"UP出货、领奖庆祝","奖励"),
    ("mambo_fail","空大曼波 · 败北","ja_two","fail",1.0,"空大、技能歪、抽卡歪","失败"),
    ("mambo_alarm","警告曼波 · 紧急","zh_one","alarm",1.0,"Boss登场、血量警告","警告"),
    ("mambo_stutter","抽搐曼波 · 卡顿","ja_two","stutter",1.0,"角色鬼畜反复、卡壳反应","鬼畜"),
]

def quote_seconds(samples):
    return round(len(samples)/SR,3)

def fade(audio,fade_in=.014,fade_out=.07):
    x=np.array(audio,dtype=np.float64,copy=True)
    n=len(x)
    if n==0:raise ValueError("empty voice")
    a=min(n//3,max(1,round(fade_in*SR)))
    b=min(n//3,max(1,round(fade_out*SR)))
    x[:a]*=np.linspace(0,1,a)
    x[-b:]*=np.linspace(1,0,b)
    return x

def load_voice(mp3):
    data=subprocess.run(
        ["ffmpeg","-v","error","-i",str(mp3),"-ac","1","-ar",str(SR),
         "-f","f32le","pipe:1"],
        check=True,capture_output=True,timeout=75).stdout
    x=np.frombuffer(data,dtype="<f4").astype(np.float64)
    if len(x)<1000:raise RuntimeError("TTS voice is too short")
    valid=np.flatnonzero(np.abs(x)>.005)
    if valid.size<700:raise RuntimeError("TTS is silent")
    l=max(0,int(valid[0])-round(.055*SR));r=min(len(x),int(valid[-1])+round(.090*SR))
    return fade(x[l:r])

def create_sources(tmp):
    sources={}
    for key,(voice,phrase) in BASE_PHRASES.items():
        mp3=tmp/(key+".mp3")
        subprocess.run([
            "edge-tts","--voice",voice,"--rate","+6%",
            "--text",phrase,"--write-media",str(mp3)],
            check=True,capture_output=True,timeout=90)
        sources[key]=load_voice(mp3)
        print("VOICE",key,phrase,round(len(sources[key])/SR,2),"sec",flush=True)
    return sources

def resample_speed(x,rate):
    if rate<=0:raise ValueError("invalid rate")
    src=np.arange(len(x),dtype=np.float64)
    pos=np.arange(0,len(x)-1,rate,dtype=np.float64)
    return np.interp(pos,src,x)

def padded(n):
    return np.zeros(int(n),dtype=np.float64)

def add(x,source,seconds,gain=1):
    i=max(0,int(seconds*SR))
    end=min(len(x),i+len(source))
    if end>i:x[i:end]+=np.asarray(source[:end-i],dtype=np.float64)*gain

def tone(freq,seconds,vol=.12,kind="bell"):
    n=max(1,int(seconds*SR))
    t=np.arange(n,dtype=np.float64)/SR
    envelope=np.minimum(1,t*120)*np.exp(-t*(5 if kind=="bell" else 10))
    phase=2*math.pi*freq*t
    return (np.sin(phase)+(0.22 if kind=="bell" else 0.40)*np.sin(2*phase))*vol*envelope

def extra(x,style):
    x=np.array(x,dtype=np.float64)
    if style=="plain":
        out=np.concatenate([x,padded(.08*SR)])
    elif style=="fast":
        out=np.concatenate([x,padded(.04*SR)])
        # Add rhythmic original plucks under the voice, not borrowed music.
        for i in range(3):add(out,tone(260+i*93,.10,.075),i*.18)
    elif style=="slow":
        out=np.concatenate([x,padded(.16*SR)])
    elif style in ("helium","deep"):
        out=np.concatenate([x,padded(.12*SR)])
    elif style=="echo":
        out=padded(len(x)+int(.78*SR))
        for when,gain in [(0,1),(.17,.45),(.35,.24),(.54,.13)]:
            add(out,x,when,gain)
    elif style=="robot":
        t=np.arange(len(x))/SR
        # Ring modulator adds cartoon robot timbre but leaves speech intelligible.
        x=x*(.70+.30*np.sin(2*math.pi*24*t))
        out=np.concatenate([x,padded(.08*SR)])
        for i in range(4):add(out,tone(520+i*70,.13,.06),i*.3)
    elif style=="win":
        out=padded(len(x)+int(.6*SR))
        add(out,x,.12,.93)
        for i,fr in enumerate((523.25,659.25,783.99,1046.5)):
            add(out,tone(fr,.22,.12),.06+i*.23)
    elif style=="fail":
        out=padded(len(x)+int(.75*SR))
        add(out,x,0,.86)
        for i,fr in enumerate((349,294,220,164)):
            add(out,tone(fr,.34,.13),max(0,len(x)/SR-.21)+i*.18)
    elif style=="alarm":
        out=padded(len(x)+int(.65*SR))
        add(out,x,.18,.87)
        for when in (.03,.46,.92):
            add(out,tone(750,.21,.25,kind="buzzer"),when)
    elif style=="stutter":
        out=padded(len(x)+int(.62*SR))
        # Repeat only a short ORIGINAL neural-TTS onset, then finish full utterance.
        snippet=x[:min(len(x),int(.19*SR))]
        for when in (.0,.19,.38):
            add(out,snippet,when,.75)
        add(out,x,.57,.9)
    else:raise ValueError("unknown style "+style)
    out=fade(out)
    if not np.isfinite(out).all() or float(np.max(np.abs(out)))<.015:
        raise RuntimeError("silent or invalid audio "+style)
    # Compressor with consistent ceiling, no clipping or hard limiter.
    out=np.tanh(out*1.8)
    out*=.82/max(.01,float(np.max(np.abs(out))))
    return np.asarray(np.round(out*32767),dtype="<i2")

def wav_to(path,samples):
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR)
        f.writeframes(samples.tobytes())
    with wave.open(str(path),"rb") as f:
        assert f.getnframes()==len(samples) and f.getframerate()==SR

def write_library(dest):
    dest.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        voices=create_sources(Path(temp))
    items=[]
    for ident,name,source,style,rate,usage,category in RECIPES:
        x=resample_speed(voices[source],rate)
        result=extra(x,style)
        path=dest/(ident+".wav")
        wav_to(path,result)
        sec=quote_seconds(result)
        info={
            "id":ident,"name":name,"kind":"sound","category":"曼波",
            "sub_category":category,
            "description":usage,
            "path":"mambo/"+path.name,
            "bytes":path.stat().st_size,
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "origin":"new_neural_tts_voice_and_self_synthesized_processing",
            "voice_engine":"edge-tts",
            "voice_model":BASE_PHRASES[source][0],
            "spoken_text":BASE_PHRASES[source][1],
            "original_game_voice":False,
            "copyright_notice":"自制中性TTS改编音效，非诗歌剧原声，不复刻特定声优，不包含他人音频；使用时遵守语音服务及游戏二创条款",
            "seconds":sec,"sample_rate":SR,"channels":1,
            "bit_depth":16,"mime":"audio/wav",
            "use_at":["cut","reaction","meme commentary"],
            "tags":["曼波","诗歌剧相关网络梗","自制配音","鬼畜短剧",category],
        }
        items.append(info)
    zippath=dest/"mambo-sfx-14-wav.zip"
    with zipfile.ZipFile(zippath,"w",zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for item in items:
            p=dest/Path(item["path"]).name
            z.write(p,p.name)
    doc={
        "schema_version":"1.0.0","library":"NMD3 Mambo-inspired original speech editing kit",
        "generated_on":"2026-10-21",
        "generator":"tools/generate_mambo_sfx.py",
        "summary":{"sfx":len(items),"animated_vfx":0,"total":len(items)},
        "reference_sources":[
            {"title":"诗歌剧活全家音效合集 / 仅供梗文化溯源，不提供下载",
             "url":"https://www.bilibili.com/video/BV13T421k732/","original_audio_imported":False},
            {"title":"曼波音效门类及多种变奏 / 仅供归类与名词参考",
             "url":"https://www.aigei.com/sound/class/man_bo_bu_1/","original_audio_imported":False}
        ],
        "notice":"14个WAV均含新合成的「曼波」可辨语音，声音来自常规TTS神经人声而不是赛马娘游戏原声/二创UP主原声；与原梗声线不等同。无第三方音乐。不得宣传为官方配音。",
        "notes":"该分包与 assets/comedy/catalog.json 合并显示，不修改原24个音效和16种特效。不同TTS服务版本生成可能略有变化，元数据和 SHA256 反映本次实际文件。",
        "sounds":items,"effects":[]
    }
    (dest/"catalog.json").write_text(json.dumps(doc,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("GENERATED",len(items),"real vocal WAV clips;",
          sum(o["bytes"] for o in items),"audio bytes; zip",zippath.stat().st_size,flush=True)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",default="assets/comedy/mambo")
    args=ap.parse_args()
    write_library(Path(args.output))
