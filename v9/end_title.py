"""Stroke geometry layout for the v9 final title tableau.

All positions are in the existing epilogue's world coordinates.  The final
camera is (0, 1, 35), aimed at the origin at a 58 degree vertical field of
view.  Build the lettering with ``textmesh`` so its contours, back edges and
connecting strokes have real depth; no bitmap title or flat caption layer.

The caller must retain the existing *whole framebuffer* freeze at 154.6 s.
Clamping this layout alone is insufficient to freeze the background.
"""

TITLE = "I'm Upping My P(doom)"
CREDIT = "Made by Chiyang001"
FREEZE_TIME = 154.6


def _ease(x):
    x = min(1.0, max(0.0, float(x)))
    return x * x * (3.0 - 2.0 * x)


def end_title_layout(t):
    """Return a renderer independent layout with fully settled final bounds.

    ``size`` is the actual em size passed to ``textmesh``.  ``scale`` is used
    only for the existing infinity mesh.  Rotation is XYZ in radians.  The
    small title pitch preserves its engraved depth without compromising
    the title's normal left to right reading order.
    """
    t = min(FREEZE_TIME, float(t))
    title_reveal = _ease((t - 153.415) / 0.685)
    credit_reveal = _ease((t - 154.05) / 0.40)
    infinity_reveal = _ease((t - 152.05) / 1.365)
    return {
        "active": t >= 152.05,
        "freeze_time": FREEZE_TIME,
        "title": {
            "text": TITLE,
            "size": 3.15,
            "position": (0.0, -5.35, 1.0),
            "rotation": (-0.018, 0.0, 0.0),
            "depth": 0.42,
            "reveal": title_reveal,
            "gain": 1.35,
            "color": (0.89, 0.95, 1.0),
        },
        "credit": {
            "text": CREDIT,
            "size": 1.35,
            "position": (0.0, -8.65, 2.0),
            "rotation": (0.0, 0.0, 0.0),
            "depth": 0.24,
            "reveal": credit_reveal,
            "gain": 1.15,
            "color": (0.89, 0.95, 1.0),
        },
        "infinity": {
            "position": (0.0, 3.0, -1.0),
            "rotation": (0.0, 0.0, 0.0),
            "scale": 1.50,
            "reveal": infinity_reveal,
            "gain": 1.05,
        },
        # The title already contains P(doom). The old formula would compete
        # with it and should be replaced rather than stacked as a fourth row.
        "formula": {"text": "P(doom) = \u221e", "gain": 0.0, "reveal": 0.0},
        "maker_rail": {
            "position": (0.0, -9.30, -7.0),
            "scale": (0.55, 0.035, 0.12),
            "gain": 0.18 * credit_reveal,
        },
        "bounds_target_ndc": {
            "title": (-0.56, -0.30, 0.56, -0.13),
            "credit": (-0.25, -0.49, 0.25, -0.36),
            "infinity": (-0.49, -0.13, 0.49, 0.46),
        },
    }


if __name__ == "__main__":
    frame = end_title_layout(FREEZE_TIME)
    assert frame["title"]["text"] == "I'm Upping My P(doom)"
    assert frame["credit"]["text"] == "Made by Chiyang001"
    assert frame["title"]["reveal"] == frame["credit"]["reveal"] == 1.0
    assert frame == end_title_layout(156.667)
    print("Final tableau: full title, maker signature, settled by 154.6 s")
