# Food Felonies commercial kit

The two approved 25-second videos are in `final-videos/`:

- `food-felonies-gelatin-25s.mp4` — the gelatin commercial with the final “Do I dare to cook this?” caption.
- `food-felonies-breakfast-final-boss-25s.mp4` — French toast with bacon ice cream and the new lead actor.

These are the original final exports, preserved without re-encoding. Their checksums and cleanup verification are recorded in `cleanup-manifest.json`.

## Reusable material

`shared/` contains the app design reference, licensed brand fonts, normal and toxic chef artwork, approved mask ending and native artwork, ingredient cutouts, guitar/drum music, four recipient identities and phone-reading clips, and the animation/compositing helpers. See `shared/README.md` for details. The recipient footage includes the gelatin dish below the phone-reading crop; use the documented crop for other recipes.

`food-crime-images/` contains the three original food hero images. The recipe database and its archival pictures remain in `../seed_database/`.

`projects/gelatin/` and `projects/breakfast/` contain the retained native footage, campaign artwork, generation prompts and completed job records, phone tracks, and editable render sources. Historical paths and URLs inside generation records describe the original requests; use each project's README for current local asset locations.

## Creating another commercial

Use a new folder under `projects/` for the next recipe. Reuse `shared/` for branding, mascot states, hearts, recipient phone shots, fonts, music, and ending. Create fresh food/actor references and cooking footage for the new story. Retain the clean source clips and completed generation records.

Python 3.12, the packages in `requirements.txt`, and `ffmpeg`/`ffprobe` on PATH are used by the render sources. Follow the campaign README for preview and render commands. All new previews, temporary video passes, sound mixes, and logs go into the campaign's ignored `build/` folder. Approved finals are kept separately so rendering cannot overwrite them.

Superseded exports, obsolete storyboard/review images, temporary renders, caches, and partial job-status snapshots were moved to the Windows Recycle Bin after consolidating the sources. They remain recoverable there until it is emptied. `cleanup-manifest.json` records the original inventory and the retained/removed files. Git history remains available for older tracked versions.
