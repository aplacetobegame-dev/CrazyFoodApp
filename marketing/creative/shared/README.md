# Shared commercial kit

This folder contains reusable Food Felonies artwork, licensed fonts, music,
recipient identities, original phone-reaction clips, and rendering helpers.
The helpers run without importing any older commercial project.

## Rendering API

Load `engine.py` using `importlib.util.spec_from_file_location` when a campaign
folder is not a Python package. It provides the existing template's `v7` API at
module level, and compatibility namespaces `engine.v5` and `engine.previous`.

- Output geometry: `W=1080`, `H=1920`, `FPS=30`, `S=1.5`; `sc`, `box`, `rr`,
  `text`, `paste`, `font`, `cover`, `new_layer`, `ease`.
- `v5`: the geometry and drawing primitives above, `brand`, `Reader`,
  `ordered_quad`, `detect_phone`, `composite_phone`,
  `precompute_phone_track`, `lower_pill`, and `uploads`.
- `brand`: palette constants, `font(size, role='body', bold=False)`, and
  `v1.cover`. Font roles are `display`, `body`, and `mono`.
- `previous`: `rigid_track(path, duration=3, segments=None)`, `pop_layer`,
  `punch`, and `v5`.
- Chef and kinetic type: `STAGES`, `crime`, `stage`, `chef`, `place_art`,
  `type_art`, `floating`, `rays`, `opening_wash`, `opening`, `leader`, `stamp`.
- Shared bitmaps: `ingredient_art(name)`, `app_design()`,
  `approved_end_card()`, and `end_card(t=0)`. Bitmap getters return cached
  artwork; copy before modifying it. `end_card` already returns a copy.
- `phone_ui('meter', t)` provides only the shared meter screen. A campaign
  supplies its own concept/result screen and food photographs.

Load `hearts.py` by path in the same way. It imports only neighboring
`engine.py`, and exposes `ENTRIES`, `ease`, `heart_points`, `heart_art`,
`draw_heart`, `hearts`, and `heart_iris`. Timing and geometry match the approved
four-recipient sequence.

Coordinates accepted by drawing helpers use the original720×1280 design space.
`brand.font` accepts pixel sizes; `text` and `type_art` scale design sizes.
`Reader.get(t)` reads forward; instantiate a new reader before seeking backward.
Close its `cap` when finished. Tracking and UI composition expect1080×1920 RGB
frames, preserving the previous templates' behavior.

Runtime dependencies: Python3, Pillow, NumPy, and OpenCV. Full campaign exports
also use an installed FFmpeg executable. These modules submit no generation
jobs and make no network requests. No campaign food photograph is opened at
import. Only the shared chef sprite atlas is opened eagerly.

## Assets and provenance

- `brand/`: approved toxic chef progression, normal identity sheet, app design
  reference, approved gas-mask ending, art-generation records, and fonts.
- `brand/fonts/`: Bricolage Grotesque, DM Sans, and IBM Plex Mono. Keep each
  family's `OFL.txt` with its font file.
- `ingredients/`: transparent onion, green pepper, gelatin, and celery artwork.
- `audio/`: the approved electric-guitar/drums track and its generation request.
- `recipients/raw/`: four original paid phone-reaction clips.

  For a different recipe, use only the opening phone-reading action, capped at
  source1.55s, and crop the1080×1920 frame to `(135,0,945,1440)` before resizing.
  The finished gelatin dish in the lower part of the original footage must stay
  outside that crop. Replace the overlaid post avatar, food photo and case score
  with the new campaign's assets.

- `recipients/references/`: the matching four identity references and original
  fictional community cast sheet.
- `recipients/*generation*.json`: original plans and completed job records for
  the recipient reactions and their gelatin cooking shots. These are provenance
  records; relative paths inside them describe the original generation runs.

Generation records may contain historical names and paths. The rendering
helpers never resolve those paths. Each campaign retains its own footage,
food references, tracking data, timing, and export verification.
