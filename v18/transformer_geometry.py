"""Procedural line sculptures for Transformer / forward-backward computation.

API: ``build_transformer(Mesh, np, math, C, WHITE, ACC) -> dict[str, Mesh]``.
Every primitive is a line segment; no faces, images, characters, or labels.
The empty foreground corridor is x +/-5, y +/-1.7.  All geometry fits within
x +/-16, y +/-9, z -18..4.  Front is +Z.  The machine is deliberately not a
robot: its visible causal story is token order -> Q/K/V -> weighted relations
in four heads -> concatenation -> residual / MLP -> repeated decode layers.

Keys and suggested shot sequence for 109.4--115.0 seconds:
  tf_token_belt: individual token cards across the top; enter along its length.
  tf_positions: two different-frequency position waves bonded to those cards.
  tf_q_branch / tf_k_branch / tf_v_branch: three distinct physical projections;
    reveal in that order, preferably from an oblique, close, lateral angle.
  tf_attention_heads: four independent six-by-six attention mechanisms in the
    corners; contains each head's pins, precision chassis, and connectors.
  tf_attention_weights: weighted many-to-many strands, all behind the word
    corridor.  Four heads have different strongest connections, rather than
    four copies of a decorative web.  Reveal/gain gives a readable match step.
  tf_concat: four bundles gather into an interleaved physical output bridge.
  tf_residual: one unbroken outer bypass, physically skipping the attention
    and MLP mechanisms; keep it visible through those two transforms.
  tf_mlp: small -> wide -> small node banks / feed-forward wiring, below and
    behind the attention frame.  This is a separate, differently shaped shot.
  tf_decoder: six successive U-shaped architectural layer slices, receding
    down -Z.  Fly through their off-centre mouth and out of their far end.
  tf_output: a new token exits the right-side sampling comb after decoding.
  tf_structure: asymmetric braces, power rails and periphery detail; low gain.

For 73.96--77.34 seconds, independent forward/backward keys:
  nn_layers: four fixed node banks, expanding then contracting, on both sides.
  nn_connections: dense weighted paths connecting adjacent banks only.
  nn_forward: chevron packets point from input (+Z) to output (-Z).
  nn_backward: separate red gradient branches point back towards +Z; ramp the
    return only after the forward sweep.  The banks do not reverse or rotate.

Animating the layers separately is preferable to rotating the entire object.
Suggested first show full architecture for 8--12 frames, then cut on beats to
cards, attention correspondence, concat and the decoder.  A camera can travel
through the central aperture; the large surrounding mechanisms then cross the
edges instead of remaining an isolated spinning object at the screen centre.
"""


