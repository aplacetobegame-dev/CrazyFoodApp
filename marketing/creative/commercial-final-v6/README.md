# Food Felonies — guitar/drums revision

**Final reviewed file:** food-felonies-radioactive-rock-25s.mp4. Exactly 25.000 seconds; 1080 x 1920; 30 fps; H.264 and stereo 48 kHz AAC. Verification and final frames are in qa/final-verification.json and qa/final-contact-sheet.jpg. The full export decodes without errors; peak audio level is -1.5 dBFS.

Revision requested 2026-11-11. The v5 export and source footage are preserved.

## Changes

- Opening phone UI uses one fixed screen shape with a smoothed rotation, uniform scale and translation. Independent corner deformation from the old optical-flow track is removed. The same constraint is used on the sharing phone.
- Crime meter starts at zero and reaches 100/100. Following the user's additional steering, the code-native chef mascot has a radioactive green aura, asymmetric twitching eyes, a crooked buck-tooth grin, and a third eye and radiation badge at maximum crime. The phone and magnified app detail show the same state. This replaces the earlier friendly/sunglasses preview.
- New instrumental electric-guitar, bass and acoustic-drums track generated with ElevenLabs Music v2.5. Quote: 3.64 Higgsfield credits; one variation, 25 seconds, force_instrumental=true. Prompt and job ID are in music-request.json.
- All original actor/reaction vocal tracks are absent from the new mix. The cooking track contributes only its first 3.12 seconds of quiet prep, placed at 6–9.12 seconds; the exclamation around 10 seconds is excluded. Clean non-vocal interface clicks and camera shutter effects are added separately.
- Uniform camera punches, short verb captions, popping cards, ingredient chips, and verdict stamps add energy. UI layers stay rigid and readable.
- Story remains 25 seconds: meter, dish reveal, grin, ingredients, cooking, comparison sharing, reactions, community cooking, uploaded results, brand/download end card. No prompt writing or AI badges on screen.

## Source and rebuild

Run `python marketing/creative/commercial-final-v6/revise_commercial.py` from the repository root. This reuses the completed Seedance 2.5 footage, original reference images, brand fonts and wordmark from ../commercial-final-v5 and ../commercial-v2-plan. The new music is stored in audio/guitar-drums-original.mp3.

The final incremental update rebuilt the first two seconds with the user's radioactive-face steering using replace_opening(), then combined that opening with the already rendered v6 picture. The soundtrack was freshly mixed from the original music/Foley inputs. A full rebuild from the current script includes the radioactive mascot directly.

The existing archival-photo credit, generated-image provenance and font licenses in [the v5 production notes](../commercial-final-v5/README.md) continue to apply. Chef face animation and interface effects are code-native graphics in revise_commercial.py. No new video-model generations were submitted for this revision.
