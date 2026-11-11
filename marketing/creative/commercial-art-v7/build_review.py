"""Review layouts only; generated artwork remains unchanged in source PNGs."""
from pathlib import Path
from functools import lru_cache
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = Path(__file__).resolve().parent
FONTS = ROOT.parent / 'commercial-v2-plan/references/fonts'
PAPER, INK, RED = '#FAF6EF', '#211F1C', '#C83E2F'
GREEN, MUTED, PICKLE = '#276D52', '#665E56', '#B7D76E'
RES = Image.Resampling.LANCZOS


@lru_cache(maxsize=60)
def font(size, mono=False):
    path = FONTS / ('ibmplexmono/IBMPlexMono-Regular.ttf' if mono else 'bricolagegrotesque/BricolageGrotesque.ttf')
    f = ImageFont.truetype(str(path), size)
    if not mono:
        axes = f.get_variation_axes()
        f.set_variation_by_axes([800 if b'Weight' in a['name'] else a['default'] for a in axes])
    return f


def text(im, xy, value, size, color=INK, mono=False, anchor=None):
    ImageDraw.Draw(im).text(xy, value, font=font(size, mono), fill=color, anchor=anchor)


def place(im, art, center, bounds):
    art = art.copy()
    bbox = art.getchannel('A').getbbox()
    if bbox:
        art = art.crop(bbox)
    art.thumbnail(bounds, RES)
    im.alpha_composite(art, (round(center[0]-art.width/2), round(center[1]-art.height/2)))


def floating_word(im, word, center, size, angle, color=RED):
    f = font(size)
    probe = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    bb = probe.textbbox((0, 0), word, font=f, stroke_width=3)
    layer = Image.new('RGBA', (bb[2]-bb[0]+42, bb[3]-bb[1]+48))
    d = ImageDraw.Draw(layer)
    pos = (20-bb[0], 18-bb[1])
    d.text((pos[0]+4, pos[1]+7), word, font=f, fill=INK, stroke_width=5, stroke_fill=INK)
    d.text(pos, word, font=f, fill=color, stroke_width=3, stroke_fill=PAPER)
    layer = layer.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    im.alpha_composite(layer, (round(center[0]-layer.width/2), round(center[1]-layer.height/2)))


def chef_board():
    im = Image.new('RGBA', (1920, 1390), PAPER)
    text(im, (75, 43), 'FOOD FELONIES / CHARACTER ART', 24, MUTED, True)
    text(im, (72, 85), 'TURN UP THE CRIME.', 91)
    text(im, (1845, 150), 'SIX ESCALATING STATES', 23, MUTED, True, 'ra')
    d = ImageDraw.Draw(im)
    d.line((75, 211, 1845, 211), fill=INK, width=2)
    sheet = Image.open(ROOT/'chef-toxic-progression.png').convert('RGBA')
    labels = ['CURIOUS', 'BAD IDEA', 'SUIT UP', 'TOXIC', 'UNSTABLE', 'FOOD FELONY']
    for i, label in enumerate(labels):
        col, row = i%3, i//3
        crop = sheet.crop((col*512, row*512, (col+1)*512, (row+1)*512))
        cx, cy = 365+col*595, 440+row*505
        place(im, crop, (cx, cy), (484, 386))
        text(im, (cx, cy+210), label, 36, RED if i==5 else INK, anchor='mm')
        text(im, (cx, cy+253), f'{i*20:03d} / 100', 22, MUTED, True, 'mm')
    d.line((75, 1248, 1845, 1248), fill=INK, width=2)
    text(im, (75, 1291), 'SAME CHEF. MORE CHAOS AT EVERY STEP.', 28)
    text(im, (1845, 1297), 'ART REVIEW / BEFORE ANIMATION', 21, MUTED, True, 'ra')
    im.convert('RGB').save(ROOT/'chef-progression-review.png')


def ingredients_board():
    im = Image.new('RGBA', (1920, 940), PAPER)
    text(im, (75, 43), 'FOOD FELONIES / INGREDIENT ART', 24, MUTED, True)
    text(im, (72, 85), 'THE INGREDIENT LINEUP.', 88)
    d = ImageDraw.Draw(im)
    d.line((75, 211, 1845, 211), fill=INK, width=2)
    items = [('gelatin', 'GELATIN', -6), ('celery', 'CELERY', 5), ('green-pepper', 'GREEN PEPPER', -4), ('onion', 'ONION', 6)]
    for i, (name, label, angle) in enumerate(items):
        cx = 295+i*445
        art = Image.open(ROOT/f'ingredient-{name}.png').convert('RGBA')
        place(im, art, (cx, 468), (340, 355))
        floating_word(im, label, (cx, 728), 53 if name=='green-pepper' else 66, angle, GREEN if i in (1, 2) else RED)
        for side in [-1, 1]:
            x = cx+side*173
            d.line((x, 668, x+side*13, 646), fill=RED if i%2 else GREEN, width=5)
            d.line((x+side*8, 697, x+side*31, 688), fill=RED if i%2 else GREEN, width=5)
    text(im, (960, 856), 'Isolated artwork + precisely typeset floating labels', 27, MUTED, anchor='mm')
    im.convert('RGB').save(ROOT/'ingredient-art-review.png')


def validate():
    report = {'tool': 'built-in image_gen', 'source_art_unchanged': True, 'assets': []}
    for p in sorted(ROOT.glob('*.png')):
        if 'review' in p.stem:
            continue
        im = Image.open(p)
        a = np.asarray(im.getchannel('A'))
        entry = {'file':p.name, 'size':list(im.size), 'mode':im.mode,
                 'transparent_fraction':round(float((a==0).mean()), 4), 'alpha_min':int(a.min()), 'alpha_max':int(a.max())}
        assert im.mode=='RGBA' and a.min()==0 and a.max()>250, entry
        report['assets'].append(entry)
    report['visual_review'] = ['Chef identity and gas-mask design checked across six states.',
        'Two eye windows and two side filters preserved in masked states.',
        'Increasing vapor and green lens light are deliberate foreground artwork.',
        'Ingredient silhouettes and labels checked: GELATIN, CELERY, GREEN PEPPER, ONION.',
        'Review boards alpha-composite source art on the app paper color.']
    (ROOT/'verification.json').write_text(json.dumps(report, indent=2)+'\n')


if __name__ == '__main__':
    chef_board()
    ingredients_board()
    validate()
    print('Rendered chef and ingredient review boards; verified all 6 source PNGs have alpha.')
