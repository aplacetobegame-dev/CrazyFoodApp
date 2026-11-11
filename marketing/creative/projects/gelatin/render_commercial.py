"""Editable 25-second gelatin commercial; source footage plus shared brand kit.

Writes new exports only under build/. The selected delivery remains unchanged.
"""
from pathlib import Path
from functools import lru_cache
import sys, math, json, shutil, subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
ROOT=Path(__file__).resolve().parent
CREATIVE=ROOT.parents[1]
SHARED=CREATIVE/'shared'
sys.path.insert(0,str(SHARED))
import engine as v7
import hearts as v8
v5=v7.v5
previous=v7.previous
W,H,FPS,S=v7.W,v7.H,v7.FPS,v7.S
sc,box,rr,text,paste=v7.sc,v7.box,v7.rr,v7.text,v7.paste
PAPER,INK,RED,PICKLE,MUTED,GREEN=v7.PAPER,v7.INK,v7.RED,v7.PICKLE,v7.MUTED,v7.GREEN
crime,stage,chef=v7.crime,v7.stage,v7.chef
floating,place_art,leader,ease=v7.floating,v7.place_art,v7.leader,v7.ease
rays=v7.rays
opening_wash,STAGES=v7.opening_wash,v7.STAGES
RES=Image.Resampling.LANCZOS
SOURCE=ROOT
BUILD=ROOT/'build'
FINAL=BUILD/'food-felonies-gelatin-25s.mp4'
AUDIO_SOURCE=CREATIVE/'final-videos/food-felonies-gelatin-25s.mp4'
CONCEPT=Image.open(CREATIVE/'food-crime-images/AC-041-vegetable-gelatin-v1.png').convert('RGB')
ORIGINAL=Image.open(CREATIVE.parent/'seed_database/archive_images/AC-041_savory-gelatin-mold-with-suspended-vegetables.png').convert('RGB')
INGREDIENTS={name:Image.open(SHARED/f'ingredients/{name}.png').convert('RGBA') for name in ['onion','green-pepper','gelatin','celery']}
STARTS=[16.4,17.6,18.8,20.0]
SOURCE_STARTS=[.55,.75,.55,1.35]
SPEEDS=[1,1,1,1.5]


def concept_phone_ui(kind, t):
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
        rr(d,(22,105,224,139),v5.brand.MUSTARD,4)
        text(d,(33,113),"CASE FILE #0041",16,role="mono")
        text(d,(22,167),"Vegetable Gelatin",30,role="display")
        paste(im,CONCEPT,(22,225,356,315),.83,14)
        rr(d,(22,568,378,632),"#F8D3CC",15)
        text(d,(39,585),"CRIME LEVEL",16,RED,"mono")
        text(d,(362,600),"92/100",27,RED,"display",anchor="rm")
        rr(d,(22,661,378,719),RED,27)
        text(d,(200,690),"Show recipe  >",22,"white",bold=True,anchor="mm")
    return np.array(im)

def phone_ui(kind,t):
    if kind!='meter':
        return concept_phone_ui(kind,t)
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
    paste(panel,CONCEPT,(15,15,530,530),.82,16)
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

@lru_cache(maxsize=2)
def photo_card(which):
    # Explicit framing gives both molds comparable scale despite different source ratios.
    source=CONCEPT if which==0 else ORIGINAL
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

@lru_cache(maxsize=8)
def avatar(index=-1):
    if index<0:
        im=Image.open(ROOT/'references/lead-avatar.jpg').convert('RGB').crop((140,430,980,1270))
    else:
        im=Image.open(SHARED/f'recipients/references/recipient-{index}.png').convert('RGB').crop((70,30,740,700))
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
    v7.paste(im,ORIGINAL,(194,12,123,124),.5,9)
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
    cap=cv2.VideoCapture(str(SHARED/f'recipients/raw/reaction-{i}.mp4'))
    cap.set(cv2.CAP_PROP_POS_MSEC,3500);ok,bgr=cap.read();cap.release();assert ok
    im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).crop((55,1400,1025,1900))
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


def readers():
    return {'lead':[v5.Reader(ROOT/f'raw/scene-{i}.mp4') for i in range(3)],
            'recipients':[v5.Reader(SHARED/f'recipients/raw/reaction-{i}.mp4') for i in range(4)],
            'cooking':[v5.Reader(ROOT/f'raw/cooking-{i}.mp4') for i in range(4)]}


def close(data):
    for group in data.values():
        for reader in group:reader.cap.release()


@lru_cache(maxsize=1)
def end_card():
    return Image.open(SHARED/'brand/end-card-mask.png').convert('RGB')


