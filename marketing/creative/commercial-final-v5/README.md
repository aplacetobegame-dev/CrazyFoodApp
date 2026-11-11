# Food Felonies — Seedance commercial production

**Final reviewed output:** `food-felonies-commercial-25s.mp4` — exactly 25.000 seconds, 1080 x 1920, 30 fps, H.264 video and stereo AAC at 48 kHz. Final verification: `qa/final-verification.json`. Net generation spend: 352 Higgsfield credits. The full export decoded without errors; AAC audio peak was -1.3 dBFS. `qa/contact-sheet.jpg` shows the assembled sequence.

Approved story: `../commercial-v2-plan/person-flow-v5.md`.

Four 1080p Seedance 2.5 clips have been submitted: opening 6 seconds, cooking 5 seconds, sharing 4 seconds, community 7 seconds. Combined footage is 22 seconds; the exact branded end card adds 3 seconds. Generation allocation: 352 credits.

The batch endpoint accepted the first two jobs and explicitly rejected the other two as out of credits despite a sufficient balance. Only those rejected items were resubmitted individually; both individual submissions were accepted. Failed connection-validation attempts returned no job IDs. The accepted job IDs are recorded in `generation-jobs.json` and the individual submission response files.

The first community generation ended with an `ip_detected` status and its 112 credits were refunded. The replacement community generation uses a fresh original fictional-cast sheet and the generated dish concept only, without the archive photo as a model reference. Its prompt and response are in `community-original-cast-submission.json`; character-reference provenance is in `community-cast-reference.md`. Total net allocation remains 352 credits.

The replacement community clip completed successfully. Its native cuts were aligned to the approved two-second reaction, three-second community-cooking, and two-second upload beats; action audio was retimed with the footage. The three staged uploaded-result images were extracted from that same completed community video, preserving each cook's distinct plate.

`compose_commercial.py` creates controlled app UI and screen composites, music and sync effects, extracts staged community result thumbnails, and exports `food-felonies-25s-seedance-v5.mp4` after all four raw clips are downloaded to `raw/scene-0.mp4` through `raw/scene-3.mp4`.

The lead's visual identity was generated with built-in image_gen and saved as `references/main-cook.png`. Its exact prompt and output provenance are recorded in `reference-generation.md`. Submitted video prompts and confirmed reference IDs are in `submission-plan.json`. No prompt typing or AI wording appears in the commercial UI; comparison labels are The idea and The result. A Commercial dramatization label identifies the staged comparison and community demonstration.

## Reference credits

The concept image was created earlier in this chat from the archival vegetable gelatin image. The staged main cooked result uses that original archive image, as requested. Both are stored in `references/`.

Archival reference: “Kitchen Chemistry savory jello” by Staff videographer, [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/), via [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Kitchen_Chemistry_savory_jello.png). The AI concept changes framing, background, lighting and presentation. Keep this source credit and applicable license terms with any reuse of the final concept edit.

App visual reference, wordmark and mascot: supplied by the user in this chat, stored in `../commercial-v2-plan/references/food-felonies-app-design.png`. Fonts are Bricolage Grotesque, DM Sans and IBM Plex Mono from Google Fonts; their OFL license files are stored with the downloaded fonts in that reference folder. Music and sync effects are original procedural synthesis in the compositor. Native Seedance action audio is retained under the music.
