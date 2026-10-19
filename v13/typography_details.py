"""Five physical line treatments drawn inside the original glyph outline.

Call decorate_word immediately after textmesh has drawn its contours, before
the individual word is positioned.  No font, raster asset, random generator
or additional character is used. Existing front outlines are never removed
or displaced; hatch lines use even/odd clipping so counters remain empty.

style accepts 0..4 or 'pcb', 'fault', 'woven', 'skeleton', 'scan'.  All added
lines belong to the glyph's own face, sidewall or back edge. GO gets a long
counter tunnel and extra ribs, which supply parallax in a camera plane pass.
The function mutates and returns mesh. Mesh is accepted to match the renderer
factory convention; np/math/colors are supplied by the renderer.
"""

STYLE_NAMES = ('pcb', 'fault', 'woven', 'skeleton', 'scan')


def decorate_word(mesh, text, size, depth, style, Mesh, np, math, C, WHITE, ACC):
    if not mesh.l or size <= 0.:
        return mesh
    if isinstance(style, str):
        style = STYLE_NAMES.index(style.lower()) if style.lower() in STYLE_NAMES else 0
    style = int(style) % 5
    a = np.asarray(mesh.l, dtype=float)
    pairs = a.reshape((-1, 2, a.shape[-1]))
    # Only the actual front contour, excluding woven interiors and ribs.
    front = pairs[np.all(np.abs(pairs[:, :, 2]-depth) < 1.e-7, axis=1), :, :3]
    if not len(front):
        return mesh
    # Font curves contain many nearly collinear sampling points. Additional
    # technical layers use a carefully simplified contour; the complete
    # original bright silhouette above is left byte-for-byte unchanged.
    def simplify(points, tolerance):
        if len(points) <= 2:
            return points
        a, b = points[0], points[-1]
        v = b-a
        den = float(v@v)
        if den < 1.e-15:
            distances = np.linalg.norm(points-a, axis=1)
        else:
            u = np.clip(((points-a)@v)/den, 0., 1.)
            distances = np.linalg.norm(points-(a+u[:, None]*v), axis=1)
        k = int(np.argmax(distances))
        if distances[k] <= tolerance:
            return np.array([a, b])
        return np.concatenate((simplify(points[:k+1], tolerance)[:-1],
                               simplify(points[k:], tolerance)))

    contours, run = [], []
    for p, q in front:
        if run and np.linalg.norm(run[-1]-p) > 1.e-6:
            contours.append(np.asarray(run))
            run = []
        if not run:
            run.append(p)
        run.append(q)
        if np.linalg.norm(run[-1]-run[0]) < 1.e-6:
            contours.append(np.asarray(run))
            run = []
    if run:
        contours.append(np.asarray(run))
    simplified = []
    for points in contours:
        if len(points) > 4 and np.linalg.norm(points[-1]-points[0]) < 1.e-6:
            split = int(np.argmax(np.linalg.norm(points[:-1]-points[0], axis=1)))
            p = np.concatenate((simplify(points[:split+1], size*.006)[:-1],
                                simplify(points[split:], size*.006)))
        else:
            p = simplify(points, size*.006)
        simplified.extend(np.stack((p[:-1], p[1:]), axis=1))
    if simplified:
        front = np.asarray(simplified)
    bounds = front[:, :, :2].reshape((-1, 2))
    lo, hi = bounds.min(axis=0), bounds.max(axis=0)
    width = float(hi[0]-lo[0])
    if width < 1.e-5:
        return mesh
    C, WHITE, ACC = (np.asarray(q, dtype=float) for q in (C, WHITE, ACC))
    size = float(size)
    go = ''.join(ch for ch in str(text).upper() if ch.isalpha()) == 'GO'
    front_z = float(depth)+size*.004

    def hatch(angle, spacing, z, color, dash=False):
        """Clip scan lines against all outer contours and all counters."""
        direction = np.array([math.cos(angle), math.sin(angle)])
        normal = np.array([-direction[1], direction[0]])
        pp = front[:, :, :2]
        uv = np.stack((pp@direction, pp@normal), axis=-1)
        low, high = float(uv[:, :, 1].min()), float(uv[:, :, 1].max())
        scans = np.arange(low+spacing*.43, high, spacing)
        for row, y in enumerate(scans):
            crossings = []
            for p, q in uv:
                if (p[1] <= y < q[1]) or (q[1] <= y < p[1]):
                    crossings.append(p[0]+(y-p[1])*(q[0]-p[0])/(q[1]-p[1]))
            crossings.sort()
            for left, right in zip(crossings[::2], crossings[1::2]):
                margin = size*.008
                left, right = left+margin, right-margin
                if right-left < size*.012:
                    continue
                spans = [(left, right)]
                if dash and right-left > size*.18:
                    # A restrained copper break, not a noise texture.
                    cut = left+(right-left)*(.42 if row % 2 else .61)
                    spans = [(left, cut-size*.018), (cut+size*.018, right)]
                for x0, x1 in spans:
                    if x1 <= x0:
                        continue
                    p = direction*x0+normal*y
                    q = direction*x1+normal*y
                    mesh.line([[*p, z], [*q, z]], color)
                yield row, left, right, y, direction, normal

    def copies(levels, color, selected=1, shift=None):
        for k, z in enumerate(levels):
            delta = np.zeros(2) if shift is None else np.asarray(shift(k), float)
            for index, seg in enumerate(front):
                if selected > 1 and index % selected:
                    continue
                p = seg.copy()
                p[:, 2] = z
                p[:, :2] += delta
                mesh.line(p, color*(.65+.35*(k+1)/len(levels)))

    def side_ribs(back, stride, color, diagonals=False):
        for index in range(0, len(front), max(1, stride)):
            p, q = front[index]
            mesh.line([p, [p[0], p[1], back]], color)
            if diagonals:
                mesh.line([p, [q[0], q[1], back]], color*.63)

    if style == 0:  # Etched PCB: interrupted traces, pads and via holes.
        traces = list(hatch(0., size*.085, front_z, C*.46, dash=True))
        for row, left, right, y, direction, normal in traces:
            if right-left < size*.12 or row % 3:
                continue
            radius = min(size*.017, (right-left)*.08)
            for x in (left+radius*1.8, right-radius*1.8):
                pts = [[x+radius*math.cos(th), y+radius*math.sin(th), front_z+size*.004]
                       for th in np.linspace(0., math.tau, 7)]
                mesh.line(pts, WHITE*.48)
                mesh.line([[x, y, front_z], [x, y, -size*.12]], C*.25)
        copies([-size*.11], C*.18)
        side_ribs(-size*.11, max(3, len(front)//38), C*.23)

    elif style == 1:  # Fault plates: laminated back faces and diagonal seams.
        levels = [depth*.72, depth*.28-size*.05, -size*.18]
        copies(levels, C*.20,
               shift=lambda k: ((-1 if k % 2 else 1)*size*.010, size*.009*k))
        list(hatch(.63, size*.19, front_z, WHITE*.28, dash=True))
        side_ribs(-size*.18, max(3, len(front)//44), ACC*.26, diagonals=True)

    elif style == 2:  # Two real depths of warp and weft across each stroke.
        list(hatch(0., size*.074, front_z, C*.44))
        list(hatch(math.pi/2., size*.082, depth-size*.028, WHITE*.32))
        # Sparse stitches span the depth, emphasizing the two wire fabrics.
        side_ribs(-size*.11, max(4, len(front)//28), C*.25)
        copies([-size*.11], C*.15, selected=2)

    elif style == 3:  # Open structural extrusion with diagonal wall trusses.
        back = -max(size*.42, depth*.9)
        copies([depth*.47, back], WHITE*.22)
        side_ribs(back, max(2, len(front)//72), C*.43, diagonals=True)
        list(hatch(math.pi/2., size*.15, front_z, C*.24))

    else:  # Scan sections, each occupying a different true depth plane.
        levels = np.linspace(depth*.82, -max(size*.28, depth*.55), 5)
        for k, z in enumerate(levels):
            copies([float(z)], C*(.13+.018*k), selected=2 if k % 2 else 1)
        list(hatch(-.26, size*.13, front_z, WHITE*.30))
        side_ribs(float(levels[-1]), max(5, len(front)//24), ACC*.28)

    if go:
        # Front glyph remains untouched and readable. Deep repeated counters
        # become physical tunnel walls, then sweep through the camera lens.
        back = -max(size*1.65, depth*2.25)
        levels = np.linspace(depth*.45, back, 6)
        copies(levels, C*.19)
        side_ribs(back, max(2, len(front)//96), WHITE*.36, diagonals=True)
        # Bright terminal edge is still exactly the letter silhouette.
        copies([back], ACC*.33)
    return mesh
