# Breakfast: Final Boss

Approved final: `../../final-videos/food-felonies-breakfast-final-boss-25s.mp4`.

The 25-second commercial features an original male lead in a mustard apron, French toast with bacon ice cream (case AC-059, crime 88), and the input crime slider reaching 100. Four recipients see the post, cook the dish in four separate shots, and upload four results. The ending uses the shared gas-mask artwork.

| Seconds | Action |
| --- | --- |
| 0–2 | Crime meter to 100, six chef states, Breakfast: Final Boss title |
| 2–3.2 | Dish reveal and recipe score 88 |
| 3.2–4.7 | Lead's grin and “Do I dare to cook this?” |
| 4.7–6 | Brioche, egg mix, bacon and ice cream inventory |
| 6–11 | Dip, flip, crunch, finish and taste with combo graphics |
| 11–14 | Idea/result comparison, sharing tap and hearts |
| 14–16.4 | Four recipients discover the same post |
| 16.4–21.2 | Four separate cooking shots |
| 21.2–22 | Four result uploads |
| 22–25 | Clean mask ending and download CTA |

## Sources

`raw/` contains all four original Seedance 2.5 clips: opening (6s), cooking (6s), sharing (4s), community cooking (5s). `references/` contains native food, result, actor, ingredient-atlas and community-result artwork.

- `generation-plan.json` and `generation-completed.json`: video prompts, references, jobs and result URLs.
- `art-generation.json`, `art-prompts-extra.json`, `community-results-generation.json`: source image prompts.
- `timing.json`: measured source cuts and optional ingredient anchor overrides.
- `tracking.json`: measured phone tracks, including the corrected sharing screen.
- `../../shared/`: reusable branding, effects, music and recipient footage.
- `../../final-videos/breakfast-verification.json`: original final export verification.

## Rebuild

Run from the repository root after installing `marketing/creative/requirements.txt` and making ffmpeg/ffprobe available:

```powershell
python -B marketing/creative/projects/breakfast/render_commercial.py --preview
python -B marketing/creative/projects/breakfast/render_commercial.py
python -B marketing/creative/projects/breakfast/verify_export.py
```

Outputs go to `build/`; the selected final is never overwritten. Foley is regenerated automatically when missing. To customize its event times, use `make_foley.py --events overrides.json --output build/audio/breakfast-foley.wav`. `repair_share_track.py` rebuilds the sharing track if needed. `prepare_assets.py` can restore absent raw clips from completed job URLs and make a review sheet; the local clips are already retained.

The soundtrack uses the shared electric-guitar/drum instrumental with restrained non-vocal Foley. No generated actor or reaction audio is mixed. Source imagery represents staged commercial scenes.
