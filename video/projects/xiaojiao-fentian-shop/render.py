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
DURATION = 22.5
ASSETS = {
    "seller": ROOT / "assets/characters/xiaojiao_01.png",
    "buyer": ROOT / "assets/characters/xiaohei_01.png",
    "weapon": ROOT / "assets/weapons/wiki/wiki_weapon_101_fentian.png",
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
    (0.7, "忍村街口，新开了一家兵器铺。", "zh-CN-YunyangNeural"),
    (3.15, "老板，你这焚天，怎么卖这么贵？", "zh-CN-YunxiNeural"),
    (5.65, "贵是贵了点，但是不烧心。", "zh-CN-XiaoxiaoNeural"),
    (10.22, "行！那我试试！", "zh-CN-YunxiNeural"),
    (15.45, "不是？你管这叫不烧心？！", "zh-CN-YunxiNeural"),
    (18.0, "只烧铺子，不烧心。", "zh-CN-XiaoxiaoNeural"),
]
BEATS = [0, 3.15, 5.65, 7.6, 10.2, 13.5, 14.55, 16.7, 19.8]
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

    def base_intro(self,im,t):
        self.drawtext(im,"忍 村 街 口",360,115,27,PAPER)
        pulse=spring(t/1.8)
        self.character(im,"seller",370+16*math.sin(t*1.2),716+(1-pulse)*120,
                       610*pulse+15,rot=2*math.sin(t*2))
        if t>1.2:
            self.character(im,"weapon",552,726,240,rot=math.sin(t*2)*6)
        self.drawtext(im,"新开一家兵器铺",360,1030,38,CREAM)
        if t>2.0:self.drawtext(im,"据说卖的都是好东西。",360,1087,28,PAPER)

    def bargaining(self,im,t):
        local=t-3.15
        self.character(im,"buyer",164+max(0,1-local*2)*-90,696+math.sin(t*5)*4,456,
                       flip=False,rot=2*math.sin(t*3))
        self.character(im,"seller",565,670+math.sin(t*2.6)*4,535,
                       flip=True,rot=-2*math.sin(t*2))
        self.character(im,"weapon",369,688+8*math.sin(t*3),220,rot=math.sin(t*1.2)*9)
        if t<5.65:
            self.subtitle(im,"这焚天，怎么卖这么贵？","小黑")
        else:
            self.subtitle(im,"贵是贵了点，但不烧心。","小椒")
        if t>6.45:
            self.drawtext(im,"童叟无欺",365,505,34,GOLD)

    def product(self,im,t):
        local=t-7.6
        d=ImageDraw.Draw(im,"RGBA")
        im.alpha_composite(Image.new("RGBA",im.size,(30,18,15,170)))
        for j in range(5):
            rad=165+j*33+math.sin(t*2+j)*7
            d.arc((self.z(360-rad),self.z(640-rad),self.z(360+rad),self.z(640+rad)),
                  start=(t*80+j*49)%360,end=(t*80+j*49+172)%360,
                  fill=(246,148,57,170),width=self.z(3))
        self.character(im,"weapon",360,648,620*(.74+.26*smooth(local/1.0)),
                       rot=-9+7*math.sin(t*2.9))
        self.drawtext(im,"焚 天",360,212,116,CREAM,stroke=3)
        self.drawtext(im,"限量神兵 · 品相上乘",360,337,34,PAPER)
        self.drawtext(im,"老板口头保证：不烧心",360,1068,32,GOLD)

    def demo(self,im,t):
        local=t-10.2
        self.character(im,"buyer",195,775,570,rot=3*math.sin(t*7))
        self.character(im,"seller",575,757,405,flip=True,rot=5)
        self.drawtext(im,"现场验货",360,122,65,CREAM)
        if local<1.25:
            self.character(im,"weapon",230,535,230,rot=-30+15*local)
            self.subtitle(im,"行！那我试试！","小黑")
        else:
            # Rotating prop plus drawn fire trail follows the actual weapon.
            p=cap((local-1.25)/2.55)
            x=200+460*smooth(p)
            y=550-180*math.sin(p*math.pi)
            d=ImageDraw.Draw(im,"RGBA")
            for j in range(16):
                u=cap(p-j*.019)
                xx=200+460*smooth(u)
                yy=550-180*math.sin(u*math.pi)
                r=8+j*.95
                d.ellipse((self.z(xx-r),self.z(yy-r),self.z(xx+r),self.z(yy+r)),
                          fill=(255,max(33,190-j*9),39,max(0,210-j*12)))
            self.character(im,"weapon",x,y,290,rot=48+190*p)
            self.drawtext(im,"等等！",360,1124,64,GOLD)
        if local>2.65:
            n=cap((local-2.65)/.65)
            d.polygon([(0,self.z(1050)),(self.z(720),self.z(970)),
                       (self.z(720),self.z(1280)),(0,self.z(1280))],
                       fill=(255,79,23,int(225*n)))
            self.drawtext(im,"轰！！",350,540,120,(255,220,120),stroke=4)

    def aftermath(self,im,t):
        # Burned storefront. Music hard stops, desaturated pause.
        self.rect(im,(0,0,720,1280),(9,10,12,160))
        self.rect(im,(110,258,610,365),(17,19,22,250),outline=(74,58,47,230),width=5)
        self.drawtext(im,"小 椒 兵 器 铺",360,306,52,(134,104,77))
        d=ImageDraw.Draw(im,"RGBA")
        for i in range(20):
            x=i*49-65+int(12*math.sin(t+i))
            y=1020+(i%4)*21
            d.polygon([(self.z(x),self.z(y)),(self.z(x+24),self.z(y-12)),
                       (self.z(x+54),self.z(y+29)),(self.z(x-3),self.z(y+38))],
                       fill=(17,16,16,225))
        self.character(im,"seller",533,687,480,flip=True,opacity=195)
        self.character(im,"buyer",179,710,425,opacity=210)
        self.drawtext(im,"……",360,1017,105,(220,215,203))

    def punchline(self,im,t):
        self.rect(im,(0,0,720,1280),(23,24,28,80))
        self.character(im,"buyer",192,700,495,rot=-5+2*math.sin(t*9))
        self.character(im,"seller",545,674,525,flip=True,rot=math.sin(t*2))
        self.drawtext(im,"什么？！",370,452,74,GOLD)
        if t<18.0:
            self.subtitle(im,"你管这叫不烧心？！","小黑")
        else:
            self.subtitle(im,"只烧铺子，不烧心。","小椒")
            if t>18.8:self.drawtext(im,"只 烧 铺 子",360,945,62,CREAM)

    def endcard(self,im,t):
        self.rect(im,(0,0,720,1280),(10,14,17,229))
        self.drawtext(im,"只烧铺子",360,430,105,CREAM,stroke=2)
        self.drawtext(im,"不烧心",360,572,120,GOLD,stroke=3)
        self.character(im,"weapon",360,835,280,rot=10*math.sin(t*4))
        self.drawtext(im,"售后说明：本店不包重建。",360,1065,30,CREAM)
        self.drawtext(im,"忍者必须死3 · 玩家脑洞二创",360,1195,22,PAPER)

    def frame(self,t):
        if t>=19.8:
            im=Image.new("RGBA",(self.w,self.h),(15,19,23,255))
            self.endcard(im,t)
        else:
            im=self.shell(t,night=t>=13.5)
            if t<3.15:self.base_intro(im,t)
            elif t<7.6:self.bargaining(im,t)
            elif t<10.2:self.product(im,t)
            elif t<14.55:self.demo(im,t)
            elif t<16.7:self.aftermath(im,t)
            else:self.punchline(im,t)
        # brief editorial flash cuts
        for a in BEATS[1:]:
            delta=t-a
            if 0<=delta<.07:
                self.rect(im,(0,0,720,1280),(255,238,174,int(130*(1-delta/.07))))
        self.vignette(im,70)
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
        if at>=secs or 14.55<=at<16.7:continue
        if i%2==0:add(note(66,.25,.13,"kick"),at)
        if i%2==1:
            n=rng.standard_normal(int(sr*.052)).astype(np.float32)
            n*=np.exp(-np.arange(len(n))/sr*84)*.024
            add(n,at)
        if i%4 in (0,2):add(note(notes[(i//3)%6],.40,.047),at)
    # Hand-made sound effects; no third-party songs or clips.
    for i,(at,f,dur,v) in enumerate([(3.15,460,.18,.08),(7.6,680,.44,.09),
                                    (10.2,370,.17,.08),(13.8,76,.88,.22),
                                    (16.7,280,.12,.10),(19.8,820,.65,.10)]):
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
    l=int(14.55*sr);r=min(count,int(16.6*sr))
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
        "title":"小椒卖焚天：贵是贵了点，但不烧心",
        "actual_dimensions":[mv.w,mv.h],
        "fps":mv.fps,"duration":seconds,
        "reference_art":[str(p.relative_to(ROOT)) for p in ASSETS.values()],
        "spoken_clips":narration,
        "failed_or_skipped_voice_clips":failures,
        "audio_has_music":True,
        "voice_success":len(narration)==len(LINES) if not args.preview else None,
        "copyright":"非官方原创恶搞；第三方游戏素材未取得另行商用授权",
    }
    (output.parent/(output.stem+"-report.json")).write_text(
        json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print("RENDER OK",str(output),json.dumps({"speeches":len(narration),
          "voice_failures":len(failures),"size":[mv.w,mv.h]}),flush=True)

if __name__=="__main__":
    main()
