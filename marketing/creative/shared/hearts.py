"""Share-heart transport and recipient reveals, without campaign dependencies."""
from pathlib import Path
from functools import lru_cache
import importlib.util
import math
import sys
import numpy as np
from PIL import Image, ImageDraw

# Resolve the sibling directly, including when this file is loaded by path.
_ENGINE_KEY = '_food_felonies_shared_engine'
if _ENGINE_KEY in sys.modules:
    v7 = sys.modules[_ENGINE_KEY]
else:
    _spec = importlib.util.spec_from_file_location(_ENGINE_KEY, Path(__file__).with_name('engine.py'))
    v7 = importlib.util.module_from_spec(_spec)
    sys.modules[_ENGINE_KEY] = v7
    try:
        _spec.loader.exec_module(v7)
    except BaseException:
        sys.modules.pop(_ENGINE_KEY, None)
        raise
v5 = v7.v5
W, H, FPS, S = v7.W, v7.H, v7.FPS, v7.S
sc, box, rr, text = v7.sc, v7.box, v7.rr, v7.text
PAPER, INK, RED, GREEN, MUTED = v7.PAPER, v7.INK, v7.RED, v7.GREEN, v7.MUTED
RES = Image.Resampling.LANCZOS
ENTRIES = [14.0,14.14,14.28,14.42]


def ease(p):return v7.ease(p)


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
