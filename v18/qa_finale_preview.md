# v18 finale source-preview review

Reviewed the actual rendered `loop-0..3.jpg` at 152.960, 153.415,
153.870, 154.325 and `dive-0..3.jpg` at 154.780, 155.150, 155.800,
156.600. Also inspected `meaning_page_2.jpg`, `meaning_page_3.jpg`, and
the full-resolution 153.415 / 156.600 frames.

Verdict: **PASS for the sculpture, composition, and new ending. One small
renderer handoff correction is required before final encode: retire the old
outro witness / trail with `1 - sample_finale(t)['camera_mix']`.**

## Visual findings

- At 153.415 the infinity has a clear, large two-lobed silhouette. Its
  varying ribbon width, fine conductor lines, cross ribs, and physically
  separate crossover give it a consistent fabricated structure. It reads as
  an extension of the existing wire machine rather than a new graphic badge.
- At 153.870 and 154.325 the camera changes from viewing the complete shape
  to following a nearby curved rail. The near and far edges separate in
  depth, and the lower bend approaches the lens; this provides translation
  and parallax rather than an object rotating in place.
- At 154.780 and 155.150 the same rail passes off the sides while the iris
  becomes the destination. This is a readable continuation through the
  crossover. The red tail supports direction without creating a new screen
  scan or repeated red-bar animation.
- At 155.800 the iris grows across the frame. At 156.600 the camera is inside
  its deeper throat: curved radial conductors extend to all four screen
  boundaries and converge around the single small witness. The empty pupil
  is an intentional focal aperture, not an unpopulated scene. The ending is
  quieter and darker than the drum-driven infinity approach, but the lines
  remain legible and the depth structure occupies the whole frame.
- The final image has a useful return-to-the-eye association without adding
  a second face, text card, title, credit, or generic HUD. No added filler or
  exposure increase is necessary for this ending.

## Required handoff correction

The 153.415 render contains a large magenta ring from the **old** outro
`signal` at the crossover, while the **new** white witness is already on the
right rail. The old `draw_red_path` and `signal.draw` calls in
`draw_long_outro` currently keep their full gain even after the new camera
mix reaches 1. This creates two simultaneous witness markers and obscures
the carefully separated crossover.

Multiply both old witness gains by `1 - sample_finale(t)['camera_mix']`
(which is 1 before START because of the inactive return). Retain the old
world structures' existing slower `old_world_gain` envelope. The new rail
witness / short tail then becomes the sole focal marker from 153.2 onward,
while the machine rooms can continue their spatial handoff.

No `infinity_finale.py` production changes are requested. After this gain
correction the source-preview design is approved. These are rendered still
reviews supported by the earlier finite-geometry / camera-continuity checks;
actual encoded MP4 review remains with the final production validation.

## Final encoded resolution

The handoff correction was applied before the final master render. Actual
encoded review is now complete and **PASS**; see `qa_finale_encoded.md` and
`encoded_ending_validation.json`. The large old magenta marker is absent
from the 153.4s encoded frame. No further production corrections remain.
