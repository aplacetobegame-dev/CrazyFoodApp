# Food Felonies — Share hearts and four reactions

Final deliverable: `food-felonies-hearts-four-reactions-25s-v8.mp4`.

## Changes

- The comparison uses equal photo tiles and matched dish framing. Both originals remain intact as source files; the video displays clean crops in lightly tilted paper photo cards with subtle shadows. Labels remain `The idea` and `The result`.
- Share depresses once at 13.35 seconds and becomes `Shared!`. Four leading hearts and a few smaller companion hearts rise from the button. Their curved motion leads into four staggered heart reveals.
- Four newly generated people appear in a 2×2 layout from 14–18 seconds. Each has a real phone and their physical dish in view, lowers their phone, shifts their gaze toward the food, then reacts. Three cast identities match the following community cooking scene; the fourth is the braided woman in a cream sweater.
- Verdict stamps appear after the gaze actions and sit away from faces. The existing community cooking is retimed to 18–20 seconds, followed by uploaded results at 20–22 seconds and the original end card at 22–25 seconds.
- The v7 opening, toxic chef progression, ingredient art, floating labels and first cooking sequence remain in the first 11 seconds. The existing guitar/drum instrumental remains. Reaction clips have no generated audio; subtle non-vocal sharing/transition Foley is mixed in.

## New generation

Four Seedance 2.5 jobs, each 4 seconds at 1080p portrait with original fictional-cast and dish references. Preflight quote: 256 credits total. All four jobs completed with no retries. Exact prompts and reference IDs are in `generation-plan.json`; job IDs and result URLs are in `generation-completed.json`. The complete set was displayed once through Higgsfield's batch-result gallery.

The original archive photo continues to represent the staged result, marked `Commercial dramatization`. Photo attribution and font licenses remain in [the v5 production notes](../commercial-final-v5/README.md). Generated mascot/ingredient prompts are in [the v7 artwork notes](../commercial-art-v7/README.md).

## Reproduction

- `prepare_assets.py` downloads the completed jobs for authorized video editing and creates raw performance review frames.
- `render_commercial.py --comparison` renders comparison samples without reaction files.
- `render_commercial.py --preview` renders the updated sequence's sample frames.
- `render_commercial.py` exports the complete 25-second picture and audio.
- `verify_export.py` fully decodes the encoded file, checks duration/resolution/frame count/sound, and creates `qa/final-contact-sheet.jpg` and `qa/final-verification.json`.

Use the repository root as the working directory. All source footage and earlier exports are preserved.
