"""Composite the approved 25s Seedance commercial with precise branded UI.

Never submits generations. Requires the four confirmed clips in raw/scene-N.mp4.
UI text deliberately follows the user's approved no-prompt/no-AI-label treatment.
"""
from pathlib import Path
import importlib.util
import math
import json
import shutil
import subprocess
import wave
import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("brand", ROOT.parent / "commercial-v2-plan/build_brand_storyboard.py")
brand = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand)
S, W, H, FPS = 1.5, 1080, 1920, 30
PAPER, INK, RED, PICKLE, MUTED = brand.PAPER, brand.INK, brand.RED, brand.PICKLE, brand.MUTED
RES = Image.Resampling.LANCZOS
DURATIONS = [6, 5, 4, 7]
COMMUNITY_CUT_1 = 58/24
COMMUNITY_CUT_2 = 119/24


def sc(v):
    return round(v*S)


def box(values):
    return tuple(sc(v) for v in values)


def rr(d, values, fill, radius=18, outline=None, width=1):
    d.rounded_rectangle(box(values), radius=sc(radius), fill=fill, outline=outline, width=sc(width))


def text(d, xy, value, size=25, color=INK, role="body", bold=False, anchor=None):
    d.text(tuple(sc(v) for v in xy), value, font=brand.font(sc(size), role, bold), fill=color, anchor=anchor)


