"""Food-specific branded overlays for Breakfast: Final Boss.

All scene overlay functions mutate and return the supplied RGBA layer. Coordinates
are in the existing 720x1280 design space, scaled to the 1080x1920 output by S.
The source bitmaps remain unchanged; this module performs layout and animation.
"""
from pathlib import Path
from functools import lru_cache
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent
REF = ROOT / 'references'
SHARED = ROOT.parents[1] / 'shared'
sys.path.insert(0, str(SHARED))
import engine as v7
v5 = v7.v5
W, H, FPS, S = v7.W, v7.H, v7.FPS, v7.S
sc, box, rr, text, paste = v7.sc, v7.box, v7.rr, v7.text, v7.paste
PAPER, INK, RED, PICKLE, MUTED, GREEN = v7.PAPER, v7.INK, v7.RED, v7.PICKLE, v7.MUTED, v7.GREEN
MUSTARD = v5.brand.MUSTARD
RES = Image.Resampling.LANCZOS
HERO = Image.open(REF / 'hero-food.png').convert('RGB')
RESULT = Image.open(REF / 'homemade-result.png').convert('RGB')
CASE_ID, CRIME_SCORE = 'AC-059', 88
INGREDIENT_NAMES = ['brioche', 'egg-mix', 'bacon', 'ice-cream']
INGREDIENT_LABELS = ['BRIOCHE', 'EGG MIX', 'BACON', 'ICE CREAM']


def ease(value):
    return v7.ease(value)


@lru_cache(maxsize=4)
def ingredient_art(index):
    sheet = Image.open(REF / 'ingredient-atlas.png').convert('RGBA')
    cw, ch = sheet.width // 2, sheet.height // 2
    col, row = index % 2, index // 2
    tile = sheet.crop((col*cw, row*ch, (col+1)*cw, (row+1)*ch))
    bounds = tile.getchannel('A').getbbox()
    return tile.crop(bounds) if bounds else tile


def place_cutout(layer, art, center, size=84, angle=0):
    piece = art.copy()
    piece.thumbnail((sc(size), sc(size)), RES)
    if angle:
        piece = piece.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    layer.alpha_composite(piece, (round(sc(center[0])-piece.width/2), round(sc(center[1])-piece.height/2)))


def phone_ui(kind, t):
    """RGB numpy UI at 400x760 base units; input max100, recipe stat88."""
    im = Image.new('RGBA', (sc(400), sc(760)), PAPER)
    d = ImageDraw.Draw(im)
    text(d, (22,25), 'Food Felonies', 27, role='display')
    d.line(box((22,77,378,77)), fill='#DED9CB', width=sc(1))
    if kind == 'meter':
        value = v7.crime(t)
        text(d, (22,101), 'Choose your chaos.', 28, role='display')
        text(d, (22,148), 'Normal is optional.', 17, MUTED)
        v7.chef(im, t, (200,315), 265)
        text(d, (22,470), 'Crime level', 22, bold=True)
        text(d, (378,470), f'{value}/100', 22, RED, 'mono', anchor='ra')
        rr(d, (25,534,375,544), '#D5D2C7', 5)
        xx = 25 + 350*value/100
        if value:
            rr(d, (25,534,xx,544), RED, 5)
        for notch in range(1,5):
            x = 25 + 70*notch
            d.line(box((x,535,x,543)), fill=PAPER, width=sc(2))
        d.ellipse(box((xx-12,527,xx+12,551)), fill=RED, outline='white', width=sc(2))
        text(d, (25,576), 'Normal', 16, MUTED)
        text(d, (375,576), 'Food Felony', 16, RED, anchor='ra')
        rr(d, (22,635,378,696), RED, 29)
        text(d, (200,665), 'Generate recipe  >', 22, 'white', bold=True, anchor='mm')
        text(d, (200,733), v7.STAGES[v7.stage(t)], 18, RED, 'mono', anchor='mm')
    else:
        rr(d, (22,105,244,139), MUSTARD, 4)
        text(d, (33,113), 'CASE FILE #AC-059', 15, role='mono')
        text(d, (22,164), 'Bacon Ice-Cream', 28, role='display')
        text(d, (22,200), 'French Toast', 29, role='display')
        paste(im, RESULT if kind == 'share' else HERO, (22,254,356,267), .5, 14)
        rr(d, (22,568,378,632), '#F8D3CC', 15)
        text(d, (39,585), 'CRIME LEVEL', 16, RED, 'mono')
        text(d, (362,600), '88/100', 27, RED, 'display', anchor='rm')
        rr(d, (22,661,378,719), RED, 27)
        text(d, (200,690), 'Share my result  >' if kind == 'share' else 'Show recipe  >', 22, 'white', bold=True, anchor='mm')
    return np.array(im.convert('RGB'))


