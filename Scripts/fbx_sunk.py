"""Is each small piece of a mesh sunk into the biggest piece? Ray casting (parity of crossings, three directions, majority vote) tells whether a point lies inside the biggest piece's closed surface.
For every small piece (under 100 vertices) it tests the piece's base vertices (the lowest ones along the length axis) and the point 1 cm above the base centre, and prints how many are inside. Assumes the big piece is a closed surface:
the first line prints the share of its edges used by exactly two polygons (1.0 = watertight), which tells how far the vote can be trusted.
Usage: python -I Scripts/fbx_sunk.py <file.fbx> [--axis 1]. Plain Python, uses fbx_probe's reader."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fbx_probe  # noqa: E402


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def hit(origin, direction, tri):
    a, b, c = tri
    e1, e2 = sub(b, a), sub(c, a)
    p = cross(direction, e2)
    det = dot(e1, p)
    if abs(det) < 1e-12:
        return False
    inv = 1.0 / det
    t0 = sub(origin, a)
    u = dot(t0, p) * inv
    if u < 0.0 or u > 1.0:
        return False
    q = cross(t0, e1)
    v = dot(direction, q) * inv
    if v < 0.0 or u + v > 1.0:
        return False
    return dot(e2, q) * inv > 1e-9


def inside(point, tris):
    votes = 0
    for d in ((1.0, 0.0001, 0.0002), (0.0001, 1.0, 0.0003), (0.0002, 0.0003, 1.0)):
        n = sum(1 for t in tris if hit(point, d, t))
        votes += n % 2
    return votes >= 2


def main():
    path = sys.argv[1]
    axis = int(sys.argv[sys.argv.index("--axis") + 1]) if "--axis" in sys.argv else 1
    _, top = fbx_probe.parse(path)
    geom = next(o for o in {n["name"]: n for n in top}["Objects"]["children"] if o["name"] == "Geometry")
    v = fbx_probe.find(geom, "Vertices")[0]["props"][0]
    idx = fbx_probe.find(geom, "PolygonVertexIndex")[0]["props"][0]
    pts = [(v[i], v[i + 1], v[i + 2]) for i in range(0, len(v), 3)]
    weld, key = [], {}
    for p in pts:
        weld.append(key.setdefault((round(p[0] / 1e-3), round(p[1] / 1e-3), round(p[2] / 1e-3)), len(key)))
    parent = list(range(len(key)))

    def root(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    polys, cur = [], []
    for i in idx:
        cur.append(i if i >= 0 else ~i)
        if i < 0:
            polys.append(cur)
            cur = []
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            ra, rb = root(weld[a]), root(weld[b])
            if ra != rb:
                parent[ra] = rb
    groups = {}
    for poly in polys:
        groups.setdefault(root(weld[poly[0]]), []).append(poly)
    ordered = sorted(groups.values(), key=lambda g: -len({i for p in g for i in p}))
    big = ordered[0]
    edges = {}
    for poly in big:
        for a, b in zip(poly, poly[1:] + poly[:1]):
            e = tuple(sorted((weld[a], weld[b])))
            edges[e] = edges.get(e, 0) + 1
    print("big piece: %d polygons, share of edges used by exactly two polygons %.3f" % (len(big), sum(1 for c in edges.values() if c == 2) / len(edges)))
    tris = []
    for poly in big:
        for k in range(1, len(poly) - 1):
            tris.append((pts[poly[0]], pts[poly[k]], pts[poly[k + 1]]))
    for n, group in enumerate(ordered[1:], 1):
        vs = sorted({i for p in group for i in p}, key=lambda i: pts[i][axis])
        low = pts[vs[0]][axis]
        base = [pts[i] for i in vs if pts[i][axis] - low < 0.05]
        centre = [sum(p[k] for p in base) / len(base) for k in range(3)]
        above = list(centre)
        above[axis] += 1.0
        in_base = sum(1 for p in base if inside(p, tris))
        flags = "".join("Y" if inside(p, tris) else "n" for p in base)
        below = [list(p) for p in base]
        for q in below:
            q[axis] -= 1.0
        flags_below = "".join("Y" if inside(tuple(q), tris) else "n" for q in below)
        print("  piece %d: base %d vertices at %.2f, %d of them inside the big piece (%s); the same points 1 cm lower (%s); centre of the base inside: %s; 1 cm above the base centre inside: %s" % (n, len(base), low, in_base, flags, flags_below, inside(tuple(centre), tris), inside(tuple(above), tris)))


main()
