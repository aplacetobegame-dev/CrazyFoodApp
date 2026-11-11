"""V8: matched comparison cards, Share hearts, four phone-to-dish reactions."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import wave
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v7',ROOT.parent/'commercial-final-v7/render_commercial.py')
v7=importlib.util.module_from_spec(spec);spec.loader.exec_module(v7)
v5=v7.v5
W,H,FPS,S=v7.W,v7.H,v7.FPS,v7.S
sc,box,rr,text=v7.sc,v7.box,v7.rr,v7.text
PAPER,INK,RED,GREEN,MUTED=v7.PAPER,v7.INK,v7.RED,v7.GREEN,v7.MUTED
RES=Image.Resampling.LANCZOS
FINAL=ROOT/'food-felonies-hearts-four-reactions-25s-v8.mp4'
ENTRIES=[14.0,14.14,14.28,14.42]


def ease(p):return v7.ease(p)


@lru_cache(maxsize=1)
def tracking():return v7.state()


def readers(reactions=True):
    data={'master':v5.Reader(v7.FINAL),
          'share':v5.Reader(v7.SOURCE/'raw/scene-2.mp4'),
          'community':v5.Reader(v7.SOURCE/'raw/scene-3.mp4')}
    if reactions:
        data['reactions']=[v5.Reader(ROOT/f'raw/reaction-{i}.mp4') for i in range(4)]
    return data


def close(data):
    for key,value in data.items():
        if key=='reactions':
            for r in value:r.cap.release()
        else:value.cap.release()


@lru_cache(maxsize=2)
def photo_card(which):
    # Explicit framing gives both molds comparable scale despite different source ratios.
    source=v5.CONCEPT if which==0 else v5.ORIGINAL
    photo=ImageOps.fit(source,(sc(304),sc(234)),RES,centering=(.5,.59 if which==0 else .50))
    card=Image.new('RGBA',(sc(320),sc(250)),PAPER)
    card.alpha_composite(photo.convert('RGBA'),(sc(8),sc(8)))
    card=card.rotate(1.3 if which==0 else -1.3,Image.Resampling.BICUBIC,expand=True)
    shadow=Image.new('RGBA',card.size)
    shadow.putalpha(card.getchannel('A').point(lambda a:round(a*.18)))
    shadow=shadow.filter(ImageFilter.GaussianBlur(sc(4)))
    out=Image.new('RGBA',(card.width+sc(18),card.height+sc(20)))
    out.alpha_composite(shadow,(sc(10),sc(12)))
    out.alpha_composite(card,(sc(7),sc(5)))
    return out


def share_panel(t):
    layer=v5.new_layer()
    age=t-11.2
    if age<0:return layer
    top=590+round(55*(1-ease(age/.28)))
    shadow=v5.new_layer();sd=ImageDraw.Draw(shadow)
    rr(sd,(29,top+7,697,1193),(25,20,15,36),27)
    shadow=shadow.filter(ImageFilter.GaussianBlur(sc(9)))
    layer.alpha_composite(shadow)
    d=ImageDraw.Draw(layer)
    rr(d,(27,top,693,1185),PAPER,27)
    text(d,(51,top+26),'My food felony',31,role='display')
    text(d,(668,top+36),'#AC-041',17,RED,'mono',anchor='ra')
    text(d,(199,top+97),'The idea',29,role='display',anchor='mm')
    text(d,(521,top+97),'The result',29,role='display',anchor='mm')
    for i,x in enumerate([199,521]):
        card=photo_card(i)
        layer.alpha_composite(card,(round(sc(x)-card.width/2),sc(top+126)))
    text(d,(360,top+405),'CRIME LEVEL  92 / 100',18,RED,'mono',anchor='mm')
    tap=t-13.35
    press=math.sin(max(0,min(1,tap/.16))*math.pi)*3 if 0<tap<.16 else 0
    shared=t>=13.48
    button_y=top+447+press
    rr(d,(51,button_y,669,button_y+83),GREEN if shared else RED,40)
    if shared:
        d.line([tuple(map(sc,p)) for p in [(263,button_y+40),(273,button_y+50),(290,button_y+31)]],fill='white',width=sc(3),joint='curve')
        text(d,(382,button_y+41),'Shared!',31,'white',bold=True,anchor='mm')
    else:
        d.line([tuple(map(sc,p)) for p in [(231,button_y+51),(231,button_y+31),(223,button_y+39),(231,button_y+31),(239,button_y+39)]],fill='white',width=sc(2),joint='curve')
        text(d,(387,button_y+41),'Share my result',30,'white',bold=True,anchor='mm')
    text(d,(360,top+562),'Commercial dramatization',14,MUTED,anchor='mm')
    if t>=13.86:
        fade=max(0,1-(t-13.86)/.20)
        layer.putalpha(layer.getchannel('A').point(lambda a:round(a*fade)))
    return layer


@lru_cache(maxsize=1)
def heart_points():
    # Smooth mathematical heart, normalized so its optical center sits at origin.
    a=np.linspace(0,math.tau,120)
    x=16*np.sin(a)**3
    y=-(13*np.cos(a)-5*np.cos(2*a)-2*np.cos(3*a)-np.cos(4*a))
    return np.c_[x/32,(y-2)/32]


@lru_cache(maxsize=100)
def heart_art(size,color):
    n=max(12,sc(size));pad=sc(4)
    im=Image.new('RGBA',(n+2*pad,n+2*pad))
    d=ImageDraw.Draw(im)
    points=heart_points()*n+np.array([n/2+pad,n/2+pad])
    d.polygon([tuple(p) for p in points],fill=color)
    return im


def draw_heart(layer,center,size,angle=0,alpha=1,color=RED):
    art=heart_art(round(size),color)
    if angle:art=art.rotate(angle,Image.Resampling.BICUBIC,expand=True)
    if alpha<1:
        art=art.copy();art.putalpha(art.getchannel('A').point(lambda a:round(a*alpha)))
    layer.alpha_composite(art,(round(sc(center[0])-art.width/2),round(sc(center[1])-art.height/2)))


def hearts(layer,t):
    # Four leading hearts carry the Share action into the four recipients.
    for i,end in enumerate(ENTRIES):
        start=13.43+i*.045
        finish=end+.06
        if not start<=t<=finish+.08:continue
        p=min(1,(t-start)/(finish-start));u=1-p
        target=np.array([180+(i%2)*360,320+(i//2)*640])
        origin=np.array([344+(i-1.5)*12,1078])
        c1=origin+np.array([(-1 if i%2==0 else 1)*85,-260])
        c2=target+np.array([(-1 if i%2==0 else 1)*25,-155])
        xy=u**3*origin+3*u*u*p*c1+3*u*p*p*c2+p**3*target
        alpha=max(0,1-(t-finish)/.08) if t>finish else 1
        draw_heart(layer,xy,23+11*math.sin(math.pi*p),(-12 if i%2==0 else 12)*math.sin(math.pi*p),alpha)
    # A few smaller companion hearts float upwards, with gentle drag and stagger.
    for i in range(5):
        age=t-(13.46+i*.055)
        if not 0<age<.78:continue
        p=age/.78
        xy=(356+(i-2)*24*p+7*math.sin(p*4+i),1070-260*ease(p))
        draw_heart(layer,xy,11+(i%2)*4,10*math.sin(p*3+i),min(1,age/.06)*(1-p)**.6,'#DA6457')


def heart_iris(tile,age):
    if age>=.52:return tile
    if age<=0:return Image.new('RGBA',tile.size)
    mask=Image.new('L',tile.size)
    p=ease(age/.52)
    # Expanding heart grows past the panel bounds; the full rectangle settles cleanly.
    diameter=35+3100*p
    points=heart_points()*diameter+np.array([tile.width/2,tile.height/2])
    ImageDraw.Draw(mask).polygon([tuple(x) for x in points],fill=255)
    tile=tile.copy();tile.putalpha(mask)
    return tile


def reaction_grid(t,data):
    background=Image.new('RGBA',(W,H),PAPER)
    for i,start in enumerate(ENTRIES):
        age=t-start
        if age<0:continue
        local=min(3.94,max(0,age*4/(18-start)))
        frame=Image.fromarray(data['reactions'][i].get(local)).convert('RGBA')
        tile=frame.resize((540,960),RES)
        # Gentle camera settle within each panel, maintaining uniform geometry.
        z=1+.035*(1-ease(age/.45))
        if z>1:
            tile=tile.resize((round(540*z),round(960*z)),RES)
            tile=tile.crop(((tile.width-540)//2,(tile.height-960)//2,(tile.width+540)//2,(tile.height+960)//2))
        tile=heart_iris(tile,age)
        background.alpha_composite(tile,((i%2)*540,(i//2)*960))
    d=ImageDraw.Draw(background)
    d.line((540,0,540,H),fill=PAPER,width=5)
    d.line((0,960,W,960),fill=PAPER,width=5)
    return background


def visual_frame(t,data,pp):
    if t<11:
        return Image.fromarray(data['master'].get(t))
    if t>=22:
        return Image.fromarray(data['master'].get(t))
    layer=v5.new_layer()
    if t<14:
        local=t-11
        track=tracking()['share']
        frame=data['share'].get(local)
        quad=track['quads'].get(round(local*track['fps']))
        frame=v5.composite_phone(frame,v7.phone_ui('concept',local),quad)
        im=Image.fromarray(frame).convert('RGBA')
        layer.alpha_composite(share_panel(t))
        v7.floating(layer,'SHOW THE EVIDENCE.',(360,180),43,t-11.2,PAPER,-4,life=2.8)
        im=Image.alpha_composite(im,layer)
        if t>=13.86:
            wash=Image.new('RGBA',(W,H),PAPER)
            wash.putalpha(round(235*min(1,(t-13.86)/.14)))
            im=Image.alpha_composite(im,wash)
        layer=v5.new_layer();hearts(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<18:
        im=reaction_grid(t,data)
        hearts(layer,t)
        # Verdicts arrive after the phone-to-dish performance has played.
        if t>=17.15:
            v7.stamp(layer,'GUILTY',(120,500),t-17.15,RED,-8)
        if t>=17.37:
            v7.stamp(layer,'ACQUITTED',(602,1145),t-17.37,GREEN,7)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<20:
        source_time=v5.COMMUNITY_CUT_1+(t-18)*(v5.COMMUNITY_CUT_2-v5.COMMUNITY_CUT_1)/2
        im=Image.fromarray(data['community'].get(source_time)).convert('RGBA')
        v7.floating(layer,'SAME RECIPE.',(360,122),53,t-18,PAPER,-3,life=2)
        v7.floating(layer,'THEIR CHAOS.',(360,1132),58,t-18.14,RED,3,life=1.86)
    else:
        source_time=v5.COMMUNITY_CUT_2+(t-20)*(7-v5.COMMUNITY_CUT_2)/2
        im=Image.fromarray(data['community'].get(source_time)).convert('RGBA')
        v5.uploads(layer,t-20,pp)
        v7.floating(layer,'PROOF UPLOADED!',(360,185),45,t-20.85,PAPER,-4,life=1.15)
    return Image.alpha_composite(im,layer).convert('RGB')


def preview(comparison_only=False):
    times=[11.5,12.3,13.1,13.47,13.7,13.9] if comparison_only else [11.5,12.3,13.1,13.47,13.7,13.9,14.15,14.5,15.0,15.7,16.4,17.3,18.5,20.9,23.5]
    rows=math.ceil(len(times)/5)
    board=Image.new('RGB',(1350,rows*520),PAPER);d=ImageDraw.Draw(board)
    pp=v7.photos()
    for i,t in enumerate(times):
        data=readers(not comparison_only)
        frame=visual_frame(t,data,pp)
        frame.save(ROOT/f'qa/frame-{t:05.2f}.jpg',quality=95)
        board.paste(frame.resize((270,480),RES),((i%5)*270,(i//5)*520))
        d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',fill=INK,font=v5.brand.font(20))
        close(data)
    board.save(ROOT/('qa/comparison-review.jpg' if comparison_only else 'qa/contact-sheet.jpg'),quality=95)
    print('Preview frames ready.',flush=True)


def make_foley():
    with wave.open(str(ROOT.parent/'commercial-final-v6/audio/clean-foley.wav'),'rb') as f:
        sr=f.getframerate();old=np.frombuffer(f.readframes(f.getnframes()),'<i2').reshape(-1,2).astype(np.float64)/32768
    rng=np.random.default_rng(81126)
    for at,gain in [(13.43,.07),(14.0,.035),(14.14,.035),(14.28,.035),(14.42,.035)]:
        duration=.14;n=round(sr*duration);tt=np.arange(n)/sr
        sound=np.convolve(rng.standard_normal(n),np.ones(21)/21,mode='same')*np.sin(np.pi*tt/duration)**2*gain
        a=round(at*sr);old[a:a+n]+=sound[:,None]
    with wave.open(str(ROOT/'share-foley.wav'),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(old,-.98,.98)*32767).astype('<i2').tobytes())


def mix_audio():
    filters=('[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:3.12,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.03,afade=t=out:st=2.9:d=0.22,volume=0.45,adelay=6000|6000,apad=whole_dur=25[kitchen];'
             '[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:25,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.012,afade=t=out:st=24.55:d=0.45,volume=0.90[music];'
             '[3:a]volume=0.65[fx];[music][kitchen][fx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-15.5:TP=-2:LRA=8[a]')
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(ROOT/'picture.mp4'),
        '-i',str(v7.SOURCE/'raw/scene-1.mp4'),'-i',str(ROOT.parent/'commercial-final-v6/audio/guitar-drums-original.mp3'),
        '-i',str(ROOT/'share-foley.wav'),'-filter_complex',filters,'-map','0:v:0','-map','[a]',
        '-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','25','-movflags','+faststart',str(FINAL)],check=True)


def render():
    cmd=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-t','25',str(ROOT/'picture.mp4')]
    data=readers();pp=v7.photos()
    with (ROOT/'render.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(750):
                proc.stdin.write(visual_frame(i/30,data,pp).tobytes())
                if i%90==0:print(f'Rendered {i//30}/25 seconds',flush=True)
        finally:
            proc.stdin.close();close(data)
        if proc.wait():raise RuntimeError((ROOT/'render.log').read_text())
    make_foley();mix_audio()
    print('Final video ready:',FINAL,flush=True)


if __name__=='__main__':
    (ROOT/'qa').mkdir(parents=True,exist_ok=True)
    if '--comparison' in sys.argv:preview(True)
    elif '--preview' in sys.argv:preview()
    else:render()
