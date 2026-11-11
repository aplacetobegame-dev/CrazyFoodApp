# Food Felonies — toxic chef commercial v7

Final video: `food-felonies-toxic-chef-25s-v7.mp4`.

25 seconds, portrait 1080 × 1920, 30 fps, H.264 with stereo 48 kHz AAC.

## Updated creative

- Six generated chef states escalate with the opening crime slider: curious, mischievous with goggles, fitted gas mask, toxic vapor, illuminated lenses, maximum chaos. The same state appears on the physical phone and in the enlarged detail. Sprite changes use controlled pose movement rather than facial warping.
- Opening phone tracking preserves one fixed screen shape with smoothed translation, rotation and uniform scale. No independent corner bending.
- Floating outlined type replaces caption bars. `BAD IDEA?` becomes `PERFECT.` beside the cook's grin. `CHOP.`, `MIX.`, `POUR.` and `JIGGLE.` appear near the action.
- `ONION`, `GREEN PEPPER`, `GELATIN`, and `CELERY` have matching illustrated cutouts and leaders placed beside the actual ingredients. Small optical-flow movements keep those callouts attached to the scene. The celery endpoint was adjusted to the exposed stalk after visual QA.
- The nine-person reaction grid builds tile by tile, followed by verdict stamps, three people cooking the same dish, and their uploaded results.
- Electric guitar, bass and drums use the existing ElevenLabs Music v2.5 instrumental. The original repeated actor/reaction vocal tracks are excluded. Only quiet kitchen audio from source scene 1 at 0–3.12 seconds is included, placed at 6–9.12 seconds in the edit, with clean non-vocal interface and shutter Foley.

## Timeline

| Seconds | Content |
| --- | --- |
| 0–2 | Crime slider to 100 and escalating toxic chef |
| 2–3.15 | Vegetable gelatin concept dish |
| 3.15–4.8 | Cook's grin, BAD IDEA? / PERFECT. |
| 4.8–6 | Positional ingredient callouts |
| 6–11 | Cooking and finished gelatin reveal |
| 11–15 | The idea beside the staged original-photo result, then share |
| 15–17 | Nine reactions and verdict stamps |
| 17–20 | Three community members cooking the same recipe |
| 20–22 | Their separate results uploaded |
| 22–25 | Food Felonies wordmark and download call to action |

The reference/archive result remains marked as a commercial dramatization. No prompt typing or AI labels are on screen.

## Source and validation

The footage is the completed Seedance 2.5 source from [v5](../commercial-final-v5/README.md). This revision does not submit new video generation jobs. It recomposites the new [generated art](../commercial-art-v7/README.md), precise typography, phone UI and transitions over those clips. Existing music is from [v6](../commercial-final-v6/README.md). Font licenses, original-photo attribution and generated-image provenance remain with those source folders.

- `render_commercial.py`: main renderer, previews, audio mix and optional ingredient-shot repair.
- `verify_export.py`: checks the final encoded video, fully decodes it and extracts final review frames.
- `qa/final-contact-sheet.jpg`: frames from the encoded deliverable.
- `qa/final-verification.json`: duration, resolution, frame count, sound and decode checks.
- `delivery.json`: local deliverable paths.

From the repository root, run `python marketing/creative/commercial-final-v7/render_commercial.py`, followed by `python marketing/creative/commercial-final-v7/verify_export.py`.
