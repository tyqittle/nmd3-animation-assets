#!/usr/bin/env python3
"""Ninja Must Die 3 fan MV: procedural 2.5D camera, stylized ink, particles and beat cuts."""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os, math, random, subprocess
from pathlib import Path
random.seed(33)
W,H,FPS=960,540,24
ROOT=Path("ninja")
OUT=Path("output");OUT.mkdir(exist_ok=True)
BGS=[
"assets/backgrounds/wallpaper_moon_01.jpg",
"assets/backgrounds/wallpaper_rooftop_01.jpg",
"assets/backgrounds/wallpaper_torii_01.png",
"assets/backgrounds/wallpaper_ink_dragon_01.jpg",
"assets/backgrounds/wallpaper_blue_lake_01.jpg",
"assets/backgrounds/wallpaper_festival_01.jpg",
"assets/backgrounds/extra/wallpaper_lantern_lake_02.jpg",
]
CHARS=[
("HAYABUSA","assets/characters/hayabusa_01.png"),
("BLOOD SHADOW","assets/characters/blood_shadow_01.png"),
("KAGURA","assets/characters/extra/lin_kagura_01.png"),
("CANGYA","assets/characters/cangya_01.png"),
("YI HE","assets/characters/yihe_01.png"),
("NINJA","assets/characters/extra/hayabusa_yasha_01.png"),
("XIAO HEI","assets/characters/xiaohei_fire_01.png"),
("HAYABUSA","assets/characters/extra/hayabusa_anniversary_01.png"),
("BLOOD SHADOW","assets/characters/blood_shadow_01.png"),
("FINAL BATTLE","assets/bosses/red_crystal_dragon_01.png"),
("NINJA MUST DIE","assets/characters/hayabusa_01.png"),
]
DURATION=44
SCENE_SECONDS=4
def font(sz):
 for f in ["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
  if os.path.exists(f): return ImageFont.truetype(f,sz)
 return ImageFont.load_default()
F1,F2=font(61),font(20)
def load(p):
 im=Image.open(ROOT/p).convert("RGBA")
 return im
def cover(im,w,h):
 iw,ih=im.size; scale=max(w/iw,h/ih); im=im.resize((int(iw*scale)+2,int(ih*scale)+2),Image.Resampling.LANCZOS)
 return im.crop(((im.width-w)//2,(im.height-h)//2,(im.width+w)//2,(im.height+h)//2))
def character(im,height):
 scale=min(height/im.height, W*.76/im.width)
 return im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.Resampling.LANCZOS)
def frame(n):
 t=n/FPS; idx=min(int(t//SCENE_SECONDS),len(CHARS)-1); sub=t-idx*SCENE_SECONDS
 name,cp=CHARS[idx]; bg=load(BGS[idx%len(BGS)])
 bg=cover(bg,1080,640)
 x=int(60+24*math.sin(t*.62)+15*sub/4);y=int(50+13*math.cos(t*.46))
 base=bg.crop((x,y,x+W,y+H)).convert("RGB")
 # Teal/crimson tint, thin ink stripes, and edge shadows.
 wash=Image.new("RGB",(W,H),(5,16,26) if idx%2==0 else (28,5,22))
 base=Image.blend(base,wash,.25)
 base=ImageEnhance.Contrast(base).enhance(1.22)
 im=load(cp)
 im=character(im,530+int(sub*11))
 # Character slides slightly in opposition to background, with a slight cut-in.
 center=int(W*.68 + 55*math.sin((sub/4)*math.pi) + (1-sub/4)*45)
 cy=int(H*.57+10*math.sin(t*1.7))
 px=center-im.width//2;py=cy-im.height//2
 layer=Image.new("RGBA",(W,H))
 layer.alpha_composite(im,(px,py))
 # Glow behind subject made by blurred alpha
 glow=Image.new("RGBA",(W,H),(255,45,84,0))
 glow.putalpha(layer.getchannel("A").filter(ImageFilter.GaussianBlur(25)).point(lambda p:int(p*.42)))
 base=Image.alpha_composite(base.convert("RGBA"),glow)
 base=Image.alpha_composite(base,layer)
 d=ImageDraw.Draw(base,"RGBA")
 # vignette bars
 d.rectangle((0,0,W,36),fill=(0,0,0,195));d.rectangle((0,H-40,W,H),fill=(0,0,0,202))
 d.polygon([(0,0),(125,0),(0,210)],fill=(0,10,17,175))
 d.line([(35,110),(35,430)],fill=(244,64,86,190),width=3)
 d.text((58,127),name,font=F1,fill=(250,247,238,245),stroke_width=1,stroke_fill=(5,8,12))
 d.text((61,205),"NINJA MUST DIE 3  //  AMV",font=F2,fill=(250,95,110,245))
 d.text((60,H-28),f"CHAPTER {idx+1:02d}     //     SHADOWS IN MOTION",font=F2,fill=(230,230,230,200))
 d.text((W-110,H-28),f"{t:05.1f} S",font=F2,fill=(220,220,220,170))
 # particle embers animated deterministically
 rr=random.Random(idx*100+7)
 for j in range(58):
  sx=rr.randrange(W);sy=rr.randrange(H);speed=rr.uniform(25,105)
  xx=int((sx+math.sin(j*2)*22+t*13)%W); yy=int((sy-t*speed)%H)
  size=rr.choice([1,1,1,2,3])
  d.ellipse((xx,yy,xx+size,yy+size),fill=(255,110+rr.randrange(100),80,rr.randrange(60,190)))
 # attack diagonal flash accents timed at every 2 second pulse
 phase=t%2
 if phase<.14:
  opacity=int(185*(1-phase/.14))
  d.polygon([(W*.35,0),(W*.41,0),(W*.78,H),(W*.72,H)],fill=(250,248,240,opacity))
 if sub<.20:
  d.rectangle((0,0,W,H),fill=(255,255,255,int(105*(1-sub/.20))))
 return base.convert("RGB")
def main():
 import shutil
 if not shutil.which("ffmpeg"): raise SystemExit("ffmpeg missing")
 audio=Path("music/music/game-ost/jrpg-epic-rock-full.mp3")
 assert audio.exists(),audio
 # stream RGB frames to ffmpeg, avoid thousands of intermediate PNG files
 cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(audio),"-t",str(DURATION),"-filter_complex","[0:v]scale=1280:720:flags=lanczos,format=yuv420p[v];[1:a]afade=t=in:st=0:d=1.3,afade=t=out:st=41:d=3[a]","-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","20","-r",str(FPS),"-c:a","aac","-b:a","192k","-movflags","+faststart",str(OUT/"ninja3-shadow-bloom-mv.mp4")]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for i in range(FPS*DURATION):
   p.stdin.write(frame(i).tobytes())
 except BrokenPipeError: pass
 finally:
  try:p.stdin.close()
  except:pass
 assert p.wait()==0,"ffmpeg failed"
 print("OUTPUT",OUT/"ninja3-shadow-bloom-mv.mp4")
if __name__=="__main__":main()
