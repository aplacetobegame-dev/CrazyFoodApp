"""25-second revision: rigid UI, animated chef, guitar/drums, clean Foley.

Reuses the completed Seedance footage. The v5 deliverable is preserved.
"""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import math
import shutil
import subprocess
import wave
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"commercial-final-v5"
spec=importlib.util.spec_from_file_location("v5",SOURCE/"compose_commercial.py")
v5=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v5)
W,H,FPS,S=v5.W,v5.H,v5.FPS,v5.S
PAPER,INK,RED,PICKLE,MUTED=v5.PAPER,v5.INK,v5.RED,v5.PICKLE,v5.MUTED
rr,text,paste,sc,box=v5.rr,v5.text,v5.paste,v5.sc,v5.box
RES=Image.Resampling.LANCZOS


def crime_value(t):
    return round(100*min(max(t/1.55,0),1)**.9)


def expression(value):
    return "A LITTLE CURSED" if value<28 else "UNSTABLE" if value<58 else "MUTATING" if value<85 else "RADIOACTIVE" if value<100 else "FOOD FELONY"


@lru_cache(maxsize=240)
def chef_face(value,size=260,phase=0):
    # The radioactive styling belongs to this fictional mascot, not the actor.
    n=600
    im=Image.new("RGBA",(n,n),(0,0,0,0))
    d=ImageDraw.Draw(im)
    u=n/200
    def b(rect):return tuple(round(v*u) for v in rect)
    def line(points,fill=INK,width=4):d.line([(round(x*u),round(y*u)) for x,y in points],fill=fill,width=round(width*u),joint="curve")
    glow=Image.new("RGBA",(n,n),(0,0,0,0));gd=ImageDraw.Draw(glow)
    gd.ellipse(b((12,23,189,195)),fill=(120,255,10,100+round(value*.65)))
    glow=glow.filter(ImageFilter.GaussianBlur(round(11*u)))
    im=Image.alpha_composite(im,glow);d=ImageDraw.Draw(im)
    color="#D5F88A" if value<28 else "#BCF95F" if value<58 else "#A7F52B" if value<85 else "#9EFF00"
    blob=[]
    for i in range(64):
        a=i*math.tau/64
        rad=79+(4+value/20)*math.sin(5*a+.5)+3*math.sin(9*a)
        blob.append((round((100+rad*math.cos(a))*u),round((106+rad*math.sin(a))*u)))
    d.polygon(blob,fill=color)
    if value>=85:
        for angle in [-80,-35,10,145,190,235]:
            a=math.radians(angle)
            line([(100+86*math.cos(a),100+86*math.sin(a)),(100+97*math.cos(a),100+97*math.sin(a))],RED,4)
    skin="#EDFFD0" if value<28 else "#DEFF9B" if value<58 else "#D4FF58" if value<85 else "#C8FF2B"
    d.rounded_rectangle(b((58,83,146,171)),radius=round(23*u),fill=skin,outline=INK,width=round(4*u))
    # Union the hat's puffs before stroking to avoid internal circle seams.
    mask=Image.new("L",(n,n),0);md=ImageDraw.Draw(mask)
    for rect in [(31,42,91,101),(63,21,130,94),(110,41,171,103)]:md.ellipse(b(rect),fill=255)
    md.rectangle(b((54,66,151,110)),fill=255)
    arr=np.array(mask)
    contours,_=cv2.findContours(arr,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    rgba=np.array(im)
    cv2.drawContours(rgba,contours,-1,(*tuple(int(PAPER[i:i+2],16) for i in (1,3,5)),255),cv2.FILLED)
    cv2.drawContours(rgba,contours,-1,(*tuple(int(INK[i:i+2],16) for i in (1,3,5)),255),round(4*u),cv2.LINE_AA)
    im=Image.fromarray(rgba);d=ImageDraw.Draw(im)
    d.rounded_rectangle(b((56,96,149,114)),radius=round(5*u),fill=PAPER,outline=INK,width=round(4*u))
    twitch=math.sin(phase*math.pi/2)*(1+value/55)
    if value<28:
        eyes=[(69,122,92,142),(111,118,137,143)]
        pupils=[(83+twitch,132),(122-twitch,128)]
        mouth=[(81,151),(128,146),(123,163),(94,166)]
    elif value<58:
        eyes=[(67,122,94,145),(112,117,141,146)]
        pupils=[(84+twitch,136),(125-twitch,126)]
        mouth=[(77,149),(131,145),(128,164),(90,168)]
    else:
        eyes=[(65,120,96,148),(112,115,143,149)]
        pupils=[(79+twitch,136-twitch/2),(131-twitch,127+twitch/2)]
        mouth=[(74,151),(131,143),(134,162),(112,174),(81,167)]
    for eye in eyes:d.ellipse(b(eye),fill="#FFFFFF",outline=INK,width=round(3*u))
    for x,y in pupils:
        d.ellipse(b((x-4,y-5,x+4,y+5)),fill=INK)
        if value>=85:d.ellipse(b((x-1,y-2,x+2,y+1)),fill=RED)
    line([(65,118),(88,112)],width=3)
    line([(114,111),(141,117)],width=3)
    d.polygon([(round(x*u),round(y*u)) for x,y in mouth],fill=INK)
    # Irregular buck teeth and a crooked grin, deliberately cartoonish.
    d.polygon([b((83,151))[0:2],b((93,149))[0:2],b((92,160))[0:2],b((85,158))[0:2]],fill=PAPER)
    d.polygon([b((103,149))[0:2],b((115,146))[0:2],b((113,158))[0:2],b((104,157))[0:2]],fill=PAPER)
    if value>=58:
        d.polygon([b((122,147))[0:2],b((130,145))[0:2],b((129,154))[0:2],b((123,157))[0:2]],fill=PAPER)
    if value>=85:
        d.ellipse(b((98,116,110,128)),fill=PAPER,outline=INK,width=round(2*u))
        d.ellipse(b((102+twitch/2,120,106+twitch/2,125)),fill=RED)
        d.ellipse(b((109,163,123,169)),fill=RED)
        d.ellipse(b((151,151,187,187)),fill="#F5BA47",outline=INK,width=round(2.5*u))
        cx,cy=169,169
        for angle in [-90,30,150]:
            points=[]
            for a in np.linspace(angle,angle+60,12):points.append(((cx+13*math.cos(math.radians(a)))*u,(cy+13*math.sin(math.radians(a)))*u))
            for a in np.linspace(angle+60,angle,12):points.append(((cx+5*math.cos(math.radians(a)))*u,(cy+5*math.sin(math.radians(a)))*u))
            d.polygon(points,fill=INK)
        d.ellipse(b((cx-2.5,cy-2.5,cx+2.5,cy+2.5)),fill=INK)
    angle=0 if value<28 else -3 if value<58 else 3 if value<85 else -5
    return im.rotate(angle,resample=Image.Resampling.BICUBIC).resize((size,size),RES)


BASE_PHONE_UI=v5.phone_ui
def funky_phone_ui(kind,t):
    if kind!="meter":return BASE_PHONE_UI(kind,t)
    value=crime_value(t)
    im=Image.new("RGB",(sc(400),sc(760)),PAPER);d=ImageDraw.Draw(im)
    text(d,(22,24),"Food Felonies",27,role="display")
    text(d,(22,97),"Choose your chaos.",28,role="display")
    text(d,(22,141),"Normal is optional.",17,MUTED)
    face=chef_face(value,sc(247),int(t*12)%4);im.paste(face,(sc(77),sc(185)),face)
    text(d,(22,468),"Crime level",22,bold=True)
    text(d,(378,470),f"{value}/100",22,RED,"mono",anchor="ra")
    rr(d,(25,533,375,543),"#D5D2C7",5)
    xx=25+350*value/100
    rr(d,(25,533,xx,543),RED,5)
    d.ellipse(box((xx-12,526,xx+12,550)),fill=RED,outline="white",width=sc(2))
    text(d,(25,574),"Normal",16,MUTED)
    text(d,(375,574),"Food Felony",16,RED,anchor="ra")
    rr(d,(22,635,378,696),RED,29)
    text(d,(200,665),"Generate recipe  >",22,"white",bold=True,anchor="mm")
    text(d,(200,730),expression(value),18,RED,"mono",anchor="mm")
    return np.array(im)


def rigid_track(path,duration=3,segments=None):
    original=v5.precompute_phone_track(path,duration,segments)
    fps=original["fps"];quads=original["quads"]
    ranges=segments or [(0,round(2*fps),1.75),(round(2*fps),round(3*fps),2.45)]
    stable={}
    for start,end,preferred in ranges:
        indices=[i for i in range(start,end) if i in quads]
        if not indices:continue
        anchor=min(indices,key=lambda i:abs(i/fps-preferred))
        fixed=quads[anchor].astype(np.float32)
        params=[]
        for i in indices:
            matrix,inliers=cv2.estimateAffinePartial2D(fixed,quads[i].astype(np.float32),method=cv2.RANSAC,ransacReprojThreshold=12,maxIters=5000,confidence=.999)
            if matrix is None:matrix=np.array([[1.,0.,0.],[0.,1.,0.]])
            a,b=matrix[0,0],matrix[1,0]
            params.append([math.log(max(math.hypot(a,b),.1)),math.atan2(b,a),matrix[0,2],matrix[1,2]])
        values=np.array(params);values[:,1]=np.unwrap(values[:,1])
        for column in range(4):
            values[:,column]=np.convolve(np.pad(values[:,column],(2,2),mode="edge"),np.array([1,2,3,2,1])/9,mode="valid")
        for k,i in enumerate(indices):
            scale=math.exp(values[k,0]);angle=values[k,1];tx,ty=values[k,2:]
            matrix=np.array([[scale*math.cos(angle),-scale*math.sin(angle),tx],[scale*math.sin(angle),scale*math.cos(angle),ty]])
            q=np.c_[fixed,np.ones(4)]@matrix.T
            center=q.mean(axis=0)
            stable[i]=(center+(q-center)*.972).astype(np.float32)
    return {"fps":fps,"quads":stable}


def juice_meter(layer,t):
    d=ImageDraw.Draw(layer);value=crime_value(t)
    rr(d,(32,760,688,1200),PAPER,30)
    text(d,(63,791),"HOW FAR WILL YOU GO?",28,role="display")
    size=sc(210*(1+.04*math.sin(20*t)*math.exp(-8*max(t-1.55,0)) if t>=1.55 else 1))
    face=chef_face(value,size,int(t*12)%4)
    layer.paste(face,(sc(55)+(sc(210)-size)//2,sc(855)+(sc(210)-size)//2),face)
    text(d,(645,889),f"{value}",76,RED,"display",anchor="ra")
    text(d,(645,991),expression(value),23,RED,"mono",anchor="ra")
    rr(d,(65,1090,655,1102),"#D7D2C6",6)
    xx=65+590*value/100
    rr(d,(65,1090,xx,1102),RED,6)
    d.ellipse(box((xx-17,1079,xx+17,1113)),fill=RED,outline="white",width=sc(3))
    text(d,(65,1144),"Normal",20,MUTED)
    text(d,(655,1144),"Food Felony",20,RED,anchor="ra")


def pop_layer(layer,t,duration=.28):
    if t>=duration:return layer
    p=max(0,t/duration)
    scale=.86+.14*(1+2.6*(p-1)**3+1.6*(p-1)**2)
    resized=layer.resize((round(W*scale),round(H*scale)),RES)
    canvas=v5.new_layer();canvas.paste(resized,((W-resized.width)//2,(H-resized.height)//2),resized)
    return canvas


def punch(im,t):
    if t<3.15 or 15<=t<17:return im
    strength=0
    for at in [3.15,4.8,6,7.85,8.8,9.4,11,17,20]:
        dt=t-at
        if 0<=dt<.28:strength=max(strength,.035*math.exp(-dt*13))
    if not strength:return im
    z=1+strength;nw,nh=round(W*z),round(H*z)
    enlarged=im.resize((nw,nh),RES)
    return enlarged.crop(((nw-W)//2,(nh-H)//2,(nw+W)//2,(nh+H)//2))


def visual_frame(t,readers,photos,state):
    if t>=22:
        card=v5.end_card(t-22).convert("RGBA")
        background=Image.new("RGBA",(W,H),PAPER)
        return Image.alpha_composite(background,pop_layer(card,t-22,.22)).convert("RGB")
    index=0 if t<6 else 1 if t<11 else 2 if t<15 else 3
    local=t-[0,6,11,15][index]
    source_time=local
    if index==3:
        source_time=local*v5.COMMUNITY_CUT_1/2 if local<2 else v5.COMMUNITY_CUT_1+(local-2)*(v5.COMMUNITY_CUT_2-v5.COMMUNITY_CUT_1)/3 if local<5 else v5.COMMUNITY_CUT_2+(local-5)*(7-v5.COMMUNITY_CUT_2)/2
    frame=readers[index].get(source_time)
    if (index==0 and local<3) or index==2:
        track=state["phone" if index==0 else "share"]
        quad=track["quads"].get(round(local*track["fps"]))
        frame=v5.composite_phone(frame,funky_phone_ui("meter" if index==0 and local<2 else "concept",local),quad)
    im=Image.fromarray(frame)
    im=ImageEnhance.Contrast(im).enhance(1.035)
    im=ImageEnhance.Color(im).enhance(1.055)
    im=punch(im,t).convert("RGBA")
    layer=v5.new_layer();d=ImageDraw.Draw(layer)
    if t<2:
        rr(d,(35,79,685,159),PAPER,25)
        text(d,(360,119),"How criminal is dinner?",34,role="display",anchor="mm")
        juice_meter(layer,t)
    elif t<3.15:
        rr(d,(85,210,635,971),PAPER,29)
        text(d,(360,261),"YOU'RE MAKING THIS.",32,role="display",anchor="mm")
        paste(layer,v5.CONCEPT,(108,309,504,505),.82,20)
        text(d,(360,876),"Vegetable Gelatin",34,role="display",anchor="mm")
        layer=pop_layer(layer,t-2,.27)
    elif t<4.8:
        v5.lower_pill(layer,"Bad idea?" if t<4.08 else "Perfect.",y=1108)
    elif t<6:
        values=[("GELATIN",40,150),("CELERY",199,140),("PEPPER",348,140),("ONION",497,180)]
        for i,(label,x,width) in enumerate(values):
            if t<4.85+i*.15:continue
            shift=round(20*(1-v5.ease((t-4.85-i*.15)/.18)))
            rr(d,(x,1114+shift,x+width,1174+shift),RED if i%2 else PICKLE,18)
            text(d,(x+width/2,1144+shift),label,20,"white" if i%2 else INK,"display",anchor="mm")
    elif t<9.4:
        v5.lower_pill(layer,"CHOP." if t<7.8 else "MIX." if t<8.8 else "POUR.",y=1120)
    elif t<11:
        rr(d,(36,85,285,141),PAPER,17)
        text(d,(160,113),"After chilling",22,MUTED,anchor="mm")
        if t>10.2:v5.lower_pill(layer,"JIGGLE.",y=1120)
    elif t<15:
        if t>=11.25:
            v5.comparison(layer,local)
            layer=pop_layer(layer,t-11.25,.24)
    elif t<17:
        v5.lower_pill(layer,"YOUR TURN.",y=1120)
        if t>15.3:
            rr(d,(23,371,221,415),RED,8);text(d,(122,393),"GUILTY",21,"white","mono",anchor="mm")
        if t>15.83:
            rr(d,(499,371,697,415),v5.brand.GREEN,8);text(d,(598,393),"ACQUITTED",19,"white","mono",anchor="mm")
    elif t<20:
        v5.lower_pill(layer,"CHALLENGE ACCEPTED.",y=1120)
    else:
        v5.uploads(layer,t-20,photos)
        if t>21.15:
            rr(d,(167,82,553,142),PICKLE,20);text(d,(360,112),"PROOF UPLOADED",24,INK,"display",anchor="mm")
    return Image.alpha_composite(im,layer).convert("RGB")


def make_foley():
    sr=48000;n=sr*25;rng=np.random.default_rng(62026);s=np.zeros(n)
    def add(signal,start,gain=1):
        a=round(start*sr);b=min(n,a+len(signal))
        if a>=0 and b>a:s[a:b]+=signal[:b-a]*gain
    def click(length=.027):
        t=np.arange(round(sr*length))/sr
        noise=rng.standard_normal(len(t))
        filtered=np.convolve(noise,np.ones(5)/5,mode="same")
        return filtered*np.exp(-t*180)+.15*np.sin(2*np.pi*180*t)*np.exp(-t*110)
    # Short tactile interface clicks, not tonal beeps or celebratory vocals.
    for time in [.18,.4,.6,.78,.94,1.08,1.21,1.33,1.43,1.52]:add(click(.018),time,.16)
    for time in [1.57,12.95,20.2,20.53,20.86,21.3]:add(click(),time,.25)
    # A restrained camera shutter: two mechanical noise transients.
    for time in [20.12,20.48,20.83]:
        add(click(.045),time,.23);add(click(.024),time+.055,.15)
    for time in [2,6,11.25,15,17,20,22]:
        t=np.arange(round(sr*.10))/sr
        noise=rng.standard_normal(len(t));noise=np.convolve(noise,np.ones(15)/15,mode="same")
        add(noise*np.sin(np.pi*t/.1)**2,time,.12)
    fade=np.minimum(np.arange(n)/(.01*sr),1)*np.minimum((n-1-np.arange(n))/(.22*sr),1)
    s=np.tanh(s)*fade
    with wave.open(str(ROOT/"audio/clean-foley.wav"),"wb") as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.column_stack((s,s))*32767).astype("<i2").tobytes())


def mix_audio(picture=None):
    # Retain only the quiet, non-vocal chopping/mixing from the cooking clip.
    # Every other native actor/reaction track, including the 10s exclamation,
    # is completely absent from this mix.
    filters=("[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:3.12,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.03,afade=t=out:st=2.9:d=0.22,volume=0.45,adelay=6000|6000,apad=whole_dur=25[kitchen];"
             "[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:25,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.012,afade=t=out:st=24.55:d=0.45,volume=0.90[music];"
             "[3:a]volume=0.65[fx];[music][kitchen][fx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-15.5:TP=-2:LRA=8[a]")
    cmd=[shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(picture or ROOT/"picture.mp4"),"-i",str(SOURCE/"raw/scene-1.mp4"),"-i",str(ROOT/"audio/guitar-drums-original.mp3"),"-i",str(ROOT/"audio/clean-foley.wav"),"-filter_complex",filters,"-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-t","25","-movflags","+faststart",str(ROOT/"food-felonies-25s-rock-v6.mp4")]
    subprocess.run(cmd,check=True)


def replace_opening():
    """Rebuild only the revised first two seconds of an existing v6 picture."""
    state={"phone":rigid_track(SOURCE/"raw/scene-0.mp4")}
    readers=[v5.Reader(SOURCE/"raw/scene-0.mp4"),None,None,None]
    prefix=ROOT/"opening-radioactive.mp4"
    cmd=[shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","pipe:0","-an","-c:v","libx264","-preset","fast","-crf","16","-pix_fmt","yuv420p","-t","2",str(prefix)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    board=Image.new("RGB",(1080,1360),PAPER);d=ImageDraw.Draw(board)
    snapshots=[0,.4,.75,1.1,1.55,1.85]
    for i,t in enumerate(snapshots):
        preview=[v5.Reader(SOURCE/"raw/scene-0.mp4"),None,None,None]
        im=visual_frame(t,preview,[],state)
        board.paste(im.resize((360,640),RES),((i%3)*360,(i//3)*680))
        d.text(((i%3)*360+10,(i//3)*680+650),f"{t:.2f}s",fill=INK,font=v5.brand.font(20))
        preview[0].cap.release()
    board.save(ROOT/"qa/radioactive-opening-review.jpg",quality=95)
    for i in range(60):proc.stdin.write(visual_frame(i/30,readers,[],state).tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError("Opening render failed")
    picture=ROOT/"picture-radioactive.mp4"
    filters="[0:v]trim=duration=2,setpts=PTS-STARTPTS[p];[1:v]trim=start=2:end=25,setpts=PTS-STARTPTS[r];[p][r]concat=n=2:v=1:a=0,fps=30[v]"
    subprocess.run([shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(prefix),"-i",str(ROOT/"picture.mp4"),"-filter_complex",filters,"-map","[v]","-c:v","libx264","-preset","fast","-crf","16","-pix_fmt","yuv420p","-t","25",str(picture)],check=True)
    mix_audio(picture)
    print("Radioactive chef revision rendered.",flush=True)


def render():
    phone=rigid_track(SOURCE/"raw/scene-0.mp4")
    share=rigid_track(SOURCE/"raw/scene-2.mp4",4,[(0,96,.3)])
    state={"phone":phone,"share":share}
    photos=[Image.open(SOURCE/f"references/community-result-{i}.jpg").convert("RGB") for i in range(1,4)]
    readers=[v5.Reader(SOURCE/f"raw/scene-{i}.mp4") for i in range(4)]
    make_foley()
    snapshots=[0,.45,.9,1.6,2.15,3.9,6.6,10.2,12.8,15.7,18.5,20.9,23.2]
    board=Image.new("RGB",(4*270,4*520),PAPER);d=ImageDraw.Draw(board)
    for i,t in enumerate(snapshots):
        preview_readers=[v5.Reader(SOURCE/f"raw/scene-{j}.mp4") for j in range(4)]
        im=visual_frame(t,preview_readers,photos,state)
        im.save(ROOT/f"qa/frame-{i:02d}.jpg",quality=95)
        board.paste(im.resize((270,480),RES),((i%4)*270,(i//4)*520))
        d.text(((i%4)*270+9,(i//4)*520+486),f"{t:04.2f}s",fill=INK,font=v5.brand.font(19))
        for reader in preview_readers:reader.cap.release()
    board.save(ROOT/"qa/contact-sheet-v6.jpg",quality=95)
    cmd=[shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","pipe:0","-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-t","25",str(ROOT/"picture.mp4")]
    with (ROOT/"render.log").open("w") as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for i in range(750):
            proc.stdin.write(visual_frame(i/30,readers,photos,state).tobytes())
            if i%150==0:print(f"Revised {i//30}/25 seconds",flush=True)
        proc.stdin.close();code=proc.wait()
    if code:raise RuntimeError((ROOT/"render.log").read_text())
    mix_audio()
    data=json.loads(subprocess.check_output([shutil.which("ffprobe"),"-v","error","-show_streams","-show_format","-of","json",str(ROOT/"food-felonies-25s-rock-v6.mp4")],text=True))
    (ROOT/"verification.json").write_text(json.dumps(data,indent=2),encoding="utf-8")
    print("Revised export ready:",ROOT/"food-felonies-25s-rock-v6.mp4",flush=True)


if __name__=="__main__":render()
