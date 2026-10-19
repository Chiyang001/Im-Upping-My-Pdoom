"""A single continuous dolly through the ten chapters of the machine.

The renderer scrolls the world by ``travel``.  ``eye`` and ``target`` are
*local* coordinates, so the lens can stay near the lyric architecture while
foreground rails, rooms and structures pass it.  No lyric index or word timing
is used here: a sentence cannot reset the camera or make it snap to its centre.

All channels use a non-uniform cubic Hermite spline with shared derivatives.
Thus every edit, including the chapter boundaries, is C1 continuous.  The
forward distance uses a monotone Hermite spline; no backwards world travel is
possible.  FOV is in degrees and roll is in radians.
"""

from bisect import bisect_right

DURATION = 156.667
CHAPTERS = (
    (0.0, "awakening machine"),
    (22.0, "language city"),
    (38.0, "stable plane to singularity"),
    (58.0, "basilisk ascent"),
    (74.0, "feedback and escape"),
    (94.0, "paperclip factory"),
    (109.0, "safety fences fall"),
    (124.0, "recursive loom"),
    (131.0, "theatre seen from its wings"),
    (141.0, "the machine swallows its world"),
)

# time, eye xyz, target xyz, roll, fov
# The lens moves through streets and under apparatus rather than orbiting a
# central object.  Large semantic changes are carried by the world procession;
# the local composition can therefore remain readable without camera lock-on.
_PATH = (
    (0.0,       2.8,  1.6, 28.0,   -0.8,  0.2, -5.0,  -0.018, 58.0),
    (5.5,       0.8,  0.8, 26.5,    0.2, -0.1, -5.6,   0.006, 57.0),
    (11.0,     -2.3,  1.3, 25.0,    0.4,  0.3, -6.0,   0.023, 58.5),
    (16.5,     -4.3, -0.1, 24.0,   -0.5, -0.4, -5.0,   0.014, 60.0),
    (22.0,     -2.6, -1.0, 25.0,    0.7, -0.1, -5.7,  -0.018, 61.0),
    # Slalom through the language city: low street, shoulder, elevated exit.
    (26.0,      1.4, -1.5, 23.3,    1.3, -0.5, -6.2,  -0.041, 63.0),
    (30.0,      4.8, -0.2, 24.8,   -0.3,  0.3, -6.5,  -0.025, 61.0),
    (34.0,      3.2,  1.7, 27.0,   -0.8,  0.7, -6.8,   0.009, 59.0),
    (38.0,      0.3,  2.1, 28.3,    0.3,  0.5, -6.6,   0.024, 58.0),
    # A quiet high survey becomes a long descent into the singularity.
    (43.0,     -1.5,  1.5, 27.0,    0.5,  0.1, -7.0,   0.015, 58.5),
    (48.0,     -2.8, -0.4, 23.3,    0.1, -0.6, -6.2,  -0.021, 62.0),
    (53.0,     -1.8, -2.5, 22.2,    0.8, -0.9, -5.5,  -0.043, 64.0),
    (58.0,      1.6, -1.6, 25.2,    1.0, -0.4, -6.0,  -0.022, 60.5),
    # The basilisk is climbed on one side, then crossed over at its crown.
    (62.0,      4.7,  0.3, 24.7,    0.8,  0.2, -6.8,   0.018, 62.0),
    (66.0,      4.0,  2.6, 23.4,   -0.4,  0.6, -6.5,   0.051, 63.0),
    (70.0,      0.3,  3.3, 25.3,   -1.1,  0.5, -6.8,   0.038, 61.0),
    (74.0,     -3.8,  1.4, 27.5,   -0.9, -0.2, -7.0,   0.007, 59.0),
    # Reverse-flow feedback lane, followed by a single decisive lateral turn.
    (78.0,     -4.6, -0.5, 26.5,   -0.3, -0.6, -6.7,  -0.026, 60.0),
    (81.0,     -2.2, -1.6, 24.6,    0.9, -0.6, -6.0,  -0.046, 62.0),
    (83.5,      2.8, -0.9, 23.5,    1.5,  0.2, -5.5,  -0.047, 64.0),
    (87.0,      5.2,  0.8, 25.5,    0.0,  0.6, -6.4,  -0.010, 61.0),
    (91.0,      3.7,  2.1, 27.6,   -1.0,  0.5, -7.0,   0.026, 59.0),
    (94.0,      1.5,  1.7, 27.2,   -0.8,  0.0, -7.0,   0.019, 60.0),
    # Factory tracking shot: travel along one conveyor, dip underneath it,
    # emerge on the far side.  This is deliberately not another central orbit.
    (98.0,      0.0,  0.2, 25.5,   -0.1, -0.3, -6.5,  -0.010, 61.5),
    (102.0,    -1.0, -2.1, 22.5,    0.7, -0.8, -5.5,  -0.036, 64.0),
    (106.0,    -3.6, -1.4, 24.2,    0.5, -0.2, -6.5,  -0.020, 62.5),
    (109.0,    -4.5,  0.2, 26.5,   -0.6,  0.3, -7.0,   0.017, 60.5),
    # Climb over the first fence, then plunge through the breached last fence.
    (113.0,    -2.2,  2.5, 27.8,   -0.9,  0.6, -7.4,   0.043, 60.0),
    (117.0,     1.7,  2.0, 25.7,    0.0,  0.2, -6.8,   0.024, 61.5),
    (121.0,     4.0, -0.2, 23.2,    0.9, -0.5, -6.0,  -0.025, 64.0),
    (124.0,     2.6, -2.2, 24.8,    0.8, -0.8, -6.0,  -0.049, 62.0),
    # One over-under weave of the loom, without resetting its velocity.
    (127.5,    -0.9, -1.5, 24.0,   -0.4, -0.2, -6.6,  -0.025, 63.0),
    (131.0,    -3.7,  0.5, 26.4,   -0.7,  0.4, -7.0,   0.021, 60.5),
    # The stage is seen from a moving wing, never an abrupt front-on tableau.
    (136.0,    -2.5,  1.9, 28.3,    0.1,  0.6, -7.2,   0.024, 59.0),
    (141.0,     0.8,  1.1, 27.2,    0.5, -0.1, -6.8,  -0.006, 61.0),
    # A final bank into the intake; the last phrase floats beyond the lens.
    (145.0,     3.4, -0.5, 24.8,    0.2, -0.5, -7.0,  -0.040, 64.0),
    (149.0,     2.1, -1.7, 22.6,   -0.6, -0.3, -7.8,  -0.045, 65.0),
    (152.5,    -0.8, -0.4, 24.2,   -0.4,  0.2, -8.4,  -0.005, 62.0),
    (DURATION, -1.8,  1.0, 28.0,    0.0,  0.3, -9.5,   0.014, 58.5),
)

