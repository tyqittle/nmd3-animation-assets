#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小椒卖焚天：贵是贵了点，但不烧心 — independent comic film.
Uses real locally stored Ninja Must Die 3 portraits and weapon imagery.
Fictional dialogue, fictional fire accident; no claims about actual game stats.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
DURATION = 37.0
ASSETS = {
    "seller": ROOT / "assets/characters/xiaojiao_01.png",
    "buyer": ROOT / "assets/characters/xiaohei_01.png",
    "weapon": ROOT / "assets/weapons/wiki/wiki_weapon_101_fentian.png",
    "bailian": ROOT / "assets/weapons/wiki/wiki_weapon_102_bailian.png",
    "location": ROOT / "assets/backgrounds/wallpaper_rooftop_01.jpg",
}
FONT_REG = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]
FONT_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
]
LINES = [
    (0.65, "忍村新开了一家兵器铺。", "zh-CN-YunyangNeural"),
    (3.25, "百炼便宜，先整一把！", "zh-CN-YunxiNeural"),
    (6.4, "哎？这锤还得自己接？", "zh-CN-YunxiNeural"),
    (10.75, "接到了！还得蓄力一秒半？", "zh-CN-YunxiNeural"),
    (15.65, "我刚蓄完力，BOSS跑了！", "zh-CN-YunxiNeural"),
    (19.4, "钱省了，人快烧心了。", "zh-CN-YunxiNeural"),
    (21.8, "来试试焚天，两段都有短暂无敌。", "zh-CN-XiaoxiaoNeural"),
    (25.5, "定身，重劈！这回顺手了！", "zh-CN-YunxiNeural"),
    (28.7, "老板，贵是贵了点，但用着不烧心！", "zh-CN-YunxiNeural"),
    (33.0, "做兵器，先把规矩立住。", "zh-CN-XiaoxiaoNeural"),
]
BEATS = [0, 3.25, 6.4, 10.75, 15.65, 19.4, 21.8, 25.5, 28.7, 33.0]
CREAM = (252, 232, 184)
PAPER = (234, 209, 155)
DARK = (17, 25, 32)
RED = (196, 62, 45)
GOLD = (241, 164, 71)