def paste(im, asset, rect, focus=.5, rounded=0, contain=False):
    x,y,w,h = rect
    if contain:
        factor=min(sc(w)/asset.width,sc(h)/asset.height)
        fitted=asset.resize((round(asset.width*factor),round(asset.height*factor)),RES)
        canvas=Image.new("RGB",(sc(w),sc(h)),PAPER)
        canvas.paste(fitted,((canvas.width-fitted.width)//2,(canvas.height-fitted.height)//2))
        asset=canvas
    else:
        asset = brand.v1.cover(asset, sc(w), sc(h), focus)
    if rounded:
        mask = Image.new("L", asset.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,asset.width-1,asset.height-1),radius=sc(rounded),fill=255)
        im.paste(asset, (sc(x),sc(y)), mask)
    else:
        im.paste(asset, (sc(x),sc(y)))


def ease(v):
    v=max(0,min(1,v))
    return 1-(1-v)**3


def new_layer():
    return Image.new("RGBA", (W,H), (0,0,0,0))


CONCEPT = Image.open(ROOT/"references/gelatin-concept.png").convert("RGB")
ORIGINAL = Image.open(ROOT/"references/gelatin-original.png").convert("RGB")


def phone_ui(kind, t):
    im = Image.new("RGB", (sc(400),sc(760)), PAPER)
    d=ImageDraw.Draw(im)
    text(d,(22,26),"Food Felonies",27,role="display")
    d.line(box((22,77,378,77)),fill="#DED9CB",width=2)
    if kind=="meter":
        text(d,(22,111),"Create recipe",32,role="display")
        text(d,(22,173),"Ingredients on hand",20,bold=True)
        for value,x,y,w in [("Gelatin",22,218,150),("Celery",188,218,143),("Green pepper",22,277,204),("Onion",241,277,137)]:
            rr(d,(x,y,x+w,y+43),PICKLE,13)
            text(d,(x+13,y+10),value,17)
        value=round(15+85*ease(t/1.45))
        text(d,(22,374),"Weirdness level",22,bold=True)
        text(d,(378,377),f"{value}/100",22,RED,"mono",anchor="ra")
        rr(d,(25,447,375,456),"#D5D3C9",5)
        xx=25+350*value/100
        rr(d,(25,447,xx,456),RED,5)
        d.ellipse(box((xx-13,438,xx+13,464)),fill=RED,outline="white",width=3)
        text(d,(25,486),"Normal",16,MUTED)
        text(d,(375,486),"Food Felony",16,RED,anchor="ra")
        rr(d,(22,555,378,614),"#F8D3CC" if value==100 else "#EEE9DD",15)
        text(d,(200,584),"CRIME MODE: MAX" if value==100 else "TURN UP THE WEIRD",19,RED,"mono",anchor="mm")
        rr(d,(22,661,378,719),RED,27)
        text(d,(200,690),"Generate recipe  >",22,"white",bold=True,anchor="mm")
    else:
        rr(d,(22,105,224,139),brand.MUSTARD,4)
        text(d,(33,113),"CASE FILE #0041",16,role="mono")
        text(d,(22,167),"Vegetable Gelatin",30,role="display")
        paste(im,CONCEPT,(22,225,356,315),.83,14)
        rr(d,(22,568,378,632),"#F8D3CC",15)
        text(d,(39,585),"CRIME LEVEL",16,RED,"mono")
        text(d,(362,600),"92/100",27,RED,"display",anchor="rm")
        rr(d,(22,661,378,719),RED,27)
        text(d,(200,690),"Show recipe  >",22,"white",bold=True,anchor="mm")
    return np.array(im)


def ordered_quad(points):
    points=np.asarray(points,dtype=np.float32).reshape(4,2)
    sums=points.sum(axis=1)
    diffs=np.diff(points,axis=1).flatten()
    return points[[np.argmin(sums),np.argmin(diffs),np.argmax(sums),np.argmax(diffs)]]


def detect_phone(frame, previous=None):
    small=cv2.resize(frame,(540,960))
    gray=cv2.cvtColor(small,cv2.COLOR_RGB2GRAY)
    edges=cv2.Canny(gray,45,125)
    contours,_=cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    hsv_small=cv2.cvtColor(small,cv2.COLOR_RGB2HSV)
    bright=((hsv_small[:,:,1]<52)&(hsv_small[:,:,2]>168)).astype(np.uint8)*255
    bright=cv2.morphologyEx(bright,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    color_contours,_=cv2.findContours(bright,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    contours=list(contours)+list(color_contours)
    candidates=[]
    for contour in contours:
        area=cv2.contourArea(contour)
        if not 2000<area<340000:
            continue
        peri=cv2.arcLength(contour,True)
        quad=cv2.approxPolyDP(contour,.035*peri,True)
        if len(quad)!=4 or not cv2.isContourConvex(quad):
            continue
        q=ordered_quad(quad)
        width=(np.linalg.norm(q[1]-q[0])+np.linalg.norm(q[2]-q[3]))/2
        height=(np.linalg.norm(q[3]-q[0])+np.linalg.norm(q[2]-q[1]))/2
        if not 1.35<height/max(width,1)<3.5:
            continue
        src=np.float32([[0,0],[100,0],[100,180],[0,180]])
        mat=cv2.getPerspectiveTransform(q,src)
        patch=cv2.warpPerspective(small,mat,(100,180))[18:82,18:82]
        mean=patch.mean(axis=(0,1))
        std=float(patch.std(axis=(0,1)).mean())
        if mean.min()<120 or std>53:
            continue
        # Empty cream phone displays are smooth and bright; cabinetry is penalized.
        score=3*(53-std)+math.sqrt(area)*.07
        if previous is not None:
            dist=np.linalg.norm(q.mean(axis=0)-previous.mean(axis=0)/2)
            score-=dist*.5
        else:
            score-=abs(q.mean(axis=0)[0]-270)*.08
        candidates.append((score,q*2))
    if not candidates:
        return previous
    best=max(candidates,key=lambda item:item[0])[1]
    if previous is not None and np.linalg.norm(best.mean(axis=0)-previous.mean(axis=0))<120:
        best=previous*.35+best*.65
    return best


def composite_phone(frame, ui, quad):
    if quad is None:
        return frame
    height,width=ui.shape[:2]
    matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[width,0],[width,height],[0,height]]),quad)
    warped=cv2.warpPerspective(ui,matrix,(W,H))
    mask=cv2.warpPerspective(np.full((height,width),255,np.uint8),matrix,(W,H))
    hsv=cv2.cvtColor(frame,cv2.COLOR_RGB2HSV)
    # Preserve real fingers crossing the display over the composited UI.
    skin=(hsv[:,:,0]<28)&(hsv[:,:,1]>60)&(hsv[:,:,2]>70)
    mask[skin]=0
    alpha=mask.astype(np.float32)[:,:,None]/255
    return (warped*alpha+frame*(1-alpha)).astype(np.uint8)