def build_transformer(Mesh, np, math, C, WHITE, ACC):
    C, WHITE, ACC = [np.asarray(v, dtype=float) for v in (C, WHITE, ACC)]
    names = (
        'tf_token_belt', 'tf_positions',
        'tf_q_branch', 'tf_k_branch', 'tf_v_branch',
        'tf_attention_heads', 'tf_attention_weights', 'tf_concat',
        'tf_residual', 'tf_mlp', 'tf_decoder', 'tf_output', 'tf_structure',
        'nn_layers', 'nn_connections', 'nn_forward', 'nn_backward',
    )
    out = {name: Mesh() for name in names}

    def line(m, points, col=C, closed=False):
        m.line(np.asarray(points, dtype=float), np.asarray(col), closed=closed)

    def ring(m, p, r, col=C, axis=2, n=16):
        p = np.asarray(p, dtype=float)
        if axis == 2:
            u, v = np.array([1., 0, 0]), np.array([0., 1, 0])
        elif axis == 1:
            u, v = np.array([1., 0, 0]), np.array([0., 0, 1])
        else:
            u, v = np.array([0., 1, 0]), np.array([0., 0, 1])
        line(m, [p+r*(math.cos(q)*u+math.sin(q)*v)
                 for q in np.linspace(0, math.tau, n, endpoint=False)], col, True)

    def box(m, p, size, col=C):
        p, h = np.asarray(p, float), np.asarray(size, float)*.5
        corners = [p+h*[x, y, z]
                   for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        for i, a in enumerate(corners):
            for j, b in enumerate(corners):
                if j > i and np.count_nonzero(a != b) == 1:
                    line(m, [a, b], col)

    def path(m, points, col=C, strands=3, step=.055, axis=1):
        points = np.asarray(points, float)
        for k in range(strands):
            shift = np.zeros(3)
            shift[axis] = (k-(strands-1)/2)*step
            line(m, points+shift, col*(1 if k == strands//2 else .45))

    def arrow(m, p, direction, col=C, size=.34):
        p, d = np.asarray(p, float), np.asarray(direction, float)
        d /= max(1.e-8, float(np.linalg.norm(d)))
        u = np.cross(d, [0, 1, 0] if abs(d[1]) < .9 else [1, 0, 0])
        u /= max(1.e-8, float(np.linalg.norm(u)))
        line(m, [p-d*size+u*size*.55, p, p-d*size-u*size*.55], col)

    def beam(m, a, b, col=C, radius=.12, divisions=8):
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b-a
        d /= max(1.e-8, float(np.linalg.norm(d)))
        u = np.cross(d, [0, 1, 0] if abs(d[1]) < .9 else [1, 0, 0])
        u /= max(1.e-8, float(np.linalg.norm(u)))
        v = np.cross(d, u)
        offsets = [radius*(sx*u+sy*v)
                   for sx, sy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]
        for off in offsets:
            line(m, [a+off, b+off], col)
        for j in range(divisions+1):
            p = a+(b-a)*j/divisions
            line(m, [p+off for off in offsets], col*.55, True)
            if j < divisions:
                q = a+(b-a)*(j+1)/divisions
                for k in range(4):
                    line(m, [p+offsets[k], q+offsets[(k+1)%4]], col*.38)

    def card(m, p, w=1.3, h=1.8, col=C, variant=0):
        x, y, z = p
        box(m, p, [w, h, .18], col)
        # Vector components as differing lengths, never letters or pseudo text.
        for j in range(6):
            yy = y-h*.34+j*h*.135
            length = w*(.22+.075*((variant*3+j*5)%7))
            line(m, [[x-w*.34, yy, z+.12], [x-w*.34+length, yy, z+.12]],
                 WHITE*(.45+.055*((variant+j)%6)))
        for sx in (-1, 1):
            for sy in (-1, 1):
                ring(m, [x+sx*w*.39, y+sy*h*.42, z+.11], .035, col*.7, n=8)
        for side in (-1, 1):
            for j in range(4):
                xx = x-w*.24+j*w*.16
                line(m, [[xx, y+side*h*.50, z], [xx, y+side*(h*.50+.19), z]], col*.7)

    def bezier(a, b, lift=0., depth=-2., n=15):
        a, b = np.asarray(a, float), np.asarray(b, float)
        c = (a+b)*.5+np.array([0., lift, depth])
        return [(1-t)**2*a+2*t*(1-t)*c+t*t*b for t in np.linspace(0, 1, n)]

    # Top belt: discrete ordered tokens, not a single decorative line.
    m = out['tf_token_belt']
    for j in range(11):
        x = -13.5+j*2.7
        y = 7.05+.20*math.sin(j*.9)
        card(m, [x, y, 2.0], 1.55, 1.65, C*.90, j)
        for z in (1.7, 2.3):
            line(m, [[x-.9, 5.92, z], [x+.9, 5.92, z]], C*.55)
        ring(m, [x, 5.85, 2.0], .24, WHITE*.55, axis=0)
        if j < 10:
            path(m, [[x+.8, y, 1.9], [x+1.25, y, 1.9],
                     [x+1.9, 7.05+.20*math.sin((j+1)*.9), 1.9]], C*.55)
    for yy in (5.75, 5.97):
        line(m, [[-15.3, yy, 1.55], [15.3, yy, 1.55]], C*.50)

    m = out['tf_positions']
    for k, frequency in enumerate((.54, 1.10)):
        pts = [[x, 8.25+.37*math.sin(x*frequency+k*.7), 2.35+k*.17]
               for x in np.linspace(-15.3, 15.3, 301)]
        line(m, pts, ACC*(.9 if k == 0 else .5))
    for j in range(11):
        x = -13.5+j*2.7
        path(m, [[x, 7.92, 2.13], [x, 8.25+.37*math.sin(x*.54), 2.35]],
             ACC*.65, strands=2)
        for tick in range(j%4+1):
            line(m, [[x-.36+tick*.18, 8.73, 2.05],
                     [x-.36+tick*.18, 8.88, 2.05]], C*.55)

    # Three differently routed projections. They are separate meshes so a
    # shot can reveal the actual split before their attention correspondences.
    branch_cols = (C, WHITE, ACC)
    for b, key in enumerate(('tf_q_branch', 'tf_k_branch', 'tf_v_branch')):
        m = out[key]
        x, col = -10.5+b*10.5, branch_cols[b]
        box(m, [x, 4.45, .85], [3.7, 1.75, 1.3], col*.85)
        for row in range(3):
            for j in range(9):
                xx, yy = x-1.38+j*.345, 4.0+row*.42
                box(m, [xx, yy, 1.59], [.16, .19, .12], col*(.48+.04*((j+row)%5)))
        for j in range(6):
            off = (j-2.5)*.20
            path(m, [[x+off, 5.8, 1.65], [x+off, 5.5, .85],
                     [x+off, 5.32, .85]], col*.75, strands=2, step=.025)
            # Three longitudinal depths make the branches visually separable.
            path(m, [[x+off, 3.55, .65], [x+off, 3.1, -1.0-b*.45],
                     [(-10 if b == 0 else 10)+off, 3.1, -1.0-b*.45]],
                 col*.75, strands=2, step=.025)
        for side in (-1, 1):
            yy = side*4.7
            for lane in range(6):
                xx = side*10.5+(lane-2.5)*.15
                pts = [[x+(lane-2.5)*.18, 3.45, -.1-b*.45],
                       [x+(lane-2.5)*.18, 2.35, -3.0-b*.8],
                       [xx, 2.35, -4.8-b*.7], [xx, yy, -4.8-b*.7]]
                path(m, pts, col*.55, strands=2, step=.025)
                arrow(m, pts[-1], [0, side, 0], col*.8, .24)

    # Four attention heads: each uses its own relationship pattern. Head
    # panels live in four quadrants and leave a genuine flight / lyric void.
    m, weighted = out['tf_attention_heads'], out['tf_attention_weights']
    for h, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        cx, cy, zz = sx*10.25, sy*4.70, -6.2
        for z in (zz+.7, zz-.7):
            # A chamfered board, not another concentric rectangle.
            outline = [[cx-3.5, cy-1.5, z], [cx-2.8, cy-2.15, z],
                       [cx+2.8, cy-2.15, z], [cx+3.5, cy-1.5, z],
                       [cx+3.5, cy+1.5, z], [cx+2.8, cy+2.15, z],
                       [cx-2.8, cy+2.15, z], [cx-3.5, cy+1.5, z]]
            line(m, outline, C*.72, True)
        queries, keys = [], []
        for j in range(6):
            yy = cy-1.45+j*.58
            qa, kb = np.array([cx-2.75, yy, zz+.9]), np.array([cx+2.75, yy, zz+.9])
            queries.append(qa)
            keys.append(kb)
            for p in (qa, kb):
                ring(m, p, .17, WHITE*.8, n=12)
                line(m, [p+[0, 0, -.8], p+[0, 0, .10]], C*.6)
                box(m, p+[0, 0, -.52], [.35, .35, .22], C*.5)
        for q, a in enumerate(queries):
            for k, b in enumerate(keys):
                primary = ((k-q-h*2) % 6 == 0)
                secondary = ((k+q+h) % 5 == 0)
                col = (ACC*.98 if primary else WHITE*.6 if secondary else C*.19)
                # Different strengths become differing conductor counts.
                pts = bezier(a, b, lift=(q-k)*.055,
                             depth=-.50-.12*abs(q-k), n=13)
                path(weighted, pts, col, strands=3 if primary else 1, step=.038)
                if primary:
                    arrow(weighted, pts[8], np.asarray(pts[9])-pts[7], ACC*.95, .25)
        for sx2 in (-1, 1):
            for sy2 in (-1, 1):
                ring(m, [cx+sx2*2.95, cy+sy2*1.73, zz+.72], .10, C*.8, n=12)
        # Output value pins are on a separate far-depth rail.
        for j in range(6):
            p = [cx-1.4+j*.56, cy, zz-1.2]
            box(m, p, [.20, .30, .35], ACC*.6)
            path(weighted, [keys[j], [p[0], p[1], zz-1.2]], ACC*.44, strands=2)

    # Four groups physically gather and interleave into one output bridge.
    m = out['tf_concat']
    for h, (sx, sy) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        for lane in range(6):
            x0, y0 = sx*10.25-1.4+lane*.56, sy*4.7
            x1 = -3.85+(lane*4+h)*.335
            pts = [[x0, y0, -7.4], [x0, sy*2.8, -9.5],
                   [x1, -3.4, -10.4-h*.12], [x1, -6.9, -10.4-h*.12]]
            path(m, pts, (C if h%2 == 0 else ACC)*.72, strands=2, step=.032)
            arrow(m, pts[-1], [0, -1, 0], WHITE*.8, .24)
    beam(m, [-4.5, -6.3, -10.3], [4.5, -6.3, -10.3], C*.65, .13, 18)
    beam(m, [-4.5, -7.4, -11.1], [4.5, -7.4, -11.1], C*.65, .13, 18)
    for j in range(24):
        x = -3.85+j*.335
        box(m, [x, -6.9, -10.6], [.21, .52, .52], WHITE*.75)

    # The skip connection visibly bypasses both processing mechanisms.
    m = out['tf_residual']
    skip = [[-14.9, 7.25, 1.8], [-15.3, 7.25, .3], [-15.3, 2.35, -.5],
            [-15.3, 2.35, -12.2], [-15.3, -8.1, -12.2],
            [14.8, -8.1, -12.2], [14.8, -4.25, -12.2], [10.7, -4.25, -12.2]]
    path(m, skip, ACC*.8, strands=5, step=.065)
    for j in range(1, len(skip)-1):
        ring(m, skip[j], .28, WHITE*.7, n=16)
    # Physical addition junction; a cross is mathematical geometry, no label.
    ring(m, [10.7, -4.25, -12.2], .55, WHITE*.9, n=28)
    line(m, [[10.36, -4.25, -12.15], [11.04, -4.25, -12.15]], ACC)
    line(m, [[10.7, -4.59, -12.15], [10.7, -3.91, -12.15]], ACC)

    # MLP: a narrow vector bank fans into a visibly wider hidden bank, then
    # contracts.  It sits behind the middle so the lyric cannot be occluded.
    m = out['tf_mlp']
    banks = []
    for layer, (x, count) in enumerate(((-10.5, 5), (0., 13), (10.5, 5))):
        nodes = []
        for j in range(count):
            y = -7.1+(j-(count-1)/2)*(.25 if count > 5 else .46)
            p = np.array([x, y, -14.2])
            nodes.append(p)
            ring(m, p, .13 if count > 5 else .20, WHITE*.9, n=12)
            box(m, p+[0, 0, -.2], [.34, .29, .20], C*.5)
        banks.append(nodes)
        beam(m, [x, -8.75, -14.5], [x, -5.35, -14.5], C*.5, .11, 7)
    for left, right in zip(banks[:-1], banks[1:]):
        for j, a in enumerate(left):
            for k, b in enumerate(right):
                line(m, bezier(a, b, depth=-.35, n=9), C*(.22+.1*((j+k)%3)))
    for x in (-6.8, 6.8):
        for lane in range(3):
            arrow(m, [x, -7.1+(lane-1)*.38, -14.3], [1, 0, 0], ACC*.85, .33)

    # Repeated computation layers become real architecture in depth.  The
    # asymmetric shoulders distinguish it from a generic rectangular tunnel.
    m = out['tf_decoder']
    for j in range(6):
        z = -.3-j*3.25
        for sx in (-1, 1):
            xx = sx*(6.5+.2*(j%2))
            box(m, [xx, 0, z], [1.0, 4.5, .6], C*.65)
            for k in range(6):
                yy = -1.8+k*.72
                box(m, [xx, yy, z+.35], [.6, .24, .16], WHITE*.6)
            beam(m, [xx, 2.4, z], [sx*4.25, 4.6, z], C*.55, .10, 5)
            beam(m, [xx, -2.4, z], [sx*4.8, -4.2, z], C*.55, .10, 5)
            if j < 5:
                path(m, [[xx, sy*2.2, z] for sy in (-1, 1)], C*.28, strands=2)
                for sy in (-1, 1):
                    path(m, [[xx, sy*2.2, z], [xx, sy*2.2, z-3.25]], C*.45, strands=3)
        path(m, [[-4.25, 4.6, z], [-1.1, 5.15, z], [4.25, 4.6, z]], C*.55, strands=3)
        path(m, [[-4.8, -4.2, z], [.8, -4.9, z], [4.8, -4.2, z]], C*.55, strands=3)
        # Layer token cell combs, varied by depth instead of repeated circles.
        for side in (-1, 1):
            for k in range(7):
                x = -3.3+k*1.1
                card(m, [x, side*(5.8+.09*(j%2)), z], .7, .92, C*.45, j+k)

    m = out['tf_output']
    for j in range(9):
        x, y, z = 8.0+j*.78, 5.15, -13.2
        h = .9+1.5*(.5+.5*math.sin(j*2.17))
        box(m, [x, y, z], [.46, h, .46], WHITE*(.4+.04*j))
        path(m, [[x, y-h*.5, z], [x, 3.2, z], [14.4, 3.2, z]], C*.45, strands=2)
    card(m, [14.4, 1.65, -13.2], 1.6, 1.8, ACC*.95, 5)
    arrow(m, [14.4, 2.85, -13.2], [0, -1, 0], ACC, .4)

    # Precision detail, deliberately asymmetric so changing view reveals a
    # genuinely different silhouette. All sides of the screen have anchors.
    m = out['tf_structure']
    for side in (-1, 1):
        beam(m, [side*15.6, 8.5, 2.9], [side*15.6, -8.5, -15.6], C*.35, .14, 24)
        for k in range(14):
            yy = -7.8+k*1.17
            z = -6.2-.5*math.sin(k*.7)
            box(m, [side*14.7, yy, z], [.8, .42, 1.5], C*.32)
            for p in range(3):
                ring(m, [side*14.72, yy, z+.35-p*.35], .095, WHITE*.4, axis=0, n=10)
        for lane in range(8):
            x = side*(14.2+lane*.13)
            pts = [[x, y, -15.5+.35*math.sin(y*.8+lane*.35)]
                   for y in np.linspace(-8.4, 8.4, 89)]
            line(m, pts, C*.30)
    for x in (-12.8, 13.4):
        beam(m, [x, -8.5, -15.7], [x*.42, -8.5, -15.7], C*.35, .12, 11)
        for k in range(8):
            box(m, [x-(k*.65 if x > 0 else -k*.65), -8.3, -15.3], [.28, .5, .4], C*.3)

    # Forward and backward have direction encoded in their physical arrows.
    # The same network stays put; gradients return through the same topology.
    layers, connections = out['nn_layers'], out['nn_connections']
    forward, backward = out['nn_forward'], out['nn_backward']
    for side in (-1, 1):
        banks = []
        for layer, count in enumerate((5, 9, 9, 5)):
            z = 2.6-layer*5.8
            nodes = []
            for j in range(count):
                y = (j-(count-1)*.5)*(.98 if count > 5 else 1.45)
                x = side*(9.8+.26*math.sin(j*1.7+layer))
                p = np.array([x, y, z])
                nodes.append(p)
                ring(layers, p, .28, WHITE*.85, n=18)
                ring(layers, p+[0, 0, -.16], .18, C*.7, n=12)
                for a in np.linspace(0, math.tau, 4, endpoint=False):
                    delta = np.array([math.cos(a), math.sin(a), 0])
                    line(layers, [p+delta*.33, p+delta*.57], C*.6)
            banks.append(nodes)
            beam(layers, [side*11.2, -5.4, z-.2], [side*11.2, 5.4, z-.2], C*.6, .11, 13)
            for sy in (-1, 1):
                beam(layers, [side*11.2, sy*5.4, z-.2], [side*7.2, sy*5.4, z-.2], C*.6, .10, 8)
        for li, (left, right) in enumerate(zip(banks[:-1], banks[1:])):
            for aidx, a in enumerate(left):
                for bidx, b in enumerate(right):
                    c = (a+b)*.5+np.array([side*.55, 0, 0])
                    pts = [(1-t)**2*a+2*t*(1-t)*c+t*t*b
                           for t in np.linspace(0, 1, 11)]
                    strong = ((aidx+bidx+li)%4 == 0)
                    line(connections, pts, C*(.48 if strong else .17))
                    if strong:
                        for t in (.29, .58, .84):
                            p = (1-t)**2*a+2*t*(1-t)*c+t*t*b
                            d = 2*(1-t)*(c-a)+2*t*(b-c)
                            arrow(forward, p, d, WHITE*.95, .31)
                            # Gradient magnitude differs per edge, not a mirror
                            # of the forward packet count or a second network.
                            arrow(backward, p+[side*.20, .12, 0], -d,
                                  ACC*(.6+.09*((aidx+bidx)%4)), .25+.025*(aidx%3))
            for j, p in enumerate(right):
                for k in range(3):
                    box(backward, p+[side*(.65+k*.19), 0, 0],
                        [.10, .10+.07*((j+k)%3), .10], ACC*.7)
        # Low, deep crosslinks show one connected calculation, not two cages.
        for lane in range(6):
            path(connections, [[side*9.8, -4.6-lane*.11, -14.8],
                               [side*6.0, -6.6-lane*.11, -14.8],
                               [0, -6.6-lane*.11, -14.8]], C*.32, strands=2)

    return out


def audit_geometry(meshes, np):
    """Small JSON-serializable audit; never modifies meshes or writes files."""
    counts = {key: len(mesh.l) for key, mesh in meshes.items()}
    points = np.asarray([p[:3] for mesh in meshes.values() for p in mesh.l])
    triangles = sum(len(mesh.v)//3 for mesh in meshes.values())
    return {
        'layers': len(meshes),
        'line_vertices': sum(counts.values()),
        'triangles': triangles,
        'minimum': points.min(axis=0).tolist(),
        'maximum': points.max(axis=0).tolist(),
        'by_layer': counts,
        'within_vertex_budget': sum(counts.values()) < 250000,
        'line_only': triangles == 0,
    }