def opening(layer, t):
    layer.alpha_composite(v7.opening_wash())
    v7.floating(layer, 'BREAKFAST:', (360,90), 40, t, PAPER, -3, life=2, drift=.6)
    v7.floating(layer, 'FINAL BOSS', (360,151), 61, t-.045, RED if t>=1.55 else PAPER, -3, life=1.955, drift=.6)
    v7.chef(layer, t, (177,984), 255)
    value = v7.crime(t)
    d = ImageDraw.Draw(layer)
    text(d, (506,917), 'CRIME LEVEL', 22, INK, 'mono', anchor='mm')
    text(d, (507,985), str(value), 91, RED, 'display', anchor='mm')
    text(d, (507,1050), v7.STAGES[v7.stage(t)], 20, RED, 'mono', anchor='mm')
    rr(d, (63,1122,657,1134), '#D8D2C6', 6)
    xx = 63 + 594*value/100
    if value:
        rr(d, (63,1122,xx,1134), RED, 6)
    for notch in range(1,5):
        x = 63 + 594*notch/5
        d.line(box((x,1123,x,1133)), fill=PAPER, width=sc(3))
    d.ellipse(box((xx-15,1113,xx+15,1143)), fill=RED, outline=PAPER, width=sc(3))
    text(d, (63,1170), 'Normal', 21, MUTED)
    text(d, (657,1170), 'Food Felony', 21, RED, anchor='ra')
    return layer


def dish_reveal(layer, t):
    age = t-2
    if age < 0:
        return layer
    panel = Image.new('RGBA', (sc(560),sc(568)), PAPER)
    d = ImageDraw.Draw(panel)
    rr(d, (146,20,414,61), MUSTARD, 8)
    text(d, (280,40), 'RECIPE UNLOCKED', 19, INK, 'mono', anchor='mm')
    paste(panel, HERO, (15,79,530,398), .5, 15)
    text(d, (280,520), 'CRIME LEVEL  88 / 100', 21, RED, 'mono', anchor='mm')
    panel = panel.rotate(-2+ease(age/.22), Image.Resampling.BICUBIC, expand=True)
    layer.alpha_composite(panel, (round(sc(360)-panel.width/2), round(sc(563)-panel.height/2+sc(36*(1-ease(age/.22))))))
    v7.floating(layer, 'BACON ICE-CREAM', (360,1000), 43, age, RED, -4, life=1.2)
    v7.floating(layer, 'FRENCH TOAST', (360,1075), 58, age-.045, PAPER, 2, life=1.155)
    return layer


def grin(layer, t):
    v7.floating(layer, 'Do I dare to cook this?', (360,1070), 54, t-3.24, PAPER, -4, life=1.46, drift=1.2)
    return layer


DEFAULT_INVENTORY = {
    'brioche': {'center':(160,185), 'target':(200,400), 'size':42, 'angle':-5},
    'egg-mix': {'center':(545,185), 'target':(530,430), 'size':42, 'angle':4},
    'bacon': {'center':(155,1030), 'target':(180,810), 'size':43, 'angle':-5},
    'ice-cream': {'center':(550,1030), 'target':(545,820), 'size':41, 'angle':4},
}


def inventory(layer, t, layout=None):
    """Optional layout maps ingredient keys to center/target/size/angle/icon entries.

    A key may also map directly to an (x,y) center. Set target=None to omit its
    leader, or pass an explicit icon center. This lets raw-footage QA tune anchors.
    """
    for i, (key,label) in enumerate(zip(INGREDIENT_NAMES,INGREDIENT_LABELS)):
        settings = dict(DEFAULT_INVENTORY[key])
        if layout and key in layout:
            change = layout[key]
            settings.update(change if isinstance(change,dict) else {'center':change})
        start = 4.75+i*.13
        age = t-start
        if age < 0:
            continue
        center, target = settings['center'], settings.get('target')
        size, angle = settings.get('size',42), settings.get('angle',-4)
        if target is not None and age>.10:
            direction = -1 if target[1]<center[1] else 1
            v7.leader(layer, (center[0],center[1]+direction*31), target)
        icon_center = settings.get('icon',(center[0],center[1]-76))
        kick = 1+.10*math.sin(math.pi*min(age/.18,1)) if age<.18 else 1
        place_cutout(layer, ingredient_art(i), icon_center, 88*kick, angle/2)
        v7.floating(layer, label, center, size, age, RED if i%2==0 else GREEN, angle, life=6-start, drift=.7)
    return layer