def precompute_phone_track(path,duration=3,segments=None):
    cap=cv2.VideoCapture(str(path))
    fps=cap.get(cv2.CAP_PROP_FPS)
    frames=[]
    while len(frames)<round(fps*duration):
        ok,bgr=cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(cv2.resize(bgr,(W,H)),cv2.COLOR_BGR2RGB))
    cap.release()
    tracks={}
    ranges=segments or [(0,min(len(frames),round(2*fps)),1.75),(round(2*fps),len(frames),2.45)]
    for start,end,preferred in ranges:
        if start>=end:
            continue
        candidates=[]
        for i in range(start,end):
            q=detect_phone(frames[i])
            if q is not None:
                candidates.append((abs(i/fps-preferred),i,q))
        if not candidates:
            continue
        _,anchor,q=min(candidates,key=lambda item:item[0])
        tracks[anchor]=q
        for direction in [-1,1]:
            i=anchor
            points=q.copy().astype(np.float32)
            old_gray=cv2.cvtColor(frames[i],cv2.COLOR_RGB2GRAY)
            while start<=i+direction<end:
                nxt=i+direction
                gray=cv2.cvtColor(frames[nxt],cv2.COLOR_RGB2GRAY)
                moved,status,error=cv2.calcOpticalFlowPyrLK(old_gray,gray,points.reshape(-1,1,2),None,winSize=(41,41),maxLevel=4,
                    criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,35,.01))
                moved=moved.reshape(4,2)
                valid=status.reshape(-1).astype(bool)&(np.linalg.norm(moved-points,axis=1)<85)
                if valid.any():
                    delta=np.median((moved-points)[valid],axis=0)
                    moved[~valid]=points[~valid]+delta
                    points=moved
                tracks[nxt]=points.copy()
                old_gray=gray
                i=nxt
    return {"fps":fps,"quads":tracks}


def lower_pill(layer,label,tint=RED,y=1137):
    d=ImageDraw.Draw(layer)
    rr(d,(37,y,683,y+70),tint,27)
    text(d,(360,y+35),label,29,"white",role="display",anchor="mm")


def comparison(layer,t):
    d=ImageDraw.Draw(layer)
    p=ease((t-.3)/.35)
    dy=round((1-p)*90)
    top=445+dy
    rr(d,(28,top,692,1191+dy),PAPER,26)
    text(d,(54,top+31),"Show the evidence.",36,role="display")
    text(d,(360,top+89),"SAVORY VEGETABLE GELATIN",17,MUTED,"mono",anchor="mm")
    text(d,(195,top+134),"The idea",25,role="display",anchor="mm")
    text(d,(525,top+134),"The result",25,role="display",anchor="mm")
    paste(layer,CONCEPT,(48,top+166,305,286),.83,18)
    paste(layer,ORIGINAL,(367,top+166,305,286),.5,18,contain=True)
    rr(d,(50,top+492,670,top+580),RED,40)
    shared=t>2.7
    text(d,(360,top+536),"Shared!" if shared else "Share my result  >",30,"white",bold=True,anchor="mm")
    if 2.05<t<2.7:
        rad=15+45*(t-2.05)/.65
        d.ellipse(box((560-rad,top+535-rad,560+rad,top+535+rad)),outline=brand.MUSTARD,width=sc(4))
    text(d,(360,top+630),"Commercial dramatization",16,MUTED,anchor="mm")


def uploads(layer,t,photos):
    d=ImageDraw.Draw(layer)
    top=459
    rr(d,(22,top,698,1225),PAPER,25)
    text(d,(48,top+27),"Cooked Results",37,role="display")
    text(d,(48,top+80),"Same recipe. Their versions.",21,MUTED)
    for i,photo in enumerate(photos):
        phase=ease((t-.1-i*.25)/.45)
        if not phase:
            continue
        x=41+i*226
        yy=top+138+round((1-phase)*40)
        paste(layer,photo,(x,yy,208,300),.6,15)
        rr(d,(x,yy+313,x+208,yy+356),"#E2EECF",13)
        text(d,(x+104,yy+334),"Photo added",18,brand.GREEN,bold=True,anchor="mm")
    rr(d,(48,top+540,672,top+621),RED,35)
    text(d,(360,top+579),"I cooked it - add proof",27,"white",bold=True,anchor="mm")
    text(d,(360,top+682),"Commercial dramatization",16,MUTED,anchor="mm")


def end_card(t):
    im=Image.new("RGB",(W,H),PAPER)
    d=ImageDraw.Draw(im)
    text(d,(360,83),"CASE CLOSED. APP OPEN.",23,RED,"mono",anchor="mm")
    wm=brand.wordmark
    width=520
    paste(im,wm,(100,172,width,width*wm.height/wm.width))
    tag=brand.reference.crop((53,263,253,356))
    paste(im,tag,(144,658,432,432*tag.height/tag.width))
    offset=round(16*(1-ease(t/.4)))
    rr(d,(45,954+offset,675,1055+offset),RED,48)
    text(d,(360,1004+offset),"Download Food Felonies",34,"white",bold=True,anchor="mm")
    text(d,(360,1130),"Commit your first food crime.",31,role="display",anchor="mm")
    return im


