"""Render the 25-second Food Felonies commercial test with editable timing.

Uses approved AI concept stills, deterministic UI animation, an original
procedural instrumental soundtrack, and sound effects. No AI video job was
submitted: the Higgsfield connection returned UNAUTHORIZED after reconnect.
"""

from pathlib import Path
from functools import lru_cache
import json
import math
import shutil
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parent / "food-crime-images"
W, H, FPS, DURATION = 720, 1280, 30, 25
INK = "#20231D"
CREAM = "#F5F0E5"
PAPER = "#FFFCF5"
RED = "#D94332"
MUTED = "#74796D"
LINE = "#DEDCCD"
YELLOW = "#FFE36E"
FONTS = Path("C:/Windows/Fonts")
RESAMPLE = Image.Resampling.LANCZOS


@lru_cache(maxsize=120)
def font(size, weight="regular"):
    names = {"regular": "segoeui.ttf", "bold": "segoeuib.ttf",
             "display": "ARIALNB.TTF"}
    return ImageFont.truetype(str(FONTS / names[weight]), int(size))


def txt(draw, xy, value, size=24, color=INK, weight="regular", anchor=None):
    draw.text(xy, value, fill=color, font=font(size, weight), anchor=anchor,
              stroke_width=0)


def rr(draw, box, color, radius=18, outline=None, width=1):
    draw.rounded_rectangle(tuple(int(v) for v in box), radius=radius,
                           fill=color, outline=outline, width=width)


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease(v):
    v = clamp(v)
    return 1 - (1 - v) ** 3


def cover(im, width, height, focus=0.5):
    factor = max(width / im.width, height / im.height)
    nw, nh = round(im.width * factor), round(im.height * factor)
    im = im.resize((nw, nh), RESAMPLE)
    left = (nw - width) // 2
    top = round((nh - height) * focus)
    return im.crop((left, top, left + width, top + height))


STILLS = {
    "butter": Image.open(ASSETS / "AC-011-deep-fried-butter-v1.png").convert("RGB"),
    "candle": Image.open(ASSETS / "AC-030-candle-salad-v1.png").convert("RGB"),
    "gelatin": Image.open(ASSETS / "AC-041-vegetable-gelatin-v1.png").convert("RGB"),
}
BASES = {key: cover(im, W + 100, H + 178) for key, im in STILLS.items()}
SQUARES = {key: cover(im, 400, 320, focus=0.80) for key, im in STILLS.items()}


def top_brand(im, light=False):
    d = ImageDraw.Draw(im)
    color = CREAM if light else INK
    txt(d, (46, 60), "FOOD FELONIES", 30, color, "display")
    d.line((46, 110, 674, 110), fill=color, width=1)
    txt(d, (674, 66), "THE DINNER FILES", 14, color, anchor="ra")


