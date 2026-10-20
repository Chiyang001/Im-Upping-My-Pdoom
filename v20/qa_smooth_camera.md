# v20 smooth camera audit

Baseline: original v20 commit `7bab5f9`. The baseline source was read directly from Git into memory in an isolated process; no historical version directory was created.

The final production camera was sampled 1 ms before and after 75 ordinary word-group boundaries **within the same lyric line**. Every lyric-line start/end is excluded uniformly and recorded separately in the JSON report. Original shot cuts and deliberate flight, FREE, Moon, Repeat, CDR, Transformer, upgrade and ending rigs were also excluded. Common world travel was subtracted.

| Pose change across 2 ms | Original median | Smooth median | Original maximum | Smooth maximum |
| --- | ---: | ---: | ---: | ---: |
| eye | 3.483419 | 0.004092 | 5.645914 | 0.014113 |
| direction_degrees | 6.297540 | 0.006805 | 19.879947 | 0.023075 |
| bank_degrees | 2.579151 | 0.001329 | 5.585961 | 0.047215 |
| lens_degrees | 2.178882 | 0.002266 | 12.970538 | 0.096878 |

- Original lexical camera cues: 147.
- Candidate calls to phrase_camera / pair_camera: {'phrase_camera': 0, 'pair_camera': 0}.
- Ordinary hit=0 versus hit=1 checks: 87; camera poses and projections equal: True.
- Retained deliberate camera intervals: 11; all retain measured local movement: True.
- Residual same-line boundary flags: 0.
- Numerical result for this limited scope: **PASS**.

Original line/scene transitions remain intentional. For example, Without begins at 84.720 s while its authored shot cut occurs at 84.780 s; its inherited lens transition is retained. This audit does not claim that the entire movie has no cuts or pose jumps. It checks removal of repeated word-group camera resets and ordinary beat shake. Detailed samples, including every lyric-line transition, are in the generated qa_smooth_camera.json report.

The finalized smooth-v20 MP4 was separately decoded for 32 opening stills, including five native 1920x1080 images, plus two supplemental native BAG checkpoints at 28.400 and 28.500 s. Both contact-sheet pages were inspected: the original hook, single eye, circuits, loss, authority, dialogue and mushroom scenes remain. BAG is clearly readable in both supplemental frames before passing the camera. Contact sheets cannot prove temporal smoothness; the measured camera test above supplies the complementary motion check.
