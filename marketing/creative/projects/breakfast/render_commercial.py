"""Breakfast: Final Boss — approved25s story, fresh actor/food and game effects."""
from pathlib import Path
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('breakfast_ui',ROOT/'breakfast_ui.py')
ui=importlib.util.module_from_spec(spec);spec.loader.exec_module(ui)
v7,v5=ui.v7,ui.v5
SHARED=ROOT.parents[1]/'shared'
sys.path.insert(0,str(SHARED))
import hearts as v8
BUILD=ROOT/'build'
W,H,FPS=v5.W,v5.H,v5.FPS
PAPER,INK=v5.PAPER,v5.INK
RES=Image.Resampling.LANCZOS
FINAL=BUILD/'food-felonies-breakfast-final-boss-25s.mp4'
GLOBAL_INTRO=[0,2,3.2,4.7,6]
COOK_STARTS=[16.4,17.6,18.8,20]
DEFAULT_TIMING={'intro':[0,2,3.2,4.7,6],'community':[0,1.25,2.5,3.75,5],
                'inventory_layout':None}


def timing():
    path=ROOT/'timing.json'
    return json.loads(path.read_text()) if path.exists() else DEFAULT_TIMING


def remap(t,src,dest):
    i=min(len(src)-2,max(0,int(np.searchsorted(src,t,side='right')-1)))
    return dest[i]+(t-src[i])/(src[i+1]-src[i])*(dest[i+1]-dest[i])


def tracks():
    path=ROOT/'tracking.json'
    if path.exists():
        data=json.loads(path.read_text())
        if not data.get('share_track_method'):
            subprocess.run([sys.executable,str(ROOT/'repair_share_track.py')],check=True)
            data=json.loads(path.read_text())
        for key in ['intro','share']:
            data[key]['quads']={int(i):np.array(q,dtype=np.float32) for i,q in data[key]['quads'].items()}
        return data
    cuts=timing()['intro']
    cap=cv2.VideoCapture(str(ROOT/'raw/scene-0.mp4'));fps=cap.get(cv2.CAP_PROP_FPS);cap.release()
    segments=[(0,round(cuts[1]*fps),cuts[1]*.8),
              (round(cuts[1]*fps),round(cuts[2]*fps),(cuts[1]+cuts[2])/2)]
    data={'intro':v7.previous.rigid_track(ROOT/'raw/scene-0.mp4',cuts[2],segments),
          'share':v7.previous.rigid_track(ROOT/'raw/scene-2.mp4',4,[(0,96,.4)])}
    serial={k:{'fps':v['fps'],'quads':{str(i):q.tolist() for i,q in v['quads'].items()}} for k,v in data.items()}
    path.write_text(json.dumps(serial,separators=(',',':')))
    subprocess.run([sys.executable,str(ROOT/'repair_share_track.py')],check=True)
    return tracks()


def readers():
    return {'intro':v5.Reader(ROOT/'raw/scene-0.mp4'),
            'cooking':v5.Reader(ROOT/'raw/scene-1.mp4'),
            'share':v5.Reader(ROOT/'raw/scene-2.mp4'),
            'community':[v5.Reader(ROOT/'raw/scene-3.mp4') for _ in range(4)],
            'recipients':[v5.Reader(SHARED/f'recipients/raw/reaction-{i}.mp4') for i in range(4)]}


def close(data):
    for value in data.values():
        if isinstance(value,list):
            for r in value:r.cap.release()
        else:value.cap.release()


