# Food Felonies — clean regenerated ending

Final video: [food-felonies-clean-ending-25s-v9.mp4](food-felonies-clean-ending-25s-v9.mp4).

The new end card replaces seconds22–25. It has a polished normal chef character, a sharp Food Felonies wordmark, the clean three-line recipe/cook/evidence tagline, and one red download button. The CASE CLOSED. APP OPEN. line, old low-resolution chef, mismatched paper rectangles, stray marks, CTA rays and extra bottom slogan are removed.

- [Regenerated original artwork](end-card-generated.png)
- [1080×1920 end frame](end-frame-1080x1920.png)
- [Exact prompt and reference provenance](end-card-generation.json)
- [Final verification](qa/final-verification.json)

Artwork was regenerated with the built-in `image_gen` tool using the old end frame as the replacement target and the previously generated normal chef sheet as the character reference. The generated file is preserved unchanged. Video scaling fits it to1080×1920 for the final 3-second clean hold.

The first22 seconds retain the v8 edit, including comparison, hearts and four reaction shots. The AAC audio stream is copied directly and its SHA-256 matches v8 exactly. Final export is25.000 seconds,750 frames at30fps,1080×1920, with no decode errors. Earlier exports are preserved. No additional video-model generation jobs were submitted.

Rebuild from the repository root with `python marketing/creative/commercial-final-v9/replace_end_card.py`.
