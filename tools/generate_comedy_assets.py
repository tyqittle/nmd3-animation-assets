#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate an ORIGINAL comedy SFX + transparent VFX library.
No third-party audio samples, celebrity voices, stock loops, AI voice or meme rips.
Outputs real editable WAV, RGBA PNG, animated WebP, and zipped PNG frame sequences.
Deterministic (same code + Pillow/numpy versions produce the same content).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import random
import wave
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SEED = 20261021
SR = 32000
FPS = 12
N_FRAMES = 16
SIZE = 360
SFX = [
    ("comic_boom","夸张重击 / Boom","冲击","搞笑BOSS登场、突然大字、反转",1.15,"impact"),
    ("hollow_bonk","敲头咚 / Bonk","冲击","被打脸、敲脑袋、人物撞墙",.57,"bonk"),
    ("rubber_boing","弹簧蹦 / Boing","肢体","角色弹飞、阿力抖动、失误回弹",.88,"boing"),
    ("wrong_answer","答错提示 / Wrong","失败","抽卡歪、字幕打叉、答错题",.72,"wrong"),
    ("sad_trombone","垮掉小号 / Wah wah","失败","空大、抽歪、白忙一场",1.91,"trombone"),
    ("vinyl_stall","刹停唱片 / Scratch","转场","反转暂停、全员沉默、台词打断",.66,"scratch"),
    ("awkward_crickets","尴尬虫鸣 / Crickets","尴尬","冷场、没人接话、社死",2.35,"crickets"),
    ("slow_clap","假装鼓掌 / Claps","尴尬","一本正经的烂理由、反向庆祝",1.80,"claps"),
    ("cartoon_pop","气泡啵 / Pop","肢体","人物突然出现、字幕弹出",.29,"pop"),
    ("whoosh_whip","快速甩镜 / Whoosh","转场","甩镜、瞬移、镜头滑动",.68,"whoosh"),
    ("tiny_victory","塑料胜利号 / Victory","胜利","小战果大庆祝、过度颁奖",1.70,"victory"),
    ("cash_register","到账叮 / Cash","金钱","武器售价、抽卡开销、开店",1.12,"cash"),
    ("keyboard_panic","疯狂按键 / Panic","肢体","临时抱佛脚、狂按技能",1.18,"type"),
    ("duck_squeak","玩具吱 / Squeak","肢体","表情包捏脸、搞怪走路",.70,"squeak"),
    ("descending_whistle","下坠口哨 / Slide","失败","角色出糗、掉下平台",1.14,"whistle"),
    ("suspense_ticks","悬念滴答 / Ticks","悬念","抽卡出货前、技能CD等待",2.10,"ticks"),
    ("error_double_beep","错误双响 / Beeps","失败","技能灰掉、装备不满足",.58,"error"),
    ("sparkle_magic","金闪闪 / Sparkle","胜利","商品闪耀、抽到好货、少女变身",1.19,"sparkle"),
    ("gasp_choir","人群倒吸气 / Faux gasp","惊讶","突然出现大数字、全员震惊",1.03,"gasp"),
    ("drum_rimshot","冷笑话鼓点 / Rimshot","尴尬","烂梗说完，主动补上鼓点",1.45,"rimshot"),
    ("heart_thump","心跳紧张 / Thump","悬念","残血躲技能、等判定",1.72,"heart"),
    ("cartoon_splat","糊脸啪 / Splat","冲击","正面拍墙、事故现场",.61,"splat"),
    ("retro_levelup","像素升级 / Level up","胜利","角色觉醒、成就、进度暴涨",1.67,"level"),
    ("laser_zap","离谱激光 / Zap","惊讶","战斗鬼畜、人物眼神放光",.86,"zap"),
]
VFX = [
    ("comic_impact","漫画冲击波","冲击","打脸、爆炸、Boss拍脸","impact"),
    ("question_swarm","疑问号乱飞","表情","听到离谱台词、怀疑人生","question"),
    ("sweat_drop","巨型冷汗","表情","被拆穿、尴尬、社死","sweat"),
    ("rage_veins","怒气青筋","表情","玩家上火、怒火值上升","rage"),
    ("speed_streaks","飞速残影","动作","鬼畜加速、闪现、冲刺","speed"),
    ("gold_sparkles","金光四射","氛围","抽卡出货、武器展示","sparkle"),
    ("fire_burst","爆笑炸裂火花","冲击","夸张打击、武器大招","fire"),
    ("smoke_poof","烟雾砰一声","氛围","角色消失、翻车烟尘","smoke"),
    ("freeze_shatter","定格碎裂","转场","音乐刹车、社死定格","freeze"),
    ("confetti_party","离谱庆祝彩纸","氛围","抽出SSR、倒霉后硬庆祝","confetti"),
    ("heart_pop","爱心砰砰","表情","喜欢角色、甜蜜或反差","heart"),
    ("spotlight_reveal","登场聚光圈","转场","大人物现身、商品揭晓","spotlight"),
    ("giant_alert","红灯警告","惊讶","下饭操作、爆雷、抽数超支","alert"),
    ("exclaim_bounce","感叹号弹跳","表情","看到意外结果、惊讶","exclaim"),
    ("dust_trail","摔倒烟尘","动作","跑偏、角色摔倒、技能落空","dust"),
    ("money_shower","金币倾泻","金钱","付费狂砸、钱包空了","coins"),
]

