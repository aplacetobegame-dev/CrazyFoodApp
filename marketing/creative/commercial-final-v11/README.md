# Food Felonies — see the post, then cook it

Final video: [food-felonies-discover-then-cook-25s-v11.mp4](food-felonies-discover-then-cook-25s-v11.mp4).

The corrected story shows the main cook posting her dish, four recipients seeing that same post on their phones, and then four separate full-screen cooking shots of those same people making the recipe. Their completed dishes first appear after the cooking sequence.

## Timing

| Seconds | Content |
| --- | --- |
| 0–14 | Existing main-cook sequence, comparison, Share and hearts |
| 14–16.4 | Four phone viewers, each with the same main-cook avatar and posted result |
| 16.4–17.6 | Burgundy-shirt man chopping vegetables |
| 17.6–18.8 | Blue-apron woman mixing the gelatin |
| 18.8–20 | Mustard-shirt man pouring into a ring mold |
| 20–21.2 | Braided woman unmolding her chilled version |
| 21.2–22 | Four distinct result photos uploaded |
| 22–25 | Clean final gas-mask end card from v10 |

Phone discovery reuses only the phone-reading openings from v8, reframed to remove every physical finished dish. Each attached post card contains the same main-character face, original posted dish photo and case data. The four new cooking clips preserve those people and wardrobes. Cooking is shown in separate close-ups; some generated shots crop headroom while keeping the activity and identity clear.

Four Seedance 2.5 jobs were submitted and completed, each 4 seconds at 1080p portrait, with no generated audio. Total preflight quote: 256 credits. No retries. Exact prompts and confirmed identity reference IDs are in [generation-plan.json](generation-plan.json); completed job IDs/URLs are in [generation-completed.json](generation-completed.json).

The soundtrack is copied directly from v10. All four cooking clips are silent; original unwanted reaction vocal effects remain absent. Earlier exports and source files are preserved. Existing image attribution, font licenses and commercial dramatization context remain in [v5 production notes](../commercial-final-v5/README.md).

## Files

- `references/recipient-0..3.png`: identity/kitchen crops, also used to check the discovery framing.
- `raw/cooking-0..3.mp4`: the four completed new cooking clips.
- `prepare_assets.py`: authorized source downloads and raw clip review frames.
- `render_commercial.py`: scene assembly, discovery cards, four cooking transitions, results and soundtrack copy.
- `verify_export.py`: final format/decode/audio checks and encoded review frames.
- `qa/final-contact-sheet.jpg` and `qa/final-verification.json`: final deliverable review and checks.

Run the scripts from the repository root. Use `render_commercial.py --discovery` for the four phone-viewing previews and `--preview` for the revised full sequence.
