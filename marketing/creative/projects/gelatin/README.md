# Vegetable gelatin commercial

The selected delivery is `../../final-videos/food-felonies-gelatin-25s.mp4`. It is preserved from the approved final export. This project keeps the original footage, identity references, tracking, generation prompts and a standalone editable renderer.

From this directory, run:

```powershell
python render_commercial.py --preview
python render_commercial.py
```

Requirements: Python 3, Pillow, NumPy, OpenCV, and FFmpeg on PATH. Outputs go into `build/`; rendering never overwrites the selected delivery. Build files and Python caches can be removed at any time.

The renderer uses `../../shared/` for fonts, toxic chef states, ingredient cutouts, phone tracking helpers, hearts, four recipient clips and the approved gas-mask end card. `raw/scene-0..2.mp4` are the lead's introduction, cooking and sharing shots. `raw/cooking-0..3.mp4` are the four separate community cooking shots. `references/` contains the lead identity and the avatar frame actually used in the shared-post cards.

The concept image is the existing canonical `../../food-crime-images/AC-041-vegetable-gelatin-v1.png`. The result image is the existing canonical `../../../seed_database/archive_images/AC-041_savory-gelatin-mold-with-suspended-vegetables.png`. Both are exact matches for the source images in the approved commercial; no extra copies are needed here.

The approved delivery supplies its exact AAC soundtrack during a rebuild. The editable shared guitar/drum music source is also retained in `../../shared/audio/`. A rebuilt video will be freshly encoded; the preserved delivery remains the original approved file.

Flow: crime slider and toxic chef states, dish reveal, “Do I dare to cook this?”, ingredient labels, cooking, idea/result comparison, Share hearts, four recipients reading the same post, four separate cooking shots, four uploads, clean gas-mask ending. `final-verification.json` records the checks on the original approved export. `provenance/` keeps the original provider generation records; historical paths inside those records are documentary, not renderer dependencies.