def footer(im, caption, light=False):
    d = ImageDraw.Draw(im)
    color = CREAM if light else MUTED
    txt(d, (W // 2, 1224), caption, 17, color, anchor="mm")


def stamp(im, label, x, y, phase=1, angle=-7):
    phase = ease(phase)
    if phase <= 0:
        return
    layer = Image.new("RGBA", (330, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((6, 5, 324, 83), radius=3, outline=RED, width=5)
    txt(d, (165, 43), label, 39, RED, "display", "mm")
    scale = 1.23 - 0.23 * phase
    layer = layer.resize((round(layer.width * scale), round(layer.height * scale)), RESAMPLE)
    layer = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    layer.putalpha(layer.getchannel("A").point(lambda a: round(a * phase)))
    im.paste(layer, (int(x - layer.width / 2), int(y - layer.height / 2)), layer)


def hero(key, p, headline, name, score, case_id, caption):
    # Gentle push-in and lateral camera drift over the approved concept image.
    base = BASES[key]
    scale = 1.0 + 0.055 * ease(p)
    rw, rh = round(base.width * scale), round(base.height * scale)
    moving = base.resize((rw, rh), RESAMPLE)
    x = round((rw - W) / 2 + 12 * math.sin(p * 1.4))
    y = round((rh - H) / 2 - p * 12)
    im = moving.crop((x, y, x + W, y + H))
    shade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shade)
    for yy in range(510):
        alpha = int(75 * (1 - yy / 510))
        sd.line((0, yy, W, yy), fill=(0, 0, 0, alpha))
    im = Image.alpha_composite(im.convert("RGBA"), shade).convert("RGB")
    top_brand(im, True)
    d = ImageDraw.Draw(im)
    offset = round(20 * (1 - ease(p * 8)))
    txt(d, (46, 154 + offset), f"EXHIBIT {case_id}", 19, YELLOW, "bold")
    for index, line in enumerate(headline):
        txt(d, (43, 200 + index * 88 + offset), line, 83, CREAM, "display")
    title_y = 200 + len(headline) * 88 + 20
    txt(d, (46, title_y), name, 25, CREAM, "bold")
    rr(d, (46, title_y + 51, 286, title_y + 102), YELLOW, 7)
    txt(d, (166, title_y + 76), f"CRIME LEVEL {score}/100", 20, INK, "bold", "mm")
    # Intentional satirical stamp; food remains clearly visible below it.
    stamp(im, "CULINARY CRIME", 470, title_y + 79, clamp((p - .32) * 7))
    rr(d, (153, 1171, 567, 1209), "#292A22", 8)
    txt(d, (360, 1190), "AI-GENERATED CONCEPT IMAGE", 16, CREAM, "bold", "mm")
    footer(im, caption, True)
    return im


def screen_base(title, subtitle):
    im = Image.new("RGB", (448, 810), CREAM)
    d = ImageDraw.Draw(im)
    txt(d, (23, 18), "9:41", 15, INK, "bold")
    txt(d, (421, 18), "5G  100%", 12, INK, anchor="ra")
    txt(d, (23, 58), "FOOD FELONIES", 22, INK, "display")
    d.line((23, 94, 425, 94), fill=LINE, width=1)
    txt(d, (23, 110), title, 31, INK, "bold")
    txt(d, (23, 151), subtitle, 15, MUTED)
    return im


def nav(d, active="Create"):
    d.rectangle((0, 744, 448, 810), fill=PAPER)
    d.line((0, 744, 448, 744), fill=LINE, width=1)
    for i, name in enumerate(["Discover", "Create", "My Cases", "Profile"]):
        x = 56 + i * 112
        fill = RED if name == active else MUTED
        d.ellipse((x - 4, 758, x + 4, 766), fill=fill)
        txt(d, (x, 781), name, 13, fill, "bold" if name == active else "regular", "mm")
    rr(d, (170, 800, 278, 804), INK, 2)


def create_ui(t):
    im = screen_base("Open a new case", "3 free generations today")
    d = ImageDraw.Draw(im)
    txt(d, (23, 196), "Ingredients on hand", 20, INK, "bold")
    rr(d, (22, 231, 426, 355), PAPER, 15, LINE)
    chips = [("Gelatin", 36, 246, 128), ("Celery", 177, 246, 108),
             ("Green pepper", 36, 300, 176), ("Onion", 227, 300, 100)]
    for i, (name, x, y, width) in enumerate(chips):
        phase = ease((t - .25 - i * .32) / .28)
        if phase:
            yy = int(y + (1 - phase) * 13)
            rr(d, (x, yy, x + width, yy + 38), "#E9EDDB", 9)
            txt(d, (x + 13, yy + 8), name, 16, INK, "bold")
    txt(d, (23, 377), "Exclude ingredients", 18, INK, "bold")
    rr(d, (23, 413, 155, 451), "#F5E5DF", 8)
    txt(d, (36, 420), "Peanuts  x", 16, RED, "bold")
    txt(d, (23, 483), "Servings", 18, INK, "bold")
    rr(d, (286, 476, 425, 516), PAPER, 9, LINE)
    txt(d, (308, 494), "-", 23, INK, anchor="mm")
    txt(d, (355, 496), "2", 19, INK, "bold", "mm")
    txt(d, (403, 495), "+", 22, INK, anchor="mm")
    value = round(18 + 74 * ease((t - 2.0) / 2.15))
    txt(d, (23, 548), "Normal", 16, MUTED)
    txt(d, (424, 548), "Food Felony", 16, RED, "bold", "ra")
    rr(d, (25, 590, 423, 599), "#D9DCCD", 4)
    xx = round(25 + 398 * value / 100)
    rr(d, (25, 590, xx, 599), RED, 4)
    d.ellipse((xx - 12, 582, xx + 12, 606), fill=RED)
    rr(d, (xx - 29, 618, xx + 29, 646), INK, 6)
    txt(d, (xx, 632), str(value), 17, CREAM, "bold", "mm")
    pressed = t >= 4.75
    rr(d, (23, 675, 425, 724), INK if pressed else RED, 12)
    txt(d, (224, 699), "Opening case..." if pressed else "Generate recipe", 20, CREAM, "bold", "mm")
    if 4.6 < t < 5.2:
        pulse = clamp((t - 4.6) / .6)
        rad = int(15 + 33 * pulse)
        d.ellipse((325-rad, 698-rad, 325+rad, 698+rad), outline=YELLOW, width=3)
    nav(d)
    return im


def case_ui(t):
    im = screen_base("Vegetable Gelatin", "CASE 041  /  AI-generated recipe")
    d = ImageDraw.Draw(im)
    crop = SQUARES["gelatin"].resize((402, 292), RESAMPLE)
    im.paste(crop, (23, 190))
    txt(d, (23, 494), "AI-generated concept image", 15, MUTED)
    rr(d, (23, 531, 425, 587), YELLOW, 12)
    txt(d, (40, 548), "CRIME LEVEL", 17, INK, "bold")
    txt(d, (409, 559), "92/100", 27, INK, "bold", "rm")
    txt(d, (23, 606), "Guilty or acquitted?", 20, INK, "bold")
    chosen = t > 1.0
    rr(d, (23, 644, 217, 694), RED if chosen else PAPER, 10, RED)
    txt(d, (120, 669), "Guilty", 19, CREAM if chosen else RED, "bold", "mm")
    rr(d, (229, 644, 425, 694), PAPER, 10, LINE)
    txt(d, (327, 669), "Acquitted", 19, INK, "bold", "mm")
    if chosen:
        txt(d, (224, 721), "Verdict recorded.", 15, MUTED, anchor="mm")
    else:
        txt(d, (224, 721), "You be the judge.", 15, MUTED, anchor="mm")
    nav(d, "Discover")
    return im


def ui_scene(t, case=False):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    top_brand(im)
    heading = ["YOU BE", "THE JUDGE."] if case else ["YOUR FRIDGE.", "YOUR CRIME."]
    for i, line in enumerate(heading):
        txt(d, (43, 147 + i * 74), line, 72, INK, "display")
    caption = "GENERATE. COOK. SHOW THE EVIDENCE." if case else "PICK INGREDIENTS. TURN UP THE WEIRD."
    txt(d, (46, 308), caption, 18, MUTED, "bold")
    # A deterministic UI layer, reconstructed directly from the written brief.
    screen = case_ui(t) if case else create_ui(t)
    phx, phy = 124, 363
    rr(d, (phx + 7, phy + 12, phx + 479, phy + 850), "#C7C6B9", 43)
    rr(d, (phx, phy, phx + 472, phy + 834), INK, 42)
    mask = Image.new("L", screen.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 447, 809), radius=28, fill=255)
    im.paste(screen, (phx + 12, phy + 12), mask)
    rr(d, (phx + 174, phy + 15, phx + 298, phy + 35), INK, 10)
    footer(im, "UI RECONSTRUCTED FROM THE APP BRIEF")
    return im


def montage(t):
    im = Image.new("RGB", (W, H), INK)
    top_brand(im, True)
    d = ImageDraw.Draw(im)
    for i, line in enumerate(["MAKE IT.", "JUDGE IT.", "SHARE IT."]):
        txt(d, (46, 165 + i * 87), line, 84, CREAM if i != 2 else YELLOW, "display")
    labels = [("butter", "88", "BUTTER"), ("candle", "90", "CANDLE SALAD"),
              ("gelatin", "92", "VEGETABLE JELLY")]
    for i, (key, score, label) in enumerate(labels):
        x = 35 + 222 * i
        yy = 535 + round(25 * (1 - ease((t - i * .1) / .5)))
        rr(d, (x, yy, x + 208, yy + 454), CREAM, 16)
        pic = cover(STILLS[key], 190, 330, focus=.8)
        im.paste(pic, (x + 9, yy + 9))
        txt(d, (x + 104, yy + 367), label, 15, INK, "bold", "mm")
        txt(d, (x + 104, yy + 408), f"CRIME {score}/100", 17, RED, "bold", "mm")
    txt(d, (360, 1086), "DINNER JUST GOT INTERESTING.", 25, CREAM, "bold", "mm")
    footer(im, "AI-GENERATED FOOD CONCEPTS", True)
    return im


def end_card(t):
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    top_brand(im)
    txt(d, (46, 176), "CASE CLOSED. APP OPEN.", 22, RED, "bold")
    shift = round(18 * (1 - ease(t / .45)))
    txt(d, (39, 297 + shift), "FOOD", 158, INK, "display")
    txt(d, (39, 448 + shift), "FELONIES", 132, INK, "display")
    d.line((46, 632, 674, 632), fill=INK, width=2)
    txt(d, (46, 680), "Commit your first", 43, INK, "bold")
    txt(d, (46, 739), "food crime.", 57, RED, "bold")
    pulse = 1 + .012 * math.sin(t * 3)
    button_w = round(628 * pulse)
    bx = (W - button_w) // 2
    rr(d, (bx, 918, bx + button_w, 1011), RED, 14)
    txt(d, (360, 963), "DOWNLOAD NOW   >", 32, CREAM, "bold", "mm")
    txt(d, (360, 1080), "Make dinner questionable.", 26, MUTED, anchor="mm")
    txt(d, (360, 1224), "FOOD FELONIES", 21, INK, "display", "mm")
    return im


def frame(t):
    if t < 3.5:
        return hero("butter", t / 3.5, ["THIS SHOULD", "BE ILLEGAL."],
                    "DEEP-FRIED BUTTER", 88, "A", "Meet your next food crime.")
    if t < 6.75:
        return hero("candle", (t - 3.5) / 3.25, ["BANANA. MAYO.", "NO ALIBI."],
                    "CANDLE SALAD", 90, "B", "Yes, those ingredients are together.")
    if t < 10:
        return hero("gelatin", (t - 6.75) / 3.25, ["VEGETABLES.", "IN JELLY."],
                    "SAVORY VEGETABLE GELATIN", 92, "C", "The weirdness is entirely your choice.")
    if t < 16:
        return ui_scene(t - 10)
    if t < 20:
        return ui_scene(t - 16, True)
    if t < 22:
        return montage(t - 20)
    return end_card(t - 22)


def soundtrack():
    """Original 120 BPM bass-and-mallet cue, with custom percussive accents."""
    sr = 48000
    n = sr * DURATION
    out = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(41030)

    def add(signal, start, gain=1.0):
        a = max(0, round(start * sr))
        b = min(n, a + len(signal))
        if b > a:
            out[a:b] += signal[:b-a] * gain

    def tone(freq, duration, decay=7, kind="bass"):
        tt = np.arange(round(duration * sr)) / sr
        env = np.minimum(tt / .012, 1) * np.exp(-tt * decay)
        if kind == "mallet":
            sig = (np.sin(2*np.pi*freq*tt) + .36*np.sin(2*np.pi*2.002*freq*tt)
                   + .13*np.sin(2*np.pi*4.01*freq*tt))
        else:
            sig = (np.sin(2*np.pi*freq*tt) + .25*np.sin(2*np.pi*2*freq*tt)
                   + .08*np.sin(2*np.pi*3*freq*tt))
        return sig * env

    bass_notes = [73.416, 73.416, 110, 130.813, 73.416, 87.307, 98, 110]
    melody = [293.665, 349.228, 440, 523.251, 440, 349.228, 329.628, 293.665]
    for beat in range(50):
        start = beat * .5
        # A short final logo cadence leaves room at the tail.
        if start > 24:
            continue
        tt = np.arange(round(.22*sr))/sr
        kick = np.sin(2*np.pi*(48*tt + 45*.035*(1-np.exp(-tt/.035))))*np.exp(-tt*23)
        add(kick, start, .30)
        if beat % 2:
            ts = np.arange(round(.16*sr))/sr
            noise = rng.standard_normal(len(ts))
            noise = noise - np.concatenate(([0], noise[:-1])) * .75
            add((noise*.17 + np.sin(2*np.pi*185*ts)*.16)*np.exp(-ts*28), start, .45)
        for off in [0, .25]:
            th = np.arange(round(.065*sr))/sr
            noise = rng.standard_normal(len(th))
            noise = noise - np.concatenate(([0], noise[:-1]))
            add(noise*np.exp(-th*75), start + off, .032)
        add(tone(bass_notes[beat % 8], .43, 5), start + .02, .22)
        if beat % 4 in [0, 2, 3]:
            add(tone(melody[(beat//2) % 8], .7, 5, "mallet"), start + .25, .10)

    # Short cinematic impact at the hook and the logo.
    for start in [0, 3.5, 6.75, 20, 22]:
        tt = np.arange(round(.5*sr))/sr
        impact = np.sin(2*np.pi*(47*tt+45*.07*(1-np.exp(-tt/.07))))*np.exp(-tt*10)
        add(impact, start, .32)
    # Soft upward whooshes into UI and end card.
    for start in [9.7, 15.7, 19.7, 21.7]:
        tt = np.arange(round(.3*sr))/sr
        noise = rng.standard_normal(len(tt))
        smooth = np.convolve(noise, np.ones(7)/7, mode="same")
        add(smooth * np.sin(np.pi*tt/.3)**2, start, .16)
    # UI ingredient chips, slider confirmation, generate tap, and verdict tap.
    for start in [10.3, 10.62, 10.94, 11.26, 14.2, 14.8, 17.02]:
        add(tone(1050 if start < 14 else 730, .12, 30, "mallet"), start, .12)
    add(tone(146.832, 1.8, 2.2), 22, .14)
    add(tone(293.665, 1.8, 2.2, "mallet"), 22, .10)
    fade = np.minimum(np.arange(n)/(.03*sr), 1)
    fade *= np.minimum((n-1-np.arange(n))/(.6*sr), 1)
    out = np.tanh(out * 1.05) * fade
    out = out / max(np.max(np.abs(out)), .01) * .78
    # Small stereo ambience without placing the bass off center.
    delay = round(.011 * sr)
    right = out * .94 + np.concatenate((np.zeros(delay), out[:-delay]))*.06
    stereo = np.column_stack((out, right))
    with wave.open(str(ROOT / "soundtrack.wav"), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes((stereo*32767).astype("<i2").tobytes())


def main():
    soundtrack()
    snapshots = [.8, 4.5, 7.8, 11.9, 14.3, 17.7, 20.8, 23.4]
    contact = Image.new("RGB", (4*360, 2*680), "#D8D4C8")
    cd = ImageDraw.Draw(contact)
    for i, t in enumerate(snapshots):
        im = frame(t)
        im.save(ROOT / f"frame-{i+1:02d}.jpg", quality=93)
        contact.paste(im.resize((360, 640), RESAMPLE), ((i%4)*360, (i//4)*680))
        txt(cd, ((i%4)*360+12, (i//4)*680+648), f"{t:04.1f}s", 19)
    contact.save(ROOT / "storyboard.jpg", quality=94)
    frame(.8).resize((1080, 1920), RESAMPLE).save(ROOT / "poster.jpg", quality=95)
    ffmpeg = shutil.which("ffmpeg")
    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", f"{W}x{H}",
           "-framerate", str(FPS), "-i", "pipe:0", "-i", str(ROOT/"soundtrack.wav"),
           "-map", "0:v:0", "-map", "1:a:0", "-vf", "scale=1080:1920:flags=lanczos",
           "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-t", str(DURATION), "-movflags", "+faststart",
           str(ROOT / "food-felonies-commercial-25s-v1.mp4")]
    with (ROOT / "render.log").open("w") as log:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
        try:
            for index in range(FPS * DURATION):
                process.stdin.write(frame(index/FPS).tobytes())
                if index % 150 == 0:
                    print(f"Rendered {index//FPS:02d}/25 seconds", flush=True)
            process.stdin.close()
            code = process.wait()
        except Exception:
            process.kill()
            raise
    if code:
        raise RuntimeError((ROOT / "render.log").read_text())
    probe = subprocess.check_output([shutil.which("ffprobe"), "-v", "error", "-show_entries",
                                    "format=duration,size:stream=codec_name,codec_type,width,height,avg_frame_rate,nb_frames,duration",
                                    "-of", "json", str(ROOT/"food-felonies-commercial-25s-v1.mp4")], text=True)
    (ROOT / "verification.json").write_text(probe, encoding="utf-8")
    print(probe, flush=True)


if __name__ == "__main__":
    main()