# Timing follows the measured source cuts, retimed from6 seconds to5 seconds.
_CUTS = [6+x*5/6 for x in [0,1.0417,1.8333,2.6667,4.3333,6]]
COOKING_CUES = [
    (_CUTS[0],_CUTS[1],'DIP.',(164,1100),72,PAPER,-6),
    (_CUTS[1],_CUTS[2],'FLIP.',(540,1100),72,RED,5),
    (_CUTS[2],_CUTS[3],'CRUNCH.',(190,1100),65,PAPER,-5),
    (_CUTS[3],_CUTS[4],'FINISHER.',(360,1110),62,RED,3),
    (_CUTS[4],_CUTS[5],'WORTH IT.',(360,1100),65,PAPER,-3),
]


def cooking(layer, t):
    cue = next((c for c in COOKING_CUES if c[0]<=t<c[1]), None)
    if cue is None:
        return layer
    start,end,label,center,size,color,angle = cue
    v7.floating(layer, label, center, size, t-start, color, angle, life=end-start)
    combo = min(4, 1+sum(t>=c[0] for c in COOKING_CUES[1:4]))
    d = ImageDraw.Draw(layer)
    rr(d, (544,65,685,133), PAPER, 14, outline='#D8D1C8', width=1)
    text(d, (560,79), 'COMBO', 13, MUTED, 'mono')
    text(d, (666,104), f'x{combo}', 29, RED, 'display', anchor='rm')
    for i in range(4):
        d.ellipse(box((560+i*14,111,566+i*14,117)), fill=RED if i<combo else '#D8D1C8')
    return layer


@lru_cache(maxsize=2)
def photo_card(which):
    source = HERO if which==0 else RESULT
    photo = ImageOps.fit(source, (sc(304),sc(234)), RES, centering=(.5,.52))
    card = Image.new('RGBA', (sc(320),sc(250)), PAPER)
    card.alpha_composite(photo.convert('RGBA'), (sc(8),sc(8)))
    card = card.rotate(1.2 if which==0 else -1.2, Image.Resampling.BICUBIC, expand=True)
    shadow = Image.new('RGBA', card.size)
    shadow.putalpha(card.getchannel('A').point(lambda a:round(a*.16)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(sc(4)))
    out = Image.new('RGBA', (card.width+sc(18),card.height+sc(20)))
    out.alpha_composite(shadow, (sc(10),sc(12)))
    out.alpha_composite(card, (sc(7),sc(5)))
    return out


def comparison(layer, t):
    age = t-11.2
    if age<0:
        return layer
    v7.floating(layer, 'SHOW THE EVIDENCE.', (360,90), 43, age, PAPER, -4, life=2.8)
    card_layer = v5.new_layer()
    top = 590+round(55*(1-ease(age/.28)))
    shadow = v5.new_layer();sd = ImageDraw.Draw(shadow)
    rr(sd, (29,top+7,697,1193), (25,20,15,32), 27)
    card_layer.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(sc(8))))
    d = ImageDraw.Draw(card_layer)
    rr(d, (27,top,693,1185), PAPER, 27)
    text(d, (51,top+26), 'My breakfast felony', 28, role='display')
    text(d, (668,top+36), '#AC-059', 17, RED, 'mono', anchor='ra')
    text(d, (199,top+97), 'The idea', 29, role='display', anchor='mm')
    text(d, (521,top+97), 'The result', 29, role='display', anchor='mm')
    for i,x in enumerate([199,521]):
        tile = photo_card(i)
        card_layer.alpha_composite(tile, (round(sc(x)-tile.width/2),sc(top+126)))
    text(d, (360,top+405), 'CRIME LEVEL  88 / 100', 18, RED, 'mono', anchor='mm')
    tap = t-13.35
    press = math.sin(max(0,min(1,tap/.16))*math.pi)*3 if 0<tap<.16 else 0
    shared = t>=13.48
    button_y = top+447+press
    rr(d, (51,button_y,669,button_y+83), GREEN if shared else RED, 40)
    if shared:
        d.line([tuple(map(sc,p)) for p in [(263,button_y+40),(273,button_y+50),(290,button_y+31)]], fill='white', width=sc(3), joint='curve')
        text(d, (382,button_y+41), 'Shared!', 31, 'white', bold=True, anchor='mm')
    else:
        d.line([tuple(map(sc,p)) for p in [(231,button_y+51),(231,button_y+31),(223,button_y+39),(231,button_y+31),(239,button_y+39)]], fill='white', width=sc(2), joint='curve')
        text(d, (387,button_y+41), 'Share my result', 30, 'white', bold=True, anchor='mm')
    text(d, (360,top+562), 'Commercial dramatization', 14, MUTED, anchor='mm')
    if t>=13.86:
        alpha = max(0,1-(t-13.86)/.20)
        card_layer.putalpha(card_layer.getchannel('A').point(lambda a:round(a*alpha)))
    layer.alpha_composite(card_layer)
    return layer


