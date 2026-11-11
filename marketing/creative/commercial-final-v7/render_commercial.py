"""25s v7: generated toxic chef sprites and anchored kinetic typography.

Recomposites the existing Seedance 2.5 footage; no new model jobs.
"""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent/'commercial-final-v5'
ART = ROOT.parent/'commercial-art-v7'
spec = importlib.util.spec_from_file_location('previous', ROOT.parent/'commercial-final-v6/revise_commercial.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
v5 = previous.v5
W, H, FPS, S = v5.W, v5.H, v5.FPS, v5.S
sc, box, rr, text, paste = v5.sc, v5.box, v5.rr, v5.text, v5.paste
PAPER, INK, RED, PICKLE, MUTED = v5.PAPER, v5.INK, v5.RED, v5.PICKLE, v5.MUTED
GREEN = v5.brand.GREEN
RES = Image.Resampling.LANCZOS
FINAL = ROOT/'food-felonies-toxic-chef-25s-v7.mp4'
SHEET = Image.open(ART/'chef-toxic-progression.png').convert('RGBA')
SPRITES = [SHEET.crop(((i%3)*512, (i//3)*512, (i%3+1)*512, (i//3+1)*512)) for i in range(6)]
INGREDIENTS = {name:Image.open(ART/f'ingredient-{name}.png').convert('RGBA') for name in ['onion','green-pepper','gelatin','celery']}
STAGES = ['CURIOUS','BAD IDEA','SUIT UP','TOXIC','UNSTABLE','FOOD FELONY']


def ease(x):
    return 1-(1-max(0,min(1,x)))**3


def crime(t):
    return round(100*min(max(t/1.55,0),1))


def stage(t):
    return min(5, int(crime(t)//20))


def place_art(layer, art, center, size, angle=0):
    piece = art.resize((sc(size), sc(size)), RES)
    if angle:
        piece = piece.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    layer.alpha_composite(piece, (round(sc(center[0])-piece.width/2), round(sc(center[1])-piece.height/2)))


@lru_cache(maxsize=200)
def type_art(label, size, color=PAPER):
    font = v5.brand.font(sc(size), 'display', True)
    stroke = sc(2.5)
    bb = ImageDraw.Draw(Image.new('RGBA',(1,1))).textbbox((0,0),label,font=font,stroke_width=stroke)
    pad = sc(16)
    im = Image.new('RGBA',(bb[2]-bb[0]+pad*2,bb[3]-bb[1]+pad*2))
    d = ImageDraw.Draw(im)
    xy = (pad-bb[0],pad-bb[1])
    d.text((xy[0]+sc(3),xy[1]+sc(5)),label,font=font,fill=INK,stroke_width=sc(4),stroke_fill=INK)
    d.text(xy,label,font=font,fill=color,stroke_width=stroke,stroke_fill=INK if color==PAPER else PAPER)
    return im


def floating(layer,label,center,size,age,color=PAPER,angle=-5,life=100,drift=1.8):
    if age<0 or age>=life:
        return
    p=min(age/.19,1)
    # Fast controlled overshoot. Once settled, the lettering stays readable.
    z=.76+.24*ease(p)+.10*math.sin(math.pi*p)
    end=max(0,min(1,(life-age)/.10))
    z*=.92+.08*end
    art=type_art(label,size,color)
    art=art.resize((round(art.width*z),round(art.height*z)),RES)
    rotation=angle+(1-p)*8
    art=art.rotate(rotation,Image.Resampling.BICUBIC,expand=True)
    alpha=min(1,age/.06)*end
    if alpha<1:
        art.putalpha(art.getchannel('A').point(lambda x:round(x*alpha)))
    x=center[0]+drift*math.sin(age*2.2)
    y=center[1]+22*(1-ease(p))+drift*math.sin(age*2.8)
    layer.alpha_composite(art,(round(sc(x)-art.width/2),round(sc(y)-art.height/2)))


def rays(layer,center,radius,age,color=RED):
    if not 0<=age<.5:
        return
    p=ease(age/.45)
    d=ImageDraw.Draw(layer)
    for angle in [-160,-130,-45,-15,25,145]:
        a=math.radians(angle)
        r=radius+12*p
        d.line(box((center[0]+r*math.cos(a),center[1]+r*.32*math.sin(a),
                    center[0]+(r+13*(1-p)+5)*math.cos(a),center[1]+(r*.32+11)*math.sin(a))),fill=color,width=sc(3))


def chef(layer,t,center,size):
    idx=stage(t)
    age=t-idx*.31
    kick=.055*math.sin(min(max(age,0)/.18,1)*math.pi) if age<.18 else 0
    tilt=(1.1 if idx>2 else .5)*math.sin(t*6)
    place_art(layer,SPRITES[idx],center,size*(1+kick),tilt)


def phone_ui(kind,t):
    if kind!='meter':
        return v5.phone_ui(kind,t)
    im=Image.new('RGBA',(sc(400),sc(760)),PAPER)
    d=ImageDraw.Draw(im)
    text(d,(22,25),'Food Felonies',27,role='display')
    d.line(box((22,77,378,77)),fill='#DED9CB',width=sc(1))
    text(d,(22,101),'Choose your chaos.',28,role='display')
    text(d,(22,148),'Normal is optional.',17,MUTED)
    chef(im,t,(200,315),265)
    value=crime(t)
    text(d,(22,470),'Crime level',22,bold=True)
    text(d,(378,470),f'{value}/100',22,RED,'mono',anchor='ra')
    rr(d,(25,534,375,544),'#D5D2C7',5)
    xx=25+350*value/100
    if value:
        rr(d,(25,534,xx,544),RED,5)
    d.ellipse(box((xx-12,527,xx+12,551)),fill=RED,outline='white',width=sc(2))
    text(d,(25,576),'Normal',16,MUTED)
    text(d,(375,576),'Food Felony',16,RED,anchor='ra')
    rr(d,(22,635,378,696),RED,29)
    text(d,(200,665),'Generate recipe  >',22,'white',bold=True,anchor='mm')
    text(d,(200,733),STAGES[stage(t)],18,RED,'mono',anchor='mm')
    return np.array(im.convert('RGB'))


@lru_cache(maxsize=1)
def opening_wash():
    a=np.zeros((H,W,4),np.uint8)
    a[:,:,:3]=(250,246,239)
    a[:,:,3]=np.clip((np.arange(H)[:,None]-sc(835))/sc(230),0,1)*245
    return Image.fromarray(a)


def opening(layer,t):
    layer.alpha_composite(opening_wash())
    value=crime(t)
    label='TURN IT UP.' if t<1.55 else 'MAX CRIME!'
    floating(layer,label,(360,125),67 if t<1.55 else 65,t if t<1.55 else t-1.55,
             PAPER if t<1.55 else RED,angle=-4,life=1.55 if t<1.55 else .45)
    chef(layer,t,(177,984),255)
    d=ImageDraw.Draw(layer)
    text(d,(506,917),'CRIME LEVEL',22,INK,'mono',anchor='mm')
    text(d,(507,985),str(value),91,RED,'display',anchor='mm')
    text(d,(507,1050),STAGES[stage(t)],20,RED,'mono',anchor='mm')
    rr(d,(63,1122,657,1134),'#D8D2C6',6)
    xx=63+594*value/100
    if value:
        rr(d,(63,1122,xx,1134),RED,6)
    d.ellipse(box((xx-15,1113,xx+15,1143)),fill=RED,outline=PAPER,width=sc(3))
    text(d,(63,1170),'Normal',21,MUTED)
    text(d,(657,1170),'Food Felony',21,RED,anchor='ra')
    if value==100:
        rays(layer,(360,125),270,t-1.55)


def food_reveal(layer,t):
    age=t-2
    panel=Image.new('RGBA',(sc(560),sc(668)),PAPER)
    paste(panel,v5.CONCEPT,(15,15,530,530),.82,16)
    d=ImageDraw.Draw(panel)
    text(d,(280,583),'THE IDEA',30,INK,'mono',anchor='mm')
    panel=panel.rotate(-3+2*ease(age/.3),Image.Resampling.BICUBIC,expand=True)
    layer.alpha_composite(panel,(round(sc(360)-panel.width/2),round(sc(570)-panel.height/2+sc(45*(1-ease(age/.24))))))
    floating(layer,'VEGETABLE',(350,1020),59,age+.02,RED,-5,life=1.18)
    floating(layer,'GELATIN.',(385,1100),72,age-.06,PAPER,2,life=1.10)


def ingredient_tracks():
    cap=cv2.VideoCapture(str(SOURCE/'raw/scene-0.mp4'))
    fps=cap.get(cv2.CAP_PROP_FPS)
    start,end=round(4.8*fps),round(6*fps)
    cap.set(cv2.CAP_PROP_POS_FRAMES,start)
    gray=[]
    for _ in range(start,end):
        ok,bgr=cap.read()
        if not ok:break
        gray.append(cv2.cvtColor(cv2.resize(bgr,(720,1280)),cv2.COLOR_BGR2GRAY))
    cap.release()
    reference=min(len(gray)-1,round(5.25*fps)-start)
    rois={'onion':(90,315,260,540),'green-pepper':(270,220,460,500),
          'gelatin':(470,425,675,655),'celery':(85,745,620,885)}
    out={}
    for name,(x0,y0,x1,y1) in rois.items():
        mask=np.zeros_like(gray[reference]);mask[y0:y1,x0:x1]=255
        points=cv2.goodFeaturesToTrack(gray[reference],maxCorners=60,qualityLevel=.025,minDistance=7,mask=mask)
        deltas={reference:[0.,0.]}
        if points is not None:
            for direction in [-1,1]:
                old=points.copy();total=np.zeros(2);i=reference
                while 0<=i+direction<len(gray):
                    nxt=i+direction
                    moved,status,_=cv2.calcOpticalFlowPyrLK(gray[i],gray[nxt],old,None,winSize=(25,25),maxLevel=3)
                    good=status[:,0].astype(bool)&(np.linalg.norm(moved[:,0]-old[:,0],axis=1)<25)
                    if good.sum()>3:
                        delta=np.median((moved-old)[good,0],axis=0)
                        total=np.clip(total+delta,-18,18)
                        old=moved[good].reshape(-1,1,2)
                    deltas[nxt]=total.tolist();i=nxt
        out[name]={str(start+i):deltas.get(i,[0.,0.]) for i in range(len(gray))}
    return {'fps':fps,'deltas':out}


def state():
    path=ROOT/'tracking.json'
    if path.exists():
        saved=json.loads(path.read_text())
        for name in ['phone','share']:
            saved[name]['quads']={int(i):np.array(q,dtype=np.float32) for i,q in saved[name]['quads'].items()}
        return saved
    data={'phone':previous.rigid_track(SOURCE/'raw/scene-0.mp4'),
          'share':previous.rigid_track(SOURCE/'raw/scene-2.mp4',4,[(0,96,.3)]),
          'ingredients':ingredient_tracks()}
    serial={k:{'fps':v['fps'],'quads':{str(i):q.tolist() for i,q in v['quads'].items()}} for k,v in data.items() if k!='ingredients'}
    serial['ingredients']=data['ingredients']
    path.write_text(json.dumps(serial,separators=(',',':')))
    return data


def leader(layer,a,b):
    d=ImageDraw.Draw(layer)
    mid=((a[0]+b[0])/2+15,(a[1]+b[1])/2)
    points=[]
    for u in np.linspace(0,1,20):
        points.append((sc((1-u)**2*a[0]+2*u*(1-u)*mid[0]+u*u*b[0]),
                       sc((1-u)**2*a[1]+2*u*(1-u)*mid[1]+u*u*b[1])))
    d.line(points,fill=PAPER,width=sc(5),joint='curve')
    d.line(points,fill=INK,width=sc(1.5),joint='curve')
    d.ellipse(box((b[0]-3,b[1]-3,b[0]+3,b[1]+3)),fill=RED)


def ingredient_labels(layer,t,tracking):
    items=[('onion','ONION',(155,255),(160,400),43,-6,4.85),
           ('green-pepper','GREEN PEPPER',(400,160),(365,335),39,4,4.95),
           ('gelatin','GELATIN',(555,685),(550,530),42,-4,5.05),
           ('celery','CELERY',(225,640),(440,800),46,5,5.15)]
    for name,label,center,target,size,angle,start in items:
        age=t-start
        if age<0:continue
        delta=tracking['deltas'][name].get(str(round(t*tracking['fps'])),[0,0])
        c=(center[0]+delta[0],center[1]+delta[1]);tip=(target[0]+delta[0],target[1]+delta[1])
        side=-1 if tip[1]<c[1] else 1
        if age>.10:
            leader(layer,(c[0],c[1]+side*33),tip)
        icon=INGREDIENTS[name]
        place_art(layer,icon,(c[0]-size*len(label)*.23-26,c[1]-49),65,angle/2)
        floating(layer,label,c,size,age,RED if name in ['gelatin','onion'] else GREEN,angle,life=6-start,drift=.8)


def comparison(layer,t):
    age=t-11.25
    if age<0:return
    floating(layer,'SHOW THE EVIDENCE.',(360,192),43,age,PAPER,-4,life=3.75)
    d=ImageDraw.Draw(layer)
    top=527+round(60*(1-ease(age/.25)))
    rr(d,(28,top,692,1204),PAPER,24)
    text(d,(53,top+28),'CASE FILE #AC-041',17,RED,'mono')
    text(d,(195,top+86),'The idea',27,role='display',anchor='mm')
    text(d,(525,top+86),'The result',27,role='display',anchor='mm')
    paste(layer,v5.CONCEPT,(48,top+119,305,286),.83,18)
    paste(layer,v5.ORIGINAL,(367,top+119,305,286),.5,18,contain=True)
    shared=t>=13.7
    rr(d,(50,top+446,670,top+529),GREEN if shared else RED,39)
    text(d,(360,top+487),'Shared!' if shared else 'Share my result  >',30,'white',bold=True,anchor='mm')
    if 13.3<t<13.7:
        r=15+35*(t-13.3)/.4
        d.ellipse(box((562-r,top+487-r,562+r,top+487+r)),outline=v5.brand.MUSTARD,width=sc(4))
    text(d,(360,top+592),'Commercial dramatization',16,MUTED,anchor='mm')


def reaction_build(frame,age):
    if age>=.62:return frame
    out=Image.new('RGBA',(W,H),PAPER)
    for i in range(9):
        u=ease((age-i*.035)/.20)
        if u<=0:continue
        col,row=i%3,i//3
        tile=frame.crop((col*360,row*640,(col+1)*360,(row+1)*640))
        z=.85+.15*u
        tile=tile.resize((round(360*z),round(640*z)),RES)
        tile.putalpha(round(255*u))
        out.alpha_composite(tile,(col*360+(360-tile.width)//2,row*640+(640-tile.height)//2))
    return out


def stamp(layer,label,center,age,color,angle):
    if age<0:return
    width=195 if label=='ACQUITTED' else 160
    badge=Image.new('RGBA',(sc(width),sc(54)))
    d=ImageDraw.Draw(badge)
    rr(d,(3,3,width-3,51),None,2,outline=color,width=3)
    text(d,(width/2,27),label,23,color,'mono',anchor='mm')
    badge=badge.rotate(angle+8*(1-ease(age/.13)),Image.Resampling.BICUBIC,expand=True)
    z=1+.2*math.exp(-age*20)
    badge=badge.resize((round(badge.width*z),round(badge.height*z)),RES)
    layer.alpha_composite(badge,(round(sc(center[0])-badge.width/2),round(sc(center[1])-badge.height/2)))


def end_card(t):
    card=v5.end_card(t).convert('RGBA')
    d=ImageDraw.Draw(card)
    for x,y,dx in [(34,976,-14),(686,976,14),(30,1036,-16),(690,1036,16)]:
        d.line(box((x,y,x+dx,y-10)),fill=RED,width=sc(4))
    if t<.22:
        background=Image.new('RGBA',(W,H),PAPER)
        background.alpha_composite(previous.pop_layer(card,t,.22))
        return background.convert('RGB')
    return card.convert('RGB')


def visual_frame(t,readers,photos,tracking):
    if t>=22:return end_card(t-22)
    index=0 if t<6 else 1 if t<11 else 2 if t<15 else 3
    local=t-[0,6,11,15][index]
    source_time=local
    if index==3:
        source_time=local*v5.COMMUNITY_CUT_1/2 if local<2 else v5.COMMUNITY_CUT_1+(local-2)*(v5.COMMUNITY_CUT_2-v5.COMMUNITY_CUT_1)/3 if local<5 else v5.COMMUNITY_CUT_2+(local-5)*(7-v5.COMMUNITY_CUT_2)/2
    frame=readers[index].get(source_time)
    if (index==0 and local<3) or index==2:
        track=tracking['phone' if index==0 else 'share']
        q=track['quads'].get(round(local*track['fps']))
        frame=v5.composite_phone(frame,phone_ui('meter' if index==0 and local<2 else 'concept',local),q)
    im=Image.fromarray(frame)
    im=ImageEnhance.Contrast(im).enhance(1.035)
    im=ImageEnhance.Color(im).enhance(1.055)
    # Keep positional labels aligned with the ingredient footage; no zoom there.
    if not 4.8<=t<6:
        im=previous.punch(im,t)
    im=im.convert('RGBA')
    if 15<=t<15.62:
        im=reaction_build(im,t-15)
    layer=v5.new_layer()
    if t<2:opening(layer,t)
    elif t<3.15:food_reveal(layer,t)
    elif t<4.02:
        floating(layer,'BAD IDEA?',(257,1060),47,t-3.24,PAPER,-5,life=.78)
    elif t<4.8:
        floating(layer,'PERFECT.',(390,1070),74,t-4.02,RED,-7,life=.78)
        rays(layer,(390,1070),205,t-4.02,RED)
    elif t<6:ingredient_labels(layer,t,tracking['ingredients'])
    elif t<7.8:
        floating(layer,'CHOP.',(167,1040),72,t-6,PAPER,-7,life=1.8)
    elif t<8.8:
        floating(layer,'MIX.',(550,1020),75,t-7.8,RED,5,life=1)
    elif t<9.4:
        floating(layer,'POUR.',(174,1120),68,t-8.8,PAPER,-6,life=.6)
    elif t<11:
        d=ImageDraw.Draw(layer)
        text(d,(47,97),'AFTER CHILLING',20,PAPER,'mono')
        if t>=10.22:
            floating(layer,'JIGGLE.',(375,1122),72,t-10.22,RED,4,life=.78)
    elif t<15:comparison(layer,t)
    elif t<17:
        floating(layer,'YOUR TURN.',(360,1130),61,t-15.14,PAPER,-4,life=1.86)
        stamp(layer,'GUILTY',(118,397),t-15.43,RED,-10)
        stamp(layer,'ACQUITTED',(593,818),t-15.9,GREEN,8)
    elif t<20:
        floating(layer,'SAME RECIPE.',(360,122),53,t-17,PAPER,-3,life=3)
        floating(layer,'THEIR CHAOS.',(360,1132),58,t-17.18,RED,3,life=2.82)
    else:
        v5.uploads(layer,t-20,photos)
        floating(layer,'PROOF UPLOADED!',(360,185),45,t-20.85,PAPER,-4,life=1.15)
    return Image.alpha_composite(im,layer).convert('RGB')


def readers():
    return [v5.Reader(SOURCE/f'raw/scene-{i}.mp4') for i in range(4)]


def photos():
    return [Image.open(SOURCE/f'references/community-result-{i}.jpg').convert('RGB') for i in range(1,4)]


def preview(tracking):
    times=[0,.35,.68,1.0,1.35,1.75,2.55,3.65,4.4,5.6,6.6,8.25,9.12,10.65,12.7,15.8,16.45,18.6,21.4,23.4]
    board=Image.new('RGB',(1350,4*520),PAPER)
    d=ImageDraw.Draw(board)
    pp=photos()
    for i,t in enumerate(times):
        rrds=readers()
        frame=visual_frame(t,rrds,pp,tracking)
        frame.save(ROOT/f'qa/frame-{t:05.2f}.jpg',quality=95)
        board.paste(frame.resize((270,480),RES),((i%5)*270,(i//5)*520))
        d.text(((i%5)*270+9,(i//5)*520+486),f'{t:05.2f}s',font=v5.brand.font(20),fill=INK)
        for r in rrds:r.cap.release()
    board.save(ROOT/'qa/contact-sheet.jpg',quality=95)
    print('Review frames ready.',flush=True)


def mix_audio():
    filters=('[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:3.12,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.03,afade=t=out:st=2.9:d=0.22,volume=0.45,adelay=6000|6000,apad=whole_dur=25[kitchen];'
             '[2:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:25,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.012,afade=t=out:st=24.55:d=0.45,volume=0.90[music];'
             '[3:a]volume=0.65[fx];[music][kitchen][fx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-15.5:TP=-2:LRA=8[a]')
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y',
        '-i',str(ROOT/'picture.mp4'),'-i',str(SOURCE/'raw/scene-1.mp4'),
        '-i',str(ROOT.parent/'commercial-final-v6/audio/guitar-drums-original.mp3'),
        '-i',str(ROOT.parent/'commercial-final-v6/audio/clean-foley.wav'),
        '-filter_complex',filters,'-map','0:v:0','-map','[a]','-c:v','copy',
        '-c:a','aac','-b:a','192k','-ar','48000','-t','25','-movflags','+faststart',str(FINAL)],check=True)


def render(tracking):
    cmd=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18',
         '-pix_fmt','yuv420p','-t','25',str(ROOT/'picture.mp4')]
    rrds,pp=readers(),photos()
    with (ROOT/'render.log').open('w') as log:
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(750):
                process.stdin.write(visual_frame(i/30,rrds,pp,tracking).tobytes())
                if i%90==0:print(f'Rendered {i//30}/25 seconds',flush=True)
        finally:
            process.stdin.close()
            for r in rrds:r.cap.release()
        if process.wait():raise RuntimeError((ROOT/'render.log').read_text())
    mix_audio()
    print('Final export ready:',FINAL,flush=True)


def repair_ingredient_segment(tracking):
    """Replace only the ingredient shot after the precise leader placement check."""
    segment=ROOT/'qa/ingredients-fixed.mp4'
    cmd=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','16',
         '-pix_fmt','yuv420p',str(segment)]
    rrds,pp=readers(),photos()
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for i in range(144,180):
        process.stdin.write(visual_frame(i/30,rrds,pp,tracking).tobytes())
    process.stdin.close()
    for r in rrds:r.cap.release()
    if process.wait():raise RuntimeError('Ingredient replacement render failed')
    corrected=ROOT/'picture-corrected.mp4'
    filters='[0:v]trim=end_frame=144,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=180:end_frame=750,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0,fps=30[v]'
    subprocess.run([shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-i',str(ROOT/'picture.mp4'),'-i',str(segment),
                    '-filter_complex',filters,'-map','[v]','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-t','25',str(corrected)],check=True)
    corrected.replace(ROOT/'picture.mp4')
    mix_audio()
    print('Ingredient leader correction applied to final export.',flush=True)


if __name__=='__main__':
    (ROOT/'qa').mkdir(parents=True,exist_ok=True)
    tracking=state()
    if '--preview' in sys.argv:preview(tracking)
    elif '--repair-ingredients' in sys.argv:repair_ingredient_segment(tracking)
    else:render(tracking)
