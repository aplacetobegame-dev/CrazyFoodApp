# Food Felonies — 25-second commercial test

Created 2026-11-10. This is a concept edit for review, assuming the app is live.

## Deliverable

- `food-felonies-commercial-25s-v1.mp4`
- Exactly 25.000 seconds; 750 frames; 1080 x 1920; 30 fps.
- H.264 video, AAC stereo sound, MP4 fast-start playback.
- Music and sound effects; no spoken narration.
- `poster.jpg` and `storyboard.jpg` provide a poster frame and a contact sheet.

## What was generated

The three food images were generated earlier in this chat with built-in image_gen. This test animates those stills with camera moves and composites deterministic UI animations reconstructed from `docs/mockup/FOOD_FELONIES_MOCKUP.md`.

No AI video or audio jobs were submitted. Higgsfield returned `UNAUTHORIZED` / “This app connection requires reauthentication” before generation. The same error persisted after the user reported reconnecting and on a later verification attempt. This MP4 is an image-and-UI motion graphics test, not an AI-generated live-action video. It does not depict real cooked user submissions. The UI is a reconstruction, not a recording of a shipped app.

The soundtrack and UI/transition effects are original procedural synthesis in `render_commercial.py`.

## Timeline

| Time | Content |
| --- | --- |
| 0.00–3.50 | Deep-fried butter, Crime Level 88/100. “This should be illegal.” |
| 3.50–6.75 | Candle salad, Crime Level 90/100. “Banana. Mayo. No alibi.” |
| 6.75–10.00 | Savory vegetable gelatin, Crime Level 92/100. “Vegetables. In jelly.” |
| 10.00–16.00 | Ingredient chips appear, weirdness slider moves from 18 to 92, Generate is tapped. |
| 16.00–20.00 | Generated concept case file, Crime Level, Guilty/Acquitted interaction. |
| 20.00–22.00 | Three-food montage. “Make it. Judge it. Share it.” |
| 22.00–25.00 | Wordmark and “Commit your first food crime. Download now.” |

## Source credits

Food images are AI reconstructions with new framing, plating, backgrounds and lighting, based on the following archive references. Source records and crime levels come from `marketing/seed_database/seed_cases.csv`.

- Deep-fried butter reference: “Deep-fried butter at State Fair of Texas 2009a” by Collin Harvey from Grand Prairie, Texas, USA, [CC BY 2.0](https://creativecommons.org/licenses/by/2.0/), via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Deep-fried_butter_at_State_Fair_of_Texas_2009a.jpg).
- Candle salad reference: “Candle salads” by Judielaine, public domain, via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Candle_salads.jpg).
- Vegetable gelatin reference: “Kitchen Chemistry savory jello” by Staff videographer, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Kitchen_Chemistry_savory_jello.png).

Reuse this concept edit and its source-derived imagery with these source credits and the relevant source license terms, including the gelatin reference's share-alike terms. Prompt provenance for the two later images is in `../food-crime-images/generation-notes.md`.

## Rebuild and verification

Run `python marketing/creative/commercial-test-v1/render_commercial.py` from the repository root. Requires the installed Python packages Pillow and NumPy, FFmpeg/FFprobe on PATH, and Windows Segoe UI / Arial Narrow fonts.

The renderer preserves source stills, creates editable animated UI and soundtrack, and exports the MP4. `verification.json` records FFprobe output. The final file was decoded end-to-end by FFmpeg without errors; both audio and video streams are exactly 25 seconds. Audio peak after AAC encoding: -2.7 dBFS; mean level: -20.0 dBFS. Layout was visually reviewed in `storyboard.jpg`.