_TRAVEL = (
    (0.0, 0.0), (22.0, 27.0), (38.0, 48.0), (58.0, 78.0),
    (74.0, 106.0), (94.0, 142.0), (109.0, 171.0),
    (124.0, 202.0), (131.0, 218.0), (141.0, 236.0),
    (DURATION, 250.0),
)

# A broad, slow rig score gives the chapters different spatial gestures.  It
# acts on the same continuous path, never on the sung row.  The target carries
# a portion of the side movement: this is a travelling look-ahead camera, not
# a camera permanently orbiting the scene's origin.
# time, lateral reach, vertical reach, forward push, banking, look-ahead share
_RIG = (
    (0.0,       1.50, 1.60, .5, 1.15, .12),
    (22.0,      1.80, 1.40, 1.2, 1.50, .22),
    (38.0,      1.40, 1.80, .4, 1.15, .14),
    (53.0,      1.70, 2.00, 1.5, 1.80, .18),
    (58.0,      1.75, 1.80, .7, 1.60, .20),
    (70.0,      1.70, 1.80, .5, 1.50, .14),
    (74.0,      1.90, 1.60, .2, 1.60, .22),
    (83.5,      1.85, 1.65, .8, 1.90, .24),
    (94.0,      1.80, 1.70, .7, 1.50, .20),
    (102.0,     1.80, 1.90, 1.0, 1.80, .22),
    (109.0,     1.70, 2.10, .5, 1.70, .18),
    (117.0,     1.90, 2.00, 1.0, 1.80, .20),
    (124.0,     1.70, 1.90, .7, 1.70, .22),
    (131.0,     1.85, 1.70, .6, 1.60, .20),
    (141.0,     1.80, 1.70, .7, 1.50, .20),
    (149.0,     1.80, 1.90, 1.5, 1.60, .20),
    (DURATION,  1.40, 1.50, .0, 1.20, .16),
)


def _tangents(keys, monotone=False):
    """One tangent per shared vertex, in units per second."""
    slopes = [tuple((b[j] - a[j]) / (b[0] - a[0])
                    for j in range(1, len(a)))
              for a, b in zip(keys, keys[1:])]
    out = [slopes[0]]
    for i in range(1, len(keys) - 1):
        left = keys[i][0] - keys[i - 1][0]
        right = keys[i + 1][0] - keys[i][0]
        values = []
        for j, (s0, s1) in enumerate(zip(slopes[i - 1], slopes[i])):
            if monotone:
                if s0 * s1 <= 0:
                    value = 0.0
                else:
                    # Weighted harmonic mean (Fritsch-Butland), preserving
                    # positive forward velocity without phase discontinuity.
                    w0, w1 = 2 * right + left, right + 2 * left
                    value = (w0 + w1) / (w0 / s0 + w1 / s1)
            else:
                value = (s0 * right + s1 * left) / (left + right)
            values.append(value)
        out.append(tuple(values))
    out.append(slopes[-1])
    return tuple(out)


