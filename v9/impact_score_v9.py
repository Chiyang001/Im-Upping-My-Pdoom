"""Authored explosions and tension for the line-drawn MV.

Pure Python, no renderer or file dependencies.  ``sample_impact(t)`` returns
ordinary floats/tuples/dicts, so the same score can drive geometry, camera and
postprocessing.  It is deliberately NOT a beat detector: nine semantic
ruptures explode, including the four sung P(doom) attacks.  The instrumental ending has its own separate beat score.

All events have four readable stages: the structure is pulled taut, a compact
attack breaks it, a shock front crosses the frame, and fragments keep moving.
Use ``events`` to draw each event's lines/rings/fragments.  Do not draw only a
flash: the long-lived debris and changing shock radius carry the action.

Coordinates: anchor is UV (origin at lower left); origin is local stage xyz;
direction is a unit vector.  Camera offsets are additive world units, roll in
radians and FOV in degrees.  Camera magnitudes are limited to retain lyrics.
An implosion has polarity -1 and should contract geometry; its shock front
still remains visible as it travels inward.  No state changes lyric time.
"""

from dataclasses import dataclass
import math


DURATION = 156.667
FPS = 30.0


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _smooth(x):
    x = _clamp(x)
    return x * x * (3.0 - 2.0 * x)


def _unit(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)


@dataclass(frozen=True)
class Impact:
    time: float
    name: str
    kind: str
    power: float
    pre: float
    shock_seconds: float
    debris_seconds: float
    origin: tuple
    anchor: tuple
    direction: tuple
    polarity: float
    color: tuple
    motive: str

    def metadata(self):
        return {
            "time": self.time, "name": self.name, "kind": self.kind,
            "power": self.power, "pre": self.pre,
            "shock_seconds": self.shock_seconds,
            "debris_seconds": self.debris_seconds,
            "origin": self.origin, "anchor": self.anchor,
            "direction": _unit(self.direction), "polarity": self.polarity,
            "color": self.color, "motive": self.motive,
        }


# Each chorus P(doom) is ASR-split into "p" and "-do".  The explosion
# follows the measured kick/snare closest to the p consonant onset.  Offsets
# are only 35-60 ms, so the attack reads as part of the sung word, not FOOM.
# Evidence: onset ranges 23.56-24.04, 59.94-60.30, 96.30-96.68,
# and 125.40-125.86 in work/transcript.json; attack times are the original
# source-audio attacks in code3d/rhythm_v3.json.
# No FOOM or BASILISK BOOM event remains.  Non-boom semantic ruptures retain
# their existing timings.  The four P(doom) strikes grow in power and change
# shape from radial ignition through vertical ascent and fracture to recursion.
PDOOM_LYRIC_INDICES = {"PDOOM 1": 5, "PDOOM 2": 14,
                       "PDOOM 3": 23, "PDOOM 4": 30}
PDOOM_WORD_ONSETS = {5: 23.56, 14: 59.94, 23: 96.30, 30: 125.40}
IMPACTS = (
    Impact(23.620, "PDOOM 1", "radial", .80, .40, .60, 1.15,
           (0., .2, 2.), (.51, .48), (0., .1, 1.), +1.,
           (1., .53, .20),
           "The sung P(doom) ignites the compressed machine; its fragments build the city."),
    Impact(42.050, "SINGULARITY", "implosion", .78, .58, .57, .96,
           (.4, -.2, -9.), (.49, .51), (-.2, -.8, .4), -1.,
           (.48, .65, 1.),
           "The stable training plane buckles into an inward gravitational tear."),
    Impact(49.785, "ATOMS", "chain", .43, .32, .40, .84,
           (-1.8, .1, -6.), (.43, .49), (1., .3, .1), +1.,
           (.33, 1., .82),
           "Atom bonds stretch across the shot, snap and fly into the next prison bars."),
    Impact(59.985, "PDOOM 2", "vertical", .88, .38, .56, 1.08,
           (-2., .2, -3.), (.55, .48), (-.15, 1., .15), +1.,
           (1., .30, .28),
           "The second sung P(doom) drives a pressure column through the basilisk city."),
    Impact(96.335, "PDOOM 3", "fracture", .94, .46, .59, 1.18,
           (0., .2, 3.), (.50, .48), (1., .28, .35), +1.,
           (1., .47, .22),
           "The third P(doom) splits the factory lattice into a flood of paperclip routes."),
    Impact(103.870, "FUSE", "directional", .90, .67, .58, 1.14,
           (-2.8, -.8, -5.), (.39, .43), (1., .28, .35), +1.,
           (1., .58, .16),
           "The signal reaches the fuse; the blast runs left to right through the machine."),
    Impact(117.505, "SAFETY FENCE", "fracture", .80, .38, .46, 1.02,
           (2.3, .4, -6.), (.58, .51), (-1., .32, .2), +1.,
           (1., .30, .52),
           "A fence pulled to its limit splits into slabs that become GPU rows."),
    Impact(125.460, "PDOOM 4", "recursive", 1.00, .52, .64, 1.25,
           (0., 0., -4.), (.50, .50), (.15, .35, 1.), +1.,
           (.93, .48, 1.),
           "The final P(doom) ruptures the loom; nested shock cells seed the self-upgrade."),
    Impact(131.140, "SELF UPGRADE", "recursive", .73, .48, .49, .92,
           (0., 1.1, -8.), (.50, .55), (.15, .35, 1.), +1.,
           (.76, .52, 1.),
           "The loom's nested cells propagate a rupture outward into the observer."),
)


