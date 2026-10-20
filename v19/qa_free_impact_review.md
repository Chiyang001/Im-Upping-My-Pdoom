# FREE: repeated blows and total fracture

The production module replaces the former single opening/rebound with six
escalating blows followed by one complete failure. All seven attacks use
measured kick events: 56.380, 56.615, 56.840, 57.070, 57.295, 57.525 and
57.745 seconds. The contact changes location, each hit compresses and rebounds
the steel, and permanent dents accumulate before the final kick.

The cage, its rear and side supports, horizontal frame members, bearings,
lock crossbars and bars share a single source geometry. At the last blow that
entire geometry separates into 366 rigid mechanical cells, with source-based
positions, individual rotation, XYZ momentum and gravity. No intact cage
frame or opening-panel fallback is rendered afterwards. The cells remain
recognizable rod sections, sleeve rings and lock pieces rather than particles.

`python v19/qa_free_impact.py` passes:

- Seven strikes match measured kicks; each produces its own physical camera
  recoil and pressure impulse.
- Permanent deformation increases across all six preliminary blows.
- All 29,850 line vertices are procedural, with zero triangle vertices.
- No fragment spans more than 2.64 units along any axis.
- All 366 cells move at least 3.23 units away from their source by 58.05 s.
- Rigid-cell lengths are preserved and breakup starts continuously, with
  under 0.00002 units of discontinuity.
- 401 dense samples contain finite geometry and camera/target values.
- The complete intact/debris assembly takes one GPU draw per frame.

The final integrated fifteen-frame, full-HD preview has been visually reviewed. Successive
hits show local steel compression with a return between impacts. At 57.82 s,
the original large cage is replaced by individual rings and metal sections;
the fragments disperse across depth and leave an open route through the cage.
The ME FREE outlines remain clear during breakup and camera advance.
Native 1080p frames at 56.86, 57.765 and 57.82 s were checked in addition to the
contact sheet. Bright white clipping peaks at 0.819 percent of pixels in
each sampled frame; the detailed rods do not become a solid white plane.

The final preview includes the camera integration, enabling `camera_local`
throughout 56.20–58.43 s and resetting the post pressure-wave age with
`contact_age` on each new hit. It also includes the increased physical dent
strength. The first six hits visibly deform the steel and trigger distinct
translational recoils before the final all-cell breakup. The short chromatic
peak at 57.765 s preserves the FREE outline, followed by visible fragments
across the frame at 57.82 s. The cage clears as the camera advances through it.

Status: source-level checks and integrated visual preview PASS. The completed
MP4 has also passed the separate [actual encoded FREE review](qa_free_encoded_review.md),
covering 24 decoded frames, three contact pages and three native 1080p views.