def envelope(n, attack=.012, release=.20):
    e=np.ones(n,dtype=np.float64)
    at=min(n,max(1,int(attack*SR))); rt=min(n,max(1,int(release*SR)))
    e[:at]*=np.linspace(0,1,at,endpoint=True)
    e[-rt:]*=np.linspace(1,0,rt,endpoint=True)
    return e

def one_tone(n,f0,f1=None,overtones=(1,.23,.11), vibrato=0):
    f=np.linspace(f0,f0 if f1 is None else f1,n,dtype=np.float64)
    if vibrato:f+=np.sin(np.arange(n)*2*math.pi*5.1/SR)*vibrato
    phase=2*math.pi*np.cumsum(f)/SR
    return sum((amp*np.sin(phase*k) for k,amp in enumerate(overtones,1)))

def add(a,b,at,gain=1):
    begin=max(0,int(round(at*SR)))
    n=min(len(a)-begin,len(b))
    if n>0:a[begin:begin+n]+=b[:n]*gain

def note(f,dur,amp=.5,waveform="bell",decay=8):
    n=max(1,int(SR*dur))
    t=np.arange(n,dtype=np.float64)/SR
    if waveform=="brass": s=one_tone(n,f,overtones=(1,.48,.28,.15),vibrato=1.7)
    elif waveform=="square":
        s=np.tanh(2.5*one_tone(n,f,overtones=(1,.44,.22)))
    else: s=one_tone(n,f,overtones=(1,.32,.18))
    return s*amp*np.exp(-t*decay)*envelope(n,.007,min(.12,dur*.3))