def opening_frame(t,data,tracking):
    index=0 if t<6 else 1
    local=t if index==0 else t-6
    frame=data['lead'][index].get(local)
    if index==0 and local<3:
        track=tracking['phone']
        q=track['quads'].get(round(local*track['fps']))
        frame=v5.composite_phone(frame,phone_ui('meter' if t<2 else 'concept',local),q)
    im=ImageEnhance.Color(ImageEnhance.Contrast(Image.fromarray(frame)).enhance(1.035)).enhance(1.055)
    if not 4.8<=t<6:im=previous.punch(im,t)
    im=im.convert('RGBA');layer=v5.new_layer()
    if t<2:opening(layer,t)
    elif t<3.15:food_reveal(layer,t)
    elif t<4.8:
        floating(layer,'Do I dare to cook this?',(360,1070),54,t-3.21,PAPER,-4,life=1.59,drift=1.2)
    elif t<6:ingredient_labels(layer,t,tracking['ingredients'])
    elif t<7.8:floating(layer,'CHOP.',(167,1040),72,t-6,PAPER,-7,life=1.8)
    elif t<8.8:floating(layer,'MIX.',(550,1020),75,t-7.8,RED,5,life=1)
    elif t<9.4:floating(layer,'POUR.',(174,1120),68,t-8.8,PAPER,-6,life=.6)
    else:
        text(ImageDraw.Draw(layer),(47,97),'AFTER CHILLING',20,PAPER,'mono')
        floating(layer,'JIGGLE.',(375,1122),72,t-10.22,RED,4,life=.78)
    return Image.alpha_composite(im,layer).convert('RGB')


def sharing_frame(t,data,tracking):
    local=t-11
    track=tracking['share']
    frame=data['lead'][2].get(local)
    quad=track['quads'].get(round(local*track['fps']))
    frame=v5.composite_phone(frame,phone_ui('concept',local),quad)
    im=Image.fromarray(frame).convert('RGBA')
    layer=v5.new_layer();layer.alpha_composite(share_panel(t))
    floating(layer,'SHOW THE EVIDENCE.',(360,180),43,t-11.2,PAPER,-4,life=2.8)
    im=Image.alpha_composite(im,layer)
    if t>=13.86:
        wash=Image.new('RGBA',(W,H),PAPER)
        wash.putalpha(round(235*min(1,(t-13.86)/.14)))
        im=Image.alpha_composite(im,wash)
    layer=v5.new_layer();v8.hearts(layer,t)
    return Image.alpha_composite(im,layer).convert('RGB')


def visual_frame(t,data,tracking):
    if not 0<=t<25:raise ValueError('Time must be within [0, 25).')
    if t<11:return opening_frame(t,data,tracking)
    if t<14:return sharing_frame(t,data,tracking)
    if t<16.4:
        im=discovery_grid(t,data);layer=v5.new_layer();v8.hearts(layer,t)
        return Image.alpha_composite(im,layer).convert('RGB')
    if t<21.2:return cooking_transition(t,data).convert('RGB')
    if t<22:return four_uploads(t).convert('RGB')
    return end_card().copy()


def preview():
    times=[.4,1.75,2.6,3.9,5.5,6.4,8.2,9.1,10.5,12.8,13.7,14.7,15.7,16.8,18.,19.2,20.5,21.6,23.5]
    board=Image.new('RGB',(1350,math.ceil(len(times)/5)*520),PAPER)
    d=ImageDraw.Draw(board);data=readers();tracking=state()
    try:
        for i,t in enumerate(times):
            frame=visual_frame(t,data,tracking)
            assert frame.size==(W,H)
            frame.save(BUILD/f'frame-{t:05.2f}.jpg',quality=95)
            board.paste(frame.resize((270,480),RES),((i%5)*270,(i//5)*520))
            d.text(((i%5)*270+8,(i//5)*520+487),f'{t:05.2f}s',fill=INK,font=v5.brand.font(20))
    finally:close(data)
    board.save(BUILD/'contact-sheet.jpg',quality=95)
    print('Preview ready:',BUILD/'contact-sheet.jpg',flush=True)


def render():
    if not AUDIO_SOURCE.is_file():raise FileNotFoundError(AUDIO_SOURCE)
    ffmpeg=shutil.which('ffmpeg')
    if not ffmpeg:raise RuntimeError('Install FFmpeg and put it on PATH.')
    picture=BUILD/'picture.mp4';log_path=BUILD/'render.log'
    command=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-c:v','libx264',
             '-preset','fast','-crf','16','-pix_fmt','yuv420p','-t','25',str(picture)]
    data=readers();tracking=state()
    with log_path.open('w') as log:
        proc=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(750):
                proc.stdin.write(visual_frame(i/30,data,tracking).tobytes())
                if i%90==0:print(f'Rendered {i//30}/25 seconds',flush=True)
        finally:proc.stdin.close();close(data)
        if proc.wait():raise RuntimeError(log_path.read_text())
    # The approved delivery is the soundtrack source: preserves exact AAC music/foley.
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-i',str(picture),'-i',str(AUDIO_SOURCE),
                    '-map','0:v:0','-map','1:a:0','-c','copy','-t','25','-movflags','+faststart',str(FINAL)],check=True)
    print('New export ready:',FINAL,flush=True)


if __name__=='__main__':
    BUILD.mkdir(parents=True,exist_ok=True)
    if '--preview' in sys.argv:preview()
    else:render()

