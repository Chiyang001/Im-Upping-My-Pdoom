# v20 upgrade sequence: encoded-frame review

**PASS for the inspected samples.** This review reads the delivered H.264 MP4,
not a render preview or a geometry mockup. No production source was changed
during the review.

Movie: `output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4`
(1,210,355,128 bytes).

## Scope

`python v20/qa_upgrade_preview.py --encoded
"output_v20/Im_Upping_My_Pdoom_Semantic_Thrust_1080p.mp4"` extracted 25
1920×1080 frames spanning 127.80–132.40 seconds. All three contact pages were
visually inspected. Native-size encoded frames at **128.470, 129.420, 130.360
and 132.200 seconds** were also inspected.

One additional native frame was decoded at **128.000 seconds** to check the
FROM entrance after the old transition effects and story-machine skeleton
were disabled. Thus this review covers 26 distinct decoded images, including
five native-size focus checks; it does not constitute frame-by-frame viewing
of the complete song or a verdict on the whole movie's aesthetic quality.

Local outputs are `qa_upgrade_encoded.json`,
`qa_upgrade_encoded_page_1.jpg`–`qa_upgrade_encoded_page_3.jpg`, the 25
timestamped JPEGs and the additional `qa_upgrade_encoded_128.000.jpg`.
They are generated review evidence, not production assets.

## Observations

- **FROM, 128.000:** the outlined word is clear on its physical mounting
  plane. The archive floor and side supports have sharp lines. The earlier
  inherited radial transition blur is absent, and no black legacy machine
  skeleton cuts across the word or the conveyor.
- **Masked, 128.470:** the opened slats, archive feed and common housing
  remain visible behind the physical FROM MASKED plate. The framing is
  closer than in the first preview; the word and apparatus fit together.
- **Pre-training / days, 129.420:** the comb, sample route and indexing chain
  occupy separate depth layers. The actual encoded word contours remain
  clear against those layers. Compared with the adjacent contact samples,
  the rail and machine sides change perspective with the translating camera.
- **Recursive, 130.360:** archive leaves recede toward the fabrication front,
  while the extractor and print arms occupy the near side. The word stays
  on its machine plane, without a camera-relative row of detached symbols.
- **Self-upgrade, 130.760–131.360:** sampled frames show the word's approach
  and the stronger original forward flight. The successor structures and
  impact lines lead into the existing one-way word pass. The former central
  concentric-ring / small-robot presentation is absent from the rebuilt
  archive/training/fabrication section. A brief impact ripple at the word
  flight is a separate retained transition effect.
- **Exit, 132.200:** the camera has passed WHAT, and foreground successor
  wings, bridge trusses and rails remain visible across the frame. This
  resolves the first preview's nearly empty exit. The next sampled DID frame
  at 132.400 restores the next physical lyric without a black hold.

There was no blocking issue in these decoded samples. Full-file decoding,
original AAC bitstream comparison, all 356 event windows, ending checks and
the 225-word spatial regression are separate checks owned by the main
validation process. This document does not claim their results.
