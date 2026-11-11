"""Reusable Food Felonies rendering primitives, independent of campaign folders.

Coordinates use the original 720x1280 design space; output is1080x1920.
No generation jobs, network access, or campaign food photographs are loaded.
"""
from pathlib import Path
from functools import lru_cache
from types import SimpleNamespace
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
S, W, H, FPS = 1.5, 1080, 1920, 30
PAPER, WHITE, INK, RED = '#FAF6EF', '#FFFFFF', '#211F1C', '#C83E2F'
MUTED, MUSTARD, PICKLE, GREEN = '#665E56', '#F5BA47', '#B7D76E', '#276D52'
RES = RESAMPLE = Image.Resampling.LANCZOS
STAGES = ['CURIOUS','BAD IDEA','SUIT UP','TOXIC','UNSTABLE','FOOD FELONY']


@lru_cache(maxsize=100)
def font(size, role="body", bold=False):
    paths = {
        "display": "bricolagegrotesque/BricolageGrotesque.ttf",
        "body": "dmsans/DMSans.ttf",
        "mono": "ibmplexmono/IBMPlexMono-Regular.ttf",
    }
    f = ImageFont.truetype(str(ROOT / "brand/fonts" / paths[role]), int(size))
    try:
        axes = f.get_variation_axes()
        values = []
        for axis in axes:
            name = axis["name"].decode().lower()
            values.append(min(axis["maximum"], 800 if role == "display" else 700) if "weight" in name and (bold or role == "display") else axis["default"])
        f.set_variation_by_axes(values)
    except (OSError, ValueError):
        pass
    return f

def cover(im, width, height, focus=0.5):
    factor = max(width / im.width, height / im.height)
    nw, nh = round(im.width * factor), round(im.height * factor)
    im = im.resize((nw, nh), RESAMPLE)
    left = (nw - width) // 2
    top = round((nh - height) * focus)
    return im.crop((left, top, left + width, top + height))


brand = SimpleNamespace(PAPER=PAPER, WHITE=WHITE, INK=INK, RED=RED,
    MUTED=MUTED, MUSTARD=MUSTARD, PICKLE=PICKLE, GREEN=GREEN,
    font=font, v1=SimpleNamespace(cover=cover, RESAMPLE=RES))


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


# Compatibility names used by the existing campaign templates.
# These aliases point to local primitives; no old render module is imported.
v5 = SimpleNamespace(**{name:globals()[name] for name in (
    'S','W','H','FPS','PAPER','WHITE','INK','RED','PICKLE','MUTED','GREEN','MUSTARD',
    'RES','brand','font','cover','sc','box','rr','text','paste','ease','new_layer',
    'ordered_quad','detect_phone','composite_phone','precompute_phone_track',
    'lower_pill','uploads','Reader')})


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


previous = SimpleNamespace(v5=v5, rigid_track=rigid_track,
    pop_layer=pop_layer, punch=punch)



SHEET = Image.open(ROOT/'brand/chef-toxic-progression.png').convert('RGBA')
SPRITES = [SHEET.crop(((i%3)*512, (i//3)*512, (i%3+1)*512, (i//3+1)*512)) for i in range(6)]

@lru_cache(maxsize=4)
def ingredient_art(name):
    """Return a shared transparent ingredient cutout, loaded on first use."""
    if name not in ('onion','green-pepper','gelatin','celery'):
        raise ValueError(f'Unknown shared ingredient: {name}')
    return Image.open(ROOT/'ingredients'/f'{name}.png').convert('RGBA')

@lru_cache(maxsize=1)
def app_design():
    """Return the supplied reference sheet only when a caller needs it."""
    return Image.open(ROOT/'brand/app-design.png').convert('RGB')

@lru_cache(maxsize=1)
def approved_end_card():
    return ImageOps.fit(Image.open(ROOT/'brand/end-card-mask.png').convert('RGB'),(W,H),RES)

def end_card(t=0):
    """Approved static mask ending; t is accepted by campaign renderers."""
    return approved_end_card().copy()


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

def phone_ui(kind,t):
    if kind!='meter':
        raise ValueError('Shared phone_ui supports meter only; supply campaign-specific food UI')
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
