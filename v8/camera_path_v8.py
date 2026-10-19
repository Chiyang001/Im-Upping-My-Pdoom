"""Faster continuous travel underneath the authored short camera shots.

The same distance is used by scenery, lyric anchors, signal and its wake.
It therefore increases real parallax without resetting the lyrics to a stage.
The lyric clock and music are unchanged.
"""

from camera_path import camera_state as _base_camera_state

TRAVEL_GAIN = 1.65


def camera_state(t, np, math):
    state = dict(_base_camera_state(t, np, math))
    state['travel'] *= TRAVEL_GAIN
    return state
