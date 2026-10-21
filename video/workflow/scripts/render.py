#!/usr/bin/env python3
"""Sprite-based offline MP4 renderer. No third-party hotlinks or surrogate characters."""
import argparse,json,math,subprocess,tempfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from check import load,asset
from audio import create as make_audio
FONT_PATHS=[
"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
"/usr/share/fonts/truetype/arphic/ukai.ttc",
"C:/Windows/Fonts/msyh.ttc",
"C:/Windows/Fonts/simhei.ttf",
]
def font(sz):
    for f in FONT_PATHS:
        if Path(f).is_file():return ImageFont.truetype(f,max(9,sz))
    raise RuntimeError("Missing Chinese font (install fonts-noto-cjk)")
def ease(x):
    v=max(0,min(1,x));return v*v*(3-2*v)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--recipe",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--quality",choices=("draft","final"),default="final")
    ap.add_argument("--tts",choices=("off","placeholder"),default="placeholder")
    ap.add_argument("--seconds",type=float,default=None)
    args=ap.parse_args()
    ep=load(args.recipe)
    W,H,F=(640,360,24) if args.quality=="draft" else (1280,720,30)
    scale=W/1280
    p=lambda v:round(v*scale)
    seconds=min(ep["duration"],args.seconds) if args.seconds else ep["duration"]
    if seconds<=0:raise ValueError("invalid seconds")
    font_sizes=(16,18,22,26,36,42,44,47,62)
    fonts={s:font(p(s)) for s in font_sizes}
    def text(d,label,x,y,size,color="#F4F0E7",anchor=None):
        d.text((p(x),p(y)),str(label),font=fonts[size],fill=color,anchor=anchor,
            stroke_fill="#10171f",stroke_width=max(1,p(1)))
    bg0=Image.open(asset(ep["background"])).convert("RGB")
    m=max(W/bg0.width,H/bg0.height)
    bg0=bg0.resize((math.ceil(bg0.width*m),math.ceil(bg0.height*m)),Image.Resampling.LANCZOS)
    bg=Image.new("RGBA",(W,H),(9,18,29,255))
    bg.paste(bg0,((W-bg0.width)//2,(H-bg0.height)//2))
    bg=Image.blend(bg,Image.new("RGBA",(W,H),(8,16,26,255)),.67)
    people=ep["characters"]
    imgs={k:Image.open(asset(c["path"])).convert("RGBA") for k,c in people.items()}
    cache={}
    def sprite(k,height,opacity):
        key=(k,p(height),opacity)
        if key not in cache:
            original=imgs[k]
            bbox=original.getchannel("A").getbbox()
            if bbox:original=original.crop(bbox)
            h=max(8,p(height));w=max(8,round(original.width/original.height*h))
            im=original.resize((w,h),Image.Resampling.LANCZOS)
            if opacity<255:im.putalpha(im.getchannel("A").point(lambda x:x*opacity//255))
            cache[key]=im
        return cache[key]
    def place(c,k,x,foot,height,t,opacity=255,shift=0):
        im=sprite(k,height,opacity)
        y=p(foot)-im.height+round(p(4)*math.sin(t*3))
        xx=p(x+shift)-im.width//2
        # Clip if a pose enters slightly outside the stage
        if xx<0 or y<0 or xx+im.width>W or y+im.height>H:
            l=max(0,-xx);top=max(0,-y);r=min(im.width,W-xx);bottom=min(im.height,H-y)
            if r>l and bottom>top:c.alpha_composite(im.crop((l,top,r,bottom)),(xx+l,y+top))
        else:c.alpha_composite(im,(xx,y))
    def box(d,coords,fill,outline=None,radius=12,width=2):
        d.rounded_rectangle(tuple(map(p,coords)),radius=max(2,p(radius)),fill=fill,outline=outline,width=max(1,p(width)))
    def frame(t):
        c=bg.copy()
        d=ImageDraw.Draw(c,"RGBA")
        s=next((x for x in ep["shots"] if x["start"]<=t<x["end"]),ep["shots"][-1])
        effect=s.get("effect","normal")
        if effect in ("panic","boss"):
            d.rectangle((0,0,W,H),fill=(212,36,58,72 if effect=="boss" else 45))
        for j in range(12):
            x=p((j*129+t*12)%1280)
            d.line((x,p(100),x+p(60),p(100)),fill=(178,214,221,34),width=max(1,p(2)))
        d.rectangle((0,0,W,p(31)),fill=(6,9,16,245))
        d.rectangle((0,p(688),W,H),fill=(6,9,16,245))
        box(d,(31,45,402,96),(15,25,37,240),(184,206,218,145),6)
        text(d,"忍 村 深 渊 · 家 族 语 音",55,70,18)
        if s["kind"] in ("intro","outro"):
            cast=list(people)[:5]
            for j,k in enumerate(cast):
                place(c,k,640+(j-(len(cast)-1)/2)*245,675,390,t,180)
            d=ImageDraw.Draw(c,"RGBA")
            box(d,(135,148,1145,510),(11,17,27,233),(237,194,138,200),14,3)
            text(d,s["lines"][0],640,235,62,"#F8E5CA","mm")
            for j,l in enumerate(s["lines"][1:]):text(d,l,640,353+j*70,36 if j else 44,"#FFDEAE","mm")
        elif s["kind"]=="system":
            actor=s.get("actor") or ("ali" if "ali" in people else next(iter(people)))
            place(c,actor,980,671,495,t,190,math.sin(t*3)*65)
            d=ImageDraw.Draw(c,"RGBA")
            box(d,(190,233,1090,510),(34,25,40,244),(255,115,126,230),14,4)
            text(d,s["lines"][0],640,325,62,"#FFB8B3","mm")
            text(d,s["lines"][1],640,419,36,"#F7E9E2","mm")
        else:
            k=s["speaker"];l=t-s["start"];color=people[k]["color"]
            others=[x for x in people if x!=k]
            for j,key in enumerate(others[:3]):
                place(c,key,760+j*196,625,260,t,66)
            sh=10*math.sin(t*67) if effect=="panic" and l<.7 else 0
            place(c,k,972,671,583,t,255,100*(1-ease(l/.5))+sh)
            d=ImageDraw.Draw(c,"RGBA")
            box(d,(42,230,741,547),(15,25,39,245),color,12,3)
            d.rectangle((p(43),p(231),p(54),p(546)),fill=color)
            box(d,(75,250,360,306),color,None,5)
            text(d,people[k]["name"]+"  /  NINJA 3",89,278,22,"#131A21")
            for j,line in enumerate(s["lines"][:2]):
                text(d,line,81,377+j*80,42 if j==0 else 47,"#F8F1EA" if j==0 else color)
            if effect=="boss":
                box(d,(698,122,1199,212),(174,24,56,243),(255,199,205,255),6,4)
                text(d,"BOSS 已加入家族语音",948,169,26,"#FFFFFF","mm")
            elif effect=="panic":
                text(d,"指挥红温",1030,165,36,"#FFDCB8","mm")
            text(d,"VOICE  /  "+people[k]["name"],58,605,18,color)
            box(d,(147,635,1138,681),(4,11,20,235),None,4)
            text(d,"  ".join(s["lines"]),641,659,22,"#F8F7F3","mm")
        d=ImageDraw.Draw(c,"RGBA")
        d.rectangle((0,p(706),W,H),fill=(19,41,56,255))
        d.rectangle((0,p(706),max(1,int(W*t/ep["duration"])),H),fill=(244,190,137,255))
        return c.convert("RGB")
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        track=Path(tmp)/"track.wav";make_audio(ep,track,seconds,args.tts)
        args_ff=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo",
             "-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(F),
             "-i","pipe:0","-i",str(track),"-c:v","libx264","-preset","veryfast",
             "-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
             "-movflags","+faststart","-shortest",str(output)]
        process=subprocess.Popen(args_ff,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for i in range(round(seconds*F)):process.stdin.write(frame(i/F).tobytes())
            process.stdin.close()
            err=process.stderr.read().decode("utf-8","replace")
            if process.wait()!=0:raise RuntimeError("FFmpeg error: "+err)
        except Exception:
            process.kill()
            raise
    info=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height",
        "-of","json",str(output)],capture_output=True,text=True,check=True)
    result=json.loads(info.stdout)
    codecs={stream.get("codec_name") for stream in result["streams"]}
    if "h264" not in codecs or "aac" not in codecs:raise RuntimeError("Expected MP4 H.264 + AAC")
    if abs(float(result["format"]["duration"])-seconds)>.3:raise RuntimeError("Bad duration")
    print(f"SUCCESS: {output}, {W}x{H} at {F}fps, {seconds}s with audio")
if __name__=="__main__":main()
