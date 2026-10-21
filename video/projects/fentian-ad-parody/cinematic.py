#!/usr/bin/env python3
"""Cinematic version of Fentian's miss-parody: independently staged frames.

No inherited static stage/template: layered camerawork, squash/stretch, speed
trails, shot-specific titles, editorial audio beats and practical compositing.
Uses checked in Ninja 3 artwork and existing music repository.
"""
import argparse
import json
import math
import random
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from render import Film as ImageLoader

ROOT=Path(__file__).resolve().parents[3]
WORKSPACE=ROOT.parent
MUSIC=WORKSPACE/"music/music/game-ost/unique-boss-battle.mp3"
DURATION=24.0
SHOT_CUTS=(0,2.05,4.75,7.65,10.05,12.50,15.20,18.15,21.35,24.0)
VOICE=[
    (2.10,"忍村新武器，焚天！", "zh-CN-YunxiNeural"),
    (10.45,"目标锁定，准备发射！", "zh-CN-YunjianNeural"),
    (15.55,"不是……它怎么自己拐弯了？", "zh-CN-YunxiNeural"),
    (19.10,"恭喜，最佳闪避奖。", "zh-CN-YunyangNeural"),
]


def clamp(x,low=0,high=1):
    return max(low,min(high,x))

def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)

def lerp(a,b,u):
    return a+(b-a)*u