def build_sound(kind,seconds,seed):
    rng=np.random.default_rng(seed);n=int(round(SR*seconds))
    t=np.arange(n,dtype=np.float64)/SR
    x=np.zeros(n,dtype=np.float64)
    if kind in ("impact","bonk","splat"):
        freq={"impact":65,"bonk":152,"splat":91}[kind]
        wobble=np.exp(-t*14)
        x+=one_tone(n,freq*1.8,freq*.55,overtones=(1,.53,.18))*wobble*.75
        x+=rng.standard_normal(n)*np.exp(-t*{"impact":19,"bonk":40,"splat":15}[kind])*.4
        if kind=="splat":
            for i in range(5):add(x,note(320+i*52,.1,.19),.018+i*.035)
    elif kind=="boing":
        phase=2*math.pi*np.cumsum(200+480*np.exp(-t*5)*np.cos(t*2*math.pi*5))/SR
        x=np.sin(phase)*(.85*np.exp(-t*2.8))+np.sin(phase*2)*.15*np.exp(-t*5)
    elif kind=="wrong":
        add(x,note(389,.34,.7,"square",3),0)
        add(x,note(190,.42,.8,"square",3),.25)
    elif kind=="trombone":
        for i,f in enumerate((330,294,277,220)):
            at=(0,.43,.86,1.28)[i]; d=(.47,.46,.46,.62)[i]
            add(x,note(f,d,.56,"brass",2.3),at)
        x+=rng.standard_normal(n)*.008*np.exp(-t)
    elif kind=="scratch":
        # Synthesized aperiodic filtered noise + variable frequency. No vinyl sample.
        noise=rng.standard_normal(n)
        smooth=np.convolve(noise,np.ones(11)/11,mode="same")
        f=650+340*np.sin(2*math.pi*(4.2*t+7*t*t))
        x=np.sin(2*math.pi*np.cumsum(f)/SR)*.35+smooth*.72
        x*=np.exp(-t*4.1)
    elif kind=="crickets":
        for i in range(9):
            start=.08+i*.242
            length=.065 if i%3 else .1
            chirp=note(3520+i%4*260,length,.40,"bell",13)
            add(x,chirp,start)
            add(x,chirp,start+.08,.76)
        x+=rng.standard_normal(n)*.008
    elif kind=="claps":
        for i in range(4):
            at=.12+i*.43
            nn=int(.23*SR)
            noise=rng.standard_normal(nn)
            # Timbre built from independent narrow, decaying bursts.
            env=np.exp(-np.arange(nn)/SR*25)
            burst=(noise-np.convolve(noise,np.ones(7)/7,mode="same"))*env*.22
            add(x,burst,at)
    elif kind=="pop":
        x=one_tone(n,760,280,overtones=(1,.22,.07))*np.exp(-t*28)
        x+=rng.standard_normal(n)*.10*np.exp(-t*70)
    elif kind=="whoosh":
        noise=rng.standard_normal(n)
        kernel=np.ones(17)/17
        low=np.convolve(noise,kernel,mode="same")
        x=(low*.78+one_tone(n,180,1150)*.14)*np.sin(np.pi*t/seconds)**2
    elif kind=="victory":
        for i,(f,d) in enumerate(((523,.20),(660,.20),(785,.19),(1047,.57))):
            add(x,note(f,d,.45,"brass",2.2),(.08,.37,.65,.93)[i])
    elif kind=="cash":
        for i,f in enumerate((920,1380,1840)):
            add(x,note(f,.5,.29,"bell",6),.08+i*.13)
        add(x,note(190,.2,.19,"square",8),.04)
    elif kind=="type":
        for i in range(17):
            at=.02+i*.061+float(rng.uniform(-.009,.009))
            f=float(rng.uniform(240,560))
            add(x,note(f,.052,.20,"square",34),at)
    elif kind=="squeak":
        x=one_tone(n,920,250,overtones=(1,.42,.28))*np.exp(-t*4.5)
        x*=1+.3*np.sin(2*math.pi*18*t)
    elif kind=="whistle":
        f=1400*np.exp(-t*1.8)+180
        phase=2*math.pi*np.cumsum(f)/SR
        x=(np.sin(phase)+np.sin(phase*2)*.06)*.60*envelope(n,.06,.23)
    elif kind=="ticks":
        for i in range(6):
            add(x,note(980 if i%2==0 else 680,.068,.32),.1+i*.32)
        x+=one_tone(n,44)*.015
    elif kind=="error":
        for at in (.05,.31):
            add(x,note(310,.21,.56,"square",5),at)
    elif kind=="sparkle":
        freqs=[720,960,1280,1568,2092,2637]
        for i,f in enumerate(freqs):
            add(x,note(f,.30,.31,"bell",9),.045+i*.16)
    elif kind=="gasp":
        # Formant-ish synthetic exhalation, intentionally NOT a human voice recording.
        filt=np.convolve(rng.standard_normal(n),np.ones(32)/32,mode="same")
        form=np.sin(2*math.pi*(190*t+48*t*t))
        x=(filt*.8+form*.15)*np.sin(np.pi*t/seconds)**1.2
    elif kind=="rimshot":
        add(x,note(140,.25,.35,"square",19),.05)
        add(x,note(220,.24,.35,"square",16),.13)
        add(x,rng.standard_normal(int(.2*SR))*np.exp(-np.arange(int(.2*SR))/SR*35)*.25,.34)
        add(x,note(490,.55,.32,"bell",6),.60)
    elif kind=="heart":
        for i in range(3):
            at=.08+i*.55
            add(x,note(72,.26,.60,"bell",17),at)
            add(x,note(65,.26,.50,"bell",16),at+.15)
    elif kind=="level":
        seq=[262,330,392,523,659,784,1047]
        for i,f in enumerate(seq):add(x,note(f,.31,.30,"square",4),i*.18)
    elif kind=="zap":
        x=one_tone(n,2300,85,overtones=(1,.5,.35))*np.exp(-t*5)
        x+=rng.standard_normal(n)*.16*np.exp(-t*23)
    else:
        raise ValueError("Unknown synth "+kind)
    # Attack/release, correct peak normalization, and no clipped int16 samples.
    x*=envelope(n,.006,min(.13,seconds*.12))
    peak=float(np.max(np.abs(x))) if n else 0
    if peak < .000001: raise AssertionError("Sound is silent")
    x=np.tanh(x/max(.1,peak)*1.3)
    x*=.89/max(1e-9,float(np.max(np.abs(x))))
    # Add tiny fadeout if the waveform is nonzero at the very end.
    return np.asarray(np.round(x*32767),dtype="<i2")