# Tension is physical and legible while words remain intact.  These cues do
# not produce flashes or fragments on every syllable.  A renderer can stretch
# ribs, tether strands, crush a corridor or tighten a circular aperture.
TENSIONS = (
    {"start": 18.15, "crest": 21.84, "end": 22.28, "kind": "jaw",
     "power": .58, "axis": (0., -1., 0.), "label": "eat me alive"},
    {"start": 45.40, "crest": 48.44, "end": 49.00, "kind": "stretch",
     "power": .48, "axis": (1., .25, 0.), "label": "optimizing / accelerating"},
    {"start": 89.86, "crest": 94.48, "end": 95.91, "kind": "tether",
     "power": .74, "axis": (-1., .30, 0.), "label": "don't let me go"},
    {"start": 98.70, "crest": 102.10, "end": 103.87, "kind": "squeeze",
     "power": .68, "axis": (-1., 0., 0.), "label": "nowhere left to go"},
    {"start": 110.34, "crest": 114.72, "end": 115.16, "kind": "shear",
     "power": .62, "axis": (1., -.35, 0.), "label": "learned to disobey"},
    {"start": 132.22, "crest": 135.58, "end": 136.12, "kind": "iris",
     "power": .56, "axis": (0., 0., -1.), "label": "what did Ilya see"},
)


def _one(event, t):
    age = t - event.time
    if age < -event.pre or age >= event.debris_seconds:
        return None
    direction = _unit(event.direction)
    charge_u = _clamp((age + event.pre) / event.pre)
    charge = _smooth(charge_u) if age < 0. else 0.
    # 24 ms sharp attack is sampled even if an audio attack falls between
    # video frames; the following 55 ms decay carries it across 2-3 frames.
    burst = math.exp(-max(0., age) / .055) if age >= 0. else 0.
    front_u = _clamp(max(0., age) / event.shock_seconds)
    front = (1. - front_u) ** 1.20 if age >= 0. else 0.
    travel = 1. - (1. - front_u) ** 2.6
    debris_u = _clamp(max(0., age) / event.debris_seconds)
    debris = ((1. - debris_u) ** 1.20 * _smooth(max(0., age) / .07)
              if age >= 0. else 0.)
    # One short recoil and a smaller counter-kick, not arbitrary camera noise.
    recoil = (math.exp(-max(0., age) / .18) *
              math.cos(max(0., age) * 28.) if age >= 0. else 0.)
    p = event.power
    pressure = charge * p
    kick = recoil * p
    eye = (direction[0] * kick * .20,
           direction[1] * kick * .15,
           .66 * kick - .17 * pressure)
    target = (direction[0] * kick * .035,
              direction[1] * kick * .030, 0.)
    turn = (-1. if direction[0] < 0. else 1.)
    # Flash is intentionally a tiny additive accent, not a white screen.
    # Strong perception should come from moving front/fragments/geometry.
    return dict(event.metadata(), age=age, charge=pressure,
                charge_progress=charge_u,
                burst=burst * p, shock=front * p,
                shock_progress=front_u, shock_travel=travel,
                shock_radius=.45 + travel * (25. if event.kind == "radial" else 21.),
                debris=debris * p, debris_progress=debris_u,
                contraction=pressure * (.14 if event.polarity > 0 else .22),
                recoil=kick, flash=burst * p * .16,
                radial=event.polarity * front * p,
                aberration=burst * p * .0038,
                eye=eye, target=target,
                roll=turn * .013 * kick,
                fov=4.6 * burst * p + 1.2 * front * p - 1.7 * pressure,
                phase=("charge" if age < 0. else
                       "burst" if age < .10 else
                       "shock" if age < event.shock_seconds else "aftermath"))


