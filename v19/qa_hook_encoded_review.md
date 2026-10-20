# Encoded hook and first-half visual review

Result: **PASS within the inspected scope**.

Source: finalized `output_v19/Im_Upping_My_Pdoom_Kinetic_Hook_1080p.mp4`,
1,195,362,504 bytes. All material below was decoded from that actual MP4
using FFmpeg. No renderer, OpenGL context or production source was changed.

## Complete encoded intro

Decoded all 43 native 1920 × 1080 frames at 30 fps, from 0.000 through
1.400 seconds. Inspected the full contact sheet `qa_hook_encoded_all.jpg`
and the native final intro frame `qa_hook_encoded_42.jpg`.

- 43 decoded frames, **43 different pixel hashes**.
- Minimum lit-pixel fraction, max(R,G,B) > 12/255: **0.193417**.
- Minimum mean RGB: **11.7368/255**.
- Last frame at 1.400 seconds retains **19.3417%** lit-pixel coverage.
- No black hold, empty decoded frame or static intro frame was found.
- The first capsule macro is present immediately. The four cuts follow
  the seed through its rail and induction chamber. The final frame keeps
  the dense radial/ring engraving around the iris opening, preserving the
  corrected lip approach rather than the earlier sparse last frame.

Per-frame measurements and pixel hashes are recorded locally in
`encoded_hook_validation.json`.

## First-half actual-encode samples

Inspected the first six rows (24 frames) of the actual encoded contact
sheets `qa_encoded_page_1.jpg` and `qa_encoded_page_2.jpg`: hook, sparks,
authority, dialogue, detail and training. Also extracted and inspected
native 1080p frames at **3.7, 14.6, 20.5, 28.9, 36.9, 37.9, 40.2, 73.0
and 73.8 seconds**, in addition to the final intro frame above.

- AGI retains the single detailed eye. The contour word and fine iris
  construction survive encoding without becoming an unreadable block.
- The authority gantry and jaw POV retain their near/far layering. AND,
  EAT, ME ALIVE and TRAINING are legible in the sampled fully traced views.
  Early partial CHATGPT/BOSS strokes in the contact sheet are their planned
  tracing phases; this does not assert every sample is a completed word.
- The mushroom cargo, caps and gills remain recognizable, connected to
  their carrier and consistent with the established thin-line style.
- 36.9 and 37.9 seconds visibly advance across the iris rim and adjoining
  machine structure, instead of holding a static no-word image.
- 73.0 and 73.8 seconds show two distinct, densely drawn inspection-exit
  compositions after the final RECKONED word. The ivory inspection treatment
  remains the authored treatment for this passage; it is not a blank frame.
- The reviewed fine lines and white contour lettering remain coherent in
  the compressed result. No blocking encode-specific visual issue was found.

This review covers the entire 43-frame intro and the explicitly listed
first-half samples. Full-movie decoding, original AAC verification, all
lyric visibility, FREE fracture, REPEAT/CDR and the ending are validated by
their separate checks; they are not implied by this bounded visual review.
