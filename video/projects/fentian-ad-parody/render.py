#!/usr/bin/env python3
"""焚天：命中率靠缘分 — vertical kinetic-comedy animation, standalone art direction.
A fictional weapon advertisement parody. Does not assert actual NMD3 statistics.
Uses authentic locally checked repository artwork; no borrowed movie footage.
"""
import argparse
import json
import math
import os
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
DURATION = 24.0
PROJECT = "fentian-ad-parody"
FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyhbd.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]
ASSETS = {
    "weapon": ROOT / "assets/weapons/wiki/wiki_weapon_101_fentian.png",
    "boss": ROOT / "assets/bosses/wiki/wiki_boss_haigu_sishen.png",
    "hero": ROOT / "assets/characters/xiaohei_fire_01.png",
    "bg": ROOT / "assets/backgrounds/wallpaper_rooftop_01.jpg",
}
VOICE_SCRIPT = [
    (1.05, "忍村新品，焚天！", "zh-CN-YunxiNeural"),
    (7.2, "目标锁定，骸骨死神。", "zh-CN-YunjianNeural"),
    (13.25, "等等，怎么拐弯了？", "zh-CN-YunxiNeural"),
    (19.4, "恭喜获得，最佳闪避奖！", "zh-CN-YunyangNeural"),
]


def clamp(v, low=0.0, high=1.0):
    return max(low, min(high, v))


def ease(v):
    x = clamp(v)
    return x*x*(3-2*x)


def palette_image(w, h, t):
    # Dark red-to-violet stage, continuous animated gradient; no static talk layout.
    Y, X = np.ogrid[:h, :w]
    yy = Y / h
    xx = X / w
    wave = .5 + .5 * np.cos(xx * 7.3 + yy * 4.0 - t * .6)
    glow = np.exp(-((xx-.56)**2/.27 + (yy-.40)**2/.21))
    r = np.clip(10 + 20*yy + 48*glow + 12*wave, 0, 255)
    g = np.clip(11 + 10*(1-yy) + 13*glow, 0, 255)
    b = np.clip(29 + 44*yy + 28*(1-wave), 0, 255)
    rgb = np.empty((h,w,3), np.uint8)
    rgb[:,:,0] = r
    rgb[:,:,1] = g
    rgb[:,:,2] = b
    return Image.fromarray(rgb, "RGB").convert("RGBA")