class Stage(ImageLoader):
    def __init__(self,preview=False):
        super().__init__(preview=preview)
        self.w,self.h,self.fps=(432,768,12) if preview else (1080,1920,30)
        self.s=self.w/720
        self.font_cache={}
        self.sprites={}
        self.rand=random.Random(47)
        self.make_background()
        # Compute vignette only once, not once per video frame.
        Y,X=np.ogrid[:self.h,:self.w]
        xx=(X-self.w*.5)/(self.w*.5)
        yy=(Y-self.h*.5)/(self.h*.5)
        vignette=np.clip((xx*xx*.52+yy*yy*.39),0,1)
        dark=(vignette*148).astype(np.uint8)
        self.vignette=Image.fromarray(dark,"L")
        self.glow=Image.new("RGBA",(self.w,self.h),(0,0,0,0))
        self.trails=[]
        for j in range(145):
            self.trails.append((self.rand.randint(-100,820),self.rand.randint(-60,1370),
                                self.rand.random()*.6+.4,self.rand.random()*6.2))
        self.huge_headlines={
            "LAUNCH":self.font(97),"FENTIAN":self.font(135),"MISS":self.font(151)}

    def make_background(self):
        src=self.imgs["bg"].convert("RGB")
        w,h=self.w,self.h
        factor=max(w/src.width,h/src.height)*1.36
        sw,sh=math.ceil(src.width*factor),math.ceil(src.height*factor)
        src=src.resize((sw,sh),Image.Resampling.LANCZOS)
        self.backdrop=src
        self.bgsize=(sw,sh)
        # Nonuniform blur layers for a photographic depth cue.
        self.bg_blur=src.filter(ImageFilter.GaussianBlur(max(2,self.P(8))))

    def background(self,t,energy=.2,blur=False):
        w,h=self.w,self.h
        sw,sh=self.bgsize
        ox=clamp(.48+math.sin(t*.32)*.10,0,1)*(sw-w)
        oy=clamp(.48+math.cos(t*.30)*.10,0,1)*(sh-h)
        source=self.bg_blur if blur else self.backdrop
        patch=source.crop((int(ox),int(oy),int(ox+w),int(oy+h))).convert("RGBA")
        # Proper atmosphere: tint avoids raw art and puts bright silhouettes forward.
        shad=Image.new("RGBA",(w,h),(8,10,20,int(160-26*energy)))
        patch=Image.alpha_composite(patch,shad)
        color=Image.new("RGBA",(w,h),(int(51+30*energy),9,int(23+35*energy),35))
        return Image.alpha_composite(patch,color)

    def rect(self,canvas,box,fill,width=None):
        d=ImageDraw.Draw(canvas,"RGBA")
        box=tuple(map(self.P,box))
        d.rectangle(box,fill=fill,width=max(1,self.P(width)) if width else 1)

    def circle(self,canvas,x,y,r,outline,stroke=2):
        d=ImageDraw.Draw(canvas,"RGBA")
        d.ellipse(tuple(map(self.P,(x-r,y-r,x+r,y+r))),outline=outline,width=max(1,self.P(stroke)))

    def type(self,canvas,words,x,y,size,color="#FFFFFF",stroke=0,anchor="mm"):
        # Central screen-safe typography without persistent HUD.
        self.txt(canvas,words,x,y,size,color,anchor=anchor,stroke=stroke)

    def flare(self,canvas,x,y,r,color=(255,131,61,180)):
        d=ImageDraw.Draw(canvas,"RGBA")
        cx,cy=self.P(x),self.P(y)
        rad=self.P(r)
        d.ellipse((cx-rad//2,cy-rad//2,cx+rad//2,cy+rad//2),fill=color)
        d.line((cx-rad*2,cy,cx+rad*2,cy),fill=color,width=max(1,self.P(2)))
        d.line((cx,cy-rad*2,cx,cy+rad*2),fill=color,width=max(1,self.P(2)))

    def grain(self,canvas,t,intensity=1):
        # Thin animated glimmer/speed flecks (deterministic).
        d=ImageDraw.Draw(canvas,"RGBA")
        speed=26 if intensity<1.5 else 110
        for x,y,amp,phase in self.trails[::2]:
            xx=(x+speed*t+40*math.sin(phase))%810-45
            yy=(y+32*math.sin(t*.3+phase))%1450-80
            alpha=int(min(100,18+amp*60)*intensity)
            length=max(2,self.P((3+4*amp)*intensity))
            d.line((self.P(xx),self.P(yy),self.P(xx)+length,self.P(yy)-length//2),
                   fill=(255,191,111,alpha),width=max(1,self.P(1.3)))

    def speedlines(self,canvas,vanish=(350,640),progress=1.0,warm=True):
        d=ImageDraw.Draw(canvas,"RGBA")
        rng=random.Random(120)
        color=(255,210,160,165) if warm else (164,220,255,158)
        for j in range(68):
            a=(j/68)*2*math.pi+rng.uniform(-.03,.03)
            r=330+rng.uniform(0,530)
            x=vanish[0]+math.cos(a)*r
            y=vanish[1]+math.sin(a)*r
            length=80+100*progress+rng.randrange(110)
            xx=x+math.cos(a)*length
            yy=y+math.sin(a)*length
            d.line((self.P(x),self.P(y),self.P(xx),self.P(yy)),
                   fill=color,width=max(1,self.P(1.2+rng.random()*2.1)))

    def split_label(self,canvas,t,top,kicker=None):
        a=ease(t/.27)
        x=lerp(-510,42,a)
        self.type(canvas,top,x,110,29,"#FFE6B1",anchor="lm")
        if kicker:
            self.type(canvas,kicker,x,167,52,"#FFF2E9",anchor="lm")

    def overlay(self,canvas,t):
        # Film-style letterbox is not forced globally; here scenes use subtle vignette only.
        shade=Image.new("RGBA",(self.w,self.h),(0,0,0,0))
        shade.putalpha(self.vignette)
        canvas.alpha_composite(shade)
        # Small lower-left credits instead of a permanent screen frame.
        if t<2.0 or t>22.0:
            self.type(canvas,"非官方二创 / NINJA MUST DIE 3",360,1209,17,"#CEB9C6")

    def stage0(self,canvas,t):
        # Cold open: extreme crop close-up and sharp kinetic slash before title.
        self.grain(canvas,t,.6)
        u=ease(t/1.5)
        self.place(canvas,"weapon",230+70*u,780,1020-220*u,angle=-43+15*u)
        self.flare(canvas,460,590,25+25*math.sin(t*3))
        if t>.45:
            self.type(canvas,"这把武器",350,203+56*(1-ease((t-.45)/.25)),57,"#FFCA8D")
        if t>1.05:
            self.type(canvas,"看起来稳了。",350,326+42*(1-ease((t-1.05)/.3)),63,"#FFF3E6",stroke=2)
        self.rect(canvas,(34,434,48,550),(255,156,67,240))

    def stage1(self,canvas,t):
        p=(t-2.05)/2.7
        self.grain(canvas,t,.9)
        self.circle(canvas,360,688,268+math.sin(t*3)*12,(253,126,53,168),3)
        self.circle(canvas,360,688,300+math.cos(t*2)*9,(255,212,116,113),2)
        self.place(canvas,"weapon",360,688,785,angle=-18+11*math.sin(t*2.2),
                   scale=.74+.17*ease(p/.5))
        self.type(canvas,"焚 天",360,255,103,"#FFE6BE",stroke=3)
        self.type(canvas,"忍村绝赞发布",360,1070,37,"#FFC39E")
        self.type(canvas,"★  火力亮相  ★",360,1126,27,"#F6B364")
        self.flare(canvas,355,580,42)

    def stage2(self,canvas,t):
        p=(t-4.75)/2.9
        self.speedlines(canvas,(375,760),p,warm=False)
        self.grain(canvas,t,1)
        self.place(canvas,"hero",445-76*ease(p),805,775,angle=-5,scale=.7+.27*ease(p))
        self.type(canvas,"忍者出击",350,205,86,"#FFF0DF",stroke=3)
        self.type(canvas,"这次真的稳！",350,1170,45,"#FFBD81")
        self.flare(canvas,300,640,18)

    def stage3(self,canvas,t):
        p=(t-7.65)/2.4
        self.grain(canvas,t,.75)
        self.place(canvas,"boss",365,695,830,scale=.75+.34*ease(p))
        self.circle(canvas,365,700,270,(255,104,118,225),4)
        self.circle(canvas,365,700,300+8*math.sin(t*6),(255,130,144,138),2)
        self.type(canvas,"骸骨死神",350,176,91,"#FFF3EE",stroke=3)
        self.type(canvas,"LOCKED ON",350,1100,37,"#FF9994")
        self.rect(canvas,(88,1136,632,1141),(247,75,95,180))

    @staticmethod
    def path(p):
        # Bezier curve with continuity: direct charge and unmistakable evasive turn.
        p=clamp(p)
        if p<.62:
            u=ease(p/.62)
            return (45+335*u,1260-570*u)
        if p<.84:
            u=ease((p-.62)/.22)
            return (380+282*u,690-320*u)
        u=ease((p-.84)/.16)
        return (662+180*u,370-295*u)

    def stage4(self,canvas,t):
        p=(t-10.05)/2.45
        self.speedlines(canvas,(360,725),.8,warm=True)
        self.place(canvas,"boss",405,675,790,scale=.84)
        self.type(canvas,"发射！",360,167,112,"#FFE2A5",stroke=3)
        for j in range(42):
            f=max(0,p-j*.015)
            if f<0:continue
            x,y=self.path(f)
            rr=clamp(j/42)
            self.circle(canvas,x,y,22-rr*15,(255,112,30,int(188*(1-rr))),3)
        x,y=self.path(p)
        # Physical rotation/trail, no teleport between static card positions.
        self.place(canvas,"weapon",x,y,415,angle=40+37*math.sin(t*9))
        self.flare(canvas,x,y,23)
        if t>11.77:
            self.type(canvas,"等等……",350,1112,48,"#FFB7A9")

    def stage5(self,canvas,t):
        # Camera zooms boss while the weapon flies off camera. Stereo gag pause.
        p=(t-12.5)/2.7
        self.grain(canvas,t,.42)
        self.place(canvas,"boss",340,785,1050,scale=.82+.12*ease(p))
        self.speedlines(canvas,(360,710),.35,warm=False)
        x=640+110*ease(p);y=120-85*ease(p)
        self.place(canvas,"weapon",x,y,310,angle=-35)
        self.type(canvas,"？？？",360,285,127,"#FFCB8B",stroke=4)
        self.type(canvas,"武器：我先撤了",360,1100,46,"#FFF0E8",stroke=2)

    def stage6(self,canvas,t):
        p=(t-15.2)/2.95
        # Graphic freeze-frame for comedic timing: black/white inverted lines.
        self.grain(canvas,t,.22)
        self.place(canvas,"boss",360,800,1040,opacity=245,scale=.83)
        self.type(canvas,"完美闪避",360,206,103,"#FFE6B8",stroke=4)
        self.type(canvas,"（指武器）",360,340,44,"#FFAAA3")
        self.type(canvas,"伤害：保密",360,1120,36,"#F0C9CE")
        d=ImageDraw.Draw(canvas,"RGBA")
        for k in range(4):
            y=550+k*90
            d.line((self.P(58),self.P(y),self.P(668),self.P(y-190)),
                   fill=(255,201,126,90),width=max(1,self.P(2)))
        if int(t*6)%2==0:
            self.flare(canvas,330,600,16,(255,255,255,230))

    def stage7(self,canvas,t):
        # Award gag, a hard visual break from all combat shots.
        p=(t-18.15)/3.2
        d=ImageDraw.Draw(canvas,"RGBA")
        for i in range(55):
            x=18+(i*107+t*52)%720
            y=(i*166+140*t)%1280
            r=2+2*math.sin(i)
            d.ellipse((self.P(x-r),self.P(y-r),self.P(x+r),self.P(y+r)),
                      fill=(255,193,91,110))
        spin=25*(1-ease(p/.45))
        self.place(canvas,"weapon",360,765,705,angle=spin,scale=.65+.18*ease(p/.7))
        self.circle(canvas,360,765,320,(255,218,133,170),4)
        self.type(canvas,"最佳闪避奖",360,231,82,"#FFE0A0",stroke=3)
        self.type(canvas,"年度最会绕路的武器",360,1120,39,"#FFE9D8")
        self.flare(canvas,360,670,37)

    def stage8(self,canvas,t):
        p=(t-21.35)/2.65
        self.place(canvas,"hero",390,763,890,scale=.72+.15*ease(p))
        self.type(canvas,"小黑：",347,218,57,"#FFC38A")
        self.type(canvas,"至少……",347,342,67,"#FFF3E5",stroke=2)
        self.type(canvas,"它躲得很帅。",355,464,69,"#FFE2B4",stroke=2)
        self.type(canvas,"本片为非官方虚构二创",360,1110,21,"#CFC0C1")
        self.circle(canvas,355,718,316,(255,180,99,74),3)

    def frame(self,t):
        cut=sum(t>=x for x in SHOT_CUTS[:-1])-1
        # Stage palettes and camera dolly are per-shot artistic choices.
        base=self.background(t,blur=cut in (0,2,7),energy=.5 if cut in (1,4,7) else .1)
        # Color split on cuts, warm highlights against cold boss cyan.
        if cut in (3,5,6):
            tint=Image.new("RGBA",(self.w,self.h),(8,36,68,44))
            base.alpha_composite(tint)
        fn=(self.stage0,self.stage1,self.stage2,self.stage3,self.stage4,
            self.stage5,self.stage6,self.stage7,self.stage8)[max(0,min(8,cut))]
        fn(base,t)
        # Real shake and light strike around launch, not permanent jitter.
        for point in (2.05,4.75,7.65,10.05,12.5,15.2,18.15,21.35):
            delta=t-point
            if 0<=delta<.10:
                overlay=Image.new("RGBA",(self.w,self.h),(255,233,196,int(152*(1-delta/.1))))
                base.alpha_composite(overlay)
        if 10.05<=t<12.5:
            # Quick cut-driven camera shake only at moments of perceived impact.
            strength=4.0*(1-clamp((t-10.05)/1.2))
            dx=self.P(strength*math.sin(t*67))
            dy=self.P(strength*math.cos(t*53))
            shifted=Image.new("RGBA",(self.w,self.h),(4,7,12,255))
            shifted.alpha_composite(base,(dx,dy))
            base=shifted
        self.overlay(base,t)
        return base.convert("RGB")


def ffmpeg_float(args):
    return np.frombuffer(subprocess.check_output(args),dtype="<f4").copy()

def write_wav(path,x,sr=24000):
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(x,-1,1)*32767).astype("<i2").tobytes())

def sound_mix(path,length,preview):
    sr=24000
    size=int(round(length*sr))
    if not MUSIC.is_file():
        raise FileNotFoundError("Need musical score from your anime-music-library: "+str(MUSIC))
    track=ffmpeg_float(["ffmpeg","-v","error","-ss","4","-i",str(MUSIC),
                        "-t",str(length),"-ac","1","-ar",str(sr),"-f","f32le","-"])
    bed=np.zeros(size,np.float32)
    bed[:min(size,len(track))]=track[:min(size,len(track))]
    rms=float(np.sqrt(np.mean(bed*bed))+.00001)
    bed*=min(1.5,.115/rms)
    # Deep comic silence beats. Music falls out when "weapon" decides to flee.
    attack=np.ones(size,dtype=np.float32)
    for a,b,g in ((12.50,13.25,.03),(15.24,15.80,.10),(18.15,18.43,.12)):
        left=max(0,int(a*sr));right=min(size,int(b*sr))
        if right>left:attack[left:right]=g
    bed*=attack
    effects=np.zeros(size,np.float32)
    rng=np.random.default_rng(808)
    def add(x,t,gain=1):
        i=int(t*sr)
        if 0<=i<size:
            end=min(size,i+len(x))
            effects[i:end]+=x[:end-i]*gain
    def thunk(freq,dur,gain):
        tt=np.arange(max(1,int(dur*sr)),dtype=np.float32)/sr
        return (np.sin((freq*tt-45*tt*tt)*2*np.pi)*np.exp(-tt*15)*gain).astype(np.float32)
    def whoosh(sec=0.3):
        n=int(sec*sr)
        tt=np.arange(n,dtype=np.float32)/sr
        noise=rng.standard_normal(n).astype(np.float32)
        return noise*(np.sin(np.pi*tt/sec)**2)*.035
    for i,t in enumerate(SHOT_CUTS[1:-1]):
        add(thunk(94+i*8,.27,.23),t)
        add(whoosh(),max(0,t-.12))
    for j in range(17):
        t=10.05+j*.13
        if t>12.48:break
        add(thunk(170+j*28,.14,.057),t)
    add(thunk(68,.55,.28),12.53)
    add(whoosh(.85),17.95)
    voices=[]
    if not preview:
        for i,(at,text,voice) in enumerate(VOICE):
            if at>=length:continue
            with tempfile.TemporaryDirectory() as tmp:
                clip=Path(tmp)/"voice.mp3"
                subprocess.run(["edge-tts","--voice",voice,"--rate=+14%",
                                "--text",text,"--write-media",str(clip)],
                               capture_output=True,check=True,timeout=75)
                spoken=ffmpeg_float(["ffmpeg","-v","error","-i",str(clip),
                                     "-ac","1","-ar",str(sr),"-f","f32le","-"])
            if not len(spoken):raise RuntimeError("Empty voice "+text)
            ids=np.flatnonzero(np.abs(spoken)>.008)
            if not len(ids):raise RuntimeError("Silent voice "+text)
            spoken=spoken[max(0,ids[0]-1000):min(len(spoken),ids[-1]+2400)]
            end=at+len(spoken)/sr
            next_mark=VOICE[i+1][0] if i+1<len(VOICE) else length
            if end>min(next_mark-.2,length-.1):
                raise RuntimeError("Voice overlaps another scene "+text)
            left=max(0,round((at-.11)*sr))
            right=min(size,round((end+.26)*sr))
            if right>left:
                envelope=np.full(right-left,.23,np.float32)
                n=min(2600,len(envelope)//2)
                if n:
                    envelope[:n]=np.linspace(1,.23,n)
                    envelope[-n:]=np.linspace(.23,1,n)
                bed[left:right]*=envelope
            maxpeak=float(np.max(np.abs(spoken)))
            spoken*=min(1.8,.61/max(.001,maxpeak))
            add(spoken,at)
            voices.append({"line":text,"start":at,"end":round(end,3),"voice":voice})
    mix=bed+effects
    level=float(np.max(np.abs(mix))) if len(mix) else 0
    if level>.94:mix*=.94/level
    write_wav(path,mix,sr)
    return {"voice_clips":voices,"score":str(MUSIC),"duration":length,
            "peak":float(np.max(np.abs(mix))),"original_fx":True}


def render(args):
    stage=Stage(preview=args.preview)
    length=min(float(args.seconds),DURATION) if args.seconds else DURATION
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav=Path(tmp)/"audio.wav"
        info=sound_mix(wav,length,args.preview)
        ff=["ffmpeg","-y","-hide_banner","-loglevel","error",
            "-f","rawvideo","-pixel_format","rgb24",
            "-video_size",f"{stage.w}x{stage.h}","-framerate",str(stage.fps),
            "-i","pipe:0","-i",str(wav),"-map","0:v","-map","1:a",
            "-c:v","libx264","-crf","17","-preset","veryfast",
            "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest",
            "-movflags","+faststart",str(output)]
        pipe=subprocess.Popen(ff,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for k in range(round(length*stage.fps)):
                pipe.stdin.write(stage.frame(k/stage.fps).tobytes())
                if k%max(1,stage.fps*3)==0:
                    print(f"Render {k/stage.fps:.1f}/{length:.1f}s",flush=True)
            pipe.stdin.close()
            stderr=pipe.stderr.read().decode("utf-8","replace")
            if pipe.wait()!=0:raise RuntimeError("Encoder failed: "+stderr[-1800:])
        except Exception:
            pipe.kill()
            raise
    report=output.with_name(output.stem+"-render-report.json")
    info.update({"visual":"scene-specific cinematic 2.5D edits, motion smear and parallax",
                 "width":stage.w,"height":stage.h,"fps":stage.fps})
    report.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
    print("SUCCESS cinematic:",output,"report",report,flush=True)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--preview",action="store_true")
    p.add_argument("--seconds",type=float)
    render(p.parse_args())
