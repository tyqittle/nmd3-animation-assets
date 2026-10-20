#!/usr/bin/env python3
"""SHADOW PROTOCOL: music-reactive comic/cinematic Ninja 3 fan AMV.
Render with: python3 ninja/mv/make_mv.py
Uses only image files in ninja/ and audio file in music/.
"""
import os, math, random, subprocess, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps

W,H,FPS = 960,540,24
LENGTH = 48.0
ROOT=Path("ninja"); MUSIC=Path("music")
OUTPUT=Path("output");OUTPUT.mkdir(exist_ok=True)
AUDIO=MUSIC/"music/game-ost/jrpg-epic-rock-full.mp3"
BG=[
 "assets/backgrounds/wallpaper_moon_01.jpg",
 "assets/backgrounds/wallpaper_rooftop_01.jpg",
 "assets/backgrounds/wallpaper_torii_01.png",
 "assets/backgrounds/wallpaper_ink_dragon_01.jpg",
 "assets/backgrounds/wallpaper_blue_lake_01.jpg",
 "assets/backgrounds/wallpaper_festival_01.jpg",
 "assets/backgrounds/extra/wallpaper_lantern_lake_02.jpg"]
HERO=[
 ("HAYABUSA","assets/characters/hayabusa_01.png"),
 ("BLOOD SHADOW","assets/characters/blood_shadow_01.png"),
 ("KAGURA","assets/characters/extra/lin_kagura_01.png"),
 ("CANGYA","assets/characters/cangya_01.png"),
 ("YI HE","assets/characters/yihe_01.png"),
 ("NINJA","assets/characters/extra/hayabusa_yasha_01.png"),
 ("XIAO HEI","assets/characters/xiaohei_fire_01.png"),
 ("HAYABUSA","assets/characters/extra/hayabusa_anniversary_01.png")]
BOSS=["assets/bosses/red_crystal_dragon_01.png","assets/bosses/thunder_dragon_01.png"]
# A deliberately authored rhythm: prologue -> summons -> duel -> acceleration -> boss -> resolve.
# Cuts are NOT periodic; lengths tighten through the battle section.
SHOTS=[
 (0.0,2.8,"opening",0,0),(2.8,5.2,"reveal",0,1),
 (5.2,7.7,"hero",0,2),(7.7,10.0,"hero",1,3),
 (10.0,12.6,"duel",0,4),(12.6,15.0,"hero",2,5),
 (15.0,17.2,"hero",3,2),(17.2,19.2,"duel",2,1),
 (19.2,20.9,"hero",4,3),(20.9,22.6,"hero",5,4),
 (22.6,24.0,"duel",0,3),(24.0,25.5,"hero",6,5),
 (25.5,26.9,"hero",1,1),(26.9,28.3,"duel",0,4),
 (28.3,30.6,"boss",0,3),(30.6,32.4,"hero",7,2),
 (32.4,34.0,"boss",1,4),(34.0,36.2,"duel",1,3),
 (36.2,38.4,"hero",0,5),(38.4,41.4,"final",0,0),
 (41.4,44.8,"final",7,1),(44.8,48.0,"outro",0,0)]
ASSETS={}
def get(path):
 if path not in ASSETS: ASSETS[path]=Image.open(ROOT/path).convert("RGBA")
 return ASSETS[path]
def font(sz):
 for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
  if os.path.exists(p):return ImageFont.truetype(p,sz)
 return ImageFont.load_default()