class Film:
    def __init__(self, preview=False):
        self.w, self.h, self.fps = (432, 768, 12) if preview else (720, 1280, 24)
        self.s = self.w / 720
        self.font_cache = {}
        self.imgs = {}
        for name, path in ASSETS.items():
            if not path.is_file():
                raise FileNotFoundError("Missing real repository art: " + str(path))
            im = Image.open(path).convert("RGBA")
            if name != "bg":
                bbox = im.getchannel("A").getbbox()
                if bbox:
                    im = im.crop(bbox)
            self.imgs[name] = im
        self.sprites = {}

    def P(self, x):
        return int(round(x*self.s))

    def font(self, n):
        size = max(8, self.P(n))
        if size not in self.font_cache:
            name = next((p for p in FONTS if Path(p).exists()), None)
            if name is None:
                raise RuntimeError("Missing Chinese font: install fonts-noto-cjk")
            self.font_cache[size] = ImageFont.truetype(name, size)
        return self.font_cache[size]

    def sprite(self, name, height, opacity=255, flipped=False):
        key = (name, self.P(height), opacity, flipped)
        if key not in self.sprites:
            original = self.imgs[name]
            width = max(1, int(original.width * self.P(height) / original.height))
            obj = original.resize((width, self.P(height)), Image.Resampling.LANCZOS)
            if flipped:
                obj = obj.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            if opacity != 255:
                obj.putalpha(obj.getchannel("A").point(lambda a: a*opacity//255))
            self.sprites[key] = obj
        return self.sprites[key]

    def place(self, canvas, name, x, y, height, angle=0, opacity=255, scale=1):
        obj = self.sprite(name, height*scale, opacity)
        if angle:
            obj = obj.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        left = self.P(x)-obj.width//2
        top = self.P(y)-obj.height//2
        right = left+obj.width
        bottom = top+obj.height
        # Explicitly crop out-of-bounds sprites rather than silently skip them.
        l, top2 = max(0, -left), max(0, -top)
        r, b = min(obj.width,self.w-left), min(obj.height,self.h-top)
        if r>l and b>top2:
            canvas.alpha_composite(obj.crop((l,top2,r,b)),(left+l,top+top2))

    def txt(self, canvas, words, x, y, n, color="#FFFFFF", anchor="mm", stroke=0, outline="#120D1D"):
        d = ImageDraw.Draw(canvas)
        d.text((self.P(x),self.P(y)),words,font=self.font(n),anchor=anchor,fill=color,
               stroke_width=self.P(stroke),stroke_fill=outline)

    def line(self, canvas, points, fill, width):
        ImageDraw.Draw(canvas,"RGBA").line([(self.P(x),self.P(y)) for x,y in points],
                                      fill=fill,width=max(1,self.P(width)),joint="curve")

    def accent(self, canvas, t, intensity=1):
        d = ImageDraw.Draw(canvas,"RGBA")
        for k in range(18):
            a = k * 2.3999 + t*.17
            x = 360 + math.cos(a)*(190+90*math.sin(t*.9+k))
            y = 620 + math.sin(a)*(370+55*math.cos(t+k))
            rad = (1.5+2*abs(math.sin(t*2+k)))*intensity
            d.ellipse((self.P(x-rad),self.P(y-rad),self.P(x+rad),self.P(y+rad)),
                      fill=(255,171,64,int(55+90*abs(math.sin(t+k)))))

    def rings(self, canvas, cx, cy, radius, t, count=3, color=(255,157,46,125)):
        d=ImageDraw.Draw(canvas,"RGBA")
        for j in range(count):
            rr=radius+16*j+9*math.sin(t*4+j)
            d.arc((self.P(cx-rr),self.P(cy-rr),self.P(cx+rr),self.P(cy+rr)),
                  12+(t*100+j*36)%360, 224+(t*100+j*36)%360,
                  fill=color, width=max(1,self.P(3-j*.45)))

    def cover_bg(self, canvas, t, alpha=90):
        im = self.imgs["bg"]
        factor = max(self.w/im.width, self.h/im.height) * 1.18
        ww, hh = math.ceil(im.width*factor), math.ceil(im.height*factor)
        obj=im.resize((ww,hh),Image.Resampling.BILINEAR)
        x=max(0,min(ww-self.w,int((ww-self.w)*(.5+.1*math.sin(t*.3)))))
        y=max(0,min(hh-self.h,int((hh-self.h)*.5)))
        obj=obj.crop((x,y,x+self.w,y+self.h))
        obj.putalpha(alpha)
        canvas.alpha_composite(obj)

    def title_stage(self, canvas, t):
        p=ease(t/2.5)
        self.cover_bg(canvas,t,65)
        self.accent(canvas,t,.8)
        y=445+(1-p)*160
        self.txt(canvas,"忍 村 兵 器 台",360,260,39,"#FFBD67")
        self.txt(canvas,"新品发布",360,y,94,"#FFF6E5",stroke=2)
        self.txt(canvas,"「 焚 天 」",360,610,60,"#FF9041")
        self.txt(canvas,"非官方 · 虚构恶搞广告",360,1050,21,"#CEBCC8")
        self.line(canvas,[(92,730),(628,730)],(255,139,68,200),4)
        if t>1.5:
            self.place(canvas,"weapon",360,810,310,angle=math.sin(t*5)*9,scale=.7+.3*ease((t-1.5)/.8))

    def showcase(self, canvas, t):
        p=t-2.5
        self.accent(canvas,t,1.6)
        self.rings(canvas,360,625,244,t,count=3)
        self.place(canvas,"weapon",360,655,670,angle=-10+math.sin(t*1.7)*14,
                   scale=.70+.22*ease(p/.9))
        self.txt(canvas,"100%",360,180,116,"#FFE5A2",stroke=2)
        self.txt(canvas,"气势拉满",360,310,52,"#FFF7E4")
        self.txt(canvas,"攻击力气场测试中...",360,1053,30,"#FDBF89")
        # Animated labels are stage-specific, not fixed dialogue boxes.
        for i,label in enumerate(("火光 ★★★★★","牌面 ★★★★★","命中率 ？")):
            self.txt(canvas,label,360,1125+i*42,24,"#E7C4B3")

    def target_stage(self, canvas, t):
        p=t-6.8
        self.cover_bg(canvas,t,110)
        self.accent(canvas,t,.45)
        self.place(canvas,"boss",360,690,680,scale=.75+.16*ease(p/.7))
        self.rings(canvas,360,650,260,t,count=3,color=(255,75,116,200))
        self.txt(canvas,"目标锁定",360,188,78,"#FF7187")
        self.txt(canvas,"骸骨死神",360,295,54,"#FFE4E7")
        self.txt(canvas,"三 · 二 · 一",360,1120,45,"#FFE9BB")
        d=ImageDraw.Draw(canvas,"RGBA")
        for x,y in ((85,410),(635,410),(85,960),(635,960)):
            d.line((self.P(x-24),self.P(y),self.P(x+24),self.P(y)),fill=(255,111,119,190),width=self.P(3))
        # Deliberately NOT a boss HP / combat HUD: this is a mock TV-ad target lock.

    def missile_path(self, p):
        # Weapon starts bottom-left, accelerates toward the target, then consciously
        # dodges around it in a broad S-shaped comic arc.
        if p<.54:
            u=ease(p/.54)
            return (45+300*u, 1140-480*u)
        if p<.78:
            u=ease((p-.54)/.24)
            return (345+295*u, 660-330*u)
        u=ease((p-.78)/.22)
        return (640+120*u, 330-360*u)

    def attack_stage(self, canvas, t):
        p=clamp((t-10.0)/3.5)
        self.accent(canvas,t,.9)
        self.place(canvas,"boss",360,605,590,opacity=235)
        self.rings(canvas,360,585,206,t,count=2,color=(255,91,116,160))
        pts=[self.missile_path(j/100) for j in range(max(1,int(p*100)))]
        if len(pts)>1:
            self.line(canvas,pts,(255,85,33,70),34)
            self.line(canvas,pts,(255,162,37,210),13)
            self.line(canvas,pts,(255,246,167,245),4)
        x,y=self.missile_path(p)
        self.place(canvas,"weapon",x,y,360,angle=35+20*math.sin(t*10))
        self.txt(canvas,"必杀技 · 发射！",360,176,56,"#FFE3A1")
        if t>12:
            self.txt(canvas,"？？？",360,1090,94,"#FF8D9A",stroke=4)

    def freeze_stage(self, canvas, t):
        # Multi-speed freeze-frame, image turns monochrome-ish; comedic silence.
        p=clamp((t-13.5)/2.9)
        self.place(canvas,"boss",340,605,645,opacity=210)
        self.place(canvas,"weapon",675,285,300,angle=-40)
        self.line(canvas,[(115,1120),(250,850),(350,610),(500,290),(790,170)],(255,171,55,230),8)
        self.txt(canvas,"诶？",360,225,146,"#FFF7DF",stroke=5)
        self.txt(canvas,"这也能拐弯？！",360,1038,70,"#FF8A87",stroke=4)
        if (int(t*3)%2)==0:
            self.txt(canvas,"目标：一脸懵",360,1140,32,"#FAD7DC")

    def award_stage(self, canvas, t):
        p=ease((t-16.4)/2.0)
        self.accent(canvas,t,1.4)
        d=ImageDraw.Draw(canvas,"RGBA")
        cx,cy=self.P(360),self.P(470)
        size=self.P(145*(.65+.35*p))
        d.ellipse((cx-size,cy-size,cx+size,cy+size),fill=(250,171,59,220),
                  outline=(255,242,196,240),width=self.P(8))
        d.polygon([(cx-self.P(60),cy+self.P(120)),(cx-self.P(92),cy+self.P(260)),
                   (cx,cy+self.P(204)),(cx+self.P(92),cy+self.P(260)),
                   (cx+self.P(60),cy+self.P(120))], fill=(255,105,69,220))
        self.txt(canvas,"★",360,461,148,"#FFFBE8")
        self.txt(canvas,"最佳闪避奖",360,763,72,"#FFE9B1",stroke=3)
        self.txt(canvas,"伤害：保密",360,900,32,"#F6C1C4")
        self.txt(canvas,"求生欲：100%",360,957,32,"#FFB489")
        self.txt(canvas,"*本节目为玩家脑洞二创",360,1130,22,"#CCBACA")

    def ending(self, canvas, t):
        p=ease((t-20.4)/1.3)
        self.cover_bg(canvas,t,100)
        self.place(canvas,"hero",365,700,710,angle=math.sin(t*8)*5,
                   scale=.75+.18*p)
        self.txt(canvas,"小黑：",360,226,58,"#FFB777")
        self.txt(canvas,"它至少",360,353,76,"#FFEBD8",stroke=2)
        self.txt(canvas,"躲得很帅。",360,451,76,"#FFEBD8",stroke=2)
        self.txt(canvas,"NINJA MUST DIE 3 FAN EDIT",360,1125,22,"#DFBFD0")
        self.txt(canvas,"原立绘素材 / 忍3素材库",360,1176,22,"#BFB1C2")

    def frame(self,t):
        canvas = palette_image(self.w,self.h,t)
        if t < 2.5: self.title_stage(canvas,t)
        elif t < 6.8: self.showcase(canvas,t)
        elif t < 10.0: self.target_stage(canvas,t)
        elif t < 13.5: self.attack_stage(canvas,t)
        elif t < 16.4: self.freeze_stage(canvas,t)
        elif t < 20.4: self.award_stage(canvas,t)
        else: self.ending(canvas,t)
        # Stage-dependent strobe on hard cuts; no persistent shared screen frame.
        for cut in (2.5,6.8,10,13.5,16.4,20.4):
            dt=t-cut
            if 0<=dt<.14:
                curtain=Image.new("RGBA",(self.w,self.h),(255,238,198,int(135*(1-dt/.14))))
                canvas.alpha_composite(curtain)
        if 10 <= t < 13.5 and math.sin(t*67)>0.92:
            d=ImageDraw.Draw(canvas,"RGBA")
            d.rectangle((0,0,self.w,self.h),fill=(255,112,18,30))
        return canvas.convert("RGB")


def write_wave(path,arr,sr):
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes((np.clip(arr,-1,1)*32767).astype("<i2").tobytes())


def make_audio(path,seconds,preview=False):
    sr=24000
    samples=int(seconds*sr)
    audio=np.zeros(samples,dtype=np.float32)
    beats=112/60
    rng=np.random.default_rng(87)
    def add(src,when,gain=1):
        i=int(when*sr)
        j=min(samples,i+len(src))
        if i>=0 and j>i:
            audio[i:j] += src[:j-i]*gain
    def synth(f,dur,amp=.05):
        tt=np.arange(max(1,int(dur*sr)),dtype=np.float32)/sr
        envelope=np.minimum(1,tt/.008)*np.exp(-tt*9)
        return np.sin(tt*2*np.pi*f)*envelope*amp
    # Original rhythmic bed: fast electro pulse, deliberate gag-stop at 13.5–16.4.
    for b in range(int(seconds*beats)+1):
        when=b/beats
        if when>=seconds:break
        if 13.5 <= when < 16.4: continue
        add(synth(58,.19,.15),when)
        if b%2:
            hiss=rng.standard_normal(int(.085*sr)).astype(np.float32)
            hiss *= np.exp(-np.arange(len(hiss))/sr*55) * .03
            add(hiss,when)
        notes=[174.61,207.65,261.63,233.08]
        add(synth(notes[(b//4)%4],.24,.052),when)
    for when in (2.5,6.8,10,16.4,20.4):
        add(synth(900,.22,.105),when)
    # Ascending whoosh during flight + record scratch on gag freeze.
    for i in range(26):
        tt=10.0 + i*.126
        if tt >= seconds: break
        add(synth(260+27*i,.10,.07),tt)
    add(synth(110,.65,.18),13.52)
    if not preview:
        report={"voice_clips":[],"audio_mode":"original music + Chinese AI narration"}
        with tempfile.TemporaryDirectory() as tmp:
            for idx,(at,phrase,voice) in enumerate(VOICE_SCRIPT):
                if at>=seconds:continue
                mp3=Path(tmp)/("voice-%d.mp3"%idx)
                cmd=["edge-tts","--voice",voice,"--rate=+18%","--text",phrase,"--write-media",str(mp3)]
                subprocess.run(cmd,check=True,timeout=80,capture_output=True)
                raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(mp3),"-ac","1",
                                             "-ar",str(sr),"-f","f32le","pipe:1"])
                spoken=np.frombuffer(raw,dtype="<f4").copy()
                if not len(spoken):raise RuntimeError("Empty speech "+phrase)
                audible=np.flatnonzero(abs(spoken)>0.009)
                if not len(audible):raise RuntimeError("Silent narration "+phrase)
                spoken=spoken[max(0,audible[0]-1200):min(len(spoken),audible[-1]+3000)]
                if at+len(spoken)/sr >= seconds-.15:raise RuntimeError("Narration exceeds video duration")
                # Sidechain music locally, with 0.1 s attack and 0.2 s release.
                left=max(0,int((at-.1)*sr))
                right=min(samples,int((at+len(spoken)/sr+.2)*sr))
                vol=np.ones(right-left,dtype=np.float32)*.32
                aa=min(int(.1*sr),len(vol))
                bb=min(int(.2*sr),len(vol))
                if aa:vol[:aa]=np.linspace(1,.32,aa)
                if bb:vol[-bb:]=np.linspace(.32,1,bb)
                audio[left:right] *= vol
                spoken*=min(1.7,.54/max(.1,float(np.max(abs(spoken)))))
                add(spoken,at)
                report["voice_clips"].append({"at":at,"end":round(at+len(spoken)/sr,3),
                                              "voice":voice,"text":phrase})
        report_file=Path(str(path)).with_name("fentian-audio-report.json")
        report_file.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    peak=float(np.max(np.abs(audio))) if len(audio) else 0
    if peak>.96:audio*=.96/peak
    write_wave(path,audio,sr)


def render(args):
    film=Film(args.preview)
    duration=min(DURATION,float(args.seconds)) if args.seconds else DURATION
    frames=int(round(duration*film.fps))
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav=Path(tmp)/"sound.wav"
        make_audio(wav,duration,preview=args.preview)
        cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
             "-f","rawvideo","-pixel_format","rgb24",
             "-video_size",str(film.w)+"x"+str(film.h),
             "-framerate",str(film.fps),"-i","pipe:0",
             "-i",str(wav),"-map","0:v:0","-map","1:a:0",
             "-c:v","libx264","-preset","veryfast","-crf","21",
             "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
             "-movflags","+faststart","-shortest",str(output)]
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for i in range(frames):
                process.stdin.write(film.frame(i/film.fps).tobytes())
            process.stdin.close()
            err=process.stderr.read().decode("utf-8","replace")
            if process.wait()!=0:raise RuntimeError("FFmpeg render failed: "+err[-1800:])
        except Exception:
            process.kill()
            raise
    probe=subprocess.check_output(["ffprobe","-v","error","-show_entries",
                                   "format=duration:stream=codec_name,width,height","-of","json",str(output)])
    info=json.loads(probe)
    if abs(float(info["format"]["duration"])-duration)>.25:raise RuntimeError("Invalid duration")
    print("SUCCESS:",output,film.w,film.h,film.fps,duration,"seconds; original animation",flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--preview",action="store_true")
    parser.add_argument("--output",required=True)
    parser.add_argument("--seconds",type=float)
    render(parser.parse_args())
