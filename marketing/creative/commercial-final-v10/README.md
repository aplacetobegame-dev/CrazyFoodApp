# Food Felonies — final gas-mask end card

[Updated25-second commercial](food-felonies-mask-ending-25s-v10.mp4)

The end-card chef is replaced with the last toxic mask state from the crime slider: tilted white hat, glowing green eye lenses, two green filter canisters, red scarf, lime vapor and the small impact accents beside the head. Branding, tagline and the clean download button are retained. CASE CLOSED and the old button marks remain absent.

- [Edited end-card artwork](end-card-generated.png)
- [1080×1920 end frame](end-frame-1080x1920.png)
- [Exact built-in image_gen edit prompt](end-card-generation.json)
- [Verification report](qa/final-verification.json)

The end image was edited with built-in `image_gen`, using v9 as the edit target and the bottom-right/100 state from `commercial-art-v7/chef-toxic-progression.png` as the replacement reference. Seconds22–25 are replaced; the earlier edit and original AAC soundtrack are retained. Verified25.000 seconds,750frames,1080×1920,30fps, no decode errors, and matching audio SHA-256. No new video-model jobs were submitted.

Rebuild with `python marketing/creative/commercial-final-v10/replace_end_card.py` from the repository root.