FONT={s:font(s) for s in (14,18,26,42,72,108)}
def clamp(x,a=0,b=1):return max(a,min(b,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def fitcover(im,w,h):
 z=max(w/im.width,h/im.height);nw=max(w,round(im.width*z));nh=max(h,round(im.height*z))
 im=im.resize((nw,nh),Image.Resampling.BILINEAR)
 return im.crop(((nw-w)//2,(nh-h)//2,(nw+w)//2,(nh+h)//2))
def scaleheight(im,height):
 z=min(height/im.height,800/im.width)
 return im.resize((max(1,int(im.width*z)),max(1,int(im.height*z))),Image.Resampling.BILINEAR)
def paste(canvas,im,x,y):
 canvas.alpha_composite(im,(int(x),int(y)))
def backdrop(idx,t,p,energy):
 bg=get(BG[idx%len(BG)])
 xpan=50*math.sin(p*1.1+idx)+20*(p-.5)
 shot=fitcover(bg,1100,650).crop((int(70+xpan),int(55+22*math.sin(p+idx)),int(1030+xpan),int(595+22*math.sin(p+idx))))
 base=shot.convert("RGBA")
 tint=Image.new("RGBA",(W,H),(4,8,20,70) if idx%2==0 else (35,6,18,60))
 base=Image.alpha_composite(base,tint)
 return base
def cutmask(canvas,im,x,y,p,direction=1):
 # The character advances into frame with eased acceleration.
 sx=x+(1-ease(p))*250*direction
 paste(canvas,im,sx,y)
def inkspeed(d,t,amt=1):
 rng=random.Random(715)
 for j in range(25):
  y=rng.randrange(-100,H+100); xx=rng.randrange(-350,W+200)+int(350*((t*.8)%1))
  length=rng.randrange(50,270)*amt
  d.line((xx,y,xx+length,y-rng.randint(10,70)),fill=(235,242,250,rng.randrange(18,90)),width=rng.choice([1,2,3]))
def title(d,txt,y=370,big=False,alpha=255):
 f=FONT[108] if big else FONT[72]
 d.text((48,y),txt,font=f,fill=(245,244,234,alpha),stroke_width=2,stroke_fill=(6,8,18,alpha))
def subtitle(d,txt):
 d.rectangle((43,447,49,485),fill=(230,51,78,255))
 d.text((62,454),txt,font=FONT[18],fill=(230,231,233,220))
def beat_analysis():
 # Decode audio and derive short-term energy attacks; prevents non-musical fixed-interval flashing.
 b=subprocess.check_output(["ffmpeg","-v","error","-i",str(AUDIO),"-ac","1","-ar","8000","-f","f32le","-"])
 a=np.frombuffer(b,dtype="<f4")
 hop=400;chunks=len(a)//hop
 rms=np.sqrt(np.mean(a[:chunks*hop].reshape(chunks,hop)**2,axis=1)+1e-9)
 rms=np.maximum(0,rms)
 rise=np.maximum(0,rms-np.concatenate([[rms[0]],rms[:-1]]))
 rise=np.convolve(rise,np.ones(3)/3,mode="same")
 q=np.quantile(rise,.96)+1e-8
 return np.clip(rise/q,0,1)
def energyat(arr,t):
 ix=min(len(arr)-1,max(0,int(t*20)))
 return float(arr[ix])
def shot_for(t):
 for k,(start,end,kind,hero,bg) in enumerate(SHOTS):
  if t<end:return k,start,end,kind,hero,bg
 return len(SHOTS)-1,*SHOTS[-1]
def hero_image(hero,height=560):
 return scaleheight(get(HERO[hero][1]),height)
def screen(t,beats):
 k,a,b,kind,hi,bi=shot_for(t); p=(t-a)/(b-a); ep=ease(p)
 e=energyat(beats,t)
 # Smooth changes of scale and placement, authored by shot types.
 base=backdrop(bi,t,p,e)
 d=ImageDraw.Draw(base,"RGBA")
 if kind=="opening":
  d.rectangle((0,0,W,H),fill=(0,3,12,int(210*(1-ep))))
  d.ellipse((350-120*ep,95-110*ep,650+120*ep,395+110*ep),outline=(220,220,225,int(120*ep)),width=2)
  title(d,"SHADOW",215,False);subtitle(d,"A NINJA MUST DIE 3 FAN EDIT")
 elif kind=="reveal":
  im=hero_image(hi,675+int(80*ep))
  cutmask(base,im,600-im.width/2,H*.55-im.height/2,p,-1)
  d=ImageDraw.Draw(base,"RGBA");title(d,"AWAKEN",360);subtitle(d,"THE NIGHT HAS A NAME")
 elif kind=="hero":
  im=hero_image(hi,570+int(65*ep))
  # use opposing parallax movement, and figure crosses the title-free two thirds of the frame
  x=590-im.width/2+65*(.5-ep); y=H*.55-im.height/2
  cutmask(base,im,x,y,p,1 if k%2 else -1)
  d=ImageDraw.Draw(base,"RGBA")
  d.rectangle((0,0,400,H),fill=(3,7,18,75))
  if p>.1:
   d.text((55,255),HERO[hi][0],font=FONT[42],fill=(253,252,245,255))
   subtitle(d,"CHAPTER %02d // THE HUNT"%k)
 elif kind=="duel":
  l=hero_image(hi,570);r=hero_image((hi+1)%len(HERO),580)
  # opposing characters enter diagonally into a comic-book split panel
  for xx in (int(W*.49),int(W*.5)):
   d.line((xx-80,0,xx+80,H),fill=(254,246,235,220),width=4)
  paste(base,l,190-l.width/2-80*(1-ep),H*.54-l.height/2)
  # mirror second character for graphic contrast
  r=ImageOps.mirror(r)
  paste(base,r,750-r.width/2+110*(1-ep),H*.54-r.height/2)
  d=ImageDraw.Draw(base,"RGBA")
  d.polygon([(475,0),(490,0),(610,H),(595,H)],fill=(231,52,76,200))
  d.text((40,40),"VS",font=FONT[42],fill=(255,255,255,220))
 elif kind=="boss":
  im=scaleheight(get(BOSS[(k//2)%len(BOSS)]),480+int(120*ep))
  paste(base,im,630-im.width/2,H*.48-im.height/2)
  d=ImageDraw.Draw(base,"RGBA")
  d.text((43,80),"BOSS // INCOMING",font=FONT[42],fill=(255,74,93,255))
  inkspeed(d,t,1.5)
 elif kind=="final":
  im=hero_image(hi,650+int(ep*75))
  paste(base,im,665-im.width/2,H*.53-im.height/2)
  d=ImageDraw.Draw(base,"RGBA")
  d.rectangle((0,330,580,448),fill=(0,0,0,145))
  title(d,"NO RETREAT",350)
  inkspeed(d,t,1)
 else:
  d.rectangle((0,0,W,H),fill=(0,2,10,int(225*ep)))
  title(d,"NINJA",155,True)
  d.text((54,295),"MUST DIE 3",font=FONT[72],fill=(255,77,98,255))
  subtitle(d,"SHADOW PROTOCOL  //  FAN MUSIC VIDEO")
 d=ImageDraw.Draw(base,"RGBA")
 # Authored comic framing: letterbox and an animated timecode
 d.rectangle((0,0,W,29),fill=(0,0,0,220));d.rectangle((0,H-30,W,H),fill=(0,0,0,235))
 d.rectangle((35,H-18,int(35+(W-70)*t/LENGTH),H-15),fill=(238,63,89,210))
 d.text((42,6),"SHADOW PROTOCOL",font=FONT[14],fill=(243,244,245,220))
 d.text((W-158,6),"%02d:%02d // %02d"%(int(t//60),int(t%60),k+1),font=FONT[14],fill=(240,242,244,200))
 # Music-controlled impact overlays: only at significant local transients.
 if e>.42:
  power=clamp((e-.42)/.58)
  d.rectangle((0,29,W,H-30),fill=(255,237,222,int(42*power)))
  if kind in ("duel","boss","hero"):
   x=int(140+500*((t*.18)%1))
   d.polygon([(x-36,-20),(x-11,-20),(x+225,H+20),(x+198,H+20)],fill=(254,248,240,int(115*power)))
 # Layout-motivated match cuts: an edge streak during the first 120ms.
 if p<.09 and k>0:
  s=int(360*(1-p/.09))
  d.polygon([(0,0),(s,0),(s+190,H),(0,H)],fill=(244,245,244,int(170*(1-p/.09))))
 return base.convert("RGB")
def render():
 if not shutil.which("ffmpeg"):raise SystemExit("ffmpeg required")
 assert AUDIO.exists(),str(AUDIO)
 for p in BG+[x[1] for x in HERO]+BOSS:
  assert (ROOT/p).exists(),p
 beats=beat_analysis()
 path=OUTPUT/"ninja3-shadow-protocol-v2.mp4"
 cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-i",str(AUDIO),"-t",str(LENGTH),"-filter_complex","[0:v]scale=1280:720:flags=lanczos,format=yuv420p[v];[1:a]afade=t=in:st=0:d=1.5,afade=t=out:st=45:d=3[a]","-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","21","-c:a","aac","-b:a","192k","-movflags","+faststart",str(path)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(int(LENGTH*FPS)):
   proc.stdin.write(screen(i/FPS,beats).tobytes())
 finally:
  proc.stdin.close()
 if proc.wait():raise SystemExit("ffmpeg failed")
 print("Rendered:",path)
if __name__=="__main__":render()
