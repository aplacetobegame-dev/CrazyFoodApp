"""Compose a review storyboard from the user's supplied app design reference.

Local layout only: no image/video model jobs and no reference uploads.
The app screenshots and wordmark are placed directly from the supplied sheet.
"""
from pathlib import Path
from functools import lru_cache
import importlib.util
import json
import textwrap
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REF = ROOT / "references/food-felonies-app-design.png"
spec = importlib.util.spec_from_file_location("previous_plan", ROOT / "build_storyboard.py")
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)
v1 = previous.v1
PAPER, WHITE, INK, RED = "#FAF6EF", "#FFFFFF", "#211F1C", "#C83E2F"
MUTED, MUSTARD, PICKLE, GREEN = "#665E56", "#F5BA47", "#B7D76E", "#276D52"
W, H = 720, 1280
reference = Image.open(REF).convert("RGB")
screens = {
    "welcome": reference.crop((7, 9, 317, 778)),
    "create": reference.crop((320, 9, 630, 778)),
    "loading": reference.crop((631, 9, 922, 778)),
    "case": reference.crop((923, 9, 1227, 778)),
    "community": reference.crop((1230, 9, 1536, 778)),
}
wordmark = reference.crop((41, 60, 284, 268))
tagline = reference.crop((53, 267, 253, 352))


def ensure_fonts():
    sources = {
        "bricolagegrotesque": ("BricolageGrotesque.ttf", "BricolageGrotesque%5Bopsz%2Cwdth%2Cwght%5D.ttf"),
        "dmsans": ("DMSans.ttf", "DMSans%5Bopsz%2Cwght%5D.ttf"),
        "ibmplexmono": ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Regular.ttf"),
    }
    for family, (name, remote_name) in sources.items():
        folder = ROOT / "references/fonts" / family
        folder.mkdir(parents=True, exist_ok=True)
        for target_name, url_name in [(name, remote_name), ("OFL.txt", "OFL.txt")]:
            path = folder / target_name
            if not path.exists():
                response = requests.get(f"https://raw.githubusercontent.com/google/fonts/main/ofl/{family}/{url_name}", timeout=30)
                response.raise_for_status()
                path.write_bytes(response.content)


@lru_cache(maxsize=100)
def font(size, role="body", bold=False):
    paths = {
        "display": "bricolagegrotesque/BricolageGrotesque.ttf",
        "body": "dmsans/DMSans.ttf",
        "mono": "ibmplexmono/IBMPlexMono-Regular.ttf",
    }
    f = ImageFont.truetype(str(ROOT / "references/fonts" / paths[role]), int(size))
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


def text(d, xy, value, size=25, color=INK, role="body", bold=False, anchor=None):
    d.text(xy, value, fill=color, font=font(size, role, bold), anchor=anchor)


def place(im, asset, x, y, width):
    height = round(asset.height * width / asset.width)
    im.paste(asset.resize((width, height), v1.RESAMPLE), (x, y))
    return height


def food_frame(scene, index):
    im = v1.cover(v1.STILLS[scene["key"]], W, H)
    d = ImageDraw.Draw(im)
    # Reuse the supplied wordmark as an image layer; do not redraw its lettering.
    place(im, wordmark, 37, 31, 157)
    text(d, (674, 64), f"EXHIBIT {chr(65+index)}", 21, PAPER, "mono", anchor="ra")
    for j, line in enumerate(scene["headline"]):
        size = 65 if len(line) > 12 else 73
        text(d, (39, 210+j*86), line, size, PAPER, "display")
    text(d, (42, 405), scene["name"], 24, PAPER, "body", True)
    d.rounded_rectangle((42, 455, 330, 514), radius=18, fill=RED)
    text(d, (186, 483), f"CRIME LEVEL {scene['score']}/100", 20, WHITE, "mono", anchor="mm")
    d.rounded_rectangle((147, 1173, 573, 1214), radius=18, fill=PAPER)
    text(d, (360, 1193), "AI-generated concept image", 20, INK, anchor="mm")
    return im


