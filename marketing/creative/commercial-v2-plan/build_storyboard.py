"""Local storyboard only. Does not upload media or submit generation jobs."""
from pathlib import Path
import importlib.util
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("commercial_v1", ROOT.parent / "commercial-test-v1/render_commercial.py")
v1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
W, H = 720, 1280
BG, INK, WHITE, RED, YELLOW = "#10120F", "#20231D", "#F5F0E5", "#F04B39", "#FFE36E"


def text(d, xy, value, size=28, color=WHITE, weight="regular", anchor=None):
    v1.txt(d, xy, value, size, color, weight, anchor)


def app_frame(kind):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    text(d, (42, 52), "FOOD FELONIES", 29, WHITE, "display")
    text(d, (42, 132), "EVERY RECIPE.", 75, WHITE, "display")
    text(d, (42, 217), "A CRIME SCENE.", 75, YELLOW, "display")
    d.rounded_rectangle((112, 352, 608, 1195), radius=42, fill="#2B2E27", outline="#505548", width=3)
    d.rounded_rectangle((125, 365, 595, 1182), radius=31, fill=WHITE)
    if kind == "create":
        ui = v1.create_ui(4.3).resize((448, 790), v1.RESAMPLE)
        im.paste(ui, (136, 377))
        text(d, (360, 1230), "HOW ILLEGAL SHOULD DINNER BE?", 21, WHITE, "bold", "mm")
    else:
        d.rounded_rectangle((126, 366, 594, 478), radius=29, fill=RED)
        text(d, (151, 397), "CULINARY FELONY", 25, WHITE, "display")
        text(d, (151, 439), "CASE #000041", 19, WHITE, "bold")
        text(d, (149, 501), "Vegetable Gelatin", 32, INK, "bold")
        pic = v1.SQUARES["gelatin"].resize((420, 237), v1.RESAMPLE)
        im.paste(pic, (150, 554))
        text(d, (151, 799), "AI-generated concept image", 16, "#75796D")
        for yy, title, value in [(853, "CRIME LEVEL", "92/100"), (924, "REGRET POTENTIAL", "99%")]:
            text(d, (152, yy), title, 17, INK, "bold")
            text(d, (567, yy-4), value, 30, RED, "bold", "ra")
            d.rounded_rectangle((151, yy+31, 566, yy+39), radius=4, fill="#D7DACB")
            d.rounded_rectangle((151, yy+31, 151+int(415*(.92 if yy==853 else .99)), yy+39), radius=4, fill=RED)
        text(d, (151, 991), "OFFICIAL CHARGES", 17, INK, "bold")
        text(d, (151, 1020), "Aggravated celery suspension.", 19, INK)
        d.rounded_rectangle((150, 1080, 569, 1148), radius=12, fill=RED)
        text(d, (360, 1112), "COMMIT THIS CRIME", 25, WHITE, "display", "mm")
        text(d, (360, 1230), "SATIRICAL STATS. ACTUAL RECIPES.", 21, WHITE, "bold", "mm")
    return im


def end_frame():
    im = Image.new("RGB", (W, H), RED)
    d = ImageDraw.Draw(im)
    text(d, (42, 60), "CASE CLOSED.", 30, WHITE, "display")
    text(d, (35, 230), "FOOD", 167, WHITE, "display")
    text(d, (35, 391), "FELONIES", 138, WHITE, "display")
    d.line((43, 580, 677, 580), fill=WHITE, width=3)
    text(d, (43, 650), "COMMIT YOUR", 74, WHITE, "display")
    text(d, (43, 738), "FIRST FOOD CRIME.", 65, WHITE, "display")
    d.rounded_rectangle((43, 967, 677, 1067), radius=14, fill=YELLOW)
    text(d, (360, 1016), "DOWNLOAD NOW   >", 36, INK, "bold", "mm")
    text(d, (360, 1160), "Making food worse since 2026.", 26, WHITE, anchor="mm")
    return im


