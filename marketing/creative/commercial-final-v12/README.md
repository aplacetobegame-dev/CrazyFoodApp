# Food Felonies — dare to cook caption

[Updated commercial](food-felonies-dare-to-cook-25s-v12.mp4)

Replaced both grin-shot captions, BAD IDEA? and PERFECT., with **Do I dare to cook this?** The word `date` in the request was interpreted as the intended `dare`.

The question uses the existing precise floating type style and appears during the grin before the ingredients. The replacement covers video frames95–143; the remainder of the v11 edit is retained, including four shared-post viewers, four cooking shots and the final gas-mask card. The AAC soundtrack is copied exactly. No image/video model generation was needed.

- `replace_caption.py`: render and verification script.
- `qa/encoded-*.jpg`: caption frames from the final encoded video.
- `qa/final-verification.json`: duration, format, decoding and audio continuity checks.

Run `python marketing/creative/commercial-final-v12/replace_caption.py` from the repository root to rebuild.