class Reader:
    def __init__(self,path):
        self.cap=cv2.VideoCapture(str(path))
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open {path}")
        self.fps=self.cap.get(cv2.CAP_PROP_FPS)
        self.current=-1
        self.cached=None

    def get(self,t):
        goal=round(t*self.fps)
        while self.current<goal:
            ok,im=self.cap.read()
            if not ok:
                break
            self.cached=im
            self.current+=1
        if self.cached is None:
            raise RuntimeError("Empty video")
        im=cv2.cvtColor(self.cached,cv2.COLOR_BGR2RGB)
        if im.shape[:2]!=(H,W):
            im=np.array(brand.v1.cover(Image.fromarray(im),W,H))
        return im


def community_photos():
    cap=cv2.VideoCapture(str(ROOT/"raw/scene-3.mp4"))
    cap.set(cv2.CAP_PROP_POS_MSEC,6050)
    ok,frame=cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Cannot extract community result photos")
    frame=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    photos=[]
    for i in range(3):
        photo=frame.crop((i*frame.width//3,round(frame.height*.62),(i+1)*frame.width//3,round(frame.height*.96)))
        photo.save(ROOT/f"references/community-result-{i+1}.jpg",quality=95)
        photos.append(photo)
    return photos


def visual_frame(t,readers,photos,state):
    if t>=22:
        return end_card(t-22)
    index=0 if t<6 else 1 if t<11 else 2 if t<15 else 3
    offset=[0,6,11,15][index]
    local=t-offset
    source_time=local
    if index==3:
        if local<2:
            source_time=local*COMMUNITY_CUT_1/2
        elif local<5:
            source_time=COMMUNITY_CUT_1+(local-2)*(COMMUNITY_CUT_2-COMMUNITY_CUT_1)/3
        else:
            source_time=COMMUNITY_CUT_2+(local-5)*(7-COMMUNITY_CUT_2)/2
    frame=readers[index].get(source_time)
    if index==0 and local<3.0:
        track=state.get("phone_track")
        if track:
            quad=track["quads"].get(round(local*track["fps"]))
        else:
            if local<.08 or 1.9<local<2.1:
                state["quad"]=None
            state["quad"]=detect_phone(frame,state.get("quad"))
            quad=state["quad"]
        frame=composite_phone(frame,phone_ui("meter" if local<2 else "concept",local),quad)
    elif index==2:
        track=state.get("share_track")
        quad=track["quads"].get(round(local*track["fps"])) if track else detect_phone(frame)
        frame=composite_phone(frame,phone_ui("concept",local),quad)
    im=Image.fromarray(frame).convert("RGBA")
    layer=new_layer()
    d=ImageDraw.Draw(layer)
    if t<2:
        rr(d,(35,83,685,155),PAPER,25)
        text(d,(360,119),"How criminal is dinner?",33,role="display",anchor="mm")
        value=round(15+85*ease(t/1.45))
        rr(d,(35,835,685,1168),PAPER,25)
        text(d,(63,876),"Weirdness level",29,bold=True)
        text(d,(653,881),f"{value}/100",28,RED,"mono",anchor="ra")
        rr(d,(65,960,655,972),"#D7D2C6",6)
        xx=65+590*value/100
        rr(d,(65,960,xx,972),RED,6)
        d.ellipse(box((xx-17,949,xx+17,983)),fill=RED,outline="white",width=sc(3))
        text(d,(65,1015),"Normal",21,MUTED)
        text(d,(655,1015),"Food Felony",21,RED,anchor="ra")
        text(d,(360,1100),"CRIME MODE: MAX" if value==100 else "TURN IT ALL THE WAY UP",27,RED,"display",anchor="mm")
    elif t<3.15:
        rr(d,(92,217,628,943),PAPER,28)
        text(d,(360,263),"You're making this.",32,role="display",anchor="mm")
        paste(layer,CONCEPT,(110,310,500,490),.82,20)
        text(d,(360,855),"Vegetable Gelatin",32,role="display",anchor="mm")
        lower_pill(layer,"Vegetable gelatin. Seriously.",y=1110)
    elif t<4.8:
        lower_pill(layer,"That grin says everything.",y=1110)
    elif t<6:
        lower_pill(layer,"Gelatin + celery + pepper + onion",y=1110)
    elif 6<=t<9.4:
        lower_pill(layer,"Make it.",y=1120)
    elif 9.4<=t<11:
        rr(d,(36,85,265,136),PAPER,16)
        text(d,(150,110),"After chilling",20,MUTED,anchor="mm")
    elif 11.3<=t<15:
        comparison(layer,local)
    elif 15<=t<17:
        lower_pill(layer,"Your turn.",y=1120)
        if t>15.35:
            rr(d,(23,371,221,415),RED,8)
            text(d,(122,393),"GUILTY",21,"white","mono",anchor="mm")
        if t>15.95:
            rr(d,(499,371,697,415),brand.GREEN,8)
            text(d,(598,393),"ACQUITTED",19,"white","mono",anchor="mm")
    elif 17<=t<20:
        lower_pill(layer,"Now everyone is making it.",y=1120)
    elif 20<=t<22:
        uploads(layer,t-20,photos)
    im=Image.alpha_composite(im,layer).convert("RGB")
    return im


def make_music():
    # Original 128 BPM cue and sync hits, composed procedurally for this edit.
    sr=48000
    n=sr*25
    signal=np.zeros(n,np.float64)
    rng=np.random.default_rng(410725)

    def add(s,start,gain=1):
        a=round(start*sr)
        b=min(n,a+len(s))
        if a<n and b>a:
            signal[a:b]+=s[:b-a]*gain

    step=60/128
    bass=[73.416,73.416,110,130.813,73.416,87.307,98,110]
    for beat in range(math.ceil(25/step)):
        pos=beat*step
        tt=np.arange(round(.27*sr))/sr
        kick=np.sin(2*np.pi*(48*tt+58*.028*(1-np.exp(-tt/.028))))*np.exp(-tt*22)
        add(kick,pos,.34)
        tb=np.arange(round(.34*sr))/sr
        f=bass[beat%8]
        add((np.sin(2*np.pi*f*tb)+.25*np.sin(2*np.pi*2*f*tb))*np.exp(-tb*7),pos+.035,.25)
        for off in [0,step/2]:
            th=np.arange(round(.065*sr))/sr
            noise=rng.standard_normal(len(th))
            noise-=np.concatenate(([0],noise[:-1]))*.8
            add(noise*np.exp(-th*70),pos+off,.04)
        if beat%2:
            ts=np.arange(round(.13*sr))/sr
            add(rng.standard_normal(len(ts))*np.exp(-ts*33),pos,.09)
        if beat%4 in [0,2,3]:
            tm=np.arange(round(.3*sr))/sr
            fm=[293.665,349.228,440,523.251][beat%4]
            add((np.sin(2*np.pi*fm*tm)+.3*np.sin(4*np.pi*fm*tm))*np.exp(-tm*13),pos+step/2,.09)
    for pos in [0,1.55,6,11,15,17,20,22]:
        tt=np.arange(round(.55*sr))/sr
        add(np.sin(2*np.pi*(43*tt+35*.06*(1-np.exp(-tt/.06))))*np.exp(-tt*9),pos,.4)
    for pos in [5.78,10.78,14.78,16.78,19.78,21.78]:
        tt=np.arange(round(.22*sr))/sr
        noise=rng.standard_normal(len(tt))
        add(np.convolve(noise,np.ones(8)/8,mode="same")*np.sin(np.pi*tt/.22)**2,pos,.18)
    for pos in [12.85,20.25,20.6,20.95]:
        tt=np.arange(round(.14*sr))/sr
        add(np.sin(2*np.pi*900*tt)*np.exp(-tt*32),pos,.13)
    fade=np.minimum(np.arange(n)/(.015*sr),1)*np.minimum((n-1-np.arange(n))/(.6*sr),1)
    signal=np.tanh(signal*.9)*fade
    signal=signal/max(np.max(np.abs(signal)),.001)*.72
    with wave.open(str(ROOT/"music.wav"),"wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes((np.column_stack((signal,signal)) * 32767).astype("<i2").tobytes())


def render():
    readers=[Reader(ROOT/f"raw/scene-{i}.mp4") for i in range(4)]
    photos=community_photos()
    phone_track=precompute_phone_track(ROOT/"raw/scene-0.mp4")
    share_track=precompute_phone_track(ROOT/"raw/scene-2.mp4",4,[(0,96,.3)])
    state={"phone_track":phone_track,"share_track":share_track}
    make_music()
    snapshots=[.7,2.5,3.9,5.5,7,9.9,12.6,15.7,18.5,20.9,23.5]
    board=Image.new("RGB",(4*270,3*520),PAPER)
    bd=ImageDraw.Draw(board)
    for i,t in enumerate(snapshots):
        readers_preview=[Reader(ROOT/f"raw/scene-{j}.mp4") for j in range(4)]
        im=visual_frame(t,readers_preview,photos,{"phone_track":phone_track,"share_track":share_track})
        im.save(ROOT/f"qa/frame-{i:02d}.jpg",quality=95)
        board.paste(im.resize((270,480),RES),((i%4)*270,(i//4)*520))
        bd.text(((i%4)*270+10,(i//4)*520+486),f"{t:04.1f}s",fill=INK,font=brand.font(19))
        for reader in readers_preview:
            reader.cap.release()
    board.save(ROOT/"qa/contact-sheet.jpg",quality=95)
    visual_frame(3.7,[Reader(ROOT/f"raw/scene-{j}.mp4") for j in range(4)],photos,{}).save(ROOT/"poster.jpg",quality=95)
    cmd=[shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-t","25",str(ROOT/"picture.mp4")]
    with (ROOT/"render.log").open("w") as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        for i in range(750):
            proc.stdin.write(visual_frame(i/FPS,readers,photos,state).tobytes())
            if i%150==0:
                print(f"Composited {i//30}/25 seconds",flush=True)
        proc.stdin.close()
        code=proc.wait()
    if code:
        raise RuntimeError((ROOT/"render.log").read_text())
    mix_and_verify()


def mix_and_verify():
    audio_cmd=[shutil.which("ffmpeg"),"-hide_banner","-loglevel","error","-y","-i",str(ROOT/"picture.mp4")]
    for i in range(4):
        audio_cmd += ["-i",str(ROOT/f"raw/scene-{i}.mp4")]
    audio_cmd += ["-i",str(ROOT/"music.wav")]
    parts=[]
    for i,duration in enumerate(DURATIONS):
        if i!=3:
            parts.append(f"[{i+1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{duration},apad=whole_dur={duration},asetpts=PTS-STARTPTS[a{i}]")
        else:
            parts.append("[4:a]aresample=48000,aformat=channel_layouts=stereo,asplit=3[c0][c1][c2]")
            parts.append(f"[c0]atrim=0:{COMMUNITY_CUT_1},asetpts=PTS-STARTPTS,atempo={COMMUNITY_CUT_1/2}[cr]")
            parts.append(f"[c1]atrim={COMMUNITY_CUT_1}:{COMMUNITY_CUT_2},asetpts=PTS-STARTPTS,atempo={(COMMUNITY_CUT_2-COMMUNITY_CUT_1)/3}[cc]")
            parts.append(f"[c2]atrim={COMMUNITY_CUT_2}:7,asetpts=PTS-STARTPTS,atempo={(7-COMMUNITY_CUT_2)/2}[cp]")
            parts.append("[cr][cc][cp]concat=n=3:v=0:a=1,apad=whole_dur=7,atrim=0:7,asetpts=PTS-STARTPTS[a3]")
    parts += ["anullsrc=r=48000:cl=stereo,atrim=duration=3[tail]", "[a0][a1][a2][a3][tail]concat=n=5:v=0:a=1,volume=0.8[native]", "[5:a]volume=0.6[bed]", "[native][bed]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=9[mix]"]
    audio_cmd += ["-filter_complex",";".join(parts),"-map","0:v:0","-map","[mix]","-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000","-t","25","-movflags","+faststart",str(ROOT/"food-felonies-25s-seedance-v5.mp4")]
    subprocess.run(audio_cmd,check=True)
    probe=subprocess.check_output([shutil.which("ffprobe"),"-v","error","-show_entries","format=duration,size:stream=codec_name,codec_type,width,height,avg_frame_rate,nb_frames,duration","-of","json",str(ROOT/"food-felonies-25s-seedance-v5.mp4")],text=True)
    (ROOT/"verification.json").write_text(probe,encoding="utf-8")
    print(probe,flush=True)


if __name__=="__main__":
    render()
