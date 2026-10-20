# Hook and first-half preview review

Result: **PASS for the reviewed preview scope**. This is an inspection of
rendered 1920 × 1080 RGB frames, before final MP4 encoding.

Executed `python v19/render.py --meaning-preview` twice. The second run
contains the refined opening macro. Inspected the first six storyboard
rows (24 frames: hook, sparks, authority, dialogue, detail and training)
in `meaning_page_1.jpg` and `meaning_page_2.jpg`. Additionally inspected
nine native-resolution frames: `hook-0.jpg`, `hook-2.jpg`, `sparks-2.jpg`,
`authority-2.jpg`, `dialogue-2.jpg`, `detail-0.jpg`, `detail-2.jpg`,
`detail-3.jpg` and `training-1.jpg`.

## Observations

- Frame zero already shows a charged capsule, curved carrier rail and
  induction machinery. There is no black hold or title before the vocal.
  Four views share the same moving seed and its real rail. The capsule's
  initial size was increased after the first review and its shell received
  fine turned seams and captive sockets; the revised first frame has a
  stronger foreground subject. Hook geometry totals 17,200 line vertices
  and no triangle faces, in eight bounded batches.
- Cold-open cuts at 0.24, 0.69 and 1.14 seconds follow measured source-audio
  onset peaks near 0.239, 0.688 and 1.137 seconds. The stronger 0.918-second
  energy peak falls during coil ignition. First sung word remains 1.42.
- The opening AGI/sparks passage retains one eye. Close angles show its
  fine iris loops and physical internal structure; no second eyeball or
  disconnected symbol has been added.
- Circuit/authority frames have near-edge supports and connected physical
  detail. The control gantry remains the dominant fabrication rather than
  a collection of floating icons. The jaw POV fills the edges and the
  sampled EAT and ME ALIVE contours remain clear against the inner space.
- Mushrooms remain attached to their cargo/exit mechanism. The sampled
  OF frame is readable and the object is recognizable as mushrooms.
- Training uses a different overhead composition and stepped deck. The
  word outline remains legible. Optimization and atom reassembly have
  direction and physical depth instead of an empty central tunnel.
- The 36.9- and 37.9-second no-word shots visibly move across the existing
  iris rim. Measured eye displacement after removing shared world travel
  is approximately **−3.057 X, −1.734 Y, −1.691 Z units** across those two
  samples, confirming real XYZ movement rather than a fixed-camera spin.
  The word-free inspection exit is scheduled only after RECKONED ends at
  72.90 seconds, with continuing movement to 73.87.

Partial glyph outlines in early tracing samples (for example CHATGPT at
17.1 seconds and BOSS at 15.6) are intentional tracing phases. Fully
drawn lexical readability is checked separately by the full 225-word
spatial audit; this visual review does not substitute for that audit or
for encoded-video validation.

No blocking visual issue remains in the reviewed frames. FREE fracture,
REPEAT/CDR and the final infinity sequence are outside this review's scope.

## Complete 43-frame cold-open check

Rendered every actual 30 fps intro frame, from 0.000 through 1.400 seconds,
and inspected their contact sheet `qa_hook_all_frames.jpg` plus the final
native 1080p frame `hook-tail-42.jpg`. All 43 frame hashes are different.
The initial last-frame review found the lens had moved past the front iris
and left too few bright edges around the pupil. Its endpoint was pulled
back to the physical iris lip at Z = −24.0, retaining the fast approach and
the match cut into the sung eye. The full 43-frame check was repeated after
that correction.

Final minimum lit-pixel fraction, using max(R,G,B) > 12/255, is **0.167909**;
minimum mean RGB is **12.0191/255**. No blank frame or static hold is present.
The last frame retains etched rings and radial detail across the image;
its central dark pupil is part of the iris composition. Source is now fixed
for the full-movie render.