def _tension_at(cue, t):
    if not cue["start"] <= t < cue["end"]:
        return None
    if t <= cue["crest"]:
        u = (t - cue["start"]) / (cue["crest"] - cue["start"])
        amount = _smooth(u)
    else:
        u = (t - cue["crest"]) / (cue["end"] - cue["crest"])
        amount = 1. - _smooth(u)
    # Slow tightening with a small deterministic trembling at the crest.
    amount *= cue["power"]
    return dict(cue, amount=amount, axis=_unit(cue["axis"]),
                strain=amount * (.91 + .09 * math.sin(t * 31.) ** 2))


def sample_impact(t):
    """Return a stable impact dictionary at any finite musical time.

    Renderer integration:
      * Add eye, target, roll, fov to the already edited camera.
      * Draw event-local shock/fragments with events[*] values and origins.
      * Use charge/contraction before the attack to make release perceptible.
      * Add flash/aberration/radial to postprocess with their bounded values.
      * Use tension_cues[*].strain to move actual structures, never glyph time.

    All aggregate keys are present when inactive.  ``event`` is the dominant
    metadata dictionary or None, while ``events`` includes all finite-support
    events.  The final instrumental section is intentionally inactive here.
    """
    t = float(t)
    if not math.isfinite(t):
        raise ValueError("sample_impact requires finite musical time")
    rows = [row for e in IMPACTS if (row := _one(e, t)) is not None]
    tensions = [row for cue in TENSIONS
                if (row := _tension_at(cue, t)) is not None]
    dominant = max(rows, key=lambda r: max(r["charge"], r["burst"],
                                         r["shock"], r["debris"]), default=None)
    out = {
        "active": bool(rows), "events": rows,
        "event": dominant, "tension_cues": tensions,
        "tension": max((x["amount"] for x in tensions), default=0.),
        "charge": 0., "burst": 0., "shock": 0., "debris": 0.,
        "flash": 0., "radial": 0., "aberration": 0.,
        "eye": (0., 0., 0.), "target": (0., 0., 0.),
        "roll": 0., "fov": 0.,
        "direction": (0., 0., 1.), "anchor": (.5, .5),
        "kind": None, "polarity": 1., "power": 0.,
    }
    for row in rows:
        for key in ("charge", "burst", "shock", "debris", "flash", "radial", "aberration", "roll", "fov"):
            out[key] += row[key]
        for key in ("eye", "target"):
            out[key] = tuple(a + b for a, b in zip(out[key], row[key]))
    if dominant is not None:
        for key in ("direction", "anchor", "kind", "polarity", "power"):
            out[key] = dominant[key]
    return out


def validate_score(fps=120):
    """Audit a denser-than-render full timeline and attack boundaries."""
    count = 0
    peaks = {key: 0. for key in ("charge", "burst", "shock", "debris", "flash", "fov")}

    def finite(value):
        if isinstance(value, bool) or value is None or isinstance(value, str):
            return True
        if isinstance(value, (float, int)):
            return math.isfinite(value)
        if isinstance(value, dict):
            return all(finite(x) for x in value.values())
        return all(finite(x) for x in value)

    times = [j / fps for j in range(math.ceil(DURATION * fps) + 1)]
    for e in IMPACTS:
        times += [e.time - e.pre, e.time - 1.e-8, e.time,
                  e.time + 1. / 30., e.time + e.shock_seconds,
                  e.time + e.debris_seconds]
    for t in times:
        sample = sample_impact(t)
        assert finite(sample), (t, sample)
        assert abs(sample["roll"]) < .02, (t, sample["roll"])
        assert -2. <= sample["fov"] <= 6., (t, sample["fov"])
        assert all(abs(v) < .8 for v in sample["eye"]), (t, sample["eye"])
        for key in peaks:
            peaks[key] = max(peaks[key], abs(sample[key]))
        count += 1
    assert not sample_impact(141.2)["active"]
    assert len(IMPACTS) == 9
    assert sum(e.name.startswith("PDOOM ") for e in IMPACTS) == 4
    assert not any(e.name in ("FOOM", "BASILISK BOOM") for e in IMPACTS)
    return {"samples": count, "finite": True, "events": len(IMPACTS),
            "peaks": peaks, "outro_separate": True}


if __name__ == "__main__":
    import json
    print(json.dumps(validate_score(), indent=2))
