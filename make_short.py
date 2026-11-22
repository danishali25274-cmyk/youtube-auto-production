#!/usr/bin/env python3
import argparse, subprocess, sys, urllib.request, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/"assets"; OUT=ROOT/"output"; WORK=OUT/"work"
VOICE="en_GB-alan-medium"
VOICE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/"
NARRATION=("In 1775, thirteen American colonies stood against British rule. "
"Arguments over taxes and representation had grown into open conflict. "
"After fighting began at Lexington and Concord, the colonies moved toward independence. "
"On the fourth of July, 1776, leaders adopted the Declaration of Independence. "
"The war continued for years, and in 1783 Britain recognised the United States. "
"The revolution changed the course of history.")
SCENES=[
("1775","THIRTEEN COLONIES","Tension with Britain reaches a breaking point"),
("LEXINGTON","THE FIRST CLASHES","Fighting begins in Massachusetts"),
("1776","A DECLARATION","The colonies announce independence"),
("1781","A TURNING POINT","Allied forces help secure victory at Yorktown"),
("1783","A NEW NATION","Britain recognises American independence")]
def run(cmd, **kw):
    print("+"," ".join(map(str,cmd)))
    subprocess.run(list(map(str,cmd)),check=True,**kw)
def getfont(n,b=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if b else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,n) if Path(p).exists() else ImageFont.load_default()
def slide(i,kicker,title,sub):
    w,h=1080,1920; im=Image.new("RGB",(w,h)); d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/h; d.line((0,y,w,y),fill=(int(15+16*t),int(25+8*t),int(42+4*t)))
    d.ellipse((650,-180,1320,490),fill=(85,45,35),outline=(190,145,80),width=8)
    d.ellipse((-260,1220,480,1940),fill=(32,55,72),outline=(190,145,80),width=6)
    d.rounded_rectangle((70,330,1010,1450),radius=42,fill=(229,213,177),outline=(197,158,99),width=8)
    d.text((130,430),"AMERICAN REVOLUTION",font=getfont(38,True),fill=(85,52,35))
    d.line((130,510,950,510),fill=(145,100,55),width=5)
    d.text((130,650),kicker,font=getfont(64,True),fill=(120,48,38))
    for j,line in enumerate(textwrap.wrap(title,22)): d.text((130,800+j*105),line,font=getfont(82,True),fill=(31,39,49))
    for j,line in enumerate(textwrap.wrap(sub,34)): d.text((130,1120+j*58),line,font=getfont(36),fill=(63,56,47))
    d.rounded_rectangle((130,1540,950,1640),radius=24,fill=(150,45,35))
    d.text((165,1560),f"HISTORY • {i+1}/5",font=getfont(34,True),fill=(255,245,220))
    d.text((70,1790),"A SHORT DOCUMENTARY",font=getfont(30,True),fill=(229,213,177))
    p=WORK/f"slide_{i:02}.png"; im.save(p); return p
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--topic",default="American Revolution")
    ap.add_argument("--music",default=str(ASSETS/"music.mp3"))
    ap.add_argument("--output",default=str(OUT/"american_revolution_short.mp4"))
    a=ap.parse_args()
    for p in (ASSETS,OUT,WORK): p.mkdir(parents=True,exist_ok=True)
    for name in (VOICE+".onnx",VOICE+".onnx.json"):
        p=ASSETS/name
        if not p.exists():
            print("Downloading Piper voice",name)
            urllib.request.urlretrieve(VOICE_URL+name,p)
    (OUT/"narration.txt").write_text(NARRATION,encoding="utf-8")
    voice=OUT/"voice.wav"
    run(["piper","--model",ASSETS/(VOICE+".onnx"),"--config",ASSETS/(VOICE+".onnx.json"),"--output_file",voice],input=NARRATION,text=True)
    clips=[]
    for i,s in enumerate(SCENES):
        p=slide(i,*s); clip=WORK/f"scene_{i:02}.mp4"; clips.append(clip)
        run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",p,"-vf",
             "zoompan=z='min(zoom+0.0007,1.06)':d=180:s=1080x1920:fps=30,format=yuv420p",
             "-t","6","-an","-c:v","libx264","-preset","veryfast",clip])
    concat=WORK/"concat.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in clips),encoding="utf-8")
    visuals=WORK/"visuals.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",concat,"-c","copy",visuals])
    from faster_whisper import WhisperModel
    model=WhisperModel("tiny",device="cpu",compute_type="int8")
    segments,_=model.transcribe(str(voice),word_timestamps=False)
    def stamp(t):
        ms=int(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    rows=[]
    for n,seg in enumerate(segments,1):
        rows += [str(n),f"{stamp(seg.start)} --> {stamp(seg.end)}",seg.text.strip(),""]
    cap=OUT/"captions.srt"; cap.write_text("\n".join(rows),encoding="utf-8")
    music=Path(a.music)
    if music.exists():
        aud=["-i",music,"-filter_complex","[1:a]volume=0.13[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2[a]","-map","0:v","-map","[a]"]
    else:
        print("No assets/music.mp3: using a quiet generated ambient tone.")
        aud=["-f","lavfi","-i","sine=frequency=110:duration=30","-filter_complex","[1:a]volume=0.025,lowpass=f=220[m];[0:a][m]amix=inputs=2:duration=first[a]","-map","0:v","-map","[a]"]
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
    run(["ffmpeg","-y","-loglevel","error","-i",visuals,"-i",voice,*aud,
         "-vf",f"subtitles={cap.as_posix()}:force_style='FontName=DejaVu Sans,FontSize=18,Bold=1,Outline=2,Shadow=1,Alignment=2,MarginV=170'",
         "-t","30","-r","30","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-shortest",out])
    print("MP4 READY:",out.resolve())
if __name__=="__main__": main()