def punch(im,t):
    for at in [3.2,6,6.868,7.528,8.222,9.611,16.4,17.6,18.8,20]:
        age=t-at
        if 0<=age<.22:
            z=1+.022*math.exp(-age*15)
            big=im.resize((round(W*z),round(H*z)),RES)
            return big.crop(((big.width-W)//2,(big.height-H)//2,(big.width+W)//2,(big.height+H)//2))
    return im


def discovery(t,data):
    out=Image.new('RGBA',(W,H),PAPER)
    for i,start in enumerate(v8.ENTRIES):
        age=t-start
        if age<0:continue
        frame=Image.fromarray(data['recipients'][i].get(min(1.55,.04+age*.65)))
        # Only phone-reading crops are reused. Physical gelatin is outside this crop.
        tile=frame.crop((135,0,945,1440)).resize((540,960),RES).convert('RGBA')
        tile=v8.heart_iris(tile,age)
        out.alpha_composite(tile,((i%2)*540,(i//2)*960))
        card_age=t-(14.46+i*.065)
        if card_age>=0:
            card=ui.post_card().copy();p=v8.ease(card_age/.2)
            if p<1:card.putalpha(card.getchannel('A').point(lambda a:round(a*p)))
            out.alpha_composite(card,(v5.sc((i%2)*360+15),v5.sc((i//2)*640+476+20*(1-p))))
    d=ImageDraw.Draw(out)
    d.line((540,0,540,H),fill=PAPER,width=5);d.line((0,960,W,960),fill=PAPER,width=5)
    return out


def community_frame(i,age,data):
    cuts=timing()['community'];fps=data['community'][i].fps
    end=cuts[i+1]-1/fps
    source=min(end,cuts[i]+max(0,age)/1.2*(cuts[i+1]-cuts[i]))
    return Image.fromarray(data['community'][i].get(source)).convert('RGBA')


def community(t,data):
    i=min(3,max(0,int((t-16.4+1e-6)/1.2)));age=t-COOK_STARTS[i]
    incoming=community_frame(i,age,data)
    if i==0 and age<.16:
        out=discovery(16.39,data);p=v8.ease(age/.16)
        out.alpha_composite(incoming.resize((round(540+540*p),round(960+960*p)),RES),(0,0))
        return out
    if i>0 and age<.10:
        p=v8.ease(age/.10);delta=round(W*p)
        outgoing=community_frame(i-1,1.2,data)
        out=Image.new('RGBA',(W,H),PAPER)
        sign=1 if i%2 else -1
        out.alpha_composite(outgoing,(-sign*delta,0))
        out.alpha_composite(incoming,(sign*(W-delta),0))
        return out.filter(ImageFilter.GaussianBlur(1.2*math.sin(math.pi*p)))
    return incoming


def visual_frame(t,data,tracking):
    if t>=22:return ui.end_card(t-22).convert('RGB')
    layer=v5.new_layer()
    if t<6:
        source=remap(t,GLOBAL_INTRO,timing()['intro'])
        frame=data['intro'].get(source)
        if t<3.2:
            tr=tracking['intro'];quad=tr['quads'].get(round(source*tr['fps']))
            frame=v5.composite_phone(frame,ui.phone_ui('meter' if t<2 else 'concept',t),quad)
        im=Image.fromarray(frame)
        if 3.2<=t<4.7:im=punch(im,t)
        im=im.convert('RGBA')
        if t<2:ui.opening(layer,t)
        elif t<3.2:ui.dish_reveal(layer,t)
        elif t<4.7:ui.grin(layer,t)
        else:ui.inventory(layer,t,timing().get('inventory_layout'))
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<11:
        im=Image.fromarray(data['cooking'].get((t-6)*6/5))
        im=punch(im,t).convert('RGBA');ui.cooking(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<14:
        source=(t-11)*1.9/2.35;tr=tracking['share'];quad=tr['quads'].get(round(source*tr['fps'])) if source>=.65 else None
        frame=v5.composite_phone(data['share'].get(source),ui.phone_ui('share',source),quad)
        im=Image.fromarray(frame).convert('RGBA');ui.comparison(layer,t)
        im=Image.alpha_composite(im,layer)
        if t>=13.86:
            wash=Image.new('RGBA',(W,H),PAPER);wash.putalpha(round(235*min(1,(t-13.86)/.14)))
            im=Image.alpha_composite(im,wash)
        layer=v5.new_layer();v8.hearts(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<16.4:
        im=discovery(t,data);v8.hearts(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<21.2:return community(t,data).convert('RGB')
    return ui.uploads(t).convert('RGB')


def preview(tracking):
    times=[.4,1.75,2.6,3.9,5.5,6.4,7.1,7.8,8.7,10.4,12.8,13.7,14.7,15.7,16.8,18,19.2,20.5,21.6,23.5]
    board=Image.new('RGB',(1350,2080),PAPER);d=ImageDraw.Draw(board)
    for i,t in enumerate(times):
        data=readers();im=visual_frame(t,data,tracking);close(data)
        im.save(BUILD/f'qa/frame-{t:05.2f}.jpg',quality=96)
        board.paste(im.resize((270,480),RES),((i%5)*270,(i//5)*520))
        d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',fill=INK,font=v5.brand.font(20))
    board.save(BUILD/'qa/contact-sheet.jpg',quality=95)
    print('Preview frames ready.',flush=True)


def mix_audio():
    foley=BUILD/'audio/breakfast-foley.wav'
    if not foley.exists():
        subprocess.run([sys.executable,str(ROOT/'make_foley.py'),'--output',str(foley)],check=True)
    filters=('[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:25,asetpts=PTS-STARTPTS,'
             'afade=t=in:st=0:d=0.012,afade=t=out:st=24.55:d=0.45,volume=0.85[music];'
             '[2:a]volume=1.25[fx];[music][fx]amix=inputs=2:duration=longest:normalize=0,'
             'loudnorm=I=-15.5:TP=-2:LRA=8[a]')
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(BUILD/'picture.mp4'),
                    '-i',str(SHARED/'audio/guitar-drums-original.mp3'),
                    '-i',str(BUILD/'audio/breakfast-foley.wav'),'-filter_complex',filters,'-map','0:v:0','-map','[a]',
                    '-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','25','-movflags','+faststart',str(FINAL)],check=True)


def render(tracking):
    BUILD.mkdir(parents=True,exist_ok=True)
    data=readers()
    cmd=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','17',
         '-pix_fmt','yuv420p','-t','25',str(BUILD/'picture.mp4')]
    with (BUILD/'render.log').open('w') as log:
        proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(750):
                proc.stdin.write(visual_frame(i/30,data,tracking).tobytes())
                if i%90==0:print(f'Rendered {i//30}/25 seconds',flush=True)
        finally:proc.stdin.close();close(data)
        if proc.wait():raise RuntimeError((BUILD/'render.log').read_text())
    mix_audio();print('Breakfast commercial exported:',FINAL,flush=True)


if __name__=='__main__':
    (BUILD/'qa').mkdir(parents=True,exist_ok=True)
    tracking=tracks()
    if '--preview' in sys.argv:preview(tracking)
    else:render(tracking)
