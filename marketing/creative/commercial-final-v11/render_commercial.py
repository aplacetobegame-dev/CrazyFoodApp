"""Discover a shared post, then FOUR separate full-frame cooking shots."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import math
import json
import shutil
import subprocess
import sys
import cv2
from PIL import Image,ImageDraw,ImageFilter,ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v8',ROOT.parent/'commercial-final-v8/render_commercial.py')
v8=importlib.util.module_from_spec(spec);spec.loader.exec_module(v8)
v7,v5=v8.v7,v8.v5
W,H,FPS=v8.W,v8.H,v8.FPS
sc,box,rr,text=v8.sc,v8.box,v8.rr,v8.text
PAPER,INK,RED,GREEN,MUTED=v8.PAPER,v8.INK,v8.RED,v8.GREEN,v8.MUTED
RES=Image.Resampling.LANCZOS
MASTER=ROOT.parent/'commercial-final-v10/food-felonies-mask-ending-25s-v10.mp4'
FINAL=ROOT/'food-felonies-discover-then-cook-25s-v11.mp4'
STARTS=[16.4,17.6,18.8,20.0]
SOURCE_STARTS=[.55,.75,.55,1.35]
SPEEDS=[1,1,1,1.5]


def readers(cooking=True):
    data={'master':v5.Reader(MASTER),
          'recipients':[v5.Reader(ROOT.parent/f'commercial-final-v8/raw/reaction-{i}.mp4') for i in range(4)]}
    if cooking:data['cooking']=[v5.Reader(ROOT/f'raw/cooking-{i}.mp4') for i in range(4)]
    return data


def close(data):
    for value in data.values():
        if isinstance(value,list):
            for r in value:r.cap.release()
        else:value.cap.release()


@lru_cache(maxsize=8)
def avatar(index=-1):
    if index<0:
        im=Image.open(ROOT.parent/'commercial-final-v7/qa/encoded-04.40.jpg').convert('RGB').crop((140,430,980,1270))
    else:
        im=Image.open(ROOT/f'references/recipient-{index}.png').convert('RGB').crop((70,30,740,700))
    im=ImageOps.fit(im,(sc(38),sc(38)),RES)
    mask=Image.new('L',im.size);ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255)
    im=im.convert('RGBA');im.putalpha(mask)
    return im


@lru_cache(maxsize=1)
def shared_post():
    # All four get the SAME main-character post: same face, archive result and case.
    im=Image.new('RGBA',(sc(330),sc(148)))
    d=ImageDraw.Draw(im)
    rr(d,(1,1,329,147),PAPER,15,outline='#D8D1C8',width=1)
    im.alpha_composite(avatar(),(sc(13),sc(13)))
    text(d,(61,13),'New post',17,role='display')
    text(d,(61,38),'From the cook',12,MUTED)
    text(d,(15,72),'Vegetable',20,role='display')
    text(d,(15,96),'gelatin',20,role='display')
    text(d,(15,128),'CRIME 92/100',11,RED,'mono')
    v7.paste(im,v5.ORIGINAL,(194,12,123,124),.5,9)
    return im


def discovery_grid(t,data,cards=True):
    out=Image.new('RGBA',(W,H),PAPER)
    for i,start in enumerate(v8.ENTRIES):
        age=t-start
        if age<0:continue
        source_time=min(1.55,.04+age*.65)
        frame=Image.fromarray(data['recipients'][i].get(source_time))
        # Reframe only the phone-reading opening; remove every finished dish.
        frame=frame.crop((135,0,945,1440)).resize((540,960),RES).convert('RGBA')
        frame=v8.heart_iris(frame,age)
        out.alpha_composite(frame,((i%2)*540,(i//2)*960))
        card_age=t-(14.46+i*.065)
        if cards and card_age>=0:
            card=shared_post().copy()
            u=v8.ease(card_age/.20)
            if u<1:card.putalpha(card.getchannel('A').point(lambda a:round(a*u)))
            out.alpha_composite(card,(sc((i%2)*360+15),sc((i//2)*640+476+20*(1-u))))
    d=ImageDraw.Draw(out)
    d.line((540,0,540,H),fill=PAPER,width=5)
    d.line((0,960,W,960),fill=PAPER,width=5)
    return out


def cooking_frame(i,age,data):
    source_time=SOURCE_STARTS[i]+max(0,age)*SPEEDS[i]
    return Image.fromarray(data['cooking'][i].get(source_time)).convert('RGBA')


def cooking_transition(t,data):
    i=min(3,int((t-16.4+1e-6)/1.2))
    age=t-STARTS[i]
    incoming=cooking_frame(i,age,data)
    if i==0 and age<.16:
        background=discovery_grid(16.39,data)
        p=v8.ease(age/.16)
        width=round(540+540*p);height=round(960+960*p)
        tile=incoming.resize((width,height),RES)
        background.alpha_composite(tile,(0,0))
        return background
    if i>0 and age<.12:
        p=v8.ease(age/.12)
        outgoing=cooking_frame(i-1,1.2,data)
        canvas=Image.new('RGBA',(W,H),PAPER)
        delta=round(W*p)
        if i%2:
            canvas.alpha_composite(outgoing,(-delta,0));canvas.alpha_composite(incoming,(W-delta,0))
        else:
            canvas.alpha_composite(outgoing,(delta,0));canvas.alpha_composite(incoming,(-W+delta,0))
        return canvas.filter(ImageFilter.GaussianBlur(1.2*math.sin(math.pi*p)))
    return incoming


@lru_cache(maxsize=4)
def result_photo(i):
    # These staged result stills are shown AFTER the same people cook.
    cap=cv2.VideoCapture(str(ROOT.parent/f'commercial-final-v8/raw/reaction-{i}.mp4'))
    cap.set(cv2.CAP_PROP_POS_MSEC,3500);ok,bgr=cap.read();cap.release();assert ok
    im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).crop((55,1400,1025,1900))
    im.save(ROOT/f'references/result-{i}.jpg',quality=95)
    return im


def four_uploads(t):
    im=Image.new('RGBA',(W,H),PAPER)
    d=ImageDraw.Draw(im)
    text(d,(360,93),'Cooked Results',48,role='display',anchor='mm')
    text(d,(360,151),'Same recipe. Four versions.',24,MUTED,anchor='mm')
    for i in range(4):
        age=t-21.2-i*.04
        if age<0:continue
        u=v8.ease(age/.17)
        x=36+(i%2)*344;y=235+(i//2)*416+round(65*(1-u))
        rr(d,(x,y,x+304,y+364),'white',20,outline='#DDD6CC',width=1)
        v7.paste(im,result_photo(i),(x+10,y+10,284,263),.6,14)
        im.alpha_composite(avatar(i),(sc(x+15),sc(y+292)))
        text(d,(x+66,y+300),'Photo added',22,GREEN,bold=True)
    text(d,(360,1167),'Commercial dramatization',15,MUTED,anchor='mm')
    return im


def visual_frame(t,data):
    if t<14 or t>=22:
        return Image.fromarray(data['master'].get(t))
    if t<16.4:
        im=discovery_grid(t,data)
        layer=v5.new_layer();v8.hearts(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<21.2:
        return cooking_transition(t,data).convert('RGB')
    return four_uploads(t).convert('RGB')


def preview(discovery=False):
    times=[14.2,14.6,15.0,15.5,16.2] if discovery else [13.7,14.2,14.7,15.6,16.3,16.7,17.9,19.2,20.5,21.6,23.5]
    board=Image.new('RGB',(1350,math.ceil(len(times)/5)*520),PAPER);d=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        data=readers(not discovery)
        im=visual_frame(t,data);close(data)
        im.save(ROOT/f'qa/frame-{t:05.2f}.jpg',quality=95)
        board.paste(im.resize((270,480),RES),((i%5)*270,(i//5)*520))
        d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',fill=INK,font=v5.brand.font(20))
    board.save(ROOT/('qa/discovery-review.jpg' if discovery else 'qa/contact-sheet.jpg'),quality=95)
    print('Preview ready.',flush=True)


def render():
    data=readers()
    cmd=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','16',
         '-pix_fmt','yuv420p','-t','25',str(ROOT/'picture.mp4')]
    with (ROOT/'render.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(750):
                proc.stdin.write(visual_frame(i/30,data).tobytes())
                if i%90==0:print(f'Rendered {i//30}/25 seconds',flush=True)
        finally:proc.stdin.close();close(data)
        if proc.wait():raise RuntimeError((ROOT/'render.log').read_text())
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(ROOT/'picture.mp4'),'-i',str(MASTER),
                    '-map','0:v:0','-map','1:a:0','-c','copy','-t','25','-movflags','+faststart',str(FINAL)],check=True)
    print('Final export ready:',FINAL,flush=True)


if __name__=='__main__':
    (ROOT/'qa').mkdir(exist_ok=True)
    if '--discovery' in sys.argv:preview(True)
    elif '--preview' in sys.argv:preview()
    else:render()
