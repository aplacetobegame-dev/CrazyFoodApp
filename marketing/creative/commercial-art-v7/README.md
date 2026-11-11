# Food Felonies commercial artwork — v7 review

Generated with the built-in `image_gen` tool, then arranged into review boards with precisely typeset labels. The existing videos have not been replaced.

## Review boards

- [Six-state chef progression](chef-progression-review.png)
- [Ingredient illustrations and floating type treatment](ingredient-art-review.png)

## Source PNG artwork

- [Toxic chef sprite sheet](chef-toxic-progression.png): 3 columns × 2 rows, read left to right, then next row. States correspond to 0, 20, 40, 60, 80 and 100 on the slider. This is the current direction.
- [Normal chef expression sheet](chef-normal-expressions.png): retained as the character identity reference.
- [Gelatin](ingredient-gelatin.png)
- [Celery](ingredient-celery.png)
- [Green pepper](ingredient-green-pepper.png)
- [Onion](ingredient-onion.png)

All source PNGs contain alpha transparency. Preserve alpha when importing. The final chef sheet is 1536 × 1024; the ingredient cutouts are each 1254 × 1254. Source artwork is unchanged by the review-layout script.

## Direction for animation

Keep the same chef and hat throughout. Escalate from curious, to mischievous with goggles, to a fitted gas mask, to increasing vapor, illuminated lenses, and maximum food-felony chaos. Transition between source states with short controlled reveals and pose movement; retain the physical phone's stable shape.

Place ingredient names near the matching real ingredients: onion upper-left, green pepper upper-center, gelatin upper-right, celery lower-middle. Keep hands and knife visible. Use typed text for exact spelling. Illustrated cutouts should support the live-action food rather than replace it.

Continue the existing 25-second narrative and guitar/drums soundtrack when the visual direction is accepted. No new video generation was submitted for this artwork review.

## Reproduction and checks

- [Exact generation prompts and source mapping](generation-manifest.json)
- [Alpha and visual review report](verification.json)
- [Review-layout renderer](build_review.py)

Run `python marketing/creative/commercial-art-v7/build_review.py` from the repository root to rebuild the two review boards.