def cap(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def smooth(x):
    u=cap(x)
    return u*u*(3-2*u)

def spring(x):
    u=cap(x)
    return 1-(1-u)**3 * math.cos(u*9)*.22

def hex_rgba(rgb, a):
    return (rgb[0], rgb[1], rgb[2], int(a))

class Movie:
    def __init__(self, preview=False):
        self.preview=preview
        self.w,self.h,self.fps=(360,640,12) if preview else (720,1280,24)
        self.k=self.w/720
        self.fonts={}
        self.sprites={}
        self.images={}
        self.sprite_cache={}
        for tag, p in ASSETS.items():
            if not p.is_file():
                raise FileNotFoundError("真实原图缺失，拒绝用色块替换: " + str(p))
            im=Image.open(p).convert("RGBA")
            if tag!="location":
                bb=im.getchannel("A").getbbox()
                if bb: im=im.crop(bb)
            self.images[tag]=im
        self.noise=np.random.default_rng(20261021).integers(0,13,(self.h,self.w),dtype=np.uint8)
        # Pre-render a real repository scene as an atmospheric background, not a
        # stretched image occupying the shop's front layer.
        bg=self.images["location"]
        s=max(self.w/bg.width,self.h/bg.height)*1.07
        bg=bg.resize((int(bg.width*s)+2,int(bg.height*s)+2),Image.Resampling.BILINEAR)
        l=max(0,(bg.width-self.w)//2)
        top=max(0,(bg.height-self.h)//2)
        self.roof=bg.crop((l,top,l+self.w,top+self.h)).convert("RGBA")
        overlay=Image.new("RGBA",(self.w,self.h),(13,25,30,190))
        self.roof.alpha_composite(overlay)

    def z(self,x):
        return int(round(x*self.k))

    def font(self,size,bold=False):
        key=(size,bold)
        if key not in self.fonts:
            opts=FONT_BOLD if bold else FONT_REG
            f=next((p for p in opts if Path(p).exists()),None)
            if f is None: raise RuntimeError("缺少可用于中文字幕的 Noto CJK 字体")
            self.fonts[key]=ImageFont.truetype(f,max(8,self.z(size)))
        return self.fonts[key]

    def drawtext(self,im,txt,x,y,size=36,color=CREAM,anchor="mm",stroke=0,bold=True):
        d=ImageDraw.Draw(im,"RGBA")
        d.text((self.z(x),self.z(y)),txt,font=self.font(size,bold),fill=color,
               anchor=anchor,stroke_width=self.z(stroke),stroke_fill=(15,19,21,220))

    def rect(self,im,bbox,fill,outline=None,width=1,radius=0):
        d=ImageDraw.Draw(im,"RGBA")
        b=tuple(self.z(v) for v in bbox)
        if radius:
            d.rounded_rectangle(b, radius=self.z(radius), fill=fill,
                                outline=outline,width=max(1,self.z(width)))
        else:
            d.rectangle(b, fill=fill,outline=outline,width=max(1,self.z(width)))

    def character(self,im,tag,cx,cy,height=550,flip=False,rot=0,opacity=255):
        h=max(1,self.z(height))
        key=(tag,h,flip,opacity)
        if key not in self.sprite_cache:
            src=self.images[tag]
            w=max(1,round(src.width*h/src.height))
            obj=src.resize((w,h),Image.Resampling.LANCZOS)
            if flip: obj=obj.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if opacity!=255:obj.putalpha(obj.getchannel("A").point(lambda v:v*opacity//255))
            self.sprite_cache[key]=obj
        obj=self.sprite_cache[key]
        if rot:obj=obj.rotate(rot,Image.Resampling.BICUBIC,expand=True)
        x=self.z(cx)-obj.width//2
        y=self.z(cy)-obj.height//2
        l=max(0,-x);t=max(0,-y);r=min(obj.width,self.w-x);b=min(obj.height,self.h-y)
        if r>l and b>t:
            im.alpha_composite(obj.crop((l,t,r,b)),(x+l,y+t))

    def particles(self,im,t,kind="dust"):
        d=ImageDraw.Draw(im,"RGBA")
        rng=random.Random(943)
        for i in range(45):
            x=rng.randrange(-30,750) + math.sin(t*(.3+i%7*.02)+i)*14
            speed=.2+(i%4)*.17
            y=(rng.randrange(0,1300)-t*56*speed)%1300
            rad=1.2+(i%3)*.7
            if kind=="ember":
                color=(255,107+min(120,i*4),44,95+(i%3)*45)
                rad+=1
            else:color=(246,184,102,46+(i%3)*18)
            d.ellipse((self.z(x-rad),self.z(y-rad),self.z(x+rad),self.z(y+rad)),fill=color)

    def shell(self,t,night=False):
        # Scenic depth: art from repository behind a hand-illustrated market.
        im=self.roof.copy()
        self.rect(im,(0,0,720,1280),(14,20,25,90))
        d=ImageDraw.Draw(im,"RGBA")
        d.polygon([(0,self.z(420)),(self.z(720),self.z(460)),
                   (self.z(720),self.z(970)),(0,self.z(920))],fill=(36,35,34,140))
        for i in range(7):
            x=i*126-40
            d.polygon([(self.z(x),self.z(225)),(self.z(x+96),self.z(225)),
                       (self.z(x+122),self.z(415)),(self.z(x-7),self.z(415))],
                       fill=(126,44,36,230) if i%2==0 else (214,177,119,225))
        d.line((0,self.z(415),self.w,self.z(415)),fill=(249,207,122,220),width=self.z(10))
        # Framed lanterns and tiled storefront.
        for x in (80,640):
            yy=360+math.sin(t*2+x)*8
            d.line((self.z(x),self.z(392),self.z(x),self.z(yy+15)),fill=(240,206,142,160),width=self.z(3))
            d.ellipse((self.z(x-33),self.z(yy),self.z(x+33),self.z(yy+78)),
                     fill=(230,79,48,210),outline=(250,188,92,235),width=self.z(3))
            d.line((self.z(x-27),self.z(yy+34),self.z(x+27),self.z(yy+34)),fill=(251,195,91,170),width=self.z(2))
        self.rect(im,(110,258,610,365),(25,28,33,245),outline=(239,187,111,240),width=5,radius=5)
        self.drawtext(im,"小 椒 兵 器 铺",360,307,52,GOLD)
        self.rect(im,(25,810,695,1060),(72,43,38,255),outline=(178,118,79,255),width=8,radius=9)
        self.rect(im,(10,805,708,859),(116,74,51,255),outline=(246,186,95,230),width=3,radius=8)
        self.rect(im,(0,1060,720,1280),(27,29,31,230))
        self.particles(im,t,"ember" if night else "dust")
        return im

    def vignette(self,im,amount=115):
        # scene-specific lens vignette, not a shared fixed text card layout
        w,h=im.size
        d=ImageDraw.Draw(im,"RGBA")
        for j in range(12):
            a=int(amount/13)
            d.rectangle((j*self.z(5),j*self.z(6),
                         w-j*self.z(5),h-j*self.z(6)),
                        outline=(9,8,11,a),width=max(1,self.z(9)))
        return im

    def subtitle(self,im,text,tag=None):
        if not text:return
        if tag:
            self.drawtext(im,tag,65,1125,25,GOLD,"lm")
        # Text only at speaking moments: no persistent static dialogue bubble.
        self.rect(im,(30,1152,690,1227),(15,18,23,214),radius=14)
        self.drawtext(im,text,360,1190,29,(254,242,218))

    def wooden_sign(self,im,label,x,y,color=(232,199,139),subtext=None):
        self.rect(im,(x-170,y-38,x+170,y+52),(44,32,29,242),outline=color,width=4,radius=9)
        self.drawtext(im,label,x,y,50,color,stroke=1)
        if subtext:self.drawtext(im,subtext,x,y+79,27,PAPER)

    def gripe_card(self,im,index,word):
        self.rect(im,(26,94,694,197),(21,21,23,238),outline=(210,97,67,215),width=3,radius=12)
        self.drawtext(im,"百炼烧心体验 "+str(index)+"/3",360,122,31,(255,144,111))
        self.drawtext(im,word,360,172,37,CREAM)

    def shard(self,im,x,y,tint=(246,158,72),r=20):
        d=ImageDraw.Draw(im,"RGBA")
        X,Y=self.z(x),self.z(y)
        rad=self.z(r)
        d.ellipse((X-rad,Y-rad,X+rad,Y+rad),fill=tint+(100,),
                  outline=tint+(230,),width=self.z(3))
        d.ellipse((X-rad//3,Y-rad//3,X+rad//3,Y+rad//3),fill=(255,252,222,190))

    def street_arrival(self,im,t):
        self.drawtext(im,"忍 村 兵 器 街",360,111,32,PAPER)
        self.wooden_sign(im,"百 炼",215,445,(221,137,112),subtext="便宜点儿")
        self.wooden_sign(im,"焚 天",555,445,(241,199,105),subtext="贵一些")
        self.character(im,"bailian",205,660,235,rot=11*math.sin(t*3))
        self.character(im,"weapon",542,668,235,rot=8*math.sin(t*3))
        self.character(im,"buyer",320,995,310,rot=math.sin(t*3)*5)
        self.character(im,"seller",610,974,290,flip=True)
        self.drawtext(im,"小黑：先看看谁家便宜",360,1133,29,PAPER)
        self.drawtext(im,"（忍3二创 · 虚构武器街）",360,1197,21,PAPER)

    def cheap_stall(self,im,t):
        p=t-3.25
        self.character(im,"buyer",170,799+math.sin(t*9)*8,470,rot=4*math.sin(t*5))
        self.character(im,"bailian",515,676,405,rot=10*math.sin(t*3),)
        self.drawtext(im,"便 宜，先 上！",360,150,65,CREAM)
        self.rect(im,(370,940,671,1008),(53,34,29,245),outline=(255,191,95,220),width=2,radius=10)
        self.drawtext(im,"老板：卖出一把",522,975,28,GOLD)
        self.subtitle(im,"百炼便宜，先整一把！","小黑")
        if p>2:
            self.drawtext(im,"*本段价格对比为剧情设定",355,1058,23,PAPER)

    def missed_catch(self,im,t):
        p=cap((t-6.4)/4.2)
        self.gripe_card(im,1,"非双焰角色得自己接锤")
        self.character(im,"buyer",185,794,560,rot=-8+6*math.sin(t*4))
        xx=270+550*smooth(p); yy=480+390*smooth(p)
        d=ImageDraw.Draw(im,"RGBA")
        for j in range(14):
            z=cap(p-j*.023)
            tx=270+550*smooth(z);ty=480+390*smooth(z)
            rr=max(3,18-j)
            d.ellipse((self.z(tx-rr),self.z(ty-rr),self.z(tx+rr),self.z(ty+rr)),
                      fill=(255,187,95,max(8,160-j*10)))
        self.character(im,"bailian",xx,yy,275,rot=50+170*p)
        self.drawtext(im,"等等！锤！",360,1060,59,(250,169,125))
        self.subtitle(im,"哎？这锤还得自己接？","小黑")
        self.drawtext(im,"*双焰·小椒使用百炼可自动接回",354,245,22,PAPER)

    def timed_charge(self,im,t):
        p=cap((t-10.75)/4.75)
        self.gripe_card(im,2,"回锤后得站稳蓄力1.5秒")
        self.character(im,"buyer",205,829,526,rot=0)
        self.character(im,"bailian",390,715,280,rot=-26)
        self.drawtext(im,"蓄 力 中",352,372,48,CREAM)
        self.rect(im,(160,429,560,466),(32,33,37,240),outline=PAPER,width=2,radius=6)
        self.rect(im,(165,434,165+390*min(1,p*1.2),461),(232,139,75,240),radius=4)
        self.drawtext(im,"1.5 秒",352,529,83,GOLD)
        self.drawtext(im,"（高伤蓄力条件）",352,626,28,PAPER)
        self.subtitle(im,"接到了！还得蓄力一秒半？","小黑")
        if p>.76:
            self.drawtext(im,"BOSS：趁你蓄力，先走了",352,1020,30,(249,159,121))

    def target_gone(self,im,t):
        p=cap((t-15.65)/3.6)
        self.gripe_card(im,3,"前方出手，得看Boss站位")
        self.character(im,"buyer",178,856,475,rot=7*math.sin(t*4))
        self.character(im,"bailian",270+520*p,632,380,rot=140*p)
        d=ImageDraw.Draw(im,"RGBA")
        for j in range(22):
            z=cap(p-j*.016)
            xx=270+520*z
            yy=640-24*math.sin(z*4)
            rr=5+j%5
            d.ellipse((self.z(xx-rr),self.z(yy-rr),self.z(xx+rr),self.z(yy+rr)),
                      fill=(250,157,61,max(8,200-j*9)))
        self.drawtext(im,"BOSS：已离开直线攻击区域",360,386,27,(235,173,150))
        self.drawtext(im,"空 了 ！",360,973,87,(255,132,97))
        self.subtitle(im,"我刚蓄完力，BOSS跑了！","小黑")
        self.drawtext(im,"*情景夸张演绎，非所有Boss实战结果",355,1058,22,PAPER)

    def burnt_heart(self,im,t):
        self.rect(im,(0,0,720,1280),(34,19,25,140))
        self.character(im,"buyer",235,774,535,rot=-4)
        self.character(im,"bailian",575,777,300,rot=-40,opacity=170)
        self.drawtext(im,"便 宜 是 便 宜",360,326,56,PAPER)
        self.drawtext(im,"但是真烧心！",360,460,74,(252,123,100),stroke=2)
        self.subtitle(im,"钱省了，人快烧心了。","小黑")
        self.drawtext(im,"*百炼有强控与伤害，烦的是操作节奏",355,1032,24,PAPER)

    def fentian_entry(self,im,t):
        p=smooth((t-21.8)/2.2)
        self.rect(im,(0,0,720,1280),(49,35,20,120))
        self.character(im,"seller",141,778,455,flip=True,rot=math.sin(t*2)*3)
        self.character(im,"weapon",450,686,620*(.65+.35*p),rot=14*math.sin(t*2))
        self.drawtext(im,"焚 天",360,230,102,(255,224,145),stroke=2)
        self.drawtext(im,"两段都有短暂无敌",360,336,36,CREAM)
        self.subtitle(im,"来试试焚天，两段都有短暂无敌。","小椒")
        self.drawtext(im,"*无敌效果为技能释放期间短暂触发",356,1034,22,PAPER)

    def fentian_combo(self,im,t):
        p=cap((t-25.5)/3.2)
        self.rect(im,(0,0,720,1280),(25,26,18,85))
        self.character(im,"buyer",155,842,400)
        # Spell arcs and real weapon sprite are animated separately.
        d=ImageDraw.Draw(im,"RGBA")
        for j in range(7):
            radius=112+j*37+9*math.sin(t*5+j)
            d.arc((self.z(425-radius),self.z(700-radius),self.z(425+radius),self.z(700+radius)),
                  (t*130+j*35)%360,(t*130+j*35+140)%360,fill=(255,172,64,195),
                  width=self.z(max(2,7-j//2)))
        self.character(im,"weapon",425,700,530,rot=120*math.sin(p*math.pi))
        for i in range(12):
            x=150+i*39
            y=580+math.sin(i+t*8)*110
            self.shard(im,x,y,r=4+i%6)
        self.drawtext(im,"定 身 → 击 飞 → 重 劈 → 戳 刺",360,210,35,(255,235,194))
        self.drawtext(im,"这次不慌！",360,1060,61,(255,216,141))
        self.subtitle(im,"定身，重劈！这回顺手了！","小黑")

    def payoff(self,im,t):
        self.character(im,"seller",567,766,550,flip=True,rot=2*math.sin(t*2))
        self.character(im,"buyer",166,799,490,rot=2*math.sin(t*4))
        self.character(im,"weapon",356,722,270,rot=8*math.sin(t*3))
        self.drawtext(im,"贵 是 贵 了 点",360,218,70,CREAM)
        self.drawtext(im,"但用着不烧心！",360,346,69,GOLD,stroke=2)
        self.subtitle(im,"老板，贵是贵了点，但用着不烧心！","小黑")

    def moral_end(self,im,t):
        p=smooth((t-33.0)/2.4)
        self.rect(im,(0,0,720,1280),(15,19,23,int(210*p+40)))
        self.character(im,"seller",355,750,620,rot=2*math.sin(t*4))
        self.drawtext(im,"规 矩 得 立 住",360,248,62,GOLD,stroke=2)
        self.drawtext(im,"忍 忍 才 能 少 遭 罪",360,352,43,CREAM)
        self.subtitle(im,"做兵器，先把规矩立住。","小椒")
        self.drawtext(im,"百炼 ≠ 废武器，区别在使用机制与操作习惯",360,1045,21,PAPER)
        self.drawtext(im,"数据依据：忍3官方武器介绍 / BWIKI",360,1096,23,PAPER)
        self.drawtext(im,"非官方玩家二创 · 非真实价格/伤害排行",360,1240,20,PAPER)

    def frame(self,t):
        im=self.shell(t,night=t>=15.65 and t<21.8)
        if t<3.25:self.street_arrival(im,t)
        elif t<6.4:self.cheap_stall(im,t)
        elif t<10.75:self.missed_catch(im,t)
        elif t<15.65:self.timed_charge(im,t)
        elif t<19.4:self.target_gone(im,t)
        elif t<21.8:self.burnt_heart(im,t)
        elif t<25.5:self.fentian_entry(im,t)
        elif t<28.7:self.fentian_combo(im,t)
        elif t<33.0:self.payoff(im,t)
        else:self.moral_end(im,t)
        for a in BEATS[1:]:
            delta=t-a
            if 0<=delta<.075:
                self.rect(im,(0,0,720,1280),(255,239,176,int(110*(1-delta/.075))))
        self.vignette(im,75)
        return im.convert("RGB")

def save_wave(dest,data,sr):
    with wave.open(str(dest),"wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(sr)
        out.writeframes((np.clip(data,-1,1)*32767).astype("<i2").tobytes())

def soundtrack(dest,secs,voice=True):
    sr=24000
    count=int(round(sr*secs))
    audio=np.zeros(count,dtype=np.float32)
    rng=np.random.default_rng(712)
    def add(wav,at,gain=1.0):
        pos=int(at*sr)
        end=min(count,pos+len(wav))
        if 0<=pos<end:audio[pos:end]+=wav[:end-pos]*gain
    def note(f,dur,vol,kind="plucked"):
        ts=np.arange(max(1,int(sr*dur)),dtype=np.float32)/sr
        if kind=="plucked":
            env=(1-np.exp(-ts*180))*np.exp(-ts*9)
            wave0=np.sin(2*np.pi*f*ts)+.28*np.sin(4*np.pi*f*ts)
        else:
            env=np.exp(-ts*21)
            wave0=np.sin(2*np.pi*f*ts)
        return (wave0*env*vol).astype(np.float32)
    bpm=96/60
    notes=[196,220,261.6,293.66,329.63,392]
    for i in range(math.ceil(secs*bpm*2)+1):
        at=i/(bpm*2)
        if at>=secs or 19.4<=at<21.8:continue
        if i%2==0:add(note(66,.25,.13,"kick"),at)
        if i%2==1:
            n=rng.standard_normal(int(sr*.052)).astype(np.float32)
            n*=np.exp(-np.arange(len(n))/sr*84)*.024
            add(n,at)
        if i%4 in (0,2):add(note(notes[(i//3)%6],.40,.047),at)
    # Hand-made sound effects; no third-party songs or clips.
    for i,(at,f,dur,v) in enumerate([(3.25,460,.18,.08),(6.4,680,.44,.09),
                                    (10.75,370,.17,.08),(15.65,76,.88,.22),
                                    (19.4,280,.12,.10),(21.8,820,.65,.10),
                                    (25.5,920,.45,.12),(28.7,690,.20,.06),
                                    (33.0,540,.3,.10)]):
        if at<secs:add(note(f,dur,v),at)
    narration=[]
    errors=[]
    if voice and secs>8:
        with tempfile.TemporaryDirectory() as tmp:
            for i,(start,text,voice_id) in enumerate(LINES):
                if start>=secs:continue
                media=Path(tmp)/("line_"+str(i)+".mp3")
                cmd=["edge-tts","--voice",voice_id,"--rate=+19%","--text",text,
                     "--write-media",str(media)]
                try:
                    subprocess.run(cmd,check=True,capture_output=True,timeout=55)
                    raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(media),
                                                  "-ac","1","-ar",str(sr),"-f","f32le","pipe:1"])
                    spoken=np.frombuffer(raw,dtype="<f4").copy()
                    valid=np.flatnonzero(np.abs(spoken)>.008)
                    if not len(valid):raise RuntimeError("silent speech")
                    spoken=spoken[max(0,valid[0]-1100):min(len(spoken),valid[-1]+2900)]
                    # Prevent rushing and overlap; captions always remain readable.
                    deadline=LINES[i+1][0]-.14 if i+1<len(LINES) else secs-.25
                    if start+len(spoken)/sr>deadline:
                        raise RuntimeError("voice too long for its own shot")
                    left=max(0,int((start-.14)*sr))
                    right=min(count,int((start+len(spoken)/sr+.15)*sr))
                    audio[left:right]*=.34
                    peak=max(.1,float(np.max(np.abs(spoken))))
                    add(spoken,start,min(2.0,.65/peak))
                    narration.append({"text":text,"at":start,"seconds":round(len(spoken)/sr,2),
                                      "voice":voice_id})
                except (subprocess.CalledProcessError,subprocess.TimeoutExpired,RuntimeError,
                        FileNotFoundError) as e:
                    errors.append({"text":text,"error":str(e)[:160]})
    # One post-fire beat of comic silence
    l=int(19.4*sr);r=min(count,int(21.7*sr))
    if r>l:audio[l:r]*=.12
    mx=float(np.max(np.abs(audio)))
    if mx>.96:audio*=.96/mx
    save_wave(dest,audio,sr)
    return narration,errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",required=True)
    ap.add_argument("--preview",action="store_true")
    ap.add_argument("--seconds",type=float,default=None)
    args=ap.parse_args()
    mv=Movie(args.preview)
    seconds=min(DURATION,args.seconds) if args.seconds is not None else DURATION
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        wav=Path(td)/"original-audio.wav"
        narration,failures=soundtrack(wav,seconds,voice=not args.preview)
        cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
             "-f","rawvideo","-pixel_format","rgb24","-video_size",
             str(mv.w)+"x"+str(mv.h),"-framerate",str(mv.fps),"-i","pipe:0",
             "-i",str(wav),"-map","0:v:0","-map","1:a:0",
             "-c:v","libx264","-preset","veryfast","-crf","20",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
             "-movflags","+faststart","-t",str(seconds),str(output)]
        ff=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for i in range(round(seconds*mv.fps)):
                ff.stdin.write(mv.frame(i/mv.fps).tobytes())
            ff.stdin.close()
            stderr=ff.stderr.read().decode("utf-8","replace")
            if ff.wait()!=0:raise RuntimeError("ffmpeg encode failed: "+stderr[-1800:])
        except Exception:
            ff.kill()
            raise
    report={
        "title":"小椒卖焚天：贵是贵了点，但不烧心（百炼对比版）",
        "actual_dimensions":[mv.w,mv.h],
        "fps":mv.fps,"duration":seconds,
        "reference_art":[str(p.relative_to(ROOT)) for p in ASSETS.values()],
        "spoken_clips":narration,
        "failed_or_skipped_voice_clips":failures,
        "audio_has_music":True,
        "voice_success":len(narration)==len(LINES) if not args.preview else None,
        "copyright":"非官方原创恶搞；第三方游戏素材未取得另行商用授权",
        "comparative_disclaimer":"百炼的非双焰接锤与1.5秒蓄力为机制事实；价格关系为虚构剧情；不声称百炼客观伤害低于焚天",
    }
    (output.parent/(output.stem+"-report.json")).write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RENDER OK",str(output),json.dumps({"speeches":len(narration),
          "voice_failures":len(failures),"size":[mv.w,mv.h]}),flush=True)

if __name__=="__main__":
    main()