def app_frame(kind):
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    text(d, (40, 49), "FOOD FELONIES", 27, INK, "display")
    if kind == "create":
        text(d, (40, 135), "Your ingredients.", 65, INK, "display")
        text(d, (40, 215), "Your food crime.", 65, RED, "display")
        place(im, screens["create"], 31, 337, 354)
        place(im, screens["loading"], 401, 436, 275)
        text(d, (360, 1238), "Create recipe  >  Chef mascot reveal", 23, MUTED, anchor="mm")
    else:
        text(d, (40, 135), "Make it. Cook it.", 65, INK, "display")
        text(d, (40, 215), "Show the evidence.", 60, RED, "display")
        place(im, screens["case"], 30, 337, 351)
        place(im, screens["community"], 398, 425, 278)
        text(d, (360, 1238), "Case file  >  Cooked results + verdict", 23, MUTED, anchor="mm")
    return im


def end_frame():
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)
    text(d, (360, 77), "CASE CLOSED. APP OPEN.", 23, RED, "mono", anchor="mm")
    place(im, wordmark, 99, 179, 522)
    place(im, tagline, 146, 654, 428)
    d.rounded_rectangle((47, 951, 673, 1051), radius=47, fill=RED)
    text(d, (360, 1000), "Download Food Felonies", 33, WHITE, "body", True, "mm")
    text(d, (360, 1123), "Commit your first food crime.", 31, INK, "display", anchor="mm")
    return im


def build():
    ensure_fonts()
    scenes = [dict(scene) for scene in previous.SCENES]
    scenes[3].update(motion="Ingredients appear. Slider moves to 72. Chef mascot pops in.", method="Supplied Create + Generating screens")
    scenes[4].update(motion="Case file lands. Crime + regret cards pulse. Community verdict reveal.", method="Supplied recipe + Community screens")
    scenes[5].update(motion="Actual wordmark lands. Red download button pops.", method="Supplied wordmark + handwritten tagline")
    canvas = Image.new("RGB", (1440, 2245), PAPER)
    d = ImageDraw.Draw(canvas)
    text(d, (28, 24), "Food Felonies / 25-second commercial", 45, INK, "display")
    text(d, (28, 85), "REVISED TO MATCH YOUR APP REFERENCE", 24, RED, "mono")
    text(d, (28, 128), "Review storyboard only. Proposed Seedance motion has not been generated.", 23, MUTED)
    for i, scene in enumerate(scenes):
        x, y = 24+(i%3)*472, 190+(i//3)*985
        im = food_frame(scene, i) if i < 3 else end_frame() if i == 5 else app_frame(scene["key"])
        im.save(ROOT/f"brand-scene-{i+1:02d}.jpg", quality=95)
        canvas.paste(im.resize((424, 754), v1.RESAMPLE), (x+12,y+43))
        d.rounded_rectangle((x,y,x+448,y+43), radius=6, fill=PICKLE if i in [3,4] else MUSTARD)
        text(d, (x+12,y+9), f"{scene['time']} / {scene['title']}", 20, INK, "display")
        lines = textwrap.wrap(scene["motion"], width=36)
        for j, line in enumerate(lines):
            text(d, (x+2,y+811+j*29), line, 20, INK, "body", True)
        text(d, (x+2,y+910), scene["audio"], 18, RED)
        for j, line in enumerate(textwrap.wrap(scene["method"], width=48)):
            text(d, (x+2,y+939+j*20), line, 15, MUTED)
    text(d, (28, 2182), "SEEDANCE 2.5 / 3 x 4s AT 1080p / PREVIOUS QUOTE: 192 CREDITS TOTAL", 23, INK, "mono")
    canvas.save(ROOT/"explosive-25s-storyboard-brand-v2.jpg", quality=95)
    plan = json.loads((ROOT/"generation-plan.json").read_text(encoding="utf-8"))
    plan.update(status="awaiting_user_review", brand_reference=str(REF.relative_to(ROOT)),
                storyboard="explosive-25s-storyboard-brand-v2.jpg", scenes=scenes,
                typography=["Bricolage Grotesque", "DM Sans", "IBM Plex Mono"],
                palette={"paper":PAPER, "red":RED, "pickle_green":PICKLE, "mustard":MUSTARD, "muted_ink":MUTED},
                notes="Use the supplied app screen designs directly. The displayed example recipe is Pickle-Maple Crispy Rice, Crime Level 72/100, Regret Potential 38/100. These are supplied visual mockups, not independently verified user testimonials. No video jobs submitted.")
    (ROOT/"generation-plan-brand-v2.json").write_text(json.dumps(plan,indent=2),encoding="utf-8")
    print(ROOT/"explosive-25s-storyboard-brand-v2.jpg")


if __name__ == "__main__":
    build()