SCENES = [
    {"time": "00-04s", "title": "THE BUTTER IMPACT", "key": "butter", "score": 88,
     "headline": ["THIS SHOULD", "BE ILLEGAL."], "name": "DEEP-FRIED BUTTER",
     "motion": "Crust cracks. Butter bursts. Camera punches in.", "method": "Seedance 2.5 / 4s / 1080p", "audio": "Bass hit + crisp crack + sizzle"},
    {"time": "04-08s", "title": "THE CANDLE CRIME", "key": "candle", "score": 90,
     "headline": ["BANANA. MAYO.", "NO ALIBI."], "name": "CANDLE SALAD",
     "motion": "Cherry lands. Mayo splashes. Whip-pan out.", "method": "Seedance 2.5 / 4s / 1080p", "audio": "Plop + whoosh + beat cut"},
    {"time": "08-12s", "title": "MAXIMUM JIGGLE", "key": "gelatin", "score": 92,
     "headline": ["VEGETABLES.", "IN JELLY."], "name": "SAVORY VEGETABLE GELATIN",
     "motion": "Gelatin lands and wobbles. Fast macro orbit.", "method": "Seedance 2.5 / 4s / 1080p", "audio": "Impact + exaggerated wobble"},
    {"time": "12-17s", "title": "TURN UP THE CHAOS", "key": "create",
     "motion": "Ingredient chips fly in. Slider races to 92.", "method": "Precise UI animation / reconstructed from brief", "audio": "Fast ticks + rising synth"},
    {"time": "17-21s", "title": "THE CRIMINAL RECORD", "key": "case",
     "motion": "Case file slams in. Crime + regret meters fill.", "method": "UI inspired by the shared app reference", "audio": "File slam + stamp hit"},
    {"time": "21-25s", "title": "THE DOWNLOAD PAYOFF", "key": "end",
     "motion": "Food flashes, then a bold red download card.", "method": "Motion graphics / clear 4-second call to action", "audio": "Final drop + clean logo sting"},
]


def build():
    width, panel_w, panel_h = 1440, 448, 796
    canvas = Image.new("RGB", (width, 2220), BG)
    d = ImageDraw.Draw(canvas)
    text(d, (28, 28), "FOOD FELONIES / EXPLOSIVE 25-SECOND PLAN", 41, WHITE, "display")
    text(d, (28, 85), "STORYBOARD ONLY  |  9:16  |  3 SEEDANCE SHOTS + ANIMATED APP UI", 22, YELLOW, "bold")
    text(d, (28, 123), "Existing stills show framing. The motion below is proposed, not yet generated.", 22, "#B8BCAE")
    for i, scene in enumerate(SCENES):
        x = 24 + (i%3)*472
        y = 190 + (i//3)*980
        if i < 3:
            image = v1.hero(scene["key"], .63, scene["headline"], scene["name"], scene["score"], chr(65+i), "AI-generated concept image")
        elif scene["key"] == "end":
            image = end_frame()
        else:
            image = app_frame(scene["key"])
        image.save(ROOT/f"scene-{i+1:02d}.jpg", quality=94)
        canvas.paste(image.resize((panel_w, panel_h), v1.RESAMPLE), (x,y))
        d.rectangle((x,y,x+panel_w,y+39), fill=YELLOW)
        text(d, (x+12,y+7), f"{scene['time']}  /  {scene['title']}", 21, INK, "display")
        # Short wrapped production notes sit beneath each frame.
        lines = scene["motion"].split(". ")
        for j, line in enumerate(lines):
            text(d, (x+2, y+panel_h+16+j*29), line.rstrip(".")+".", 20, WHITE, "bold")
        text(d, (x+2,y+panel_h+112), scene["audio"], 18, YELLOW)
        text(d, (x+2,y+panel_h+143), scene["method"], 15, "#A6AC9D")
    text(d, (28, 2166), "SEEDANCE PREFLIGHT: 64 CREDITS/SHOT x 3 = 192 CREDITS. NO VIDEO JOBS SUBMITTED.", 24, YELLOW, "bold")
    canvas.save(ROOT/"explosive-25s-storyboard.jpg", quality=95)
    plan = {"status":"awaiting_user_review", "duration_seconds":25, "format":"1080x1920, 9:16",
            "model":"seedance_2_5", "ai_shots":3, "seconds_per_ai_shot":4,
            "resolution":"1080p", "generate_audio":True,
            "quoted_credits_per_shot":64, "estimated_total_credits":192,
            "submitted_jobs":[], "ui_reference":"https://chatgpt.com/share/6aee6355-7448-83eb-8f8c-315972f168d5",
            "notes":"Satirical regret figure is a mock display value. Crime Levels come from seed_cases.csv. UI is reconstructed, not captured from a live app.",
            "scenes":SCENES}
    (ROOT/"generation-plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(ROOT/"explosive-25s-storyboard.jpg")


if __name__ == "__main__":
    build()