_PATH_TIMES = tuple(k[0] for k in _PATH)
_TRAVEL_TIMES = tuple(k[0] for k in _TRAVEL)
_RIG_TIMES = tuple(k[0] for k in _RIG)
_PATH_TANGENTS = _tangents(_PATH)
_TRAVEL_TANGENTS = _tangents(_TRAVEL, monotone=True)
_RIG_TANGENTS = _tangents(_RIG)
_CHAPTER_TIMES = tuple(k[0] for k in CHAPTERS)


def _sample(t, keys, times, tangents):
    i = max(0, min(len(keys) - 2, bisect_right(times, t) - 1))
    a, b = keys[i], keys[i + 1]
    h = b[0] - a[0]
    u = max(0.0, min(1.0, (t - a[0]) / h))
    u2, u3 = u * u, u * u * u
    h00, h10 = 2 * u3 - 3 * u2 + 1, u3 - 2 * u2 + u
    h01, h11 = -2 * u3 + 3 * u2, u3 - u2
    return tuple(h00 * a[j + 1] + h10 * h * tangents[i][j]
                 + h01 * b[j + 1] + h11 * h * tangents[i + 1][j]
                 for j in range(len(a) - 1))


def camera_state(t, np, math):
    """Return the continuously moving local camera and global world travel.

    ``np`` and ``math`` are accepted from the renderer so this tiny path module
    introduces no additional runtime dependencies.  Return vectors are numpy
    arrays, ready for the engine's ``look`` matrix.
    """
    t = max(0.0, min(DURATION, float(t)))
    v = list(_sample(t, _PATH, _PATH_TIMES, _PATH_TANGENTS))
    lateral, vertical, push, bank, look_share = _sample(t, _RIG, _RIG_TIMES, _RIG_TANGENTS)
    v[0] *= lateral
    v[1] *= vertical
    v[2] -= push
    v[3] += v[0] * look_share
    v[4] += v[1] * look_share * .55
    v[6] *= bank
    v[7] -= 2.0
    travel = _sample(t, _TRAVEL, _TRAVEL_TIMES, _TRAVEL_TANGENTS)[0]
    section = min(9, max(0, bisect_right(_CHAPTER_TIMES, t) - 1))
    return {
        "eye": np.asarray(v[:3], dtype=float),
        "target": np.asarray(v[3:6], dtype=float),
        "roll": float(v[6]),
        "fov": float(v[7]),
        "section": section,
        "travel": float(travel),
    }


if __name__ == "__main__":
    # This is a meaningful mathematical audit: discontinuities can create a
    # full-frame jerk in the final movie even when individual stills look good.
    import math
    import numpy as np

    samples = [camera_state(t, np, math) for t in np.linspace(0, DURATION, 9401)]
    channels = np.array([list(s["eye"]) + list(s["target"])
                         + [s["roll"], s["fov"], s["travel"]]
                        for s in samples])
    assert np.isfinite(channels).all(), "non-finite camera channel"
    assert np.diff(channels[:, -1]).min() >= -1e-10, "world moves backwards"
    assert abs(channels[0, -1]) < 1e-9
    assert abs(channels[-1, -1] - 250) < 1e-9
    assert channels[:, 2].min() >= 18 and channels[:, 2].max() <= 30
    assert np.linalg.norm(channels[:, :3] - channels[:, 3:6], axis=1).min() > 20
    eps = 1e-4
    worst = 0.0
    knots = sorted(set(_PATH_TIMES[1:-1] + _TRAVEL_TIMES[1:-1] + _RIG_TIMES[1:-1]))
    def values(t):
        s = camera_state(t, np, math)
        return np.r_[s["eye"], s["target"], s["roll"], s["fov"], s["travel"]]
    for t in knots:
        left = (values(t) - values(t - eps)) / eps
        right = (values(t + eps) - values(t)) / eps
        worst = max(worst, float(np.max(np.abs(right - left))))
    assert worst < 1e-3, ("derivative mismatch", worst)
    print("camera audit passed:", len(samples), "finite samples; C1 residual", worst)
    print("eye bounds:", channels[:, :3].min(axis=0), channels[:, :3].max(axis=0))
    print("travel:", channels[0, -1], "to", channels[-1, -1], "; ten continuous chapters")
