"""Semantic travel: a rail retrace and a parallax study of one Lisp machine.

The matrices are frozen by semantic_host against authored_frame_view; the
camera never constructs or reparents the props.  Repeat preserves the signed
normal distance of the existing physical lyric flight.
"""


def _smooth(x):
    x = min(1., max(0., x))
    return x*x*(3.-2.*x)


def _mix(a, b, u):
    return a*(1.-u)+b*u


def repeat_travel(t):
    """Forward, reverse, repeated accelerated scan along the SAME rail."""
    if not 73.87 <= t < 77.24:
        return None
    if t < 74.40:
        u = _smooth((t-73.87)/.53)
        return {'phase': 'forward-entry', 'rail': -2.4*u, 'lift': .65*u}
    if t < 75.90:
        u = _smooth((t-74.40)/1.5)
        return {'phase': 'forward-pass', 'rail': -2.4-4.1*u, 'lift': .65+.7*u}
    if t < 76.30:
        u = _smooth((t-75.90)/.4)
        return {'phase': 'backward-retrace', 'rail': -6.5+5.2*u, 'lift': 1.35-1.25*u}
    # The final repeat rides the existing one-way FEEDBACK REPEAT word pass.
    # Only tangent displacement is added: no crossing, uncrossing or return
    # of its normal coordinate.  At the two cuts the same rail is recognised.
    u = _smooth((t-76.30)/.94)
    return {'phase': 'repeat-launch', 'rail': -1.3-3.3*u, 'lift': .1-.85*u}


def meaning_camera(t, eye, target, roll, fov, *, g):
    np, math = g['np'], g['math']
    eye, target = np.asarray(eye, float), np.asarray(target, float)
    scan = repeat_travel(t)
    if scan:
        b = g['semantic_host']('mlp', 75.1, t, 20., 1.16)
        right = b[:3, 0]/np.linalg.norm(b[:3, 0])
        up = b[:3, 1]/np.linalg.norm(b[:3, 1])
        if t >= 76.30:
            event = g['NARRATIVE_EVENTS']['FEEDBACK REPEAT']
            _, normal = g['camera_impact_focus'](event, t)
            right -= normal*float(right@normal)
            right /= np.linalg.norm(right)
            up = np.cross(normal, right)
            up /= np.linalg.norm(up)
        move = right*scan['rail']+up*scan['lift']
        # Equal displacement of eye and target makes an actual truck/dolly,
        # rather than a look-at orbit around the same unmoving central point.
        return dict(eye=eye+move, target=target+move,
                    roll=roll+(.045 if t >= 76.30 else -.035)*math.sin(math.pi*_smooth((t-73.87)/3.37)),
                    fov=fov, phase=scan['phase'])
    if 84.78 <= t < 89.995:
        b = g['semantic_host']('cdr', 87.1, t, 20., 1.12)
        basis = b[:3, :3]/np.linalg.norm(b[:3, :3], axis=0)
        u = _smooth((t-84.78)/.24)
        progress = _smooth((t-85.10)/3.9)
        # First inspect the head/tail split, then glide low along the common
        # backbone.  The last .8 s is a faster departure under its open arch.
        selecting = _smooth((t-86.85)/1.77)
        departing = _smooth((t-88.62)/1.375)
        move = np.array([-1.15+3.1*progress, -.35-.70*progress-1.2*departing,
                         .65*math.sin(progress*math.pi)])
        move += np.array([4.0,-1.35,-4.0])*selecting
        move += np.array([5.2,-2.0,-6.0])*departing
        move *= u
        look = np.array([.24*progress-.9*selecting, -.16*progress+.5*selecting,
                         -.35*departing])*u
        return dict(eye=eye+basis@move, target=target+basis@(move+look),
                    roll=roll-.04*u*math.sin(progress*math.pi), fov=fov,
                    phase='cdr-tail-parallax')
    return None
