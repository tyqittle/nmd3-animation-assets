#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立竖屏搞笑短片：真正的“随便打打”。使用忍3库真实立绘，不使用占位方块。"""
import math, argparse, subprocess, tempfile, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
ROOT=Path(__file__).resolve().parents[3]
W,H,FPS=540,960,24
K=W/720
DURATION=21.6
ASSETS={
 "hero":"assets/characters/xiaohei_01.png",
 "pro":"assets/characters/hayabusa_01.png",
 "boss":"assets/bosses/shark_01.png",
 "sword":"assets/weapons/wiki/wiki_weapon_101_fentian.png",
 "rooftop":"assets/backgrounds/wallpaper_rooftop_01.jpg",
 "moon":"assets/backgrounds/wallpaper_moon_01.jpg",
}
FONTS=["/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
       "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
       "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
def px(x):return round(x*K)
def clamp(t):return max(0.,min(1.,t))
def ease(t):t=clamp(t);return t*t*(3-2*t)
FONT_CACHE={}
def font(n):
 n=max(8,px(n))
 if n not in FONT_CACHE:
  p=next((z for z in FONTS if Path(z).is_file()),None)
  if not p:raise RuntimeError("CJK font missing")
  FONT_CACHE[n]=ImageFont.truetype(p,n)
 return FONT_CACHE[n]
class Movie:
 def __init__(self):
  self.img={}
  for k,p in ASSETS.items():
   im=Image.open(ROOT/p).convert("RGBA")
   if k not in ("rooftop","moon"):
    box=im.getchannel("A").getbbox()
    if box:im=im.crop(box)
    else:raise ValueError("Source PNG empty: "+p)
   self.img[k]=im
  self.bg={}
  for name in ("rooftop","moon"):
   i=self.img[name]
   ratio=max(W/i.width,H/i.height)*1.08
   sz=(math.ceil(i.width*ratio),math.ceil(i.height*ratio))
   i=i.resize(sz,Image.Resampling.BICUBIC)
   x=(i.width-W)//2;y=(i.height-H)//2
   self.bg[name]=ImageEnhance.Brightness(i.crop((x,y,x+W,y+H))).enhance(.53)
  self.cache={}
 def base(self,which,color):
  image=self.bg[which].copy()
  layer=Image.new("RGBA",(W,H),color)
  return Image.alpha_composite(image,layer)
 def txt(self,c,t,x,y,size,col="#FFF",stroke=4,anchor="mm"):
  d=ImageDraw.Draw(c)
  d.text((px(x+3),px(y+5)),t,font=font(size),anchor=anchor,fill="#090911",
       stroke_width=max(0,px(stroke+2)),stroke_fill="#090911")
  d.text((px(x),px(y)),t,font=font(size),anchor=anchor,fill=col,
       stroke_width=max(0,px(stroke)),stroke_fill="#100F19")
 def box(self,c,bb,color,r=14):
  ImageDraw.Draw(c,"RGBA").rounded_rectangle(tuple(px(i) for i in bb),radius=px(r),fill=color)
 def actor(self,c,name,x,y,height,angle=0,mirror=False,opacity=255):
  height=max(40,round(height/22)*22)
  angle=round(angle/5)*5
  key=(name,height,angle,mirror,opacity)
  if key not in self.cache:
   im=self.img[name]
   h=px(height);w=max(1,round(im.width*h/im.height))
   im=im.resize((w,h),Image.Resampling.LANCZOS)
   if mirror:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if angle:im=im.rotate(angle,Image.Resampling.BICUBIC,expand=True)
   if opacity!=255:im.putalpha(im.getchannel("A").point(lambda a:a*opacity//255))
   self.cache[key]=im
  im=self.cache[key]
  a=px(x)-im.width//2;b=px(y)-im.height//2
  l=max(0,-a);t=max(0,-b);r=min(im.width,W-a);bt=min(im.height,H-b)
  if l<r and t<bt:c.alpha_composite(im.crop((l,t,r,bt)),(a+l,b+t))
 def speed(self,c,t,col=(255,210,132,135),direction=1,count=20):
  d=ImageDraw.Draw(c,"RGBA")
  for i in range(count):
   x=((i*.6180339887+t*.23)%1)*720;y=100+(i*137)%1050
   a=25+(i%6)*39
   d.line((px(x),px(y),px(x+direction*a),px(y-28*direction)),
          fill=col,width=max(1,px(1+i%3)))
 def pulse(self,c,t,at):
  p=t-at
  if 0<=p<.12:
   lay=Image.new("RGBA",(W,H),(255,245,225,round(165*(1-p/.12))))
   c.alpha_composite(lay)
 def frame(self,t):
  if t<2.6:
   c=self.base("moon",(8,33,41,162))
   self.speed(c,t,(70,220,230,80),1,17)
   self.actor(c,"pro",530+190*(1-ease(t/.5)),770+8*math.sin(4*t),880)
   self.box(c,(43,156,378,206),(109,255,224,215),5)
   self.txt(c,"深渊野队 · 第1秒",60,180,27,"#071B23",0,"lm")
   self.txt(c,"队友说：",65,328,70,anchor="lm")
   self.txt(c,"这把",68,445,95,"#FEFEFF",anchor="lm")
   self.txt(c,"随便打打",68,555,78,"#73FFD5",anchor="lm")
   self.txt(c,"（大佬说的“随便”别信）",85,1118,28,anchor="lm")
  elif t<5.2:
   p=t-2.6
   c=self.base("rooftop",(22,51,62,135))
   self.actor(c,"hero",465+150*(1-ease(p/.38)),735+9*math.sin(8*t),700)
   self.txt(c,"我：懂了！",70,294,73,anchor="lm")
   self.txt(c,"休 闲 局",65,420,83,"#8BFFF0",anchor="lm")
   self.box(c,(64,530,380,620),(255,230,136,244),16)
   self.txt(c,"今天负责摸鱼",222,575,38,"#1D2630",0)
   for k in range(4):
    x=70+k*180
    self.txt(c,"✦",x,940+40*math.sin(t*2+k),27,"#FFE5AF",0)
  elif t<7.4:
   c=Image.new("RGBA",(W,H),(25,6,20,255))
   self.speed(c,t,(255,76,96,182),-1,35)
   self.actor(c,"boss",360,760,620,opacity=162)
   self.txt(c,"然而",360,340,91)
   self.txt(c,"开局 3 秒后",360,500,69,"#FF6C80")
   self.txt(c,"⚠ 画风突变 ⚠",360,1080,31,"#FFC2B8")
   self.pulse(c,t,6.65)
  elif t<11.2:
   p=t-7.4
   c=self.base("rooftop",(56,10,17,190))
   self.speed(c,t,(255,184,76,185),1,55)
   self.actor(c,"boss",860-450*ease(p/.9),765+17*math.sin(t*6),740)
   self.actor(c,"pro",-340+700*ease(p/1.03),710,850,angle=-9 if p<1.4 else 4)
   if p>.8:
    d=ImageDraw.Draw(c,"RGBA")
    for i in range(10):
     dy=px(16*i)
     d.line((-px(100),px(1050)+dy,px(800),px(335)+dy),
            fill=(255,235,185,max(10,196-18*i)),width=max(1,px(15-i)))
    self.actor(c,"sword",380,630,520,angle=43+9*math.sin(t*7),opacity=240)
    self.txt(c,"斩——！",360,335,118,"#FFF0C2")
   if p>2.45:
    self.txt(c,"BOSS：不是哥们？！",360,1110,42,"#FFDC92")
    self.txt(c,"？？？",500,225,60,"#FFF080")
   self.pulse(c,t,8.26)
  elif t<14.5:
   p=t-11.2
   c=self.base("moon",(23,14,55,176))
   self.actor(c,"hero",435,770,645+24*math.sin(p*13))
   self.txt(c,"等等！",360,295,111)
   self.txt(c,"我技能还没按！",360,423,64,"#FFDA7D")
   for k in range(6):
    self.txt(c,"？",78+(k%3)*255+20*math.sin(t*5+k),600+(k//3)*375,68,"#87F8FF",0)
   self.box(c,(90,1095,630,1171),(0,0,0,165),18)
   self.txt(c,"我到底是来干嘛的？",360,1133,34)
  elif t<18.5:
   c=self.base("moon",(47,9,28,160))
   self.actor(c,"pro",450,825,1020)
   self.box(c,(25,211,700,626),(2,5,15,194),24)
   self.txt(c,"我说随便打打",360,306,67)
   self.txt(c,"没说",360,431,65,"#FFBEC3")
   self.txt(c,"让你出手。",360,554,80,"#FFE07E")
   self.txt(c,"—— 隼白（疑似）",490,1129,30,"#FFD6DD")
  else:
   p=t-18.5
   c=self.base("rooftop",(9,33,27,183))
   self.speed(c,t,(197,255,215,105),-1,22)
   self.actor(c,"pro",554,810,950)
   self.actor(c,"hero",136,912,444)
   self.box(c,(38,236,681,580),(13,18,21,215),22)
   self.txt(c,"队友的工作分配",360,292,51,"#D3FFEF")
   self.txt(c,"大佬：负责输出",360,407,43,"#C8FFEA")
   self.txt(c,"我：负责喊",360,506,59,"#FFF5DE")
   self.txt(c,"666",360,757,171*(1+.065*math.sin(p*14)*math.exp(-p*.8)),"#FFE369",7)
   self.txt(c,"遇到这种队友，你会说什么？",360,1163,28)
  for at in (0,2.6,5.2,7.4,11.2,14.5,18.5):self.pulse(c,t,at)
  return c.convert("RGB")
def soundtrack(path,dur):
 sr=32000;n=int(sr*dur);a=np.zeros(n,np.float64)
 def add(start,sig,gain=1):
  i=int(start*sr)
  if 0<=i<n:
   end=min(len(sig),n-i)
   a[i:i+end]+=sig[:end]*gain
 beat=60/142
 for j in range(int(dur/beat)+2):
  st=j*beat;t=np.arange(int(sr*.28))/sr
  kick=np.sin(2*np.pi*(55*t+95*(1-np.exp(-t*24))/24))*np.exp(-t*21)
  add(st,kick,.65 if j%4==0 else .45)
  if j%2:
   v=np.random.default_rng(200+j).normal(size=int(sr*.15))
   add(st,v*np.exp(-np.arange(len(v))/sr*28),.19)
  for z in (0,.5):
   v=np.random.default_rng(3000+2*j+int(z*2)).normal(size=int(sr*.065))
   add(st+z*beat,v*np.exp(-np.arange(len(v))/sr*91),.12)
  if j>=11:
   f=[110,130.8,146.8,98,164.8,146.8][j%6]
   q=np.arange(int(sr*beat*.88))/sr
   add(st,(np.sin(2*np.pi*f*q)+.24*np.sin(2*np.pi*f*q*2))*np.exp(-q*5),.18)
 for st,f in [(0,392),(1.1,494),(2.6,587),(3.2,659),(4.4,494),(5.3,440),
              (7.4,880),(8.0,988),(9.0,1047),(11.2,392),(11.65,370),(12.1,330),
              (14.5,587),(15.1,554),(16,494),(18.5,784),(19.1,988),(19.55,1175)]:
  tt=np.arange(int(sr*.28))/sr
  add(st,(np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*2*f*tt))*np.exp(-tt*12),.13)
 for i,st in enumerate((2.6,5.2,7.4,11.2,14.5,18.5)):
  tt=np.arange(int(sr*.2))/sr
  noise=np.random.default_rng(1000+i).normal(size=tt.size)
  add(st-.055,noise*np.sin(np.pi*tt/.2)**2,.22)
  add(st,np.sin(2*np.pi*(60*tt+120*tt*tt))*np.exp(-tt*20),.36)
 a[int(sr*7.17):int(sr*7.4)]*=.1
 a=np.tanh(a*1.2);a*=.88/max(.1,np.max(np.abs(a)))
 with wave.open(str(path),"wb") as wf:
  wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(sr)
  wf.writeframes((a*32767).astype("<i2").tobytes())
def render(out,preview=False):
 duration=3.25 if preview else DURATION
 Path(out).parent.mkdir(parents=True,exist_ok=True)
 m=Movie()
 with tempfile.TemporaryDirectory() as td:
  sound=Path(td)/"score.wav";soundtrack(sound,duration)
  args=["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
        "-r",str(FPS),"-i","pipe:0","-i",str(sound),
        "-vf","scale=720:1280:flags=lanczos","-c:v","libx264",
        "-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-movflags","+faststart",
        "-shortest",str(out)]
  proc=subprocess.Popen(args,stdin=subprocess.PIPE)
  try:
   total=round(duration*FPS)
   for i in range(total):
    proc.stdin.write(m.frame(i/FPS).tobytes())
    if i%120==0:print("FRAMES",i,"/",total,flush=True)
   proc.stdin.close()
   if proc.wait(timeout=200):raise RuntimeError("ffmpeg export failed")
  except:
   proc.kill();raise
 print("FINISHED",out,Path(out).stat().st_size,flush=True)
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--preview",action="store_true")
 parser.add_argument("--output",required=True)
 a=parser.parse_args();render(a.output,a.preview)