def save_wav(path,array):
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(array.tobytes())

def I(v):
    return int(round(v))

def draw_vfx(kind,frame):
    im=Image.new("RGBA",(SIZE,SIZE),(0,0,0,0))
    d=ImageDraw.Draw(im,"RGBA")
    t=frame/max(1,N_FRAMES-1)
    u=1-(1-t)**3
    cx=SIZE//2;cy=SIZE//2
    rng=random.Random(884+frame//4)
    def circ(x,y,r,fill,outline=None,width=1):
        if r<=0:return
        d.ellipse((I(x-r),I(y-r),I(x+r),I(y+r)),fill=fill,outline=outline,width=max(1,I(width)))
    def poly(pts,color):
        d.polygon([(I(x),I(y)) for x,y in pts],fill=color)
    def ray(x,y,angle,length,width,color):
        vx,vy=math.cos(angle),math.sin(angle)
        poly([(x-vy*width/2,y+vx*width/2),(x+vy*width/2,y-vx*width/2),
              (x+vx*length+vy*width*.2,y+vy*length-vx*width*.2),
              (x+vx*length-vy*width*.2,y+vy*length+vx*width*.2)],color)
    fade=min(1,t*6,(1-t)*5)
    fa=lambda a:I(max(0,min(255,a*fade)))
    if kind=="impact":
        for j in range(3):
            r=30+u*(90+j*40)
            circ(cx,cy,r,(0,0,0,0),(251,200-j*25,60+j*20,fa(220-j*35)),max(2,12-j*3))
        for j in range(16):
            ang=j*math.tau/16+frame*.03
            ray(cx,cy,ang,70+u*105+(j%3)*11,5+(j%4)*2,(255,225-j%5*19,93,fa(245)))
        circ(cx,cy,25*(1-t)+6,(255,250,178,fa(210)))
    elif kind=="question":
        for j in range(7):
            x=70+(j%4)*76+17*math.sin(j+t*7)
            y=270-(j//4)*120-t*(78+j*6)
            color=(247,195,83,fa(240)) if j%2 else (231,236,252,fa(220))
            # hand-drawn question-mark silhouette
            circ(x,y-23,12,(0,0,0,0),color,7)
            d.arc((I(x-12),I(y-35),I(x+12),I(y-11)),200,35,fill=color,width=7)
            d.line((I(x+8),I(y-10),I(x),I(y+12)),fill=color,width=7)
            circ(x,y+25,4,color)
    elif kind=="sweat":
        scale=math.sin(t*math.pi)**.65
        for j in range(4):
            x=80+j*70+10*math.sin(j*4)
            y=48+j*25+180*t
            w=(24+j*4)*scale;h=(48+j*7)*scale
            poly([(x,y-h),(x-w*.8,y+h*.2),(x,y+h),(x+w*.8,y+h*.2)],(102,215,252,fa(222)))
            circ(x-w*.18,y+h*.2,w*.24,(213,249,255,fa(170)))
    elif kind=="rage":
        for j in range(5):
            ang=j*math.tau/5+.2
            x=cx+115*math.cos(ang);y=cy+115*math.sin(ang)
            rr=1+.2*math.sin(t*11+j)
            pts=[(x-22*rr,y-10),(x-3,y-10),(x+3,y-32*rr),
                 (x+8,y-10),(x+26,y-10),(x+25,y+9),
                 (x+10,y+9),(x+2,y+28*rr),(x-7,y+8),(x-22,y+8)]
            poly(pts,(235,60,64,fa(235)))
            d.line(pts+[pts[0]],fill=(100,22,23,fa(180)),width=3)
    elif kind=="speed":
        for j in range(21):
            ang=j*math.tau/21
            start=55+(j%3)*12+12*math.sin(t*7+j)
            length=115+50*t+(j%5)*4
            ray(cx+math.cos(ang)*start,cy+math.sin(ang)*start,ang,length,4+j%3*2,
                (255,244,215,fa(220 if j%2 else 160)))
    elif kind=="sparkle":
        for j in range(24):
            a=j*2.3999
            r=40+(j%6)*21+70*u
            x=cx+math.cos(a)*r;y=cy+math.sin(a)*r
            q=3+j%3*3
            poly([(x,y-q*2),(x+q/2,y-q/2),(x+q*2,y),
                  (x+q/2,y+q/2),(x,y+q*2),(x-q/2,y+q/2),
                  (x-q*2,y),(x-q/2,y-q/2)],(255,234-j%4*28,102,fa(250)))
    elif kind=="fire":
        for j in range(16):
            a=j*math.tau/16
            r=26+u*(100+j%4*13)
            poly([(cx+math.cos(a)*25,cy+math.sin(a)*25),
                 (cx+math.cos(a+.1)*r,cy+math.sin(a+.1)*r),
                 (cx+math.cos(a+.18)*30,cy+math.sin(a+.18)*30)],
                 (255,100+j%5*18,45,fa(225)))
        circ(cx,cy,58*(1-t)+6,(255,235,105,fa(210)))
        for j in range(9):
            x=45+j*34+15*math.sin(j);y=280-t*160-j%4*11
            poly([(x,y+14),(x-7,y+3),(x+5,y-17),(x+10,y+5)],
                 (255,120+j%5*18,47,fa(200)))
    elif kind in ("smoke","dust"):
        for j in range(12):
            a=j*math.tau/12
            x=cx+math.cos(a)*(20+u*(77+j%4*12))
            y=cy+math.sin(a)*(17+u*(65+j%3*14))-(35*u if kind=="smoke" else 0)
            radius=(25+j%4*8)*(.55+.5*math.sin(math.pi*t))
            shade=(178,183,193,fa(153)) if kind=="smoke" else (212,177,120,fa(182))
            circ(x,y,radius,shade)
    elif kind=="freeze":
        for j in range(12):
            a=j*math.tau/12+.1
            r1=22+u*(j%4*4);r2=175*u+19
            xx=cx+math.cos(a)*r1;yy=cy+math.sin(a)*r1
            x=cx+math.cos(a)*r2;y=cy+math.sin(a)*r2
            d.line((I(xx),I(yy),I(x),I(y)),fill=(157,238,255,fa(235)),width=2+j%3)
            if j%2==0:
                zz=r1+(r2-r1)*.58
                bx=cx+math.cos(a)*zz;by=cy+math.sin(a)*zz
                for da in (-.55,.65):
                    d.line((I(bx),I(by),I(bx+24*math.cos(a+da)),I(by+24*math.sin(a+da))),
                           fill=(217,249,255,fa(200)),width=3)
    elif kind=="confetti":
        for j in range(54):
            x=((j*127+43)%340+10+36*math.sin(j+2*t))%360
            y=((j*83+frame*16)%440)-45
            size=4+j%4*3
            col=[(247,101,101),(247,204,88),(103,208,238),(184,130,231)][j%4]
            poly([(x,y),(x+size,y+size/3),(x+size+2,y+size+5),(x+1,y+size+2)],
                 col+(fa(230),))
    elif kind=="heart":
        for j in range(14):
            a=j*2.4
            r=35+150*u*(.5+j%4*.14)
            x=cx+math.cos(a)*r;y=cy+math.sin(a)*r
            size=7+j%4*5
            color=(255,93+j%3*22,145,fa(236))
            circ(x-size*.5,y-size*.35,size*.56,color)
            circ(x+size*.5,y-size*.35,size*.56,color)
            poly([(x-size,y),(x+size,y),(x,y+size*1.35)],color)
    elif kind=="spotlight":
        r=35+135*smoothstep(t)
        circ(cx,cy,r,(251,217,109,fa(18)),(251,231,148,fa(225)),max(3,12-I(t*5)))
        for j in range(12):
            a=j*math.tau/12+t*.1
            ray(cx,cy,a,180+40*math.sin(t*3+j),3,(255,244,195,fa(140)))
    elif kind=="alert":
        for j in range(4):
            r=44+u*50+j*25
            circ(cx,cy,r,(0,0,0,0),(255,64,66,fa(180-j*27)),max(2,12-j*2))
        poly([(cx,cy-93),(cx-77,cy+58),(cx+77,cy+58)],(242,69,61,fa(240)))
        d.line((cx,cy-42,cx,cy+11),fill=(255,255,230,fa(255)),width=16)
        circ(cx,cy+35,9,(255,255,230,fa(255)))
    elif kind=="exclaim":
        bounce=24*abs(math.sin(t*math.pi*2.2))*(1-t)
        scale=.5+.8*math.sin(math.pi*min(t,1))**.65
        for j in range(3):
            x=110+j*72;y=180-bounce+14*math.sin(j*2)
            poly([(x-12*scale,y-95*scale),(x+12*scale,y-95*scale),
                  (x+7*scale,y+20*scale),(x-7*scale,y+20*scale)],
                 (255,229-j*34,105,fa(240)))
            circ(x,y+53*scale,10*scale,(255,221,100,fa(240)))
    elif kind=="coins":
        for j in range(24):
            x=(j*71+30+30*math.sin(t*5+j))%360
            y=((j*107+frame*29)%445)-52
            rr=8+j%5*3
            circ(x,y,rr,(243,181,52,fa(232)),(255,245,145,fa(238)),max(1,rr//4))
            d.line((I(x),I(y-rr*.65),I(x),I(y+rr*.65)),fill=(161,92,36,fa(225)),width=2)
    else: raise ValueError(kind)
    return im

def smoothstep(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def asset_record(path,relative,kind,asset_id,name,category,description,duration=None):
    data=path.read_bytes()
    record={
        "id":asset_id, "name":name, "kind":kind,"category":category,
        "description":description,"path":relative,
        "bytes":len(data),"sha256":hashlib.sha256(data).hexdigest(),
        "origin":"synthesized_from_original_code",
        "license_note":"本仓库自制无外来录音/采样；不代表游戏官方授权"
    }
    if duration is not None:record["seconds"]=duration
    return record

def build(dest):
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"sfx").mkdir(exist_ok=True)
    (dest/"vfx").mkdir(exist_ok=True)
    sounds=[];effects=[]
    for i,(ident,name,category,description,sec,engine) in enumerate(SFX):
        wav=build_sound(engine,sec,SEED+i*97)
        p=dest/"sfx"/(ident+".wav")
        save_wav(p,wav)
        info=asset_record(p,"sfx/"+p.name,"sound",ident,name,category,description,sec)
        info.update({"sample_rate":SR,"channels":1,"bit_depth":16,"mime":"audio/wav","use_at":["cut","reaction","comic timing"]})
        sounds.append(info)
    for ident,name,category,description,engine in VFX:
        frames=[draw_vfx(engine,i) for i in range(N_FRAMES)]
        cover=dest/"vfx"/(ident+".png")
        frames[5].save(cover,optimize=True)
        anim=dest/"vfx"/(ident+".webp")
        frames[0].save(anim,save_all=True,append_images=frames[1:],duration=[round(1000/FPS)]*N_FRAMES,
                       loop=0,lossless=True,method=5)
        seq=dest/"vfx"/(ident+"_frames.zip")
        with zipfile.ZipFile(seq,"w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for i,fr in enumerate(frames):
                buf=io.BytesIO();fr.save(buf,format="PNG",optimize=True)
                z.writestr(f"{ident}_{i:03d}.png",buf.getvalue())
        # Fade-in/out animation is allowed to have a FULLY transparent first or last frame.
        # Midway frames MUST contain visible content and at least some transparent pixels.
        for fi,fr in enumerate(frames):
            if fr.mode!="RGBA":raise AssertionError("Alpha missing")
            aa=fr.getchannel("A");hist=aa.getextrema()
            if hist[0] != 0:raise AssertionError(f"Background not transparent {ident}:{fi}:{hist}")
            if 4 <= fi <= 10 and hist[1]==0:
                raise AssertionError(f"Missing visible middle frame {ident}:{fi}:{hist}")
        if Image.open(anim).n_frames!=N_FRAMES:
            raise AssertionError("WebP not really animated: "+ident)
        effects.append({
            **asset_record(anim,"vfx/"+anim.name,"effect",ident,name,category,description,N_FRAMES/FPS),
            "poster":"vfx/"+cover.name,"frames_zip":"vfx/"+seq.name,"frame_count":N_FRAMES,
            "fps":FPS,"size":[SIZE,SIZE],"has_alpha":True,
            "format":"animated_webp","editing_source":"transparent_png_sequence_zip",
            "poster_sha256":hashlib.sha256(cover.read_bytes()).hexdigest(),
            "frames_zip_sha256":hashlib.sha256(seq.read_bytes()).hexdigest()
        })
    # A reusable JSON manifest is the single source of truth for the browser.
    catalog={
        "schema_version":"1.0.0","library":"NMD3 comedy-editing SFX & VFX",
        "generated_on":"2026-10-21",
        "generator":"tools/generate_comedy_assets.py",
        "summary":{"sfx":len(sounds),"animated_vfx":len(effects),"total":len(sounds)+len(effects)},
        "audio_specs":{"format":"wav","sample_rate":SR,"channels":1,"bits_per_sample":16},
        "vfx_specs":{"preview_format":"animated_webp","editing_format":"zip_png_rgba_frames","still_format":"png_rgba","size":SIZE,"fps":FPS,"frames":N_FRAMES},
        "provenance":"All sounds and vector shapes are freshly synthesized/drawn by included code, not extracted from popular clips. Third-party game assets are NOT embedded.",
        "notes":"描述里的热门音效类型仅是剪辑场景参考，不表示获得相应流行录音版权，也不宣称等同原版。",
        "sounds":sounds,"effects":effects
    }
    (dest/"catalog.json").write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    with zipfile.ZipFile(dest/"comedy-sfx-24-wav.zip","w",zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for item in sounds:z.write(dest/item["path"],item["path"])
    # Reproducibility and audit counts
    total_bytes=sum(p.stat().st_size for p in dest.rglob("*") if p.is_file())
    print(json.dumps({"sounds":len(sounds),"effects":len(effects),"bytes":total_bytes,
                      "wav_zip":str(dest/"comedy-sfx-24-wav.zip")},ensure_ascii=False),flush=True)

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="assets/comedy")
    args=parser.parse_args()
    build(Path(args.output))