@lru_cache(maxsize=5)
def avatar(index=-1):
    if index<0:
        im = Image.open(REF/'lead-actor.png').convert('RGB').crop((170,60,770,660))
    else:
        im = Image.open(SHARED/f'recipients/references/recipient-{index}.png').convert('RGB').crop((70,30,740,700))
    im = ImageOps.fit(im, (sc(38),sc(38)), RES)
    mask = Image.new('L',im.size)
    ImageDraw.Draw(mask).ellipse((0,0,im.width-1,im.height-1),fill=255)
    im = im.convert('RGBA');im.putalpha(mask)
    return im


@lru_cache(maxsize=1)
def post_card():
    im = Image.new('RGBA',(sc(330),sc(148)))
    d = ImageDraw.Draw(im)
    rr(d,(1,1,329,147),PAPER,15,outline='#D8D1C8',width=1)
    im.alpha_composite(avatar(),(sc(13),sc(13)))
    text(d,(61,13),'New post',17,role='display')
    text(d,(61,38),'From the cook',12,MUTED)
    text(d,(15,72),'Bacon ice-cream',18,role='display')
    text(d,(15,96),'toast',20,role='display')
    text(d,(15,128),'CRIME 88/100',11,RED,'mono')
    paste(im,RESULT,(194,12,123,124),.5,9)
    return im


@lru_cache(maxsize=4)
def community_photo(index):
    sheet = Image.open(REF/'community-results-atlas.png').convert('RGB')
    cw,ch = sheet.width//2,sheet.height//2
    col,row = index%2,index//2
    return sheet.crop((col*cw,row*ch,(col+1)*cw,(row+1)*ch))


def uploads(t):
    im = Image.new('RGBA',(W,H),PAPER)
    d = ImageDraw.Draw(im)
    text(d,(360,93),'Cooked Results',48,role='display',anchor='mm')
    text(d,(360,151),'Same recipe. Four versions.',24,MUTED,anchor='mm')
    for i in range(4):
        age = t-21.2-i*.04
        if age<0:
            continue
        u = ease(age/.17)
        x,y = 36+(i%2)*344,235+(i//2)*416+round(65*(1-u))
        rr(d,(x,y,x+304,y+364),'white',20,outline='#DDD6CC',width=1)
        paste(im,community_photo(i),(x+10,y+10,284,263),.5,14)
        im.alpha_composite(avatar(i),(sc(x+15),sc(y+292)))
        text(d,(x+66,y+300),'Photo added',22,GREEN,bold=True)
    text(d,(360,1167),'Commercial dramatization',15,MUTED,anchor='mm')
    return im


@lru_cache(maxsize=1)
def _end_frame():
    return ImageOps.fit(Image.open(SHARED/'brand/end-card-mask.png').convert('RGB'),(W,H),RES)


def end_card(t):
    return _end_frame().copy()


def _preview():
    """Optional UI-only QA board, without any video-model calls."""
    (ROOT/'build/qa').mkdir(parents=True, exist_ok=True)
    board = Image.new('RGB',(5*270,2*520),PAPER)
    views = []
    for t in [.5,1.75]:
        layer = Image.new('RGBA',(W,H),'#344B48');opening(layer,t);views.append(layer.convert('RGB'))
    for fn,t in [(dish_reveal,2.7),(inventory,5.7),(cooking,8.8),(comparison,12.6),(comparison,13.7)]:
        layer = Image.new('RGBA',(W,H),'#344B48');fn(layer,t);views.append(layer.convert('RGB'))
    views += [uploads(21.7),end_card(1)]
    for i,im in enumerate(views):
        board.paste(im.resize((270,480),RES),((i%5)*270,(i//5)*520))
    board.save(ROOT/'build/qa/ui-preview.jpg',quality=95)
    return ROOT/'build/qa/ui-preview.jpg'


if __name__=='__main__':
    print(_preview())
